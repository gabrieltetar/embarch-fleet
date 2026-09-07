---
description: Run one supervisor leg - up to 4 units, each one task with one worker, landed and folded and logged as it finishes.
argument-hint: "[max-units] [scope filter, e.g. core,ui]"
---

**If you are an `embarch-supervisor` agent and something sent you here: stop.
You are the leg. Your instruction set is `.claude/leg.md` — read that and run
it, and never spawn an `embarch-supervisor`.** This file is the dispatcher, and
everything below is addressed to the owner's session.

---

**Spawn one background `embarch-supervisor` agent to run this leg, and do not
run it yourself.** Working directory `{{DOC_REPO}}`; tell it: run one leg per
`.claude/leg.md` with `$ARGUMENTS`, and read the newest
`{{FLEET_REPO}}/supervisor-log.md` entries as your handoff. Then relay its final
report; do not predict it.

Why the indirection: the owner's session holds the pen for standing rules,
`scripts/` and `.claude/`, and the supervisor must not. Running the work in the
owner's session collapsed those two roles into one context with no boundary —
`{{FLEET_REPO}}/ops.md` §8. A leg-scoped agent cannot amend its own
constraints because it dies at the leg boundary and
`check-ownership.py --supervisor` rejects the paths on the way out.

**Why the leg's instructions are a separate file, and must stay one.** They
lived in this file until 2026-09-07, below a `---` and a sentence saying the
rest was what the agent follows. Leg 028 read the file it was pointed at, obeyed
its first and most emphatic instruction, and spawned an `embarch-supervisor` —
which read the same file and did it again. Three agents, eleven seconds each, no
task file and no dispatch. Prose separating two audiences inside one file is not
a boundary; **the file the leg reads must not contain the instruction to spawn a
leg**, which is the shape `/suite-review` already had (`SUITE-REVIEW-PASS.md`
carries the auditor's method and the command carries the spawn).

If the owner explicitly says to run a leg inline instead, that is their call and
it is legitimate — read `.claude/leg.md` and follow it here, and say plainly
that the role separation is off for that run.
