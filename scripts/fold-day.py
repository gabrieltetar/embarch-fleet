#!/usr/bin/env python3
r"""Fold a day of supervisor-log entries into one, and roll old days out.

protocol.md §11 owes two things and had a mechanism for neither.

**The fold.** On its first unit after local midnight a supervisor collapses the
previous day's per-unit entries into one dated entry. Leg 009 skipped it and the
file reached 84 KB; leg 010 made it by hand and it cost ~35 K tokens of context,
because the obvious mechanism -- an ad-hoc `python3 <script>` -- was refused by
the permission classifier, leaving `Read` the whole file and `Write` it back. A
fold that re-emits ~34 KB of text nobody meant to change can silently corrupt the
relay's own handoff, and "verify it afterwards with a diff" is a save, not a
mechanism.

So this is two commands, and the split is the point:

    fold-day.py <yyyy-mm-dd>                 extract the day, and its ledger
    fold-day.py <yyyy-mm-dd> --apply <file>  splice the folded entry back in

Nothing but the day's own entries is ever read, and nothing but the day's own
entries is ever rewritten. The retained text is untouched *by construction*
rather than by inspection afterwards.

**The ledger is what makes the fold safe to trust.** Extraction records every
SHA, every `**Reviewer:**` line and every `**Hardware debts:**` line in the day.
`--apply` refuses a folded entry that lost any of them. §11 keeps every SHA
because under embarch-dev-workflow.md §6 there is no merge commit and no
surviving branch name, so the SHA is a revert's only handle; and
`grep '^\*\*Reviewer:' supervisor-log.md` is the tally that decides whether
per-unit review keeps earning its cost, which a fold collapsing nine reviewer
lines into one would destroy without failing anything.

**The roll.** §11 said the oldest entries roll into `history/archive/` past
25 KB, "matching what build_changelog.py already does". Nothing ever did it for
this file, and 25 KB was never reachable: leg 010's folded 2026-09-04 entry is
**25 KB on its own**, so the line could not hold one folded day, never mind the
current one beside it. The line is ROLL_BYTES here, raised to 40 KB, and the roll
moves WHOLE DAYS -- never part of one -- oldest first, into `log-archive/`. It
lives in this repo rather than the instance's `history/archive/` because this log
does; §11 says so now.

Usage:
  scripts/fold-day.py --status                  what is unfolded, and roll pressure
  scripts/fold-day.py 2026-09-04                extract to .fold/2026-09-04.md
  scripts/fold-day.py 2026-09-04 --out PATH     extract somewhere else
  scripts/fold-day.py 2026-09-04 --apply PATH   splice, verifying the ledger
  scripts/fold-day.py --roll                    roll whole days past ROLL_BYTES
  scripts/fold-day.py --roll --dry-run          say what would move
Exit status: 0 done / nothing to do, 1 refused, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLEET_REPO = HERE.parent
# Rebound by --log so this is testable against a fixture, and so a fold can be
# rehearsed on a copy before it touches the relay's own handoff.
LOG = FLEET_REPO / "supervisor-log.md"
ARCHIVE = FLEET_REPO / "log-archive"
SCRATCH = FLEET_REPO / ".fold"

# See the docstring: 25 KB could not hold a single folded day.
ROLL_BYTES = 40 * 1024

# A per-unit heading carries a time; a folded day's does not. That difference is
# the whole parser, and it is also what stops a fold from being applied twice.
UNIT_H = re.compile(r"^## (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) — (.+)$")
DAY_H = re.compile(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$")
# Loose on purpose: an entry may write a SHA as 7 or as 40 characters, and the
# ledger's job is to notice a LOSS -- a false negative costs a revert its only
# handle. The one narrowing is that it must contain a digit, which no real SHA
# realistically lacks (7 hex characters with none is about 1 in 1000) and which
# keeps ordinary words out: `defaced` and `effaced` are hex, and refusing a fold
# over a word the summary legitimately dropped is a refusal nobody can diagnose.
# A Slack `ts` matches too, and that is kept rather than fixed: an announcement
# window's timestamp is exactly the kind of handle §11 wants carried.
SHA = re.compile(r"\b(?=[0-9a-f]{7,40}\b)[0-9a-f]*[0-9][0-9a-f]*\b")
REVIEWER = re.compile(r"^\*\*Reviewer:", re.M)
DEBTS = re.compile(r"^\*\*Hardware debts:\*\*.*$", re.M)


def read_log() -> list[str]:
    if not LOG.exists():
        sys.exit(f"no log at {LOG}")
    return LOG.read_text().splitlines(keepends=True)


def sections(lines: list[str]) -> list[tuple[int, int, str, str | None]]:
    """(start, end, date, time) per entry, in file order. time None = folded day.

    The file's own header and `## Entry shape` are not entries and are skipped:
    the shape section is a fenced example containing a literal heading line, and
    a parser that reads a documented shape as data is the failure this log has
    already had twice (see its `## Entry shape` note).
    """
    body = 0
    for i, ln in enumerate(lines):
        if ln.rstrip() == "---":
            body = i + 1
            break
    marks: list[tuple[int, str, str | None]] = []
    for i in range(body, len(lines)):
        m = UNIT_H.match(lines[i].rstrip())
        if m:
            marks.append((i, m.group(1), m.group(2)))
            continue
        m = DAY_H.match(lines[i].rstrip())
        if m:
            marks.append((i, m.group(1), None))
    out = []
    for n, (i, d, t) in enumerate(marks):
        end = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
        out.append((i, end, d, t))
    return out


def ledger_of(text: str) -> dict:
    return {
        "shas": sorted(set(SHA.findall(text))),
        "reviewer_lines": [l for l in text.splitlines() if l.startswith("**Reviewer:")],
        "debt_lines": DEBTS.findall(text),
    }


def cmd_status(lines: list[str]) -> int:
    secs = sections(lines)
    size = LOG.stat().st_size
    print(f"{LOG.name}: {size:,} B against a {ROLL_BYTES:,} B roll line "
          f"({'OVER' if size > ROLL_BYTES else 'ok'})")
    per_day: dict[str, list] = {}
    for s in secs:
        per_day.setdefault(s[2], []).append(s)
    for d in sorted(per_day, reverse=True):
        ss = per_day[d]
        folded = [x for x in ss if x[3] is None]
        units = [x for x in ss if x[3] is not None]
        b = sum(len("".join(lines[a:e])) for a, e, _, _ in ss)
        state = ("folded" if folded and not units else
                 f"{len(units)} UNFOLDED unit(s)" +
                 (" beside a folded entry" if folded else ""))
        print(f"  {d}  {b:7,} B  {state}")
    print("\nA day is foldable once it is over: fold yesterday, not today.")
    return 0


def cmd_extract(lines: list[str], date: str, out: Path) -> int:
    secs = [s for s in sections(lines) if s[2] == date]
    units = [s for s in secs if s[3] is not None]
    if not units:
        print(f"nothing to fold: no per-unit entries dated {date}", file=sys.stderr)
        return 1
    if any(s[3] is None for s in secs):
        print(f"{date} already has a folded entry beside {len(units)} per-unit one(s).\n"
              "Fold them into it by hand, or delete it first -- merging two folds is\n"
              "an editorial act and this refuses to guess at it.", file=sys.stderr)
        return 1
    a, b = units[0][0], units[-1][1]
    if [s for s in sections(lines) if a <= s[0] < b and s[2] != date]:
        print(f"the {date} entries are not contiguous; the log is out of order.",
              file=sys.stderr)
        return 1
    text = "".join(lines[a:b])
    led = ledger_of(text)
    led["date"], led["units"] = date, len(units)
    led["headings"] = [lines[s[0]].rstrip() for s in units]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    (out.with_suffix(".ledger.json")).write_text(json.dumps(led, indent=2) + "\n")
    print(f"{len(units)} unit(s), {len(text):,} B -> {out}")
    print(f"ledger -> {out.with_suffix('.ledger.json')}: "
          f"{len(led['shas'])} SHA(s), {len(led['reviewer_lines'])} reviewer line(s), "
          f"{len(led['debt_lines'])} hardware-debt line(s)")
    print(f"\nWrite the folded entry to a NEW file, starting `## {date} — "
          f"{len(units)} units`,\nthen: scripts/fold-day.py {date} --apply <that file>")
    return 0


def cmd_apply(lines: list[str], date: str, src: Path, allow_debt_edit: bool) -> int:
    ledger_path = SCRATCH / f"{date}.ledger.json"
    for cand in (src.with_suffix(".ledger.json"), ledger_path):
        if cand.exists():
            led = json.loads(cand.read_text())
            break
    else:
        print(f"no ledger for {date} (looked in {ledger_path}); run the extract first "
              "-- applying without one would check nothing.", file=sys.stderr)
        return 2
    folded = src.read_text()
    if not folded.endswith("\n"):
        folded += "\n"

    problems = []
    head = folded.splitlines()[0].rstrip() if folded.strip() else ""
    if not DAY_H.match(head) or not head.startswith(f"## {date} —"):
        problems.append(f"first line must be `## {date} — <N> units`, not {head!r}")
    missing = [s for s in led["shas"] if s not in folded]
    if missing:
        problems.append(f"{len(missing)} SHA(s) dropped: {', '.join(missing[:12])}"
                        + (" ..." if len(missing) > 12 else ""))
    kept = REVIEWER.findall(folded)
    if len(kept) != len(led["reviewer_lines"]):
        problems.append(
            f"{len(kept)} line-anchored `**Reviewer:` line(s), expected "
            f"{len(led['reviewer_lines'])} -- one per unit, at the start of a line, or "
            "`grep '^\\*\\*Reviewer:' supervisor-log.md` stops tallying this day")
    lost_debts = [d for d in led["debt_lines"] if d not in folded]
    if lost_debts and not allow_debt_edit:
        problems.append(f"{len(lost_debts)} hardware-debt line(s) not carried verbatim:\n"
                        + "\n".join(f"      {d[:110]}" for d in lost_debts)
                        + "\n    A debt names a board nobody else knows is owed. Carry the\n"
                          "    line, or pass --allow-debt-edit and say in the commit why.")
    if problems:
        print(f"REFUSED: the folded entry loses something the day carried.\n")
        for p in problems:
            print(f"  - {p}")
        return 1

    secs = [s for s in sections(lines) if s[2] == date and s[3] is not None]
    a, b = secs[0][0], secs[-1][1]
    before = LOG.stat().st_size
    LOG.write_text("".join(lines[:a]) + folded + "".join(lines[b:]))
    after = LOG.stat().st_size
    if lost_debts:
        print(f"--allow-debt-edit: {len(lost_debts)} debt line(s) reworded. Name them "
              "in the fold commit.")
    print(f"folded {len(secs)} unit(s) of {date}: {before:,} B -> {after:,} B "
          f"({before - after:,} B)")
    print(f"kept {len(led['shas'])} SHA(s), {len(kept)} reviewer line(s), "
          f"{len(led['debt_lines']) - len(lost_debts)} debt line(s) verbatim")
    return 0


def cmd_roll(lines: list[str], dry: bool) -> int:
    """Move the OLDEST whole days out. The file is newest-first, so `oldest`
    means a trailing slice -- getting that backwards would archive the handoff
    and keep the history, which is the one direction this must never get wrong.
    """
    size = LOG.stat().st_size
    if size <= ROLL_BYTES:
        print(f"{size:,} B, under the {ROLL_BYTES:,} B line; nothing to roll.")
        return 0
    secs = sections(lines)
    if not secs:
        sys.exit("no entries found; refusing to roll a file this cannot parse")
    days: dict[str, tuple[int, int]] = {}
    for a, b, d, _ in secs:
        lo, hi = days.get(d, (a, b))
        days[d] = (min(lo, a), max(hi, b))
    order = sorted(days)                      # oldest first
    # The two newest days always stay: a relay's step 0 reads the current day
    # and the one before it, and an archive that has to be opened to make the
    # handoff readable is not an archive.
    n, freed = 0, 0
    while n < len(order) - 2:
        d = order[n]
        chunk = sum(len(l) for l in lines[days[d][0]:days[d][1]])
        if size - freed - chunk < 0:
            break
        n += 1
        freed += chunk
        if size - freed <= ROLL_BYTES:
            break
    if not n:
        print(f"{size:,} B is over the line, but only {len(order)} day(s) are here "
              "and the two newest always stay. Fold a day rather than rolling one.")
        return 0
    rolled = order[:n]
    start = days[rolled[-1]][0]               # newest of the rolled set = earliest line
    # Whole days only, and they must tile the tail exactly: half a day in the
    # archive and half in the log is a handoff that reads as complete and is not.
    covered = sorted(days[d] for d in rolled)
    if covered[0][0] != start or covered[-1][1] != len(lines) or \
            any(covered[k][1] != covered[k + 1][0] for k in range(len(covered) - 1)):
        print("the days to roll are not a contiguous tail; the log is out of order.",
              file=sys.stderr)
        return 1
    lo, hi = rolled[0], rolled[-1]
    dest = ARCHIVE / f"supervisor-log-{lo}-to-{hi}.md"
    body = "".join(lines[start:])
    header = (f"# Supervisor log archive: {lo} to {hi}\n\n"
              f"**Status:** retired, {hi}. Rolled out of "
              f"[../supervisor-log.md](../supervisor-log.md) by `scripts/fold-day.py "
              f"--roll` (protocol.md §11). Newest first, exactly as they stood.\n\n---\n\n")
    pointer = (f"*Days {lo} to {hi} rolled to "
               f"[log-archive/{dest.name}](log-archive/{dest.name}).*\n")
    if dry:
        print(f"would move {n} day(s) ({lo}..{hi}, {len(body):,} B) -> {dest}")
        print(f"leaving {size - len(body) + len(pointer):,} B")
        return 0
    ARCHIVE.mkdir(exist_ok=True)
    dest.write_text(header + body)
    LOG.write_text("".join(lines[:start]) + pointer)
    print(f"rolled {n} day(s) ({lo}..{hi}) -> {dest}")
    print(f"{LOG.name}: {LOG.stat().st_size:,} B")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date", nargs="?", help="the day to fold, yyyy-mm-dd")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--out", type=Path, help="where the extract goes")
    ap.add_argument("--apply", type=Path, metavar="FILE", help="the folded entry to splice in")
    ap.add_argument("--allow-debt-edit", action="store_true",
                    help="permit a hardware debt to be reworded rather than carried verbatim")
    ap.add_argument("--roll", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--log", type=Path, help="operate on this log instead (testing, rehearsal)")
    args = ap.parse_args()

    if args.log:
        global LOG, ARCHIVE, SCRATCH
        LOG = args.log.resolve()
        ARCHIVE = LOG.parent / "log-archive"
        SCRATCH = LOG.parent / ".fold"

    lines = read_log()
    if args.status:
        return cmd_status(lines)
    if args.roll:
        return cmd_roll(lines, args.dry_run)
    if not args.date or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        ap.error("give a date as yyyy-mm-dd, or --status / --roll")
    if args.apply:
        return cmd_apply(lines, args.date, args.apply, args.allow_debt_edit)
    return cmd_extract(lines, args.date, args.out or SCRATCH / f"{args.date}.md")


if __name__ == "__main__":
    sys.exit(main())
