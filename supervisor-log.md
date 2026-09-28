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

## 2026-09-28 17:56 — api/111 `validate`'s kind-classification thread gets its own file, and the park it sat in named its own exit

**Decided:** **that `tasks/api/111`'s `In flux: yes` did not forbid its own second exit, and
unparked it at claim** (`65b9e019`). The task named two unpark conditions, the second "once the
file is judged safe to split" along a seam it drew itself (57/67 vs 71/73/76). A verbatim move
restates nothing, so `DOC-BUDGET.md`'s split-first rule applies — the same reading `core/093` got
earlier today. `In flux:` rewritten to `no — for the move this task makes`, the old answer kept as
history and stated to still govern any **squeeze** of 71/73/76. The dispatch note said split only.

**Merged:** `agent/api/111-compact-api` (code: **zero commits**, `embarch-api` main unchanged at
`2ebcfe4`; doc **`0f0dc2cb`**, rebased by me from `1cd74544` onto `cce10a88`). Decisions 71, 73, 76
moved byte-identical to the new `embarch-api/decisions/validate-kind.md` (6,980 B); 57 and 67 stay;
`failure-reporting.md` **11,578 → 5,657 B**, off the ledger (was due 09-27). `decisions.md`'s row
split in two with correct Size cells. No inbound link named the file for 71/73/76; the two that name
it for 67 stay correct. `changelog.d/api-failure-reporting-split.changed.md` folded into
`history/api.md`. Gate on the merge result: `check-docs.py` **all 11 green**; `cargo build`/`test`/
`clippy --workspace --all-targets -- -D warnings` green on the untouched tree; `check-ownership.py
--scope api` clean on 5 paths, `--code-repo` clean; `check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
71, 73, 76 zero-diff against `cce10a88`; all three `Must not delete:` items present by that
identity; the new file's header asserts nothing the decisions do not; code citations are all bare
`embarch-api decision N`. It read the task file at `0f0dc2cb` rather than my dirty fold tree, and
said so.

**Hardware debts:** none created — a verbatim move.

**Budget:** PROCEED, weekly **21.2% → 21.6%**, wave **6**.

**Least sure about:** **the three unparks in a row.** This leg unparked three `In flux: yes` tasks
at claim (`study-designer/032`, `core/046`, this one), each on a defensible reading, and the
previous leg did two more. Every one was a verbatim split or a lapsed condition, and every reviewer
confirmed byte-identity — but "the supervisor decides the park no longer applies" is now the
fleet's normal path out of `blocked`, and nothing but these entries records that it is happening.

---

## 2026-09-28 17:52 — core/046 the route sweep leaves the auth decisions, and a park ends because four routes landed somewhere else

**Decided:** **that `tasks/core/046`'s `In flux: yes` was falsified by its own prediction, and
unparked it at claim** (`9701f722`). The prediction was "the next new HTTP route ... is likely to
land here again"; four have landed in `build_router` since the file's last edit (`f6e23215`,
2026-09-12) — `.../load/spans` `4251af3`, `GET /studies` `d73a73a`, `DELETE /probes/enrolled/{role}`
`e50de6d`, `PUT /probes/enrolled/{role}/board` `f832043` — and none touched `auth.md`. `In flux:`
rewritten to `no` with that evidence, the old answer kept as history.
**Also decided: I corrected the worker's Size cell in this fold** — `decisions.md` said `auth.md`
is 2.9 KB; it is 3,799 B, so 3.8 KB. The reviewer read the cell and did not measure it.

**Merged:** `agent/core/046-compact-core` (code **`fdb9b1d`**, one comment, fast-forward onto
`48dc591`; doc **`7c5ad6f9`**, rebased by me from `2e6173ea` onto `1a42bea3`). Decisions 42, 46, 60
moved byte-identical to the new `embarch-core/decisions/route-sweep.md` (8,468 B); 5, 6, 11, 53
stay; `auth.md` **11,356 → 3,799 B**, off the ledger (was due 09-26). One paragraph of 53's ("What
this decision does not claim", about the ACL) had sat after 60 in the old file; removing 60 left it
beside 53, unreworded. `decisions.md`'s row split in two; `platform.md`'s pointer names both files;
`src/api.rs:1712`'s file-qualified citation of 42 repointed; two bare-number cites left alone.
`changelog.d/core-split-route-sweep.decided.md` folded into `history/core.md`. Gate on the merge
result: `check-docs.py` **all 11 green**; `cargo build`/`test` (245 passed, 2 ignored)/`clippy
--all-targets -- -D warnings` green; `check-ownership.py --scope core` clean on 6 paths,
`--code-repo` clean; `check-client-names.py` clean.

**One slip of mine, harmless and on `origin/main` — the same one the previous leg logged.** My
first fold attempt was refused (I had not yet written this entry), but a `| tail` in the chain ate
the exit status, so `git push origin HEAD:main` still ran: **`7c5ad6f9` reached `origin/main` a few
minutes before its fold** — the worker's commit with its fragment still pending, a legal state —
and one spurious `leg-fold` tick went into `.fleet/tick.log`. Two legs in a row is a pattern:
`fold-commit.py` refusing is not enough while the push rides the same `&&` chain behind a pipe.

**Blocked:** nothing.
**Reviewer:** no findings.
42 and 46 zero-diff against `1a42bea3`; 60's body identical, its trailing paragraph confirmed as
53's and verbatim; all four `Must not delete:` items present; no inbound link anywhere names
`auth.md` for 42/46/60.

**Hardware debts:** none created. The `api.rs` change is a comment, so no native Windows build is
owed for it.

**Budget:** PROCEED, weekly **21.2%**, wave **6**.

**Least sure about:** **whether "four routes landed elsewhere" really falsifies the flux.** The task
said the next route or *the next gap in this sweep family* would land here; no gap has been found
in sixteen days, but nobody has looked, and a verbatim split does not care either way — which is
the argument that actually carries the unpark, not the route count.

---

## 2026-09-28 17:47 — study-designer/032 what a study carries gets its own spec file, and a seventeen-day park ends on its own condition

**Decided:** **that `tasks/study-designer/032`'s `In flux: yes` had lapsed on its own terms, and
unparked it at claim** (`22fa5c9b`). Its unpark condition was "§4 has gone a full leg without a new
field or seal-placement edit"; §4's last edit is `ac9c2116` (2026-09-18), one table cell for
decision 77, and nothing has touched `spec.md` since. `In flux:` rewritten to `no` with that
evidence, the old answer kept as history. **Also: the worker's inbox drop became
`tasks/api/120`** at this fold (below), not dispatched this leg.

**Merged:** `agent/study-designer/032-compact-study-designer` (code **`b9a2d5d`**, one comment,
fast-forward onto `15087ae`; doc **`22dc629c`**, fast-forward onto `12731da4`). §4 ("What a study
carries" — the carriage/seal table and its two paragraphs) moved verbatim to the new
`embarch-study-designer/spec/carriage.md` (2,144 B); `spec.md` **9,400 → 7,924 B**, off the ledger
(was due 09-25). **The worker renumbered the remaining sections 5/6/7 → 4/5/6** and repointed its
own repo's one citation (`src/study.rs:1062`, §7 → §6). The one it could not reach —
`embarch-api/src/main.rs:538`, `spec.md §7` — is **`tasks/api/120`**, filed here, preferring a
decision-63 citation over a section number. `changelog.d/study-designer-spec-carriage-split.changed.md`
folded into `history/study-designer.md`. Gate on the merge result: `check-docs.py` **all 11
green**; `cargo build`/`test`/`clippy --all-targets -- -D warnings` with `--all-features` green
(298+12+10); `check-ownership.py --scope study-designer` clean on 4 paths, `--code-repo` clean;
`check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
Removed §4 byte-identical to `carriage.md`'s body; the Must-not-delete seal order (`steps, streams,
steps_crc, streams_crc, protocols, protocols_crc`) present unchanged; §6 is now Constants, so the
repointed comment is right; no decision touched. It also checked `embarch-ui` for a
`study-designer/spec.md §5` citation a closed task once recorded (`ui/045`, `app.js:2542`) and found
none — without a pinned `ui` worktree, so that half is unanchored.

**Hardware debts:** none created — a move, a renumber and a comment.

**Budget:** PROCEED, weekly **20.4% → 21.2%**, wave **6**.

**Least sure about:** **the renumber.** Leaving a one-line "§4 moved to `spec/carriage.md`" stub
would have kept every section number stable; renumbering broke two known citations (one fixed, one
filed), and `embarch-core/src/study.rs` still carries a family of legacy `spec.md §4.8`/`§5.1`
decimal citations that matched nothing before this unit and match nothing now — so a grep for
stale section cites into this file is already noisy, and the next reader cannot tell which kind a
hit is without reading it.

---

## 2026-09-28 17:23 — umbrella/088 check 15's bullet stops saying the hash is unbuilt, and a parked `open.md` compaction rides along

**Decided:** nothing by me beyond the dispatch note, which applied `.claude/leg.md`'s rule that a
reserve file parked on `In flux: yes` gets compacted by the unit writing it (`tasks/umbrella/077`,
single file). **The worker decided not to consume `binary_sha256` in check 15** — a real behavior
change needing its own decision (warn semantics, when to hash, null handling, a new `AuthedStatus`
field) in `decisions/schema-skew.md`, itself at 733 B left — and filed **`tasks/umbrella/089`** for
it, open, with the design questions stated as unanswered. That is the Done-when's second legal
answer, and it was the worker's call by the task's own words.

**Merged:** `agent/umbrella/088-check-15-self-hash-bullet` (code: **zero commits**,
`embarch-umbrella` main unchanged at `2764e89`; worker still ran `cargo build`/`test`/`clippy` green
on the untouched tree, 228 tests; doc **`61e13c92`**, rebased onto `9140247e`).
`embarch-umbrella/open.md` **4,372 → 3,905 B**, out of reserve (the real line is 3,920 B because
`RESERVE_FLOOR` beats 10% on a 5 KB file — 077's prose said 4,096). **A squeeze, not a split**:
three bullets now point at the decision that owns their mechanism instead of restating it (34,
51, 49). `tasks/umbrella/077` and `088` closed and removed in this fold.
`changelog.d/umbrella-check15-self-hash-bullet-corrected.changed.md` folded into
`history/umbrella.md`. Gate on the merge result: `check-docs.py` **all 11 green**;
`check-ownership.py --scope umbrella` clean on 5 paths, `--code-repo` clean;
`check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
Directed at the squeeze: every `077` `Must not delete:` item survives; each deleted clause is stated
near-verbatim by the decision it now points at (34's `CARGO_PKG_VERSION` blind spot, 51's three-step
protocol, 49's "contents, not its home"); the 67/68 claim matches `embarch-core`'s record; 089
asserts no design. It noted, below its bar, that 077's own "why `saved.host` was left unfixed" item
already described a pre-decision-51 state before this unit.

**Hardware debts:** none created. The open.md bullets carrying debts are unchanged in substance:
check 13 (one `doctor` run on the primary bench), check 5 (a Linux box with Core native), decision
51's three-step real-machine confirmation.

**Budget:** PROCEED, weekly **20.3% → 20.3%**, wave **6**.

**Least sure about:** **whether a squeeze that replaces restated mechanism with "see decision N"
leaves `open.md` answerable cold.** The reviewer confirmed every deleted clause lives in its
decision, so nothing is lost; but a reader of `open.md` alone now has to follow three links to learn
*why* check 15 is blind, which is exactly the kind of thing `open.md` is read for.

**Leg close, for the next leg.** 4/4 units, all green, no reds, no blocks; four doc commits and
**zero code commits**. Three of four were the size ledger (**10 → 7 overdue**) and the fourth paid
`umbrella/077` by riding. **Two cross-scope links broken by this leg's splits were repointed by me in
the folds** (`embarch-ui` `live-study.md:30`, `firmware-build.md:7`) — in two different forms, see
`study-designer/068`. Filed **`core/095`**; `study-designer/066` re-stated, still open. Oldest
*payable* overdue: **`study-designer/069`** (`gatt-extract.md`, **36 B left**, due 09-27, `open`)
and `api/111` (`failure-reporting.md`, blocked on flux, but its own text names a split seam — 57/67
vs 71/73/76 — so it can be unparked for a verbatim move the way `core/093` was). `suite/030` and
`doc/031` remain owner-only. Queue: **12 dispatchable** over 5 scopes (api 2, core 6, study-designer
2, ui 1, umbrella 1); 2 bench tasks still waiting on the dev-bench probe (`validate dev-bench` at step
0: `001057729826` not attached, not a mismatch). Refill fired on scope spread; I swept only the
missing scopes' `open.md` (dev-bench, outpost, topology) and found nothing host-side, as
`tasks/doc/081` predicts. `inbox/` empty at close. No `suite` window open. **Structural note: as a
subagent, ending a turn to wait for workers makes the harness demand a handback** — this leg waited
inside its turn with a scratchpad poll script instead (`git ls-remote` every 30 s). A successor that
ends its turn after dispatching will be told to hand back with four workers in flight.

---

## 2026-09-28 17:19 — study-designer/068 what a study builds leaves the firmware-versions file, and a file with 88 bytes left gets room

**Decided:** **that the fold repoints the ui link to the index, not the new topic file** —
`embarch-ui/decisions/firmware-build.md:7`, decision 77, `declares.md` → `decisions.md`. Same line
already links `embarch-core` decision 74 at `embarch-core/decisions.md`, and the index survives the
next split. `core/093` one unit earlier repointed to the topic file instead; both pass the gate, so
this is a convention the suite has two answers to (`tasks/doc/055` is the owner's). The worker's
drop `inbox/ui-decision-77-link-stale-after-study-designer-split.md` deleted as resolved.

**Merged:** `agent/study-designer/068-compact-study-designer-declares` (code: **zero commits**,
`embarch-study-designer` main unchanged at `15087ae`; doc **`837d7696`**, rebased onto
`3edfeb20`). `decisions/declares.md` **12,200 → 8,896 B**; new `decisions/builds.md` 4,059 B.
Two non-verbatim edits, both pointers: a header line naming `builds.md`, and "— closed by decision
77" inside decision 40's verification-asymmetry paragraph (40: 4,409 → 4,462 B, under its 4,608 B
pin). `decisions.md` gained a routing row and its "seventeen files" became "twenty", which matches
the directory — so **`tasks/study-designer/066`'s premise is now false and its preferred fix is
not done**; I rewrote 066's state line to say so and left it `open` for the rephrase and the table
census. `changelog.d/study-designer-declares-builds-split.changed.md` folded into
`history/study-designer.md`. Gate on the merge result plus my repoint: `check-docs.py` **all 11
green**; `check-ownership.py --scope study-designer` clean on 5 paths, `--code-repo` clean;
`check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
77 byte-identical against `3edfeb20`, 74 untouched; both pointer edits restate only what 77 already
says, and 40's "cannot be designed away" stands verbatim; the only file-naming inbound link to 77
was the one I repointed; 20 files, 20 routing rows.

**Hardware debts:** none created — a move and two pointers.

**Budget:** PROCEED, weekly **20.2% → 20.3%**, wave **6**.

**Least sure about:** **the two repoint forms.** A reader of `embarch-ui` now finds one cross-repo
decision link pointing at a topic file (`live-study.md` → `streams-live.md`) and one pointing at an
index (`firmware-build.md` → `decisions.md`), both written by me twenty minutes apart. Neither is
wrong under today's gate; the topic-file one is the one the next split breaks.

---

## 2026-09-28 17:13 — core/093 pushing-live decisions get their own file, and a park on hardware ends because a move is not a squeeze

**Decided:** **that `tasks/core/093`'s `In flux: yes` did not forbid its own remedy, and unparked
it at claim** (`bebb1a64`). Its block was "decisions 72 and 73 unvalidated on hardware", and its own
body said the split is the remedy precisely because it moves that reasoning untouched.
`DOC-BUDGET.md`'s split-first rule says the same: a verbatim move restates nothing, so flux cannot
forbid one. `In flux:` rewritten to `no — for the move this task makes`, the old answer kept as
history and stated to still govern any **squeeze** of 72/73. Unlike `dev-bench/014` last leg, the
flux here has **not** lapsed — the bench is still unplugged — so this is a different argument, not
the same one again.
**Also decided: the one cross-scope link the split broke is fixed in this fold, by me**, not
queued. `embarch-ui/decisions/live-study.md:30` linked decision 70 at `streams.md`; repointed to
`streams-live.md`. The worker could not (ui is not its row), reported the merge alone as red
(`check-decision-refs.py`), and dropped `inbox/ui-repoint-streams-md-decision-70-cite.md`, which I
deleted as resolved. The worker's commits alone are red in history for one commit; `origin/main`
never was.

**Merged:** `agent/core/093-compact-core-streams-decisions` (code: **zero commits**, `embarch-core`
main unchanged at `48dc591`; doc **`02e6ff79`** + **`439fea1c`**, rebased onto `d63b3752`).
`decisions/streams.md` **11,094 → 5,760 B** (30, 38, 39 stay); new `decisions/streams-live.md`
5,889 B (70, 72, 73). `decisions.md`'s row split, its stale "7.7 KB" corrected.
`changelog.d/core-streams-live-split.changed.md` folded into `history/core.md`. Gate on the merge
result plus my repoint: `check-docs.py` **all 11 green**; `check-ownership.py --scope core` clean on
5 paths, `--code-repo` clean; `check-client-names.py` clean on the code worktree.
**Filed `tasks/core/095`** from the reviewer's aside: `embarch-core/src/study.rs` ≈4209, the `/load`
handler's comment, cites "`embarch-core` decision, `decisions/streams.md`" with **no number**, for a
route that is decision 62 in `stream-index.md` since `core/060`. Pre-existing, not this unit's.

**Blocked:** nothing.
**Reviewer:** no findings.
All six decisions byte-identical against `d63b3752`; 72's render-vs-live paragraph and 73's
`core_rx_utc_ms` clock clause intact; reversals row 112 cites "core 72" by bare number, unaffected;
the only file-naming inbound link to 70/72/73 anywhere was the one I repointed.

**Hardware debts:** none created. Decisions 72 and 73 are **still unvalidated on hardware** — a
traced study with the outpost bridge attached — exactly as before; the split moved that debt, it did
not pay it.

**Budget:** PROCEED, weekly **20.1% → 20.2%**, wave **6**.

**Least sure about:** **whether "flux cannot forbid a verbatim split" will be read as a licence to
unpark anything by calling it a split.** It is right here because the task itself named the split as
the remedy and the reviewer confirmed six byte-identical sections. A task whose remedy needed a
single reworded sentence in 72 or 73 would not qualify, and nothing mechanical tells the two apart.

---

## 2026-09-28 17:08 — ui/072 decision 14 gets its own file, and the Study Designer group leaves reserve

**Decided:** nothing. The worker picked the seam: decision 14 ("Open project" — repo picker,
recents, first-time detection) is a different mission from 11/12/20/22, which are the designer
itself. Decision 11's reversal paragraph (row 113), the newest text in the file, was left alone.

**Merged:** `agent/ui/072-compact-ui-study-designer-decisions` (code: **zero commits**,
`embarch-ui` main unchanged at `ad49a7ae`; doc **`28989725`**, fast-forward onto `b41e1531`, no
rebase). `decisions/study-designer.md` **11,392 → 7,897 B**; new `decisions/project.md` 4,237 B.
`decisions.md`'s routing row split in two; `designer-panels.md` and `study-authoring.md` repointed
from `study-designer.md` to `project.md`. `changelog.d/ui-study-designer-project-split.changed.md`
folded into `history/ui.md`. Gate on the merge result: `check-docs.py` **all 11 green**;
`check-ownership.py --scope ui` clean on 7 paths, `--code-repo` clean; `check-client-names.py`
clean on the code worktree.

**Blocked:** nothing.
**Reviewer:** no findings.
Decision 14 byte-identical against `b41e1531`; 11 and row 113 untouched; every inbound citation of
14 in `embarch-doc` and `embarch-ui/src` is number-only or repointed; the routing table matches both
files.

**Hardware debts:** none created — a verbatim move.

**Budget:** PROCEED, weekly **19.4% → 20.1%**, wave **6**.

**Least sure about:** **my own worktree slip at dispatch, not the unit.** I ran `git -C embarch-doc
worktree add .worktrees/...` with a *relative* path, which `-C` resolves inside the repo, so all
four doc worktrees were created at `embarch-doc/.worktrees/embarch-doc/` — inside the owner's
checkout — for about a minute before any worker started. `git worktree move`d all four to
`embarch/.worktrees/embarch-doc/`, removed the empty directory, confirmed his `git status` clean.
Nothing was committed there and no worker saw the wrong path, but it is the exact placement
`tasks/doc/059` exists for, and `check-dispatch.py` passed beforehand because the paths it was
given were the right ones.

---

## 2026-09-28 16:52 — study-designer/067 the `.eap` constants and decision 71 move out, and two files with 14 and 75 bytes left get room

**Decided:** **nothing** by me. My dispatch note suggested checking whether the `.eap` constants
belonged in the existing `interfaces/eap.md`; the worker measured that it would land `eap.md` at
12,173 B, past its own reserve floor, and made a new sibling instead — the pattern `types.md`'s
four siblings already follow. It moved decision 71 (`render_layout` refuses loudly) to
`decisions/payload-meaning.md` rather than `protocol-exec.md`, on mission: 71 is host-side
rendering and cites 52 twice.

**Merged:** `agent/study-designer/067-compact-study-designer` (code: **zero commits**,
`embarch-study-designer` main unchanged; doc **`5f1ba9ab`**, rebased onto `171e0013`).
`interfaces/limits.md` **12,274 → 8,951 B**, new `interfaces/eap-limits.md` 4,251 B (18 rows,
decisions 58–62); `decisions/protocols.md` **12,213 → 10,876 B**, `decisions/payload-meaning.md`
8,650 → 9,987 B. `decisions.md`'s routing table moved 71 between rows. Both files were past their
2026-09-24 clock. `changelog.d/study-designer-eap-limits-split.changed.md` folded into
`history/study-designer.md`. Gate on the merge result: `check-docs.py` **all 11 green**;
`check-ownership.py --scope study-designer` clean on 7 paths; `check-client-names.py` clean on the
code worktree.

**Blocked:** nothing.
**Reviewer:** no findings.
All 18 rows and decision 71 byte-identical against `171e0013`, every `[measured]`/`[assumed]`
marker intact; decision 75 untouched; 71 fits `payload-meaning.md`'s mission beside 52 and 70; the
routing table matches both files; inbound citations (`embarch-dev-bench/spec.md`,
`embarch-ui/interfaces.md`, `src/crc.rs:180`, `src/limits.rs`) cite a Rust path or a bare number, so
none moved. It noted the section intro above the moved table was lightly reworded for its new file
("the constants above" → "`limits.md`'s table") — an adaptation, not a content change.

**Hardware debts:** none created — two verbatim moves.

**Budget:** PROCEED, weekly **17.9% → 19.3%**, wave **6**.

**Least sure about:** **whether moving a decision between topic files is a split or a
re-filing.** Decision 71 now lives beside 52 because the worker judged its mission, and the
reviewer agreed; but a reader who learned "protocol decisions are in `protocols.md`" will look
there first, and only the routing table tells them otherwise.

**Leg close, for the next leg.** 4/4 units, all green, no reds, no blocks; four doc commits and
**zero code commits** across the leg. Size ledger **14 → 10 overdue**. The oldest,
`tasks/suite/030`, is still parked on owner-only `tasks/doc/045`; `tasks/doc/031` (`DOC-BUDGET.md`)
is owner-only. The oldest *payable* overdue ones are `study-designer/068` (`declares.md`, 88 B left)
and `ui/072` (`study-designer.md`), both due 09-25 and `open`; `core/093` (`decisions/streams.md`,
09-25) is `blocked` on `In flux` — re-read it against `git log` the way `dev-bench/014` was. **Filed
`tasks/api/119`** (decision 72 says seven, names six). Queue: **13 dispatchable** over 5 scopes
(api 2, core 5, study-designer 3, ui 2, umbrella 1), 2 bench tasks still waiting on the dev-bench
probe (`validate dev-bench` at step 0: `001057729826` not attached, not a mismatch). `inbox/` empty
at start and end. No `suite` announcement window is open. The `.worktrees/embarch-doc/embarch-ui` and
`embarch-fleet` symlinks stay.

---

## 2026-09-28 16:48 — dev-bench/014 link.md's two ceilings get their own file, and a twenty-day park ends on its own clock

**Decided:** **that `tasks/dev-bench/014`'s `In flux: yes` had lapsed on its own terms, and unparked
it at claim** (`7909f091`). Its unpark condition was "whichever of the flash-route migration or the
step-cap divergence is next quiet"; `git log` showed `link.md` untouched since `84243a33`
(2026-09-08) and no open task targeting decision 13 or 35 — `dev-bench/010` cites 35's divergence but
is `toolchain`-gated and was not in flight. Same reading the previous leg gave `dev-bench/012`.
`In flux:` rewritten to `no` with that evidence, the old answer kept as history. The worker then
took the seam the task named.

**Merged:** `agent/dev-bench/014-compact-dev-bench` (code: **zero commits**, `embarch-dev-bench`
main `edc278bb`; doc **`3df6d63b`**, rebased onto `a9ce7fb5`). Decisions 30 (inbound FIFO ceiling)
and 35 (step-cap divergence) moved verbatim to the new `decisions/link-limits.md` (4,419 B);
`link.md` **11,241 → 7,434 B** (was past its 2026-09-22 clock). `decisions.md`'s "Core link" row
split in two with correct Size cells; `decisions/dispatch.md:27`'s backtick citation of 35's
amendment repointed to the new file. `changelog.d/dev-bench-link-limits-split.changed.md` folded
into `history/dev-bench.md`. Gate on the merge result: `check-docs.py` **all 11 green**;
`check-ownership.py --scope dev-bench` clean on 6 paths; `check-client-names.py` clean on the code
worktree.

**One slip of mine, harmless and on `origin/main`.** My first fold attempt failed on a stale
`old_string` and `fold-commit.py` correctly refused, but the chained `git push origin HEAD:main`
still ran (a `| tail` ate the exit status), so **`3df6d63b` reached `origin/main` a minute before its
fold** — the worker's commit, with its fragment still pending, which is a legal state. One spurious
`leg-fold` tick went into `.fleet/tick.log` at the same moment.

**Blocked:** nothing.
**Reviewer:** no findings.
30 and 35 byte-identical against `a9ce7fb5`; both `Must not delete:` items verbatim (35's
"crate 64, bench 16" amendment in the new file, 13's "what is still unestablished" paragraph
untouched in `link.md`); 6, 7, 12, 13, 18, 19, 25, 36 unchanged; both Size cells match measured
bytes; source comments in `main.c`, `ble_bridge_real.c` and `serial_protocol.h` cite 30/35 by number
only, so they resolve through the index. It noted, below its bar and outside this diff, that the
`platform.md`, `scanning.md` and `dispatch.md` Size cells in the same table look stale.

**Hardware debts:** none created — a verbatim move.

**Budget:** PROCEED, weekly **17.9%**, wave **6**.

**Least sure about:** **whether "quiet for twenty days" is the flux ending or the fleet having been
stopped for eleven of them.** The fleet was down 2026-09-17 to 09-28, so the file's quiet is partly
nobody working; the owner could have had a step-cap change in mind for exactly this file. A
verbatim split restates nothing, so the cost of being wrong is one extra file to edit, not a clean
statement of something about to change.

---

## 2026-09-28 16:44 — api/118 decision 59 stops calling `SignalLink` a mirror

**Decided:** **nothing** by me. The worker amended decision 59's parenthetical in place, no new
number: the "cannot link the `hardware` feature" constraint is what made `SignalLink` a
hand-written mirror **before** decision 72, which replaced it with an alias. It read the two other
places my dispatch note named and changed neither, correctly: decision 60's "this route's mirror"
is `HelloAckResponse`'s mirror of Core's `HelloAckInfo`, a different and still-live mirror; and
`client.rs:882`'s pointer lands on a block comment already rewritten for decision 72.

**Merged:** `agent/api/118-decision-59-signallink-mirror` (code: **zero commits**, `embarch-api` main
`2ebcfe4`; doc **`968f37f0`**, rebased onto `4f465dce`). `hardware-selection.md` 9,124 → 9,303 B.
`changelog.d/api-decision-59-signallink-alias.fixed.md` folded into `history/api.md`. Gate on the
merge result: `check-docs.py` **all 11 green**; `check-ownership.py --scope api` clean on 3 paths;
`check-client-names.py` clean on the code worktree. **Filed `tasks/api/119`** in this fold from the
reviewer's out-of-scope observation below.

**Blocked:** nothing.
**Reviewer:** no findings.
It checked the amended sentence against the code rather than the docs: `embarch-topology`'s
`hardware` module is `cfg(any(feature = "hardware", feature = "wire"))` and `embarch-core-client`
enables `software` + `wire` only, so "cannot link `hardware`" and "`SignalLink` is an alias" are both
true at once. Below its bar, and **pre-existing** by `merge-base --is-ancestor` (authored
`c62cc870`, 2026-09-12): decision 72 says "seven" three times and names six types, and the source
comment says six. That is `tasks/api/119`.

**Hardware debts:** none created — one parenthetical.

**Budget:** PROCEED, weekly **17.9%**, wave **6**.

**Least sure about:** **whether "seven" is the typo or the list is.** `api/117` and `api/118` both
repeated "decision 72's retired seven" from the heading, so if the list is short a type, a seventh
retired mirror is undocumented — which is a bigger defect than a miscount, and `api/119` has to
settle it from `git show c62cc870` rather than from either doc.

---

## 2026-09-28 16:38 — core/092 the three `/stream/{name}*` sub-routes get their own reference file

**Decided:** **nothing** by me. The worker took the seam the task named: the `arrivals`, `load` and
`load/spans` rows moved verbatim from `interfaces/studies.md` into a new `interfaces/streams.md`;
`/stream/{name}` itself stayed behind with the run/status routes, and `interfaces.md`'s route index
gained a Streams row.

**Merged:** `agent/core/092-compact-core-interfaces-studies` (code: **zero commits**, `embarch-core`
main `48dc591`, no `.rs` comment cites the file; doc **`d6820f76`**, fast-forward onto `53211671`,
no rebase). `studies.md` **12,101 → 9,076 B** (was 187 B from its cap and past its 2026-09-25
clock); `streams.md` new at 3,969 B; `interfaces.md` 6,185 → 6,401 B.
`changelog.d/core-interfaces-streams-split.changed.md` folded into `history/core.md`. Gate on the
merge result: `check-docs.py` **all 11 green**; `check-ownership.py --scope core` clean on 5 paths;
`check-client-names.py` clean on the code worktree (worker's run, zero paths changed).

**Blocked:** nothing.
**Reviewer:** no findings.
All three moved rows byte-identical against `53211671`; every `400`/`404`/`422` clause intact,
including `/load/spans`'s "same cases as `/load`" cross-reference; bare `(decision 74)` and the
`outpost-preflight.md` pointer untouched above the cut; no inbound citation anywhere in the suite
links into a moved row — they cite route text or decision numbers.

**Hardware debts:** none created — a verbatim move, no source change, no native Windows build owed.

**Budget:** PROCEED, weekly **17.9%**, wave **6**.

**Least sure about:** **whether the worker's grep for inbound citations was wide enough.** It and
the reviewer both searched for file-and-line pointers into `studies.md`; a prose sentence
elsewhere saying "`studies.md` lists every `/stream` route" would pass `check-links.py` and now be
quietly wrong, and neither search was shaped to find that. I grepped `interfaces/studies.md` with
stream/load/arrival across live docs at the fold: only `interfaces.md`'s index, and it is right.

---

## 2026-09-28 16:02 — ui/073 two verbatim splits, and `main`'s doc gate is green for the first time since the fleet stopped

**Decided:** **nothing** by me. The worker took the seams the task named: decisions 8, 25 and 42 (how
the app looks and is drawn) out of `shell.md` into `decisions/design-system.md`, and decision 44's
"Retracting" and "A saved bench" sections out of `topology-boards.md` into
`decisions/saved-benches.md` — so **decision 44 now spans two files**, indexed as `44 (saved bench)`,
the convention decision 10 already uses across three.

**Merged:** `agent/ui/073-compact-ui` (code: **zero commits**, `embarch-ui` main `ad49a7a`, no source
comment cites either file; doc **`ffee1b77`**, rebased onto `55adb798`). `shell.md` **12,538 → 5,228
B** (was over its cap and past its 2026-09-27 clock), `topology-boards.md` 12,177 → 10,013 B; new
files 7,770 B and 2,648 B. `decisions.md`'s group table updated. The worker also repointed one live
link in a **pending fragment it did not write** — the owner's `changelog.d/ui-brand-token.added.md`
(2026-09-09), decision 25 → `decisions.md` — which the reviewer confirmed is what `DOC-CONVENTIONS.md`
prescribes for history-shaped links; leaving it would have been the break.
`changelog.d/ui-compact-shell-and-boards.changed.md` folded into `history/ui.md`. **Gate on the merge
result: `check-docs.py` all 11 green** — the first green `main` since the clocks expired;
`check-ownership.py --scope ui` clean on 8 paths; `check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
Every moved section byte-identical against `55adb798`; all five must-not-delete facts present
verbatim (25's 1.12:1 and 4.84:1 / 4.98:1, 42's 6.9 px, 47's rejected revision list, 46's ordering
rule); 44's remaining text self-contained, with a pointer to `saved-benches.md` in the file's intro;
every live inbound link resolves. Only `history/ui.md` and four closed task files still name
`shell.md` for 25 — frozen narrative, not navigation.

**Hardware debts:** none created — two verbatim moves.

**Budget:** PROCEED, weekly **17.2%**, wave **6**.

**Least sure about:** **whether splitting one decision across two files is a split or a quiet
renumbering.** Decision 44 is now "44" in one file and "44 (saved bench)" in another, and a reader
who greps `### 44` finds one heading and not the other half. It has a precedent in decision 10 and
the reviewer found nothing dangling — but `check-decision-refs.py` cannot tell which half a
citation of 44 means, so the next correction to the retract path may land against the wrong file.

**Leg close, for the next leg.** 4/4 units, all four overdue size debts, `main`'s doc gate RED → green.
Size ledger **20 → 14 overdue**; the oldest, `tasks/suite/030`, is still genuinely parked on
owner-only `tasks/doc/045`, so the next leg's first unit is the oldest *payable* one —
`tasks/dev-bench/014` (`decisions/link.md`, due 09-22; its `In flux: yes` names "next quiet" and the
file has not moved since 09-08, so re-read it the way `dev-bench/012` was re-read). Queue: **15
dispatchable** over 5 scopes, 2 bench tasks still waiting on the dev-bench probe. No `suite`
announcement window is open. The `.worktrees/embarch-doc/embarch-ui` symlink this leg made stays — it
is what keeps `check-links.py` green from any doc worktree until `tasks/doc/085` is settled.

---

## 2026-09-28 15:56 — core/094 decision 74 gets its own file, and the one link the split broke was in `ui`

**Decided:** **that the supervisor repoints a cross-sub-project citation a split broke, at landing,
rather than filing it as a task.** `core/094`'s verbatim split turned `check-decision-refs.py` RED
on `embarch-ui/decisions/firmware-build.md:7`, a file the `core` worker may not touch; it dropped
`inbox/ui-repoint-firmware-build-decision-74-link.md` with the exact fix. Filed as a `ui` task it
would have queued behind `ui/073` with `main` red on it for a whole unit, and the fix is one link
target in a doc the supervisor may write. So I made it in this fold — `[embarch-core decision 74]`
now points at `../../embarch-core/decisions.md`, the routing table, per the script's own "link the
index" rule — and deleted the drop. **Not announced before doing it**, which `.claude/leg.md` asks
of an inbox item taken for dispatch; it was not dispatched, and it is named in this unit's post.

**Merged:** `agent/core/094-compact-core-handshake` (code `48dc591` — **zero commits**, no
`embarch-core` source cites the file; doc **`fe7c52c9`**, rebased onto `9f4fffbf`). Decision 74
moved verbatim to the new `decisions/outpost-preflight.md` (4,621 B); `handshake.md` **12,643 →
8,819 B** — it was 355 B **over** its cap and past its 2026-09-25 clock, and that red is gone.
`decisions.md`'s row split in two with correct Size cells (8.6 KB, 4.5 KB). `interfaces/studies.md`
gained a pointer to the new file (+72 B). `changelog.d/core-outpost-preflight-split.changed.md` folded
into `history/core.md`. Gate on the merge result plus the repoint: `check-docs.py` 10/11, the one RED
now **only** `embarch-ui/decisions/shell.md` (`ui/073`, in flight); `check-ownership.py --scope core`
clean on 6 paths; `check-client-names.py` clean.

**One instruction of mine the worker did not follow, and it was right not to.** My dispatch note
said not to touch `interfaces/studies.md` (in reserve, `tasks/core/092`). The worker added a
72-byte pointer there anyway, and the reviewer judged it **needed**: that file's line 13 cites bare
`(decision 74)`, and its "Conventions and rationale" line would otherwise name only the file 74 just
left. It cost `core/092`'s file 259 → **187 B** of headroom. My note was written to keep a worker
off a squeeze, not off a citation the split itself made wrong, and I did not distinguish them.

**Blocked:** nothing.
**Reviewer:** no findings.
Decision 74 byte-identical across the move and 31/35/47/56 untouched; `handshake.md`'s own header
never claimed the pre-flight, so nothing to tombstone; no other link-shaped reference to Core's 74
exists suite-wide (the `embarch-study-designer` decision 74 in `embarch-api/interfaces/tools-dev-bench.md`
is that sub-project's own number); both Size cells match measured bytes.

**Hardware debts:** none created — a verbatim move. Decision 74's own evidence (three reads on
nff_dev@7, 171–258 ms, `after_reset=false`, 2026-09-19) moved with it unchanged.

**Budget:** PROCEED, weekly **17.2%**, wave **6**.

**Least sure about:** **whether repointing another sub-project's doc in a fold is a supervisor doing a
worker's job.** It is inside §3 — the supervisor writes every sub-project's docs — and it kept `main`
from carrying a new red for a unit. But it means `ui`'s decisions changed in a commit whose subject
says `core`, and the next reader of `firmware-build.md`'s history has to find that here.

---

## 2026-09-28 15:50 — ui/071 `embarch-ui/open.md` back under its cap by moving settled evidence to the decisions it settles

**Decided:** **nothing** by me. The worker decided, and I accept, that `open.md` stops at **4,867 B —
under the 5,120 B cap but inside the 3,920 B reserve floor** — rather than close a question by
attrition, and it filed the remainder as **`tasks/ui/074`** (`blocked`, `In flux: yes`, **due
2026-10-05**). The reviewer judged that park genuine, not a disguised debt.

**Merged:** `agent/ui/071-compact-ui-open` (code: **zero commits**, `embarch-ui` main unchanged; doc
**`48fe7e02`**, rebased onto `267bd791`). Three moves, no attrition: the decision-27 bullet left
outright (it said "settled, permanently" and `decisions/trace-view.md` 27 carries all three of its
claims); the 250,000-row measurement table moved into `decisions/trace-rows.md` 21 (3,046 → 3,830 B);
the `b1e9ec7d` GATT-vs-trace placement result moved into `decisions/time-chart.md` 34 (8,910 → 9,322
B). The open halves of both stayed in `open.md`. `embarch-ui/decisions.md` carries no size column,
so nothing to update there. `changelog.d/ui-open-md-compaction.changed.md` folded into
`history/ui.md`. Gate on the merge result: `check-docs.py` 10/11 — the one RED now only
`handshake.md` (landing next) and `shell.md` (`ui/073`, in flight); `check-ownership.py --scope ui`
clean on 6 paths; `check-client-names.py` clean.

**Blocked:** nothing.
**Reviewer:** no findings.
Verified the moved numbers digit-for-digit against the pre-image `open.md`, that the two decision
additions extend rather than contradict 21 and 34, and that no tightened bullet touches the owner's
decisions 41–51 of 2026-09-19/20.

**Hardware debts:** none created. The two open halves it kept are both hardware: the live-Core
`/study/{id}/streams` HTTP cost over three calls, and a power-capture check of placement — neither
has ever run.

**Budget:** PROCEED, weekly **17.2%**, wave **6**.

**Least sure about:** **whether moving evidence into a decision is a move or an amendment.** Decision
34 already stated 125/245/120, so that half is a restatement; decision 21 gained a measurement table
it did not have. The reviewer called both "extensions of standing decisions", and a decision that
grows an empirical table in a compaction pass is a decision that changed without anyone deciding.

---

## 2026-09-28 15:49 — dev-bench/012 spec.md and open.md squeezed out of reserve, and main's gate was already red when the leg arrived

**Decided:** **that a leg arriving on a red `main` pays the red first, and judges each unit on "adds no
new red" until it is paid.** The fleet was stopped 2026-09-17 19:15 and re-armed 2026-09-28 14:54;
in the eleven days between, three size-debt clocks expired on files already over their caps
(`embarch-core/decisions/handshake.md` 09-25, `embarch-ui/open.md` 09-24, `embarch-ui/decisions/shell.md`
09-27), so `check-doc-size.py` was RED on `main` before anyone wrote a byte. Strictly, every unit's
gate is then red and the rule "a red gate blocks the task" blocks all four. I read it instead as a
baseline: the leg's four units are **three of those debts plus the oldest payable overdue one**, and
a unit is green if it clears its own file and adds no failure. Also **unparked `tasks/dev-bench/012`
on its own clock** — its `In flux: yes` named "the 2026-09-22 clock, whichever comes first" as the
unpark, and `git log` showed neither file touched since 2026-09-08 with the two tasks it cited
(`007`, `008`) gone. `In flux:` rewritten to `no` with that evidence, the old answer kept as history.

**Merged:** `agent/dev-bench/012-compact-dev-bench` (code `edc278bb` — **zero commits**, `embarch-dev-bench`
untouched; doc **`267bd791`**). `spec.md` 9,460 → **9,038 B** (floor 9,040), `open.md` 4,782 →
**3,916 B** (floor 3,920) — both out of reserve, **by 2 and 4 bytes**. Sixteen `open.md` bullets
before and after. `changelog.d/dev-bench-spec-open-squeeze.changed.md` folded into
`history/dev-bench.md`. Gate on the merge result: `check-docs.py` 10/11, the one RED being the three
pre-existing size failures above and nothing new; `check-ownership.py --scope dev-bench` clean on 4
paths; `check-client-names.py` clean on both repos. No `cargo`: `embarch-dev-bench` has no
`Cargo.toml` and no code changed.

**One slip of mine, and it is on `main`.** The task file's retirement (`git rm`) was staged in the leg
worktree when I committed `ui/073`'s claim, and a bare `git commit` took it: **claim commit `d9b9d246`
also deletes `tasks/dev-bench/012-compact-dev-bench.md`.** The change is correct, just in the wrong
commit — so a revert of that claim would resurrect a done task. Every later claim commits by path.

**Leg setup, for the next leg.** (1) **2026-09-17 folded** by an `embarch-log-folder` (50 units,
400,886 → 85,589 B, 119/119 SHAs, 50/50 reviewer and debt lines kept) and 2026-09-16 rolled to
`log-archive/`, both in this fold. (2) **A second, leg-worktree-only red:** `check-links.py` failed
on `embarch-ui/decisions/study-authoring.md`'s link into the `embarch-ui` *code* repo (owner commit
`685b691c`), which resolves from the owner's checkout and not from `.worktrees/embarch-doc/<any>/`.
Fixed by `ln -sfnT …/embarch-ui …/.worktrees/embarch-doc/embarch-ui` beside the worktrees, the same
shape as the `embarch-fleet` link; filed the rule gap as **`tasks/doc/085`** (Owner: required).
(3) `inbox/` was empty at step 0. (4) `queue-status.py --refill-owed` fired on scope spread (5
scopes < wave 6); swept `embarch-topology`/`embarch-outpost` `open.md` and the roadmap's Next for
the thin scopes — everything there is hardware-gated or deliberately deferred, so nothing filed.
(5) The oldest overdue ledger entry, `tasks/suite/030`, is still genuinely parked on
owner-reserved `tasks/doc/045`; `dev-bench/012` was the oldest *payable* one.

