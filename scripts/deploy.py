#!/usr/bin/env python3
"""Render this framework into its instance, gate it, stamp it, commit it.

`install.py` writes files. This is the thing you run: it refuses to deploy into
a live fleet, installs, runs the instance's own gate on the result, records
which framework version produced it, and commits the generated paths -- by
explicit path, never `git add -A`, so a deploy cannot sweep up whatever else is
mid-edit in that checkout.

It deliberately does NOT push and does NOT re-arm. Pushing the instance before
the framework would leave a stamp naming a SHA nobody can fetch, and re-arming
is a Claude Code session doing `/fleet start`, which no shell can do. It prints
what you still owe, in order.

See DEVELOPING.md for the loop this belongs to -- in particular §2, on the fact
that a live cron job keeps the heartbeat prompt it was armed with however many
times `templates/.claude/commands/fleet.md` changes.

Usage:
  scripts/deploy.py                 refuse if live, install, gate, stamp, commit
  scripts/deploy.py --dry-run       say what would change, write nothing
  scripts/deploy.py --no-commit     install and gate, leave the changes unstaged
  scripts/deploy.py --force         deploy anyway (you have checked ListAgents)
  scripts/deploy.py --allow-dirty   stamp an uncommitted framework tree
Exit status: 0 deployed / nothing to do, 1 refused or gate red, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402
from install import planned  # noqa: E402

HERE = Path(__file__).resolve().parent
FLEET_REPO = HERE.parent
STAMP = ".fleet-version"

# Editing this file in the instance is what a re-arm is owed for: arming copies
# the heartbeat prompt into a cron job, so the live job keeps its original
# wording however many times the template changes. They drifted once already.
REARM_TRIGGER = ".claude/commands/fleet.md"


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed in {repo.name}:\n{r.stderr.strip()}")
    return r.stdout


def refuse_if_live(force: bool) -> None:
    """Two proxies, and neither is authoritative -- say so rather than imply it.

    The latch says the pump is on, not that a leg is alive; a leg between units
    holds no worktree. The real check is ListAgents in a session, which a script
    cannot run. Changing the rules under a running supervisor gives you a leg
    that read half its protocol from one version and half from another, and no
    log entry records which.
    """
    reasons = []
    if (CONF.state_dir / "pump").exists():
        reasons.append(f"the pump latch exists ({CONF.state_dir / 'pump'})")

    # A directory under the worktree root is NOT the signal: a leg clones shared
    # crates there for path dependencies, and those stay clean and checked out
    # on main between legs. Six of them were sitting there when this was
    # written. What means work is in flight is a worktree git has registered, or
    # a branch a worker is on.
    for repo in sorted(p for p in CONF.root.iterdir() if (p / ".git").is_dir()):
        for line in git(repo, "worktree", "list", "--porcelain", check=False).splitlines():
            if line.startswith("worktree "):
                path = Path(line[len("worktree "):])
                if CONF.worktree_root in path.parents:
                    reasons.append(f"{repo.name} has a worktree at {path}")
        branches = [b.strip() for b in
                    git(repo, "branch", "--list", "agent/*", "--format=%(refname:short)",
                        check=False).splitlines() if b.strip()]
        if branches:
            reasons.append(f"{repo.name} has {len(branches)} agent branch(es): "
                           + ", ".join(branches[:3]))

    if not reasons:
        return
    if force:
        print("WARNING: deploying into what looks like a live fleet, because "
              "--force:\n  " + "\n  ".join(reasons) + "\n")
        return
    sys.exit("refusing to deploy: the fleet may be running.\n  "
             + "\n  ".join(reasons)
             + "\n\nSay `fleet stop`, let the leg finish its unit, then deploy.\n"
               "Neither check is authoritative -- confirm with ListAgents in a\n"
               "session, then --force if it is genuinely idle.")


def framework_version(allow_dirty: bool) -> dict:
    sha = git(FLEET_REPO, "rev-parse", "HEAD").strip()
    dirty = bool(git(FLEET_REPO, "status", "--porcelain").strip())
    if dirty and not allow_dirty:
        sys.exit("the framework tree has uncommitted changes.\n\n"
                 "Commit them first: a stamp naming a SHA that does not contain\n"
                 "what was rendered is worse than no stamp. Use --allow-dirty if\n"
                 "you are deliberately testing an uncommitted change.")
    return {
        "framework_sha": sha,
        "framework_dirty": dirty,
        "config": str(CONF.path.name),
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "installed_from": str(FLEET_REPO),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="target instance (default: fleet.toml's doc_repo)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    ap.add_argument("--force", action="store_true", help="deploy into a live fleet")
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args()

    target = Path(args.repo).resolve() if args.repo else CONF.doc_repo
    if not (target / ".git").exists():
        sys.exit(f"not a git repo: {target}")

    if not args.dry_run:
        refuse_if_live(args.force)
    version = framework_version(args.allow_dirty or args.dry_run)

    # What the instance already has, so we can report the deploy rather than
    # just performing it -- and so the re-arm question can be answered.
    before = git(target, "status", "--porcelain").strip()
    if before and not args.dry_run:
        print(f"note: {target.name} has {len(before.splitlines())} pre-existing "
              "uncommitted change(s); this deploy stages only its own paths.\n")

    if args.dry_run:
        r = subprocess.run([sys.executable, str(HERE / "install.py"),
                            "--repo", str(target), "--check", "--diff"],
                           capture_output=True, text=True)
        print(r.stdout or r.stderr)
        print(f"would stamp {STAMP} with {version['framework_sha'][:10]}")
        return 0

    print(f"deploying {version['framework_sha'][:10]} -> {target.name}\n")
    r = subprocess.run([sys.executable, str(HERE / "install.py"), "--repo", str(target)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        return 1

    (target / STAMP).write_text(json.dumps(version, indent=2) + "\n")

    # The instance's own gate, on the rendered result. This is what catches a
    # template whose links no longer resolve once {{FLEET_REL}} is expanded --
    # the failure that actually recurs.
    print("\nrunning the instance gate:")
    gate = subprocess.run([sys.executable, str(target / "scripts" / "check-docs.py")],
                          cwd=target, capture_output=True, text=True)
    sys.stdout.write(gate.stdout)
    if gate.returncode != 0:
        sys.stderr.write(gate.stderr)
        print("\nGATE RED. The instance is left rendered but uncommitted, so you can\n"
              "see what broke. Fix the template here, not the copy there.")
        return 1

    # EXACTLY the files this deploy generated, plus the stamp. A prefix filter
    # like "scripts/" was the first version and it was wrong for the same reason
    # `git add -A` is wrong in a fold: the instance's own scripts live there too,
    # and a deploy swept two owner-authored ones into a commit calling them
    # generated. The set is knowable, so use it.
    generated = {str(path.relative_to(target))
                 for path, _, _ in planned(target)} | {STAMP}
    changed = [ln[3:] for ln in git(target, "status", "--porcelain").splitlines()]
    ours = [p for p in changed if p in generated]
    foreign = [p for p in changed if p not in generated]
    if foreign:
        print(f"\nleaving {len(foreign)} non-generated change(s) alone: "
              + ", ".join(foreign[:5]))

    if args.no_commit:
        print(f"\n{len(ours)} generated path(s) left unstaged (--no-commit).")
        return 0

    if not ours:
        print("\nnothing to commit: the instance already matched this version.")
        return 0

    git(target, "add", "--", *ours)
    git(target, "commit", "-m",
        f"Deploy fleet {version['framework_sha'][:10]}\n\n"
        f"Generated by embarch-fleet/scripts/deploy.py. Edit the templates in\n"
        f"that repo, never these copies -- install.py --check is what catches\n"
        f"the difference, and the next deploy reverts a hand-edit silently.\n\n"
        f"Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>")
    print(f"\n{target.name}  {git(target, 'rev-parse', '--short', 'HEAD').strip()}  "
          f"{len(ours)} path(s)")

    print("\nStill yours:")
    print(f"  git -C {FLEET_REPO} push && git -C {target} push")
    print("     framework first -- the stamp names a SHA that must be fetchable.")
    if any(p == REARM_TRIGGER for p in ours):
        print(f"  /fleet start")
        print("     RE-ARM OWED: the heartbeat cron prompt changed, and a live job\n"
              "     keeps the wording it was armed with. Editing the file is not enough.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
