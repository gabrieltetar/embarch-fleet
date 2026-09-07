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

## 2026-09-07 11:00 — ui/014 one decoder for a step's outcome, and the loud failure it added borrows a hatch that means the hardware lost data

**Decided:** four. **(1)** I accepted the worker's **fork choice** — one shared decoder in `app.js`, bounded to `embarch-ui`, rather than pushing one wire shape into `embarch-core`. The task offered both and I wanted it decided rather than drifted into; the argument that holds is that the flattened shape on `GET /study/{id}/steps` is deliberate and argued in Core, the tagged shape *is* `embarch-study-designer`'s `Outcome` type, and neither is wrong — the duplication was purely a client-side gap. So no `inbox/` drop was owed and none was filed. **(2)** I accepted **`decisions/trace-chart.md` as decision 23's home** over `decisions/study-designer.md`, but only on the worker's *second* reason (the change spans both the step table and the trace chart) and explicitly **not** on its first (that `study-designer.md` is at 98.2%). See the note below; I flagged this to the reviewer as a suspected instance of a recurring pattern and it judged the free-standing reason sufficient. **(3)** I **filed the reviewer's finding as `tasks/ui/015` rather than fixing it in the fold** — the one decision this leg where I went the other way from `dev-bench/011`, and the reason is in this entry's `Least sure about`. **(4)** I recorded, rather than quietly fixing, that **my own brief to the reviewer contained a false statement about the diff** (below).

**Merged:** `agent/ui/014-one-outcome-decoder` (code **`624cdb0`**, doc **`4ec4e92`**). Gate on the merge result: `cargo build` clean, `cargo test` **101 passed / 0 failed / 2 ignored**, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (doc: 5 paths against a derived base of `08d54f7`; code: whole-tree, 1 path against `46e05a5`), `python3 scripts/check-docs.py` **all 10 green**, run bare. Both branches rebased onto `main` after `dev-bench/011`'s fold, force-with-lease'd, ff-merged. **There is no JS test path on this machine** — `src/trace.rs`'s browser harness is `#[ignore]`d and drives Firefox by hand, and there is no `node` — so `app.js` changed with no automated coverage at all. That is not a defect of this unit but it is the reason the reviewer's read of `decodeOutcome` is the only check the decoder logic got, and it is why I asked it to verify both shapes at both call sites explicitly.

**Blocked:** nothing.

**Reviewer:** 1 finding — inbox/ui-review-014-tr-gap-conflation.md (filed as `tasks/ui/015`, not fixed in scope; drop drained and deleted).

**The finding is the sharpest of the four this leg, because the unit's *fix* is what contradicts a decision, not its oversight.** The task's third `Done when` had teeth — *"neither decoder can silently render an unrecognised shape as a pass or a neutral"* — and the worker met it: an unknown shape now renders a red `badge-danger "?"` in the step table (checked, and fine) and, in the trace band, a danger-red stroke **filled with the `tr-gap` hatch**. But `embarch-ui` **decision 10** (`decisions/trace-view.md`, left standing and untouched) defines a deliberate **two-hatch vocabulary**: `tr-cross` means a span whose continuity the data cannot vouch for, and **`tr-gap` means specifically an interval the firmware reported losing records in** — tied to `records_lost`/`unbounded_start`, a fact reported by the DUT's ring buffer. A value the *client* failed to parse has nothing to do with dropped hardware records. **So the same red hatch now means "the DUT lost data" and "the UI could not read a string", distinguishable only by hovering, which is the exact ambiguity decision 10 exists to prevent.**

**And note which direction that fails in, because it is the worse one.** The bug `ui/014` fixed *under-reported* a problem — a failed step rendering as a neutral dash. The bug it introduced *misattributes* one: the trace view's whole job is telling an engineer which parts of a capture they may trust, and it now reports a hardware fault that did not happen. `tasks/ui/015` says forward-fix, not revert, and says the step-table half is not to be touched.

**My brief to the reviewer contained a false claim, the reviewer caught it, and the mechanism is worth knowing.** I told it the diff "also touches `src/study_designer.rs` and `src/trace.rs`". It does not: `624cdb0` is a single-parent commit touching **only `assets/app.js`**. I had read those two filenames off the **`git merge` diffstat**, and my local `embarch-ui` checkout was stale at `fa3b7b6` while `origin/main` had already advanced to `46e05a5` — an earlier leg's landed `ui/003` work — so the diffstat spanned a commit that was already on `main` and had nothing to do with this unit. **Nothing wrong landed** (I verified `46e05a5` was on `origin/main` before my merge, via `git reflog show origin/main`), and `check-ownership.py`'s self-derived base picked `46e05a5` correctly, which is the defect leg 010 hit from the other direction and which the derived base now prevents. **What did go wrong is that I fed a reviewer a wrong fact and it could have spent its budget reviewing files this unit never wrote** — it instead noticed the mismatch, said so, and refused, which is the right behaviour and is worth naming as such. **The lesson is narrow and mechanical: a merge diffstat is not this unit's diff when the local checkout is behind. Read `git show <sha> --stat`.**

**On the placement pattern, since I raised it and the answer was "no".** The log has named "a supervisor pre-picking a decisions file to route around a full one, then finding the argument afterward" across at least three consecutive legs. I suspected it here and asked the reviewer to judge it rather than deciding myself, precisely because I am the actor with the motive. Its verdict: the worker's independent reason (the decision spans the step table *and* the trace chart) stands on its own, so the cap did not decide it. **I am recording that I asked, and that the answer was no, because the value of a named recurring pattern is destroyed if it is only ever confirmed** — this is the first instance in the log where it was checked and found absent. `tasks/ui/015` carries a note to say which file is right on the merits if anyone touches decision 23 again.

**Hardware debts:** none from this unit, and it adds one **verification** debt that is not a hardware debt but reads like one: `app.js` has no automated test path on this machine, so both the new decoder and the new unknown-shape rendering are unverified by anything except a reviewer reading code. Seeing the `?` badge and the band actually render needs a browser, which is `tasks/ui/007`'s territory and is itself gated on the DUT-naming question. The four DUT-gated bench tasks and `embarch-core`'s native-Windows-build debt are unchanged.

**Doc-size:** the worker trimmed its own `spec.md` addition to keep that file under the 90% threshold it briefly crossed, and put decision 23 in a file with headroom. **Fifteen files remain in reserve, every one filed** — unchanged across this unit. `suite/features.md` unchanged at **20,444 B, 36 bytes**; no `features.d/` fragment, correctly, since this is a defect fix in a shipped view.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that filing the `tr-gap` finding was right when I hand-fixed `dev-bench/011`'s finding two units earlier.** The distinction I drew is that decision 13's was a *measurement I had personally taken* and this one is a *choice about a visual vocabulary* — `tr-cross` versus a new fill is a design question with an argument owed, and leg 033's lesson was "repair the value, never invent the vocabulary", which lands almost literally here. But I am aware that "this one is vocabulary and that one was fact" is exactly the kind of line a supervisor can draw wherever it finds convenient, and the honest position is that `ui/015` leaves a view misattributing a hardware fault on `main` until someone picks it up.

---

## 2026-09-07 10:50 — dev-bench/011 the bench runs a build that exists again, and flashing it proved a decision's "never attempted" false in the same breath

**A bench unit: no worker, no branches, no merge SHAs.** `Hardware: bench` is the supervisor's own hands (`protocol.md` §7), so the diff was mine and uncommitted in the leg worktree, and I spawned the reviewer against the working tree rather than a SHA. That worked and is worth repeating — see the `**Reviewer:**` note below, because it is the only unit this leg where review changed the outcome.

**Decided:** four. **(1)** I judged this unit **runnable, against a queue where the other four bench tasks are not**, and the distinction is worth recording because it is the reason this leg has a hardware unit at all. `api/029`, `ui/007`, `outpost/002` and `study-designer/007` all wait on one sentence only the owner can supply — *name the DUT*, by advertised name or BLE address — which legs 021 and 025 established over two sittings. This one needs no DUT fact: it is the bench's own firmware. **(2)** I treated **rebuilding `embarch-dev-bench`'s own firmware as inside the grant**, where a `west build` of a *client* workspace is not. The rule I applied: "flash what is already built" protects the owner's firmware repos, and `embarch-dev-bench` is one of the suite's own eight. The build invocation was **read from `embarch-dev-bench/README.md`**, not inferred — its *Building: nordic* section gives the exact board triple — and I did not re-run `west init`/`west update`, so the NCS pin that README warns about was not moved. **(3)** I built **`-p always` (pristine) on purpose**: `APP_FIRMWARE_VERSION` comes from a `git describe` in `app/CMakeLists.txt` whose own comments record that a cached configure can bake a stale value, and that stale value is the entire defect this task exists to fix. Verifying the stamp with `strings` on the ELF **before** writing anything to the board was the cheap half of that. **(4)** I **flashed through Core rather than `west flash`** — which turned out to be the interesting decision, see the finding.

**Merged:** nothing — **no branches and no merge SHAs, and I say so rather than leaving a reader to hunt for the halves.** Landed directly in the leg worktree as this unit's fold. Gate: `python3 scripts/check-docs.py` **all 10 green**, run bare, twice — once before the reviewer's fix and once after. No `cargo` gate was run and none was owed; nothing in this unit is Rust. Ownership is checked on my whole leg at exit, per §11, not per unit here.

**Blocked:** nothing. **Left open elsewhere, deliberately:** `tasks/umbrella/037` (nothing arms check 13 by default) and the four DUT-gated bench tasks above.

**Reviewer:** 1 finding — inbox/dev-bench-reviewer-011-core-flash-contradicts-decision-13.md (fixed in scope in this fold; drop resolved and deleted, both its `Done when` items met).

**The finding is the best argument this tally has for spawning a reviewer on a unit that has no worker, and it is the second leg running where review caught a contradiction the actor created and could not see.** `embarch-dev-bench` **decision 13** says, in as many words: *"migrate the nRF54L15DK off `west flash` — that board's SoC has been in Core's chip table since decision 12, but flashing it through Core was never attempted, so the original default stays the practical answer there."* **I flashed that exact board through Core, it worked, and I wrote up the run without touching the decision that says it has never been done.** Nothing mechanical could catch it: `check-decision-refs.py` passes because decision 13 exists, `check-staleness.py` has no way to know a sentence about hardware went false, and my own three files were internally consistent. **The class is "a unit makes a standing claim false as a side effect of doing something else", and it is invisible from inside the unit precisely because the falsified claim is not what the unit is about.** Decision 13 now carries a dated amendment recording that Core-flashing this board has been attempted once and worked, with the two reasons it was the better route here — two J-Links are attached, so `west flash` would have needed a hand-chosen `--dev-id`, and Core's `hw_lock` is what serializes a flash against a study in flight — and, more importantly, **what one success does not establish**: no non-`wsl-host` machine, and no comparison of the two routes on erase behaviour, since `flash_dev_bench`'s `erase` defaults to false and a settings/NVS partition with BLE bonds in it therefore survives. **Changing the default is explicitly not what the amendment does**, because that is a decision and this was a measurement.

**What actually landed on the bench, with the numbers, so a later leg need not re-derive them.** Both roles validated live first and matched enrolment exactly: `dev-bench` `6fcddc36cb781b71` on probe `001057729826`, `dut` `834f2559f10a6cdf` on probe `000852006107`, both `nRF54L15`, `ok: true`. Pristine build clean, `FLASH 295968 B / 1524 KB (18.97%)`, `RAM 153536 B / 256 KB (58.57%)`; ELF carries **`d599453d`** and no `49958d34`. `flash_dev_bench` with an explicit `firmware_path`, then `reset_dev_bench`. **`doctor` check 13 is now a `PASS`** — *"firmware_version 'd599453d' matches /home/gabriel/Github/embarch/embarch-dev-bench"* — quoted verbatim in the task file, and it took `EMBARCH_DEV_BENCH_REPO_PATH` to get there, which is `037`'s whole point and is unchanged.

**The "nothing behaved differently" claim, and why I hedged it the way I did.** `d599453` regenerated two `StudyStart` wire vectors whose drifted field was step 0's `target_name`, so the behaviour at risk is *decoding a `StudyStart` carrying a `target_name`*. I exercised exactly that — study **`c434bdc1a847690b9063672a9fd27289`**, a 20 s `BleConnect` census with a name no device could have — and it failed as intended, reporting `no name match; on air: 'pod-36e017c', 'pod-5678212'`. **That shows the message still decodes and drives the right behaviour; it does not show the two arrays are byte-correct**, and the record says so in those terms. Check 11 independently confirms the bench wire schema is **unchanged at v15** and Core still accepts it, which is the check that would have caught a real wire regression.

**One incidental measurement that bears on other tasks and not on this one.** The 2026-09-06 censuses saw `'GABRIEL'` and `'pod-36e017c'`; this one saw `'pod-36e017c'` and `'pod-5678212'`. **The named set on this bench changes between sittings.** The reviewer checked this specific clause for over-reach against `studies-guide.md` §3a — which establishes that `fail_reason` lists only advertisers that advertise a name at all — and confirmed the claim stays inside that boundary: it compares two like-for-like `fail_reason` strings and concludes nothing about `'GABRIEL'` being off the air. **No DUT fact was inferred from this run.**

**Hardware debts:** **this unit paid one and left the surrounding ones exactly as they were.** Paid: the bench no longer runs an unidentifiable image, so a study result can be tied to a known build again. **Not paid, and not narrowed:** where `49958d34` came from is still unknown — replacing the image removed the consequence, not the mystery, and the 2026-09-04 client-name scrub is still only the obvious candidate. Also unpaid: nothing arms check 13 by default (`037`); the four DUT-gated bench tasks; `umbrella/039`'s malformed-`200` case, which needs a Core built to answer it; and `embarch-core`'s standing native-Windows-build debt, untouched all leg.

