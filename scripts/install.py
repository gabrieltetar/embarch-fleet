#!/usr/bin/env python3
"""Install this fleet into its instance repo, and check it stays installed.

Three kinds of thing have to exist inside the instance repo rather than here,
and they get two different treatments because they fail differently.

**Prose gets copied.** `.claude/commands/` and `.claude/agents/` are only loaded
from the working directory's own `.claude/`, and the four protocol READMEs are
read in place by anyone who opens `tasks/` or `inbox/`. A pointer would not be
read. So they are rendered from `templates/` with `{{PLACEHOLDER}}` expanded from
fleet.toml, and `--check` re-renders and diffs -- which is what stops the copy
drifting from its source, the failure this repo exists to make impossible.

**So does config, and `.claude/settings.json` is the only one.** It carries the
`PermissionRequest` hook that alerts `#embarch-fleet` when an unattended agent is
suspended on a prompt -- the fleet's one backstop for a condition that, by
definition, the blocked agent cannot report itself. It lived in
`.claude/settings.local.json` until 2026-09-05, which is `.gitignore`d and was
not installed from anywhere, so the backstop was unversioned, undeployable and
invisible to `--check`: a re-clone or a wiped settings file dropped it silently.
**The split is by file, not by merge logic** -- Claude Code loads `settings.json`
and `settings.local.json` together, so the fleet owns the first and the owner's
machine-local permissions stay in the second, untouched by this installer. The
hook must therefore never name an absolute path; it resolves the alert script
through `$CLAUDE_PROJECT_DIR` and the committed shim.

**Code gets a shim.** Every doc in the suite names `scripts/check-ownership.py`
and every worker invokes it from a worktree whose depth varies, so the path has
to keep working. A five-line shim that execs the framework copy keeps one
implementation and cannot drift; copying 900 lines of Python would be a second
implementation held equal only by a checker.

**State gets created empty.** The `.fleet/` state directory holds the pump
latch, the tick file and the alert webhook, and lives outside every repo because
the webhook is a secret and the latch must not be committed.

Usage:
  scripts/install.py                 install into the doc_repo named in fleet.toml
  scripts/install.py --check         does the instance match this working tree?
  scripts/install.py --diff          show what --check found, as a diff
  scripts/install.py --verify        was anything generated hand-edited since
                                     the last install? -- what the gate asks
  scripts/install.py --repo PATH     override the target
Exit status: 0 installed / in sync, 1 out of sync, 2 misconfigured.

`--check` and `--verify` answer different questions and only one belongs in a
gate. An instance BEHIND the framework is the normal state between
`deploy.py --queue` and the boundary that lands it; a generated file EDITED IN
PLACE is silently reverted by the next install and must be loud. `--check`
cannot tell them apart, so using it as the gate meant a queued deploy turned
`check-docs.py` red for every worker.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
TEMPLATES = HERE / "templates"

# Framework scripts the instance repo gets a shim for. Anything not listed is
# framework-internal and is never invoked from the instance.
SHIMMED = ("check-ownership.py", "queue-status.py", "usage-budget.py",
           "fleet-alert.py", "fleet-post.py", "fold-commit.py", "fold-day.py",
           "check-client-names.py", "check-dispatch.py")

PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")

SHIM = '''#!/usr/bin/env python3
"""Shim: the implementation lives in the embarch-fleet repo.

Written by `embarch-fleet/scripts/install.py`. Do not edit -- edit the framework
copy and re-run the installer. A shim rather than a copy because there must be
exactly one implementation: two that a checker holds equal is still two.

