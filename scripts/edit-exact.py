#!/usr/bin/env python3
"""Apply several exact-string replacements to one file, all or none.

    edit-exact.py PATH [--dry-run] < pairs.json

`pairs.json` is a JSON list of `{"old": "...", "new": "..."}`. Each `old` must
occur exactly once in the file as it is on disk, or the pair may say
`"all": true` to replace every occurrence (at least one). The pairs must not
overlap. Nothing is written unless every pair matches; `--dry-run` prints the
unified diff and writes nothing.

**Why it exists** (owner's call, 2026-11-17, EMB-99 and its eleven twins).
Claude Code's Edit tool makes one replacement per call and needs the file Read
first, so an agent with six to fifteen known replacements in a file it has not
read writes the same throwaway Python every time: read, check each passage
occurs once, replace, write. This is that script, once, so the throwaway-Python
hook can point at it instead of asking for an issue.

A heredoc keeps the JSON out of shell quoting:

    python3 edit-exact.py src/drv.c <<'EOF'
    [{"old": "#define N 4", "new": "#define N 8"},
     {"old": "foo(1);", "new": "foo(2);"}]
    EOF

Exit status: 0 written (or the dry run's diff printed), 1 a pair matched zero
or several times, or two pairs overlap (each named, nothing written), 2 usage:
a missing file, input that is not a list of pairs.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import tempfile
from pathlib import Path


class Usage(Exception):
    """The input is not what this script takes."""


def load_pairs(text: str) -> list[dict]:
    try:
        pairs = json.loads(text)
    except ValueError as e:
        raise Usage(f"stdin is not JSON: {e}") from None
    if not isinstance(pairs, list) or not pairs:
        raise Usage("stdin must be a non-empty JSON list of {\"old\", \"new\"} objects")
    for n, p in enumerate(pairs, 1):
        if not isinstance(p, dict) or not isinstance(p.get("old"), str) or not isinstance(p.get("new"), str):
            raise Usage(f"pair {n} needs string \"old\" and \"new\"")
        if not p["old"]:
            raise Usage(f"pair {n} has an empty \"old\"")
        unknown = set(p) - {"old", "new", "all"}
        if unknown:
            raise Usage(f"pair {n} has unknown keys: {', '.join(sorted(unknown))}")
    return pairs


def spans(text: str, old: str) -> list[int]:
    out, at = [], text.find(old)
    while at != -1:
        out.append(at)
        at = text.find(old, at + len(old))
    return out


def plan(text: str, pairs: list[dict]) -> tuple[list[tuple[int, int, str]], list[str]]:
    """([(start, end, new)] sorted, problems). Problems name each pair by number
    and its first line, so a refusal says which passage to fix."""
    edits, problems = [], []
    for n, p in enumerate(pairs, 1):
        first = p["old"].splitlines()[0][:60] if p["old"].strip() else repr(p["old"])
        hits = spans(text, p["old"])
        if not hits:
            problems.append(f"pair {n} matches nothing: {first!r}")
        elif len(hits) > 1 and not p.get("all"):
            problems.append(f"pair {n} matches {len(hits)} times; give more context or \"all\": true: {first!r}")
        else:
            edits += [(h, h + len(p["old"]), p["new"], n) for h in hits]
    edits.sort()
    for a, b in zip(edits, edits[1:]):
        if b[0] < a[1]:
            problems.append(f"pairs {a[3]} and {b[3]} overlap")
    return [(s, e, new) for s, e, new, _ in edits], problems


def apply(text: str, edits: list[tuple[int, int, str]]) -> str:
    out, at = [], 0
    for s, e, new in edits:
        out += [text[at:s], new]
        at = e
    out.append(text[at:])
    return "".join(out)


def write_atomic(path: Path, text: str) -> None:
    mode = path.stat().st_mode
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path")
    ap.add_argument("--dry-run", action="store_true", help="print the diff, write nothing")
    args = ap.parse_args(argv)
    path = Path(args.path)
    try:
        if not path.is_file():
            raise Usage(f"{path}: no such file")
        pairs = load_pairs(sys.stdin.read())
    except Usage as e:
        print(f"edit-exact: {e}", file=sys.stderr)
        return 2
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    edits, problems = plan(text, pairs)
    if problems:
        print(f"edit-exact: nothing written to {path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    new = apply(text, edits)
    if args.dry_run:
        sys.stdout.writelines(difflib.unified_diff(
            text.splitlines(keepends=True), new.splitlines(keepends=True), str(path), str(path)))
        return 0
    write_atomic(path, new)
    print(f"{path}: {len(edits)} replacement(s) from {len(pairs)} pair(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
