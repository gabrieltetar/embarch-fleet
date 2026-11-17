#!/usr/bin/env python3
"""edit-exact.py against scratch files.

    python3 scripts/test_edit_exact.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "edit-exact.py"


def run(path, pairs, *args):
    stdin = pairs if isinstance(pairs, str) else json.dumps(pairs)
    return subprocess.run([sys.executable, str(SCRIPT), str(path), *args],
                          input=stdin, capture_output=True, text=True)


class EditExact(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "drv.c"
        self.path.write_text("#define N 4\nfoo(1);\nbar(1);\nfoo(1);\n")
        self.path.chmod(0o755)

    def tearDown(self):
        self.dir.cleanup()

    def test_applies_every_pair(self):
        r = run(self.path, [{"old": "#define N 4", "new": "#define N 8"},
                            {"old": "bar(1);", "new": "bar(2);"}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.path.read_text(), "#define N 8\nfoo(1);\nbar(2);\nfoo(1);\n")
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o755)

    def test_a_miss_writes_nothing(self):
        r = run(self.path, [{"old": "#define N 4", "new": "#define N 8"},
                            {"old": "baz(1);", "new": "baz(2);"}])
        self.assertEqual(r.returncode, 1)
        self.assertIn("pair 2 matches nothing", r.stderr)
        self.assertIn("#define N 4", self.path.read_text())

    def test_two_matches_refused_unless_all(self):
        r = run(self.path, [{"old": "foo(1);", "new": "foo(2);"}])
        self.assertEqual(r.returncode, 1)
        self.assertIn("matches 2 times", r.stderr)
        r = run(self.path, [{"old": "foo(1);", "new": "foo(2);", "all": True}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.path.read_text().count("foo(2);"), 2)

    def test_overlap_refused(self):
        r = run(self.path, [{"old": "#define N 4\nfoo", "new": "x"},
                            {"old": "foo(1);\nbar", "new": "y"}])
        self.assertEqual(r.returncode, 1)
        self.assertIn("overlap", r.stderr)

    def test_dry_run_prints_diff_and_writes_nothing(self):
        before = self.path.read_text()
        r = run(self.path, [{"old": "bar(1);", "new": "bar(2);"}], "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("-bar(1);", r.stdout)
        self.assertIn("+bar(2);", r.stdout)
        self.assertEqual(self.path.read_text(), before)

    def test_bad_input_is_usage(self):
        self.assertEqual(run(self.path, "not json").returncode, 2)
        self.assertEqual(run(self.path, [{"old": "x"}]).returncode, 2)
        self.assertEqual(run(self.path, []).returncode, 2)
        self.assertEqual(run(Path(self.dir.name) / "none.c", [{"old": "a", "new": "b"}]).returncode, 2)

    def test_crlf_kept(self):
        self.path.write_bytes(b"a\r\nb\r\n")
        r = run(self.path, [{"old": "b", "new": "c"}])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.path.read_bytes(), b"a\r\nc\r\n")


if __name__ == "__main__":
    unittest.main()
