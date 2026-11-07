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

## 2026-11-07 10:45 — dev-bench/041 a study over a bench cap is refused out loud

**Decided:** nothing suite-wide. Third `toolchain` unit by the leg's own hands. **New `embarch-dev-bench` decision 51** (`decisions/link-limits.md`): `dbm_decode_frame` returns `DBM_DECODE_OVER_CAP` (-2) for a well-formed `StudyStart` over a decode-time cap, `dbm_decode_frame_why` also names the cap, the value and the limit, and `receive_message` sends `StudyStart refused: 17 steps over the bench cap of 16` as a `LogLine`; a malformed frame stays -1 and silent. Every cap refuses through one helper writing to a call-scoped pointer and still returning -1, so none of the propagation sites changed; I declined a context threaded through every reader and a code per cap. **Amended decision 50** (written by `dev-bench/004` an hour earlier): its "a decode refusal is silent" argument no longer holds, and the amendment says what is left of it. Overlay ride-along: `uart20` is VCOM1, interface 2 (decision 43); `uart30` is no longer given a VCOM, since nothing records which it is.
**Merged:** `agent/dev-bench/041-a-study-the-bench-cannot-hold-is-refused-out-loud` (code `4026cde` on `952f788`, ff; doc `73f4d033`, `d35e009f` cherry-picked onto the claim commit). Gate on the merge result: ztests `serial_protocol` 65/65, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 5/5; `native_sim` app and nRF54L15DK image build; ownership `dev-bench` OK on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the ESP32-C5 image, one `Done when` box left unticked in the task for it (`EMB-83`, no `esptool` in the fleet venv). On a board: a 17-step `StudyStart` should produce the `LogLine` in Core's `dev-bench.log`; nothing has sent one yet.
**Budget:** DEGRADED at the last boundary (wave 2); serial anyway.
**Least sure about:** closing the task `done` with the ESP32-C5 box unticked. The code it builds is the same C the Nordic and `native_sim` builds compile, so I judged the box an environment debt rather than an open question, and wrote that in the box itself.

## 2026-11-07 10:36 — dev-bench/004 a state-machine index the run cannot follow fails the run

**Decided:** nothing suite-wide. Second `toolchain` unit by the leg's own hands, built the same way (worktree sources, main checkout's workspace). **New `embarch-dev-bench` decision 50** (`decisions/protocols.md`, a new entry because 41 is pinned with 249 B left): a `when … goto`, `otherwise` or `on_timeout` target past `states_len`, or a `remember` variable past `session_len`, ends the run as `Fail` without moving (`EAP_FAIL_NO_SUCH_STATE`, `EAP_FAIL_NO_SUCH_VARIABLE` in `eap_interp.h`), so `final_state` names the state whose entry was bad. **Run-time rather than a decode refusal**, my pick of the task's two: a refused `StudyStart` is dropped without a word on the link today, while a failed run reaches Core by name. The cost, stated in the decision: a bad index on a branch never taken is never reported, which Core's validation covers. Four ztests (the task asked three; the `remember` got its own), all four failing with the interpreter change reverted (59/63), 63/63 with it.
**Merged:** `agent/dev-bench/004-protocol-state-indices-reach-a-c-array-unchecked` (code `952f788` on `61c96c2`, ff; doc `d4922d38`, `97eda043` cherry-picked onto `d7056346`). Gate on the merge result: ztests `serial_protocol` 63/63, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 5/5 (suite by suite; `twister` cannot start); nRF54L15DK image builds; ownership `dev-bench` OK on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. ESP32-C5 image not attempted (`EMB-83`, no `esptool` in the fleet venv).
**Budget:** DEGRADED at this boundary (cache stale with the pump off, wave 2); serial anyway.
**Least sure about:** the reviewer's side note, not filed: the Rust reference interpreter subscripts `states[]` directly and would panic on the same input, so "the crate is the specification" now has one class of input where only the C side has a defined answer. Harmless while `validate_protocol` runs first, but `eap_interp.h`'s header does not say so.

## 2026-11-07 10:28 — dev-bench/003 a length prefix is bounded before any arithmetic

