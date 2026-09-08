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

Usage:
    scripts/fleet-usage-reading.py --session 71 --session-resets 2026-09-07T20:00 \\
                                   --weekly 76 --weekly-resets 2026-09-09T07:00
    scripts/fleet-usage-reading.py --show          print the log and the latest pins
Exit status: 0 recorded / printed, 2 bad arguments.
"""
from __future__ import annotations

import argparse
import calendar
import datetime
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

TRANSCRIPTS = Path(os.path.expanduser("~/.claude/projects"))
LOG = CONF.state_dir / "usage-readings.tsv"
HEADER = ("read_at\twindow\tused_pct\tresets_at\twindow_hours\telapsed_pct"
          "\tmeasured_billable\timplied_allowance\tsubagent_share_pct\n")
WINDOWS = {"session": 5.0, "weekly": 168.0}


def burn_since(start: float) -> tuple[int, int, int]:
    """(billable, requests, subagent billable) across every transcript."""
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
                    if when < start:
                        continue
                    b = ((use.get("input_tokens") or 0)
                         + (use.get("output_tokens") or 0)
                         + (use.get("cache_creation_input_tokens") or 0))
                    total += b
                    requests += 1
                    if is_sub:
                        subagent += b
    return total, requests, subagent


def record(name: str, used: float, resets: str) -> str:
    hours = WINDOWS[name]
    try:
        reset_at = datetime.datetime.fromisoformat(resets)
    except ValueError:
        sys.exit(f"--{name}-resets must be ISO local time, e.g. 2026-09-07T20:00")
    start = reset_at.timestamp() - hours * 3600
    total, reqs, sub = burn_since(start)
    now = time.time()
    elapsed = 100 * (now - start) / (hours * 3600)
    allowance = total / (used / 100) if used > 0 else 0
    row = (f"{datetime.datetime.now().astimezone().isoformat(timespec='seconds')}\t"
           f"{name}\t{used:g}\t{reset_at.isoformat()}\t{hours:g}\t{elapsed:.1f}\t"
           f"{total}\t{allowance:.0f}\t{100 * sub / total if total else 0:.1f}\n")
    print(f"{name}: {used:g}% used, {elapsed:.0f}% of the window elapsed\n"
          f"  measured {total:,} billable over {reqs:,} requests "
          f"({100 * sub / total if total else 0:.0f}% subagents)\n"
          f"  implied allowance {allowance:,.0f}; headroom to 80% "
          f"{0.80 * allowance - total:,.0f}, to 90% {0.90 * allowance - total:,.0f}")
    return row


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
    args = ap.parse_args()

    if args.show:
        return show()
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
