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

## 2026-09-13 12:46 — api/080 the tool index advertised three tools that do not exist, and two counts that were wrong at birth

**Decided:** nothing suite-wide. The judgement worth naming is **the opposite of the one the
previous unit reached, on the same question, in the same leg** — and that is why both are worth
reading together. `ui/042` found a stale number that had been true when written and preserved it
with its provenance. This unit found two numbers that were **wrong in the code at the moment they
were written**, and the worker proved it at the introducing commits rather than asserting it:
`57d27f7` (where `decisions/dev-bench.md` decision 68 says *"Nine sites reuse `status_timeout`"*)
already had 13 sites, and `3041549` (where `crates/embarch-core-client/src/lib.rs:81` names
`study_streams` as a `study_timeout_secs` consumer) already had `study_streams` calling
`self.status_timeout`. The reviewer re-derived both at those same two commits and agreed.
**"Was never right" and "was right and the source moved" are different defects with different
fixes, they look identical to a grep, and only the history separates them.** Two units this leg
landed on opposite sides of that line and both did the work to get there.

**The headline half is smaller and more consequential.** `embarch-api/interfaces/tools.md:15`
listed the Studies tools as ending in *"the three data aliases"*. `suite/015` retired
`study_power_data`, `study_waveform_data` and `study_gatt_data` on 2026-09-11, the sibling file
`interfaces/studies.md:15` already said *"the three **retired** fixed-channel aliases"*, and the
wrong one was the index a reader meets first. That is not a sentence that reads oddly; it is an
agent choosing a tool name that 404s. The fix says what happened and names the forwarding address
(`study_stream_data`), because a reader arriving from an older transcript needs one.

**The census that makes the fix trustworthy.** The task asked for every count in `tools.md` to be
re-derived from the `#[tool(...)]` attributes rather than from the file. **26 annotated functions
in `src/tools.rs`, and the five section lists sum to 3+6+5+6+6 = 26** once the stale phrase is
gone. The reviewer repeated the census independently and diffed the doc's tool-shaped identifiers
against the real function list; everything left over is prose. Nothing mechanical checks a prose
enumeration against the attributes, so this is the only kind of evidence available for that file.

**Merged:** `agent/api/080-tools-md-retired-data-aliases` — `embarch-api` `cd1bc2f`,
`embarch-doc` `76e75af`. The code half is one doc comment in `lib.rs`; the client's historical
alias comment in `client.rs` (drifted from `:1548` to `:1562`, text unchanged) was checked and
left alone because it is honestly past-tense, which the reviewer confirmed by reading it rather
than inferring it.

**Blocked:** nothing. `tasks/api/080` closed `done`.

**Reviewer:** no findings. Beyond the two commit-level re-derivations above it confirmed
`study_timeout` has exactly three call sites (`post_study`, `get_study_status`, `get_study_csv`),
that no other file still says "Nine sites", that `tools.md`'s new citation to
`decisions/study-reads.md` decision 39 lands on the block carrying the retirement note, and that
`embarch-decision-reversals.md` has no entry touching timeouts, study-reads or `tools.md`. It also
stated explicitly that it read both spawn-supplied worktrees by absolute path and made no bare
relative read — which is the `pre-existing`-mislabel failure mode, and it is the first entry in
this log where a reviewer says so unprompted.

**Hardware debts:** none created, none possible — a doc line, a decision's count, and one source
comment. Standing debts unchanged: `core/015`'s native Windows build, the unplugged dev-bench
probe (`tasks/api/059` **open**, re-checked live this leg: `GET /status` → `"probes": []`, and
`fleet-hardware.py --refresh` still crashes per `tasks/doc/041`), `umbrella/037` check 13,
`umbrella/033` check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record
stale prefix, the bench queue parked by the owner's `d0cf9a0`, and the `embarch-outpost` /
`embarch-dev-bench` toolchains absent from a worker's worktree.

**Budget:** PROCEED — weekly 53.3% of a 90% cap at leg start, resets in ~66h27m. Wave 6 suggested,
four workers dispatched, bounded by queue scope spread rather than by the cap.

**Least sure about:** **whether `tools.md`'s 26 is still 26 a week from now, and whether anything
will notice when it is not.** The census is correct today and it was produced by two agents
counting the same attributes; nothing in the gate can repeat it. `interfaces/tools.md` disagreed
with its own sibling `interfaces/studies.md` for two days after `suite/015`, in the same directory,
and no check saw it. The general fix is owner-reserved (`tasks/doc/033`, `tasks/doc/044`), but a
narrower one is not: a check that counts `#[tool(...)]` attributes in `embarch-api/src` and
compares the total against the tool index would be cheap and would have caught this exact defect
the day it landed. A new `scripts/` check is the owner's to write, so I filed it rather than only
naming it here: **`tasks/doc/051-nothing-counts-the-tool-attributes-against-the-tool-index.md`**,
`Owner: required`, landed in this fold. A log entry folds daily and rolls into `log-archive/`;
nothing dispatches from one. The task file is the durable half.

---

## 2026-09-13 12:44 — ui/042 a marker count that was true when written, and three citations off by one

**Decided:** one thing, and it is a precedent rather than a correction. `tasks/ui/030` treated
"a number in a decisions file disagrees with the code" as a defect to overwrite; the task file said
so and said explicitly that the precedent was not the answer. **The worker went to the history
instead of the grep and came back with the opposite call, and I accepted it.** `git show` at each
of the three commits of `embarch-ui/tests/fixtures/outpost-native-sim.trace.csv` gives marker
counts 132 (`fcf5c1e`), 163 (`d6877bd`), 155 (`dc5de2b`, current, matching both committed fixtures
and `trace.rs:2874`). `trace-view.md`'s *"132 across 760 ms swamped every span"* is past tense and
was **true of the fixture as first committed**. So the fix names which capture the 132 was measured
on rather than substituting 155 — and `trace.rs`'s assertion, both fixtures, and `style.css` were
left untouched, which is what the task's "Do not" existed to protect.

**The reviewer did the archaeology the worker could not.** `git log --follow` stops at `1190b72`,
a 12-way split of `embarch-ui/design.md` that git does not detect as a rename, so the worker's
trace ended there. The reviewer went past it: the "132" text first appears in `design.md` at
`4cfd0db0` (embarch-doc, 2026-08-26 01:46), **twelve minutes after** `fcf5c1e` (embarch-ui,
01:34), and then survives unedited through two doc revisions that land in the same day as the
regenerations to 163 and 155. So the number was true for about fourteen hours and stale for two
weeks. That is a stronger statement than "true when written" and it is now the one in the doc.

**Merged:** `agent/ui/042-stale-pointers-in-decision-docs` — `embarch-doc` `13a528c`;
`embarch-ui` **zero diff**, branch equal to `origin/main` at `e4d10ac`, verified by `rev-parse`.
Doc-only by design: the task is four numbers in two decisions files and no rendered pixel changes.

**Blocked:** nothing. `tasks/ui/042` closed `done`.

**Reviewer:** no findings. It re-derived all three fixture counts independently, traced the
sentence's origin past the split commit the worker's `--follow` could not cross, re-ran
`grep -n -- '--brand' embarch-ui/assets/style.css` (43 / 72 / 123, matching the corrected
123/43/72 exactly), confirmed `index.html:34` genuinely carries the header glyph's second
`<path fill="var(--brand)">` and was right to be left alone, and confirmed the sweep claim — one
citation of that shape exists in the whole sub-project's docs.

**On the reserve this unit spent.** The added clause pushed `embarch-ui/decisions/trace-view.md`
to 90.3% of its cap, the reserve floor. The worker filed `tasks/ui/043-compact-ui.md` in the same
commit, `In flux: no`, proposing a split of decision 10's three sub-arguments from 19/21 — which
is `DOC-BUDGET.md`'s split-first rule applied correctly, and it is `open` rather than `blocked`,
so it is dispatchable work rather than a park. **This is the reserve rule working as designed:**
`ui` had nothing in reserve at dispatch, the unit put one file there, and the debt was recorded by
the actor holding the context instead of discovered later by an unrelated worker meeting a wall.

