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

## 2026-09-16 11:45 — topology/045 a zero-defect sweep whose zero survived an independent check, and a stale tree that nearly manufactured a defect

**Decided:** **two things, neither a design call.** (a) Leg 116 is the first leg of the run the
listener latched at 10:57 today, after leg 115 ended on the owner's `fleet stop` on 2026-09-14; the
pump had been down ~58 h. (b) This unit's refill task was **filed by me this leg** rather than drawn
from the queue, and the reasoning is the part worth keeping. Four things.

**(a) The task exists because of a doubt two previous legs raised and neither could settle.**
`ui/049` and `umbrella/066` both asked, independently, whether three-plus consecutive zero-defect
citation sweeps mean the corpus is clean or mean **refill has converged on picking always-clean files
by size**. Nothing tracks per-sweep hit rate, so the question cannot be answered by looking at the
tally. So instead of filing a fifth citation sweep I filed a **different class**: the reversals page's
own **shape 8 — "the comment names the right invariant; the code does not implement it"** (rows 100,
101, 102, 104), which that page records as having produced **three findings in one pass** and which
has never been run over `embarch-topology`. I bounded it to the enrolment trio
(`hardware_id.rs`, `enrollment.rs`, `validate.rs`, ~1,640 of the crate's 4,612 lines) on the argument
that reading a third properly beats skimming all of it.

**It came back zero.** That is a real answer to the doubt rather than another instance of it: a
different defect class, in a repo that has produced exactly this defect before (`topology/020`,
*"crate.md decisions 4 and 8 claim a uniqueness the crate cannot enforce"*), still found nothing.

**(b) The worker reported three numbers, not one, and that is why the zero is worth anything.**
**53 comments read that make a checkable claim; 22 traced into the code and confirmed; 4 left
`unsettled` and named with line numbers; 27 excluded** as citation/rationale text already covered by
`topology/036`'s closed sweep. 22 + 4 + 27 = 53. The task file required the traced count to be stated
separately from the read count precisely because they are different numbers and only the second is
evidence.

**(c) The reviewer did not take the zero on trust, and went past what the worker could reach.** It
re-derived the arithmetic against the actual list in `git show f2cc6be` rather than the asserted
total, spot-checked **4 of the 22** traced claims against real source (`classify_chip`'s ordering at
`hardware_id.rs:93-114`; `upsert`'s `retain` at `enrollment.rs:207` evicting on serial-**or**-role by
De Morgan; `validate.rs:145-152` logging via `alert::record` *before* constructing
`TopologyMismatch`; and the cross-repo `resolve_probe`→`select_probe` delegation at `embarch-core`
`src/hardware.rs:92-99`), and then **located Zephyr's `hwinfo_nrf.c`/`hwinfo_esp32.c` and ST's
`stm32g0b1xx.h` on this machine** — in `embarch-dev-bench`'s west workspace — and matched the quoted
pseudocode byte for byte, plus `UID_BASE (0x1FFF7590UL)`. So all four `unsettled` claims are in fact
**true**. That does not make the worker wrong: it declined to assert what it could not reach from its
own session, which is the `api/095` discipline and the opposite of `umbrella/066`'s 114/0-for-113/1.

**(d) The near-miss is the most reusable thing this unit produced, and it is not in the diff.**
Verifying the `resolve_probe` claim, the worker first read
`/mnt/c/Users/tmp12/source/repos/embarch-core` — **an rsync deploy target with no `.git`**, not a
checkout — found the *pre*-decision-61 hand-rolled duplicate still sitting there, and was about to
report a real shape-8 defect. It caught itself against
`/home/gabriel/Github/embarch/embarch-core`. **A stale tree does not fail; it manufactures a finding
of exactly the class the sweep is hunting** — the reversals page's shape 5, "a guess
indistinguishable from an answer", turned on the fleet itself. The fix belongs in
`embarch-dev-workflow.md` §4a or the worker agent definition, both owner-reserved, so I filed
**`tasks/doc/063`** (`Owner: required`) with three options rather than picking one. **I removed the
task file carrying the worker's full 22-claim trace list per convention; it survives in commit
`f2cc6be` and nowhere else.**

**Merged:** `agent/topology/045-comments-vs-code-in-enrolment-trio` — **code: none.** The
`embarch-topology` branch was pushed identical to `main` with **zero commits** (`rev-list --count
origin/main..branch` = 0), because a zero-defect sweep changes nothing; the ref exists only so I
could see the worker had finished. Doc `f2cc6be` in `embarch-doc`, fast-forwarded from `9cf8ff7`.
Gate re-run by me on the merge result: `check-docs.py` **11/11**; `check-client-names.py --repo
embarch-topology` clean against 7 denylist entries; `check-ownership.py --scope topology` OK on the
doc branch (1 path) before the merge. **I did not re-run `cargo build`/`test`/`clippy`, and that is
a deliberate gap worth naming**: with zero code commits the merge result in `embarch-topology` *is*
`main`, so a cargo run would have gated an unchanged tree and said nothing about this unit. The
worker reports it green (80+5 tests); I did not verify that and it does not matter here.
**No `changelog.d/`, `status.d/` or `features.d/` fragment** — nothing changed, so there was nothing
to consume, and `build_changelog.py --check`/`build_features.py --check` both confirm the assemblers
were already in sync (29 of the owner's fragments pending, untouched).

**Blocked:** nothing. `tasks/topology/045` closed and removed; `tasks/doc/063` filed, `Owner:
required`, so it is visible in the queue and dispatchable by nobody.

**Reviewer:** no findings — see (c); it reconciled the count against the real list rather than the
asserted total, independently verified 4 of the 22 traced claims and the cross-repo one, cross-read
`topology` decisions 4, 8, 21, 23, 25 and `core` decision 61, and settled all 4 `unsettled` claims
against vendor SDK source the worker could not reach.

**Hardware debts:** **none created.** Nothing in this unit executed: no board, no probe, no live
Core, no `validate` call, no enrolment — the task file forbade all of it explicitly. **The dev-bench
probe is still unplugged** — I read Core live at this leg's top and `status` returned `"probes": []`,
so `tasks/api/059` stays **open**, not blocked, for the **seventh** consecutive leg. Note also that
the owner parked every bench task in `d0cf9a0` ("the owner is taking the DUT questions himself"), so
no bench unit was eligible regardless. `core/015`'s native Windows build is untouched by this unit
(`embarch-topology`, not `embarch-core`); the re-derived count to carry forward is **40 commits since
`1c1224e`**, not an incremented ordinal. `fleet-hardware.py --refresh` still crashes
(`tasks/doc/041`) and I did not rely on its buffer.

**Budget:** PROCEED throughout — weekly **0.7% → 1.6%** of a 90% cap, resets in ~164 h. Wave **6**
suggested; I used **4**, bounded by the unit cap and not by the budget. **Treat that percentage as
very loose**: a reading at 1.6% pins the allowance to roughly ±50%.

**Least sure about:** **that I filed this task's number by reading the directory** —
`tasks/README.md` line 17 warns in bold not to, because completed tasks are `git rm`'d and the
highest number on disk is not the highest ever issued. History carried `topology` to 044 and 037 was
already spent. `check-task-numbers.py` caught it as a **push-time warning, not a refusal**, so it
printed four times and `main` briefly carried a reissued number before I renumbered to 045. The
mechanism worked, but it worked *after* the push, and a supervisor that had been less attentive to a
warning it had already seen three times would have left it.

---

## 2026-09-14 — 8 units

*Folded by an `embarch-log-folder` subagent on 2026-09-16, dispatched by leg 116 on its
first unit per protocol.md §11. Eight per-unit entries (legs 114 and 115) collapse here
with every SHA, every `**Reviewer:**` line and every `**Hardware debts:**` line preserved
verbatim. What is gone is the narrative reasoning behind each accepted judgement; git holds
it in `embarch-doc` at the SHAs below and in `embarch-fleet` history before this commit.*

**Two legs ran this day.** Leg 114: `ui/052` (00:15), `core/061` (00:18), `api/096`
(00:19), `outpost/022` (00:31, its fourth and last unit). Leg 115: `core/062` (00:54, its
first unit), `topology/044` (00:57), `ui/053` (01:04), `api/095` (01:14, its fourth and
last unit, run past a `fleet stop`).

### Decided

**The one numbered decision of the day is `core/061`'s field name.** Decision 63
deliberately left the name open ("name it for the fact, not for power"), which is fine for
one implementer and impossible for two running in parallel — `tasks/core/061` spanned two
code repos (`embarch-core` sets the flag, `embarch-api`'s client crate deserializes it), and
§5 gives a worker one repo. The supervisor split it into `core/061` (kept) and
**`api/096`** (filed), pinned the name **`source_deferred`** before dispatch — the
roadmap's own word for power sampling is *deferred, not cancelled*, so the name carries the
general fact and a second deferred source later fits the same field — and ran both workers
side by side with neither waiting on the other (`#[serde(default)] Option<bool>` lets either
land first). Both landed spelling it identically, verified by the reviewer against the
landed `embarch-core` merge rather than against the task file that pinned it. **Rejected
alternatives, recorded because a supervisor closing an open question never gets a number or
a review**: one worker with two worktrees (breaks the one-repo-one-branch rule), and
re-scoping to `suite` to do it themselves (a §4 announcement window for a design decision
leg 113 had already announced).

Everything else was "nothing numbered," and five things are worth carrying past the ledger:

- **`ui/052` uncovered a supervisor-authored bug that cost three workers a wrong
  diagnosis.** Two task files the leg-115 supervisor wrote (`tasks/api/096`, the edit to
  `tasks/core/061`) cited `../../embarch-fleet/protocol.md` as a markdown link — two `../`
  from `tasks/<scope>/` lands on `embarch-doc`'s own tracked `embarch-fleet/` sub-project
  directory, not the sibling repo. `ui/052`'s worker, and later two more, hit a RED
  `check-links.py` and called it "pre-existing baseline noise" from `embarch-fleet` being an
  empty worktree stub. **It was not pre-existing.** Only re-running the gate on the merge
  result caught it; fixed in the `ui/052` fold, and `api/096`'s worker independently fixed
  its own half on-branch with three `../`, the form that landed.
- **`core/062` found that presence-on-remote is not proof a worker finished.** Step 0
  found two `agent/*` branches (`api/096-...-doc`, `core/052-...`) that `git cherry
  origin/main <branch>` reports **unmerged, and always will**, because their content landed
  via a cherry-pick that *conflicted*, and a conflict resolution is a different patch id by
  construction. `fold-commit.py` retires a branch only on `git cherry`'s `-`, so both are
  permanently stranded — `core/052` since 2026-09-13. Not data loss (both diffed
  byte-identical against `origin/main`), but a false positive against a rule whose whole
  strength is that presence never lies. Filed as `tasks/doc/061`, owner-required —
  and the supervisor itself wrote that task's `**Owner:**` field as `**required**`
  (bolded), which made it invisible to `queue-status.py`'s parser and had it reporting as
  dispatchable; caught on the post-fold queue read and unbolded. Both of the leg's new
  `doc` tasks are correctly `Owner: required` now.
- **`outpost/022` closed the citation-sweep series clean, and this fold also carries
  2026-09-13's own day fold and roll**, landed inside this unit: an `embarch-log-folder`
  subagent folded 78 numbered units (80 landed sub-units) into one dated entry — 471,249 B
  down to 69,325 B, ledger satisfied on 263/263 SHAs, 80/80 reviewer lines and 48/48
  hardware-debt lines — then rolled 2026-09-12 into `log-archive/`. It was owed on leg
  115's... no, leg 114's first unit and landed on its fourth, three units late, because the
  471 KB day took 22 minutes; safe only because `fold-day.py` splices the day's own block
  and never rewrites retained text. Its own two carry-forwards, both since resolved or
  reduced: the `core/015` Windows-build tally was narrated with three different ordinals
  through 2026-09-13 (fixed by `core/062`'s recount below), and reviewer completions
  misrouted to the listener five times that day (`tasks/doc/042`, still open).
  Separately, `outpost/022`'s own reviewer found `check-decision-refs.py`'s `DEF_HEAD`
  regex matches only `###`/`####` headers while `suite/decisions/*.md` uses `##`, so all
  four `suite` decision definitions are invisible to the resolver and the script reports
  **877 of 1,995 references "ambiguous ... not an error"** — 44% of the corpus unchecked,
  in the one scope every repo cites. Filed as `tasks/doc/060`, owner-required.
- **`ui/053` re-opened the split-vs-squeeze question on `open.md` and found the tooling
  cannot hold the seam it found.** A third squeeze of `embarch-ui/open.md` out of reserve
  in four units; the worker found a real seam (trace, second-stream-placement and row-cap
  bullets share a reader) but `check-doc-size.py`'s `CAPS` defines a mission-split role only
  for `decisions.md` and `interfaces.md`, none for `open.md` — a split file falls through to
  `legacy`, 25 KB, unratcheted, described by the script's own comment as debt to migrate
  *out of*. Squeezing today is honest; splitting today would move debt rather than pay it.
  Filed as `tasks/doc/062`, owner-required: if this file hits reserve a third time,
  squeezing stops being defensible and there is still nowhere for the split to land.
- **`api/095` found the sharpest instance of the bare-citation defect series yet, cut the
  sweep short at a `fleet stop`, and filed the remainder.** Three bare `decision 59`
  citations in `embarch-api/crates/embarch-core-client/src/client.rs` resolve, under this
  suite's bare-is-same-repo convention, to `embarch-api`'s decision 59 — a real decision in
  the right repo about the wrong thing. All three describe `embarch-core`'s decision 59
  instead (the `kind`/`fix_it_url` split), invisible to anything mechanical since the number
  resolves and the repo is right; found only by reading the body. 39 of ~105 cited lines
  were checked across six decision files: 3 wrong labels fixed, 0 false sentences in the
  checked subset, **1 explicitly left unsettled** (L403's `(decisions 37, 38)`, whose
  language the worker judged belongs to decision 72 but could not confirm because 37/38's
  pre-compaction wording is unrecoverable) — the worker refused to resolve it either way,
  which `umbrella/066` failed at previously. Remainder enumerated in `tasks/api/097`, filed
  `open`.

### Merged

| Unit | Code | Doc |
|---|---|---|
| `agent/ui/052-decision-7-retention-line-doc` | *none — branch carried zero commits by design* | `e9018e9` (fast-forwarded, parent `e3e5569`) |
| `agent/core/061-power-tap-says-so-in-stream-index` | `e1b796e` (fast-forwarded, parent `2e9eeed`) | `d95dc58` (cherry-picked from branch commit `f7d20a6`; `--ff-only` refused, `ui/052`'s fold had already moved `main`) |
| `agent/api/096-deferred-source-flag-client-half` | `c26d930` (fast-forwarded, parent `3e0e4ba`) | `99a166c` (cherry-picked from branch commit `caee440`; `--ff-only` refused by two intervening folds, and the cherry-pick **conflicted** on the task file — resolved to the worker's version, later removed by its own fold) |
| `agent/outpost/022-citation-sweep-non-c-sources` | *none — a clean sweep edits nothing* | `e8364bc` (cherry-picked from branch commit `e4e9f3e`) |
| `agent/core/062-core-comments-vs-ui-052` | `1073bf7` (fast-forwarded, parent `e1b796e`) | `7e851c1` (fast-forwarded, parent `04020d8`; `--ff-only` accepted — leg 115's first fold) |
| `agent/topology/044-compact-topology` | *none, confirmed by commit count against `origin/main` before landing* | `32caf10` (cherry-picked from branch commit `3ca94a8`; `--ff-only` refused, `core/062`'s fold had already moved `main`) |
| `agent/ui/053-compact-ui` | *none, confirmed by commit count before landing* | `c70aae5` (cherry-picked from branch commit `1a3319e`; `--ff-only` refused, `topology/044`'s fold had already moved `main`) |
| `agent/api/095-core-client-citation-sweep` | `1de0c09` (fast-forwarded, parent `c26d930`) | `f3b5b6a` (cherry-picked from branch commit `4a46589`; `--ff-only` refused, `ui/053`'s fold had already moved `main`) |

Every unit's gate was re-run by the supervisor **on the merge result, not on the branch**:
`cargo build` / `cargo test` / `clippy --all-targets -- -D warnings` wherever Rust changed
(209 tests passed on both `core/061` and `core/062`'s Core runs), `check-client-names.py`
clean against 7 denylist entries wherever code changed, `check-docs.py` **11/11** on every
unit, `check-ownership.py` OK on both halves before each merge. `outpost/022` has no
`Cargo.toml`; its gate was `tests/decoder_unit.py` (31 tests) and `tests/vocab_check.py`,
repo `main` unchanged at `8f6e667` (the commit taken as the sweep's scope baseline, landed
by leg 113). `topology/044`'s reviewer additionally read commit `ad3f642`'s message to
confirm none of a prior unit's seven cuts was restored. Every `changelog.d/` fragment
consumed into its `history/<repo>.md` with `--only`; 29 of the owner's own fragments left
pending throughout.

### Blocked

**Nothing, across all 8 units.** No task went to `blocked` and no gate went red on a merge
result. Five tasks filed this day, all owner-required and none dispatchable:
`tasks/doc/059` (worktree-nesting defect, `ui/052`), `tasks/doc/060` (`DEF_HEAD` regex gap,
`outpost/022`), `tasks/doc/061` (stranded-branch false positive, `core/062`), `tasks/doc/062`
(open.md split-role gap, `ui/053`), and `tasks/api/097` (citation-sweep remainder, `api/095`,
**open** and dispatchable). `tasks/core/060` (compact `decisions/streams.md`) sat untouched
and `open` all day, deliberately not dispatched beside `core/061`/`core/062` — one task per
sub-project per slot.

### Reviewer

**Reviewer:** no findings — `ui/052`. Re-derived Core's log rotation from `main.rs` at the
real SHA, confirmed decision 7's decision itself is untouched by the diff, re-ran the
`size.cap` grep across both `embarch-ui` tips and the whole `embarch-doc` tree rather than
trusting the worker's, and traced the "missing" inbox drop to `tasks/core/062` rather than
reporting a lost finding.

**Reviewer:** no findings — `core/061`. Confirmed the flag is set from the declared
`StreamSource` inside `StreamStore::create` rather than derived from `bytes_written`, that
nothing in the diff or surrounding file branches on `note`, that the new test is non-vacuous
in both directions, and read `embarch-dev-bench` decision 24's body to confirm the code
comment is a faithful restatement rather than a stretch.

**Reviewer:** no findings — `api/096`. Read the three neighbouring doc comments clause by
clause, read `StreamRef`'s definition to confirm independently that `streams_json` cannot
surface the flag, showed the serde test fails both without `#[serde(default)]` and when the
field is never populated, and checked the field's spelling against `embarch-core`'s actual
merge SHA rather than the task file that pinned it.

**Reviewer:** 1 finding — `outpost/022`, `inbox/outpost-citation-sweep-missed-file-classes.md`.
A bare case-insensitive grep turned up 4 more citations in 3 file classes nobody's include
list scoped (`README.md` ×2, `cmake/outpost_build_id.h.in`,
`tests/native_sim_stream/app.overlay`); all four read against their decision bodies and are
correct — no defect behind the overstatement, but the third consecutive time this repo's
sweep scope claim outran its grep. **Accepted, verified by the supervisor, and acted on in
this fold** by correcting `history/outpost.md`'s scope line rather than filing a follow-up
sweep.

**Reviewer:** no findings — `core/062`. Checked all three things asked and gave evidence for
each: read the corrected `debug-tab.md` at `ui/052`'s own fold SHA rather than at this
unit's (catching and correcting a wrong SHA in the supervisor's spawn prompt), read
`src/main.rs`'s comment itself to confirm leaving it alone was the right call, and read
`embarch-core` decision 16's body plus all four reversal row files to confirm nothing
contradicts.

**Reviewer:** no findings — `topology/044`. Performed the hunk count
`DOC-COMPACTION-PASS.md` assigns to the reviewer rather than agreeing with the commit
message's own summary of itself: located both deleted hunks by line, showed both fall
outside the protected probe-selection bullet and the Shape consumer-call table, read
`ad3f642`'s message to confirm none of a prior unit's seven cuts was restored, and read
decision 29's body in `decisions/scope.md` to confirm the deleted parenthetical was
illustration, not the only statement of the rule.

**Reviewer:** no findings — `ui/053`. Did the word-level hunk count `DOC-COMPACTION-PASS.md`
assigns to the reviewer rather than reading the commit message's own summary: confirmed
exactly five deleted spans against exactly five quotes with no sixth, specifically checked
the one clause reworded rather than deleted, and read both cited decision bodies
independently rather than accepting the "already said elsewhere" justification.

**Reviewer:** no findings — `api/095`. Verified the relabel's *direction* against both
decision-59 bodies at the merge SHAs, reconciled every one of the diff's 8+8 lines against
the three claimed hunks with nothing riding along unreported, agreed the unsettled `(decisions
37, 38)` citation is genuinely unsettled after reading 37, 38 and 72 itself, and cross-checked
`097`'s "already verified" list against `095`'s own tally for under-description, finding them
identical.

### Hardware debts

**None created by any of the 8 units** — the day touched no board, no probe, no DUT, no live
Core route. The standing debts, carried in each unit's own words:

**Hardware debts:** **none.** Doc prose in one decision file; no board, no probe, no live Core, no
deploy, nothing built. — `ui/052`

**Hardware debts:** **one, and it is the first behavioural addition to it in a while.** `core/015`'s
outstanding **native Windows build** now carries a twelfth landed `embarch-core` change, and unlike
the comment sweeps and test recoveries of the last five days this one changes what the service
*serves*. Separately, decision 63's end state has never been seen on a real study: confirming that a
`PowerFrontEnd` tap reports `source_deferred: true` through a live Core needs the **dev-bench board**,
and `tasks/core/061` said so before it closed. No board, probe or live Core was touched here. —
`core/061`

**Hardware debts:** **none.** A deserialized struct field and a tool description string; no board, no
probe, no live Core, no deploy. The end-to-end confirmation this half participates in is recorded
against `core/061`, not here. — `api/096`

**Hardware debts:** **none created, and none of this leg's four units touched hardware at all.** Worth
stating for this unit in particular because it is the one firmware repo the leg entered: no board, no
flash, no DUT, no Zephyr build — `tests/run-all.sh` stops at its `WEST` guard by design on this
machine. `embarch-outpost`'s two hardware-gated tasks are untouched and still waiting on a board. —
`outpost/022`

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
consecutive leg; `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`). — `core/062`
(**this is the number to carry forward: 40 commits since `1c1224e`, re-derived, not incremented**)

**Hardware debts:** **none created.** Two sentence fragments deleted from a markdown file; nothing
built, nothing executed, no board, no probe, no live Core. Standing debts carried unchanged — see
the `core/062` entry above for the `core/015` Windows-build count, which was re-derived there (**40
commits since `1c1224e`**, not the ordinal the last five days had been incrementing). The dev-bench
probe is still unplugged and `tasks/api/059` stays **open**. — `topology/044`

**Hardware debts:** **none created.** Five clause-level edits in a markdown file; nothing built,
nothing executed, no board, no probe, no live Core, no UI launched. Standing debts carried
unchanged, including `embarch-ui`'s 18-record stale prefix, which still has never met a real stale
prefix. The dev-bench probe is still unplugged — checked live at this leg's top, `status` returned
`"probes": []` — so `tasks/api/059` stays **open** for the fifth consecutive leg. — `ui/053`

**Hardware debts:** **none created.** Eight lines of doc-comment text in a Rust source file; nothing
executed, no board, no probe, no live Core, no route called. `core/015`'s native Windows build is
untouched by this unit — `embarch-api`, not `embarch-core` — and see the `core/062` entry above for
the re-derived count (**40 commits since `1c1224e`**) that replaces the incrementing ordinal.
The dev-bench probe is still unplugged; `tasks/api/059` stays **open**. — `api/095`

**Carry forward: the dev-bench probe was unplugged for all 8 units across both legs**
(`status` → `"probes": []` at both leg tops), so `tasks/api/059` stays `open`, not
`blocked`, into its sixth consecutive leg. `fleet-hardware.py --refresh` still crashes
(`tasks/doc/041`).

### Budget

Leg 114 (`ui/052` → `outpost/022`): PROCEED throughout, weekly **82.4% → 84.6%** of a 90%
cap, resets in ~54–55h, wave 5 suggested and 4 used. Leg 115 (`core/062` → `api/095`):
PROCEED throughout, weekly **85.0% → 86.2%** of a 90% cap, resets in ~54h, wave 3 suggested
and 3 used.

### Least sure about

- **Letting `api/095`'s worker run ~12 more minutes after `fleet stop`.** The stop arrived
  at 00:55:44 mid-`topology/044`; the leg 115 supervisor deleted `.fleet/pump` immediately
  and did not dispatch anything further, but let the already-running `api/095` worker (five
  minutes into a twenty-minute run) finish with a wrap-up instruction rather than killing it.
  It produced three real fixes and a well-specified remainder, which argues for the choice —
  but the outcome is not the argument.
- **Pinning `source_deferred` unilaterally.** It unblocked two parallel halves that landed
  spelling it identically, but decision 63 left the name open on purpose, and a supervisor
  closing an open question in a task file is a decision that never gets a number or a
  review.
- **Deleting the reviewer's drop on `outpost/022` instead of filing a fourth sweep task.**
  Every citation it named checks out, but this is the third actor in a row to declare this
  repo's citation surface finished, and the previous two were wrong for the same reason each
  time.
- **The `open.md` squeeze-then-file cycle reading as success when it is really a repeating
  pattern nobody can act on.** Squeezed twice in four units for the same reason;
  `tasks/doc/062` is owner-required, so nothing in the fleet can act on it before a third
  squeeze arrives.
- **Handing the `core/062` reviewer the wrong doc SHA for a file another unit had changed.**
  It caught the error itself only because the file was obviously not this unit's; a reviewer
  handed a wrong SHA for a file the unit actually did touch has no such tell.
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
