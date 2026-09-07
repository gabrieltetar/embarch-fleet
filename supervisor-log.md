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
  (one client project, name redacted) setting `build_command`, `artifact_path`, `chip`,
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
*Days 2026-09-04 to 2026-09-04 rolled to [log-archive/supervisor-log-2026-09-04-to-2026-09-04.md](log-archive/supervisor-log-2026-09-04-to-2026-09-04.md).*
