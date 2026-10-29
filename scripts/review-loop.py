#!/usr/bin/env python3
"""The state of one independent-reviewer loop: rounds, briefs, a findings
ledger, and the rule that stops it.

**Why this exists.** Measured on one field project, 2026-09-09 to 2026-10-20
(`tasks/suite/051`): fresh reviewer agents were **54 % of all review-loop cost
and 30 of 76 active hours** -- 177 of them, ~400 k peak context each, every one
re-reading the whole branch and a free-text "already handled" list that grew
every round. Rounds 4-11 of one loop cost 59 M units for no high finding, the
loop's state lived in `/tmp` and was lost twice to a WSL restart, and the
engineer had to ask whether the rounds were converging. Three things cut that,
and this script holds the mechanical half of each; `/review-loop` is the
procedure that calls it.

- **Delta rounds.** Round 1, and a final round if asked for, read the whole
  branch. Every other round's brief carries `git diff <last reviewed>..<tip>`,
  the functions its hunks sit in, and their call sites, and nothing else.
- **One context pack per loop**, `context.md` beside the ledger: written once
  by the session, read by every reviewer, re-derived by none.
- **A ledger instead of the handled list**, and a stop rule read off it.

**Where it lives.** `<repo>/embarch/review/<loop>/` when git ignores
`embarch/` -- the project's untracked folder -- and otherwise
`<git common dir>/embarch-review/<loop>/`, which is untracked by construction.
Never `/tmp`. A round's snapshot is a `git archive` of the reviewed SHA under
`<repo's parent>/.review-snapshots/`: outside every repo tree, not a worktree,
so nothing registers and nothing needs pruning, and the session can keep
editing while reviewers read a fixed SHA. `end` deletes it.

**The report format** a reviewer ends with, one line per finding:

    FINDING <high|medium|low> <path>:<line> <one-line summary>

or the single line `NO FINDINGS`. Anything else in the report is prose for the
session and is not parsed.

**The ledger** is `ledger.json`: the loop (`repo`, `base`, `cap`), one entry per
round (`n`, `sha`, `mode` full/delta/verify, tokens per reviewer, severity
counts, `decision`), and one row per finding (`id`, `round`, `reviewers`,
`sev`, `path`, `line`, `summary`, `status` open/fixed/rejected/decision, fix
`sha`, `note`). `status` prints it as two tables.

**Dedupe** is per round: a finding on the same path within 3 lines of one
already ingested this round is the same finding -- the reviewer is added to its
row and the higher severity kept. Two distinct bugs three lines apart merge;
the summary of the first is kept and the session sees both reviewers' prose.
Across rounds nothing is merged: a delta round reads code the last one did not,
and a rejected row is handed to the next brief so it is not re-reported.

**The stop rule**, decided by `end` and written into the round:

- `stop: round cap` at the cap (default 6) -- the backstop;
- after **two consecutive rounds with no high or medium finding**:
  `verify` if the last round fixed anything (one reviewer, `round --verify`,
  reading only the fix diff), else `stop`;
- `continue` otherwise.

`end` refuses while a row of the round is still `open`: a finding the session
has not answered is not a round that is over.

Usage:
  review-loop.py init --repo R --base REF [--name N] [--cap 6]   prints the loop dir
  review-loop.py round LOOP [--full | --verify]                 prints the brief
  review-loop.py ingest LOOP --reviewer NAME [--tokens T] < report
  review-loop.py close LOOP ID fixed SHA [note] | rejected [note] | decision [note]
  review-loop.py end LOOP
  review-loop.py status LOOP
"""
from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

SEVS = ("high", "medium", "low")
FINDING = re.compile(r"^\s*FINDING\s+(high|medium|low)\s+(\S+):(\d+)\s+(.+?)\s*$", re.I)
NEAR = 3            # lines: same path this close, same round -> one finding
CALLERS_PER_FN = 8  # call sites listed per touched function in a delta brief


def git(repo: Path, *args: str, check: bool = True) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def home(repo: Path, name: str) -> Path:
    ignored = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", "embarch/"]).returncode == 0
    if ignored:
        return repo / "embarch" / "review" / name
    common = Path(git(repo, "rev-parse", "--git-common-dir").strip())
    return (common if common.is_absolute() else repo / common) / "embarch-review" / name


def load(loop: Path) -> dict:
    return json.loads((loop / "ledger.json").read_text())


def save(loop: Path, led: dict) -> None:
    tmp = loop / "ledger.json.tmp"
    tmp.write_text(json.dumps(led, indent=1) + "\n")
    tmp.replace(loop / "ledger.json")


def snapshot_dir(led: dict, n: int) -> Path:
    repo = Path(led["repo"])
    return repo.parent / ".review-snapshots" / repo.name / led["name"] / f"r{n}"


