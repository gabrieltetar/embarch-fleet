#!/usr/bin/env python3
"""Answer "is there work to dispatch right now?" from the task queue itself.

Why this file exists: the count was written out in prose in four places
(`.claude/commands/fleet.md` twice, its `fleet status` row, and
`.claude/commands/supervise.md`), and every one said "State is open". That is
wrong for the listener, and it stalled the fleet for five hours on 2026-09-03:
`tasks/umbrella/001` sat `claimed` by a worker that had died with its leg,
`claimed` is not `open`, so the dispatchable count read 0 and the heartbeat had
nothing to spawn into while the only task in the queue was recoverable in one
commit.

**A claim is not evidence that anyone is working.** `tasks/README.md` settles
staleness exactly rather than by timeout: workers are the supervisor's own
in-process subagents, so *if no supervisor is running, every claim is stale*.
The listener establishes exactly that with `ListAgents` immediately before it
counts -- so at the moment of counting, a claimed task is
dispatchable-with-recovery. Pass --no-supervisor to say so.

A leg does not need that flag: step 0 reclaims stale claims to `open` before it
ever counts, so by then the raw `State:` line is already right. That asymmetry
is the whole bug, and it is why one predicate in one place beats four
restatements of it.

The timeout survives as the backstop for the one case the process tree cannot
settle -- a supervisor alive but wedged -- as --stale-after, default 4 hours,
matching `tasks/README.md`.

**--tasks-only exists because an inbox drop can starve itself.** A drop counts as
dispatchable, and refill is the only thing that drains `inbox/`. So a leg whose
refill gate counts drops sees a non-zero count, skips refill, never drains, and
the drop sits there permanently keeping the count non-zero. The leg passes
--tasks-only and drains `inbox/` unconditionally before counting; the listener
does not, because for it a drop is a real reason to spawn a leg.

Exit status is the interface:
  0  there is work (dispatchable > 0)
  1  there is nothing dispatchable

Usage:
  scripts/queue-status.py                     human-readable breakdown
  scripts/queue-status.py --count             just the integer
  scripts/queue-status.py --no-supervisor     the listener's question
  scripts/queue-status.py --tasks-only        a leg's refill gate (see below)
  scripts/queue-status.py --json
  scripts/queue-status.py --warn-below 3      louder about a thin queue
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys

TASKS = "tasks"
INBOX = "inbox"
DISPATCHABLE_HW = ("none", "verify-only")

STATE_RE = re.compile(r"^\*\*State:\*\*\s*(.+?)\s*$", re.M)
HW_RE = re.compile(r"^\*\*Hardware:\*\*\s*([a-z-]+)", re.M)
SCOPE_RE = re.compile(r"^\*\*Scope:\*\*\s*([a-z-]+)", re.M)
CLAIM_RE = re.compile(r"^claimed by\s+(\S+?),\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")


def parse(path: str) -> dict:
    """One task file. A missing or unreadable field degrades to the safe
    reading, never the permissive one: no Hardware line means `required`
    (tasks/README.md), which is not dispatchable."""
    with open(path, encoding="utf-8") as f:
        body = f.read()

    m = STATE_RE.search(body)
    raw_state = m.group(1).strip() if m else "unknown"

    claim_branch = claim_at = None
    state = raw_state.split()[0] if raw_state else "unknown"
    cm = CLAIM_RE.match(raw_state)
    if cm:
        state = "claimed"
        claim_branch = cm.group(1)
        try:
            claim_at = dt.datetime.strptime(cm.group(2), "%Y-%m-%d %H:%M")
        except ValueError:
            claim_at = None

    hw = HW_RE.search(body)
    scope = SCOPE_RE.search(body)
    return {
        "path": path,
        "state": state,
        "raw_state": raw_state,
        "claim_branch": claim_branch,
        "claim_at": claim_at,
        "hardware": hw.group(1) if hw else "required",
        "scope": scope.group(1) if scope else "unknown",
    }


def task_files(root: str) -> list[str]:
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".md") and name != "README.md":
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def inbox_drops(root: str) -> list[str]:
    if not os.path.isdir(root):
        return []
    return sorted(os.path.join(root, n) for n in os.listdir(root)
                  if n.endswith(".md") and n != "README.md")


def stale_reason(task: dict, no_supervisor: bool, after_h: float,
                 now: dt.datetime) -> str | None:
    """Why this claim is releasable, or None if it must be respected."""
    if task["state"] != "claimed":
        return None
    if no_supervisor:
        return "no supervisor alive, so every claim is stale (tasks/README.md)"
    if task["claim_at"] is None:
        return "claim line carries no parseable timestamp"
    age_h = (now - task["claim_at"]).total_seconds() / 3600.0
    if age_h >= after_h:
        return f"claimed {age_h:.1f}h ago (backstop {after_h:g}h)"
    return None


def classify(tasks: list[dict], no_supervisor: bool, after_h: float,
             now: dt.datetime) -> dict:
    buckets = {"open": [], "recoverable": [], "claimed": [], "gated": [], "other": []}
    for t in tasks:
        hw_ok = t["hardware"] in DISPATCHABLE_HW
        if t["state"] not in ("open", "claimed"):
            buckets["other"].append(t)
        elif not hw_ok:
            buckets["gated"].append(t)
        elif t["state"] == "open":
            buckets["open"].append(t)
        else:
            why = stale_reason(t, no_supervisor, after_h, now)
            if why:
                t["stale_reason"] = why
                buckets["recoverable"].append(t)
            else:
                buckets["claimed"].append(t)
    return buckets


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-supervisor", action="store_true",
                    help="caller has established no supervisor is running, so "
                         "every claim is stale (the listener's case)")
    ap.add_argument("--stale-after", type=float, default=4.0, metavar="H",
                    help="hours after which a claim is stale even if a supervisor "
                         "may be alive (default 4, per tasks/README.md)")
    ap.add_argument("--warn-below", type=int, default=2, metavar="N",
                    help="print a LOW QUEUE line when dispatchable is under N "
                         "(default 2); 0 disables")
    ap.add_argument("--tasks-only", action="store_true",
                    help="exclude inbox/ drops from the count. A leg's refill "
                         "gate must pass this: refill is the only thing that "
                         "drains inbox/, so counting a drop as dispatchable "
                         "keeps the count non-zero, suppresses refill, and the "
                         "drop starves itself. The listener does NOT pass it -- "
                         "a drop is a real reason to spawn a leg.")
    ap.add_argument("--count", action="store_true",
                    help="print only the dispatchable integer")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--root", default=".", help="repo root (default .)")
    args = ap.parse_args()

    now = dt.datetime.now()
    tasks = [parse(p) for p in task_files(os.path.join(args.root, TASKS))]
    drops = [] if args.tasks_only else inbox_drops(os.path.join(args.root, INBOX))
    b = classify(tasks, args.no_supervisor, args.stale_after, now)

    dispatchable = len(b["open"]) + len(b["recoverable"]) + len(drops)
    low = bool(args.warn_below and dispatchable < args.warn_below)

    if args.count:
        print(dispatchable)
        return 0 if dispatchable else 1

    if args.as_json:
        print(json.dumps({
            "dispatchable": dispatchable,
            "open": [t["path"] for t in b["open"]],
            "recoverable": [{"path": t["path"], "why": t["stale_reason"],
                             "branch": t["claim_branch"]} for t in b["recoverable"]],
            "claimed_respected": [t["path"] for t in b["claimed"]],
            "hardware_gated": [{"path": t["path"], "hardware": t["hardware"]}
                               for t in b["gated"]],
            "other": [{"path": t["path"], "state": t["state"]} for t in b["other"]],
            "inbox": drops,
            "low": low,
        }))
        return 0 if dispatchable else 1

    print(f"dispatchable: {dispatchable}")
    for t in b["open"]:
        print(f"  open        {t['scope']:<14} {t['path']}")
    for t in b["recoverable"]:
        print(f"  recoverable {t['scope']:<14} {t['path']}")
        print(f"              -> {t['stale_reason']}; branch {t['claim_branch']}")
    for p in drops:
        print(f"  inbox drop  {'-':<14} {p}")
    for t in b["claimed"]:
        print(f"  claimed     {t['scope']:<14} {t['path']} (respected)")
    for t in b["gated"]:
        print(f"  hw-gated    {t['scope']:<14} {t['path']} ({t['hardware']})")
    for t in b["other"]:
        print(f"  {t['state']:<11} {t['scope']:<14} {t['path']}")

    if low:
        print(f"LOW QUEUE -- {dispatchable} dispatchable, below {args.warn_below}. "
              "Refill runs on the next leg; say so rather than waiting for zero.")
    if not dispatchable:
        print("NOTHING DISPATCHABLE -- a leg would refill, and dream if refill also "
              "finds nothing (embarch-parallel-agents-ops.md section 7).")
    return 0 if dispatchable else 1


if __name__ == "__main__":
    sys.exit(main())
