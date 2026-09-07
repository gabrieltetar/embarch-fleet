---
description: Run one suite review pass - seven parallel hunters over every sub-project at once, looking for design flaws and improvement opportunities, landing as inbox drops.
argument-hint: "[dimension filter, e.g. dry,layering] [--no-drops]"
---

**Spawn one `embarch-auditor` agent to run this pass, and do not run it
yourself.** Pass it the working directory `{{DOC_REPO}}` and the arguments
below. Relay its final report; do not predict it.

Why the indirection is the same as `/supervise`'s: the owner's session holds the
pen for standing rules, `scripts/` and `.claude/`, and a pass that reads the
whole suite looking for things to change must not also be the context that can
change them. The auditor writes to `inbox/` and one ignored report file, and
nothing else (`{{DOC_REPO}}/SUITE-REVIEW-PASS.md` §10).

Arguments: `$ARGUMENTS` — an optional comma-separated subset of the seven
dimensions to run (default: all seven), and `--no-drops` to write the report
without writing anything to `inbox/`.

## Before you spawn anything

Two preflight checks, and **you** run them, not the auditor — the first can
require the owner to act and the second is cheap here and awkward from a
subagent:

1. **Is the pump latched?** `{{STATE_DIR}}/pump` exists and
   `{{STATE_DIR}}/tick` is fresh (under ~25 minutes) means a leg is alive or
   about to be. **Do not start the pass.** Say so, and say why in one line: a
   leg's tree is up to three units stale and *nothing errors*, so a pass reading
   a moving tree produces confidently wrong findings against files that were
   fixed twenty minutes ago. Stopping the fleet is the owner's move — `fleet
   stop` in {{SLACK_CHANNEL_NAME}}, or closing the listener window.
2. **Is every repo clean and current?** `git status --porcelain` and
   `git log --oneline -1` in `{{DOC_REPO}}` and each sub-project repo under
   `{{FLEET_ROOT}}`. Uncommitted work is not a refusal — it is a fact the
   auditor must be told, because a finding about a file you are mid-edit on is
   noise it cannot detect on its own. Name the dirty repos in the spawn.

If the owner says to run it anyway with the pump up, that is their call and it
is legitimate. Say plainly that findings may be up to one leg stale, and pass
that fact to the auditor so the report carries it.

## What to hand the auditor

- The working directory `{{DOC_REPO}}`, absolute.
- The `main` SHA of `{{DOC_REPO}}` and of every sub-project repo, read at
  preflight. The report is against those SHAs and says so.
- Which dimensions to run, and whether `--no-drops` is set.
- Any dirty repos from check 2, by name.
- The pump's state as you found it.

## What comes back

A report at `{{DOC_REPO}}/.claude/suite-review-<yyyy-mm-dd>.md` — uncommitted,
`.gitignore`d, regenerable — plus one `inbox/` drop per finding that cleared the
bar. Relay the ranking and the count; the drops speak for themselves at the next
leg's phase 1.

**The report's owner-only section is for you.** Findings about the fleet's own
rules, `DOC-PROTOCOL.md`, `scripts/`, `.claude/` or anything else in
`fleet.toml`'s `reserved` list **cannot become queue tasks** — there is no
`fleet` worker scope and those paths are yours. Read that section yourself; the
auditor is forbidden from filing any of it.

## Afterwards, one question

`{{DOC_REPO}}/SUITE-REVIEW-PASS.md` §7: **of what this run dropped, how much
would you have wanted done anyway?** Mostly yes means the pass is working;
mostly no means the bar drifted, and the next run's instruction is to raise it
rather than to find more. Nothing records the answer — say it out loud so the
next run's spawn can carry it.