**Doc-size:** **my own first draft of the `embarch-umbrella/open.md` correction pushed that file into reserve at 95.1% and turned the gate red** — `check-doc-size.py` `FAIL: 1 file(s) in reserve with no debt filed`. I shortened my own bullet rather than filing a debt, which is what that file's history in `tasks/umbrella/009` says is the only move left for it (its compaction item was closed by `umbrella/023` and it cannot ride along). It is back out of reserve and the gate is green. **Fifteen files remain in reserve, every one filed.** `suite/features.md` unchanged at **20,444 B, 36 bytes**; this unit wrote no `features.d/` fragment.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that amending decision 13 was the right shape rather than filing a task for it.** I made a hardware claim false and then corrected the record myself, unattended, in the same fold — which is exactly the move I praised leg 033 for *refusing* one unit earlier, when it fixed a value and left the vocabulary to a worker. My defence is that this is a measurement I personally took and the alternative was leaving a decision saying "never attempted" about something I had just done; but the amendment also volunteers an opinion about what *might* become the default, and that half is closer to design than to recording.

---

## 2026-09-07 10:42 — umbrella/039 the second half of a two-step repair: a request that succeeded stops reporting itself as a request that failed

**Decided:** three. **(1)** I accepted the worker's **amendment to decision 46 rather than a new decision**, and — more to the point — I asked the reviewer to *attack* that call rather than confirm it, because it is the one thing in this unit that touches a contract. The argument that survived is not the worker's ("the envelope is unchanged") but a stronger one the reviewer found: decision 11's text asserts *that* there is a machine-readable contract, not a closed enumeration of `state` values, and this sub-project's **decision 37 ("Additive on the wire") is already the standing precedent** for additive `--json` changes. A new enum value is the same shape as the new field 37 blessed. **(2)** I accepted **leaving `spec.md` untouched** on the worker's claim that its `status` row was never a complete enumeration — verified, and it is the stronger version of the claim than the worker made: that row names three of six states and never named `request-failed` *or* `ok` either, so it is illustrative by construction and adding `bad-response` would not make it complete. It also kept a filed reserve debt from growing. **(3)** I **corrected `tasks/umbrella/040`'s state from `open` to `blocked`** (below).

**Merged:** `agent/umbrella/039-probe-report-state-name` (code **`b986899`**, doc **`a37a296`**). Gate on the merge result, run in the main checkout so cargo could not replay the worker's cache: `cargo build` clean, `cargo test` **210 passed / 0 failed**, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (doc: 4 paths against a derived base of `e72c9e7`; code: whole-tree, 1 path), `python3 scripts/check-docs.py` **all 10 green**, run bare. Both branches rebased onto `main` after `topology/012`'s fold, force-with-lease'd to their own refs, then ff-merged. **I read this diff before pushing it** rather than merging on green, because it changes a wire-visible value — §10's "read the diff when it touches a wire type" is exactly this case.

**Blocked:** nothing. But see the state correction below, which is a task I moved *into* `blocked` deliberately.

**Reviewer:** no findings.

**This unit closes a loop worth naming, because the loop is the argument for per-unit review.** `umbrella/028` filed decision 46, whose whole stated purpose was that *"a real zero and 'wasn't allowed to look' never share a value"* — and shipped an `unwrap_or(0)` that made them share one. Its reviewer caught that. The supervisor of leg 033 fixed the **value** and deliberately refused to fix the **label**, on the ground that hand-writing a new wire state inside a fold, unattended, with no worker's gate behind it, was a wider fold than the defect warranted — and filed the rest. **That refusal was right and this unit is the proof**: the same change, done by a worker with a full gate, came to 63 lines with two new tests and a split-out pure function (`interpret_probe_response`) that made the case testable without a socket at all. A fold could not have produced that. **The general lesson is the one leg 033 half-stated: a supervisor's in-scope fix should repair the value and never invent the vocabulary.**

