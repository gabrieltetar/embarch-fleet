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

## 2026-09-06 02:20 — suite/006 no-repo-in-this-suite-is-rustfmt-clean-and-nothing-checks

**Leg 016's third unit, and mine under §8.** Announced at `ts 1788678196.359869` (01:03 MDT),
parked, thread re-read at every unit boundary, run at 02:05 after a window that closed at 01:33
with **zero replies**. Fourth time §4's window has been served rather than restarted.

**Decided:** **the suite does not enforce `rustfmt` and nobody runs `cargo fmt`** — recorded in
`embarch.md` §5 with the measured cost and a reversal condition, and as a deferred item in
`suite/roadmap.md`'s **Later**. `embarch-dev-workflow.md` is the more natural home and is
owner-reserved, so §5 is the only reachable one; the register objection is real and is below.

**The announced reason was wrong and I changed it, which is the part of this unit worth
reading.** The `#embarch-fleet` announcement said reformatting would put `git blame` on a
mechanical commit "in a suite whose entire review surface is *why* a line reads the way it is."
On measuring I judged that weaker than I had claimed — **this suite's review surface is its
`decisions/` docs, deliberately, not `git blame`** — and moved the decision onto **sequencing**:
the check that keeps formatting true lives in `protocol.md` §10 and is the owner's, so
formatting first decays immediately. Same action, better reason. I asked the reviewer directly
whether I had rationalised my way back to the outcome I had already announced. **It said no, and
gave a reason neither version of mine states: the `git blame` objection has a standard cheap
answer, `.git-blame-ignore-revs`, while nothing similarly cheap answers decay.**

**Merged:** none — this unit has no branches. It is the supervisor's own diff on the leg
worktree, landed in its fold commit.

**Blocked:** none.

**Reviewer:** 1 finding — `inbox/suite-rustfmt-cost-omits-a-path-dep-crate.md`. Tally after this
unit: **26 ran, 23 no findings, 3 findings.** Spawned on my own uncommitted diff, and it found
something no other actor in this design would have:

- **`cargo fmt --check` does not descend into local path-dependency crates.** It never sees
  `embarch-api/crates/embarch-core-client`, which is not a workspace member — **6 files, 42
  hunks, 66 lines.** Corrected totals **87 files / 1,288 hunks / 1,947 lines**, and `embarch-api`
  becomes 24 files, tying `embarch-study-designer` for largest, so my "largest first" clause was
  wrong too. **The 3.5% on the total is not why this matters**: my reversal condition named
  `cargo fmt --check` by name, so wired into §10 or CI as written **it would pass green with six
  files unformatted.** Fixed in `embarch.md` §5, which now warns about it explicitly.
- **It caught its own error on the way and said so**: `cargo fmt --all` reaches sideways through
  `path = "../..."` into sibling *repos*, so a naive per-repo `--all` sum triple-counts
  `study-designer` and `topology` — it briefly had 225 files / 4,461 lines. Its table is
  deduplicated by owning repo.
