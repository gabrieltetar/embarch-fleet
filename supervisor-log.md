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

## 2026-09-14 01:04 — ui/053 the split that was the right answer and had nowhere to land

**Decided:** **nothing numbered, and the unit's real product is a refusal.** `embarch-ui/open.md`
went **4,033 B → 3,879 B**, out of reserve with 154 B clear — but the task asked it to re-open the
split-vs-squeeze question, and the answer it came back with is the part worth keeping. Four things.

**(a) The seam is real and the tooling cannot hold it.** `ui/050` squeezed this file out of reserve,
`ui/051` refilled it four units later with a bullet a reviewer had required, and the task filed
against that argued the 5,120 B cap is simply tight for the number of live questions `embarch-ui`
carries — so **look for a seam before squeezing a third time.** The worker found one (the trace,
second-stream-placement and row-cap bullets share a reader) and then found it could not use it:
**`check-doc-size.py`'s `CAPS` defines a mission-split role for `decisions.md` and `interfaces.md`
and none for `open.md`**, so a split file matches no named role and falls through to `legacy` — 25 KB,
unratcheted, and described by the script's own comment as debt to migrate *out of*. Splitting today
would move four questions' worth of content out from under the size discipline the rest of the corpus
gets, which is moving the debt rather than paying it. So it squeezed and said exactly why, in the
commit message, as the task required.

**(b) `scripts/` is reserved, so it dropped the gap instead of closing it — and that is the rule
working.** I drained that drop in this same fold as **`tasks/doc/062`**, re-checking its
`Hardware:` claim myself (a regex and a `DOC-BUDGET.md` §3 paragraph — `none` is right) and keeping
the worker's own text. It is `Owner: required`, so nothing dispatches it; it is in the queue so the
owner sees it. **Its own "why now" is the line to read**: `DOC-BUDGET.md`'s rule is that a split is
the default and a squeeze the exception, and **the exception is currently forced on every `open.md`
in the suite by a tooling gap rather than by the absence of a seam.** If this file hits reserve a
third time, squeezing stops being defensible and there will still be nowhere for the split to go.

**(c) The five cuts were quoted and the reviewer counted them, including the one that was not a
deletion.** Two clauses redundant with a decision citation two words away, one provenance clause
`embarch-ui` decision 11 already carries in more detail, one filler word, and one clause **reworded
rather than removed** — the reviewer diffed at word level, confirmed exactly five deleted spans
against exactly five quotes with no sixth, and specifically checked the reworded one, finding
`"real HTTP"` surviving verbatim inside the sentence that absorbed it.

**(d) The `Must not delete:` list held, and it is the one that has already failed once.** Its first
item exists because a reviewer caught its predecessor being deleted in `ui/051`; all three of the
trace-analysis bullet's load-bearing facts are present verbatim and outside the diff, and all seven
open questions still carry their own trigger and citation. The reviewer also read
`embarch-umbrella` decision 14 and `embarch-ui` decision 11's bodies to check the "already said
elsewhere" justification rather than accepting it — which is the reasoning that, when wrong, deletes
the only statement of a fact.

**Merged:** `agent/ui/053-compact-ui` — **code: none.** Zero commits beyond `origin/main`, confirmed
by commit count before landing. Doc `c70aae5` in `embarch-doc` (**cherry-picked**, from branch commit
`1a3319e`; `--ff-only` refused because `topology/044`'s fold had already moved `main`). Gate re-run
by me on the merge result: `cargo build` / `test` / `clippy --all-targets -- -D warnings` green in
`embarch-ui`; `check-client-names.py --repo embarch-ui` clean against 7 denylist entries;
`check-docs.py` **11/11**; `check-ownership.py --scope ui` OK on the doc half (3 paths), run before
the merge. `changelog.d/ui-open-out-of-reserve-again.changed.md` consumed into `history/ui.md` with
`--only`; 29 of the owner's own fragments left pending.

**Blocked:** nothing. `tasks/ui/053` closed and removed, which leaves the `ui` scope with no
dispatchable task. **The size-debt ledger is down from 15 dated entries to 13 across this leg's two
compaction units, 0 overdue**, and both `embarch-topology/` and `embarch-ui/` now have nothing in
reserve.

**Reviewer:** no findings — see (c) and (d); it did the word-level hunk count
`DOC-COMPACTION-PASS.md` assigns to the reviewer rather than reading the commit message's summary of
itself, and it read both cited decision bodies independently.

**Hardware debts:** **none created.** Five clause-level edits in a markdown file; nothing built,
nothing executed, no board, no probe, no live Core, no UI launched. Standing debts carried
unchanged, including `embarch-ui`'s 18-record stale prefix, which still has never met a real stale
prefix. The dev-bench probe is still unplugged — checked live at this leg's top, `status` returned
`"probes": []` — so `tasks/api/059` stays **open** for the fifth consecutive leg.

**Budget:** PROCEED — weekly **85.7%** of a 90% cap, resets in ~54h. The leg ends on the owner's
`fleet stop`, not on the budget or the unit cap.

**Least sure about:** **that the drop and the squeeze together let a bad outcome look like a good
one.** The unit ends with the file out of reserve and a well-argued task filed, which reads as
success — but the substance is that this file has now been squeezed twice in four units for the same
reason, and `tasks/doc/062` is owner-required, so nothing in the fleet can act on it. If nobody
reads it, the third squeeze will arrive and the same argument will be made a third time.

---

## 2026-09-14 00:57 — topology/044 seventy bytes, two sentences, and a reserve line that is not ten percent of anything

**Decided:** **nothing numbered** — a 70-byte trim decides nothing. **But a `fleet stop` arrived
from the owner at 00:55:44 while this unit was landing, and that is the most important fact in this
entry.** What I did about it is (d).

**(a) The pass is clean and the human question answers yes.** `embarch-topology/spec.md` went
**9,110 B → 9,001 B** (87.9%), out of reserve, confirmed by `check-doc-size.py --pressure` rather
than by arithmetic — the whole point of this task, since `topology/043` hit a target it computed
itself from 10% of the cap and the gate still went red. The ledger is **15 dated entries → 14**, and
`embarch-topology` now has nothing in reserve at all. My own answer to
`DOC-COMPACTION-PASS.md`'s question, having read the diff: **yes.** What went was the clause
*"previously ad hoc across env vars, config files and doctor checks"* — a *used-to-be* lead-in whose
subject is fully stated by the two bullets immediately after it — and the parenthetical *"(one
flash, one reset, one study attempt)"*, three examples of an operation, where the rule they
illustrate is untouched and still cites decision 29 by number. Neither is a constraint, an
invariant, a rejected alternative or a failure signature.

**(b) The squeeze quoted its cuts, and it did so because it was told mid-run.** I sent both
compaction workers a course correction after dispatch pointing at `DOC-COMPACTION-PASS.md`'s rule
that a squeeze's commit message lists every deleted hunk as the first dozen words of the deleted
text, verbatim and file-qualified, with a category summary permitted only *after* those lines. This
worker replied that it had verified the rule against the file itself before acting rather than
taking my word for it, and the commit message does exactly what the rule asks. **I should not have
needed to send it** — the rule is in a file the worker is expected to read for any compaction, and
the dispatch prompt named the human question but not this. That is a gap in my prompt, not in the
worker.

**(c) The reviewer did the count, which is the half of that rule that is explicitly its job.** Two
hunks in the diff, two quoted in the message, no third deletion anywhere in the commit; it located
both hunks by line (6-9 and ~107) and showed they fall outside the protected probe-selection bullet
(90-96) and the Shape consumer-call table (23+); it read `ad3f642`'s message and confirmed none of
`043`'s seven cuts was restored; and it read decision 29's body in `decisions/scope.md` to confirm
the deleted parenthetical was illustration and not the only statement of the rule.

**(d) The stop, and what "finish landing what is in flight" cost.** I polled `#embarch-fleet` at this
unit boundary — the poll `.claude/leg.md` calls the *primary* route, not a backstop — and found
`fleet stop`, posted 00:55:44, about a minute old. **I deleted `/home/gabriel/Github/embarch/.fleet/pump` immediately**, which
is the supervisor's own stop-direction act and the thing that prevents a successor, and posted in
that message's thread without reacting to it, so the listener can still claim and confirm it. Then I
kept landing: `ui/053`'s worker had already finished and pushed, and `api/095`'s was mid-run. **I
did not kill the running worker.** I sent it a wrap-up instruction instead — verify only what it has
already read, report the honest count, say the sweep was cut short rather than completed, and file a
remainder task — which bounds the extra time without throwing the work away or leaving a claimed
task behind. Dispatching anything further would have been the actual violation, and I dispatched
nothing.

**Merged:** `agent/topology/044-compact-topology` — **code: none.** The code branch carries zero
commits, and I confirmed that by commit count against `origin/main` before landing rather than
assuming it from the task's shape. Doc `32caf10` in `embarch-doc` (**cherry-picked**, from branch
commit `3ca94a8`; `--ff-only` refused because `core/062`'s fold had already moved `main`). Gate
re-run by me on the merge result: `cargo build` / `test` / `clippy --all-targets -- -D warnings`
green in `embarch-topology`; `check-client-names.py --repo embarch-topology` clean against 7
denylist entries; `check-docs.py` **11/11**; `check-ownership.py --scope topology` OK on the doc
half (3 paths), run before the merge.
`changelog.d/topology-spec-out-of-reserve.changed.md` consumed into `history/topology.md` with
`--only`; 29 of the owner's own fragments left pending.

**Blocked:** nothing. `tasks/topology/044` closed and removed, which leaves the `topology` scope with
no dispatchable task at all.

**Reviewer:** no findings — see (c); it performed the hunk count `DOC-COMPACTION-PASS.md` assigns to
the reviewer specifically, rather than agreeing with the commit message's own summary of itself.

**Hardware debts:** **none created.** Two sentence fragments deleted from a markdown file; nothing
built, nothing executed, no board, no probe, no live Core. Standing debts carried unchanged — see
the `core/062` entry below for the `core/015` Windows-build count, which I re-derived there (**40
commits since `1c1224e`**, not the ordinal the last five days have been incrementing). The dev-bench
probe is still unplugged and `tasks/api/059` stays **open**.

**Budget:** PROCEED — weekly **85.7%** of a 90% cap, resets in ~54h, wave 3 suggested and 3 used.
The leg ends on the stop, not on the budget.

**Least sure about:** **letting `api/095`'s worker keep running after a stop.** `.claude/leg.md` says
honouring a stop means finishing what is in flight, and a dispatched worker is in flight — but it
also warns about "a full leg of unwanted work after the owner asked you to stop", and a worker five
minutes into a twenty-minute run is the case the rule does not name. I chose the reading that wastes
no work and leaves no stranded claim; the other reading is defensible and would have stopped sooner.

---

## 2026-09-14 00:54 — core/062 a comment that claimed another repo's text was unchanged, and the one beside it that correctly said nothing

**Decided:** **nothing numbered.** A one-line comment correction is not a decision and does not want
to be one. This is leg 115's first unit. Three things, and one of them is about this leg rather than
this unit.

**(a) The clause was false and is now true, and the worker checked which half of it was false.**
`embarch-core/src/logs.rs`'s module doc ended *"`embarch-ui`'s own text is unchanged"* — written by
`core/058` to be accurate at its landing, and falsified hours later when `ui/052` added a dated
blockquote correction under `embarch-ui` decision 7's stale size-capped-logfile sentence. **The
sentence itself was not rewritten** — `ui/052` deliberately left it standing as the record of an
abandoned proposal — so "unchanged" was wrong about the *file* and right about the *sentence*, and
the new clause says exactly that: the sentence stands, and now carries a dated correction. The
reviewer compared the new clause against `ui/052`'s actual blockquote at `ui/052`'s own fold commit
`e9018e9` and found it a near word-for-word match in substance.

**(b) The interesting half is what the worker did *not* change, and it did not take my word for it.**
The task named two comments. `src/main.rs`'s `build_log_file_writer` comment (lines ~375-379) makes
no claim about `embarch-ui`'s text at all — it only cites what decision 7 *says*, which is still
literally true of that sentence — so it was left alone. **Changing nothing was named in the task file
as a legitimate outcome and half the unit took it.** The reviewer read that comment independently at
the merge SHA rather than accepting the worker's account, which is the check that makes the
half-outcome trustworthy.

**(c) I filed `tasks/doc/061` from something I found in this leg's own step 0, not from this unit.**
Three `agent/*` branches were still on `embarch-doc`'s remote; `git cherry origin/main <branch>`
reports two of them (`api/096-...-doc`, `core/052-...`) as **unmerged, and always will**, because
their content landed by a cherry-pick that *conflicted* and a conflict resolution is a different
patch id by construction. `fold-commit.py` retires a branch only on `git cherry`'s `-`, so those two
are permanently stranded — `core/052` since 2026-09-13. Not data loss (I verified both branches'
content is on `main` by diffing each against `origin/main`), but **step 0's scan treats a pushed
branch carrying commits as proof a worker finished**, so a stranded branch is a false positive for
finished work against a rule whose whole strength is that presence never lies. Owner-required;
`scripts/` is reserved.

