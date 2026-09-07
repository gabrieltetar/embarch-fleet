#!/usr/bin/env python3
"""Install the pre-push hook git actually reads, and verify it is current.

Why this is separate from `install.py`: that one renders the INSTANCE -- the
`.claude/` tree and the protocol READMEs in `doc_repo` -- and stamps
`.fleet-version`, which `deploy.py` gates and a queued deploy pins to a SHA.
A git hook is neither framework prose nor instance config: it is local state
outside every repo, and it is not versioned by the repos it protects.

**It goes where `core.hooksPath` points, not in `.git/hooks`.** This machine
sets `core.hooksPath = ~/.git-hooks-personal` from `~/.gitconfig-personal`,
included by an `includeIf "gitdir:<fleet root>/"` -- so that directory is
already fleet-scoped, and a per-repo `.git/hooks/pre-push` would be **silently
ignored**. The first version of this script wrote ten of those, and wrote them
into a literal `~` directory inside each repo because it did not expand the
tilde. Both mistakes are the same one: assuming where git looks instead of
asking it.

**Worktrees are covered for free**, which is much of the point: a leg and every
worker push from a worktree, and hooksPath is config, shared by every worktree
of every repo it covers. One install covers every agent that will ever push.

**The hook that was already there is preserved, not replaced.** It refused a
push to a non-personal GitHub remote -- a real credential guard, and one that
lived in an unversioned file. Its logic now sits at the top of
`hooks/pre-push`, versioned, and runs first and unconditionally; the previous
file is kept as `pre-push.pre-embarch.bak` on the first install.

Usage:
  scripts/install-hooks.py            install or refresh
  scripts/install-hooks.py --check    report drift; exit 1 if stale
Exit status: 0 current, 1 drift (--check) or nothing to install into.
"""
from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "hooks" / "pre-push"

SHIM = '''#!/usr/bin/env bash
# Managed by embarch-fleet/scripts/install-hooks.py -- DO NOT EDIT HERE.
# The implementation, including the credential guard that used to live in this
# file, is versioned at:
#   {source}
# `install-hooks.py --check` reports a hand-edit; `install-hooks.py` restores it.
exec "{source}" "$@"
'''


def hooks_path() -> Path | None:
    """Where git will look for hooks in the fleet's repos.

    Asked of git, in the doc repo, so an `includeIf` and a `~` are resolved the
    way git resolves them rather than the way a script guesses.
    """
    r = subprocess.run(["git", "-C", str(CONF.doc_repo), "config", "core.hooksPath"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(os.path.expanduser(r.stdout.strip()))
    r = subprocess.run(["git", "-C", str(CONF.doc_repo), "rev-parse", "--git-common-dir"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    common = Path(r.stdout.strip())
    if not common.is_absolute():
        common = CONF.doc_repo / common
    return common / "hooks"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report drift, change nothing")
    args = ap.parse_args()

    base = hooks_path()
    if base is None:
        print("cannot ask git where hooks live; is the doc repo a git repo?")
        return 1
    dest = base / "pre-push"
    # Rendered beside the shim rather than inside the repo: the template holds
    # placeholders and is not runnable, and a rendered copy in `scripts/hooks/`
    # would sit in the tree as an untracked near-duplicate of a versioned file.
    live_impl = base / "pre-push.embarch-impl"
    want = SHIM.format(source=live_impl)

    # The implementation itself carries two absolute paths. Rendering them at
    # install time rather than reading fleet.toml from bash keeps the hook a
    # plain script with no import path to get wrong.
    impl = SOURCE.read_text(encoding="utf-8")
    rendered_impl = (impl.replace("__FLEET_SCRIPTS__", str(HERE))
                         .replace("__FLEET_ROOT__", str(CONF.root)))

    print(f"hooks path (asked of git): {base}")
    have = dest.read_text(encoding="utf-8") if dest.exists() else None
    impl_have = live_impl.read_text(encoding="utf-8") if live_impl.exists() else None
    shim_ok = have == want
    impl_ok = impl_have == rendered_impl

    if args.check:
        if shim_ok and impl_ok:
            print("OK: pre-push shim and implementation are current.")
            return 0
        if not shim_ok:
            print(f"  STALE shim at {dest}"
                  + ("" if have is not None else "  (missing)"))
        if not impl_ok:
            print(f"  STALE rendered implementation at {live_impl}")
        print("\nRun without --check.")
        return 1

    if have is not None and not shim_ok:
        backup = dest.with_suffix(".pre-embarch.bak")
        if not backup.exists():
            backup.write_text(have, encoding="utf-8")
            print(f"  kept the previous hook as {backup}")

    live_impl.write_text(rendered_impl, encoding="utf-8")
    live_impl.chmod(live_impl.stat().st_mode | stat.S_IXUSR)
    # The shim execs the rendered copy, not the template -- a template with
    # placeholders left in is not runnable, and a hook that silently fails open
    # is the worst of the three outcomes.
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(SHIM.format(source=live_impl), encoding="utf-8")
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  installed shim   {dest}")
    print(f"  rendered impl    {live_impl}")
    print("\nOK: pre-push installed. It blocks on a client name, warns on a task\n"
          "number, and keeps the credential guard first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