- **It strengthened the decay evidence rather than accepting mine.** My §5 text cited
  `embarch-umbrella` 209 → 211 across two units. It first confirmed both legs used the same
  command (leg 015's other three rows reproduce digit-for-digit), then walked umbrella's tree at
  every commit that night by `git archive`, validating the method against HEAD first:
  **172 → 212 hunks over eleven commits in thirteen hours, monotonic.** My two-point slice was
  the weakest part of that curve. §5 now carries the eleven-commit number.
- **It named where my text oversells.** §5 said the trap "is closed by instruction" — present
  tense — when **nothing a worker reads says it today**, which is `embarch-decision-reversals.md`
  shape 3 ("documentation is not a gate", row 81) and shape 4 ("a note describing a gap is not a
  mechanism for closing one", row 44), ageing into shape 1. The bullet now says outright that
  until the `inbox/` drop lands **this is a decision without a mechanism.**
- **And it named the honest limit of my own argument.** The sequencing case explains why *a leg*
  could not do the §10 half; it does **not** establish that declining was forced, because §5's
  own reversal condition admits "or to any repo's CI" and CI lives in the code repos, which
  workers own. Both arms therefore reduce to "do the reachable half, drop the owner half to
  `inbox/`", symmetrically. Recorded rather than argued away: §5 now opens "adopting is worth
  doing, doing the expensive half first is not."

**Hardware debts:** none. Nothing here touches a board or a machine.

**What this unit did NOT do, because the task's `Done when` says so and it must not read as
done anyway.** The load-bearing half — a worker being *told* not to run `cargo fmt` — lives in
`embarch-fleet/` and no leg checks that repo out. It is `inbox/workers-must-be-told-not-to-run-cargo-fmt.md`.
The task named that drop as the discharge, so closing is honest on its own terms, and the
reviewer checked that specifically. **"Delegated to the owner" and "done" are different facts
and the task file is deleted either way**, which is why it is said twice: here, and in §5 itself.
I pasted the instruction by hand into all three of this leg's dispatches; that is a per-leg act
no successor inherits.

**A structural note for the next leg.** `check-ownership.py --scope <s> --code-repo` prints
*"worker owns the whole tree — not path-checked"*, correctly and deliberately. It also means
**the one check that exists to stop out-of-scope writes is structurally blind to the largest
out-of-scope diff a worker can produce.** The only thing between this suite and a 1,947-line
mechanical commit under a one-line task message is a worker choosing not to type a normal
command. `api/019`'s worker typed it, reverted it by hand, and reported it — the sole reason
any of this is visible.

**Also found and not acted on**: `embarch.md` is **not tracked by `check-doc-size.py`** at all.
12 KB, no cap, no reserve, while every other suite-level doc has one — and it is the file this
decision was just written into. `scripts/` is the owner's, so it is in the `inbox/` drop.

**Reserve after this unit:** three files, unchanged, every one filed. `suite/roadmap.md` took
the pointer and stayed out of reserve at 87-something percent; `embarch.md` has no cap to spend.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** putting a 1,342-character decision entry — date, measured cost, reversal
condition — into a list of five principles whose longest is 193. The reviewer measured that and
called it an observation rather than a finding because **there is no `suite/decisions.md` to move
it to and `embarch-dev-workflow.md` is reserved**, so §5 is the only reachable home. That is a
real gap in the doc layout rather than a bad choice on my part, but it means the suite's
principles list now has one entry that is not a principle. **If a second suite-wide decision
lands with nowhere to go, the answer is a new home, not a sixth bullet.**

## 2026-09-06 01:52 — umbrella/020 check-17s-other-two-holes-and-decision-37s-stale-example

**Leg 016's second unit**, and the largest diff of the leg. Five items filed by `umbrella/018`'s
reviewer; all five closed.

**Decided:** nothing suite-wide, and two sub-project calls I accepted on the worker's argument
rather than my own:

- **Item 1 got a guard, not a deletion.** `018` deleted `embarch setup` from `bind-too-narrow`
  outright; `020` kept it on `bound-narrow` and conditioned it. The distinction is real and the
  worker stated it cleanly: `bind-too-narrow` fires only when *something answered*, so `setup`
  can never install there and the offer is unconditionally wrong; `bound-narrow` fires when
  nothing answered, so it does install, and from the guest side it is the shorter honest
  remedy. **Mechanically distinguishable, therefore a guard.**
- **Item 2 was guarded rather than recorded as an exposure, and it was *not* `embarch-topology`'s
  to fix.** `recommended_bind_address(Remote) == "0.0.0.0"` is the correct recommendation for
  whichever machine runs Core; what was wrong is which machine `doctor` read it against. New
  Warn `bind-elsewhere`, citing decisions 31 and 38.

**The reserve was paid by splitting, and that is the part worth carrying.** The worker took
`018`'s "no further without deleting live reasoning" **as evidence rather than as a starting
point** and split by mission instead of squeezing again: decision 22 moved verbatim into a new
`embarch-umbrella/decisions/bind.md`, then was amended *there*. `decisions/doctor.md` 11,519 →
**6,188 B (50.4%)**, `bind.md` 8,465 B (68.9%), no number renumbered, `decisions.md` gains an
index row. `open.md` went into reserve on item 3's addition and was **repaid in the same
commit** to 4,601/5,120 B — 89.86%, which the reviewer checked is genuinely under 90 rather
than a rounding trick. **`embarch-umbrella` now has no file in reserve at all**, first time in
this log.

**Merged:** `agent/umbrella/020-check-17-holes` (code `08ccd6f`, doc `0824325`). The doc branch
was cut at `c1ec5f7` and `main` had moved to `8e86c88` by the time it reported, so I rebased it
and **re-ran `check-ownership.py` after the rebase** — 10 paths, base `8e86c88`, clean — before
the `--ff-only`. Gate on the merge result: `cargo build`, 181 tests, clippy, all 9 doc checks,
ownership both branches, client-names clean.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **25 ran, 23 no findings, 2 findings.** It
verified the split **by extracting decision 22 from both files and diffing them** — the only
delta is the two appended amendments, nothing dropped or reworded — and confirmed every inbound
reference still resolves, including that `spec.md`, `features.d/umbrella-060` and
`history/umbrella.md` cite "decision 22" by number with no path, which is what
`DOC-COMPACTION.md` §5 wants. It also re-derived `009`'s `Must not delete:` items one by one and
checked the whitespace near-miss across the *whole* file rather than the new arm.

**Four observations it declined to call findings, and two of them I filed as
`tasks/umbrella/021`:**

1. **`setup_would_infer` shares `infer_class` but not its inputs.** Decision 22's new amendment
   says the two are "shared rather than mirrored so the two can never disagree" — and the
   reviewer checked the *inputs*: `setup` passes only the `--host` flag, `doctor` passes
   `config.core.host` **or** the sticky `saved.host`. In one reachable state the fix line names
   class `remote` where a bare `embarch setup` would infer `wsl-host`. **The remedy's direction
   survives; the class it names does not.** Shape 8, with a decision amendment written in the
   same commit as the false witness. Not reverted, and the reviewer's reason is right: check 2
   has passed the same config-or-saved `host` to the same function since it shipped, so this
   adopted an existing convention rather than contradicting a standing decision.
2. **The `Remote` branch of that same predicate is reachable, unguarded and untested** — and
   `setup` inferring `Remote` installs nothing, which is *exactly* the failure the amendment
   used to justify deleting the half from `bind-too-narrow`. The tests pin `WslHost` and `Local`
   only. **The same defect the unit was filed to close, one path further over.**
3. Decision 37's reuse list was edited to "Two so far" in the same commit in which both existing
   codes narrowed again; `bind.md` argues that restoring an intended referent is not a reuse.
   Defensible, but the sub-project's reading of 37 is one day old and has now been applied two
   ways. Item 3 of `021`.
4. `features.d/umbrella-061` flipped `Verified` `unit` → `hw` — correct on decision 38's live
   measurement, and it is item 5 of the task, but it is a drive-by in a unit whose own
   `Hardware:` is `none`.

**Hardware debts:** none discharged; **one more step added to an existing one.** Item 3 was
*recorded*, not answered, as instructed: nothing has confirmed that
`embarch-core install --bind 0.0.0.0` rewrites an existing narrow registration, which is
load-bearing under **both** Fail arms' fix lines. It is now a third named step of check 17's
verification debt in `embarch-umbrella/open.md`, alongside `018`'s experiment (a Core installed
`--bind 127.0.0.1` on a `wsl-host` machine, stopped for `bound-narrow`, running for
`bind-too-narrow`, plus the wide-registration control). **Needs the Windows side and a real
narrow-bound Core.**

**The `status.d/` fold was mine and it cost more than it looks.** Applying the fragment to
`suite/user-guide.md`'s check-17 row put that file **into reserve at 91.8% with nothing filed**
— a red gate on my own fold, not the worker's. I did not file a task: I **shortened the row
instead**, back to 89-point-something, because the row had grown into a six-code roster and a
troubleshooting table's job is symptom → action. It now names only the two codes that change
*where you go* (`bind-unproven`, `bind-elsewhere`), says the fix line names your case, and
points at decision 22 for the taxonomy. Note the shape: **a `status.d/` fragment is the one
edit in a unit that no worker's reserve budget covers**, because the worker cannot write the
file and the supervisor is not told its headroom.

**Reserve after this unit:** three files, every one filed — `suite/features.md` 93.5%
(`suite/004`), `embarch-study-designer/decisions/crate.md` 91.7% (`study-designer/006`),
`embarch-decision-reversals.md` 90.9% (`suite/004`). Down from four.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** merging a unit whose central mechanism the reviewer showed is not quite
what its own decision says it is. Item 1 above is a decision amendment asserting an invariant
that the shipped code does not hold, written in the same commit — and the log's own shape-8
entry is about exactly that being indistinguishable from a correct one to a later reader. I
merged it because the direction of the remedy is right, the alternative convention is
pre-existing and suite-wide in that file, and reverting would restore a strictly worse fix
line. **But "filed as `021`" is not the same as "fixed", and decision 22 is wrong on `main`
until it is.**

## 2026-09-06 01:22 — umbrella/019 doctor-spawn-tests-lose-their-own-exec-to-etxtbsy

**Leg 016's first unit.** A flaky test `umbrella/018`'s worker reported while running its own
gate — ~1 run in 20, `Text file busy` on execing a `#!/bin/sh` fake the test had just written.

**Decided:** nothing suite-wide. The worker took the task's own harder arm — **the bounded
retry, not a narrowing fix** — and the argument is the part worth keeping: `std::fs::write`
has already closed *our* descriptor by exec time, so the offending fd is a **copy made by a
`fork` in another test thread**, which dies at that child's own `exec` microseconds later.
Nothing on the writing side can shorten a window it does not hold, which is exactly why
`File` + `sync_all` + drop only narrows. 50 attempts, 20 ms apart, ~1 s ceiling.

**And the flake was in two tests, not one.** Reproducing it hit check **8**'s
`a_located_binary_is_actually_spawned_and_its_failures_are_reported`, same write-then-exec
shape, never reported by anyone. Both are fixed. **Read the original report as a report of the
class, not of the test it named** — that generalisation is the unit's real yield.
`src/setup.rs:748` writes an executable fake too and is not at risk: its only test never spawns it.

**Merged:** `agent/umbrella/019-etxtbsy-flake` (code `8e70b78`, doc `03c995a`). Gate on the
merge result: `cargo build`, 179 tests, clippy, all 9 doc checks, ownership on both branches
(bases `bd46a71` and `5f978e7`), client-names clean. Test-module-only diff, so I did not read
it before merging under §10's shared-crate rule; the reviewer read it after.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **24 ran, 22 no findings, 2 findings.** It
did the most independent work of any reviewer so far and two of its results are load-bearing:

- **It reproduced the flake itself** — `git archive` of the parent `5f978e7`, built in
  scratchpad, **2 failures in 80 runs**, both check 10, both `Text file busy`. **It did not
  reproduce a check-8 hit**, and said so: that half of the worker's "it is the class" claim
  rests on the worker's run, not the reviewer's. The structural argument (identical shape) is
  what carries it. Then **200 consecutive runs on the merged SHA, 0 failures**, independently.
- **It checked the masking claim from source rather than from the report**, which is the thing
  I most wanted checked: `for _ in 1..TRIES` plus an unconditional trailing spawn is exactly
  50 attempts, and **the 50th result is returned unchecked**, so a genuine `ETXTBSY` comes back
  verbatim and still fails its assertion — never a pass, never a hang, only later. It also
  confirmed the fakes are written *outside* the retried closure, so a retry re-execs and never
  re-writes, and that the one other spawning test (`/no/such/embarch-api-xyz`) has no fake and
  is correctly left unwrapped.
- **Three observations it explicitly declined to call findings**, all worth carrying:
  1. **"Closes the race" leans on an unstated premise.** The set of forked copies is fixed at
     write time and cannot grow (`O_CLOEXEC`), which is why this differs in kind from
     `sync_all`; but what makes it a *bound* rather than a closure is that **every copy's
     holder execs within ~1 s**. Nothing in this suite delays an exec that long. The
     `Done when` bar is satisfied independently by the 200 green runs, so nothing turns on it.
  2. **The new test roughly doubles the suite's wall time** — 178 tests in 0.41 s at the
     parent, 179 in **1.04 s** merged, because the `stuck` arm sleeps 49 × 20 ms and sets the
     floor. The cost is the *asserted* arm, not the fix. Parameterising `TEXT_FILE_BUSY_TRIES`
     down in that one test buys back ~0.6 s with no loss of what it pins. Not filed as a task;
     it is a one-line change for whoever next opens that module.
  3. **The retry keys on the substring `"Text file busy"`**, which is libc's strerror text
     rather than our wording — so decision 37's "never derived from `detail`" is not engaged.
     But it **fails silently open** (straight back to flaking) if a later unit changes how
     `mcp_initialize` or `api_host_schema_version` wraps the io error.
     `ErrorKind::ExecutableFileBusy` is still unstable, so there is no clean alternative today.

**Hardware debts:** none new, none discharged. Test-harness only.

**Reserve after this unit:** unchanged at four files, every one filed —
`embarch-umbrella/decisions/doctor.md` 93.7% (`umbrella/009`), `suite/features.md` 93.5%
(`suite/004`), `embarch-study-designer/decisions/crate.md` 91.7% (`study-designer/006`),
`embarch-decision-reversals.md` 90.9% (`suite/004`). The worker wrote **no** decisions file and
said why — a test-harness race changes nothing about what `doctor` decides — which is the right
call and also the convenient one, so I asked the reviewer to check it specifically. It did, from
`spec.md`, `open.md` and `decisions/doctor.md`, and agreed.

**A fold hazard the next leg must know about, because it is silent and I nearly committed it.**
`main` currently carries **15 `changelog.d` fragments the owner wrote and has not folded** —
twelve `fleet-*`, one `doc-*`, one `suite-*`, two `umbrella-*`. They are **tracked and committed**
(`de07c82`, 2026-09-05 20:37), so a leg worktree has them, and **`python3 scripts/build_changelog.py`
consumes all of them**: my first run said "16 fragment(s) consumed" and mixed the owner's two
umbrella entries into the same `history/umbrella.md` block as this unit's. Staging that file
would have folded his work under my unit's message — the legs 004/005 failure by a different
route, and `git add -A` is not involved, so the standing rule does not catch it. **What I did:**
`git checkout -- changelog.d history`, moved the 15 fragments to a scratch directory, re-ran the
assembler (`1 fragment consumed`), moved them back, and confirmed `git status` showed only this
unit's two paths. **Do this every fold until his fragments are gone.** Leg 015 evidently arrived
at the same end state — its `history/umbrella.md` diff is +4 lines, one entry — but nothing in
`supervise.md` or `ops.md` says to, so it is luck or an unrecorded habit either way. Filed as an
`inbox/` drop this leg, because the fix is a `scripts/` change and that is the owner's.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** dispatching one worker against a wave of 2 for the whole leg. Both
remaining worker tasks are `umbrella` and §6 allows one per sub-project at a time, so the second
slot sat empty for twenty minutes with no way to fill it that does not break that rule. **The
honest reading is that the queue is narrow, not that the fleet is slow** — and a queue whose
only dispatchable work is two tasks in one sub-project is one unit away from a dream.

## 2026-09-06 01:35 — suite/005 features-fragments-are-longer-than-the-file-says-they-are

**Leg 015's fourth and last unit, and mine under §8** — announced at `ts 1788675832.554579`
(00:23 MDT) with the full guardrail list, parked, and run at 01:20 after a 30-minute window
that closed at 00:55 with **zero replies**. I re-read that thread at every unit boundary and
did not re-announce. Third time §4's window has been served correctly rather than restarted.

**Why it ran at all.** `suite/features.md` closed leg 014 at 96.9% and grew in *every one* of
this leg's three folds, reaching **20,076 / 20,480 B — 98.0%, 404 B left.** When it crosses,
`check-doc-size.py` goes red inside `check-docs.py`, which is every unit's merge gate in every
sub-project — a fleet-wide stall that no agent may clear, because the file is `never` for every
worker scope and `tasks/suite/004`'s other two moves are `scripts/`. **Legs 013 and 014 both
reported this and neither acted**, and leg 014's own "least sure about" says reporting twice
and acting zero times is how a known ceiling becomes an outage. So this is that leg's advice
taken.

**Decided:** a suite-wide decision, recorded in `features.d/README.md`. The trim is
**enforcement of that file's own contract, not an exception to it**: `HEADER.md` says the row
is a pointer and the reasoning lives in the owning decision, and twelve rows had stopped being
pointers — the worst at 481–534 B, all `doctor` rows restating what their decision says. So
twelve Status columns were shortened, capability text and `Verified` and decision numbers
untouched.

**It bought 934 B — 20,076 → 19,142 B — and that is the whole yield.** The file stays in
reserve at 93.5%. **The 18,432 B reserve line was not reachable and is not reachable this
way**, because what remains is the capability column, which is the row's identity, and the row
count itself. That is now the *measured* version of what `features.d/README.md` already
claimed before this leg: *every row must be present, so the budget is spent on rows and no
compaction pass can help.* **The next fragment pass is worth roughly nothing** — that sentence
is in the README so a later leg does not run this again as a treadmill.

**`DOC-COMPACTION-PASS.md`'s human question, answered in my own words**, since this was a
compaction pass and the question is the thing no script answers: *can the file alone answer
what someone needs to work on this component today?* **Yes, and more cleanly than before.**
The inventory's job is to say what exists and how far it is verified; every trimmed row still
carries its `Verified` value and its caveat, and what came out was reasoning that the owning
decision holds and states better. The one thing a reader loses is the *why* — which is exactly
what the contract says never belonged here.

**Merged:** none — this unit has no branches. It is the supervisor's own diff on the leg
worktree, landed in its fold commit.

**Blocked:** none.

**Reviewer:** 1 finding — `tasks/suite/004`, fixed in this same commit rather than filed.
Tally after this unit: **23 ran, 21 no findings, 2 findings.** I spawned it on my own
uncommitted diff, which is new: **this is the only unit in the leg whose work nothing else
checks**, and the case for reviewing a supervisor is the same as for reviewing a worker.
It earned it immediately.

- **The finding.** I ticked `004`'s `features.md` item and wrote "the cap-and-split half below
  is now the only half left" — **and there was no item below covering it.** The Done-when list
  was reversals / features `[x]` / the compaction question / gate green, with cap-and-split
  discussed only in prose above. So `004` would have closed, with `features.md` still in
  reserve and both real fixes undone, **at which point the reserve goes *unfiled* and the next
  unit to write a `features.d/` fragment meets the cap mid-flight** — precisely what §2's
  reserve exists to prevent. A new unticked `[ ]` item now carries the owner's cap-or-split
  move and is what keeps `004` open and the filing alive.
- **It verified the guardrails mechanically rather than by reading** — a script diffing HEAD's
  assembled file against the working tree row by row, keyed on the capability cell: 123 data
  rows before and after, capability set **byte-identical**, zero diffs on the `Verified` and
  decision columns, only Status moved, and `suite/features.md` byte-for-byte what
  `build_features.py` produces. It also confirmed each cut fact still lives in its owning
  decision, by citation, which is the difference between "the pointer contract was enforced"
  and "prose was deleted".
- **It found a false claim I had preserved.** `features.d/umbrella-061` said check 1's
  `sc.exe qc` read "has never run inside `doctor` on the live machine" — **false since
  2026-09-05.** Decision 38's closing paragraph records check 1 locating the live service's
  binary by `BINARY_PATH_NAME` on the first run after the `deploy-core` that had never landed,
  in the same measurement that made check 14 answer; my own trim of `umbrella-090` had
  corrected the check-14 half of that fact and left the check-1 half standing, so two adjacent
  rows disagreed about one run. **I checked decision 38 myself rather than taking it**, and
  corrected the Status text. **I did not change that row's `Verified` column, which still reads
  `unit` while `umbrella-090` beside it reads `hw` on the same run** — changing it was outside
  the announced guardrails and it is the owning scope's claim to make, so it is item 5 of
  `tasks/umbrella/020`.
- **What it deliberately did not verify**, and this is the honest gap: **whether the §4 window
  was actually waited out.** It does not read Slack. The window is attested only by me and by
  the `ts` in the task file.

**Hardware debts:** none new. One hardware-relevant *correction*: `umbrella-061` no longer
understates check 1's verification, and whether its `Verified` column should now read better
than `unit` is `tasks/umbrella/020` item 5.

**Reserve after this unit:** four files, every one filed. `suite/features.md` 93.5%
(`suite/004`, and its second item is now the owner's), `embarch-umbrella/decisions/doctor.md`
93.7% (`umbrella/009`), `embarch-study-designer/decisions/crate.md` 91.7%
(`study-designer/006`), `embarch-decision-reversals.md` 90.9% (`suite/004`). **1,338 B of
headroom on `features.md` — about five legs at this leg's observed +228 B, six at the ~200 B
its script header models.** A reprieve, not a fix.

**Budget:** DEGRADED at start and end of the leg, wave 2, **no 429 anywhere**.

**Least sure about:** ticking `004`'s features item while the file is still listed in reserve.
The item's own text offers "or the fragments shrink" as one of three acceptable answers and
says recording the decision is the point, so it is satisfied on its own terms — and the
reviewer agreed, then immediately found that the tick was only safe *because* of the item it
made me add. **Without that item the tick was a slow-acting bug**, and I wrote it and did not
see it. The general shape is worth carrying: **ticking the last open item on a task is how a
filing disappears**, and a reserve filing that disappears is invisible until a worker meets a
wall mid-task.

## 2026-09-06 01:20 — study-designer/005 release-workflow-absence-has-no-decision-behind-it

**Leg 015's third unit**, and the one I swept out of `open.md` when the queue hit zero. Two
files in this sub-project pointed at a decision about the missing `release.yml` — `open.md`
calling it "unaddressed, not deferred" and `decisions/crate.md:63` saying it had "a separate
decision behind it" — **and that decision did not exist**, while the other half of the pointer,
`embarch-umbrella`'s 27/29, already answered it.

**Decided:** nothing suite-wide. **`embarch-study-designer` does not release** — decision 65,
on three facts the worker checked rather than took from my task file: no git tags at all and
`0.1.0` since creation; all five consumers depend by sibling path with **no `version` key**;
and there is no artifact — `extract-gatt-config` is authoring-time behind an off-by-default
feature and `study-designer-ui` was retired 2026-08-24. `verify-version` asserts a **pushed
tag** agrees with the manifest, and there is nothing here to assert. Reversal named three ways:
crates.io publication, a consumer depending by version or git ref, or a tag pushed for any
reason. This is the consistent completion of 27/29's own clause — *whichever gains a release
workflow first inherits the obligation* — not a departure from it, and no `embarch-umbrella`
path appears in either diff.

**The argument against the rejected arm is the reusable part.** Writing `release.yml` now so
the guard exists before the first tag would produce a job that fires `on: push: tags:` in a
repo that pushes none — **a step that never executes once**, which is decision 64's own
prohibition one entry up, and worse here: the audit question "does every repo check its version
against its tag?" would then read *yes* for a check that never ran.

**And it mechanised the obligation instead of restating it**, which I did not ask for and which
is the better half of the unit. `test.yml` gained a step that passes while no `release.yml`
exists and **fails if one appears without a `verify-version` job that another job `needs:`** —
so the obligation 27/29 leaves to whoever acts first now binds at the moment they act, in the
repo where it applies. 27/29 verified its own `needs:` wiring structurally only; this checks it.

**Merged:** `agent/study-designer/005-release-workflow-decision` (code `48cac00`, doc
`8100540`). Gate on the merge result: `cargo build`, 9 tests, clippy, all 9 doc checks,
ownership both branches, client-names clean. **I read this diff before merging** —
`embarch-study-designer` is the shared crate every other repo compiles — and the code side is
one workflow file; no `Cargo.toml`, no feature definition, no public surface touched.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **22 ran, 21 no findings, 1 finding.** It
re-derived all three facts independently (0 tags; five path consumers each with no `version`
key, `embarch-topology` naming the crate only in a comment, so "five" is right), rebuilt the
new step's two greps and ran them against five shapes, and confirmed a `verify-version` job in
a *different* file cannot fool it — the greps are scoped to `release.yml` by path.
**One real defect it found and correctly declined to call a finding:** the YAML block-list form
`needs:` / newline / `  - verify-version` fails the grep and exits 1. That is a **false alarm
on a correct workflow** — the *opposite* failure mode from the one decision 64 prohibits, and
it fires only inside a hypothetical future `release.yml` whose author gets an error naming the
exact wiring. A one-line grep widening whenever `crate.md` is next touched; not revert-worthy,
and deliberately not filed as a task because `crate.md` is already in reserve and the fix rides
along with the compaction that is already filed.

**A judgement call the worker flagged for me, and I accepted it.** It **removed** the `open.md`
release bullet rather than leaving it, against my task file's "closed by the decision, not
deleted". Its reading: `DOC-CONVENTIONS.md` makes every top-level bullet in an `open.md` an
open question and `collect-open-questions.py` reads it that way, **so a settled item cannot
stay without being re-reported as unsettled forever.** It quoted the bullet's substance —
including its own "unaddressed, not deferred" — inside decision 65, with a link back. The
reviewer verified the quote is actually there and actually complete, which is the whole thing
standing between "closed by a decision" and "deleted", and found the precedent: `d19d0ec`,
decision 64's own unit, *replaced* its resolved bullet the same way. **My instruction was aimed
at the failure of deleting instead of deciding, and the worker read past the wording to the
intent.** The right form of that instruction is "do not delete *instead of* deciding" — I will
phrase it that way next time.

**Hardware debts:** none, and none owed. Nothing here touches a board.

**Reserve — and this is the leg's live problem.** `embarch-study-designer/decisions/crate.md`
entered reserve at **11,267 / 12,288 B (91.7%)** on this commit; the worker trimmed decision 65
from 3,243 to 2,124 B first and filed `tasks/study-designer/006-compact-study-designer.md` in
the same commit, `blocked`, `In flux: yes` — correctly, because decision 64's `ffi` paragraph
and `open.md`'s surviving staticlib bullet both state an absence the dev-bench cross-build
landing will change. It also **declined to touch `spec.md`** at 9,080 B, 136 B under its line,
rather than put a second file into reserve for a sentence that is rationale rather than current
truth. That is a worker planning against the dispatch-time headroom instead of discovering it.
**`suite/features.md` is now 20,076 / 20,480 B — 98.0%, 404 B left**, having grown in every
one of this leg's three folds. `suite/005` runs next and it is no longer optional.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** accepting a worker's step that no CI run has ever executed. The reviewer
ran the `run:` block's *logic* in a local shell against five shapes, which is the same evidence
`suite/001` accepted for `verify-version` itself and the same qualification that entry carries
— **it has not been parsed by GitHub Actions.** That is now two release-guard mechanisms in
this suite whose only proof is a reconstruction of their own shell, and the second was accepted
partly because the first was. If the next leg meets a third, the honest move is to say the
pattern has compounded rather than to cite the precedent again.

## 2026-09-06 01:05 — umbrella/018 check-17-fix-line-can-green-its-own-check

**Leg 015's second unit.** `umbrella/017` shipped `doctor` check 17 hours earlier and its
reviewer found two defects in one arm after the merge; this is that arm rebuilt.

**Decided:** nothing suite-wide. Of the task's three shapes the worker chose **give the arm
evidence**, and the argument it wrote against the cheap one is the part worth keeping:
demoting `bind-too-narrow` to a warn "surrenders the one state the arm uniquely catches on
every machine where one `sc.exe qc` — which `bound-narrow` already spends — would settle it
outright. **Cheapest is not the same as least wrong.**" Against the expensive one it stopped
where it was told to: probing the other candidates is `embarch-topology`'s resolve contract,
another sub-project, **and it is also the weaker evidence** — a failed gateway probe indicts
Windows Firewall and a narrow bind indistinguishably, while the registration states the bind
outright. That second half was not in the task; it is the worker's own.

**`bind-too-narrow` now Fails only when the service registration is also narrow.** A wide
registration Passes `bind-matches-registered`; an unreadable one Warns `bind-unproven`, whose
fix asks from the guest rather than asserting. The extra `sc.exe` is spent only where it can
move the verdict, behind a new pure predicate
`bind_registration_can_change_the_verdict(recorded, winner_base_url)` with its own five-case
test. The fix line no longer offers `embarch setup`, and says why it is not an alternative on
that path; `bound-narrow` keeps its `setup` half, verified. The unearned word "only" is gone
from the detail string and a test asserts it stays gone.

**Merged:** `agent/umbrella/018-check-17-evidence` (code `5f978e7`, doc `c793301`). Gate on the
merge result: `cargo build`, 178 tests, clippy, all 9 doc checks, ownership both branches,
client-names clean.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **21 ran, 20 no findings, 1 finding.** It
checked `bound-narrow`'s `setup` claim against the cited source lines rather than the citation,
read **every** shortened sentence in decisions 18/19/22(b)/22(c) against its predecessor and
confirmed no conclusion or reversal condition was dropped, and settled the decision-37 question
I put to it in the other direction from the one I expected: **`spec.md`'s table must *not*
gain the two new code names**, because 37 explicitly refuses to hold a roster of code names —
"the roster that used to sit here went stale within a day of check 5 landing". Nothing owed
there. **Its three observations are now `tasks/umbrella/020`**, and two of them matter:

- **`bound-narrow`'s own `setup` fix line has the same hole `018` just closed, one path over.**
  Run `doctor` natively on the Windows side of a `wsl-host` machine and `infer_class` returns
  `Local`, `setup` installs `--bind 127.0.0.1` and writes `topology: "local"`, after which
  check 17 Passes `bind-matches` with the bind still narrow. Not a contradiction — the claim
  was made in `018`'s own diff — which is exactly why it is a task and not a revert.
- **Nothing has confirmed that `embarch-core install --bind 0.0.0.0` rewrites an existing
  narrow registration** rather than failing on an already-registered service. That is the
  load-bearing assumption under **both** Fail arms' fix lines, and if it is false the check's
  diagnosis is right while its whole remedy errors. Needs the Windows side.

**Hardware debts:** unchanged in kind and now sharper. **No arm of check 17 has met a real
narrow-bound Core.** The experiment is written into `embarch-umbrella/open.md` — a Core
installed `--bind 127.0.0.1` on a `wsl-host` machine, stopped for `bound-narrow`, running for
`bind-too-narrow`, **plus a wide-registration control that must NOT Fail**, which is the half
`017` lacked and the reason its plan could not fail. Add the `install --bind` rewrite question
above to that same sitting. Second, new: `bind-too-narrow`'s Fail is now gated on `sc.exe qc`
being readable from wherever `doctor` runs — on a WSL2 guest that means interop, and where it
is unreadable the arm degrades to `bind-unproven` by design. Unverified live.

**Also folded into this unit, both mine:**

- **`tasks/umbrella/019` drained from `inbox/`.** The worker found
  `doctor::tests::a_real_spawn_separates_answering_broken_and_hanging` fails **~1 run in 20**
  with `ETXTBSY` — reproduced 3 times in ~90 runs, predating its branch (`4e48c77`). The test
  writes shell fakes and spawns them while other test threads fork and inherit the write fd.
  **Its final gate run was green and mine was too**, so this is a red that will land on
  whatever unrelated unit is in flight when it next fires. The drop names the only fix that
  beats the race rather than narrowing it (bounded retry on `ETXTBSY`).
- **`suite/user-guide.md`'s check-17 troubleshooting row**, from the worker's `status.d/`
  fragment — it gains all three new codes and, load-bearing, the instruction **not** to answer
  `bind-too-narrow` with `embarch setup`. That file is mine, not the worker's, which is why it
  came through `status.d/` and why the fragment is the right mechanism rather than a request
  nobody actions.

**Reserve:** `embarch-umbrella/open.md` is **paid and out** — 4,840 → 4,591 B (89.7%), the
ride-along `009` was blocked on, with no bullet or open question removed and `009`'s `open.md`
item ticked. **In exchange `decisions/doctor.md` went 10,634 → 11,519 B (93.7%) and is now in
reserve**, filed on `009`'s `Compacts:` line in the same commit. The worker paid back ~900 B
by shortening 18/19/22(a)/22(b)/22(c) first and said plainly it could go no further without
deleting live reasoning — **so `020`'s ride-along is likely a mission split, not a squeeze**,
the way `012` and `015` split that file before. `suite/features.md` moved the wrong way again,
19,848 → **19,918 B, 97.3%, 562 B left**, which `suite/005` is this leg's last unit for.

**A fold mechanism worth copying, because I got it wrong first.** `build_changelog.py` is
all-or-nothing and the owner has 15 pending fragments sitting in `changelog.d/`. On `api/019`
I ran it and then `git checkout`-ed back the four `history/` files and the fragments I did not
own — which *worked* but is a revert of a completed write, and on this unit it silently
re-consumed two `umbrella-*` fragments of his that I had to catch and undo. **The right shape
is to move his 15 fragments out of `changelog.d/` first, run the assembler on what is left,
and move them back**: the assembler then consumes exactly one fragment and no revert is needed.
Verified by count on the way back in.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** merging a diff that adds two `doctor` codes when the reviewer's own read
is that `spec.md` must not list them. I believe 37 and I believe the reviewer — the entry
refuses a roster on the evidence of a roster that went stale in a day. But it means the only
place `bind-matches-registered` and `bind-unproven` are written down is the decision entry and
`suite/user-guide.md`'s row, which I wrote by hand from a `status.d/` fragment. **If that row
is ever missed, a new code exists in shipped output and in no document a user reads.** That is
a fine argument for 37's position and a bad property to have discovered by writing the row.

## 2026-09-06 00:50 — api/019 decision-20-remedy-says-remove-and-add-the-same-field

**Leg 015's first unit.** The last loose end of the decision-20 thread that ran through
`api/015`, `016` and `017`, and the third consecutive unit in this sub-project to come out of a
*reviewer* observation rather than a failure.

**Decided:** nothing suite-wide. Decision 20 gains one clause and keeps its posture: the
static-project refusal is still one `bail!` at config load with the same two remedies, and no
fourth posture joined 20's refusal, 53's retired-key refusal and 51's absent-stays-absent —
which the task forbade explicitly and the reviewer confirmed by reading the diff rather than
the claim.

**The fix is a three-arm conditional and the interesting arm is the one nobody can reach yet.**
The second remedy's tail now partitions the two `zephyr-west`-required fields by whether they
are themselves the offender: `adding {needed}` / `keeping {kept}` / `keeping {kept} and adding
{needed}`. So a `static` project setting `west_binary` is told to *keep* it rather than to
remove and re-add it in one sentence. **The reviewer checked reachability rather than assuming
it** — the partition predicate is `unhonourable.contains(f)`, the arms are ordered so none
shadows another, and all three are reachable — **and then reported that the both-offenders arm
is exercised by no test**, because the test loop sets one field at a time. Correct by
construction, no decision requires the coverage, and it is recorded here rather than filed.

**Merged:** `agent/api/019-decision-20-remedy` (code `943419b`, doc `2b22c92`). Gate on the
merge result: `cargo build`, 169 tests across 7 suites, clippy `--all-targets -D warnings`, all
9 doc checks, ownership both branches, `check-client-names.py` clean against 7 entries.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **20 ran, 19 no findings, 1 finding.** It
verified the appended decision clause against the code's real behaviour rather than its intent,
ran the new test itself at the merge SHA, and grepped for stale copies of the old remedy
wording across `.rs`/`.toml`/`.md` (only `suite/user-guide.md:161`, which describes the refusal
without quoting the remedy). **Its one observation worth carrying:**
`embarch-api/interfaces/config.md:56` says the switch keeps "**one** of those two when it is
itself the offender", while the code has a both-offenders arm that names both. The doc is
narrower than the code, not contrary to it. **I deliberately did not fix it** — see the reserve
line below, where four bytes is the whole reason.

**Two flags from the worker, and it was right to report both rather than act on either.**

1. **`embarch-api/decisions/zephyr.md` finished at 11,056 / 12,288 B — 89.97%, and the reserve
   line is 11,060 B. Four bytes.** Still under, so `DOC-COMPACTION.md` §5 correctly forbids
   filing anything against it, and nothing was filed. `interfaces/config.md` is at
   11,008 B — 52 B of headroom. **So the next `api` unit that touches either file at all
   crosses into reserve and owes a compaction task in the same commit**, and that is now true
   of the two files any decision-20-adjacent work must edit. This is the tightest a file has
   been in this suite without being filed against, and the rule that forbids filing early is
   what makes it invisible to `--pressure`. A leg reading this cold: **dispatch `api`'s
   compaction as its own unit before dispatching `api` work**, rather than making the next
   worker discover it mid-task.
2. **No Rust repo in this suite is `rustfmt`-clean and nothing has ever checked.** The worker
   ran `cargo fmt` reflexively, watched it rewrite 18 files / ~780 lines it had not touched,
   reverted all of it and re-applied its own change by hand. I counted the rest:
   `embarch-core` 289 files, `embarch-umbrella` 209, `embarch-api` 147, `embarch-topology` 53.
   §10 runs build/test/clippy and no formatting check. **The risk is not the diff, it is that
   `check-ownership.py` would allow it** — a worker owns its whole code repo, so 780 unrelated
   reformatted lines land under a one-line task's message and are unreviewable by
   construction. Filed as `tasks/suite/006`, `open` and **deliberately un-announced**: I am
   not running it, and filing is not a §4 window. I added "do not run `cargo fmt`" to this
   leg's remaining dispatches by hand.

**Also folded into this unit, mine:** `tasks/suite/006` as above.

**Hardware debts:** none. One string, one test, two doc clauses; nothing hardware-adjacent, and
the worker said plainly that the message text is asserted by the test rather than eyeballed
against a real config load.

**Reserve:** unchanged by this unit — no `features.d` row, no suite-level doc grew.
`suite/features.md` still **96.9%, 632 B left**, filed against `suite/004` and now also the
subject of `suite/005`, parked on a §4 window that closes 00:55 MDT.
`embarch-umbrella/open.md` 94.5% (filed, `009`, and `umbrella/018` is carrying it as a
ride-along right now), `embarch-decision-reversals.md` 90.9% (filed, `suite/004`, owner-only).

**The owner's 15 `changelog.d` fragments are still pending and I left them again.**
`build_changelog.py` is all-or-nothing: running it consumed all 16 fragments into five
`history/` files, so I reverted everything but `history/api.md` and this unit's own fragment.
That is the fourth leg in a row to do this. It is not a defect, but it is a standing manual
step that every fold silently depends on getting right, and a leg that forgets it folds the
owner's work under its own unit's message.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** leaving `interfaces/config.md:56` narrower than the code. It is one
word, I own the file as supervisor, and the reviewer handed it to me. I left it because the
file has 52 bytes of headroom and leg 014 was caught by exactly this — a supervisor's one-line
edit tripping the reserve and demanding a compaction task from the fold. **But "I did not fix a
known doc/code mismatch because of a byte budget" is a bad sentence**, and if the next leg
dispatches `api`'s compaction it should carry this correction with it rather than treat it as
a separate find.

## 2026-09-06 00:20 — core/004 chip-list-help-routes-to-a-retired-key

**Leg 014's fourth and last unit**, and the only one that exists because a *reviewer* found it
— `api/017`'s reviewer, three hours earlier, reporting it as an observation rather than
dropping it in `inbox/` because help text is not a decision.

**Decided:** nothing suite-wide. `embarch-core` decisions 8 and 34 are amended in place:
`chip-list` is no longer grounded in "configuring an override for an unmapped SoC", because
that override no longer exists. **`chip-list` itself is untouched and still Shipped** — what
changed is where its output goes, and the trap in this task was over-correcting into deleting
a tool that is still the right tool.

**The worker fixed five sites, not the three the task named, and the two extras are the ones
that mattered.** The task pointed at the clap doc comment and two module comments. It also
found the `SOC_TO_CHIP` const doc, and — the real one — **`UnmappedSoc`'s `Display`, which is
the text of the `/resolve-chip` 404 an operator actually reads.** That string was stale twice
over: it offered `embarch-core detect-dev-bench`'s "sibling chip-list item, **once it
exists**" (it has existed since decision 34 shipped), and then told the reader to "configure it
manually" — which is exactly the config file that does not exist. **The one string in this
whole area that a stuck operator is guaranteed to see was the one nobody had listed.**

**It rejected a config path for `SOC_TO_CHIP` rather than quietly leaving the question open**,
citing `embarch-api` 13's tombstone: this suite rebuilds and redeploys Core routinely, so the
rebuild requirement is a recorded choice. The reviewer checked that the rejection **keeps the
reversal condition live** rather than closing it — "reverse *that* first" — which is the
correct posture for a condition another sub-project owns.

**Merged:** `agent/core/004-chip-list-help` (code `8be583f`, doc `666ba55`). Gate on the merge
result: 171 tests, clippy, all 9 doc checks, ownership both branches, client-names clean.

**Blocked:** none — but **one gate item was red and I merged anyway, deliberately, and this is
the part to read.** `cargo build --target x86_64-pc-windows-msvc` fails. The worker reported
it honestly and showed it fails identically on the unmodified base; **I reproduced it myself
rather than taking that**, and it dies in `hidapi`'s build script on `guiddef.h: No such file
or directory` — WSL has no MSVC toolchain or Windows SDK, and the rustup target alone does not
supply one. `release.yml` builds this target on a native `windows-latest` runner, and
`Cross.toml` configures `cross` only for `aarch64-unknown-linux-gnu`, so **there is no
configured path for a Linux checkout to produce it at all.** The diff is doc comments plus one
`write!` format string, none of it `#[cfg]`-gated, so the Linux build covers it. **But
`supervise.md` requires "a native Windows build where `embarch-core` is involved", and that
requirement is unrunnable for every `embarch-core` worker and every leg.** The worker dropped
it in `inbox/`; I rescued the drop into the main checkout as
`inbox/core-windows-target-build-unrunnable-in-wsl.md` before deleting its worktree — it is
`scripts/`/protocol territory and therefore the owner's.

**Reviewer:** no findings. Tally after this unit: **19 ran, 18 no findings, 1 finding.** It
verified the changed error string breaks no consumer — `resolve_chip_handler` passes
`e.to_string()` through as an opaque body, the shared client only deserializes the 200 case,
and `embarch-api`'s call site wraps with `.with_context()` and never inspects the text — and
grepped `soc_chip_overrides` across the whole suite: zero in `embarch-core` code, and every
remaining doc hit is a record of the retirement. **Its one observation worth carrying:** that
`Display` string is now the unit's sole executable artifact and **no test reads it**, so the
next drift in it will be caught by nobody. `embarch-decision-reversals.md` row 52's own lesson
is that a refusal test asserting only that it refuses gates half the surface; Core has no
equivalent rule, so this is a gap rather than a violation.

**Also folded into this unit, both mine:**

- **`tasks/umbrella/018` filed** from `umbrella/017`'s two reviewer observations, which I had
  merged over. It is the sharper of the two that carries: `bind-too-narrow`'s fix line tells
  the user to re-run `embarch setup`, which on that exact path prints "already running", does
  nothing, and then **rewrites the recorded topology class to `local` — after which check 17
  passes.** A fix that greens its own check and destroys the evidence in the process. The task
  offers three shapes and forbids reaching into `embarch-topology` for the expensive one.
- **`embarch-topology/open.md` corrected by me.** It still called umbrella's
  bind-versus-topology check "a separate, still-unwired consumer"; it has been wired since
  `umbrella/017` landed. Out of an umbrella worker's ownership row, in mine, one line. **And
  my first draft of that one line put the file into reserve at exactly 90.0%**, so
  `check-doc-size.py` failed the fold and demanded a `tasks/topology/<NNN>-compact-topology.md`
  from me. I shortened the sentence instead — the tautology detail belongs to umbrella's
  decision 22 and to this log, not to `embarch-topology`'s open questions. **The reserve rule
  is not a worker rule; it caught the supervisor on a one-line edit**, which is the first time
  it has.

**Hardware debts:** none new. Text and decisions only; no logic, no field, no signature moved,
confirmed mechanically by the reviewer.

**Reserve:** unchanged by this unit — no `features.d` row, no suite-level doc grew.
`suite/features.md` stands at **96.9%, 632 B left** and is the fleet-wide risk described in
this leg's `study-designer/004` entry. `embarch-umbrella/open.md` 94.5% (filed, `009`),
`embarch-decision-reversals.md` 90.9% (filed, `suite/004`, owner-only).

**Budget:** DEGRADED at start and end of the leg, wave 2, **no 429 anywhere**.

**Least sure about:** merging with a gate item red. My reasoning is that the failure is
environmental, reproduced on the base, and cannot be caused by doc comments — and I checked it
myself instead of believing the worker. But **"the gate item is unrunnable" and "the gate item
passed" are not the same fact**, and I have now normalised skipping it for one unit. If the
next leg meets an `embarch-core` task with real logic in it, the honest position is that this
suite has *never* gate-checked a Windows build from a leg, and it should say so out loud
rather than inheriting my judgement call.

## 2026-09-06 00:12 — study-designer/004 no-ci-feature-matrix

**Leg 014's third unit**, and the second task this leg wrote for itself after the queue hit
zero. **This unit's fold also carries the daily fold of 2026-09-05** — 20 units across legs
010–014, 169,057 → 108,857 B, with 46 SHAs, 20 `**Reviewer:**` lines and all five
debt-carrying lines verified kept by `--apply`. Run by an `embarch-log-folder` subagent, so
the day itself never entered this context.

**Decided:** nothing suite-wide. `embarch-study-designer` now has CI — its **first workflow of
any kind**, on the crate `embarch-core`, `embarch-api`, `embarch-ui`, `embarch-umbrella` and
dev-bench firmware all depend on, and the crate with the largest feature matrix in the suite.

**The unit's value is a finding, not a file, and it inverts the instruction I gave.** I told
the worker to copy `embarch-topology/test.yml`'s shape, which is all `cargo test`. Doing that
would have produced exactly the fake coverage the task warned against: `serde_json` is the
crate's only dev-dependency, it pulls `serde` with `std`, and resolver v2 unifies
dev-dependency features into the library for any target needing dev-deps — **which
`cargo test` always does.** So `cargo test --features alloc` silently receives `serde/std`
and passes while `cargo build --features alloc` fails.

**Both the worker and the reviewer proved it rather than reasoning it**, independently, by
reintroducing `study-designer/003`'s actual bug (`alloc = []`) on a scratch tree: **build
fails with 16 errors, test passes 9 of 9.** The same numbers twice. `study-designer/003` was a
real compile failure that sat undetected on `main` for exactly this reason, and a matrix of
`cargo test` steps would have left it undetectable while looking like it had been fixed.

So `default`, `alloc` and `ffi` get `cargo build` steps; `std`, `gatt-extract`, `study-ui` and
`eap-parse` get `cargo test` alone, because the reviewer confirmed the converse too — their
`-e normal` and `-e normal,dev` feature columns are identical, so a build twin there adds
nothing. **The split is correct in both directions**, which is more than the task asked for.

**The `ffi` cell is a deliberate partial and says so in three places** — the workflow comment,
decision 64, and `open.md`, which now names the `--crate-type staticlib` cross-link as the
surviving absence rather than leaving it an invisible gap. A cross-compile step before that
build root exists would have been the same mistake in a different cell.

**Merged:** `agent/study-designer/004-no-ci-feature-matrix` (code `2fa7f7f`, doc `d19d0ec`).
The code diff is exactly one new file. Gate on the merge result: `cargo build`/`test`/clippy,
all 9 doc checks, ownership both branches, client-names clean. **I read this diff before
merging** because `embarch-study-designer` is a shared crate — `Cargo.toml`, the feature
definitions and the public surface are untouched, confirmed again by the reviewer.

**Blocked:** none.

**Reviewer:** no findings. Tally after this unit: **18 ran, 17 no findings, 1 finding.** It
re-derived the central claim with `cargo tree` per cell rather than accepting it, reproduced
the scratch-tree proof to the same 16 errors and 9 passes, and confirmed decision 64's number
is genuinely free across all sixteen `decisions/*.md`. Three phrasing observations, none
filed: decision 64 says "six cells" where the workflow has seven steps (it reconciles against
`spec.md`'s merged `std`/`alloc` row); it says `default` and `alloc` are checked "with
`cargo build`, not `cargo test`" where the workflow runs both; and `spec.md`'s "every cell is
built on every push" is true but loose. All three are the decision reading tighter than the
code, which is the harmless direction.

**Hardware debts:** none, and the worker was right to decline one — the staticlib cross-link
is a missing **build root**, not a missing board, so it is an `open.md` item rather than a
debt line. Worth copying: "needs hardware" and "needs tooling nobody has built" are different
kinds of owed work and only one of them waits on the owner's desk.

**Reserve — and `suite/features.md` is now the leg's most important fact.** It finished this
unit at **19,848 / 20,480 B — 96.9%, 632 B left**, having grown **+1,311 B in this one leg**
against the ~200 B per leg its own script header models. It is filed against
`tasks/suite/004`, which is `Owner: required` and cannot be dispatched, and the file is
`never` for every agent because `build_features.py` assembles it. **When it crosses the cap,
`check-doc-size.py` goes red inside `check-docs.py`, which is every unit's gate in every
sub-project — a fleet-wide stall that no agent is permitted to clear.** One more four-unit leg
at this leg's rate takes it over. The fix nobody is blocked from doing is **shortening the
`features.d/` fragments**, which are per-scope and writable by workers and by me; the fixes
that need the owner are raising the cap or splitting the inventory, both in `scripts/`.

**Budget:** DEGRADED at start and here, wave 2, no 429.

**Least sure about:** that I reported the `features.md` ceiling rather than acting on it. It
is within my ownership to shorten `features.d/` fragments — that is an ordinary doc edit, not
a reserved path — and I chose not to, on the grounds that rewriting 122 inventory rows
unattended in the last minutes of a leg is the "invent work to fill a slot" failure. But the
previous leg also only reported it, and it grew 1.3 KB since. **Reporting twice and acting
zero times is how a known ceiling becomes a fleet-wide outage**, and the next leg should treat
this as a task to file and dispatch, not a line to repeat.

## 2026-09-05 — 20 units

*Folded by leg 015's log-folder subagent on 2026-09-06, per §11. Twenty per-unit entries
from legs 010 through 014 collapse here with every SHA, every hardware debt and every
`**Reviewer:**` line preserved — the reviewer lines kept one per unit and line-anchored so
`grep '^\*\*Reviewer:' supervisor-log.md` still tallies. What is gone is the narrative
reasoning behind each accepted judgement; git holds it in `embarch-fleet` and in each
unit's own doc commit, listed below. **Three of this day's entries wrote a field as
`**Hardware debts: …**` — bolding past the colon — which is invisible to the fold's own
ledger**; those three are carried here in prose and re-stated in the shape the ledger can
see. The day is the relay's whole handoff surface: legs 010–014 ran back to back, the
queue hit zero twice and was refilled twice out of `open.md`, and the last leg wrote its
own tasks.*

**Read this first: `suite/features.md` is 963 B from taking every gate in the suite red,
and no agent may touch it.** It closed the day at **19,517 / 20,480 B — 95.3%**, having
grown **~980 B in leg 014 alone** against the ~200 B per leg its own script header
measures. It is assembled by `build_features.py` from `features.d/` on every fold and is
`never` for every worker scope; `check-ownership.py` refuses it to all of them. So when it
crosses, `check-doc-size.py` goes red — and that is **every unit's merge gate in every
sub-project, fleet-wide** — while the check's own message prints *shorten this file and
file a compaction task*, **an instruction naming an action nobody is allowed to take, and
which the next fold would overwrite anyway.** It is filed against `tasks/suite/004`, which
is `Owner: required` and cannot be dispatched. At 119 rows its growth is monotonic by
design: the inventory records what the suite has and the suite gains capabilities, so it
**will re-enter reserve on the next feature row whatever anyone does today**. The three
real moves are shortening the `features.d/` fragments (a per-scope act, so the enforcement
is aimed at the wrong scope), raising the cap for an assembled inventory, or splitting it —
**and the last two are `scripts/`, which is the owner's.** `suite/004` marks that half
blocked on the owner rather than on flux, explicitly so no leg dispatches a worker at it.
A compaction task refiled every few folds is a treadmill, not a debt.

**Two dispatch mechanisms failed this day and both are filed `Owner: required`; a leg must
work around them, not re-derive them.**

1. **Two workers ran the same two tasks concurrently, in the same worktrees** (leg 012,
   `api/012` and `umbrella/012`). The supervisor was told mid-leg that both workers had
   died, checked all four worktrees — clean, zero commits — and re-dispatched. They were
   alive and mid-pass. **A worktree is as bad a liveness probe as a branch, for the reason
   `ops.md` §3 rejected the branch**: a worker's tree is clean for the entire reading half
   of its run, and the `api` worker's transcript ends mid-sentence at "Now I'll write the
   compacted `spec.md`" — every byte of analysis done, not one byte written.
   `tasks/README.md` already settles staleness by the **process tree**; nothing consulted
   it. `tasks/doc/009`, `Owner: required`, because every candidate fix is in `.claude/` or
   the fleet docs.
2. **A reviewer reads `embarch-doc`'s working tree at the *leg's* start, not at the unit it
   is reviewing.** A leg works in a detached worktree and never advances the owner's
   checkout; a reviewer is spawned into the ordinary working directory. Its `git show <sha>`
   reads are correct, so **the verdict is sound** — but everything it reads *around* the
   diff is as many units stale as the leg is old, and the failure mode is a confidently
   wrong **`pre-existing`** label, which is the phrase that routes a finding to "not this
   unit's problem". A reviewer reading stale context systematically under-reports exactly
   the contradictions the leg itself introduced. `tasks/doc/010`, `Owner: required`.
   **The workaround costs a leg nothing: pass the reviewer the leg's worktree path and tell
   it to read files there.** Leg 012 did not, for any of its four reviewers; **leg 013 did,
   for all four, and it worked** — no stale `pre-existing` label, and one reviewer flagged
   the single path it read outside the worktree rather than letting it pass.

**Slack is settled and must not be re-derived.** Leg 010 confirmed the connector is
**deferred**: absent from the initial tool list, reachable with `ToolSearch`
`select:mcp__claude_ai_Slack__*`, exactly as `ops.md` §5.2a now says. Unit lines went to
**#embarch-fleet** and both stop channels were live from leg 010 onward. The three
predecessors that recorded "no Slack tool" were all wrong.

**No §4 announcement window is open.** `suite/003`'s was announced by the owner at
**11:32:15 MDT (`ts 1788629535.009729`)** and discharged at 12:02:31 with **zero replies**;
leg 011 re-read that thread twice, did **not** re-announce and did **not** restart the
clock. That is the second time §4's relay handoff worked as designed (`suite/001` was the
first) and the first time it worked across a *day* and three intervening legs. The rule
earns its complexity: a leg that restarted the clock would have parked a task that had
already served its window, and legs 007–009 each did exactly that for the wrong reason.

**No rebase is unsettled, and nothing is left mid-flight.** Four units rebased onto a
moving `main` (`api/016`, `umbrella/007`, `umbrella/015`, `umbrella/011` — the last twice)
and all were clean; `umbrella/015`'s single conflict was its own task file's `State:` line.
`umbrella/012`'s doc branch was rebased onto `84c0486` before merging. Nothing blocked, in
any of the twenty units, and no gate went red on a merge result that was not fixed before
the push.

### Decided

**The one suite-wide decision of the day is `suite/003`, and it is the supervisor's own
hands on `main` under §8.** `embarch-core/spec.md` §5 — the on-disk result layout — **now
lives in `embarch-core/interfaces.md`**, and `embarch-study-designer/spec.md`'s citation
follows it. Four calls inside it: the block landed **at the end of `interfaces.md`,
immediately after the Studies route table**, because `GET /study/{id}` · `/steps` ·
`/streams` · `/stream/{name}` are exactly what read those files (*rejected: a section of
its own near the top* — it is reference material loaded deliberately, `DOC-COMPACTION.md`
§9, not something every reader of the HTTP surface meets first); **no stub `## 5.` heading
was left behind**, the header line carries the pointer instead, because a stub keeps a
slice of the byte cost the move exists to remove; **the citation now points by section
*name*, not number** — *Result layout on disk* — and **that is the actual fix, not the
move**, since a section number is the thing that broke and `check-links.py` skips anchors
while `check-decision-refs.py` only resolves decision numbers, so nothing mechanical would
ever have caught it; and **two sentences were added that the old §5 never had**, lifted out
of `umbrella/005` three hours earlier — `study_results/` retention is bounded by **count,
not bytes** (`EMBARCH_STUDY_RESULTS_KEEP`, default 50, `0` disables, swept at `POST
/study`), and `embarch doctor` check 16 reports count *and* size because the bytes are
still nobody's bound. That fact was sitting only inside an `embarch-umbrella` decision, and
a `suite` unit is the only actor allowed to move it. `spec.md` 8,988 → 8,148 B (87.8% →
79.6%); `interfaces.md` 9,953 → 11,405 B (64.8% → 74.3%). Only §6 → §5 renumbered, which is
what bounded the blast radius to one citation. A repo-wide `grep` found exactly that one
section-number citation, confirming the task's day-old count.

Everything else was sub-project-scoped and accepted from the worker. **The pattern worth
naming across the day: on eight `build or retire` forks the worker took neither option as
written, and in six of those the *losing* argument was what made the answer right.** The
ones the next leg cannot recover:

- **`api/016` ships a deliberate breaking config change, and it is the highest-blast-radius
  diff of the day.** Five fields — `default_target`, `default_snippets`,
  `default_extra_args`, `west_binary`, `build_dir_root` — now fail at **config load** on a
  `static` project, in one message naming every one set. A config that loads today can stop
  loading and the suite has no deprecation window (`embarch-dev-workflow.md` §6). Both
  rejections are arguments, not preferences: **narrowing** deletes the one member of the
  class already behaving correctly and decision 44c is the *measured* cost of a silently
  dropped setting (a build reporting success having produced an image whose config said the
  option was unset); **warn-for-all-five**, the only consistent non-breaking shape, lands
  the warn on a binary whose normal mode is an MCP server whose stderr nobody reads, and
  would make a **third** posture for one class of config mistake beside this refusal and
  decision 53's. The supervisor checked blast radius by reading the live
  `/home/gabriel/Github/embarch/embarch-api/config.toml`: one `[[projects]]` entry
  (`healthband-roadrunner`) setting `build_command`, `artifact_path`, `chip`,
  `flash_format`, `build_timeout_secs`, `probe_serial`, `artifact_path_for_core` — **none of
  the five**; the `west_binary` in that file is under `[dev_bench]`, which deserializes into
  `DevBenchConfig` and is never walked by `validate()`. **The live config still loads.**
- **`api/014` orphans build directories, once, deliberately.** `extra_args` is hashed with
  **FNV-1a spelled out in `zephyr.rs`** rather than `DefaultHasher`, whose output is not
  stable across Rust releases. A keyed SipHash was rejected — `extra_args` comes from this
  machine's own project config, never an untrusted caller, so a key buys nothing and becomes
  one more thing that must stay in step with names already on disk forever; a sanitised
  non-hash spelling was rejected because an arbitrary `west build` flag has no length bound
  and its escaping becomes a second thing to hold stable. The encoding **length-prefixes
  each argument**, so `["-p", "always"]` (`0x6222ab5e7fce6ae9`) and `["-p always"]`
  (`0xbd3c86d6cdf7411a`) cannot collide. **Every build directory already named by the old
  scheme is orphaned by this change, deliberately and once** — no migration is soundly
  buildable, because recomputing an old name means reproducing the `DefaultHasher` output of
  whichever toolchain wrote it. One orphaning now at a known moment against an unbounded
  number later, silently. **Those directories belong to still-valid targets, so
  `embarch-umbrella` decision 26 protects them from `--prune` forever, and they are a
  human's to delete.**
- **`api/013` built decision 19's `target.json`** rather than retiring it, and the reason is
  invisible from inside `embarch-api`: `embarch-umbrella` decision 26's `doctor --prune` is
  *already deferred on this file*, so the cheap doc-fix would have left another repo's
  decision blocked on something nobody was ever going to build. The claim had stood as
  current truth in `interfaces/config.md` for ~three months with no source hit anywhere in
  the crate. Four calls: `TargetManifest` carries the descriptor `serde_json::Value`
  **itself**, the same object the tool response echoes, so provenance on disk and the answer
  the caller got are one serialization; written **after** the build command, only into a
  directory that already exists, **never creating one** (a manifest beside a directory no
  build produced is manufactured evidence), and a **failed** build's directory still gets
  one; **absence means "unattributable", never "orphaned"**, and the write is best-effort —
  the second is only sound because of the first; routed through `json_out::pretty` so it
  carries `schema_version`, decided after noticing the file is read by *another repo*.
  **Rejected:** writing at `resolve()`'s return, which the task suggested — `resolve` also
  serves `flash` and `reset`, so it would create build directories for targets nobody built.
- **`api/017` retires decision 13 (per-project SoC→chip overrides) rather than building
  it**, on a stronger argument than the task's. `embarch-core` decision 8 has Core validate
  every SoC→chip mapping against probe-rs's own registry per call, so even a stale entry in
  Core's table fails like an unmapped SoC — **and a per-project override consulted *before*
  that call skips the validation entirely.** One typo would reach `/flash` as a plausible
  chip name and attach the wrong physical target, the exact silent-wrong-target failure Core
  decision 8 refused fuzzy matching to avoid. **The short-circuit was the entry's whole
  selling point and the short-circuit is the defect**; the saving it bought was one loopback
  HTTP call this crate makes at `/flash` anyway. The losing case is kept **with a reversal
  condition** — *a Core the operator cannot rebuild* — which is what makes this a retirement
  rather than a deletion, and the hatch would then belong in Core's own config,
  machine-scoped, still registry-validated. It is not closed by deleting doc text:
  `src/config.rs` keeps the key as `retired_soc_chip_overrides: Option<toml::Value>` so a
  config written from the old interface doc is **refused at load on both discovery kinds**.
- **`umbrella/017` closed decision 22's three designed-and-unbuilt checks: (a) built as
  `doctor` check 17, (b) firewall and (c) disk space retired unbuilt**, each half carrying
  the losing argument. **The worker found 22(a) as written to be tautological and the entry
  now says so** — "the address `/status` was reached at versus what the detected topology
  needs" cannot disagree, because `probe_topology` sets the class *from* the winning
  candidate (`doctor.rs:139`), so the check would compare the winner against itself. The
  independent half is **the class `setup` recorded in machine state**, and with none
  recorded the check warns `no-recorded-class` rather than passing vacuously — a design the
  decision did not contain, arrived at by reading the code the decision described. And the
  failure 22(a) names is mostly invisible from the reachable side, so check 17 also reads
  `--bind` off the same `sc.exe qc` line `locate_core` and `deploy-core` already parse, only
  when nothing answered: two Fails on different evidence (`bind-too-narrow`, `bound-narrow`)
  plus `bind-not-the-cause` as the useful negative. **The doctor table went from twenty rows
  / two unbuilt decisions to eighteen rows / one**, and `tasks/umbrella/009`'s counts were
  refreshed with it, which matters because that task's `Must not delete:` clause protects
  the table *by a count*.
- **`umbrella/010` fixed check 1's false red on a healthy `wsl-host` and it took both
  readings, not one.** The task offered topology-awareness *or* an explicit
  not-applicable; the worker took the first and kept the second as its **fallback**.
  Reading (b) alone clears the red **and leaves check 14 permanently unanswerable on the
  primary topology**, because decision 31 has check 14 shell out to Core's own binary
  precisely because nothing else can answer about the right machine. So both layers ship:
  `locate_core` consults `windows_core_service_binary_path()` (the service's own
  `BINARY_PATH_NAME`, read by `deploy-core` since decision 32) in the WSL2 branch, **after
  `PATH`, ahead of both guesses**, with its own `FoundBy::WindowsServiceRegistration`
  because check 1 prints provenance and *a reading is not a guess*; and if that finds
  nothing, check 1 is **Warn / `core-not-local`** on `wsl-host` and `remote`, never a Fail
  where no local Core belongs. `remote` had the same false red and nobody had noticed. New
  **decision 38** in `decisions/topology.md`, **decision 31 amended** for check 14's half.
  **Where decision 31 bit:** the path `sc.exe qc` names and `wslpath` translates *is* the
  file the Windows service runs, so resolving it is not a verdict about the wrong machine —
  **but the suite manifest sitting next to `embarch` is**, describing the Linux archive
  `embarch` came from while Core is a Windows build from a different one. Check 1 no longer
  compares those two, says so in `detail`, and points at check 15 with code
  `manifest-partial`. **Without that, this unit would have replaced one FAIL on the owner's
  machine with a different one.** Three of sixteen dark checks becomes one, pending the live
  run; **check 15 stays degraded and the worker did not reach for it** — the running Core
  serves no `core_version`, which is `embarch-core`'s, outside its ownership row.
- **`umbrella/005` answered a `build both halves or retire` fork with a third option, and it
  was right.** It built the reporting half as `doctor` **check 16**, **deferred `--prune`
  with its blockers named**, and **amended decision 26 rather than retiring it**. Three
  facts none of which are visible from inside `embarch-umbrella`: (1) the `study_results/`
  half of decision 26's premise is **dead** — `embarch-core` already ships
  `sweep_study_results` / `EMBARCH_STUDY_RESULTS_KEEP`, and umbrella building a second
  retention policy for a directory it does not own, and cannot reach at all on `remote`, is
  the mirror-that-drifts mistake decision 17's amendment already refused; what survives is
  a real gap, that the sweep bounds a **count** so the bytes are still nobody's bound, which
  is what check 16 reports. (2) **Nothing in this crate can name a valid build directory,
  only count directories** — `crate::zephyr` deliberately overcounts and models neither
  variant names nor cpucluster, so the oracle is `embarch-api list-targets` and wiring that
  shell-out is decision 17's own amendment, itself unbuilt: **`--prune` is blocked behind
  another decision rather than behind effort.** (3) The prune rule is under-specified
  against the name it would judge. **The refused checkbox is the best thing in the unit:**
  `Done when` box 2 asked for "a test that a currently-valid target's build directory is
  never deleted"; nothing in the change deletes anything, so the worker **declined to fake
  it green** and said what stands in its place.
- **`umbrella/007` built decision 17's shell-out and its reason retires the alternative
  rather than merely beating it.** Reading `count_for_variants`, it found the local scanner
  counts the declared **default** revision as backed *unconditionally*, with `variant_count`
  `.max(1)` and a missing revision section yielding 1 — so **for any repo with a parseable
  `boards/` and a non-empty `app/`, the count could not be zero.** The fail its own doc
  comment promised was unreachable and check 8's zephyr-west branch was re-asserting
  `init`'s shape test under a stronger name; the error was one-sided toward passing, which
  is the *absence* of a signal, and retiring the amendment would have meant writing that
  down as intended behaviour. Three outcomes rather than two (`Count` / `Rejected` /
  `Unanswerable`), an unanswerable being a **warn naming which**, never a pass — "answered
  less often but able to say no" over "always answered, structurally unable to say no."
  **`zephyr::count_valid_targets` and its revision/variant/soc modelling are deleted**; only
  `init`'s shape detection remains.
- **`umbrella/011` replaced check 10's parse of a format that does not exist.** It reads
  `~/.claude.json` and keeps the spawn, over trusting `Status: ✔ Connected` — and the reason
  retires the alternative: reading `Status:` *still means running `claude`*, which is never
  on `PATH` from a terminal, so that route reaches **no verdict at all** on the machine the
  check was written for, and it would hand the answer back to the CLI's own health check,
  the thing decision 23 built a spawn to reproduce independently. **New decision 40**, with
  **decision 23 amended in place** — the spawn, the 10 s budget and the three distinct codes
  all stand, only *where it got the command line* was replaced. **Identity is the command,
  not the config key**: key `embarch`, else any entry whose `command` file stem is
  `embarch-api` (so `.exe` counts), else key `embarch-api` — which is what stops `doctor`
  printing `not registered` beside a server the same session is using. `Environment:` is
  half-closed and `open.md` says which half: the registered `env` map is now applied on the
  spawn; the server still starts in `doctor`'s environment rather than the CLI's.
- **`umbrella/006` built decision 18's Linux probe-permission branch with one condition
  decision 18 never named, and it is the right call: the scan runs only when Core
  enumerates on *this* machine** — Linux **and** `TopologyClass::Local`. Check 5's count
  comes off Core's `/status`, so under `wsl-host` the count describes the Windows box while
  the USB bus describes the WSL2 guest, and scanning anyway would reproduce check 14's
  failure signature (decision 31): a confident verdict about the wrong machine. A
  `std::fs` scan of `/sys/bus/usb/devices/*/idVendor`, `cfg!` rather than `#[cfg]` so all
  three host branches compile and are tested here. **Rejected, and all three are right:**
  `0403` (FTDI) on the vendor list — several JTAG adapters use it and so does every third
  serial cable on this bench, so it would fail the check on a machine with no probe at all;
  a `probe.rs` udev-rules URL it could not verify; and shelling out to `lsusb`, which needs
  `usbutils` while sysfs is always there. Nine vendor IDs kept.
- **`api/010` retired the `[[projects.targets]]` menu (new decision 53), and the argument
  that decides it is not the task's.** A `target` param does **not** contradict decision 51,
  because a row replaces the whole argv rather than splicing into another build system's
  flag grammar; it loses on **cost against value** — a second, differently-shaped selection
  grammar across `build`/`flash`/`build_and_flash`/`reset`/`run_study` and the CLI, for a
  feature **no config anywhere uses**. The worker checked rather than assumed: absent from
  `config.example.toml`, from `/home/gabriel/.config/embarch/`, and from every other repo's
  source and docs; the only declaration in existence was `tests/json_surface.rs`'s own
  fixture. Two things make the removal lossless: **`list_targets` for a `static` project no
  longer errors**, returning exactly one row — the project itself, with `build_command`,
  `chip` and **resolved** `artifact_path`, the row *being* the build a bare `build` runs;
  and a config still declaring `[[projects.targets]]` **fails at load naming the
  retirement**, for both discovery kinds.
- **`api/011` built decision 27's capacity diagnostic, and the design property that makes it
  safe is the one to keep:** `src/capacity.rs` runs **only after `serde` has already refused
  the value**. It is a diagnostic on the error path, never a second gate, so a wrong entry
  in its bounds table can only *worsen a message*, never reject a study `serde` would have
  accepted — **which is what licenses the table being deliberately partial** instead of
  becoming a second, drifting copy of every limit in `embarch-study-designer`. Lists are
  named by entry count, names by **byte** length, because bytes are what `heapless::String<N>`
  actually bounds. The test pins what the caller used to get — `sequence exceeds its bound
  at line 1 column 8785` — and asserts 64 steps still deserializes, so the refusal under
  test is the bound and not the fixture.
- **`api/009` built decisions 20 and 21 and retired neither**, and it **corrected decision
  21's own premise while building it**: decision 21 argued the literal `"none"` "cannot
  collide with a real snippet name", and that is **false** — a snippet name is just a
  directory under `app/<app>/snippets/` and nothing reserves `none`. So `["none"]` against
  an app that really declares one is now **refused naming the collision** rather than the
  collision being assumed away, and `"none"` inside `default_snippets` is a config-load
  error. `[projects.default_target]` is a `zephyr-west` base applied **per field** before a
  call's params narrow (**rejected**: all-or-nothing, which turns "narrow to the other
  revision" into "restate every axis"), with `NoMatch`/`Ambiguous` errors **naming which
  axes came from the default**. It found a **third** false statement in the same interface
  file: the build directory was documented as `…-<snippets-or-none>-<extra-args-hash>`, and
  `Target::build_dir_name` has never produced that — both trailing segments are *absent*,
  not spelled `none`, when empty.
- **`api/015` is the fleet's first unit that exists because a reviewer found something** —
  `api/010`'s reviewer, reading a landed diff against decision 12. **The review pass has now
  paid for itself once, against a defect the gate was structurally blind to.** The worker
  chose the shape the supervisor would not have: it kept the `retired_targets` check one
  level above the `match project.discovery` and made only the remediation sentence a
  `match`, because **a config carrying retired rows *and* a per-kind field error must hear
  about the retired menu first** — inside the match, the `zephyr-west` arm's field checks
  come first and the caller is told to remove `build_command` before being told the menu is
  gone. **The test is the real deliverable and it is better than what was asked for:** a
  **negative** assertion (`!contains("Declare one [[projects]] entry per target")`, the
  static remedy's phrase, pinned positively by the static test) so **the two tests cannot
  both pass against a shared tail**; and a **conditional** stronger than any phrase check —
  if the message names `build_command` at all, it must be inside `Do not move them into
  build_command/chip/artifact_path`, so a future rewrite cannot name a decision-12-forbidden
  field as an instruction. That second one generalises past this defect.
- **`ui/001` moved trace binning server-side, and a defect was found by driving it that no
  test in this suite would have caught.** `GET /api/trace/{study}/{tap}/bins?from&to&width`
  now does in Rust what the browser was doing, at most `width` runs per lane; **`Lane.spans`
  is no longer serialized at all** and `span_count` replaces the two places `app.js` counted
  them. On a synthetic capture built to the reference's shape (225,627 rows / 112,804 spans
  / 26 lanes) spans were **12.6 MB of a 12.6 MB payload**; first paint is now 12.7 KB +
  30.5 KB and a window costs 1–6 ms. The defect: zooming at the pointer computed its anchor
  from a pixel fraction, so **every wheel notch produced a fractional window** — invisible
  while the aggregation was in the same floats, a `400` against a `u64` query. **Every Rust
  test passed with the bug present**; it took headless Firefox against the real binary and a
  stub Core. Decision 18 went in a **new** `embarch-ui/decisions/trace-transfer.md` rather
  than inside `decisions/trace-chart.md`, on the worker's own argument that putting a
  load-time decision inside the navigation decision's file is *the same conflation `open.md`
  warned against, in the docs instead of the code*.
- **`umbrella/012` split a decision group rather than squeezing it**, because
  `decisions/doctor.md` would have gone **over** its 12 KB cap, not merely into reserve.
  Decisions **11, 37 and 39 moved verbatim** into a new `decisions/reporting.md` — "what a
  consumer reads back" — leaving 18, 19, 22, 23 and 31 in `doctor.md` — "what is checked":
  10,566 B → 9,454 + 4,089 B. The `In flux: yes` objection that keeps `tasks/umbrella/009`
  parked **does not reach a verbatim move, which restates nothing.** New **decision 39**: a
  check that resolves a directory prints which one, in `detail` and as a `path` field beside
  `code` — one path, not every path a check mentions — and the `%ProgramData%` caveat is
  printed **only on the arm where it can mislead**, because `setup::data_dir_for` *hardcodes*
  `/mnt/c/ProgramData/embarch` for `wsl-host`, a **stronger** assumption than the gap
  `embarch-token.md` §5 records.
- **`umbrella/015` kept the `no-cli` code and wrote the *general* rule rather than the
  instance.** Both states are "there is no agent CLI here to consult" and both take the same
  action, so a seventh code would split a set nothing branches on — and the durable half is
  what went into decision 37: **renaming a code breaks loudly, moving what a code means
  breaks silently, and nothing mechanical can see the second**, so a deliberate reuse gets
  written down in the decision that moved it. It also kept the "checks 5 and 22" clause by
  **demoting it from a `Do not delete` list item to a test** — re-expressed as the *rule*
  the two checks were evidence for (more states than statuses earns a code), both checks
  still named. A `Must not delete:` item honoured by understanding what it was for.
- **`umbrella/013` rewrote decision 26 to state what `api/013` actually shipped**, and
  `api/012` did the doc-compaction that let `api` start the day's second half with nothing
  in reserve. `api/012` also settled three moves worth keeping: decision 30 (the
  smoke-harness tier) **moved verbatim** to `decisions/shape.md`; `spec.md` §3's selection
  semantics now live **only** in `interfaces/config.md`; and the `build_cwd`/`west` trap
  left `spec.md` for `decisions/build.md` 5 **gaining a qualifier it had in neither place** —
  `build_cwd` is a `static` project's field, a `zephyr-west` build directory being
  per-target. **A qualifier added during a compaction pass is a claim, not a move**, so the
  reviewer was asked to check that one against source specifically; it holds.

### Merged

| Unit | Code | Doc |
|---|---|---|
| `agent/umbrella/017-decision-22-three-first-day-checks` | umbrella `80f4cb8` | doc `cbe8a5d` |
| `agent/api/017-soc-chip-overrides-decided-never-built` | api `4ef324f` | doc `495a7bf` |
| `agent/api/016-decisions-20-21-loose-ends` | api `4fd08d1` | doc `4e1c132` |
| `agent/umbrella/007-doctor-target-count-shellout` | umbrella `1489f36` | doc `1382ad1` |
| `agent/umbrella/015-decision-37-appends-instead-of-editing` | *code branch empty — `9d459b9` is the pre-existing tip* | doc `3f4078a` |
| `agent/umbrella/013-decision-26-target-json-is-written` | *code branch empty — `9d459b9` is the pre-existing tip* | doc `5b53a00` |
| `agent/umbrella/011-check-10-parses-a-format-that-does-not-exist` | umbrella `9d459b9` | doc `0e75931` |
| `agent/api/014-extra-args-hash-not-stable` | api `ab51bd1` | doc `60b316f` |
| `agent/umbrella/012-check-16-names-dir` | umbrella `d9844dd` (force-pushed over `c54d5f0`) | doc `811380b` |
| `agent/api/012-compact-api` | *doc-only — code branch carried no commits* | doc `a7ec7d0` |
| `agent/umbrella/010-doctor-check-1-fails-on-a-healthy-wsl-host` | umbrella `1b41853`, plus supervisor fix `81e20f4` | doc `1c87314` |
| `agent/api/015-retired-targets-error-misadvises-zephyr` | api `9c8d646` | doc `4be6baf` |
| `agent/api/013-target-json-not-written` | api `ac1e37c` | doc `353a03e` (inbox drain `f5a5d29`, separate on purpose) |
| `agent/umbrella/006-doctor-probe-not-permitted` | umbrella `66e4a78` | doc `de8a381` |
| `suite/003-core-spec-5-to-interfaces` | *no branches — a `suite` unit is the supervisor's own hands on `main`* | `embarch-doc` only, folded in that unit's own commit |
| `agent/api/011-capacity-error-message` | api `4a4d541` | doc `f54d8ad` |
| `agent/umbrella/005-doctor-prune` | umbrella `ddd3e4d` | doc `da4aa4c` |
| `agent/api/010-static-project-target-menu` | api `863f187` | doc `f46fb80` |
| `agent/api/009-config-decisions-20-21-unbuilt` | api `9b961da` | doc `304b7db` |
| `agent/ui/001-trace-view-server-side-binning` | ui `f4bf4b3` | doc `33c1430` |

Every unit's gate was re-run by the supervisor **on the merge result, not on the branch**,
and every one was green: `cargo build` / `cargo test` / `clippy --all-targets -D warnings`
wherever there was Rust in the diff, the doc checks (**8** for legs 010–012, **9** from
leg 013 onward — `check-decision-refs.py` joined, which is what proves a file move did not
break a `decision N` reference), `check-ownership.py` on both branches, and `client-names`
clean against 7 entries. Test counts climbed 95 → 174 across the day. **No native Windows
build ran on any unit**, deliberately: `embarch-umbrella` shells out to `embarch-core`
rather than depending on it, so §10's Windows clause does not reach it — `umbrella/001`'s
reasoning, not a new one. `crates/embarch-core-client/` was verified untouched by path on
`api/009`, `api/010`, `api/011` and `api/013`, so nothing reached `embarch-ui`. `suite/003`
ran **no `cargo` at all, deliberately** — the diff is three markdown files; that is the
"gate satisfied by an argument rather than a run" shape, and the argument here is that the
compiler was given nothing to disagree about. **Two contextual SHAs, neither a unit's:**
`7e21b08` is where leg 013 started, and `17c4669` / `180c2be` are the `origin/main` and
stale-local-`main` pair behind the `umbrella/005` ownership false red below. `4e48c77` is
the commit that first built check 10, cited because decision 37 has described its code set
incompletely since that day.

### Blocked

**None, in any of the twenty units.** No task went to `blocked` as an outcome, and no gate
went red on a merge result that was not fixed and re-run before the push. Two tasks were
*filed* `blocked` — `tasks/umbrella/016` (`In flux: yes`) and `tasks/suite/004` (blocked on
the **owner**, not on flux) — and `tasks/api/012` was **re-blocked by the supervisor after a
worker unblocked it**, see below.

### Reviewer

**Reviewer:** no findings. — `umbrella/017`. Cleared decision 37's code-roster rule (7 codes
across 3 statuses, no reused spelling), decision 32's parse-duplication concern, and
`DOC-CONVENTIONS.md`'s tombstone shape at the sub-part level. **Its two observations are the
most valuable thing in that unit, neither is a contradiction, and neither was filed as a
task — the leg ran out of units, not out of reason to file them. They are the next leg's:**
(1) **`bind-too-narrow`'s fix line can silence its own check instead of fixing anything** —
it offers "or re-run `embarch setup`", but `bind-too-narrow` only fires when a candidate
*answered*, which is exactly the condition `setup.rs:80` treats as `already_running`, so
setup prints "nothing to install" and never touches the bind, and `setup.rs:343` then writes
the recorded topology unconditionally from the **winner's** class, after which check 17
passes `bind-matches`. **A fix that makes the check green without changing anything is worse
than no fix**, and the same string is correct on the `bound-narrow` arm. (2)
**`bind-too-narrow`'s evidence does not discriminate, and `open.md`'s plan for retiring its
debt cannot retire it** — `candidates()` always tries `Local @ 127.0.0.1` first and stops at
the first responder, so a Core bound `0.0.0.0` wins at loopback exactly as one bound
`127.0.0.1` does; the new bullet says settling it means a `doctor` run from the Windows side
"which still reaches loopback", and that arm emits `bind-too-narrow` either way. The detail
string's word "only" is unearned for the same reason. A third, out of scope and correctly
untouched: **`embarch-topology/open.md:17` still calls umbrella's bind-versus-topology check
"a separate, still-unwired consumer". It is wired now** — needs a `topology` unit or an owner
edit.
**Reviewer:** no findings. — `api/017`. It verified the cross-repo claim about Core against
`embarch-core/src/chip_resolve.rs:80-93` rather than against decision 8's wording, and caught
**one overstatement confined to the task file** (the supervisor wrote that Core validates "at
load *and* per call"; there is no load-time validation, it is per call plus a test over every
table entry) — decision 13's own text says only "validates every mapping against probe-rs's
registry", so **the retirement argument does not rest on the error**. Its two observations
were filed as tasks: **`tasks/core/004`** — `embarch-core chip-list --help` (`src/main.rs:100`
plus two `chip_resolve.rs` module comments) still routes an operator into the retired key, so
Core's own help sends someone to a key that stops `embarch-api` starting; its sharper half is
that `SOC_TO_CHIP` is a source `const` with no config path, so the remedy is really "edit
Core's source and redeploy" and neither message says so. And **`tasks/api/019`** — decision
20's remedy is self-contradictory for two of its five fields ("remove `west_binary`" and "add
`west_binary`" in one message), with an explicit instruction not to invent a fourth posture
for this class.
**Reviewer:** no findings. — `api/016`. It verified the refusal is structurally inside the
`Discovery::Static` arm and cannot catch a `zephyr-west` project; that no reader of the five
fields is now dead code; that `grep -rn soc_chip_overrides` across the whole crate returns
**zero hits**, which is what the decision-13 correction rests on; that decision 44c says what
it is cited for; and that the three decisions were amended **in the heading as well as the
body**. Its sub-threshold observation, which it declined to file and was right to: the new
refusal's second remedy is one step short in exactly the way `api/015` fixed for the
retirement message — a `static` project setting only `default_snippets` that follows the
advice literally lands on `has no west_binary`, then `has no build_dir_root`, in the next arm
of the same `validate()`. **Advice that is correct and incomplete is a refinement gap, not a
contradiction** — decision 53 and reversals row 52 cover advice that re-proposes a schema
another decision forbids, advice with **no** completion. **`tasks/api/018`'s `Must not
delete:` already asserts, slightly too strongly, that this remedy "stops a reader landing in
the next branch of the same check", so the overclaim is written down and should be corrected
by whoever takes 018.**
**Reviewer:** no findings. — `umbrella/007`. It confirmed the deletion took nothing
(`count_valid_targets` has zero remaining callers; `looks_zephyr_west_shaped` still called
from `src/init.rs:382`) and found the one real widening and judged it harmless: `BoardYml.board`
went from a typed `BoardSection` to `serde_yaml::Value`, so a `board:` key holding a scalar or
null now counts as shape where it used to fail deserialization — nothing in decision 17 pins
that, and the new test `a_yaml_file_without_a_board_key_is_not_a_board` guards the case that
matters. Three things it raised that are not findings and that the next leg should carry:
(1) **the worker rewrote decision 26, which was this same leg's own first unit, two hours
earlier** — correctly, since 26 cited "17's amendment, which is itself unbuilt" twice and both
clauses went false the moment this landed; the reviewer verified the replacement against
`embarch-api/src/resolve.rs:454` and `src/zephyr.rs:171` and **caught one clause that
overstates** (the listing *does* emit `snippets_by_app`, `default_snippets` and
`default_extra_args`; what it never sees is a particular call's selection). (2) **A tension
inside a deferred feature nobody would meet until they built it:** `embarch-api` decision 19
says pre-`target.json` and pre-FNV directories are off-limits to `--prune` *because they still
belong to a valid target*, while umbrella 26 now reads as though publishing `build_dir_name`
were sufficient — a name-set-complement prune built on it would delete exactly those
directories. Nothing is wrong today; **anyone who picks up `--prune` needs to read both
entries, not one.** (3) **`tasks/umbrella/009`'s `Must not delete:` clause protects a table by
a *count*, and the count's referent moved** — before this unit the unbuilt set was
{22(a-c), 27/29, 17's amendment}; now `open.md` says {22(a-c), 27/29} and `009`/`016` say
{22(a-c), 26's `--prune`}. Still two, **but two of a different list**. Same defect shape as
`umbrella/015`'s `no-cli`: a stable name over a moved referent.
**Reviewer:** no findings. — `umbrella/015`. **It did the check the supervisor most wanted and
could not have done cheaply**: it extracted decisions 23 and 40 out of `3f4078a^`'s
`doctor.md` and diffed them byte-for-byte against the new `mcp.md`, which is the only way
"moved verbatim" is a fact rather than a claim. Decision 23 is byte-identical *including* its
amendment tombstone; decision 40 differs by exactly the two changes the commit message
declares — **plus one half-clause the commit did not mention**, a descriptive "readable yet
unspawnable" phrase about a remote-transport entry. The reviewer checked that conclusion and
reason both survive and that the clause is not on `016`'s `Must not delete:` list, and
declined to file it; it is recorded here because "compaction dropped something nobody listed"
is exactly the failure that leaves no trace. One thing it put below its own reporting bar:
**`decisions/reporting.md`'s header still says "entries moved verbatim" while this unit then
rewrote decision 37 in it** — it describes the split event rather than the file's state, the
same shape as the defect this unit fixed, one level up.
**Reviewer:** no findings. — `umbrella/013`. **And it did the one thing the worker could not.**
The worker verified umbrella's new claim about `embarch-api` against `embarch-api`'s own
landed decision entry and interface doc, which is all it was allowed to do; the reviewer went
to the shipped source at `embarch-api` tip `ab51bd1`, read `src/resolve.rs:415` and
`write_target_manifest` in `src/build.rs:302`, and reports the nine-field descriptor
**byte-accurate rather than approximated** — a cross-repo check nothing else in the pipeline
performs. It listed what it did not verify, unprompted.
**Reviewer:** no findings. — `umbrella/011`. It confirmed decision 23's amendment keeps both
halves, that `find_registration` matches the documented lookup order and is pure over a
`serde_json::Value`, and that all six codes decision 37 names are still emitted. **It said
what it left unverified** — no build, no test run, several decision files grepped rather than
read — which is the first reviewer in this tally to do that unprompted. Two asides, both
filed: **`judge_mcp` emits a seventh code, `no-handshake`, that decision 37's list omits**,
pre-existing since `4e48c77`; and the stale-working-tree defect that became `tasks/doc/010`.
A third, the supervisor's own from reading the merge result: **`no-cli` survived with a
changed meaning** — it used to mean *the `claude` binary is not on `PATH`*, and after decision
40 the check never looks for that binary and the code is emitted for *"no agent-CLI config to
read"*. Nothing is wrong today because check 10 is `code`'s only real consumer, but decision
37's entire argument for the field is that a consumer may match on a code *because* it is
stable, and **a code whose referent moves under a stable name is the one way that promise
breaks silently** — invisible to every check in the gate.
**Reviewer:** no findings. — `api/014`. It **recomputed all four pinned literals
independently** rather than trusting the test, confirmed the FNV constants and the length
prefix, so the pinning test pins rather than being tautological. It checked the orphaning
claim against `embarch-umbrella` decision 26 and found it forward-looking but not
contradictory, and confirmed `interfaces/config.md` stays true because it says only "hashed"
and never names the algorithm. **It declined to run `cargo test`** because it had been asked
for the verdict immediately, and said so — the literals were checked by recomputation
instead, which is the stronger check.
**Reviewer:** no findings. — `umbrella/012`. It verified decision 11 byte-identical across the
move and 37's body byte-identical plus the append, that `decisions.md`'s index carries both
files with the right number sets, that nothing still cites 11/37/39 as living in `doctor.md`,
that `path` does not contradict 37's "the key is always present … every existing consumer
keeps working" binding clause, and that both `spec.md` deletions preserve their facts
elsewhere. **One quality defect landed and was not reverted:** decision 37's **body** still
reads "Check 10 is the only user today", corrected by a **`Users, 2026-09-05:` line appended
four paragraphs below** — an append contradicting an unedited body sentence, the shape
`DOC-PROTOCOL.md` §4 says not to write. The worker flagged it itself and left it rather than
making a third commit from a second agent on a branch its author considered finished, which
is precisely the collision it had just stopped to avoid. Filed as `tasks/umbrella/015` with
the real fix named: **not "update the count", which resets the same clock, but delete the
roster from the body and cite `spec.md`'s table.**
**Reviewer:** no findings. — `api/012`. It verified decision 30 byte-identical across the
move, decision 51's new pointer against `shape.md` 53 and reversals row 52, all four
`Must not delete:` clauses byte-identical, and the `build_cwd` qualifier against
`config.rs:198-209` and `resolve.rs:155/400`. Two things it looked at and declined to call
findings, recorded because a future pass will meet them: **`spec.md` §4's shortened "no UNC
path is computed anywhere any more" reads more absolutely than what it replaced** (but
`decisions/core-link.md` 15 says the same, so nothing standing is contradicted), and
**`spec.md` §1 lost its `decisions/surface.md` 52 citation** — a dropped pointer, not a
changed claim.
**Reviewer:** skipped (leg ending at its unit cap — a reviewer spawned on the last unit would
outlive the leg meant to read its finding). — `umbrella/010`. The supervisor read the code
diff itself, which is how the whitespace defect below was found, and that is not a substitute.
**Reviewer:** skipped (leg ending at its unit cap — `umbrella/010` is the last unit and a
reviewer spawned here would outlive the leg meant to read its finding). — `api/015`. The
supervisor read the diff itself, which is not a substitute.
**Reviewer:** no findings. — `api/013`.
**Reviewer:** no findings. — `umbrella/006`.
**Reviewer:** skipped (a `suite` unit has no worker branch, and the diff is the supervisor's
own — a reviewer given those SHAs would be reviewing the supervisor, which is what this log is
for). — `suite/003`. Same reason `suite/001` skipped.
**Reviewer:** skipped (leg ending at its unit cap — `suite/003` is the last unit and a
reviewer spawned here would outlive the leg meant to read its finding). — `api/011`. The
supervisor read the diff before merging because it changes both front-ends' error path,
§10's judgement call and not a substitute.
**Reviewer:** 1 finding — `inbox/api-retired-targets-error-tells-a-zephyr-project-to-store-what-decision-12-forbids.md`.
— **this is `api/010`'s reviewer, reported after that unit's fold and recorded against
`umbrella/005`**, the same §10/§11 ordering gap `core/003` hit on 2026-09-04. **It is the
first real finding any reviewer has produced in this log**, and it became `api/015`, the
fleet's first review-driven unit. What it found: decision 53's new `bail!` sits *above* the
`match project.discovery`, so a **`zephyr-west`** project carrying retired rows is told to
"Declare one `[[projects]]` entry per target instead, each with its own
name/build_command/chip/artifact_path" — advice the same `validate()` **refuses thirty lines
later**, and which is the exact snapshotted static schema decision 12 exists to prevent.
**Message-only; a revert is the wrong remedy.** The commit's own zephyr-west test asserts only
`contains("retired")`, so **the gate is structurally blind to it**, which is why nothing else
would ever have caught this. Two more things it established: `decisions/zephyr.md`'s 96 B was
real (12192/12288) so decision 53 genuinely could not go there — **but decision 51 was not
amended to point at 53, and a pointer would have fit inside the 96 B**, so a reader loading
`zephyr.md` for the static-project mission reads 51 and sees no sign the menu is gone; and the
losslessness claim **holds** across ten files plus `embarch-umbrella`'s two `list-targets`
references. It judged decision 12 needs no tombstone and no reversals row is owed, and the
supervisor agreed with all three.
**Reviewer:** spawned at merge on both SHAs; **result recorded in the next unit's entry.** —
`api/010`. Same deviation `core/003` hit and for the same structural reason: §10 says spawn at
merge and do not wait, §11 says the entry ships in the fold commit, and those cannot both hold
for a reviewer slower than the fold. The supervisor chose "landed implies logged". See the
`umbrella/005` line above for the result.
**Reviewer:** no findings — and it earned its spawn here more than on either other unit,
because this was the one that *changed a decision's premise*. — `api/009`. It confirmed the
correction is written into decision 21's own entry with the original wrong clause **left
standing and the correction appended** (§5.4's licence) rather than silently edited away, and
that no reversals row was added — correct, since §3 gives a worker `never` on
`embarch-decision-reversals.md`. It **checked the build-directory correction against the code
rather than the worker's word**. Two things it raised that are not findings, written into
`embarch-api/open.md` rather than lost: the new collision error tells a caller to "omit
`snippets` to take the project's configured `default_snippets`" while `Config::validate` in
the same commit makes a `default_snippets` containing `"none"` a load error — **advice that
cannot be followed**; and the load-time refusal is **asymmetric**, `default_target` failing at
load on a `static` project while `default_snippets`, `default_extra_args` and
`soc_chip_overrides` are equally unhonourable there and still load silently — reversals
shape 7, "a rule that exists in some of the places it applies".
**Reviewer:** no findings. Ran in about three minutes against a twenty-six minute worker. —
`ui/001`, and worth recording *what* it checked, because it is the first reviewer in the tally
that had a real chance of finding something: it verified against **reversal row 100** (the
lower-bound-plus-one-step-back defect) that the new binary search had not silently
re-introduced a fixed bug, confirmed the retained JavaScript reference is deliberately naive
so the production search is under test rather than restated by itself, and independently
checked that nothing anywhere consumes `lane.spans` before agreeing the field could stop being
serialized.

**Day's tally: the log's running count reached 17 ran, 16 no findings, 1 finding** by the last
unit — that count is cumulative from 2026-09-04, not this day's alone. Four of this day's
twenty were **skipped**, all four for the unit-cap reason or because a `suite` unit has no
worker branch; none for budget. **Leg 012 skipped none of its four**, including the last,
waiting the two-to-three minutes each took against workers taking ten to fourteen, on the
grounds that the tally is the only evidence that will settle whether the pass earns its cost.
**On that leg it earned it twice, and neither time through its verdict — both were asides in
reviews that returned "no findings."** That is the pattern of the whole day: **the reviewer's
value is in what it notices beside the diff, not in the verdict**, and the two most valuable
observations of the day (`umbrella/017`'s pair) are still unfiled.

**One process defect of the supervisor's own, recorded because nothing else would catch it.**
Leg 011 wrote the `**Reviewer:**` line into **both** of its first two entries *before the
reviewer had reported* — and for `api/013` had not even spawned one when it wrote "no
findings". It noticed on `umbrella/006`'s reviewer returning, spawned `api/013`'s immediately,
and both came back **no findings**, so the two entries are factually true. **They were true by
luck, not by process.** §10 says "no findings" and "no reviewer ran" are different facts, and
a supervisor writing the line from expectation silently corrupts exactly the tally this log
exists to keep. The fold order makes it easy to get wrong — the entry goes *in* the fold
commit, which lands before a ~90-second reviewer can report — and the honest options are to
spawn the reviewer before writing the entry, or to write "pending" and never leave it.

### Hardware debts

**No board, no probe, no DUT and no live Core was touched all day.** Nine verification debts
were collected and **not one of them needs a board**; six of them are discharged by **live
runs on machines**, and two of those machines are different from each other.

**Hardware debts:** one, and it is new. **Check 17 has never met a real narrow-bound Core.**
This bench registers `--bind 0.0.0.0`, so the check passes here by agreement rather than by
discriminating anything. Settling it needs a Core deliberately installed `--bind 127.0.0.1` on
a `wsl-host` machine. **Read `umbrella/017`'s reviewer observation 2 above before planning that
session** — half the plan written into `embarch-umbrella/open.md` is unfalsifiable, and only
the `bound-narrow` arm is settled by it. (`umbrella/017`)

**Hardware debts:** one, and the worker asked for it to be read as red. **The shell-out has
never run against a real `embarch-api`** — 6 new unit tests against injected exit codes and
stdout only; the flag ordering (`--config`/`--json` *before* the subcommand, which is check
11's documented clap trap) and the `{success, targets}` shape are read off `embarch-api`'s
source, **not observed**. It is not hardware: one `embarch doctor --json` in an attended
session settles it. **Prediction written before the run, which is what makes it diagnostic:**
on this machine check 8 **warns** with `embarch-api not located`, because check 1 does not
locate that binary here. Carried in `embarch-umbrella/open.md`. (`umbrella/007`)

**Hardware debts:** one, riding on the live `embarch doctor` already owed. **Nothing in this
unit ran against the owner's machine** — no `claude mcp get`, no MCP spawn, no live Core, by
the supervisor's instruction. The task file carries the prediction written before the run:
from a terminal in a repo carrying the registration, `[10] PASS … registered as \`embarch-api\`
(local scope), and it answered initialize` with `code == "handshake-ok"`,
**and `unreadable-entry` should now be unreachable on that machine** — if it appears it means a
genuinely malformed or remote entry, not that the parse is wrong again. That last clause is
what makes the run diagnostic rather than merely confirmatory. (`umbrella/011`)

**Hardware debts:** one, and it rides free. Not a board — a **live `embarch doctor` on the
owner's machine**, where Core is the Windows service and this binary runs under WSL2. Nothing
under test ever resolves a real data directory, by design, so `wsl-host` is the one arm units
cannot reach. Written into `tasks/umbrella/012` with the exact expected line —
`[16] PASS … study_results/ at /mnt/c/ProgramData/embarch/study_results: 50 entries,
809.0 MiB …` — and `embarch doctor --json | jq '.checks[15].path'` giving that same string with
every other check's `.path` null. **The `%ProgramData%` sentence should not appear there;
seeing it would mean the hardcoded path is wrong**, which is the finding it exists to produce.
(`umbrella/012`)

**Hardware debts:** **one, and it is a machine rather than a board.** Nothing ran against a
live Core or a real DUT capture: deploy the UI, open the Trace tab on a real recorded study's
outpost tap, and confirm first paint, a wheel zoom and a drag pan against a capture *Core*
rendered rather than one this task generated. The numbers in decision 18 are the synthetic
capture's and are labelled as such; the feature row says `local`, not `hw`. (`ui/001`)

**Three more that the day's own entries wrote with the field bolded past the colon**
(`**Hardware debts: …**`), which is why the fold's ledger cannot see them — carried here so
they are not lost:

- **`umbrella/010`: one, and it is free.** The `sc.exe qc com.embarch.core` shell-out has never
  run inside `doctor` on the live machine; only its parse is unit-tested. **The owner's next
  live `embarch doctor`, already owed for checks 11, 15 and 16, discharges it at no extra
  cost.** Predictions written before the run: check 1 **PASS** naming
  `/mnt/c/Users/tmp12/embarch-setup/embarch-0.1.0-x86_64-pc-windows-msvc/embarch-core.exe`, and
  check 14 a real per-family PASS/FAIL rather than a WARN mentioning `sc.exe qc`. **A `WARN
  core-not-local` on check 1 instead means layer (a) missed and layer (b) caught it — the
  honest degraded state, not a regression.**
- **`umbrella/006`: one, and it is the reason that task was `verify-only`.** The Fail branch has
  never met a real permission-denied probe. Settling it needs a **Linux machine running
  `embarch-core` natively** (class `local` — the primary `wsl-host` topology skips the scan by
  design and cannot exercise it at all), with a debug probe attached and its udev rules
  removed, where `embarch doctor` should read check 5 as **Fail** / `probe-not-permitted`
  naming the probe by product string and vendor ID, and **Warn** / `no-probe-found` once the
  rules are restored and the probe is unplugged. **This is a different machine from the one
  that owes the live `embarch doctor`** — that one is `wsl-host` and cannot discharge this.
- **`umbrella/005`: none in the hardware sense, but one verification debt and it is a live
  install rather than a board.** Check 16 has never resolved a real data directory, so nothing
  shows whether `setup::data_dir_for(WslHost, false)` lands on the Windows Core's
  `study_results/` from WSL2. It is the **same `embarch doctor` run** already owed for checks
  11 and 15 — **one run on the real machine now discharges four things.**

**Not hardware and not to be lost:** `api/013`'s worker was explicit that a real `west build -d`
is unaffected and **correctly declined to call that a hardware debt** — no board is involved,
no Zephyr workspace is reachable from the worktree, the write lands after west has already run
and creates nothing west could trip over, and the two `run_build` end-to-end tests are
`#[cfg(unix)]`, matching that file's pre-existing platform gap. `api/017`'s one cross-repo fact
was settled by reading `embarch-core`'s source. `umbrella/015` records **none new** — decision
40 still carries `Unverified live` and that debt is `umbrella/011`'s, unchanged.

### Doc-size reserve, across the day

**The day opened with four files in reserve across two sub-projects, hit `nothing in the suite
in reserve` twice, and closed with three — one of them the undispatchable `suite/features.md`.**
The mechanism worked, and it worked because `DOC-COMPACTION.md` §2's **ride-along rule** got
its first real test on `umbrella/006` and passed: one commit, `de8a381`, carrying both the
change and the shortening, `embarch-umbrella/spec.md` **10,089 → 9,131 B** (98.5% → 89.2%).
Leg 010's final entry had predicted the opposite — "the next umbrella worker will meet the wall
the reserve was designed to replace, and it will meet it mid-task" — and it did not, **because
the rule that arrived the same day put the compaction in the hands of the actor making the
flux.** Five more ride-alongs followed (`api/013`, `umbrella/012`, `umbrella/015`,
`umbrella/007`, `api/017`) and all five paid.

Three things about the mechanism that are worth more than the byte counts:

- **A doc split beats a squeeze, and verbatim is what makes it legal.** `umbrella/012` moved
  decisions 11/37/39 into a new `decisions/reporting.md`, `umbrella/015` moved 23/40 into a new
  `decisions/mcp.md`, `api/012` moved decision 30 into `decisions/shape.md`, all **verbatim** —
  and a verbatim move restates nothing, so the `In flux: yes` objection that parks a compaction
  task does not reach it. That is the instrument §2–§3 prefer, and it is why
  `tasks/umbrella/009` could stay parked while its files came back under.
- **A ride-along makes "what did this commit delete" a question no single diff answers.**
  `umbrella/015`'s reviewer had to byte-diff across a file boundary to establish the move was
  verbatim, and **found one unmentioned dropped clause while doing it.** That cost is not
  written down anywhere in §2.
- **A unit that compacts a file changes the reserve line quoted in every *other* task file, and
  nothing propagates that.** `umbrella/006`'s worker rewrote `tasks/umbrella/007`'s `Compacts:`
  block because the dispatch had baked "151 B left" into it and its own change made that false.
  The content was right and it was let stand — but **the staleness was created by the ride-along
  rule itself**, which is a structural consequence of §2 worth watching, not a worker defect.

**State at the end of the day, which is what the next leg walks into:** `suite/features.md`
**19,517 / 20,480 B (95.3%)**, `embarch-umbrella/open.md` **94.5%** (filed, `tasks/umbrella/009`),
`embarch-decision-reversals.md` **90.9%** (filed, `tasks/suite/004`). **`api` has nothing in
reserve for the first time since `api/012` — but `decisions/zephyr.md` finished at 10,962 /
12,288 B (89.2%)**, the same 89.2% it went in at, with the tombstone's argument having spent the
slack. **Nothing is filed against it and nothing may be** (§5 forbids filing against a file not
in reserve), so `tasks/api/019` carries the warning in its own `## Reserve` section instead.
**`tasks/umbrella/016` is now fully paid** — `umbrella/015` closed its `decisions/doctor.md`
item (11,918 → 7,774 B, 97% → 63%) and `umbrella/007` closed its `spec.md` item (9,286 → 9,014
B, 88.0%) — **and should be closed by the next leg.**

Two moments the mechanism nearly failed and did not: **`api/010` is the first time in this log
that a doc-size cap moved a decision rather than merely shortening one** — decision 53 is
build-orchestration and belongs in `decisions/zephyr.md`, which had 96 B and physically could
not take an entry, so it went into `decisions/shape.md` framed as a scope decision. The framing
is honest and a reader looking in the obvious file will still not find it. And `api/015`'s
worker **measured twice**: its first pass put `interfaces/config.md` at 11,078 B (90.2%), back
into reserve one unit after `api/013` paid it out; it noticed, **shortened the
`[[projects.targets]]` row instead of appending to it**, and committed at 11,040 B (89.8%).

**`DOC-COMPACTION-PASS.md`'s human question was answered twice in the compactors' own words,
and both answers argue from what a reader gains rather than from bytes.** `api/012`: *yes for
changing `embarch-api`, no for calling it* — what left was surface description
`interfaces/config.md` already carried in fuller form; what stayed is every claim a reader
would get *wrong* by not knowing it. **The honest residual, reached independently by worker and
reviewer: `spec.md` names no tool at all**, so an agent asking "what can this crate do" gets a
description of a build orchestrator and no list of what it orchestrates — not closeable inside
a 10 KB role cap. `umbrella/007`: *yes, and better than before* — and **the one place the file
got denser rather than shorter is check 8's row**, which now states an outcome it did not have
(warn where it cannot ask), so a reader of `spec.md` alone learns check 8 depends on locating
`embarch-api`, which is a thing they can trip over.

### Queue and reconciliation

- **The queue hit zero twice and was refilled twice out of `open.md`.** `api/016` and
  `umbrella/017` are the first tasks a leg wrote for itself, both swept out of their
  sub-project's `open.md`. Leg 013's wave was **unusable for three of its four units** — all
  dispatchable tasks were `umbrella`, and §6 allows one task per sub-project in flight, so it
  ran serially at half the permitted concurrency however healthy the budget was. It used the
  full wave exactly once (`umbrella/007` beside `api/016`) and only because a refill sweep
  produced an `api` task.
- **Open, `Owner: required`, none of them a leg's to fix:** `tasks/doc/002` (the
  `features.d/` → `suite/features.md` gate contradiction), `tasks/doc/007` (the fold had no
  mechanism a leg was allowed to use — now solved by `fold-day.py`), `tasks/doc/009` (double
  dispatch), `tasks/doc/010` (reviewer reads a stale tree), `tasks/doc/011`
  (`scripts/check-doc-size.py` cites `DOC-COMPACTION.md` §6–§9 three times, at lines 29, 119 and
  226, while line 99 correctly names the split — **the enforcement script misquoting the
  protocol it enforces**), `tasks/suite/004` (the assembled-file cap). **And a citation the
  fleet's own worker-dispatch template still gets wrong:** `DOC-COMPACTION.md` **§7 does not
  exist** — that doc has five sections, §6–§9 moved to `DOC-COMPACTION-PASS.md` on 2026-09-04 —
  and **the copy in the template is owner-reserved and stays wrong until he fixes it**, invisible
  to the worker, which cannot see where its instructions came from.
