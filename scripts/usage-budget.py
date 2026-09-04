#!/usr/bin/env python3
"""Answer "may the supervisor dispatch more workers right now?" from the real
Claude.ai rate-limit numbers.

Why this file exists: the supervisor's whole point is to keep the seat busy
(protocol.md §1), and the only way to do that safely is to know
how close to the ceiling it already is. Claude Code publishes exactly that --
``rate_limits.five_hour.used_percentage`` and ``rate_limits.seven_day.*`` -- but
ONLY on the JSON it hands a status line command. Quota state arrives over the
wire, so a tool that reads only files can say what was consumed and never what
is left -- see the degradation note below, which is the case that actually
applies on this machine.

So ``~/.claude/statusline-usage.py`` runs as the status line, caches those
numbers to ``~/.claude/usage-cache.json``, and this script reads that cache.

Two thresholds, deliberately different, both overridable:

* ``--seven-day-max`` (default 70) -- the weekly cap is the actual budget. This
  is the number the owner asked for.
* ``--five-hour-max`` (default 85) -- the 5-hour window is not a budget, it is a
  lockout. Burning it to 100% stops the OWNER working, not just the fleet, so it
  gets a higher ceiling but is still a stop: the window refills on its own in
  hours, and a batch that waits loses nothing.

**The percentages are often unavailable, and that is the normal case here.**
They arrive only on the JSON Claude Code hands a status line command, and the VS
Code extension does not run one -- measured 2026-09-03, after a restart, no
cache ever appeared. So UNKNOWN is not an incident: it is this machine's steady
state, and treating it as HOLD would mean the fleet never starts.

Instead UNKNOWN degrades to a **capped wave** (``DEGRADED_WORKERS``) and leans on
the signal that *is* available locally: an actual HTTP 429 recorded in the
session transcript. ``--check-429`` finds one. That is the real protection --
the percentages were only ever there to avoid reaching it.

Exit status is the whole interface:
  0  PROCEED  -- headroom on both windows; ``--suggest`` prints a wave size
  1  HOLD     -- a threshold is reached, or a recent 429; stop dispatching
  2  DEGRADED -- no percentages available; proceed with a capped wave.
                 ``--strict`` turns this back into HOLD.

Usage:
  scripts/usage-budget.py                       check, human-readable
  scripts/usage-budget.py --suggest             also print a worker count
  scripts/usage-budget.py --json                machine-readable
  scripts/usage-budget.py --seven-day-max 55    tighter weekly budget
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse
import json
import os
import time

CACHE = os.path.expanduser("~/.claude/usage-cache.json")
MAX_WORKERS = CONF['limits']['max_workers']          # ops.md §1's cap
DEGRADED_WORKERS = CONF['limits']['degraded_workers']  # wave when percentages are unavailable
TRANSCRIPTS = os.path.expanduser("~/.claude/projects")


def check_feeder() -> str | None:
    """Is the thing that WRITES the cache still the versioned copy?

    risks.md: the budget's data source lived outside every repo, unversioned and
    uncovered by any check. A machine reinstall or a settings edit silently turns
    every leg DEGRADED -- and DEGRADED is the steady state on this machine, so
    nothing would ever report it. The script is now in this repo; this asserts
    that settings.json actually points at it.

    Advisory, never fatal. A wrong statusLine is a reason to distrust a verdict,
    not a reason to refuse to produce one -- the whole design of this gate is to
    degrade rather than block.
    """
    settings = os.path.expanduser("~/.claude/settings.json")
    versioned = str(Path(__file__).resolve().parent / "statusline-usage.py")
    try:
        with open(settings) as fh:
            cmd = json.load(fh).get("statusLine", {}).get("command", "")
    except (OSError, ValueError) as e:
        return f"cannot read {settings}: {e}"
    if not cmd:
        return f"no statusLine configured in {settings}; nothing writes the cache"
    if versioned not in cmd:
        return (f"statusLine runs {cmd.split()[-1]!r}, not the versioned "
                f"{versioned!r} -- an unversioned feeder can break silently")
    return None


def read_cache(path: str, max_age: int):
    """(payload, None) or (None, reason-it-is-unusable)."""
    if not os.path.exists(path):
        return None, (f"no cache at {path} -- either no status line ran, or it "
                      "ran and its payload carried no rate_limits. Those are "
                      "indistinguishable from disk: statusline-usage.py writes "
                      "nothing unless rate_limits is present "
                      "(ops.md section 2)")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return None, f"cache unreadable: {e}"

    age = int(time.time()) - int(data.get("cached_at", 0))
    if age > max_age:
        return None, (f"cache is {age}s old (limit {max_age}s) -- the status "
                      "line has not run recently; set statusLine.refreshInterval")
    if not isinstance(data.get("rate_limits"), dict):
        return None, "cache has no rate_limits (not a Pro/Max seat, or no API response yet)"
    data["_age"] = age
    return data, None


def window(limits: dict, key: str):
    """(used_percentage, resets_at) for a window, or (None, None). A window is
    dropped by Claude Code once its resets_at passes, so absence is normal and
    means 'this window is not currently constraining'."""
    node = limits.get(key)
    if not isinstance(node, dict):
        return None, None
    used = node.get("used_percentage")
    if not isinstance(used, (int, float)):
        return None, None
    return float(used), node.get("resets_at")


def recent_429(minutes: int) -> str | None:
    """An actual rate-limit error in any transcript within the window.

    This is the signal the percentages were a proxy for. Claude Code records a
    throttled request as `"error":"rate_limit"` with `apiErrorStatus":429`, so a
    real limit is detectable locally even when no percentage ever is.
    """
    cutoff = time.time() - minutes * 60
    newest = None
    for root, _dirs, files in os.walk(TRANSCRIPTS):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    continue                      # cheap reject before reading
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if '"error":"rate_limit"' not in line:
                            continue
                        try:
                            ts = json.loads(line).get("timestamp", "")
                            when = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
                        except Exception:
                            continue
                        if when >= cutoff and (newest is None or when > newest):
                            newest = when
            except OSError:
                continue
    if newest is None:
        return None
    return f"a real 429 was recorded {int((time.time()-newest)/60)} min ago"


def human_reset(ts) -> str:
    if not isinstance(ts, (int, float)):
        return "unknown"
    delta = int(ts) - int(time.time())
    if delta <= 0:
        return "now"
    h, m = divmod(delta // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def suggest(five: float | None, seven: float | None,
            five_max: float, seven_max: float, taper: float) -> int:
    """A wave size from the tighter of the two headrooms.

    Full width until the tighter window is inside its taper band, then linear
    down to one worker. Running at full width is the POINT -- the fleet exists
    because the seat is under-used (§1), so a curve that tapers from zero would
    defeat it. The taper only exists so the last workers of a batch don't slam
    into the threshold six-in-flight.

    Still a heuristic over a number nobody has calibrated. The digest records
    actual per-batch burn (§11); once a few batches exist, replace this with
    cost-per-worker arithmetic against the measured headroom.
    """
    fracs = []
    for used, cap in ((five, five_max), (seven, seven_max)):
        if used is None or cap <= 0:
            continue
        band = taper * cap                      # width of the slow-down zone
        headroom = max(0.0, cap - used)
        fracs.append(1.0 if band <= 0 else min(1.0, headroom / band))
    if not fracs:
        return 0
    return max(1, min(MAX_WORKERS, round(MAX_WORKERS * min(fracs))))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--five-hour-max", type=float, default=float(CONF["limits"]["five_hour_pct"]),
                    help="stop dispatching at this %% of the 5-hour window (fleet.toml)")
    ap.add_argument("--seven-day-max", type=float, default=float(CONF["limits"]["weekly_pct"]),
                    help="stop dispatching at this %% of the weekly window (fleet.toml)")
    ap.add_argument("--max-age", type=int, default=300,
                    help="reject a cache older than this many seconds (default 300)")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--taper", type=float, default=0.25,
                    help="fraction of a cap within which the wave narrows "
                         "toward 1 worker; below it, run full width (default 0.25)")
    ap.add_argument("--suggest", action="store_true", help="print a suggested wave size")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--strict", action="store_true",
                    help="treat missing percentages as HOLD instead of a capped wave")
    ap.add_argument("--check-429", type=int, default=90, metavar="MIN",
                    help="HOLD if a real 429 was recorded in the last MIN minutes (default 90)")
    args = ap.parse_args()

    throttled = recent_429(args.check_429)

    data, why = read_cache(args.cache, args.max_age)
    if why:
        if throttled:
            if args.as_json:
                print(json.dumps({"verdict": "HOLD", "reason": throttled, "workers": 0}))
            else:
                print(f"HOLD -- {throttled}")
            return 1
        feeder = check_feeder()
        workers = 0 if args.strict else DEGRADED_WORKERS
        verdict = "HOLD" if args.strict else "DEGRADED"
        if args.as_json:
            print(json.dumps({"verdict": verdict, "reason": why,
                              "workers": workers, "feeder": feeder}))
        else:
            print(f"{verdict} -- {why}")
            if feeder:
                print(f"  FEEDER: {feeder}")
                print("  DEGRADED and 'the feeder is broken' are indistinguishable on\n"
                      "  disk, so this is the only thing that tells them apart.")
            if args.strict:
                print("--strict: not dispatching without numbers.")
            else:
                print(f"Proceeding with a capped wave of {workers}. No 429 in the last "
                      f"{args.check_429} min, which is the signal that actually matters.")
        return 1 if args.strict else 2

    limits = data["rate_limits"]
    five, five_reset = window(limits, "five_hour")
    seven, seven_reset = window(limits, "seven_day")

    blocking = []
    if throttled:
        blocking.append(throttled)
    if five is not None and five >= args.five_hour_max:
        blocking.append(f"5-hour at {five:.1f}% (max {args.five_hour_max:g}%), "
                        f"resets in {human_reset(five_reset)}")
    if seven is not None and seven >= args.seven_day_max:
        blocking.append(f"weekly at {seven:.1f}% (max {args.seven_day_max:g}%), "
                        f"resets in {human_reset(seven_reset)}")

    workers = 0 if blocking else suggest(five, seven, args.five_hour_max,
                                         args.seven_day_max, args.taper)
    verdict = "HOLD" if blocking else "PROCEED"

    if args.as_json:
        print(json.dumps({
            "verdict": verdict,
            "workers": workers,
            "five_hour": five, "five_hour_resets_at": five_reset,
            "seven_day": seven, "seven_day_resets_at": seven_reset,
            "blocking": blocking,
            "cache_age_s": data["_age"],
        }))
        return 1 if blocking else 0

    def fmt(label, used, reset, cap):
        if used is None:
            return f"  {label}: not reported (window inactive)"
        bar = "#" * int(used / 5) + "." * (20 - int(used / 5))
        return f"  {label}: {used:5.1f}% [{bar}] cap {cap:g}%, resets in {human_reset(reset)}"

    print(f"{verdict}  (cache {data['_age']}s old)")
    print(fmt("5-hour", five, five_reset, args.five_hour_max))
    print(fmt("weekly", seven, seven_reset, args.seven_day_max))
    for b in blocking:
        print(f"  BLOCKING: {b}")
    if args.suggest and not blocking:
        print(f"  suggested wave: {workers} worker(s)")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