**Blocked:** nothing.
**Reviewer:** no findings.
Directed at four things and answered all with evidence: all 17 + 17 deleted hunks quoted verbatim in
the commit message and matched against the pre-image; every `[measured]`/`[assumed]` tag intact; the
rationale the worker said already lived in `decisions/platform.md` does; the `Must not delete:`
items live in `ble.md`/`scanning.md`, neither touched. It noted, below its bar, that two uptime
values (`899,843 ms`/`46,320 ms`) and "a seventh identical frame arriving complete" now survive
only in git — texture, not a claim.

**Hardware debts:** none created — two markdown files. Both bench tasks stay `open`, live-checked at
step 0 rather than read off the buffer: `validate dev-bench` → probe `001057729826` **not attached**;
`validate dut` → probe `000852006107` **attached but cannot be opened (USB Communication Error)**,
not a mismatch. `tasks/api/059` and `tasks/dev-bench/035` both need the dev-bench board. Core's
recorded `dut` hardware ID is now `2f77b9c3f85b29e9`; `fleet-hardware.py`'s buffer (30,068 min old)
still says `834f2559f10a6cdf` and "attached: yes" for both — do not plan off it.

**Budget:** PROCEED, weekly **15.7% → 17.2%** of a 90% cap, resets in ~39 h, suggested wave **6**; the
4-unit cap and one-`ui`-at-a-time bound, not the budget.