- **Newly filed and dispatchable:** `tasks/api/018` (compaction — **closed and `git rm`ed by
  `api/017`**), `tasks/api/019`, `tasks/core/004`, `tasks/umbrella/015` (**landed**),
  `tasks/umbrella/016` (**fully paid, close it**), `tasks/umbrella/013` (**landed**).
  `tasks/umbrella/009` remains parked, correctly, `In flux: yes`.
- **`tasks/api/012` was re-blocked by the supervisor after a worker unblocked it, and the worker
  was right on everything it could see.** It moved 012 to `open` on the correct ground that
  `tasks/api/010` had landed. **What it could not see is that three `api` tasks had been drained
  out of `inbox/` twenty minutes earlier in the same leg**, two of which put back in motion
  exactly what 012 compacts. `supervise.md` is explicit that an `open` task saying `In flux: yes`
  is the filer getting it wrong and that the fix is the state, not a worker — this is that, with
  the supervisor as the filer who created the flux. It was later unparked **by the owner**, by
  narrowing, which is the move leg 012 recommended and leg 013 deliberately declined to repeat
  for `umbrella/016` (both of 016's files were in flux from leg 013's own queue, so it **split
  `016` across the two units already spending its reserve** instead).
- **A worker's reasonable deviation inside `tasks/` had to be adjudicated after the fact on
  three legs running** (`api/012`'s path on leg 009, `api/012`'s state on leg 011,
  `tasks/umbrella/007`'s `Compacts:` block on leg 011). **The pattern is a worker having better
  information than the queue and no sanctioned way to write it down.**
- **Four `done` task files** (`api/012`, `api/014`, `umbrella/011`, `umbrella/012`) were still
  sitting in `tasks/`, never `git rm`'d by the legs that finished them. **`fold-commit.py` does
  not delete a `done` task file for you** — the log has said so since leg 008 and it keeps
  happening. Cleared by leg 013 in a separate commit so the fold stayed exactly its unit's paths.
- **Fifteen `changelog.d` fragments are pending on `main` and they are not the fleet's.** They
  are the owner's, committed by his own 2026-09-05 sessions (`3f47a61`, `de07c82` and others) and
  never assembled. **`build_changelog.py` is all-or-nothing** — running it consumed all sixteen
  and rewrote five `history/` files; `fold-commit.py` **refused the resulting path list,
  correctly and by design**, which is the second time that guard has fired on something real.
  The leg reverted, moved the fifteen aside, assembled only its own fragment, and put them back
  untouched. **They are still sitting in `changelog.d/` waiting for their author. A leg cannot
  fold them and should not try.**
- **Housekeeping:** `fold-day.py --roll` moved `2026-09-03` into `log-archive/`
  (114,946 → 96,795 B) during leg 012.

### Five mechanism defects the day surfaced, all in the supervisor's own hands

1. **A pipeline swallows the gate's exit status, and one fold committed over a RED gate.**
   `python3 scripts/check-docs.py 2>&1 | tail -2 && python3 scripts/fold-commit.py …` — a
   pipeline's status is `tail`'s, which is always 0. The gate printed `1 of 9 checks RED:
   check-doc-size.py` and `fold-commit.py` ran anyway. Caught by reading the output, cause
   fixed and commit amended before pushing, so nothing red reached `origin`. **`supervise.md`
   tells a leg to run the wrapper rather than a list of its own; it does not say not to pipe
   it. Run it bare, or the "one command" discipline buys nothing.** This is the second time in
   this log that a *convenience* around the gate — not the gate — was the failure.
2. **Pass `fold-commit.py` explicit file paths, never a directory.** `--path changelog.d` as a
   directory is how eight drained fragments that were not the unit's would have ridden in
   unnoticed; the fold **refused it by name** rather than staging it, the first time that guard
   fired.
3. **`check-staleness.py` cannot fire until the supervisor assembles, so a worker can leave a
   false positive it had no seat to see.** `umbrella/017` rewrote a `doctor` row to say a
   sub-row "is **design-only**", and `design-only` is one of `STALE_FEATURE_WORDS`, so the check
   read the *row's own status* as design-only while `spec.md` names the shipped command. Fixed
   by rewording to "designed and unbuilt" — same fact, no trigger word. **The fragment was
   `umbrella`'s and it landed in `api/017`'s fold purely because the assembler runs per fold and
   not per merge.**
4. **`check-ownership.py` prefers the worktree's local `main`, and a stale one produces a red on
   paths the worker never wrote.** Local `main` sat at `180c2be` while the branch was cut from
   `origin/main` at `17c4669`, so the default-base check swept in the leg's *other* claim. The
   worker reported it rather than waving it through and proved itself green against both
   `--base origin/main` and `--base 17c4669`. **One claim per commit is not enough on its own —
   the worktree's local `main` must also be fetched at setup.** Leg-008's defect in a new dress,
   third leg running, and the fix is in `scripts/`.
5. **A worker's dependency closure, not its own `Cargo.toml`.** The `embarch-api` code worktree
   was missing `../embarch-topology` — `embarch-core-client` path-depends on it, so `cargo
   build` failed outright before compiling anything; same for `embarch-ui`. **Both workers
   created the symlink themselves and left it in place.** `supervise.md`'s setup step names two
   siblings by example; **the real rule is *every* sibling in the dependency closure.**

**And one defect nothing mechanical could ever have caught, worth the line:** `umbrella/010`'s
new check-14 skip message carried **eighteen stray spaces** in the middle of its string literal
— a wrapped source line written into a single-line `&str` — so it would have printed *"registered
as the⎵⎵…⎵⎵Windows service"*. It is valid Rust and the test asserts `contains("sc.exe qc")` and
passes either way. The supervisor fixed it in scope as `embarch-umbrella` **`81e20f4`**. **Read
the strings, not just the diff** — it was the user-facing text of the check whose entire point
in that unit was that its message stops saying "see check 1".

### Budget

**DEGRADED at the start and end of every leg, wave 2 throughout, and no 429 anywhere in the
entire day** — five legs, twenty units. The wave was the binding constraint only through the
queue's shape, never through the budget: leg 013 ran three of four units serially because every
dispatchable task was `umbrella`.

### Least sure about

Twenty standing doubts, one per unit; these are the seven that are still live:

- **Merging check 17 when the reviewer had just shown that one of its two Fail arms cannot
  discriminate and its fix line can green itself** (`umbrella/017`). Merged because the arm that
  *does* discriminate is sound and a check right in one arm beats the vacuous check it replaced
  — **but "over-claiming" is the exact failure decision 22's own prose says a check must not
  have, and the honest sequencing would have been to hold the merge and hand the observation
  back to the same worker while it still had the context.**
- **Merging a breaking config change unattended** (`api/016`). The one config on this machine
  was verified and survives, the failure mode is loud rather than silent — but **"the one config
  I can see still loads" is not "no config breaks"**, there is no inventory of `embarch-api`
  configs anywhere, and the operator most likely to meet it is running an MCP server whose
  stderr nobody reads, **which is the same property the worker used to argue against warning.**
- **Letting a worker rewrite a decision another unit of the same leg had edited two hours
  earlier, and finding out only from its report** (`umbrella/007`). It was right to do it and
  the reviewer confirmed the new claim against source. But **nothing in the dispatch told either
  worker the other existed**, and the second happened to notice 26 had gone false; had it not,
  the leg would have landed a unit that made its own earlier unit's edit wrong, **and the
  reviewer reads one diff at a time.**
- **Whether `c54d5f0` was really identical before the force-push** (`umbrella/012`). The "empty
  diff" claim rests on the second worker's own `git diff c54d5f0 d9844dd`, and after the
  force-push `c54d5f0` is an unreferenced object nobody re-verified. **If that diff was not
  actually empty, the difference is now only in a dangling object in
  `/home/gabriel/Github/embarch/.worktrees/embarch-umbrella/012-check-16-names-dir`'s reflog, and
  it will be gone at the next `gc`. A leg that wants to check this has hours, not days.**
- **Whether folding `api/012` at all was right**, given the branch was written by a worker
  already declared dead and dispatched over. Green three times independently — by its author, by
  the worker that stood down, and on the merge result — but **"three green gates" is a statement
  about the content**, and what cannot be ruled out from here is whether any byte in `a7ec7d0`
  came from the second worker's two failed edits. It reports writing nothing and both attempts
  failed on `old_string` mismatch, **which means relying on a worker's self-report for a fact
  with no independent check.**
- **The `TopologyClass::Local` gate on the probe scan** (`umbrella/006`) — right for the verdict,
  but it means **the branch decision 18 asked for is unreachable on the only topology this suite
  is actually used on**, and its hardware debt is therefore owed against a machine that does not
  currently exist in the owner's setup. What makes it better than the warn it replaced is
  `--json`'s `code`, which is a thinner win than the diff looks.
- **`api/015`'s reversals placement.** The defect went into the **review-driven** section rather
  than as numbered row 110, because that page's standing rule is that a numbered row "was caught
  by a real build, install, capture, or by reading a real repo's actual files — **never by
  inspection alone**", and a reviewer reading a diff is inspection. **The section is
  lower-signal by its own header and this defect is not** — it is a shipped error message
  telling a user to build the exact thing the suite retired. The alternative was breaking a
  range-file boundary unattended: **row 109 is the last number and the range files stop at
  `rows-93-109.md`**, so a row 110 needs a rename or a new file, which is a structural call about
  a reserved-adjacent doc. The reversible mistake was chosen over the structural one, **and that
  boundary is still there for the next unit that owes a row.**

Also carried, because it is a fact about the mechanism rather than about a unit: **`ui/001`
recorded three worker-visible instances in one leg of a single root cause — a gate half that
tells a worker to write a file the ownership half refuses** — and `protocol.md` §6 obliged
saying so loudly. Two of the three (`features.d/` → `suite/features.md`, the compaction debt's
path) are `tasks/doc/002`. **None of it blocked anything, because the fold is where both resolve
and the supervisor's hands are allowed there. That is exactly what makes it dangerous: a red
every unit of a shape produces is a red that stops being read**, which is the risk §10 names
about this check being a merge gate. And **"the gate satisfied by an argument rather than a
run"** appeared twice more this day (`suite/003`'s three markdown files, and every doc-only
unit's byte-identical code tree); each argument is sound, and this log has now flagged the shape
eight times.
## 2026-09-04 — 9 units

*Folded by leg 010 on 2026-09-05 at 12:10 MDT. **This fold was owed by the leg that ran
at 00:18 and never made** — §11 puts it on the first unit after local midnight, and the
file had reached 84 KB against a 25 KB roll line as a result. Nine per-unit entries
collapse here with every SHA, every debt and every `**Reviewer:**` line preserved — the
reviewer lines are kept one per unit and line-anchored so
`grep '^\*\*Reviewer:' supervisor-log.md` still tallies correctly. What is gone is the
narrative reasoning behind each accepted judgement; git holds it in `embarch-fleet`
`1dfbcbf` and earlier.*

**Legs 007, 008 and 009 all ran this day, and all three recorded "no Slack tool"
(`ops.md` §5.2a) — all three were wrong.** The connector arrives **deferred**: absent
from an agent's initial tool list, named only in a `system-reminder`, callable after
`ToolSearch` with `select:mcp__claude_ai_Slack__*`. Each leg read its tool list and
concluded it had no channel. Nothing in their entries about the control plane is
evidence of anything, and this is why `tasks/suite/003` sat unannounced for three legs.

### Decided

**The one suite-wide decision of the day is `suite/001`.** `embarch-umbrella` decisions
27/29 claimed every repo's release workflow asserts `Cargo.toml`'s version against its
pushed tag before building. **No repo did.** Four now do — a `verify-version` job the
build matrix `needs:`. Three sub-calls, recorded in the decision itself: **`awk` on
`Cargo.toml`, not `cargo metadata`** (three of the four manifests have sibling path
dependencies that only resolve once the other repos are checked out, and the point is to
fail *before* that setup, so `cargo metadata` would make the guard depend on the thing it
guards); **compare against `GITHUB_REF_NAME` with a leading `v` stripped**, passing on a
tag pushed without the prefix (the claim is that version and tag agree, not that the tag
is spelled a particular way); and **`workflow_dispatch` exits 0 with a printed reason**,
because the ref is then a branch with no tag to disagree with, and a silent pass would
read as a check that ran. Executed by the supervisor itself under §8. Its §4 window had
already been discharged by leg 006 (`ts 1788460873.097499`, zero replies, elapsed
13:11 MDT 2026-09-03) and was **not** re-announced and the clock **not** restarted —
that handoff worked exactly as §4 intends. **Four repos still have no release workflow at
all** (`embarch-study-designer`, `embarch-dev-bench`, `embarch-outpost`, `embarch-ui`),
so "every repo" now means every repo that releases, and whichever of those gains a
workflow inherits the obligation to copy the job — recorded in the decision, where
someone adding one will see it.

Everything else was sub-project-scoped and accepted from the worker. The five worth
carrying cold:

- **`umbrella/004`** — check 10 previously ran `claude mcp get embarch` and returned
  **Pass on a zero exit**, reporting "registered but broken" — the exact state it exists
  to catch — as healthy. It now spawns the registered command and does one JSON-RPC
  `initialize` over piped stdio, 10 s budget, kills the child either way, three
  distinguishable outcomes; new decision 37 explains the `code` field that keeps them
  distinguishable in `--json` without matching on prose. Two "cannot tell" states — no
  `claude` on `PATH`, and a registration whose output the parser cannot read — are
  **`Warn` rather than a verdict**, the same posture `umbrella/001` took on the check-11
  stub. A real bug its own test found: EPIPE was reported as `couldn't write to its
  stdin: Broken pipe` when the registered command died on its own arguments, naming the
  symptom while the exit code and stderr sat one line away, and flaking about 1 run in 30
  on which message appeared. EPIPE now falls through to the read loop, which sees EOF and
  reports the exit with stderr attached; 60 consecutive clean runs after.
- **`umbrella/008`** — check 11 stopped failing deploys on `embarch`'s own constant.
  `local_host` became `api_host: Result<u32, String>`, fallible and never defaulted, with
  not-located / clap-exited-2 / not-executable / answered-without-the-field each a
  distinct `Warn` naming which; a test pins that `core_host: Ok(16), api_host: Err(..)`
  is a **Warn** where `Ok(16)` vs `Ok(17)` is a **Fail**. `embarch`'s own constant
  survives as a fourth number that can only warn (decision 36). This is the fix for what
  leg 003 recorded as its own least-sure line.
- **`umbrella/003`** — the task file said `--dry-run` was "one flag and an early return
  away" **and it was wrong, which is the point**: `make_plan` did run every detection step
  before anything acted, but two of the three side effects — decision 28's binary copy and
  the `PATH` write — only ever printed *while* acting, because they post-date decision
  21's text. An early return would have printed a plan silently omitting the two steps a
  user most wants warned about, which `Done when` box 2 forbids. So `Locations` resolves
  the four writable paths once and a read-only `plan_install` describes the install from
  the **same `SUITE_BINARIES` constant, the same `paths_refer_to_the_same_file`, and the
  same sourcing-line predicate `install_into` uses**, so the description cannot drift from
  the act; one `apply_plan` walks both modes. `FoundBy::PendingInstall` exists so a dry
  run never claims `JustInstalled`, and `--dry-run` `conflicts_with = "uninstall"` rather
  than being silently ignored by it. **The test proves absence** —
  `a_dry_run_reaches_no_side_effecting_call` points every writable location at a sandbox
  and makes `embarch-core` a script that would leave a sentinel if it were ever executed,
  then asserts the sandbox untouched. The worker also ran the built binary as `embarch
  setup --dry-run --port 1`, port 1 chosen so nothing could reach the live Core, and
  md5-verified `~/.bashrc`, `~/.local/share/embarch` and `~/.config/embarch/umbrella.toml`
  byte-identical afterwards — a worker declining to touch a live service unasked.
- **`api/005`** — split the build-log cap head-and-tail (first 16 KB, last 48 KB, middle
  behind one marker), which decision 18 had always said and nobody had built; decision 18
  moved from `decisions/surface.md` to `decisions/zephyr.md` where build orchestration
  lives. **The cap bounds retained bytes, not each half**, so the split does not double a
  response an MCP client has to carry. The worker **refused to mark the `capture cap` row
  measured**: nothing has ever measured a real Zephyr failure's log, so the 1:3 split is
  reasoned, not sized, and `spec.md` now says so while decision 18 names the observation
  that would move the number. That is the opposite of this suite's usual failure, where a
  reasoned number ages into a measured-looking one. One piece of craft worth not
  re-deriving: a both-ends UTF-8 boundary test against a pure 3-byte fixture proves only
  half of what it claims — `OUTPUT_HEAD_BYTES` = 16384 ≡ 1 (mod 3) so the head offset
  always lands mid-character in a run of `'€'`, but 49152 ≡ 0 (mod 3) so the tail offset
  always lands *on* a boundary; the fixture appends one ASCII byte purely to shift it.
- **`api/008`** — the compaction line that now governs `api` docs: **a `decisions/` entry
  may state its own claim** (`DOC-COMPACTION.md` §5 — an entry that cannot state its claim
  is not readable alone) **but must not carry reference detail or the status of a gap**;
  those belong to `interfaces/` and `open.md`. Read the other way, an `interfaces/` file
  carries the rule a caller obeys, never the argument for it. Sixteen overlaps resolved by
  assignment, **one kept deliberately** — *"reflash means build and flash the tree as it
  stands, then verify"*, which `spec.md` §2 needs as an invariant for an agent that loads
  only `spec.md` and decision 40 needs as its own claim — with decision 40 now saying
  inline that the restatement is intentional, so the next reader of the advisory report
  finds the answer in the doc rather than in a task file that gets deleted in the fold.
  `check-duplication.py embarch-api`: 17 → 1, and the 1 is the one that is supposed to be
  there.

**Three compaction passes answered `DOC-COMPACTION.md` §7 in the compactor's own words,
and one answered no.** `core/003` said `embarch-core/spec.md` alone cannot tell you what
you need to work on Core today and structurally never could — Core is a 25-route service
whose route table is 10 KB in `interfaces.md`. What it *now* answers alone, and did not
before, is the narrower question: which module owns a thing, what must not be broken,
which constants are measured. Accepted, because an honest "no" beats a confident yes and
both files came out of reserve. `dev-bench/001` and `outpost/001` both answered yes, and
each named exactly what it removed: **how numbers were arrived at, not what they are**
(the ESP32-C5 SRAM percentage history, superseded frame bounds, the scan-table census)
while the live constraint stayed; and, for `outpost`, evidence for numbers that are not
`spec.md`'s own and now sit one file away next to the knob they set. `outpost` is the only
entry in `check-doc-size.py`'s `TIGHTENED` map, so §9 forbade it a second hot/cold pass and
it took the bytes from duplication and misplaced provenance instead. Both refused cuts on
principle: `outpost` kept the **anti-footgun clause of every invariant that has one**, on
the reasoning that a constraint's reason is hot precisely because a reader who does not
know it re-proposes the rejected fix; `dev-bench` brought its whole `Must not delete:` set
through untouched, including the six-part failure signature, the six short-by counts and
the 899,843 ms / 46,320 ms uptime pair.

### Merged

| Unit | Code | Doc |
|---|---|---|
| `agent/umbrella/004-doctor-mcp-handshake` | umbrella `69eb1f1` | doc `a6d0635` |
| `agent/dev-bench/001-compact-docs` | *doc-only — code branch carried no commits* | doc `d7d30f4` |
| `agent/outpost/001-compact-spec` | *doc-only — code branch carried no commits* | doc `3e5cdd3` |
| `agent/umbrella/003-setup-dry-run` | umbrella `23c9deb` | doc `a0319f9` |
| `agent/api/008-duplication-overlaps` | *doc-only — code branch carried no commits* | doc `9c4842b` |
| `agent/api/005-build-log-head-and-tail` | api `f1fe90e` | doc `5a6d319` |
| `agent/umbrella/008-check-11-reads-embarch-api-versions` | umbrella `535a2c4` | doc `dbd47f4` |
| `agent/core/003-compact-docs` | *doc-only — code branch carried no commits* | doc `6db0cc7` |
| `suite/001-release-tag-version-assertion` | umbrella `de8d81b`, core `a2706aa`, api `60abdcf`, topology `e1d9ff2` | folded in the same commit |

Every unit's gate was re-run by the supervisor **on the merge result, not on the branch**,
and every one was green: `cargo build` / `cargo test` / `clippy --all-targets -D warnings`
wherever there was Rust in the diff, the doc checks, and `check-ownership.py` on both
branches before either merged. **No native Windows build ran on any unit**, and that is
deliberate rather than skipped: `embarch-umbrella` shells out to `embarch-core` rather
than depending on it, so §10's Windows clause does not reach it — the reasoning
`umbrella/001` established, not a new one. The doc-only units ran no `cargo` at all
because the merge result's code tree was byte-identical to `main`.

### Blocked

**None, in any of the nine units.** No task went to `blocked` and no gate went red on a
merge result.

### Reviewer

**Reviewer:** no findings. — `umbrella/004`. It raised one thing that is *not* a finding
and is worth acting on: `parse_registered_command` reads `Command:` and `Args:` and
**ignores the `Environment:` block** that `claude mcp get`'s own sample output shows, so
check 10 spawns the server in *doctor's* environment rather than the registered one. It
contradicts nothing — decision 16's mirroring rule is scoped to token and config, and
decision 23 asks only for the registered *command* — but it is exactly the shape decision
16 is about, and it is now in `embarch-umbrella/open.md`.
**Reviewer:** skipped (budget DEGRADED, wave 2). — `dev-bench/001`
**Reviewer:** skipped (budget DEGRADED, wave 2). — `outpost/001`
**Reviewer:** skipped (budget DEGRADED, wave 2). — `umbrella/003`
**Reviewer:** no findings. — `api/008`, **the first reviewer ever to run**. It resolved
every claim the four shrinking files gave up against the file the diff says now owns it:
no decision entry lost its reason or its rejected alternative, `decisions/zephyr.md` 18
in fact *gained* an explicit *Rejected: a cap per half*, and it read the one narrowing
that changes a claim rather than moving it (`config.md`'s "every field is required" →
"none of the five board-identifying fields is defaulted") as a refinement matching
decision 45's own wording rather than a contradiction.
**Reviewer:** skipped (leg ending at its unit cap — a reviewer spawned there would
outlive the leg meant to read its finding). — `api/005`
**Reviewer:** skipped (budget DEGRADED, wave 2). — `umbrella/008`
**Reviewer:** no findings. — `core/003`. Spawned at merge and **reported after that
fold**, so it was recorded in `umbrella/008`'s entry instead; the tally undercounted by
this line until now. It confirmed all three `Must not delete:` items verbatim, all five
de-duplication moves carrying their claim in the surviving copy, none of the four "cold"
drops orphaning a decision, and — usefully — that `embarch-study-designer`'s citation of
`embarch-core/spec.md` **§5** still resolves, because only §7 was removed and §7 was
last, so §1–§6 never renumbered. **That is what narrows `tasks/suite/003` from a repair
to a clean structural move**, and makes it less urgent than its own text implies.
**Reviewer:** skipped (a `suite` unit has no worker branch, and the diff is the
supervisor's own — a reviewer given those SHAs would be reviewing the supervisor, which
is what this log is for). — `suite/001`

**Day's tally: 3 ran with no findings, 6 skipped**, five of the six for a DEGRADED wave
of 2. That is the cause that made the accumulate-twenty-entries plan unable to complete
under the rule governing it, and the reason §10 was amended so a reviewer no longer counts
against the worker wave. One process note kept because it cost a correction: `umbrella/004`
first wrote a fourth Reviewer form ("spawned on merge, did not count against the wave")
and amended it once the reviewer returned — **the fix is to spawn at merge and write the
line at fold time, never to invent a placeholder**, because `grep '^\*\*Reviewer:'` is the
tally and a fourth form breaks it.

### Hardware debts

**No board, no probe, no live Core, no DUT was touched all day.** Three verification debts
were collected and **not one of them needs a board**:

1. **One `embarch doctor` from an environment with the agent CLI installed and `embarch`
   registered.** **Nothing in this suite has ever seen `claude mcp get`'s output**, so the
   format `parse_registered_command` reads is assumed rather than measured — which is
   exactly why an unparsable entry is a `Warn`. The 10 s handshake budget is assumed too,
   against a real `embarch-api` cold start. Both in `embarch-umbrella/open.md`.
2. **One `embarch doctor` against the *installed* suite.** That the installed
   `embarch-api` answers `--json versions` with the field is unconfirmed — only fabricated
   binaries and a local debug build have been asked. It rides with the live-Core and
   flashed-bench debts already in `embarch-umbrella/open.md` from `umbrella/001`, and
   **one `embarch doctor` on the real machine discharges all three.**
3. **One `embarch setup --dry-run` on a real Windows box.** `plan_path`'s Windows arm and
   `windows_path::is_on_path` are `#[cfg(windows)]`, there is no Windows linker on this
   machine, and `clippy --all-targets` cannot reach them. **A machine, not a board.** It
   settles this *and* the identical gap decision 28 has carried for `ensure_path` since it
   was written — the suite now has **two** unbuilt Windows arms resting on one untested
   assumption instead of one. Recorded in the task file and in decision 21. Also
   unexercised, but nothing new is at risk there: the `wsl-host` and `remote` arms print
   identical text in both modes because they were already print-only.

Not hardware, and not to be lost: **`suite/001`'s `needs: verify-version` wiring is
checked structurally only** — parsed YAML, `build.needs == verify-version` in all four
repos. Its 16 scenario runs extracted the step's own `run:` block and executed it against
each repo's real `Cargo.toml` under four refs (matching tag, mismatched tag, tag without
the `v`, `workflow_dispatch` branch), every one as intended, mismatch exiting 1 with an
`::error::` line. That the job actually gates the matrix **will first be proven by a real
release**, and pushing a tag is the owner's under §2. Written into the task file and the
decision rather than letting "verified" stand unqualified.

