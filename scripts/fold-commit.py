#!/usr/bin/env python3
"""Commit one unit's fold across both repos, or commit neither.

protocol.md §11 says the log entry goes IN the fold commit, so that "landed but
unlogged" is impossible rather than merely detectable. `api/003` landed in
exactly that window on 2026-09-03: the fold did every other part correctly and
never touched the log, nothing failed, and that unit's handoff is gone.

Moving the log into the embarch-fleet repo reopens that window, because one
commit becomes two in two repos. This script closes it again. It stages both
sides, refuses unless both are coherent, and commits the instance repo only
after the log commit exists -- so the orderings a kill can leave behind are:

  nothing            no unit landed, nothing to recover
  log only           an entry describing a fold that did not happen -- loud, and
                     `--check` names it, because the entry's SHAs resolve to
                     nothing in the doc repo
  both               the intended state

The one ordering that must never occur is "fold without entry", which is the
one this exists to prevent, and it cannot: the doc-repo commit is last.

It also does what `git add -A` was doing, and refuses what `git add -A` was
sweeping. risks.md: the supervisor folds in the main checkout while the owner
may be dropping a file into `inbox/`, and legs 004 and 005 both swept his
`changelog.d` fragments into their folds. Staging is by explicit path here, and
a path outside the unit's own set is an error rather than a silent inclusion.

Usage:
  scripts/fold-commit.py --unit api/007 --message "Fold api/007: ..." \\
      --path embarch-api/spec.md --path changelog.d/api-foo.added.md
  scripts/fold-commit.py --check          verify the two repos agree
  scripts/fold-commit.py ... --dry-run    print what would be staged
Exit status: 0 committed / coherent, 1 refused, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

FLEET_REPO = Path(__file__).resolve().parent.parent
LOG = FLEET_REPO / "supervisor-log.md"

# What a unit's fold is allowed to touch in the instance repo. Anything else is
# the owner's concurrent edit or another unit's work, and sweeping it is the
# defect this replaces.
ALLOWED = (
    "embarch-",       # the worker's own sub-project docs
    "changelog.d/",   # its history fragment, and any it folded
    "status.d/",      # fragments it consumed (as deletions)
    "tasks/",         # its task file, closed
    "history/",       # build_changelog.py output
    "suite/",         # a suite-level doc a status.d fragment targeted
    "embarch.md",
    "embarch-decision-reversals.md",
    "embarch-glossary.md",
)

UNIT_RE = re.compile(r"^[a-z-]+/\d{3}$")


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"git {' '.join(args)} failed in {repo}:\n{r.stderr.strip()}",
              file=sys.stderr)
        sys.exit(1)
    return r.stdout


def head(repo: Path) -> str:
    return git(repo, "rev-parse", "--short", "HEAD").strip()


def common_git_dir(repo: Path) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--path-format=absolute",
                        "--git-common-dir"], capture_output=True, text=True)
    return r.stdout.strip() or None if r.returncode == 0 else None


DONE_TASK = re.compile(r"^\*\*State:\*\*\s*done\b", re.M)


def finished_task(doc: Path, rel: str) -> bool:
    """A task file this fold is supposed to retire: under tasks/, and `done`."""
    if not rel.startswith("tasks/") or rel.endswith("README.md"):
        return False
    f = doc / rel
    try:
        return bool(DONE_TASK.search(f.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return False


def stage_plan(doc: Path, paths: list[str]) -> tuple[list[str], list[str], list[str], list[str]]:
    """(addable, to_delete, already_staged, missing) for exactly these paths.

    Three cases that are not errors and used to look like one:

    - **A finished task file.** tasks/README.md says the supervisor deletes it
      in the fold, so it is always in a fold's path list. If the worker's branch
      merged it in its `done` state it has no pending change at all, `git add`
      stages nothing, and leg 008's first fold reported "2 path(s)" for three --
      the task file silently surviving the fold that was meant to retire it.
      This fold does the `git rm` itself rather than trusting the caller to.
    - **One already `git rm`'d.** Nothing in the worktree or index to match,
      deletion already staged, nothing to do.
    - **A path matching nothing and not staged.** That one is a real mistake.
    """
    staged = {p for p in git(doc, "diff", "--cached", "--name-only").split("\n") if p}
    addable, to_delete, already, missing = [], [], [], []
    for p in paths:
        if finished_task(doc, p):
            to_delete.append(p)
            continue
        r = subprocess.run(["git", "-C", str(doc), "add", "-A", "--dry-run", "--", p],
                           capture_output=True, text=True)
        (addable if r.returncode == 0 else already if p in staged else missing).append(p)
    return addable, to_delete, already, missing


def invoking_repo() -> Path | None:
    """The instance checkout the caller is standing in, worktree or not.

    protocol.md §6 step 0 puts a leg in its own worktree, but this script
    defaulted to fleet.toml's `doc_repo` -- so the invocation documented in
    supervise.md staged the OWNER'S checkout, which is the exact thing step 0
    moved the leg out of. A worktree shares its parent's common git dir, so
    that is what identifies the instance repo wherever it is checked out.
    Anything else (a code repo, an unrelated tree) falls back to the config.
    """
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    top = Path(r.stdout.strip()).resolve()
    canonical = common_git_dir(CONF.doc_repo)
    return top if canonical and common_git_dir(top) == canonical else None


def newest_unit_entry() -> tuple[str, str] | None:
    """The newest per-unit entry, as (unit, body).

    Not every entry is a unit: a leg that ran none still writes one, and a
    folded day collapses several. Those are skipped rather than treated as the
    unit -- taking the heading from one entry and the SHAs from the next is a
    check that reports on a pairing that does not exist.
    """
    sections = re.split(r"^## ", LOG.read_text(), flags=re.M)[1:]
    for sec in sections:
        m = re.match(r"\d{4}-\d{2}-\d{2}[^—\n]*— ([a-z-]+/\d{3})", sec)
        if m:
            return m.group(1), sec
    return None


def check() -> int:
    """Do the two repos agree about the last unit?

    A log entry whose merge SHAs do not resolve in the doc repo describes a fold
    that did not happen -- the "log only" ordering a kill can leave.
    """
    doc = CONF.doc_repo
    found = newest_unit_entry()
    if found is None:
        print("no per-unit entry in the log (a folded day, or empty).")
        return 0
    unit, body = found

    # §11's Merged line labels each SHA with the repo it lives in:
    #   `agent/api/006-...` (api `1a396ba`, doc `9c3f1de`)
    # so a SHA is resolved against the repo its label names, never all of them
    # against the doc repo. Getting that wrong would make every entry fail.
    pairs = re.findall(r"\(?([a-z][a-z-]*)\s+`([0-9a-f]{7,40})`", body)
    if not pairs:
        print(f"newest unit entry ({unit}) names no merge SHA. protocol.md §11\n"
              "requires both -- there is no merge commit and no surviving branch\n"
              "name, so the SHA is the only handle a revert has.")
        return 1

    missing = []
    for label, sha in pairs:
        repo = doc if label == "doc" else CONF.root / f"embarch-{label}"
        if not (repo / ".git").exists():
            missing.append((label, sha, f"no repo at {repo}"))
            continue
        if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True).returncode != 0:
            missing.append((label, sha, f"not in {repo.name}"))

    if missing:
        print(f"log's newest entry ({unit}) names {len(missing)} SHA(s) that do not\n"
              "resolve:\n")
        for label, sha, why in missing:
            print(f"  {label} {sha}  -- {why}")
        print("\nThis is the 'log only' ordering: an entry was pushed for a fold that\n"
              "did not land. Either the fold is missing and the unit must be redone,\n"
              "or that repo needs a pull. Do not write a second entry.")
        return 1
    print(f"OK: newest entry ({unit}) and its {len(pairs)} SHA(s) resolve "
          f"({', '.join(l for l, _ in pairs)}).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unit", help="scope/NNN, e.g. api/007")
    ap.add_argument("--message", "-m", help="commit subject for the doc repo")
    ap.add_argument("--path", action="append", default=[],
                    help="a path in the doc repo this fold may stage (repeatable)")
    ap.add_argument("--doc-repo",
                    help="the instance checkout to stage in -- pass a leg's own "
                         "worktree; defaults to fleet.toml's doc_repo")
    ap.add_argument("--check", action="store_true", help="verify the two repos agree")
    ap.add_argument("--dry-run", action="store_true", help="print, commit nothing")
    args = ap.parse_args()

    if args.check:
        return check()
    if not (args.unit and args.message and args.path):
        print("--unit, --message and at least one --path are required "
              "(or use --check)", file=sys.stderr)
        return 2
    if not UNIT_RE.match(args.unit):
        print(f"--unit must look like 'api/007', got {args.unit!r}", file=sys.stderr)
        return 2

    doc = (Path(args.doc_repo).resolve() if args.doc_repo
           else invoking_repo() or CONF.doc_repo)
    if not (doc / '.git').exists():
        print(f'not a git checkout: {doc}', file=sys.stderr)
        return 2

    bad = [p for p in args.path if not p.startswith(ALLOWED)]
    if bad:
        print(f"{len(bad)} path(s) outside what a unit's fold may stage:\n")
        for p in bad:
            print(f"  {p}")
        print("\nA fold stages its own unit and nothing else. If one of these genuinely\n"
              "belongs, it is the owner's commit or a separate one -- not this fold.\n"
              "This is the rule that replaces `git add -A`, which swept the owner's\n"
              "own fragments into legs 004 and 005.")
        return 1

    # The log entry must already be written, and must name this unit. Checking
    # before anything is staged means a missing entry costs nothing to recover
    # from -- the failure §11 describes is a fold that already happened.
    found = newest_unit_entry()
    entry_unit = found[0] if found else None
    if entry_unit != args.unit:
        print(f"the log's newest entry is for {entry_unit!r}, not {args.unit!r}.\n\n"
              "Write this unit's entry to supervisor-log.md FIRST, then fold. The\n"
              "entry is part of the fold, not a step after it: writing it afterwards\n"
              "is the window api/003 landed in on 2026-09-03.", file=sys.stderr)
        return 1

    if not git(FLEET_REPO, "status", "--porcelain", "--", "supervisor-log.md").strip():
        print("supervisor-log.md has no uncommitted change, so this unit's entry is\n"
              "either already committed or was never written. Check before retrying.",
              file=sys.stderr)
        return 1

    # Stage-ability is settled BEFORE the log is committed. `git add` refuses a
    # path that is in neither the worktree nor the index, and a `git rm`'d task
    # file is exactly that -- already staged as a deletion, with nothing left to
    # match. tasks/README.md guarantees every fold has one, so this aborted on
    # every unit of leg 007, twice after the log commit had already landed and
    # twice recovered by hand. The ordering was safe by design and manual every
    # time; now the case is simply understood.
    addable, to_delete, already, missing = stage_plan(doc, args.path)
    if missing:
        print(f"{len(missing)} path(s) cannot be staged in {doc.name}, and they are\n"
              "not already staged either -- so the log has NOT been committed:\n")
        for m in missing:
            print(f"  {m}")
        print("\nFix the path list and retry. Nothing has been written.",
              file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"would commit to {FLEET_REPO.name}: supervisor-log.md")
        print(f"  staging in: {doc}")
        print(f"would commit to {doc.name}:")
        for p in addable:
            print(f"  {p}")
        for p in to_delete:
            print(f"  {p}  (finished task, this fold deletes it)")
        for p in already:
            print(f"  {p}  (already staged as a deletion)")
        return 0

    # Log first. If the machine dies between the two, the surviving state is an
    # entry for a fold that did not happen -- recoverable and loud -- rather
    # than a fold nobody logged, which is unrecoverable.
    git(FLEET_REPO, "add", "--", "supervisor-log.md")
    git(FLEET_REPO, "commit", "-m", f"Log {args.unit}: {args.message}")
    log_sha = head(FLEET_REPO)

    # -A with an EXPLICIT pathspec, never bare: it stages a deletion as well as
    # an add or a modification, for exactly the listed paths and nothing else.
    # Bare `git add -A` is what swept the owner's own fragments into legs 004
    # and 005, and the path allowlist above is what replaces it.
    if addable:
        git(doc, "add", "-A", "--", *addable)
    if to_delete:
        # tasks/README.md: a landed task leaves the queue in the same commit
        # that folds its fragments. Git holds it, and a completed task left in
        # the queue competes with the open ones for attention.
        git(doc, "rm", "-q", "--", *to_delete)
    staged = git(doc, "diff", "--cached", "--name-only").strip()
    # A path that produced no change at all is worth a line. The count on its
    # own is not enough: leg 008 read "2 path(s)" for a three-path fold and had
    # to notice the discrepancy by eye.
    quiet = [p for p in args.path if p not in set(staged.split("\n"))]
    for p in quiet:
        print(f"note: {p} staged nothing -- it was already committed unchanged")
    if not staged:
        print(f"nothing staged in {doc.name}; the log commit {log_sha} stands alone.\n"
              "Investigate before retrying -- do not write a second entry.",
              file=sys.stderr)
        return 1
    git(doc, "commit", "-m", f"{args.message}\n\nLog: embarch-fleet@{log_sha}")

    print(f"{FLEET_REPO.name}  {log_sha}  supervisor-log.md")
    print(f"{doc.name}  {head(doc)}  {len(staged.splitlines())} path(s)"
          f"{f', {len(to_delete)} task file(s) retired' if to_delete else ''}")
    print("\nPush both. A fold is not landed until the log is pushed too.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
