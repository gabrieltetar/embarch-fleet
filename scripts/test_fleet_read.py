#!/usr/bin/env python3
"""fleet-read.py --leg-gate and --dream-check against a scratch origin and a
lagging checkout.

    python3 scripts/test_fleet_read.py
"""
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
TMP = tempfile.TemporaryDirectory()
ROOT = Path(TMP.name)


def git(*args, cwd=None, when=None):
    env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when) if when else None
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=cwd, check=True, capture_output=True, env=env)


def conf() -> Path:
    """fleet.toml rooted in the scratch dir, with no [linear]: no Fleet Ready read."""
    toml = (HERE.parent / "fleet.toml").read_text()
    toml = re.sub(r'^root = ".*"$', f'root = "{ROOT}"', toml, flags=re.M)
    toml = toml[:toml.index("\n[linear]")] + "\n"
    path = ROOT / "fleet.toml"
    path.write_text(toml)
    return path


os.environ["EMBARCH_FLEET_CONF"] = str(conf())


def load():
    spec = importlib.util.spec_from_file_location("fleet_read", HERE / "fleet-read.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


OPEN = "# t\n\n**State:** open\n\n**Hardware:** none\n"


class Scratch(unittest.TestCase):
    """An origin with one open task, the owner's clone of it, and a leg's."""

    def setUp(self):
        for d in ("origin.git", "embarch-doc", "leg"):
            subprocess.run(["rm", "-rf", str(ROOT / d)], check=True)
        git("init", "-q", "--bare", "-b", "main", str(ROOT / "origin.git"))
        git("clone", "-q", str(ROOT / "origin.git"), str(ROOT / "leg"))
        leg = ROOT / "leg"
        (leg / "tasks" / "api").mkdir(parents=True)
        (leg / "tasks" / "api" / "150-last.md").write_text(OPEN)
        (leg / "tasks" / "README.md").write_text("queue\n")
        git("add", "-A", cwd=leg)
        git("commit", "-qm", "one open task", cwd=leg, when=f"@{int(time.time()) - 7200}")
        git("push", "-q", "origin", "HEAD:main", cwd=leg)
        # The owner's checkout, which no leg advances.
        git("clone", "-q", str(ROOT / "origin.git"), str(ROOT / "embarch-doc"))
        self.fr = load()
        self.posts, self.replies = [], []
        self.fr.fs.read_token = lambda: "xoxb-test"
        self.fr.fs.get = lambda token, method, **kw: {
            "ok": True, "messages": self.posts if method == "conversations.history"
            else [{"ts": kw["ts"]}] + self.replies}

    def land_the_last_task(self):
        leg = ROOT / "leg"
        git("rm", "-q", "tasks/api/150-last.md", cwd=leg)
        git("commit", "-qm", "fold api/150", cwd=leg)
        git("push", "-q", "origin", "HEAD:main", cwd=leg)


class LegGate(Scratch):
    """EMB-175: the gate counts origin/main, not the owner's checkout."""

    def gate(self):
        out = StringIO()
        with redirect_stdout(out):
            code = self.fr.leg_gate()
        return code, out.getvalue()

    def test_a_dream_holds_though_the_owner_checkout_still_shows_the_task(self):
        self.land_the_last_task()
        self.posts = [{"ts": f"{time.time() - 60:.6f}",
                       "reactions": [{"name": "crystal_ball", "count": 1}]}]
        self.assertTrue((ROOT / "embarch-doc" / "tasks" / "api" / "150-last.md").exists())
        code, out = self.gate()
        self.assertEqual(code, 1, out)
        self.assertIn("HOLD -- queue empty on origin/main", out)

    def test_the_owner_checkout_is_not_moved(self):
        head = subprocess.run(["git", "-C", str(ROOT / "embarch-doc"), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout
        self.land_the_last_task()
        self.gate()
        self.assertEqual(head, subprocess.run(
            ["git", "-C", str(ROOT / "embarch-doc"), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout)

    def test_an_open_task_on_origin_spawns(self):
        code, out = self.gate()
        self.assertEqual(code, 0, out)
        self.assertIn("SPAWN -- 1 dispatchable on origin/main", out)

    def test_an_empty_queue_with_no_dream_spawns_a_refill(self):
        self.land_the_last_task()
        code, out = self.gate()
        self.assertEqual(code, 0, out)
        self.assertIn("no dream", out)


class DreamCheck(Scratch):
    """EMB-183: an unanswered dream over unchanged sources does not page again."""

    def dream(self, hours_ago=1.0):
        ts = f"{time.time() - hours_ago * 3600:.6f}"
        self.posts = [{"ts": ts, "reactions": [{"name": "crystal_ball", "count": 1}]}]
        return ts

    def check(self):
        out = StringIO()
        with redirect_stdout(out):
            code = self.fr.dream_check()
        return code, out.getvalue()

    def test_unanswered_and_nothing_new_is_quiet(self):
        self.dream()
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("QUIET", out)

    def test_a_commit_on_origin_since_the_dream_asks(self):
        self.dream()
        self.land_the_last_task()
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("1 commit(s) on origin/main", out)

    def log_the_fold(self, ts, subject):
        """fold-commit.py's framework side: `Log <unit>: <instance subject>`,
        its entry carrying the dream's ts."""
        fleet = ROOT / "fleet"
        (fleet / "supervisor-log.md").write_text(f"dreamt, ts `{ts}`\n")
        git("add", "-A", cwd=fleet)
        git("commit", "-qm", f"Log api/150: {subject}", cwd=fleet)

    def own_fold(self):
        fleet = ROOT / "fleet"
        subprocess.run(["rm", "-rf", str(fleet)], check=True)
        git("init", "-q", "-b", "main", str(fleet))
        self.fr.FLEET_REPO = fleet

    def test_the_posting_legs_own_fold_is_quiet(self):
        self.own_fold()
        ts = self.dream(hours_ago=0.01)
        self.land_the_last_task()
        self.log_the_fold(ts, "fold api/150")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("own fold not counted (1)", out)

    def test_a_commit_after_the_posting_legs_own_fold_asks(self):
        self.own_fold()
        ts = self.dream(hours_ago=0.01)
        self.land_the_last_task()
        self.log_the_fold(ts, "fold api/150")
        leg = ROOT / "leg"
        (leg / "open.md").write_text("a new open question\n")
        git("add", "-A", cwd=leg)
        git("commit", "-qm", "doc: open question", cwd=leg)
        git("push", "-q", "origin", "HEAD:main", cwd=leg)
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("1 commit(s) on origin/main", out)

    def test_a_fold_whose_log_names_another_dream_asks(self):
        self.own_fold()
        ts = self.dream(hours_ago=0.01)
        self.land_the_last_task()
        self.log_the_fold(f"{float(ts) - 9:.6f}", "fold api/150")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_an_owner_reply_in_the_thread_asks(self):
        ts = self.dream()
        self.replies = [{"ts": f"{float(ts) + 60:.6f}", "user": self.fr.CONF.owner,
                         "text": "none"}]
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn("owner has spoken", out)

    def test_no_dream_asks(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        TMP.cleanup()
