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
import calendar
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
    """An actual rate-limit error in any transcript within the window, unless
    the throttle it recorded has already expired.

    This is the signal the percentages were a proxy for. Claude Code records a
    throttled request with `"error":"rate_limit"`, `"apiErrorStatus":429` and a
    top-level `quotaLimits` carrying the `resetsAt` the server itself declared.

    Three things this gets right that the first version did not, all measured
    2026-09-06/07 and filed as `tasks/doc/023`:

    * **The timestamp is UTC.** `time.mktime` reads a naive struct as LOCAL, so
      west of UTC every age came out inflated by the offset -- 6.0 h on this
      machine, which turned a 90-minute lookback into a ~7.5-hour one and
      printed negative ages ("a real 429 was recorded -356 min ago").
      `calendar.timegm` is the correct pair for a `...Z` timestamp.

    * **A spent 429 does not HOLD.** The rejection carries its own reset time;
      once that has passed the window has refilled and requests are being
      served again. Holding the fleet on it stops work for no reason -- the
      case that actually happened, with `resetsAt` 27 seconds after the
      rejection. A 429 line with no `quotaLimits` keeps the old behaviour,
      because then nothing says the throttle is over.

    * **The verdict comes from parsed fields, not a substring.** The old
      pre-filter matched the raw line, so ANY transcript that merely QUOTED
      the marker -- a session reading this script, or discussing a 429 --
      looked like a live throttle and held the fleet. The cheap string test
      survives as a pre-filter; the decision is made on the top-level keys,
      which a quotation inside some other field cannot forge.
    """
    cutoff = time.time() - minutes * 60
    newest = None                                 # (epoch, resets_at or None)
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
                        if "rate_limit" not in line:
                            continue              # pre-filter only, see above
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        if not isinstance(rec, dict):
                            continue
                        if rec.get("error") != "rate_limit":
                            continue
                        if rec.get("apiErrorStatus") != 429:
                            continue
                        try:
                            when = calendar.timegm(
                                time.strptime(rec.get("timestamp", "")[:19],
                                              "%Y-%m-%dT%H:%M:%S"))
                        except Exception:
                            continue
                        if when < cutoff:
                            continue
                        quota = rec.get("quotaLimits")
                        resets = quota.get("resetsAt") if isinstance(quota, dict) else None
                        if not isinstance(resets, (int, float)):
                            resets = None
                        if newest is None or when > newest[0]:
                            newest = (when, resets)
            except OSError:
                continue
    if newest is None:
        return None
    when, resets = newest
    age = int((time.time() - when) / 60)
    if resets is not None and resets <= time.time():
        return None                               # spent: the window refilled
    if resets is None:
        return (f"a real 429 was recorded {age} min ago, and it recorded no "
                f"reset time -- holding for the full {minutes} min window")
    return (f"a real 429 was recorded {age} min ago; the window it names "
            f"resets in {human_reset(resets)}")


def measured_wave(used_frac: float, full_below: float, cap: int) -> int:
    """A wave size from the measured burn, as a rate control rather than a budget.

    `suggest()` above tapers over a percentage of a window with a known reset,
    which is the right shape for a quota that refills at a wall-clock instant.
    The five-hour window here is ROLLING and its numbers are inferred, so the
    quantity that matters is the sustainable RATE: at steady state a rolling
    five-hour sum is five times the hourly rate, so staying under the ceiling
    means staying under `ceiling / 5` tokens an hour.

    Full width only below `full_below` of the ceiling, then linear to one
    worker at the ceiling. `full_below = 0.25` is not arbitrary: at the burn
    this bench actually runs, it returns the same wave the rate arithmetic
    does, and it degrades the right way at both ends.

    **It is a feedback loop, not a prediction, and that is the whole safety
    argument.** Every leg's step 0 re-reads the burn its predecessor produced,
    so a wave that was too wide is narrowed within one leg -- about forty
    minutes -- and a real 429 remains the hard stop underneath it.
    """
    if used_frac >= 1.0:
        return 1
    if used_frac <= full_below:
        return cap
    frac = 1.0 - (used_frac - full_below) / (1.0 - full_below)
    return max(1, min(cap, round(cap * frac)))


