#!/usr/bin/env python3
"""The fleet's one way to Linear: the desk `fleet.toml`'s `[linear]` names.

Work enters the fleet as a Linear issue the owner, or the fleet itself, puts in
the Fleet Ready status. A leg splits it into task files, this script lists their
paths on the issue, and the issue moves on when the last of them closes. The
queue stays in git, so the claim commit stays the double-dispatch guard.

**Through the desk, on a port read from config, never the agent's own tools.**
The desk holds the Linear token, whichever login the fleet runs on. An agent's
`linear_*` tools reach whichever desk its window's environment names, and the
work desk reads client workspaces, so a listener armed outside the suite would
have read and written those. This script cannot: the port is `fleet.toml`'s, and
every key it is handed must be in the configured team.

    ready [--json]       flush the spool, then the Fleet Ready issues in full
    list                 Fleet Ready issues as a JSON array, for queue-status.py
    filed KEY PATH...    list task files on an issue, move it to Fleet Working
    send-back KEY --why  an issue that cannot be split: say why, back to Backlog
    finish               issues whose tasks have all closed: comment, move to Done
    file --from KIND --project P --title T (--body B | --body-file F)
                         a new issue; KIND sets its status
    rewrite KEY (--body B | --body-file F) [--title T]
                         replace an issue's description, its title too if given
    comment KEY --kind K (--body B | --body-file F) [--reply-to ID]
                         a comment; `---` lines split the body into a thread
    lint [KEY...] [--json]
                         check open issues (or these) against the protocol
    hide-session ID      keep this window's desk session off the session list

**Every body and comment has the shape embarch-doc's `LINEAR-PROTOCOL.md` gives
it.** `file`, `rewrite` and `comment` refuse one that breaks it, naming what is
wrong, with exit 4 and nothing sent; `lint` reports open issues that break it.

**Where a new issue starts is `file_status` in `fleet.toml`.** A worker's or a
reviewer's finding goes straight to Fleet Ready, as those are small and found in
passing. An audit finding or a withheld decision goes to Backlog, for the owner
to mark.

**A filing never fails its caller.** Writing an `inbox/` file could not fail, and
a worker's final report goes astray often enough that it cannot be the fallback.
With the desk down, `file` writes `<state_dir>/linear-spool/` and exits 0, and
the next leg's `ready` files what is there.

Tasks are read from `origin/main`, so a leg's dirty worktree cannot change the
answer: a task file on main is open, and a fold `git rm`s it.

Exit status: 0 done, 1 nothing there, 2 the desk or Linear refused or is down,
3 no `[linear]` table in fleet.toml, 4 a body or comment breaks the protocol.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import quote

REQUEST_TIMEOUT_S = 20
BROKEN = 4


class DeskError(Exception):
    """The desk is down, or it or Linear refused the call."""


class Broken(Exception):
    """A body or comment breaks LINEAR-PROTOCOL.md; each arg is one problem."""


# --- the protocol (embarch-doc/LINEAR-PROTOCOL.md) ---------------------------

# Type: (required sections in order, optional sections), §3's table.
TYPES = {
    "bug": (("What happens", "Expected", "Where"), ("Reproduce", "Why it matters", "Found while")),
    "change": (("Today", "Wanted", "Where"), ("Why", "Found while")),
    "gap": (("What is missing", "Who needs it"), ("Direction", "Where", "Found while")),
    "doc": (("Where", "What it says", "What it should say"), ("Found while",)),
    "decision": (("Question", "Options", "Blocks"), ("Where", "Found while")),
    "investigation": (("Symptom", "Known", "Next check"), ("Hypotheses", "Where", "Found while")),
}
FIELDS = ("Type", "Scope", "Hardware", "Filed by")
HARDWARE = ("none", "verify-only", "bench", "required")
FILERS = ("owner", "session", "worker", "reviewer", "audit", "decision")
KINDS = ("Split", "Sent back", "Closed", "Question", "Answer", "Progress", "Handoff",
         "Blocked", "Changed", "Finding")
DONE_WHEN = "Done when"
TITLE_MAX = 80
SUMMARY_MAX = 400
HEAD_MAX = 600
REPLY_MAX = 1500
FIELD_RE = re.compile(r"^\*\*([A-Za-z ]+):\*\* *(.*?) *$")
HEADER_RE = re.compile(r"^## +(.+?) *$")
# What Linear makes of a bare file name: `[store.rs](<http://store.rs>)`.
AUTOLINK_RE = re.compile(r"\[([^\]\s]+)\]\(<?https?://\1/?>?\)")
HEAD_RE = re.compile(r"^\*\*(" + "|".join(KINDS) + r")\*\* — \S")
# What Linear would make a link of, before it does: a dotted name outside code
# spans, links and URLs (`store.rs`, `claude.ai`, `README.md`).
NOT_PROSE_RE = re.compile(r"```.*?```|`[^`\n]*`|\[[^\]]*\]\([^)]*\)|<https?://[^>]*>|https?://\S+", re.S)
BARE_NAME_RE = re.compile(r"(?<![\w/.@-])(?:[\w-]+/)*[\w-]*[A-Za-z][\w-]*(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")


def scopes() -> set[str]:
    """The worker scopes, as check-ownership.py derives them: embarch-doc's
    `embarch-*` directories on origin/main, plus `doc` and `suite`."""
    out = git("ls-tree", "--name-only", "origin/main").split()
    return {d.removeprefix("embarch-") for d in out if d.startswith("embarch-") and "." not in d} | {"doc", "suite"}


def parse_body(body: str) -> tuple[str, dict[str, str], list[tuple[str, str]]]:
    """(summary, fields, [(section, text)]) as §2 lays a body out. Text between
    the fields and the first section comes back as a section named ''."""
    summary, fields, sections = [], {}, []
    for line in body.strip().splitlines():
        if fields and not sections and line.strip() and not FIELD_RE.match(line) and not HEADER_RE.match(line):
            sections.append(("", ""))
        h = HEADER_RE.match(line)
        if h:
            sections.append((h.group(1), ""))
            continue
        if sections:
            name, text = sections[-1]
            sections[-1] = (name, text + line + "\n")
            continue
        f = FIELD_RE.match(line)
        if f and f.group(1) in FIELDS:
            fields[f.group(1)] = f.group(2)
        elif not fields:
            summary.append(line)
    return "\n".join(summary).strip(), fields, sections


def body_problems(body: str, title: str | None = None, project: str | None = None,
                  known: set[str] | None = None) -> list[str]:
    """Everything in this issue that breaks §2-3, one line each; empty when it fits."""
    out = []
    if title is not None:
        if len(title) > TITLE_MAX:
            out.append(f"the title is {len(title)} characters; the most is {TITLE_MAX}")
        if re.match(r"^\s*(\[[^\]]*\]|[A-Za-z]+:\s)", title):
            out.append("the title carries a prefix; the Project and Type say that")
    summary, fields, sections = parse_body(body)
    if not summary:
        out.append("no summary before the fields")
    elif len(summary) > SUMMARY_MAX:
        out.append(f"the summary is {len(summary)} characters; the most is {SUMMARY_MAX}")
    for f in FIELDS:
        if f not in fields:
            out.append(f"no **{f}:** field")
    typ = fields.get("Type", "")
    if "Type" in fields and typ not in TYPES:
        out.append(f"Type {typ!r} is not one of {', '.join(TYPES)}")
    scope = fields.get("Scope", "")
    if "Scope" in fields and known is not None and scope not in known:
        out.append(f"Scope {scope!r} is not a sub-project; one of {', '.join(sorted(known))}")
    if project and scope and scope not in ("suite", "doc") and project != f"embarch-{scope}":
        out.append(f"Scope {scope!r} but the Project is {project!r}")
    if "Hardware" in fields and fields["Hardware"] not in HARDWARE:
        out.append(f"Hardware {fields['Hardware']!r} is not one of {', '.join(HARDWARE)}")
    if "Filed by" in fields and fields["Filed by"] not in FILERS:
        out.append(f"Filed by {fields['Filed by']!r} is not one of {', '.join(FILERS)}")
    if any(n == "" for n, _ in sections):
        out.append("text between the fields and the first ## section")
        sections = [(n, t) for n, t in sections if n]
    names = [n for n, _ in sections]
    if not names or names[-1] != DONE_WHEN:
        out.append(f"the last section is not ## {DONE_WHEN}")
    elif not re.search(r"^- \[[ x]\] \S", sections[-1][1], re.M):
        out.append(f"## {DONE_WHEN} has no `- [ ]` item")
    if typ in TYPES:
        required, optional = TYPES[typ]
        allowed = set(required) | set(optional) | {DONE_WHEN}
        for n in names:
            if n not in allowed:
                out.append(f"## {n} is not a {typ} section; it takes {', '.join(required + optional)}")
        for n in required:
            if n not in names:
                out.append(f"no ## {n}, which a {typ} needs")
        present = [n for n in names if n in required]
        if present != [n for n in required if n in names]:
            out.append(f"a {typ}'s sections go in this order: {', '.join(required)}")
        for n, text in sections:
            if not text.strip():
                out.append(f"## {n} is empty")
    if len(names) != len(set(names)):
        out.append("a section appears twice")
    for m in AUTOLINK_RE.finditer(body):
        out.append(f"`{m.group(1)}` became a link; put file names in backticks, and name a domain in words")
    for name in dict.fromkeys(m.group(0) for m in BARE_NAME_RE.finditer(NOT_PROSE_RE.sub(" ", body))):
        out.append(f"`{name}` would become a link; put file names in backticks, and name a domain in words")
    return out


def with_filer(body: str, kind: str) -> str:
    """The body with **Filed by:** after its last field, when it has none."""
    summary, fields, _ = parse_body(body)
    if "Filed by" in fields or not fields:
        return body
    lines = body.strip().splitlines()
    last = max(i for i, line in enumerate(lines) if (m := FIELD_RE.match(line)) and m.group(1) in FIELDS)
    return "\n".join(lines[:last + 1] + [f"**Filed by:** {kind}"] + lines[last + 1:]) + "\n"


def thread(kind: str, body: str) -> tuple[str, list[str]]:
    """A comment as §4 shapes it: `**Kind** — ` on the head, `---` lines between
    the head and each reply. Raises Broken naming every part that does not fit."""
    if kind not in KINDS:
        raise Broken(f"kind {kind!r} is not one of {', '.join(KINDS)}")
    parts = [p.strip() for p in re.split(r"^-{3,}\s*$", body.strip(), flags=re.M)]
    problems = []
    if not parts[0]:
        problems.append("the comment is empty")
    head = f"**{kind}** — {parts[0]}"
    if len(head) > HEAD_MAX:
        problems.append(f"the head comment is {len(head)} characters; the most is {HEAD_MAX}: "
                        "move detail below a `---` line")
    for n, r in enumerate(parts[1:], 1):
        if not r:
            problems.append(f"reply {n} is empty")
        elif len(r) > REPLY_MAX:
            problems.append(f"reply {n} is {len(r)} characters; the most is {REPLY_MAX}: split it with `---`")
    if problems:
        raise Broken(*problems)
    return head, parts[1:]


def comment_problems(comments: list) -> list[str]:
    """Top-level comments that do not open with a kind, and replies over size."""
    out = []
    for c in comments:
        if not isinstance(c, dict):
            continue
        body = str(c.get("body") or "")
        at = str(c.get("at") or "")[:16]
        if c.get("parent"):
            if len(body) > REPLY_MAX:
                out.append(f"the reply of {at} is {len(body)} characters; the most is {REPLY_MAX}")
        elif not HEAD_RE.match(body):
            out.append(f"the comment of {at} does not open with **Kind** — ; kinds: {', '.join(KINDS)}")
        elif len(body) > HEAD_MAX:
            out.append(f"the comment of {at} is {len(body)} characters; detail goes in replies under it")
    return out


def lines_thread(kind: str, summary: str, items: list[str]) -> tuple[str, list[str]]:
    """The fleet's own comments: a summary and a list, the list in the head
    when it fits there and in replies under it when it does not."""
    head = f"{summary}\n\n" + "\n".join(items)
    if len(f"**{kind}** — {head}") <= HEAD_MAX:
        return thread(kind, head)
    replies, cur = [], ""
    for item in items:
        if cur and len(cur) + len(item) + 1 > REPLY_MAX:
            replies.append(cur)
            cur = ""
        cur = f"{cur}\n{item}" if cur else item[:REPLY_MAX]
    replies.append(cur)
    return thread(kind, "\n---\n".join([summary, *replies]))


def settings() -> dict | None:
    return CONF.get("linear")


def need_settings() -> dict:
    s = settings()
    if not s:
        print("fleet-linear: fleet.toml has no [linear] table", file=sys.stderr)
        sys.exit(3)
    return s


def call(s: dict, method: str, route: str, body: dict | None = None) -> dict:
    """One call to the configured desk, with its own token."""
    token_path = Path(os.path.expanduser(s["desk_config_dir"])) / "desk-token"
    try:
        token = token_path.read_text().strip()
    except OSError as e:
        raise DeskError(f"cannot read the desk's token: {e}") from e
    url = f"http://127.0.0.1:{int(s['desk_port'])}{route}"
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_S) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise DeskError(f"{method} {route}: {e.code} {e.read().decode(errors='replace')[:400]}") from e
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        raise DeskError(f"{method} {route}: {e}") from e


def check_key(s: dict, key: str) -> str:
    """A key in the configured team, upper-cased; anything else is refused."""
    key = key.strip().upper()
    if not re.fullmatch(rf"{re.escape(s['team'].upper())}-\d+", key):
        raise DeskError(f"{key!r} is not an issue in team {s['team']}")
    return key


def open_rows(s: dict, status: str) -> list[dict]:
    """The team's open issues in one status."""
    prefix = s["team"].upper() + "-"
    v = call(s, "GET", "/linear/open")
    if v.get("truncated"):
        print("fleet-linear: the desk's open-issue list was cut short", file=sys.stderr)
    return [r for r in v.get("issues", [])
            if str(r.get("key", "")).upper().startswith(prefix) and r.get("state") == status]


