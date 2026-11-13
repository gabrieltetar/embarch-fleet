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

## 2026-11-12 19:52 — desk/028 a line body the desk cannot honour is refused, and a session takes back its own line

**Decided:** nothing suite-wide. New `embarch-desk` decision 85 (the worker's, `decisions/notes.md`; 85 was the next free number): a line body with a field the desk does not know is a 400 naming each field and writes nothing, on both `POST /sessions/{sid}/line` and `POST /tiles/{id}/line`. It collects unknown fields with `#[serde(flatten)]` and refuses in `LineBody::note`, rather than `deny_unknown_fields`, because axum's extractor would answer 422. New `DELETE /sessions/{sid}/line/{nid}` and MCP tool `desk_remove_line`: a session removes only a line it wrote itself (source `agent`, its own `session_id`), and only while the tile is open; another session's line is 403, an unknown id 404, a sent, folded or discarded tile 400 saying to add a correcting line. The worker grepped every caller read-only (chat's `client.ts`, ui's `desk.js` and `drive_desk.py`, the desk's own MCP tool): none sends an unknown field, so nothing was filed. The reviewer checked decision 78's rejected "session tool for the tile route" and found no conflict, since removal goes through the session route.
**Merged:** `agent/desk/028-a-line-body-with-an-unknown-field-is-refused` (code `bf93853`, ff on `1997108`; doc `1cea2713`, ff on `1cd0bb45` after a clean rebase). Gate on the merge result: `cargo build`, `cargo test` (260 passed), `cargo clippy --all-targets -- -D warnings` green; ownership `desk` OK on both branches, client names clean, `check-docs.py` 12/12. Code pushed after the doc gate.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needs a board. One deploy debt for the owner: the installed desk still drops unknown fields and has no `desk_remove_line` until it is redeployed (and the plugin's version bumped, so sessions load the new tool). Then check that `POST /sessions/<sid>/line` with `{"text":"x","bogus":1}` answers 400 naming `bogus`, and that `desk_add_line` then `desk_remove_line` removes the line from the tile.
**Budget:** PROCEED, wave 6; 5-hour 16%, weekly 30%.
**Least sure about:** an older chat or plugin build that someday sends a field this desk lacks now fails loudly with a 400 instead of misfiling; that is the intent, but it turns a version skew that was silent into a visible error in whichever client is behind.

---

## 2026-11-12 19:45 — chat/026 login and handoff decisions leave sessions.md by verbatim split

**Decided:** nothing numbered. `embarch-chat/decisions/sessions.md` 12,745 → 6,673 B, from 457 B over its cap to clear of reserve: decisions 101, 103, 105 and 106 (a window's login and desk, the handoff to a fresh session, a due login's warm-up, one pick for every panel) moved whole to a new `decisions/logins.md`, and the group table in `decisions.md` gained its row. I diffed removed against added lines: only the new file's header block and one separator blank line differ. **Compaction-pass answer** (mine; the worker called it not applicable): yes. `spec.md` (8,947 B) was not touched and still says what the chat is, how it runs, its invariants, constants and non-goals; the split moved reasons, not current truth, and the four decisions are one index row away. **Fold extras:** `suite/features.md` gained one row the assembler had not yet built on `main`, the owner's EMB-161 login-pick fragment; the 2026-11-10 (52 units) and 2026-11-11 (7 units) log days were folded by two `embarch-log-folder` agents, and 2026-11-07..09 rolled into `log-archive/supervisor-log-2026-11-07-to-2026-11-09.md`.
**Merged:** `agent/chat/026-compact-chat` (doc only: `d76e0412`, ff on the claim `45b9cb6e`; no code worktree). Gate on the merge result: `check-docs.py` 12/12; ownership `chat` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 16%, weekly 30%.
**Least sure about:** whether the owner has a branch editing one of the four moved decisions; he landed 106 and 100's amendment in this file today, and a branch of his would now meet them in `logins.md`.
**Leg notes (this leg, first unit):** normal mode, pump latched, no stop marker, no owner message, nothing to recover (no claims, no unit or leg worktrees; stale local `agent/*` branches in seven repos left for `fold-commit.py`). Leg began at `1411a9a9` (fleet `42db4cd`). Fleet Ready: seven issues split in `7866a9ab` and moved to Fleet Working: EMB-155 → `api/151`, EMB-158 → `api/152`, EMB-113 → `atlas/063`, EMB-109 → `atlas/064`, EMB-141 → `desk/028`, EMB-140 → `ui/109`, EMB-147 → `dev-bench/047` (`toolchain`, a leg's own hands; its pd-bench west workspace is not initialised, so the first `west update` is several GB). Announced at `ts` `1794537223.969339`. `finish` moved EMB-73 to Done. Refill not owed (9 dispatchable across 6 scopes). Size ledger: nothing overdue. Bench: Core reachable, no probe attached, neither role validates, so `api/059` and `dev-bench/038` stay `open`. Client-name history scan: all 16 repos clean. Dispatched 19:35: `desk/028`, `ui/109`, `api/151`, `chat/026`.

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
## 2026-11-10 — 52 units

_Folded 2026-11-12 by the log-folder agent for leg 011's first unit: per-unit Decided, gate, ownership and Least-sure narrative, budget lines and leg notes went to git; SHAs, reviewer lines and hardware debts kept verbatim._

**Carry forward.** Pump ran in burndown until 2026-11-11 06:00, wave 6. Five units (api/108, 126, 127, dev-bench/036, 037) were run by owner-dispatched worker threads and landed by an owner-dispatched landing agent, no leg number; their reviewer line is `skipped`. api decisions 102, 103, 104 landed as written; decision 24's note gained `schema_version` 2 (a `--json build` reader outside the suite's repos would break; the lander could not search them). `tasks/api/150-compact-api.md` filed (open, due 2026-11-24). Real-board debts below need an attached bench board; the 05:11 dev-bench units found neither role attached.

**Units.**

### 2026-11-10 23:19 — api/127 build --each builds a range from each commit's own module
**Merged:** `08f9a53` `46bc4128` `c7cb8708` `d36be9e` `fca417c`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one, toolchain rather than a board. Under `build --each`, a sysbuild version header and any commit id computed at CMake configure time go stale between commits: the tool removes `app_version.h` only at `<build>/zephyr/include/…`, so a sysbuild image's copy under `<build>/<app>/zephyr/…` keeps the first commit's id, and `--same-tree-as` has met one fixture workspace (a T2 module on Zephyr 4.4), never a sysbuild one. `open.md` names both.

### 2026-11-10 23:17 — api/126 build answers with a verdict and builds named variants
**Merged:** `08f9a53` `15cef80` `eae5b2a1` `fca417c` `fd0c6e96`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two, both toolchain rather than a board. (1) Re-run the size comparison on the real field variant pair, which only the owner can do because it lives in a client workspace; the worker's replay used a substitute pair (Zephyr `hello_world` on `qemu_cortex_m3`, default and a logging variant), and `open.md` names the debt. (2) No real twister output or sysbuild log has been fed to the verdict parser yet: twister's per-scenario lines are fixture-tested only, and the one real test run was a `native_sim` ztest through `west build -t run`.

### 2026-11-10 23:11 — api/108 a timed-out build's Windows tree kill is verified on Windows
**Merged:** `15cef80` `6c9fd490` `6d3f24c6` `febdaf2`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 23:06 — dev-bench/037 pd-bench is checked without a board
**Merged:** `50579d3` `e90bae7` `f04ff0bd` `fb57a30e`
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief ran a reviewer only if leg.md needed one to land, and a reviewer gates no merge).
**Hardware debts:** one, payable with 036's on the same board. Flash both shields and run `pd srccaps`, `pd max` and a refused Request: `main.c` now calls `pd_logic.c`, and its unchanged messages are the worker's claim, which the `native_sim` suite does not cover.

