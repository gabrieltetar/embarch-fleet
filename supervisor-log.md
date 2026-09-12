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

## 2026-09-12 01:26 — core/045 the route sweep proves reach as well as rejection, and both lists are derived

**Decided:** `embarch-core` **decision 60** in `decisions/auth.md`. Decision 42's sweep measured
exactly one property — every registered route refuses an absent or wrong token — and a route wired
to the wrong handler was green under it. The other half now exists: every handler carries a
`// route: METHOD path` comment above its own definition, and a test derives `build_router`'s
actual `.route(...)` wiring from the source and cross-checks the two. **Neither list is hand-kept**,
which is the whole point and what the task insisted on, following `embarch-api` decision 54.

**The worker mutation-tested its own check before claiming it worked** — swapped two handlers'
wiring, watched the test go red naming both, reverted. That is the step that separates a check
which passes from a check which can fail, and it is the one nothing in the gate would have caught
the absence of.
**Merged:** `agent/core/045-route-sweep-reach` (code `4459668`, doc `5a6d355` after rebasing onto
`umbrella/056`'s fold). Ownership check base `3c9f809c7ec2`, 6 changed doc paths, all owned; the
code-repo half is unrunnable for the same `tasks/doc/036` reason recorded under `umbrella/056`.
Gate green on the merge results: `embarch-core` `cargo build`/`test`/`clippy --all-targets --
-D warnings` clean, `check-docs.py` 11/11, `check-client-names.py --repo embarch-core` clean.
`tasks/core/046-compact-core.md` arrived with the merge — decision 60 put `decisions/auth.md` at
92.4% — filed `blocked`, `In flux: yes`, size debt due 2026-09-26.
**Blocked:** nothing.
**Reviewer:** no findings. It also settled a number this task's own `Source:` line got wrong: the
task, quoting `open.md`, says decision 42 asserts **26** routes. The current router registers **22**
`.route()` lines carrying **23** verb/handler bindings (`/signals` chains two verbs); 42's "26" is
explicitly historical text about 2026-09-06, superseded by retirements noted in the same paragraph.
Decision 60 uses 23, and its `> 20` plausibility guard mirrors 42's own rather than hardcoding a
count. **Nobody should re-derive "26" from this entry.**
**Hardware debts:** none created, one deepened. This is a host-side wiring check and touches no
board, but it adds a fifth thing riding on the **owner's outstanding native Windows build of
`embarch-core`** — the new test does not run in the Windows service build until that lands, and the
service is what actually serves these 26 routes.
**Budget:** PROCEED (weekly 38.1% of a 90% cap), wave 6.
**Least sure about:** whether the derivation reads `.route(...)` lines robustly enough to stay true.
It parses the router's own source text, so a future refactor that registers a route through a
helper, a loop or a macro would drop out of the derived list silently and the test would still pass
on a smaller set. Decision 60 does not say what happens then. That is the failure mode a
derived-from-source check trades for, and it is worth a line in the decision if anyone touches
`build_router`'s shape.

## 2026-09-12 01:24 — umbrella/056 a sticky `--host` now expires when the run that gave it stops being remote

**Decided:** `embarch-umbrella` **decision 51** — `apply_plan` writes `state.host` only when the
plan concludes `Remote`, and clears it on `local`/`wsl-host`. Decision 48 made `--host` sticky and
said in as many words that it was *deliberately* not settling when the value is cleared; 51 closes
that named gap rather than reversing 48, which is why the reviewer read it as settlement and not
contradiction. The losing argument is recorded: keeping a stale value spares a user who alternates
machines one retype, and costs a later run being steered by a host nobody typed in it.

**Two workers wrote this unit concurrently and only one of them should have existed** — my dispatch
error, described in the leg note below. The surviving worker's version is what landed; the
duplicate was told to stand down, confirmed it had edited the same two files with the same
one-branch fix, and committed nothing. Nothing was lost, and nothing about the diff depends on
which one wrote it, but a leg reading this entry should not take "two workers agreed" as
corroboration — they were the same instructions run twice, not an independent check.
**Merged:** `agent/umbrella/056-saved-host-clearing` (code `bbe998c`, doc `d67acc4`). Ownership
check base `139b86edf343`, 5 changed doc paths, all owned. **The code-repo half of the ownership
check could not be run**: `check-ownership.py --scope umbrella` answers `unknown scope 'umbrella'
(known: doc, suite)` when pointed at a code worktree — that is `tasks/doc/036`, already filed and
owner-only, and the code repo is wholly owned by this scope anyway. Gate green on the merge
results: `embarch-umbrella` `cargo build`/`test` (229 tests)/`clippy --all-targets -- -D warnings`
clean, `check-docs.py` 11/11, `check-client-names.py --repo embarch-umbrella` clean.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** one, carried not created — the new clearing behaviour has never run on a real
machine, and `embarch-umbrella/open.md` keeps that as the surviving half of the bullet rather than
striking it. Needs no board, only the owner's own Windows/WSL setup.
**Budget:** PROCEED at dispatch (weekly 38.1% of a 90% cap), wave 6.
**Least sure about:** that the duplicate worker left nothing of its own in the landed diff. Both
edited `setup.rs` and `state.rs` in the same worktree; the surviving worker's commit is what I
merged and it builds and tests clean, but if the two Edits interleaved inside a line nobody would
see it. The diff is 83 lines and I read it as a fast-forward, not line by line.

## 2026-09-12 01:12 — suite/012 the suite's hardest input finally has a worked example, and it is a file a test consumes

**Decided:** the canonical worked study is **`embarch-api/tests/fixtures/self_test_study.json`** —
the one that ran green against the real bench — and it is canonical **because two committed tests
deserialize it into `Study` on every run**, so it cannot drift from the type model. The docs point
at it and show a one-step excerpt; they do not carry a second copy. And the thing a `serde` reading
will not predict is now stated where a hand-author meets it: **`Action` is externally tagged** —
`{"BleAdvertise": {…}}`, one key, the variant name — in `embarch-study-designer/interfaces/types.md`
and again in one line of `suite/studies-guide.md` §1.

**The fixture taught a retired field for eighteen days and nothing could have caught it.** It
carried `"validations": []`; `Study` has no such field and no `deny_unknown_fields`, so it was
accepted and silently dropped — `embarch-decision-reversals.md` shape 3 landing inside the only
example anyone would copy. Removed, and the *reason* it was invisible is now written next to the
type table: **a key this table does not list is accepted and dropped, so check a hand-authored
study against the table because nothing else will.**

**One "Done when" item was deliberately not taken, and I filed it rather than stretching the
window.** The task asked for a `BleConnect` with a `target_address` so §3b's advice has a form.
That changes what a committed test exercises, against a bench nothing in this fleet can reach, and
the announcement promised a worked example and explicitly disclaimed schema and reader changes.
`tasks/api/076` carries it as a **second** fixture — leaving `self_test_study.json` untouched —
which is the better shape anyway.
**Merged:** doc `<this fold>`; code `embarch-api` **`7abca3d`**, my own hands, pushed to `main`.
Gate on the result: `embarch-api` `cargo test` green (44 tests across the binaries),
`clippy --all-targets -- -D warnings` clean, `check-client-names.py --repo embarch-api` clean,
`check-docs.py` 11/11.
**Blocked:** nothing. `tasks/suite/012` closed and removed; `tasks/api/076` filed.
**Reviewer:** skipped (supervisor's own hands, `suite` scope under a closed announcement window —
no worker diff to review).
**Hardware debts:** **one, and it is pre-existing rather than created here.** The canonical example
is two `BleAdvertise` steps and **no study in this suite has ever reached a DUT** — `studies-guide.md`
§3a already says the bench half works and the DUT was never involved. Naming the fixture as the
worked example makes that gap easier to mistake for completeness, which is why §3a now names the
file right where it says the DUT was not involved.
**Budget:** PROCEED at start and end (weekly 37.3% of a 90% cap), wave 6.
**Least sure about:** putting the JSON excerpt in `interfaces/types.md` rather than in
`suite/studies-guide.md`, which is where a newcomer actually starts. The guide is at **94.2%** of
its cap behind a blocked compaction task, so a full example there would have spent most of what is
left — the guide got one pointer sentence instead. If a reader still cannot get to a first study
from the guide alone, the fix is to unblock `tasks/suite/030` and make room, not to duplicate the
JSON.

## 2026-09-12 00:44 — suite/033 the suite decisions file becomes an index, and the debt is paid in the leg that made it

**Decided:** `suite/decisions.md` is now an **index** and the decision text lives in
`suite/decisions/tooling.md` (1, 2) and `suite/decisions/naming.md` (3) — the shape every
sub-project's own `decisions.md` already has, and which the suite level did not. **Nothing was
re-worded**: the three entries are byte-identical moves, with only the relative link paths re-based
for the extra directory level, the same allowance `suite/008` took when it moved decision 1 in.
12,034 B → 2,470 + 8,116 + 3,268, all three comfortably under cap.

**This is the debt the unit before it created, paid one unit later.** `suite/027`'s decision 3 put
the file 1,794 B over on the once-on-a-clock allowance; I filed `tasks/suite/033` in that fold and
closed it in this one, so the ledger entry existed for about fifteen minutes. **The argument for a
split rather than a trim is that `suite/031` had compacted this file out of reserve two hours
earlier and one new decision undid it** — a file a single decision can blow past is the wrong shape,
not a badly compacted one.

**An index, not a redirect stub**, which is the difference from `api/074` the night before. That
split deleted nothing and kept a stub because `history/` linked at the old path and a compaction may
not edit `history/`. Here the old path is genuinely an index — it has a routing table and a reason
to exist — so `history/suite.md`'s three links at it stay correct with no stub semantics at all.

**The gate taught me something mid-unit and I reverted eight edits because of it.** I re-pointed
every citation at the new topic files, as the task file told me to; `check-decision-refs.py` went
RED with `DOC-CONVENTIONS.md`'s rule — **link the index, not the topic file**, precisely because a
split moves an entry while the old path keeps resolving and naming the wrong file. Every citation
now points at `suite/decisions.md`, which is what the index is for.

**One extra fix, same defect as the unit before.** `embarch-outpost/spec.md` §2's third property
carried the *same* false clause `suite/027` had just corrected in decision 17 — "the same wall clock
every other stream in the study carries". The spec is where a reader arrives first. Fixed here
rather than filed.
**Merged:** doc `<this fold>`, my own hands. **No ops §4 announcement, deliberately**: §4's window
is for a suite-wide *design* act or a wire-schema bump, and a verbatim split that decides nothing is
neither. If that reading is wrong, this is the unit to object to.
Gate on the result: `check-docs.py` 11/11 green; `check-doc-size.py` reads **PAID, 24.1%**.
**Blocked:** nothing. `tasks/suite/033` closed and removed in the same fold that created it.
**Reviewer:** skipped (supervisor's own hands, `suite` scope, no worker diff to review).
**Hardware debts:** none — docs only, no repo outside `embarch-doc` touched.
**Budget:** PROCEED (weekly 37.3%), wave 6.
**Least sure about:** whether `tooling.md` is one topic or two. Decision 1 is a formatting-policy
sequencing call and decision 2 is a CI-coverage call, and I grouped them as "how the suite's checks
are run" mostly because a two-decision file and a one-decision file is a thinner seam than a
three-way split of three decisions. The next suite decision that is neither will force the question.

## 2026-09-12 00:41 — suite/027 one field name, two clocks, and the name stays

**Decided:** suite decision 3 — **`rx_utc_ms` keeps its name in both homes, and every home now says
which clock it is.** An outpost trace's `rx_utc_ms` is Core's real epoch clock; a study's CSV,
transcript and `Sample` carry dev-bench **uptime** under the identical name. Neither arm the task
proposed was taken.

**The task offered two arms and I took a third, which is the part to check me on.** Leg 093's
announcement is what bounded this, and it is narrower than the task file: it named
`embarch-study-designer` decision 72's text, `embarch-outpost/spec.md:88-89` and the suite-level
guides, and explicitly disclaimed the firmware arm. **It did not promise the rename**, and consent
for a doc pass is not consent for a four-repo rename — one of those repos being `embarch-dev-bench`,
whose wire struct nothing in this fleet can build — **plus every capture file already on disk, which
no code change reaches.** A rename no already-written file follows replaces one ambiguity with two.
So the rename stays open and is the owner's, with the board in front of him, and the decision says
so in its own text.

**What was actually wrong, and is now fixed.** `suite/016` disclosed the collision where a *study*
reader looks and left the other home alone. `embarch-outpost` decision 17 asserted that a trace's
stamp is *"the same wall clock every other stream in a study carries"* — **false, and false in the
direction that invites exactly the join this decision refuses.** Corrected there, plus the column
listing in `interfaces/integration.md` and `spec.md` §5, each naming the other clock. Decision 72
now points forward to the settlement instead of to an open task.
**Merged:** doc `<this fold>`, my own hands, no branch and no worker (`suite` scope, §8). Gate on
the result: `check-docs.py` 11/11 green after the ledger entry below. No code touched in any repo.
**Blocked:** nothing. `tasks/suite/027` closed and removed.
**Reviewer:** skipped (a `suite` unit run by the supervisor's own hands under an announced window
that closed unanswered — there is no worker diff to review, and the announcement thread is the
review surface this path was given).
**Hardware debts:** none. It **names** one and declines to take it: the firmware arm — one
subtraction at `ble_bridge_real.c`'s stamp site — is written into the decision as its reversal
condition rather than left in a task nobody reads.
**Budget:** PROCEED (weekly 37.3%), wave 6.
**Least sure about:** `suite/decisions.md` went **1,794 B over its 10 K cap** on this decision,
landing on the once-on-a-clock allowance with `tasks/suite/033` filed and due 2026-09-19. The file
was compacted out of reserve **two hours earlier** by `suite/031`, and one new decision undid it. I
read that as the file being the wrong shape — three unrelated subjects, no `suite/decisions/`
directory where every sub-project has one — and filed a split rather than trimming decision 3 into
something less true. The other reading is that I simply wrote too much, and if so the fix is to cut
this entry's decision text, not to split the file.

## 2026-09-12 00:40 — suite/014 decision 7's two false claims, adopted from a killed leg rather than redone

**Decided:** `embarch-study-designer` decision 7 no longer claims `cbindgen` generates the C header
(there is no `cbindgen` in any repo — only a README to-do) and no longer claims C does not
re-implement the wire format (it does, in ~3,000 lines: `serial_protocol.c`, `eap.h`,
`eap_interp.c`). What the FFI boundary *actually* is, is written down in its place. The
`embarch-topology`↔`embarch-study-designer` mutual-precedent loop — each citing the other's
no-caller surface as the reason to keep its own, neither holding an independent argument — is cut
at the topology end.

**This unit is an adoption, not a re-run, and that is the judgement worth recording.** Leg 093 was
killed with this work staged-uncommitted in the leftover leg worktree, already reviewed by an
`embarch-reviewer` against source. I inspected the diff myself before adopting — every factual
claim in it is checkable from the task file's own citations and they hold — and landed it rather
than discarding ~20 minutes of correct work. **Leg 093's split is also upheld**: it announced the
staticlib retirement and then executed only the half with no build coupling, splitting the rest
into `tasks/suite/032`. Doing *less* than an announced act is inside the consent the window gave;
`embarch-dev-bench/app/CMakeLists.txt:162-202` cross-compiles the staticlib on every non-POSIX
build and nothing in this fleet can observe breaking it, so the retirement would have landed green
and been found on the bench.

**One thing I changed before landing it.** The staged work edited `history/suite.md` **directly**,
and `changelog.d/README.md`'s first rule is that nothing edits a shared history file directly. I
reverted that hunk and routed the identical line through
`changelog.d/suite-decision-7-cbindgen-claims.fixed.md`, assembled by `build_changelog.py --only`
in this fold. Same text, correct route, and the fold's own `--only` guard can see it.
**Merged:** doc `<this fold>`. **Code half was already on `origin/main`** — `embarch-study-designer`
`eeb5d2f`, pushed by leg 093 before it died (`README.md`/`Cargo.toml`'s two stale
"does not exist yet" claims); not merged by me, verified present on the remote. Gate on the result:
`check-docs.py` 11/11 green. No `cargo` run — the `embarch-study-designer` tree is unmoved from
`main`.
**Blocked:** nothing. `tasks/suite/014` closed and removed; `tasks/suite/032` filed for the
toolchain-gated retirement, correctly classified `Hardware: required` so no worker can take it.
**Reviewer:** skipped (leg 093's `embarch-reviewer` already reviewed this exact diff against source
and reported no findings; I re-derived its factual claims myself before adopting rather than
spawning a second reviewer on an unchanged diff).
**Hardware debts:** none new. `tasks/suite/032` is now the third `Hardware:`-gated suite item and
needs the dev-bench board plus a Zephyr toolchain no worktree here has.
**Budget:** PROCEED at start (weekly 37.3% of a 90% cap, resets in 102h), wave 6.
**Least sure about:** the `**Reviewer:** skipped` line. The three permitted skip reasons are a
HOLD, a recent 429, and a leg ending at its cap — "a previous leg's reviewer already read this
exact diff" is none of them, and I judged a second spawn on a byte-identical diff to be waste
rather than insurance. If that reading is wrong, the rule is the thing to fix, not this entry.

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
## 2026-09-10 — 55 units

*Folded by leg 080 on 2026-09-11. Fifty-five per-unit entries collapse here with every SHA, every
hardware debt naming a board, and every `**Reviewer:**` line preserved — reviewer lines stay one per
unit and line-anchored so `grep '^\*\*Reviewer:' supervisor-log.md` still tallies correctly, and the
11 of 55 hardware debts that actually name a board are carried in the day's own words. What is gone
is the narrative reasoning behind each accepted judgement; git holds it in `embarch-fleet` at the
commit before this fold and earlier.*

**The day, compressed.** Roughly a dozen legs ran (~062 through ~080). Four cross-cutting patterns
run through nearly all of them, and matter more than any single unit:

1. **Recovery-fold traffic was heavy, and it kept working.** Legs 062, 063, 068, 069 and 071 were
   each killed mid-fold or mid-leg with green, pushed worker branches still unmerged. Every successor
   leg recovered rather than re-dispatched — `api/060`, `core/036`, `core/021`, `core/017`, `api/051`,
   `umbrella/047`, `umbrella/045`, `api/027`, `core/013`, `api/056` are all recoveries, not re-runs —
   because `fold-commit.py`'s one-commit-per-fold rule kept every half-landed state legible. One
   genuine gap surfaced: leg 062's `umbrella/043` sweep was uncommitted in its worktree when killed
   and was correctly discarded per `ops.md` §3 (nothing to recover), while leg 069's `api/056` split
   across a landed code commit and an unmerged doc branch, leaving the suite ~22 hours with a shipped
   behaviour change and no decision recording it — a shape `leg.md` does not yet name.
2. **Several sub-projects independently concluded a doc-size cap is wrong rather than their files
   being sloppy.** `api/060` and `core/036` reached it independently in one leg; `study-designer/026`
   and `study-designer/027` reached it a third and fourth time. Five of eight sub-projects now carry
   an `open.md` in the same reserve against the same 5 KB role cap, every one of those compaction
   tasks `blocked`, and `study-designer/026` is the first hard evidence one has **no payable form at
   all** without deleting a live question. Filed to `tasks/doc/031`, `tasks/doc/034` and a new
   `inbox/doc-a-full-open-md-of-live-questions-has-no-payable-debt.md` — `DOC-BUDGET.md` is
   owner-reserved and no leg touched it. Where a cap was hit, **verbatim splits** were preferred over
   squeezes throughout the day (`topology/026`, `api/062`, `api/051`, `umbrella/046`, `outpost/008`,
   `outpost/014`, `topology/019`, `api/058`) and two compactions (`api/026`, `core/022`) each lost one
   real fact to an over-eager squeeze, caught only by a reviewer and repaired at the fold.
3. **Citation sweeps kept finding real miscitations hiding behind mechanical dead-pointer fixes.**
   `umbrella/043`, `core/032`, `core/033`, `core/008`, `study-designer/027` each swept or repaired a
   sub-project's decision citations and each found the filed estimate wrong (four sweeps running) and
   at least one citation that was a **real but wrong** decision number rather than a dead one — the
   dangerous case, because `check-decision-refs.py` only resolves a number and cannot tell a plausible
   wrong citation from a correct one. The settled citation-form convention (bare `` decision M `` for
   a same-repo citation, `` `<repo>` decision M `` cross-repo) was independently reinvented wrong twice
   this day — a `` `decision N` `` backtick-wrapped form in `core/032`'s sweep, and a fabricated
   "`embarch-ui milestone 1`" form in the work `core/008` corrected — both caught and either filed
   forward or fixed in the same fold.
4. **A standing hardware debt turned out to be false, and is now corrected everywhere it was
   recorded.** Three earlier log entries said "this environment has no `west` and no `ZEPHYR_BASE`"
   as an `embarch-dev-bench` hardware debt. `dev-bench/008` and `core/019` each measured it this day
   from the **main checkout** (not a worker's gitignored worktree) and it builds and runs clean,
   `esptool>=5.0.2` installed into the shared `.west-venv` as a result. `tasks/dev-bench/008` is
   reclassified `none` → `toolchain`, which is the accurate class `tasks/README.md` already defined:
   undispatchable to a worker's worktree, not unrunnable on the machine. `embarch-outpost`'s Zephyr
   suite remains genuinely unbuildable here throughout the day — that debt is real and unchanged.

### Decided — the suite-wide and owner-facing calls

- **`suite/016` (22:29):** `Sample::rx_utc_ms` is dev-bench uptime, not UTC — the seed-and-resync
  from `Hello.host_utc_ms` that would make it real UTC was designed and never built. Three contracts
  (`interfaces/decoders.md`, decision 12's own text, `src/protocol.rs`'s doc comment) plus two read
  points (`src/gatt.rs`, `src/outpost.rs`) corrected; recorded as `embarch-study-designer` decision
  72. **The rename itself is deliberately not done** — it reaches four repos plus every capture file
  already on disk — and is split out as `tasks/suite/027` with the firmware alternative argued and
  refused (it would make every capture before the fix incomparable with every capture after, silently).
  A scheduled decision, not a settled one; a leg that agrees with the task's own framing (that the
  **name** is the false witness, not just the doc text) should feel free to take it.
- **`api/044` (22:24):** the deferred `hardware_id` rename is **cancelled**, not merely deferred
  again — `embarch-core` decision 56 is the settlement. Unprefixed `hardware_id` stays the suite's
  name for the probe-read identity; `probe_hardware_id` stays confined to the one route
  (`GET /dev-bench/hello`) where the two IDs are neighbours. All three `embarch-core-client` structs
  now carry a doc comment naming which ID they hold, in exchange. Also filed `core/039`: two live
  `embarch-core` decisions are both numbered 54 (`flashing.md:46`, `surfaces.md:45`) —
  `check-decision-refs.py` is green on both because it resolves per sub-project, not per file; the
  missing uniqueness check is `doc/033`, owner-reserved.
- **`suite/024` (22:07):** declined unifying `embarch-topology`'s chip-family classifier with
  `embarch-core`'s `flash_backend.rs` prefix match. The task's own premise — that the two "already
  agree" on the nRF54H boundary — was false since `embarch-core` decision 49: one abstains from
  naming a register pair, the other definitively refuses probe-rs; reading the second as agreement
  with the first is exactly what a unification would be built on. Two false corroborating claims
  deleted (topology decision 25's amendment, `classify_chip`'s own doc comment); `embarch-core` was
  not touched.
- **`suite/023` (21:02):** completed leg 073's parked §4 window. `DOC-CONVENTIONS.md`'s existing
  `[measured]`/`[assumed]` marker earns a **scope correction**, not a new convention: its own earning
  test already covers a check-table arm distinguishing an exercised arm from a merely-designed one,
  found via 17 `open.md` bullets across five sub-projects converging on the same word independently.
  **`DOC-CONVENTIONS.md` is owner-reserved** (`protocol.md` §3 — `never` for the supervisor too, not
  only workers) so the task could not be closed; a drafted ~560 B paragraph is left for the owner,
  marked `Owner: required`. Also recorded: leg 042's routing of this drop to `suite/` scope conflated
  "keeps it off a worker" with write access — scope does not confer write access to an owner-reserved
  file, and a leg can burn its one §4 window on a task it then cannot finish.
- **`suite/008` (20:18):** created `suite/decisions.md`; moved `embarch.md` §5's ~5 KB rustfmt
  decision into it verbatim as decision 1 (`embarch.md` 17,832 → 14,090 B). Both of the task's own
  boundary conditions checked, not assumed: the new file needs no ownership classification, and
  neither `DOC-PROTOCOL.md` nor `DOC-COMPACTION.md` needed amending. What *is* left — `DOC-PROTOCOL.md`'s
  two enumerations of suite-level docs now under-list rather than mis-list them — is filed as
  `tasks/doc/038`, not edited, because amending doc-structure rules to accommodate a file the
  supervisor just created is the one thing a supervisor should not do to its own constraints.
- **`suite/026` (19:02):** `embarch-token.md` §2 now cites `embarch-core` decision 53 (auth.md) for
  why Core deliberately never restricts `%ProgramData%\embarch`'s ACL, alongside the existing
  `embarch-topology` decision 23 citation — linked to the decision **file**, not an anchor, because
  `check-links.py` rejects an anchor slug containing a backslash and backticks.

### Merged

Every unit below in the day's own order, newest first. Every `Merged:` paragraph is carried close to
verbatim so every SHA and ownership-check base survives; narrative is condensed to the load-bearing
judgement, what a next reader must not re-derive, and (for the 11 real ones) the hardware debt in the
day's own words. "Hardware debts: none." means the unit's own line said so — no board, no board-shaped
follow-up.

---

**`suite/016`** (22:29) — see Decided above.
**Merged:** `agent/suite/016-rx-utc-ms` (code `e5e5d88` in `embarch-study-designer`, doc `d1f4345`).
Supervisor-executed, no worker branch pair; committed directly on the leg's detached HEAD for the doc
half.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **one named and deliberately not taken** — the firmware offset arm of
`tasks/suite/027` needs the dev-bench board, and it is the owner's call because of what it does to
capture comparability, not merely because it needs hardware. `embarch-dev-bench/open.md`'s
"Clock-resync accuracy is not validated" bullet stands.

---

**`api/044`** (22:24) — see Decided above.
**Merged:** `agent/api/044-hardware-id-rollout` (code `9b7bfac`, doc `7a066e2`). Ownership check
bases: code `57d27f70cff7`, doc derived at the fold.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** none. Note for the record: the landed `embarch-api` commit message `9b7bfac` says
"decision 55" where the content is decision 56 — renumbered mid-unit after `core/037` took 55
concurrently, message not amended; on `main`, not worth rewriting, flagged so a grep for "decision 55"
is not misled.

---

**`core/037`** (22:19) — retired the name `study_schema_mismatch` rather than build the member: it
was typed into decision 12's prose for a hypothetical future error-code enum `embarch-core` has never
had, and building the member would mean building the whole deferred `{code, message, cause}` body,
which §5 puts outside one worker's repo. Recorded as decision 55, with a forward note that prior
mention owes the name no seat if the enum is ever built.
**Merged:** `agent/core/037-study-schema-mismatch-code` (code none — docs-only, zero commits on the
`embarch-core` branch; doc `4b39245`). Ownership check base `9780cc65d8fd`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`ui/024`** (22:19) — a decision 334 B (8%) over the 4,096 B per-decision cap, compacted in place
rather than split, because the file holds exactly one decision and a split would only relocate the
cap problem. 4,430 → 4,034 B; reviewer independently checked every invariant, rejected alternative and
failure signature survived. Flagged: `check-doc-size.py --decisions` (not the size ledger) shows three
more over-cap decisions with nothing filed — `embarch-topology/decisions/validation.md#25`,
`embarch-outpost/decisions/testing.md#22`, `embarch-core/decisions/logging.md#44` (the last left
deliberately unflagged by leg 076).
**Merged:** `agent/ui/024-decision-10-over-cap` (code none — docs-only, zero commits on the
`embarch-ui` branch; doc `9780cc6`). Ownership check base `170f5b867691`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`suite/024`** (22:07) — see Decided above. Its `ops.md` §4 window was announced at
`ts 1789097484.647639`, ran its full 30 minutes, closed with no objection; two further windows opened
this leg (`suite/016`, `api/044`) were not consumed the same way.
**Merged:** `agent/suite/024` — none; executed directly on `main` as a supervisor unit. Code
`embarch-topology` `b872f6d`; doc half in this fold. Ownership clean, scope `suite`, base
`f0b7389602a0`; `check-ownership.py --supervisor` clean, 16 of 16 top-level docs classified. Gate:
`cargo build`/`test --all-features` (69 + 5 tests)/`clippy --all-targets --all-features -D warnings`
green in `embarch-topology`; `check-docs.py` 11/11.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **none owed, and one deliberately not discharged.** The way to settle nRF54H for
either matcher is a register read and an erase/write check on real silicon, and **no nRF54H part
exists on this bench or in this suite** — refusing on both sides rather than promoting a prefix to a
fact. Also carried: `outpost/017-compact-outpost.md` was filed this unit against `outpost/016`'s
`testing.md#22`, already over cap before that unit touched it.

---

**`study-designer/028`** (21:54) — four EAP protocol primitives (`repeat`, `bitpack`, `crc32`,
`fixed`) were parsed but silently rendered wrong or not at all. `render_layout(frame)` is a new
accessor returning `Err(RenderUnimplemented{frame, primitive})` naming the missing primitive; `Ok(None)`
still means a shape never described. Additive: `EapErrorKind` is not named outside this crate and
nothing calls `struct_layouts()` outside it (reviewer-confirmed suite-wide), so nothing broke. New
decision 71 refuses rather than converts, consistent with the crate never claiming what a DUT's bytes
mean.
**Merged:** `agent/study-designer/028-primitives-fail-loudly` (code `2652e11`, doc `19614f8`).
Ownership clean, 5 doc paths, scope `study-designer`, base `a77543cb73ce`. Gate: `cargo build`,
`clippy --all-targets -D warnings` clean; `cargo test --features eap-parse` green, 152 + 12 + 10
tests.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none — host-side Rust throughout.

---

**`outpost/016`** (21:53) — filed on the false premise that `tasks/suite/021` was never issued (a
directory-listing inference `tasks/README.md` warns against); the worker checked and found 021 was
real, finished, folded 2026-09-08 (`ac20966`), and about something else (`embarch-core`/
`embarch-dev-bench` CI claims, not `embarch-outpost`) — which is why it was not on disk (a completed
task is `git rm`'d). Two `embarch-outpost` docs corrected to state the no-CI fact directly
and cite `embarch.md` §5, leaving "should outpost get a workflow" unfiled rather than falsely filed.
**Merged:** `agent/outpost/016-ci-citation` (code none — docs-only, no `embarch-outpost` branch; doc
`a77543c`). Ownership clean, 4 paths, scope `outpost`, base `b9e111fe9b18`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none — and deliberately created
none: the standing outpost toolchain debt is exactly why no agent may author that CI job.

---

**`api/062`** (21:52) — `embarch-api` decision 19 (34% over cap) turned out to be one number wearing
two decisions — the FNV-1a hash for `extra_args`, and `target.json`'s own file semantics — split
verbatim into 19 and new 69, both staying in `target-json.md` since only the decision, not the file,
was over cap. Came out of this leg's refill sweep, which also surfaced that `check-doc-size.py
--decisions` (not the ledger) is where such over-cap-decision debt hides.
**Merged:** `agent/api/062-compact-target-json` (code none — docs-only, no `embarch-api` branch; doc
`b9e111f`). Ownership clean, 5 paths, scope `api`, base `0c70e6814dd3`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`topology/026`** (21:27) — paid the 419 B debt `api/042`'s supervisor filed against its own fold one
leg earlier. Split rather than squeezed: decision 18 (DUT signal link/route) stayed at `links.md`
because four other sub-projects cite it by path and none is in this task's ownership row; decisions 17
and 24 moved to new `links-port.md`. 11,478 B → 7,360 + 5,155 B, verified verbatim by diff, not by
trusting the report. **Rule recorded as reusable: when a split must choose which half keeps the
filename, the half with out-of-scope citers keeps it.**
**Merged:** `agent/topology/026-compact-topology` (code none — docs-only, no `embarch-topology`
branch; doc `1614157`). Ownership clean, 6 paths, scope `topology`, base `202949bf5bb2`. The branch
needed a rebase onto `main` after this leg's own `api/037` fold; pre-rebase tip is not a revert handle.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`api/037`** (21:26) — `GET /dev-bench/hello`'s timeout stops silently reusing `status_timeout` (10s,
justified as "pure local-file read") and is argued to `serial_timeout` (15s) instead, because Core
actually opens the bench's serial link and completes a Hello/HelloAck exchange before reading the
flushed boot log — the same shape of cost `serial_log` already budgets for. New decision 68 in
`decisions/dev-bench.md` (not the topically obvious `decisions/core-link.md`, which is over cap).
**Merged:** `agent/api/037-dev-bench-hello-timeout` (code `57d27f7`, doc `0fdf709`). Ownership clean
on both: code repo 1 path, doc branch 4 paths, all `api`. The doc branch needed a rebase onto `main`
after this leg's own `api/060` fold and `topology/026` claim moved it. Gate green including `cargo
clippy --all-targets -- -D warnings` and `check-client-names.py`.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **one new, and it is small and precise.** No handshake duration has ever been
timed on any bench, so both `serial_timeout`'s 15s and the `status_timeout` it replaced are assumed.
One timed authenticated `curl` of `GET /dev-bench/hello` on the primary bench (dev-bench board
attached, Core running) sizes this route and `serial_log` at the same time. Needs only the dev-bench
board.

---

**`api/060`** (21:20) — recovered leg 074's killed fold. Accepted a partial payment: worker cut 84 B
of filler (`, and it fired`; `; revisit otherwise`; a settled-deferred sentence), 4,208 → 4,124 B,
still 204 B inside reserve — filed and unpaid, due 2026-09-24, rather than pushed for a third squeeze
after two prior passes (`api/026`, `api/031`) each lost a real fact doing exactly that. Second
sub-project (with `core/036`) concluding independently the cap is the thing that should move.
**Merged:** `agent/api/060-compact-api` (code none — docs-only, no `embarch-api` branch; doc
`41d21bd`). Ownership clean, 3 paths, scope `api`, base `05e86063c0a9`.
**Blocked:** `tasks/api/060` itself, by design — 204 B of debt unpaid, dated 2026-09-24.
**Reviewer:** no findings. **Hardware debts:** none.

---

**`core/036`** (21:17) — recovered leg 074's killed fold. Accepted a documented **no-safe-cut** as a
completed unit: the worker read `embarch-core/open.md` bullet by bullet and found nothing strikeable
beyond ~17 B, and rejected a verbatim split (no outside consumers). File unchanged, zero bytes moved —
the correct result, contrasted with `core/022`'s manufactured cut. `blocked`, not `done`, debt dated
2026-09-26 — `blocked` keeps the ledger's debt on the clock without stranding it in a deleted `done`
task.
**Merged:** `agent/core/036-compact-core` (code none — docs-only, no `embarch-core` branch; doc
`feb1c84`). Ownership clean, 2 paths, scope `core`, base `189c7658606d`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`api/042`** (21:08) — surfaced two capabilities to CLI/MCP that were GUI-only: decision 67
(`decisions/surface.md`) and a verbatim section split of `interfaces/tools.md` (closing `api/053`) into
`tools-discovery.md`, `tools-build-flash.md`, `tools-dev-bench.md`, `tools-topology.md`. New
`SetDevBenchLinkRequest` checked field-for-field against `embarch-core/src/api.rs:737` against exactly
the class of unpinned-mirror defect `embarch-api/open.md` already records having fired once. Consuming
this unit's own `status.d/` fragment spent doc reserve in *another* sub-project's file
(`embarch-topology/decisions/links.md`) — trimmed in the fold and filed as `topology/026` (above)
rather than cut into the four clauses the note exists for.
**Merged:** `agent/api/042-signal-and-link-writers` (code `234ca66`, doc `8840ebc`). Ownership clean
on both: code repo 6 paths, doc branch 14 paths, all `api`. The doc branch needed a rebase onto `main`
after this leg's own `suite/023` fold moved it.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **none new, and the unit deliberately needed none** — the client wrappers it
surfaced were already round-trip tested. One re-affirmed cost, not new: `embarch-topology` decision
18's *"a bench with no Core running has no terminal path to declare a signal"* still stands, because
`embarch-api` needs Core running exactly as the UI does.

---

**`suite/023`** (21:02) — see Decided above. Completed leg 073's parked §4 window (`ts 1789093650.796139`,
announced 20:27:31 MDT, closed 20:57:31 with no reply) rather than restarting it.
**Merged:** nothing. This unit committed one file, `tasks/suite/023-*.md`, in its own fold commit — no
branch, no worker, no code diff. The fold commit's SHA is the only handle.
**Blocked:** nothing, but **the task is not closeable and I could not do its second half** —
`DOC-CONVENTIONS.md` is owner-reserved (verified via `check-ownership.py --supervisor --stdin`, exits
1); marked `Owner: required` with a drafted paragraph.
**Reviewer:** no findings. **Hardware debts:** none.

---

**`api/039`** (20:40) — authored the missing decision for why `embarch-core-client` lives where it
does (decision 66), after discharging the task's own blocker (its reserve-spending prohibition,
already lifted by `api/026` two units earlier). **The reviewer found the decision's own reversal
condition — "a third Cargo consumer appears" — had already fired** (`embarch-umbrella` has
path-depended on the crate since `umbrella/036`, 2026-09-08); amended in the fold rather than left
standing false overnight, count corrected to three consumers, an FFI/C-boundary rationale wrongly
attributed to `embarch-topology` decision 13 also corrected. Conclusion survived both corrections;
decision numbers are permanent so it was amended, not reverted.
**Merged:** `agent/api/039-core-client-home` (code none — documentation-only, `embarch-api` has no
diff; doc `fcbcb6f`, a merge commit; the worker's own commit is `17155cc`). Ownership clean, 6 paths,
all `api`.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/api-review-039-third-consumer.md.
**Hardware debts:** none. Note: the supervisor's own amendment pushed `decisions/core-link.md` further
over its cap (13,164 B, 876 B over) — filed via the existing `tasks/api/061`, due 2026-09-24, not a
new debt, but a supervisor arguing the caps are too tight then writing 680 B of over-cap correction
prose is worth someone pushing back on.

---

**`api/026`** (20:25) — second compaction this leg to lose a fact to a squeeze. Worker's pass was real
(`open.md` 5,068→3,914 B, `spec.md` 9,441→9,038 B) but self-reported cutting one "tangential aside" —
that `embarch init` never writes `serial_port` at all — which the reviewer swept nine files for and
found recorded **nowhere else in the suite**. Restored (227 B), putting the file back inside reserve
by 221 B — filed as `tasks/api/060` (above), same shape as `core/036` deliberately. A defect of the
supervisor's own landed and fixed one commit later: `suite/008`'s fold had left `suite/decisions.md`
linking to a task file the same fold `git rm`'d.
**Merged:** `agent/api/026-compact-api` (code none — documentation-only, `embarch-api` has no diff;
doc `04929b8`, a merge commit — `suite/008` had advanced `main`, so this was not a fast-forward; the
worker's own commit is `b01f8d2`). Ownership clean, 4 paths, all `api`.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/api-026-squeeze-quoting-and-lost-fact.md.
**Hardware debts:** none.

---

**`suite/008`** (20:18) — see Decided above. Completed leg 018's parked §4 window rather than
restarting it: announced 2026-09-06 04:17:43 MDT (`ts 1788689863.494449`), closed 04:47:43, re-read
before acting with no replies then or since.
**Merged:** nothing — this unit is the supervisor's own work under §8 and had no worker, no branch and
no code repo. It lands in this fold commit alone; that commit's SHA is the only revert handle.
**Blocked:** nothing.
**Reviewer:** skipped (reviewer did not report — spawned at the change, still silent 18 minutes later
with no completion and no drop; supervisor stopped waiting rather than strand a finished `api/026`
branch behind it).
**Hardware debts:** none.

---

**`core/022`** (19:56) — `embarch-core/open.md` squeezed 4,551→3,911 B, real cut. **Reviewer found two
cuts that were status changes, not shortenings**: an `Alert` deferral's named trigger flattened to a
closed "Not needed", and an Espressif port-selection claim that reads as if confirming an enumeration
were the whole gap. 111 B put back in the fold. `fold-commit.py` refused leaving the task `open`, so it
closes and the 102 B unpaid residue is filed fresh as `tasks/core/036` (above) rather than left as an
unpaid balance on a deleted `done` task.
**Merged:** `agent/core/022-compact-core` (code none — documentation-only, `embarch-core` has no diff;
doc `25b5239`). The 111-byte restoration and the task state are in this fold commit, not in `25b5239`.
Ownership check clean, 3 paths, all `core`.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/core-open-md-compaction-residue.md.
**Hardware debts:** none — but names one question still hardware-gated: the ESP32-C5-WROOM-1 DK's
single-USB-Serial/JTAG enumeration is still **[assumed]**.

---

**`api/035`** (19:42) — `embarch-api/open.md`'s stream-status bullet no longer claims the event stream
has never met a real Core; it now states what was actually seen (leg 021, 2026-09-06: pushed live
frames, `transport: live`, an observed `polled` fallback) and what was not (`study-status --follow`,
the drop path, `lagged`, a reconnect). The debt pointer it replaced, `tasks/api/001-sse-client.md`,
**was never filed at all** — a phantom, replaced with real `tasks/api/059`. Supervisor also corrected
the unit's own second half: it had left `tasks/api/026` `blocked` on a self-referential condition
("this task's own remaining job"), which would have hidden a dispatchable size-debt task for four
days — reviewer caught it, `026` reset to `open`/`In flux: no` in this fold.
**Merged:** `agent/api/035-sse-live` (doc `3e7bde8` after the rebase; no code branch — the remote
`agent/api/035-sse-live` carried zero commits, correct for this unit). Ownership check base
`04290f1a20f7`, 5 paths, all `api`. Gate green, 11/11 doc checks.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/api-026-blocked-on-nothing.md.
**Hardware debts:** **none new; one restated more honestly and one retired.** No board was touched,
and the worker was directed away from the one action that would have needed one. `tasks/api/059` now
carries what's owed — `study-status --follow`, the drop path, `lagged`, a reconnect — all needing a
live Core and a running study. The phantom `tasks/api/001` is retired.

---

**`ui/023`** (19:37) — timed the request path's in-process half only (parse + JSON encode: 4.6→8.3→
23.5 ms; in-process total 210 ms→518 ms→1.32 s at 250k/500k/1M rows, [measured 2026-09-10, release]),
and stopped honestly at the boundary where `decode_trace` calls into a live Core with nothing synthetic
standing in. Cap stays 250,000. Also paid `embarch-ui/open.md`'s reserve debt as the actor making the
flux, per `tasks/ui/021`'s park.
**Merged:** `agent/ui/023-trace-request-timing` (code `20bb3a9`, doc `04290f1`). Ownership check
bases: code `9361329a3af1` (`--code-repo`, 1 path), doc `6608755477a8`, 4 paths, all `ui`. Gate green
in both repos. Note the code merge also fast-forwarded `embarch-ui` past three commits of another
unit's work (`408e3b1` → `20bb3a9`); this unit's own diff is `src/trace.rs` alone.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **none new, and one sharpened.** The unit needed no board and took none. What it
names is precisely what a board is still owed for: `/study/{id}/streams` end-to-end remains
unmeasured and 1.32 s must not be read as the whole cost — the three Core calls in front of `parse`
have no number and cannot get one without a live Core. `embarch-ui/open.md`'s older stale-prefix debt
(the 18-record capture, decision 19) is unchanged and is the owner's own session.

---

**`umbrella/049`** (19:15) — recovery of leg 071's pushed, unreviewed work. Two-armed answer approved:
`CoreConfig` re-exports `embarch_core_client::CoreConfig` outright (the token-mirror pattern);
`ProjectConfig` cannot follow (lives in `embarch-api`'s own binary), so it gets a
`deny_unknown_fields`-shadow test against the real `embarch-api/config.example.toml` instead — narrower
than a diff job, a real improvement on nothing-fails-when-they-drift. Decision 20's second amendment in
`decisions/mirrors.md`.
**Merged:** `agent/umbrella/049-coreconfig-mirror` (code `46ec5c0`, doc `2fecd0e` after the rebase; the
doc branch's pre-rebase tip `1499bba` is not a revert handle). Ownership check bases: code `584f7e7a3658`
(`--code-repo`, 1 path), doc `a8e6642145746e` after the rebase, 4 paths, all `umbrella`. Gate green in
both repos — 226 tests, clippy `-D warnings` clean, 11/11 doc checks.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** none. Flagged instead: `.claude/leg.md`'s worktree link table omits
`embarch-api` from `embarch-umbrella`'s links even though `Cargo.toml` has path-depended on
`embarch-core-client` for some time, and this unit's new test reads across that same sibling path —
filed as `inbox/leg-md-worktree-link-table-omits-embarch-api-for-umbrella.md` (owner-reserved file).

---

**`core/017`** (19:12) — completed a fold leg 071 started and did not finish; both branches already
merged and pushed. `Backend::NrfJprog` retired rather than documented (no bench in this suite has ever
selected it), decision 54 in `decisions/flashing.md`, which crossed into reserve (93.5%) on the way —
filed `tasks/core/035-compact-core.md`, blocked on `In flux: yes`.
**Merged:** `agent/core/017-nrfjprog` (code `31a2e09`, doc `d9fa167`).
**Blocked:** nothing. 
**Reviewer:** no findings (carried from leg 071's handoff, not re-witnessed).
**Hardware debts:** none — the one thing a board would have settled (doctor check 14 reporting the
selected backend) is now moot, since the variant it might have reported is gone.

---

**`api/058`** (19:06) — split-first: decision 43 (the per-machine logfile) moved verbatim out of
`core-link.md` (about Core's *link*) into new `embarch-api/decisions/logging.md`, paying the reserve
debt by relocating rather than squeezing. `core-link.md` 11,962 → 9,955 B, off `--pressure` entirely.
No code change.
**Merged:** `agent/api/058-compact-api-doc` (doc `f5b46eb`; no code branch — `embarch-api` had nothing
to change). Ownership check base `55f31f1031a9` after the rebase, 6 paths, all `api`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`suite/026`** (19:02) — see Decided above. Executed leg 068's announced `ops.md` §4 window
(`ts 1789083897.811379`) rather than restarting its clock — the thread was quiet and well over 30
minutes had elapsed.
**Merged:** nothing — supervisor-executed suite task, committed directly in the leg worktree with the
fold.
**Blocked:** nothing.
**Reviewer:** skipped (supervisor-executed suite unit; a one-clause citation with no branch diff).
**Hardware debts:** none.

---

**`dev-bench/008`** (18:58) — see the toolchain-debt correction in the day summary above (measured
`west`/`ZEPHYR_BASE` working from the main checkout; three prior "no toolchain" debt entries were
false). Also: the `fail_reason` census prefix now carries two counts (`no name match; 2/10 named:
'A', 'B'`), rejecting the tempting fix of widening `OUTCOME_MAX_FAIL_REASON_LEN` (a wire-size change
that would not have fixed the actual gap — the field not saying what it omitted); and the runtime
reservation for `(census full)` was made conditional, amending decision 45 (it is always known ahead
of time, unlike `(truncated)`).
**Merged:** no branch and no merge — a supervisor-executed `toolchain` unit. Code `a0bf1d8` in
`embarch-dev-bench`, committed and pushed straight to `main`; the doc half is in this fold commit.
**Blocked:** nothing, but **`tasks/dev-bench/008` stays `open` on purpose** — its third `Done when` box
(tests over a mixed named/nameless set) is unsatisfiable from here, since both gates live in
`ble_bridge_real.c`, which never builds under `native_sim`.
**Reviewer:** no findings.
**Hardware debts:** **one new and it is the honest half of this unit — the behaviour has never been
observed.** No test reaches either changed gate; nothing has watched a real nameless advertiser appear
in a `2/10 named` line. Needs the dev-bench board and a 20-second census. Also filed `tasks/doc/036`:
`check-ownership.py --scope dev-bench` fails with "unknown scope" when run from inside a code repo
(same root cause as `tasks/doc/035`'s cwd-dependent `queue-status.py` misreport — 0 dispatchable from
the fleet repo, 29 from the instance).

---

**`topology/025`** (18:51) — filed by this leg's own refill off `embarch-topology/open.md`'s standing
"nothing states what a caller may assume" bullet. New decision 29 in `decisions/scope.md`: no cache, no
watcher, no invalidation signal (considered and rejected — every real caller already re-resolves per
operation); a caller may hold a result only for the one operation it was taken for, never across a
retry.
**Merged:** `agent/topology/025-caller-granularity-contract` (doc `6633072`; no code commit —
doc-only). Ownership check base: doc `07a632e76d6f` after rebasing onto api/054's fold. The same
commit paid `spec.md`'s reserve debt — landed at 9,195 B (89.8%); `tasks/topology/024` stays blocked.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none — and flags an unverified
direction: nobody has checked whether `embarch-core`, `embarch-api` or `embarch-umbrella` actually
holds an answer across operations today, which the new contract would make a bug if so.

---

**`api/054`** (18:48) — `decisions/core-link.md`'s decision 26 retitled (not retired) about intent,
freeing the compaction task `api/026` that had been stuck twice for want of room — the reserve was
cleared **because it was also required to be paid** in the same commit, carrying `026`'s
`Must not delete:` list. First time this ledger has been paid down and re-filed (as `api/058`, above,
recommending a topic split) in one unit.
**Merged:** `agent/api/054-decision-26-retire-or-retitle` (doc `212f4a4`; no code commit — a doc-only
unit, the branch was pushed at `embarch-api`'s main tip). Ownership check base: doc `253abc67f692`
after rebasing onto core/019's fold. `decisions/core-link.md` went 12,082 → 11,962 B, still in reserve
at 326 B left.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`core/019`** (18:47) — see the toolchain-debt correction in the day summary above (this is the twin
measurement to `dev-bench/008`). `embarch-token.md` §5's per-caller-identity row moved from bare
`Todo` to `Declined — single-engineer scope forbids a permission model; revisit only if Core ever needs
to tell which caller`, accepted as prose since `Status` has no closed vocabulary. This leg's refill
(`--refill-owed`) also corrected `tasks/umbrella/048` from `open` to `blocked` (it carried
`In flux: yes` while advertising itself as dispatchable).
**Merged:** `agent/core/019-per-caller-identity-row` (doc `5b6c980`; no code commit — the branch was
pushed unchanged at `embarch-core`'s main tip, the whole change is a `features.d` fragment). Ownership
check base: doc `e56d302c3f15` after rebasing onto this leg's two later claim commits.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`dev-bench/015`** (18:36) — completed the combined-truncation-marker fix `dev-bench/007`'s reviewer
found the gap in: both `(truncated)` and `(census full)` now write independently rather than one
priority chain silently dropping the other, exactly what decision 45 forbids re-collapsing. Budget
widened `BUILD_ASSERT` from `MAX(a,b)` to `a+b`.
**Merged:** `agent/dev-bench/015-combined-truncation-markers` (code `a4ab003`, doc `7dd4b8f`).
Ownership check bases: code `79d474345fa9`, doc `2d8d137c6ef9`.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** **one, and it is a toolchain rather than a board — the same class the
`embarch-outpost` debt is in, and this is the second sub-project now carrying it.** Firmware not built,
no ztest run — no `west`, no `ZEPHYR_BASE` in that worker's environment. `ble_bridge_real.c` never
builds under `native_sim` regardless (decision 16), so even a toolchain session would not cover these
lines by ztest — only a real board compile would catch a `BUILD_ASSERT` that no longer holds.

---

**`umbrella/045`** (18:30) — accepted a no-op as the right outcome: `doctor` renders no
`confirmed_at_utc_ms` and never will without a hardware-lock-taking change nobody asked for. Landed ten
lines of module doc in `src/doctor.rs` instead, naming the required label ("Enrolled", never
"Validated"/"Verified") for any future umbrella surface that does render the field, citing `embarch-core`
decision 54. Third recovery landing of leg 069's pushed work.
**Merged:** `agent/umbrella/045-confirmed-at-label` (code `584f7e7`, doc `66f9788`). Ownership check
bases: code `6c423e1cd9eb`, doc `95831bb0fa0b` after rebasing onto api/027's fold.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`api/027`** (18:29) — recovery of leg 069's pushed work. Corrected a false clause inside decision
55's own rejection text (claiming `reqwest`'s `default_headers` would "leave the sweep nothing to
assert" — false, the sweep asserts the header on the wire at `MockCore`); the remaining rejection
reason marked prospective rather than current. Two test-side repairs rode with it.
**Merged:** `agent/api/027-decision-55-sweep-clause` (code `0350c8c`, doc `b96c98c`). Ownership check
bases: code `7e859b541302`, doc `b78e0fb5d906` after rebasing the doc branch onto core/013's fold.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`core/013`** (18:27) — recovery of leg 069's pushed work; the substantive build-vs-retire call was
already leg 069's. Decision 14's 503 on `hw_lock` contention built at last: `hw_lock` is now
`Arc<Mutex<Option<HolderInfo>>>` behind one `acquire_hw_lock` helper used by all 8 hardware sites, a
500 ms acquire timeout, a `503` naming the holder.
**Merged:** `agent/core/013-hw-lock-503` (code `0411c14`, doc `1128a74`). Ownership check bases: code
`126283970b49`, doc `f52e18686389` after rebasing the doc branch onto the two later claim commits leg
069 had made.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** none new (host-side test only), but this unit makes an existing debt matter more:
the 503 only reaches an operator once `core/015`'s outstanding native Windows build of `embarch-core`
is deployed — now load-bearing three times over (`core/020`'s rename, `core/021`'s SSE retirement, and
this).

---

**`core/021`** (18:15) — recovered leg 068's dead fold: both merges already ancestors of `origin/main`,
gate re-run and committed with nothing re-derived or re-read for intent. Substantive call was leg 068's
worker: `GET /logs/stream` retired (decision 7's SSE half marked gone, not rewritten).
**Merged:** `agent/core/021-retire-logs-stream` (code `1262839` in `embarch-core`, doc `6c902c7`) —
both by leg 068, both already on `origin/main`, recorded here for the first time because leg 068 never
wrote them down. Code diff `src/api.rs`, `src/logs.rs`, `src/main.rs` only — 27 insertions, 296
deletions. Gate on the merge result: `check-docs.py` 11/11 green, `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** none — a route retirement. `core/015`'s outstanding Windows build now also carries
this retirement, since the running Windows service still serves `GET /logs/stream` until deployed.

---

**`api/051`** (18:08) — landed the drain-decoding policy as its own decision 65 (`decisions/log-capture.md`)
rather than widening decision 18, on the axis argument that 18 is about a *truncated* log while the
drain fires on every line regardless of cap proximity. **Unparked `api/050`, blocked on `In flux: yes`,
by pointing at its own written unpark condition** — a verbatim split "restates nothing, so `In flux:
yes` cannot forbid one." Four missions moved to four files (`build.md`, `log-capture.md`,
`target-json.md`, `flash-address.md`); reviewer verified item-by-item against `050`'s `Must not
delete:` list.
**Merged:** `agent/api/051-drain-decoding-decision` (code none — the `embarch-api` branch carried no
commits; doc `989faa9`, cherry-picked from the branch tip `a7ac87b`, which is not a revert handle —
cherry-picked because the branch was based on `404c387` and `main` had moved to `9c15974`, and
`embarch-dev-workflow.md` §6 forbids a merge commit). Ownership check base `9c15974b52f0`: 11 paths,
all owned. Gate: `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`umbrella/047`** (18:05) — a one-line pointer fix (`decisions/doctor.md`'s `Current truth:` line
repointed at `../interfaces/doctor-chain.md`), dispatched deliberately narrow. **Also fixed a red
`main`** found underneath it: leg 067's `dev-bench/007` fold had `git rm`'d a task file that
`tasks/dev-bench/008` links to by relative path, breaking `check-links.py` for every unit since — the
gate had run before that removal was staged in leg 067's own fold. Repointed `008`'s opening paragraph
at what actually survived (decision 45, `scan_seen_names.c`, `tasks/dev-bench/015`).
**Merged:** `agent/umbrella/047-doctor-current-truth` (code none — the `embarch-umbrella` branch
carried no commits, documentation only; doc `73e7678`). Fast-forward onto `404c387`. Ownership check
base `404c387ae6db`: 4 paths, all owned. Gate: `check-docs.py` 11/11 green after the `008` fix;
`check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`dev-bench/007`** (17:41) — new `embarch-dev-bench` decision 45: two distinct overflow markers,
`(truncated)` (64-byte name-list cap) and `(census full)` (256-entry `SCAN_SEEN_MAX`), deliberately not
combined into one (would say something was cut without saying which). Rewrote `scan_seen_names_append()`
to format-then-copy-whole so a rejected entry changes nothing — closing a real underflow-adjacent bug
class. **Reviewer found the priority-order hole**: when both conditions fire, the code wrote
`(truncated)` and silently dropped `(census full)`, exactly what decision 32 forbids — filed as
`tasks/dev-bench/015` (above, landed same leg).
**Merged:** `agent/dev-bench/007-census-truncation-marker` (code `79d4743`, doc `07a5062`). Doc branch
rebased onto `ui/022`'s fold; the code branch fast-forwarded `embarch-dev-bench` `main` from `07f15bd`.
Ownership check bases: code `07f15bd4ccc2` (whole tree owned, 8 paths), doc `dc1ff1a82cce` (4 paths,
all owned). Gate: `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/dev-bench-census-marker-priority.md.
**Hardware debts:** **one, and it is the biggest of the leg.** This is the only unit of the four
that landed real code into a repo whose toolchain this environment does not have: `app/src/scan_seen_names.c` has
**never been compiled**, and the ztest suite the worker wrote for it has **never been run** — by
anyone. Landed on two careful reads. Also owes one 20-second study to re-observe the original
`fail_reason` on a real bench; an attended-leg debt, not attempted here.

---

**`ui/022`** (17:35) — implements `embarch-core` decision 54 rather than deciding anything: the
`confirmed_at_utc_ms` column renders **twice** (Dashboard and Topology/Enroll "Enrolled boards"
tables), both now labelled "Enrolled" rather than any variant of "Validated". Guard comments added at
`Snapshot::enrolled` and `enrolledTableRows`. First thing in the decision-54 chain a human can actually
see; `tasks/umbrella/045` (above, landed same leg) is the weaker remaining half.
**Merged:** `agent/ui/022-confirmed-at-label` (code `9361329`, doc `d2f52ee`). Doc branch rebased onto
`core/034`'s fold; the code branch fast-forwarded `embarch-ui` `main` from `408e3b1`. Ownership check
bases: code `408e3b17fd7c` (whole tree owned, 3 paths), doc `424f5cc00961` (2 paths, all owned). Gate:
`embarch-ui` `cargo build` clean, `cargo test` 101 passed/0 failed/3 ignored plus 2 passed in the
second target, `clippy --all-targets -- -D warnings` zero warnings; `check-docs.py` 11/11 green;
`check-client-names.py` clean against 7 denylist entries.
**Blocked:** nothing. 
**Reviewer:** no findings — swept the whole `embarch-ui` tree for a third
"Confirmed"/"Validated" sibling the relabel could have missed. **Hardware debts:** none.

---

**`core/034`** (17:26) — decided nothing new; corrected decision 50's closing sentence, which still
said three consumers were "filed and blocked" when one had landed (`api/045`, `a687baf`) and two closed
unsatisfiable (`e0dc52b`) — now forward-pointing to decision 54 for what replaced their intent.
Verification was made the deliverable rather than the edit, per dispatch instruction; reviewer
independently re-checked all three tasks and both SHAs.
**Merged:** `agent/core/034-decision-50-consumers` (code none — documentation-only, the `embarch-core`
branch was pushed with zero commits; doc `af785d8`). Rebased onto `umbrella/046`'s fold before
merging. Ownership check base `5d79b29a1934`, 3 paths, all owned. Gate: `check-docs.py` 11/11 green.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`umbrella/046`** (17:18) — took leg 066's parked option 2 as this leg's first unit: verbatim mission
split (not a compaction pass, deliberately, since `038` is blocked correctly on real flux) of
`embarch-umbrella/spec.md`'s eighteen-row `doctor`-chain table into new
`embarch-umbrella/interfaces/doctor-chain.md`. `spec.md` 10,144 → 5,795 B, entirely out of reserve.
Verified verbatim mechanically: every row identical, only link re-basing and the new header differ.
**Merged:** `agent/umbrella/046-split-doctor-chain` (code none — documentation-only, the
`embarch-umbrella` branch was pushed with zero commits; doc `fc6f738`). Ownership check base
`a2e993ab72cd`, 10 paths, all owned. Gate: `check-docs.py` 11/11 green.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/umbrella-doctor-md-current-truth-pointer-stale.md.
**Hardware debts:** none.

---

**`umbrella/036`** (16:45) — `doctor` check 6 ("embarch-api config loads") stopped answering entirely
from `embarch-umbrella`'s own hand-mirrored `ProjectConfig` — it could Pass on a config `embarch-api`
would refuse. Now shells out to the real `embarch-api --config <path> --json list-projects` via a
three-arm `LoaderVerdict` (`Ok`→Pass, `Rejected(why)`→Fail carrying `embarch-api`'s own error text,
`Unanswerable(why)`→Warn, never Pass/Fail). `artifact_path_for_core` confirmed **not** drift (decision
64, dated the same day) and kept. Supervisor's own bookkeeping correction: this unit spent, rather than
paid, `tasks/umbrella/038`'s reserve on both files, moving its size-debt clock from 2026-09-30 to
2026-09-12 — three options written into `038` including a verbatim mission split of the table
`outpost/008` proved safe under flux this same leg.
**Merged:** `agent/umbrella/036-mirrors-two-and-three` (code `6c423e1`, doc `293a647`). Ownership check
bases: code `d06bb6472fb4` (whole tree owned, 2 paths), doc `7dce408b7caf` (5 paths, all owned). Gate:
`cargo build` clean, `cargo test` 225 passed/0 failed (up from leg 051's 216), `clippy --all-targets --
-D warnings` zero warnings; `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing.
**Reviewer:** no findings — confirmed `embarch-api`'s `validate()` bails on a missing `source_path` for
every project, so the one check the new `Ok` arm skips is redundant rather than lost; the first time in
four legs of tallying a reviewer changed what the supervisor would have written, not by finding a
contradiction but by turning a merge-on-green into a merge on evidence.
**Hardware debts:** none — host-side throughout, the one thing that could have needed a board (check 6
shelling to a real `embarch-api`) is exercised by integration tests instead.

---

**`core/027`** (16:41) — `EnrolledBoardResponse` does **not** grow a persisted last-validation
timestamp; the fix is a label. New decision 54: render `confirmed_at_utc_ms` as "Enrolled", never
"Validated"/"Last validated" — a reader wanting staleness must call `POST /validate` and read
`validated_at_utc_ms` from *that* response. Declined the persist arm because `EnrolledBoard` is
`embarch-topology`'s storage (a cross-repo change, §8's not a `core` worker's) and because every board
enrolled before the field existed would come back `None`, rendered as "never validated" — a lie about
every board on the bench today. **Reviewer found decision 50, immediately above 54 in the same file,
still gave a stale status for its own three consumers** (one landed, two closed unsatisfiable) with no
pointer to 54 — filed as `core/034` (above, landed same leg), re-scoped from `doc` to `core` since
`doc` scope would have made it undispatchable to the only worker able to fix it.
**Merged:** `agent/core/027-validated-at-reaches-no-reader` (code none — the label arm needs no code,
branch pushed with zero commits; doc `56cb0b1`). Ownership check base `317795f077fb`, 4 paths, all
owned. Gate: `embarch-core` `cargo build` clean, `cargo test` 192 passed/0 failed/2 ignored plus 1
passed in the second target, `clippy --all-targets -- -D warnings` zero warnings; `check-docs.py`
11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/doc-decision-50-stale-consumer-list-after-decision-54.md.
**Hardware debts:** none, and it is the first thing this leg landed that *reduces* one — the declined
arm is the one that would have needed a store migration and a bench to prove.

---

**`outpost/008`** (16:33) — decision 6 (manual markers, build-registered IDs) moved verbatim into new
`decisions/markers.md`, freeing `decisions/tracing.md` from four days of a correct decision being
unwritable purely on byte count (thrown away by a 2026-09-06 worker when the gate refused it).
6,940/8,192 B, debt paid rather than reassigned. New decision 25 records two GPIO-dispatch traps in the
*decision*, not only `wire.md`: `GpioCallbackDone` is an exit marker (read as entry, every handler's
span attributes to the wrong handler); `GpioDispatch`'s mask is `0`, not a pin mask (8-bit hook vs.
32-bit `gpio_fire_callbacks()`, pins above 7 gone before the record is made).
**Merged:** `agent/outpost/008-gpio-family-decision` (code none — documentation-only by dispatch
instruction, branch pushed with zero commits; doc `896f9c9`). Ownership check base `3236e9ab5870`, 5
paths, all owned. Gate: `check-docs.py` 11/11 green; `check-decision-refs.py` re-run explicitly after
the split — all 18 topic-file links and all 19 reversal-row citations resolve; decision numbers 1–25
contiguous, checked by hand (`tasks/doc/033` records nothing checks this automatically).
**Blocked:** nothing. 
**Reviewer:** no findings — confirmed verbatim survival of both protected
passages in decision 19, matched decision 25's two traps against `interfaces/wire.md` field by field.
**Hardware debts:** **one, unchanged and re-stated because it is now several units deep.**
`embarch-outpost`'s Zephyr `tests/unit` ztest suite was not run (no `west`, no `ZEPHYR_BASE`) — the
standing condition, not this unit's failure; this unit changed no C or Kconfig. No leg has been able
to claim that suite green after any `embarch-outpost` change for several days.

---

**`study-designer/027`** (16:31) — `open.md`'s power-profiling deferral cited decision 24 (about the
`StudyStart`/`StudyDone` wire messages, nothing to do with an analog front end) for a hardware pick.
The worker searched for the correct number and **found none exists** — no decision records a
power-profiling front-end pick at all — and wrote "No decision records this pick; none is cited" rather
than reach for the nearest plausible number. Reviewer independently re-derived the negative and checked
the file's four other citations.
**Merged:** `agent/study-designer/027-open-md-decision-24-citation` (code none — the branch was pushed
with zero commits, correctly: this unit changed no code; doc `eb06bae`). Ownership check base
`09109e782502`, 4 paths, all owned. Gate: `check-docs.py` 11/11 green; `cargo test` / `clippy
--all-targets -- -D warnings` clean in the code worktree (0 tests); `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`core/033`** (15:28) — settled the four citations `core/032` refused to guess at, and all four
resolved cleanly. Two verified: `chip_resolve.rs`/`api.rs:1273` confirmed `embarch-dev-bench` decision
26, and a false "reversing that repo's decision 13" clause deleted (13 is unrelated — the sentence
around a defensible number was itself false); `dev_bench_link.rs:115` repointed from a nonexistent
`embarch-outpost` CRC decision to that repo's `interfaces/wire.md`, which actually states it — citing
an interface doc because no decision exists is the honest move. `api.rs:970` repointed to decision 28;
`study.rs:2471` confirmed unchanged. Also normalized ~47 sites from a worker-invented `` `decision N` ``
form back to the settled plain-prose form — zero `design.md` citations and zero competing citation
forms now remain in `embarch-core`.
**Merged:** `agent/core/033-flagged-miscitations` (code `1ba44af`, doc `b4a036e`). Ownership check
bases: code `9b8e716e5d1a` (10 paths, whole tree owned), doc `58d17c026201` after the rebase (2 paths,
both owned). Gate: `embarch-core` `cargo build` clean, `cargo test` 192 passed/0 failed/2 ignored plus
1 passed in the second target, `clippy --all-targets -- -D warnings` zero warnings; `check-docs.py`
11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings — independently confirmed all four citations, found no
reversals-index entry for any of dev-bench 13/26, outpost 5, or core 7/28.
**Hardware debts:** none — deepens the standing `core/015` Windows-build debt by one more commit.

---

**`topology/011`** (15:26) — `embarch-topology`'s CLI performed four mutations
(`enroll`/`validate`/two `set-dev-bench-link` writers) that decision 15 places inside Core, in-process
only and blind to a second process — on the one validated topology, `hardware/paths.rs`'s
`#[cfg(unix)]` resolution meant `embarch-topology enroll` from WSL wrote **a different store than Core
reads**, silently. Landed `refuse_if_core_reachable` (a refusal naming Core's base URL and route,
falling back to in-process only when no Core answers) rather than an HTTP-client routing layer,
explicitly forbidden in the dispatch note as a suite-wide cost for a CLI convenience. New decision 28.
Also fixed the refusal message's own bug (`curl -X /probes/enroll <base_url>` passed a route where curl
wants a method) as a separate commit, without inventing the unverified HTTP method.
**Merged:** `agent/topology/011-cli-mutations-lock` (code `3a9937c`, plus `3508dc8` for the
error-message fix; doc `6cba4ff`). Ownership check bases: code `2e94db47cda0` (1 path, whole tree
owned), doc `3e0b168ff9a0` (6 paths, all owned). Gate: `embarch-topology` `cargo build` clean, `cargo
test` 15 passed/0 failed across the suite's targets, `clippy --all-targets -- -D warnings` zero
warnings; `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing, one item left undone on purpose (named in decision 28): `--clear-serial`/
`--clear-interface` refuse the same way but Core's `/dev-bench/link` has no documented clear semantics
to point an operator at — `embarch-core`'s gap, not this worker's to fix.
**Reviewer:** no findings.
**Hardware debts:** **one new, and it is small but real.** The refusal path has never been exercised on
a `wsl-host` machine with the live Windows-service Core answering — the exact configuration the whole
change is about, and the only one where the wrong-store bug bites. Needs no board, only the owner's
machine with Core running: `embarch-topology validate <role>` from WSL should refuse and name the
right base URL. Until then the fix is argued, not observed.

---

**`study-designer/026`** (15:23) — a compaction pass that struck **zero bytes** and is landed as a
completed unit rather than a failure: worker checked all six of `embarch-study-designer/open.md`'s
bullets against current `spec.md`/`decisions/`/`interfaces/` and found none strikeable (reviewer
independently verified all six). `blocked` with the clock kept (due 2026-10-04) rather than `done`,
because a `done` task is deleted at the fold and would leave a 91.1%-full file with nothing filed
against it. Filed `inbox/doc-a-full-open-md-of-live-questions-has-no-payable-debt.md` — five of eight
sub-projects now carry an `open.md` in the same reserve against the same 5 KB cap, every compaction
task blocked, and this is the first hard evidence at least one has no payable form at all.
**Merged:** `agent/study-designer/026-compact-open` (code none — the `embarch-study-designer` branch is
empty by design, zero changed paths; doc `02775af`). Ownership check base `b1bce56f2c72` after the
rebase, 2 paths, both owned; code repo base `7063dc84dcec`, whole tree owned, 0 paths. Gate 11/11 green
on the merge result plus `check-client-names.py` clean; no `cargo` run against a zero-diff tree.
**Blocked:** `tasks/study-designer/026-compact-study-designer.md` — deliberately, by the worker, with a
named unpark condition and its 2026-10-04 clock intact.
**Reviewer:** no findings — also found a pre-existing citation defect this unit did not introduce (the
same decision-24 miscitation `study-designer/027` fixed, above).
**Hardware debts:** none.

---

**`umbrella/044`** (15:20) — a drop asked to replace `decision 14` with `decision 24` in
`src/manifest.rs`; leg 063's supervisor had already refused, and this unit took the third option: cite
both, with the split named ("decision 14, and decision 24 for why a mismatch is a warning rather than a
refusal"). Three independent readers (leg 063, this worker, the reviewer) reached the same conclusion
from the same two bodies without taking the task title at face value. Dispatched specifically to
complete an un-audited Done-when item (does any other `umbrella/043`-sweep comment pair 14 with 24's
claim?) — came back audited in full and negative.
**Merged:** `agent/umbrella/044-manifest-decision-14` (code `d06bb64`, doc `5c87654`). Ownership check
bases: code `ea9b72a85b7f` (1 path, whole tree owned), doc `3e0b168ff9a0` (2 paths, both owned). Gate:
`embarch-umbrella` `cargo build` clean, `cargo test` 218 passed/0 failed, `clippy --all-targets --
-D warnings` zero warnings; `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings — read both decision bodies independently and confirmed
both citations accurate. **Hardware debts:** none.

---

**`core/032`** (15:05) — the last repo's citation sweep: 170 occurrences across 14 files (filed
estimate was 68 — the fourth sweep in a row where the filed count was wrong). Of five citations with a
suspect number, resolved one with confidence and left four flagged with candidates rather than guessed,
filed as `core/033` (above, landed same leg). Verified three of the five personally, including one that
ships: `study.rs`'s shipped error string for an undeclared signal tap repointed to `embarch-topology`
decision 18 — the second leg running where a citation sweep rewrote text a real operator sees.
Deliberately did not fix in the fold a citation-form drift the sweep itself introduced (~50 sites in a
`` `decision N` `` form, a third form beside the two settled ones) — filed into `core/033` rather than
hand-patched.
**Merged:** `agent/core/032-design-md-citations` (code `9b8e716`, doc `a555eac`). Ownership check
bases: doc `29ee8e6258a7` after the rebase, 2 paths; code repo, whole tree owned. Gate: `embarch-core`
`cargo build` clean, `cargo test` 192 passed/0 failed/2 ignored, `clippy --all-targets -- -D warnings`
zero warnings; `check-docs.py` 11/11 green; `check-client-names.py` clean.
**Blocked:** nothing. 
**Reviewer:** no findings — spot-checked eleven citations independently, all
correct, no reversals-index hit for any touched number.
**Hardware debts:** none — deepens the standing `core/015` Windows-build debt.

