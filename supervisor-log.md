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

## 2026-10-26 00:51 — desk/002 fold and approve edges

**Decided:** nothing beyond the worker's decision 60 (`decisions/cockpit.md`: a fold goes only into a
strictly later real `YYYY-MM-DD` day, else 400 and nothing changes; every tile route refuses a tile id
whose date part is not a real day; ✓ with an empty note sends the target's and the folded tiles'
lines, oldest first; a folded row's `hours`/`computed_hours`/`captured_hours` report the gap it
carried, frozen at the fold, while `logged_hours` stays that day's Harvest — 3 h captured, 0.5 h
logged reports 2.5 h where it used to report 2.0). The reviewer checked the Desk tab's `desk.js`: ids
and fold targets come from the server, so nothing it sends is newly refused.
**Merged:** `agent/desk/002-fold-and-approve-edges` (code `41d9ff2`, ff onto `3f56975`; doc
`0f73bb27`, two commits cherry-picked from `6082323f`). Gate re-run on the merge: build, `cargo test`
123 pass, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not deployed: the desk service on :4891 is the owner's to rebuild.
**Budget:** PROCEED, weekly 52.7%, wave 6.
**Least sure about:** the fold refusal is tested at the store and `split_tile_id` level, not through an
HTTP call (no route harness exists); `/day/{date}` and other date-taking routes were not tightened.

## 2026-10-26 00:50 — api/134 flash results carry the erased ranges

**Decided:** nothing beyond the worker's change (`FlashResponse.erased: Vec<String>`,
`#[serde(default)]`, in the shared `embarch-core-client`; every flash result's JSON carries `erased`,
the CLI text appends `; erased <ranges>`; the `erase` descriptions follow `embarch-core` decision 84).
Read the shared-crate hunk before merging: additive, and no consumer builds `FlashResponse` by struct
literal (grepped `embarch-ui`, `embarch-umbrella`). In the fold I amended api decision 41
(`decisions/tool-wrapping.md`) by one sentence: it still required the description to say
"destructive full-chip erase", which decision 84 made false; the reviewer flagged it below its bar.
**Merged:** `agent/api/134-flash-print-erased-ranges` (code `765ff8e`, ff onto `2f3749b`; doc
`719a0d42`, two commits cherry-picked from `37012484`). Gate re-run on the merge: build, `cargo test`
green across the workspace (client 48), clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none of its own; decision 84's STM32G0B1VE bench check (core/096) still owed.
**Budget:** PROCEED, weekly 52.7%, wave 6.
**Least sure about:** only the client parse is tested; the `erased` key in the MCP and CLI JSON is
covered by compilation, not by a mock-Core test.

## 2026-10-26 00:49 — core/107 one timeout_ms covers an exchange's write and read