### 2026-11-10 23:04 — dev-bench/036 pd-bench builds from its own west workspace
**Merged:** `25c748ea` `668b743` `752b13c4` `e90bae7`
**Blocked:** nothing.
**Reviewer:** skipped (owner-dispatched landing outside a leg; the landing brief ran a reviewer only if leg.md needed one to land, and a reviewer gates no merge).
**Hardware debts:** one. Flash pd-bench from this workspace onto a NUCLEO-G0B1RE with each shield: the patches' run-time fixes (DMA transmit, the late TXMSGDISC, RX overrun, VCONN `-ENOTSUP`, the DRD bit) are asserted from the patch headers and pd-bench's history, never measured from this workspace.

### 2026-11-10 13:21 — chat/024 four input bullets leave the chat's spec.md by verbatim split
**Merged:** `1794342092` `1d3a1b2b` `237a36fe` `7e275ff5`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 13:16 — chat/025 the host test expected a cards call decision 97 removed
**Merged:** `192ee5ef` `1997108` `3e3c96b1` `56fcb0a5` `7003850` `9162e45` `93ede9b7`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 12:59 — promptu/004 the uninstalled build steps leave spec.md by verbatim split
**Merged:** `5584d2aa` `62fe3cd5` `67fc2606` `6ef3e8f0` `f1b22701`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 12:58 — outpost/029 overflow and override decisions leave transport.md and manifest.md by verbatim split
**Merged:** `428b0dd0` `843882b0` `e48351bb`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 12:57 — desk/027 three suite-desk paragraphs leave spec.md by verbatim split
**Merged:** `12394e78` `1794340428` `192ee5ef` `2e6f5899` `4ddea194` `ab95a63c`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 06:45 — chat/023 an ended issue ends its chat
**Merged:** `02c5ab99` `1fd8b63e` `5b39b89d` `89a8ae7c` `9162e45` `b1802d6` `b50281ca`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 06:33 — desk/026 the issue's folder goes once no window shows it
**Merged:** `1997108` `7246a599` `901b8f5c` `9a32975`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 06:25 — desk/025 Done or Canceled tells the issue's window to end its chat
**Merged:** `1794316615` `546d670b` `89a8ae7c` `8d91a804` `9a32975` `b229d45` `d39131db`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 06:08 — dev-bench/035 the protocols seal gates a study
**Merged:** `263b33b6` `668b743` `8a57a032` `a6b597c` `f497b6e5`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a study with a corrupted `protocols_crc` sent by a real Core to a bench board should come back as that log line and `StudyDone { completed: false }`; neither role was attached at 05:11.