---

**`api/055`** (14:52) — authored `embarch-api` decision 64 (retired config keys: `[[projects.targets]]`
and `soc_chip_overrides` refused by name at load; `artifact_path_for_core` not, and loads silently
unread) in `decisions/shape.md` rather than the topically obvious `decisions/zephyr.md`, which is over
its cap (14,238/12,288 B). **Reviewer found the exception's premise — "`embarch-umbrella` still
scaffolds `artifact_path_for_core` into every config it writes" — was never checked**; verified in the
source and narrower than claimed (only a static-project/WSL2-UNC path, per umbrella decisions 16/17),
rewritten and marked `[verified 2026-09-10]`.
**Merged:** `agent/api/055-retired-config-keys` (code none — the `embarch-api` branch is empty by
design; doc `2f42558`). Ownership check base `5621bb545ac5` after the rebase, 5 paths, all owned. Gate
11/11 green on the merge result plus `check-client-names.py --repo embarch-api` clean; no `cargo` run,
code tree byte-identical to `main`.
**Blocked:** nothing.
**Reviewer:** 1 finding — accepted, verified in `embarch-umbrella/src` and fixed in this fold
(`inbox/api-055-review-finding.md` deleted, having been acted on).
**Hardware debts:** none — narrows an existing one: the tolerance decision 64 records is about configs
`embarch-umbrella` writes on this machine; `umbrella/037`'s corrected check 13 still needs the
dev-bench board.

