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
                     `--check` names it, because the entry's merge SHAs resolve
                     in none of the suite's repos; re-running the same command
                     finds that log commit and lands the instance half
  both               the intended state

The one ordering that must never occur is "fold without entry", which is the
one this exists to prevent, and it cannot: the doc-repo commit is last.

Everything that can refuse runs before the log commit, staging included, so
"log only" is a kill between two commits and nothing else (tasks/doc/075).

It also refuses a fold whose framework repo carries a denylisted client name
(2026-09-06). That repo is the one nothing else scans -- the instance's gate
covers the instance, the merge gate covers the code repos, and a leg never
checks the framework out -- so a name quoted into a log entry had reached `main`
with every gate green. Refused before the log commit, where it is still cheap.

It also refuses an entry that does not match `## Entry shape`. The shape is not
decoration: `fold-day.py` finds a day's SHAs, hardware debts and reviewer lines
by those literal `**Field:**` markers, so an entry that bolds a whole phrase
instead loses that field from the daily fold silently. Four of 2026-09-05's ten
entries did exactly that -- three dropping `**Hardware debts:**`, one writing a
fourth `**Reviewer:**` form -- and nothing failed.

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
import datetime
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
    "features.d/",    # its row in the assembled feature inventory
    "tasks/",         # its task file, closed
    "history/",       # build_changelog.py output
    "suite/",         # a suite-level doc a status.d fragment targeted
    "embarch.md",
    "embarch-decision-reversals.md",
    "reversals/",     # its DOC-COMPACTION split: the range files hold the rows
    "embarch-glossary.md",
)
# A split doc keeps its old file's rules and none of its old file's place in
# this list (tasks/doc/073): `reversals/` was refused for a day while the
# four-row index it was split from was accepted. A new split directory of a
# doc above belongs here in the same edit that creates it.

UNIT_RE = re.compile(r"^[a-z-]+/\d{3}$")

# supervisor-log.md's `## Entry shape`, as data. Every one of these is written
# literally, as `**Field:**` at the start of a line, and the shape says so of
# each -- "if it decided nothing, say nothing"; "exactly one of the three,
# always"; "not optional". None of that was enforced anywhere, and the entries
# drifted exactly as an unenforced shape does: on 2026-09-05 three of ten lost a
# field by bolding a whole phrase instead of the marker, `umbrella/010` writing
# `**Hardware debts: one, and it is free.**`. That is not cosmetic -- fold-day.py
# extracts debts, reviewer lines and SHAs by these markers, so a bent one is a
# hardware debt the daily fold cannot see and a reviewer line
# `grep '^\*\*Reviewer:'` never counts. `umbrella/004` had already needed a
# correcting commit for the same class.
REQUIRED_FIELDS = ("Decided:", "Merged:", "Blocked:", "Reviewer:",
                   "Hardware debts:", "Budget:", "Least sure about:")
# The three forms, and nothing else. A fourth form breaks the tally that is the
# only thing able to settle open.md's reviewer question, and `pending` is the
# tempting fourth: it reads as honest and is never resolved by anybody.
REVIEWER_FORM = re.compile(
    r"^\*\*Reviewer:\*\*\s+(no findings\b|\d+ findings?\b|skipped\s*\()", re.M)


def entry_shape_problems(body: str) -> list[str]:
    """What the newest entry drops or bends. Empty means it matches the shape."""
    out = []
    missing = [f for f in REQUIRED_FIELDS
               if not re.search(rf"^\*\*{re.escape(f)}\*\*", body, re.M)]
    if missing:
        out.append("missing, or not written as a literal `**Field:**` at the start of "
                   "a line:\n" + "\n".join(f"      **{f}**" for f in missing))
    if not any(f.startswith("Reviewer") for f in missing) and \
            not REVIEWER_FORM.search(body):
        out.append("the `**Reviewer:**` line is not one of the three forms "
                   "(`no findings` /\n      `N finding — <inbox file>` / "
                   "`skipped (<why>)`). `pending` is not a form:\n"
                   "      collect the reviewer before writing the entry, and if it never\n"
                   "      reported say `skipped (reviewer did not report -- <what "
                   "happened>)`.")
    return out


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


STATE_LINE = re.compile(r"^\*\*State:\*\*\s*(.+?)\s*$", re.M)