def burn_window(hours: float) -> tuple[int, int, float] | None:
    """Billable tokens across every transcript in the trailing window.

    The percentages are the number this gate was designed around and they are
    unavailable on this machine by construction -- `rate_limits` reaches only a
    status line, the VS Code extension runs none, and a search of every
    transcript on disk finds the field recorded nowhere. So the fallback used to
    be a CONSTANT: wave `degraded_workers`, forever, whatever the seat had left.

    What IS on disk is every request's own `message.usage`. Summing it over the
    trailing five hours gives a real burn rate, which is what this docstring's
    first version asked for: "once a few batches exist, replace this with
    cost-per-worker arithmetic against the measured headroom."

    `billable` counts input + output + cache WRITES and excludes cache reads,
    which bill at roughly a tenth. That is a ratio, not a contract, so the
    ceiling it is compared against is calibrated from observed behaviour rather
    than derived -- see `[limits] five_hour_token_ceiling` in fleet.toml.

    Returns (billable, requests, hours_covered), or None if no transcript in the
    window could be read -- which is NOT zero burn, and must not be read as
    headroom.
    """
    cutoff = time.time() - hours * 3600
    billable = 0
    requests = 0
    oldest = None
    seen_any = False
    for root, _dirs, files in os.walk(TRANSCRIPTS):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    continue                      # cannot hold a request in it
                seen_any = True
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        if '"usage"' not in line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        msg = rec.get("message")
                        if not isinstance(msg, dict):
                            continue
                        use = msg.get("usage")
                        if not isinstance(use, dict):
                            continue
                        try:
                            when = calendar.timegm(
                                time.strptime(rec.get("timestamp", "")[:19],
                                              "%Y-%m-%dT%H:%M:%S"))
                        except Exception:
                            continue
                        if when < cutoff:
                            continue
                        requests += 1
                        billable += ((use.get("input_tokens") or 0)
                                     + (use.get("output_tokens") or 0)
                                     + (use.get("cache_creation_input_tokens") or 0))
                        oldest = when if oldest is None else min(oldest, when)
            except OSError:
                continue
    if not seen_any:
        return None
    covered = (time.time() - oldest) / 3600 if oldest else 0.0
    return billable, requests, covered


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
    ap.add_argument("--five-hour-grace-min", type=float,
                    default=float(CONF["limits"].get("five_hour_grace_min", 60)),
                    help="ignore the 5-hour window entirely when it resets within "
                         "this many minutes (fleet.toml [limits] five_hour_grace_min)")
    ap.add_argument("--taper", type=float,
                    default=float(CONF["limits"].get("taper", 0.25)),
                    help="fraction of a cap within which the wave narrows "
                         "toward 1 worker; below it, run full width "
                         "(fleet.toml [limits] taper)")
    ap.add_argument("--suggest", action="store_true", help="print a suggested wave size")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--strict", action="store_true",
                    help="treat missing percentages as HOLD instead of a capped wave")
    ap.add_argument("--token-ceiling", type=float,
                    default=float(CONF["limits"].get("five_hour_token_ceiling", 0)),
                    help="billable tokens the 5-hour window holds (fleet.toml); "
                         "0 disables the measured wave and restores the constant one")
    ap.add_argument("--burn-full-below", type=float, default=0.25,
                    help="run the full wave while the measured 5-hour burn is "
                         "under this fraction of the ceiling (default 0.25)")
    ap.add_argument("--burn", action="store_true",
                    help="print the measured 5-hour burn and exit")
    ap.add_argument("--check-429", type=int, default=90, metavar="MIN",
                    help="HOLD if a real 429 was recorded in the last MIN minutes (default 90)")
    args = ap.parse_args()

    if args.burn:
        b = burn_window(5.0)
        if b is None:
            print("no transcript in the last 5 h could be read")
            return 2
        ceiling = float(args.token_ceiling)
        pct = f"{100.0 * b[0] / ceiling:.0f}% of ceiling" if ceiling > 0 else "no ceiling set"
        if args.as_json:
            print(json.dumps({"billable": b[0], "requests": b[1],
                              "hours_covered": round(b[2], 2),
                              "ceiling": ceiling}))
        else:
            print(f"5h burn: {b[0]:,} billable tokens, {b[1]:,} requests, "
                  f"oldest {b[2]:.1f} h back -- {pct}")
        return 0

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
        burn = burn_window(5.0)
        ceiling = float(args.token_ceiling)
        # A measured wave rather than a constant one. Same taper as the
        # percentage path, over the one headroom that can actually be read
        # here; the floor is 1 rather than 0 because a burn at the ceiling
        # without a 429 is a reason to go slowly, not to stop -- a real 429 is
        # what stops the fleet, and it is checked above.
        if burn is not None and ceiling > 0:
            used_pct = 100.0 * burn[0] / ceiling
            workers = measured_wave(burn[0] / ceiling, args.burn_full_below, MAX_WORKERS)
            measured = (f"5h burn {burn[0]:,} billable tokens over {burn[1]:,} "
                        f"requests = {used_pct:.0f}% of the calibrated ceiling "
                        f"({ceiling:,.0f}); sustainable rate is "
                        f"{ceiling / 5:,.0f}/h, observed "
                        f"{burn[0] / max(burn[2], 0.1):,.0f}/h")
        else:
            used_pct = None
            workers = DEGRADED_WORKERS
            measured = ("no transcript in the last 5 h could be read, so the "
                        "burn is unknown -- falling back to the constant wave")
        if args.strict:
            workers, verdict = 0, "HOLD"
        elif used_pct is not None and used_pct >= 100.0:
            workers, verdict = 1, "DEGRADED"
        else:
            verdict = "DEGRADED"
        if args.as_json:
            print(json.dumps({"verdict": verdict, "reason": why,
                              "workers": workers, "feeder": feeder,
                              "burn_5h_billable": burn[0] if burn else None,
                              "burn_5h_requests": burn[1] if burn else None,
                              "burn_pct_of_ceiling": used_pct,
                              "token_ceiling": ceiling}))
        else:
            print(f"{verdict} -- {why}")
            if feeder:
                print(f"  FEEDER: {feeder}")
                print("  DEGRADED and 'the feeder is broken' are indistinguishable on\n"
                      "  disk, so this is the only thing that tells them apart.")
            print(f"  {measured}")
            if args.strict:
                print("--strict: not dispatching without numbers.")
            else:
                print(f"Proceeding with a measured wave of {workers}. No 429 in the "
                      f"last {args.check_429} min, which is the hard signal.")
        return 1 if args.strict else 2

    limits = data["rate_limits"]
    five, five_reset = window(limits, "five_hour")
    seven, seven_reset = window(limits, "seven_day")

    # **A 5-hour window about to reset does not gate anything.** It is a lockout
    # rather than a budget (ops.md §2) and it refills on a clock, so holding on
    # it with minutes left buys nothing and costs the fleet those minutes. The
    # exposure is bounded by the same clock that justifies the grace: ignoring
    # it with N minutes to go risks at most an N-minute lockout, which is why
    # the grace is a duration and not a flag. **The weekly window is never
    # graced** -- it is the real budget and its reset is days away.
    five_graced = None
    if five is not None and five_reset:
        grace = (five_reset - time.time()) / 60
        if 0 < grace <= args.five_hour_grace_min:
            five, five_graced = None, five   # out of the HOLD test and the wave

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
            "five_hour": five if five is not None else five_graced,
            "five_hour_resets_at": five_reset,
            "five_hour_ignored": five_graced is not None,
            "five_hour_grace_min": args.five_hour_grace_min,
            "seven_day": seven, "seven_day_resets_at": seven_reset,
            "blocking": blocking,
            "cache_age_s": data["_age"],
            "derived": bool(data.get("derived")),
        }))
        return 1 if blocking else 0

    def fmt(label, used, reset, cap):
        if used is None:
            return f"  {label}: not reported (window inactive)"
        bar = "#" * int(used / 5) + "." * (20 - int(used / 5))
        return f"  {label}: {used:5.1f}% [{bar}] cap {cap:g}%, resets in {human_reset(reset)}"

    print(f"{verdict}  (cache {data['_age']}s old)")
    if data.get("derived"):
        # A derived cache is byte-compatible with the status line's, so nothing
        # downstream could otherwise tell a proxy from a first-party number.
        print("  DERIVED: these percentages come from fleet-usage-cache.py -- a "
              "pinned allowance\n           over the transcripts' own token sum, "
              "not from `rate_limits`. Re-pin with\n           "
              "fleet-usage-reading.py after a fresh /usage.")
    print(fmt("5-hour", five if five is not None else five_graced,
              five_reset, args.five_hour_max))
    if five_graced is not None:
        # NOT "window inactive", which is what fmt() would have said for a None
        # it could not tell apart from an unreported one.
        print(f"  IGNORED: the 5-hour window resets in {human_reset(five_reset)}, "
              f"inside the {args.five_hour_grace_min:g}-min grace, so it gates\n"
              "           neither the verdict nor the wave. Worst case is a "
              "lockout no longer than that.")
    print(fmt("weekly", seven, seven_reset, args.seven_day_max))
    for b in blocking:
        print(f"  BLOCKING: {b}")
    if args.suggest and not blocking:
        print(f"  suggested wave: {workers} worker(s)")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