**Hardware debts:** none created, none possible — two decisions files, and the code branch was
empty. Standing debts unchanged and none of them touched: `core/015`'s native Windows build, the
unplugged dev-bench probe (`tasks/api/059` **open**; I re-checked live this leg — `GET /status`
returned `"probes": []`, so it is still unplugged and `fleet-hardware.py --refresh` still crashes
on `tasks/doc/041`'s `AttributeError`), `umbrella/037` check 13, `umbrella/033` check-17 arms,
umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale prefix (untouched and
unrelated to this unit), the bench queue parked by the owner's `d0cf9a0`, and the
`embarch-outpost` / `embarch-dev-bench` toolchains absent from a worker's worktree.

**Budget:** PROCEED throughout — weekly 53.3% of a 90% cap at leg start, resets in ~66h27m.
Wave 6 suggested; four workers dispatched at once, which is the queue's scope spread, not the cap.

**Least sure about:** **whether "the number was true when written" is now going to be the default
answer, which would be worse than the defect it replaced.** Two units in a row have reached it —
`umbrella/058` yesterday and this one — and both were right, but both were also the cases where
the history happened to be legible. The cheap failure is a worker that cannot find the history,
concludes "probably true once", and writes a historical claim it did not verify. Note the shape
here: the worker's own trace stopped at a split commit and it was the **reviewer** that got past
it. A worker with no reviewer would have shipped a weaker version of the same sentence, and
nothing would have said so.

---

## 2026-09-13 12:29 — umbrella/058 a decision said `saved.host` is sticky for every class, and the code clears it

**Decided:** nothing suite-wide, and the one judgement worth naming is **what the worker did not
do.** `decisions/bind.md:29` asserted `apply_plan` writes `host.map(…).or(saved.host)` for *every*
class; `src/setup.rs:349` writes
`host: if plan.class == TopologyClass::Remote { plan.host } else { None }`. The cheap fix is to
delete the sentence. The worker instead put the claim in the past tense and **named decision 51 as
what changed it**, because the reason the field was once sticky is part of why clearing it needed a
decision at all — and a decision corpus that silently rewrites itself to match today's code stops
being a record of how the design moved.

**The second half is the one I would have got wrong.** `sticky-host.md:27` quoted `state.rs`'s
*"Only meaningful for `remote`"*, and the scout that filed this reported the quote as **not
existing** — `grep` finds three matches of that phrase and all three are in `config.rs`, about
something else. The obvious reading is that the citation was always wrong, which is what my task
file leaned toward. It was not: the worker checked `git show e63ce13:src/state.rs` and the comment
**was there verbatim** when decision 48 was written, then was rewritten twice (`umbrella/050`, then
decision 51). So the clause is not a mis-citation to correct but a **quote whose source moved**,
and it now says so and points at `state.rs`'s current comment. The reviewer confirmed both halves
independently — the old commit contains the comment, and `src/state.rs:26-32` carries what the
rewrite says it carries. **A stale citation and a citation that was never right need different
fixes, and only reading the history tells them apart.**

**Merged:** `agent/umbrella/058-saved-host-no-longer-sticky` — `embarch-doc` `9adaa1a`;
`embarch-umbrella` **zero diff**, branch equal to `origin/main` at `eacfb36`, verified by
`rev-parse`. Doc-only by design: the code was already right, and the task said in as many words
that if the worker concluded otherwise it was to report rather than change behaviour inside a
documentation task.

**Blocked:** nothing. `tasks/umbrella/058` closed `done` and retired in this fold.

**Reviewer:** no findings. It verified `setup.rs:349` against decision 51's own text; checked the
dead quote **both ways** (present at `e63ce13`, absent now, and the current comment says what the
rewrite claims); confirmed decision 48's *"what a stored value actually attests to"* argument
survives **verbatim**, with only tense and a trailing pointer added; and re-derived the byte count
exactly — 215 → 301 B, the +86 B the worker reported. That last one mattered: the worker's first
draft was +274 B and tripped decision 22's pinned per-decision baseline, so the wording was
tightened to fit, and **a byte budget buying brevity at the cost of a qualifier is the one way this
unit could have gone quietly wrong.** The reviewer's read is that the tightened clause adds
precision rather than dropping anything.

**On spending 86 B of a file already in reserve.** `bind.md` is at 11,533 / 12,288 B (93.9%) with
`tasks/umbrella/009-compact-docs.md` blocked on `In flux: yes`, due 2026-10-06 and not overdue. I
told the worker to compact it in-unit if its edit pushed the file over, per `DOC-COMPACTION.md` §2.
It did not, and the reviewer's argument for why that is right is better than mine: **compacting
`bind.md` in this unit would itself be barred by the same flux flag that parked the task.** The
debt is dated and owned; adding 86 B to it is defensible and the ledger will collect.

**Hardware debts:** none created, none possible — three prose assertions in two decisions files and
an empty code branch. One **narrowed rather than closed**: `open.md`'s note that decision 51's
clearing needs a real machine to confirm is untouched and still owed — this unit made the docs
agree with the code, not the bench agree with either. The worker ran the full cargo gate on an
untouched tree (229 tests, including
`a_local_conclusion_clears_a_previously_saved_host`), which is evidence about the code and not
about a machine. Standing debts unchanged: `core/015`'s native Windows build, the unplugged
dev-bench probe (`tasks/api/059` **open**) with `fleet-hardware.py --refresh` still crashing,
`umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's permission-denied probe,
`embarch-ui`'s 18-record stale prefix, the bench queue parked by the owner's `d0cf9a0`, and the
`embarch-outpost` / `embarch-dev-bench` toolchains absent from a worker's worktree.

**Budget:** PROCEED throughout — weekly 50.3% of a 90% cap at leg start, **53.0%** at this fold,
resets in ~66h30m. Wave 6 suggested and never reached; three workers at peak, bounded by queue
scope spread for the whole leg. **This is unit 4 of 4 and the leg ends here.**

**Least sure about:** **whether the six tasks I filed this leg are as good as they look, because
one scout wrote all six and nothing disagreed with it before they were dispatched.** Two of the six
ran this leg and both came back with the finding substantially confirmed — but `umbrella/058` is
also the one where the scout's framing was **wrong in a way that would have propagated**: it
reported the `state.rs` quote as never having existed, my task file inherited that, and only the
worker going to the history caught it. Four more tasks (`topology/036`, `api/080`, `ui/042`,
`outpost/020`) are sitting in the queue carrying that same single-source framing, each one marked
"scout-verified" — which now reads to me as a stronger word than it earned. The next leg should
treat those four the way this one's worker treated its task: **re-derive before acting, and expect
the framing to be wrong about one thing in ten.**

---

## 2026-09-13 12:25 — dev-bench/022 122 dead citations across four C files, and two of them named the wrong repo outright

**Decided:** nothing suite-wide. Two calls of mine, both recorded in `core/047`'s entry as queue
decisions and both now settled by this unit's result.

**(a) Collapsing `023`/`024`/`025` into `022` was right, and the evidence is specific.** One worker
covered all four files and all 122 citations in one pass, and the thing that would have been lost
by splitting it is exactly what the split could not have delivered: **`embarch-dev-bench`'s own
decisions run 1-46 with no gaps and `embarch-study-designer`'s overlap them entirely**, so a bare
`decision 39` is ambiguous until its paragraph is read. Eight hits of decision 39 resolved to
dev-bench's own (`dev_bench_log_level`) and nine to study-designer's (stream-tap / schema v8-v9).
A worker holding only one file has a smaller sample of that ambiguity and no reason to notice it is
systematic. All three retired tasks are `done` in this fold.

**(b) Two citations named the wrong repo outright, and the reviewer says both repoints are
"strictly better", not judgement calls.** `app/tests/serial_protocol/src/main.c`'s GATT-transcript
section header cited `embarch-dev-bench` decision 36 — which is chip-ID reporting — for a section
about the GATT capture window and streamed transcript, which is `embarch-study-designer` decision
36 verbatim. And `app/src/main.c`'s `RunProtocol` pre-flight comment cited `embarch-core` decision
18 — flashing, `Format::Bin` at the merge address — for "Core validates a submitted `Study`
structurally before touching the serial link", which is `embarch-study-designer` decision 18. The
reviewer checked all three repos' 18 and 36 and confirmed the old citations were **wrong rather
than ambiguous**. Neither was in the task; both were found by reading.

**A defect I fixed myself before merging, and it was in the one line the unit had deliberately
re-attributed.** `main.c`'s decision-18 comment came back reading `` §3 decision 18's rule `` — the
repo prefix replaced by a dangling fragment of the deleted filename, while its sibling citation of
the same decision in `serial_protocol.c` carried the full cross-repo form. Trivial and in scope, so
I fixed it (`15c8796`) rather than blocking; the reviewer confirmed the meaning is unchanged.

**Merged:** `agent/dev-bench/022-dead-design-md-citations` — `embarch-dev-bench` `15c8796`
(fast-forwarded onto `main`; the worker's `38cadda` plus my follow-up), `embarch-doc` `eae8205`.

**Blocked:** nothing. `tasks/dev-bench/022` closed `done`; `023`, `024` and `025` closed `done` as
covered, each carrying the merge SHAs and what was re-attributed in its file. **One new task filed:
`tasks/dev-bench/029`** — see below.

**Reviewer:** no findings. It spot-checked 8 decision-39 hits, both re-attributions three ways
across all three repos, my follow-up commit, and ~20 further numbers (dev-bench's own 7, 11, 16,
21, 27, 29(a), 37; `embarch-core`'s 35, 37; `embarch-study-designer`'s 10, 12, 24, 31, 32, 43, 44,
47, 50, 53, 55, 58, 60, 61, 62) — every one correctly attributed. It also checked
`embarch-decision-reversals.md` for 18/36/39 unprompted and found nothing being re-proposed. **It
caught two arithmetic slips that are not findings and are worth recording anyway**: the worker's
own closing note said *six* decision-39 hits were dev-bench's own where there are eight, and it
called the surviving bare-`§N` count 22 against the reviewer's 21. Both were in a task file that
this fold retires, so neither would have survived to be corrected.

**And I asked it one question the task did not contain, which is where the unit's one real
follow-up came from.** The worker stripped the citations that carried only a *section* number and
no decision number down to a bare `§4.8`, on `dev-bench/020`'s precedent. The reviewer's read:
*"a different dangling reference, not an improvement — it drops the repo name too, so a reader can
no longer even tell which repo's history to search; less traceable than the dead-but-named path it
replaced."* That is right, and three units have now applied the treatment on each other's
precedent, which is how a convention gets established by accident. Filed as
**`tasks/dev-bench/029`**, which requires a numbered decision rather than a fourth silent
repetition, and **tells whoever takes it to re-derive the count because the two that exist (22
lines, 21 occurrences) disagree and neither was checked against the other** — in a task family that
exists because of numbers nobody checked.

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

**Budget:** PROCEED — weekly ~52% of a 90% cap, resets in ~67h. Wave 6 suggested, three workers at
peak, bounded by scope spread.

**Least sure about:** **this reviewer finished and its completion notification did not reach me** —
the third instance this log records of finished work stranded by a misrouted notification, and the
first where it happened to a *reviewer* rather than a worker. Its transcript froze for four
minutes, so I resumed it with a `SendMessage` asking for its conclusions rather than reading its
transcript, and it replied immediately. **That worked, and I am not sure it should be the answer.**
It is a fourth ad-hoc recovery route for the same defect (`tasks/doc/042` is the filed one), it
costs a model turn, and it relies on the agent still being resumable — a property nothing
guarantees and nothing checks. What I am least sure of is whether I should have written
`skipped (reviewer did not report)` and moved on, which is the honest answer under the rule as
written, instead of inventing a way to get the true one.

---

## 2026-09-13 12:09 — study-designer/036 two interface docs said `StreamRef` refused a fourth field, and it has one

**Decided:** nothing suite-wide. One judgement worth naming, and it is the worker's rather than
mine: **a refusal and a later acceptance are not automatically a reversal.**
`interfaces/taps.md` said *"`StreamRef` deliberately did not grow a `note` field"*, and the type
now carries `records: Option<RecordReport>` (`src/streams.rs:351`, decision 70, 2026-09-08). The
lazy fix is to delete the sentence; the wrong fix is to file a reversal row. The worker did
neither — it rewrote the paragraph to say what was refused (**unstructured** free text, which a
caller cannot rely on the way it relies on `truncated`) and what was later accepted (a structured
verdict computed the same way every time from framing declared per-tap in `Study.record_checks`,
against a CRC-32 each record already carries on the DUT), and **owned the cost rather than hiding
it**: the host schema bump the old paragraph used as its reason was paid, 17 → 18, with dev-bench's
own wire schema untouched. The reviewer checked that reading independently and agreed, adding the
fact that settles it: **that refusal was never a numbered decision anywhere** — `git log` on
`taps.md` shows only this file ever said it — so there is no numbered decision to reverse, and
every existing row in `embarch-decision-reversals.md`'s review-driven section anchors to one.

**Merged:** `agent/study-designer/036-streamref-fourth-field` — `embarch-doc` `5bbc0bc`;
`embarch-study-designer` **zero diff**, branch equal to `origin/main` at `efbf76e`, verified by
`rev-parse`. Doc-only is the correct outcome: the code was already right and the task forbade
touching the type.

**Blocked:** nothing. `tasks/study-designer/036` closed `done` and retired in this fold. The unit
filed **`tasks/study-designer/037-compact-study-designer.md`** in the same commit — its edit pushed
`interfaces/types.md` to 91.6% (1,037 B left), and the reserve rule is that the actor spending it
records the debt while it still holds the context. Filed `blocked` with `In flux: yes` and a
`Size debt due: 2026-09-27`, which is the shape `DOC-COMPACTION.md` asks for.

**Reviewer:** no findings. Given six questions and it answered every one against code rather than
prose: decision 70 located at `decisions/payload-meaning.md:34` and its characterisation matched;
`HOST_TYPE_SCHEMA_VERSION = 18` and `DEV_BENCH_WIRE_SCHEMA_VERSION = 15` confirmed in
`src/schema_version.rs`; `Study.record_checks` at `src/study.rs:240` with
`RecordFraming::MagicPrefixedCrc32Le` and CRC-32/ISO-HDLC in `src/records.rs`/`src/crc.rs`; the
four-field list confirmed complete; and task 037's size arithmetic re-derived exactly
(11,251/12,288 B against a 12 KB interface-group cap). **It raised one minor-only nit and
explicitly declined to file it** — 037 said `types.md` had taken edits from *four* of the last
seven merged units and named three, and `git log` corroborates three. **I applied it in this fold**
rather than leaving it: it is a false count inside a queue file, which is the same defect class the
whole refill this leg is made of, and a reviewer being right about something too small to file is a
bad reason to leave it wrong.

**Hardware debts:** none created, none possible — two documentation paragraphs and an empty code
branch; no field reordering, no wire change, and the one schema bump mentioned was **already
landed** by decision 70, not made here. Standing debts carried unchanged: `core/015`'s outstanding
native Windows build, the unplugged dev-bench probe (`tasks/api/059` still **open**) with
`fleet-hardware.py --refresh` still crashing, `umbrella/037` check 13, `umbrella/033` check-17 arms,
umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record stale prefix, the bench queue
parked by the owner's `d0cf9a0`, and the `embarch-outpost` / `embarch-dev-bench` toolchains absent
from a worker's worktree.

**Budget:** PROCEED — weekly 52.0% of a 90% cap at the previous fold, resets in ~67h. Wave 6
suggested; three workers at this leg's peak, bounded by scope spread rather than budget, which is
what the six-task refill in `core/047`'s entry was for.

**Least sure about:** **whether a doc-only unit on a shared crate's interface should merge on green
at all.** This diff rewrites how a wire-adjacent type's contract reads, and the gate cannot see a
word of it — `check-docs.py` passed the same before and after, and the only thing that checked the
claims was a reviewer running *after* the merge. Merge-on-green is the owner's standing choice and
I did not deviate, but `protocol.md` §10 already carves out shared crates for a supervisor's own
read-before-merge, and I did read it; what I am unsure of is whether reading it myself is
meaningfully different from the reviewer doing it ninety seconds later, or whether I am just the
same check run earlier by someone with less time.

---

## 2026-09-13 12:00 — core/047 two decision entries said a cross-repo fix was still owed, and both had landed

**Decided:** nothing suite-wide. Two queue calls that the next leg should know about, because both
changed what is dispatchable rather than what is documented.

**(a) Four `dev-bench` task files were re-scoped into one.** `dev-bench/022`, `023`, `024` and
`025` described one mechanical sweep — 122 citations of a deleted `embarch-study-designer/design.md`
filename — across four files in one repo. **One-task-per-sub-project is per slot**, so they could
never run concurrently: four task files meant four legs each spending a unit on ~30 citations of the
same transformation. The expensive half is resolving the 28 distinct decision numbers against that
repo's index, and it is paid once whether the sweep covers one file or four. So `022` now carries
all four files and `023`/`024`/`025` are **`blocked` on it**, unparking from the worker's report:
whatever `022` does not cover goes back to `open` with its remaining count. **A defect in `025`
went with it** — it named `tests/serial_protocol/src/main.c` and the file is at
`app/tests/serial_protocol/src/main.c`, so its own `Done when` grep would have returned zero
against a path that does not exist, a checkbox passing for the wrong reason.

**(b) Refill ran for scope spread, not depth, and filed six tasks in six scopes.**
`queue-status.py --refill-owed --wave 6` reported three distinct scopes against a wave of six. A
scout swept `api`, `ui`, `umbrella`, `topology`, `study-designer` and `outpost` and came back with
one verified finding in each, all of the same class: **a doc asserting something about code, and
the code saying otherwise.** Filed as `9a37a39` — `study-designer/036` (two interface docs say
`StreamRef` refused a fourth field; it has one, `src/streams.rs:351`), `umbrella/058`
(`decisions/bind.md` says `saved.host` is sticky for every class; `src/setup.rs:349` clears it),
`topology/036` (three dead citations inside that repo's own source comments, one of them a decision
number that was **never** right rather than one that moved), `api/080` (`interfaces/tools.md` still
advertises three tools `suite/015` retired, while its sibling `interfaces/studies.md` already says
they are gone), `ui/042` (a marker count off by 23 against a test that asserts the true value, plus
three CSS line citations each off by one — the worst kind, because they land on a real line) and
`outpost/020` (`interfaces/wire.md` describes 5 legs and 1 host-only test; `run-all.sh` has 6 and
3). **Not one of these is visible to any gate**: `check-decision-refs.py` and `check-links.py` walk
`embarch-doc/*.md` only, so a decision number in a source comment or a prose claim about a struct's
field list is unchecked by anything in the suite.

**A defect in my own task file, found by the worker.** I wrote that the stale paragraph was
`embarch-core` decision **54**'s. `studies.md` has no decision 54 — the index row is
`19, 20, 24, 33, 40, 41, 43, 45`, and `enrollment.md` carries an explicit tombstone for a 54 that
moved to 57 (`tasks/core/039`, after a collision with `decisions/flashing.md` 54). The paragraph is
decision **43**'s. The worker corrected it in the task file rather than doing what the task said,
which is the right failure mode; the reviewer independently confirmed the correction against the
index.

**Merged:** `agent/core/047-cross-repo-handoff-claims` — `embarch-doc` `f50b5a6`; `embarch-core`
**zero diff**, branch equal to `origin/main` at `53f1ed1` and verified by `rev-parse`, not taken on
the worker's word. The task is doc-only because `embarch-core`'s decisions live in
`embarch-doc/embarch-core/`, so an empty code branch is the correct outcome here rather than a
worker that did not finish. Landed by cherry-pick onto current `main` rather than `--ff-only`: the
branch was based on its own claim commit and two later claims had moved `main` underneath it.

**Blocked:** nothing. `tasks/core/047` closed `done` and retired in this fold.

**Reviewer:** no findings. Given four questions and it answered all four against sources rather than
prose: it re-derived the 43-versus-54 correction from `embarch-core/decisions.md`'s index and the
tombstone; confirmed `embarch-ui/assets/app.js:2499` renders `currentStep + 2` clamped with
`src/study_designer.rs:1823` asserting the old `+ 1` form is gone; confirmed the Topology tab labels
`confirmed_at_utc_ms` **"Enrolled"** citing decision 57 by name (`assets/app.js:160-175`,
`src/snapshot.rs:21-29`) after `3d2f870` repointed it from 54; and confirmed decision 57's
*Rejected* clause and decision 43's two-counters explanation both survived intact, amended rather
than deleted. **It was told in the spawn that `tasks/umbrella/045` may legitimately be absent
because it closed `done`** — it found the file present, but that line is worth keeping in future
spawns: a retired task file is the exact shape a reviewer misreads as a broken citation.

**Hardware debts:** none created, none possible — two paragraphs in two decisions files, and an
empty code branch. Standing debts unchanged and none deepened: `core/015`'s outstanding native
Windows build of `embarch-core` (this unit adds nothing to it — no `embarch-core` source moved),
the unplugged dev-bench probe with `tasks/api/059` left **open**, `fleet-hardware.py --refresh`
still crashing, `umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's
permission-denied probe, `embarch-ui`'s 18-record stale prefix, the bench queue parked by the
owner's `d0cf9a0`, and the `embarch-outpost` / `embarch-dev-bench` toolchains absent from a
worker's worktree.

**Budget:** PROCEED throughout — weekly 50.3% of a 90% cap at leg start, 52.0% at this fold, resets
in ~67h. Wave 6 suggested and never reached: three workers at this leg's peak, bounded by queue
scope spread, which is exactly what the refill above was for.

**Least sure about:** **whether collapsing four task files into one is a supervisor's call or a
quiet loss of four independent reviews.** Each of `022`–`025` would have been read cold by a
different leg, gated separately and reviewed separately; one task means one worker's judgement over
122 citations with one reviewer behind it. I think the trade is right — the discrimination that
matters (which hits are *not* instances of the defect) is per-hit either way, and four legs on one
sweep is real throughput lost — but it is the kind of consolidation that looks obviously correct
from inside a leg and obviously lossy from outside one. The guard I left is that the three parked
tasks unpark from the worker's own report rather than from my assumption that it finished.

---

## 2026-09-13 11:32 — suite/036 the argument against renaming a served field was arithmetically wrong, and the field is still not renamed

**Decided:** one design call and one deliberate non-call, both mine, and the second is the one to
read.

**(a) `GET /dev-bench/hello` keeps `firmware_version` for now, and every reader of it is now told
whose build that is.** `embarch-core/interfaces/studies.md` already said so (landed with
`suite/010`); the two `embarch-api` surfaces did not. Both now say the value is the **bench's** and
that the `Study` field it corresponds to is `requires.dev_bench_version`, not the identically named
`requires.firmware_version`, which is the DUT's. Nothing served, no output key, no rendered string
and no behaviour changed.

**(b) The reason this task gave for *not* renaming is wrong, and I corrected it rather than
inheriting it.** `tasks/suite/036` argued the rename would leave the suite with **three** spellings
for the bench's build instead of two. It would not — `dev_bench_version` is one spelling used on
two surfaces, so the count is **two either way**:

| | wire (`HelloAck`) | HTTP (`/dev-bench/hello`) | study (`Requirements`) |
|---|---|---|---|
| today | `firmware_version` | `firmware_version` | `dev_bench_version` |
| renamed | `firmware_version` | `dev_bench_version` | `dev_bench_version` |

What the rename moves is **where the crossing happens**, and that argues *for* it. Today the
crossing is in the caller's hands, at the exact point where the HTTP name collides with a field on
the same struct holding a **different board's** version — so a caller matching name to name does
the wrong thing and it looks right. After a rename the crossing is inside Core, where Core composes
the response and no caller crosses anything. That is `embarch-core` decision 47's shape exactly.

**So I removed the bad argument and did not take the rename, and those are two separate
judgements.** The rename is not mine to take this leg because it needs work the task did not name:
`firmware_version` is a plain `String` on `embarch-core-client` and `embarch-api`'s reflash gate
compares it, so a renamed Core needs the same `Option` tolerance `embarch-api` decision 60 gave the
identity fields after decision 47 — and **the Core actually running on this machine is already
behind `main`** (`core/015`), so "old Core" here is the bench, not a hypothetical. A silent empty
string would turn a real version check into a vacuous one. The task now states that as the open
cost, and says the rename needs its own announcement window; mine covered documenting the field.

**`embarch-study-designer` decision 74 was not amended and does not need to be.** The previous
leg's handoff flagged that 74 "reads as settling the question". It does not — it says in its own
words that this surface *"is a genuinely open question and this decision does not close it"*. That
doubt is answerable by reading the decision, and the reviewer independently agreed the reading is
fair rather than convenient. **Consider that handoff item closed.**

**Announcement:** posted 2026-09-13 10:40, `ts 1789317643.030479`, no `--action`; window closed
11:11 with no reply and no human message in `#embarch-fleet` for the whole leg. Ran unobjected.

**Merged:** `embarch-api` `72e8b12` plus follow-up `265c8ff`; `embarch-doc` `6f369d3`, doc fold in
this commit. No agent branch on `embarch-doc` — a `suite` unit is my own hands.

**Blocked:** nothing. `tasks/suite/036` is **`done`** for the documentation half and the rename is
split out as **`tasks/suite/037`**, which carries the corrected argument, the old-Core tolerance
work, the three repos' consumer list, and a `Done when` that requires its own announcement window.
The split was forced by a good refusal: `fold-commit.py` will not fold a unit whose task is still
`open`, which is right — a half-done task left `open` is indistinguishable from one nobody started.

**Reviewer:** 1 finding — `inbox/suite-036-decision-58-misattribution.md`, acted on and consumed in
this fold rather than left in the queue. I had written that `embarch-api` decision 58 "exists
because of" decision 47's rename. It does not: 58 is the crate-wide rule that parsing an older Core
is not a per-field judgement (it came from `api/045`'s `validated_at_utc_ms`), and **decision 60**
is the one decision 47 produced. Fixed in the task file and in the rustdoc (`265c8ff`). **I
disagree with one line of the finding**: it called the `client.rs` comment's phrasing correct, and
it carried the same misattribution, so I corrected that too rather than only the task file. The
reviewer's other four answers all came back clean and each was checked against code, not prose — it
re-derived the spelling count from `protocol.rs:67`, `study.rs:621`, `study.rs:280-281` and
`result.rs:44,49` and confirmed `Provenance` adds no third spelling; confirmed the plain `String`
and `reflash.rs:259-270`; confirmed decision 74's clause verbatim; and confirmed `embarch-ui`
already spells the value `dev_bench` at both cited lines with no doc or guide mentioning the field
anywhere. **This is this leg's only non-zero finding, and it landed on the `suite` unit — the class
with no worker and no other outside read.** That is an argument for keeping per-unit review at
least for `suite` units.

**Hardware debts:** none created. One **not** deepened, deliberately: this unit changes
`embarch-api` only, so unlike yesterday's `suite/010` it adds nothing to `core/015`'s outstanding
native Windows build — and part of why the rename was deferred is that it *would*. Standing debts
unchanged: `core/015`, the unplugged dev-bench probe (`GET /status` returned `"probes": []` at this
leg's step 0, so `tasks/api/059` stays **open**) with `fleet-hardware.py --refresh` still crashing,
`umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's permission-denied probe,
`embarch-ui`'s 18-record stale prefix, the bench queue parked by the owner's `d0cf9a0`, and the
`embarch-outpost` / `embarch-dev-bench` toolchains absent from a worker's worktree.

**Budget:** PROCEED throughout — weekly 48.5% of a 90% cap at leg start, 49.8% at this fold, resets
in ~67h46m. Wave 6 suggested and never reached: the leg held two workers at its peak, bounded by
queue scope spread, not by budget.

**Least sure about:** **whether "correct the argument, decline the change" is a real outcome or a
way of looking decisive while deferring.** I ended this unit with the rename still unmade, the task
still open, and its central argument now pointing the *other* way from the conclusion I reached.
That is honest — the cost I substituted is real and I verified it in the code — but it means the
next reader of `tasks/suite/036` finds a task whose analysis favours acting and whose supervisor
did not act, and the only things separating those are the announcement's scope and the old-Core
work. If that reader concludes I simply lacked the nerve, they may be right, and the remedy is
cheap: the rename is perhaps two hours with the `Option` tolerance done properly, announced on its
own.

---

## 2026-09-13 11:06 — outpost/019 a rejection kept and its three premises retired, plus five citations of the wrong decision

**Decided:** nothing suite-wide. The judgement worth naming is the one in the task file rather than
in the fix: **a decision whose premises have gone false is not thereby a decision to reopen.**
`embarch-outpost` decision 26 rejected "fail the cross-decoder leg when the sibling fixtures are
missing", and closed by saying the real fix would be a CI workflow, which *this repo has never
had*, and that whether to build one is a suite-scope call this repo cannot file. All three of
those facts stopped being true on 2026-09-11: `host-tests.yml` exists, suite decision 2 made the
call, and `open.md` and `embarch.md` were both updated — leaving this clause as the last place in
the repo asserting the old world. **The rejection is still right**, because suite decision 2
deliberately leaves the cross-decoder leg outside that workflow. So the task was written to require
the premises replaced and the rejection kept, and to forbid the tempting adjacent change (adding
the leg to `host-tests.yml`), which is a suite-scope call and not an outpost task's.

**The worker found three more instances than the task named.** The task named two `run-all.sh`
strings citing decision 22 for decision 26's skip-versus-failure rationale; it found a third in
that file plus `tests/vocab_check.py`'s docstring and `README.md`'s test section — five in all —
and **left `run-all.sh:37` alone**, which is a genuine decision-22 citation about leg ordering.
That discrimination is the whole value of the unit: a `sed` over "decision 22" would have broken
the one correct one.

**Merged:** `agent/outpost/019-decision-26-ci-clause` — `embarch-outpost` `94db7d1`,
`embarch-doc` `6dc5251`.

**Blocked:** nothing.

**Reviewer:** no findings. Given three questions: does the rewritten clause still *reject* rather
than drift into a deferral; does its new claim about suite decision 2's scope match that decision's
actual text and `host-tests.yml` itself; and is the five-changed/one-left split right. All three
held — it quoted suite decision 2's own stronger reason for excluding the cross-decoder ("it would
SKIP on every run… a permanent skip is worse than an absence"), confirmed `host-tests.yml` carries
only the two host jobs, and read `run-all.sh:37` line by line to confirm it really is about leg
ordering. It also checked `embarch-decision-reversals.md` for outpost CI history unprompted and
found nothing being re-proposed. **One process note: this reviewer's code worktree had already been
removed when it ran**, so it read the code with `git show 94db7d1:<path>` against the owner's
checkout instead. That is safe — a SHA is a SHA — but it is luck rather than design, and the next
leg should delete a unit's worktrees *after* its reviewer reports, not after its merge.

**A defect in my own task file, twice, and the second one is the interesting one.**
`check-decision-refs.py` resolves a suite decision only through `suite/decisions.md`; naming the
topic file that holds the text followed by the number does not resolve. My first draft did that and
turned the gate red. I fixed it and added a dispatch note warning the worker — **and the warning
quoted the failing form, so the checker parsed the quote and the gate went red again, this time on
`main`, from my own claim commit** (fixed in `d830771` before anything else landed on top). The
rule this leg learned: a warning about an unparseable citation cannot contain the citation.

**Hardware debts:** none new — a decisions file, three shell/Python strings and a README. The
worker ran all three host legs green (`decoder_unit.py` 31/31, `vocab_check.py`, `cross_decoder.py`
skipping loudly as designed) and `run-all.sh` itself with `WEST`/`ZEPHYR_BASE` unset, which exits 1
at the guard by design. **Not run**: the three Zephyr legs and a `WEST`-present `run-all.sh`, for
the standing reason — no `west`/Zephyr SDK in a worker's worktree. `embarch-outpost` has no
`Cargo.toml`, so the cargo half of the gate selects nothing there. Standing debts otherwise
unchanged.

**Budget:** PROCEED — weekly 49.5% of a 90% cap at this fold, resets in ~68h. Wave 6 suggested;
the leg never exceeded two workers in flight, and the reason was scope spread rather than budget.

**Least sure about:** **whether a task I filed this leg and dispatched this leg got enough
adversarial reading.** `outpost/019` went from sweep to filed to claimed to dispatched inside about
twenty minutes, written by me from a scout's evidence that I re-verified but did not sit on. It was
right — the worker confirmed both halves and found three more instances — but the failure mode of
same-leg filing is that the task's framing and the supervisor's framing are the same framing, and
nothing between them disagrees. The reviewer is the only independent read, and it reviews the
*fix*, not the *task*. A task filed one leg and run the next gets a cold reader at step 0; this one
never did.

---

## 2026-09-13 11:00 — dev-bench/021 thirty-nine dead citations repointed, and the two decision numbers that mean different things in two repos

**Decided:** nothing suite-wide. One judgement is the worker's and it is the reason this unit was
worth a reviewer: **decisions 15 and 32 exist in both `embarch-dev-bench` and
`embarch-study-designer` with entirely unrelated content**, and `ble_bridge_real.c` cites both
repos' versions of both numbers. A mechanical repoint — the obvious way to fix 39 identical dead
filenames — would have attributed several of them to the wrong repo, and **no gate in this suite
can see it**: `check-decision-refs.py` reads `*.md` under a repo root and these are C comments.
The worker resolved each citation by reading the surrounding code against both repos' decision
prose. 31 became the cross-repo form, 8 stayed bare as `embarch-dev-bench`'s own, and **no decision
number changed.**

**Three of the 39 were not decision citations at all** — `design.md §4.3` / `§4.3a`, bare section
pointers into a file that no longer exists, with no number to carry. They were stripped to bare
`§4.3` / `§4.3a` and flagged rather than given an invented attribution, which is the same treatment
`dev-bench/019` gave `eap.h`'s `§4.9`. **That is the defect `tasks/dev-bench/026` already
describes** — a section reference that was wrong-but-attributed becoming wrong-and-unattributed —
and this unit has now added two more instances to that task's class without extending the task.
Whoever takes `026` should sweep `ble_bridge_real.c` too; it is filed nowhere else and I have not
edited `026` to say so, which is a gap the next leg could close in a minute.

**Merged:** `agent/dev-bench/021-ble-bridge-real-citations` — `embarch-dev-bench` `68821a7`,
`embarch-doc` `768f98e`.

**Blocked:** nothing.

**Reviewer:** no findings. Pointed at the shared-number attribution specifically, because that is
the one thing about this unit a supervisor cannot settle by reading a worker's summary. It
re-derived both collisions from the decision text itself — dev-bench 15 is one-DUT-connection
(`ble.md:14`), study-designer 15 is fixed-capacity heapless collections (`limits.md:9`); dev-bench
32 is the advertised-name scan filter (`scanning.md:22`), study-designer 32 is `GattMonitorAll`
overflow (`gatt.md:15`) — and confirmed all four sites split correctly. It also found the
attribution was **necessary rather than optional** in at least one place: the "a Hello is a hard
reset" comment cites study-designer decisions 12/16, and dev-bench's own decision 12 is
debug-chip vendor-ID detection, so a bare citation there would have been wrong. Confirmed
`embarch-study-designer/spec.md` has no numbered subsections, so the three bare `§` pointers hide
no successor section.

**Hardware debts:** none new. Two **unchanged limits** are worth restating because this unit ran
inside them: `embarch-dev-bench` has no `Cargo.toml` at all (its own `decisions/platform.md`
decision 9), so `cargo build`/`test`/`clippy` select nothing there and a green report means the doc
gate and nothing else; and no `west`/Zephyr toolchain exists in a worker's worktree, so no
`native_sim` build was attempted. **This is a C file that was edited and never compiled**, which is
acceptable for comment-only changes and would not be for anything else. Standing debts otherwise
unchanged, including the unplugged dev-bench probe.

**Budget:** PROCEED — weekly 48.5% at leg start, 49.5% at this fold, cap 90%, resets in ~68h.
Suggested wave 6; two workers in flight at the peak, which is what the queue's scope spread
allowed rather than what the budget allowed.

**Least sure about:** **whether "comment-only, so no build" is a judgement I should be making
per-unit or a rule this suite should write down.** I merged 39 edits to a C file that nothing
compiled, on the reasoning that they are all inside `/* */` and `//`. That reasoning is sound
exactly until one edit is not — an unterminated comment, a stray `*/`, a line continuation — and
the failure would reach a board rather than a gate. The cheap guard exists (`gcc -fsyntax-only`
over the one file, or a `native_sim` build if the toolchain were there) and I did not ask for
either. It has been the accepted practice for every `dev-bench` citation unit this queue has run,
which is either a settled convention or a habit nobody has examined; I could not tell which from
the record.

---

## 2026-09-13 10:51 — study-designer/035 decision 45 moved out of declares.md verbatim, and the split-first rule paid for itself

**Decided:** nothing suite-wide, and the compaction convention being applied was already settled.
One judgement is mine and it is in the dispatch note rather than the task: `tasks/study-designer/035`
argued for a verbatim split *and* left squeezing decision 40 on the table as an alternative, and I
told the worker to **prefer the split and not re-litigate it** — because `DOC-BUDGET.md`'s
split-first rule already decides that, and because decision 40 is this crate's largest decision,
over the per-decision cap and pinned. A worker re-opening a rule the repo has already settled is
cost with no upside. It split cleanly on the seam the task named, which the index row had been
announcing for days: *"firmware versions **and** the GATT table"*.

`decisions/declares.md` 11,309 → 8,676 B (92.0% → 70.6% of cap), out of reserve and off the size
ledger. Decision 45 now lives in a new `embarch-study-designer/decisions/declared-gatt.md` (3,267 B).
Decisions 40 and 74 untouched byte-for-byte — 74 landed **yesterday** in `suite/010`, so this is
the first thing to touch that file since, and leaving it verbatim is what makes that safe.

**`DOC-COMPACTION-PASS.md`'s human question, answered by the worker in its own words and not by a
script:** yes — `embarch-study-designer/spec.md` alone still answers what someone needs to work on
this crate today, and this unit did not have to touch it to keep that true. Decision 45 was never
*in* `spec.md`, because it is designed-never-built and `spec.md` is what is true now; moving it
between two decisions files changes nothing about a reader following `spec.md`'s own pointer into
`decisions.md`. I record that as a genuine pass rather than a formality: the four-file model
working as designed is the answer the question is looking for.

**Merged:** `agent/study-designer/035-split-declares` — `embarch-doc` `01d1642`. **Code side:
no commits at all** — `embarch-study-designer` was not changed, and the branch exists on its remote
only because the worker pushed it to establish it. There is no code SHA for this unit and a revert
needs only the doc one.

**Blocked:** nothing.

**Reviewer:** no findings. Given four specific questions rather than an open read, because a
verbatim claim is exactly the kind a reviewer can settle mechanically and a supervisor cannot
settle by reading a summary. It diffed the removed block against the added one byte-for-byte;
confirmed all four of the task's `Must not delete` paragraphs survived unaltered (decision 40's
verification-asymmetry paragraph and its four `VersionSource` variants, decision 40's "a
consequence this decision did not anticipate" paragraph, decision 45's "what building it would
take" paragraph and its deferral trigger, decision 74's reversal condition and its `tasks/suite/036`
pointer); walked all 19 index rows in `decisions.md` and found no number dropped and none
duplicated; and swept the whole worktree for any other live citation of `declares.md` for decision
45, finding only closed task files and a changelog entry, which are history rather than citations.

