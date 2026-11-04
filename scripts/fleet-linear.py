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
    hide-session ID      keep this window's desk session off the session list

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
3 no `[linear]` table in fleet.toml.
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


class DeskError(Exception):
    """The desk is down, or it or Linear refused the call."""


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


def comment(s: dict, key: str, body: str) -> None:
    call(s, "POST", "/drafts", {"kind": "linear_comment", "issue_key": key, "body": body})


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
        "body": f"{body.rstrip()}\n\nFiled by the fleet ({kind})."})
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
            print(f"from the spool: {create(s, e['kind'], e['project'], e['title'], e['body'])}")
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
    lines = "\n".join(f"- `{p}`" for p in args.paths)
    comment(s, key, f"Split into these task files, and the fleet now holds it:\n\n{lines}")
    move(s, key, s["working"])
    print(f"{key} in {s['working']}, with {len(args.paths)} task path(s) listed")
    return 0


def cmd_send_back(s: dict, args) -> int:
    key = check_key(s, args.key)
    comment(s, key, f"The fleet could not split this, and put it back:\n\n{args.why}")
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
        lines = "\n".join(f"- {c}" for c in closed)
        comment(s, key, f"Every task from this issue has closed:\n\n{lines}")
        move(s, key, s["done"])
        print(f"{key} moved to {s['done']}: {len(closed)} task(s) closed")
        moved += 1
    return 0 if moved else 1


def cmd_file(s: dict, args) -> int:
    body = Path(args.body_file).read_text() if args.body_file else args.body
    try:
        print(create(s, args.kind, args.project, args.title, body))
    except DeskError as e:
        print(f"desk unavailable ({e}); spooled for the next leg: "
              f"{spool(args.kind, args.project, args.title, body, str(e))}")
    return 0


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
    p = sub.add_parser("hide-session")
    p.add_argument("session_id")
    p.set_defaults(fn=cmd_hide_session)
    args = ap.parse_args()
    s = need_settings()
    try:
        return args.fn(s, args)
    except (DeskError, ValueError) as e:
        print(f"fleet-linear: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
