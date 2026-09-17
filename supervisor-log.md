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

## 2026-09-17 00:30 — dev-bench/034 the same number with two right answers in one repo, for the second time

**Decided:** **two things, and the first closes the wrap-aware census in this repo.**

**1. `embarch-dev-bench`'s wrapped-citation surface is swept out: 23 lines, 39 instances, 0 wrong
numbers, 2 missing repo labels, 1 wrong file name.** The census grep returned **24** hits, matching
the task's estimate. Two of them are adjudications rather than citations, and both were called
correctly: `ble_bridge_real.c:1197` is *"the decision / is made from the *entry*"* — plain prose with
no number on the next line, **left alone**; and `workspaces/nordic/manifest/west.yml:1` is a real
citation whose three numbers all resolve, so the coincidence the task asked about was not one. The
three fixes:

- `app/src/serial_protocol.h:39` — bare `decisions 31/32` for `GattDiscover`/`GattMonitorAll`. Those
  are **`embarch-study-designer`'s** (`decisions/gatt.md`, literally named for those two actions);
  dev-bench's own 31/32 (`decisions/scanning.md`) are the 16-bit UUID offset bug and the
  `target_name` scan filter. Label added.
- `app/src/serial_protocol.h:740` — bare `decision 39` for `streams_crc`'s *"sibling seal"*. That is
  **`embarch-study-designer`** `decisions/seals.md` 39, whose own text says *"three sibling seals,
  not one widened seal"*. Label added.
- `app/tests/scan_seen_mfg/src/main.c:1` — cited `decisions/ble.md` for decision 44, which lives in
  `decisions/scanning.md`. **Number and repo were right all along; only the file name was wrong** —
  a shape no census in this suite had produced before, and one that a resolution check keyed on the
  number alone cannot see.

**2. The second same-number collision in this repo, and the reviewer confirmed both halves.**
`decision 39` has **two right answers inside `embarch-dev-bench`**: the study designer's seal
decision at `serial_protocol.h:740`, and dev-bench's own logging/verbosity 39 (`decisions/logging.md`)
at `app/src/main.c:1085`, which is **correctly bare and was left untouched**. `dev-bench/033` found
the first such collision on `decision 39` too, split by sentence inside one file. So the standing
instruction for this repo — *read the sentence, not the number* — now has two independent
confirmations, and the failure mode it guards against is a relabelling pass that "fixes" the
correctly-bare side.

**Nothing in this unit was compiled, and that is structural rather than a lapse.**
`embarch-dev-bench` has no `Cargo.toml`, so the cargo legs of the gate select nothing, and a
worker's worktree has no `west` and no Zephyr SDK — the standing `dev-bench/019`/`020` debt,
restated, not added to. **This is a comment-only change, so the untestable half is untestable in the
least dangerous way there is.** What *was* verified mechanically: all three changed lines measured
**under 100 columns** (94, 98, 80), and the one line over 100 in these files is pre-existing and not
this unit's.

**Merged:** `agent/dev-bench/034-wrapped-citations` (code `edc278b`, doc `4288fd9`). The doc branch
needed a rebase onto `ea5b880` first, since `topology/053`'s fold had moved `main`. Gate re-run by me
on the merge result: in `embarch-doc`, `check-docs.py` **11/11** via the wrapper;
`check-ownership.py --scope dev-bench` OK on 2 doc paths and OK on the code repo;
`check-client-names.py --repo` clean against 7 denylist entries; no cargo legs, per above. I read
the full code diff before merging rather than merging on green, because two of the three edits are
in a **wire-format header** — `serial_protocol.h` — and that is one of the cases `.claude/leg.md`
names. Comments only; no struct, no field, no constant touched.
`changelog.d/dev-bench-wrapped-citation-census.changed.md` consumed into `history/dev-bench.md` with
`--only`; **29 of the owner's own fragments left pending**, untouched. No `status.d/` and no
`features.d/` fragment.

**Blocked:** nothing. `tasks/dev-bench/034` carries its per-instance write-up in a `## Result`
section and every `Done when` box ticked — but **the worker left its `State:` line at `claimed`**,
and `fold-commit.py` refused the fold and said so before writing anything. I set it to `done` and
re-ran. Worth knowing for the next leg: that refusal is the only thing standing between a landed
unit and a task file that reads as a live claim, which the next recovery would reclaim to `open` and
re-dispatch (`tasks/doc/028`, six prior instances). It cost one edit because the check fires before
the commit.

**Reviewer:** no findings.

Collected before this entry was written, in about two minutes — I asked all three reviewers after the
first for tightness and got it without losing substance. This one resampled both sides of the
`decision 39` collision independently, quoting `seals.md` 39's *"three sibling seals"* and
`logging.md` 39's *"study state like the bond table"* against the two call sites, and it grepped
`ble.md` for `44` and got no hit before accepting the file-name fix. **It checked exactly the three
lines I scoped it to and did not re-audit the other twenty** — which is the shape I want on a
23-line census, and is the first time this leg a reviewer's scope and its cost matched.

