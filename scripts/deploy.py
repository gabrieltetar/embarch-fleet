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
the listener spawns at a leg boundary; it refuses unless the pin is still an
ancestor of HEAD with **no render input changed since**, and the tree is still
clean of them, then renders, gates, stamps, commits, pushes both repos, and
deletes the latch. HEAD is allowed to have moved *only* in the fleet's own log
-- see `unrelated_to_render`, and the reason that is not a loophole.

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
from fleetconf import (ARMED_PROMPTS, CONF, armed_stamp,  # noqa: E402
                       cron_block)
from install import manifest, planned  # noqa: E402

HERE = Path(__file__).resolve().parent
FLEET_REPO = HERE.parent
STAMP = ".fleet-version"

# Arming copies a heartbeat prompt into a cron job, so the live job keeps its
# original wording however many times the template changes -- they drifted once
# already. Both armed windows have one: the listener's tick and the watchdog's.
def rearm_detail(target: Path) -> list[tuple[str, str]]:
    """Which armed prompts a re-arm is owed for, and why. Empty means none.

    Keying on the filename -- which this did until 2026-09-06 -- meant editing
    one line of surrounding prose raised a re-arm alarm the owner had to
    overrule by hand, and the vocabulary around the block is re-read from disk
    on every tick, so it owes nothing. A warning that is usually wrong is one
    that gets ignored the time it is right, and this one is relayed to Slack
    with an `@`. It also covers the watchdog, whose block is the same trap and
    was checked by nothing at all.

    **The live side is the arming stamp, not the repo.** Inferring it from the
    repo -- the working tree, then `HEAD` -- was wrong in both forms, and the
    second one only more quietly. On 2026-09-07 `install.py` had been run by
    hand, so the working-tree comparison read new-against-new, reported nothing
    owed, and the listener spent twenty minutes spawning legs with a tick
    prompt that named the wrong file. `HEAD` fixes that case and still answers
    a different question than the one that matters: **a commit is not evidence
    that any window read it.** Arming now records the block it armed with
    (`fleet-armed.py --stamp`), so this compares the render against what is
    actually running.

    An unstamped prompt is owed. A window armed before stamping existed is
    indistinguishable from one never armed at all, and the safe reading of both
    is the same: a re-arm costs one command, a missed one leaves a fleet
    running a rule nobody can see. It self-clears on the next arming.
    """
    want = {p: c for p, c, _ in planned(target)}
    owed: list[tuple[str, str]] = []
    for rel in ARMED_PROMPTS:
        fresh = want.get(target / rel)
        if fresh is None:
            owed.append((rel, "not a generated file in this instance"))
            continue
        stamp = armed_stamp(rel)
        try:
            was = stamp.read_text().rstrip("\n")
        except OSError:
            owed.append((rel, "never stamped -- armed before this was recorded, "
                              "or not armed at all"))
            continue
        if was != cron_block(fresh):
            owed.append((rel, "the live job carries older wording"))
    return owed


def rearm_owed(target: Path) -> bool:
    """True if any armed prompt is stale. See `rearm_detail` for which."""
    return bool(rearm_detail(target))


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed in {repo.name}:\n{r.stderr.strip()}")
    return r.stdout


# Paths in THIS repo that the fleet writes while it runs, and which are not
# inputs to the render. A leg's fold commits `supervisor-log.md` here on every
# unit -- the only path a leg ever touches in this repo -- and `fold-day.py
# --roll` moves whole days into `log-archive/`.
#
# Without this distinction `--queue` cannot work at all, which is what it did.
# It pinned HEAD and `--from-latch` required HEAD to still equal that SHA and
# the tree to still be clean; both go false within about ten minutes, because
# the fleet commits its own log to its own framework repo on every fold. So a
# queue issued while the fleet was running -- the only case --queue exists for,
# and the whole ~3.7 h of uptime it was built to recover -- was guaranteed to be
# refused at the boundary it was waiting for. Caught 2026-09-06 on the first
# --queue issued during a live leg, by which time HEAD was already the leg's
# next fold. The safety property is unchanged: what may move between the pin and
# the deploy is the fleet's own bookkeeping and nothing else, so the deployer
# still renders exactly the content the owner pinned.
def unrelated_to_render(paths) -> list[str]:
    """Those of `paths` that are not the fleet's own running bookkeeping."""
    # `p and` is load-bearing: `git diff --name-only` ends in a newline, and the
    # empty string that splitting leaves behind is not "supervisor-log.md", so
    # without it every queued deploy refuses on a path that is not a path.
    return sorted(p for p in paths
                  if p and p != "supervisor-log.md"
                  and not p.startswith("log-archive/"))