### 2026-11-10 06:04 — dev-bench/017 tx_scratch holds only what the bench sends
**Merged:** `38e56904` `470bbc9` `6cd71164` `a6b597c`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** run one real study on a bench board (`nrf54l15dk` or the ESP32-C5) and confirm every message the bench sends still decodes at Core, a `StepResult` with GATT services included; neither role was attached at 05:11.

### 2026-11-10 05:54 — suite/032 the FFI staticlib is retired: dev-bench links no Rust
**Merged:** `1794312920` `470bbc9` `8f7e1f0` `b95955d6` `f3baaf48` `f6cca94`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** flash one bench board (`nrf54l15dk` or the ESP32-C5) and confirm Core's `Hello` gets `HelloAck` with schema 15 and `compatible: true`; neither role was attached at 05:11. The task's flash box is left unticked for this.

### 2026-11-10 05:21 — dev-bench/046 the retired stream-capture GATT kind is refused and its path deleted
**Merged:** `05d144c5` `1794312920` `3daa719` `6a5e7ec7` `8a57a032` `8f7e1f0` `ad5744cc` `d992392a`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 05:09 — outpost/027 three Kconfig values keep the promise their option exists for
**Merged:** `26a92bc0` `28c3d76e` `6e07fc8` `9b95b94` `c64422b` `c91baaec`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the blocking wait is measured on `native_sim` only (decision 28 says so); on a real DUT, a thread at a priority above the drain thread filling the ring with `OVERFLOW_BLOCK=y` should return with its records and no gap.

### 2026-11-10 05:00 — dev-bench/045 the link-level wire enums take their values from the crate
**Merged:** `3daa719` `6874b02c` `70929779` `759c402`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 04:52 — core/125 pre-flight refuses a one-shot monitor inside an open window
**Merged:** `b6035a7` `c64422b` `c79b74b` `d4ab17a0` `f462d1fe`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** native Windows build of `embarch-core` not run (gate debt; one host-independent call and a test).

