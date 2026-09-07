# Developing the fleet

**Status:** active, 2026-09-04. How to change this repo and get the change into
a running instance. The design is in [protocol.md](protocol.md); this is the
loop you actually run.

## The loop

```sh
$EDITOR templates/... | scripts/... | protocol.md      # 1. author
python3 scripts/deploy.py                              # 2. render, gate, stamp, commit
git push && git -C ../embarch-doc push                 # 3. publish
/fleet start                                           # 4. re-arm, IF §4 says so
```

`deploy.py` refuses to run while the fleet is live. **With the fleet running,
commit and `deploy.py --queue` instead** — it pins the SHA and a leg boundary
lands it, so editing a rule no longer costs the fleet its uptime (§4.1). Stopping
the fleet to deploy is still available and still correct; it is just no longer
the price of picking up the pen.

## 1. Authored here, generated there

The single most common mistake is editing the copy. **Everything in the instance
repo's `.claude/`, its four protocol READMEs, and its five fleet scripts is
output.** A hand-edit there survives until the next deploy and is then silently
reverted — which is why `install.py --verify` is a gate in that repo's
`check-docs.py`, and why it names the file rather than just failing.

**`--verify` and `--check` answer different questions, and only one belongs in a
gate.** `--verify` asks *was anything generated hand-edited since the last
install*, by hashing against the manifest `deploy.py` records in
`.fleet-version`. `--check` asks *does the instance match this working tree*,
which is what a deploy wants to know. Until 2026-09-06 the gate used `--check`,
so it went red whenever the instance was merely **behind** — the normal state
between `deploy.py --queue` and the boundary that lands it, and the state of any
tree where a template is edited and not yet deployed. A queued deploy therefore
turned `check-docs.py` red for every worker and every merge gate for its whole
window, which is how `--queue` — built to deploy *without* stopping the fleet —
managed to block it instead.

The residue is deliberate: while a deploy is queued the gate no longer says the
instance is behind. Two things already do, and neither is a gate — the
`pending-deploy` latch, and `deploy.py --dry-run`.

| You want to change | Edit | Instance gets |
|---|---|---|
| What the supervisor or worker agent does | `templates/.claude/agents/*.md` | a rendered copy |
| The listener, its cron prompt, the Slack vocabulary | `templates/.claude/commands/fleet.md` | a rendered copy |
| How a leg runs | `templates/.claude/leg.md` | a rendered copy |
| The watchdog, its cron prompt, the staleness threshold | `templates/.claude/commands/fleet-watch.md` | a rendered copy |
| The claim protocol, the drop format, fragment rules | `templates/protocol/*.README.md` | `tasks/README.md`, etc. |
| Ownership, queue state, budget, alerting, the fold | `scripts/*.py` | a shim — no re-render needed |
| A path, channel, identity or limit | `fleet.toml` | **both**, see §3 |
| The rules themselves | `protocol.md`, `ops.md`, `risks.md`, `open.md` | nothing — read in place |

**Placeholders.** A template may use `{{FLEET_ROOT}}`, `{{DOC_REPO}}`,
`{{FLEET_REPO}}`, `{{STATE_DIR}}`, `{{SLACK_CHANNEL}}`, `{{SLACK_OWNER}}` and the
rest of what `scripts/fleetconf.py --help` prints, plus `{{FLEET_REL}}`, which
`install.py` resolves **per output file** — a link from `tasks/README.md` needs a
different number of `../` than one from `.claude/commands/fleet.md`. An unknown
placeholder is a hard error, not a silent passthrough: a rule that ships literal
braces to an agent is a rule with a hole in it.

**Which to use.** Markdown links use `{{FLEET_REL}}`, so `check-links.py`
resolves them on disk. Prose in `.claude/` uses the absolute `{{FLEET_REPO}}` —
an agent has no stable working directory, and an instruction to read a file has
to be unambiguous.

## 2. When a change actually takes effect

Not all at once, and the differences have bitten before.

| Change | Live for |
|---|---|
| `scripts/*.py` | the next invocation — shims, so immediately |
| `protocol.md`, `ops.md`, `risks.md` | the next agent that reads them; a **running leg already read them** |
| `.claude/agents/*.md` | the next agent spawned. A running leg keeps the definition it started with |
| `.claude/leg.md` | the next leg |
| `.claude/commands/supervise.md` | the next `/supervise` **typed by the owner** — a leg never reads it |
| `.claude/commands/fleet.md` — vocabulary | the next tick, which re-reads the file |
| `.claude/commands/fleet.md` — **the cron block** | **only after re-arming** |
| `.claude/commands/fleet-watch.md` — **the cron block** | **only after re-arming `/fleet-watch`** |

Those last two rows are the ones to remember. Arming copies the heartbeat prompt
into a cron job, so the live job keeps the wording it was created with however
many times you edit the file. They drifted once already.

**`deploy.py` compares the render against what the window was actually armed
with, per file, and names which one owes a re-arm.** Prose is re-read from disk
every tick and owes nothing; the block is what a live cron job froze. Arming
records that block (`fleet-armed.py --stamp`, step 3 of both commands) because
every repo-side inference of it has been wrong: keying on the filename cried
wolf over a line of prose, the working tree read new-against-new after a
hand-run `install.py` and stayed silent through leg 029, and `HEAD` answers
whether a deploy committed the wording rather than whether any window read it.
**An unstamped prompt is owed**, which is how a window armed before this existed
reports itself; it self-clears on the next arming.
`scripts/fleet-armed.py --check --diff` answers the same question at any time,
not only after a deploy.