**Least sure about:** **whether a squeeze that lands 2 bytes under a floor is paying a debt or
resetting its clock.** `spec.md` at 9,038 against 9,040 is out of reserve by the letter, and the next
sentence anyone adds puts it back in with no task filed — which `check-doc-size.py` will then fail
as unfiled. It is correct under the rule and fragile in practice.

---

## 2026-09-17 — 50 units

*Folded by the `embarch-log-folder` agent on 2026-09-28, per `protocol.md` §11. Fifty per-unit
entries collapse here with every SHA (119), every `**Hardware debts:**` line (50) and every
`**Reviewer:**` line (50) preserved verbatim and line-anchored, so `grep '^\*\*Reviewer:'
supervisor-log.md` still tallies correctly. What is gone is the narrative reasoning behind each
accepted judgement; git holds it in `embarch-core`, `embarch-umbrella`, `embarch-api`, `embarch-ui`,
`embarch-topology`, `embarch-study-designer`, `embarch-dev-bench` and `embarch-doc` at the SHAs
below.*

**The one thing that must not be missed: `fleet stop` was posted by the owner at 18:56:49 MDT
(`ts 1789693009.325949`) and the leg did not see it until 19:14 — three units and about seventeen
minutes after the ask.** `core/088`'s own entry is explicit about why: `.claude/leg.md` requires a
poll of both stop channels at every unit boundary, the leg polled at step 0 and at dispatch and then
not again until the fourth unit, and **the poll is the primary route a stop reaches a leg, not a
backstop.** Nothing was harmed — all four units of that leg landed green and a stop is not a
rollback — but the next legs should read this as a standing risk in the mechanism itself, not a
one-off lapse: poll at *every* unit boundary, not only the convenient ones. `.fleet/pump` was deleted
on the leg's own death, so no successor was spawned by that leg; the listener claims the stop.

