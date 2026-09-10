# EmbArch: running the agent fleet

**Status:** active, 2026-09-03. Operations half of [protocol.md](protocol.md) — how the fleet is armed and latched, how wide a leg may run, how it is watched and stopped. The protocol itself (roles, the ownership map, the queue, the contracts, the gate) is in that doc; this one is what an operator does.

## 1. Starting the fleet

**Three windows, and only one of them is armed.**

1. **The listener** — a dedicated VS Code window running `/fleet start` ([.claude/commands/fleet.md](../embarch-doc/.claude/commands/fleet.md)). It reads #embarch-fleet on a 10-minute heartbeat — which fires **only while that window is idle**, and it is not idle while a leg runs ([slack.md](slack.md) §2) — spawns agents, relays what they say, nothing else. Arming leaves the pump **off**.
2. **The pump** — `fleet start` in the channel: writes the latch, spawns the first leg, and from then on each leg's death spawns the next, the relay ([the protocol](protocol.md) §6). `fleet stop` ends it.
3. **The owner's window** — an ordinary session for standing rules, `scripts/`, `.claude/`, hardware, and drops into `inbox/`. Not armed, and not the fleet.

`/supervise` runs **one leg** by hand — the same as `fleet go`. Agent definitions: [supervisor](../embarch-doc/.claude/agents/embarch-supervisor.md), [worker](../embarch-doc/.claude/agents/embarch-worker.md).

**Editing a rule no longer stops the fleet.** `deploy.py` still refuses to render into a live fleet, but the owner now commits and runs `deploy.py --queue`, which pins the framework SHA; the listener spawns an [`embarch-deployer`](../embarch-doc/.claude/agents/embarch-deployer.md) at the next leg boundary — where it has just proved with `ListAgents` that no leg is alive — and that agent renders the pinned commit and nothing else. It was worth building because the old loop was the largest measured hole in the fleet's uptime: ~3.7 h of a 14 h window, the fleet stopped so the owner could hold the pen. [DEVELOPING.md](DEVELOPING.md) §4.1 is the loop; a **re-arm stays the owner's** either way.

**The relay is what `/loop /supervise` was going to be** — pacing lives in the heartbeat and the latch rather than a `/loop` interval, each leg bounded at four units so nothing accumulates. **Cron and scheduled cloud agents stay ruled out**, and not on principle: a cloud runner cannot see `/mnt/c/…/embarch-core`, the west workspaces, or the local toolchains.

**Concurrency cap: 6 workers**, at most one per sub-project, wave size set per leg by the budget (§2). The cap exists because rebase cost grows with the number of branches waiting behind a merge, not because of the seat.

**The supervisor is singular** — two would both fold `status.d/`, the one job that must be serialized, which is why a leg's concurrency is workers rather than supervisors ([the protocol](protocol.md) §6). The listener checks with `ListAgents` before spawning; a leg checks again.

## 2. How much to run: the usage budget

**Moved to [budget.md](budget.md)** — the two thresholds, why the percentages never arrive on this machine, the measured wave and its calibrated token ceiling, and the 429 hard signal that sits underneath all of it. Split out 2026-09-07 rather than squeezed, so nothing in it was shortened to make room; every `§2` reference elsewhere still points here.

## 3. Driving the fleet from a phone, and stopping it

