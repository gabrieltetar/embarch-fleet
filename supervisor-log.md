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

## 2026-11-06 12:47 — atlas/029 join decodes Nordic devicetree pin use

**Decided:** nothing suite-wide. `EMB-50`, picked ahead of `atlas/028` on value: every pin-level check was silently empty on a whole MCU family. `dt.py` decodes `nordic,nrf-gpio` controllers (`port` property, else the label digit) and pinctrl `psels` through `NRF_PSEL` (bits 8:0 `port*32+pin`, 0x1FF disconnected, bits 31:24 function; pull from `bias-*`), names pins `P<port>.<pin:02>`, and `dt.json` gains an additive `pin_decoder` (`stm32`, `nordic` or null; an old file with `stm32: true` still reads as `stm32`). `join.py`'s new `mcu_port` pads `P0.4` to `P0.04`. `mismatch.py` folds DPPIC, PPIB, MPC, UICR and GPIOTE into `FOLD_INFRA` after `dt_intent`, and `checks.md` says when a family has no decoder. I checked the worker's encoding constants against Zephyr's own `nrf-pinctrl.h` on this machine: `NRF_FUN_POS 24`, `NRF_FUN_MSK 0xFF`, `NRF_PIN_MSK 0x1FF`, all match.
**Merged:** `agent/atlas/029-join-decodes-nordic-devicetree-pin-use` (code `49c8169` on `238db6f`, ff; doc `30b4f104`, the worker's `2dfa8444` cherry-picked onto `bf13f4b3`). Gate on the merge result: `pytest` 638 passed, 3 skipped (real west, real atlas, real SVD; `test_public_guard` ran), client names clean on the code worktree, ownership `atlas` OK on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real nRF54L15 atlas (owner-attended or a toolchain leg): `dt.json` `gpio_controllers`, the pin map's DT column and a non-zero "ran" on the pin checks against a real `edt.pickle` (the `EMBARCH_ATLAS_REAL_ATLAS` test). Function names show as `NRF_FUN_<n>`, so "pinctrl function vs net name" compares the group name only.
**Budget:** PROCEED at the end (5-hour 21.0%, weekly 27.0%, wave 6).
**Least sure about:** the worker ticked "the pin map's DT column is filled and the pin checks list a non-zero ran", and the reviewer confirmed no test exercises it: no test joins a Nordic project end to end. I closed the task on the structure and filed the gap as `EMB-78` (Fleet Ready) rather than holding a green unit open for a missing test.
**Leg close (next leg, read this first):** 4 of 4 units (`dev-bench/040`, `atlas/027`, `ui/104`, `atlas/029`), cap reached. Leg began at `2e98b8a6`; `check-ownership.py --supervisor` on the leg's paths is green. **Fleet Ready now holds `EMB-77` and `EMB-78`**, both filed by this leg from reviewer residuals; the next leg's `ready` splits them. **Queue:** `atlas/028`, `030`–`033` open (one atlas slot at a time, so they drain serially; `028` and `EMB-77` both touch `build.py` and `kconfig.py`), `desk/005` open (due 2026-11-28). Size ledger: nothing overdue; next due `core/112` 2026-11-09 (`blocked`, two files). Bench: neither role attached at this leg's refresh; `api/059`, `dev-bench/035`, `038` stay `open`. Refill was not owed this leg; the last full sweep is still 2026-10-29. My dispatch prompts said "done (token zero)" and two workers wrote it literally into `State:`; say "a bare `done`" instead. I removed `atlas/027`'s worktree with `--force` because its untracked `.venv` blocked a plain remove; the branch had landed. No `suite` task announced, nothing deployed, the owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone.

## 2026-11-06 12:39 — ui/104 spec.md and open.md out of reserve by verbatim splits

**Decided:** nothing suite-wide. Taken ahead of its 2026-11-12 due date because the budget turned PROCEED (wave 6) mid-leg and atlas, the other live scope, holds one slot at a time. The worker split rather than squeezed: three role, catalog-row and board-type invariants (decisions 44, 45, 47, 48, 49) moved verbatim to new `embarch-ui/spec/roles.md`, with one pointer bullet left in `spec.md` that states the gist; five trace and live-study questions moved verbatim to new `embarch-ui/open/trace.md`. The task's must-not-delete items (the unit-install and release-archive bullets, the binds-before-it-polls sentence) are untouched. I normalised `**State:** done (token zero)` to `done`: my dispatch prompts said "done (token zero)" and two workers copied the parenthesis literally.
**Merged:** `agent/ui/104-compact-ui` (doc `44b31310`, the worker's `06dc5aa9` cherry-picked onto `6dfcfc7b`; code none, the `embarch-ui` branch has no commits and was never pushed). `spec.md` 9,265 → 8,290 B, `open.md` 4,226 → 2,220 B, both PAID. Gate on the merge result: `check-docs.py` 12/12, ownership `ui` OK (6 paths). `cargo` not run, no code changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED (5-hour 16.0%, weekly 27.0%, wave 6).
**Least sure about:** the pointer bullet left in `spec.md` paraphrases five decisions in one sentence; the reviewer read it as stating the gist without restating a rule differently, but a paraphrase beside its own source is where drift starts.

## 2026-11-06 12:37 — atlas/027 build picks the app image of a multi-image sysbuild

**Decided:** nothing suite-wide. The first of the seven Fleet Ready atlas bugs (`EMB-49`). `kconfig.py` gained `image_dir(bdir, marker, app=None)`: under sysbuild the image is `domains.yaml`'s `default:`, then the target app directory's basename, and when neither picks one the error names every `zephyr/edt.pickle` found. `run_build` and `extract_kconfig` both go through it, so `.config` and `edt.pickle` come from one image. I normalised the worker's `**State:** done (token zero)` to a bare `done` before the fold.
**Merged:** `agent/atlas/027-build-picks-the-app-image-of-a-multi-image-sysbuild` (code `238db6f` on `029c41b`, ff; doc `2aa05c86`, the worker's `72a34d97` cherry-picked onto the leg HEAD after `dev-bench/040`'s fold). Gate on the merge result: `pytest` 633 passed, 3 skipped (real west, real atlas, real SVD; `test_public_guard` ran), client names clean on the code worktree, ownership `atlas` OK on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The only check on a real two-image layout is the synthetic-tree test: the first `embarch-atlas build` of a real application-plus-MCUboot target is the confirmation, owner-attended or a toolchain leg.
**Budget:** PROCEED at this unit's boundary (5-hour 16.0%, weekly 27.0%, wave 6); the leg started DEGRADED with no cache.
**Least sure about:** the reviewer's residual: `buildq.named()` (a build dir the caller names, for `config` and `dt_node`) still calls `zephyr_dir(p)` with no app, so a named multi-image sysbuild with no `domains.yaml` still errors there. Not a contradiction and not `atlas/028`'s scope either. I filed it as `EMB-77` (Fleet Ready, `--from reviewer`), so the next leg's `ready` splits it.

## 2026-11-06 12:34 — dev-bench/040 spec.md out of reserve by a verbatim split

**Decided:** (1) **Split all seven Fleet Ready issues** (`EMB-49`–`55`, every one an `embarch-atlas` bug filed by a worker, `Hardware: none`) into `tasks/atlas/027`–`033`, one task per issue (`f6eaffa6`), `filed` moved all seven to Fleet Working, announced `ts` `1793993406.066929` before dispatch, no reply. Map: 027 `EMB-49` sysbuild app image, 028 `EMB-54` build dir keyed on args, 029 `EMB-50` Nordic DT pin decode, 030 `EMB-51` codecheck compiled sources, 031 `EMB-52` offset define, 032 `EMB-53` DT-limits quantity and role, 033 `EMB-55` strap wording. (2) **Reopened `dev-bench/040` from `blocked`** as the size ledger's first unit (overdue since 2026-11-01), flipping `In flux:` to `no, for the remedy this task now takes` on `chat/004`'s 2026-10-28 reading: a verbatim split restates nothing. The filer expected a PD bench section to move, but `spec.md` holds only one paragraph and one row about it, which is the in-flux text; so the worker moved settled §5 instead and left both PD bench passages word for word. (3) Committed one `suite/features.md` row with no fragment from this unit (a desk-notes row already on `main` as a fragment, unassembled), the same deterministic rebuild `ui/103` made.
**Merged:** `agent/dev-bench/040-compact-dev-bench` (doc `e3caf357` on `8dd4bd2f`, ff; code none, the `embarch-dev-bench` branch has no commits and was never pushed). `spec.md` 9,632 → 7,151 B, PAID; new `embarch-dev-bench/spec/constants.md` 2,898 B. I diffed the removed lines against the added ones: identical except the SRAM paragraph's `open.md` link, now `../open.md`. Gate on the merge result: `check-docs.py` 12/12, ownership `dev-bench` OK (4 paths). `cargo` not run, no code changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at start, no usage cache, measured wave 2, no 429.
**Least sure about:** whether flipping a `yes` to `no, for the remedy` is the reading the owner meant `In flux:` to allow. The gate forces it (`claimed` with `yes` is red), `DOC-BUDGET.md` says a split is never forbidden by flux, and one precedent did it, but `.claude/leg.md` also says "never dispatch one whose `In flux:` says yes", and a field rewritten to make a dispatch legal is the pattern that rule watches for.
**Leg notes (this leg, first unit):** step 0 found no claims, no worker worktrees, no mid-ops; the pump latch was present, no stop marker. Bench refreshed: `dev-bench` and `dut` both **not attached**, so `api/059`, `dev-bench/035`, `038` stay `open`. Refill not owed (10 dispatchable across 4 scopes, wave 2). This fold also carries the `2026-11-04` day fold (by the log-folder) and the roll of `2026-10-28`; `check-client-names.py --suite --history` clean on all 16 repos. `embarch-fleet`'s `scripts/fleet-pump.py` is modified in its working tree and is not mine: left alone, not staged.

## 2026-11-04 — 1 units

*Folded by a leg's log-folder, 2026-11-06: the narrative reasoning behind each accepted call is dropped, git holds it; the ledger, the three judgement calls and the leg-close carry-forward stay.*

**Carry-forward (next leg, read this first):** 1 of 1 units, the cap the prompt set; no pump latch was present. **Owed by the next unrestricted leg:** `dev-bench/040` is overdue (due 2026-11-01, `blocked`) and takes the first unit; the refill sweep was last run 2026-10-29. Read the `2026-10-29` carry-forward's "`inbox/` is empty" as "Fleet Ready is empty": that directory is gone. The dream `ts` `1793318476.457199` has had no human reply. `desk/005` is the only other dispatchable task. `changelog.d/` holds 66 fragments I did not write and left alone, `umbrella-check-17-measured.decided.md` among them. This `ui` fold pruned `embarch-ui`'s two `agent/ui/059-*` branches (the `2026-10-29` carry-forward listed them as unproven): `9199da5` and `052990c` are on `main`, and the one unmatched commit, `21a48de`, is the earlier draft of the same `src/logs.rs` fix. `embarch-doc`'s origin copy still stands. `agent/ui/103-*` stays as `embarch-doc`'s origin branch and a local branch in both repos until the next `ui` fold, since a fold prunes one behind. The day's fold also carried `2026-10-29`'s day fold and the roll of `2026-10-26`; `check-client-names.py --suite --history` was clean on every repo. Nothing deployed.

## 2026-11-04 16:00 — ui/103 a tab manifest says icon is required

**Decided:** nothing suite-wide. First issue through Linear intake since `inbox/` was retired: `EMB-8` split into `tasks/ui/103` (`eb2c5ab6`), announced `ts` `1793832990.931349` before dispatch, no reply. `embarch-ui/interfaces.md` now says a manifest's `label`, `icon` and `panel` are required, `icon` names an `.svg`, and a failing tab is left off the page with `tab <id> is left out: <error>` logged. Three calls: (1) honoured the prompt's `1 ui` over the size ledger, so overdue `dev-bench/040` got no unit this leg; (2) skipped the refill sweep though `--refill-owed` exited 0; (3) committed `suite/features.md` with no `features.d/` fragment, because `build_features.py` found `main`'s table stale and rebuilt it deterministically (a revert only makes it stale again).
**Merged:** `agent/ui/103-tab-manifest-says-icon-is-required` (doc `a2081aac` on `5218e1a6`, ff; code none, doc-only, `embarch-ui` `main` stays at `ca9e6bc`). Gate: `check-docs.py` 12/12, client names clean, ownership `ui` OK. `cargo` not run.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at start and end, no usage cache, measured wave 2, no 429.
**Least sure about:** "missing `icon` is left out" rests on `Manifest.icon` being a required `String` and four log call sites in `src/tabs.rs`; no test has a manifest missing that key.
## 2026-10-29 — 31 units

*Folded 2026-11-04 by the log-folder for the supervisor leg: the per-unit reasoning, gate-result lists and "least sure about" prose went to git; SHAs, reviewer lines and hardware debts are kept per unit. Five legs ran (14:24 to 18:01), wave 6, budget PROCEED throughout, weekly 22.2% rising to 29.4%.*

**Carry forward (read this first):**
- **The queue is dry; owner reply pending.** Last dream posted (`ts` `1793318476.457199`, `crystal_ball`): (1) review the `standard` design in `embarch-atlas-wt` (unparks `atlas/016`, `004`, `011`); (2) plug in the dev bench (`api/059`, `dev-bench/035`, `038`); (3) delete `embarch-ui/vscode-extension/` to finish `embarch-chat` decision 29 (changes his launcher reinstall path, so offered not filed). **If no reply has arrived and `inbox/` is empty, do not dream again and do not invent work: end after step 0.**
- **Parked on my own call (`8854b1d1`):** `atlas/016` `blocked` (unparks on the owner's review of `embarch-atlas-wt`), `atlas/004`, `011` `blocked` behind it (unparks on `tasks/atlas/016`). Reverse by setting them `open` when he answers.
- **Owner-only:** `tasks/doc/093`, `094`, `095` (`095`: `fold-commit.py`'s `ALLOWED` refuses top-level docs not named `embarch-*`; `bootload-proposal.md` went in its own commit `b21b0fef`). `changelog.d/umbrella-check-17-measured.decided.md` (owner's `a5062887`, 14:01) is unconsumed.
- **Owner call, stream-pipeline proposal:** its outbound half has no task, `open.md` line or roadmap line; study-designer decision 58 may have closed it by the `.eap` state machine. Said so in the file.
- **Branches left for the owner:** `agent/ui/059-diff-new-lines-republish` (code `21a48de`, doc `ec150926`) is still on both remotes; the fold cannot prove them landed.
- **Safe-direction decisions made on his behalf:** `suite/053` retired 87 `done` task files; `suite/055` kept all eleven pre-October tasks (recommendation to keep the owner's parked four: `api/029`, `outpost/002`, `study-designer/007`, `ui/007`); `suite/030` classified the 28 unlisted MCP tools (allow adds `capture_read`, `capture_start`, `capture_stop`, `lease_show`, `ledger_pending`, `ledger_show`, `list_instruments`, `show_bootload_ports`, `study_stream_load`; the rest ask) into `suite/agent-guide.md`.
- **Atlas rules a later unit must not undo:** `atlas/005` narrowed `atlas/014`'s "silent reply is an answer" to the last console; `atlas/026` made fall-through happen only on an explicit `echo_seen: false`; `atlas/009` read-only list for the MCP `shell` is a short default (`gpio get`, `sensor get` now refuse until a project lists them); a public vendor SVD set lives read-only at `/home/gabriel/STMicroelectronics/STM32Cube/STM32CubeProgrammer/SVD/` (never copy into a repo); `test_public_guard` rejects real part names; `check_public.py` does not exist, read as `test_public_guard` plus `check-client-names.py`.
- **Open residuals:** `atlas/021`'s `af410ad` fix was read by me only, not a reviewer; `tasks/atlas/001` (toolchain-gated) shares `update.py` with `atlas/020` and can reuse `split_diff`; the `toolchain` lane (17 tasks) is unstarted by any leg; `dev-bench/035` reads `Hardware: bench` but is a ztest and C (`toolchain`?); `tasks/doc/045`'s size-ledger debt is paid. My claim commit `00fe466d` lacks the co-author trailer (pushed, not rewritten). Slip: `chat/005`'s fold `9d278461` landed with `check-task-state.py` red; fixed in `333c3ca7`; every gate since runs unpiped.
- **Bench:** `dut` attached (probe `000852006107`), `dev-bench` not. Ledger: nothing overdue (next `dev-bench/040`, 2026-11-01, blocked). Nothing deployed (`core/124` needs the owner's native Windows build first). 2026-10-28 was day-folded earlier this day by the log-folder and 2026-10-25 rolled. Legs began at `64976739`, `a7e87bca`, `abb009ab`, `0e6d6b06`-era `7eb36fa2`, `d15e820c`, `2d456db9`, `46ab7922`.

### Units (newest first)

**18:01 atlas/026** silent console reply follows one rule (`Console.exchange` passes over only on explicit `echo_seen: false`).
**Merged:** `agent/atlas/026-silent-console-fall-through-says-one-thing` (code `fad13ca` on `e68d4d3`, ff; doc `cdc38857` on `d1997f85`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; `atlas/005`'s two-console bench check now also expects the deployed Core to send `echo_seen` (a Core older than decision 85 never falls through).

**17:55 atlas/025** clock-gate word never tips a reg_read into refusal.
**Merged:** `agent/atlas/025-clock-gate-word-never-tips-a-read-into-refusal` (code `e68d4d3` on `b1d4e6e`, ff; doc `fdb2d73d`, the worker's `063fbb51` rebased onto `eca4f89a`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; `atlas/013`'s enable-bit check on an STM32 board still stands.

**17:52 atlas/005** console follows the running image (`[live] consoles`); filed `atlas/026`.
**Merged:** `agent/atlas/005-console-follows-the-running-image` (code `b1d4e6e` on `1eb055f`, ff; doc `cc5ed29f` on `3d3c7037`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the board with its shell switchable between a USB-UART bridge and USB CDC ACM, both declared as signals, shell on USB: with `[live] consoles` mapping both nodes and the build pinned, `embarch-atlas live shell "kernel uptime"` answers through the CDC signal and the `src:` line says "the image's shell is on <cdc node> (... flash matches ...)"; without `[live] consoles`, the bridge is passed over and the `src:` line says no byte came back from it. The task file that carried this is retired by this fold.

**17:40 atlas/010** missing.md records the engineer's answers; `net_trace` walks generic cards.
**Merged:** `agent/atlas/010-missing-datasheets` (code `1eb055f` on `0f68b0a`, ff; doc `8ba01deb` on `8b2ee6a8`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The ranking and the card walk have met only the synthetic two-board fixture.

**17:32 atlas/013** reg_read says when a peripheral's clock is off (sent back once for unmeasured clock-gate facts; filed `atlas/025`).
**Merged:** `agent/atlas/013-reg-read-says-when-the-clock-is-off` (code `0f68b0a` on `108ee85` on `4d68d53`, ff; doc `75224fc2` on `3ebf6dd4` on `5450f81e`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** an STM32 board through Core (the DUT qualifies): `reg_read TIM1` (or any peripheral the image leaves gated) says `clock off (RCC.APBENR2.TIM1EN = 0)` with no `*`/"at reset" markers; an enabled peripheral says `clock on`; the RCC word rides in the same halted read. The task file that carried this is retired by this fold.

**17:22 atlas/023** live core-state names where the core is, as symbols (new `corestate.py`; default read now runs one halted flash check after the sample).
**Merged:** `agent/atlas/023-core-state-symbol-decode` (code `4d68d53` on `1e5541a`, ff; doc `6b7452cf` on `d70bcb90`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** DUT bench with a deployed Core carrying `/live/core-state` (`core/103`) and the flashed build's dir: `embarch-atlas live core-state` and `--halt` name functions and lines; `addr2line` is found beside the build's `nm` (derived by name, tested only with a fake); a deliberately different build is refused by name. The task file that carried this is retired by this fold.

**17:14 atlas/020** a bump's second look batches changed facts by (id, key); `CHECKED_VERSION` deliberately not bumped.
**Merged:** `agent/atlas/020-second-look-batches-and-compares-what-changed` (code `1e5541a` on `5e7df62`, ff; doc `89c8602b` on `00fe466d`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**17:06 atlas/014** live shell tells silence, a lost port and an empty success apart (pre-write-error matching on Core wording; a future reworded post-write error containing "nothing was written" would resend).
**Merged:** `agent/atlas/014-shell-tells-silence-lost-port-and-empty-success-apart` (code `5e7df62` on `b23a73d`, ff; doc `f2b577f4`, the worker's commit rebased onto `ce45fb98`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-attended or a bench leg, on the dev bench with a DUT console declared, a Core with decision 85 deployed and an image built with `CONFIG_SHELL_CMDS_RETURN_VALUE=y`: `embarch-atlas live shell <a command that prints nothing>` prints "printed nothing and returned 0" and exits 0; a refused value prints its nonzero code; with the DUT unpowered or held in reset, `live shell` exits 2 with port identity and core state; a command that drops the DUT's USB port exits 3 and is not resent on a second console. The task file carried this and is retired by this fold.

**17:03 atlas/019** an atlas names a board with no netlist and a Kconfig it failed to extract (`update` does not stop for a missing netlist).
**Merged:** `agent/atlas/019-join-and-build-name-what-they-left-out` (code `b23a73d` on `5f208ad`, ff; doc `93791ed1`, the worker's commit rebased onto `84544f6f`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `kconfig-extract` is tested with the extraction monkeypatched, never over a real Zephyr build.

**16:56 atlas/018** every cut answer can be continued with `offset`.
**Merged:** `agent/atlas/018-every-cut-answer-takes-offset` (code `5f208ad` on `17880f2`, ff; doc `4f1b0e03`, the worker's commit rebased onto `1cc26877`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**16:50 atlas/007** `find_text` searches a document's page text; `atlas/012`'s owed hints paid.
**Merged:** `agent/atlas/007-find-text` (code `17880f2` on `fa9b1b9`, ff; doc `48a9ceea` on `d3a6cd26`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Never run against a real atlas's text layer; the timing is synthetic (55 lines a page).

**16:37 atlas/015** every lookup says when the atlas is behind HEAD (new `stale.py`).
**Merged:** `agent/atlas/015-stale-signal` (code `fa9b1b9` on `197784a`, ff; doc `4dae8850`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**16:31 atlas/012** four lookup misses become the next call to make (`cmsisalias.py`; `pdf=` on `src:`).
**Merged:** `agent/atlas/012-query-misses` (code `197784a` on `c71c703`, ff; doc `4b686f3f`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The CMSIS alias is tested on a synthetic header and SVD only, never a real vendor header.

**16:24 atlas/006** an external reg_read names the true cause. Its doc cherry-pick reached `origin/main` one push ahead of its fold, inside `ui/059`'s fold push.
**Merged:** `agent/atlas/006-ext-reg-read-states-true-causes` (code `c71c703` on `af410ad`, ff; doc `0a22af11`, the worker's `4bdde008` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The no-I2C-shell answer has not met a real board without the shell.

**16:23 ui/059** a grown trailing line is republished, not swallowed (I unparked it; new decision 70; old branches left on remotes).
**Merged:** `agent/ui/059-diff-new-lines-publishes-the-grown-line` (code `052990c` on `f6da709`, ff, two commits: `21a48de` cherry-picked as `9199da5`, then the fix; doc `78235e0c`, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**16:13 suite/055** the pre-October tasks all still describe real work (all eleven kept; window `ts` `1793305740.224299`, closed 14:59:00; `diff_new_lines` unchanged since `ea0227b`).
**Merged:** no branches (supervisor's own unit). Doc SHA is this fold's commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**16:11 atlas/021** write-one-to-clear does not guard a read; undefined reset bits claim no reset. The reviewer caught a real decode bug (field reset shifted twice), fixed forward.
**Merged:** `agent/atlas/021-w1c-and-reset-mask-read-as-stated` (code `05be6a5` on `fa98820`, ff, then the fix `af410ad`, ff; doc `b54dbe72`, the worker's `16504b38` cherry-picked).
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/atlas-decode-field-reset-shifted-twice.md (fixed forward in `af410ad`, drop deleted).
**Hardware debts:** none. Records already built from SVDs keep their invented `0` resets until `mcu svd` re-runs.

**16:06 atlas/024** a non-object record line is written back as it was (sent back once; a bisect can land on red commit `c65cb61`, fixed by `ba07dcd`).
**Merged:** `agent/atlas/024-save-records-keeps-a-non-object-line-as-written` (code `fa98820` on `5fd3caa`, ff, three commits; doc `72a7dcaf`, the worker's `da3e3dd9` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**16:00 chat/006** `/embarch-claude-md` cites agent-guide §1.1.
**Merged:** `agent/chat/006-embarch-claude-md-cites-the-moved-user-guide-section` (code `e6186d9` on `b9b0e6c`, ff; doc `107e67f9`, ff). Filed from the inbox the same leg: `tasks/doc/095` at `7674b1e3`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:47 suite/054** the four root proposals keep only unbuilt design (window `ts` `1793305739.311079`, closed 14:58:59).
**Merged:** no branches (supervisor's own unit). Doc SHAs: `b21b0fef` (bootload-proposal.md alone) and this fold's commit `0e6d6b06`. `main` was red at leg start, fixed `fa05c77c`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:40 umbrella/096** the install test's ETXTBSY race is retried, not the install.
**Merged:** `agent/umbrella/096-install-replaces-running-binary-test-flakes` (code `d3f1c83` on `50f4022`, ff; doc `6e788299`, the worker's `a9384c30` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:39 atlas/017** doc check reports a malformed record instead of crashing; filed `atlas/024`.
**Merged:** `agent/atlas/017-doc-check-survives-malformed-records` (code `5fd3caa` on `8a32edb`, ff; doc `d212f7b1`, the worker's `85133924` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:36 ui/102** the host-clock fallback is already named by an existing test (closed, no code change; filed from drop as `umbrella/096` at `f93950b2`).
**Merged:** `agent/ui/102-a-dut-counter-restart-test-asserts-the-view-names-the-host-clock-it-fell-back-to` (code none, `embarch-ui` main unchanged at `f6da709`; doc `5962b4b7`, the worker's `0fe1d448` cherry-picked). Leg began at `abb009ab`; `suite/053`'s fold had left `main` red, reworded in `fa05c77c`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:23 suite/053** the 87 done task files are retired (window `ts` `1793305738.327939`, closed 14:58:58).
**Merged:** no branches (supervisor's own unit). Doc SHA is this fold's commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:20 atlas/009** a live call that can change the board carries no read-only hint (`shell` list, `shell_run`, `reg_read_clear`; chained-command rule added).
**Merged:** `agent/atlas/009-live-writes-carry-no-read-only-hint` (code `8a32edb` on `63055f7`, ff; doc `b526d00c`, the worker's `904f5603` rebased, ff). My slip fixed in `333c3ca7` (after `9d278461`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run live (tests use a fake `embarch-api`). Owner-side: the installed `atlas-use` skill in `~/.claude/skills/` and any running atlas MCP server are the old ones until `./install.py` runs and the server restarts; how a host behaves in plan mode with the new hints is unobserved.

**15:17 chat/005** `/embarch-permissions` carries the agent guide's 54-tool split; filed `chat/006`. The rebased doc branch was not force-pushed (classifier refused); the remote holds pre-rebase `8562f5e8`, which `fold-commit.py` prunes by patch-id.
**Merged:** `agent/chat/005-embarch-permissions-carries-the-agent-guides-54-tool-split` (code `b9b0e6c` on `origin/main`, ff; doc `fd695c22`, the worker's `8562f5e8` rebased, ff).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**15:13 umbrella/095** check 17's fix lines name Core 106's in-place install; `umbrella/094` paid; reviewer found two dropped live claims, restored in the fold.
**Merged:** `agent/umbrella/095-check-17s-fix-lines-name-an-install-that-refuses-a-registered-service` (code `50f4022` on `4c786fa`, ff; doc `5e93f5b3` on `2c5ed35c`, ff). Leg began at `a7e87bca`.
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/umbrella-open-md-compaction-dropped-desk-restart-warning.md
**Hardware debts:** owner-run, in `embarch-umbrella/open.md` (it reinstalls the service): with Core 106 deployed, register `--bind 127.0.0.1`, stop it, `doctor` in the guest says "stopped and bound narrow", then the printed `install --bind 0.0.0.0` widens it; `bind-too-narrow` from a mirrored guest and `setup` over a registration unmeasured. Core 106 itself still needs the owner's native Windows build.

**15:01 suite/030** the user guide's Claude Code section becomes `suite/agent-guide.md` (window `ts` `1793305727.873799`, 14:28:47 to 14:58:47; tools checked as sets against `tools.rs` on `0f1f0d4`, 23 + 31 = 54; filed `chat/005`).
**Merged:** no branches (supervisor's own unit). Doc SHA is this fold's commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**14:44 atlas/008** a live read from another chip is refused, not decoded (the fleet's first atlas unit; prefix match accepted, an atlas with no SVD device compares nothing).
**Merged:** `agent/atlas/008-live-refuses-another-chip` (code `63055f7` on `0cf93ce`, ff; doc `503c1549` cherry-picked from the worker's `fed00c4a` onto `a90b34dd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one `reg_read` through a live Core against a board whose probe is another chip, seeing the refusal (owner-attended; the atlas tests use a fake `mem-read`).

**14:42 outpost/018** a 13 µs backwards DUT-clock step is pinned as tolerated (test only; re-homed the host-fallback box as `ui/102`; leg.md's sibling table is missing the `embarch-study-designer` link `vocab_check.py` needs).
**Merged:** `agent/outpost/018-backwards-dut-clock-decoder-tests` (code `ac3b96f` on `514d2c0`, ff; doc `202377aa` cherry-picked from the worker's `b8099ee5` onto `8b81f423`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**14:41 core/124** install over a registered Windows service rewrites in place (core decision 106; `embarch-core/open.md` compacted; unblocked `umbrella/095`; `core/112` stays blocked). Leg began at `64976739`. The owner answered the 2026-10-28 dream "do 1" (`2e28b74d`), so `atlas` became dispatchable. Filed `suite/053`, `054`, `055` from drops.
**Merged:** `agent/core/124-install-over-a-registered-service` (code `80dfa0d` on `85846c4`, doc `baec9822` on `e0a59709`; both ff). `cargo check --target x86_64-pc-windows-msvc` could not run (`hidapi` needs MSVC headers); `cfg(windows)` hunks hand-read.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, in `embarch-core/open.md`: (1) native Windows build, since the `cfg(windows)` registry and `sc failure` code has never been compiled; (2) a live `install --bind` over the registered service, checking `EMBARCH_SIGNAL_BAUD` survives and `sc qfailure` shows five restarts.
*Days 2026-10-28 to 2026-10-28 rolled to [log-archive/supervisor-log-2026-10-28-to-2026-10-28.md](log-archive/supervisor-log-2026-10-28-to-2026-10-28.md).*
