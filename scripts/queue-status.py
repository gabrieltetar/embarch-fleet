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

**--refill-owed is the low-water mark, and it replaced refilling on zero.**
Refill used to run only when *nothing* was dispatchable, on the argument that
sweeping eight `open.md` files every twenty minutes to serve a queue that already
has work is pure cost. The argument is right and the threshold was wrong:
measured over the 7.2 h continuous run of 2026-09-05/06, the queue held **one or
zero** dispatchable tasks for **53%** of it and literally zero for 12%, against a
wave of 2 -- so "top up once it is empty" means the wave is starved before the
sweep that would feed it ever fires. A low-water mark keeps the cost argument
(no sweep while the queue is deep) and removes the starvation.

Two ways it fires, because a count is not the whole predicate:

  * fewer dispatchable tasks than `units_per_leg` -- the queue cannot fill the
    leg that is about to run, never mind the one after it; and
  * fewer *distinct scopes* than the wave size -- `supervise.md`'s "at most one
    task per sub-project" is per slot, so three `api` tasks fill exactly one
    slot of a wave of two. That cost 9% of the same run. A count-only gate
    cannot see it.

Exit status is the interface:
  0  there is work (dispatchable > 0)      -- or, with --refill-owed, refill IS owed
  1  there is nothing dispatchable         -- or, with --refill-owed, it is not

Usage:
  scripts/queue-status.py                     human-readable breakdown
  scripts/queue-status.py --count             just the integer
  scripts/queue-status.py --no-supervisor     the listener's question
  scripts/queue-status.py --tasks-only        a leg's refill gate (see below)
  scripts/queue-status.py --refill-owed       the low-water mark (see below)
  scripts/queue-status.py --refill-owed --wave 4
  scripts/queue-status.py --json
  scripts/queue-status.py --warn-below 3      louder about a thin queue
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse
import datetime as dt
import json
import os
import re

TASKS = "tasks"
INBOX = "inbox"
DISPATCHABLE_HW = ("none", "verify-only")

STATE_RE = re.compile(r"^\*\*State:\*\*\s*(.+?)\s*$", re.M)
HW_RE = re.compile(r"^\*\*Hardware:\*\*\s*([a-z-]+)", re.M)
SCOPE_RE = re.compile(r"^\*\*Scope:\*\*\s*([a-z-]+)", re.M)
# A task only the owner's own session can do -- every path it must write is
# reserved (check-ownership.py). Dispatching one wastes a worker that will fail
# the ownership check, so it is gated the way hardware gates one. Absent means
# `no`, unlike Hardware: a missing line here must not gate the whole queue, and
# check-ownership.py is the enforcement either way.
OWNER_RE = re.compile(r"^\*\*Owner:\*\*\s*([a-z-]+)", re.M)
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
    owner = OWNER_RE.search(body)
    return {
        "path": path,
        "state": state,
        "raw_state": raw_state,
        "claim_branch": claim_branch,
        "claim_at": claim_at,
        "hardware": hw.group(1) if hw else "required",
        "scope": scope.group(1) if scope else "unknown",
        "owner": owner.group(1) if owner else "no",
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
    buckets = {"open": [], "recoverable": [], "claimed": [], "gated": [],
               "owner_gated": [], "other": []}
    for t in tasks:
        hw_ok = t["hardware"] in DISPATCHABLE_HW
        if t["state"] not in ("open", "claimed"):
            buckets["other"].append(t)
        elif t["owner"] == "required":
            buckets["owner_gated"].append(t)
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


def refill_owed(b: dict, args) -> int:
    """The low-water mark. Exit 0 when refill is owed, 1 when it is not.

    Deliberately reports BOTH reasons rather than short-circuiting: a leg that
    refills because the count is low still wants to know its scopes are thin,
    because that changes what it should sweep for -- one more `api` task does
    not widen a wave that already has an `api` worker in it.
    """
    ready = b["open"] + b["recoverable"]
    scopes = {t["scope"] for t in ready}
    low_water = args.low_water if args.low_water is not None else CONF.units_per_leg
    wave = args.wave if args.wave is not None else CONF.degraded_workers

    thin_count = len(ready) < low_water
    thin_scopes = len(scopes) < wave
    reasons = []
    if thin_count:
        reasons.append(f"{len(ready)} dispatchable, below the {low_water} "
                       f"low-water mark (units_per_leg)")
    if thin_scopes:
        reasons.append(f"{len(scopes)} distinct scope(s) "
                       f"({', '.join(sorted(scopes)) or 'none'}), below a wave "
                       f"of {wave} -- one task per sub-project is per slot, so "
                       f"a deeper queue in the same scope buys no concurrency")

    if reasons:
        print("REFILL OWED -- " + "; and ".join(reasons))
        return 0
    print(f"refill not owed -- {len(ready)} dispatchable across "
          f"{len(scopes)} scope(s), wave {wave}, low-water {low_water}")
    return 1


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
    ap.add_argument("--refill-owed", action="store_true", dest="refill_owed",
                    help="the low-water mark: exit 0 if refill is owed, 1 if "
                         "not. Owed when dispatchable is below --low-water, or "
                         "when the dispatchable tasks span fewer distinct "
                         "scopes than --wave. Implies --tasks-only, because a "
                         "drop that suppresses the drain that would file it is "
                         "the starvation this flag exists to end.")
    ap.add_argument("--wave", type=int, default=None, metavar="N",
                    help="the wave size this leg will run, from "
                         "usage-budget.py --suggest (default: degraded_workers "
                         "from fleet.toml). Only the scope half of "
                         "--refill-owed reads it.")
    ap.add_argument("--low-water", type=int, default=None, metavar="N",
                    help="refill when dispatchable is below this "
                         "(default: units_per_leg from fleet.toml -- a queue "
                         "that cannot fill the leg about to run is already late)")
    ap.add_argument("--count", action="store_true",
                    help="print only the dispatchable integer")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--root", default=".", help="repo root (default .)")
    args = ap.parse_args()

    now = dt.datetime.now()
    tasks = [parse(p) for p in task_files(os.path.join(args.root, TASKS))]
    tasks_only = args.tasks_only or args.refill_owed
    drops = [] if tasks_only else inbox_drops(os.path.join(args.root, INBOX))
    b = classify(tasks, args.no_supervisor, args.stale_after, now)

    dispatchable = len(b["open"]) + len(b["recoverable"]) + len(drops)
    low = bool(args.warn_below and dispatchable < args.warn_below)

    if args.refill_owed:
        return refill_owed(b, args)

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
            "owner_gated": [t["path"] for t in b["owner_gated"]],
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
    for t in b["owner_gated"]:
        print(f"  owner-only  {t['scope']:<14} {t['path']} (reserved paths)")
    for t in b["other"]:
        print(f"  {t['state']:<11} {t['scope']:<14} {t['path']}")

    if low:
        print(f"LOW QUEUE -- {dispatchable} dispatchable, below {args.warn_below}. "
              "Ask --refill-owed, which is the actual gate; this line is advice.")
    if not dispatchable:
        print("NOTHING DISPATCHABLE -- a leg would refill, and dream if refill also "
              "finds nothing (ops.md section 7).")
    return 0 if dispatchable else 1


if __name__ == "__main__":
    sys.exit(main())