### 2026-11-10 04:49 — study-designer/083 decision 41 leaves gatt.md by verbatim split
**Merged:** `50a55434` `5a774c9f` `c91baaec` `cdbcf3b8`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 04:43 — dev-bench/010 crate limits and .eap wire enums are read from the crate at configure time
**Merged:** `244b19f1` `759c402` `9f6b5ae9` `caca256` `f8144fff`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 04:36 — study-designer/082 a one-shot monitor inside an open window is refused when the study is built
**Merged:** `6874b81` `a843f6af` `aa488fa3` `dea33acf`
**Blocked:** nothing. **New debt filed by the worker:** `tasks/study-designer/083-compact-study-designer.md` (`In flux: no`, due 2026-11-24): decision 89 took `decisions/gatt.md` to 12,048 of 12,288 B and `interfaces/types.md` to 11,154 B, both in reserve.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 04:28 — dev-bench/042 an open monitor window survives the steps inside it
**Merged:** `3acc3891` `caca256` `f2295f66` `fa5daf6`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT. Owed on the bench (DK plus a BLE peer): a one-shot monitor inside an open window (refused, window still capturing after); a `GattDiscover` and a `RunProtocol` inside an open window with the window's rows still labelled; a `RunProtocol` inside an unfiltered window completing instead of timing out, each frame one row; a `DataExchange` notify on a characteristic the window holds; `Hello` during a live `DataExchange` subscription.

### 2026-11-10 04:18 — dev-bench/043 a monitor step fails when its subscriptions fail or the link drops
**Merged:** `244b19f1` `5f9a4a5b` `a249ff5` `fa5daf6` `fdb0932f`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT, and no `native_sim` test reaches `ble_bridge_real.c`. Owed on the bench (DK plus a BLE peer): a CCC write the peer refuses; a notifying characteristic with no CCC; a disconnect during the subscribe walk; one inside an open window followed by its `Stop`; a `RunProtocol` source with no CCC; an unfiltered monitor against a peer with nothing that notifies.

### 2026-11-10 04:00 — study-designer/081 the att_status doc comment names its per-kind meanings
**Merged:** `14310512` `5c2f9a6` `5f9e118e` `a2b538b5` `b0ed2cbf`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:57 — dev-bench/044 the transcript keeps full-MTU notifications and records connects and disconnects
**Merged:** `10889a74` `1d4949b3` `72659053` `9371510` `a249ff5` `b890718a` `d245f2cc`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** nothing ran against a DUT. Owed on the bench (DK plus a BLE peer): a notification of 211 to 244 B reaching the transcript tap; `Connected` and `Disconnected` rows with the reason in a real study's `gatt.csv`; the bond-clear disconnect as the transcript's last row, before its `StreamClose`.

### 2026-11-10 03:44 — desk/024 decisions 38, 40 and 41 leave desks.md by verbatim split
**Merged:** `32d80fd6` `40c6f27d` `6b5ff8e7`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:41 — desk/023 decisions 79 and 81 leave access-point.md by verbatim split
**Merged:** `88d8d133` `a2b538b5` `c312b30f`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:36 — desk/022 the desk says when a repo has no embarch-api in its login
**Merged:** `8559cf3` `b229d45` `cfa0cd1e` `d4df4a3e` `d80ccc9b` `e14a064f` `e7a4d76c`
**Blocked:** nothing. **New debt filed by the worker:** `tasks/desk/024-compact-desk.md` (`In flux: no`), since decision 82 took `decisions/desks.md` to 90.1%.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:31 — desk/021 a desk tool reads an issue's images and files
**Merged:** `4fa470a` `8559cf3` `8bff8a95` `c9222741` `fd69c972`
**Blocked:** nothing. **New debt filed by the worker:** `tasks/desk/023-compact-desk-access-point-decisions.md` (`In flux: no`), since `decisions/access-point.md` is at 91.2% (1082 B left).
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:23 — desk/020 a Start work worktree builds its own Zephyr module
**Merged:** `4fa470a` `4feae56a` `5fedab9a` `939f5363` `e02b8bc`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** verify-only, needs a real west workspace and a session (no board): Start work on a firmware-repo issue, `ZEPHYR_MODULES` present in the worktree's `settings.local.json`, a board-file edit in the worktree, `west build` from a session there reading the worktree's file. **Unverified and load-bearing:** that Claude Code applies a settings `env` to a session's shell commands; the tests use a stand-in `west` and are `cfg(unix)` only.