## 3. Changing fleet.toml is two changes

A config value reaches the scripts **immediately** — they read it at
invocation — but reaches the rendered templates **only through an install**. So
between editing `fleet.toml` and deploying, the two disagree: a script pointed at
the new channel, an agent definition still naming the old one. Deploy in the same
sitting, and never with the pump latched.

## 4. Deploying while the fleet is live

Don't do it directly — **queue it instead**, and keep working.

`deploy.py` refuses if the pump latch exists or a worktree is registered under
the worktree root, because changing the rules under a running supervisor means a
leg that read half its protocol from one version and half from another, and there
is no version marker in a log entry that would let you tell afterwards.

Neither check is authoritative — the latch says the pump is on, not that a leg is
alive, and a leg between units holds no worktree. **The authoritative check is
`ListAgents` in a session**, which no script can run. So the old loop was
`fleet stop`, watch for the leg to finish its unit, deploy, re-arm.

**That loop was the single most expensive thing about editing a rule.** Over the
14 h window ending 2026-09-06, ~6.6 h had no leg running at all, and **~3.7 h of
it was the fleet stopped so the owner could hold the pen.** None of it was a
capacity problem; it was a lock held for the length of a writing session.

### 4.1 Queue a deploy, land it at a leg boundary

```sh
git commit                                   # in this repo, as always
python3 scripts/deploy.py --queue            # pins HEAD in the state directory
git push                                     # framework first, now
```

`--queue` refuses a dirty tree and refuses a no-op, then writes
`pending-deploy` in the state directory recording the exact framework SHA. The
fleet keeps running. At the next leg boundary the listener — which has just
established with `ListAgents` that no leg is alive, the one moment this is safe —
spawns an `embarch-deployer`, whose entire job is:

```sh
python3 scripts/deploy.py --from-latch
```

That renders the **pinned** SHA, runs both gates, stamps, commits the generated
paths, pushes both repos framework-first, and deletes the latch. Then it reports
one line and dies.

**What makes it safe is the pin, not the agent.** The deployer authors nothing:
it renders content you already committed to a repo no leg ever checks out, and
**any render input that moved past the pin is a *refusal***, not a fresher
deploy — it names the paths and stops.

**HEAD itself is expected to move, and must be allowed to.** The fleet commits
`supervisor-log.md` to *this* repo on every fold, so a latch waiting for a
boundary watches HEAD advance every ten minutes. Requiring strict equality —
which it did until 2026-09-06 — meant a `--queue` issued while the fleet was
running could never survive to the boundary it was queued for, which is the only
case `--queue` exists for. So the rule is the pin is an **ancestor** of HEAD and
`git diff <pin> HEAD` touches nothing but the log and `log-archive/`. The
property is unchanged: what the deployer renders is exactly the content you
pinned. Caught on the first `--queue` issued during a live leg, which is also the
only way it could have been caught.

Every liveness check except the pump latch still applies — a registered worktree or a
surviving `agent/*` branch still refuses — which is exactly the difference
between "the pump is on" and "a leg is mid-unit".

**Two things stay yours.** A **re-arm** — `deploy.py` says when one is owed and
the deployer relays it, but arming is a Claude Code session and no agent may do
it, so a changed heartbeat prompt sits dormant until you type `/fleet start`. And
a **red gate**: the deployer leaves the instance rendered and uncommitted with
the latch still pinned, and stops. Fix the template here and re-queue.

`python3 scripts/deploy.py --queue --clear` unpins. `--force` still exists for a
direct deploy when you have checked `ListAgents` yourself and it is genuinely
idle.

## 5. Versions and rollback

`install.py` stamps `.fleet-version` into the instance: the framework SHA, the
config it rendered from, and when. That file is committed there, so
`git log .fleet-version` in the instance is the deploy history, and a leg that
misbehaves can be matched to the framework version it ran under.

**Rollback is a revert plus a deploy**, never an edit in the instance:

```sh
git revert <bad-sha>          # in this repo
python3 scripts/deploy.py     # re-render, re-gate, re-stamp
```

The instance's generated files are not the artifact to fix — they are the output
of the artifact.

## 6. What deploy.py will not do for you

- **Push.** Two repos, and pushing the instance before the framework would leave
  a stamp naming a SHA nobody else can fetch. It prints both commands in order.
- **Re-arm.** That is a Claude Code session doing `/fleet start`, not a shell.
- **Restart a leg.** The pump is the owner's latch, by design ([protocol.md](protocol.md) §2).

## 7. Testing a change without a fleet

`install.py --repo <path>` renders into any git repo, so a scratch clone is a
safe target for a template change. The four scripts run standalone against a
real instance:

```sh
python3 scripts/fleetconf.py                      # what config resolves to
python3 scripts/queue-status.py --no-supervisor   # what a leg would dispatch
python3 scripts/usage-budget.py --suggest         # what wave size it would pick
python3 scripts/fold-commit.py --check            # do the two repos agree
python3 scripts/fleet-alert.py --dry-run "test"   # payload, sends nothing
```

There is no test suite. Two gates run: `scripts/check-fleet-doc-size.py` caps
*this* repo's docs as a ratchet before anything renders (nothing did until
2026-09-05, which is how `protocol.md` and `ops.md` reached 32 KB), and then the
instance's `check-docs.py`, which
`deploy.py` runs for you, and it catches the failure that actually recurs: a
rendered file whose links no longer resolve.
