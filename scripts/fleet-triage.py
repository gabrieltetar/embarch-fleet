#!/usr/bin/env python3
"""Answer the question the watchdog cannot: WHY has the fleet stopped?

`fleet-deadman.py` reports "no progress since <t>, so I stopped it restarting"
and then says, correctly, that it cannot tell a wedged listener from a dead one
from a closed window from a slept machine, and does not guess. That honesty is
right and the gap is expensive: on 2026-09-07 the answer was none of those four
-- a leg was **orphaned**, holding two finished units -- and finding that out
took a person reading four transcripts and three remotes by hand.

This does that reading. Four signals, each cheap and each a fact:

  1. `<state_dir>/tick` -- when the fleet last made progress.
  2. The newest **subagent** transcript under the listener session's directory.
     Agent activity AFTER the last tick is the orphan signature: work happened
     that nothing recorded as progress.
  3. `git ls-remote --heads <remote> 'agent/*'` per repo, cross-checked against
     `origin/main`. An unmerged pushed branch is a **finished** worker: pushing
     is a worker's last act, so presence proves completion (absence proves
     nothing -- see `leg.md`, and leg 007's re-dispatch of two live workers).
  4. Whether any Claude process is alive at all.

**It never concludes a worker died, and it never touches anything.** Read-only
by construction: the recovery it recommends is always "relatch and let phase 0
run", because a leg's own gate is a better arbiter than this script's guess.

Usage:
  scripts/fleet-triage.py            human-readable verdict and evidence
  scripts/fleet-triage.py --json     the same, machine-readable
Exit status: 0 the fleet looks alive, 1 stopped with a diagnosis, 2 no diagnosis.
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
from fleetconf import CONF  # noqa: E402

PROJECTS = Path(os.path.expanduser("~/.claude/projects"))


def project_dir() -> Path:
    """Claude Code's transcript directory for the listener's cwd.

    The slug is the absolute path with separators replaced by dashes -- derived
    from `fleet.toml` rather than written down, so a second instance needs no
    edit here.
    """
    return PROJECTS / str(CONF.doc_repo).replace("/", "-")


def newest_agent_activity(proj: Path):
    """(mtime, path) of the newest subagent transcript, or None.

    Subagents of a session -- a leg, and every worker a leg dispatches -- all
    land under that session's `subagents/`, so one glob covers the whole tree
    the fleet runs in.
    """
    best = None
    for p in proj.glob("*/subagents/*.jsonl"):
        try:
            m = p.stat().st_mtime
        except OSError:
            continue
        if best is None or m > best[0]:
            best = (m, p)
    return best


def unmerged_agent_branches():
    """Pushed `agent/*` branches not yet on their repo's origin/main.

    A worker's last act is pushing both halves, so each of these is finished
    work that nothing has landed. This is the signal that separates "orphaned
    leg" from every other stall, and the one the 2026-09-07 triage turned on.
    """
    out = []
    for repo in sorted(CONF.root.iterdir()):
        if not (repo / ".git").exists():
            continue
        r = subprocess.run(["git", "-C", str(repo), "ls-remote", "--heads", "origin", "agent/*"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            sha, _, ref = line.partition("\t")
            if not sha:
                continue
            merged = subprocess.run(
                ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, "origin/main"],
                capture_output=True)
            if merged.returncode != 0:
                out.append((repo.name, ref.replace("refs/heads/", ""), sha[:7]))
    return out


def claude_alive() -> int:
    r = subprocess.run(["pgrep", "-fc", "native-binary/claude"], capture_output=True, text=True)
    try:
        return int(r.stdout.strip() or 0)
    except ValueError:
        return 0


def claimed_tasks():
    tasks = CONF.doc_repo / "tasks"
    out = []
    if not tasks.is_dir():
        return out
    for p in sorted(tasks.rglob("*.md")):
        if p.name == "README.md":
            continue
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:400]
        except OSError:
            continue
        for line in head.splitlines():
            if line.startswith("**State:**") and "claimed" in line:
                out.append(str(p.relative_to(CONF.doc_repo)))
                break
    return out


def ago(t: float) -> str:
    d = int(time.time() - t)
    return f"{d // 60}m{d % 60:02d}s ago" if d < 7200 else f"{d // 3600}h{(d % 3600) // 60:02d}m ago"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    tick = CONF.state_dir / "tick"
    pump = CONF.state_dir / "pump"
    tick_m = tick.stat().st_mtime if tick.exists() else None
    activity = newest_agent_activity(project_dir())
    branches = unmerged_agent_branches()
    procs = claude_alive()
    claims = claimed_tasks()

    ev = {
        "tick": tick_m,
        "tick_ago_s": None if tick_m is None else int(time.time() - tick_m),
        "pump_latched": pump.exists(),
        "newest_agent_activity": None if activity is None else activity[0],
        "activity_after_tick_s": (None if (activity is None or tick_m is None)
                                  else int(activity[0] - tick_m)),
        "unmerged_pushed_branches": [f"{r}:{b}@{s}" for r, b, s in branches],
        "claude_processes": procs,
        "claimed_tasks": claims,
    }

    # Ordered most-specific first: each verdict is a conjunction of facts, and
    # the first that matches is the narrowest true statement available.
    if procs == 0:
        verdict, why = "WINDOW_GONE", (
            "No Claude process is running, so the listener window is closed or its "
            "process died. Nothing was wedged; there is nothing to wake.")
        fix = "Reopen the listener window, arm it with /fleet start, then say `fleet start` in the channel."
    elif branches and ev["activity_after_tick_s"] and ev["activity_after_tick_s"] > 60:
        verdict, why = "ORPHANED_LEG", (
            f"{len(branches)} pushed branch(es) are unmerged and an agent was still "
            f"writing {ev['activity_after_tick_s']}s after the last tick. That is a leg "
            "that stopped while its workers finished -- the completion notification did "
            "not reach it. Nothing is lost: the work is on the remotes.")
        fix = ("Relatch (`fleet start`). Phase 0 re-lands a pushed branch rather than "
               "blocking it (tasks/README.md), and the task files should say so.")
    elif branches:
        verdict, why = "UNMERGED_WORK", (
            f"{len(branches)} pushed branch(es) are unmerged, but no agent wrote after "
            "the last tick, so this may be a leg killed between the push and the fold.")
        fix = "Relatch. Phase 0 re-lands a pushed branch rather than blocking it."
    elif claims:
        verdict, why = "CLAIMED_NO_WORK", (
            f"{len(claims)} task(s) are claimed with nothing pushed and no agent activity "
            "since the tick. A worker's tree is clean for the whole reading half of its "
            "run, so this is EQUALLY a live worker and a dead one -- do not conclude "
            "either from here.")
        fix = ("If the listener window is responsive the leg may still be running; give it "
               "a worker's twenty minutes before relatching.")
    else:
        verdict, why = "IDLE_OR_WEDGED", (
            "A Claude process is alive, nothing is claimed, nothing is pushed and no agent "
            "has written since the tick. Either the queue went dry, the pump was never "
            "latched, or the listener is wedged. This script cannot tell those apart.")
        fix = "Check the listener window directly, then `fleet start` in the channel."

    if args.as_json:
        print(json.dumps({"verdict": verdict, "why": why, "fix": fix, "evidence": ev}, indent=2))
    else:
        print(f"VERDICT: {verdict}\n\n{why}\n")
        print("Evidence:")
        print(f"  tick               {'never' if tick_m is None else ago(tick_m)}")
        print(f"  pump latch         {'present' if ev['pump_latched'] else 'absent (fleet stopped)'}")
        if activity:
            print(f"  newest agent write {ago(activity[0])}  ({activity[1].name})")
        else:
            print("  newest agent write none found")
        print(f"  claude processes   {procs}")
        for b in ev["unmerged_pushed_branches"]:
            print(f"  UNMERGED           {b}")
        for c in claims:
            print(f"  claimed            {c}")
        print(f"\nRecommended: {fix}")

    if verdict == "IDLE_OR_WEDGED":
        return 2
    return 0 if ev["pump_latched"] and not branches else 1


if __name__ == "__main__":
    sys.exit(main())
