#!/usr/bin/env python3
"""Record one `/usage` reading against the burn measured from the same window.

**Why this exists.** The quota percentages are the number the budget gate was
designed around and they never reach this machine's disk: `rate_limits` arrives
only in a status line payload, and the VS Code extension runs none. So
`usage-budget.py` degrades to a token-burn proxy against a ceiling calibrated
from **two** observations -- 15.4M in a window that did not 429, 17.7M in one
that did. On 2026-09-07 that ceiling read 101% while `/usage` said the session
window was 71% used, and the fleet throttled itself to one worker with a third
of the window left.

A `/usage` reading is a percentage, which is a numerator over a denominator.
**The denominator is the seat's allowance and it changes essentially never; the
numerator is `message.usage`, which is on disk for every request ever made.** So
one pasted reading pins the allowance, and from then on the percentage is
arithmetic rather than a guess. Each new reading re-pins it and corrects drift.

**The windows are fixed, not rolling, and that matters.** `/usage` reports a
reset instant ("resets Sep 7, 8pm"), so the numerator must be summed from
`resets_at - length`, not over a trailing N hours. `usage-budget.py --burn` sums
a trailing five hours, which is a different quantity and reads high mid-window.

**What it cannot do.** `billable` here is input + output + cache writes, with
cache reads excluded because they bill at roughly a tenth -- a ratio, not a
contract. Whatever Anthropic actually meters, the implied allowance absorbs a
constant factor of it, so the percentage stays honest while the workload mix
holds and drifts when it changes. That is what re-pinning is for. **Never
present an implied allowance as the published limit.**

**Since 2026-09-08 nothing has to be pasted.** `/usage` renders its answer into
the terminal, and Claude Code writes what it rendered into the session
transcript as a `local_command` record -- both percentages and both reset
instants, in the owner's own timezone. `--scan` finds those, pins each one that
is newer than the newest row already logged, and runs on the same `*/4` cron
that writes the cache. So the pin is now a side effect of the owner glancing at
his usage, and the only manual step left is glancing.

The pasted form below still works and is still the fallback: it is the only
route if the rendered format ever changes, and `--scan` skips anything it cannot
parse rather than guessing.

Usage:
    scripts/fleet-usage-reading.py --scan          pin every /usage on disk
    scripts/fleet-usage-reading.py --session 71 --session-resets 2026-09-07T20:00 \\
                                   --weekly 76 --weekly-resets 2026-09-09T07:00
    scripts/fleet-usage-reading.py --show          print the log and the latest pins
Exit status: 0 recorded / printed, 1 --scan found nothing new, 2 bad arguments.
"""
from __future__ import annotations

import argparse
import calendar
import datetime
import json
import os
import re
import sys
import time
import zoneinfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

TRANSCRIPTS = Path(os.path.expanduser("~/.claude/projects"))
LOG = CONF.state_dir / "usage-readings.tsv"
HEADER = ("read_at\twindow\tused_pct\tresets_at\twindow_hours\telapsed_pct"
          "\tmeasured_billable\timplied_allowance\tsubagent_share_pct\n")
WINDOWS = {"session": 5.0, "weekly": 168.0}


def burn_since(start: float) -> tuple[int, int, int]:
    """(billable, requests, subagent billable) from `start` until now."""
    return burn_between(start, None)