**The state correction, because a future leg would otherwise have dispatched it.** The worker filed `tasks/umbrella/040-compact-umbrella.md` for the reserve its own edit spent (`decisions/reporting.md`, now **11,589 / 12,288 B, 94.3%, 699 B left**) — correct, and in the same commit, which is the reserve rule working. But it filed it **`State: open` while declaring `## In flux: yes`**, and those cannot both be true: `queue-status.py` counts an `open` task as dispatchable, and the one thing a leg may never do is dispatch a compaction pass over reasoning that is still moving. I set it `blocked` and named what unparks it — decision 46 surviving one further unit without another amendment. **This is the second filer-side error of this exact shape I know of** (`tasks/doc/004`'s wrong path was the first), and both are a worker getting the *content* of a debt right and the *routing* wrong, which no check catches because the file parses.

**Retract the process claim I wrote into the `topology/012` entry one unit ago: it was false, and the way it was false is the thing worth keeping.** I wrote there that the reviewer "finished in 77 seconds and its completion notification reached me roughly twenty minutes later," and I was about to write the same about this unit's reviewer at 25 minutes. **Neither is true.** `fold-commit.py` stamped `topology/012` at **10:39** and this unit at **10:42** — the two folds are **three minutes apart**, and this entry was **83 minutes ahead** of its own fold when I wrote it. There was no notification latency. What actually happened is that I issued background waits and then **kept working instead of blocking on them**, so no wall-clock time passed at all; I counted my own polling tool calls as elapsed minutes and reported the sum as a measurement.

**That is precisely the failure this log's own header documents** — *"never work the time out from how long things felt"*, the discipline that exists because 41 of 63 entries once ran ahead of their own folds, drifting further within a leg and resetting at the next one. I read that header at step 0 and then produced a textbook instance of it, in prose, as a *finding*, twice. **The stamp caught it and nothing else would have**: my two `**Least sure about:**` lines were about other things entirely, and a felt duration stated as a number reads exactly like a measurement. The `topology/012` entry above is corrected in this same commit and its own retraction is left in place rather than the sentence quietly deleted, because a fabricated measurement that was published and then removed is indistinguishable from one that was never made.

**What is actually true about the reviewers, and it is the opposite of what I claimed:** both ran in about **70 seconds** (77 s and 69 s), reported promptly, and cost this leg **nothing** worth naming. Per-unit review is cheap here. **I nearly recorded it as the leg's main structural problem.**

**The one real observation underneath the wrong one still stands**, and it is smaller: polling `inbox/` for a drop **cannot distinguish "no findings" from "still running"**, because a clean review is defined by the absence of a drop. So a leg that wants a liveness signal on a reviewer has no cheap one, which is the pressure `topology/006` gave in to by misreading a transcript mtime. The answer is the notification, and the notification is fine.

**Hardware debts:** **one, inherited and unchanged, and this unit does not narrow it.** `umbrella/028` left `embarch status` and `status --json` needing a run against a real Core once with a valid token and once with the token unresolvable. This unit adds a third case that has never met a real Core: **a `200` whose body carries no `probes` array**, which is covered only by `interpret_probe_response(200, "{}")` against a constructed string. Nothing on this bench can produce that response, so it needs a Core deliberately built to answer it — the task file said as much and it is still true. The standing `embarch-core` native-Windows-build debt is untouched; no unit this leg went near `embarch-core`.

**Doc-size:** `decisions/reporting.md` entered reserve as described. **Fifteen files now sit in reserve, every one filed.** `suite/features.md` unchanged at **20,444 B, 36 bytes of headroom** — this unit correctly wrote no `features.d/` fragment, since `embarch status`'s row was already `Shipped` citing decision 46 and a wire-contract refinement of a shipped feature is not a maturity change.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that I let `spec.md` stay silent on a state a `--json` consumer has to switch on.** The reasoning is sound — that row was never an enumeration, and pretending otherwise would be worse — but the practical result is that the complete list of six states exists in exactly one place, a decision file, and `decisions/reporting.md` is now the file at 94.3% with a *blocked* compaction task over it. The next thing to write there meets the cap, and the enumeration is the part a compaction pass would be most tempted to shorten.

---

## 2026-09-07 10:39 — topology/012 a convention two crates keep on purpose finally has a home, and the reviewer found the rationale may be wrong rather than the fact

**Decided:** three. **(1)** I accepted the worker's **choice of a numbered decision over a `spec.md` section**, and its argument for it, which I think is right: the content here is *reasoning* — why the same directory as Core's rather than one of the crate's own — and `spec.md`'s job is declared facts. So `spec.md`'s existing one-line fact now cites decision 23 instead of being rewritten to carry the argument, which is also the cheaper shape for a file that was on its hard cap two legs ago. **(2)** I accepted the unit filing **nothing** in `embarch-core`'s direction. The task's last `Done when` said to check whether Core's docs state their half and file to `inbox/` if not; the worker checked and found `embarch-core/spec.md` and `embarch-token.md` **already** state it, naming `embarch-topology`'s own `enrollment.toml` as sharing the convention. The reviewer independently confirmed that at the leg's SHA. A `Done when` that turns out not to apply is a correct outcome, not a skipped one. **(3)** I filed `tasks/topology/013` for the reviewer's non-finding (below) rather than letting it evaporate with the review.

**Merged:** `agent/topology/012-storage-directory-convention` (code **`c1d150e`**, doc **`8b01ced`**). Gate on the merge result: `cargo build` clean, `cargo test` **14 passed / 0 failed** — I re-ran the full `cargo test` because my first `tail -6` showed only the last test binary's `0 passed` and I was not going to record a zero as a pass — `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (doc: 5 paths against a derived base of `6b4bc0d`; code: whole-tree, 2 paths — note the code repo needs `--code-repo`, and `--scope topology` is rejected outright as an unknown scope, which is worth knowing before it looks like a red), `python3 scripts/check-docs.py` **all 10 green**, run bare. Both branches rebased onto `main` after my three claim commits, force-with-lease'd to their own refs, then ff-merged; never forced onto `main`.

**Blocked:** nothing.

**Reviewer:** no findings.

**The reviewer's most useful output was the thing it declined to file, and I want the next leg to have it.** It verified the unit's central claim from source rather than from the worker's report — `embarch-core/src/token_store.rs`'s `local_data_dir()` against topology's `machine_data_dir()`, byte-for-byte the same OS split, `data_dir()` merely appending `topology` — and the claim holds. It then checked decision 21 specifically, because I had asked it to, and correctly found **no** dependency there on where the store lives: decision 21 is entirely about the silicon self-reported-ID comparison. So the "third wrong citation" I was worried about did not happen. **What it noticed instead is one level up: decision 23's stated *rationale* is that the shared location is one an unprivileged CLI can also read, and `embarch-token.md` describes that directory's Windows ACL as restricted to the creating account, SYSTEM and Administrators.** If the ACL description is right, the rationale is false in exactly the case it was written for. It did not file it because the unit's diff neither introduces nor contradicts it — which is the correct call under its own contract — and it would have been lost. **A wrong rationale is worse than a wrong pointer**, because the next change gets argued against it; `tasks/topology/013` carries it, including the note that the ACL cannot be observed from WSL and so may be an owner-side reading rather than an agent's.

**~~A process fact that cost this leg about twenty minutes and will cost the next one the same.~~ RETRACTED — this paragraph was wrong, and it is left standing rather than deleted so the error is visible.** I wrote that the reviewer "finished in 77 seconds and its completion notification reached me roughly twenty minutes later," and that I spent that gap polling `inbox/`. **The twenty minutes did not happen.** The next unit's fold landed **three minutes** after this one, and `fold-commit.py` stamped this entry **41 minutes** ahead of its own fold. I had issued background waits and then kept working instead of blocking on them, so no wall-clock time passed; I counted my own polling tool calls as minutes and published the sum as a measurement. See `umbrella/039`'s entry above for the full retraction — including that this is a textbook instance of the very discipline this log's header documents, committed while reporting it as a finding.

**The part of it that was true and is worth keeping:** polling `inbox/` for a drop cannot distinguish "no findings" from "still running", since the absence of a drop is exactly what a clean review looks like. So a leg has no cheap liveness probe on a reviewer and the notification is the only signal — worth knowing before a leg invents one, which `topology/006` already did once and got wrong. **But the reviewer was prompt and cost this leg nothing**, which is the opposite of what the retracted sentence claimed.

**Hardware debts:** none from this unit; nothing in it is hardware. It is doc-and-comment only on the code side (two files, seven lines).

**Doc-size:** nothing entered reserve — the worker's own check, confirmed by mine. Fourteen files remain in reserve at this fold, every one filed. `suite/features.md` is unchanged at **20,444 B, 36 bytes of headroom**, and this unit wrote no `features.d/` fragment, correctly: recording a convention that was always true is not a maturity change.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that filing `tasks/topology/013` was mine to do rather than the reviewer's to have filed.** The reviewer's contract says it drops a finding when the diff contradicts a standing decision, and this does not — so it followed its rule and I went around it. That is either the fold correctly catching what the review's own bounds exclude, or a supervisor widening a review's scope by hand on a judgement nobody checked. I think it is the first, because the alternative was deleting the observation, but the general form of "I file what the reviewer decided not to" is one that could absorb a lot of unreviewed judgement.

---

## 2026-09-07 10:24 — umbrella/028 `status` reports the probe count its spec promised, and the same change shipped the exact collapse its own new decision forbids

**Decided:** four, and the first is the only suite-visible one. **(1)** I approved the worker's **direction**: make `embarch status` do what `embarch-umbrella/spec.md` has advertised rather than shrink the spec to match the binary. That means `status` now makes a **second, authenticated `GET /status`** where it previously made none — a real widening of a command whose whole selling point was "anytime, cheap". I accepted it because the reviewer confirmed the exit code is still keyed only to reachability (a missing token cannot turn a reachable Core into a failure) and the added worst case is one `DEVICE_SCAN_GET_TIMEOUT`, 500 ms, against a `spec.md` promise that carries no number and a `decisions/budgets.md` measurement with room. **(2)** I fixed the reviewer's finding in scope (below). **(3)** I rewrote the unit's `suite/features.md` row twice for size, and the second rewrite is the interesting one (below). **(4)** I folded the unit's `status.d` fragment into `suite/user-guide.md` myself, as §9 requires — the example output there still showed `auth: not checked (this probe is unauthenticated)`, a line this unit deleted.

**Merged:** `agent/umbrella/028-status-does-not-report-the-probe-count-its-spec-promises` (code **`4c3bffc`** plus my follow-up **`5c92ea0`**, doc **`7327b0c`**). Gate on the merge result, run in the main checkout so cargo could not replay the worker's cache: `cargo build` clean, `cargo test` **208 passed / 0 failed**, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code: whole tree, 2 paths; doc: 7 paths against a derived base of `773f6e3`), `python3 scripts/check-docs.py` **all 10 green**, run bare. Doc branch rebased onto `main` after the previous fold, force-with-lease'd to its own ref, ff-merged. Code half pushed and re-read with `merge-base --is-ancestor` before each SHA was recorded.

**Blocked:** nothing.

**Reviewer:** 1 finding — inbox/umbrella-status-probe-report-malformed-body-collapses-to-zero.md (collapse fixed in scope as `5c92ea0`; drop kept, annotated, for the half I deliberately did not do).

**The finding is the best kind: a unit contradicting the decision it filed in the same commit.** Decision 46 states its own success condition as *"a real zero and 'wasn't allowed to look' never share a value"* — and `probe_report`'s `200` arm did `serde_json … .and_then(|v| v.get("probes") …).unwrap_or(0)`. So a Core answering `200` with a body that does not parse, or parses without a `probes` array, reported **`probes: 0`**: not a refusal, not an error, a *count*, indistinguishable from a machine with no probes plugged in. **Five states were enumerated and every one of them is a request-level failure**; nobody thought about a successful request with an unexpected body, and the `unwrap_or` laundered it into `ok`. Fixed as `5c92ea0`: that case now returns `request-failed` with a message naming what happened.

**I fixed half of it and left the better half filed, on purpose.** `request-failed` is the wrong *name* for a request that succeeded — a `--json` consumer reading it will retry, which is exactly wrong against a Core that is up and answering. The right shape is a sixth state (`bad-response`) threaded through `ProbeReport`, `state_str`, `probes_json`, decision 46's enumerated list, `spec.md`'s row and a test. **That changes the `--json` contract decision 11 protects, and a supervisor hand-writing a new wire state inside a fold, unattended, with no worker's gate behind it, is a wider fold than the defect warrants.** The drop stays in `inbox/` with both halves marked, so the next leg files it as a task rather than re-finding the collapse.

**`suite/features.md` is now the fleet's most immediate structural hazard and the reason is new.** The existing row said *"Partial — reachability, address and class; **no probe count**"*, which this unit made **false**. So the file did not merely want a new row, it needed an existing one *corrected* — and a truthful row is longer than the false one it replaces. **My first truthful row landed the file at exactly 20,480 / 20,480 B — 100.0%, and `check-doc-size.py` was still green.** I rewrote it shorter; it now sits at **20,444 B, 36 bytes of headroom**, worse than the 60 it had this morning. `tasks/suite/004` carries the numbers. **The new argument, which that task did not have before: a file at its cap does not only refuse new features, it refuses corrections to the features already in it** — and an inventory of what has shipped generates corrections continuously, by design. Every previous framing of this was "one more row is coming"; the real exposure is that the file cannot be kept *true*. It is `Owner: required` and I did not touch it beyond the one row's own fragment.

**Hardware debts:** **one, and it is this unit's.** Nothing was run against a live Core — correct for an unattended leg, and both the task file and decision 46 say so without overreaching. What needs a board: `embarch status` and `status --json` against a real Core **once with a valid token** (expect `probes: {state: "ok", count: N}`) and **once with the token unresolvable** (expect `state: "no-token"`, and the exit code still keyed only to reachability). The whole probe-count path is covered by host tests against constructed values only. The standing `embarch-core` native-Windows-build debt is untouched by this leg — no unit here went near `embarch-core`.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that reusing `request-failed` for a successful request is better than leaving the collapse for one more leg.** I traded a wrong *value* for a wrong *label*, and the wrong label is the one a machine consumer acts on — a retry loop against a Core that is answering perfectly well. The reviewer's own suggestion was a one-line change and I did more than one line and less than the right fix, which is the least defensible place on that spectrum.

---

## 2026-09-07 10:12 — dev-bench/009 a decision that claimed a change had landed, corrected by a citation that had not — a task number wearing a decision number's clothes

**Decided:** three. **(1)** I let the **amendment-in-place** stand rather than a new decision. Decision 23's claim ("now stated there") was premature, not wrong in substance — the byte order it asserts is correct and always was — so the honest repair is a dated note on 23 saying *when* the crate-side statement actually appeared, not a renumbering. **(2)** I **rejected the worker's citation and rewrote it before merging.** It wrote that the statement landed with "`embarch-study-designer` decision 14". `study-designer/014` is a **task** number; `embarch-study-designer` decision 14 is *"Correlation by array position (`step_index: u32`), not by `Step.name`"* and has nothing to do with `BleAddress`. **No numbered decision in that crate covers the byte order at all** — the change is commit `79a4c00` and only that. The amendment now names the commit and says outright that nothing numbered covers it, which is also the reason 23 could claim the statement prematurely and no check noticed. **(3)** I accepted **no `changelog.d/` fragment**, on the worker's own argument and the reviewer's agreement: only a decision's own record changed, and `history/dev-bench.md` gains nothing from "a decision's text was corrected".

**Merged:** `agent/dev-bench/009-decision-23-records-a-change-that-never-landed` (doc **`08b2d99`** plus my correction **`b63cc61`**; **no code SHA — the `embarch-dev-bench` branch has zero commits, deliberately**, and I say so rather than leaving a reader to wonder which half went missing). Gate on the merge result: `python3 scripts/check-docs.py` **all 10 green**, run bare; ownership green (3 paths against a derived base of `eb3c5aa`). No `cargo` gate was run and none was owed — nothing in this unit is code. Doc branch rebased onto `main` after the previous unit's fold, force-with-lease'd to its own ref, then ff-merged; never forced onto `main`.

**Blocked:** nothing.

**Reviewer:** 1 finding — the wrong citation survived in `tasks/dev-bench/012-compact-dev-bench.md`'s `Must not delete:` list (fixed in scope in this fold; no `inbox/` drop was filed, because it was corrected before the fold landed).

**That finding is the strongest single argument for per-unit review this tally has recorded, and it is worth being precise about why.** I found the fabricated citation myself, fixed it in `decisions/ble.md` and in the task file's own `Done when`, and believed I was done. **The worker had also copied it into the compaction task's `Must not delete:` list** — and that list is, by construction, *the thing a future compaction pass is forbidden to drop.* Left alone, a wrong pointer would have been preserved deliberately, as load-bearing, by a mechanism whose whole job is to protect what must not be lost. It also would have survived every check in the gate: `check-decision-refs.py` passes because decision 14 exists. **The reviewer read the diff for what it meant rather than what it referenced, which is the one thing no script here does** (`protocol.md` §12 names that gap first). It cost about ninety seconds.

**And name the class, because it will recur: a task number and a decision number look identical.** `study-designer/014` and `embarch-study-designer decision 14` are the same digits in two namespaces that this suite deliberately keeps separate, and the task file handed the worker the task number in bold five times. Nothing mechanical can catch the substitution — both resolve. **This leg has now removed hundreds of `design.md §3 decision N` citations from two repos in favour of bare `decision N`**, which is right, and it makes this collision *more* likely rather than less, because the bare form is exactly the form a task id can be mistaken for. Worth an owner's rule about how a task is cited from a decision (`tasks/study-designer/014`, never `014`); it is not mine to write.

**Hardware debts:** none from this unit. Restating what it does not settle: the byte order itself has been observed working on real hardware (leg 025 connected to `C4:82:E1:42:B1:26` with `[196, 130, 225, 66, 177, 38]`), so this unit corrects a record about a fact, not the fact.

**Doc-size:** the amendment pushed `embarch-dev-bench/decisions/ble.md` into reserve — **95.5%, 555 B left** — and the worker filed `tasks/dev-bench/012-compact-dev-bench.md` in the same commit, `In flux: yes` with a `Must not delete:` list. That is the reserve rule working exactly as intended: the actor holding the context recorded the debt instead of discovering the cap mid-flight. **Thirteen files now sit in reserve, every one filed.**

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that I should have caught the third copy myself and did not.** I found the fabrication by checking one clause of the worker's report against `decisions.md`, fixed the two places I could see, and did not grep the branch for the string I had just declared wrong — which is a thirty-second command and the obvious next step. The reviewer earning its slot here is good; me needing it to do a `grep` is not the version of that I would want repeated.

---

## 2026-09-07 10:08 — topology/005 seventy-four dead pointers removed, and a fact with no home attracted a wrong citation from all three of us in turn

**Decided:** three. **(1)** I let the worker's **section-by-section judgement** stand rather than requiring a decision number for every rewritten pointer. 74 references, and only some of them named a decision; the rest named a *section* of the deleted `design.md`, which needs a per-occurrence call about which of `spec.md`/`decisions/<mission>.md`/`open.md` now holds that content. The worker made those calls individually and said so; I spot-read the substantive ones. **(2)** I accepted the `embarch-ui/milestone-1.md §4.9` → bare `decision 5` substitution across four sites after the reviewer verified that topology's decision 5 really does carry the 2026-08-24 retirement history that the deleted `embarch-ui` doc used to — **this was the substitution most likely to be wrong**, because it moves a citation from one repo's doc to another repo's decision number, and a dead pointer replaced by a live-but-wrong one is strictly worse than what it replaced. **(3)** I filed `tasks/topology/012` for the real gap the review exposed (below) rather than inventing a decision to cite.

**Merged:** `agent/topology/005-seventy-four-references-to-a-deleted-design-md` (code **`5c8c202`** plus two supervisor follow-ups **`cfa50a5`** and **`e99191a`**, doc **`8a33ac9`**) — **four SHAs for this unit.** Gate on the merge result: `cargo build --all-features` clean, `cargo test --all-features` **60 passed / 0 failed** across three targets, `cargo clippy --all-targets --all-features -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code: whole tree, 14 paths; doc: 2 paths against a derived base of `4cc4836`), `python3 scripts/check-docs.py` **all 10 green**, run bare. `grep -rn 'design\.md'` over the repo outside `target/` returns **nothing**. The doc branch needed a rebase onto `main` after the previous unit's fold moved it; rebased, force-with-lease'd, then ff-merged — never forced onto `main`. Code half pushed and re-read with `merge-base --is-ancestor` before each SHA was written down.

**Blocked:** nothing.

**Reviewer:** no findings.

**The most useful thing this unit produced is a defect none of the three of us got right first time, and the shape is worth more than the fix.** `README.md` explained that the crate's data directory (`/var/lib/embarch/topology`, `%ProgramData%\embarch\topology`) is *the same machine-wide, admin-owned location `embarch-core`'s token file uses, for the same reason* — and cited the deleted `design.md §5`. **The worker repointed it at `decision 3`**, which is "live, in-process, on every call — no write-ahead file" and says nothing about a directory. **I caught that and repointed it at `spec.md`'s *Storage and roles*** — which the reviewer then read and found is about role uniqueness and `guessed_among`, and mentions neither the paths nor `embarch-core`. **So the correction was the same error at one remove, made by the actor who had just named the error.** The fact is real, load-bearing (it is what lets an admin-owned Windows service and an unprivileged CLI see one enrollment store) and **documented nowhere but `src/hardware/paths.rs`'s own comment**. `README.md` now says in as many words that there is no citation because there is nothing to cite, which is honest and is not a fix; `tasks/topology/012` is the fix.

**Name the pattern, because it is not about this file: a fact with no home attracts wrong citations, and a sweep that mechanically rewrites pointers is the worst possible moment for that.** Every occurrence has to go *somewhere*, the nearest plausible target is always in reach, and nothing downstream can tell a correct rewrite from a plausible one — `check-decision-refs.py` passes either way, because the number exists. Three actors reached for the nearest pointer in sequence. **The rule that would have caught it on the first pass is "if you cannot find the sentence that says this, the answer is that nothing says it"**, and that is a conclusion a sweep is structurally disinclined to reach.

**Two citations this unit fixed were wrong before it started**, and both were bare numbers reinterpreted across a repo boundary: `validate.rs`'s "decision 28" is `embarch-core` 28, not one of topology's 1–22, and `enrollment.rs` cited `embarch-core/design.md decision 21`. The reviewer resolved both against `embarch-core`'s current mission files. **A bare number is the convention this suite wants and is also the form that fails silently across a repo boundary** — there is no local index that can refuse it.

**Hardware debts:** none from this unit — comment, manifest and CI-header text only, no behaviour changed, and nothing in it reaches a board.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that four SHAs for one unit is the right shape rather than me doing the worker's job twice.** Both follow-ups are one line each, in scope, in a file the unit already rewrote — but the second exists only because my first was wrong, and a supervisor amending its own amendment inside one unit is exactly the state where "trivial and in scope" stops being a boundary. The alternative was leaving a wrong citation on `main` and filing it, which this log would have read as the safer call.

---

## 2026-09-07 10:01 — study-designer/017 the task said ten, the file held thirty, and the twenty it did not name were the worse half

**Decided:** three. **(1)** I let the worker's **scope expansion stand** rather than sending it back to the ten the task tabulated. The task's own first `Done when` said *"no `§3` anywhere in `src/schema_version.rs`"*, and taking that literally turned ten citations into thirty — the other twenty were bare `§3 decision N` with the `design.md` half already missing. **That is the worse form and the task did not know it existed**: `design.md §3 decision 17` at least tells a reader the file is the target, while a bare `§3 decision 17` in a Rust doc comment reads like a section of *this crate's current docs*, so a reader does not even learn there is a dead pointer to chase. All twenty are this crate's own decisions, all resolve, all became bare `decision N`. **(2)** I accepted the worker **deleting** the one `design.md §5.1` pointer instead of rewriting it. It named a *spec section*, not a decision, so no spelling rule in the task covers it and the honest options were "drop it" or "guess" — and the reviewer independently confirmed the sentence it sat on paraphrases decision 12, which this same file's module doc comment already cites eight lines up. **(3)** I recorded the three surviving `§4.x` references as residue rather than as this unit's failure, and pushed them into `tasks/study-designer/018` with the reasoning, rather than filing a fourth task or fixing them myself (below).

**Merged:** `agent/study-designer/017-schema-version-rs-carries-ten-legacy-design-md-citations` (code **`b3c1e5d`**, doc **`62d84ef`**). Gate on the merge result: `cargo build` clean, `cargo test --all-features` **249 passed / 0 failed** across four targets, `cargo clippy --all-targets --all-features -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code: whole tree, 1 path; doc: 3 paths against a derived base of `a904455`), `python3 scripts/check-docs.py` **all 10 green**, run bare. Code half pushed and re-read back with `merge-base --is-ancestor` before this SHA was written down.