def cmd_init(a) -> int:
    repo = Path(git(Path(a.repo), "rev-parse", "--show-toplevel").strip())
    name = a.name or re.sub(r"[^A-Za-z0-9._-]+", "-",
                            git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip())
    loop = home(repo, name)
    if (loop / "ledger.json").exists():
        sys.exit(f"a loop already lives at {loop}; use it, or --name another")
    loop.mkdir(parents=True)
    base = git(repo, "rev-parse", a.base).strip()
    save(loop, {"name": name, "repo": str(repo), "base": base, "cap": a.cap,
                "rounds": [], "findings": []})
    (loop / "context.md").write_text(
        "# Context pack\n\nWritten once per loop, read by every reviewer.\n\n"
        "## File map\n\n## Spec sections in scope (extracted text, with page cites)\n\n"
        "## Project rules\n")
    print(loop)
    return 0


def touched(repo: Path, a: str, b: str) -> list[str]:
    """Function names from the hunk headers of a..b -- git's own funcname
    context, so no parser per language. Approximate by design: a reviewer reads
    beyond the brief to confirm a finding, never to find one."""
    names = []
    for line in git(repo, "diff", "-U0", f"{a}..{b}").splitlines():
        m = re.match(r"^@@ [^@]* @@ ?(.*)$", line)
        if m and m.group(1):
            ident = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", m.group(1))
            if ident and ident[-1] not in names:
                names.append(ident[-1])
    return names