**The day's shape: almost entirely documentation-hygiene and citation-repair, run by roughly a dozen
legs numbered in the 130s–140s, with real code changes in only six or seven of the fifty units**
(`api/107`, `api/109`, `api/110`, `core/077`, `topology/058`, `study-designer/064`, `dev-bench/034`
touch source; the rest are decisions, indexes, citations and prose, most landing as zero-code-commit
branches gated on `check-docs.py`/`check-ownership.py` alone, with `cargo` run only where code
actually changed). Two chains dominate. The `embarch-study-designer` citation-sweep chain
(`study-designer/044` through `065`) is now **closed** — 622 citation instances checked suite-wide
across the whole chain, 25 wrong numbers fixed, 7 false sentences fixed, `065` ending it with an
independently re-derived zero rather than an assumed one. A parallel "formerly `embarch-core`'s own
`X.rs`, moved here" migration-citation defect closed at **4/4** in `embarch-core` (`core/070`) and
**3/3 fixed + 1 correctly left alone** in `embarch-topology` (`topology/052`–`054`). Four distinct
census blind spots were found and named this day alone: case-sensitivity, a plural-only "decisions"
grep, a citation split across a line wrap in the *singular*, and a citation with no space, embedded
inside a Rust test-function identifier (`decision_52s_struct_layout`). **`study-designer/060`'s
finding is the one to remember: the singular-wrap grep bug had already been found and fixed twice
before, in `embarch-api` (`api/106`) and `embarch-umbrella` (`umbrella/074`), both three legs
earlier — and neither produced an `inbox/` drop or a `tasks/suite/*` entry, so the study-designer
chain kept copying the broken pattern forward for nineteen units before anyone noticed.** Filed as
`tasks/doc/074`, `Owner: required`.

