#!/usr/bin/env python3
"""fold-commit.py --prepend-entry against a scratch log.

    python3 scripts/test_fold_commit.py
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

LOG = """# Supervisor log

## Entry shape

```markdown
## <yyyy-mm-dd HH:MM> — <scope>/<NNN> <slug>
```

---

## 2026-11-14 23:58 — leg after the dream: no units

**Leg close:** nothing ran.
"""

UNIT = """## 2026-11-17 09:00 — api/007 a-slug

**Decided:** nothing.
**Merged:** api@abc1234.
**Blocked:** none.
**Reviewer:** no findings
**Hardware debts:** none.
**Budget:** 40%.
**Least sure about:** the retry.
"""


def load():
    spec = importlib.util.spec_from_file_location("fold_commit", HERE / "fold-commit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Prepend(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fc = load()
        self.fc.LOG = Path(self.tmp.name) / "supervisor-log.md"
        self.fc.LOG.write_text(LOG)

    def tearDown(self):
        self.tmp.cleanup()

    def test_goes_above_the_newest_entry_and_below_the_shape(self):
        self.assertEqual(self.fc.prepend_entry(UNIT), 0)
        log = self.fc.LOG.read_text()
        self.assertLess(log.index("<scope>/<NNN>"), log.index("api/007"))
        self.assertLess(log.index("api/007"), log.index("leg after the dream"))
        self.assertIn("**Least sure about:** the retry.\n\n---\n\n## 2026-11-14", log)
        self.assertEqual(self.fc.newest_unit_entry()[0], "api/007")

    def test_a_unit_entry_that_breaks_the_shape_writes_nothing(self):
        self.assertEqual(self.fc.prepend_entry(UNIT.replace("**Budget:** 40%.\n", "")), 1)
        self.assertEqual(self.fc.prepend_entry(UNIT.replace("no findings", "pending")), 1)
        self.assertEqual(self.fc.LOG.read_text(), LOG)

    def test_a_leg_close_entry_needs_only_its_heading(self):
        self.assertEqual(self.fc.prepend_entry("## 2026-11-17 10:00 — leg: no units\n\nquiet."), 0)
        self.assertEqual(self.fc.prepend_entry("no heading"), 1)


if __name__ == "__main__":
    unittest.main()