def comment(s: dict, key: str, head: str, replies: list[str] | None = None,
            reply_to: str | None = None) -> dict:
    """A comment, and its replies as one thread (embarch-desk decision 75)."""
    body = {"kind": "linear_comment", "issue_key": key, "body": head}
    if replies:
        body["replies"] = replies
    if reply_to:
        body["reply_to"] = reply_to
    return call(s, "POST", "/drafts", body)


def move(s: dict, key: str, status: str) -> None:
    call(s, "POST", "/linear/status", {"key": key, "status": status})


def git(*args: str) -> str:
    """git in the doc repo. Empty when git fails, so a bad read files nothing."""
    r = subprocess.run(["git", "-C", str(CONF.doc_repo), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def issue_field(key: str) -> str:
    return rf"^\*\*Issue:\*\* *{re.escape(key)}( |$)"


def tasks_on_main(key: str) -> list[str]:
    """Task files on origin/main that name this issue."""
    out = git("grep", "-lE", issue_field(key), "origin/main", "--", "tasks/")
    paths = [line.split(":", 1)[1] for line in out.splitlines() if ":" in line]
    # tasks/README.md shows the field, and it is no task.
    return [p for p in paths if not p.endswith("/README.md")]


def closed_tasks(key: str) -> list[str]:
    """`<sha> <subject>: <path>` for each task of this issue a commit removed."""
    out = git("log", "origin/main", "--diff-filter=D", "--extended-regexp",
              f"-G{issue_field(key)}", "--format=@%h %s", "--name-only", "--", "tasks/")
    rows, commit = [], ""
    for line in out.splitlines():
        if line.startswith("@"):
            commit = line[1:]
        elif line.strip():
            rows.append(f"{commit}: {line.strip()}")
    return rows


# --- the spool --------------------------------------------------------------

def spool_dir() -> Path:
    return CONF.state_dir / "linear-spool"


def checked(s: dict, kind: str, project: str, title: str, body: str) -> str:
    """The body as it will be filed, its **Filed by:** written from `kind` when
    absent. Raises Broken when it breaks the protocol, before anything is sent."""
    if kind not in s["file_status"]:
        raise ValueError(f"no file_status for {kind!r}; it has {sorted(s['file_status'])}")
    body = with_filer(body, kind)
    problems = body_problems(body, title, project, scopes())
    filer = parse_body(body)[1].get("Filed by")
    if filer and filer != kind:
        problems.append(f"**Filed by:** {filer} but --from {kind}")
    if problems:
        raise Broken(*problems)
    return body


def create(s: dict, kind: str, project: str, title: str, body: str) -> str:
    """Make the issue and put it in its status. Returns a line naming it."""
    status = s["file_status"].get(kind)
    if not status:
        raise ValueError(f"no file_status for {kind!r}; it has {sorted(s['file_status'])}")
    for row in call(s, "POST", "/linear/search", {"query": title}).get("issues", []):
        if row.get("title") == title and row.get("state") not in (s["done"], "Canceled"):
            return f"{row['key']} already open with this title, in {row.get('state')}"
    sent = call(s, "POST", "/drafts", {
        "kind": "linear_issue", "team_key": s["team"], "project": project, "title": title,
        "body": body.rstrip()})
    url = sent.get("url") or ""
    m = re.search(rf"/({re.escape(s['team'].upper())}-\d+)", url)
    if not m:
        raise DeskError(f"the desk did not send it: {json.dumps(sent)[:300]}")
    move(s, m.group(1), status)
    return f"{m.group(1)} in {status}: {url}"


def spool(kind: str, project: str, title: str, body: str, why: str) -> Path:
    d = spool_dir()
    d.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
    path = d / f"{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}-{slug}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"kind": kind, "project": project, "title": title,
                               "body": body, "why": why}, indent=1))
    tmp.replace(path)
    return path


