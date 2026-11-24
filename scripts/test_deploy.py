#!/usr/bin/env python3
"""deploy.py's sibling fast-forward against scratch clones (EMB-285).

    python3 scripts/test_deploy.py

The instance gate reads the sibling code clones, which no leg advances. A
deploy must bring a clean one level with origin before the gate, and name the
ones it may not move rather than gate against them silently.
"""
import importlib.util
import os
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = tempfile.TemporaryDirectory()
ROOT = Path(TMP.name)
toml = (HERE.parent / "fleet.toml").read_text()
(ROOT / "fleet.toml").write_text(re.sub(r'^root = ".*"$', f'root = "{ROOT}"', toml, flags=re.M))
os.environ["EMBARCH_FLEET_CONF"] = str(ROOT / "fleet.toml")

spec = importlib.util.spec_from_file_location("deploy", HERE / "deploy.py")
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def clone(name):
    """A bare origin with one commit, and a clone of it under the root."""
    bare = ROOT / "remotes" / f"{name}.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
    seed = ROOT / "seeds" / name
    subprocess.run(["git", "clone", "-q", str(bare), str(seed)], check=True, capture_output=True)
    (seed / "f.txt").write_text("one\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-qm", "one")
    git(seed, "push", "-q", "origin", "HEAD:main")
    path = ROOT / name
    subprocess.run(["git", "clone", "-q", str(bare), str(path)], check=True, capture_output=True)
    return path, seed


def advance(seed):
    (seed / "g.txt").write_text(f"{len(list(seed.iterdir()))}\n")
    git(seed, "add", "-A")
    git(seed, "commit", "-qm", "next")
    git(seed, "push", "-q", "origin", "HEAD:main")


class Siblings(unittest.TestCase):
    def test_a_clean_clone_moves_and_the_others_are_named_or_left(self):
        target, _ = clone("embarch-doc")
        behind, s1 = clone("embarch-api")
        dirty, s2 = clone("embarch-core")
        branched, s3 = clone("embarch-ui")
        current, _ = clone("embarch-desk")
        ahead, _ = clone("embarch-atlas")
        for seed in (s1, s2, s3):
            advance(seed)
        (dirty / "f.txt").write_text("edited\n")
        git(branched, "checkout", "-qb", "work")
        (ahead / "h.txt").write_text("mine\n")
        git(ahead, "add", "-A")
        git(ahead, "commit", "-qm", "mine")
        before = {p: git(p, "rev-parse", "HEAD") for p in (dirty, branched, current, ahead)}

        out = StringIO()
        with redirect_stdout(out):
            stale = deploy.fast_forward_siblings(target)

        self.assertEqual(git(behind, "rev-parse", "HEAD"), git(behind, "rev-parse", "origin/main"))
        self.assertIn("fast-forwarded embarch-api main by 1 commit(s)", out.getvalue())
        self.assertEqual(stale, ["embarch-core (on main, 1 commit(s) behind origin/main, with uncommitted changes)",
                                 "embarch-ui (on work, 1 commit(s) behind origin/main)"])
        for p, sha in before.items():
            self.assertEqual(git(p, "rev-parse", "HEAD"), sha, f"{p.name} was moved")
        self.assertEqual((dirty / "f.txt").read_text(), "edited\n")


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        TMP.cleanup()