**Hardware debts:** **one, carried and not worsened.** Nothing here was built or run: no board, no
probe, no `west`, no Zephyr SDK, no live Core. That is the `dev-bench/019`/`020` debt restated — 6
changed lines of firmware comment that nothing compiled. Standing debts otherwise unchanged: the
dev-bench probe is **still unplugged** (`"probes": []` read live from Core at this leg's top), so
`tasks/api/059` stays `open`, **not** `blocked`, for a **fourteenth** consecutive leg;
`fleet-hardware.py --refresh` still crashes (`tasks/doc/041`) and its buffer still claims both
boards attached, so **do not plan a bench unit off it**; `core/015`'s native Windows build carries
its twelfth landed `embarch-core` change from this leg's `core/070` and is untouched by this unit;
`umbrella/037` check 13, `umbrella/033`'s check-17 arms, umbrella check 5's permission-denied probe,
`embarch-ui`'s 18-record stale prefix and the `embarch-outpost`/`embarch-dev-bench` toolchains are
all unchanged. The bench queue is still parked by the owner's `d0cf9a0`.

**Budget:** PROCEED throughout — weekly **26.4%** of a 90% cap at the leg's top and **27.4%** at its
last check, resets in ~150h, no 429 anywhere. Wave **6** suggested both times; **the 4-unit cap, not
the budget, is what ended this leg** — as it has every leg since the queue got cheap work to do.

**Least sure about:** **whether a citation-shaped unit is still buying anything at the margin.** Four
units, four scopes, seven real defects, and every one of them was a comment. That is a genuinely
good hit rate and it is also the fourth consecutive leg spending its whole budget on prose about
code rather than on code — while `tasks/api/059` has sat `open` for fourteen legs, `core/015`'s
Windows build for twelve `embarch-core` changes, and `umbrella/056`'s clearing behaviour and
`suite/038`'s check 9 have never been seen on a real machine. **The queue is what it is because
citation work is abundant and cheap to file, not because it is the most valuable work available**,
and I filed one more of it myself this leg. Somebody with the owner's authority should decide
whether that is the right allocation; a leg cannot, because the queue is the only thing it can see.

---

## 2026-09-17 00:25 — topology/053 the same wrong sentence a third time, and the one place it is right

**Decided:** **two things, and the second is the useful one.**

**1. `src/hardware/validate.rs:1-3`'s migration clause now cites `embarch-core` decision 22, and
decision 8 stayed where it belongs.** The header cited a bare `decisions 2, 8` for *"formerly
`embarch-core`'s own `board_gate.rs`"*. `embarch-topology` decision 2 (`decisions/crate.md`)
describes the crate's shared-library architecture and says nothing about a migration; decision 8
(`decisions/consumer-boundary.md`, *"One implementation, multiple call sites — not two independent
layers"*) is correct, but for the *next* clause, and it is now attached to that clause explicitly.
The provenance clause cites `` (`embarch-core` decision 22) ``, whose own body closes *"**Moved
wholesale into `embarch-topology`**, because the stale-serial incident that motivated that crate *is*
this mechanism's own override path going stale."* **The prose is byte-identical before and after** —
only citation placement moved, which is exactly what `topology/052`'s rewording lesson asked for and
what I told this worker to do.

**2. The class now stands at six instances, three of them in `embarch-topology` alone, and one
sentence of the same shape that is correctly cited — which is the part that makes it a real class
rather than a pattern-match.** This leg has paid `embarch-core`'s three (`core/070`) and
`embarch-topology`'s second (here); `enrollment.rs` was the first (`topology/052`, last leg). The
worker found the third — `src/hardware/hardware_id.rs:1-6`, *"formerly `embarch-core`'s own
`hardware_id.rs`, moved here unchanged (decisions 2, 4)"*, where decision 4 is a forward-looking
scope decision that never names the file — and **filed it rather than fixing it**, which was right:
its task's scope was one line and said so. Drained to `tasks/topology/054`, `open`.

**And it checked the fourth sibling and correctly said no.** `port.rs` carries the identical
sentence shape for `dev_bench.rs` with the identical `decisions 2, 4` citation, and it is **not** a
defect: decision 4 names *"the dev-bench port heuristic"* by name, and no `embarch-core` decision
records that particular migration, so decision 4 is the correct and only provenance available. **A
worker that finds three instances of a shape and then declines the fourth on the evidence is the
thing that distinguishes this class from a find-and-replace**, and it is worth recording as loudly
as the fixes.

**Merged:** `agent/topology/053-validate-rs-migration-citation` (code
`c0c4f84`, doc `d655d1e`). The doc branch needed **two** rebases — first onto `b05efc1` after
`core/070`'s fold, then onto `a8dbff2` after `study-designer/060`'s; the code branch fast-forwarded
straight on. Gate re-run by me on the merge result: in `embarch-topology`, `cargo build
--all-targets` clean, `cargo test` green (**80 + 5 with `--all-features`**, and I re-ran it after a
`touch` because a first pass reported nothing recompiled), `cargo clippy --all-targets -- -D
warnings` clean; in `embarch-doc`, `check-docs.py` **11/11** via the wrapper, re-run after I added
`tasks/topology/054`; `check-ownership.py --scope topology` OK on 2 doc paths and OK on the code
repo; `check-client-names.py --repo` clean against 7 denylist entries.
`changelog.d/topology-validate-rs-migration-citation.fixed.md` consumed into `history/topology.md`
with `--only`; **29 of the owner's own fragments left pending**, untouched. No `status.d/` and no
`features.d/` fragment.

**Blocked:** nothing. `tasks/topology/053` closed in the worker's own merge; `tasks/topology/054`
drained from `inbox/` and landed here, with its `protocol.md` link depth corrected from `../../` to
`../../../` — the drop was written from `inbox/`, where two levels is right, and one level deeper is
where it ended up.

**Reviewer:** no findings.

Collected before this entry was written, and it answered the one question the diff's shape actually
risked: **splitting one citation into two can leave the surviving number attached to the wrong
clause**, and it read decision 8's body against the final wording to confirm it did not. It also
diffed the header line by line to establish the prose is byte-identical, and independently confirmed
no `embarch-topology` decision records the `board_gate.rs` move closer than `embarch-core` 22. Three
minutes, against the eight the previous reviewer took — I asked for tightness this time and got it
without losing the substantive check.

**Hardware debts:** **none created, and none could be** — one doc-comment hunk, nothing built for a
board, no probe, no study. Standing debts carried unchanged: the dev-bench probe is **still
unplugged** (`"probes": []` read live from Core at this leg's top), so `tasks/api/059` stays `open`
for a fourteenth consecutive leg; `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`) and
its buffer still claims both boards attached, so **do not plan a bench unit off it**. `core/015`'s
native Windows build is untouched by this unit — `embarch-topology`, not `embarch-core`.
`umbrella/037` check 13, `umbrella/033`'s check-17 arms and `embarch-ui`'s 18-record stale prefix
are all untouched.

**Budget:** PROCEED — weekly **27.4%** of a 90% cap, resets in ~150h, no 429. Wave **6** suggested;
the 4-unit cap is what bounds this leg.

**Least sure about:** **whether `topology/054` should have been this leg's fourth unit.** It is the
third instance of a class this leg has now paid twice, the evidence is already attached, and it is a
ten-minute fix — but `dev-bench/034` is already merged and waiting, and re-ordering to take `054`
would leave a landed worker's branches unfolded while I dispatched a fresh one. The last leg asked
almost exactly this question about this same task family and answered it the same way; **if `054`
sits in the queue for four legs, both of us will have been wrong.**

---

## 2026-09-17 00:21 — study-designer/060 nineteen units ran a grep that could only see half the citations it claimed

**Decided:** **three things, and the first is the most consequential finding this leg produced.**

**1. The continuation-grep every unit of this chain has run since `044` matches only the PLURAL
"decisions", and nineteen units closed files under it.** The standing line was `grep -rlIE
'[Dd]ecisions[[:space:]]*$'`. A citation that wraps in the **singular** — `— decision` ending one
line, `52 (interfaces/decoders.md).` beginning the next — is invisible to it, and equally invisible
to the per-file `grep -cE '[Dd]ecisions? [0-9]+'` census, which needs the number on the same line.
`src/decoder.rs`'s own module-doc citation is exactly that, and **`060` found it by reading the
file, not by running the tool.** With the `s` made optional the repo returns **17 hits across 9
files**, thirteen of them on citation lines inside **six files this chain has already declared
swept**. `tasks/study-designer/061` carries the corrected pattern forward as the new standing method
plus those thirteen lines as owed re-check work.

**2. `src/decoder.rs` is a true zero, and the reviewer resampled all nine rather than the four I
asked for.** 9 distinct citation instances (decisions 52, 35, 39, 59, 60, 61, every one same-repo;
no cross-repo citation anywhere in the file), 0 wrong numbers, 0 false sentences. Third true zero in
nineteen files, after `bounded.rs` and `gatt.rs`. The count is 9 rather than the 7 a line-grep gives
because line 154 carries `(decisions 59/60)` and the module doc's decision-52 citation is the
singular wrap above. **No source changed at all, so this unit has a doc SHA and no code SHA.**

**3. The cross-scope half, which is the part worth carrying: two other scopes had already found and
fixed this exact gap before `060` ran, and there was no channel for that to reach it.**
`history/api.md` records `api/106` as a *"singular-wrapped citation re-check"* and
`history/umbrella.md` records `umbrella/074`'s *"singular-wrapped citation census"* — both
2026-09-16, both three legs before this unit. Neither produced an `inbox/` drop and neither produced
a `tasks/suite/*` entry, so the fix lived only inside each scope's own `history/` file while
`study-designer`'s chain kept copying the broken pattern forward unit after unit. **Filed as
`tasks/doc/074`, `Owner: required`** — every candidate fix is a reserved path (a rule, or a script),
and it lays out the three real options rather than picking one. `tasks/suite/041` is the one
sanctioned path that exists for this shape and it depends on the worker who fixes a method
recognising the fix is not scope-local; neither of those two workers did, reasonably, since each was
handed a task framed as a re-check of its own repo.

**I also corrected three numbers inside `tasks/study-designer/061` at this fold.** Its summary said
16 hits where its own itemised list adds to 17, and the same paragraph said "seven already-closed
files" and "six" two sentences apart. Corrected to **17 hits** and **thirteen citation lines in six
files**, with the six named, and a short paragraph recording that the itemisation was right and the
summary was the slip — which is the reassuring direction for that error to run. A stale count in the
task that *is* the next unit's method is worth a supervisor's edit; leaving it would have had the
next worker reconcile it from scratch.

**Merged:** `agent/study-designer/060-src-citation-sweep-remainder` (doc
`2a020687a8bd1f6e9e11e8a21fbf58f5b08ba0e5`; **no code SHA — the worker changed no source**). The doc
branch needed a rebase onto `b05efc1` first, since `core/070`'s fold had moved `main`. Gate re-run by
me on the merge result: in `embarch-study-designer`, `cargo build --all-targets` clean, `cargo test`
green, `cargo clippy --all-targets -- -D warnings` clean — a no-op by construction, since the code
tree is unchanged; in `embarch-doc`, `check-docs.py` **11/11** via the wrapper;
`check-ownership.py --scope study-designer` OK on 3 doc paths pre-merge and OK on the code repo (0
paths); `check-client-names.py --repo` clean against 7 denylist entries.
`changelog.d/study-designer-decoder-citation-sweep.changed.md` consumed into
`history/study-designer.md` with `--only`; **29 of the owner's own fragments left pending**,
untouched. No `status.d/` and no `features.d/` fragment.

**Also in this commit, and not this unit's work:** the **2026-09-16 day fold** (63 units, by an
`embarch-log-folder` subagent — 165 SHAs, 63 reviewer lines and 63 of 63 debt lines kept; its first
attempt was refused for 53 dropped SHAs that were rebase points and announcement timestamps rather
than merge handles, and it added a verbatim appendix and passed) plus the **roll** of 2026-09-13 and
2026-09-14 into `log-archive/supervisor-log-2026-09-13-to-2026-09-14.md`. `supervisor-log.md` went
from **509 KB to 51.6 KB** and is now at its two-day floor. The archive file is a new untracked path
in the fleet repo that `fold-commit.py` does not know about, so it lands in **a separate commit
immediately after this fold** — recorded here because the fold alone is not the whole handle.

**Blocked:** nothing. `tasks/study-designer/060` closed and `061` filed in the worker's own merge;
`tasks/doc/074` filed and landed here.

**Reviewer:** 2 findings — tasks/doc/074-a-method-fix-found-in-one-scopes-audit-chain-has-no-path-to-anothers.md

Collected before this entry was written, and **this line is the one I bent furthest.** The reviewer
filed nothing in `inbox/` and said so deliberately: no locked decision is contradicted, which is the
correct read of its charter. But it produced two things I acted on — the arithmetic slips and the
propagation gap — and writing `no findings` would have told the tally that review earned nothing
here when it earned the leg's best finding. So the count is real and the path is the task I filed
from it rather than an `inbox/` drop. **If a later reader thinks that corrupts the tally worse than
`no findings` would have, the honest fix is a fourth form, which `.claude/leg.md` forbids for good
reasons — so this is a gap in the vocabulary, not a licence I am claiming.** It also ran about
**eight minutes**, far past the ninety-second-to-three-minute estimate the fold-ordering rule is
built on, because I asked it to re-derive a repo-wide grep and read two other scopes' history files.
That cost was worth paying once; it is not a per-unit shape.

**Hardware debts:** **none created, and none could be** — one file read, no file written in the code
repo at all. Standing debts carried unchanged: the dev-bench probe is **still unplugged**
(`"probes": []` read live from Core at this leg's top), so `tasks/api/059` stays `open` for a
fourteenth consecutive leg; `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`) and its
buffer still claims both boards attached, so **do not plan a bench unit off it**. `core/015`'s
native Windows build is untouched by this unit — `embarch-study-designer`, not `embarch-core`.
`umbrella/037` check 13, `umbrella/033`'s check-17 arms and `embarch-ui`'s 18-record stale prefix
are all untouched.

**Budget:** PROCEED — weekly **27.4%** of a 90% cap, resets in ~150h45m, no 429. Wave **6**
suggested; the 4-unit cap is what bounds this leg.

**Least sure about:** **whether `tasks/doc/074` is a real mechanism gap or a two-instance
coincidence I have just given a permanent home.** Two scopes fixed a grep and a third did not hear
about it — that is one observation with n=2, and the last leg's own entries warn twice about
inventing a sweep for an observation that is not yet a pattern. What tips it for me is that the
*cost* was measurable and one-sided: a whole unit spent rediscovering it, plus thirteen citation
lines now owed a re-check that were signed off as swept. But I filed it `Owner: required` partly
because I am not confident enough to have anyone act on it.

---

## 2026-09-17 00:12 — core/070 the wrong decision supplied by adjacent prose, not by a wrong number

**Decided:** **two things, and the first is a new shape of citation defect this suite had not named.**

**1. A migration claim with no number attached is invisible to every grep this fleet owns, and the
number a reader *will* use is whichever one is nearest in the paragraph.** `embarch-core` moved its
own `board_gate.rs` into `embarch-topology`; that move is recorded as `embarch-core` decision 22
(*"Moved wholesale into `embarch-topology`"*, `decisions/probes.md`). Four doc comments in this
crate describe the move. **One cited 22. Three cited nothing for the migration claim.** All three
now carry `decision 22;` in the position `src/api.rs:681` already used, and **no sentence was
reworded** — `topology/052` established last leg that a rewording made while repointing a number is
the one move that can *introduce* a defect, and this unit took that seriously.

**`src/hardware.rs:107` is the instance worth remembering.** Its doc comment already carried
**decision 61**, twice, correctly, for a different fact — the selection rule no longer being this
crate's own copy. A reader arriving at that paragraph takes 61 as the citation for the whole thing,
including the `board_gate.rs` move, which 61 says nothing about anywhere in its body. That is
`study-designer/059`'s and `ui/063`'s shape — on-topic, correctly labelled, wrong decision — **with
the wrong decision supplied by adjacent prose rather than by a wrong number.** No citation census in
this suite, wrap-aware or not, can see that: there is no number to check. The whole-class grep
(`formerly|used to live|moved wholesale|migrated from` over `src/`) returns **4 hits before and
after**, so the class is closed in `embarch-core` at four instances with no fifth.

**2. Decision 22 covers all three migrated symbols, and I made the worker prove it rather than
assume it.** The live question was `study.rs:873`'s role-keyed `validate_role` (formerly
`board_gate::enforce_for_role`) — 22's *header* names enrollment, so covering a role-keyed variant
could have been a stretch. It is not: 22's own body carries *"a role-keyed variant exists because a
plain UART bridge has no JTAG capability, so it can never be an enrollment candidate"*, which is the
identical UART-bridge-has-no-JTAG reasoning `study.rs:857-872` makes, near-verbatim. Worker and
reviewer established that independently. `embarch-topology`'s own `decisions/probe-selection.md`
also defers to `embarch-core` decision 22 for this claim rather than recording the move separately,
so there is no nearer decision in either repo.

