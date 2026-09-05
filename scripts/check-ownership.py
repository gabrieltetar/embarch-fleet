#!/usr/bin/env python3
"""Enforce protocol.md §3's ownership map on a worker's branch.

§3 is the whole conflict-avoidance mechanism -- branches are only the backstop.
But it was written as a table in prose, and nothing checked it: a worker that
edited embarch.md's status table would sail through every other gate, because
`check-staleness.py` only flags a row that *disagrees* with a sub-project doc,
and a worker's edit is plausible by construction. Then two workers touch the
same table in one batch and the supervisor is merging two intents it never held
-- exactly what §9 exists to prevent.

So: given the sub-project a branch belongs to, verify every changed path is one
that sub-project's worker is allowed to write.

In embarch-doc a worker may write:
    embarch-<scope>/**        its own sub-project's four files
    changelog.d/<scope>-*     its own history fragment
    features.d/<scope>-*      its own row in the assembled feature inventory
    status.d/<scope>-*        its request to change a shared suite-level doc
    tasks/<scope>/**          its own task file
and nothing else -- notably not suite/features.md itself, which is assembled
from those fragments and never hand-edited, nor embarch.md, embarch-features.md,
embarch-roadmap.md, embarch-decision-reversals.md, embarch-glossary.md,
embarch-user-guide.md, DOC-PROTOCOL.md, DOC-COMPACTION.md,
embarch-dev-workflow.md, or scripts/. The fleet's own standing rules
live in the embarch-fleet repo, which a leg never checks out at all.

In a code repo the worker owns the whole tree, so the only question this can
answer is whether it is in the right repo at all; pass --code-repo to assert
that and skip the path rules.

The `suite` scope is not a worker scope: a cross-repo change is the supervisor's
(§8), and this refuses it outright rather than granting it everything.

Usage:
  scripts/check-ownership.py --scope api                     # HEAD vs its branch point
  scripts/check-ownership.py --scope api --base origin/main
  git diff --name-only main...HEAD | scripts/check-ownership.py --scope api --stdin
  scripts/check-ownership.py --scope api --code-repo         # in a code repo
Exit status: 0 if every changed path is owned, 1 otherwise.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

# Paths a worker for <scope> may write in embarch-doc, as prefix rules.
def allowed(path: str, scope: str) -> bool:
    return (
        path.startswith(f"embarch-{scope}/")
        or path.startswith(f"tasks/{scope}/")
        or (path.startswith("changelog.d/") and _frag_scope(path, "changelog.d/") == scope)
        or (path.startswith("status.d/") and _frag_scope(path, "status.d/") == scope)
        # A feature row is now a fragment, so a worker writes its OWN row rather
        # than asking the supervisor to hand-fold it into suite/features.md --
        # which is, and stays, outside every worker's row (build_features.py).
        or (path.startswith("features.d/") and _frag_scope(path, "features.d/") == scope)
    )


def _frag_scope(path: str, prefix: str) -> str | None:
    """A fragment is <scope>-<slug>.<...>.md; the scope is the longest known
    prefix, so `dev-bench-foo` resolves to `dev-bench`, not `dev`. Mirrors
    build_changelog.py's own rule rather than inventing a second one."""
    name = path[len(prefix):]
    if "/" in name or name == "README.md":
        return None
    for s in sorted(KNOWN_SCOPES, key=len, reverse=True):
        if name.startswith(s + "-"):
            return s
    return None


# Paths protocol.md §2 reserves to the OWNER. Neither a worker nor the supervisor
# may write them: they are the rules the fleet runs under, the scripts that
# enforce those rules, and the agent definitions that carry them. A supervisor
# that can edit its own constraints has none.
#
# The list is instance data and lives in fleet.toml, because which docs are
# standing rules is a fact about a suite rather than about the fleet. Everything
# in the embarch-fleet repo itself is reserved implicitly: a leg never checks it
# out, so there is no path from a leg's diff to a rule it runs under.
RESERVED = CONF.reserved