def burn_between(start: float, end: float | None) -> tuple[int, int, int]:
    """(billable, requests, subagent billable) across every transcript.

    `end` exists for `--scan`. A reading scraped out of a transcript describes
    the seat as it was **when `/usage` ran**, so its numerator must stop there:
    summing to now would divide a percentage from one instant by a token count
    from another, and the implied allowance would come out high by exactly the
    burn in between. Live use passes `None`, which means now.
    """
    total = subagent = requests = 0
    for root, _dirs, files in os.walk(TRANSCRIPTS):
        is_sub = os.path.basename(root) == "subagents"
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            try:
                if os.path.getmtime(path) < start:
                    continue          # cannot hold a request inside the window
                fh = open(path, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    msg = rec.get("message")
                    use = msg.get("usage") if isinstance(msg, dict) else None
                    if not isinstance(use, dict):
                        continue
                    try:
                        when = calendar.timegm(time.strptime(
                            rec.get("timestamp", "")[:19], "%Y-%m-%dT%H:%M:%S"))
                    except ValueError:
                        continue
                    if when < start or (end is not None and when > end):
                        continue
                    b = ((use.get("input_tokens") or 0)
                         + (use.get("output_tokens") or 0)
                         + (use.get("cache_creation_input_tokens") or 0))
                    total += b
                    requests += 1
                    if is_sub:
                        subagent += b
    return total, requests, subagent


def record(name: str, used: float, resets: str, at: float | None = None) -> str:
    """One row. `at` is when the reading was TAKEN -- now for a pasted one, the
    transcript's own timestamp for a scraped one."""
    hours = WINDOWS[name]
    try:
        reset_at = datetime.datetime.fromisoformat(resets)
    except ValueError:
        sys.exit(f"--{name}-resets must be ISO local time, e.g. 2026-09-07T20:00")
    start = reset_at.timestamp() - hours * 3600
    now = time.time() if at is None else at
    total, reqs, sub = burn_between(start, None if at is None else at)
    elapsed = 100 * (now - start) / (hours * 3600)
    allowance = total / (used / 100) if used > 0 else 0
    row = (f"{datetime.datetime.fromtimestamp(now).astimezone().isoformat(timespec='seconds')}\t"
           f"{name}\t{used:g}\t{reset_at.isoformat()}\t{hours:g}\t{elapsed:.1f}\t"
           f"{total}\t{allowance:.0f}\t{100 * sub / total if total else 0:.1f}\n")
    print(f"{name}: {used:g}% used, {elapsed:.0f}% of the window elapsed\n"
          f"  measured {total:,} billable over {reqs:,} requests "
          f"({100 * sub / total if total else 0:.0f}% subagents)\n"
          f"  implied allowance {allowance:,.0f}; headroom to 80% "
          f"{0.80 * allowance - total:,.0f}, to 90% {0.90 * allowance - total:,.0f}")
    return row


# `/usage` renders into the terminal, and Claude Code writes what it rendered
# into the session transcript as a `local_command` record. That text carries
# BOTH percentages and BOTH reset instants -- everything a pin needs -- so a
# reading that used to be pasted by hand is on disk within a second of the owner
# typing the command. Discovered 2026-09-08 while answering "can you fill the
# percentages automatically when I do /usage?": yes, and this is how.
#
# **This is not `rate_limits`.** That field still reaches nothing but a status
# line (budget.md, and open.md's remaining question). What is scraped here is
# the same first-party numbers in rendered form -- better than the pasted route
# only in that nobody has to paste, and identical in what it can be trusted for.
STDOUT_RE = re.compile(r"<local-command-stdout>(.*?)</local-command-stdout>", re.S)
LINE_RE = {
    "session": re.compile(r"Current session:\s*([\d.]+)%\s*used"
                          r"(?:[^\n]*?resets\s+([^\n(]+?)\s*\(([^)\n]+)\))?", re.I),
    # "(all models)" distinguishes the real weekly window from the per-model
    # rows `/usage` prints beside it. Matching "Current week" loosely would pick
    # up "Current week (Fable): 0% used" and pin the allowance to zero.
    "weekly": re.compile(r"Current week \(all models\):\s*([\d.]+)%\s*used"
                         r"(?:[^\n]*?resets\s+([^\n(]+?)\s*\(([^)\n]+)\))?", re.I),
}
RESET_FORMATS = ("%b %d, %I:%M%p", "%b %d, %I%p", "%b %d %I:%M%p", "%b %d %I%p")


def parse_reset(text: str, tzname: str, taken: float, hours: float):
    """The reset instant `/usage` printed, as an aware datetime, or None.

    `/usage` prints no year ("resets Sep 9, 7am"), so the year comes from the
    reading's own timestamp and is rolled forward if that puts the reset in the
    past -- the December-to-January case, which would otherwise pin a weekly
    window eleven months wide.

    **The result is then checked against the window it claims to be.** A reset
    more than one window-length ahead of the reading is not a reset this code
    understood, and a wrong one is worse than none: it moves the window start,
    which moves the numerator, which moves the implied allowance. So an
    unparseable or implausible instant returns None and that window is skipped
    while the other is still recorded.
    """
    try:
        tz = zoneinfo.ZoneInfo(tzname.strip())
    except Exception:
        tz = datetime.datetime.now().astimezone().tzinfo
    base = datetime.datetime.fromtimestamp(taken, tz)
    for fmt in RESET_FORMATS:
        try:
            naive = datetime.datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
        for year in (base.year, base.year + 1):
            try:
                when = naive.replace(year=year, tzinfo=tz)
            except ValueError:
                continue
            ahead = (when.timestamp() - taken) / 3600.0
            if 0 <= ahead <= hours + 1:
                return when
        return None
    return None


def usage_records() -> list[tuple[float, dict]]:
    """Every `/usage` output on disk: (when it ran, {window: (pct, reset)}).

    Newest last. Cheap string tests before `json.loads` for the same reason
    `usage-budget.py` pre-filters its 429 scan -- these transcripts hold tens of
    thousands of requests and this runs on a `*/4` cron.
    """
    found: list[tuple[float, dict]] = []
    for root, _dirs, files in os.walk(TRANSCRIPTS):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            try:
                fh = open(os.path.join(root, name), encoding="utf-8", errors="replace")
            except OSError:
                continue
            with fh as f:
                for line in f:
                    if "local-command-stdout" not in line or "Current session:" not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    m = STDOUT_RE.search(rec.get("content") or "")
                    if not m:
                        continue
                    try:
                        taken = calendar.timegm(time.strptime(
                            rec.get("timestamp", "")[:19], "%Y-%m-%dT%H:%M:%S"))
                    except ValueError:
                        continue
                    windows = {}
                    for win, pat in LINE_RE.items():
                        hit = pat.search(m.group(1))
                        if not hit or hit.group(2) is None:
                            continue
                        reset = parse_reset(hit.group(2), hit.group(3) or "",
                                            taken, WINDOWS[win])
                        if reset is not None:
                            windows[win] = (float(hit.group(1)), reset)
                    if windows:
                        found.append((taken, windows))
    found.sort(key=lambda r: r[0])
    return found


def newest_read_at() -> float:
    """When the log's newest row was taken. 0 if there are none.

    This is the dedupe: a `/usage` at or before it has already been pinned,
    whether it was pasted by hand or scraped by an earlier run. Comparing
    instants rather than remembering which records were consumed means the log
    is the only state, and re-running the scan is free.
    """
    try:
        rows = LOG.read_text().splitlines()[1:]
    except OSError:
        return 0.0
    newest = 0.0
    for row in rows:
        try:
            newest = max(newest, datetime.datetime.fromisoformat(
                row.split("\t")[0]).timestamp())
        except (ValueError, IndexError):
            continue
    return newest


def scan(quiet: bool = False) -> int:
    """Pin every `/usage` reading newer than the newest row already logged."""
    cutoff = newest_read_at()
    fresh = [(t, w) for t, w in usage_records() if t > cutoff]
    if not fresh:
        if not quiet:
            print("no /usage output on disk newer than the newest recorded "
                  f"reading ({datetime.datetime.fromtimestamp(cutoff)})"
                  if cutoff else "no /usage output found in any transcript")
        return 1
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a") as fh:
        if new:
            fh.write(HEADER)
        for taken, windows in fresh:
            if not quiet:
                print(f"/usage at {datetime.datetime.fromtimestamp(taken)}:")
            for win, (pct, reset) in sorted(windows.items()):
                row = record(win, pct, reset.isoformat(), at=taken)
                fh.write(row)
                if quiet:
                    print(f"  pinned {win} {pct:g}% from /usage at "
                          f"{datetime.datetime.fromtimestamp(taken):%H:%M %d-%b}")
    if not quiet:
        print(f"\nrecorded in {LOG}")
    return 0


def show() -> int:
    if not LOG.is_file():
        print(f"no readings yet at {LOG}")
        return 0
    rows = LOG.read_text().splitlines()
    print("\n".join(rows))
    latest: dict[str, str] = {}
    for line in rows[1:]:
        f = line.split("\t")
        if len(f) > 7:
            latest[f[1]] = f[7]
    if latest:
        print("\nlatest implied allowances (billable tokens):")
        for k, v in latest.items():
            print(f"  {k:<8} {int(float(v)):,}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--session", type=float, help="session %% from /usage")
    ap.add_argument("--session-resets", help="its reset instant, local ISO")
    ap.add_argument("--weekly", type=float, help="weekly %% from /usage")
    ap.add_argument("--weekly-resets", help="its reset instant, local ISO")
    ap.add_argument("--show", action="store_true", help="print the log and exit")
    ap.add_argument("--scan", action="store_true",
                    help="pin every /usage output found in the transcripts that "
                         "is newer than the newest recorded reading")
    ap.add_argument("--quiet", action="store_true",
                    help="with --scan, one line per pin and nothing when there "
                         "is nothing new (for the cron)")
    args = ap.parse_args()

    if args.show:
        return show()
    if args.scan:
        return scan(args.quiet)
    pairs = [("session", args.session, args.session_resets),
             ("weekly", args.weekly, args.weekly_resets)]
    given = [(n, u, r) for n, u, r in pairs if u is not None]
    if not given:
        ap.print_help()
        return 2
    for name, used, resets in given:
        if not resets:
            sys.exit(f"--{name} needs --{name}-resets: a percentage with no window "
                     "start cannot be turned into an allowance")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    with LOG.open("a") as fh:
        if new:
            fh.write(HEADER)
        for name, used, resets in given:
            fh.write(record(name, used, resets))
    print(f"\nrecorded in {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
