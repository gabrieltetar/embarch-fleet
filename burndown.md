# Burndown

**Split out of [budget.md](budget.md) on 2026-09-08, the day it was written**,
because adding it left that file with 19 bytes of headroom. A split rather than
a squeeze, for the reason [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md)
§2 gives and this repo has now taken twice: moving an argument verbatim
restates nothing, so no existing argument had to be shortened to pay for a new
one. `budget.md` answers "may the fleet dispatch, and how many?"; this answers
the one case where the goal is to reach the ceiling rather than avoid it.

**Added 2026-09-08 at the owner's call, on the evening the case for it was
sitting on disk:** the week reset at 07:00 the next morning with the seat at
81%, and the ~36M billable tokens between there and the ceiling had no other way
to be spent. The weekly window is use-it-or-lose-it. Every control in [budget.md](budget.md) is
built to keep the fleet *away* from the wall, which is right for six days and
exactly wrong for the seventh.

So burndown is that same gate with four numbers swapped — `[burndown]` in
fleet.toml: stops at 97% instead of 90%, `taper = 0`, and a worker cap of its
own. `suggest()` already reads a zero band as full width, so the mode is config
and a latch, **not a second code path**. Everything else about a leg is
unchanged: same 4 units, same reviewer, same commits to `main`. That is the
whole design constraint — a mode that also changed how work is done would be a
second fleet, held equal to the first by nothing.

**Of those, `taper = 0` is the one doing the work, and the first run proved it
by accident.** The taper is a fraction of the cap, so it narrows the wave as
the cap approaches: at weekly 89% against a 90% cap it suggests **one** worker,
and at 90% it stops the fleet outright — which it had already done at 20:23 on
2026-09-08, with the reset ten and a half hours away and the seat holding dead
flat until the mode was armed. Zeroing the taper is what returns a full wave,
and moving the stop to 97% is what buys the hours to spend it in. **The width
number bought nothing** (below).

**Three properties are load-bearing, and each is a refusal in
[`scripts/fleet-burndown.py`](scripts/fleet-burndown.py).**

*Manual.* Nothing self-arms it. A mode that decides on its own to spend the rest
of the allowance can decide wrong at 3 a.m., and only the owner knows whether he
wants the seat tonight.

*Deadlined.* Every burndown races a known reset instant, bounded by
`max_horizon_h` (48). **The instant defaults to the pinned weekly reset**: the
scraped `/usage` reading that pins the allowance carries it, so `--arm` alone is
the normal form and `--until` is the override for stopping short. It was a
required argument for one afternoon, until the owner asked why he was retyping a
number already on disk — which is how a wrong date gets typed. **Early in a week
the derived deadline is refused**, because a reset 160 hours out is not something
about to expire. The instant is also the expiry: `CONF.burndown()` reads a passed
`until` as **not a burndown**, with no write from anyone, so forgetting to end
one cannot leave the safeties off. The same reading covers an unparseable
`until` — an unreadable date must never widen a wave.

*Pinned to a fresh reading.* The percentages here are DERIVED ([budget.md](budget.md)), and
burndown is the only mode that spends to the wall, so it is the only one that
refuses a stale denominator: `pin_max_age_h` is **4**, tighter than the 24 h the
cache itself enforces, because at a 97% stop the margin for drift is three
points. **The precondition costs one command**: `/usage` writes what it rendered
into the session transcript, `fleet-usage-reading.py --scan` pins it, and
arming runs that refresh itself. So the ceremony is two commands, and the second
takes no arguments: run `/usage`, then `--arm`. **97 and not 100 for the same reason** — a proxy reading three points
low puts 97% of it at 100% of the real thing, and the one cost burndown must not
pay is the *start* of the next week.

**A 429 ends the mode rather than pausing it** (owner, 2026-09-08). Normally a
429 is a throttle to wait out; in burndown the fleet is already at the wall and
there is nothing to back off into. The leg lands what is in flight and runs
`--clear`, which reverts the latch to `mode=normal` rather than deleting it — so
the pump survives and the ordinary 90% gate decides what happens next, which at
97% used is a HOLD it reaches by itself. An empty queue and a hard fault end it
the same way; burndown spends the allowance on work that already exists and
authorises nobody to invent more.

**Two extra guardrails, because it runs unattended at full width:** no `bench`
tasks even by the supervisor's own hands, and no new numbered decisions. The
first is about `hw_lock` with nobody watching; the second is that a decision is
the most expensive thing in this suite to reverse, and this is the one mode
explicitly optimising for volume.

**A withheld decision is owed, and owing it means dropping an inbox file** —
not a log line. The first run produced five and recorded them three ways: one
task, two `open.md` sections, and two that lived in `supervisor-log.md` alone,
which folds daily and rolls to `log-archive/`. Volume is the point of this mode
and deferred design is its bill; a bill nothing dispatches from is not a bill.

## What the first run measured, 2026-09-08

Armed 22:06 at weekly 89.0%, stopped itself 01:51 at 97.6% by reaching its own
cap five hours before the deadline. **28 units, none blocked, no 429**, 16.3M
billable — about **582K per unit** — and the next week started clean. The three
refusals all held and the mode is worth keeping. Three corrections, though:

**The width never happened, and the prediction above was wrong about why.** A
leg cannot hold more workers in flight than it has units left, so `units_per_leg
= 4` bound before `max_workers` ever did: every leg printed a suggested wave of
**12**, dispatched **4**, and said so in its own log entry. Git contention and
the bench were never reached. `max_workers` is **6** now — `.claude/leg.md`
caps a leg at a hard 6 units and the fleet runs one leg at a time, so 6 is the
widest this design goes. Past that needs concurrent legs, and that is where the
contention question really lives.

**So burndown buys hours, not speed.** Throughput per hour barely moved: 7.2
units/hr in normal mode earlier that same evening against 7.7 in burndown, both
running 4 workers. The 3h37m were the whole win, and they were worth having,
because the alternative was zero.

**Reaching the cap is a trapdoor, not a pause.** The last leg reasoned that
leaving the latch in place would resume the fleet at the reset. It does not:
a leg's death wakes the listener, but nothing wakes a listener that has stopped
ticking, and five hours of a fresh weekly window went by with 43 tasks queued.
**Ending a burndown needs a plan to restart the fleet, and that plan is the
owner saying so.** `fleet-deadman.py` now tells the two cases apart — a HOLD is
an FYI, a fleet that could be running and is not is a page.

One mechanical note: `--refill-owed --wave <n>` is unsatisfiable for any `n`
above the dispatchable scope count, since refill allows one task per
sub-project per slot and there are ten scopes. It reported "owed" all night and
could never clear.