### Doc-size reserve, across the day

**12 files in reserve at the start of the day, 6 at the end, every one filed at every
moment.** Paid off: `api/decisions/surface.md`, `api/open.md`, `core/spec.md`,
`core/open.md`, `outpost/spec.md`, and both `dev-bench` files. Went the other way and
stayed filed: `umbrella/spec.md`, 9527 → 9761 B, still against `tasks/umbrella/009`, which
stays `blocked` with `In flux: yes` — correctly, because five open `umbrella` tasks still
rewrite that doctor table.

**No worker ever hit `check-doc-size.py`'s reserve *failure***, because the gate fails only
on an *unfiled* file in reserve and everything in reserve was filed. The mechanism stayed
a debt notice rather than a wall, and **it has still never been tested by a worker meeting
an actual refusal.** `umbrella/003` came closest and is the interesting case: it sized
`decisions/install.md` to **11009 B against an 11059 B reserve line, deliberately**, so no
new compaction task was owed — a worker planning against the dispatch-time headroom line
rather than discovering it. `umbrella/008` likewise **split `decisions/doctor.md` rather
than compacting it** (decisions 24, 33, 34 and two new ones moved to
`decisions/schema-skew.md`, numbers unchanged and permanent, `decisions.md`'s index row
added) and filed no debt, correctly, because `open.md` came *out* of reserve in the same
pass.

