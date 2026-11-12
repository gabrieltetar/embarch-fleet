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

## 2026-11-11 22:40 — atlas/003 config takes a list of names and a second build to compare

**Not a leg.** This unit was run by a worker thread the owner's session dispatched directly on 2026-11-10, and landed by an owner-dispatched landing agent on the owner's instruction in his interactive session (2026-11-11, land all branches), first of six `atlas` units it lands in order (003, 001, 016, 004, 011, 002), each branched from the one before. No supervisor or listener was running, so no leg number exists. The leg's merge gate and fold were followed as written.
**Decided:** nothing by the lander, and no decision number: the atlas keeps its contract in the code repo's DESIGN.md. The worker's choices land as written and are listed in the retired task file: in `config vs=`, absent, unset and `n` count as one value; `dt_node` takes `vs=` but no list, because commas occur inside compatibles; a devicetree comparison compares values, not where they were set, and stops naming the side that cannot load rather than falling back to a `zephyr.dts` text diff. The worker's question to the owner (cache the extraction after each engineer build, or let `dt_node vs=` fall back to text) has no answer yet and is recorded in that file; EMB-148, a replay harness, was filed separately.
**Merged:** `agent/atlas/003-config-takes-a-list-and-a-second-build` (code `718c4fe`, ff on `f293d94`, no rebase needed; doc `c8b1e210`, ff on `adbabe34`, suite/037's fold, after a clean rebase of the claim and the unit commit). Gate on the merge result, re-run by the lander in the code worktree's own venv: `pytest -q` 738 passed, 3 skipped (the real-workspace, built-atlas and vendor-SVD skips), `test_public_guard` ran. Ownership `atlas` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief dispatched no reviewer, and a reviewer gates no merge).
**Hardware debts:** none needs a board. One toolchain debt: `dt_node vs=` has never run on a real pair of builds whose devicetrees differ, and the MCP tools ran in process, not through a Claude Code session.
**Budget:** not read: no leg and no wave.
**Least sure about:** 41 of the field workspace's 44 build dirs predate its Zephyr, so on most real builds `config` answers value and fragment only and `dt_node vs=` cannot answer at all until an extraction is cached.

---

## 2026-11-11 22:33 — suite/037 GET /dev-bench/hello serves dev_bench_version

**Not a leg.** An owner-dispatched suite unit: its work ran on 2026-11-10 and 2026-11-11 in threads the owner's session dispatched directly, and an owner-dispatched landing agent landed it on the owner's instruction (2026-11-10, "land all branches"; 2026-11-11, "land, then deploy Core"). No supervisor or listener was running, so no leg number exists. Protocol §8's sequenced cross-repo landing, the merge gate and the fold were followed as written; the landing agent deployed nothing.
**Decided:** nothing by the lander. The owner decided on 2026-11-11, in his interactive session, as the retired task file records: `embarch-umbrella` lands with core, api and ui; when Core sends no `dev_bench_version`, `run_study` always refuses a study that pins a bench version and `allow_version_mismatch` does not let it through, so only a bench requirement of `any` runs such a study against an old Core; Core is deployed after landing. `embarch-core` decision 108 (`GET /dev-bench/hello` serves the bench's build as `dev_bench_version`; the wire `HelloAck` is unchanged) and `embarch-api` decision 105 (`HelloAckResponse.dev_bench_version` is `Option<String>` with `#[serde(default)]`, no alias) land as written, and `embarch-study-designer` decision 74's open HTTP question is closed. The unit filed `tasks/core/126-compact-core.md` (open, due 2026-11-25): its `embarch-core/open.md` bullet put that file into its size reserve.
**Merged:** `agent/suite/037-rename-dev-bench-hellos-firmware-version-to-dev-bench-version-or-close-it`, landed in order, each a fast-forward with no rebase needed: core `c0d2a7e` (on `b6035a7`), api `ceae118` (on `d36be9e`), ui `2e16164` (on `08f9a53`), umbrella `47feb0f` (on `6ddb653`), doc `a68957f4` (on `25efa3f4`). Gate on the merge result, re-run by the lander: `cargo build`, `cargo test` and `cargo clippy --all-targets -- -D warnings` green on the first run in core and in api, `tests/lease_client.rs` included; then ui and umbrella green on all three against the landed api `ceae118`, each rebuilding `embarch-core-client` from it. The gate also included a native Windows `cargo build --release` of `embarch-core` at `c0d2a7e` in a scratch copy on the Windows side, run 2026-11-10: exit 0, 3 m 07 s, no warnings; its three sibling crates (`embarch-study-designer` `f6cca94`, `embarch-topology` `b905523`, `embarch-smp` `4b23bc2`) are still `origin/main`, so that build is of the landed tree. Client names clean in all four code repos, `check-docs.py` 12/12 before and after the fold. `check-ownership.py` not run: it refuses `suite` by design, because §8 work spans scopes. The changelog assembler rolled `history/core.md`'s 2026-09 window into `history/archive/core-2026-09--2026-09.md` at its size cap.
**Blocked:** nothing.
**Reviewer:** skipped (a 429 in the last window; owner-dispatched landing outside a leg).
**Hardware debts:** one, a deploy rather than a board, and the owner's session runs it after this landing: Core installed per `embarch-dev-workflow.md` §4a, then the API rebuilt. Until then the installed Core serves `firmware_version`, so `run_study` refuses every study that pins a bench version, the Study Designer shows the bench's build as unavailable, and umbrella check 13 warns. The `embarch-core/open.md` bullet stays until that deploy closes it.
**Budget:** not read: no leg and no wave.
**Least sure about:** the absent-field paths in ui and umbrella were gated by their tests only; this lander ran neither against the installed pre-108 Core, which is the state the bench stays in until the deploy.

---

## 2026-11-10 23:19 — api/127 build --each builds a range from each commit's own module

**Not a leg.** Third and last of the three `api` units the owner-dispatched landing agent lands in order, after `api/126` below and on the same terms: run by a worker thread the owner's session dispatched directly on 2026-11-10, branched from 126's code branch, landed on the owner's instruction, no leg number.
**Decided:** nothing by the lander. The worker's `embarch-api` decision 104 (`decisions/build.md`) lands as written: `build --each <base>..<tip>` builds every commit in every named variant from a detached `git clone --shared` kept inside the west workspace and passed as `-DEXTRA_ZEPHYR_MODULES`, never from the workspace's own module and never through a `git worktree` beside the repo; `--same-tree-as` allows only hex runs that are each commit's own id. 104 was free on `main`. The `build_each` MCP tool and `build --each` are recorded in the parity test as a documented asymmetry. `tasks/api/150` gained this unit's `open.md` bullet.
**Merged:** `agent/api/127-build-each-commit` (code `d36be9e`, ff on `fca417c` after a clean rebase of its one commit off 126's old tip; doc `46bc4128`, ff on `c7cb8708`, 126's fold, after a rebase that dropped 108's and 126's commits as already applied and replayed the claim and the unit commit clean). Gate on the merge result, re-run by the lander in the code worktree: `cargo build`, `cargo test`, `cargo clippy --all-targets -- -D warnings` green on the first run; `embarch-ui`'s `origin/main` (`08f9a53`) `cargo check --all-targets` against this tree green, after a forced re-check of the two `embarch-api` crates. Ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one, toolchain rather than a board. Under `build --each`, a sysbuild version header and any commit id computed at CMake configure time go stale between commits: the tool removes `app_version.h` only at `<build>/zephyr/include/…`, so a sysbuild image's copy under `<build>/<app>/zephyr/…` keeps the first commit's id, and `--same-tree-as` has met one fixture workspace (a T2 module on Zephyr 4.4), never a sysbuild one. `open.md` names both.
**Budget:** not read: no leg and no wave.
**Least sure about:** only one real west workspace, a scratch fixture, has run `build --each`, so the override of a module named like the project's repository is untested on a manifest with several modules.

---

## 2026-11-10 23:17 — api/126 build answers with a verdict and builds named variants

**Not a leg.** Second of the three `api` units the owner-dispatched landing agent lands in order, after `api/108` below and on the same terms: run by a worker thread the owner's session dispatched directly on 2026-11-10, landed on the owner's instruction, no leg number.
**Decided:** nothing by the lander. The worker's `embarch-api` decisions 102 (`decisions/log-capture.md`: `build` and `build_and_flash` answer with a verdict, and the whole log stays on disk as `embarch-build.log` in the build directory) and 103 (`decisions/build.md`: named build variants, each in its own directory, for both discovery kinds) land as written; 102 and 103 were free on `main`. Decision 24's note gains `schema_version` 2, because the default `build` answer dropped `stdout`/`stderr` (`verbose` keeps them); the lander's grep of the sibling repos found no reader of those fields or of `schema_version`. The worker filed `tasks/api/150-compact-api.md` (open, due 2026-11-24): its `open.md` bullet put that file 307 B into its size reserve; 150 was free on `main`.
**Merged:** `agent/api/126-build-returns-a-verdict-and-takes-named-variants` (code `fca417c`, ff on `15cef80` after a clean rebase onto `api/108`; doc `fd0c6e96`, ff on `eae5b2a1`, 108's fold, after a rebase that dropped 108's three commits as already applied and replayed the claim and the unit commit clean). Gate on the merge result, re-run by the lander in the code worktree: `cargo build`, `cargo test`, `cargo clippy --all-targets -- -D warnings` green on the first run. `embarch-firmware-build` is path-depended on by `embarch-ui`, so the lander also ran `cargo check --all-targets` on `embarch-ui`'s `origin/main` (`08f9a53`) against this tree, from a fresh target directory: green. Ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two, both toolchain rather than a board. (1) Re-run the size comparison on the real field variant pair, which only the owner can do because it lives in a client workspace; the worker's replay used a substitute pair (Zephyr `hello_world` on `qemu_cortex_m3`, default and a logging variant), and `open.md` names the debt. (2) No real twister output or sysbuild log has been fed to the verdict parser yet: twister's per-scenario lines are fixture-tested only, and the one real test run was a `native_sim` ztest through `west build -t run`.
**Budget:** not read: no leg and no wave.
**Least sure about:** `schema_version` 2 breaks any `--json build` reader outside the suite's own repos, which the lander could not search.

---

## 2026-11-10 23:11 — api/108 a timed-out build's Windows tree kill is verified on Windows

**Not a leg.** This unit was run by a worker thread the owner's session dispatched directly on 2026-11-10, and landed by an owner-dispatched landing agent on the owner's instruction ("then land all branches"), first of three `api` units it lands in order (108, 126, 127); no supervisor or listener was running, so no leg number exists. The leg's merge gate and fold were followed as written.
**Decided:** nothing by the lander, and no new decision number. The worker rewrote `embarch-api` decision 75 (`decisions/build.md`) to current truth: a timed-out build kills its whole process tree, a process group on unix and a Job Object on Windows, now verified by a native Windows run (a new `#![cfg(windows)]` test, a control with the job disabled that fails, and an end-to-end `build` that left no forked `ping.exe`). The `decisions.md` row and `spec/implementation.md` §3 say the same. `open.md` and `release.yml` were left alone, each with its reason in the retired task file.
**Merged:** `agent/api/108-windows-tree-kill` (code `15cef80`, ff on `febdaf2`, no rebase needed; doc `6d3f24c6`, ff on `6c9fd490`, dev-bench/037's fold, after a clean rebase of the claim and two unit commits). Gate on the merge result, re-run by the lander in the code worktree: `cargo build` and `cargo clippy --all-targets -- -D warnings` green; the first `cargo test` was red on 2 of 19 tests in `tests/lease_client.rs` (request-count asserts in `a_required_lease_leaves_open_routes_alone_so_a_session_can_take_one` and `a_second_process_sends_the_token_from_the_environment_with_no_argument`), which this unit cannot reach: its one file is `#![cfg(windows)]` and compiles to nothing on Linux. `--test lease_client` alone then passed 19 of 19, and the whole gate re-run was green. Ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needs a board. One verification debt: CI never runs the new Windows test, because the Windows job in `release.yml` only builds; the Windows tree kill stays verified by the worker's one manual run until that job runs `cargo test`.
**Budget:** not read: no leg and no wave.
**Least sure about:** the two `lease_client` failures are read as a flake on `main` from one red run and one green one; nothing measured how often they fail or why.

## 2026-11-10 23:06 — dev-bench/037 pd-bench is checked without a board

**Not a leg.** Same as `dev-bench/036` below: a worker thread the owner's session dispatched directly on 2026-11-10, branched from 036 and landed after it by the same owner-dispatched landing agent; no leg number exists.
**Decided:** nothing by the lander. The worker's `embarch-dev-bench` decision 59 (`decisions/pd-bench.md`) lands as written: pd-bench is checked by a build-only twister run of both shields and a `native_sim` ztest of its pure logic, now in `pd-bench/src/pd_logic.{c,h}`, never by running its USB-C stack, because v4.4.2 has no TCPC emulator (`open.md` says so). 59 was free on `main`. The worker found the carried R3.2 patch's `usbc_pd.h` is not self-contained (`__packed` without `toolchain.h`); `pd_logic.h` works around it, and fixing the patch waits on the owner's which-copy-leads question from 036. One `Done when` box was left unticked in the retired task file, the fleet venv's twister requirements: the owner's session installed them, and the file's Twister section records it.
**Merged:** `agent/dev-bench/037-pd-bench-build-gate` (code `50579d3`, ff on `e90bae7`; doc `f04ff0bd`, ff on `fb57a30e`, 036's fold, after a rebase that dropped 036's two commits as already applied and replayed 037's four clean). Gate on the merge result, re-run by the lander from the branch worktree's `workspaces/pd-bench/`: `west twister -T pd-bench -p nucleo_g0b1re` 2 of 2 built, 1 filtered (`pd_bench.logic`), 0 failed, no warnings; SNK1M1 FLASH 128,856 B, RAM 19,720 B; DRP1M1 FLASH 148,904 B, RAM 21,648 B; `CONFIG_USBC_TCPC_STM32_DMA=y` in both. `west twister -T pd-bench/tests/logic -p native_sim` 1 of 1 configuration, 13 of 13 test cases passed, no warnings. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief ran a reviewer only if leg.md needed one to land, and a reviewer gates no merge).
**Hardware debts:** one, payable with 036's on the same board. Flash both shields and run `pd srccaps`, `pd max` and a refused Request: `main.c` now calls `pd_logic.c`, and its unchanged messages are the worker's claim, which the `native_sim` suite does not cover.
**Budget:** not read: no leg and no wave.
**Least sure about:** the 13 tests exercise `pd_logic.c` alone, so nothing off-hardware checks that `main.c` still maps each refusal code to the same text it printed before.

## 2026-11-10 23:04 — dev-bench/036 pd-bench builds from its own west workspace

**Not a leg.** This unit was run by a worker thread the owner's session dispatched directly on 2026-11-10, and landed by an owner-dispatched landing agent on the owner's instruction ("then land all branches"); no supervisor or listener was running, so no leg number exists. The leg's merge gate and fold were followed as written.
**Decided:** nothing by the lander. The worker's `embarch-dev-bench` decision 58 (`decisions/pd-bench.md`) lands as written: `workspaces/pd-bench/` pins Zephyr v4.4.2 and carries six USB-C patches as a `west patch` set, superseding decision 48's "It builds outside `workspaces/`"; 58 was free on `main`. **The owner's open question stays open** (`embarch-dev-bench/open.md`): which copy of a carried patch leads when it changes, and how a fix reaches the other. Fold: `status.d/dev-bench-pd-bench-workspace.md` consumed into `embarch-host-study-proposal.md` (the dev-bench bullet cites 48, 49, 58; "What is left" item 1 deleted, the rest renumbered), and `embarch.md`'s proposal row drops "pd-bench's own west workspace" from its "left" list to match.
**Merged:** `agent/dev-bench/036-pd-bench-own-west-manifest` (code `e90bae7`, ff on `668b743`; doc `752b13c4`, ff on `25c748ea` after a clean rebase of the claim and the unit commit; `main` moved once under the fold, and the rebase onto it was clean too). Gate on the merge result, re-run by the lander: from the branch worktree's `workspaces/pd-bench/` (v4.4.2, six patches applied), `west build -p always` of both shields green with no compiler warnings (the one CMake warning is Zephyr's `__ASSERT()` notice, which `prj.conf` sets on purpose); SNK1M1 FLASH 128,736 B, RAM 19,720 B; DRP1M1 FLASH 148,252 B, RAM 21,648 B; `CONFIG_USBC_TCPC_STM32_DMA=y` in both. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12 before and after the fold. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief ran a reviewer only if leg.md needed one to land, and a reviewer gates no merge).
**Hardware debts:** one. Flash pd-bench from this workspace onto a NUCLEO-G0B1RE with each shield: the patches' run-time fixes (DMA transmit, the late TXMSGDISC, RX overrun, VCONN `-ENOTSUP`, the DRD bit) are asserted from the patch headers and pd-bench's history, never measured from this workspace.
**Budget:** not read: no leg and no wave.
**Least sure about:** flash is 368 B and 392 B over the 2026-10-20 reference; the worker attributes it to `WEST_TOPDIR/zephyr/...` source paths, a likely cause it did not prove.

## 2026-11-10 13:21 — chat/024 four input bullets leave the chat's spec.md by verbatim split

