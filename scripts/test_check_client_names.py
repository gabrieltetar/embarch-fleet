#!/usr/bin/env python3
"""check-client-names.py's `--text-file` mode, against a scratch fleet whose
denylist holds a made-up name."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "Zyxwv Corp"


class TextFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        toml = (HERE.parent / "fleet.toml").read_text()
        (self.root / "fleet.toml").write_text(re.sub(r'^root = ".*"$', f'root = "{self.root}"', toml, flags=re.M))
        (self.root / ".fleet").mkdir()
        (self.root / ".fleet" / "client-names").write_text(NAME + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, text: str, *extra: str) -> subprocess.CompletedProcess:
        path = self.root / "text.md"
        path.write_text(text)
        env = dict(os.environ, EMBARCH_FLEET_CONF=str(self.root / "fleet.toml"))
        return subprocess.run([sys.executable, str(HERE / "check-client-names.py"), "--text-file", str(path), *extra],
                              env=env, capture_output=True, text=True, timeout=60)

    def test_clean_text_passes(self):
        r = self.check("A title\n\nA body naming nobody.\n")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_hit_names_the_line_and_never_the_name(self):
        r = self.check("A title\n\nThe zyxwv-corp board resets.\n")
        self.assertEqual(r.returncode, 1)
        self.assertIn("text:3  denylist entry #1", r.stdout)
        self.assertNotIn("zyxwv", r.stdout.lower())

    def test_a_dark_denylist_refuses(self):
        (self.root / ".fleet" / "client-names").write_text("# nothing\n")
        self.assertEqual(self.check("A title\n").returncode, 2)

    def test_it_reads_no_repo(self):
        self.assertEqual(self.check("A title\n", "--history").returncode, 2)


if __name__ == "__main__":
    unittest.main()