def unit_task_not_settled(doc: Path, unit: str) -> str | None:
    """Refuse a fold whose OWN task file still says `open` or `claimed`.

    This is `tasks/doc/028`'s failure (1), and it is the one with teeth: a task
    left `claimed` after its leg dies is indistinguishable from a live claim, so
    `ops.md` §3's recovery reclaims it to `open` and the next leg re-dispatches a
    unit that already landed, into a repo whose `main` already has the change.
    Six instances in two legs, every one repaired by hand at a fold or found by
    the next leg; nothing ever checked it.

    **The fold is the only place this is checkable**, which is why it lives here
    and not in the gate. A `claimed` task is perfectly legal in general — it
    means a worker is running — so no repo-wide checker can call it wrong. What
    makes it wrong is *this* fold asserting that *this* unit landed, and at that
    moment the truth is known and one comparison settles it.

    Only the unit's own task is inspected. A fold legitimately touches other
    task files: filing new ones, and reopening a task whose debt turned out to
    stand, which leg 060 did to `tasks/core/022` on 2026-09-09.

    `blocked` and `done` both pass. `blocked` is a real ending — the unit
    reports what stopped it and the queue keeps the task — and the log entry
    carries a `**Blocked:**` line saying so.
    """
    scope, num = unit.split("/", 1)
    matches = sorted((doc / "tasks" / scope).glob(f"{num}-*.md"))
    if not matches:
        # No file: the task was already retired, or this is a recovery fold
        # reconstructing a unit whose file went with an earlier one. Silence is
        # right -- the other refusals cover a fold with nothing behind it, and
        # inventing a failure here would block the recoveries this repo does.
        return None
    f = matches[0]
    m = STATE_LINE.search(f.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return (f"{f.relative_to(doc)} has no `**State:**` line, so nothing can "
                f"say whether this unit finished.\nNothing has been written.")
    tok = (m.group(1).split() or [""])[0].strip("*_`")
    if tok in ("done", "blocked"):
        return None
    return (f"this fold says {unit} landed, but {f.relative_to(doc)} still says "
            f"`{tok}`.\n\n"
            f"  **State:** {m.group(1)[:100]}\n\n"
            "A task left `claimed` reads as a live claim to the next leg's recovery,\n"
            "which reclaims it to `open` and re-dispatches work that already landed\n"
            "(tasks/doc/028, six instances). Set the state to `done` — or `blocked`\n"
            "with a `## Blocked` section — and re-run. Nothing has been written.")


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
    leg.md staged the OWNER'S checkout, which is the exact thing step 0
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



def stamp_entry_time(unit: str, now: datetime.datetime, apply: bool) -> str | None:
    """Set the newest entry's heading to the wall clock. Returns a note, or None.

    Nothing used to write this field and nothing checked it, so it was a guess.
    Measured 2026-09-06 over 63 entries: 41 were more than five minutes ahead of
    the fold that wrote them, the worst by 63. The error accumulates
    monotonically within a leg and resets at the next one -- the signature of
    reading a clock once and estimating from there.

    It is not cosmetic. `fold-day.py` groups a day by THIS date, so an entry
    written at 23:50 and stamped 00:15 folds into the wrong day and nothing
    says so; and protocol.md §11 makes this log the only review surface under a
    full delegate, where a heading an hour out is one that correlates with
    nothing -- not Slack, not the tick file, not `git log`.

    Matched against `unit` rather than "the first timed heading", because a leg
    entry (`## <date> <time> -- leg 019: ...`) can sit above the newest unit
    entry and stamping that one would move a heading this fold does not own.
    The time is optional in the pattern so a heading that carries none is
    repaired rather than skipped.
    """
    text = LOG.read_text()
    m = re.search(r"^## (\d{4}-\d{2}-\d{2})(?: (\d{2}:\d{2}))? — "
                  + re.escape(unit) + r"\b", text, re.M)
    if not m:
        return None
    stamp = now.strftime("%Y-%m-%d %H:%M")
    if m.group(2):
        was = f"{m.group(1)} {m.group(2)}"
        drift = (datetime.datetime.strptime(was, "%Y-%m-%d %H:%M")
                 - now.replace(second=0, microsecond=0)).total_seconds() / 60
        note = (f"stamped {unit} {stamp} -- the entry said {was}, "
                f"{abs(drift):.0f} min {'ahead' if drift > 0 else 'behind'}")
        # Under five minutes and on the right day is the clock being read
        # properly; saying so every fold would train the reader to skip it.
        quiet = abs(drift) <= 5
    else:
        was, note, quiet = None, f"stamped {unit} {stamp} -- the entry carried no time", False
    if apply and was != stamp:
        LOG.write_text(text[:m.start()] + f"## {stamp} — {unit}" + text[m.end():])
    return None if quiet else note

# A SHA inside backticks, and nothing else. `defaced` and `effaced` are hex
# words; requiring a digit keeps them out, the same narrowing fold-day.py makes
# for the same reason.
SHA_TICKED = re.compile(r"`(?=[0-9a-f]{7,40}`)([0-9a-f]*[0-9][0-9a-f]*)`")
# A `suite` unit is the supervisor's own hands on `main`: no worker branch, so
# no merge SHA to name. That is an entry shape, not an omission.
NO_BRANCH = re.compile(r"\*\*Merged:\*\*\s*(no branches|none)\b", re.I)


def merged_para(body: str) -> str | None:
    """The `**Merged:**` line and its wrapped continuation, to the blank line.

    Scoped deliberately. The old check swept the WHOLE entry for `word `sha``
    and read the word before each one as a repo name, so the template's own
    `code `<sha>`` phrasing -- used by every entry for eleven legs -- resolved
    to `embarch-code`, a repo that has never existed, and `--check` reported
    every healthy unit as one that "must be redone". A recovering leg is the
    actor least able to disbelieve that. The narrative SHAs an entry quotes
    (a rebase base, a superseded merge) are not what §11 requires carried, and
    reading them cost the `api/005` entry a prose edit to appease this check.
    """
    lines = body.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("**Merged:**"):
            out = [ln]
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    break
                out.append(nxt)
            return "\n".join(out)
    return None


def suite_repos() -> list[Path]:
    """Every git checkout under the fleet root, doc repo first.

    A SHA is resolved by ASKING the repos, never by deriving a repo name from
    the log's prose: §11 fixes that both SHAs are recorded, not what they are
    labelled, and eleven legs have labelled them `code`, `doc`, `api`, `sd`,
    `umbrella` and `core` -- three of which are not directory names.
    """
    doc = CONF.doc_repo
    rest = sorted(d for d in CONF.root.glob("embarch-*")
                  if (d / ".git").exists() and d != doc)
    return ([doc] if (doc / ".git").exists() else []) + rest


def check() -> int:
    """Do the two repos agree about the last unit?

    A log entry whose merge SHAs resolve in no repo of the suite describes a
    fold that did not happen -- the "log only" ordering a kill can leave.
    """
    found = newest_unit_entry()
    if found is None:
        print("no per-unit entry in the log (a folded day, or empty).")
        return 0
    unit, body = found

    para = merged_para(body)
    if para is None:
        print(f"newest unit entry ({unit}) has no `**Merged:**` line at all.\n"
              "protocol.md §11 requires one on every entry.")
        return 1

    shas = sorted(set(SHA_TICKED.findall(para)))
    if not shas:
        if NO_BRANCH.search(para):
            print(f"OK: newest entry ({unit}) names no merge SHA, and says why "
                  "-- a `suite`\nunit lands on `main` by the supervisor's own hands. "
                  "Nothing to resolve.")
            return 0
        print(f"newest unit entry ({unit}) names no merge SHA. protocol.md §11\n"
              "requires both -- there is no merge commit and no surviving branch\n"
              "name, so the SHA is the only handle a revert has.")
        return 1

    repos = suite_repos()
    if not repos:
        print(f"no git checkouts under {CONF.root}; nothing to resolve against.",
              file=sys.stderr)
        return 2

    found_in, missing = {}, []
    for sha in shas:
        for repo in repos:
            if subprocess.run(["git", "-C", str(repo), "cat-file", "-e",
                               f"{sha}^{{commit}}"], capture_output=True).returncode == 0:
                found_in[sha] = repo.name
                break
        else:
            missing.append(sha)

    if missing:
        print(f"log's newest entry ({unit}) names {len(missing)} SHA(s) that resolve "
              f"in\nnone of the suite's {len(repos)} repos:\n")
        for sha in missing:
            print(f"  {sha}")
        print("\nThis is the 'log only' ordering: an entry was pushed for a fold that\n"
              "did not land. Either the fold is missing and the unit must be redone,\n"
              "or a repo needs a pull. Do not write a second entry.")
        return 1
        return 1
    print(f"OK: newest entry ({unit}) and its {len(shas)} SHA(s) resolve "
          f"({', '.join(f'{s} in {r}' for s, r in sorted(found_in.items()))}).")
    return 0


# Paths a fold consumes on `main`: a task file is retired, a fragment is
# assembled and deleted. A branch's copy of one of these can never match
# `origin/main` again, by design, so their absence there is the landing.
CONSUMED = ("tasks/", "changelog.d/", "status.d/")


def blob(repo: Path, rev: str, path: str) -> str:
    return git(repo, "rev-parse", "-q", "--verify", f"{rev}:{path}", check=False).strip()


def landed(repo: Path, ref: str, base: str = "origin/main") -> bool:
    """Is everything `ref` carries already on `base`? False whenever unsure.

    `git cherry` first: a commit whose patch-id is on `base` is proven, and that
    answer has no false positives. It does have false negatives, and they
    stranded branches for good (`tasks/doc/061`, `080`): a cherry-pick or a
    rebase that **conflicted** produces a different patch, and the conflict is
    nearly always on the task file, because `main` moved it (a claim, a fold)
    after the worker branched. `api/096` and `core/052` sat on the remote from
    2026-09-13 for that reason alone.

    So a commit cherry cannot match is proven file by file instead: every path
    it touched must read the same on `base` as at the branch tip -- or, for a
    path a fold consumes (`CONSUMED`), be gone from `base` *because `base`
    deleted it after the branch forked*, which is what a retired task file and
    an assembled fragment look like. A fragment that never landed was never on
    `base` to be deleted, so it still holds the branch. A path edited further
    since it landed also still holds it: unprovable stays, the safe direction.
    """
    if subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", ref, base],
                      capture_output=True).returncode == 0:
        return True           # the cheap proof, and the common one: a fast-forward
    r = subprocess.run(["git", "-C", str(repo), "cherry", base, ref],
                       capture_output=True, text=True)
    if r.returncode:
        return False
    unmatched = [ln.split()[1] for ln in r.stdout.splitlines() if ln.startswith("+")]
    if not unmatched:
        return True
    fork = git(repo, "merge-base", base, ref, check=False).strip()
    if not fork:
        return False
    paths: set[str] = set()
    for c in unmatched:
        if len(git(repo, "rev-list", "--parents", "-n1", c, check=False).split()) != 2:
            return False      # a merge or a root: no single diff to reason about
        paths.update(p for p in git(repo, "diff-tree", "-z", "--no-commit-id",
                                    "--name-only", "-r", c, check=False).split("\0") if p)
    for p in paths:
        there = blob(repo, base, p)
        if there == blob(repo, ref, p):
            continue
        if not there and p.startswith(CONSUMED) and git(
                repo, "log", "-1", "--format=%h", "--diff-filter=D",
                f"{fork}..{base}", "--", p, check=False).strip():
            continue
        return False
    return True


