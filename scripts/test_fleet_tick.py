#!/usr/bin/env python3
"""fleet-tick.py's leg lock against a scratch state dir.

    python3 scripts/test_fleet_tick.py
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class LegEnd(unittest.TestCase):
    """EMB-107: a leg waiting on its workers keeps its lock."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        toml = (HERE.parent / "fleet.toml").read_text()
        self.conf = root / "fleet.toml"
        toml = re.sub(r'^root = ".*"$', f'root = "{root}"', toml, flags=re.M)
        # leg-end archives Linear issues: never reach the real desk from a test.
        toml = re.sub(r'^desk_port = .*$', 'desk_port = 9', toml, flags=re.M)
        toml = re.sub(r'^desk_config_dir = .*$', f'desk_config_dir = "{root}/no-desk"', toml, flags=re.M)
        self.conf.write_text(toml)
        self.state = Path(re.search(r'^state_dir = "(.*)"$', toml, re.M).group(1))
        self.state = root / self.state

    def tearDown(self):
        self.tmp.cleanup()

    def tick(self, *args):
        env = dict(os.environ, EMBARCH_FLEET_CONF=str(self.conf))
        return subprocess.run([sys.executable, str(HERE / "fleet-tick.py"), *args],
                              env=env, capture_output=True, text=True, timeout=30)

    def test_leg_end_keeps_the_lock_while_a_dispatch_has_no_report(self):
        self.assertEqual(self.tick("leg-start").returncode, 0)
        self.tick("leg-dispatch")
        self.tick("leg-dispatch")
        self.tick("leg-reported")
        r = self.tick("leg-end")
        self.assertEqual(r.returncode, 1)
        self.assertIn("1 dispatched worker(s) have not reported", r.stdout)
        self.assertTrue((self.state / "leg").exists())
        self.tick("leg-reported")
        self.assertEqual(self.tick("leg-end").returncode, 0)
        self.assertFalse((self.state / "leg").exists())

    def test_only_dispatches_since_the_newest_leg_start_count(self):
        self.tick("leg-start")
        self.tick("leg-dispatch")
        (self.state / "leg").unlink()  # that leg died; its lock went stale
        self.assertEqual(self.tick("leg-start").returncode, 0)
        self.assertEqual(self.tick("leg-end").returncode, 0)

    def test_a_leg_that_dispatched_nothing_ends_at_once(self):
        self.tick("leg-start")
        self.tick("leg-fold")
        self.assertEqual(self.tick("leg-end").returncode, 0)


if __name__ == "__main__":
    unittest.main()
