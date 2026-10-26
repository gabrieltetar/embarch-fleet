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

## 2026-10-25 23:57 — chat/001 a message the CLI sends Claude is never an owner bubble

**Decided:** nothing beyond the worker's own decision 89 (a CLI-sent `user` line is a `note` row,
never a user entry; panel-written lines with `turnOrigin: "sdk"` and no `origin` stay the owner's
as the one exception). The fleet's first `chat` unit: set up `.worktrees/embarch-chat/` with
`embarch-doc`, `embarch-fleet` and `embarch-desk` links beside the code worktree. Filed
`tasks/chat/003` (a CSS comment cites a nonexistent decision 90; fold into chat/002).
**Merged:** `agent/chat/001-cli-turns-are-not-the-owners` (code `82b82e0`, ff; doc `c25be23c`,
cherry-picked from `98c6ec25`). Gate re-run on the merge: `npm run build`, `typecheck` clean,
`npm test` 216 pass / 0 fail / 67 skipped (desk tests, no `EMBARCH_DESK_BIN`), `test:webview` all
pass, client names clean, `check-docs.py` 11/11. First `history/chat.md` created by the assembler.
**Blocked:** nothing. `tasks/chat/002` (the hand-back card) is now unblocked by this landing.
**Reviewer:** no findings.
**Hardware debts:** none. Not installed: the `.vsix` is the owner's to rebuild.
**Budget:** PROCEED, weekly 47.5%, wave 6.
**Least sure about:** the idle-turn case where the CLI never starts a turn was not recorded;
decision 89 marks it assumed, and its row is dropped at the owner's next message.

## 2026-10-25 23:55 — study-designer/026 open.md under its cap; main's doc gate green again