---

**`study-designer/006`** (14:51) — a repoint, not a split (correctly — the worker's first attempt
appending to `interfaces/limits.md` would have relocated a debt rather than removed it, and it
self-reverted). `spec.md` §7's closing paragraphs, which duplicated `decisions/limits.md` decision 63's
own measurement table, were cut and pointed at decision 63 by number: 9,600 → 8,941 B, out of reserve.
Supervisor overrode the worker's `blocked` (on grounds `open.md` "is still in flux") back to `open` —
an open-questions file is edited every week by design, so "in flux" applied to it is a property of the
filename, not a fact about a subsystem settling; task split into `006` (done, empty `Compacts:`) and
new `study-designer/026` (carries the unpaid `open.md` half, same clock). **Reviewer found a genuinely
homeless fact** (the 77,368-byte pre-reduction `Study` baseline and its three-pass reduction history) —
restored into decision 49, arithmetic checked (77,368 ÷ 2 ÷ 35 ≈ 1,105, against decision 63's 1,080);
the reviewer's second claim (a "97% of what remained" mismatch) was checked and found wrong.
**Merged:** `agent/study-designer/006-compact-study-designer` (code none — the
`embarch-study-designer` branch is empty by design, docs-only; doc `4705746`). Ownership check base
`5621bb545ac5` after the rebase onto `topology/019`'s fold, 3 paths, all owned. Gate 11/11 green on the
merge result. No `cargo` run: tree byte-identical to `main`.
**Blocked:** nothing. Task 006 closed `done`; surviving half is `tasks/study-designer/026-compact-study-designer.md`.
**Reviewer:** 1 finding — half accepted and fixed in this fold, half refused;
`inbox/study-designer-review-006-lost-77368-provenance.md` deleted, having been acted on.
**Hardware debts:** none.

---

**`topology/019`** (14:45) — verbatim split along a seam decision 20 itself had already drawn
("Two independent gaps, one event"): decisions 20 and 27 moved out of `decisions/enrollment.md`
(11,346/12,288 B, 92.3%) into new `decisions/link-declares.md` (8,157 B), leaving `enrollment.md` at
4,034 B. Diffed the moved text directly rather than trusting the report — byte-identical. Considered
and rejected folding into `decisions/links.md` (would push a second file over cap).
**Merged:** `agent/topology/019-compact-topology` (code none — the `embarch-topology` branch is empty
by design, a docs-only compaction with a zero-line diff; doc `867945d`). Ownership check base
`12563915c73a`, 5 paths, all owned. Gate 11/11 green on the merge result, plus
`check-client-names.py --repo embarch-topology` clean. No `embarch-topology` `cargo` run: tree
byte-identical to `main`.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none.

---

**`umbrella/043`** (14:31) — leg 062's version of this sweep was killed uncommitted (~10 minutes of
work correctly discarded per `ops.md` §3); redone from scratch. Filed for 68 across 15 files, actual 75
across 13 (third sweep running with a wrong filed count). **Four real miscitations, all the same
error**: `state.rs`, `setup.rs` (twice) and `deploy.rs` cited decision 37 (`reporting.md`'s machine-readable
`code`) for `deploy-core`'s subject; the match is decision 32 (`decisions/deploy.md`, the `deploy-core`
command itself), verified by reading both bodies. One of the four ships: `deploy.rs`'s `elevated_script`
emits an rc-file header carrying the citation onto real machines. **Supervisor refused a reviewer
finding** proposing `manifest.rs`'s `decision 14` become `decision 24` — read both bodies and 14 is the
better citation (its own third paragraph is the only text anywhere saying `doctor` reads the suite
manifest at all); left the drop in place with the counter-argument written into it rather than deleted,
since two readers stopped on the same ambiguous line independently. Resolved for real one leg later as
`umbrella/044` (above): cite both.
**Merged:** `agent/umbrella/043-design-md-citations` (code `ea9b72a`, doc `18c859d`). Ownership check
bases: code `cffed3d96c9a` (code repo, whole tree owned, 15 paths), doc `07bab8221f82` after rebasing
onto `outpost/014`'s fold, 2 changed paths. Gate green on both merge results: `check-docs.py` 11/11,
`embarch-umbrella` `cargo build`/`test` (218 tests)/`clippy --all-targets -- -D warnings` clean,
`check-client-names.py --repo embarch-umbrella` clean.
**Blocked:** nothing. 
**Reviewer:** 1 finding — inbox/umbrella-review-043-manifest-decision-14-miscite.md
(refused by the supervisor, left standing for the next reader; resolved by `umbrella/044`).
**Hardware debts:** none — the corrected rc-file header text does not reach the owner's machine until
`core/015`'s outstanding native Windows build runs `deploy-core`.
**Postscript:** correcting a task's `State:` token by hand at fold time broke the fold exactly as
`tasks/doc/028` predicts: `fold-commit.py` committed this entry to the fleet repo (`9d19d3c`) and then
refused its own second half — `git rm` will not remove a task file carrying local modifications, since
the `State:` line had been hand-edited in the same sitting. Recovered as a second commit (`ba7f742`)
with the same paths, nothing lost. **Rule for the next leg: use `git rm -f`
after a hand-edited `State:` token at fold time, or the fold half-lands.**