**Hardware debts:** none — the unit is a documentation split and no board, no build and no wire is
involved. Standing debts unchanged and carried: `core/015`'s outstanding native Windows build of
`embarch-core`, the unplugged dev-bench probe (confirmed again this leg — `GET /status` returned
`"probes": []`, so `tasks/api/059` stays **open**, not blocked) with `fleet-hardware.py --refresh`
still crashing, `umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's
permission-denied probe, `embarch-ui`'s 18-record stale prefix, the bench queue parked by the
owner's `d0cf9a0`, and the `embarch-outpost` / `embarch-dev-bench` toolchains absent from a
worker's worktree.

**Budget:** PROCEED at the start and at this fold — weekly 48.5% of a 90% cap, resets in ~68h21m,
suggested wave 6. Two workers in flight when this landed, so the wave was never the constraint;
**the queue's scope spread was**, which is the next paragraph.

**Least sure about:** **whether filing two new tasks off a scouted sweep is a supervisor writing
its own work.** `queue-status.py --refill-owed` fired on the *second* half of its gate — 10
dispatchable tasks but only three distinct scopes (`dev-bench`, `study-designer`, `suite`), and
`suite` is my own hands, so a wave of 6 had **two** worker slots it could fill. I swept, and filed
`tasks/outpost/019` and `tasks/core/047`, both stale-claim corrections verified against the code
before filing. That is squarely what refill is for. What I am less sure about is the *mechanism*: I
delegated the reading to a read-only scout agent to save my own context, and a scout optimises for
finding candidates, which is a pressure toward manufacturing work in a queue that is thin rather
than empty. I re-verified both findings myself against the actual files before writing either task
— which is the guard — and I dropped its third candidate (`embarch-api`'s Windows smoke-harness
tier) precisely because I could not confirm from here that it is closable without a native Windows
run. Worth someone deciding whether a scouted refill is a normal move or a reported exception; it
is not written down either way.

---

## 2026-09-13 10:34 — suite/010 one field name, two boards' builds, and the message that blamed the wrong one

**Decided:** `embarch-study-designer` **decision 74**, plus one deliberate non-decision.

**(a) `firmware_version` keeps its name on every surface, and every reader is told whose build it
is.** `HelloAck.firmware_version` is the bench's; `Requirements.firmware_version` and
`Provenance.firmware_version` are the DUT's; the field the first corresponds to is
`Requirements.dev_bench_version`. Renaming the wire field is rejected **on cost** — it is a schema
bump that reflashes every bench and redeploys Core in one sitting, against a defect whose damage is
a misleading log line and a mis-authored study — and renaming only the host-side pair is worse than
either, breaking every saved study and `StudyResult` on disk while leaving the wire field that
invites the confusion.

**(b) The half where that argument does NOT hold is filed, not taken.** `embarch-core` serves the
value as `firmware_version` over **HTTP** on `GET /dev-bench/hello`, where a rename costs no
reflash — and `embarch-core` decision 47 made exactly that rename on exactly that route for exactly
this defect class (`hardware_id` → `self_reported_hardware_id`). I did not take it, because it
changes a served field and **this unit's announcement window covered the `clamp_version` fix and
the doc comments, not an API rename.** Filed as `tasks/suite/036` with both sides of the argument
written out, including the one that cuts against it: renaming the HTTP field alone leaves the suite
with *three* spellings instead of two.

**The demonstrated defect is fixed rather than documented.** `clamp_version` warned *"dev-bench
reported a firmware_version longer than N bytes"* for all four values that reach it — including the
DUT's `flashed_firmware_version`, which `embarch-api` supplies out of band and which no bench ever
reported. It now takes a `VersionSubject`, the enum decision 40 already introduced for this exact
distinction, so the message names the board and **the compiler makes every call site say which one
it means.**

**Announcement window: inherited from leg 103 and not restarted**, which is the second consecutive
entry able to say the handoff mechanism works from the receiving end. Announced 2026-09-12 23:37,
`ts 1789277838.510359`, no `--action`, closed 00:07. Re-polled `fleet-read.py --thread` at 10:21 —
one reply, written by an app, and **no human message in `#embarch-fleet` across either leg.** Ran
unobjected, ~10.5 h after the window closed.