Two forward-looking notes from the compactors, both still true: **`dev-bench/open.md` has
no second pass of that kind left in it** — all 17 bullets survive
`collect-open-questions.py`, diffed 17 in / 17 out and reworded only, and the 267 B came
entirely from mechanism clauses `decisions/` already owned, so a future pass would have to
drop whole items and name each as answered. And **`dev-bench/decisions/ble.md` is at
89.8%, 22 B from re-entering reserve on its next edit, with nothing filed against it** —
deliberately, because that pass *shrank* it and `tasks/README.md` files a debt against the
commit that spends the reserve. Also worth knowing generally: **a doc split creates
overlaps as a matter of course** — `api/008` was filed against 15 and the report said 17,
because `interfaces/modules.md` had been split out of `spec.md` §5 the same day and
carried two more claims with it.

### Queue reconciliation

- **`tasks/api/007-compact-docs.md` closed and deleted.** It was `blocked` on `api/005`
  landing and that landing **paid its whole debt** — `decisions/surface.md` 11305 →
  10928 B, `open.md` 4821 → 4560 B, `--pressure` saying `PAID` for each. A compaction task
  whose files are no longer in reserve is not a task.
- **Its non-size half survived as `tasks/api/008-duplication-overlaps.md`**, carrying
  `007`'s `Must not delete:` verbatim. `check-duplication.py` is advisory and in nobody's
  gate, so deleting `007` silently would have lost the finding for good.
