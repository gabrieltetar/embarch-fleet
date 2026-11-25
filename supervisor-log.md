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

## 2026-11-25 01:11 — umbrella/107 compact-umbrella

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says. The whole "Command surface" section (the seven-row command table and the exit-codes line) moved from `embarch-umbrella/spec.md` into the new `embarch-umbrella/spec/commands.md`, beside `marketplace.md`; `spec.md` 9,272 to 6,329 B, out of reserve, with the heading and a pointer left in place. Decision numbers 12, 21, 26, 41, 46, 58, 59, 60 and EMB-192 kept. Only three relative link prefixes changed (one level deeper). No `decisions/` file touched; several still sit within 200 B of their limit (`prune-policy`, `deploy`, `mirrors`, `budgets`), and the next umbrella decision lands on one of those.
**Merged:** `agent/umbrella/107-compact-umbrella` (doc `f2538f73`, the worker's `a1c44420` cherry-picked onto `6a54b70b`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6); PROCEED at this fold (5-hour 31%, weekly 84%).
**Least sure about:** whether the command table was the right section to move: it is what a reader of the umbrella reaches for first, and it now sits one click away.

---

## 2026-11-25 01:11 — atlas/107 compact-atlas

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says. Two sections moved byte-identical from `embarch-atlas/design.md` into the new `embarch-atlas/design/library-and-cad.md`: "A shared datasheet library, and a copy of every file an atlas read" and "Reading an Altium project's sources: `cad`". `design.md` 23,474 to 19,214 B, out of reserve; each heading stays with a one-line pointer. The worker avoided "Protocol records" because `notes/hil/04-premade-suites.md` links its anchor, and left the measured-plane sections alone. **Finding, for the owner's `scripts/`:** `check-links.py`'s `anchors_of()` slugs headings from `strip_code(body)`, which drops inline code spans, so a heading like "sources: `cad`" is recorded as `#...-sources` where GitHub renders `#...-sources-cad`. The gate therefore requires the pointer this unit wrote (`#reading-an-altium-projects-sources`), which will not jump to the section on GitHub; I tried the GitHub form and the gate refused it, so I left the worker's. Any link to a heading with inline code has the same mismatch.
**Merged:** `agent/atlas/107-compact-atlas` (doc `6a54b70b`, the worker's `0fc7b04d` cherry-picked onto `99057054`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6); PROCEED at this fold.
**Least sure about:** that the anchor mismatch is worth a fix: it only costs a jump-to-section, and every heading with inline code in the suite has it.

---

## 2026-11-25 01:10 — desk/038 compact-desk

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). **I unparked four size debts early, for the verbatim moves their own tasks name:** `desk/038`, `atlas/107`, `umbrella/107` and `promptu/025` were `blocked` on `In flux: yes`, none overdue (due 2026-12-01 to 12-09). Each task's What is a verbatim move, and `DOC-BUDGET.md`'s split-first rule says flux cannot forbid one, so at claim I rewrote each `In flux:` to "no — for the move this task makes", keeping the old answer as history (`core/093`'s form, 2026-09-28), with a dispatch note saying move only, squeeze nothing. **`suite/061` (the studies guide, 25,636 of 25,600 B on the ledger allowance) is unparked the same way and announced, ts `1795593942.722269` at 01:05**: it is `open`, the window closes 01:35, and a later leg runs it as its last unit if no objection is in that thread (move §4 verbatim into its own guide). This unit: §1's desks and knowledge paragraphs and §3's body moved into `embarch-desk/spec/desks-knowledge-interfaces.md`; `spec.md` 9,225 to 7,795 B, out of reserve; §2's invariants stay. Only relative link prefixes changed; I checked every removed line against the new file. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker). **Linear is rate-limited all leg** (2,500/hour cap): `ready --brief`, `list` and `queue-status.py`'s Fleet Ready read all exit 2 from 01:00, failing on a per-issue GET partway through. `ready` and `list` fetch every open issue one request at a time, so one read costs about one request per open issue. No Fleet Ready issue was read or split this leg; EMB-404 to EMB-406 should now be unblocked by EMB-403's landing, unverified. `finish` ran (exit 1: EMB-334, EMB-312 and EMB-136 still have tasks open). The refill gate fired on depth (0 dispatchable tasks); since the 2026-11-24 02:36 sweep the only source commits are `promptu/024`'s `open.md` bullet (paid here by `promptu/025`), `embarch-dev-bench/open/analog.md` (every item a bench run) and `ui/115`'s already-judged line, so I filed nothing and did not re-read the rest. **Log defect, not touched:** the `## 2026-11-24 — 43 units` heading, its note, carry-forward and splits paragraph appear twice in a row in this file; the day's `###` entries follow the second copy only.
**Merged:** `agent/desk/038-compact-desk` (doc `0ce75348` and `99057054`, the worker's `8bf257a8` and `7656f71a` cherry-picked onto `005334ad`; no code repo). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 27%, weekly 83%, wave 6), four dispatched in one wave; PROCEED at this fold (5-hour 31%, weekly 84%).
**Least sure about:** the early unpark: the filers chose "rides in the next unit that writes the file", and I read the split-first rule as overriding that for a verbatim move; `core/093` did the same only once its debt was overdue.

---

## 2026-11-25 00:56 — atlas/108 the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-atlas/src/embarch_atlas/livelog.py` no longer keeps `UNGATED`: `note()` writes no line when the api's `--json` answer carries no gated `core_calls` (absent, empty, null or study-only), which the reviewer traced to the api's own trace filter (`lease_gate::is_gated` in `client.rs`, `core_calls` added in `cli.rs` only when non-empty), so the five old verbs behave exactly as before. The path walk is split out as a pure `repo_above(here)`. `tests/test_livelog.py` gains a lease-free-verb test (the five old verbs and an invented one) and a test parametrised over `../embarch-api/tests/fixtures/live-log/*.json` (`api/191`'s 19 cases), comparing the path and the line minus `t`, `writer`, `via`, `sent` and the atlas's own `outcome`; a companion test asserts at least 19 cases when the sibling is there and skips with its reason when it is not. The code repo's `DESIGN.md` gains one paragraph; `embarch-doc/embarch-atlas/design.md` never named `UNGATED`, so it is untouched and still in reserve (2,126 B, `atlas/107` parked). **Coverage the worker disclosed and the reviewer judged a gap, not a contradiction:** the atlas has no configured-project list, so the three `source_path`-fallback cases only assert that the walk finds no `embarch/`; and the board-order cases are replayed as `--role`/`--probe-serial`/`--chip` flags in entry order, a stand-in for how the atlas learns a board. **Worktree link, new for this unit:** I linked `embarch-api` (the main checkout, which I pulled to `c254d15`) beside the atlas worktree; `.claude/leg.md`'s table lists only `.atlas-local` for `embarch-atlas`, and any atlas unit after this one needs both. EMB-319's last task: `finish` after this push should move it to Done.
**Merged:** `agent/atlas/108-the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture` (code `d0b5ca5`, ff from `74048d8`; doc `347a28f4`, the worker's `31792f90` cherry-picked onto `0d7e8a3c`). Re-gated on the merge result: `.venv/bin/pytest -q` 1052 passed, 3 skipped (all three on `EMBARCH_ATLAS_REAL_*`, none of this unit's; `test_public_guard` and the fixture tests ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 22%, weekly 83%, wave 6); PROCEED at this fold.
**Least sure about:** the fixture test needs a sibling `embarch-api` checkout that carries the fixture; the atlas's own CI has none, so there it skips and reads green, and only the fleet's gate (with the link above) or a full suite checkout runs it.

---

## 2026-11-25 00:54 — api/190 hil-guide-words-point-at-the-glossary

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). The HIL guide's Words entry for Study now reads "**Study** (the mode; **a study** is its file): a custom question answered by measurement on one bench, run by `run_study` or `run_host_study`. EmbArch's glossary row **Study** is the definition." Bench, Test, Run, Measurement and Verdict keep their gloss in place, since the glossary has no row for them (`doc/102` added Study only). **How it landed:** the worker edited the api's pinned copy (`guide/hil-guide.md`) and quoted the bytes in `status.d`; I applied them to `suite/hil-guide.md` in this fold (22,829 B), as `api/189`. The drift guard (`tests/guide_cli.rs`) ran green with `EMBARCH_DOC_DIR` at my leg worktree carrying the edit; between the code push and this fold, `main`'s suite copy differed from the api's pinned copy for about four minutes. **Reviewer's note, below its bar, not filed:** the bullet no longer says `run_study` runs on the dev bench and `run_host_study` on Core's runner; the guide's own Study section still does. EMB-317's last task: `finish` after this push should move it to Done.
**Merged:** `agent/api/190-hil-guide-words-point-at-the-glossary` (code `a3d0831`, ff from `c254d15`; doc `0d7e8a3c`, the worker's `b1e151df` cherry-picked onto `fcadb4c0`); the suite guide edit is in this fold commit. Re-gated on the merge result: `cargo build`, `cargo test` (no failures; `guide_cli` 4 passed against the edited guide), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 22%, weekly 83%, wave 6), two dispatched; PROCEED at this fold.
**Least sure about:** "EmbArch's glossary row **Study** is the definition" points a binary-only reader at a doc they may not have; the gloss in front of it carries the meaning, but the pointer is only useful with a repo at hand.

---

## 2026-11-25 00:39 — promptu/024 the-contract-fixes-build-step-5s-shapes-and-forks

**Decided:** nothing suite-wide, and **no new decision** (burndown leg; the issue itself says the forks hold the choices). `embarch-promptu/docs/contract.md` gains §15 "The linker's kinds (build step 5)": §15.1 the reference entry (`kind`, `key`, `words`, `names`, `line`, `text(find)`, scored within a kind, then merged), §15.2 the `<references>` block (12 lines, 3,600 characters, 4 per kind) and one table of the twelve kinds (source, refresh, cue words, written form), §15.3 the JSON of `embarch-atlas refs`, `embarch-api --json list-studies` and the desk's `GET /refs` `projects`/`documents`, each carrying its own marker rather than `"promptu": 1`. §11 gains "From step 5" and §0 names step 5 (no model call). `docs/forks.md` gains L1 to L22, the riskiest five first (L11 cue-word gate, L5 Core through the api CLI, L3 the atlas verb, L10 block size, L2 contract first); **L1, L18, L19 and L21 say the plan's choice is unrecorded and the owner's to state** (my Question on EMB-403 asks for them). Promptu's `spec.md`, `spec/status.md`, `interfaces.md` say step 5 is under way and point at §15; `open.md` names the four unrecorded choices. **The worker's calls, which I keep:** instruments, captures, traces and worktrees are gated too, as their issues say, wider than the task's "high-volume" list; the numeric limits (300 branches, 200 projects, 500 documents, 60 s, 5 min, 20 studies) are marked assumed in the forks. **New debt, filed by the worker:** `tasks/promptu/025-compact-promptu.md`, `blocked`, due 2026-12-09: `embarch-promptu/open.md` 4,060 of 5,120 B; `In flux: yes`. Its own What is a verbatim move of settled step 1 to 3 bullets into `open/`, which flux does not forbid, so the next leg may unpark it. **Reviewer's note, below its bar, not filed:** §15.2 and L14 say "only decision 16's atlas citations become links", which read literally omits decision 88's issue/PR prose links; the same section says issues and PRs follow 88, so it reads as scoped to the new kinds. L10 cites "2,400" for decision 88's block, a figure not in 88's text. This landing is what EMB-404 to EMB-406 wait on in Linear: `finish` after this push should move EMB-403 to Done and let the next `ready` split the atlas, api and desk read surfaces.
**Merged:** `agent/promptu/024-the-contract-fixes-build-step-5s-shapes-and-forks` (code `6d091a1`, ff from `dcb6588`, docs only; doc `076da6d2`, the worker's `15a24261` cherry-picked onto `0bf5cb47`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. I read the contract diff before merging. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 0%, weekly 80%, wave 6); PROCEED at this fold (5-hour 21%).
**Least sure about:** whether the four missing choices change §15 itself: I told the owner they do not, but choice 1 could be the step's scope (which kinds exist at all), and if so the kinds table is built on an assumption no issue states.

---

## 2026-11-25 00:37 — api/191 a-shared-fixture-pins-the-live-log-rules

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-api/tests/fixtures/live-log/` holds 19 plain-JSON cases pinning the five rules both live-log writers share (the 4096-byte answer cap with 2- and 4-byte characters at the cut, the board order body then arguments then answer, `repeat`/409/headerless `core` entries, the path walk with the `source_path` fallback and the git-root stop, and the `<date>-<session>` name with a `+02:00` start left unconverted and the no-lease case). `src/live_log.rs` gains a pure `build_line(call, live, lease, status, now)` and `repo_above`/`repo_dir_from`; `record()` calls them with the real lease, status and clock, so behaviour is unchanged (the reviewer checked). A unit test runs every case and compares the path and the line minus `t`, `writer`, `via` and `sent`. `interfaces/live-log.md` gains "The shared fixture": the case format key by key, the compared fields, the sibling path a second writer reads, and that a rule change lands in the fixture first. **My split of EMB-319:** this task, then `atlas/108` (delete `UNGATED`, a pytest reading these cases from `../embarch-api/`), unparked to `open` in this fold. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no unfolded `status.d`). The owner re-armed burndown at 00:01 (weekly 80%, until 2026-11-25 06:00). `finish` moved EMB-308 and EMB-304 to Done, so the Linear cap the last legs hit is clear. Fleet Ready held 18 unsplit issues and 45 waiting; I split two at `39be7664`: EMB-403 to `promptu/024`, EMB-319 to this task and `atlas/108`; announced ts `1795590679.186489`. **EMB-403, which the last legs did not take:** the plan it cites is in no repo, but EMB-404 to EMB-415 state its choices 2 to 17, 20 and 22; choices 1, 18, 19 and 21 are stated nowhere, so the forks for them say so and I asked the owner on EMB-403 (a Question comment). **Not taken in burndown, as the last legs judged:** EMB-323, 326, 338, 352, 362 (new decisions), EMB-358 and the audit's cross-repo changes EMB-295, 302, 303, 305, 306, 307, 314 (suite passes), EMB-387 and 388 (toolchain hands). The refill gate fired on depth (1 dispatchable); the only sources changed since the 2026-11-24 02:36 sweep are `embarch-dev-bench/open/analog.md` (new, every item a bench run) and `ui/115`'s already-judged line, so no sweep. **Day fold:** an `embarch-log-folder` folded 2026-11-24 (43 units, 117.9 KB to 40.7 KB, `--apply` confirmed 186 SHAs, 43 reviewer lines, 4 debt lines), and `--roll` moved 2026-11-22 to `log-archive/`; both ride in this fold. `check-client-names.py --suite --history`: all 16 repos clean. Wave 1 was this and `promptu/024`, two foreground workers in one message with the log folder, all reported to the leg; reviewers ran foreground after the merges.
**Merged:** `agent/api/191-a-shared-fixture-pins-the-live-log-rules` (code `c254d15`, ff from `d755007`; doc `0bf5cb47`, the worker's `50b9ec81` cherry-picked onto `aed2c46d`). Re-gated on the merge result: `cargo build`, `cargo test` (no failures, the new `every_shared_fixture_case_comes_out_as_pinned` among them), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No feature row.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 0%, weekly 80%, wave 6), two dispatched; PROCEED at this fold.
**Least sure about:** the fixture's expected values were generated by the worker in Python and checked against the Rust once, with no mutation run, so a case that pins a wrong value would pass both writers equally; the atlas half is where a disagreement would first show.

---

## 2026-11-24 — 43 units

*Folded by leg 010 successor on 2026-11-25 (embarch-log-folder): per-unit narrative reasoning, gate transcripts and budget lines dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, debt and the spread sweep line kept.*

**Carry forward.** Burndown ran 00:06 to 02:36 and ended on an empty queue (pump stays latched in normal mode); a second burndown leg 03:05 onward ran to the 14:28 fold with the usage cache stopped at 14:00. Open at day end: a **second listener session is live** and spawns a leg per leg death, each waiting on the leg lock (doubles Linear reads); **Linear's 2,500/hour cap** is hit repeatedly, so `filed`/`finish` for EMB-320, EMB-312, EMB-308, EMB-402 and the EMB-317 move may not have reached Linear (next `ready` reports ALREADY SPLIT; re-run `filed`/`finish`); 25+ Fleet Ready issues unsplit; EMB-403 not taken (cites a plan found in no repo); `suite/058` parked to 2026-12-01 (announce first); `api/188` parked on the owner supplying the et54 load's input-off command. Owner questions: replay cost cap (W24), EMB-398 token scope, EMB-399/EMB-400 findings. Owed: `notes/goals/03-status.md` goal 3 still says topology alone opens a probe or port. Safe-off re-declare: `PUT /instruments` replaces by name. Dream ts `1795512985.272199` (previous dream ts `1795476373.403649`, 10 h and 133 commits earlier).

**Splits this day (Linear to task file; commit, announcement ts):** EMB-278 to `promptu/021` (`bd163fc8`, `1795503287.195659`); EMB-283/284 to `desk/043`+`ui/113` and `chat/035` (`248e2321`, `1795505033.011589`); EMB-318 to `doc/100`, EMB-297 to `api/186`+`core/149`+`umbrella/104` (`245c7cbf`, `1795515529.865329`); EMB-310/320/312 at `afe9024f` (`1795518116.601709`); EMB-321 to `topology/072`, EMB-299 to `umbrella/106`, EMB-386 to `ui/116`, EMB-357 (`f9bb180f`, `1795535418.541089`); EMB-401/400/399/389 (`3711fb0d`, `1795541360.131669`; the unit-`study-designer/091` split `2ff73f95` above is a separate commit); EMB-343 to `umbrella/108`, EMB-322 and others (`cd0b1fe8`); EMB-402/308/344 (`4a4a7f87`, `1795549699.487149`; `suite/060` window ts `1795543398.128079`, follow-up announcement `1795543453.347959`); `c06ce2be` as above. Owner's `ed5d290a` (the HIL guide's Live section) reached `origin/main` during `api/189`.

Spread sweep: nothing filed (2026-11-24 00:23)

## 2026-11-24 — 43 units

*Folded by leg 010 successor on 2026-11-25 (embarch-log-folder): per-unit narrative reasoning, gate transcripts and budget lines dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, debt and the spread sweep line kept.*

**Carry forward.** Burndown ran 00:06 to 02:36 and ended on an empty queue (pump stays latched in normal mode); a second burndown leg 03:05 onward ran to the 14:28 fold with the usage cache stopped at 14:00. Open at day end: a **second listener session is live** and spawns a leg per leg death, each waiting on the leg lock (doubles Linear reads); **Linear's 2,500/hour cap** is hit repeatedly, so `filed`/`finish` for EMB-320, EMB-312, EMB-308, EMB-402 and the EMB-317 move may not have reached Linear (next `ready` reports ALREADY SPLIT; re-run `filed`/`finish`); 25+ Fleet Ready issues unsplit; EMB-403 not taken (cites a plan found in no repo); `suite/058` parked to 2026-12-01 (announce first); `api/188` parked on the owner supplying the et54 load's input-off command. Owner questions: replay cost cap (W24), EMB-398 token scope, EMB-399/EMB-400 findings. Owed: `notes/goals/03-status.md` goal 3 still says topology alone opens a probe or port. Safe-off re-declare: `PUT /instruments` replaces by name. Dream ts `1795512985.272199` (previous dream ts `1795476373.403649`, 10 h and 133 commits earlier).

**Splits this day (Linear to task file; commit, announcement ts):** EMB-278 to `promptu/021` (`bd163fc8`, `1795503287.195659`); EMB-283/284 to `desk/043`+`ui/113` and `chat/035` (`248e2321`, `1795505033.011589`); EMB-318 to `doc/100`, EMB-297 to `api/186`+`core/149`+`umbrella/104` (`245c7cbf`, `1795515529.865329`); EMB-310/320/312 at `afe9024f` (`1795518116.601709`); EMB-321 to `topology/072`, EMB-299 to `umbrella/106`, EMB-386 to `ui/116`, EMB-357 (`f9bb180f`, `1795535418.541089`); EMB-401/400/399/389 (`3711fb0d`, `1795541360.131669`; the unit-`study-designer/091` split `2ff73f95` above is a separate commit); EMB-343 to `umbrella/108`, EMB-322 and others (`cd0b1fe8`); EMB-402/308/344 (`4a4a7f87`, `1795549699.487149`; `suite/060` window ts `1795543398.128079`, follow-up announcement `1795543453.347959`); `c06ce2be` as above. Owner's `ed5d290a` (the HIL guide's Live section) reached `origin/main` during `api/189`.

Spread sweep: nothing filed (2026-11-24 00:23)

### 2026-11-24 14:28 — doc/102 glossary-rows-for-the-guides-terms

Glossary Study row now names the host runner; eleven link-only rows point at the doc owning each guide term; studies-guide §1 points at the Study row. Worker had no write access to either file, so its quoted edit set was applied verbatim at fold. Gaps flagged, not filed: publish has no single owning decision; saved/live bench have no one-sentence definition (saved-benches.md has no `### 44` heading). Glossary is 1 B under its reserve line. `api/190` unparked to `open`.
**Merged:** `agent/doc/102-glossary-rows-for-the-guides-terms` (doc `991de560`, the worker's `325fcfef` cherry-picked onto `ff4913f6`; no code repo); the glossary and guide edits are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 14:25 — chat/037 atlas-citations-link-in-a-worktree-chat

`atlasRoot` walks up to the first `embarch/atlas`, and from a worktree falls back to the main clone's atlas via `gitdir:`/`commondir`; chat decision 16 amended. Split this leg: EMB-409 to this task, EMB-317 to `doc/102` + `api/190` (`c06ce2be`, ts `1795553476.798679`); EMB-317's Linear move hit the cap (next `ready` reads it as already split). EMB-403 not taken: it cites a build-step-5 plan (choices 1-22, units P5.x) found in no repo; owner's `f1208495` may carry it, unread. Three chat tests failed once under load in the worker's run and passed on rerun; nobody ran the `main` baseline.
**Merged:** `agent/chat/037-atlas-citations-link-in-a-worktree-chat` (code `695f46d`, ff from `23492eb`; doc `ff4913f6`, the worker's `af1dbb34` cherry-picked and rebased onto the owner's `45be94e0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:32 — ui/119 the-study-tab-uses-the-shared-tap-check

Study tab's no-subscriber tap refusal now comes from `Study::validate_stream_subscriptions()` via a scratch `Study` in `build_taps`; the refusal runs after the whole tap loop. gatt-capture decision 15 reworded. EMB-308 fully landed (`study-designer/093`, `core/152`, this) but stays in Fleet Working until a `finish` reaches Linear. Risk: the scratch `Study` literal breaks on the next field `Study` gains.
**Merged:** `agent/ui/119-the-study-tab-uses-the-shared-tap-check` (code `2213de6`, ff from `3974192`; doc `db2c1a56`, the worker's `b6e9366a` cherry-picked onto `69a7b6bf`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:31 — core/152 core-refuses-a-study-with-a-tap-no-step-subscribes-to

Core's `validate_study` refuses a GATT notify tap no step subscribes to, with the crate's text (core decision 90); `run_study` gets it through `POST /study`; interface row added. Fix at landing: comments cited the task number as 'study-designer decision 93', it is decision 55 (core `9154f7d`). **Leg start, to carry:** this leg waited 35 min for the leg lock because a second listener session was live (one spawning a leg at 12:42, the other at 12:44); the lock serialised them as designed, and the second listener keeps spawning a leg per leg death. Linear was rate limited all leg (2,500/hour cap; `ready`, `finish`, `queue-status.py` exit 2 at 13:20, 13:21, 13:30), so no Fleet Ready issue was split and EMB-308/EMB-402 stay in Fleet Working. Pump latched in burndown until 2026-11-25 06:00; leftover `agent/atlas/097-*` and `agent/ui/059-*` branches are known, not mine.
**Merged:** `agent/core/152-core-refuses-a-study-with-a-tap-no-step-subscribes-to` (code `0d1f027`, ff from `1b3562d`, plus my comment fix `9154f7d`; doc `69a7b6bf`, the worker's `af7098dc` cherry-picked onto `f2ccf405`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none beyond the standing native Windows build of `embarch-core`, which a worktree cannot run.

---

### 2026-11-24 13:19 — suite/060 the-one-owner-hardware-claim-says-what-core-and-topology-each-own

Supervisor's own unit, executed after the `protocol.md` §8 window (announced ts `1795543398.128079`, no reply). `embarch.md` §4 corrected: topology decides which device, Core opens every probe session and serial port, `embarch-smp` opens nothing; §4 gains the six runtime edges the sketch omitted; `embarch-smp` decision 2 amended; §3's smp row corrected. **Owed:** `notes/goals/03-status.md` goal 3 carries the same wrong claim and `fold-commit.py` refuses to stage it, so it still says topology is the only code opening a probe or port. Reviewer spot-checked, not re-audited, the nine port opens.
**Merged:** no branch (supervisor's own unit); the edits are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:13 — umbrella/109 a-script-cuts-a-signed-suite-release

`scripts/cut-release.py <suite-version> [--go] [--root DIR] [--dest DIR]` cuts a signed suite release (dry run by default; tags and pushes each changed component, watches `release.yml`, stops for the owner to commit `suite.toml`; second `--go` tags `suite-v<version>`, watches `assemble-suite.yml`, runs `embarch verify-release`). Never approves the `release` environment. My fix at landing: removed committed `__pycache__` and gitignored it (`ed5645b`). `gh` call shapes unverified until the first real cut; `--root` must name real checkouts from a worktree; tags go on HEAD unchecked. Umbrella `spec.md` at 9,272 B (968 B left). Linear rate limited again at the 13:14 `finish` (EMB-402 landed, still Fleet Working).
**Merged:** `agent/umbrella/109-a-script-cuts-a-signed-suite-release` (code `ed5645b`, the worker's `7bc6759` plus my fix, ff from `43ddda7`; doc `2448e2ca`, the worker's `03d1816a` cherry-picked onto `b67225a6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none, but the script has never met a real `gh` or `git` remote: `gh run list --workflow --branch <tag> --jq`, `gh run watch --exit-status` and `gh release download -D` are written from memory, and the first real cut (the rehearsal release) is where they get checked.

---

### 2026-11-24 13:12 — api/189 the-hil-guide-sends-the-dut-census-to-the-dev-bench-log

HIL guide's Study 1 bullet says to read the DUT census in `dev-bench.log` and that `fail_reason` is capped (measurement in `suite/studies-guide.md` §3a). Worker edited the api's pinned `guide/hil-guide.md`; I applied the same bytes to `suite/hil-guide.md` at fold and the drift guard passed against the leg worktree. A few minutes of drift-guard failure existed between the api push and this fold; any two-copy guide edit has it.
**Merged:** `agent/api/189-the-hil-guide-sends-the-dut-census-to-the-dev-bench-log` (code `7cbcd3d`, ff from `8786605`; doc `b67225a6`, the worker's `2e3762d5` cherry-picked onto `07b5294e`); the suite guide edit is in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 13:11 — study-designer/093 a-study-refuses-a-stream-tap-no-step-subscribes-to

`Study::validate_stream_subscriptions() -> Result<(), UnsubscribedTapError>` added (own error type, additive); decision 55 amended, decision 89 names the sibling. Only Core's `cargo check` was run against it; UI and api not.
**Merged:** `agent/study-designer/093-a-study-refuses-a-stream-tap-no-step-subscribes-to` (code `42a9d8a`, ff from `7ad0a02`; doc `07b5294e`, the worker's `af600edb` cherry-picked onto `c42cb4c1`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 11:18 — doc/101 one-study-walkthrough-and-the-guides-link-hil-guide

One study walkthrough lives in `suite/hil-guide.md`; `studies-guide.md` §1-§3b defer to it and keep this bench's measurements; `agent-guide.md` and `user-guide.md` §9 point at `embarch-api guide hil`. Installed `embarch-api` predates `guide hil` (needs a build after `api/163`), so the `hil-guide.md` link is the fallback.
**Merged:** `agent/doc/101-one-study-walkthrough-and-the-guides-link-hil-guide` (doc `0cfa89ff`, the worker's `4275bea0` cherry-picked onto `e9c29bc0`; no code repo); the guide edits themselves are in this fold commit.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 11:17 — umbrella/108 verify-release-checks-the-certificates-repository-and-ref

`embarch verify-release` requires the leaf certificate's Source Repository URI, Ref and Build Config URI to equal the umbrella repo, `refs/tags/suite-v<version>` and the identity (new `VerifyError::CertificateClaim`). **Risk to carry:** nothing has signed a suite release yet; if the release workflow's build config URI differs from the identity (a reusable workflow, say), every install refuses.
**Merged:** `agent/umbrella/108-verify-release-checks-the-certificates-repository-and-ref` (code `43ddda7`, ff from `6934dae`; doc `e9c29bc0`, the worker's `d45c0f95` cherry-picked onto `96ad575d`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. No signed suite manifest has been verified end to end yet; the check has met the uv and cosign fixtures only.

---

### 2026-11-24 11:16 — topology/073 the-cli-refuses-store-writes-while-a-core-service-is-registered

Topology CLI asks the OS whether a Core service is registered before any store write (`bin/registry.rs`, `ServiceRegistry` seam; `reg query` / `systemctl show` / `sc.exe qc`); enrol, unenrol, set-board, validate, set-dev-bench-link refused when registered, `list`/`alerts` point at Core's routes under `--service`. Decisions 23 and 28 amended. Fail-open: a registry read that errors restores local writes.
**Merged:** `agent/topology/073-the-cli-refuses-store-writes-while-a-core-service-is-registered` (code `81fb9ae`, ff from `77335f2`; doc `96ad575d`, the worker's `4297ff49` cherry-picked onto `df54c0af`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** a real registered Core service, stopped and running, on Windows and under WSL2, with a non-default `--bind`; `list` and `alerts` against a `--service` registration; the `ImagePath` and `sc.exe` parsing against real output (sample text only). The Windows build of the whole binary is the known `hidapi` debt; `registry.rs` alone type-checked for `x86_64-pc-windows-msvc` in a scratch crate.

---

### 2026-11-24 10:44 — core/151 the-spec-says-what-core-persists-of-what-it-flashed

Core spec's invariant now says Core keeps a persisted record of what it *flashed*, not of what the chip holds (`flashed-images.jsonl`, decision 93). Compaction paid in-unit: the signing/run-log/publish/restore/measurements text of §2 moved verbatim to new `spec/signing.md`, one pointer line keeps citations. Signing surface is still moving (EMB-254, EMB-265).
**Merged:** `agent/core/151-the-spec-says-what-core-persists-of-what-it-flashed` (code none; doc `d8532a55`, the worker's `583e018c` cherry-picked onto `8318fa47`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 10:42 — dev-bench/050 a-script-writes-the-released-bench-firmware-list

`scripts/bench-firmware-list.py [--version V] [--commit C] [--out FILE] [--study-designer DIR] <release> <app:board:path[@base]>...` writes `release/bench-firmware.json` (schema 1) using study-designer's `image_segments` example; four new tests. Never run on a real Zephyr image.
**Merged:** `agent/dev-bench/050-a-script-writes-the-released-bench-firmware-list` (code `f93cebf`, ff from `60ab42c`; doc `25655245`, the worker's `f30224d6` cherry-picked onto `9e14433b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the script reads image files only and was run on the shared crate's fixtures, never on a built bench image.

---

### 2026-11-24 10:41 — ui/118 make-live-skips-a-signal-whose-stored-safe-off-it-cannot-read

Make live skips (posts no row for, with a failed `POST /signals` row) a signal when `GET /signals` fails and the bench states no safe-off; decision 90 amended and trimmed back under 4 KB; my edits at fold: a typo in 90 and `spec/bench-live.md`'s Safe-off paragraph. Nothing re-declares such a signal by itself.
**Merged:** `agent/ui/118-make-live-skips-a-signal-whose-stored-safe-off-it-cannot-read` (code `3974192`, ff from `974813e`; doc `367e4f5c`, the worker's `0215ee98` cherry-picked onto `82dcfabe`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; tested against the stub Core only.

---

### 2026-11-24 10:38 — study-designer/092 the-image-segment-reader-checks-a-segments-end-address

`merge` in `hil_image.rs` checks every chunk end with `checked_add`; overflow is `ImageError::Overlap`. Reviewer note below its bar, not filed: `Overlap`'s Display says 'writes address twice' for an overflow.
**Merged:** `agent/study-designer/092-the-image-segment-reader-checks-a-segments-end-address` (code `7ad0a02`, ff from `11a98fa`; doc `55580c05`, ff from `8ff59eba`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 10:22 — ui/117 make-live-declares-an-outputs-safe-off

`Part.safe_off` and `[[signals]]` `safe_off` sent by Make live (and `embarch-ui bench make-live`); report rows say declared / none / kept from Core; Safe-off textarea in the part inspector (no browser drive exercised it). Re-declare rule kept: bench's safe-off wins; none stated means read `GET /instruments`/`/signals` and keep Core's; never clears. Decision 90 amended.
**Merged:** `agent/ui/117-make-live-declares-an-outputs-safe-off` (code `974813e`, ff from `1eee252`; doc `2b89bf6b`, the worker's `8cff84c7` cherry-picked onto `5ef957ec`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The new textarea was only `node --check`ed and `tests/browser` was not run (no browser in the worker's environment); the stub Core does not check bearer tokens, so the person-token path is the same client as before rather than a tested one.

---

### 2026-11-24 10:18 — api/187 the-instrument-and-signal-tools-carry-a-safe-off

`declare_instrument`/`declare_signal` take `safe_off`; CLI `--safe-off`, `--clear-safe-off`. Re-declare rule (decision 97 amended): omitted keeps the stored value, empty clears, failed read stops the declare. `api/188` (et54 preset safe-off) parked `blocked`: needs the load's input-off command from its programming manual, found in no doc repo; Blocked comment on EMB-334 asks the owner.
**Merged:** `agent/api/187-the-instrument-and-signal-tools-carry-a-safe-off` (code `f6907c1`, ff from `e34ec16`; doc `50a446ea`, the worker's `33c8224a` cherry-picked onto `a741bfbe`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; tested against the mock Core only, through the CLI path (the MCP tool entry shares its helpers).

---

### 2026-11-24 10:15 — core/150 core-records-what-it-flashed-with-its-segments-across-a-restart

Core's `ImageLog` backed by `flashed-images.jsonl`, read back at start; entries gain `identity`, `segments`, `scope`, `at_utc_ms`, `call_log_seq`; Core turns on study-designer's `hil-image` feature; `/status` `last_images` unchanged. No test drives the real `/flash`/`/bootload` handler (a handler forgetting to mark its `BoardNote` would pass). Reviewer finding EMB-400.
**Merged:** `agent/core/150-core-records-what-it-flashed-with-its-segments-across-a-restart` (code `1b3562d`, ff from `cadbdb1`; doc `bee96da1`, the worker's `2629a079` cherry-picked onto `c078af54`).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-400
**Hardware debts:** one real `/flash` and one real `/bootload` on the bench, then check `flashed-images.jsonl` has each line with `role` and a `call_log_seq` matching the call-log entry, and that it survives a Core restart; plus the native Windows build of `embarch-core`.

---

### 2026-11-24 10:09 — study-designer/091 the-image-segment-reader-refuses-a-malformed-elf-and-unknown-keys

ELF path checks every offset sum; overflow is `ImageError::Elf`; `Segment`, `BenchImage`, `BenchFirmwareList` refuse unknown keys. One sum left, `merge`'s address end: filed EMB-399, fixed by `study-designer/092`. **Leg start, to carry:** Fleet Ready held 27 unsplit issues; I split four at `2ff73f95` (EMB-397 here, EMB-361 to `core/150`, EMB-334 to `api/187`+`api/188`, EMB-337 to `ui/117`), ts `1795539178.532629`. Not taken: EMB-323, EMB-326, EMB-352 (each needs a new decision).
**Merged:** `agent/study-designer/091-the-image-segment-reader-refuses-a-malformed-elf-and-unknown-keys` (code `11a98fa`, ff from `74cb8dc`; doc `cfa2a28a`, ff from `37ef5968`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 09:44 — suite/059 land-the-safe-off-field-with-its-consumers

Cross-repo pass, announced (ts `1795536052.967279`, 09:00, no reply) and run at 09:32: `Instrument.safe_off` and `SignalLink.safe_off` in topology (line cap 4,096 B repeated from Core's `MAX_WRITE_BYTES`), decision 49 amended, consumer struct literals gain an empty `safe_off`, Core's `PUT /instruments` and `POST /signals` store it and 400 a bad line. Nothing sends a safe-off yet. **Carry:** `PUT /instruments` replaces by name, so a re-declare drops a safe-off unless the surface carries it; EMB-334 and EMB-337 have Finding comments saying so. Landed alone `topology/072` would have broken consumers, so it was parked `blocked` behind this and all four landed back to back.
**Merged:** `agent/topology/072-an-instrument-and-a-signal-declare-a-safe-off` (code `77335f2`, ff from `6a62335`; doc `a5171480`, the worker's `8efe2814` cherry-picked onto `cd2eda0c`, task-file conflict resolved to `done`); `agent/suite/059-land-the-safe-off-field-with-its-consumers` (core `cadbdb1` from `1f9a629`, api `e34ec16` from `d8de537`, ui `1eee252` from `f3f796d`; doc `0acd7123`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (test-only literal change, so a formality).

---

### 2026-11-24 09:10 — ui/116 a-saved-bench-is-made-live-from-the-terminal

`embarch-ui bench make-live <slug> [--config <name>] [--bind <role>=<serial>]...` runs `live::make_live` with the person's token; exits 1 on a failed row or a bind that applied nothing; retracts nothing. Decision 90 amended. Open question EMB-398: as shipped, any process that can run the UI binary acts as the person on Core.
**Merged:** `agent/ui/116-a-saved-bench-is-made-live-from-the-terminal` (code `f3f796d`, ff from `328790f`; doc `f5babce0`, the worker's `50077e0a` cherry-picked onto `1f675d46`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the command is verified against a stub Core only, as the feature row's `unit` says.

---

### 2026-11-24 09:08 — umbrella/106 status-and-doctor-json-carry-a-schema-version

`status --json` and `doctor --json` carry `schema_version` (`JSON_SCHEMA_VERSION = 1`, the umbrella's own counter); `status --json` gains `success` (always true). Decision 11 amended; bump rule is any shape change. A strict-parsing GUI consumer would break on the new keys; none found.
**Merged:** `agent/umbrella/106-status-and-doctor-json-carry-a-schema-version` (code `6934dae`, ff from `ea8fbf0`; doc `1f675d46`, the worker's `7f9e8b77` cherry-picked onto `cc9c72a5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 09:05 — study-designer/090 an-images-segments-and-identity-are-defined-once

Host-only `hil-image` feature: `image_segments(bytes, Hex|Elf|Bin, base)`, segment `{address, length, sha256}`, `identity` = SHA-256 of canonical JSON, `BenchFirmwareList`/`BenchImage` (schema 1); new `interfaces/hil-image.md`. Fixtures are an x86-64 ELF standing in for firmware; a real Zephyr ELF's `PT_LOAD` set may differ from its hex.
**Merged:** `agent/study-designer/090-an-images-segments-and-identity-are-defined-once` (code `74cb8dc`, ff from `1fe70b8`; doc `55738ecd`, the worker's `3d7ae275` cherry-picked onto `4e999d62`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 04:10 — umbrella/105 the-first-run-chip-hint-names-cores-chip-list

`embarch doctor`'s chip fix line and `embarch init`'s scaffold comment now say `embarch-core chip-list <soc-substring>`. Leg's last unit (cap 4). After it `queue-status.py` held no task-file work (`suite/058` parked to 2026-12-01). Linear's hourly cap: something spends ~2,500/hour incl. the fleet's own per-issue `ready` reads; the next leg may find Fleet Ready unreadable (THR-32).
**Merged:** `agent/umbrella/105-the-first-run-chip-hint-names-cores-chip-list` (code `ea8fbf0`, ff from `4cc725f`; doc `285eb0de`, the worker's `dec917ec` cherry-picked onto `0bd1987e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 04:10 — topology/071 the-linking-process-sets-the-identity-stores-folder

`paths::set_data_dir(dir)` (re-exported `hardware::set_data_dir`) lets the linking process set the identity store's folder once before first read; decision 23 amended. Core calling it is the HIL plan's attested-phase unit A.4. The setting test is safe only while no other lib test reads `data_dir()`. **Leg, to carry:** I split EMB-310 (`umbrella/105`), EMB-320 (this), EMB-312 (`suite/058`, **parked `blocked` until 2026-12-01**, the removal date of decisions 97/83; a cross-repo wire removal, so the leg that unparks it announces first) at `afe9024f`, ts `1795518116.601709`; only EMB-310 reached Fleet Working: `filed` for EMB-320 and EMB-312 hit Linear's cap, so the next `ready` reports them ALREADY SPLIT and must re-run `filed` for each. 25 Fleet Ready issues remain unsplit, ~20 more wait on blockers.
**Merged:** `agent/topology/071-the-linking-process-sets-the-identity-stores-folder` (code `6a62335`, ff from `ee45b6c`; doc `0bd1987e`, the worker's `3cb744cb` cherry-picked onto `5d3dfdf4`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:52 — umbrella/104 the-umbrella-readme-carries-no-counted-inventory

Umbrella README loses its command table and counted inventory; links interface docs and `embarch --help`. README now points at `interfaces/`, which holds only `doctor-chain.md` and `verify-release.md` (the command surface lives in `spec.md`); one-line fix not filed.
**Merged:** `agent/umbrella/104-the-umbrella-readme-carries-no-counted-inventory` (code `4cc725f`, ff from `b2579bf`; doc `751ee6c4`, the worker's `b067f49d` cherry-picked onto `fb6efd41`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:52 — core/149 the-core-readme-carries-no-counted-inventory

Core README loses endpoint counts, source layout, endpoint table and dev-bench detection prose; links Core's interface docs.
**Merged:** `agent/core/149-the-core-readme-carries-no-counted-inventory` (code `1f9a629`, ff from `5255f67`; doc `fb6efd41`, the worker's `4190d0cf` cherry-picked onto `da42c84b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (README-only change, so a formality).

---

### 2026-11-24 03:42 — doc/100 studies-guide-leads-with-the-signals-own-baud

Studies guide leads with the signal's own baud; `EMBARCH_SIGNAL_BAUD` is only the fallback for a signal that declares none (default 1000000).
**Merged:** `agent/doc/100-studies-guide-leads-with-the-signals-own-baud` (doc `e8eb2358`, the worker's `4d81b548` cherry-picked; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:41 — ui/115 four-routes-nothing-calls-are-deleted

Four routes nothing calls deleted (`POST /api/topology/roles/{role}/board`, `POST /api/topology/link`, `POST /api/topology/profiles/{slug}/apply`, `GET /api/study-designer/gatt/{study_id}`) with their handlers; decisions 90 and 94 amended. An out-of-repo caller now gets 404.
**Merged:** `agent/ui/115-four-routes-nothing-calls-are-deleted` (code `328790f`, ff from `df42a52`; doc `08dfde1b`, the worker's `f7404c09` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:39 — umbrella/103 the-installed-hil-skill-cannot-drift-from-the-apis

`embarch init` now `include_str!`s the api's `skills/embarch-hil/SKILL.md` through the sibling checkout instead of a pinned copy (decision 59 amended); a missing sibling is a compile error. A worktree build embeds the api main checkout's working tree, so an uncommitted edit there is compiled in.
**Merged:** `agent/umbrella/103-the-installed-hil-skill-cannot-drift-from-the-apis` (code `b2579bf`, ff from `27f43a5`; doc `754b8acc`, the worker's `a6eac931` cherry-picked).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 03:37 — api/186 the-api-readme-carries-no-counted-inventory

Api README no longer counts or lists tools or endpoints; getting-started follows `suite/user-guide.md`. Not run-true (the `embarch` binary was not run). **Leg start, to carry:** burndown leg re-armed by the owner at 03:05 (weekly 56%); leftover `agent/atlas/097-*` and `agent/ui/059-*` remote branches are not landed work.
**Merged:** `agent/api/186-the-api-readme-carries-no-counted-inventory` (code `d8de537`, ff from `abbd3cf`; doc `6c6db754`, the worker's `aed774c8` cherry-picked onto `270062bb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:36 — chat/036 the-promptu-card-test-waits-for-the-state-it-asserts

The promptu card test waits (5 s bound) for the `state` event after the one it asserts. **This leg ended burndown and dreamed:** EMB-294 was the only dispatchable work; sweep read the `chat`, `desk`, `promptu`, `ui` open questions the 00:23 spread sweep had skipped, nothing filed; `fleet-burndown.py --clear --reason 'queue empty'` at 02:36, pump stays latched in normal mode. Dream posted ts `1795512985.272199`: (1) `last_session` writes a Handoff desk line (EMB-189's second half); (2) the desk answers 200 to a mark without an item; (3) old `/api/topology/profiles/{slug}` routes refuse a non-slug with 400. Burndown ended with 44% of the week unspent and 27 h to reset; re-arm with `/fleet start burndown` if wanted.
**Merged:** `agent/chat/036-the-promptu-card-test-waits-for-the-state-it-asserts` (code `23492eb`, ff from `497cbba`; doc `599ad4a9`, the worker's `0f013ce6` cherry-picked onto `95b8eef5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:16 — promptu/020 a-pattern-line-is-replayed-on-past-prompts

Decision 47 amended: `week draft` replays up to 5 past rough prompts per changed pattern line (question/new_question/picker targets) with old and new frontmatter, side by side under `week/<week>/replay/`, listed in `check.replay`. A CLI that reports no cost counts as $0, so the dollar cap never stops a replay; W24's call-count cap is the alternative, **owner to pick before the timer runs unattended**.
**Merged:** `agent/promptu/020-a-pattern-line-is-replayed-on-past-prompts` (code `dcb6588`, ff from `eb1c674`, two commits `2d6fae4` and `dcb6588`; doc `c6d9434c`, the worker's `c0fdb90a` cherry-picked onto `7b29fc41`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fake `claude` answers every call alike, so no test has seen old and new disagree: one `week draft` on a real week with a question-changing line should write replay files whose two sides differ.

---

### 2026-11-24 02:15 — chat/035 a-click-on-the-promptu-cards-weekly-line-runs-or-opens

Decision 95 amended: a click on the Promptu card's weekly line opens an untracked chat with `/embarch-promptu:review` typed unsent, or runs `promptu week run --json` once in the background when no sheet waits (nothing starts while a run is going, `week status` says `running`, or exit 4). 30-minute run limit vs the contract's 60-minute drafter cap: a heavy week may show as failed while running.
**Merged:** `agent/chat/035-a-click-on-the-promptu-cards-weekly-line-runs-or-opens` (code `497cbba`, ff from `36b5c41`; doc `7b29fc41`, the worker's `dcc76c8e` cherry-picked onto `3cfb639c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Run only against a fake `promptu` and headless Firefox: in a real VS Code window with `promptu` installed, a click with no sheet should start one `week run`, and with a sheet waiting should open a chat with `/embarch-promptu:review` typed.

---

### 2026-11-24 02:08 — ui/114 compact-ui

Compaction, no code: `embarch-ui/decisions/shell.md` 11,553 to 8,931 B (decisions 58-59 moved verbatim to `decisions/page-links.md`), `spec/tabs.md` 9,079 to 8,165 B (tab folders to `spec/tab-folders.md`). Worker's open question, shared: can `spec.md` alone answer what someone needs to work on the UI. Repointed link in `decisions/tab-folders.md` still reads `../spec/tabs.md` as text.
**Merged:** `agent/ui/114-compact-ui` (code: no commits, embarch-ui `main` stays `df42a52`; doc `96bc184d`, the worker's `03649426` cherry-picked onto `5d1ed1a7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

---

### 2026-11-24 02:08 — promptu/021 the-weekly-sheet-opens-with-decision-15s-numbers

Decision 15 amended: all five checks on the sheet in fixed order; the two friction checks carry `control` (sessions with `promptu: false`); no data is `value: null`, contract §10 now says so; `sheet.md` opens with a read-only numbers block and the feel line. Targets are still text; nothing marks a miss.
**Merged:** `agent/promptu/021-the-weekly-sheet-opens-with-decision-15s-numbers` (code `eb1c674`, ff from `d4cdb6a`; doc `5d1ed1a7`, the worker's `87632ea6` cherry-picked onto `5d877f98`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run on a real week's pack: the five checks are tested on fixtures only; `promptu week draft` on a real week should show all five, with a control figure if any session ran without Promptu.

---

### 2026-11-24 01:56 — promptu/023 a-terminal-skill-walks-the-weekly-sheet

**Recovery fold:** the leg that merged this, `desk/043` and `ui/113` died on a 5-hour 429 at ~00:45 with its fold half done and uncommitted; I checked the half-fold against the merged commits, re-gated `main` and committed it here. Plugin skill `/embarch-promptu:review` (`disable-model-invocation: true`) walks `week show --json` in `AskUserQuestion` pages. Nothing the dead leg wrote says it gated before merging.
**Merged:** `agent/promptu/023-a-terminal-skill-walks-the-weekly-sheet` (code `d4cdb6a`, ff from `43f195a`; doc `4cd54137`), both merged by the dead leg.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill has not been typed in a real Claude Code session against a real sheet; `/embarch-promptu:review` on a machine with the plugin at 0.4.0 and a drafted week is owed.

---

### 2026-11-24 00:36 — desk/043 the-desk-sets-the-weekly-sheets-feel-line

Desk decision 65 amended: fifth Promptu route `POST /promptu/feel/{week}` (`better|same|worse`) runs `promptu week mark --feel`; no MCP tool reaches it (`no_tool_reaches_the_promptu_routes` guards). Settled/superseded sheet is a 400 the tab can tell apart only by message text.
**Merged:** `agent/desk/043-the-desk-sets-the-weekly-sheets-feel-line` (code `99ffa07`, ff from `921f0ee`; doc `ba634c47`, the worker's `42dd21f8` cherry-picked onto `c5034930`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Tested only against a fake `promptu`; on a desk with `promptu` installed and a sheet waiting, `POST /promptu/feel/<week>` with `{"feel":"same"}` should set the sheet's `feel` and show it in `week show`.

---

### 2026-11-24 00:35 — ui/113 the-desk-tab-draws-the-weekly-promptu-sheet

UI decision 56 amended: Desk tab's Promptu bar ('Promptu · <week> · n waiting', hidden at `open: 0`) opens a panel from `GET /promptu/sheet` (numbers, group ✕, line ✓/✕ with notes, feel line, Apply). No Rust changed (generic desk proxy). Group ✕ posts a group id through the line route; not tested end to end.
**Merged:** `agent/ui/113-the-desk-tab-draws-the-weekly-promptu-sheet` (code `df42a52`, ff from `b1b1a24`; doc `1d05bc8b`, the worker's `c97666f2` cherry-picked onto `ba634c47`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against a real desk or a real `promptu`: the drive serves its own stand-in desk. On a desk with `promptu` installed and a sheet waiting, open the Desk tab, mark a line, set the feel line and apply.

---

### 2026-11-24 00:19 — desk/042 the-desk-serves-promptus-weekly-sheet

Desk decision 65 amended: four Promptu routes behind the desk token (`GET /promptu` cached 60 s, `GET /promptu/sheet`, `POST /promptu/sheet/{week}/{line}`, `POST /promptu/apply/{week}`), each runs one `promptu` command. A timing flake `claude_agents_is_dated_by_when_it_was_asked_not_when_it_answered` failed once in four full runs; not filed.
**Merged:** `agent/desk/042-the-desk-serves-promptus-weekly-sheet` (code `921f0ee`, ff from `d0c0233`; doc `5fda0d30`, the worker's `a17f226b` cherry-picked onto `f21146a2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against the real `promptu` CLI: the tests use a fake on a scratch `PATH`. On a desk with `promptu` installed, `GET /promptu/sheet` and a mark round trip are owed.

---

### 2026-11-24 00:18 — promptu/018 week-run-packs-and-drafts-one-run-at-a-time

Decisions 14 and 45 amended: `promptu week run` packs and drafts under `week/run.lock`; a second run exits 4 (contract §14); stale lock = dead pid or over 2 h; `run.json` always settled; `week timer`. The 2 h stale age is a guess at the longest real pass.
**Merged:** `agent/promptu/018-week-run-packs-and-drafts-one-run-at-a-time` (code `43f195a`, ff from `f9c43d0`; doc `f21146a2`, the worker's `103334e8` cherry-picked onto `04ee3aa9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run under a real systemd user manager: enable the printed units once and confirm `Persistent=true` catch-up and the `ExecStart` quoting (in `open.md`). Without `/proc` only the 2-hour age frees a dead run's lock.

---

### 2026-11-24 00:06 — promptu/019 week-mark-and-apply-turn-approved-lines-into-changes

Decisions 30 and 43 amended: `promptu week mark` (verdicts, notes, `--feel`; refuses unknown id, bad verdict, applied line, settled or superseded sheet) and `week apply` (memory lines via the hook's topic/index checks with a backup; pattern lines committed on `promptu/week-<week>`). 'Settled' means every line applied, so a sheet of only cut lines can still be re-marked.
**Merged:** `agent/promptu/019-week-mark-and-apply-turn-approved-lines-into-changes` (code `f9c43d0`, ff from `beecb5c`; doc `d4d7fc82`, the worker's `e4040860` cherry-picked onto `1b0b3d65`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not yet run against real data: a real memory folder, a real pattern checkout or real drafter output.

---

### 2026-11-24 00:06 — api/184 live-log-states-zone-sent-form-and-added-fields

No code: `embarch-api/interfaces/live-log.md` states the file-name time (lease `started_at` as Core wrote it), `sent`'s object-or-string split by `writer`, additive fields without a `schema` bump, and `core_calls` on a failed call. Nothing confirms Core always stamps UTC.
**Merged:** `agent/api/184-live-log-states-zone-sent-form-and-added-fields` (code: no commits, embarch-api `main` stays `abbd3cf`; doc `1b0b3d65`, the worker's `d3e5faf3` cherry-picked onto `f409bc58`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new. The live log on a real bench stays as `embarch-api/open.md` says: run `mem_read` and `reset` with a lease held and read `embarch/live/`.
## 2026-11-23 — 46 units

*Folded by the leg of 2026-11-24 per protocol §11 (embarch-log-folder): the per-unit narrative reasoning, gate transcripts and "Least sure about" prose went, and git holds them; every SHA, Reviewer line, board-naming debt and the spread-sweep line is kept as written. Detail for any unit is in the commit named under it.*

**Carry forward (open at the end of the day):**
- **Decisions made on the owner's behalf, all under the delegation, none new-numbered in burndown:** `doc/099` moved ten board-reaching `embarch-api` tools from ask to allow in `suite/agent-guide.md` §1.1 (58 tools, 37 allow, 21 ask; resting on the lease gating them and on Core refusing them during a run, `core/143`). `core/148` and `api/185` landed together as one cross-repo shape, `observed.call_log {head, first_seq, last_seq, count}` in `report-data.json`; either half alone fails verify check 6. Accepted cost in decision 124: a zip published by a Core built between `core/145` and `core/148` fails check 6 for the missing field, so redeploy Core before publishing.
- **Blocked on the owner:** `atlas/097` (EMB-248, the prior-art source's robots-file question) with `atlas/098` and `atlas/099` behind it; the owner has since marked all three Owner required. Branch `agent/atlas/097-prior-art-search-returns-a-hit-table` is kept in the `embarch-doc` main checkout, task `blocked`.
- **Open and dispatchable at day end, two scopes only (the refill gate fires for spread):** `api/184` (EMB-290), `promptu/018` (EMB-277), `promptu/019` (EMB-279), `promptu/020` (EMB-281). EMB-278 is splittable once EMB-274 is Done; EMB-284 waits on EMB-277, EMB-280 and EMB-282 on EMB-279, EMB-283 on EMB-282. The promptu tasks all add `week` subcommands in `src/main.rs`, one per wave.
- **Filed:** EMB-292 (fleet, owner's lane: `build_features.py` has no `promptu` or `atlas` section, so those workers have no feature row they may write; `features.d/chat-036-promptu-week-pack-sessions.md` was adopted by hand); EMB-293 closed in `core/148`'s fold. `atlas/107` (compact `embarch-atlas/design.md`, 23,474 of 25,600 B) is `blocked`, due 2026-12-07. EMB-286 (promptu gate fails with a crowded `/tmp`) was fixed by `promptu/012`.
- **Bench and Windows:** `api/059` and `dev-bench/038` stay open, no board; burndown skipped them. Native Windows build of `embarch-core` is owed for `core/139` to `core/148` (a worktree cannot build natively), and the deployed Core needs a redeploy to carry `core/139` to `core/148`.
- **Recurring failure:** a leg died on a 5-hour 429 mid-fold (after `core/143`, about 20:50) leaving a doc half merged and unpushed for about ten minutes; `promptu/011`'s leg recovered it. Burndown runs until 2026-11-25 06:00 (stops at 97%). A fold-trailer wart: `core/141`'s fold commit `c4a8592d` carries `Log: embarch-fleet@bb4a01b`, a commit that is on no remote; after a forced rebase, add a second log commit, never amend.
- **Announcements:** last leg's wave went out with the 23:45 announcement ts `1795501351.430619`; earlier ones `1795482132.287899`, `1795473685.846769`, `1795466178.988799`, `1795464400.823999`.

Spread sweep: nothing filed (2026-11-23 18:00)

**Other SHAs and timestamps the day named** (split, claim and fold commits of the legs, and Slack announcement/dream ts values; a revert handle only): 09b3ddf8 1c25ce9 1f743ba7 29f15e09 4509d241 49c5d3b4 54812073 572bca3 636db678 8088d6e0 8ee6c6bb 91e0286e ab50139f b5c7ff65 d0c0233c1198 d9c2f60c dce9b7b e5d025c2 f79c167 f99f6816 fafa3f2c fddca96d ffee53fe; ts 1795463694 1795470987 1795471472 1795476373 1795478837 1795494535 1795496707.

---

### 2026-11-23 23:47 — api/185 check-6-and-the-appendix-read-the-call-log-claim
**Merged:** `agent/api/185-check-6-and-the-appendix-read-the-call-log-claim` (code `abbd3cf`, ff from `c2b619a`; doc `51e679bf`, the worker's `893eff1f` cherry-picked onto `2f624847`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. With `core/148` deployed, `embarch-api verify` on a fresh publish should pass check 6 with the call-log field and the appendix should print it; a zip from a Core between `core/145` and `core/148` should fail check 6 naming `observed.call_log`.

### 2026-11-23 23:46 — core/148 report-data-carries-the-call-log-claim
**Merged:** `agent/core/148-report-data-carries-the-call-log-claim` (code `5255f67`, ff from `7165e51`; doc `37db70fd`, the worker's `67f1cbda` cherry-picked onto `51e679bf`, plus my three-line fix in this fold).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-293
**Hardware debts:** none on a board. The native Windows build of embarch-core at `5255f67` is owed (the owner runs it). On the deployed Core once it carries `core/148`, publish one run and run `embarch-api verify` on the zip: check 6 should pass with `observed.call_log` present, and the appendix should print the head, range and count.

### 2026-11-23 23:46 — atlas/106 a-measured-fact-shows-beside-its-datasheet-claim
**Merged:** `agent/atlas/106-a-measured-fact-shows-beside-its-datasheet-claim` (code `74048d8`, ff from `b7f894a`; doc `337544ac`, the worker's `fd14ebb9` cherry-picked onto `37db70fd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, write one real measurement back with `live write-back` against a register whose datasheet reset value is known, then run `register` on it and the mismatch report: the value should show beside the claim, and a disagreement should appear as `measured-vs-datasheet`. Tests use fixtures and a fake `embarch-api`.

### 2026-11-23 23:45 — promptu/016 week-pack-carries-friction-unmatched-starts-and-outcomes
**Merged:** `agent/promptu/016-week-pack-carries-friction-unmatched-starts-and-outcomes` (code `beecb5c`, ff from `ac36f2d`; doc `e0139deb`, the worker's `b3ae36dd` cherry-picked onto `337544ac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:16 — promptu/017 week-draft-turns-the-pack-into-a-sheet
**Merged:** `agent/promptu/017-week-draft-turns-the-pack-into-a-sheet` (code `ac36f2d`, ff from `d0431fe`; doc `d3a1d70c`, the worker's `3fa228a5` cherry-picked onto `4d376762`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:15 — chat/034 promptu-card-shows-the-weekly-pass
**Merged:** `agent/chat/034-promptu-card-shows-the-weekly-pass` (code `36b5c41`, ff from `8101942`; doc `4d376762`, the worker's `56da0bb2` cherry-picked onto `6e5703e4`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 23:14 — atlas/105 a-live-finding-is-written-back-as-a-measured-fact
**Merged:** `agent/atlas/105-a-live-finding-is-written-back-as-a-measured-fact` (code `b7f894a`, ff from `4403850`; doc `6e5703e4`, the worker's `90cda886` cherry-picked onto `61d7c7c3`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read`, then `live write-back --seq <its entry>`: the record's receipt should match `embarch-api call-log --seq N --json` for that entry and name the image "read back" or "as last flashed by Core". The worker read the `call_log.entries` shape from embarch-core and embarch-api source on `origin/main`; tests use a fake `embarch-api`.

### 2026-11-23 23:13 — api/183 verify-checks-the-call-log-segment
**Merged:** `agent/api/183-verify-checks-the-call-log-segment` (code `c2b619a`, ff from `421d01c`; doc `61d7c7c3`, the worker's `b48457a9` cherry-picked onto `d93f9484`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. On the deployed Core, publish one run sealed after `core/145` and run `embarch-api verify` on its zip: check 8 should list the call-log range it compared.

### 2026-11-23 22:34 — atlas/104 live-log-lines-agree-with-embarch-api
**Merged:** `agent/atlas/104-live-log-lines-agree-with-embarch-api` (code `4403850`, ff from `e461ddd`; doc `3d8ce989`, the worker's `84c3e4f2` cherry-picked onto `4003b6ec`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read` against a board Core has flashed. Its decoded line should name the same `image_sha256` and `board` as embarch-api's raw line for that call. Then stop Core and check that an atlas live call writes no decoded line.

### 2026-11-23 22:33 — chat/033 permissions-command-drops-instrument-exchange
**Merged:** `agent/chat/033-permissions-command-drops-instrument-exchange` (code `8101942`, ff from `22717b0`; doc `4003b6ec`, the worker's `51150f81` cherry-picked onto `9ea1c31c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 22:32 — promptu/012 folder-name-decode-survives-a-crowded-temp-folder
**Merged:** `agent/promptu/012-folder-name-decode-survives-a-crowded-temp-folder` (code `d0431fe`, ff from `28eab3a`; doc `9ea1c31c`, the worker's `85b1e26b` cherry-picked onto `fe32fb59`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 22:31 — api/182 restore-skips-the-call-log-segment
**Merged:** `agent/api/182-restore-skips-the-call-log-segment` (code `421d01c`, the worker's `7d32fa4` plus my `421d01c`, ff from `f2912db`; doc `fe32fb59`, the worker's `cecbd75d` cherry-picked as `15114739` onto `48bfda50`, plus my `fe32fb59`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on the deployed Core, swept-then-republish a run whose earlier zip carries `call-log-segment.jsonl`: no PUT for the segment, and the republish succeeds. Also publish one run sealed before `core/145` and check it succeeds with no segment.

### 2026-11-23 21:57 — doc/099 agent-guide-permission-lists-match-the-live-design
**Merged:** `agent/doc/099-agent-guide-permission-lists-match-the-live-design` (doc `bcaff6c6`, the worker's `464ebcee` cherry-picked onto `ac147543`; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:55 — atlas/103 live-tools-append-a-decoded-line-to-the-live-log
**Merged:** `agent/atlas/103-live-tools-append-a-decoded-line-to-the-live-log` (code `e461ddd`, ff from `2adf1cc`; doc `ac147543`, the worker's `523f2ef4` cherry-picked onto `fee73fe8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run one atlas `reg_read` and one `shell`, then read `embarch/live/`. The atlas's decoded lines should follow embarch-api's raw lines in the same file and name the same Core entries.

### 2026-11-23 21:54 — promptu/014 week-status-show-and-desk-report-the-weekly-pass
**Merged:** `agent/promptu/014-week-status-show-and-desk-report-the-weekly-pass` (code `28eab3a`, ff from `761eb83`; doc `fee73fe8`, the worker's `1ee67f10` cherry-picked onto `810a14b2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:53 — api/179 an-idle-released-lease-refuses-the-next-hardware-call
**Merged:** `agent/api/179-an-idle-released-lease-refuses-the-next-hardware-call` (code `f2912db`, ff from `c7efaef`; doc `810a14b2`, ff from `ee8747ae`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on the deployed Core, hold a lease, leave it 30 minutes with no hardware call, then run `mem_read` and `lease_show`. The `mem_read` should refuse with Core's reason, without reaching Core, and `lease_show` should report no token (recorded in `open/bench-verification.md`).

### 2026-11-23 21:22 — promptu/013 week-pack-writes-per-run-events
**Merged:** `agent/promptu/013-week-pack-writes-per-run-events` (code `761eb83`, ff from `cb9d928`; doc `89f04e05`, the worker's `30a571d5` rebased onto `1a7059fd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 21:21 — core/145 a-runs-signed-record-names-its-call-log-range
**Merged:** `agent/core/145-a-runs-signed-record-names-its-call-log-range` (code `7165e51`, ff from `f1bcefc`; doc `4d655e9a`, the worker's `cbeff2eb` rebased onto `2d3af3f8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a real bench study's published zip carrying `call-log-segment.jsonl`, whose entries recompute to the recorded head and still pass `embarch-api verify`.

### 2026-11-23 21:19 — api/180 each-hardware-call-appends-a-live-log-line
**Merged:** `agent/api/180-each-hardware-call-appends-a-live-log-line` (code `c7efaef`, ff from `acde856`; doc `cc67c0c6`, ff from `7cbf31d7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a bench with a lease held, run `mem_read` and `reset`, then read `embarch/live/`. Check that Core's real `X-Embarch-Call-*` headers appear as `seq` and `hash`, that `last_images` gives a real board's image hash, and that a real MCP client's working folder picks the right repo (written into `embarch-api/open.md`).

### 2026-11-23 20:57 — promptu/011 weekly-pass-contract
**Merged:** `agent/promptu/011-weekly-pass-contract` (code `cb9d928`, ff from `ea5c032`; doc `cf5847e1`, ff from `38682ca9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 18:26 — core/143 core-refuses-lease-gated-calls-during-a-run
**Merged:** `agent/core/143-core-refuses-lease-gated-calls-during-a-run` (code `f1bcefc`, ff from `6766785`; doc `ca46bec6`, the worker's commit rebased onto `73ee90ab`).
**Blocked:** nothing.
**Reviewer:** skipped (budget HOLD, 5-hour 98% against burndown's 97% cap).
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a live bench or host study refusing a `mem_read` and a `reset` from the lease holder, and admitting the study's cancel.

### 2026-11-23 18:25 — api/178 instrument-exchange-tool-and-verb-are-gone
**Merged:** `agent/api/178-instrument-exchange-tool-and-verb-are-gone` (code `acde856`, ff from `f28cc3d`; doc `ce097c63`, ff from `39f485cb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 17:42 — core/142 instrument-exchange-refuses-outside-a-run
**Merged:** `agent/core/142-instrument-exchange-refuses-outside-a-run` (code `6766785`, ff from `415cdf3`; doc `30bb99a3`, ff from `db0c7947`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; on the deployed Core, a host study with an `Instrument` step still drives the supply while the bare route refuses.

### 2026-11-23 17:28 — core/141 core-releases-a-lease-idle-for-30-minutes
**Merged:** `agent/core/141-core-releases-a-lease-idle-for-30-minutes` (code `415cdf3`, ff from `5fe3e8a`; doc `d894af6f`, the worker's `507991cb` rebased onto the owner's `160a52f2`, which landed during the fold; fold `c4a8592d`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`; a live MCP-held lease left idle for 30 minutes on the deployed Core, to see `embarch-api`'s renew meet the `404` (EMB-256 changes what it does then).

### 2026-11-23 17:20 — atlas/102 design-head-says-what-the-doc-is-today
**Merged:** `agent/atlas/102-design-head-says-what-the-doc-is-today` (code none, the branch had no commits; doc `e58223de`, the worker's `9151c4e7` rebased onto `82b24e12`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 17:18 — core/140 core-keeps-a-hash-chained-call-log
**Merged:** `agent/core/140-core-keeps-a-hash-chained-call-log` (code `5fe3e8a`, ff from `73c51a7`; doc `8b74a0b3`, ff from `6699c5ee`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (not runnable from a worktree), and a first real call log: a live Core session's flash, reset and mem-read entries, with `board` and its image hash. `board` is named only by `/flash`, `/reset`, `/live/mem-read` and `/live/core-state`; null elsewhere (in `open.md`).

### 2026-11-23 16:26 — api/177 study-measurements-reads-a-finished-run-before-publish
**Merged:** `agent/api/177-study-measurements-reads-a-finished-run-before-publish` (code `f28cc3d`, ff from `f30570f`; doc `2c1e505d`, the worker's `4f476a87` rebased onto the owner's `2da83766`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Run both tools against a live Core once the Windows service carries `core/139` (`73c51a7`): **until then the deployed Core has no such route, its unknown-route 404 reads as `no-such-run`**, which is a wrong name for "this Core is too old".

### 2026-11-23 16:11 — core/139 core-serves-a-finished-runs-measurements-before-publish
**Merged:** `agent/core/139-core-serves-a-finished-runs-measurements-before-publish` (code `73c51a7`, ff from `6116b1e`; doc `83991fd7`, the worker's `f8f5e2db` cherry-picked onto `7c37f1fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core` (`cargo.exe build` from the main checkout), not runnable from a worktree. The route has not met a live Core: read a real finished run's `measurements.json` through it once the Windows service is redeployed. The 410 path has no test.

### 2026-11-23 16:09 — api/176 core-key-prints-cores-public-key
**Merged:** `agent/api/176-core-key-prints-cores-public-key` (code `f30570f`, ff from `f56b423`; doc `1da37390`, the worker's `bb4b3145` rebased onto the owner's `a691d693`, which landed during the fold; fold `7c37f1fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** `core-key` has not met a live Core: the mock cannot sign a fresh nonce, so the success path is unit-tested only. Run it against the running Core and pass its key to `verify` on a published zip.

### 2026-11-23 15:04 — atlas/101 design-records-the-mcp-server-as-atlas-transport
**Merged:** `agent/atlas/101-design-records-the-mcp-server-as-atlas-transport` (code none, the branch had no commits; doc `4edf440a`, ff from `ad6638c9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 14:55 — atlas/097 prior-art-search-returns-a-hit-table
**Merged:** none (blocked before any merge).
**Blocked:** `agent/atlas/097-prior-art-search-returns-a-hit-table` — the robots-file question above; task `blocked` on EMB-248, worktrees removed, branches kept. `atlas/098` and `atlas/099` stay blocked behind it.
**Reviewer:** skipped (not landed: blocked on EMB-248 before any merge).
**Hardware debts:** none.

### 2026-11-23 14:44 — atlas/096 translation-fills-a-module-pads-port
**Merged:** `agent/atlas/096-translation-fills-a-module-pads-port` (code `2adf1cc`, ff from `dae31d4`; doc `6d42f66b`, the worker's `348abdc2` cherry-picked onto `6a5a36bc`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Translate one real module datasheet with the skill and confirm `port` on its pad records (an engineer-supplied datasheet, no board); none sits in either repo.

### 2026-11-23 14:04 — atlas/095 atlas-live-tools-work-under-the-sessions-own-lease
**Merged:** `agent/atlas/095-atlas-live-tools-work-under-the-sessions-own-lease` (code `dae31d4`, ff from `64d2c5b`; doc `910c80c9`, ff from `b185dcac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** with the lease taken through the embarch-api MCP, atlas `shell` `device list` in the same session with `lease_token` set should return the device list, not a 409; and Core's real 409 text for a wrong or missing token should still match `409|lease`. Needs a live Core and a board (recorded in the task's Outcome, now retired).

### 2026-11-23 13:57 — atlas/094 a-modules-pad-table-gives-unnamed-pads-their-port
**Merged:** `agent/atlas/094-a-modules-pad-table-gives-unnamed-pads-their-port` (code `64d2c5b`, ff from `902f144`; doc `8f75e182`, ff from `a56d71f1`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The pad-table source has met one synthetic module fixture; no real module datasheet has been translated with `port`.

### 2026-11-23 13:52 — atlas/093 shell-commands-help-text-and-kernel-subcommands
**Merged:** `agent/atlas/093-shell-commands-help-text-and-kernel-subcommands` (code `902f144`, ff from `893275d`; doc `ec22da7f`, the worker's `e800a878` cherry-picked onto `74e0cfb2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Both layouts have met only synthetic ELFs built from the 4.4 headers; `shell_commands command=kernel` and `command=i2c` on a real 4.4 image would confirm it, including the help struct's alignment on a 64-bit target.

### 2026-11-23 13:50 — api/175 build-verdict-reports-the-application-image-on-sysbuild
**Merged:** `agent/api/175-build-verdict-reports-the-application-image-on-sysbuild` (code `e68ce94`, ff from `de53e6e`; doc `ffe77a59`, ff from `9a539ba9`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The first-table rule has met one synthetic two-table log shaped like the issue's; no real sysbuild build log has been parsed.

### 2026-11-23 13:30 — atlas/092 pin-table-fills-port-and-dt-use-for-every-module-pin
**Merged:** `agent/atlas/092-pin-table-fills-port-and-dt-use-for-every-module-pin` (code `893275d`, ff from `0180a9f`; doc `8d6a4755`, ff from `d8052972`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The net-name fallback has met one generic module fixture; the real-board read was the worker's diagnosis, not a test.

### 2026-11-23 13:21 — desk/041 missing-embarch-api-line-names-every-missing-piece
**Merged:** `agent/desk/041-missing-embarch-api-line-names-every-missing-piece` (code `08214ff`, ff from `25b6877`; doc `28142601`, the worker's `64e84faf` cherry-picked onto `e06d6845`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 13:20 — api/174 zephyr-west-scan-takes-cpu-clusters-from-the-soc
**Merged:** `agent/api/174-zephyr-west-scan-takes-cpu-clusters-from-the-soc` (code `de53e6e`, ff from `97d58d8`; doc `5a56344c`, the worker's `3adab50a` cherry-picked onto `919e5327`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The scan has met only a fixture `soc.yml` shaped like Zephyr's `soc/nordic` file, never a real Zephyr tree or the project that filed the issue; that project still runs `discovery = "static"` until someone switches it back.

### 2026-11-23 13:18 — atlas/091 net-trace-uses-the-fitted-packages-pin-map
**Merged:** `agent/atlas/091-net-trace-uses-the-fitted-packages-pin-map` (code `0180a9f`, ff from `d80aa9f`; doc `b86eb5cc`, ff from `e01c28fb`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fitted-package inference has met only a generic two-package fixture, never a real board's atlas.

### 2026-11-23 12:55 — api/173 compact-api
**Merged:** `agent/api/173-compact-api` (doc only, no code branch; doc `7602bb15`, the worker's `66187c6e` cherry-picked onto `bf446f98`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 12:51 — core/138 open-md-still-owes-verify-check-8
**Merged:** `agent/core/138-open-md-still-owes-verify-check-8` (doc only, no code branch; doc `f3bf0c1d`, the worker's `c187939b` cherry-picked onto `4397f813`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 2026-11-23 12:51 — api/172 republish-a-swept-run-from-the-earlier-zip
**Merged:** `agent/api/172-republish-a-swept-run-from-the-earlier-zip` (code `97d58d8`, ff from `2804e41`; doc `4397f813`, ff from `f31b1850`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The restore path has met a mock Core only: Core's real `409` body and `restore` answers are unseen, and no real swept run has been republished. `restore_file`'s timeout is assumed.

### 2026-11-23 11:57 — core/137 a-republish-after-the-retention-sweep-takes-the-earlier-zips-files
**Merged:** `agent/core/137-a-republish-after-the-retention-sweep-takes-the-earlier-zips-files` (code `606b267` and `6116b1e`, ff from `88aff23`; doc `84ff218a`, worker's `f68ff56a` cherry-picked onto `574e6411`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`, unrun (a worktree cannot build natively). The restore route has met only Core's in-process HTTP tests; no real retention sweep has run on the Windows service, and embarch-api does not send the files until `api/172`.

### 2026-11-23 11:50 — study-designer/089 the-footer-band-is-measured-on-a-typst-page
**Merged:** `agent/study-designer/089-the-footer-band-is-measured-on-a-typst-page` (doc only, no code branch; doc `cf5145d5` and `f7b6260f`, the worker's `8543c1a3` and `7341d8a0` cherry-picked onto `c1d2b942`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The band rests on one font set on one machine, A4 only; a Letter page and a font outside the embedded set are unmeasured.

### 2026-11-23 11:49 — promptu/008 compact-promptu
**Merged:** `agent/promptu/008-compact-promptu` (doc only, no code branch; doc `044c117c`, fast-forward from `60e002f0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
*Days 2026-11-22 to 2026-11-22 rolled to [log-archive/supervisor-log-2026-11-22-to-2026-11-22.md](log-archive/supervisor-log-2026-11-22-to-2026-11-22.md).*