**Decided:** unparked `study-designer/026`: its own unpark condition ("any bullet gets a real
answer") fired on 2026-09-17 when owner commit `685b691c` closed the authoring-path bullet and moved
it to a Closed section, taking `open.md` 327 B over cap; overdue since 2026-10-04, it made
`check-doc-size.py` red on `main`. Re-parked it `blocked` after the pay (still in reserve, nothing
live is payable). Filed `tasks/topology/060` and `tasks/dev-bench/040` (both `blocked`, due
2026-11-01, split-first) for three files the owner's 2026-10-06..13 commits put in reserve unfiled
(`embarch-topology/decisions/enrollment.md`, `embarch-topology/spec.md`, `embarch-dev-bench/spec.md`):
the over-cap red had masked them, and filing them is what turns the gate green.
**Leg start, for the record:** first leg after a 26-day gap; drained all 50 inbox drops into the
queue (`ee7d80c1`, numbers in its message; doc/089 added: `gate.md` has no Python bullet, so no
`atlas` task was dispatched). Folded 2026-09-29 and rolled 2026-09-17 (`3030aed`). Linked
`embarch-dev-bench` beside the doc worktrees (`.worktrees/embarch-doc/embarch-dev-bench`), which
clears the worktree-only `check-links` red on `decisions/pd-bench.md` (`tasks/doc/085`'s shape).
**Merged:** `agent/study-designer/026-compact-open-md` (doc `3f33bc0c`, `91294f77`, ff; no code).
`open.md` 5,447 → 4,473 B: the whole Closed section went; decision 75, the authoring decision's
RunProtocol amendment and `interfaces/eap.md` carry what it said. Gate on the merge: 11/11 green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `validate dev-bench` at step 0: probe `001057729826` not attached, not a
mismatch; Core sees only J-Link `000852006107`. `api/059`, `dev-bench/035` stay `open`.
**Budget:** PROCEED, weekly 47.5%, wave 6 (4 units dispatched at once).
**Least sure about:** re-parking 026 rather than leaving the worker's `open`: it keeps the next leg
off a file with nothing payable, but the debt stays overdue on a park, which is the shape the
ledger's clock exists to revisit.

## 2026-09-29 — 17 units

*Folded by the leg of 2026-10-25 from 17 entries (~21 KB): per-unit narrative, gate transcripts, "least sure about" musings and leg-close prose went; git holds them. Last activity before a ~4-week gap.*

**Standing items for the next leg**
- `tasks/core/091` is paid (`surfaces.md` 89.9% after core/089) but still on disk: my `git rm` was classifier-refused twice (the api/121 rm went through). Owner must remove it.
- Windows-only findings from api/108 (two unused imports in `embarch-core-client/src/token_discovery.rs`, `config::` fixture bug with backslash TOML paths) are closed by api/121; nothing left to file.
- `api/108`: decision 75 keeps its unix-only qualifier and `tasks/api/108` stays `open`, because the kill path has never run on Windows. Do not mark it done or drop the qualifier without a real-Windows kill of a timed-out forked tree.
- Overdue size debts `suite/030` (blocked) and `doc/031` (owner-only) wait on the owner; reserved paths.
- Stale remote `agent/*` branches nobody owns: `api/096-...-doc`, `core/052-...`, `ui/059-...` (also in embarch-ui), and `core/081-...-doc` (its second commit `6f42cf62` task-file only, deliberately not landed). Worth a look.
- Owed: native Windows build of `embarch-core` (core/090, `src/flash_backend.rs`); owner runs it from the main checkout.
- `tasks/ui/078-compact-ui.md` overlaps older open ui compaction tasks 021/043; not reconciled. `tasks/ui/078` set `blocked` (due 2026-10-13). `tasks/doc/087` is `Owner: required` (DOC-COMPACTION-PASS.md reserved); `tasks/doc/086` likewise (a refused `fold-commit.py` does not stop a chained push; use no `| tail` masking its exit). `ui/075` squeezed to 9,031 B vs 9,040 B reserve line; reviewer finding below is still in `inbox/`.
- Pending owner fragment `changelog.d/ui-launcher-focus-existing-tab.changed.md` left in place on purpose (owner commit `615b57bd`).
- Use absolute paths when creating worktrees (relative path under `git -C` landed them inside the repos).
- Bench: dev-bench probe `001057729826` not attached at step 0, not a mismatch; `api/059` and `dev-bench/035` stay `open`.

**Merged** (no code commit means doc-only; every merge ff or cherry-picked, gate green, docs 11/11)
- core/084: doc `e3b57ea6` (leg start `f411caa1`). 14 of 17 rows of core `decisions.md` size column corrected.
- api/120: code `5c6b199`, doc `64faa5f3`. main.rs cites study-designer decision 63.
- ui/069: doc `efa77706` (rebased onto `64faa5f3`). Decisions 3+28 split to `decisions/launcher.md`, tabs table to `spec/tabs.md`; filed ui/075.
- study-designer/069: doc `7301e0a5` (rebased onto `2966a95b`). gatt-extract.md squeezed to 89.9%; filed ui/076.
- study-designer/066: doc `df01f487`. File count made unstale.
- ui/076: doc `30b3e169`. Decision links repointed at the index.
- core/095: code `2590885`, doc `129b38aa`. /load comment cites decision 62; no Windows build (comment-only diff).
- api/083: doc `43b9d2b4`. spec.md §§3-7 split verbatim into `spec/implementation.md`.
- core/090: code `ae66d3f`, doc `f3cb903e`. `nrfutil_erase_options()` extracted and tested.
- api/119: doc `b3085b2a`. Decision 72 mirror count is six; drained `history-api-seven-should-be-six.md`.
- ui/075: doc `e4167090`. spec.md 9,275 to 9,031 B.
- core/081: doc `55e2b314` (from `ba07d029`; `6f42cf62` not landed). Stale decision-64 bullet removed.
- core/083: doc `bc355356`; core/089 claim `d1991ea2`.
- ui/077: doc `5df5d116`. "served by the binary" restored; filed ui/078.
- core/089: doc `2aa45f64` (rebased from `bc094a7c`). Decision 59 citations restored.
- api/108: code `cfa8197`, doc `f97d7a3a`. Windows Job Object tree-kill; task stays open.
- api/121: code `b01f203`, doc `67dbe33b`. Windows reds fixed (`toml_path()` test helper). Worker's code commit lacks Co-Authored-By.

**Blocked:** nothing.

**Reviewer:** no findings. (api/121)
**Reviewer:** no findings. (api/108)
**Reviewer:** no findings. (core/089)
**Reviewer:** no findings. (ui/077)
**Reviewer:** no findings. (core/083)
**Reviewer:** no findings. (core/081)
**Reviewer:** 1 finding — inbox/ui-075-dropped-served-by-binary.md (ui/075; restoring the phrase landed as ui/077)
**Reviewer:** no findings. (api/119)
**Reviewer:** no findings. (core/090)
**Reviewer:** no findings. (api/083)
**Reviewer:** no findings. (core/095)
**Reviewer:** no findings. (ui/076)
**Reviewer:** no findings. (study-designer/066)
**Reviewer:** no findings. (study-designer/069)
**Reviewer:** no findings. (ui/069)
**Reviewer:** no findings. (api/120)
**Reviewer:** no findings. (core/084)

**Hardware debts:** native Windows build of `embarch-core` owed (real code change in `src/flash_backend.rs`); owner runs it from the main checkout.

**Budget:** PROCEED throughout, weekly 22.0% to 29.3%, wave 6.
## 2026-09-28 — 16 units

*Folded by an `embarch-log-folder` leg, 2026-09-29, from sixteen unit entries (15:49–18:00). Per-unit
narrative reasoning is dropped; every SHA, every `**Reviewer:**` line and the one real hardware debt
survive below. This was the fleet's first day back after the 2026-09-17→09-28 stop; `main`'s doc-size
gate was RED on arrival (three expired clocks) and the leg's first eight units were split/squeeze
compactions paying that debt down, several unparking `In flux: yes` tasks whose own stated conditions
had lapsed or been satisfied by a verbatim move.

**Units, oldest first:**

1. **dev-bench/012** 15:49 — `spec.md`/`open.md` squeezed out of reserve (doc **`0c528a9f`**, base
   `edc278bb`). Unparked on its own 2026-09-22 clock. Decided: a leg arriving on a red `main` pays the
   red first, judging each unit on "adds no new red" until paid. Also folded 2026-09-17 (50 units,
   119 SHAs, done by an `embarch-log-folder`) and rolled 09-16. Slip: claim commit **`b25a513f`** for
   `ui/073` also deleted this task's retired file (harmless, on `main`). Filed `tasks/doc/085`
   (leg-worktree `check-links.py` red on `embarch-ui/decisions/study-authoring.md` via owner commit
   `685b691c`; fixed with a symlink). Bench state: dev-bench probe **`001057729826`** not attached;
   DUT probe **`000852006107`** attached but USB Communication Error; Core's recorded DUT hardware ID
   now `2f77b9c3f85b29e9`, `fleet-hardware.py`'s stale buffer still says `834f2559f10a6cdf`.
**Reviewer:** no findings.
**Hardware debts:** none created.

2. **ui/071** 15:50 — `embarch-ui/open.md` compacted to 4,867 B, evidence moved into
   `decisions/trace-rows.md` and `decisions/time-chart.md` (doc **`6d204cd3`**, base `0c528a9f`),
   including the **`b1e9ec7d`** GATT-vs-trace placement result. Filed `tasks/ui/074` (blocked,
   `In flux: yes`, due 2026-10-05) for the remainder.
**Reviewer:** no findings.
**Hardware debts:** none created. Two open halves kept, both hardware, neither ever run: the
   live-Core `/study/{id}/streams` HTTP cost over three calls, and a power-capture check of placement.

3. **core/094** 15:56 — decision 74 moved to new `decisions/outpost-preflight.md` (doc **`1a05988c`**,
   base `91b9736b`; code base `48dc591`, zero commits). Supervisor repointed the `embarch-ui`
   `firmware-build.md:7` link the split broke, at landing rather than filing a task (not announced
   first, named here per `.claude/leg.md`). Worker added a 72-byte pointer in `interfaces/studies.md`
   against the dispatch note, judged needed by the reviewer.
**Reviewer:** no findings.
**Hardware debts:** none created — decision 74's own hardware evidence (three reads on nff_dev@7,
   171–258 ms, `after_reset=false`, 2026-09-19) moved with it unchanged.

4. **ui/073** 16:02 — two verbatim splits: decisions 8/25/42 out of `shell.md` into
   `decisions/design-system.md`; decision 44's two sections out of `topology-boards.md` into
   `decisions/saved-benches.md` (doc **`ccf2eacf`**, base `9d7f2951`; code base `c5857fd`/`c5857fd9`,
   zero commits). Worker also repointed a pending fragment it did not write (owner's
   `changelog.d/ui-brand-token.added.md`, decision 25 → `decisions.md`). First green `check-docs.py`
   (all 11) on `main` since the clocks expired.
**Reviewer:** no findings.
**Hardware debts:** none created.

5. **core/092** 16:38 — `arrivals`/`load`/`load/spans` rows moved from `interfaces/studies.md` into
   new `interfaces/streams.md` (doc **`df7cb35e`**, base `a6cace62`; code base `48dc591`, zero
   commits).
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move, no source change, no native Windows build owed.

6. **api/118** 16:44 — decision 59's parenthetical amended in place (`SignalLink` stopped being called
   a mirror) (doc **`0db25814`**, base `e76d35cd`; code base `517a7e3`, zero commits). Reviewer found,
   below its bar, that decision 72's "seven" retired mirrors vs. six named types is pre-existing
   (authored **`c62cc870`**, 2026-09-12) — filed as `tasks/api/119`.