The framework is located at RUN TIME, not baked in. This file is committed to
the instance repo, so a second checkout on another machine would otherwise get a
path that exists only where the installer ran.
"""
import os, sys

NAME = {name!r}
HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.path.join(os.environ["EMBARCH_FLEET_ROOT"], "embarch-fleet", "scripts", NAME)
    if os.environ.get("EMBARCH_FLEET_ROOT") else None,
    # the documented layout: the framework cloned beside the instance
    os.path.join(HERE, os.pardir, os.pardir, "embarch-fleet", "scripts", NAME),
    # where the installer ran, as a last resort
    {target!r},
]
for c in CANDIDATES:
    if c and os.path.exists(c):
        os.execv(sys.executable, [sys.executable, os.path.abspath(c)] + sys.argv[1:])
sys.exit("fleet framework missing; tried:\\n  " +
         "\\n  ".join(c for c in CANDIDATES if c) +
         "\\nClone embarch-fleet beside this repo and re-run its scripts/install.py.")
'''


def render(text: str, subs: dict[str, str]) -> tuple[str, list[str]]:
    """Expand {{PLACEHOLDER}}. Returns the text and any names it did not know.

    An unknown placeholder is reported rather than left in place: a template
    that silently ships `{{SLACK_OWNER}}` to an agent is a rule with a hole in
    it, and the agent would read the braces as literal text.
    """
    unknown: list[str] = []

    def sub(m):
        k = m.group(1)
        if k not in subs:
            unknown.append(k)
            return m.group(0)
        return subs[k]

    return PLACEHOLDER.sub(sub, text), unknown


def planned(target: Path) -> list[tuple[Path, str, bool]]:
    """Every file the installer owns in the instance: (path, content, is_exec)."""
    base = CONF.substitutions()
    out: list[tuple[Path, str, bool]] = []
    problems: list[str] = []

    def add(src: Path, rel: Path):
        # FLEET_REL is per-file: a markdown link has to resolve from the
        # directory the rendered file lands in, and `tasks/README.md` is one
        # level deeper than `.claude/commands/fleet.md`. Getting this wrong
        # would mean check-links.py fails on files nobody edited by hand.
        #
        # It is computed from the file's CANONICAL location, never from
        # `target`, because the rendered bytes are what gets committed and must
        # not depend on where the render ran from. Computing it from `target`
        # made `--check` fail in every leg and worker worktree -- those sit
        # three levels below the canonical checkout, so the link came out
        # different and the check reported three README files as drifted while
        # `diff` said they were byte-identical. protocol.md §6 step 0 requires
        # a leg to work in a worktree, so that was every leg and every worker:
        # `check-docs.py` was permanently red for a whole class of correct
        # trees, and leg 007 had to tell three workers which reds to ignore.
        # A gate with a standing exception teaches an agent to triage reds,
        # which is the judgement the gate exists to remove.
        canonical = CONF.doc_repo / rel
        subs = dict(base, FLEET_REL=os.path.relpath(HERE, canonical.parent))
        text, unknown = render(src.read_text(), subs)
        if unknown:
            problems.append(f"{src.relative_to(HERE)}: unknown {sorted(set(unknown))}")
        out.append((target / rel, text, False))

    for src in sorted((TEMPLATES / ".claude").rglob("*")):
        if src.is_file() and src.suffix in (".md", ".json"):
            add(src, Path(".claude") / src.relative_to(TEMPLATES / ".claude"))

    for src in sorted((TEMPLATES / "protocol").glob("*.README.md")):
        add(src, Path(src.name.replace(".README.md", "")) / "README.md")

    for name in SHIMMED:
        impl = HERE / "scripts" / name
        if not impl.exists():
            continue
        out.append((target / "scripts" / name,
                    SHIM.format(name=name, target=str(impl)), True))

    if problems:
        print("template placeholders with no value in fleet.toml:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        sys.exit(2)
    return out


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def manifest(target: Path) -> dict[str, str]:
    """Every generated path in the instance, mapped to the hash install writes.

    `deploy.py` records this in `.fleet-version` so `--verify` can answer the
    question the gate actually asks, which is NOT the question `--check` answers.
    """
    return {str(path.relative_to(target)): digest(content)
            for path, content, _ in planned(target)}


def verify(target: Path) -> int:
    """Has anything generated been hand-edited SINCE THE LAST INSTALL?

    `--check` compares the instance against the framework *working tree*, which
    conflates two different failures. A hand-edit here is silently reverted by
    the next install and must be loud. An instance that is merely *behind* the
    framework is neither wrong nor anybody's fault -- it is the normal state
    between `deploy.py --queue` and the leg boundary that lands it, and it is
    also the state of any tree where the owner has edited a template and not
    deployed yet.

    Conflating them meant a queued deploy turned `check-docs.py` RED for every
    worker and every merge gate for the whole window it was queued -- so
    `--queue`, whose entire purpose is deploying without stopping the fleet,
    blocked the fleet instead. Measured 2026-09-06 on the first one issued
    during a live leg. "Is the instance behind?" already has two answers that do
    not live in a gate: the pending-deploy latch, and `deploy.py --dry-run`.

    Hashes rather than a re-render at the installed SHA: a re-render would still
    be read through *today's* `fleet.toml`, shim text and render logic, so it
    reports drift that has nothing to do with the instance. What install wrote
    is a fact, and a fact is what a gate should test.
    """
    stamp = target / ".fleet-version"
    recorded: dict[str, str] = {}
    if stamp.is_file():
        try:
            recorded = json.loads(stamp.read_text()).get("files") or {}
        except (ValueError, OSError):
            recorded = {}
    if not recorded:
        print(f"no file manifest in {stamp.name} -- this instance predates it, or "
              f"was installed\nby install.py directly. Falling back to --check.\n")
        return check(target, diff=False)

    edited, missing = [], []
    for rel, want in sorted(recorded.items()):
        path = target / rel
        if not path.is_file():
            missing.append(rel)
        elif digest(path.read_text()) != want:
            edited.append(rel)

    if edited or missing:
        print(f"{len(edited) + len(missing)} generated file(s) no longer match "
              f"what install wrote:\n")
        for rel in edited:
            print(f"  edited   {rel}")
        for rel in missing:
            print(f"  missing  {rel}")
        print("\nThese are output, not source. Edit the template in embarch-fleet;\n"
              "a hand-edit here is reverted by the next install without a word.")
        return 1
    print(f"OK: all {len(recorded)} generated file(s) match what install wrote.")
    return 0


def check(target: Path, diff: bool) -> int:
    """Does the instance match the framework working tree? Used by deploy.py."""
    stale = []
    for path, content, _ in planned(target):
        rel = path.relative_to(target)
        current = path.read_text() if path.is_file() else None
        if current == content:
            continue
        stale.append(rel)
        if diff:
            print(f"\n--- {rel} (installed)\n+++ {rel} (framework)")
            sys.stdout.writelines(difflib.unified_diff(
                (current or "").splitlines(True), content.splitlines(True), n=1))
    if stale:
        print(f"{len(stale)} installed file(s) differ from the framework:\n")
        for rel in stale:
            print(f"  {rel}")
        print("\nEdit the template in embarch-fleet and re-run scripts/install.py.\n"
              "The instance copy is output, not source.")
        return 1
    print("OK: all installed file(s) match the framework.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="target repo (default: fleet.toml's doc_repo)")
    ap.add_argument("--check", action="store_true", help="verify against the framework, write nothing")
    ap.add_argument("--verify", action="store_true",
                    help="verify nothing generated was hand-edited since the last install")
    ap.add_argument("--diff", action="store_true", help="with --check, show the diffs")
    args = ap.parse_args()

    target = Path(args.repo).resolve() if args.repo else CONF.doc_repo
    if not (target / ".git").exists():
        print(f"not a git repo: {target}", file=sys.stderr)
        return 2

    if args.verify:
        return verify(target)
    if args.check:
        return check(target, args.diff)

    for path, content, is_exec in planned(target):
        rel = path.relative_to(target)
        current = path.read_text() if path.is_file() else None
        if current == content:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if is_exec:
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  wrote {rel}")

    state = CONF.state_dir
    state.mkdir(parents=True, exist_ok=True)
    (state / ".gitignore").write_text("*\n")  # belt and braces: never committable
    print(f"  state dir {state}")
    print(f"\nInstalled into {target}.")
    if not (state / "alert-webhook").exists():
        print("\nNot configured yet: the alert webhook. Without it every alert exits 2\n"
              "and says so, which is the intended failure -- a muted alarm that looks\n"
              "fine is worse than no alarm. Setup is in scripts/fleet-alert.py's header.")
    if not (state / "bot-token").exists():
        print("\nNot configured yet: the bot token. Until it exists the fleet cannot\n"
              "post under its own identity, so ordinary reporting does not reach the\n"
              "channel at all and only alerts get through, via the webhook, without\n"
              "their thread. Setup is in scripts/fleet-post.py's header.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