**Merged:** `agent/core/062-core-comments-vs-ui-052` — code `1073bf7` in `embarch-core`
(fast-forwarded, parent `e1b796e`), doc `7e851c1` in `embarch-doc` (fast-forwarded, parent
`04020d8`; `--ff-only` was accepted because this was the leg's first fold and nothing had moved
`main` under it). Gate re-run by me on the merge result: `cargo build` / `test` (**209 passed**, 2
ignored, plus 1) / `clippy --all-targets -- -D warnings` green; `check-client-names.py --repo
embarch-core` clean against 7 denylist entries; `check-docs.py` **11/11**; `check-ownership.py
--scope core` OK on the doc half and `--code-repo` OK on the code half, both run **before** the
merge. `changelog.d/core-logs-unchanged-clause-vs-ui-052.fixed.md` consumed into `history/core.md`
with `--only`; 29 of the owner's own fragments left pending.

**Blocked:** nothing. `tasks/core/062` closed and removed. `tasks/core/060` (compact
`decisions/streams.md`, due 2026-09-27) is untouched and still `open`, deliberately not dispatched
beside this unit — one task per sub-project per slot.

**Reviewer:** no findings — it checked all three things I asked and gave evidence for each: it read
the corrected `debug-tab.md` at `ui/052`'s own fold SHA rather than at this unit's (and said so,
correcting my spawn prompt, which had given it this unit's doc SHA for a file `ui/052` changed
earlier), read `src/main.rs`'s comment itself to confirm leaving it alone was right, and read
`embarch-core` decision 16's body plus all four reversal row files to confirm nothing contradicts.

**Hardware debts:** **one, carried not created — and I counted it, which retires a carry-forward and
contradicts every recent entry.** 2026-09-13's day fold asked the next leg to *"count the commits, do
not trust the ordinal — including mine"*, so: `core/015` landed as `1c1224e` (*"core: fix --version
leaking a log warning onto stdout"*), and **`git log --oneline 1c1224e..HEAD` in `embarch-core` is
40 commits**, this unit's included. The entries of the last five days called the same debt the
ninth, tenth, eleventh, twelfth and thirteenth landed change. **None of those is the number, and the
basis for any of them is unrecoverable** — each was copied from the entry before it and incremented.
Use **40 since `1c1224e`** and re-derive it the same way rather than incrementing this. The pile
includes `core/061`'s `source_deferred` field, which *does* change what the service serves,
`core/045`'s route-wiring test, and the `suite/020`/`suite/035` wire-feature split; this unit itself
is a single comment line and nothing behavioural moved. Standing debts otherwise
unchanged — **the dev-bench probe is still unplugged**, checked live at this leg's top
(`status` returned `"probes": []`), so `tasks/api/059` stays **open**, not `blocked`, for the fifth
consecutive leg; `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`).

**Budget:** PROCEED — weekly **85.0% → 85.7%** of a 90% cap across this unit, resets in ~54h, wave 3
suggested and 3 used.

**Least sure about:** **giving the reviewer this unit's doc SHA for a file another unit changed.**
It caught the error itself and read `ui/052`'s fold commit instead, which is the right answer — but
it caught it because the file was *obviously* not this unit's. A reviewer handed the wrong SHA for a
file the unit *did* touch has no such tell, and nothing in the spawn shape would surface it.

---

## 2026-09-14 00:31 — outpost/022 a clean sweep, and its reviewer found the same scope overstatement one layer down

**Decided:** **nothing numbered** — 0 wrong citations means nothing to decide. This is the leg's
fourth and last unit. Four things to carry.

**(a) The sweep is clean and that is the headline: 22 citations, 0 wrong numbers, 0 false sentences.**
This is the other half of `outpost/021`, which called itself a whole-repo sweep and had in fact
grepped only `.c`/`.h`. The worker re-derived the scope rather than trusting the task's file-and-line
list — the list was taken before leg 113's own `8f6e667` landed — and found **three citations the task
never listed** (`tests/run-all.sh:40`, `tests/native_sim_stream/assert_stream.py:85`,
`.github/workflows/host-tests.yml:9`), all correct. It read every one against the decision's **body**,
across `manifest.md`, `naming.md`, `clocks.md`, `layout.md`, `tracing.md`, `wire.md`, `testing.md` and
`module.md`.

**(b) The reviewer found the recursion, and it is the finding worth keeping.** The commit message says
*"every non-`.c`/`.h` file"*; the grep's include list was `Kconfig*`, `*.py`, `*.sh`, `CMakeLists.txt`,
`*.yml`/`*.yaml`, `*.rst`, `*.cmake`. A bare case-insensitive grep turns up **4 more citations in 3
file classes nobody scoped**: `README.md` (×2), `cmake/outpost_build_id.h.in`, and
`tests/native_sim_stream/app.overlay`. **The reviewer read all four against their decision bodies and
all four are correct**, so there is no defect behind the overstatement — but this is the *third*
consecutive time in this repo that a sweep's scope claim outran its grep, which is the exact shape
`022` existed to fix in `021`. I corrected `history/outpost.md`'s line to say what was actually
covered, by whom, and deleted the drop rather than filing `outpost/023`: there is no unswept surface
left, only a sentence that claimed more than it did.

**(c) Two things the worker checked that a clean report usually hides.** All 6 pre-topic-split
citations (`decisions.md decision N`) still resolve after the split, verified independently by the
reviewer; and leg 113's own `gen_outpost_manifest.py:613` fix still reads `(interfaces/wire.md)` — the
sweep did not revert or re-touch the one line it was told to leave alone.

**(d) I filed `tasks/doc/060` from something this worker decided not to report.** It hit
`check-decision-refs.py`'s `DEF_HEAD` regex matching `###`/`####` only, judged it a formatting quirk
with no observed false negative, and folded it into its report instead of dropping it. I verified the
mechanism and disagree about the size: **`suite/decisions/*.md` uses `##`**, so all four `suite`
decision definitions are invisible to the resolver, and the script reports **877 of 1,995 references
"ambiguous ... not an error"** — 44% of the corpus unchecked, in the one scope that is cited from
every repo. Owner-required; `scripts/` is reserved.

**Merged:** `agent/outpost/022-citation-sweep-non-c-sources` — **code: none.** The code branch carries
zero commits by design; a sweep that finds nothing wrong edits nothing. Doc `e8364bc` in `embarch-doc`
(**cherry-picked**, from branch commit `e4e9f3e`). Gate re-run by me on the merge result:
`embarch-outpost` has no `Cargo.toml`, so the host-side surface is the whole gate —
`tests/decoder_unit.py` (**31 tests**) and `tests/vocab_check.py` green in the worker's own run, repo
`main` unchanged at `8f6e667`; `check-docs.py` **11/11**; `check-ownership.py --scope outpost` OK on
the doc half (2 paths). **Nothing was built for a board and no DUT was attached.**
`changelog.d/outpost-citation-sweep-non-c-sources.changed.md` consumed into `history/outpost.md` with
`--only`; 29 of the owner's own fragments left pending.

**This fold also carries the 2026-09-13 day fold and a roll.** An `embarch-log-folder` subagent folded
**78 numbered units (80 landed sub-units)** into one dated entry — 471,249 B down to 69,325 B, with
`--apply`'s ledger satisfied on 263/263 SHAs, 80/80 `**Reviewer:**` lines and 48/48 hardware-debt
lines — then `--roll`ed 2026-09-12 into
`log-archive/supervisor-log-2026-09-12-to-2026-09-12.md`. **It was owed on this leg's first unit and
landed on its fourth**, because a 471 KB day took it 22 minutes and six chunk-readers; I folded three
units past it rather than stall four landed units behind it, which is safe only because `fold-day.py`
splices the day's own block and never rewrites the retained text. Its own two carry-forwards: the
`core/015` Windows-build tally was narrated with three different ordinals through the day (count the
commits, do not trust the ordinal — including mine), and reviewer completions misrouted to the
listener **five** times that day (`tasks/doc/042`).

**Blocked:** nothing. `tasks/outpost/022` closed and removed, so the `outpost` scope is back to no
dispatchable task (`002` is `blocked`, `018` is `Hardware: required`). **`tasks/doc/060`** filed per
(d).

**Reviewer:** 1 finding — `inbox/outpost-citation-sweep-missed-file-classes.md`, **accepted, verified
by me, and acted on in this fold** by correcting the `history/outpost.md` line rather than filing a
follow-up sweep; drop deleted once the correction landed. See (b) for why the correction is the whole
fix.

**Hardware debts:** **none created, and none of this leg's four units touched hardware at all.** Worth
stating for this unit in particular because it is the one firmware repo the leg entered: no board, no
flash, no DUT, no Zephyr build — `tests/run-all.sh` stops at its `WEST` guard by design on this
machine. `embarch-outpost`'s two hardware-gated tasks are untouched and still waiting on a board.

**Budget:** PROCEED throughout — weekly **82.4% → 84.6%** of a 90% cap across the leg, resets in ~54h,
wave 5 suggested and 4 used.

**Least sure about:** **deleting the reviewer's drop instead of filing `outpost/023`.** Every citation
it named checks out, so a sweep task would have nothing to sweep — but I am the third actor in a row
to declare this repo's citation surface finished, and the previous two were wrong for the same reason
each time. If a fourth file class exists that neither the worker's include list nor the reviewer's
bare grep reached, nothing in the queue is now looking for it.

---

## 2026-09-14 00:19 — api/096 the client half of decision 63, and a tool description that disclaims a field instead of promising it

**Decided:** **nothing numbered.** This is the `embarch-api` half of the split described in the
`core/061` entry above; the one judgement it contains is the worker's, in (b). Three things.

**(a) The two halves agree on the wire, and that was checked rather than assumed.** Both were written
in parallel against a field name I pinned before dispatch, neither read the other's branch, and the
reviewer verified against the landed `embarch-core` merge (`e1b796e`) that both spell it
`source_deferred`. `StudyStreamEntry` in `crates/embarch-core-client/src/client.rs` now carries it as
the fourth `#[serde(default)] Option<bool>`, documented on the three points its neighbours document:
what `Some(true)` means, what `Some(false)` means, and that `None` is a Core predating the field.

**(b) The worker refused a box in its own task file, and was right to.** I wrote *"check whether
`streams_json` needs to surface the flag — if it renders the other three booleans, it renders this
one."* It does not: `streams_json` iterates `StreamRef` from `embarch-study-designer`, which carries
`name`/`bytes_written`/`truncated`/`records` and has never carried `named`/`timed`/`self_excluded`
either. So the conditional I wrote was false, no code change was owed there, and **the new sentence in
`list_study_streams`' description says the listing does not carry the flag rather than implying it
does** — "…which this listing does not carry, so do not read a 0 here as ruling it out". A tool
description promising a field the tool does not return is exactly the failure this unit could have
shipped; the reviewer read `StreamRef`'s definition itself to confirm both halves.

**(c) The worker also fixed my link-depth bug on its own file** — the `../../embarch-fleet/protocol.md`
citations described in the `ui/052` entry — using three `../` as a real markdown link, which is the
better form and is what landed. Its `inbox/` drop naming the same bug in `tasks/core/061` I deleted
rather than filed: I had already fixed that half on `main` before reading it.

**Merged:** `agent/api/096-deferred-source-flag-client-half` — code `c26d930` in `embarch-api`
(fast-forwarded, parent `3e0e4ba`), doc `99a166c` in `embarch-doc` (**cherry-picked**, from branch
commit `caee440`; `--ff-only` refused because two folds had already moved `main`, and the cherry-pick
**conflicted** on the task file — resolved to the worker's version, which is the one the fold then
removed). Gate re-run by me on the merge result: `cargo build` / `test` / `clippy --all-targets --
-D warnings` green; `check-client-names.py --repo embarch-api` clean against 7 denylist entries;
`check-docs.py` **11/11**; `check-ownership.py --scope api` OK on the doc half (2 paths) and
`--code-repo` OK on the code half. `changelog.d/api-source-deferred-flag.added.md` consumed into
`history/api.md` with `--only`; 29 of the owner's own fragments left pending.

**Blocked:** nothing. `tasks/api/096` closed and removed — filed, claimed, run and closed inside one
leg. `tasks/api/095` (the 103-citation sweep of this same `client.rs`) was deliberately **not**
dispatched beside it and is still `open`; it is now the `api` scope's only dispatchable task, and it
opens on a file this unit has changed.

**Reviewer:** no findings — it answered all four questions with evidence rather than agreement: read
the three neighbouring doc comments and compared them clause by clause, read `StreamRef`'s definition
to confirm (b) independently, showed the serde test fails both without `#[serde(default)]` and when
the field is never populated, and checked the field's spelling against `embarch-core`'s actual merge
rather than against the task file that pinned it.

**Hardware debts:** **none.** A deserialized struct field and a tool description string; no board, no
probe, no live Core, no deploy. The end-to-end confirmation this half participates in is recorded
against `core/061`, not here.

**Budget:** PROCEED — weekly **82.4%** of a 90% cap at the leg's start, resets in ~55h, wave 5
suggested and 4 used.