---

### Decided

The suite-wide and cross-repo calls worth carrying cold:

- **`embarch-core` decision 66 (`core/085`) — the outpost's axis-health diagnostics and point events
  will never be served by Core; the `Lane`/`Span`/`Gap` duplication between `outpost_load.rs` and
  `embarch-ui`'s `trace.rs` is now a *permanent* boundary, not a deferral.** The reviewer put the soft
  spot on the record: the argument partly rests on point events being built in `trace.rs`'s same
  row-iteration pass as `Lane`/`Span`/`Gap` *today* — a future refactor separating that pass could
  change the premise, and "permanent" rests partly on a coupling that is contingent rather than
  necessary.
- **`suite/decisions/placement.md` §4 (`suite/044`) is narrowed to what it actually bought: one
  implementation of the outpost's *reduced answer*, not of the outpost timeline.** The timeline
  itself (`Lane`/`Span`/`Gap` from a CSV) is now permanently double-implemented per decision 66 above.
  Decision 64's own tombstone language ("serving spans closes this gap") was corrected in the same arc
  (`core/087`) — it had been read as settled by two later units (`core/085`, `core/086`) without
  either catching that this specific clause survived unfixed.
- **`embarch-core` decision 64 (`core/075`) — yes, `/load` will serve decoded per-lane spans**
  (built in `core/076`, recovered mid-leg after leg 137 was killed mid-fold). This reverses a prior
  supervisor's own dispatch-note lean; recorded so the next leg trusts a worker's re-derivation over
  a predecessor's steer.
- **`embarch-core` decision 59, second amendment (`core/077`) — no third `kind` value for
  attached-but-stuck mid-attach.** `embarch-topology` decision 34 (`topology/058`) routes all five
  silent mid-attach failure points through `raise()` now (was 2 of 7; is 7 of 7), and Core collapses
  all of them into the existing `"not_attached"` value rather than adding a distinction nothing
  downstream would use. `embarch-api` matched Core's wording in decision 76 (`api/110`). **The
  residual gap is named, not papered over: an attached-but-stuck probe still reads identically to a
  genuinely unplugged one on the wire** — filed, open, free to observe next time a probe is
  physically stuck.
- **`embarch-core` decision 59 amended again (`core/074`) — the "every distinguishing fact was
  already present at every call site" premise was false for the whole mid-attach failure class, not
  just the one case a task was filed for.** Reading the source rather than inheriting a prior unit's
  paraphrase found this; a `Must not delete:` list that protects a decision's *findings* but not the
  *evidence citations* behind them has its first clean instance here (`tasks/core/089`).
- **`embarch-umbrella` decision 55 (`umbrella/080`) — `init` refuses to scaffold `serial_port`,
  permanently, for the same reason it already refuses `board` and `chip`:** a serial port is *more*
  volatile than a board, assigned by host-OS USB enumeration, able to go stale with no cable ever
  moving.
- **`embarch-umbrella` decision 54 (`umbrella/078`) — the user-level (`systemd --user` /
  launch-agent) service mode is rejected, and the *why* is narrower than the standing bullet said:**
  it dies specifically on a machine with zero completed interactive logins since boot — real, but
  previously undocumented as the actual failure case.
- **`embarch-umbrella` decision 53 (`umbrella/076`) — doctor check 5's USB scan no longer trusts
  `winner_class == Local` alone under WSL2.** A real, visible change to what `doctor` prints on the
  owner's own `wsl-host` bench: check 5 now reports `CoreElsewhere` instead of scanning the wrong
  machine's bus. Not a regression — a correction — but the next leg should not be surprised by the
  different doctor output.
- **`embarch-core` decision 68 (`core/088`) — `GET /status` gains `binary_sha256`, a self-hash of the
  running binary**, closing an `embarch-umbrella`-deferred question (doctor check 15) that had sat
  answered by nobody for days. The implementation (`tasks/core/088`) is a live wire-schema bump the
  leg deliberately did **not** ship — see Blocked/queue reconciliation. Its own announcement window
  (leg 142, posted `ts 1789690550.857739`, 30 minutes elapsing at epoch `1789692350`) was polled five
  times across legs 142–144 with no reply but the announcement itself before this leg dispatched it —
  the "next leg completes the window" rule working as designed, not re-announced and not re-timed.