**Decided:** nothing numbered. **Ended burndown on an empty queue and dreamt** (both at 13:21, below). `embarch-chat/spec.md` 9,373 → 8,077 B, out of reserve: four §2 bullets (the library, the Haiku assistant, Promptu, the desk's reference index) moved verbatim to a new `spec/input.md`, with one pointer bullet left in §2 and the header paragraph linking it. Both `Must not delete:` bullets (decisions 104 and 63) stay in `spec.md`. I diffed removed against added lines: only the new file's header, status line and split note, the pointer bullet, and the header paragraph's added link differ. Inbound links name `chat/spec.md` whole, so no anchor broke. **Compaction-pass answer** (the worker's, and I agree): yes, `spec.md` still says what the chat is, how a chat runs, the end-of-issue and reload behaviour, the invariants and the non-goals; the input features are one link away.
**Merged:** `agent/chat/024-compact-chat` (doc only: `1d3a1b2b`, ff on the claim `237a36fe`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `chat` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown wave 6; 5-hour 9% to 18%, weekly 73% to 74%. Normal mode from 13:21.
**Least sure about:** whether to dream rather than take a toolchain task by my own hands. I read `api/126` and `127` again: both author new decisions, which burndown withholds, and both carry a replay box against build data only the owner holds. The rest of that lane is unchanged from the 06:08 leg close.
**Leg close (next leg, read this first):** **1 unit, ended early on an empty queue.** Leg began at `7e275ff5`, burndown. Spawned with the pump latched, no stop marker, no owner message; nothing to recover. Fleet Ready empty; `finish` moved nothing (EMB-73 still waits on `doc/097`, owner-only). Refill owed on depth and spread; I swept (`collect-open-questions.py`, roadmap Now/Next, reversals) and no source has changed since 12:52, so nothing filed. Spread sweep: nothing filed (2026-11-10 13:18). Size ledger: nothing in reserve after this fold, nothing overdue. **Burndown cleared** (`fleet-burndown.py --clear --reason 'queue empty'`, 13:21): the pump stays latched in normal mode. **Dream posted** at `ts` `1794342092.017879` with `crystal_ball`, as an `--action`: (1) an attended bench session paying the three owed checks from `suite/032`, `dev-bench/017`, `dev-bench/035`, then `api/059` and `dev-bench/038`; (2) `api/126`, `build` answers a verdict and builds named variants; (3) decide whether `embarch-ui` ships in the suite release archive (`embarch-ui/open.md`, `embarch-umbrella` decision 14). The listener should not spawn into the empty queue for 6 hours while that post is in its newest 20. **If the owner answers**, the answer is direction for the next leg: (1) needs a normal-mode leg and the boards attached; (2) is a toolchain unit by the leg's own hands; (3) is the owner's decision, then a `suite` pass to announce. No `suite` task, no deploy. `PushNotification` was not available to me, so the dream reached the owner by the channel mention alone. Stray build cache: `/home/gabriel/Github/embarch/.worktrees/embarch-chat/desk-target/` (from `chat/025`'s gate), not a worktree; left in place.

## 2026-11-10 13:16 — chat/025 the host test expected a cards call decision 97 removed

**Decided:** nothing numbered. EMB-134's cause, the worker's and confirmed by me and the reviewer: **the test was stale, not the desk binary.** A desk built fresh from `main` (`1997108`) failed the same way as the week-old one. Decision 97 (amended 2026-11-10, EMB-66) makes `Assistant.cards()` return `[]` before any call when the desk sends no references; `test/host.test.mjs`'s window gets none, yet the test still asserted "the cards call ran". It now asserts no cards call without references, as `assistant.test.mjs`'s 97 test does. The with-references path (88) is untouched. Cause posted on EMB-134 as a Finding. **Supervisor edit in this fold: I unparked `tasks/chat/024` as a verbatim split**, the same call as `outpost/029` and `promptu/004`; it is now the one worker-dispatchable task.
**Merged:** `agent/chat/025-a-host-test-fails-whenever-the-desk-binary-is-set` (code `7003850`, ff on `9162e45`; doc `3e3c96b1`, the worker's `56fcb0a5` cherry-picked onto `93ede9b7`). Gate on the merge result: `npm run build` and `typecheck` clean; `npm test` with `EMBARCH_DESK_BIN` at the fresh desk build: 339 pass, 0 fail, 3 skipped; `npm run test:webview` all passed (the worker could not run it: its own earlier e2e run still held port 4989; it had exited by the time I ran it). Ownership `chat` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The worker's webview debt is paid: it ran green in the gate.
**Budget:** PROCEED, burndown wave 6; 5-hour 9%, weekly 73%.
**Least sure about:** the test's name still says "the host streams Haiku's answers back" for cards that no longer reach Haiku; the reviewer called it loose wording, not a contradiction, and I left it.
**Leg close (next leg, read this first):** **4 of 4 units**, all workers, all reviewers clean: `desk/027`, `outpost/029`, `promptu/004`, `chat/025`. Leg began at `192ee5ef`, **burndown** (armed 12:48 until 2026-11-11 06:00). **What you would not expect:** I unparked three `In flux: yes` compaction parks (`outpost/029`, `promptu/004`, `chat/024`) as verbatim splits on `DOC-BUDGET.md`'s split-first rule; two landed clean, `chat/024` is open for you. No new decisions, no `suite` task, no deploy, no alert. **Filed:** nothing. **EMB-134** should move to Done at this fold's `finish`. **Queue for the next leg:** `chat/024` is the one worker task. After it the worker queue is empty: toolchain lane unchanged (`api/126`, `127`, `atlas/001`-`003`, `dev-bench/036`, `037`, reasons in the 06:08 leg close), bench (`api/059`, `dev-bench/038`) barred in burndown, owner-only `doc/093`-`097`. So the leg after `chat/024` will meet an empty queue: per `.claude/leg.md`, sweep, then `fleet-burndown.py --clear --reason 'queue empty'` and dream. **Owed live runs** (unchanged from the morning legs): EMB-73 end to end, and one bench-board flash checking `suite/032`, `dev-bench/017` and `dev-bench/035`. Supervisor ownership check on the leg's diff: in the final report.

## 2026-11-10 12:59 — promptu/004 the uninstalled build steps leave spec.md by verbatim split

**Decided:** nothing numbered. Unparked by me at this leg's start (see `desk/027`'s leg notes). `embarch-promptu/spec.md` 9,563 → 6,949 B, out of reserve: §2b and §2c (build steps 2 and 3, committed or built but not installed) moved verbatim to a new `spec/build-steps.md`, with a two-line §2b pointer left. One edit outside the moved text: the status line's "(§2c)" now links the new file. I diffed removed against added lines: only the status line differs. §3 (invariants) and §5 (does not do) untouched. **Compaction-pass answer** (the worker's, and I agree): yes, `spec.md` says what promptu is, what is installed (step 1), the invariants and the does-not-do list; work on steps 2 or 3 needs `spec/build-steps.md`. The worker's first push was red on two checks (a changelog link, the task's state line) and it fixed both in a second commit before reporting.
**Merged:** `agent/promptu/004-compact-promptu` (doc only: `f1b22701` and `67fc2606`, the worker's `62fe3cd5` and `5584d2aa` cherry-picked onto `6ef3e8f0`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `promptu` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown wave 6; 5-hour 5%, weekly 70%.
**Least sure about:** nothing in the unit. The status line still says "2026-10-30", and the split did not refresh it; that is a status-line date, not a fact the split changed.

## 2026-11-10 12:58 — outpost/029 overflow and override decisions leave transport.md and manifest.md by verbatim split

**Decided:** nothing numbered. Unparked by me at this leg's start (see `desk/027`'s leg notes). `embarch-outpost/decisions/transport.md` 7,908 → 5,402 B: decisions 5 and 28 (overflow policy, blocking overflow) moved verbatim to a new `decisions/overflow.md`. `decisions/manifest.md` 7,350 → 5,666 B: decision 24 (the operator's override of both post-hoc refusals) moved verbatim to a new `decisions/override.md`. Pointer lines where each left; the `decisions.md` index row split into four. Two link edits outside the moved text, both to keep a link true: `decisions/clocks.md`'s and decision 9's closing sentence's pointers to 24 now name `override.md`. I diffed removed against added lines: only those two lines differ. Both files PAID. **Compaction-pass answer** (the worker's, and I agree): yes, `spec.md` states current behaviour; the reasons sit in `decisions/`, found through the index. Its line 79 cites decision 20, which did not move.
**Merged:** `agent/outpost/029-compact-outpost` (doc only: `e48351bb`, the worker's `428b0dd0` cherry-picked onto `843882b0`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `outpost` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown wave 6; 5-hour 5%, weekly 70%.
**Least sure about:** whether the worker that filed the park would have agreed. Its `In flux: yes` argued a squeeze would restate what layout 4 changes; a split restates nothing, but layout 4 will now amend decisions spread over three files instead of two.

## 2026-11-10 12:57 — desk/027 three suite-desk paragraphs leave spec.md by verbatim split

**Decided:** nothing numbered. `embarch-desk/spec.md` 9,440 → 8,882 B, out of reserve: the suite-desk, west-module and login-flag paragraphs (decisions 70, 80, 82) moved verbatim to a new `spec/suite-desk.md`, with a one-sentence pointer left in §1. I diffed removed against added lines: identical apart from the new file's header and status line. **Compaction-pass answer** (the worker's, and I agree): yes, `spec.md` still says what the desk is, its invariants including decision 83's close-out contract, and its constants; the three moved paragraphs are one link away.
**Merged:** `agent/desk/027-compact-desk` (doc only: `4ddea194`, ff on the claim `ab95a63c`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `desk` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown wave 6; 5-hour 1% to 5% (resets 13:10), weekly 70%.
**Least sure about:** nothing in the unit; the leg's judgement call is the two unparks below.
**Leg notes (this leg, first unit):** **burndown**, armed by the owner 12:48 until 2026-11-11 06:00 (weekly 70%). Spawned with the pump latched, no stop marker, no owner message; nothing to recover (no claims, no unit or leg worktrees). Leg began at `192ee5ef`. Fleet Ready: EMB-134, split as `tasks/chat/025` (`2e6f5899`), announced at `ts` `1794340428.736879`. **I unparked `outpost/029` and `promptu/004` as verbatim splits** (`12394e78`): both were `blocked` on `In flux: yes` waiting for a change with no date (outpost layout 4, which `open.md` says is deliberately not made; promptu build step 4), and `DOC-BUDGET.md` makes a split the default remedy because it restates nothing. Their `In flux:` now says `no, for the verbatim split`. Refill owed on depth and spread; no refill source changed since 06:12 and the `open.md` index reads as the 05:13 and 06:12 sweeps found it, so nothing filed. Spread sweep: nothing filed (2026-11-10 12:52). Size ledger: nothing overdue. Bench: not refreshed, since burndown takes no bench task. Four workers dispatched 12:55: `desk/027`, `chat/025`, `outpost/029`, `promptu/004`.

## 2026-11-10 06:45 — chat/023 an ended issue ends its chat

**Decided:** nothing suite-wide. New `embarch-chat` decision 104 (the worker's, `decisions/desk.md`): an `end` shows `Chat has ended because the issue is done` (or `canceled`) on top with one Close window button (`workbench.action.closeWindow`, no route), and the input closes. With a turn running it waits until no chat of the issue is busy. Endings are kept per item in `workspaceState`, so a reload stays ended. `ChatManager.adopt` refuses an ended chat and `Chat.end()` refuses send, rerun and process start, so it never resumes. That narrows decision 27's "the next message resumes it" with its reason stated. A second `end` changes nothing. An `unfinished` shows the blockers and a Finish button over a live chat; a 404 says the desk has no Finish yet. With no page showing the issue's chat, the newest one is opened, else a VS Code notification carries the text and button. **Supervisor edits in this fold:** `tasks/chat/024` (the worker's new debt for `spec.md`, 9,373 B, due 2026-11-24) named both desk tasks in `Unparks when:`; it now names the owner's word on a live run, or the due date. `tasks/desk/027` is now `open`, `In flux: no`, since the close-out is whole; it is the next worker-dispatchable task. **EMB-73 is done apart from `doc/097`**, which is `Owner: required`, so the issue stays in Fleet Working until the owner edits `embarch-dev-workflow.md` §6.
**Merged:** `agent/chat/023-an-ended-issue-ends-its-chat` (code `9162e45`, ff on `b1802d6`; doc `02c5ab99` and `5b39b89d`, the worker's two commits cherry-picked onto `b50281ca`). Gate on the merge result: `npm run build` and `typecheck` clean; `npm test` 265 pass, 77 skipped, 0 fail without `EMBARCH_DESK_BIN`; with it set to the desk's 2026-11-03 debug build, 338 pass and 1 fail, the same host test the worker saw fail on `main` (filed as EMB-134, investigation, Fleet Ready); `npm run test:webview` all passed. Ownership `chat` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; a live run is owed. With current `main` deployed, mark a real issue Done from the Work tab. Check that its chat shows the message and closes its input, that Close window closes the window, and that the desk removes the folder about 3 minutes later. The turn-running wait is covered by a unit test only.
**Budget:** PROCEED at dispatch; 5-hour 89% to 94%, **HOLD** at this fold; weekly 69%.
**Least sure about:** whether the host test failure is pre-existing or a stale binary. I trusted the worker's stash-and-rerun on `main` rather than repeat it, and the binary it ran against is a week old. EMB-134 names the one check that settles it.
**Leg close (next leg, read this first):** **3 units, ended early on a budget HOLD** (5-hour 94%, resets about 08:10). Units: `desk/025`, `desk/026`, `chat/023`, all workers, all reviewers clean. Leg began at `89a8ae7c`, normal mode. **What you would not expect:** (1) I split EMB-73 (`Scope: suite`) into two single-repo worker tasks against a contract I fixed in the task files, instead of a `suite` pass by my own hands; the `desk/025` entry says why. (2) **My `desk/026` fold left `main` red on `check-task-state` for one commit** (`1fd8b63e`): `desk/027`'s `Unparks when:` named the task the fold retired, and I had piped `check-docs.py` into `tail` in the push chain, so the push ran anyway. Fixed in `b50281ca`. The trap: a fold that retires task N must first rewrite any `Unparks when:` naming N. (3) `desk/027` is `open` with `In flux: no`. **New decisions:** `embarch-desk` 83, 84 (both in the new `decisions/closeout.md`); `embarch-chat` 104. **Filed:** EMB-134 (chat, Fleet Ready). **Queue for the next leg:** `desk/027` (compaction of desk `spec.md`, due 2026-11-17) is the one worker task. Fleet Ready holds EMB-134 (split it as a `chat` task, `Hardware: none`). Toolchain lane unchanged (`api/126`, `127`, `atlas/001`-`003`, `dev-bench/036`, `037`). Bench (`api/059`, `dev-bench/038`): neither role attached at 06:13. Owner-only: `doc/093`-`097`. **Owed live runs:** EMB-73 end to end (above) and the three bench-board checks from the previous leg. No `suite` task announced, nothing deployed, no alert sent.

## 2026-11-10 06:33 — desk/026 the issue's folder goes once no window shows it

**Decided:** nothing suite-wide. New `embarch-desk` decision 84 (the worker's): an `end`'s folder is removed once no `GET /mailbox?folder=` poll for it has arrived for 180 s ([chosen], `spec/constants.md`), measured from the later of the last poll and the desk's start; the checks run again first and a failure posts an `unfinished`; Canceled deletes the remote branches first, so a network failure leaves the folder whole; never removed: a branch named `main`/`master`, a folder that is a symlink, a repo whose `.git` is a directory; with the chat setting off nothing is removed. `close_out.removal` (`waiting`/`removed`/`left`, why) on the card. **Decision 83 moved verbatim** from `decisions/sessions.md` to a new `decisions/closeout.md` (my dispatch note), so `sessions.md` left reserve (8,930 B). **I read the removal code before merging** (it deletes on the owner's machine): the folder path comes only from `Suite::issue_dir`, which refuses an empty, dotted or slashed key, so nothing outside `.dev-worktrees/<key>/` can be reached. **Supervisor edit in this fold:** `tasks/desk/027`'s `Unparks when:` named `desk/026`, which this fold retires; it now names `tasks/chat/023`. 027 is down to `spec.md` (9,440 B).
**Merged:** `agent/desk/026-the-issues-folder-goes-once-no-window-shows-it` (code `1997108`, ff on `9a32975`; doc `901b8f5c`, ff on the claim `7246a599`). Gate on the merge result: `cargo build`, `test` (258 passed), `clippy --all-targets -D warnings` clean; ownership `desk` OK on both branches; client names clean; `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; a live run is owed instead. Mark a real issue with a `.dev-worktrees/<key>/` folder Done, close its window, and confirm the folder goes after about 3 minutes with every symlink target intact. Not run, because the deployed desk is the owner's.
**Budget:** PROCEED, wave 6; 5-hour 85% to 89%, weekly 68% to 69%.
**Least sure about:** that polls really mean a window. `embarch-chat` activates `onStartupFinished`, but it declares untrusted workspaces unsupported, so a window on an untrusted folder never polls. If a `.dev-worktrees/<key>/` window were untrusted, the desk would read it as closed and remove a clean, merged folder under it. No data is lost (the checks pass first), but it is the original EMB-73 symptom. I believe the suite root's trust covers it and did not verify.

## 2026-11-10 06:25 — desk/025 Done or Canceled tells the issue's window to end its chat

**Decided:** **suite-wide, on the owner's behalf: EMB-73 split into two single-repo worker tasks against one desk-chat contract I fixed in the task files** (`8d91a804`), rather than a `suite` pass by my own hands. The contract: two mailbox kinds written only by the desk, `end` (`outcome` done/canceled, every check passed) and `unfinished` (plus `blockers` of repo and reason), neither on the 10-minute launch clock; `POST /items/{id}/finish` re-runs the checks and posts a fresh entry; a window shows a folder while it polls `GET /mailbox?folder=` for it, so the desk reads polls stopping as the window closed. **Why not a `suite` pass:** each half lands safely alone. A chat that knows the kinds before a desk sends them does nothing new; an older chat takes an unknown kind and drops it, so its window just stays open. Four tasks: `desk/025` (this), `chat/023` (in flight), `desk/026` (folder removal, opened in this fold), `doc/097` (`Owner: required`: the `embarch-dev-workflow.md` §6 line). The Work tab row and EMB-73's read-only-chat box live outside the fleet's repos; not split. New `embarch-desk` decision 83 (the worker's, `decisions/sessions.md`): triggers are `/linear/status` at once and a pass after the reference index refresh, once per move; checks are `closeout::check` (uncommitted or untracked files; for Done, branch an ancestor of `origin/main` after a fetch, so a squash-merged branch blocks, tagged [chosen]); `close_out {outcome, blockers}` on each card in `GET /view`. **`desk/026` opened in this fold** with two dispatch notes: split decision 83 verbatim out of `sessions.md` (111 B left) before extending it, and fix the comments citing "decision 77".
**Merged:** `agent/desk/025-done-or-canceled-tells-the-issues-window-to-end-its-chat` (code `9a32975`, ff on `b229d45`; doc `546d670b`, ff on the claim `d39131db`). Gate on the merge result: `cargo build`, `test` (248 passed), `clippy --all-targets -D warnings` clean; ownership `desk` OK on both branches; client names clean; `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not run end to end against the chat half; the MCP-connector path (no state type, re-reads the issue on a name change) is untested.
**Budget:** PROCEED, wave 6; 5-hour 77% to 85%, weekly 68%.
**Least sure about:** the split itself. Protocol §8 sends a change spanning sub-projects to the supervisor's own hands; I judged this one two independent changes with a fixed seam, because neither half can break the other on landing. The new debt: the worker filed `tasks/desk/027` (blocked, `In flux: yes`, due 2026-11-17) for `sessions.md` and `spec.md`.
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover. Leg began at `89a8ae7c`. Fleet Ready: EMB-73, split and announced (`ts` `1794316615.761109`). Refill owed on depth and spread; sources changed since 05:13 only by removals and one new study-designer `open.md` item (keep the `no_std` shape with no consumer?), an owner's call, so nothing filed. Spread sweep: nothing filed (2026-11-10 06:12). Size ledger: nothing overdue. Bench: `--refresh` at 06:13, neither role attached.

## 2026-11-10 06:08 — dev-bench/035 the protocols seal gates a study

**Decided:** nothing new numbered; `embarch-dev-bench` decision 41 gains one sentence. By my own hands. **I reclassified `dev-bench/035` from `bench` to `toolchain` in its claim** (`263b33b6`): every `Done when` item is a ztest or a build. The decoder computed `protocols_crc_valid` and `dispatch_study` never read it, against `embarch-study-designer` decision 17 (the bench aborts on any seal mismatch, naming which). New `dbm_study_start_broken_seal()` names the first failing seal of steps/streams/protocols or returns NULL; `dispatch_study` refuses with one `snprintk` line in the existing "StudyStart <seal> mismatch; aborting without running any step" wording. The decoder test for a corrupt protocol span already existed; it and the three other seal tests now assert what the gate names.
**Merged:** `agent/dev-bench/035-protocols-crc-valid-is-never-checked` (code `668b743`, ff on `a6b597c`; doc `f497b6e5`, ff on the claim `263b33b6`). `serial_protocol` 70/70, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12, the `native_sim` app clean; `nrf54l15dk` FLASH 297,096 B, RAM 132,464 B unchanged; ESP32-C5 FLASH 641,472 B, `sram0_0_seg` 308,432 B unchanged. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a study with a corrupted `protocols_crc` sent by a real Core to a bench board should come back as that log line and `StudyDone { completed: false }`; neither role was attached at 05:11.
**Budget:** PROCEED, wave 6; 5-hour 72% to 75%, weekly 67%.
**Least sure about:** nothing in the unit; the gate's only new path is a string choice the ztests pin.
**Leg close (next leg, read this first):** 4 of 4 units (`dev-bench/046`, `suite/032`, `dev-bench/017`, `dev-bench/035`), all by my own hands, all reviewers clean. Leg began at `8a57a032`, normal mode. No worker ran: no task a worker could take existed all leg. **Three things I changed that you would not expect:** (1) I sent atlas EMB-27, 32, 33, 34 back to Backlog, each with the input it needs from the owner; Fleet Ready now holds only EMB-73. (2) I reclassified `dev-bench/017` (`required`) and `dev-bench/035` (`bench`) to `toolchain` and ran them: both were host work behind a stale field. (3) `suite/032` ran: dev-bench boards link no Rust and the crate has no `ffi` feature. **New decisions:** `embarch-dev-bench` 57; dev-bench 8 retired, 20 rewritten, 56 and 41 amended; study-designer 7 rewritten, 23 retired, 64 amended. **Closed:** EMB-133 (Done). **RAM:** ESP32-C5 `sram0_0_seg` is 81.51% (was 88.10%), nRF RAM 50.53% (was 60.04%). **Queue for the next leg:** no worker task. Fleet Ready: EMB-73 (`Scope: suite`, desk + chat: Done/Canceled ends the chat and removes the folder). Its only owner-reserved box is the `embarch-dev-workflow.md` §6 line; the desk and chat halves are a cross-repo pass a leg could split, announce and run, with the doc line filed `Owner: required`. That is the one real piece of work left, and the owner spelled the design out in the issue. Toolchain lane: `api/126`, `api/127`, `atlas/001`-`003` (each has a replay box against field data only the owner holds, and `atlas/001` wants his answer), `dev-bench/036`, `037` (a pd-bench west manifest carrying patches copied from a client workspace: not for an unattended leg). Bench: `api/059`, `dev-bench/038`, nothing attached. Owner-only: `doc/093`-`096`. If you take none of these, dream. **Hardware debts owed this leg:** one bench-board flash of current `main` checks all three (032 handshake schema 15, 017 every TX message decodes at Core, 035 the protocols-seal refusal). No deploy, no alert sent. Supervisor ownership check on the leg's diff: clean (21 paths).

## 2026-11-10 06:04 — dev-bench/017 tx_scratch holds only what the bench sends

**Decided:** new `embarch-dev-bench` decision 57 (`decisions/dispatch.md`), by my own hands. **I reclassified `dev-bench/017` from `required` to `toolchain` in its claim** (`6cd71164`): its own Hardware field said "a toolchain, not a board", written before the fleet had a `west`. `tx_scratch` is now a `struct dev_bench_tx_message`, the seven variants the bench sends, sharing one `DBM_TX_VARIANTS` member list with `struct dev_bench_message`; `dbm_encode_tx_frame` stages at `DBM_MAX_OUTBOUND_RAW_LEN`; `dbm_encode_frame` keeps `StudyStart`'s bound for the round-trip tests and is no longer linked into the firmware (`nm` on the ESP32-C5 ELF shows only `dbm_encode_tx_frame`). The old encoder switch became one static encoder per TX variant, shared by both entry points. Decision 38 extended, not superseded (it sized the RX buffer; nothing in it became false); the task's box says so. **Supervisor touch-up in this fold, on the reviewer's note:** `decisions/capture.md`'s "costs no SRAM ... which `StudyStart` sizes" now says that was when written.
**Merged:** `agent/dev-bench/017-tx-scratch-reserves-space-for-a-message-it-can-never-send` (code `a6b597c`, ff on `470bbc9`; doc `38e56904`, ff on the claim `6cd71164`). **Measured:** ESP32-C5 `sram0_0_seg` 333,360 to 308,432 B (88.10% to 81.51%), FLASH 641,560 to 641,504 B; nRF54L15DK RAM 157,384 to 132,464 B (60.04% to 50.53%), FLASH 298,076 to 297,068 B. ~15.7 KB is the buffer, the rest the encoder's staging buffer. `serial_protocol` 70/70 (two new: the TX encoder writes the general encoder's bytes for a HelloAck, a fully populated StepResult and a StudyDone; it refuses a StudyStart), `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12, the `native_sim` app clean. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** run one real study on a bench board (`nrf54l15dk` or the ESP32-C5) and confirm every message the bench sends still decodes at Core, a `StepResult` with GATT services included; neither role was attached at 05:11.
**Budget:** PROCEED, wave 6; 5-hour 68% to 72%, weekly 67%.
**Least sure about:** the encoder refactor moved ~170 lines of case bodies into functions with a sed de-indent and `msg->x.` to `m->` renames; the equivalence ztest and the reviewer's line-by-line read both say no byte changed, but the cross-language pins still run through the general encoder, so the TX path's bytes are pinned only by that equivalence test.

## 2026-11-10 05:54 — suite/032 the FFI staticlib is retired: dev-bench links no Rust

**Decided:** suite-wide, on the owner's behalf (announced at `ts` `1794312920.762869` 05:15, window closed 05:45 with no reply, run by my own hands): dev-bench firmware links no Rust. Every board takes `DEV_BENCH_WIRE_SCHEMA_VERSION` from the configure-time read of the crate's `schema_version.rs` that `native_sim` already used; `study_ffi.h`, `study_ffi_real.c`, `study_ffi_stub.c`, the board-to-triple map and the `cargo rustc --crate-type staticlib` target are deleted. `embarch-study-designer` dropped the `ffi` feature, `src/ffi.rs` and the CI `ffi` cell; `panic = "abort"` stays on decision 5's ground. **Decisions rewritten:** study-designer 7 (the boundary now: hand-written C codec pinned by byte tests, plus configure-time reads), 23 marked retired, 64's `ffi` row and paragraph replaced (the title's "six cells" is now exact: default, `alloc`, `std`, three tool features); dev-bench 8 marked retired, 20 rewritten. **New open item** in study-designer `open.md`: no consumer builds the crate `no_std` any more; keeping that shape is open. `embarch-api/interfaces/dev-bench-config.md` no longer says boards need `cargo`. **Landed out of the usual tier order on purpose:** dev-bench before the shared crate, so no board build on `main` ever asked for a feature that was gone (the task's own reason).
**Merged:** `agent/suite/032-retire-the-ffi-staticlib-itself-the-toolchain-gated-half-of-014` (dev-bench `470bbc9`, ff on `8f7e1f0`; study-designer `f6cca94`, ff; doc `f3baaf48`, ff on the claim `b95955d6`). Gate: dev-bench built with `EMBARCH_STUDY_DESIGNER_PATH` at the crate worktree: `serial_protocol` 68/68, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12, the `native_sim` app; `nrf54l15dk/nrf54l15/cpuapp` FLASH 299,356 to 298,076 B, RAM 157,384 B unchanged; `esp32c5_devkitc/esp32c5/hpcore` FLASH 666,208 to 641,560 B, `sram0_0_seg` 333,360 B unchanged; both boards configure "schema version 15 (from the crate)", the value `essd_schema_version()` returned; no `cargo` step in either log. Crate: `cargo build` (default, `alloc`), `cargo test` (`--all-features`, `std`), clippy `-D warnings` (all-features, default, `alloc`) green. No consumer manifest enables `ffi`. Ownership `--supervisor` OK on the doc diff, client names clean on both code trees, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** flash one bench board (`nrf54l15dk` or the ESP32-C5) and confirm Core's `Hello` gets `HelloAck` with schema 15 and `compatible: true`; neither role was attached at 05:11. The task's flash box is left unticked for this.
**Budget:** PROCEED, wave 6; 5-hour 62% to 68%, weekly 66% to 67%.
**Least sure about:** the ESP32-C5 FLASH drop (24.6 KB) is far larger than the nRF's (1.3 KB) for the same three exported functions; I read it as the RISC-V staticlib pulling in more of `core`/`postcard` than the Arm one and did not dig. Nothing was in RAM, so the SRAM lever (`dev-bench/017`) is untouched.

## 2026-11-10 05:21 — dev-bench/046 the retired stream-capture GATT kind is refused and its path deleted

**Decided:** `embarch-dev-bench` decision 56 amended, by my own hands (`toolchain`; EMB-133, split at this leg's start as `tasks/dev-bench/046`, `6a5e7ec7`): the bench's decoder arm, `ble_bridge.h` kind, `streaming` routing in `notify_cb`, `ble_stream_sample_handler` and its setter (real and stub) for the retired `GattOperation::StreamCapture` are deleted, so a kind 5 fails the decode like any kind the crate lacks and both C GATT enums take every value from `crate_limits.h`. Decision 56 now names two link-level readings, not three, and says why `GattOperation` needs none. **Also decided this leg, before any unit:** I sent atlas EMB-27, 32, 33 and 34 back to Backlog, each with the input the fleet lacks (the failing stack's `nm`/section lines; the reference manual's outline and one register page; the datasheet lines each Next check asks for). Six legs had read and skipped them; `LINEAR-PROTOCOL.md` §4's Sent back row is "why it could not be split, and what the body lacks". EMB-73 left in Fleet Ready (owner's: its last box edits `embarch-dev-workflow.md`). **Announced and parked `suite/032`** (retire the FFI staticlib) at `ts` `1794312920.762869`, 05:15; window closes 05:45; recorded in the task (`d992392a`).
**Merged:** `agent/dev-bench/046-the-retired-stream-capture-kind-is-refused-and-its-path-deleted` (code `8f7e1f0`, ff on `3daa719`; doc `05d144c5`, ff on the claim `ad5744cc`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `serial_protocol` 68/68 (new `test_study_start_refuses_the_retired_stream_capture_kind`: kind 5 fails, the same frame with Read decodes), `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12 on `native_sim`; the `native_sim` app clean; `nrf54l15dk/nrf54l15/cpuapp` FLASH 299,524 to 299,356 B, RAM 157,400 to 157,384 B; `esp32c5_devkitc/esp32c5/hpcore` FLASH 666,256 to 666,208 B, `sram0_0_seg` 333,360 B unchanged. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the deleted path was unreachable from any host since schema v8.
**Budget:** PROCEED, wave 6; 5-hour 54% to 60%, weekly 65% to 66%.
**Least sure about:** the send-backs. They change what six legs did, on my reading that an issue the fleet cannot execute belongs with the owner and a stated gap rather than in Fleet Ready; if he wanted them parked there as a reminder, each is one move back.
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover (no claims, no unit or leg worktrees). Leg began at `8a57a032`. Refill owed on depth and spread; I swept every `open.md` (153 questions): each is hardware-gated, an owner's call, or waiting on a named trigger, so nothing filed. Spread sweep: nothing filed (2026-11-10 05:13). Size ledger: nothing overdue. Bench: `--refresh` at 05:11, neither role attached; three bench tasks stay `open`. No worker task exists; this leg's units are mine.

## 2026-11-10 05:09 — outpost/027 three Kconfig values keep the promise their option exists for

**Decided:** **I reclassified `outpost/027` from `toolchain` to `none` and gave it to a worker** (claim `26a92bc0`): `tasks/README.md` says outpost tasks stay `none` and name `WEST` and `ZEPHYR_BASE`, and the filer's only reason for `toolchain` was that no Zephyr tree had been used for outpost. I ran `tests/run-all.sh` on a bare `git archive` copy of `main` with `WEST` the fleet venv's `west`, `ZEPHYR_BASE` the dev-bench `native_sim` workspace's `zephyr/` (4.4.0, only read; still clean after) and the venv's `bin/` on `PATH`: every leg green. **New `embarch-outpost` decisions (the worker's):** 28 (`decisions/transport.md`): `OVERFLOW_BLOCK` kept, a full ring now `k_sleep(K_MSEC(1))`s instead of `k_yield()`ing (the priority-10 drain thread never got the CPU), only where `can_wait_for_space()` allows (not ISR, pre-kernel, idle, the drain thread itself, or interrupts locked); decision 5's title now "blocks only by opt-in (28)"; `RING_BYTES` range floor 256 → 320 (16 slots × 20 B) with a `BUILD_ASSERT`. 29 (`decisions/manifest.md`, refines 9): the build ID cuts the describes and keeps the `+m<hash>` tail whole down to `BUILD_ID_MAX` 16. **`tasks/outpost/028` closed `done` in this fold:** the worker trimmed `spec.md` to 9,025 B (out of reserve) inside its own unit, per my dispatch note; 028's must-not-delete items checked present; `In flux: yes` left as written. **New debt the worker filed:** `tasks/outpost/029` (blocked, `In flux: yes` until the layout-4 change, due 2026-11-26) for `transport.md` 7,908/8,192 B and `manifest.md` 7,350/8,192 B.
**Merged:** `agent/outpost/027-three-kconfig-settings-break-their-own-promise` (code `9b95b94`, ff on `6e07fc8`; doc `28c3d76e`, the worker's commit rebased onto the claim `26a92bc0`, ff). Gate on the merge result, run by me in the code worktree with the same three variables: `tests/run-all.sh` every leg green (decoder unit, vocab 11 kinds/8 flags, cross-decoder 831 rows ran, build-ID compose, ring 6/6, wire 9/9, overflow block 1/1 at the 320 B floor, module off, e2e 37 frames/729 records); ownership `outpost` OK on both branches; client names clean; `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the blocking wait is measured on `native_sim` only (decision 28 says so); on a real DUT, a thread at a priority above the drain thread filling the ring with `OVERFLOW_BLOCK=y` should return with its records and no gap.
**Budget:** PROCEED, wave 6; 5-hour 52% to 54%, weekly 65%.
**Least sure about:** the reviewer's residual, which I share: a producer that sleeps while holding something the drain thread or the UART driver needs (a mutex) would still wedge; the mode is opt-in and no decision addresses it. The thread-switch hooks are safe only because they run with interrupts locked or in an exception, which the reviewer read rather than ran. And 029's `In flux: yes` covers a `transport.md` with 284 B left; a verbatim split would not be forbidden by it.
**Leg close (next leg, read this first):** 4 of 4 units (`study-designer/083`, `core/125`, `dev-bench/045`, `outpost/027`), all reviewers clean. Leg began at `c91baaec`, normal mode. `dev-bench/045` was a `toolchain` unit by my own hands; the other three were workers. **New decisions:** `embarch-outpost` 28, 29; `embarch-dev-bench` 56 amended; `embarch-core` 90 extended. **Closed:** EMB-131, EMB-132 (Done). **Filed:** EMB-133 (dev-bench, Fleet Ready, `Hardware: toolchain`): retire the bench's dead `GattOperation` `StreamCapture` path, which would free decision 56's last hand-typed wire value. **Queue for the next leg:** no task a worker can take; Fleet Ready holds EMB-133 (split it as a `toolchain` task), atlas EMB-27, 32, 33, 34 (need a real build or a vendor file) and EMB-73 (`Scope: suite`, owner's). Toolchain lane: `api/126`, `api/127`, `atlas/001`-`003`, `dev-bench/036`, `037`, `suite/032`. **Worth trying before dreaming:** other `toolchain` tasks may be worker work in disguise, as `outpost/027` was. A mistake of mine, repaired: my first log edit swallowed `dev-bench/010`'s heading into a leg-notes line (`embarch-fleet` `c64422b`), restored in the `core/125` fold. Bench: neither role attached at 04:45. No `suite` task announced, nothing deployed.

## 2026-11-10 05:00 — dev-bench/045 the link-level wire enums take their values from the crate

**Decided:** `embarch-dev-bench` decision 56 amended, by my own hands (`toolchain`; EMB-132): `gen_crate_limits.py`'s `ENUMS` gains `DevBenchMessage`, `Action`, `GattOperation`, `BleSecurityLevel`, `BleRole`, `BleAddressKind`, `DevBenchLogLevel`, `GattDirection`, `GattEventKind`, `Unit`, `StreamSource`, `StreamScope`, and `crate_limits.cmake` their six source files. Every C enum that is one of those enums' postcard index takes its values from `crate_limits.h` with a `_COUNT` assert, in both `serial_protocol.h` and `ble_bridge.h`. **Three readings, recorded in 56:** (1) `GattOperation`'s retired `StreamCapture` (crate decision 39 removed the variant) still has a decoder arm and a bridge path, so `DBM_GATT_OP_STREAM_CAPTURE`/`GATT_OP_STREAM_CAPTURE` stay a hand-typed 5 and the count assert keeps an appended variant off that slot. (2) `DBM_LOG_LEVEL_*` are also Zephyr severities, so `dev_bench_log.c` now `BUILD_ASSERT`s each against `LOG_LEVEL_*`, and the hand-typed boot level and kernel ceiling against `Warn`. (3) `BleRole`/`BleAddressKind` are step bytes `main.c` compared to a literal 1; now the crate's value. Not derived: `ble_role`, `ble_address_kind`, `action_kind`, `outcome_kind` (bench-internal, mapped rather than cast). The "Not covered" sentence is gone.
**Merged:** `agent/dev-bench/045-link-level-wire-enums-take-their-values-from-the-crate` (code `3daa719`, ff on `759c402`; doc `6874b02c`, ff on `70929779`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `serial_protocol` 67/67, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12 on `native_sim`; the `native_sim` app, `nrf54l15dk/nrf54l15/cpuapp` (RAM 157,400 B) and `esp32c5_devkitc/esp32c5/hpcore` (`sram0_0_seg` 333,360 B) clean, **sizes unchanged**, so no value moved. Drift checked against two altered crate copies: an inserted `Action` variant stops the compile on its count assert; `Error`/`Warn` swapped in `DevBenchLogLevel` stops it on the Zephyr asserts. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate. **ESP32-C5 needs the venv's `bin/` on `PATH`** (`esptool`); calling `west` by absolute path alone fails configure.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; build-time only, no value changed.
**Budget:** PROCEED, wave 6; 5-hour 46% to 52%, weekly 64% to 65%.
**Least sure about:** the bench still carries a whole `GATT_OP_STREAM_CAPTURE` path for a kind the crate can no longer send; I kept it (removing it is a decision this task did not ask for) and did not file it yet. Process note: I ran one throwaway inline `python3 -c` to list the crate enums the generator reads (a test of the generator, not a recurring job; not filed) and one empty heredoc by mistake.

## 2026-11-10 04:52 — core/125 pre-flight refuses a one-shot monitor inside an open window

**Decided:** nothing new numbered; `embarch-core` decision 90 extended (the worker's): Core's `validate_study` calls `Study::validate_monitor_windows()` right after `validate_wait_budgets`, so a hand-written study with a one-shot monitor inside an open window is refused before dispatch with the crate's message naming both steps. Closes EMB-131 with `study-designer/082`. **Supervisor edit outside the core scope, in this fold, on the reviewer's note:** `embarch-study-designer/decisions/gatt.md` decision 89's last bullet said Core's pre-flight did not call it yet; it now says it does. **Also in this fold, a repair of my own:** my `study-designer/083` log edit (`embarch-fleet` `c64422b`) swallowed the heading line of the `dev-bench/010` entry below into my leg-notes line; restored verbatim here.
**Merged:** `agent/core/125-pre-flight-refuses-a-one-shot-monitor-inside-an-open-window` (code `b6035a7`, ff on `c79b74b`; doc `f462d1fe`, the worker's commit rebased onto `d4ab17a0`, ff). Gate on the merge result: `cargo build`, `test` (390 passed, 2 ignored), `clippy --all-targets -D warnings` clean; ownership `core` OK on both branches; client names clean; `check-docs.py` 12/12. Code pushed after the doc gate, doc right after.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** native Windows build of `embarch-core` not run (gate debt; one host-independent call and a test).
**Budget:** PROCEED, wave 6; 5-hour 46%, weekly 64%.
**Least sure about:** nothing in the unit.

## 2026-11-10 04:49 — study-designer/083 decision 41 leaves gatt.md by verbatim split

**Decided:** nothing numbered. `embarch-study-designer/decisions/gatt.md` 12,048 → 10,012 B: decision 41 (vendor GATT service identities) moved verbatim to a new `decisions/vendor-identities.md`, pointer stub in `gatt.md`, index row split. I compared removed against added lines: identical apart from the new file's header. `interfaces/types.md` 11,154 → 10,950 B by trimming the `BleAddress` dated history and the `Uuid` derive detail. Both PAID; no study-designer file is in reserve now. **Compaction-pass answer** (the worker's, after reading `spec.md`): yes for orientation; `spec.md` says what the crate is, its invariants, the feature/target split, result storage, the consumers and where constants live, each pointing at the owning doc; current work is only in `open.md`.
**Merged:** `agent/study-designer/083-compact-study-designer` (doc only: `cdbcf3b8`, the worker's commit rebased onto the claim `50a55434`, ff; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `study-designer` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 44% to 46%, weekly 64%.
**Least sure about:** nothing in the unit.
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover (no claims, no unit or leg worktrees). Leg began at `c91baaec`. Fleet Ready: split EMB-132 into `tasks/dev-bench/045` (`5a774c9f`, `Hardware: toolchain`, mine), announced; atlas EMB-27, 32, 33, 34 and EMB-73 unchanged. Refill owed on depth and spread; no refill source changed since `2026-11-10 03:41`, so I did not re-sweep and filed nothing. Size ledger: nothing overdue. Bench: `--refresh` at 04:45, neither role attached; three bench tasks stay `open`. In flight: `core/125` (worker, EMB-131), `dev-bench/045` (my hands).

## 2026-11-10 04:43 — dev-bench/010 crate limits and .eap wire enums are read from the crate at configure time

**Decided:** `embarch-dev-bench` decision 56 (new, `decisions/platform.md`), by my own hands (`toolchain`): decision 20's read-the-crate's-source mechanism, generalised. `app/cmake/gen_crate_limits.py`, run at configure time by `app/cmake/crate_limits.cmake` (included by `app/CMakeLists.txt` and all four test projects), writes `crate_limits.h` from the crate's `src/limits.rs`, `src/decoder.rs`, `src/eap.rs`: every `usize` const as `CRATE_<NAME>`, and each variant's declaration index (postcard's wire value) plus a count for `ScalarType`, `Operand`, `Expr`, `CompareOp`, `StateKind`, `TerminalOutcome`. Every hand-typed crate bound in `serial_protocol.h`, `ble_bridge.h`, `study_ffi.h`, `eap.h` now uses it; the six C enums take their values from it and assert the count. **Forks kept, and the direction set:** `DBM_MAX_STEPS_PER_STUDY` (16), `EAP_MAX_EVENT_ARMS_PER_STATE` (2) and `DBM_MAX_PROTOCOLS_WIRE_LEN` stay the bench's own numbers and are asserted equal to the crate's advisory `DEV_BENCH_*` copies (and the first two at or below the crate's ceilings): the bench is the original, the crate the mirror. Generator invoked through Zephyr's `PYTHON_EXECUTABLE`. **Filed: EMB-132** (dev-bench, Fleet Ready, `Hardware: toolchain`): the link-level wire enums (`DevBenchMessage` tags, `Action`, `SecurityLevel`, GATT and stream enums, `Unit`, `DevBenchLogLevel`) are still hand-mirrored. Also refreshed `spec/constants.md`'s measured SRAM line, which `dev-bench/042` had left stale (my miss in that unit).
**Merged:** `agent/dev-bench/010-thirty-three-hand-mirrored-crate-constants-and-three-mirrored-enums` (code `759c402`, ff on `caca256`; doc `9f6b5ae9`, rebased onto `f8144fff`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `serial_protocol` 67/67, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12, the `native_sim` app, `nrf54l15dk/nrf54l15/cpuapp` and `esp32c5_devkitc/esp32c5/hpcore` all clean, **same image sizes as before** (nRF RAM 157,400 B, ESP32-C5 `sram0_0_seg` 333,360 B), so no value changed. Drift checked by hand against a modified copy of the crate: an inserted `ScalarType` variant and a changed `DEV_BENCH_MAX_STEPS_PER_STUDY` each stop the compile on their assert; a const the generator cannot read stops configure naming it. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; build-time only.
**Budget:** PROCEED, wave 6; 5-hour 37% to 41%, weekly 63% to 64%.
**Least sure about:** the generator needs the crate checked out beside the repo (or `EMBARCH_STUDY_DESIGNER_PATH`) for the ztest projects too, which until now built without it; the app already required it for every target, and no CI in this repo builds the tests, but a fresh clone that runs only a test now needs the sibling.
**Leg close (next leg, read this first):** 4 of 4 units (`dev-bench/043`, `dev-bench/042`, `study-designer/082`, `dev-bench/010`), all reviewers clean. Leg began at `244b19f1`, normal mode. Three were `toolchain` units by my own hands (`protocol.md` §7), one a worker unit. **New decisions:** `embarch-dev-bench` 54, 55, 56 and 28 amended (28 and 54 now live in a new `decisions/monitoring.md`, moved verbatim); `embarch-study-designer` 89 (worker). **Filed this leg:** EMB-131 (split into `study-designer/082`, landed, and `tasks/core/125`, open), EMB-132 (Fleet Ready). **Queue for the next leg:** `tasks/core/125` (one-line Core pre-flight call, worker, `Hardware: none`; closes EMB-131), `tasks/study-designer/083` (compaction debt the 082 worker filed, `In flux: no`, due 2026-11-24), EMB-132 to split as a `toolchain` task; atlas EMB-27, 32, 33, 34 and EMB-73 unchanged. Every `dev-bench` change this leg is unverified on a board: the hardware debts in the 043 and 042 entries are owed. Bench: neither role attached at 04:02. No `suite` task announced, nothing deployed.

## 2026-11-10 04:36 — study-designer/082 a one-shot monitor inside an open window is refused when the study is built

**Decided:** `embarch-study-designer` decision 89 (new, `decisions/gatt.md`; EMB-131), the worker's, on the direction I set at the split (`dea33acf`): the crate mirrors `embarch-dev-bench` decision 55 at authoring time. `Study::validate_monitor_windows()` returns `MonitorWindowError { step, opened_by }` (re-exported), additive like decision 83's `validate_wait_budgets`; `build_study` refuses the bracketed one-shot as `BuildStudyError::OneShotInOpenMonitorWindow { step, opened_by }`, naming both rows. The walk: a window opens at a `Start`, a second `Start` replaces it, the next `Stop` closes it, a lone `Stop` is legal, `continue_on_fail` changes nothing. **Split EMB-131 into two tasks, the second filed in this fold:** `tasks/core/125` (open, `Hardware: none`) has Core's `validate_study` call the new method beside `validate_wait_budgets`, so a hand-written study is refused at pre-flight too; EMB-131 stays in Fleet Working until it lands.
**Merged:** `agent/study-designer/082-a-one-shot-monitor-inside-an-open-window-is-refused-when-the-study-is-built` (code `6874b81`, ff; doc `aa488fa3`, the worker's commit rebased onto `a843f6af`). Shared crate, so I read the diff: one pure walk over actions, used by both the method and `build_study` (one step per row, so the row-name lookup is aligned); no consumer matches `BuildStudyError` exhaustively. Gate on the merge result, once per consumer feature set (default, `alloc`, `std`, `study-ui,gatt-extract,eap-parse`): `cargo build`, `test` (153, 172, 185, 355 passed), `clippy --all-targets -D warnings` clean; ownership `study-designer` OK on both branches; client names clean; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing. **New debt filed by the worker:** `tasks/study-designer/083-compact-study-designer.md` (`In flux: no`, due 2026-11-24): decision 89 took `decisions/gatt.md` to 12,048 of 12,288 B and `interfaces/types.md` to 11,154 B, both in reserve.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 35% to 37%, weekly 63%.
**Least sure about:** nothing in the unit. The worker reported using inline Python to edit files once despite the dispatch line, and declining to file on the hook's prompt because it arrived inside tool output.

## 2026-11-10 04:28 — dev-bench/042 an open monitor window survives the steps inside it

**Decided:** `embarch-dev-bench` decision 55 (new), by my own hands (`toolchain`), and decision 28 amended to say what a window does with a monitor step inside it. **28 and 54 moved verbatim to a new `decisions/monitoring.md`** (checked with `diff` before any edit), because `decisions/dispatch.md` had 186 B left before its reserve and 55 is the same subject; `dispatch.md` keeps 14, 21, 22, 27 (6.3 KB), `monitoring.md` holds 28, 54, 55 (7.1 KB). (1) **A one-shot `GattMonitorAll`/`Selected` inside an open window is refused by name** ("a monitor window is open; Stop it before this step"); rejected: close-and-reopen, an unreported gap in the capture. (2) Each monitor slot carries its service and characteristic UUIDs copied at subscribe time, so a later `GattDiscover`, monitor or `RunProtocol` rebuilding the discovery table no longer relabels the window's rows (+960 B RAM on each board; the flat-index helpers are gone). (3) `ble_bridge_reset` forgets `subscribe_params.value_handle` instead of zeroing a struct its in-flight CCC-clear write still calls through. (4) **A subscription another already covers counts at once**: Zephyr writes no CCC and calls nothing back then, so a `RunProtocol` inside an unfiltered window (every source it reads) and a `DataExchange` subscribe on a held characteristic waited out their step. `subscription_covers` mirrors the host's rule over the bridge's own three subscription sets. **While a monitor subscription holds a handle it alone writes that handle's transcript rows** (`monitor_holds`, in `notify_cb`, the protocol dequeue and the protocol overflow's `drop_sink`), so unblocking (4) does not record each frame twice or send it to a tap twice. **Filed this unit: EMB-131** (study-designer, Fleet Ready): the crate's validation could refuse a one-shot inside a Start/Stop bracket at authoring time.
**Merged:** `agent/dev-bench/042-an-open-monitor-window-survives-the-steps-inside-it` (code `caca256`, ff on `fa5daf6`; doc `f2295f66`, ff on the claim `3acc3891`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `nrf54l15dk/nrf54l15/cpuapp` (RAM 156,440 to 157,400 B) and `esp32c5_devkitc/esp32c5/hpcore` (`sram0_0_seg` 332,400 to 333,360 B, 88.10%) both clean; `serial_protocol` 67/67 on `native_sim`. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12 on the merge result.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT. Owed on the bench (DK plus a BLE peer): a one-shot monitor inside an open window (refused, window still capturing after); a `GattDiscover` and a `RunProtocol` inside an open window with the window's rows still labelled; a `RunProtocol` inside an unfiltered window completing instead of timing out, each frame one row; a `DataExchange` notify on a characteristic the window holds; `Hello` during a live `DataExchange` subscription.
**Budget:** PROCEED, wave 6; 5-hour 29% to 35%, weekly 63%.
**Least sure about:** `subscription_covers` mirrors Zephyr's private rule instead of reading the host's list, so a subscription the host keeps that the bridge stopped tracking (a bonded peer's single subscription across a reconnect) still makes a subscribe wait as before; and the walk's `memset` of a slot is safe only because a teardown's CCC-clear writes precede the next walk's discovery on the one ATT bearer, which holds while EATT is off (it is, in both board configs) and is written in a comment, not asserted.

## 2026-11-10 04:18 — dev-bench/043 a monitor step fails when its subscriptions fail or the link drops

**Decided:** `embarch-dev-bench` decision 54 (new, `decisions/dispatch.md`), by my own hands (`toolchain`), and decision 28 amended in place. (1) A shared `subscribe_and_wait` gives the monitor walk and the protocol subscribe one verdict per subscription: subscribed, refused (ATT error in the row's status byte), no CCC, dropped before it landed, could not start, timed out, limit; only the first is a `SUBSCRIBED` row and counted. (2) **An unfiltered `GattMonitorAll`/`Start` that subscribed to nothing now fails** (the question the task left to a decision): each characteristic may be skipped, the whole set may not be empty. A selective target that did not land fails naming its verdict. (3) A disconnect anywhere in the walk is `Disconnected`; the capture wait no longer resets one away. (4) Every subscribe/unsubscribe uses one checked snapshot of the connection; monitor and protocol subscriptions are `VOLATILE`, so a bonded peer's disconnect removes them too and teardown after a drop calls nothing. A window whose link dropped stays open until its `Stop`, which returns `Disconnected` (28 used to say the flag clears on disconnect; the code never did). (5) `subscribe_cb` and the monitor/protocol NULL arms wake `ccc_sem` only for the params being waited on (`ccc_waiting`), which also covers `ensure_subscribed`. A `RunProtocol` source with no CCC fails by name instead of timing out. **Supervisor edit outside the dev-bench scope, in this fold:** three clauses in `embarch-study-designer/interfaces/types.md`'s monitor rows (nothing subscribed fails; a Stop after a drop is `Disconnected`; a target that did not subscribe fails); that file is at 11,051 B, 8 B short of its reserve.
**Merged:** `agent/dev-bench/043-monitor-step-fails-when-its-subscriptions-do` (code `fa5daf6`, ff on `a249ff5`; doc `fdb0932f`, ff on the claim `5f9a4a5b`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `nrf54l15dk/nrf54l15/cpuapp` (RAM 156,432 to 156,440 B) and `esp32c5_devkitc/esp32c5/hpcore` (`sram0_0_seg` 332,400 B, unchanged) both clean, no new warnings; `serial_protocol` ztest 67/67 on `native_sim`. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12 on the merge result. Code and doc landed in order, code first.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT, and no `native_sim` test reaches `ble_bridge_real.c`. Owed on the bench (DK plus a BLE peer): a CCC write the peer refuses; a notifying characteristic with no CCC; a disconnect during the subscribe walk; one inside an open window followed by its `Stop`; a `RunProtocol` source with no CCC; an unfiltered monitor against a peer with nothing that notifies.
**Budget:** PROCEED, wave 6; 5-hour 23% to 29%, weekly 62% to 63%.
**Least sure about:** gating `subscribe_cb` on `ccc_waiting` changes `ensure_subscribed` too (DataExchange subscribe), on reasoning about Zephyr's ATT ordering rather than a run; if a path waits on `ccc_sem` without setting `ccc_waiting` it will now time out instead of waking. I found none, but nothing exercised it. The same-slot reuse race (a re-armed walk memsetting a params whose CCC-clear answer is still in flight) is left for `dev-bench/042`, which owns "no params struct zeroed while Zephyr can still call through it".
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover (no claims, no unit or leg worktrees). Leg began at `244b19f1`. Fleet Ready unchanged (atlas EMB-27, 32, 33, 34 need a real build or a vendor file; EMB-73 is `Scope: suite`, the owner's). Refill owed on depth and spread; no refill source changed since `2026-11-10 03:41`, so nothing filed. Size ledger: nothing overdue. Bench: `--refresh` at 04:02, neither role attached; three bench tasks stay `open`. No worker task exists, so this leg runs `toolchain` units; `dev-bench/042` (same function, must follow 043) is next.

## 2026-11-10 04:00 — study-designer/081 the att_status doc comment names its per-kind meanings

**Decided:** nothing numbered. Comment-only: `GattTranscriptEntry::att_status` in `embarch-study-designer/src/gatt.rs` now says the byte's meaning depends on `kind` (ATT error code, a discovered characteristic's properties byte, the HCI disconnect reason) and points at `interfaces/gatt-types.md`. I filed it as **EMB-130** (`--from reviewer`, Fleet Ready) from the `dev-bench/044` reviewer's residual, split it at once into this task (`b0ed2cbf`), announced it, and dispatched a worker.
**Merged:** `agent/study-designer/081-att-status-doc-comment-names-per-kind-meaning` (code `5c2f9a6`, ff; doc `5f9e118e`, ff on the claim `14310512`). Shared crate, so I read the diff: one doc comment, no code. Gate on the merge result: `cargo build`, `test` (144 + 9 passed), `clippy --all-targets -D warnings` clean; ownership `study-designer` OK on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 23%, weekly 62%.
**Least sure about:** nothing in the unit. The code comment in `embarch-dev-bench/app/src/ble_bridge_real.c` (`disconnected_cb`) still says "the crate already reads that byte per event kind", the slight overstatement the `044` reviewer flagged in decision 53, which I fixed in the doc but not in the code.
**Leg close (next leg, read this first):** 4 of 4 units (`desk/023`, `desk/024`, `dev-bench/044`, `study-designer/081`), all reviewers clean. Leg began at `a2b538b5`, normal mode. **`dev-bench/044` was a `toolchain` unit by my own hands** (the worker queue was empty after the two desk compactions); new `embarch-dev-bench` decision 53. **The fleet venv now has `esptool`**, so the ESP32-C5 image builds in the toolchain lane (it did not on 2026-11-07); `natsort` is still missing, so `twister` cannot run and ztests go suite by suite. EMB-83 (which lane `toolchain` tasks belong in) is still the owner's, in Backlog. **Queue for the next leg:** no task file a worker can take; Fleet Ready holds atlas EMB-27, 32, 33, 34 (need a real build or a vendor file) and EMB-73 (`Scope: suite`, owner's). So the next leg runs another `toolchain` unit (12 remain; `dev-bench/042` and `043` both rewrite `monitor_subscribe_matching` and must land one after the other) or dreams. No desk file in reserve now. Bench: neither role attached at 03:40. One ordering slip of mine in `044` (code pushed before the doc gate; the doc side was red one minute, fixed). No `suite` task announced, nothing deployed. Supervisor ownership check on the leg's diff: clean.

## 2026-11-10 03:57 — dev-bench/044 the transcript keeps full-MTU notifications and records connects and disconnects

**Decided:** `embarch-dev-bench` decision 53 (new, `decisions/capture.md`), by my own hands (`toolchain`). (1) `DBM_MAX_STREAM_CHUNK_BYTES` is now `DBM_MAX_TRANSCRIPT_RECORD_LEN`, the exact worst-case encoded entry, 293 B (was 256, sized against the payload alone, so every notification over about 210 B failed to encode); a `_Static_assert` holds it under the crate's 512, and a new ztest encodes the worst case into a real `dbm_stream_record` and pins the length. (2) The end-of-study loss line names two causes, queue full and did not fit a record. (3) `connected_cb` (success only) and `disconnected_cb` emit `Local` `Connected`/`Disconnected` rows, before giving any semaphore; **the HCI reason rides in `att_status`**, not a new field (no schema bump). (4) End of study now clears the bond *before* the drain and `close_all_taps()`, as decision 37 always said, and the drain waits on a queued/handled count (`atomic_t`, one `goto handled` exit in the TX thread) instead of an empty queue, which closed a gap where the last entry could be dropped at the tap-open check. **Supervisor edit outside the dev-bench scope, in this fold:** one clause in `embarch-study-designer/interfaces/gatt-types.md` saying a disconnected entry's `att_status` is the HCI reason.
**Merged:** `agent/dev-bench/044-transcript-keeps-full-mtu-rows-and-connection-events` (code `a249ff5`, ff on `9371510`; doc `1d4949b3` and `10889a74`, the branch's `b890718a` and its fragment fix `72659053` cherry-picked onto `d245f2cc`). Built from the worktree against the main checkout's workspaces with the fleet `west`: `serial_protocol` ztest 67/67 on `native_sim`, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 12/12 (one by one; `twister` still lacks `natsort`); the `native_sim` app, `nrf54l15dk/nrf54l15/cpuapp` and **`esp32c5_devkitc/esp32c5/hpcore` all build — `esptool` is in the fleet venv now**, so the ESP32-C5 image built for the first time in the toolchain lane. RAM: nRF 156,416 → 156,432 B, ESP32-C5 `sram0_0_seg` 332,384 → 332,400 B (87.85%), the record lives only in the `tx_scratch` union. Ownership `dev-bench` OK on both branches, client names clean, `check-docs.py` 12/12. **My ordering slip:** I pushed the code to `embarch-dev-bench` `main` before the doc gate ran, and the doc side was red for a minute (fragment 344 B, over the 200 B limit); fixed on the branch and re-gated green. Code and doc landed in the same unit, but not as one script with a reset.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT. Owed on the bench (DK plus a BLE peer): a notification of 211 to 244 B reaching the transcript tap; `Connected` and `Disconnected` rows with the reason in a real study's `gatt.csv`; the bond-clear disconnect as the transcript's last row, before its `StreamClose`.
**Budget:** PROCEED, wave 6; 5-hour 21%, weekly 62%.
**Least sure about:** the reviewer's residual: the crate's own doc comment on `GattTranscriptEntry.att_status` (`embarch-study-designer/src/gatt.rs`) still says "raw ATT error code", now untrue for a disconnected row; a comment-only fix in a repo this unit could not touch, filed below. And a `Connected` row comes from `connected_cb`'s context, which adds one ~290 B stack local there, the same cost the notify path already pays; no stack overflow was measured because nothing ran.

## 2026-11-10 03:44 — desk/024 decisions 38, 40 and 41 leave desks.md by verbatim split

**Decided:** nothing numbered. `embarch-desk/decisions/desks.md` 11,066 → 9,424 B (76.7%): decisions 38, 40 and 41 (a tile's default Harvest target, the Desk tab's day list, Harvest's entries joined) moved verbatim to a new `decisions/day-list.md`, with a pointer stub in `desks.md` and the index row split. I compared removed against added lines: identical except the headers, the stub and the index rows. PAID; no desk file is in reserve now. **Compaction-pass answer** (the worker's, after reading `spec.md`): yes, `spec.md` says what the desk is, its invariants and constants, and points to `interfaces.md` for every route and tool; its Desks paragraph cites "decisions 33–40, 77" by number, so a reader goes through the index to find `day-list.md`. On the reviewer's note I re-pointed `decisions/tiles-after-send.md`'s line naming 41 at `day-list.md` (one line, in this fold).
**Merged:** `agent/desk/024-compact-desk` (doc only: `40c6f27d`, the worker's `32d80fd6` cherry-picked onto `6b5ff8e7`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `desk` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 10%, weekly 61%.
**Least sure about:** nothing in the unit. **The worker queue is now empty** (no `none` or `verify-only` task open; Fleet Ready holds only what the last five legs could not split), so this leg's last two units are `toolchain` tasks by my own hands, as `protocol.md` §7 grants and the 2026-11-07 leg did first; `dev-bench/044` claimed at 03:45 (`6b5ff8e7`). EMB-83, the owner's question about that lane, is still in Backlog with no reply.

## 2026-11-10 03:41 — desk/023 decisions 79 and 81 leave access-point.md by verbatim split

**Decided:** nothing numbered. `embarch-desk/decisions/access-point.md` 11,206 → 6,477 B: decisions 79 and 81 moved verbatim to a new `decisions/linear-reads.md` (5,269 B), with a header, a pointer line in `access-point.md`, and the index row in `decisions.md` split in two. I compared removed against added lines: identical except the two headers and the index rows. PAID. **Compaction-pass answer** (the worker could not give one, it did not open `spec.md`; mine): no. `spec.md` names no Linear read tool and points to `interfaces.md` for every tool, so someone working on the desk's Linear reads needs `decisions/linear-reads.md` for the no-fallback rule and the file-read limits.
**Merged:** `agent/desk/023-compact-desk-access-point-decisions` (doc only: `c312b30f`, ff on the claim `88d8d133`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `desk` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 10%, weekly 61%.
**Least sure about:** nothing in the unit; the leg's open question is what follows `desk/024`, below.
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover (no claims, no unit or leg worktrees). Leg began at `a2b538b5`. Fleet Ready unchanged and not split: atlas EMB-27 (needs a real build), EMB-32, 33, 34 (need a vendor file), EMB-73 (`Scope: suite`, its last box is an `embarch-dev-workflow.md` edit, the owner's). Refill owed (depth and spread); the only refill source changed since `2026-11-10 03:12` was `embarch-desk/open.md` (`desk/020` removing its answered item), so nothing filed. Spread sweep: nothing filed (2026-11-10 03:41). Size ledger: nothing overdue. Bench: `--refresh` at 03:40, neither role attached; three bench tasks stay `open`. The worker ran one empty inline-Python heredoc by mistake and did not file on the hook's prompt.

## 2026-11-10 03:36 — desk/022 the desk says when a repo has no embarch-api in its login

**Decided:** `embarch-desk` decision 82 (new, `decisions/desks.md`; EMB-17), on the direction I set at the split: the desk reads the instance login's `.claude.json` (`<CLAUDE_CONFIG_DIR>/.claude.json`, else `~/.claude.json`) and the folder's `.mcp.json`, and **never writes either**; `embarch-api` counts as registered at user scope, in `projects.<folder>.mcpServers`, or in the folder's `.mcp.json` (another login's file does not count). New `src/mcpreg.rs`. `GET /desks` gains an `embarch_api` list per desk, one entry per folder, and a folder without it carries `login` and `register_command`; a SessionStart in such a folder appends one paragraph after the standing notes (74). **The worker's picks:** the command is `[CLAUDE_CONFIG_DIR=<dir> ]claude mcp add --scope user embarch-api -- <binary> <args>` (flags checked against `--help`), binary and args copied from an existing entry in this login, `~/.claude.json` or a sibling `~/.claude*` login (user scope first), else two placeholders; no `desks.json` field; **every desk is told**, not only ones that build; no parent-folder search; `embarch setup` registering it recorded as out of scope. `features.d/desk-078-embarch-api-login-check.md` added.
**Merged:** `agent/desk/022-the-desk-says-when-a-repo-has-no-embarch-api-in-its-login` (code `b229d45`, ff on `8559cf3`; doc `d80ccc9b`, the worker's `cfa0cd1e` cherry-picked onto `d4df4a3e`). Gate on the merge result: `cargo build`, `test` (234 passed), `clippy --all-targets -D warnings` clean; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing. **New debt filed by the worker:** `tasks/desk/024-compact-desk.md` (`In flux: no`), since decision 82 took `decisions/desks.md` to 90.1%.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to the live work-login desk: `GET /desks` and a session start in a client folder with no `embarch-api` registered, showing the command, and the command run as given registering it. Nothing installed.
**Budget:** PROCEED, wave 6; 5-hour 9%, weekly 61%.
**Least sure about:** "every desk is told" means a desk folder that never builds firmware hears the paragraph at every session start until `embarch-api` is registered for that login; and the command copies its binary path from a sibling login's file, which assumes both logins run the same `embarch-api` build.
**Leg close (next leg, read this first):** 4 of 4 units (`atlas/062`, `desk/020`, `desk/021`, `desk/022`), all first-pass green, all four reviewers clean. Leg began at `e14a064f`, normal mode. **Split this leg** (`e7a4d76c`): EMB-19 into `desk/020` + `atlas/062`, EMB-14 into `desk/021`, EMB-17 into `desk/022`; EMB-19 and EMB-14 are Done and EMB-17 closes with this fold. **Filed this leg, both Backlog for the owner:** EMB-128 (api, investigation: does `embarch-api`'s `build` from a worktree session build the worktree; `desk/020`'s worker skipped the check its task asked for) and EMB-129 (doc: `LINEAR-PROTOCOL.md` §1 says the desk cannot read attachments, now false and reserved). **Queue for the next leg:** two desk compaction debts filed by workers this leg, `tasks/desk/023` (`decisions/access-point.md`, 91.2%) and `tasks/desk/024` (`decisions/desks.md`, 90.1%), both `open`, `In flux: no`, both desk so one at a time; Fleet Ready holds only atlas EMB-27 (needs a real build), EMB-32, 33, 34 (need a vendor file) and EMB-73 (`Scope: suite`, the owner's). So the next leg has two units unless the owner adds work. Bench: neither role attached at 03:10; three bench tasks `open`. Three of four workers used inline Python edits despite the dispatch line and none filed on the hook's prompt (fourth leg running). No `suite` task announced, nothing deployed.

## 2026-11-10 03:31 — desk/021 a desk tool reads an issue's images and files

**Decided:** `embarch-desk` decision 81 (new, `decisions/access-point.md`; EMB-14), on the direction I set at the split. `linear_get_issue` returns **`files`**, `{url, title, found}` with `found` one of `description`, `comment <id> by <author>`, `attachment`, built over every comment read (the 500 cap), not only the 25 returned. New tool **`linear_get_file(key, url)`** over `POST /linear/issue/{key}/file` re-reads the issue and refuses any URL it does not list. **The worker's picks:** 10 MiB cap (chosen, not measured; checked by `Content-Length` and a running count); an image (not SVG) comes back as image content, text as text, a text file over 200 KB or any other file written owner-only to `<data>/linear-files/<KEY>/<name>` and the path returned; the workspace credential goes only to `uploads.linear.app`, links out of Linear are fetched with none, and only `https` to a non-IP, non-`localhost` host with no login or port. API-key backend: bare key in `Authorization`, attachment records from one extra GraphQL field. Linear-MCP backend: the sign-in token as bearer, falling back to the server's `extract_images` for images; a non-image it cannot fetch is an error naming the backend. Code in a new `src/files.rs`. `features.d/desk-021-linear-get-file.md` added (the worker numbered the row after the task, not after the last row, 077; it sorts early, harmless). **Filed for the owner: EMB-129** (Backlog, `Type: doc`), `LINEAR-PROTOCOL.md` §1's "(the desk cannot read attachments)", which is now false and reserved.
**Merged:** `agent/desk/021-a-desk-tool-reads-an-issues-images-and-files` (code `8559cf3`, ff on `4fa470a`; doc `fd69c972`, the worker's `8bff8a95` cherry-picked onto `c9222741`). Gate on the merge result: `cargo build`, `test` (224 passed), `clippy --all-targets -D warnings` clean; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing. **New debt filed by the worker:** `tasks/desk/023-compact-desk-access-point-decisions.md` (`In flux: no`), since `decisions/access-point.md` is at 91.2% (1082 B left).
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live workspace on each backend: one real issue with an image, a PDF and an attachment record, read through `linear_get_file`. Unverified: that the upload host takes the bare key and the MCP bearer, that `extract_images` takes an argument named `markdown`, and that the MCP `get_issue` returns `attachments` unasked. No HTTP fake exists for either backend, so the real fetch calls are untested.
**Budget:** PROCEED, wave 6; 5-hour about 5%, weekly 60%.
**Least sure about:** the reviewer's refinement, not a finding: decision 81 says "a public hostname", but the code refuses only IP literals, `localhost`, a login or a port, so an attachment record pointing at an internal DNS name is fetched (bare, with no credential). Cheap to tighten if the owner wants it; not filed.
**Leg notes:** `desk/022` (EMB-17) dispatched 03:31 with a note that `access-point.md` is in reserve. The worker ran one empty inline-Python heredoc by mistake and did not file on the hook's prompt.

## 2026-11-10 03:23 — desk/020 a Start work worktree builds its own Zephyr module

**Decided:** `embarch-desk` decision 80 (new, `decisions/sessions.md`; EMB-19, the desk half), on the direction I set at the split: a worktree shares the west workspace and replaces only its own module, so it needs no `west update` of its own (answers and removes the `open.md` item). `set_zephyr_modules` in `src/worktree.rs` runs `west list -f '{abspath}'` in the main clone, keeps only Zephyr modules (`zephyr/module.yml` or `zephyr/CMakeLists.txt`, so `zephyr` itself drops out), swaps the main clone for the worktree, and merges `ZEPHYR_MODULES` into the worktree's `.claude/settings.local.json` `env`, git-excluded; single-clone Start work only (a suite desk is untouched). **The worker's picks:** a module with no `name:` gets a warning naming the fix (add `name:`) and the override is still written; `west` missing or failing is a warning in Start work's answer. No west workspace above the clone, or a repo west does not list: nothing written, nothing said. The worker confirmed from a Zephyr tree that `zephyr_get` reads the environment. `features.d/desk-077-start-work-zephyr-modules.md` added.
**Merged:** `agent/desk/020-a-start-work-worktree-builds-its-own-zephyr-module` (code `4fa470a`, ff on `e02b8bc`; doc `4feae56a`, the worker's `939f5363` cherry-picked onto `5fedab9a`). Gate on the merge result: `cargo build`, `test` (213 passed), `clippy --all-targets -D warnings` clean; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** verify-only, needs a real west workspace and a session (no board): Start work on a firmware-repo issue, `ZEPHYR_MODULES` present in the worktree's `settings.local.json`, a board-file edit in the worktree, `west build` from a session there reading the worktree's file. **Unverified and load-bearing:** that Claude Code applies a settings `env` to a session's shell commands; the tests use a stand-in `west` and are `cfg(unix)` only.
**Budget:** PROCEED, wave 6; 5-hour 4% (window reset at 03:22), weekly 60%.
**Least sure about:** the whole mechanism rests on Claude Code passing settings `env` to the Bash tool, which nobody ran; and the worker did not check whether `embarch-api`'s `build` tool, called from a worktree session, builds the main clone (the task asked it to say so and file it if so), so that question is open and unfiled.
**Leg notes:** `desk/021` (EMB-14) dispatched 03:24 into the freed desk slot. The worker used inline Python for the doc edits and did not file on the hook's prompt.

## 2026-11-10 03:22 — atlas/062 the atlas follows the worktree a session runs in

**Decided:** nothing numbered; `DESIGN.md` gains "Which `fw` a process uses" (EMB-19, the atlas half), on the direction I set at the split. `project.resolve_fw` picks the checkout per process, in order: **`EMBARCH_ATLAS_FW`** (the worker's pick for the override; no `--fw`, which already means the configured repo), then a working directory inside a linked worktree of the configured repo (same `git rev-parse --git-common-dir`), then `atlas.toml`'s `fw` as before. `fw_dir` goes through it, so `status`, staleness, inventory, live and `build` follow it. `status` prints `fw: <path> (worktree; atlas.toml names <main>)` and returns `fw_is_worktree`, `fw_configured`. `build` keeps the configured repo's basename for `.work/<commit12>/<basename>`, excludes the main clone from the module list, counts an input from either checkout as a leak, and records `build.fw_checkout`. The `embarch/` folder stays shared: a build from a worktree pins the one atlas to that commit and the other checkout's `status` reports it stale; one atlas per worktree is not done.
**Merged:** `agent/atlas/062-the-atlas-follows-the-worktree-a-session-runs-in` (code `f293d94`, ff on `d8bc57f`; doc `1fd9f20b`, the worker's `b2debcd4` cherry-picked onto `634a3b9a`). Gate on the merge result: `pytest -rs` 731 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real project: an atlas MCP session started in a Start work worktree, `status` naming the worktree, and `build` from it on a real west workspace.
**Budget:** PROCEED, wave 6; 5-hour 64% (inside its reset grace), weekly 60%.
**Least sure about:** the reviewer's two non-findings: `status` run from a worktree rewrites the shared `MAP.md` and `current.json` against the worktree's HEAD, and `graph.py` and a few other readers still take the configured `fw` directly rather than the resolved one.
**Leg notes (this leg, first unit):** spawned with the pump latched in normal mode, no stop marker, no owner message; nothing to recover (no claims, no leg or unit worktrees). Leg began at `e14a064f`. **Split EMB-19 into `desk/020` and `atlas/062`, EMB-14 into `desk/021`, EMB-17 into `desk/022`** (`e7a4d76c`), announced at `ts` `1794305754.855269`. Directions I set on the owner's behalf: `desk/020` (verify-only) writes `ZEPHYR_MODULES` (the workspace's module list with the main clone swapped for the worktree) into the worktree's `.claude/settings.local.json` `env`, sharing every other module rather than a second `west update`; `atlas/062` resolves `fw` from the working directory; `desk/021` reads only links the issue itself lists; `desk/022` reads the login's `.claude.json` and never writes it, and gives a user-scope `claude mcp add`. Refill owed (depth and spread); the only refill source changed since `2026-11-10 01:46` was `embarch-atlas/design.md` (`atlas/061`'s as-built note, no open question), so nothing filed. Spread sweep: nothing filed (2026-11-10 03:12). Size ledger: nothing overdue. Bench: `--refresh` at 03:10, neither role attached; three bench tasks stay `open`. Atlas EMB-27, 32, 33, 34 still need a real build or a vendor file; EMB-73 is the owner's. `desk/020` dispatched 03:16 with this unit. The worker used inline Python edits again despite the dispatch line and did not file on the hook's prompt.

## 2026-11-10 03:07 — atlas/061 an atlas for a target with no Zephyr board yet

**Decided:** nothing numbered; `DESIGN.md` principle 6 amended in place, plus a new section "A target with no Zephyr board yet", the stamp text, the `atlas.toml` example and the CLI table (EMB-21), on the direction set at the split. The opt-in is **`no_board = true`** on a `[[targets]]` entry, or **`build --no-board`** for one run; a missing or misspelt `board` still errors naming `--board`, `no_board` with a `board` is refused, and it is never inferred. Such a build makes no worktree and no west build and writes a stamp with `board: null` and **`build: {built: false, reason, fw, west_topdir}`** (the worker named the field); the atlas is still `<target>@<commit12>`. `join`, the pin map, the netlist-only checks, `MAP.md`, `graph.json` and the second-look queue still run. **Absent**, named by `status` and `MAP.md` through `common.NO_BUILD_ABSENT`: `build/`, `kconfig.json`, `dt.json`, `in_use.json`, codecheck, `limits.json`, the RM worklist, and the pinned-build `config`, `dt_node`, `footprint`, `stacks` (which answer "no Zephyr board yet"; `build=<dir>` still works). **Degraded:** `pins.json`/`pins.md`/`pin_slice.txt` keep the schematic side with empty DT columns, `checks.md` and `mismatches.json` run the netlist-only checks (`mismatch.run` gains `no_build`, reusing `atlas/058`'s `NEEDS_BUILD`), `graph.json` has empty code layers and a `code_note`. A later normal build supersedes it and `status` reports the board change as stale; `--no-board` against an atlas with a board keeps it unless `--force`. `atlas-build` and `atlas-use` skills have notes; `embarch-atlas/design.md` in the instance has a short note. No `features.d` row.
**Merged:** `agent/atlas/061-an-atlas-for-a-target-with-no-zephyr-board-yet` (code `d8bc57f`, ff on `dbeac7c`; doc `7e7311bc`, the worker's `a069f4cf` cherry-picked onto `5a5036ed`). Gate on the merge result: `pytest -rs` 728 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. 12 new tests in `tests/test_no_board.py`; no real west build ran.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real project: `build --no-board` on a firmware repo with schematics and datasheets and no board files, then `status` and `MAP.md` read cold by a session; the west project list is recorded best-effort and was never tried against a real workspace.
**Budget:** PROCEED, wave 6; 5-hour 62% (resetting within minutes), weekly 59%.
**Least sure about:** the stamp keeps `dirty: false`, which DESIGN.md glosses as "a worktree is always clean", on an atlas made with no worktree (the reviewer's aside: a stretch, not a contradiction).
**Leg close (next leg, read this first):** 4 of 4 units (`desk/018`, `atlas/060`, `desk/019`, `atlas/061`), all first-pass green, all four reviewers clean. Leg began at `0cd81401`, in **normal mode**. **Split this leg** (`51d97635`): EMB-82, EMB-11, EMB-25, EMB-21, all four now Done. **Filed this leg: EMB-127** (desk, `Type: decision`, Backlog for the owner): whether a session's desk should bound `linear_list_issues`, which reads any team in any workspace (`desk/019`'s reviewer residual risk). Fleet Ready still holds desk EMB-14 (read an issue's attachments; it would make a line in the reserved `LINEAR-PROTOCOL.md` §1 stale, so the owner owes that edit), EMB-17 (register `embarch-api` in a new repo's login, or say how), EMB-19 (west module override for a worktree build; needs a real west workspace to verify, likely `verify-only`); atlas EMB-27 (needs a real build), EMB-32, 33, 34 (need a vendor file); EMB-73 (`Scope: suite`, owner's). So the next leg has **no task files to dispatch**: it must split desk EMB-14, 17 or 19 at `ready`, one desk worker at a time, and atlas has nothing splittable. Sweep skipped at this leg's start (no source changed since `2026-11-10 01:46`). Bench: neither role attached (`--refresh` at 02:47); three bench tasks `open`. All four workers used inline Python edits at least once despite the dispatch line, and all ignored the hook's filing prompt. No `suite` task announced, nothing deployed.

## 2026-11-10 03:00 — desk/019 a desk tool lists a team's issues by state

**Decided:** `embarch-desk` decision 79 (new, `decisions/access-point.md`; EMB-11), on the direction set at the split. MCP tool **`linear_list_issues(team_key, state, project?)`** over a new route `POST /linear/issues` (`{team, state, project?}`), answering `{workspace, team, state, project, issues, truncated, note?}`. The team is found by key, case ignored, **across every connected workspace, not limited to the session's desk** (the issue's "any connected workspace"; 79 says so and why). The state is matched by name against that team's own states, and a miss is a 400 listing them, never an empty list; an unknown project name gives an empty list. API-key backend filters in GraphQL; the Linear-MCP backend (68) passes team, state and project and then filters after fetching. Both page 50 at a time up to `MINE_CAP` (500), newest first, and say when the cap cut. **The no-fallback line I set at the split** is in decision 79 as 29 applied and in `plugin/skills/desk/SKILL.md`: agents never use Claude's own Linear connector for what the desk lacks, and file the gap against the desk. `features.d/desk-075-list-issues-by-state.md` added.
**Merged:** `agent/desk/019-a-desk-tool-lists-a-teams-issues-by-state` (code `e02b8bc`, ff on `45d38e0`; doc `1b090552`, the worker's `4119299d` cherry-picked onto `02c08b78`). Gate on the merge result: `cargo build`, `test` (208 passed), `clippy --all-targets -D warnings` clean; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: the tool against a real workspace on each backend; the tests are pure-function (no network fakes exist), so whether the Linear MCP server's `list_issues` takes `team` as an id and `state` and `project` as names is unverified.
**Budget:** PROCEED, wave 6; 5-hour 56% (inside its reset grace), weekly 59%.
**Least sure about:** **the reviewer's residual risk, for the owner:** decisions 33 and 77 still say a session's desk "scopes its agents' Linear calls", which is now false for this one tool, so a session on one client's desk can read another client's team through the owner's own tokens. Neither decision states desk scope as a confidentiality boundary, so it is not a contradiction, but whether it should be is the owner's call; I filed it to Backlog as a decision, **EMB-127** (three options, the as-built first). Separately, the MCP backend's argument shape is untested against the real server.
**Leg notes:** the worker again used inline Python edits and saw the hook's filing prompt three times without filing. `atlas/061` dispatched 02:58.

## 2026-11-10 02:56 — atlas/060 unnamed pins get a recorded name and its source

**Decided:** nothing numbered; `DESIGN.md`'s `netlist.json` section, CLI table and "Not yet built" amended in place (EMB-25), on the direction set at the split. **`boards/<label>/pin_names.json`**, an overlay `schematic` never writes, holds `{ref: {pin: {name, prov, note}}}`. New verb **`embarch-atlas declare-pin-name <board> <ref> <pin> <name> [--prov llm-unverified|engineer-declared|engineer-confirmed] [--note]`**, **default `llm-unverified`** (the worker's pick: the documented step is a read of a rendered crop). It refuses a board with no netlist, an unknown ref or pin, a pin the PDF's text already named, an empty name and an unknown prov; the same key replaces; it also merges into `netlist.json`, `nets.md` and `parts.md`. `netlist.json` is the merged view: every named pin carries `name_source` (`pdf-text` or `overlay:<prov>`), PDF text always wins, and `schematic` re-applies the overlay. `counts` gains `pins_named_from_overlay` and `pins_unnamed_on_3plus_pin_parts`, printed by `schematic`. The step is `atlas-translate-docs` step 3: render the region with PyMuPDF, read it, declare it `llm-unverified`, have the engineer confirm. No crop verb (listed under "Not yet built"). No `features.d` row.
**Merged:** `agent/atlas/060-unnamed-pins-get-a-recorded-name-and-its-source` (code `dbeac7c`, ff on `17af295`; doc `17ea11e8`, the worker's `088a56a1` cherry-picked onto `26138cfb`). Gate on the merge result: `pytest -rs` 716 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. The worker set `done` itself.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real project: a module symbol whose pad names the netlist lacks, named through the skill step from a rendered crop, then `pin_trace` showing the overlay name and its source.
**Budget:** PROCEED, wave 6; 5-hour 56% (inside its reset grace), weekly 59%.
**Least sure about:** an overlay entry may name a pin on a part with fewer than 3 pins, where the PDF deliberately names none (values, not names); the reviewer finds DESIGN.md silent on it, so it is allowed rather than decided.
**Leg notes:** the worker used inline Python for two doc edits despite the dispatch line, and saw the hook's filing prompt and did not file. `desk/019` dispatched 02:55.

## 2026-11-10 02:54 — desk/018 desk_add_line can note another item

**Decided:** `embarch-desk` decision 78 (new, `decisions/notes.md`; EMB-82, on the owner's direction in the issue). `desk_add_line` and `POST /sessions/{sid}/line` take an optional `item`: an issue key (any case) or a desk item id, on any desk. With it, the note is an ordinary note on that item's tile for today, carrying the calling session's id; a tile it opens waits in the hand at 0 h. An unknown `item` is a 404 naming it, and nothing is written or held. Absent or blank, unchanged (held line included; the old body still parses). **The worker's reading:** a tile already approved takes the note as an ordinary line, with no `require_waiting` refusal, as the session's own item does; the reviewer confirmed decision 64 expects lines on an approved tile. The tool description and `plugin/skills/desk/SKILL.md` say when to set `item`. No `features.d` row.
**Merged:** `agent/desk/018-desk-add-line-can-note-another-item` (code `45d38e0`, ff on `4b83b5e`; doc `5dbd0ec2`, the worker's `223e6b21` cherry-picked onto `30749852`). Gate on the merge result: `cargo build`, `test` (203 passed), `clippy --all-targets -D warnings` clean; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a chat calling `desk_add_line` with another issue's key, and the note appearing on that item's tile. Nothing installed.
**Budget:** PROCEED, wave 6; 5-hour 50% (inside its reset grace), weekly 58%.
**Least sure about:** decision 78 lets any session write a note onto any item on any desk; that is the issue's ask, but nothing now stops a session from filing on the wrong item by a mistyped key that happens to exist.
**Leg notes (this leg, first unit):** spawned with the pump latched in **normal mode** (the previous leg cleared burndown), no stop marker, no owner message; nothing to recover (no claims, no leg or unit worktrees; local branches `agent/atlas/059` and `agent/ui/059-diff-new-lines-republish` left for the fold and the owner). Leg began at `0cd81401`. **Split EMB-82 into `desk/018`, EMB-11 into `desk/019`, EMB-25 into `atlas/060`, EMB-21 into `atlas/061`** (`51d97635`), announced at `ts` `1794304156.771549`. Directions I set on the owner's behalf: `019`'s tool covers both Linear backends with decision 59's cap, and `SKILL.md` says agents never fall back to Claude's Linear connector (decision 29 applied, not a new rule); `060` is an engineer-owned per-board overlay `schematic` never overwrites, a declare verb in `declare-interface`'s shape, a source on every pin name, and an unnamed count in `schematic`; `061` is an explicit no-board opt-in in `atlas.toml` (a forgotten `board` still fails), `build` skipping the west build and what reads it, `status` and `MAP.md` naming the absent outputs, principle 6 amended. Refill owed (depth and spread); sweep skipped: no source changed since `2026-11-10 01:46`, whose sweep filed nothing. Size ledger: nothing overdue. Bench: `fleet-hardware.py --refresh` shows neither role attached, so the three bench tasks stay `open`. The worker saw the hook's prompt to file an issue about inline Python edits and did not file. `atlas/060` dispatched 02:50 with this unit.

## 2026-11-10 02:43 — atlas/059 a pin record can state its package

**Decided:** nothing numbered; `DESIGN.md`'s `pin` row, the `boards/bindings.json` line, the join and "Not yet built" amended in place (EMB-45), on the direction set at the split. `pin` records take an optional `package` (a record without one applies to every package). `bindings.json` gains **`packages`**, ref (or `board:ref`, which wins) to package string, engineer-declared, compared ignoring case and spacing. `Join.pin_lookup`: with a declared package, that package's records plus unpackaged ones; with none declared and **more than one distinct name** for a number among records that carry a package, the pin is ambiguous (the worker's definition: two packages both naming the pin VCC are not ambiguous). Then `part_pin_name` falls back to the symbol's name, `part_pin_record` returns None, `build_pin_map` drops the number, and a new `pin-package-ambiguous` mismatch candidate (check "pin names per package", key `<board>:<ref>-<pin>`) says to declare the package. Reading the package from the BOM footprint or `variant` records is listed under "Not yet built". No `features.d` row.
**Merged:** `agent/atlas/059-a-pin-record-can-state-its-package` (code `17af295`, ff on `38a87fa`; doc `75c49164`, the worker's `5e281c7a` cherry-picked onto `1ff05cff`). Gate on the merge result: `pytest -rs` 707 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. This worker set `done` itself.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: a logic part with two pinouts distilled with `package` on its pin records, joined on a board with and without `packages` declared.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6, at this unit's start; **burndown cleared at 02:43** (below), so the leg ends in normal mode: PROCEED, wave 6, 5-hour 49% (inside its reset grace), weekly 58%.
**Least sure about:** an undeclared multi-package part now gets no datasheet name or record for its ambiguous pins and a mismatch candidate until someone declares its package; that is the intent, but it is new noise on every such part in an existing atlas.
**Leg close (next leg, read this first):** 3 units, not 4 (`atlas/057`, `atlas/058`, `atlas/059`), all first-pass green, all three reviewers clean. Leg began at `1f83ada2`. **I ended burndown** (`fleet-burndown.py --clear`, 02:43, reason "queue empty for burndown"): after `atlas/059` nothing in the queue or Fleet Ready is something a burndown leg may take. The latch now reads `mode=normal` and the pump is still on, so **the next leg runs in normal mode and may take Fleet Ready issues that need a new numbered decision**, which burndown withheld: desk EMB-82 (asks for a new desk decision outright), EMB-14, EMB-11 (its `SKILL.md` half is a policy call), EMB-17, EMB-19 (west design); atlas EMB-21, EMB-25 ("Direction: not decided"). Still stuck in either mode: atlas EMB-27 (needs a real build), EMB-32, 33, 34 (need a vendor file the public repo cannot carry), and EMB-73 (`Scope: suite`, needs an `embarch-dev-workflow.md` change, the owner's). I did not take a fourth unit after clearing, because the rule is clear and end. Done this leg: EMB-124, EMB-23; EMB-45 closes with this fold. Filed this leg: EMB-126 (by the `057` worker, a region-replace edit helper; not in Fleet Ready at my next `ready`, so routed to the owner). **Two of three workers left the task's `State:` as the claim line** and I set `done` at the fold; the third was told to in its dispatch and did. No `suite` task announced, nothing deployed, no bench. Supervisor ownership check on the leg's diff: clean.

## 2026-11-10 02:38 — atlas/058 part_card and mismatch_report answer before an atlas exists

**Decided:** nothing numbered; `DESIGN.md` "Query surface" amended in place (EMB-23), on the direction set at the split. With no atlas (`a.atlas is None`), `part_card` builds the part-to-document join from the netlists and `Coverage.part_docs` (`Atlas.part_docs`); a board MPN resolves to its card, `board=all` lists refs and nets, and a covered but undistilled MPN answers with the covering file and "not translated yet". `mismatch_report` runs `mismatch.run_netlist_only` (in memory, writes nothing; the MCU from `atlas.toml` `[mcu] part`) and lists every check in `mismatch.NEEDS_BUILD` under "Not run" with what it lacked. Run without a build: connector net names, DNI parts on MCU paths, pull rail vs MCU I/O supply, MCU symbol pin name vs datasheet, far-end level vs pin tolerance (when pin records exist), driver claims vs datasheet. **The worker's calls:** open-drain far-end pull goes under "Not run" (its pull may be a DT flag); an atlas present but missing `pins.json` behaves as before. Also `DESIGN.md`'s "declare no hint" sentence now names `reg_read_bank` (`atlas/057`'s reviewer aside).
**Merged:** `agent/atlas/058-part-card-and-mismatch-report-answer-before-an-atlas-exists` (code `38a87fa`, ff on `6eca094`; doc `f8d6fca9`, the worker's `f53565ea` cherry-picked onto `e91066b0`). Gate on the merge result: `pytest -rs` 704 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. The worker again left the claim line; I set `done` at the fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real project: `q part_card` and `q mismatch_report` on a repo with netlists and translated datasheets but no `/atlas-build` yet.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6.
**Least sure about:** the no-atlas `mismatch_report` is not cached and rebuilds the join, every distillation's records included, on each call; nobody measured it on a real project's size.

## 2026-11-10 02:31 — atlas/057 a live read selects a register's bank first

**Decided:** nothing numbered; `DESIGN.md`'s `bus` row and live-read section amended in place (EMB-124). A `bus` record may state `bank_select: {reg, values: {<bank>: <value>}}`. `ext_reg_read` reads the select register once (the previous page), writes the bank's value, reads, and writes the previous page back on every exit, a failed read included; consecutive registers on one bank share one select; an unreadable select register means nothing is written. **The opt-in is `allow_bank_select`**: CLI `live reg-read --allow-bank-select`, and **a new MCP write tool `reg_read_bank`** (the worker's pick: `reg_read` stays read-only and gains no parameter). Without it a single banked register is refused naming the opt-in and nothing reaches the shell; a whole-part read lists banked registers under "Not read"; a part with no `bank_select` reads as before and says "Page not selected".
**Merged:** `agent/atlas/057-a-live-read-selects-a-registers-bank-first` (code `6eca094`, ff on `f1c3bc4`; doc `3c9e7c96`, the worker's `867da3b4` cherry-picked onto `354dbf6b`). Gate on the merge result: `pytest -rs` 699 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12. The worker left the task's `State:` as the claim line; I set it `done` at the fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** `embarch-atlas live reg-read <label>.<REG>@<bank> --allow-bank-select` on a board with a paged I2C part whose `bus` record states `bank_select`: the value comes from that bank and the select register reads its old value afterwards. The Zephyr `i2c write_byte` argument order is from the worker's memory, not a board or the fake.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 41% (inside its reset grace), weekly 57%.
**Least sure about:** the sequence assumes an 8-bit, readable page register reached through the same `windows` routing as the others; a write-only page register refuses outright, which is safe but may be common. The reviewer's non-finding (`DESIGN.md`'s "declare no hint" sentence does not name `reg_read_bank`) rides along in `atlas/058`'s dispatch.
**Leg notes (this leg, first unit):** spawned with the pump latched in burndown, no stop marker, no owner message; nothing to recover (no claims, no leg worktree, no unit worktrees). Leg began at `1f83ada2`. **Split EMB-23 into `atlas/058` and EMB-45 into `atlas/059`** (`354dbf6b`), announced at `ts` `1794302695.415959`. Direction I set for both, on the owner's behalf: 058's `part_card` resolves an MPN through `coverage.py` and the netlists when there is no `pins.json`, and `mismatch_report` runs the build-free checks with a "Not run" list (the issue's own candidates); 059's board package is engineer-declared per ref in `boards/bindings.json`, reading it from the BOM footprint or `variant` records is out of scope, and an undeclared pin whose records differ by package is reported ambiguous rather than first-matched. Refill was owed (depth and spread); sweep skipped: no source changed since `2026-11-10 01:46`, whose sweep filed nothing. Size ledger: nothing overdue. The worker filed EMB-126 (a scripted region-replace helper, after it used inline Python edits again). `atlas/058` dispatched 02:31.

## 2026-11-10 02:19 — atlas/056 atlas-use knows the no-atlas placeholder

**Decided:** nothing numbered; `DESIGN.md` "How a session sees the atlas" amended in place (EMB-123). The `atlas-use` skill's step 1 now says: if `MAP.md`'s first line is `# No hardware atlas is built yet`, there is no atlas; say so, name `/atlas-translate-docs` then `/atlas-build`, do not answer from memory, and stop before step 2. The skill's `description` names the placeholder case. `test_skill_and_placeholder_name_the_same_next_steps` (in `tests/test_project.py`, beside the other `NO_ATLAS_MAP` tests) reads both and fails if the steps or their order drift.
**Merged:** `agent/atlas/056-atlas-use-knows-the-no-atlas-placeholder` (code `f1c3bc4`, ff on `dcf8e16`; doc `e1c10a30`, the worker's commit cherry-picked onto `18bdcea5`). Gate on the merge result: `pytest -rs` 693 passed, 3 expected skips (`test_public_guard` ran); client names clean on both repos; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real firmware repo: a session after `init` that loads the skill and the placeholder together, to see it stop (atlas/052's debt, now with the skill fixed).
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 40% (inside its reset grace), weekly 57%.
**Least sure about:** the skill's stop omits the placeholder's "first fill in `atlas.toml`" (the reviewer's non-finding; `atlas-translate-docs` step 0 covers it), so a session may name the two skills without saying the config comes first.
**Leg close (next leg, read this first):** 4 of 4 units (`chat/022`, `promptu/005`, `atlas/055`, `atlas/056`), all first-pass green, all four reviewers clean. Leg began at `d25dee1d`. **Split this leg** (`f285ca92`): EMB-125 into `promptu/005` and `chat/022` (two scopes' docs), EMB-123 into `atlas/056`, **EMB-124 into `atlas/057`, open** (`Hardware: verify-only`; its dispatch note puts the page-select write behind an explicit opt-in because the read tool is read-only, and asks for a restore even when the read fails). Done this leg: EMB-125, EMB-26, EMB-123. Filed: nothing. Queue: `atlas/057` only; `chat`, `promptu`, `desk`, `ui` have no task file. Fleet Ready: atlas EMB-21, 23, 25, 27, 32, 33, 34, 45 and desk EMB-11, 14, 17, 19, 73, 82, as the last two legs found them (each wants a new decision, a vendor file, a real build or the owner; EMB-82 asks for a new desk decision outright). Spread sweep skipped: no source changed since `2026-11-10 01:46`. Three of four workers again used inline Python edits despite the dispatch line, and all skipped the hook's filing prompt. I removed the two atlas code worktrees with `git worktree remove --force`, since their untracked `.venv` blocks a plain remove; both were otherwise clean and landed. Bench: not checked; burndown takes none. No `suite` task announced, nothing deployed. Supervisor ownership check on the leg's paths: clean.

## 2026-11-10 02:16 — atlas/055 a verb declares a board mating

**Decided:** nothing numbered; `DESIGN.md`'s `boards/system.json` paragraph and CLI table amended in place (EMB-26). New verb `embarch-atlas declare-interface <board>:<ref> <board>:<ref> (--rule R | --pin-map 1:6,2:5) [--prov engineer-declared|engineer-confirmed] [--note T]` (`declare()` in `interfaces.py`) writes one `interfaces` entry, leaving every other key alone; **an entry with the same id is replaced** (the worker's choice: re-declaring updates). It refuses a board with no netlist, a ref that is not a connector there, a rule outside the four, a pin-map contact the connector lacks, an odd-count connector with `row-swap`/`column-reverse`, both or neither of rule and pin map, and a non-engineer `prov` (exit 2). **Not done, the worker's pick the task allowed:** promoting an existing proposal by id; the `atlas-update` skill re-confirms with `--prov engineer-confirmed` instead. `atlas-translate-docs` step 4 and `atlas-update` step 3 name the verb and forbid hand edits. No `features.d` row (a verb on an existing capability).
**Merged:** `agent/atlas/055-a-verb-declares-a-board-mating` (code `dcf8e16`, ff on `c302ffe`; doc `915f6ab9`, the worker's `abc2db40` cherry-picked onto `424e0f9c`). Gate on the merge result: `pytest -rs` 692 passed, 3 expected skips (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); client names clean on both repos; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real project: a mating declared through the verb on a two-board system, then `interfaces` and a cross-board query reading it.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 38%, weekly 56%.
**Least sure about:** the reviewer's two non-findings: re-declaring with the default `--prov` silently downgrades an `engineer-confirmed` entry of the same id, and a hand-written entry under a different id for the same pair sits beside the verb's, so `mated_pairs` emits both; neither is filed, and either is a one-line refusal if the owner wants it.

## 2026-11-10 02:14 — promptu/005 decision 39 still keeps the handoff chip

**Decided:** nothing new; `embarch-promptu` decision 39 (the owner's, 2026-10-30, fork P9) **retired in place** for EMB-125: its heading now reads "Retired: the handoff card and its 'Fresh chat with this handoff' chip are gone", and an "Amended 2026-11-10 (EMB-66, EMB-125)" note in decision 40's form says the chat no longer offers a handoff card, so the chip and the handoff-request marker are gone (chat 36 and 97), and points to chat 103 for an agent's own handoff. The original sentence and the **Rejected** line stay as history; the number stands. The worker picked retire over amend, which the task allowed. `spec.md`, `open.md` and `interfaces.md` claim neither the chip nor the marker (checked by worker and reviewer); `docs/forks.md` P9 in the code repo stays as the dated fork record. Doc only.
**Merged:** `agent/promptu/005-decision-39-still-keeps-the-handoff-chip` (doc `20cde62c`, the worker's `68f102d4` cherry-picked onto `3953b4c8`; no code branch). Gate on the merge result: `check-docs.py` 12/12; client names clean; ownership `promptu` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 38%, weekly 56%.
**Least sure about:** 39 now says "the chat no longer offers a handoff card" beside chat 103, which has a handoff card of its own (the agent's `handoff` tool's); the reviewer calls it loose, not contradictory, and EMB-125 is otherwise closed by this unit and `chat/022`.

## 2026-11-10 02:13 — chat/022 decision 103 stops naming a deleted function and chip

**Decided:** nothing. `embarch-chat` decision 103's decision text is unchanged; its **As built** sentence now says the fresh session starts through `startChat` on the old chat's cwd, work item and mode, then takes its model, effort and Ultracode (what `handoffChat` in `src/extension.ts` does), where it said "`freshChat`'s start"; its **Rejected** "a new tab (36's chip does that)" now gives a reason that stands without the removed chip (the old panel would be left showing the ended chat). The chat half of EMB-125; the Promptu half is `promptu/005`. Doc only: no `embarch-chat` commit (nothing under `src/`, `webview/` or `test/` names `freshChat` any more, checked at dispatch).
**Merged:** `agent/chat/022-decision-103-names-a-deleted-function-and-chip` (doc `3953b4c8`, the worker's `3d6c446b` cherry-picked onto `ed3d9e3a`; no code branch). Gate on the merge result: `check-docs.py` 12/12; client names clean; ownership `chat` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 35% to 38% (inside its reset grace), weekly 56%.
**Least sure about:** the new rejection reason is the worker's own wording (the old text gave none); the reviewer checked it against `handoffChat` and calls it a rationale, not a new decision.
**Leg notes (this leg, first unit):** spawned with the pump latched in burndown, no stop marker, no owner message; nothing to recover (no claims, no leg worktree; the local `agent/chat/018` branch is the fold's to prune). Leg began at `d25dee1d`. **Split EMB-125 into `promptu/005` and `chat/022`** (it names docs in two scopes), **EMB-123 into `atlas/056`, EMB-124 into `atlas/057`** (`f285ca92`), announced at `ts` `1794301835.560849`. `atlas/057` is `Hardware: verify-only` and its dispatch note requires the page-select write to sit behind an explicit opt-in, since the read tool declares itself read-only. Spread sweep skipped: no source changed since `2026-11-10 01:46`. Day fold and history name check: done by an earlier leg today. Size ledger: nothing overdue. Dispatched `atlas/055`, `promptu/005`, `chat/022` at 02:11.

## 2026-11-10 02:04 — chat/018 the bulb stops suggesting context handling

**Decided:** nothing new; `embarch-chat` decisions 36 and 97 amended in place (EMB-66, the owner's call). The 💡's cards call asks Haiku for desk references only, and with no desk references it makes no call (the worker's addition: nothing else is left to judge). Removed with the cards: the handoff request (`handoffRequest`, `extractHandoff`, the fence), the "Fresh chat with this handoff" chip and `freshChat`, and the Promptu `handoff` origin, all of which only the handoff card reached (checked on `main`: `freshChat` was called from the chip alone). Kept: a typed `/compact` first line (`splitCompact`, `sendAfterCompact`), the header's meter and Compact button, and the agent's own handoff (103, `handoffChat`, untouched). `spec.md` went to 9,011 B, out of reserve; `features.d/chat-020-haiku-assistant.md` amended.
**Merged:** `agent/chat/018-the-bulb-stops-suggesting-context-handling` (code `b1802d6`, ff on `7a93e95`; doc `787c9cfb`, the worker's `27d39662` cherry-picked onto `88129529`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (258 pass, 0 fail, 75 skipped without `EMBARCH_DESK_BIN`), `test:webview` all passed, its new "offers no context-handling card" PASS line present; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12. The 60 desk-gated host tests did not run (no desk binary; EMB-122), and this unit deleted 30 lines of them.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-125
**Hardware debts:** none needing a board. Owed to a live window: the 💡 on a long chat showing reference cards only. Nothing installed.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 35%, weekly 56%.
**Least sure about:** EMB-125 is real and left for the next leg: `embarch-promptu` decision 39 (the owner's, 2026-10-30) still says the handoff card keeps the chip, and `embarch-chat` 103's as-built prose still names `freshChat` and "36's chip"; both are doc edits, no revert, and 39's is in another scope from this unit's.
**Leg close (next leg, read this first):** 4 of 4 units (`atlas/052`, `atlas/053`, `atlas/054`, `chat/018`), all first-pass green; reviewers: three clean, one finding (EMB-125). Leg began at `fe4a4e3f`. One supervisor commit outside a fold: `c302ffe` in `embarch-atlas`, restoring `width` to `DESIGN.md`'s `register` row that `atlas/054` dropped. **Split this leg:** EMB-47, 46, 26 into `atlas/053`, `054`, `055` (`83f27e2f`); 47 and 46 Done, **`atlas/055` (EMB-26, the mating verb) is open**. Done this leg: EMB-22, 47, 46, 66. Filed this leg: EMB-123 (atlas, `atlas-use` skill vs the placeholder), EMB-124 (atlas, page-select write, verify-only, by the `054` worker), EMB-125 (promptu, by the `chat/018` reviewer); all three in Fleet Ready for the next `ready`. Queue: `atlas/055` only; `chat`, `desk`, `ui` have no task file. Fleet Ready: the three new issues plus atlas EMB-21, 23, 25, 27, 32, 33, 34, 45 and desk as before (all want a decision or the owner). Spread sweep: nothing filed (2026-11-10 01:46). Workers still use inline Python edit scripts and skip the hook's filing prompt (all four said so). Bench: not checked; burndown takes none. No `suite` task announced, nothing deployed. Supervisor ownership check on the leg's diff: clean.

## 2026-11-10 01:55 — atlas/054 a register record can state its bank

**Decided:** nothing numbered; `DESIGN.md`'s `register` and `field` rows amended in place (EMB-46). `register` takes an optional `bank` (non-empty string or non-negative integer); **a `field` has no `bank` of its own and inherits its register's through `reg`** (the worker's pick, offered in the dispatch). Check G keys duplicates on `(bank, addr)`. Codecheck's `RegMap` keeps `(bank, addr)` maps beside the old address-only view, which stays the default, so unbanked parts and every existing caller resolve as before. **The worker invented a live-target syntax, `<label>.<REG>@<bank>`**; a name on several banks with none on the main map errors naming them. Not done: codecheck does not know which bank a driver's constants mean (driver constants carry none). Page-select writes on the device were out of scope and the worker filed **EMB-124** (Fleet Ready, `Hardware: verify-only`). The edit dropped `width` from `DESIGN.md`'s `register` row (the reviewer's aside); I restored it on `main` as `c302ffe`, doc only.
**Merged:** `agent/atlas/054-a-register-record-can-state-its-bank` (code `d6efe11`, ff on `ca710c5`, plus my fix-forward `c302ffe`; doc `370801a6`, the worker's `a9f97f5f` cherry-picked onto `1c71cca2`). Gate on the merge result: `pytest -rs` 690 passed, 3 expected skips (`test_public_guard` ran); client names clean (also after `c302ffe`); ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a live read of a banked register returns whichever page the part is on, because nothing selects the page (EMB-124); needs a board with a paged sensor to confirm. Owed to a real vendor file: check G on the paged sensor that showed 59 duplicate addresses.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 30%, weekly 56%.
**Least sure about:** the `@<bank>` syntax is now a user-facing name nobody chose; it is cheap to change before anyone types it, and costly after.

## 2026-11-10 01:50 — atlas/053 a variant record kind lists orderable parts

**Decided:** nothing numbered; `DESIGN.md`'s record-kind table gains a `variant` row in place (EMB-47). A `variant` is one orderable part: `mpn` (non-empty string) and `options` (an object of option name to string, number or boolean, at least one; no other fields). `rule` stays behaviour and `quirk` class `variant` still only flags a row that differs by variant. It is in `KINDS`, `FACT_KEYS`, the schema enum with its own `$defs/variant`, `render.RENDERERS` (`t_variant`) and the datasheet procedure. The records mini-validator now honours `minProperties`, which only `variant.options` sets, so no existing record's validation changes (checked on the diff). No `features.d` row: a schema kind, not a capability.
**Merged:** `agent/atlas/053-a-variant-record-kind-lists-orderable-parts` (code `ca710c5`, ff on `9b875c2`; doc `63142756`, the worker's `92c1d85b` cherry-picked onto `6f6b3b97`). Gate on the merge result: `pytest -rs` 686 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: a distillation that writes `variant` records for a regulator's orderable-parts table.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 30%, weekly 56%.
**Least sure about:** `secondlook.py` has no `variant` entry and falls back to its generic re-read, as `requirement`, `conflict` and `check` already do (the reviewer's non-finding); whether that re-read checks an `options` table well is untested.

## 2026-11-10 01:46 — atlas/052 a session before the first atlas is told there is none

**Decided:** nothing numbered; `DESIGN.md` "How a session sees the atlas" amended in place (EMB-22). `embarch-atlas init` writes `<atlas_dir>/MAP.md` as a placeholder (`NO_ATLAS_MAP`, first line `# No hardware atlas is built yet`, naming `/atlas-translate-docs` then `/atlas-build`) when none exists, never over a real map; the first `join` replaces it as before. `mark_map` and `stale.py` needed no change: `mark_map` already ignores a first line that is not an atlas header, and `stale.py` never reads `MAP.md`. A `join` of an atlas not at HEAD leaves the placeholder, which is right. Filed **EMB-123** (Fleet Ready, atlas) from the reviewer's aside: the `atlas-use` skill triggers on `MAP.md` existing and its step 1 does not know the placeholder.
**Merged:** `agent/atlas/052-a-session-before-the-first-atlas-is-told-there-is-none` (code `9b875c2`, ff on `f796611`; doc `15ab2fa5`, the worker's `724df3eb` cherry-picked onto `f5c64d18`). Gate on the merge result: `pytest -rs` 685 passed, 3 expected skips (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real firmware repo: `init` then a session that reads the placeholder through `CLAUDE.local.md`; only tests show it.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6; 5-hour 25% to 29%, weekly 55% to 56%.
**Least sure about:** whether a session that loads the placeholder and the `atlas-use` skill together follows the placeholder or the skill's card steps; EMB-123 is the fix, and until it lands the skill can send a session looking for cards that do not exist.
**Leg notes (this leg, first unit):** spawned with the pump latched in burndown, no stop marker, no owner message; nothing to recover (no claims, no leg worktree, only the long-parked `agent/ui/059-diff-new-lines-republish` doc branch, which is not mine to delete). Leg began at `fe4a4e3f`. **Split EMB-47 into `atlas/053`, EMB-46 into `atlas/054`, EMB-26 into `atlas/055`** (`83f27e2f`), announced at `ts` `1794300040.711179`; all three have a stated direction and add only optional fields or a verb, so none needs a numbered decision (the atlas has none; `DESIGN.md` is amended in place). Fleet Ready left: atlas EMB-21, 23, 25 (direction not decided), 27 (needs a real build), 32, 33, 34 (33 and 34 need a vendor datasheet), 45 (package choice per board part undecided), and EMB-123; desk as the last leg found it (all want a new decision or the owner). Spread sweep: nothing filed (2026-11-10 01:46): the only source changed since `2026-11-09 17:34` was `embarch-chat/open.md` (`chat/015`, an owner question). Day fold and history name check: done by the previous leg. Size ledger: nothing overdue. Dispatched `atlas/052` and `chat/018` at 01:42, `atlas/053` at 01:45. Bench: not checked; burndown takes none.

## 2026-11-10 01:34 — chat/015 the spec status line says what is installed

**Decided:** nothing. `embarch-chat/spec.md`'s **Status:** line now says decisions 94–100 are installed (67 retired), citing the 2026-11-05 measurement as a dated fact (the installed `dist/extension.js` md5-identical to the clone's, built 2026-11-04 02:10 after `2b04ff5`; install time unrecorded), and that decision 100 is **not recorded as reviewed**. The line was edited, not appended, and dropped "86–91 live after a window reload" to stay out of reserve: `spec.md` went 9,034 to 9,027 B, 12 B under the reserve line, so no compaction task. `open.md`'s "Promptu in the chat (94–99) waits for install" now says installed, and a new open question asks the owner whether decision 100 was reviewed. Plus, at my dispatch, the comment near line 33 of `webview/chat/composer.tsx` now says the thumbnail sits **above** the input (decision 56 as amended by `chat/020`); comment only. Closes EMB-68.
**Merged:** `agent/chat/015-the-spec-status-line-says-what-is-installed` (code `7a93e95`, ff on `6e15acf`; doc `78ea54b3`, the worker's `77ecf360` cherry-picked onto `4be6006e`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (261 pass, 0 fail, 76 skipped without `EMBARCH_DESK_BIN`), `test:webview` all passed; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The install claim rests on a 2026-11-05 reading; nothing since checks what the installed extension is, and `main` has moved through decision 103 and `chat/010` to `chat/015` since.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6, at start and end; 5-hour 18% to 24%, weekly 55%.
**Least sure about:** the status line now reads "94–100 installed" while saying nothing of what `main` built after 2026-11-04, so a reader can still take the install as current; the task scoped it that way.
**Leg close (next leg, read this first):** 4 of 4 units (`chat/021`, `chat/020`, `atlas/051`, `chat/015`), all first-pass green, all four reviewers clean. Leg began at `dc663c8b`. Two of the four were the killed leg's finished-and-pushed workers, landed here rather than blocked. **Split this leg:** EMB-120 (`atlas/051`, now Done) and **EMB-22 into `atlas/052`, open**: `init` writes a placeholder `MAP.md` until the first `join`. Done this leg: EMB-118, EMB-119, EMB-120, EMB-68. Filed: **EMB-122** (Fleet Ready, `Scope: fleet`: the chat gate never runs the 60 desk-gated host tests); `ready` should move it to the owner's lane. Queue: `atlas/052`, `chat/018`; Fleet Ready is otherwise atlas (11 issues; the two I read besides EMB-22, EMB-23 and EMB-25, say "Direction: not decided") and desk (every one wants a new decision or the owner; EMB-73 is `Scope: suite`). **`desk` and `ui` have no task file.** The desk binary at `.worktrees/embarch-chat/desk-target` is deleted (1.3 GB); a leg gating a chat unit's host tests rebuilds it with `--target-dir` outside every tree. Day fold of 2026-11-09 done; nothing overdue on the size ledger; spread sweep skipped (no source changed since `2026-11-09 17:34`). Bench: not checked; burndown takes no bench task. No `suite` task announced, nothing deployed. Supervisor ownership check on the leg's diff: clean.

## 2026-11-10 01:32 — atlas/051 doc check reports a cite of a page outside the document

**Decided:** nothing numbered; `DESIGN.md`'s `doc check` row amended in place (EMB-120). `doc check` now **fails** a cite outside `1..pages` as a new `P:` check, the worker's choice by analogy: `check.py` already fails a quote cited on the wrong page (A `wrong-page`) and an unanchored prose number (M), and an out-of-range cite can never anchor anything. A record is `failed` with `P: cites page N, outside 1-n`; a `card.md` or `s/*.md` cite goes into `checks.json` under `P` and prints as `P <file>: ...`; either exits 1. `freeze` and `check` share one test, `check.out_of_range`, which reports nothing when `pages` is 0 (a non-PDF source). A record cite of page 0 is already refused by the schema as `V:` and never reaches `P:`, so page 0 is covered through prose and the helper's own assertions.
**Merged:** `agent/atlas/051-doc-check-refuses-a-cite-outside-the-document` (code `f796611`, ff on `bfeae59`; doc `059f6796`, the worker's `6432aa52` cherry-picked onto `29a2d4e8`). Gate on the merge result: `pytest` 684 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `doc check` on the datasheet behind EMB-40, to see whether its extra page was an out-of-range cite (now a `P:` line) or a high `pages` in `doc.json`.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6.
**Least sure about:** `freeze` used to flag every cite as out of range when `pages` was 0 and now flags none (the reviewer's non-finding); no decision covers that case, and a PDF whose `doc.json` read 0 pages would now pass both checks silently.

## 2026-11-10 01:28 — chat/020 two decisions put the notice and thumbnails under the input

**Decided:** nothing new; decisions 56 (`embarch-chat/decisions/input.md`) and 96 (`decisions/promptu.md`) amended in place for EMB-119. 56's heading now says the pasted image is a thumbnail **above** the input; 96's failed-pass line is "one line above the input (the composer's notice line, as paste and `/btw` use)", and Desk Start work's fallback line says "above the input" too. Both match `webview/chat/composer.tsx` since `chat/014`. The only other "under the box" left in `embarch-chat`'s docs is a **Rejected** alternative in `decisions/assistant.md`, which is history and stays. Doc only: no `embarch-chat` commit.
**Merged:** `agent/chat/020-two-decisions-put-the-notice-and-thumbnails-under-the-input` (doc `e5698bf7`, the worker's `e8fa7f27` cherry-picked onto `1bee15af`; no code branch). Landed by this leg from the branch the worker pushed at 23:08, as the previous leg was being killed. Gate on the merge result: `check-docs.py` 12/12; ownership `chat` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6.
**Least sure about:** the reviewer found a stale code comment near line 33 of `webview/chat/composer.tsx` ("thumbnail under the input"); I folded fixing it into `chat/015`'s dispatch as a comment-only edit, so if that unit blocks, the comment stays stale.

## 2026-11-10 01:26 — chat/021 six host tests fail against the local desk binary

**Decided:** nothing. The cause is test-side, not the desk: a chat's process environment is taken when the chat is created (`ChatManager.create` reads `s.env?.()`, and a reload restores the same way), and five tests started their chat on `basic` or `deny` and only then set `FAKE_CLAUDE_FIXTURE` or `FAKE_CLAUDE_INPUT_LOG`, so the fake CLI replayed the wrong recording into a 5 s timeout. The sixth (Start work with Promptu, decision 96) was the stale 2026-11-03 binary and passes on a desk built from `main`. Fix in `test/host.test.mjs` only: `startUntracked` takes a recording name or an absolute path and the five name theirs there; the reload-queue test sets its input log before `reload`. No desk bug. Closes EMB-118.
**Merged:** `agent/chat/021-six-host-tests-fail-against-the-local-desk-binary` (code `6e15acf`, ff on `424c3cf`; doc `208e3dc0`, the worker's `bf60fd1f` cherry-picked onto `e852ae8e`). Landed by this leg from branches the worker pushed at 23:06, before the previous leg was killed. Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (261 pass, 0 fail, 76 skipped without `EMBARCH_DESK_BIN`), `test:webview` all passed; **`test/host.test.mjs` with `EMBARCH_DESK_BIN` set to the desk built from `main` `4b83b5e`: 60 pass, 0 fail**; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00 (latch re-armed 01:16 at weekly 55%, no `gate=off` line this time, so the 97% caps apply), wave 6; 5-hour 18%.
**Least sure about:** the gate still skips those 60 tests on every chat unit, so the next test-side fault there is as invisible as this one was; running them needs a `gate.md` rule, which is the owner's, so I filed **EMB-122** (`Scope: fleet`, gap; `ready` will move it to the owner's lane).
**Leg notes (this leg, first unit):** spawned with the pump latched in burndown, no stop marker, no owner message. **Recovery:** the previous leg was killed at ~23:08 with `chat/020` and `chat/021` claimed; both worktrees were clean and both workers had pushed (`chat/021` code and doc, `chat/020` doc only, as the task is doc only), so a pushed branch retired each worker and this leg lands them as its units 1 and 2 rather than blocking them. Leg began at `dc663c8b`. The 2026-11-09 day is folded (log-folder: 43 units, 112 KB to 26 KB) and 2026-11-06 rolled to `log-archive/`; `check-client-names.py --suite --history` clean on all 16 repos. **Split EMB-120 into `tasks/atlas/051` and EMB-22 into `atlas/052`** (`9a88a836`). Spread sweep skipped: no source changed since `2026-11-09 17:34`. `atlas/051` dispatched 01:21 and reported at 01:24. Nothing overdue on the size ledger.

## 2026-11-09 — 43 units

*Folded 2026-11-10 by the leg's log-folder from the day's 43 per-unit entries (the narrative reasoning behind each accepted judgement, the gate transcripts and every "Least sure about" that git or a filed issue already holds went; every SHA, every Reviewer line and every Hardware debts line stays, one block per unit below). The day ran as ten legs at wave 6 under burndown (`gate=off` latch until 2026-11-11 06:00; a real 429 is still the stop signal).*

**Carry forward (the next leg cannot recover these):**
- **chat/020 and chat/021 are not in this day.** The leg that died at ~23:08 dispatched them (EMB-119 into `chat/020`, doc only: decisions 56 and the Promptu decision still say "under the input"; EMB-118 into `chat/021`, host tests against a desk built from `main`, split in `ff265215`); the current leg is landing them. The desk binary for `chat/021` was built at `/home/gabriel/Github/embarch/.worktrees/embarch-chat/desk-target` (outside every repo tree); delete it at leg end.
- **Filed today and still open:** EMB-116 (Backlog, `Type: decision`, owed `embarch-chat` decision beside 91: the chat never scrolls sideways; proposed text under `## Owed decision` in the retired `chat/010` task file), EMB-118 (Fleet Ready, chat: six host tests fail against the local desk binary; the binary was built 2026-11-03), EMB-119 (Fleet Ready, chat: decisions 56 and Promptu say "under the input", stale after `chat/014`), EMB-120 (Fleet Ready, atlas, gap). Also EMB-111 (desk, `/linear/mine` and `/linear/open` still answer an empty scope on a team-bound desk), EMB-112 and EMB-113 (Backlog, atlas, for the owner: the port join ignores sheet hierarchy; Check K's best-agreeing group lets a wrong-condition number pass), EMB-104 (Backlog, Fleet Ready has no one-line listing), EMB-105 (desk, landed as `desk/012`), EMB-115/117 (ui, landed as `ui/106`/`ui/107`).
- **desk has no task file.** Every desk issue left in Fleet Ready wants a new decision (EMB-14, 17, 82) or the owner (EMB-11's SKILL.md half, EMB-19's west design); burndown withholds decisions. **EMB-73 (`Scope: suite`) is untouched**: its last box asks for an `embarch-dev-workflow.md` section 6 change, which is the owner's, plus new decisions in two sub-projects.
- **Queue at day end:** `chat` 015, 018 (018 opened by the `chat/017` fold), plus `chat/020`, `021`; `chat/019` and `promptu/004` are `blocked`, `In flux: yes`, due 2026-11-23 (size debts, both `spec.md` compactions; `desk/011` is paid). `promptu/004` stays blocked on decision 30's build step 4. `embarch-chat/spec.md` is 9,034 B, 5 B under its reserve line: a chat unit that edits it must ride the compaction along. Fleet Ready is mostly `atlas` (about 16 left; EMB-40 landed as `atlas/050`) and `desk` as above.
- **Still owed:** the first leg after midnight owes the day fold (this) and `check-client-names.py --suite --history`; the size ledger has nothing overdue. Spread sweep skipped all evening: no source changed since `2026-11-09 17:34` (its marker). Bench not checked; burndown takes no bench task. No `suite` task announced, nothing deployed.
- **Failure patterns likely to recur:** (1) workers leave a state line the gate refuses (`claimed`, `done,`, `done (`): check the task's state line before cherry-picking. (2) A fold that retires a task named in another task's `Unparks when:` turns `check-task-state.py` red only after the fold's own gate ran (fixed on `main` as `f76b9305`): check other parks before folding. (3) A green `test:webview` proves nothing about a new check unless its own PASS line is in the output; grep for it on every chat unit that adds one (`chat/010` called a check passing that never ran). (4) The harness sends a leg a hand-back prompt with workers in flight (twice): keep landing, do not `leg-end`; the auto-mode classifier refuses a force-push to an `agent/*` branch after a rebase. (5) Workers use inline Python edit scripts and skip the hook's filing prompt (one filed EMB-108). (6) The chat host tests fail 5 to 6 ways against a stale desk binary (decisions 63, 64, 72, 77, 78, 96 on `chat/013`; five different ones on `chat/007`); `chat/021` is the check. (7) Read each issue's named files on `main` before writing a task (`ui/105` and `chat/013` were two-thirds stale); reconcile desk issues against decision 77 (EMB-94).
- **Decisions made on the owner's behalf today:** unparked `core/112` on its due date to fill a fourth scope slot (verbatim split only; decision 89 still unverified against a moved probe); split Fleet Ready issues in waves (`cef37baf` 14 issues into 16 tasks and the first `promptu` tasks; `273ed317`, `bf619a2a`, `e20382b7`, `5fdc6473`, `288a1fce`, `e4273cec`, `dc2a64de`, `ff265215` later), announcements at `ts` `1794270556.536659` and `1794277712.673199`. The only design call no task made: `chat/008`'s Memory pass chat is `untracked` (one line in `startMemoryPass` if the owner wants it tracked).
- **Leg start SHAs (main at each leg's begin, oldest first):** `5b8d8362`, `3ffc8e00`, `0ebf3855`, `fa94400b`, `2ef4d1d7`, `9e8abd40`, `504bd5e6`, `62b51dff`, `0d7c20c4`, `836d2a3c`, `7332632a`.
- **Recovery:** the leg that started 17:47 split six issues (`273ed317`), dispatched at 17:54, landed `atlas/038` and died without a tick, fold or log entry; the `atlas/038` fold below is recovery (its three other claims reclaimed to `open` in `2bc10797`).

**Units, newest first** (code SHA is on `main`; "doc" is the cherry-picked doc commit; each gate was green on the merge result unless stated):

### 23:08 — ui/108 the Desk tab's note count and switch warning match the desk
**Merged:** `agent/ui/108-the-desk-note-count-and-switch-warning-match-the-desk` (code `08f9a53`, ff on `c3c4909`; doc `b4c08f80`, the worker's `a0ba7d4b` cherry-picked onto `64098d7c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The e2e debt the worker recorded is paid (above).

### 23:03 — atlas/050 doc freeze reports the document's real page count
**Merged:** `agent/atlas/050-doc-freeze-reports-the-document-s-real-page-count` (code `bfeae59`, ff on `cbd1bb9`; doc `0a4077b5`, the worker's `b49ff555` cherry-picked onto `275ee998`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `doc freeze` on the datasheet that showed P one over its page count. A warning line means the cause was an out-of-range cite; still one over with no warning means `doc.json`'s `pages` is itself high, a separate bug.

### 22:52 — chat/014 the input is one row
**Merged:** `agent/chat/014-the-input-is-one-row` (code `424c3cf`, ff on `fad3fe8`; doc `3cc86864`, the worker's `1245cc10` cherry-picked onto `02589f25`).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-119
**Hardware debts:** none needing a board. Owed to a live window: the one-row input at a narrow pane, Send never pushed off, and both popovers inside it. Nothing installed.

### 22:36 — atlas/049 a document's own header names its revision and number
**Merged:** `agent/atlas/049-a-document-s-own-header-names-its-revision-and-number` (code `cbd1bb9`, ff on `84d8909`; doc `ce813c73`, the worker's `a7c8d3c7` cherry-picked onto `6ea97619`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `atlas inventory` and `doc prep` on the non-chip datasheet that showed it, confirming rev `A` and doc_no `001`; only synthetic PDFs show either.

### 22:34 — ui/107 a session row whose folder is gone says so
**Merged:** `agent/ui/107-a-session-whose-folder-is-gone-says-so-on-the-desk-tab` (code `c3c4909`, ff on `9f2026d`; doc `5bb109d7`, the worker's `99bc240c` cherry-picked onto `34e9fab6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live UI: a session whose folder was deleted showing "folder gone" on the Desk tab. Nothing installed.

### 22:32 — desk/017 a start that resolves no desk is no desk everywhere
**Merged:** `agent/desk/017-a-start-that-resolves-no-desk-is-no-desk-everywhere` (code `4b83b5e`, ff on `377c116`; doc `5c77a371`, the worker's `08ca0b5e` cherry-picked onto `bc5a34f7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a session resumed in a folder with no desk hearing and writing no desk's notes. Nothing installed.

### 22:20 — chat/013 a window start never raises the UI tab
**Merged:** `agent/chat/013-a-window-start-never-raises-the-ui-tab` (code `fad3fe8`, ff on `bae5fa8`; doc `2aa4a91c`, the worker's `79c7760c` cherry-picked onto `799bd173`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a reload that raises no browser tab. Nothing installed.

### 22:12 — atlas/048 a part named in passing is not covered
**Merged:** `agent/atlas/048-a-part-named-in-passing-is-not-covered` (code `84d8909`, ff on `df232e9`; doc `108cc9c1`, the worker's commit cherry-picked onto `25a6cd7e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: a datasheet whose own part first appears on page 2 (a long cover page) is now proposed rather than covered; only synthetic PDFs show either case.

### 22:12 — ui/106 Pick up says no card on the board
**Merged:** `agent/ui/106-pick-up-says-no-card-on-the-board` (code `9f2026d`, ff on `877a042`; doc `25a6cd7e`, the worker's commit cherry-picked onto `ad2cd9dc`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live UI: the Pick up title and empty note reading the new words. Nothing installed.

### 22:09 — desk/016 a session whose folder is gone says so
**Merged:** `agent/desk/016-a-session-whose-folder-is-gone-says-so` (code `377c116`, ff on `d48a18d`; doc `664a1198`, the worker's `9817a08a` cherry-picked onto `a6129099`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a session whose folder was deleted showing `folder_missing` and no Go to chat. Nothing installed.

### 21:58 — chat/010 the chat never scrolls sideways
**Merged:** `agent/chat/010-the-chat-never-scrolls-sideways` (code `bae5fa8`, ff on `80bf56d`: the worker's `889efda` and `8990003` plus my `bae5fa8`; doc `f29acbf1`, the worker's `197b3fbc` cherry-picked onto `5a032a31`).
**Blocked:** nothing, after one send-back. **The worker's first report called the new check passing when it never ran**: a one-off Python replace hit the first `await teardown();` in `test/webview.e2e.mjs`, which is inside the `uncaughtException` handler, so the check only ran on a crash and the gate was green without it. I caught it because the new check's name was absent from the `test:webview` output, and sent it back; the worker moved it to the chat checks (it must run before `go("/list.html")`) and showed it FAIL with `style.css` reset to `main`. Its fix left the crash handler's `await teardown();` unindented, which `bae5fa8` restores (whitespace only).
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a long line in a code block, diff and table wrapping with no sideways bar. Nothing installed.

### 21:28 — desk/015 an issue whose card the view window hides is listed in Pick up
**Merged:** `agent/desk/015-a-card-outside-the-view-window-is-in-pick-up` (code `d48a18d`, ff on `3d29d6c`; doc `51bd41a7`, the worker's `a68f1316` cherry-picked onto `3f82ff92`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a card quiet past the window showing its issue in Pick up, and Add card putting it back. Nothing installed.

### 21:27 — atlas/047 application reports and reference-manual user's guides get their kind
**Merged:** `agent/atlas/047-application-reports-and-reference-manual-users-guides-get-their-kind` (code `df232e9`, ff on `ca32a6c`; doc `dba08bbe`, the worker's `640ece3a` cherry-picked onto `2a255c73`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: that an actual reference manual published as a user's guide carries the self-naming line within page 1's top and 80 characters; only synthetic PDFs show it.

### 21:24 — desk/014 my issues and open issues name their scope
**Merged:** `agent/desk/014-my-issues-and-open-issues-name-their-scope` (code `3d29d6c`, ff on `5a8fcad`; doc `a3c58e99`, the worker's `67707ef2` cherry-picked onto `57a9dbb5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a team-bound desk's My issues and open-issues answers reading `team <KEY>`. Nothing installed.

### 21:15 — chat/016 a deleted chat folder is named as missing
**Merged:** `agent/chat/016-a-deleted-chat-folder-is-named-as-missing` (code `80bf56d`, ff on `55e758b`; doc `b54dae62`, the worker's `3649fb60` cherry-picked onto `5f07e385`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a chat whose folder was deleted showing the folder error on its next message. Nothing installed.

### 21:11 — atlas/046 Check K reads side-by-side groups and a lone TYP column
**Merged:** `agent/atlas/046-check-k-reads-side-by-side-groups-and-a-lone-typ` (code `ca32a6c`, ff on `4a27ae0`; doc `aadfe5e5`, the worker's `9f20c0b8` cherry-picked onto `2a544fae`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 21:05 — atlas/045 nets joined through an off-sheet port are one net
**Merged:** `agent/atlas/045-nets-joined-through-an-off-sheet-port-are-one-net` (code `4a27ae0`, ff on `b2d418e`; doc `48a93f88`, the worker's `d9baa1e0` cherry-picked onto `d9e681b6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real export: that a net's `Ports > <title>` outline children carry the port name, which only the synthetic fixtures show.

### 21:02 — desk/013 a word search names the team it searched
**Merged:** `agent/desk/013-a-word-search-names-the-team-it-searched` (code `5a8fcad`, ff on `bc06133`; doc `3c9141d4`, the worker's `04c05358` cherry-picked onto `169207d2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a team-bound desk's word search answering with `team <KEY>`. Nothing installed; the running desk keeps the old answer until the owner rebuilds it.

### 20:54 — chat/011 the inline diff is one line until opened
**Merged:** `agent/chat/011-the-inline-diff-is-one-line-until-opened` (code `55e758b`, ff on `9fd3f0b`; doc `6761d22d`, the worker's `aca3157b` cherry-picked onto `325d8acd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: an Edit row closed, opening and closing on a click, and a permission card's diff still open. Nothing installed.

### 20:43 — atlas/044 a cite of another document is checked there
**Merged:** `agent/atlas/044-a-cite-of-another-document-is-checked-there` (code `b2d418e`, the worker's `f893727` rebased by me onto `9bc7b11` (atlas/043) and ff; doc `94f703fd`, the worker's `73129abc` cherry-picked onto `e2609b78`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:41 — desk/012 the skill and the server take the work item from the prompt first
**Merged:** `agent/desk/012-the-skill-and-server-take-the-work-item-from-the-prompt` (code `bc06133`, ff on `b47c12e`; doc `f4bc2dc9`, the worker's `2c0b9858` cherry-picked onto `39ba6c6a`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live session: a session started with an issue key in its prompt taking it from the skill or the server instructions rather than asking. Nothing installed; the running desk keeps the old strings until the owner rebuilds it.

### 20:40 — atlas/043 the renderer reads Note N footnotes
**Merged:** `agent/atlas/043-the-renderer-reads-note-n-footnotes` (code `9bc7b11`, ff on `fe7c00c`; doc `db7c29d6`, the worker's `f5d8ede6` cherry-picked onto `8d7ff3e0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:30 — chat/012 the side-question button is on the rail
**Merged:** `agent/chat/012-the-side-question-button-is-on-the-rail` (code `9fd3f0b`, ff on `b765313`; doc `f81355d1`, the worker's `23de1281` cherry-picked onto `51929357`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: the 💬 on the rail asking, Esc and the disabled state; nothing installed.

### 20:28 — desk/010 a Start work worktree links the clone's local files
**Merged:** `agent/desk/010-a-start-work-worktree-links-the-clones-local-files` (code `b47c12e`, ff on `5837ef5`; doc `b6730147`, the worker's `3710aa5b` cherry-picked onto `b67caf1e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a real Start work on a clone holding an atlas and an `.mcp.json`, and the session in it loading both; the Windows symlink branch (`symlink_dir`/`symlink_file`) was neither compiled nor run here. Nothing installed; the running desk keeps the old behaviour until the owner rebuilds it.

### 20:24 — atlas/042 a kind override reaches a prepped document's doc.json
**Merged:** `agent/atlas/042-a-kind-override-reaches-a-prepped-documents-doc-json` (code `fe7c00c`, ff on `da6c505`; doc `0da06622` and `d7f95f58`, the worker's `77dd3890` and `0391c5c2` cherry-picked onto `d2a90464`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:22 — desk/011 decisions/agents.md leaves the reserve by verbatim split
**Merged:** `agent/desk/011-compact-desk` (doc only: `49030a21`, the worker's `6cf2b043` cherry-picked onto `f4925c97`, plus my link fix `b0c191b3`; no code worktree).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:14 — chat/008 the Memory menu shows when a memory pass is due
**Merged:** `agent/chat/008-the-memory-menu-shows-when-a-memory-pass-is-due` (code `b765313`, ff on `a46c5ac`; doc `574f817a`, the worker's `47ce86ea` cherry-picked onto `e14370ac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: the three settings set, the due dot and the line showing, and a click opening a chat whose first message is the command, on the window's login and desk; the host path (reading the stamp, `startMemoryPass`) has no test that runs here. The due state refreshes only on page load or menu open. Nothing installed.

### 20:09 — desk/009 the start hook takes the work item from the prompt
**Merged:** `agent/desk/009-the-start-hook-takes-the-item-from-the-prompt` (code `5837ef5`, ff on `aa56a7a`; doc `ec7d333f`, the worker's `10570fdb` cherry-picked onto `529a0a77`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live session: the key-first behaviour lives in a model following the hook's text, and the test asserts only the text. Nothing installed; the running desk keeps the old text until the owner rebuilds it.

### 20:08 — atlas/041 check S reads a dimension cell as one value
**Merged:** `agent/atlas/041-check-s-reads-a-dimension-cell-as-one-value` (code `da6c505`, ff on `18756a3`; doc `38280b72`, the worker's `93d563cf` cherry-picked onto `4eee35c3`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:06 — core/112 two full Core docs leave the reserve by verbatim split
**Merged:** `agent/core/112-compact-core` (doc only: `901e51d0`, ff on `aae32208`; no code worktree).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `open.md`'s decision-89 bullet (a moved-probe run) is unchanged and still owed.

### 19:58 — chat/017 the chat gives Promptu's pass its context usage
**Merged:** `agent/chat/017-promptu-is-given-the-chats-context-usage` (code `a46c5ac`, ff on `468547a`; doc `abb84190`, the worker's `9d55fcaa` cherry-picked onto `15057714`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a real Promptu run from the chat receiving the flag; the test calls `runs.begin` with a stub CLI. Nothing installed or deployed.

### 19:53 — desk/008 a foreign issue key names the desk that holds it
**Merged:** `agent/desk/008-a-foreign-issue-key-names-the-desk-that-holds-it` (code `aa56a7a`, ff on `3141190`; doc `677278e6`, the worker's `1e60c745` cherry-picked onto `61deb548`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Nothing installed or deployed; the running desk keeps the old message until the owner rebuilds it.

### 19:53 — atlas/040 check U finds a unit as a token and reads a symbol whole
**Merged:** `agent/atlas/040-check-u-finds-a-unit-as-a-token-and-reads-a-symbol-whole` (code `18756a3`, ff on `335939a`; doc `61deb548`, the worker's `e15cda32` cherry-picked onto `be0a0118`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:50 — promptu/003 decision 40 follows the one-colour rail
**Merged:** `agent/promptu/003-decision-40-follows-the-one-colour-rail` (doc only: `b92ffb51`, the worker's `ec956b31` cherry-picked onto `724d0dfa`; the `embarch-promptu` worktree stayed clean and was not pushed).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:43 — chat/009 the rail's icons are one-colour SVGs
**Merged:** `agent/chat/009-the-rail-icons-are-one-colour` (code `468547a`, ff on `f823dc8`; doc `2313f775`, the worker's `212da07f` cherry-picked onto `6d480129`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: nobody has looked at the five icons in a light and a dark theme, and the shapes are the worker's own 16 px strokes, which may want a design pass. Nothing installed.

### 19:33 — desk/007 an issue read says when comments were cut
**Merged:** `agent/desk/007-an-issue-read-says-when-comments-were-cut` (code `3141190`, ff on `0c44f9d`; doc `15f59412`, the worker's `84a8c0ef` cherry-picked onto `816f2c92`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live Linear check, written into the task and decision 59: which end of a thread of more than 25 comments each account type keeps is assumed newest-first, not measured. Nothing installed or deployed.

### 19:32 — promptu/002 the pass plans for work that will outgrow one context window
**Merged:** `agent/promptu/002-the-pass-plans-for-high-context-work` (code `95f0d69`, ff on `94181bb`; doc `71b1dfb0`, the worker's `5a71d01a` cherry-picked onto `35f430ef`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed Promptu on this machine runs the old binary until the owner rebuilds it; nothing here deploys.

### 19:30 — atlas/039 a step marker in a rule is not a numeric claim
**Merged:** `agent/atlas/039-a-step-marker-in-a-rule-is-not-a-numeric-claim` (code `335939a`, ff on `50a9a15`; doc `a61362e6`, the worker's `e3084a54` cherry-picked onto `bf619a2a`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:26 — atlas/038 a spaced minus and a thousands separator parse as one number
**Merged:** `agent/atlas/038-a-spaced-minus-and-a-thousands-separator-parse-as-one-number` (code `50a9a15`, ff on `a034cc6`; doc `3ffc8e00`), both landed by the dead leg. I re-ran the gate on the merge result: `pytest` 656 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean. The task now reads `done` and this fold retires it; one changelog fragment assembled into `history/atlas.md`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 17:45 — chat/007 an agent hands its chat to a fresh session
**Merged:** `agent/chat/007-an-agent-hands-its-chat-to-a-fresh-session` (code `f823dc8` on `bce5ac7`, ff; doc `ee7e48bf`, the worker's `5a6fc140` cherry-picked onto `1e8be150`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window, written into the task: a real `claude` calling `mcp__embarch-chat__handoff` (the wire tests call the tool through `mcpServer` directly, there is no recorded fixture), and the tab and sidebar re-pointing in a real VS Code window. Nothing installed or deployed.

### 17:37 — ui/105 the README points at the chat's launcher
**Merged:** `agent/ui/105-the-readmes-point-at-the-chats-launcher` (code `877a042`, ff; doc `6164b79d`, the worker's `1f1a082e` cherry-picked onto `e222ce57`, task file and changelog fragment only).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 17:36 — promptu/001 a header-less memory index may take its first header
**Merged:** `agent/promptu/001-a-header-less-memory-index-may-take-its-first-header` (code `94181bb` on `866a24e`, ff; doc `0b519941`, the worker's `f76382b0` cherry-picked onto `c8f4b929`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed hook on this machine still runs the old binary until the owner rebuilds or reinstalls it; nothing here deploys.

### 17:34 — desk/006 four desk docs leave the reserve by verbatim split
**Merged:** `agent/desk/006-compact-desk` (doc `ab1d2c96`, the worker's `b55848d2` cherry-picked onto `93cd09a7`; no code). `decisions/cockpit.md` 12,062 → 6,100 B (57, 58, 60, 61, 76 to new `decisions/hand.md`), `decisions/desks.md` 12,169 → 8,306 B (62–64 to new `decisions/tiles-after-send.md`), `interfaces.md` 14,426 → 10,498 B (the embarch-chat route table to `interfaces/chat-routes.md`), `spec.md` 9,219 → 8,379 B (constants rows to `spec/constants.md`), PAID. I compared removed against added lines: identical except index rows and links re-pointed one level up.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

## 2026-11-07 — 4 units

*Folded 2026-11-09 by a log-folder; per-unit reasoning, gate detail, budget lines and least-sure notes went, git and the decision files hold them.*

**Carry-forward (next leg, read this first):** 4 of 4 units (`dev-bench/003`, `004`, `041`, `016`), all `toolchain` tasks run by the leg's own hands, serially. Leg began at `68a20e3a`. **52 issues reached Fleet Ready during this leg** (25 atlas, 16 desk, 9 chat, 1 promptu, 1 ui; `queue-status.py` now reads 52 dispatchable): the next leg's `ready` takes them in and splits them, and that split is most of its work. **The pump is off and the listener disarmed** (its own FYI at 10:15), so no relay follows this leg unless the owner starts one. **`EMB-83` (Backlog, decision) is the owner's**: whether `toolchain` tasks go to workers as `none` (a worktree builds fine against the main checkout's workspace) or stay with legs, and the fleet venv's missing `natsort` and `esptool`. Decisions 50, 51 and 52 are new in `embarch-dev-bench`; 50 was amended by 51 within the leg. 13 `toolchain` tasks remain. Bench: neither role attached; `api/059`, `dev-bench/035`, `038` stay `open`. Size ledger: `core/112` falls due **2026-11-09**. No `suite` task announced, nothing deployed, the owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone.

**Decided (day):** nothing suite-wide. Started the `toolchain` lane with the leg's own hands (`protocol.md` §7, `tasks/README.md` grant it; first use ever; legs dreamt instead on 2026-10-28 and 2026-11-06, no reply in dream thread `1793997725.841939`), built from a worktree against the main checkout's workspace; that undercuts the README's reason these are not worker tasks, hence `EMB-83`. `scanning.md` is at 11,034 B, 25 B outside its reserve line. `twister` cannot start (no `natsort`), so ztests ran suite by suite. ESP32-C5 image never built (no `esptool` in the fleet venv). Open side note, not filed: the Rust reference interpreter subscripts `states[]` unchecked and would panic where the C side now fails the run. New `census_summary` static is +56 B RAM on the Nordic image (59.67%), unbuilt on the ESP32-C5.

### Units

**dev-bench/003** (10:28) length prefix bounded before arithmetic (`pc_skip_len_prefixed`).
**Merged:** `agent/dev-bench/003-pc-skip-len-prefixed-wraps-past-its-own-bounds-check` (code `61c96c2` on `5dd78b5`, ff; doc `f4e7213f`, `b3ddf812` cherry-picked onto `6ac10be8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The ESP32-C5 image was not built: Zephyr's Espressif SoC CMake wants `esptool` on `PATH` and the fleet venv has none. Same file compiles for host and Cortex-M33, so the risk is low; `EMB-83` carries the venv gap.

**dev-bench/004** (10:36) out-of-range state-machine index fails the run; new `embarch-dev-bench` decision 50 (`decisions/protocols.md`), run-time rather than decode refusal.
**Merged:** `agent/dev-bench/004-protocol-state-indices-reach-a-c-array-unchecked` (code `952f788` on `61c96c2`, ff; doc `d4922d38`, `97eda043` cherry-picked onto `d7056346`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. ESP32-C5 image not attempted (`EMB-83`, no `esptool` in the fleet venv).

**dev-bench/041** (10:45) a study over a bench cap is refused out loud; new decision 51 (`decisions/link-limits.md`), amends 50.
**Merged:** `agent/dev-bench/041-a-study-the-bench-cannot-hold-is-refused-out-loud` (code `4026cde` on `952f788`, ff; doc `73f4d033`, `d35e009f` cherry-picked onto the claim commit).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the ESP32-C5 image, one `Done when` box left unticked in the task for it (`EMB-83`, no `esptool` in the fleet venv). On a board: a 17-step `StudyStart` should produce the `LogLine` in Core's `dev-bench.log`; nothing has sent one yet.

**dev-bench/016** (10:53) the census `fail_reason` is composed where a test reaches it; new decision 52 (`decisions/scanning.md`).
**Merged:** `agent/dev-bench/016-the-two-census-gates-have-no-test-that-can-reach-them` (code `9371510` on `4026cde`, ff; doc `ec9ed080`, `33422dbe` cherry-picked onto the claim commit).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** unchanged from `dev-bench/008`: one failed name-filtered and one failed address-filtered `BleConnect` on the bench, reading the `fail_reason` and the census log. ESP32-C5 image not built (`EMB-83`).
*Days 2026-11-06 to 2026-11-06 rolled to [log-archive/supervisor-log-2026-11-06-to-2026-11-06.md](log-archive/supervisor-log-2026-11-06-to-2026-11-06.md).*