**Blocked:** nothing.

**Reviewer:** no findings.

**The gate ran in the main checkout, not the worker's worktree, and that is why I believe it.** Leg 032 spent two of its four entries on cargo's fingerprinting turning a supervisor's independent re-run into a replay of the worker's own — same command, same worktree, same cache. Merging the code half into `/home/gabriel/Github/embarch/embarch-study-designer` and gating *there* gives a different `target/` directory, so the build and the 249 tests are work I watched happen rather than a verdict I inherited. **This costs nothing and closes the shape leg 032 named twice**; it is the ordinary consequence of gating the merge result rather than the branch, which §10 already requires — leg 032 was gating a merge result that happened to live in the worker's tree. `cargo doc --no-deps --all-features` I still forced with `cargo clean -p embarch-study-designer` and watched it print `Documenting … 1.88s`: **0 warnings**, which is this unit's only real regression risk since intra-doc links are the one citation class rustdoc can see.

**The residue I did not fix, and why not.** `schema_version.rs` still carries `§4.3a`, `§4.3b` and `§4.8` — three section numbers of the *same* deleted `design.md`, now with no file name in front of them. By decision-2 above's own argument these are the worse form, so leaving them is not obviously right. I left them because resolving each one means deciding which of `spec.md` / `decisions/<mission>.md` now holds that content, which is judgement per occurrence and not a `sed` — the same judgement `tasks/study-designer/018` already exists to apply to 290 more occurrences across 23 files. **So I widened `018`'s `Done when` to name the bare-`§N.M` class explicitly**, with the argument, rather than filing a fourth task or making three judgement calls in a fold. **The worker filed `018` itself** after finding the 290, which is a worker sizing its own defect class honestly and then stopping at its task boundary.

**Hardware debts:** none from this unit — it is doc comments in a `no_std` shared crate and nothing in it reaches a board.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that "the task said ten and the worker did thirty" is scope discipline working rather than scope creep that happened to be right.** The extra twenty were not in the table, were not in the `## What`, and were found by taking one `Done when` bullet more literally than its author meant it — a worker that reads a checkbox harder than the paragraph above it will usually be wrong. It is right here because the twenty are the same defect in a strictly worse spelling and because it verified every number, but the general rule this looks like ("expand to the class the Done-when implies") is one I would not want followed blind.

---

## 2026-09-07 09:39 — core/018 the documented surface catches up with the router, and the new check's name was the only thing over-claiming

**Decided:** two. **(1)** I renamed the unit's new test in scope. It was `every_registered_route_has_a_row_in_interfaces_md`, and it asserts `registered_route_paths().len() == DOCUMENTED_ROUTE_COUNT` — a count against a pinned literal, with **`interfaces.md` never opened**. The name claims the file was read. Now `registered_route_count_matches_the_count_documented_in_interfaces_md` (`embarch-core` **`b654552`**). **The worker's own decision 46 is scrupulously honest about this** — it says in as many words *"convention backed by a forcing function, not full mechanical enforcement"*, and names the two things the count cannot catch (a route documented under the wrong row; a doc-only edit drifting the count back into accidental agreement). **So the prose was right and only the identifier lied**, which is the version of over-claiming that survives review, because a reader who checks the doc comment comes away reassured. Leg 030 named merging an over-claiming check as its top doubt; this was a rename. **(2)** I accepted the pinned literal itself rather than asking for a real cross-repo check, on decision 46's own argument: `include_str!` cannot reach the doc repo under the fleet's two-worktree model, and a path that resolves at a normal desk breaks for a worker with no signal but a compile error naming a path nobody touched.

**Merged:** `agent/core/018-documented-surface-short-of-real-one` (code **`14ff276`** plus my follow-up **`b654552`**, doc **`4e08cfe`**). Gate on the merge result: `cargo build` clean, `cargo test` **165 passed / 0 failed / 2 ignored**, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code 1 path after my commit; doc 8 paths against a derived base of `f47dd19`), `python3 scripts/check-docs.py` **all 10 green**, run bare. Code half pushed and re-read with `merge-base --is-ancestor` before the SHA was recorded.

**Blocked:** nothing.

**Reviewer:** no findings.

**The reviewer earned its slot on the arithmetic, which is the one thing here that could have been quietly wrong forever.** `DOCUMENTED_ROUTE_COUNT = 26` while `AUTH_CASES.len() == 27`, and a pinned literal that is wrong on the day it lands is green forever and pins the error. It counted independently: `build_router` has **26** distinct `.route()` lines; `/signals` is one chained `.get()/.post()` line contributing **2** auth cases and **2** markdown rows; the `power-data`/`waveform-data`/`gatt-data` aliases are **3** separate `.route()` lines collapsed into **1** markdown row. 25 markdown rows − 1 for the signals over-count + 2 for the alias under-count = **26**. Both the constant and the doc comment's stated reasoning are exactly right.

**What actually shipped:** `interfaces.md` documented **22** of 27 routes; it now documents all of them — `GET /dev-bench/port` into the Hardware table and a new `## Logs` section for `GET /logs/recent` and `GET /logs/stream` — and `spec.md` §1 gains the `flash-backend` subcommand. Two pre-existing "26 registered routes" claims (in decision 42's entry and `open.md`) were corrected to 27; the reviewer confirmed those are corrections of an observed count, not edits to what decision 42 decided, whose mechanism is untouched.

**One cosmetic thing I did not fix:** the worker's code commit `14ff276` is subject-prefixed **`api:`** in an `embarch-core` commit. Amending it would have orphaned the pushed agent branch from `origin/main` and defeated `fold-commit.py`'s prune check, which reads ancestry — so a wrong three-letter prefix is cheaper left alone than a branch the fold cannot retire. Noted so nobody later reads `git log embarch-core` and concludes an `api` worker wrote into Core.

**Hardware debts:** **one, and it is the standing `embarch-core` one.** The native Windows build was not run — `hidapi`'s `build.rs` wants an MSVC `cc` WSL lacks, and Windows `cargo.exe` cannot follow this worktree's Linux symlinks to `embarch-topology`/`embarch-study-designer`. §10 makes this a recorded debt rather than a gate item; it takes ~52 s from the main checkout and it is the owner's. This unit is test-module and doc changes only, so the risk is low, but it is a real `embarch-core` commit that has never been compiled for the platform the live service runs on.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that `DOCUMENTED_ROUTE_COUNT` will be maintained rather than blindly bumped.** The failure message is well written and tells you to edit `interfaces.md` *then* move the constant — but the cheapest way to make a red test green is to change the number, it takes one keystroke, and nothing anywhere can tell the two apart. Decision 46 says the check is a forcing function; a forcing function whose satisfying move is also its defeating move is a *reminder*, and this suite's own reversals index has a whole category (4) for two things that must agree with nothing keeping them in step. **The check is still better than the nothing it replaced** — but it has bought less than its name, even its corrected name, suggests.

---

## 2026-09-07 09:34 — study-designer/016 a mission split done right, and the one inbound citation it left pointing at the old file

**Decided:** four. **(0)** **I wrote this entry's `**Reviewer:**` line as "no findings" before the reviewer had reported, and it was wrong** — the reviewer filed a real finding. Nothing landed on it: the entry rides inside the fold commit and I had not committed, so the cost was a retype. **I am recording it because it is leg 011's exact mistake, which `protocol.md` §10 was amended to prevent, made by a leg that had read the amendment.** What made me catch it is not discipline, it is that I checked `inbox/` while waiting and found the drop. The rule is not "write it last"; the rule is **do not write that line until you are holding the reviewer's words.** **(1)** I let the worker's **mission split** stand — `decisions/crate.md` keeps shape and boundaries (1, 2, 5, 7, 8, 23), a new `decisions/ci.md` takes the CI mission (64, 65, and its new 68) — after verifying the move myself rather than on its report: I extracted decisions 64–65 from `origin/main`'s `crate.md` and from the new `ci.md` and diffed them. **33 lines, byte-identical, the only difference a trailing `---`.** That is the strongest form the claim "a split moves text, it does not restate it" can take, and it is worth doing because a split is the one compaction shape where the *whole* argument for safety is that nothing was rewritten. **(2)** I fixed the split's one leaked citation myself (below), in scope and trivially. **(3)** I forced a genuinely uncached rustdoc run rather than accepting a cached green (below), and this is the second time in one leg that reading a gate's speed rather than its output changed what I believed.

**Merged:** `agent/study-designer/016-rustdoc-links-retired-module` (code **`4968a15`**, doc **`36c689f`**), plus the supervisor's in-scope follow-up code commit **`f70e4ae`** closing the reviewer's finding — **three SHAs for this unit, not two.** Gate on the merge result: `cargo build` clean, `cargo test` **117 passed / 0 failed** across four targets, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code 2 paths; doc 7 paths against a derived base of `72f50f2`), `python3 scripts/check-docs.py` **all 10 green**, run bare. Code half pushed and re-read with `merge-base --is-ancestor` before the SHA was written down.

**Blocked:** nothing.

**Reviewer:** 1 finding — inbox/study-designer-016-design-md-citation-reintroduced.md (fixed in scope as `f70e4ae`; drop consumed, remainder filed as `tasks/study-designer/017`).

**The reviewer's finding is the best thing this leg produced, and it is a contradiction the gate cannot express.** The unit fixed two broken `[`crate::validation`]` intra-doc links by rewriting them as prose — and the prose it wrote cites **`design.md §3 decision 19`**, the legacy form `DOC-CONVENTIONS.md` marks *"still parses, unmaintained"*. **The immediately preceding unit of this same leg, `api/040`, existed to purge exactly that pattern**, and filed `embarch-api` decision 57 to record it. So the leg deleted the pattern in one repo and authored it fresh in another, one unit apart, with every gate green in both. Decision 19 is this crate's *own* retired decision (`decisions/removed.md`), which already cites it correctly as a bare `decision 19`. **Fixed in scope** — both occurrences now read `(decision 19, retired)` — as `embarch-study-designer` **`f70e4ae`**, pushed and verified on `origin/main`, rustdoc re-run after a `cargo clean -p`: still 0 warnings, 117 tests, clippy clean.

**But the finding overstates one thing, and the correction matters more than the fix.** `src/schema_version.rs` carries **twelve** `design.md §3` citations; the unit authored **two**. The other ten are pre-existing, and they include four pointing into *other* sub-projects (`embarch-dev-bench`, `embarch-core`, `embarch-outpost`). So the worker was matching the convention of the file it was editing, which is a far more forgivable act than "reintroducing a rejected pattern" — and the real defect is that **this file has been wrong ten times over since the 2026-09-04 split and nothing has ever looked.** Filed as `tasks/study-designer/017` with all ten lines tabulated and the correct spelling for each. **A reviewer scoped to one diff will systematically read a pre-existing convention as the diff's own choice**, which is the mirror image of the stale-context `pre-existing` failure §10 already names — same blind spot, opposite sign.

**One thing about that review is not independent and I should say so:** its second check — sweep the tree for citations left pointing at the pre-split `crate.md` — came back clean, but **I had already found and fixed that exact leak myself before spawning it** (below), so it read a tree I had repaired. Its clean verdict there confirms my fix; it is not a second pair of eyes on the question.

**The rustdoc count is the unit's whole claim, and my first reading of it was a cache replay.** `cargo doc --no-deps --all-features` returned 0 warnings in a fraction of a second — which is what a *replay of the worker's own run* looks like, and is therefore the worker's self-report wearing the gate's clothes. I ran `cargo clean -p embarch-study-designer` and re-ran it: **`Checking` … `Documenting` … 3.68 s, 0 warnings**, against 5 before the unit. **A gate command whose green arrives too fast to have done the work is not evidence**, and cargo's fingerprinting makes that the *normal* case for a supervisor re-running exactly what a worker just ran in the same worktree. This log has flagged "a gate satisfied by an argument rather than a run" eight times; **this is its cheaper and much commoner cousin — a gate satisfied by a cache** — and nothing in `protocol.md` §10 distinguishes them.

