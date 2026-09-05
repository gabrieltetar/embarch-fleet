# status.d

One file per **pending edit to a shared suite-level doc**. A worker never edits
[../embarch.md](../embarch.md),
[../suite/roadmap.md](../suite/roadmap.md),
[../embarch-decision-reversals.md](../embarch-decision-reversals.md),
[../embarch-glossary.md](../embarch-glossary.md) or
[../suite/user-guide.md](../suite/user-guide.md) directly; it drops a
fragment here and the supervisor folds every fragment in one serialized commit
at the end of a batch ([the protocol]({{FLEET_REL}}/protocol.md) §9).

**A feature-inventory row is no longer one of these.**
[../suite/features.md](../suite/features.md) is assembled from
[../features.d/](../features.d/README.md), and a worker owns
`features.d/<its own scope>-*` — so it writes the row itself, in the commit that
earned it, rather than asking for one here.

    <scope>-<slug>.md

Same `scope` vocabulary as [../changelog.d/README.md](../changelog.d/README.md).

## Format

```markdown
**Target:** embarch.md §3 — the `embarch-ui` row
**Was:** "six tabs live; Trace view has never rendered a DUT capture"
**Now:** seven tabs; the Trace view renders a real DUT capture as of 2026-09-02.
```

Three lines, in that order. `Target` names the doc and the smallest place in it
that changes. `Was` is what the doc says today — quoted, so the supervisor can
find it and can tell whether someone else already changed it. `Now` is the fact,
not the sentence: **write the truth, not the prose.** The supervisor writes the
prose, because it is folding several fragments into one table and only it can
see them together.

Free prose may follow the three lines where the change needs it — a roadmap
bucket move, a status-table correction. Keep it short; the account of the
change lives in the sub-project doc the worker already updated, and this
fragment links there rather than restating it.

## Rules

- **One fragment, one target doc.** A change that makes facts false in two
  suite-level docs is two fragments.
- **A fragment is not a changelog entry.** `changelog.d/` records that something
  happened; `status.d/` records that a shared doc is now wrong. Most changes
  need the first and not the second.
- **The batch is not done while a fragment is left here.** An unfolded fragment
  means a suite-level doc disagrees with a sub-project's, which is exactly what
  `DOC-PROTOCOL.md` §5 exists to prevent.

## Why this exists

`DOC-PROTOCOL.md` §5 tells whoever ships a change to update the suite-level
facts in the same pass. That is a rule against drift when one engineer works
alone, and a rule that puts four agents into the same table at once when they
do not. `changelog.d/` already proved the shape: one file per change, nothing
edits a shared file directly.