### 2026-11-10 03:22 — atlas/062 the atlas follows the worktree a session runs in
**Merged:** `1794305754` `1fd9f20b` `634a3b9a` `b2debcd4` `d8bc57f` `e14a064f` `e7a4d76c` `f293d94`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:07 — atlas/061 an atlas for a target with no Zephyr board yet
**Merged:** `0cd81401` `51d97635` `5a5036ed` `7e7311bc` `a069f4cf` `d8bc57f` `dbeac7c`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 03:00 — desk/019 a desk tool lists a team's issues by state
**Merged:** `02c08b78` `1b090552` `4119299d` `45d38e0` `e02b8bc`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:56 — atlas/060 unnamed pins get a recorded name and its source
**Merged:** `088a56a1` `17af295` `17ea11e8` `26138cfb` `dbeac7c`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:54 — desk/018 desk_add_line can note another item
**Merged:** `0cd81401` `1794304156` `223e6b21` `30749852` `45d38e0` `4b83b5e` `51d97635` `5dbd0ec2`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:43 — atlas/059 a pin record can state its package
**Merged:** `17af295` `1f83ada2` `1ff05cff` `38a87fa` `5e281c7a` `75c49164`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:38 — atlas/058 part_card and mismatch_report answer before an atlas exists
**Merged:** `38a87fa` `6eca094` `e91066b0` `f53565ea` `f8d6fca9`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:31 — atlas/057 a live read selects a register's bank first
**Merged:** `1794302695` `1f83ada2` `354dbf6b` `3c9e7c96` `6eca094` `867da3b4` `f1c3bc4`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** `embarch-atlas live reg-read <label>.<REG>@<bank> --allow-bank-select` on a board with a paged I2C part whose `bus` record states `bank_select`: the value comes from that bank and the select register reads its old value afterwards. The Zephyr `i2c write_byte` argument order is from the worker's memory, not a board or the fake.

### 2026-11-10 02:19 — atlas/056 atlas-use knows the no-atlas placeholder
**Merged:** `18bdcea5` `d25dee1d` `dcf8e16` `e1c10a30` `f1c3bc4` `f285ca92`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:16 — atlas/055 a verb declares a board mating
**Merged:** `424e0f9c` `915f6ab9` `abc2db40` `c302ffe` `dcf8e16`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:14 — promptu/005 decision 39 still keeps the handoff chip
**Merged:** `20cde62c` `3953b4c8` `68f102d4`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:13 — chat/022 decision 103 stops naming a deleted function and chip
**Merged:** `1794301835` `3953b4c8` `3d6c446b` `d25dee1d` `ed3d9e3a` `f285ca92`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 02:04 — chat/018 the bulb stops suggesting context handling
**Merged:** `27d39662` `787c9cfb` `7a93e95` `83f27e2f` `88129529` `b1802d6` `c302ffe` `fe4a4e3f`
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-125
**Hardware debts:** none.

### 2026-11-10 01:55 — atlas/054 a register record can state its bank
**Merged:** `1c71cca2` `370801a6` `a9f97f5f` `c302ffe` `ca710c5` `d6efe11`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a live read of a banked register returns whichever page the part is on, because nothing selects the page (EMB-124); needs a board with a paged sensor to confirm. Owed to a real vendor file: check G on the paged sensor that showed 59 duplicate addresses.

### 2026-11-10 01:50 — atlas/053 a variant record kind lists orderable parts
**Merged:** `63142756` `6f6b3b97` `92c1d85b` `9b875c2` `ca710c5`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 01:46 — atlas/052 a session before the first atlas is told there is none
**Merged:** `15ab2fa5` `1794300040` `724df3eb` `83f27e2f` `9b875c2` `f5c64d18` `f796611` `fe4a4e3f`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 01:34 — chat/015 the spec status line says what is installed
**Merged:** `2b04ff5` `4be6006e` `6e15acf` `77ecf360` `78ea54b3` `7a93e95` `dc663c8b`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 01:32 — atlas/051 doc check reports a cite of a page outside the document
**Merged:** `059f6796` `29a2d4e8` `6432aa52` `bfeae59` `f796611`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 01:28 — chat/020 two decisions put the notice and thumbnails under the input
**Merged:** `1bee15af` `e5698bf7` `e8fa7f27`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-10 01:26 — chat/021 six host tests fail against the local desk binary
**Merged:** `208e3dc0` `424c3cf` `4b83b5e` `6e15acf` `9a88a836` `bf60fd1f` `dc663c8b` `e852ae8e`
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
*Days 2026-11-07 to 2026-11-09 rolled to [log-archive/supervisor-log-2026-11-07-to-2026-11-09.md](log-archive/supervisor-log-2026-11-07-to-2026-11-09.md).*
