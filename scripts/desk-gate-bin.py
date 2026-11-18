#!/usr/bin/env python3
"""Print the path of an `embarch-desk` binary built from desk `origin/main`, for
the chat gate's `EMBARCH_DESK_BIN`.

`embarch-chat`'s desk-gated tests (`test/host.test.mjs`, `test/desk.test.mjs`,
`test/resume.test.mjs`) skip unless `EMBARCH_DESK_BIN` names a desk binary, and
gate.md counted a skip as no red. So 60 tests ran on no unit, and five of them
were red for days from a test-side fault nobody saw (EMB-122). The binary is
built from desk's `origin/main`, never from a checkout's working tree: a stale
binary was the other half of that symptom, and a checkout can be behind or
dirty.

    EMBARCH_DESK_BIN="$(python3 scripts/desk-gate-bin.py)" npm test

stdout is the path and nothing else, so the line above works; progress and
errors go to stderr. The tree at that SHA is exported with `git archive` (not a
worktree: deploy.py reads a registered worktree under the worktree root as a
leg in flight) into `<worktree_root>/desk-gate/src`, and built into
`<worktree_root>/desk-gate/target`, which every build shares, so a rebuild after
desk `main` moves is incremental. `built-sha` beside them says which SHA the
binary is; the same SHA twice is no build at all.

Exit status: 0 the path is printed, 1 the fetch, export or build failed (the
message says which), 2 misconfigured.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

DESK_REPO = "embarch-desk"


def say(msg: str) -> None:
    print(f"desk-gate-bin: {msg}", file=sys.stderr)


def main() -> int:
    repo = CONF.root / DESK_REPO
    if not (repo / ".git").exists():
        say(f"no {DESK_REPO} checkout at {repo}")
        return 2
    base = CONF.worktree_root / "desk-gate"
    src, target, stamp = base / "src", base / "target", base / "built-sha"
    binary = target / "debug" / DESK_REPO

    fetch = subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin", "main"],
                           capture_output=True, text=True)
    if fetch.returncode != 0:
        say(f"git fetch failed: {fetch.stderr.strip()}")
        return 1
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "origin/main"],
                         capture_output=True, text=True, check=True).stdout.strip()

    if binary.exists() and stamp.exists() and stamp.read_text().strip() == sha:
        say(f"current: built from {sha[:12]}")
        print(binary)
        return 0

    say(f"building {DESK_REPO} at origin/main {sha[:12]} (about a minute when desk main moved)")
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True)
    archive = subprocess.Popen(["git", "-C", str(repo), "archive", sha], stdout=subprocess.PIPE)
    untar = subprocess.run(["tar", "-x", "-C", str(src)], stdin=archive.stdout,
                           capture_output=True, text=True)
    archive.stdout.close()
    if archive.wait() != 0 or untar.returncode != 0:
        say(f"exporting {sha[:12]} failed: {untar.stderr.strip()}")
        return 1
    stamp.unlink(missing_ok=True)
    build = subprocess.run(["cargo", "build", "--quiet", "--manifest-path", str(src / "Cargo.toml"),
                            "--target-dir", str(target)], capture_output=True, text=True)
    if build.returncode != 0 or not binary.exists():
        tail = "\n".join(build.stderr.strip().splitlines()[-15:])
        say(f"cargo build failed at {sha[:12]}:\n{tail}")
        return 1
    stamp.write_text(sha + "\n")
    say(f"built from {sha[:12]}")
    print(binary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
