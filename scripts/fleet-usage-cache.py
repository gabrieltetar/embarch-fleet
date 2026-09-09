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

**It pins new readings before it computes** (2026-09-08). `/usage` writes its
rendered output into the session transcript, so `fleet-usage-reading.py --scan`
turns every glance the owner takes at his usage into a fresh pin with nothing
pasted. Running it from here rather than from a second cron entry means the pin
and the cache can never be a cycle out of step.

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


def pins(now: float | None = None,
         horizons: dict[str, float] | None = None) -> dict[str, dict]:
    """The most PRECISE usable pin per window, not simply the newest.

    A pin's whole job is the denominator: `implied_allowance` came out of
    `measured_billable / (used_pct/100)`, and `/usage` renders **whole
    percentages**. So a reading's own percentage IS its precision -- rounding
    alone puts the allowance within +-`0.5/used_pct` of the truth. At 71% that
    is +-0.7%. At **1% it is +-50%**.

    Taking the newest row unconditionally therefore lets a worthless reading
    evict a good one, and it did. On 2026-09-08 at 22:05, arming the first
    burndown, `/usage` caught the 5-hour window six minutes old at `1%` and
    pinned the session allowance at 36.9M off 369,287 billable; better readings
    the same week implied ~25.1M. Every 5-hour percentage that night's
    supervisor log recorded therefore read about a third low -- `43.4%` at the
    last fold against a real ~66%, and ~74% of the calibrated five-hour
    ceiling. Nothing caught it because every guard in this repo is on a pin's
    AGE. **Fresh and precise are different properties**, and only one of them
    was being checked.

    So: among the rows inside this window's horizon, keep the tightest; a newer
    row wins a tie. `read_at` still comes from the row actually chosen, so the
    caller's own age checks stay honest about what they are describing, and
    `project()` walks an older row's reset instant forward -- sound for the
    weekly, and the reason the session horizon is the caller's own
    `--pin-max-age-h` rather than something longer. With no horizon given, or
    nothing inside it, this falls back to the newest row and is exactly what it
    replaced.

    **Every row is still written to the log.** This changes which reading is
    believed, not what is recorded: `usage-readings.tsv` is also the drift
    series, and a low reading remains perfectly good evidence about the
    numerator and about the reset instant.
    """
    out: dict[str, dict] = {}
    if not LOG.is_file():
        return out
    now = time.time() if now is None else now
    horizons = horizons or {}
    best: dict[str, tuple[tuple[float, float], dict]] = {}
    newest: dict[str, tuple[float, dict]] = {}
    for line in LOG.read_text().splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 8:
            continue
        try:
            row = {"read_at": datetime.datetime.fromisoformat(f[0]),
                   "used_pct": float(f[2]),
                   "resets_at": datetime.datetime.fromisoformat(f[3]),
                   "allowance": float(f[7])}
        except ValueError:
            continue
        win, at = f[1], row["read_at"].timestamp()
        if win not in newest or at >= newest[win][0]:
            newest[win] = (at, row)
        if row["allowance"] <= 0 or row["used_pct"] <= 0:
            continue
        horizon = horizons.get(win)
        if horizon is not None and (now - at) / 3600 > horizon:
            continue
        # Smaller rounding error first; a newer row breaks a tie.
        key = (0.5 / row["used_pct"], -at)
        if win not in best or key < best[win][0]:
            best[win] = (key, row)
    for win, (_key, row) in best.items():
        out[win] = row
    for win, (_at, row) in newest.items():
        out.setdefault(win, row)
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
    ap.add_argument("--no-scan", action="store_true",
                    help="do not pin new /usage output found in the transcripts "
                         "first; compute from the pins already logged")
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

    # **Scan first, so the cron is the whole loop.** `/usage` writes what it
    # rendered into the session transcript, so every reading the owner takes is
    # on disk within a second; pinning it here means the pin refreshes itself
    # and the "paste a reading" step this file's docstring describes is now
    # only a fallback. It is cheap when there is nothing new -- one pass with a
    # string pre-filter -- and it must run BEFORE `pins()`, or a reading taken
    # in the last four minutes would be computed against the previous pin.
    if not args.no_scan:
        reading.scan(quiet=True)

    now = time.time()
    # The horizon each window picks its pin from. Session gets the same limit
    # the age check below enforces, so a chosen pin can never be one that
    # check would then refuse; weekly gets its own length, because a reading
    # from a previous week describes an allowance that has not changed but a
    # reset instant `project()` handles anyway.
    have = pins(now, {"session": args.pin_max_age_h, "weekly": LENGTH_H["weekly"]})
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
                     f"pin {age_h:.1f}h old @{pin['used_pct']:g}% "
                     f"(+-{0.5 / pin['used_pct']:.1%})")

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
