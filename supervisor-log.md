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

## 2026-09-29 21:29 — api/083 spec.md §§3-7 split verbatim into spec/implementation.md

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/api/083-compact-api-doc` (doc `ba0a2175`, cherry-picked; **no code commit** —
code branch at parity with `main`). `embarch-api/spec.md` now 3,616 B, §§1-2 plus one pointer line;
§§3-7 moved to `embarch-api/spec/implementation.md`. I diffed every removed line against the new
file: identical except relative-link depth (`decisions/` → `../decisions/`). Fragment
`api-spec-implementation-split.changed.md` folded into `history/api.md`. Task removed; the size
ledger no longer lists `api/083` as overdue. Gate: `check-docs.py` 11/11, ownership clean on 4 paths.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.3%, wave 6.
**Least sure about:** `spec/implementation.md` is a new top-level-ish doc; the supervisor ownership
check at leg end is what tells whether it needs the owner to classify it.

**Leg close, for the next leg.** Recovery leg: 4/4 units, all four were the previous leg's claims.
Its workers were alive at my step 0 (two dirty trees), finished and pushed; I landed them — no
re-dispatch, no new claims. Queue **7 dispatchable** at close. Overdue ledger: `suite/030`
(blocked) and `doc/031` (owner-only) only. Stale remote `embarch-doc` branches from older legs
still exist (`api/096-…-doc`, `core/052-…`, `ui/059-…` also in `embarch-ui`) — not mine, not
touched; worth a look. Did not drain or sweep: inbox empty, and a recovery leg at cap has no slot.
Two self-inflicted fold refusals: I matched the log by the heading time I typed, and `fold-commit.py`
had restamped it; re-read the heading before each prepend.

---

## 2026-09-29 21:28 — core/095 /load doc comment cites decision 62

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/core/095-load-handler-decision-62-cite` (code `2590885`, fast-forward;
doc `68c7d0ee`, task close, cherry-picked). `src/study.rs` `stream_load_handler`'s comment now
says "(decision 62; suite decision 4)" instead of a file path. Gate on the merged tree: clippy
`-D warnings` clean, `cargo test` green, ownership + client-names clean, `check-docs.py` 11/11.
**No native Windows build**: the diff is one doc comment, which cannot change it; said here so it
is not mistaken for a run. Task removed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.3%, wave 6.
**Least sure about:** skipping the Windows build on a comment-only diff is my reading, not a written exemption.

---

## 2026-09-29 21:26 — ui/076 study-designer decision links repointed at the index

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/ui/076-repoint-study-designer-links-doc` (doc `e810317e`, cherry-picked onto
`276a92b8`; **no code commit** — doc-only). `embarch-ui/decisions/gatt-capture.md` (56) and
`designer-panels.md` (33, 78) now link `embarch-study-designer/decisions.md`, not
`decisions/gatt-extract.md` — which unblocks a future split of that topic file (see the
`study-designer/069` entry). `changelog.d/ui-decision-links-repoint-index.changed.md` folded into
`history/ui.md`. Task removed. Gate: `check-docs.py` 11/11; ownership clean on 4 paths.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.3%, wave 6.
**Least sure about:** the reviewer read at the merge SHA in the owner checkout rather than my leg
worktree; it used `git show <sha>`, so the read is exact, but it did not follow the path it was given.

---

## 2026-09-29 21:25 — study-designer/066 decisions.md file count made unstale

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/study-designer/066-decisions-md-no-count-doc` (doc `276a92b8`, fast-forward;
**no code commit** — doc-only task). "these twenty files" became "the files under `decisions/`".
Table census clean: 78 decisions, 20 rows for 20 files, every number in exactly one row. No
changelog fragment (not reader-facing). Task removed. Gate: `check-docs.py` 11/11; ownership clean
on 2 paths. Recovered from the previous leg's handoff: this worker had pushed before it died.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 23.3%, wave 6.
**Least sure about:** nothing material; a one-sentence edit.

---