**Reviewer:** no findings.
**Hardware debts:** none created — one parenthetical.

7. **dev-bench/014** 16:48 — decisions 30/35 moved to new `decisions/link-limits.md` (doc
   **`027d62df`**, base `9807430c`; code base `edc278bb`, zero commits). Unparked at claim
   (**`b63ddeda`**) on its own lapsed clock: `link.md` untouched since **`84243a33`** (2026-09-08).
   Slip: a refused first fold attempt
   still let `git push origin HEAD:main` run (`| tail` ate the exit status) — same pattern as
   `core/046` below; two legs in a row.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

8. **study-designer/067** 16:52 — `.eap` constants split from `interfaces/limits.md` into new
   `interfaces/eap-limits.md`; decision 71 moved to `decisions/payload-meaning.md` (doc **`88e0b2de`**,
   base `aef01be1`; code, zero commits).
**Reviewer:** no findings.
**Hardware debts:** none created — two verbatim moves.

9. **ui/072** 17:08 — decision 14 split into new `decisions/project.md` (doc **`de3efeef`**, base
   **`d47c32e4`**; code base `c5857fd9`, zero commits, fast-forward, no rebase). Slip noted: a
   dispatch-time worktree add resolved a relative path inside the repo instead of beside it; caught
   and moved before any worker started, nothing committed there.
