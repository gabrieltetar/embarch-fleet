#!/usr/bin/env python3
"""Refuse to start a second worker into a task another worker already holds.

The claim commit is the interlock against **two supervisors** dispatching one
task. There has never been one against **one supervisor** dispatching it twice,
and branch, worktree and ownership row are all keyed on the task -- so two
workers on one task share every one of them and are protected by none.

Leg 012 ran both of its first two tasks twice, concurrently, in the same
worktrees (`tasks/doc/009`). It concluded its workers were dead and re-dispatched;
both were alive and mid-pass. `api/012` survived only because the second worker's
`old_string`s no longer matched. `umbrella/012` reached `origin`: the second
worker committed and pushed, and the first then force-pushed over it. **No damage
by luck of content only** -- `git diff` between the two commits was empty, so the
rewrite swapped an identical tree under a different message. One line of the
second worker's own would have been deleted from pushed history with no conflict
and nothing to notice.

**Why an existing worktree, rather than a dirty one.** A dirty test is the
obvious guard and it is not enough: a worker's tree is clean for the entire
*reading* half of its run, and leg 012's supervisor sampled exactly there -- true
at the instant taken, false ninety seconds later. `ops.md` §3 already reads the
worktree instead of the branch because a branch's commit count is a bad liveness
probe; leg 012 established that the worktree is a bad one too, for the same
reason. Neither distinguishes "never started" from "about to write".

**Existence has no such gap.** A fresh dispatch *creates* its worktrees, so
finding them already there is evidence rather than a state to reuse. That is
strictly stronger than the dirty test and it is what this checks. The dirty test
is kept as a second opinion under `--allow-existing`, sampled twice seconds
apart, for the one legitimate case: a leg resuming after a kill, where the
worktrees are its own dead workers' and `ops.md` §3 recovery governs.

**This is a backstop, not the root cause.** The root cause is that a supervisor
may conclude a worker died from repo state at all; `tasks/README.md` settles
claim staleness by the **process tree**, and that is the rule that should govern
re-dispatch -- `ListAgents`, not `git status`. No script can check that from
outside the session, so it stays prose. This catches the consequence.

Usage:
  scripts/check-dispatch.py --worktree PATH [--worktree PATH ...]
  scripts/check-dispatch.py --worktree PATH --allow-existing   # a recovery leg
  scripts/check-dispatch.py --worktree PATH --settle 5         # seconds between samples
Exit status: 0 safe to dispatch, 1 refused, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def porcelain(path: Path) -> str | None:
    r = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", action="append", default=[], metavar="PATH",
                    help="a worktree this dispatch is about to create (repeatable)")
    ap.add_argument("--allow-existing", action="store_true",
                    help="a recovery leg reclaiming its predecessor's worktrees: "
                         "existence is expected, so fall back to sampling for activity")
    ap.add_argument("--settle", type=float, default=3.0,
                    help="seconds between the two samples (default %(default)s)")
    args = ap.parse_args()
    if not args.worktree:
        print("--worktree is required (repeatable)", file=sys.stderr)
        return 2

    existing = [Path(p) for p in args.worktree if Path(p).exists()]
    if existing and not args.allow_existing:
        print(f"{len(existing)} worktree(s) already exist, so this task is already "
              "dispatched:\n", file=sys.stderr)
        for p in existing:
            print(f"  {p}", file=sys.stderr)
        print("\nA fresh dispatch CREATES its worktrees. Finding them is evidence that a\n"
              "worker holds this task -- not a state to reuse. Leg 012 reused them and ran\n"
              "two workers in one tree; one force-pushed over the other's pushed commit.\n\n"
              "If you believe that worker is dead, prove it with the PROCESS TREE\n"
              "(ListAgents), which is what tasks/README.md settles staleness by -- never\n"
              "with `git status` or a branch's commit count, both of which read clean for\n"
              "the whole reading half of a worker's run. Then recover per ops.md §3 and\n"
              "re-run with --allow-existing.", file=sys.stderr)
        return 1

    if not existing:
        print(f"OK: none of the {len(args.worktree)} worktree(s) exist; safe to dispatch.")
        return 0

    first = {p: porcelain(p) for p in existing}
    time.sleep(args.settle)
    second = {p: porcelain(p) for p in existing}

    busy = []
    for p in existing:
        a, b = first[p], second[p]
        if a is None or b is None:
            busy.append((p, "not a git worktree"))
        elif a.strip() or b.strip():
            busy.append((p, f"dirty ({len(b.strip().splitlines())} path(s))"))
        elif a != b:
            busy.append((p, "changed between samples"))
    if busy:
        print(f"{len(busy)} worktree(s) show activity; something is working in there:\n",
              file=sys.stderr)
        for p, why in busy:
            print(f"  {p} -- {why}", file=sys.stderr)
        print("\nDo not dispatch into it. Two samples were taken because ONE can land in a\n"
              "gap between another agent's tool calls -- which is exactly what leg 012's\n"
              "single sample did at 21:26, reading clean while a worker was mid-pass.",
              file=sys.stderr)
        return 1

    print(f"OK: {len(existing)} existing worktree(s), clean across two samples "
          f"{args.settle:g}s apart.\nThat is consistent with a dead worker, and NOT proof "
          "of one -- a tree is clean for the\nwhole reading half of a live worker's run "
          "too. Confirm with ListAgents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
