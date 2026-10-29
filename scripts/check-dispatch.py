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
strictly stronger than the dirty test and it is what this checks.

**No flag accepts an existing worktree, and none is needed** (2026-10-29,
`tasks/doc/040`). There was one, `--allow-existing`, which fell back to sampling
the tree for activity; the auto-mode classifier refused it before the script
ran, so the recovery this refusal recommended could not be taken. It had no case
to serve either. `ops.md` §3 recovery deletes a clean tree with no commits and
keeps any other for a `blocked` task -- neither is dispatched into -- and a leg
that resumes a dead worker's tree commits it to its branch, removes the tree,
and dispatches onto that branch fresh, at which point this check passes as
written and `--created` checks the result. A tree is never handed to a second
worker; that is the property leg 012 lost.

**This is a backstop, not the root cause.** The root cause is that a supervisor
may conclude a worker died from repo state at all; `tasks/README.md` settles
claim staleness by the **process tree**, and that is the rule that should govern
re-dispatch -- `ListAgents`, not `git status`. No script can check that from
outside the session, so it stays prose. This catches the consequence.

**`--created` is the other half: a post-condition, run after `worktree add`.**
The check above is a pre-condition and proves only that the paths were free. On
2026-09-12 (leg 095, `tasks/doc/046`) and again on 09-14 (leg 114, `059`) it
passed on twelve intended paths while `git -C <repo> worktree add <relative>`
created the worktrees somewhere else -- `git -C` resolves a relative target
against the repo it moved into, so they landed *inside* their repos, exit 0.
The first thing to notice was a worker. `--created` re-reads the same paths and
proves each one is what the dispatch asked for: it exists and is a worktree's
root, it sits at `<worktree_root>/<repo>/<slug>` in fleet.toml's layout, it is
registered to that repo, every worktree of the unit is on the one branch
`agent/<scope>/<slug>`, and every relative Cargo path-dep reachable from it
resolves -- lexically, the way cargo resolves one, which is what made the
sibling-link table's misses (`tasks/doc/037`, `090`) fail a worker's first
build instead of the dispatch. A missing link is printed as the `ln` that fixes
it. Skipping `--created` leaves a leg exactly where it was before it existed.

**Both modes refuse a relative path.** A relative `--worktree` is resolved
against wherever the checker runs, which is how a check can pass on paths that
were never going to be created.

Usage:
  scripts/check-dispatch.py --worktree PATH [--worktree PATH ...]       # before
  scripts/check-dispatch.py --created --worktree PATH [--worktree PATH ...]  # after
Exit status: 0 safe to dispatch, 1 refused, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

# A relative path-dep: what `grep -rn 'path *= *"\.\.' --include=Cargo.toml`
# finds, the hand check leg.md's link table used to send a leg to. Only `..`
# targets, so a `[lib] path = "src/lib.rs"` is never mistaken for a dependency.
PATH_DEP = re.compile(r'\bpath\s*=\s*"(\.\.[^"]*)"')


def git(path: Path, *args: str) -> str | None:
    r = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def unresolved_deps(wt: Path) -> list[tuple[str, str, str]]:
    """(manifest, dep as written, where it resolved) for every relative Cargo
    path-dep reachable from `wt` that has no Cargo.toml.

    Resolved LEXICALLY (`normpath`, never `resolve`): cargo joins a dep's
    `../../../embarch-topology` onto the path it reached that crate by, symlink
    and all, which is why `embarch-ui`'s link to `embarch-api` needs a second
    link to `embarch-topology` beside it. A dep outside the worktree is followed,
    so the whole closure is checked, not the manifests this repo happens to own.
    """
    listed = git(wt, "ls-files", "--", "*Cargo.toml") or ""
    todo = [os.path.join(wt, m) for m in listed.splitlines()
            if os.path.basename(m) == "Cargo.toml"]
    seen, reported, missing = set(), set(), []
    while todo:
        manifest = os.path.normpath(todo.pop())
        if manifest in seen:
            continue
        seen.add(manifest)
        try:
            text = Path(manifest).read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            for rel in PATH_DEP.findall(line):
                dep = os.path.normpath(os.path.join(os.path.dirname(manifest), rel))
                if os.path.isfile(os.path.join(dep, "Cargo.toml")):
                    if not dep.startswith(str(wt) + os.sep):
                        todo.append(os.path.join(dep, "Cargo.toml"))
                elif dep not in reported:
                    reported.add(dep)
                    missing.append((os.path.relpath(manifest, wt.parent), rel, dep))
    return missing


