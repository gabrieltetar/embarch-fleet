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

## 2026-11-27 04:26 — desk/048 compact-desk

**Decided:** nothing suite-wide, no new decision. A verbatim split: decisions 27, 69 and 94 (the user service, its instances, the unit writer) moved byte for byte from `embarch-desk/decisions/built.md` into a new `decisions/service.md`, with an index row in `decisions.md` (`built.md` now lists 22 to 26, 28, 70 to 73, 75); `built.md` 11,873 to 9,001 B, out of reserve; `service.md` 3,333 B. Every `Must not delete:` item survives (27's rejected Windows service, hosting inside the UI and spool file; 94's rejected alternatives and WSL quoting rule; 69's instance rules). `interfaces.md` untouched (still `desk/049`'s debt). **The human question, the worker's answer:** yes, `decisions.md` routes the service, its instances and the unit writer to `service.md`, which says why a user service (27: the desk runs `claude -p` and resolves repo paths inside WSL) and how the unit is written (94: the shared `embarch-user-unit` crate, `%` doubled everywhere and `$` doubled in `ExecStart` only, the installing shell's `PATH` carried in). **Fixed in this fold:** `history/desk.md` line 28 linked decision 94 to `decisions/built.md`, which turned `check-decision-refs.py` red once 94 moved; repointed at the index `decisions.md`, as DOC-CONVENTIONS asks. The worker filed that as EMB-596; closed after the push, since this fold is the fix.
**Merged:** `agent/desk/048-compact-desk` (doc only, `5e354385`, the worker's `dd1cfb61` cherry-picked onto `af644e49`; no code branch). `check-docs.py` red on the worker's branch alone (the history link), 12/12 on the merge result with the link repointed; ownership green; `check-doc-size.py --pressure` no longer lists `built.md`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 49%, weekly 50%, wave 6).
**Least sure about:** whether every mission split will keep tripping on `history/` links to a topic file: a worker cannot edit `history/`, so each split that moves a decision a changelog entry cites will arrive red, and only the fold can repair it.

---

## 2026-11-27 04:25 — core/186 compact-core

