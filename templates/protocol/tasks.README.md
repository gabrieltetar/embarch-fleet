# tasks

The work queue background agents pull from. One file per task, committed to
`main`, claimed by editing the file. Governed by
[the protocol]({{FLEET_REL}}/protocol.md).

    tasks/<sub-project>/<NNN>-<slug>.md

- **sub-project** — without the `embarch-` prefix (`core`, `api`, `dev-bench`,
  `study-designer`, `outpost`, `ui`, `topology`, `umbrella`, `promptu`,
  `atlas`), or `doc` for this repo, or `suite` for a task spanning several.
  A `suite/` task is **never dispatched to a worker** — the supervisor executes
  it itself (`{{FLEET_REL}}/protocol.md` §8).
- **NNN** — three digits, monotonic per sub-project, never reused.
- **slug** — short, hyphenated.

## File format

```markdown
# 007 — Drain the SSE subscriber on api's study_status

**State:** open
**Source:** embarch-core/open.md — "api/CLI consumption of /study/{id}/events is not built"
**Scope:** api                     <!-- one sub-project, or `suite` -->
**Hardware:** none                 <!-- none | verify-only | required -->
**Owner:** no                      <!-- `required` if every path it writes is reserved -->

## What

One paragraph. What is to be true when this is done.

## Why now

One or two sentences, and the doc that says so. A task with no source doc is a
task the supervisor invented; that is allowed, and it says so here.

## Done when

- [ ] Concrete, checkable items.
- [ ] Gate green (`{{FLEET_REL}}/protocol.md` §10).
- [ ] `spec.md`/`decisions.md`/`open.md` updated, `changelog.d/` fragment
      dropped, `status.d/` fragment for anything suite-level it made false.
```

## States

`open` → `claimed` → `done`, or → `blocked`.

- **claimed** — the claim line becomes
  `**State:** claimed by agent/<scope>/<NNN-slug>, <yyyy-mm-dd HH:MM>`.
  Claiming is a commit to `main` by the supervisor **before** dispatch, not by
  the worker after it starts. Two supervisors cannot both claim; one supervisor
  is what this relies on.

  **A claim outlives the worker that made it, so releasing it needs a rule.**
  The rule is exact rather than a timeout, because the process tree makes it
  exact: workers are the supervisor's own in-process subagents, so **if no
  supervisor is running, every claim is stale.** A supervisor killed mid-batch
  — and closing VS Code is the owner's kill switch, so this is routine — takes
  its workers with it.

  Recovery (`{{FLEET_REL}}/protocol.md` §6 phase 0) therefore reclaims every
  claim at startup — **reading the worktree, not the branch.** A worker's tree
  is uncommitted for its whole run and becomes commits only in its final
  bookkeeping, so a branch's commit count reads zero both for a worker that
  never started and for one that died holding finished work. Three outcomes:

  - **Clean tree, no commits** → back to `open`, delete the worktree.
  - **Anything else** → `blocked`, naming the branch **and the worktree path**,
    and delete nothing.

  **Commit a dirty tree to its branch before deciding.** It is cheap and
  reversible; deleting is neither, and committing is what saved leg 007 when it
  began recovery on a worker that turned out to be alive. It also makes "delete
  dead worktrees" a safe unconditional step afterwards rather than a judgement
  call made twice.

  **This rule replaced its opposite on 2026-09-05, and the opposite had already
  fired.** It used to read "no commits means back to `open`". Leg 009's
  `tasks/ui/002` was reclaimed to `open` on exactly that basis — branch tip
  identical to `main`, which is what the old rule expects of work that never
  happened — while its worktree held **306 uncommitted insertions that built
  clean, passed 97 tests and covered three of the task's four code `Done when`
  boxes**. Nothing was lost only because the worktree deletion that the same
  tidy-up owed had not run either: two defects cancelled out. The dangerous
  combination is the old rule working as written — reclaim to `open` *and*
  delete — after which a task is re-dispatched and nobody ever learns it was
  done once. `{{FLEET_REL}}/ops.md` §3's table says the same thing; when they
  disagree, they are both wrong and it is worth saying so out loud.

  The timestamp remains as the backstop for the one case the process tree
  cannot settle — a supervisor that is alive but wedged — where a claim older
  than 4 hours is reclaimed the same way.
- **blocked** — the worker appends a `## Blocked` section saying what it found
  and exits. State returns to `open` only when whatever it named is resolved.
- **done** — the worker ticks its `Done when` boxes and appends what shipped;
  the **supervisor deletes the file in the fold**, so a landed task leaves the
  queue in the same commit that folds its fragments. Git holds it, and a
  completed task left in the queue competes with the open ones for attention —
  the same reasoning `DOC-PROTOCOL.md` §3 applies to a shipped milestone doc.
  (Batch 003's supervisor flagged that this said only "deleted in the merge"
  while both its workers had marked the body `done`. Both behaviours are right;
  only the description was missing half of it.)

