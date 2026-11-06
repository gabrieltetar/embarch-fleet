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

## 2026-11-06 13:12 — atlas/031 codecheck offset define is not a register

**Decided:** nothing suite-wide. `EMB-52`. Re-landed from the last leg: its worker had finished and pushed both branches, nothing merged, so step 0 gated and landed it rather than reclaiming it. `ENCODING_TOKENS` in `codecheck.py` gained `OFFSET` and `OFS`, so a `REG_`-named define ending in one classifies as `encoding`, not `register`, and the masks after it lose their phantom positional register. The worker tested at the `classify` level only and said so in the task's Done section. I filed the reviewer's residual (below) as `EMB-79` (Fleet Ready, `--from reviewer`); the next leg's `ready` splits it.
**Merged:** `agent/atlas/031-codecheck-offset-define-is-not-a-register` (code `5685cee` on `536a098`, ff; doc `47294ae0`, the worker's `631c3dc8` cherry-picked onto `925f76fc`). Gate on the merge result: `pytest` 642 passed, 3 skipped (real west, real atlas, real SVD; `test_public_guard` ran), client names clean on the code worktree, ownership `atlas` OK on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The two mask criteria (no `reg-field-in-other-register` or `reg-mask-vs-field` against the phantom 0x05) rest on reading, not a test; `EMB-79` asks for the end-to-end excerpt test. A real `codecheck` run on the charger driver is the confirmation, owner-attended or a toolchain leg.
**Budget:** PROCEED at start (5-hour 32.0%, weekly 28.0%, wave 6).
**Least sure about:** a real offset-calibration register named `*_REG_*_OFFSET` at a hex address now classifies as `encoding` and is never compared; the reviewer confirmed it, and `EMB-79` proposes keeping a hex-addressed one as `register`.
**Leg notes (this leg, first unit):** step 0 found only `atlas/031` claimed, its branches pushed; no stop marker, pump latched, no mid-ops. Bench refreshed: `dev-bench` and `dut` not attached, so `api/059`, `dev-bench/035`, `038` stay `open`. Fleet Ready empty at the top of the leg. `--refill-owed` fired on spread only; nothing in the sweep's sources changed since the 12:55 `Spread sweep` line, so I skipped it. Size ledger: nothing overdue; `core/112` due 2026-11-09. Rolled `2026-10-29` to `log-archive/`. A log-folder I spawned for `2026-11-04`'s straggler `ui/103` entry wrote a second folded heading with a duplicated carry-forward (`fold-day.py` had refused the merge as editorial); I reverted it, so that straggler still sits beside its day's folded entry, harmless. Dispatched `atlas/033` (`EMB-55`) at 13:10, ahead of `032` because a false strap conflict freezes into the mismatch report.

## 2026-11-06 13:04 — atlas/030 codecheck reads only compiled driver sources

**Decided:** nothing suite-wide. `EMB-51`. `gather_files` now seeds from the compiled driver TUs in `dt.json`'s driver lists plus their quoted includes, transitively, and no longer reads every `.c`/`.h` beside a driver. The worker used `dt.json` in place of a `compile_commands.json` reader; the reviewer confirmed `dt.py`'s `scan_sources` builds `drivers` from the compile database, so it is the same set. `classify` now returns `value` for a register-looking name ending in a quantity unit (MV, UV, NV, UA, MA, NA, MW, UW, UAH, MAH) or carrying MAX, MIN, STEP or STEPS after its first token.
**Merged:** `agent/atlas/030-codecheck-reads-only-compiled-driver-sources` (code `536a098` on `25ee47b`, ff; doc `3a793b2d`, the worker's `ea7fba1d` cherry-picked onto the leg after `atlas/028`'s fold). Gate on the merge result: `pytest` 641 passed, 3 skipped (real west, real atlas, real SVD; `test_public_guard` ran), client names clean on the code worktree, ownership `atlas` OK on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The 71-of-89 noise figure came from a real charger board's build; the first real `codecheck` run on that build is the confirmation that the list shrank, owner-attended or a toolchain leg.
**Budget:** PROCEED (wave 6) at this boundary.
**Least sure about:** the reviewer's residual: a real register whose name carries an inner MIN or MAX (a `REG_VSYS_MIN` shape) now classifies as `value` and is never compared. The task asked for this skip, so it is not filed, but it is the kind of silent miss `codecheck` exists to prevent.
**Leg close (next leg, read this first):** this leg was **ended early by the harness's hand-back enforcement**, at 3 of 4 units (`desk/005`, `atlas/028`, `atlas/030`). **`atlas/031` is claimed and its worker was dispatched at 13:03 and may still be running** (`agent/atlas/031-codecheck-offset-define-is-not-a-register`, worktrees `/home/gabriel/Github/embarch/.worktrees/embarch-atlas/031-codecheck-offset-define-is-not-a-register` and `.../embarch-doc/031-...`, claim `43574a61`). Step 0 recovery: both branches pushed with commits → re-land them through the normal gate; otherwise reclaim by the worktree's state. Its worker was told to use a generic part prefix in fixtures. Leg began at `fe57f14a`. **Queue:** `atlas/032`, `033`, `034` (`EMB-77`), `035` (`EMB-78`) open, one atlas slot at a time; no other scope is dispatchable. Spread sweep run this leg, nothing filed (see the `desk/005` entry). Size ledger: nothing overdue; `core/112` (`blocked`, `In flux: yes`) falls due **2026-11-09** and takes the first unit of the first leg on or after that date. Bench: neither role attached; `api/059`, `dev-bench/035`, `038` stay `open`. The owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone. No `suite` task announced, nothing deployed.

## 2026-11-06 12:58 — atlas/028 build dir follows the build arguments

**Decided:** nothing suite-wide. `EMB-54`. The worker chose a directory key over `-p always`: `.work/build-<target>-<commit12>-<args8>`, `args8` the first 8 hex of a sha256 over board, app and `extra_args` (`build_dir_name`, `build.py`), with the log on the same key. An unchanged rebuild keeps its directory and incremental cache; a changed argument list never meets the old cache. `kconfig-extract` and `config` read the directory from the stamp, so atlases built before this still resolve. No decision entry: the task asked for one only if the choice was not obvious from the code, and `embarch-atlas` keeps its design in the code repo's `DESIGN.md`, which the change updates.
**Merged:** `agent/atlas/028-build-dir-follows-the-build-arguments` (code `25ee47b` on `49c8169`, ff; doc `360219e2`, the worker's `3b644a00` cherry-picked onto `256de75e`). Gate on the merge result: `pytest` 639 passed, 3 skipped (real west, real atlas, real SVD; `test_public_guard` ran), client names clean on the code worktree, ownership `atlas` OK on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The CMake cache error the task names (`--sysbuild` then `--no-sysbuild` at one commit) was not reproduced; the test is on the directory key. The first real rebuild with changed `extra_args` is the confirmation, owner-attended or a toolchain leg.
**Budget:** PROCEED (5-hour 27.0%, weekly 28.0%, wave 6).
**Least sure about:** a target's old `.work/build-<target>-<commit12>` directories are now orphaned on disk rather than reused; nothing prunes `.work/`, so they stay until someone deletes them.

## 2026-11-06 12:54 — desk/005 spec.md out of reserve

**Decided:** (1) **Split the two Fleet Ready issues** the last leg filed from reviewer residuals: `EMB-77` → `tasks/atlas/034` (a named build dir picks its sysbuild image the way `atlas build` does), `EMB-78` → `tasks/atlas/035` (a Nordic end-to-end `join` test), in `bb483366`; `filed` moved both to Fleet Working; announced `ts` `1793994691.038249` before any dispatch. (2) Took `desk/005` (due 2026-11-28) now because only two scopes are dispatchable and atlas holds one slot at a time. The worker folded `spec.md`'s per-decision deploy history (56–68) into one "deployed through decision 68" line and trimmed phrasing elsewhere; every `Must not delete:` item is untouched.
**Merged:** `agent/desk/005-compact-desk` (doc `1b4883e4` on `a3327739`, ff; code none, the `embarch-desk` branch has no commits and was never pushed). `spec.md` 9,764 → 9,025 B, PAID (line 9,039). Gate on the merge result: `check-docs.py` 12/12, ownership `desk` OK (3 paths), client names clean on the code worktree. `cargo` not run, no code changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at start (5-hour 24.0%, weekly 28.0%, wave 6) and at this boundary (27.0%, 28.0%).
**Least sure about:** the folded paragraph dropped "the service unit now quotes its PATH, so the service sees Windows folders with a space in them"; `decisions/built.md` still says the unit carries the installing shell's `PATH`, but the quoting-for-spaces detail now lives only in git. The reviewer judged it below revert level and so do I; it also points deploy history at `changelog.d/` where `history/desk.md` is the assembled home.
**Leg notes (this leg, first unit):** step 0 found no claims, no worker worktrees, no mid-ops, no stop marker; pump latched. Bench refreshed: `dev-bench` and `dut` **not attached**, so `api/059`, `dev-bench/035`, `038` stay `open`. No day fold owed (`2026-11-05` has no entries; today's first leg already ran `check-client-names.py --suite --history`). `--refill-owed` fired on spread only (2 scopes, wave 6) and no `Spread sweep` line existed, so I swept: sources changed since 2026-10-29 are the owner's chat, promptu, desk, ui bench-editor and api lease work, and every new `open.md` line is hardware-gated, an owner's pick, or an unfired trigger. Roadmap Next is hardware; reversals unchanged. Spread sweep: nothing filed (2026-11-06 12:55). Size ledger: nothing overdue; `core/112` (`blocked`, `In flux: yes`) falls due 2026-11-09.


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
*Days 2026-10-29 to 2026-10-29 rolled to [log-archive/supervisor-log-2026-10-29-to-2026-10-29.md](log-archive/supervisor-log-2026-10-29-to-2026-10-29.md).*