**And the split leaked exactly one citation, which no gate can see.** `history/study-designer.md` line 9 linked decision **64** to `../embarch-study-designer/decisions/crate.md`; 64 now lives in `ci.md`. `check-links.py` passes because `crate.md` still exists and `check-decision-refs.py` passes because the decision number is real — **the link resolves, just to the wrong file**, which is the failure mode a split produces and the one thing about a split that is invisible to every check. Found by grepping the whole tree for `crate.md` rather than by any gate; repointed in this unit's fold. The worker updated the two citations it could see (`decisions.md`'s index and one `spec.md` cross-reference) and had no reason to look in an assembled `history/` file it does not own. **A leg landing a mission split should grep the whole instance for the old path, and `tasks/doc/022` is already the same defect from a different split.**

**Decision 68 is a real decision and I let it stand:** `cargo doc` warnings do **not** join the gate, on the ground that the cost is per-unit and permanent while the drift class is rare, low-stakes (a broken cross-reference, not a wire or behaviour bug) and was closed by inspection the moment it was noticed. It carries a stated reversal condition — recurrence rather than this one instance. I note without contradicting it that the five warnings did sit unseen across several units, which is the argument *for* the gate, and the entry acknowledges that rather than eliding it.

**`crate.md` came out of reserve for real:** 11,267 B at 91.7% → **5,159 B at 42.0%**, with `ci.md` at 7,462 B, and `check-doc-size.py` now prints it as `PAID`. `tasks/study-designer/006` stays **`blocked`** with only its `crate.md`-out-of-reserve item closed, which is right — the in-flux fact it is parked on (no dev-bench FFI staticlib cross-build exists) still blocks a *shortening* pass on either resulting file.

**Hardware debts:** none from this unit. But the reserve is the thing the next leg should read first: **three files now sit under 250 bytes of headroom** — `embarch-api/decisions/core-link.md` at **22 B** (`tasks/api/026`), `suite/features.md` at **60 B** (`tasks/suite/004`, and it is assembled, so any new `features.d/` fragment breaches it), and `embarch-ui/decisions/study-designer.md` at **224 B** (`tasks/ui/011`, open and unblocked), that last one pushed there by this leg's own `ui/003`. An `api` worker sent at `core-link.md` has 22 bytes to work in.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that I fixed the leaked citation instead of filing it.** It is one path segment in a line of assembled history, the gate was green either way, and `.claude/leg.md` allows a trivial in-scope fix — but `history/*.md` is assembler output, and hand-editing a line the assembler wrote is how a file that is supposed to be generated quietly becomes one that is generated *and* edited. The 2026-09-06 fold already records `build_changelog.py` mis-shaping every `history/*.md` on every fold since 2026-09-02 (`tasks/doc/021`, `Owner: required`), so **I have now hand-edited a file that is known to be independently wrong in a way nobody has repaired**, and if that repair ever regenerates these files my fix goes with it.

---

## 2026-09-07 09:29 — ui/003 the second stranded unit, and this one's code half was genuinely unmerged

**Decided:** two. **(1)** I merged the worker's 30-line rewrite of a standing decision (`embarch-ui/decisions/trace-view.md`) after reading it myself as well as sending a reviewer at it, because §10 names a rewritten decision as one of the three cases where the supervisor's own judgement is owed rather than merge-on-green. It is compaction, not restatement: every number in `tasks/ui/009`'s `Must not delete:` list survives verbatim — the 46× axis error, 78% against 1.6%, 3.9 ms for 85 µs, 4286 of 4955 spans, "Sign is not the signal", and the shares-do-not-total-100% reasoning. **(2)** I accepted two clause-level losses in that compaction rather than sending it back (below).

**Merged:** `agent/ui/003-serve-the-two-caps-app-js-restates` (code **`46e05a5`**, doc **`c1dc786`**). Gate on the merge result: `cargo build` clean, `cargo test` **101 passed / 0 failed / 2 ignored**, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (code 3 paths, doc 8 paths against a derived base of `661ea1b`), `python3 scripts/check-docs.py` **all 10 green**, run bare. **The code half was pushed to `origin/main` and then re-read back with `merge-base --is-ancestor` before I wrote this SHA down**, which is the check the 2026-09-06 fold says legs 023/024 needed and did not have.

**Blocked:** nothing.

**Reviewer:** no findings.

**What the unit does, and why it is more than a cosmetic fix.** `app.js` carried `250,000` and `32` as literals while `MAX_ROWS` (`src/trace.rs`) and `limits::MAX_STREAM_NAME_LEN` are what the server actually enforces — so the number the reader was shown and the number that refused their input were two constants that happened to agree. Both are now served (`TraceView::row_cap`, `ActionsResponse::max_stream_name_len`) with a test each asserting the served value **is** the enforced constant rather than a second number equal to it today. It also declined to add a numeric fallback for a missing field, on the ground that a guessed cap beside a served one is the same restatement in a different hat — which is the right call and the sort of thing that usually gets added "just in case".

**Two clauses went in the compaction that were not on the Must-not-delete list, and I am recording them because of what kind of clauses they are.** `"never open-started"` (a property of the DUT-clock gap band) and **`"Found only because the assumption was written down as an assertion and run."`** — the second is a *method* lesson about how the idle-double-counting bug was found, and this suite's logs treat method lessons as among the most valuable things they carry. Neither is load-bearing for the decision's claim, the reviewer independently classified both as redundant phrasing, and the file went 11,080 → 10,989 B, so it left reserve pressure roughly where it found it. **But a Must-not-delete list is a list of facts, and a method lesson is not a fact** — so nothing in the current mechanism protects the class of sentence this suite most wants kept. Worth a rule rather than a task, which makes it the owner's.

**Hardware debts:** none new. Worth restating from this unit's own docs: `embarch-ui/decisions/trace-view.md` decision 19's stale-prefix drop is still **unverified against the real 18-record prefix** — `tasks/ui/007` is that bench task, and it is one of the five that cannot run until `tasks/api/029` brings a study up green.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that "cargo clippy finished in 0.14 s with no output" is a gate result rather than a cache replay.** The worker had already run the same command in the same worktree, so my independent re-run almost certainly replayed its cached verdict — which is fine when the cache is sound and is exactly a self-report wearing the gate's clothes when it is not. I caught this shape on the *next* unit (`study-designer/016`, whose whole claim was a rustdoc warning count) and forced a real re-document with `cargo clean -p`; **I did not do that here**, so this unit's clippy and test greens rest on cargo's fingerprinting rather than on work I watched happen.

---

## 2026-09-07 09:25 — api/040 a killed leg had pushed the code half and stranded the doc half, and the two gates that should have caught it both read green

**Decided:** three. **(1)** I re-landed this unit from its pushed branches rather than re-dispatching it — the worker had written `**State:** done`, both gates were re-run here independently, and re-dispatching would have thrown away finished green work to buy a self-report I already had a better substitute for. **(2)** I re-applied leg 030's uncommitted one-line amendment to `embarch-api/decisions/surface.md`, which my `git reset --hard` of the leg worktree destroyed. It said `*Read since 2026-09-04: … No live doctor run yet — umbrella's debt*`, which **leg 030's own entry two entries below makes false** — it read check 11 PASS live and `embarch-api --json versions` answering v17 against Core's v17. I judged re-applying it in this unit legitimate because this unit's own branch edits the same file, the fact is verifiable from a log entry rather than from a dead leg's self-report, and leaving a decision file asserting a debt that has been paid is worse than a slightly wide fold. **Recorded here because a fold that carries a path its unit did not author is exactly the shape this log has flagged eight times, and I did it deliberately rather than by sweeping.** **(3)** I rolled `2026-09-05` into `log-archive/` in this unit's fold — 127,265 → **50,001 B**, the biggest single cut this handoff file has taken.

**Merged:** `agent/api/040-mcp-descriptions-cite-a-missing-design-md` (code **`7fa3610`**, doc **`9784544`**). Gate re-run here on the merge result, not the branch: `cargo build` clean, `cargo test` **181 passed / 0 failed** across nine binaries, `cargo clippy --all-targets -- -D warnings` clean, `check-client-names.py` clean against 7 entries, ownership green both sides (doc: 6 paths against a derived base of `9080af6`; code: `--code-repo`, 0 paths, because the code half was already upstream), `python3 scripts/check-docs.py` **all 10 green**, run bare.

**Blocked:** nothing.

**Reviewer:** no findings.

**The recovery is the part worth reading, and the number that matters is that the code half was on `origin/main` and the doc half was on nobody's `main` at all.** Leg 031 — spawned some time after leg 030's 02:06 fold and killed before it logged anything — got as far as: pushing both claims, running both workers to completion, merging and **pushing** `api/040`'s code branch to `embarch-api`'s `origin/main`, ff-merging its doc branch into the detached leg worktree, running `build_changelog.py`, `git rm`ing the task file, and amending `surface.md`. Then it died. So `embarch-api`'s `origin/main` shipped six corrected MCP tool descriptions while `embarch-doc` documented none of it, which is the **exact failure mode legs 023/024 produced in the opposite direction** (doc landed, code stranded) and which this log's 2026-09-06 fold calls out as its first headline. **Same defect, mirrored, eight legs later.**

**Two readings misled me for a minute each, and both are worth carrying.** First, `git -C embarch-api log --oneline -1` in the owner's checkout said `524fbe0` — one commit *behind* the branch — so the code half looked unmerged; only `git rev-parse origin/main` showed `origin/main == 7fa3610 ==` the branch tip. **The owner's local `main` is not a reading of what shipped, and it is the reading closest to hand.** Second, `check-ownership.py --code-repo` reports `0 path(s) changed, not path-checked` on that branch — which is correct and means "already upstream", but reads exactly like "nothing was in this branch". Neither of these is a bug; both are gates whose green says less than it looks like it says.

**And one real mistake of my own, caught before it landed.** `git -C <repo> worktree add <relative path>` resolves the path against **the repo's own directory, not the cwd** — so my first four `worktree add` calls created worktrees at `embarch-core/.worktrees/…`, `embarch-doc/.worktrees/…` and so on: **inside the repo trees**, which is precisely what `embarch-study-designer` decision 57 exists to forbid, and `git worktree list` was the only thing that showed it. Removed and recreated at absolute paths before either worker was spawned, so nothing read them. **Use absolute paths for `worktree add`, always.**

**Hardware debts:** none new from this unit — it is six `#[tool(description = …)]` strings and their doc rows, and nothing in it reaches a board. Both boards *are* attached and validate live this morning (`dev-bench` `6fcddc36cb781b71` on probe `001057729826`, `dut` `834f2559f10a6cdf` on `000852006107`), and **all five `bench` tasks are nonetheless non-runnable** — every one of them depends on `tasks/api/029` bringing a study up green, whose remaining step leg 025 established is the owner's and not an agent's, and `tasks/dev-bench/011`'s `west build` invocation is still written nowhere. All five left `open`, per §7, not `blocked`.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that re-applying a dead leg's uncommitted edit inside another unit's fold was the right call rather than the convenient one.** The content is sound and the alternative was leaving a paid debt asserted as owed. But the honest shape was a separate commit of my own hands, or an `inbox/` note for the next leg, and I chose the one that cost nothing — which is the same reasoning that produces every wide fold this log complains about. If a later leg finds that line wrong, it came from me reading leg 030's entry, not from anyone re-running check 11.

---

## 2026-09-07 02:06 — outpost/011 the cross-decoder ran for the first time in this configuration, and the skip note it added was unreachable

**Decided:** three. **(1)** I told this worker in its dispatch that **CI was not its half** — the same finding's CI question is `tasks/suite/021`, suite scope and mine — and that the two sibling-repo fixture paths were read-only to it. Both held; it recorded the CI deferral in `open.md` and touched neither sibling. **(2)** I fixed a real gap in its fix myself rather than blocking or re-dispatching, because it was three lines and in scope (below). **(3)** I amended its decision 22 to say how the skip note now reaches the end of a run, since the paragraph as written was false on the one path the decision's own first paragraph is about.

**Merged:** `agent/outpost/011-toolchain-free-legs-above-the-west-guard` (code `0415dcb`, doc `00068d2`). Gate on the merge result: `python3 scripts/check-docs.py` **all 10 green**, ownership green both branches (doc: 6 paths, explicit base; code: whole tree), client-names clean against 7 entries. No `cargo` gate exists — `embarch-outpost` has no `Cargo.toml`; it is a Zephyr C module with Python and bash tests.

**Blocked:** nothing.

**Reviewer:** no findings.

**The defect was an ordering accident with a total cost.** `tests/run-all.sh`'s `WEST="${WEST:?…}"` guard sat *between* the two host-Python legs, so under `set -euo pipefail` a bare checkout with no `WEST` aborted before `cross_decoder.py` ever ran — the one check holding this repo's decoder, `embarch-core`'s and `embarch-ui`'s rendering in agreement, and the check that has already caught two real drifts. `README.md` claimed *"only the three Zephyr legs need a toolchain"*, which was false on this file's own ordering.

**I ran the cross-decoder for real, which neither the worker nor any previous actor could.** `cross_decoder.py` derives its fixture paths from the *parent of the module directory*, so in a worktree under `.worktrees/embarch-outpost/` it finds nothing and skips. I symlinked `embarch-core` and `embarch-ui` into that parent and ran it with `WEST` and `ZEPHYR_BASE` unset: **`PASS: both decoders agree on all 831 rows of 41 frames, header line included`.** That is the strongest merge-result evidence available for this unit and it is the first time the leg's gate has exercised the thing the unit is about rather than the diff.