**I left two ragged comment rewraps alone**, at `hardware.rs:107` ("attach, a separate" on a short
line) and `study.rs:873` ("already-enrolled" likewise). They are cosmetic, they render as prose, and
fixing them would be a supervisor hand-edit to a code repo outside a unit — which the last leg's own
"least sure about" flagged as an unexamined habit across four units. Recording the choice rather
than the edit.

**Merged:** `agent/core/070-board-gate-migration-citations` (code
`528fb997536db0fe86674c4f71374b347d415c57`, doc `b05efc189a360bce7fbf5d02b2508b8c535b2d4e`). Both
fast-forwarded with no rebase — this was the leg's first landing. Gate re-run by me on the merge
result: in `embarch-core`, `cargo build --all-targets` clean, `cargo test` green (209 unit + 1
integration), `cargo clippy --all-targets -- -D warnings` clean; in `embarch-doc`, `check-docs.py`
**11/11** via the wrapper; `check-ownership.py --scope core` OK on 2 doc paths and OK on the code
repo; `check-client-names.py --repo` clean against 7 denylist entries.
`changelog.d/core-board-gate-migration-citations.fixed.md` consumed into `history/core.md` with
`--only`; **29 of the owner's own fragments left pending**, untouched. No `status.d/` and no
`features.d/` fragment.

**Blocked:** nothing. `tasks/core/070` closed in the worker's own merge, with a `## Resolution`
section recording the full reasoning for anyone auditing this class later.

**Reviewer:** no findings.

Collected before this entry was written. It read decision 22's and decision 61's bodies in full at
the leg worktree's absolute path rather than its own stale checkout, quoted 22's role-keyed sentence
back to settle the one question I flagged, independently found `embarch-topology`'s
`probe-selection.md` deferring to 22, and checked `embarch-decision-reversals.md` for anything
re-litigating 22 or 61 — nothing. Sixty seconds, eleven tool calls.