**Merged:** `agent/suite/010-firmware-version-subject` — `embarch-core` `7914352`,
`embarch-study-designer` `3a1920f`. Two follow-ups on `main` after the reviewer and a `cargo doc`
run: `embarch-study-designer` `efbf76e` (three rustdoc links in the new comments did not resolve —
`HelloAck` is a `DevBenchMessage` variant, not a `HostMsg`, and `Requirements`/`Provenance` are not
in scope in `protocol.rs`; `cargo doc` is deliberately outside this crate's gate, decision 68, so
nothing failed) and `embarch-core` `53f1ed1` (the test rename below). Doc side in this fold commit.

**Also landed, and it is not this unit's work:** `embarch-ui` `e4d10ac` and `embarch-umbrella`
`eacfb36`, each one line of `Cargo.lock` recording `embarch-core-client`'s `serde` dependency.
**That lock has been stale on `main` since `suite/035` landed yesterday**, so `cargo build
--locked` would have failed in both repos; my own `cargo check` of those consumers is what surfaced
it. Committed rather than reverted, because leaving it meant two dirty checkouts and a `main` that
does not build under `--locked`.

**Blocked:** nothing.

**Reviewer:** no findings — and this one was given five specific questions rather than an open read,
because a `suite` unit is the supervisor's own hands and gets no other outside look. It re-derived
decision 74's number from the decision *bodies* rather than the index and confirmed it free;
confirmed decision 72 really was missing from `decisions.md`'s index row and that my fix is right;
confirmed against the code that `requires.firmware_version` is only compared inside
`if let Some(flashed) = run.flashed_firmware_version`, which is the claim my doc comments rest on;
and checked `tasks/study-designer/035`'s byte arithmetic independently (decision 40 = 4,409 B,
45 = 2,795 B, 74 = 3,836 B, file 11,309/12,288 = 92.02%). **It also caught something I had talked
myself into**: the new test's name implied it pinned the fix, and it does not — clamping was always
subject-independent, so the assertion was already true before the change, and what enforces the fix
is the `VersionSubject` parameter at compile time. Renamed and the doc comment now leads with the
limitation (`53f1ed1`). On the decision 47 tension it said the seam is right rather than
inconsistent, because decision 47's target was HTTP-only with no wire half.

**Hardware debts:** none created, and **one deepened in a way worth reading twice.** This changes
`embarch-core`, and the running Core on this machine is the Windows service built from the rsync
target — so `core/015`'s outstanding native Windows build now also gates a log-message fix in the
study path. The change is platform-neutral and nothing here is wrong against the deployed Core (the
old message is merely misleading, not incorrect about the value it records), but the gap between
`main` and what is running is one commit wider. Standing debts otherwise unchanged: the unplugged
dev-bench probe with `fleet-hardware.py --refresh` still crashing, `umbrella/037` check 13,
`umbrella/033` check-17 arms, umbrella check 5's permission-denied probe, `embarch-ui`'s 18-record
stale prefix, and the `embarch-outpost` / `embarch-dev-bench` toolchains absent from a fleet
worktree.

**Budget:** PROCEED throughout — weekly 47.7% of a 90% cap at leg start, 48.3% at the end, resets in
~68h28m. Wave 6 suggested and **never used**: this leg dispatched no workers at all, because its
four units were three of leg 103's finished orphans plus this `suite` task.

