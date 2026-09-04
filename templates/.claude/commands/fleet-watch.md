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

**It has no hands, and that is the whole argument.** It cannot spawn an agent,
cannot write a file in any repo, cannot start a leg, cannot touch the pump. It
reads one mtime and posts.

So closing the *listener* window still stops every unit of work in flight —
workers are subagents of a leg, a leg is a subagent of the listener, and they die
together. Nothing outlives that close except an alarm, and an alarm that fires
after the fleet is deliberately stopped is telling the truth. Closing this window
too costs nothing and stops the alarm.

The rule `ops.md` §3 states is that **nothing may be arranged to outlive the
editor in a way that takes away the stop**. A watchdog that could restart a leg
would do that. One that can only speak does not.

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
> single slow tick is not enough — the listener is wedged or dead. Run
> `{{FLEET_REPO}}/scripts/fleet-alert.py "listener silent since <mtime>; pump
> still latched"`, then post one line to `{{SLACK_CHANNEL_NAME}}` saying the same
> and react `robot_face`. **Then read `{{STATE_DIR}}/alerted`: if it holds a
> timestamp under 60 minutes old, skip both — you already said this.** Otherwise
> write the current time there afterwards. A watchdog that repeats itself every
> ten minutes is a pager, and `ops.md` §3's alert set is closed for that reason.
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

**It is not a stop channel.** If the listener is wedged, `fleet stop` cannot be
delivered by anyone, including this window. Closing VS Code remains the backstop,
and this exists so you learn you need to within ten minutes instead of five
hours.

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