- **`tasks/suite/003-core-spec-5-to-interfaces.md` was filed by `core/003`** — the one
  structural cut it could not make. `spec.md` §5's result-layout tree is a reference table
  that `DOC-COMPACTION.md` §9 puts in `interfaces/`, but `embarch-study-designer/spec.md`
  cites `embarch-core/spec.md` **§5 by section number**, `check-links.py` skips anchors and
  `check-decision-refs.py` only resolves decision numbers, so **nothing in the gate would
  catch the break** — and fixing it means writing another sub-project's file, which a
  worker may not do. `core/spec.md` was left with 228 B above the reserve line and **no
  cheap cut remaining**; `suite/003` is the ~640 B that buys Core's spec room.

### Three supervisor defects, all found by workers, none fixed by the leg that made them

1. **A batched claim commit breaks a worker's own ownership check.** Leg 008 claimed
   `umbrella/003` and `api/008` in one commit (embarch-doc `61b5cd0`) and branched both
   workers off it, so each worker's `origin/main...HEAD` diff contained the *other's* task
   file and `check-ownership.py --scope <its own>` went **red on paths it never wrote** —
   nine paths by the fourth worker, once landed folds had joined the base. Every worker
   diagnosed it correctly, **and that is the danger rather than the reassurance**: §10
   makes this check a merge gate, and a supervisor who learns to read a red ownership check
   as "just the claim commit again" will wave a real one through. Mitigated from that leg
   onward by **one claim commit per task, pushed to `origin/main` before the branch is
   cut**, which narrows the false red without removing it — a branch cut after an earlier
   unit's fold still carries that fold. The structural fix is in `scripts/` and is the
   owner's.
