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

## 2026-11-10 01:34 — chat/015 the spec status line says what is installed

**Decided:** nothing. `embarch-chat/spec.md`'s **Status:** line now says decisions 94–100 are installed (67 retired), citing the 2026-11-05 measurement as a dated fact (the installed `dist/extension.js` md5-identical to the clone's, built 2026-11-04 02:10 after `2b04ff5`; install time unrecorded), and that decision 100 is **not recorded as reviewed**. The line was edited, not appended, and dropped "86–91 live after a window reload" to stay out of reserve: `spec.md` went 9,034 to 9,027 B, 12 B under the reserve line, so no compaction task. `open.md`'s "Promptu in the chat (94–99) waits for install" now says installed, and a new open question asks the owner whether decision 100 was reviewed. Plus, at my dispatch, the comment near line 33 of `webview/chat/composer.tsx` now says the thumbnail sits **above** the input (decision 56 as amended by `chat/020`); comment only. Closes EMB-68.
**Merged:** `agent/chat/015-the-spec-status-line-says-what-is-installed` (code `7a93e95`, ff on `6e15acf`; doc `78ea54b3`, the worker's `77ecf360` cherry-picked onto `4be6006e`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (261 pass, 0 fail, 76 skipped without `EMBARCH_DESK_BIN`), `test:webview` all passed; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The install claim rests on a 2026-11-05 reading; nothing since checks what the installed extension is, and `main` has moved through decision 103 and `chat/010` to `chat/015` since.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6, at start and end; 5-hour 18% to 24%, weekly 55%.
**Least sure about:** the status line now reads "94–100 installed" while saying nothing of what `main` built after 2026-11-04, so a reader can still take the install as current; the task scoped it that way.
**Leg close (next leg, read this first):** 4 of 4 units (`chat/021`, `chat/020`, `atlas/051`, `chat/015`), all first-pass green, all four reviewers clean. Leg began at `dc663c8b`. Two of the four were the killed leg's finished-and-pushed workers, landed here rather than blocked. **Split this leg:** EMB-120 (`atlas/051`, now Done) and **EMB-22 into `atlas/052`, open**: `init` writes a placeholder `MAP.md` until the first `join`. Done this leg: EMB-118, EMB-119, EMB-120, EMB-68. Filed: **EMB-122** (Fleet Ready, `Scope: fleet`: the chat gate never runs the 60 desk-gated host tests); `ready` should move it to the owner's lane. Queue: `atlas/052`, `chat/018`; Fleet Ready is otherwise atlas (11 issues; the two I read besides EMB-22, EMB-23 and EMB-25, say "Direction: not decided") and desk (every one wants a new decision or the owner; EMB-73 is `Scope: suite`). **`desk` and `ui` have no task file.** The desk binary at `.worktrees/embarch-chat/desk-target` is deleted (1.3 GB); a leg gating a chat unit's host tests rebuilds it with `--target-dir` outside every tree. Day fold of 2026-11-09 done; nothing overdue on the size ledger; spread sweep skipped (no source changed since `2026-11-09 17:34`). Bench: not checked; burndown takes no bench task. No `suite` task announced, nothing deployed. Supervisor ownership check on the leg's diff: clean.

## 2026-11-10 01:32 — atlas/051 doc check reports a cite of a page outside the document

**Decided:** nothing numbered; `DESIGN.md`'s `doc check` row amended in place (EMB-120). `doc check` now **fails** a cite outside `1..pages` as a new `P:` check, the worker's choice by analogy: `check.py` already fails a quote cited on the wrong page (A `wrong-page`) and an unanchored prose number (M), and an out-of-range cite can never anchor anything. A record is `failed` with `P: cites page N, outside 1-n`; a `card.md` or `s/*.md` cite goes into `checks.json` under `P` and prints as `P <file>: ...`; either exits 1. `freeze` and `check` share one test, `check.out_of_range`, which reports nothing when `pages` is 0 (a non-PDF source). A record cite of page 0 is already refused by the schema as `V:` and never reaches `P:`, so page 0 is covered through prose and the helper's own assertions.
**Merged:** `agent/atlas/051-doc-check-refuses-a-cite-outside-the-document` (code `f796611`, ff on `bfeae59`; doc `059f6796`, the worker's `6432aa52` cherry-picked onto `29a2d4e8`). Gate on the merge result: `pytest` 684 passed, 3 expected skips (`test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `doc check` on the datasheet behind EMB-40, to see whether its extra page was an out-of-range cite (now a `P:` line) or a high `pages` in `doc.json`.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6.
**Least sure about:** `freeze` used to flag every cite as out of range when `pages` was 0 and now flags none (the reviewer's non-finding); no decision covers that case, and a PDF whose `doc.json` read 0 pages would now pass both checks silently.

## 2026-11-10 01:28 — chat/020 two decisions put the notice and thumbnails under the input

**Decided:** nothing new; decisions 56 (`embarch-chat/decisions/input.md`) and 96 (`decisions/promptu.md`) amended in place for EMB-119. 56's heading now says the pasted image is a thumbnail **above** the input; 96's failed-pass line is "one line above the input (the composer's notice line, as paste and `/btw` use)", and Desk Start work's fallback line says "above the input" too. Both match `webview/chat/composer.tsx` since `chat/014`. The only other "under the box" left in `embarch-chat`'s docs is a **Rejected** alternative in `decisions/assistant.md`, which is history and stays. Doc only: no `embarch-chat` commit.
**Merged:** `agent/chat/020-two-decisions-put-the-notice-and-thumbnails-under-the-input` (doc `e5698bf7`, the worker's `e8fa7f27` cherry-picked onto `1bee15af`; no code branch). Landed by this leg from the branch the worker pushed at 23:08, as the previous leg was being killed. Gate on the merge result: `check-docs.py` 12/12; ownership `chat` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00, wave 6.
**Least sure about:** the reviewer found a stale code comment near line 33 of `webview/chat/composer.tsx` ("thumbnail under the input"); I folded fixing it into `chat/015`'s dispatch as a comment-only edit, so if that unit blocks, the comment stays stale.

## 2026-11-10 01:26 — chat/021 six host tests fail against the local desk binary

**Decided:** nothing. The cause is test-side, not the desk: a chat's process environment is taken when the chat is created (`ChatManager.create` reads `s.env?.()`, and a reload restores the same way), and five tests started their chat on `basic` or `deny` and only then set `FAKE_CLAUDE_FIXTURE` or `FAKE_CLAUDE_INPUT_LOG`, so the fake CLI replayed the wrong recording into a 5 s timeout. The sixth (Start work with Promptu, decision 96) was the stale 2026-11-03 binary and passes on a desk built from `main`. Fix in `test/host.test.mjs` only: `startUntracked` takes a recording name or an absolute path and the five name theirs there; the reload-queue test sets its input log before `reload`. No desk bug. Closes EMB-118.
**Merged:** `agent/chat/021-six-host-tests-fail-against-the-local-desk-binary` (code `6e15acf`, ff on `424c3cf`; doc `208e3dc0`, the worker's `bf60fd1f` cherry-picked onto `e852ae8e`). Landed by this leg from branches the worker pushed at 23:06, before the previous leg was killed. Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (261 pass, 0 fail, 76 skipped without `EMBARCH_DESK_BIN`), `test:webview` all passed; **`test/host.test.mjs` with `EMBARCH_DESK_BIN` set to the desk built from `main` `4b83b5e`: 60 pass, 0 fail**; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, burndown until 2026-11-11 06:00 (latch re-armed 01:16 at weekly 55%, no `gate=off` line this time, so the 97% caps apply), wave 6; 5-hour 18%.
**Least sure about:** the gate still skips those 60 tests on every chat unit, so the next test-side fault there is as invisible as this one was; running them needs a `gate.md` rule, which is the owner's, so I filed **EMB-122** (`Scope: fleet`, gap; `ready` will move it to the owner's lane).
**Leg notes (this leg, first unit):** spawned with the pump latched in burndown, no stop marker, no owner message. **Recovery:** the previous leg was killed at ~23:08 with `chat/020` and `chat/021` claimed; both worktrees were clean and both workers had pushed (`chat/021` code and doc, `chat/020` doc only, as the task is doc only), so a pushed branch retired each worker and this leg lands them as its units 1 and 2 rather than blocking them. Leg began at `dc663c8b`. The 2026-11-09 day is folded (log-folder: 43 units, 112 KB to 26 KB) and 2026-11-06 rolled to `log-archive/`; `check-client-names.py --suite --history` clean on all 16 repos. **Split EMB-120 into `tasks/atlas/051` and EMB-22 into `atlas/052`** (`9a88a836`). Spread sweep skipped: no source changed since `2026-11-09 17:34`. `atlas/051` dispatched 01:21 and reported at 01:24. Nothing overdue on the size ledger.

## 2026-11-09 — 43 units

*Folded 2026-11-10 by the leg's log-folder from the day's 43 per-unit entries (the narrative reasoning behind each accepted judgement, the gate transcripts and every "Least sure about" that git or a filed issue already holds went; every SHA, every Reviewer line and every Hardware debts line stays, one block per unit below). The day ran as ten legs at wave 6 under burndown (`gate=off` latch until 2026-11-11 06:00; a real 429 is still the stop signal).*

**Carry forward (the next leg cannot recover these):**
- **chat/020 and chat/021 are not in this day.** The leg that died at ~23:08 dispatched them (EMB-119 into `chat/020`, doc only: decisions 56 and the Promptu decision still say "under the input"; EMB-118 into `chat/021`, host tests against a desk built from `main`, split in `ff265215`); the current leg is landing them. The desk binary for `chat/021` was built at `/home/gabriel/Github/embarch/.worktrees/embarch-chat/desk-target` (outside every repo tree); delete it at leg end.
- **Filed today and still open:** EMB-116 (Backlog, `Type: decision`, owed `embarch-chat` decision beside 91: the chat never scrolls sideways; proposed text under `## Owed decision` in the retired `chat/010` task file), EMB-118 (Fleet Ready, chat: six host tests fail against the local desk binary; the binary was built 2026-11-03), EMB-119 (Fleet Ready, chat: decisions 56 and Promptu say "under the input", stale after `chat/014`), EMB-120 (Fleet Ready, atlas, gap). Also EMB-111 (desk, `/linear/mine` and `/linear/open` still answer an empty scope on a team-bound desk), EMB-112 and EMB-113 (Backlog, atlas, for the owner: the port join ignores sheet hierarchy; Check K's best-agreeing group lets a wrong-condition number pass), EMB-104 (Backlog, Fleet Ready has no one-line listing), EMB-105 (desk, landed as `desk/012`), EMB-115/117 (ui, landed as `ui/106`/`ui/107`).
- **desk has no task file.** Every desk issue left in Fleet Ready wants a new decision (EMB-14, 17, 82) or the owner (EMB-11's SKILL.md half, EMB-19's west design); burndown withholds decisions. **EMB-73 (`Scope: suite`) is untouched**: its last box asks for an `embarch-dev-workflow.md` section 6 change, which is the owner's, plus new decisions in two sub-projects.
- **Queue at day end:** `chat` 015, 018 (018 opened by the `chat/017` fold), plus `chat/020`, `021`; `chat/019` and `promptu/004` are `blocked`, `In flux: yes`, due 2026-11-23 (size debts, both `spec.md` compactions; `desk/011` is paid). `promptu/004` stays blocked on decision 30's build step 4. `embarch-chat/spec.md` is 9,034 B, 5 B under its reserve line: a chat unit that edits it must ride the compaction along. Fleet Ready is mostly `atlas` (about 16 left; EMB-40 landed as `atlas/050`) and `desk` as above.
- **Still owed:** the first leg after midnight owes the day fold (this) and `check-client-names.py --suite --history`; the size ledger has nothing overdue. Spread sweep skipped all evening: no source changed since `2026-11-09 17:34` (its marker). Bench not checked; burndown takes no bench task. No `suite` task announced, nothing deployed.
- **Failure patterns likely to recur:** (1) workers leave a state line the gate refuses (`claimed`, `done,`, `done (`): check the task's state line before cherry-picking. (2) A fold that retires a task named in another task's `Unparks when:` turns `check-task-state.py` red only after the fold's own gate ran (fixed on `main` as `f76b9305`): check other parks before folding. (3) A green `test:webview` proves nothing about a new check unless its own PASS line is in the output; grep for it on every chat unit that adds one (`chat/010` called a check passing that never ran). (4) The harness sends a leg a hand-back prompt with workers in flight (twice): keep landing, do not `leg-end`; the auto-mode classifier refuses a force-push to an `agent/*` branch after a rebase. (5) Workers use inline Python edit scripts and skip the hook's filing prompt (one filed EMB-108). (6) The chat host tests fail 5 to 6 ways against a stale desk binary (decisions 63, 64, 72, 77, 78, 96 on `chat/013`; five different ones on `chat/007`); `chat/021` is the check. (7) Read each issue's named files on `main` before writing a task (`ui/105` and `chat/013` were two-thirds stale); reconcile desk issues against decision 77 (EMB-94).
- **Decisions made on the owner's behalf today:** unparked `core/112` on its due date to fill a fourth scope slot (verbatim split only; decision 89 still unverified against a moved probe); split Fleet Ready issues in waves (`cef37baf` 14 issues into 16 tasks and the first `promptu` tasks; `273ed317`, `bf619a2a`, `e20382b7`, `5fdc6473`, `288a1fce`, `e4273cec`, `dc2a64de`, `ff265215` later), announcements at `ts` `1794270556.536659` and `1794277712.673199`. The only design call no task made: `chat/008`'s Memory pass chat is `untracked` (one line in `startMemoryPass` if the owner wants it tracked).
- **Leg start SHAs (main at each leg's begin, oldest first):** `5b8d8362`, `3ffc8e00`, `0ebf3855`, `fa94400b`, `2ef4d1d7`, `9e8abd40`, `504bd5e6`, `62b51dff`, `0d7c20c4`, `836d2a3c`, `7332632a`.
- **Recovery:** the leg that started 17:47 split six issues (`273ed317`), dispatched at 17:54, landed `atlas/038` and died without a tick, fold or log entry; the `atlas/038` fold below is recovery (its three other claims reclaimed to `open` in `2bc10797`).

**Units, newest first** (code SHA is on `main`; "doc" is the cherry-picked doc commit; each gate was green on the merge result unless stated):

### 23:08 — ui/108 the Desk tab's note count and switch warning match the desk
**Merged:** `agent/ui/108-the-desk-note-count-and-switch-warning-match-the-desk` (code `08f9a53`, ff on `c3c4909`; doc `b4c08f80`, the worker's `a0ba7d4b` cherry-picked onto `64098d7c`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The e2e debt the worker recorded is paid (above).

### 23:03 — atlas/050 doc freeze reports the document's real page count
**Merged:** `agent/atlas/050-doc-freeze-reports-the-document-s-real-page-count` (code `bfeae59`, ff on `cbd1bb9`; doc `0a4077b5`, the worker's `b49ff555` cherry-picked onto `275ee998`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `doc freeze` on the datasheet that showed P one over its page count. A warning line means the cause was an out-of-range cite; still one over with no warning means `doc.json`'s `pages` is itself high, a separate bug.

### 22:52 — chat/014 the input is one row
**Merged:** `agent/chat/014-the-input-is-one-row` (code `424c3cf`, ff on `fad3fe8`; doc `3cc86864`, the worker's `1245cc10` cherry-picked onto `02589f25`).
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-119
**Hardware debts:** none needing a board. Owed to a live window: the one-row input at a narrow pane, Send never pushed off, and both popovers inside it. Nothing installed.

### 22:36 — atlas/049 a document's own header names its revision and number
**Merged:** `agent/atlas/049-a-document-s-own-header-names-its-revision-and-number` (code `cbd1bb9`, ff on `84d8909`; doc `ce813c73`, the worker's `a7c8d3c7` cherry-picked onto `6ea97619`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: `atlas inventory` and `doc prep` on the non-chip datasheet that showed it, confirming rev `A` and doc_no `001`; only synthetic PDFs show either.

### 22:34 — ui/107 a session row whose folder is gone says so
**Merged:** `agent/ui/107-a-session-whose-folder-is-gone-says-so-on-the-desk-tab` (code `c3c4909`, ff on `9f2026d`; doc `5bb109d7`, the worker's `99bc240c` cherry-picked onto `34e9fab6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live UI: a session whose folder was deleted showing "folder gone" on the Desk tab. Nothing installed.

### 22:32 — desk/017 a start that resolves no desk is no desk everywhere
**Merged:** `agent/desk/017-a-start-that-resolves-no-desk-is-no-desk-everywhere` (code `4b83b5e`, ff on `377c116`; doc `5c77a371`, the worker's `08ca0b5e` cherry-picked onto `bc5a34f7`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a session resumed in a folder with no desk hearing and writing no desk's notes. Nothing installed.

### 22:20 — chat/013 a window start never raises the UI tab
**Merged:** `agent/chat/013-a-window-start-never-raises-the-ui-tab` (code `fad3fe8`, ff on `bae5fa8`; doc `2aa4a91c`, the worker's `79c7760c` cherry-picked onto `799bd173`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a reload that raises no browser tab. Nothing installed.

### 22:12 — atlas/048 a part named in passing is not covered
**Merged:** `agent/atlas/048-a-part-named-in-passing-is-not-covered` (code `84d8909`, ff on `df232e9`; doc `108cc9c1`, the worker's commit cherry-picked onto `25a6cd7e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: a datasheet whose own part first appears on page 2 (a long cover page) is now proposed rather than covered; only synthetic PDFs show either case.

### 22:12 — ui/106 Pick up says no card on the board
**Merged:** `agent/ui/106-pick-up-says-no-card-on-the-board` (code `9f2026d`, ff on `877a042`; doc `25a6cd7e`, the worker's commit cherry-picked onto `ad2cd9dc`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live UI: the Pick up title and empty note reading the new words. Nothing installed.

### 22:09 — desk/016 a session whose folder is gone says so
**Merged:** `agent/desk/016-a-session-whose-folder-is-gone-says-so` (code `377c116`, ff on `d48a18d`; doc `664a1198`, the worker's `9817a08a` cherry-picked onto `a6129099`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a session whose folder was deleted showing `folder_missing` and no Go to chat. Nothing installed.

### 21:58 — chat/010 the chat never scrolls sideways
**Merged:** `agent/chat/010-the-chat-never-scrolls-sideways` (code `bae5fa8`, ff on `80bf56d`: the worker's `889efda` and `8990003` plus my `bae5fa8`; doc `f29acbf1`, the worker's `197b3fbc` cherry-picked onto `5a032a31`).
**Blocked:** nothing, after one send-back. **The worker's first report called the new check passing when it never ran**: a one-off Python replace hit the first `await teardown();` in `test/webview.e2e.mjs`, which is inside the `uncaughtException` handler, so the check only ran on a crash and the gate was green without it. I caught it because the new check's name was absent from the `test:webview` output, and sent it back; the worker moved it to the chat checks (it must run before `go("/list.html")`) and showed it FAIL with `style.css` reset to `main`. Its fix left the crash handler's `await teardown();` unindented, which `bae5fa8` restores (whitespace only).
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a long line in a code block, diff and table wrapping with no sideways bar. Nothing installed.

### 21:28 — desk/015 an issue whose card the view window hides is listed in Pick up
**Merged:** `agent/desk/015-a-card-outside-the-view-window-is-in-pick-up` (code `d48a18d`, ff on `3d29d6c`; doc `51bd41a7`, the worker's `a68f1316` cherry-picked onto `3f82ff92`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a card quiet past the window showing its issue in Pick up, and Add card putting it back. Nothing installed.

### 21:27 — atlas/047 application reports and reference-manual user's guides get their kind
**Merged:** `agent/atlas/047-application-reports-and-reference-manual-users-guides-get-their-kind` (code `df232e9`, ff on `ca32a6c`; doc `dba08bbe`, the worker's `640ece3a` cherry-picked onto `2a255c73`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real vendor file: that an actual reference manual published as a user's guide carries the self-naming line within page 1's top and 80 characters; only synthetic PDFs show it.

### 21:24 — desk/014 my issues and open issues name their scope
**Merged:** `agent/desk/014-my-issues-and-open-issues-name-their-scope` (code `3d29d6c`, ff on `5a8fcad`; doc `a3c58e99`, the worker's `67707ef2` cherry-picked onto `57a9dbb5`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a team-bound desk's My issues and open-issues answers reading `team <KEY>`. Nothing installed.

### 21:15 — chat/016 a deleted chat folder is named as missing
**Merged:** `agent/chat/016-a-deleted-chat-folder-is-named-as-missing` (code `80bf56d`, ff on `55e758b`; doc `b54dae62`, the worker's `3649fb60` cherry-picked onto `5f07e385`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a chat whose folder was deleted showing the folder error on its next message. Nothing installed.

### 21:11 — atlas/046 Check K reads side-by-side groups and a lone TYP column
**Merged:** `agent/atlas/046-check-k-reads-side-by-side-groups-and-a-lone-typ` (code `ca32a6c`, ff on `4a27ae0`; doc `aadfe5e5`, the worker's `9f20c0b8` cherry-picked onto `2a544fae`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 21:05 — atlas/045 nets joined through an off-sheet port are one net
**Merged:** `agent/atlas/045-nets-joined-through-an-off-sheet-port-are-one-net` (code `4a27ae0`, ff on `b2d418e`; doc `48a93f88`, the worker's `d9baa1e0` cherry-picked onto `d9e681b6`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a real export: that a net's `Ports > <title>` outline children carry the port name, which only the synthetic fixtures show.

### 21:02 — desk/013 a word search names the team it searched
**Merged:** `agent/desk/013-a-word-search-names-the-team-it-searched` (code `5a8fcad`, ff on `bc06133`; doc `3c9141d4`, the worker's `04c05358` cherry-picked onto `169207d2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a team-bound desk's word search answering with `team <KEY>`. Nothing installed; the running desk keeps the old answer until the owner rebuilds it.

### 20:54 — chat/011 the inline diff is one line until opened
**Merged:** `agent/chat/011-the-inline-diff-is-one-line-until-opened` (code `55e758b`, ff on `9fd3f0b`; doc `6761d22d`, the worker's `aca3157b` cherry-picked onto `325d8acd`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: an Edit row closed, opening and closing on a click, and a permission card's diff still open. Nothing installed.

### 20:43 — atlas/044 a cite of another document is checked there
**Merged:** `agent/atlas/044-a-cite-of-another-document-is-checked-there` (code `b2d418e`, the worker's `f893727` rebased by me onto `9bc7b11` (atlas/043) and ff; doc `94f703fd`, the worker's `73129abc` cherry-picked onto `e2609b78`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:41 — desk/012 the skill and the server take the work item from the prompt first
**Merged:** `agent/desk/012-the-skill-and-server-take-the-work-item-from-the-prompt` (code `bc06133`, ff on `b47c12e`; doc `f4bc2dc9`, the worker's `2c0b9858` cherry-picked onto `39ba6c6a`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live session: a session started with an issue key in its prompt taking it from the skill or the server instructions rather than asking. Nothing installed; the running desk keeps the old strings until the owner rebuilds it.

### 20:40 — atlas/043 the renderer reads Note N footnotes
**Merged:** `agent/atlas/043-the-renderer-reads-note-n-footnotes` (code `9bc7b11`, ff on `fe7c00c`; doc `db7c29d6`, the worker's `f5d8ede6` cherry-picked onto `8d7ff3e0`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:30 — chat/012 the side-question button is on the rail
**Merged:** `agent/chat/012-the-side-question-button-is-on-the-rail` (code `9fd3f0b`, ff on `b765313`; doc `f81355d1`, the worker's `23de1281` cherry-picked onto `51929357`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: the 💬 on the rail asking, Esc and the disabled state; nothing installed.

### 20:28 — desk/010 a Start work worktree links the clone's local files
**Merged:** `agent/desk/010-a-start-work-worktree-links-the-clones-local-files` (code `b47c12e`, ff on `5837ef5`; doc `b6730147`, the worker's `3710aa5b` cherry-picked onto `b67caf1e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live desk: a real Start work on a clone holding an atlas and an `.mcp.json`, and the session in it loading both; the Windows symlink branch (`symlink_dir`/`symlink_file`) was neither compiled nor run here. Nothing installed; the running desk keeps the old behaviour until the owner rebuilds it.

### 20:24 — atlas/042 a kind override reaches a prepped document's doc.json
**Merged:** `agent/atlas/042-a-kind-override-reaches-a-prepped-documents-doc-json` (code `fe7c00c`, ff on `da6c505`; doc `0da06622` and `d7f95f58`, the worker's `77dd3890` and `0391c5c2` cherry-picked onto `d2a90464`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:22 — desk/011 decisions/agents.md leaves the reserve by verbatim split
**Merged:** `agent/desk/011-compact-desk` (doc only: `49030a21`, the worker's `6cf2b043` cherry-picked onto `f4925c97`, plus my link fix `b0c191b3`; no code worktree).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:14 — chat/008 the Memory menu shows when a memory pass is due
**Merged:** `agent/chat/008-the-memory-menu-shows-when-a-memory-pass-is-due` (code `b765313`, ff on `a46c5ac`; doc `574f817a`, the worker's `47ce86ea` cherry-picked onto `e14370ac`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: the three settings set, the due dot and the line showing, and a click opening a chat whose first message is the command, on the window's login and desk; the host path (reading the stamp, `startMemoryPass`) has no test that runs here. The due state refreshes only on page load or menu open. Nothing installed.

### 20:09 — desk/009 the start hook takes the work item from the prompt
**Merged:** `agent/desk/009-the-start-hook-takes-the-item-from-the-prompt` (code `5837ef5`, ff on `aa56a7a`; doc `ec7d333f`, the worker's `10570fdb` cherry-picked onto `529a0a77`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live session: the key-first behaviour lives in a model following the hook's text, and the test asserts only the text. Nothing installed; the running desk keeps the old text until the owner rebuilds it.

### 20:08 — atlas/041 check S reads a dimension cell as one value
**Merged:** `agent/atlas/041-check-s-reads-a-dimension-cell-as-one-value` (code `da6c505`, ff on `18756a3`; doc `38280b72`, the worker's `93d563cf` cherry-picked onto `4eee35c3`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 20:06 — core/112 two full Core docs leave the reserve by verbatim split
**Merged:** `agent/core/112-compact-core` (doc only: `901e51d0`, ff on `aae32208`; no code worktree).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `open.md`'s decision-89 bullet (a moved-probe run) is unchanged and still owed.

### 19:58 — chat/017 the chat gives Promptu's pass its context usage
**Merged:** `agent/chat/017-promptu-is-given-the-chats-context-usage` (code `a46c5ac`, ff on `468547a`; doc `abb84190`, the worker's `9d55fcaa` cherry-picked onto `15057714`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a real Promptu run from the chat receiving the flag; the test calls `runs.begin` with a stub CLI. Nothing installed or deployed.

### 19:53 — desk/008 a foreign issue key names the desk that holds it
**Merged:** `agent/desk/008-a-foreign-issue-key-names-the-desk-that-holds-it` (code `aa56a7a`, ff on `3141190`; doc `677278e6`, the worker's `1e60c745` cherry-picked onto `61deb548`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Nothing installed or deployed; the running desk keeps the old message until the owner rebuilds it.

### 19:53 — atlas/040 check U finds a unit as a token and reads a symbol whole
**Merged:** `agent/atlas/040-check-u-finds-a-unit-as-a-token-and-reads-a-symbol-whole` (code `18756a3`, ff on `335939a`; doc `61deb548`, the worker's `e15cda32` cherry-picked onto `be0a0118`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:50 — promptu/003 decision 40 follows the one-colour rail
**Merged:** `agent/promptu/003-decision-40-follows-the-one-colour-rail` (doc only: `b92ffb51`, the worker's `ec956b31` cherry-picked onto `724d0dfa`; the `embarch-promptu` worktree stayed clean and was not pushed).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:43 — chat/009 the rail's icons are one-colour SVGs
**Merged:** `agent/chat/009-the-rail-icons-are-one-colour` (code `468547a`, ff on `f823dc8`; doc `2313f775`, the worker's `212da07f` cherry-picked onto `6d480129`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: nobody has looked at the five icons in a light and a dark theme, and the shapes are the worker's own 16 px strokes, which may want a design pass. Nothing installed.

### 19:33 — desk/007 an issue read says when comments were cut
**Merged:** `agent/desk/007-an-issue-read-says-when-comments-were-cut` (code `3141190`, ff on `0c44f9d`; doc `15f59412`, the worker's `84a8c0ef` cherry-picked onto `816f2c92`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live Linear check, written into the task and decision 59: which end of a thread of more than 25 comments each account type keeps is assumed newest-first, not measured. Nothing installed or deployed.

### 19:32 — promptu/002 the pass plans for work that will outgrow one context window
**Merged:** `agent/promptu/002-the-pass-plans-for-high-context-work` (code `95f0d69`, ff on `94181bb`; doc `71b1dfb0`, the worker's `5a71d01a` cherry-picked onto `35f430ef`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed Promptu on this machine runs the old binary until the owner rebuilds it; nothing here deploys.

### 19:30 — atlas/039 a step marker in a rule is not a numeric claim
**Merged:** `agent/atlas/039-a-step-marker-in-a-rule-is-not-a-numeric-claim` (code `335939a`, ff on `50a9a15`; doc `a61362e6`, the worker's `e3084a54` cherry-picked onto `bf619a2a`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 19:26 — atlas/038 a spaced minus and a thousands separator parse as one number
**Merged:** `agent/atlas/038-a-spaced-minus-and-a-thousands-separator-parse-as-one-number` (code `50a9a15`, ff on `a034cc6`; doc `3ffc8e00`), both landed by the dead leg. I re-ran the gate on the merge result: `pytest` 656 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean. The task now reads `done` and this fold retires it; one changelog fragment assembled into `history/atlas.md`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 17:45 — chat/007 an agent hands its chat to a fresh session
**Merged:** `agent/chat/007-an-agent-hands-its-chat-to-a-fresh-session` (code `f823dc8` on `bce5ac7`, ff; doc `ee7e48bf`, the worker's `5a6fc140` cherry-picked onto `1e8be150`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window, written into the task: a real `claude` calling `mcp__embarch-chat__handoff` (the wire tests call the tool through `mcpServer` directly, there is no recorded fixture), and the tab and sidebar re-pointing in a real VS Code window. Nothing installed or deployed.

### 17:37 — ui/105 the README points at the chat's launcher
**Merged:** `agent/ui/105-the-readmes-point-at-the-chats-launcher` (code `877a042`, ff; doc `6164b79d`, the worker's `1f1a082e` cherry-picked onto `e222ce57`, task file and changelog fragment only).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 17:36 — promptu/001 a header-less memory index may take its first header
**Merged:** `agent/promptu/001-a-header-less-memory-index-may-take-its-first-header` (code `94181bb` on `866a24e`, ff; doc `0b519941`, the worker's `f76382b0` cherry-picked onto `c8f4b929`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed hook on this machine still runs the old binary until the owner rebuilds or reinstalls it; nothing here deploys.

### 17:34 — desk/006 four desk docs leave the reserve by verbatim split
**Merged:** `agent/desk/006-compact-desk` (doc `ab1d2c96`, the worker's `b55848d2` cherry-picked onto `93cd09a7`; no code). `decisions/cockpit.md` 12,062 → 6,100 B (57, 58, 60, 61, 76 to new `decisions/hand.md`), `decisions/desks.md` 12,169 → 8,306 B (62–64 to new `decisions/tiles-after-send.md`), `interfaces.md` 14,426 → 10,498 B (the embarch-chat route table to `interfaces/chat-routes.md`), `spec.md` 9,219 → 8,379 B (constants rows to `spec/constants.md`), PAID. I compared removed against added lines: identical except index rows and links re-pointed one level up.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

## 2026-11-07 — 4 units

*Folded 2026-11-09 by a log-folder; per-unit reasoning, gate detail, budget lines and least-sure notes went, git and the decision files hold them.*

**Carry-forward (next leg, read this first):** 4 of 4 units (`dev-bench/003`, `004`, `041`, `016`), all `toolchain` tasks run by the leg's own hands, serially. Leg began at `68a20e3a`. **52 issues reached Fleet Ready during this leg** (25 atlas, 16 desk, 9 chat, 1 promptu, 1 ui; `queue-status.py` now reads 52 dispatchable): the next leg's `ready` takes them in and splits them, and that split is most of its work. **The pump is off and the listener disarmed** (its own FYI at 10:15), so no relay follows this leg unless the owner starts one. **`EMB-83` (Backlog, decision) is the owner's**: whether `toolchain` tasks go to workers as `none` (a worktree builds fine against the main checkout's workspace) or stay with legs, and the fleet venv's missing `natsort` and `esptool`. Decisions 50, 51 and 52 are new in `embarch-dev-bench`; 50 was amended by 51 within the leg. 13 `toolchain` tasks remain. Bench: neither role attached; `api/059`, `dev-bench/035`, `038` stay `open`. Size ledger: `core/112` falls due **2026-11-09**. No `suite` task announced, nothing deployed, the owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone.

**Decided (day):** nothing suite-wide. Started the `toolchain` lane with the leg's own hands (`protocol.md` §7, `tasks/README.md` grant it; first use ever; legs dreamt instead on 2026-10-28 and 2026-11-06, no reply in dream thread `1793997725.841939`), built from a worktree against the main checkout's workspace; that undercuts the README's reason these are not worker tasks, hence `EMB-83`. `scanning.md` is at 11,034 B, 25 B outside its reserve line. `twister` cannot start (no `natsort`), so ztests ran suite by suite. ESP32-C5 image never built (no `esptool` in the fleet venv). Open side note, not filed: the Rust reference interpreter subscripts `states[]` unchecked and would panic where the C side now fails the run. New `census_summary` static is +56 B RAM on the Nordic image (59.67%), unbuilt on the ESP32-C5.

### Units

**dev-bench/003** (10:28) length prefix bounded before arithmetic (`pc_skip_len_prefixed`).
**Merged:** `agent/dev-bench/003-pc-skip-len-prefixed-wraps-past-its-own-bounds-check` (code `61c96c2` on `5dd78b5`, ff; doc `f4e7213f`, `b3ddf812` cherry-picked onto `6ac10be8`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. The ESP32-C5 image was not built: Zephyr's Espressif SoC CMake wants `esptool` on `PATH` and the fleet venv has none. Same file compiles for host and Cortex-M33, so the risk is low; `EMB-83` carries the venv gap.

**dev-bench/004** (10:36) out-of-range state-machine index fails the run; new `embarch-dev-bench` decision 50 (`decisions/protocols.md`), run-time rather than decode refusal.
**Merged:** `agent/dev-bench/004-protocol-state-indices-reach-a-c-array-unchecked` (code `952f788` on `61c96c2`, ff; doc `d4922d38`, `97eda043` cherry-picked onto `d7056346`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. ESP32-C5 image not attempted (`EMB-83`, no `esptool` in the fleet venv).

**dev-bench/041** (10:45) a study over a bench cap is refused out loud; new decision 51 (`decisions/link-limits.md`), amends 50.
**Merged:** `agent/dev-bench/041-a-study-the-bench-cannot-hold-is-refused-out-loud` (code `4026cde` on `952f788`, ff; doc `73f4d033`, `d35e009f` cherry-picked onto the claim commit).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the ESP32-C5 image, one `Done when` box left unticked in the task for it (`EMB-83`, no `esptool` in the fleet venv). On a board: a 17-step `StudyStart` should produce the `LogLine` in Core's `dev-bench.log`; nothing has sent one yet.

**dev-bench/016** (10:53) the census `fail_reason` is composed where a test reaches it; new decision 52 (`decisions/scanning.md`).
**Merged:** `agent/dev-bench/016-the-two-census-gates-have-no-test-that-can-reach-them` (code `9371510` on `4026cde`, ff; doc `ec9ed080`, `33422dbe` cherry-picked onto the claim commit).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** unchanged from `dev-bench/008`: one failed name-filtered and one failed address-filtered `BleConnect` on the bench, reading the `fail_reason` and the census log. ESP32-C5 image not built (`EMB-83`).
*Days 2026-11-06 to 2026-11-06 rolled to [log-archive/supervisor-log-2026-11-06-to-2026-11-06.md](log-archive/supervisor-log-2026-11-06-to-2026-11-06.md).*
