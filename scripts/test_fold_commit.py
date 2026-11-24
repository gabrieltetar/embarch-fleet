#!/usr/bin/env python3
"""fold-commit.py --prepend-entry against a scratch log, and its refusal of a
retirement that turns check-task-state.py red, against a scratch instance.

    python3 scripts/test_fold_commit.py
"""
import importlib.util
import subprocess
import sys
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


# A stand-in for the instance's rule 7: a blocked task's `Unparks when:` may
# not name a task file that is not in the queue.
STUB_CHECK = '''import re, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent / "tasks"
bad = [p.name for p in root.rglob("*.md")
       if "**State:** blocked" in p.read_text()
       for s, n in re.findall(r"tasks/([a-z]+)/(\\d{3})", p.read_text())
       if not list((root / s).glob(n + "-*.md"))]
print("\\n".join(bad))
sys.exit(1 if bad else 0)
'''


class RetirementGate(unittest.TestCase):
    """EMB-106: a fold retiring a task another task waits on is refused."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fc = load()
        self.doc = Path(self.tmp.name)
        (self.doc / "scripts").mkdir()
        (self.doc / "scripts" / "check-task-state.py").write_text(STUB_CHECK)
        (self.doc / "tasks" / "api").mkdir(parents=True)
        self.task("001-landed", "done")
        self.task("002-parked", "blocked\n\n**Unparks when:** tasks/api/001 lands.")
        for cmd in (["init", "-q"], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(self.doc), *cmd], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, name, state):
        (self.doc / "tasks" / "api" / f"{name}.md").write_text(f"# t\n\n**State:** {state}\n")

    def retire(self):
        _, to_delete, _, _ = self.fc.stage_plan(self.doc, ["tasks/api/001-landed.md"])
        self.assertEqual(to_delete, ["tasks/api/001-landed.md"])
        subprocess.run(["git", "-C", str(self.doc), "rm", "-qf", "--", *to_delete], check=True)
        return to_delete

    def test_a_dependent_park_left_naming_the_retired_task_is_refused(self):
        red = self.fc.red_after_retirement(self.doc, self.retire())
        self.assertIsNotNone(red)
        self.assertIn("002-parked", red)
        self.assertIn("--path", red)

    def test_the_dependent_set_open_in_the_same_fold_passes(self):
        retired = self.retire()
        self.task("002-parked", "open")
        self.assertIsNone(self.fc.red_after_retirement(self.doc, retired))

    def test_a_fold_that_retires_nothing_runs_no_check(self):
        (self.doc / "scripts" / "check-task-state.py").write_text("raise SystemExit(1)")
        self.assertIsNone(self.fc.red_after_retirement(self.doc, []))


class PruneLanded(unittest.TestCase):
    """EMB-240: after the leg's push, every repo's landed agent branches go."""

    def setUp(self):
        import os
        import re
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        toml = (HERE.parent / "fleet.toml").read_text()
        conf = self.root / "fleet.toml"
        toml = re.sub(r'^root = ".*"$', f'root = "{self.root}"', toml, flags=re.M)
        # leg-end archives Linear issues: never reach the real desk from a test.
        toml = re.sub(r'^desk_port = .*$', 'desk_port = 9', toml, flags=re.M)
        toml = re.sub(r'^desk_config_dir = .*$', f'desk_config_dir = "{self.root}/no-desk"', toml, flags=re.M)
        conf.write_text(toml)
        self.env = dict(os.environ, EMBARCH_FLEET_CONF=str(conf))
        self.doc = self.repo("embarch-doc", {"tasks/api/001-landed.md": "# t\n\n**State:** claimed\n",
                                             "tasks/api/002-live.md": "# t\n\n**State:** claimed\n"})
        self.api = self.repo("embarch-api", {"src.rs": "fn a() {}\n"})
        for unit in ("001-landed", "002-live"):
            self.git(self.api, "checkout", "-qb", f"agent/api/{unit}", "main")
            (self.api / f"{unit}.rs").write_text("fn b() {}\n")
            self.git(self.api, "add", "-A")
            self.git(self.api, "commit", "-qm", unit)
            self.git(self.api, "push", "-q", "origin", f"agent/api/{unit}")
            self.git(self.api, "checkout", "-q", "main")
        # Both units' code is on origin/main; only 001's task is retired there.
        self.git(self.api, "merge", "-q", "--ff-only", "agent/api/001-landed")
        self.git(self.api, "merge", "-q", "agent/api/002-live", "-m", "merge 002")
        self.git(self.api, "push", "-q", "origin", "main")
        self.git(self.doc, "rm", "-q", "tasks/api/001-landed.md")
        self.git(self.doc, "commit", "-qm", "Fold api/001")
        self.git(self.doc, "push", "-q", "origin", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, repo, *args):
        return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                              check=True, capture_output=True, text=True).stdout

    def repo(self, name, files):
        bare = self.root / "remotes" / f"{name}.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        path = self.root / name
        subprocess.run(["git", "clone", "-q", str(bare), str(path)], check=True, capture_output=True)
        for rel, text in files.items():
            (path / rel).parent.mkdir(parents=True, exist_ok=True)
            (path / rel).write_text(text)
        self.git(path, "add", "-A")
        self.git(path, "commit", "-qm", "base")
        self.git(path, "push", "-q", "origin", "HEAD:main")
        return path

    def branches(self, *where):
        return self.git(self.api, "for-each-ref", "--format=%(refname:short)", *where).split()

    def test_a_landed_retired_branch_goes_and_a_claimed_one_stays(self):
        r = subprocess.run([sys.executable, str(HERE / "fold-commit.py"), "--prune-landed"],
                           env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.branches("refs/heads/agent/"), ["agent/api/002-live"])
        self.git(self.api, "fetch", "-q", "--prune", "origin")
        self.assertEqual(self.branches("refs/remotes/origin/agent/"), ["origin/agent/api/002-live"])

    def test_leg_end_runs_it(self):
        r = subprocess.run([sys.executable, str(HERE / "fleet-tick.py"), "leg-end"],
                           env=self.env, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.branches("refs/heads/agent/"), ["agent/api/002-live"])


if __name__ == "__main__":
    unittest.main()