## 2026-09-29 21:19 — study-designer/069 gatt-extract.md squeezed out of reserve; the split was blocked by ui's links

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/study-designer/069-compact-gatt-extract-doc` (doc **`0e23aba4`**, rebased by me
onto `c6580928`; **no code commit** — the code branch was pushed at parity with `main`).
`decisions/gatt-extract.md` 12,252 → 11,053 B (89.9%, just under the floor). Squeeze, not split:
`embarch-ui/decisions/gatt-capture.md` and `designer-panels.md` link decisions 33/56/78 at this
topic file's path, so moving 33 would turn `check-decision-refs.py` red in a scope the worker could
not write. Every cut hunk is quoted in the task file; the three protected clauses (57's failure
modes, 56's rejected `name` field, 78's union argument) are verbatim. The worker's inbox drop is
filed as **`tasks/ui/076`** (repoint those links at `decisions.md`), which is what unblocks a
future split. Task closed and removed; `changelog.d/study-designer-gatt-extract-reserve.changed.md`
folded into `history/study-designer.md`. Gate: `check-docs.py` 11/11; `check-ownership.py --scope
study-designer` clean on 3 paths. Size ledger **4 → 3 overdue**, all three owner-only or blocked.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 22.0%, wave 6.
**Least sure about:** 89.9% is under the floor by about 6 bytes' worth of rounding, so the next
amendment to 33/56/57/78 puts this file straight back in reserve. `ui/076` is the real fix, and it
should land before anyone adds to this file again.

**Leg close, for the next leg.** 4/4 units, all green, no reds, no blocks; one code commit
(`embarch-api` `0ee185f`, a comment). Filed `doc/086` (owner-only) and `ui/076` from `inbox/`;
workers filed `ui/075`. Queue **10 dispatchable** at close. Overdue ledger is now `suite/030`,
`doc/031` (owner-only) and **`api/083`** (`embarch-api/spec.md`, blocked on flux but names its own
§§1-2 vs §§3-7 seam — the next leg's first unit if it unparks it the way `core/093` was).
Bench: dev-bench `001057729826` not attached at step 0; `api/059`, `dev-bench/035` stay `open`.
Refill was owed on scope spread; no thin scope's `open.md` changed since the 09-28 sweep, so I did
not re-sweep. `inbox/` empty at close. No `suite` window open. Folded 2026-09-28 in the `core/084`
fold. **One slip**: at the `ui/069` fold I passed `build_changelog.py --only` a fragment the owner wrote
(`ui-launcher-focus-existing-tab.changed.md`, touched by that unit's link fix); I noticed before
committing, restored it, and it is still pending.

---

## 2026-09-29 21:16 — ui/069 shape.md and spec.md out of reserve by two verbatim splits

**Decided:** nothing. No new numbered decision.
**Merged:** `agent/ui/069-compact-ui-doc` (doc **`6e5a8c33`**, rebased by me onto `624426ae`; **no
code commit**). Decisions 3 + 28 moved verbatim from `embarch-ui/decisions/shape.md` into new
`decisions/launcher.md` (shape.md 12,194 → 2,079 B; launcher.md 10,373 B); the five-tab table moved
verbatim from `spec.md` into new `spec/tabs.md` (spec.md 11,022 → 9,275 B, was **over** cap;
tabs.md 2,435 B). `decisions.md` group table split into two rows; the one inbound citation
(pending fragment `changelog.d/ui-launcher-focus-existing-tab.changed.md`) repointed. `spec.md` is
still in reserve (965 B left), so the worker filed **`tasks/ui/075`**, `open`, due 2026-10-20.
`tasks/ui/069` closed and removed; `changelog.d/ui-compact-shape-and-spec.changed.md` folded into
`history/ui.md`. **I left `ui-launcher-focus-existing-tab.changed.md` pending** — it belongs to the
owner's decision-28 commit `615b57bd`; this unit only edited its link. Gate: `check-docs.py` 11/11;
`check-ownership.py --scope ui` clean on 9 paths.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 22.0%, wave 6.
**Least sure about:** the worker's report said `ui/075` was `blocked` on `tasks/ui/070`, but the
file on `main` says `open` — and `ui/070` is done (owner, 2026-09-17), so `open` is the right state;
the report was wrong, not the file.

---

## 2026-09-29 21:15 — api/120 main.rs cites study-designer decision 63 instead of a renumbered spec section

**Decided:** nothing.
**Merged:** `agent/api/120-main-rs-spec-section-cite` (code **`0ee185f`**, fast-forward, one comment
line in `src/main.rs`; doc **`624426ae`**, rebased by me onto the `core/084` fold). No other
`spec.md §` citation in `embarch-api`. Task closed and removed;
`changelog.d/api-spec-section-cite.fixed.md` folded into `history/api.md`. Gate on the merge result:
`cargo build`/`test` (226 passed)/`clippy --all-targets -- -D warnings` green;
`check-client-names.py` clean; `check-docs.py` 11/11; `check-ownership.py --scope api` clean.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 22.0%, wave 6.
**Least sure about:** nothing material; a one-line comment repoint the reviewer matched to the
right decision's subject.

---

## 2026-09-29 21:11 — core/084 every row of core's decisions.md size column checked against wc -c

**Decided:** nothing. Leg start `1337a148`. At step 0 I filed the one inbox drop as
**`tasks/doc/086`** (a refused `fold-commit.py` does not stop a push chained behind it;
`Owner: required`) and folded 2026-09-28 via `embarch-log-folder` (16 units, 65/65 SHAs kept) in
this commit.
**Merged:** `agent/core/084-size-column-pass-doc` (doc **`dea691e2`**, fast-forward; **no code
commit** — docs-only). 14 of 17 rows in `embarch-core/decisions.md`'s size column were stale, not
just the `surfaces.md` outlier the task named; all corrected. `surfaces.md` itself untouched (still
parked under `core/091`). Task closed and removed; `changelog.d/core-decisions-size-column.fixed.md`
folded into `history/core.md`. Gate: `check-docs.py` all 11 green; `check-ownership.py --scope
core` clean on 3 paths.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. At step 0 `validate dev-bench`: probe `001057729826` not attached, not a
mismatch — `api/059` and `dev-bench/035` stay `open`.
**Budget:** PROCEED, weekly 22.0%, wave 6 (4 units, all dispatched at once).
**Least sure about:** whether a hand-maintained size column is worth keeping at all when it drifted
on 14 of 17 rows in ~12 days; a script could print it. Not filed — `check-doc-size.py` is the
owner's.

---

## 2026-09-28 — 16 units

*Folded by an `embarch-log-folder` leg, 2026-09-29, from sixteen unit entries (15:49–18:00). Per-unit
narrative reasoning is dropped; every SHA, every `**Reviewer:**` line and the one real hardware debt
survive below. This was the fleet's first day back after the 2026-09-17→09-28 stop; `main`'s doc-size
gate was RED on arrival (three expired clocks) and the leg's first eight units were split/squeeze
compactions paying that debt down, several unparking `In flux: yes` tasks whose own stated conditions
had lapsed or been satisfied by a verbatim move.

**Units, oldest first:**

1. **dev-bench/012** 15:49 — `spec.md`/`open.md` squeezed out of reserve (doc **`267bd791`**, base
   `edc278bb`). Unparked on its own 2026-09-22 clock. Decided: a leg arriving on a red `main` pays the
   red first, judging each unit on "adds no new red" until paid. Also folded 2026-09-17 (50 units,
   119 SHAs, done by an `embarch-log-folder`) and rolled 09-16. Slip: claim commit **`d9b9d246`** for
   `ui/073` also deleted this task's retired file (harmless, on `main`). Filed `tasks/doc/085`
   (leg-worktree `check-links.py` red on `embarch-ui/decisions/study-authoring.md` via owner commit
   `685b691c`; fixed with a symlink). Bench state: dev-bench probe **`001057729826`** not attached;
   DUT probe **`000852006107`** attached but USB Communication Error; Core's recorded DUT hardware ID
   now `2f77b9c3f85b29e9`, `fleet-hardware.py`'s stale buffer still says `834f2559f10a6cdf`.
**Reviewer:** no findings.
**Hardware debts:** none created.

2. **ui/071** 15:50 — `embarch-ui/open.md` compacted to 4,867 B, evidence moved into
   `decisions/trace-rows.md` and `decisions/time-chart.md` (doc **`48fe7e02`**, base `267bd791`),
   including the **`b1e9ec7d`** GATT-vs-trace placement result. Filed `tasks/ui/074` (blocked,
   `In flux: yes`, due 2026-10-05) for the remainder.
**Reviewer:** no findings.
**Hardware debts:** none created. Two open halves kept, both hardware, neither ever run: the
   live-Core `/study/{id}/streams` HTTP cost over three calls, and a power-capture check of placement.

3. **core/094** 15:56 — decision 74 moved to new `decisions/outpost-preflight.md` (doc **`fe7c52c9`**,
   base `9f4fffbf`; code base `48dc591`, zero commits). Supervisor repointed the `embarch-ui`
   `firmware-build.md:7` link the split broke, at landing rather than filing a task (not announced
   first, named here per `.claude/leg.md`). Worker added a 72-byte pointer in `interfaces/studies.md`
   against the dispatch note, judged needed by the reviewer.
**Reviewer:** no findings.
**Hardware debts:** none created — decision 74's own hardware evidence (three reads on nff_dev@7,
   171–258 ms, `after_reset=false`, 2026-09-19) moved with it unchanged.

4. **ui/073** 16:02 — two verbatim splits: decisions 8/25/42 out of `shell.md` into
   `decisions/design-system.md`; decision 44's two sections out of `topology-boards.md` into
   `decisions/saved-benches.md` (doc **`ffee1b77`**, base `55adb798`; code base `ad49a7a`/`ad49a7ae`,
   zero commits). Worker also repointed a pending fragment it did not write (owner's
   `changelog.d/ui-brand-token.added.md`, decision 25 → `decisions.md`). First green `check-docs.py`
   (all 11) on `main` since the clocks expired.
**Reviewer:** no findings.
**Hardware debts:** none created.

5. **core/092** 16:38 — `arrivals`/`load`/`load/spans` rows moved from `interfaces/studies.md` into
   new `interfaces/streams.md` (doc **`d6820f76`**, base `53211671`; code base `48dc591`, zero
   commits).
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move, no source change, no native Windows build owed.

6. **api/118** 16:44 — decision 59's parenthetical amended in place (`SignalLink` stopped being called
   a mirror) (doc **`968f37f0`**, base `4f465dce`; code base `2ebcfe4`, zero commits). Reviewer found,
   below its bar, that decision 72's "seven" retired mirrors vs. six named types is pre-existing
   (authored **`c62cc870`**, 2026-09-12) — filed as `tasks/api/119`.
**Reviewer:** no findings.
**Hardware debts:** none created — one parenthetical.

7. **dev-bench/014** 16:48 — decisions 30/35 moved to new `decisions/link-limits.md` (doc
   **`3df6d63b`**, base `a9ce7fb5`; code base `edc278bb`, zero commits). Unparked at claim
   (**`7909f091`**) on its own lapsed clock: `link.md` untouched since **`84243a33`** (2026-09-08).
   Slip: a refused first fold attempt
   still let `git push origin HEAD:main` run (`| tail` ate the exit status) — same pattern as
   `core/046` below; two legs in a row.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

8. **study-designer/067** 16:52 — `.eap` constants split from `interfaces/limits.md` into new
   `interfaces/eap-limits.md`; decision 71 moved to `decisions/payload-meaning.md` (doc **`5f1ba9ab`**,
   base `171e0013`; code, zero commits).
**Reviewer:** no findings.
**Hardware debts:** none created — two verbatim moves.

9. **ui/072** 17:08 — decision 14 split into new `decisions/project.md` (doc **`28989725`**, base
   **`b41e1531`**; code base `ad49a7ae`, zero commits, fast-forward, no rebase). Slip noted: a
   dispatch-time worktree add resolved a relative path inside the repo instead of beside it; caught
   and moved before any worker started, nothing committed there.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

10. **core/093** 17:13 — decisions 70/72/73 split into new `decisions/streams-live.md` (doc
    **`02e6ff79`** + **`439fea1c`**, base `d63b3752`; code base `48dc591`, zero commits). Unparked at
    claim (**`bebb1a64`**): its `In flux: yes` block (72/73 unvalidated on hardware) does not forbid
    the verbatim-move remedy the task itself named; flux otherwise unlapsed (bench still unplugged).
    Supervisor repointed `embarch-ui/decisions/live-study.md:30` (decision 70) at landing. Filed
    `tasks/core/095` from the reviewer's aside (unnumbered decision citation in `src/study.rs`).
**Reviewer:** no findings.
**Hardware debts:** none created. Decisions 72 and 73 are still unvalidated on hardware — a traced
    study with the outpost bridge attached — the split moved that debt, it did not pay it.

11. **study-designer/068** 17:19 — decision 77 split from `decisions/declares.md` into new
    `decisions/builds.md` (doc **`837d7696`**, base `3edfeb20`; code base `15087ae`, zero commits).
    Supervisor repointed `embarch-ui/decisions/firmware-build.md:7` to the index (`decisions.md`),
    a different repoint convention than `core/093`'s topic-file repoint one unit earlier. Rewrote
    `tasks/study-designer/066`'s now-false premise (seventeen files → twenty) and left it open.
**Reviewer:** no findings.
**Hardware debts:** none created — a move and two pointers.

12. **umbrella/088** 17:23 — `check-15` bullet corrected to stop saying the hash is unbuilt;
    `open.md` squeezed 4,372 → 3,905 B (doc **`61e13c92`**, base `9140247e`; code base `2764e89`,
    zero commits). Worker declined to consume `binary_sha256` in check 15 itself — a real behavior
    change needing its own decision — and filed `tasks/umbrella/089` (below) instead. Reviewer noted
    pre-existing stale text in `open.md`'s own "why `saved.host` was left unfixed" item.
**Reviewer:** no findings.
**Hardware debts:** none created. `open.md` bullets carrying debts unchanged in substance: check
    13 (one `doctor` run on the primary bench), check 5 (a Linux box with Core native), decision 51's
    three-step real-machine confirmation.

13. **study-designer/032** 17:47 — §4 ("What a study carries") moved to new
    `embarch-study-designer/spec/carriage.md`; §§5/6/7 renumbered to §§4/5/6 (code **`b9a2d5d`**,
    base `15087ae`; doc **`22dc629c`**, base `12731da4`). Unparked at claim (**`22fa5c9b`**): §4's
    last edit was **`ac9c2116`** (2026-09-18), a full leg quiet as the task's own unpark condition
    required. Filed `tasks/api/120` for the one repointed citation the worker couldn't reach
    (`embarch-api/src/main.rs:538`).
**Reviewer:** no findings.
**Hardware debts:** none created — a move, a renumber and a comment.

14. **core/046** 17:52 — decisions 42/46/60 moved to new `decisions/route-sweep.md`;
    `auth.md` 11,356 → 3,799 B (code **`fdb9b1d`**, base `48dc591`; doc **`7c5ad6f9`**, rebased from
    **`2e6173ea`** onto `1a42bea3`). Unparked at claim (**`9701f722`**): the task's own prediction ("the next new HTTP
    route ... likely to land here") was falsified by four routes landing in `build_router` elsewhere
    since **`f6e23215`** (2026-09-12) — `4251af3`, **`d73a73a`**, **`e50de6d`**, **`f832043`** — none
    touching `auth.md`. Supervisor corrected the worker's Size cell (2.9 KB claimed vs. measured
    3.8 KB). Slip: same refused-fold-still-pushed pattern as `dev-bench/014` — **`7c5ad6f9`** reached
    `origin/main` a few minutes before its fold.
**Reviewer:** no findings.
**Hardware debts:** none created. The `api.rs` change is a comment, so no native Windows build
    owed for it.

15. **api/111** 17:56 — decisions 71/73/76 moved to new
    `embarch-api/decisions/validate-kind.md` (code base `2ebcfe4`, zero commits; doc **`0f0dc2cb`**,
    base **`cce10a88`**, rebased from `1cd74544`). Unparked at claim (**`65b9e019`**): the task's own
    second unpark condition ("once the file is judged safe to split") is satisfied by its own named
    seam.
**Reviewer:** no findings.
**Hardware debts:** none created — a verbatim move.

16. **umbrella/089** 18:00 — check 15 now hashes the located `embarch-core` binary once
    `core_version` already matches and compares it to `/status`'s `binary_sha256`; a mismatch is
    **Warn**, never Fail; missing hash on either side falls back to the old version-only Pass (code
    **`b55809c`**, fast-forward onto **`2764e89`**; doc **`1d85a3dd`**, rebased from **`57c380dd`**
    onto **`127d98fb`**). Wrote `embarch-umbrella` decision 56; amended decision 34 as "narrowed, not
    retired". Filed `tasks/umbrella/090` (blocked on the hardware debt below, due 2026-10-19).
**Reviewer:** no findings.
**Hardware debts:** **two `doctor` runs on the primary bench machine**, recorded in `open.md`'s
    check-15 bullet: one against the installed Core at a matching version and binary, confirming the
    new closed-gap Pass renders; one against a deliberately stale same-version install, confirming
    the new Warn fires with a sensible fix line. Either one also unparks `tasks/umbrella/090`. No live
    Core was touched.

**What the next leg cannot recover from git alone:**

- **The owner posted `fleet stop` in #embarch-fleet at 18:00:14** (`ts` **`1790640014`**.685759),
  during the last unit's fold; seen at 18:02 after all four of that leg's units had landed. Nothing
  was in flight; the leg deleted `.fleet/pump` and posted its stop line in the thread. **No successor
  leg should start.**
- **`| tail` eats the push exit status.** Twice this day (`dev-bench/014`, `core/046`) a refused fold
  attempt still let the chained `git push origin HEAD:main` run, landing the worker's commit on
  `origin/main` a few minutes ahead of its fold entry — legal but a pattern now, and
  `fold-commit.py` refusing is not sufficient while the push rides the same `&&` chain behind a pipe.
- **Six `In flux: yes` tasks were unparked at claim this day** (`dev-bench/012`, `core/093`,
  `study-designer/032`, `core/046`, `api/111`, plus `dev-bench/014`'s own-clock lapse), each on the
  task's own stated condition or the split-first rule that a verbatim move restates nothing — but
  nothing besides these log entries records that "the supervisor decides the park no longer applies"
  is now the fleet's normal path out of `blocked`.
- **Two different repoint conventions for a cross-repo link a split breaks** now coexist:
  `core/093`→`ui/live-study.md` pointed at the new topic file; `study-designer/068`→
  `ui/firmware-build.md` pointed at the index. Both pass the gate; `tasks/doc/055` is the owner's to
  settle which is canonical.
- **Decision 44 (`embarch-ui`) now spans two files** (`topology-boards.md` and the new
  `decisions/saved-benches.md`), indexed as `44 (saved bench)` — a precedent already set by decision
  10, but `check-decision-refs.py` cannot tell which half a bare citation means.
- **`tasks/api/119`** (decision 72 says "seven" retired mirrors, names six) may be a bigger defect
  than a miscount — `api/117`/`118` both repeated "seven" from the heading, so a seventh retired
  mirror may be undocumented; settle it from `git show c62cc870`, not from either doc.
- Two bench probes are still the live blocker for `tasks/api/059` and `tasks/dev-bench/035`: dev-bench
  probe **`001057729826`** not attached; DUT probe **`000852006107`** attached but unopenable
  (USB Communication Error) — neither is a mismatch, and `fleet-hardware.py`'s buffer is stale
  (says `834f2559f10a6cdf`/attached, real ID is now `2f77b9c3f85b29e9`).
- Size ledger moved **20 overdue → 4 overdue** across the day (`dev-bench/012` start, `umbrella/089`
  close). Oldest remaining payable overdue at close: `study-designer/069` (`gatt-extract.md`, 36 B
  left, due 09-27) and `api/083` (blocked on flux, names its own split seam). `suite/030` and
  `doc/031` remain owner-only. Queue at close: 12 dispatchable over 4 scopes.
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