---

**`outpost/014`** (14:27) — a compaction that clears one file's reserve by pushing another file into
its own is not a compaction, and the worker caught its own first attempt doing exactly that (moving
`spec.md` §5's host-side-output formats into `interfaces/wire.md` cleared `spec.md` but pushed
`wire.md` to 94.8% of its own cap) — retargeted to `interfaces/integration.md` (6,096 → 7,953 B of a
12,288 B cap) instead, and reported the false start rather than hiding it. `spec.md` 9,775 → 8,316 B.
Second consecutive day the split-first rule paid without removing a single fact from the corpus
(`core/030` did the same to `embarch-core/spec.md` the day before).
**Merged:** `agent/outpost/014-compact-outpost` (code none — docs-only by design, the `embarch-outpost`
code branch had a zero diff; doc `cb64fcf`). Ownership check base `d6fefc7fe17d`, 5 changed paths, all
owned. The doc branch was rebased onto `core/008`'s fold before merging. Gate green 11/11 on the merge
result, first run, no fold fixes needed.
**Blocked:** nothing. 
**Reviewer:** no findings. 
**Hardware debts:** none — the standing outpost
toolchain debt is unchanged and correctly not claimed away (no C touched, so it is not deepened either).

---

**`core/008`** (14:24) — `embarch-core/spec.md` §4's module table was missing one row
(`outpost_manifest`); two `decision 48` comments really mean decision 36 (verified against the body).
Task said two stale `milestone-N.md` citations; there were five. **Reviewer caught a worker-invented
form**: four of the five had been repointed to `` embarch-ui milestone 1 `` on a claimed "deleted, not
indexed" convention that is not a real convention — the settled form (from `api/052`, adopted by
`umbrella/043` an hour earlier) is bare `decision M` same-repo / `` `<repo>` decision M `` cross-repo,
and the decision numbers were already sitting in the repo unused
(`decisions/surfaces.md:29` already tombstones `/enroll`'s retirement as `embarch-ui` decision 1;
`embarch-ui/decisions/wiring.md` decision 6 is verbatim the polling rule `logs.rs` describes). Fixed in
the fold after re-deriving the verdict from both bodies, not the reviewer's word — a heading-only check
(`embarch-ui` decision 1's title reads as a packaging decision) would have rejected this correct
citation; only the body says why. One adjacent look-alike (three lines away, citing
`embarch-topology/design.md`) deliberately not widened into this unit — filed as
`inbox/core-src-still-cites-a-design-md-embarch-core-no-longer-has.md`, `embarch-core` being the
fourth sub-project with this defect class and the one most cited into by the others.
**Merged:** `agent/core/008-outpost-manifest-module` (code `61bce4f`, doc `1b03ce0`), plus the fold's
own citation fix `a5daef6` in `embarch-core`. Ownership check bases: code `586b6d60f84d` (code repo,
whole tree owned), doc `b0ad6110e7cf` after rebasing onto `api/056`'s fold, 3 changed paths. Gate green
on the merge result and again after the fold fix: `check-docs.py` 11/11, `embarch-core` `cargo
build`/`test` (193 tests)/`clippy --all-targets -- -D warnings` clean, `check-client-names.py --repo
embarch-core` clean.
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/core-review-008-milestone-citation-form.md (deleted after being acted
on in the fold).
**Hardware debts:** none — comment-only plus one table row; adds a third thing riding on `core/015`'s
outstanding native Windows build.

---

**`api/056`** (14:19) — reconstruction, not a re-run. Leg 062 was killed by `fleet stop`; its worker had
already pushed both branches, and the **code half had already reached `embarch-api` `main`** while the
**doc half sat unmerged on the remote at `0a0af12` for ~22 hours** — so the suite shipped a behaviour change (`apps/`
directory discovery, `["apps","app"]` collision order) with no decision recording it for the better
part of a day. Nobody re-derived the work; the reviewer, given both worktree paths, confirmed all three
clauses of decision 63 against the implementation directly, the one check nobody had run because the
two halves were written together and landed apart. `tasks/api/057-compact-api.md` arrived with the
merge: decision 63 put `decisions/zephyr.md` 1,950 B past cap, and `embarch-api` now has six open or
blocked compaction tasks, more than any other sub-project.
**Merged:** `agent/api/056-zephyr-apps-dir` (code `d6fec7a` — already on `main` before this leg, not
merged by the supervisor; doc `be4c155` after rebasing onto this leg's claim commits, merged
`--ff-only`). Ownership check base `887a948ff735`, 6 changed paths, all owned. Gate re-run on the merge
result, not taken from the worker's report: `check-docs.py` 11/11 green, `embarch-api` `cargo
build`/`test`/`clippy --all-targets -- -D warnings` all clean on `main` (201 tests across 11 binaries),
`check-client-names.py --repo embarch-api` clean.
**Blocked:** nothing. 
**Reviewer:** no findings.
**Hardware debts:** none — narrows a reason to care about one: `list_targets` for an `apps/`-layout
repo is implemented and unit-tested but never exercised against the real repo that motivated it
(`chargerito-fw`), which is a client repo and the owner's to point EmbArch at.

---

### Standing hardware debts, carried across the whole day and still open at the fold

Unchanged throughout 2026-09-10 and not repeated per-unit above: **`core/015`'s native Windows build of
`embarch-core`** is the owner's and still outstanding — by day's end it is load-bearing for `core/008`,
`core/013`, `core/020`'s `self_reported_hardware_id` rename, `core/021`'s SSE retirement, `core/032`,
`core/033`, and `umbrella/043`'s corrected operator-facing rc-file header, none of which reach the
running service until that build lands. **`umbrella/037`'s corrected check 13** has never met the bench
that found its defects; needs only the dev-bench board. **`embarch-outpost`'s Zephyr `tests/unit` ztest
suite** cannot be built from this environment (no `west`, no `ZEPHYR_BASE` in a worker's worktree) and
this remains true even after `dev-bench/008`/`core/019` corrected the false "no toolchain at all" version
of the same claim for `embarch-dev-bench` — the two are not the same debt. **The bench queue is still
parked by the owner's own commit** — no bench unit was runnable on any leg this day.

---

*Days before 2026-09-10 already stand rolled into `log-archive/`.*
*Days 2026-09-09 to 2026-09-09 rolled to [log-archive/supervisor-log-2026-09-09-to-2026-09-09.md](log-archive/supervisor-log-2026-09-09-to-2026-09-09.md).*
