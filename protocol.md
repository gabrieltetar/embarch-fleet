# EmbArch: parallel agent work

**Status:** active, 2026-09-03. Nineteen legs have run under it (see [supervisor-log.md](supervisor-log.md)); the risks are in [risks.md](risks.md). The relay in §6 has run since 2026-09-05.

## 1. Why this exists

Every rule in this suite was written for one engineer in one session. [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6 says commit straight to `main` and justifies it *by* that assumption — "this suite has one engineer … there is nothing to collide with". [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 tells whoever ships a change to update the suite-level status tables in the same pass, safe exactly once per moment. Both stop being safe the moment four agents work at once.

So: **a supervisor thread keeps 4–6 short-lived worker threads in flight, each owning one sub-project, and lands their work itself.** A supervisor runs a bounded **leg** — four tasks — and a listener spawns its successor, so the fleet outlives any one supervisor's context (§6). This doc replaces the single-session assumption for those threads. It governs background threads only — the owner's interactive sessions keep working as before, on `main`, under §6 unchanged.

The design principle throughout: **prevent collisions structurally; do not resolve them.** A supervisor merging two workers' edits to one table is guessing at two intents it never held. Every rule below exists so that merge never has to happen.

## 2. Roles

Four, and the boundaries between them are the whole design.

**The owner.** Approves nothing routine — the supervisor is a full delegate, steered by exception from Remote Control or **#embarch-fleet** on a phone: start, stop, question, redirect ([running the fleet](ops.md) §3–§5; §11 is why that is a real risk and what it buys). Four things stay the owner's and cannot be delegated:

- **Amending a standing rule** — every row §3's table marks **never** for both agents: this doc and the framework's others, every [DOC-*.md](../embarch-doc/DOC-COMPACTION.md), the protocol READMEs, `scripts/` and `.claude/`. `check-ownership.py --supervisor` enforces it. **A supervisor that can rewrite its own constraints has none** — dev-workflow §6's "ends when the repo owner says it ends, and on no other condition" is that property for one rule, and this is it for the class.
- **Anything physical** — plugging in a board, swapping hardware. Unchanged from [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §5's Tier 3.
- **Anything outside the suite's own repos** — a deployed machine, a release, and *writing* to a client firmware repo. **Amended 2026-09-06:** flashing a configured project's board and running studies against it is granted to the fleet (§7); everything else here is unchanged.
- **Latching the pump.** Neither a supervisor nor the fleet starts itself: `fleet start` and `fleet stop` in #embarch-fleet are the owner's. What they start is the *pump*, not each leg — once latched, the listener spawns leg after leg until told to stop ([running the fleet](ops.md) §5). The owner still decides that the fleet runs at all, and closing VS Code still ends it; what he no longer does is start each piece of work by hand.

**The supervisor.** Exactly one runs at a time, ever, and it lives for one leg — four units, then it dies and hands off (§6). It refills the queue when the queue drains, dispatches workers, lands their branches in order, owns every shared suite-level file, executes cross-repo passes itself, and writes its log entries. It designs suite-wide changes and approves them. It runs a `bench` task with its own hands, one at a time (§7), and runs no other worker's task except where §8 says so.

**A worker.** Takes one task, in one repo, on one branch, ships it with its docs, and exits. It holds no state between tasks — everything it learned is in the docs it wrote or it is gone. Not a limitation to work around: it is [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §4's discipline with the escape hatch removed.

**The listener.** One VS Code window, armed with `/fleet start`, that reads #embarch-fleet and spawns things. A **strict dispatcher**: no hands, edits no file, answers no question, runs no build — everything that is work becomes an agent it spawns and relays, which is what lets it live all day beside a fleet whose every other thread dies on purpose. It is **not** the owner's session: that pen, and hardware, stay in a window opened separately ([slack.md](slack.md) §1).

## 3. The ownership map

Branches are the backstop. **This table is the mechanism** — honored, a merge conflict is a bug in the dispatch, not a normal event.

| Path | Worker | Supervisor | Owner |
|---|---|---|---|
| Its own sub-project's code repo | write | write | write |
| Another sub-project's code repo | **never** | write | write |
| `embarch-doc/<its own sub-project>/` | write | write | write |
| `embarch-doc/<another sub-project>/` | **never** | write | write |
| `changelog.d/` (new fragment) | write | write | write |
| `features.d/<its own scope>-*` (new row) | write | write | write |
| `status.d/` (new fragment) | write | write | write |
| [embarch.md](../embarch-doc/embarch.md), [suite/roadmap.md](../embarch-doc/suite/roadmap.md) | **never** | write | write |
| [suite/features.md](../embarch-doc/suite/features.md) — **assembled, never edited** | **never** | **never** | via `build_features.py` |
| [embarch-decision-reversals.md](../embarch-doc/embarch-decision-reversals.md), [embarch-glossary.md](../embarch-doc/embarch-glossary.md), [suite/user-guide.md](../embarch-doc/suite/user-guide.md) | **never** | write | write |
| `tasks/` | claim + close its own | write | write |
| Every [DOC-*.md](../embarch-doc/DOC-PROTOCOL.md), this doc, [running the fleet](ops.md), [the risks](risks.md), [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md), `CLAUDE.md` | **never** | **never** | write |
| `tasks/README.md`, `inbox/README.md`, `changelog.d/README.md`, `status.d/README.md`, `features.d/README.md` | **never** | **never** | write |
| `scripts/`, `.claude/` | **never** | **never** | write |
| Hardware (probe, DUT, dev-bench, live Core) | **never** | a `bench` task only, serialized (§7) | write |

The three "never" rows a worker most wants to break are the shared suite-level docs, and [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 explicitly tells it to edit them. §9 is the replacement.

**A table of filenames drifts from what it means to protect.** `scripts/` read `write` here while `check-ownership.py` had always rejected it — the script was right, so the table was the stale copy. Two more went missing, and `fleet.toml`'s `reserved` list records both beside the entries that fix them. **The script is the enforcement; this table is its description**, and the script wins when they disagree. **The next split is loud:** `--supervisor` also asserts every tracked top-level `*.md` is classified reserved or fleet-writable, so a doc from a [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md) split fails until someone decides which.

## 4. The task queue

`tasks/<sub-project>/NNN-slug.md`, committed to `main` in this repo. Format and claim protocol: [tasks/README.md](../embarch-doc/tasks/README.md).

A queue in git rather than the supervisor's head buys three things: two supervisor runs cannot dispatch one task, a task survives the thread working it, and the reason it exists is written beside it instead of re-derived from the roadmap every batch.

**The supervisor refills the queue itself**, from [suite/roadmap.md](../embarch-doc/suite/roadmap.md)'s Now/Next, every sub-project's `open.md`, and [embarch-decision-reversals.md](../embarch-doc/embarch-decision-reversals.md)'s unaddressed follow-ups. Nobody hand-writes a backlog. **Refill runs when the queue is below its low-water mark** — `queue-status.py --refill-owed`, which fires on fewer dispatchable tasks than `units_per_leg`, or fewer distinct *scopes* than the wave size, since one-task-per-sub-project is per slot. Not at the top of every leg: sweeping eight `open.md` files every twenty minutes to serve a queue that already has work is pure cost. **It used to fire at zero, and zero was too late**: over the 7.2 h run ending 2026-09-06 the queue held one or zero dispatchable tasks for 53% of it, so the sweep meant to feed the wave only ran after it had starved. **Draining `inbox/` is the exception and runs every leg** — it is cheap and the only thing that files a drop, so gating it on the count lets a lone drop suppress its own drain.

**What counts as dispatchable is `scripts/queue-status.py`, never a `State:` grep — and the listener and a leg ask it different questions.** A leg asks *after* step 0, when recovery has already released the claims of workers that died with their supervisor, so a claim still standing is one to respect. The listener asks *before* recovery, so it passes `--no-supervisor` and a standing claim counts as recoverable work — sound because it has just established with `ListAgents` that no supervisor is alive, and [tasks/README.md](../embarch-doc/tasks/README.md) settles staleness by the process tree, not a timeout. Restating that count in prose stalled the fleet for five hours on 2026-09-03. The script owns the predicate; the timeout survives inside it as `--stale-after`, the backstop for a supervisor alive but wedged. The queue is therefore a *view* of the docs, true only as long as closing a task also updates the doc it came from — §5's contract.

## 5. The worker contract

A worker gets one task file and this contract. It must:

1. **Work in two worktrees, on one branch name.** Almost every task changes both its code repo *and* `embarch-doc/<sub-project>/`, so a worker gets a branch `agent/<sub-project>/<NNN-slug>` in **both**, landed together (§10). Not bookkeeping: a shipped change whose docs sit on an unmerged branch is the drift [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 exists to prevent. Six workers branching `embarch-doc` at once is safe *because* of §3 — their paths are disjoint by construction. Both worktrees live under `embarch/.worktrees/<repo>/<NNN-slug>/`, **outside every repo tree**, created and deleted by the supervisor (§6). Never inside `.claude/worktrees/`: a repo checked out inside itself made a naive scan find six GATT service blocks instead of three (`embarch-study-designer` decision 57).
2. **Stay inside its ownership row** (§3). If the task needs another repo, it stops and reports that — it does not reach across. A task needing two repos was mis-filed, and §8 owns the fix. **Never `cargo fmt`**: unenforced ([embarch.md](../embarch-doc/embarch.md) §5), and here you own the whole tree, so nothing stops an 87-file diff.
3. **Never touch hardware** (§7).
4. **Design freely within its own sub-project.** A new `decisions.md` entry scoped to one sub-project needs nobody's approval — the owner's call, and it stands. Number it per [DOC-CONVENTIONS.md](../embarch-doc/DOC-CONVENTIONS.md); numbers are permanent.
5. **Update its own four files** — `spec.md`, `decisions.md`, `open.md`, `interfaces.md` — per [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §4–5. Edit the body; never append.
6. **Drop a `changelog.d/` fragment**, and a `status.d/` fragment for every suite-level fact it made false (§9). It does not edit the suite-level docs.
7. **Pass the gate** (§10) before saying it is done — including `scripts/check-ownership.py --scope <sub-project>`, the mechanical form of rule 2. Green, or it reports red and does not claim otherwise.
8. **Close its task file** and push its branch. It never merges.

A worker that cannot finish writes what it found into the task file and exits. A half-done branch with an honest note is worth more than a finished-looking one.

## 6. The leg, the pump, and the relay

Three words, and keeping them apart is most of understanding how this runs.

- A **unit** is one task: one worker, gated independently by the supervisor, landed, folded, logged. The smallest thing the fleet finishes.
- A **leg** is one supervisor's whole life: recover, refill if the queue is dry, then keep the budget's wave size of workers in flight — landing, folding and logging each as it reports — until **four units** are done. Then it dies.
- The **pump** is the latch the owner holds. While it is on, a leg's death wakes the listener, which spawns the next leg with the previous one's log entries as its handoff. That chain is the **relay**.

**A leg is a rolling wave, not a batch.** Nothing waits for everything: a finished worker's branches land, its fragments fold, its entry is written, and another task starts in the freed slot. The five-phase batch it replaced had a barrier at the end, so the slowest worker's runtime was dead time for every other slot.

The steps, in order, per leg:

0. **Take a checkout, then recover.** A leg works in its own worktree of this
   repo, not the checkout the owner uses — two actors in one working tree is how
   legs 004 and 005 swept his `changelog.d` fragments into their folds, and a
   rebase in a tree he has dirtied fails outright. **Detached, never on `main`**:
   `git worktree add --detach`, push with `HEAD:main` — git refuses a second
   worktree on a branch the owner's checkout holds, and two worktrees sharing
   one branch ref is worse than the problem this solves. Every fold advances
   `main`, so his HEAD moves while his index and working tree stay at the leg's start commit: leg 007 left his
   checkout holding **a staged inverse of the whole leg**, where a `git commit`
   would have reverted four units. That staleness is also why a reviewer must be
   handed a worktree path (§10). `inbox/` is the exception: drops are gitignored,
   so they live only in the main checkout and are read there by absolute path.
   A previous leg may have been killed outright — closing VS Code is the kill switch and is expected to be used. Abort any in-progress merge or rebase, reclaim every stale claim, and delete dead worktrees **before** anything else; the rule, and what a kill leaves behind, is [running the fleet](ops.md) §3. Then read the newest [supervisor-log.md](supervisor-log.md) entries: under the relay a predecessor this leg has no memory of wrote them, and they are the only thing that crossed the boundary.
1. **Refill, if the queue is below its low-water mark** (§4). Drain `inbox/`, then sweep the roadmap, every `open.md`, and the reversals follow-ups; write any new task files. Reconcile: a task whose source doc no longer says the thing is closed, not dispatched. **If refill also finds nothing**, dream three proposals and end the leg ([running the fleet](ops.md) §7) — do not pick one, and do not write a dreamt item into the queue.
2. **Select and set up**, per free slot. `scripts/usage-budget.py --suggest` sets how many may be in flight ([running the fleet](ops.md) §2); it, not the cap, is the number. At most one task per sub-project, `Hardware: none`/`verify-only` only — `bench` is the leg's own (§7). Claim it *before* dispatch — that commit is what stops a double-dispatch — **one commit per task, pushed to `origin/main` before the branch is created**, so a reclaim reverts exactly one task and the listener sees each claim as it happens. It used to also be what kept a worker's ownership check honest and was never enough; `check-ownership.py` now derives its own base — the furthest-forward merge-base between HEAD and `main`/`origin/main` — so neither a batched claim (leg 008) nor a stale worktree `main` (leg 010) can put an unwritten path in a worker's diff. **A red ownership check is now evidence, not noise**, and a supervisor who had learned to discount it was the real cost. Then create the branch and both worktrees under `embarch/.worktrees/`, outside every repo tree and never inside `.claude/worktrees/` (`embarch-study-designer` decision 57).
3. **Dispatch** as a background worker agent, without blocking on the one before it. Re-check the budget before refilling a slot, not only at the leg's start.
4. **Land, fold and log the moment a worker reports.** Run the gate (§10) independently — never trust the worker's word for green — then merge both branches in §10's order, rebase the rest onto the new `main`, consume its `status.d/` fragments, and prepend its entry to the log (§11), as one commit per unit. **A rebased branch's tip is never an ancestor of `main`** even when its content landed, so `merge-base --is-ancestor` cannot prove a rebased branch is safe to delete — check the commit it rebased *to*. **Record every merge commit's SHA**: no merge commit and no branch name survives, so the SHA is the only handle a revert has (§11). Delete a worker's worktrees once its branches land or are abandoned; `fold-commit.py` deletes the *pushed* branches itself, a fold late, once `git cherry` proves them on `origin/main`.

Then start another unit, until four are done.

**Landing and folding are serialized by there being one actor, not a lock.** The supervisor is the only thing that touches `main`, a unit's fold is one commit, and two folds never interleave — the property the old phase 5 got from being one phase, kept while dropping the barrier. It is also why wave-size *worker* concurrency is safe while wave-size *supervisor* concurrency would not be, and why §7's hardware lane is the supervisor's.

**Why four units.** A supervisor running until the pump stopped would accumulate every unit and eventually auto-compact — a summarized transcript instead of a written handoff, at the moment the fleet is deepest into unattended work ([running the fleet](ops.md) §8). Four keeps a leg's context batch-sized while leaving the handoff a small part of the work, and needs no new machinery: step 0 already reads the newest log entries cold.

**A leg ends early, saying why, on** a `fleet stop`, a budget HOLD, or an empty queue.

**A red gate blocks the task; the leg keeps going.** The owner's call, progress over caution: the task goes to `blocked` with the reason and the next unit starts. The cost is that a systemically broken `main` blocks several tasks in a row before anyone notices, so a supervisor seeing the same failure twice must say so loudly rather than continue quietly.

## 7. Hardware: workers never touch it; the supervisor may, one at a time

There is one `hw_lock`, one study in flight (rejected with `409`, deliberately no queue), one live Core, and one DUT + dev-bench pair (`embarch-topology` decision 10). Four workers cannot share that, and the `409` is no coordination mechanism — it is a refusal an agent misreads as a bug in its own change.

So: **workers are host-side only.** Build, `cargo test`, `clippy --all-targets -- -D warnings`, host unit tests, docs, design. A worker whose change can only be verified on hardware writes a **hardware-verification debt** into the task file and ships the host-side half; the supervisor collects those into its log entry (§11).

**The supervisor may run hardware, granted by the owner 2026-09-06.** It was barred for a worker's reason plus one more: it is unattended, and [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §5's Tier 2/3 autonomy was granted to a session the owner sat in front of. What replaced the bar is narrower than lifting it. A **`bench` task**, and a **`toolchain`** one (host-side, but needing a toolchain no worktree can carry), is executed by the leg **itself**, never dispatched, **at most one at a time** — needing no lock, because exactly one supervisor exists; the shape §8 uses for a cross-repo pass, for the same reason. It **validates the roles a task names before starting**, and an unattached board leaves the task `open`, never `blocked` — boards come back. [tasks/README.md](../embarch-doc/tasks/README.md) carries the rest.

**The client-repo line moved with it, and only this far.** §2 reserves anything outside the suite's own repos; the grant is to **flash a configured project's board and run studies against it**. *Writing* to a client repo stays reserved — no commit, no source edit, no release. The fleet exercises EmbArch against real hardware; it does not develop someone else's firmware.

Hardware is serial by construction: it adds depth, not width, and most of what blocks this suite is still hardware-gated.

## 8. Cross-repo changes: the supervisor does them itself

A schema change touching five repos must land as one sequenced pass, shared crate first, each repo's `main` compiling on its own ([embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6). One-thread-per-repo cannot do that: a half-landed wire change is the worst failure this suite has.

So a task that spans sub-projects is **never dispatched to a worker.** The supervisor executes it itself, sequenced, after designing it — which under full delegation it may do without asking. Workers stay single-repo, always.

So the supervisor's own hands do the riskiest work in the suite, unattended. It therefore **announces before it starts**: a Slack post naming what it is about to do, the task parked rather than begun, the leg's other units running normally, and a reply able to cancel it for 30 minutes ([running the fleet](ops.md) §4) — a veto that costs the leg nothing, which is why it is this rather than a delay. **A leg that ends first leaves the task parked with the announcement's `ts`** and its successor completes the window; the relay would otherwise reset the clock every twenty minutes and a `suite` task would never run.

## 9. Shared suite-level docs: `status.d/` fragments

[DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 requires the suite-level facts to move in the same pass as the change. With one engineer that is a rule against drift; with four workers it puts four agents into [embarch.md](../embarch-doc/embarch.md) §3's table at once.

The fix is the one `changelog.d/` already proved: **one file per pending edit, no shared file touched.** [suite/features.md](../embarch-doc/suite/features.md) went further on 2026-09-04 and became *assembled* rather than folded — a worker writes `features.d/<its own scope>-<NNN>-<slug>.md` and `build_features.py` builds the table, so a feature's row lands in the commit that earned it rather than as a request somebody has to honour. A worker writes `status.d/<scope>-<slug>.md` naming the target doc and the fact that changed; the supervisor folds a worker's fragments as it lands that worker's branches, and deletes them (§6 step 4). Format: [status.d/README.md](../embarch-doc/status.d/README.md).

The rule DOC-PROTOCOL §5 protects is unchanged — the suite-level docs still must not disagree with a sub-project's — it just takes two actors and two commits. The window in which they *can* disagree is **one unit**, because folding is part of landing it (§6). **A unit that lands with its fragments still sitting in `status.d/` has failed**, whatever else it shipped.

## 10. The merge gate and merge order

Run by the worker, then **re-run independently by the supervisor** on the merge result — not on the branch:

- `cargo build`, `cargo test`, `cargo clippy --all-targets -- -D warnings` in the touched repo — which reach **only the packages they select**, never an in-repo non-member crate ([embarch.md](../embarch-doc/embarch.md) §5). **The native Windows build is a debt, not a gate item**, unrunnable from a worktree twice over — `hidapi`'s `build.rs` wants an MSVC `cc` WSL lacks, and Windows `cargo.exe` cannot follow a worktree's Linux symlinks to its path-dep siblings. It takes 52 s from the main checkout [2026-09-06], so a unit touching `embarch-core` records the debt; the owner runs it.
- The whole `embarch-doc` gate as **one command, `python3 scripts/check-docs.py`** — **which names its own checks, and this doc does not.** The enumeration here went stale twice in two days, and a supervisor triaging a red against a short list is triaging blind. `CHECKS` in that file is the list; no count is restated anywhere.
- **`check-client-names.py --repo <path>` on the code repo too**, alongside `cargo`. The wrapper covers only `embarch-doc`, a fifth of the suite's bytes, and 2026-09-04's leak was mostly on the other side. Per repo, never one pass over the siblings — a leg and a worker run from `embarch/.worktrees/`, where a sibling walk finds other worktrees. It reads a denylist kept outside every repo and **never prints what it matched**; its header carries the gaps it leaves.
- **`build_features.py --check` validates the fragments only.** The byte-equality assertion `--check-assembled` is deliberately **not** in a branch gate: `suite/features.md` is `never` for a worker in §3's table, so asserting it per branch left a feature-shipping worker unable to be green on this and `check-ownership.py` at once (leg 009, twice). It is asserted on `main`, by CI and the fold.
- **`check-ownership.py --scope <sub-project>`** on both branches — the mechanical form of §3. Either `core` or `embarch-core` is accepted; **`suite` is refused outright, because a cross-repo change is §8's.** Without it §3 is prose nothing reads: a worker's edit to [embarch.md](../embarch-doc/embarch.md)'s status table is *plausible by construction*, so `check-staleness.py` (which only flags a row disagreeing with a sub-project doc) passes it, and the collision §9 prevents happens anyway.

That is [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6's standard applied per branch, not per commit. Nothing here licenses a lower bar because an agent wrote it.

**A reviewer reads for intent, alongside landing, and gates no merge.** When a
unit's branches merge, the supervisor spawns an `embarch-reviewer` on the diff
against that sub-project's decisions and the reversals index. Findings land in
`inbox/` and in the unit's log entry; a confirmed contradiction is reverted by
SHA — the first thing that ever uses the SHAs §11 requires.
**Merge-on-green is unchanged**: a blocking reviewer would make every unit a
two-agent serial dependency, and the owner chose progress over caution here as
elsewhere.

**A reviewer reads the leg's worktree, or a SHA — never the tree it is spawned
into.** It lands in the owner's checkout, which a leg never advances, so a
relative read answers about the commit the leg *started* at: one unit stale on
its first review, three on its last, and it never errors. What that produces is a
confidently wrong **`pre-existing`** label on precisely the contradictions this
leg introduced, which is the one class §10 exists to catch. So the supervisor
passes both worktree paths in the spawn, and a reviewer given neither says so
rather than reading what is under it.

**It is the last thing the fold waits for, and that is not the same as gating.**
"Spawn it and never wait" was the rule until 2026-09-05 and was incoherent with
§11: the `**Reviewer:**` line rides *inside* the fold commit, which lands a
minute or two after the merge, while a reviewer reports in ninety seconds to
three. The line was required to state a fact that did not exist yet, and three
of leg 011's were true by luck. So the merge does not wait and the *entry* does:
spawn at merge, do the rest of the fold, collect the reviewer immediately before
writing the entry. The wait is under a minute against a twenty-minute worker,
and it is what makes the tally evidence rather than a guess.

**A reviewer does not count against the worker wave.** The rule that said it did
was self-defeating: ninety seconds of reading cost a whole slot out of a
DEGRADED wave of two — this machine's steady state — so eight entries in,
one had run and six were skipped for the wave alone. **The question the tally
exists to answer could not be answered under the rule governing it.** Skip only
on a HOLD, a recent 429, or a leg ending at its unit cap where the reviewer would
outlive it, and **the log says which**: "no findings" and "no reviewer ran" are
different facts.

**The gate is mechanical and catches broken, not wrong.** The one judgement the supervisor adds: read the diff before merging when the change touches a shared crate (`embarch-study-designer`, `embarch-topology`, and `embarch-core-client` — inside `embarch-api` but path-depended on by `embarch-ui`, so an `api` worker can change `ui`'s dependency without owning `ui`), a wire type, or retires a decision. That is where passing and correct diverge most expensively; everything else merges on green.

**Merge order** is shared crates first, then consumers, then `embarch-doc` — §6's cross-repo sequencing applied to a leg's independent passes. Within a tier, oldest branch first, so nothing sits.

## 11. The log

Canon is the doc, Slack the ping.

**One entry per unit**, prepended to [supervisor-log.md](supervisor-log.md), newest first: what it **decided**, what merged with its SHAs, what blocked and why, and any hardware debt. Per unit, not per leg: a leg can be killed at any moment, and an entry written at the end does not exist for the leg that was.

**The entry goes in the fold commit, not after it, and a unit that lands without one has failed** — §9's rule for an unfolded `status.d/` fragment, same reason. A separate step leaves a window in which a unit is landed and unlogged, and `api/003` landed in it on 2026-09-03: that fold did every other part correctly, never touched this log, and the handoff is gone. One commit makes the state impossible rather than detectable. What *shipped* is already in the workers' `changelog.d` fragments, assembled into `history/<scope>.md`; the log does not restate it.

**Folded daily, by a subagent, with a script.** On its first unit after local midnight a supervisor folds the previous day's entries into one dated entry, keeping every SHA, debt and `**Reviewer:**` line. Without it, per-unit entries hit the roll every few days and the handoff shortens — the opposite of what a relay needs.

**The heading's date and time are the fold's wall clock, and `fold-commit.py` sets them** — never by hand, never a guess. 41 of 63 entries once ran over 5 min ahead of the fold that wrote them, the worst by 63. The day-fold groups by that date, so one written 23:50 and stamped 00:15 lands in the wrong day, silently.

**Neither the subagent nor the script is decoration.** `scripts/fold-day.py <yyyy-mm-dd>` extracts the day and a ledger of what it carries; `--apply` splices the folded entry back over exactly those and **refuses one that dropped a SHA, a debt or a reviewer line.** The alternative cost leg 010 ~35 K tokens re-emitting text nobody meant to change, any transcription error corrupting this file silently. It goes to an `embarch-log-folder` subagent rather than the leg — **a leg is bounded at four units precisely so it does not accumulate context** — and still lands in that unit's `fold-commit.py` commit.

**Every day but the two newest rolls into `log-archive/`** — `scripts/fold-day.py --roll`, which never splits a day. Two, because step 0 reads today and the day before; *this* repo's `log-archive/`, not the instance's `history/archive/`, because this log lives here. **There is deliberately no byte line**: two were written and neither was reachable, so the quantity was wrong — a day's size is the fold's job, and this counts days.

Slack gets **one line per unit** as it happens — dispatched, landed with its SHA, or blocked with the reason — and nothing on an ordinary leg end: under the relay legs end constantly and one per leg is a pager.

**This is the review surface, and under a full delegate the only one.** Read after the fact, so it must be honest about what was decided, not just what shipped — a suite-wide design the supervisor approved on the owner's behalf is the most important line it will write, and belongs at the top of its entry, not under the merge list.

## 12. Known risks

Stated rather than designed away, in [risks.md](risks.md), split out when this doc hit its size cap. No count here, for §10's reason. The two worth knowing first: **almost no diff is read for intent before it lands**, and **nobody watches the relay.**

## 13. Running it

Arming the listener, latching the pump, sizing a leg against the usage limits, watching it from a phone, stopping it: [running the fleet](ops.md).
