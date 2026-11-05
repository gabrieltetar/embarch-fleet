#!/usr/bin/env python3
"""fleet-linear.py and queue-status.py against a stand-in desk and a scratch queue.

    python3 scripts/test_fleet_linear.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent

# A body that fits embarch-doc's LINEAR-PROTOCOL.md, which `file` now requires.
VALID = """The Tabs list drops a tab whose manifest has no icon, and says nothing :

**Type:** bug
**Scope:** ui
**Hardware:** none

## What happens
`embarch-ui` skips the tab with no log line.

## Expected
A refused tab is named in the log.

## Where
- `embarch-ui/src/tabs.rs` `load` — skips it

## Done when

- [ ] A manifest without `icon` logs its tab's name.
"""
# The same, as it reads once filed: `file` writes the filer, `rewrite` and `lint` need it.
FILED = VALID.replace("**Hardware:** none", "**Hardware:** none\n**Filed by:** worker")


def load_script():
    """fleet-linear.py's functions, for the checks that need no desk."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("fleet_linear", HERE / "fleet-linear.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Desk:
    """Holds issues and records what it was told, as the dev desk's routes do."""

    def __init__(self):
        self.issues = {}
        self.calls = []
        self.next_id = 100
        desk = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def reply(self, value, code=200):
                data = json.dumps(value).encode()
                self.send_response(code)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if self.path == "/linear/open":
                    return self.reply({"issues": list(desk.issues.values()), "truncated": False})
                key = self.path.rsplit("/", 1)[1]
                self.reply({"description": f"body of {key}", "comments": [], **desk.issues[key]})

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                desk.calls.append((self.path, body))
                if self.headers["Authorization"] != "Bearer tok":
                    return self.reply({"error": "token"}, 401)
                if self.path == "/linear/search":
                    return self.reply({"issues": [i for i in desk.issues.values() if body["query"] in i["title"]]})
                if self.path == "/linear/status":
                    desk.issues[body["key"]]["state"] = body["status"]
                    return self.reply({"ok": True})
                if self.path == "/drafts" and body["kind"] == "linear_issue":
                    desk.next_id += 1
                    key = f"EMB-{desk.next_id}"
                    desk.issues[key] = {"key": key, "title": body["title"], "state": "Backlog", "project": body["project"]}
                    return self.reply({"status": "sent", "url": f"https://linear.app/x/issue/{key}/slug"})
                self.reply({"status": "sent"})

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_port
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def issue(self, key, state, title="A title", project="embarch-ui"):
        self.issues[key] = {"key": key, "title": title, "state": state, "project": project}

    def said(self, route, field="body"):
        return [b.get(field) for p, b in self.calls if p == route]


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class Fleet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.desk = Desk()
        self.addCleanup(self.desk.server.shutdown)
        (root / "cfg").mkdir()
        (root / "cfg" / "desk-token").write_text("tok\n")
        toml = (HERE.parent / "fleet.toml").read_text()
        toml = re.sub(r'^root = ".*"$', f'root = "{root}"', toml, flags=re.M)
        toml = re.sub(r"^desk_port = \d+$", f"desk_port = {self.desk.port}", toml, flags=re.M)
        toml = re.sub(r'^desk_config_dir = ".*"$', f'desk_config_dir = "{root}/cfg"', toml, flags=re.M)
        self.conf = root / "fleet.toml"
        self.conf.write_text(toml)
        self.doc = root / "embarch-doc"
        bare = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        subprocess.run(["git", "clone", "-q", str(bare), str(self.doc)], check=True, capture_output=True)
        git(self.doc, "config", "user.email", "t@example.com")
        git(self.doc, "config", "user.name", "t")
        (self.doc / "tasks" / "ui").mkdir(parents=True)
        (self.doc / "tasks" / "README.md").write_text("# tasks\n")
        # A sub-project directory, so `ui` is a scope as it is in embarch-doc.
        (self.doc / "embarch-ui").mkdir()
        (self.doc / "embarch-ui" / "spec.md").write_text("# ui\n")
        self.commit("start")
        self.state = root / ".fleet" / "linear-spool"

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, message):
        git(self.doc, "add", "-A")
        git(self.doc, "commit", "-qm", message)
        git(self.doc, "push", "-q", "origin", "HEAD:main")

    def task(self, name, issue):
        (self.doc / "tasks" / "ui" / name).write_text(
            f"# 001 — t\n\n**State:** open\n**Source:** s\n**Issue:** {issue}\n**Scope:** ui\n**Hardware:** none\n")

    def run_script(self, script, *args):
        env = dict(os.environ, EMBARCH_FLEET_CONF=str(self.conf))
        return subprocess.run([sys.executable, str(HERE / script), *args], env=env,
                              capture_output=True, text=True, timeout=60, cwd=self.doc)

    def linear(self, *args):
        return self.run_script("fleet-linear.py", *args)

    def test_list_keeps_the_team_and_the_status(self):
        self.desk.issue("EMB-1", "Fleet Ready")
        self.desk.issue("EMB-2", "Backlog")
        self.desk.issue("CLIENT-3", "Fleet Ready")
        self.assertEqual([i["key"] for i in json.loads(self.linear("list").stdout)], ["EMB-1"])

    def test_a_key_outside_the_team_is_refused_before_any_write(self):
        r = self.linear("filed", "CLIENT-3", "tasks/ui/001-a.md")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.desk.calls, [])

    def test_filed_lists_the_paths_and_moves_it(self):
        self.desk.issue("EMB-1", "Fleet Ready")
        self.assertEqual(self.linear("filed", "emb-1", "tasks/ui/001-a.md").returncode, 0)
        self.assertIn("tasks/ui/001-a.md", self.desk.said("/drafts")[0])
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Fleet Working")

    def test_ready_says_when_a_killed_leg_already_split_it(self):
        self.desk.issue("EMB-1", "Fleet Ready")
        self.assertNotIn("ALREADY SPLIT", self.linear("ready").stdout)
        self.task("001-a.md", "EMB-1")
        self.commit("split")
        out = self.linear("ready").stdout
        self.assertIn("ALREADY SPLIT", out)
        self.assertIn("tasks/ui/001-a.md", out)

    def test_ready_with_nothing_there_exits_1(self):
        self.assertEqual(self.linear("ready").returncode, 1)

    def test_an_issue_prefix_is_not_its_neighbour(self):
        self.desk.issue("EMB-1", "Fleet Working")
        self.task("001-a.md", "EMB-12")
        self.commit("the other issue's task")
        r = self.linear("finish")
        self.assertIn("no task ever named it", r.stdout)
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Fleet Working")

    def test_the_tasks_readme_showing_the_field_is_no_task(self):
        self.desk.issue("EMB-1", "Fleet Working")
        (self.doc / "tasks" / "README.md").write_text("**Issue:** EMB-1\n")
        self.task("001-a.md", "EMB-1")
        self.commit("split")
        (self.doc / "tasks" / "ui" / "001-a.md").unlink()
        self.commit("Fold ui/001")
        self.assertEqual(self.linear("finish").returncode, 0)
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Done")

    def test_finish_waits_for_the_last_task_then_moves_to_done(self):
        self.desk.issue("EMB-1", "Fleet Working")
        self.task("001-a.md", "EMB-1")
        self.task("002-b.md", "EMB-1")
        self.commit("split")
        (self.doc / "tasks" / "ui" / "001-a.md").unlink()
        self.commit("Fold ui/001")
        self.assertEqual(self.linear("finish").returncode, 1)
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Fleet Working")
        (self.doc / "tasks" / "ui" / "002-b.md").unlink()
        self.commit("Fold ui/002")
        self.assertEqual(self.linear("finish").returncode, 0)
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Done")
        said = self.desk.said("/drafts")[-1]
        for want in ("Fold ui/001", "Fold ui/002", "tasks/ui/001-a.md", "tasks/ui/002-b.md"):
            self.assertIn(want, said)

    def test_where_a_filed_issue_starts_follows_who_filed_it(self):
        for kind, want in (("worker", "Fleet Ready"), ("reviewer", "Fleet Ready"),
                           ("audit", "Backlog"), ("decision", "Backlog")):
            r = self.linear("file", "--from", kind, "--project", "embarch-ui",
                            "--title", f"from {kind}", "--body", VALID)
            self.assertEqual(r.returncode, 0, r.stderr)
            row = next(i for i in self.desk.issues.values() if i["title"] == f"from {kind}")
            self.assertEqual(row["state"], want)
            self.assertEqual(row["project"], "embarch-ui")

    def test_the_same_title_is_not_filed_twice(self):
        self.desk.issue("EMB-1", "Backlog", title="Same")
        out = self.linear("file", "--from", "worker", "--project", "embarch-ui", "--title", "Same", "--body", VALID).stdout
        self.assertIn("EMB-1 already open", out)
        self.assertEqual(self.desk.said("/drafts"), [])

    def test_a_down_desk_spools_and_the_next_ready_files_it(self):
        real = self.conf.read_text()
        self.conf.write_text(re.sub(r"^desk_port = \d+$", "desk_port = 9", real, flags=re.M))
        r = self.linear("file", "--from", "worker", "--project", "embarch-ui", "--title", "Kept", "--body", VALID)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("spooled", r.stdout)
        self.assertEqual(len(list(self.state.glob("*.json"))), 1)
        self.conf.write_text(real)
        self.linear("ready")
        self.assertEqual(list(self.state.glob("*.json")), [])
        self.assertTrue(any(i["title"] == "Kept" and i["state"] == "Fleet Ready" for i in self.desk.issues.values()))

    def test_a_body_that_breaks_the_protocol_is_refused_and_nothing_sent(self):
        r = self.linear("file", "--from", "worker", "--project", "embarch-ui", "--title", "T", "--body", "x")
        self.assertEqual(r.returncode, 4)
        for want in ("no **Type:** field", "the last section is not ## Done when"):
            self.assertIn(want, r.stderr)
        self.assertEqual(self.desk.calls, [], "refused before the duplicate search, and nothing spooled")
        self.assertFalse(self.state.exists() and list(self.state.glob("*.json")))

    def test_file_writes_the_filer_and_refuses_one_that_contradicts_it(self):
        self.assertEqual(self.linear("file", "--from", "worker", "--project", "embarch-ui",
                                     "--title", "T", "--body", VALID).returncode, 0)
        sent = self.desk.said("/drafts")[0]
        self.assertIn("**Hardware:** none\n**Filed by:** worker\n", sent)
        self.assertNotIn("Filed by the fleet", sent)
        owned = VALID.replace("**Hardware:** none", "**Hardware:** none\n**Filed by:** owner")
        r = self.linear("file", "--from", "worker", "--project", "embarch-ui", "--title", "U", "--body", owned)
        self.assertEqual(r.returncode, 4)
        self.assertIn("**Filed by:** owner but --from worker", r.stderr)
        r = self.linear("file", "--from", "worker", "--project", "embarch-desk", "--title", "V", "--body", VALID)
        self.assertIn("Scope 'ui' but the Project is 'embarch-desk'", r.stderr)

    def test_rewrite_sends_an_edit_and_refuses_a_broken_body(self):
        self.desk.issue("EMB-1", "Backlog")
        self.assertEqual(self.linear("rewrite", "emb-1", "--body", "x").returncode, 4)
        self.assertEqual(self.desk.said("/drafts"), [])
        r = self.linear("rewrite", "EMB-1", "--body", FILED, "--title", "New title")
        self.assertEqual(r.returncode, 0, r.stderr)
        sent = [b for p, b in self.desk.calls if p == "/drafts"][0]
        self.assertEqual((sent["kind"], sent["issue_key"], sent["title"]), ("linear_edit", "EMB-1", "New title"))
        self.assertEqual(sent["body"], FILED.rstrip())

    def test_comment_splits_into_a_thread_and_an_answer_needs_its_question(self):
        self.desk.issue("EMB-1", "Backlog")
        r = self.linear("comment", "EMB-1", "--kind", "Question", "--body", "which one ?\n---\nthe detail")
        self.assertEqual(r.returncode, 0, r.stderr)
        sent = [b for p, b in self.desk.calls if p == "/drafts"][0]
        self.assertEqual((sent["body"], sent["replies"]), ("**Question** — which one ?", ["the detail"]))
        self.assertEqual(self.linear("comment", "EMB-1", "--kind", "Answer", "--body", "this").returncode, 4)
        r = self.linear("comment", "EMB-1", "--kind", "Answer", "--reply-to", "c1", "--body", "this one")
        self.assertEqual([b for p, b in self.desk.calls if p == "/drafts"][-1]["reply_to"], "c1")
        r = self.linear("comment", "EMB-1", "--kind", "Progress", "--body", "y" * 700)
        self.assertEqual(r.returncode, 4)
        self.assertIn("move detail below a `---` line", r.stderr)
        self.assertEqual(self.linear("comment", "EMB-1", "--kind", "Hello", "--body", "x").returncode, 2)

    def test_the_fleets_comments_open_with_their_kind_and_a_long_list_is_a_thread(self):
        self.desk.issue("EMB-1", "Fleet Ready")
        paths = [f"tasks/ui/{n:03}-a-fairly-long-task-file-name-for-the-test.md" for n in range(40)]
        self.assertEqual(self.linear("filed", "EMB-1", *paths).returncode, 0)
        sent = [b for p, b in self.desk.calls if p == "/drafts"][0]
        self.assertTrue(sent["body"].startswith("**Split** — the fleet holds this now, as 40 task files :"))
        self.assertLessEqual(len(sent["body"]), 600)
        self.assertTrue(all(len(r) <= 1500 for r in sent["replies"]))
        self.assertEqual("\n".join(sent["replies"]).count("tasks/ui/"), 40, "every path, once")
        self.assertEqual(self.desk.issues["EMB-1"]["state"], "Fleet Working")

    def test_lint_names_what_breaks_and_exits_4(self):
        self.desk.issue("EMB-1", "Backlog")
        self.desk.issues["EMB-1"]["description"] = FILED
        self.desk.issue("EMB-2", "Backlog", title="[ui] Bug: a prefix")
        r = self.linear("lint")
        self.assertEqual(r.returncode, 4)
        self.assertIn("1 of 2 issue(s) fit", r.stdout)
        self.assertIn("EMB-2", r.stdout)
        self.assertIn("the title carries a prefix", r.stdout)
        self.assertNotIn("EMB-1 ", r.stdout)
        self.assertEqual(self.linear("lint", "EMB-1").returncode, 0)

    def test_a_body_spooled_before_the_protocol_is_still_filed_with_its_filer(self):
        self.state.mkdir(parents=True)
        (self.state / "20261101-000000-1-old.json").write_text(json.dumps(
            {"kind": "worker", "project": "embarch-ui", "title": "Old", "body": "x", "why": "down"}))
        self.linear("ready")
        self.assertEqual(list(self.state.glob("*.json")), [])
        self.assertIn("x\n\nFiled by the fleet (worker).", self.desk.said("/drafts")[0])

    def test_hide_session_asks_the_desk_to_hide_it(self):
        self.assertEqual(self.linear("hide-session", "abc").returncode, 0)
        self.assertEqual(self.desk.calls, [("/sessions/abc/assign", {"hidden": True})])

    def test_queue_status_counts_an_issue_and_tasks_only_does_not(self):
        self.desk.issue("EMB-1", "Fleet Ready")
        v = json.loads(self.run_script("queue-status.py", "--json", "--no-supervisor", "--root", str(self.doc)).stdout)
        self.assertEqual((v["dispatchable"], v["issues"][0]["key"], v["issues_error"]), (1, "EMB-1", None))
        r = self.run_script("queue-status.py", "--count", "--tasks-only", "--no-supervisor", "--root", str(self.doc))
        self.assertEqual(r.stdout.strip(), "0")

    def test_queue_status_with_a_down_desk_says_so_and_still_counts_tasks(self):
        self.conf.write_text(re.sub(r"^desk_port = \d+$", "desk_port = 9", self.conf.read_text(), flags=re.M))
        r = self.run_script("queue-status.py", "--json", "--no-supervisor", "--root", str(self.doc))
        v = json.loads(r.stdout)
        self.assertEqual(v["dispatchable"], 0)
        self.assertIn("/linear/open", v["issues_error"])
        self.assertIn("cannot read Fleet Ready", r.stderr)