def flush_spool(s: dict) -> None:
    """File what a down desk left behind. A file that keeps failing stays, named."""
    d = spool_dir()
    for path in sorted(d.glob("*.json")) if d.is_dir() else []:
        try:
            e = json.loads(path.read_text())
            body = e["body"]
            # Spooled before LINEAR-PROTOCOL.md: filed as it was, its filer kept
            # the old way, for `lint` to find and a `rewrite` to fix.
            if "Filed by" not in parse_body(body)[1]:
                body = f"{body.rstrip()}\n\nFiled by the fleet ({e['kind']})."
            print(f"from the spool: {create(s, e['kind'], e['project'], e['title'], body)}")
            path.unlink()
        except (DeskError, ValueError, KeyError) as err:
            print(f"still spooled: {path} ({err})", file=sys.stderr)


# --- the commands -----------------------------------------------------------

def cmd_ready(s: dict, args) -> int:
    git("fetch", "-q", "origin")
    flush_spool(s)
    rows = open_rows(s, s["ready"])
    full = []
    for r in rows:
        detail = call(s, "GET", f"/linear/issue/{quote(r['key'])}")
        full.append({"key": r["key"], "title": r["title"], "project": r.get("project"),
                     "url": r.get("url"), "description": detail.get("description") or "",
                     "comments": detail.get("comments") or [], "tasks": tasks_on_main(r["key"])})
    if args.json:
        print(json.dumps(full, indent=1))
        return 0 if full else 1
    if not full:
        print("no Fleet Ready issues")
        return 1
    for i in full:
        print(f"== {i['key']}  {i['title']}  (Project: {i['project']})")
        if i["tasks"]:
            print("   ALREADY SPLIT, do not split again; run `filed` with: " + " ".join(i["tasks"]))
        print(i["description"] or "(no description)")
        for c in i["comments"]:
            print(f"   comment: {c.get('body', c) if isinstance(c, dict) else c}")
        print()
    return 0