def dirty_paths() -> list[str]:
    """Uncommitted paths in the framework tree, as porcelain reports them."""
    out = []
    for line in git(FLEET_REPO, "status", "--porcelain").splitlines():
        path = line[3:]
        if " -> " in path:  # a rename reports "old -> new"; the new name is the file
            path = path.split(" -> ", 1)[1]
        out.append(path.strip().strip('"'))
    return out


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
    # "Dirty" means the RENDER INPUTS are uncommitted. An in-flight
    # `supervisor-log.md` is a leg mid-fold, which says nothing about what this
    # deploy would render and is true at a random ~10% of moments.
    unstaged = unrelated_to_render(dirty_paths())
    dirty = bool(unstaged)
    if dirty and not allow_dirty:
        sys.exit("the framework tree has uncommitted changes:\n  "
                 + "\n  ".join(unstaged) +
                 "\n\nCommit them first: a stamp naming a SHA that does not contain\n"
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
    unstaged = unrelated_to_render(dirty_paths())
    if unstaged:
        sys.exit("the framework tree has uncommitted changes:\n  "
                 + "\n  ".join(unstaged) +
                 "\n\nA queued deploy pins a SHA, and the whole reason it is safe to\n"
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

    rearm = rearm_owed(target)
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
        print("\nRE-ARM WILL BE OWED once it lands -- a live job keeps the wording it\n"
              "was armed with:")
        for rel, why in rearm_detail(target):
            print(f"  {rel}: {why}")
        print("The deployer cannot `/fleet start`; that stays yours.")
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
        pin = pinned["framework_sha"]
        if head != pin:
            # HEAD is EXPECTED to have moved: the fleet commits its own log here
            # on every fold while the latch waits for a boundary. What must not
            # have moved is anything the render reads.
            ahead = subprocess.run(
                ["git", "-C", str(FLEET_REPO), "merge-base", "--is-ancestor", pin, head],
                capture_output=True, text=True).returncode == 0
            if not ahead:
                sys.exit(
                    f"refusing: the latch pins {pin[:10]}, which is not an "
                    f"ancestor of HEAD {head[:10]}.\n\n"
                    "The branch was reset, rewritten or diverged since the queue, so\n"
                    "the pinned content is not simply older than what is here.\n"
                    "Re-run --queue in the owner's window.")
            drift = unrelated_to_render(
                git(FLEET_REPO, "diff", "--name-only", pin, head).splitlines())
            if drift:
                sys.exit(
                    f"refusing: {len(drift)} path(s) changed between the pinned "
                    f"{pin[:10]} and HEAD {head[:10]}:\n  "
                    + "\n  ".join(drift) +
                    "\n\nA queued deploy renders exactly the commit the owner pinned.\n"
                    "These are content nobody queued, so this is a refusal rather\n"
                    "than a fresher deploy. Re-run --queue in the owner's window.")
            print(f"pinned {pin[:10]}; HEAD is {head[:10]} and differs only in the\n"
                  "fleet's own log, which the render does not read.\n")
        if args.repo and Path(args.repo).resolve() != Path(pinned["target"]):
            sys.exit(f"refusing: the latch targets {pinned['target']}")

    if not args.dry_run:
        refuse_if_live(args.force, ignore_pump=args.from_latch)

    # Before install.py overwrites the installed copies, or there is nothing
    # left to compare them against.
    rearm = rearm_owed(target)
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

    # The same argument as the size cap, for the same reason: this repo is the
    # one nothing else scans. `check-docs.py` runs the name check on the
    # instance and the merge gate runs it per code repo, and a leg never checks
    # the framework out -- so on 2026-09-06 a client project name quoted into a
    # log entry reached `main` with every gate green. `fold-commit.py` refuses
    # it on the leg's path; this is the owner's.
    cn = subprocess.run([sys.executable, str(HERE / "check-client-names.py"),
                         "--repo", str(FLEET_REPO), "--no-commits"],
                        capture_output=True, text=True)
    if cn.returncode != 0:
        sys.stdout.write(cn.stdout)
        sys.stderr.write(cn.stderr)
        print("\nNothing was rendered. Reword it and re-run -- and keep the name "
              "out of the fixing commit's own message.")
        return 1

    print(f"deploying {version['framework_sha'][:10]} -> {target.name}\n")
    r = subprocess.run([sys.executable, str(HERE / "install.py"), "--repo", str(target)],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        return 1

    # The manifest of what was just written, so `install.py --verify` can ask
    # "was anything generated hand-edited since?" without re-rendering. That is
    # the question the instance's gate needs; `--check`'s "does this match the
    # framework working tree?" is a different one, and answering it in a gate
    # turned every queued deploy into a red gate for every worker.
    version["files"] = manifest(target)
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

    # `rearm` was computed before install.py ran, and it has to be: afterwards
    # the installed copy equals the framework and the comparison is always False.

    if args.from_latch:
        # The deployer pushes, because nobody is sitting there to. Framework
        # first, always: the stamp just committed to the instance names a SHA
        # that must be fetchable, and pushing the instance first would publish a
        # dangling reference to it.
        git(FLEET_REPO, "push")
        git(target, "push")
        latch_path().unlink(missing_ok=True)
        print(f"\npushed both; latch cleared ({latch_path()}).")
        detail = rearm_detail(target)
        if detail:
            print("\nRE-ARM OWED, and it is the owner's -- a live job keeps the wording\n"
                  "it was armed with:")
            for rel, why in detail:
                print(f"  {rel}: {why}")
            print("Say so in the channel: a deployer cannot run `/fleet start`, and a\n"
                  "fleet running the previous tick prompt looks entirely healthy.")
        return 0

    print("\nStill yours:")
    print(f"  git -C {FLEET_REPO} push && git -C {target} push")
    print("     framework first -- the stamp names a SHA that must be fetchable.")
    detail = rearm_detail(target)
    if detail:
        print("  re-arm the window that owns each of these:")
        for rel, why in detail:
            who = "/fleet watch" if "watch" in rel else "/fleet start"
            print(f"     {who:14} {rel}\n     {'':14} {why}")
        print("     A live cron job keeps the wording it was armed with, so editing\n"
              "     the file is not enough. `scripts/fleet-armed.py --check --diff`\n"
              "     says the same thing at any time, not only after a deploy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
