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
fleet.toml: 12 workers instead of 6, stops at 97% instead of 90%, and `taper =
0`. `suggest()` already reads a zero band as full width, so the mode is config
and a latch, **not a second code path**. Everything else about a leg is
unchanged: same 4 units, same reviewer, same commits to `main`. That is the
whole design constraint — a mode that also changed how work is done would be a
second fleet, held equal to the first by nothing.

**Three properties are load-bearing, and each is a refusal in
[`scripts/fleet-burndown.py`](scripts/fleet-burndown.py).**

*Manual.* Nothing self-arms it. A mode that decides on its own to spend the rest
of the allowance can decide wrong at 3 a.m., and only the owner knows whether he
wants the seat tonight.

*Deadlined.* `--until` is required and bounded by `max_horizon_h` (48). The near
reset instant is the entire justification, so it is also the expiry:
`CONF.burndown()` reads a passed `until` as **not a burndown**, with no write
from anyone, so forgetting to end one cannot leave the safeties off. The same
reading covers an unparseable `until` — an unreadable date must never widen a
wave.

*Pinned to a fresh reading.* The percentages here are DERIVED ([budget.md](budget.md)), and
burndown is the only mode that spends to the wall, so it is the only one that
refuses a stale denominator: `pin_max_age_h` is **4**, tighter than the 24 h the
cache itself enforces, because at a 97% stop the margin for drift is three
points. **97 and not 100 for the same reason** — a proxy reading three points
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

**What is untested is the width.** 12 is the owner's number and the binding
constraint is not tokens — it is git contention on `main`, since every unit
lands through one supervisor, and the single dev bench. Some of the extra width
will show up as workers queued to land rather than throughput. The first
burndown is also the measurement.