def reserved_hits(paths):
    return [p for p in paths if any(p == r or p.startswith(r) for r in RESERVED)]


# Top-level docs the fleet legitimately writes -- also fleet.toml, and for the
# same reason. This list exists only so that RESERVED plus this one is
# EXHAUSTIVE over top-level *.md: see audit() for why that matters. Adding a doc
# here is a decision that it is not a rule the fleet runs under; if in doubt,
# reserve it, because the cost of a wrong reservation is a blocked commit and the
# cost of a wrong omission is a supervisor editing its own constraints.
FLEET_WRITABLE = CONF.fleet_writable


def audit(repo_root: str):
    """Every tracked top-level *.md must be classified, in one list or the other.

    RESERVED is a denylist of filenames, and that broke once already: the risk
    register was §12 of protocol.md until its size cap split it
    into risks.md on 2026-09-03, and reserved content stopped
    being reserved purely by moving. Nothing noticed for a day. DOC-COMPACTION.md
    tells a doc to split at its cap and knows nothing about ownership, so the
    same split can happen again at any time.

    This makes the next one loud instead of silent. A new top-level doc -- from a
    split, or written from scratch -- is unclassified until a human puts it in a
    list, and that is exactly the moment to decide which one.
    """
    out = subprocess.run(["git", "-C", repo_root, "ls-files", "*.md"],
                         capture_output=True, text=True).stdout.split()
    top = sorted(p for p in out if "/" not in p)
    known = set(RESERVED) | set(FLEET_WRITABLE)
    return [p for p in top if p not in known], len(top)


def known_scopes(repo_root: str) -> set[str]:
    out = subprocess.run(["git", "-C", repo_root, "ls-tree", "--name-only", "HEAD"],
                         capture_output=True, text=True).stdout.split()
    return {d.replace("embarch-", "") for d in out if d.startswith("embarch-") and "." not in d} | {"doc", "suite"}


def _git(repo_root: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo_root, *args],
                          capture_output=True, text=True)


def _merge_base(repo_root: str, ref: str) -> str | None:
    """Where this branch actually left `ref`, or None if `ref` does not exist."""
    if _git(repo_root, "rev-parse", "--verify", "-q", ref).returncode != 0:
        return None
    r = _git(repo_root, "merge-base", ref, "HEAD")
    return r.stdout.strip() or None


def pick_base(repo_root: str) -> str | None:
    """The FURTHEST-FORWARD merge-base among the candidate refs -- not a fixed
    preference between them.

    Preferring one ref outright is wrong in both directions, and this check has
    now been red on a clean branch for each of them:

      * `origin/main` first is wrong when the supervisor's claim commit is still
        unpushed. The branch is cut from local `main`, `origin/main` is behind
        it, and every other task file in that claim shows up as a path the
        worker "changed". Batch 003, on both workers.
      * local `main` first is wrong when the worktree's `main` is STALE. A leg
        worktree freezes local `main` at the leg's start commit, while a branch
        cut later in the same leg is cut from `origin/main`, which an earlier
        unit's fold has advanced. The diff then sweeps in that fold. Leg 010,
        on the `umbrella/005` worker, red on `tasks/api/010-...`.

    Both are the same question -- which ref is this branch actually descended
    from -- and neither ref answers it; the merge-base does. Take each
    candidate's merge-base with HEAD and keep the one the others are ancestors
    of. It is the branch point in both cases above, and it needs no fetch to be
    correct, so a stale worktree stops mattering rather than having to be
    maintained.
    """
    bases = [b for b in (_merge_base(repo_root, ref) for ref in ("main", "origin/main")) if b]
    if not bases:
        return None
    best = bases[0]
    for b in bases[1:]:
        if b != best and _git(repo_root, "merge-base", "--is-ancestor", best, b).returncode == 0:
            best = b
    return best


