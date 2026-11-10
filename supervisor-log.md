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

## 2026-11-09 19:58 — chat/017 the chat gives Promptu's pass its context usage

**Decided:** nothing new; decision 96 in `embarch-chat/decisions/promptu.md` is amended in place to name the context usage, `embarch-promptu` decision 41 and contract §7.10. `beginPromptu` passes the header meter's percentage as `contextUsage`; `prep` appends `--context-usage <n>` as a whole number clamped to 0–100, and nothing when the chat has not measured it (Start work into a new chat). This completes EMB-65 with `promptu/002`. **In this fold I set `chat/018` `open`**, as its `Unparks when:` named this task, and **rewrote `promptu/004`'s `Unparks when:` and `In flux:`** to drop the landed `chat/017` half, because `check-task-state.py` refuses a park naming a task no longer in the queue; it stays `blocked` on build step 4.
**Merged:** `agent/chat/017-promptu-is-given-the-chats-context-usage` (code `a46c5ac`, ff on `468547a`; doc `abb84190`, the worker's `9d55fcaa` cherry-picked onto `15057714`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (259 pass, 0 fail, 75 skipped for want of `EMBARCH_DESK_BIN`), `test:webview` all passed; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: a real Promptu run from the chat receiving the flag; the test calls `runs.begin` with a stub CLI. Nothing installed or deployed.
**Budget:** PROCEED, gate off by latch (burndown), wave 6; this leg holds 4.
**Least sure about:** the worker reported `test:webview` red on `EADDRINUSE` (port 4989, a listener left by its own first gate run, which it had backgrounded), said the auto-mode classifier refused its kill, and asked me to kill the process. **I did not**: a denied action is not one to run on a worker's behalf. By the time I gated, the process was gone and the port free, and the whole gate passed on my run. The worker also reverted its `embarch-chat/spec.md` edit because it would have put that file into reserve, so `spec.md`'s Promptu line does not mention the context usage; decision 96 carries it.
**Leg close (next leg, read this first):** 4 of 4 units (`promptu/003`, `atlas/040`, `desk/008`, `chat/017`), all first-pass green, all reviewers clean. Leg began at `0ebf3855`; `check-ownership.py --supervisor` OK on its 13 paths. **Burndown is latched with `gate=off`** (until 2026-11-11 06:00), so `usage-budget.py` checks nothing and says PROCEED at wave 6; a real 429 is still the stop signal. **I split no Fleet Ready issue**: all 28 are `desk` or `atlas` (EMB-82 wants a new decision, EMB-76 is half outside the fleet, EMB-40 needs a datasheet the fleet does not have), and both scopes already hold queued tasks. Spread sweep skipped (nothing changed since `2026-11-09 17:34`); no new marker line, since I did not sweep. Queue now: `atlas` 041–044, `chat` 008, 010–013, 015, 016, 018 (just unparked), `desk` 009–011; **`promptu` has nothing dispatchable**, so three scopes. `chat/014` still waits for `chat/012`. **`core/112` falls overdue tomorrow**: the first leg after midnight spends its first unit on it and also owes the day fold and `check-client-names.py --suite --history`. All four workers met a hook asking them to file an issue about their inline Python edit scripts and all four skipped it; a pattern for the owner, not filed. Bench: not checked; burndown takes no bench task. No `suite` task announced, nothing deployed.

## 2026-11-09 19:53 — desk/008 a foreign issue key names the desk that holds it

**Decided:** nothing new; decision 77 is amended in place with one sentence (a key no workspace has says why), and `agents.md`, in reserve, is untouched. A missing key now gets one of three messages: its team is bound to another desk, so the message names that desk and its first folder; no connected workspace has its team, so it says so and names no desk; otherwise the old plain message. Wired into `GET /linear/issue/{key}`, `POST /linear/status`, `ensure_item` and `link_item`, through a typed `linear::NoWorkspaceHas` whose text is unchanged.
**Merged:** `agent/desk/008-a-foreign-issue-key-names-the-desk-that-holds-it` (code `aa56a7a`, ff on `3141190`; doc `677278e6`, the worker's `1e60c745` cherry-picked onto `61deb548`). Gate on the merge result: `cargo build`, `cargo test` (194), `clippy --all-targets -D warnings` green; client names clean; ownership `desk` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Nothing installed or deployed; the running desk keeps the old message until the owner rebuilds it.
**Budget:** PROCEED, gate off by latch (burndown), wave 6; this leg holds 4.
**Least sure about:** the Send-side paths (`post_comment`, `edit_issue`, `create_issue`'s team message) still give the plain message, and a key whose team is bound to another desk names that desk even if the team has since left every workspace; neither is in the task's `Done when`, and nothing is filed for them.

## 2026-11-09 19:53 — atlas/040 check U finds a unit as a token and reads a symbol whole

**Decided:** nothing new; `DESIGN.md`'s check U row says what changed. A unit is on the page only as a token: no letter may touch it on either side, digits may, so `100mA` still matches and `µA` no longer passes on "guaranteed". A CamelCase symbol (`LoadReg`) gets no dimension from its first letter; `VOVP`, `IQ`, `Lx`, `tPD`, `fSWmin` still do. The font case (µ and Ω printed as `m` and `W`) stayed out of scope with no fixture showing it, as the task allowed.
**Merged:** `agent/atlas/040-check-u-finds-a-unit-as-a-token-and-reads-a-symbol-whole` (code `18756a3`, ff on `335939a`; doc `61deb548`, the worker's `e15cda32` cherry-picked onto `be0a0118`). Gate on the merge result: `pytest` 658 passed, 3 expected skips (west workspace, built atlas, vendor SVD; `test_public_guard` ran); client names clean; ownership `atlas` OK on both branches; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, gate off by latch (burndown), wave 6; this leg holds 4.
**Least sure about:** the word-symbol guard also exempts names like `VoutMax` from the first-letter read, so U no longer checks their unit at all, and plural `ohms` no longer matches the `ohm` token; the worker judged both rare, and no test pins either.

## 2026-11-09 19:50 — promptu/003 decision 40 follows the one-colour rail

**Decided:** nothing new; the owner's EMB-56 change, recorded on the Promptu side. Decision 40 in `embarch-promptu/decisions/chat.md` is amended in place: the rail's icons are one-colour inline SVGs in `currentColor`, bottom placement and Usage-at-top kept, colour emoji added to its Rejected list. `spec.md` §2c no longer names 📚 and 💡; the worker made that edit one byte smaller rather than larger, since `spec.md` is in reserve under the parked `promptu/004`. Leg notes: **I split no Fleet Ready issue this leg.** All 28 are `desk` or `atlas`, the queue already holds five `atlas` and four `desk` tasks beyond this wave, and a split adds depth without scope spread. `--refill-owed` fired on spread only, and no sweep source changed since the `2026-11-09 17:34` marker, so I skipped the sweep.
**Merged:** `agent/promptu/003-decision-40-follows-the-one-colour-rail` (doc only: `b92ffb51`, the worker's `ec956b31` cherry-picked onto `724d0dfa`; the `embarch-promptu` worktree stayed clean and was not pushed). Gate on the merge result: `check-docs.py` 12/12; ownership `promptu` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, gate off by latch (burndown until 2026-11-11 06:00), wave 6; this leg holds 4.
**Least sure about:** nothing material; two lines of prose, and `chat` decision 94 already said the same thing.

## 2026-11-09 19:43 — chat/009 the rail's icons are one-colour SVGs

**Decided:** nothing new; the owner changed his own pick (EMB-56) and decision 94 is amended in place, naming `tasks/promptu/003` for the promptu side. The five rail entries are inline SVGs in `currentColor`; lit and unlit differ by opacity or the theme's colours, with no CSS filter left on a rail icon. The worker also dropped incidental emoji wording from `decisions/promptu.md` and `decisions/readouts.md`. **In this fold I set `promptu/003` `open`**, as its `Unparks when:` named this task, and corrected the worker's state line (`done,` is not a state token; `check-task-state.py` was red on `main` for the minutes between the doc landing and this fold, see below).
**Merged:** `agent/chat/009-the-rail-icons-are-one-colour` (code `468547a`, ff on `f823dc8`; doc `2313f775`, the worker's `212da07f` cherry-picked onto `6d480129`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (257 pass, 0 fail, 75 skipped for want of `EMBARCH_DESK_BIN`), `test:webview` all passed; client names clean; ownership `chat` OK on both branches; `check-docs.py` 12/12 after this fold's fix.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window: nobody has looked at the five icons in a light and a dark theme, and the shapes are the worker's own 16 px strokes, which may want a design pass. Nothing installed.
**Budget:** PROCEED, gate off by latch (burndown), wave 6.
**Least sure about:** **I pushed the doc cherry-pick with `check-docs.py` red**, because I piped the gate through `tail -1` in an `&&` chain, the exact shape `.claude/leg.md` warns about for `fold-commit.py`. Only `check-task-state.py` was red, on one malformed state line, and this fold fixes it; but the landing step should read the gate's exit status, not a pipe's.
**Leg close (next leg, read this first):** 4 of 4 units (`atlas/039`, `promptu/002`, `desk/007`, `chat/009`) plus `atlas/038`'s recovery fold, from a leg that died at 17:54 after landing it. Leg began at `3ffc8e00`. **Burndown is latched with `gate=off`** (until 2026-11-11 06:00), so `usage-budget.py` checks nothing and says PROCEED at wave 6; a real 429 is still the stop signal. Queue: dispatchable work in `atlas` (040–044), `chat` (008, 010–013, 015–017), `desk` (008–011) and `promptu` (003, just unparked), four scopes. **`chat/017` and `promptu/003` were unparked this leg**; `chat/014` still waits for `chat/012`, `chat/018` for `chat/017`. Fleet Ready holds 28 (10 desk, 18 atlas); EMB-82 asks for a new decision and EMB-76 is half outside the fleet, so leave both for a normal leg, and EMB-40 needs a datasheet the fleet does not have. New size debts: `promptu/004` (blocked, due 2026-11-23) and `desk/011` (open, due 2026-11-23). **`core/112` is due today and falls overdue tomorrow**: the first leg after midnight spends its first unit on it, and also owes the day fold and `check-client-names.py --suite --history`. Workers in this leg twice left a state line the gate refuses (`promptu/002` and `desk/007` still `claimed`, `chat/009` `done,`), so check the task's state line before cherry-picking. Filed EMB-104 (Backlog): Fleet Ready has no one-line listing. Bench: not checked; burndown takes no bench task.

## 2026-11-09 19:33 — desk/007 an issue read says when comments were cut

**Decided:** nothing new; the worker chose a `skip` parameter on `linear_get_issue` (and `GET /linear/issue/{key}?skip=N`) over a second tool and recorded it as an amendment to decision 59, as my dispatch note asked under burndown. Both account paths now page comments 50 a request up to 500, return the newest 25 oldest first with `comments_total`, `comments_truncated`, `comments_capped` and a `comments_note` naming the next `skip`. The worker filed `tasks/desk/011-compact-desk.md` (`decisions/agents.md` 11,455 of 12,288 B), `open`, `In flux: no`, due 2026-11-23. I set the task `done` in this fold; the worker had ticked every box and left my claim line.
**Merged:** `agent/desk/007-an-issue-read-says-when-comments-were-cut` (code `3141190`, ff on `0c44f9d`; doc `15f59412`, the worker's `84a8c0ef` cherry-picked onto `816f2c92`). Gate on the merge result: `cargo build`, `cargo test` (193), `clippy --all-targets -D warnings` green; client names clean; `check-docs.py` 12/12; ownership `desk` OK on both branches.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live Linear check, written into the task and decision 59: which end of a thread of more than 25 comments each account type keeps is assumed newest-first, not measured. Nothing installed or deployed.
**Budget:** PROCEED, gate off by latch (burndown), wave 6.
**Least sure about:** every issue read now pages all comments, including the description-only callers (`linear_edit`'s draft checks, search, the brief), so a long thread costs up to ten requests where it cost one; the reviewer found no decision against it, but nobody measured it.

## 2026-11-09 19:32 — promptu/002 the pass plans for work that will outgrow one context window

**Decided:** nothing new; decision 41 was the owner's design and now reads built for the Promptu side. The pass takes `promptu prep --context-usage <0-100>` (over 100 exits 2), judges whether the work runs at high context, and names one of `workers`, `handoff`, `compactions`, `decimation` as one line in Who does it; the footer carries `way=<name>` only when one is picked. The input is `docs/contract.md` §7.10. **In this fold I set `chat/017` `open`**, as its `Unparks when:` named this task, with the flag's name in its state line. The worker filed `tasks/promptu/004-compact-promptu.md` (`spec.md` 9,564 of 10,240 B), `blocked` with `In flux: yes`, due 2026-11-23.
**Merged:** `agent/promptu/002-the-pass-plans-for-high-context-work` (code `95f0d69`, ff on `94181bb`; doc `71b1dfb0`, the worker's `5a71d01a` cherry-picked onto `35f430ef`). Gate on the merge result: `cargo build`, `cargo test` (67 + 17 + 28), `clippy --all-targets -D warnings` green; client names clean; `check-docs.py` 12/12; ownership `promptu` OK on both branches.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed Promptu on this machine runs the old binary until the owner rebuilds it; nothing here deploys.
**Budget:** PROCEED, gate off by latch (burndown), wave 6.
**Least sure about:** `promptu/004` parks `spec.md` on `In flux: yes` until `chat/017` and decision 30's build step 4 settle; `DOC-BUDGET.md` says a verbatim split restates nothing, so whoever reaches its due date should read it as splittable now rather than wait for the flux to end.

## 2026-11-09 19:30 — atlas/039 a step marker in a rule is not a numeric claim

**Decided:** (1) **Split five more Fleet Ready issues** (`bf619a2a`): EMB-16 into `desk/009`, EMB-18 into `desk/010`, EMB-31, 39 and 44 into `atlas/042`–`044`, each checked against `main` first (the desk and atlas code paths each names still read as the issue says). Announced at `ts` `1794277712.673199`. **Left in Fleet Ready on purpose:** EMB-82 asks for a new `embarch-desk` decision, which burndown withholds; EMB-76 has half its Done when in a repo the fleet does not work; EMB-40 needs the one real datasheet that showed it. 28 remain (10 desk, 18 atlas). (2) For the unit itself, nothing: `NOT_CLAIMS` gains a bare one- or two-digit integer in parentheses, which `rm.py` also picks up through `blank_not_claims`; `DESIGN.md` says so.
**Merged:** `agent/atlas/039-a-step-marker-in-a-rule-is-not-a-numeric-claim` (code `335939a`, ff on `50a9a15`; doc `a61362e6`, the worker's `e3084a54` cherry-picked onto `bf619a2a`). Gate on the merge result: `pytest` 657 passed, 3 expected skips, client names clean, `check-docs.py` 12/12; ownership `atlas` OK on both branches.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, gate off by latch (burndown), wave 6, 4 in flight.
**Least sure about:** a bare `(12)` meant as a real value is now ignored by check M too, and only `(100)` and up still counts; the reviewer called it a narrow loss of coverage rather than a contradiction, and no test pins where a real two-digit bare value appears in a distilled section.

## 2026-11-09 19:26 — atlas/038 a spaced minus and a thousands separator parse as one number

**Decided:** nothing new; the worker refined atlas `DESIGN.md` decision 2's number-reading note in the same diff. **This fold is recovery.** The leg that started 17:47 split six Fleet Ready issues (`273ed317`: EMB-36, 37, 38, 41 into `atlas/038`–`041`, EMB-13 and 9 into `desk/007`–`008`), claimed four tasks, dispatched at 17:54, landed `atlas/038`'s code and doc to `main`, and died without a tick, a fold or a log entry. The listener's ticks resumed at 18:58; I took the lock at 19:20. Recovery: its three other claims (`chat/009`, `desk/007`, `promptu/002`) had clean worktrees and no commits anywhere, so I removed the worktrees, deleted the empty local branches and reclaimed them to `open` (`2bc10797`), then claimed and dispatched them again in this leg.
**Merged:** `agent/atlas/038-a-spaced-minus-and-a-thousands-separator-parse-as-one-number` (code `50a9a15`, ff on `a034cc6`; doc `3ffc8e00`), both landed by the dead leg. I re-ran the gate on the merge result: `pytest` 656 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean. The task now reads `done` and this fold retires it; one changelog fragment assembled into `history/atlas.md`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, the usage gate OFF by latch (`gate=off`, `mode=burndown` until 2026-11-11 06:00), suggested wave 6; this leg holds 4.
**Least sure about:** whether the dead leg ran its own gate before landing; I re-ran it after the fact on `main`, which is the same tree, so the code is checked, but any reasoning it did about the split of the six issues died with it.

## 2026-11-09 17:45 — chat/007 an agent hands its chat to a fresh session

**Decided:** nothing suite-wide; decision 103 was the owner's design and the worker built it as written. A `handoff(prompt)` tool on the panel's own MCP server (`src/handoff.ts`), declared whenever `embarchChat.handoff` (machine scope: `card` default, `immediate`, `off`) is not `off`. Continue starts a fresh session on the same item in the same panel, keeping mode (never looser), model, effort and Ultracode, with the old timeline above a divider holding the prompt; Stay answers the call. Decision 103 now reads built, with an as-built note including one known limit: after a window reload the fresh chat shows only its own transcript, because the copied history lived in memory. **In this fold I set `promptu/002` `open`**, as its `Unparks when:` named this task.
**Merged:** `agent/chat/007-an-agent-hands-its-chat-to-a-fresh-session` (code `f823dc8` on `bce5ac7`, ff; doc `ee7e48bf`, the worker's `5a6fc140` cherry-picked onto `1e8be150`). Gate on the merge result: `npm ci`, `build`, `typecheck`, `test` (257 pass, 0 fail, 75 skipped for want of `EMBARCH_DESK_BIN`), `test:webview` green; ownership `chat` OK on both branches; client names clean; `check-docs.py` 12/12. One new `features.d` row assembled.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owed to a live window, written into the task: a real `claude` calling `mcp__embarch-chat__handoff` (the wire tests call the tool through `mcpServer` directly, there is no recorded fixture), and the tab and sidebar re-pointing in a real VS Code window. Nothing installed or deployed.
**Budget:** PROCEED at the boundary, 5-hour 64.0%, weekly 11.0%.
**Least sure about:** the worker ran `test/host.test.mjs` with the desk binary as an extra and saw 5 failures it says also fail on a clean baseline (diff-tab reject, plan comments, always-allow, queued message on reload, new chat reloaded). I did not reproduce the baseline, and nobody has filed them; the regular gate skips that file.
**Leg close (next leg, read this first):** 4 of 4 units (`desk/006`, `promptu/001`, `ui/105`, `chat/007`), the first wave dispatched at once at wave 6. Leg began at `5b8d8362`. **Fleet Ready still holds 39 issues: 14 `desk` (EMB-9, 11–19, 48, 72, 73, 76, 82) and 25 `atlas` (EMB-21–27, 29–42, 44–47).** Splitting them is the next leg's first job and its only source of scope spread: the task queue now holds dispatchable work in `chat` (008–013, 015, 016) and `promptu/002` alone. **Reconcile the desk issues against decision 77 before writing a task** (it landed today as EMB-94): EMB-15, "the open desk is one global switch", reads as already answered by it, and EMB-12, 16 and 48 touch the code it rewrote. EMB-73's last box asks for an `embarch-dev-workflow.md` §6 change, which no agent may write. And read each issue's named files on `main` first: `ui/105`'s issue was two-thirds stale. Blocked chain: `chat/017` waits for `promptu/002`, `chat/018` for `chat/017`, `chat/014` for `chat/012`, `promptu/003` for `chat/009`; whoever folds the first sets the second `open`. **`core/112` falls overdue tomorrow** and takes the first unit of the first leg after midnight. **The 5-hour window went from 0% to 64% during this leg**, so the next leg may meet the 90% HOLD inside its own run. Bench: neither role attached. No `suite` task announced, nothing deployed, the owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone.

## 2026-11-09 17:37 — ui/105 the README points at the chat's launcher

**Decided:** nothing. Most of EMB-69 was already true on `main` when the worker started: `vscode-extension/` is deleted, so its README does not exist, and the architecture sketch already names `embarch-ui.service`. What remained: the README's launcher section now names `embarch-chat` as the launcher's home, its four commands, and its status bar states. The task named three states; `embarch-chat`'s `launcher.ts` has a fourth, `embarch-ui (not installed)`, and the README lists it. No `embarch-doc/embarch-ui/` change; `spec.md` already agreed.
**Merged:** `agent/ui/105-the-readmes-point-at-the-chats-launcher` (code `877a042`, ff; doc `6164b79d`, the worker's `1f1a082e` cherry-picked onto `e222ce57`, task file and changelog fragment only). Gate on the merge result: README only, so no `cargo`; ownership `ui` OK on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED (wave 6).
**Least sure about:** the split itself: I wrote the task from the issue's text without checking `main`, and two of its three targets had already been fixed. The next leg splitting 39 more issues should read the named files before writing a task.

## 2026-11-09 17:36 — promptu/001 a header-less memory index may take its first header

**Decided:** nothing. The first `promptu` unit the fleet has run; every gate script already knew the scope. Check I2 on a `MEMORY.md` with no `## <domain>` header now says the writer may add the first one in the same write; with headers present the message is unchanged. Decision 21 gains one sentence saying so; the rule itself and I3 are untouched.
**Merged:** `agent/promptu/001-a-header-less-memory-index-may-take-its-first-header` (code `94181bb` on `866a24e`, ff; doc `0b519941`, the worker's `f76382b0` cherry-picked onto `c8f4b929`). Gate on the merge result: `cargo build`, `cargo test` (67 + 17 + 26), `clippy --all-targets -D warnings` green; ownership `promptu` OK on both branches; client names clean; `check-docs.py` 12/12. First `history/promptu.md`, created by the assembler.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The installed hook on this machine still runs the old binary until the owner rebuilds or reinstalls it; nothing here deploys.
**Budget:** PROCEED (wave 6).
**Least sure about:** nothing material; the change is one message string and its test.

## 2026-11-09 17:34 — desk/006 four desk docs leave the reserve by verbatim split

**Decided:** (1) **Split 14 of the 54 Fleet Ready issues, not all 54**, into 16 tasks (`cef37baf`): `chat/007`–`018`, `promptu/001`–`003` (the first `promptu` tasks ever), `ui/105`. EMB-65 and EMB-56 each span two repos and split into a chat and a promptu task. Five are `blocked` on the task each waits for: `chat/014` on `012`, `promptu/002` on `chat/007`, `chat/017` on `promptu/002`, `chat/018` on `chat/017`, `promptu/003` on `chat/009`. **Whoever folds a dependency sets its dependant `open` in the same fold**, or `check-task-state.py` refuses a `blocked` task naming a task no longer in the queue; each dependency's task file says so. The 14 `desk` and 25 `atlas` issues stay in Fleet Ready for the next legs: reading 110 KB of issues and writing 54 task files in one leg is the context a four-unit bound exists to prevent. Announced at `ts` `1794270556.536659`, no reply. (2) **desk/006's three `In flux: yes` files were dispatched split-only, the field left as written.** Decision 77 landed today (desk `0c44f9d`, doc `5b8d8362`), which is the condition the field named; `DOC-BUDGET.md` makes a verbatim split the default remedy whatever the flux. My dispatch note in the task says so. (3) **`core/112`, due today, did not take the first unit**: `check-doc-size.py --due` reads 0 overdue on its due date, so it is overdue from tomorrow and takes the first unit of the first leg after midnight.
**Merged:** `agent/desk/006-compact-desk` (doc `ab1d2c96`, the worker's `b55848d2` cherry-picked onto `93cd09a7`; no code). `decisions/cockpit.md` 12,062 → 6,100 B (57, 58, 60, 61, 76 to new `decisions/hand.md`), `decisions/desks.md` 12,169 → 8,306 B (62–64 to new `decisions/tiles-after-send.md`), `interfaces.md` 14,426 → 10,498 B (the embarch-chat route table to `interfaces/chat-routes.md`), `spec.md` 9,219 → 8,379 B (constants rows to `spec/constants.md`), PAID. I compared removed against added lines: identical except index rows and links re-pointed one level up. Gate on the merge result: `check-docs.py` 12/12, ownership `desk` OK.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at start (5-hour 0.0%, weekly 6.0%, wave 6).
**Least sure about:** `spec.md` sits 660 B under its reserve line and fourteen desk issues are waiting; the next desk unit that adds a constant will likely cross it again. The reviewer noted `embarch-ui/spec/tabs.md` still links desk decisions 57 and 64 to their old files, where pointer stubs now stand; meaning survives, not filed.
**Leg notes (this leg, first unit):** spawned with the pump latched (17:21), no stop marker, no owner message in the channel. Step 0 found no claims, no worker worktrees, no mid-merge; leg began at `5b8d8362`. Bench refreshed: neither `dev-bench` nor `dut` attached, so `api/059`, `dev-bench/035`, `038` stay `open`. `finish` moved nothing. Day-folded 2026-11-07 (4 units) by a log-folder and rolled 2026-11-04 to `log-archive/`. `check-client-names.py --suite --history` clean on all 16 repos. The owner's dirty `embarch-fleet/scripts/fleet-pump.py` left alone. First wave dispatched at once: `desk/006`, `chat/007`, `promptu/001`, `ui/105`. `--refill-owed` fired on spread only (tasks in `chat` alone); no marker line existed, so I swept: the one source changed since the 2026-11-07 sweep is `5b8d8362`, which deletes an answered `embarch-desk/open.md` question. Spread sweep: nothing filed (2026-11-09 17:34). The spread the queue lacks is in Fleet Ready (desk, atlas), and splitting it is the next leg's first job.

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
*Days 2026-11-04 to 2026-11-04 rolled to [log-archive/supervisor-log-2026-11-04-to-2026-11-04.md](log-archive/supervisor-log-2026-11-04-to-2026-11-04.md).*