## Hardware field

`none` — fully host-side, dispatchable. `verify-only` — the change can be built
and unit-tested by a worker but its real behaviour needs a board; dispatchable,
and it must leave a hardware-verification debt (§7). `required` — cannot be
started without hardware; **not dispatchable**, it waits for the owner's own
session. A task nobody has classified is treated as `required`.

## Owner field

`no` (the default, and what an absent line means) — any worker may take it.
`required` — **every path this task must write is reserved to the owner**
(`{{FLEET_REL}}/fleet.toml`'s `reserved` list, enforced by `check-ownership.py`),
so dispatching it burns a worker that will fail the ownership check on its first
edit. Not dispatchable; it waits for the owner's own session.

Unlike `Hardware:`, a missing line here is **not** read as `required` — that
would gate the whole queue on a field most tasks have no reason to carry, and
`check-ownership.py` refuses the write either way. This field exists to stop the
dispatch being wasted, not to be the enforcement.

## Compaction tasks

A doc within the last 10% of its size cap is **in reserve**
(`scripts/check-doc-size.py`). The reserve is writable and the gate still
passes, but the file must be named by an open task here, and **the commit that
spends the reserve is the one that files it** — see `DOC-COMPACTION.md` §2. The
gate fails on an unfiled file in reserve and names it.

    tasks/<scope>/<NNN>-compact-<scope>.md

**`<scope>` is the scope of the doc being compacted, not `doc`** — an
`embarch-api` file in reserve is filed at `tasks/api/<NNN>-compact-api.md`, and
`doc` is for this repo's own protocol docs and nothing else. That is a path the
actor who spent the reserve owns, which is the whole point: until 2026-09-05 this
said `tasks/doc/` for everyone, and `check-ownership.py` refuses `tasks/doc/**` to
every worker scope — so the only actor told to file the debt was the one actor
forbidden to. `check-doc-size.py` rglobs all of `tasks/` and matches on the
`**Compacts:**` field, so it found the debt either way and the two rules had no
mechanical collision to reveal them; `agent/api/009` found it by disobeying one of
them on purpose and saying so (`tasks/doc/004`).

**One task may name several files**, and normally does: a compaction pass is a
sub-project act, one commit per sub-project (`DOC-COMPACTION-PASS.md`). Three
fields are required and they are not paperwork — **they are the judgements no
script can make, recorded by the only actor with the context to make them:**

```markdown
**Compacts:** embarch-core/spec.md, embarch-core/open.md
**In flux:** no                    <!-- yes → State: blocked, and say what unparks it -->
**Must not delete:** the 18-stale-records candidate fix in open.md; decision 36's
probe-rs counterfactual, which is evidence and not proof and reads as proof once
shortened.
```

- **`Compacts:`** is what `check-doc-size.py` matches on. It matches this field
  and nothing else: a path merely *mentioned* in a task body made five of one
  day's twelve files read as filed, because every task cites the doc it is about
  to edit.
- **`In flux:`** is `DOC-COMPACTION-PASS.md`'s warning, asked of whoever just
  worked in that subsystem. **Yes is a legitimate and cheap answer** — set
  `**State:** blocked` and name the milestone that unparks it. Compacting a
  subsystem still moving writes a clean statement of something about to be
  wrong and destroys the alternatives you are about to need; a parked task is
  the mechanism working. **But it parks the pass, not the reserve** — the next
  unit to write that file still meets the cap mid-flight, and on 2026-09-05 a
  96-byte remainder pushed an `embarch-api` decision into the wrong topic file
  rather than refusing it. So a parked file's compaction **rides in the unit
  that next writes it**, same commit, carrying this task's `Must not delete:`
  list and closing only that file's item. `DOC-COMPACTION.md` §2 is the rule;
  a mission split is the cheaper move where the file holds more than one.
- **`Must not delete:`** is what the filer knows and the eventual compactor will
  not. Anything: a failure signature, a rejected alternative, a measurement that
  reads as an assumption once its date goes.

**`Done when` carries `DOC-COMPACTION-PASS.md`'s human question**, answered in the
compactor's own words in the commit message: *can `spec.md` alone answer what
someone needs to work on this component today?* No script answers it and the
gate does not either.

When the paths are reserved — `DOC-PROTOCOL.md` and `DOC-COMPACTION.md` are the
standing case — the task still lives here, because `inbox/` is not committed and
a debt filed there would pass on the filer's machine and fail in CI. Mark it
`**Owner:** required` so no worker is sent at it.

## Why the queue is a file and not the supervisor's head

Two supervisor runs cannot dispatch the same task; a task outlives the thread
working it; and the reason a task exists is written next to it rather than
re-derived from the roadmap each batch. The cost is that the queue is a *view*
of the docs and can drift from them — refill reconciles, in one direction only
(`{{FLEET_REL}}/protocol.md` §12).
