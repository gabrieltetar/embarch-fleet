---
description: Arm the fleet watchdog in this window - a second, hands-free session that alerts when the listener stops ticking. It can never spawn work.
argument-hint: "[start | stop | status]"
disable-model-invocation: true
---

The fleet cannot detect that it has stopped making progress. This window can.

`CronCreate` fires **only while the REPL is idle**, so a tick that *hangs* —
rather than fails — takes the fleet dark with the pump still latched, and
`fleet stop` cannot be delivered either, because a listener mid-query cannot read
the channel. Nothing inside that process can notice, and `{{FLEET_REPO}}/ops.md`
§3 rules out anything that survives the editor closing. On 2026-09-03 that cost
five hours, and the mitigation on the books was "the owner notices channel
silence".

This is the replacement. A **second window, in its own process tree**, whose cron
is therefore not suppressed by anything the fleet is doing. **This window must
never spawn an agent**, and that is not only about authority: a session holding a
live background agent is not idle, and an unidle window has no cron. A watchdog
that spawned once would silence itself for as long as the spawn lived.

## What `tick` means, and what it used to mean

**`{{STATE_DIR}}/tick` means the fleet made progress.** Two actors touch it: the
listener at the end of every tick, and **a leg at every dispatch and every fold**
(`.claude/leg.md`). Fresh means at least one of them moved.

It used to mean only the first, and that was a design defect rather than a tuning
problem. The listener's cron is dark for the entire life of a leg — measured
2026-09-06: ticks at 14:04:24 then nothing until 14:53:49, four slots suppressed,
while the leg underneath landed 4/4 units and was healthy the whole time. A leg
is *designed* to run four units and that one took 44 minutes, so a threshold
under a leg's length was guaranteed to fire on **every healthy leg**, not
occasionally. It did: a false wedge alert at 14:37 unlatched the pump, and when
the leg died at 14:47 the listener read "pump absent" and stopped. The relay was
capped at one leg and the only explanation in the channel was wrong.

Adding the leg as a writer keeps this window's logic **literally unchanged** —
still one mtime, still stop-only — and *widens* what it catches: a leg that hangs
mid-unit now goes stale, which the old signal could not detect at all.

**The tradeoff, stated rather than left implicit: while a leg runs, a wedged
listener is masked by the leg's own touches.** That is acceptable. A wedged
listener only costs anything at a leg boundary — during a leg it has no work to
do — and once the leg ends nothing touches `tick`, so it is caught one threshold
later. The alternative, a second `.fleet/leg` file with the watchdog requiring
*tick stale AND no live leg*, buys that window back at the cost of a second piece
of state, a writer that must delete it on every exit path including a kill, and
branch logic in the one window whose entire safety argument is that it reads one
mtime and can only ever stop. Not worth it for a failure that is detected 35
minutes later anyway.

## Why this does not weaken the kill switch

**It can only ever reduce what the fleet is doing.** It cannot spawn an agent,
cannot write a file in any repo, cannot start a leg. It reads one mtime, posts,
and — when it declares a wedge — deletes the pump latch. That is its entire
vocabulary, and every word of it points the same way: **stop, never start.**

The rule `ops.md` §3 states is that **nothing may be arranged to outlive the
editor in a way that takes away the stop.** A watchdog that could restart a leg
would take it away. One whose only action *is* a stop cannot: the worst it can
do to you is stop a fleet that was fine, which costs a `fleet start` you type
yourself.

So closing the *listener* window still ends every unit of work in flight —
workers are subagents of a leg, a leg is a subagent of the listener, and they
die together. Nothing outlives that close except an alarm and, at worst, an
unlatched pump. Both are the safe direction. Closing this window too costs
nothing.

## Arming it

1. **Confirm you are not the listener.** If this window is armed with
   `/fleet start`, stop: one window cannot watch itself, and the shared cron
   queue is exactly what is being routed around. Open a new window.
