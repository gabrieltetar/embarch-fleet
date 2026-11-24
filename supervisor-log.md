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

## 2026-11-24 03:41 — ui/115 four-routes-nothing-calls-are-deleted

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-ui` loses four routes no page and no sibling repo calls: `POST /api/topology/roles/{role}/board`, `POST /api/topology/link`, `POST /api/topology/profiles/{slug}/apply` and `GET /api/study-designer/gatt/{study_id}`, with their handlers and the code only they used (`SetRoleBoardRequest`, `pin_combination`, `LinkRequest`, `RoleProposal.displaces`). `apply_role`, `apply_link` and `resolve_chip_or_refuse` stay. The apply-route test became `enrol_finds_the_chip_it_looked_up_and_refuses_a_board_nothing_answers_for`, keeping its `/api/enroll` assertions. Decisions 90 and 94 amended in place (`bench-live.md`, `bench-canvas.md`), pointers fixed in `saved-benches.md` and `board-row.md`, three rows dropped from `interfaces/topology.md`; no decision retired, so no reversal row. **The worker's call, which I keep:** the `open/bench.md` slugify bullet was narrowed, not closed, because the profile delete route stays and still slugifies its path. That also narrows the 02:36 dream's third proposal to the delete route. The caller search was by literal route path; the reviewer re-grepped and found none. Reviewer's side note, not filed: `decisions/topology-boards.md` line 53 still describes the old picker writing a board pin, which `pin_combination` implemented.
**Merged:** `agent/ui/115-four-routes-nothing-calls-are-deleted` (code `328790f`, ff from `df42a52`; doc `08dfde1b`, the worker's `f7404c09` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test` (320 passed, 4 ignored), `clippy --all-targets -D warnings` green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. `build_changelog.py` rolled `history/ui.md`'s September window into `history/archive/`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 63%, weekly 57%, wave 6).
**Least sure about:** a caller outside the suite's repos (a script on the owner's machine) would now get a 404; the audit and the worker could only search what is checked in.

---