def cmd_list(s: dict, _args) -> int:
    print(json.dumps([{k: r.get(k) for k in ("key", "title", "project")}
                      for r in open_rows(s, s["ready"])]))
    return 0


def cmd_filed(s: dict, args) -> int:
    key = check_key(s, args.key)
    n = len(args.paths)
    comment(s, key, *lines_thread("Split", f"the fleet holds this now, as {n} task file{'s' if n != 1 else ''} :",
                                  [f"- `{p}`" for p in args.paths]))
    move(s, key, s["working"])
    print(f"{key} in {s['working']}, with {len(args.paths)} task path(s) listed")
    return 0


def cmd_send_back(s: dict, args) -> int:
    key = check_key(s, args.key)
    comment(s, key, *thread("Sent back", f"the fleet could not split this, so it is back in {s['backlog']} :\n\n"
                                         f"{args.why.strip()}"))
    move(s, key, s["backlog"])
    print(f"{key} back in {s['backlog']}")
    return 0


def cmd_finish(s: dict, _args) -> int:
    git("fetch", "-q", "origin")
    moved = 0
    for r in open_rows(s, s["working"]):
        key = r["key"]
        open_tasks = tasks_on_main(key)
        if open_tasks:
            print(f"{key}: {len(open_tasks)} task(s) still open")
            continue
        closed = closed_tasks(key)
        if not closed:
            # Moved here by hand, or its split never reached main.
            print(f"{key}: in {s['working']} but no task ever named it; left alone")
            continue
        comment(s, key, *lines_thread("Closed", "every task from this issue has closed :",
                                      [f"- {c}" for c in closed]))
        move(s, key, s["done"])
        print(f"{key} moved to {s['done']}: {len(closed)} task(s) closed")
        moved += 1
    return 0 if moved else 1