**Reviewer:** no findings.
**Hardware debts:** none created — verbatim move.

10. **core/093** 17:13 — decisions 70/72/73 split into new `decisions/streams-live.md` (doc
    **`b594ac91`** + **`23987bd3`**, base `8b4786d3`; code base `48dc591`, zero commits). Unparked at
    claim (**`9ee5de6b`**): its `In flux: yes` block (72/73 unvalidated on hardware) does not forbid
    the verbatim-move remedy the task itself named; flux otherwise unlapsed (bench still unplugged).
    Supervisor repointed `embarch-ui/decisions/live-study.md:30` (decision 70) at landing. Filed
    `tasks/core/095` from the reviewer's aside (unnumbered decision citation in `src/study.rs`).
**Reviewer:** no findings.
**Hardware debts:** none created. Decisions 72 and 73 are still unvalidated on hardware — a traced
    study with the outpost bridge attached — the split moved that debt, it did not pay it.

11. **study-designer/068** 17:19 — decision 77 split from `decisions/declares.md` into new
    `decisions/builds.md` (doc **`01d209d8`**, base `fc08de8f`; code base `15087ae`, zero commits).
    Supervisor repointed `embarch-ui/decisions/firmware-build.md:7` to the index (`decisions.md`),
    a different repoint convention than `core/093`'s topic-file repoint one unit earlier. Rewrote
    `tasks/study-designer/066`'s now-false premise (seventeen files → twenty) and left it open.