2. **Create the heartbeat**, one recurring cron job on `7-59/10 * * * *` — offset
   from the listener's `3-59/10` so the two never contend. Its prompt must be
   **exactly** the block below, and that block is the source of truth for the
   live job: if you change one, change the other in the same pass. They have
   drifted before, and a job armed with an older threshold looks entirely
   healthy.
3. **Record what you just armed it with**: `scripts/fleet-armed.py --stamp
   .claude/commands/fleet-watch.md`, after the `CronCreate` so a failed arming
   leaves no stamp. This window's block has drifted before and *"a job armed
   with an older threshold looks entirely healthy"* is the sentence above; the
   stamp is what makes it visible. Disarming clears it (`--clear`).
4. Say so in the channel — `{{FLEET_REPO}}/scripts/fleet-post.py "the watchdog
   is armed and will speak up if the fleet goes quiet for 35 minutes"`. That is
   an FYI, so it must not use `--action`: being armed asks nothing of anyone.
   Tell the owner in the terminal which window this is.

> **Fleet watchdog tick.** Do not read the channel. Do not read the repo. Do not
> spawn anything. This tick is three file checks and at most one post.
>
> 1. Read `{{STATE_DIR}}/pump`. **If it is absent, stop and print nothing** —
> the pump is off, so nothing is expected to be ticking and silence is correct.
>
> 2. Read the mtime of `{{STATE_DIR}}/tick`. It is touched by the listener at the
> end of every tick **and by a leg at every dispatch and every fold**, so it
> means "the fleet made progress". If the file does not exist, nothing has moved
> since the watchdog was armed; treat that as stale only if the pump latch is
> older than 35 minutes, otherwise stop (the fleet was just started and has not
> ticked yet).
>
> 3. If the mtime is **more than 35 minutes old**, the fleet has stopped.
> **Delete `{{STATE_DIR}}/pump`**, then run
> `{{FLEET_REPO}}/scripts/fleet-triage.py` — one read-only command that answers
> *why*, which this window used to say it could not. It reports one of
> `WINDOW_GONE` / `ORPHANED_LEG` / `UNMERGED_WORK` / `CLAIMED_NO_WORK` /
> `IDLE_OR_WEDGED`, its evidence, and the recovery. Then one post, which is this
> window's entire output:
>
> ```
> {{FLEET_REPO}}/scripts/fleet-post.py \
>   "the fleet has not made progress since <time>, so I stopped it restarting" \
>   --action "<the triage verdict's own Recommended line>" \
>   --detail "<verdict>: <its one-line why>. tick mtime <mtime>; pump latch deleted at {{STATE_DIR}}/pump."
> ```
>
> **Relay the verdict, do not re-derive it and do not soften it.** On
> 2026-09-07 this window correctly said it could not tell four causes apart, and
> the true cause was a fifth: a leg orphaned while holding **two finished
> units**, which took a person reading four transcripts and three remotes to
> find. If `fleet-triage.py` fails or exits 2, say so and fall back to the old
> wording — "wedged, dead, closed, or the machine slept, and this window cannot
> tell those apart" — which is still the honest answer when there is no
> diagnosis.
>
> **`--action`, because this one really does need him** — it is in `ops.md`
> §3's closed set, and a wedged fleet that nobody is told about is the whole
> failure this window exists for. **Then read `{{STATE_DIR}}/alerted`: if it
> holds a timestamp under 60 minutes old, skip the post — you already said this
> — but still delete the latch if it is back.** Otherwise write the current time
> there afterwards. A watchdog that repeats itself every ten minutes is a pager,
> and `ops.md` §3's alert set is closed for that reason.
>
> **35 minutes is measured, not chosen for roundness.** Re-derived 2026-09-06
> from git commit times — claims and folds are the only touches that leave a
> record — over the six 4-unit legs from 16:01 to 21:22, the first that carried
> the dispatch touch. 46 gaps: median **4.5 min**, p90 14.1, p95 17.1, **max
> 29.6**, nothing above 30. The reconstruction cannot see the step-0 touch or
> the listener's between-leg cron, so every number is an **upper bound** on the
> real gap — the conservative direction for a threshold.
>
> **The binding gap is a deploy, not a leg.** Both gaps over 25 minutes — 29.6
> and 28.4 — are leg boundaries with an `embarch-deployer` in them, and nothing
> touches `tick` while one runs, because a window holding a live background
> agent has no cron either. *In-leg* gaps top out at **17.4**: four workers are
> rarely all silent at once. Going below ~32 means making the deployer touch
> `tick` too; until it does, that is the floor and 35 is the margin over it.
>
> **Why 45 was loose.** It came from fold-to-fold gaps of 40–41 minutes over the
> 00:12–05:20 run, measured before a leg touched `tick` at dispatch. Count that
> run's own claim commits as the touches they would be today and its max falls
> to **32.0** — and that was a 13-unit leg, a shape the 4-unit cap has retired.
>
> Do not lower it without new measurement; a false wedge is not a harmless
> conservative alarm, because it unlatches the pump. Under the old 25 the
> watchdog fired on a leg that landed 4/4 units.
>
> **Deleting the latch is the only write this window ever makes, and the only
> direction it may push.** It can stop a fleet; it can never start one. That
> asymmetry is what keeps it from being a second control plane: the worst a
> false positive costs is a `fleet start` you have to type, and the worst a
> failure of this window costs is the silence you had before it existed.
>
> 4. If the mtime is fresh, do nothing and print nothing.
>
> Never spawn an agent. Never edit a file in any repo. If you find yourself about
> to do either, the answer is a line in the channel saying what you saw.

