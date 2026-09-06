#!/usr/bin/env python3
"""Cap this repo's own docs, as a ratchet, because nothing else ever did.

`embarch-doc` has had per-file caps since 2026-09-02 and `check-doc-size.py`
enforces them in CI. **This repo was never in that corpus**, and the gap was
invisible because the docs here cite the rule as though it were: `risks.md`
opens by saying it was "split out of [protocol.md] §12 on 2026-09-03 when that
doc reached its size cap ([DOC-COMPACTION.md] §3)" -- and §2's table has no row
for `embarch-fleet/*.md`, and `check-doc-size.py` never walks this directory.
A cap enforced by nothing but the memory of having split a file once is the same
"discipline, not a mechanism" `risks.md` prefers to remove everywhere else.

What it had cost by 2026-09-05: `protocol.md` and `ops.md` sat within ~500 B of
32 KB, 2.7x the 12 KB DOC-COMPACTION.md §2 gives a protocol doc, and a single
owner sitting grew `protocol.md` by ~1 KB with nothing noticing.

**Baselines come from `git show HEAD:`, never the working tree.** A ratchet
seeded from whatever is on disk pins the growth that revealed the need for it,
which is the opposite of a ratchet. Seeding from HEAD means the change being
made right now has to pay for itself.

**No reserve band and no debt filing here**, unlike `check-doc-size.py`. Those
exist so a *worker* meets a cap as a filed task rather than as a refused edit
mid-flight, and no worker ever writes these files -- a leg never checks this repo
out. The only actor here is the owner, in their own session, who can shorten a
paragraph on the spot. Adding the reserve machinery would be a second
implementation of it for a corpus with nobody to protect.

`supervisor-log.md` is exempt: its size is governed by the fold and the roll
(`fold-day.py`), which bound it by days rather than by bytes, and a byte cap
here would be the third unreachable line written for that file.

Usage:
  scripts/check-fleet-doc-size.py            check (deploy.py runs this)
  scripts/check-fleet-doc-size.py --report   the whole corpus against its caps
  scripts/check-fleet-doc-size.py --update   record progress: lower what shrank
  scripts/check-fleet-doc-size.py --adopt    seed a baseline from HEAD (bootstrap)
Exit status: 0 if nothing exceeds min(cap, baseline), 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "scripts" / "doc-size-baseline.json"
KB = 1024

# role -> (cap, matcher). Deliberately few: this repo is eight files, not a
# corpus, so a role table with more rows than documents would be theatre.
CAPS = [
    # The two design docs. 25 KB is DOC-COMPACTION.md §2's narrative tier, which
    # is the closest existing role -- these are read start to finish the way a
    # guide is, not consulted by section the way a reference is. Both are over
    # it today and hold baselines; the ratchet is what closes that.
    ("design",   25 * KB, re.compile(r"^(protocol|ops)\.md$")),
    # Everything else here is a protocol doc in DOC-COMPACTION.md's sense.
    ("protocol", 12 * KB, re.compile(r"^[A-Za-z][A-Za-z.-]*\.md$")),
]
# supervisor-log.md: bounded by fold-day.py, see the docstring. log-archive/ is
# where the roll puts whole days and is meant to grow. templates/ renders into
# the instance, where check-doc-size.py already caps the result.
EXEMPT = re.compile(r"^(supervisor-log\.md$|log-archive/|templates/|\.)")


def role_and_cap(rel: str):
    for role, cap, pat in CAPS:
        if pat.search(rel):
            return role, cap
    return None, None


def docs():
    for p in sorted(REPO.rglob("*.md")):
        rel = str(p.relative_to(REPO))
        if EXEMPT.search(rel) or ".git" in p.parts:
            continue
        yield rel, p.stat().st_size


def head_size(rel: str) -> int | None:
    r = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                       capture_output=True)
    return len(r.stdout) if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--update", action="store_true",
                    help="lower a baseline that shrank; refuses to raise one")
    ap.add_argument("--adopt", action="store_true",
                    help="seed a missing baseline from HEAD (bootstrap only)")
    args = ap.parse_args()

    base = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    fails, rows, changed = [], [], False

    for rel, size in docs():
        role, cap = role_and_cap(rel)
        if cap is None:
            continue
        if args.adopt and rel not in base:
            h = head_size(rel)
            if h is not None and h > cap:
                base[rel], changed = h, True
                print(f"  adopt {rel}: baseline {h:,} B (HEAD, not the worktree)")
        # A file WITH a baseline is over cap and is allowed up to that baseline,
        # which only ever moves down; a file without one is capped outright.
        # `min(cap, baseline)` reads well in prose and is wrong as code -- it
        # would hold every over-cap file to the cap it has not reached yet, which
        # is a wall, not a ratchet. Same shape as check-doc-size.py, on purpose.
        limit = base[rel] if rel in base else cap
        if args.update and rel in base and size < base[rel]:
            print(f"  lower {rel}: {base[rel]:,} -> {size:,} B")
            base[rel], changed, limit = size, True, size
        if rel in base and size <= cap and (args.update or args.adopt):
            print(f"  {rel} reached its {cap:,} B cap; baseline retires")
            del base[rel]
            changed, limit = True, cap
        rows.append((rel, role, size, cap, base.get(rel)))
        if size > limit:
            fails.append((rel, role, size, limit, cap))

    if changed and (args.update or args.adopt):
        BASELINE.write_text(json.dumps(dict(sorted(base.items())), indent=2) + "\n")
        print(f"\nwrote {BASELINE.relative_to(REPO)}")

    if args.report:
        print(f"{'file':28} {'size':>8} {'cap':>8} {'baseline':>9}  role")
        for rel, role, size, cap, b in rows:
            print(f"{rel:28} {size:8,} {cap:8,} "
                  f"{(f'{b:,}' if b else '-'):>9}  {role}")

    if fails:
        print(f"\n{len(fails)} file(s) over their limit:\n")
        for rel, role, size, limit, cap in fails:
            over = size - limit
            why = "cap" if limit == cap else "baseline (it may only shrink)"
            print(f"  {rel}  {size:,} B against {limit:,} ({why}) -- {over:,} B over")
        print("\nShorten the file. A baseline never rises: this repo's whole premise\n"
              "is that a rule the fleet runs under stays readable start to finish.")
        return 1
    if not args.report:
        print(f"OK: {len(rows)} doc(s) within min(cap, baseline).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
