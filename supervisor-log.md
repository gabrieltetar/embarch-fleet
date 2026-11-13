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

## 2026-11-13 13:57 — dev-bench/047 the carried R3.2 patch's usbc_pd.h includes zephyr/toolchain.h

**Decided:** nothing numbered. **A toolchain unit, run by this leg with its own hands** (protocol §7), not dispatched. EMB-147: `usbc-pd-r32.patch` gained one hunk adding `#include <zephyr/toolchain.h>` after `<zephyr/types.h>` in `usbc_pd.h`; I edited the patch by hand rather than regenerating it, so the 13 later `usbc_pd.h` hunks' new-file starts moved by one, the post-image blob id became `273904975c1` (checked with `git hash-object` on the applied file), the diffstat moved by one, and part 16 of the patch message gained a bullet saying why. `patches.yml` carries the new `sha256sum`. `pd_logic.h` dropped its workaround include and comment. The other copy of the patch, outside the suite, is untouched (the owner's open question in `embarch-dev-bench/open.md`).
**Merged:** `agent/dev-bench/047-usbc-pd-header-compiles-on-its-own` (code `0aaf5d6`, ff on `50579d3`, pushed to `embarch-dev-bench` main from the unit worktree; doc `dc24b67c`, task file and changelog fragment, committed in the leg worktree). Gate, in a fresh west workspace inside the unit worktree (`west init -l manifest`, `west update --path-cache` from the main checkout's `native_sim` workspace, Zephyr v4.4.2): **red first** — the old patch with the workaround removed failed `tests/logic` on `native_sim` with the four `conflicting types for '__packed'` errors; then `west patch apply` 6 applied, `west twister -T pd-bench/tests/logic -p native_sim` 13 of 13 passed, `west twister -T pd-bench -p nucleo_g0b1re` both shields built with 0 warnings. `git apply -v` offsets identical before and after the edit, none in `usbc_pd.h`. Ownership `dev-bench` OK on both halves, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; both shield builds are build-only, as decision 59 has it.
**Budget:** PROCEED, wave 6; 5-hour 52% at the unit's start to 74% now (resets about 16:20), weekly 41% to 43%.
**Least sure about:** the unit worktree holds a 2.7 GB west workspace that goes when the worktree is removed, so the next pd-bench toolchain unit pays the clone again; `--path-cache` from the `native_sim` workspace made it a few minutes, which is the trick worth reusing.

---

## 2026-11-13 13:51 — core/126 core's open.md split by mission

**Decided:** nothing. A verbatim split, the worker's: the seven `## Never exercised` bullets (`POST /bootload`, the signal tap, decisions 35, 106, 89, 92, 93) moved to a new `embarch-core/open/never-exercised.md`, each Owner-run: and To verify: step with its bullet; `open.md` keeps one pointer bullet and decision 108's deploy bullet whole. `open.md` 4,314 to about 2,670 B, out of reserve. I diffed removed against added lines (nothing removed that was not re-added) and `collect-open-questions.py` still prints the new file.
**Merged:** `agent/core/126-compact-core` (doc only: `cd20175e`, cherry-picked onto `1d2af482`). Gate on the merge result: ownership `core` OK, `check-docs.py` 12/12. No code repo touched, so no cargo gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.
**Budget:** PROCEED, wave 6; 5-hour 40%, weekly 41%.
**Least sure about:** nothing specific to this unit; with both compactions landed the only size debt left is the owner's `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17).

---

## 2026-11-13 13:50 — api/150 split api's open.md by mission

**Decided:** nothing. A verbatim split, the worker's: seven verification-debt bullets (bootload, `bench_exchange`, `study_watch`, ledger, lease, build verdict, `build --each`) moved to a new `embarch-api/open/bench-verification.md`, links given a `../` prefix and nothing else; `open.md` keeps one pointer bullet, the `stack` and `patches` bullets (real-repo debts, not bench or toolchain ones) and the Settled-deferred section untouched. `open.md` 4,502 to 3,076 B, out of reserve. I diffed removed against added lines and `collect-open-questions.py` still prints all seven.
**Merged:** `agent/api/150-compact-api` (doc only: `e1c6b57f`, ff on the claim `afd23f2b`). Gate on the merge result: ownership `api` OK, `check-docs.py` 12/12. No code repo touched, so no cargo gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.
**Budget:** PROCEED, wave 6; 5-hour 40%, weekly 41%.
**Least sure about:** the worker's answer to the compaction question says `spec.md` alone cannot say what is unproven on hardware, which is true by design; I did not read `spec.md` myself to judge the rest of that answer.
**Leg notes (this leg, first unit):** normal mode, pump latched 13:18:59 by the owner, no stop marker, nothing actionable in the channel. Leg began at `90ffd7fa` (fleet `ed64e0f`); step 0 found nothing to recover (no leg worktree, no claims, no unit worktrees). Fleet Ready empty; `finish` moved nothing (EMB-147 still has `dev-bench/047` open). Size ledger: nothing overdue. Bench: Core reachable, neither role attached at 13:47, so `api/059` and `dev-bench/038` stay `open`. Refill owed on depth and spread: the only source change since the 13:38 sweep was `embarch-atlas/design.md`'s EMB-109 section, a recorded trade-off, so nothing filed. Spread sweep: nothing filed (2026-11-13 13:50). Dispatched 13:48: `api/150`, `core/126`, both doc-only worktrees with no code worktree; both reported inside a minute.

---

## 2026-11-13 13:45 — api/153 test scratch directories named from a counter, not the clock

**Decided:** nothing numbered. EMB-169, the worker's: a `support::unique_dir(tag)` helper beside 152's `api_command` in `tests/support/mod.rs` names a scratch directory from the pid plus a process-wide `AtomicUsize`. All ten clock-named files call it: the five the issue named and the five the task's grep added (`dev_bench_hello_success`, `json_surface`, `run_study_unreported_bench`, `smoke_harness`, `study_follow_cli`); every one named a directory, so none was left. `src/main.rs`'s unit-test tempdir, which cannot reach `tests/support`, got an inline counter. Left alone: dirs named from the pid plus a fixed tag (`patches_cli`, `stack_cli`, `core_client_http`, `src/ledger.rs`), which collide only if one tag repeats in a process. `lease_client.rs` keeps 151's own counter rather than the shared helper. Load: 50 runs per changed file (5 parallel batches of 10, 14 CPU burners on 14 cores, `EMBARCH_REQUIRE_LEASE=1` exported), 500 runs, 0 failures.
**Merged:** `agent/api/153-test-scratch-dirs-named-from-the-clock` (code `d97985f`, ff on `af2ea2b`; doc `82c27cda`, cherry-picked onto `94d7a010`). Gate on the merge result with `EMBARCH_REQUIRE_LEASE=1` set: `cargo build`, `cargo test --no-fail-fast` (401 passed, 0 failed), `cargo clippy --all-targets -- -D warnings` green; ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 8% at the leg's start to 40% now (resets about 16:10), weekly 38% to 41%.
**Least sure about:** the `src/main.rs` counter had no load run of its own, only the normal `cargo test`.
**Leg close (next leg, read this first):** **4 of 4 units**, all reviewers clean: `api/152` and `atlas/063` recovered from the 2026-11-12 20:04 leg (stopped at ~20:10, then died mid-fold with no entry), `atlas/064` and `api/153` dispatched here. Leg began at `ff933079` (fleet `cb2b4df`). **What you would not expect:** (1) that dead leg had already pushed `atlas/063`'s code to `embarch-atlas` main; only its doc half and fold were missing, and I reset its dirty leg worktree rather than finishing its fold in place; (2) one atlas test flaked once at 063's gate and I lost its name (see that entry); (3) the first fold day-folded 2026-11-12 and rolled 2026-11-10 into `log-archive/`. **New decisions:** none numbered; `embarch-atlas` `design.md` gained 064's freeze section. **Closed:** EMB-158, EMB-113, EMB-109, and EMB-169 at this fold's `finish`. **Queue for the next leg:** worker tasks `api/150` (compact api `open.md`, due 2026-11-24) and `core/126` (compact core `open.md`, due 2026-11-25), two scopes, so refill stays owed on spread; my spread sweep at 13:38 filed nothing, so a later leg skips it unless a source changes. Toolchain by a leg's own hands: `dev-bench/047` (EMB-147; pd-bench west workspace uninitialised, first `west update` several GB). Bench: `api/059`, `dev-bench/038`, neither role attached at 13:20. Owner-only: `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17, four days). **Deploy debts owed by the owner**, unchanged: the desk (decision 85 plus a plugin version bump), the UI service (decision 102), and Core per `embarch-dev-workflow.md` §4a. No `suite` task, nothing deployed, no alert sent.

---

## 2026-11-13 13:40 — atlas/064 freeze leaves a cite of another document out of the citing document's pages

**Decided:** nothing numbered (`embarch-atlas` keeps no `decisions.md`). EMB-109's design choice, the worker's, recorded in the code repo's `DESIGN.md` and a new `embarch-atlas/design.md` section: a page cite that names another document contributes its page to **no** frozen set, rather than to that document's. Filing it under the other document would need a second set of page hashes and a second `thaw-check` rule, since `thaw-check` reads only its own document's `pages/`. A unit citing only other documents rests on every page, as an uncited unit does. The cost, accepted: a change to the other document's page no longer thaws the unit. Code: the sibling-document lookup moved out of check M's nested `sibling()` into a module-level `check.find_sibling`, which `freeze.own_cited_pages()` now shares, so cites are not parsed a second way; `out_of_range` runs on own-document pages only.
**Merged:** `agent/atlas/064-freeze-files-a-cross-document-cite-under-its-own-document` (code `d0c2f12`, ff on `3f3d77c`; doc `57d06376`, cherry-picked onto `893d0440`). Gate on the merge result in the unit's worktree with its own venv: `pytest -q` 826 passed, 3 skipped, `test_public_guard` ran; ownership `atlas` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 8%, weekly 38%.
**Least sure about:** whether "none" is the choice the issue's author wanted; the task left it open and the worker's reason holds, but a unit resting on a changed page of another document now stays frozen with nothing saying so.

---

## 2026-11-13 13:39 — atlas/063 check K holds a record to the group its cond names

**Decided:** nothing numbered (`embarch-atlas` keeps no `decisions.md`; the change is in the code repo's `DESIGN.md`). EMB-113, the worker's: check K now picks a record's table group by the condition its `cond` names, so a record matching a side-by-side group headed by a different condition fails; a `cond` that names no group is reported (`K_cond: unmatched`, per record and per document) rather than passing.
**Merged:** `agent/atlas/063-check-k-holds-a-record-to-its-conditions-group` (code `3f3d77c`, ff on `78fe5b4`, **landed by the 2026-11-12 20:04 leg before it died**; doc `d31ba2ec`, cherry-picked onto `4eedc6ad`, changelog fragment and task file only). Gate on the merge result (atlas `main` = `3f3d77c`), in the unit's worktree with its own venv: `pytest -q` **824 passed, 1 failed, 3 skipped; the failing test passed alone on `--lf`**, and I lost its name to that rerun. The full suite on `atlas/064`'s branch, which is `3f3d77c` plus 064, then ran 826 passed, 0 failed, so I read it as a flake, not this unit's red. `test_public_guard` ran, not skipped. Ownership `atlas` OK on both branches, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 8%, weekly 38%.
**Least sure about:** the one flaky atlas test I could not name: if it recurs at another leg's gate, run `pytest -q -rf` the first time so the name survives.
**Spread sweep:** sources changed since the `2026-11-09 17:34` marker, so I swept the diff since then rather than all of `open.md` (chat, core, dev-bench, api, study-designer, desk, atlas `design.md`, reversals). Every new item is owner-run (deploys, a phone check, a pick awaiting him), toolchain-gated (real twister or sysbuild output) or explicitly undriven (study-designer's `no_std` CI cell). Spread sweep: nothing filed (2026-11-13 13:38).

---

## 2026-11-13 13:26 — api/152 CLI tests fail when cargo test runs from outside the repo

**Decided:** nothing numbered. EMB-158's cause (the worker's; the reviewer and I read the diff): `EMBARCH_REQUIRE_LEASE=1`, which a listener under the suite exports, reached the spawned `embarch-api` binary in five subprocess tests. Inside the repo `.cargo/config.toml` forces it empty (decision 101); from the suite root that file is not read. Fix, test code only: a `support::api_command` helper calls `env_remove("EMBARCH_REQUIRE_LEASE")` on the spawned binary, and `bench_exchange_cli`, `dev_bench_hello_success`, `run_study_unreported_bench`, `serial_log_truncation` and `signal_exchange_cli` use it. Not the same bug as EMB-169 (`tasks/api/153`, clock-named scratch dirs): different cause, three files in common.
**Merged:** `agent/api/152-cli-tests-fail-from-outside-the-repo` (code `af2ea2b`, ff on `e4957c5`; doc `8cbd3642`, cherry-picked onto `5914a007`). **Recovered, not dispatched by this leg:** the worker was the 2026-11-12 20:04 leg's, finished and pushed both branches at 20:15, and that leg died before landing it. Gate on the merge result, run with `EMBARCH_REQUIRE_LEASE=1` in my own environment (the failing condition): `cargo build`, `cargo test --no-fail-fast` (401 passed, 0 failed), `cargo clippy --all-targets -- -D warnings` green; ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 8%, weekly 38%.
**Least sure about:** I did not re-run the suite from the suite root myself; my run proves the variable no longer reaches the binary from inside the repo with it exported, which is the mechanism, not the exact repro the task names.
**Leg notes (this leg, first unit):** normal mode, pump latched 13:18:59 by the owner, no stop marker, nothing actionable in the channel. **Recovery:** the leg that started 2026-11-12 20:04 claimed `api/152`, `atlas/063`, `core/126` (split EMB-169 into `api/153` at `5acbaa19`), took a fleet stop at ~20:10 and released `core/126` (`ff933079`), landed `atlas/063`'s code (`3f3d77c` on `embarch-atlas` main) and died mid-fold with no log entry, its leg worktree holding the rebased 063 doc commit unpushed plus the changelog assembler's output. I reset that worktree to `origin/main` (both were re-derivable: the pushed doc branch carries the same patch) and land 063 as an ordinary unit. Leg began at `ff933079` (fleet `cb2b4df`). Fleet Ready empty; `finish` moved nothing. Size ledger: nothing overdue (doc/098 due 11-17, owner-only). Bench: Core reachable, neither role attached, `api/059` and `dev-bench/038` stay `open`. Day fold: 2026-11-12 folded by an `embarch-log-folder` agent, 2026-11-10 rolled to `log-archive/`. Client-name history scan: all 16 repos clean. Dispatched 13:22: `atlas/064` (already reported).

---

## 2026-11-12 — 4 units

*Folded 2026-11-13 by the embarch-log-folder agent for the leg that recovered this day: per-unit narrative reasoning, gate detail and budget lines went; git holds them. SHAs, reviewer lines and debts are kept below.*

**Carry forward (next leg, read this first):**
- The leg that started 2026-11-12 20:04 was stopped or killed with no log entry; the 2026-11-13 leg recovers its two finished units.
- **Leg close, 20:03 (4 of 4 units, all workers, all reviewers clean):** began at `1411a9a9` (fleet `42db4cd`), normal mode. Surprises: (1) the first fold also day-folded 2026-11-10 (52 units) and 2026-11-11 (7) and rolled 2026-11-07..09 into `log-archive/`; (2) two workers left `State:` as the claim line with every box ticked, and `fold-commit.py` refused until set to `done`, so read the state line before folding. New decisions: `embarch-desk` 85, `embarch-ui` 102. Closed: EMB-141, EMB-140, EMB-155 (at the fold's `finish`); EMB-73 moved to Done at the leg's start. Filed: EMB-169 (by the api worker, Fleet Ready, not yet split: split at `ready`; five test files use clock-named scratch dirs; may be one bug with EMB-158 / `tasks/api/152`, since three of its five files are among the twenty EMB-158 measured failing from the suite root, so give both to one worker or read 152's cause first). No `suite` task, nothing deployed, no alert sent.
- **Queue for the next leg:** worker tasks `atlas/063` (EMB-113), `atlas/064` (EMB-109), `api/152` (EMB-158; see above), `api/150` (compact api `open.md`, due 2026-11-24), `core/126` (compact core `open.md`, due 2026-11-25). Toolchain by a leg's own hands: `dev-bench/047` (EMB-147; pd-bench west workspace uninitialised, first `west update` is several GB). Bench: `api/059`, `dev-bench/038`, no probe attached at 19:30. Owner-only: `doc/098`.
- **Deploy debts owed by the owner:** the desk (decision 85, plus a plugin version bump) and the UI service (decision 102); details in the per-unit debt lines below.
- Open risk: chat/026 moved decisions 101, 103, 105, 106 of `embarch-chat/decisions/sessions.md` to `decisions/logins.md`; an owner branch editing them would conflict.
- Decisions made on the owner's behalf: ui/109 (decision 102) with `EMBARCH_UI_CONFIG` unset reads `embarch-ui/config.toml` under XDG/`~/.config` (`%APPDATA%` on Windows) if present, else zero-config default. desk/028 (decision 85): unknown line-body fields are a 400 on both line routes; new `DELETE /sessions/{sid}/line/{nid}` and MCP `desk_remove_line` (own, open-tile lines only), so a client behind in version now fails loudly.

### api/151 two lease_client tests fail once under load, then pass
Cause: scratch dir named from pid and clock nanoseconds collided between test threads; fixed with a static `AtomicUsize` counter (test-only). 0 failures in 700 runs after, 5 in 810 before.
**Merged:** `agent/api/151-lease-client-tests-flake-under-load` (code `e4957c5`, ff on `ceae118`; doc `f022b24e`, ff on `5bb3d108`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### ui/109 service install keeps the UI's config when the shell does not set EMBARCH_UI_CONFIG
**Merged:** `agent/ui/109-service-install-keeps-the-ui-config` (code `b81ed12`, ff on `2e16164`; doc `7a2fb44e`, ff on `8284e316`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needs a board. One deploy debt for the owner: `cargo build` in the main `embarch-ui` checkout, then restart or reinstall the user service, with the config at `~/.config/embarch-ui/config.toml` (or `EMBARCH_UI_CONFIG` exported for the install), and confirm the tabs load. The Windows `%APPDATA%` branch is written and not run.

### desk/028 a line body the desk cannot honour is refused, and a session takes back its own line
**Merged:** `agent/desk/028-a-line-body-with-an-unknown-field-is-refused` (code `bf93853`, ff on `1997108`; doc `1cea2713`, ff on `1cd0bb45`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needs a board. One deploy debt for the owner: the installed desk still drops unknown fields and has no `desk_remove_line` until it is redeployed (and the plugin's version bumped, so sessions load the new tool). Then check that `POST /sessions/<sid>/line` with `{"text":"x","bogus":1}` answers 400 naming `bogus`, and that `desk_add_line` then `desk_remove_line` removes the line from the tile.

### chat/026 login and handoff decisions leave sessions.md by verbatim split
`sessions.md` 12,745 to 6,673 B; `spec.md` untouched. Fold extras: `suite/features.md` gained the EMB-161 login-pick row; 2026-11-10 and 2026-11-11 were folded and 2026-11-07..09 rolled to `log-archive/supervisor-log-2026-11-07-to-2026-11-09.md`. Dispatched 19:35; seven issues split in `7866a9ab` (EMB-155, 158, 113, 109, 141, 140, 147); announced at `ts` `1794537223.969339`.
**Merged:** `agent/chat/026-compact-chat` (doc only: `d76e0412`, ff on the claim `45b9cb6e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

## 2026-11-11 — 7 units

*Folded by the embarch-log-folder agent on 2026-11-12 (leg's first unit after midnight): per-unit narrative, gate re-run detail and worker-choice lists dropped; git and the retired task files hold them. All SHAs, reviewer lines and debts kept.*

**Not a leg.** All seven units were owner-dispatched: worker threads the owner's session started on 2026-11-10/11, landed by an owner-dispatched landing agent on his instruction, no supervisor or listener running, no leg number, budget not read. Order landed: suite/037, then six `atlas` units each branched from the one before (003, 001, 016, 004, 011, 002).

**Carry forward**
- **Deploy owed (suite/037):** Core must be installed per `embarch-dev-workflow.md` §4a, then the API rebuilt, by the owner's session. Until then `run_study` refuses every study that pins a bench version, the Study Designer shows the bench build as unavailable, and umbrella check 13 warns. The `embarch-core/open.md` bullet stays until the deploy closes it. Owner decided: when Core sends no `dev_bench_version`, a pinned-version study is always refused and `allow_version_mismatch` does not override it; only a bench requirement of `any` runs. Decisions landed: embarch-core 108, embarch-api 105, study-designer 74's open question closed. `tasks/core/126-compact-core.md` filed (open, due 2026-11-25).
- **Owner decisions made on his behalf's record:** (a) 2026-11-10, a worker may land the 2026-10-08 `standard` design in `embarch-atlas-wt` as written (atlas/016; doc `e3b2218f`). (b) 2026-11-10, `atlas-translate-docs`, `atlas-build`, `atlas-update` lose `disable-model-invocation: true`, so a session may start a bump on its own judgement (atlas/001; code `9c912da`, doc `3f2b9b20`; `changelog.d/atlas-skills-model-invoked.decided.md`). (c) 2026-11-11, atlas/002's replay miss accepted (70 Zephyr calls became 72 against a target of 35 or fewer); tools land as built, task closed `done` with the replay box unticked (doc commits `2077eba5`, `e068b439`).
- **Open follow-ups:** EMB-160 (atlas/011: check L has no column-position check; an x-position test like check K's would close it). EMB-159 (atlas/004: USB PD PDO/APDO decode written from memory, unverified against the standard; check once the standard is distilled). EMB-148 (replay harness). atlas/003's question to the owner (cache extraction after each engineer build, or let `dt_node vs=` fall back to text) is unanswered, recorded in the retired task file.
- **Slip to avoid:** the lander pushed code before reading the doc gate (atlas/004). 016's 12/12 was read before `fold-commit.py` deleted the task file, which reddened `check-task-state.py` on `tasks/atlas/011`; 011's landing cleared it. Read the gate after the fold, not before.
- **Least sure:** 41 of the field workspace's 44 build dirs predate its Zephyr, so `config` answers value and fragment only and `dt_node vs=` cannot answer until an extraction is cached; model-invocable atlas skills may start unrequested bumps, unmeasured; no real standard has been filed by `inventory`; absent-field paths in ui/umbrella were gated by tests only, never against the installed pre-108 Core; whether whole-file review rounds show the gain atlas/002's replay did not.

### suite/037 GET /dev-bench/hello serves dev_bench_version (22:33)
**Merged:** `agent/suite/037-rename-dev-bench-hellos-firmware-version-to-dev-bench-version-or-close-it`, each a fast-forward: core `c0d2a7e` (on `b6035a7`), api `ceae118` (on `d36be9e`), ui `2e16164` (on `08f9a53`), umbrella `47feb0f` (on `6ddb653`), doc `a68957f4` (on `25efa3f4`). Gate green: cargo build/test/clippy in core and api, ui and umbrella against api `ceae118`, native Windows release build of core at `c0d2a7e` (exit 0, 3 m 07 s) with siblings `embarch-study-designer` `f6cca94`, `embarch-topology` `b905523`, `embarch-smp` `4b23bc2` still `origin/main`. `check-ownership.py` not run (refuses `suite` by design). Changelog assembler rolled `history/core.md` 2026-09 into the archive at its size cap.
**Blocked:** nothing.
**Reviewer:** skipped (a 429 in the last window; owner-dispatched landing outside a leg).
**Hardware debts:** one, a deploy rather than a board, and the owner's session runs it after this landing: Core installed per `embarch-dev-workflow.md` §4a, then the API rebuilt. Until then the installed Core serves `firmware_version`, so `run_study` refuses every study that pins a bench version, the Study Designer shows the bench's build as unavailable, and umbrella check 13 warns. The `embarch-core/open.md` bullet stays until that deploy closes it.

### atlas/003 config takes a list of names and a second build to compare (22:40)
**Merged:** `agent/atlas/003-config-takes-a-list-and-a-second-build` (code `718c4fe`, ff on `f293d94`; doc `c8b1e210`, ff on `adbabe34`, suite/037's fold). `pytest -q` 738 passed, 3 skipped; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none needs a board. One toolchain debt: `dt_node vs=` has never run on a real pair of builds whose devicetrees differ, and the MCP tools ran in process, not through a Claude Code session.

### atlas/001 bump the atlas when HEAD moves, without a session ritual (22:41)
**Merged:** `agent/atlas/001-bump-on-head` (code `9c912da`, ff on `718c4fe`; doc `9875b0b0`, ff on `6d874115`, 003's fold). `pytest -q` 746 passed, 3 skipped; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none needs a board. One toolchain debt: no bump has run from a hook on a real west workspace, and a rebase of many commits is covered only by construction (the in-progress check reads `git rev-parse --git-path rebase-merge` and friends).

### atlas/016 the standard document kind, and a standard's sections picked from use (22:42)
**Merged:** `agent/atlas/016-standard-sections` (code `31e1857`, ff on `9c912da`; doc `cabe583a`, ff on `3007e601`, 001's fold). Design landed as code `e3a12bf`, doc `e3b2218f`. `pytest -q` 762 passed, 3 skipped; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none.

### atlas/004 check firmware configuration against a standard's requirements (22:43)
**Merged:** `agent/atlas/004-config-vs-standard` (code `198a51f`, ff on `31e1857`; doc `e36b4143`, ff on `63bdab21`, 016's fold). `pytest -q` 775 passed, 3 skipped; `check-docs.py` 11/12, the red being `check-task-state.py` on `tasks/atlas/011` (see Carry forward), not this unit's.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none.

### atlas/011 applicability, state and transition records of a standard (22:44)
**Merged:** `agent/atlas/011-protocol-records` (code `ece94d6`, ff on `198a51f`; doc `0a2af463`, ff on `dab47b1e`, 004's fold). `pytest -q` 806 passed, 3 skipped; `check-docs.py` 12/12, the `check-task-state.py` red cleared by this merge.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none.

### atlas/002 look up a symbol or a state machine in the sources a build compiled (22:45)
**Merged:** `agent/atlas/002-code-lookup-over-the-build` (code `78fe5b4`, ff on `ece94d6`; doc `acd6742c`, ff on `3b19523f`, 011's fold). `pytest -q` 823 passed, 3 skipped; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none needs a board. One toolchain debt: the libclang and ctags paths never ran (neither is on this machine nor in the Zephyr SDK), and the `.ninja_deps` reader has met format 3 only by reading.

---
*Days 2026-11-10 to 2026-11-10 rolled to [log-archive/supervisor-log-2026-11-10-to-2026-11-10.md](log-archive/supervisor-log-2026-11-10-to-2026-11-10.md).*