**Reviewer:** no findings.
**Hardware debts:** none created — a move and two pointers.

12. **umbrella/088** 17:23 — `check-15` bullet corrected to stop saying the hash is unbuilt;
    `open.md` squeezed 4,372 → 3,905 B (doc **`ecc2880c`**, base `5bb668d6`; code base `2764e89`,
    zero commits). Worker declined to consume `binary_sha256` in check 15 itself — a real behavior
    change needing its own decision — and filed `tasks/umbrella/089` (below) instead. Reviewer noted
    pre-existing stale text in `open.md`'s own "why `saved.host` was left unfixed" item.
**Reviewer:** no findings.
**Hardware debts:** none created. `open.md` bullets carrying debts unchanged in substance: check
    13 (one `doctor` run on the primary bench), check 5 (a Linux box with Core native), decision 51's
    three-step real-machine confirmation.

13. **study-designer/032** 17:47 — §4 ("What a study carries") moved to new
    `embarch-study-designer/spec/carriage.md`; §§5/6/7 renumbered to §§4/5/6 (code **`b9a2d5d`**,
    base `15087ae`; doc **`9fe1ec5c`**, base `01190ef5`). Unparked at claim (**`1db80acc`**): §4's
    last edit was **`ac9c2116`** (2026-09-18), a full leg quiet as the task's own unpark condition
    required. Filed `tasks/api/120` for the one repointed citation the worker couldn't reach
    (`embarch-api/src/main.rs:538`).
**Reviewer:** no findings.
**Hardware debts:** none created — a move, a renumber and a comment.

14. **core/046** 17:52 — decisions 42/46/60 moved to new `decisions/route-sweep.md`;
    `auth.md` 11,356 → 3,799 B (code **`fdb9b1d`**, base `48dc591`; doc **`b887482f`**, rebased from
    **`2e6173ea`** onto `9d7b3df1`). Unparked at claim (**`11c9ae7d`**): the task's own prediction ("the next new HTTP
    route ... likely to land here") was falsified by four routes landing in `build_router` elsewhere
    since **`f6e23215`** (2026-09-12) — `4251af3`, **`d73a73a`**, **`e50de6d`**, **`f832043`** — none
    touching `auth.md`. Supervisor corrected the worker's Size cell (2.9 KB claimed vs. measured
    3.8 KB). Slip: same refused-fold-still-pushed pattern as `dev-bench/014` — **`b887482f`** reached
    `origin/main` a few minutes before its fold.
**Reviewer:** no findings.
**Hardware debts:** none created. The `api.rs` change is a comment, so no native Windows build
    owed for it.

15. **api/111** 17:56 — decisions 71/73/76 moved to new
    `embarch-api/decisions/validate-kind.md` (code base `517a7e3`, zero commits; doc **`c8dbb6e6`**,
    base **`8f54d73a`**, rebased from `1cd74544`). Unparked at claim (**`e92f430e`**): the task's own
    second unpark condition ("once the file is judged safe to split") is satisfied by its own named
    seam.
**Reviewer:** no findings.
**Hardware debts:** none created — a verbatim move.

16. **umbrella/089** 18:00 — check 15 now hashes the located `embarch-core` binary once
    `core_version` already matches and compares it to `/status`'s `binary_sha256`; a mismatch is
    **Warn**, never Fail; missing hash on either side falls back to the old version-only Pass (code
    **`b55809c`**, fast-forward onto **`2764e89`**; doc **`ab3a56e4`**, rebased from **`57c380dd`**
    onto **`3d01e141`**). Wrote `embarch-umbrella` decision 56; amended decision 34 as "narrowed, not
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
*Days 2026-09-17 to 2026-09-17 rolled to [log-archive/supervisor-log-2026-09-17-to-2026-09-17.md](log-archive/supervisor-log-2026-09-17-to-2026-09-17.md).*
