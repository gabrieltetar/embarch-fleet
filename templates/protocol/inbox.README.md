# inbox

Where any thread hands work to the fleet without touching the queue, `main`, or
each other.

    inbox/<scope>-<slug>.md      one file per request, never committed

**Nothing here is in git** (`.gitignore`, except this README). That is the point:
a thread drops a file and is done — no commit, no push, no rebase, and no chance
of sweeping someone else's in-progress edits into a commit, which is the
collision [the protocol]({{FLEET_REL}}/protocol.md) §12
records happening twice on 2026-09-02. One file per request rather than one
shared file, for the same reason `changelog.d/` is shaped that way: two threads
appending to one file conflict on the same lines.

## What to write

**A complete task file**, exactly the format in [tasks/README.md](../tasks/README.md)
— title, `**State:** open`, `**Source:**`, `**Scope:**`, `**Hardware:**`, then
`## What` / `## Why now` / `## Done when`. Two differences, both because you do
not own the queue:

- **No number.** Name the file `<scope>-<slug>.md`. The supervisor assigns `NNN`
  when it files the task, so two threads can never pick the same one.
- **`Hardware:` is a claim, not a verdict.** Write your honest read; the
  supervisor re-checks it. An unclassified or wrong `none` is the failure that
  matters here — it is what gets a task dispatched to a worker that cannot
  finish it.

Being asked for the full format rather than loose prose is deliberate: it forces
the writer to state a `Done when`, which is the part a supervisor cannot invent
later from a one-line wish.

## What happens to it

At phase 1 the supervisor reads this directory, validates each file, assigns the
next free number for its scope, moves it into `tasks/<scope>/`, commits that, and
deletes the drop. **It announces what it picked up in `{{SLACK_CHANNEL_NAME}}` before
dispatching** — naming the file and what it will do — so there is a window to say
stop, the same one suite-scope work gets
([ops]({{FLEET_REL}}/ops.md) §4).

A file that does not parse is **left here, not deleted**, and named in the digest.
Silently dropping someone's request is worse than carrying a broken one.

## Who may write here

Any thread on this machine, and **workers too**. A worker that finds something
outside its own task drops it here instead of reaching outside its ownership row
— which is how `study-designer/002` (the test-harness stack overflow) should have
been captured on 2026-09-03, rather than the supervisor hand-writing it.

That does mean the fleet can generate its own backlog. Worth watching: a queue
that grows only from what the fleet noticed while working is a queue that can
drift away from what the owner actually wants done.
