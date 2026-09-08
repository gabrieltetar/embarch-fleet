#!/usr/bin/env python3
"""Arm, report and end BURNDOWN -- the mode that spends a weekly window before
it resets.

**Why this exists**, in one line -- the argument is `burndown.md`. The weekly
allowance is use-it-or-lose-it: it refills at a fixed instant and whatever is
unspent then is gone. Every other control in this repo is built to keep the
fleet away from the ceiling, which is right for six days and wrong for the
seventh -- on 2026-09-08 the seat entered
the last evening of its week at 81% used, with roughly 36M billable tokens that
had no other way to be spent and a gate that would have stopped at 90%.

Burndown swaps four numbers (`[burndown]` in fleet.toml: a wider cap, higher
stops, no taper) and adds one precondition. **Everything else about a leg is
unchanged** -- same protocol, same reviewer, same commits to `main`. It is not a
different fleet, it is the same fleet with the throttle open.

**Three properties are load-bearing, and each is a refusal here.**

*Manual.* Nothing self-arms this. A mode that decides on its own to spend the
remaining allowance is a mode that can decide wrong at 3 a.m., and the owner is
the only one who knows whether he wants the seat tonight.

*Deadlined.* Every burndown races a known reset instant, and is bounded by
`[burndown] max_horizon_h`. **The instant defaults to the pinned weekly reset**
-- the scraped `/usage` reading that pins the allowance carries it, so `--arm`
alone is the normal form and `--until` is the override. Requiring it to be typed
was, briefly, asking the owner to re-enter data already on disk. The deadline is
the entire justification, so it is also the expiry: `CONF.burndown()` reads a
passed deadline as "not a burndown" with no write from anyone, which means
forgetting to end it cannot leave the safeties off. **Early in a week the
derived deadline is refused**, because a reset 160 hours out is not something
about to expire -- it is the fleet with its safeties off.

*Pinned to a fresh reading.* The percentages on this machine are DERIVED
(budget.md): a pinned allowance over the transcripts' own token sum. Burndown is
the only mode that spends to the wall, so it is the only one that refuses to run
on a stale denominator -- `[burndown] pin_max_age_h`, tighter than the 24 h the
cache itself enforces, because at a 97% stop the margin for drift is three
points. **Running `/usage` is the whole ceremony**: its rendered output lands in
the session transcript, `fleet-usage-reading.py --scan` pins it, and `--until`
runs that refresh itself rather than making the owner wait out a cron tick.

**What ends it.** The deadline, `fleet stop`, an empty queue, a hard fault, or a
real 429 -- the owner's call, 2026-09-08: in burndown a 429 does not throttle,
it stops the mode. `--clear` is how a leg says so; it reverts the latch to
normal mode rather than deleting it, so the normal 90% gate is what decides
whether anything runs next, and after a 429 at 97% that gate holds by itself.

Usage:
  scripts/fleet-burndown.py                      report (default)
  scripts/fleet-burndown.py --arm [--scope core,ui]
                                    arm until the pinned weekly reset -- run
                                    /usage first, this pins it for you
  scripts/fleet-burndown.py --until '2026-09-09 07:00'
                                    same, with the deadline stated by hand
  scripts/fleet-burndown.py --clear --reason '429 at 04:12Z'
  scripts/fleet-burndown.py --json               machine-readable, any mode
Exit status: 0 armed / live / cleared, 1 not armed (report) or refused, 2 bad
arguments or unreadable state.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF, parse_instant  # noqa: E402

CACHE = os.path.expanduser("~/.claude/usage-cache.json")
READINGS = CONF.state_dir / "usage-readings.tsv"
PUMP = CONF.state_dir / "pump"
BD = CONF.get("burndown", {})


def cfg(key, default):
    return BD.get(key, default)


def iso(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(ts))


def human(seconds: float) -> str:
    seconds = int(max(0, seconds))
    h, m = divmod(seconds // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m"


def pin_age_h() -> float | None:
    """Hours since the newest `/usage` reading, or None if there is none.

    The reading log is the denominator's provenance: every percentage this repo
    prints is `measured_billable / implied_allowance`, and the allowance came
    from one of these rows. An unreadable log is not a fresh pin -- it is no pin
    at all, and returns None so the caller refuses rather than proceeds.
    """
    try:
        rows = [r for r in READINGS.read_text().splitlines()[1:] if r.strip()]
    except OSError:
        return None
    newest = None
    for row in rows:
        ts = parse_instant(row.split("\t")[0])
        if ts is not None and (newest is None or ts > newest):
            newest = ts
    return None if newest is None else (time.time() - newest) / 3600.0


def cache() -> tuple[dict | None, str | None]:
    """The usage cache, or why it cannot be used. Same validity test
    `usage-budget.py` applies, restated in no way: a cache older than 300 s is
    what its own reader rejects, and arming on one it would reject would arm a
    burndown that immediately HOLDs."""
    try:
        with open(CACHE, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError:
        return None, f"no usage cache at {CACHE}"
    except ValueError as e:
        return None, f"usage cache unreadable: {e}"
    age = time.time() - float(data.get("cached_at", 0))
    if age > 300:
        return None, (f"usage cache is {age:.0f}s old (limit 300) -- the "
                      "*/4 fleet-usage-cache.py cron is not running")
    if not isinstance(data.get("rate_limits"), dict):
        return None, "usage cache carries no rate_limits"
    return data, None


def snapshot() -> dict:
    """Everything a report or an arming decision needs, in one dict."""
    latch, why_not = CONF.burndown()
    data, cache_why = cache()
    limits = (data or {}).get("rate_limits", {})

    def win(key):
        node = limits.get(key)
        if not isinstance(node, dict):
            return None, None
        used = node.get("used_percentage")
        return (float(used) if isinstance(used, (int, float)) else None,
                node.get("resets_at"))

    weekly, weekly_reset = win("seven_day")
    five, five_reset = win("five_hour")
    return {
        "active": latch is not None,
        "why_not": why_not,
        "latch": latch or CONF.pump(),
        "until": parse_instant((latch or {}).get("until", "")) if latch else None,
        "weekly_pct": weekly, "weekly_resets_at": weekly_reset,
        "five_hour_pct": five, "five_hour_resets_at": five_reset,
        "derived": bool((data or {}).get("derived")),
        "cache_problem": cache_why,
        "pin_age_h": pin_age_h(),
        "caps": {"max_workers": cfg("max_workers", CONF['limits']['max_workers']),
                 "weekly_pct": cfg("weekly_pct", 97),
                 "five_hour_pct": cfg("five_hour_pct", 97),
                 "taper": cfg("taper", 0.0)},
    }


def arm(until_raw: str | None, scope: str | None, snap: dict) -> tuple[int, list[str]]:
    """Write the burndown latch, or refuse and say which precondition failed.

    Every refusal below is a case where arming would produce a burndown that
    cannot do its job: no deadline to race, no trustworthy denominator to stop
    at 97% of, or nothing left to burn. Refusing is cheap -- the owner re-runs
    one command -- and the failure it prevents is spending into next week.

    **`until_raw` is optional, and defaulting it is not a weakening of the
    deadline rule.** The rule is that a burndown must race a known reset
    instant; it was a required argument only because, when this was written, the
    only place that instant existed was the owner's eyes reading `/usage`. It is
    now on disk -- the same scraped reading that pins the allowance carries
    `seven_day.resets_at` -- so asking him to retype it was asking him to
    re-enter data the machine already had, which is how a wrong date gets typed.
    Stated still wins over derived, and the latch records which it was.
    """
    bad: list[str] = []
    horizon = float(cfg("max_horizon_h", 48))
    max_pin = float(cfg("pin_max_age_h", 4))
    derived = until_raw is None

    if derived:
        reset = snap["weekly_resets_at"]
        when = float(reset) if isinstance(reset, (int, float)) else None
        if when is None:
            bad.append("no weekly reset instant is pinned, so there is no "
                       "deadline to derive -- run /usage, or pass --until")
    else:
        when = parse_instant(until_raw)
        if when is None:
            bad.append(f"--until {until_raw!r} is not an instant I can read "
                       "(try '2026-09-09 07:00'; no timezone means local)")

    if when is None:
        pass
    else:
        left = (when - time.time()) / 3600.0
        if left <= 0:
            bad.append(f"--until {iso(when)} is in the past")
        elif left > horizon:
            which = ("the weekly reset" if derived else f"--until {iso(when)}")
            bad.append(f"{which} is {left:.1f}h out, past the "
                       f"{horizon:g}h horizon ([burndown] max_horizon_h) -- a "
                       "burndown with no near reset is the fleet with its "
                       "safeties off"
                       + (". This is early in the week, not the end of one; "
                          "there is nothing about to expire." if derived else ""))

    if snap["cache_problem"]:
        bad.append(snap["cache_problem"] + " -- burndown stops at a percentage, "
                   "so it will not start without one")
    age = snap["pin_age_h"]
    if age is None:
        bad.append(f"no /usage reading in {READINGS} -- the allowance every "
                   "percentage divides by has never been pinned")
    elif age > max_pin:
        bad.append(f"the newest /usage reading is {age:.1f}h old (limit "
                   f"{max_pin:g}h, [burndown] pin_max_age_h). Run /usage and "
                   "record it:\n      scripts/fleet-usage-reading.py --session "
                   "<pct> --session-resets <iso> --weekly <pct> --weekly-resets <iso>")

    weekly = snap["weekly_pct"]
    if weekly is not None and weekly >= float(snap["caps"]["weekly_pct"]):
        bad.append(f"weekly is already {weekly:.1f}%, at or past the "
                   f"{snap['caps']['weekly_pct']}% burndown stop -- there is "
                   "nothing left to burn")

    if bad:
        return 1, bad

    lines = ["mode=burndown",
             f"until={iso(when)}",
             # Which it was, because a derived deadline is only as good as the
             # pin it came from and a reader of this file should not have to
             # guess. Nothing branches on it; it is provenance.
             f"until_source={'weekly-reset' if derived else 'stated'}",
             f"armed_at={iso(time.time())}"]
    if scope:
        lines.append(f"scope={scope}")
    lines += ["",
              "# Written by scripts/fleet-burndown.py. See embarch-fleet/budget.md",
              "# 'Burndown'. Deleting this file stops the fleet; setting mode",
              "# back to normal ends the burndown and leaves the pump running.",
              f"# Weekly was {weekly:.1f}% when this was armed." if weekly is not None else "",
              ""]
    PUMP.parent.mkdir(parents=True, exist_ok=True)
    PUMP.write_text("\n".join(l for l in lines if l is not None) + "\n")
    return 0, []


def clear(reason: str | None) -> int:
    """End the burndown, keep the pump. See the module docstring's last
    paragraph: reverting to normal mode rather than deleting the latch means the
    ordinary 90% gate decides what happens next, which after a 429 at 97% is a
    hold it reaches on its own."""
    latch = CONF.pump()
    if latch is None:
        print("the pump is not latched; nothing to clear")
        return 1
    if latch.get("mode") != "burndown":
        print("the pump latch is already in normal mode")
        return 0
    keep = [f"{k}={v}" for k, v in latch.items()
            if k in ("scope",)]
    body = ["mode=normal"] + keep + [
        "",
        f"# Burndown ended {iso(time.time())}"
        + (f": {reason}" if reason else "."),
        "# The pump is still latched -- the normal [limits] caps apply now.",
        ""]
    PUMP.write_text("\n".join(body) + "\n")
    print("burndown ended; pump still latched, normal caps apply"
          + (f" ({reason})" if reason else ""))
    return 0


def report(snap: dict) -> int:
    caps = snap["caps"]
    if snap["active"]:
        left = snap["until"] - time.time()
        print(f"BURNDOWN LIVE -- ends {iso(snap['until'])}, in {human(left)}")
        print(f"  caps: {caps['max_workers']} workers, weekly stop "
              f"{caps['weekly_pct']}%, 5-hour stop {caps['five_hour_pct']}%, "
              f"taper {caps['taper']:g}")
    else:
        print(f"burndown not active -- {snap['why_not']}")
    for label, key in (("weekly", "weekly_pct"), ("5-hour", "five_hour_pct")):
        pct = snap[key]
        reset = snap[f"{'weekly' if key.startswith('week') else 'five_hour'}_resets_at"]
        if pct is None:
            print(f"  {label}: not reported")
        else:
            print(f"  {label}: {pct:5.1f}%  resets in "
                  f"{human(reset - time.time()) if reset else 'unknown'}")
    if snap["derived"]:
        age = snap["pin_age_h"]
        pin = "never pinned" if age is None else f"{age:.1f}h old"
        print("  DERIVED: percentages are a pinned allowance over the "
              "transcripts' token sum,\n           not `rate_limits`. "
              f"Newest /usage pin: {pin} "
              f"(burndown refuses past {cfg('pin_max_age_h', 4):g}h).")
    if snap["cache_problem"]:
        print(f"  PROBLEM: {snap['cache_problem']}")
    return 0 if snap["active"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", action="store_true",
                    help="arm burndown until the pinned weekly reset instant")
    ap.add_argument("--until", metavar="INSTANT",
                    help="arm until this instant instead of the weekly reset "
                         "(no timezone = local)")
    ap.add_argument("--scope", help="comma-separated sub-projects, recorded in "
                                    "the latch the way `fleet start core,ui` does")
    ap.add_argument("--clear", action="store_true",
                    help="end the burndown, leave the pump latched in normal mode")
    ap.add_argument("--reason", help="with --clear, why it ended (recorded in the latch)")
    ap.add_argument("--no-refresh", action="store_true",
                    help="with --until, judge the pin and cache as they are "
                         "instead of running fleet-usage-cache.py first")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    if (args.until or args.arm) and args.clear:
        ap.error("--clear is the opposite of arming")
    # Arming is never the default. `--until` implies it, because passing a
    # deadline can mean nothing else; a bare invocation reports, because a
    # command that latches the fleet when run with no arguments is one typo
    # away from a burndown nobody asked for.
    arming = bool(args.until or args.arm)

    if args.clear:
        rc = clear(args.reason)
        if args.as_json:
            print(json.dumps(snapshot(), default=str))
        return rc

    if arming and not args.no_refresh:
        # **Arming refreshes first, because the owner has just run `/usage`.**
        # The pin comes from the transcripts and the cache from the pin, both on
        # a */4 cron -- so without this, "run /usage, then arm" fails its own
        # freshness check for up to four minutes after the reading it needs is
        # already on disk. One subprocess rather than an import: this is the
        # same command the cron runs, and running exactly that is what makes a
        # refusal here mean the cron would have failed too.
        r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent
                                                / "fleet-usage-cache.py")],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("could not refresh the usage cache "
                  f"(fleet-usage-cache.py exit {r.returncode}):")
            print("  " + (r.stderr or r.stdout).strip().replace("\n", "\n  "))

    snap = snapshot()
    if arming:
        rc, bad = arm(args.until, args.scope, snap)
        snap = snapshot()
        if args.as_json:
            print(json.dumps(dict(snap, refused=bad), default=str))
        elif bad:
            print("REFUSED to arm burndown:")
            for b in bad:
                print(f"  - {b}")
        else:
            left = snap["until"] - time.time()
            src = (snap["latch"] or {}).get("until_source")
            how = " (the pinned weekly reset)" if src == "weekly-reset" else ""
            print(f"BURNDOWN ARMED until {iso(snap['until'])}{how} "
                  f"({human(left)} from now)")
            print(f"  {snap['caps']['max_workers']} workers, no taper, stops at "
                  f"{snap['caps']['weekly_pct']}% weekly / "
                  f"{snap['caps']['five_hour_pct']}% 5-hour")
            if snap["weekly_pct"] is not None:
                print(f"  weekly is {snap['weekly_pct']:.1f}% now")
            print("  The pump is latched. A leg starts on the next tick, or "
                  "say `fleet go` to start one immediately.")
        return rc

    if args.as_json:
        print(json.dumps(snap, default=str))
        return 0 if snap["active"] else 1
    return report(snap)


if __name__ == "__main__":
    sys.exit(main())