2. **Recovery began against a live worker** (`api/005`). `git rev-list --count` read **0
   commits on both branches** with both worktrees dirty. `ops.md` §3's table has no row for
   that, and its "no commits ⇒ reclaim to `open`, delete the worktrees" arm would have
   destroyed ~200 lines of finished, green work. The leg **looked at the work before
   deleting it** — read the diff, ran build/tests/clippy against the dirty tree, found it
   complete and green, committed it to preserve it — at which point the worker, in its
   final bookkeeping the whole time, committed the code side itself and pushed both
   branches, then **reported its supervisor's now-false commit message back to it,
   unprompted**. The message was amended to state what actually happened. **`rev-list
   --count` against a working worker is a race, not a reading**: there is no observation of
   the *branch* that distinguishes a finishing worker from a dead one. Now
   `tasks/doc/006-recovery-reads-commits-not-worktrees.md`, `Owner: required`.
3. **A feature-shipping worker could not be green on both gates at once.** Adding a
   `features.d/` row makes `suite/features.md` stale by construction, while
   `check-ownership.py` refuses that file to *every* worker scope. The worker chose the
   mechanical red over the boundary violation — the right call — and said so. **Resolved
   since:** the fold runs `python3 scripts/build_features.py` and lists `suite/features.md`
   in `fold-commit.py --path`, and `build_features.py --check` validates fragments only
   while `--check-assembled` stays out of every branch gate. Two facts that came out of it:
   `check-docs.py` runs **eight** checks while `protocol.md` §10 and `supervise.md` both
   said six (since fixed), and `scripts/build_features.py` is mode **644**, so it must be
   run as `python3 scripts/build_features.py` and not as a bare path.

