#!/usr/bin/env python3
"""usage-budget.py's 429 reading against scratch transcripts.

    python3 scripts/test_usage_budget.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location("usage_budget", HERE / "usage-budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def record(ago_s, resets_in_s, limit="five_hour", session="s1"):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - ago_s))
    return json.dumps({"error": "rate_limit", "apiErrorStatus": 429, "timestamp": ts,
                       "sessionId": session,
                       "quotaLimits": {"resetsAt": time.time() + resets_in_s, "rateLimitType": limit}})


class List429(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.login = Path(self.tmp.name) / "login"
        proj = self.login / "projects" / "p"
        proj.mkdir(parents=True)
        (proj / "s1.jsonl").write_text(record(600, -60, session="s1") + "\n"
                                       + record(300, 3600, session="s1") + "\n"
                                       + '{"quoted": "rate_limit apiErrorStatus 429"}\n')
        (proj / "s2.jsonl").write_text(record(120, 7200, "seven_day", session="s2") + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_the_listing_and_the_verdict_read_the_same_records(self):
        ub = load()
        ub.TRANSCRIPTS = str(self.login / "projects")
        hits = ub.list_429s(90)
        self.assertEqual(sorted(h["session"] for h in hits), ["s1", "s1", "s2"])
        newest = ub.recent_429_hit(90)
        self.assertEqual(newest["limit"], "seven_day")
        self.assertEqual(newest["when"], max(h["when"] for h in hits))

    def test_list_429_with_login_reads_that_folder(self):
        r = subprocess.run([sys.executable, str(HERE / "usage-budget.py"), "--list-429",
                            "--login", str(self.login)], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(len(lines), 4, r.stdout)
        self.assertIn("spent", lines[0])
        self.assertIn("session s2", lines[2])
        self.assertIn("3 429 record(s)", lines[3])


if __name__ == "__main__":
    unittest.main()
