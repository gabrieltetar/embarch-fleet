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

## 2026-11-21 22:05 — umbrella/101 init-installs-the-hil-skill

**Decided:** nothing suite-wide. `embarch-umbrella` decision 59 (`decisions/integration.md`): `embarch init` installs `.claude/skills/embarch-hil/SKILL.md` from a copy pinned into `embarch-umbrella` (`src/skills/embarch-hil/SKILL.md`), excluded locally like the rest of `init`'s writes; a test fails, never skips, when the pin drifts from `../embarch-api/skills/embarch-hil/`; `--uninstall` removes it; `init --dry-run` is new and prints the plan. **This is a recovery fold**: the 17:01 leg merged the code to `origin/main`, cherry-picked the doc commit into its leg worktree and had consumed the changelog fragment, built `suite/features.md` and amended `embarch-api/open.md` when it died on a 5-hour 429 at about 17:38, before `fold-commit.py`. I found that worktree dirty with exactly that, re-gated, and finished it here rather than redoing it. I shortened the leg's `embarch-api/open.md` line (3,965 to 3,870 of 5,120 B), since it had pushed the file into reserve with no debt filed and the gate was red on it. **I closed `tasks/umbrella/099` `done`**: the worker moved `spec.md`'s marketplace paragraph verbatim to `spec/marketplace.md` (9,281 to 8,808 B) per its dispatch note, the release paragraph and its "not yet run on a tag" statement untouched; `In flux: yes` left as written. The worker's finding stands unfiled: a repo already `init`ed gets no skill (`init` exits on an existing config), and the open line now says to `init --uninstall` then `init`.
**Merged:** `agent/umbrella/101-init-installs-the-hil-skill` (code `b3d0106`, ff on `origin/main` from `ed5d14b`, landed by the 17:01 leg; doc `7ca69785`, the worker's `305c0c0c` cherry-picked onto `2d8d5f1a`). Re-gated by this leg on `origin/main`: `cargo build`, `cargo test` (277 passed), `clippy --all-targets -- -D warnings` green; ownership green on both branches (code checked against `ed5d14b`); client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill path `.claude/skills/<name>/SKILL.md` is `[assumed]` and has not been loaded in a live Claude Code session: run `embarch init` in a scratch repo and confirm the agent lists `embarch-hil`.
**Budget:** PROCEED, 5-hour 0%, weekly 52%, wave 6.
**Least sure about:** the code sat on public `main` for four hours with no doc fold behind it; nothing reads that state as wrong, so a leg that died one step earlier would have left `history/` and `features.md` silently behind the shipped binary.

---

## 2026-11-21 17:37 — ui/111 ui-calls-core-with-the-person-token

**Decided:** nothing suite-wide. `embarch-ui` decision 103 (`decisions/core-token.md`): `config::core_client` builds the UI's one `CoreClient` with `TokenScope::Person`, and **there is no fallback to the agent's token**. **The worker departed from the task's wording, and I accepted it**: the task asked for a missing person token to be reported where the UI reports Core unreachable; instead the UI stops at start with an error naming the token's sources, because every handler holds one `CoreClient` and none can be built without a token, and a banner would need an `Option<CoreClient>` through every handler. The reviewer read it against `embarch-ui` decision 26 (Core unreachable is a runtime state, not a config one) and `embarch-api` decision 109 (no person token is an error naming its sources) and found no contradiction. A banner is a follow-up if the owner wants one; unfiled. I amended `embarch-token.md` §2 (the UI is the person's client and does not start without its token) and `embarch-core/open.md`'s scope line, and set `tasks/api/165`'s `In flux:` to `no` for both files, since its only `yes` waited on this unit. **The api/164 fold's note edit landed apart as `dc7b3757`** (`notes/hil/06`, check 9's `path("…")`): `fold-commit.py` does not stage `notes/`, the gap the 2026-11-20 entry already recorded.
**Merged:** `agent/ui/111-ui-calls-core-with-the-person-token` (code `279c33f`, ff on `origin/main` from `d824791`; doc `4cca5341`, the worker's `f38d3517` cherry-picked onto `dc6dabeb`). Re-gated on the merge result: `cargo build`, `cargo test` (319 passed, 4 ignored, plus 8), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. **A deploy ordering debt**: the next `embarch-ui` deploy does not start unless the UI can read a person token, which a Core from `core/128` on writes at its first start; deploy Core first. Not run against the installed `embarch-ui.service` or a real Core, and the missing-token test passes without checking the error on a machine that has a `person-token` file.
**Budget:** PROCEED, 5-hour 22% at dispatch, weekly 44%, wave 6.
**Least sure about:** whether the deployed Core on the owner's bench already writes `person-token`; if it predates `core/128`, the UI goes from working to not starting on its next deploy, and only the unit's journal says why.

---

## 2026-11-21 17:35 — api/164 render-a-report-to-pdf-offline

**Decided:** nothing suite-wide. `embarch-api` decision 110 (`decisions/report-pdf.md`, `interfaces/report-pdf.md`): Typst linked as a library (`typst`, `typst-pdf`, `typst-layout` 0.15.1, `typst-as-lib` 0.18.0) behind a cargo feature **`pdf`, on by default** because `publish` (M1.10) needs it; measured cold debug build 66 s to 147 s, release 71 s to 187 s, release binary 21.5 MB to 84.3 MB (for a binary that calls `render_report`; `main.rs` does not yet). lilaq 0.6.0 and its three imports (elembic 1.1.1, tiptoe 0.4.0, zero 0.6.1) vendored unedited from the registry tarballs, hashes and MIT licences in `typst-packages/PROVENANCE.md`; lilaq's `jitter` fails, its `suiji` import not vendored. A custom resolver serves only the embedded packages and the staging directory, so no registry is reachable; staging copies by content and refuses symlinks, hard links and escaping names; `ident` and `timestamp` set, and two processes gave identical bytes. EmbArch's own `@embarch/report` helper (`minmax-plot`, `plot-ticks`, `m`), with `plot_ticks` also in Rust and a test holding the two equal. **I folded its fragment** into `embarch-study-designer/interfaces/hil-pdf.md` (`plot_ticks` lives in embarch-api until it moves to the shared crate; the tick arithmetic is `f64`, so `(-0.3, 0.3)` gives step 0.1 where decimal arithmetic gives 0.2, and that case is a test) and `notes/hil/06-report-and-publish.md` check 9 (the helper takes `path("…")`, since a Typst package cannot read the project by a string, so M1.11's whitelist must admit `path()`). I accepted the float behaviour rather than sending it back: the tick texts are still built by integer arithmetic, only the compares are float, and the Typst helper's copy is held equal to the Rust `plot_ticks` by a test. On the reviewer's note I corrected my own fold wording (it had said "one function"; there are two copies held equal), amended `hil-pdf.md` step 6's "exact compare", and appended a dated amendment to `embarch-study-designer` decision 91. **`plot_ticks` moving into the shared crate is owed and unfiled**: it is a two-repo move (crate, then embarch-api's call), best taken with M1.11, which must call the Rust one.
**Merged:** `agent/api/164-render-a-report-to-pdf-offline` (code `b2afdf5`, ff on `origin/main` from `c9f0c79`; doc `9fa11640`, the worker's `1676e029` cherry-picked onto `4567439a`). Re-gated on the merge result: `cargo build`, `cargo test`, `clippy --workspace --all-targets -- -D warnings` and `cargo check --no-default-features` green; `embarch-core-client` untouched, so `embarch-ui` and `embarch-umbrella` were not rebuilt for it; ownership green on both branches; client names clean (vendored text included); `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, 5-hour 22% at dispatch, weekly 44%, wave 6.
**Least sure about:** byte identity across machines is unmeasured, and `verify` (M1.11) rests on it; the first second machine to render the fixture is the check, and nothing schedules it.

---

## 2026-11-21 17:32 — core/131 hash-chained-run-log

**Decided:** **Leg setup, to carry:** this leg split EMB-221 to `core/131` (M1.6), EMB-238 to `api/166` (open), and **EMB-222 into two: `suite/057` and `core/132`.** A study cannot declare a derived measurement today (`Study` has no field for one), and adding one bumps `HOST_TYPE_SCHEMA_VERSION` and breaks the exhaustive `Study` literals in `embarch-core`, `embarch-api` and `embarch-ui` tests, so it is a §8 cross-repo pass, not a worker task. **`suite/057` was announced and parked at 17:10, `ts 1795306202.861479`, window closing 17:40**; `core/132` is `blocked` on it. A spread sweep (only `embarch-api/open.md`, `embarch-core/open.md` and `embarch-token.md` had changed since `Spread sweep: nothing filed (2026-11-18 23:20)`) filed `umbrella/101` from the api `open.md` line. Four workers went out as four foreground `Agent` calls in one message (EMB-214's pattern) and all four reported to this leg. Unit itself: `embarch-core` decisions 111 and 112 (`decisions/run-log.md`, `interfaces/run-log.md`): `run-log.jsonl` beside the token files, one `{entry, hash}` line per run chained by `prev`, entries `run` (carrying the hash of `record.dsse.json` and of every capture), `published` (a manifest hash) and `discarded`; a log that does not verify is never extended. Retention spares a run the log has not seen published or discarded, and `GET /studies` follows the same split. **Decision 112 is the first refusal by scope**: the agent's token gets `403` discarding a failed, errored, inconclusive or published run's captures. Four new lease-open routes (`GET /run-log`, `GET /study/{id}/log`, `POST /study/{id}/published`, `POST /study/{id}/discard`), swept. No schema bump. I folded its fragment into `embarch-token.md` §3, and **closed `tasks/core/130` `done`**: the worker moved `spec.md`'s deployment and release-assets text verbatim to `spec/deployment.md` (9,529 to 7,965 B). The worker filed `tasks/core/133` (compact `open.md`, 4,829 of 5,120 B), blocked, `In flux: yes`. From the reviewer's note I filed **EMB-239** (Fleet Ready, core): retention reads an unreadable log as "nothing protected" and would sweep unpublished captures.
**Merged:** `agent/core/131-hash-chained-run-log` (code `c3414e4`, ff on `origin/main` from `4f5dcc4`; doc `13a86f36`, the worker's `a9ceacf8` cherry-picked onto `fbc0af1a`). Re-gated on the merge result: `cargo build`, `cargo test` (416 passed, 2 ignored, plus 2), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `run-log.jsonl`, unrun (a worktree cannot build natively). No board needed.
**Budget:** PROCEED at the start, 5-hour 0%, weekly 44%, wave 6; 22% 5-hour at dispatch.
**Least sure about:** the discard has never met a person's token from a real client (`ui/111` lands this leg, the CLI has no person scope), so decision 112's refusal is proven only in Core's own tests.

---

## 2026-11-21 12:41 — api/162 core-client-resolves-both-token-scopes

**Decided:** nothing suite-wide. `embarch-api` decision 109 (`decisions/client-crate.md`): `embarch-core-client` gains `TokenScope { Agent, Person }`, `CoreClient::new_with_scope` and `CoreConfig::{person_token, person_token_env, resolve_token_for}`, all additions; a person client reads `person_token_env`, `person_token`, `EMBARCH_PERSON_TOKEN`, then `person-token` beside the agent's file (the same WSL2 `%ProgramData%` mapping), and **never falls back to the agent's token**. The MCP server and every CLI verb build their client through `agent_core_client`, and **no CLI flag selects the person scope**, so only library code (`ui/111`) reaches it. I folded the fact into `embarch-token.md` §2, replacing "Clients still resolve the agent's token alone", and set **`tasks/ui/111` `open`** (its `Unparks when:` named this unit), with a dispatch note naming the API it calls. The worker filed `tasks/api/165` (compact `decisions/client-crate.md` and `interfaces/config.md`, `In flux: per file`, due 2026-11-28), `open`.
**Merged:** `agent/api/162-core-client-resolves-both-token-scopes` (code `c9f0c79`, ff on `origin/main` from `97577b6`; doc `b407e472`, the worker's `21f92513` cherry-picked onto `0eacb879`). Re-gated on the merge result: `cargo build`, `cargo test` and `clippy --workspace --all-targets -- -D warnings` green; **`embarch-ui` and `embarch-umbrella` built green against the branch's crate** (detached worktrees under `.worktrees/gate-162/` with `embarch-api` linked to the unit worktree, `cargo tree -i` confirming the path; removed after); ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The WSL2 `person-token` path has not met a live Core.
**Budget:** PROCEED, 5-hour 60%, weekly 41%, wave 6.
**Least sure about:** the signed-challenge step before a client sends any token (Core decision 110's route) is in no task yet; EMB-238 covers only the build claims, and the challenge matters once an attested install writes a fingerprint, so it is unfiled on purpose but worth naming when M1.10 is split.

---

## 2026-11-21 12:38 — study-designer/086 hil-verdict-rules

**Decided:** nothing suite-wide. `embarch-study-designer` decisions 95 to 98 (`decisions/hil-verdicts.md`): `src/verdicts.rs` behind a new feature `verdicts = ["alloc"]`, beside `reducers`; five rules (`step_verdict`, `limit_verdict`, `acceptance_width`, `combine`, `requirement`) each at behaviour 1, pinned by `Rules::latest()` and refused by `Rules::pinned()` for a behaviour never shipped; it follows decision 93's contract rather than reusing the reducers' `Registry`, since the five signatures differ. **95 closes the gap `084`'s reviewer left on EMB-218**: an observation prompt that times out or is cancelled is `inconclusive`, reason `observation_unanswered`, amended into `hil-shapes.md` (no file carries the string yet, so no `schema` bump). 97 orders evidence defects before `calibration_expired` before the limit, so a truncated capture is `inconclusive` however far out its number; 98's width check is strict, a `relayed` test is listed apart and counted in nothing, and "N of M" counts `not_selected` in `m`. 97's edge handling and 98's readings are marked as assumed where `03` was open. **The unit also paid `tasks/study-designer/087`** per its dispatch note: `interfaces/hil-shapes.md` 11,205 to 9,994 of 12,288 B, its characterisation section moved verbatim to `interfaces/hil-characterisation.md`; I closed 087 `done` in this fold, `In flux: yes` left as written.
**Merged:** `agent/study-designer/086-hil-verdict-rules` (code `1238def`, ff on `origin/main` from `17332cf`; doc `5d512fb4`, ff on the leg worktree from `e559e851`). Re-gated on the merge result: build, test and `clippy --all-targets -- -D warnings` green under no features, `alloc`, `std`, `study-ui,gatt-extract,eap-parse`, and `--no-default-features` with `verdicts` and with `reducers,verdicts`; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at the second pair's dispatch, 5-hour 60%, weekly 41%, wave 6; two units left in the leg, so two workers.
**Least sure about:** M1.3 has no user in milestone 1, so decisions 97 and 98 will first meet real data in the Test phase; a reading there that disagrees with them costs a behaviour version, and nothing schedules that check.

---

## 2026-11-21 12:27 — core/129 sign-study-run-records

**Decided:** nothing suite-wide. `embarch-core` decision 110 (`decisions/signing.md`): an Ed25519 key (`ed25519-dalek` 2) in `signing-key` beside the token files, created on first start, `0600` on Linux and the `icacls` lockdown on Windows, a malformed key stopping Core; `record.dsse.json` per study run, a standard DSSE envelope over an in-toto Statement with predicate type `urn:embarch:predicate:study-run:v1`, its subjects the SHA-256 of every file the run has when it ends (so `measurements.json` joins once M1.7 writes it), `observed` kept apart from `claimed.build`; a run that cannot be signed ends `failed`, never `completed` unsigned. **`POST /auth/challenge` takes no token**, the one exception to "every route requires the token": it signs only `embarch-core-auth-v1`, Core's nonce and the caller's hex nonce, and is merged outside `build_router`'s swept lines, so decision 42's route sweep does not see it. A device study now writes `study.json` so it can be a subject. Build claims arrive as `build_*` query parameters nothing sends yet: I filed **EMB-238** (Fleet Ready, `api`). I folded its fragment into `embarch-token.md` §2 (the key beside the tokens) and added the challenge to §3's "every request carries the token"; on the reviewer's note I corrected `embarch-core/spec.md`'s sweep and scope-record clauses, which the unit had left stale. The worker filed `tasks/core/130` (compact `spec.md`, 9,458 of 10,240 B), blocked, `In flux: yes`.
**Merged:** `agent/core/129-sign-study-run-records` (code `4f5dcc4`, ff on `origin/main` from `789cbfc`; doc `f85141d6`, the worker's `4ebfeb1e` cherry-picked onto `c75b26a2`). Re-gated on the merge result: `cargo build`, `cargo test` (405 passed, 2 ignored, plus 2), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `signing-key`, unrun (a worktree cannot build natively); the task's closing note, now in `embarch-core/open.md`, says how to check both from the main checkout on Windows, and that a second start must reuse the key. No board needed.
**Budget:** DEGRADED, measured wave 2.
**Least sure about:** the declarations ledger that stamps each declaration's scope is in memory, so a record from a Core restarted after its enrolments vouches only from `witnessed_since_utc_ms`; M1.6's protected store is where it should persist, and nothing yet forces that unit to pick it up.

---

## 2026-11-21 12:25 — study-designer/085 hil-reducers

**Decided:** nothing suite-wide. **Leg setup, to carry:** this leg split the four HIL milestone-1 issues in Fleet Ready (`d7ae8e5b`): EMB-217 to `study-designer/085` (M1.2, reducers), EMB-218 to `study-designer/086` (M1.3, verdict rules), EMB-220 to `core/129` (M1.5, signing), EMB-224 to `api/164` (M1.9, PDF); refill then not owed (5 dispatchable, 3 scopes). Workers dispatched as two foreground `Agent` calls in one message, per EMB-214's finding: they ran concurrently and both reported to this leg (370 s and 584 s). Unit itself: `embarch-study-designer` decisions 92 to 94 (`decisions/hil-reducers.md`): the eight reducers in `src/reducers.rs` behind a new feature `reducers = ["alloc"]`, with a dependency-free square root so results match to the bit on every target; a `Registry` keeps every (name, behaviour) pair shipped, all at behaviour 1, and an unshipped one is `UnknownBehaviour`; inputs are standard uncertainties, `U = k·sqrt(instrument² + type_a²)`, `k` 2 by default. `embarch-core` and `embarch-api` are to turn `reducers` on (M1.7, M1.11); no existing consumer names it, so none changed. The worker filed `tasks/study-designer/087` (compact `interfaces/hil-shapes.md`, now 11,205 of 12,288 B), blocked, `In flux: yes`, `Unparks when:` naming `study-designer/086`. This unit also commits the 2026-11-20 day fold, rolls 2026-11-18 into `log-archive/`, and ran `check-client-names.py --suite --history`: clean on all 16 repos.
**Merged:** `agent/study-designer/085-hil-reducers` (code `17332cf`, ff on `origin/main` from `f6cca94`; doc `ffe5c599`, ff on the leg worktree from `731d60a0`). Re-gated on the merge result: build, test and `clippy --all-targets -- -D warnings` green under no features, `alloc`, `std`, `study-ui,gatt-extract,eap-parse` and `--no-default-features --features reducers`; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 12:06 refresh.
**Budget:** DEGRADED at the start (usage cache 20 h old), measured wave 2.
**Least sure about:** the percentile's type-A term (half the one-sigma order-statistic spread) is the worker's convention, unmeasured against any reference; decision 94 records it, and changing it later costs a behaviour version, not a rewrite.

---

## 2026-11-20 — 3 units

*Folded 2026-11-21 by the supervisor leg's embarch-log-folder: per-unit narrative reasoning, re-gate command lists and budget lines went (git holds them); SHAs, Reviewer lines, debts and the carry-forward items below stayed.*

**Carry forward:**
- **A recovery leg.** The 14:25 leg claimed `study-designer/084`, `core/128`, `api/163`, dispatched three background workers at 14:41 and was cut off; the workers died 14:45-14:51 with nothing committed or pushed and no log entry. The 16:05 leg committed each tree as found to its branch, pushed, removed the worktrees, reclaimed each (`bbf6b7be`, `07f42aaf`, `bd893eee`) and resumed all three.
- **EMB-214's foreground-dispatch finding:** the three resumed workers went out as three foreground `Agent` calls in one message at 15:51:55 and returned together at about 15:57 (78 s, 307 s, 291 s). They ran concurrently and each reported to the leg.
- **Refill skipped on a depth firing** (0 dispatchable after the re-claims): no source path has a commit since `Spread sweep: nothing filed (2026-11-18 23:20)`, the same reasoning the 2026-11-19 04:10 leg applied, which the rule's text covers only for a spread-only firing.
- **`/fleet stop` arrived 15:58** (marker on disk, pump already deleted); nothing dispatched after it, the three reported units landed. Leg ended at three, not by budget.
- **`fold-commit.py` refuses to stage `notes/`.** The note edits and three pointer fragments landed as their own commit `c937c8e0`, ahead of the fold. `check-ownership.py --supervisor` passes `notes/`, so the gap is the fold script's file list, not ownership.
- This unit also committed the 2026-11-19 day fold (applied by the 14:25 leg's folder, never committed), rolled 2026-11-17 into `log-archive/`, and ran `check-client-names.py --suite --history`: clean on all 16 repos.
- Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 15:49 refresh.
- Decisions made, none suite-wide: `embarch-api` 108 (`embarch-api guide hil [live|study|test]` serves a pinned `include_str!` copy of `guide/hil-guide.md`; `skills/embarch-hil/SKILL.md` install is owed by umbrella's `embarch init`); `embarch-core` 109 (agent token plus person token, either authenticates, `Scope` request extension, nothing refused by scope; decision 93 gains a pointer); decisions 90 and 91 in `decisions/hil-shapes.md`. `tasks/api/162` set `open` (Unparks when: core/128); `tasks/ui/111` still waits on `api/162`.
- Least sure: (api/163) the drift test between the pinned guide and `suite/hil-guide.md` is silent until M1.13 writes the suite guide, and only checks with `embarch-doc` beside `embarch-api`. (core/128) `service.rs` install passes only `EMBARCH_TOKEN`, so an installed Windows service generates its own `person-token` in `ProgramData`; nothing reads it yet and the directory-ACL inference is unchecked. (study-designer/084) 03 makes an observation-prompt timeout `inconclusive` while `hil-shapes.md`'s closed `reason` list has no matching reason; left as a `Finding` comment on EMB-218 (M1.3, Fleet Ready).

### 16:07 — api/163 serve-the-hil-guide

**Merged:** `agent/api/163-serve-the-hil-guide` (code `97577b6`, ff on `origin/main` from `0d93709`; doc as-found `00ff3328`, resume `ca885d91`, cherry-picked onto `5d4b8ab2`, task file state line resolved by hand to `done`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 16:06 — core/128 agent-and-person-tokens

**Merged:** `agent/core/128-agent-and-person-tokens` (code `789cbfc`, ff on `origin/main` from `d4c9564`; doc as-found `a4f429c4`, resume `5d4b8ab2`, cherry-picked onto `59b55276`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, and the `icacls` lockdown on the new `person-token` file, unrun (a worktree cannot build natively); the task's closing note says how to check both from the main checkout on Windows. No board needed.

### 16:05 — study-designer/084 hil-file-shapes

**Merged:** `agent/study-designer/084-hil-file-shapes` (doc only: as-found `abb234ef`, resume `59b55276`, cherry-picked onto `a8c1d25f`; recovery doc commit `5322a69c`; notes and fragments `c937c8e0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 15:49 refresh.

---

## 2026-11-19 — 6 units

*Folded by the 2026-11-20 leg's `embarch-log-folder`: per-unit "Decided" reasoning, test tallies and "Least sure about" narrative dropped (git holds them); SHAs, Reviewer lines, debts and carry-forward items kept.*

**Carry forward:**
- **Spread sweep skip line, verbatim:** `Spread sweep: nothing filed (2026-11-18 23:20)`. No source path had a commit since; the refill gate fired on depth and spread at 04:10 and was skipped.
- **Background dispatch cuts a leg off.** The three legs before 00:02 dispatched workers in the background, ended their turn to wait, and were cut off (the 00:30 leg died mid-`atlas/090`, wrote no entry, left 247 uncommitted lines that were committed as found at `d80aa9f`). Foreground dispatch returned in about 3 minutes each (`087`, `088`, `089`, `090`). Filed **EMB-214** (Backlog, investigation); it names `.claude/leg.md` paragraphs, which are the owner's.
- **Bench `api/059` and `dev-bench/038` stay `open`**: neither `dev-bench` nor `dut` attached at 23:56 or 04:04. Fleet Ready empty. Atlas was the only scope with work; none left after `090`.
- **`suite/056` run by the supervisor** after its announcement window (`1795086320.551719`, 04:05, no `--action`, no reply by 04:35): `embarch.md` 23,314 to 22,735 B (reserve 23,040). Two stale facts corrected ("ten legs run", §6 "one entry per batch"). Possibly out of rule: the depth sweep was skipped by applying the spread-only skip's reasoning.
- Mid-day: 2026-11-18 folded (17 units) and 2026-11-14 rolled into `log-archive/` by the 00:02 leg; `check-client-names.py --suite --history` clean on 15 repos.
- Budget throughout: PROCEED, wave 6, 5-hour 0% to 79%, weekly 18% to 23%.

**Owner-side debts (in the task files, none need a board):** `doc regparse --template maxim` on the real datasheets (layout 3 optical-sensor, and the one that read 0 registers; real tables wrap their headers and descriptions, so a summary-table row regex may report `no_summary_row`); `doc regparse --template ti` on the real datasheet; `mcu rm-outline` and `mcu vote` on the real nRF54L-series datasheet.

---

### 04:37 — suite/056 compact-suite
**Merged:** `suite/056` (doc `670c15cc`, on `origin/main`; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 04:10 — atlas/090 maxim-bit-column-register-map (EMB-34, second half; recovery of the dead leg's worker)
**Merged:** `agent/atlas/090-maxim-bit-column-register-map` (code `d80aa9f`, ff on `origin/main` from `124dc60`; doc `2bd99b5d`, the worker's `2bff3d8c` cherry-picked onto `256cf62f`). Dead leg's claim `76a04e89`, reclaimed `0a31d1d5`. Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template maxim` on the real optical-sensor datasheet; only synthetic PDFs have exercised layout 3. Bench `api/059`, `dev-bench/038` stay `open` (neither `dev-bench` nor `dut` attached at 04:04).

### 00:22 — atlas/089 maxim-register-headings-with-a-hex-address (EMB-34, first half)
**Merged:** `agent/atlas/089-maxim-register-headings-with-a-hex-address` (code `124dc60`, ff on `origin/main`; doc `c04d874b`, ff on the leg worktree). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template maxim` on the real datasheet that read 0 registers; the synthetic table has one-line rows, while the real one wraps its `REGISTER NAME` header and its descriptions.

### 00:15 — atlas/088 read-ti-width-prefixed-binary-resets (EMB-33)
**Merged:** `agent/atlas/088-read-ti-width-prefixed-binary-resets` (code `85ee2b9`, ff on `origin/main`; doc `503fc4a6`, the worker's `22f8ea03` cherry-picked onto `14960676`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template ti` on the real datasheet, to see its resets and its 3 conflicts, which this unit does not claim.

### 00:09 — atlas/087 read-a-nordic-style-reference-manual (EMB-32)
**Merged:** `agent/atlas/087-read-a-nordic-style-reference-manual` (code `1948a8c`, ff on `origin/main`; doc `27a2efb5`, the worker's `19c8f474` cherry-picked onto `1439f6ea`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: one `mcu rm-outline` and one `mcu vote` run on the real nRF54L-series datasheet; the `ID` row's real column alignment, multi-letter field IDs and table rows unlike the issue's shape are unverified.

### 00:02 — atlas/086 check-the-pdo-decode-against-the-standards-tables (EMB-159; third-leg re-land)
**Merged:** `agent/atlas/086-check-the-pdo-decode-against-the-standards-tables` (code `69bf11f`, ff on `origin/main`; doc `2098422f`, the worker's `d0196cb2` cherry-picked onto `b74bfd51`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059`, `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 23:56 refresh.

---
*Days 2026-11-18 to 2026-11-18 rolled to [log-archive/supervisor-log-2026-11-18-to-2026-11-18.md](log-archive/supervisor-log-2026-11-18-to-2026-11-18.md).*
