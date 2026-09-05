---
description: Arm the fleet watchdog in this window - a second, hands-free session that alerts when the listener stops ticking. It can never spawn work.
argument-hint: "[start | stop | status]"
---

The listener cannot detect that it is wedged. This window can.

`CronCreate` fires **only while the REPL is idle**, so a tick that *hangs* —
rather than fails — takes the fleet dark with the pump still latched, and
`fleet stop` cannot be delivered either, because a listener mid-query cannot read
the channel. Nothing inside that process can notice, and `{{FLEET_REPO}}/ops.md`
§3 rules out anything that survives the editor closing. On 2026-09-03 that cost
five hours, and the mitigation on the books was "the owner notices channel
silence".

This is the replacement. A **second window, in its own process tree**, whose cron
is therefore not suppressed by the listener being mid-query.

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
   **exactly** the block below.
3. Post one line to `{{SLACK_CHANNEL_NAME}}` saying the watchdog is armed and at
   what threshold, and react `robot_face`. Tell the owner in the terminal which
   window this is.

> **Fleet watchdog tick.** Do not read the channel. Do not read the repo. Do not
> spawn anything. This tick is three file checks and at most one post.
>
> 1. Read `{{STATE_DIR}}/pump`. **If it is absent, stop and print nothing** —
> the pump is off, so nothing is expected to be ticking and silence is correct.
>
> 2. Read the mtime of `{{STATE_DIR}}/tick`. If the file does not exist, the
> listener has not ticked since the watchdog was armed; treat that as stale only
> if the pump latch is older than 25 minutes, otherwise stop (the fleet was just
> started and has not ticked yet).
>
> 3. If the mtime is **more than 25 minutes old** — two missed heartbeats, so a
> single slow tick is not enough — the listener is wedged or dead. **Delete
> `{{STATE_DIR}}/pump`**, then run `{{FLEET_REPO}}/scripts/fleet-alert.py
> "listener silent since <mtime>; pump unlatched"`, post one line to
> `{{SLACK_CHANNEL_NAME}}` saying both, and react `robot_face`. **Then read
> `{{STATE_DIR}}/alerted`: if it holds a timestamp under 60 minutes old, skip the
> alert and the post — you already said this — but still delete the latch if it
> is back.** Otherwise write the current time there afterwards. A watchdog that
> repeats itself every ten minutes is a pager, and `ops.md` §3's alert set is
> closed for that reason.
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

**It detects silence, not health.** A listener that ticks happily while every leg
fails its gate looks identical to a healthy one from here. That is fine — a red
gate is already reported per unit, and this exists for the one failure that
reports nothing at all.

**A stale tick has three causes and this cannot tell them apart:** the tick hung
on a tool call, the window was closed without stopping the pump, or the machine
slept. All three want the same response from the owner — look at the listener
window — so the alert does not guess.

**It is not a control plane, and unlatching is not `fleet stop`.** A graceful
stop is delivered to a live supervisor, which finishes landing what is in
flight, folds, logs and exits. This window cannot do that — a wedged listener
cannot relay a message to anyone. Deleting the latch only stops the *next* leg
from being spawned once the listener recovers. Whatever is already running is
still running, and closing VS Code remains the only thing that ends it. What
this buys is learning you need to within ten minutes instead of five hours, and
not coming back to a fleet that quietly resumed on a rule you no longer wanted.

## Vocabulary

| Message | Action |
|---|---|
| `watch status` | When the listener last ticked, whether the pump is latched, and whether an alert is currently suppressed |
| `watch stop` | Delete the cron job. The listener is unaffected |

`watch status` is the one thing worth asking from a phone, because it answers
"is the fleet actually running" without waking the listener to ask it.

## Stopping

Delete the cron job, or close the window. Neither affects the listener, any live
leg, or the pump — this window holds nothing anyone else depends on, which is the
property that makes it safe to run all day beside the thing it watches.
