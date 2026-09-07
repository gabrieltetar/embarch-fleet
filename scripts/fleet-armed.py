#!/usr/bin/env python3
"""Record what a window was armed with, and answer whether it is still current.

A `CronCreate` job keeps the prompt it was armed with for its whole life. Every
other generated file in the instance is re-read by whatever uses it -- an agent
definition on the next spawn, `fleet.md`'s vocabulary on the next tick -- so the
cron blocks in `fleet.md` and `fleet-watch.md` are the only place where editing
the file and deploying it changes nothing at all. The window has to be re-armed,
by a person, in the window.

Nothing recorded what any window was armed WITH, so `deploy.py` inferred it from
the repo, and on 2026-09-07 the inference failed in the expensive direction: an
`install.py` run by hand had already put the new text in the instance, so the
comparison read new-against-new, reported nothing owed, and the live listener
kept spawning legs with a tick prompt that pointed them at the wrong file. That
was leg 029.

`--stamp` is therefore part of arming, immediately after the `CronCreate`, and
it stores the block **as text**: a stale window shows up as a diff a person can
read rather than two unequal hashes. `--clear` belongs with disarming, because a
stamp for a window that no longer has a cron job claims a job exists.

The stamp says what was armed, never what is running. A closed window leaves its
stamp behind and nothing can tell from disk that it is gone -- but closing VS
Code is the fleet's kill switch and re-arming re-stamps, so the residue is a
stamp that is merely unused. The failure this closes is the other one: a window
that IS running, on wording nobody can see.

Usage:
  scripts/fleet-armed.py --stamp .claude/commands/fleet.md
  scripts/fleet-armed.py --clear .claude/commands/fleet.md
  scripts/fleet-armed.py --check          every armed prompt, against the instance
Exit status: 0 all current / stamped, 1 something is stale or unstamped.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import ARMED_PROMPTS, CONF, armed_stamp, cron_block  # noqa: E402


def _instance_block(rel: str) -> str | None:
    f = CONF.doc_repo / rel
    try:
        return cron_block(f.read_text())
    except OSError:
        return None


def stamp(rel: str) -> int:
    block = _instance_block(rel)
    if block is None:
        print(f"cannot read {CONF.doc_repo / rel}", file=sys.stderr)
        return 1
    if not block:
        # A prompt file with no blockquote is a template that changed shape, or
        # the wrong file. Stamping nothing would read as "armed and current".
        print(f"{rel} has no `>` block -- nothing to stamp", file=sys.stderr)
        return 1
    p = armed_stamp(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(block + "\n")
    print(f"stamped {rel} ({len(block.splitlines())} lines) -> {p}")
    return 0


def clear(rel: str) -> int:
    p = armed_stamp(rel)
    existed = p.exists()
    p.unlink(missing_ok=True)
    print(f"{'cleared' if existed else 'no stamp for'} {rel}")
    return 0


def check(verbose: bool) -> int:
    worst = 0
    for rel in ARMED_PROMPTS:
        p = armed_stamp(rel)
        fresh = _instance_block(rel)
        if fresh is None:
            print(f"  MISSING   {rel} -- not in the instance")
            worst = 1
            continue
        if not p.exists():
            print(f"  UNSTAMPED {rel} -- armed before this was recorded, or never armed")
            worst = 1
            continue
        was = p.read_text().rstrip("\n")
        if was == fresh:
            print(f"  current   {rel}")
            continue
        worst = 1
        print(f"  STALE     {rel} -- the live job carries older wording")
        if verbose:
            for ln in difflib.unified_diff(
                    was.splitlines(), fresh.splitlines(),
                    fromfile=f"armed with ({rel})", tofile="in the instance",
                    lineterm="", n=1):
                print("    " + ln)
    if worst:
        print("\nRe-arm the window that owns it: `/fleet start` for the listener,\n"
              "`/fleet watch` for the watchdog. Editing the file is not enough.")
    return worst


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--stamp", metavar="REL", help="record the block this window just armed")
    g.add_argument("--clear", metavar="REL", help="drop the record; belongs with disarming")
    g.add_argument("--check", action="store_true", help="every armed prompt, against the instance")
    ap.add_argument("--diff", action="store_true", help="with --check, show what differs")
    a = ap.parse_args()

    if a.stamp or a.clear:
        rel = a.stamp or a.clear
        if rel not in ARMED_PROMPTS:
            print(f"{rel} is not an armed prompt. Expected one of:\n  "
                  + "\n  ".join(ARMED_PROMPTS), file=sys.stderr)
            return 2
        return stamp(rel) if a.stamp else clear(rel)
    return check(a.diff)


if __name__ == "__main__":
    sys.exit(main())
