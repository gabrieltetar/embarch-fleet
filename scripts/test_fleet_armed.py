#!/usr/bin/env python3
"""fleet-armed.py --print against a scratch instance.

    python3 scripts/test_fleet_armed.py
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

BLOCK = """# fleet

Arm it:

> You are the listener.
>
> 1. Run `scripts/fleet-tick.py`.
>    Then read the channel.
"""


class Print(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        toml = (HERE.parent / "fleet.toml").read_text()
        self.conf = root / "fleet.toml"
        self.conf.write_text(re.sub(r'^root = ".*"$', f'root = "{root}"', toml, flags=re.M))
        self.commands = root / "embarch-doc" / ".claude" / "commands"
        self.commands.mkdir(parents=True)
        (self.commands / "fleet.md").write_text(BLOCK)

    def tearDown(self):
        self.tmp.cleanup()

    def armed(self, *args):
        env = dict(os.environ, EMBARCH_FLEET_CONF=str(self.conf), CLAUDE_CONFIG_DIR=self.tmp.name)
        return subprocess.run([sys.executable, str(HERE / "fleet-armed.py"), *args],
                              env=env, capture_output=True, text=True, timeout=30)

    def test_print_is_the_stamp_without_its_quote_marks(self):
        r = self.armed("--print", ".claude/commands/fleet.md")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "You are the listener.\n\n1. Run `scripts/fleet-tick.py`.\n"
                                   "   Then read the channel.\n")
        self.assertEqual(self.armed("--stamp", ".claude/commands/fleet.md").returncode, 0)
        stamp = next(Path(self.tmp.name).rglob("*fleet.md.block")).read_text()
        requoted = "\n".join(f"> {ln}" if ln else ">" for ln in r.stdout.splitlines()) + "\n"
        self.assertEqual(requoted, stamp)

    def test_a_missing_file_or_no_block_fails_on_stderr(self):
        (self.commands / "fleet.md").unlink()
        r = self.armed("--print", ".claude/commands/fleet.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("cannot read", r.stderr)
        (self.commands / "fleet.md").write_text("# fleet\n\nno block here\n")
        r = self.armed("--print", ".claude/commands/fleet.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no `>` block", r.stderr)
        self.assertEqual(r.stdout, "")


if __name__ == "__main__":
    unittest.main()