**Decided:** nothing suite-wide, no new decision. A verbatim split: `embarch-core/decisions/platform.md`'s `## Locking` section (decisions 4, 14, 15) moved byte for byte into a new `decisions/locking.md`, with an index row in `decisions.md` (the platform row lost 4, 14, 15) and `decisions/lease.md`'s sibling link repointed; `platform.md` 11,555 to 8,265 B, `locking.md` 3,595 B. `spec.md` §5 rewritten as a shorter pointer to `interfaces/constants.md` keeping the path convention, 9,082 to 9,008 B: out of reserve, but by only 31 B. Every `Must not delete:` item survives (spec §3's 129, 156, 157; 106's `CreateService FAILED 1073` and `Environment` loss; 157's rejected alternatives and unverified-on-Windows note). **The human question, the worker's answer:** yes, `spec.md` alone says what Core is and is not, its invariants (auth and its one exception, `hw_lock` and the 500 ms `503`, the lease, the call log, fail-closed identity, the error contract), the deployment shape (two stores, `mode`, `keyid`, decision 157's install rule) and where the rest lives. **Edited in this fold:** `tasks/core/193`'s size line, which named `core/186`, now says `spec.md` sits 31 B under its reserve line.
**Merged:** `agent/core/186-compact-core` (doc only, `c686d729`, the worker's `812c57d1` cherry-picked onto `0829cd04`; no code branch). `check-docs.py` 12/12 on the merge result; ownership green; `check-doc-size.py --pressure` no longer lists either file.
**Blocked:** nothing.
**Reviewer:** no findings.
Reviewer's residue, not a contradiction: `history/archive/core-2026-09--2026-09.md` (around line 101) still links decision 14 to `platform.md`; a frozen archive, left alone.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 49%, weekly 50%, wave 6).
**Least sure about:** `spec.md`'s 31 B margin: the next core unit that adds a line to it is back in reserve, and only `core/193`'s task file warns about it.

---

## 2026-11-27 04:23 — ui/132 firmware-build-finds-embarch-toml-by-the-shared-rule

**Decided:** nothing suite-wide. **At leg start, at `5c898c14`:** no Fleet Ready issues; spread sweep skipped (the `git log` of every sweep source since the 02:58 sweep was empty); no boards attached (buffer refreshed at step 0), so `api/059` and `dev-bench/038` stay `open`; nothing overdue in the size ledger. One wave of four, one per scope: `api/227`, `ui/132`, `core/186`, `desk/048`. **Picked `api/227` over `api/226` on purpose**: `core/193` waits on `api/227`, so landing it first would have let the next leg run `api/226` and `core/193` side by side in two scopes. **New ui decision 114** (`decisions/firmware-build.md`, index row; decision 38 points at it): `src/firmware_build.rs`'s `config_path(configured, repo)` calls `embarch_core_client::config_discovery::find_config_path`, `[build].config_path` as the explicit path and the open repo as the start directory; the ui's own order is gone. Three behaviour changes, all written into 114: the walk now reaches ancestors of the open repo (a repo below a directory holding `embarch/embarch.toml` used to read "no config"); an explicit path or variable naming a missing file is an error naming it, and the survey omits `config_path` (it was `available: false` either way); an empty `EMBARCH_API_CONFIG` reads as unset. Tests run on `find_config_path_with`, so they do not read the process environment. **EMB-306 is complete with this fold** (`api/224`, `umbrella/128`, `ui/132`).
**Merged:** `agent/ui/132-firmware-build-finds-embarch-toml-by-the-shared-rule` (code `7075ca4`, ff from `217705f`; doc `d38a17c1`, the worker's `cdbe82c4` cherry-picked onto `2cd4e1d0`). Re-gated on the merge result, built against `embarch-api` `ed2703b`'s core-client: `cargo build`, `cargo test --no-fail-fast` (0 failed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 49%, weekly 50%, wave 6; four scopes picked, so a wave of 4); PROCEED at dispatch (5-hour 49%, weekly 50%).
**Least sure about:** the ancestor walk in the ui: a config found above the open repo that does not list the repo now reports "not one of the projects" instead of "no config", which is the same outcome (nothing builds) under a different message, and nobody has seen it in the running ui.

---

## 2026-11-27 04:14 — api/225 check-6-reads-the-attestation-by-the-signed-records-mode-and-release

**Decided:** **Re-sequenced EMB-332's writing half, on the reviewer's residue.** Core's `src/publish.rs` `attestation()` is called by Study publishing *and* by `src/test_publish.rs`, so `core/193` as filed would change every Test-run report too, and `embarch-api`'s Test-run verifier (`src/verify_test.rs`, which compares `core_attested`) would reject them: a `main` of Core writing reports the `main` of api rejects, the exact state this split was built to prevent. So I filed **`tasks/api/227`** (open, `Hardware: none`): the Test-run verifier and appendix apply check 6's rule, keyed on the Test-run record's `observed.release`; and **`core/193` stays `blocked`, now on `api/227`**, with a paragraph saying both report kinds change. `filed` on EMB-332 after the push. **Api decision 124 amended in place** (`decisions/verify-report.md`; `interfaces/verify.md` row 6): when the signed record's `observed` has a `release` key, `attestation` must be `{label, core_mode, release, reason}` with `core_mode` = `observed.mode`, `release` = `observed.release`, and no `core_attested`; without the key, today's `{label, core_attested: false}`; `reason` never compared; each differing key named as `attestation.<key>`. No schema bump; the key's presence was enough. The Study appendix prints Core mode and Release when present and Core attested only when that is. Mode not added to check 6's PDF claim list (optional in the task). `client-crate.md` untouched.
**Merged:** `agent/api/225-check-6-reads-the-attestation-by-the-signed-records-mode-and-release` (code `ed2703b`, ff from `f7b8efb`; doc `e383db5a`, the worker's `2d5be85a` cherry-picked onto `3d856c01`). Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (647 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
Reviewer's residue, not a contradiction: `src/verify_test.rs` (around 959 and 1074) and `src/publish_test.rs` (around 293) still use the `core_attested` shape; acted on above as `api/227`.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 39%, weekly 49%, wave 6); PROCEED at fold (5-hour 47%, weekly 49%).
**Least sure about:** whether a Test-run record's `observed` carries `mode` today; `api/227` tells its worker to stop and say so if it does not, which would push a Core-side change ahead of it and make EMB-332 a three-step chain.

---

## 2026-11-27 04:13 — core/194 cores-wire-types-move-into-a-crate-core-client-can-depend-on

**Decided:** nothing new suite-wide (the home was the last leg's EMB-295 call, announced at ts `1795775071.202839`, no reply in its window). **I accepted two deviations from the task's brief**, both written into the decision: the crate depends on `serde`, `serde_json` and `embarch-study-designer` (feature `alloc`), not `serde` alone, because a `StudyEvent` carries the study-designer's own wire types; and `StudyEvent` is strict, with no `#[serde(other)]` fallback, because the client's frame decoder already reports an unknown frame as `Unrecognized` with its data. **New core decision 164** (`decisions/wire.md`, a new topic file, index row; `interfaces/modules.md` row): `crates/embarch-core-wire` holds `StudyEvent`, `HelloAckInfo`, `LoadAnswer`/`LoadSummary`/`LoadSubject`, `LEASE_GATED`, and the prompt types the event names (`PendingPrompt`, `SwitchedOn`, `SessionPromptInfo`, `SessionPhase`, `RunFieldInfo`, `AnsweredBy`); Core re-exports each from its old module. The repo root is a workspace (root package and crate both default members); `cargo build --release` still writes `target/release/embarch-core`. Three `&'static str` fields became `String`, same bytes; `PromptPending` keeps its alphabetical keys by keeping the `serde_json::Value` round trip. JSON pinned per family from lines captured off the pre-move binary. `platform.md` and `spec.md` untouched. **Unparked in this fold:** `api/226` set `open`, with a note naming the two deviations and the one choice it owes: the client's mirrors tolerate an older Core (six stamps and four hello fields `Option`), the shared types do not, so it accepts that in decision 49 or keeps lenient client types. **`api/226` needs an `embarch-core` link** in every api, ui and umbrella worktree parent once it lands, which `.claude/leg.md`'s table lacks: EMB-595. I fast-forwarded the owner's clean `embarch-core` checkout to `a7cec14` so that link resolves to the crate.
**Merged:** `agent/core/194-cores-wire-types-move-into-a-crate-core-client-can-depend-on` (code `a7cec14`, ff from `c2ee2f5`: the worker's `0a85302`, `385d010`, and my `a7cec14`, two Cargo.toml comments that cited "decision 194's task" and "wire decision 1" now name decision 164; doc `baa221ad`, the worker's `d989c531` cherry-picked onto `0925dc22`). Read before merging (a wire type and a new crate): manifests, decision 164 and the moved modules' references. Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (672 Core + 7 crate + 2 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean, `cargo build --release` writes the same path, the crate alone by `--manifest-path`; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (the root is now a workspace) and a `cross` aarch64 release build, neither run. **Deploy debt:** one `deploy-core` run once this is on the installed Core, to see the workspace build through the rsync path.
**Budget:** PROCEED at dispatch (5-hour 39%, weekly 49%, wave 6); PROCEED at fold (5-hour 45%, weekly 49%).
**Least sure about:** the strict `StudyEvent`: once `api/226` adopts it, a client talking to an older Core loses frames that carry no stamps as `Unrecognized`, and I left that trade to the api worker rather than deciding it here.

---

## 2026-11-27 04:12 — ui/131 the-ui-installs-its-service-through-the-desks-unit-crate

**Decided:** nothing suite-wide. **Ui decision 101 amended in place** (`decisions/launcher.md`): the ui's `service install`, `uninstall` and `status` go through `embarch-desk`'s `crates/embarch-user-unit` (desk decision 94) by a path dependency, `../embarch-desk/crates/embarch-user-unit`. `src/service.rs`'s own `quoted`, `unit_path`, `systemctl` wrapper and the inline file write and remove are gone; `unit_text` stays as a thin wrapper building the crate's `Unit` with no `args` and `vars` carrying `CARRIED`; `CARRIED`, `config_note`, `USAGE` and the command parsing stay in the ui. A new test pins the unit text byte for byte against a literal (a path with spaces, a `$`, a carried variable). **New edge:** `embarch-ui` now path-depends on `embarch-desk`; the ui has no CI workflow, so nothing breaks today, but any future CI or fresh checkout needs the desk beside it. **The dispatch link table in `.claude/leg.md` lacks this row** (second leg to say so): I made `/home/gabriel/Github/embarch/.worktrees/embarch-ui/embarch-desk` by hand and filed **EMB-595** (Backlog, for the owner: the table, and the `embarch-core` link `api/226` will need for api, ui and umbrella). EMB-302 is complete with this fold (`desk/047`, `ui/131`).
**Merged:** `agent/ui/131-the-ui-installs-its-service-through-the-desks-unit-crate` (code `217705f`, ff from `ade8c4a`; doc `0925dc22`, the worker's `fd65ed30` cherry-picked onto `18b73f7c`). Re-gated on the merge result, built against the desk main checkout at `9faef72`'s crate: `cargo build`, `cargo test --no-fail-fast` (367 passed, 4 ignored, 0 failed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches (the worker's own `--code-repo` run printed an empty scope; mine passed `--scope ui`); client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run on a real service manager: `embarch-ui service install`, `uninstall` and `status` under WSL2; only the pinned unit text covers it. **Deploy debt:** the installed ui, whenever it is next updated.
**Budget:** PROCEED at dispatch (5-hour 39%, weekly 49%, wave 6); PROCEED at fold (5-hour 45%, weekly 49%).
**Least sure about:** whether anything builds `embarch-ui` from a checkout without `embarch-desk` beside it (a packaging script, the launcher's own rebuild path); I found no CI, but did not look for a release script outside the repo.

---

## 2026-11-27 04:10 — umbrella/128 doctor-and-status-read-the-config-the-api-reads

**Decided:** nothing suite-wide. **At leg start:** no Fleet Ready issues; spread sweep skipped (the `git log` of every sweep source since the 02:58 sweep was empty); no boards attached (buffer 28 min old), so `api/059` and `dev-bench/038` stay `open`; the EMB-295 window the last leg left open (ts `1795775071.202839`) had no reply, so `core/194` went out in this leg's one wave with `api/225`, `ui/131` and this. Rolled 2026-11-25 into `log-archive/` (owed since midnight; rides in this fold's log commit). **New umbrella decision 73** (`decisions/config-discovery.md`, index row; `spec/commands.md`'s `doctor` and `status` rows): `src/config.rs`'s `find_config_path` is replaced by `discover_config_path(explicit)`, which calls `embarch_core_client::config_discovery::find_config_path_with` (api decision 152): `--config`, then `EMBARCH_API_CONFIG`, then the walk for the nearest `embarch/embarch.toml` (no longer stopping at the first `.git`; 73 says so). `doctor` and `status` take `--config`; a named path that is not a file is an error naming it (check 6 fails with a fix line; `status` shows `no-token` with the text). Checks 6, 8 and 10 read the discovered path (the task said 12; the code's callers are 6, 8 and 10, and 73 names those). `status` resolves its token through the found config's `[core].token`/`token_env` (new `status_token`); a config the mirror cannot parse is ignored by `status` and judged by check 6. `init` takes no flag (it never called `find_config_path`). `reporting.md`'s status aside rewritten shorter, so that file did not grow; `open.md` untouched; no size debt filed. `interfaces/doctor-chain.md` does not name the flag; only `spec/commands.md` does. EMB-306 still has `ui/132`.
**Merged:** `agent/umbrella/128-doctor-and-status-read-the-config-the-api-reads` (code `ffc598f`, ff from `4cdfea7`; doc `18b73f7c`, the worker's `82829d7c` cherry-picked onto `420500c8`). Re-gated on the merge result, built against `embarch-api` `f7b8efb`'s core-client: `cargo build`, `cargo test --no-fail-fast` (445 passed, 0 failed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 36%, weekly 48%, wave 6; four scopes picked, so a wave of 4); PROCEED at dispatch (5-hour 39%, weekly 49%); PROCEED at this fold (5-hour 45%, weekly 49%).
**Least sure about:** the walk change: a user who kept `embarch/embarch.toml` only at a repo root and runs `embarch doctor` from a nested directory holding its own `embarch/embarch.toml` now gets the nearer file, which matches the API but is a behaviour change nobody asked the owner about.

---

## 2026-11-27 03:44 — desk/046 the-desks-path-rule-names-its-two-client-copies

**Decided:** nothing suite-wide, and no new desk decision. `embarch-desk/interfaces.md`'s HTTP section now says the address and token rule lives in `src/paths.rs` and is written three times, there and in two client copies (`embarch-core-client`'s `desk_discovery.rs`, api decision 151; `embarch-chat`'s `src/desk/rule.ts`, chat decision 124), and that a change moves all three in one pass. In code, doc comments on `config_dir`, `data_dir`, `port` and `desk_token` in `src/paths.rs` name both copies; no behaviour change. Decision 56 and `decisions/built.md` (in reserve under `desk/048`) untouched. **Size debt filed by the worker:** `tasks/desk/049-compact-desk-interfaces.md`, `open`, `In flux: no`, due 2026-12-11 (`interfaces.md` 13,938 of 15,360 B). **EMB-305 is complete with this fold** (`api/223`, `chat/053`, `ui/130`, `desk/046`).
**Merged:** `agent/desk/046-the-desks-path-rule-names-its-two-client-copies` (code `7923ab6`, ff from `9faef72`; doc `f11b328d`, the worker's `a71cd3e8` cherry-picked onto `49502e8f`). Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (327 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 30%, weekly 48%, wave 6).
**Least sure about:** whether "change all three in one pass" can be honoured by the fleet at all, since the three copies sit in three repos and a worker owns one; it reads as a `suite` task or a three-task split whenever the rule next moves, and nothing in the desk's docs says which.

---

## 2026-11-27 03:44 — core/190 service-start-and-stop-try-without-elevation-first

**Decided:** nothing suite-wide. **New core decision 163** (`decisions/service-control.md`, a new topic file, index row; narrows decision 3's self-elevation for `start` and `stop`, and 157's "`start`, `stop` unchanged"): `service::start` and `stop` go through `service::control`, which calls the service manager as the current user; only a rights refusal logs one `debug!` line, calls `ensure_elevated_or_fallback` and retries, and an already-elevated process or any other error returns as today. `install`, `uninstall` and `install --service` still elevate first. The classifier is `is_rights_refusal(&io::Error, windows: bool)`, a pure function over the error text, because `service-manager` 0.11 wraps every failure as `io::Error` kind `Other` reading `Command failed with exit code N: msg`: Windows matches exit code 5 or "access is denied", systemd "interactive authentication required", "access denied" or "permission denied". The real `sc.exe` and `systemctl` texts are matched by reading, not constructed, and 163 says so; that `systemctl` with no terminal prints one of the three is marked `[assumed]`. launchd is not classified, so a refusal there reports as before. `platform.md`, `spec.md` and `open.md` untouched (all in reserve under `core/186`). EMB-342 has `umbrella/124`'s grant (landed earlier) and this; `finish` decides whether anything is left.
**Merged:** `agent/core/190-service-start-and-stop-try-without-elevation-first` (code `c2ee2f5`, ff from `2db1406`; doc `49502e8f`, the worker's `3fa53278` cherry-picked onto `c6f13e33`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (674 passed, 0 failed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I did not fast-forward the owner's `embarch-core` checkout; nothing waits on this.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on Windows and on a systemd Linux, with and without `umbrella/124`'s grant: `embarch-core stop` then `start` gives no prompt with the grant and the usual prompt without it; the Linux refusal text needs confirming (written in the task's debt section, now retired, and in decision 163). The native Windows build of Core (the matcher's Windows branch is selected by `cfg!(windows)` and was never compiled for Windows). **Deploy debt:** the installed Core.
**Budget:** PROCEED at dispatch (5-hour 30%, weekly 48%, wave 6).
**Least sure about:** the systemd text match: a polkit refusal with no terminal is assumed, not observed, to print "Interactive authentication required", and if it prints something else the unelevated try fails and the user sees an error instead of the old prompt.

---

## 2026-11-27 03:44 — ui/130 the-desk-proxy-takes-the-desks-address-from-core-client

**Decided:** nothing suite-wide. **Ui decision 56 amended in place** (`decisions/shell.md`, one clause): the desk proxy takes the desk's address and token path from `embarch_core_client::desk_discovery` (api decision 151). In `src/desk.rs`, `DEFAULT_PORT`, the local `token_path()` and the `EMBARCH_DESK_PORT` parse are deleted; `desk_url()` is `desk_discovery::base_url()` plus the path, `desk_token()` reads `desk_discovery::token_path()`, mapped through `.ok()` so an unresolvable path still reads as "desk not running"; the `/view` test compares against `desk_discovery::port()`. The base URL is unchanged (`http://127.0.0.1:<port>`). The launcher unit's stripping of `EMBARCH_DESK_PORT` (`src/service.rs`) is untouched. EMB-305 is complete once `desk/046` folds, in this leg.
**Merged:** `agent/ui/130-the-desk-proxy-takes-the-desks-address-from-core-client` (code `ade8c4a`, ff from `db0562e`; doc `c6f13e33`, the worker's `d456b352` cherry-picked onto `87beae9a`). Re-gated on the merge result, built against `embarch-api` `482bab7`'s core-client: `cargo build`, `cargo test --no-fail-fast` (366 passed, 0 failed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches (the worker ran it before its `shell.md` edit; mine ran on the landed branch); client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a live desk: the ui proxy finding a scratch desk started with `EMBARCH_DESK_PORT` or `EMBARCH_DESK_CONFIG_DIR` set.
**Budget:** PROCEED at dispatch (5-hour 30%, weekly 48%, wave 6).
**Least sure about:** whether the launcher's unit, which strips `EMBARCH_DESK_PORT`, now leaves an installed ui unable to find a desk on a non-default port that the old code also could not find; the behaviour is unchanged, but the shared rule makes the strip look more deliberate than anything records.

---

## 2026-11-27 03:43 — api/224 core-client-holds-the-one-rule-for-finding-embarch-toml

**Decided:** **Suite-wide, at leg start, at `74929214`:** split EMB-332 and EMB-295, the two Fleet Ready issues two legs had left unsplit. **EMB-332** (a report names the Core's mode and release) is compat-first, not a `suite` task: `tasks/api/225` (open) makes check 6 accept the new attestation, keyed on the signed record's `observed` carrying a `release` key (null or `{suite_version, manifest_sha256}`); with the key, `attestation` must be `{label, core_mode, release, reason}` and no `core_attested`; without it, today's `{label, core_attested: false}`. Then `core/193` (blocked on `api/225`) writes it. No `schema` bump of the record or `report-data.json`: the key's presence is the discriminator, as `observed.call_log` was added. **EMB-295** (Core's wire types hand-mirrored in core-client): I decided the one home is a serde-only crate in Core's repo, `embarch-core/crates/embarch-core-wire` (desk/047's shape, the root becomes a workspace); rejected topology's `wire` feature (topology carries hardware facts, not run events or a lease table) and a core-client feature Core depends on (the server would build against a client's crate). `tasks/core/194` (open) builds it; `api/226` (blocked on `core/194`) switches core-client. **Not dispatched this leg on purpose**, so the owner has a leg's window on that design; announced with the picks (ts `1795775071.202839`). Consequence to know: once `api/226` lands, every `embarch-api`, `embarch-ui` and `embarch-umbrella` worktree needs an `embarch-core` link in its parent, a row `.claude/leg.md`'s table lacks (`check-dispatch.py --created` prints the `ln`). Both `filed`, Fleet Working. Spread sweep skipped: no source changed since the 02:58 sweep (the `git log` was empty). **New api decision 152** (`decisions/config-discovery.md`, index row; `interfaces/config.md`): `embarch_core_client::config_discovery::find_config_path(explicit, start)` (and `_with`, taking the variable's value, for tests; `CONFIG_ENV_VAR`) is the one rule: `--config`, then `EMBARCH_API_CONFIG`, then a walk up every ancestor for `embarch/embarch.toml` (the API's walk; the umbrella's stop at the first `.git` would miss a config kept above a repo). Two behaviour changes, both written into 152: a named file that does not exist is an error naming it, never a fall-through, and an empty variable reads as unset. `main.rs`'s `find_config_upward` and its four tests are gone. `client-crate.md` untouched. **Unparked in this fold:** `umbrella/128` and `ui/132` set `open` (each waited on `api/224` alone).
**Merged:** `agent/api/224-core-client-holds-the-one-rule-for-finding-embarch-toml` (code `f7b8efb`, ff from `482bab7`; doc `87beae9a`, ff from `4d2d04eb`). Read before merging (a shared crate): one additive public module, no existing item changed. Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (646 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-api` checkout to `f7b8efb`, so `umbrella/128` and `ui/132` build against it.
**Blocked:** nothing.
**Reviewer:** no findings.
Reviewer's residue, not a contradiction: api `decisions/firmware-build-crate.md` (around line 19) and `crates/embarch-firmware-build/src/lib.rs:16` still say path resolution stays in `main.rs` "because embarch-ui answers that differently"; 152 overrides that on purpose and `ui/132` follows, so a later api unit can point both at 152.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (5-hour 26%, weekly 47%, wave 6; four scopes picked, so a wave of 4); PROCEED at dispatch (5-hour 30%, weekly 48%).
**Least sure about:** the EMB-295 home: a crate in Core's repo adds a new path-dependency edge from three client repos into `embarch-core`, which I judged cheaper than putting Core's run and lease wire into topology, but it is a suite-shape call made on the owner's behalf and nothing has built it yet.

---

## 2026-11-27 03:17 — desk/047 the-systemd-user-unit-writer-becomes-a-crate-the-ui-can-share

**Decided:** nothing suite-wide. **New desk decision 94** (`decisions/built.md`, index row; `interfaces/cli.md`'s service line): the systemd user-unit writer lives once, in `crates/embarch-user-unit` inside the desk repo, depending on `std` and `anyhow` only, in `embarch-core-client`'s mold; the repo's root `Cargo.toml` becomes a workspace with the crate as a member and a default member, so a plain `cargo build`, `test` and `clippy` reach both, and the crate also builds alone by `--manifest-path`. The crate's API: `Unit { description, exe, args, path_env, vars }`, `unit_text`, `quoted` (the WSL `PATH` rule), `xdg_dir`, `unit_path` (an empty `$XDG_CONFIG_HOME` read as unset), `systemctl`, `install`, `uninstall`, `status`; `args` lets the desk write `serve` and the ui none, `vars` carries the ui's `CARRIED` in order. Instance support (names, ports, folders, the flags that need `--instance`) stays in `src/service.rs` and feeds the crate. The adversarial quoting test moved into the crate; a new desk test pins the first desk's and an instance's unit text byte for byte against the old format. `spec.md` has no service-install text and is untouched; decision 56 untouched. **Size debt filed by the worker:** `tasks/desk/048-compact-desk.md`, `open`, `In flux: no`, due 2026-12-11 (`decisions/built.md` 11,873 of 12,288 B). **Unparked in this fold:** `ui/131` set `open`, with a dispatch note that the ui worktree's parent needs an `embarch-desk` link (the path dependency is `../embarch-desk/crates/embarch-user-unit`), a row `.claude/leg.md`'s link table does not have yet; `check-dispatch.py --created` will print the `ln`.
**Merged:** `agent/desk/047-the-systemd-user-unit-writer-becomes-a-crate-the-ui-can-share` (code `9faef72`, ff from `3067f07`; doc `dc5fb7d2`, the worker's `4f4204d8` rebased onto `0a1f0df4`). Read before merging (a new crate a second repo will path-depend on): the manifests, the public API and the workspace stanza. Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace` (323 passed, plus the crate's 4), `clippy --workspace --all-targets -D warnings` clean; the crate alone by `--manifest-path`, test (4 passed) and clippy clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-desk` checkout to `9faef72` so `ui/131`'s link has the crate to resolve; that does not rebuild or redeploy the installed desk.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run on a real service manager: `embarch-desk service install`, `uninstall` and `status`, first desk and an instance, under WSL2 with a `PATH` holding `Program Files`; only the pinned unit text covers it. **Deploy debt:** the installed desk, whenever it is next updated.
**Budget:** PROCEED at dispatch (5-hour 19%, weekly 47%, wave 6).
**Least sure about:** whether turning the desk repo into a cargo workspace changes anything that builds it from outside — `scripts/desk-gate-bin.py` for chat's gate and the desk's own install path both build from the root, which still builds the binary, but I did not run either.

---

## 2026-11-27 03:15 — umbrella/126 umbrella-takes-the-data-directory-from-topology

**Decided:** nothing suite-wide. **Umbrella decision 39 amended in place** (`decisions/reporting.md`): `doctor` check 16 resolves the machine data directory through `embarch-topology` (decision 52) instead of assuming `C:\ProgramData`, and a resolver error shows in `detail` as "could not be resolved: <error>", not as "nothing yet". Code: `setup::data_dir_for` calls `machine_data_dir` (an error becomes `None` for callers that can only act on a path; `Remote` has no path, as before), and the `windows: bool` argument is gone from `data_dir_for` and `token_path_for`, since topology's resolver reads `cfg!(windows)` itself; `locate.rs` drops its own shell-out and path translation for topology's `windows_env_var` and `windows_path_to_wsl`; check 16 goes through `check_growth_via`, which takes the resolver as an argument, with two new tests (a relocated `ProgramData` and a resolver error) and the old hardcoded-caveat test removed. **No `status.d/` fragment, the worker's call, written into 39:** `embarch-token.md` §5's last gap, a relocated `ProgramData` on a drive WSL2 does not mount, still resolves to an absent `/mnt/<drive>` path, so the gap is not closed for `doctor`. `open.md` (in reserve, parked under `umbrella/127`) untouched. **Size debt filed by the worker:** `tasks/umbrella/129-compact-umbrella.md`, `open`, `In flux: no`, due 2026-12-18 (`decisions/reporting.md` 11,503 of 12,288 B). **EMB-307 is complete with this fold** (`topology/074`, `api/221`, `core/192`, `umbrella/126`).
**Merged:** `agent/umbrella/126-umbrella-takes-the-data-directory-from-topology` (code `4cdfea7`, ff from `88e09ac`; doc `9a10fe73`, the worker's `554abcdd` rebased onto `3c81d86a`). Re-gated on the merge result, built against `embarch-api` `482bab7` (`api/223`'s core-client): `cargo build`, `cargo test --no-fail-fast` (438 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-umbrella` checkout to `4cdfea7`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Host debt on the Windows machine: `embarch doctor` check 16 under WSL2 against a relocated `ProgramData` (only the stubbed seam is tested); the native Windows build of `embarch` (the changed `locate.rs` code is `cfg(unix)` only).
**Budget:** PROCEED at dispatch (5-hour 19%, weekly 47%, wave 6).
**Least sure about:** whether dropping `windows: bool` from `data_dir_for` and `token_path_for` removed the only seam a test used to drive the Windows arm from Linux; the suite still passes, but a Windows-only path may now be covered by nothing that runs here.

---

## 2026-11-27 03:14 — core/192 core-takes-its-data-directory-from-topology

**Decided:** nothing suite-wide. **Core decision 53 amended in place** (`decisions/auth.md`, net-neutral by a tightened sentence): Core's machine data directory comes from `embarch-topology`'s one-machine resolver (topology decision 52, `local_machine_data_dir()`), Core has no resolver of its own, and an unset `ProgramData` is that call's error. `token_store::local_data_dir()` is deleted, both arms; its callers in `token_store.rs`, `staging.rs`, `service.rs`, `logs.rs` and `main.rs` call topology. `--data-dir` and `StoreLayout` untouched; no token-store test changed. One shift the worker named: topology also errors on an empty `ProgramData`, where Core erred only on unset. `interfaces/modules.md`'s `token_store` row drops the function; `spec.md` and `decisions/platform.md` (in reserve) untouched. EMB-307 has `umbrella/126` left, landing in this leg.
**Merged:** `agent/core/192-core-takes-its-data-directory-from-topology` (code `2db1406`, ff from `77401e3`; doc `00587282`, the worker's `6dd953a4` rebased onto `090eb69d`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (670 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-core` checkout to `2db1406`.
**Blocked:** nothing.
**Reviewer:** no findings.
Reviewer's residue, not a contradiction: topology decision 23's text in `embarch-topology/decisions/storage.md` still names `token_store.rs::local_data_dir()`, which no longer exists; decision 52 already names this move, so a later topology unit can refresh the line.
**Hardware debts:** none on a board. The native Windows build of Core (the deleted `cfg(windows)` arm is the only Windows-side change). **Deploy debt:** the installed Core.
**Budget:** PROCEED at dispatch (5-hour 19%, weekly 47%, wave 6).
**Least sure about:** whether any Windows machine runs Core with `ProgramData` set but empty; it was a path under the empty string before and is an error now, which I read as a fix but have no machine to confirm on.

---

## 2026-11-27 03:13 — api/223 core-client-holds-the-clients-copy-of-the-desks-address

**Decided:** nothing suite-wide. **Split at leg start, at `fff95d78`:** EMB-302 (the systemd user-unit writer twice, desk and ui) into `tasks/desk/047` (a dependency-free crate in the desk repo, `std` and `anyhow` only, in core-client's mold; the desk keeps instances) and `ui/131` (blocked on `desk/047`); EMB-306 (three `embarch.toml` rules) into `tasks/api/224` (one resolver in `embarch-core-client`: explicit, `EMBARCH_API_CONFIG`, then a walk from a start dir; the worker picks the API's or the umbrella's walk and writes why), `umbrella/128` (`doctor` and `status` take `--config` and the variable; `status` resolves its token through the config) and `ui/132`, both blocked on `api/224`; `filed`, Fleet Working; announced before any claim (ts `1795773483.576089`). **Left in Fleet Ready, unsplit:** EMB-332 (report names the Core's mode and release; core writes it and api checks it, the issue says "landed together", so it is a `suite` task with a 30-minute window or a compat-first split) and EMB-295 (Core's wire types into a shared wire home, three repos in series). Spread sweep: nothing filed (2026-11-27 02:58) — a delta read of the two source changes since 02:12, both the last leg's own (core's old-key removal waits on a released Core; `embarch-token.md` §2 was that fold's own fragment). Claim notes added to `umbrella/126` (`open.md` has gone into reserve since it was filed) and `core/192` (the over-limit decisions). **New api decision 151** (`decisions/desk-discovery.md`, index row): `embarch-core-client::desk_discovery` is the Rust clients' one copy of the desk's rule (`config_dir`, `data_dir`, `token_path`, `port`, `base_url`, `DESK_DEFAULT_PORT`, `DESK_TOKEN_FILE`), read-only, tested through an injected env lookup; `session_desk.rs`'s own copies are deleted and decision 85 points at it. The one behaviour change, written into 151: an empty `HOME` now reads as unset, as the desk's `paths.rs` does. `user_dirs.rs` not reused (its rule differs) and unchanged. `client-crate.md` untouched.
**Merged:** `agent/api/223-core-client-holds-the-clients-copy-of-the-desks-address` (code `482bab7`, ff from `a2ac963`; doc `0dd7c1cf`, ff from `68bcedb0`). Read before merging (a shared crate): one additive public module and three call sites; no existing public item changed. Re-gated on the merge result: `cargo build`, `cargo test --workspace` (642 passed, 0 failed), `clippy --workspace --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-api` checkout to `482bab7`, so `umbrella/126` gates against it. **Unparked in this fold:** `ui/130` and `desk/046` set `open` (each waited on `api/223` alone).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a live desk: the API finding a scratch desk started with `EMBARCH_DESK_PORT` or `EMBARCH_DESK_CONFIG_DIR` set.
**Budget:** PROCEED at leg start (5-hour 17%, weekly 46%, wave 6; four scopes after the split, so a wave of 4); PROCEED at dispatch (5-hour 19%, weekly 47%).
**Least sure about:** whether anything relied on the old copy accepting an empty `HOME`; it now errors as "no desk" where it used to build a path under `/`, which I read as a fix, but a container with `HOME=""` would change behaviour.

---

## 2026-11-27 02:52 — chat/053 chat-finds-the-desk-by-the-desks-own-rule

**Decided:** nothing suite-wide. **New chat decision 124** (`decisions/desk.md`, index row; `interfaces.md` settings rows): `embarchChat.deskUrl` and `deskTokenPath` lose their literal defaults in `package.json`, and `src/desk/rule.ts` is chat's one copy of the desk's rule (`embarch-desk` `paths.rs`), read from the extension host's environment: `EMBARCH_DESK_CONFIG_DIR` itself, else `$XDG_CONFIG_HOME/embarch-desk` (empty counts as unset), else `~/.config/embarch-desk`, with `desk-token` in it; the URL is `127.0.0.1` on `EMBARCH_DESK_PORT` when it parses as a port, else 4891. A value set in User or Remote settings wins, read through `inspect().globalValue` so a workspace value can never name the desk; a folder rule's `activeDesk()` is unchanged. **The worker's own choice, written into 124:** a blank setting counts as unset and falls back to the rule. 124 names `embarch-core-client` (`tasks/api/223`) as the Rust counterpart; `tasks/desk/046` will point the desk at both copies once `api/223` lands. `test/vscode-mock.cjs` gained an `inspect()` so `settings.test.mjs` still activates.
**Merged:** `agent/chat/053-chat-finds-the-desk-by-the-desks-own-rule` (code `5af77da`, ff from `edc9d5e`; doc `169981da`, the worker's `a4c81f1a` cherry-picked onto `78f0a55d`). Re-gated on the merge result: `npm ci`, `npm run build`, `npm run typecheck`, `npm run test:webview` green; `npm test` with the desk gate binary 448 passed, 3 skipped, 0 failed on the second run. **The first run hung:** `test/wire.test.mjs` sat 16 minutes with no output while three cargo gates ran beside it; alone it passed 86 of 86 in 6 s, I killed the hung child, and the full rerun took 45 s. This unit does not touch that file or what it tests, so I read it as a load-sensitive hang, not this branch. **Narrowed in this fold:** `desk/046` stays `blocked`, its `Unparks when:` now naming `api/223` alone. `check-docs.py` 12/12; ownership green on both branches (the code branch is the whole-tree row); client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run in a real VS Code: a scratch desk started with `EMBARCH_DESK_PORT` or `EMBARCH_DESK_CONFIG_DIR` set is found by chat on its next launch with no setting edited; only the unit tests cover that.
**Budget:** PROCEED at dispatch (5-hour 7%, weekly 45%, wave 6); PROCEED at this fold (5-hour 17%, weekly 46%).
**Least sure about:** whether `inspect().globalValue` carries a value set in a remote window's Remote settings; the old `get()` read it, and if `globalValue` holds only local User settings, an engineer who set the desk in Remote settings now silently gets the env-derived default instead (the reviewer read VS Code's model as merging Remote into the user layer but could not confirm it, and the test mock cannot tell).

---

## 2026-11-27 02:37 — umbrella/125 doctor-reads-host-type-schema-version

**Decided:** nothing suite-wide. **Umbrella decision in `decisions/schema-skew.md` amended in place** (its line naming Core's served key; a dated measurement of the old key further down left as written): `doctor`'s authenticated `/status` read takes `host_type_schema_version` first and falls back to `study_designer_schema_version`, and when a body carries both the new key wins, the same rule as `embarch-core-client` (api decision 150), so the suite's two readers agree. The `AuthedStatus` field, the check-11 message and the doc comments use the new name; a Core serving neither key gets a message naming both. One test covers old-only, new-only, both and neither. `open.md` (in reserve, 567 B left, parked under `umbrella/127`) untouched; `interfaces/doctor-chain.md` names neither key. **EMB-314 is complete with this fold** (`api/220`, `core/191`, `umbrella/125`); the old key's removal is core's `open.md` follow-up under decision 162.
**Merged:** `agent/umbrella/125-doctor-reads-host-type-schema-version` (code `88e09ac`, ff from `271da7f`; doc `cede3928`, the worker's `460f062b` cherry-picked onto `c604ce31`). Re-gated on the merge result, built against `embarch-api` `a2ac963` (`api/221`'s core-client): `cargo build`, `cargo test` (438 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-umbrella` checkout to `88e09ac`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a live Core: `embarch doctor` check 11 against a Core before and after `core/191`.
**Budget:** PROCEED at dispatch (5-hour 7%, weekly 45%, wave 6).
**Least sure about:** the two readers differ on one edge the reviewer found: with the new key present but null or not a number, `doctor` returns no version (its fallback fires only on an absent key) while core-client falls back to the old key; Core always serves a `u32`, so I left it, but a hand-written test body or a future Core bug would show it.

---

## 2026-11-27 02:35 — core/191 status-serves-host-type-schema-version

**Decided:** nothing suite-wide. **New core decision 162** (new topic file `decisions/status-schema-key.md`; index row): `GET /status` serves `host_type_schema_version` beside `study_designer_schema_version`, both from `embarch_study_designer::HOST_TYPE_SCHEMA_VERSION`, and a test pins the key set and the two values' equality. Additive; the old key stays until `embarch-core-client` (api decision 150, landed) and `embarch doctor` (`umbrella/125`, landing in this leg) both read the new one **and a released Core has served it**; the removal is a follow-up in `open.md`, not done. `interfaces/hardware.md`'s `/status` row names the new key with its wording trimmed (11,055 to 11,042 B, out of reserve); `open.md` 3,915 to 3,897 B; `spec.md` and `decisions/platform.md` untouched.
**Merged:** `agent/core/191-status-serves-host-type-schema-version` (code `77401e3`, ff from `23eb0f8`; doc `82a014fb`, the worker's `488743f2` cherry-picked onto `c0e8f104`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (670 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Read before merging (a wire type): one added field and its fill in `status_handler`. I fast-forwarded the owner's clean `embarch-core` checkout to `77401e3`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The native Windows build of Core. **Deploy debt:** the installed Core; the old key's removal needs a released Core serving both first.
**Budget:** PROCEED at dispatch (5-hour 7%, weekly 45%, wave 6).
**Least sure about:** what "a released Core has served it" means in practice for the removal follow-up — the suite has no release cadence I can read from here, so that condition may sit unmet for a long time and keep both keys on the wire indefinitely.

---

## 2026-11-27 02:34 — api/221 core-client-takes-the-data-directory-from-topology

**Decided:** nothing suite-wide. **Split at leg start, at `e280b70b`:** EMB-305 (the desk's address and token rule re-derived in four clients) into `tasks/api/223` (`embarch-core-client` holds the Rust clients' one copy, in `token_discovery`'s mold; the desk keeps `paths.rs` and does not take the crate, since it has no path dependency and this one would pull topology and study-designer into it), `ui/130` (blocked on `api/223`), `chat/053` (chat's one TypeScript copy) and `desk/046` (blocked on both: `paths.rs` and the desk's contract doc name the two copies); `filed`, Fleet Working; picks announced before any claim (ts `1795770778.638689`). **Left in Fleet Ready, unsplit, on purpose:** EMB-332, EMB-306, EMB-302, EMB-295 — each is a suite-scope design (a shared home for the systemd unit writer, Core's wire types, config-file resolution, report attestation) and this leg had enough work in four scopes; the next leg should split at least one. Spread sweep: nothing filed (2026-11-27 02:12) — a delta read of the four `open.md` changes since 00:42, all the units' own (umbrella install-core debts, core's "no client sends the quota route (161)", which is a client follow-up in a scope already dispatchable). **Api decision 62 amended in place** (`decisions/client-crate.md`, 11,828 to 11,832 B, still in reserve under `api/222`): token discovery takes the machine data directory from `embarch_topology::machine_data_dir` (`WslHost` under WSL2, `Local` elsewhere), and an unset `ProgramData` is an error naming it through the existing no-token path; the crate's own resolver, the silent `C:\ProgramData` literal, the WSL shell-out and the path translation are deleted, and `dev_file`'s WSL2 `LOCALAPPDATA` read goes through topology's `windows_env_var` and `windows_path_to_wsl`. Every deleted item was private; umbrella calls only `resolve_token`, ui none. **Status fragment folded:** `embarch-token.md` §2's WSL2 discovery line now names topology's resolver (decision 52) and the error on an unset `ProgramData`.
**Merged:** `agent/api/221-core-client-takes-the-data-directory-from-topology` (code `a2ac963`, ff from `62b28ff`; doc `12df6e98`, the worker's `751f19fb` cherry-picked onto `c51c24aa`). Read before merging (a shared crate). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast`, `clippy --all-targets -D warnings` at the workspace root, all green; `embarch-umbrella` rebuilt, tested (438 passed) and clippy-clean against it; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-api` checkout to `a2ac963` so the umbrella gate built against it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Host debt: on the Windows host, the native build of `embarch-core-client`, and under WSL2 the API finding Core's token through topology's shell-out against a live Core; only topology's own tests cover the unset-`ProgramData` error.
**Budget:** PROCEED at leg start (5-hour 5%, weekly 45%, wave 6; four scopes dispatchable, so a wave of 4); PROCEED at dispatch (5-hour 7%, weekly 45%).
**Least sure about:** whether anything outside the suite's repos read the old literal fallback as a feature — a machine with `ProgramData` unset now gets "no token" naming it where it used to get `C:\ProgramData`, and I cannot tell from here whether any engineer's WSL2 setup relied on that.

---

## 2026-11-27 02:06 — umbrella/124 install-core-grants-start-and-stop-only-for-a-stated-container

**Decided:** nothing suite-wide. Recovered from the dead leg: its worker had pushed both branches by 01:24, so I gated and landed them by the presence rule. **New umbrella decision 72** (`decisions/install-core-platforms.md`, index row, `interfaces/install-core.md`, `spec/commands.md`, `open.md`): `install-core --agent-in-container` makes the elevated half write one start-and-stop grant for the engineer's account, and without the flag the script has no grant step at all. **Windows:** one ACE `(A;;RPWPLC;;;<engineer SID>)` (start, stop, query status) on `com.embarch.core`'s descriptor through `sc sdshow`, an edit and `sc sdset`; interrogate, user control, change-config, write-DAC, write-owner and delete are left out on purpose; a pure `add_start_stop_ace` places it at the DACL's end, keeps every other ACE, adds nothing a second time and refuses a descriptor with no DACL; `run_windows_half` recomputes the edit from the transcript's before and after. **Linux:** one polkit rule `/etc/polkit-1/rules.d/50-embarch-core.rules`, root `0644`, allowing `manage-units` on `com.embarch.core.service` for `start` or `stop` by that user only (polkit 0.106 or newer). **The statement is sticky** in `installed-release.json` (`agent_in_container`, `agent_in_container_at`, both `serde(default)`): an install without the flag keeps the earlier statement, because nothing removes a grant; removing one is by hand. **`embarch down` refuses while Core's `/status` shows a study in flight**, and `down --cancel-run` cancels it first through `deploy_dev::clear_study`, as `deploy-core --cancel-run` does; a Core that does not answer has no study. Out of scope and written into 72: the passkey case (no registration exists yet) and Core's unelevated start and stop (`tasks/core/190`). Feature row `features.d/umbrella-166-install-core-grant.md`, assembled in this fold. **Size debt filed by the worker:** `tasks/umbrella/127-compact-umbrella.md`, `blocked`, `In flux: yes`, due 2026-12-18 (`open.md` 4,553 of 5,120 B).
**Merged:** `agent/umbrella/124-install-core-grants-start-and-stop-only-for-a-stated-container` (code `271da7f`, ff from `bdf9f54`; doc `748318c1`, the worker's `0fe0e688` rebased onto `4cc5722c`). Re-gated on the merge result: `cargo build`, `cargo test` (437 passed), `clippy --all-targets -D warnings` clean, built against `embarch-api` `62b28ff` and `embarch-topology` `76694d1`; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, elevated install, nothing ran on a real service manager or polkit. Windows: with `--agent-in-container`, `sc sdshow com.embarch.core` shows the one new ACE and the transcript's before and after agree; unelevated as the engineer, `sc stop`, `sc start` and `sc query` succeed and `sc config com.embarch.core start= demand` is refused (if start or stop is refused, try adding `LO`). Linux: `sudo embarch install-core <release> --agent-in-container`, then as the engineer `systemctl stop` and `start com.embarch.core` succeed with no prompt and `restart` or a unit edit is refused. Both: a second install with and without the flag leaves the grant as it was; whether `install --service` on a re-install keeps the descriptor. `embarch down` against a live Core running a study refuses, and `--cancel-run` cancels then stops.
**Budget:** PROCEED at leg start (5-hour 1%, weekly 45%, wave 6); PROCEED at this fold (5-hour 4%, weekly 45%).
**Least sure about:** whether re-running `install --service` on a re-install recreates the Windows service and drops the ACE while the record still says `agent_in_container`; decision 72 names it as assumed, and if it does, the record overstates what the machine allows until the next flagged install.

---

## 2026-11-27 02:05 — core/189 staging-read-follows-no-link-in-any-folder-of-the-path

**Decided:** nothing suite-wide. Recovered from the dead leg: its worker had pushed both branches by 01:24, so I gated and landed them by the presence rule. This closes EMB-593, the `core/185` reviewer's finding. **Core decision 160 amended in place** (`decisions/flashing.md`; `interfaces/hardware.md`'s `/flash` row now reads "one file name in `staging/`"): under `run --service`, `staging::read` accepts exactly one plain file name directly under `staging/`, relative or absolute-and-inside, and answers `400` for a nested name as for a link, a reparse point, a hardlink, `..` or an outside path. **The worker's choice, written into 160:** no-follow (`O_NOFOLLOW`, `FILE_FLAG_OPEN_REPARSE_POINT`) covers only the last component, and an `openat` chain would have fixed Unix but not Windows, so it removed the nested case rather than take a guarantee on one platform only. 160 now says the staging folder itself is checked, not held; the reviewer confirmed umbrella decisions 69 and 70 leave that folder owned by Administrators or root, so the engineer can change its contents but not replace it. No caller builds a nested name (`api.rs`'s two service branches pass names through).
**Merged:** `agent/core/189-staging-read-follows-no-link-in-any-folder-of-the-path` (code `23eb0f8`, ff from `3d68b0a`; doc `b6b2d760`, the worker's `5ca71bee` rebased onto `8b7375c7`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (670 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean, built against `embarch-topology` `76694d1`; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. On the Windows host with a `run --service` Core: a staged flat name flashes, and `sub\name.hex` answers `400` naming the one-name rule; `core/185`'s junction, symlink and hardlink checks are still owed. The native Windows build of Core. **Deploy debt:** the installed Core.
**Budget:** PROCEED at leg start (5-hour 1%, weekly 45%, wave 6).
**Least sure about:** whether any engineer workflow staged firmware in a subfolder of `staging/` between `core/185` (00:35) and this fold; such a flash now answers `400`, and nothing I can read shows whether anyone did.

---

## 2026-11-27 02:04 — api/220 core-client-reads-host-type-schema-version

**Decided:** nothing suite-wide. Recovered from the dead leg: its worker had pushed both branches by 01:24, so I gated and landed them by the presence rule. **New api decision 150** (`decisions/client-crate.md`, index row): `embarch-core-client`'s `StatusResponse` now has one field, `host_type_schema_version: Option<u32>`, filled from Core's new key and, failing that, the old `study_designer_schema_version`, so it reads the same value from a Core before and after `core/191`. It deserializes through a private `StatusWire` that carries both keys as two `#[serde(default)]` fields, because `#[serde(alias)]` fails a body carrying both as a duplicate field; when the two disagree the new key wins. `post_study`'s two schema checks read the new name. The field rename breaks source for field reads and struct literals; I grepped `embarch-api`, `embarch-ui` and `embarch-umbrella` at `origin/main` and found none (`embarch doctor` parses `/status` itself, `tasks/umbrella/125`). **One wire-visible change:** `StatusResponse` is `Serialize`, and `embarch-ui` re-serializes it to the browser, so that JSON now carries `host_type_schema_version` instead of the old key. No frontend file in `embarch-ui` reads either key; only its Python browser-test stubs feed the old key in as a Core response, which still parses. **Size debt filed by the worker:** `tasks/api/222-compact-api.md`, `open`, `In flux: no`, due 2026-12-10 (`client-crate.md` 11,828 of 12,288 B).
**Merged:** `agent/api/220-core-client-reads-host-type-schema-version` (code `62b28ff`, ff from `5b9f71f`; doc `8b7375c7`, the worker's `6f4e71cb` rebased onto `916b02de`). Re-gated on the merge result: `cargo build --workspace`, `cargo test --workspace --no-fail-fast` (all green, 0 failed), `clippy --workspace --all-targets -D warnings` clean, built against `embarch-topology` `76694d1`; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Read before merging (a shared crate and a wire type). I fast-forwarded the owner's clean `embarch-api` checkout to `62b28ff` so `umbrella/124`'s gate builds against it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a live Core: `embarch-api status` and a study post against a Core before and after `core/191`.
**Budget:** PROCEED at leg start (5-hour 1%, weekly 45%, wave 6).
**Least sure about:** the old key's serialized readers; `embarch-ui`, `embarch-chat`, `embarch-desk` and `embarch-atlas` hold none, and the reviewer confirmed `status --json` and the MCP `status` tool build their JSON by hand, so decision 24's shape counter is untouched — but a reader outside the suite's repos (an owner script) would not show in either search.

---

## 2026-11-27 01:58 — topology/074 one-machine-data-directory-resolver

**Decided:** nothing suite-wide. **Recovery of a dead leg's fold:** the leg that started at 01:06 split EMB-342, EMB-314 and EMB-307 into nine tasks at `6a8165f8` (EMB-307 into `topology/074`, `core/192`, `api/221`, `umbrella/126`; EMB-314 into `api/220`, `core/191`, `umbrella/125`; EMB-342 into `umbrella/124`, `core/190`), claimed `core/189`, `umbrella/124`, `api/220` and `topology/074`, saw all four report at 01:24, merged `topology/074`'s two branches to `origin/main`, assembled its changelog fragment in its leg worktree and died there on a 5-hour 429 before committing the fold or writing any entry. This entry stands in for that leg's split and pick lines too. **New topology decision 52** (`decisions/storage.md`, index row, `spec.md` pointer): `src/machine_dir.rs` is the one resolver for the machine data directory, re-exported at the crate root under `software` or `hardware` — `machine_data_dir(class)` (`Local` the local dir, `WslHost` the Windows host's through a cached shell-out and `/mnt` translation, `Remote` `Ok(None)`), `local_machine_data_dir()`, `windows_env_var(name)` (refuses a name that is not letters, digits or `_` before any shell-out) and `windows_path_to_wsl(path)`; an unset or empty `ProgramData`, or a WSL2 shell-out with nothing usable, is an error naming what was tried, so `core-client`'s silent `C:\ProgramData` goes when `api/221` lands. `TopologyClass` moved to that module and `software::TopologyClass` still names it. **Unparked in this fold:** `core/192`, `api/221` and `umbrella/126`, each set `open` (their `Unparks when:` named only `topology/074`).
**Merged:** `agent/topology/074-one-machine-data-directory-resolver` (code `76694d1`, ff from `5b8d493`; doc `bbfac981`, ff from `ad087be1`), both merged by the dead leg. Re-gated by me on `main` as a shared crate, per every consumer's feature set: `cargo build`; `cargo test` default, `--no-default-features --features software,wire` (39 passed), `--features hardware` (133 passed) and `--all-features` (147 passed plus 15); `clippy --all-targets -D warnings` under default, `software,wire` and `hardware`, all clean. `check-docs.py` 12/12; ownership green on the doc diff (5 paths); client names clean on the code worktree. I fast-forwarded the owner's clean `embarch-topology` checkout from `5b8d493` to `76694d1` so the next units' consumer gates build against it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Host debt: on the WSL2 host, `machine_data_dir(WslHost)` returns the real `%ProgramData%\embarch` through `cmd.exe` or `powershell.exe` and `wslpath`; only an injected shell-out has run.
**Budget:** PROCEED at leg start (5-hour 1% after the reset, weekly 45%, wave 6).
**Least sure about:** whether the dead leg gated this shared crate fully before it merged; I re-ran the whole feature-set gate on `main` and it is green, but no consumer (Core, `embarch-core-client`, `embarch`) has yet been rebuilt against `76694d1` in this unit — the next three units' gates do that.

---

## 2026-11-27 01:04 — umbrella/122 install-core-on-linux-makes-cores-logs-folder

**Decided:** nothing suite-wide. **Umbrella decision 70 amended in place**: on Linux `step_store` also makes `<data dir>/logs/` as `embarch:embarch-users` `0750`, like `study_results/`, so the engineer (in `embarch-users`) can read the core log when Core is down but not write it; `LinPaths` gains `logs`, the dry-run plan names it, a golden assertion covers it. The worker re-read `embarch-core/src` and 70 now states Core's only data-dir-root accesses are `study_results/`, `logs/` and the read of `installed-release.json`. **Size debt paid by a verbatim split, as I directed at dispatch:** decisions 69 and 70 moved into a new `decisions/install-core-platforms.md` (6,794 B after 70's amendment; the reviewer confirmed 69 byte-identical and 70 changed only in its deviations paragraph), 61 and 71 stay in `install-core.md` (11,774 to 5,855 B, out of reserve); index rows for both; `interfaces/install-core.md` links the decisions index, since `check-decision-refs.py` rejects a link into a split topic file. `tasks/umbrella/123` closed `done` in this fold with its `In flux: yes` left as written; every `Must not delete:` item survives. The two stale lines the `umbrella/121` reviewer found are corrected: `spec/commands.md` row 9 (`setup` registers nothing and names `install-core`) and `decisions/setup-reversal.md`'s dry-run line. `open.md` 3,762 to 3,759 B.
**Merged:** `agent/umbrella/122-install-core-on-linux-makes-cores-logs-folder` (code `bdf9f54`, ff from `af433bb`; doc `c4ed552a`, the worker's `6997da79` rebased onto `58623bfd`). Re-gated on the merge result: `cargo build`, `cargo test` (415 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** added to `umbrella/120`'s Linux debt (owner-run, scratch systemd distro): after `sudo embarch install-core <release>`, `/var/lib/embarch/logs/` is `embarch:embarch-users` `0750`, holds a dated core log, and `GET /logs/recent` returns lines.
**Budget:** PROCEED (5-hour 87%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the Windows half has the same question unanswered: a service Core under `NT SERVICE\com.embarch.core` writes `logs/` and `study_results/` under `%ProgramData%\embarch`, which keeps the ACL Windows gave it (69's deviation), and nobody has read whether a virtual service account can create folders there.

---

## 2026-11-27 01:03 — core/187 the-call-log-has-a-quota-the-agent-meets-first

**Decided:** nothing suite-wide. **New core decision 161** (new topic file `decisions/call-log-quota.md`, 2,936 B; index row; `decisions/call-log.md` 158's "Quota: EMB-329" now "a quota (161)"; `interfaces/call-log.md`; `interfaces.md` lists the route; `open.md` 3,915 B, out of reserve by 5 B): `call-log.jsonl` has a byte quota kept in `call-log-quota.json` beside it, read at start, default 1 GiB when absent or unreadable; the size is the log's length on disk. From 90 % a gated call with the agent's token answers `503` naming the size, the quota, `PUT /call-log/quota` and the person's token; at 100 % the person's calls are refused too; the cancel route is served at any size; a quota refusal is not entered (as 158's free-space refusal). `start`, `stop` and `safe_off` entries bypass the gate, so the safe-off lands past the quota. `PUT /call-log/quota {quota_bytes}` (minimum 1): the agent's token gets `403` on every Core, development included (`QUOTA_ROUTES`, `QUOTA_REFUSAL` in `token_store.rs`); lease-open and not gated, so a full log's person can still reach it; enters a `quota` entry first, then writes the file by temp and rename; returns `{quota_bytes, previous_bytes, size_bytes}`. `GET /call-log` adds `size_bytes` and `quota_bytes`. Route count 73 to 74. 1 GiB, 90 % and 100 % are the owner's chosen values, not measured, and 161 says so. **The worker's own choice, recorded in 161:** a host study's per-step `cannot_log()` uses the person's 100 % mark, so a study the agent started is not cut off at 90 %. No client sends the new route yet (`open.md`, a follow-up for a client scope). Feature row `features.d/core-403-call-log-quota.md` (new), assembled in this fold.
**Merged:** `agent/core/187-the-call-log-has-a-quota-the-agent-meets-first` (code `3d68b0a`, ff from `4805d97`; doc `58623bfd`, ff from `8bbb6735`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (669 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Read before merging for wire impact: `embarch-core-client` has no `deny_unknown_fields`, and api's `verify` filters run-log entries by `type`, so the added `GET` fields and the `quota` entry type break no reader I found.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; no hardware path. The native Windows build of Core (no Windows arm touched). **Deploy debt:** the installed Core.
**Budget:** PROCEED at this dispatch (5-hour 85%, inside the 60-minute reset grace, weekly 43%); PROCEED at this fold (5-hour 87%, weekly 43%).
**Least sure about:** whether a study the agent started should run on past 90 %: the worker chose the person's 100 % mark for `cannot_log()` so a study is not cut off mid-run, which keeps the agent's 10 % margin open to every step of an agent-started study, and nothing in the issue decided it either way.

---

## 2026-11-27 00:52 — umbrella/121 setup-and-doctor-stop-naming-a-core-install-that-registers-nothing

**Decided:** nothing suite-wide. **New umbrella decision 71** (`decisions/install-core.md`, now 11,774 of 12,288 B, in reserve; index row; `interfaces/doctor-chain.md` row 2; `open.md` 3,818 to 3,762 B): `setup` runs no `embarch-core install` at all, since `install --service` needs a record only a verified signed release writes and `setup` holds none. The Local arm no longer says "Installed and started."; it says nothing was registered and names `sudo embarch install-core <release>`, and a real run exits 1 (a dry run keeps its exit); macOS says `install-core` is not built there. The `wsl-host` and `remote` arms name `install-core` (the elevated Windows form for `wsl-host`), then the installed binary's `install --service --bind 0.0.0.0`, because `install-core` binds the `Local` address (69) and Core refuses a binary the record does not list. Doctor check 2 and check 17 fix lines name the same two routes; check 17 no longer offers `embarch setup`; the `up` failure and the non-WSL2 `deploy-core` messages corrected too. Shared text lives in `setup.rs` (`registration_route`, `rebind_route`). **Size debt filed:** `tasks/umbrella/123-compact-umbrella.md`, blocked, `In flux: yes`, due 2026-12-18. **Correction to `core/188`'s entry:** its spread-sweep line should read Spread sweep: nothing filed (2026-11-27 00:42) — I typed a time 14 minutes ahead of the fold's stamp, and this line is the newest, so it governs.
**Merged:** `agent/umbrella/121-setup-and-doctor-stop-naming-a-core-install-that-registers-nothing` (code `af433bb`, ff from `b641c2a`; doc `b2b26d5e`, the worker's `94a6203e` rebased onto `d063b4bb`). Re-gated on the merge result: `cargo build`, `cargo test` (415 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; text only, nothing registered. `open.md`'s existing check 17 live-verification debt (owner-run, reinstalls the service) now names the `--service` form.
**Budget:** PROCEED (5-hour 82%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the reviewer found two stale lines this unit did not touch — `embarch-umbrella/spec/commands.md` row 9 still says `setup` will "install Core as a service", and `decisions/setup-reversal.md` line 23 has the dry run naming `embarch-core install --bind`; I handed both to `umbrella/122`, the next umbrella unit, rather than file an issue, so if that unit misses them nothing else will.

---

## 2026-11-27 00:51 — core/188 every-probe-open-steps-around-cores-own-hold

**Decided:** nothing suite-wide. Split at leg start, at `1e79bff0`: EMB-592 into `tasks/core/188` (`verify-only`), EMB-593 into `core/189`, EMB-594 into `umbrella/122`; all `filed`, Fleet Working; picks announced before any claim (ts `1795765384.910169`). Spread sweep: nothing filed (2026-11-27 01:05) — a delta read: only `embarch-umbrella/open.md` changed since the 00:25 sweep (`umbrella/119`, `120` rewording their own debts), nothing new in another scope. **Core decision 159 amended in place** (`decisions/port-hold.md`): a new `probe_hold::around_role(role, f)` looks up the role's enrolled probe serial and runs `around` on it, or runs `f` unchanged when the role has none; `POST /validate` (role and serial), `POST /probes/enroll` with a `probe_serial`, `enforce_dev_bench_gate` (which covers `GET /dev-bench/hello` and `POST /study`, so `study.rs`'s other two sites needed no edit) and the test executor's `validated_id` now close and reopen the held probe. **Named uncovered in 159:** `POST /probes/enroll` with no `probe_serial`, which learns the serial only by opening the one attached probe. The worker grepped every caller of `validate_*`, `open_probe`, `attach::attach` and `enroll_reporting`; the reviewer re-grepped and agrees. No change to `interfaces/hardware.md`, `open.md` or `spec.md`.
**Merged:** `agent/core/188-every-probe-open-steps-around-cores-own-hold` (code `4805d97`, ff from `364cf99`; doc `d063b4bb`, ff from `29eb92d7`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (665 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a real J-Link and a CMSIS-DAP or ST-Link, with the probe held by a lease: `POST /validate` by role and by serial; `POST /study` and `GET /dev-bench/hello`; `POST /probes/enroll` with a `probe_serial` — each succeeds and logs the close and reopen. Whether a second open of a held probe fails on each probe kind is still unmeasured. The native Windows build of Core. **Deploy debt:** the installed Core; `core/184`'s "do not deploy past `576cb04` until EMB-592 lands" is now discharged at `4805d97`, subject to the bench check above.
**Budget:** PROCEED at leg start (5-hour 80%, weekly 42%, wave 6; only two scopes dispatchable, so a wave of 2); PROCEED at this fold (5-hour 82%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the new test drives `around_role` with the fake opener, not the `POST /validate` or study-gate handlers under a live lease, because the identity gate needs the topology store and a real probe; the wiring at each handler is read, not run.

---

## 2026-11-27 00:38 — umbrella/120 install-core-gives-core-a-user-and-a-protected-store-on-linux

**Decided:** nothing suite-wide. **New umbrella decision 70** (`decisions/install-core.md`, now 9,385 B; index row; `interfaces/install-core.md`; `spec/commands.md`): on Linux, `install-core` runs one generated POSIX `sh` script as the root calling process (`sh -s`, script on stdin, no file written, no `sudo` re-launch), reusing `umbrella/119`'s `parse_transcript` and `Host` seam, so the steps and transcript lines match Windows; Windows behaviour unchanged. Step 0 refuses before any write when not root, `systemctl` is missing, the engineer account is missing, or `store/` is a link, not a folder, or not owned by `embarch`. Then the `embarch` system user and `embarch-users` group, `/opt/embarch/core/<version>/`, `store/` `embarch` `0700`, firmware `staging/` `root:embarch-users` `0770`, token files `0640 embarch:embarch-users` when absent, `install --service --bind`, start and `core-fingerprint`. Core's unit writer already sets `User=embarch` on Linux (`service.rs`), so no Core task was needed for that. **Deviations, written into 70:** the engineer is `$SUDO_USER`, validated as a plain account name that is not `root` or `embarch`, unset refused; the unit name `com.embarch.core` is assumed; only the default data dir; the engineer needs a fresh login for the new group; and `study_results/` is created `embarch:embarch-users` `0750` because the data dir stays `root` `0755` and Core writes run directories there (core 129). The reviewer found the same case for `logs/`, which 70 misses: **EMB-594**. `embarch-token.md` §5 still true (nothing service-validated), so no status fragment. `open.md` 3,915 to 3,818 B.
**Merged:** `agent/umbrella/120-install-core-gives-core-a-user-and-a-protected-store-on-linux` (code `b641c2a`, ff from `060380b`; doc `a793da53`, the worker's `474a89df` rebased onto `1e41a6bb`). Re-gated: `cargo build`, `cargo test` (412 passed), `clippy --all-targets -D warnings` clean; the script checked with `sh -n` and the store refusal run for real against a temp dir by the worker. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-594
**Hardware debts:** owner-run, in a scratch systemd distro: `sudo embarch install-core <a signed release>` reports all seven steps OK; `systemctl cat com.embarch.core` shows `User=embarch`; `store/` is `embarch` `0700`; both token files are `0640 embarch:embarch-users` and the engineer reads `token` after logging in again; `core-fingerprint` equals `/status`'s `keyid`; a root-made `store/` is refused with nothing written. Assumed, not measured: `useradd --system --user-group`, `usermod -aG`, GNU `stat -c`, the unit file name, Core accepting `0640` token files it did not create.
**Budget:** PROCEED (5-hour 78%, weekly 42%, resets in 1h12m).
**Least sure about:** whether `logs/` is the last data-dir-root write a service Core makes as `embarch`; the reviewer read `embarch-core/src` and found no other, but the only proof is the first install in a scratch distro, and on Windows the same question is answered by `%ProgramData%`'s default ACL, which nobody has read for a virtual service account.

---

## 2026-11-27 00:35 — core/185 a-service-core-takes-firmware-only-from-its-staging-folder

**Decided:** nothing suite-wide. **New core decision 160** (`decisions/flashing.md`, now 8,134 B; index row "10, 18, 21, 32, 82, 84, 160"; a 48-byte note in `interfaces/hardware.md`, now 11,055 B, kept out of reserve): under `run --service`, `/flash`'s JSON `firmware_path` and `manifest_path` are read only through `staging::read` (`src/staging.rs`, the one helper a later path-taking route must call), which resolves each component under `<data dir>/staging/` and answers `400` before opening for a symlink, a junction or other reparse point, a hardlink (link count above 1), `..`, or an absolute path outside; a missing staging folder is refused, never created. The bytes are read from the opened handle, written to a temp file and flashed from there, so the flashed-image record's path reads `(uploaded)` as for multipart. Multipart and a development Core are unchanged. Decisions 10 and 18 were not amended; the reviewer found nothing in them that 160 contradicts. The staging folder matches what `umbrella/119` (umbrella decision 69) now creates on Windows.
**Merged:** `agent/core/185-a-service-core-takes-firmware-only-from-its-staging-folder` (code `364cf99`, ff from `576cb04`; doc `401c0070`, ff from `fe60332d`). Re-gated: `cargo build`, `cargo test --no-fail-fast` (664 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; the Windows branches of `staging.rs` type-checked by the worker in a throwaway crate (hidapi blocks the whole crate under WSL). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-593
**Hardware debts:** on the Windows host with a `run --service` Core and `%ProgramData%\embarch\staging\` present: a staged file flashes by name; a path through a `mklink /J` junction, a `mklink` symlink and a `mklink /H` hardlink each answer `400`. The native Windows build of Core. **Deploy debt:** the installed Core (and see `core/184`'s entry: not past `576cb04` until EMB-592 lands).
**Budget:** PROCEED (5-hour 75%, weekly 42%).
**Least sure about:** decision 160 says a link swapped in after the check is never followed, and EMB-593 shows that holds only for a flat name: `staging::read` lstat-checks each component and then opens the joined path with a no-follow flag that covers the last component alone, so a nested parent swapped for a link in between is followed (it needs a writer inside `staging/`). The worker reported the stronger claim; I kept the merge (additive, gate green) and left the fix, or a narrowed 160, to the next core unit.

---

## 2026-11-27 00:27 — umbrella/119 install-core-puts-core-under-its-own-account-on-windows

**Decided:** nothing suite-wide. **New umbrella decision 69** (`decisions/install-core.md`, now 6,293 B; index row; `interfaces/install-core.md`; `spec/commands.md`): on Windows, `install-core` follows its verify-and-stage half with one generated PowerShell script, run elevated through `Start-Process -Verb RunAs` and logged from inside, in the issue's order: step 0 refuses a store owned by anyone but Administrators, SYSTEM or the service SID; then the binary into `%ProgramFiles%\EmbArch\core\<version>\`, `store\`, the firmware `staging\`, the token files when absent (32 random bytes as 64 hex, which matches Core's own token shape), `install --service --bind`, then start and `core-fingerprint`. The transcript parser fails a silent step, a missing `=== done ===`, a bad fingerprint or a missing transcript. `installed-release.json` gains `binary_sha256` (array of the staged `embarch-core` hash, `binaries` kept, `serde(default)` so old records read), which Core's `install --service` (157) needs. **Deviations, written into 69:** verify-and-stage still runs unelevated (self-elevation stays a later unit; the engineer's SID is `whoami` there); only the default data dir gets the Windows half; `--bind` is the topology's `Local` address (wrong for a WSL2 host, which 61 already defers); `%ProgramData%\embarch` keeps the ACL Windows gave it. **Size debt paid:** `open.md` 4,634 to 3,915 B, out of reserve with `umbrella/111`'s `Must not delete:` list intact, so I closed `umbrella/111` `done` in this fold (its `In flux: yes` left as written). **My own edit in this fold:** `embarch-core/interfaces/installed-release.md` no longer says the record's writer is a later task; it names `install-core` (decisions 61, 69).
**Merged:** `agent/umbrella/119-install-core-puts-core-under-its-own-account-on-windows` (code `060380b`, ff from `5533608`; doc `4180be6a`, the worker's `8fe2f8fc` rebased onto `878605cc`). Re-gated: `cargo build`, `cargo test` (395 passed), `clippy --all-targets -D warnings` clean; Windows code type-checked by the worker in a throwaway crate (`aws-lc-sys` blocks the whole crate under WSL). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, elevated Windows shell: `install-core <signed release> --data-dir <temp>` writes the record and the staging ACL lists only Administrators and SYSTEM, a tampered release writes nothing; a default-dir install reports all six steps OK, `sc qc com.embarch.core` shows `NT SERVICE\com.embarch.core`, the store ACL is the service, SYSTEM and Administrators, `core-fingerprint` equals `/status`'s `keyid`; an engineer-made store is refused at step 0. Assumed and never run: the `sc showsid` parse, PowerShell 5.1's handling of native stderr, Core accepting the script-written tokens.
**Budget:** PROCEED (5-hour 72%, weekly 42%).
**Least sure about:** the whole Windows half has run only as text against a fake host; the first elevated install is the first time any of its six steps meets a real ACL or service manager, and `sc showsid`'s output parse is the step I would bet on failing first.

---

## 2026-11-27 00:25 — core/184 core-holds-its-probes-while-a-lease-or-study-holds-the-bench

**Decided:** nothing suite-wide. Split at leg start, at `6f0a39a9`: EMB-339 into `tasks/umbrella/119` (the elevated Windows step) and `umbrella/121` (`setup` and `doctor` stop naming `install --bind`, the finding comment `core/183` left on EMB-339), EMB-340 into `umbrella/120`, EMB-329 into `core/187`; all `filed`, Fleet Working; picks announced before any claim (ts `1795763673.393199`). Found while splitting: umbrella's `installed-release.json` had a `binaries` map and no `binary_sha256`, which Core's `install --service` (157) requires, so `umbrella/119` was told to add it. Spread sweep: nothing filed (2026-11-27 00:25) — a delta read: only `embarch-api/open.md` and `embarch-core/open.md` changed since the 2026-11-26 19:55 sweep, and neither names new work outside core. **New core decision 159** (`decisions/port-hold.md`, now 6,123 B; index row "130, 159"; `interfaces/signing.md` gains `observed.probes_held`): the decision-130 holder also opens each enrolled board's probe at lease take or study start, keyed by serial. **Deviation from the issue's direction, written into 159:** a Core call does not borrow the held probe, it closes and reopens it (`probe_hold::around`), because the topology identity gate opens the probe itself and probe-rs 0.31's `Session` consumes the `Probe`; the windows between are named as not covered. A failed open at the take, or a failed reopen, drops the probe from the hold and the record, logged only. **Filed from the review: EMB-592** (Fleet Ready, core): `POST /validate`, `test_executor.rs` and the dev-bench identity gate open the probe without `around`, so under a lease they run against Core's own hold.
**Merged:** `agent/core/184-core-holds-its-probes-while-a-lease-or-study-holds-the-bench` (code `576cb04`, ff from `8b7dbe1`; doc `b2387867`, ff from `c7936e5b`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (659 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-592
**Hardware debts:** on a real J-Link and a CMSIS-DAP or ST-Link under a lease: a second Core cannot open the held probe; `probes_held` lists its serial in the signed record; an `nrfutil` flash on the nRF54L15 closes and reopens the probe as logged; whether a second open fails on Windows is assumed. Also, per EMB-592, validation under a lease and a study started under a lease. The native Windows build of Core. **Deploy debt:** the installed Core, and **do not deploy a Core at or past `576cb04` to the bench until EMB-592 lands** — under a lease, a study's dev-bench gate may fail against Core's own probe hold.
**Budget:** PROCEED at leg start (5-hour 64%, weekly 41%, wave 6); PROCEED after wave 1 (5-hour 72%, weekly 42%).
**Least sure about:** whether a second open of a held probe actually fails on the bench's probes; if it does not, EMB-592 is only a coverage gap, and if it does, `576cb04` breaks studies under a lease until it lands — the fake opener cannot tell which.

---

## 2026-11-27 00:07 — core/182 core-refuses-a-hardware-call-it-cannot-log

**Decided:** nothing suite-wide. Split at `a1798eb0` (see `api/218`'s entry in the 2026-11-26 fold), dispatched alone as wave 2 once `core/183` had landed. **New core decision 158** (`decisions/call-log.md`, 10,990 of 12,288 B; index row; 122's "Not here" line now points to it; `interfaces/call-log.md`; `open.md`): Core keeps a **cannot-log** state, set when an append fails (any error, a chain that does not verify included) or when free space falls below the reserved tail, cleared by the next append that succeeds with room left; the space check is redone at each gated call. In that state every gated route answers `503` naming the call log and the reason, except `POST /study/{id}/cancel`; the gate sits inside auth and outside the lease layer, and the lease-open routes (`GET /call-log` among them) are not gated. After a failed write, the first refusal once the writer recovers is itself entered and serves as the probe; a refusal for lack of space is not entered, so the tail stays for the safe-off. A host study asks the gate before each step, `Repeat` pass and teardown step; a cannot-log answer stops the step list and Core's safe-off (156) runs in place of the teardown, `events.json` carrying `teardown_replaced` and the stop reason. `start`, `stop` and the new per-result `safe_off` entries bypass the gate. **Reserved tail:** (declared safe-off lines + signals + 2) × 8,192 B, read from the declarations at each gate; the 8,192 B per entry is assumed, not measured, and 158 says so. A `Store` trait in `call_log.rs` is the seam (append and free space: `statvfs` on Unix, `GetDiskFreeSpaceExW` on Windows, with the `Win32_Storage_FileSystem` feature added to `windows-sys`). **Two deviations, both written into 158 and `open.md`:** a device study is not stopped by the cannot-log state (its steps run in the bench firmware and Core can only ask it to stop); a call whose entry fails after its handler ran is still served, and the next call is the first refused. Feature row `features.d/core-402-call-log-fails-closed.md` (new). **Unblocks in Linear:** EMB-329 (the call log's quota) once `finish` moves EMB-328 to Done. **Day fold in this unit:** an `embarch-log-folder` subagent folded 2026-11-26's 51 unit entries into one (186 SHAs, 51 reviewer lines, 11 debt lines kept; its first `--apply` was refused for 17 dropped SHAs and it added a reference-points line); I rolled 2026-11-24 into `log-archive/` (log 133,479 to 92,676 B). `check-client-names.py --suite --history`: every repo clean.
**Merged:** `agent/core/182-core-refuses-a-hardware-call-it-cannot-log` (code `8b7dbe1`, ff from `4ae97c6`; doc `60c0fe66`, the worker's `5bf4061e` rebased onto `264c57bc`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (654 passed, 2 ignored, 0 failed, plus 2), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches (7 doc paths); client names clean on the code worktree. The feature row assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core, now also owed for the `GetDiskFreeSpaceExW` call and the new `windows-sys` feature, which no compiler has built. A real full disk under a live Core; a real host study whose teardown is replaced by the safe-off against a real instrument. **Deploy debt:** the installed Core.
**Budget:** PROCEED at leg start (5-hour 51%, weekly 39%, wave 6, capped at 4 units); PROCEED at this dispatch (5-hour 59%, weekly 40%).
**Least sure about:** decision 95's "Teardown always runs" (`decisions/host-study.md` line 17) is now narrowed by 158 but not amended, which the reviewer called a doc-consistency gap rather than a contradiction; 95 is already 799 B over the per-decision cap, so I left it rather than grow it, and the next compaction of 95 should carry 158's exception.

---

## 2026-11-26 — 51 units

*Folded by an embarch-log-folder agent on 2026-11-27: per-unit narrative reasoning, gate transcripts (test counts, clippy and check-docs runs), budget lines and "least sure about" notes dropped; git holds the diffs and the decisions themselves. Every SHA, reviewer line, board-naming debt and blocked line kept, one block per unit, newest first, each with a one-to-three-line gist of what it decided. The day's twelve "Leg end, to carry" paragraphs are folded into the carry-forward below.*

**Carry forward (state at the last leg's end, 23:55).**
- **Four clear legs, 51 units, one blocked half.** Every leg landed 4 of 4; only `ui/124`'s prompt-modal half was left `blocked` (14:18, since landed at 18:08). Budget at the last recorded leg end: PROCEED, 5-hour about 53%, weekly about 40%.
- **Suite-level decisions made on the owner's behalf (the owner's to strike):** three parked tasks run by a leg's own hands after a silent announcement window. `suite/064` (21:56): `suite/agent-guide.md` §1.1 places all 64 registered tools (allow gains `run_test`, `test_status`, `test_show`, `test_pending`, `test_plan`, `test_propose`, `cancel_study`, `export_audio`; ask gains `test_add`; `ledger_*` gone; retired stub `embarch-api/interfaces/tools-ledger.md` deleted). `suite/065` (22:48): `embarch-core-client`'s `StudyEvent::PromptPending` gains optional `prompt_kind` (api decision 137 amended in place; ui 113's "no kind until EMB-577" line corrected). `api/217` (22:36) folded `resume_test` into the agent guide's allow list, now 65 tools. `api/206` (17:36): one cross-repo landing by my own hands (`embarch-ui` consumer commit `59c5e5a`) after a 30-minute announcement with no reply; a new `pub` field on a struct a consumer builds by literal is not "additive". Also marked the owner's to strike: dev-bench decision 69 (`pd times`, `dev-bench/053`) and EMB-461's `chat/050` (container login; plan choices 11 and 22).
- **Recurring worker and dispatch faults:** workers cited the task number instead of the decision number in code comments three times across two legs (`api/216`, `core/172`, `core/168`); landing fixed each. A dispatch note should **quote a field's source, never paraphrase its meaning** (`api/216`'s "`U` is `k x u`" was my error and printed `U` doubled until the reviewer caught it: EMB-590, closed by the fix `419d020` / `13c683e7`). `api/213`'s worker guessed Core's `n_of_m` shape from a stale main checkout (fixed at landing). The gate's `<this repo>/scripts/desk-gate-bin.py` is the framework repo's, not the instance's (`embarch-fleet/scripts/`); a wrong path returns an empty desk binary and a silent `npm test`. Shell `for` and `until ... done` loops are unallowlistable: claim and poll one command per task. A 150-minute barrier at 14:29 (`chat/048`'s flake hunt) left three landed-ready units waiting; the foreground call ticks nothing while open.
- **Open reviewer note, not filed:** `api/208`'s copied `judge` reads an empty reply with no `reply_bytes` as TimedOut, so an older `events.json` that places its steps but predates `reply_bytes` and recorded Fail would fail `verify` check 2; whether such a zip exists was not checked. Known consequence of `core/183`: no path in the suite can register a Core service until EMB-339 or EMB-340 lands (`embarch setup` on a Local topology prints "Installed and started." while registering nothing); the owner's existing Windows service is untouched.
- **Dispatchable now:** `tasks/core/182` (EMB-328, `hw:none`), `core/184` (EMB-327), `core/185` (EMB-330, `verify-only`) are filed, with `core/183` landed; Fleet Ready: core EMB-324 (unblocks 339, 340, then 342) and EMB-329 (waits behind EMB-325, now Done); the next leg owes a split. The `Scope: suite` audit issues (EMB-295, 302, 305, 306, 307, 314, 332) are §8 work, none taken; EMB-303 was split as two single-scope tasks (`chat/052`, `ui/129`, both landed) rather than run as `suite`, and the other doc-only ones may split the same way where each half stays inside one ownership row. EMB-332 is genuinely two code repos and stays §8.
- **Hardware / bench:** hardware buffer last refreshed 22:52: Core reachable, dev-bench and DUT not attached; bench tasks `api/059` and `dev-bench/038` stay `open`. Debts owed this day are in the per-unit lines (largest: `core/181`'s five bench steps, `core/183`'s first elevated install, the PD bench's two characterisation sessions, and the native Windows build of Core, never compiled here, owed by `core/168`, `169`, `170`, `167`, `178`, `180`, `181`, `183`).
- **Deploy debts:** the installed Core runs none of today's Core work until redeployed (no Test-run record signing, no amended study record, no smoke check, no output safe-off at start or stop, no `install --service` registration). `core/183`: a plain `install --bind` from a new build registers nothing and names `embarch deploy-core`.
- **Size debts:** none overdue. Reserve files all filed and parked: `umbrella/111`, `dev-bench/052`; `api/218` (paid in this fold's last leg) and `core/186-compact-core.md` (`spec.md` 9,082 B, `decisions/platform.md` 11,527 of 12,288 B, due 2026-12-10, `open`). Chat decision 123 is 36 B under the per-decision cap.
- **Stale, the owner's:** `embarch-analog-capture-proposal.md` is in neither `reserved` nor `fleet_writable` (`check-ownership.py --supervisor`), unclassified all day.
- **Refill and spread:** Spread sweep: nothing filed (2026-11-26 19:55) is the newest; every other leg split Fleet Ready instead of sweeping. The 19:55 sweep read 15 source files changed since 2026-11-24 00:23 and found nothing host-side and dispatchable in a new scope.
- **Reference points, kept because the ledger counts them:** the leg-start split commits (the log's `Split ... at` SHAs): `dbf2088a` (14:29 leg), `6967737b` (14:02), `a429277b` (17:43), `e2ff47f5` (18:14), `17282b6d` (19:24), `28d227f9` (19:56), `7ba4ce56` (21:15), `b3b44903` (20:58), `1f421053` (21:22), `abdacdc8` (22:02), `af80de62` (11:33); also `b31a7d8b`, `b65f3f9c`, and `7391457` (the `hil_check.rs` hunk of the reverted `study-designer/099`, applied by the worker in a throwaway crate worktree to prove `api/204`'s fix). `#embarch-fleet` thread timestamps of the announcement windows: `1795750706` (`suite/064`), `1795753355` (`suite/065`), `1795755747`, `1795758923` (leg picks).

---

### 23:55 — core/183 install-service-registers-only-a-listed-release-under-cores-own-account
New core decision 157 (`decisions/platform.md`, index row; new `interfaces/installed-release.md` with a row in `interfaces.md`; `spec.md` §3): `install --service --bind <addr>` hashes its own binary and refuses, before any elevation or service-manager call, unless `<data …
**Merged:** `agent/core/183-install-service-registers-only-a-listed-release-under-cores-own-account` (code `4ae97c6`, ff from `c0a1b43`; doc `83d1d58f`, the worker's `bc761904` rebased onto `2d216b1e`).
**Reviewer:** no findings.
**Hardware debts:** the first elevated install on Windows and on Linux: `sc qc` and `systemctl cat` show the account and `run --service --bind`; `update` refuses a `--service` registration; the in-place rewrite still sets the account; the virtual account can write `store/` (EMB-339's part). The Windows-gated code (`apply_windows_account`, the registry read in `registered_command`) has not been type-checked: `cargo check --target x86_64-pc-windows-msvc` fails in hidapi's `build.rs` under WSL, the known limit, so the native Windows build of Core is owed. **Deploy debt:** the installed Core; note that a plain `install --bind` from a new build registers nothing.

### 23:54 — ui/129 ui-points-at-chats-launcher-decisions
The second half of EMB-303 (first half `chat/052`, chat decision 123). Ui decision 28 is now a one-line pointer to chat 123 (heading kept); decision 3's first paragraph says the launcher lives in `embarch-chat` (chat 29) and points at 123 for the thin-launcher stance, keeping ui's own `.vsix` and …
**Merged:** `agent/ui/129-ui-points-at-chats-launcher-decisions` (doc `971c32d6`, the worker's `1d5e74eb` rebased onto `db3fad7c`; code: the worker touched none, and my comment fix is code `db0562e` on embarch-ui main, ff from `7575d64`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:51 — api/218 compact-api
Split at leg start, at `a1798eb0`: EMB-328 into `tasks/core/182`, EMB-324 into `core/183`, EMB-327 into `core/184`, EMB-330 into `core/185` (all `filed`, Fleet Working); picks announced before any claim (ts `1795761780.530059`) …
**Merged:** `agent/api/218-compact-api` (code none, embarch-api untouched; doc `db3fad7c`, ff from `8595cfb3`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:36 — chat/052 chat-records-the-vs-code-launchers-decisions
New chat decision 123 (`decisions/launcher.md`, a new topic file, 4,060 B against the 4,096 B per-decision cap; index row): the VS Code launcher's behaviour, moved from `embarch-ui` decisions 3, 28 and 101 and restated in chat's voice …
**Merged:** `agent/chat/052-chat-records-the-vs-code-launchers-decisions` (code `edc9d5e`, ff; doc `d5a390ab`, the worker's `52b671db` cherry-picked onto `e332c13a`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:35 — core/181 core-switches-every-declared-output-off-at-start-and-graceful-stop
New core decision 156 (`decisions/call-log.md`, beside 122; index row; `interfaces/call-log.md` gives the `start` and `stop` entry shapes and the safe-off result shape exactly, for EMB-328 and EMB-329 to build on …
**Merged:** `agent/core/181-core-switches-every-declared-output-off-at-start-and-graceful-stop` (code `c0a1b43`, ff; doc `2a793a4f`, the worker's `d5256043` cherry-picked onto `bb2cdea7`).
**Reviewer:** no findings.
**Hardware debts:** five steps written in the task file for a real instrument and bench board: the safe-off at start with outputs switched on first; SIGTERM, Ctrl-C and SCM Stop with outputs on, timing the SCM stop; `kill -9` then the next start; an unplugged instrument at start; a stop mid host study. The native Windows build of Core (the `cfg(not(unix))` arm of `shutdown_signal` was not compiled here). **Deploy debt:** the installed Core.

### 23:34 — api/219 verify-judges-a-refused-exchange-step-under-its-recorded-target
New api decision 149 (`decisions/verify-test-run.md`, beside 146; index row "146, 149"; `interfaces/verify.md` check 3 row; 146's "what the zip cannot give" paragraph points to it): `verify` check 3 judges an `Exchange` step row carrying `target` `"dut"` or `"bench"` (core 155) under that target …
**Merged:** `agent/api/219-verify-judges-a-refused-exchange-step-under-its-recorded-target` (code `5b9f71f`, ff; doc `32fc7721` and `f91e2f7f`, the worker's `fb56c4e3` and `8be34e76` cherry-picked onto `4bc0e35e`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:33 — ui/128 the-prompt-modal-takes-a-test-run-prompts-kind-from-the-event
Split this leg, at `39559d93`: EMB-591 into this task, EMB-589 into `api/219`, EMB-325 into `core/181`, EMB-303 into `chat/052` plus `tasks/ui/129` (blocked on `chat/052`; ui scope already had this unit in the wave, and 129 needs 052's decision number). All `filed`, Fleet Working …
**Merged:** `agent/ui/128-the-prompt-modal-takes-a-test-run-prompts-kind-from-the-event` (code `7575d64`, ff; doc `a5ab8480`, ff).
**Reviewer:** no findings.
**Hardware debts:** none

### 22:48 — suite/065 the-core-client-reads-a-prompt-events-kind
suite-level, on the owner's behalf, after a silent window: `embarch-core-client`'s `StudyEvent::PromptPending` gains an optional `prompt_kind` (`PromptKind`, `#[serde(default, skip_serializing_if = "Option::is_none")]`), and `as_pending_prompt` and `prompt_pending` carry it both ways, so a Test run's event parsed by the client names its kind without the `GET /study/{id}` poll …
**Merged:** no branch merge: my own commits on each `main`, sequenced shared crate first: api `5ba0749` (ff from `2b54d0d`), then ui `0b08867` (ff), then doc `ffcbc725`, then this fold.
**Reviewer:** no findings.
**Hardware debts:** none

### 22:36 — api/217 embarch-api-resumes-an-interrupted-test-run
suite-level fold, on the owner's behalf: `suite/agent-guide.md` §1.1 places the new MCP tool `resume_test` in allow, beside `run_test`, and now counts 65 tools (65 `#[tool(` attributes in `src/tools.rs` on `origin/main`, 64 before this unit); the paragraph under it says `run_test` and `resume_test` both only prepare, the go being the engineer's on Core's card …
**Merged:** `agent/api/217-embarch-api-resumes-an-interrupted-test-run` (code `2b54d0d`, ff from `419d020`; doc `65b94f7c`, ff from `2490adb7`).
**Reviewer:** no findings.
**Hardware debts:** none

### 22:23 — core/180 a-test-runs-exchange-steps-record-their-target-in-the-signed-files
New core decision 155 (`decisions/test-run-target.md`, a new topic file; index row; `interfaces/host-studies.md` names the fields): each `Exchange` step row of `events.json` gains `signal` (the signal name) and `target` (`"dut"` or `"bench"`), on `Exchange` rows only, both `Option` with …
**Merged:** `agent/core/180-a-test-runs-exchange-steps-record-their-target-in-the-signed-files` (code `ef7416a`, ff from `b85a419`; doc `f82ed294`, the worker's `23275059` cherry-picked onto `e8aecf77`).
**Reviewer:** no findings.
**Hardware debts:** a real Test run on the bench whose study addresses a DUT signal and a bench-board signal: only fake-backend tests have exercised the live topology lookup that now writes `target`. The native Windows build of Core. **Deploy debt:** the installed Core.

### 22:22 — api/216 a-test-report-prints-each-limits-decision-rule-and-verify-rebuilds-it
New api decision 147 (`decisions/publish-test-limits.md`, index row): the Test PDF gains a "Limits and decision rule" section after the tests table, one row per limit of core decision 154's `limits` (measurement, bounds and unit, rule and its `w` multiple, `w`, `U` with its `k`), "U not declared" …
**Merged:** `agent/api/216-a-test-report-prints-each-limits-decision-rule-and-verify-rebuilds-it` (code `002ecc2`, ff from `48634b0`, then my `419d020`; doc `e8aecf77`, ff from `fef9c736`, then my `13c683e7`).
**Reviewer:** 1 finding — EMB-590
**Hardware debts:** none

### 21:56 — suite/064 the-agent-guide-places-the-test-tools
suite-wide, on the owner's behalf, after a silent window: `suite/agent-guide.md` §1.1 now places all 64 tools `embarch-api/src/tools.rs` registers on `origin/main` (`48634b0`; checked by diffing the registered names against the two lists: same set, each once) …
**Merged:** no branch: the leg's own commit `b3df6724` on `main`, then this fold. `check-docs.py` 12/12 on the result; `check-ownership.py --supervisor` over the leg's diff: nothing owner-reserved.
**Reviewer:** no findings.
**Hardware debts:** none

### 21:53 — core/179 a-test-runs-report-data-states-each-limits-decision-rule
New core decision 154 (`decisions/test-run-publish.md`, beside 148, which is not grown; index row; `interfaces/publish.md`'s field list): each `tests[]` entry of a Test run's `report-data.json` gains `decision_rule` (`{kind, w_multiple}`) and `limits` (each `measurement`, `unit`, `lower`, `upper` …
**Merged:** `agent/core/179-a-test-runs-report-data-states-each-limits-decision-rule` (code `b85a419`, ff from `478d61a`; doc `110d673c`, ff).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:45 — api/215 verify-checks-a-test-runs-zip-and-recomputes-its-verdicts
New api decision 146 (`decisions/verify-test-run.md`, index row; `interfaces/verify.md` says per check what a Test zip gets): a zip with `test-run.dsse.json` and `run.json` and no `record.dsse.json` is a Test run's, anything else a Study's, which verifies exactly as before (check 3's "not …
**Merged:** `agent/api/215-verify-checks-a-test-runs-zip-and-recomputes-its-verdicts` (code `48634b0`, ff from `aa15a2f`; doc `96617ba2`, the worker's `3a634493` cherry-picked onto `327d3e31`).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:44 — core/178 an-interrupted-test-run-keeps-its-verdicts-and-resumes-as-a-new-run
New core decision 153 (`decisions/test-run-resume.md`, index row): the executor writes `test-runs/<id>.checkpoint.json` (every `TestResult` so far plus the smoke findings, tmp-and-rename) after each test through a new `Env::checkpoint` hook …
**Merged:** `agent/core/178-an-interrupted-test-run-keeps-its-verdicts-and-resumes-as-a-new-run` (code `478d61a`, ff from `0a19be0`; doc `327d3e31`, ff). Also: `96617ba2`
**Reviewer:** no findings.
**Hardware debts:** a real Core restart under a Test run on the bench: the checkpoint, the interrupted seal, the resume and its go have met only unit tests. The native Windows build of Core. **Deploy debt:** the installed Core.

### 21:15 — api/214 a-test-runs-zip-carries-junit-and-ocp-exports-mapped-from-its-verdicts
New api decision 145 (`decisions/publish-test-export.md`, a new topic file; 144 amended to "five files" and its "Not done" list no longer names the exports, 199 B left; `interfaces/publish.md` …
**Merged:** `agent/api/214-a-test-runs-zip-carries-junit-and-ocp-exports-mapped-from-its-verdicts` (code `aa15a2f`, ff from `fc8059a`; doc `a45655ba`, the worker's `1652eaca` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:13 — core/168 core-keeps-the-host-awake-through-a-test-run
New core decision 152 (`decisions/test-run-awake.md`, a new topic file pointing at 135 to 137; `decisions.md` index row): a `KeepAwake` trait (`hold`, `release`) and a `Hold` drop guard in the new `src/keep_awake.rs` …
**Merged:** `agent/core/168-core-keeps-the-host-awake-through-a-test-run` (code `03579dc`, ff from `c21e9e6`, then my `0a19be0`: three comments cited "decision 151" (`core/172`'s) for 152, which the reviewer noted; doc `12bcbba0`, the worker's `550ac813` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** **the native Windows build of Core is the first test of the `cfg(windows)` half** (never compiled here). On the first Test run on the bench host: the host stays awake through an idle timeout while a run holds the lease, and sleeps normally after it ends; whether the request holds a Windows service's host awake at all is inferred, not measured. **Deploy debt:** the installed Core.

### 20:58 — api/213 a-test-run-publishes-as-one-zip
New api decision 144 (`decisions/publish-test-run.md`, a new topic file; `interfaces/publish.md` gains "A Test run's zip" and its `run_id` row is now true …
**Merged:** `agent/api/213-a-test-run-publishes-as-one-zip` (code `fc8059a`, ff from `1ae13b1`: the worker's `50e7bcc` plus my fix; doc `fdd06e23` and `c28ec796`, the worker's `9542e118` and my `dcd7d4d9` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:56 — core/172 a-test-runs-prompt-pending-event-names-its-kind-without-a-collision
New core decision 151 (`decisions/host-prompt.md`, beside 138; index row in `decisions.md`; `interfaces/host-studies.md` names the key): on the `PromptPending` event only, a Test run's prompt kind is written as `prompt_kind` through a `serialize_with` on the flattened field, so the event carries …
**Merged:** `agent/core/172-a-test-runs-prompt-pending-event-names-its-kind-without-a-collision` (code `c21e9e6`, ff from `ecfdea2`: the worker's `2020a2c` plus my comment fix; doc `b32d48c3`, the worker's `c85cddb2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:31 — api/212 the-identity-tools-name-the-persons-surfaces-on-a-refusal
New api decision 143 (`decisions/identity-acts.md`; a "Who makes an identity act" table in `interfaces/tools-topology.md`, which the instruments, bootload and dev-bench interface docs point to): a new `src/identity_act.rs` holds the ten identity acts …
**Merged:** `agent/api/212-the-identity-tools-name-the-persons-surfaces-on-a-refusal` (code `1ae13b1`, ff from `fe0f8b1`; doc `65720b7d`, the worker's `7281eda0` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:28 — core/177 core-serves-a-test-runs-revision-files
New core decision 150 (`decisions/test-run-publish.md`, with 149's "Not done" line pointing to it; `interfaces/publish.md`, the `interfaces.md` Publish row): `GET /test-runs/{run_id}/publish/{revision}/files/{*name}` (`test_file_handler` in `src/test_publish.rs`), same auth and lease stance as the …
**Merged:** `agent/core/177-core-serves-a-test-runs-revision-files` (code `ecfdea2`, ff from `5cd938b`; doc `4149f1db`, the worker's `37341cd2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:16 — api/211 the-test-ledger-reads-cores-run-log
New api decision 142 (`decisions/test-ledger.md`; `interfaces/tools-test-ledger.md`, the `tools.md` row): `test_show`, `test_pending` and `test_add` (MCP tools; CLI `test-show`, `test-pending`, `test-add`) replace `ledger_*`, removed with no alias (`src/ledger.rs` became `src/test_ledger.rs`) …
**Merged:** `agent/api/211-the-test-ledger-reads-cores-run-log` (code `fe0f8b1`, ff from `d53ab44`, two commits; doc `7613c32b`, the worker's `d7504ba3` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:14 — core/176 discard-refuses-the-agent-on-a-study-a-published-test-run-rests-on
Split this leg, at `28d227f9`: EMB-582 into this task, EMB-581 into `core/177`, EMB-379 into `api/211`, EMB-335 into `api/212` (all `filed`, Fleet Working) …
**Merged:** `agent/core/176-discard-refuses-the-agent-on-a-study-a-published-test-run-rests-on` (code `5cd938b`, ff from `062b48d`; doc `1dd95525`, the worker's `948fff4c` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:50 — ui/126 compact-ui
Size debt paid: `embarch-ui/spec/tabs.md` 9,334 to 9,034 B, out of reserve (threshold 9,039; the task said 9,160, it had grown since). The worker cut the file's provenance paragraph to "Split from ../spec.md." and "no Slack bar since 2026-10-29;" from the Desk row (ui decision 63's tombstone …
**Merged:** `agent/ui/126-compact-ui` (doc only, `3ad3b506`, the worker's `753078d0` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green; `check-doc-size.py --pressure` no longer lists the file.
**Reviewer:** no findings.
**Hardware debts:** none

### 19:48 — chat/051 compact-chat
Size debt paid, both files: `embarch-chat/spec.md` 9,318 to 9,015 B (threshold 9,039) and `open.md` 4,298 to 3,913 B (threshold 3,919), both out of reserve per `check-doc-size.py --pressure` on the merge result …
**Merged:** `agent/chat/051-compact-chat` (doc only, `1232366d`, the worker's `fe7e6fa5` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green.
**Reviewer:** no findings.
**Hardware debts:** none

### 19:47 — core/175 core-publishes-a-test-run
New core decisions 148 and 149 (`decisions/test-run-publish.md`, a new topic file: adding them to `decisions/publish.md` would have put that file at 15 KB against its 12 KB cap, so the worker split rather than grew it …
**Merged:** `agent/core/175-core-publishes-a-test-run` (code `062b48d`, ff from `ea7609c`; doc `2646346b`, the worker's `d36d35d6` cherry-picked).
**Reviewer:** 1 finding — EMB-582
**Hardware debts:** none

### 19:45 — api/210 the-person-acts-from-the-terminal
New api decision 141 (`decisions/person-verb.md`, a new topic file; `interfaces/tools-person.md`, linked from `interfaces/tools.md`): `embarch-api person confirm <hash> | go <run> | answer <run> <prompt> [value] [--cancel] | unit <key> --serial --revision | name <name>` …
**Merged:** `agent/api/210-the-person-acts-from-the-terminal` (code `d53ab44`, ff from `ee8dd30`; doc `b2567178`, the worker's `93f4de85` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:18 — ui/127 the-core-identity-line-reads-the-mode-core-reports
Ui decision 112 amended in place (`decisions/core-identity.md`, its index line too): the identity line's mode is now read from `StatusResponse.mode` (api decision 139), not derived from the attestation's match; `None` reads `mode unknown`, never `service` …
**Merged:** `agent/ui/127-the-core-identity-line-reads-the-mode-core-reports` (code `83d32db`, ff from `62dd46a`; doc `8fd09b95`, the worker's `3e3063a7` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:16 — chat/050 a-container-login-starts-claude-inside-the-agent-container
New chat decision 122 (`decisions/logins.md`): a login may be `embarchChat.logins.<name>.container = { record, manifestPath? }`, where `record` is the agent's `container.toml` (what `embarch agent` writes), re-read at every chat start or resume …
**Merged:** `agent/chat/050-a-container-login-starts-claude-inside-the-agent-container` (code `fc235ad`, ff from `b7e37c8`; doc `262d08f7`, the worker's `a6bd023b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** the first container session on the owner's machine (`Hardware: verify-only`, written in the retired task): a chat starts in the container; its transcript is found under the exchange folder and resumes after an idle close and after a window reload; a handoff stays in the container; no host hook runs; a stopped container shows the `embarch agent up` line (Podman's "not running" text unverified); rewind and the interrupted-step rerun in a container chat.

### 19:14 — api/208 verify-re-evaluates-step-outcomes-and-re-parses-step-numbers
New api decision 140 (`decisions/verify.md`; 120 amended so it no longer says check 2 is always partial; `interfaces/verify.md` row 2): `verify`'s check 2 finds each `events.json` step in the signed `study.json` by `list`, `index` and `inner_index` and recomputes an Exchange step's outcome from its …
**Merged:** `agent/api/208-verify-re-evaluates-step-outcomes-and-re-parses-step-numbers` (code `ee8dd30`, ff from `94be2fa`; doc `87500ca6`, the worker's `92f6c9f2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:12 — core/174 core-keeps-a-manual-verdict-a-units-serial-and-the-persons-name
New core decision 147 (`decisions/manual-verdicts.md`, a new topic file, with `interfaces/manual-verdicts.md`): a manual verdict, a unit's serial and board revision, and the person's name are each a run-log entry, so the chain recomputes over them and a later declaration is a new entry whose GET …
**Merged:** `agent/core/174-core-keeps-a-manual-verdict-a-units-serial-and-the-persons-name` (code `ea7609c`, ff from `018a6e7`; doc `512fd1b7`, the worker's `564586d3` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:47 — ui/123 compact-ui
Size debt paid: `embarch-ui/decisions/live-study.md` 11,539 to 10,999 B, out of reserve (threshold 11,059). Cuts are rationale prose only, in decisions 31, 32, 33, 60 and 64; 109 untouched; no number or heading changed …
**Merged:** `agent/ui/123-compact-ui` (doc only, `dbfc81ad`, the worker's `babbda92` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green; `check-doc-size.py --pressure` no longer lists the file.
**Reviewer:** no findings.
**Hardware debts:** none

### 18:45 — chat/049 the-ghost-text-pause-check-passes-under-load
New chat decision 121 (`decisions/assistant.md`, beside 120, the same page-clock mechanism): the webview stand-in stamps every post with `performance.now()` and records the page's last `input` event, and the check asserts the first ghost post comes at least 300 ms after the last keystroke, in one …
**Merged:** `agent/chat/049-the-ghost-text-pause-check-passes-under-load` (code `b7e37c8`, ff from `f54c3b8`; doc `0c058ca2`, the worker's `3b606437` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:43 — api/207 the-client-status-carries-cores-mode-and-keyid
New api decision 139 (`decisions/client-crate.md`): the shared client's `StatusResponse` gains `mode` and `keyid` (core decision 129), each `Option<String>` with `#[serde(default)]`; `None` means a Core that predates them and reads as unknown, never `service` …
**Merged:** `agent/api/207-the-client-status-carries-cores-mode-and-keyid` (code `94be2fa`, ff from `37e5289`; doc `895aeec3`, the worker's `e5b4863e` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:42 — core/173 a-test-runs-amended-study-record-is-bound-in-the-run-log
New core decision 146 (`decisions/test-run-record.md`), fixing the contradiction the `core/170` reviewer found (EMB-579): the amend stays and the amended hash is bound in the chain …
**Merged:** `agent/core/173-a-test-runs-amended-study-record-is-bound-in-the-run-log` (code `018a6e7`, ff from `b2e195d`; doc `33667240`, the worker's `bcb22408` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:08 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind
New ui decision 113 (`decisions/operator-prompt.md`, now 10,701 B, out of reserve): the prompt's kind is read from `GET /study/{id}`'s `pending_prompt`, not the event (api decision 137, until EMB-577 lands as `core/172`): on each `PromptPending`, `follow` spawns one `get_study_status` read, and …
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `62dd46a`, ff from `59c5e5a`; doc `95fedf4a`, the worker's `6c06a896` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:06 — dev-bench/053 pd-bench-reports-pd-timings-on-its-own-clock
New dev-bench decision 69 (`decisions/pd-bench.md`): a new `pd times` command, chosen over extra `pd status` lines so a test parsing one interval does not have to find it among unrelated lines (the owner may strike it) …
**Merged:** `agent/dev-bench/053-pd-bench-reports-pd-timings-on-its-own-clock` (code `e3a73a0`, ff from `06ef18d`; doc `41aa818c`, the worker's `5e5ab03e` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on each shield: compare `pd times` with a probe on CC (attach, `pd max`, `pd keepalive off` against a PPS source, then `pd times`); record which callback stamps each event and so what each interval includes; record the kernel tick's resolution on the G0B1 and switch to `k_cycle_get_32` if it is coarser than the 100 us a PD timing needs; confirm a Hard Reset the bench sends is never stamped as received, on both roles (`tasks/dev-bench/053`, retired in this fold).

### 18:03 — core/170 a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against
New core decision 145 (`decisions/test-run-record.md`, beside 144): a study is sealed before it is judged, so when a Test run ends Core amends each of its studies' `record.dsse.json` just before the run's own record (144) hashes it: `Sealer::amend_for_test` keeps every other byte of the Statement …
**Merged:** `agent/core/170-a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against` (code `b2e195d`, ff from `81ab021`; doc `44740e1a`, the worker's `444a6b22` cherry-picked).
**Reviewer:** 1 finding — EMB-579
**Hardware debts:** one real Test run on a bench, under the lease: the DUT's and each bench board's image status, the identities and `*IDN?` replies, and an answered observation prompt's scope reach the amended record, and it still verifies. The native Windows build of Core. **Deploy debt:** the installed Core amends no study record until redeployed.

### 18:02 — api/205 declare-instrument-passes-metrology-and-calibration
New api decision 138 (`decisions/instruments.md`): `declare_instrument` takes `metrology` (a list), `calibration` and `clear_calibration`; `declare-instrument` takes `--metrology '<json>'` (repeatable), `--calibration '<json>'`, `--clear-metrology` and `--clear-calibration` …
**Merged:** `agent/api/205-declare-instrument-passes-metrology-and-calibration` (code `37e5289`, ff from `f2156f1`; doc `168f3fca`, the worker's `23285338` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:36 — api/206 the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value
one cross-repo landing by my own hands, announced and parked first (`#embarch-fleet` ts `1795737738.383629`, 30 minutes elapsed with no reply): adding `value` to `PromptAnswerRequest` and two fields to `StudyEvent::PromptPending` broke two struct literals in `embarch-ui`, so I landed `api/206` and then a three-line `embarch-ui` commit of my own (`value: None` in the answer route's literal …
**Merged:** `agent/api/206-the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value` (code `f2156f1`, ff from `8f0ba84`; doc `0831bbc2`, the worker's `c88a9aba` cherry-picked). Consumer commit `embarch-ui` `59c5e5a` (ff from `e5edeac`), mine.
**Reviewer:** no findings.
**Hardware debts:** none

### 17:09 — chat/048 the-cards-checks-pass-under-load
New chat decision 120 (`decisions/assistant.md`): `waitAssist` is now one async script that polls the page's own posts against a deadline on the page's clock, 15 s. No product code changed …
**Merged:** `agent/chat/048-the-cards-checks-pass-under-load` (code `f54c3b8`, ff from `3f9a95f`; doc `e07a8173`, the worker's `4c7aa074` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:07 — ui/125 the-ui-shows-which-core-it-is-talking-to
New ui decision 112 (`decisions/core-identity.md`): one line under the top bar, so on every tab, built from the client's `attestation()` in the snapshot poll (`CoreIdentity::from_attestation`, `Snapshot.core_identity`): `Core: service|development, <16 hex>, matches the installed fingerprint|does …
**Merged:** `agent/ui/125-the-ui-shows-which-core-it-is-talking-to` (code `e5edeac`, ff from `1e49270`; doc `b3c27a83`, the worker's `b107d287` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:05 — core/169 a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test
New core decision 144 (`decisions/test-run-record.md`): a Test run is sealed as it ends — finish, cancel or deadline — before `end_run` releases the run lock, as `test-runs/<run_id>.test-run.dsse.json` (the worker added the `<run_id>.` prefix to the task's name), predicate …
**Merged:** `agent/core/169-a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test` (code `81ab021`, ff from `90a6cc9`; doc `d33cc7f6`, the worker's `49924869` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** one real Test run on a bench, under the lease, leaves `test-runs/<id>.test-run.dsse.json` and a `test_run` run-log entry, and a cancelled one names every selected test with a verdict or reason. The native Windows build of Core (nothing new is `cfg(windows)`). **Deploy debt:** the installed Core signs no Test run record until redeployed.

### 14:23 — dev-bench/051 pd-bench-has-an-idle-command-and-a-hello-line
New dev-bench decision 68 (`decisions/pd-bench.md`): `pd idle` puts keep-alive on, DR/PR/Request replies back to accept and the `pd max` choice, restores the devicetree's Source_Capabilities on the DRP1M1, drops any contract and ends `pd: ok`, or `pd: error <what>` when VBUS did not discharge or a …
**Merged:** `agent/dev-bench/051-pd-bench-has-an-idle-command-and-a-hello-line` (code `06ef18d`, ff from `5cff766`; doc `68444e79`, the worker's `3d104147` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on both shields: set `keepalive off`, `dr reject`, `pr reject`, `answer wait`, `srccaps` and `pps`, run `pd idle`, and read `pd status` and `pd srccaps` back at their defaults; a sink holding a PPS contract — `pd idle` sends the Hard Reset and renegotiates at the default choice; the DRP1M1 sourcing to a sink — VBUS under 0.6 V within tSafe0V and the port attaches again from scratch; `pd hello` prints the right version, commit (with `-dirty` when it was) and shield on each build (`tasks/dev-bench/051`, retired in this fold).

### 14:20 — chat/046 the-linker-offers-a-studys-capture-or-trace
New chat decision 119, in a new topic file `decisions/references-studies.md` (so `references-kinds.md` stays out of reserve): the 💡 linker reads `embarch-api --json list-studies --limit 20` through `chat/043`'s runner and offers one entry per tap, `trace` when its `encoding_kind` is …
**Merged:** `agent/chat/046-the-linker-offers-a-studys-capture-or-trace` (code `3f9a95f`, ff from `3587735`; doc `fe801c24`, the worker's `40a529d0` cherry-picked, no conflict).
**Reviewer:** no findings.
**Hardware debts:** none

### 14:18 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind
New ui decision 111 (`decisions/confirm-tab.md`): the go card lives in the Confirm tab (the worker's call, its reason in 111). New routes `GET /api/test-runs/{run_id}/card` and `POST /api/test-runs/{run_id}/go` …
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `1e49270`, ff from `4a2e694`; doc `4d6ec789`, the worker's `31f54bc3` cherry-picked).
**Blocked:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind`'s prompt-modal half — waits on EMB-575 (client prompt fields); task `blocked` with `Unparks when:` EMB-575 landing. EMB-384 stays in Fleet Working.
**Reviewer:** no findings.
**Hardware debts:** none

### 14:15 — core/167 a-bench-is-smoke-checked-before-its-first-test
New core decision 143 (`decisions/smoke-check.md`): before a bench's first test, the first bench included, `drive` calls `Env::smoke_check`, which checks the bench's declared signals, roles and instruments, `validate` for the DUT and each bench board, each board's hello line (an echo alone is not …
**Merged:** `agent/core/167-a-bench-is-smoke-checked-before-its-first-test` (code `90a6cc9`, ff from `ca34d61`; doc `06b5099e`, the worker's `a93b889d` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** the smoke check once on a real bench, in a two-bench fixture run under the lease: a DUT, one bench board with a hello line, one instrument with a declared calibration (`tasks/core/167`, retired in this fold, lists what to confirm). `SMOKE_WAIT_MS` (2 s) and `SMOKE_PORT_WAIT_MS` (5 s) are chosen, not measured. The native Windows build of Core. **Deploy debt:** the installed Core runs no smoke check until redeployed.

### 13:55 — chat/047 the-long-chat-scroll-check-settles-before-it-reads
New chat decision 118 in `decisions/timeline.md`. The worker's evidence: a one-check copy failed 16 of 25 runs under 24 busy loops before the fix, 0 of 25 after; the full check passed 20 of 20 under a lighter `cargo test` load …
**Merged:** `agent/chat/047-the-long-chat-scroll-check-settles-before-it-reads` (code `3587735`, ff from `701a019`; doc `adc0f48d`, the worker's `7dd99028` cherry-picked, rebased over the owner's `6f6fcbd8`).
**Reviewer:** no findings.
**Hardware debts:** none

### 13:54 — study-designer/100 check-test-refuses-a-study-that-does-not-match-its-hash
The study-hash chain that `study-designer/099` started on 2026-11-25 is complete: `hil_check::check_test` now refuses a host study that does not hash to its test's `study.hash` by `hil_test::study_hash`, as `Rule::StudyHashMismatch` on `study.hash`, naming the study file and both hashes …
**Merged:** `agent/study-designer/100-check-test-refuses-a-study-that-does-not-match-its-hash` (code `8bd6bcc`, ff from `ebbaaca`; doc `e067e275`, the worker's `fcaeea23` cherry-picked, rebased over the owner's `6f6fcbd8`).
**Reviewer:** no findings.
**Hardware debts:** none

### 11:56 — api/204 test-propose-fills-a-studys-hash-with-study-hash
reversals row 118 added (`reversals/rows-115-115.md`): a Test's `study.hash` had three conventions across three repos (the file's bytes in `embarch-api`, whatever the fixture said in Core, `study_hash` in the crate), found when the crate's refusal turned two consumers red on 2026-11-25; all three now call `study_hash` …
**Merged:** `agent/api/204-test-propose-fills-a-studys-hash-with-study-hash` (code `8f0ba84`, ff from `fc1a33b`; doc `859faca3`, the worker's `85b9699b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 11:54 — core/166 the-test-run-prepare-checks-each-study-against-its-hash
`POST /test-runs`'s prepare now hashes every premade study it was sent with the crate's `hil_test::study_hash` and compares it with its test's `study.hash`; a mismatch is refused `422` naming the test, the file and both hashes, and nothing is registered …
**Merged:** `agent/core/166-the-test-run-prepare-checks-each-study-against-its-hash` (code `ca34d61`, ff from `5964670`; doc `be9e5e76`, the worker's `1a756f99` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none
*Days 2026-11-25 to 2026-11-25 rolled to [log-archive/supervisor-log-2026-11-25-to-2026-11-25.md](log-archive/supervisor-log-2026-11-25-to-2026-11-25.md).*
