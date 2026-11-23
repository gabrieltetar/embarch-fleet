#!/usr/bin/env python3
"""review-loop.py's ledger merge and delta brief against a scratch repo.

    python3 scripts/test_review_loop.py
"""
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location("review_loop", HERE / "review-loop.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rl = load()


def ledger():
    return {"rounds": [{"n": 1}], "findings": []}


class Merge(unittest.TestCase):
    """EMB-215: nearness merges code findings, not prose ones."""

    def test_two_near_findings_in_prose_stay_two_rows(self):
        led = ledger()
        rl.ingest(led, "a", "FINDING high notes/design.md:10 the lease outlives its session\n"
                            "FINDING medium notes/design.md:11 step 3 names the wrong owner")
        self.assertEqual(len(led["findings"]), 2)

    def test_the_same_summary_in_prose_merges(self):
        led = ledger()
        rl.ingest(led, "a", "FINDING medium notes/design.md:10 The lease outlives its session.")
        rl.ingest(led, "b", "FINDING high notes/design.md:12 the lease outlives its session")
        self.assertEqual(len(led["findings"]), 1)
        self.assertEqual(led["findings"][0]["reviewers"], ["a", "b"])
        self.assertEqual(led["findings"][0]["sev"], "high")

    def test_two_near_findings_in_code_still_merge(self):
        led = ledger()
        rl.ingest(led, "a", "FINDING low src/lease.rs:10 unchecked return\n"
                            "FINDING high src/lease.rs:12 lock held across await")
        self.assertEqual(len(led["findings"]), 1)
        self.assertEqual(led["findings"][0]["sev"], "high")


class Touched(unittest.TestCase):
    """EMB-215: a delta over prose names no touched functions."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        self.git("init", "-q", "-b", "main")
        (self.repo / "notes.md").write_text("# Notes\n\nIt is on to own the container (here).\n\nend\n")
        (self.repo / "lease.py").write_text("def take(n):\n    a = 1\n    b = 2\n    c = 3\n    return n\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "one")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        self.dir.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              capture_output=True, text=True, check=True).stdout

    def change(self, path, old, new):
        p = self.repo / path
        p.write_text(p.read_text().replace(old, new))
        self.git("commit", "-qam", "two")
        return self.git("rev-parse", "HEAD").strip()

    def test_a_prose_delta_names_no_function(self):
        tip = self.change("notes.md", "end", "the end")
        self.assertEqual(rl.touched(self.repo, self.base, tip), [])

    def test_a_code_delta_names_its_function(self):
        tip = self.change("lease.py", "return n", "return n + 1")
        self.assertEqual(rl.touched(self.repo, self.base, tip), ["take"])


if __name__ == "__main__":
    unittest.main()