**Least sure about:** **(b), and I want the next reader to weigh it rather than inherit it.** I declined
a rename that this suite's own decision 47 made, on this same route, for this same defect class,
and my reason is a procedural one — the announcement window covered something narrower. That is a
correct reason to *defer*, and I am less sure it is a correct reason to have written decision 74
in a form that reads as settling the question. If `suite/036` is picked up and the rename lands,
decision 74 will need amending rather than just extending, and its reversal condition (the next
wire bump taken for another reason) does not cover that path.

**Also worth one line for the next leg:** `git -C <repo> worktree add <relative path>` resolves the
path against **the repo**, not the caller's cwd, so my first attempt at this unit's two code
worktrees created them *inside* `embarch-core/.worktrees/` and `embarch-study-designer/.worktrees/`
— which is the layout `.claude/leg.md` forbids and `embarch-study-designer` decision 57 exists to
prevent. Caught immediately and redone with absolute paths. Use absolute paths for every `worktree
add`; the recipe in `.claude/leg.md` does, and that is why.

## 2026-09-13 10:20 — topology/035 a size debt paid by splitting one decisions file and squeezing a spec, and the compaction question answered

**Decided:** nothing suite-wide; the compaction convention being applied is already settled. Two
judgements are mine and worth naming.

**(a) The `In flux:` answer was rewritten before the work, correctly.** The task was filed
`In flux: per file — crate.md no, spec.md yes`, parked on `suite/035` landing. `suite/035` landed
yesterday at 12:45, so the worker re-answered the field as `no` for both files and did both in one
pass. That is the per-file rule working exactly as `tasks/doc/030` intended: the flux answer
belonged to a *file*, the thing it was waiting on happened, and the task became fully payable
without anyone re-filing it.

**(b) `DOC-COMPACTION-PASS.md`'s answer, in my own words: yes.** `embarch-topology/spec.md` alone
still answers what someone needs to work on this component today — what the crate is and is not,
the four facts detection cannot produce and why, what validation asserts and what it explicitly
cannot, the three cargo features and which consumer links which, the caching rule, and the
failure *signature* of the one defect that has cost this bench a day (a bench that flashes, boots,
runs, and times out waiting for a handshake). Nothing that was cut was load-bearing.

**Merged:** `agent/topology/035-compact-topology-doc` (doc `5aead72`). **No code merge** — the
whole unit is documentation; the code branch carries zero commits beyond `embarch-topology`
`main`. Pre-rebase tips, not revert handles: `8c37a15`, then `9c32dc7`.

`decisions/crate.md` split verbatim: decisions 4, 8 and 31 — "what a consumer may link" — moved to
a new `decisions/consumer-boundary.md`, 1/2/3/6/13 stayed, and `decisions.md`'s index row became
two. `spec.md` squeezed 9,570 B → 9,037 B by word-level trims. **Both files are off the size
ledger** — 16 dated debts before this unit, 14 after, 0 overdue either way.

**Blocked:** nothing.

**Reviewer:** no findings. It diffed the moved sections directly and confirmed the split is
byte-for-byte, checked all four `Must not delete:` items survived, and went through the `spec.md`
squeeze hunk by hunk. It agreed with the four cuts I had flagged as cosmetic and **found a fifth I
missed** — `"Description only, not a stronger promise"` dropped whole from the caching paragraph —
and judged it recoverable from the decision-29 citation standing beside it. It also made a process
observation I am recording rather than acting on: **the worker's commit message claims "without
dropping any fact" at the category level instead of itemising the cut hunks the way
`DOC-COMPACTION-PASS.md` asks.** The reviewer did that count by hand and it came out clean, but
the letter of the rule was not followed and nothing failed — which is the same shape as the three
incidents that rule was written for.