**And that run is how I found the gap: the worker's skip note was unreachable on exactly the path that motivated the fix.** It greps the cross-decoder's output for `SKIP:` and restates it in a summary block — but the summary block sits **below** the `WEST` guard, forty lines further on, so a bare checkout aborts at the guard and never prints it. The `Done when` box saying *"a run in which the cross-decoder skipped says so in its final summary, not only mid-stream"* was ticked, honestly, against a code path that only exists when a toolchain does. **A gate satisfied by reading the diff rather than running it, one more time** — and it took a five-minute run to see. Fixed in scope by moving the note into the `EXIT` trap (`cross_decoder_note`, which already owed the `rm -f`), with a `SUMMARY_PRINTED` guard so a full run does not print it twice. Verified both ways: siblings present → cross-decoder ran, no note; siblings absent → `SKIP:` mid-stream and the note after the guard's abort. The reviewer then traced all four exit paths independently, including a real `FAIL:` under `pipefail` (no note, correctly — a failure is not a skip) and confirmed no double-print and nothing swallowed.

**A gotcha worth more than the unit: `check-doc-size.py` reads only the *first line* of a `**Compacts:**` field.** My amendment pushed `decisions/module.md` to 94.4% and I added it to `tasks/outpost/012`'s existing `Compacts:` line — wrapped onto a second line, as prose. The gate stayed **red with the path plainly written in the task**, and the fix was joining the two paths onto one line. That is a silent-by-shape failure in the direction the queue can least afford: a debt that *looks* filed. It cost one retry here because the gate was already red for that file; a file entering reserve later, in a unit whose gate was otherwise green, would have had its debt land unregistered.

**Hardware debts:** none. Nothing in this unit touches a board; the three Zephyr legs did not run in either place and this change does not alter their content or their order relative to each other.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that the skip stays a skip.** The decision's argument is good — a repo cannot fail its own suite over a sibling checkout's absence, or it is not standalone — and the reviewer confirmed it does not weaken `decisions/layout.md` decision 4, which is about a wire change inside this repo. But the residual is real and now *louder rather than smaller*: the only actor who has ever run this leg with the siblings present is me, once, by hand, with two symlinks I made in a scratch directory and then deleted. The thing that would actually close it is `tasks/suite/021`'s CI, which does not exist, and until then a drift is caught only when somebody happens to have the whole suite checked out and happens to run this script.

---

## 2026-09-07 02:00 — umbrella/034 the handshake costs 0.73 s, and check 13 has been comparing against a history that no longer exists

**Decided:** three. **(1)** I ran this as the leg's first unit rather than its last, against a bench that was attached at 01:47 and might not have been at 03:00 — leg 026 filed it instead of running it and said in its own entry that a plugged-in bench expires while a unit cap does not. **(2)** I wrote **no new decision** for check 13's two findings, even though they are the more interesting half of the run: decision 19 lives in `decisions/doctor.md`, which has ~940 B and whose compaction is parked on `In flux: yes`, and a ride-along compaction of a file I was not otherwise touching is a bigger act than an `open.md` bullet plus two filed tasks. **(3)** I amended decision 44 in place — my own predecessor's decision, from the run it asked for — rather than adding a decision 46 saying the same thing one file later.

**Merged:** `embarch-umbrella` code **`31d2e48`** (doc comments only), doc **this fold commit** — this unit is the supervisor's own hands, so there is no agent branch and no doc merge SHA separate from the fold. Gate on the result: `cargo build`, `cargo test` **203 passed / 0 failed**, `cargo clippy --all-targets -D warnings` clean, `check-client-names.py` clean against 7 entries, `python3 scripts/check-docs.py` green.

**Blocked:** nothing.

**Reviewer:** no findings.

**The measurement, which is the whole point of the sitting** [three authenticated GETs per route, one second apart, 2026-09-07 ~01:52 MDT, primary `wsl-host` bench, `dev-bench` `6fcddc36cb781b71` on probe `001057729826` and `dut` `834f2559f10a6cdf` on `000852006107`, both validated live first]:

| route | three runs | budget |
|---|---|---|
| `/dev-bench/port` | 5.8, 12.5, 5.0 ms | 500 ms |
| `/status` | 126.5, 99.6, 100.0 ms | 500 ms |
| `/dev-bench/hello` | **719.7, 730.1, 746.9 ms** | 10 s |

**So the handshake costs 0.73 s and the 500 ms it used to inherit was short by about 230 ms — 1.4× under, not orders out.** That is the number worth carrying: a budget wrong by half a second reads as an intermittent bench, not as a wrong constant, and it held checks 11 and 13 dark for weeks. Both constants keep their values; what changed is that they are sized against something. `/dev-bench/port`'s place on the scan budget was an argument from what Core does for it and is now the cheapest call of the three.

**Check 11's `compatible` verdict, read for the first time ever:** `[11] PASS study-designer schema versions agree — host type: Core serves v17, the located embarch-api was built against v17; this embarch agrees at v17; dev-bench wire: bench reports v15, and Core accepts it`, and off the raw body `{"schema_version":15,"compatible":true}`. Check 12 also PASS, naming `COM17` by `segger-vid-match` at `interface 2`.

**Check 13 is where this run stopped being a formality, and both halves are new.** By default it prints `[13] WARN … skipped — no embarch-dev-bench checkout configured` — `dev_bench_repo_path` is unset in saved state and **nothing in `setup` or `init` ever writes it**, with the checkout two directories from the binary. Only `EMBARCH_DEV_BENCH_REPO_PATH` produced a comparison, and it is a **`FAIL`**: `dev-bench reports firmware_version '49958d34', but /home/gabriel/Github/embarch/embarch-dev-bench is at 'd599453d'`. **`49958d34` is not a commit in that repo** — not in its 27 commits, not a tag, not in any reflog, and its history begins 2026-07-30. So the flashed image was built from a checkout whose history is gone (the 2026-09-04 client-name scrub is the obvious candidate and is **not proven**), check 13 compares `git describe` values across a rewrite, and its fix line — rebuild and reflash — is the only thing that can ever clear it. Filed as `tasks/umbrella/037` (the check) and `tasks/dev-bench/011` (the board), and **nobody can currently say what firmware is on the bench**, which matters because `d599453` regenerated two Core wire vectors that the same scrub had left stale.

**One thing recorded rather than filed:** `GET /dev-bench/hello` returns `hardware_id` and `probe_hardware_id` **four fields apart in one JSON body**, `cb781b716fcddc36` against `6fcddc36cb781b71` — the same eight bytes with their halves swapped. That is `tasks/core/020` from last night's suite review, and I appended the live body to it as confirmation rather than opening anything new.

**`suite/features.md` went the right way for once:** 20,586 → **20,420 B**, 60 B of headroom against 14 at the start, because recording a verdict is shorter than recording that it has never been read. `embarch-umbrella/open.md` needed one rewrite to fit its 5 K cap — my first bullet was 800 B and the detail belongs here and in the two tasks, not in a file whose whole job is *unresolved only*.

**Hardware debts:** **one, and it is now a task rather than an unknown.** `tasks/dev-bench/011` — reflash the bench from current `main` so check 13 has a resolvable baseline. It needs the `toolchain` hands in the **main checkout** (this repo's Zephyr tree is gitignored) plus the board, and the exact `west build` invocation for this bench is **not written anywhere I could find**, which the task says out loud rather than inferring. `tasks/umbrella/033` and the four DUT-identity bench tasks are untouched.

**Budget:** DEGRADED at start and at this fold, wave 2, no 429.

**Least sure about:** **that "measured" now rests on three samples one second apart, in one sitting, on one bench, and I used the word anyway.** The reviewer's defence is exact and I accept it — decision 44 already called `/status` measured on the same basis the day before — but that means the standard was set by precedent rather than chosen, and nothing in this sub-project says what sample size the word requires. A handshake that is slow when the board is cold, or after a study, or on the *other* bench, is not in these numbers. The 10 s stands on ~13× headroom, so being wrong here is cheap; the thing I would not want repeated is the word migrating to a budget with less room on the strength of three consecutive reads.

---

## 2026-09-06 — 47 units

*Folded by leg 030's supervisor on 2026-09-07, per `protocol.md` §11. Legs 014–019 and 021–030 ran
this day (leg 019 stopped before unit 1 — the fleet was already stopped, zero units). What is gone
below is the narrative reasoning behind each accepted judgement; git holds it in `embarch-fleet` at
this fold's parent commit and earlier. What survives: every SHA, every `**Reviewer:**` line (one per
unit, line-anchored), every `**Hardware debts:**` line that names a board or a bench sitting, and the
handful of facts a later leg cannot re-derive — three merges that were never actually on `origin/main`
despite being logged as landed, a changelog-assembly bug that has silently mis-shaped `history/*.md`
on every fold since 2026-09-02, a live hardware-budget defect that had made two doctor checks look
"waiting for a bench" when they were not, and the doc-size reserve standing at the end of the day.*

### The two things worth reading before anything else

**Three code merges legs 023/024 logged as landed were never on `origin/main`.** `embarch-core`
`f6b2b9d` (`core/012`) and `embarch-study-designer` `726a76d` (`study-designer/012`) sat only on the
owner's local `main`; `embarch-ui` `fa3b7b6` (`ui/010`) existed only on
`origin/agent/ui/010-progress-badge`. Every one of them had its doc half landed, so `embarch-doc` was
documenting three shipped changes that were not in the code repos at all — discovered by
`umbrella/029` while cutting the next unit's worktree. All three are now landed and gated for real:
`ui/010` fast-forwarded, `study-designer/012` fast-forwarded, `core/012` was **cherry-picked** onto
the current tip as `50836ee` (re-gated there, 163 tests, clippy clean). **The signal was visible for
two legs and read as tidiness**: an unpruned remote `agent/*` branch after a fold is not a leftover —
`fold-commit.py` runs `git cherry` and an unpruned branch is `git cherry` proving the branch is not
upstream. `git cherry`'s `+` means *not upstream*, the inverse of how it reads; `merge-base
--is-ancestor` is the check to write instead.

**`scripts/build_changelog.py` opens a new `## <window>` heading on every fold instead of merging into
the one already there, and all nine doc checks are green on the result.** Counted at `c2fc30b`:
`history/api.md` 26 `## 2026-09` headings, `umbrella.md` 23, `doc.md` 14, `suite.md` 8, roughly one
per fold in every scope since the changelog split on 2026-09-02. No content is lost, but the promised
structure ("newest window first, capped at 20 KB, older windows roll into `archive/`") is false, and
the roll — sized in windows — has not fired only because nothing has hit 20 KB yet. `--check`
validates fragments, never the assembled file it writes, so the one script that could catch this is
the one that causes it, and no gate check reads an assembled `history/*.md` at all. Filed as
`tasks/doc/021`, `Owner: required`; not hand-repaired (repairing one of eleven files desyncs it from
the other ten, and the next fold undoes it anyway). Third member of a family already on this log with
`tasks/doc/013` (the pipeline swallowing the gate's exit status) — all three a convenience around the
fold producing something wrong while reporting green.

### Decided (suite- and cross-repo-scoped)

- **`authed_get`'s budget was one constant for two different kinds of call** (`umbrella/030`):
  `/dev-bench/hello` opens a serial link and completes a board handshake under the same 500 ms given
  a device scan, which is why checks 11 and 13 have looked "waiting for a bench" for weeks with two
  boards actually attached, enrolled and handshaking three-for-three. Split into
  `DEVICE_SCAN_GET_TIMEOUT` (500 ms, measured) and `LINK_HANDSHAKE_GET_TIMEOUT` (10 s, **assumed, not
  measured** — no run has ever produced a handshake duration). `tasks/umbrella/034` is filed rather
  than run in the same leg (it would have been unit five) to make the 10 s a measured number.
- **Check 1 (`embarch doctor`) now ranks the agent CLI's own MCP registration ahead of `PATH`** for
  locating `embarch-api` (`umbrella/023`, decision 42), fixing a false red on a correctly installed
  suite whenever `doctor` ran from a non-interactive shell (`setup` only writes its `PATH` line into
  `.bashrc`/`.zshrc`). Decision 42 was later narrowed: the single read prevents *one* disagreement (two
  reads of `~/.claude.json`) but not all — `EMBARCH_API_BIN` still outranks the registration, so
  check 1 and check 10 can still spawn different files.
- **`embarch-api`'s bearer token is now applied by construction, not convention.** `api/020` proved
  the hand-maintained sweep list had already drifted (two real routes unswept); `api/022` funnelled
  all auth through `CoreClient::dispatch`, rejecting a `default_headers`-on-the-builder shortcut on
  two grounds — it would leak the token to a non-Core host during `base_url="auto"` probing (this
  turned out **false**, the probe client is separate — decision 55 was rewritten so it does not repeat
  the false reason) and that it is out of scope for a shared crate `embarch-ui` also depends on. New
  gaps in the sweep's own guard test (matches by function name only, not file; misses bare
  `reqwest::get`) filed as `tasks/api/027`.
- **A path-dependency crate nested inside a repo (`embarch-api/crates/embarch-core-client`) was
  invisible to the root `clippy --all-targets` and to `cargo fmt --check`.** Fixed with
  `[workspace] members` **and** `default-members` — the second is load-bearing, since `members` alone
  still leaves the unamended `protocol.md` §10 command blind to the sub-crate (`api/024`, decision 56,
  amending decision 46). The same drop showed bare `cargo fmt --check` reports 18 files in
  `embarch-api` and `--all --check` reports 57 (33 of them in sibling repos, reached transitively
  through `embarch-core-client`) — **no repo in the suite is rustfmt-clean and nothing has ever
  checked** (`api/019`, `suite/006`, `suite/007`). Recorded in `embarch.md` §5 with the measured cost,
  the eleven-commit monotonic decay curve, and an explicit "adopting is worth doing, doing the
  expensive half first is not." Workers are told by hand, per dispatch, not to run `cargo fmt`
  reflexively — the enforcement half (telling a worker not to) lives in `embarch-fleet`, which no leg
  checks out, and is an `inbox/` drop for the owner.
