# Fleet: open questions

**Status:** active, 2026-09-04. Unresolved questions and known limitations, each
with what would unblock it. Distinct from [risks.md](risks.md), and the split is
load-bearing: a **risk** is a cost the owner accepted and is not looking to
remove; an **open question** is something nobody has decided yet. The risk
register was doing both jobs, which is why several of these had nowhere to live.

## Detecting a wedged listener

`CronCreate` fires only while the REPL is idle, so a tick that *hangs* — rather
than fails — takes the fleet dark with the pump still latched, and `fleet stop`
cannot be delivered either, because a listener mid-query cannot read the
channel. Nothing detects this from inside the process, and [ops.md](ops.md) §3
rules out anything that survives the editor closing. On 2026-09-03 it cost five
hours.

**What would unblock it:** a second, report-only window. It observes a tick file
the listener touches, and alerts when the mtime goes stale — it can never spawn
work, so closing the fleet's window still stops everything and the kill switch
keeps its meaning. Decided in principle 2026-09-04, not built.

## The fold still runs in the instance's main checkout

[scripts/fold-commit.py](scripts/fold-commit.py) removed the `git add -A` half
of this — staging is by explicit path and a path outside the unit's set is an
error. What remains is that a leg and the owner share one working tree, so a
`git checkout`, a rebase or a stash during a fold still reaches the owner's
uncommitted edits.

**What would unblock it:** give a leg its own worktree of the instance repo, the
way workers already get one. The complication is `inbox/`, which is gitignored
and therefore exists only in the main checkout — the drain would read drops by
absolute path and write task files in the worktree.

## Nothing reads a diff for intent before it lands

`main` across eight repos moves on green alone; [protocol.md](protocol.md) §10's
shared-crate carve-out is deliberately narrow and is a judgement the supervisor
is told to make, not a mechanism. The characteristic failure is a change that
passes every check and contradicts a locked-in decision, and it will not
announce itself.

**What would unblock it, without giving up merge-on-green:** a reviewer agent
spawned *alongside* landing, reading the diff against that sub-project's
`decisions.md` and the reversals index. Findings go to `inbox/` and the unit's
log entry; a confirmed contradiction is reverted by SHA — which is the first
thing that would ever use the SHAs §11 already requires. Open: whether it runs
per unit or only on diffs a script flags as high-blast-radius, since per unit
roughly doubles agent spawns.

## Doc-size caps block work and nothing sees it coming

Five files sit above 99% of `min(cap, baseline)`. A task that cannot be written
without exceeding one becomes a compaction task wearing a feature task's
clothes, and the supervisor discovers this only when a worker reports.

**What would unblock it:** a `--pressure` mode on `check-doc-size.py` that
refill reads, filing a compaction task per file above threshold. A worker may
already write its own four files, so this needs no ownership change. Undecided:
DOC-COMPACTION §8 warns against compacting a subsystem still in flux and a
script cannot tell — restricting it to sub-projects with no other task in flight
is a proxy, not an answer. Whatever runs it must record §7's human question in
the log rather than skip it.

## The budget is calibrated against nothing, and its feeder is now versioned

[ops.md](ops.md) §2's thresholds and taper are guesses until many legs have run.
Separately, the thing that feeds them — `statusline-usage.py` — had no history
and no check; it is now [scripts/statusline-usage.py](scripts/statusline-usage.py).

**What would unblock the calibration:** legs that report real percentages. On
this machine they never arrive, so every leg reports DEGRADED, and DEGRADED is
indistinguishable from a broken feeder. Narrowing that needs a payload capture,
not more code.

**Still open:** `~/.claude/settings.json` must point `statusLine` at the
versioned copy, and nothing asserts that it does.

## Whether a second instance is real

This repo is shaped for portability and has exactly one instance. Until a second
one exists, `fleet.toml`'s division between framework and instance is a
hypothesis — the likely discovery is that something suite-specific is still
hard-coded in prose rather than in config, since only paths and identifiers were
mechanically extracted.