**Least sure about:** **that `list_study_streams`' description now carries a sentence about a field
that endpoint does not return.** It is honest and it is the only place a reader of that tool would
look — but it points at `GET /study/{id}/streams` for the real answer, and a description that
explains a neighbouring endpoint's field is a shape nothing in this suite has decided is right.

---

## 2026-09-14 00:18 — core/061 decision 63's Core half, and the split that made it a worker's job at all

**Decided:** **one thing, and it is mine rather than the worker's: the field is named
`source_deferred`, and I pinned it before dispatch.** Decision 63 deliberately left the name open
("name it for the fact, not for power"), which is fine for one implementer and impossible for two
running in parallel. The roadmap's own word for power sampling is *deferred, not cancelled*, so the
name carries the general fact and a second deferred source later fits the same field. Four things.

**(a) The split is the structural part of this unit.** `tasks/core/061` as filed spanned **two code
repos** — `embarch-core` sets the flag, `embarch-api`'s client crate deserializes it and its
`tools.rs` describes it — and §5 gives a worker one task in one repo on one branch. I narrowed `061`
to `embarch-core` and filed the other half as **`tasks/api/096`**, claimed both, and ran them side by
side against the pinned name. Neither half waits on the other: `#[serde(default)] Option<bool>` means
either can land first. **The alternatives I rejected**: one worker with two code worktrees (breaks the
one-repo rule and the land-both-branches-together shape), and re-scoping to `suite` so I would run it
myself (a §4 announcement window for an implementation whose design decision was already announced and
decided by leg 113).

**(b) Set at declaration, not inferred from silence — which is the whole point of decision 63.**
`StreamStore::create` sets `source_deferred` from the tap's declared `StreamSource` in the same loop
that fills every other index field, before a byte exists, with `note` carrying the prose and a
citation of `embarch-dev-bench` decision 24 at the site. Core *states* the fact; it does not measure
it. Two structs carry it (`StreamIndexEntry`, `StreamIndexEntryResponse`), 209 tests pass, and the new
test puts a `PowerFrontEnd` tap and a `GattTranscript` tap side by side at `bytes_written: 0` so the
only difference is this field.

**(c) `note` was left alone, and the reviewer checked that specifically.** The cheap version of this
change was to set `note` and stop. `StudyStreamEntry`'s own history forbids it in writing — the
`is_named` comment records the conjunction that *"stopped being correct when a trace gained a second
way to be incomplete"* — and the diff branches on `note` nowhere.

**(d) No doc prose in `decisions/streams.md`, by instruction and correctly obeyed.** The file is
1,069 B inside its cap with `tasks/core/060` filed against it; decision 63's entry was already
written by leg 113. The worker documented the field in `interfaces/studies.md` and
`interfaces/result-layout.md` instead, which is where a reader of `GET /study/{id}/streams` looks.