def committed_log(unit: str, doc: Path) -> tuple[str | None, str]:
    """For a clean log: (the log commit to resume from, "") or (None, why not).

    A clean `supervisor-log.md` used to be refused outright -- "either already
    committed or was never written" -- which was accurate and a dead end: the
    "log only" ordering this script documents had no supported way out, so legs
    104, 131 and 139 each finished a fold by hand-writing the instance commit
    (tasks/doc/075, 082). The truth is cheap to establish, so establish it.
    """
    full, short, subject = git(FLEET_REPO, "log", "-1",
                               "--format=%H%x00%h%x00%s").strip().split("\0", 2)
    if not subject.startswith(f"Log {unit}: "):
        return None, (
            f"supervisor-log.md has no uncommitted change, and the fleet repo's newest\n"
            f"commit is not {unit}'s log commit, so there is no half-landed fold of\n"
            f"this unit to resume:\n\n  {short} {subject[:70]}\n\n"
            "Write this unit's entry and re-run. If its log commit is further back,\n"
            "commit the instance half by hand with the same paths and message,\n"
            "ending it `Log: embarch-fleet@<that sha>`. Nothing has been written.")
    folded = git(doc, "log", "-n", "200", "--format=%h", "-F",
                 f"--grep=embarch-fleet@{full[:7]}", "HEAD", check=False).split()
    if folded:
        return None, (f"{unit} is already folded: embarch-fleet@{short} and {doc.name} "
                      f"{folded[0]}.\nNothing to do -- push both if you have not. "
                      "Nothing has been written.")
    return short, ""


