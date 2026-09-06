#!/usr/bin/env python3
"""Render this framework into its instance, gate it, stamp it, commit it.

`install.py` writes files. This is the thing you run: it refuses to deploy into
a live fleet, installs, runs the instance's own gate on the result, records
which framework version produced it, and commits the generated paths -- by
explicit path, never `git add -A`, so a deploy cannot sweep up whatever else is
mid-edit in that checkout.

It also caps this repo's own docs before rendering anything
(`check-fleet-doc-size.py`) -- `check-doc-size.py` covers the instance's corpus
and never walked this one.

It deliberately does NOT push and does NOT re-arm. Pushing the instance before
the framework would leave a stamp naming a SHA nobody can fetch, and re-arming
is a Claude Code session doing `/fleet start`, which no shell can do. It prints
what you still owe, in order.

See DEVELOPING.md for the loop this belongs to -- in particular §2, on the fact
that a live cron job keeps the heartbeat prompt it was armed with however many
times `templates/.claude/commands/fleet.md` changes.

**--queue and --from-latch are how a rule change stops costing uptime.** Until
2026-09-06 the only way to deploy was to stop the fleet, because this script
refuses while the pump is latched -- so an owner sitting down to edit a rule took
the fleet down for the sitting. Measured against the 14 h window ending that
morning, that was **~3.7 h of the ~6.6 h in which no leg existed at all**: the
single largest block of lost throughput, and none of it a capacity problem.

So the deploy splits in two. `--queue` is the owner's half: it verifies the
framework tree is committed and that the render would actually change something,
then writes `pending-deploy` in the state directory **pinning the exact framework
SHA**. `--from-latch` is the machine's half, run by an `embarch-deployer` agent
the listener spawns at a leg boundary; it refuses unless HEAD still equals the
pinned SHA and the tree is still clean, then renders, gates, stamps, commits,
pushes both repos, and deletes the latch.

**What makes that safe is the pin, not the agent.** The deployer authors nothing:
it renders content the owner already committed to a repo no leg ever checks out,
and a SHA mismatch is a refusal rather than a newer deploy. It also keeps every
liveness check except the pump latch -- a registered worktree or a surviving
`agent/*` branch still refuses, which is the difference between "the pump is on"
and "a leg is mid-unit". A leg boundary is exactly the moment the first is true
and the second is not. `risks.md` carries the residue.

Usage:
  scripts/deploy.py                 refuse if live, install, gate, stamp, commit
  scripts/deploy.py --dry-run       say what would change, write nothing
  scripts/deploy.py --no-commit     install and gate, leave the changes unstaged
  scripts/deploy.py --force         deploy anyway (you have checked ListAgents)
  scripts/deploy.py --allow-dirty   stamp an uncommitted framework tree
  scripts/deploy.py --queue         pin HEAD for the next leg boundary
  scripts/deploy.py --queue --clear drop a queued deploy
  scripts/deploy.py --from-latch    the deployer agent's half; pushes, then unpins
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


PENDING = "pending-deploy"


def latch_path() -> Path:
    return CONF.state_dir / PENDING


def refuse_if_live(force: bool, ignore_pump: bool = False) -> None:
    """Two proxies, and neither is authoritative -- say so rather than imply it.

    The latch says the pump is on, not that a leg is alive; a leg between units
    holds no worktree. The real check is ListAgents in a session, which a script
    cannot run. Changing the rules under a running supervisor gives you a leg
    that read half its protocol from one version and half from another, and no
    log entry records which.
    """
    reasons = []
    # ignore_pump is --from-latch's one relaxation, and it is the whole point of
    # a leg-boundary deploy: the pump being latched says the fleet is *running*,
    # not that a leg is mid-unit, and at a boundary the first is true while the
    # second is not. Every other reason below is a live-work signal and still
    # refuses.
    if not ignore_pump and (CONF.state_dir / "pump").exists():
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


def queue(target: Path, clear: bool, note: str | None) -> int:
    """The owner's half: pin HEAD so a leg boundary can deploy it unattended."""
    p = latch_path()
    if clear:
        if p.exists():
            p.unlink()
            print(f"unpinned {p}")
        else:
            print("nothing queued")
        return 0

    sha = git(FLEET_REPO, "rev-parse", "HEAD").strip()
    if git(FLEET_REPO, "status", "--porcelain").strip():
        sys.exit("the framework tree has uncommitted changes.\n\n"
                 "A queued deploy pins a SHA, and the whole reason it is safe to\n"
                 "hand to an agent is that the content is already committed and\n"
                 "reviewable. Commit first, then --queue.")

    chk = subprocess.run([sys.executable, str(HERE / "install.py"),
                          "--repo", str(target), "--check", "--diff"],
                         capture_output=True, text=True)
    if chk.returncode == 0:
        print("nothing to deploy: the instance already matches this framework.\n"
              "Not queuing -- a latch for a no-op deploy is a latch that will be\n"
              "cleared by something that did nothing.")
        return 0

    rearm = REARM_TRIGGER in (chk.stdout or "")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "framework_sha": sha,
        "queued_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target": str(target),
        "rearm_owed": rearm,
        "note": note or "",
    }, indent=2) + "\n")
    print(f"queued {sha[:10]} -> {target.name}\n  {p}\n\n"
          "The listener deploys this at the next leg boundary and posts what it\n"
          "did. The fleet keeps running until then; nothing needs stopping.")
    if rearm:
        print("\nRE-ARM WILL BE OWED once it lands: the heartbeat cron prompt\n"
              "changed, and a live job keeps the wording it was armed with. The\n"
              "deployer cannot `/fleet start`; that stays yours.")
    print(f"\nPush the framework now, or the stamp will name a SHA nobody can\n"
          f"fetch:\n  git -C {FLEET_REPO} push")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="target instance (default: fleet.toml's doc_repo)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    ap.add_argument("--force", action="store_true", help="deploy into a live fleet")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--queue", action="store_true",
                    help="pin HEAD in the state directory for a leg-boundary deploy")
    ap.add_argument("--clear", action="store_true", help="with --queue: unpin")
    ap.add_argument("--note", help="with --queue: one line for the deployer to relay")
    ap.add_argument("--from-latch", action="store_true", dest="from_latch",
                    help="the deployer agent's half: deploy exactly the pinned SHA, "
                         "push both repos, delete the latch")
    args = ap.parse_args()

    target = Path(args.repo).resolve() if args.repo else CONF.doc_repo
    if not (target / ".git").exists():
        sys.exit(f"not a git repo: {target}")

    if args.queue:
        return queue(target, args.clear, args.note)

    pinned = None
    if args.from_latch:
        p = latch_path()
        if not p.exists():
            print(f"no deploy queued ({p}); nothing to do.")
            return 0
        pinned = json.loads(p.read_text())
        head = git(FLEET_REPO, "rev-parse", "HEAD").strip()
        if head != pinned["framework_sha"]:
            sys.exit(
                f"refusing: the latch pins {pinned['framework_sha'][:10]} but "
                f"HEAD is {head[:10]}.\n\n"
                "A queued deploy renders exactly the commit the owner pinned. A\n"
                "newer HEAD is content nobody queued, so this is a refusal rather\n"
                "than a fresher deploy. Re-run --queue in the owner's window.")
        if args.repo and Path(args.repo).resolve() != Path(pinned["target"]):
            sys.exit(f"refusing: the latch targets {pinned['target']}")

    if not args.dry_run:
        refuse_if_live(args.force, ignore_pump=args.from_latch)
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

    # This repo's own docs, before anything is rendered. `check-doc-size.py`
    # caps the instance's corpus and has never walked this one, which is how
    # protocol.md and ops.md came to sit at 2.7x the cap DOC-COMPACTION.md §2
    # gives a protocol doc while risks.md's own opening line cited that rule as
    # though it applied. deploy.py is where it belongs: every framework change
    # passes through here, it always runs in the real checkout rather than a
    # worktree, and a leg never runs it at all.
    sz = subprocess.run([sys.executable, str(HERE / "check-fleet-doc-size.py")],
                        capture_output=True, text=True)
    if sz.returncode != 0:
        sys.stdout.write(sz.stdout)
        sys.stderr.write(sz.stderr)
        print("\nNothing was rendered. Shorten the file and re-run.")
        return 1

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
    status = git(target, "status", "--porcelain").splitlines()
    changed = [ln[3:] for ln in status]
    # A path already in the INDEX is the dangerous one: staging by explicit path
    # does not stop `git commit` committing the whole index, so on 2026-09-04 a
    # deploy carried the owner's DOC-CONVENTIONS.md into a commit titled
    # "Deploy fleet". Named separately because the fix below is silent when it
    # works, and a silent fix teaches nobody.
    staged_foreign = [ln[3:] for ln in status
                      if ln[0] not in " ?" and ln[3:] not in generated]
    ours = [p for p in changed if p in generated]
    foreign = [p for p in changed if p not in generated]
    if foreign:
        print(f"\nleaving {len(foreign)} non-generated change(s) alone: "
              + ", ".join(foreign[:5]))
    if staged_foreign:
        print(f"  {len(staged_foreign)} of them are already STAGED and are NOT "
              f"being committed:\n    " + "\n    ".join(staged_foreign[:5])
              + "\n  They stay staged; commit them yourself.")

    if args.no_commit:
        print(f"\n{len(ours)} generated path(s) left unstaged (--no-commit).")
        return 0

    if not ours:
        print("\nnothing to commit: the instance already matched this version.")
        if args.from_latch:
            latch_path().unlink(missing_ok=True)
            print("latch cleared: there was nothing left for it to ask for.")
        return 0

    git(target, "add", "--", *ours)
    # Pathspec-limited: commit these paths and nothing else, whatever else the
    # index holds. `git commit -m` alone commits the whole index -- staging by
    # explicit path is only half of not sweeping up someone's work.
    # `-m` must precede `--`: everything after it is a pathspec, so a message
    # placed there would be committed as a filename.
    git(target, "commit", "-m",
        f"Deploy fleet {version['framework_sha'][:10]}\n\n"
        f"Generated by embarch-fleet/scripts/deploy.py. Edit the templates in\n"
        f"that repo, never these copies -- install.py --check is what catches\n"
        f"the difference, and the next deploy reverts a hand-edit silently.\n\n"
        f"Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>",
        "--", *ours)
    print(f"\n{target.name}  {git(target, 'rev-parse', '--short', 'HEAD').strip()}  "
          f"{len(ours)} path(s)")

    rearm = any(p == REARM_TRIGGER for p in ours)

    if args.from_latch:
        # The deployer pushes, because nobody is sitting there to. Framework
        # first, always: the stamp just committed to the instance names a SHA
        # that must be fetchable, and pushing the instance first would publish a
        # dangling reference to it.
        git(FLEET_REPO, "push")
        git(target, "push")
        latch_path().unlink(missing_ok=True)
        print(f"\npushed both; latch cleared ({latch_path()}).")
        if rearm:
            print("\nRE-ARM OWED, and it is the owner's: the heartbeat cron prompt\n"
                  "changed and a live job keeps the wording it was armed with. Say\n"
                  "so in the channel -- a deployer cannot run `/fleet start`, and a\n"
                  "fleet running the previous tick prompt looks entirely healthy.")
        return 0

    print("\nStill yours:")
    print(f"  git -C {FLEET_REPO} push && git -C {target} push")
    print("     framework first -- the stamp names a SHA that must be fetchable.")
    if rearm:
        print(f"  /fleet start")
        print("     RE-ARM OWED: the heartbeat cron prompt changed, and a live job\n"
              "     keeps the wording it was armed with. Editing the file is not enough.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
