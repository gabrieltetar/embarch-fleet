#!/usr/bin/env python3
"""install.py against a scratch instance repo.

    python3 scripts/test_install.py
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
INSTALL = HERE / "install.py"


def run(*args):
    return subprocess.run([sys.executable, str(INSTALL), *args], capture_output=True, text=True)


def tree(root: Path) -> dict:
    """Every file under root but .git, with its text and x bit."""
    return {str(p.relative_to(root)): (p.read_bytes(), os.access(p, os.X_OK))
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


class Install(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def tearDown(self):
        self.dir.cleanup()

    def test_diff_alone_writes_nothing(self):
        before = tree(self.repo)
        r = run("--repo", str(self.repo), "--diff")
        self.assertEqual(tree(self.repo), before, r.stdout + r.stderr)
        self.assertEqual(r.returncode, 1, "an empty instance differs from the framework")

    def test_a_shim_without_its_x_bit_fails_check(self):
        r = run("--repo", str(self.repo))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(run("--repo", str(self.repo), "--check").returncode, 0)
        shim = self.repo / "scripts" / "fleet-burndown.py"
        shim.chmod(0o644)
        r = run("--repo", str(self.repo), "--check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("scripts/fleet-burndown.py (not executable)", r.stdout)
        self.assertEqual(run("--repo", str(self.repo)).returncode, 0)
        self.assertTrue(os.access(shim, os.X_OK))

    def test_every_script_a_command_file_names_is_shimmed_or_the_instances(self):
        """A command file calls `scripts/<name>.py` by bare path from the
        instance repo, so each must be a shim the installer writes executable,
        or one the instance repo carries itself."""
        import re
        sys.path.insert(0, str(HERE))
        import importlib.util
        spec = importlib.util.spec_from_file_location("install", INSTALL)
        install = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(install)
        named = set()
        for f in (HERE.parent / "templates" / ".claude").rglob("*.md"):
            named |= set(re.findall(r"(?<![\w./-])scripts/([\w-]+\.py)", f.read_text()))
        instance = set()
        doc = HERE.parent.parent / "embarch-doc" / "scripts"
        if doc.is_dir():
            instance = {p.name for p in doc.glob("*.py") if p.name not in install.SHIMMED}
        # Named by a command file but run in the framework repo, never the
        # instance: the deployer runs deploy.py there, cron runs the dead man.
        framework_only = {"deploy.py", "fleet-deadman.py"}
        missing = sorted(n for n in named - framework_only
                         if n not in install.SHIMMED and n not in instance)
        self.assertEqual(missing, [], "named by a command file, but neither shimmed nor in embarch-doc/scripts")


if __name__ == "__main__":
    unittest.main()
