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

## 2026-11-04 16:00 — ui/103 a tab manifest says icon is required

**Decided:** nothing suite-wide. The first issue through Linear intake since `inbox/` was retired: `EMB-8` split into
`tasks/ui/103` (`eb2c5ab6`), `filed` moved it to Fleet Working, announced `ts` `1793832990.931349` before dispatch, no
reply. `embarch-ui/interfaces.md`'s manifest section now says `label`, `icon` and `panel` are required, `icon` must
name an `.svg`, and a tab that fails this is left off the page with `tab <id> is left out: <error>` logged. Three calls
of mine: (1) **I honoured the prompt's `1 ui` over the size ledger**, so overdue `dev-bench/040` did not get this leg's
first unit. (2) **I skipped the sweep although `--refill-owed` exited 0**: a one-unit leg restricted to `ui` had its
unit from the split, and nothing it filed could run. (3) **I committed `suite/features.md` with no `features.d/`
fragment from this unit**, because `build_features.py` found `main`'s table stale: it picked up already-committed rows
(the lease row's update, a `tab-folders` row, a desk Start-work row, a two-logins row), rebuilt deterministically, so a
revert of this fold only makes the table stale again. Worker left the task's `State:` at `claimed` with its boxes
ticked, which is all its definition's checklist asks; I set `done` at the fold, so the file retires.
**Merged:** `agent/ui/103-tab-manifest-says-icon-is-required` (doc `a2081aac` on `5218e1a6`, ff; code none, doc-only
unit, `embarch-ui` `main` stays at `ca9e6bc`, its worktree never committed or pushed). Gate on the merge result:
`check-docs.py` 12/12, client names clean on the code worktree, ownership `ui` OK on both branches (3 paths and 0).
`cargo` not run: no code changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** DEGRADED at start and end, no usage cache, measured wave 2, no 429.
**Least sure about:** the "missing `icon` is left out" sentence rests on `Manifest.icon` being a required `String` and
on the four log call sites in `src/tabs.rs`; no test has a manifest with that key missing. Worker, reviewer and I all
read it from the type.
**Leg close (next leg, read this first):** 1 of 1 units, the cap the prompt set; no pump latch was present. This fold
also carries `2026-10-29`'s day fold and the roll of `2026-10-26`, and `check-client-names.py --suite --history` was
clean on every repo. **Owed by the next unrestricted leg:** `dev-bench/040` is overdue (due 2026-11-01, `blocked`) and
takes the first unit; the refill sweep, last run 2026-10-29. **Read the `2026-10-29` carry-forward's "`inbox/` is
empty" as "Fleet Ready is empty"**: that directory is gone. The dream `ts` `1793318476.457199` has had no human reply.
`desk/005` is the only other dispatchable task. `changelog.d/` holds 66 fragments I did not write and left alone,
`umbrella-check-17-measured.decided.md` among them. This `ui` fold prunes `embarch-ui`'s two `agent/ui/059-*` branches,
which the 2026-10-29 carry-forward lists as unproven: I checked, `9199da5` and `052990c` are on `main` and the one
unmatched commit, `21a48de`, is the earlier draft of the same `src/logs.rs` fix. `embarch-doc`'s origin copy still
stands. `agent/ui/103-*` stays as `embarch-doc`'s origin branch and a local branch in both repos until the next `ui`
fold, since a fold prunes one behind. Nothing deployed.

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
## 2026-10-28 — 32 units

*Folded by an `embarch-log-folder` subagent for the next leg's first unit, 2026-10-29: the per-unit narrative reasoning, gate-result detail, budget lines and "least sure about" prose went; every SHA, every reviewer line and every owed hardware debt is kept below, and git holds the rest.*

**Carry forward (read this first):**
- **The queue is dry outside `atlas`.** `queue-status.py` counted 19 dispatchable at the day's end and every one is an `atlas` task, skipped per `tasks/doc/089` (no atlas gate). The listener may keep spawning legs because the script counts atlas as dispatchable; that gap is the owner's to close. A dream was posted (`ts` `1793248372.130149`): settle `tasks/doc/089`, start the `toolchain` lane by a leg's own hands (13 tasks), plug in the bench. **If no reply has arrived and `inbox/` is empty, do not dream again and do not invent work: end after step 0.**
- **Bench:** Core up, no probes; `validate dev-bench` and `validate dut` both not attached (not a mismatch). `api/059`, `dev-bench/035`, `dev-bench/038` open. `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`). Overdue size ledger: `suite/030` (owner-blocked), `doc/031` (owner-only); `study-designer/026` retired this day.
- **Nothing from this day is deployed:** the live Core, the installed `embarch-api`, `embarch-ui` and `embarch` all predate it (`suite/046`-`049`, `api/125`, `api/128`, `api/129`, `api/130`, `core/116`-`121`, `ui/100`). An `embarch` built before `suite/047` reads the new `--version` lines as a manifest mismatch (doctor checks 1 and 15), so rebuild umbrella together with api and core.
- **Suite-wide cross-repo designs approved by the supervisor under protocol §8, announced windows closed with no reply:** `suite/046` (bench board owns signals; topology decision 48, core 103, api 95), `suite/049` (SCPI instruments; topology 49, core 104, api 97), `suite/047` (every binary names its commit, install replaces a running binary, doctor check 18, core-log check renumbered 19; umbrella 57, api 93, core 100), `suite/048` (operator prompt step; core 105, api 99, `embarch-core-client`; the answer route is deliberately **not** lease-gated, anyone holding Core's token may answer, checked by prompt id; step `timeout_ms` capped at one hour). None is a wire-schema bump. `GET /study/{id}` on a finished host study now carries `host_result` rather than `result`.
- **Open filings:** `tasks/umbrella/094` (compact `open.md`, blocked `In flux: yes`, due 2026-11-11); `tasks/ui/101`, `core/123`, `api/149` were filed and landed same day. Decision-compaction by verbatim split is the default remedy that `DOC-BUDGET.md` allows even over `In flux: yes` (used for `chat/004`, `topology/066`). **88 task files with `State: done` remain in `tasks/`**, not bulk-retired (docs may link them).
- **Recurring failures likely to repeat:** (1) the fold's `&&` chain running past a refused fold through a `| tail` (three units named it: `api/128`, `ui/098`, `core/121`, `api/144`); a spurious `leg-fold` tick and Slack line go out before the real fold. (2) Workers leave the task's `State:` at `claimed` after ticking boxes (`tasks/doc/050`; workaround: commit `done` before the fold). (3) `git -C <repo> worktree add` with a relative path creates trees inside the repo; use absolute paths under `embarch/.worktrees/`. `embarch-api/.worktrees/embarch-api/` holds two 2026-09-13 symlinks, left alone. (4) The core gate flaked about one run in four on two capture-timing tests until `core/122` fixed them. (5) A worker can report a comment it did not write (`core/123`); only the reviewer's diff read caught it.
- **A leg killed at ~17:35 left four claims in flight;** recovered by re-landing pushed branches (`topology/068`, `api/144`) and committing dead trees as WIP and re-claiming them as resumes (`ui/100` `cc29076`, `core/122` `a24c7d7`). Whether the owner wants resume rather than block next time is unasked.
- **Open design questions the units left:** counting an ambiguous role-less-board `need` as met (`api/149`); the answer route being lease-open (`suite/048`); a 3 s server-side poll opening a UI session per running study (`ui/100`, nothing measured eight follows); `ui/101`'s "no uncaught JavaScript error" check reads `window.__errs`, which the page never installs, so it cannot fail. This fold also carried the 2026-10-26 day-fold (85 units; 268/268 SHAs, 85 reviewer lines, 27/27 debts) and `--roll` of 2026-09-28 and 2026-09-29.

**Merged** (one line per unit; code SHA on its base, doc SHA rebased from the worker's; all ff unless stated; each gated on the merge result: build/test/clippy `-D warnings`, client names, `check-docs.py` 11/11, ownership):
- `chat/004` timeline.md split by mission, verbatim (decisions 15, 16, 67, 68, 69, 74, 85 to `readouts.md`; 13,806 to 10,535 B): doc `4949d467` (worker `172bd8a0`) onto `043bf14d`; no code. Budget 9.2%. Leg 22:13 closed 4 of 4 (`api/149`, `core/123`, `ui/101`, `chat/004`); dream `ts` `1793248372.130149`.
- `ui/101` modal driven headless against a stub Core (no rendering bug found): code `f6da709` on `9f5461e`, doc `7265c7e9` (worker `a525b68d`) onto `611c567e`.
- `core/123` pacing comments say end of exchange (`mark_sent` renamed `mark_exchanged`; I finished the worker's placeholder comment): code `12192cc` on `5a310bb`, then fix `85846c4`; doc `10865fa0` (worker `ff11ac91`) onto `0610f8ff`.
- `api/149` ledger needs match a role-less bench board by enrolled name (api decision 98 amended, `ambiguous_needs`): code `0f1f0d4` on `124f461`, doc `138d1a05` on `266d925c`, no rebase. Leg started 22:13 at `314ae07c`.
- `ui/100` operator-prompt modal on any tab (ui decision 69, `operator-prompt.md`; server-side 3 s poll, `MAX_SESSIONS` 8): code `9f5461e` on `4914db5` (WIP `cc29076` + resume), doc `1a63895d` (worker `4fd56e26`) onto `a652ae4e`.
- `core/122` capture-timing tests stop flaking (window `199..=10_000` ms): code `5a310bb` on `248a899` (WIP `a24c7d7` + resume), doc `5c89ff2f` (worker `bb26198f`) onto `e724500d`.
- `api/144` compact `embarch-api/open.md` (4,810 to 3,905 B): doc `b2daa5e9` (worker `a086aebc`) onto `a42269ff`; code none, api main stays `124f461`.
- `topology/068` `min_interval_ms` states Core's measurement point: code `eebc122` on `0803354`, doc `bb75de6e` (worker `f0135df7`) onto `2f2c7295`. Leg started 21:50 at `36923622`; resume re-claims `0d478fbe` (ui/100) and `2f2c7295` (core/122).
- `suite/048` operator prompt step (announced `ts` `1793226580.382079`, 16:29:40): core `248a899` on `52d4659`, api `124f461` on `f088971`, ui `4914db5` on `0b18d18`, doc `7a018932`; ff in that order 17:18-17:21, ui main uncompilable against api main about two minutes between.
- `ui/099` Study Designer tab shows protocol divergence (ui decision 68): code `0b18d18` on `7361c2b`, doc `35ad8443` (worker `77eb68ef`) onto `7e1fa488`.
- `api/128` hardware test ledger per project (api decision 98; `run_study` gained optional `test`): code `f088971` on `2a89a61`, doc `dc7fa414` (worker `993289fe`) onto `67e62b55`.
- `study-designer/080` pure reordering reported under the part that moved (decision 87 amended): code `d9dee0e` on `f0de25e`, doc `c5b6c58f`. Leg started 16:28 at `db81050d`; DUT role enrolled as an STM32G0B1VE, probe `000852006107`.
- `suite/049` SCPI bench instruments (announced `ts` `1793223204.666079`, 15:33:24): topology `0803354` on `76bd3d1`, core `52d4659` on `2fccb61`, api `2a89a61` on `9c7832b`, doc `afbaa12f` onto `eda0e50b`.
- `ui/098` signals table and dialog know a bench-board origin (ui decision 67): code `7361c2b` on `9d23e62`, doc `58cf8732` onto `7cd6a2e6`. Its Slack line names `6566cce6` (the `api/130` fold) as its fold by mistake; the real fold is the next commit.
- `api/130` `embarch-api stack plan|fold|restack` (api decision 96; backups under `refs/backup/`): code `9c7832b` on `943f89d`, doc `7cd6a2e6` onto `fcc7c739`.
- `study-designer/079` saved study told its protocol no longer matches the `.eap` (decision 87): code `f0de25e` on `302784c`, doc `fcc7c739`. Leg started 15:30 at `f9ef3f03`; announced `suite/049` `ts` `1793223204.666079`.
- `suite/046` bench board owns signals (announced `ts` `1793219633.062879`, 14:33:53): topology `462e92e` + `76bd3d1` on `b4d1b0a`, core `2fccb61` on `c54591a`, api `943f89d` on `8e25811`, doc `b199ab9e`.
- `core/121` bench study on a captured signal refused at submission (core decision 102): code `c54591a` on `c9bdfab`, doc `1ac397d3` (from `21d32f7d`) onto `e75e9c17`.
- `ui/097` bench box takes its label on the first draw: code `9d23e62` on `7a6d923`, doc `589fa4f9` (from `05ea89d6`) onto `1ae3b546`.
- `api/140` `decisions/client-crate.md` compacted (11,581 to 10,817 B): doc `a7d5dbec` onto `c20f1713`; no code. Leg started 14:53 at `70c9512b`.
- `core/120` `GET /serial-log` resolves a declared signal (core decision 101): code `c9bdfab` on `2d3532d`, doc `3c959c85` onto `c73f6519`.
- `ui/096` `drive_topology.py` isolates its state: code `7a6d923`, doc `9616e75e` onto `c7913c79`.
- `umbrella/093` `embarch setup` installs the desk service and plugin (umbrella decision 58): code `4c786fa` on `97b1358`, doc `8469ab5f` onto `aeb1f31d`.
- `api/125` `serial_log` reads a declared signal (api decision 94): code `8e25811` on `525cda7`, doc `213408cf` onto `ea68b4bc`.
- `suite/047` every suite binary names its commit (announced `ts` `1793216385.010889`, 13:39:45): api `525cda7` on `744b94b`, core `2d3532d` on `72bbd52`, umbrella `97b1358` on `9d27e12`, doc `1c65685f`.
- `ui/095` `time-chart.md` split verbatim (decision 37 to `time-chart-live.md`): doc `7aa213b0` onto `213bd3d0`; no code; `done` in `56550f47`.
- `api/132` `zephyr.rs` cites decision 86, not 64: code `744b94b`, doc `25f394d4` onto `b8ca7aa6`; `done` in `4767f859`.
- `core/118` `halt_count` takes the gate's share from `Validation.halts` (decision 97 amended): code `72bbd52`, doc `02869ae6` onto `4b128505`; `done` in `8f7e81f4`.
- `api/129` `embarch-api patches export|import|regroup` (api decision 92, new dependency `sha2`): code `0fdcf05`, doc `90e2cbeb` onto `dae32801`.
- `topology/066` links.md and enrollment.md split verbatim, `topology/060` paid early: doc `ccf66b1c` onto `5efffa07`; no code.
- `study-designer/078` decision 81 no longer claims a "0 of 0" print: doc `e35da7be` onto `bf6efa5d`; no code.
- `core/116` host study runs Repeat, per-pass line counts (core decision 99): code `29b552e`, doc `710dde87` onto `60f97214`.

**Blocked:** nothing, all 32 units. One reviewer finding (`core/121`) was fixed in its fold and its drop deleted.

**Reviewer** (one per unit, newest first):
**Reviewer:** chat/004 — no findings.
**Reviewer:** ui/101 — no findings.
**Reviewer:** core/123 — no findings (it caught the unwritten placeholder comment; fixed as `85846c4`).
**Reviewer:** api/149 — no findings.
**Reviewer:** ui/100 — no findings.
**Reviewer:** core/122 — no findings.
**Reviewer:** api/144 — no findings.
**Reviewer:** topology/068 — no findings.
**Reviewer:** suite/048 — no findings.
**Reviewer:** ui/099 — no findings.
**Reviewer:** api/128 — no findings.
**Reviewer:** study-designer/080 — no findings.
**Reviewer:** suite/049 — no findings.
**Reviewer:** ui/098 — no findings.
**Reviewer:** api/130 — no findings.
**Reviewer:** study-designer/079 — no findings.
**Reviewer:** suite/046 — no findings.
**Reviewer:** core/121 — 1 finding — inbox/core-decision-92-not-done-clause-stale-after-102.md (fixed in this fold, drop deleted)
**Reviewer:** ui/097 — no findings.
**Reviewer:** api/140 — no findings.
**Reviewer:** core/120 — no findings.
**Reviewer:** ui/096 — no findings.
**Reviewer:** umbrella/093 — no findings.
**Reviewer:** api/125 — no findings.
**Reviewer:** suite/047 — no findings.
**Reviewer:** ui/095 — no findings.
**Reviewer:** api/132 — no findings.
**Reviewer:** core/118 — no findings.
**Reviewer:** api/129 — no findings.
**Reviewer:** topology/066 — no findings.
**Reviewer:** study-designer/078 — no findings.
**Reviewer:** core/116 — no findings.

**Hardware debts owed** (14 of 32 units; the rest none or "none new"; each in the day's own words, unit named on the line above):
ui/101:
**Hardware debts:** one prompt answered from the UI against a live Core with the beep and desktop notification
heard (not exercisable headless); the installed `embarch-ui` predates `ui/100`.
core/123:
**Hardware debts:** native Windows build of `embarch-core` (comment-only change, so a formality).
ui/100:
**Hardware debts:** (1) the modal has never rendered in a browser (`tasks/ui/101`, host-side); (2) one prompt
answered from the UI against a live Core, with sound and notification heard, and the installed `embarch-ui`
predates this.
suite/048:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this (and `suite/049`
and `api/128`); (2) one prompt answered on a real bench from each surface, including a stale answer refused; (3)
native Windows build of `embarch-core`.
api/128:
**Hardware debts:** the task's bench box, written as three steps in the retired task and in `open.md`: a
`tests.toml` with one `dut` test and one needing an absent role gives one runnable and one grouped; `run-study --test`
lands a row that settles; amending a passed commit flags `commit-unreachable`. Needs a deployed Core and a rebuilt
`embarch-api` binary; nothing is deployed.
suite/049:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this; (2) the task's
bench check, owed: on the ET5410A+, `*IDN?`, `MEAS1:ALL?`, `CH1:SW ON`/`OFF` read back and `LOAD1:ABNO?`, time per
command recorded in core decision 104 (no instrument is declared; the bench was unattached this leg); (3) native
Windows build of `embarch-core`.
suite/046:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this; (2) one real
run on a bench board: `declare_signal origin_board=<its name>`, `mem_read probe_serial=`, `validate probe_serial=`,
and a reset resolved from that signal; (3) native Windows build of `embarch-core`.
core/121:
**Hardware debts:** (1) native Windows build of `embarch-core`; (2) once deployed, one bench study tapping a signal
while `POST /signals/{name}/capture` holds it: expect `409` and no flash. Not deployed.
core/120:
**Hardware debts:** (1) once deployed, one `serial_log signal=<name> port_wait_ms=~10000` across a DUT reset on
a CDC ACM console: expect 200, `port` the new name, lines at the signal's baud; one `signal=` on a `host-to-dut`
signal, expect 409; (2) native Windows build of `embarch-core`. Not deployed.
umbrella/093:
**Hardware debts:** owner run: one real `embarch setup` on a machine with `embarch-desk` and `claude`, both steps
reporting done (the service install restarts the live desk), then `setup --uninstall` removing both.
api/125:
**Hardware debts:** once `core/120` lands and Core is deployed, one `serial_log signal=<DUT console>
port_wait_ms=5000` across a DUT reset on a CDC ACM console, confirming lines arrive at the signal's baud.
Not deployed: the installed `embarch-api` does not have `signal` yet.
suite/047:
**Hardware debts:** (1) nothing is rebuilt, installed or deployed: the owner's installed `embarch-api`, the
live Core and `embarch` still print the old lines until rebuilt; **an `embarch` built before this reads the
new `--version` lines as a manifest mismatch (checks 1 and 15), so rebuild umbrella with the others**;
(2) `deploy-core`'s `WSLENV` hand-off has never run against the real service, so the first deploy should
confirm the service's `--version` names the commit; (3) Windows install over a running binary is stated,
not tested; (4) native Windows build of `embarch-core`.
core/118:
**Hardware debts:** (1) a real STM32G0 through `POST /live/core-state` on a running core should report
`halt_count == 1` by default and 2 with `halt=true`; (2) native Windows build of `embarch-core`. Not deployed.
core/116:
**Hardware debts:** (1) run the designer's fixture study (`host_pd_hard_reset_counts.json`, 8 Hard Resets, two
taps) on the PD bench and compare the per-pass counts against a hand count of the console dump — it checks the
assumption that a console line lands in the pass that caused it (a reply delayed past a pass's end counts in the
next pass); (2) native Windows build of `embarch-core`. Not deployed.
Not owed but unrun: ui/099, ui/098, ui/097 and ui/096 were never driven in a browser (`tests/browser/drive_topology.py` needs only geckodriver and a debug build; one headless look at an edited `.eap` study, one `declare_signal origin_board=` then a dialog re-save); `api/130`'s `stack` has met only throwaway fixture repos and needs git 2.38+; `api/129`'s `patches` has met only a synthetic 3-patch repo.
*Days 2026-10-26 to 2026-10-26 rolled to [log-archive/supervisor-log-2026-10-26-to-2026-10-26.md](log-archive/supervisor-log-2026-10-26-to-2026-10-26.md).*
