#!/usr/bin/env python3
"""fold-day.py's ledger keeps the day's newest `Spread sweep: nothing filed`
line through a fold (EMB-209), against a scratch log.

    python3 scripts/test_fold_day.py
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "fold-day.py"

PREAMBLE = """# Supervisor log

---

"""

DAY_WITH_SWEEPS = """## 2026-11-17 19:30 — leg after the dream: no units

**Refill:** swept once. Spread sweep: nothing filed (2026-11-17 19:22).
**Hardware debts:** none.

## 2026-11-17 08:10 — api/007 a-slug

**Merged:** `agent/api/007-a-slug` (code `1a2b3c4`, doc `5d6e7f8`).
**Reviewer:** clean.
**Refill:** Spread sweep: nothing filed (2026-11-17 08:05).
**Hardware debts:** none.

"""

DAY_WITHOUT = """## 2026-11-16 08:10 — api/006 b-slug

**Merged:** `agent/api/006-b-slug` (code `9a8b7c6`, doc `5f4e3d2`).
**Reviewer:** clean.
**Hardware debts:** none.

"""

FOLD_HEAD = "## {date} — 1 units\n\n*Folded by a test.*\n\n**Merged:** `{code}`, `{doc}`.\n**Reviewer:** clean.\n"


def run(*args, log):
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--log", str(log)],
                          capture_output=True, text=True)


class SpreadSweepSurvivesAFold(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = self.tmp / "supervisor-log.md"
        self.log.write_text(PREAMBLE + DAY_WITH_SWEEPS + DAY_WITHOUT)
        # No --out: the extract and its ledger go to <log dir>/.fold/, where --apply looks.
        r = run("2026-11-17", log=self.log)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.extract_out = r.stdout

    def fold(self, body: str) -> subprocess.CompletedProcess:
        f = self.tmp / "folded.md"
        f.write_text(FOLD_HEAD.format(date="2026-11-17", code="1a2b3c4", doc="5d6e7f8") + body)
        return run("2026-11-17", "--apply", str(f), log=self.log)

    def test_the_extract_names_only_the_newest_line(self):
        self.assertIn("Spread sweep: nothing filed (2026-11-17 19:22)", self.extract_out)
        self.assertNotIn("08:05", self.extract_out)

    def test_a_fold_that_drops_it_is_refused_and_the_log_is_unchanged(self):
        before = self.log.read_text()
        r = self.fold("**Refill:** swept twice, nothing filed.\n")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("Spread sweep: nothing filed (2026-11-17 19:22)", r.stdout)
        self.assertEqual(self.log.read_text(), before)

    def test_an_older_sweep_line_alone_does_not_satisfy_it(self):
        r = self.fold("**Refill:** Spread sweep: nothing filed (2026-11-17 08:05).\n")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_a_fold_that_carries_it_rewrapped_is_applied(self):
        r = self.fold("**Refill:** the last one read: Spread sweep: nothing\nfiled (2026-11-17 19:22).\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("## 2026-11-17 — 1 units", self.log.read_text())


class ADayWithNoSweepLineFoldsAsBefore(unittest.TestCase):
    def test_no_line_is_required(self):
        tmp = Path(tempfile.mkdtemp())
        log = tmp / "supervisor-log.md"
        log.write_text(PREAMBLE + DAY_WITHOUT)
        self.assertEqual(run("2026-11-16", log=log).returncode, 0)
        f = tmp / "folded.md"
        f.write_text(FOLD_HEAD.format(date="2026-11-16", code="9a8b7c6", doc="5f4e3d2"))
        r = run("2026-11-16", "--apply", str(f), log=log)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
