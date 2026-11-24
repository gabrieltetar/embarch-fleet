---
description: Retired 2026-11-23 - the fleet watchdog is now scripts/fleet-deadman.py, a cron job outside Claude. Do not arm this window.
disable-model-invocation: true
---

**Retired by the owner on 2026-11-23. Do not arm a watchdog window.** If this was
typed, say so in one line and do nothing else: create no cron job and delete
nothing.

The watchdog is `{{FLEET_REPO}}/scripts/fleet-deadman.py`, run by the owner's
crontab every five minutes. It reads the same `tick` mtime with the same
50-minute threshold, and it also catches what a Claude window never could: a
logout that takes every window down with it, a failing token refresh, and a
fleet stopped on budget. It alerts and never unlatches the pump; after a stall
alert the owner stops the fleet himself. This window was retired because the dead
man already covers the stall it watched for, it had not been armed since
2026-10-29, and its one extra power, deleting the pump latch, once unlatched a
healthy fleet on a false alarm (2026-09-06).

## What `tick` means, and what it used to mean

Kept because the listener's tick prompt points here. "The watchdog" below is
the retired window; the dead man reads the same mtime the same way.

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
still one mtime — and *widens* what it catches: a leg that hangs
mid-unit now goes stale, which the old signal could not detect at all.

**The tradeoff, stated rather than left implicit: while a leg runs, a wedged
listener is masked by the leg's own touches.** That is acceptable. A wedged
listener only costs anything at a leg boundary — during a leg it has no work to
do — and once the leg ends nothing touches `tick`, so it is caught one threshold
later. The alternative, a second `.fleet/leg` file with the watchdog requiring
*tick stale AND no live leg*, buys that window back at the cost of a second piece
of state, a writer that must delete it on every exit path including a kill, and
branch logic in the one window whose entire safety argument is that it reads one
mtime and can only ever stop. Not worth it for a failure that is detected 50
minutes later anyway.

