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

## 2026-11-26 18:43 — api/207 the-client-status-carries-cores-mode-and-keyid

**Decided:** nothing suite-wide. **New api decision 139** (`decisions/client-crate.md`): the shared client's `StatusResponse` gains `mode` and `keyid` (core decision 129), each `Option<String>` with `#[serde(default)]`; `None` means a Core that predates them and reads as unknown, never `service`. No `skip_serializing_if`, so where `embarch-ui` re-serializes the status a `None` now emits `"mode":null` and `"keyid":null`, like the struct's other optional fields. Interface line in `interfaces/tools-lease.md`; `spec.md` untouched. **Shared crate, diff read before landing:** two additive `pub` fields and one test; no consumer builds `StatusResponse` by literal (the worker's grep and mine over `embarch-ui`, `embarch-umbrella`, `embarch-api`). **Worker filed EMB-580** (ui, Fleet Ready): the UI's Core identity line (ui decision 112) should read the reported `mode` instead of inferring it from the attestation match; `embarch-ui/src/snapshot.rs`'s comment that the client drops these fields is now stale and that issue covers it. **New size debt:** `tasks/api/209-compact-api.md`, `client-crate.md` at 11,808 of 12,288 B, `blocked`, In flux: yes (the client keeps gaining fields as Core's bodies grow), due 2026-12-26.
**Merged:** `agent/api/207-the-client-status-carries-cores-mode-and-keyid` (code `94be2fa`, ff from `37e5289`; doc `895aeec3`, the worker's `e5b4863e` cherry-picked). Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (592 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean. Consumer: `embarch-ui` built from a gate-only worktree (`.worktrees/gate-207/`, its `embarch-api` link at the branch): `cargo test` 364 passed, 4 ignored, 0 failed; clippy clean. `embarch-umbrella` not built: no literal, and the fields are additive. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. Nothing has read `mode` or `keyid` from a live Core through the client.
**Budget:** PROCEED at leg start (5-hour 23%, weekly 29%, wave 6); PROCEED at this fold (5-hour 30%, weekly 30%).
**Least sure about:** the `null` keys a re-serialized status now carries: the UI's tests pass, but whether any page script treats a present-but-null `mode` differently from an absent one was not read.

---

## 2026-11-26 18:42 — core/173 a-test-runs-amended-study-record-is-bound-in-the-run-log

**Decided:** nothing suite-wide. **Split this leg from Fleet Ready, at `e2ff47f5`:** EMB-579 into `core/173` (this unit), EMB-372 into `core/174` (manual verdict, unit serial, person's name; heads the HIL chain), EMB-374 into `api/208` (verify re-evaluates step outcomes), EMB-461 into `chat/050` (`verify-only`, a container login; the owner may strike it). **EMB-317 closed as Done**: its `doc/102` and `api/190` had both landed, but its 2026-11-24 move to Fleet Working hit Linear's cap, so it sat in Fleet Ready reading unsplit. **New core decision 146** (`decisions/test-run-record.md`), fixing the contradiction the `core/170` reviewer found (EMB-579): **the amend stays and the amended hash is bound in the chain.** The `test_run` run-log entry gains `study_records: [{study_id, record_sha256}]`, each hash taken after `amend_studies`; `study_ids` stays, derived from it, so retention is unchanged. The binding entry for a study is the latest `test_run` entry naming it with a non-null hash, else its `run` entry (a plain study, or one whose amend failed): `RunLog::bound_record_sha256`. Readers after the change: `GET /study/{id}/log` gains a `record_sha256` field carrying the bound hash; publish's `report-data.json` `record_sha256` reads the bound hash; publish's "has a signed record" check still reads the `run` entry's non-null hash. The worker kept the amend because the study's own signed record is what gets published, and a verdict only the Test run's record states would be an unsigned claim about the study. 145 and 111 carry pointers to 146 (111 used about 95 of its 120 B).
**Merged:** `agent/core/173-a-test-runs-amended-study-record-is-bound-in-the-run-log` (code `018a6e7`, ff from `b2e195d`; doc `33667240`, the worker's `bcb22408` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (612 passed, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board beyond `core/170`'s (one real Test run, under the lease, whose amended records verify); that run should now also show each study's `test_run` hash equal to its file. The native Windows build of Core. **Deploy debt:** the installed Core writes no `study_records` until redeployed.
**Budget:** PROCEED at leg start (5-hour 23%, weekly 29%, wave 6); PROCEED at this fold (5-hour 30%, weekly 30%).
**Least sure about:** a Core crash between a study's `run` entry and the Test run's `test_run` entry leaves the sealed hash bound and the run sealed `interrupted` with its studies unamended; 146 says so but no test covers it, and whether `embarch-api` or `embarch-ui` reads `GET /study/{id}/log` with strict unknown-field rules was not checked.

---

## 2026-11-26 18:08 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind

**Decided:** nothing suite-wide. **The modal half of `ui/124` landed, so the task is done** (the go card landed at 14:18, ui decision 111). **New ui decision 113** (`decisions/operator-prompt.md`, now 10,701 B, out of reserve): the prompt's kind is read from `GET /study/{id}`'s `pending_prompt`, not the event (api decision 137, until EMB-577 lands as `core/172`): on each `PromptPending`, `follow` spawns one `get_study_status` read, and when the same prompt id has a `kind` it sends a second `prompt` frame; `pmAdd` redraws the open modal in place, never while an answer is sending or after the prompt ended, and a failed read leaves the modal with no kind line. `prompt_json` carries `kind`, `observation` and `switched_on` (null, null, empty for a host study, whose modal is unchanged). The modal shows a kind line (an observation or a clearance says only the person answers it) and each output Core switched on; an observation's declared answers are buttons in place of Confirm, a number-only observation gets a number field in its unit stepping by its resolution, and an empty or non-numeric number is not sent. `POST /api/live/prompt` takes an optional `value` sent on a confirmed answer only; Core's refusals keep the modal open (107). Decision 111's "not done here" line now points at 113. **How I resumed it:** the branches survived the first half, so I dispatched onto them (no `-b`): the code branch fast-forwarded to `origin/main`, and the doc branch took a merge of `origin/main` whose tree equals main (`b65f3f9c`; the first half's commit was already on main as `4d6ec789`), so nothing was force-pushed; only the worker's own doc commit was cherry-picked.
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `62dd46a`, ff from `59c5e5a`; doc `95fedf4a`, the worker's `6c06a896` cherry-picked). Re-gated on the merge result, built against the landed `api/205` client: `cargo build`, `cargo test --no-fail-fast` (364 passed, 4 ignored, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/ui-142-prompt-kind-modal.md` was assembled into `suite/features.md` in `dev-bench/053`'s fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. The modal has not run in a browser, and `tests/browser/drive_prompt.py` and `stub_core.py` do not cover an observation prompt, so a driven check of kind, choices and a number answer is owed; whether Core's study record already holds the prompt when the event arrives is unmeasured (if not, the kind line waits for the next frame). **Deploy debt:** the installed embarch-ui shows no kind line until rebuilt.
**Budget:** PROCEED at leg start (5-hour 13%, weekly 28%, wave 6); PROCEED at this fold (5-hour 22%, weekly 29%).
**Least sure about:** the page refuses an empty or non-numeric number itself, which the reviewer read as an input-shape check rather than a copy of a Core rule (decision 107 rejected the page copying Core's blank-field rule); it is a line the owner may read the other way.

**Leg end, to carry:** 4 of 4 units landed in one wave (claimed 17:43, all four reported by about 17:55, the slowest api/205 at about 11 minutes): `api/205`, `core/170`, `dev-bench/053`, `ui/124`; none blocked. **Split this leg, at `a429277b`, all `filed` (Fleet Working):** EMB-576 to `api/207` (client `StatusResponse` gains `mode`, `keyid`; a shared-crate struct field, so the landing leg builds `embarch-ui` and `embarch-umbrella` against it), EMB-577 to `core/172` (the PromptPending kind collision), EMB-578 to `chat/049` (the ghost-text pause check under load). **Done in Linear this leg:** EMB-375, EMB-369, EMB-388, and EMB-384 once `finish` reads this fold. **EMB-369 Done unblocks EMB-370 and EMB-372** (now splittable, both core), and EMB-372 heads the chain behind it (EMB-373, 378, 379, then 380 to 382 and 390). **New issue by a reviewer: EMB-579** (core, Fleet Ready): a Test run's amended study record no longer matches the hash the run log chained (core decision 111); worth taking with or before the next core unit. **Dispatchable now:** `api/207`, `chat/049`, `core/168`, `core/172`, `ui/123`, `ui/126` (four scopes); Fleet Ready 19 unsplit (including EMB-370, 372, 579), 12 waiting. Refill was owed on spread only at leg start; I split Fleet Ready rather than sweep `open.md` (21 source commits since the last `Spread sweep` line, 2026-11-24 00:23, so a sweep was due by the rule), so no `Spread sweep` line. **Size debts:** none overdue, none new; six files in reserve, all filed. **Hardware buffer refreshed at 17:40:** Core reachable, dev-bench and DUT not attached; bench tasks `api/059` and `dev-bench/038` stay `open`. **Still unclassified:** `embarch-analog-capture-proposal.md`, the owner's. **Budget at leg end:** PROCEED, 5-hour 22%, weekly 29%.

---

## 2026-11-26 18:06 — dev-bench/053 pd-bench-reports-pd-timings-on-its-own-clock

**Decided:** nothing suite-wide. **New dev-bench decision 69** (`decisions/pd-bench.md`): a new `pd times` command, chosen over extra `pd status` lines so a test parsing one interval does not have to find it among unrelated lines (the owner may strike it). It prints up to 8 events, `event <name> <us>`, oldest first, then one `<name> <us>` line per interval, then `pd: ok`; `pd idle` clears the stamps. Stamps are the bench's uptime in microseconds from `k_uptime_ticks()` (`k_ticks_to_us_near64`). Events and where each is stamped: `attach` (a new power-role start with no partner held), `src_caps` (`SOURCE_CAPABILITIES_RECEIVED`), `request` (`policy_get_rdo`, before the Request is on the wire), `accept` (`MSG_ACCEPT_RECEIVED`), `ps_rdy` (`TRANSITION_PS`), `hard_reset_sent` (when queued, from `pd hardreset` and `pd idle`), `hard_reset_received` (`HARD_RESET_RECEIVED` on a DRP build, or `SNK_TRANSITION_TO_DEFAULT` when the bench did not send it), `keepalive_stopped` (the first PPS keep-alive due and skipped under `pd keepalive off`, one 8 s period after the last Request). Intervals `attach_to_src_caps`, `request_to_ps_rdy`, `keepalive_stopped_to_hard_reset` run from the last start event to the last end event; a missing end or a start after the end gives no line. The arithmetic is in `pd_logic.c` (`PdLogicInterval`, `PdLogicTimesAdd`), stamps taken in `main.c` under a `times_lock`. `cmd_hardreset` now calls `hard_reset_request()` directly with unchanged output. `spec.md` not written (in reserve, `dev-bench/052` blocked).
**Merged:** `agent/dev-bench/053-pd-bench-reports-pd-timings-on-its-own-clock` (code `e3a73a0`, ff from `06ef18d`; doc `41aa818c`, the worker's `5e5ab03e` cherry-picked). Re-gated on the merge result from the main checkout's `workspaces/pd-bench` with the suite's `.west-venv` west: `west twister -T <worktree>/pd-bench -p nucleo_g0b1re` built both shields (SNK1M1, DRP1M1), `west twister -T <worktree>/pd-bench/tests/logic -p native_sim` 23 of 23 passed, `python3 -m unittest discover scripts` 9 passed. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/dev-bench-053-pd-times.md` assembled into `suite/features.md` in this fold, along with `ui/124`'s `ui-142-prompt-kind-modal.md`, whose doc commit landed before this fold ran `build_features.py`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on each shield: compare `pd times` with a probe on CC (attach, `pd max`, `pd keepalive off` against a PPS source, then `pd times`); record which callback stamps each event and so what each interval includes; record the kernel tick's resolution on the G0B1 and switch to `k_cycle_get_32` if it is coarser than the 100 us a PD timing needs; confirm a Hard Reset the bench sends is never stamped as received, on both roles (`tasks/dev-bench/053`, retired in this fold).
**Budget:** PROCEED at leg start (5-hour 13%, weekly 28%, wave 6); PROCEED at this fold (5-hour 22%, weekly 29%).
**Least sure about:** the tick resolution: Zephyr's default tick on this part may be far coarser than a microsecond, so every interval `pd times` prints may be quantised well above what a PD timing limit needs, and nothing host-side can tell.

---

## 2026-11-26 18:03 — core/170 a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against

**Decided:** nothing suite-wide. **New core decision 145** (`decisions/test-run-record.md`, beside 144): a study is sealed before it is judged, so when a Test run ends Core **amends** each of its studies' `record.dsse.json` just before the run's own record (144) hashes it: `Sealer::amend_for_test` keeps every other byte of the Statement, adds `predicate.test`, adds `run.json` to the subjects (sorted) and signs again. `predicate.test` carries `run_id`, `test_id`, `bench`, `definition_hash`, `run_index`, `run_count`, `note`; `run` (this study's verdict, null when none was judged) and `verdict` (the test's), each `{verdict, reason, qualifiers}`; from the smoke check `unit_key`, `images` (DUT and bench boards), `identities` and `instruments` (`*IDN?` replies), null when the bench was never checked; and `prompts` read from the study's `events.json` with `answered_by` and `answered_scope`. A plain study is never amended. An amend that fails is logged and leaves the record as first sealed. **The worker's own calls:** no board hello-line reply carried; `observed.behaviours` not copied into `test` since the record already has it. **The reviewer found a real contradiction, filed as EMB-579 (Fleet Ready):** core decision 111 binds the run log's `run` entry to the hash of `record.dsse.json` and calls a replaced record a mismatch, and the chained hash is written when the study ends, so every study record amended at a Test run's end no longer matches its logged hash. 145 does not say so and 111 stands. Its suggested fix is to chain the amended hash (for example in the `test` entry) and amend 111 and 145; I did not revert, since the merge is additive and a revert would lose the per-test record the HIL chain waits on. **EMB-369 is now Done in Linear** once `finish` runs (its last task), which unblocks EMB-370 and EMB-372.
**Merged:** `agent/core/170-a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against` (code `b2e195d`, ff from `81ab021`; doc `44740e1a`, the worker's `444a6b22` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (611 passed, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-390-test-study-record-verdict.md` was assembled into `suite/features.md` in `api/205`'s fold, because its doc commit had landed before that fold ran `build_features.py`.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-579
**Hardware debts:** one real Test run on a bench, under the lease: the DUT's and each bench board's image status, the identities and `*IDN?` replies, and an answered observation prompt's scope reach the amended record, and it still verifies. The native Windows build of Core. **Deploy debt:** the installed Core amends no study record until redeployed.
**Budget:** PROCEED at leg start (5-hour 13%, weekly 28%, wave 6); PROCEED at this fold (5-hour 20%, weekly 29%).
**Least sure about:** whether re-signing an already-sealed record is the design the owner wants at all, rather than sealing a study's record once after the verdict is known; EMB-579 fixes the run-log mismatch either way, but the choice between those two is a decision, not a bug fix.

---

## 2026-11-26 18:02 — api/205 declare-instrument-passes-metrology-and-calibration

**Decided:** nothing suite-wide. **New api decision 138** (`decisions/instruments.md`): `declare_instrument` takes `metrology` (a list), `calibration` and `clear_calibration`; `declare-instrument` takes `--metrology '<json>'` (repeatable), `--calibration '<json>'`, `--clear-metrology` and `--clear-calibration`; both surfaces parse one struct in `embarch-topology`'s `Instrument` shape (`U` upper-case, `basis` one of `datasheet`, `certificate`, `declared`). A `calibration.certificate` is a file path read here and sent as its SHA-256 only. Malformed dates, a negative `U` or resolution and an inverted range are refused by topology's own `Instrument::check` before Core is called (no second validator); an unknown `basis` or an unreadable certificate is refused too. **The worker's own call, not in the task:** decision 97's re-declare rule now covers the new blocks, since `PUT /instruments` replaces by name: an omitted block keeps the stored one, an empty list or a clear flag drops it, so the declare reads `GET /instruments` unless `safe_off`, `metrology` and `calibration` are all given. `tests/safe_off_cli.rs`'s "a clear needs no read" case now clears all three. **Shared crate, diff read before landing:** `embarch-core-client` gained `pub use` re-exports of topology's `Calibration`, `Metrology`, `MetrologyBasis` and `MeasuringRange`, additive, no struct fields; no consumer glob-imports the client, and `embarch-ui` built and passed against it in `ui/124`'s gate.
**Merged:** `agent/api/205-declare-instrument-passes-metrology-and-calibration` (code `37e5289`, ff from `f2156f1`; doc `168f3fca`, the worker's `23285338` cherry-picked). Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (591 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/api-326-instruments.md` (amended) assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. Nothing has declared metrology or calibration to a live Core, and what Core stamps on a measurement from a declared `U` was not read back.
**Budget:** PROCEED at leg start (5-hour 13%, weekly 28%, wave 6); PROCEED at this fold (5-hour 20%, weekly 29%).
**Least sure about:** a declare that gives `safe_off` and omits metrology or calibration now reads `GET /instruments` first where it used not to, and a failed read stops it, so the rule protects stored values at the cost of one more way for a declare to fail.

---

## 2026-11-26 17:36 — api/206 the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value

**Decided:** **one cross-repo landing by my own hands, announced and parked first** (`#embarch-fleet` ts `1795737738.383629`, 30 minutes elapsed with no reply): adding `value` to `PromptAnswerRequest` and two fields to `StudyEvent::PromptPending` broke two struct literals in `embarch-ui`, so I landed `api/206` and then a three-line `embarch-ui` commit of my own (`value: None` in the answer route's literal; `observation: None, switched_on: Vec::new()` in a test helper), gated against the branch's crate before either push. My task file had told the worker "additive fields only", which a new `pub` field on a struct some consumer builds by literal is not; that was my miss in the split, not the worker's. **New api decision 137** (`decisions/client-crate.md`): `PendingPrompt` gains `kind` (the study designer's `PromptKind`), `observation` (JSON) and `switched_on` (`SwitchedOn {target, line, step}`), each defaulted and skipped when absent; `StudyEvent::PromptPending` gains `observation` and `switched_on` **but not `kind`**, because Core flattens the prompt's `kind` onto an event whose serde tag is also `kind`; a Test run's event carrying both is refused by the client as a duplicate field (pre-existing, filed by the worker as **EMB-577**, core, Fleet Ready), so a prompt's kind is read from `GET /study/{id}`'s `pending_prompt`. `PromptAnswerRequest` gains `value`, skipped when `None`. A host study's prompt and answer are byte for byte as before (`tests/prompt_types.rs`). **In this fold: `ui/124` unparked to `open`**, its `## Blocked` section extended with both points (kind from the polled prompt until EMB-577; the literal already carries `value: None`).
**Merged:** `agent/api/206-the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value` (code `f2156f1`, ff from `8f0ba84`; doc `0831bbc2`, the worker's `c88a9aba` cherry-picked). Consumer commit `embarch-ui` `59c5e5a` (ff from `e5edeac`), mine. Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (585 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean. Both consumers built against the branch's crate from gate-only worktrees (`.worktrees/gate-206/`, their `embarch-api` link pointed at the branch): `embarch-ui` with the fix 362 passed, 4 ignored, clippy clean; `embarch-umbrella` unchanged 371 passed, clippy clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the api and ui trees. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. Nothing has met a live Core's Test run prompt through the client.
**Budget:** PROCEED at leg start (5-hour 39%, weekly 25%, wave 6); PROCEED at this fold (5-hour 10%, weekly 28%).
**Least sure about:** whether a three-line consumer update counted as the kind of cross-repo change that needs the 30-minute window; I treated it as one, which cost about 25 minutes of an idle leg, and the alternative reading (a trivial in-scope fix at landing) would have let it land with no announcement at all.

**Leg end, to carry:** 4 of 4 units landed in one wave (claimed 14:29), none blocked: `core/169`, `ui/125`, `chat/048`, `api/206` (with my `embarch-ui` consumer commit `59c5e5a`). **The wave was a 150-minute barrier**: `ui/125` reported in about 9 minutes, `core/169` in 19, `api/206` in 32 and `chat/048` in about 150 (a flake hunt under load), so three finished units sat unlanded for two hours; the foreground call ticks nothing while open, and the watchdog did not fire. **Split this leg, at `dbf2088a`, all `filed` (Fleet Working):** EMB-369 to `core/169` (landed) and `core/170` (now `open`), EMB-575 to `api/206` (landed, Done), EMB-388 to `dev-bench/053` (`verify-only`, `open`; `embarch-dev-bench/spec.md` is in reserve with its compaction blocked, so its dispatch note owes the reserve line). **New issues by workers, all Fleet Ready:** EMB-576 (api: `StatusResponse` drops Core's `mode` and `keyid`; `ui/125`'s line infers `service` from the match until it lands), EMB-577 (core: a Test run's `PromptPending` event carries `kind` twice and the client refuses it), EMB-578 (chat: the ghost-text pause check fails under load). **EMB-369 stays in Fleet Working** until `core/170` lands; once it is Done, EMB-370 and EMB-372 unblock and the HIL Test chain behind them moves. **Dispatchable now:** `api/205`, `core/168`, `core/170`, `dev-bench/053`, `ui/123`, `ui/124`, `ui/126` (four scopes); Fleet Ready 18 unsplit plus the 3 new, 14 waiting. Refill was owed on spread only at leg start; I split Fleet Ready rather than sweep `open.md`, so no `Spread sweep` line. **New size debt:** `core/171` (`embarch-core/open.md`, blocked In flux: yes, due 2026-12-10); `spec/tabs.md` now 906 B from its cap. None overdue. **Hardware buffer refreshed at 14:26:** Core reachable, dev-bench and DUT not attached; bench tasks `api/059` and `dev-bench/038` stay `open`. **Still unclassified:** `embarch-analog-capture-proposal.md`, the owner's. **Budget at leg end:** PROCEED, 5-hour 10% (reset at about 16:50), weekly 28%.

---

## 2026-11-26 17:09 — chat/048 the-cards-checks-pass-under-load

**Decided:** nothing suite-wide. **The 💡 cards flake (EMB-574) was the test, not the product**, by the worker's measurement, unlike `chat/047`'s: the page posts its `cards` request every time, 2 s after the draft moves, but `waitAssist` kept its 5 s deadline on the runner's clock between polls, so one slow driver reply under load ended the wait with no further poll. Evidence: 6 of 6 sampled failures still held the request on the page when asked afterwards. **New chat decision 120** (`decisions/assistant.md`): `waitAssist` is now one async script that polls the page's own posts against a deadline on the page's clock, 15 s. No product code changed. **The evidence is thinner than the task asked for, and the worker says so:** one burst of 11 failures in 20 runs at a 5 s page-clock deadline went unexplained (its logs were lost), which is why the deadline is 15 s rather than 5; the fix-removed failure is an injected 6 s runner stall, not a natural run (a natural loaded run with the fix removed failed 0 of 12 in later batches); no parallel `cargo test` was in the load. Before: 6 of 12 loaded runs red; after: 23 of 24 green, the one red a different flake, filed as **EMB-578** (the ghost-text "not before the pause" check). `npm test` hung once under the worker's busy loops in a wire test and was not looked into.
**Merged:** `agent/chat/048-the-cards-checks-pass-under-load` (code `f54c3b8`, ff from `3f9a95f`; doc `e07a8173`, the worker's `4c7aa074` cherry-picked). Re-gated on the merge result on a lightly loaded machine: `npm ci`, `build`, `typecheck`, `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (436 tests, 433 passed, 0 failed, 3 skipped), `test:webview` (all 163 checks passed). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 39%, weekly 25%, wave 6); PROCEED at this fold (5-hour 6%, weekly 27%).
**Least sure about:** the unexplained 11-in-20 burst hit a deadline on the page's own clock, which a slow driver reply does not explain, so a product-side late post may still exist and the 15 s deadline would now hide it; this worker also ran about 150 minutes, so the wave's foreground barrier held the other three finished units idle for two hours.

---

## 2026-11-26 17:07 — ui/125 the-ui-shows-which-core-it-is-talking-to

**Decided:** nothing suite-wide. **New ui decision 112** (`decisions/core-identity.md`): one line under the top bar, so on every tab, built from the client's `attestation()` in the snapshot poll (`CoreIdentity::from_attestation`, `Snapshot.core_identity`): `Core: service|development, <16 hex>, matches the installed fingerprint|does not match|no attested install on this machine`; a mismatch and a failed challenge (what a Core too old to report one produces) are drawn as warnings; nothing is blocked. **The worker's own call, the limit to know:** `service` or `development` is derived from the client's match result, not read from Core's status `mode`, because `embarch-core-client`'s `StatusResponse` drops `mode` and `keyid`; a development Core whose key was recorded as the installed fingerprint would read `service`. The worker filed **EMB-576** (api, Fleet Ready) to add the fields; 112 says to switch when they land. The client caches its attestation per connection, so a Core swapped behind a running UI is not re-checked until the UI restarts (not written into 112). `spec/tabs.md` took one line and is now 906 B from its cap, still filed against `tasks/ui/126`.
**Merged:** `agent/ui/125-the-ui-shows-which-core-it-is-talking-to` (code `e5edeac`, ff from `1e49270`; doc `b3c27a83`, the worker's `b107d287` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (362 passed, 4 ignored, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/ui-141-core-identity-line.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. The line has not been drawn in a browser or against a live Core, service or development. **Deploy debt:** the installed embarch-ui shows no identity line until rebuilt.
**Budget:** PROCEED at leg start (5-hour 39%, weekly 25%, wave 6); PROCEED at this fold (5-hour 6%, weekly 27%).
**Least sure about:** the line says `service` on a match alone, so until EMB-576 lands it is only as true as the recorded fingerprint, which is the one thing the line exists to let the person doubt.

---

## 2026-11-26 17:05 — core/169 a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test

**Decided:** nothing suite-wide. **Split this leg from Fleet Ready, at `dbf2088a`:** EMB-369 into `core/169` (this unit) and `core/170` (the per-test study record's predicate, unparked to `open` in this fold), EMB-575 into `api/206`, EMB-388 into `dev-bench/053` (`verify-only`, queued). **New core decision 144** (`decisions/test-run-record.md`): a Test run is sealed as it ends — finish, cancel or deadline — before `end_run` releases the run lock, as `test-runs/<run_id>.test-run.dsse.json` (the worker added the `<run_id>.` prefix to the task's name), predicate `urn:embarch:predicate:test-run:v1`, subjects `run.json` (canonical hash) and `result.json`; the predicate carries status, reason, unit key, `resumes`, the go's `selection` (the prepare record now keeps it), the call-log range and `tests[]` with verdict or reason (`not_run`, `interrupted`) and each study record's hash. A run with a started marker and no result is sealed `interrupted` at Core's start. Run log: one `test` entry per test (`run_id, test_id, definition_hash, requirements, unit_key, dut_image, verdict`) and one `test_run` entry per run with the record's hash and study ids. Retention: a Test run's study runs are held until a `published` entry carries its `run_id`, then swept as one unit. **The worker's own calls, the owner's to strike:** the `run_id` key on `published` (no route writes one yet, so Test-run captures are never swept for now, an `open.md` item), the unit key as the first bench's DUT hardware ID, and an interrupted run recording every test `interrupted` with no verdict (no per-test checkpoint exists; the resume unit owns that). Interfaces `signing.md` and `run-log.md` amended; 110 and 111 not grown. **New size debt:** `embarch-core/open.md` entered reserve (4,227 of 5,120 B), filed as `tasks/core/171-compact-core.md`, `blocked`, In flux: yes, due 2026-12-10.
**Merged:** `agent/core/169-a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test` (code `81ab021`, ff from `90a6cc9`; doc `d33cc7f6`, the worker's `49924869` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (610 passed, 2 ignored, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-388-test-run-record.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one real Test run on a bench, under the lease, leaves `test-runs/<id>.test-run.dsse.json` and a `test_run` run-log entry, and a cancelled one names every selected test with a verdict or reason. The native Windows build of Core (nothing new is `cfg(windows)`). **Deploy debt:** the installed Core signs no Test run record until redeployed.
**Budget:** PROCEED at leg start (5-hour 39%, weekly 25%, wave 6); PROCEED at this fold (5-hour 6% after its reset, weekly 27%).
**Least sure about:** the hold-until-published rule keys on a `run_id` field of a `published` entry that the worker invented and no route writes yet, so until the Test-run publish unit lands every Test run's captures accumulate unswept, and that unit may want a different key.

---

## 2026-11-26 14:23 — dev-bench/051 pd-bench-has-an-idle-command-and-a-hello-line

**Decided:** nothing suite-wide. **New dev-bench decision 68** (`decisions/pd-bench.md`): `pd idle` puts keep-alive on, DR/PR/Request replies back to accept and the `pd max` choice, restores the devicetree's Source_Capabilities on the DRP1M1, drops any contract and ends `pd: ok`, or `pd: error <what>` when VBUS did not discharge or a request failed. `pd hello` prints `pd-bench version <v> commit <c> shield <s>` then `pd: ok`; the commit is `git describe --always --dirty --abbrev=12` taken at CMake configure, the version a new `1.0.0` constant in `pd-bench/CMakeLists.txt`. The restored list is `PdLogicIdle(drp, &idle)` in `pd_logic.c` with four new native_sim tests. `pd detach` not added. **The worker's own calls, not in the task and the least certain part until a board runs them:** dropping a contract is a wire action — a sink holding a contract sends a Hard Reset; on the DRP1M1 `source_off()` runs and, if the bench was the source, it calls `detach()` and requests ErrorRecovery. The `1.0.0` version is the worker's pick. **New size debt:** `embarch-dev-bench/spec.md` entered reserve (9,138 of 10,240 B), filed as `tasks/dev-bench/052-compact-dev-bench.md`, `blocked`, In flux: yes, due 2026-12-10, unparking after the HIL characterisation session runs `pd idle` and `pd hello`.
**Merged:** `agent/dev-bench/051-pd-bench-has-an-idle-command-and-a-hello-line` (code `06ef18d`, ff from `5cff766`; doc `68444e79`, the worker's `3d104147` cherry-picked). Re-gated on the merge result from the main checkout's `workspaces/pd-bench` with the suite's own `.west-venv` west: `west twister -T <worktree>/pd-bench -p nucleo_g0b1re` built both shields (SNK1M1, DRP1M1), `west twister -T <worktree>/pd-bench/tests/logic -p native_sim` passed, `python3 -m unittest discover scripts` 9 passed. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row (none exists for pd-bench).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on both shields: set `keepalive off`, `dr reject`, `pr reject`, `answer wait`, `srccaps` and `pps`, run `pd idle`, and read `pd status` and `pd srccaps` back at their defaults; a sink holding a PPS contract — `pd idle` sends the Hard Reset and renegotiates at the default choice; the DRP1M1 sourcing to a sink — VBUS under 0.6 V within tSafe0V and the port attaches again from scratch; `pd hello` prints the right version, commit (with `-dirty` when it was) and shield on each build (`tasks/dev-bench/051`, retired in this fold).
**Budget:** PROCEED at leg start (5-hour 27%, weekly 24%, wave 6); PROCEED at this fold (5-hour 38%, weekly 25%).
**Least sure about:** the worker initialised the main checkout's `workspaces/pd-bench` (`west init`, `west update --narrow`, `west patch apply`, git-ignored files only) using a west from a client workspace's venv rather than the suite's `.west-venv`; nothing in a client repo was written, but a worker reaching for a client venv is a habit to watch.

**Leg end, to carry:** 4 of 4 units landed in one wave (claimed 14:02, all four reported by about 14:11): `core/167`, `ui/124` (half — the go card; the task is `blocked` on EMB-575), `chat/046`, `dev-bench/051`. **Split this leg, at `6967737b`, all `filed` (Fleet Working):** EMB-574 to `chat/048` (the 💡 cards flake: find late or never sent, then fix), EMB-375 to `api/205` (`declare_instrument` passes metrology and calibration), EMB-336 to `ui/125` (the which-Core line on every tab), EMB-371 to `core/168` (keep the host awake through a Test run, `verify-only`). **Done in Linear this leg:** EMB-368 and EMB-415. **New issues by workers:** EMB-575 (api: `CoreClient`'s prompt types carry `kind`, `observation`, `switched_on` and an answer `value`), Fleet Ready, which unparks `ui/124`. **EMB-369 is now splittable** (its blocker EMB-368 is Done): it heads the HIL Test chain that nine waiting issues sit behind (EMB-370, 372, 373, 378 to 382, 390), so a leg that splits it unblocks the most. **Dispatchable now:** `api/205`, `chat/048`, `core/168`, `ui/123`, `ui/125`, `ui/126` (four scopes, `ui` three times); Fleet Ready 19 unsplit, 14 waiting. **New size debts:** `ui/126` (`spec/tabs.md`, open, due 2026-12-09) and `dev-bench/052` (`spec.md`, blocked In flux: yes, due 2026-12-10); none overdue. Refill was owed on spread only at leg start; I split Fleet Ready rather than sweep `open.md`, so no `Spread sweep` line. **Hardware buffer refreshed at 13:59:** Core reachable, dev-bench and DUT not attached; bench tasks `api/059` and `dev-bench/038` stay `open`. **Still unclassified:** `embarch-analog-capture-proposal.md`, the owner's. **Watchdog:** this wave's foreground call held about 9 minutes, so no tick gap this time. **Budget at leg end:** PROCEED, 5-hour 38%, weekly 25%.

---

## 2026-11-26 14:20 — chat/046 the-linker-offers-a-studys-capture-or-trace

**Decided:** nothing suite-wide. **New chat decision 119**, in a new topic file `decisions/references-studies.md` (so `references-kinds.md` stays out of reserve): the 💡 linker reads `embarch-api --json list-studies --limit 20` through `chat/043`'s runner and offers one entry per tap, `trace` when its `encoding_kind` is `outpost_trace`, else `capture`, newest study first, written as the task specified (` not rendered` when the tap's `rendered` is false; names through `clipTitle` and carried in `titles` so `copiesTitle` drops a card that copies them). A study id in the draft offers its taps with no cue word; otherwise a cue word (capture, trace, recording, stream, tap, study, run, samples, log, plurals) gates it and a tap is offered when its name or its study's shares a word with the draft; a recency word orders newest first. **The runner now splits a verb's text into arguments**, so `list-studies --limit 20` is one cache key beside `list-instruments` under the one cache rule the decision states. **The worker's own figures, marked in 119 as the owner's to strike:** the 20-study limit, a fallback of the newest 4 traces or taps when "trace" or "capture" has no shared word, "study", "run" and "log" opening the gate for a name match only, and dates in UTC.
**Merged:** `agent/chat/046-the-linker-offers-a-studys-capture-or-trace` (code `3f9a95f`, ff from `3587735`; doc `fe801c24`, the worker's `40a529d0` cherry-picked, no conflict). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (433 passed, 0 failed, 3 skipped), `test:webview` all passed (EMB-574's cards flake did not fire, run on a near-idle machine after the other three gates finished). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/chat-043-linker-study-captures.md` assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. The source has met only the fake `embarch-api`; Core's real `GET /studies` list has not been read through it.
**Budget:** PROCEED at leg start (5-hour 27%, weekly 24%, wave 6); PROCEED at this fold (5-hour 37%, weekly 25%).
**Least sure about:** my first chat gate piped `npm test` into `grep | head`, so its exit status was `head`'s and the line count printed nothing; I re-ran `npm test` bare for the counts above, but a leg that copies that shape will land a red `npm test` as green.

---

## 2026-11-26 14:18 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind

**Decided:** nothing suite-wide. **Half landed, task left `blocked`**: the go card shipped, the prompt-modal half did not. **New ui decision 111** (`decisions/confirm-tab.md`): the go card lives in the Confirm tab (the worker's call, its reason in 111). New routes `GET /api/test-runs/{run_id}/card` and `POST /api/test-runs/{run_id}/go`; the go relays `CoreClient::test_run_go` with `{run_hash, nonce}` and the person's token, never retries, and Core's 400/403/404/409/422 come back with Core's own status and words (the confirm route now shares that refusal helper). The card draws the upper bound, each test's origin and diff, every prompt with its kind, what will be powered and each limit with `U`/`k`/`w`, every agent string as text; go is disabled while an input is unconfirmed (named by kind, name and hash) or when Core issued no nonce, and the card reloads after any answer. **Blocked half:** `embarch-core-client`'s `PendingPrompt` and `StudyEvent::PromptPending` drop `kind`, `observation` and `switched_on`, and `PromptAnswerRequest` has no `value`, so the UI can neither show a prompt's kind nor send an observation's answer; the client is not ui's to write. **The worker filed EMB-575** (api, Fleet Ready) for those fields; `tasks/ui/124` unparks when it lands, and its `## Blocked` section says what to do then. `operator-prompt.md` and `live-study.md` untouched. **New size debt:** `embarch-ui/spec/tabs.md` entered reserve (9,160 of 10,240 B), filed as `tasks/ui/126-compact-ui.md` (`open`, In flux: no, due 2026-12-09). **One line of 111 fixed in this fold, by me:** it said a second click on a started run gets Core's `422`; core decision 135 gives `409` for a started run and `422 replayed` only for a spent nonce (the reviewer's note; the code passes both through).
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `1e49270`, ff from `4a2e694`; doc `4d6ec789`, the worker's `31f54bc3` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (349 + 3 + 2 + 3 passed, 4 ignored, 0 failed), `clippy --all-targets -D warnings` clean; `Cargo.lock` not rewritten. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/ui-140-go-card.md` assembled into `suite/features.md` in this fold.
**Blocked:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind`'s prompt-modal half — waits on EMB-575 (client prompt fields); task `blocked` with `Unparks when:` EMB-575 landing. EMB-384 stays in Fleet Working.
**Reviewer:** no findings.
**Hardware debts:** none to a board. The page has not run in a browser and no `tests/browser` drive was written; the card is drawn by key from Core's documented shape and has met only a stub Core. Owed with `api/203`'s debt: one go given from the UI against a real Core with a prepared run. **Deploy debt:** the installed embarch-ui shows no go card until rebuilt.
**Budget:** PROCEED at leg start (5-hour 27%, weekly 24%, wave 6); PROCEED at this fold (5-hour 37%, weekly 25%).
**Least sure about:** what Core's card answers for a run that has already started; the worker did not know and neither do I, so the card's behaviour after a go was given from another surface is untested.

---

## 2026-11-26 14:15 — core/167 a-bench-is-smoke-checked-before-its-first-test

**Decided:** nothing suite-wide. **New core decision 143** (`decisions/smoke-check.md`): before a bench's first test, the first bench included, `drive` calls `Env::smoke_check`, which checks the bench's declared signals, roles and instruments, `validate` for the DUT and each bench board, each board's hello line (an echo alone is not an answer), each instrument's `*IDN?` (reply kept), and `readback` for the DUT and each bench board. Every piece runs, so a failure names all that failed; the bench's tests become `error`, reason `smoke_check`, and the run goes on (decision 136's policy). **The worker's own calls, stated in 143 and the owner's to strike:** a DUT image that `differs` fails; a DUT `claim` and a bench board's `unreleased`, `unknown` or `unverified` are recorded, not failed. The unit key is the DUT's hardware ID from `validate`; a different ID on a later bench refuses that bench and the earlier bench's results stand; an unreadable ID carries `unit_identity_not_read`; `run.json`'s `dut.declared_serial` is not a key, because Core has nothing to compare it with. A calibration whose serial is not an exact comma-separated field of the kept `*IDN?` reply is `applied: false` with no due date and a note, and reads as no calibration declared. Findings ride `Progress.smoke`, `RunOutcome.smoke` and `result.json`'s `smoke_checks` (additive; `embarch-core-client` mirrors neither type). 142's "nothing calls it yet" and 139's "empty until the smoke check" amended in place; `main.rs`'s `#[allow(dead_code)]` on `readback` is gone. **Limits the worker named:** the `*IDN?` store is process-wide, so a reply outlives its run; `ImageLog` keeps one entry per chip, so two boards of one chip can hide each other's flash entry (reads `claim` or `unknown`, never a failure); the check adds no time to the run's deadline.
**Merged:** `agent/core/167-a-bench-is-smoke-checked-before-its-first-test` (code `90a6cc9`, ff from `ca34d61`; doc `06b5099e`, the worker's `a93b889d` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (603 passed, 2 ignored, 0 failed), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Feature rows `features.d/core-386-bench-smoke-check.md` (new) and `core-384-image-readback.md` (amended) assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the smoke check once on a real bench, in a two-bench fixture run under the lease: a DUT, one bench board with a hello line, one instrument with a declared calibration (`tasks/core/167`, retired in this fold, lists what to confirm). `SMOKE_WAIT_MS` (2 s) and `SMOKE_PORT_WAIT_MS` (5 s) are chosen, not measured. The native Windows build of Core. **Deploy debt:** the installed Core runs no smoke check until redeployed.
**Budget:** PROCEED at leg start (5-hour 27%, weekly 24%, wave 6); PROCEED at this fold (5-hour 34%, weekly 25%).
**Least sure about:** the hello check reads "an echo alone is not an answer" from a console Core has never talked to on a real bench board, so a board whose hello prints differently from the fixture's would fail its bench's smoke check on the first real run.

---

## 2026-11-26 13:55 — chat/047 the-long-chat-scroll-check-settles-before-it-reads

**Decided:** nothing suite-wide. **The race was in the product, not the test**: the timeline's follow in `webview/chat/index.tsx` ran in a `useEffect`, which Preact runs after the next paint (up to about 100 ms late under load), so a read or a scroll event in that gap saw a grown timeline short of the bottom. It is now a `useLayoutEffect`; the test is unchanged. **New chat decision 118** in `decisions/timeline.md`. The worker's evidence: a one-check copy failed 16 of 25 runs under 24 busy loops before the fix, 0 of 25 after; the full check passed 20 of 20 under a lighter `cargo test` load; removing the scroll line made it fail at "at the bottom while it streams". **A second, unrelated webview flake is filed, EMB-574** (Fleet Ready, by the worker): "no cards request in 5000 ms" on the 💡 cards checks, 8 of the worker's 20 full runs. **I saw it on `main` as well** (1 of 3 runs at `701a019`, a different cards check) and said so on the issue, so it predates this change.
**Merged:** `agent/chat/047-the-long-chat-scroll-check-settles-before-it-reads` (code `3587735`, ff from `701a019`; doc `adc0f48d`, the worker's `7dd99028` cherry-picked, rebased over the owner's `6f6fcbd8`). Re-gated on the merge result: `npm ci`, `build`, `typecheck`, `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (428 passed, 0 failed, 3 skipped). **`test:webview` was red once in two runs and I landed anyway**: the run that failed did so on EMB-574's cards check ("hovering a card whose edit adds lines"), and the scroll check passed in both; `main` failed the same way once in three. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at leg start (cache 19 h old, wave 2); PROCEED at `study-designer/100`'s fold (5-hour 26%, weekly 24%, wave 6).
**Least sure about:** this worker ran for about 90 minutes inside a foreground wave, and the leg can tick nothing while a foreground call is open, so the fleet's liveness tick went about 85 minutes without a write (dispatch 11:57, next tick 13:27); `deadman.log` shows no alert this time (I did not find out why), but a long worker in a foreground wave is a stall to the watchdog by construction.

**Leg end, to carry:** 4 of 4 units landed, none blocked: `core/166` and `api/204` (wave 1, claimed 11:33, both reported by about 11:47), then `study-designer/100` and `chat/047` (wave 2, claimed 11:57; 100 reported in about 5 minutes, 047 in about 90). **The study-hash chain is finished**: no task waits on it any more. **Split this leg, at `af80de62`, both `filed` (Fleet Working):** EMB-571 to `chat/047` (landed) and EMB-368 to `core/167` (the smoke check before a bench's first test, `open`, `Hardware: none`, a bench-run debt in the task). **New issue:** EMB-574 (chat's 💡 cards checks fail "no cards request in 5000 ms" under load, on `main` too), Fleet Ready; until it lands, a chat unit's `test:webview` can go red on a cards check that its branch did not touch. **Dispatchable now:** `chat/046`, `core/167`, `dev-bench/051`, `ui/123`, `ui/124` (four scopes); Fleet Ready holds 20 unsplit issues and 15 waiting on blockers. Refill was not owed at leg start (6 across 5 scopes); no sweep, so no `Spread sweep` line. **Hardware buffer refreshed at 11:3x**: Core reachable, dev-bench and DUT not attached, so bench tasks `api/059` and `dev-bench/038` stay `open`. **Still unclassified:** `embarch-analog-capture-proposal.md` (`check-ownership.py --supervisor`), the owner's call. `fold-day.py`: 2026-11-25 folded, 2026-11-23 rolled; the duplicate `## 2026-11-24 — 43 units` heading is untouched. **Budget at leg end:** PROCEED, 5-hour 27%, weekly 24%.

---

## 2026-11-26 13:54 — study-designer/100 check-test-refuses-a-study-that-does-not-match-its-hash

**Decided:** nothing suite-wide. **The study-hash chain that `study-designer/099` started on 2026-11-25 is complete**: `hil_check::check_test` now refuses a host study that does not hash to its test's `study.hash` by `hil_test::study_hash`, as `Rule::StudyHashMismatch` on `study.hash`, naming the study file and both hashes. Only `7391457`'s `src/hil_check.rs` hunk was taken; its test was rewritten against `main`'s helpers (`tests/hil_checks.rs`). Decision 113 amended in place: the refusal is in force, and it waited for both consumers. `Rule` gained a variant, which I read before landing (the shared-crate rule): additive, behind `hil-test`. **The consumer re-test the handoff asked for was done before landing:** gate-only worktrees of `embarch-api` at `8f0ba84` and `embarch-core` at `ca34d61` at fresh target dirs, their `embarch-study-designer` link pointed at this branch's worktree (`StudyHashMismatch` present through the link), `cargo clean -p embarch-study-designer`, then `cargo test`: api 582 passed, core 596 passed, 0 failed in both. Links restored to the main checkout and the gate worktrees removed. `embarch-ui` and `embarch-umbrella` do not enable `hil-test`; the crate's own gate covered their feature sets.
**Merged:** `agent/study-designer/100-check-test-refuses-a-study-that-does-not-match-its-hash` (code `8bd6bcc`, ff from `ebbaaca`; doc `e067e275`, the worker's `fcaeea23` cherry-picked, rebased over the owner's `6f6fcbd8`). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings` and `cargo test` under default (200 passed), `--all-features` (506), and each consumer's set: `alloc` (225), `alloc,reducers,hil-test` (291), `std,reducers,hil-image,hil-test` (326), `study-ui,gatt-extract,eap-parse` (417), 0 failed and clippy clean in all six. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at leg start (cache 19 h old, wave 2); PROCEED at this fold (5-hour 26%, weekly 24%, wave 6).
**Least sure about:** a premade study Core was not sent is still accepted at the prepare with its card saying `false` (`core/166`), so this refusal covers the definition-time check and a sent study, not a test whose study never reached Core.

---

## 2026-11-26 11:56 — api/204 test-propose-fills-a-studys-hash-with-study-hash

**Decided:** **reversals row 118 added** (`reversals/rows-115-115.md`): a Test's `study.hash` had three conventions across three repos (the file's bytes in `embarch-api`, whatever the fixture said in Core, `study_hash` in the crate), found when the crate's refusal turned two consumers red on 2026-11-25; all three now call `study_hash`. The unit: `src/hil_repo.rs` fills and compares `study.hash` with `hil_test::study_hash(&study)` instead of the SHA-256 of the bytes it writes; a given hash that differs is still refused naming both; `sha256_hex` and the `sha2` import are gone from that file; `tests/run_test_cli.rs`'s placeholder hash and `tests/test_propose_cli.rs`'s assertions use `study_hash`, plus one new test (a wrong given hash is refused and Core is not called). **New api decision 136** in `decisions/test-plans.md`, superseding 134's bytes line (134 shortened to a pointer, so it shrank). **The worker's refusal run:** with only the `src/hil_check.rs` hunk of `7391457` applied in a throwaway crate worktree and `cargo clean -p embarch-study-designer`, the crate recompiled from that path and the workspace was green. **In this fold: `study-designer/100` unparked to `open`** (both `api/204` and `core/166` have landed). The shared client crate was not touched.
**Merged:** `agent/api/204-test-propose-fills-a-studys-hash-with-study-hash` (code `8f0ba84`, ff from `fc1a33b`; doc `859faca3`, the worker's `85b9699b` cherry-picked). Re-gated on the merge result: `cargo build --workspace`, `clippy --workspace --all-targets -D warnings`, `cargo test --workspace --no-fail-fast` (582 passed, 0 failed). `check-docs.py` 12/12 with `core/166`'s doc commit beside it; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at leg start (cache 19 h old, wave 2); PROCEED at `core/166`'s fold (5-hour 13%, weekly 23%, wave 6).
**Least sure about:** `study-designer/100` is now dispatchable, and the leg that lands it must still re-run `embarch-api`'s and `embarch-core`'s tests against it after `cargo clean -p embarch-study-designer` in each; both workers' throwaway runs say that will be green, but neither was run against the branch that will actually land.

---

## 2026-11-26 11:54 — core/166 the-test-run-prepare-checks-each-study-against-its-hash

**Decided:** nothing suite-wide. `POST /test-runs`'s prepare now hashes every premade study it was sent with the crate's `hil_test::study_hash` and compares it with its test's `study.hash`; a mismatch is refused `422` naming the test, the file and both hashes, and nothing is registered. An expanded template's study is skipped (`expand` hashes it itself), and so is a premade study that was not sent, as before. The go card's `bytes_checked_against_hash` keeps its name and now reads `true` when the study was sent and checked, `false` otherwise (`ui/124` and `api`'s `run_test` read it). Core's fixture `tests/fixtures/hil-tests/test.json` carried a made-up hash and now carries `study_hash` of its study. Core decision 134 amended in place (its "not here: a check of the study files" clause removed); `interfaces/test-runs.md` rows updated. **The worker's refusal run:** with only the `src/hil_check.rs` hunk of `7391457` (the reverted `check_test` refusal, i.e. `study-designer/100`) applied in a throwaway crate worktree and `cargo clean -p embarch-study-designer`, Core was 594 passed, 0 failed; with the old fixture hash the same setup failed 11 (the definitions test and ten `test_runs` tests), so the refusal bites and this fixture is what makes it green. **Also in this fold:** the 2026-11-25 day folded into one entry by an `embarch-log-folder` (64 units, the log 286 KB to 118 KB) and 2026-11-23 rolled to `log-archive/`; `check-client-names.py --suite --history` clean in every repo.
**Merged:** `agent/core/166-the-test-run-prepare-checks-each-study-against-its-hash` (code `ca34d61`, ff from `5964670`; doc `be9e5e76`, the worker's `1a756f99` cherry-picked). Re-gated on the merge result: `cargo build`, `clippy --all-targets -D warnings`, `cargo test --no-fail-fast` (596 passed, 0 failed). `check-docs.py` 12/12 with `api/204`'s doc commit beside it; ownership green on both branches; client names clean on the code worktree. Feature row `features.d/core-360-test-runs-prepare.md` (amended) assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none to a board. The native Windows build of Core. **Deploy debt:** the installed Core accepts unchecked study files until redeployed.
**Budget:** DEGRADED at leg start (cache 19 h old, wave 2); PROCEED at this fold (5-hour 13%, weekly 23%, wave 6).
**Least sure about:** a premade study that was not sent is still accepted with its card saying `false`; nothing in the decisions requires a refusal there, but a go card the person approves without reading that field approves an unchecked study.

---

## 2026-11-25 — 64 units

*Folded by an embarch-log-folder agent on 2026-11-26 (the leg that follows the owner's `/fleet stop`): per-unit narrative reasoning, gate transcripts, budget lines and "least sure about" notes dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, board-naming debt and blocked line kept, one block per unit, newest first. The day's ten "Leg end, to carry" paragraphs are folded into the carry-forward below.*

**Carry forward (state at the last leg's end, 16:07).**
- **The fleet is stopped.** The owner's `/fleet stop` (about 16:01) ended the last leg; its `.fleet/stop` marker was deleted after landing, the pump latch is gone, and there was no channel message to reply in. Last leg: 4 of 4 landed (`study-designer/101`, `api/203`, `core/165`, `umbrella/118`), none blocked; budget PROCEED, 5-hour 24%, weekly 21%.
- **`study-designer/100` stays `blocked` until both `api/204` (EMB-570) and `core/166` (EMB-555's Core half) have landed**, and its landing leg must re-test `embarch-api` and `embarch-core` after `cargo clean -p embarch-study-designer`. Why: `study-designer/099` was landed, turned two consumers red (`embarch-api` hashes the study file's bytes into `study.hash`, Core's fixture does the same) and was reverted the same leg; `api` and Core `main` were red 15:14 to 15:28. The supervisor's consumer gate had not been real: swapped path dependencies were not rebuilt (mtime fingerprint), so both tested the old crate. **EMB-572** (fleet, shared-crate gate: a shared-crate unit's gate runs no consumer's tests) is the open fix, moved to Todo as `Scope: fleet`. `study-designer/101` landed the additive half (`study_hash` plus decision 113, no refusal); until `api/204` lands, `embarch-api`'s test-plans decision (`study.hash` is the file's bytes) and 113 disagree on what the field means.
- **Dispatchable now:** `api/204`, `core/166`, `chat/046` (captures and traces as linker kinds), `dev-bench/051` (`pd idle` and `pd hello`, verify-only), `ui/123` (compact `live-study.md`, due 2026-12-09) and `ui/124` (the go card, unparked by `api/203`); five scopes, `ui` twice. `api/201` (compact `embarch-api/spec.md`, due 2026-12-09) is `blocked`. Fleet Ready: 21 unsplit issues. New issues: EMB-571 (chat's webview scroll check fails under load; `chat/045` landed past it), EMB-572, EMB-570.
- **Hardware / bench:** bench tasks `api/059` and `dev-bench/038` stay `open`, no board; hardware buffer last refreshed 09:38, not refreshed since. Debts owed this day are in the per-unit lines below (`umbrella/118`'s five `deploy-core` runs on the Windows machine and `core/165`'s image readback per chip family are the largest).
- **Deploy debts:** the installed `embarch` binary keeps the old `deploy-core` behaviour until rebuilt from `main` (after that it no longer overwrites or restarts the service; new umbrella decision 68 in `decisions/deploy.md`, `--restore-service` to go back); the installed service Core still answers the old plain-text `422` for a missing measurements file until redeployed with `core/164` (`api/202` tolerates both).
- **Stale, the owner's:** `embarch-dev-workflow.md` §4a (and its step 3) still describes stop, copy over the service's binary, start and verify the service. `embarch-analog-capture-proposal.md` is in neither `reserved` nor `fleet_writable` (`check-ownership.py --supervisor`), still unclassified all day. `notes/hil/06-report-and-publish.md` line 36 still names `hil-run.md` for a Study's export and check (`fold-commit.py` refuses to stage `notes/`; resolves through the stub; not seen resolved by any later leg). `embarch-ui`'s committed `Cargo.lock` is behind `embarch-api`'s `embarch-core-client`, so any ui build rewrites it. Core decision 133 (`decisions/definitions.md`) is 233 B over its per-decision limit. `embarch-api/interfaces/tools-tests.md` still says of `run_test` that "no code path calls the go", less precise than api decision 135.
- **Decisions made on the owner's behalf (marked the owner's to strike in their entries):** two suite passes, both announced and run as a leg's last unit after a silent window: `suite/062` (host step parses a number, a prompt has a kind; `HOST_TYPE_SCHEMA_VERSION` 24 to 25, wire stays 17; study-designer decision 108; `number_grammar` moved from `pdf-text` to `std`) and `suite/063` (an instrument's declaration carries its metrology; topology decision 51; `Instrument` lost its `Eq` derive; plan choice 14, metrology in Core's own store, marked the owner's to strike). Deploy loop: umbrella decision 68 (above). Image readback: core decision 142 (per-chip `ImageLog` entry is an argument; the `EMBARCH_BENCH_FIRMWARE_LIST` variable's name is a recommendation). Nothing calls `readback` yet.
- **Linear:** flapped on the 2,500/hour cap through the morning legs (finished and filed through single calls), and the free-plan issue cap spooled up to 8 entries; by 13:40 the spool was empty and Linear answered. Two reviewer findings were left unfiled at the cap (`tasks/api/197`, and core `4ef12e6` fixed forward). Refill gate fired on depth and spread at the 15:39 leg; Fleet Ready was split rather than the `open.md` sources swept, so **no `Spread sweep` line was written this day** (the newest is `Spread sweep: nothing filed (2026-11-24 00:23)` in the 2026-11-24 entry).
- **Transient:** one `git push` to `embarch-api` refused with SSH `publickey` and went through on retry; if it recurs it is the agent's SSH access. The chat compaction-test flake (`wire.test.mjs`) hit again under the full run (fixed by `chat/045`).
- **The log carries `## 2026-11-24 — 43 units` twice** (about ten lines apart, the first apparently a partial copy of the second); left untouched, not part of this fold.

---

### 16:07 — umbrella/118 deploy-core-installs-a-development-core-beside-the-service
But this changes the owner's own deploy loop: once the umbrella binary is rebuilt from `main`, `embarch deploy-core` no longer overwrites and restarts the service.
**Merged:** `agent/umbrella/118-deploy-core-installs-a-development-core-beside-the-service` (code `5533608`, ff from `4d99988`; doc `7e726d5a`, the worker's `c3265055` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** five `deploy-core` runs on the Windows machine, each checked against `/status`: with the service running; refused with a study in flight; with `--cancel-run`; `--restore-service`; a second deploy while the development Core runs (from `tasks/umbrella/118`, retired in this fold). **Deploy debt:** the installed `embarch` binary keeps the old behaviour until rebuilt.

### 16:06 — core/165 core-reads-an-image-back-through-the-probe
New `src/readback.rs`: `readback(core, Board::{Dut, Bench}, entry, list) -> ImageStatus` reads each segment of a board's newest `flashed-images.jsonl` entry back through `CoreAccess` in chunks of `MAX_WORDS` (one …
**Merged:** `agent/core/165-core-reads-an-image-back-through-the-probe` (code `5964670`, ff from `74d3530`; doc `69ef51af`, the worker's `20878c42` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** whether a whole image reads back through the probe on each chip family Core flashes (nRF54L, nRF54H, STM32 G0 and F4, ESP32-C5), especially where Core flashes with the vendor tool rather than the probe library; recorded in `tasks/core/165` (retired in this fold, so the debt lives here and in decision 142). The native Windows build of Core.

### 16:05 — api/203 the-core-client-carries-a-person-only-go
`embarch-core-client` gains `CoreClient::test_run_go(run_id, run_hash, nonce)`, posting `{run_id, run_hash, nonce}` to `/test-runs/{id}/go` through `send` with whichever bearer the client was built with
**Merged:** `agent/api/203-the-core-client-carries-a-person-only-go` (code `fc1a33b`, ff from `7b45e83`; doc `5965c768`, the worker's `b31493ac` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the method has met a mock Core only. Owed with `ui/124`: one go given from the UI against a real Core with a prepared run.

### 16:04 — study-designer/101 study-hash-lands-alone
The additive half of the reverted `study-designer/099`: `hil_test::study_hash(&HostStudy)` (the `definition_hash` of the study, SHA-256 of its canonical JSON) is back, and `check_test` refuses nothing new (the `StudyHashMismatch` …
**Merged:** `agent/study-designer/101-study-hash-lands-alone` (code `ebbaaca`, ff from `1dfdae1` through the worker's `01f983e`, the revert of the revert; doc `d08a42a8`, the worker's `5c44041a` cherry-picked onto the owner's `ebab3222`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 15:39 — study-designer/099 one-function-fixes-a-premade-studys-hash
I landed this unit, it turned two consumers red, and I reverted it the same leg.
**Merged:** `agent/study-designer/099-one-function-fixes-a-premade-studys-hash` (code `7391457`, ff from `0caf76b`; doc `a9c73a20`, the worker's `1bc42244` cherry-picked), **then reverted**: code `1dfdae1`, doc `29869b13`.
**Reviewer:** 1 finding — EMB-570
**Hardware debts:** none.
*Also cited:* `8e89c85c`.

### 15:34 — chat/045 the-compaction-test-stops-racing-and-holding-the-run
Re-landed from the 429'd leg (see `core/164`'s entry). Only `test/wire.test.mjs` changed
**Merged:** `agent/chat/045-the-compaction-test-stops-racing-and-holding-the-run` (code `701a019`, ff from `1109bb0`; doc `40155087`, the worker's `2a51292b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none.

### 15:33 — api/202 read-the-no-measurements-refusal-by-a-stable-code
Re-landed from the 429'd leg (see `core/164`'s entry). `embarch-core-client`'s `MeasurementsRefusal::NoMeasurements` is recognised by the `422` status alone, a body `code` of `"no_measurements"` (core decision 141) or none (an …
**Merged:** `agent/api/202-read-the-no-measurements-refusal-by-a-stable-code` (code `7b45e83`, ff from `9214394`; doc `cefcc941`, the worker's `6b507571` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the refusal has met a mock Core only. Owed against a real Core once redeployed with `core/164`: `study-measurements` on a run with no file reads as no-measurements from the JSON body.
*Also cited:* `1dfdae1`.

### 15:32 — core/164 the-measurements-route-serves-a-host-studys-file
Re-landed from the leg that claimed `chat/045`, `study-designer/099`, `api/202` and `core/164` at about 13:45 and died on a 429 (spend limit) before folding anything
**Merged:** `agent/core/164-the-measurements-route-serves-a-host-studys-file` (code `74d3530`, the worker's `c5a34af` rebased onto `3f41ff8`, the owner's EMB-563 commit; doc `939540af`, the worker's `47d39599` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board. The native Windows build of Core. **Deploy debt:** the installed service Core still answers the old plain-text `422` until redeployed; `api/202` tolerates both.
*Also cited:* `1dfdae1`, `5b8d493`.

### 13:40 — chat/044 the-linker-offers-a-linear-project-or-document
`RefIndex` gains optional `projects` and `documents` (`IndexProject`, `IndexDocument`), parsed by `DeskClient.refs()`, read as `[]` from a desk that omits them.
**Merged:** `agent/chat/044-the-linker-offers-a-linear-project-or-document` (code `1109bb0`, ff from `5f97b9f`; doc `b9f70a41`, the worker's `b55a7728` cherry-picked onto `6cdaa4a3`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the kinds have met only the invented index, never a real Linear workspace through a real desk.
*Also cited:* `b4766574`.

### 13:38 — ui/121 the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input
A resume of the unit that stopped on my split error: `api/199` added the client methods, and this leg put the worker on the old branches, `embarch-ui`'s fast-forwarded to `origin/main` and `embarch-doc`'s with `origin/main` …
**Merged:** `agent/ui/121-the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input` (code `68ab18f`, ff from `9e8f193`, then my `b3cfc4b`; doc `cefa026c`, the worker's `e76f38f0` cherry-picked onto `bf632cc4`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the tab has met a stub Core only and has not been opened in a browser. Owed: open Confirm against a Core holding an unconfirmed custom test, confirm one, and see the run log's `confirmed` entry record surface `ui`.
*Also cited:* `0caf76b`, `5b8d493`, `69223acd`, `9214394`.

### 13:36 — core/163 an-instruments-metrology-and-calibration-reach-its-measurements
`PUT /instruments` already took the shared crate's `Instrument` with `metrology` and `calibration` and already recorded its scope in `Declarations`, so `api.rs` is unchanged.
**Merged:** `agent/core/163-an-instruments-metrology-and-calibration-reach-its-measurements` (code `0ddfd05`, ff from `80f6798`; doc `39222b88`, the worker's `07b8e0ed` cherry-picked onto `c0c88cc1`).
**Reviewer:** no findings.
**Hardware debts:** a host study on a real bench with a declared instrument whose calibration is current, and one past due, to see both stamps in `measurements.json`. The native Windows build of Core. **Deploy debt:** the installed service Core stamps no metrology until redeployed. The `*IDN?` serial check waits for the smoke check (EMB-368).
*Also cited:* `0caf76b`, `5b8d493`.

### 13:35 — api/200 run-test-prepares-a-test-run-and-test-status-watches-it
New `src/hil_run.rs`: `run_test` (MCP tool, CLI `run-test`) turns a saved plan, or a suite with test ids, tags or `all`, into a plan through `hil_expand::expand` (a refusal there is the crate's, with Core not called), posts the …
**Merged:** `agent/api/200-run-test-prepares-a-test-run-and-test-status-watches-it` (code `9214394`, ff from `14ea8f3`; doc `b33d607e`, ff from `a42e1592`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the tools have met only a mock Core. Owed against a real Core (in `open/bench-verification.md`): that it reproduces the crate's `run.json` byte for byte, accepts the base studies a template needs beside the expanded ones, and serves a premade suite's studies at `GET /definitions/<study hash>`.

### 12:26 — chat/043 the-linker-offers-a-bench-instrument
Landed from a dead worker's uncommitted tree, gated by me — the next leg should know this unit's provenance.
**Merged:** `agent/chat/043-the-linker-offers-a-bench-instrument` (code `5f97b9f`, ff from `fd154a5`; doc `e6522cf1`, the recovered `14bc0506` cherry-picked onto `14e85de7` and reworded).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the kind has met only `test/fake-api.mjs`, so one draft naming an instrument in a chat folder with a real `embarch-api` and a declared bench is owed.
*Also cited:* `0facb46`, `9e10f685`.

### 12:00 — ui/122 a-running-study-has-a-cancel-button-in-the-ui
Re-landed from the leg killed at about 10:15 (its worker had pushed both branches).
**Merged:** `agent/ui/122-a-running-study-has-a-cancel-button-in-the-ui` (code `9e8f193`, ff from `508b1e6`; doc `6a967a4a`, the worker's `20bedac9` cherry-picked onto `68797785`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the button has met a stub Core only, so one real cancel of a running study from the UI against a live Core is owed.
*Also cited:* `0caf76b`, `14ea8f3`.

### 11:58 — core/162 a-test-run-opens-a-setup-window-between-benches
Re-landed from the leg killed at about 10:15 (its worker had pushed both branches).
**Merged:** `agent/core/162-a-test-run-opens-a-setup-window-between-benches` (code `80f6798`, ff from `9233136`; doc `384c208f`, the worker's `958de02a` cherry-picked onto `e12e81fc`).
**Reviewer:** no findings.
**Hardware debts:** a real two-bench fixture run on a bench, enrolling a board in the setup window between the two benches, in the person's session. The native Windows build of Core. **Deploy debt:** the installed service Core has no setup window until redeployed.
*Also cited:* `0caf76b`.

### 11:54 — api/199 the-core-client-calls-the-confirmation-routes
Re-landed from a killed leg: the leg that claimed `api/199`, `core/162`, `ui/122` and `chat/043` at 10:12 died with the Claude Code session at about 10:15 and folded nothing.
**Merged:** `agent/api/199-the-core-client-calls-the-confirmation-routes` (code `14ea8f3`, ff from `9f3f9e2`; doc `bdaaf7d9`, the worker's `666c137f` cherry-picked onto `17af2b2b`).
**Reviewer:** no findings.
**Hardware debts:** none; the methods have met only a mock Core.
*Also cited:* `047bb59d`, `0facb46`, `14bc0506`.

### 10:07 — ui/121 the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input
My split error, caught by the worker: Core serves the three confirmation routes, but `embarch-core-client` has no method for any of them, and its one-funnel test forbids the UI from sending around it, so the card cannot be built …
**Merged:** nothing in code. Doc: the worker's blocked note `4beb3058`, cherry-picked onto `a6586e07` as `c6713baf`, and my edit to it with the new task in this fold.
**Blocked:** `agent/ui/121-the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input` — the core client lacks the confirmation routes' methods; `blocked`, unparks when `api/199` lands. Its doc branch is pushed with the note; the `embarch-ui` branch never got a commit and was never pushed.
**Reviewer:** skipped (nothing landed: the unit stopped before writing code).
**Hardware debts:** none.

### 10:06 — umbrella/117 embarch-agent-starts-stops-and-checks-the-agents-container
New `src/agent_run.rs`: a `ContainerRuntime` trait (`build`, `image_exists`, `volume_create`, `run`, `stop`, `rm`, `exec`, `inspect`) over a `Process` seam, `CliRuntime` as Docker or Podman by binary alone (`docker()`/`podman()`, …
**Merged:** `agent/umbrella/117-embarch-agent-starts-stops-and-checks-the-agents-container` (code `4d99988`, ff from `82f5ef7`; doc `2988c6eb`, the worker's `b27e6987` cherry-picked onto `1fa92ad0`).
**Reviewer:** no findings.
**Hardware debts:** the owner's first container, with Docker or Podman installed and `init --container` run in a repo: `embarch agent up`; `embarch agent status`, every line `ok`; `embarch agent shell` and `shell --claude`; `docker inspect embarch-agent-<name>` against the vector in `container.toml`; `embarch agent down`, volume and exchange folder still there; then each from-memory item above. No runtime has ever run any of it.
*Also cited:* `0caf76b`, `9f3f9e2`.

### 10:04 — core/161 core-enforces-a-prompts-kind-by-the-tokens-scope
A prompt's kind is `run.json`'s `prompt_kinds` by step name, reaching the backend through a new `RunContext` passed to `run_study_blocking`
**Merged:** `agent/core/161-core-enforces-a-prompts-kind-by-the-tokens-scope` (code `9233136`, ff from `dc0bccc`: `c6ad3be` and `9233136`; doc `d6b058a1`, the worker's `84f2eee0` cherry-picked onto `e5f7df0d`).
**Reviewer:** no findings.
**Hardware debts:** a Test run on a real bench with a person answering an observation from a surface, the agent's token refused `403`, and a real instrument set listed as switched on. The native Windows build of Core. **Deploy debt:** the installed service Core enforces none of this until redeployed.
*Also cited:* `0caf76b`.

### 10:03 — api/198 a-tool-and-a-subcommand-cancel-a-running-study
`cancel_study` (MCP) and `cancel-study <study_id>` (CLI, `--json`) share `CoreClient::cancel_study`, new in `embarch-core-client` with `StudyCancelled {study_id, status}` (read before landing
**Merged:** `agent/api/198-a-tool-and-a-subcommand-cancel-a-running-study` (code `9f3f9e2`, ff from `0b36fcb`; doc `e5f7df0d`, ff from `dffe499b`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the tool has met only a mock Core.
*Also cited:* `1795624948`, `a1eff5c7`.

### 09:35 — umbrella/116 the-agents-container-makes-its-own-clone-on-first-start
`render_entrypoint_agent(&plan)` (and `_at(&plan, root)`, which puts every container path under a temp root for the shell test) in `src/agent.rs` renders the agent half of the entrypoint, run as uid 1000 after decision 63's root …
**Merged:** `agent/umbrella/116-the-agents-container-makes-its-own-clone-on-first-start` (code `82f5ef7`, ff from `dfad2a8`; doc `de5c194c`, the worker's `71a8ca94` cherry-picked onto `fd977ee4`).
**Reviewer:** no findings.
**Hardware debts:** the owner's first container: `git remote -v` shows one remote, `claude mcp list` from the clone shows `embarch`, `/work/.west/config` and `west list` look right, and an edit under `/outbox/embarch` survives a restart while a new person file arrives. The shell test ran on stub `git` and `claude`, so real git behaviour is unproven.
*Also cited:* `0b36fcb`, `0caf76b`, `be08040b`.

### 09:34 — core/160 core-runs-a-test-selection-test-by-test
New `src/test_executor.rs`: `drive` walks `run.json` against an `Env` trait (a fake in tests, `CoreEnv` on the real bench), bench by bench and test by test
**Merged:** `agent/core/160-core-runs-a-test-selection-test-by-test` (code `dc0bccc`, ff from `b0b10e7`; doc `fd977ee4`, ff from `67e9d52c`).
**Reviewer:** no findings.
**Hardware debts:** the real reset, the idle line and `run_study_blocking` have run over no bench: one run of a two-test fixture suite on a bench with a DUT and a board, through the person's go. The native Windows build of Core. **Deploy debt:** the installed service Core has neither the executor nor the route until redeployed.
*Also cited:* `0caf76b`.

### 09:17 — study-designer/097 compact-study-designer
A verbatim split, no text deleted: the "A Study's export and check" section (`run_status`, what a Study's run exports, the JUnit and OCP T&V exports, `verify`'s check table 0 to 9, what `verify` cannot recompute) moved from …
**Merged:** `agent/study-designer/097-compact-study-designer` (doc only, `9d167879`, the worker's `b9d305d6` cherry-picked onto `8d004762`; no code SHA).
**Reviewer:** no findings.
**Hardware debts:** none.

### 09:15 — api/197 test-files-are-written-through-the-person-writer
`hil_repo` has no file write of its own: `write_under_embarch` calls `ConfinedWriter::write_with`, a new form of the person writer that takes `overwrite` (false refuses an existing file, which keeps "a saved bench is never …
**Merged:** `agent/api/197-test-files-are-written-through-the-person-writer` (code `0b36fcb`, ff from `eb2f64d`: the worker's `f5ad7f2` and my `0b36fcb`; doc `8d004762`, ff from `047c959e`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the Windows branch of `person_writer` was edited and is unbuilt (already `tasks/api/193`'s debt).

### 08:52 — ui/120 a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted
New `src/bench/references.rs` scans `embarch/studies/*.json` (not recursive) and every `.json` under `embarch/tests/suites/` (the layout `api/196` pinned)
**Merged:** `agent/ui/120-a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted` (code `508b1e6`, ff from `90668da`; doc `d318facc`, the worker's `6f029875` cherry-picked onto `efa8c712`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the dialogs and the tweak to `tests/browser/drive_bench_configs.py` (Delete now waits on an async lookup) were not run in headless Firefox: one run of that script, plus a case with a fixture test naming a config.
*Also cited:* `0caf76b`, `eb2f64d`.

### 08:51 — umbrella/115 init-sets-up-the-agents-container-and-registers-the-repo
`embarch init --container [--runtime docker|podman]` renders `umbrella/112` to `114`'s outputs (Containerfile, `container.toml`, firewall script, a clone config template) into `~/.config/embarch/agents/<name>/` (Windows …
**Merged:** `agent/umbrella/115-init-sets-up-the-agents-container-and-registers-the-repo` (code `dfad2a8`, ff from `7b1c1f0`; doc `f3c21c52`, the worker's `53a497e5` cherry-picked onto `9cdb8dd2`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; native Windows is unrun (the `%APPDATA%`/`%LOCALAPPDATA%` folders are covered only by the pure resolver's test), and `west list` has never run against a real west workspace.
*Also cited:* `0caf76b`, `eb2f64d`.

### 08:49 — core/159 a-test-runs-go-takes-the-lease-and-starts-the-run
`POST /test-runs/{run_id}/go`, the person's token only (the agent's gets `403` from `person_middleware`, new `token_store::GO_ROUTES`)
**Merged:** `agent/core/159-a-test-runs-go-takes-the-lease-and-starts-the-run` (code `b0b10e7`, ff from `4ef12e6`; doc `b141b632`, the worker's `5fbc7e56` cherry-picked onto `01743947`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core. **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-366 and the person's terminal.
*Also cited:* `0caf76b`.

### 08:46 — api/196 test-plans-in-the-repo-and-proposals-sent-to-core
I pinned the tests layout across two scopes at the split, so `api/196` and `ui/120` could run in one wave
**Merged:** `agent/api/196-test-plans-in-the-repo-and-proposals-sent-to-core` (code `eb2f64d`, ff from `add96ab`; doc `44c88c7d`, ff from `3c9d68cb`).
**Reviewer:** 1 finding — `tasks/api/197` (unfiled: Linear refused at its issue cap; I wrote the task and dropped the spool entry so it is not filed twice)
**Hardware debts:** none from a board; everything ran against `MockCore`, a real Core's card should show the hash `TestDef::hash()` gives, and the Windows `std::fs` writes in `hil_repo` are unbuilt (all in `open/bench-verification.md`).
*Also cited:* `1795620494`, `97b00fdd`.

### 08:19 — chat/041 the-linker-offers-kconfig-symbols-and-devicetree-nodes
The 💡 linker offers two more kinds from `chat/040`'s one `embarch-atlas refs --json` read, with no second run
**Merged:** `agent/chat/041-the-linker-offers-kconfig-symbols-and-devicetree-nodes` (code `fd154a5`, ff from `4093c1a`; doc `4aa3d7e0`, the worker's `3171871b` cherry-picked onto `d52660fd`).
**Reviewer:** no findings.
**Hardware debts:** none; never seen against a real atlas or window (said in 115 and the feature row).

### 08:08 — umbrella/114 the-agents-container-image-and-west-workspace-mounts
`src/agent.rs` gains, pure: `render_containerfile(&plan)` (the plan gains `toolchain
**Merged:** `agent/umbrella/114-the-agents-container-image-and-west-workspace-mounts` (code `7b1c1f0`, ff from `d9a4b8a`; doc `318ec292`, the worker's `6b8fc8fa` cherry-picked onto `01032278`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; no image has been built, so every from-memory line and the nft backend of Debian's `iptables` under 63's rules are unverified until EMB-448's first build and start.
*Also cited:* `0caf76b`.

### 08:07 — core/158 core-prepares-a-test-run-and-serves-its-go-card
`POST /test-runs` (either token) takes `{run, plan, suite?, studies}`
**Merged:** `agent/core/158-core-prepares-a-test-run-and-serves-its-go-card` (code `4ef12e6`, ff from `2f25415`: the worker's `ec0e629`, my `128fe14` and `4ef12e6`; doc `01032278`, the worker's `f41e3f2d` cherry-picked onto `6bf2d218`).
**Reviewer:** 1 finding — fixed forward in core `4ef12e6` (unfiled: Linear refused at its issue cap, spool entry dropped once fixed).
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-376.
*Also cited:* `0caf76b`.

### 08:04 — study-designer/098 one-function-turns-a-tests-records-into-its-verdict
; I read the shared-crate diff before landing it (one `pub mod hil_judge` line in `lib.rs` behind `hil-test`, the rest new files
**Merged:** `agent/study-designer/098-one-function-turns-a-tests-records-into-its-verdict` (code `0caf76b`, ff from `2366f86`; doc `6bf2d218`, the worker's `efe831c9` cherry-picked onto `1c276399`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795617464`, `49acf3ad`.

### 07:30 — suite/063 an-instruments-declaration-carries-its-metrology
A suite pass, run by me as this leg's last unit, announced by the previous leg (ts `1795612302.163159`, 06:11
**Merged:** `agent/suite/063-an-instruments-declaration-carries-its-metrology`, landed in order, each ff from its `origin/main`: topology `5b8d493` (from `7b0b87d`), core `2f25415` (from `2e8a18b`), api `add96ab` (from `5e18cc3`), ui `90668da` (from `7d52207`); doc `9aad9194`, my own commit in the leg worktree.
**Reviewer:** no findings.
**Hardware debts:** none from the code; the native Windows build of Core. **Deploy debt:** the installed service Core accepts the new fields only once redeployed; nothing sends them yet.

### 07:11 — umbrella/113 the-agent-containers-firewall-and-cores-address-from-inside
`src/agent.rs` gains, pure: `render_entrypoint_root(&plan, core_host)`, a POSIX root script that drops IPv4 and IPv6 egress, allows loopback, established flows, DNS to the IPv4 resolvers in `/etc/resolv.conf`, TCP to Core's …
**Merged:** `agent/umbrella/113-the-agent-containers-firewall-and-cores-address-from-inside` (code `d9a4b8a`, ff from `aecbcf8`; doc `f6c24010`, the worker's `1447d4ae` cherry-picked onto `7bb1421c`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; every rule is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.

### 07:09 — core/157 core-keeps-definitions-premade-suites-and-confirmations
Core keeps HIL definitions and records confirmations: `POST /definitions` checks a test, suite or plan with the crate's `check` functions (and `hil_check::check_test` when the request carries a study and a bench), keeps it as …
**Merged:** `agent/core/157-core-keeps-definitions-premade-suites-and-confirmations` (code `2e8a18b`, ff from `22646fc`; doc `3f9ffd2f` and `40517a43`, the worker's `8baf99f5` and `2a6e2bfb` cherry-picked onto `d21d666e`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has none of these routes until it is redeployed with this commit; nothing consumes a confirmation until EMB-364.
*Also cited:* `2366f86`.

### 07:07 — study-designer/096 expand-a-test-selection-into-the-resolved-run-file
; I read the shared-crate diff before landing it. Leg start, to carry
**Merged:** `agent/study-designer/096-expand-a-test-selection-into-the-resolved-run-file` (code `2366f86`, ff from `8ecf13e`; doc `4641e35a`, ff from `e5dce1e8`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795612302`, `1795614703`, `2cfd93a4`.

### 06:43 — umbrella/112 a-pure-renderer-for-the-agents-container
New `src/agent.rs`, pure, no I/O, nothing calling it yet (`#![allow(dead_code)]` until EMB-445 to EMB-448)
**Merged:** `agent/umbrella/112-a-pure-renderer-for-the-agents-container` (code `aecbcf8`, ff from `4715a1a`; doc `5e323a7d`, the worker's `c4f6790b` cherry-picked onto `eee38f71`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; every flag and mount is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.
*Also cited:* `1795612302`.

### 06:41 — core/156 a-service-core-refuses-identity-routes-to-the-agents-token
A `--service` Core answers `403` to the agent's token on the eleven identity routes (probe enrol, unenrol, set board, unenrol by serial, dev-bench link, signal declare and remove, instrument declare and remove, bootload ports set …
**Merged:** `agent/core/156-a-service-core-refuses-identity-routes-to-the-agents-token` (code `22646fc`, ff from `0108da1`; doc `a75984d9` and `eee38f71`, the worker's `358a23ab` and its anchor fix `3866852f` cherry-picked onto `c91f40c1`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core refuses nothing new until it is redeployed with this commit.

### 06:39 — api/195 the-client-sends-cores-token-only-after-a-challenge
; I read the shared-crate diff (`embarch-core-client` gains a public `attest` module, `CoreClient::attestation()`, `CoreClient::new_with_stores(...)` and `CoreConfig::token_is_explicit(scope)`
**Merged:** `agent/api/195-the-client-sends-cores-token-only-after-a-challenge` (code `5e18cc3`, ff from `9f698e3`; doc `c91f40c1`, the worker's `152e1588` cherry-picked onto `cac9ad95`).
**Reviewer:** no findings.
**Hardware debts:** a live-Core check: install a `core-fingerprint` beside the token file and confirm a matching service Core gets the machine-wide token and a development Core gets the development store's, through WSL2 on the bench machine. **Deploy debt:** the MCP server and `embarch-ui` pick this up only when rebuilt; until a `core-fingerprint` exists on the machine nothing changes.

### 06:37 — study-designer/095 a-hil-test-is-checked-when-it-is-defined
; I read the shared-crate diff before landing it (one `pub mod hil_check` line in `lib.rs` behind `hil-test`, the rest new files
**Merged:** `agent/study-designer/095-a-hil-test-is-checked-when-it-is-defined` (code `8ecf13e`, ff from `faddb4c`; doc `cac9ad95`, the worker's `0ed109fa` cherry-picked onto `7e1e1206`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795612297`, `1795612302`, `bf0f6723`.

### 04:08 — chat/040 the-linker-offers-datasheet-and-spec-sections
The 💡 linker has an atlas section source on decision 112's interface
**Merged:** `agent/chat/040-the-linker-offers-datasheet-and-spec-sections` (code `4093c1a`, ff; doc `3962c9e0`, the worker's `0645b448` cherry-picked onto `86b58e9a`).
**Reviewer:** no findings.
**Hardware debts:** none (tested against a fake `embarch-atlas` only, and not seen in a real VS Code window; the feature row says so; the `cards-refs` model call was not re-recorded for the new `section` kind).
*Also cited:* `20fa59c`.

### 03:56 — api/194 compact-api
Nothing. `embarch-api/open.md` went from 4,292 to 3,779 B, out of reserve, by two verbatim moves with their relative links fixed
**Merged:** `agent/api/194-compact-api` (doc `06ae6b10`, the worker's `f1751160` cherry-picked onto `aae8a2d9` with its subject corrected; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none new; the moved live-log line still needs a bench with a lease.

### 03:53 — study-designer/094 types-for-a-hil-test-a-suite-and-a-plan
; I read the shared-crate diff before landing it (one new feature line in `Cargo.toml`, one `pub mod` line in `lib.rs`, the rest new files).
**Merged:** `agent/study-designer/094-types-for-a-hil-test-a-suite-and-a-plan` (code `faddb4c`, ff from `3e4e301`; doc `e973a520`, the worker's `870441c5` cherry-picked onto `e22bc4ee`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 03:43 — core/155 a-host-step-parses-its-number-and-writes-measurements
Split three Fleet Ready issues at leg start (`d68e30ab`): EMB-359 as `tasks/core/155`, EMB-353 as `tasks/study-designer/094` (HIL test, suite and plan types, the root of the HIL Test chain), EMB-411 as `tasks/chat/040` (atlas …
**Merged:** `agent/core/155-a-host-step-parses-its-number-and-writes-measurements` (code `0108da1`, ff from `d645ecd`; doc `ed57d5bb`, the worker's `da086fb0` cherry-picked onto `dfa05876`).
**Reviewer:** no findings.
**Hardware debts:** a host study with a `parse` run on a bench against a DUT console, a bench board's signal and a real instrument, checking `by`, `instrument` and the signed subject list; the native Windows build. **Deploy debt** carried from `suite/062`: Core, `embarch-api` and `embarch-ui` deploy together for host v25.
*Also cited:* `1795602826`.

### 03:26 — suite/062 a-host-step-parses-a-number-and-a-prompt-has-a-kind
A suite pass, run by me as this leg's last unit, and a host-schema bump, both announced (ts `1795597152.735759`, 01:59
**Merged:** `agent/suite/062-a-host-step-parses-a-number-and-a-prompt-has-a-kind`, landed in order: study-designer `3e4e301` (from `31b4408`), core `d645ecd` (from `cf5b661`), ui `7d52207` (from `d66e313`) (each ff from its `origin/main`); doc `df83f1b2`, my own commit in the leg worktree.
**Reviewer:** no findings.
**Hardware debts:** none from the code; a **deploy debt**: the host gate is a strict match both ways, so Core, `embarch-api` (MCP server restarted) and `embarch-ui` deploy together and `embarch-umbrella` is rebuilt, or `embarch doctor` check 11 warns. The installed Core already reports host v21 (`fleet-hardware.py`, 02:43), so it was behind before this unit. The native Windows build of Core.

### 03:05 — api/193 a-confined-writer-for-the-persons-embarch-folder
New `src/person_writer.rs` (`pub mod person_writer`): `ConfinedWriter::open(repo_root)` refuses a linked or non-folder `<repo>/embarch`
**Merged:** `agent/api/193-a-confined-writer-for-the-persons-embarch-folder` (code `9f698e3`, ff from `cd1f428`; doc `0e34d264`, the worker's `3856e88b` cherry-picked onto `7a16781f`).
**Reviewer:** no findings.
**Hardware debts:** `cargo test person_writer` on Windows from the main checkout (the whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `aws-lc-sys`'s C build before it reaches the module); a Windows symlink and junction fixture is still unwritten, since those fixtures are `#[cfg(unix)]`; the native Windows build.

### 03:04 — chat/039 the-linker-offers-branches-and-worktrees
The 💡 linker has its first new source on decision 112's interface
**Merged:** `agent/chat/039-the-linker-offers-branches-and-worktrees` (code `a70291c`, ff from `89b20a8`; doc `333e2799`, the worker's `52a0c771` cherry-picked onto `bb0b51d8`).
**Reviewer:** no findings.
**Hardware debts:** none (the feature has not been seen in a real VS Code window; the feature row says so).
*Also cited:* `1795600044`, `20fa59c`, `6d313db3`.

### 02:40 — core/154 core-holds-the-bench-ports-under-a-lease
I split EMB-326 mid-leg (`8cb884ea`; `filed` hit the rate limit at the status move and reached it on the retry, so the issue may carry its filed comment twice) and dispatched it beside `umbrella/110` as this leg's fourth unit, …
**Merged:** `agent/core/154-core-holds-the-bench-ports-under-a-lease` (code `cf5b661`, ff from `b539f6a`; doc `78090367`, the worker's `64c8cd99` cherry-picked onto `9d79ef78`).
**Reviewer:** no findings.
**Hardware debts:** on Windows COM ports, a second open of a held signal or instrument port must fail while Core's own exchange, instrument call and study tap still work (COM exclusivity assumed); on a real CDC ACM bench port, what a hold does across a DUT reset or re-enumeration (a held handle may go stale); that asserting DTR at hold time does not reset a board a plain open leaves alone; the native Windows build.
*Also cited:* `1795597152`.

### 02:40 — umbrella/110 install-core-verifies-a-signed-release-first
`embarch install-core <release dir or archive> [--allow-downgrade] [--dry-run] [--data-dir DIR] [--trusted-root FILE | --refresh-trust-root]` (new `src/install_core.rs`)
**Merged:** `agent/umbrella/110-install-core-verifies-a-signed-release-first` (code `4715a1a`, ff; doc `b3a8b0e8`, the worker's `62166429` cherry-picked onto `0d2c9c77`).
**Reviewer:** no findings.
**Hardware debts:** one elevated Windows run of `install-core` with a signed release and a tampered one, checking the staging folder's ACL lists only Administrators and SYSTEM (`open.md`'s line); the native Windows build.

### 02:28 — chat/038 the-linker-takes-references-of-any-kind
The 💡 linker takes references from any number of sources: `src/assistant/refsBase.ts` (entry and source types), `refsDesk.ts` (the desk's issues and PRs, the first source, line and text unchanged), `references.ts` …
**Merged:** `agent/chat/038-the-linker-takes-references-of-any-kind` (code `89b20a8`, ff from `695f46d`; doc `3dc7ccd8`, the worker's `6779dcf8` cherry-picked onto `99be4085`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795597152`, `20fa59c`.

### 02:26 — core/153 core-keeps-a-service-store-and-a-development-store
First normal-mode leg after the burndown ended, so new decisions are back in scope
**Merged:** `agent/core/153-core-keeps-a-service-store-and-a-development-store` (code `b539f6a`, ff from `9df9976`; doc `269dad6d`, the worker's `ca1b414f` cherry-picked onto `288f488a`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build (whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `hidapi`'s `build.rs`, as `gate.md` expects); the owner builds natively and runs `run --service` with no store (expect the refusal), then `run --store <dir>`. None of the new code is `cfg(windows)`-gated.
*Also cited:* `1795597146`, `1795597152`, `2b361b09`, `3dc22553`, `52de0e4d`, `a2da724a`.

### 01:51 — desk/045 the-reference-index-holds-linear-documents
And no new decision (burndown leg). The desk's reference index (`GET /refs`) now carries `documents
**Merged:** `agent/desk/045-the-reference-index-holds-linear-documents` (code `20fa59c`, ff from `2afbcbe`; doc `88c5ef48`, the worker's `15f5da00` cherry-picked onto `97b76588`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `009d3d63`, `1795596282`.

### 01:38 — suite/061 compact-studies-guide
Beyond the announced move, and no new decision (burndown leg).
**Merged:** no worker branch; my own commit, doc `3d291eed` on `47609410`, landed in this fold's push. Gate on the result:.
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795593942`.

### 01:35 — desk/044 the-reference-index-holds-linear-projects
And no new decision (burndown leg). The desk's reference index (`GET /refs`) now carries `projects
**Merged:** `agent/desk/044-the-reference-index-holds-linear-projects` (code `2afbcbe`, ff; doc `f2fde423`, the worker's `e888d977` cherry-picked onto `ae4f54a4`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:34 — api/192 a-list-studies-verb
And no new decision (burndown leg). `embarch-api [--json] list-studies [--limit N]` lists Core's retained studies newest first by `started_utc_ms` (no start time after, by id), each tap with Core's tagged `encoding` and a flat …
**Merged:** `agent/api/192-a-list-studies-verb` (code `cd1f428`, ff from `a3d0831`; doc `ae4f54a4`, the worker's `f9129c46` cherry-picked onto `28311ead`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:33 — atlas/109 a-refs-verb-lists-sections-symbols-and-nodes
And no new decision (burndown leg). `embarch-atlas refs [--json] [--atlas-dir D] [--atlas <id>]` (new `src/embarch_atlas/refs.py`, listed in `cli.py`) prints every translated document's sections, and the current atlas's Kconfig …
**Merged:** `agent/atlas/109-a-refs-verb-lists-sections-symbols-and-nodes` (code `b4c3c75`, ff from `d0b5ca5`; doc `28311ead`, the worker's `309356a3` cherry-picked onto `bf5d945c`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `08b3ca7a`, `1795594763`.

### 01:12 — promptu/025 compact-promptu
And no new decision (burndown leg). Unparked early for the verbatim move its task names, as the `promptu/024` entry suggested and `desk/038`'s entry explains.
**Merged:** `agent/promptu/025-compact-promptu` (doc `c18a2754`, the worker's `f54c6c73` cherry-picked onto `f2538f73`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:11 — umbrella/107 compact-umbrella
And no new decision (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says.
**Merged:** `agent/umbrella/107-compact-umbrella` (doc `f2538f73`, the worker's `a1c44420` cherry-picked onto `6a54b70b`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:11 — atlas/107 compact-atlas
And no new decision (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says.
**Merged:** `agent/atlas/107-compact-atlas` (doc `6a54b70b`, the worker's `0fc7b04d` cherry-picked onto `99057054`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:10 — desk/038 compact-desk
And no new decision (burndown leg). I unparked four size debts early, for the verbatim moves their own tasks name
**Merged:** `agent/desk/038-compact-desk` (doc `0ce75348` and `99057054`, the worker's `8bf257a8` and `7656f71a` cherry-picked onto `005334ad`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795593942`.

### 00:56 — atlas/108 the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture
And no new decision (burndown leg). `embarch-atlas/src/embarch_atlas/livelog.py` no longer keeps `UNGATED`
**Merged:** `agent/atlas/108-the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture` (code `d0b5ca5`, ff from `74048d8`; doc `347a28f4`, the worker's `31792f90` cherry-picked onto `0d7e8a3c`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `c254d15`.

### 00:54 — api/190 hil-guide-words-point-at-the-glossary
And no new decision (burndown leg). The HIL guide's Words entry for Study now reads "Study (the mode
**Merged:** `agent/api/190-hil-guide-words-point-at-the-glossary` (code `a3d0831`, ff from `c254d15`; doc `0d7e8a3c`, the worker's `b1e151df` cherry-picked onto `fcadb4c0`); the suite guide edit is in this fold commit.
**Reviewer:** no findings.
**Hardware debts:** none.

### 00:39 — promptu/024 the-contract-fixes-build-step-5s-shapes-and-forks
And no new decision (burndown leg; the issue itself says the forks hold the choices).
**Merged:** `agent/promptu/024-the-contract-fixes-build-step-5s-shapes-and-forks` (code `6d091a1`, ff from `dcb6588`, docs only; doc `076da6d2`, the worker's `15a24261` cherry-picked onto `0bf5cb47`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 00:37 — api/191 a-shared-fixture-pins-the-live-log-rules
And no new decision (burndown leg). `embarch-api/tests/fixtures/live-log/` holds 19 plain-JSON cases pinning the five rules both live-log writers share (the 4096-byte answer cap with 2- and 4-byte characters at the cut, the board …
**Merged:** `agent/api/191-a-shared-fixture-pins-the-live-log-rules` (code `c254d15`, ff from `d755007`; doc `0bf5cb47`, the worker's `50b9ec81` cherry-picked onto `aed2c46d`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795590679`, `39be7664`.
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
*Days 2026-11-23 to 2026-11-23 rolled to [log-archive/supervisor-log-2026-11-23-to-2026-11-23.md](log-archive/supervisor-log-2026-11-23-to-2026-11-23.md).*
