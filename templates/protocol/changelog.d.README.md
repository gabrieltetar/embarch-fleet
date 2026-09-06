# changelog.d

One file per change, holding **one line** of reader-facing text. Nothing edits a
shared history file directly.

    <scope>-<slug>.<category>.md

- **scope** — a sub-project without the `embarch-` prefix (`core`, `api`,
  `dev-bench`, `study-designer`, `outpost`, `ui`, `topology`, `umbrella`,
  `fleet`, `promptu`, `atlas`), or `suite` for something spanning several, or
  `doc` for this repo's own practices. The list is derived from the `embarch-*`
  directories rather than from this sentence, so a new sub-project needs no edit
  here — but `fleet` is worth naming: its work lands in the framework repo and
  only its fragment comes back here.
- **slug** — any short unique hyphenated name for the change.
- **category** — `added`, `changed`, `fixed`, `removed`, or `decided`.

The line is a pointer, not the account: **200 bytes maximum, one line, hard
checked.** Where the change is explained is the doc it changed — link to it.

    core-rram-runner.changed.md
      Core picks the board's declared vendor runner per chip family; never probe-rs on Nordic RRAM parts.

**A fold passes `--only '<its own fragment>'`.** Bare, the assembler consumes
every pending fragment rather than the folding unit's, and on 2026-09-06 that
swept 15 of the owner's into a leg's fold — well-formed entries in the right
file, so nothing failed and the diff read correctly. `fold-commit.py` refuses
that now. Assembling the whole directory is right only when you mean to.

`scripts/build_changelog.py` assembles these into `history/<scope>.md` under a
dated window heading and deletes the consumed fragments. `--check` validates
without assembling, and runs in CI, so a misnamed fragment fails loudly instead
of being silently skipped.

## Why this exists

Until 2026-09-02 this repo kept history as a `## Changelog` section inside every
doc. Those sections reached **642 KB — 25% of the whole corpus** — with a mean
entry of 1,100 bytes, against DOC-PROTOCOL.md's own rule that an entry is "a
one-line dated pointer". A history section that lives inside the doc it
describes grows without anyone ever deciding to let it, and it competes for the
reader with the thing the doc is actually for.