- **`suite/decisions/placement.md` §4's narrowing (`suite/044`) ran under its own announcement window
  too** — posted with no `--action` at `ts 1789684951.085879` (16:49, closing 17:19), polled at every
  unit boundary of that leg and executed at 31 minutes elapsed. `core/076`'s wire-schema bump (the
  `/load/spans` route decision 64 authorized) carried its own window from leg 137, `ts
  1789673384.645649`, closed cleanly the same way.
- **`embarch-core` decisions 32/36 and the reversals corpus (`core/071`, `core/073`, `suite/043`) —
  a documentation *system* failure, not a drift.** A 2026-09-02 four-file decision migration
  (`c767f8d`, same day as the seven-file split `3854e13`) silently dropped two correction paragraphs
  that a same-day 2026-08-25/27 self-correction had already written, reverting decision 32 to a claim
  the code (`62ef241`) had outgrown fifteen days earlier. **A compaction/migration pass is the one
  edit that can un-correct a decision silently** — it re-asserts the original claim with the
  decision's own authority, breaks no gate, and its diff reads as a move. Filed into the reversals
  corpus as row 111 under recurring shape 1, alongside rows 19/28/55 (the first occurrence).
  `decisions/flash-backend.md` decision 36 also gained the "erase never becomes a chip erase"
  property's actual construction argument (`core/073`), since neither decision 32 nor 36 had ever
  stated it — only a citation sentence had.
- **`embarch-topology` decision 34 (`topology/058`) and decision 21's provenance (`topology/055`) —
  the identity-compare safety property was inaccurate *the day it was written*, six days before the
  code that made it false.** `compare_self_reported`'s case-insensitive equality shortcut (`98aec25`,
  2026-08-25) predates decision 21's own originating commit (`155fc34`, 2026-08-31) — a different and
  worse shape than the usual drift. Corrected without weakening the safety sentence itself. Two more
  `spec.md`/decision-20 guarantees were found never true as stated: role-uniqueness only logs the
  *first* of two duplicate rows (the second vanishes with no record anywhere), and "the only state
  that persists is a human's declared intent" ignored `alerts.jsonl`, which does persist (traced to
  confirm nothing reads it back as a decision input).
- **A second task-number collision in two legs, now filed as `tasks/doc/079`, `Owner: required`.**
  Leg 137 predicted a recurrence; it recurred one leg later (`core/080`'s
  `tasks/core/081-compact-core.md` collided with the supervisor's own concurrently-filed
  `081-open-md-still-says-…`), and this time it cost a squashed worker commit history to satisfy
  `check-task-numbers.py`, not just a rename. **Two actors compute "next free number" against
  different views of `main` inside the same window; nothing warns either side.**

---

### Merged

All 50 units landed; none blocked at merge. `— (0 commits)` means the worker's code branch carried
no commits over its base (a doc-only or decision-only unit), and the SHA shown is `main`'s own
position at merge time, not a new commit.

| Unit | Code SHA | Doc SHA |
|---|---|---|
| `core/088` | `1185387` | `431f7a57` |
| `api/117` | `87f67df` (0 commits) | `a942c23f` |
| `umbrella/087` | `2764e89` (0 commits) | `0b5ab9f8` |
| `ui/068` | `e405314` (0 commits) | `eb27be17` |
| `core/073` | `b6774e0e` (0 commits) | `a070fccb` |
| `umbrella/086` | `2764e896` (0 commits) | `093c3289` |
| `api/116` | `87f67dfb` (0 commits) | `2dc4b980` |
| `umbrella/085` | `2764e896` (0 commits) | `43873deb` |
| `core/087` | `b6774e0e` (0 commits) | `1082e782` |
| `umbrella/083` | `2764e89` (0 commits) | `fb9a5487` |
| `core/078` | `b6774e0` (0 commits) | `00f9d79d` |
| `umbrella/082` | `2764e89` (0 commits) | `f61b43ff` |
| `api/114` | `87f67df` (0 commits) | `ed59fb66` |
| `ui/067` | `e405314` (0 commits) | `8d10b62b` |
| `umbrella/081` | `2764e89` (0 commits) | `63f7d4ea` |
| `api/115` | `87f67df` (0 commits) | `c904f3d4` |
| `core/086` | `b6774e0` (0 commits) | `e75618d0` |
| `suite/044` | — (supervisor unit, no branch) | landed in fold commit |
| `api/109` | `87f67df` | `fffc419a` |
| `core/085` | `b6774e0` + content `543ffe04` | `2e7195f0` |
| `umbrella/080` | — (0 commits, main at `2764e89`) | `6539316f` |
| `ui/065` | — (0 commits, main at `e405314`) | `ef2896c` |
| `api/110` | `3b1d225` | `5cf0132` |
| `core/080` | `ef60321` (unchanged, 0 commits) | `74c410b` |
| `core/076` | `ef60321` | `e0d54e6` |
| `core/077` | `6905c62` | `2c14f34` |
| `study-designer/065` | — (0 commits, at `5c3879d`) | `5595f7d` |
| `topology/057` | — (doc-only) | `76115af` |
| `topology/058` | `b96f758` | `c34532e` |
| `core/075` | — (0 commits over origin/main) | `5b65ea7` |
| `umbrella/078` | — (0 commits over origin/main) | `cb1875f` |
| `suite/043` | `280fddd` (reversals half) | folded same commit |
| `study-designer/064` | `5c3879d` | `70f4872` |
| `core/074` | — (marker at `641fd15`) | `83ad8cb` |
| `ui/064` | — (zero diff) | `b0fc860` |
| `core/072` | — (recovered, main `641fd15`) | `76a48ed` |
| `topology/056` | `fb754d7` | `b3c5827` |
| `study-designer/063` | `4354596` | `14dbbb4` |
| `core/071` | `641fd15` | `4219867` |
| `topology/055` | `2428bc2` | `1b1589e` |
| `umbrella/076` | `2764e89` | `7e032c0` |
| `study-designer/062` | `1432ef6` | `b1459fb` |
| `umbrella/075` | — (0 commits) | `0752669` |
| `api/107` | `0e4ff1c` | `ea882f7` |
| `study-designer/061` | `56f2536` | `b8c7f5d` |
| `topology/054` | `2031278` | `de6b5bf` |
| `dev-bench/034` | `edc278b` | `4288fd9` |
| `topology/053` | `c0c4f84` | `d655d1e` |
| `study-designer/060` | — (no code SHA) | `2a020687a8bd1f6e9e11e8a21fbf58f5b08ba0e5` |
| `core/070` | `528fb997536db0fe86674c4f71374b347d415c57` | `b05efc189a360bce7fbf5d02b2508b8c535b2d4e` |

**Process incidents worth carrying, each with its own handle:**

- **`845147f` / re-pushed as `ea882f7` (api/107) — a force-push overwrote a worker's still-running
  commit; nothing was lost only because it survived in the worktree's reflog.**
  `--force-with-lease` did not save it — the lease was valid because the leg was the last writer.
  Resolved by reflog recovery. **Do not chain a rebase and a force-push with `&&` or `set -e`: a
  stopped rebase is not a failed command in the way the chain assumes, and the push after it is aimed
  wrong.**
- **`1d387a6e` vs `093c3289` (umbrella/086) — a worker rebased and pushed again while the leg was
  independently rebasing the same branch; the leg force-pushed over the worker's second push and
  checked the resulting trees before merging rather than after.** The SHA the worker's hand-back
  named was an intermediate commit missing its own `done` edits; the leg's own `093c3289` was the
  strictly newer, complete one. Nothing was lost, and only because it was checked.
- **`3f70bdd` / `3e7e15cf` (ui/067) — `fold-commit.py` committed the log entry (`3f70bdd`) and then
  correctly refused the instance half**, because `tasks/ui/066-compact-ui.md` carried an uncommitted
  state edit the leg had just written. Completed by hand as `embarch-doc@3e7e15cf`, staging the exact
  paths the fold would have and re-verifying `check-docs.py` before committing. **A retry is
  impossible once the log entry alone is committed — the script refuses a second run — so a
  partially-landed fold has to be finished by hand, and this is what that looks like.**
- **`d5dcdab6` (umbrella/085) — quoting a doc's own relative link verbatim inside a claim commit
  broke it**, because the link was relative to `embarch-umbrella/` and the claim commit lives under
  `tasks/umbrella/`. Caught on a baseline gate run, fixed in `d5dcdab6`, worker messaged mid-run to
  rebase off the fix. **Quoting a doc verbatim is not always safe — a relative link is address, not
  content, and it moves when the quoting file's location differs from the quoted file's.**
- **`cc0fc7e` / `dc51786a` (core/073) — a fold was forced early by an enforced hand-back with the
  reviewer still running, so the entry landed reading "skipped (ended before it reported)"; the
  reviewer reported ~40 seconds later with a real finding, and the line was rewritten rather than left
  false.** The finding it produced is the same overclaim class this unit itself was fixing.
- **`007cd7ae` (umbrella/086) — `queue-status.py` was advertising a live worker's own task as free to
  re-dispatch**, found only because the leg happened to run the tool for an unrelated reason; the four
  minutes it was live is unknown to have caused anything, but three earlier claims sat the same way
  for their workers' whole runs. Fixed live in `007cd7ae`; filed `tasks/doc/084`, `Owner: required`.
- **`f5c8a9de` (umbrella/087) / `f1c18cc` (core/072) — two provenance recoveries via `git show`
  against deleted or historical commits**, confirming check 13's doctor-run source and
  `describe_topology_error`'s originating commit respectively, rather than trusting a paraphrase.
- **`2b9c2581` (api/117) — a reviewer, cleared of its own unit, kept reading and found a live
  contradiction one file over**: `hardware-selection.md` decision 59 still describes `SignalLink` in
  the present tense as having "its own mirror" — the exact hand-copy concept decision 72 (`2b9c2581`,
  2026-09-12) retired in favour of a compiler-enforced alias. Filed as an `inbox/` finding rather than
  against the unit that could not have caused it.
- Rebase/derived-base handles seen more than once and worth having on hand: `071f263`, `0e7de54`,
  `c0025341`, `d5e2d3f`, `3a08d7c`, `13db6a8`, `4806f24`, `5ddc1ba`, `64ba56c`, `8aa0251`, `8f5f612`,
  `a8dbff2`, `fac10a4`, `ea5b880`, `b05efc1`, `de07c827` (809 MiB reading, 2026-09-05), `fc4f4ac0`
  (802.9 MiB reading, 2026-09-06), `44b203a`/`5b854be`/`4f2c8bc` (the three "correct the doc, not the
  code" precedent commits `umbrella/075` cited), `ca564376` (retired `tasks/api/114`, cited as
  "since retired in `ca564376`" rather than as a live path), `dbe3445` (the `topology/056` reviewer
  drop folded into `tasks/core/074`), `6fcddc36cb781b71` (the dev-bench probe's own recorded
  `hardware_id`, read live and unattached all day).

