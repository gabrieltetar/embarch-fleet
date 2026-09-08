#!/usr/bin/env python3
"""Write the quota cache the status line would write, without a status line.

**The problem.** `rate_limits` -- the only first-party "how much of my limit is
left" -- arrives solely in a status line payload, and a status line exists only
inside a live `claude` session. **The VS Code extension runs none**, which is why
`~/.claude/usage-cache.json` has never existed on this machine and why
`usage-budget.py` has always degraded to a token-burn proxy. Keeping a terminal
session open forever fixes it with better numbers than this script produces; this
exists for when nobody wants to keep a window open.

**The idea.** A percentage is a numerator over a denominator. The denominator is
the seat's allowance and changes essentially never; the numerator is
`message.usage`, which is on disk for every request ever made. So one pasted
`/usage` reading pins the allowance (`fleet-usage-reading.py`), and from then on
the percentage is arithmetic over the transcripts. Each new reading re-pins it.

**What it writes is byte-compatible with `statusline-usage.py`'s cache**, so
`usage-budget.py` reads it unchanged and the whole percentage path -- PROCEED /
HOLD, the taper, the 5-hour grace -- comes alive with no code downstream. It adds
one key, `derived: true`, precisely because the two are otherwise
indistinguishable: a proxy standing in for a first-party number must say so, and
`usage-budget.py` prints it.

**The limits, and they are not small.**

- `billable` is input + output + cache writes, excluding cache reads, which bill
  at roughly a tenth. That is a ratio, not a contract. The implied allowance
  absorbs a constant factor of whatever is really metered, so the percentage
  holds while the workload mix holds and drifts when it changes.
- **The weekly reset is a true weekly instant**, so projecting a recorded one
  forward in 7-day steps is sound.
- **The 5-hour window is anchored to activity, not to a grid.** It starts with
  the first message after an idle gap, so a projected boundary drifts as soon as
  the machine goes quiet for a few hours. A session pin older than
  `--pin-max-age-h` is therefore refused rather than projected, and the weekly
  half is still written on its own -- `usage-budget.py` treats a missing window
  as "not currently constraining", which is the correct reading. **The drift is
  in the safe direction**, which is why projecting at all is defensible: a grid
  boundary sits at or before the real one, so the sum spans at least the real
  window and the percentage reads high rather than low.
- **It never writes an empty `rate_limits`.** That would pass the reader's
  validity check and then produce "PROCEED with 0 workers", the one verdict a
  leg cannot act on.

Pair it with cron at **`*/4`**, not `*/5`: the reader rejects a cache older than
300s, so a five-minute cadence is sometimes one second too late.

Usage:
    scripts/fleet-usage-cache.py                 recompute and write the cache
    scripts/fleet-usage-cache.py --check         print what it would write
    scripts/fleet-usage-cache.py --install-cron  add the */4 entry, once
Exit status: 0 written / printed, 1 nothing pinned or every pin too old, 2 bad args.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

HERE = Path(__file__).resolve().parent
CACHE = Path(os.path.expanduser("~/.claude/usage-cache.json"))
LOG = CONF.state_dir / "usage-readings.tsv"
KEYS = {"session": "five_hour", "weekly": "seven_day"}
LENGTH_H = {"session": 5.0, "weekly": 168.0}
CRON = (f"*/4 * * * * /usr/bin/python3 {HERE / 'fleet-usage-cache.py'} "
        f">> {CONF.state_dir / 'usage-cache.log'} 2>&1")


def pins() -> dict[str, dict]:
    """Newest pin per window from the readings log. Later rows win."""
    out: dict[str, dict] = {}
    if not LOG.is_file():
        return out
    for line in LOG.read_text().splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 8:
            continue
        try:
            out[f[1]] = {"read_at": datetime.datetime.fromisoformat(f[0]),
                         "resets_at": datetime.datetime.fromisoformat(f[3]),
                         "allowance": float(f[7])}
        except ValueError:
            continue
    return out


def project(reset: datetime.datetime, length_h: float, now: float) -> float:
    """The next reset instant at or after `now`, stepping by the window length."""
    at = reset.timestamp()
    step = length_h * 3600
    if step <= 0:
        return at
    while at <= now:
        at += step
    return at


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="print, write nothing")
    ap.add_argument("--install-cron", action="store_true", help="add the */4 entry")
    ap.add_argument("--pin-max-age-h", type=float, default=24.0,
                    help="refuse a session pin older than this, because the "
                         "5-hour window is anchored to activity (default 24)")
    args = ap.parse_args()

    if args.install_cron:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        if "fleet-usage-cache.py" in cur:
            print("already installed")
            return 0
        subprocess.run(["crontab", "-"], input=cur.rstrip("\n") + "\n" + CRON + "\n",
                       text=True, check=True)
        print(f"installed:\n  {CRON}")
        return 0

    sys.path.insert(0, str(HERE))
    from importlib.machinery import SourceFileLoader
    reading = SourceFileLoader("reading", str(HERE / "fleet-usage-reading.py")).load_module()

    now = time.time()
    have = pins()
    limits: dict[str, dict] = {}
    notes: list[str] = []
    for name, key in KEYS.items():
        pin = have.get(name)
        if not pin or pin["allowance"] <= 0:
            notes.append(f"{name}: no pin in {LOG.name} -- paste a /usage reading")
            continue
        age_h = (now - pin["read_at"].timestamp()) / 3600
        if name == "session" and age_h > args.pin_max_age_h:
            notes.append(f"{name}: pin is {age_h:.0f}h old (max {args.pin_max_age_h:g}h) "
                         "-- the 5-hour window has almost certainly re-anchored")
            continue
        reset = project(pin["resets_at"], LENGTH_H[name], now)
        start = reset - LENGTH_H[name] * 3600
        total, reqs, _sub = reading.burn_since(start)
        used = 100.0 * total / pin["allowance"]
        limits[key] = {"used_percentage": round(used, 1), "resets_at": int(reset)}
        notes.append(f"{name}: {used:.1f}% ({total:,} of {pin['allowance']:,.0f} "
                     f"billable, {reqs:,} req), resets "
                     f"{datetime.datetime.fromtimestamp(reset):%H:%M %d-%b}, "
                     f"pin {age_h:.1f}h old")

    for n in notes:
        print(f"  {n}")
    if not limits:
        print("nothing pinned and usable: writing no cache. An empty rate_limits "
              "would read as\nvalid and produce 'PROCEED with 0 workers'.",
              file=sys.stderr)
        return 1

    payload = {"cached_at": int(now), "session_id": "derived:fleet-usage-cache.py",
               "derived": True, "rate_limits": limits}
    if args.check:
        print(json.dumps(payload, indent=2))
        return 0
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(CACHE.parent), prefix=".usage-cache.")
    with os.fdopen(fd, "w") as fh:
        json.dump(payload, fh)
    os.replace(tmp, CACHE)
    print(f"wrote {CACHE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