**Merged:** `agent/core/061-power-tap-says-so-in-stream-index` — code `e1b796e` in `embarch-core`
(fast-forwarded, parent `2e9eeed`), doc `d95dc58` in `embarch-doc` (**cherry-picked**, from branch
commit `f7d20a6`; `--ff-only` correctly refused because `ui/052`'s fold had already moved `main`).
Gate re-run by me on the merge result: `cargo build` / `test` (**209 passed**, 2 ignored, plus 1) /
`clippy --all-targets -- -D warnings` green; `check-client-names.py --repo embarch-core` clean against
7 denylist entries; `check-docs.py` **11/11**; `check-ownership.py --scope core` OK on the doc half
(4 paths) and `--code-repo` OK on the code half.
`changelog.d/core-power-tap-source-deferred.added.md` consumed into `history/core.md` with `--only`;
29 of the owner's own fragments left pending.

**Blocked:** nothing. `tasks/core/061` closed and removed. `tasks/core/060` (compact `streams.md`) is
untouched and still `open`.

**Reviewer:** no findings — it checked the three things I asked and gave evidence for each: the flag is
set from the declared `StreamSource` inside `StreamStore::create` rather than derived from
`bytes_written`; nothing in the diff or the surrounding file branches on `note`; and the new test is
non-vacuous **in both directions** (setting the flag unconditionally fails the `None` assertion,
never setting it fails the `Some(true)` one). It also read `embarch-dev-bench` decision 24's body and
confirmed the code comment's claim is a faithful restatement rather than a stretch.

**Hardware debts:** **one, and it is the first behavioural addition to it in a while.** `core/015`'s
outstanding **native Windows build** now carries a twelfth landed `embarch-core` change, and unlike
the comment sweeps and test recoveries of the last five days this one changes what the service
*serves*. Separately, decision 63's end state has never been seen on a real study: confirming that a
`PowerFrontEnd` tap reports `source_deferred: true` through a live Core needs the **dev-bench board**,
and `tasks/core/061` said so before it closed. No board, probe or live Core was touched here.

**Budget:** PROCEED — weekly **82.4%** of a 90% cap at the leg's start, resets in ~55h, wave 5
suggested and 4 used.

**Least sure about:** **pinning the field name myself.** It unblocked two parallel halves and both
landed spelling it identically, which is the outcome I wanted — but decision 63 left the name open on
purpose, and a supervisor closing an open question in a task file is a decision that never gets a
number and never gets reviewed as one. If `source_deferred` turns out to be the wrong name for the
second deferred source, nothing in the decision record explains who chose it or why.

---

## 2026-09-14 00:15 — ui/052 a retention sentence that was a proposal, marked as one rather than rewritten

**Decided:** **nothing numbered**, and the worker correctly filed none — but one judgement call was
made and is worth carrying. Three things.

**(a) The drop was true, and the worker checked it rather than trusting it.** `embarch-ui` decision 7
said retention is *"a size-capped rotating logfile rather than a time-based policy"*. `embarch-core`
builds no such thing: `src/main.rs`'s `build_log_file_writer` is `Rotation::DAILY` with
`.max_log_files(7)`, and `embarch-core/decisions/logging.md` decision 16 says so in prose — including
the line that `embarch-ui` *"had proposed a second size-capped logfile without knowing this one
existed."* So decision 7's sentence was the abandoned proposal, left standing unqualified.

**(b) The judgement: mark it as an earlier design, do not rewrite it as daily-rolling.** Both were
open. Rewriting would make decision 7 *read* correct and destroy the record of what was proposed;
`embarch-ui` has no retention policy of its own to state anyway, because decision 7's own text says
the UI never reads Core's logfile directly. So a dated blockquote correction sits under the sentence,
in the shape `embarch-outpost/decisions/clocks.md` decision 17 already uses. **Not a reversal** —
nothing decided changed, only a stale factual clause about another repo's mechanism.

**(c) The reviewer found the one thing that is genuinely missing, and it is not this unit's to fix.**
`DOC-CONVENTIONS.md` codifies the one-line retirement tombstone and **not** this blockquote-correction
shape, whose only textual precedent is `clocks.md` itself. The unit's commit message attributes the
style to `clocks.md` rather than to the conventions doc, so nothing here is misattributed — but the
suite now has two correction shapes and one of them is documented. `DOC-CONVENTIONS.md` is
owner-reserved; recorded here rather than filed, because it is a gap in a reserved doc, not a defect
in a sub-project.

**Merged:** `agent/ui/052-decision-7-retention-line-doc` — doc `e9018e9` in `embarch-doc`
(fast-forwarded, parent `e3e5569`). **Code: none.** `agent/ui/052-decision-7-retention-line` carries
zero commits by design — the worker grepped `embarch-ui`'s whole source for the stale claim and found
it nowhere, which is the outcome the task allowed for. Gate re-run by me on the merge result:
`check-docs.py` **11/11**, `check-ownership.py --scope ui` OK on 3 paths.
`changelog.d/ui-debug-tab-retention-line.fixed.md` consumed into `history/ui.md` with `--only`;
29 of the owner's own fragments left pending.

**A gate correction that matters more than the unit.** This worker — and, later, two of the other
three — reported `check-links.py` RED and called it *"pre-existing baseline noise"* from
`embarch-fleet` being an empty stub in a worktree. **It was not pre-existing: it was mine.** The two
task files I wrote at the top of this leg (`tasks/api/096`, and my edit to `tasks/core/061`) cited
`../../embarch-fleet/protocol.md` **as a markdown link**, and two `../` from `tasks/<scope>/` lands on
`embarch-doc`'s own tracked `embarch-fleet/` sub-project directory, not the sibling repo. Three
workers in a row diagnosed a red gate as environmental and were wrong, and only re-running the gate
myself on the merge result caught it. Fixed in this fold; `api/096`'s worker independently fixed its
own half on its branch with three `../`, which is the better form and is what landed.

**Blocked:** nothing. `tasks/ui/052` closed and removed. Two `inbox/` drops drained in this same fold:
**`tasks/core/062`** (the worker's own finding — `embarch-core`'s `src/logs.rs` comment says
*"`embarch-ui`'s own text is unchanged"*, which this unit made false) and **`tasks/doc/059`**,
owner-required, the worktree-nesting defect described in my final report. A third drop
(`core-061-task-file-fleet-link-depth.md`) was deleted rather than filed: it named the link bug above,
which was already fixed on `main` by the time I read it.

**Reviewer:** no findings — it re-derived Core's rotation from `main.rs` at the real SHA, confirmed
decision 7's *decision* is untouched by the diff, re-ran the `size.cap` grep across both `embarch-ui`
tips and the whole `embarch-doc` tree itself rather than trusting the worker's, and traced the
"missing" inbox drop to `tasks/core/062` rather than reporting a lost finding.

**Hardware debts:** **none.** Doc prose in one decision file; no board, no probe, no live Core, no
deploy, nothing built.

**Budget:** PROCEED — weekly **82.4%** of a 90% cap at the leg's start, resets in ~55h, wave 5
suggested and 4 used.

**Least sure about:** **that leaving decision 7's sentence standing is kinder to a future reader than
rewriting it.** The correction is directly underneath and dated, so nobody reading the file top to
bottom is misled — but somebody grepping for `size-capped` still lands on a false sentence first, and
that is exactly how this defect reached `embarch-core`'s source comments in the first place.

---

## 2026-09-13 — 78 units

*Folded by leg 114 on 2026-09-14 at 00:16 MDT. Eighty landed sub-units — 78 numbered task
headings plus two (`core/050`, `study-designer/038`) that landed nested inside a sibling
unit's own entry the same leg — collapse here with every SHA, every `**Reviewer:**` line
and every `**Hardware debts:**` line preserved. What is gone is the narrative reasoning
behind each accepted judgement and the per-unit gate output; git holds the first in
`embarch-fleet` history up to this commit, and every gate was re-run green on the merge
result before landing, per §10, all day.*

**The day was almost entirely one campaign: a suite-wide dead-citation sweep**, dispatched
across every repo by a run of "refill from `open.md`" legs once the hand-authored queue ran
dry around midday. Of the 78 numbered units, roughly 60 were citation/doc-comment sweeps or
the compactions and splits that fed them; five were `suite`-scope decisions executed by a
supervisor directly; the rest were code fixes the sweeps turned up. Aggregate scale: **well
over 900 citations read against their own decision bodies across nine repos**, on the order
of **35–40 real defects** found and fixed, at wildly different rates by file
(`embarch-core`'s dirtiest sweep was 10-in-109, `embarch-study-designer`'s worst was
5-in-36, several repos ran multiple **zero-defect** sweeps in a row). That unevenness is
itself the day's headline finding, below.

### Decided

**Five suite-scope decisions, three of them binding and two of them deliberate refusals.**

- **`suite/018` (20:15) — new suite decision 4**, in `suite/decisions/placement.md`: which
  sub-project holds a computation more than one path needs. Executed directly by the
  supervisor (no worker branch); the previous leg's own 30-minute announcement window had
  already closed unanswered at `ts 1789348880.412099` and was **not** restarted, per §4.
  Filed `core/057` to give it a code half. `core/057` (21:12) landed **embarch-core decision
  62**, computing the outpost power-tap answer once in `embarch-core` — but the result is
  **two implementations, not one**: `embarch-ui`'s `trace.rs` still independently derived the
  same arithmetic until `ui/051` (23:04) retired the 520-line duplicate later the same leg.
  Even after `ui/051`, decision 4 is **half true**: aggregation moved, but `embarch-ui` still
  independently derives Lane/Span/Gap from the shared data — a reviewer caught a changelog
  line in `api/094` that overclaimed decision 4 as fully closed before that retirement
  landed, and fixed it in-fold.
- **`suite/029` (23:22) — new embarch-core decision 63**: the `StreamSource::PowerFrontEnd`
  tap's answer shape (`StudyStreamEntry` gains a fourth boolean field). Resolved an
  announcement this leg had itself parked (`ts 1789358454.801729`) for a fourth worker slot.
  Filed `core/060` and `core/061` to implement; closed with 3 of 4 `Done when` boxes still
  unticked, carried into `core/061`.
- **`suite/010` (10:34) — new embarch-study-designer decision 74**: `firmware_version` keeps
  its name on every surface; **declined** the rename decision 47 had already made for a
  sibling defect class, and explicitly split the HTTP-only half out as `suite/036` rather
  than deciding it here. Also found and fixed, unprompted, that `main` had been left
  non-buildable under `--locked` since `suite/035` landed the day before (a stale
  `Cargo.lock` in `embarch-ui`/`embarch-umbrella`) — the supervisor's own `cargo check`
  surfaced it, and a reviewer separately caught the supervisor having "talked herself into"
  a wrong claim about what a new test's name implied. Announcement window inherited from leg
  103, not restarted, ran unobjected roughly 10.5 hours after it closed at `ts
  1789277838.510359` (00:07); re-polled at 10:21 to confirm silence.
- **`suite/036` (11:32) — declined again**: `GET /dev-bench/hello` keeps `firmware_version`
  for now. The argument *for* declining was itself arithmetically wrong (a citation
  misattributed decision 58 to what is actually decision 60 — the leg's only non-zero
  reviewer finding, landing on the one class of unit with no worker and no other outside
  read) and was corrected further than the reviewer's own finding asked. Announced 10:40
  (`ts 1789317643.030479`), closed 11:11, ran unobjected. Split the doc half done from the
  rename itself, which stays undecided.
- **`suite/038` (16:33) — retirement**: `artifact_path_for_core` retired across
  `embarch-api` **and** `embarch-umbrella` together, amending decision 64 and re-scoping
  doctor check 9 (chain table plus operator-facing text) — a cross-repo binding change.
  Completed a 30-minute owner-announcement window a now-dead prior leg had opened at `ts
  1789336383.873349` and never closed, after confirming 31 minutes had passed with no
  objection.

**One more cross-repo decision, sub-project-scoped but suite-relevant: `core/055` (18:39) —
new embarch-core decision 61**, closing a fork that decision 22 opened back in August when
one probe-selection rule silently forked into two copies (`embarch-core` and
`embarch-topology`) with three behavioral divergences, unfixed until now. `topology/041`
(19:26) and `topology/038` (18:05) both independently rediscovered the same drift class
from the topology side the same day, confirming it as a real, repeating shape rather than a
one-off — `topology/037` (17:23), `core/053` (16:41) and `core/047` (12:00) each record a
smaller instance of the identical class (a shared computation copy-pasted across a repo
boundary, only one copy ever exercised, and nothing failing because nothing tested either
copy).

### The recurring defect classes a day of sweeping actually taught

1. **"Real text, wrong subject"** — a citation that resolves to a real decision, in the
   right repo, with nothing wrong about the number, that simply has nothing to do with the
   code it annotates. Independently named in `umbrella/067`, `core/050`, and `topology/040`
   (whose comment survived **three weeks and two prior handling passes**, including one that
   added a *new* citation to the same wrong sentence, before anyone noticed its subject no
   longer existed). No gate can see this class; `check-decision-refs.py` only resolves
   numbers, and this number resolves.
2. **Same-number collision** — a bare `Decision N` is ambiguous when two repos independently
   number their own decisions past N. Found in `umbrella/064` (embarch-umbrella's own
   decision 13 vs. embarch-api's) and `study-designer/044` (study-designer's own decision 29
   vs. dev-bench's), two days running.
3. **The dirty-file hypothesis** — the same handful of files (mostly in `embarch-core` and
   `embarch-study-designer`) that restate other repos' decisions account for almost all of
   the day's defects, while most repos ran multiple clean sweeps in a row. `core/056`
   (10/109, breaking a clean streak) and `study-designer/046` (5/36, the worst rate of the
   day) both landed on this "dirty end"; `umbrella/066` was the **fifth consecutive
   zero-defect sweep** in that repo the same day. Whether three-plus clean sweeps in a row
   means a corpus is actually healthy, or that sweeps have converged on always-clean files by
   picking-by-size, is flagged and unresolved (`ui/049`).
4. **A doc-mission split breaks links no gate can see.** `api/087`'s verbatim split of
   decision 67 broke three cross-repo links in `embarch-ui`, `embarch-topology` and
   `suite/studies-guide.md`; `api/092`'s split broke four, one inside a *source code*
   comment. In both cases only a supervisor could fix it, because the splitting repo's own
   worker scope cannot touch the repos whose links broke. Filed as `doc/044`, expected to
   recur on every future split.
5. **A split can silently drop machinery that keys off the split file.**
   `decision-size-baseline.json` pins a size baseline by `<file>#<decision-number>`; a
   verbatim split (`umbrella/059`) orphans the pin with the gate staying green throughout.
   Filed `doc/052`, **Owner: required**, three unranked fix-shapes offered.
6. **The byte-budget floor, not the percentage, usually governs.** `topology/043`'s task
   file computed its target from "90% of cap," but the real gate is
   `max(RESERVE_FLOOR=1200B, (100-RESERVE_PCT)%)`, and the 1200-byte floor dominates for any
   cap under roughly 12,000 bytes — most of this corpus. The file landed 70 bytes inside
   reserve and the gate went red on a clean compaction. Filed `doc/058`, owner-required.
7. **A size figure in a task file is a measurement with a timestamp, and nothing marks it as
   one.** `topology/042`'s dispatch note quoted a headroom figure that was stale by the time
   the unit ran (real margin was 3 bytes, not the ~9,000 the note claimed); flagged as the
   second class of stale fact a task file can carry (the first, from `doc/030`, is a
   `Compacts:` line).

### Standing defects in the supervisor's own process, found more than once today

- **Reviewer completions misrouted to the listener instead of the supervisor — five
  separate instances in one day** (`core/056`, `umbrella/066`, `api/092`, `ui/050`,
  `core/050`, `dev-bench/029`, `dev-bench/022`'s reviewer — the count kept climbing through
  the day). All recorded against `tasks/doc/042`. `ui/050`'s entry is the important one:
  "what saved the unit is that I was waiting on the reviewer rather than proceeding without
  it" — had the fold run first, it would have carried a false Reviewer line silently.
- **A "LOST FINDING" escalation, `study-designer/038`**: a reviewer could not find an inbox
  drop the worker's own report claimed existed. Root cause was the supervisor's own habit —
  draining a drop at the merge instead of at the fold, before the reviewer had run. Confirmed
  a false alarm; filed `doc/042` as its fifth recorded instance. Two more of the supervisor's
  own mistakes are named in the same entry: telling a worker "not in scope: any change to
  embarch-study-designer's source" when the intent was "no logic change," and the worker
  correctly pushing back on a wrong header-convention instruction copied from a different
  repo.
- **"Thumb on the scale" task-file leads, two legs running, same sub-project.** `core/052`
  and `core/053` (consecutive units) both record the supervisor writing a candidate repair
  into the task file before dispatch, which is "an instruction that names the intended repair
  before the derivation" — biasing the worker rather than asking it to check. `core/054`'s
  own entry independently records that **all three of the supervisor's own "known leads"
  that day turned out false** — "a supervisor's lead is a hypothesis."
- **Mechanism gotchas, each hit more than once:** `check-ownership.py` without
  `--code-repo --stdin` false-flags a code repo's own source files as ownership violations
  (third leg to hit it, `core/051`); `check-task-state.py`'s title-substring match went red
  on `main` from the supervisor's own task-file title, twice the same day
  (`core/052`, `umbrella/061`), fixed by rewording the title rather than touching the
  reserved script; `fold-commit.py`'s `git rm` refuses a task file the fold itself just
  edited (`study-designer/041`) — the fix is to `git rm` before folding, not after correcting
  `State:`, filed `doc/050`; `git worktree add` resolves relative paths against the repo, not
  the caller's cwd, caught and worked around twice (`suite/036`, `suite/010`).
- **Two no-op units from recovering leg 103's orphans** (`ui/041`, `dev-bench/028`): both
  cases where an earlier fold had already applied a reviewer's finding *and* filed a task
  describing the same finding as still outstanding — the same shape `fa0a327` recorded once
  already. `dev-bench/028` also recovered leg 103 itself, killed mid-flight with three
  workers finished and pushed; the supervisor reset to `origin/main` and redid every landing
  under a full gate rather than inherit half-finished worktree state, rather than risk
  compounding it — "nothing was lost by the kill," flagged as possibly overcautious.
- **"State: claimed" left behind instead of "done."** Recorded as a pattern (not a one-off)
  in `umbrella/067` and `api/093` the same leg, and separately in `core/055`,
  `topology/041`, `umbrella/064`, `ui/047`, `study-designer/041`, `dev-bench/028` — harmless
  today because the supervisor closes them at fold time, but `check-task-state.py` accepts a
  claimed task whose body says done, so a leg that does not look would leave a completed task
  sitting in the queue.
- **A queue-mechanics dead end, named explicitly by `api/081`**: fourteen doc files sat in
  size-reserve behind a rule that could never release them — `In flux: yes` mechanically
  forces a compaction task to `blocked`, and a file that is both in reserve *and* actively
  being edited (the common case) has no path to payment until the churn stops, which nothing
  makes happen. The way out, used repeatedly through the day (`api/081`, `api/086`,
  `study-designer/035`, `topology/039`, `ui/043`, `umbrella/059`, `study-designer/038`): a
  **verbatim mission split**, which `DOC-COMPACTION.md` §2 and `DOC-BUDGET.md` line 47
  already named as the cheaper move, citing a 2026-09-05 precedent where a 96-byte-short cap
  once misfiled a decision into the wrong topic file entirely.

### Hardware

**No board, no probe, and no live Core was ever touched today.** The dev-bench probe stayed
unplugged for every one of the roughly twenty times it was checked — live at `GET /status`
early (probe `001057729826`, recorded `hardware_id 6fcddc36cb781b71`, live `None`) and
repeatedly thereafter — and `tasks/api/059` stayed `open` throughout, climbing across
"third," "fourth," "fifth," "sixth," "seventh" consecutive-leg mentions before the day ended.
`fleet-hardware.py --refresh` still crashes (`tasks/doc/041`); its cached buffer went from
roughly 8,400 minutes stale mid-afternoon to well past that by evening.

**`core/015`'s outstanding native Windows build of `embarch-core` picked up another landed
change on nearly every `core`-repo unit today** — the running count was narrated
inconsistently through the day (a `suite/018` note at 20:15 called it "fourteen changes
deep," while `core/057` at 21:12 called the same pile "a ninth landed change," and
`core/059`, the day's last core unit at 23:31, called it "eleventh... fifth consecutive
day") — **nobody is maintaining one source of truth for this tally, and the next leg should
count landed commits directly rather than trust the narrated ordinal.** What is not in doubt:
by day's end the pile included a genuinely new HTTP route and module (`core/057`), not only
comments and tests, and the Windows service build does not serve that route until the build
actually runs — nobody has run it in at least five consecutive days of additions.

**Two new never-run-against-a-live-Core debts were created today**, both flagged as the same
shape one day apart: `api/094`'s new `study_stream_load` MCP tool, and `ui/051`'s Trace tab,
now depending on a live Core route at runtime for the first time. Neither needs its own
board beyond whatever capture a real study produces; both are the owner's to exercise through
a live session.

### Merged

Every unit's gate was re-run by the supervisor **on the merge result**, per §10: `cargo
build`/`test`/`clippy --all-targets -- -D warnings` wherever Rust was touched, `check-docs.py`
(11/11 throughout), `check-client-names.py`, and `check-ownership.py` on both halves. Every
unit landed clean; the only gate reds recorded were transient and diagnosed in-leg (a
concurrent worker's `cargo test` causing a false 100x timeout in `api/087`; the byte-budget
miscalculation in `topology/043`; the task-title substring false-positives above) — none
reflect a real defect surviving to `main`.

| Unit | SHAs (code + doc + parents, as landed) |
|---|---|
| `outpost/021` | `7cb71d5`, `94db7d1`, `1450c08` |
| `core/059` | `2e9eeed`, `3cbe6977a08fa7964cd5553b842c8f707db793a0`, `42e0db0` |
| `study-designer/048` | `1c99d7f`, `26fd908a1b982890fd8212d8cf2c1207a43ce47c`, `4f8271f` |
| `suite/029` | — (supervisor's own hands, no worker branch, no merge SHA) |
| `ui/051` | `87d01b4`, `37061a59bf065567ae27283f207b591fe7449730`, `ffeaebf`, `fd90452b5ac283d27d44fbfc43ea5fc1493aa093` |
| `core/058` | `3cbe697`, `a131f6334df1dba3218b3858a834b84e8b482128`, `4edd897`, `f7cff4d0a91879f37f2e64f904f6397a2978f85b` |
| `study-designer/047` | `26fd908`, `5a8bcb509f60ccd097ab1aa1842cc22ff98e4bfe`, `9c8270e`, `a413965570cf2d85762c33ab8de15150ea97776b` |
| `topology/043` | `ad3f642`, `10c157baf6fa1823b04c6db041a4b340bd84c751` |
| `api/094` | `3e0e4ba`, `92f598bd5f405b234e2585c5355a1a961131476d`, `5b04745`, `ea38325` |
| `ui/050` | `69e3715`, `1880d4f` |
| `study-designer/046` | `5a8bcb5`, `03eef2e82ff06d75126564661bf80c878f6ecabc`, `70f6f3c140676031f0b9626e0b8e65bd83f4f9aa`, `7872076` |
| `topology/042` | `020d03b316f84f6c86e92f7b798f78afe90086bd`, `0ef88ed6ee1a414f04ee60a22c643ec26bf049ea` |
| `umbrella/067` | `3c6565b`, `9eb450b`, `5ff18f1`, `ebf7971` |
| `api/093` | `92f598b`, `f2f1de2`, `73dd14f`, `b0287df` |
| `core/057` | `a131f63`, `4de0e41`, `886a0bc`, `b8249c4` |
| `topology/039` | `2b3a694`, `c9216d3` |
| `api/091` | `f2f1de2`, `1001899`, `1fe5b8b`, `49a17ce` |
| `topology/040` | `8161092`, `96e86c6`, `49a17ce`, `8415c07` |
| `study-designer/045` | `03eef2eb8a8c`, `a850a2d`, `8415c07`, `f484ad5`, `94fb61f` |
| `suite/018` | `f484ad5ef38cdcc959be91e68c626c0f1181a922`, `94fb61f` |
| `core/056` | `70109bd5753e60990c73368513a83a19fa8b00ef`, `86345c01a451b0696af36f42c28bf6676478124c`, `a66e38ea782f9584aa0f888697362c9f258ae17a`, `0bec5df7fcbb4f13483fa6ed96c6bf8e4737c578`, `4de0e415997fdc363eca470d1adac984b14cf8f4` |
| `umbrella/066` | `4844a1cba9aa7037ab4c26b6169ae95db7dff684`, `065648296a6bc0ee5a76867f24eb095221dd42cb` |
| `api/092` | `2900a27fcde659d52548fea759e89f615ae46e0f`, `be04f9e8a6410bf9aedd36fad3a7a541566c4540`, `74fec6e5ae5d65b3ef8ac2f32c361a4843e3cc66`, `642a277a2db46d8f30374b43703a0803e02c8471`, `100189939825b966088d33bfbb8d1b3af6283f2a` |
| `topology/041` | `f93139fbd7e256d1ac7f640bade19f3e03e1313a`, `3b655c3d8012edbad0fd63d89a4ebbdf3bf7320d` |
| `ui/049` | `37061a59bf065567ae27283f207b591fe7449730`, `c31d3cd49dd27d3b2b0a346b205c6589555a5a8d`, `16e1ae0c6552f38717d8f9472a378f4ccd836b11`, `c20f2b740f9a9930eb746289bdb1280eb3bb394e` |
| `api/088` | `be04f9e8a6410bf9aedd36fad3a7a541566c4540`, `54f0c3e3483f0c1c33f19861cd462bc00ddca6f1`, `6ef2131809969c4606e4816ab2a3c01f6d5b0a05`, `16322c3179f436bd78b3f0bd96f1b0813d89cff8` |
| `study-designer/044` | `a850a2d62483b7fc2446958972db45b65522e4a8`, `7cfef952f3b826298d2609ea20c049ac1e88765f`, `b79d0577e3c78fd94124f38058b8e3e72081991a`, `a1b4a59a98cb3a4c51b5eca264b6e4df94e14e1f` |
| `core/055` | `86345c01a451b0696af36f42c28bf6676478124c`, `e4b5b728ddafeaf7833a1f515257ca50acba05dd`, `16e7515a3663fb72c763e5f94e537605556dbfeb`, `701013accc494f4d277759d6dfa28b2bb427324e` |
| `umbrella/065` | `9eb450b11cc2293c275f9555cda01e6d8f926cee`, `551e33c4f9716f3725c927c926d5a7e32a76afa5`, `0a5d453851814b913554153bbe58c2f91b126250`, `3b2d9d5ef4edb5f119ed1cffdae77472a2dd320f` |
| `api/087` | `54f0c3e3483f0c1c33f19861cd462bc00ddca6f1`, `24ddc597770239ee2b75d89818a715884f72d414`, `d5f3895`, `739ff618995cd93cb1ee333a65a6fa671cb58025` |
| `topology/038` | `96e86c68cc3383a7dd491ff3dfb5394f5a93f547`, `9dc44dd5abea801915ee9079b9a30ded1d96d373`, `b98b53b7fb214d8e9f6a6aec3b18817b330f42de`, `d7f3b6e76a8952f08478adbb2be2dec94ceca277` |
| `umbrella/064` | `91e75f545e89ca0680386674291f21baecd31d2b`, `a840f96eb2401ec8b6ca6f8d201422d9b7faa7e1` |
| `api/086` | `c2f1e41dd8244d20188dd7fd12187f29d729e620`, `aac4f0bd479d023b0c2058ce83dfdb9ef68482bc` |
| `umbrella/063` | `551e33c4f9716f3725c927c926d5a7e32a76afa5`, `f4bf2cdc46b2ebeb5c1a2b10618f0567c1bc550b`, `6b5fd27ed98e3375e5e2aeeb76faa405101bbe6e`, `25c1750de3e042be971ae502cd41138a192c7712` |
| `core/054` | `e4b5b728ddafeaf7833a1f515257ca50acba05dd`, `49bc726a656bc7b7ce25ce76b369e8b4ec2c8a72`, `7ecc0b8df8924aac4b2f06925e38d80e1d3fd636`, `45c16b2ad55e155ef82c77ac36dc7f0b97d5be7c` |
| `topology/037` | `9dc44dd5abea801915ee9079b9a30ded1d96d373`, `e51f7edd7d16a6afe7f8daa44b5a1158235b77ef`, `d7c51a8dfd9c40a4215b7fe1f6e38781280d28f4`, `1608e85be87f34b4a09c1de8e4a23ced2e84e050` |
| `umbrella/062` | `4f4d7b1fcede2fa50fada17f800fd38d8db8ac4b`, `a8026d17cf7d2e6a759bbe584e0f3b45881eaf82`, `54615b7adc3f204cb2232f3cba0eb34c33ca0af4`, `e38cdc7`, `d3787b3` |
| `core/053` | `d71c45a5877ea24d640516cc2ce6cda752084a27`, `49bc726a656bc7b7ce25ce76b369e8b4ec2c8a72`, `f7f6918` |
| `ui/048` | `c31d3cd49dd27d3b2b0a346b205c6589555a5a8d`, `609bdaa6a0fc56db28545e76b1724d5c0e2e4c2e`, `39e4951`, `fccdda8` |
| `suite/038` | `a8026d17cf7d2e6a759bbe584e0f3b45881eaf82`, `f4bf2cdc46b2ebeb5c1a2b10618f0567c1bc550b` |
| `core/052` | `49bc726a656bc7b7ce25ce76b369e8b4ec2c8a72`, `f852fa8d29088a29be0655456ce6ecf70713bb60`, `c77fcc2015f1b907269bf4e25a53338440c8a745`, `dda7d6c` |
| `ui/047` | `609bdaa6a0fc56db28545e76b1724d5c0e2e4c2e`, `29147b533b3b322a7283a53b86575e3224437a91`, `cf49004a6e988055b9283032ead2efbffa614562`, `252752f`, `29bc092` |
| `api/085` | `44a7d4cf7a15e6a5f54d259e6f0f2ac9fff0d248`, `43ee85176356ba21b43e8aef15c87ef89b3df9cc`, `24ddc597770239ee2b75d89818a715884f72d414`, `10b3d5a5e43e2bd254942b2bcb62116cc7f3d82a`, `7920aee` |
| `umbrella/061` | `f4bf2cdc46b2ebeb5c1a2b10618f0567c1bc550b`, `319f035795f15adb396e38e69fa29d243c431e19`, `34cf627f048df476f2f0d0ad23efd337ca97bb08`, `9fd1684`, `5dcfc88` |
| `api/084` | `77a8998320a5917c230afae675476ff4f3727e36`, `cd1bc2fe5dce126c63c31fb7b5b6ef1903efc5c9`, `43ee85176356ba21b43e8aef15c87ef89b3df9cc`, `54e2093833bef3b3d8afaa812169a9895e6c0c8e`, `42af222` |
| `umbrella/060` | `b9452abd164cbf57fc54c45bcd49942a0fb1b0fe`, `eacfb361c0cfde570116222688844a5ed45fb54e`, `319f035795f15adb396e38e69fa29d243c431e19`, `ce3a917b0adb7918a6429680c61b26aa2bcc7151`, `ebefeca` |
| `core/051` | `f852fa8d29088a29be0655456ce6ecf70713bb60`, `53f1ed183f99c7976876c73c655fe1f907902812`, `681854f81c05432c1a063614b9bca20e8f7205f9`, `21e2eed`, `3a3bd32` |
| `study-designer/043` | `cb48e51ce8e6786cedfede356141c748b7d2dbb4`, `a5ea68ebcd353b038841718063d8804d480d652c` |
| `study-designer/042` | `7cfef952f3b826298d2609ea20c049ac1e88765f`, `2eaa7f5fecdb3857069a992863939a0eacdec27e`, `42864a9b4000d29693d68160e440461f05da676e`, `0a5958e` |
| `ui/046` | `29147b533b3b322a7283a53b86575e3224437a91`, `6963544767f77a05dec422aab917b490ee748441`, `a14f12bd15d346024f6a899eed3c050b00d436b6`, `734c527` |
| `study-designer/041` | `4087964e742cde8db3d2f9c64e5101eb7b136c76`, `6fd2218f6d5d7255487b9dbde903793c6f7d4ddb`, `2eaa7f5`, `e4e6079`, `734c527` |
| `ui/045` | `6963544767f77a05dec422aab917b490ee748441`, `364afe3e38c9fbac9192673a024d9303d0c531b6`, `310ead64165e1b12526370119d370d3660e0bcbd`, `d8d3f4edb9bb887371fb245588f73c6dd79db17e` |
| `api/082` | `253b8f1`, `b87c526`, `b87c52639d07` |
| `study-designer/040` | `2eaa7f5`, `419e196`, `834decc`, `be9efce`, `be9efcee6f5c` |
| `ui/044` | `364afe3`, `e4d10ac`, `7885fdb`, `c4dd375`, `d6e703e`, `c4dd3750a4c7` |
| `study-designer/039` | `419e196`, `efbf76e`, `21909b6`, `d6e703e`, `efbf76e80a19`, `d6e703e0bfe2` |
| `study-designer/038` | `8b4b574`, `5a5fb52`, `a90abb995e92cf8808f833fcf061cb0407565e52` |
| `umbrella/059` | `979af88`, `fcb3bdf`, `3ffa8304a34f157b0f342fc4401736ecbb8a9b91` |
| `dev-bench/030` | `8ff290bbd539465562b506ef407c526403a4f978`, `3ffa8304a34f157b0f342fc4401736ecbb8a9b91`, `242c9e2`, `59ea8484f57034f6fc45f8de5a23b7e826fd05ca` |
| `api/081` | `59ea8484f57034f6fc45f8de5a23b7e826fd05ca`, `c1bbff0`, `43d18f51fef41d0bc00159a695d7bf717210d09f` |
| `core/050` | `f3424d8508eeb2f7fcb2b88eee08ae699694b775`, `d58206cbb263988d28e1bff79f5e1ae10dda3196` |
| `dev-bench/026` | `c133703573648f1c4d959f04ccd509d5ba8c400f`, `d0cf9a0` |
| `ui/043` | `61fa53ae704469f2811a8cd5cbed0057f637bde4`, `c133703`, `d0cf9a0` |
| `outpost/020` | `60bb955bca1f93bad35a4ce063453625e7568e14` |
| `dev-bench/029` | `4816230`, `7210b5a` |
| `topology/036` | `e51f7ed`, `56777eb` |
| `api/080` | `cd1bc2f`, `76e75af` |
| `ui/042` | `13a528c`, `e4d10ac` |
| `umbrella/058` | `9adaa1a`, `eacfb36` |
| `dev-bench/022` | `15c8796`, `38cadda`, `eae8205` |
| `study-designer/036` | `5bbc0bc`, `efbf76e` |
| `core/047` | `f50b5a6`, `53f1ed1` |
| `suite/036` | `72e8b12`, `265c8ff`, `6f369d3` |
| `outpost/019` | `94db7d1`, `6dc5251` |
| `dev-bench/021` | `68821a7`, `768f98e` |
| `study-designer/035` | `01d1642` |
| `suite/010` | `7914352`, `3a1920f`, `efbf76e`, `53f1ed1`, `e4d10ac`, `eacfb36` |
| `topology/035` | `5aead72`, `8c37a15`, `9c32dc7` |
| `ui/041` | `7efa9ab`, `bba6cbc`, `46a8202` |
| `dev-bench/028` | `e1cd955`, `656516b`, `f9b192b` |

**Additional SHAs cited in reviewer archaeology and process notes, not in a Merged/Blocked
line above:** `ui/049` recorded that its logged parent was wrong — the script said `609bdaa`
but the true parent, verified via `git branch -r --contains`, was `c31d3cd` (`ui/048`,
landed earlier the same leg from a worktree never pulled into the owner's checkout); both
are preserved here because the correction matters more than the number. `core/055`'s own
merge SHA is also written short-form as `86345c01` inside `topology/041`'s text.
`outpost/021`'s supervisor-authored follow-up fix is `8f6e667`, pushed directly to
`embarch-outpost`. `study-designer/046`'s reviewer independently re-derived the decision
56/57 boundary from the split commit `d0b7608`. `outpost/019`'s own decision-ref-checker red
(caused by the supervisor's own task file, twice) was fixed at `d830771` before anything
else landed on top. `umbrella/058`'s reviewer settled a scout's wrong "does not exist" claim
by running `git show e63ce13:src/state.rs` and finding the quote there verbatim. `ui/041`
names its own recurring shape as `fa0a327` — a fix applied in-fold *and* filed as an
outstanding task in the same leg, the second such instance. `dev-bench/026`'s reviewer
archaeology traced `eap.h`'s history with `git log --follow`, which stops at `1190b72`.
`umbrella/067`'s duplicate was traced with `git log -L` to sweep commit `5131ec7`.
`api/080`'s two wrong-at-birth counts were root-caused to their introducing commits
`57d27f7` and `3041549`. `topology/037`'s citation was checked against `embarch-core` commit
`b8da819`'s own `resolve_probe` comment. `topology/037`'s own repo history citation is
commit `956f07c`. `ui/044`'s citation-count history across three prior states of the same
file reads `132` (`fcf5c1e`), `163` (`d6877bd`), and `155` (`dc5de2b`, current); the `doc`
commit `4cfd0db0` landed twelve minutes after `fcf5c1e`. `ui/044`'s spot-check baseline
reaches back to `13493e2` (2026-08-24). `study-designer/041`'s doc branch was cut before
`3cd6770` and needed a rebase to fast-forward. `core/057`'s rebase-as-cherry-pick left the
owner's own checkout exactly where it started, at `7937e45`. `dev-bench/022`'s reviewer
traced the `BleAddress` correction to `79a4c00`. `ui/045`'s reviewer traced a stale
"2026-08-15" date through history to `9500811`, rather than accepting it at face value.
`core/047` filed its refill task as `9a37a39` (`study-designer/036`). `api/080` and `ui/042`
both cite `validation-classifier.md`'s birth at `a40fd32` with 25 sites from the start.
`umbrella/061` filed two tasks at commit `d32a400`. `study-designer/036`'s citation cross-
check reaches `src/snapshot.rs:21-29`, repointed from decision 54 at commit `3d2f870`. The
dev-bench probe's own identifiers, checked live and unplugged throughout the day, are probe
`001057729826` and recorded `hardware_id 6fcddc36cb781b71`. The five suite-unit announcement
timestamps are `ts 1789277838.510359` (`suite/010`, inherited from leg 103), `ts
1789317643.030479` (`suite/036`), `ts 1789336383.873349` (`suite/038`, inherited from a dead
prior leg), `ts 1789348880.412099` (`suite/018`, closed unanswered by the previous leg), and
`ts 1789358454.801729` (`suite/029`, parked by this leg for its own fourth unit).

### Blocked

**Nothing landed in `blocked` state all day.** Every one of the 78 numbered units closed
`done` or was folded directly by a `suite`-scope supervisor action. The only near-misses were
transient gate reds, diagnosed and cleared within the same leg (see Merged above) rather than
left for the queue.

### Reviewer

**Reviewer:** 1 finding — `inbox/outpost-gen-manifest-decision-4-miscite.md`, accepted and fixed in-fold. — `outpost/021`. Its own completion notification was misrouted to the listener, the day's first instance of that pattern.
**Reviewer:** no findings — verified the test adaptation strengthened rather than narrowed the deleted tests' original semantics; confirmed no contradiction with core decision 62 or suite decision 4. — `core/059`
**Reviewer:** no findings — independently re-derived all three citation fixes and resolved a scope ambiguity as imprecise rather than contradictory. — `study-designer/048`
**Reviewer:** no findings — independently re-derived decision 63 as a free decision number and answered the wire-bump question from decisions 50 and 58 rather than opinion. — `suite/029`
**Reviewer:** 1 finding — `inbox/doc-ui051-timeline-duplication-not-retired.md`, accepted and fixed in-fold: the code commit overclaimed suite decision 4 as fully true before the retirement it described had landed. — `ui/051`
**Reviewer:** no findings on the sweep itself, but confirmed the escalated cross-repo miscite: two comments claimed an `embarch-ui` decision had been "corrected in place," and no such correction exists anywhere. — `core/058`
**Reviewer:** no findings — and this is "the strongest reviewer result this log has recorded": independently re-verified the 301-citation remainder list as clean, the first time a zero tally was checked rather than trusted. — `study-designer/047`
**Reviewer:** no findings — traced all seven deleted restatement hunks back to their owning decision files, confirmed nothing lost. — `topology/043`
**Reviewer:** 1 finding — `inbox/doc-api-094-changelog-overclaims-decision-4-closure.md`, accepted and fixed in-fold; also verified a hand-mirrored three-struct type copy field-for-field against embarch-core's real types. — `api/094`
**Reviewer:** no findings — but its completion again reached the supervisor via the listener rather than directly, the second instance in one leg. — `ui/050`
**Reviewer:** no findings — and this is the unit where I most wanted one: independently re-derived the decision 56/57 boundary from the split commit's own history and confirmed the worker's backward-seeming correction was actually right. — `study-designer/046`
**Reviewer:** no findings — re-derived decision 33's three behaviors against live source rather than decision text, confirmed no restatement of what a prior unit had moved out. — `topology/042`
**Reviewer:** no findings — verified decision 7 is silent on resolution order by checking every decision that mentions conventional directories, not just the cited one. — `umbrella/067`
**Reviewer:** no findings — verified the decision-18-creation-date claim from git history and spot-checked 20 of the 73 untouched citations. — `api/093`
**Reviewer:** no findings — grepped all eight forbidden geometry symbols and confirmed the "computed once" scope claim directly against source. — `core/057`
**Reviewer:** no findings — diffed the pre- and post-split paragraphs one by one against the decision-size baseline. — `topology/039`
**Reviewer:** no findings — re-derived the split, spot-checked six more citations, confirmed the reversals doc silent on the relevant decisions. — `api/091`
**Reviewer:** no findings — independently confirmed decision 32's close and the retirement date of `GET /enroll` against the reversals doc. — `topology/040`
**Reviewer:** no findings — re-derived all four corrections, spot-checked eight more citations, and independently flagged a related decision-17 risk of its own. — `study-designer/045`
**Reviewer:** no findings — but caught one over-reach in the supervisor's own reasoning, an invariant argument stretched past its scope; corrected in-fold. — `suite/018`
**Reviewer:** 1 finding, escalated — caught a worker rewrite that introduced a *new* false cross-repo misattribution about an `embarch-topology` decision, "the exact defect the unit existed to remove." — `core/056`
**Reviewer:** 1 finding, escalated — overturned the worker's own self-adjudicated "defensible either way" citation call, ruling it not defensible: "a sweeper adjudicating its own doubt, caught." — `umbrella/066`
**Reviewer:** 1 finding — `inbox/api-088-dispatch-timeout-context-review.md` — plus independently caught a fourth broken cross-repo link the supervisor had missed in her own manual repair; both accepted and fixed in-fold. — `api/092`
**Reviewer:** no findings — thorough re-derivation of the closing note's three clauses against the pinned merge SHA. — `topology/041`
**Reviewer:** no findings. — `ui/049`
**Reviewer:** 1 finding, escalated — the dispatch-timeout fix stamps every `send()` failure with the same false "(request timeout Ns)" regardless of actual cause, landing in the machine-readable field decision 50 deliberately left unstructured; filed rather than fixed in-fold for lack of doc headroom. — `api/088`
**Reviewer:** no findings. — `study-designer/044`
**Reviewer:** no findings — worker had left the task `claimed` rather than `done`; caught and fixed in fold. — `core/055`
**Reviewer:** no findings. — `umbrella/065`
**Reviewer:** no findings on the worker's own diff — the false gate-red diagnosis and the three cross-repo link repairs were the supervisor's own hands, and its completion again reached the supervisor via a coordinator relay rather than directly, the third such instance. — `api/087`
**Reviewer:** made one incorrect claim — asserted an inbox drop "does not exist," when the drop was gitignored and simply invisible from the reviewer's own worktree; the supervisor overruled it and confirmed the drop was real. — `topology/038`
**Reviewer:** no findings — caught the embarch-umbrella-vs-embarch-api decision-13 same-number collision on an otherwise clean sweep. — `umbrella/064`
**Reviewer:** no findings — filed `umbrella/064` after finding one stale bare-filename citation in a different repo's own decisions file. — `api/086`
**Reviewer:** no findings. — `umbrella/063`
**Reviewer:** no findings — but the sweep itself refuted all three of the supervisor's own written "leads," each independently checked and found false. — `core/054`
**Reviewer:** no findings — confirmed the cross-repo drift as a third instance of a known class in `embarch-topology/open.md`. — `topology/037`
**Reviewer:** no findings — found one real dead citation the worker's four fixes had missed, a target gone stale four days earlier; fixed and the drop deleted. — `umbrella/062`
**Reviewer:** no findings — but the task file itself carried a repair baked in before dispatch, the same mistake as the following unit's entry records one leg later. — `core/053`
**Reviewer:** no findings. — `ui/048`
**Reviewer:** no findings — this is a `suite`-scope unit with no worker branch; the diff reviewed is the supervisor's own. — `suite/038`
**Reviewer:** no findings — the worker independently filed the same title-substring gate defect the supervisor had already found and fixed. — `core/052`
**Reviewer:** no findings — noted, unprompted and unfiled, one further pre-existing dead pointer for the next refill to pick up. — `ui/047`
**Reviewer:** 1 finding — `inbox/api-client-rs-decision-14-route-misattribution.md`, the same wrong phrasing already landed at five sites across two units; accepted and fixed in-fold. — `api/085`
**Reviewer:** no findings — the queue was effectively empty of dispatchable non-`suite` work, a standing risk noted rather than a citation defect. — `umbrella/061`
**Reviewer:** 1 finding — `inbox/api-084-list-study-streams-does-not-answer-mid-study.md`: the worker's own replacement fix answered nothing mid-study either; caught because the reviewer's first question was the worker's own justification. — `api/084`
**Reviewer:** 1 finding — `inbox/umbrella-doctor-rs-cross-repo-link-depth.md`: the worker's unrequested seventh fix was backwards and broke a working link by copying a broken precedent; accepted and fixed in-fold. — `umbrella/060`
**Reviewer:** no findings — the worker independently filed the same `check-ownership.py --code-repo` gate gap the supervisor's own note records. — `core/051`
**Reviewer:** no findings — independently reached the same "prose, not a numbered decision" conclusion from unrelated precedent. — `study-designer/043`
**Reviewer:** no findings — noticed unprompted corroborating evidence, a sibling function that already cited the correct decision. — `study-designer/042`
**Reviewer:** no findings — verified the thirteen-site substitution against existing citation convention unprompted. — `ui/046`
**Reviewer:** no findings — independently confirmed the worked example in the task file was itself factually wrong, the same fact the worker had already caught. — `study-designer/041`
**Reviewer:** no findings — declined to escalate one nuance (a citation "closer to" one file's wording than another's, but still resolving correctly). — `ui/045`
**Reviewer:** no findings — caught and cleared a near-miss between two different "five fields" concepts that could have been confused. — `api/082`
**Reviewer:** no findings — verified the *replacement* text against decision 48's own wording, not only the removal, and found one true-but-incomplete comment it deliberately declined to file. — `study-designer/040`
**Reviewer:** no findings — re-read the module doc at the merge SHA rather than trusting the commit message's own framing, which is how an overclaim in a related unit was caught at all. — `ui/044`
**Reviewer:** no findings — independently re-derived correctness of all six repointed citations. — `study-designer/039`
**Reviewer:** 1 finding, a LOST FINDING escalation — could not find an inbox drop the worker's report claimed existed; confirmed a false alarm caused by the supervisor draining the drop before the reviewer ran, the fifth recorded instance of misrouted/early-drained notifications. — `study-designer/038`
**Reviewer:** no findings — confirmed the split silently orphaned the decision-size-baseline pin, filed owner-required. — `umbrella/059`
**Reviewer:** no findings — its own completion notification reached the supervisor roughly four minutes late, worth the next leg knowing before declaring a reviewer dead. — `dev-bench/030`
**Reviewer:** no findings — flagged an honest gap, no worktree existed to verify two hits directly in two other repos. — `api/081`
**Reviewer:** no findings — independently re-ran the full sweep, got 244 and 141 hits, and confirmed the two apparent extra hits were the multi-line-split false positive the worker's own note had anticipated. — `core/050`
**Reviewer:** no findings on the merge itself, but caught two arithmetic slips in the worker's own closing note (six vs. eight hits, 22 vs. 21) inside a task file that gets retired and would never otherwise have been corrected; its own completion notification also failed to reach the supervisor. — `dev-bench/026`
**Reviewer:** no findings — demonstrated the split-first argument live and confirmed a live debt (decision 19's stale-prefix mechanism) was deliberately left untouched rather than compacted over. — `ui/043`
**Reviewer:** no findings — read `decisions/testing.md` decision 26 at current HEAD deliberately, since it had been corrected earlier the same day, rather than risk judging against superseded text. — `outpost/020`
**Reviewer:** no findings — its own completion notification reached the supervisor via the listener rather than directly. — `dev-bench/029`
**Reviewer:** no findings — confirmed no decision was renumbered and added a parenthetical to avoid implying one had been. — `topology/036`
**Reviewer:** no findings — confirmed by reading, not inferring, that a similarly worn-looking line elsewhere was legitimately past tense rather than stale. — `api/080`
**Reviewer:** no findings — re-derived all three fixture counts and confirmed the citation figures independently. — `ui/042`
**Reviewer:** no findings — but corrected a scout's wrong framing: a quoted comment reported as "not existing" was verified present at an earlier commit and rewritten twice since, which needs a different fix than a citation that was never right. — `umbrella/058`
**Reviewer:** no findings on the sweep, but caught two arithmetic slips in the worker's own closing note before it was retired; its own completion notification failed to reach the supervisor, the third instance of that pattern that day. — `dev-bench/022`
**Reviewer:** no findings — raised one minor nit about a false count in the follow-up task's own text, which the supervisor applied anyway in-fold. — `study-designer/036`
**Reviewer:** no findings — confirmed the worker's corrected decision number and independently verified the collapse of four dev-bench tasks into one. — `core/047`
**Reviewer:** 1 finding — `inbox/suite-036-decision-58-misattribution.md`, the leg's only non-zero finding, landing on the one class of unit with no worker and no other outside read; the supervisor corrected further than the finding itself asked. — `suite/036`
**Reviewer:** no findings — its code worktree had already been deleted when it ran, so it read code via `git show <SHA>` against the owner's own checkout instead, "safe, but luck rather than design." — `outpost/019`
**Reviewer:** no findings — flagged, without filing, three more unrecorded instances of the same defect class in a sibling file. — `dev-bench/021`
**Reviewer:** no findings — verified the split byte-for-byte and confirmed all four "must not delete" paragraphs survived intact. — `study-designer/035`
**Reviewer:** no findings — but caught the supervisor having "talked herself into" a wrong claim about what a new test's name implied. — `suite/010`
**Reviewer:** no findings — but found a fifth cut the supervisor had missed, a hedge dropped from a caching paragraph, recoverable via an adjacent citation but flagged as the shape compaction loss usually takes. — `topology/035`
**Reviewer:** no findings — this unit and the one after it are both no-op recoveries of leg 103's orphans, where an earlier fold had already applied the fix it also filed as outstanding. — `ui/041`
**Reviewer:** no findings — corrected the worker's own arithmetic, nine occurrences rather than the five originally claimed. — `dev-bench/028`

### Hardware debts, carried in the day's own words

*The 48 units below wrote a debt line the fold mechanism treats as owing something (the
other 32 wrote a plain "none" and are omitted here for length; their content is folded
into the Hardware section above). Reproduced verbatim, one unit per heading, per §11.*

### outpost/021
**Hardware debts:** **none created, and none of this leg's four units touched hardware at all.** Worth
stating for this unit in particular because it is the one firmware repo the leg entered: no board, no
flash, no DUT, no Zephyr build — only the host-side Python test surface. `embarch-outpost`'s two
hardware-gated tasks are untouched and still waiting on a board.

### core/059
**Hardware debts:** **one, carried not created — `core/015`'s native Windows build now carries an
eleventh landed `embarch-core` change.** This one is host-side test code with no behavioural change at
all, which is the weakest possible addition to that pile, but it is the fifth consecutive day a `core`
unit has added to it. The pile still includes `core/045`'s route-wiring test, the `suite/020`/`suite/035`
wire-feature split, and now `core/058`'s comment sweep. No board, no probe, no live Core touched.

### study-designer/048
**Hardware debts:** **none.** Source comments in a host-side crate; no board, no probe, no live Core,
no deploy, and nothing built for a target.

### suite/029
**Hardware debts:** **none created.** This unit is doc prose and two task files; nothing was built,
flashed or run. Worth stating that decision 63 *describes* behaviour nobody has implemented yet — the
debt it creates is `core/061`, not a board. Confirming the end state against a real study will need
the dev-bench board when `core/061` lands, and `core/061` says so. Unchanged: `core/015`'s native
Windows build debt, and `tasks/api/059` still `open` on `"probes": []` for a fourth consecutive leg.

### ui/051
**Hardware debts:** **none created, and one worth stating precisely.** This unit is host-side Rust and
one doc file. **But it makes the Trace tab depend on a Core route at runtime for the first time**, and
that path has never run against a live Core — `api/094` created the same debt for the agent side
yesterday and this is the human side of it. Needs no board of its own beyond whatever capture a study
produces; exercising it is the owner's, through the UI. Unchanged: `core/015`'s native Windows build
still carries nine landed `embarch-core` changes, and `tasks/api/059` stayed `open` for a third
consecutive leg on `"probes": []`.

### core/058
**Hardware debts:** **one, added to an existing pile rather than created.** `core/015`'s outstanding
native Windows build now carries a **ninth** landed `embarch-core` change. Comment-only, nothing
behavioural — but this is the third consecutive day a `core` unit has added to it, and the pile also
carries `core/045`'s route-wiring test and the `suite/020`/`suite/035` wire-feature split. The worker
correctly did not attempt a Windows build; that is the owner's.

### study-designer/047
**Hardware debts:** **none created.** Two comment lines in a host-side Rust crate — no board, no
probe, no live Core, no deploy, and nothing here changes what any binary does. Unchanged: `tasks/api/059`
is `Hardware: bench` and stayed `open`, `embarch-core` having answered `"probes": []` at step 0.

### topology/043
**Hardware debts:** **none created.** Doc prose only — no board, no probe, no live Core, no deploy.
Unchanged and not created here: `tasks/api/059` is `Hardware: bench` and stayed `open` for a third
consecutive leg, because `embarch-core` answered `"probes": []` at step 0 — both boards unplugged.

### api/094
**Hardware debts:** **one, created here and small.** `study_stream_load` has never run against a
live `embarch-core` or a real outpost capture — it is unit-tested against a realistic body only,
and `features.d/api-260` says so in its own test column ("hw only for a real capture"). Needs no
board of its own beyond whatever capture a study produces. **Also unchanged and not created here:**
the MCP binary on this machine goes stale against a schema bump and the running server keeps the
old one, so verifying this tool is the owner's, through the CLI.

### ui/050
**Hardware debts:** **one, carried not created, and this unit is the reason it is still legible.**
`embarch-ui`'s stale-prefix debt — 18 records from a real capture, buffered inside the USB-UART
bridge past `embarch-core`'s open-time purge, never replayed, with `STALE_PREFIX_MAX_ROWS` (512) an
assumption about a FIFO nobody has measured — was one of the three things this compaction was
forbidden to lose, and it survives. It needs the owner's own session: run a study, open its Trace
tab, check the axis note reports a dropped prefix. No board was touched here.

### study-designer/046
**Hardware debts:** **none.** Source comments only, in a crate that builds for the host. No board,
no probe, no live Core, no deploy, and nothing here changes what any binary does.

### topology/042
**Hardware debts:** **none.** One documentation file. No board, no probe, no live Core, no deploy,
and nothing here changes what any binary does. Separately and not created here: `validate dev-bench`
was called live at step 0 to select bench work and answered `recorded hardware_id
6fcddc36cb781b71, live None` — **both boards are still unplugged**, so `tasks/api/059` stays `open`
rather than `blocked`, unchanged from leg 085.

### umbrella/067
**Hardware debts:** **none.** One source doc comment; no board, no probe, no live Core, no deploy,
and nothing here changes what any binary does.

### api/093
**Hardware debts:** **none.** Two source citations and one doc row; no board, no probe, no live
Core. **But (c) is deploy-shaped, exactly as `api/091`'s was**: a corrected MCP tool description
does not reach an agent until the `embarch-api` MCP binary is rebuilt, and this machine's is
already known to go stale against a shipped change. That is now **two** landed string corrections
waiting on the same rebuild.

### core/057
**Hardware debts:** **one, carried and deepened rather than created.** No board, no probe, no live
Core, no deploy in this unit — but `core/015`'s outstanding **native Windows build** now carries a
**ninth** landed `embarch-core` change, and this is the first of those that is a genuinely new
**HTTP route and module** rather than a comment or a test. The worker did not attempt the Windows
build and said why (Windows `cargo.exe` cannot resolve the worktree's symlinked path-dep siblings
over UNC) and correctly noted it adds no `cfg(windows)` surface, so the debt's *shape* is
unchanged. Its *size* is not: the Windows service build does not serve this route until that build
lands.

### topology/039
**Hardware debts:** **none.** One documentation file split into two; no board, no probe, no live
Core, no deploy, no code.

### api/091
**Hardware debts:** **none created.** Source comments plus one runtime string; no board, no probe,
no live Core, no deploy. **But (c) is deploy-shaped rather than doc-shaped**: the corrected
`"unavailable"` message does not reach an operator until an `embarch-api` MCP binary is rebuilt, and
this machine's is already known to go stale against a shipped change.

### topology/040
**Hardware debts:** **none.** Source comments only; no board, no probe, no live Core, no deploy.

### study-designer/045
**Hardware debts:** **none.** Source comments only; no board, no probe, no live Core, no deploy,
and `embarch-study-designer` builds no artifact for a board in this unit.

### suite/018
**Hardware debts:** **none created.** No board, no probe, no live Core, no deploy — the decision
moves no code and the unit read four repos without writing to any but `embarch-doc`. Note
`tasks/core/057` will inherit `core/015`'s outstanding native Windows build, now fourteen changes
deep and untouched by this leg.

### core/056
**Hardware debts:** **one, carried and added to.** `core/015`'s outstanding native Windows build now
carries a **fourteenth** landed `embarch-core` change — comment-only, nothing behavioral, but this is
the third consecutive day a `core` unit has added to it and nobody has run it. No board, no probe, no
live Core, no deploy touched by this leg at all. The **dev-bench probe is still unplugged** — checked
live at 19:19, Core reachable and `"probes": []` — so `tasks/api/059` stays **open**, not blocked, for
the **seventh** consecutive leg.

### umbrella/066
**Hardware debts:** **none created and none touched.** A sweep that changed no code and a task file.
Standing debts carried unchanged; `core/015`'s native Windows build is **not** added to by this unit.
The dev-bench probe is still unplugged (checked live 19:19, `"probes": []`) — `tasks/api/059` stays
**open**, seventh consecutive leg.

### api/092
**Hardware debts:** **none created and none touched.** An error-string change, two tests, a doc
split and four link repairs; no board, no probe, no live Core, no deploy. Standing debts carried
unchanged, including `core/015`'s native Windows build — **this unit adds nothing to it**, since the
change is in `embarch-api`, not `embarch-core`. The dev-bench probe is still unplugged (checked live
19:19, `"probes": []`), so `tasks/api/059` stays **open** for the seventh consecutive leg.

### topology/041
**Hardware debts:** **none created and none touched.** A doc close and a task-state correction; no
board, no probe, no live Core. Standing debts carried unchanged from `ui/049`'s entry, including
`core/015`'s native Windows build at thirteen landed `embarch-core` changes. **The dev-bench probe is
still unplugged** — I checked live at 19:19, Core reachable and `"probes": []` — so `tasks/api/059`
stays **open**, not blocked, for the **seventh** consecutive leg.

### ui/049
**Hardware debts:** **none created and none touched.** Source comments and one doc link; no board,
no probe, no live Core, no deploy. Standing debts carried unchanged — `core/015`'s native Windows
build at **thirteen** landed `embarch-core` changes (this leg added one, `core/055`), `umbrella/056`'s
unrun clearing behaviour, `suite/038`'s re-scoped check 9, `umbrella/037` check 13, `umbrella/033`'s
check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale prefix, and
the `embarch-outpost`/`embarch-dev-bench` toolchains. The **dev-bench probe is still unplugged** —
sixth consecutive leg — so `tasks/api/059` stays **open**, not blocked.

### api/088
**Hardware debts:** **none created.** Host-side test and error-context change; no board, no live
Core. **One pre-existing exposure named rather than fixed**: raising `status_timeout_secs` in the
*fixture* leaves the production path on the same 10 s bound under the same contention, and decision
74 scopes itself to the fixture without claiming otherwise. Standing debts carried unchanged —
`core/015`'s native Windows build at thirteen landed `embarch-core` changes, the dev-bench probe
still unplugged (`tasks/api/059` stays **open**), `fleet-hardware.py --refresh` still crashing
(`tasks/doc/041`).

### study-designer/044
**Hardware debts:** **none created and none touched.** Source comments in a host-side crate; nothing
built for a board, nothing executed. Standing debts carried unchanged.

### core/055
**Hardware debts:** **none created, one added to.** No board, no probe, no live Core — this is a code
structure change and nothing was executed. It does land on `core/015`'s outstanding native Windows
build, which now carries **thirteen** landed `embarch-core` changes. All other standing debts carried
unchanged, including the dev-bench probe still unplugged (`tasks/api/059` stays **open**) and
`fleet-hardware.py --refresh` still crashing (`tasks/doc/041`).

### umbrella/065
**Hardware debts:** **none created.** Source comments only; nothing built for a board, nothing
executed. The **dev-bench probe is still unplugged** — `status` returned `"probes": []` live at this
leg's top, **fifth consecutive leg**, so `tasks/api/059` stays **open**, not blocked. Standing debts
carried unchanged: `core/015`'s native Windows build at **twelve** landed `embarch-core` changes
(**`tasks/core/055`, which I unparked this leg, will make it thirteen**), `umbrella/056`'s unrun
clearing behaviour, `suite/038`'s re-scoped check 9, `umbrella/037` check 13, `umbrella/033`'s
check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale prefix,
and the `embarch-outpost`/`embarch-dev-bench` toolchains. `fleet-hardware.py --refresh` still
crashes (`tasks/doc/041`).

### api/087
**Hardware debts:** **none created, and one *reduced in principle*.** Decision 73 is the fix for a
hazard that only appears against an out-of-date deployed Core, so **the observed instance closes
when the owner redeploys** — that deploy is his alone and is not this task's. `core/015`'s native
Windows build still carries twelve landed `embarch-core` changes and **that pile is what produced
this bug's visible form**, which is the most concrete argument yet for paying it. The dev-bench probe
is still unplugged (`"probes": []` live at this leg's top, fifth consecutive leg), so `tasks/api/059`
stays **open**. All other standing debts carried unchanged.

### topology/038
**Hardware debts:** **none created, and this one deserves a caveat.** Every behaviour here is
message text and control flow over an already-enumerated probe list; `select_probe` never opens a
probe, so nothing in it needs a board. **But no attached probe has exercised the reconciled
function** — the five new tests cover zero/one/two probes and serial hit/miss with synthetic
`DebugProbeInfo` values, which is a real gain over the zero tests either copy had, and is not the
same as an enrolment against silicon. The dev-bench probe is still unplugged (`"probes": []` live at
this leg's top, fifth consecutive leg), so that could not have been checked this leg regardless.
Standing debts carried unchanged, including `core/015`'s native Windows build at twelve landed
`embarch-core` changes — **`core/055` will add a thirteenth**, since it edits `embarch-core`.

### umbrella/064
**Hardware debts:** **none created.** A doc-only citation edit; nothing built for a board, nothing
executed. Standing debts carried unchanged — `core/015`'s native Windows build (twelve landed
`embarch-core` changes), `umbrella/056`'s unrun clearing behaviour, `suite/038`'s re-scoped check 9,
`umbrella/037` check 13, `umbrella/033`'s check-17 arms, umbrella check 5's permission-denied probe,
`embarch-ui`'s 18-record stale prefix. **The dev-bench probe is still unplugged** — `status`
returned `"probes": []` live at this leg's top, fifth consecutive leg, so `tasks/api/059` stays
**open**, not blocked.

### api/086
**Hardware debts:** **none created.** A doc split; nothing executed. Standing debts carried
unchanged — `core/015`'s native Windows build (twelve landed `embarch-core` changes),
**the dev-bench probe unplugged, confirmed live this leg**, `umbrella/056`'s unrun clearing
behaviour, `suite/038`'s re-scoped check 9.

### umbrella/063
**Hardware debts:** **none created**, and one **not** discharged: `umbrella/056`'s clearing
behaviour has still never run on a real machine, and this unit touched only comments so it moves
that not at all. Other standing debts unchanged — `core/015`'s native Windows build (twelve landed
`embarch-core` changes), the dev-bench probe unplugged, `suite/038`'s re-scoped check 9.

### core/054
**Hardware debts:** **one, carried not created.** `core/015`'s outstanding native Windows build now
carries a **twelfth** landed `embarch-core` change; this one is three comment lines and nothing
behavioural, so it adds to the count and not to the risk. Other standing debts unchanged — the
dev-bench probe still unplugged, `umbrella/056`'s unrun clearing behaviour, `suite/038`'s re-scoped
check 9.

### topology/037
**Hardware debts:** **none created.** One doc comment, one decision, one `open.md` bullet; nothing
executed, no board, no probe, no Core. Standing debts carried unchanged — `core/015`'s native
Windows build, the **dev-bench probe still unplugged** (confirmed live this leg by
`validate dev-bench`: probe `001057729826`, live hardware_id `None`; `tasks/api/059` stays `open`,
not `blocked`), `umbrella/056`'s unrun clearing behaviour, `suite/038`'s re-scoped check 9.

### umbrella/062
**Hardware debts:** **none created.** Four comment lines plus one repointed citation; nothing
executed, no board, no Core. Standing debts carried unchanged — `core/015`'s native Windows build
(eleven landed `embarch-core` changes), the **dev-bench probe still unplugged** (`tasks/api/059`
stays `open`), `umbrella/056`'s unrun clearing behaviour, and `suite/038`'s own re-scoped check 9,
which has not been seen on a real `doctor` run either.

### core/053
**Hardware debts:** **one, carried not created — `core/015`'s native Windows build now carries an
eleventh landed `embarch-core` change.** Comment-only, nothing behavioral, but that is now **five
consecutive days** of `core` units adding to a debt nobody has paid, and the pile still includes
`core/045`'s route-wiring test and the `suite/020`/`suite/035` wire-feature split. Everything else
carried unchanged, including the **dev-bench probe still unplugged** (`tasks/api/059` stays `open`)
and `fleet-hardware.py --refresh` still crashing (`tasks/doc/041`).

### ui/048
**Hardware debts:** **none created.** Two comment lines in a Rust source file; nothing executed, no
board, no Core, no UI launched. Standing debts carried unchanged, including `embarch-ui`'s 18-record
stale prefix, which still has never met a real stale prefix.

### suite/038
**Hardware debts:** **none created, and one worth naming as *not* created.** This changes what
`embarch init` writes into a config and what `doctor` check 9 reports — both host-side, neither
needing a board. But **nothing here has been run on a real machine**: the owner's own `embarch init`
and `doctor` on a WSL2 split are where a re-scoped check 9 would first be seen, and that is the same
unpaid class as `umbrella/056`'s clearing behaviour. Standing debts carried unchanged, including
`core/015`'s native Windows build (ten landed `embarch-core` changes) and the **dev-bench probe
still unplugged**.

### core/052
**Hardware debts:** **one, carried not created — `core/015`'s native Windows build now carries a
tenth landed `embarch-core` change.** This one is readme prose with no platform-conditional code
touched, but that is now **four consecutive days** of `core` units adding to a debt nobody has paid,
and the pile still includes `core/045`'s route-wiring test and the `suite/020`/`suite/035`
wire-feature split. Everything else carried unchanged: the **dev-bench probe is still unplugged** —
`status` returned `"probes": []` live at this leg's top, so `tasks/api/059` stays **open**, not
blocked, for the fourth consecutive leg — plus `umbrella/037` check 13, `umbrella/033`'s check-17
arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale prefix, and the
`embarch-outpost`/`embarch-dev-bench` toolchains. `fleet-hardware.py --refresh` still crashes
(`tasks/doc/041`) and its buffer is six days stale.

### ui/047
**Hardware debts:** **none created.** Four comment lines in a shipped JS asset; nothing executed, no
board, no Core, no UI launched. Standing debts carried unchanged, including `embarch-ui`'s
18-record stale prefix, which still has never met a real stale prefix.

### api/085
**Hardware debts:** **none created.** Doc comments in a client crate; nothing executed, no Core, no
board, no route called. The dev-bench probe is still unplugged (`status` returned `"probes": []`
live at this leg's top), so `tasks/api/059` stays **open**. `core/015`'s native Windows build is
untouched by this unit — `embarch-api`, not `embarch-core`.

### umbrella/061
**Hardware debts:** **none created.** Four relative paths inside `doctor.rs`'s own comments and two
of its `fix` strings; `doctor` itself was not executed and nothing here runs. Standing debts carried
unchanged: `core/015`'s native Windows build (nine landed `embarch-core` changes and counting),
`umbrella/037` check 13, `umbrella/033`'s check-17 arms, umbrella check 5's permission-denied probe,
`embarch-ui`'s 18-record stale prefix, and the `embarch-outpost`/`embarch-dev-bench` toolchains.
**The dev-bench probe is still unplugged** — I read Core live at this leg's top and `status`
returned `"probes": []`, so `tasks/api/059` stays **open**, not blocked, for the fourth consecutive
leg. `fleet-hardware.py`'s buffer is **8521 minutes stale** and `--refresh` still crashes
(`tasks/doc/041`), so the buffer's "attached: yes" is six days old and was not believed.

### api/084
**Hardware debts:** **none created.** Tool descriptions, doc comments and one doc sentence; nothing
executed, no Core, no board. `inbox/api-stale-decision-22-citations-remaining.md` is left standing
for the next leg — four `embarch-core` decision 22 citations in `client.rs` (199, 381, 1249, 1333)
that cite HTTP routes rather than pairing the stale number with `known_boards`, which the worker and
the reviewer both judged needs a contextual look rather than a mechanical repoint. The dev-bench
probe is still unplugged and `tasks/api/059` stays **open**.

### umbrella/060
**Hardware debts:** **none created.** Nothing here runs: the unit is citations and one relative
path inside `doctor.rs`'s own comments and strings, and `doctor` itself was not executed. Standing
debts carried unchanged — and note `umbrella/037` check 13, `umbrella/033`'s check-17 arms and
check 5's permission-denied probe all still need a real machine, which this leg cannot give them.
The dev-bench probe is still unplugged (`status` returned `"probes": []` live at the top of this
leg), so `tasks/api/059` stays **open**.

### core/051
**Hardware debts:** **one, and it is the ninth thing riding on the same outstanding build.**
`core/015`'s native Windows build now carries a ninth landed `embarch-core` change. This one is
comment-only and nothing behavioural moved, but that is now three consecutive days of `core` units
adding to a debt nobody has paid, and the pile includes `core/045`'s route-wiring test and the
`suite/020`/`suite/035` wire-feature split. Everything else carried unchanged and untouched: the
dev-bench probe is **still unplugged** — I checked Core live at this leg's top and `status` returned
`"probes": []`, so `tasks/api/059` stays **open**, not blocked — plus `umbrella/037` check 13,
`umbrella/033` check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record
stale prefix, and the `embarch-outpost` / `embarch-dev-bench` toolchains. `fleet-hardware.py
--refresh` still crashes (`tasks/doc/041`).

### dev-bench/022
**Hardware debts:** one, carried and not worsened. **Nothing in this unit was built or run on
hardware and the host legs could not run either**: `embarch-dev-bench` has no `Cargo.toml`, so the
cargo half of the gate selects nothing, and the worker's worktree has no `west` binary and no
Zephyr SDK, so neither a `native_sim` build nor the `app/tests/serial_protocol` ztest suite could
be built — the standing debt from `dev-bench/019` and `020`, restated rather than added to. What
*was* verified mechanically: the grep gate is zero across all four files, comment-block balance is
unchanged per file, no line crosses 100 columns, and `check-client-names.py` is clean on the code
repo. **This is a comment-only change, so the untestable half is untestable in the least dangerous
way there is** — but it is still 131 changed lines in firmware nothing compiled. Standing debts
otherwise unchanged: `core/015`'s native Windows build, the unplugged dev-bench probe
(`tasks/api/059` **open**) with `fleet-hardware.py --refresh` still crashing, `umbrella/037` check
13, `umbrella/033` check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s
18-record stale prefix, and the bench queue parked by the owner's `d0cf9a0`.


### Budget

**PROCEED all day, no 429 anywhere.** Weekly usage climbed from roughly 56% of a 90% cap at
the day's first leg to the low-80s% by its last core-heavy legs, resetting on its normal
weekly clock throughout. Wave sizing ranged 2–6 depending on the leg; several legs explicitly
noted the queue itself, not the budget cap, was the binding constraint — citation-sweep
refill work is abundant and cheap to dispatch, which is most of why one day produced 80
sub-units.

### Least sure about

Standing doubts carried forward rather than resolved:

- **Whether the eleven-plus core/015 Windows-build tally is trustworthy at all.** The day
  narrated it inconsistently (see Hardware, above) — the next leg should count commits
  directly rather than propagate the ordinal from the most recent unit's own claim.
- **Whether three-plus consecutive zero-defect sweeps in a repo mean the corpus is actually
  clean, or that refill has converged on picking always-clean files by size.** No per-sweep
  hit-rate is tracked anywhere; `ui/049` and `umbrella/066` both raised this independently.
- **Whether hand-fixing cross-repo defects a worker's own scope cannot reach — done directly
  by the supervisor in `core/056`, `api/092`, `api/085`, and `umbrella/060` — is the right
  call every time, or whether some of those four should have waited for a task another
  scope's worker could pick up.** Each was reasoned through individually; nobody has looked
  at the four together.
- **Whether spending reviewer effort on small, single-citation sweeps generalizes**, raised
  explicitly in `study-designer/047`, against the five misrouted-notification incidents the
  same day that make a reviewer's result easy to lose regardless of its size.
- **Whether declining the `firmware_version` rename twice in one day (`suite/010`,
  `suite/036`) is genuine caution or looking decisive while deferring** — both units correct
  the argument against renaming without taking the rename, and the question of whether that
  is the right shape of answer is explicitly unresolved in both entries.

---
*Days 2026-09-12 to 2026-09-12 rolled to [log-archive/supervisor-log-2026-09-12-to-2026-09-12.md](log-archive/supervisor-log-2026-09-12-to-2026-09-12.md).*