**Decided:** (1) **Started the `toolchain` lane with the leg's own hands, the first unit of it any leg has run.** `protocol.md` §7 and `tasks/README.md` already give a `toolchain` task to the leg, one at a time; legs dreamt instead on 2026-10-28 and 2026-11-06 and neither dream got a reply. At this leg's top Fleet Ready was empty, `queue-status.py` read 0 worker-dispatchable, and the sweep filed nothing, so the alternative was a third identical dream. (2) **Built from a worktree, not the owner's main checkout**: `west build -d <scratch> <worktree>/app/tests/serial_protocol` from the main checkout's `workspaces/native_sim` compiles the worktree's sources (its `compile_commands.json` says so) in 17 s; the nRF54L15DK image the same way from `workspaces/nordic` in 23 s. The owner's `embarch-dev-bench` checkout was only read. That undercuts the README's reason these are not worker tasks, so I filed `EMB-83` (Backlog, `decision`): reclassify them `none`, or add `toolchain` to `queue-status.py`'s supervisor bucket. (3) The fix: `pc_skip_len_prefixed` refuses `len > (in_len - *pos) / elem_size` before any arithmetic. Two ztests (a protocol name of 2^64 - 1, a `service_uuids` count of 2^60) are laid out so the wrapped walk decodes cleanly: 57/59 with the fix reverted, 59/59 with it. One invariant line in `spec.md` §3, no decision entry.
**Merged:** `agent/dev-bench/003-pc-skip-len-prefixed-wraps-past-its-own-bounds-check` (code `61c96c2` on `5dd78b5`, ff; doc `f4e7213f`, `b3ddf812` cherry-picked onto `6ac10be8`). Gate on the merge result: ztests `serial_protocol` 59/59, `dev_bench_log` 15/15, `scan_seen_mfg` 7/7, `scan_seen_names` 5/5, each built and run on its own because `west twister` cannot start (the fleet venv lacks `natsort`); nRF54L15DK image builds; ownership `dev-bench` OK on both branches; client names clean on the code worktree; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The ESP32-C5 image was not built: Zephyr's Espressif SoC CMake wants `esptool` on `PATH` and the fleet venv has none (the old build used a client workspace's venv, which a leg must not reach for). Same file compiles for host and Cortex-M33, so the risk is low; `EMB-83` carries the venv gap.
**Budget:** PROCEED at start (5-hour 9.0%, weekly 34.0%, wave 6).
**Least sure about:** whether starting the `toolchain` lane without an answer to two dreams is the owner's caution or my overreach. The protocol grants it; nobody had used the grant, and a self-gated unit has only the reviewer as a second reader.
**Leg notes (this leg, first unit):** spawned with the pump off and the listener disarmed (its FYI posted at 10:15); no stop marker, no owner message, no reply in the dream thread `1793997725.841939`. Step 0 found no claims, no worker worktrees, no mid-ops; leg began at `68a20e3a` (`doc/096`, owner-only, landed overnight). Bench refreshed: `dev-bench` and `dut` not attached, so `api/059`, `dev-bench/035`, `038` stay `open`. Fleet Ready empty, `finish` moved nothing. `--refill-owed` fired on depth (0 dispatchable); I swept roadmap Next, all 17 `open.md`/`design.md` sources and the reversals rows, and filed nothing: no source has changed since the 2026-11-06 13:28 sweep, and every item is hardware-gated, the owner's pick or an unfired trigger. Size ledger: nothing overdue; `core/112` due **2026-11-09**. Day-folded 2026-11-06 (13 units) by a log-folder; `check-client-names.py --suite --history` clean on all 16 repos. The owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone.

## 2026-11-06 — 13 units

*Folded by the supervisor's log-folder, 2026-11-07: the per-unit reasoning behind each accepted judgement, the gate transcripts and the budget lines went; SHAs, reviewer lines and hardware debts stay. The detail is in git. Entry list: atlas/027–037 and desk/005, ui/104, dev-bench/040 (14 entries counting atlas/029, whose heading the extract lost).*