def created(paths: list[Path]) -> int:
    """The post-condition: see the module docstring's `--created` paragraph."""
    bad: list[tuple[Path, str]] = []
    branches: dict[Path, str] = {}
    for p in paths:
        if p.parent.parent != CONF.worktree_root:
            bad.append((p, f"not at {CONF.worktree_root}/<repo>/<slug>, outside every "
                           "repo tree, where protocol.md §5 puts a worker worktree"))
            continue
        repo = CONF.root / p.parent.name
        if not p.is_dir():
            why = "does not exist -- the dispatch never created it here"
            for line in (git(repo, "worktree", "list", "--porcelain") or "").splitlines():
                where = line.removeprefix("worktree ")
                if line.startswith("worktree ") and Path(where).name == p.name:
                    why += (f"; a worktree named {p.name} IS registered at {where}. "
                            "A relative `worktree add` target under `git -C` resolves "
                            "against the repo, not where you stand")
            bad.append((p, why))
            continue
        top = git(p, "rev-parse", "--show-toplevel")
        if top is None or Path(top).resolve() != p.resolve():
            bad.append((p, "exists but is not a worktree's root "
                           f"({'not in git at all' if top is None else 'git sees ' + top})"))
            continue
        common = git(p, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if common is None or Path(common).resolve() != (repo / ".git").resolve():
            bad.append((p, f"is a worktree of {common}, not of {repo}"))
            continue
        branch = git(p, "symbolic-ref", "-q", "--short", "HEAD")
        if not branch or not (branch.startswith("agent/") and branch.endswith("/" + p.name)):
            bad.append((p, f"is on {branch or 'a detached HEAD'}, not agent/<scope>/{p.name}"))
            continue
        branches[p] = branch
        for manifest, rel, dep in unresolved_deps(p):
            sibling = Path(os.path.relpath(dep, p.parent)).parts[0]
            fix = (f"ln -sfn {CONF.root / sibling} {p.parent / sibling}"
                   if sibling != os.pardir and (CONF.root / sibling).is_dir() else "no sibling of that name")
            bad.append((p, f"{manifest}: path-dep {rel} resolves to {dep}, which has no "
                           f"Cargo.toml -- {fix}"))
    if len(set(branches.values())) > 1:
        bad.append((Path("(unit)"), "its worktrees are on different branches: " +
                    ", ".join(sorted(set(branches.values()))) +
                    " -- protocol.md §5 gives one unit one branch name in both repos"))
    if bad:
        print(f"{len(bad)} problem(s) with this unit's worktrees -- do not dispatch:\n",
              file=sys.stderr)
        for p, why in bad:
            print(f"  {p}\n    {why}", file=sys.stderr)
        return 1
    print(f"OK: {len(paths)} worktree(s) created where asked, registered to their repos, "
          f"on {next(iter(branches.values()))}, every Cargo path-dep resolving.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", action="append", default=[], metavar="PATH",
                    help="a worktree this dispatch is about to create (repeatable)")
    ap.add_argument("--created", action="store_true",
                    help="after `worktree add`: prove each path was created where asked, "
                         "on the unit's branch, with every Cargo path-dep resolving")
    args = ap.parse_args()
    if not args.worktree:
        print("--worktree is required (repeatable)", file=sys.stderr)
        return 2
    relative = [p for p in args.worktree if not os.path.isabs(p)]
    if relative:
        print("--worktree takes absolute paths only; relative: " + ", ".join(relative) +
              f"\nWrite {CONF.worktree_root}/<repo>/<NNN-slug>, the path the worktree add "
              "used.", file=sys.stderr)
        return 2
    if args.created:
        return created([Path(os.path.normpath(p)) for p in args.worktree])

    existing = [p for p in args.worktree if Path(p).exists()]
    if existing:
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
              "the whole reading half of a worker's run. Then recover per ops.md §3: commit\n"
              "whatever the tree holds to its branch, push it, and `git worktree remove` the\n"
              "tree. Re-run this check unchanged; it passes once the paths are gone. To\n"
              "resume that work, dispatch onto the existing branch -- `worktree add <path>\n"
              "<branch>`, no `-b` -- and run --created. A tree is never handed to a second\n"
              "worker.\n\n"
              "If you created these yourself a moment ago, before running this: they are\n"
              "clean with no commits, so remove them, run this, and create them again.",
              file=sys.stderr)
        return 1

    print(f"OK: none of the {len(args.worktree)} worktree(s) exist; safe to dispatch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