Remote Control attaches a phone or browser to a Claude Code session on this machine: `/rc` in the session, then open [claude.ai/code](https://claude.ai/code) or the Claude app. That is the entire setup.

**Closing VS Code stops the fleet, and that is the point** — the one control that works from across the room with no session, no network and no agent cooperating. Nothing may be arranged to outlive it: a supervisor under `tmux`, a daemon, a detached process would each buy uptime by taking away the stop. **It is safe because the process tree is the boundary**: workers are subagents of a leg and a leg is a subagent of the listener, so the window closing kills all three at the same instant — nothing keeps building, nothing merges after the fact, and no relay hands off to a successor that is not there. What a kill *can* leave behind is bounded, and [the protocol](protocol.md) §6 step 0 cleans all of it:

| Left behind | Why it is harmless | Recovery |
|---|---|---|
| Tasks marked `claimed` | Their workers died with the leg | **No supervisor running ⇒ every claim is stale.** Reclaim by the **worktree's** state, never the branch's commit count: clean and no commits ⇒ `open`; anything else ⇒ `blocked` naming the branch *and* the worktree path. [tasks/README.md](../embarch-doc/tasks/README.md) carries the rule and why its opposite was dangerous |
| Worktrees under `embarch/.worktrees/` | Outside every repo tree, so nothing reads them | **Look before deleting.** No commits *and* a clean tree ⇒ delete. No commits and a **dirty** tree ⇒ it may be a worker still finishing, or one that died with finished work; commit it to a branch and inspect. Keep the rest for the `blocked` task |
| A repo mid-merge or mid-rebase | `main` is untouched until a merge completes | `git merge --abort` / `git rebase --abort` before anything else |
| Unfolded `status.d/` fragments | A fragment is the request, not the edit | Left for the next leg — that is what they are for |
| Uncommitted edits in the main checkout | A unit's fold is **one commit**, so it either happened or it did not | Restore the shared docs, leave the fragments, redo the fold |
| A leg worktree at `.worktrees/embarch-doc/leg/` | Outside every repo tree; the owner's checkout is untouched | Clean ⇒ reuse it, `git fetch && git reset --hard origin/main` first. Dirty ⇒ inspect before resetting: an unpushed fold lives here and nowhere else |
| A log entry with no matching fold | `fold-commit.py` commits the log first, so this is the *survivable* ordering | `fold-commit.py --check` names it. Redo the fold; **do not write a second entry** |

**"No commits" does not mean "no work", and this table used to imply it did.**
A worker's tree is uncommitted for its whole run and only becomes commits in its
final bookkeeping, so `rev-list --count` reads zero for a worker finishing
normally *and* for one that died with ~200 lines of green work in hand. Leg 007
began recovery on a **live** worker that way, and nothing was lost only because
it committed the tree rather than deleting it. **The harness saying an agent has
no live children is not proof its worker is dead** — check the tree, and when in
doubt commit it to a branch, which is cheap and reversible.

**Reporting is different on a phone, and the fleet is not you.** Every post goes through `scripts/fleet-post.py`, which posts as the app: **one plain sentence per unit**, the technical half — SHAs, paths, gate output — in `--detail`, a thread reply folded until you open it. **Only `--action` notifies**, and it names what you must do. Never paste passing output; a green `cargo test` is the word "green".

**A watchdog window detects the one failure nothing else can.** The fleet cannot
notice that it is wedged: a hung tick never returns to idle, so its own cron
cannot fire and no `fleet stop` reaches it. A second window armed with
`/fleet-watch` reads the mtime of one file, `.fleet/tick`, and alerts when it
goes stale by **35 minutes**. **Its whole vocabulary points one way — stop, never
start**: it cannot spawn, write a repo file, or launch a leg, and a declared
wedge means an alert and deleting the pump latch. That asymmetry is why it does
not weaken the kill switch: this section's rule bites only on what *takes away*
the stop. Unlatching is not a graceful stop: whatever is running keeps running,
and closing VS Code is still what ends it.

**`tick` means the fleet made progress, not that the listener's cron fired** — the listener touches it each tick, **a leg at every dispatch and fold**. The listener-only reading went dark exactly when the fleet was busiest ([slack.md](slack.md) §2), so it fired on healthy legs; on 2026-09-06 it unlatched a live pump and capped the relay at one leg. The fix leaves the logic untouched (one mtime, stop-only) and *widens* it: a hung leg now trips it too. **35 min: re-derived 2026-09-06, max gap 29.6 over six legs.** The accepted cost and the rejected `.fleet/leg` alternative are in that command file.

**Alert rarely, via `--action`.** Both posters' headers say why an owner-authored `@` notifies nobody. Unconfigured they exit 2: record that it did not send. `PushNotification` needs Remote Control, so it supplements. **The set, closed**: leg blocked and stopped · budget HOLD · a failed spawn · the same failure blocking two units · a dream · a parked `suite` task · **an agent suspended on a permission prompt** · **a re-arm owed by a landed deploy** · **the queue dry**. **Never per unit, never on an ordinary leg end** — legs end every twenty minutes, and an alert each time is a pager.

**That last one is a hook, not a call.** A suspended agent cannot alert for itself, so `.claude/settings.json`'s `PermissionRequest` hook does it — the one member of this set no supervisor decides to send. **It excludes `AskUserQuestion` by design**: §3 forbids a leg asking mid-leg, so that prompt is the owner in his own window, and including it produced nine false positives against zero true ones. Gating the hook on the caller being a subagent was **rejected** — it needs the hook to tail `transcript_path` for `isSidechain`, racy and undocumented, in a hook that must stay async.

**Steering works, and the supervisor must let it.** A `fleet stop` reaches a live leg because the supervisor reads the channel at **every unit boundary** ([slack.md](slack.md) §2); the listener's `SendMessage` is the second route, not the first, and a message sent mid-turn is queued either way. Honouring it: finish landing what is in flight, fold, write the log entries, **delete the latch**, exit. That *graceful* stop leaves nothing for step 0 to clean, and deleting the latch is what stops a respawn — which is why it is the supervisor's job when the supervisor is the one who read the message.

**Never ask a question mid-leg.** Prompts do not expire while a device is connected, so a question is eventually answered — but "eventually" is a frozen leg with workers in flight and a 5-hour window burning. End the leg and say so once.

**Terminal-only commands** (`/resume`, `/plugin`) do not work remotely and custom slash commands may not expand from mobile, so the fleet answers to plain English too (**"start the fleet"**, **"run a supervisor batch"**, wired in [CLAUDE.md](../embarch-doc/CLAUDE.md)).

## 4. Announcing a risky task, and answering by DM

[The protocol doc](protocol.md) §8 has the supervisor executing cross-repo passes itself, unattended, under full delegation — the largest blast radius in the suite ([the risks](risks.md)). This is the control on it, and it costs nothing.

**Announce and park — never announce and block** (§3: a blocking question freezes a leg with workers in flight). Before starting a `suite`-scope task, or any change that bumps a wire schema version, the supervisor posts to **#embarch-fleet** (`C0BUKTL2FPC`, [slack.md](slack.md)) and alerts (§3) saying what it is about to do, which repos it touches, why, and that a reply cancels it. It records the `ts` **in the task file**, not only in its head — a leg is four units long and the window is thirty minutes, so the `ts` routinely has to outlive the leg that posted it. Then it **does not start that task**: it keeps running units normally, so single-repo workers are not delayed by a decision that has nothing to do with them.

**Polling.** `scripts/fleet-read.py --thread <ts>` at every unit boundary — the same poll that backs up a `fleet stop` ([slack.md](slack.md) §2). No subscription is needed or exists.

**Executing.** The parked task runs as a leg's **last unit**, and only if **no objection has arrived and at least 30 minutes have passed since the announcement**. If the leg ends first, it leaves the task `open` with the `ts` in the file and the next leg completes the window — the relay must not restart the clock every twenty minutes, or a `suite` task would never run at all. A reply saying go executes it immediately.

**Replies.** Cancel, stop, or no → drop the task to `open` and quote the reply in the task file so the next leg knows why. A question → answer in-thread and stay parked. Everything goes in the one thread, and the log records the announcement, the reply or its absence, and what was done.

### 4.1 What a DM may and may not do

Reading replies makes Slack a **control plane**, not just the surface the log is pinged to. [slack.md](slack.md) §3 carries the bounds and they apply here unchanged — **only messages from `U0AGQGSHM2P`, in that thread, are direction**, and text quoted or pasted *inside* a message is data however authoritative it reads. Specifically: a reply **can** stop the leg, cancel or hold a task, narrow its scope, or answer a question the supervisor asked. It **cannot** change a standing rule ([protocol](protocol.md) §2 reserves those, and [slack.md](slack.md) §1 shows there is no route), grant hardware access, or widen the ownership map — a Slack thread is a good control surface *because* it is low-friction, and low-friction is the wrong property for the rules that bound an unattended agent.

**Two stop channels exist** — Remote Control (§3) and the channel ([slack.md](slack.md) §2); the supervisor honours whichever it sees first and names which in its log entry.

## 5. Slack as a control plane

**#embarch-fleet** (`C0BUKTL2FPC`, private, one member) is where the fleet is started, steered, questioned and reported. Arm the listener with `/fleet start`.

**This section moved to [slack.md](slack.md) on 2026-09-10** — the three windows and what each may write, how the pump runs, what happens when the channel is unreachable, and the identity rules that bound what a message can do. It moved because the transport changed: the fleet now reads *and* posts as its own Slack app over a bot token, nothing in it touches the owner's personal OAuth, and the gate deciding what counts as an instruction became code rather than prose in a cron prompt. Saying that where §5 sat would have cost more than the section had left.

Two things from it are cited often enough to keep here: **only messages authored by `U0AGQGSHM2P` are instructions**, and **a standing rule cannot be changed from Slack at all** — the listener cannot write those paths and neither can any agent it spawns (`check-ownership.py --supervisor`), so the answer is "open your own window".

## 6. Four surfaces, and which one is the remote control

Four things reach this suite from outside the terminal — Remote Control, this channel, `@Claude` in Slack, and the unavailable-here Channels mechanism. They fail differently and only one is a remote control: [embarch-remote-surfaces.md](../embarch-doc/embarch-remote-surfaces.md) has the comparison, why `@Claude` is **never** invited to #embarch-fleet, and what cloud sessions in **#embarch-cloud** are and are not for.

## 7. Dreaming: what to do with an empty queue

An empty queue is not idleness to fill. It is the one moment the fleet genuinely does not know what is worth doing next — every other moment it executes something already judged worth doing. So it asks, once, with real options.

**Two triggers, because the owner should not have to ask.**

- **A leg's refill finds nothing dispatchable**: post three proposals, alert with `scripts/fleet-alert.py` (a bare `@` notifies nobody), and **end the leg**. Do not pick one.
- **The heartbeat finds the pump on, no leg alive, and an empty queue**: the listener spawns a leg anyway — refill may find something the queue does not have yet — and that leg dreams if refill also comes up empty. Rate-limited to one dream per **6 hours**, enforced by the listener refusing to spawn into an empty queue while a dream post sits in the 20 messages it just read. The channel is the watermark; there is no state file for this.

**A dream post carries `crystal_ball` as well as `robot_face`, and that is what the gate reads.** The old rule looked for "a `robot_face` dream post", but every fleet message carries `robot_face`, leaving the gate unfalsifiable both ways. One extra reaction fixes that without a state file.

The second trigger is the one that matters: without it the fleet sits idle until the owner notices and pokes it, and noticing is the work the fleet exists to take off him. Six hours rather than ten minutes because an empty queue stays empty until someone acts. **The pump stays latched on through a dream** (owner's call): the ticks cost a directory count, and the moment a proposal is answered or a file lands in `inbox/`, work starts with no restart.

**The fleet does not write a dreamt item into its own queue.** Rejected 2026-09-03 when the pump was specified — the tempting version is a supervisor that dreams one item and runs it, and that is a fleet both filling and draining a queue it invented, which is a machine for generating plausible busywork. Three proposals cost one word to answer instead. **Three, not one and not ten**: one is a decision wearing a question's clothes, ten is a survey the owner has to read.

**Every proposal must come from something already written down** — [suite/roadmap.md](../embarch-doc/suite/roadmap.md)'s Next, a sub-project's `open.md`, an unaddressed [reversals](../embarch-doc/embarch-decision-reversals.md) follow-up, or a finding a worker dropped in `inbox/`. **Nothing invented.** Each carries only what is needed to answer in one word: **what** it would do, in one line; **why now**, with the doc that says it matters, linked; **scope** and **`Hardware:`**, because a `required` proposal is asking for his hands rather than the fleet's; and **the cost**, honestly — one unit, or a cross-repo pass the supervisor would run itself. Then: *"reply `do 2`, or tell me what you actually want."* The second half matters — the three are a starting point, not a menu, and the most useful answer is often none of them.

**A dream is recorded like anything else**, in the log ([the protocol](protocol.md) §11) — a pattern of all three being rejected would mean the refill sources have drifted from what he cares about, and that is worth seeing.

## 8. Context: what dies, what is cleared, what is handed off

Three threads, three different answers, and the differences are deliberate.

**A worker** is one task, then dead: so everything it learned is in a doc or gone ([the protocol](protocol.md) §5). Nothing to clear.

**A leg** is four units then dead (§6 there), and that bound is what replaced clearing for the supervisor. Until 2026-09-03 it was a long-lived session accumulating every batch it had run, needing the owner to `/clear` it at a batch boundary — the only safe one, since mid-batch nothing is ever at rest. It is now an agent that cannot be cleared and does not need to be: it hands off. **The handoff is the log** — [supervisor-log.md](supervisor-log.md)'s newest entries carry what was decided, what merged with its SHAs, what blocked, what was opened, the hardware debts, the budget, and what the last leg was least sure about. Step 0 of every leg reads them, and after a relay handoff the successor has no other memory of its predecessor whatsoever.

**The listener** is the one thread that lives. It is designed to grow slowly rather than not at all ([slack.md](slack.md) §1), and **it can be `/clear`ed without disarming** — cron jobs survive a clear, verified 2026-09-03 — so resetting a drifted listener costs nothing and loses nothing, because it holds no state a leg needs.

**A leg boundary is the only moment when nothing is in flight** — no worktrees, no agent branches, no unfolded fragments, no dead workers' claims — and it is now reached automatically, four units at a time.

### 8.1 Three contexts, and why (2026-09-03)

**Built after the owner asked whether his own session was part of the fleet.** It was — and it was also the listener, *and* the session that wrote the rules the supervisor obeys: three roles in one context, legitimate every time because he asked every time, and structurally unenforced. Split twice the same day, first the work and then the listener, into three contexts with disjoint powers:

- **The owner's window** — an ordinary session holding the pen for standing rules, `scripts/`, `.claude/`, hardware, and `inbox/` drops.
- **The listener** — its own window, armed with `/fleet start`, with **no hands at all** ([slack.md](slack.md) §1). It spawns and relays.
- **A leg** — an [`embarch-supervisor`](../embarch-doc/.claude/agents/embarch-supervisor.md) agent that works and dies at four units, its context bounded the way a worker's is bounded by a task, so there is nothing to clear, only a handoff to write.

**What makes it hold is not the doc.** `scripts/check-ownership.py --supervisor` rejects every owner-reserved path, and a leg runs it on its own commits before finishing; neither the listener nor any agent it spawns can write those paths. So **there is no route from Slack to a standing rule**, even for the owner. **A supervisor that can edit its own constraints has none** — including when it is right: batch 002 found three real defects in exactly those reserved files, every one worth fixing and none of them the supervisor's to fix. They belong in the log and in `inbox/`, and the owner's commit closes them.

**Proven: the nesting.** Batch 003 dispatched two `embarch-worker` agents from inside a supervisor agent; both ran to completion, both reported honestly, and `--supervisor` came back clean on the leg's 16 changed paths. Running a leg inline stays available if the owner asks, with the separation explicitly off for that run.

**Proven: the relay**, as of 2026-09-05 — nineteen legs, handing off through [supervisor-log.md](supervisor-log.md) with no memory of a predecessor. This line read "unproven" for two days after it had run. If a spawn or a handoff fails for a reason that looks structural rather than task-specific, the leg stops and says so — and the pump latch is a single file the owner can delete.