One smaller one, still true and still unenforced: **`fold-commit.py` does not delete a
`done` task file for you.** A task file already merged in its `done` state is not pending,
so it silently drops out of the `--path` count — leg 008's first fold staged 2 paths where
3 were passed, and the silent "2 path(s)" is the only signal. `git rm` the completed task
file explicitly before calling `fold-commit.py`.

### Budget

**DEGRADED at the start and end of every leg, wave 2 throughout, and no 429 anywhere in
the entire day.** One deliberate deviation: `core/003` ran **three** concurrent spawns
against a suggested wave of 2 — two workers plus a reviewer — on the grounds that the cap
is concurrency control against rate limits and the budget script's own line is that "no
429 in the last 90 min is the signal that actually matters". Recorded so a later leg can
decide differently; §10 has since made the reviewer not count against the wave anyway.

### Least sure about

Six standing doubts rather than closed questions, one per entry that raised one:

- **Landing four units with a reviewer on only one**, on a night when two of the four were
  compaction passes — the one class of change whose whole risk is a deletion that reads
  fine. The single reviewer that ran was on the unit that needed it least.
- **Committing another agent's uncommitted working tree at all.** It was right against the
  alternative handed over — deleting it — and the content was verified green before and
  after. But a commit exists whose author did not write its message, on a branch whose
  worker was still running, and **the only reason that is visible is that the worker
  noticed and said so. Had it really died, nobody would ever have known.**
- **Accepting a check whose input format has never been observed** (`umbrella/004`) — a
  check that now *asserts* something about an environment nobody in this suite has run it
  in, which `umbrella/001` is the record of the cost of.
- **Merging `#[cfg(windows)]` code no compiler on this machine has ever seen**
  (`umbrella/003`), accepted only because decision 28 already carries the identical gap —
  which means the suite now has two of them resting on one assumption.
- **Accepting "no" as `DOC-COMPACTION.md` §7's answer and closing the task anyway**
  (`core/003`). Both files did come out of reserve, so the mechanical goal was met, but §7
  is supposed to be what stops a compaction pass being purely mechanical, and a "no" that
  closes the task regardless is very close to not asking.
- **`outpost/001`'s duplication count 31 → 29 is partly a threshold effect**, not two
  claims resolved: shortening a manifest failure signature kept the teeth but dropped the
  overlap below the detector's threshold, so if the count is to move only through deletions
  the honest number is 30. The worker said so unprompted, and the advisory report is now
  slightly better than the docs actually are.

Also carried forward, and it is a fact about the mechanism rather than about a unit: two
more entries in this day recorded **the gate satisfied by an argument rather than a run** —
`suite/001` ran no `cargo` per repo because the diff is four YAML files and a workflow file
cannot break a build, and every doc-only unit ran none because the code tree was
byte-identical. Each argument is sound. It is the same shape batches 001 and 002 flagged,
and this log has now flagged it six times.

---

*Days 2026-09-03 to 2026-09-03 rolled to [log-archive/supervisor-log-2026-09-03-to-2026-09-03.md](log-archive/supervisor-log-2026-09-03-to-2026-09-03.md).*