## What it can and cannot tell you

**It detects silence, not health.** A fleet that ticks happily while every leg
fails its gate looks identical to a healthy one from here. That is fine — a red
gate is already reported per unit, and this exists for the one failure that
reports nothing at all.

**A stale tick has four causes and this cannot tell them apart:** a listener tick
hung on a tool call, a leg hung mid-unit, the window was closed without stopping
the pump, or the machine slept. All four want the same response from the owner —
look at the listener window — so the alert does not guess. The second is new:
under the old signal a hung leg was invisible, because the listener's cron kept
ticking underneath it.

**While a leg runs it cannot see a wedged listener**, because the leg's own
touches keep `tick` fresh. That is the accepted cost of the signal meaning
progress; the case it gives up is one that costs nothing until the leg ends, and
35 minutes after that it is caught.

**The next re-derivation reads a log rather than reconstructing one.** The
numbers above came from git commit times, because claims and folds were the only
touches that left a record; every touch now also appends a labelled line to
`{{STATE_DIR}}/tick.log`, so `{{FLEET_REPO}}/scripts/fleet-tick.py --report`
prints the real gaps — including the step-0 and between-leg touches that
reconstruction is blind to. Re-derive from that, and only widen the threshold if
the measured max says to.

**It is not a control plane, and unlatching is not `fleet stop`.** A graceful
stop is delivered to a live supervisor, which finishes landing what is in
flight, folds, logs and exits. This window cannot do that — a wedged listener
cannot relay a message to anyone. Deleting the latch only stops the *next* leg
from being spawned once the listener recovers. Whatever is already running is
still running, and closing VS Code remains the only thing that ends it. What
this buys is learning you need to within the hour instead of five hours, and not
coming back to a fleet that quietly resumed on a rule you no longer wanted.

**The graceful stop you do have while a leg runs is `fleet stop` in the
channel** — the supervisor reads it at every unit boundary and honours it itself
(`.claude/leg.md`), latch included. This window is for when there
is no leg to read it.

## Vocabulary

| Message | Action |
|---|---|
| `watch status` | When the fleet last made progress (`tick`'s mtime — listener or leg), whether the pump is latched, and whether an alert is currently suppressed. Add `scripts/fleet-tick.py --report` when the question is about *cadence* rather than right now |
| `watch stop` | Delete the cron job. The listener is unaffected |

`watch status` is the one thing worth asking from a phone, because it answers
"is the fleet actually running" without waking the listener to ask it.

## Stopping

Delete the cron job, or close the window. Neither affects the listener, any live
leg, or the pump — this window holds nothing anyone else depends on, which is the
property that makes it safe to run all day beside the thing it watches.