def cmd_round(a) -> int:
    loop = Path(a.loop)
    led = load(loop)
    if led["rounds"] and "decision" not in led["rounds"][-1]:
        sys.exit(f"round {led['rounds'][-1]['n']} is not ended; `end` it first")
    repo, n = Path(led["repo"]), len(led["rounds"]) + 1
    sha = git(repo, "rev-parse", "HEAD").strip()
    mode = "full" if (n == 1 or a.full) else ("verify" if a.verify else "delta")
    since = led["base"] if mode == "full" else led["rounds"][-1]["sha"]
    snap = snapshot_dir(led, n)
    if snap.exists():
        shutil.rmtree(snap)
    snap.mkdir(parents=True)
    tar = subprocess.run(["git", "-C", str(repo), "archive", sha], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(snap, filter="data")
    out = [f"# Round {n} -- {mode}", "",
           f"- Read files under `{snap}` only: the tree at `{sha}`. Never the repo's working tree.",
           f"- Context pack: `{loop / 'context.md'}`. Read it first; do not re-derive it.",
           f"- Report format: `FINDING <high|medium|low> <path>:<line> <summary>` per line, or `NO FINDINGS`.", ""]
    if mode == "full":
        out += ["## The whole branch", "", f"Changed since `{since[:12]}`:", "", "```",
                git(repo, "diff", "--stat", f"{since}...{sha}").rstrip(), "```", ""]
    else:
        out += ["## Delta" + (" -- verify these fixes and nothing else" if mode == "verify" else ""), "",
                "Read beyond this only to confirm a finding.", "", "```diff",
                git(repo, "diff", f"{since}..{sha}").rstrip(), "```", ""]
        fns = touched(repo, since, sha)
        if fns:
            out += ["## Touched functions and their call sites", ""]
            for fn in fns:
                sites = git(repo, "grep", "-n", "-w", "-I", f"{fn}", sha, "--", check=False).splitlines()
                sites = [s.split(":", 1)[1] for s in sites][:CALLERS_PER_FN]
                out += [f"- `{fn}`: " + (", ".join(f"`{s.split(':')[0]}:{s.split(':')[1]}`" for s in sites)
                                         or "no other call site")]
            out.append("")
    settled = [f for f in led["findings"] if f["status"] in ("rejected", "decision")]
    if settled:
        out += ["## Already answered -- do not report again", ""]
        out += [f"- {f['id']} {f['status']}: {f['path']}:{f['line']} {f['summary']}"
                + (f" -- {f['note']}" if f.get("note") else "") for f in settled]
    brief = loop / f"round-{n}.md"
    brief.write_text("\n".join(out) + "\n")
    led["rounds"].append({"n": n, "sha": sha, "mode": mode, "tokens": {}})
    save(loop, led)
    print(brief)
    return 0


def ingest(led: dict, reviewer: str, report: str) -> list[str]:
    rnd = led["rounds"][-1]["n"]
    touched_ids = []
    for line in report.splitlines():
        m = FINDING.match(line)
        if not m:
            continue
        sev, path, ln, summary = m.group(1).lower(), m.group(2), int(m.group(3)), m.group(4)
        same = next((f for f in led["findings"] if f["round"] == rnd and f["path"] == path
                     and abs(f["line"] - ln) <= NEAR), None)
        if same:
            if reviewer not in same["reviewers"]:
                same["reviewers"].append(reviewer)
            if SEVS.index(sev) < SEVS.index(same["sev"]):
                same["sev"] = sev
            touched_ids.append(same["id"])
            continue
        fid = f"F{len(led['findings']) + 1}"
        led["findings"].append({"id": fid, "round": rnd, "reviewers": [reviewer], "sev": sev,
                                "path": path, "line": ln, "summary": summary,
                                "status": "open", "sha": "", "note": ""})
        touched_ids.append(fid)
    return touched_ids


def cmd_ingest(a) -> int:
    loop = Path(a.loop)
    led = load(loop)
    if not led["rounds"] or "decision" in led["rounds"][-1]:
        sys.exit("no round is open; `round` first")
    report = sys.stdin.read()
    ids = ingest(led, a.reviewer, report)
    if not ids and "NO FINDINGS" not in report.upper():
        sys.exit(f"{a.reviewer}: no FINDING line and no NO FINDINGS -- not a report this can read")
    led["rounds"][-1]["tokens"][a.reviewer] = a.tokens
    save(loop, led)
    print(f"{a.reviewer}: {len(ids)} finding line(s) -> {', '.join(dict.fromkeys(ids)) or 'none'}")
    return 0


def cmd_close(a) -> int:
    loop = Path(a.loop)
    led = load(loop)
    row = next((f for f in led["findings"] if f["id"] == a.id), None)
    if row is None:
        sys.exit(f"no finding {a.id}")
    rest = list(a.rest)
    if a.status == "fixed":
        if not rest:
            sys.exit("fixed needs the fix SHA")
        row["sha"] = git(Path(led["repo"]), "rev-parse", rest.pop(0)).strip()
    row["status"], row["note"] = a.status, " ".join(rest)
    save(loop, led)
    return 0


def decide(led: dict) -> str:
    rs = led["rounds"]
    cur = rs[-1]
    if cur["n"] >= led["cap"]:
        return "stop: round cap"
    serious = lambda r: r["counts"]["high"] + r["counts"]["medium"]
    if len(rs) >= 2 and serious(rs[-2]) == 0 and serious(cur) == 0:
        fixed = any(f["round"] == cur["n"] and f["status"] == "fixed" for f in led["findings"])
        return ("verify: two rounds clean of high and medium; one verifier on the fix diff"
                if fixed else "stop: two rounds clean of high and medium")
    return "continue"


def cmd_end(a) -> int:
    loop = Path(a.loop)
    led = load(loop)
    cur = led["rounds"][-1] if led["rounds"] else None
    if cur is None or "decision" in cur:
        sys.exit("no round is open")
    rows = [f for f in led["findings"] if f["round"] == cur["n"]]
    left = [f["id"] for f in rows if f["status"] == "open"]
    if left:
        sys.exit(f"round {cur['n']} still has open findings: {', '.join(left)} -- close each first")
    cur["counts"] = {s: sum(1 for f in rows if f["sev"] == s) for s in SEVS}
    if cur["mode"] == "verify":
        # A verifier that finds a high or medium has reopened the loop.
        serious = cur["counts"]["high"] + cur["counts"]["medium"]
        cur["decision"] = "continue" if serious else "stop: verified"
    else:
        cur["decision"] = decide(led)
    save(loop, led)
    shutil.rmtree(snapshot_dir(led, cur["n"]), ignore_errors=True)
    c = cur["counts"]
    print(f"round {cur['n']}: {c['high']} high, {c['medium']} medium, {c['low']} low -> {cur['decision']}")
    return 0


def cmd_status(a) -> int:
    led = load(Path(a.loop))
    print(f"loop {led['name']} on {led['repo']}, base {led['base'][:12]}, cap {led['cap']}\n")
    print("| round | sha | mode | reviewers | tokens | high | medium | low | decision |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in led["rounds"]:
        c = r.get("counts", {})
        tok = sum(t for t in r["tokens"].values() if t)
        print(f"| {r['n']} | {r['sha'][:12]} | {r['mode']} | {len(r['tokens'])} | {tok or '-'} | "
              f"{c.get('high', '-')} | {c.get('medium', '-')} | {c.get('low', '-')} | {r.get('decision', 'open')} |")
    print("\n| id | round | sev | where | status | sha | summary |\n|---|---|---|---|---|---|---|")
    for f in led["findings"]:
        print(f"| {f['id']} | {f['round']} | {f['sev']} | {f['path']}:{f['line']} | {f['status']} | "
              f"{f['sha'][:12]} | {f['summary']} ({', '.join(f['reviewers'])}) |")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("--repo", required=True); p.add_argument("--base", required=True)
    p.add_argument("--name"); p.add_argument("--cap", type=int, default=6); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("round"); p.add_argument("loop")
    g = p.add_mutually_exclusive_group(); g.add_argument("--full", action="store_true")
    g.add_argument("--verify", action="store_true"); p.set_defaults(fn=cmd_round)
    p = sub.add_parser("ingest"); p.add_argument("loop"); p.add_argument("--reviewer", required=True)
    p.add_argument("--tokens", type=int); p.set_defaults(fn=cmd_ingest)
    p = sub.add_parser("close"); p.add_argument("loop"); p.add_argument("id")
    p.add_argument("status", choices=("fixed", "rejected", "decision")); p.add_argument("rest", nargs="*")
    p.set_defaults(fn=cmd_close)
    p = sub.add_parser("end"); p.add_argument("loop"); p.set_defaults(fn=cmd_end)
    p = sub.add_parser("status"); p.add_argument("loop"); p.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
