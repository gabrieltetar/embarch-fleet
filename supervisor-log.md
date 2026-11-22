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

## 2026-11-22 03:23 — umbrella/102 init-on-an-initialised-repo-installs-what-it-lacks

**Decided:** nothing suite-wide. `embarch-umbrella` decision 60 (`decisions/integration.md`): `embarch init` on a repo whose `embarch/embarch.toml` already exists **exits `0`** where it exited `1`, never opens, parses or rewrites the config, and installs what it lacks of the rest: the `embarch-hil` skill (byte-compared with the pinned copy) and the two `.git/info/exclude` lines; a repo lacking nothing gets "Nothing to add" and no write, and `--dry-run` lists what it would add. The exit code is a contract change the decision argues for: the repo is already in the state `init` exists to reach, and a nonzero exit would make `--uninstall`, which deletes the edited config (decision 41), look like the cure; a script that relied on `1` can test for the file. **The MCP registration is not repaired on this path**: detecting it needs `claude mcp list`, whose output shape is not pinned, and re-adding a registered server errors, so the path prints the `claude mcp add` line instead. Decision 59's "Not covered" line now points at 60. I amended `embarch-api/open.md`'s skill line from the uninstall workaround to running `init` again. **This fold landed with `check-doc-size.py` red**: my first wording took the file to 3,963 of 5,120 B, inside the reserve with no debt filed, and I chained the gate through `| tail -1`, so `&&` saw `tail`'s exit and the fold and its push went ahead. Found on the output a minute later and fixed apart as `c10ea59a` (the line shortened, 3,877 B, gate 12/12); `origin/main` was red from `c1b23b9b` to `c10ea59a`, about a minute. Corrected in this entry after the fold. The reviewer noted, and dropped, that a hand-edited skill file reads as missing and is reinstalled over; first-run `init` already behaves that way and no decision forbids it.
**Merged:** `agent/umbrella/102-init-on-an-initialised-repo-installs-what-it-lacks` (code `27f43a5`, ff on `origin/main` from `b3d0106`; doc `55c42437`, the worker's `df48ddd8` cherry-picked onto `bc418c8a`). Re-gated on the merge result: `cargo build`, `cargo test` (280 passed), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a real initialised firmware repo, and the skill path `.claude/skills/<name>/SKILL.md` is still unconfirmed in a live Claude Code session: run `embarch init` twice in a scratch repo and confirm the agent lists `embarch-hil`.
**Budget:** PROCEED at dispatch, 5-hour 21%, weekly 62%, wave 6. This is the leg's fourth unit; the queue now holds no dispatchable task (bench `api/059` and `dev-bench/038` wait for their boards), so the next leg's refill fires on depth, and `core/open.md`, `embarch-api/open.md` and `embarch-umbrella`'s docs have moved since the 22:05 sweep.
**Least sure about:** the exit-code change from `1` to `0`: no caller in the suite reads it, but none outside it was searched for, and anything that treated `1` as "already initialised" now proceeds silently.

---

## 2026-11-22 03:22 — ui/112 the-study-designer-keeps-a-studys-measurements

**Decided:** nothing suite-wide. `embarch-ui` decision 104 (`decisions/study-authoring.md`): the Study Designer keeps a study's `measurements` and does not author them (deferred, stated in 104). Load returns the file's array verbatim; Save, Run and Pre-flight send it back, and a new `apply_measurements`, beside `build_authored` rather than inside it because the declarations are host-only and sealed by neither CRC, puts it on the built study after `validate_measurements`; a refusal is a `400` prefixed `measurements: `, the file on disk untouched, and Run and Pre-flight refuse the same way. The browser holds the array opaque and lists the names in the build-options summary, cleared on a project switch. `features.d/ui-025` amended (decisions 29, 30, 104). **On the reviewer's note I corrected the unit's code comments**, which cited `ui` decision 31 (Live Study) where 104 is meant: `embarch-ui` `b1b1a24`, comments only, re-gated green. This closes the gap I filed this task for at `suite/057`.
**Merged:** `agent/ui/112-the-study-designer-keeps-a-studys-measurements` (code `a9d7e95`, ff on `origin/main` from `279c33f`, then my `b1b1a24` on top; doc `fdfa45e8`, the worker's `24f6be14` cherry-picked onto `c9cf3216`). Re-gated on the merge result, and again after `b1b1a24`: `cargo build`, `cargo test` (320 passed, 4 ignored, plus 8), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The `app.js` change is exercised by no test and no browser drive, and no agent-written study has been opened and saved through the tab; the route test uses a hand-made `count` declaration over a GATT tap.
**Budget:** PROCEED at dispatch, 5-hour 21%, weekly 62%, wave 6.
**Least sure about:** the summary line sits inside the build-options area, so a person editing steps may never see that the study carries declarations they cannot edit here.

---

## 2026-11-22 03:20 — api/165 compact-api

**Decided:** nothing suite-wide. A verbatim split, no wording changed: `embarch-api/decisions/client-crate.md` 12,278 to 9,360 of 12,288 B, decisions 55 (one auth funnel) and 66 (the crate's home) moved to a new `decisions/client-crate-funnel.md` (3,470 B), index rows and the citations in `decisions/tests.md` and `spec/implementation.md` repointed; `interfaces/config.md` 11,368 to 7,945 B, the prose after the `[[projects]]` table (zephyr-west selection, `static` refusals, snippets, the build directory name, `target.json`) moved to a new `interfaces/config-selection.md` (4,175 B), with a pointer left and the `[core]` table and the `EMBARCH_PERSON_TOKEN` order kept in place. Decision 109 (no fallback to the agent's token, no CLI flag) stays in `client-crate.md` untouched. The worker's first split moved 62, 66 and 72 and broke `check-decision-refs.py`, because `history/api.md` and its archive cite 58, 62 and 72 at `client-crate.md` and a worker may not edit `history/`; it chose 55 and 66, which nothing in `history/` names. I closed the task `done` (the worker left it claimed). **Does `spec.md` alone answer what someone needs to work on `embarch-api` today?** Mostly: it says what the crate is, the mode switch, the Core boundary and every live invariant through the build claims, the ledger and the PDF render; it does not say that this repo hosts `embarch-core-client`, which `embarch-ui` and `embarch-umbrella` build against, nor its two token scopes, and a newcomer finds those only through `spec/implementation.md` and decision 109.
**Merged:** `agent/api/165-compact-api` (doc only, no code branch; doc `6b448201` and `569ca60a`, the worker's `54adc7d4` and `d6a708ee` cherry-picked onto `9cb0f77e`). Re-gated on the result: `check-docs.py` 12/12, `check-doc-size.py --pressure` lists neither file; ownership green on the branch.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch, 5-hour 21%, weekly 62%, wave 6.
**Least sure about:** `client-crate.md` is still 85% of its cap with 58, 62 and 72 pinned there by `history/` citations, so the next decision about the client crate refills it; moving those three needs the supervisor to repoint the history lines, and nothing files that.

---

## 2026-11-22 03:19 — core/132 measurements-at-a-studys-end

**Decided:** nothing suite-wide. `embarch-core` decisions 113 to 115 (`decisions/measurements.md`, `interfaces/measurements.md`): Core turns on the shared crate's `reducers` feature and, as a device study ends and before the record is sealed, computes every declared measurement over its own captures and writes `measurements.json`, so the file is a signed subject (decision 110 already named it); a run whose measurements cannot be written fails, as an unsignable one does. A study that declares none writes no file; a failed study and a host study compute nothing. `validate_measurements` now runs at submission beside `validate_record_checks`. **The three things `suite/057` left to this unit**: every point is on Core's receipt stamp (`core_rx_utc_ms`), never the record's `rx_utc_ms`; the window is the capture's span, first stamp to last; **a marker is the first whitespace-delimited word of a line in any `Text` tap**, stamped by the arrival row covering that line's first byte, its `u_ms` undeclared. `by`, `instrument` and `bench_image` come from the tap (`GattNotify` and a signal leaving role `dut` are the DUT's word, everything else `bench`, `bench_image: unverified`, `identity: null`); a study's declared resolution and `U` are honoured for DUT values only (`u_source: study`), bench values read `u_source: undeclared`. `rate_check` agrees within `0.05 + 2/(n-1)` of the declared rate, tagged **[assumed]**. `declared_by` carries a `study_value` entry with the submitting token's scope (`SealJob` gained `submitted_by`; `POST /study` takes the `Scope` extractor). Whole-number floats are written as integers for RFC 8785. The reviewer read decision 113's clock against the crate's decision 90 ("the clock of `rx_utc_ms`") and judged it a refinement, not a contradiction: in a study `rx_utc_ms` is dev-bench uptime, so only Core's stamp is epoch. `open.md` took its edit in spare bytes (269 B from the reserve line), so `core/133` stays parked. **Leg setup, to carry:** step 0 found no claim, no `agent/*` branch and no unit worktree in any repo, only the clean leg worktree the 22:33 leg (dead on a 5-hour 429) left, reused at `origin/main`; Fleet Ready had nothing to split (EMB-223, 225, 226 waiting on blockers); bench `api/059` and `dev-bench/038` stay `open` (neither `dev-bench` nor `dut` attached at the 03:02 refresh). The refill gate fired spread only (4 scopes, wave 6); **I skipped the sweep without a `nothing filed` marker to point at**: the newest is `2026-11-18 23:20`, but every source commit since it predates the 22:05 leg's sweep, which read them and filed `umbrella/102`, and none has moved since. Four workers went out as four foreground `Agent` calls in one message and all four reported to this leg (120 s to 500 s). This unit also commits the 2026-11-21 day fold, rolls 2026-11-19 into `log-archive/`, and ran `check-client-names.py --suite --history`: clean on all 16 repos.
**Merged:** `agent/core/132-measurements-at-a-studys-end` (code `f16a35b`, ff on `origin/main` from `99a3e7c`; doc `b134f58f`, the worker's `71505591` cherry-picked onto `38b28a75`). Re-gated on the merge result: `cargo build`, `cargo test` (426 passed, 2 ignored, plus 2), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). No real study's captures have been reduced: run a study with a `rate` and an `interval` over a bench console, then read `measurements.json` for the arrival granularity and the rate tolerance (recorded in `embarch-core/open/never-exercised.md`). A `study_value` scope from a person token has never been seen end to end.
**Budget:** PROCEED, 5-hour 0% at the start and 21% at dispatch, weekly 62%, wave 6.
**Least sure about:** the `rate_check` tolerance is a guess, and the reducer's `rate` is `n/T` over a first-to-last window, which reads high by one interval in `n-1`; the first real capture is the check, and nothing schedules it.

---

## 2026-11-21 — 11 units

*Folded by the 2026-11-22 leg: per-unit narrative, gate lists and budget lines went; SHAs, reviewer lines and hardware debts kept, one line per unit. `git log` holds the reasoning.*

**Carry forward:**
- **Suite-wide, by the supervisor, under the 17:10 announcement (`ts 1795306202`; no reply, window closed 17:40): host-type schema bump, `HOST_TYPE_SCHEMA_VERSION` 21 to 22, wire 15 unchanged** (`suite/057`: `Study.measurements`, up to 32 `MeasurementDecl`, always compiled, nothing skipped when empty because `Study` travels as postcard). **A deploy, the owner's:** Core, `embarch-api` (restart the MCP server) and `embarch-ui` refuse each other across 21 and 22 until all three are rebuilt from `main`; `embarch-umbrella` `doctor` check 11 warns until it is too. The running MCP binary is stale from this commit on.
- **Deploy order: Core first.** The next `embarch-ui` deploy does not start without a readable person token, which a Core from `core/128` on writes at first start. Core before UI.
- Filed or opened this day: `tasks/ui/112` (the UI save handler drops a study's declarations), `tasks/core/132` open (calls `validate_measurements` at submission, window time bounds, what a marker is), `tasks/umbrella/102` open (an already-`init`ed repo gets no skill; the workaround deletes the engineer's config), `tasks/api/165` open (compact `client-crate.md`, `interfaces/config.md`, due 2026-11-28), `tasks/core/133` blocked (compact `open.md`), EMB-238 (now `api/166`, landed), EMB-239 (now `core/134`, landed). Owed and unfiled: `plot_ticks` into the shared crate (best with M1.11, which must call the Rust one); whether `run_host_study` takes an optional `project`; a missing-person-token banner in the UI.
- `fold-commit.py` does not stage `notes/` (already recorded 2026-11-20); the `api/164` fold's `notes/hil/06` edit landed apart as `dc7b3757`.
- Two decisions to remember: `embarch-core` decision 112, the first refusal by scope (the agent's token gets `403` discarding a failed, errored, inconclusive or published run's captures), proven so far only in Core's own tests; `POST /auth/challenge` takes no token and sits outside decision 42's route sweep. Signed-challenge step before a client sends any token (Core decision 110's route) is in no task; name it when M1.10 is split.
- Spread sweep, carried verbatim for the refill skip: `Spread sweep: nothing filed (2026-11-18 23:20)`. A later sweep this day (17:32 and 22:14 units) read only `embarch-api/open.md`, `embarch-core/open.md` and `embarch-token.md` since it, and filed `umbrella/101`, then `umbrella/102`.
- Recovery: the 17:01 leg died on a 5-hour 429 at about 17:38 before `fold-commit.py`; the 22:05 unit finished its dirty worktree. A leg that dies between merging code and folding docs leaves `history/` and `features.md` behind the shipped binary.
- Workers: foreground `Agent` calls in one message run concurrently and each reports to its own leg (EMB-214's pattern); background calls (22:08) also reported to this leg.

### Units

**suite/057 a-study-declares-its-derived-measurements (22:31)**
**Merged:** `agent/suite/057-a-study-declares-its-derived-measurements`, §8 order: `embarch-study-designer` `d6230ad` (ff from `1238def`), `embarch-core` `99a3e7c` (ff from `9a9d31a`), `embarch-api` `2f7550d` (ff from `069e892`); doc `9e5e5301` (`e4de7d76` cherry-picked onto `af0b4e7e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** **a deploy, the owner's**: Core, `embarch-api` (restart the MCP server) and `embarch-ui` refuse each other across 21 and 22 until all three are rebuilt from the new `main`, and `embarch-umbrella`'s `doctor` check 11 warns until it is too. The running MCP binary is stale from this commit on. No board needed.
**Least sure about:** declaring values per measurement rather than per tap lets two declarations over one tap state different sample rates; nothing refuses the disagreement (`core/132` reports each `rate_check` separately).

**api/166 send-build-claims-when-a-study-starts (22:20)**
**Merged:** `agent/api/166-send-build-claims-when-a-study-starts`, code `069e892` (ff from `b2afdf5`); doc `9d20f924` (`e221d851` cherry-picked onto `1322a2eb`). `embarch-api` decision 111; `build_dirty` ignores untracked files.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The MCP `run_study` path is untested end to end (no harness drives the MCP subprocess; it shares `build_claims::for_project` with the CLI, which is tested against a mock Core), and nothing has sent a claim to a real Core.

**core/134 retention-holds-when-the-run-log-cannot-be-read (22:14)**
**Merged:** `agent/core/134-retention-holds-when-the-run-log-cannot-be-read`, code `9a9d31a` (ff from `c3414e4`); doc `d4b39eaf` (`5fd3437b` cherry-picked onto `0daa1ff6`). Leg setup claim `1822a2eb`. `GET /studies` answers `keep: 0` on an unreadable log, the opposite of what retention does; the UI does not read `keep`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). No board needed. The `error` log line itself is not asserted by a test (no log-capture crate in `embarch-core`).

**umbrella/101 init-installs-the-hil-skill (22:05, recovery fold)**
**Merged:** `agent/umbrella/101-init-installs-the-hil-skill`, code `b3d0106` (ff from `ed5d14b`, landed by the 17:01 leg); doc `7ca69785` (`305c0c0c` cherry-picked onto `2d8d5f1a`). `tasks/umbrella/099` closed `done`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill path `.claude/skills/<name>/SKILL.md` is `[assumed]` and has not been loaded in a live Claude Code session: run `embarch init` in a scratch repo and confirm the agent lists `embarch-hil`.

**ui/111 ui-calls-core-with-the-person-token (17:37)**
**Merged:** `agent/ui/111-ui-calls-core-with-the-person-token`, code `279c33f` (ff from `d824791`); doc `4cca5341` (`f38d3517` cherry-picked onto `dc6dabeb`); note edit `dc7b3757`. No fallback to the agent's token; the UI stops at start naming the token's sources (worker's departure from the task, accepted).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. **A deploy ordering debt**: the next `embarch-ui` deploy does not start unless the UI can read a person token, which a Core from `core/128` on writes at its first start; deploy Core first. Not run against the installed `embarch-ui.service` or a real Core, and the missing-token test passes without checking the error on a machine that has a `person-token` file.

**api/164 render-a-report-to-pdf-offline (17:35)**
**Merged:** `agent/api/164-render-a-report-to-pdf-offline`, code `b2afdf5` (ff from `c9f0c79`); doc `9fa11640` (`1676e029` cherry-picked onto `4567439a`). Typst behind cargo feature `pdf`, default on; release binary 21.5 MB to 84.3 MB; `embarch-study-designer` decision 91 amended.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** byte identity across machines unmeasured, and `verify` (M1.11) rests on it; nothing schedules a second-machine render.

**core/131 hash-chained-run-log (17:32)**
**Merged:** `agent/core/131-hash-chained-run-log`, code `c3414e4` (ff from `4f5dcc4`); doc `13a86f36` (`a9ceacf8` cherry-picked onto `fbc0af1a`). `embarch-core` decisions 111 and 112; `tasks/core/130` closed `done`; `suite/057` announced at 17:10.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `run-log.jsonl`, unrun (a worktree cannot build natively). No board needed.

**api/162 core-client-resolves-both-token-scopes (12:41)**
**Merged:** `agent/api/162-core-client-resolves-both-token-scopes`, code `c9f0c79` (ff from `97577b6`); doc `b407e472` (`21f92513` cherry-picked onto `0eacb879`). `embarch-api` decision 109; no CLI flag selects the person scope.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The WSL2 `person-token` path has not met a live Core.

**study-designer/086 hil-verdict-rules (12:38)**
**Merged:** `agent/study-designer/086-hil-verdict-rules`, code `1238def` (ff from `17332cf`); doc `5d512fb4` (ff from `e559e851`). Decisions 95 to 98; `tasks/study-designer/087` paid and closed `done`. Decisions 97 and 98 meet real data first in the Test phase; a disagreeing reading costs a behaviour version.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**core/129 sign-study-run-records (12:27)**
**Merged:** `agent/core/129-sign-study-run-records`, code `4f5dcc4` (ff from `789cbfc`); doc `f85141d6` (`4ebfeb1e` cherry-picked onto `c75b26a2`). `embarch-core` decision 110, Ed25519 (`ed25519-dalek` 2); the declarations ledger is in memory, so a record after a Core restart vouches only from `witnessed_since_utc_ms` until M1.6's store persists it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `signing-key`, unrun (a worktree cannot build natively); the task's closing note, now in `embarch-core/open.md`, says how to check both from the main checkout on Windows, and that a second start must reuse the key. No board needed.

**study-designer/085 hil-reducers (12:25)**
**Merged:** `agent/study-designer/085-hil-reducers`, code `17332cf` (ff from `f6cca94`); doc `ffe5c599` (ff from `731d60a0`). Decisions 92 to 94; the percentile's type-A convention is unmeasured. Also committed the 2026-11-20 fold; `check-client-names.py --suite --history` clean on all 16 repos. Spread of the HIL M1 issues in Fleet Ready (`d7ae8e5b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 12:06 refresh.
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

*Days 2026-11-19 to 2026-11-19 rolled to [log-archive/supervisor-log-2026-11-19-to-2026-11-19.md](log-archive/supervisor-log-2026-11-19-to-2026-11-19.md).*
