# embarch-fleet

A supervisor keeps a wave of short-lived worker agents in flight, each owning one
sub-project, and lands their work itself. A **leg** is one supervisor's whole
life — four tasks, then it dies and hands off to a successor through a written
log entry. A **pump** latch keeps legs coming until it is switched off. Nobody
approves anything routine, and closing the editor stops all of it.

This repo is that machine: the rules it runs under, the scripts that enforce
them, and the agent definitions that carry them. It is deliberately **not** the
repo the fleet works in.

## Why it is its own repo

**A supervisor that can edit its own constraints has none.** The fleet works in
an *instance* repo; the rules live here, and a leg never checks this repo out.
That was previously enforced by a denylist of filenames inside the instance
repo, and it broke once already: the risk register was §12 of the protocol until
it hit a size cap and split into its own file, and reserved content stopped
being reserved purely by moving. Nothing noticed for a day. A separate repo
cannot drift that way, because there is no path from a leg's diff to a rule.

The second reason is this one: **you can stand up another fleet.** Everything
machine-specific is in [fleet.toml](fleet.toml) — one file, about forty lines.

## Standing one up

```sh
git clone <this repo>                 # beside the repo the fleet will work in
cd embarch-fleet
$EDITOR fleet.toml                    # root, doc_repo, scopes, Slack ids
python3 scripts/install.py            # writes .claude/ and the protocol READMEs
python3 scripts/install.py --check    # verify
umask 077 && $EDITOR .fleet/client-names   # names that must never reach a repo
```

The last line is not optional: `check-client-names.py` is in the doc gate and
**fails while the denylist is absent or empty**, because a check that silently
scans nothing is the muted-alarm failure this repo has already written down
once. It lives outside every repo — a committed list of the names you are hiding
is the leak it exists to prevent.

**Do not wire `--check` into the instance's CI**, which this line told you to do
until 2026-09-05 and nobody ever did. CI checks out one repo, so there is no
framework beside it to diff against; `check-docs.py` skips the check for exactly
that reason. The real guard is local and already in place — `--check` is one of
that wrapper's checks, every worker runs the wrapper before it reports and every
fold runs it again on the merge result, so a hand-edit of a generated file is
caught within one unit. An instruction nobody followed for a check that already
had a home was worse than no instruction: it read as a gap.

`install.py` writes into the instance repo the things that only work in place:
`.claude/commands/` and `.claude/agents/`, which load only from the working
directory's own `.claude/`, and the four protocol READMEs, which are read where
they sit. Those are **copies, rendered from [templates/](templates/)**, so
`--check` re-renders and diffs — the instance copy is output, not source, and
editing it there is a change that the next check reverts.

The scripts are **shims** rather than copies: every doc in the suite names
`scripts/check-ownership.py` and workers invoke it from worktrees of varying
depth, so the path has to keep working, but there must be exactly one
implementation. Two held equal by a checker is still two.

Then, in the instance repo: arm a listener window with `/fleet start`, and say
`fleet start` in the channel to latch the pump.

## What is here

| File | What it is |
|---|---|
| [protocol.md](protocol.md) | The design: roles, the ownership map, the queue, the worker contract, the leg, the gate, the log |
| [ops.md](ops.md) | Running it: arming, the usage budget, driving it from a phone, Slack as a control plane, dreaming |
| [risks.md](risks.md) | The risk register — what each choice traded away and what its failure looks like |
| [DEVELOPING.md](DEVELOPING.md) | Changing this repo and deploying the change: what is authored vs generated, when a change takes effect, rollback |
| [open.md](open.md) | Unresolved questions and known limitations, each with what would unblock it |
| [supervisor-log.md](supervisor-log.md) | One entry per unit, newest first. The review surface, and the relay handoff |
| [fleet.toml](fleet.toml) | The instance: paths, channel, identity, limits, the ownership lists |
| [scripts/](scripts/) | The enforcement — ownership, client names, queue state, usage budget, alerting, the fold |
| [templates/](templates/) | What `install.py` renders into the instance repo |

Read `protocol.md` first, then `ops.md`, then `risks.md` — in that order, and
not `risks.md` instead of the protocol. To change any of it, `DEVELOPING.md`.

## What stays in the instance repo, and why

The queue does: `tasks/`, `inbox/`, `status.d/`, `changelog.d/`. The claim
commit on the instance repo's `main` **is** the double-dispatch interlock — two
supervisors cannot claim the same task because one of them loses a race in git —
and the queue is a view of docs that live there. Splitting them would buy a sync
problem and no safety. This repo ships their *protocol*; the instance holds
their *contents*.

`supervisor-log.md` is the exception that runs the other way: it is the fleet's
own output, so it lives here even though a leg writes it. That makes a unit's
fold two commits in two repos, which reopens a window the protocol closed by
making it one — so [scripts/fold-commit.py](scripts/fold-commit.py) commits both
or neither, and orders them so the survivable failure is an entry for a fold
that did not happen, never a fold nobody logged.

## Requirements

Python 3.11+ (`tomllib`), `git`, and Claude Code. The Slack control plane is
optional: without a webhook, `fleet-alert.py` exits 2 and says so, which is the
intended failure — a muted alarm that looks fine is worse than no alarm.
`check-client-names.py` applies the same rule to its denylist, with one
difference: it is in the gate, so its absence is red rather than merely loud.