def changed_paths(base: str | None, repo_root: str) -> list[str]:
    """An explicit --base keeps three-dot (`<base>...HEAD`), so the documented
    invocations mean what they always did. The default resolves to a commit
    rather than a ref, so two-dot is already the branch point."""
    spec = f"{base}...HEAD" if base else None
    if spec is None:
        picked = pick_base(repo_root)
        if picked is None:
            print("cannot find a base ref (tried main, origin/main); pass --base", file=sys.stderr)
            sys.exit(2)
        # Say which commit, not which ref: the whole point is that the ref name
        # is not the answer, and a reader who has to re-derive the branch point
        # by hand is the reader who waves a red check through.
        print(f"base: {picked[:12]} (merge-base of HEAD with main/origin/main)", file=sys.stderr)
        spec = picked
    r = _git(repo_root, "diff", "--name-only", spec)
    if r.returncode != 0:
        print(r.stderr.strip(), file=sys.stderr)
        sys.exit(2)
    return [p for p in r.stdout.split("\n") if p.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scope", default="", help="sub-project, without the embarch- prefix")
    ap.add_argument("--base", help="ref to diff against (default: the branch point -- see pick_base)")
    ap.add_argument("--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--stdin", action="store_true", help="read changed paths from stdin instead of git")
    ap.add_argument("--supervisor", action="store_true",
                    help="check a supervisor's own batch commits: reject any path "
                         "§2 reserves to the owner (standing rules, scripts/, .claude/)")
    ap.add_argument("--code-repo", action="store_true",
                    help="this is the worker's own code repo, where it owns the whole tree")
    args = ap.parse_args()

    if args.supervisor:
        paths = ([p.strip() for p in sys.stdin.read().split("\n") if p.strip()]
                 if args.stdin else changed_paths(args.base, args.repo))
        rc = 0
        bad = reserved_hits(paths)
        if bad:
            print(f"{len(bad)} path(s) the supervisor may not write "
                  f"(protocol.md §2 reserves them to the owner):\n")
            for p in bad:
                print(f"  {p}")
            print("\nA supervisor that can edit its own constraints has none. If one of\n"
                  "these genuinely needs changing, that is the owner's commit, not a batch's.")
            rc = 1
        else:
            print(f"OK: none of the {len(paths)} changed path(s) is owner-reserved.")

        # Repo-state assertion, not a fact about this diff: see audit().
        unclassified, total = audit(args.repo)
        if unclassified:
            print(f"\n{len(unclassified)} top-level doc(s) classified by neither "
                  f"list, so nothing knows whether the fleet may write them:\n")
            for u in unclassified:
                print(f"  {u}")
            print("\nAdd each to RESERVED or to FLEET_WRITABLE in this script, and to\n"
                  "protocol.md §3's table if it is reserved. A doc that\n"
                  "appears from a DOC-COMPACTION.md split carries its old file's rules\n"
                  "and none of its old file's protection -- that is how the risk register\n"
                  "stopped being owner-reserved on 2026-09-03.")
            rc = 1
        else:
            print(f"OK: all {total} top-level doc(s) classified.")
        return rc

    global KNOWN_SCOPES
    KNOWN_SCOPES = known_scopes(args.repo)

    # A code repo has no `embarch-*` directories to derive the scope list from,
    # so validating the scope there is impossible -- and it used to run BEFORE
    # the --code-repo return, which made the documented worker invocation die
    # with `unknown scope 'api' (known: doc, suite)`. Both workers of batch 001
    # hit it independently. The scope is already validated by the task file that
    # named it, so --code-repo skips the check rather than faking a list.
    if args.code_repo:
        paths = ([p.strip() for p in sys.stdin.read().split("\n") if p.strip()]
                 if args.stdin else changed_paths(args.base, args.repo))
        print(f"OK: code repo, worker for '{args.scope}' owns the whole tree "
              f"({len(paths)} path(s) changed, not path-checked).")
        return 0

    if not args.scope:
        print("--scope is required unless --supervisor is passed")
        return 2

    if args.scope == "suite":
        print("REFUSED: `suite` is not a worker scope -- a cross-repo change is the")
        print("supervisor's to execute in one sequenced pass (protocol.md §8).")
        return 1

    if args.scope == "fleet":
        # `embarch-doc/embarch-fleet/` exists because DOC-PROTOCOL.md §3 gives
        # every sub-project a directory. It is the suite's view of this
        # framework, and creating it also created a scope name that the
        # `embarch-<scope>/**` rule would otherwise grant to a worker -- a door
        # back into the fleet's own rules, opened by a doc-layout convention
        # rather than by anyone deciding it. Refused here and reserved in
        # fleet.toml, so neither a worker nor a supervisor can write it.
        print("REFUSED: `fleet` is not a worker scope. `embarch-fleet/` is the suite's")
        print("view of the framework the fleet runs under, and protocol.md §2 reserves")
        print("the whole class to the owner -- as it does this repo itself.")
        return 1
    # Every doc that names this check writes it as `--scope <sub-project>`, which a
    # reader fills in as `embarch-core`, while the scope vocabulary is the bare
    # `core`. Accept both: the prefixed form identifies exactly one scope, so
    # refusing it is a false red on a correct branch -- found by running it.
    if args.scope.startswith("embarch-") and args.scope[len("embarch-"):] in KNOWN_SCOPES:
        args.scope = args.scope[len("embarch-"):]

    if args.scope not in KNOWN_SCOPES:
        print(f"unknown scope '{args.scope}' (known: {', '.join(sorted(KNOWN_SCOPES))})")
        return 1

    paths = ([p.strip() for p in sys.stdin.read().split("\n") if p.strip()]
             if args.stdin else changed_paths(args.base, args.repo))

    bad = [p for p in paths if not allowed(p, args.scope)]
    if bad:
        print(f"{len(bad)} path(s) outside what an '{args.scope}' worker may write "
              f"(protocol.md §3):\n")
        claims = []
        for p in bad:
            hint = ""
            if p in ("embarch.md", "embarch-features.md", "embarch-roadmap.md",
                     "embarch-decision-reversals.md", "embarch-glossary.md",
                     "embarch-user-guide.md"):
                hint = "  <- drop a status.d/ fragment instead (§9)"
            elif p.startswith("scripts/") or p.startswith("DOC-"):
                hint = "  <- supervisor or owner only"
            elif p.startswith("tasks/"):
                # This used to be almost certainly NOT the worker's edit: a
                # mis-chosen base swept a leg's other claims into every worker's
                # diff (leg 008, nine such paths by its fourth worker; leg 010
                # again from the other direction). pick_base ended that class,
                # so the note now says so rather than offering the excuse first.
                claims.append(p)
                hint = "  <- another scope's task file; see the note below"
            elif p.startswith("embarch-"):
                hint = "  <- another sub-project's docs"
            print(f"  {p}{hint}")
        print(f"\nAllowed for '{args.scope}': embarch-{args.scope}/**, tasks/{args.scope}/**, "
              f"changelog.d/{args.scope}-*, features.d/{args.scope}-*, "
              f"status.d/{args.scope}-*")
        if claims:
            # Named, never excused. The failure this guards against is a
            # supervisor waving a REAL violation through as "just the claim
            # commit again", and that only stays impossible while the two read
            # differently. So this says which it is; it does not decide.
            print(f"\n{len(claims)} of those are another scope's task file, which a worker\n"
                  "normally cannot have written. The base printed above is this branch's\n"
                  "own merge-base, so a leg's other claims are no longer swept in by\n"
                  "construction -- which means this is far more likely to be REAL than it\n"
                  "was for legs 008 and 010. Do NOT treat it as routine. Check your own\n"
                  "diff (`git diff --name-only <the base above>..HEAD`); if it really is\n"
                  "clean, say so in your report and name the base -- fixing it is the\n"
                  "supervisor's (embarch-fleet protocol.md §6 step 2).")
        return 1

    print(f"OK: all {len(paths)} changed path(s) owned by the '{args.scope}' worker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