UNIT_BRANCH = re.compile(r"^agent/([a-z-]+)/(\d{3})-")


def unfinished_units(doc: Path) -> set[tuple[str, str]]:
    """(scope, NNN) of every task on the instance's `origin/main` not reading `done`.

    A unit whose task is still open, claimed or blocked has not landed, whatever
    its branch holds -- and its branch may be all there is of it. The case that
    needs this is `tasks/doc/040`'s dead-worker route: commit what the worktree
    holds, push, `git worktree remove`, and resume later with `worktree add
    <path> <branch>`. Between the remove and the resume nothing has the branch
    checked out, so `git branch -D` no longer refuses it, and a branch that holds
    nothing yet is an ancestor of `main` -- `landed()` alone would delete the
    branch the resume is about to name. A `done` file not yet retired still
    counts as finished: on 2026-10-29, 88 `done` files sat unretired on `main`.
    """
    out: dict[tuple[str, str], bool] = {}
    for ln in git(doc, "grep", "-e", r"^\*\*State:\*\*", "origin/main", "--",
                  "tasks/", check=False).splitlines():
        parts = ln.split(":", 2)
        m = re.match(r"tasks/([a-z-]+)/(\d{3})-", parts[1]) if len(parts) == 3 else None
        if m and m.groups() not in out:
            out[m.groups()] = not DONE_TASK.match(parts[2])
    return {u for u, live in out.items() if live}


