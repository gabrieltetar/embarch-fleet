#!/usr/bin/env python3
"""Check that every slash command this repo tells someone to type exists.

Found 2026-09-07, by the owner reading a line this script now checks:
**eleven places said `/fleet watch` and the command is `/fleet-watch`.**

That is not a typo with cosmetic consequences. `/fleet` and `/fleet-watch` are
two different commands with two different `argument-hint`s, and `/fleet`'s
default argument is `start` -- so typing `/fleet watch` does not fail, it arms
a **listener**, the window that spawns supervisor legs, where the reader was
being told to arm the **watchdog**, which is specified as a window with no
hands. A wrong instruction that silently arms the wrong kind of window is worth
a gate.

Where it was: `deploy.py`'s own re-arm instructions, `fleet-armed.py`'s,
`fleet-post.py`'s, three places in `fleet-deadman.py`, the deployer agent's
alert text, and four of the eight docs. Every one of them was written by
copying a neighbour, which is how a wrong string reaches eleven places and no
right one.

**What it checks**, and deliberately only this:

  1. Every `/<command>` named in this repo's prose or scripts is a real file
     under `templates/.claude/commands/`.
  2. The token after it, **when both sit inside one inline-code span**, is one
     of that command's own `argument-hint` alternatives. That is the rule that
     catches the bug. The span scoping is what keeps it quiet: prose after a
     closed span is prose, so "`/fleet-watch` in a new window" reads `in` as
     English rather than as an argument.

It does NOT try to discover unknown commands from arbitrary `/x` tokens: this
corpus is full of absolute paths, and `/home`, `/mnt`, `/study` and `/status`
are not commands. Scanning for the commands that exist, rather than for
anything command-shaped, is the difference between a check and a noise source.

`supervisor-log.md` and `log-archive/` are exempt: they are a record of what
past legs said, and correcting a quotation in a log would make the log wrong.

Usage:
  scripts/check-fleet-commands.py            check (deploy.py runs this)
  scripts/check-fleet-commands.py --list     the commands and their arguments
Exit status: 0 clean, 1 a wrong invocation exists.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMANDS_DIR = REPO / "templates" / ".claude" / "commands"
# `supervisor-log.md` and `log-archive/`: a record of what past legs said, and
# correcting a quotation inside a log would make the log wrong.
# `templates/.claude/commands/`: a command file naming its own siblings.
# **This script itself**, because it has to quote the wrong string in order to
# explain what it detects -- the same trap `supervisor-log.md`'s header
# records, where an entry-shape template with real-looking SHAs was read as
# work that had run. Documentation shaped exactly like the data it documents.
EXEMPT = re.compile(r"^(supervisor-log\.md$|log-archive/|templates/\.claude/commands/"
                    r"|scripts/check-fleet-commands\.py$)")

# An argument only counts inside the same inline-code span as the command.
# Without this, "`/fleet-watch` in a new window" reads `in` as an argument --
# a real false positive from `fleet-post.py`. Prose after a closed span is
# prose; a span holding both tokens is an invocation someone will type.
CODE_SPAN = re.compile(r"`([^`]*)`")
HINT = re.compile(r"^argument-hint:\s*\"?\[?([^\"\]\n]*)", re.M)


def commands() -> dict[str, set[str]]:
    """name -> the arguments its own `argument-hint` allows."""
    out = {}
    for p in sorted(COMMANDS_DIR.glob("*.md")):
        m = HINT.search(p.read_text(encoding="utf-8", errors="replace"))
        args = set()
        if m:
            args = {a.strip() for a in m.group(1).split("|") if a.strip()}
        out[p.stem] = args
    return out


def scanned():
    for p in sorted(REPO.rglob("*")):
        if p.is_dir() or p.suffix not in (".md", ".py"):
            continue
        rel = str(p.relative_to(REPO))
        if EXEMPT.search(rel) or ".git" in p.parts:
            continue
        yield rel, p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    cmds = commands()
    if not cmds:
        print(f"no commands found under {COMMANDS_DIR.relative_to(REPO)}")
        return 1
    if args.list:
        for name, allowed in cmds.items():
            print(f"  /{name}  [{' | '.join(sorted(allowed)) or 'no arguments'}]")
        return 0

    # Longest name first, so `/fleet-watch` is matched before `/fleet` and a
    # correct invocation is never reported as a wrong argument to a shorter one.
    names = sorted(cmds, key=len, reverse=True)
    pattern = re.compile(r"/(" + "|".join(re.escape(n) for n in names) + r")\b[ \t]*([A-Za-z][\w-]*)?")
    bad = []
    for rel, text in scanned():
        for i, line in enumerate(text.splitlines(), start=1):
            # Each span on its own. Joining them made `/supervise` and a
            # neighbouring `fleet go` read as `/supervise fleet` -- two things
            # a reader would never type together.
            for hay in (sp.group(1) for sp in CODE_SPAN.finditer(line)):
                for m in pattern.finditer(hay):
                    name, arg = m.group(1), m.group(2)
                    if arg is None or not cmds[name]:
                        continue
                    if arg in cmds[name]:
                        continue
                    # Is this another command's name split by a space? That is
                    # the bug this exists for, so say it that way.
                    merged = f"{name}-{arg}"
                    hint = (f"did you mean /{merged}?" if merged in cmds
                            else f"allowed: {' | '.join(sorted(cmds[name]))}")
                    bad.append((rel, i, f"/{name} {arg}", hint))

    if not bad:
        print(f"OK: every slash invocation names one of {len(cmds)} real command(s) "
              f"with a legal argument.")
        return 0

    print(f"{len(bad)} wrong slash invocation(s):\n")
    for rel, line, found, hint in bad:
        print(f"  {rel}:{line}  `{found}`  -- {hint}")
    print("\nA command with a default argument does not fail on a wrong one, it does\n"
          "something else -- `/fleet watch` arms a listener, which spawns work, where\n"
          "`/fleet-watch` arms a watchdog that has no hands. Fix the string.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