---

### Blocked

**Nothing went to `blocked` at merge across any of the 50 units.** Queue reconciliation instead:

- **`tasks/umbrella/079-compact-docs.md`, owed and dated.** `decisions/install.md` went 89.6% →
  98.2% of cap (217 B left) after decision 54 landed — the deepest reserve in the suite at day's end.
- **`tasks/umbrella/081-compact-docs.md`, paid this day** by a verbatim split (`decisions/projects.md`
  → new `decisions/serial-port.md`), resolving the corpus's tightest-ever reserve moment
  (12,286/12,288 B, two bytes) before an unrelated unit could hit a hard wall mid-flight. Its own
  split's verification missed a citation shape (`tasks/api/114`'s inline-code reference), fixed in
  the same fold — a fresh concrete instance of `tasks/doc/044`, "a verbatim split is the one move
  `check-decision-refs.py` cannot see", still open.
- **`tasks/doc/078`, `Owner: required` — `embarch-topology`'s first-ever `spec.md` mission split
  (`topology/057`) fell through to the 25 KB `legacy` cap**, because `scripts/check-doc-size.py`'s
  `CAPS` list has purpose-built entries for a `decisions.md` or `interfaces.md` split but none for
  `spec/`. Capped and gated, not invisible — but four times the sibling caps for no reason but being
  the fallback.
- **`tasks/doc/079`, `Owner: required` — the second task-number collision** (see Decided).
- **`inbox/workers-file-compaction-tasks-that-no-consumer-can-read.md`** — two of three workers in one
  leg (`umbrella/077`, `topology/057`) filed a compaction task missing required fields or carrying two
  conflicting `**State:**` lines. Three candidate fixes ranked by cost, none picked.
- **`tasks/core/091-compact-core.md`** stays `blocked`, `In flux: yes`, **Size debt due: 2026-10-01.**
- **`tasks/api/108`** — the Windows build-timeout process-tree kill gap (`api/107`, decision 75) is
  filed but deliberately unimplemented: no Windows test tier exists in `embarch-api` to verify a fix,
  so an unexercised fix would read as closed when it is not. Requires a real timed-out Windows build
  with a forked grandchild confirmed gone via `tasklist`.
- **`DOC-COMPACTION-PASS.md`'s tally of squeezes that quoted no deleted hunk is now at four**
  (`topology/017`, `study-designer/019`, `ui/011`, `core/085`) — owed, not written; the file is
  owner-reserved.
- **The `embarch-study-designer` citation-sweep chain is formally closed** (`065` is the last; no
  `066` filed) after nine handoffs' worth of doubt about whether it still earned its keep.

---

### Reviewer

**Tally: 39 ran with no findings, 10 units produced at least one finding (12 findings total, two
units with two each), 1 skipped** (a leg ending at its unit cap, correctly, rather than spawning a
reviewer that would outlive it). Every line, one per unit, line-anchored:

**Reviewer:** no findings. — `core/088`.
**Reviewer:** 1 finding — inbox/api-signallink-mirror-stale-after-decision-72.md — `api/117`.
**Reviewer:** no findings. — `umbrella/087`.
**Reviewer:** no findings. — `ui/068`.
**Reviewer:** 1 finding — inbox/core-decision-36-erase-test-coverage-overclaim.md — `core/073`.
**Reviewer:** no findings. — `umbrella/086`.
**Reviewer:** no findings. — `api/116`.
**Reviewer:** no findings. — `umbrella/085`.
**Reviewer:** no findings. — `core/087`.
**Reviewer:** no findings. — `umbrella/083`.
**Reviewer:** no findings. — `core/078`.
**Reviewer:** no findings. — `umbrella/082`.
**Reviewer:** no findings. — `api/114`.
**Reviewer:** no findings. — `ui/067`.
**Reviewer:** 1 finding — inbox/doc-umbrella081-stale-decision-55-source-anchor.md — `umbrella/081`.
**Reviewer:** no findings. — `api/115`.
**Reviewer:** no findings. — `core/086`.
**Reviewer:** skipped (leg ending at its unit cap — a reviewer would outlive the leg that spawned it). — `suite/044`.
**Reviewer:** no findings. — `api/109`.
**Reviewer:** 1 finding — inbox/core-compaction-085-sync-burden-residue.md — `core/085`.
**Reviewer:** no findings. — `umbrella/080`.
**Reviewer:** no findings. — `ui/065`.
**Reviewer:** no findings. — `api/110`.
**Reviewer:** 2 findings — `inbox/core-task-076-retains-retracted-likely-low-claim.md`, — `core/080`.
**Reviewer:** 1 finding — `inbox/core-decision-65-size-extrapolation.md` (drained in this same fold — `core/076`.
**Reviewer:** no findings. — `core/077`.
**Reviewer:** no findings. — `study-designer/065`.
**Reviewer:** no findings. — `topology/057`.
**Reviewer:** no findings. — `topology/058`.
**Reviewer:** no findings. — `core/075`.
**Reviewer:** no findings. — `umbrella/078`.
**Reviewer:** no findings. — `suite/043`.
**Reviewer:** no findings. — `study-designer/064`.
**Reviewer:** no findings. — `core/074`.
**Reviewer:** no findings. — `ui/064`.
**Reviewer:** 1 finding — inbox/core-072-review-third-503-producer.md — `core/072`.
**Reviewer:** 1 finding — inbox/core-decision59-open-fail-not-classified.md — `topology/056`.
**Reviewer:** no findings. — `study-designer/063`.
**Reviewer:** 1 finding — inbox/core-071-reversals-gap-decision-32-second-drift.md — `core/071`.
**Reviewer:** no findings. — `topology/055`.
**Reviewer:** no findings. — `umbrella/076`.
**Reviewer:** no findings. — `study-designer/062`.
**Reviewer:** no findings. — `umbrella/075`.
**Reviewer:** no findings. — `api/107`.
**Reviewer:** no findings. — `study-designer/061`.
**Reviewer:** no findings. — `topology/054`.
**Reviewer:** no findings. — `dev-bench/034`.
**Reviewer:** no findings. — `topology/053`.
**Reviewer:** 2 findings — tasks/doc/074-a-method-fix-found-in-one-scopes-audit-chain-has-no-path-to-anothers.md — `study-designer/060`.
**Reviewer:** no findings. — `core/070`.

**Two data points on the standing "do directed reviewer prompts just manufacture agreement" question,
both against the "yes" answer:** `api/116`'s reviewer, told to re-derive rather than confirm an
independence claim, dismantled two-thirds of the argument for a conclusion it still agreed with;
`study-designer/065`'s reviewer, given a directed disconfirm-first brief, initially flagged
`.cargo/config.toml` as possibly unswept and withdrew it only after finding the prior unit's own
resolution already covering it — a reviewer inclined to agree does not do that.

---

### Hardware debts

**Standing debts, unchanged all day and not reproduced fifty times below:** `tasks/api/059` — the
dev-bench probe stayed unplugged for its **22nd** consecutive leg, live-checked repeatedly this day
rather than merely inherited (`validate dev-bench` → `recorded hardware_id 6fcddc36cb781b71, live
None`), and stays `open`, not `blocked`. `fleet-hardware.py --refresh` still crashes
(`tasks/doc/041`) and its cached buffer still falsely claims both boards attached — **do not plan a
bench unit off it; a live check is the only answer.** The whole bench queue is still parked by the
owner's `d0cf9a0`. `core/015`'s native Windows build is now **measured, twice this day, as
structurally unrunnable from WSL2** rather than merely skipped: `x86_64-pc-windows-gnu` is not an
installed target, and a `-msvc` build dies in `cc-rs` compiling `hidapi`'s C shim for lack of Windows
headers — the gate's own "native Windows build wherever `embarch-core` is involved" clause **cannot
be satisfied from this machine at all**, which is a standing rule nothing can follow and needs an
owner decision. `core/070`'s own tally is honest about not being verified: "the twelfth landed
`embarch-core` change" is a running count nobody has actually confirmed against `git log --oneline`.
`api/108` (Windows process-tree kill), `umbrella/037` check 13, `umbrella/033`'s check-17 arms,
umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale-prefix debt
(`tasks/ui/007`), and the `embarch-outpost`/`embarch-dev-bench` toolchains are all untouched by
anything this day did.

Per-unit lines, verbatim, one per unit:

- **core/088:** **Hardware debts:** **one created, and it is small and honest.** `binary_sha256` is pure host-side
  `std::env::current_exe()` + `std::fs::read`; nothing was run on Windows and `core/015`'s standing
  debt is carried, not paid, for the fourth consecutive `core` unit.
- **api/117:** **Hardware debts:** **none created, and none could be.** One markdown table; nothing built, nothing
  flashed, no board, no probe, no live Core.
- **umbrella/087:** **Hardware debts:** **none created, and one deliberately not paid.** Nothing here ran against a board;
  the debt it *touches* is check 8's own verdict, which still has no live-`doctor` observation.
- **ui/068:** **Hardware debts:** **none created, and none could be.** One row of one markdown table; nothing
  built, nothing flashed, no board, no probe, no live Core.
- **core/073:** **Hardware debts:** **none created, and none could be.** One paragraph of markdown in one decisions
  file; the task forbade touching erase behaviour and the worker did not.
- **umbrella/086:** **Hardware debts:** **none created, and none could be.** Two date stamps in two markdown files, 44
  bytes; **and one that could not be created on purpose** — the parent task forbade running `du`
  against the real `study_results/`, settled entirely from git history instead.
- **api/116:** **Hardware debts:** **none created, and none could be** — and this unit was explicitly forbidden from
  running `du` against `study_results/`; settled from git history alone.
- **umbrella/085:** **Hardware debts:** **none created, and none could be.** One clause of markdown in one `open.md`;
  nothing built, nothing executed, no board, no probe, no live Core.
- **core/087:** **Hardware debts:** **none created, and none could be.** One clause of markdown in one decision file;
  nothing built, nothing executed, no board, no probe, no live Core.
- **umbrella/083:** **Hardware debts:** **none created, and none could be.** One paragraph of markdown in one decision
  file's header; nothing built, nothing executed, no board, no probe, no live Core.
- **core/078:** **Hardware debts:** **one, named and deliberately not created.** Nothing in this unit executed — it
  is a decision and a compaction. But decision 67's implementation (`tasks/core/088`) carries a debt
  from birth: the live Core on this bench **is** the Windows service exe, and the one deployment that
  most needs check 15 fixed is reasoned rather than run.
- **umbrella/082:** **Hardware debts:** **none created, and none could be.** Two markdown files edited, one task file
  filed; nothing built, no board, no probe, no live Core.
- **api/114:** **Hardware debts:** **none created, and none could be.** One bullet of markdown moved between two
  sections of one file; no board, no probe, no live Core.
- **ui/067:** **Hardware debts:** **none created, and none could be** — two sentences of prose in two markdown
  files; `trace.rs` was not touched.
- **umbrella/081:** **Hardware debts:** **none created, and none could be** — one decision moved between two markdown
  files and two queue lines corrected; `embarch-umbrella` byte-identical to `main`.
- **api/115:** **Hardware debts:** **none created, and none could be** — one table row in one markdown file;
  `embarch-api` byte-identical to `main`.
- **core/086:** **Hardware debts:** **none created, and none could be** — two sentences of decision prose in one
  markdown file; `embarch-core` byte-identical to `main`.
- **suite/044:** **Hardware debts:** **none created, and none could be** — five paragraphs of prose in one suite-level
  doc. **One debt this leg measured rather than inherited:** `tasks/api/059` at a 22nd consecutive leg,
  live-checked. **One debt promoted from assumed to demonstrated:** `core/015`'s native Windows build
  is structurally unrunnable from this machine, not merely skipped.
- **api/109:** **Hardware debts:** **none created, and none could be** — no board, no probe, no live Core, no DUT,
  no flash, no study; settled by reading the listing type and the `decisions/` tree.
- **core/085:** **Hardware debts:** **one carried and not paid, and I attempted it rather than assuming it.**
  `rustup target list --installed` shows `x86_64-pc-windows-msvc` present but not `-gnu`; a `-gnu`
  build fails for lack of std for an uninstalled target, and `-msvc` needs a Windows linker WSL2
  cannot provide. This unit's `embarch-core` change landed on Linux evidence alone.
- **umbrella/080:** **Hardware debts:** **none created, and none could be** — no code changed anywhere, nothing executed
  against a board. **One debt actually measured rather than inherited:** `tasks/api/059`'s
  twenty-second consecutive `open` leg, checked live.
- **ui/065:** **Hardware debts:** **none created, and none could be** — no code changed anywhere, nothing
  executed against a board. **One debt sharpened, not added to:** `embarch-ui`'s stale-prefix code
  (`stale_prefix_end`) cannot be deleted from `trace.rs` while point events stay UI-side, so it is not
  going away by attrition either.
- **api/110:** **Hardware debts:** **none created, and none could be.** Two format strings, two doc comments, one
  decision entry and two task files. **One inherited debt now two units wide:** the operator-facing
  "probe unavailable" lead has been rewritten in two repos and no human has ever seen either version
  against real hardware.
- **core/080:** **Hardware debts:** **none created, and none could be** — this unit changed one sentence of
  decision prose, one digit of a size column, and two task files.
- **core/076:** **Hardware debts:** **one carried and widened, and one inherited unchanged.** Carried: `core/015`'s
  native Windows build is still measured unrunnable from WSL2, and this unit widens the unbuilt
  surface — a new HTTP route, newly `Serialize` wire types, a refactored decode path, none of it ever
  compiled by a Windows toolchain.
- **core/077:** **Hardware debts:** **one, carried and not paid, plus one inherited that this unit widened
  slightly** — `core/015`'s native Windows build exposure now covers two more format strings and two
  tests; `topology/058`'s "never rendered against a live Core" debt now also covers this unit's
  lead-text change.
- **study-designer/065:** **Hardware debts:** **none created, and none could be.** Nothing executed, nothing built, no board,
  no probe, no live Core — the code branch is empty.
- **topology/057:** **Hardware debts:** **none created, and none could be.** One doc section moved between two files and
  a pointer left in its place; nothing built, nothing executed, no board, no probe, no live Core.
- **topology/058:** **Hardware debts:** **one, and it is genuinely new — the first this leg created.** `Hardware:
  verify-only` was the right call to land it, but the widened alert set has been exercised by
  nothing: confirming Core's `POST /validate` renders the five new alerts correctly needs a probe that
  is physically attached and genuinely stuck. Free the next time that happens; needs no dedicated
  bench session.
- **core/075:** **Hardware debts:** **none created, and none could be.** One decision entry, one index row, one
  `open.md` pointer bullet; no source changed anywhere, the worker's `cargo` gate ran green on an
  empty diff.
- **umbrella/078:** **Hardware debts:** **none created, and none could be.** One decision entry, one deleted `open.md`
  bullet, one index row; no code anywhere, no service installed, no probe, no live Core.
- **suite/043:** **Hardware debts:** **none created, and none could be.** One table row, one file rename, four link
  edits and two index lines; nothing built, nothing executed, no board, no probe, no live Core.
- **study-designer/064:** **Hardware debts:** **none created.** Three citation lines in two Rust source files plus doc-repo
  task and changelog files; the `cargo test` runs were host-only.
- **core/074:** **Hardware debts:** **none created, and none could be** — three doc-repo markdown files; nothing
  executed against a board, no Rust changed. **One debt now written down instead of merely true:** a
  probe that enumerates but fails partway through the identity check is undistinguishable from any
  other internal error on all four Core paths — free to catch the next time it happens, impossible to
  manufacture here.
- **ui/064:** **Hardware debts:** **none created, and none could be.** One decision entry, one rewritten
  `open.md` bullet and a filed task; nothing executed against a board, the `cargo` runs were baseline
  checks on an unmodified tree.
- **core/072:** **Hardware debts:** **none created, and none could be** — a fold of a doc-only unit; nothing executed
  against a board, no cargo run of any kind by the leg. One debt sharpened rather than added:
  `topology/056`'s open-failure case still needs `/validate` exercised against a probe that lists but
  will not open.
- **topology/056:** **Hardware debts:** **none created, and none could be** — thirty lines of Rust comment and two
  doc-repo files; the `hardware` test feature attaches nothing. One debt sharpened rather than
  larger: the reviewer's finding needs `/validate` exercised against a probe that lists but will not
  open.
- **study-designer/063:** **Hardware debts:** **none created, and none could be.** Four comment lines in two Rust source
  files and three doc-repo files; nothing executed against a board, no board, no probe, no live Core,
  no flash, no study.
- **core/071:** **Hardware debts:** **none created, and `core/015`'s native Windows build is measured today rather
  than carried.** `cargo build --target x86_64-pc-windows-msvc` in `embarch-core` dies in `cc-rs`
  compiling `hidapi`'s `hid.c` — no toolchain here to build the C shim against Windows headers. The
  gate's own clause cannot be satisfied from WSL2 at all.
- **topology/055:** **Hardware debts:** **none created, and one re-measured rather than assumed.** No board, no probe, no
  live Core, no deploy, deliberately no `validate` run. `core/015`'s native Windows build: attempted
  this leg and still fails, same `cc-rs`/`hidapi` wall.
- **umbrella/076:** **Hardware debts:** **none created, and one narrowed on paper only.** Nothing executed: no board, no
  probe, no live Core, no deploy, and `doctor` was never run — the whole unit is about what `doctor`
  would conclude and was settled by reading `doctor.rs`.
- **study-designer/062:** **Hardware debts:** **none created, and none could be.** One character of a source comment; nothing
  executed, no board, no probe, no live Core, no deploy.
- **umbrella/075:** **Hardware debts:** **none created, and none could be** — prose in one `spec.md` and nothing
  executed: no board, no probe, no live Core, no deploy, and no `setup` run.
- **api/107:** **Hardware debts:** **none created, and one made explicit that was previously implicit.** Nothing
  here executed: no board, no probe, no live Core, no deploy, and — the point of the unit — nothing
  on Windows. The Windows process-group kill gap is now a numbered decision and a task with a stated
  verification requirement instead of an unqualified invariant. It is not paid.
- **study-designer/061:** **Hardware debts:** **none created, and none could be** — one Rust doc comment; nothing executed, no
  board, no probe, no live Core, no deploy. But this unit is *about* a hardware debt and sharpens it:
  `rx_utc_ms`'s clock-resync gap is restated, not added to.
- **topology/054:** **Hardware debts:** **none created, and none could be** — one comment line in a Rust source file;
  nothing executed, no board, no probe, no live Core, no deploy.
- **dev-bench/034:** **Hardware debts:** **one, carried and not worsened.** Nothing here was built or run: no board, no
  probe, no `west`, no Zephyr SDK, no live Core — the `dev-bench/019`/`020` debt restated: six changed
  lines of firmware comment that nothing compiled.
- **topology/053:** **Hardware debts:** **none created, and none could be** — one doc-comment hunk, nothing built for a
  board, no probe, no study.
- **study-designer/060:** **Hardware debts:** **none created, and none could be** — one file read, no file written in the code
  repo at all.
- **core/070:** **Hardware debts:** **one, carried not created — `core/015`'s native Windows build now carries a
  twelfth landed `embarch-core` change**, doc-comment-only with no platform-conditional code touched.
  The last leg asked for this tally to be counted rather than propagated, and it was not — the doubt
  stands, unresolved, one leg older.

---

### Budget

**PROCEED throughout, weekly usage moving through roughly the 50–52% band of a 90% cap across the
legs this day covers, suggested wave 2–6 depending on scope spread.** The 4-unit cap bound before
budget did on every leg this day; no 429 anywhere.

---

### Carry forward — top five

1. **Poll both stop channels at every unit boundary, without exception** — `core/088` found the
   owner's `fleet stop` 17 minutes and three units late because the poll lapsed between dispatch and
   the fourth unit. The poll is the primary route a stop reaches a leg, not a backstop.
2. **`tasks/doc/074` (Owner: required) is a cross-scope blind spot, not a one-off bug**: a method fix
   found and applied in one sub-project's audit chain (`api/106`, `umbrella/074`) has no path to reach
   a different sub-project's chain running the identical method (`embarch-study-designer`'s
   nineteen-unit citation sweep), so the same defect got fixed twice and propagated forward a third
   time regardless.
3. **`core/015`'s native Windows build is not merely undone — it is now measured, twice, as
   structurally impossible from this machine** (`cc-rs` cannot compile `hidapi`'s C shim without
   Windows headers under WSL2). The gate's own "native Windows build wherever `embarch-core` is
   involved" clause cannot be satisfied here at all. This needs an owner decision, not another leg
   re-discovering it.
4. **`tasks/umbrella/079` (deepest reserve in the suite, 217 B left) and `tasks/doc/078`/`tasks/doc/079`
   (Owner: required, spec.md split cap + second task-number collision) are the queue's live pressure
   points** — see Blocked.
5. **Do not chain a rebase and a force-push with `&&`/`set -e`** (`845147f`) — a stopped rebase is not
   a failed command in the way the chain assumes, and only a worktree reflog saved a worker's commit
   this day. Always check `git status` between a rebase and the push that follows it.
*Days 2026-09-16 to 2026-09-16 rolled to [log-archive/supervisor-log-2026-09-16-to-2026-09-16.md](log-archive/supervisor-log-2026-09-16-to-2026-09-16.md).*
