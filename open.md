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

**The tally is trustworthy from 2026-09-05 and not before.** Until then the rule
was "spawn it and never wait", which [protocol.md](protocol.md) §10 required the
fold commit to summarise before the reviewer could report — so a `no findings`
line was a prediction, not a result. Leg 011 wrote three of them that way and
happened to be right. The reviewer is now collected immediately before the entry
is written. **Read the eight lines that predate the change as weaker evidence
than the ones after it**, and count the twenty from here.

## Compaction is scheduled, and the reserve is calibrated against one pass

**Closed 2026-09-04.** A cap used to be a wall discovered by the worker whose
edit it refused, which converted unrelated work into a compaction task
mid-flight. It is now a **reserve**: the last 10% of a file's limit is writable,
the gate still passes, and the file must be named on a `**Compacts:**` line of an
open `tasks/` task — filed by whoever spends the reserve, in the same commit.
`check-doc-size.py` fails on an unfiled file in reserve and names it;
`--pressure` lists both bands; `queue-status.py` gates out an `Owner: required`
task so no worker is sent at a reserved path.

**Why the filer and not a cron.** [DOC-COMPACTION-PASS.md](../embarch-doc/DOC-COMPACTION-PASS.md)
warns against compacting a subsystem still in flux — it writes a clean
statement of something about to be wrong and destroys the alternatives you are
about to need — and no script can tell. The actor who just worked in that
subsystem can. So the task carries `**In flux:**`, and `yes` parks it naming
what unparks it. Three of the seven filed on the day the mechanism landed are
parked, which is the mechanism working rather than a backlog.

**§7's question is still human, and now it is attached to something.** A
compaction task's `Done when` requires it answered in the commit message, in the
compactor's own words. That makes it reviewable, not verified — unchanged from
before, and it is not clear anything could verify it.

**What is still open, and it is two things.**

- **The reserve is one cycle of runway, not a steady state.** 10% of a 12 KB
  decision group is ~1.2 KB and of a 5 KB `open.md` is ~512 B. The corpus grows
  because work happens; this buys the crossing being recorded and judged, and
  nothing about the growth rate.
- **`suite/features.md` is in flux permanently** — it is an inventory of a suite
  under development, so a row lands about as often as a task does, and there is
  no quiet state to wait for. `tasks/suite/002` parks on the owner picking a
  shape and lists the four candidates, none free.

**The calibration is one pass deep.** 90% was chosen from a single 2026-09-04
sitting across twelve files. Two findings from it that any future tuning should
respect: a good pass **adds** bytes — the protocol-doc commit deleted ~900 gross
and netted 335, because the read that finds cold prose is the read that finds the
defects worth fixing — so a pass cannot be budgeted by expected yield; and the
recoverable bytes were **not** cold sentences but a claim held in two of the four
files, worth ~1.2 KB in `umbrella` alone. `check-duplication.py` reports that
class, advisory only.

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

## Whether the framework's prose is portable

**Answered 2026-09-04, differently than asked.** The question was whether to
genericize `protocol.md` and `ops.md`'s suite-specific prose. The owner's answer:
EmbArch references are correct — the fleet *is* part of EmbArch — but **client
names must never appear in any of these repos**, and they did.

That turned into a scrub across all ten repos plus a history rewrite: an exported
type, a config value, board identifiers, 43 files of prose, and 1,540 committed
build artifacts leaking a client workspace path. Verified clean from fresh clones
across every ref and tag.

**What is still open.** Nothing prevents the next one. A name reaches these repos
through ordinary work, and no check looks for one — the audit that found these
was a grep somebody thought to run. A `check-client-names.py` in the doc gate,
reading a denylist kept outside the repo, is the obvious shape and is not built.

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