class Protocol(unittest.TestCase):
    """LINEAR-PROTOCOL.md's shapes, checked without a desk."""

    @classmethod
    def setUpClass(cls):
        cls.fl = load_script()

    def problems(self, body, title="A title", project="embarch-ui"):
        return self.fl.body_problems(body, title, project, {"ui", "doc", "suite"})

    def test_the_valid_body_fits(self):
        self.assertEqual(self.problems(FILED), [])

    def test_each_type_needs_its_own_sections_in_order(self):
        decision = VALID.replace("**Type:** bug", "**Type:** decision")
        p = self.problems(decision)
        self.assertIn("no ## Question, which a decision needs", p)
        self.assertIn("## What happens is not a decision section; it takes Question, Options, Blocks, Found while", p)
        swapped = VALID.replace("## What happens", "## TMP").replace("## Expected", "## What happens").replace("## TMP", "## Expected")
        self.assertIn("a bug's sections go in this order: What happens, Expected, Where", self.problems(swapped))
        self.assertIn("## Expected is empty", self.problems(VALID.replace("A refused tab is named in the log.", "")))

    def test_the_fields_take_only_their_values(self):
        p = self.problems(VALID.replace("**Type:** bug", "**Type:** feature").replace("**Hardware:** none", "**Hardware:** maybe")
                          .replace("**Scope:** ui", "**Scope:** nope"))
        self.assertTrue(any(x.startswith("Type 'feature' is not one of") for x in p), p)
        self.assertTrue(any(x.startswith("Hardware 'maybe' is not one of") for x in p), p)
        self.assertTrue(any(x.startswith("Scope 'nope' is not a sub-project") for x in p), p)

    def test_the_summary_title_and_linear_autolinks_are_checked(self):
        self.assertIn("no summary before the fields", self.problems(VALID.split("\n", 2)[2]))
        self.assertIn("the summary is 450 characters; the most is 400", self.problems("y" * 450 + VALID[VALID.index("\n\n"):]))
        self.assertIn("the title carries a prefix; the Project and Type say that", self.problems(VALID, title="Bug: x"))
        self.assertIn("the title is 81 characters; the most is 80", self.problems(VALID, title="t" * 81))
        linked = VALID.replace("`embarch-ui/src/tabs.rs`", "[tabs.rs](<http://tabs.rs>)")
        self.assertIn("`tabs.rs` became a link; put file names in backticks", self.problems(linked))
        stray = VALID.replace("\n## What happens", "\nan aside\n\n## What happens")
        self.assertIn("text between the fields and the first ## section", self.problems(stray))
        self.assertIn("## Done when has no `- [ ]` item", self.problems(VALID.replace("- [ ] A manifest", "A manifest")))

    def test_comments_open_with_a_kind_and_replies_need_none(self):
        ok = {"body": "**Progress** — two of three landed", "at": "2026-11-05T10:00"}
        reply = {"body": "detail", "parent": "c1", "at": "2026-11-05T10:01"}
        bare = {"body": "Split into these task files", "at": "2026-11-04T22:56"}
        self.assertEqual(self.fl.comment_problems([ok, reply]), [])
        self.assertEqual(len(self.fl.comment_problems([bare])), 1)


if __name__ == "__main__":
    unittest.main()
