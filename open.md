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
touches `{{STATE_DIR}}/tick` at the end of every tick and the watchdog alerts
when that mtime goes stale by 25 minutes. Five hours became about ten.

**What is still open.** Nothing *recovers* a wedged listener — the alert tells
the owner to go close a window. A wedged listener also cannot be sent
`fleet stop` by anyone, so the watchdog is not a second control plane and must
not become one. And it cannot distinguish a hung tick from a closed window from
a slept machine; all three want the same response, which is why it does not
guess, but it means the alert is never diagnostic.

**What would close it:** nothing safe, on current understanding. Anything that
could restart a leg would have to survive the editor closing, which is the kill
switch ([ops.md](ops.md) §3). This may simply be the floor.

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

This repo is shaped for portability and has exactly one instance. Until a second
one exists, [fleet.toml](fleet.toml)'s division between framework and instance is
a hypothesis — the likely discovery is that something suite-specific is still
hard-coded in prose rather than in config, since only paths and identifiers were
mechanically extracted.

**What would close it:** standing one up somewhere else, even a scratch clone.
`install.py --repo <path>` renders into any git repo, so the experiment is cheap
and has not been run.