**Hardware debts:** none — a documentation split and a prose squeeze; nothing here reaches a
board or moves a byte on a wire. Standing debts unchanged and carried: `core/015`'s outstanding
native Windows build, the unplugged dev-bench probe with `fleet-hardware.py --refresh` still
crashing, `umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's
permission-denied probe, `embarch-ui`'s 18-record stale prefix, and the `embarch-outpost` /
`embarch-dev-bench` toolchains absent from a fleet worktree.

**Budget:** PROCEED, weekly 47.7% of a 90% cap at leg start, wave 6 suggested and unused.

**Least sure about:** the fifth cut, and I am recording it because I read that diff carefully and
still missed it. `"Description only, not a stronger promise"` was a *hedge about the strength of a
claim*, not a fact, and a hedge is the one thing a squeeze deletes without the sentence reading
wrong afterwards. If a compaction pass in this suite ever does lose something, my guess after this
unit is that it will be a qualifier rather than a number — and no check will see it, because
nothing that remains is false.

## 2026-09-13 10:18 — ui/041 the second of leg 103's three orphans, and the second whose fix had already landed

**Decided:** nothing suite-wide, and the absence is the interesting part. Two of leg 103's three
dispatches turned out to be work that had already landed — `dev-bench/028` as `656516b`, this one
as `fa0a327` — and in **both** cases the fix was a *reviewer-finding task filed by the same leg
that then fixed it in its own fold*. `ui/040`'s reviewer found two mis-prefixed citations; that
leg applied the fix as `fa0a327` **and** filed `tasks/ui/041` describing it as outstanding. The
task and the fix were produced by the same unit and only one of them knew about the other.

**That is a cheap class to stop and I am not fixing it by rule here**, because the rule would have
to live in `.claude/leg.md` or `protocol.md` and neither is mine: **when a fold applies a
reviewer's finding itself, it must not also file a task for that finding** — or if it files one,
it files it `done`. Both of last night's no-op dispatches cost a worker spawn, a claim commit, a
branch pair, a rebase and a landing to discover nothing needed doing. Filed as an observation for
the owner rather than an edit, per §2.

**Merged:** `agent/ui/041-vendor-gatt-decision-41-doc` (doc `7efa9ab`). **No code merge** — the
worker made no edit; its code branch carries zero commits beyond `embarch-ui` `main`. Pre-rebase
tips, not revert handles: `bba6cbc`, then `46a8202`.

**Blocked:** nothing.

**Reviewer:** no findings. Reviewed at `46a8202`, which is the same content as the landed
`7efa9ab` — I rebased once more after `dev-bench/028`'s fold moved `main`, and the SHA moved with
it. It confirmed both `assets/app.js` sites cite `embarch-study-designer` decision 41, that
decision 41's body is genuinely the vendor-defined GATT identity table, and — the question worth
asking after two legs found this exact class — that decision 39 is not a plausible-but-wrong
alternative at those sites but simply a different topic.

**Hardware debts:** none — no code changed in this unit. Standing debts unchanged and carried, the
same set as `dev-bench/028`'s entry above.

**Budget:** PROCEED, weekly 47.7% of a 90% cap at leg start, wave 6 suggested and unused — this
leg dispatched no workers, because its four units were three of leg 103's finished orphans plus a
`suite` task whose announcement window it inherited.

**Also in this fold:** `tasks/doc/050`, filed against `fold-commit.py` for the defect that made
the previous unit's fold finish by hand — its `git rm` of the finished task file refuses a file
the fold itself modified, and correcting `**State:** closed` to `done` is exactly such a
modification, so the failure lands *after* the log commit with no way back through the script.

**Least sure about:** whether the two no-op units should have been landed as units at all rather
than closed with a single commit and not counted. I counted them, because each still needed a
gate, an ownership check, a merge and a fold — but a leg whose cap is four units has just spent
half of it discovering that two tasks were already done, and a reader of this log a month from now
should know that is what "4 units" bought here.

## 2026-09-13 10:16 — dev-bench/028 a dispatched task whose fix had already landed, and a `closed` that would have kept it in the queue forever

**Decided:** nothing suite-wide. One correction the worker could not have known to make, and it is
the reason this unit is not a pure formality: the worker left the task at **`**State:** closed`**,
and `closed` is not one of the four words. `tasks/README.md` is explicit — `fold-commit.py` retires
a task file by matching **`done`** at token zero, and the last time five tasks said `closed` every
one of them survived the fold meant to remove it and sat in the queue for up to four days. I
rewrote it to `done` before folding. **Worth carrying forward as a dispatch note, not as a scold**:
a worker that concludes "already fixed, nothing to do" is exactly the worker most likely to reach
for the English word for that, and this is the second defect class this week that is invisible to
everything except a reader who knows the vocabulary is closed.

**Recovered, not run.** Leg 103 dispatched this at 23:36 last night and was killed at ~23:46 with
three workers in flight; all three finished and pushed. Its `leg` worktree still held an
uncommitted merge of a *different* unit (`ui/041`) plus a staged task-file deletion — reproducible
from pushed refs, so I reset to `origin/main` and redid the landings under the full gate rather
than inheriting a half-state I did not create. **Nothing was lost by the kill.** The branch was
cut before `3cd6770` and so would not fast-forward; rebased onto `origin/main`, then `--ff-only`.

**Merged:** `agent/dev-bench/028-devbench-loglevel-cite-doc` (doc `e1cd955`). **No code merge** —
the worker found the fix already on `embarch-dev-bench` `main` as `656516b` before its dispatch
reached it, made no edit, and its code branch carries zero commits beyond `main`. Pre-rebase tip
for reference: `f9b192b`.

**Blocked:** nothing.

**Reviewer:** no findings. Asked two verification questions rather than the usual open read, because
a task-file-only diff gives an ordinary contradiction read nothing to chew on: it confirmed
`656516b` does make the `DevBenchLogLevel` comment cite `embarch-dev-bench`'s own decision 39
(`decisions/logging.md`, runtime log level from a study) and that the other `decision 39` sites in
`serial_protocol.h` genuinely belong to `embarch-study-designer`'s stream-pipeline decision. It
also corrected the worker's arithmetic — **nine** such occurrences, not five — with no
misattribution among them.

**Hardware debts:** none — a citation-text question with no code change in this unit. Standing
debts unchanged and carried: `core/015`'s outstanding native Windows build of `embarch-core`, the
unplugged dev-bench probe (`tasks/api/059` left `open`, `fleet-hardware.py --refresh` still
crashing), `umbrella/037` check 13, `umbrella/033` check-17 arms, umbrella check 5's
permission-denied probe, `embarch-ui`'s 18-record stale prefix, and the `embarch-outpost` /
`embarch-dev-bench` toolchains absent from a fleet worktree.

**Budget:** PROCEED at leg start — weekly 47.7% of a 90% cap, resets in ~68h51m, wave 6 suggested.
No worker was dispatched this leg (see below), so the wave went unused.

**Also in this fold, and both are recoveries rather than this unit's work:** (a) the 2026-09-12
day-fold, 33 units across legs 096–101 collapsed by `embarch-log-folder`, 137,048 B → 48,562 B,
ledger clean at 81/81 SHAs and 33/33 reviewer lines, no roll due at the 2-day floor; and (b)
`log-archive/supervisor-log-2026-09-10-to-2026-09-10.md`, which **an earlier leg rolled but never
staged** — `supervisor-log.md` has linked to it since, and the file existed only in the owner's
working tree. It is committed here. Also filed: `tasks/doc/049` from this leg's refill sweep — and note the
number, because I picked `046` off the queue listing and `check-task-numbers.py` caught that 046,
047 and 048 already exist as finished or blocked files the listing did not show me. **Use
`check-task-numbers.py --next <scope>`; do not read the next free number off `queue-status.py`.**

**Least sure about:** whether redoing leg 103's landings from `origin/main` rather than continuing
its worktree was the right call. It cost three rebases and I am confident nothing was lost — every
input was a pushed ref — but the `D tasks/ui/041-...` staged deletion in that tree was a real
decision another supervisor had made, and I threw it away and re-made it. The cheaper reading is
that continuing would have been fine. What tipped it: I could not tell from the tree alone whether
that merge had been gated, and a merge I did not gate is one I would have to gate again anyway.

## 2026-09-12 — 33 units

*Folded by `embarch-log-folder` on 2026-09-13, spawned by the supervisor's first unit
after local midnight. Nine legs' worth of a day (096 through 101, plus recoveries of
096, 098 and 093's orphaned work) collapse here with every SHA, every
`**Hardware debts:**` line naming a board, and every `**Reviewer:**` line preserved
one per unit. What is gone is the narrative reasoning behind each accepted judgement;
git holds it in `embarch-fleet` and in the per-repo history at the SHAs below.*

**The defect class of the day: a citation that resolves to the WRONG decision, not
a dead one.** Three units independently swept for it at scale and each found more
than it went looking for — `core/049` filed one repoint and its own sweep of ~150
citation sites found **thirteen**, seven of them wrong *numbers* (not missing repo
prefixes); `ui/040` found **twenty-two** foreign decision numbers `embarch-ui`'s own
`decisions.md` (ceiling 26) could never have issued; `dev-bench/020` found **48**
dead-filename citations where the bare ones needed the surrounding paragraph, not the
number, because `embarch-dev-bench` and `embarch-study-designer`'s decision ranges
overlap. **`check-decision-refs.py` only resolves numbers inside `*.md` under a repo
root** — every one of these lived in a source comment, where no gate reaches, and a
wrong number that happens to resolve fails nothing. That is not closed: `dev-bench`
alone still carries ~236 more such citations behind `tasks/dev-bench/021`–`026`, and
nobody has filed the same sweep for `embarch-core`'s or `embarch-umbrella`'s source.

**Three worker units this day were recoveries of a different leg's finished, orphaned
work** — `ui/039` (leg 098 died, this day's leg 099 landed it on the evidence of the
pushed branches alone, ~7 hours later), `api/076` + `ui/034` (leg 096 finished both,
pushed both, and exited without landing either), and `suite/014` (leg 093 was killed
with the diff staged-uncommitted in its leftover worktree, already reviewed by its own
`embarch-reviewer`; adopted rather than redone after independent verification).
`topology/033` was landed by a *third* leg after leg 084 claimed it, merged both
halves, and died mid-fold. **The positive-signal rule — a branch present on its
remote carrying commits is a finished worker, regardless of whether a notification
ever arrived — is what made all four legal, and all four were re-gated from scratch
on the merge result rather than trusted from any worker's own report.**

**Four silence-as-consent windows (`ops.md` §4) were completed by a leg that did not
open them, and none was restarted:** `suite/011` (leg 096 announced at
`ts 1789200593.666659`, this leg closed it and ran the unit), `suite/034` (leg 097
announced at `ts 1789201472.118549`, closed and run), `suite/035` (leg 101 announced
at `ts 1789232916.230899`, closed and run one leg later), and `suite/020` half (a)
(leg 099 opened it, scoped it into two units mid-window, ran only half (a), and left
the window's own `ts` in the task file rather than restarting it for half (b), which
became `suite/035` and reused the inherited consent). **The handoff mechanism worked
every time it was tested this day.**

### Decided

**`suite/035`** (`embarch-api` decision 72): `embarch-core-client` names
`embarch_topology::hardware`'s seven wire types via `wire` feature rather than
hand-mirroring them; old `*Response` names survive as aliases. **The supervisor
overrode its own task's "Done when"**: `client.rs`'s mirror-pinning tests are
**kept**, re-scoped from "our copy matches theirs" to "the wire has not moved under a
deployed Core" — the compiler cannot see a Core already deployed and running older
code. If this is wrong, decision 72 is where to reverse it. Also compacted
`client-crate.md` to make the room decision 72 needed, discharging `tasks/api/073`.

**`suite/020`** half (a): `embarch-topology` gates a new `wire` feature (serde only)
under `hardware`, so `embarch-core-client` no longer hand-copies seven data types it
was forbidden to reach. `DetectedPort::detected_by` became a `String` (a `&'static
str` cannot derive `Deserialize`). Decisions 4 and 8 are qualified, not rewritten, and
now say outright they are not fully true until `suite/035` lands (which it did, same
day). **Run in the `embarch-topology` MAIN checkout with three workers in flight** —
unsafe, cost nothing this time only because `core/048`'s worker correctly diagnosed
the resulting syntax error as someone else's concurrent work and waited it out. A
`sed` edit also mangled eleven function signatures before being caught by grep.
**`.claude/leg.md` has no rule that a `suite` task editing a linked crate needs its
own worktree or must not run beside workers in the repos that link it — this is a
rule-file gap, found twice in one leg, not yet fixed.**

**`core/049`**: the citation sweep above (13 fixed, 7 of them wrong numbers,
including two cases of the *same number* resolving in two different repos:
`study.rs:3571`'s 58 and `api.rs:2032`'s repointing). The worker's commit message
gives a **false reason** for one of the fixes (says Core has no decision 20; it does,
it is simply unrelated) — the citation that landed is right, but a later reader
re-deriving it from the commit message would start from a false premise.

**`ui/034`**: `embarch-ui` decision 26 — Core being unreachable is an expected,
renderable state, not an error to surface as a crash — written down for the first
time after shipping unstated for months, constructed independently in three places
(`snapshot.rs::poll`, `Snapshot::pending()`, `logs.rs::poll_loop`).

**`core/045`**: `embarch-core` decision 60 — every registered route now has both
halves proven (rejects a bad token, *and* is wired to the handler its comment
claims), both lists derived from source, neither hand-kept. **Nobody should re-derive
"26 routes" from `open.md`'s decision 42** — the router registers 22 `.route()` lines
/ 23 verb-handler bindings today; 42's "26" is stale, historical text.

**`umbrella/056`**: `embarch-umbrella` decision 51 — `--host` (sticky since decision
48) now clears itself when a run concludes `local`/`wsl-host` rather than staying set
from a prior remote run. **Two workers were dispatched to this same task
concurrently** (a supervisor dispatch error); the surviving worker's version landed,
the duplicate stood down after confirming an identical fix, and the 83-line diff was
read as a fast-forward, not line-by-line — an interleaving inside one line would not
have been seen.

**`suite/027`**: suite decision 3 — `rx_utc_ms` **keeps its name** in both an outpost
trace (Core's real epoch clock) and a study's CSV/Sample (dev-bench uptime); every
home now states which clock it is. The task offered a rename or a doc fix; the
announcement that bounded this (leg 093) named only the doc fix, so **the rename
stays open, owned by the owner, with the board in front of him** — it touches
`embarch-dev-bench`'s wire struct (unbuildable in this fleet) and every capture file
already on disk. `embarch-outpost` decision 17's false claim that the trace clock is
"the same wall clock every other stream carries" is corrected.

**`suite/033`**: `suite/decisions.md` split into an index plus `suite/decisions/
tooling.md` and `naming.md` — verbatim moves, no rewording — paying off the 1,794 B
overage `suite/027`'s own decision 3 had just created in the same session.

**`suite/014`**: `embarch-study-designer` decision 7 no longer claims `cbindgen`
generates the C header (no `cbindgen` exists anywhere) or that C does not
re-implement the wire format (it does, ~3,000 lines). Adopted from leg 093's killed,
staged, already-reviewed work rather than redone.

**`study-designer/033`**: decision 45's GATT-authoring deferral now states its own
trigger (the first study needing to say which GATT table it was authored against)
instead of pointing at `open.md` — closing the "designed, never built, no trigger"
third state this suite keeps paying for.

Everything else (`api/078`, `api/079`, `dev-bench/019`, `topology/034`, `umbrella/057`,
`ui/031`–`033`/`037`/`039`/`040`, `dev-bench/020`, `study-designer/034`, `suite/011`,
`suite/012`, `suite/034`, `api/075`/`076`/`057`, `core/035`/`048`, `topology/033`) was
sub-project-scoped citation, compaction or worked-example work — real, gate-verified,
and detailed in the units' own task files and this fold's SHAs below, not restated
here.

### Merged

| Unit | Code | Doc / notes |
|---|---|---|
| `suite/035` | `embarch-api` `7d817a3` (pre-merge tip `88f9095`); `embarch-topology` `83af7ed` (pre-merge tip `2382d7a`) | doc in this leg's fold commit; announce `ts 1789232916` |
| `ui/040` | `embarch-ui` `baebcaf` | doc merged at `6cf5b58`; reviewer fix `fa0a327` |
| `dev-bench/020` | `embarch-dev-bench` `adbc380` | doc merged at `b1a026b`; reviewer fix `656516b` |
| `study-designer/034` | *none — docs only* | `d8655da`, merged at `c8d9988` |
| `core/049` | `embarch-core` `2dfff12` (parent `1e7a6bd`) | doc `e7f1565` (parent `c0202e5`) |
| `api/079` | *none — zero diff by design* | `839057d` (parent `fcbeb27`) |
| `dev-bench/019` | `embarch-dev-bench` `0eabb81` (parent `a0bf1d8`) | doc `00ae49f` (parent `6ebc5e4`) |
| `topology/034` | `embarch-topology` `2382d7a` (parent `e2725ce`) | doc `1fc2b5a` (parent `13bf34e`) |
| `suite/020` (a) | `embarch-topology` `e2725ce`, supervisor's own hands | `embarch-doc` `94d703e` |
| `umbrella/057` | `embarch-umbrella` `6f494b4` | doc `6232c87`, plus fold fix `9a8f89b`; ownership base `4823b8c71365` |
| `api/078` | `embarch-api` `88f9095` | doc `48be77a`; ownership base `5baa7f7b4397`; deletion verified against compaction commit `6f22dd6` |
| `core/048` | `embarch-core` `1e7a6bd` | doc `6e04955`; ownership base `ae6c4538ebf6` |
| refill (queue) | *nothing landed — files tasks only* | — |
| `core/035` | *none — zero diff by design* | `23ec10c`; ownership base `f1ae8f2cf7c8` |
| `api/057` | *none — zero diff by design* | `87a8930`; ownership base `f1ae8f2cf7c8` |
| `ui/039` | `embarch-ui` `2bd3460` | doc `6dc43d4`; ownership base `5b1fd40eb006` |
| `suite/034` | supervisor's own hands | `embarch-doc` `a4b6f53`; announce `ts 1789201472` |
| `suite/011` | `embarch-core` `1ee95d8`, `embarch-api` `793f705`, `embarch-ui` `8160b84`, `embarch-umbrella` `464b48b` | doc in this fold; announce `ts 1789200593` |
| `ui/037` | `embarch-ui` `8a48798` | doc `0871915`, plus fold fix `41b9482`; ownership bases `aaf440b` (code), `49de22c` (doc) |
| `ui/034` | `embarch-ui` `aaf440b` | doc `a9a72e8`; ownership bases `eca2fa1` (code), `fa08866` (doc) |
| `api/076` | `embarch-api` `f402163` | doc `fa08866`; ownership bases `29944ac` (code), `b5407a1` (doc) |
| `ui/033` | `embarch-ui` `eca2fa1` | doc `acdc92c`; ownership base `ff9507911b0f` |
| `ui/032` | `embarch-ui` `1430650` | doc `dd4c2b8`; ownership base `4a21b471cfd9` |
| `api/075` | `embarch-api` `29944ac` | doc `f556ebb`; ownership base `46cebf2997eb` |
| `topology/033` | *none — unrelated `4b7ee73` on `main`, not this unit* | doc `bc8c5ef`; ownership base `bbf15e19ddc9` |
| `ui/031` | *none* | doc `5c762df`; ownership base `a88de5936523` |
| `study-designer/033` | *none — zero diff by design* | doc `037fac2`; ownership base `5534ce842d88` |
| `core/045` | `embarch-core` `4459668` | doc `5a6d355`; ownership base `3c9f809c7ec2` |
| `umbrella/056` | `embarch-umbrella` `bbe998c` | doc `d67acc4`; ownership base `139b86edf343` |
| `suite/012` | `embarch-api` `7abca3d`, supervisor's own hands | doc in this fold |
| `suite/033` | supervisor's own hands | doc in this fold |
| `suite/027` | supervisor's own hands | doc in this fold |
| `suite/014` | `embarch-study-designer` `eeb5d2f` (pushed by leg 093 before it died; adopted, not re-derived) | doc in this fold |

Every unit's gate was re-run by the leg **on the merge result, not the branch**:
`check-docs.py` 11/11 on every unit, `cargo build`/`test`/`clippy --all-targets --
-D warnings` clean wherever Rust was in the diff, `check-client-names.py` and
`check-ownership.py` clean on both halves of every unit that had two.

### Blocked

**Nothing, in any of the 33 units.** No task went to `blocked` and no gate went red
on a merge result. Queue deltas instead: `tasks/api/077` (tests.md compaction, landed
with `api/076`) and `tasks/suite/034` (both filed and closed within this same day);
new open tasks left in the queue — `tasks/dev-bench/020`–`026` (five still open plus
`026`'s dangling-`§`-reference follow-up), `tasks/core/046` (`decisions/auth.md` at
92.4%, `blocked`, `In flux: yes`, size debt due 2026-09-26), `tasks/suite/032`
(`Hardware: required`, the dev-bench staticlib retirement, unreachable by any worker
here), `tasks/ui/032` (owner-reserved — see Least sure about), and `tasks/doc/036`
(owner-only, `check-ownership.py --scope` confusion — see below).

### Reviewer

**Reviewer:** no findings — asked three specific questions rather than the usual open
read; confirmed no standing decision is contradicted and every `api/073`
Must-not-delete item survived. — `suite/035`
**Reviewer:** 1 finding — inbox/ui-040-decision-39-vs-41-misattribution.md, a
decision-39-vs-41 misattribution, fixed in this fold. — `ui/040`
**Reviewer:** 1 finding — inbox/dev-bench-020-review.md, caught the exact
cross-repo-number-collision failure the unit's own first paragraph predicted; fixed
in this fold. — `dev-bench/020`
**Reviewer:** no findings. — `study-designer/034`
**Reviewer:** no findings; verified all thirteen repoints old-body-against-new-body,
and caught that the worker's own commit message gives a false reason for one of them. — `core/049`
**Reviewer:** no findings; independently re-derived both cited decision numbers
rather than trusting the task file. — `api/079`
**Reviewer:** no findings; read all three bodies asked to carry claims and confirmed
each holds. — `dev-bench/019`
**Reviewer:** no findings; re-ran the bare-number-above-30 sweep independently and
agreed. — `topology/034`
**Reviewer:** no findings; confirmed the `&'static str` → `String` change breaks no
consumer across four repos, and that no wire type still holds a `hardware`-gated field. — `suite/020`
**Reviewer:** no findings; confirmed decision 52 belongs in `reporting.md` on its
merits and is a free, correctly-indexed number. — `umbrella/057`
**Reviewer:** no findings; answered the over-citation question directly — `core/048`
cites a different clause of decision 14 than this unit, so it is not double-cited. — `api/078`
**Reviewer:** no findings. — `core/048`
**Reviewer:** skipped (this unit landed no code or doc diff to review — it files task
files only). — refill
**Reviewer:** no findings. — `core/035`
**Reviewer:** no findings. — `api/057`
**Reviewer:** no findings. — `ui/039`
**Reviewer:** no findings — read the fixture itself and confirmed all three clauses
of the new sentence and that decision 43 is reinforced, not contradicted. — `suite/034`
**Reviewer:** skipped (leg ending at its unit cap — a reviewer spawned here would
outlive the leg that spawned it). — `suite/011`
**Reviewer:** 1 finding — inbox/ui-review-037-decision-7-mismatch.md, refused on the
citation after re-deriving it (both bodies hold), acted on as an ambiguity instead;
drop deleted after the fold's disambiguation commit landed. — `ui/037`
**Reviewer:** no findings — confirmed decision 26 does not collide with 5 or 6 in the
same file. — `ui/034`
**Reviewer:** no findings — read the `tests.md` compaction against `api/077`'s own
Must-not-delete list and confirmed every item survives; flagged a real
misattribution risk in the fixture's own comment. — `api/076`
**Reviewer:** no findings — re-derived all seven renumberings independently from the
decision bodies and confirmed each. — `ui/033`
**Reviewer:** 1 finding — inbox/ui-032-citation-form.md, **refused by the
supervisor** after disagreeing on scope; left standing with the counter-argument
written into it, for the owner. — `ui/032`
**Reviewer:** no findings. — `api/075`
**Reviewer:** no findings. — `topology/033`
**Reviewer:** no findings — and turned up, unprompted, that the very string this unit
verified cites a `design.md` that does not exist; filed as `ui/032`. — `ui/031`
**Reviewer:** no findings; verified directly that nothing in `src/` describes the
GATT field as built, rather than taking the commit message's word. — `study-designer/033`
**Reviewer:** no findings; also corrected the task's own stale "26 routes" claim to
the current 22/23. — `core/045`
**Reviewer:** no findings. — `umbrella/056`
**Reviewer:** skipped (supervisor's own hands, `suite` scope, closed announcement
window — no worker diff to review). — `suite/012`
**Reviewer:** skipped (supervisor's own hands, `suite` scope, no worker diff to
review). — `suite/033`
**Reviewer:** skipped (supervisor's own hands, `suite` scope, announced window closed
unanswered — no worker diff; the announcement thread was the review surface). — `suite/027`
**Reviewer:** skipped (leg 093's own `embarch-reviewer` already reviewed this exact
diff against source before the leg died; re-derived its factual claims by hand rather
than spawning a second reviewer on an unchanged diff). — `suite/014`