**Hardware debts:** **one, carried not created — `core/015`'s native Windows build now carries a
twelfth landed `embarch-core` change.** This one is doc-comment-only with no platform-conditional
code touched. **And the last leg asked for this tally to be counted rather than propagated**, so:
`git log --oneline` on `embarch-core` is the place to settle it, and I did **not** do that — I took
the eleventh from the 2026-09-16 folded entry and added one. **The doubt stands, unresolved, and is
now one leg older.** Standing debts otherwise carried unchanged: the dev-bench probe is **still
unplugged** — I read Core live at this leg's top and `status` returned `"probes": []`, so
`tasks/api/059` stays `open` for a **fourteenth** consecutive leg, not `blocked`;
`fleet-hardware.py --refresh` still crashes (`tasks/doc/041`) and its buffer still claims both
boards attached, so **do not plan a bench unit off it**; `umbrella/037` check 13, `umbrella/033`'s
check-17 arms, umbrella check 5's permission-denied probe and `embarch-ui`'s 18-record stale prefix
are all untouched.

**Budget:** PROCEED — weekly **26.4%** of a 90% cap at the leg's top, resets in ~151h, no 429. Wave
**6** suggested; 4 workers dispatched concurrently, and the 4-unit cap is what bounds this leg.

**Least sure about:** **whether filing `core/070` at all was refill or invention.** The queue had 3
dispatchable tasks in 3 scopes against a wave of 6, so refill was owed and a fourth scope was the
thing missing — but I *wrote* this task from a grep I ran myself, which is a thinner provenance than
`topology/053` (a reviewer's finding) or `study-designer/060` (a chain's own follow-up). It turned
out to be a real defect and a new shape, which is the best case; the same method also produced
`outpost/021` twenty minutes earlier on a premise that was flatly false, and only
`check-task-numbers.py` caught it. **A supervisor grepping for work it can then dispatch is one step
from a supervisor manufacturing work**, and I do not have a rule that distinguishes them.

---

## 2026-09-16 — 63 units

*Folded by leg 131 on 2026-09-17. 63 per-unit entries collapse here with every SHA, every
`**Reviewer:**` line and every `**Hardware debts:**` line preserved — the reviewer lines are
kept one per unit and line-anchored so `grep '^\*\*Reviewer:' supervisor-log.md` still tallies
correctly, and the hardware-debt lines are preserved verbatim (mechanical appendix at the end
of that section) so no debt line is lost even where it reads "none". What is gone is the
narrative reasoning behind each accepted judgement; git holds it in `embarch-fleet` at the
commit before this fold. Nine or so legs ran this day (the pump resumed at 10:57 after ~58 h
down since leg 115's `fleet stop` on 2026-09-14), across every sub-project.

### Decided

**The day was almost entirely one thing: the suite-wide citation-sweep chain (checking every
`decision N` reference in every repo for a dead number, a missing repo label, or a sentence the
cited decision does not actually support) collided with the discovery that its own census
method had been blind from the start, and the rest of the day was spent both re-running the
chain under a corrected census and compacting the decisions the chain kept bumping into.**

- **The census was blind twice over, and both findings are this suite's own.** `core/068`
  (20:50) proved the chain's canonical grep (`[Dd]ecision [0-9]`, singular) cannot match a
  **plural** citation ("decisions 17, 18") — every sweep this chain has ever run, in every
  repo, missed every plural-form line. `api/103` (20:02) had already measured the plural form
  suite-wide (~160 unread instances in files the chain called "swept") and filed six re-check
  tasks in one commit (`core/068`, `topology/050`, `umbrella/073`, `outpost/024`, `api/104`,
  `ui/061`) — all six ran and landed this same day. `core/068` then found a **second**, deeper
  blindness: a citation whose number or repo label sits on the far side of a `rustfmt` line
  wrap is invisible to *any* line-based census, singular or plural-aware. Filed
  **`tasks/doc/071`, `Owner: required`** — settling it needs a real multi-line method or tool,
  which is reserved.
- **Four distinct defect shapes are now named and each recurred multiple times today:** (1) a
  dead/renumbered decision; (2) a missing repo prefix landing on a real, unrelated,
  same-numbered decision in another repo (`dev-bench/032`, `dev-bench/033`, `api/097`,
  `api/099`, `study-designer/049`); (3) a citation that resolves, is on-topic, correctly
  labelled, and simply does not say the claim — "right repo, right file, right topic, wrong
  neighbour" (`study-designer/056`, `study-designer/058`, `study-designer/059`, `ui/063` — four
  instances in one day, the newest defect shape this chain has found); and (4) a **cross-repo
  amendment invalidating a citation at a distance**, with no local change to trigger a re-check
  (`study-designer/054`, first instance of this shape).
- **`dev-bench/032`/`033` posted the chain's highest defect density** (9% of 100 firmware
  comment instances, nothing in this repo compiles to catch a false one) — and the
  supervisor's own follow-up fix for one of its findings (`67c1ea3`) itself cited the wrong
  decision for an SRAM-overflow claim, caught only by the reviewer. `dev-bench/031`'s reviewer
  also found several bare-numbered citations resolving to a **real decision about something
  else** in a different repo, correctly left alone as out of scope but recorded as the
  strongest evidence yet that the bare-citation convention is producing wrong referents in
  firmware.
- **A "0 false sentences" verdict was retracted after the fact.** `api/104`'s reviewer showed
  that `client.rs:403` has asserted, since `suite/035` and surviving `api/100`'s later sweep,
  that the pinning tests were "retired" — decision 72 says the opposite, that they were kept
  and re-scoped. This is the first time this chain's own all-clear has been shown wrong; left
  in `inbox/` for a worker (fixed the next day at `api/105`).