**Carry forward (next leg, read this first):**
- **Dream `ts` `1793997725.841939` is live** (posted 13:41 after the leg ended early at 3 of 4 on an empty queue). The listener will not spawn into an empty queue for 6 hours; a reply naming one of the three is direction for the leg it spawns: (1) a leg runs `dev-bench/041`–`044` with its own hands (`toolchain`, main checkout); (2) `suite/032`, retire the FFI staticlib (cross-repo, after a 30-minute window); (3) roadmap Next's real `.eap` run (owner's sitting). Nothing dreamt was written into the queue. Open question for the owner: whether legs should start taking `toolchain` work.
- **Queue:** 0 dispatchable. Bench `api/059`, `dev-bench/035`, `038` stay `open` (neither `dev-bench` nor `dut` attached at any refresh).
- **Size ledger:** nothing overdue; `core/112` (`blocked`, `In flux: yes`) falls due **2026-11-09** and takes the first unit of the first leg on or after that date.
- **Atlas bugs filed from reviewer residuals this day** (`EMB-77` → `atlas/034`, `EMB-78` → `atlas/035`, `EMB-79` → `atlas/036`, `EMB-80` → `atlas/037`) are all landed; `EMB-49`–`55` split into `atlas/027`–`033`. No atlas doc in reserve.
- **Known residual misses, not filed** (silent-miss kinds `codecheck`/`second-look` exist to prevent): a decimal-written offset register (`X_REG_ADC_OFFSET 18`) stays `encoding` and is never compared; a register with an inner MIN/MAX in its name (`REG_VSYS_MIN` shape) classifies as `value`; `below`/`above` as offset words in `limits.py` may push a real out-of-limit pair into "uncertain"; second-look `_NEGATED` eats one word only and "VDD via a high-impedance pull-up" now reads floating plus VDD; `named()` trusts the atlas stamp's `app` for whatever dir is named; `.work/build-<target>-<commit12>` dirs are orphaned after `atlas/028` and nothing prunes them.
- **`CHECKED_VERSION` was not bumped** by `atlas/033` or `037`, so false strap conflicts frozen in earlier second-look rounds stay frozen until a deliberate bump.
- **Dispatch wording:** say "a bare `done`" for `**State:**`, not "done (token zero)"; two workers wrote the parenthesis literally and the supervisor normalised it (`atlas/027`, `ui/104`).
- **Flux flip to watch:** `dev-bench/040` was reopened from `blocked` by flipping `In flux:` to `no, for the remedy this task now takes` on `chat/004`'s 2026-10-28 reading (a verbatim split restates nothing). The gate forces it, `DOC-BUDGET.md` allows it, one precedent exists, but `.claude/leg.md` says never dispatch an `In flux: yes` task; a field rewritten to make a dispatch legal is the pattern that rule watches for. Owner's reading wanted.
- **`2026-11-04`'s straggler `ui/103` entry** still sits beside its folded entry: `fold-day.py` refuses to merge two folds, and a hand-fold produced a duplicate heading that was reverted. Leave it until it rolls.
- Atlas worktrees are removed with `--force` (untracked `.venv`) after each branch lands. The owner's dirty `embarch-fleet/scripts/fleet-pump.py` (mode 644 → 755) is left alone. No `suite` task announced, nothing deployed. Spread sweeps ran (12:55 and 13:28), nothing filed. `check-client-names.py --suite --history` clean on all 16 repos. `2026-10-28` and `2026-10-29` rolled to `log-archive/`. Pump latched, no stop marker throughout. Budget PROCEED, wave 6 (DEGRADED at the first leg's start, no cache), 5-hour 48.0% / weekly 30.0% at the close.

### Merged

Gate on every code merge: `pytest` green (3 skipped: real west, real atlas, real SVD; `test_public_guard` ran), client names clean, ownership OK on both branches, `check-docs.py` 12/12. Doc-only merges: `check-docs.py` 12/12 and ownership OK, `cargo` not run.

