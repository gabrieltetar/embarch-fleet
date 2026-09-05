# embarch-fleet

## Docs

**Read [README.md](README.md) first** — it says what each file here is and in what
order to read them. This repo *is* its own documentation: [protocol.md](protocol.md)
is the design, [ops.md](ops.md) is running it, [risks.md](risks.md) is what each
choice traded away, [open.md](open.md) is unresolved, and
[DEVELOPING.md](DEVELOPING.md) is how to change any of it and deploy the change.

The suite-level view — what this sub-project is, for a reader coming from the
suite rather than from here — is
[../embarch-doc/embarch-fleet/spec.md](../embarch-doc/embarch-fleet/spec.md). It
is one file on purpose: everything else about the fleet lives here, and a second
copy of a rule an agent is running under is the one kind of drift this repo
cannot afford. Update it per `../embarch-doc/DOC-PROTOCOL.md` §4–5 whenever
something here changes what the fleet *is*; history goes in a
`../embarch-doc/changelog.d/` fragment scoped `fleet-`, not into a doc.

## Editing this repo

**The instance's `.claude/`, its four protocol READMEs and its `scripts/` shims
are generated from [templates/](templates/) and [scripts/](scripts/) here.** Edit
the template, never the copy; `python3 scripts/deploy.py` renders, gates, stamps
and commits, and `install.py --check` is what catches a hand-edit. DEVELOPING.md
§1–2 has the table of what takes effect when.

## Git

Work directly on `main` — no feature branches, no PRs (2026-08-25). Overrides the
general "branch before committing to the default branch" default, for this suite
only; ends when the repo owner explicitly says so. See
`../embarch-doc/embarch-dev-workflow.md` §6.
