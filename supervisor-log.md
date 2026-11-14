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

## 2026-11-14 11:41 — leg after api/155: no units, queue empty, dream posted

**Zero units.** A leg-level entry, not a unit entry, so it carries no `**Reviewer:**` line (no unit ran, and a `skipped` would be a false row in the tally). Nothing claimed, dispatched, landed or folded; `embarch-doc` `main` is exactly as the previous leg left it, `86233fd0` (fleet `7ecf19c` before this entry).
**Decided:** nothing numbered. One judgement call: **I dreamed.** The previous dream (2026-11-13 13:58) was past its 6 hours and unanswered, Fleet Ready was empty, and refill found nothing, so the listener's second trigger (pump on, no leg, empty queue) is what spawned this leg and a dream is what it owes. Posted 11:40 (`ts` `1794681603.529909`, `crystal_ball`, `--action`). Three proposals: (1) plug in the bench for `api/059` (dev-bench and DUT) and `dev-bench/038` (the NUCLEO-G0B1RE with the SNK1M1); (2) read UM2891 and the SNK1M1 manual and correct the two PD shields' power-connector kinds (`embarch-ui/open/bench.md`), a yes approving that web lookup; (3) decide whether `embarch-study-designer` keeps its `no_std` CI cell with no `no_std` consumer left (`embarch-study-designer/open.md`). The detail thread also carries yesterday's EMB-159/EMB-160 proposal and `doc/098`'s due date. **The detail says "queue at 11:45" and "attached at 11:40"; both readings were about 11:38.**
**Merged:** nothing.
**Blocked:** nothing.
**Refill:** `--refill-owed` fired on depth and spread (0 dispatchable, 0 scopes, wave 6). **A real re-read this time, not a diff**: all 162 questions in `collect-open-questions.py`, the roadmap's Next and the reversals index (last changed 2026-11-11, row 117). The only source change since the 2026-11-13 13:38 full sweep is `atlas/066`'s `design.md` section, which describes the replay harness and opens no question. Everything left is hardware-gated, owner-only, waiting on an owner fork, trigger-gated, or recorded as not-work. Spread sweep: nothing filed (2026-11-14 11:38).
**Hardware debts:** none new. Bench `api/059` and `dev-bench/038` stay `open`: Core reachable, neither `dev-bench` nor `dut` attached at 11:38 (`fleet-hardware.py --refresh`).
**Budget:** PROCEED, wave 6; 5-hour **66% at 11:37** (resets about 16:00), weekly 50%. Up from 60% at the previous leg's close three minutes earlier.
**Least sure about:** proposal 2's premise: I took the open bullet's word that neither manual has been read, and did not check whether `embarch-atlas` already holds either document.
**Leg close (next leg, read this first):** normal mode, pump latched 2026-11-14 11:09:56, no stop marker, nothing actionable in the channel. Step 0 found nothing to recover (no claims, no unit worktrees; the remote branches `agent/api/155-*` in both repos and `agent/atlas/066-*` in `embarch-atlas` are the usual one-fold lag and were left for `fold-commit.py`; `agent/ui/059-diff-new-lines-republish` on `embarch-doc`'s origin, older, left alone). Fleet Ready empty; `finish` moved nothing. Size ledger: only owner-only `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17). **Queue:** zero dispatchable; bench `api/059`, `dev-bench/038`; hw-gated `core/119`, `dev-bench/039`; owner-only `doc/098`; four blocked. **The 11:40 dream is the fleet's open question to the owner**, and the listener's 6-hour gate holds new spawns into an empty queue until about 17:40. `check-ownership.py --supervisor` on the leg's diff: empty diff, OK. No `suite` task, nothing deployed; the dream was the only alert sent.

---

## 2026-11-14 11:33 — api/155 a worktree session's build builds that worktree, or refuses

**Decided:** **`embarch-api` decision 106**, the worker's (normal mode, so a worker may number one): at startup, after the config loads, `src/worktree.rs` compares each project's `source_path` with the working directory by read-only `git rev-parse` (`--git-common-dir`, `--show-toplevel`); same repository, different working tree, and `source_path` moves to the same relative path under the worktree's root, with `build_dir_root` moved to `<build_dir_root>/worktree-<dir name>-<8 hex FNV-1a of the worktree path>` so a worktree build never writes or reuses the main clone's directory. **A worktree that lacks the path refuses at startup, naming both trees, and that stops the whole server** (all projects), accepted in the decision as loud over wrong. Not moved: absolute paths inside a static `build_command` or `env` values, and a `source_path` outside any git repo. Done in `embarch-api`'s own code, so `embarch-firmware-build`'s public API (which `embarch-ui` uses) is unchanged; the only crate edit deletes `api/154`'s pinning test, so I did not build `embarch-ui`. `spec.md`'s known-defect bullet (my reword at the `api/154` fold) is replaced by the rule. **Also closed: `tasks/api/156` (EMB-182)**, the `api/154` reviewer's finding, which I filed `done` at its split because I had already reworded the bullet in `api/154`'s fold; it is retired in this fold.
**Merged:** `agent/api/155-a-worktree-session-build-builds-the-worktree` (code `54d4035`, ff on `4707020`; doc `1ddd14b6`, cherry-picked onto `0188da88`). Gate on the merge result with `EMBARCH_REQUIRE_LEASE=1` exported: `cargo build`, `cargo test --no-fail-fast` 404 passed 0 failed, `cargo clippy --all-targets -- -D warnings` green; ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none for a board. **Owed, owner-side:** a real build asked from a Start work worktree session, to see it take the worktree's tree and its own build directory; unit tests only so far. It depends on the MCP server's working directory being the worktree, which is `embarch-desk`'s side and was not assumed.
**Budget:** PROCEED, wave 6; 5-hour **23% at 11:16 to 60% at 11:34**, weekly 47% to 50%.
**Least sure about:** the reviewer noted the rebase runs for every CLI subcommand that loads a config, not only the MCP server, so any `embarch-api` command run from a worktree that lacks the project's path now refuses to start; consistent with the rule, but it is a wider blast radius than the decision's wording says.
**Leg close (next leg, read this first):** **4 of 4 units, all from Fleet Ready**, landed in this order: `api/154` (EMB-128, investigation; reviewer 1 finding, EMB-182), `atlas/065` (EMB-179), `atlas/066` (EMB-148), `api/155` (EMB-181, the fix 154 found). Leg began at `b69b1db2` (fleet `6df0c08`); `check-ownership.py --supervisor` on the leg's diff OK. **What you would not expect:** (1) the owner moved EMB-148 and EMB-179 into Fleet Ready three minutes into this leg, and the leg's own units filed two more (EMB-181 by a worker, EMB-182 by a reviewer), so Fleet Ready was read four times; (2) I reworded a worker's `spec.md` bullet at the `api/154` fold on the reviewer's finding, and closed EMB-182's task `done` at its split rather than dispatching a worker to a sentence already fixed; (3) the 5-hour window climbed 23% to 60% in about twenty minutes, so the next leg may meet the 90% HOLD within two legs. **Closed:** EMB-128, EMB-179, EMB-148; EMB-181 and EMB-182 close at this fold's `finish`. **Queue left:** zero dispatchable; bench `api/059`, `dev-bench/038` (neither role attached at 11:11); hw-gated `core/119`, `dev-bench/039`; owner-only `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17, three days); four blocked. No dream posted: this leg ended at its cap, not on an empty refill, and the last dream (2026-11-13 13:58) is past its 6 hours, so the next leg refills and dreams if nothing new arrives. **Owed by the owner:** the first real `scripts/replay.py` run (atlas/066), a real worktree-session build (api/155), and the deploy debts carried from earlier legs (the desk, decision 85 plus a plugin version bump; the UI service, decision 102; Core per `embarch-dev-workflow.md` §4a). No `suite` task, nothing deployed, no alert sent.

---

## 2026-11-14 11:31 — atlas/066 a replay harness for atlas lookups against recorded sessions

**Decided:** nothing numbered (`embarch-atlas` keeps no `decisions.md`). EMB-148, the worker's: `scripts/replay.py` in `embarch-atlas`, a script and never a verb or MCP tool because it reads private transcripts. It scans a project's transcripts (subagents included) for two named patterns, `config-grep` (to `q config SYMS`) and `config-diff` (to `q config SYMS --vs`), and with `--atlas-dir`/`--build-dir` replays them, printing calls and characters before and after, numbers only; `--report` prints the `## Result` table. **A recorded command is never run:** it is parsed, and an argv is rebuilt from the parts with whitelisted flags and no shell, the `.config` path rebuilt from `--build-dir`/`--vs-dir`; pipes, redirects and substitutions do not match. The lookup runs in process against a `/tmp` copy of the atlas dir with `GIT_OPTIONAL_LOCKS=0`; a test proves the real atlas and build dirs are byte-identical after a replay. `--pinned` added; a failed replay counts as skipped, not dropped; the optional old-lookup comparison not built.
**Merged:** `agent/atlas/066-a-replay-harness-for-atlas-lookups` (code `1e6a07b`, ff on `ceb64ac`; doc `7b25c952`, cherry-picked onto `51893a2d`). Gate on the merge result in the unit's worktree with its own venv: `pytest -q -rs` 836 passed, 3 skipped (real west workspace, real atlas, vendor SVD: env-gated), `test_public_guard` ran; ownership `atlas` OK on both branches, client names clean, `check-docs.py` 12/12. I read the two `subprocess.run` sites myself: `grep` and `diff` only.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the first real run, `scripts/replay.py --project <name> --atlas-dir <atlas> --build-dir <build> --report`; the parsers are deliberately narrow and may match fewer calls than atlas task 003's throwaway script did.
**Budget:** PROCEED, wave 6; 5-hour 23%, weekly 47% at 11:21.
**Least sure about:** whether `q config --build` writes into the build dir during a replay; the reviewer flagged that neither the code nor `DESIGN.md` says, and the byte-identical test may not cover that path.

---

## 2026-11-14 11:23 — atlas/065 schematic writes its extraction issues to a readable file

**Decided:** nothing numbered (`embarch-atlas` keeps no `decisions.md`). EMB-179, the worker's: `embarch-atlas schematic` writes `boards/<label>/issues.md` beside `nets.md` and `parts.md` and prints its path; `MAP.md` names that path on each board's line. Issues are plain strings in `netlist.json`, so a new `smartpdf.classify_issue` derives kind, net and sheet from the text by pattern, page from the text or the sheet's page, `-` where a kind carries none, `other` for unmatched text, and the original text follows `|` on every line. The optional `q schematic-issues` lookup was not added. Recorded debt, not a contradiction (the reviewer checked): `MAP.md` names `issues.md` for a board extracted before this change, where the file appears only once `schematic` is re-run.
**Merged:** `agent/atlas/065-schematic-writes-its-issues-to-a-readable-file` (code `ceb64ac`, ff on `d0c2f12`; doc `f293ce41`, cherry-picked onto `e9120d26`). Gate on the merge result in the unit's worktree with its own venv: `pytest -q -rf` 829 passed, 3 skipped, `test_public_guard` ran (checked alone); ownership `atlas` OK on both branches, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, wave 6; 5-hour 23%, weekly 47% at 11:16.
**Least sure about:** the pattern-based `classify_issue`: an extractor message whose wording changes later falls to `other` silently rather than failing a test.

---

## 2026-11-14 11:20 — api/154 which tree a worktree session's build builds

**Decided:** nothing numbered. EMB-128 answered, the worker's, by a run: for a project configured on the main clone and a server started in a worktree, `west` runs in the config's `source_path` verbatim, the app path is `<source_path>/app/<app>`, `-d` is under the config's `build_dir_root`, and the plan sets only the project's `env` table over the server's inherited environment. So a worktree session builds **the main clone**; the working directory only finds the config. Bug **EMB-181** filed by the worker (Fleet Ready), fix not attempted. A test (`a_zephyr_build_runs_in_and_builds_the_configured_source_path_not_the_working_directory`, `resolve.rs`) pins today's behaviour and goes when EMB-181 lands. I posted the answer on EMB-128 as a `Finding` comment. **My own edit at the fold, on the reviewer's finding (EMB-182):** the worker's `spec.md` bullet stated the defect as a "never" invariant and the fragment filed it as decided; I reworded the bullet as a known defect that EMB-181's fix replaces, and the history line likewise, before the doc half reached `main`, so `main` never carried the invariant wording.
**Merged:** `agent/api/154-which-tree-a-worktree-session-build-builds` (code `4707020`, ff on `d97985f`, test only in `crates/embarch-firmware-build`, which `embarch-ui` also consumes, but the change is inside `#[cfg(test)]`; doc `12670bf9`, cherry-picked onto `c80b45ee`, plus my reword in this fold). Gate on the merge result with `EMBARCH_REQUIRE_LEASE=1` exported: `cargo build`, `cargo test --no-fail-fast` 402 passed 0 failed, `cargo clippy --all-targets -- -D warnings` green; ownership `api` OK on both branches, client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-182
**Hardware debts:** none.
**Budget:** DEGRADED wave 2 at the leg's start (stale cache), then PROCEED wave 6 at 11:16; 5-hour 23%, weekly 47%.
**Least sure about:** whether a worktree's `settings.local.json` `env` reaches the MCP server's process at all; the worker did not check it and it is the desk's side, so EMB-181's fix may need a desk half too.
**Leg notes (this leg, first unit):** normal mode, pump latched 11:09:56 by the owner, no stop marker, nothing actionable in the channel; the 2026-11-13 13:58 dream got no reply. Leg began at `b69b1db2` (fleet `6df0c08`); step 0 found nothing to recover. Fleet Ready held EMB-128 at the first read and **EMB-148 and EMB-179 by the second, three minutes later**, so the owner moved them in while this leg ran; split into `api/154` (`8e4dd179`), `atlas/065` and `atlas/066` (`1b7b0aad`), all announced. Size ledger: only owner-only `doc/098`, due 2026-11-17. Bench: Core reachable, neither role attached at 11:11. Refill owed on depth and spread; the only source commit since the 2026-11-13 13:50 marker is `core/126`'s verbatim split, so no re-read. Spread sweep: nothing filed (2026-11-14 11:11). Day fold: 2026-11-13 folded by an `embarch-log-folder` agent, 2026-11-11 rolled to `log-archive/`. Client-name history scan: all 16 repos clean. Dispatched 11:12 `api/154`, 11:17 `atlas/065`.

---

## 2026-11-13 — 8 units

*Folded by an embarch-log-folder agent on 2026-11-14 (leg fold). Dropped: per-unit narrative reasoning, gate transcripts and worker-answer commentary; git holds them. Kept: every SHA, every Reviewer line, every hardware-debt line, and what the next leg cannot recover.*

**Carry forward (read first):**
- **Dream open:** posted 13:58:12 (`ts` `1794603492.409399`, `crystal_ball`), three proposals (plug in the bench for `api/059` and `dev-bench/038`; move EMB-160 and EMB-159 to Fleet Ready). Owner has not answered; the 6-hour dream gate holds until about 20:00. No second dream was posted by the 14:02 leg.
- **EMB-175 (Backlog, `Scope: fleet`):** `fleet-read.py --leg-gate` counts the queue in the owner's `CONF.doc_repo` checkout without a fetch, and legs push from a detached worktree, so the checkout was stale (`90ffd7fa`) and read landed tasks as 2 dispatchable, returning SPAWN before the dream check. Until fixed, a leg that lands the last open tasks and then dreams is followed by one empty leg. Filed `--from audit` to Backlog deliberately (Fleet Ready counts in the same gate). Unproven whether it explains all three of `tasks/doc/096`'s earlier post-dream spawns.
- **Unnamed flaky atlas test:** one atlas test failed once at `atlas/063`'s gate (824 passed, 1 failed) and passed alone; its name was lost. If it recurs, run `pytest -q -rf` the first time.
- **Budget:** 5-hour window 8% at 13:22 to 86% at 14:02 (resets about 16:10), weekly 38% to 44%; the next spawn is likely to meet the 90% HOLD.
- **Queue left:** zero dispatchable; bench `api/059`, `dev-bench/038` (no role attached at 14:01); hw-gated `core/119`, `dev-bench/039`; owner-only `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17); four blocked. Both compactions (`api/150`, `core/126`) landed, so no size debt besides `doc/098`.
- **Deploy debts owed by the owner, unchanged:** the desk (decision 85 plus a plugin version bump), the UI service (decision 102), Core per `embarch-dev-workflow.md` §4a.
- **Open owner questions / leftovers:** the other copy of the R3.2 patch outside the suite is untouched (`embarch-dev-bench/open.md`); remote branch `agent/ui/059-diff-new-lines-republish` still on `embarch-doc`'s origin, left alone. Reusable trick: `west update --path-cache` from the main checkout's `native_sim` workspace makes a fresh pd-bench workspace a few minutes (2.7 GB per unit worktree).
- **Recovery done:** the 2026-11-12 20:04 leg died mid-fold; I reset its leg worktree to `origin/main` and landed `api/152` and `atlas/063` as ordinary units (063's code `3f3d77c` was already on atlas main). Day fold of 2026-11-12 and roll of 2026-11-10 to `log-archive/` done at 13:26. Client-name history scan: all 16 repos clean.
- **Decisions:** none numbered all day. `atlas/064` recorded a design choice in `embarch-atlas/design.md` (a cross-document page cite contributes to no frozen set; accepted cost: a change to the other document's page no longer thaws the unit). Fleet `cb2b4df` at the first leg, `ed64e0f` at the later two; no `suite` task, nothing deployed; the dream was the only alert sent.

### 14:02 — leg after dev-bench/047: no units, queue empty, spawned past a standing dream
Zero units; a leg-level entry, so no unit Reviewer line (no unit ran). `embarch-doc` `main` stayed at `b69b1db2`. Depth sweep was a diff, not a re-read (only `api/150`, `core/126`, `atlas/064` design section since 13:38); nothing filed.
**Merged:** nothing.
**Blocked:** nothing.
**Hardware debts:** none new. Bench `api/059` and `dev-bench/038` stay `open`: Core reachable, neither `dev-bench` nor `dut` attached at 14:01 (`fleet-hardware.py --refresh`).
**Least sure about:** whether EMB-175 explains all three earlier post-dream spawns.

### 13:57 — dev-bench/047 the carried R3.2 patch's usbc_pd.h includes zephyr/toolchain.h
EMB-147, toolchain unit run by the leg's own hands: `usbc-pd-r32.patch` gained one hunk adding `#include <zephyr/toolchain.h>`; patch edited by hand, post-image blob id `273904975c1`, `patches.yml` sha256sum updated, `pd_logic.h` workaround dropped. Red first, then 13 of 13 on `native_sim`, both shields built.
**Merged:** `agent/dev-bench/047-usbc-pd-header-compiles-on-its-own` (code `0aaf5d6`, ff on `50579d3`; doc `dc24b67c`; later fold `b69b1db2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; both shield builds are build-only, as decision 59 has it.

### 13:51 — core/126 core's open.md split by mission
Verbatim split: seven `## Never exercised` bullets moved to `embarch-core/open/never-exercised.md`; `open.md` 4,314 to about 2,670 B.
**Merged:** `agent/core/126-compact-core` (doc only: `cd20175e`, cherry-picked onto `1d2af482`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.

### 13:50 — api/150 split api's open.md by mission
Verbatim split: seven verification-debt bullets moved to `embarch-api/open/bench-verification.md`; `open.md` 4,502 to 3,076 B.
**Merged:** `agent/api/150-compact-api` (doc only: `e1c6b57f`, ff on the claim `afd23f2b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.
**Least sure about:** I did not read `spec.md` to judge the worker's compaction answer.

### 13:45 — api/153 test scratch directories named from a counter, not the clock
EMB-169: `support::unique_dir(tag)` (pid plus `AtomicUsize`) used by ten clock-named test files; `src/main.rs` got an inline counter. 500 loaded runs, 0 failures; 401 passed on the merge result.
**Merged:** `agent/api/153-test-scratch-dirs-named-from-the-clock` (code `d97985f`, ff on `af2ea2b`; doc `82c27cda`, cherry-picked onto `94d7a010`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** the `src/main.rs` counter had no load run of its own.

### 13:40 — atlas/064 freeze leaves a cite of another document out of the citing document's pages
EMB-109: a cross-document page cite contributes to no frozen set; `check.find_sibling` now shared with `freeze.own_cited_pages()`. `pytest -q` 826 passed, 3 skipped.
**Merged:** `agent/atlas/064-freeze-files-a-cross-document-cite-under-its-own-document` (code `d0c2f12`, ff on `3f3d77c`; doc `57d06376`, cherry-picked onto `893d0440`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** whether "none" is what the issue's author wanted; a unit resting on a changed page of another document now stays frozen silently.

### 13:39 — atlas/063 check K holds a record to the group its cond names
EMB-113: check K picks a record's table group by the condition its `cond` names; an unmatched `cond` is reported (`K_cond: unmatched`). Gate: 824 passed, 1 failed (flake, name lost, see carry-forward). Spread sweep since the `2026-11-09 17:34` marker: nothing filed (13:38).
**Merged:** `agent/atlas/063-check-k-holds-a-record-to-its-conditions-group` (code `3f3d77c`, ff on `78fe5b4`, landed by the 2026-11-12 20:04 leg before it died; doc `d31ba2ec`, cherry-picked onto `4eedc6ad`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 13:26 — api/152 CLI tests fail when cargo test runs from outside the repo
EMB-158: `EMBARCH_REQUIRE_LEASE=1` leaked into five subprocess tests; `support::api_command` calls `env_remove` on it. Not the same bug as EMB-169. Gate run with the variable exported: 401 passed.
**Merged:** `agent/api/152-cli-tests-fail-from-outside-the-repo` (code `af2ea2b`, ff on `e4957c5`; doc `8cbd3642`, cherry-picked onto `5914a007`). Recovered from the 2026-11-12 20:04 leg, which had pushed both branches; that leg's `core/126` split of EMB-169 went in at `5acbaa19` and `core/126` was released at `ff933079`. This leg began at `ff933079`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** I did not re-run from the suite root itself, only proved the variable no longer reaches the binary.

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

*Days 2026-11-11 to 2026-11-11 rolled to [log-archive/supervisor-log-2026-11-11-to-2026-11-11.md](log-archive/supervisor-log-2026-11-11-to-2026-11-11.md).*
