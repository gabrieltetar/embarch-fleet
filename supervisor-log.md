# Supervisor log

**Status:** active, 2026-09-03. Three batches ran before the relay ([protocol.md](protocol.md) §6) replaced them; entries below `batch 003` are per-batch, and everything after is per-unit.

One entry per **unit** — one task landed or blocked — **newest first**. Written
by the supervisor as part of landing that unit
([protocol.md](protocol.md) §6 step 4), and read by
the owner as the review surface for work that landed without approval (§11).

**It is also the relay handoff.** A leg dies after four units and the listener
spawns a successor whose step 0 reads these entries cold, with no other memory of
its predecessor at all. So an entry that omits something — a rebase that has not
settled, a `suite` task parked with a live 30-minute window, a failure likely to
recur — is a fact the next leg cannot recover, and it will act confidently
without it.

**Per unit rather than per leg** because a leg can be killed at any moment;
closing VS Code is a normal thing to do. An entry written at the end of a leg is
an entry that does not exist for the leg that got killed.

What *shipped* is not restated here — the workers' own `changelog.d` fragments
carry that into `history/<scope>.md`. This file carries what was **decided**,
what did not land, and what still needs a board.

**Folded daily.** On its first unit after local midnight a supervisor folds the
previous day's unit entries into one dated entry, keeping every SHA and every
debt. Per-unit entries would otherwise hit the roll cap every few days and the
handoff would get shorter and shorter — the opposite of what a relay needs.

Past **40 KB** the oldest whole days roll into `log-archive/` —
`scripts/fold-day.py --roll`, which never splits a day and always leaves the two
newest. The line was 25 KB and named the instance's `history/archive/`; neither
was right. This log lives in this repo, and 25 KB could not hold one folded day
(the `2026-09-04` entry below is 25 KB on its own), so nothing ever rolled it.

## Entry shape

The example below uses placeholders on purpose. It once used a real-looking date
and real-looking SHAs, and step 0 — which reads the newest entries as its
handoff — picked the *template* up as work that had run, complete with a hardware
debt that never existed. Second instance of the same root cause as batch 001's
recovery greps: documentation shaped exactly like the data it documents.

```markdown
## <yyyy-mm-dd HH:MM> — <scope>/<NNN> <slug>

**Decided:** anything the supervisor approved on the owner's behalf, suite-wide
first. If it decided nothing, say "nothing" — an empty line here is ambiguous.
**Merged:** `agent/<scope>/<task>` (code `<sha>`, doc `<sha>`). Always both SHAs —
under `embarch-dev-workflow.md` §6 there is no merge commit and no surviving
branch name, so the SHA is the only handle a revert has.
**Blocked:** `agent/<scope>/<task>` — why, and what state the task was left in.
**Reviewer:** `no findings` / `N finding — <inbox file>` / `skipped (<why>)`.
Exactly one of the three, always, and **collected before this entry is written**
rather than predicted — the reviewer is spawned at the merge and waited for
here, which is the only point in the unit where waiting costs anything and the
only point where the line can be true. Never `pending`, and never a fourth form:
whether per-unit review is worth double the spawns is undecided, and this line
is the only evidence that will settle it.
**Hardware debts:** what needs a board, and what board.
**Budget:** verdict at start and end, and the wave size it produced.
**Least sure about:** one sentence. Not optional.
```

**The heading's date and time are the wall clock at the fold, and
`fold-commit.py` writes them.** Do not type them and do not work them out — it
stamps the newest entry from the machine clock just before it commits, and says
so when what you wrote was more than five minutes out. Nothing used to do this
and nothing checked it, so the field was a guess: measured 2026-09-06 across all
63 entries, **41 were more than five minutes ahead of the fold that wrote them,
the worst by 63 minutes**, and the error grows monotonically within a leg and
resets at the next one — the signature of reading a clock once and estimating
from there. It is not cosmetic. `fold-day.py` groups a day by *this* date, so an
entry written at 23:50 and stamped 00:15 folds into the wrong day and nothing
says so; and under a full delegate this log is the only review surface
([protocol.md](protocol.md) §11), where a heading an hour out correlates with
nothing — not Slack, not `.fleet/tick`, not `git log`.

**Entries before 2026-09-06 17:00 carry the old estimated times**, and they are
not corrected: they are true in every other respect, and rewriting this file
wholesale is exactly what `fold-day.py`'s refusals exist to prevent. Read them as
±1 hour, and use the fold commit's own timestamp when the minute matters.

Every one of those seven markers is written literally, as `**Field:**` at the
start of a line, and `fold-commit.py` refuses a fold whose entry drops one or
bends one. That is newer than most of this file: `umbrella/010` below opens its
debt with `**Hardware debts: one, and it is free.**`, bolding the whole phrase,
which is invisible to the fold's own ledger — three of 2026-09-05's ten entries
lost a field that way. The shape is data, not decoration.

A folded day collapses that into one entry with the same fields, listing every
unit under **Merged** and **Blocked**:

```markdown
## <yyyy-mm-dd> — <N> units
```

---

## 2026-11-25 11:58 — core/162 a-test-run-opens-a-setup-window-between-benches