def prune_landed_branches(doc: Path, scope: str, dry: bool) -> None:
    """Delete `agent/*` branches, pushed and local, whose work is on `origin/main`.

    The fleet deleted a worker's worktrees and its local branches and never the
    branch it pushed, so every unit left one behind in each of its two repos.
    Five had accumulated from leg 011 alone -- and on 2026-09-05 they did real
    damage rather than merely being untidy: an `embarch-api` history rewrite
    looked complete from `main` and from a fresh clone's worktree, while
    `origin/agent/api/013-...` still pinned the client name on GitHub.

    **Against `origin/main`, never local `main`, and that is the whole safety
    argument.** This script deliberately does not push (see the header), so at
    fold time the merge exists locally and may not exist on the remote. Deleting
    the remote branch then would leave the remote holding neither the branch nor
    the merge, and a machine that died in that window would have lost the unit.
    Gating on `origin/main` means the remote provably already has the content.

    The cost is that a unit's own branches usually survive until the NEXT fold,
    once the push has happened -- one unit late, self-healing, and it sweeps a
    backlog left by earlier legs for free. That is strictly better than a rule
    telling a tired supervisor to remember, which is what this replaces.

    **Content, not ancestry.** protocol.md §6: a rebased branch's tip is never
    an ancestor of `main` even when its content landed, so ancestry cannot
    prove a rebased branch safe to delete. `landed()` proves it by patch-id and,
    where a conflicted cherry-pick or rebase changed the patch, file by file;
    batch 003 correctly refused a delete on exactly this distinction.

    **The local branch goes in the same breath, on the same proof**
    (`tasks/doc/066`). It was never "deleted with the worktree": `git worktree
    remove` leaves the ref, so the owner's checkout held 112 dead `agent/*`
    branches by leg 119 and 297 by 2026-10-29 -- `git branch` there, a recovery
    tool, had become unreadable. `git branch -D` and not `update-ref -d`,
    because `-D` refuses a branch a live worktree has checked out, which is what
    keeps an in-flight worker's branch safe whatever its content.

    **And never a branch whose unit is unfinished on `origin/main`**, pushed or
    local, whatever `landed()` says -- see `unfinished_units()`. Measured
    2026-10-29, that protects exactly `ui/059`'s, which the proof keeps anyway;
    what it adds is the empty branch parked for a resume.

    Best-effort throughout: the fold is already committed when this runs, and a
    network failure must never turn a landed unit into a failed one.
    """
    repos = [doc]
    code = CONF.root / f"embarch-{scope}"
    # `doc` is usually a leg worktree, so the doc scope's `code` is the same
    # repository under another path -- one pass is enough.
    if (code / ".git").exists() and common_git_dir(code) != common_git_dir(doc):
        repos.append(code)
    unfinished = unfinished_units(doc)

    def keep(branch: str) -> bool:
        m = UNIT_BRANCH.match(branch)
        return bool(m and m.groups() in unfinished)

    for repo in repos:
        if not git(repo, "rev-parse", "--verify", "-q", "origin/main",
                   check=False).strip():
            continue
        refs = git(repo, "for-each-ref", "--format=%(refname:short)",
                   "refs/remotes/origin/agent/", check=False).split()
        for ref in refs:
            branch = ref[len("origin/"):]
            if keep(branch) or not landed(repo, ref):
                continue          # not provably on origin/main yet -- leave it
            if dry:
                print(f"would delete {repo.name}: origin/{branch}")
                continue
            r = subprocess.run(["git", "-C", str(repo), "push", "origin",
                                "--delete", branch], capture_output=True, text=True)
            if r.returncode == 0:
                git(repo, "update-ref", "-d", f"refs/remotes/origin/{branch}",
                    check=False)
                print(f"pruned {repo.name}: origin/{branch} (landed on origin/main)")
            else:
                print(f"note: could not prune {repo.name}: origin/{branch} -- "
                      f"{r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'push failed'}")
        name = Path(common_git_dir(repo) or repo).parent.name
        local = [b for b in git(repo, "for-each-ref", "--format=%(refname:short)",
                                "refs/heads/agent/", check=False).split()
                 if not keep(b) and landed(repo, f"refs/heads/{b}")]
        if not local:
            continue
        if dry:
            print(f"would delete {len(local)} local agent/* branch(es) in {name}")
            continue
        r = subprocess.run(["git", "-C", str(repo), "branch", "-D", *local],
                           capture_output=True, text=True)
        gone = r.stdout.count("Deleted branch")
        held = len(local) - gone
        print(f"pruned {gone} local agent/* branch(es) in {name} (on origin/main)"
              + (f"; {held} kept, checked out in a live worktree" if held else ""))


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
    ap.add_argument("--no-prune-branches", action="store_true",
                    help="keep agent/* branches, pushed and local, already on origin/main")
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

    # Before anything is staged and long before the log is committed, so a bent
    # entry costs a retype rather than a recovery.
    shape = entry_shape_problems(found[1])
    if shape:
        print(f"the log's newest entry ({args.unit}) does not match "
              "`## Entry shape`:\n", file=sys.stderr)
        for pr in shape:
            print(f"  - {pr}", file=sys.stderr)
        print("\nThose markers are how fold-day.py finds a day's SHAs, hardware debts\n"
              "and reviewer lines, so a bent one is data the daily fold cannot carry.\n"
              "Fix the entry and re-run. Nothing has been written.", file=sys.stderr)
        return 1

    stale = unit_task_not_settled(doc, args.unit)
    if stale:
        print(stale, file=sys.stderr)
        return 1

    # A clean log is either the "log only" ordering -- this unit's log commit
    # is the fleet repo's newest and no instance commit names it, so a retry
    # lands the missing half -- or a refusal that says which it is instead.
    resume = None
    if not git(FLEET_REPO, "status", "--porcelain", "--", "supervisor-log.md").strip():
        resume, why = committed_log(args.unit, doc)
        if not resume:
            print(why, file=sys.stderr)
            return 1
        print(f"resuming {args.unit}: its log is committed as embarch-fleet@{resume} "
              f"and no\n{doc.name} commit names it, so this lands the instance half only.")

    # A client's name in a log entry is the one leak a later fix cannot make
    # cheaply: file content is one commit to remove, a landed commit message
    # needs a history rewrite. And THIS repo is the one nothing else scans --
    # `check-docs.py` runs the name check on the instance, the merge gate runs
    # it per code repo, and a leg never checks the framework out at all. On
    # 2026-09-06 a leg had quoted a client project name out of the owner's live
    # `embarch-api/config.toml` into an entry, and it sat on `main` unnoticed
    # because no gate anywhere covers this file. Refused here rather than
    # reported by a gate, because here it is still uncommitted, and because
    # this is the one actor that can fix it: a worker cannot write this repo,
    # so a red it raised elsewhere would be a red nobody could act on.
    names = FLEET_REPO / "scripts" / "check-client-names.py"
    if names.is_file():
        r = subprocess.run([sys.executable, str(names), "--repo", str(FLEET_REPO),
                            "--no-commits"], capture_output=True, text=True)
        if r.returncode:
            print(r.stdout + r.stderr, file=sys.stderr)
            print("Nothing has been written. Reword the entry -- do not paste the\n"
                  "name into the fix's own commit message either.", file=sys.stderr)
            return 1


    # After the guard above, never before it: stamping an unmodified log would
    # manufacture the very uncommitted change that guard exists to detect. And
    # never on a resume, whose entry is already committed.
    note = None if resume else stamp_entry_time(args.unit, datetime.datetime.now(),
                                                apply=not args.dry_run)
    if note:
        print(note)

    # Stage-ability is settled BEFORE the log is committed. `git add` refuses a
    # path that is in neither the worktree nor the index, and a `git rm`'d task
    # file is exactly that -- already staged as a deletion, with nothing left to
    # match. tasks/README.md guarantees every fold has one, so this aborted on
    # every unit of leg 007, twice after the log commit had already landed and
    # twice recovered by hand. The ordering was safe by design and manual every
    # time; now the case is simply understood.
    # A fragment this unit did not write, deleted in the worktree, is the
    # signature of `build_changelog.py` having consumed the whole directory --
    # the fold then carries somebody else's history entries in a file whose
    # path IS in the list, so staging-by-explicit-path cannot see it and the
    # diff review cannot either, because the swept lines are well-formed
    # entries in the right file. Leg 016 landed exactly that with 15 of the
    # owner's pending fragments (`tasks/doc/013`). The assembler now takes
    # `--only`; this refuses the fold if it was run without one anyway.
    swept = [q for q in git(doc, "diff", "--name-only", "--diff-filter=D", "--",
                            "changelog.d").split() if q not in set(args.path)]
    if swept:
        print(f"{len(swept)} changelog fragment(s) were consumed that this unit "
              "did not write:\n", file=sys.stderr)
        for q in swept:
            print(f"  {q}", file=sys.stderr)
        # The assembler lives in the INSTANCE and a leg's worktree freezes it at
        # that leg's start commit, while this script is a shim that execs the
        # framework copy at run time. So a leg can be refused by a new rule
        # while holding an assembler too old to satisfy it. Ask before advising.
        helptext = subprocess.run(
            [sys.executable, str(doc / "scripts" / "build_changelog.py"), "--help"],
            capture_output=True, text=True).stdout
        print("\nThat means `build_changelog.py` ran over the whole directory.",
              file=sys.stderr)
        if "--only" in helptext:
            print("Restore them and re-assemble with only this unit's own:\n\n"
                  "    git checkout -- changelog.d history\n"
                  "    python3 scripts/build_changelog.py --only '<this unit's fragment>'",
                  file=sys.stderr)
        else:
            print("Your checkout's assembler predates `--only`, so park them instead --\n"
                  "this is the dance leg 016 did by hand:\n\n"
                  "    git checkout -- changelog.d history\n"
                  "    mkdir -p ../.held && mv changelog.d/<not-yours>.md ../.held/\n"
                  "    python3 scripts/build_changelog.py\n"
                  "    mv ../.held/*.md changelog.d/", file=sys.stderr)
        print("\nNothing has been written. The fragments are still in git.",
              file=sys.stderr)
        return 1

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
        print(f"would commit to {FLEET_REPO.name}: supervisor-log.md" if not resume
              else f"would resume: the log is already embarch-fleet@{resume}")
        print(f"  staging in: {doc}")
        print(f"would commit to {doc.name}:")
        for p in addable:
            print(f"  {p}")
        for p in to_delete:
            print(f"  {p}  (finished task, this fold deletes it)")
        for p in already:
            print(f"  {p}  (already staged as a deletion)")
        if not args.no_prune_branches:
            prune_landed_branches(doc, args.unit.split("/")[0], dry=True)
        return 0

    # Stage the instance half BEFORE the log commit, so that anything staging
    # can refuse -- a path, a removal, nothing to stage at all -- is refused
    # with nothing written. Until 2026-10-29 this ran after the log commit,
    # while leg.md told every supervisor the script "settles every path
    # before it commits the log"; `dev-bench/034`'s fold proved otherwise and
    # left a log-only commit (tasks/doc/075). Staging is local and repeatable,
    # so a refusal here leaves nothing a retry does not simply re-stage.
    #
    # -A with an EXPLICIT pathspec, never bare: it stages a deletion as well as
    # an add or a modification, for exactly the listed paths and nothing else.
    # Bare `git add -A` is what swept the owner's own fragments into legs 004
    # and 005, and the path allowlist above is what replaces it.
    def stage(*cmd: str) -> bool:
        r = subprocess.run(["git", "-C", str(doc), *cmd], capture_output=True, text=True)
        if r.returncode:
            print(f"git {' '.join(cmd[:3])} ... failed in {doc.name}:\n{r.stderr.strip()}\n\n"
                  "Nothing has been committed, the log included. Fix the path list and\n"
                  "re-run; whatever this run staged is simply staged again.", file=sys.stderr)
        return r.returncode == 0

    if addable and not stage("add", "-A", "--", *addable):
        return 1
    if to_delete:
        # tasks/README.md: a landed task leaves the queue in the same commit
        # that folds its fragments. Git holds it, and a completed task left in
        # the queue competes with the open ones for attention.
        #
        # `-f`, because a task file reaches `done` by being edited, and plain
        # `git rm` refuses an edited file whether the edit is staged or not.
        # The supervisor writes `done` in the fold for every `suite` task (it
        # has no branch to arrive on), and for any unit whose worker left
        # `closed` or `claimed` -- which `unit_task_not_settled()` above makes
        # it correct. So the refusal fired on exactly the edits this script
        # demands, and after the log commit had landed (tasks/doc/050, 072,
        # 075, 082). The file is deleted in this commit, so `-f` discards
        # nothing the fold was not already discarding.
        if not stage("rm", "-q", "-f", "--", *to_delete):
            return 1
    staged = git(doc, "diff", "--cached", "--name-only").strip()
    # A path that produced no change at all is worth a line. The count on its
    # own is not enough: leg 008 read "2 path(s)" for a three-path fold and had
    # to notice the discrepancy by eye.
    quiet = [p for p in args.path if p not in set(staged.split("\n"))]
    for p in quiet:
        print(f"note: {p} staged nothing -- it was already committed unchanged")
    if not staged:
        print(f"nothing staged in {doc.name}, so nothing has been committed"
              + (f"; the log commit embarch-fleet@{resume} still stands alone"
                 if resume else ", the log included")
              + ".\nInvestigate before retrying -- do not write a second entry.",
              file=sys.stderr)
        return 1

    # Log first. If the machine dies between the two, the surviving state is an
    # entry for a fold that did not happen -- recoverable and loud -- rather
    # than a fold nobody logged, which is unrecoverable.
    if resume:
        log_sha = resume
    else:
        git(FLEET_REPO, "add", "--", "supervisor-log.md")
        git(FLEET_REPO, "commit", "-m", f"Log {args.unit}: {args.message}")
        log_sha = head(FLEET_REPO)
    git(doc, "commit", "-m", f"{args.message}\n\nLog: embarch-fleet@{log_sha}")

    print(f"{FLEET_REPO.name}  {log_sha}  supervisor-log.md"
          + ("  (committed earlier; resumed)" if resume else ""))
    print(f"{doc.name}  {head(doc)}  {len(staged.splitlines())} path(s)"
          f"{f', {len(to_delete)} task file(s) retired' if to_delete else ''}")

    # After both commits: the fold is landed, so nothing below may fail it.
    if not args.no_prune_branches:
        prune_landed_branches(doc, args.unit.split("/")[0], dry=False)

    print("\nPush both. A fold is not landed until the log is pushed too.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