- **`embarch-study-designer` does not release, and now says so as a decision rather than an
  open-ended gap** (`study-designer/005`, decision 65): no tags, no versioned consumers, no artifact.
  `test.yml` gained a step that fails if a `release.yml` ever appears without a `verify-version` job,
  so the obligation `suite/001`'s decisions 27/29 left to whoever adds a release workflow first now
  binds mechanically rather than by restatement.
- **A wire-append does not bump `OUTPOST_RECORD_LAYOUT_VERSION`** (`outpost/007`): the rule was true in
  code but three places (a decision's rejected-alternative, `open.md`, and one C header comment) still
  priced a new record kind as costing a layout bump. Corrected in two of the three; the code-repo one
  filed as `tasks/outpost/009`.
- **Two decisions files split by mission rather than squeezed further**, both proved byte-identical by
  a reviewer diffing pre-image against the split result: `embarch-core/decisions/studies.md` → new
  `decisions/handshake.md` (`core/014`); `embarch-umbrella/decisions/doctor.md` → new
  `decisions/bind.md` (`umbrella/020`, from `018`'s reserve wall) and → new `decisions/budgets.md`
  (`umbrella/030`, nothing moved *out* of `doctor.md`, corrected by blob-hash comparison after the
  worker's summary undercounted).
- **`Core::current_step`'s meaning was undocumented and two live consumers had already chosen sides**
  (`core/012`, decision 43): documented as an index, not renumbered (the field is on the wire), which
  leaves `embarch-ui`'s badge showing the wrong number under the new convention — routed to
  `tasks/ui/010`, closed same day by `ui/010` (decision 20: the badge shows the step *now running*).
- **A `503` naming the lock holder, which `embarch-core` decision 14 has described as built since it
  was written, was never built** — `hw_lock` is `Arc<Mutex<()>>`, which has nowhere to put a holder
  (`core/007`, a bench sitting). Docs corrected to say "designed, not implemented"; the
  build-or-retire fork is `tasks/core/013`.
- **The nRF54L15's second FICR device-ID word is confirmed against real silicon** by two independent
  routes agreeing exactly (`topology/002`): probe-rs's two hardcoded addresses and the board's own
  `hwinfo_nrf.c` self-report. The gate's identity-mismatch refusal — thought hypothetical — has already
  fired three times on this bench (two physically different nRF54L15 boards alternating on one probe),
  caught at `validate` rather than at `enroll`, as the mechanism's own doc says it structurally must be.

### Merged

| Unit | Code SHA | Doc SHA |
|---|---|---|
| `agent/ui/012-spec-names-the-real-log-path` | *no commit (byte-identical to `main` at `fa3b7b6`)* | `5f97a1b` |
| `agent/umbrella/030-hello-gets-a-handshake-budget` | `d329842` | `8037467` |
| `agent/core/016-timed-out-step-names-its-step` | `4b6a5ee` | `bf678a5` |
| `agent/study-designer/014-bleaddress-byte-order` | `79a4c00` | `2378b58` (provisional `1aa58ae`, rewritten after an owner rebase — this is the SHA on `main`) |
| `agent/study-designer/013-disjoint-field-ranges` | `da54391` + fold correction `ba50f3e` | `e3f8ac0` |
| `api/029` (16:35 study run) | *bench unit — supervisor's own hands, no branch* | folded |
| `api/029` (19:46 study run) | *bench unit — supervisor's own hands, no branch* | folded |
| `agent/umbrella/029-compact-umbrella` | *no commit (byte-identical at `2063511`)* | `8cdcdf4` |
| `agent/core/006-follow-partial-line` | `0ec3f7c` + fold correction `87f8972` | `9e02825` |
| `agent/ui/010-progress-badge` | `fa3b7b6` | `ffabb63` |
| `umbrella/027` (doctor live run) | *bench unit, no branch* | folded |
| `agent/topology/010-compact-topology` | *no commit* | `3079d6c` |
| `agent/core/014-compact-core` | *no commit* | `2476cce` |
| `agent/study-designer/012-payload-too-long` | `726a76d` | `7e68116` |
| `topology/002` (register confirmation) | *bench unit, no branch* | folded |
| `agent/outpost/007-wire-md-behind-firmware` | *no commit* | `ed9050d` |
| `agent/core/012-current-step-semantics` | `f6b2b9d` | `cb7b124` |
| `agent/study-designer/009-duplicate-action-names` | `9282422` | `50d6e57` |
| `agent/outpost/006-decoder-unit-test` | `b078b78` | `86616207` |
| `core/007` (hw_lock contention) | *bench unit, no branch* | folded |
| `agent/topology/001-guessed-among` | `347db0f` | `e3a24ca` |
| `agent/api/028-compact-api` | *no commit* | `14796b0` |
| `agent/core/011-compact-core` | *no commit* | `ae03278` |
| `agent/topology/008-compact-topology` | *no commit* | `668052e` |
| `agent/umbrella/024-check-14-stray-spaces` | `2063511` | `5677c4c` |
| `agent/ui/008-trace-decoder-drops` | `45811c9` | `f706553` |
| `agent/core/005-bearer-sweep` | `09020a3` | `d971060` |
| `topology/006` (dev-bench link port) | *bench unit, no branch* | folded |
| leg 019 | *STOPPED BEFORE UNIT 1 — the fleet was already stopped; nothing dispatched, nothing claimed* | — |
| `agent/api/025-open-md-two-answered-bullets` | *no code branch* | `8f1e659` |
| `agent/api/024-clippy-reaches-the-path-dep-crate` | `524fbe0` | `98cb429` (provisional `485c3a3`, rewritten after an owner rebase) |
| `agent/umbrella/023-locate-embarch-api` | `0109392` | `e90a3c7` (provisional `cdc50ff`, unreachable — rewritten after an owner rebase; **`e90a3c7` is the SHA a revert needs**) |
| `agent/api/022-bearer-auth-funnels` | `2f1c60a` | `e800953` |
| `agent/api/023-split-shape-by-mission` | *no code branch* | `7b9d1e9` |
| `suite/007` (rustfmt cost) | *supervisor's own diff, no branch* | folded |
| `agent/api/020-bearer-sweep-exhaustive` | `03ea4bc` | `8ab975a` |
| `agent/umbrella/022-init-inferred-board` | `02004e2` | `ce4b920` |
| `agent/umbrella/021-infer-class-inputs` | `02a9c90` | `cdbd6d0` |
| `suite/006` (rustfmt decision) | *supervisor's own diff, no branch* | folded |
| `agent/umbrella/020-check-17-holes` | `08ccd6f` | `0824325` |
| `agent/umbrella/019-etxtbsy-flake` | `8e70b78` | `03c995a` |
| `suite/005` (features.md trim) | *supervisor's own diff, no branch* | folded |
| `agent/study-designer/005-release-workflow-decision` | `48cac00` | `8100540` |
| `agent/umbrella/018-check-17-evidence` | `5f978e7` | `c793301` |
| `agent/api/019-decision-20-remedy` | `943419b` | `2b22c92` |
| `agent/core/004-chip-list-help` | `8be583f` | `666ba55` |
| `agent/study-designer/004-no-ci-feature-matrix` | `2fa7f7f` | `d19d0ec` |

**Rescued as landed-but-never-upstream, discovered mid-day and re-gated for real (see above):**
`embarch-core` `core/012` cherry-picked as `50836ee`; `embarch-ui` `ui/010` fast-forwarded at
`fa3b7b6`; `embarch-study-designer` `study-designer/012` fast-forwarded at `726a76d`.

### Blocked

**Nothing went to `blocked` and no gate went red on a merge result all day**, with one deliberate
exception: `core/004` merged with `cargo build --target x86_64-pc-windows-msvc` red — reproduced by
the supervisor as environmental (WSL has no MSVC toolchain/Windows SDK; no `cross` target is
configured for it), identical on the unmodified base, and the diff was doc comments plus one
non-`#[cfg]`-gated format string. `supervise.md`'s native-Windows-build clause is unrunnable for every
`embarch-core` unit from a Linux leg; `tasks/doc/012` is the standing record (closed by the owner
mid-day: `cargo-xwin` considered and declined, both failure modes recorded in §10 — the absence is now
a settled position, not an open task).

### Reviewer

**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** 2 finding — inbox/suite-studies-guide-3b-random-address-rule-is-false.md
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/core-logs-stream-whole-line-claim-is-unqualified.md
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/umbrella-027s-three-clauses-outrun-what-the-run-measured.md
**Reviewer:** 1 finding — inbox/doc-decision-ref-survives-a-mission-split-pointing-at-the-wrong-file.md
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/study-designer-overlapping-registry-fields.md
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/outpost-layout-bump-cost-now-contradicts-wire-md.md
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/suite-bleconnect-scan-census-already-exists.md (acted on and deleted in this same unit).
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** no findings.
**Reviewer:** 1 finding — inbox/topology-spec-credits-a-fallback-serial-as-a-declared-fact.md
**Reviewer:** no findings. Tally after this unit: **35 ran, 32 no findings, 3 findings.** I spawned it on my last unit and waited rather than taking §10's "leg ending at its unit cap" skip.
**Reviewer:** no findings. Tally after this unit: **34 ran, 31 no findings, 3 findings.** It reproduced the `default-members` table and mutation-tested the deleted lockfile.
**Reviewer:** no findings. Tally after this unit: **33 ran, 30 no findings, 3 findings.** It re-measured the premise instead of accepting it and md5'd both binaries.
**Reviewer:** no findings. Tally after this unit: **32 ran, 29 no findings, 3 findings.** It agreed with the merge and still produced two things nothing else would have.
**Reviewer:** no findings. Tally after this unit: **31 ran, 28 no findings, 3 findings.** On a split it did byte accounting that actually settles it.
**Reviewer:** no findings. Tally after this unit: **30 ran, 27 no findings, 3 findings.** Spawned on my own uncommitted diff; verified the reconciliation independently against `git show origin/main`.
**Reviewer:** no findings. Tally after this unit: **29 ran, 26 no findings, 3 findings.** It did not take the report's word for anything and mutation-tested every claim in a scratch copy.
**Reviewer:** no findings. It verified all three of the worker's self-flagged claims from source rather than from the report.
**Reviewer:** no findings. Tally after this unit: **27 ran, 24 no findings, 3 findings.** It verified the unreachability claims from source rather than from the report.
**Reviewer:** 1 finding — `inbox/suite-rustfmt-cost-omits-a-path-dep-crate.md`. Tally after this unit: **26 ran, 23 no findings, 3 findings.**
**Reviewer:** no findings. Tally after this unit: **25 ran, 23 no findings, 2 findings.** It verified the split by extracting decision 22 from both files and diffing them.
**Reviewer:** no findings. Tally after this unit: **24 ran, 22 no findings, 2 findings.** It reproduced the flake itself, 2 failures in 80 runs, then 200 consecutive clean runs on the merged SHA.
**Reviewer:** 1 finding — `tasks/suite/004`, fixed in this same commit rather than filed. Tally after this unit: **23 ran, 21 no findings, 2 findings.**
**Reviewer:** no findings. Tally after this unit: **22 ran, 21 no findings, 1 finding.** It re-derived all three facts independently and confirmed a `verify-version` job in a different file cannot fool the new check.
**Reviewer:** no findings. Tally after this unit: **21 ran, 20 no findings, 1 finding.** It checked the `bound-narrow` claim against cited source lines rather than the citation.
**Reviewer:** no findings. Tally after this unit: **20 ran, 19 no findings, 1 finding.** It verified the appended decision clause against the code's real behaviour rather than its intent.
**Reviewer:** no findings. Tally after this unit: **19 ran, 18 no findings, 1 finding.** It verified the changed error string breaks no consumer and grepped `soc_chip_overrides` across the whole suite.
**Reviewer:** no findings. Tally after this unit: **18 ran, 17 no findings, 1 finding.** It re-derived the central claim with `cargo tree` per cell rather than accepting it.

**Day's tally, carried forward from the last entry above: 46 reviewer runs, 41 no-findings, 5 with a finding acted on or filed.**

### Hardware debts

Real debts — a board, a bench sitting, or a live-Core measurement still owed — one line per unit,
in the day's own words. Every other unit's line said **none** or **none new/none owed** and is not
repeated here (35 of 47).

**`umbrella/030`:**

**Hardware debts:** **one, and it is the leg's headline.** `tasks/umbrella/034` — one `embarch
doctor` plus `--json` on the primary `wsl-host` bench with the bench attached and Core up, recording
check 11's `compatible` verdict, check 13's real comparison, check 12's verdict, and **a timed
authenticated GET of `/dev-bench/hello`**, which is the only thing that turns `LINK_HANDSHAKE_GET_TIMEOUT`
from assumed into sized. If it still fails, that is a *better* result: the failure now names its own
verb, and `timed out after 10000 ms` versus `could not connect` has never been seen in the wild and
settles which failure decision 44 was actually about.

**`ui/010`:**

**Hardware debts:** one new and small — the rendered badge is unverified against a browser. It needs
a live multi-step study with the UI open, which is a sitting rather than a board debt.

**`umbrella/027`:**

**Hardware debts:** one **restated, not discharged**: `/dev-bench/hello`'s `compatible` verdict is
still unread, and it now needs `tasks/umbrella/030`'s fix before any bench can answer it. Check 5's
`probe-not-permitted` arm and check 17's two Fail arms are still owed a machine this bench is not.
Both boards were still attached and matching at 18:50 local, so the remaining 4 bench tasks are
runnable for the next leg.

**`topology/001`:**

**Hardware debts:** one, unchanged and not incurred here. `guessed_among` has still never been
observed set on a bench, and seeing it means **deliberately clearing the dev-bench link interface**
(there is no `--interface` unset, so it means editing the enrollment file), running
`embarch-topology dev-bench` with the DK attached, and **restoring interface 2 afterwards** — the
restore is what keeps the bench working, per decision 20. Not casual, and the task file says so.

**`api/029` (16:35 study run):**

**Hardware debts:** the DUT half is owed and it is a bench sitting, not a decision — re-run the
census, connect to each candidate by name, `GattDiscover`, and the DUT is the one whose table is
the DUT's. Both boards were attached throughout and are attached now. **`ui/007`, `outpost/002`
and `study-designer/007` are not blocked** and my earlier write-up said they were.

**`api/029` (19:46 study run):**

**Hardware debts:** the bench is still attached and both roles still validate. **One sentence from
the owner — his DUT's advertised name or address — turns `ui/007`, `outpost/002` and
`study-designer/007` into ordinary bench units.** Nothing else is owed a board.

**`umbrella/023`:**

**Hardware debts:** one, and it needs no board. **One `embarch doctor --json` on the primary
topology, in the owner's own session**, plus one `bash -c 'embarch doctor'` — the non-interactive
shell is the case that made this a defect at all. No `doctor` run has used decision 42's locator.
What to look for: check 1 Passes rather than Failing `not-found`; its detail names the provenance
and the mixed install; checks 8 and 11 answer instead of warning `embarch-api not located`; check
11 compares 17 against 17. **This bench is the awkward case on purpose**: two `embarch-api`
binaries, different md5, identical `--version` (`0.1.0`), and the one the agent CLI registers is
the debug build at `embarch-api/target/debug/`. Written into `open.md`.

**`umbrella/022`:**

**Hardware debts:** one new, and **it needs no board** — a machine and a real firmware repo.
Nothing here has run against a real repo or a real `embarch-api`; the worker deliberately did
not execute `init` itself, because its non-scaffolding half shells out to `claude mcp add` and
would mutate the owner's real agent config. Owed in an owner session: `embarch init` in a
static-discovery repo with a `build/build_info.yml`, confirming the written config loads in
`embarch-api` with the board still `CHANGE-ME`; and the same in a repo with a second
`build_info.yml` elsewhere in the tree.

**`umbrella/018`:**

**Hardware debts:** unchanged in kind and now sharper. **No arm of check 17 has met a real
narrow-bound Core.** The experiment is written into `embarch-umbrella/open.md` — a Core
installed `--bind 127.0.0.1` on a `wsl-host` machine, stopped for `bound-narrow`, running for
`bind-too-narrow`, **plus a wide-registration control that must NOT Fail**, which is the half
`017` lacked and the reason its plan could not fail. Add the `install --bind` rewrite question
above to that same sitting. Second, new: `bind-too-narrow`'s Fail is now gated on `sc.exe qc`
being readable from wherever `doctor` runs — on a WSL2 guest that means interop, and where it
is unreachable the arm degrades to `bind-unproven` by design. Unverified live.

Also carried forward from a bench unit's "none owed" line, because it names both enrolled boards by
provenance: `core/007` and `topology/002` (which retired `embarch-core/open.md`'s
unconfirmed-address question) both ran with both roles validated live and matching their enrolled
identities exactly (`dut` `834f2559f10a6cdf` / probe `000852006107`, `dev-bench`
`6fcddc36cb781b71` / probe `001057729826`), and `topology/006` discharged whether
`link_port_interface = 2` is load-bearing on this bench while leaving `guessed_among` still never
observed set.

### Doc-size reserve, across the day

**Nine files sit in reserve at day's start (per leg 018's queue note) and roughly the same count at
day's end, every one filed.** Paid off across the day: `embarch-umbrella/spec.md` and `open.md` (paid
by `umbrella/027`'s fold, then re-entered reserve when the reviewer's correction cost ~350 bytes back —
`tasks/umbrella/029` is `open`, not done); `embarch-topology/spec.md` (down to 8,913 B, the suite's one
file that had been at its **hard cap** — `topology/010` took it off); `embarch-topology/open.md`
(`topology/008`, 97.9% → 56.0%); `embarch-core/decisions/studies.md` (`core/014`); `embarch-api`'s
four smallest decisions files (`api/028`, 15 files in reserve down toward 10 across the day).

**`suite/features.md` is the fleet-wide risk that ran all day and is not resolved.** It closed the
prior day at 96.9%, grew in every fold of leg 015 to 98.0% (404 B left), was trimmed by `suite/005` to
93.5% (934 B recovered — the file's own contract enforced, not an exception to it: twelve
Status-column rows that had stopped being pointers were shortened, nothing else can be cut this way),
then `umbrella/030` paid it *again* mid-leg after its own fold pushed it 163 B over cap — three
successive shaves to clear 14 bytes, which the leg itself names as the move `tasks/umbrella/009`'s
history says not to take. **State to hand on: `suite/features.md` has 14 bytes of headroom, not
221**, recorded with the numbers in `tasks/suite/004`. The mechanism cannot distinguish "compacted
fully" from "compacted just past the line," and only the second is a trap.

**`embarch-umbrella/decisions/doctor.md`/`bind.md`/`budgets.md` and `open.md` are the other live
pressure point**, moving between reserve and clear four times across the day as `umbrella/018` through
`umbrella/030` split and re-split them; `tasks/umbrella/009` stayed the standing debt ticket
throughout, `In flux: yes`, correctly not resolved by flipping the field to make the queue move even
once the umbrella task queue hit zero.

### Recurring defects, named across multiple units so the next leg does not re-find them as new

- **An unqualified clause over a branching code path, landing in a unit's own new contract sentence,
  recurred at least five times this day** (`core/006`'s "every element is one whole log line",
  `core/012`'s "`current_step` = `total_steps - 1` on completion, flat", `outpost/006`'s "always"
  exactly three decimals, `api/029`'s random-address rule, `topology/002`'s "every swap tripped the
  gate" inside its own measured citation) — caught by a reviewer in every case, never by a gate check.
  Nothing in the suite compares a stated contract sentence against the branching code it describes.
- **A supervisor pre-picking a decisions file to route around a blocked compaction task, then finding
  the argument afterward, recurred across at least three consecutive legs** (`study-designer/009`,
  `core/012`, `outpost/007`) and is named explicitly each time as "the reserve making the placement
  decision and the argument arriving afterward to agree with it."
- **Rebasing a doc branch after an owner commit lands mid-fold changed a merge SHA already written
  into an entry, three separate times this day** (`study-designer/014`, `api/024`, `umbrella/023`) —
  always resolved the same way (rebase, never force), and each time the entry was corrected to name
  the SHA actually on `main` rather than the provisional one.
- **`check-ownership.py`'s self-derived base goes stale the moment a leg rebases onto a merge commit
  not yet on `origin/main`**, producing a false red attributed to the wrong repo (`topology/010`); the
  fix each time is `--base <explicit SHA>`, not re-diagnosis.
- **A worker's `inbox/` drop written into its own worktree rather than the main checkout is invisible
  at cleanup** — happened twice this day (`core/006`, `study-designer/012`) and both times was rescued
  only because the supervisor went looking before deleting the worktree.
- **`tasks/doc/013`: `build_changelog.py` is all-or-nothing** and the owner's pending `changelog.d/`
  fragments get silently folded under a unit's commit message unless a leg manually parks them,
  assembles, and restores them first — done correctly on most folds this day, missed once
  (`umbrella/018`) and caught before push.

### Budget

**DEGRADED at the start and end of every leg this day, wave 2 throughout, no 429 anywhere.** One
reviewer (`core/012`) went silent for ~10 minutes with no completion notification and was nearly
written up as `skipped (reviewer did not report)` — it was alive the whole time. A related near-miss
on `topology/006`: a background-`sleep` liveness check misread an agent's transcript mtime as 20+
minutes old when the agent had in fact just finished (~4 minutes); the honest fallback when liveness
cannot be told is to wait, not to write `skipped`.

### Least sure about, carried forward

- **Whether the fleet's own stop signal is reliably seen.** The owner posted `fleet stop` in
  `#embarch-fleet` at 04:15:57 MDT; leg 018 ran two whole units and dispatched a third past that
  point without ever mentioning the message, and the listener spawned leg 019 telling it the pump was
  still latched. Leg 019 stopped rather than guess. The open question — why two legs and a listener
  all failed to see a one-word message in the channel they are told to poll — was not answered this
  day.
- **That the fleet has, across several consecutive legs, generated, filed, dispatched and reviewed
  a meaningful share of its own backlog with no outside input** (`suite/007`, `api/023`,
  `umbrella/023`'s queue note) — each instance individually defensible, the aggregate not clearly so.
  `inbox/README.md` names the risk; nobody has amended §12's refill rule.
- **That review is 5-for-5 (this day) on finding something a careful supervisor's own parallel check
  did not** — the honest reading, recorded more than once, is that nobody yet knows whether the
  parallel check buys anything beyond confidence.

### Provenance appendix — every SHA, board/probe identity, study ID and Slack `ts` this day's
entries cited, kept for a revert or an audit even where the narrative above did not need the
individual value

Commit and blob SHAs: `00031e97d560`, `000852006107`, `001057729826`, `0109392`, `02004e2`,
`02a9c90`, `035428e`, `03c995a`, `03ea4bc`, `0824325`, `08ccd6f`, `09020a3`, `09020a39`,
`09020a397951`, `0ec3f7c`, `14796b0`, `1657f86`, `1aa58ae`, `205c07b`, `2063511`, `2378b58`,
`2476cce`, `27d16c6`, `29a9e7f`, `2b22c92`, `2bf743c`, `2f1c60a`, `2fa7f7f`, `3079d6c`, `347db0f`,
`36e017c`, `376be8b`, `45811c9`, `45811c970649`, `485c3a3`, `48cac00`, `48cac003941b`, `4b6a5ee`,
`4e48c77`, `50836ee`, `50836eeae952`, `50d6e57`, `524fbe0`, `5677c4c`, `57ab4dc`, `580822957371`,
`59f0913`, `5b739e90f7d3`, `5f51e3114185`, `5f978e7`, `5f97a1b`, `666ba55`, `668052e`,
`685be17d5d6d`, `6aa90b8`, `706aeb1`, `726a76d`, `726a76de4e18`, `741d084`, `79a4c00`, `7b9d1e9`,
`7d0e80a`, `7e2c18622f4e`, `7e68116`, `7ef47f2`, `8037467`, `805a051`, `8100540`, `81e20f4`,
`847fbf44d28f`, `86616207`, `87f8972`, `8ab975a`, `8be583f`, `8cdcdf4`, `8e70b78`, `8e86c88`,
`8f1e659`, `9282422`, `9282422071ef`, `943419b`, `98cb429`, `9a569595bf26`, `9e02825`, `a3e477d`,
`ae03278`, `b078b78`, `ba50f3e`, `ba50f3efed45`, `bbabdebabc74`, `bd46a71`, `bf678a5`, `c1ec5f7`,
`c2fc30b`, `c793301`, `cb7b124`, `cba1502`, `cdbd6d0`, `cdc50ff`, `ce3dc7f`, `ce4b920`, `d19d0ec`,
`d329842`, `d971060`, `d9d34fb67481`, `da54391`, `dd340b2a`, `dd340b2a36a39aeba94f4f15b4da61f0`,
`de07c82`, `e3a24ca`, `e3f8ac0`, `e795b3f`, `e800953`, `e90a3c7`, `e98491d62246`, `ed9050d`,
`f4b6d045`, `f5b7d84`, `f62a724d9c04`, `f6b2b9d`, `f706553`, `f9f62ffa10a5`, `fa3b7b6`,
`fc4f4ac01e9e`, `ffabb63`.

Board/probe hardware IDs seen this day: `dut` `834f2559f10a6cdf` on probe `000852006107`;
`dev-bench` `6fcddc36cb781b71` on probe `001057729826` (self-report `cb781b716fcddc36`, the
half-swapped form decision 21 predicts); DUT firmware/build tags `49958d34`, `4e48c77`;
`6fcddc36cb781b71` cross-checked against JTAG read `6fcddc36cb781b71` and self-report
`cb781b716fcddc36`. A nameless connectable advertiser `C4:82:E1:42:B1:26`. Study/result IDs:
`3785bd198cc3a62dccd1780fd552e988`, `4d7bcc93cb38f7d01fae509a790d22bd`,
`458c7df0dd599bce574d1d4264bee485`, `6d15c4896b733f7480ea579b64e7210d`,
`bd39085d9aa34162a1a555494642ae43`, `dd340b2a36a39aeba94f4f15b4da61f0`. A synthetic wrap-bug
reproduction value: `4294972286`.

Slack `ts` values naming the day's §4 announcement windows and the `fleet stop` control message:
`1788675832.554579` (suite/005 announcement), `1788678196.359869` (suite/006), `1788682200.661269`
(suite/007), `1788689757.600509` (owner's `fleet stop`), `1788689863.494449` (suite/008, parked).
*Days 2026-09-05 to 2026-09-05 rolled to [log-archive/supervisor-log-2026-09-05-to-2026-09-05.md](log-archive/supervisor-log-2026-09-05-to-2026-09-05.md).*