**Decided:** nothing beyond the worker's amendment to decision 79 (one deadline starts with the write;
the read gets what the write left, and always one read pass; the write's per-call port timeout is the
remaining budget; bound `timeout_ms` + one 50 ms poll + `port_wait_ms`; cap 10,000 and its 15 s
rationale unchanged). In the fold I moved core/097's "Measured: only against a fake port…" sentence
back onto the 097 amendment (the worker had re-homed it onto 107's paragraph, where it duplicated
107's own measured line) and marked 097's "read's own deadline starts after the write" as superseded.
**Leg start, for the record:** the previous leg (spawned ~00:30) died before any claim, tick or
commit; nothing to reclaim. Inbox empty. `validate dev-bench`: probe `001057729826` not attached, not
a mismatch; `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`. `fleet-hardware.py --refresh`
still crashes (`measured: None` on the dut entry, line 214) — `tasks/doc/041`, owner's. Four units
dispatched at once: `ui/074` (overdue ledger, unparked), `core/107`, `api/134`, `desk/002`.
**Merged:** `agent/core/107-exchange-twice-its-timeout` (code `476e3e7`, ff onto `3dba64b`; doc
`2fa9f645`, cherry-picked from `f93730a1`). Gate re-run on the merge: build, `cargo test` 280 pass /
2 ignored, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two. (1) On a real CDC ACM port, confirm a blocking `write` honours the shortened
per-call timeout (folds into core/097's STM32G0 960-character check). (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 52.3% at start, 52.7% here, wave 6.
**Least sure about:** the new test's 250 ms slack is wall-clock, so a loaded CI host could flake it.

## 2026-10-26 00:28 — desk/001 Harvest and Linear reads page past their first page

**Decided:** nothing beyond the worker's decision 59 (a shared `take_capped` pages Harvest entries at
`per_page=100` to 2,000 per account and Linear's assigned issues at 50 a page to 500 per workspace;
both caps `[chosen]`; `POST /harvest/entries` and `GET /linear/mine` carry `truncated`, and a cut
entries answer notes `total_hours` is a lower bound; `/pickup`, the 45-day polish read and a day's
`logged_hours` ignore the flag). The fleet's first `desk` unit: linked `embarch-doc` and
`embarch-fleet` beside it at `.worktrees/embarch-desk/`; the assembler created `history/desk.md`.
**Leg close, for the next leg:** `ui/open.md` is 5,117 of 5,120 B and `ui/074` is parked, so any
`ui` worker that adds a bullet there must compact it inside its own unit; `chat/004` now holds
`embarch-chat/decisions/timeline.md` (12,144 of 12,288 B); the overdue ledger's next entries are
owner-only (`suite/030`, `doc/031`) or parked with nothing payable (`study-designer/026`), then
`ui/074`. `embarch-smp` has no links under `.worktrees/` yet. The owner's uncommitted
`embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/desk/001-connector-reads-past-first-page` (code `3f56975`, ff onto `880d970`; doc
`58b0ee4f`, cherry-picked). Gate re-run on the merge: build, `cargo test` 120 pass, clippy
`-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not run against the live APIs: Harvest `/time_entries` paging and Linear's
`viewer.assignedIssues` cursor follow the shapes `targets` and `scope_issues` already use, tested on
synthetic pages only. Not deployed: the desk service on :4891 is the owner's to rebuild.
**Budget:** PROCEED, weekly 51.1% at start; end figure in the leg's final report.
**Least sure about:** the HTTP paging loops themselves never ran; the tests drive `take_capped` with
canned pages, so a wrong `next_page`/`endCursor` read would pass every test.

## 2026-10-26 00:27 — chat/002 a background Agent's card shows the subagent's report

**Decided:** nothing beyond the worker's decision 90 (the card's result is the hand-back, read from
the `isMeta` peer line carrying `origin.handback` before the meta drop, falling back to the
subagent's last reply with `parent_tool_use_id`; the launch reply's `agentId` fills `tasks` so a
reload finds the card; the stream-json hand-back shape is marked assumed). `chat/003` rode in the
same branch, as it asked. **Worth the owner's eye:** trying to record a real hand-back, the worker
launched a subagent run with `--permission-mode bypassPermissions`; the auto-mode classifier refused
it ("Create Unsafe Agents") and the worker did not retry. Nothing in the landed diff launches a
process. The worker filed `tasks/chat/004` (blocked, `In flux: yes`, due 2026-11-02):
`decisions/timeline.md` is at 12,144 of 12,288 B.
**Merged:** `agent/chat/002-agent-card-shows-the-hand-back` (code `90c6707`, ff onto `82b82e0`; doc
`4b340782`, two commits cherry-picked onto `59712c51`). Gate re-run on the merge: `npm ci`, build,
typecheck, `npm test`, `test:webview` all green, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, not hardware: record a hand-back on the live stream-json wire from an
owner session where a subagent calls SubagentHandback (written into the retired task and decision
90). Not installed: the `.vsix` is the owner's to rebuild.
**Budget:** PROCEED, weekly 51.1%, wave 6.
**Least sure about:** decision 90's primary path has never been seen on the wire, only in a
transcript; if stream-json never emits the hand-back line, the card shows the fallback (the
subagent's last reply), which a reload cannot rebuild.

## 2026-10-26 00:23 — core/097 a console exchange's write survives a throttling device

**Decided:** nothing beyond the worker's amendment to decision 79 (the write retries
`TimedOut`/`WouldBlock`/`Interrupted`/zero-length results until the request's `timeout_ms`, resuming
from the reported count, and past it the exchange fails naming how many bytes were taken; the port
timeout is `timeout_ms` for the write and back to 50 ms for the read poll). Retired the task with its
bench box unticked, as `core/096` was: the debt below is the record. Filed `tasks/core/107` from the
reviewer's below-bar note: the read's deadline now starts after the write, so one exchange can take
`2 × timeout_ms` plus `port_wait_ms`, past the 15 s client timeout decision 79's cap was sized under.
**Merged:** `agent/core/097-exchange-write-throttled-device` (code `3dba64b`, ff onto `0d712cd`; doc
`bae8d660`, cherry-picked). Gate re-run on the merge: build, `cargo test` 279 pass / 2 ignored, clippy
`-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** three, all from this unit. (1) On the STM32G0 Zephyr CDC ACM board (the field
board, not this bench): send a 960-character line through `POST /signals/{name}/exchange` with shell
echo on and `timeout_ms` ≥ 2000; the device's own byte count must be 960. (2) Confirm Windows
`serialport` honours `set_timeout` mid-session (assumed, not measured). (3) Native Windows build of
`embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 51.1%, wave 6.
**Least sure about:** the `set_timeout` switch between write and read is the whole fix on the real
port and only a fake port has exercised it; if Windows ignores a mid-session change the field bug is
untouched while every test passes.

## 2026-10-26 00:21 — api/113 embarch-api/open.md out of reserve by deleting answered questions

**Decided:** unparked `api/113` (overdue since 2026-10-01; the ledger's oldest *payable* entry, since
`suite/030` waits on the owner's `tasks/doc/045` and `doc/031` is owner-only). Its `In flux: yes`
argued against shortening live prose, but `DOC-BUDGET.md` names a 5 KB `open.md` as a role cap with
no seam, whose remedy is deleting answered questions, which shortens nothing live; the flux line was
rewritten to say so. **Leg start, for the record:** drained 42 inbox drops (`df57ce53`: api/133-137,
atlas/017-021, core/104-106, desk/001-004 and smp/001 as two new scopes, dev-bench/041-044,
outpost/026-027, study-designer/072-076, topology/061-063, ui/079-087, umbrella/091). Completed
`api/134`'s header (the worker's drop had no `State:`); reclassified `outpost/027` `none` to
`toolchain` (native_sim builds against a Zephyr tree no worktree carries). Day-fold of 2026-10-25
done by an `embarch-log-folder` (30,538 to 29,802 B), riding in this commit. Atlas still not
dispatched (`tasks/doc/089`).
**Merged:** `agent/api/113-compact-api-open` (doc `12c59b8d`, cherry-picked from `988469e7`; no code).
`open.md` 4,714 to 3,780 B, under the 3,891 B floor: five answered items went, with the facts that had
no other home moved first into decision 70 and `interfaces/config.md`. Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `validate dev-bench` at step 0: probe `001057729826` not attached, not a
mismatch; `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`.
**Budget:** PROCEED, weekly 51.1%, wave 6 (four units dispatched at once).
**Least sure about:** `interfaces/config.md` is now 10,063 B and `decisions/hardware-selection.md`
about 10.4 KB; both outside reserve today, but this pass moved bytes rather than removing them.

## 2026-10-26 00:00 — core/096 flash `erase: true` skips alias and option-byte regions

**Decided:** nothing beyond the worker's decision 84 (erase touches only non-alias, writable NVM
regions; every kept region is checked for a flash algorithm before anything is erased; `POST /flash`
answers `{flashed, chip, erased}`; never a chip-erase fallback, consistent with decisions 32 and
36). The API half (print the erased ranges) is the worker's drop `inbox/api-flash-print-erased-ranges.md`.
Filed `tasks/doc/090` (owner): `embarch-core` now path-depends on `../embarch-smp`, which
`.claude/leg.md`'s link table omits; the worker made the link itself and I left it in place at
`.worktrees/embarch-core/embarch-smp`.
**Merged:** `agent/core/096-flash-erase-skips-alias-regions` (code `0d712cd`, ff; doc `ec80c3d3`,
cherry-picked from `8f0b1ac2`). Gate re-run on the merge: build, `cargo test` 277 pass / 2 ignored,
clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two, both from this unit. (1) STM32G0B1VE bench check: write a non-erased word in
a partition the image does not cover, flash with `erase: true`, `mem-read` it back as `0xFFFFFFFF`,
confirm `erased` is `["0x08000000..0x08080000"]` and the image boots; the algorithm-selector check
was tested only on a synthetic memory map. (2) Native Windows build of `embarch-core`, owner's, from
the main checkout.
**Budget:** PROCEED, weekly 47.5%, wave 6.
**Least sure about:** my own `check-docs.py | tail -1 && fold-commit.py` let the chat/001 fold commit
over a red gate (the `| tail` masks the exit, `tasks/doc/086`'s shape, which I knew about): caught
before the push and amended (`7da4011c`). Run the gate unpiped before every fold.

## 2026-10-25 — 3 units

*Folded by the supervisor's fold agent on 2026-10-26: per-unit decision narrative, gate-re-run detail and "least sure about" reasoning went; git holds them.*

**Carry forward:**
- Leg start: first leg after a 26-day gap; drained all 50 inbox drops into the queue (`ee7d80c1`, numbers in its message; doc/089 added: `gate.md` has no Python bullet, so no `atlas` task was dispatched). Folded 2026-09-29 and rolled 2026-09-17 (`3030aed`).
- Linked `embarch-dev-bench` beside the doc worktrees (`.worktrees/embarch-doc/embarch-dev-bench`): clears the worktree-only `check-links` red on `decisions/pd-bench.md` (`tasks/doc/085`'s shape).
- Tasks filed: `topology/060` and `dev-bench/040` (both `blocked`, due 2026-11-01, split-first) for three reserve files the owner's 2026-10-06..13 commits left unfiled (`embarch-topology/decisions/enrollment.md`, `embarch-topology/spec.md`, `embarch-dev-bench/spec.md`), which the over-cap red had masked; `api/132` (new `zephyr.rs` comments cite decision 64, about retired config keys, a wrong citation `check-decision-refs.py` passes); `chat/003` (a CSS comment cites nonexistent decision 90; fold into chat/002).
- `study-designer/026` unparked (its condition fired 2026-09-17 on owner commit `685b691c`, which pushed `open.md` 327 B over cap; overdue since 2026-10-04, made `check-doc-size.py` red on main), paid, and re-parked `blocked` (nothing live payable; the debt stays overdue on a park).
- First `chat` unit: set up `.worktrees/embarch-chat/` with `embarch-doc`, `embarch-fleet`, `embarch-desk` links. `history/chat.md` created by the assembler. `tasks/chat/002` (hand-back card) now unblocked.
- Open caveats: api/122 checked against Zephyr's `dts.cmake` only, an existing test's expectation changed from empty-`Ok` to the new error (reviewer traced in-crate callers, not `embarch-ui`); chat/001's idle-turn case (CLI never starts a turn) unrecorded, decision 89 marks it assumed.
- Budget: PROCEED, weekly 47.5%, wave 6 throughout.

**Decisions made on the owner's behalf:** none beyond the workers' own: decision 86 (api/122: shortened `<board>.dts` stem accepted only for a one-SoC `board.yml`, refused for multi-SoC and for both stems present; "boards found, every candidate dropped" is `ScanError::AllBoardsDropped`, never `Ok(vec![])`) and decision 89 (chat/001: a CLI-sent `user` line is a `note` row, never an owner bubble; panel-written `turnOrigin: "sdk"` lines with no `origin` stay the owner's). Decision 75 plus the authoring decision's RunProtocol amendment and `interfaces/eap.md` carry what study-designer/026 removed from `open.md`.

### study-designer/026 open.md under its cap; main's doc gate green again
**Merged:** `agent/study-designer/026-compact-open-md` (doc `3f33bc0c`, `91294f77`, ff; no code). `open.md` 5,447 -> 4,473 B. Gate 11/11 green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `validate dev-bench` at step 0: probe `001057729826` not attached, not a mismatch; Core sees only J-Link `000852006107`. `api/059`, `dev-bench/035` stay `open`.

### chat/001 a message the CLI sends Claude is never an owner bubble
**Merged:** `agent/chat/001-cli-turns-are-not-the-owners` (code `82b82e0`, ff; doc `c25be23c`, cherry-picked from `98c6ec25`). Gate: build, typecheck clean, `npm test` 216 pass / 0 fail / 67 skipped (no `EMBARCH_DESK_BIN`), `test:webview` pass, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not installed: the `.vsix` is the owner's to rebuild.

### api/122 zephyr-west accepts a single-SoC board's shortened `<board>.dts`
**Merged:** `agent/api/122-zephyr-west-single-soc-dts` (code `2f3749b`, ff; doc `c98c1a40`, cherry-picked from `e303a1f8`). Gate: build, test green, clippy `-D warnings` clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Checked against Zephyr's `dts.cmake` source only, not a real build of a single-SoC board through `list_targets`; the field repo that reported it is the natural first use.
## 2026-09-29 — 17 units

*Folded by the leg of 2026-10-25 from 17 entries (~21 KB): per-unit narrative, gate transcripts, "least sure about" musings and leg-close prose went; git holds them. Last activity before a ~4-week gap.*

**Standing items for the next leg**
- `tasks/core/091` is paid (`surfaces.md` 89.9% after core/089) but still on disk: my `git rm` was classifier-refused twice (the api/121 rm went through). Owner must remove it.
- Windows-only findings from api/108 (two unused imports in `embarch-core-client/src/token_discovery.rs`, `config::` fixture bug with backslash TOML paths) are closed by api/121; nothing left to file.
- `api/108`: decision 75 keeps its unix-only qualifier and `tasks/api/108` stays `open`, because the kill path has never run on Windows. Do not mark it done or drop the qualifier without a real-Windows kill of a timed-out forked tree.
- Overdue size debts `suite/030` (blocked) and `doc/031` (owner-only) wait on the owner; reserved paths.
- Stale remote `agent/*` branches nobody owns: `api/096-...-doc`, `core/052-...`, `ui/059-...` (also in embarch-ui), and `core/081-...-doc` (its second commit `6f42cf62` task-file only, deliberately not landed). Worth a look.
- Owed: native Windows build of `embarch-core` (core/090, `src/flash_backend.rs`); owner runs it from the main checkout.
- `tasks/ui/078-compact-ui.md` overlaps older open ui compaction tasks 021/043; not reconciled. `tasks/ui/078` set `blocked` (due 2026-10-13). `tasks/doc/087` is `Owner: required` (DOC-COMPACTION-PASS.md reserved); `tasks/doc/086` likewise (a refused `fold-commit.py` does not stop a chained push; use no `| tail` masking its exit). `ui/075` squeezed to 9,031 B vs 9,040 B reserve line; reviewer finding below is still in `inbox/`.
- Pending owner fragment `changelog.d/ui-launcher-focus-existing-tab.changed.md` left in place on purpose (owner commit `615b57bd`).
- Use absolute paths when creating worktrees (relative path under `git -C` landed them inside the repos).
- Bench: dev-bench probe `001057729826` not attached at step 0, not a mismatch; `api/059` and `dev-bench/035` stay `open`.

**Merged** (no code commit means doc-only; every merge ff or cherry-picked, gate green, docs 11/11)
- core/084: doc `e3b57ea6` (leg start `f411caa1`). 14 of 17 rows of core `decisions.md` size column corrected.
- api/120: code `5c6b199`, doc `64faa5f3`. main.rs cites study-designer decision 63.
- ui/069: doc `efa77706` (rebased onto `64faa5f3`). Decisions 3+28 split to `decisions/launcher.md`, tabs table to `spec/tabs.md`; filed ui/075.
- study-designer/069: doc `7301e0a5` (rebased onto `2966a95b`). gatt-extract.md squeezed to 89.9%; filed ui/076.
- study-designer/066: doc `df01f487`. File count made unstale.
- ui/076: doc `30b3e169`. Decision links repointed at the index.
- core/095: code `2590885`, doc `129b38aa`. /load comment cites decision 62; no Windows build (comment-only diff).
- api/083: doc `43b9d2b4`. spec.md §§3-7 split verbatim into `spec/implementation.md`.
- core/090: code `ae66d3f`, doc `f3cb903e`. `nrfutil_erase_options()` extracted and tested.
- api/119: doc `b3085b2a`. Decision 72 mirror count is six; drained `history-api-seven-should-be-six.md`.
- ui/075: doc `e4167090`. spec.md 9,275 to 9,031 B.
- core/081: doc `55e2b314` (from `ba07d029`; `6f42cf62` not landed). Stale decision-64 bullet removed.
- core/083: doc `bc355356`; core/089 claim `d1991ea2`.
- ui/077: doc `5df5d116`. "served by the binary" restored; filed ui/078.
- core/089: doc `2aa45f64` (rebased from `bc094a7c`). Decision 59 citations restored.
- api/108: code `cfa8197`, doc `f97d7a3a`. Windows Job Object tree-kill; task stays open.
- api/121: code `b01f203`, doc `67dbe33b`. Windows reds fixed (`toml_path()` test helper). Worker's code commit lacks Co-Authored-By.

**Blocked:** nothing.

**Reviewer:** no findings. (api/121)
**Reviewer:** no findings. (api/108)
**Reviewer:** no findings. (core/089)
**Reviewer:** no findings. (ui/077)
**Reviewer:** no findings. (core/083)
**Reviewer:** no findings. (core/081)
**Reviewer:** 1 finding — inbox/ui-075-dropped-served-by-binary.md (ui/075; restoring the phrase landed as ui/077)
**Reviewer:** no findings. (api/119)
**Reviewer:** no findings. (core/090)
**Reviewer:** no findings. (api/083)
**Reviewer:** no findings. (core/095)
**Reviewer:** no findings. (ui/076)
**Reviewer:** no findings. (study-designer/066)
**Reviewer:** no findings. (study-designer/069)
**Reviewer:** no findings. (ui/069)
**Reviewer:** no findings. (api/120)
**Reviewer:** no findings. (core/084)

**Hardware debts:** native Windows build of `embarch-core` owed (real code change in `src/flash_backend.rs`); owner runs it from the main checkout.

**Budget:** PROCEED throughout, weekly 22.0% to 29.3%, wave 6.
## 2026-09-28 — 16 units

*Folded by an `embarch-log-folder` leg, 2026-09-29, from sixteen unit entries (15:49–18:00). Per-unit
narrative reasoning is dropped; every SHA, every `**Reviewer:**` line and the one real hardware debt
survive below. This was the fleet's first day back after the 2026-09-17→09-28 stop; `main`'s doc-size
gate was RED on arrival (three expired clocks) and the leg's first eight units were split/squeeze
compactions paying that debt down, several unparking `In flux: yes` tasks whose own stated conditions
had lapsed or been satisfied by a verbatim move.

**Units, oldest first:**

1. **dev-bench/012** 15:49 — `spec.md`/`open.md` squeezed out of reserve (doc **`0c528a9f`**, base
   `edc278bb`). Unparked on its own 2026-09-22 clock. Decided: a leg arriving on a red `main` pays the
   red first, judging each unit on "adds no new red" until paid. Also folded 2026-09-17 (50 units,
   119 SHAs, done by an `embarch-log-folder`) and rolled 09-16. Slip: claim commit **`b25a513f`** for
   `ui/073` also deleted this task's retired file (harmless, on `main`). Filed `tasks/doc/085`
   (leg-worktree `check-links.py` red on `embarch-ui/decisions/study-authoring.md` via owner commit
   `685b691c`; fixed with a symlink). Bench state: dev-bench probe **`001057729826`** not attached;
   DUT probe **`000852006107`** attached but USB Communication Error; Core's recorded DUT hardware ID
   now `2f77b9c3f85b29e9`, `fleet-hardware.py`'s stale buffer still says `834f2559f10a6cdf`.
**Reviewer:** no findings.
**Hardware debts:** none created.

2. **ui/071** 15:50 — `embarch-ui/open.md` compacted to 4,867 B, evidence moved into
   `decisions/trace-rows.md` and `decisions/time-chart.md` (doc **`6d204cd3`**, base `0c528a9f`),
   including the **`b1e9ec7d`** GATT-vs-trace placement result. Filed `tasks/ui/074` (blocked,
   `In flux: yes`, due 2026-10-05) for the remainder.
**Reviewer:** no findings.
**Hardware debts:** none created. Two open halves kept, both hardware, neither ever run: the
   live-Core `/study/{id}/streams` HTTP cost over three calls, and a power-capture check of placement.

3. **core/094** 15:56 — decision 74 moved to new `decisions/outpost-preflight.md` (doc **`1a05988c`**,
   base `91b9736b`; code base `48dc591`, zero commits). Supervisor repointed the `embarch-ui`
   `firmware-build.md:7` link the split broke, at landing rather than filing a task (not announced
   first, named here per `.claude/leg.md`). Worker added a 72-byte pointer in `interfaces/studies.md`
   against the dispatch note, judged needed by the reviewer.
**Reviewer:** no findings.
**Hardware debts:** none created — decision 74's own hardware evidence (three reads on nff_dev@7,
   171–258 ms, `after_reset=false`, 2026-09-19) moved with it unchanged.

4. **ui/073** 16:02 — two verbatim splits: decisions 8/25/42 out of `shell.md` into
   `decisions/design-system.md`; decision 44's two sections out of `topology-boards.md` into
   `decisions/saved-benches.md` (doc **`ccf2eacf`**, base `9d7f2951`; code base `c5857fd`/`c5857fd9`,
   zero commits). Worker also repointed a pending fragment it did not write (owner's
   `changelog.d/ui-brand-token.added.md`, decision 25 → `decisions.md`). First green `check-docs.py`
   (all 11) on `main` since the clocks expired.
**Reviewer:** no findings.
**Hardware debts:** none created.

5. **core/092** 16:38 — `arrivals`/`load`/`load/spans` rows moved from `interfaces/studies.md` into
   new `interfaces/streams.md` (doc **`df7cb35e`**, base `a6cace62`; code base `48dc591`, zero
   commits).
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move, no source change, no native Windows build owed.

6. **api/118** 16:44 — decision 59's parenthetical amended in place (`SignalLink` stopped being called
   a mirror) (doc **`0db25814`**, base `e76d35cd`; code base `517a7e3`, zero commits). Reviewer found,
   below its bar, that decision 72's "seven" retired mirrors vs. six named types is pre-existing
   (authored **`c62cc870`**, 2026-09-12) — filed as `tasks/api/119`.
**Reviewer:** no findings.
**Hardware debts:** none created — one parenthetical.

7. **dev-bench/014** 16:48 — decisions 30/35 moved to new `decisions/link-limits.md` (doc
   **`027d62df`**, base `9807430c`; code base `edc278bb`, zero commits). Unparked at claim
   (**`b63ddeda`**) on its own lapsed clock: `link.md` untouched since **`84243a33`** (2026-09-08).
   Slip: a refused first fold attempt
   still let `git push origin HEAD:main` run (`| tail` ate the exit status) — same pattern as
   `core/046` below; two legs in a row.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

8. **study-designer/067** 16:52 — `.eap` constants split from `interfaces/limits.md` into new
   `interfaces/eap-limits.md`; decision 71 moved to `decisions/payload-meaning.md` (doc **`88e0b2de`**,
   base `aef01be1`; code, zero commits).
**Reviewer:** no findings.
**Hardware debts:** none created — two verbatim moves.

9. **ui/072** 17:08 — decision 14 split into new `decisions/project.md` (doc **`de3efeef`**, base
   **`d47c32e4`**; code base `c5857fd9`, zero commits, fast-forward, no rebase). Slip noted: a
   dispatch-time worktree add resolved a relative path inside the repo instead of beside it; caught
   and moved before any worker started, nothing committed there.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

10. **core/093** 17:13 — decisions 70/72/73 split into new `decisions/streams-live.md` (doc
    **`b594ac91`** + **`23987bd3`**, base `8b4786d3`; code base `48dc591`, zero commits). Unparked at
    claim (**`9ee5de6b`**): its `In flux: yes` block (72/73 unvalidated on hardware) does not forbid
    the verbatim-move remedy the task itself named; flux otherwise unlapsed (bench still unplugged).
    Supervisor repointed `embarch-ui/decisions/live-study.md:30` (decision 70) at landing. Filed
    `tasks/core/095` from the reviewer's aside (unnumbered decision citation in `src/study.rs`).
**Reviewer:** no findings.
**Hardware debts:** none created. Decisions 72 and 73 are still unvalidated on hardware — a traced
    study with the outpost bridge attached — the split moved that debt, it did not pay it.

11. **study-designer/068** 17:19 — decision 77 split from `decisions/declares.md` into new
    `decisions/builds.md` (doc **`01d209d8`**, base `fc08de8f`; code base `15087ae`, zero commits).
    Supervisor repointed `embarch-ui/decisions/firmware-build.md:7` to the index (`decisions.md`),
    a different repoint convention than `core/093`'s topic-file repoint one unit earlier. Rewrote
    `tasks/study-designer/066`'s now-false premise (seventeen files → twenty) and left it open.
**Reviewer:** no findings.
**Hardware debts:** none created — a move and two pointers.

12. **umbrella/088** 17:23 — `check-15` bullet corrected to stop saying the hash is unbuilt;
    `open.md` squeezed 4,372 → 3,905 B (doc **`ecc2880c`**, base `5bb668d6`; code base `2764e89`,
    zero commits). Worker declined to consume `binary_sha256` in check 15 itself — a real behavior
    change needing its own decision — and filed `tasks/umbrella/089` (below) instead. Reviewer noted
    pre-existing stale text in `open.md`'s own "why `saved.host` was left unfixed" item.
**Reviewer:** no findings.
**Hardware debts:** none created. `open.md` bullets carrying debts unchanged in substance: check
    13 (one `doctor` run on the primary bench), check 5 (a Linux box with Core native), decision 51's
    three-step real-machine confirmation.

13. **study-designer/032** 17:47 — §4 ("What a study carries") moved to new
    `embarch-study-designer/spec/carriage.md`; §§5/6/7 renumbered to §§4/5/6 (code **`b9a2d5d`**,
    base `15087ae`; doc **`9fe1ec5c`**, base `01190ef5`). Unparked at claim (**`1db80acc`**): §4's
    last edit was **`ac9c2116`** (2026-09-18), a full leg quiet as the task's own unpark condition
    required. Filed `tasks/api/120` for the one repointed citation the worker couldn't reach
    (`embarch-api/src/main.rs:538`).
**Reviewer:** no findings.
**Hardware debts:** none created — a move, a renumber and a comment.

14. **core/046** 17:52 — decisions 42/46/60 moved to new `decisions/route-sweep.md`;
    `auth.md` 11,356 → 3,799 B (code **`fdb9b1d`**, base `48dc591`; doc **`b887482f`**, rebased from
    **`2e6173ea`** onto `9d7b3df1`). Unparked at claim (**`11c9ae7d`**): the task's own prediction ("the next new HTTP
    route ... likely to land here") was falsified by four routes landing in `build_router` elsewhere
    since **`f6e23215`** (2026-09-12) — `4251af3`, **`d73a73a`**, **`e50de6d`**, **`f832043`** — none
    touching `auth.md`. Supervisor corrected the worker's Size cell (2.9 KB claimed vs. measured
    3.8 KB). Slip: same refused-fold-still-pushed pattern as `dev-bench/014` — **`b887482f`** reached
    `origin/main` a few minutes before its fold.
**Reviewer:** no findings.
**Hardware debts:** none created. The `api.rs` change is a comment, so no native Windows build
    owed for it.

15. **api/111** 17:56 — decisions 71/73/76 moved to new
    `embarch-api/decisions/validate-kind.md` (code base `517a7e3`, zero commits; doc **`c8dbb6e6`**,
    base **`8f54d73a`**, rebased from `1cd74544`). Unparked at claim (**`e92f430e`**): the task's own
    second unpark condition ("once the file is judged safe to split") is satisfied by its own named
    seam.
**Reviewer:** no findings.
**Hardware debts:** none created — a verbatim move.

16. **umbrella/089** 18:00 — check 15 now hashes the located `embarch-core` binary once
    `core_version` already matches and compares it to `/status`'s `binary_sha256`; a mismatch is
    **Warn**, never Fail; missing hash on either side falls back to the old version-only Pass (code
    **`b55809c`**, fast-forward onto **`2764e89`**; doc **`ab3a56e4`**, rebased from **`57c380dd`**
    onto **`3d01e141`**). Wrote `embarch-umbrella` decision 56; amended decision 34 as "narrowed, not
    retired". Filed `tasks/umbrella/090` (blocked on the hardware debt below, due 2026-10-19).
**Reviewer:** no findings.
**Hardware debts:** **two `doctor` runs on the primary bench machine**, recorded in `open.md`'s
    check-15 bullet: one against the installed Core at a matching version and binary, confirming the
    new closed-gap Pass renders; one against a deliberately stale same-version install, confirming
    the new Warn fires with a sensible fix line. Either one also unparks `tasks/umbrella/090`. No live
    Core was touched.

**What the next leg cannot recover from git alone:**

- **The owner posted `fleet stop` in #embarch-fleet at 18:00:14** (`ts` **`1790640014`**.685759),
  during the last unit's fold; seen at 18:02 after all four of that leg's units had landed. Nothing
  was in flight; the leg deleted `.fleet/pump` and posted its stop line in the thread. **No successor
  leg should start.**
- **`| tail` eats the push exit status.** Twice this day (`dev-bench/014`, `core/046`) a refused fold
  attempt still let the chained `git push origin HEAD:main` run, landing the worker's commit on
  `origin/main` a few minutes ahead of its fold entry — legal but a pattern now, and
  `fold-commit.py` refusing is not sufficient while the push rides the same `&&` chain behind a pipe.
- **Six `In flux: yes` tasks were unparked at claim this day** (`dev-bench/012`, `core/093`,
  `study-designer/032`, `core/046`, `api/111`, plus `dev-bench/014`'s own-clock lapse), each on the
  task's own stated condition or the split-first rule that a verbatim move restates nothing — but
  nothing besides these log entries records that "the supervisor decides the park no longer applies"
  is now the fleet's normal path out of `blocked`.
- **Two different repoint conventions for a cross-repo link a split breaks** now coexist:
  `core/093`→`ui/live-study.md` pointed at the new topic file; `study-designer/068`→
  `ui/firmware-build.md` pointed at the index. Both pass the gate; `tasks/doc/055` is the owner's to
  settle which is canonical.
- **Decision 44 (`embarch-ui`) now spans two files** (`topology-boards.md` and the new
  `decisions/saved-benches.md`), indexed as `44 (saved bench)` — a precedent already set by decision
  10, but `check-decision-refs.py` cannot tell which half a bare citation means.
- **`tasks/api/119`** (decision 72 says "seven" retired mirrors, names six) may be a bigger defect
  than a miscount — `api/117`/`118` both repeated "seven" from the heading, so a seventh retired
  mirror may be undocumented; settle it from `git show c62cc870`, not from either doc.
- Two bench probes are still the live blocker for `tasks/api/059` and `tasks/dev-bench/035`: dev-bench
  probe **`001057729826`** not attached; DUT probe **`000852006107`** attached but unopenable
  (USB Communication Error) — neither is a mismatch, and `fleet-hardware.py`'s buffer is stale
  (says `834f2559f10a6cdf`/attached, real ID is now `2f77b9c3f85b29e9`).
- Size ledger moved **20 overdue → 4 overdue** across the day (`dev-bench/012` start, `umbrella/089`
  close). Oldest remaining payable overdue at close: `study-designer/069` (`gatt-extract.md`, 36 B
  left, due 09-27) and `api/083` (blocked on flux, names its own split seam). `suite/030` and
  `doc/031` remain owner-only. Queue at close: 12 dispatchable over 4 scopes.
*Days 2026-09-17 to 2026-09-17 rolled to [log-archive/supervisor-log-2026-09-17-to-2026-09-17.md](log-archive/supervisor-log-2026-09-17-to-2026-09-17.md).*