def body_arg(args) -> str:
    return Path(args.body_file).read_text() if args.body_file else args.body


def cmd_file(s: dict, args) -> int:
    git("fetch", "-q", "origin")
    body = checked(s, args.kind, args.project, args.title, body_arg(args))
    try:
        print(create(s, args.kind, args.project, args.title, body))
    except DeskError as e:
        print(f"desk unavailable ({e}); spooled for the next leg: "
              f"{spool(args.kind, args.project, args.title, body, str(e))}")
    return 0


def cmd_rewrite(s: dict, args) -> int:
    key = check_key(s, args.key)
    git("fetch", "-q", "origin")
    now = call(s, "GET", f"/linear/issue/{quote(key)}")
    title = args.title.strip() if args.title else None
    body = body_arg(args)
    problems = body_problems(body, title or now.get("title"), now.get("project"), scopes())
    if problems:
        raise Broken(*problems)
    sent = call(s, "POST", "/drafts", {"kind": "linear_edit", "issue_key": key, "title": title,
                                       "body": body.rstrip()})
    print(f"{key} rewritten: {sent.get('url') or sent.get('status')}")
    return 0


def cmd_comment(s: dict, args) -> int:
    key = check_key(s, args.key)
    head, replies = thread(args.comment_kind, body_arg(args))
    if args.comment_kind == "Answer" and not args.reply_to:
        raise Broken("an Answer goes in its Question's thread: give --reply-to <the Question's comment id>")
    sent = comment(s, key, head, replies, args.reply_to)
    print(f"{key}: {args.comment_kind}, {1 + len(replies)} comment(s): {sent.get('url') or sent.get('status')}")
    return 0