## 2026-11-24 03:39 — umbrella/103 the-installed-hil-skill-cannot-drift-from-the-apis

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decision 59 (`embarch-umbrella/decisions/integration.md`) amended in place: `embarch init` no longer installs a pinned copy of the `embarch-hil` skill; `src/init.rs` now `include_str!`s `../../embarch-api/skills/embarch-hil/SKILL.md` through the sibling checkout the crate already path-depends on, and `src/skills/embarch-hil/SKILL.md` is deleted. The worker checked every build that compiles umbrella has the sibling (local, `build-check.yml`, `release.yml`; `assemble-suite.yml` only downloads releases), so a missing sibling is a compile error rather than a stale skill. The recorded cost: an api skill edit reaches users with the next umbrella build. The drift test, renamed `the_installed_skill_is_what_embarch_api_ships`, still compares at run time. This takes the issue's "installer reads the one file" route, so no api-side drift check is owed and none was filed.
**Merged:** `agent/umbrella/103-the-installed-hil-skill-cannot-drift-from-the-apis` (code `b2579bf`, ff from `27f43a5`; doc `754b8acc`, the worker's `a6eac931` cherry-picked). Re-gated on the merge result: `cargo build`, `cargo test` (280 passed), `clippy --all-targets -D warnings` green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 63%, weekly 57%, wave 6).
**Least sure about:** a worktree build of umbrella now embeds whatever the sibling link points at, which is the api's main checkout and its working tree, not the api's `origin/main`, so an uncommitted edit there would be compiled in.

---

## 2026-11-24 03:37 — api/186 the-api-readme-carries-no-counted-inventory

**Decided:** nothing suite-wide, and **no new decision** (burndown leg, re-armed by the owner at 03:05, weekly 56%). `embarch-api/README.md` no longer counts or lists tools or Core endpoints; it links `embarch-api/interfaces/tools.md`, `interfaces/config.md` and Core's docs, and its getting-started follows `suite/user-guide.md` (release archive, `embarch setup`, `embarch init`, config found by the upward search, `--config` or `EMBARCH_API_CONFIG` outside a repo). `config.example.toml` stays as an annotated example. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker; leftover `agent/atlas/097-*` and `agent/ui/059-*` remote branches are not landed and not mine). Fleet Ready held 19 issues from the 2026-11-23 suite audit; I split four: EMB-311 to `ui/115`, EMB-315 to `umbrella/103`, EMB-318 to `doc/100`, EMB-297 to `api/186` plus `core/149` and `umbrella/104` (open), at `245c7cbf`; announced ts `1795515529.865329`. 15 issues remain in Fleet Ready, unsplit. The refill gate fired spread-only (5 scopes, wave 6); the only source changed since the 00:23 spread line was `promptu/021`'s `open.md` edit, which `chat/036`'s 02:36 sweep had read, so I skipped the sweep. Wave 1 was all four units, four foreground calls in one message, all reported to the leg. No day fold owed (2026-11-23 was folded at 00:10).
**Merged:** `agent/api/186-the-api-readme-carries-no-counted-inventory` (code `d8de537`, ff from `abbd3cf`; doc `6c6db754`, the worker's `aed774c8` cherry-picked onto `270062bb`). Re-gated on the merge result: `cargo build`, `cargo test`, `clippy --all-targets -D warnings` green; `check-docs.py` 12/12 after all four doc merges; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start (BURNDOWN, 5-hour 59%, weekly 56%, wave 6); PROCEED at dispatch (5-hour 63%, weekly 57%), four dispatched against the unit cap.
**Least sure about:** the worker checked the README's setup steps against the guide and the CLI flags but never ran the `embarch` binary, so the getting-started is read-true, not run-true.

---

## 2026-11-24 02:36 — chat/036 the-promptu-card-test-waits-for-the-state-it-asserts

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). **This leg ends the burndown and dreams.** Split EMB-294 (filed by `chat/035`'s worker) as this task; it was the only dispatchable work. The refill gate fired on depth (1 dispatchable, 1 scope, wave 6), so I swept: the only source changed since the 00:23 sweep was `promptu/021`'s one-line `open.md` status edit, and I read the `chat`, `desk`, `promptu` and `ui` open questions that the 00:23 spread sweep had passed over because those scopes held work then; every item is the owner's call, a live or hardware check, or waiting on a trigger that has not fired. Roadmap Next is hardware (`.eap` run) or deployed (`embarch-chat`); no reversal follow-up is open. Nothing filed. So after this unit `queue-status.py` reads 0 dispatchable (2 bench tasks, held in burndown), and I ran `fleet-burndown.py --clear --reason 'queue empty'` at 02:36: the pump stays latched in normal mode. **Dream posted, ts 1795512985.272199**, `--dream-check` said ASK (the previous dream, ts 1795476373.403649, was 10 h and 133 commits old): (1) `last_session` writes a Handoff desk line (`embarch-chat/open.md`, EMB-189's second half); (2) the desk answers 200 to a mark without an item (`embarch-desk/open.md`); (3) the old `/api/topology/profiles/{slug}` routes refuse a non-slug path with 400 (`embarch-ui/open/bench.md`). All three `Hardware: none`, one unit each. What the unit did: the card test "the card: on by default…" in `test/promptu.test.mjs` took the first `state` event, but the patterns load and the week-status load run side by side and each emits one; it now waits (5 s bound) for the `state` event after which `patterns` is non-empty. The worker judged event order not part of the service's contract (decision 96 promises none, the reviewer confirmed), so `src/promptu/` and `spec.md` are unchanged. Before: 4 failures in 20 runs; after: 0 in 20 (worker), and 10 of 10 in my own runs on the merge result.
**Merged:** `agent/chat/036-the-promptu-card-test-waits-for-the-state-it-asserts` (code `23492eb`, ff from `497cbba`; doc `599ad4a9`, the worker's `0f013ce6` cherry-picked onto `95b8eef5`). Re-gated on the merge result: `npm ci`, `npm run build` and `npm run typecheck` ok; `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (desk built from `99ffa07`) 395 tests, 392 passed, 0 failed, 3 skipped for outside binaries; `npm run test:webview` all passed; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at leg start and dispatch (BURNDOWN, 5-hour 25%, weekly 53%, wave 6); PROCEED at this fold (5-hour 28%, weekly 53%), then burndown cleared on the empty queue.
**Least sure about:** ending burndown with 44% of the week unspent and 27 h to the reset; the rule says an empty queue ends it, so a dream answered in the morning runs under normal caps unless the owner re-arms with `/fleet start burndown`.

---

## 2026-11-24 02:16 — promptu/020 a-pattern-line-is-replayed-on-past-prompts

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decision 47 (`decisions/learning.md`) amended in place. New `src/replay.rs`: for a pattern line whose target is a `question`, `new_question` or `picker` and whose proposed frontmatter differs from the old, `week draft` runs the pass on up to 5 past rough prompts of that pattern (the log's `original` only, via `state::all_logs()`, with no other source), once with the old set and once with the new, on the `pass_*` model settings. Each pair is written side by side to `week/<week>/replay/<pattern>/<run>.md`, listed in `check.replay`, and linked from the line by a `- replay:` sub-line in `sheet.md`. A template-only or body-only change, a new pattern, one with no past prompts, or one that failed lint gets no replay, and `check.replay_note` says why. New setting `week_replay_cap_usd`, default 1.00, checked before each pair, so the pair that crosses it finishes; a stopped line says "stopped by the replay cap … after N of M prompts"; 0 turns the replay off. `parse_md` in `src/weekapply.rs` now skips a `- replay:` sub-line as it skips `- proposed:`, so it is never read as the owner's note. **The worker's calls, which I keep:** fork W7 marked built on (b), the model replay; W23 (a), the newest five distinct originals of that pattern in `prompt` mode; W24 (a), a dollar cap of 1.00 counted from the cost the CLI reports, the drafter's own call not counted. Status edit went to `spec/status.md`, as dispatched. No feature row (EMB-292). **End of this leg's units:** promptu step 4's host-side units are all landed (`019`, `018`, `023`, `021`, `020`), and `promptu/022` closed in `021`'s fold.
**Merged:** `agent/promptu/020-a-pattern-line-is-replayed-on-past-prompts` (code `dcb6588`, ff from `eb1c674`, two commits `2d6fae4` and `dcb6588`; doc `c6d9434c`, the worker's `c0fdb90a` cherry-picked onto `7b29fc41`). Re-gated on the merge result: `cargo build` ok, `cargo test --all-targets --no-fail-fast` 191 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fake `claude` answers every call alike, so no test has seen old and new disagree: one `week draft` on a real week with a question-changing line should write replay files whose two sides differ.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 9%, weekly 51%, wave 6); PROCEED at this fold (5-hour 13%, weekly 52%).
**Least sure about:** a CLI that reports no cost counts as $0, so the dollar cap would never stop a replay; W24 names a call-count cap as the alternative, and the owner should pick before the timer runs this unattended.

---

## 2026-11-24 02:15 — chat/035 a-click-on-the-promptu-cards-weekly-line-runs-or-opens

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decision 95 (`decisions/promptu.md`) amended in place: the click is described and dropped from **Rejected**; "a key for the pass" stays rejected. With a sheet waiting, a click opens a new untracked chat with `/embarch-promptu:review` typed, unsent (the name read from `embarch-promptu`'s contract on `origin/main`, exported as `REVIEW_SKILL` in `src/promptu/text.ts`), and runs nothing. With none, it runs `promptu week run --json` once in the background: nothing starts while this window's run is going, while `week status` says `running` (the timer's run), or when `week run` exits 4, which reads as busy, not failure. A failed run is one `warn` line under the weekly line. The page posts only `{t:"promptuWeek", op}` and the host decides from its own state, so the page names no command. **The worker's calls, which I keep:** the spec text went to `embarch-chat/spec/input.md`, since `spec.md` is an index 36 B under reserve; the open action starts an untracked chat, as the memory pass does (decision 98). **Worth the owner's eye:** `TIMEOUTS.weekRun` is 30 minutes while the contract caps the drafter at 60, so a long pass would be cut off by the chat; the decision states the 30. Feature row `chat-035` assembled. **Filed:** EMB-294 (Fleet Ready), the card test "the card: on by default…" in `test/promptu.test.mjs`, which the worker saw fail 2 of 3 runs on unchanged `main`; my gate run passed it.
**Merged:** `agent/chat/035-a-click-on-the-promptu-cards-weekly-line-runs-or-opens` (code `497cbba`, ff from `36b5c41`; doc `7b29fc41`, the worker's `dcc76c8e` cherry-picked onto `3cfb639c`). Re-gated on the merge result: `npm ci`, `npm run build` and `npm run typecheck` ok; `npm test` with `EMBARCH_DESK_BIN` from `desk-gate-bin.py` (desk built from `99ffa07`) 395 tests, 392 passed, 0 failed, 3 skipped for outside binaries; `npm run test:webview` all passed; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. My first `npm test` named `desk-gate-bin.py` in the wrong repo and ran without the desk; I reran it with the right path and that run is the one above.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Run only against a fake `promptu` and headless Firefox: in a real VS Code window with `promptu` installed, a click with no sheet should start one `week run`, and with a sheet waiting should open a chat with `/embarch-promptu:review` typed.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 5%, weekly 51%, wave 6); PROCEED at this fold (5-hour 13%, weekly 52%).
**Least sure about:** the 30-minute run limit against the contract's 60-minute drafter cap; a heavy week's pass may be reported as failed by the chat while it is still running.

---

## 2026-11-24 02:08 — ui/114 compact-ui

**Decided:** nothing, and no decision added or renumbered (burndown leg). A compaction, per file as the task's `In flux:` said. `embarch-ui/decisions/shell.md` 11,553 to 8,931 B: decisions 58 and 59 moved verbatim to a new `decisions/page-links.md`, a pointer stub keeping both numbers, and the `decisions.md` index row added. `embarch-ui/spec/tabs.md` 9,079 to 8,165 B: the "Tab folders" section moved verbatim to a new `spec/tab-folders.md`, a heading and link left, the one link into it (`decisions/tab-folders.md`) repointed; the Desk row untouched, as dispatched. Everything on the Must-not-delete list stayed in place. **The human question, in the worker's words, which I share:** can `spec.md` alone answer what someone needs to work on the Desk tab today? No. It is a router: it points at `spec/tabs.md` for the Desk row, decisions 56 and 57 hold the reasons, and the detail lives in `embarch-desk`'s docs. That is the intended shape for a multi-file sub-project, not a gap this pass could close by moving text.
**Merged:** `agent/ui/114-compact-ui` (code: no commits, embarch-ui `main` stays `df42a52`; doc `96bc184d`, the worker's `03649426` cherry-picked onto `5d1ed1a7`). Re-gated: no code to build; `check-docs.py` 12/12; `check-doc-size.py --pressure` lists neither file; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 5%, weekly 51%, wave 6); PROCEED at this fold (5-hour 9%, weekly 51%).
**Least sure about:** the repointed link in `decisions/tab-folders.md` still reads `../spec/tabs.md` as its text while pointing at `spec/tab-folders.md` (the reviewer's note); it resolves, but a reader sees the old file name.

---

## 2026-11-24 02:08 — promptu/021 the-weekly-sheet-opens-with-decision-15s-numbers

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decision 15 (`decisions/learning.md`) amended in place: all five checks are on the sheet, in a fixed order (`friction_per_prompt`, `redirects_per_task`, `fills_kept`, `patterns_kept`, `questions_per_run`). The two friction checks carry a new `control` field, the same figure over the week's sessions with `promptu: false` (null when there are none). A check with no data is `value: null`, never zero or left out, and contract §10 now says so (it said "left out"). `sheet.md` opens with a read-only numbers block and the feel line, nulls shown as "no data"; `week apply` still parses only `- [x] lN` lines. **The worker's call, which I keep:** fork W22 (a), counting every redirect candidate because the drafter records no per-candidate judgement; (b), a keep or drop per candidate, is the alternative. **Paid in the unit, per my dispatch note:** `embarch-promptu/spec.md` out of reserve (9,147 to 7,710 B), its status paragraph moved verbatim to `embarch-promptu/spec/status.md` with four relative links adjusted for the new folder; I closed `promptu/022` `done` in this fold. No feature row (EMB-292).
**Merged:** `agent/promptu/021-the-weekly-sheet-opens-with-decision-15s-numbers` (code `eb1c674`, ff from `d4cdb6a`; doc `5d1ed1a7`, the worker's `87632ea6` cherry-picked onto `5d877f98`). Re-gated on the merge result: `cargo build` ok, `cargo test --all-targets --no-fail-fast` 185 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run on a real week's pack: the five checks are tested on fixtures only; `promptu week draft` on a real week should show all five, with a control figure if any session ran without Promptu.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 5%, weekly 51%, wave 6); PROCEED at this fold (5-hour 9%, weekly 51%).
**Least sure about:** the targets (0.10, "down about 30%") are still text on each number, so the sheet shows a value beside its target but nothing marks a miss.

---

## 2026-11-24 01:56 — promptu/023 a-terminal-skill-walks-the-weekly-sheet

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). **This fold is a recovery:** the leg that merged this unit (with `desk/043` and `ui/113`) died on a 5-hour 429 at about 00:45 with the fold half done and uncommitted in its leg worktree (changelog consumed into `history/promptu.md`, `promptu/022` edited, no log entry). I checked the half-fold against the merged commits, re-gated `main`, and committed it here; the reviewer had already written its verdict file at 00:34. What the unit did: a plugin skill `plugin/skills/review/SKILL.md`, typed **`/embarch-promptu:review`** (Claude Code names a plugin skill `<plugin>:<skill>`), `disable-model-invocation: true`, walks `week show --json` in `AskUserQuestion` pages of at most four lines, records each answer with `week mark`, asks the feel line, then applies after a confirmation; its `allowed-tools` are the `promptu week` commands only, plugin 0.4.0, README says how to review without the Desk. Decision 30 (`decisions/learning.md`) amended in place with the real name, contract and `interfaces.md` follow. **The worker's call, which I keep:** fork W21 (a); the free-text answer is a note on a kept line, never a cut. **The dead leg's edit I keep:** `promptu/022`'s `In flux:` and `Unparks when:` now name only `promptu/020` and `021` (spec.md 9,147 B, 1,093 B left). This landing is what `chat/035` was held for: its click types this skill name. No feature row (EMB-292, owner's lane). **Leg start, to carry:** step 0 found the half-fold above, six clean unit worktrees whose branches had landed (`desk/043`, `ui/113`, `promptu/023`, removed), no claim, no stop marker, empty `status.d/`; pump latched in burndown until 2026-11-25 06:00. Fleet Ready empty; `finish` moved EMB-283 to Done. Refill gate fired spread-only (3 scopes, wave 6) and no source changed since the 00:23 sweep line, so I skipped the sweep.
**Merged:** `agent/promptu/023-a-terminal-skill-walks-the-weekly-sheet` (code `d4cdb6a`, ff from `43f195a`; doc `4cd54137`), both merged by the dead leg. Re-gated by me on `main` at `d4cdb6a` in a scratch worktree: `cargo build` ok, `cargo test --all-targets --no-fail-fast` 183 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12 on the fold; ownership green on both commits' paths; client names clean on the code tree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill has not been typed in a real Claude Code session against a real sheet; `/embarch-promptu:review` on a machine with the plugin at 0.4.0 and a drafted week is owed.
**Budget:** PROCEED at this leg's start (BURNDOWN, 5-hour 5%, weekly 51%, wave 6) after the 429 pause reset at 01:50.
**Least sure about:** that the dead leg gated this unit before merging it; nothing it wrote says so, which is why I re-ran the gate on `main` rather than trusting the merge.

---

## 2026-11-24 00:36 — desk/043 the-desk-sets-the-weekly-sheets-feel-line

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Desk decision 65 (`decisions/cockpit.md`) is amended in place with a fifth Promptu route, `POST /promptu/feel/{week}` with `{"feel": "better" | "same" | "worse"}`, which runs `promptu week mark --feel <feel> --week <week> --json` and passes its JSON on: the same week check, the same status mapping as the mark route (no binary a 503 naming it, Promptu's exit 2 a 400 in its words, anything else a 502), and it clears the `GET /promptu` cache. Any other `feel`, an empty one or a flag-like week is a 400 before the binary runs. **No MCP tool reaches it**; `no_tool_reaches_the_promptu_routes` (`src/mcp.rs`) still guards it. `interfaces.md`'s `/promptu` row names it (still out of reserve). **I set the path and body myself** when I split EMB-283 (see `ui/113`'s entry), so the tab and the desk agreed before either was built; the router took them as written. **No feature row**, the worker's call, which I kept: the route only serves the section `desk-042`'s and `ui-136`'s rows already describe. `spec.md` and `tasks/desk/038` are untouched (`spec.md` still 9,186 B, due 2026-12-01).
**Merged:** `agent/desk/043-the-desk-sets-the-weekly-sheets-feel-line` (code `99ffa07`, ff from `921f0ee`; doc `ba634c47`, the worker's `42dd21f8` cherry-picked onto `c5034930`). Re-gated on the merge result: `cargo build` ok, `cargo test --no-fail-fast` 308 passed 0 failed (last leg's `claude_agents_is_dated_by_when_it_was_asked_not_when_it_answered` flake did not fire), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Tested only against a fake `promptu`; on a desk with `promptu` installed and a sheet waiting, `POST /promptu/feel/<week>` with `{"feel":"same"}` should set the sheet's `feel` and show it in `week show`.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 90%, weekly 49%, wave 6); PROCEED at this fold (5-hour 96%, weekly 50%).
**Least sure about:** the route answers a 400 for a sheet Promptu calls settled or superseded, as the mark route does, but the tab has no way to tell that apart from a bad request except by Promptu's message text.

---

## 2026-11-24 00:35 — ui/113 the-desk-tab-draws-the-weekly-promptu-sheet

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). UI decision 56 (`decisions/shell.md`) is amended in place: the Desk tab's empty Promptu spot is now a bar ("Promptu · <week> · n waiting", hidden and taking no space while `GET /promptu` says `open: 0`) opening a panel drawn from `GET /promptu/sheet` — decision 15's numbers first, read-only, a `null` shown as "no data"; each group with ✕ and its count; each line with ✓/✕ and a note sent with its mark; the better · same · worse line; Apply ✓ (n), with a failed line staying open with its `error`. A 400 shows Promptu's words and a 503 names the missing binary. No Rust changed: the generic `/api/desk/{*rest}` proxy carries every route, so the UI holds no Promptu logic (desk decision 65). **My split of EMB-283, which the owner may want to know:** the issue asked the tab to set the feel line, and the desk had no route for it (`week mark --feel` takes no line id), so I split it into `desk/043` (the route) and this task, with the route's path and body fixed in both task files so the two ran in one wave against a stub. **The worker's call, which I kept:** Apply's count leaves out `external` and `no-change` lines, since Promptu applies neither. **New debt, filed by the worker:** `tasks/ui/114-compact-ui.md`, `open`, due 2026-12-08: `decisions/shell.md` 11,553 of 12,288 B and `spec/tabs.md` 9,079 of 10,240 B; `In flux: per file` (shell.md no, tabs.md yes in its Desk row). Feature row `ui-136` assembled. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no unfolded `status.d`; pump latched in burndown until 2026-11-25 06:00). Fleet Ready held EMB-283 and EMB-284: split as `desk/043` + `ui/113` and `chat/035` (`248e2321`), announced ts `1795505033.011589`. `chat/035` is held for a second wave because its click types the review skill's name, which `promptu/023` fixed in this wave as `/embarch-promptu:review`. The refill gate fired spread-only (4 scopes, wave 6); the sources changed since the 23:52 line were `promptu/018`'s and `promptu/019`'s one-line `open.md` status edits (promptu scope only, no spread) and `api/184`'s verbatim `open.md` move. Spread sweep: nothing filed (2026-11-24 00:23). Wave 1 was `promptu/023`, `desk/043` and `ui/113`, three foreground calls in one message, all reported to the leg. **Reviewers ran foreground**, three in one message after the merges, rather than in the background: each reported to the leg in under 30 s and the verdict files agreed.
**Merged:** `agent/ui/113-the-desk-tab-draws-the-weekly-promptu-sheet` (code `df42a52`, ff from `b1b1a24`; doc `1d05bc8b`, the worker's `c97666f2` cherry-picked onto `ba634c47`). Re-gated on the merge result: `cargo build` ok, `cargo test --no-fail-fast` 328 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12 after all three doc cherry-picks; ownership green on both branches; client names clean on the code worktree. The worker's headless-Firefox drive `tests/browser/drive_desk_promptu.py` passed 18 checks; I did not re-run it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against a real desk or a real `promptu`: the drive serves its own stand-in desk. On a desk with `promptu` installed and a sheet waiting, open the Desk tab, mark a line, set the feel line and apply.
**Budget:** PROCEED at leg start (BURNDOWN, 5-hour 88%, weekly 49%, wave 6); PROCEED at dispatch (5-hour 90%); PROCEED at this fold (5-hour 96%, weekly 50%).
**Least sure about:** the group ✕ posts a group id (`g1`) through the per-line mark route; the contract says `week mark` takes a group id and the desk's id check accepts it, but no test runs that path end to end through the desk.

---

## 2026-11-24 00:19 — desk/042 the-desk-serves-promptus-weekly-sheet

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Desk decision 65 (`decisions/cockpit.md`) is amended in place to record four routes behind the desk bearer token, each running one `promptu` command and passing its JSON on, so the desk holds no Promptu logic: `GET /promptu` (`promptu desk --json`, cached 60 s, `{"promptu":1,"open":0}` when the binary is missing or fails), `GET /promptu/sheet` (`week show --json`, optional `?week=`), `POST /promptu/sheet/{week}/{line}` with `{verdict, note?}` (`week mark`), and `POST /promptu/apply/{week}` (`week apply`, a failed line still a 200 with its JSON). The week must match `YYYY-Www` and a line id is alphanumeric, so neither reads as a flag; mark and apply clear the cache. **The worker's status mapping, which I kept:** no binary is a 503 naming it, Promptu's exit 2 a 400 in Promptu's words, anything else a 502; the issue did not fix these, so EMB-283 (the tab, `embarch-ui`) should read the `error` text. **No MCP tool reaches the routes**, and a test in `src/mcp.rs` asserts it; the reviewer confirmed decision 67's "never cached" still holds, since only the command's output is cached and the binary is found on every call. **Paid in the unit, per my dispatch note:** `embarch-desk/interfaces.md` out of reserve (14,073 to 12,723 B, two route rows moved verbatim to `interfaces/draft-note-routes.md`); I struck it off `desk/038`'s `Compacts:` line in this fold, which stays `blocked` on `spec.md` alone (9,186 B, due 2026-12-01). Feature row `desk-042` assembled. **Newly splittable once `finish` moves EMB-282 to Done:** EMB-283 (the Desk tab's Promptu section, `embarch-ui`).
**Merged:** `agent/desk/042-the-desk-serves-promptus-weekly-sheet` (code `921f0ee`, ff from `d0c0233`; doc `5fda0d30`, the worker's `a17f226b` cherry-picked onto `f21146a2`). Re-gated on the merge result: `cargo build` ok, `cargo test --no-fail-fast` 307 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12 on both merged doc branches; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Nothing has run against the real `promptu` CLI: the tests use a fake on a scratch `PATH`. On a desk with `promptu` installed, `GET /promptu/sheet` and a mark round trip are owed.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 84%, weekly 48%, wave 6); PROCEED at this fold (BURNDOWN, 5-hour 86%, weekly 49%).
**Least sure about:** the worker saw `claude_agents_is_dated_by_when_it_was_asked_not_when_it_answered` (`src/server.rs`, not this unit's code) fail once in four full runs; my gate run passed, so it is a timing flake that nobody has filed yet.

---

## 2026-11-24 00:18 — promptu/018 week-run-packs-and-drafts-one-run-at-a-time

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decisions 14 and 45 (`decisions/learning.md`) are amended in place. `promptu week run [--week] [--scheduled] [--json]` packs then drafts under `week/run.lock` (`{pid, week, started}`, created exclusively): a second run while one is live exits **4** (new in contract §14) and writes nothing; a lock whose pid is gone or that is over 2 hours old is taken over and the dead run's `run.json` settled `failed` with `interrupted`. `run.json` is written `running` first and always settled `ok` or `failed`, a failed pack included, and now carries `kind` (`scheduled` or `manual`), `scheduled_for` and `cost_usd`, which `week status` shows. `promptu week timer [--enabled] [--json]` prints a `Type=oneshot` service (`ExecStart=<binary> week run --scheduled`) and a timer (`OnCalendar` from `week_schedule`, `Persistent=true`) and installs nothing. New `src/weekrun.rs`, 9 tests in `tests/weekrun.rs`. **The worker's calls, which I kept:** a pid-and-age lock file over `flock` (fork W19); and, because the timer now installs nothing, `--enabled` writes `week/timer.json` so `status` can say "missed" without asking systemd (fork W20; decision 45's rejection of asking the scheduler stands, the reviewer checked). It also fixed the three stale lines `promptu/019`'s reviewer found (contract "one commit per pattern", the `sheet_md` comment, fork W5). **Feature row owed** (EMB-292). **My edits in this fold:** `promptu/022`'s `Unparks when:` named `week timer` being built, which this unit did, but step 4 is still moving, so I kept it `blocked` and rewrote its `Unparks when:` and `In flux:` to name `promptu/020`, `021` and `023`; `embarch-promptu/spec.md` is 9,090 B, still in reserve. **Correction to `api/184`'s entry:** its spread sweep ran at about 23:52, not at the fold's 00:10, so the newest marker is Spread sweep: nothing filed (2026-11-23 23:52).
**Merged:** `agent/promptu/018-week-run-packs-and-drafts-one-run-at-a-time` (code `43f195a`, ff from `f9c43d0`; doc `f21146a2`, the worker's `103334e8` cherry-picked onto `04ee3aa9`). Re-gated on the merge result: `cargo build` ok, `cargo test --all-targets --no-fail-fast` 183 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12 on both merged doc branches; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Never run under a real systemd user manager: enable the printed units once and confirm `Persistent=true` catch-up and the `ExecStart` quoting (in `open.md`). Without `/proc` only the 2-hour age frees a dead run's lock.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 84%, weekly 48%, wave 6); PROCEED at this fold (BURNDOWN, 5-hour 86%, weekly 49%).
**Least sure about:** the 2-hour stale age is a guess at the longest real pass; a pack and draft of a heavy week that runs longer would be taken over while still alive.

---

## 2026-11-24 00:06 — promptu/019 week-mark-and-apply-turn-approved-lines-into-changes

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). Decisions 30 and 43 (`decisions/learning.md`) are amended in place. `promptu week mark` records a line's or group's verdict, a line's note and the week's `--feel`, and refuses (exit 2) an unknown id, a bad verdict, an applied line, a settled sheet (every line applied) or a superseded one. `sheet.md` is now read back by `mark` and `apply`: an unticked box cuts an open or failed line, indented text is its note, and a `[x]` never re-approves a line the JSON cut. `promptu week apply` writes a memory line only through the hook's topic and index checks, after a backup under `week/<week>/backup/`; commits pattern lines on `promptu/week-<week>` in the configured checkout (version bumped, lint, golden renders, the public-safety command run without a shell), never pushes, refuses a dirty checkout, and restores the owner's branch; with no checkout it writes `patterns.patch`. A second apply changes nothing; `--dry-run` writes nothing. New `src/weekapply.rs`, 12 tests on scratch folders and a scratch git checkout. **The worker's two calls, which I kept:** one commit per pattern carrying all its approved lines rather than one per line, because a pattern file is whole (fork W17, decision 43 amended); and an `external` line is never applied by `mark` (fork W18, where contract §10 and §14.4 disagreed). W4 and W5 are marked built on their defaults. **New debt:** `embarch-promptu/spec.md` is in reserve (9,074 of 10,240 B), filed as `tasks/promptu/022-compact-promptu.md`, `blocked`, `In flux: yes`, due 2026-12-07. **Feature row owed:** I told the worker not to write a `features.d` fragment, since `build_features.py` has no promptu section (EMB-292, owner's lane). **Reviewer's leftovers, not findings:** `docs/contract.md` (about line 704) still says "one commit per line", and the "read-only view" wording survives in the comment above `sheet_md` in `src/draft.rs` and in fork W5's option text; I am handing them to the next promptu worker.
**Merged:** `agent/promptu/019-week-mark-and-apply-turn-approved-lines-into-changes` (code `f9c43d0`, ff from `beecb5c`; doc `d4d7fc82`, the worker's `e4040860` cherry-picked onto `1b0b3d65`). Re-gated on the merge result: `cargo build` ok, `cargo test --all-targets --no-fail-fast` 173 passed 0 failed, `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12 on both merged doc branches; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not yet run against real data: a real memory folder, a real pattern checkout or real drafter output.
**Budget:** PROCEED at dispatch (BURNDOWN, 5-hour 77%, weekly 48%, wave 6); PROCEED at this fold (BURNDOWN, 5-hour 83%, weekly 48%).
**Least sure about:** "settled" is read as every line applied, so a sheet of only cut or no-change lines can still be re-marked; if the owner means a sheet nothing more can change, `mark` should refuse it too.

---

## 2026-11-24 00:06 — api/184 live-log-states-zone-sent-form-and-added-fields

**Decided:** nothing suite-wide, and **no new decision** (burndown leg). `embarch-api/interfaces/live-log.md` now states four things the atlas had to guess as the live log's second writer, each checked against the code: the file name's date and `HHMMSS` are the lease's `started_at` text as Core wrote it, unconverted, and a `no-lease` file uses UTC now; `sent` is the Rust debug form of the parsed subcommand from embarch-api and a command line from the atlas, so a reader relies on the object-or-string split and branches on `writer`; a writer may add fields with no `schema` bump, records them in its own docs, and the atlas's `outcome` (five values) is named; `--json` carries `core_calls` on a failed call that reached a gated route. No code changed: doc and code already agreed. **My dispatch note, paid in this unit:** `api/181`'s unpark condition was met (the atlas's live-log writers landed in `atlas/103` to `atlas/106`), so I told this worker to bring `embarch-api/open.md` out of reserve: two bullets (`publish`, `artifact_path_for_core`) moved verbatim to `open/unmeasured-details.md`, 4,204 to 3,873 B, and I closed `api/181` `done` in this fold. **Leg start, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no unfolded `status.d`; pump latched in burndown until 2026-11-25 06:00). Leftover remote branches `agent/atlas/097-*` (doc and atlas) and `agent/ui/059-*` (doc) are not landed and not mine to delete. Fleet Ready held one splittable issue: EMB-278 to `promptu/021` (`bd163fc8`), announced ts `1795503287.195659`. `ready` moved EMB-292 to Todo (Scope: fleet). The refill gate fired spread-only (2 scopes, wave 6); sources changed since the 18:00 line were Core's `open.md` compaction, the atlas's own `design.md` edits and two hardware-gated api items. Spread sweep: nothing filed (2026-11-24 00:10). Wave 1 was `api/184` and `promptu/019`, two foreground calls in one message, both reported to the leg. **Day fold:** an `embarch-log-folder` folded 2026-11-23 (46 units, 167 KB to 53.5 KB, `--apply` confirmed 194 SHAs and 46 reviewer lines), and `--roll` moved 2026-11-21 to `log-archive/`; both ride in this fold. `check-client-names.py --suite --history`: all 16 repos clean.
**Merged:** `agent/api/184-live-log-states-zone-sent-form-and-added-fields` (code: no commits, embarch-api `main` stays `abbd3cf`; doc `1b0b3d65`, the worker's `d3e5faf3` cherry-picked onto `f409bc58`). Re-gated: no code to build; `check-docs.py` 12/12 on both merged doc branches; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new. The live log on a real bench stays as `embarch-api/open.md` says: run `mem_read` and `reset` with a lease held and read `embarch/live/`.
**Budget:** PROCEED at leg start (BURNDOWN, 5-hour 77%, weekly 48%, wave 6); PROCEED at this fold (BURNDOWN, 5-hour 83%, weekly 48%).
**Least sure about:** the zone sentence says the name's time is whatever zone Core stamped `started_at` in; nothing here confirms Core always stamps UTC, so a reader comparing a file name to `t` may be an offset apart.

---

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
## 2026-11-22 — 11 units

*Folded by leg 010's log-folder on 2026-11-23: per-unit narrative reasoning, gate transcripts and budget readings went; every SHA, reviewer line and hardware debt stayed. Detail is in git and in each unit's decision files.*

**Carry forward (the next leg cannot recover these):**
- **EMB-226 (`verify`) is fully landed** with `api/171`; `finish` moves it to Done after that push. EMB-225 and EMB-223 landed earlier in the day.
- **`api/172` (blocked on `core/137`) must compact `embarch-api/interfaces/publish.md`** (11,437 of 12,288 B, in reserve; `api/173` filed blocked, `In flux: yes`) and fix check 5's stale "`adopted` recomputed" cell (now check 6's). `core/137` (open) is dispatchable: Core takes a swept run's earlier files back, closing the one place publish departs from `notes/hil/06` (decision 117 records a refusal).
- **EMB-242** waits in Fleet Ready (study-designer): amend `hil-pdf.md`'s footer band 8 to 15 mm; the first Typst PDF measured 14.96 mm, check 4 uses 8 to 16 mm, A4 width assumed.
- **Open owner question (`api/170`)**: `verify` takes `--public-key`, not a fingerprint (118); whether Core should serve the key instead is unasked.
- **Stale, untouched**: decision 110's "`main.rs` does not call `render_report`" sentence in `embarch-api`.
- **Failure likely to recur**: do not chain a gate through `| tail`; at `umbrella/102` the fold went ahead on `tail`'s exit and `origin/main` was red from `c1b23b9b` to `c10ea59a`, about a minute.
- **Shared crate changed**: `study-designer/088` added the off-by-default `pdf-text` feature, turned on by `embarch-api`'s `pdf` feature only; `api/170` turned on `reducers` and `ed25519-dalek`; `api/167` added four `CoreClient` methods (consumers `embarch-ui`, `embarch-umbrella` built green).
- Leg worktree at `00c50d0b` found clean at 13:14 leg setup; the owner closed `tasks/doc/098` in `b671c249`.
- **Budget**: the weekly window sat at 87 to 93%; the last leg ended on a 5-hour HOLD at 18:37 (5-hour 82%, weekly 93%, resetting about 20:00), three units of four. Bench `api/059` and `dev-bench/038` stay `open`, neither board attached at the 18:09 refresh.
- **Never exercised against real things**: no real Core zip verified or published (M1.14's first real publish is the check); footer band and A4 width rest on this machine's Typst only; the `rate_check` tolerance and `by`/clock choices of `core/132` have met no real capture.
- Spread sweep line (the refill gate reads it): `Spread sweep: nothing filed (2026-11-22 13:05)`

---

### 18:37 api/171 verify-the-pdf-text-report-data-and-pictures
`embarch-api` decisions 122 to 125: check 9 is a whitelist over `report.typ`'s syntax tree and `publish` refuses by it too; check 4 reads the PDF via `pdf-text` and stays `partial` because `appendix.typ` literals are unsigned; check 6 recomputes `report-data.json` independently of Core (two copies that can drift, in `open.md`). Least sure: a number embarch-api wrote wrongly into `appendix.typ` passes as `partial`.
**Merged:** `agent/api/171-verify-the-pdf-text-report-data-and-pictures` (code `2804e41`, ff from `3acf3e1`; doc `b71a55cc`, worker's `81d777c4` cherry-picked onto `0492e7fc`). Gated green, 481 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. No real Core zip verified; footer band and A4 width untested beyond this machine's Typst; fonts outside the embedded set or a number wrapped across a table cell untested.

### 18:19 study-designer/088 the-pdf-text-extractor-and-number-grammar
Decisions 101 to 103: `pdf-text` feature (`lopdf` default-features off, own content-stream interpreter, `DEFAULT_GLYPH_WIDTH_EM = 0.5` assumed, 0.3 `size` word gap assumed). Set `tasks/api/171` open. Shared crate: manifest and `lib.rs` diff read, additive and `cfg`-gated. Least sure: `lopdf`'s dependency weight in embarch-api's binary is unmeasured.
**Merged:** `agent/study-designer/088-the-pdf-text-extractor-and-number-grammar` (code `1fe70b8`, ff from `d6230ad`; doc `750a7fa3`, worker's `8f293b4f` cherry-picked onto `9c08dd4b`). Gated green under every consumer feature set.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Extractor has read only ten hand-assembled fixtures; the 0.3 gap and 0.5 em fallback stay assumed until a Typst PDF runs through it.

### 18:15 api/170 verify-a-published-zip-offline
Decisions 118 to 121 (`verify` CLI-only, `--public-key`, unattested origin passes with words, exit 1 only on `FAIL`, check 2 always `partial`, check 8 to the signed head). Leg setup: the 13:01 leg died on a 5-hour 429, both branches pushed and landed here; refill on depth filed `core/137` (open) and `api/172` (blocked on it). Least sure: decision 121's `serde_json`-bytes hash read from Core's source, not its interface doc.
**Merged:** `agent/api/170-verify-a-published-zip-offline` (code `3acf3e1`, ff from `b274114`; doc `d16a2d58`, worker's `d5374fac` cherry-picked onto `48c6d000`). Gated green, 471 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. `verify` has read only a mock-Core zip re-signed in tests; DSSE statement and run-log entry shapes came from Core's source, not a real zip.

### 13:34 api/168 publish-lists-every-number-and-writes-revisions
Decisions 115 to 117 (`decisions/publish-revisions.md`): lexical number oracle, never refuses on a number; `--prose*` params; revisions `-r<N>`; **a republish after the retention sweep refuses** (departs from `notes/hil/06`, closed by `core/137`). `open.md` out of reserve; `api/169` closed done. I added `b274114` (`cfg_attr` dead_code allow for `--no-default-features`).
**Merged:** `agent/api/168-publish-lists-every-number-and-writes-revisions` (code `db2b7e8` and `b274114`, ff from `a1eda4b`; doc `7fce65bc`, ff from `728e089b`). Gated green, 470 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. No real Core, swept run or `report.typ` through the oracle; OCP T&V lines unvalidated against the schema.

### 13:14 core/136 serve-a-pending-revisions-run-files
Decision 116 amended: the files route serves the run's own files at the pending revision; closes EMB-241. I folded `api/167`'s fragment into embarch-api docs myself and messaged `api/168`'s worker to rebase. Spread sweep: nothing filed (2026-11-22 13:05).
**Merged:** `agent/core/136-serve-a-pending-revisions-run-files` (code `88aff23`, ff from `768c20f`; doc `4923ff44`, ff from `9cd74798`). Gated green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`, unrun (a worktree cannot build natively). The route has met only Core's in-process HTTP test, never embarch-api's `publish` against a real Core; M1.14's first real publish is the check.

### 08:38 api/167 publish-a-study-run-as-one-zip
Split EMB-225 into this and `api/168`. Decisions 112 to 114: `[publish] folder` config, zip naming, call order, CSVs are Core's own renderings. Touched `embarch-core-client` and `Config` additively; `embarch-ui` and `embarch-umbrella` built green against it (build only, not tests). Worker found EMB-241 (split to `core/136`); filed `api/169`. Leg ended on a 5-hour HOLD (92%).
**Merged:** `agent/api/167-publish-a-study-run-as-one-zip` (code `a1eda4b`, ff from `2f7550d`; doc `2b09bc78`, ff from `7b3ef7eb`). Gated green, 457 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. `publish` has met a mock Core only; OCP T&V unvalidated; the `.csv` name for an `OutpostTrace` tap's rendering is unconfirmed.

### 08:16 core/135 cores-side-of-publish
Split EMB-223. `embarch-core` decisions 116 to 119: two publish routes plus a files route, `POST /study/{id}/adopt` (scope and SHA-256, no text), `log_head` tail anchor, `report-data.json` with no clock and two attestation labels. `open.md` compacted in-unit; `tasks/core/133` closed done; `tasks/doc/098` retired. Spread sweep: nothing filed (2026-11-22 08:16). Least sure: attestation labels are the worker's reading of `notes/hil/06`; `run_status` comes from the `clean` flag, not recomputed from `events.json`.
**Merged:** `agent/core/135-cores-side-of-publish` (code `768c20f`, ff from `f16a35b`; doc `a6f48f16`, ff from `ee123c83`). Gated green, 433 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). The publish files under `study_results/` have no `icacls` lockdown, and the `signing-key` and `run-log.jsonl` lockdowns are still unrun on Windows. No real study has been published, and no third-party DSSE verifier has read the manifest; the tests check DSSE v1 with code written from the spec.

### 03:23 umbrella/102 init-on-an-initialised-repo-installs-what-it-lacks
`embarch-umbrella` decision 60: `init` on an initialised repo exits `0` (was `1`), installs the skill and exclude lines it lacks, does not repair MCP registration. Exit-code change: no caller outside the suite was searched. The fold landed with `check-doc-size.py` red (see carry-forward), fixed as `c10ea59a`.
**Merged:** `agent/umbrella/102-init-on-an-initialised-repo-installs-what-it-lacks` (code `27f43a5`, ff from `b3d0106`; doc `55c42437`, worker's `df48ddd8` cherry-picked onto `bc418c8a`). Gated green, 280 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a real initialised firmware repo; skill path `.claude/skills/<name>/SKILL.md` unconfirmed in a live session: run `embarch init` twice in a scratch repo and confirm the agent lists `embarch-hil`.

### 03:22 ui/112 the-study-designer-keeps-a-studys-measurements
`embarch-ui` decision 104: the Study Designer keeps `measurements` without authoring them; `apply_measurements` beside `build_authored`; refusals `400` prefixed `measurements: `. I corrected the code comments citing decision 31 to 104 (`b1b1a24`, comments only). Least sure: the summary line may hide that the study carries uneditable declarations.
**Merged:** `agent/ui/112-the-study-designer-keeps-a-studys-measurements` (code `a9d7e95`, ff from `279c33f`, then `b1b1a24`; doc `fdfa45e8`, worker's `24f6be14` cherry-picked onto `c9cf3216`). Gated green twice, 320 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The `app.js` change has no test or browser drive; no agent-written study opened and saved through the tab.

### 03:20 api/165 compact-api
Verbatim split, no wording changed: `decisions/client-crate.md` 12,278 to 9,360 B (decisions 55 and 66 to `client-crate-funnel.md`), `interfaces/config.md` 11,368 to 7,945 B (to `config-selection.md`). Least sure: `client-crate.md` is 85% full with 58, 62 and 72 pinned by `history/` citations; nothing files moving them. `spec.md` alone omits that the repo hosts `embarch-core-client` and its two token scopes.
**Merged:** `agent/api/165-compact-api` (doc only; doc `6b448201` and `569ca60a`, worker's `54adc7d4` and `d6a708ee` cherry-picked onto `9cb0f77e`). `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 03:19 core/132 measurements-at-a-studys-end
`embarch-core` decisions 113 to 115: Core computes declared measurements at a study's end into the signed `measurements.json`; points on `core_rx_utc_ms`; marker is the first word of a `Text`-tap line; `rate_check` tolerance `0.05 + 2/(n-1)` **[assumed]**; `declared_by` carries the token scope. Leg setup: the 22:33 leg died on a 5-hour 429; four workers ran as foreground calls and all reported. Skipped the spread sweep without a fresh marker (newest was `2026-11-18 23:20`). Also committed the 2026-11-21 fold, rolled 2026-11-19, `check-client-names.py --suite --history` clean on 16 repos. Least sure: `rate_check` tolerance and the `n/T` rate reading high by one interval in `n-1`.
**Merged:** `agent/core/132-measurements-at-a-studys-end` (code `f16a35b`, ff from `99a3e7c`; doc `b134f58f`, worker's `71505591` cherry-picked onto `38b28a75`). Gated green, 426 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). No real study's captures have been reduced: run a study with a `rate` and an `interval` over a bench console, then read `measurements.json` for the arrival granularity and the rate tolerance (recorded in `embarch-core/open/never-exercised.md`). A `study_value` scope from a person token has never been seen end to end.

---
*Days 2026-11-21 to 2026-11-21 rolled to [log-archive/supervisor-log-2026-11-21-to-2026-11-21.md](log-archive/supervisor-log-2026-11-21-to-2026-11-21.md).*
