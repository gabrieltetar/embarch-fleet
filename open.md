# Fleet: open questions

**Status:** active, 2026-09-04. Unresolved questions and known limitations, each
with what would unblock it. Distinct from [risks.md](risks.md), and the split is
load-bearing: a **risk** is a cost the owner accepted and is not looking to
remove; an **open question** is something nobody has decided yet. The risk
register was doing both jobs, which is why several of these had nowhere to live.

An entry stays here after the work lands if something about it is still
undecided. It leaves when there is no question left, not when code exists.

## A wedge is reported, never recovered

`/fleet watch` (2026-09-04) is a second window with no hands: the listener
touches a `tick` file in the state directory at the end of every tick and the watchdog alerts
when that mtime goes stale by 25 minutes. Five hours became about ten.

**Narrowed 2026-09-04:** the watchdog may now delete the pump latch as well as
alert. That is safe in a way a restart never could be — **stop, never start** —
and §3's rule bites on actions that take a stop away, not on actions that are
one. It means a wedge no longer ends with the fleet quietly resuming on its own.

**What is still open.** Nothing *recovers* a wedged listener; unlatching only
stops the next leg from being spawned, and whatever is already running keeps
running until the window is closed. The watchdog cannot deliver a graceful
`fleet stop` either, because a wedged listener relays nothing. And it cannot
distinguish a hung tick from a closed window from a slept machine; all three
want the same response, which is why it does not guess, but the alert is never
diagnostic.

**What would close it:** nothing safe, on current understanding. Anything that
could *resume* work would have to survive the editor closing, which is the kill
switch ([ops.md](ops.md) §3). This is probably the floor.

## The reviewer's scope is unsettled

`embarch-reviewer` (2026-09-04) reads one unit's diff against its decisions and
the reversals index, spawned alongside landing and never waited for.

**What is still open.** Whether it should run per unit at all. It roughly
doubles agent spawns, and today the budget decides by skipping it under pressure
— which means the units most likely to go unreviewed are the ones landing when
the fleet is busiest. The alternative is a script that flags high-blast-radius
diffs (shared crate, wire type, a retired decision, a deleted doc) and reviews
only those, which is cheaper and catches less.

**What would settle it:** several legs' worth of findings. If per-unit review
produces nothing over twenty units, the flagged-diff version is strictly better.
Nobody has run it yet.

## Compaction is detected but not scheduled

`check-doc-size.py --pressure` (2026-09-04) reports files near their effective
limit, and a leg reads it *before* dispatch so a task that cannot be written
without a compaction pass says so in its own file.

**What is still open.** Nothing files the compaction task. **15 files sit above
95%** of `min(cap, baseline)` — including `embarch-api/spec.md` with three bytes
of headroom — so this is the queue's real blocker, not a future one.

The reason it reports rather than files is [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md)
§8: compacting a subsystem still in flux writes a clean statement of something
about to be wrong and destroys the alternatives you are about to need. No script
can tell. "No other task in flight for that sub-project" is a proxy and a weak
one.

**What would close it:** a decision about who judges §7's question — *can
`spec.md` alone answer what someone needs to work on this component today* — for
a pass the fleet ran unattended. Today the leg is told to record its answer in
the log, which makes it reviewable but not verified.

## The budget is calibrated against nothing

[ops.md](ops.md) §2's thresholds and its taper are guesses until many legs have
run. The feeder half is closed: `statusline-usage.py` is versioned in
[scripts/](scripts/), and `usage-budget.py` asserts `settings.json` points at
that copy rather than an unversioned one.

**What is still open.** Real percentages have never arrived on this machine, so
every leg reports DEGRADED, and there is nothing to calibrate against. Narrowing
*why* needs a payload capture, not more code — `rate_limits` arrives only for a
Pro/Max seat, only after a session's first API response, and each window
disappears once its `resets_at` passes.

## Whether a second instance is real

**Tested 2026-09-04** against a scratch repo with its own `fleet.toml` — a
different root, doc-repo name, channel, owner, limits and reserved list. It
rendered clean, the shims executed, and the ownership check read the *fake*
reserved list and derived scopes from the *fake* repo tree. Nothing of this
instance leaked into it.

It found three real defects, all now fixed, and the shape of them is worth
keeping: **every one was a value derived from the wrong source.** `FLEET_REPO`
was guessed as `<root>/embarch-fleet` while `FLEET_REL` was computed from
`__file__`, so the two disagreed the moment the framework was not beside the
instance's root. The shims baked in the installing machine's absolute path,
which is committed to the instance repo and therefore wrong on any other
checkout. And the reviewer template reached the reversals index through
`{{FLEET_REL}}/../{{DOC_REPO_NAME}}/`, which resolved to nonsense.

**What is still open.** The test used a scratch repo, not a real suite: nothing
proves the *prose* is portable. `protocol.md` and `ops.md` still say "eight
repos", name `embarch-core` and the probe, and describe a hardware topology that
is this suite's. A second real fleet would have to rewrite paragraphs, not just
`fleet.toml` — and none of that is mechanically detectable, which is why this
entry stays open after the test passed.
