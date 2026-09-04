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

`deploy.py` refuses to run while the fleet is live, so the normal order is
`fleet stop`, deploy, re-arm. It says which of those you still owe.

## 1. Authored here, generated there

The single most common mistake is editing the copy. **Everything in the instance
repo's `.claude/`, its four protocol READMEs, and its five fleet scripts is
output.** A hand-edit there survives until the next deploy and is then silently
reverted — which is why `install.py --check` is a gate in that repo's
`check-docs.py`, and why it names the file rather than just failing.

| You want to change | Edit | Instance gets |
|---|---|---|
| What the supervisor or worker agent does | `templates/.claude/agents/*.md` | a rendered copy |
| The listener, its cron prompt, the Slack vocabulary | `templates/.claude/commands/fleet.md` | a rendered copy |
| How a leg runs | `templates/.claude/commands/supervise.md` | a rendered copy |
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
| `.claude/commands/supervise.md` | the next leg |
| `.claude/commands/fleet.md` — vocabulary | the next tick, which re-reads the file |
| `.claude/commands/fleet.md` — **the cron block** | **only after re-arming** |

That last row is the one to remember. Arming copies the heartbeat prompt into a
cron job, so the live job keeps the wording it was created with however many
times you edit the file. They drifted once already. `deploy.py` diffs that file
and tells you when a re-arm is owed.

## 3. Changing fleet.toml is two changes

A config value reaches the scripts **immediately** — they read it at
invocation — but reaches the rendered templates **only through an install**. So
between editing `fleet.toml` and deploying, the two disagree: a script pointed at
the new channel, an agent definition still naming the old one. Deploy in the same
sitting, and never with the pump latched.

## 4. Deploying while the fleet is live

Don't. `deploy.py` refuses if the pump latch exists or a worktree is registered
under the worktree root, because changing the rules under a running supervisor
means a leg that read half its protocol from one version and half from another,
and there is no version marker in a log entry that would let you tell afterwards.

Neither check is authoritative — the latch says the pump is on, not that a leg is
alive, and a leg between units holds no worktree. **The authoritative check is
`ListAgents` in a session**, which no script can run. So: `fleet stop`, watch for
the leg to finish its unit, then deploy. `--force` exists for when you have
checked yourself and it is genuinely idle.

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

There is no test suite. The gate is the instance's `check-docs.py`, which
`deploy.py` runs for you, and it catches the failure that actually recurs: a
rendered file whose links no longer resolve.