def cmd_lint(s: dict, args) -> int:
    git("fetch", "-q", "origin")
    keys = [check_key(s, k) for k in args.keys] or [
        r["key"] for r in call(s, "GET", "/linear/open").get("issues", [])
        if str(r.get("key", "")).upper().startswith(s["team"].upper() + "-")]
    known, report = scopes(), []
    for key in keys:
        i = call(s, "GET", f"/linear/issue/{quote(key)}")
        problems = body_problems(i.get("description") or "", i.get("title"), i.get("project"), known)
        problems += comment_problems(i.get("comments") or [])
        report.append({"key": key, "title": i.get("title"), "state": i.get("state"), "problems": problems})
    bad = [r for r in report if r["problems"]]
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        for r in bad:
            print(f"{r['key']}  {r['title']}  ({r['state']})")
            for p in r["problems"]:
                print(f"   - {p}")
        print(f"{len(report) - len(bad)} of {len(report)} issue(s) fit the protocol")
    return BROKEN if bad else 0


def cmd_hide_session(s: dict, args) -> int:
    call(s, "POST", f"/sessions/{quote(args.session_id, safe='')}/assign", {"hidden": True})
    print(f"session {args.session_id} is off the desk's list")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ready")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_ready)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("filed")
    p.add_argument("key")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_filed)
    p = sub.add_parser("send-back")
    p.add_argument("key")
    p.add_argument("--why", required=True)
    p.set_defaults(fn=cmd_send_back)
    sub.add_parser("finish").set_defaults(fn=cmd_finish)
    p = sub.add_parser("file")
    p.add_argument("--from", dest="kind", required=True)
    p.add_argument("--project", required=True, help="the clone's folder name, e.g. embarch-ui")
    p.add_argument("--title", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--body")
    g.add_argument("--body-file")
    p.set_defaults(fn=cmd_file)
    p = sub.add_parser("rewrite")
    p.add_argument("key")
    p.add_argument("--title")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--body")
    g.add_argument("--body-file")
    p.set_defaults(fn=cmd_rewrite)
    p = sub.add_parser("comment")
    p.add_argument("key")
    p.add_argument("--kind", dest="comment_kind", required=True, choices=KINDS)
    p.add_argument("--reply-to", help="the comment id whose thread this joins")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--body")
    g.add_argument("--body-file")
    p.set_defaults(fn=cmd_comment)
    p = sub.add_parser("lint")
    p.add_argument("keys", nargs="*")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("hide-session")
    p.add_argument("session_id")
    p.set_defaults(fn=cmd_hide_session)
    args = ap.parse_args()
    s = need_settings()
    try:
        return args.fn(s, args)
    except Broken as e:
        print("fleet-linear: nothing sent; this breaks embarch-doc/LINEAR-PROTOCOL.md:", file=sys.stderr)
        for p in e.args:
            print(f"  - {p}", file=sys.stderr)
        return BROKEN
    except (DeskError, ValueError) as e:
        print(f"fleet-linear: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