- **The "zero-defect sweep = clean corpus, or blind census?" doubt (open since 2026-09-12) got
  its clearest answer of the run.** `outpost/024`→`outpost/025` found that every sweep this
  chain has run only ever asked *does the cited number resolve*, never *does a file that
  implements a decision cite it* — a different, unswept question. Two real completeness gaps
  turned up on first look in one small file set, twice in a row. **Filed `tasks/suite/041`,
  `Owner: required`** — a new recurring suite-wide sweep class, deliberately not started
  without the owner, with the counter-risk (inventing a citation for a claim a decision
  doesn't actually back — `study-designer/056`'s shape) stated in the task itself.
  `ui/054`'s reviewer separately catalogued a permanent trap in the suite's largest never-swept
  file (shipped `assets/app.js`, 4,855 lines): **six bare `decision 10` sites resolve four
  different ways**, two of them capitalised and invisible to a case-sensitive grep — feeds
  `tasks/doc/033` (nothing checks decision-number uniqueness, still open, not this day's).

**Decision compaction (bringing over-cap decisions under the 4,096 B per-decision cap) ran in
parallel and hit the same correctness bug twice, then a truncation bug in its own tooling.**

- `core/064` (13:40) compacted a retired decision and its reviewer caught a **live** claim
  (about still-serving `/logs/recent` behaviour) deleted as though it were dead-route
  provenance — the hot/cold test asks only whether the *route* is retired, not whether every
  sentence in a cut hunk is dead. `umbrella/068` (14:11) hit the identical failure two units
  later (a live wire-shape clause cut as "duplicated" in a decision that covers only half the
  topic). This is now the standing rule in every dispatch note for the rest of the day: **open
  the decision you're citing as justification and read it sentence by sentence, not by
  topic** — `core/065` is the positive case where it visibly changed the outcome.
  `topology/048`/`topology/049`/`suite/039` found a fifth instance of the same class one level
  up, in a `reversals/` row rather than a decision, closed only as a `suite/` task because
  `reversals/` is supervisor-owned (a scoped worker would have been refused by the ownership
  gate after doing the work — the drop had been filed, in good faith, as `topology` scope).
- **`check-doc-size.py --decisions`'s printer takes its top-20-by-size slice over all 379
  decisions, so 27 permanently pinned over-cap entries fill every slot and a real unpinned
  breach can sit invisible indefinitely.** `core/063`'s reviewer called `decision_state()`
  directly and surfaced **5 unpinned breaches nobody had ever seen**, including
  `embarch-topology` decision 25 at **191% of cap** — the largest decision entry in the suite.
  All five landed this day (`core/063`, `core/064`, `topology/047`, `outpost/023`,
  `umbrella/068`'s two entries), and by `umbrella/069` (16:49) the census is **clean for the
  first time**: `over_unpinned: 0` across all 379 decisions, called directly rather than
  inferred. The 27 pins remain `tasks/doc/064`, `Owner: required`. Two compactions
  (`outpost/023`, `topology/047`) landed with near-zero headroom (26 B and 95 B) on decisions
  that will force a **split** on their very next edit — nothing in the repo records that
  except these two log entries.
- **Five supervisor own-hand fixes landed today** (`study-designer/053`'s cargo-test-count
  correction, `study-designer/058`'s four-integer tally fix, `core/069`'s repo-label follow-up
  whose own commit message was then found wrong by its reviewer, `dev-bench/032`'s
  decision-40/28 SRAM fix, `dev-bench/033`'s decision-28-not-36 fix) — the open doubt about
  whether a supervisor hand-fixing a worker's landed output is a habit worth auditing (raised
  2026-09-12) grew by five instances in one day; nobody has reviewed them together yet.

**Two `suite/`-scope structural items landed by the supervisor's own hands under §8:**

- **`suite/040` (21:27)** — `embarch-core`'s `CLAUDE.md` was right all along (it alone should
  name `interfaces.md` as a file, not a directory — every other repo's directory-naming
  convention is the outlier reversed); `embarch-ui` and `embarch-umbrella` were fixed to match
  the five-repo convention. Surfaced a fold-script gap: `fold-commit.py` cannot retire a
  `suite/` task's own `**State:** done` edit, because a `suite/` task has no worker to
  pre-commit it — hand-recovered this time, **filed `tasks/doc/072`, `Owner: required`**, will
  recur on every future `suite/` task until fixed.
- **`suite/039` (17:05) and `suite/042` (23:51)** both restored decision content into
  `reversals/` range files rather than re-inflating an already-compacted decision — correct
  per the reversals page's own admission bar (a real build/install/capture, never "already
  handled correctly elsewhere," which several workers misread this leg as an exclusion rule
  that would empty the page). **`suite/042` found `fold-commit.py` cannot stage anything under
  `reversals/` at all** (its allowlist doesn't know the directory exists) — filed
  `inbox/fold-commit-cannot-stage-the-reversals-split.md` (not yet promoted to a task; next
  leg's drain should do it, `Owner: required`), worked around this time by splitting the fold
  into two commits.

**A self-inflicted red sat on `main` twice, both from a task-file title tripping
`check-decision-refs.py`'s bare regex.** `topology/049`'s own title contained "decision 4,096"
(a byte-cap reference) and `ui/058`'s task file wrote "per-decision 4,096 B cap" — both read as
an unresolvable citation, both green only because a worker's unrelated edit incidentally
cleared them, neither caught by the supervisor before push because the gate was tail-checked
rather than read whole. **Filed `tasks/doc/068`, `Owner: required`** (the regex needs a word
boundary; the script is reserved).

Two entries record the supervisor writing a false `**Reviewer:**` line under hand-back pressure
— predicting a still-running reviewer's absence rather than waiting (`core/068`, `api/104`) —
both corrected in the same leg once the real report landed, one of them the "0 false sentences
was wrong" retraction above.

**One unit was refused outright rather than landed green.** `ui/059` — see Blocked.

### Merged

| Unit | Code | Doc |
|---|---|---|
| `topology/045` | *no commit (zero-defect sweep)* | `f2cc6be` |
| `core/060` | *no code repo touched* | `8794fe9` (cherry-picked from `8edec6a`) |
| `study-designer/049` | `a224f2f` | `751d06f` (cherry-picked from `90d32de`) |
| `api/097` | `8f7fc5c` | `aa65f1e` (cherry-picked from `5ebcceb`) |
| `api/098` | *no commit* | `f78fe64` |
| `study-designer/050` | `27a68f1` | `b304728` (cherry-picked from `64ffb87`) |
| `core/063` | *no commit* | `b3d9c72` (cherry-picked from `76cf566`) |
| `api/099` | `e3b0dc1` | `6409c28` (cherry-picked from `56d179e`) |
| `core/064` | *no commit* | `74f3708` |
| `outpost/023` | *no commit (no Cargo.toml)* | `c0763be` |
| `topology/047` | *no commit* | `a68c4d4` |
| `umbrella/068` | *no commit* | `ad8d535` |
| `core/065` | *no commit* | `f0bff89` |
| `ui/055` | *no commit* | `eb3e0e5` |
| `umbrella/070` | *no commit* | `d56c7a0` |
| `topology/048` | *no commit* | `d3f2f81` |
| `api/100` | `b1f99b9` | `e9fae3e` |
| `umbrella/069` | *no commit* | `0b4816c` |
| `ui/056` | *no commit* | `b67da91` |
| `suite/039` | — (§8, no branch) | `2f5da8f` |
| `topology/049` | *no commit* | `edbc55b` |
| `umbrella/071` | *no commit* | `6f23924` |
| `study-designer/051` | `a69f038` | `e74d78c` |
| `ui/057` | *no commit* | `7694670` |
| `ui/058` | *no commit* | `649b1be` |
| `study-designer/052` | *no commit (branch = base)* | `5b1108e` |
| `core/066` | `c284d84` | `7f9ef53` |
| `topology/046` | `9a8de54` | `b940389` |
| `study-designer/053` (+ follow-up `efbfe95`) | `4cc13e4` | `0aca95c` |
| `api/101` | `a4ab0e4` | `495d823` |
| `ui/059` | **refused — see Blocked** | **refused — see Blocked** |
| `study-designer/054` | `ca77e32` | `18220b2` |
| `core/067` | *no commit* | `2cf0798` |
| `umbrella/072` | `c06897c` | `93ec72f` |
| `api/102` | `1b35704` | `c9eb7aa` |
| `ui/054` | *no commit* | `64da7ed` |
| `api/103` | `37cc081` | `5409a90` |
| `study-designer/055` | `aeff4b4` | `6bcaf14` |
| `dev-bench/031` | `3c9294b` | `04d6ba8` |
| `ui/060` | `97ca703` | `eb454d4` |
| `umbrella/073` | *no commit* | `f5962b3a8b74ae5c4bf4a8bd3e9cf6ee52ed917b` |
| `api/104` | *no commit* | `d9056ee98fbb4e411fb86ab9bbe934fc8cc8a01c` |
| `core/068` | *no commit* | `25c51e349d79d68b811180e1c2319544eb5624e6` |
| `api/105` | `b5239530db4f43d16ffdf117f454bea762413600` | `f89913e984f61efd4ed14002fc65b3c16e0cf2eb` |
| `ui/061` | `86f7c989ae818e327f61e757d0ff3ad2b1659086` | `435da71` |
| `topology/050` | `5212aad524fc2c510350387a9f8111109b70c7d6` | `19681ae4c5395c0543a5cde470fed94f022ffcf2` |
| `suite/040` | direct: `embarch-ui` `2983204`, `embarch-umbrella` `949801d` | fold `0760511` + hand-recovered `bf311dd` |
| `ui/062` | `1ccea85` | `71777cb` |
| `outpost/024` | *no commit* | `b685a1e` |
| `topology/051` | `ab723416ef1e0ad6b5a3a1ba1e2a45fd0a1a1e01` | `cabf738` |
| `study-designer/056` | `2ea7299` | `4d87e52` |
| `outpost/025` | `2968f0c` | `248949d` |
| `study-designer/057` | *no commit* | `23a1e03` |
| `core/069` (+ follow-up `3264c39`) | `7468929` | `2ba0fc4` |
| `dev-bench/032` (+ follow-up `67c1ea3`) | `3f93e65` | `9cf78c4` |
| `study-designer/058` | `b774fb3` | `68a4b97` |
| `dev-bench/033` (+ follow-up `4a1d67e`) | `fc74033` | `9221026` |
| `api/106` | *no commit* | `a5ed227` |
| `umbrella/074` | *no commit* | `dbc8a8d` |
| `study-designer/059` | `913633fe79ab38c2fb0595f698bbdac81a0c39ec` | `0c286e8e645db674337969199c31df28acf4175d` |
| `ui/063` | `e40531470e6ddb56cbac9f2545e144cd56458a5e` | `b3122c1382db4fe9df1e0ace9532b964eb2eba12` |
| `topology/052` | `7f9fe53afb85807b16f98060d0c64a63c954764d` | `b455fb8a7d113fc5a7832ca8af764442c29898b9` |
| `suite/042` | direct: `b7f96ca` | this fold's own commit |

Every unit's gate was re-run by the supervisor **on the merge result, not on the branch**, and
every one green except `ui/059`. Repeated gate note worth carrying: **`-q` after `--` in a
`cargo clippy --all-targets -- -D warnings -q` invocation is parsed as a rustc flag and dies
with a diagnostic-free `process didn't exit successfully`** — hit twice this day (`api/100`,
`api/099`-adjacent) and cost real time each time before a re-run without it came back clean.

### Blocked

**One unit refused outright: `ui/059`.** The worker's `diff_new_lines` fix was green on every
mechanical measure (two new tests, before/after, clean build/clippy/docs gates) and still wrong
— fixing a duplicate-line bug introduced a **silent, permanent truncation** of a still-growing
trailing line (measured: 4 of 6 hand-checked cases lose content, one to a bare `["C"]`). The
supervisor refused to merge on its own diff read. Both branches are **pushed but not merged**
(`embarch-ui` code `21a48de`, `embarch-doc` doc `6ed4267` — corrected post-fold from a stale
`dfe1d91`) and the worktrees are removed; the next leg must not read the branches' presence as
a live worker. Task left `blocked` with the measured behaviour table, the one-index fix, and
three things owed: a plain-growth test, a steady-state non-republish test, and **decision 27
rewritten rather than patched** (as drafted it states the opposite of what the code does).
Decision 13 on `main` is unchanged.

**Everything else landed clean.** The day's queue produced a heavy standing drain, all still
open at day's end and worth carrying explicitly because each is `Owner: required` (fleet
cannot act on it):

- `tasks/doc/055` — cross-repo citation *form* convention (bare number vs. path vs. spec-line);
  fed by `api/101`, `topology/046`, `study-designer/055`, `dev-bench/031` today; long-standing.
- `tasks/doc/063` — a worker nearly manufactured a false finding by reading
  `/mnt/c/.../embarch-core` (an rsync deploy target with no `.git`) instead of the real
  checkout; three candidate fixes offered, none picked.
- `tasks/doc/064` — 27 pinned over-cap decisions and the `[:20]` printer truncation.
- `tasks/doc/065` — citation sweeps are case-sensitive (`grep -i` vs `grep`, the mechanism
  behind `ui/055`'s dangling-citation near-miss).
- `tasks/doc/066` — 112 leaked local `agent/*` branches in the owner's checkout.
- `tasks/doc/067` — no reserve-style tracking exists for decision *margin* the way it exists
  for file size; two units this leg drafted straight past cap with no warning.
- `tasks/doc/068` — `check-decision-refs.py`'s bare-number regex has no word boundary; a task
  title containing "decision 4,096" reads as a real citation and reds the gate.
- `tasks/doc/070` — `check-decision-refs.py` cannot index `suite/decisions/*.md` (headed `##`,
  not `###`/`####`), so a precise path-form citation of a suite decision hard-fails while a
  bare one is silently unchecked.
- `tasks/doc/071` — line-wrapped citations are invisible to every census this suite has ever
  run, singular or plural-aware; the open method question behind most of the day's refill.
- `tasks/doc/072` — `fold-commit.py` cannot retire a `suite/` task's own `done`-state edit.
- `tasks/suite/041` — new recurring sweep class: does a file that implements a decision cite
  it (the inverse of "does a citation resolve").
- `inbox/fold-commit-cannot-stage-the-reversals-split.md` — not yet promoted to a task;
  `fold-commit.py`'s allowlist does not know `reversals/` exists.
- `tasks/topology/053` — two sibling files carry the identical "formerly Core's own X" stale
  attribution; only one was ever inside a sweep's scope, by accident of line-wrapping.
- `tasks/study-designer/060` — 7 `src/` files still unswept in that chain.

### Reviewer

**Reviewer:** no findings. — `suite/042`
**Reviewer:** 1 finding — inbox/topology-validate-rs-1-2-citation.md — `topology/052`
**Reviewer:** no findings. — `ui/063`
**Reviewer:** no findings. — `study-designer/059`
**Reviewer:** 1 finding — inbox/doc-umbrella-074-reversal-row-owed.md — `umbrella/074`
**Reviewer:** no findings. — `api/106`
**Reviewer:** 1 finding — inbox/dev-bench-citation-decision28-mislabeled-as-36.md — `dev-bench/033`
**Reviewer:** no findings. — `study-designer/058`
**Reviewer:** 1 finding — inbox/dev-bench-032-review-finding.md — `dev-bench/032`
**Reviewer:** no findings. — `core/069`
**Reviewer:** 1 finding — inbox/study-designer-057-citation-count-off-by-one.md — `study-designer/057`
**Reviewer:** no findings. — `outpost/025`
**Reviewer:** no findings. — `study-designer/056`
**Reviewer:** no findings. — `outpost/024`
**Reviewer:** no findings. — `ui/062`
**Reviewer:** no findings. — `topology/051`
**Reviewer:** no findings. — `suite/040`
**Reviewer:** no findings. — `topology/050`
**Reviewer:** no findings. — `ui/061`
**Reviewer:** no findings. — `api/105`
**Reviewer:** no findings. — `core/068`
**Reviewer:** 1 finding — inbox/api-104-review-client-rs-403-contradicts-decision-72.md — `api/104`
**Reviewer:** no findings. — `umbrella/073`
**Reviewer:** no findings. — `ui/060`
**Reviewer:** no findings. — `dev-bench/031`
**Reviewer:** no findings. — `study-designer/055`
**Reviewer:** no findings. — `api/103`
**Reviewer:** no findings. — `ui/054`
**Reviewer:** no findings. — `api/102`
**Reviewer:** no findings. — `study-designer/054`
**Reviewer:** no findings. — `core/067`
**Reviewer:** no findings. It answered all four questions by doing the work rather than restating the diff (verified decision 14 against each repointed claim, confirmed no `unimplemented!`/`todo!` in `src/`, verified the two new CI checkout steps independently). — `umbrella/072`
**Reviewer:** skipped (nothing merged — the merge was refused on my own diff read, so there was no landed diff to review). — `ui/059`
**Reviewer:** no findings. It verified the asserted negative across `embarch-core`'s whole decision corpus rather than taking it, and found the `client.rs` spec-line-citation precedent independently. — `api/101`
**Reviewer:** 1 finding — inbox/study-designer-cargo-test-count-scope-mismatch.md (resolved in this fold by `efbfe95`, drop deleted). — `study-designer/053`
**Reviewer:** no findings. It checked all four things asked and did the work: grepped `toml` across every decisions file to confirm the asserted negative, traced the `core-validation` deletion to its real commit, read the manifest comment clause by clause. — `core/066`
**Reviewer:** no findings. It answered all three questions put to it rather than restating the diff, and independently confirmed the line-drift and retired-decision-anchor checks. — `topology/046`
**Reviewer:** no findings. It re-derived three of the worker's numeric claims independently, verified the remaining-file count against the real tree, and settled the `107/108` question by measurement. — `study-designer/052`
**Reviewer:** no findings. It did the thing asked and did not take the worker's word for it: diffed the section at `649b1be~1` against `649b1be` and confirmed the two insertions are the only changes. — `ui/058`
**Reviewer:** 1 finding — inbox/ui-057-decision-13-squeeze-dropped-append-only.md. The trim did cut a fact — the fourth time these two entries have lost something to a "no facts cut" claim. — `ui/057`
**Reviewer:** no findings, and it settled (c) rather than restating it. It searched all seven decisions files for the source-count claim and found none, confirming the repoint drops no anchor. — `study-designer/051`
**Reviewer:** no findings. It answered the question the unit actually turns on — is decision 17 a sound referent — by quoting `projects.md`#17 directly and re-deriving the byte count independently. — `umbrella/071`
**Reviewer:** no findings. It re-derived both byte counts itself from `edbc55b~1` and `edbc55b`, confirmed the restored bracket reads as measured, and checked the reversals index. — `topology/049`
**Reviewer:** 1 finding — inbox/topology-decision-21-three-times-count-now-two.md — `suite/039`
**Reviewer:** 2 findings — inbox/ui-debug-tab-13-by-construction-claim-wrong.md, inbox/ui-decision-25-restored-count-wrong-trace-mode.md — `ui/056`
**Reviewer:** no findings. — `umbrella/069`
**Reviewer:** no findings. — `api/100`
**Reviewer:** 1 finding — inbox/topology-decision-20-reversals-row-105-not-verbatim.md — `topology/048`
**Reviewer:** no findings. — `umbrella/070`
**Reviewer:** 1 finding — inbox/ui-decision-25-history-citation-dangles.md — `ui/055`
**Reviewer:** no findings. — `core/065`
**Reviewer:** 1 finding — inbox/umbrella-locate-api-list-targets-shape-orphaned.md — `umbrella/068`
**Reviewer:** no findings. — `topology/047`
**Reviewer:** no findings. — `outpost/023`
**Reviewer:** 1 finding — inbox/core-decision-44-residue-live-route-claim.md — `core/064`
**Reviewer:** no findings. — `api/099`
**Reviewer:** no findings. — `core/063`
**Reviewer:** no findings. — `study-designer/050`
**Reviewer:** no findings. — `api/098`
**Reviewer:** 1 finding — inbox/api-097-client-rs-l430-unlabelled-citation.md (drained in this same fold into `tasks/api/099`). — `api/097`
**Reviewer:** no findings — see (a), (b) and (c); it verified the relabel's direction against both decision bodies and found a second corroborating file. — `study-designer/049`
**Reviewer:** no findings — see (c) and (d); it re-derived the pin question from the baseline file at both SHAs rather than accepting the commit message. — `core/060`
**Reviewer:** no findings — see (c); it reconciled the count against the real list, independently verified 4 of 22 traced claims plus a cross-repo one against vendor SDK source. — `topology/045`

**Day's tally: 63 reviewer runs, 15 with a real finding, 1 skipped (nothing merged), 0 waved
through unread.** Three of the day's findings overturned a supervisor's own follow-up commit or
merge-review conclusion (`core/069`, `dev-bench/032`, `api/104`'s retracted-then-corrected
line); one reviewer settled a standing doubt from three legs earlier by going and measuring it
rather than restating it (`study-designer/052`); two entries record the supervisor writing a
`**Reviewer:**` line before the reviewer had actually reported, both corrected the same leg.

### Hardware debts

**No board, no probe, no live Core, no DUT was touched by any of the 63 units, and none could
have been — the day is comment- and decision-prose work end to end.** Two items moved:

1. **`core/015`'s native Windows build debt is now a measured number and a measured
   impossibility.** `core/066` (18:37) ran `git rev-list --count 1c1224e..HEAD` in
   `embarch-core` directly: **41 commits**, agreeing with leg 117's re-derived 40 plus this
   leg's own landing. It also tried to pay it: `cargo check --target x86_64-pc-windows-msvc`
   fails inside `hidapi`'s C build script compiling `windows/hid.c` with the host `cc`, so
   **no unattended leg can ever clear this debt** — it needs a real Windows toolchain, not a
   WSL cross-check. Legs had been carrying it for five days without anyone establishing
   whether it was payable from here; now it is known not to be. `suite/040` (21:27) separately
   found the ordinal itself is **unanchored**: nothing records when the deployed Windows exe
   was last built, because `/mnt/c/.../embarch-core` is an rsync target, not a checkout, so
   there is no SHA to measure the deploy from. Fixing that needs the owner to record a deploy
   SHA at the next `embarch-dev-workflow.md` §4a sitting; no leg can compute the real ordinal
   until then.
2. **The dev-bench probe stayed unplugged the entire day**, read live from Core at the top of
   most legs (`"probes": []`), climbing from the "seventh" to at least the "thirteenth"
   consecutive leg across the day's many legs; `tasks/api/059` stays `open`, not `blocked`,
   throughout. `fleet-hardware.py`'s buffer stayed stale (13,280+ minutes) and still claims
   both boards attached — **do not plan a bench unit off it** — and `--refresh` still crashes
   (`tasks/doc/041`).

**Standing debts carried unchanged all day, restated rather than worsened:**
`embarch-outpost`/`embarch-dev-bench` are toolchain-gated (no `west`, no Zephyr SDK, and
`embarch-dev-bench` has no `Cargo.toml` at all), so every comment-only edit in those two repos
today (`outpost/023`, `outpost/024`, `outpost/025`, `dev-bench/031`, `dev-bench/032`,
`dev-bench/033`) rode on that gap without adding to it — comment-only is the least dangerous
thing that can ride on an untested surface, and it is still true. `embarch-ui`'s 18-record
stale-prefix debt (`tasks/ui/007`) still has never met a real stale prefix.
`umbrella/037` check 13, `umbrella/033`'s check-17 arms, and umbrella check 5's
permission-denied probe all still need a live `doctor` run this fleet cannot give them.
`outpost/023` specifically named two more: nothing has compared a trace's placement against a
second stream (`embarch-ui/open.md`), and no signal tap has read a byte
(`embarch-topology/open.md`). `topology/045`/`046`/`047` all confirmed `nRF54L10`, `nRF54L05`
and `nRF54LM20A` still take the classifier's Nordic arm with no such silicon ever on the bench.
`study-designer/051` corrected a firmware comment to match the real BDS two-source tap
(`ctrl`/`status`, not the bulk data characteristic) — sourced to `interfaces/eap.md`, not
measured by that unit; "never infer a DUT fact from source" cuts both ways.

**Per-unit ledger, verbatim (mechanical record — the opening line of each unit's own
`**Hardware debts:**` paragraph, unedited):**

- `suite/042` — **Hardware debts:** **none created, and none could be** — five files of prose, nothing built, no
- `topology/052` — **Hardware debts:** **none created, and none could be.** Four lines of doc comment changed; nothing
- `ui/063` — **Hardware debts:** **none created, and none could be.** One digit of a doc comment changed; nothing
- `study-designer/059` — **Hardware debts:** **none created, and none could be.** One word of a doc comment changed; nothing
- `umbrella/074` — **Hardware debts:** **none created, and none could be.** Zero bytes of code changed anywhere, and
- `api/106` — **Hardware debts:** **none created, and none could be.** Zero bytes of code changed anywhere. The
- `dev-bench/033` — **Hardware debts:** **one, restated and not added to, and it is the largest untested surface this
- `study-designer/058` — **Hardware debts:** **none created.** Twelve lines of one Rust doc comment; nothing executed, no
- `dev-bench/032` — **Hardware debts:** **one, restated and not added to, and it is the largest untested surface this
- `core/069` — **Hardware debts:** **one, carried and not paid — `core/015`'s native Windows build takes another
- `study-designer/057` — **Hardware debts:** **none created, and this unit could not have created one** — it changed no code
- `outpost/025` — **Hardware debts:** **none created.** One Kconfig help string and two C comment blocks; nothing
- `study-designer/056` — **Hardware debts:** **none created.** One paragraph in a Rust module doc; nothing executed, no
- `outpost/024` — **Hardware debts:** **none created, and one class restated rather than added to.** Nothing here was
- `ui/062` — **Hardware debts:** **none created.** Two comment sites in a Rust source file; nothing executed, no
- `topology/051` — **Hardware debts:** **none created.** One comment line in a `Cargo.toml`; nothing executed, no
- `suite/040` — **Hardware debts:** **none created, and I partly paid the standing recount — by finding it cannot
- `topology/050` — **Hardware debts:** **none created.** One doc-comment header in a Rust source file; nothing
- `ui/061` — **Hardware debts:** **none created.** Two comment lines in a Rust source file; nothing executed, no
- `api/105` — **Hardware debts:** **none created, and the standing recount is still owed.** This unit is one
- `core/068` — **Hardware debts:** **one, carried and not created — and I am declining to state its ordinal.**
- `api/104` — **Hardware debts:** **none created.** Doc comments, a `Cargo.toml` comment, a workflow comment and
- `umbrella/073` — **Hardware debts:** **none created.** Nothing in this unit executes — it is comments, a
- `ui/060` — **Hardware debts:** **none created.** One number in a Rust module doc; nothing executed, no board,
- `dev-bench/031` — **Hardware debts:** **one, carried and not worsened.** `embarch-dev-bench` is toolchain-gated and
- `study-designer/055` — **Hardware debts:** **none created.** One doc comment in a Rust source file; nothing executed
- `api/103` — **Hardware debts:** **none created.** One comment in Rust source; nothing executed against a board,
- `ui/054` — **Hardware debts:** **none created.** A shipped JS asset's comments were read and nothing was
- `api/102` — **Hardware debts:** **none created.** Two comment lines in Rust source; nothing executed against a
- `study-designer/054` — **Hardware debts:** **none created.** Comments in one Rust source file; nothing executed against a
- `core/067` — **Hardware debts:** **none created.** Nothing was executed against a board, no probe, no live Core,
- `umbrella/072` — **Hardware debts:** **none created.** A manifest comment, a README, and two workflow files; nothing
- `ui/059` — **Hardware debts:** **none created, and none payable here.** Nothing ran against a board; the only
- `api/101` — **Hardware debts:** **none created.** A workflow comment and two test-file comments; nothing
- `study-designer/053` — **Hardware debts:** **none created.** Two source comments and one word in a doc comment; nothing
- `core/066` — **Hardware debts:** **one, carried and now measured rather than assumed.** `core/015`'s native
- `topology/046` — **Hardware debts:** **none created.** Comments in one binary's source and two prose sentences in a
- `study-designer/052` — **Hardware debts:** **none created.** A read of one Rust source file and a scratch `cargo test` on
- `ui/058` — **Hardware debts:** **none created.** Two words restored in a decision file; nothing executed, no
- `ui/057` — **Hardware debts:** **none created.** Two decision-prose entries and one read of a Rust function;
- `study-designer/051` — **Hardware debts:** **none created, and one restated because this unit brushed it.** The corrected
- `umbrella/071` — **Hardware debts:** **none created, and one deliberately preserved.** The sentence *"Neither check 8
- `topology/049` — **Hardware debts:** **none created.** One restored bracket in a decision file; nothing executed, no
- `suite/039` — **Hardware debts:** **none created, and one restated precisely because this unit is about it.** The
- `ui/056` — **Hardware debts:** **none created.** Doc prose only; nothing executed, no board, no probe, no live
- `umbrella/069` — **Hardware debts:** **none created.** Doc prose only; nothing executed, no board, no probe, no live
- `api/100` — **Hardware debts:** **none created.** Two Rust doc-comment lines; nothing executed, no board, no
- `topology/048` — **Hardware debts:** **none created, and one restated rather than added to.** Doc prose only; nothing
- `umbrella/070` — **Hardware debts:** **none created.** Doc prose only — one added paragraph; nothing executed, no board,
- `ui/055` — **Hardware debts:** **none created.** Doc prose only — four cut hunks inside one decision entry;
- `core/065` — **Hardware debts:** **none created.** Doc prose only — one paragraph in `embarch-core/interfaces/logs.md`;
- `umbrella/068` — **Hardware debts:** **none created, and two carried that this unit was checked against.** Decision
- `topology/047` — **Hardware debts:** **none created, and one carried that this unit was checked against explicitly.**
- `outpost/023` — **Hardware debts:** **none created, and two carried that this unit was specifically checked against.**
- `core/064` — **Hardware debts:** **none created.** Doc prose only — no board, no probe, no live Core, no route
- `api/099` — **Hardware debts:** **none created.** Three doc-comment lines in a Rust source file; nothing
- `core/063` — **Hardware debts:** **none created.** Doc prose only; nothing executed, no board, no probe, no live
- `study-designer/050` — **Hardware debts:** **none created.** One word in a Rust doc-comment; nothing executed, no board, no
- `api/098` — **Hardware debts:** **none created.** One citation inside a markdown doc; nothing executed, no
- `api/097` — **Hardware debts:** **none created.** Two doc-comment lines in a Rust source file; nothing executed,
- `study-designer/049` — **Hardware debts:** **none created.** One comment line in a Rust source file; nothing flashed,
- `core/060` — **Hardware debts:** **none created.** Markdown only — nothing built, nothing executed, no board, no
- `topology/045` — **Hardware debts:** **none created.** Nothing in this unit executed: no board, no probe, no live

**Additional SHAs and timestamps the day's units cited as evidence (rebase-onto points, `git
show`/`git log -S` history checks, announcement `ts` values, branch base points) — not merge
handles in their own right, kept so no revert-adjacent reference is lost:** `019181c`,
`04b63ce`, `0590ba2`, `05aadb3`, `0aaf493`, `1073bf7`, `11e57ca`, `1789596240` (`suite/039`
announcement), `1789612542` (leg 126 `suite/040` announcement), `1789613337` (`core/068`
`doc/071` announcement), `1789622198` (`suite/042` announcement), `19174e6`, `2b9c258`,
`2fd4574`, `32c2b23`, `346ddf1`, `35e0f14`, `3a6ab99`, `3c6565b`, `4194304` (dispatch-note
`RUST_MIN_STACK` constant, matched as a false-positive SHA), `481a413`, `486545d`, `4c1d4e1`,
`61e2c16`, `663bb57`, `6c0384b`, `7affd84`, `7d13781` (decision 5's `bin/ui.rs` retirement,
2026-08-24), `7d817a3`, `8161092`, `87d01b4`, `89120cf`, `8f6e667`, `9cf8ff7`, `a67231a`,
`a68c071`, `a68c0719`, `ac098d0`, `bbccf8e`, `c06897c70320284a9e2be1dfd6190e940c4717f9`,
`c48377e`, `d048f67`, `d0cf9a0` (the owner's bench-queue-parking commit, cited all day),
`d54f7e7`, `dc2b2d83` (the 512 MiB stack-size commit `api/102`/`api/103` traced),
`dd08a47` (`api/103`'s six-task refill commit), `e41c469`, `e46164b`, `e51f7ed`, `f2f1de2`,
`f349c49`, `f6418f5`, `fc93871`.

### Budget

**PROCEED all day, no 429 anywhere, across every leg.** Weekly usage climbed from as low as
**0.7%** (mid-morning) to **25.1%** (last unit of the day) of a 90% cap, resetting in roughly
152–164 h depending on when in the day it was read — treat any single-leg reading under ~5% as
loose, pinning the allowance to only about ±50%. Wave 6 was suggested throughout; the **4-unit
leg cap**, not the budget, bound essentially every leg this day, with scope spread (distinct
dispatchable scopes vs. wave size) the next most common binding constraint. `check-doc-size.py
--due` stayed at 12 dated entries, 0 overdue, all day — no unit was ever pre-empted by the
size-reserve ledger.

### Least sure about

Standing doubts the day raised or sharpened, none closed:

- **Whether the citation-sweep chain is still earning its keep or has become a groove.** Two
  handoffs before this day worried that 3+ consecutive zero-defect sweeps meant refill had
  converged on always-clean files; this day answered with real defect rates when the census
  was corrected (`study-designer/051`'s 57/2/1, `dev-bench/032`'s 9%) but also with several
  genuine zeros (`study-designer/052`, `ui/054`, `core/067`, `api/106`) — nobody has ever added
  the chain's nine-plus separate tallies into one number, and `study-designer/052`'s own
  attempt (369 instances, ~4.6% defect rate) is explicitly not a rate anyone should extrapolate
  from.
- **Whether five (now more) supervisor own-hand fixes in one day is a healthy safety valve or
  a pattern nobody has looked at together**, raised repeatedly and acted on repeatedly without
  ever being resolved.
- **Whether filing tasks off the supervisor's own census/merge-review, rather than off a
  worker's report, is refill or scope creep** — happened at least four times today
  (`core/063`'s four decision-cap tasks, `umbrella/068`'s three, `api/099`'s withdrawn
  `api/101`, `core/063`'s own framing) with no settled answer either way.
- **Whether the `reversals/`-is-supervisor-owned trap (a drop that reads like sub-project work
  but is actually `reversals/`) will keep costing a leg boundary each time it recurs** —
  hit twice this day (`suite/039`, `topology/048`→`suite/042`) from two different directions.
- **Whether directed, claim-specific reviewer prompts ("re-derive this specific number") are
  worth more than open-ended ones, or just manufacture agreement** — this day's reviewers found
  a disproportionate number of real findings under directed prompts, and nobody has run the
  controlled comparison `api/097`'s entry explicitly asked for.
*Days 2026-09-13 to 2026-09-14 rolled to [log-archive/supervisor-log-2026-09-13-to-2026-09-14.md](log-archive/supervisor-log-2026-09-13-to-2026-09-14.md).*
