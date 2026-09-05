# EmbArch: parallel agent work

**Status:** active, 2026-09-03. Three legs have run under it (see [supervisor-log.md](supervisor-log.md)); the risks are in [risks.md](risks.md). The relay in §6 is new as of 2026-09-03 and has not run.

## 1. Why this exists

Every rule in this suite was written for one engineer in one session. [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6 says commit straight to `main` and justifies it *by* that assumption — "this suite has one engineer … there is nothing to collide with". [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 tells whoever ships a change to update the suite-level status tables in the same pass, which is safe exactly once per moment. Both stop being safe the moment four agents work at once.

So: **a supervisor thread keeps 4–6 short-lived worker threads in flight, each owning one sub-project, and lands their work itself.** A supervisor runs a bounded **leg** — four tasks — and a listener thread spawns its successor, so the fleet outlives any one supervisor's context (§6). This doc is what replaces the single-session assumption for those threads. It governs background threads only — the owner's own interactive sessions keep working exactly as before, on `main`, under §6 unchanged.

The design principle throughout: **prevent collisions structurally; do not resolve them.** A supervisor that merges two workers' edits to the same table is guessing at two intents it never held. Every rule below exists to make sure that merge never has to happen.

## 2. Roles

Four, and the boundaries between them are the whole design.

**The owner.** Approves nothing routine — the supervisor is a full delegate, and steers by exception, and can start, stop, question or redirect the fleet from Remote Control or **#embarch-fleet** on a phone ([running the fleet](ops.md) §3–§5) (§11 is why that is a real risk and what it buys). Four things stay the owner's and cannot be delegated:

- **Amending a standing rule** — this doc, [running the fleet](ops.md), [the risks](risks.md), [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6, [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md), [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md), `CLAUDE.md`, the four protocol READMEs, `scripts/` and `.claude/` — §3's table is the full list and `check-ownership.py --supervisor` is what enforces it. A supervisor that can rewrite its own constraints has none. Dev-workflow §6 already says its own rule "ends when the repo owner says it ends, and on no other condition"; this is that property stated once for the whole class.
- **Anything physical** — plugging in a board, swapping hardware. Unchanged from [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §5's Tier 3.
- **Anything outside the suite's own repos** — a client firmware repo, a deployed machine, a release.
- **Latching the pump.** Neither a supervisor nor the fleet starts itself: `fleet start` and `fleet stop` in #embarch-fleet are the owner's. **Amended 2026-09-03:** what they start is the *pump*, not each leg — once latched, the listener spawns leg after leg until told to stop ([running the fleet](ops.md) §5). They still decide that the fleet runs at all, and closing VS Code still ends it; what they no longer do is start each piece of work by hand.

**The supervisor.** Exactly one runs at a time, ever, and it lives for one leg — four units, then it dies and hands off (§6). It refills the queue when the queue drains, dispatches workers, lands their branches in order, owns every shared suite-level file, executes cross-repo passes itself, and writes its log entries. It designs suite-wide changes and approves them. It **never** touches hardware and never runs a worker's task itself except where §8 says so.

**A worker.** Takes one task, in one repo, on one branch, ships it with its docs, and exits. It holds no state between tasks — everything it learned is in the docs it wrote or it is gone. That is not a limitation to work around; it is [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §4's discipline with the escape hatch removed.

**The listener.** One VS Code window, armed with `/fleet start`, that reads #embarch-fleet and spawns things. A **strict dispatcher**: no hands, edits no file, answers no question out of the docs, runs no build — everything that is work becomes an agent it spawns and relays, which is what lets it live all day beside a fleet whose every other thread dies on purpose. It is **not** the owner's session: the pen for standing rules, `scripts/`, `.claude/`, hardware and `inbox/` drops stays in an ordinary window opened separately ([running the fleet](ops.md) §5.1).

## 3. The ownership map

Branches are the backstop. **This table is the actual mechanism** — if it is honored, a merge conflict is a bug in the dispatch, not a normal event.

| Path | Worker | Supervisor | Owner |
|---|---|---|---|
| Its own sub-project's code repo | write | write | write |
| Another sub-project's code repo | **never** | write | write |
| `embarch-doc/<its own sub-project>/` | write | write | write |
| `embarch-doc/<another sub-project>/` | **never** | write | write |
| `changelog.d/` (new fragment) | write | write | write |
| `status.d/` (new fragment) | write | write | write |
| [embarch.md](../embarch-doc/embarch.md), [suite/features.md](../embarch-doc/suite/features.md), [suite/roadmap.md](../embarch-doc/suite/roadmap.md) | **never** | write | write |
| [embarch-decision-reversals.md](../embarch-doc/embarch-decision-reversals.md), [embarch-glossary.md](../embarch-doc/embarch-glossary.md), [suite/user-guide.md](../embarch-doc/suite/user-guide.md) | **never** | write | write |
| `tasks/` | claim + close its own | write | write |
| [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md), [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md), this doc, [running the fleet](ops.md), [the risks](risks.md), [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md), `CLAUDE.md` | **never** | **never** | write |
| `tasks/README.md`, `inbox/README.md`, `changelog.d/README.md`, `status.d/README.md` | **never** | **never** | write |
| `scripts/`, `.claude/` | **never** | **never** | write |
| Hardware (probe, DUT, dev-bench, live Core) | **never** | **never** | write |

The three "never" rows a worker will most want to break are the shared suite-level docs, and [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 explicitly tells it to edit them. §9 is the replacement.

**A table of filenames drifts from what it means to protect.** `scripts/` read `write` for the supervisor while `check-ownership.py` had always rejected it — the script was right, so the table was the stale copy. The rest went missing two ways. [The risks](risks.md) is **reserved content that stopped being reserved by moving**: §12 of this doc until the size cap split it out, and the check names files. The four protocol READMEs were never named, because each documents a rule the fleet runs under while sitting inside a directory the fleet legitimately writes — `tasks/README.md` carries the staleness protocol `queue-status.py` implements, so a leg editing it edits its own dispatch predicate. **The script is the enforcement; this table is its description**, and the script wins when they disagree. **The next split is loud:** `--supervisor` also asserts every tracked top-level `*.md` is classified reserved or fleet-writable, so a doc from a [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md) split fails until someone decides which.

## 4. The task queue

`tasks/<sub-project>/NNN-slug.md`, committed to `main` in this repo. Format and the claim protocol: [tasks/README.md](../embarch-doc/tasks/README.md).

A queue that lives in git rather than in the supervisor's head buys three things worth the extra doc kind: two supervisor runs cannot dispatch the same task, a task survives the thread that was working it, and the reason a task exists is written down next to it instead of being re-derived from the roadmap every batch.

**The supervisor refills the queue itself**, from [suite/roadmap.md](../embarch-doc/suite/roadmap.md)'s Now/Next, every sub-project's `open.md`, and [embarch-decision-reversals.md](../embarch-doc/embarch-decision-reversals.md)'s unaddressed follow-ups. No one hand-writes a backlog. **Refill runs only when nothing is dispatchable**, not at the top of every leg: under the relay a leg begins every twenty minutes or so, and sweeping eight `open.md` files that often to serve a queue that already has work is pure cost. **Draining `inbox/` is the exception and runs every leg** — it is cheap, and it is the only thing that files a drop, so gating it on the count lets a lone drop suppress its own drain.

**What counts as dispatchable is `scripts/queue-status.py`, never a `State:` grep — and the listener and a leg ask it different questions.** A leg asks *after* step 0, when recovery has already released the claims of workers that died with their supervisor, so a claim still standing is one to respect. The listener asks *before* any recovery has run, so it passes `--no-supervisor` and a standing claim counts as recoverable work — which is sound precisely because it has just established with `ListAgents` that no supervisor is alive, and [tasks/README.md](../embarch-doc/tasks/README.md) settles staleness by the process tree rather than by a timeout. The count had been restated in prose in four places, all of them saying "State is open" and all of them therefore disagreeing with that rule: on 2026-09-03 the listener read `tasks/umbrella/001` as nothing at all while it sat one commit from dispatchable. The script owns the predicate; the timeout survives inside it as `--stale-after`, the backstop for a supervisor alive but wedged. The queue is therefore a *view* of the docs, which is only true as long as closing a task also updates the doc the task came from — §5's contract.

## 5. The worker contract

A worker is handed exactly one task file and this contract. It must:

1. **Work in two worktrees, on one branch name.** Almost every task changes both its code repo *and* `embarch-doc/<sub-project>/`, so a worker gets a branch called `agent/<sub-project>/<NNN-slug>` in **both** repos, and the supervisor lands both together (§10). Not bookkeeping: a shipped change whose docs sit on an unmerged branch is exactly the drift [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 exists to prevent. Six workers branching `embarch-doc` at once is safe *because* of §3 — their paths are disjoint by construction. Both worktrees live under `embarch/.worktrees/<repo>/<NNN-slug>/`, **outside every repo tree**, created and deleted by the supervisor (§6). Never inside `.claude/worktrees/`: a repo checked out inside itself is what made a naive source scan find six GATT service blocks instead of three (`embarch-study-designer` decision 57).
2. **Stay inside its ownership row** (§3). If the task turns out to need another repo, it stops and reports that — it does not reach across. A task that needed two repos was mis-filed, and §8 owns the fix.
3. **Never touch hardware** (§7).
4. **Design freely within its own sub-project.** A new `decisions.md` entry scoped to one sub-project needs nobody's approval — that was the owner's call and it stands. Number it per [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §7.2; numbers are permanent.
5. **Update its own four files** — `spec.md`, `decisions.md`, `open.md`, `interfaces.md` — per [DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §4–5. Edit the body; never append.
6. **Drop a `changelog.d/` fragment**, and a `status.d/` fragment for every suite-level fact its change made false (§9). It does not edit the suite-level docs.
7. **Pass the gate** (§10) before it says it is done — including `scripts/check-ownership.py --scope <sub-project>`, the mechanical form of rule 2. Green, or it reports red and does not claim otherwise.
8. **Close its task file** and push its branch. It does not merge.

A worker that cannot finish writes what it found into the task file and exits. A half-done branch left with an honest note is worth more than a finished-looking one.

## 6. The leg, the pump, and the relay

Three words, and keeping them apart is most of understanding how this runs.

- A **unit** is one task: one worker, gated independently by the supervisor, landed, folded, logged. The smallest thing the fleet finishes.
- A **leg** is one supervisor's whole life: recover, refill if the queue is dry, then keep the budget's wave size of workers in flight — landing, folding and logging each as it reports — until **four units** are done. Then it dies.
- The **pump** is the latch the owner holds. While it is on, a leg's death wakes the listener, which spawns the next leg with the previous one's log entries as its handoff. That chain is the **relay**.

**A leg is a rolling wave, not a batch.** Nothing waits for everything: a finished worker's branches land, its fragments fold, its log entry is written, and another task starts in the freed slot at once. The five-phase batch this replaces had a barrier at the end, making the slowest worker's runtime dead time for every other slot.

The steps, in order, per leg:

0. **Take a checkout, then recover.** A leg works in its own worktree of this
   repo, not in the checkout the owner uses — two actors in one working tree is
   how legs 004 and 005 swept his `changelog.d` fragments into their folds, and
   a rebase in a tree he has dirtied fails outright. **Detached, never on
   `main`**: `git worktree add --detach`, and push with `HEAD:main`. A worktree
   that *checks out* `main` needs `--force` — git refuses precisely because the
   owner's checkout holds that branch — and two worktrees sharing one branch ref
   is worse than the problem this step solves. Every fold advances `main`, so
   the owner's HEAD moves while his index and working tree stay at the leg's
   start commit: leg 007 left his checkout holding **a staged inverse of the
   whole leg**, 25 paths, where a `git commit` would have reverted four units
   and looked like ordinary work. `inbox/` is the exception:
   drops are gitignored, so they live only in the main checkout and are read
   there by absolute path. A previous leg may have been killed outright — closing VS Code is the owner's kill switch and is expected to be used ([running the fleet](ops.md) §3). Abort any in-progress merge or rebase, reclaim every stale claim, and delete dead worktrees **before** anything else. The exact rule and what a kill can leave behind: [running the fleet](ops.md) §3. Then read the newest [supervisor-log.md](supervisor-log.md) entries: under the relay they were written by a predecessor this leg has no memory of, and they are the only thing that crossed the boundary.
1. **Refill, only if nothing is dispatchable.** Drain `inbox/`, then sweep the roadmap, every `open.md`, and the reversals follow-ups; write any new task files. Reconcile: a task whose source doc no longer says the thing is closed, not dispatched. **If refill also finds nothing**, dream three proposals and end the leg ([running the fleet](ops.md) §7) — do not pick one, and do not write a dreamt item into the queue.
2. **Select and set up**, per free slot. `scripts/usage-budget.py --suggest` sets how many may be in flight ([running the fleet](ops.md) §2); it, not the cap, is the number. At most one task per sub-project, from `Hardware: none`/`verify-only` only. Claim it on `main` *before* dispatch — that commit is what stops a double-dispatch — then create the branch and both worktrees under `embarch/.worktrees/`, outside every repo tree and never inside `.claude/worktrees/` (`embarch-study-designer` decision 57).
3. **Dispatch** as a background worker agent, without blocking on the one before it. Re-check the budget before refilling a slot, never only at the start of the leg.
4. **Land, fold and log the moment a worker reports.** Run the gate (§10) independently — do not trust the worker's word for green — then merge both of its branches in the order §10 fixes, rebase the rest onto the new `main`, consume its `status.d/` fragments, and prepend its entry to the log (§11), as one serialized commit per unit. **A rebased branch's tip is never an ancestor of `main`** even when its content landed, so `merge-base --is-ancestor` cannot prove a rebased branch is safe to delete — check the commit it rebased *to*. Batch 003 correctly refused to delete one on this basis. **Record every merge commit's SHA**: there is no merge commit and no branch name left afterwards, so the SHA is the only handle a revert has (§11). Delete a worker's worktrees once its branches have landed or been abandoned.

Then start another unit, until four are done.

**Landing and folding are serialized by there being one actor, not by a lock.** The supervisor is the only thing that touches `main`, a unit's fold is one commit, and two folds never interleave — the property the old phase 5 got from being a single phase, kept while dropping the barrier. It is also why wave-size *worker* concurrency is safe while wave-size *supervisor* concurrency would not be.

**Why four units.** A supervisor that ran until the pump stopped would accumulate every unit it had run and eventually auto-compact — a summarized transcript instead of a written handoff, at the moment the fleet is deepest into unattended work ([running the fleet](ops.md) §8). Four keeps a leg's context batch-sized while leaving the handoff a small part of the work, and needs no new machinery: step 0 already reads the newest log entries cold, and after a relay handoff that is literally true.

**A leg ends early, and says why, on** a `fleet stop`, a budget HOLD, or a drained queue.

**A red gate blocks the task; the leg keeps going.** The owner's call, chosen for progress over caution: the task goes to `blocked` with the reason and the next unit starts. The cost is that a systemically broken `main` blocks several tasks in a row before anyone notices, so a supervisor seeing the same failure twice must say so loudly rather than continue quietly.

## 7. Hardware: workers never touch it

There is one probe, one `hw_lock`, one study in flight (rejected with `409`, deliberately no queue), one live Core, and one DUT + dev-bench pair (`embarch-topology` decision 10). Four workers cannot share that, and Core's `409` is not a coordination mechanism — it is a refusal an agent will misread as a bug in its own change.

So: **workers are host-side only.** Build, `cargo test`, `clippy --all-targets -- -D warnings`, host unit tests, docs, design. Anything needing a board — a flash, a study, a serial log, a deploy — is not a task. A worker that discovers its change can only be verified on hardware writes that into the task file as a **hardware-verification debt** and ships the host-side half; the supervisor collects those into its log entry (§11), and they are worked in the owner's own session.

The supervisor does not touch hardware either. It is unattended by design, and [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §5's Tier 2/3 autonomy was granted to a session the owner was sitting in front of.

This is a real cap on what parallelism buys here: most of what currently blocks this suite is hardware-gated. The threads are for the large remainder that is not.

## 8. Cross-repo changes: the supervisor does them itself

A schema change touching five repos must land as one sequenced pass, shared crate first, each repo's `main` compiling on its own ([embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6). One-thread-per-repo structurally cannot do that: a half-landed wire change is the worst failure mode this suite has.

So a task that spans sub-projects is **never dispatched to a worker.** The supervisor executes it itself, in one session, sequenced — after designing it, which under the full-delegate model it may do without asking. Workers stay single-repo, always.

Practically this means the supervisor's own hands do the riskiest work in the suite while unattended. So it **announces before it starts**: a Slack post naming what it is about to do, the task parked rather than begun, the leg's other units running normally, and a reply able to cancel it for the next 30 minutes ([running the fleet](ops.md) §4) — a veto that costs the leg nothing, which is why it is this rather than a delay. **If a leg ends before the window closes it leaves the task parked with the announcement's `ts`** and the next leg completes the window, or the relay would reset the clock every twenty minutes and a `suite` task would never run. [The risks](risks.md) say what to watch anyway.

## 9. Shared suite-level docs: `status.d/` fragments

[DOC-PROTOCOL.md](../embarch-doc/DOC-PROTOCOL.md) §5 requires the suite-level facts to move in the same pass as the change. With one engineer that is a rule against drift. With four workers it is a rule that puts four agents into [embarch.md](../embarch-doc/embarch.md) §3's table at once.

The fix is the one this repo already proved with `changelog.d/`: **one file per pending edit, no shared file touched.** A worker writes `status.d/<scope>-<slug>.md` naming the target doc and the fact that changed; the supervisor folds a worker's fragments as it lands that worker's branches, and deletes them (§6 step 4). Format: [status.d/README.md](../embarch-doc/status.d/README.md).

The rule DOC-PROTOCOL §5 was protecting is unchanged — the suite-level docs still must not disagree with a sub-project's — it just now takes two actors and two commits instead of one actor and one. The window in which they *can* disagree is the length of **one unit**, because folding is part of landing it (§6). **A unit that lands with its fragments still sitting in `status.d/` has failed**, whatever else it shipped.

## 10. The merge gate and merge order

The gate, run by the worker and then **re-run independently by the supervisor** on the merge result — not on the branch:

- `cargo build`, `cargo test`, `cargo clippy --all-targets -- -D warnings` in the touched repo, plus a native Windows build where `embarch-core` is involved ([embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §4).
- All six `embarch-doc` checks: `check-links.py`, `check-staleness.py`, `check-decision-refs.py`, `check-doc-conventions.py`, `check-doc-size.py`, `build_changelog.py --check`.
- **`check-ownership.py --scope <sub-project>`** on both branches — the mechanical form of §3. Either `core` or `embarch-core` is accepted; **`suite` is refused outright, because a cross-repo change is §8's, not a worker's.** Without it §3 is prose nothing reads: a worker's edit to [embarch.md](../embarch-doc/embarch.md)'s status table is *plausible by construction*, so `check-staleness.py` (which only flags a row disagreeing with a sub-project doc) passes it, and the collision §9 exists to prevent happens anyway.

That is [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6's existing standard, unchanged, applied per branch instead of per commit. Nothing here licenses a lower bar because an agent wrote it.

**A reviewer reads for intent, alongside landing, and gates nothing.** When a
unit's branches merge, the supervisor spawns an `embarch-reviewer` on the diff
against that sub-project's decisions and the reversals index, and does not wait
for it. Findings land in `inbox/` and in the unit's log entry; a confirmed
contradiction is reverted by SHA, which is the first thing that ever uses the
SHAs §11 already requires. **Merge-on-green is unchanged** — a reviewer that
blocked would make every unit a two-agent serial dependency, and the owner chose
progress over caution here as elsewhere. It costs a spawn, so it is skipped under
a tight budget, and **the log says which**: "no findings" and "no reviewer ran"
are different facts.

**The gate is mechanical and catches broken, not wrong.** The one judgement the supervisor adds: read the diff before merging when the change touches a shared crate (`embarch-study-designer`, `embarch-topology`, and `embarch-core-client` — which lives inside `embarch-api` but is path-depended on by `embarch-ui`, so an `api` worker can change `ui`'s dependency without owning `ui`), a wire type, or retires a decision. Those are where passing and correct diverge most expensively; everything else merges on green.

**Merge order** is shared crates first, then consumers, then `embarch-doc` — the same sequencing §6 already fixes for a cross-repo pass, applied to a leg's independent ones. Within a tier, order by branch age, oldest first, so nothing sits.

## 11. The log

Canon is a doc; Slack is the ping.

**One entry per unit**, prepended to [supervisor-log.md](supervisor-log.md), newest first: what it **decided**, what merged with its SHAs, what blocked and why, and any hardware-verification debt it collected. Per unit rather than per leg because a leg can be killed at any moment — and a per-leg entry written at the end does not exist for the leg that got killed.

**The entry goes in the fold commit, not after it, and a unit that lands without one has failed** — the same rule §9 states for an unfolded `status.d/` fragment, for the same reason. A separate step leaves a window in which a unit is landed and unlogged, and `api/003` landed in it on 2026-09-03: the fold did every other part correctly and never touched this log, nothing noticed, and that handoff is gone. One commit makes the state impossible rather than merely detectable. What *shipped* is already recorded by the workers' own `changelog.d` fragments and assembled into `history/<scope>.md`; the log does not restate it.

**Folded daily.** On its first unit after local midnight a supervisor folds the previous day's entries into one dated entry, keeping every SHA and every debt. Without it, per-unit entries would hit the 25 KB roll every few days and the handoff would get shorter and shorter — the opposite of what a relay needs.

Slack gets **one line per unit** as it happens — dispatched, landed with its SHA, or blocked with the reason — and nothing on an ordinary leg end. Under the relay legs end constantly; a push notification per leg would be a pager rather than a notification.

**This is the review surface, and under full delegate it is the only one.** It is read after the fact, so it must be honest about what was decided and not just what was shipped — a suite-wide design the supervisor approved on the owner's behalf is the single most important line it will ever write, and it belongs at the top of its unit's entry, not buried under the merge list.

## 12. Known risks

Fifteen of them, stated rather than designed away, in [risks.md](risks.md) — split out when this doc hit its size cap. The two worth knowing before reading anything else: **nothing reads a diff for intent before it lands, most of the time**, and **nobody watches the relay** — a leg hands off to a successor through a written entry, and what the entry omits is gone.

## 13. Running it

Arming the listener, latching the pump, sizing a leg against the real usage limits, watching it from a phone, and stopping it: [running the fleet](ops.md).