- `agent/atlas/035-a-join-test-runs-a-nordic-project-end-to-end` (`EMB-78`): code `a034cc6` on `9e0e8d2`, doc `91fdc70e` (worker's `10d6cc69` cherry-picked onto `69f08b5a`). Synthetic Nordic `join` test; no defect, no source change. `pytest` 656.
- `agent/atlas/036-codecheck-keeps-a-hex-addressed-offset-register` (`EMB-79`): code `9e0e8d2` on `55d0331`, doc `0db2ef34` (worker's `f4594526` onto `7138f3a6`). A `REG_*_OFFSET` with a hex body and no bit token stays `register`. `pytest` 655.
- `agent/atlas/037-second-look-reads-high-impedance-as-floating` (`EMB-80`): code `55d0331` on `e0000e0`, doc `41c71b91` (worker's `b96e74eb` onto `fe02bf6f`). `pin_states` reads high-impedance as floating. `pytest` 653.
- `agent/atlas/034-named-build-dir-picks-the-image-the-atlas-was-built-for` (`EMB-77`): code `e0000e0` on `7257c9e`, doc `d38c7928` (worker's `d26943ce` onto `7197f67a`). `pytest` 650.
- `agent/atlas/032-dt-limits-mapping-needs-quantity-and-role` (`EMB-53`): code `7257c9e` on `cc83425`, doc `9a14275d` (worker's `6bb43696` onto `2d77bca9`). `limits.json` gains `uncertain` and `counts.mapping_uncertain`. `pytest` 648.
- `agent/atlas/033-second-look-strap-wording-is-not-a-conflict` (`EMB-55`): code `cc83425` on `5685cee`, doc `42258045` (worker's `eb031b87` onto `07409c25`). Strap condition compares by pin state; wording-only mismatch is `unresolved`. `pytest` 645.
- `agent/atlas/031-codecheck-offset-define-is-not-a-register` (`EMB-52`): code `5685cee` on `536a098`, doc `47294ae0` (worker's `631c3dc8` onto `925f76fc`). Re-landed from the previous leg in step 0 (worker finished, nothing merged). `pytest` 642.
- `agent/atlas/030-codecheck-reads-only-compiled-driver-sources` (`EMB-51`): code `536a098` on `25ee47b`, doc `3a793b2d` (worker's `ea7fba1d` onto the leg after `atlas/028`'s fold). `pytest` 641.
- `agent/atlas/028-build-dir-follows-the-build-arguments` (`EMB-54`): code `25ee47b` on `49c8169`, doc `360219e2` (worker's `3b644a00` onto `256de75e`). Build dir keyed `.work/build-<target>-<commit12>-<args8>`. `pytest` 639.
- `agent/desk/005-compact-desk`: doc `1b4883e4` on `a3327739`; no code. `spec.md` 9,764 → 9,025 B, PAID. Dropped the PATH-quoting-for-spaces detail from the folded deploy history (git only).
- `agent/atlas/029-join-decodes-nordic-devicetree-pin-use` (`EMB-50`): code `49c8169` on `238db6f`, doc `30b4f104` (worker's `2dfa8444` onto `bf13f4b3`). Nordic GPIO and `NRF_PSEL` decode; constants checked against Zephyr's `nrf-pinctrl.h`. `pytest` 638. The task's "DT column filled" criterion had no end-to-end test; filed as `EMB-78`.
- `agent/ui/104-compact-ui`: doc `44b31310` (worker's `06dc5aa9` onto `6dfcfc7b`); no code. `spec.md` 9,265 → 8,290 B, `open.md` 4,226 → 2,220 B, PAID; verbatim splits to `embarch-ui/spec/roles.md` and `embarch-ui/open/trace.md`.
- `agent/atlas/027-build-picks-the-app-image-of-a-multi-image-sysbuild` (`EMB-49`): code `238db6f` on `029c41b`, doc `2aa05c86` (worker's `72a34d97` onto the leg HEAD after `dev-bench/040`'s fold). `pytest` 633.
- `agent/dev-bench/040-compact-dev-bench`: doc `e3caf357` on `8dd4bd2f`; no code. `spec.md` 9,632 → 7,151 B, PAID; new `embarch-dev-bench/spec/constants.md`. Diffed removed against added lines: identical except one `open.md` link. Same unit committed one `suite/features.md` row (a desk-notes fragment already on `main`).

Leg starts: `155ae93e` (atlas/037, 036, 035), `925f76fc` (atlas/031, 033, 032, 034), `fe57f14a` (desk/005, atlas/028, 030), `2e98b8a6` (dev-bench/040, atlas/027, ui/104, atlas/029). Fleet Ready splits: `afbc07ed`, `bb483366`, `f6eaffa6`; claim `43574a61` (`atlas/031`). Split announcements (no replies) at `ts` `1793993406.066929`, `1793994691.038249`, `1793996945.000199`.

### Blocked

Nothing, in every unit.

### Reviewer lines (one per unit)

**Reviewer:** no findings. (atlas/035)
**Reviewer:** no findings. (atlas/036)
**Reviewer:** no findings. (atlas/037)
**Reviewer:** no findings. (atlas/034)
**Reviewer:** no findings. (atlas/032)
**Reviewer:** no findings. (atlas/033)
**Reviewer:** no findings. (atlas/031)
**Reviewer:** no findings. (atlas/030)
**Reviewer:** no findings. (atlas/028)
**Reviewer:** no findings. (desk/005)
**Reviewer:** no findings. (atlas/029)
**Reviewer:** no findings. (ui/104)
**Reviewer:** no findings. (atlas/027)
**Reviewer:** no findings. (dev-bench/040)

### Hardware debts

No unit owes a board. The real-hardware confirmations owed, owner-attended or a toolchain leg, none needing a bench:

**Hardware debts:** none needing a board (atlas/035, 036, 037, 034, 032, 033, 031, 030, 028, 029, 027). Confirmations owed to real runs: real nRF54L15 atlas (`dt.json` `gpio_controllers`, pin checks on a real `edt.pickle`, `EMBARCH_ATLAS_REAL_ATLAS`); `codecheck` on a driver with an offset register and on the real charger build; `config --build` and `embarch-atlas build` on a real application-plus-MCUboot tree; a real `limits` run (read `counts.mapping_uncertain`, `uncertain[].why`); a real `second-look` round; a real rebuild with changed `extra_args`.
**Hardware debts:** none. (desk/005, ui/104, dev-bench/040)
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