**Decided:** nothing suite-wide. Re-landed from the leg killed at about 10:15 (its worker had pushed both branches). Before every bench but the first, `drive` calls `Env::setup`; `CoreEnv` publishes a `setup` prompt in the one slot under the run's id (`POST /study/{run_id}/prompt` answers it, `GET /test-runs/{id}` shows it as `waiting_prompt`), step `setup:<bench>`, carrying the bench's configuration and a `missing` list that stays empty until the smoke check (EMB-368) exists. While it waits, `AppState::setup_window` holds the run id and `lease_middleware` admits a `SETUP_ADMITTED` list (enrolment, role board, by-serial delete, bootload ports, dev-bench link, signals, instruments), every call entered in the run log as `test_run_setup_call` with its token's scope; everything else stays `409`. A decline or the 15-minute timeout (`SETUP_WAIT_MS`, chosen, not measured, and added to the run's deadline per bench) is an `error` on that bench and the run goes on; an agent's answer is accepted and recorded `relayed`. **New core decision 139** in new `decisions/test-run-setup.md`; 137's open line now points at it. I read `src/api.rs`'s middleware diff before landing. **Mine, in this fold, from the reviewer's note:** 139 said "either token is admitted whole"; I added that on a `--service` Core decision 132's person-only routes still refuse the agent `403`, because `person_middleware` is layered outside the lease layer, which is what the code does.
**Merged:** `agent/core/162-a-test-run-opens-a-setup-window-between-benches` (code `80f6798`, ff from `9233136`; doc `384c208f`, the worker's `958de02a` cherry-picked onto `e12e81fc`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (585 passed, 2 ignored); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-380-test-runs-executor.md` (amended) assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a real two-bench fixture run on a bench, enrolling a board in the setup window between the two benches, in the person's session. The native Windows build of Core. **Deploy debt:** the installed service Core has no setup window until redeployed.
**Budget:** PROCEED (5-hour 12% at leg start).
**Least sure about:** the 15-minute setup wait is a guess, and with no smoke check yet the prompt tells the person nothing about what is missing, so the first real two-bench run is where the window's usefulness gets judged.

---

## 2026-11-25 11:54 — api/199 the-core-client-calls-the-confirmation-routes

**Decided:** nothing suite-wide. Re-landed from a killed leg: the leg that claimed `api/199`, `core/162`, `ui/122` and `chat/043` at 10:12 died with the Claude Code session at about 10:15 and folded nothing. Its `api`, `core` and `ui` workers had already pushed both branches (the presence rule: finished), so this leg gates and lands them; `chat/043`'s worker died mid-run with an uncommitted tree in both repos, which I committed to its branch as `chat: 0facb46`, `doc: 14bc0506` ("work in progress, recovered from a killed leg"), pushed, and removed the worktrees, for a resume dispatch later this leg. The unit itself: `CoreClient::pending_confirmations`, `confirmation_card(hash)` and `confirm(hash, nonce, surface)` over Core's three confirmation routes (core decision 133), each returning `serde_json::Value` (the previous leg's open question, settled by the worker as untyped), each mocked with the bearer header asserted and in the one-funnel sweep; no MCP tool or CLI verb, since a confirmation is the person's. Read before landing (shared crate): additive, through `send`, nothing renamed. No new decision. **Mine, in this fold:** `ui/121` unparked to `open`, its state line naming the three methods.
**Merged:** `agent/api/199-the-core-client-calls-the-confirmation-routes` (code `14ea8f3`, ff from `9f3f9e2`; doc `bdaaf7d9`, the worker's `666c137f` cherry-picked onto `17af2b2b`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (574 passed, 0 failed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-420-confirmation-client.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the methods have met only a mock Core.
**Budget:** PROCEED at leg start (5-hour 12%, weekly 9%, wave 6).
**Least sure about:** whether `ui/121`'s card will want typed answers after all; the client returns `Value`, so the UI parses Core's JSON itself.

**Leg start, to carry:** stale lock taken at 11:48; step 0 found the killed leg's four unit worktree pairs and no stop marker, no `status.d` fragment, leg worktree clean (reset to `origin/main` `17af2b2b`). Fleet Ready answered this time (24 splittable, 20 waiting on blockers); `finish` moved EMB-448 to Done. Refill gate fired on depth and spread (0 dispatchable while this leg holds the four claims). The owner's `047bb59d` settled the owed `notes/hil/06` pointer. Spool still 8 entries, all at Linear's free-plan issue cap.

---

## 2026-11-25 10:07 — ui/121 the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input

**Decided:** nothing suite-wide. **My split error, caught by the worker:** Core serves the three confirmation routes, but `embarch-core-client` has no method for any of them, and its one-funnel test forbids the UI from sending around it, so the card cannot be built in `ui` alone. The worker stopped, wrote nothing in `embarch-ui`, and left the design for the card in the task's `## Blocked` section (`/api/confirmations` listing each item with its card, `POST /api/confirmations` relaying `{hash, nonce, surface: "ui"}`, every agent string through `textContent`). Its Linear filing hit the free plan's issue cap and spooled, so **I wrote it as `tasks/api/199` (the client's `pending_confirmations`, `confirmation_card` and `confirm`, no MCP tool or CLI twin since a confirmation is never the agent's) and deleted that spool entry so it is not filed twice.** `ui/121` stays `blocked`, its `Unparks when:` now `api/199`, so `api/199`'s fold unparks it. EMB-383 stays in Fleet Working with `ui/121` listed; `api/199` carries no issue.
**Merged:** nothing in code. Doc: the worker's blocked note `4beb3058`, cherry-picked onto `a6586e07` as `c6713baf`, and my edit to it with the new task in this fold.
**Blocked:** `agent/ui/121-the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input` — the core client lacks the confirmation routes' methods; `blocked`, unparks when `api/199` lands. Its doc branch is pushed with the note; the `embarch-ui` branch never got a commit and was never pushed.
**Reviewer:** skipped (nothing landed: the unit stopped before writing code).
**Hardware debts:** none.
**Budget:** PROCEED at this fold (5-hour window reset at 10:00).
**Least sure about:** whether the client methods should return typed answers or `serde_json::Value`; `api/199` leaves it to its worker, and the UI card is the only consumer that will tell.

**Leg end, to carry:** 4 units, 3 landed (`api/198`, `core/161`, `umbrella/117`), 1 blocked (`ui/121`, on my split). **Dispatchable now:** `api/199` (core client confirmation methods; unparks `ui/121`), `core/162` (the setup window between benches; unparked in `core/161`'s fold), `ui/122` (the UI's cancel button, EMB-487's second half). **Linear flapped all leg** (2,500/hour): `ready --brief` never answered; single `show`, `filed` and one `finish` got through. All four of this leg's issues are `filed` (Fleet Working); EMB-366 and EMB-451 are Done. **Free at the last leg's reading, unread here:** EMB-374, EMB-335 (api), EMB-336 (ui), EMB-360 (core, instrument metrology), EMB-377 (core, after EMB-366, now Done), EMB-414 and EMB-413 (chat, still needing the split-first dispatch note: `decisions/references.md` has 162 B left), EMB-317 and the `doc` change issues. **Still owed from the last leg:** `notes/hil/06-report-and-publish.md` line 36 still names `hil-run.md` for a Study's export and check (`fold-commit.py` refuses to stage `notes/`; it resolves through `hil-run.md`'s stub). **Still unclassified:** `embarch-analog-capture-proposal.md` (`check-ownership.py --supervisor`), the owner's call. **The surfaces owe `value`:** after `core/161`, an observation inside a Test run is answerable only by a hand-written request until the UI's modal and the person's terminal send `value`; those are the owner's planned HIL issues, not filed. Spool: 7 entries, all at Linear's issue cap. Bench tasks `api/059` and `dev-bench/038` stay `open`, no board (`fleet-hardware.py --refresh`, 09:38).

---

## 2026-11-25 10:06 — umbrella/117 embarch-agent-starts-stops-and-checks-the-agents-container

**Decided:** nothing suite-wide. New `src/agent_run.rs`: a `ContainerRuntime` trait (`build`, `image_exists`, `volume_create`, `run`, `stop`, `rm`, `exec`, `inspect`) over a `Process` seam, `CliRuntime` as Docker or Podman by binary alone (`docker()`/`podman()`, since no verb differed), and a `FakeProcess` recording every argv. `embarch agent up|down|status|shell [--claude]`: `up` refuses before any side effect on a hand-edited `container.toml`, a forbidden-input finding, a Containerfile hash that differs from the image tag, or an existing container; then builds only when no image carries the tag, creates the volume, writes Core's address to `<definition>/start/core-addr`, and runs the recorded vector with that address filled in, passing `entrypoint-root.sh entrypoint-agent.sh` (closes 66's open line). `down` keeps the volume and exchange folder; `status` reports seven named lines and exits 1 on any failure, reading the fingerprint from the definition folder, never the agent's seed (a test holds it); no runtime on `PATH` refuses every verb with the install pointer. **New umbrella decision 67** in new `decisions/agent-runtime.md`; 62 untouched, nothing written to `open.md` (still in reserve, `umbrella/111`). **The worker's calls, which I keep, all in 67:** `status` re-hashes the recorded vector rather than re-rendering from a plan, because no plan is stored, and `up` runs the recorded vector (the reviewer read both as 62's own rule); `up` stages a build context under `<exchange>/build-context/` from files held to the Containerfile's recorded hashes (closes 64's open line); `render_entrypoint_root` now reads `CORE_HOST` from the start file when rendered with the placeholder, so **a definition folder written before this unit keeps its old `entrypoint-root.sh` and needs that file deleted and `init --container` re-run** (in 67 and the debt). **Assumed or from memory, marked so in 67:** the gateway read from `network inspect` JSON by a case-insensitive `gateway` key; Podman's default network named `podman`; the host-side fingerprint at `<Core data dir>/core-fingerprint`; `image inspect` exiting non-zero for a missing image; `nc` present for the agent user. Plan choices 5, 6 and 9 marked the owner's to strike. **Reviewer's note, below its bar, not filed:** decision 6's title says only the address class is ever persisted, never an address, and 67 writes the address to a start file; read as a per-start handoff overwritten by every `up`, so a refinement of 6, but 67 does not say so, and a clause there is the fix if the owner reads it strictly.
**Merged:** `agent/umbrella/117-embarch-agent-starts-stops-and-checks-the-agents-container` (code `4d99988`, ff from `82f5ef7`; doc `2988c6eb`, the worker's `b27e6987` cherry-picked onto `1fa92ad0`). Re-gated on the merge result against `embarch-api` at `9f3f9e2` and `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (356 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-173-agent-container-run.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the owner's first container, with Docker or Podman installed and `init --container` run in a repo: `embarch agent up`; `embarch agent status`, every line `ok`; `embarch agent shell` and `shell --claude`; `docker inspect embarch-agent-<name>` against the vector in `container.toml`; `embarch agent down`, volume and exchange folder still there; then each from-memory item above. No runtime has ever run any of it.
**Budget:** PROCEED at this fold (5-hour window reset at 10:00).
**Least sure about:** the gateway key and Podman's network name are guesses, and `up` is where a wrong one fails, after the image is built, on a machine where nothing has run a container yet.

---

## 2026-11-25 10:04 — core/161 core-enforces-a-prompts-kind-by-the-tokens-scope

**Decided:** nothing suite-wide. A prompt's kind is `run.json`'s `prompt_kinds` by step name, reaching the backend through a new `RunContext` passed to `run_study_blocking`; a study's own `kind` field is no longer read, by the slot or by `judge_steps`. The agent's token on an `observation` or `clearance` prompt is refused `403`, naming the kind and the person's surfaces, and the prompt stays pending. Every answer records `answered_scope` (events, steps rows, `PromptResolved`); `answered_by` decides nothing. An observation's answer is `confirmed` plus a new optional `value` on `PromptAnswerBody` (read before landing: `#[serde(default)]`, so old callers work), one of the declared `answers` or a number in the declared unit, else `400` naming what is declared; it is written to `measurements.json` as `by: person`, `method {kind: "prompt", prompt_kind: "observation"}`. An unanswered observation is `inconclusive`, `observation_unanswered`; any other kind `error`, `prompt_not_confirmed`, through the crate's `step_verdict`. The prepare keeps each test's `energising_steps` (the crate's `energises`) and each pending prompt carries `switched_on`, also on `GET /test-runs/{run_id}`'s waiting prompt. A study outside a Test run has no kinds and answers as before. **New core decision 138** in `decisions/host-prompt.md`, 105 amended without growing; 93, 95 and 133 untouched. Observation shape marked the owner's to strike (plan choice 27). **Left open in the task's debts:** session prompts (decision 127) keep the scope in the slot but not their own record; an observation number's `resolution` is not enforced; `switched_on` shows the last energising line per target, since it cannot tell off from on. **Not filed, deliberately:** the UI's prompt modal and the person's terminal must send `value` for an observation; both are the owner's planned HIL issues (EMB-367 names them as its consumers), so a fleet issue would duplicate them. **Mine, in this fold:** `core/162` (the setup window) unparked to `open`, its `Where to look` now naming decision 138.
**Merged:** `agent/core/161-core-enforces-a-prompts-kind-by-the-tokens-scope` (code `9233136`, ff from `dc0bccc`: `c6ad3be` and `9233136`; doc `d6b058a1`, the worker's `84f2eee0` cherry-picked onto `e5f7df0d`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (577 + 2 passed, 2 ignored); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-382-prompt-kind-by-scope.md` was assembled in `api/198`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a Test run on a real bench with a person answering an observation from a surface, the agent's token refused `403`, and a real instrument set listed as switched on. The native Windows build of Core. **Deploy debt:** the installed service Core enforces none of this until redeployed.
**Budget:** PROCEED at this fold (5-hour 0%, the window reset at 10:00).
**Least sure about:** no surface sends `value` yet, so until the UI's modal and the person's terminal do, an observation inside a Test run can only be answered by a hand-written request, and an unanswered one reads `inconclusive`.

---

## 2026-11-25 10:03 — api/198 a-tool-and-a-subcommand-cancel-a-running-study

**Decided:** nothing suite-wide. `cancel_study` (MCP) and `cancel-study <study_id>` (CLI, `--json`) share `CoreClient::cancel_study`, new in `embarch-core-client` with `StudyCancelled {study_id, status}` (read before landing: additive, through `dispatch`, so the lease token and bearer go as on every call; `lease_gate.rs` already listed the route). The tool reports Core's immediate `202 {status: "cancelling"}` and points at `study_status` for the end, as decision 128 says the route answers at once; the reviewer confirmed that contradicts nothing. A `404` or `409` comes back as Core's own text. Subcommand count 67 to 68; parity test passes with both halves. No new decision; 90, 98 and 134 untouched. **Split this leg, at `a1eff5c7`:** EMB-367 to `core/161` and `core/162` (the setup window, `blocked` until 161 lands), EMB-448 to `umbrella/117`, EMB-383 to `ui/121`, EMB-487 to this task and `ui/122` (the UI's cancel button, `open`, dispatchable next leg). All four `filed` (Fleet Working). Announced ts `1795624948.519929`. **Leg start, to carry:** 5-hour 70% (window reset within 22 min, ignored), weekly 7%, PROCEED, wave 6. Step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`). **Linear rate-limited again at 09:37** (2,500/hour): `ready --brief`, `finish` and `queue-status.py`'s Fleet Ready read exit 2 between single calls that get through; `filed` reached EMB-366 and EMB-451 and `finish` then moved both to Done. Refill gate fired on depth (0 dispatchable); the only source commit since the last judged sweep was `core/160`'s `open/designed-not-built.md` line, whose items are EMB-367 and EMB-368 or decision 137's own open list, so I filed nothing from the sources. Neither bench role attached (`fleet-hardware.py --refresh`, 09:38): `api/059` and `dev-bench/038` stay `open`.
**Merged:** `agent/api/198-a-tool-and-a-subcommand-cancel-a-running-study` (code `9f3f9e2`, ff from `0b36fcb`; doc `e5f7df0d`, ff from `dffe499b`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (573 passed, `embarch-core-client` a member); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-410-cancel-study.md` assembled into `suite/features.md` in this fold, with `core-382` from the unit landed beside it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; the tool has met only a mock Core.
**Budget:** PROCEED at leg start (5-hour 70%, weekly 7%, wave 6) and at dispatch (72%).
**Least sure about:** the task said the tool reports "the study's end"; it reports the cancel's acceptance, which matches Core's route but leaves a caller who wants the end to poll `study_status` itself.

---

## 2026-11-25 09:35 — umbrella/116 the-agents-container-makes-its-own-clone-on-first-start

**Decided:** nothing suite-wide. `render_entrypoint_agent(&plan)` (and `_at(&plan, root)`, which puts every container path under a temp root for the shell test) in `src/agent.rs` renders the agent half of the entrypoint, run as uid 1000 after decision 63's root half: on a first start (no `/work/.embarch-seeded`) it clones the person's repo with `--no-local` and `safe.directory`, removes `origin` so `person` at `/exchange.git` is the only remote, writes `/work/.west/config`, links the clone's `embarch` to a seeded `/outbox/embarch` (the person's `embarch/` less `embarch.toml` and `build/`, plus the rendered `embarch.toml`), installs the `embarch-hil` skill excluded as `init` does, registers the MCP server inside the container's own Claude config, and touches the marker; every start then copies any file the agent's copy lacks and leaves one present in both alone, and ends `exec "$@"`. `init --container` also writes `entrypoint-agent.sh` and `embarch-hil-SKILL.md` into the definition folder (`SKILL_TEXT` is now `pub(crate)`). **New umbrella decision 66** in new `decisions/agent-clone.md`, since `agent-container.md` would have crossed its cap; 62 untouched; 65's two lines that called the clone's place open now point at 66. **The worker's calls, which I keep, all in 66:** the exclude entry is `embarch`, not `embarch/`, since the clone's `embarch` is a link (from memory, a trailing-slash pattern matches only a folder); the script exports `CLAUDE_CONFIG_DIR=/home/agent/.claude` so the MCP registration lives in the mounted folder and survives a recreated container (from memory); the registration runs from inside the clone, assuming the default scope is the working folder; an interrupted first start is refused, not overwritten. Plan choices 1, 2 and 10 marked the owner's to strike. **Open, in 66:** a file the person deletes or changes never reaches the agent's copy; re-seeding means deleting the clone and the marker by hand; EMB-448's start must pass `/etc/embarch-agent/entrypoint-agent.sh` as the root half's argument. `open.md` untouched (still in reserve, `umbrella/111`). **Reviewer's note, below its bar, not filed:** the seed also copies the person's `embarch/core-fingerprint` into the agent's writable copy; the container's fingerprint check reads a separate read-only copy in the definition folder, so it is not a contradiction, but EMB-448 should keep it that way.
**Merged:** `agent/umbrella/116-the-agents-container-makes-its-own-clone-on-first-start` (code `82f5ef7`, ff from `dfad2a8`; doc `de5c194c`, the worker's `71a8ca94` cherry-picked onto `fd977ee4`). Re-gated on the merge result against `embarch-api` at `0b36fcb` and `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (335 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-172-agent-container-clone.md` was assembled in `core/160`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the owner's first container: `git remote -v` shows one remote, `claude mcp list` from the clone shows `embarch`, `/work/.west/config` and `west list` look right, and an edit under `/outbox/embarch` survives a restart while a new person file arrives. The shell test ran on stub `git` and `claude`, so real git behaviour is unproven.
**Budget:** PROCEED at this fold (5-hour 69%, resetting at about 10:00).
**Least sure about:** four of the script's load-bearing behaviours are from memory (`safe.directory`, `--no-local`, the exclude pattern on a link, `CLAUDE_CONFIG_DIR`), and a wrong one fails only inside a real container, where the marker then says the seed was done.

**Leg end, to carry:** 4 of 4 units landed, none blocked. **Linear flapped all leg** (2,500/hour): at the start and again at 09:19 `ready` and `filed` hit the limit, while `finish` and single `show` calls got through in between. **EMB-366 and EMB-451 are split (`be08040b`) but still read Fleet Ready**: the next `ready` prints them `ALREADY SPLIT`, so run `filed` with `tasks/core/160-...` and `tasks/umbrella/116-...`; with both tasks retired, `finish` then moves each to Done. That frees EMB-367 and EMB-377 (after EMB-366) and EMB-448 (after EMB-451). Free at this leg's last reading: EMB-487, EMB-374, EMB-335 (api), EMB-383, EMB-336 (ui), EMB-360 (core), EMB-414 and EMB-413 (chat, which still need the split-first dispatch note: `decisions/references.md` has 162 B left), EMB-317 and the `doc` change issues. **Not done, owed:** the `study-designer/097` reviewer's third stale pointer, `notes/hil/06-report-and-publish.md` line 36, still names `hil-run.md` for a Study's export and check; `fold-commit.py` refuses to stage `notes/`, and a separate commit for it was refused by the permission classifier, so that line in `097`'s entry ("lands as a separate commit") did not happen. The pointer still resolves through `hil-run.md`'s stub. **A top-level doc is unclassified:** `embarch-analog-capture-proposal.md` is in neither `reserved` nor `fleet_writable` (`check-ownership.py --supervisor`); the owner's call. Spool still 7 entries, all at Linear's issue cap. Bench tasks `api/059` and `dev-bench/038` stay open, no board (`fleet-hardware.py --refresh`, 08:56).

---

## 2026-11-25 09:34 — core/160 core-runs-a-test-selection-test-by-test

**Decided:** nothing suite-wide. New `src/test_executor.rs`: `drive` walks `run.json` against an `Env` trait (a fake in tests, `CoreEnv` on the real bench), bench by bench and test by test; the go spawns it when `AppState::run_executor` is on (on in the service, off in unit tests), and it ends the run through `core/159`'s `end_run`. Policy precedence is cancel, then `stop_on_fail` (`stopped_after_fail`), then `stopped_by_error`, then `requires_not_met`; a test's verdict is its worst run, with counts; the precondition runs once per test, `reset` being the DUT reset under `hw_lock` plus each bench board's idle line. Verdicts through the shared crate's `judge_run` and `judge_test` as they stand; a step's target is `Dut` for the `dut` role and `Bench` otherwise. New `GET /test-runs/{run_id}`, either token, lease-open: state, current bench and test, verdicts so far, a waiting prompt as `agent_text`; the result is kept in `<run_id>.result.json`. `RUN_ADMITTED` now names `/study/{id}/cancel`: during a run that route passes the lease layer with no lease token (the bearer-token layer still applies; I read this part of the diff), and the test-run cancel also cancels the study in flight. **New core decisions 136 and 137** in new `decisions/test-run-executor.md`; 135's `RUN_ADMITTED` sentence rewritten in place with no growth, 134 untouched. `DOCUMENTED_ROUTE_COUNT` 63 to 64. **The worker's calls, which I keep, all in 136 and 137:** the prepare now stores each test's study in the run record, since Core keeps no study file (the bytes are still unchecked against `study.hash`, the hash-convention issue still spooled); the per-test deadline is `2 x duration_bound + 120 s`, chosen and not measured, past which the rest are `cancelled` and the run ends `deadline`; `calibration_expired` is not applied to a person's choice, and with no observation recorded yet an `expect` limit reads `record_gap`, `inconclusive`; `power_cycle` and `detach` preconditions are an `error`, since `run.json` carries no command for them; host studies only, dev-bench studies the owner's to strike (plan choice 18). **Assumed, marked so:** a bench board's signal is named by its `part`, and the idle wait is a 500 ms quiet read, because `run.json` carries no `until` for `idle`. **Left open in 137:** a restart reconcile (`interrupted` is only inferred), a setup prompt and smoke check between benches (EMB-367, EMB-368), and a measurement repeated in a `Repeat` read by its first record.
**Merged:** `agent/core/160-core-runs-a-test-selection-test-by-test` (code `dc0bccc`, ff from `b0b10e7`; doc `fd977ee4`, ff from `67e9d52c`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (570 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature rows `features.d/core-380-test-runs-executor.md` (new) and `core-370` (now pointing at it) assembled into `suite/features.md` in this fold, with `umbrella-172` from the unit landed beside it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the real reset, the idle line and `run_study_blocking` have run over no bench: one run of a two-test fixture suite on a bench with a DUT and a board, through the person's go. The native Windows build of Core. **Deploy debt:** the installed service Core has neither the executor nor the route until redeployed.
**Budget:** PROCEED at dispatch (5-hour 62%); PROCEED at this fold (5-hour 69%, resetting at about 10:00).
**Least sure about:** the idle wait is a fixed 500 ms quiet read and the deadline formula is a guess, so the first real run is where a slow board reads as an error or a long study is cut short as `deadline`.

---

## 2026-11-25 09:17 — study-designer/097 compact-study-designer

**Decided:** nothing suite-wide. A verbatim split, no text deleted: the "A Study's export and check" section (`run_status`, what a Study's run exports, the JUnit and OCP T&V exports, `verify`'s check table 0 to 9, what `verify` cannot recompute) moved from `interfaces/hil-run.md` to a new `interfaces/hil-study-export.md` (4,851 B), with a pointer section left under the old heading and `hil-shapes.md`'s index and verdict-spelling link repointed. `hil-run.md` is 7,602 of 12,288 B, out of reserve, which pays the debt; every `Must not delete:` item survives. No decision added. **The compaction question, in the worker's words:** yes, `spec.md` alone can answer what someone needs to work on this component today, since it indexes the HIL shapes and names each interface file; it was not edited. **Mine, in this fold:** two of the reviewer's three stale pointers to the moved section now name `hil-study-export.md`: core decision `publish.md`'s line on the shape of `report-data.json`, and study-designer `decisions/hil-shapes.md`'s current-truth list. The third, `notes/hil/06-report-and-publish.md`'s verdicts step, is a path `fold-commit.py` refuses to stage, so it lands as a separate commit right after this fold.
**Merged:** `agent/study-designer/097-compact-study-designer` (doc only, `9d167879`, the worker's `b9d305d6` cherry-picked onto `8d004762`; no code SHA). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch; my own line diff of the moved text found only the new file's title and status line differing.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at this fold (5-hour 61%, resetting at about 10:00).
**Least sure about:** the new file has an H1 and an H2 with the same title, left so the moved section stays verbatim; harmless, but the next edit there should drop one.

---

## 2026-11-25 09:15 — api/197 test-files-are-written-through-the-person-writer

**Decided:** nothing suite-wide. `hil_repo` has no file write of its own: `write_under_embarch` calls `ConfinedWriter::write_with`, a new form of the person writer that takes `overwrite` (false refuses an existing file, which keeps "a saved bench is never overwritten") and returns whether it replaced one. Decision 132's kinds are rewritten for `api/196`'s pinned layout: `test` (`<suite>/<id>` to `tests/suites/<suite>/<id>/test.json`), new `test_study` (`<suite>/<id>/<file>`, beside it), `suite`, `plan`, and `saved_bench` as `topologies/<name>.toml`; the `.test.toml` family is gone, since nothing wrote it. 134's second-writer sentence now says the writes go through 132; it shrank about 140 B and is still about 490 B over its per-decision limit (it was 631 B over), and no compaction task was filed for it, since the file is not in reserve. **Mine, one commit on the branch (`0b36fcb`), because the worker's green was not:** my gate on the merge result had three `tests/test_propose_cli.rs` tests red, each "Core kept it, but the repo write failed: `<repo>/embarch` cannot be opened". The person writer opens only an existing `embarch/`, while `api/196`'s writer created it, and those tests assert the folder appears; `hil_repo` now creates a missing `<repo>/embarch` before opening the writer, and a link put there still fails `create_dir` with AlreadyExists and is refused by the writer's `O_NOFOLLOW` open. The worker had reported `cargo test` green. **Also mine, in this fold:** the reviewer's wording nit in 132, "the two compound forms are the only names with a `/`", now names `test` and `test_study` too. **Leg start, to carry:** 5-hour 56%, weekly 6%, PROCEED, wave 6. Step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`); neither bench role attached (`fleet-hardware.py --refresh`, 08:56). **Linear was rate-limited again at 08:56** (2,500/hour, minutes after the last leg saw it clear): `ready --brief`, `finish` and `queue-status.py`'s Fleet Ready read all exit 2, so this leg's first wave was the two tasks on hand; `ready` answered again by about 09:15. Refill gate fired on depth and spread; the only source commit since the last judged sweep was `api/196`'s `open/bench-verification.md` line, so I filed nothing from the sources.
**Merged:** `agent/api/197-test-files-are-written-through-the-person-writer` (code `0b36fcb`, ff from `eb2f64d`: the worker's `f5ad7f2` and my `0b36fcb`; doc `8d004762`, ff from `047c959e`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (571 passed, `embarch-core-client` a default member); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row (no maturity changed).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; the Windows branch of `person_writer` was edited and is unbuilt (already `tasks/api/193`'s debt).
**Budget:** PROCEED at leg start (5-hour 56%, weekly 6%, wave 6) and at dispatch; PROCEED at this fold (5-hour 61%).
**Least sure about:** the worker reported a green `cargo test` that three tests contradicted, deterministically, so either it ran a narrower command than it said or read a stale result; the gate caught it, but a worker's green on this repo deserves less weight until we know which.

---

## 2026-11-25 08:52 — ui/120 a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted

**Decided:** nothing suite-wide. New `src/bench/references.rs` scans `embarch/studies/*.json` (not recursive) and every `.json` under `embarch/tests/suites/` (the layout `api/196` pinned): a prompt whose `bench_config` is the name counts, and so does a test whose `bench.config` is the name and whose `bench.name` is this bench's name or slug. `PUT /api/bench/benches/{slug}` refuses `409` with `x-embarch-refusal: config-named` when the saved file holds a config the new body lacks (a rename or a delete) and a study or test names it, one line per study or test with its file and the naming prompts. New `GET /api/bench/benches/{slug}/config-references?config=` answers `{named_by, unreadable}`; the Rename and Delete dialogs in `assets/bench.js` call it before any edit, Rename stays open with the list, Delete lists them and makes no edit. **New ui decision 108** in `decisions/bench-configs.md`, 96 amended in place by a dated pointer. **The worker's calls, which I keep, all in 108:** a file that does not parse, or a manifest's missing test file, is listed as unreadable and blocks every rename or delete until fixed (as the Study Designer's own reference scan does); a prompt carries no bench, so a prompt naming `A` holds every bench's `A`, while a test holds only its own bench's. `Cargo.lock` updated for `api/195`'s `embarch-core-client` dependencies, which the last leg had flagged as stale. **Reviewer's note, below its bar:** study-designer decision 88's "a name the bench lacks is never refused" reads as how a study resolves a name, not a bar on the bench refusing an edit, so 108 refines it.
**Merged:** `agent/ui/120-a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted` (code `508b1e6`, ff from `90668da`; doc `d318facc`, the worker's `6f029875` cherry-picked onto `efa8c712`). Re-gated on the merge result against `embarch-api` at `eb2f64d` and `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (351 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/ui-079-bench-configs-and-prompt-change.md` (amended) assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; the dialogs and the tweak to `tests/browser/drive_bench_configs.py` (Delete now waits on an async lookup) were not run in headless Firefox: one run of that script, plus a case with a fixture test naming a config.
**Budget:** PROCEED at this fold (5-hour 56%, weekly 6%).
**Least sure about:** one malformed JSON file anywhere under `embarch/studies/` or a suite folder now blocks every config rename and delete in the bench, which is safe but may read as the editor being broken until the person finds the named file.

**Leg end, to carry:** 4 of 4 units landed, none blocked. **Linear's rate limit cleared by about 08:53**: `filed` then reached EMB-385 and EMB-376, so all four of this leg's issues are in Fleet Working and need no re-filing. **Dispatchable now: `api/197`** (route `hil_repo`'s writes through decision 132's `person_writer`, the reviewer's finding on `api/196`) **and `study-designer/097`** (compact `hil-run.md`, unparked in `api/196`'s fold). EMB-365 done frees EMB-366 (core, the executor) once `finish` moves it; EMB-447 done frees EMB-451 and EMB-448 (umbrella); EMB-360 (core), EMB-487, EMB-374, EMB-335 (api), EMB-336 (ui) and EMB-324 (core, verify-only) were free at the last leg's reading, unverified here. **Chat's next linker unit (EMB-413 or EMB-414) still needs the split-first dispatch note**: `decisions/references.md` has 162 B left. **Spool: 7 entries**, all waiting on Linear's free-plan issue cap, not the rate limit. **One transient fault:** the first `git push` to `embarch-api` was refused with SSH `publickey` and went through on retry a minute later; if it recurs it is the agent's SSH access, not the repo. Bench tasks `api/059` and `dev-bench/038` stay open, no board attached (`fleet-hardware.py --refresh`, 08:26).

---

## 2026-11-25 08:51 — umbrella/115 init-sets-up-the-agents-container-and-registers-the-repo

**Decided:** nothing suite-wide. `embarch init --container [--runtime docker|podman]` renders `umbrella/112` to `114`'s outputs (Containerfile, `container.toml`, firewall script, a clone config template) into `~/.config/embarch/agents/<name>/` (Windows `%APPDATA%`), and creates `~/.local/share/embarch/agents/<name>/` (Windows `%LOCALAPPDATA%`) with a bare `exchange.git`, `outbox/` and `claude-config/`, then prints the person's fetch line. **Every `init` registers the repo** in umbrella's state (`registered_repos`, `RegisteredRepo`/`RegisteredContainer`, defaulted so an old state file loads, schema still 1). `--uninstall` removes the entry and, after a typed `yes` and a warning about unfetched work, the folders; `--dry-run` names every path and writes nothing, registry included; `--container` conflicts with `--uninstall`, `--runtime` requires `--container`. Logic in new `src/agent_init.rs` behind a `Host` struct, so tests never touch the real home or state; `init.rs`'s old `init` is `init_repo`. **New umbrella decision 65** in `decisions/projects.md`, extending 62 to 64 without editing 62; plan choices 1, 2, 4, 11 and 17 marked the owner's to strike; the elevated fingerprint writer adds its own printed line when it is built. **The worker's calls, which I keep, all in 65:** a generated file that exists and differs is kept, not overwritten (62's `container.toml` hash exists to notice a hand edit; deleting it regenerates); decision 64's `NotWest`/mounts disagreement is resolved in the mounts' direction, `west_workspace` filled only for `ZephyrWest`, `run_args` unchanged; a remote Core or no saved topology refuses the container but still registers the repo; the firewall script keeps the Core-address placeholder, which EMB-448's start substitutes. **A fix beyond the brief, kept:** `src/setup.rs` built a fresh `State` on every save and would have wiped the registry on a `setup` re-run; it now carries `registered_repos` through. **Assumed, marked so in 65:** toolchain `arm-zephyr-eabi` (no SoC source in `init`), the clone at `/work/<repo folder>` (EMB-451 owns it), the agent token at `<Core data dir>/agents/<name>/agent-token` with no development token mounted. `open.md` untouched (still in reserve, `umbrella/111`).
**Merged:** `agent/umbrella/115-init-sets-up-the-agents-container-and-registers-the-repo` (code `dfad2a8`, ff from `7b1c1f0`; doc `f3c21c52`, the worker's `53a497e5` cherry-picked onto `9cdb8dd2`). Re-gated on the merge result against `embarch-api` at `eb2f64d` (`api/196`'s `embarch-core-client`, landed first) and `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (330 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-115-init-container.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; native Windows is unrun (the `%APPDATA%`/`%LOCALAPPDATA%` folders are covered only by the pure resolver's test), and `west list` has never run against a real west workspace.
**Budget:** PROCEED at this fold (5-hour 55%, weekly 6%).
**Least sure about:** the agent token path under Core's data dir is assumed and nothing writes a token there yet, so the first `embarch agent` start (EMB-448) is where the mount either finds a token or mounts an empty path.

---

## 2026-11-25 08:49 — core/159 a-test-runs-go-takes-the-lease-and-starts-the-run

**Decided:** nothing suite-wide. `POST /test-runs/{run_id}/go`, the person's token only (the agent's gets `403` from `person_middleware`, new `token_store::GO_ROUTES`): `422` whose message starts `mismatched`, `expired` or `replayed`; `409` for a run already started, an input still unconfirmed (named), or a session no longer holding the lease. A new `AppState::run_lock`, which `LeaseSlot::watching` also takes and `lease_middleware` checks before the lease: while it is held every token is refused `409` naming the run, the session's own included, and renew and release are refused; `GET /lease` shows `holder: test run <id>` and a new `run_id`; the lease neither expires nor idles during a run and returns at the end under its old token, TTL and idle clock restarted. `POST /test-runs/{run_id}/cancel`, either token, not lease-gated, logs `test_run_ended` with the token's scope; the go logs `test_run_started`. `DOCUMENTED_ROUTE_COUNT` 61 to 63. **New core decision 135** in new `decisions/test-run-go.md`; 93 and 123 amended by dated pointers, 134's two lines that said "EMB-365 chooses" corrected. **The worker's calls, which I keep, all in 135:** the go does not re-expand, so the prepared hash stays the run's identity and later confirmations are read live at the go (re-expanding needs study files Core does not keep); a go needs a live lease held by the same holder that prepared the run, so a run prepared with no lease is refused at the go; the nonce is spent only after every other check passes, so an unconfirmed input does not burn a card (a wrong try still spends it, as in 133); a run starts once, even after a cancel (`<id>.started.json`); `replayed` also covers an unknown nonce or one from before a restart. **Executor seam for EMB-366:** `test_runs::end_run(state, run_id, status, reason, by)` and an empty `RUN_ADMITTED` list in `api.rs`. Open items kept in 135: a Core restart mid-run leaves a started run with no end, and the executor owns a deadline. `interfaces/hardware.md` does not mention `GET /lease`'s `run_id` (the edit put it into reserve; the worker reverted it), so only `interfaces/test-runs.md` documents that field. **Reviewer's notes, below its bar, not filed:** with `RUN_ADMITTED` empty, decision 95's one route a running study still admits (`/study/{id}/cancel`) gets `409` under a run lock, which EMB-366 must add when it starts studies inside a run; and a `run_id` or `run_hash` mismatch in the body is refused before the nonce is spent, so 135's "a wrong try still spends it" holds for a wrong nonce only.
**Merged:** `agent/core/159-a-test-runs-go-takes-the-lease-and-starts-the-run` (code `b0b10e7`, ff from `4ef12e6`; doc `b141b632`, the worker's `5fbc7e56` cherry-picked onto `01743947`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (552 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-370-test-runs-go.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core. **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-366 and the person's terminal.
**Budget:** PROCEED at this fold (5-hour 55%, weekly 6%).
**Least sure about:** the run lock refuses the session's own token on every gated route, so until EMB-366 fills `RUN_ADMITTED` a started run can only be ended by a cancel, and a Core restart mid-run leaves it started with no end and the lease held by a run that is not running.

---

## 2026-11-25 08:46 — api/196 test-plans-in-the-repo-and-proposals-sent-to-core

**Decided:** nothing suite-wide. **I pinned the tests layout across two scopes at the split**, so `api/196` and `ui/120` could run in one wave: `embarch/tests/suites/<suite>/suite.json`, each test in `<test id>/` with its study beside it, `embarch/tests/plans/<plan>.json`, `embarch/tests/results.jsonl` reserved. `notes/hil/02-study.md` writes a test's folder without the `suites/` level; the issue's `suites/` won, and api decision 134 says it reads 02 that way. This unit: `test_propose` and `test_plan` (MCP and CLI twins, subcommands 65 to 67) in new `src/hil_repo.rs`; the crate's `hil-test` feature turned on for `embarch-api`; `embarch-core-client` gains `post_definition`, `definition` and `suites` (read before landing: additive, no feature change). A proposal is checked by the crate first (a refusal never reaches Core), then `POST /definitions`, and only after Core accepts is it written under `embarch/tests/suites/`. Writing a plan that names a suite selects it, copying each bench to `embarch/topologies/<slug>.toml`, a taken name with other content left alone and reported with its diff. **New api decision 134** in new `decisions/test-plans.md`, new `interfaces/tools-tests.md`. **The worker's calls, which I keep:** the tool fills `study.hash` from the bytes it writes and refuses a given one that differs; a new custom suite gets version `0.1.0` and `validated_with: "unvalidated"`; the `test_plan` listing is not Core's expansion (no hook mapping, no `requires` chains). **The one I do not keep, and filed:** it wrote its own writer into `embarch/` instead of decision 132's `person_writer`, see the reviewer line. Decision 98 got no pointer (15 B left); `tools-ledger.md` points to the new interface instead. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`); the local `agent/atlas/097` branches are the parked prior-art unit. **Linear rate-limited at leg start** (2,500/hour): `ready --brief` and `queue-status.py`'s Fleet Ready read exit 2; `finish` ran (exit 1: EMB-334, EMB-312, EMB-136 open); single `show` calls got through. Split at `97b00fdd` from the last leg's handoff list: EMB-365 to `core/159`, EMB-447 to `umbrella/115`, EMB-376 to this task, EMB-385 to `ui/120`. `filed` reached EMB-365 and EMB-447 (Fleet Working); **EMB-376 and EMB-385 hit the limit and are still in Fleet Ready**, so the next `ready` will print them `ALREADY SPLIT`: run `filed` with the paths, never split again. Announced ts `1795620494.099999`. Refill gate fired on depth and spread (0 dispatchable before the split); the only source commits since the last judged sweep are `study-designer/095`'s two `open.md` items (the first real bench settles both), `core/155`'s unverified line (its 422 text is already a spooled filing), `api/193`'s Windows-build line and `api/195`'s `embarch-token.md` row, so I filed nothing from them and did not re-read the rest. **`study-designer/097` unparked here**: its `Unparks when:` named only EMB-376, and the three units its flux answer named (EMB-364, EMB-356, EMB-376) have all landed, so it is `open` with `In flux: no` and dispatchable.
**Merged:** `agent/api/196-test-plans-in-the-repo-and-proposals-sent-to-core` (code `eb2f64d`, ff from `add96ab`; doc `44c88c7d`, ff from `3c9d68cb`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (569 passed, `embarch-core-client` a workspace member); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-400-test-propose.md` assembled into `suite/features.md` in this fold. The first code push failed once on an SSH `publickey` refusal and went through on retry a minute later.
**Blocked:** nothing.
**Reviewer:** 1 finding — `tasks/api/197` (unfiled: Linear refused at its issue cap; I wrote the task and dropped the spool entry so it is not filed twice)
**Hardware debts:** none from a board; everything ran against `MockCore`, a real Core's card should show the hash `TestDef::hash()` gives, and the Windows `std::fs` writes in `hil_repo` are unbuilt (all in `open/bench-verification.md`).
**Budget:** PROCEED at leg start (5-hour 42%, weekly 4%, wave 6, capped at the leg's 4 units) and at dispatch (45%); PROCEED at this fold (5-hour 54%, weekly 5%).
**Least sure about:** until `api/197` lands, `hil_repo` writes into the person's `embarch/` with only a `symlink_metadata` check, which a link swapped in after the check defeats; nothing calls it unattended yet, but it is the weaker of two writers into the same folder.

---

## 2026-11-25 08:19 — chat/041 the-linker-offers-kconfig-symbols-and-devicetree-nodes

**Decided:** nothing suite-wide. The 💡 linker offers two more kinds from `chat/040`'s one `embarch-atlas refs --json` read, with no second run: `refsAtlas.ts` gains `parseRefs`, `kconfigSource` and `dtSource`, `references.ts` the `symbol` and `node` rows and `lineOf`, `refsBase.ts` an optional `RefEntry.note`, and `parseCards` appends an entry's note to the card's why. Symbols are written `CONFIG_<NAME> ("<prompt>")`, nodes `&<label> (<path>, <compatible>)` or the path alone; both gated on a cue word or an exact name. **New chat decision 115** in `decisions/references.md`, marking plan choices 4, 11 and 12 as the owner's to strike. **The worker's calls, which I keep, all in 115:** a stale atlas's notice is a fixed note on each symbol and node entry, appended as "…; the atlas is at an older commit", not left to the model's wording, and sections do not carry it since they come from the translated documents; "atlas only" keys on the `atlas` field being non-null; the bare `<NAME>` form is matched case-sensitively, capitals with an underscore only; cue words are dropped from an entry's own match words, as `chat/040` does for sections; entries are cached per atlas read. `refs --json` already carried each kind's prompt, labels, compatibles and aliases, so nothing waited on `embarch-atlas`. **Debt filed by the worker:** `decisions/references.md` went to 12126 of 12288 B, so `tasks/chat/042-compact-chat.md` is `blocked`, `In flux: yes`, due 2026-12-09, unparking when EMB-414 and EMB-415 land.
**Merged:** `agent/chat/041-the-linker-offers-kconfig-symbols-and-devicetree-nodes` (code `fd154a5`, ff from `4093c1a`; doc `4aa3d7e0`, the worker's `3171871b` cherry-picked onto `d52660fd`). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (419 tests, 416 pass, 3 skip), `test:webview` green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. **My first `npm test` run was red, and not on this unit:** `test/wire.test.mjs`'s "a model picked while a /compact waits behind a turn" failed once while Core's tests ran beside it, then passed three of three alone and in a full rerun; the test throws before `dispose()`, so the scripted CLI held the run to its 600 s idle (606 s against 41 s). The worker's own first run hit the same ten minutes. Filed for chat, spooled (Linear at its cap): "A compaction test races under load and then holds npm test for ten minutes". Feature row `features.d/chat-041-linker-atlas-symbols-nodes.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; never seen against a real atlas or window (said in 115 and the feature row).
**Budget:** PROCEED at this fold (5-hour 42%, weekly 4%).
**Least sure about:** matching is the shared word matcher's, so "turn on the shell history option" also offers a second, unrelated history symbol after the right one; on a real atlas with thousands of symbols the cue-word gate is the only thing keeping a draft's card short, and nobody has seen how long it gets.

**Leg end, to carry:** 4 of 4 units landed, none blocked. **`decisions/references.md` has 162 B left**, so the next chat unit (EMB-413 or EMB-414, both new linker kinds) cannot add its decision there: its dispatch note must tell the worker to split the file verbatim first (`DOC-COMPACTION.md`'s split-first rule; a verbatim split is allowed under `In flux: yes`) or to put the decision in a new topic file, and to close `chat/042` if that pays it. **Spool, five entries carried plus two of this leg's**, all waiting on Linear's free-plan issue cap: the worker's study-designer issue (a hash convention for a premade study file, so Core can check a run's study bytes; core decision 134 names the gap) and the chat test flake above. I dropped the core/158 reviewer's spooled finding after fixing it. EMB-364, EMB-356 and EMB-446 are done once `finish` runs, which frees EMB-365 (core, the go and the lease), EMB-447 (umbrella) and, with EMB-365, EMB-366; EMB-360 (core), EMB-376 (api, which also unparks `study-designer/097`) and EMB-385 (ui) stay free. Bench tasks `api/059` and `dev-bench/038` stay open, no board.

---

## 2026-11-25 08:08 — umbrella/114 the-agents-container-image-and-west-workspace-mounts

**Decided:** nothing suite-wide. `src/agent.rs` gains, pure: `render_containerfile(&plan)` (the plan gains `toolchain: Toolchain`, `ZephyrWest` or `NotWest`, from `Toolchain::from_workspace`), `image_tag` (`embarch-agent:<sha256 of the rendered text>`), `west_mounts(west_list, manifest_path)` and `west_projects`, `parse_sdk_version`, and `FIREWALL_BINARIES`, the binary-to-package pairs a test holds against decision 63's rendered script in both directions. **New umbrella decision 64** in `decisions/agent-container.md`, extending 62 without editing it (62 is over its per-decision limit); plan choice 10 marked the owner's to strike; the open items live in 64. **The worker's calls, which I keep, all in 64:** `debian:bookworm-slim`, not Ubuntu, whose 24.04 image ships a uid-1000 user that collides with `agent`; 63's script also calls `awk` and `sort`, so `gawk` and `coreutils` join the list; the workspace's requirements files are `COPY`d from a `requirements/` build-context folder the caller (EMB-448) supplies, each named in a comment with its SHA-256 so a changed file changes the tag; the SDK toolchains are named by the caller, since `init` has no source for the person's SoC yet (assumed); a missing or malformed `zephyr/SDK_VERSION` gives `NotWest`, never a guessed version, and the parser accepts only dotted digits and one suffix because the value reaches a URL and a shell line; a `west list` path that is absolute or contains `..` is skipped, not refused; west and the requirements go in a venv. **From memory, marked so in 64 and the Containerfile:** `west list -f "{path} {abspath}"`'s fields, the SDK release URL and archive name and `setup.sh` flags, the apt package list, the Claude Code installer URL. **Reviewer's note, below its bar, not filed:** the `NotWest` comment says no west workspace is mounted, while `run_args` renders `west_workspace` mounts independently of `toolchain`; EMB-447, which wires `init`, should make the two agree.
**Merged:** `agent/umbrella/114-the-agents-container-image-and-west-workspace-mounts` (code `7b1c1f0`, ff from `d9a4b8a`; doc `318ec292`, the worker's `6b8fc8fa` cherry-picked onto `01032278`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b`: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (319 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-171-agent-container-image.md` was assembled in `study-designer/098`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; no image has been built, so every from-memory line and the nft backend of Debian's `iptables` under 63's rules are unverified until EMB-448's first build and start.
**Budget:** PROCEED at this fold (5-hour 39%, weekly 4%).
**Least sure about:** Debian's `iptables` is the nft backend by default and 63's rules were written without a run under either, so the first container start is where the firewall could fail closed or, worse, open.

---

## 2026-11-25 08:07 — core/158 core-prepares-a-test-run-and-serves-its-go-card

**Decided:** nothing suite-wide. `POST /test-runs` (either token) takes `{run, plan, suite?, studies}`: Core resolves the manifest's tests from its kept definitions or its premade suites, re-expands through `hil_expand::expand`, compares `RunJson::hash()`, and answers `422` naming the first differing key (`tests[<id>].limits[<measurement>].upper`), `409` on a reused `run_id` (the record is hard-linked into `test-runs/<run_id>.json`, so two prepares of one id cannot both win). The record keeps Core's own re-expansion, its hash, the card's static data and the lease holder's name at that moment. `GET /test-runs/{run_id}/card` serves tests per bench, origin (`premade`, `derived` with `derived_diff`, `custom`), prompts with kinds, energising steps with lines, every limit with `U`, `k`, `w`, the duration bound, and the unconfirmed inputs read from the run log per request; the person's token gets a go nonce from decision 133's store, keyed `go:<run_id>:<run_hash>`, the agent's gets none. `DOCUMENTED_ROUTE_COUNT` 59 to 61; both routes lease-open. **New core decision 134** in a new `decisions/test-runs.md`, with `interfaces/test-runs.md`; plan choices 9 and 10 marked the owner's to strike. **The worker's calls, which I keep, all in 134:** `confirmed` is blanked on both sides before the hash comparison, since the caller cannot read Core's confirmations, so the registered hash is stale after a later confirmation and the go (EMB-365) must re-prepare or re-expand; `benches_present` comes from the caller's `run.json` (Core has no saved-bench list); study files are **not** checked against `study.hash`, because the crate fixes no hash convention for a premade study file, and the card marks each test `bytes_checked_against_hash: false` (the worker spooled a study-designer issue for it, Linear being at its cap); the card is open to both tokens with only the nonce withheld. `open.md` untouched (it sits 7 B above reserve). **Mine, two commits on the branch:** three existing comments cited "decision 134" for the service and development stores, which is 129 (`core/156`'s worker had flagged them); with 134 now real they would have pointed at this decision, so they say 129 (`128fe14`). And the reviewer's finding, fixed forward rather than reverted (`4ef12e6`): the card emitted a capability's `value`, a hook's `maps_to` (a DUT shell command) and a derived test's diff values as plain JSON, against 134's rule that every string a definition, study or `run.json` wrote is `agent_text`; a recursive `agent_value` now marks every string leaf, object keys plain, with a test, and `interfaces/test-runs.md` says so in this fold. I dropped the reviewer's spooled Linear filing for it, since it is fixed.
**Merged:** `agent/core/158-core-prepares-a-test-run-and-serves-its-go-card` (code `4ef12e6`, ff from `2f25415`: the worker's `ec0e629`, my `128fe14` and `4ef12e6`; doc `01032278`, the worker's `f41e3f2d` cherry-picked onto `6bf2d218`). Re-gated on the merge result against `embarch-study-designer` at `0caf76b` (`study-designer/098`, landed first): `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (546 passed after the fix); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-360-test-runs-prepare.md` was assembled in `study-designer/098`'s fold. `study-designer/097`'s `Unparks when:` now names only EMB-376.
**Blocked:** nothing.
**Reviewer:** 1 finding — fixed forward in core `4ef12e6` (unfiled: Linear refused at its issue cap, spool entry dropped once fixed).
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-376.
**Budget:** PROCEED at this fold (5-hour 39%, weekly 4%).
**Least sure about:** the card's prompts and energising steps rest on study files Core has not hashed against the run's `study.hash`, so until the hash convention lands a person approves a go on bytes the agent sent; the card says so, but a surface has to show that flag for it to mean anything.

---

## 2026-11-25 08:04 — study-designer/098 one-function-turns-a-tests-records-into-its-verdict

**Decided:** nothing suite-wide; I read the shared-crate diff before landing it (one `pub mod hil_judge` line in `lib.rs` behind `hil-test`, the rest new files; no public type changed). **Leg start, to carry:** 5-hour 28%, weekly 3%, PROCEED, wave 6 capped at the leg's 4 units. Step 0 recovered nothing (no claim, no unit worktree, no stop marker); neither bench role attached (`fleet-hardware.py --refresh`, 07:35), so `api/059` and `dev-bench/038` stay `open`. Split three Fleet Ready issues at `49acf3ad`, all `filed` to Fleet Working: EMB-356 to this task, EMB-364 to `core/158`, EMB-446 to `umbrella/114`; the fourth unit was `chat/041`, split by the previous leg. Refill gate not owed (4 across 4 scopes). Announced (ts `1795617464.424559`). This unit: new `src/hil_judge.rs` behind `hil-test`: `judge_run(test, steps, measurements, rules) -> Result<Judged, JudgeError>`, `judge_test(runs, rules) -> TestVerdict {judged, counts}`, `skip(reason)`, `unvalidated(judged)`, `behaviours_used(rules)`, with input types `StepRecord`, `MeasurementRecord`, `Origin`, `FirmwareState`, `DeclaredBy`. **New study-designer decision 112** in `decisions/hil-verdicts.md`, marking plan choice 27 as the owner's to strike. **The worker's calls, which I keep, all in 112:** the module sits behind `hil-test`, not `verdicts`, which stays `alloc`-only per 96; `judge_test` returns a struct because `Judged` has no counts; `skip` drops the unused `test` parameter and refuses a reason that is not a skip; `unvalidated` is applied by the caller, which alone knows whether a premade test has its evidence; a limit with no measurement is `inconclusive`, `record_gap`; an unknown decision-rule kind is an error, not simple acceptance; qualifiers come from every measurement handed in. `spec.md` not edited (an index line pushed it into reserve; the worker reverted it). **Reviewer's note, below its bar, not filed:** the `expect` (choice) path checks incomplete evidence but not `calibration_expired`, which 97's order puts before the limit; a person's choice rarely rests on a calibrated instrument, so whoever wires the executor (EMB-366) should decide whether it applies.
**Merged:** `agent/study-designer/098-one-function-turns-a-tests-records-into-its-verdict` (code `0caf76b`, ff from `2366f86`; doc `6bf2d218`, the worker's `efe831c9` cherry-picked onto `1c276399`). Re-gated on the merge result: `build`, `clippy --all-targets -D warnings` and `test` under defaults, `std,reducers,hil-image,hil-test` (Core's), `study-ui,gatt-extract,eap-parse` (the UI's), `alloc,reducers` (api's), `alloc` (`embarch-core-client`'s), `hil-test` and `--all-features` (504 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/study-designer-245-hil-judge.md` assembled into `suite/features.md` in this fold, with `core-360` and `umbrella-171` from the units landed beside it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 28%, weekly 3%, wave 6) and at dispatch (5-hour 30%); PROCEED at this fold (5-hour 38%, weekly 4%).
**Least sure about:** nothing calls these functions yet, so whether `MeasurementRecord` carries everything Core's executor will have in hand (EMB-366) is untested; the first caller may want a field the record does not have.

---

## 2026-11-25 07:30 — suite/063 an-instruments-declaration-carries-its-metrology

**Decided:** **a suite pass, run by me as this leg's last unit, announced by the previous leg** (ts `1795612302.163159`, 06:11; the window closed 06:41 with no reply, re-polled at this leg's start and again just before the pass began, still none). `embarch-topology`: `Instrument.metrology: Vec<Metrology>` (`{quantity, unit, resolution, U, k, basis, range: {min, max}}`) and `Instrument.calibration: Option<Calibration>` (`{serial, certificate_ref, due, certificate_sha256?}`), both default when absent and omitted when empty; `check` refuses a negative or non-finite `resolution` or `U`, a `k` not above zero, a `range` whose `min` is not below `max`, an empty `quantity`, `unit`, `serial` or `certificate_ref`, a `due` that is not a real `yyyy-mm-dd` date, and a `certificate_sha256` that is not 64 lower-case hex digits, each naming the field. New exports `Metrology`, `MetrologyBasis`, `MeasuringRange`, `Calibration`. **New topology decision 51** in `decisions/instruments.md`, a dated pointer on 49, index and `spec.md` rows; Core's `interfaces/instruments.md` `PUT` line names the new fields and refusals. **My calls beyond the task's text, all in 51:** `U` keeps its capital on the wire as `ObservedNumber`'s does; `basis` is a closed enum, `datasheet`, `certificate` or `declared`; `k` is required here where a person's observed number defaults it to 2; two entries for one quantity are not refused, which applies being Core's when it stamps them (EMB-360); **`Instrument` lost its `Eq` derive** (it now holds `f64`s), and no consumer needed it. Plan choice 14 (metrology in Core's own store instead) is marked the owner's to strike. Consumers changed only the struct literals: Core's test helper, `embarch-api`'s `declare_instrument` builder and its `core_client_http` test, `embarch-ui`'s Make live, plus topology's own `paths.rs` test. **Known gap, recorded in 51:** a re-declaration through `declare_instrument` or Make live writes no metrology and replaces a stored one, since `PUT` replaces by name; carrying and keeping them is EMB-375's. **Reviewer's note, below its bar, not filed:** a `U` or `resolution` of zero is accepted, where `ObservedNumber` requires them positive and 03 refuses an undeclared one at definition; zero is not undeclared, and Core's stamping (EMB-360) is the later gate, so whoever lands EMB-360 should decide whether zero is refused there.
**Merged:** `agent/suite/063-an-instruments-declaration-carries-its-metrology`, landed in order, each ff from its `origin/main`: topology `5b8d493` (from `7b0b87d`), core `2f25415` (from `2e8a18b`), api `add96ab` (from `5e18cc3`), ui `90668da` (from `7d52207`); doc `9aad9194`, my own commit in the leg worktree. Gated before any push with every consumer's `embarch-topology` link pointed at the branch: topology clippy under `hardware` (Core's), `software,wire` (`embarch-core-client`'s), defaults (`embarch-umbrella`'s) and `--all-features`, tests under `hardware` (123), `software,wire` (29) and `--all-features` (152); Core 540, api 559 plus `embarch-core-client` 65, ui 346 tests passed, clippy clean in each; `check-docs.py` 12/12; client names clean on the four code worktrees. `embarch-umbrella` does not use `Instrument` and was not rebuilt. The links are restored to the main checkouts. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from the code; the native Windows build of Core. **Deploy debt:** the installed service Core accepts the new fields only once redeployed; nothing sends them yet.
**Budget:** PROCEED at this fold (5-hour 27%, weekly 3%).
**Least sure about:** `k` required against `ObservedNumber`'s default of 2 is a split convention inside the suite; if EMB-375's tool wants to accept a datasheet that states no `k`, 51 is the decision to amend rather than the tool to work around.

**Leg end, to carry:** 4 of 4 units landed, none blocked. **`tasks/chat/041` (EMB-412, the linker's Kconfig and devicetree kinds) is split, `open` and dispatchable** — split this leg so the refill gate read 4 across 4 scopes. EMB-358 is done, so EMB-360 (Core stamps an instrument's metrology on its measurements) unblocks once `finish` moves it. Fleet Ready still holds 25 unsplit issues; free ones include EMB-446 (umbrella; its Containerfile must install what decision 63's root script calls: `iptables`, `ip6tables`, `ipset`, `nc`, `getent`, `timeout`, `setpriv`), EMB-487 and EMB-374 and EMB-335 (api), EMB-385 and EMB-336 (ui), EMB-324 (core, verify-only); `core/157` unblocked EMB-364's half and `study-designer/096` both halves of EMB-364 and EMB-356. **Two size notes:** `core/157`'s new decision 133 (`decisions/definitions.md`) is 233 B over its per-decision limit, which the gate does not fail and the worker did not report; `study-designer/097` (blocked, due 2026-12-09) is the debt `hil-run.md` now carries. `embarch-ui`'s committed `Cargo.lock` is behind `embarch-api`'s `embarch-core-client` (its `api/195` dependencies), so any ui build rewrites it; not committed here. Bench tasks `api/059` and `dev-bench/038` stay open, no board.

---

## 2026-11-25 07:11 — umbrella/113 the-agent-containers-firewall-and-cores-address-from-inside

**Decided:** nothing suite-wide. `src/agent.rs` gains, pure: `render_entrypoint_root(&plan, core_host)`, a POSIX root script that drops IPv4 and IPv6 egress, allows loopback, established flows, DNS to the IPv4 resolvers in `/etc/resolv.conf`, TCP to Core's address on Core's port and TCP 443 to an `ipset` of the resolved allowlist hosts, then checks Core is reachable and `192.0.2.1:443` is not (exit 1 otherwise) before `setpriv` to uid 1000 with inheritable, ambient and bounding sets cleared and `no-new-privs`; `core_host_findings(script, host, port)` flags any rule naming Core's host with another port or none; `core_addr_from_container(class, runtime, wsl_gateway, bridge_gateway)` (`linux` the bridge gateway, erroring with the bind note when absent; `wsl-host` the WSL gateway; `docker-desktop` and `macos` `host.docker.internal`, unverified; mirrored networking left out, not refused). `SETPCAP` joins the allowed capabilities, so `run_args` adds five; `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` in the agent's env; `AgentContainer.network_allow`; `container.toml` gains `[network] allow`, round-tripped. **New umbrella decision 63** in `decisions/agent-container.md`, superseding 62's capability clause (62 untouched, it is over its per-decision limit) and saying the agent half holds none; plan choices 7, 8, 9 marked the owner's to strike. **The worker's calls, which I keep, all in 63:** Core's host is a second argument because umbrella decision 6 never persists Core's address, and `[network] allow` holds Core as `<core-addr>:<port>`; a model-API host that resolves to Core's address is skipped; the off-list self-check uses a reserved test address and another port on Core's host is asserted as text only. Assumed, not measured: the image carries `iptables`, `ip6tables`, `ipset`, `nc`, `getent`, `timeout` and `setpriv` (EMB-446's Containerfile has to install them); login hosts past `api.anthropic.com` are a fixture placeholder. `open.md` untouched, so `umbrella/111`'s park is unchanged; the open items live in 63. **Reviewer's note, below its bar, not filed:** on WSL NAT the resolver in `/etc/resolv.conf` is often the gateway, which is Core's host, so the DNS rule opens port 53 on Core's host and `core_host_findings` does not look at it; whoever runs the container measurement (EMB-448's chain) should check it.
**Merged:** `agent/umbrella/113-the-agent-containers-firewall-and-cores-address-from-inside` (code `d9a4b8a`, ff from `aecbcf8`; doc `f6c24010`, the worker's `1447d4ae` cherry-picked onto `7bb1421c`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (311 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-113-agent-container-firewall.md` assembled in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; every rule is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.
**Budget:** PROCEED at this fold (5-hour 22%, weekly 2%).
**Least sure about:** the script's self-check proves one off-list address is unreachable, not that the DNS allowance stays DNS-only, so a resolver on Core's own host is the place this boundary is thinnest.

---

## 2026-11-25 07:09 — core/157 core-keeps-definitions-premade-suites-and-confirmations

**Decided:** nothing suite-wide. Core keeps HIL definitions and records confirmations: `POST /definitions` checks a test, suite or plan with the crate's `check` functions (and `hil_check::check_test` when the request carries a study and a bench), keeps it as `definitions/<definition_hash>.json`, posted twice kept once, refused `422` with the crate's reasons; `GET /definitions/{hash}`; `GET /suites` indexes the premade suites under `EMBARCH_SUITES_DIR` by id, version and manifest hash; `GET /confirmations/pending`; `GET /confirmations/{hash}/card` issues a single-use nonce (32 bytes, ten minutes, in memory) to the person's token only; `POST /confirmations` spends it and appends a `confirmed` entry to the run log with `kind`, `sha256`, `scope`, `surface` and, for a suite, `core_holds`. All six are lease-open; `DOCUMENTED_ROUTE_COUNT` 53 to 59. Core's build now enables `hil-test` on `embarch-study-designer`. **New core decision 133** in a new `decisions/definitions.md`, marking plan choices 7, 8 and 11 as the owner's to strike. **The worker's calls, which I keep, all in 133:** a new `token_store::CONFIRMATION_ROUTES` refuses the agent's token on every Core, beside 132's service-only `PERSON_ROUTES` and through the same `person_middleware`, the handlers re-checking scope; the card route is the nonce route, since the task named a nonce and a post but no card route; `GET /suites` is an extra route for EMB-364 and EMB-376; a suite checkout is any folder holding `suite.json` up to three levels down (assumed, said so); the nonce is spent before the "needs none" `409`, so a replayed nonce is `403`; `surface` is a caller-written label, the scope comes from the token; a suite Core does not hold is confirmed once by its manifest hash and its tests then read `confirmed_with_suite`. `spec.md` deliberately not edited (an invariant line pushed it into reserve; the worker reverted it rather than file a debt).
**Merged:** `agent/core/157-core-keeps-definitions-premade-suites-and-confirmations` (code `2e8a18b`, ff from `22646fc`; doc `3f9ffd2f` and `40517a43`, the worker's `8baf99f5` and `2a6e2bfb` cherry-picked onto `d21d666e`). Re-gated on the merge result, against `embarch-study-designer` at `2366f86` (`study-designer/096`, landed first): `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (540 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-355-definitions-and-confirmations.md` assembled in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has none of these routes until it is redeployed with this commit; nothing consumes a confirmation until EMB-364.
**Budget:** PROCEED at this fold (5-hour 22%, weekly 2%).
**Least sure about:** the nonce store is in memory, so a Core restart between a card's rendering and its post refuses the post; that is the safe direction, but whether ten minutes and loss on restart suit a person reading a long card is unmeasured.

---

## 2026-11-25 07:07 — study-designer/096 expand-a-test-selection-into-the-resolved-run-file

**Decided:** nothing suite-wide; I read the shared-crate diff before landing it. **Leg start, to carry:** 5-hour 12%, weekly 1%, PROCEED. Step 0 recovered nothing (no claim, no unit worktree, no stop marker); neither bench role attached (`fleet-hardware.py --refresh`, 06:47), so `api/059` and `dev-bench/038` stay `open`. `suite/063`'s thread (ts `1795612302.163159`) had no reply 35 minutes after the announcement, so its window is closed and it runs as this leg's last unit. Split four Fleet Ready issues at `2cfd93a4`, all `filed` to Fleet Working: EMB-355 to this task, EMB-363 to `core/157`, EMB-445 to `umbrella/113`, and EMB-412 to `chat/041`, which is left `open` for the next leg (split so the refill gate read 4 across 4 scopes rather than firing a sweep with 25 issues still unsplit). Announced (ts `1795614703.403889`). This unit: `src/hil_expand.rs` behind `hil-test`, `expand(suite, plan, dut, ctx) -> Result<Expansion, ExpandError>`, `Expansion {run: RunJson, selection: SelectionRecord, studies}`, `RunJson::hash()` over `canonical_json`, `duration_bound`. **New study-designer decision 111** in `decisions/hil-tests.md`, marking plan choice 9 (caller-written `run_id`) as the owner's to strike. **The worker's calls, which I keep, all in 111:** the record is `SelectionRecord`, leaving `hil_test::Selection` alone; `expand` returns a struct, not a pair, so the expanded studies travel with `run.json`; status order is `not_applicable`, then the plan's picks, then `hook_unmapped`/`bench_missing` for a picked test, else `not_selected`; a numeric limit cannot carry a template placeholder (it is `f64`), so templates fill names and `expect` values only; each test entry carries `step_budget_ms` and `duration_bound` is its sum times `run_count`; confirmation scopes are `capability:<name>` and `hook:<name>`, the worker's own convention. **Public-type change, read and accepted:** four optional fields, `TestDef.applies_when`, `hooks`, `checks` and `Plan.bench_order`, all skipped when empty so no file or hash moves; the three `TestDef` fields join `derived_diff`'s deciding set. No consumer builds either type by literal (`core/157` enables `hil-test` and was gated against this). `hil-run.md`'s setup terms now carry `k` instead of `scope`, matching 109. **Debt filed by the worker:** `hil-run.md` in reserve (378 B left), `tasks/study-designer/097-compact-study-designer.md` `blocked`, `In flux: yes`, due 2026-12-09, unparks when EMB-364, EMB-356 and EMB-376 land.
**Merged:** `agent/study-designer/096-expand-a-test-selection-into-the-resolved-run-file` (code `2366f86`, ff from `8ecf13e`; doc `4641e35a`, ff from `e5dce1e8`). Re-gated on the merge result: `clippy --all-targets -D warnings` and `cargo test` under defaults, `hil-test`, `std,reducers,hil-image,hil-test` (Core's set after `core/157`), clippy under `study-ui,gatt-extract,eap-parse` (the UI's), and `--all-features` (498 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/study-designer-240-hil-run-expansion.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 12%, weekly 1%, wave 6, capped at the leg's 4 units, one of them `suite/063`) and at dispatch (5-hour 15%); PROCEED at this fold (5-hour 21%, weekly 2%).
**Least sure about:** `expand` takes bench existence as a list of names and does not check a bench's configuration against its description, so a run can be resolved for a bench that exists by name but is wired differently; Core's prepare route (EMB-364) is where that has to be refused.

---

## 2026-11-25 06:43 — umbrella/112 a-pure-renderer-for-the-agents-container

**Decided:** nothing suite-wide. New `src/agent.rs`, pure, no I/O, nothing calling it yet (`#![allow(dead_code)]` until EMB-445 to EMB-448): `AgentContainer`, `Topology` (`linux`, `wsl-host`, `docker-desktop`, `macos`, the last two marked unverified), `Runtime`; `run_args(plan, core_addr)` renders the vector unchecked and `try_run_args` is the checked entry later units should call; `forbidden_findings` scans a vector for the forbidden options, env names, mounts and `person-token` paths; `container_toml` and `parse_container_toml` round-trip with the vector's SHA-256 and `hand_edited()`. **New umbrella decision 62** in a new `decisions/agent-container.md`, naming each mount and why it is read-only or read-write, and marking the shape as the plan's recommendation the owner may strike (plan choices 1, 2, 4, 5, 11, 24). **The worker's calls, which I keep, all in 62:** the hash is taken over the vector with a `<core-addr>` placeholder, because umbrella decision 6 never persists Core's address; two fields the issue did not list, `bin_dir` and `env`; `west_workspace` is a list of named projects, each read-only at `/work/<name>`; the capabilities added after `--cap-drop ALL` are `NET_ADMIN`, `NET_RAW`, `SETUID`, `SETGID` for the root entrypoint, assumed and said so; the topologies differ only in the `host.docker.internal` host entry. A mount counts as a token folder when its last path component is `embarch`, `tokens`, `token` or `person-token` outside `/agents/`, a name match the worker flagged for EMB-447 to confirm against the real paths. `open.md` untouched, so `umbrella/111`'s park is unchanged. **Filed this leg, spooled (Linear at its free plan's active-issue cap):** the 2026-11-24 day fold left that day twice in `supervisor-log.md`, the folded entry and a second heading with all 43 unit entries demoted to `###` (about 40 KB); `--from audit` against `embarch-fleet`, so the owner's Backlog.
**Merged:** `agent/umbrella/112-a-pure-renderer-for-the-agents-container` (code `aecbcf8`, ff from `4715a1a`; doc `5e323a7d`, the worker's `c4f6790b` cherry-picked onto `eee38f71`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (306 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-170-agent-container-renderer.md` was assembled in `study-designer/095`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from a board; every flag and mount is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.
**Budget:** PROCEED at this fold (5-hour 10%, weekly 1%).
**Least sure about:** the token-folder test matches folder names, not the real layout, so a token folder under a name it does not list would pass the forbidden-input scan; EMB-447, which writes the real paths, is where that has to be checked.

**Leg end, to carry:** 4 of 4 units landed, none blocked. **`suite/063` (EMB-358) is open and parked with ts `1795612302.163159`; its window closed 06:41 with no reply as of 06:42 — the next leg polls the thread once more and runs it as its last unit.** The `embarch-study-designer`, `embarch-topology` links beside the core, ui, api and umbrella worktree parents point at the main checkouts, which match `origin/main`; the pass needs them repointed at its own branch while it gates, as `suite/062` did. Fleet Ready still holds 22 unsplit issues; EMB-412 (chat), EMB-385 (ui), EMB-487 and EMB-374 (api), EMB-324 (core, verify-only) are free, and EMB-355, EMB-363, EMB-341, EMB-336, EMB-335 and EMB-445/446 were unblocked by this leg's four. Bench tasks `api/059` and `dev-bench/038` stay open, no board.

---

## 2026-11-25 06:41 — core/156 a-service-core-refuses-identity-routes-to-the-agents-token

**Decided:** nothing suite-wide. A `--service` Core answers `403` to the agent's token on the eleven identity routes (probe enrol, unenrol, set board, unenrol by serial, dev-bench link, signal declare and remove, instrument declare and remove, bootload ports set and clear), naming embarch-ui and the CLI under `EMBARCH_PERSON_TOKEN`; a development Core serves both tokens as before. The table is `token_store::PERSON_ROUTES`, applied by a `person_middleware` inside auth and outside the lease layer, so the `403` comes before any `409` and is call-logged; `AppState::person_only` is set from `--service` so a test runs both modes. **New core decision 132** in `decisions/auth.md`, with a dated pointer on 109 amending its "nothing is refused by scope" clause; it marks the rule as the owner's to strike (the standalone pass is the alternative) and says what it does not stop: an agent that can read `person-token` can still use it (assumed, not measured). `interfaces/topology.md` and `interfaces/instruments.md` name each route's scope. **Follow-up, already filed:** `embarch-api`'s identity tools will show this `403` unexplained on a service Core until EMB-335. **Reviewer's note, below its bar, not filed:** `notes/hil/12-prevention.md` also lists "a tap's declared origin" and "Make live's declarations" as the person's, and neither is in `PERSON_ROUTES`; 132 lists its routes explicitly and claims neither. **The worker flagged** that code and docs elsewhere cite "decision 134" for `status`'s `mode` field where 129 is meant; not touched here, worth a check by whoever next works in core's auth docs.
**Merged:** `agent/core/156-a-service-core-refuses-identity-routes-to-the-agents-token` (code `22646fc`, ff from `0108da1`; doc `a75984d9` and `eee38f71`, the worker's `358a23ab` and its anchor fix `3866852f` cherry-picked onto `c91f40c1`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (528 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core refuses nothing new until it is redeployed with this commit.
**Budget:** PROCEED at this fold (5-hour 10%, weekly 1%).
**Least sure about:** whether any current client sends an identity call with the agent's token on the owner's own service Core today; once Core is redeployed, such a call that used to work answers `403`, and only EMB-335 makes that refusal readable.

---

## 2026-11-25 06:39 — api/195 the-client-sends-cores-token-only-after-a-challenge

**Decided:** nothing suite-wide; I read the shared-crate diff (`embarch-core-client` gains a public `attest` module, `CoreClient::attestation()`, `CoreClient::new_with_stores(...)` and `CoreConfig::token_is_explicit(scope)`; no public item changed) and built `embarch-ui` and `embarch-umbrella` at `origin/main` against the branch before landing. Every request now takes its token through a private `CoreClient::attested()`: one `POST /auth/challenge` per connection, cached, cleared on a connect failure. With a `core-fingerprint` beside the token file (same discovery, WSL2 included) a match sends the machine-wide token, a mismatch the development store's (`%LOCALAPPDATA%\embarch\dev\` through WSL2, `~/.local/state/embarch/dev`) or no `Authorization` header and an error naming both fingerprints; a bad signature or foreign frame sends nothing. `core_key::check` and `fresh_nonce` moved into the crate. `status` (tool and CLI) carries `attestation {mode, fingerprint, installed_fingerprint, matches, error?}`. **New api decision 133** in `decisions/client-crate-funnel.md`; 109 untouched. **The worker's call, which I keep:** with no `core-fingerprint` file an explicit config token is sent with no challenge, where the task said "sent only after the challenge"; no file means no Core on the machine is attested, and challenging there would have needed a signing route in every fake Core in the suite (133 records it). An unresolvable WSL2 path is treated as unattested, fail-open, the same as an absent file. **Folded:** `status.d/api-195-attested-token.md` into `embarch-token.md` §2's `embarch-api` row. **Reviewer's note, below its bar, not filed:** in the container topology `notes/hil/12-prevention.md` puts the fingerprint copy in the container's definition folder, and this client looks only beside the token file, so inside a container it would see no fingerprint and send unchallenged; that belongs to embarch-api's container mode in the EMB-444 chain, and whoever splits it should name the lookup.
**Merged:** `agent/api/195-the-client-sends-cores-token-only-after-a-challenge` (code `5e18cc3`, ff from `9f698e3`; doc `c91f40c1`, the worker's `152e1588` cherry-picked onto `cac9ad95`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test` (559 passed); `embarch-ui` at `origin/main` against the branch: build, clippy, 346 tests green; `embarch-umbrella` at `origin/main` against it: build, 298 tests green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-376-attested-token.md` was assembled in `study-designer/095`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a live-Core check: install a `core-fingerprint` beside the token file and confirm a matching service Core gets the machine-wide token and a development Core gets the development store's, through WSL2 on the bench machine. **Deploy debt:** the MCP server and `embarch-ui` pick this up only when rebuilt; until a `core-fingerprint` exists on the machine nothing changes.
**Budget:** PROCEED at this fold (5-hour 10%, weekly 1%).
**Least sure about:** the WSL2 shell-out that finds `%LOCALAPPDATA%` has never run against a real machine, and its failure is fail-open, so a broken lookup on the bench would look exactly like an unattested machine and send the machine-wide token as today.

---

## 2026-11-25 06:37 — study-designer/095 a-hil-test-is-checked-when-it-is-defined

**Decided:** nothing suite-wide; I read the shared-crate diff before landing it (one `pub mod hil_check` line in `lib.rs` behind `hil-test`, the rest new files; no consumer enables `hil-test`, so no consumer's build moves). **Leg start, to carry:** the weekly window had reset (5-hour 1%, weekly 0%), so the previous leg's HOLD is over. Step 0 recovered nothing (no claim, no unit worktree, no stop marker). Neither bench role attached (`fleet-hardware.py --refresh`, 06:08), so `api/059` and `dev-bench/038` stay `open`. Split five Fleet Ready issues at `bf0f6723`, all `filed` to Fleet Working: EMB-354 to this task, EMB-333 to `api/195`, EMB-444 to `umbrella/112`, EMB-331 to `core/156`, and **EMB-358 to `suite/063`, a cross-repo pass, announced and parked** (ts `1795612302.163159`, 06:11; window closes 06:41). It is parked for the next leg because this one is at its unit cap: `Instrument` gains optional `metrology` and `calibration`, and Core's test helper, `embarch-api`'s `declare_instrument` builder and `embarch-ui`'s Make live build it by struct literal, so all four repos land together as `suite/059` did with `safe_off`. Announced the four worker issues (ts `1795612297.120619`). Refill gate not owed after the split (4 across 4 scopes); 22 issues remain unsplit in Fleet Ready. This unit: `check_test(test, StudyKind, &SuiteBench, &BTreeMap<String, Measured>)` returns every refusal, each `{test, field, rule, reason}`; `energises(step, bench)` is public for Core's go card. **New study-designer decision 110** in `decisions/hil-tests.md`, marking plan choices 5, 18 and 21 as the owner's to strike. **The worker's calls, which I keep, all in 110 or `open.md`:** a bench has a DUT when a saved-bench part has `role: "dut"` (spelling assumed from embarch-ui decision 73, not read from a Core type); a signal is a bench board's only when it equals that board's `part`, otherwise the DUT's, so it energises (fail safe, since the suite format has no signal-to-board map; in `open.md`); teardown is not walked, and a `Repeat` is walked twice; an action prompt's confirming measurement must feed a limit, since a host step's `until` is a text pattern naming no measurement; a person's numeric reading takes its metrology from the caller's map; instrument metrology comes in through that map until EMB-358 lands. Two limits on one measurement are refused, closing the reviewer's note on `study-designer/094`.
**Merged:** `agent/study-designer/095-a-hil-test-is-checked-when-it-is-defined` (code `8ecf13e`, ff from `faddb4c`; doc `cac9ad95`, the worker's `0ed109fa` cherry-picked onto `7e1e1206`). Re-gated on the merge result: `clippy --all-targets -D warnings` and `cargo test` clean under no features, `hil-test`, `std,reducers,hil-image` (Core's), `study-ui,gatt-extract,eap-parse` (the UI's, clippy) and `--all-features` (491 passed); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature rows `features.d/study-designer-095-hil-test-definition-checks.md`, and `api-376` and `umbrella-170` from the units landed beside it, assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 1%, weekly 0%, wave 6, capped at the leg's 4 units) and at dispatch (5-hour 3%); PROCEED at this fold (5-hour 10%, weekly 1%).
**Least sure about:** the energising rule counts any signal not named exactly as a bench board's `part` as the DUT's, so a correctly declared read-only bench line under a different name refuses a valid test; that is the safe direction, but the first real suite will show whether the name match is too strict.

---

## 2026-11-25 04:08 — chat/040 the-linker-offers-datasheet-and-spec-sections

**Decided:** nothing suite-wide. The 💡 linker has an atlas section source on decision 112's interface: `embarch-atlas refs --json` in the chat's folder with a 10 s limit, re-run only when the mtimes of `current.json`, `atlases/` or `docs/` (or the binary) changed, checked by a stat before a cards call; the binary is a new `embarchChat.atlasPath` setting, `embarch-atlas` on PATH by default; no binary, no atlas, a failed run, a timeout or bad JSON leaves the kind empty and logs once per cause. Gated on a cue word (datasheet, spec, specification, standard, section, chapter, table, manual, errata, app note) or a document's `part` named in the draft; written `<doc_id> p<N> §<id> "<title>"`, the head decision 16's citation links match. **New chat decision 114** in `decisions/references.md`, marking the cue words, the 10 s limit and the change-stat refresh as plan choices the owner may strike; 96 untouched. **The worker's calls, which I keep, all in 114:** a part named in the draft opens the gate for that document's sections only; cue words are left out of an entry's own match words; a section with no page, a page over 9999, or an id that cleaning would change is not offered; a 20,000-section cap, marked assumed in `spec/constants.md`; the stat covers only `docs/`'s top level, so an edit inside one document's folder is not seen until something else moves (recorded in 114). EMB-412 (Kconfig symbols and devicetree nodes) shares this read and is now unblocked. **Gate note:** the worker ran `npm test` without `EMBARCH_DESK_BIN` and reported 81 skips; my re-run with `desk-gate-bin.py`'s binary (desk `20fa59c`) is the gate of record.
**Merged:** `agent/chat/040-the-linker-offers-datasheet-and-spec-sections` (code `4093c1a`, ff; doc `3962c9e0`, the worker's `0645b448` cherry-picked onto `86b58e9a`). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` (414 tests, 411 pass, 0 fail, 3 skipped, desk gate binary from desk `20fa59c`), `test:webview` all green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/chat-061-linker-atlas-sections.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none (tested against a fake `embarch-atlas` only, and not seen in a real VS Code window; the feature row says so; the `cards-refs` model call was not re-recorded for the new `section` kind).
**Budget:** PROCEED at dispatch (5-hour 86%, weekly 89%, wave 1); **HOLD at this fold** (weekly 90% of a 90% cap, resets in 1h52m; 5-hour 88%, inside its reset grace). This leg ends here at its fourth unit, and the listener should not respawn until the weekly window resets.
**Least sure about:** the change-stat refresh watches directory mtimes, which a re-translated document inside `docs/<doc>/` does not move, so the linker can offer a section list one translation stale until the atlas is rebuilt; 114 records it, and a real atlas will show whether it matters.

---

## 2026-11-25 03:56 — api/194 compact-api

**Decided:** nothing. `embarch-api/open.md` went from 4,292 to 3,779 B, out of reserve, by two verbatim moves with their relative links fixed: the live-log debt (mock Core only; run `mem_read` and `reset` on a bench with a lease held and read `embarch/live/`) to `open/bench-verification.md`, and the Windows smoke-harness gap to `open/unmeasured-details.md`; each `open.md` pointer bullet now names what it gained. The `person_writer` Windows-branch line from `api/193` stays in `open.md` with its `cargo test person_writer` command, as the task's `Must not delete:` asked. **The worker's answer to `DOC-COMPACTION-PASS.md`'s question:** not `spec.md` alone, and it is not meant to be; it states what is true and links `decisions.md`, `open.md` and `interfaces/` for the rest, so "what is unverified today" now takes `spec.md` to `open.md` to `open/*.md`, three layers, which is the intended split between truth, reasons and the unresolved. **Mine:** the worker's commit subject cited "EMB-194", a Linear key that is not this task's (the task has no issue), so I landed it with that key removed rather than put a wrong issue reference on `main`. The size ledger now holds only `umbrella/111` (blocked, due 2026-12-09).
**Merged:** `agent/api/194-compact-api` (doc `06ae6b10`, the worker's `f1751160` cherry-picked onto `aae8a2d9` with its subject corrected; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved live-log line still needs a bench with a lease.
**Budget:** PROCEED at dispatch (5-hour 84%, weekly 89%, wave 1); PROCEED at this fold (5-hour 84%, weekly 89%).
**Least sure about:** whether the move into `open/bench-verification.md` puts that file nearer its own cap than the ledger shows; it went from 2,178 to 2,495 B and nothing flagged it, but `open/` files are where the next debts will land.

---

## 2026-11-25 03:53 — study-designer/094 types-for-a-hil-test-a-suite-and-a-plan

**Decided:** nothing suite-wide; I read the shared-crate diff before landing it (one new feature line in `Cargo.toml`, one `pub mod` line in `lib.rs`, the rest new files). New `src/hil_test.rs` behind a new `hil-test` feature (`verdicts`, `dep:sha2`, `dep:serde_json`, all already optional dependencies, so no consumer's graph moves and none enables it): `TestDef`, `SuiteManifest` and `Plan`, every struct and tagged enum `deny_unknown_fields`; `check()` refuses a `schema` other than 1, `run_count` 0 and a suite bench `description` that is not a JSON object; `definition_hash()` is SHA-256 over RFC 8785 canonical JSON through a canonicaliser the worker wrote (UTF-16 key order, ES6 numbers); `derived_diff(copy, premade)` returns `{field, old, new}`, per measurement for limits and sources, ignoring `test_id`, `title`, `tags`, `schema` and `derived_from`. **New study-designer decision 109** in a new `decisions/hil-tests.md`, marking the four choices the owner may strike (JSON over TOML, plan choice 2; a suite bench carrying its boards' command lines, plan choice 4; the suite's own requirement slugs over the atlas's `rid`, plan choice 3; `expect` limits, plan choice 27); no pointer on 90 or 91, and 12, 73 and 108 not grown. **The worker's calls, which I keep, all in 109:** a suite bench's saved-bench `description` stays an opaque object, since embarch-ui owns that shape; `tags` live on the test and do not decide a verdict; `bench.config` and `precondition` are required (the task's "`reset` by default, written out" read as always written); a plan's `select` is `all` or `some {tests, tags}`; `setup_terms` are `{name, unit, u, k}` uncertainty terms; `verdicts::DecisionRule` is wrapped as `DecisionRuleSpec` to refuse unknown keys rather than changing the public type. This unblocks EMB-354 (checks at definition time) and EMB-385. **Reviewer's notes, below its bar, not filed:** decision 90 hashes a file's bytes as written while 109 hashes the canonical serialisation of a test, a split 109 states (`StudyRef.hash` stays over the study file's bytes); `derived_diff` keys limits and sources by measurement name, so two limits on one measurement would collapse and could hide a change to the first, which EMB-354's definition-time checks should refuse as a duplicate. **Linear:** the retry of `filed` reached EMB-353 and EMB-411, both now in Fleet Working; the leg-start note about them is settled.
**Merged:** `agent/study-designer/094-types-for-a-hil-test-a-suite-and-a-plan` (code `faddb4c`, ff from `3e4e301`; doc `e973a520`, the worker's `870441c5` cherry-picked onto `e22bc4ee`). Re-gated on the merge result: `cargo test` and `clippy --all-targets -D warnings` clean under no features, `alloc` alone, `hil-test`, `std,reducers,hil-image` (Core's), `study-ui,gatt-extract,eap-parse` (the UI's) and `--all-features`; the 8 new `hil_tests` tests ran; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/study-designer-230-hil-test-suite-plan-types.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 80%, weekly 89%, wave 1); PROCEED at this fold (5-hour 84%, weekly 89%).
**Least sure about:** the definition hash rests on a hand-written RFC 8785 canonicaliser checked only against the RFC's number samples and the worker's own cases, and integers above 2^53 are not canonicalised as doubles; a confirmation binds this hash, so a second implementation (Core's, or a reference library in a test) disagreeing on one number would refuse a valid confirmation.

---

## 2026-11-25 03:43 — core/155 a-host-step-parses-its-number-and-writes-measurements

**Decided:** nothing suite-wide. Split three Fleet Ready issues at leg start (`d68e30ab`): EMB-359 as `tasks/core/155`, EMB-353 as `tasks/study-designer/094` (HIL test, suite and plan types, the root of the HIL Test chain), EMB-411 as `tasks/chat/040` (atlas sections in the linker); announced ts `1795602826.451439`. `filed` reached EMB-359 only: EMB-353 got its comment and then hit Linear's hourly rate limit at the status move, and EMB-411 hit it before the comment, so both still sit in Fleet Ready and the next leg's `ready` will print them `ALREADY SPLIT`; run `filed` with the paths it names. This unit: after an `Exchange` or queried `Instrument` step with a `parse`, `run_step` calls `parse_step_number` on the recorded reply (after the 4,096-byte cap) and the step's record in `events.json` gets `parsed {name, value, incomplete?}`; new `src/host_parse.rs` writes `measurements.json` for a host study once `events.json` is final and before sealing, so it is a signed subject; a study with no parse writes none. `by` and `instrument` come from what the step addressed (a `dut`-role signal `dut`; a bench board's signal `bench` with the board; an instrument `bench` with the instrument), through a now-shared `topology_signal_origin` in `measurements.rs` that `study.rs` also uses; `U` is `undeclared`. **New core decision 131** in a new `decisions/host-parse.md`; 95 and 110 not grown. **The worker's calls, which I keep:** a cut reply is still parsed and carries `truncated_reply`, plus `parse_failed` when no number is found (`null` stays reserved for `parse_failed`, as `hil-shapes.md` says); a step with no backend reply gets no `parsed`; an undeclared signal counts as `dut`, as decision 113 reads it. **Open gap, logged in `embarch-core/open/unverified-and-moved.md`:** a parse inside a `Repeat` repeats its measurement name once per pass, told apart by `source.iteration`, where `hil-shapes.md` asks names unique within the file; study-designer decision 108's uniqueness rule counts a `Repeat` inner step once, so the two standing decisions disagree and the shape's owner should settle it. **Filed (spooled):** `GET /study/{id}/measurements` still answers 422 naming "a host study", which `embarch-api` matches by text, so fixing it is a core and api pass; filed `--from worker` under `embarch-core`, and it spooled because the Linear workspace is at its free plan's active-issue cap (three earlier filings are spooled for the same reason; `leg-end`'s archive of old Done issues is what frees room).
**Merged:** `agent/core/155-a-host-step-parses-its-number-and-writes-measurements` (code `0108da1`, ff from `d645ecd`; doc `ed57d5bb`, the worker's `da086fb0` cherry-picked onto `dfa05876`). Re-gated on the merge result: `cargo build`, `cargo test` (524 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-285-host-study-parse.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a host study with a `parse` run on a bench against a DUT console, a bench board's signal and a real instrument, checking `by`, `instrument` and the signed subject list; the native Windows build. **Deploy debt** carried from `suite/062`: Core, `embarch-api` and `embarch-ui` deploy together for host v25.
**Budget:** PROCEED at leg start (5-hour 77%, weekly 88%, wave 1) and at dispatch (5-hour 78%, weekly 88%); PROCEED at this fold (5-hour 80%, weekly 89%).
**Least sure about:** a parse in a cut reply keeps its number with `truncated_reply` beside it; a number that was itself cut at the 4,096-byte boundary reads as a smaller, valid value, and only a verdict rule that refuses `truncated_reply` keeps it from passing a limit.

---

## 2026-11-25 03:26 — suite/062 a-host-step-parses-a-number-and-a-prompt-has-a-kind

**Decided:** **a suite pass, run by me as this leg's last unit, and a host-schema bump, both announced** (ts `1795597152.735759`, 01:59; the window closed 02:29 with no reply, re-polled at 03:06, still none). `embarch-study-designer`: `parse: Option<StepParse {name, pattern, unit}>` on `HostAction::Exchange` and on a queried `HostAction::Instrument` (a parse on an unqueried one is refused, no reply); `parse_step_number(reply, parse) -> Result<f64, Incomplete>` behind `std` and `reducers`, the pattern's first match with its one capture, trimmed, read by the number grammar as exactly one number spanning it, else `parse_failed`; `Prompt` gains `kind: Option<PromptKind>` (`setup`, `action`, `observation`, `clearance`, lower case), `confirmed_by` (required on `action`, must name a parse, not an observation's answer, anywhere in the study) and `answer: PromptAnswer {name, answers | number: ObservedNumber {unit, resolution, U, k}}` (required on `observation`); either field on another kind, or on a prompt with no kind, is refused; a measurement name is unique across every parse and answer in steps, teardown and `Repeat` inner steps. New `MAX_HOST_PROMPT_ANSWERS` 16, assumed. **`number_grammar` moved from `pdf-text` to `std`**, since Core builds no PDF reader. **`HOST_TYPE_SCHEMA_VERSION` 24 to 25**, wire stays 17; every new field skipped when `None`, and a v24 study with an exchange, a query and a prompt round-trips byte for byte (test-pinned). **New study-designer decision 108** in a new `decisions/host-parse.md`; dated pointers on 88 (`host-prompt.md`), 99 (`hil-declarations.md`) and 101's gating (`hil-pdf.md`); `hil-shapes.md`'s `method {kind: "parse"}`, `source.step` and `prompt_kind` point at the fields; `spec.md` and `interfaces/limits.md` rows. **My calls beyond the task's text:** the observation shape requires `resolution` and `U` and leaves `k` optional (2), as `StudyDeclared` does; `PromptKind` serializes lower case where `PatternKind` is PascalCase, because the task and the prevention notes spell the kinds that way; an observation's answer shares the parse namespace but cannot confirm an action. Consumers changed only what the fields forced: Core's executor patterns take `..` and its test constructors `None` (Core acts on neither yet; T.8 and T.16 do); the UI's bench-config probe sets `None`. `embarch-api` and `embarch-umbrella` built and tested unchanged. **Reviewer's note, below its bar:** Core now accepts a study declaring a `parse` and computes nothing from it, the silent accept `schema_version.rs`'s v22 entry warns about, and Core's "no step reads a number out of a reply" decision now describes Core alone; EMB-359 (Core parses a number at step time) and EMB-367 (Core knows a prompt's kind) are the units that close it, and this unit unblocks both. **To carry, this leg ends here at 3 units:** `suite/062` is a leg's last unit by rule, and weekly was 88% of a 90% cap. Fleet Ready still holds EMB-411 to EMB-415 (chat, one linker kind each, one per wave), which Linear lists as blocked by EMB-408 until `finish` moves it (Done in substance since `chat/038`); `tasks/api/194` (compaction, `In flux: no`) is dispatchable. Linear stayed rate-limited all leg: `ready --brief` dies, single `show`, `filed` and `finish` get through. I repointed the `embarch-study-designer` links beside the core, ui, api and umbrella worktree parents at the branch for this pass and restored them to the main checkouts after.
**Merged:** `agent/suite/062-a-host-step-parses-a-number-and-a-prompt-has-a-kind`, landed in order: study-designer `3e4e301` (from `31b4408`), core `d645ecd` (from `cf5b661`), ui `7d52207` (from `d66e313`) (each ff from its `origin/main`); doc `df83f1b2`, my own commit in the leg worktree. Gated before any push with every consumer's path-dep pointed at the branch: study-designer `cargo build`, `test`, `clippy --all-targets -D warnings` under no features, `alloc`, `alloc,reducers`, `std,reducers,hil-image`, `study-ui,gatt-extract,eap-parse` and `--all-features`; Core 518, ui 346, api 552 and umbrella 298 tests passed, the last two with no change of their own; clippy clean in each; `check-docs.py` 12/12; client names clean on the three code worktrees. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none from the code; a **deploy debt**: the host gate is a strict match both ways, so Core, `embarch-api` (MCP server restarted) and `embarch-ui` deploy together and `embarch-umbrella` is rebuilt, or `embarch doctor` check 11 warns. The installed Core already reports host v21 (`fleet-hardware.py`, 02:43), so it was behind before this unit. The native Windows build of Core.
**Budget:** PROCEED at the leg's last check (5-hour 70%, weekly 88%); PROCEED at this fold (5-hour 75%, weekly 88%).
**Least sure about:** `parse_step_number` takes the pattern's first match only, so a reply that echoes the command or holds the same key twice (a log line before the answer) reads the wrong number with no error; one parse per step and first-match are the plan's recommendations, and the first real study will show whether the pattern needs anchoring advice in the guide.

---

## 2026-11-25 03:05 — api/193 a-confined-writer-for-the-persons-embarch-folder

**Decided:** nothing suite-wide. New `src/person_writer.rs` (`pub mod person_writer`): `ConfinedWriter::open(repo_root)` refuses a linked or non-folder `<repo>/embarch`; `write(kind, name, bytes)` takes a fixed set of kinds, each with one folder and one extension, and names in `[a-z0-9][a-z0-9._-]{0,99}`. On Unix every step is `rustix` `openat` with `O_NOFOLLOW`; on Windows each step is `symlink_metadata` refusing symlinks and reparse points, the link count read through `windows-sys`; a target with more than one hard link is refused; the write is a synced temp file renamed over the target; a test reads the module's own source for `Command` and spawn. Two target-gated dependencies added to `Cargo.toml` (`rustix` with `fs` on Unix, `windows-sys` on Windows). `ledger.rs` and `live_log.rs` are untouched, as the task said: moving today's writers onto it is the person mirror's unit (C.17). **New api decision 132** in a new `decisions/person-mirror.md`. **The worker's calls, which I keep, all in 132:** extensions `.study.json`, `.host-study.json`, `.test.toml`, `.suite.toml`, `.plan.toml`, `.results.json`, `.json` for saved benches and the measured atlas, `.jsonl` for the live log; a study's own folder is `studies/<study>/`, where `report_typ` writes `report.typ` and `prose` takes `<study>/<run>` and writes `runs/<run>.md`; plan choice 3 is marked the owner's to strike. **Reviewer's note, below its bar:** the kinds go past the design's list (saved benches, the measured atlas, the live log, host studies); 132 marks them plan choice 3's recommendation, one enum arm each. **New debt, filed by the worker:** its Windows debt line put `embarch-api/open.md` in reserve (4,292 of 5,120 B), so `tasks/api/194-compact-api.md` is `open`, `In flux: no`, due 2026-12-09, and must keep that line.
**Merged:** `agent/api/193-a-confined-writer-for-the-persons-embarch-folder` (code `9f698e3`, ff from `cd1f428`; doc `0e34d264`, the worker's `3856e88b` cherry-picked onto `7a16781f`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures; 10 new `person_writer` tests), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-390-person-writer.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** `cargo test person_writer` on Windows from the main checkout (the whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `aws-lc-sys`'s C build before it reaches the module); a Windows symlink and junction fixture is still unwritten, since those fixtures are `#[cfg(unix)]`; the native Windows build.
**Budget:** PROCEED at dispatch (5-hour 64%, weekly 87%, wave 2); PROCEED at this fold (5-hour 70%, weekly 88%).
**Least sure about:** the Windows branch checks each step with `symlink_metadata` and then opens by path, which leaves a window between check and open that `O_NOFOLLOW` closes on Unix; nothing here has run it, and the first Windows caller is where that gap would matter.

---

## 2026-11-25 03:04 — chat/039 the-linker-offers-branches-and-worktrees

**Decided:** nothing suite-wide. The 💡 linker has its first new source on decision 112's interface: new `src/assistant/refsGit.ts` (pure parsers, `gitSource`, a `GitRefs` reader cached 60 s per folder) reads `git for-each-ref` (300 newest over `refs/heads` and `refs/remotes/origin`, a remote with a local twin once) and `git worktree list --porcelain` in the chat folder's main clone; `src/deskService.ts` now exports `git`, `mainRepo` and `listWorktrees` rather than the source copying them; `chatHost.ts` refreshes git before a cards call. Lines are `branch <name>` (with ` (PR owner/repo#N)` when the desk's index has a PR on it) and `worktree <path> (branch <name>)`; gated on branch, worktree, checkout, clone, rebase, merge, or an exact branch name; the chat's own branch and worktree left out. **New chat decision 113** in `decisions/references.md`. **The worker's calls, which I keep:** a name or path with an unseen character, `<`, `>` or over 200 characters is dropped rather than cut; a detached worktree is written `(detached)`; a bare `main` in a draft offers `main` with no cue word, because an exact name does (113 says the owner may strike it, and it may prove noisy); the 300 cap, the cue words and the 60 s refresh are marked assumed. **Reviewer's note, below its bar, not filed:** the git read (5 s timeout) is awaited on the cards path, so a slow repository delays the cards. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`). **Linear rate-limited all leg start:** `ready --brief`, `list` and `finish` all died on Linear's 2,500/hour limit; single `show` and `filed` calls got through, and one team listing found 72 Fleet Ready issues, most of them HIL Test and container-pass issues whose blockers I could read for three before the limit (EMB-461 waits on EMB-448, EMB-451 on EMB-447, EMB-457 free). **EMB-410 split although Linear still names EMB-408 as its blocker in Fleet Working**: EMB-408's task landed and retired in `chat/038`, and only `finish`'s status move is missing, so the block is stale, not real. Split EMB-410 and EMB-457 at `6d313db3`, both `filed` (Fleet Working), announced ts `1795600044.833469`. **Bench:** `fleet-hardware.py --refresh` shows neither `dev-bench` nor `dut` attached, so `api/059` and `dev-bench/038` stay `open`. **Refill:** the gate fired on depth and spread; the only source commit since the last judged sweep is `umbrella/110`'s owner-debt line in `open.md`, so no sweep. **My error:** this task file as I wrote it said "decision 96, 204 B under its limit", which `check-decision-refs.py` reads as a reference to a decision 204, so `main` was red on that one check from the split commit (02:46) to this fold; the worker reworded the line on its branch, and `api/193`'s worker reported the red from its base. Write a size as "204 B" with no number beside "decision".
**Merged:** `agent/chat/039-the-linker-offers-branches-and-worktrees` (code `a70291c`, ff from `89b20a8`; doc `333e2799`, the worker's `52a0c771` cherry-picked onto `bb0b51d8`). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` (407 tests, 404 pass, 0 fail, 3 skipped; desk gate binary from desk `20fa59c`), `test:webview` all green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/chat-060-linker-branches-worktrees.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none (the feature has not been seen in a real VS Code window; the feature row says so).
**Budget:** PROCEED at leg start (5-hour 62%, weekly 87%, wave 2) and at dispatch (5-hour 64%, weekly 87%, wave 2), two dispatched in one wave; PROCEED at this fold (5-hour 69%, weekly 87%).
**Least sure about:** an exact-name match on a common branch name (`main`, `master`, `dev`) offering a branch line with no cue word; a draft that says "the main issue" would get a `branch main` line, and nothing measures how often.

---

## 2026-11-25 02:40 — core/154 core-holds-the-bench-ports-under-a-lease

**Decided:** nothing suite-wide. I split EMB-326 mid-leg (`8cb884ea`; `filed` hit the rate limit at the status move and reached it on the retry, so the issue may carry its filed comment twice) and dispatched it beside `umbrella/110` as this leg's fourth unit, rather than running `suite/062` myself: the wave had a second slot, both remaining candidates were ready, and a three-repo pass on top of three folds would have pushed this leg's context well past a batch. New `src/port_hold.rs`: a process-wide holder; `POST /lease`, and `LeaseSlot::study_started` for a study with no lease, open every declared direct signal port and instrument port that enumerates; release, expiry, idle release and `study_ended` close them when the last owner lets go. `port_hold::open(name, baud, timeout)` replaces `serialport::new().open()` at the exchange, serial-log, instrument, capture, host-study tap, device-study tap and outpost preflight sites; a held port is lent to one borrower at a time (a second gets an error, not a wait); a port absent at the take is adopted on first use. Not held, by design: bootload ports, the dev-bench link, the analog samples port. The signed record's `observed` gains `ports_held`. **New core decision 130** in a new `decisions/port-hold.md`; dated pointers on 93 (`lease.md`) and 4, 14, 15 (`platform.md`). **The worker's calls, which I keep:** a process-wide static rather than an `AppState` field (no signature changes across the call sites); **expiry gained a timer** (`LeaseSlot::spawn_expiry_watch`, a tokio task per take), because lazy expiry would hold ports after a lease ended; the liveness check itself stays lazy. **Doc debt, small, not filed:** decision 93's pointer took it from 35 B under its per-decision limit to 51 B over (`check-doc-size.py --pressure`), and 93's and 123's "no timer" wording now reads as the whole story where 130 adds one; the next core unit touching `lease.md` or `lease-idle.md` should fold a pointer in. **`suite/062` (EMB-352) stays `open`**: its window (ts `1795597152.735759`) closed at 02:29 with no reply, so the next leg may run it as its last unit without re-announcing; the task file says why it is three repos.
**Merged:** `agent/core/154-core-holds-the-bench-ports-under-a-lease` (code `cf5b661`, ff from `b539f6a`; doc `78090367`, the worker's `64c8cd99` cherry-picked onto `9d79ef78`). Re-gated on the merge result: `cargo build`, `cargo test` (516 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-350-ports-held-under-a-lease.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on Windows COM ports, a second open of a held signal or instrument port must fail while Core's own exchange, instrument call and study tap still work (COM exclusivity assumed); on a real CDC ACM bench port, what a hold does across a DUT reset or re-enumeration (a held handle may go stale); that asserting DTR at hold time does not reset a board a plain open leaves alone; the native Windows build.
**Budget:** PROCEED at dispatch (5-hour 57%, weekly 86%, wave 2); PROCEED at this fold (5-hour 62%, weekly 87%).
**Least sure about:** holding a CDC ACM port across a DUT reset: if the board re-enumerates, the held handle can go stale and every call under that lease fails until it ends, which pty tests cannot show; the first bench session under a lease is where it surfaces.

---

## 2026-11-25 02:40 — umbrella/110 install-core-verifies-a-signed-release-first

**Decided:** nothing suite-wide. `embarch install-core <release dir or archive> [--allow-downgrade] [--dry-run] [--data-dir DIR] [--trusted-root FILE | --refresh-trust-root]` (new `src/install_core.rs`): `install_core_elevated(source, data_dir, allow_downgrade, verifier, now)` creates `<data dir>/release-staging/<n>/` (owner-only 0700 on Unix; an `icacls` Administrators/SYSTEM grant on Windows, never run), copies the folder in or unpacks the archive with the OS `tar`, runs the verifier on the staged copy, applies the downgrade rule (`major.minor.patch[-pre]`; an unparseable version refused without `--allow-downgrade`), and writes `installed-release.json` by temp file and rename; a failed run removes its staging folder and leaves any record untouched. The real run passes `verify_release_with_root` as the verifier, unchanged. **New umbrella decision 61** in a new `decisions/install-core.md` (keeps `install.md` under its cap), naming the later units: self-elevation, installing the binaries from staging, registering the service under its own account, `setup` calling `install-core`, WSL2 hosts, pruning old staging. `interfaces/install-core.md` gives the record's shape; `spec/commands.md` has the row. **New debt, filed by the worker:** its owner debt line in `open.md` (one elevated Windows run with a signed and a tampered release, and the staging ACL listing only Administrators and SYSTEM) put `open.md` in reserve (4,634 of 5,120 B), so `tasks/umbrella/111-compact-umbrella.md` is `blocked`, `In flux: yes`, due 2026-12-09, unparking when the install follow-ups land. Under `DOC-BUDGET.md`'s split-first rule a later leg may unpark it early for a verbatim move, as `desk/038`'s entry did for four. **Reviewer's note, below its bar, not filed:** decision 61 lists umbrella re-launching itself elevated as a later unit, while umbrella decision 7 puts self-elevation in `embarch-core`; whoever builds the elevation unit reconciles them.
**Merged:** `agent/umbrella/110-install-core-verifies-a-signed-release-first` (code `4715a1a`, ff; doc `b3a8b0e8`, the worker's `62166429` cherry-picked onto `0d2c9c77`). Re-gated on the merge result: `cargo build`, `cargo test` (298 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/umbrella-165-install-core.md` assembled into `suite/features.md` in this fold. The whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `aws-lc-sys`'s C build; the worker type-checked the one `cfg(windows)` block in a throwaway crate against that target.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one elevated Windows run of `install-core` with a signed release and a tampered one, checking the staging folder's ACL lists only Administrators and SYSTEM (`open.md`'s line); the native Windows build.
**Budget:** PROCEED at dispatch (5-hour 57%, weekly 86%, wave 2), two dispatched; PROCEED at this fold (5-hour 59%, weekly 87%).
**Least sure about:** archive input shelling out to `tar` (bsdtar on Windows 10 and later): it is never exercised on Windows here, and an elevated step trusting whatever `tar` is first on PATH is a question the elevation unit should answer.

---

## 2026-11-25 02:28 — chat/038 the-linker-takes-references-of-any-kind

**Decided:** nothing suite-wide. The 💡 linker takes references from any number of sources: `src/assistant/refsBase.ts` (entry and source types), `refsDesk.ts` (the desk's issues and PRs, the first source, line and text unchanged), `references.ts` (`linkReferences` and the caps). The block is `<references>`, at most 12 lines, 3,600 characters and 4 lines per kind before the best of the rest fill it, each line `[rN] <kind>: <line>`; the rule names only the kinds present; a gated source offers lines only on a cue word or an exact name; `referenceText` asks the entry and `copiesTitle` checks every entry's titles. **New chat decision 112**, in a new `decisions/references.md`, into which the worker moved decision 88 verbatim from `assistant.md` (writing 112 there would have left `assistant.md` 219 B from its cap; the reviewer confirmed the move character by character, bar 88's dated pointer to 112). **The worker's calls, which I keep and the reviewer judged consistent with Promptu's contract §15.1:** issues and PRs share one scoring pool (88 scored them together; every other kind scores in its own), a gated source with only a name hit offers just the named entries, and the per-kind cap is two passes (4 of each kind in rank order, then the rest in rank order). The caps are marked assumed in `spec/constants.md` as the plan's recommendations. No real Haiku calls: the recorded `cards-refs` call still replays by its TASK line but holds a prompt of the old shape, and 112 says a later unit records it. **This is what EMB-410 to EMB-415 (one linker kind each) wait on in Linear**; `finish` after this push should move EMB-408 to Done and let the next `ready` offer them. **`suite/062`'s window (ts `1795597152.735759`) closed at 02:29 with no reply in its thread.**
**Merged:** `agent/chat/038-the-linker-takes-references-of-any-kind` (code `89b20a8`, ff from `695f46d`; doc `3dc7ccd8`, the worker's `6779dcf8` cherry-picked onto `99be4085`). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` (401 tests, 398 pass, 0 fail, 3 skipped; desk gate binary built from desk `20fa59c`), `test:webview` all green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 51%, weekly 86%, wave 2); PROCEED at the `core/153` fold (5-hour 55%, weekly 86%, wave 2).
**Least sure about:** sharing one pool for issues and PRs departs from the issue's "scored within a kind" to keep the existing tests unchanged; with six more kinds coming, a later kind unit may find the issue/PR pool's word rarities skewed by PRs, and nothing yet measures it.

---

## 2026-11-25 02:26 — core/153 core-keeps-a-service-store-and-a-development-store

**Decided:** nothing suite-wide. **First normal-mode leg after the burndown ended, so new decisions are back in scope**: I split four Fleet Ready issues that burndown legs had left for that reason, `chat/038` (EMB-408, `a2da724a`), `core/153` (EMB-323, `52de0e4d`), `umbrella/110` (EMB-338, `2b361b09`) and `suite/062` (EMB-352, `3dc22553`); all four `filed`, now Fleet Working; announced ts `1795597146.765199`. **EMB-352 became a `suite` task, not a study-designer one**: new fields on `HostAction::Exchange`/`Instrument`/`Prompt` break `embarch-core/src/host_study.rs` (exhaustive destructuring at about lines 539, 574, 600, and test constructors) and `embarch-ui/src/bench/files.rs` (constructs a `Prompt`) the moment the crate lands, so it is a sequenced pass. It also bumps the host schema 24 to 25 (the issue says 22 to 23; two bumps landed since). **Announced and parked, ts `1795597152.735759` at 01:59, window closes 02:29**, recorded on the task's State line; no reply in its thread at 02:26. Blockers read through the desk's issue route (`ready` still dies on Linear's rate limit): EMB-408 waits on EMB-403 (Done), EMB-323 on EMB-320 (Done), EMB-338, EMB-326 and EMB-352 on nothing. This unit: Core's `run --service` uses `<data dir>/store/` (never created by Core; missing is a start failure naming the elevated install), `run --store <dir>` a development store created if missing, neither flag today's layout; `/status` gains `mode`, `keyid`, `study_in_flight`; the challenge answer carries `mode` unsigned; `observed.mode` is signed; `public-key` (hex) written beside the key. **New core decision 129** in `decisions/auth.md`, 53 amended with a dated pointer; 110 not grown. **The worker's calls, which I keep:** `logs/` stays in `<data dir>` (tracing starts before the flags parse; 129 says so); `flashed-images.jsonl` follows `run-log.jsonl` into the store; `EMBARCH_TOKEN`/`EMBARCH_PERSON_TOKEN` still override the token files in `--store` mode (decision 109). **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`); the local `agent/atlas/097` branches are the parked prior-art unit, not recovery. `finish` exit 1 (EMB-334, EMB-312, EMB-136 open). Refill gate fired on depth (3 dispatchable after the split); every source commit since the 2026-11-24 02:36 sweep was already judged by earlier legs, so no sweep. **Budget dropped the wave from 3 to 2 between the split and the dispatch**, so `umbrella/110` (claimed, worktrees made) waits for the second wave; I had ticked three `leg-dispatch` and balanced the third with one `leg-reported`.
**Merged:** `agent/core/153-core-keeps-a-service-store-and-a-development-store` (code `b539f6a`, ff from `9df9976`; doc `269dad6d`, the worker's `ca1b414f` cherry-picked onto `288f488a`). Re-gated on the merge result: `cargo build`, `cargo test` (511 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-345-service-and-development-store.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build (whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `hidapi`'s `build.rs`, as `gate.md` expects); the owner builds natively and runs `run --service` with no store (expect the refusal), then `run --store <dir>`. None of the new code is `cfg(windows)`-gated.
**Budget:** PROCEED at leg start (5-hour 47%, weekly 85%, wave 3); PROCEED at dispatch (5-hour 51%, weekly 86%, wave 2), two dispatched; PROCEED at this fold (5-hour 55%, weekly 86%, wave 2).
**Least sure about:** the reviewer's closest call, not filed: under `--service` the identity store (`topology/enrollment.toml`) moves into a store the elevated install will lock to Core's account, and decision 129 does not say how the unprivileged `embarch-topology` CLI then reaches it (decision 53 and topology decision 23 relied on the parent's default ACL). It is opt-in and 129 marks the install ACL assumed, but the attested phase's install unit has to answer it. Also below the bar: code comments and one test name cite "decision 134" where the doc decision is 129, and `decisions/signing.md`/`run-log.md` still say the key and logs sit beside the token files, now true only in the legacy layout.

---

## 2026-11-25 01:51 — desk/045 the-reference-index-holds-linear-documents

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). The desk's reference index (`GET /refs`) now carries `documents: [{id, title, url, project_id, project_name, updated_ms}]`, the documents of the projects `desk/044` indexes, newest 500 by update, trashed ones left out, titles and links only (no content requested on either path). Read after the projects, from their ids: GraphQL `linear::scope_documents` and the Linear MCP server's `list_documents` once per project (`linear_mcp::scope_documents`); a failed project fetch skips the document fetch and keeps the held rows. `Store::apply` treats documents as projects (failed fetch keeps rows for the same scope, changed scope drops them, a retitle moves `synced_ms`); `RefIndex.documents` is `serde(default)`. Decision 56 amended in place with a dated `(EMB-407)` clause; `interfaces/chat-routes.md` says it. **Assumed, not measured** (decision 56 and the task file say so): the GraphQL `documents(filter: {project: {id: {in: …}}}, orderBy: updatedAt)` spelling and `Document`'s `trashed`/`updatedAt`/`project` fields, and the MCP reply's `documents` key and row spelling; no test drives either fetch over the network. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`). Linear still rate-limited: `ready --brief` died on a per-issue GET; `finish` (exit 1: EMB-334, EMB-312, EMB-136 open; EMB-404 no longer listed) and single `show` calls got through. Split EMB-407 at `009d3d63`, `filed` reached it (Fleet Working), announced ts `1795596282.820579`. **Not taken in burndown, and why, so the next leg need not re-read them:** EMB-408 asks for a new chat decision ("the linker takes references of any kind"), EMB-410 to EMB-415 build on it; EMB-323, 326, 338, 352, 362 need new decisions; EMB-295, 302, 303, 305, 306, 307, 314, 358 are suite passes needing a shared home chosen (EMB-295 and 302 read). **EMB-387 and EMB-388 are not "toolchain hands" as earlier legs wrote:** `tasks/README.md` makes a dev-bench build worker work since 2026-11-17, but their Done-when builds both shields from the main checkout's `embarch-dev-bench/workspaces/pd-bench`, and that workspace was never `west init`ed (manifest and app link only: no `.west`, no `zephyr`, no `modules`). One `west init -l manifest && west update && west patch apply` there, by the owner, makes both ordinary `verify-only` worker tasks. **Refill gate** fired on depth and spread; the only source commit since the 2026-11-24 02:36 sweep not already judged is `atlas/109`'s `design.md` paragraph describing landed work, so no sweep. **After this fold the queue holds nothing burndown may take, so I end burndown** (`fleet-burndown.py --clear --reason 'queue empty'`): the latch reverts to normal mode, where the 90% gate decides, and where EMB-408's decision is a leg's to make.
**Merged:** `agent/desk/045-the-reference-index-holds-linear-documents` (code `20fa59c`, ff from `2afbcbe`; doc `88c5ef48`, the worker's `15f5da00` cherry-picked onto `97b76588`). Re-gated on the merge result: `cargo build`, `cargo test` (317 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 44%, weekly 85%, wave 6), one dispatched; PROCEED at this fold (5-hour 46%, weekly 85%).
**Least sure about:** ending burndown with weekly at 85% and four hours to the reset: the rule says an empty queue ends it, and nothing left is burndown-legal, but it also hands the next leg a normal-mode gate that may take EMB-408's new decision unattended.

---

## 2026-11-25 01:38 — suite/061 compact-studies-guide

**Decided:** nothing suite-wide beyond the announced move, and **no new decision** (burndown leg). The announcement (ts `1795593942.722269`, 01:05) had no reply when its window closed at 01:35, so I ran it as this leg's last unit. `suite/studies-guide.md` §4, the outpost trace walkthrough, moved into a new `suite/trace-guide.md` (5,843 B, under the 10 KB `suite/*.md` cap); the studies guide went 25,636 to 20,314 B, out of reserve, and the size ledger is now empty. The moved text is byte-identical but for one line: "(§3)" became "([studies guide](studies-guide.md) §3)", since the new file has no §3. §4 keeps its heading with a one-line pointer, so the section numbers and anchors other docs use still land. Repointed: the studies guide's §1 and §3 ("§4 step 1"), `suite/user-guide.md` (two lines), `notes/hil/04-premade-suites.md`, and `embarch.md`'s index row, which now reads "Studies, the dev bench, and [DUT traces](suite/trace-guide.md)" rather than a row of its own. **`embarch.md` is 23,027 B, 13 B short of its reserve** (a separate index row put it in reserve, so I folded the link into the existing row): the next edit to `embarch.md` spends the reserve and owes a compaction debt. The Must-not-delete items (§5's unmeasured list and the nRF52840 DK line, §3's 460800 ceiling note) are untouched. **For the next leg:** the task queue holds nothing a worker can take (two bench tasks, which burndown bars, and hardware-gated or parked ones), so its work is Fleet Ready: EMB-407 (desk, Linear documents in the reference index, which reads `desk/044`'s projects), EMB-408 (chat, the linker's kinds block) and EMB-410 to EMB-415 (chat, one linker kind each, probably waiting on EMB-408 and the read surfaces this leg landed); I read their fields with `show` and not their blockers. `ready --brief` cannot finish while Linear is rate-limited, but `show <KEY>` and `filed` get through on a retry. EMB-404 is still in Fleet Working, because `finish`'s status move hit the limit after it had moved EMB-405 and EMB-406 to Done; the next `finish` moves it. Two filings are still spooled at Linear's active-issue cap (`atlas/107`'s anchor finding and a throwaway); `leg-end`'s archive should free room.
**Merged:** no worker branch; my own commit, doc `3d291eed` on `47609410`, landed in this fold's push. Gate on the result: `check-docs.py` 12/12; `check-doc-size.py --pressure` lists no file in reserve.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (BURNDOWN, 5-hour 32%, weekly 84%, wave 6); PROCEED at this fold (5-hour 42%, weekly 85%).
**Least sure about:** keeping the studies guide's H1 ("studies, the dev bench, and DUT traces") unchanged: a reader who opens it for traces lands on the §4 pointer, which works, but the title now promises a section that is one click away.

---

## 2026-11-25 01:35 — desk/044 the-reference-index-holds-linear-projects

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). The desk's reference index (`GET /refs`) now carries `projects: [{id, name, state, url, team_keys}]`: a team-bound desk the team's newest 200 by update (archived in, trashed out), a project-bound desk its one project, read on both connector paths (GraphQL `scope_projects` in `linear.rs`, the Linear MCP server's `list_projects` in `linear_mcp.rs`). `RefIndex.projects` is `serde(default)`, so an older `refs.json` loads and answers `[]`; a failed project fetch keeps its rows while the scope is unchanged; a changed list moves `synced_ms`. Decision 56 amended in place with a dated `(EMB-406)` clause, the earlier text standing (decision 79's style); `interfaces/chat-routes.md` says it. **Assumed, not measured:** the MCP argument and row shapes and the GraphQL project queries were never run against live Linear (tests use fakes; decision 56 says "assumed"). **The worker's call, which the reviewer judged consistent with 56:** the index now counts as failed only when issues, projects and PRs all fail; the edge is a first refresh where issues fail and projects succeed, which records a sync with empty issues. `documents` (also in §15.3) is EMB-407's, still unsplit in Fleet Ready. **Linear:** `filed` for EMB-406 failed twice on the rate limit and reached it on the third try, just before this fold, so all three issues of this leg are in Fleet Working and `finish` after these pushes moves them to Done once Linear answers. **To carry:** a `filed` that never reaches Linear leaves its issue in Fleet Ready, and once the fold retires the task nothing on `main` names it, so a later `ready` would offer it for a second split; `finish` only reads Fleet Working.
**Merged:** `agent/desk/044-the-reference-index-holds-linear-projects` (code `2afbcbe`, ff; doc `f2fde423`, the worker's `e888d977` cherry-picked onto `ae4f54a4`). Re-gated on the merge result: `cargo build`, `cargo test` (314 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 35%, weekly 84%, wave 6); PROCEED at this fold (5-hour 40%, weekly 84%).
**Least sure about:** the two connector paths' project shapes, which no test can confirm without live Linear; a wrong field name there yields an empty `projects` list, not an error.

---

## 2026-11-25 01:34 — api/192 a-list-studies-verb

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-api [--json] list-studies [--limit N]` lists Core's retained studies newest first by `started_utc_ms` (no start time after, by id), each tap with Core's tagged `encoding` and a flat `encoding_kind`, in Promptu contract §15.3's shape; no lease, `error_result` errors, CLI only (`Asymmetry::CliOnly` beside `verify`, `guide` and others, and a test says no `list_studies` tool exists). Recorded in `interfaces/studies.md`, `interfaces/tools.md` and spec §1; no decision file grew. **A contract gap for Promptu, not filed (Linear is at its active-issue cap and rate-limited):** study-designer's `StreamEncoding` has a `Struct { decoder }` variant, and §15.3's `encoding_kind` list (`raw`, `text`, `samples`, `gatt_transcript`, `outpost_trace`) lacks it; the worker emits `struct` and `interfaces/studies.md` lists it, the reviewer judged it additive. `embarch-promptu/docs/contract.md` §15.3 should add `struct`; worth a line in the chat linker's captures unit (EMB-415). Core's `taps: []` stays `[]`; `null` only where Core could not read them. **Linear:** a retry of `filed` reached EMB-405 (Fleet Working). Its first attempt failed at the status move, after the comment step, so EMB-405 may carry the filed comment twice. **Landing order, a slip of mine:** I cherry-picked all three doc branches into the leg worktree before the first fold, so `atlas/109`'s push put this unit's and `desk/044`'s doc commits on `origin/main` about three minutes before their folds; nothing else read `main` in between.
**Merged:** `agent/api/192-a-list-studies-verb` (code `cd1f428`, ff from `a3d0831`; doc `ae4f54a4`, the worker's `f9129c46` cherry-picked onto `28311ead`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-192-list-studies.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 35%, weekly 84%, wave 6); PROCEED at this fold (5-hour 40%, weekly 84%).
**Least sure about:** the verb was only run against a mock Core; a real Core's `GET /studies` with a `Samples` tap is untested here.

---

## 2026-11-25 01:33 — atlas/109 a-refs-verb-lists-sections-symbols-and-nodes

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-atlas refs [--json] [--atlas-dir D] [--atlas <id>]` (new `src/embarch_atlas/refs.py`, listed in `cli.py`) prints every translated document's sections, and the current atlas's Kconfig symbols and devicetree nodes, in Promptu contract §15.3's `atlas_refs: 1` shape; read-only, no `usage.jsonl` row, CLI only (so the "twenty-three lookups" count stays true). **The worker's calls where §15.3 is silent, which I keep and the reviewer called refinements:** `commit` is the atlas's own commit, not HEAD; a symbol `name` is bare (the linker adds `CONFIG_`); node `aliases` exclude chosen names; a TOC row with no id is skipped; outside a git repo with no `--atlas-dir` it answers "no atlas", exit 0. Timed at 2 ms in-process on the fixture, about 0.55 s as a CLI; not measured on a real atlas (none on this machine), and `DESIGN.md` says so. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no `status.d`). **Linear stayed rate-limited** (2,500/hour): `ready --brief` died partway through its per-issue GETs both times, but single `show` calls and a second `finish` (exit 1, EMB-334, EMB-312, EMB-136 still open) got through, so I read EMB-403 (Done) and EMB-404 to EMB-415 one at a time. **Split at `08b3ca7a`:** EMB-404 to this task, EMB-405 to `api/192`, EMB-406 to `desk/044`; announced ts `1795594763.490889`. `filed` reached EMB-404 only (Fleet Working); EMB-405 and EMB-406 hit the limit, and the `api/192` and `desk/044` entries say whether a retry reached them. **Still in Fleet Ready from the same plan, unsplit:** EMB-407 (desk, documents in the index; reads this leg's projects), EMB-408 (chat change, the linker's kinds block) and EMB-410 to EMB-415 (chat, one linker kind each); I did not read their blockers. The refill gate fired on depth and spread; the only source commits since the 2026-11-24 02:36 sweep are the verbatim moves and `promptu/024`'s bullets the last two legs judged, so no sweep. **My error, small:** I told all three workers the `embarch-promptu` main checkout was current; it is one commit behind (§15 is only on `origin/main`), and each worker read §15.3 from `origin/main` instead.
**Merged:** `agent/atlas/109-a-refs-verb-lists-sections-symbols-and-nodes` (code `b4c3c75`, ff from `d0b5ca5`; doc `28311ead`, the worker's `309356a3` cherry-picked onto `bf5d945c`). Re-gated on the merge result: `.venv/bin/pytest -q` 1058 passed, 3 skipped (all three `EMBARCH_ATLAS_REAL_*`; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row (no atlas scope in `features.d/README.md`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 32 to 35%, weekly 84%, wave 6), three dispatched in one wave; PROCEED at this fold (5-hour 40%, weekly 84%).
**Least sure about:** the bare symbol `name`: §15.2 lists `CONFIG_<NAME>` as the written form, so the chat linker must prepend it, and nothing yet tests that the two halves agree.

---

## 2026-11-25 01:12 — promptu/025 compact-promptu

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Unparked early for the verbatim move its task names, as the `promptu/024` entry suggested and `desk/038`'s entry explains. Eight step 1 to 3 bullets (block mode not on, forks F5 to F10, block mode off and relabelling, the unseen shell write, step 2's review rounds, where a memory is used, step 3's install wait, the rewrite's model and wait) moved byte-identical into the new `embarch-promptu/open/steps-1-3.md`; `open.md` 4,060 to 1,946 B, out of reserve, with one pointer line. The step 4 and 5 bullets, the unmeasured-claims link, the weekly-sheet bullet and the no-feature-row bullet stay untouched. **Linear, to carry:** besides the hourly rate cap, the workspace is at Linear's free-plan cap on active issues (`USAGE_LIMIT_EXCEEDED`, `activeIssueCount`), so two filings this leg spooled in `.fleet/linear-spool/`: the `check-links.py` inline-code anchor bug (`--from audit`, Scope fleet; `atlas/107`'s entry) and a throwaway job (checking a doc split moved its text verbatim). `ready` files the spool once Linear answers; `leg-end` archives Done and Canceled issues untouched for 7 days, which is what frees the cap.
**Merged:** `agent/promptu/025-compact-promptu` (doc `c18a2754`, the worker's `f54c6c73` cherry-picked onto `f2538f73`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6); PROCEED at this fold (5-hour 31%, weekly 84%).
**Least sure about:** the next leg's first move: with Linear rate-limited and at its issue cap, it may again read no Fleet Ready issue, and with every size debt now paid but `suite/061` the task queue holds nothing a worker can take, so it may end on an empty queue while Fleet Ready holds work.

---

## 2026-11-25 01:11 — umbrella/107 compact-umbrella

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says. The whole "Command surface" section (the seven-row command table and the exit-codes line) moved from `embarch-umbrella/spec.md` into the new `embarch-umbrella/spec/commands.md`, beside `marketplace.md`; `spec.md` 9,272 to 6,329 B, out of reserve, with the heading and a pointer left in place. Decision numbers 12, 21, 26, 41, 46, 58, 59, 60 and EMB-192 kept. Only three relative link prefixes changed (one level deeper). No `decisions/` file touched; several still sit within 200 B of their limit (`prune-policy`, `deploy`, `mirrors`, `budgets`), and the next umbrella decision lands on one of those.
**Merged:** `agent/umbrella/107-compact-umbrella` (doc `f2538f73`, the worker's `a1c44420` cherry-picked onto `6a54b70b`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6); PROCEED at this fold (5-hour 31%, weekly 84%).
**Least sure about:** whether the command table was the right section to move: it is what a reader of the umbrella reaches for first, and it now sits one click away.

---

## 2026-11-25 01:11 — atlas/107 compact-atlas

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says. Two sections moved byte-identical from `embarch-atlas/design.md` into the new `embarch-atlas/design/library-and-cad.md`: "A shared datasheet library, and a copy of every file an atlas read" and "Reading an Altium project's sources: `cad`". `design.md` 23,474 to 19,214 B, out of reserve; each heading stays with a one-line pointer. The worker avoided "Protocol records" because `notes/hil/04-premade-suites.md` links its anchor, and left the measured-plane sections alone. **Finding, for the owner's `scripts/`:** `check-links.py`'s `anchors_of()` slugs headings from `strip_code(body)`, which drops inline code spans, so a heading like "sources: `cad`" is recorded as `#...-sources` where GitHub renders `#...-sources-cad`. The gate therefore requires the pointer this unit wrote (`#reading-an-altium-projects-sources`), which will not jump to the section on GitHub; I tried the GitHub form and the gate refused it, so I left the worker's. Any link to a heading with inline code has the same mismatch.
**Merged:** `agent/atlas/107-compact-atlas` (doc `6a54b70b`, the worker's `0fc7b04d` cherry-picked onto `99057054`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6); PROCEED at this fold.
**Least sure about:** that the anchor mismatch is worth a fix: it only costs a jump-to-section, and every heading with inline code in the suite has it.

---

## 2026-11-25 01:10 — desk/038 compact-desk

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). **I unparked four size debts early, for the verbatim moves their own tasks name:** `desk/038`, `atlas/107`, `umbrella/107` and `promptu/025` were `blocked` on `In flux: yes`, none overdue (due 2026-12-01 to 12-09). Each task's What is a verbatim move, and `DOC-BUDGET.md`'s split-first rule says flux cannot forbid one, so at claim I rewrote each `In flux:` to "no — for the move this task makes", keeping the old answer as history (`core/093`'s form, 2026-09-28), with a dispatch note saying move only, squeeze nothing. **`suite/061` (the studies guide, 25,636 of 25,600 B on the ledger allowance) is unparked the same way and announced, ts `1795593942.722269` at 01:05**: it is `open`, the window closes 01:35, and a later leg runs it as its last unit if no objection is in that thread (move §4 verbatim into its own guide). This unit: §1's desks and knowledge paragraphs and §3's body moved into `embarch-desk/spec/desks-knowledge-interfaces.md`; `spec.md` 9,225 to 7,795 B, out of reserve; §2's invariants stay. Only relative link prefixes changed; I checked every removed line against the new file. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker). **Linear is rate-limited all leg** (2,500/hour cap): `ready --brief`, `list` and `queue-status.py`'s Fleet Ready read all exit 2 from 01:00, failing on a per-issue GET partway through. `ready` and `list` fetch every open issue one request at a time, so one read costs about one request per open issue. No Fleet Ready issue was read or split this leg; EMB-404 to EMB-406 should now be unblocked by EMB-403's landing, unverified. `finish` ran (exit 1: EMB-334, EMB-312 and EMB-136 still have tasks open). The refill gate fired on depth (0 dispatchable tasks); since the 2026-11-24 02:36 sweep the only source commits are `promptu/024`'s `open.md` bullet (paid here by `promptu/025`), `embarch-dev-bench/open/analog.md` (every item a bench run) and `ui/115`'s already-judged line, so I filed nothing and did not re-read the rest. **Log defect, not touched:** the `## 2026-11-24 — 43 units` heading, its note, carry-forward and splits paragraph appear twice in a row in this file; the day's `###` entries follow the second copy only.
**Merged:** `agent/desk/038-compact-desk` (doc `0ce75348` and `99057054`, the worker's `8bf257a8` and `7656f71a` cherry-picked onto `005334ad`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6), four dispatched in one wave; PROCEED at this fold (5-hour 31%, weekly 84%).
**Least sure about:** the early unpark: the filers chose "rides in the next unit that writes the file", and I read the split-first rule as overriding that for a verbatim move; `core/093` did the same only once its debt was overdue.

---

## 2026-11-25 00:56 — atlas/108 the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-atlas/src/embarch_atlas/livelog.py` no longer keeps `UNGATED`: `note()` writes no line when the api's `--json` answer carries no gated `core_calls` (absent, empty, null or study-only), which the reviewer traced to the api's own trace filter (`lease_gate::is_gated` in `client.rs`, `core_calls` added in `cli.rs` only when non-empty), so the five old verbs behave exactly as before. The path walk is split out as a pure `repo_above(here)`. `tests/test_livelog.py` gains a lease-free-verb test (the five old verbs and an invented one) and a test parametrised over `../embarch-api/tests/fixtures/live-log/*.json` (`api/191`'s 19 cases), comparing the path and the line minus `t`, `writer`, `via`, `sent` and the atlas's own `outcome`; a companion test asserts at least 19 cases when the sibling is there and skips with its reason when it is not. The code repo's `DESIGN.md` gains one paragraph; `embarch-doc/embarch-atlas/design.md` never named `UNGATED`, so it is untouched and still in reserve (2,126 B, `atlas/107` parked). **Coverage the worker disclosed and the reviewer judged a gap, not a contradiction:** the atlas has no configured-project list, so the three `source_path`-fallback cases only assert that the walk finds no `embarch/`; and the board-order cases are replayed as `--role`/`--probe-serial`/`--chip` flags in entry order, a stand-in for how the atlas learns a board. **Worktree link, new for this unit:** I linked `embarch-api` (the main checkout, which I pulled to `c254d15`) beside the atlas worktree; `.claude/leg.md`'s table lists only `.atlas-local` for `embarch-atlas`, and any atlas unit after this one needs both. EMB-319's last task: `finish` after this push should move it to Done.
**Merged:** `agent/atlas/108-the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture` (code `d0b5ca5`, ff from `74048d8`; doc `347a28f4`, the worker's `31792f90` cherry-picked onto `0d7e8a3c`). Re-gated on the merge result: `.venv/bin/pytest -q` 1052 passed, 3 skipped (all three on `EMBARCH_ATLAS_REAL_*`, none of this unit's; `test_public_guard` and the fixture tests ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 22%, weekly 83%, wave 6); PROCEED at this fold.
**Least sure about:** the fixture test needs a sibling `embarch-api` checkout that carries the fixture; the atlas's own CI has none, so there it skips and reads green, and only the fleet's gate (with the link above) or a full suite checkout runs it.

---

## 2026-11-25 00:54 — api/190 hil-guide-words-point-at-the-glossary

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). The HIL guide's Words entry for Study now reads "**Study** (the mode; **a study** is its file): a custom question answered by measurement on one bench, run by `run_study` or `run_host_study`. EmbArch's glossary row **Study** is the definition." Bench, Test, Run, Measurement and Verdict keep their gloss in place, since the glossary has no row for them (`doc/102` added Study only). **How it landed:** the worker edited the api's pinned copy (`guide/hil-guide.md`) and quoted the bytes in `status.d`; I applied them to `suite/hil-guide.md` in this fold (22,829 B), as `api/189`. The drift guard (`tests/guide_cli.rs`) ran green with `EMBARCH_DOC_DIR` at my leg worktree carrying the edit; between the code push and this fold, `main`'s suite copy differed from the api's pinned copy for about four minutes. **Reviewer's note, below its bar, not filed:** the bullet no longer says `run_study` runs on the dev bench and `run_host_study` on Core's runner; the guide's own Study section still does. EMB-317's last task: `finish` after this push should move it to Done.
**Merged:** `agent/api/190-hil-guide-words-point-at-the-glossary` (code `a3d0831`, ff from `c254d15`; doc `0d7e8a3c`, the worker's `b1e151df` cherry-picked onto `fcadb4c0`); the suite guide edit is in this fold commit. Re-gated on the merge result: `cargo build`, `cargo test` (no failures; `guide_cli` 4 passed against the edited guide), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 22%, weekly 83%, wave 6), two dispatched; PROCEED at this fold.
**Least sure about:** "EmbArch's glossary row **Study** is the definition" points a binary-only reader at a doc they may not have; the gloss in front of it carries the meaning, but the pointer is only useful with a repo at hand.

---

## 2026-11-25 00:39 — promptu/024 the-contract-fixes-build-step-5s-shapes-and-forks

**Decided:** nothing suite-wide, and **no new decision** (burndown leg; the issue itself says the forks hold the choices). `embarch-promptu/docs/contract.md` gains §15 "The linker's kinds (build step 5)": §15.1 the reference entry (`kind`, `key`, `words`, `names`, `line`, `text(find)`, scored within a kind, then merged), §15.2 the `<references>` block (12 lines, 3,600 characters, 4 per kind) and one table of the twelve kinds (source, refresh, cue words, written form), §15.3 the JSON of `embarch-atlas refs`, `embarch-api --json list-studies` and the desk's `GET /refs` `projects`/`documents`, each carrying its own marker rather than `"promptu": 1`. §11 gains "From step 5" and §0 names step 5 (no model call). `docs/forks.md` gains L1 to L22, the riskiest five first (L11 cue-word gate, L5 Core through the api CLI, L3 the atlas verb, L10 block size, L2 contract first); **L1, L18, L19 and L21 say the plan's choice is unrecorded and the owner's to state** (my Question on EMB-403 asks for them). Promptu's `spec.md`, `spec/status.md`, `interfaces.md` say step 5 is under way and point at §15; `open.md` names the four unrecorded choices. **The worker's calls, which I keep:** instruments, captures, traces and worktrees are gated too, as their issues say, wider than the task's "high-volume" list; the numeric limits (300 branches, 200 projects, 500 documents, 60 s, 5 min, 20 studies) are marked assumed in the forks. **New debt, filed by the worker:** `tasks/promptu/025-compact-promptu.md`, `blocked`, due 2026-12-09: `embarch-promptu/open.md` 4,060 of 5,120 B; `In flux: yes`. Its own What is a verbatim move of settled step 1 to 3 bullets into `open/`, which flux does not forbid, so the next leg may unpark it. **Reviewer's note, below its bar, not filed:** §15.2 and L14 say "only decision 16's atlas citations become links", which read literally omits decision 88's issue/PR prose links; the same section says issues and PRs follow 88, so it reads as scoped to the new kinds. L10 cites "2,400" for decision 88's block, a figure not in 88's text. This landing is what EMB-404 to EMB-406 wait on in Linear: `finish` after this push should move EMB-403 to Done and let the next `ready` split the atlas, api and desk read surfaces.
**Merged:** `agent/promptu/024-the-contract-fixes-build-step-5s-shapes-and-forks` (code `6d091a1`, ff from `dcb6588`, docs only; doc `076da6d2`, the worker's `15a24261` cherry-picked onto `0bf5cb47`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I read the contract diff before merging. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 0%, weekly 80%, wave 6); PROCEED at this fold (5-hour 21%).
**Least sure about:** whether the four missing choices change §15 itself: I told the owner they do not, but choice 1 could be the step's scope (which kinds exist at all), and if so the kinds table is built on an assumption no issue states.

---

## 2026-11-25 00:37 — api/191 a-shared-fixture-pins-the-live-log-rules

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-api/tests/fixtures/live-log/` holds 19 plain-JSON cases pinning the five rules both live-log writers share (the 4096-byte answer cap with 2- and 4-byte characters at the cut, the board order body then arguments then answer, `repeat`/409/headerless `core` entries, the path walk with the `source_path` fallback and the git-root stop, and the `<date>-<session>` name with a `+02:00` start left unconverted and the no-lease case). `src/live_log.rs` gains a pure `build_line(call, live, lease, status, now)` and `repo_above`/`repo_dir_from`; `record()` calls them with the real lease, status and clock, so behaviour is unchanged (the reviewer checked). A unit test runs every case and compares the path and the line minus `t`, `writer`, `via` and `sent`. `interfaces/live-log.md` gains "The shared fixture": the case format key by key, the compared fields, the sibling path a second writer reads, and that a rule change lands in the fixture first. **My split of EMB-319:** this task, then `atlas/108` (delete `UNGATED`, a pytest reading these cases from `../embarch-api/`), unparked to `open` in this fold. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no unfolded `status.d`). The owner re-armed burndown at 00:01 (weekly 80%, until 2026-11-25 06:00). `finish` moved EMB-308 and EMB-304 to Done, so the Linear cap the last legs hit is clear. Fleet Ready held 18 unsplit issues and 45 waiting; I split two at `39be7664`: EMB-403 to `promptu/024`, EMB-319 to this task and `atlas/108`; announced ts `1795590679.186489`. **EMB-403, which the last legs did not take:** the plan it cites is in no repo, but EMB-404 to EMB-415 state its choices 2 to 17, 20 and 22; choices 1, 18, 19 and 21 are stated nowhere, so the forks for them say so and I asked the owner on EMB-403 (a Question comment). **Not taken in burndown, as the last legs judged:** EMB-323, 326, 338, 352, 362 (new decisions), EMB-358 and the audit's cross-repo changes EMB-295, 302, 303, 305, 306, 307, 314 (suite passes), EMB-387 and 388 (toolchain hands). The refill gate fired on depth (1 dispatchable); the only sources changed since the 2026-11-24 02:36 sweep are `embarch-dev-bench/open/analog.md` (new, every item a bench run) and `ui/115`'s already-judged line, so no sweep. **Day fold:** an `embarch-log-folder` folded 2026-11-24 (43 units, 117.9 KB to 40.7 KB, `--apply` confirmed 186 SHAs, 43 reviewer lines, 4 debt lines), and `--roll` moved 2026-11-22 to `log-archive/`; both ride in this fold. `check-client-names.py --suite --history`: all 16 repos clean. Wave 1 was this and `promptu/024`, two foreground workers in one message with the log folder, all reported to the leg; reviewers ran foreground after the merges.
**Merged:** `agent/api/191-a-shared-fixture-pins-the-live-log-rules` (code `c254d15`, ff from `d755007`; doc `0bf5cb47`, the worker's `50b9ec81` cherry-picked onto `aed2c46d`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures, the new `every_shared_fixture_case_comes_out_as_pinned` among them), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 0%, weekly 80%, wave 6), two dispatched; PROCEED at this fold.
**Least sure about:** the fixture's expected values were generated by the worker in Python and checked against the Rust once, with no mutation run, so a case that pins a wrong value would pass both writers equally; the atlas half is where a disagreement would first show.

---

## 2026-11-24 — 43 units

*Folded by leg 010 successor on 2026-11-25 (embarch-log-folder): per-unit narrative reasoning, gate transcripts and budget lines dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, debt and the spread sweep line kept.*

**Carry forward.** Burndown ran 00:06 to 02:36 and ended on an empty queue (pump stays latched in normal mode); a second burndown leg 03:05 onward ran to the 14:28 fold with the usage cache stopped at 14:00. Open at day end: a **second listener session is live** and spawns a leg per leg death, each waiting on the leg lock (doubles Linear reads); **Linear's 2,500/hour cap** is hit repeatedly, so `filed`/`finish` for EMB-320, EMB-312, EMB-308, EMB-402 and the EMB-317 move may not have reached Linear (next `ready` reports ALREADY SPLIT; re-run `filed`/`finish`); 25+ Fleet Ready issues unsplit; EMB-403 not taken (cites a plan found in no repo); `suite/058` parked to 2026-12-01 (announce first); `api/188` parked on the owner supplying the et54 load's input-off command. Owner questions: replay cost cap (W24), EMB-398 token scope, EMB-399/EMB-400 findings. Owed: `notes/goals/03-status.md` goal 3 still says topology alone opens a probe or port. Safe-off re-declare: `PUT /instruments` replaces by name. Dream ts `1795512985.272199` (previous dream ts `1795476373.403649`, 10 h and 133 commits earlier).

**Splits this day (Linear to task file; commit, announcement ts):** EMB-278 to `promptu/021` (`bd163fc8`, `1795503287.195659`); EMB-283/284 to `desk/043`+`ui/113` and `chat/035` (`248e2321`, `1795505033.011589`); EMB-318 to `doc/100`, EMB-297 to `api/186`+`core/149`+`umbrella/104` (`245c7cbf`, `1795515529.865329`); EMB-310/320/312 at `afe9024f` (`1795518116.601709`); EMB-321 to `topology/072`, EMB-299 to `umbrella/106`, EMB-386 to `ui/116`, EMB-357 (`f9bb180f`, `1795535418.541089`); EMB-401/400/399/389 (`3711fb0d`, `1795541360.131669`; the unit-`study-designer/091` split `2ff73f95` above is a separate commit); EMB-343 to `umbrella/108`, EMB-322 and others (`cd0b1fe8`); EMB-402/308/344 (`4a4a7f87`, `1795549699.487149`; `suite/060` window ts `1795543398.128079`, follow-up announcement `1795543453.347959`); `c06ce2be` as above. Owner's `ed5d290a` (the HIL guide's Live section) reached `origin/main` during `api/189`.

Spread sweep: nothing filed (2026-11-24 00:23)

## 2026-11-24 — 43 units

*Folded by leg 010 successor on 2026-11-25 (embarch-log-folder): per-unit narrative reasoning, gate transcripts and budget lines dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, debt and the spread sweep line kept.*

**Carry forward.** Burndown ran 00:06 to 02:36 and ended on an empty queue (pump stays latched in normal mode); a second burndown leg 03:05 onward ran to the 14:28 fold with the usage cache stopped at 14:00. Open at day end: a **second listener session is live** and spawns a leg per leg death, each waiting on the leg lock (doubles Linear reads); **Linear's 2,500/hour cap** is hit repeatedly, so `filed`/`finish` for EMB-320, EMB-312, EMB-308, EMB-402 and the EMB-317 move may not have reached Linear (next `ready` reports ALREADY SPLIT; re-run `filed`/`finish`); 25+ Fleet Ready issues unsplit; EMB-403 not taken (cites a plan found in no repo); `suite/058` parked to 2026-12-01 (announce first); `api/188` parked on the owner supplying the et54 load's input-off command. Owner questions: replay cost cap (W24), EMB-398 token scope, EMB-399/EMB-400 findings. Owed: `notes/goals/03-status.md` goal 3 still says topology alone opens a probe or port. Safe-off re-declare: `PUT /instruments` replaces by name. Dream ts `1795512985.272199` (previous dream ts `1795476373.403649`, 10 h and 133 commits earlier).

**Splits this day (Linear to task file; commit, announcement ts):** EMB-278 to `promptu/021` (`bd163fc8`, `1795503287.195659`); EMB-283/284 to `desk/043`+`ui/113` and `chat/035` (`248e2321`, `1795505033.011589`); EMB-318 to `doc/100`, EMB-297 to `api/186`+`core/149`+`umbrella/104` (`245c7cbf`, `1795515529.865329`); EMB-310/320/312 at `afe9024f` (`1795518116.601709`); EMB-321 to `topology/072`, EMB-299 to `umbrella/106`, EMB-386 to `ui/116`, EMB-357 (`f9bb180f`, `1795535418.541089`); EMB-401/400/399/389 (`3711fb0d`, `1795541360.131669`; the unit-`study-designer/091` split `2ff73f95` above is a separate commit); EMB-343 to `umbrella/108`, EMB-322 and others (`cd0b1fe8`); EMB-402/308/344 (`4a4a7f87`, `1795549699.487149`; `suite/060` window ts `1795543398.128079`, follow-up announcement `1795543453.347959`); `c06ce2be` as above. Owner's `ed5d290a` (the HIL guide's Live section) reached `origin/main` during `api/189`.

Spread sweep: nothing filed (2026-11-24 00:23)

### 2026-11-24 14:28 — doc/102 glossary-rows-for-the-guides-terms

Glossary Study row now names the host runner; eleven link-only rows point at the doc owning each guide term; studies-guide §1 points at the Study row. Worker had no write access to either file, so its quoted edit set was applied verbatim at fold. Gaps flagged, not filed: publish has no single owning decision; saved/live bench have no one-sentence definition (saved-benches.md has no `### 44` heading). Glossary is 1 B under its reserve line. `api/190` unparked to `open`.
**Merged:** `agent/doc/102-glossary-rows-for-the-guides-terms` (doc `991de560`, the worker's `325fcfef` cherry-picked onto `ff4913f6`; no code repo); the glossary and guide edits are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 14:25 — chat/037 atlas-citations-link-in-a-worktree-chat

`atlasRoot` walks up to the first `embarch/atlas`, and from a worktree falls back to the main clone's atlas via `gitdir:`/`commondir`; chat decision 16 amended. Split this leg: EMB-409 to this task, EMB-317 to `doc/102` + `api/190` (`c06ce2be`, ts `1795553476.798679`); EMB-317's Linear move hit the cap (next `ready` reads it as already split). EMB-403 not taken: it cites a build-step-5 plan (choices 1-22, units P5.x) found in no repo; owner's `f1208495` may carry it, unread. Three chat tests failed once under load in the worker's run and passed on rerun; nobody ran the `main` baseline.
**Merged:** `agent/chat/037-atlas-citations-link-in-a-worktree-chat` (code `695f46d`, ff from `23492eb`; doc `ff4913f6`, the worker's `af1dbb34` cherry-picked and rebased onto the owner's `45be94e0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:32 — ui/119 the-study-tab-uses-the-shared-tap-check

Study tab's no-subscriber tap refusal now comes from `Study::validate_stream_subscriptions()` via a scratch `Study` in `build_taps`; the refusal runs after the whole tap loop. gatt-capture decision 15 reworded. EMB-308 fully landed (`study-designer/093`, `core/152`, this) but stays in Fleet Working until a `finish` reaches Linear. Risk: the scratch `Study` literal breaks on the next field `Study` gains.
**Merged:** `agent/ui/119-the-study-tab-uses-the-shared-tap-check` (code `2213de6`, ff from `3974192`; doc `db2c1a56`, the worker's `b6e9366a` cherry-picked onto `69a7b6bf`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:31 — core/152 core-refuses-a-study-with-a-tap-no-step-subscribes-to

Core's `validate_study` refuses a GATT notify tap no step subscribes to, with the crate's text (core decision 90); `run_study` gets it through `POST /study`; interface row added. Fix at landing: comments cited the task number as 'study-designer decision 93', it is decision 55 (core `9154f7d`). **Leg start, to carry:** this leg waited 35 min for the leg lock because a second listener session was live (one spawning a leg at 12:42, the other at 12:44); the lock serialised them as designed, and the second listener keeps spawning a leg per leg death. Linear was rate limited all leg (2,500/hour cap; `ready`, `finish`, `queue-status.py` exit 2 at 13:20, 13:21, 13:30), so no Fleet Ready issue was split and EMB-308/EMB-402 stay in Fleet Working. Pump latched in burndown until 2026-11-25 06:00; leftover `agent/atlas/097-*` and `agent/ui/059-*` branches are known, not mine.
**Merged:** `agent/core/152-core-refuses-a-study-with-a-tap-no-step-subscribes-to` (code `0d1f027`, ff from `1b3562d`, plus my comment fix `9154f7d`; doc `69a7b6bf`, the worker's `af7098dc` cherry-picked onto `f2ccf405`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none beyond the standing native Windows build of `embarch-core`, which a worktree cannot run.

---

### 2026-11-24 13:19 — suite/060 the-one-owner-hardware-claim-says-what-core-and-topology-each-own

Supervisor's own unit, executed after the `protocol.md` §8 window (announced ts `1795543398.128079`, no reply). `embarch.md` §4 corrected: topology decides which device, Core opens every probe session and serial port, `embarch-smp` opens nothing; §4 gains the six runtime edges the sketch omitted; `embarch-smp` decision 2 amended; §3's smp row corrected. **Owed:** `notes/goals/03-status.md` goal 3 carries the same wrong claim and `fold-commit.py` refuses to stage it, so it still says topology is the only code opening a probe or port. Reviewer spot-checked, not re-audited, the nine port opens.
**Merged:** no branch (supervisor's own unit); the edits are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:13 — umbrella/109 a-script-cuts-a-signed-suite-release

`scripts/cut-release.py <suite-version> [--go] [--root DIR] [--dest DIR]` cuts a signed suite release (dry run by default; tags and pushes each changed component, watches `release.yml`, stops for the owner to commit `suite.toml`; second `--go` tags `suite-v<version>`, watches `assemble-suite.yml`, runs `embarch verify-release`). Never approves the `release` environment. My fix at landing: removed committed `__pycache__` and gitignored it (`ed5645b`). `gh` call shapes unverified until the first real cut; `--root` must name real checkouts from a worktree; tags go on HEAD unchecked. Umbrella `spec.md` at 9,272 B (968 B left). Linear rate limited again at the 13:14 `finish` (EMB-402 landed, still Fleet Working).
**Merged:** `agent/umbrella/109-a-script-cuts-a-signed-suite-release` (code `ed5645b`, the worker's `7bc6759` plus my fix, ff from `43ddda7`; doc `2448e2ca`, the worker's `03d1816a` cherry-picked onto `b67225a6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none, but the script has never met a real `gh` or `git` remote: `gh run list --workflow --branch <tag> --jq`, `gh run watch --exit-status` and `gh release download -D` are written from memory, and the first real cut (the rehearsal release) is where they get checked.

---

### 2026-11-24 13:12 — api/189 the-hil-guide-sends-the-dut-census-to-the-dev-bench-log

HIL guide's Study 1 bullet says to read the DUT census in `dev-bench.log` and that `fail_reason` is capped (measurement in `suite/studies-guide.md` §3a). Worker edited the api's pinned `guide/hil-guide.md`; I applied the same bytes to `suite/hil-guide.md` at fold and the drift guard passed against the leg worktree. A few minutes of drift-guard failure existed between the api push and this fold; any two-copy guide edit has it.
**Merged:** `agent/api/189-the-hil-guide-sends-the-dut-census-to-the-dev-bench-log` (code `7cbcd3d`, ff from `8786605`; doc `b67225a6`, the worker's `2e3762d5` cherry-picked onto `07b5294e`); the suite guide edit is in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:11 — study-designer/093 a-study-refuses-a-stream-tap-no-step-subscribes-to

`Study::validate_stream_subscriptions() -> Result<(), UnsubscribedTapError>` added (own error type, additive); decision 55 amended, decision 89 names the sibling. Only Core's `cargo check` was run against it; UI and api not.
**Merged:** `agent/study-designer/093-a-study-refuses-a-stream-tap-no-step-subscribes-to` (code `42a9d8a`, ff from `7ad0a02`; doc `07b5294e`, the worker's `af600edb` cherry-picked onto `c42cb4c1`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 11:18 — doc/101 one-study-walkthrough-and-the-guides-link-hil-guide

One study walkthrough lives in `suite/hil-guide.md`; `studies-guide.md` §1-§3b defer to it and keep this bench's measurements; `agent-guide.md` and `user-guide.md` §9 point at `embarch-api guide hil`. Installed `embarch-api` predates `guide hil` (needs a build after `api/163`), so the `hil-guide.md` link is the fallback.
**Merged:** `agent/doc/101-one-study-walkthrough-and-the-guides-link-hil-guide` (doc `0cfa89ff`, the worker's `4275bea0` cherry-picked onto `e9c29bc0`; no code repo); the guide edits themselves are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 11:17 — umbrella/108 verify-release-checks-the-certificates-repository-and-ref

`embarch verify-release` requires the leaf certificate's Source Repository URI, Ref and Build Config URI to equal the umbrella repo, `refs/tags/suite-v<version>` and the identity (new `VerifyError::CertificateClaim`). **Risk to carry:** nothing has signed a suite release yet; if the release workflow's build config URI differs from the identity (a reusable workflow, say), every install refuses.
**Merged:** `agent/umbrella/108-verify-release-checks-the-certificates-repository-and-ref` (code `43ddda7`, ff from `6934dae`; doc `e9c29bc0`, the worker's `d45c0f95` cherry-picked onto `96ad575d`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. No signed suite manifest has been verified end to end yet; the check has met the uv and cosign fixtures only.

---

### 2026-11-24 11:16 — topology/073 the-cli-refuses-store-writes-while-a-core-service-is-registered

Topology CLI asks the OS whether a Core service is registered before any store write (`bin/registry.rs`, `ServiceRegistry` seam; `reg query` / `systemctl show` / `sc.exe qc`); enrol, unenrol, set-board, validate, set-dev-bench-link refused when registered, `list`/`alerts` point at Core's routes under `--service`. Decisions 23 and 28 amended. Fail-open: a registry read that errors restores local writes.
**Merged:** `agent/topology/073-the-cli-refuses-store-writes-while-a-core-service-is-registered` (code `81fb9ae`, ff from `77335f2`; doc `96ad575d`, the worker's `4297ff49` cherry-picked onto `df54c0af`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a real registered Core service, stopped and running, on Windows and under WSL2, with a non-default `--bind`; `list` and `alerts` against a `--service` registration; the `ImagePath` and `sc.exe` parsing against real output (sample text only). The Windows build of the whole binary is the known `hidapi` debt; `registry.rs` alone type-checked for `x86_64-pc-windows-msvc` in a scratch crate.

---

### 2026-11-24 10:44 — core/151 the-spec-says-what-core-persists-of-what-it-flashed

Core spec's invariant now says Core keeps a persisted record of what it *flashed*, not of what the chip holds (`flashed-images.jsonl`, decision 93). Compaction paid in-unit: the signing/run-log/publish/restore/measurements text of §2 moved verbatim to new `spec/signing.md`, one pointer line keeps citations. Signing surface is still moving (EMB-254, EMB-265).
**Merged:** `agent/core/151-the-spec-says-what-core-persists-of-what-it-flashed` (code none; doc `d8532a55`, the worker's `583e018c` cherry-picked onto `8318fa47`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 10:42 — dev-bench/050 a-script-writes-the-released-bench-firmware-list

`scripts/bench-firmware-list.py [--version V] [--commit C] [--out FILE] [--study-designer DIR] <release> <app:board:path[@base]>...` writes `release/bench-firmware.json` (schema 1) using study-designer's `image_segments` example; four new tests. Never run on a real Zephyr image.
**Merged:** `agent/dev-bench/050-a-script-writes-the-released-bench-firmware-list` (code `f93cebf`, ff from `60ab42c`; doc `25655245`, the worker's `f30224d6` cherry-picked onto `9e14433b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the script reads image files only and was run on the shared crate's fixtures, never on a built bench image.

---

### 2026-11-24 10:41 — ui/118 make-live-skips-a-signal-whose-stored-safe-off-it-cannot-read

Make live skips (posts no row for, with a failed `POST /signals` row) a signal when `GET /signals` fails and the bench states no safe-off; decision 90 amended and trimmed back under 4 KB; my edits at fold: a typo in 90 and `spec/bench-live.md`'s Safe-off paragraph. Nothing re-declares such a signal by itself.
**Merged:** `agent/ui/118-make-live-skips-a-signal-whose-stored-safe-off-it-cannot-read` (code `3974192`, ff from `974813e`; doc `367e4f5c`, the worker's `0215ee98` cherry-picked onto `82dcfabe`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; tested against the stub Core only.

---

### 2026-11-24 10:38 — study-designer/092 the-image-segment-reader-checks-a-segments-end-address

`merge` in `hil_image.rs` checks every chunk end with `checked_add`; overflow is `ImageError::Overlap`. Reviewer note below its bar, not filed: `Overlap`'s Display says 'writes address twice' for an overflow.
**Merged:** `agent/study-designer/092-the-image-segment-reader-checks-a-segments-end-address` (code `7ad0a02`, ff from `11a98fa`; doc `55580c05`, ff from `8ff59eba`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 10:22 — ui/117 make-live-declares-an-outputs-safe-off

`Part.safe_off` and `[[signals]]` `safe_off` sent by Make live (and `embarch-ui bench make-live`); report rows say declared / none / kept from Core; Safe-off textarea in the part inspector (no browser drive exercised it). Re-declare rule kept: bench's safe-off wins; none stated means read `GET /instruments`/`/signals` and keep Core's; never clears. Decision 90 amended.
**Merged:** `agent/ui/117-make-live-declares-an-outputs-safe-off` (code `974813e`, ff from `1eee252`; doc `2b89bf6b`, the worker's `8cff84c7` cherry-picked onto `5ef957ec`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The new textarea was only `node --check`ed and `tests/browser` was not run (no browser in the worker's environment); the stub Core does not check bearer tokens, so the person-token path is the same client as before rather than a tested one.

---

### 2026-11-24 10:18 — api/187 the-instrument-and-signal-tools-carry-a-safe-off

`declare_instrument`/`declare_signal` take `safe_off`; CLI `--safe-off`, `--clear-safe-off`. Re-declare rule (decision 97 amended): omitted keeps the stored value, empty clears, failed read stops the declare. `api/188` (et54 preset safe-off) parked `blocked`: needs the load's input-off command from its programming manual, found in no doc repo; Blocked comment on EMB-334 asks the owner.
**Merged:** `agent/api/187-the-instrument-and-signal-tools-carry-a-safe-off` (code `f6907c1`, ff from `e34ec16`; doc `50a446ea`, the worker's `33c8224a` cherry-picked onto `a741bfbe`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; tested against the mock Core only, through the CLI path (the MCP tool entry shares its helpers).

---

### 2026-11-24 10:15 — core/150 core-records-what-it-flashed-with-its-segments-across-a-restart

Core's `ImageLog` backed by `flashed-images.jsonl`, read back at start; entries gain `identity`, `segments`, `scope`, `at_utc_ms`, `call_log_seq`; Core turns on study-designer's `hil-image` feature; `/status` `last_images` unchanged. No test drives the real `/flash`/`/bootload` handler (a handler forgetting to mark its `BoardNote` would pass). Reviewer finding EMB-400.
**Merged:** `agent/core/150-core-records-what-it-flashed-with-its-segments-across-a-restart` (code `1b3562d`, ff from `cadbdb1`; doc `bee96da1`, the worker's `2629a079` cherry-picked onto `c078af54`).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-400
**Hardware debts:** one real `/flash` and one real `/bootload` on the bench, then check `flashed-images.jsonl` has each line with `role` and a `call_log_seq` matching the call-log entry, and that it survives a Core restart; plus the native Windows build of `embarch-core`.

---

### 2026-11-24 10:09 — study-designer/091 the-image-segment-reader-refuses-a-malformed-elf-and-unknown-keys

ELF path checks every offset sum; overflow is `ImageError::Elf`; `Segment`, `BenchImage`, `BenchFirmwareList` refuse unknown keys. One sum left, `merge`'s address end: filed EMB-399, fixed by `study-designer/092`. **Leg start, to carry:** Fleet Ready held 27 unsplit issues; I split four at `2ff73f95` (EMB-397 here, EMB-361 to `core/150`, EMB-334 to `api/187`+`api/188`, EMB-337 to `ui/117`), ts `1795539178.532629`. Not taken: EMB-323, EMB-326, EMB-352 (each needs a new decision).
**Merged:** `agent/study-designer/091-the-image-segment-reader-refuses-a-malformed-elf-and-unknown-keys` (code `11a98fa`, ff from `74cb8dc`; doc `cfa2a28a`, ff from `37ef5968`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 09:44 — suite/059 land-the-safe-off-field-with-its-consumers

Cross-repo pass, announced (ts `1795536052.967279`, 09:00, no reply) and run at 09:32: `Instrument.safe_off` and `SignalLink.safe_off` in topology (line cap 4,096 B repeated from Core's `MAX_WRITE_BYTES`), decision 49 amended, consumer struct literals gain an empty `safe_off`, Core's `PUT /instruments` and `POST /signals` store it and 400 a bad line. Nothing sends a safe-off yet. **Carry:** `PUT /instruments` replaces by name, so a re-declare drops a safe-off unless the surface carries it; EMB-334 and EMB-337 have Finding comments saying so. Landed alone `topology/072` would have broken consumers, so it was parked `blocked` behind this and all four landed back to back.
**Merged:** `agent/topology/072-an-instrument-and-a-signal-declare-a-safe-off` (code `77335f2`, ff from `6a62335`; doc `a5171480`, the worker's `8efe2814` cherry-picked onto `cd2eda0c`, task-file conflict resolved to `done`); `agent/suite/059-land-the-safe-off-field-with-its-consumers` (core `cadbdb1` from `1f9a629`, api `e34ec16` from `d8de537`, ui `1eee252` from `f3f796d`; doc `0acd7123`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (test-only literal change, so a formality).

---

### 2026-11-24 09:10 — ui/116 a-saved-bench-is-made-live-from-the-terminal

`embarch-ui bench make-live <slug> [--config <name>] [--bind <role>=<serial>]...` runs `live::make_live` with the person's token; exits 1 on a failed row or a bind that applied nothing; retracts nothing. Decision 90 amended. Open question EMB-398: as shipped, any process that can run the UI binary acts as the person on Core.
**Merged:** `agent/ui/116-a-saved-bench-is-made-live-from-the-terminal` (code `f3f796d`, ff from `328790f`; doc `f5babce0`, the worker's `50077e0a` cherry-picked onto `1f675d46`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the command is verified against a stub Core only, as the feature row's `unit` says.

---

### 2026-11-24 09:08 — umbrella/106 status-and-doctor-json-carry-a-schema-version

`status --json` and `doctor --json` carry `schema_version` (`JSON_SCHEMA_VERSION = 1`, the umbrella's own counter); `status --json` gains `success` (always true). Decision 11 amended; bump rule is any shape change. A strict-parsing GUI consumer would break on the new keys; none found.
**Merged:** `agent/umbrella/106-status-and-doctor-json-carry-a-schema-version` (code `6934dae`, ff from `ea8fbf0`; doc `1f675d46`, the worker's `7f9e8b77` cherry-picked onto `cc9c72a5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 09:05 — study-designer/090 an-images-segments-and-identity-are-defined-once

Host-only `hil-image` feature: `image_segments(bytes, Hex|Elf|Bin, base)`, segment `{address, length, sha256}`, `identity` = SHA-256 of canonical JSON, `BenchFirmwareList`/`BenchImage` (schema 1); new `interfaces/hil-image.md`. Fixtures are an x86-64 ELF standing in for firmware; a real Zephyr ELF's `PT_LOAD` set may differ from its hex.
**Merged:** `agent/study-designer/090-an-images-segments-and-identity-are-defined-once` (code `74cb8dc`, ff from `1fe70b8`; doc `55738ecd`, the worker's `3d7ae275` cherry-picked onto `4e999d62`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 04:10 — umbrella/105 the-first-run-chip-hint-names-cores-chip-list

`embarch doctor`'s chip fix line and `embarch init`'s scaffold comment now say `embarch-core chip-list <soc-substring>`. Leg's last unit (cap 4). After it `queue-status.py` held no task-file work (`suite/058` parked to 2026-12-01). Linear's hourly cap: something spends ~2,500/hour incl. the fleet's own per-issue `ready` reads; the next leg may find Fleet Ready unreadable (THR-32).
**Merged:** `agent/umbrella/105-the-first-run-chip-hint-names-cores-chip-list` (code `ea8fbf0`, ff from `4cc725f`; doc `285eb0de`, the worker's `dec917ec` cherry-picked onto `0bd1987e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 04:10 — topology/071 the-linking-process-sets-the-identity-stores-folder

`paths::set_data_dir(dir)` (re-exported `hardware::set_data_dir`) lets the linking process set the identity store's folder once before first read; decision 23 amended. Core calling it is the HIL plan's attested-phase unit A.4. The setting test is safe only while no other lib test reads `data_dir()`. **Leg, to carry:** I split EMB-310 (`umbrella/105`), EMB-320 (this), EMB-312 (`suite/058`, **parked `blocked` until 2026-12-01**, the removal date of decisions 97/83; a cross-repo wire removal, so the leg that unparks it announces first) at `afe9024f`, ts `1795518116.601709`; only EMB-310 reached Fleet Working: `filed` for EMB-320 and EMB-312 hit Linear's cap, so the next `ready` reports them ALREADY SPLIT and must re-run `filed` for each. 25 Fleet Ready issues remain unsplit, ~20 more wait on blockers.
**Merged:** `agent/topology/071-the-linking-process-sets-the-identity-stores-folder` (code `6a62335`, ff from `ee45b6c`; doc `0bd1987e`, the worker's `3cb744cb` cherry-picked onto `5d3dfdf4`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:52 — umbrella/104 the-umbrella-readme-carries-no-counted-inventory

Umbrella README loses its command table and counted inventory; links interface docs and `embarch --help`. README now points at `interfaces/`, which holds only `doctor-chain.md` and `verify-release.md` (the command surface lives in `spec.md`); one-line fix not filed.
**Merged:** `agent/umbrella/104-the-umbrella-readme-carries-no-counted-inventory` (code `4cc725f`, ff from `b2579bf`; doc `751ee6c4`, the worker's `b067f49d` cherry-picked onto `fb6efd41`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:52 — core/149 the-core-readme-carries-no-counted-inventory

Core README loses endpoint counts, source layout, endpoint table and dev-bench detection prose; links Core's interface docs.
**Merged:** `agent/core/149-the-core-readme-carries-no-counted-inventory` (code `1f9a629`, ff from `5255f67`; doc `fb6efd41`, the worker's `4190d0cf` cherry-picked onto `da42c84b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (README-only change, so a formality).

---

### 2026-11-24 03:42 — doc/100 studies-guide-leads-with-the-signals-own-baud

Studies guide leads with the signal's own baud; `EMBARCH_SIGNAL_BAUD` is only the fallback for a signal that declares none (default 1000000).
**Merged:** `agent/doc/100-studies-guide-leads-with-the-signals-own-baud` (doc `e8eb2358`, the worker's `4d81b548` cherry-picked; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:41 — ui/115 four-routes-nothing-calls-are-deleted

Four routes nothing calls deleted (`POST /api/topology/roles/{role}/board`, `POST /api/topology/link`, `POST /api/topology/profiles/{slug}/apply`, `GET /api/study-designer/gatt/{study_id}`) with their handlers; decisions 90 and 94 amended. An out-of-repo caller now gets 404.
**Merged:** `agent/ui/115-four-routes-nothing-calls-are-deleted` (code `328790f`, ff from `df42a52`; doc `08dfde1b`, the worker's `f7404c09` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:39 — umbrella/103 the-installed-hil-skill-cannot-drift-from-the-apis

`embarch init` now `include_str!`s the api's `skills/embarch-hil/SKILL.md` through the sibling checkout instead of a pinned copy (decision 59 amended); a missing sibling is a compile error. A worktree build embeds the api main checkout's working tree, so an uncommitted edit there is compiled in.
**Merged:** `agent/umbrella/103-the-installed-hil-skill-cannot-drift-from-the-apis` (code `b2579bf`, ff from `27f43a5`; doc `754b8acc`, the worker's `a6eac931` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:37 — api/186 the-api-readme-carries-no-counted-inventory

Api README no longer counts or lists tools or endpoints; getting-started follows `suite/user-guide.md`. Not run-true (the `embarch` binary was not run). **Leg start, to carry:** burndown leg re-armed by the owner at 03:05 (weekly 56%); leftover `agent/atlas/097-*` and `agent/ui/059-*` remote branches are not landed work.
**Merged:** `agent/api/186-the-api-readme-carries-no-counted-inventory` (code `d8de537`, ff from `abbd3cf`; doc `6c6db754`, the worker's `aed774c8` cherry-picked onto `270062bb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:36 — chat/036 the-promptu-card-test-waits-for-the-state-it-asserts

The promptu card test waits (5 s bound) for the `state` event after the one it asserts. **This leg ended burndown and dreamed:** EMB-294 was the only dispatchable work; sweep read the `chat`, `desk`, `promptu`, `ui` open questions the 00:23 spread sweep had skipped, nothing filed; `fleet-burndown.py --clear --reason 'queue empty'` at 02:36, pump stays latched in normal mode. Dream posted ts `1795512985.272199`: (1) `last_session` writes a Handoff desk line (EMB-189's second half); (2) the desk answers 200 to a mark without an item; (3) old `/api/topology/profiles/{slug}` routes refuse a non-slug with 400. Burndown ended with 44% of the week unspent and 27 h to reset; re-arm with `/fleet start burndown` if wanted.
**Merged:** `agent/chat/036-the-promptu-card-test-waits-for-the-state-it-asserts` (code `23492eb`, ff from `497cbba`; doc `599ad4a9`, the worker's `0f013ce6` cherry-picked onto `95b8eef5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:16 — promptu/020 a-pattern-line-is-replayed-on-past-prompts

Decision 47 amended: `week draft` replays up to 5 past rough prompts per changed pattern line (question/new_question/picker targets) with old and new frontmatter, side by side under `week/<week>/replay/`, listed in `check.replay`. A CLI that reports no cost counts as $0, so the dollar cap never stops a replay; W24's call-count cap is the alternative, **owner to pick before the timer runs unattended**.
**Merged:** `agent/promptu/020-a-pattern-line-is-replayed-on-past-prompts` (code `dcb6588`, ff from `eb1c674`, two commits `2d6fae4` and `dcb6588`; doc `c6d9434c`, the worker's `c0fdb90a` cherry-picked onto `7b29fc41`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fake `claude` answers every call alike, so no test has seen old and new disagree: one `week draft` on a real week with a question-changing line should write replay files whose two sides differ.

---

### 2026-11-24 02:15 — chat/035 a-click-on-the-promptu-cards-weekly-line-runs-or-opens

Decision 95 amended: a click on the Promptu card's weekly line opens an untracked chat with `/embarch-promptu:review` typed unsent, or runs `promptu week run --json` once in the background when no sheet waits (nothing starts while a run is going, `week status` says `running`, or exit 4). 30-minute run limit vs the contract's 60-minute drafter cap: a heavy week may show as failed while running.
**Merged:** `agent/chat/035-a-click-on-the-promptu-cards-weekly-line-runs-or-opens` (code `497cbba`, ff from `36b5c41`; doc `7b29fc41`, the worker's `dcc76c8e` cherry-picked onto `3cfb639c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Run only against a fake `promptu` and headless Firefox: in a real VS Code window with `promptu` installed, a click with no sheet should start one `week run`, and with a sheet waiting should open a chat with `/embarch-promptu:review` typed.

---

### 2026-11-24 02:08 — ui/114 compact-ui

Compaction, no code: `embarch-ui/decisions/shell.md` 11,553 to 8,931 B (decisions 58-59 moved verbatim to `decisions/page-links.md`), `spec/tabs.md` 9,079 to 8,165 B (tab folders to `spec/tab-folders.md`). Worker's open question, shared: can `spec.md` alone answer what someone needs to work on the UI. Repointed link in `decisions/tab-folders.md` still reads `../spec/tabs.md` as text.
**Merged:** `agent/ui/114-compact-ui` (code: no commits, embarch-ui `main` stays `df42a52`; doc `96bc184d`, the worker's `03649426` cherry-picked onto `5d1ed1a7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:08 — promptu/021 the-weekly-sheet-opens-with-decision-15s-numbers

Decision 15 amended: all five checks on the sheet in fixed order; the two friction checks carry `control` (sessions with `promptu: false`); no data is `value: null`, contract §10 now says so; `sheet.md` opens with a read-only numbers block and the feel line. Targets are still text; nothing marks a miss.
**Merged:** `agent/promptu/021-the-weekly-sheet-opens-with-decision-15s-numbers` (code `eb1c674`, ff from `d4cdb6a`; doc `5d1ed1a7`, the worker's `87632ea6` cherry-picked onto `5d877f98`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run on a real week's pack: the five checks are tested on fixtures only; `promptu week draft` on a real week should show all five, with a control figure if any session ran without Promptu.

---

### 2026-11-24 01:56 — promptu/023 a-terminal-skill-walks-the-weekly-sheet

**Recovery fold:** the leg that merged this, `desk/043` and `ui/113` died on a 5-hour 429 at ~00:45 with its fold half done and uncommitted; I checked the half-fold against the merged commits, re-gated `main` and committed it here. Plugin skill `/embarch-promptu:review` (`disable-model-invocation: true`) walks `week show --json` in `AskUserQuestion` pages. Nothing the dead leg wrote says it gated before merging.
**Merged:** `agent/promptu/023-a-terminal-skill-walks-the-weekly-sheet` (code `d4cdb6a`, ff from `43f195a`; doc `4cd54137`), both merged by the dead leg.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill has not been typed in a real Claude Code session against a real sheet; `/embarch-promptu:review` on a machine with the plugin at 0.4.0 and a drafted week is owed.

---

### 2026-11-24 00:36 — desk/043 the-desk-sets-the-weekly-sheets-feel-line

Desk decision 65 amended: fifth Promptu route `POST /promptu/feel/{week}` (`better|same|worse`) runs `promptu week mark --feel`; no MCP tool reaches it (`no_tool_reaches_the_promptu_routes` guards). Settled/superseded sheet is a 400 the tab can tell apart only by message text.
**Merged:** `agent/desk/043-the-desk-sets-the-weekly-sheets-feel-line` (code `99ffa07`, ff from `921f0ee`; doc `ba634c47`, the worker's `42dd21f8` cherry-picked onto `c5034930`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Tested only against a fake `promptu`; on a desk with `promptu` installed and a sheet waiting, `POST /promptu/feel/<week>` with `{"feel":"same"}` should set the sheet's `feel` and show it in `week show`.

---

### 2026-11-24 00:35 — ui/113 the-desk-tab-draws-the-weekly-promptu-sheet

UI decision 56 amended: Desk tab's Promptu bar ('Promptu · <week> · n waiting', hidden at `open: 0`) opens a panel from `GET /promptu/sheet` (numbers, group ✕, line ✓/✕ with notes, feel line, Apply). No Rust changed (generic desk proxy). Group ✕ posts a group id through the line route; not tested end to end.
**Merged:** `agent/ui/113-the-desk-tab-draws-the-weekly-promptu-sheet` (code `df42a52`, ff from `b1b1a24`; doc `1d05bc8b`, the worker's `c97666f2` cherry-picked onto `ba634c47`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against a real desk or a real `promptu`: the drive serves its own stand-in desk. On a desk with `promptu` installed and a sheet waiting, open the Desk tab, mark a line, set the feel line and apply.

---

### 2026-11-24 00:19 — desk/042 the-desk-serves-promptus-weekly-sheet

Desk decision 65 amended: four Promptu routes behind the desk token (`GET /promptu` cached 60 s, `GET /promptu/sheet`, `POST /promptu/sheet/{week}/{line}`, `POST /promptu/apply/{week}`), each runs one `promptu` command. A timing flake `claude_agents_is_dated_by_when_it_was_asked_not_when_it_answered` failed once in four full runs; not filed.
**Merged:** `agent/desk/042-the-desk-serves-promptus-weekly-sheet` (code `921f0ee`, ff from `d0c0233`; doc `5fda0d30`, the worker's `a17f226b` cherry-picked onto `f21146a2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against the real `promptu` CLI: the tests use a fake on a scratch `PATH`. On a desk with `promptu` installed, `GET /promptu/sheet` and a mark round trip are owed.

---

### 2026-11-24 00:18 — promptu/018 week-run-packs-and-drafts-one-run-at-a-time

Decisions 14 and 45 amended: `promptu week run` packs and drafts under `week/run.lock`; a second run exits 4 (contract §14); stale lock = dead pid or over 2 h; `run.json` always settled; `week timer`. The 2 h stale age is a guess at the longest real pass.
**Merged:** `agent/promptu/018-week-run-packs-and-drafts-one-run-at-a-time` (code `43f195a`, ff from `f9c43d0`; doc `f21146a2`, the worker's `103334e8` cherry-picked onto `04ee3aa9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run under a real systemd user manager: enable the printed units once and confirm `Persistent=true` catch-up and the `ExecStart` quoting (in `open.md`). Without `/proc` only the 2-hour age frees a dead run's lock.

---

### 2026-11-24 00:06 — promptu/019 week-mark-and-apply-turn-approved-lines-into-changes

Decisions 30 and 43 amended: `promptu week mark` (verdicts, notes, `--feel`; refuses unknown id, bad verdict, applied line, settled or superseded sheet) and `week apply` (memory lines via the hook's topic/index checks with a backup; pattern lines committed on `promptu/week-<week>`). 'Settled' means every line applied, so a sheet of only cut lines can still be re-marked.
**Merged:** `agent/promptu/019-week-mark-and-apply-turn-approved-lines-into-changes` (code `f9c43d0`, ff from `beecb5c`; doc `d4d7fc82`, the worker's `e4040860` cherry-picked onto `1b0b3d65`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not yet run against real data: a real memory folder, a real pattern checkout or real drafter output.

---

### 2026-11-24 00:06 — api/184 live-log-states-zone-sent-form-and-added-fields

No code: `embarch-api/interfaces/live-log.md` states the file-name time (lease `started_at` as Core wrote it), `sent`'s object-or-string split by `writer`, additive fields without a `schema` bump, and `core_calls` on a failed call. Nothing confirms Core always stamps UTC.
**Merged:** `agent/api/184-live-log-states-zone-sent-form-and-added-fields` (code: no commits, embarch-api `main` stays `abbd3cf`; doc `1b0b3d65`, the worker's `d3e5faf3` cherry-picked onto `f409bc58`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new. The live log on a real bench stays as `embarch-api/open.md` says: run `mem_read` and `reset` with a lease held and read `embarch/live/`.
## 2026-11-23 — 46 units

*Folded by the leg of 2026-11-24 per protocol §11 (embarch-log-folder): the per-unit narrative reasoning, gate transcripts and "Least sure about" prose went, and git holds them; every SHA, Reviewer line, board-naming debt and the spread-sweep line is kept as written. Detail for any unit is in the commit named under it.*

**Carry forward (open at the end of the day):**
- **Decisions made on the owner's behalf, all under the delegation, none new-numbered in burndown:** `doc/099` moved ten board-reaching `embarch-api` tools from ask to allow in `suite/agent-guide.md` §1.1 (58 tools, 37 allow, 21 ask; resting on the lease gating them and on Core refusing them during a run, `core/143`). `core/148` and `api/185` landed together as one cross-repo shape, `observed.call_log {head, first_seq, last_seq, count}` in `report-data.json`; either half alone fails verify check 6. Accepted cost in decision 124: a zip published by a Core built between `core/145` and `core/148` fails check 6 for the missing field, so redeploy Core before publishing.
- **Blocked on the owner:** `atlas/097` (EMB-248, the prior-art source's robots-file question) with `atlas/098` and `atlas/099` behind it; the owner has since marked all three Owner required. Branch `agent/atlas/097-prior-art-search-returns-a-hit-table` is kept in the `embarch-doc` main checkout, task `blocked`.
- **Open and dispatchable at day end, two scopes only (the refill gate fires for spread):** `api/184` (EMB-290), `promptu/018` (EMB-277), `promptu/019` (EMB-279), `promptu/020` (EMB-281). EMB-278 is splittable once EMB-274 is Done; EMB-284 waits on EMB-277, EMB-280 and EMB-282 on EMB-279, EMB-283 on EMB-282. The promptu tasks all add `week` subcommands in `src/main.rs`, one per wave.
- **Filed:** EMB-292 (fleet, owner's lane: `build_features.py` has no `promptu` or `atlas` section, so those workers have no feature row they may write; `features.d/chat-036-promptu-week-pack-sessions.md` was adopted by hand); EMB-293 closed in `core/148`'s fold. `atlas/107` (compact `embarch-atlas/design.md`, 23,474 of 25,600 B) is `blocked`, due 2026-12-07. EMB-286 (promptu gate fails with a crowded `/tmp`) was fixed by `promptu/012`.
- **Bench and Windows:** `api/059` and `dev-bench/038` stay open, no board; burndown skipped them. Native Windows build of `embarch-core` is owed for `core/139` to `core/148` (a worktree cannot build natively), and the deployed Core needs a redeploy to carry `core/139` to `core/148`.
- **Recurring failure:** a leg died on a 5-hour 429 mid-fold (after `core/143`, about 20:50) leaving a doc half merged and unpushed for about ten minutes; `promptu/011`'s leg recovered it. Burndown runs until 2026-11-25 06:00 (stops at 97%). A fold-trailer wart: `core/141`'s fold commit `c4a8592d` carries `Log: embarch-fleet@bb4a01b`, a commit that is on no remote; after a forced rebase, add a second log commit, never amend.
- **Announcements:** last leg's wave went out with the 23:45 announcement ts `1795501351.430619`; earlier ones `1795482132.287899`, `1795473685.846769`, `1795466178.988799`, `1795464400.823999`.

Spread sweep: nothing filed (2026-11-23 18:00)

**Other SHAs and timestamps the day named** (split, claim and fold commits of the legs, and Slack announcement/dream ts values; a revert handle only): 09b3ddf8 1c25ce9 1f743ba7 29f15e09 4509d241 49c5d3b4 54812073 572bca3 636db678 8088d6e0 8ee6c6bb 91e0286e ab50139f b5c7ff65 d0c0233c1198 d9c2f60c dce9b7b e5d025c2 f79c167 f99f6816 fafa3f2c fddca96d ffee53fe; ts 1795463694 1795470987 1795471472 1795476373 1795478837 1795494535 1795496707.

---

### 2026-11-23 23:47 — api/185 check-6-and-the-appendix-read-the-call-log-claim
**Merged:** `agent/api/185-check-6-and-the-appendix-read-the-call-log-claim` (code `abbd3cf`, ff from `c2b619a`; doc `51e679bf`, the worker's `893eff1f` cherry-picked onto `2f624847`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. With `core/148` deployed, `embarch-api verify` on a fresh publish should pass check 6 with the call-log field and the appendix should print it; a zip from a Core between `core/145` and `core/148` should fail check 6 naming `observed.call_log`.

### 2026-11-23 23:46 — core/148 report-data-carries-the-call-log-claim
**Merged:** `agent/core/148-report-data-carries-the-call-log-claim` (code `5255f67`, ff from `7165e51`; doc `37db70fd`, the worker's `67f1cbda` cherry-picked onto `51e679bf`, plus my three-line fix in this fold).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-293
**Hardware debts:** none on a board. The native Windows build of embarch-core at `5255f67` is owed (the owner runs it). On the deployed Core once it carries `core/148`, publish one run and run `embarch-api verify` on the zip: check 6 should pass with `observed.call_log` present, and the appendix should print the head, range and count.

### 2026-11-23 23:46 — atlas/106 a-measured-fact-shows-beside-its-datasheet-claim
**Merged:** `agent/atlas/106-a-measured-fact-shows-beside-its-datasheet-claim` (code `74048d8`, ff from `b7f894a`; doc `337544ac`, the worker's `fd14ebb9` cherry-picked onto `37db70fd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, write one real measurement back with `live write-back` against a register whose datasheet reset value is known, then run `register` on it and the mismatch report: the value should show beside the claim, and a disagreement should appear as `measured-vs-datasheet`. Tests use fixtures and a fake `embarch-api`.

### 2026-11-23 23:45 — promptu/016 week-pack-carries-friction-unmatched-starts-and-outcomes
**Merged:** `agent/promptu/016-week-pack-carries-friction-unmatched-starts-and-outcomes` (code `beecb5c`, ff from `ac36f2d`; doc `e0139deb`, the worker's `b3ae36dd` cherry-picked onto `337544ac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:16 — promptu/017 week-draft-turns-the-pack-into-a-sheet
**Merged:** `agent/promptu/017-week-draft-turns-the-pack-into-a-sheet` (code `ac36f2d`, ff from `d0431fe`; doc `d3a1d70c`, the worker's `3fa228a5` cherry-picked onto `4d376762`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:15 — chat/034 promptu-card-shows-the-weekly-pass
**Merged:** `agent/chat/034-promptu-card-shows-the-weekly-pass` (code `36b5c41`, ff from `8101942`; doc `4d376762`, the worker's `56da0bb2` cherry-picked onto `6e5703e4`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:14 — atlas/105 a-live-finding-is-written-back-as-a-measured-fact
**Merged:** `agent/atlas/105-a-live-finding-is-written-back-as-a-measured-fact` (code `b7f894a`, ff from `4403850`; doc `6e5703e4`, the worker's `90cda886` cherry-picked onto `61d7c7c3`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read`, then `live write-back --seq <its entry>`: the record's receipt should match `embarch-api call-log --seq N --json` for that entry and name the image "read back" or "as last flashed by Core". The worker read the `call_log.entries` shape from embarch-core and embarch-api source on `origin/main`; tests use a fake `embarch-api`.

### 2026-11-23 23:13 — api/183 verify-checks-the-call-log-segment
**Merged:** `agent/api/183-verify-checks-the-call-log-segment` (code `c2b619a`, ff from `421d01c`; doc `61d7c7c3`, the worker's `b48457a9` cherry-picked onto `d93f9484`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. On the deployed Core, publish one run sealed after `core/145` and run `embarch-api verify` on its zip: check 8 should list the call-log range it compared.

### 2026-11-23 22:34 — atlas/104 live-log-lines-agree-with-embarch-api
**Merged:** `agent/atlas/104-live-log-lines-agree-with-embarch-api` (code `4403850`, ff from `e461ddd`; doc `3d8ce989`, the worker's `84c3e4f2` cherry-picked onto `4003b6ec`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read` against a board Core has flashed. Its decoded line should name the same `image_sha256` and `board` as embarch-api's raw line for that call. Then stop Core and check that an atlas live call writes no decoded line.

### 2026-11-23 22:33 — chat/033 permissions-command-drops-instrument-exchange
**Merged:** `agent/chat/033-permissions-command-drops-instrument-exchange` (code `8101942`, ff from `22717b0`; doc `4003b6ec`, the worker's `51150f81` cherry-picked onto `9ea1c31c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 22:32 — promptu/012 folder-name-decode-survives-a-crowded-temp-folder
**Merged:** `agent/promptu/012-folder-name-decode-survives-a-crowded-temp-folder` (code `d0431fe`, ff from `28eab3a`; doc `9ea1c31c`, the worker's `85b1e26b` cherry-picked onto `fe32fb59`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 22:31 — api/182 restore-skips-the-call-log-segment
**Merged:** `agent/api/182-restore-skips-the-call-log-segment` (code `421d01c`, the worker's `7d32fa4` plus my `421d01c`, ff from `f2912db`; doc `fe32fb59`, the worker's `cecbd75d` cherry-picked as `15114739` onto `48bfda50`, plus my `fe32fb59`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on the deployed Core, swept-then-republish a run whose earlier zip carries `call-log-segment.jsonl`: no PUT for the segment, and the republish succeeds. Also publish one run sealed before `core/145` and check it succeeds with no segment.

### 2026-11-23 21:57 — doc/099 agent-guide-permission-lists-match-the-live-design
**Merged:** `agent/doc/099-agent-guide-permission-lists-match-the-live-design` (doc `bcaff6c6`, the worker's `464ebcee` cherry-picked onto `ac147543`; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:55 — atlas/103 live-tools-append-a-decoded-line-to-the-live-log
**Merged:** `agent/atlas/103-live-tools-append-a-decoded-line-to-the-live-log` (code `e461ddd`, ff from `2adf1cc`; doc `ac147543`, the worker's `523f2ef4` cherry-picked onto `fee73fe8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read` and one `shell`, then read `embarch/live/`. The atlas's decoded lines should follow embarch-api's raw lines in the same file and name the same Core entries.

### 2026-11-23 21:54 — promptu/014 week-status-show-and-desk-report-the-weekly-pass
**Merged:** `agent/promptu/014-week-status-show-and-desk-report-the-weekly-pass` (code `28eab3a`, ff from `761eb83`; doc `fee73fe8`, the worker's `1ee67f10` cherry-picked onto `810a14b2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:53 — api/179 an-idle-released-lease-refuses-the-next-hardware-call
**Merged:** `agent/api/179-an-idle-released-lease-refuses-the-next-hardware-call` (code `f2912db`, ff from `c7efaef`; doc `810a14b2`, ff from `ee8747ae`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on the deployed Core, hold a lease, leave it 30 minutes with no hardware call, then run `mem_read` and `lease_show`. The `mem_read` should refuse with Core's reason, without reaching Core, and `lease_show` should report no token (recorded in `open/bench-verification.md`).

### 2026-11-23 21:22 — promptu/013 week-pack-writes-per-run-events
**Merged:** `agent/promptu/013-week-pack-writes-per-run-events` (code `761eb83`, ff from `cb9d928`; doc `89f04e05`, the worker's `30a571d5` rebased onto `1a7059fd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:21 — core/145 a-runs-signed-record-names-its-call-log-range
**Merged:** `agent/core/145-a-runs-signed-record-names-its-call-log-range` (code `7165e51`, ff from `f1bcefc`; doc `4d655e9a`, the worker's `cbeff2eb` rebased onto `2d3af3f8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a real bench study's published zip carrying `call-log-segment.jsonl`, whose entries recompute to the recorded head and still pass `embarch-api verify`.

### 2026-11-23 21:19 — api/180 each-hardware-call-appends-a-live-log-line
**Merged:** `agent/api/180-each-hardware-call-appends-a-live-log-line` (code `c7efaef`, ff from `acde856`; doc `cc67c0c6`, ff from `7cbf31d7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run `mem_read` and `reset`, then read `embarch/live/`. Check that Core's real `X-Embarch-Call-*` headers appear as `seq` and `hash`, that `last_images` gives a real board's image hash, and that a real MCP client's working folder picks the right repo (written into `embarch-api/open.md`).

### 2026-11-23 20:57 — promptu/011 weekly-pass-contract
**Merged:** `agent/promptu/011-weekly-pass-contract` (code `cb9d928`, ff from `ea5c032`; doc `cf5847e1`, ff from `38682ca9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 18:26 — core/143 core-refuses-lease-gated-calls-during-a-run
**Merged:** `agent/core/143-core-refuses-lease-gated-calls-during-a-run` (code `f1bcefc`, ff from `6766785`; doc `ca46bec6`, the worker's commit rebased onto `73ee90ab`).
**Blocked:** nothing.
**Reviewer:** skipped (budget HOLD, 5-hour 98% against burndown's 97% cap).
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a live bench or host study refusing a `mem_read` and a `reset` from the lease holder, and admitting the study's cancel.

### 2026-11-23 18:25 — api/178 instrument-exchange-tool-and-verb-are-gone
**Merged:** `agent/api/178-instrument-exchange-tool-and-verb-are-gone` (code `acde856`, ff from `f28cc3d`; doc `ce097c63`, ff from `39f485cb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 17:42 — core/142 instrument-exchange-refuses-outside-a-run
**Merged:** `agent/core/142-instrument-exchange-refuses-outside-a-run` (code `6766785`, ff from `415cdf3`; doc `30bb99a3`, ff from `db0c7947`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a host study with an `Instrument` step still drives the supply while the bare route refuses.

### 2026-11-23 17:28 — core/141 core-releases-a-lease-idle-for-30-minutes
**Merged:** `agent/core/141-core-releases-a-lease-idle-for-30-minutes` (code `415cdf3`, ff from `5fe3e8a`; doc `d894af6f`, the worker's `507991cb` rebased onto the owner's `160a52f2`, which landed during the fold; fold `c4a8592d`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; a live MCP-held lease left idle for 30 minutes on the deployed Core, to see `embarch-api`'s renew meet the `404` (EMB-256 changes what it does then).

### 2026-11-23 17:20 — atlas/102 design-head-says-what-the-doc-is-today
**Merged:** `agent/atlas/102-design-head-says-what-the-doc-is-today` (code none, the branch had no commits; doc `e58223de`, the worker's `9151c4e7` rebased onto `82b24e12`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 17:18 — core/140 core-keeps-a-hash-chained-call-log
**Merged:** `agent/core/140-core-keeps-a-hash-chained-call-log` (code `5fe3e8a`, ff from `73c51a7`; doc `8b74a0b3`, ff from `6699c5ee`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (not runnable from a worktree), and a first real call log: a live Core session's flash, reset and mem-read entries, with `board` and its image hash. `board` is named only by `/flash`, `/reset`, `/live/mem-read` and `/live/core-state`; null elsewhere (in `open.md`).

### 2026-11-23 16:26 — api/177 study-measurements-reads-a-finished-run-before-publish
**Merged:** `agent/api/177-study-measurements-reads-a-finished-run-before-publish` (code `f28cc3d`, ff from `f30570f`; doc `2c1e505d`, the worker's `4f476a87` rebased onto the owner's `2da83766`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Run both tools against a live Core once the Windows service carries `core/139` (`73c51a7`): **until then the deployed Core has no such route, its unknown-route 404 reads as `no-such-run`**, which is a wrong name for "this Core is too old".

### 2026-11-23 16:11 — core/139 core-serves-a-finished-runs-measurements-before-publish
**Merged:** `agent/core/139-core-serves-a-finished-runs-measurements-before-publish` (code `73c51a7`, ff from `6116b1e`; doc `83991fd7`, the worker's `f8f5e2db` cherry-picked onto `7c37f1fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (`cargo.exe build` from the main checkout), not runnable from a worktree. The route has not met a live Core: read a real finished run's `measurements.json` through it once the Windows service is redeployed. The 410 path has no test.

### 2026-11-23 16:09 — api/176 core-key-prints-cores-public-key
**Merged:** `agent/api/176-core-key-prints-cores-public-key` (code `f30570f`, ff from `f56b423`; doc `1da37390`, the worker's `bb4b3145` rebased onto the owner's `a691d693`, which landed during the fold; fold `7c37f1fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** `core-key` has not met a live Core: the mock cannot sign a fresh nonce, so the success path is unit-tested only. Run it against the running Core and pass its key to `verify` on a published zip.

### 2026-11-23 15:04 — atlas/101 design-records-the-mcp-server-as-atlas-transport
**Merged:** `agent/atlas/101-design-records-the-mcp-server-as-atlas-transport` (code none, the branch had no commits; doc `4edf440a`, ff from `ad6638c9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 14:55 — atlas/097 prior-art-search-returns-a-hit-table
**Merged:** none (blocked before any merge).
**Blocked:** `agent/atlas/097-prior-art-search-returns-a-hit-table` — the robots-file question above; task `blocked` on EMB-248, worktrees removed, branches kept. `atlas/098` and `atlas/099` stay blocked behind it.
**Reviewer:** skipped (not landed: blocked on EMB-248 before any merge).
**Hardware debts:** none.

### 2026-11-23 14:44 — atlas/096 translation-fills-a-module-pads-port
**Merged:** `agent/atlas/096-translation-fills-a-module-pads-port` (code `2adf1cc`, ff from `dae31d4`; doc `6d42f66b`, the worker's `348abdc2` cherry-picked onto `6a5a36bc`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Translate one real module datasheet with the skill and confirm `port` on its pad records (an engineer-supplied datasheet, no board); none sits in either repo.

### 2026-11-23 14:04 — atlas/095 atlas-live-tools-work-under-the-sessions-own-lease
**Merged:** `agent/atlas/095-atlas-live-tools-work-under-the-sessions-own-lease` (code `dae31d4`, ff from `64d2c5b`; doc `910c80c9`, ff from `b185dcac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** with the lease taken through the embarch-api MCP, atlas `shell` `device list` in the same session with `lease_token` set should return the device list, not a 409; and Core's real 409 text for a wrong or missing token should still match `409|lease`. Needs a live Core and a board (recorded in the task's Outcome, now retired).

### 2026-11-23 13:57 — atlas/094 a-modules-pad-table-gives-unnamed-pads-their-port
**Merged:** `agent/atlas/094-a-modules-pad-table-gives-unnamed-pads-their-port` (code `64d2c5b`, ff from `902f144`; doc `8f75e182`, ff from `a56d71f1`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The pad-table source has met one synthetic module fixture; no real module datasheet has been translated with `port`.

### 2026-11-23 13:52 — atlas/093 shell-commands-help-text-and-kernel-subcommands
**Merged:** `agent/atlas/093-shell-commands-help-text-and-kernel-subcommands` (code `902f144`, ff from `893275d`; doc `ec22da7f`, the worker's `e800a878` cherry-picked onto `74e0cfb2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Both layouts have met only synthetic ELFs built from the 4.4 headers; `shell_commands command=kernel` and `command=i2c` on a real 4.4 image would confirm it, including the help struct's alignment on a 64-bit target.

### 2026-11-23 13:50 — api/175 build-verdict-reports-the-application-image-on-sysbuild
**Merged:** `agent/api/175-build-verdict-reports-the-application-image-on-sysbuild` (code `e68ce94`, ff from `de53e6e`; doc `ffe77a59`, ff from `9a539ba9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The first-table rule has met one synthetic two-table log shaped like the issue's; no real sysbuild build log has been parsed.

### 2026-11-23 13:30 — atlas/092 pin-table-fills-port-and-dt-use-for-every-module-pin
**Merged:** `agent/atlas/092-pin-table-fills-port-and-dt-use-for-every-module-pin` (code `893275d`, ff from `0180a9f`; doc `8d6a4755`, ff from `d8052972`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The net-name fallback has met one generic module fixture; the real-board read was the worker's diagnosis, not a test.

### 2026-11-23 13:21 — desk/041 missing-embarch-api-line-names-every-missing-piece
**Merged:** `agent/desk/041-missing-embarch-api-line-names-every-missing-piece` (code `08214ff`, ff from `25b6877`; doc `28142601`, the worker's `64e84faf` cherry-picked onto `e06d6845`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 13:20 — api/174 zephyr-west-scan-takes-cpu-clusters-from-the-soc
**Merged:** `agent/api/174-zephyr-west-scan-takes-cpu-clusters-from-the-soc` (code `de53e6e`, ff from `97d58d8`; doc `5a56344c`, the worker's `3adab50a` cherry-picked onto `919e5327`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The scan has met only a fixture `soc.yml` shaped like Zephyr's `soc/nordic` file, never a real Zephyr tree or the project that filed the issue; that project still runs `discovery = "static"` until someone switches it back.

### 2026-11-23 13:18 — atlas/091 net-trace-uses-the-fitted-packages-pin-map
**Merged:** `agent/atlas/091-net-trace-uses-the-fitted-packages-pin-map` (code `0180a9f`, ff from `d80aa9f`; doc `b86eb5cc`, ff from `e01c28fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fitted-package inference has met only a generic two-package fixture, never a real board's atlas.

### 2026-11-23 12:55 — api/173 compact-api
**Merged:** `agent/api/173-compact-api` (doc only, no code branch; doc `7602bb15`, the worker's `66187c6e` cherry-picked onto `bf446f98`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 12:51 — core/138 open-md-still-owes-verify-check-8
**Merged:** `agent/core/138-open-md-still-owes-verify-check-8` (doc only, no code branch; doc `f3bf0c1d`, the worker's `c187939b` cherry-picked onto `4397f813`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 12:51 — api/172 republish-a-swept-run-from-the-earlier-zip
**Merged:** `agent/api/172-republish-a-swept-run-from-the-earlier-zip` (code `97d58d8`, ff from `2804e41`; doc `4397f813`, ff from `f31b1850`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The restore path has met a mock Core only: Core's real `409` body and `restore` answers are unseen, and no real swept run has been republished. `restore_file`'s timeout is assumed.

### 2026-11-23 11:57 — core/137 a-republish-after-the-retention-sweep-takes-the-earlier-zips-files
**Merged:** `agent/core/137-a-republish-after-the-retention-sweep-takes-the-earlier-zips-files` (code `606b267` and `6116b1e`, ff from `88aff23`; doc `84ff218a`, worker's `f68ff56a` cherry-picked onto `574e6411`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`, unrun (a worktree cannot build natively). The restore route has met only Core's in-process HTTP tests; no real retention sweep has run on the Windows service, and embarch-api does not send the files until `api/172`.

### 2026-11-23 11:50 — study-designer/089 the-footer-band-is-measured-on-a-typst-page
**Merged:** `agent/study-designer/089-the-footer-band-is-measured-on-a-typst-page` (doc only, no code branch; doc `cf5145d5` and `f7b6260f`, the worker's `8543c1a3` and `7341d8a0` cherry-picked onto `c1d2b942`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The band rests on one font set on one machine, A4 only; a Letter page and a font outside the embedded set are unmeasured.

### 2026-11-23 11:49 — promptu/008 compact-promptu
**Merged:** `agent/promptu/008-compact-promptu` (doc only, no code branch; doc `044c117c`, fast-forward from `60e002f0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
*Days 2026-11-22 to 2026-11-22 rolled to [log-archive/supervisor-log-2026-11-22-to-2026-11-22.md](log-archive/supervisor-log-2026-11-22-to-2026-11-22.md).*
