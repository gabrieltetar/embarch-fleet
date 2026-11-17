#!/usr/bin/env python3
"""permission-rules.py against scratch settings files.

    python3 scripts/test_permission_rules.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.checkout, self.login = root / "doc", root / "login"
        (self.checkout / ".claude").mkdir(parents=True)
        self.login.mkdir()
        self.write(self.login / "settings.json",
                   {"permissions": {"allow": ["Bash(git status:*)"], "deny": ["Bash(rm:*)"],
                                    "defaultMode": "auto"}})
        self.write(self.checkout / ".claude" / "settings.json", {"hooks": {}})
        self.write(self.checkout / ".claude" / "settings.local.json",
                   {"permissions": {"allow": ["Bash(python3 scripts/check-docs.py)"],
                                    "defaultMode": "dontAsk"}})

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def write(path, data):
        path.write_text(json.dumps(data))

    def run_it(self, *args):
        return subprocess.run([sys.executable, str(HERE / "permission-rules.py"),
                               "--checkout", str(self.checkout), "--login", str(self.login),
                               *args], capture_output=True, text=True, timeout=30)

    def test_every_rule_carries_the_file_it_came_from(self):
        r = self.run_it("--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["rules"]["allow"],
                         [{"rule": "Bash(python3 scripts/check-docs.py)", "from": "local"},
                          {"rule": "Bash(git status:*)", "from": "user"}])
        self.assertEqual(out["rules"]["deny"], [{"rule": "Bash(rm:*)", "from": "user"}])
        self.assertEqual(out["sources"]["user"], str(self.login / "settings.json"))
        if not Path("/etc/claude-code/managed-settings.json").exists():
            self.assertIsNone(out["sources"]["managed"])

    def test_the_mode_is_the_highest_precedence_file_that_sets_one(self):
        r = self.run_it()
        self.assertIn("mode: dontAsk  (from local)", r.stdout)
        self.assertIn("project  ", r.stdout)
        self.assertIn("0 deny, 0 ask, 0 allow", r.stdout)

    def test_a_broken_file_is_an_error_not_an_empty_list(self):
        (self.login / "settings.json").write_text("{not json")
        r = self.run_it()
        self.assertEqual(r.returncode, 2)
        self.assertIn("not valid JSON", r.stderr)


if __name__ == "__main__":
    unittest.main()
