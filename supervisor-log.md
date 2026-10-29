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

## 2026-10-29 17:06 — atlas/014 the live shell tells silence, a lost port and an empty success apart

**Decided:** nothing suite-wide. `live.shell_status` gives five answers, shared by `shell`, `shell_run` and the CLI
(exit 0/1/2/3): the output; an empty success with what `retval` says it returned (asked on the console that
answered); did not run (only when provably before the write); nothing came back (no "longer timeout" advice; echo
verdict, port VID:PID/product/serial and DHCSR state from Core decision 85); sent and the port went away or unknown
whether it ran (shown, never resent). **The safety rule, which I and the reviewer both checked against
`embarch-core/src`:** `Console.exchange` falls through to the next console only on an error text Core raises before
the write (`nothing was written`, `signal-mismatch`, `; core state: ` on a port-wait 409, an undeclared or non-writable
signal, embarch-api absent); every other failure, a capture-owned port's included, raises with `may_have_written` and
is not resent, and an older Core without the wire fields counts as "may have run". `retval` is skipped when the pinned
build's `kconfig.json` lacks or unsets `CONFIG_SHELL_CMDS_RETURN_VALUE`; with no `kconfig.json` it is asked and a
`command not found` reply is read. **One deviation accepted**: a command that ran and returned nonzero exits 0 (it
answered), stated in DESIGN.md. `live reg-read` and `live stacks` now exit 1 on a failed read. DESIGN.md's CLI table
gained the `kconfig-extract <atlas>` row owed by `atlas/019`.
**Merged:** `agent/atlas/014-shell-tells-silence-lost-port-and-empty-success-apart` (code `5e7df62` on `b23a73d`, ff;
doc `f2b577f4`, the worker's commit rebased in its own worktree onto `ce45fb98`, ff). Gate on the merge result:
worktree venv `pytest -q` 465 passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client
names clean, `check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-attended or a bench leg, on the dev bench with a DUT console declared, a Core with decision
85 deployed and an image built with `CONFIG_SHELL_CMDS_RETURN_VALUE=y`: `embarch-atlas live shell <a command that
prints nothing>` prints "printed nothing and returned 0" and exits 0; a refused value prints its nonzero code; with
the DUT unpowered or held in reset, `live shell` exits 2 with port identity and core state; a command that drops the
DUT's USB port exits 3 and is not resent on a second console. The task file carried this and is retired by this fold.
**Budget:** PROCEED, weekly 26.0% at leg start, 27.1% at leg end, wave 6.
**Least sure about:** the not-written decision rests on matching Core's error wording, because embarch-api forwards no
HTTP status; a future Core rewording a pre-write error fails safe (no resend), but a future post-write error that
happened to contain "nothing was written" would resend.
**Leg close (next leg, read this first):** 4 of 4 units (`atlas/007`, `atlas/018`, `atlas/019`, `atlas/014`), all
landed, none blocked, all four reviews "no findings". Started 16:38 at `d15e820c`; every unit ran alone because only
`atlas` was dispatchable. **No `suite` task is announced.** **Dispatchable now:** 8 `atlas` tasks (`004`, `005`,
`010`, `011`, `013`, `016`, `020`, `023`) and nothing else, so the spread gate fires again; no sweep source changed
since 15:26 as of 16:39. `atlas/023`'s Done-when names `check_public.py`, which does not exist in the repo (the
`test_public_guard` test is the check); `atlas/020` shares `update.py` lines with the toolchain-gated `atlas/001`.
Bench unchanged (`dut` attached, `dev-bench` not; `api/059`, `dev-bench/035`, `038` open). The `toolchain` lane (17
tasks) is still unstarted by any leg; the 2026-10-28 dream offered it and the owner chose another option, so I did not
start it. Owner-only: `tasks/doc/093`, `094`, `095`. Ledger: nothing overdue (next `dev-bench/040`, 2026-11-01,
blocked). `changelog.d/umbrella-check-17-measured.decided.md` is still the owner's, unconsumed. Nothing deployed.

## 2026-10-29 17:03 — atlas/019 an atlas names a board with no netlist and a Kconfig it failed to extract

**Decided:** nothing suite-wide. **One atlas design call, by the worker, accepted:** `update` does **not** stop for a
declared board with no netlist (it cannot make the netlist, and stopping would block every firmware bump on a board
not ready yet); a netlist made from a changed PDF still stops it. Written in DESIGN.md "When `update` stops". Instead
`join` logs the board, writes `missing_boards` into `inputs.json`, and `project.atlas_state` turns it into a stale
reason naming the fix (`schematic <pdf> --board X`, then `join`), so it reaches `status`, the MAP's stale line and
every `src:` line through `atlas/015`'s `stale.py` (whose cache key includes `inputs.json`, which I checked); the MAP
boards section adds a "NO netlist" line. `config` on an atlas whose stamp says `kconfig: not extracted: <why>` quotes
the reason and names a new verb, `kconfig-extract <atlas>`, which reruns the extraction over the build dir the stamp
names with `build`'s Zephyr-match guard kept, and says only `build --force` can help when the dir is gone or Zephyr
moved. **Gap I found after the review:** DESIGN.md's CLI verb table had no `kconfig-extract` row; I carried it to
`atlas/014`'s worker rather than fixing it here.
**Merged:** `agent/atlas/019-join-and-build-name-what-they-left-out` (code `b23a73d` on `5f208ad`, ff; doc `93791ed1`,
the worker's commit rebased in its own worktree onto `84544f6f`, ff). Gate on the merge result: worktree venv
`pytest -q` 455 passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names clean,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `kconfig-extract` is tested with the extraction monkeypatched, never over a real Zephyr build.
**Budget:** PROCEED, weekly 26.0% at leg start, wave 6.
**Least sure about:** the MAP's stale line still ends "run /atlas-update", which cannot fix a missing netlist; the
reason text names the real fix and the reviewer called it cosmetic, but a session reading only the line's tail would
run the wrong command. Atlases joined before this carry no `missing_boards` until joined again.

## 2026-10-29 16:56 — atlas/018 every cut answer can be continued with offset

**Decided:** nothing suite-wide. The nine lookups that were cut at their budget with no way to continue
(`part_card`, `doc_toc`, `find_fact`, `register`, `pin_trace`, `config`, `dt_node`, `footprint`, `stacks`) take
`offset` on the function, the `q` verb and the MCP tool; `doc_toc`'s three cut points, `doc_section`'s listing and
the `register` MSB/LSB pair path pass it through. All thirteen lookups now page. DESIGN.md "Query surface" states the
paging contract: offsets count body characters after the header, every page repeats the `src:` header (so `pdf=` and
`stale=` ride on each page), cuts fall on a line boundary unless one line exceeds the budget. A test walks `TOOLS`,
`BUDGET` and the MCP schema as sets, so a new lookup without `offset` fails it; per-tool tests page at a 2-token
budget and assert the bodies concatenate to the uncut answer exactly once.
**Merged:** `agent/atlas/018-every-cut-answer-takes-offset` (code `5f208ad` on `17880f2`, ff; doc `4f1b0e03`, the
worker's commit rebased in its own worktree onto `1cc26877`, ff). Gate on the merge result: worktree venv `pytest -q`
451 passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names clean,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 26.0% at leg start, wave 6.
**Least sure about:** the paging tests use a 2-token budget on fixture atlases; no answer has been paged at its real
budget on a real reference manual's `doc_toc`, which is the case the task named.

## 2026-10-29 16:50 — atlas/007 find_text searches a document's page text

**Decided:** nothing suite-wide. New lookup `find_text <doc> <pattern> [section] [context] [offset]` (MCP tool and
`q find-text`; the lookups are thirteen): case-insensitive regex, falling back to plain text on a bad regex, over
`docs/<doc>/pages/p<NNN>.txt`, one block per hit with page, deepest toc section, `s/<file>` or "not distilled", the
line and context; cut at 2,500 tokens with `next=`. Each answer appends the hits it returned to `<atlas dir>/usage.jsonl`
(write-only; the atlas dir is git-excluded in the firmware repo, so it dirties nothing). **`atlas/012`'s owed hints
are paid**: `doc_section`'s undistilled and not-found answers and `doc_toc`'s not-found answer now name `find_text`.
**Accepted as stated limits:** a page two sections share is credited to the deepest, latest-starting one (toc gives
pages, not lines); the MCP tool keeps `read_only_hint=True` while appending the log (DESIGN.md defines the hint as
"cannot change the board"). Measured on a synthetic 400-page layer: 11-14 ms per query against the 0.5 s bar.
**Leg context (next leg, read this first):** started 16:38 at `d15e820c`, clean recovery (no claims, no unit
worktrees), inbox empty. Bench: `dut` attached, `dev-bench` not, so `api/059`, `dev-bench/035`, `038` stay open.
Ledger: nothing overdue. Spread sweep skipped: no source changed since the 15:26 "nothing filed" line. Only `atlas`
is dispatchable, so this leg runs its units one at a time. I ticked `leg-dispatch` for this unit late, after the
worker had reported (three minutes).
**Merged:** `agent/atlas/007-find-text` (code `17880f2` on `fa9b1b9`, ff; doc `48a9ceea` on `d3a6cd26`, ff). Gate on
the merge result: worktree venv `pytest -q` 445 passed, 2 skipped (real west workspace, built atlas;
`test_public_guard` ran), client names clean, `check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's
atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Never run against a real atlas's text layer; the timing is synthetic (55 lines a page).
**Budget:** PROCEED, weekly 26.0% at leg start, wave 6.
**Least sure about:** DESIGN.md's on-disk layout tree does not list `usage.jsonl` (the "Query surface" text does);
the reviewer called it a doc gap, not a contradiction, and I did not file it.

## 2026-10-29 16:37 — atlas/015 every lookup says when the atlas is behind HEAD

**Decided:** nothing suite-wide. New `stale.py` computes `project.atlas_state` per call, cached on the mtimes of
`.git/HEAD`, its ref and `packed-refs` plus the stats of the stamp, manifest and board PDFs; all twelve lookups'
`src:` lines end `stale=<reasons> (HEAD <sha12>)` when there are reasons, after `atlas/012`'s `pdf=`.
`current_atlas()` treats a `current.json` whose commit is not HEAD as no match and falls through to the newest atlas,
which then reads as stale (the fall-through order is unchanged). The MCP server runs `project.status` at start, in a
try/except; I checked `status` writes nothing to stdout, which would corrupt the stdio protocol. `join.run` calls
`update.rm_todo` before rendering the MAP, so both `update` and a hand-run `build` + `join` show the RM chapters; the
reviewer confirmed `worklist.json` is derived and neither the selection nor frozen units are touched. Live tools
(`reg_read`, `shell`) carry no `stale=`: they read the board. No `features.d` row (no maturity change).
**Merged:** `agent/atlas/015-stale-signal` (code `fa9b1b9` on `197784a`, ff; doc `4dae8850`, ff). Gate on the merge
result: worktree venv `pytest -q` 439 passed, 2 skipped (`test_public_guard` ran), client names clean with history,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 25.8% at dispatch, wave 6.
**Least sure about:** the timing test asserts 5 ms per call over 200 iterations; the worker said "well under 1 ms"
without reading the number off, so the margin is asserted, not recorded.
**Leg close (next leg, read this first):** 4 of 4 units (`ui/059`, `atlas/006`, `atlas/012`, `atlas/015`), all
landed, none blocked. **`ui/059` was unparked by me** and landed on fresh branches; its old branches
`agent/ui/059-diff-new-lines-republish` stay on both remotes for the owner. **No `suite` task is announced.**
**Dispatchable now:** 12 `atlas` tasks and nothing else, so the spread gate will fire again; no sweep source changed
since 15:26 as of 16:16 (this leg skipped the sweep). Bench unchanged (`dut` attached, `dev-bench` not; `api/059`,
`dev-bench/035`, `038` open). Owner-only: `tasks/doc/093`, `094`, `095`. Ledger: nothing overdue (next
`dev-bench/040`, 2026-11-01, blocked). `tasks/atlas/007` now carries an "Also owed" line from `atlas/012` (add
`find_text` to the not-distilled hints). `changelog.d/umbrella-check-17-measured.decided.md` is still the owner's,
unconsumed. Nothing deployed.

## 2026-10-29 16:31 — atlas/012 four lookup misses become the next call to make

**Decided:** nothing suite-wide. `part_card` documents `board="all"` (`""` still accepted, CLI bare `--board` maps to
`all`), and a test asserts no MCP tool's description or schema offers `""`. New `cmsisalias.py`: `register
UCPD1.CFG1` resolves a CMSIS struct member to the SVD register at the same address, reading the header path `mcu
vote --header` recorded in an RM doc's `vote*.json`; no recorded header means no alias and the old "not found".
`doc_section` on an undistilled toc section answers title, pages and the next call; an RM register section points to
`register`; a missing id/title and an unmatched `doc_toc under=` list the nearest titles. `src:` lines on `part_card`
and every `doc_section` answer carry `pdf=<path relative to the firmware repo>`. **Two deviations I accepted:** the
task named `find_text` as a next call, but no such tool exists yet (`atlas/007` builds it), so answers point to
`doc_section tier=text` and a PDF Read — **`atlas/007` should add `find_text` to those hints when it lands**; and the
path went on the generated `src:` line, not the card's LLM-written `Source:` prose. The worker's first docstring used a
real client doc id; the public-guard test caught it before commit, and `check-client-names.py --history` on the branch
is clean.
**Merged:** `agent/atlas/012-query-misses` (code `197784a` on `c71c703`, ff; doc `4b686f3f`, ff). Gate on the merge
result: worktree venv `pytest -q` 434 passed, 2 skipped (`test_public_guard` ran), client names clean with history,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The CMSIS alias is tested on a synthetic header and SVD only, never a real vendor header.
**Budget:** PROCEED, weekly 25.8% at dispatch, wave 6.
**Least sure about:** the alias's struct-layout parser skips any typedef with a nested struct or union, and real
vendor headers have those; how many registers that leaves unaliased on a real part is unmeasured.

## 2026-10-29 16:24 — atlas/006 an external reg_read names the true cause

**Decided:** nothing suite-wide. `ext_reg_read`: a failed read whose own answer says `command not found` reports
"the image has no I2C shell, build it with `CONFIG_I2C_SHELL=y`", with no `device list` and no "Nothing answered".
**The worker detected it from the failed read's answer rather than the up-front probe exchange the task described**;
same answer, no extra exchange per read, and `DESIGN.md` records the choice — I accepted it. `_ext_effects` now
works per sentence: a clear-on-read sentence naming another register (`REG0x..`) or an underscore-named field or
register is charged to that one, and the guard's reason quotes the sentence. `atlas/021`'s `reads_clear` path for
`rclr` fields is untouched (reviewer checked). **Known limits, from the worker:** a plain-word field name (`AVG`) is
not recognised as "another field"; no real BQ25730/INA700/TPS55288 records exist in any fixture, so the tests use
synthetic records shaped like them. **Order note:** this unit's doc cherry-pick reached `origin/main` one push ahead
of its fold, inside `ui/059`'s fold push, because I landed both doc branches before folding either.
**Merged:** `agent/atlas/006-ext-reg-read-states-true-causes` (code `c71c703` on `af410ad`, ff; doc `0a22af11`, the
worker's `4bdde008` cherry-picked). Gate on the merge result: worktree venv `pytest -q` 425 passed, 2 skipped
(`test_public_guard` ran), client names clean, `check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's
atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The no-I2C-shell answer has not met a real board without the shell.
**Budget:** PROCEED, weekly 25.4% at leg start, wave 6.
**Least sure about:** the reviewer observed that a register's own record-level clear sentence naming another
register is now dropped from the carrier and charged only through the field loop; it judged that the intended fix,
and I did not construct a case where the named register ends up unguarded.

## 2026-10-29 16:23 — ui/059 a grown trailing line is republished, not swallowed

**Decided:** **I unparked `ui/059`** (blocked since leg 123's refused merge): its `Unparks when:` was its own fix, so
only a dispatch could end the park — `suite/055`'s leg flagged this. Fresh branches from `origin/main` under a new
name, `agent/ui/059-diff-new-lines-publishes-the-grown-line`, because the old doc branch carried a stale copy of the
task file and both old branches sat on a two-month-old base. **The old branches `agent/ui/059-diff-new-lines-republish`
(code `21a48de`, doc `ec150926`) are left on both remotes**; the fold cannot prove them landed, so deleting them is
the owner's call. The fix: `diff_new_lines` matches the overlap's last line by strict extension and returns
`new[k-1..]` when it grew, `new[k..]` on equality. I read the diff and walked the edge cases (window slid onto a
line that is a prefix of the next, a repeat of the pre-growth text) before landing. New decision 70; decision 13's
closing paragraph, which described the defect, became a one-line pointer (13 was at 0 B). **Leg context (next leg,
read this first):** started 16:15 at `7eb36fa2`, clean recovery, inbox empty, spread sweep skipped (no source
changed since the 15:26 "nothing filed" line). Bench: `dut` attached, `dev-bench` not, so `api/059`,
`dev-bench/035`, `038` stay open. Ledger: nothing overdue. Dispatched `atlas/006` and `ui/059` at 16:18; both
workers reported in under four minutes.
**Merged:** `agent/ui/059-diff-new-lines-publishes-the-grown-line` (code `052990c` on `f6da709`, ff, two commits:
`21a48de` cherry-picked as `9199da5`, then the fix; doc `78235e0c`, ff). Gate on the merge result: build, test (210
+ 8 pass), clippy `-D warnings` clean, client names clean, `check-docs.py` 12/12, ownership `ui` OK on both
branches. Owner's ui checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 25.4% at leg start, wave 6.
**Least sure about:** the worker did not run its five new tests against the unfixed code; the "fails before" half
rests on leg 123's measured table, which covers the same six cases.

## 2026-10-29 16:13 — suite/055 the pre-October tasks all still describe real work

**Decided:** **a supervisor-run suite task, as this leg's last unit**, after its window (`ts` `1793305740.224299`,
closed 14:59:00; thread re-read 15:51 and 16:12, no reply). Candidates re-derived at run time: every live task
added before 2026-10-01, not `done`, not `Owner: required`. **All eleven kept, none closed**, each checked against
`main` today: `api/059` keep (needs a live study; `dev-bench` unattached). `api/108` keep (Job Object code on
`main`, `windows_job` in `build.rs`; the forked-grandchild kill has never run on Windows). `dev-bench/003` keep
(`pc_skip_len_prefixed` still multiplies and adds unchecked, `serial_protocol.c:100-102`). `dev-bench/004` keep
(`goto_state`/`otherwise` still raw bytes at `serial_protocol.c:452,463,547`; only `entry_state` bounded,
`eap_interp.c:456`). `dev-bench/010` keep (constants still typed with `limits::` comments; the CMake read still
serves `DEV_BENCH_WIRE_SCHEMA_VERSION` alone). `dev-bench/016` keep (`scan_seen_names_summary` still only in
`ble_bridge_real.c`, no test reaches it). `dev-bench/017` keep (`tx_scratch` still the whole `dev_bench_message`,
`main.c:78`; `open.md:38` still names it). `dev-bench/035` keep (`main.c` gates `steps_crc_valid` and
`streams_crc_valid` only). `suite/032` keep (`study_ffi_real.c`, the `ESSD_LIB` staticlib target and
`embarch-study-designer`'s `ffi` feature all still exist). `suite/037` keep (Core still serves hello's
`firmware_version`; unparks on the owner's Windows build). `ui/059` keep (`diff_new_lines` in `logs.rs` unchanged
since `ea0227b`, 2026-08-30). Named in the task but already gone: `outpost/018` (folded today) and `suite/030`
(done). **The owner's parked four, recommendation only:** keep all (`api/029`, `outpost/002`,
`study-designer/007`, `ui/007`); each asks for a bench observation and no commit since 2026-09-08 records one.
**Two observations, not acted on:** `dev-bench/035`'s fix is a ztest and C, so `Hardware: bench` looks like it
should read `toolchain`; and `ui/059` is `blocked` on an "Unparks when" that is its own fix, which a `ui` worker
could take now, so it reads as parked work rather than gated work. Both are the next leg's or the owner's call.
**Merged:** no branches (supervisor's own unit). Gate on the result: `check-docs.py` 12/12. Doc SHA is this fold's
commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 25.1%, wave 6.
**Least sure about:** "keep" rests on the code still showing the defect, read by grep at the cited lines; I did
not rebuild or run anything, which is what a `toolchain` task would need to prove the defect live.
**Leg close (next leg, read this first):** 4 of 4 units (`chat/006`, `atlas/024`, `atlas/021`, `suite/055`), all
landed, none blocked. `atlas/024` was sent back once before merge; `atlas/021` landed a decode bug the reviewer
caught and was fixed forward in `af410ad`. Filed `tasks/doc/095` (owner-only) from the inbox. **No `suite` task is
announced.** **Dispatchable now:** 15 `atlas` tasks and nothing else, so one scope; the spread gate will fire, and
no sweep source changed since 15:26. Bench unchanged (`dut` attached, `dev-bench` not). Owner-only: `tasks/doc/093`,
`094`, `095`. Ledger: nothing overdue (next `dev-bench/040`, 2026-11-01, blocked).
`changelog.d/umbrella-check-17-measured.decided.md` is still the owner's and unconsumed. Nothing deployed.

## 2026-10-29 16:11 — atlas/021 write-one-to-clear does not guard a read; undefined reset bits claim no reset

**Decided:** nothing suite-wide. `live.reads_clear` (true for `rclr`/"clear" only) now drives both read-to-clear
guards, so `woclr`/`wclr` registers are read and decoded, whole-peripheral reads included. `mcu svd`: no
`resetValue` anywhere gives `reset: null` (was an invented 0); a register whose `resetMask` is not all ones gets
`reset: null` and its fields keep a reset only when every bit is in the mask. `mcu vote` judges "reset differs"
only on defined bits (fields' resets composed when the register's is null). Full-mask records pinned byte-identical
by a golden file generated from the pre-change code. `DESIGN.md` "Live" gains "Undefined reset bits". **The reviewer
caught a real bug after the merge, and I fixed it forward rather than reverting:** `live.decode` shifted a
field-relative reset by the field's LSB a second time, so any field above bit 0 read at reset was starred with a
made-up reset; it also stopped falling back to the register's reset for a field whose own is null (regparse
records). The worker fixed both in `af410ad` with a test at LSB > 0 and a null-field case; `main` carried the bug
between the two pushes, minutes, no consumer in between. The reviewer's drop is resolved by that commit and deleted.
**Merged:** `agent/atlas/021-w1c-and-reset-mask-read-as-stated` (code `05be6a5` on `fa98820`, ff, then the fix
`af410ad`, ff; doc `b54dbe72`, the worker's `16504b38` cherry-picked). Gate on each merge result: worktree venv
`pytest -q` 421 then 422 passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names
clean, `check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/atlas-decode-field-reset-shifted-twice.md (fixed forward in `af410ad`, drop deleted).
**Hardware debts:** none. Records already built from SVDs keep their invented `0` resets until `mcu svd` re-runs.
**Budget:** PROCEED, weekly 25.1% at dispatch, wave 6.
**Least sure about:** no reviewer read `af410ad` itself; I read its six lines and the test, and the reviewer's repro
case is now a test, but `tasks/atlas/006` (still open) rewrites `_ext_effects` beside this guard and should be
gated with the decode in mind.

## 2026-10-29 16:06 — atlas/024 a non-object record line is written back as it was

**Decided:** nothing suite-wide. `records.load_records` wraps a JSONL line that parses but is not an object in
`RawLine` (an empty dict carrying the line's original text and number); `save_records` writes that text back
verbatim; `run_check` reports it as `V: <file>:<line>: line is not a JSON object (kept as written)` and gives it no
prov. New `common.read_jsonl_lines`; `read_jsonl` unchanged for callers. **I sent it back once before merging:** the
first version re-serialised the value, so `[1, 2,   3]` came back `[1, 2, 3]` while the task said byte for byte;
the worker kept the text and the test now asserts the exact input after a direct save and after `run_check`.
**Merged:** `agent/atlas/024-save-records-keeps-a-non-object-line-as-written` (code `fa98820` on `5fd3caa`, ff, three
commits; doc `72a7dcaf`, the worker's `da3e3dd9` cherry-picked). Gate on the merge result: worktree venv `pytest -q`
415 passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names clean,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 25.1% at this unit, wave 6.
**Least sure about:** the code branch carries a commit with a failing test (`c65cb61`, fixed by `ba07dcd`), so a
bisect over `embarch-atlas` can land on a red commit; I did not squash it.

## 2026-10-29 16:00 — chat/006 /embarch-claude-md cites agent-guide §1.1

**Decided:** nothing. `plugin/commands/embarch-claude-md.md` now cites `suite/agent-guide.md` §1.1 (was
user-guide §7.1, a forwarding line since `suite/030`); its block equals the guide's text, markers aside. I checked
the guide's block sits under §1.1 myself. **Leg context (next leg, read this first):** this leg started 15:49 at
`0e6d6b06`, clean recovery (no claims, no unit worktrees), `main` green at start. Inbox: one owner drop filed as
`tasks/doc/095` (`7674b1e3`, `Owner: required`: `fold-commit.py`'s `ALLOWED` refuses `bootload-proposal.md`),
announced. Spread sweep skipped: no source changed since the 15:26 "nothing filed" line. Bench: `dut` attached,
`dev-bench` not, so `api/059`, `dev-bench/035`, `038` stay open. Ledger: nothing overdue. Dispatched `atlas/024`
and `chat/006` at 15:52; `suite/055` (window closed 14:59, thread re-read 15:51, no reply) planned as the last unit.
**Merged:** `agent/chat/006-embarch-claude-md-cites-the-moved-user-guide-section` (code `e6186d9` on `b9b0e6c`,
ff; doc `107e67f9`, ff). Gate on the merge result: `npm ci`, build, typecheck, test (292, 69 skipped),
`test:webview` all exit 0; client names clean; `check-docs.py` 12/12; ownership `chat` OK on both branches.
Owner's chat checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 24.9% at leg start, wave 6.
**Least sure about:** I took the 69 npm skips as the known `EMBARCH_DESK_BIN` skips (gate.md says so) without
listing them.

## 2026-10-29 15:47 — suite/054 the four root proposals keep only unbuilt design

**Decided:** **a supervisor-run suite task, as this leg's last unit**, after its window (`ts` `1793305739.311079`,
closed 14:58:59; thread re-read 15:26 and 15:47, no reply). Every "built" claim checked against decision text
first. **bootload** 1,908 → 1,347 B: dropped the "deliberately narrow, sim-only until firmware" paragraph and the
DOC-PROTOCOL restatement; built list (smp 1–9, topology 36, core 77–78, api 80–81) and the two left items kept.
**desk-sessions** 1,769 → 1,361 B: dropped the Why, which described the built pick-up half (desk 43–45); the
finishing half is untouched. **host-study** 7,662 → 2,439 B: dropped the Why, the owner's six choices and the
whole Shape; now a built list (study-designer 80; core 95, 98, 104, 105; topology 49; api 97, 99; ui 69;
dev-bench 48, 49) and five left items: pd-bench's own west workspace (`dev-bench/036`), a first host study on a
real bench, a numeric SCPI parse, designer rows, mixed studies. **stream-pipeline** 11,762 → 9,577 B: dropped the
thesis, the five lessons (all recorded: reversals 18, 25; `taps.md`; core streams; api `truncated`) and the line
calling the payload-interpretation deletion unbuilt, **which was false** (dev-bench decision 29 records it already
done); free-text section cut to a pointer at study-designer 37 plus the unbuilt registry field kind. **None fully
absorbed, so none deleted.** `embarch.md` §6's host-study row updated (it still named `ui/100` and the PD bench
firmware as not built). **For the owner (not mine to decide):** the stream-pipeline outbound half has **no task,
no `open.md` line and no roadmap line**, and study-designer decision 58 records itself as having closed that
write direction by a different route (the `.eap` state machine); whether the generic send step is still wanted,
or the file should go, is his call. I said so in the file.
**Merged:** no branches (supervisor's own unit). Gate on the result: `check-docs.py` 12/12, `check-links.py`
green, `check-ownership.py --supervisor` OK on the five paths (19 top-level docs classified). Doc SHAs:
`b21b0fef` (bootload-proposal.md alone: `fold-commit.py`'s `ALLOWED` prefixes refuse a top-level doc not named
`embarch-*`, so it went in its own commit; owner drop filed) and this fold's commit `0e6d6b06` for the rest.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 24.1% at leg start, wave 6.
**Least sure about:** host-study's Shape held details (event names, `study_lock`) the reviewer traced to Core's
`interfaces/` rather than to numbered decisions; I counted a sub-project's interface docs as "recorded".
**Leg close (next leg, read this first):** 4 of 4 units (`ui/102`, `atlas/017`, `umbrella/096`, `suite/054`), all
landed, none blocked. `main` was red at leg start (`suite/037`'s park named retired `suite/053`), fixed `fa05c77c`.
**One `suite` task remains announced with its window closed and no reply: `suite/055`** (triage pre-October
tasks, `ts` `1793305740.224299`); run it as a last unit, re-read the thread first. **Dispatchable now:** 17
`atlas` (incl. new `024`), `chat/006`; only two scopes, so the spread gate will fire. Bench unchanged (`dut`
attached, `dev-bench` not; `api/059`, `dev-bench/035`, `038` open). Owner-only: `tasks/doc/093`, `094`. Ledger:
nothing overdue (next `dev-bench/040`, 2026-11-01, blocked). `changelog.d/umbrella-check-17-measured.decided.md`
is the owner's, unconsumed since 14:01. Nothing deployed.

## 2026-10-29 15:40 — umbrella/096 the install test's ETXTBSY race is retried, not the install

**Decided:** nothing. Test-only fix: `install_binaries_replaces_a_binary_that_is_running` retries its own `spawn`
of the just-copied `sleep` fixture on `ErrorKind::ExecutableFileBusy` (200 tries, 10 ms). Cause, reproduced by the
worker 1 in 80 parallel runs: a sibling test thread forks while the copy's write fd is open, so the exec gets
ETXTBSY; 0 in 150 after. `install_binaries`/`replace_binary` unchanged. The reviewer checked production cannot
hit it (copy to `.{name}.new-{pid}`, rename, never execs a just-written file) and that no assertion pinning
decision 57 was weakened. This retires the one flaky test in the umbrella gate the fleet re-runs every unit.
**Merged:** `agent/umbrella/096-install-replaces-running-binary-test-flakes` (code `d3f1c83` on `50f4022`, ff;
doc `6e788299`, the worker's `a9384c30` cherry-picked). Gate on the merge result: build, test 258 pass, clippy
`-D warnings` clean, client names clean, `check-docs.py` 12/12, ownership `umbrella` OK on both branches. Owner's
umbrella checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 24.1% at leg start, wave 6.
**Least sure about:** 1 in 80 is one observation, so 0 in 150 after is suggestive rather than proof; the diagnosis
is the stronger evidence, and it is a known Linux fork/exec race.

## 2026-10-29 15:39 — atlas/017 doc check reports a malformed record instead of crashing

**Decided:** nothing suite-wide. `run_check` (`check.py`) schema-validates every record first; an invalid one
gets `V:` issues naming id and field, ends `failed`/`llm-unverified`, is kept and saved, and is left out of
`check_registers`, `check_invariants`, `record_checks`, the twin verdict, ref resolution of its own refs and the
verified-values pool. A valid record's ref *to* an invalid id still resolves (reviewer checked `seen` is built
from all records). `DESIGN.md`'s `doc check` row says so. **Filed `tasks/atlas/024`** in this fold from the
worker's own limitation, confirmed by the reviewer: a non-object JSONL line becomes `{}` in memory and
`save_records` persists that over the original line on any save that touches its file.
**Merged:** `agent/atlas/017-doc-check-survives-malformed-records` (code `5fd3caa` on `8a32edb`, ff; doc
`d212f7b1`, the worker's `85133924` cherry-picked). Gate on the merge result: worktree venv `pytest -q` 414
passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names clean,
`check-docs.py` 12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 24.1% at leg start, wave 6.
**Least sure about:** the reviewer read `DESIGN.md` and the code but not `embarch-doc/embarch-atlas/`. Separately,
`changelog.d/umbrella-check-17-measured.decided.md` has sat unconsumed since the owner's `a5062887` (14:01); not
this leg's, so `--only` leaves it, and nobody has folded it.

## 2026-10-29 15:36 — ui/102 the host-clock fallback is already named by an existing test

**Decided:** nothing. Closed with no code change: `a_splice_that_is_not_a_leading_prefix_still_costs_the_dut_clock`
(`src/trace.rs`) asserts `unit == "ms"`, `axis_clock == "host-arrival"` and `dut_clock_refused` on both its
refused-splice arms, which is outpost decision 17's "says so"; no `open.md` line owed. I checked the assertions on
`main` myself before landing. **Leg context (next leg, read this first):** this leg started 15:24 at `abb009ab`,
clean recovery (no claims, no unit worktrees). **`main` was red at start**: `suite/053`'s fold left
`suite/037`'s `Unparks when:` naming `suite/053`, a retired task; reworded in `fa05c77c`, 12/12 since. Inbox: one
drop filed as `umbrella/096` (`f93950b2`), announced. Bench: `dut` attached, `dev-bench` not, so `api/059`,
`dev-bench/035`, `038` stay open. Ledger: nothing overdue. Spread sweep: nothing filed (2026-10-29 15:26) — the
only source changed since 15:05 is `embarch-umbrella/open.md`, `umbrella/095`'s compaction, all owner-run debts.
Dispatched three at 15:28: `atlas/017`, `ui/102`, `umbrella/096`; `suite/054` planned as the last unit (window
closed 14:58:59, thread re-read 15:26, no reply).
**Merged:** `agent/ui/102-a-dut-counter-restart-test-asserts-the-view-names-the-host-clock-it-fell-back-to` (code
none, `embarch-ui` main unchanged at `f6da709`; doc `5962b4b7`, the worker's `0fe1d448` cherry-picked). Gate:
`check-docs.py` 12/12, ownership `ui` OK on both branches; no cargo run, nothing compiled changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 24.1% at leg start, wave 6.
**Least sure about:** the reviewer notes both arms of that test are *forward* jumps; no `trace.rs` test refuses
the DUT clock on a literally backwards step longer than the capture. `dut_clock_health` uses `abs_diff`, so the
path is sign-independent, which is why I did not file a test for it.

## 2026-10-29 15:23 — suite/053 the 87 done task files are retired

**Decided:** **a supervisor-run suite task, as this leg's last unit**, after its window (`ts`
`1793305738.327939`, closed 14:58:58; thread re-read 15:05 and 15:23, no reply). `git rm` of every task file
reading `done` at token zero: 87 (core 21, api 18, topology 12, ui 12, study-designer 9, umbrella 6, dev-bench 4,
suite 4, outpost 1); `queue-status.py` now lists no `done` rows. **Orphan check**: scripted scan of all 87 for
unticked boxes and "left open / deliberately / follow-up / debt" lines, then a read of each hit. Three had
unticked boxes, all already homed: `core/028` box 2 is `embarch-core/open.md`'s Espressif port-selection bullet;
`suite/022`'s size box was paid by `suite/030`; `ui/065`'s two struck boxes are `embarch-ui` decision 27 and its
`open.md`. The prose follow-ups (`api/036`'s schema-skew citation drop, `topology/056`'s deferred behaviour, now
`topology/058`, `ui/024`'s three OVER decisions, since under cap) are resolved. **Nothing re-homed.** One inbound
link repointed: `suite/decisions/placement.md` now names `embarch-ui` decision 27 where it linked `ui/065`.
`suite/037`'s `Unparks when:` named the retired `core/015` as the Windows-build debt and turned
`check-task-state.py` red; it now names `embarch-core/open.md`'s standing owner-run debt. Backtick mentions of
retired numbers elsewhere (open.md, history, this log) are left: numbers are permanent and `git log` finds them.
**Merged:** no branches (supervisor's own unit). Gate on the result: `check-docs.py` 12/12, `check-links.py`
green, `check-task-numbers.py` green (58 live numbers, none reissued). Doc SHA is this fold's commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.4% at leg start, wave 6.
**Least sure about:** my orphan scan was keyword-driven; the reviewer, spawned on the uncommitted diff before
this fold, read all 87 and found nothing unhomed, but about 40 non-task files still cite retired numbers as
prose provenance, which no gate reads.
**Leg close (next leg, read this first):** 4 of 4 units (`umbrella/095`, `chat/005`, `atlas/009`, `suite/053`),
all landed, none blocked. **Two `suite` tasks remain announced with windows closed and no reply**: `suite/054`
(shed built proposal pieces, `ts` `1793305739.311079`) and `055` (triage pre-October tasks, `ts`
`1793305740.224299`); one per leg as the last unit, re-read each thread first. **Dispatchable now:** 17 `atlas`
tasks, `ui/102`, `chat/006` (filed this leg). Bench: `dut` attached, `dev-bench` not, so `api/059`,
`dev-bench/035`, `038` stay open. Owner-only: `tasks/doc/093`, `094`. Ledger: nothing overdue (next
`dev-bench/040`, 2026-11-01, blocked). Nothing deployed.

## 2026-10-29 15:20 — atlas/009 a live call that can change the board carries no read-only hint

**Decided:** nothing suite-wide. Atlas MCP: `shell` runs only commands matching `atlas.toml`'s `[live] read_only`
globs (default `device list`, `kernel thread stacks`, `kernel uptime`, `i2c read *`, `i2c read_byte *`; `i2c
scan` deliberately out; a set list replaces the default) and refuses the rest naming `shell_run`; new `shell_run`
and `reg_read_clear` declare `read_only_hint=False`; `reg_read` refuses `allow_clear=true` naming
`reg_read_clear`. CLI unchanged, one verb each. **The worker added one rule unasked**: a command containing `; | &`,
a backtick, `$(` or a newline never matches the list, so a chained write cannot ride in behind a listed read; the
reviewer judged it stricter in the safe direction and stated in `DESIGN.md` "The live shell". The 2026-10-06
trade-off sentence in "MCP server" is replaced, not contradicted; `reg_read_clear` keeps `atlas/008`'s chip check.
**My slip, the unit before this one:** `chat/005`'s fold (`9d278461`) landed with `check-task-state.py` red,
because I piped `check-docs.py` through `tail` inside an `&&` chain; `chat/006`'s title named a path a `chat`
worker may not write. Fixed two minutes later in `333c3ca7`. Every gate since runs unpiped with its exit printed.
**Merged:** `agent/atlas/009-live-writes-carry-no-read-only-hint` (code `8a32edb` on `63055f7`, ff; doc `b526d00c`,
the worker's `904f5603` rebased onto the leg's main, ff). Gate on the merge result: worktree venv `pytest -q` 412
passed, 2 skipped (real west workspace, built atlas; `test_public_guard` ran), client names clean, `check-docs.py`
12/12, ownership `atlas` OK on both branches. Owner's atlas checkout fast-forwarded; `embarch-atlas-wt` untouched.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run live (tests use a fake `embarch-api`). Owner-side: the installed `atlas-use` skill
in `~/.claude/skills/` and any running atlas MCP server are the old ones until `./install.py` runs and the
server restarts; how a host behaves in plan mode with the new hints is unobserved.
**Budget:** PROCEED, weekly 23.4% at leg start, wave 6.
**Least sure about:** the default read list is short, so a session that used to run `shell` freely will now meet
refusals for ordinary reads (`gpio get`, `sensor get`) until a project lists them; that is the intended cost, and
nobody has felt it yet.

## 2026-10-29 15:17 — chat/005 /embarch-permissions carries the agent guide's 54-tool split

**Decided:** nothing suite-wide. `plugin/commands/embarch-permissions.md` now carries `suite/agent-guide.md`
§1.1's allow (23) and ask (31) lists, re-dated 2026-10-29, cites §1.1, and adds one line that `answer_prompt` and
`instrument_exchange` ask. Worker and reviewer each checked the 54 against `embarch-api/src/tools.rs` on `main` as
sets: exact, so the guide needed no drop. **Filed `tasks/chat/006`** in this fold from the reviewer's residue:
`/embarch-claude-md` still cites `suite/user-guide.md` §7.1 (now a forwarding line). The worker left the task's
`State:` as the claim line; set to `done` here.
**Merged:** `agent/chat/005-embarch-permissions-carries-the-agent-guides-54-tool-split` (code `b9b0e6c` on
`origin/main`, ff; doc `fd695c22`, the worker's `8562f5e8` rebased in its worktree onto the leg's main, ff). Gate
on the merge result: `npm ci`, build, typecheck, test, `test:webview` all exit 0; client names clean;
`check-docs.py` 12/12; ownership `chat` OK on both branches. Owner's chat checkout fast-forwarded. The rebased
doc branch was not force-pushed (classifier refused it); the remote branch holds the pre-rebase `8562f5e8`, which
`fold-commit.py` prunes by patch-id.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.4% at leg start, wave 6.
**Least sure about:** whether `/embarch-claude-md`'s block is §1 or §1.1 of the agent guide; `chat/006` says to
check. A grep of eight repos found no other live `user-guide §7` citation (only task text and an August note).

## 2026-10-29 15:13 — umbrella/095 check 17's fix lines name Core 106's in-place install

**Decided:** nothing suite-wide. `doctor.rs`: both check 17 fix lines keep `embarch-core install --bind 0.0.0.0`
and say it rewrites a registered service in place on Core decision 106 or newer, `uninstall` first on an older
Core; `BindEvidence` gains `service_stopped: Option<bool>` (read via `locate::windows_core_service_state()`, WSL2
guest only), so `bound-narrow` says "stopped and bound narrow", keeps "not a stopped service" when running, and
says it did not read the state when it could not. `bind-too-narrow`'s NAT unreachability is in its doc comment.
Decision 22 amended in place (`bind.md` 11,045 B, under its 11,059 B reserve line). **`umbrella/094` paid and
closed**: the worker compacted `open.md` to 3,740 B. **The reviewer found the squeeze dropped two live claims**
(the decision 58 desk-step "it restarts the service" caution, and "whether `embarch setup` gets past an existing
registration" as unmeasured, which `bind.md` now asserts from reading `setup.rs`); **I restored both in this
fold**, `open.md` 3,882 B, still under 3,919 B. Not restored, for size: check 5's "no-probe-found cannot occur"
clause (derivable, reviewer rated it lower weight). Drop deleted as resolved.
**Leg context (next leg, read this first):** this leg started 15:03 at `a7e87bca`, clean recovery (no claims, no
unit worktrees; owner's `embarch-atlas-wt` left alone). Inbox: the previous leg's two owner drops filed as
`tasks/doc/093` and `094` (both `Owner: required`), announced. Bench: `dut` attached, `dev-bench` not, so
`api/059`, `dev-bench/035`, `038` stay open. Ledger: nothing overdue. Spread sweep: nothing filed (2026-10-29
15:05) — the only source changed since 14:30 is `embarch-core/open.md` (`core/124`), whose new bullet is an
owner-run Windows debt. Dispatched three at 15:07: `umbrella/095`, `chat/005`, `atlas/009`; `suite/053` planned
as this leg's last unit (window closed 14:58:58, thread re-read 15:05, no reply).
**Merged:** `agent/umbrella/095-check-17s-fix-lines-name-an-install-that-refuses-a-registered-service` (code
`50f4022` on `4c786fa`, ff; doc `5e93f5b3` on `2c5ed35c`, ff). Gate on the merge result: build, test 258 pass,
clippy `-D warnings` clean, client names clean, `check-docs.py` 12/12, ownership `umbrella` OK on both branches.
Owner's umbrella checkout fast-forwarded. The worker saw `install::tests::install_binaries_replaces_a_binary_that_is_running`
fail once in a parallel run and pass twice after; my run passed.
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/umbrella-open-md-compaction-dropped-desk-restart-warning.md
**Hardware debts:** owner-run, in `embarch-umbrella/open.md` (it reinstalls the service): with Core 106 deployed,
register `--bind 127.0.0.1`, stop it, `doctor` in the guest says "stopped and bound narrow", then the printed
`install --bind 0.0.0.0` widens it; `bind-too-narrow` from a mirrored guest and `setup` over a registration
unmeasured. Core 106 itself still needs the owner's native Windows build.
**Budget:** PROCEED, weekly 23.4% at leg start, wave 6.
**Least sure about:** the `service_stopped` read runs only from a WSL2 guest, so a native-Windows `doctor` always
takes the "did not read the state" arm; nobody has seen that wording on a real narrow Core.

## 2026-10-29 15:01 — suite/030 the user guide's Claude Code section becomes suite/agent-guide.md

**Decided:** **a supervisor-approved suite-level doc change, run by me as this leg's last unit** after a window
with no reply (`ts` `1793305727.873799`, 14:28:47 to 14:58:47; polled 14:58:50). The overdue size-ledger debt
(due 2026-09-18) is **paid by the split fork** `tasks/doc/045` opened: `suite/user-guide.md` §7/§7.1 moved
verbatim into a new `suite/agent-guide.md` (3,336 B), headings renumbered §1/§1.1; user-guide keeps a two-line §7
pointer so §8–§11 keep their numbers. `user-guide.md` 24,945 B to 22,947 B, out of reserve. **I classified the 28
tools §7.1 had never listed** (it said "all 29" and named 26; `tools.rs` has 54): allow adds `capture_read`,
`capture_start`, `capture_stop`, `lease_show`, `ledger_pending`, `ledger_show`, `list_instruments`,
`show_bootload_ports`, `study_stream_load`; everything else new asks, including `mem_read`/`core_state` (on
`validate`'s precedent: they attach to the probe), `answer_prompt`, `instrument_exchange`, all lease writes and
`ledger_add`. Lists checked as sets against `tools.rs` on `0f1f0d4`: 23 + 31 = 54, no duplicates. Three sentences
added below the lists (those three groups, and "a tool on neither list is newer than this page: ask").
Repointed `embarch-chat/decisions/library.md` and user-guide §6's "the MCP tools in §7"; indexed in `embarch.md`
§6. **Filed** `tasks/chat/005`: `/embarch-permissions` still carries the 2026-10-23 split (36 tools) and cites
user-guide §7.1, which now lands on the forwarding line. **Owner drops left in `inbox/`** (both `Owner:
required`): `doc-doc-protocol-guides-list-names-two-of-three.md` (DOC-PROTOCOL §3's "today" list of guides) and
`doc-outpost-worktree-needs-study-designer-link.md` (leg.md's sibling table, `outpost/018`'s finding).
**The compaction question** (can `spec.md` alone answer what someone needs to work on this today? here, can the
guide alone get a newcomer working?): yes; nothing was cut, and the agent half now has a page with room to grow.
**Merged:** no branches (supervisor's own unit). Gate on the result: `check-docs.py` 12/12, `check-doc-size.py`
reports the item PAID. Doc SHA is this fold's commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 22.2% at leg start, wave 6.
**Least sure about:** putting `capture_start` on allow: it reads a console like `serial_log` (core decision 92,
no hardware lock, no write path), but it starts something that runs on after the call returns.
**Leg close (next leg, read this first):** 4 of 4 units (`core/124`, `outpost/018`, `atlas/008`, `suite/030`), all
landed, none blocked. **Three `suite` tasks are announced and their windows closed with no reply** (14:58:58 to
14:59:00): `suite/053` (retire done task files), `054` (shed built proposal pieces), `055` (triage pre-October
tasks); each is a supervisor's own unit, one per leg, run as the last unit. Re-read each thread first.
**Dispatchable now:** `umbrella/095` (unblocked by `core/124`'s decision 106), 18 `atlas` tasks, `ui/102`,
`chat/005`. Bench: `dut` attached, `dev-bench` not, so `api/059`, `dev-bench/035`, `038` stay open. Overdue
ledger: none (next due `dev-bench/040`, 2026-11-01, blocked). Nothing deployed: `core/124` needs the owner's
native Windows build before a reinstall can use it.

## 2026-10-29 14:44 — atlas/008 a live read from another chip is refused, not decoded

**Decided:** nothing suite-wide; **the fleet's first `atlas` unit** (gate.md's Python bullet, worktree venv,
`.atlas-local` linked, `test_public_guard` ran). `live.py`: `reg_read` refuses when Core's `read['chip']` is not
the atlas MCU and names both chips and the role; `image_check` raises `ChipMismatch` instead of "another build";
`live_stacks` says "the console of role X and its probe are different boards". The atlas MCU is the SVD
document's `device` only (not `MAP.md`'s MCU line); the match ignores case and punctuation and **accepts one name
being a prefix of the other**; **an atlas with no SVD device compares nothing**. Both stated in `DESIGN.md`
"Live"'s new "Wrong chip" bullet; the reviewer judged them stated weaknesses, not contradictions. Test chip names
are invented because `test_public_guard` rejected real part names. `check_public.py`, which my dispatch note
named, does not exist in the repo. The worker left the task's `State:` as the claim line; set to `done` at this fold.
**Merged:** `agent/atlas/008-live-refuses-another-chip` (code `63055f7` on `0cf93ce`, ff; doc `503c1549`
cherry-picked from the worker's `fed00c4a` onto `a90b34dd`). Gate on the merge result: `pytest -q` 409 passed, 2
skipped (real west workspace, built atlas; both expected), client names clean, `check-docs.py` 12/12, ownership
`atlas` OK on both branches. Owner's atlas checkout fast-forwarded; his `embarch-atlas-wt` untouched.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one `reg_read` through a live Core against a board whose probe is another chip, seeing the
refusal (owner-attended; the atlas tests use a fake `mem-read`).
**Budget:** PROCEED, weekly 22.2% at leg start, wave 6.
**Least sure about:** the prefix match: an SVD `device` written as a family (say a 7-character stem) would accept
every part in it, and the silent pass on a missing device means the refusal protects only atlases that name one.

## 2026-10-29 14:42 — outpost/018 a 13 µs backwards DUT-clock step is pinned as tolerated

**Decided:** nothing suite-wide. Test only, no decoder change: `tests/decoder_unit.py` gains
`test_a_13_us_inversion_between_ordinary_records_is_tolerated_and_reported` (the recorded 13 µs step, 13 cycles
at 1 MHz), mutation-checked against the `> (1 << 31)` wrap threshold. **The task's premise was half wrong**, and
the reviewer confirmed it against decision 17: the restart arm (a step longer than the capture, tested against
`rx_utc_ms`, refuse, fall back, say so) is a *host's* job and lives in `embarch-ui/src/trace.rs` and Core's
`outpost_load.rs`; `decode_outpost.py` only unwraps. The task's unticked box ("the fallback names the clock") is
re-homed in this fold as **`tasks/ui/102`** (Hardware: none). **Table gap for the owner:** leg.md's sibling table
links only `embarch-core` and `embarch-ui` beside an `embarch-outpost` worktree, but `tests/vocab_check.py` also
reads `../embarch-study-designer/src/outpost.rs` and **skips** without it; I made the link and re-ran it green.
**Merged:** `agent/outpost/018-backwards-dut-clock-decoder-tests` (code `ac3b96f` on `514d2c0`, ff; doc `202377aa`
cherry-picked from the worker's `b8099ee5` onto `8b81f423`). Gate on the merge result: `decoder_unit.py` 36 OK,
`cross_decoder.py` 831 rows agree, `vocab_check.py` PASS (after the link), client names clean, `check-docs.py`
12/12, ownership `outpost` OK on both branches. Owner's outpost checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 22.2% at leg start, wave 6.
**Least sure about:** whether `ui/102` is real work: the four `trace.rs` tests may already assert the host-clock
flag, and I filed it without reading them.

## 2026-10-29 14:41 — core/124 install over a registered Windows service rewrites in place

**Decided:** nothing suite-wide. The worker's core decision 106 (`decisions/platform.md`): on Windows, `install`
over a registered service **rewrites it in place** (stop, rewrite `ImagePath` as `"<exe>" run --bind <bind>`,
merge `Environment`, apply failure actions, start) rather than refusing with "uninstall first", because
uninstall-then-install is the route that dropped `EMBARCH_SIGNAL_BAUD`. A reinstall keeps every existing
`Environment` entry (prints their names, never values) and replaces `EMBARCH_TOKEN` only when one is set; fresh
installs and rewrites both run `sc failure reset= 3600` with five `restart/5000` actions. Linux and macOS
unchanged. `embarch-core/open.md` compacted 4,804 B to 3,918 B (out of reserve) to pay for the debt line, and the
worker struck it off `core/112`'s `Compacts:` line; 112 stays blocked for `probes.md` and `spec.md`.
**`tasks/umbrella/095` is now dispatchable**: its fix lines can say `install --bind` rewrites a registration.
**Leg context (next leg, read this first):** this leg started 14:24 at `64976739`, clean recovery (no claims, no
leg tree; the owner's own `embarch-atlas-wt` worktree on `fix/field-findings`, dirty since 2026-10-08, left alone).
**The owner answered the 2026-10-28 dream "do 1"** (settle `tasks/doc/089`); he had already landed it himself
(`2e28b74d`, gate.md's Python bullet), so `atlas` is dispatchable and this leg runs the fleet's first atlas unit.
Inbox: three owner drops filed as `tasks/suite/053` (retire done task files), `054` (shed built pieces from the
root proposals), `055` (triage pre-October tasks), each announced (`ts` `1793305738.327939`, `1793305739.311079`,
`1793305740.224299`, windows close 14:58-14:59). **`suite/030` is overdue on the size ledger and now unparked**
(`tasks/doc/045`): announced `ts` `1793305727.873799`, window closes 14:58:47, planned as this leg's last unit.
Bench: `dut` attached (probe `000852006107`), `dev-bench` not attached, so `api/059`, `dev-bench/035`, `038`
stay open. Spread sweep: nothing filed (2026-10-29 14:30) — the only source changed since the 2026-10-28 22:13
full sweep is `embarch-umbrella/open.md`, whose new bullet is already `umbrella/095` + `core/124`. Dispatched
three at once: `core/124`, `outpost/018`, `atlas/008`; `umbrella/095` held for this unit. 2026-10-28 day-folded
(32 units, by the log-folder), 2026-10-25 rolled; `check-client-names.py --suite --history` all 14 repos clean.
**Merged:** `agent/core/124-install-over-a-registered-service` (code `80dfa0d` on `85846c4`, doc `baec9822` on
`e0a59709`; both ff). Gate on the merge result: core build, clippy `-D warnings`, test 385 + 2 pass, client names
clean, `check-docs.py` 12/12, ownership `core` OK on both branches. **`cargo check --target
x86_64-pc-windows-msvc` could not run** (`hidapi`'s C build needs MSVC headers), so I read the `cfg(windows)`
hunks by hand for imports and bindings; nothing found. Owner's core checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, in `embarch-core/open.md`: (1) native Windows build, since the `cfg(windows)`
registry and `sc failure` code has never been compiled; (2) a live `install --bind` over the registered service,
checking `EMBARCH_SIGNAL_BAUD` survives and `sc qfailure` shows five restarts.
**Budget:** PROCEED, weekly 22.2% at leg start, wave 6.
**Least sure about:** the Windows half compiling at all: a Linux gate, a hand read and a reviewer are all it has
had, and `main` now carries it.

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
## 2026-10-26 — 85 units

*Folded by the 2026-10-28 leg's log-folder: the per-unit Decided / Gate / Leg-close / Budget / Least-sure-about narrative went (git holds it); every SHA, every reviewer line and every owed hardware debt below is kept.*

**Carry forward (the next leg cannot recover these):**
- **Owner `fleet stop` at 09:19** (`ts` `1793027967.518769`, relayed by the listener, acknowledged in thread). The last leg ran `topology/067`, `api/148`, `core/101`, `ui/086` to completion (all workers finished before the stop, all landed and folded, nothing dispatched after it); **all four reviewers were skipped, so those four units have had no intent read.** The pump latch was already gone. No units ran on 2026-10-27.
- **`suite/046`-`049` still open and unannounced** (`suite/052` was announced 08:09, `ts` `1793023741.728799`, no reply by 08:39, and landed as a supervisor-approved cross-repo shape change, protocol §8).
- **Overdue size ledger unchanged and judged unpayable:** `suite/030` blocked on `DOC-PROTOCOL.md`, `doc/031` owner's, `study-designer/026` every bullet live.
- **`atlas` tasks still skipped per `tasks/doc/089`** (19 queued at last count). **Bench unattached:** `validate dev-bench` not attached, not a mismatch, so `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`; `fleet-hardware.py --refresh` crashes (`tasks/doc/041`) and its buffer was 48 days stale.
- **Next candidates:** `core/116` (unblocked by `core/101`; read its 08:09 note), `core/118` (small), `topology/066`, `study-designer/078`, `ui/095`. Filed by the last leg: `core/118`, `core/119` (`Hardware: required`), `ui/095`. `queue-status.py --count` 35, `inbox/` empty at close.
- **Nothing deployed:** the live Core, the MCP binary and the UI binary all predate `core/096`-`117`, `api/124`-`148` and the new UI; a new UI against an old Core sends `interface`, which the old Core ignores. `core/102`'s `HostStudy` accepts `HOST_TYPE_SCHEMA_VERSION` 20 (the landing bumped 19 to 20, schema-bump window announced `ts` `1793017849.375049`, closed 07:01 with no reply).
- **Failure likely to recur:** a shared-crate landing must build every feature configuration its `Cargo.toml` names; the 06:59 `topology/062` landing broke the `software,wire` build for five minutes (`tasks/doc/091`). Run `check-docs.py` unpiped before every fold: a `| tail` masked its exit and let a fold commit over a red gate once (caught and amended, `7da4011c`).
- `embarch-core/open.md` was 5,070 / 5,120 B at `core/099`, parked under `core/112` (`In flux: yes`); the next core unit that adds an open question must compact it in the same unit.
- `--refill-owed` fires on scope spread only (api, atlas, core, suite, ui, `tasks/doc/081`'s shape).

**Merged / Blocked (nothing was blocked; every unit merged; SHAs in each line are code, doc, rebase bases and gate pins; newest first):**

- 09:27 `ui/086` the Time chart says when a strip or mark lane is capped — `98d9263` `ecd00154` `68fc73ad` `1793027967`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:26 `core/101` a host study's console taps hold their ports for the whole study — `0ba23bf` `68fc73ad` `1a16bae7`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:25 `api/148` core_state tool and CLI — `b0d05a1` `1a16bae7` `1de05c25`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:25 `topology/067` the identity gate reports its halts — `b4d1b0a` `1de05c25`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 08:58 `suite/052` a direct signal route declares which serial interface carries it — `1793023741` `5f87333` `62d776e` `c495360` `9e8d8bd` `74c900e` `c126ae4` `02d38b9` `5d1a1fc` `95b7f7c1`
**Reviewer:** no findings.
- 08:36 `ui/093` the desk-Slack browser check waits for its toggle and names a setup failure — `c126ae4` `15e3c63` `954a24c` `417378f7` `4072f789`
**Reviewer:** no findings.
- 08:35 `core/103` Core reads where a running or hung core is without resetting it — `5d1a1fc` `71c65b0` `20cb0159` `66334a05`
**Reviewer:** no findings.
- 08:29 `api/141` the CLI says "no records found" for a zero-record report — `001057729826` `1793023741` `44733b77` `9e8d8bd` `b7701c9` `9ad7248a` `6d662297`
**Reviewer:** no findings.
- 08:03 `ui/089` embarch-ui/spec.md is out of reserve: the tab-navigation paragraph lives in spec/tabs.md — `2ffe19ec` `35b86fb5` `86247e1e`
**Reviewer:** no findings.
- 08:02 `core/117` an ambiguous declared serial reaches every Core caller with its candidate ports — `2ffe19ec` `71c65b0` `06f2d9c` `1cf9c8b3` `24a2a13d`
**Reviewer:** no findings.
- 07:57 `api/136` the MCP startup check is retracted, and a stream 404 keeps Core's own words — `b7701c9` `72f041f` `a55824c3` `49a7aefe`
**Reviewer:** no findings.
- 07:51 `api/133` one build per lock key holds across processes, not only inside one — `72f041f` `001057729826` `401c3c4` `ffcba366` `eb6aa75a`
**Reviewer:** no findings.
- 07:37 `api/147` bench_exchange orders lines by Core's receive times when Core sends them — `401c3c4` `903c76c` `d6af5526` `4485f2f1` `302784c`
**Reviewer:** no findings.
- 07:34 `core/102` Core runs host studies: send-and-read steps against a console, with teardown on every exit — `302784c` `1793017849` `903c76c` `954a24c` `06f2d9c` `731e875` `40b05d86` `44dfab48` `7828256`
**Reviewer:** no findings.
- 07:22 `ui/094` every browser drive script takes its ports from one convention, and the old names are refused — `820ca9d6` `954a24c` `81bde80` `1b9f0b0f` `903c76c`
**Reviewer:** no findings.
- 07:19 `api/146` an old Core's /status reads as unknown images, not as nothing flashed — `001057729826` `903c76c` `3625584` `8aa20c22` `7547221d`
**Reviewer:** no findings.
- 07:02 `ui/085` a Data card's table is re-fetched when it loads, so the post-run re-read is the full file — `1793017849` `81bde80` `35fa9da` `72b042d4` `95f74625` `3625584` `62d776e`
**Reviewer:** no findings.
- 07:01 `core/115` each line of a signal capture carries the time its first byte arrived — `731e875` `de77295` `97e23132` `26a337f8` `62d776e` `7828256`
**Reviewer:** no findings.
- 07:00 `api/145` sessions can take the bench lease and every Core call carries its token — `3625584` `6d615e7` `71db5e4d` `994f5e5e` `62d776e` `5063c0b`
**Reviewer:** 1 finding, filed in the fold as `tasks/api/146` (fix forward): `last_images` must be `Option<Vec<_>>` per client-crate decision 58, so an old Core reads as unknown, not as nothing flashed.
- 06:59 `topology/062` a direct route's declared serial on several ports is refused by name, not guessed — `1793017849` `9e465cb` `62d776e` `b771dd0` `8b41ab47` `a626c70b`
**Reviewer:** no findings; refusing serial-less same-VID ports does not contradict decision 20 (its text still says "kept, not replaced", left as is).
- 06:23 `ui/081` a Slack reply from the Desk goes to the message it was drafted for — `35fa9da` `69edcdd` `f7416058` `7bffd9fe` `6d615e7` `7828256`
**Reviewer:** no findings.
- 06:17 `api/131` one bench_exchange call drives console steps and returns every listened console as one filtered timeline — `6d615e7` `aa303c2` `31c5d788` `3e1284b9` `7828256` `b771dd0` `845f3ea`
**Reviewer:** no findings.
- 06:14 `core/099` a session can lease the bench, and other callers are refused by name while it holds it — `5063c0b` `96cc87a` `2a76ad9c` `12b9e498` `7828256` `b771dd0`
**Reviewer:** no findings.
- 06:12 `study-designer/071` a host study can repeat a block of steps and count matching console lines per pass — `001057729826` `7828256` `4da23d3` `e1f65391` `cd1b8848`
**Reviewer:** no findings.
- 05:54 `topology/064` link-declares.md is out of reserve: decision 36 has its own file — `34a4a478` `3815e56c` `004f70e4`
**Reviewer:** no findings.
- 05:52 `ui/092` drive_topology.py's sidebar checks describe the Desk shell — `69edcdd` `fd7f1b6` `f2243590` `6fb4dbe9` `aa303c2` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:49 `core/114` the capture routes are under the auth sweep and a split `.route(` fails the scan — `96cc87a` `845f3ea` `b61e5610` `597c4adb` `4da23d3` `b771dd0`
**Reviewer:** no findings; decision 42's prose still says "All 22 `.route(` registrations", left because `DOCUMENTED_ROUTE_COUNT` is the pin.
- 05:48 `api/143` capture_start, capture_read and capture_stop drive Core's background signal capture — `aa303c2` `001057729826` `c4a3434` `d70ac3dc` `49bb1cb5` `4da23d3` `b771dd0` `845f3ea`
**Reviewer:** no findings; noted `SignalCaptureResponse` defaults bare scalars where decision 58 prefers `Option<T>`, left (an older Core answers 404).
- 05:33 `ui/087` the validate summary never says passed over a warning or an empty bench, and enrol refuses an unanswerable chip itself — `fd7f1b6` `aefdc8b` `b4cc368b` `250305e0` `c4a3434` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:30 `core/100` a declared signal can be captured in the background while other hardware calls run — `845f3ea` `ffba91a` `c43051a8` `8ed023a3` `4da23d3` `b771dd0`
**Reviewer:** 1 finding (`inbox/core-capture-routes-outside-auth-sweep.md`): the capture routes' multi-line `.route(` escapes decision 42's scan, so no `AUTH_CASES` rows and `DOCUMENTED_ROUTE_COUNT` stays 32; filed as `tasks/core/114`, fix forward, no revert.
- 05:27 `api/135` serial_log tells its caller when Core cut the capture short — `c4a3434` `c49e9b2` `9fd8193c` `f1b9aef0` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:26 `study-designer/074` the GATT extractor ignores definitions inside C comments — `001057729826` `4da23d3` `f25533a` `096bd289` `37567d18`
**Reviewer:** no findings.
- 05:09 `ui/080` a console's unfinished line is capped instead of growing for the whole run — `aefdc8b` `f8b2f7e` `b6321925` `d1b36664` `f25533a` `b771dd0` `c49e9b2`
**Reviewer:** no findings.
- 05:07 `core/105` GET /load/spans is retired: nothing ever called it — `91b7fb1d` `ffba91a` `74c5e4d` `00939429` `f25533a` `b771dd0`
**Reviewer:** no findings.
- 05:05 `topology/061` the topology CLI's Core guard probes a named port, and the CLI enrols bench boards the way Core does — `b771dd0` `62c188d` `c66e648c` `ab2fd2a3`
**Reviewer:** no findings.
- 05:03 `study-designer/073` the .eap parser refuses three authoring errors it used to accept — `001057729826` `f25533a` `0fabb6b` `a8c18d70` `41e0223e`
**Reviewer:** no findings.
- 04:48 `ui/079` the build log says which board it built and why, and the stored log keeps it — `f8b2f7e` `26ed2ec` `17a9dc46` `7a3d59e4` `c49e9b2` `0fabb6b` `62c188d`
**Reviewer:** no findings.
- 04:47 `core/113` POST /study refuses a Notify or Indicate step with a wait budget of 0 — `74c5e4d` `359b8c7` `f4062527` `f769b137` `0fabb6b` `62c188d` `fe68a41`
**Reviewer:** no findings.
- 04:45 `api/124` signal_exchange can match a prompt on a console with echo off — `1ebf8c94` `c49e9b2` `9e4ca14` `fa571863` `0fabb6b` `62c188d`
**Reviewer:** no findings.
- 04:43 `study-designer/077` the alloc test cell compiles again — `001057729826` `0fabb6b` `5ea5ac9` `ceeb34d0` `39ec7a4a` `ba3ad46`
**Reviewer:** no findings.
- 04:28 `outpost/026` the reference decoder refuses a record layout it does not speak — `514d2c0` `2968f0c` `96d2f920` `b61a8ac0`
**Reviewer:** no findings.
- 04:27 `ui/091` the enrol dialog says when an enrol moved a role — `d414560` `26ed2ec` `ba311f8` `84b1400a` `7d2986f4` `9e4ca14` `5ea5ac9` `62c188d`
**Reviewer:** no findings.
- 04:24 `core/111` Core refuses a probe enrolled on another chip family before any attach — `5ea5ac9` `359b8c7` `cd01043` `42ebff05` `8d9012f6` `62c188d` `fe68a41`
**Reviewer:** no findings.
- 04:22 `study-designer/075` a Notify or Indicate row waits for its notification — `001057729826` `ba3ad46` `3ec19b9` `5ea5ac9` `d777103a` `0dbed7c4`
**Reviewer:** no findings.
- 04:05 `ui/083` Live Study renders only the study and the project that are open now — `ba311f8` `5928bdb` `4728bb02` `3c7ea06f` `9e4ca14` `62c188d`
**Reviewer:** no findings.
- 04:03 `core/106` a stream capture says when a write failed, and its sidecars stay on Core's clock and aligned — `cd01043` `9b0d016` `5ac6e2af` `07c339c2` `62c188d`
**Reviewer:** 1 finding (`inbox/core-decision-73-amend-for-88.md`).
- 04:00 `api/142` the client and the enroll result say when an enrol moved a role — `9e4ca14` `7d0f859` `7e6d88c` `45b8f577` `1654d56f` `62c188d`
**Reviewer:** no findings.
- 03:57 `topology/059` a probe moved to another chip family is refused by name before any attach — `001057729826` `62c188d` `7c1ef59` `9f827af8` `de40e3e7`
**Reviewer:** no findings.
- 03:38 `ui/082` a live run's badge says running and counts its step — `5928bdb` `ca0caf8` `ec2653df` `394add5a` `7e6d88c`
**Reviewer:** no findings.
- 03:37 `core/110` the enroll response reports the row a probe vacated — `9b0d016` `fb993b1` `bc3d0263` `9aa520e1` `7c1ef59`
**Reviewer:** no findings.
- 03:36 `desk/004` a tile from an earlier day proposes its gap against that day's current Harvest — `670debc` `da354f8` `4594195f` `099a4e01`
**Reviewer:** no findings.
- 03:35 `umbrella/092` doctor reads a busy bench as busy, not broken — `001057729826` `9d27e12` `c75200d` `0d229bf3` `129ff9c4`
**Reviewer:** no findings.
- 03:20 `ui/090` the tile dialog sends hours only when a person changed them — `ca0caf8` `e111712` `a9debee9` `6a6f0d21` `7c1ef59` `7e6d88c`
**Reviewer:** no findings.
- 03:17 `umbrella/091` doctor and uninstall verdicts say what the docs say — `7c1ef59` `7e6d88c` `c508a4a6` `c75200d` `1e52116` `3c830dd4`
**Reviewer:** no findings.
- 03:15 `api/137` a follow ends on an unknown or interrupted study instead of waiting forever — `7e6d88c` `9ba2714` `ea13842d` `0839bc01` `7c1ef59`
**Reviewer:** no findings.
- 03:13 `topology/065` the wire-only build compiles again and enroll_reporting is public — `6732ad6` `001057729826` `7c1ef59` `321c78d6` `34774116`
**Reviewer:** no findings.
- 02:52 `umbrella/090` embarch-umbrella/open.md out of reserve by wording only — `a053cd7e` `bcbdf34d`
**Reviewer:** no findings.
- 02:51 `desk/003` a tile's hours are set by hand only when a person typed them — `da354f8` `41d9ff2` `16a5dc4b` `b1f03b2a`
**Reviewer:** no findings.
- 02:49 `smp/001` an upload that moves without progressing ends, naming its offsets — `fe68a41` `9236362` `f9138c24` `13f400b2`
**Reviewer:** no findings.
- 02:46 `topology/063` a probe moving roles never loses an enrolled row silently — `001057729826` `6732ad6` `93a83d9` `14571823` `49114c93`
**Reviewer:** no findings.
- 02:32 `umbrella/084` decisions/projects.md out of reserve by a verbatim split — `b91291cd` `2b890be4`
**Reviewer:** no findings.
- 02:30 `ui/084` a saved study is never written into another repo or stripped of its taps — `092fc6f5` `e111712` `aa5ffda` `02f058da` `5c59f1c1`
**Reviewer:** 1 finding (`inbox/ui-spec-restore-unreadable-dir-clause.md`).
- 02:28 `core/109` POST /study refuses an empty record magic — `fb993b1` `35d9859` `1b1242e7` `91f07e4d` `3ec19b9`
**Reviewer:** no findings.
- 02:26 `study-designer/076` GPIO records are named in Core's trace CSV — `001057729826` `3ec19b9` `b19c841` `cd255701` `bce31f0`
**Reviewer:** no findings.
- 02:15 `suite/004` reversals index and studies guide out of reserve by wording only — `1793000429` `267dc107`
**Reviewer:** no findings.
- 01:50 `umbrella/079` decisions/install.md out of reserve by a verbatim split — `4a7007e0` `e1015583`
**Reviewer:** no findings.
- 01:49 `core/108` the hello lock test can no longer reach a real bench — `35d9859` `8e29f06` `696488bb` `6cb252ca`
**Reviewer:** no findings.
- 01:47 `api/139` the exchange fields an older Core does not send are Option — `4e507c0f` `1793000429` `001057729826` `9ba2714` `dd49a1f` `3bca3c75` `4c412021`
**Reviewer:** no findings.
- 01:34 `ui/078` embarch-ui/spec.md out of reserve by a verbatim split — `32ede839` `3f644d7d` `dabb1a2b` `5c85d5a3`
**Reviewer:** no findings.
- 01:32 `core/104` the dev-bench gate and hello take the locks they share — `8e29f06` `da2dd1a8` `b19c841`
**Reviewer:** no findings.
- 01:30 `api/138` signal_exchange and signal-exchange say what Core saw on the wire — `dd49a1f` `d5e90265` `b19c841`
**Reviewer:** no findings.
- 01:28 `study-designer/072` a step name cannot shift CSV columns; zero records is not all verified — `84992d10` `4cd0a885` `001057729826` `b19c841` `5f42a4ab` `ea1934ad`
**Reviewer:** no findings.
- 01:13 `umbrella/009` decisions/bind.md out of reserve by compacting decision 22's retired halves — `3b923ec1` `bc5988ac`
**Reviewer:** no findings.
- 01:12 `core/098` an exchange says what happened on the wire — `de5e82a` `c0b665c` `6735517f` `c9209ff8`
**Reviewer:** no findings.
- 01:08 `api/123` signal-exchange fails loudly when no reply came back — `e5da1c4` `fcbc89c4` `d40d36fa`
**Reviewer:** no findings.
- 01:06 `study-designer/070` host-run study model — `001057729826` `ba3ad46` `30a18cdb`
**Reviewer:** no findings.
- 00:51 `ui/074` embarch-ui/open.md off its cap by deleting settled halves — `2d29cfa9` `cb4ecd14`
**Reviewer:** no findings.
- 00:51 `desk/002` fold and approve edges — `41d9ff2` `3f56975` `0f73bb27` `6082323f`
**Reviewer:** no findings.
- 00:50 `api/134` flash results carry the erased ranges — `765ff8e` `2f3749b` `719a0d42` `37012484`
**Reviewer:** no findings.
- 00:49 `core/107` one timeout_ms covers an exchange's write and read — `001057729826` `476e3e7` `3dba64b` `2fa9f645` `f93730a1`
**Reviewer:** no findings.
- 00:28 `desk/001` Harvest and Linear reads page past their first page — `3f56975` `880d970` `58b0ee4f`
**Reviewer:** no findings.
- 00:27 `chat/002` a background Agent's card shows the subagent's report — `90c6707` `82b82e0` `4b340782` `59712c51`
**Reviewer:** no findings.
- 00:23 `core/097` a console exchange's write survives a throttling device — `3dba64b` `0d712cd` `bae8d660`
**Reviewer:** no findings.
- 00:21 `api/113` embarch-api/open.md out of reserve by deleting answered questions — `df57ce53` `12c59b8d` `988469e7` `001057729826`
**Reviewer:** no findings.
- 00:00 `core/096` flash `erase: true` skips alias and option-byte regions — `0d712cd` `ec80c3d3` `8f0b1ac2` `7da4011c`
**Reviewer:** no findings.

**Hardware debts owed (verbatim from the day):**

- `core/101` **Hardware debts:** (1) the PD-bench check: 8 Hard Resets from `pd-bench` with both consoles tapped, counts
compared against a direct read of the same ports; (2) no `gaps` across a Hard Reset on a real CDC ACM console, and
`\n` really terminates its lines; (3) the two consoles' arrival stamps order correctly against a known PD
exchange; (4) native Windows build of `embarch-core` (the capture opener's COM-port open is the only new
platform surface). Everything was shown over in-process fake serial pairs. Not deployed.
- `api/148` **Hardware debts:** `core_state` (default and `halt=true`) and `mem_read` have never met a live Core; the field
names are mirrored from source. Needs a running STM32G0 and a debugger-halted core, core decision 97's debts
(1) and (2). The MCP binary is not redeployed, so the owner's session does not have `core_state` yet.
- `topology/067` **Hardware debts:** a real STM32G0 identity read reporting `halts == 1` on a running core is unverified on a
board; carried by `tasks/core/118`.
- `suite/052` **Hardware debts:** a real device with two serial interfaces under one USB serial has never been declared
or resolved with an interface (fixture and stub only); whether the DUT board exposes one is still the open
bench fact in `embarch-topology/open.md`. Not deployed: live Core, the MCP binary and the UI binary predate
this; a new UI talking to an old Core sends `interface`, which an old Core ignores, leaving the route
ambiguous as before.
- `core/103` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Bench, on the STM32G0 PD board:
(1) running core, default mode returns PCs inside the image with `halt_count` 1 (the gate's), and
`halt=true` gives 2; (2) a debugger-halted core reads found and left halted, registers read, no resume,
`halt_count` 0; (3) `DWT_PCSR` exists on the part; also `CONTROL`/`PRIMASK` unpacking from probe-rs
register 20, taken from probe-rs source. Not deployed: live Core predates this and `core/099`-`117`.
- `core/117` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). An ambiguity has never been
produced by a real pair of ports sharing a USB serial. Not deployed: live Core predates this and
`core/099`-`115`, `core/102`.
- `core/102` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). The task's bench check: the PD
source sequence as a host study against `pd-bench` gives the bash run's contract lines, and teardown leaves
the partner at 5 V after a forced failure and after a cancel; needs an enrolled signal, the e-load and an
installed Core with this build. Cancel latency against a real load (an exchange in flight cannot be
interrupted, up to 10 s). Not deployed: live Core predates this and `core/099`, `100`, `105`, `106`, `110`,
`111`, `113`, `114`, `115`.
- `core/115` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). No real port has produced these
times: the bridge's read latency and cross-capture wall-clock error are assumed. Not deployed: live Core
predates this and `core/099`, `100`, `105`, `106`, `110`, `111`, `113`, `114`.
- `api/145` **Hardware debts:** on an installed Core at `5063c0b` or later with this client, two sessions: A takes the
lease and exports the token; B's `reset`/`flash` gets the `409` naming A; A's MCP server holds past a 30 s
TTL with no manual renew; an atlas live call with the variable works while B is refused; `last_images`
shows a real flash's `sha256`. Not deployed: the MCP binary predates this, `api/131`, `api/143`, `api/135`
and `api/124`.
- `api/131` **Hardware debts:** two-console order check (two declared direct signals on a real board pair, Core at
`845f3ea` or later; a run across a DUT reset for the port-lost markers and a concurrent-call `409`), and
the replay of one field role-swap check as one call (281 command characters against 3 to 4 helper
calls; result characters need the bench). Both are in `embarch-api/open.md`. Not deployed: the MCP
binary predates this, `api/143`, `api/135` and `api/124`.
- `core/099` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). A two-client check against an
installed Core with a real probe: a second session's `POST /reset` is `409` naming the first, renew and
release work, `last_images` shows the sha256 of a real flash and a real `POST /bootload`. Not deployed:
live Core predates this and `core/100`, `105`, `106`, `110`, `111`, `113`, `114`.
- `api/143` **Hardware debts:** the two-console bench run in the task's own words (capture the DUT console, exchange
on the bench console, read from `next_offset`, reset the DUT for `reopening` + a `gaps` entry, stop);
needs Core at `845f3ea` or later deployed. Not deployed: the MCP binary predates this, `api/135` and
`api/124`.
- `core/100` **Hardware debts:** six bench checks, listed in `embarch-core/open.md` (decision 92 "has never met a
port"): a capture on one console while the other is exchanged and either board flashed and reset; an
exchange on the captured signal; a boot log across a UART-bridge reset; a CDC ACM re-enumeration with
its gap marker and a changed COM name; a multi-minute capture polled with `GET`; Windows refusing a
second open cleanly. Native Windows build of `embarch-core` (owner runs it). Not deployed: live Core
predates this and `core/105`, `106`, `110`, `111`, `113`.
- `core/105` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: live Core still
predates `core/106`, `110`, `111`, `113` and this, so the live route still exists until a redeploy.
- `core/113` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: live Core
predates `core/106`, `core/110`, `core/111` and this.
- `api/124` **Hardware debts:** on a Zephyr USB CDC ACM shell declared as a direct bidirectional signal, `shell echo
off`, then `signal-exchange --until ':~$ ' --match-after-echo false` returns in tens of ms with
`until_seen: true`, and without the flag still runs to timeout. Not deployed: the MCP binary predates
this, so the tool parameter is not live until the owner rebuilds it.
- `core/111` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). A moved-probe run: enrol a
J-Link on one board, flash a project of another chip family through it, expect `409 chip-mismatch` and
no attach. Not deployed: live Core predates `core/106`, `core/110` and this.
- `study-designer/075` **Hardware debts:** a UI-built study with a Notify row against a DUT that notifies within the row's
timeout reports `Pass` (DUT + dev-bench, Core redeployed on this crate).
- `core/106` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: the live Core
predates this and `core/110`.
- `core/110` **Hardware debts:** native Windows build of `embarch-core` (owner runs it); no live enrol run. Not
deployed: the live Core still returns the old shape.
- `core/109` **Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
- `core/108` **Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
- `core/104` **Hardware debts:** two. (1) Native Windows build of `embarch-core`, owner's, from the main
checkout — and run it before `core/108` lands only with the dev-bench unplugged if it includes
`cargo test`. (2) Hello's `503` is tested through the gate function only; reaching it through the
handler needs a bench to resolve the dev-bench port.
- `core/098` **Hardware debts:** two, from this unit; the task is retired with its bench box unticked and this is
the record. (1) Bench check of decision 85 on a real board: an exchange to a board held in reset
(`S_RESET_ST`) and to one halted by a debugger (`S_HALT`) each name the state; a command that drops
the CDC ACM port answers `port_lost` with its first output line; the guarded attach leaves a running
core undisturbed; 40 ms `QUIET_GAP` is enough for a real shell. (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/107` **Hardware debts:** two. (1) On a real CDC ACM port, confirm a blocking `write` honours the shortened
per-call timeout (folds into core/097's STM32G0 960-character check). (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/097` **Hardware debts:** three, all from this unit. (1) On the STM32G0 Zephyr CDC ACM board (the field
board, not this bench): send a 960-character line through `POST /signals/{name}/exchange` with shell
echo on and `timeout_ms` ≥ 2000; the device's own byte count must be 960. (2) Confirm Windows
`serialport` honours `set_timeout` mid-session (assumed, not measured). (3) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/096` **Hardware debts:** two, both from this unit. (1) STM32G0B1VE bench check: write a non-erased word in
a partition the image does not cover, flash with `erase: true`, `mem-read` it back as `0xFFFFFFFF`,
confirm `erased` is `["0x08000000..0x08080000"]` and the image boots; the algorithm-selector check
was tested only on a synthetic memory map. (2) Native Windows build of `embarch-core`, owner's, from
the main checkout.
*Days 2026-10-25 to 2026-10-25 rolled to [log-archive/supervisor-log-2026-10-25-to-2026-10-25.md](log-archive/supervisor-log-2026-10-25-to-2026-10-25.md).*
