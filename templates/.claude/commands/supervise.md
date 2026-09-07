---
description: Run one supervisor leg - up to 4 units, each one task with one worker, landed and folded and logged as it finishes.
argument-hint: "[max-units] [scope filter, e.g. core,ui]"
disable-model-invocation: true
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

**Why `disable-model-invocation` is in the frontmatter, and is the actual
mechanism.** The leg's instructions lived in this file until 2026-09-07, below a
`---` and a sentence saying the rest was what the agent follows. Legs 028 and
029 each read the file they were pointed at, obeyed its first and most emphatic
instruction, and spawned an `embarch-supervisor` that did the same. Splitting
`.claude/leg.md` out was necessary and **was not sufficient**: leg 029's first
tool call was `Skill(supervise)`, because "run one leg per
`.claude/commands/supervise.md`" reads as an instruction to invoke the command
of that name. **Invoking a command injects its whole body as a USER turn**,
which outranks an agent's system prompt — so the redirect four lines above this
one was delivered, read, and lost the argument to "spawn one background
`embarch-supervisor`" ten lines below it. The leg even copied "never spawn an
`embarch-supervisor` agent yourself" into the prompt of the agent it was
spawning.

Two things follow, and the second is the one with teeth. Prose separating two
audiences inside one file is not a boundary — **the file the leg reads must not
contain the instruction to spawn a leg**, the shape `/suite-review` already had
(`SUITE-REVIEW-PASS.md` carries the auditor's method, the command carries the
spawn). And a boundary written in prose is not a boundary at all while the file
is reachable as a tool call: `disable-model-invocation: true` means only a
person can type `/supervise`, and an agent that tries gets a refusal instead of
a leg. Every owner-typed command here carries it now.

If the owner explicitly says to run a leg inline instead, that is their call and
it is legitimate — read `.claude/leg.md` and follow it here, and say plainly
that the role separation is off for that run.