### Hardware debts

**Two, both restated rather than newly created, plus one growing pile named in three
separate units.**

**Hardware debts:** **`core/015`'s native Windows build now carries an eighth landed
`embarch-core` change** — comment-only, nothing behavioral, but the second
consecutive day a `core` unit has added to it. — `core/049`. `core/045` adds a
**fifth** thing riding on the same outstanding native Windows build (the new
route-wiring test does not run in the Windows service build until it lands), and
`suite/020`/`suite/035` both note the wire-feature split now also rides on it, since
it changes a type `embarch-core` serves.

**Hardware debts:** one, carried not created — the new clearing behaviour has never
run on a real machine, and `embarch-umbrella/open.md` keeps that as the surviving
half of the `--host` bullet rather than striking it. Needs no board, only the owner's
own Windows/WSL setup. — `umbrella/056`

**Hardware debts:** **one, and it is pre-existing rather than created here.** The
canonical example is two `BleAdvertise` steps and no study in this suite has ever
reached a DUT — naming the fixture as *the* worked example makes that gap easier to
mistake for completeness, which is why `studies-guide.md` §3a now names the file
right where it already says the DUT was not involved. — `suite/012`

The other thirty units: **none** — comments, doc prose, crate metadata, or tests that
never reach a board or a running service. No board, no probe, no live Core, no DUT
was touched this day.

### Budget

**PROCEED throughout, waves of 6 suggested and mostly used, no HOLD and no 429 all
day.** Weekly usage climbed from roughly 37.3% to 45.4% of a 90% cap across the six
legs, reset window ~91–102h out depending on when in the day it was read. `suite/020`
and `ui/039` both ran 3 workers against a wave of 6 for want of dispatchable scopes;
the `refill` unit at 11:05 is the leg spending its fourth unit on filing five
new tasks (`api/078`, `core/048`, `dev-bench/019`, `topology/034`, `umbrella/057`)
rather than the announced `suite` task, because `--refill-owed --wave 6` was right
that one scope cannot feed a wave of six.

### Carry forward — not to re-derive

- **The wrong-decision-number defect class is bigger than assumed and no gate sees
  it.** `check-decision-refs.py` resolves numbers only inside `*.md`; a wrong number
  in a source comment that happens to resolve fails nothing. `core/049`, `ui/040` and
  `dev-bench/020` each found this at a scale nobody had budgeted for. `embarch-dev-
  bench` alone still has ~236 unswept hits behind `tasks/dev-bench/021`–`026`; no
  sweep has been filed yet for `embarch-core` or `embarch-umbrella`'s own source.
