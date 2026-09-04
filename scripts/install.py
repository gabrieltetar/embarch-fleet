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
  scripts/install.py --check         verify the instance matches this repo
  scripts/install.py --diff          show what --check found, as a diff
  scripts/install.py --repo PATH     override the target
Exit status: 0 installed / in sync, 1 out of sync (--check), 2 misconfigured.
"""
from __future__ import annotations

import argparse
import difflib
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
           "fleet-alert.py", "fold-commit.py")

PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")

SHIM = '''#!/usr/bin/env python3
"""Shim: the implementation lives in the embarch-fleet repo.

Written by `embarch-fleet/scripts/install.py`. Do not edit -- edit the framework
copy and re-run the installer. A shim rather than a copy because there must be
exactly one implementation: two that a checker holds equal is still two.
"""
import os, sys
TARGET = {target!r}
if not os.path.exists(TARGET):
    sys.exit(f"fleet framework missing: {{TARGET}}\\n"
             "Clone embarch-fleet beside this repo and re-run its scripts/install.py.")
os.execv(sys.executable, [sys.executable, TARGET] + sys.argv[1:])
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

    def add(src: Path, dst: Path):
        # FLEET_REL is per-file: a markdown link has to resolve from the
        # directory the rendered file lands in, and `tasks/README.md` is one
        # level deeper than `.claude/commands/fleet.md`. Getting this wrong
        # would mean check-links.py fails on files nobody edited by hand.
        subs = dict(base, FLEET_REL=os.path.relpath(HERE, dst.parent))
        text, unknown = render(src.read_text(), subs)
        if unknown:
            problems.append(f"{src.relative_to(HERE)}: unknown {sorted(set(unknown))}")
        out.append((dst, text, False))

    for src in sorted((TEMPLATES / ".claude").rglob("*.md")):
        add(src, target / ".claude" / src.relative_to(TEMPLATES / ".claude"))

    for src in sorted((TEMPLATES / "protocol").glob("*.README.md")):
        add(src, target / src.name.replace(".README.md", "") / "README.md")

    for name in SHIMMED:
        impl = HERE / "scripts" / name
        if not impl.exists():
            continue
        out.append((target / "scripts" / name, SHIM.format(target=str(impl)), True))

    if problems:
        print("template placeholders with no value in fleet.toml:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        sys.exit(2)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="target repo (default: fleet.toml's doc_repo)")
    ap.add_argument("--check", action="store_true", help="verify, write nothing")
    ap.add_argument("--diff", action="store_true", help="with --check, show the diffs")
    args = ap.parse_args()

    target = Path(args.repo).resolve() if args.repo else CONF.doc_repo
    if not (target / ".git").exists():
        print(f"not a git repo: {target}", file=sys.stderr)
        return 2

    files = planned(target)
    stale: list[Path] = []

    for path, content, is_exec in files:
        rel = path.relative_to(target)
        current = path.read_text() if path.is_file() else None
        if current == content:
            continue
        if args.check:
            stale.append(rel)
            if args.diff:
                print(f"\n--- {rel} (installed)\n+++ {rel} (framework)")
                sys.stdout.writelines(difflib.unified_diff(
                    (current or "").splitlines(True), content.splitlines(True), n=1))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if is_exec:
            path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  wrote {rel}")

    if args.check:
        if stale:
            print(f"{len(stale)} installed file(s) differ from the framework:\n")
            for r in stale:
                print(f"  {r}")
            print("\nEdit the template in embarch-fleet and re-run scripts/install.py.\n"
                  "The instance copy is output, not source.")
            return 1
        print(f"OK: all {len(files)} installed file(s) match the framework.")
        return 0

    state = CONF.state_dir
    state.mkdir(parents=True, exist_ok=True)
    (state / ".gitignore").write_text("*\n")  # belt and braces: never committable
    print(f"  state dir {state}")
    print(f"\nInstalled into {target}.")
    if not (state / "alert-webhook").exists():
        print("\nNot configured yet: the alert webhook. Without it every alert exits 2\n"
              "and says so, which is the intended failure -- a muted alarm that looks\n"
              "fine is worse than no alarm. Setup is in scripts/fleet-alert.py's header.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
