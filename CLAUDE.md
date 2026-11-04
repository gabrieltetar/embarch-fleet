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

**The instance's `.claude/`, its three protocol READMEs and its `scripts/` shims
are generated from [templates/](templates/) and [scripts/](scripts/) here.** Edit
the template, never the copy; `python3 scripts/deploy.py` renders, gates, stamps
and commits, and `install.py --check` is what catches a hand-edit. DEVELOPING.md
§1–2 has the table of what takes effect when.

## Git

Work on a branch, land when the owner asks — no PRs (2026-11-03). One branch name
across every repo the change touches, pushed; land on `main` only when the repo
owner asks, by rebase and fast-forward. See
`../embarch-doc/embarch-dev-workflow.md` §6.