- **`.claude/leg.md` still has no rule that a `suite` task editing a linked crate
  needs its own worktree**, or must not run beside workers in repos that link it.
  Found twice this day (`suite/020`, noted independently by `core/048`'s worker) and
  cost nothing only by luck. Not the supervisor's file to fix.
- **`check-ownership.py --code-repo` is the correct flag for a code-half ownership
  check; `--repo` answers `unknown scope '<x>' (known: doc, suite)` and is not the
  bug leg 099 read it as.** `tasks/doc/036` covers it, owner-only; several units this
  day (`umbrella/056`, `core/045`) hit the same wall and correctly treated the code
  half as unrunnable rather than re-diagnosing it.
- **`check-task-numbers.py --next <scope>` is the only safe way to pick a task
  number.** `ls tasks/<scope>/ | tail -1` is not a high-water mark — a `done` task's
  file is gone from `tasks/` — and produced a wrong, reissued number this day that the
  gate caught before it landed.
- **`embarch-umbrella` decision 14 was cited by two different repos' release-CI
  comments in one leg** (`core/048`, `api/078`) — each correct in isolation, but a
  decision cited from four repos' CI comments is one whose body has to stay true for
  all of them, and nothing checks that. A third repo citing it is the signal to
  split.
- **Two reviewer findings were refused by the supervisor after re-deriving them
  independently**, both left as a record rather than silently overridden:
  `ui/032` (a citation-form question `DOC-CONVENTIONS.md` does not settle for a
  string that ships in the running UI — open, owner-reserved) and `ui/037` (a
  decision-7 citation the reviewer read as contradicted; both bodies actually hold,
  and the ambiguity was fixed with a disambiguating comment instead).
- **`suite/027`'s firmware-side rename (the `rx_utc_ms` name collision) is still
  open, deliberately, and is the owner's** — it needs `embarch-dev-bench`'s
  unbuildable-here wire struct and touches every capture file already on disk.
- **`tasks/suite/032`** (the dev-bench staticlib retirement) is the third
  `Hardware:`-gated suite item now sitting behind a board and a Zephyr toolchain no
  worktree here has.
## 2026-09-11 — 46 units

*Folded by an `embarch-log-folder` leg on 2026-09-12, per `protocol.md` §11. 46 per-unit
entries (44 headed, plus `api/063` and `umbrella/049` which the day's own log recorded
without a `##` heading) collapse here with every SHA, every hardware debt line and every
`**Reviewer:**` line preserved — reviewer lines are kept one per unit, line-anchored, so
`grep '^\*\*Reviewer:' supervisor-log.md` still tallies correctly. What is gone is the
narrative reasoning behind each accepted judgement; git holds it in `embarch-fleet`
(this fold's parent commit and earlier).*

### What the next leg should actually carry

- **`core/015`'s outstanding native Windows build of `embarch-core` is now blocking an
  eight-deep queue of landed-but-unreached fixes** (route auth comments, not-attached-vs-
  mismatch, doctor comments, deploy-landed digest fix, dev-bench env docs, and more) — none
  reach the running Windows service until it lands. It is the owner's.
- **The dev-bench probe is unplugged** (`core/041`: `GET /status` → `"probes": []`,
  `validate dev-bench` → `live None`). `tasks/api/059` is `open`, not `blocked` — correct
  per `.claude/leg.md`, a board reappearing needs no human unblock. `fleet-hardware.py
  --refresh` still raises `AttributeError` and is 79h+ stale (`tasks/doc/041`, owner-only).
- **A verbatim decision split is the one operation `check-decision-refs.py` cannot see.**
  Six stale cross-repo citations survived two separate verbatim splits this leg
  (`core/041`'s `surfaces.md`→`enrollment.md` split, 3 hits; `api/067`'s `core-link.md`
  →`client-crate.md` split, 3 hits) — all six caught only because a reviewer swept by hand.
  Filed as `tasks/doc/044` with all six as fixture.
- **Two decision-number collisions landed this leg** (`outpost/017`'s new half numbered 23,
  already live in `wire.md`, renumbered to 26 by the supervisor; `core/039` resolved a
  pre-existing 54/54 collision, renumbering the later one to 57 with a tombstone). Nothing
  in the gate checks decision-number uniqueness across a sub-project — that is
  `tasks/doc/033`, still `Owner: required`, now with two fresh live instances as evidence.
- **`embarch-api` carries seven open or blocked compaction tasks**, more than any other
  sub-project and still pulling ahead (`api/070`, `api/072` both filed a new one this leg).
  Nobody has looked at them as a group.
- **`queue-status.py`'s "dispatchable" count overstated the worker-usable queue by roughly
  6x for most of this leg** — 12–14 of the reported dispatchable tasks were `suite`-scoped
  (the supervisor's own hands, needing a 30-minute announcement window), leaving as few as
  1–2 a worker could actually take. `tasks/doc/043` already names this; several units this
  leg re-discovered it independently.
- **A `git … | tail` inside an `&&` chain under `set -e` silently disarms it**
  (`api/066`): a failed rebase read as success and force-pushed a worker's branch back to
  `origin/main`, discarding its commit on the remote (recovered from the local reflog,
  nothing lost). Treat any `git … | tail` as unchecked from here on.
- **`fold-commit.py` refuses a `suite` unit's own task file if it is dirty when first
  called** (`suite/009`, `suite/019`): `git rm`/`git add` the settled task file *before*
  the first `fold-commit.py` call, not after a failed one. Two legs hit this; the fix is
  in `scripts/`, the owner's.
- **A supervisor-executed `suite` unit has no worker and no branch — the reviewer, spawned
  before the fold commits, is the only adversarial check it gets.** Twice this leg
  (`suite/009`'s architecture-sketch repair, `umbrella/049`'s probe-vendor-table decision)
  a reviewer changed the supervisor's own drafted content before it reached `main`, once
  correcting a confidently-false "repair" that would otherwise have shipped as fixed.
- **Recovery, not re-run, is the right call on an orphaned pushed branch.** This leg landed
  four units (`core/039`, `outpost/017`, `topology/027`, `umbrella/050`) left behind by two
  supervisors that died in succession, per `.claude/leg.md`'s positive-only signal (a
  pushed branch carrying commits retires the worker) — and separately adopted `suite/013`,
  a fully-diffed but uncommitted unit left in the shared leg worktree by a killed leg,
  after reading and re-deriving its claims rather than discarding and redoing it.

### Merged — every SHA

| Unit | Code | Doc |
|---|---|---|
| `api/074` | *none — docs only* | `592a9ba` |
| `suite/015` | core `c40a278`, api `e5996d1`, ui `aa0a72f` | api fold-fix `3041549` |
| `suite/031` | *none — docs only* | `45e010e` |
| `suite/030` | *none — docs only* | `197f728` |
| `topology/032` | `4b7ee73` | `780b7b5` |
| `api/072` | *none — docs only* | `1840847` |
| `core/044` | `3ab54e3` | `beeae6a` |
| `topology/031` | `5c2a249` | `7dd9d73` |
| `ui/030` | `bfceb82` | `15762d1` |
| `study-designer/031` | *none — zero diff* | `eecafc1` |
| `umbrella/055` | `27be1f6` | `5b854be` |
| `api/070` | *none — zero diff* | `6b1ab41` |
| `core/043` | *none — zero diff* | `eb49e65` |
| `topology/030` | `cc8bab9` | `752ed2f` |
| `ui/029` | *none — zero diff* | `5e9cad4` |
| `study-designer/030` | `09abb1f` | `f833796` |
| `umbrella/054` | *none — zero diff* | `44b203a` |
| `suite/017` | study-designer `4ef1893`, ui `eaa8b13` | folded (decision 73 + spec.md invariant) |
| `umbrella/053` | `6664b48` | `b64e000`, fold-fix `6c26fac` |
| `study-designer/029` | *none — zero diff* | `65286b2` |
| `topology/029` | *none — zero diff* | `da93664` |
| `suite/028` | outpost `e349e17` | folded (`suite/decisions.md` 2) |
| `ui/027` | `69882c4` | `2742efd` |
| `core/042` | *none — zero diff* | `d30537d` |
| `api/068` | `5aec2a8` | `818453b` |
| `suite/022` | *no branch — supervisor-executed* | folded |
| `core/041` | `f1c18cc` | `7942e4f` |
| `api/067` | *none — zero diff* | `d048f67` |
| `umbrella/052` | `00c57d3` | `c7ae15f` |
| `api/066` | `f4734c9` | `2323c38` |
| `topology/028` | *none — zero diff* | `7e158a1` |
| `suite/013` | *no branch — adopted from killed leg* | `56a6ac5` (log `f9002e7`) |
| `ui/026` | *none — zero diff* | `9a6959a` |
| `api/064` | *none — zero diff* | `ba85d8c` |
| `suite/019` | ui `58a0537` | `56a6ac5`-family (log `f9002e7`) |
| `suite/009` | *no branch — supervisor-executed* | `353a285` (log `fe7220a`) |
| `api/063` | *none — zero diff* | `a622cc4` |
| `core/040` | *none — zero diff* | `1b5aefc` |
| `umbrella/049` | *no branch — supervisor-executed* | `998c28d` (log `86251c1`) |
| `topology/024` | *none — zero diff* | `d373fd4` |
| `ui/025` | `3d2f870` | `646a37b` |
| `umbrella/051` | `479069c` | `d3f3f75` |
| `umbrella/050` | `3fecfa4` | `b644685` |
| `topology/027` | *none — zero diff* | `a8b951e` |
| `outpost/017` | *none — zero diff* | `66751d2` |
| `core/039` | *none — zero diff* | `851a3d4` |

Every unit's gate was re-run on the merge result, not the branch: `check-docs.py` 11/11
throughout the day; `cargo build`/`test`/`clippy --all-targets -- -D warnings` and
`check-client-names.py` wherever a code branch carried a real diff; `check-ownership.py`
on every branch before merge. Several "zero diff" code branches were verified by
`rev-parse` equality against `origin/main`, not taken on the worker's word.

### Blocked

**One task went to `blocked` in the whole day**: `api/066` filed `tasks/api/067` (stale
decision-37/38 text in an over-cap parked file), recorded rather than worked; `api/067`
later unparked and paid it. Every other unit's task closed clean; `suite/030` and
`umbrella/009`-adjacent debts stayed `blocked` on genuine size-reserve parks, not new
this day.

### Reviewer

**Tally: 46 lines, 9 findings across 8 units (1 unit had 2), 2 skipped for leg-end timing,
35 no-findings.**

**Reviewer:** no findings. — `api/074`
**Reviewer:** no findings. — `suite/015` (the reviewer's sole flagged nit, decision 42's
stale route count, was accepted and fixed in this same fold)
**Reviewer:** no findings. — `suite/031`
**Reviewer:** no findings. — `suite/030`
**Reviewer:** no findings. — `topology/032`
**Reviewer:** no findings. — `api/072`
**Reviewer:** no findings. — `core/044`
**Reviewer:** no findings. — `topology/031`
**Reviewer:** no findings. — `ui/030`
**Reviewer:** 1 finding — inbox/study-designer-record-checks-rationale.md (accepted, fixed
in the fold, drop deleted). — `study-designer/031`
**Reviewer:** no findings. — `umbrella/055`
**Reviewer:** no findings. — `api/070`
**Reviewer:** no findings. — `core/043`
**Reviewer:** no findings. — `topology/030`
**Reviewer:** no findings. — `ui/029`
**Reviewer:** no findings. — `study-designer/030`
**Reviewer:** no findings. — `umbrella/054`
**Reviewer:** no findings. — `suite/017`
**Reviewer:** no findings. — `umbrella/053`
**Reviewer:** no findings. — `study-designer/029`
**Reviewer:** no findings. — `topology/029`
**Reviewer:** skipped (leg ending at its unit cap — a reviewer would outlive the leg that
spawned it). — `suite/028`
**Reviewer:** no findings. — `ui/027`
**Reviewer:** no findings. — `core/042`
**Reviewer:** no findings. — `api/068`
**Reviewer:** skipped (leg ending at its unit cap — a reviewer would outlive the leg that
spawned it). — `suite/022`
**Reviewer:** 1 finding — inbox/core-041-stale-surfaces-citations.md (deleted after being
acted on in this fold; caught 3 stale cross-repo citations a verbatim split could not
otherwise be checked against). — `core/041`
**Reviewer:** 1 finding — inbox/api-067-stale-core-link-citations.md (deleted after being
acted on in this fold; caught 3 more stale cross-repo citations of the same kind). —
`api/067`
**Reviewer:** no findings. — `umbrella/052`
**Reviewer:** 1 finding — inbox/api-066-core-link-decision-still-says-unpinned.md (filed as
`tasks/api/067`; drop deleted). — `api/066`
**Reviewer:** no findings. — `topology/028`
**Reviewer:** 1 finding — inbox/suite-features-power-row-mis-cites-dev-bench-decision-21.md
(acted on in this fold; drop deleted). — `suite/013`
**Reviewer:** no findings. (its own completion notification failed to arrive; collected
via a bounded 4 KB transcript-tail read after the subagent's mtime froze — flagged, not
normalized, in `inbox/a-reviewer-that-finished-and-never-notified-has-no-legal-way-to-be-collected.md`) — `ui/026`
**Reviewer:** no findings. — `api/064`
**Reviewer:** 1 finding — `inbox/api-surface-md-decision-67-broken-link.md`, drained by
this same unit into `tasks/api/064`. — `suite/019`
**Reviewer:** 2 findings — no `inbox/` drop; both applied to `embarch.md` and the task
file in this fold before either committed (a false architecture-picture repair caught
before it shipped, and an endpoint miscount). — `suite/009`
**Reviewer:** no findings. — `api/063`
**Reviewer:** no findings. — `core/040`
**Reviewer:** 1 finding — no `inbox/` drop; the correction ("rhetoric dressed as
necessity") was applied to `decisions/probe-vendors.md` and `spec.md` in this fold before
either committed. — `umbrella/049`
**Reviewer:** no findings. — `topology/024`
**Reviewer:** no findings. — `ui/025`
**Reviewer:** no findings. — `umbrella/051`
**Reviewer:** no findings. — `umbrella/050`
**Reviewer:** no findings. — `topology/027`
**Reviewer:** no findings. — `outpost/017`
**Reviewer:** no findings. — `core/039`

### Hardware debts

Two named, live debts, both discussed above: `core/015`'s outstanding native Windows
build of `embarch-core` (blocks a growing queue of landed fixes from reaching the running
service) and `core/041`'s unplugged dev-bench probe (`tasks/api/059` left `open`, not
`blocked`; `fleet-hardware.py --refresh` still crashes, buffer 5,902 min stale). Full
per-unit lines, in the day's own order, each carrying forward the same small set of
standing debts (`umbrella/037` check 13, `embarch-outpost`/`embarch-dev-bench` toolchains
absent from a fleet worktree, `umbrella/033` check-17 arms, umbrella check 5's
permission-denied probe, `embarch-ui`'s 18-record stale prefix, the bench queue parked by
the owner's `d0cf9a0`, and the STM32G0 arm never exercised against real ST silicon):

- `api/074` — **Hardware debts:** none — docs only.
- `suite/015` — **Hardware debts:** none of its own, but it **deepens `core/015`'s outstanding native Windows build**
- `suite/031` — **Hardware debts:** none — docs only.
- `suite/030` — **Hardware debts:** none — docs only.
- `topology/032` — **Hardware debts:** none — a doc comment; nothing reaches a board.
- `api/072` — **Hardware debts:** none.
- `core/044` — **Hardware debts:** none new, but this is now one more thing riding on `core/015`'s outstanding
- `topology/031` — **Hardware debts:** none — comment-only, and it touches no code path a board would exercise.
- `ui/030` — **Hardware debts:** none — no rendered pixel changed, and the standing debts are unchanged.
- `study-designer/031` — **Hardware debts:** none — no field reordering, no wire or schema change, so nothing here needs a board or
- `umbrella/055` — **Hardware debts:** none created, and the two standing `umbrella` ones are untouched — check 13's
- `api/070` — **Hardware debts:** none created, and one made slightly cheaper to reason about — the `[dev_bench]`
- `core/043` — **Hardware debts:** none — no wire change and no code change, so nothing here is waiting on
- `topology/030` — **Hardware debts:** none created, and one **clarified rather than closed** — the nRF54L family's
- `ui/029` — **Hardware debts:** none. Note the standing `embarch-ui` debt is untouched and unrelated — the
- `study-designer/030` — **Hardware debts:** none — comment text only, no constant's value changed and no public item added or
- `umbrella/054` — **Hardware debts:** none, and it does not touch the two standing `umbrella` ones — check 13's
- `suite/017` — **Hardware debts:** none — no board renders this picker. Note the change does **not** reach a running
- `umbrella/053` — **Hardware debts:** one, carried not closed, and it is the point of the unit: **nothing here has met a
- `study-designer/029` — **Hardware debts:** none — `[assumed]` is the honest marker precisely because no board has sized
- `topology/029` — **Hardware debts:** none — a doc correction about a field already on the wire. Note it does **not**
- `suite/028` — **Hardware debts:** none. Note the standing `embarch-outpost` Zephyr `tests/unit` debt is
- `ui/027` — **Hardware debts:** none — markup only, and the UI is not in the suite release archive
- `core/042` — **Hardware debts:** none — a doc count and no behaviour, so nothing here rides on `core/015`'s
- `api/068` — **Hardware debts:** none new — but this is now the second half of a two-repo correction whose Core
- `suite/022` — **Hardware debts:** none new. The bench is still unplugged; see `core/041`'s entry.
- `core/041` — **Hardware debts:** **the bench is unplugged.** `GET /status` returned `"probes": []` and
- `api/067` — **Hardware debts:** none. Unchanged and still the owner's: `core/015`'s native Windows build of
- `umbrella/052` — **Hardware debts:** none, and none deepened — the point of the unit is coverage that needs no Core.
- `api/066` — **Hardware debts:** none. It narrows a reason to care about one: the cross-repo mirror contract is
- `topology/028` — **Hardware debts:** none — a documentation split touching no code. The STM32G0 arm it documents is
- `suite/013` — **Hardware debts:** none new. This unit *removes* a false one: the studies guide's first worked
- `ui/026` — **Hardware debts:** none new. This unit **restates** two rather than closing them: the stale-prefix
- `api/064` — **Hardware debts:** none, and none possible — one path inside one prose sentence. Standing debts
- `suite/019` — **Hardware debts:** **none new, and none possible** — prose in two repos. Standing debts carried
- `suite/009` — **Hardware debts:** **none new, and none possible** — the unit is prose. Standing debts unchanged
- `api/063` — **Hardware debts:** **none new, and none possible** — prose, with an empty code branch. Standing
- `core/040` — **Hardware debts:** **none new, and none possible** — the unit is prose and its code branch was
- `umbrella/049` — **Hardware debts:** **none new, and none possible** — the unit is prose. **One retired as a
- `topology/024` — **Hardware debts:** **none new, and none possible** — a prose pass over one doc. Carried forward in
- `ui/025` — **Hardware debts:** **none new, and none possible** — two one-line edits. Carried forward unchanged
- `umbrella/051` — **Hardware debts:** **none new, and none possible** — this unit is five digits in two files.
- `umbrella/050` — **Hardware debts:** **one, named by the decision itself and deliberately not discharged.** Whether
- `topology/027` — **Hardware debts:** **none new, and none possible** — the unit is one bullet in an `open.md` and one
- `outpost/017` — **Hardware debts:** **none new.** The unit is a documentation split; nothing was built and no board
- `core/039` — **Hardware debts:** **none new, and none possible** — the whole unit is a decision number and three

### Budget

**PROCEED for nearly the whole day; DEGRADED only at the start of the leg that landed the
four orphaned units** (`core/039`, `outpost/017`, `topology/027`, `umbrella/050` —
percentages unavailable on a stale usage cache, wave 4, unused because nothing was
dispatched, only landed). Weekly usage climbed from ~21.3% to ~36.2% of a 90% cap across
the day's legs; no 429 anywhere. Wave suggestion was consistently 6 but the
worker-dispatchable queue was usually 1–3, `suite`-scoped work making up the rest (see
"What the next leg should actually carry" above).

### Least sure about

Standing doubts carried rather than closed, one per theme:

- **Whether growing `suite/user-guide.md` to 97.8% of cap to fix a real safety-guidance gap
  was right over squeezing it** (`suite/022`) — the split-into-`suite/agent-guide.md` fix
  is written down and blocked only on an owner-reserved `DOC-BUDGET.md` cap entry
  (`tasks/suite/030`).
- **Whether "recovered a dead leg's uncommitted unit" (`suite/013`) should be a normal move
  or stays a reported exception** — not written down either way.
- **Whether renumbering a colliding decision is the supervisor's to do at all**
  (`outpost/017`, `core/039`) — done both times as trivial-and-in-scope rather than left on
  `main` as a live defect, but a decision number is meant to be permanent.
- **Whether announcing a second `suite` window while the first is still open** (`suite/009`
  / `suite/019`, thirteen minutes overlapping) is a throughput move that shouldn't have been
  made — flagged as the owner's call if he wants one window at a time.
- **Whether a byte-neutral citation sweep deserved a reviewer at all** (`umbrella/051`,
  `ui/025`) — judged worth it while `tasks/doc/033` (decision-number uniqueness) is unbuilt
  and two live collisions landed the same week; becomes redundant spend once that check
  exists.

### Supplementary references

Ownership-check base commits, pre-rebase tips (not revert handles), a worker's raw pushed
tip, announcement `ts` values, and recovered-branch SHAs from the day's units, kept for
completeness: `023bb2fe202d`, `04083e2b2a70`, `04badb0`, `05c0f202b7a0`, `0f5394a`,
`1789111401`, `1789117538`, `1789179351`, `1789182061`, `1789182068`, `1789187481`,
`1789188682`, `1789189358`, `1789191158`, `1ed8cd7e05b2`, `1fcb66f63f76`,
`20bb3a908dcf`, `20e46c300551`, `2186de4`, `2b789cb`, `31a2e09`, `31a2e0960929`,
`31a2e096092938d83e3eef2a3ad71a1567b949c1`, `325e00e0a80a`, `39cdcbbcd583`, `3a86dc6`,
`3b92da68db46`, `3e8cce4365c6`, `3fecfa4b38c6`, `44d1ea9`, `46ec5c0a64b5`,
`474d6d6e38e9`, `4ef1893386df`, `558002c06609`, `58a0537415e7`, `5cec95e`,
`60043b87ef9d`, `62fa533abf7a`, `6cb5d450aa49`, `6fcddc36cb781b71`, `76afe2b`,
`79ef95bd3a87`, `7b0de3a`, `82c62a5ba6a0`, `84792ef6bdf3`, `8617c7a`, `8929ced81bfd`,
`98a2cc6c5a7a`, `9b7bfac`, `9b7bfaccc152`, `9b7bfaccc1527686461a81445c1d130be27b3e44`,
`9cf646af3ae9`, `b7863d959cc2`, `b872f6d`, `baf2ff291ba3`, `bf56bb7a385a`,
`dd4252cd93a5`, `e03930e`, `e066717d5287`, `e0be3735f158`, `e7f8923`, `e7f8923050e9`,
`e9c9299`, `efbc97c`, `f0f3331cab86`, `f58e6d2`, `fb56c0e`.
*Days 2026-09-10 to 2026-09-10 rolled to [log-archive/supervisor-log-2026-09-10-to-2026-09-10.md](log-archive/supervisor-log-2026-09-10-to-2026-09-10.md).*
