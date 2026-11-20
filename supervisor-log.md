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

## 2026-11-20 16:06 — core/128 agent-and-person-tokens

**Decided:** nothing suite-wide. A resume of the 14:25 leg's dead worker (see `study-designer/084`'s entry for the recovery). The resumed worker found the as-found code built and clippy-clean but two route-sweep tests red: a test-only `/probe` router put a line starting `.route("` in `api.rs`, which the sweep's source scan counts as a registered route; it moved the probe onto one `Router::new().route(` line, and renamed the features fragment from `core-125-` to `core-128-`. `embarch-core` decision 109: Core writes an agent token (`EMBARCH_TOKEN`, else `token`) and a person token (`EMBARCH_PERSON_TOKEN`, else `person-token` beside it), either authenticates, and `auth_middleware` puts a `Scope` request extension on every request; nothing is refused by scope. Decision 93 gains a one-line pointer: the lease holder is not the scope. I folded its fragment into `embarch-token.md` §1, §2, §3 and §5 (two tokens, clients still resolve the agent's alone, no identity within a scope), and set `tasks/api/162` (core-client resolves both scopes) `open`, its `Unparks when:` naming this unit; `tasks/ui/111` still waits on `api/162`.
**Merged:** `agent/core/128-agent-and-person-tokens` (code `789cbfc`, ff on `origin/main` from `d4c9564`; doc as-found `a4f429c4`, resume `5d4b8ab2`, cherry-picked onto `59b55276`). Re-gated on the merge result: `cargo build`, `cargo test` (395 passed, 2 ignored), `clippy --all-targets -- -D warnings` green; ownership green on both branches; client names clean; `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, and the `icacls` lockdown on the new `person-token` file, unrun (a worktree cannot build natively); the task's closing note says how to check both from the main checkout on Windows. No board needed.
**Budget:** PROCEED at the start, 5-hour 67%, weekly 17%, wave 6.
**Least sure about:** `service.rs`'s install still passes only `EMBARCH_TOKEN`, so an installed Windows service generates its own `person-token` in `ProgramData` on first start; nothing reads that file yet, and whether the person can read it there is the same unchecked directory-ACL inference `embarch-token.md` already flags for decision 23.

---

## 2026-11-20 16:05 — study-designer/084 hil-file-shapes

**Decided:** nothing suite-wide. **A recovery, and the leg's mechanics are what to carry.** The leg that took the lock at 14:25 claimed `study-designer/084`, `core/128` and `api/163`, dispatched all three workers in the background at 14:41 and was cut off; its workers wrote until 14:45-14:51 and died, nothing committed or pushed, no log entry. I committed each tree as found to its branch and pushed (this one doc `5322a69c`), removed the worktrees, reclaimed each for a resume (`bbf6b7be`, `07f42aaf`, `bd893eee`), and resumed all three onto their branches. **EMB-214's next check, answered:** the three resumed workers went out as three foreground `Agent` calls in one message at 15:51:55 and returned together at about 15:57, taking 78 s, 307 s and 291 s; they ran concurrently, and each reported to this leg. **Refill skipped on a depth firing** (0 dispatchable after the re-claims): no source path has a commit since `Spread sweep: nothing filed (2026-11-18 23:20)`, the same reasoning the 2026-11-19 04:10 leg applied, which the rule's text covers only for a spread-only firing. **A `/fleet stop` arrived at 15:58** (marker on disk, pump already deleted, relayed by the listener); I dispatched nothing after it and am landing the three units already reported. This unit also commits the 2026-11-19 day fold, which the 14:25 leg's `embarch-log-folder` applied and never committed, rolls 2026-11-17 into `log-archive/`, and ran `check-client-names.py --suite --history`: clean on all 16 repos. Unit itself: the resumed worker judged the as-found shapes docs complete and correct and kept them; decisions 90 and 91 (`decisions/hil-shapes.md`) record the choices the notes left open. I folded its three pointer fragments into notes 02, 03 and 06 as links to `interfaces/hil-shapes.md`, `hil-run.md` and `hil-pdf.md`; 02's sits under the "Measurements" heading rather than after its first paragraph, which ends by introducing a list. **`fold-commit.py` refuses to stage `notes/`**, so those edits and the three fragments landed as their own commit, `c937c8e0`, ahead of this fold; `check-ownership.py --supervisor` passes `notes/`, so the gap is the fold script's list, not ownership.
**Merged:** `agent/study-designer/084-hil-file-shapes` (doc only: as-found `abb234ef`, resume `59b55276`, cherry-picked onto `a8c1d25f`). `check-docs.py` 12/12 on the merge result, `check-ownership.py --scope study-designer` green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 15:49 refresh.
**Budget:** PROCEED at the start, 5-hour 67%, weekly 17%, wave 6; three workers, one per scope.
**Least sure about:** the reviewer noted 03 makes an observation-prompt timeout `inconclusive` while `hil-shapes.md`'s closed `reason` list has no matching reason; it called that M1.3's decision, not a contradiction, and I left it as a `Finding` comment on EMB-218 (M1.3, waiting in Fleet Ready) rather than reopening a shapes doc nobody has built against yet.

---

## 2026-11-19 — 6 units

*Folded by the 2026-11-20 leg's `embarch-log-folder`: per-unit "Decided" reasoning, test tallies and "Least sure about" narrative dropped (git holds them); SHAs, Reviewer lines, debts and carry-forward items kept.*

**Carry forward:**
- **Spread sweep skip line, verbatim:** `Spread sweep: nothing filed (2026-11-18 23:20)`. No source path had a commit since; the refill gate fired on depth and spread at 04:10 and was skipped.
- **Background dispatch cuts a leg off.** The three legs before 00:02 dispatched workers in the background, ended their turn to wait, and were cut off (the 00:30 leg died mid-`atlas/090`, wrote no entry, left 247 uncommitted lines that were committed as found at `d80aa9f`). Foreground dispatch returned in about 3 minutes each (`087`, `088`, `089`, `090`). Filed **EMB-214** (Backlog, investigation); it names `.claude/leg.md` paragraphs, which are the owner's.
- **Bench `api/059` and `dev-bench/038` stay `open`**: neither `dev-bench` nor `dut` attached at 23:56 or 04:04. Fleet Ready empty. Atlas was the only scope with work; none left after `090`.
- **`suite/056` run by the supervisor** after its announcement window (`1795086320.551719`, 04:05, no `--action`, no reply by 04:35): `embarch.md` 23,314 to 22,735 B (reserve 23,040). Two stale facts corrected ("ten legs run", §6 "one entry per batch"). Possibly out of rule: the depth sweep was skipped by applying the spread-only skip's reasoning.
- Mid-day: 2026-11-18 folded (17 units) and 2026-11-14 rolled into `log-archive/` by the 00:02 leg; `check-client-names.py --suite --history` clean on 15 repos.
- Budget throughout: PROCEED, wave 6, 5-hour 0% to 79%, weekly 18% to 23%.

**Owner-side debts (in the task files, none need a board):** `doc regparse --template maxim` on the real datasheets (layout 3 optical-sensor, and the one that read 0 registers; real tables wrap their headers and descriptions, so a summary-table row regex may report `no_summary_row`); `doc regparse --template ti` on the real datasheet; `mcu rm-outline` and `mcu vote` on the real nRF54L-series datasheet.

---

### 04:37 — suite/056 compact-suite
**Merged:** `suite/056` (doc `670c15cc`, on `origin/main`; no code repo).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 04:10 — atlas/090 maxim-bit-column-register-map (EMB-34, second half; recovery of the dead leg's worker)
**Merged:** `agent/atlas/090-maxim-bit-column-register-map` (code `d80aa9f`, ff on `origin/main` from `124dc60`; doc `2bd99b5d`, the worker's `2bff3d8c` cherry-picked onto `256cf62f`). Dead leg's claim `76a04e89`, reclaimed `0a31d1d5`. Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template maxim` on the real optical-sensor datasheet; only synthetic PDFs have exercised layout 3. Bench `api/059`, `dev-bench/038` stay `open` (neither `dev-bench` nor `dut` attached at 04:04).

### 00:22 — atlas/089 maxim-register-headings-with-a-hex-address (EMB-34, first half)
**Merged:** `agent/atlas/089-maxim-register-headings-with-a-hex-address` (code `124dc60`, ff on `origin/main`; doc `c04d874b`, ff on the leg worktree). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template maxim` on the real datasheet that read 0 registers; the synthetic table has one-line rows, while the real one wraps its `REGISTER NAME` header and its descriptions.

### 00:15 — atlas/088 read-ti-width-prefixed-binary-resets (EMB-33)
**Merged:** `agent/atlas/088-read-ti-width-prefixed-binary-resets` (code `85ee2b9`, ff on `origin/main`; doc `503fc4a6`, the worker's `22f8ea03` cherry-picked onto `14960676`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template ti` on the real datasheet, to see its resets and its 3 conflicts, which this unit does not claim.

### 00:09 — atlas/087 read-a-nordic-style-reference-manual (EMB-32)
**Merged:** `agent/atlas/087-read-a-nordic-style-reference-manual` (code `1948a8c`, ff on `origin/main`; doc `27a2efb5`, the worker's `19c8f474` cherry-picked onto `1439f6ea`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: one `mcu rm-outline` and one `mcu vote` run on the real nRF54L-series datasheet; the `ID` row's real column alignment, multi-letter field IDs and table rows unlike the issue's shape are unverified.

### 00:02 — atlas/086 check-the-pdo-decode-against-the-standards-tables (EMB-159; third-leg re-land)
**Merged:** `agent/atlas/086-check-the-pdo-decode-against-the-standards-tables` (code `69bf11f`, ff on `origin/main`; doc `2098422f`, the worker's `d0196cb2` cherry-picked onto `b74bfd51`). Gates green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059`, `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 23:56 refresh.

---
## 2026-11-18 — 17 units

*Folded 2026-11-19 by the atlas/086 leg's `embarch-log-folder`; the per-unit narrative (what each worker built, hand-checks, gate counts, budget readings, least-sure-about lines) went to git. SHAs, reviewer lines and owner-side debts are kept.*

**Carry forward (read first):**
- **atlas/086 is in flight and its leg was cut off (23:28).** The `.fleet/leg` lock was the cut-off leg's and `leg-end` was not run; wait it out, then recover `atlas/086` by presence: a pushed `agent/atlas/086-check-the-pdo-decode-against-the-standards-tables` in both `embarch-atlas` and `embarch-doc` means the worker finished, so gate and land it; no branch and a dirty tree means commit the tree to its branch and resume or block per `ops.md` §3. Claimed `23d755d1`, dispatched 23:23. Do not tick `leg-reported` for a worker whose `leg-dispatch` your leg did not tick. This is the third cut-off of the day (15:51-era, 16:37, 23:28): every leg that dispatched before its own hand-back was ended with workers in flight, and each time the workers finished and pushed. If it recurs, land at most two units per leg.
- **Pattern for the 16:37 and 15:51 cut-offs (both resolved):** the 15:51 leg split five issues, claimed `atlas/084` and `desk/039`, dispatched, and wrote no entry; the 16:26 leg re-landed both. The 16:37 leg then re-dispatched `atlas/085` and `desk/040`, cut off the same way; the 23:17 leg re-landed those. Recovery by presence worked every time.
- **Fleet Ready is empty;** `atlas/087` to `090` (EMB-32, EMB-33, EMB-34 split into 087, 088, 089 and 090, all `filed`, announced `1795044886.216409`) sit behind `086`. Atlas is the only scope with dispatchable work, so the wave is one wide. Bench `api/059` and `dev-bench/038` stay `open` (neither `dev-bench` nor `dut` attached 23:19). `tasks/doc/098` (owner-only) still reads `done`, unretired.
- **Spread-sweep skip line, verbatim:** `Spread sweep: nothing filed (2026-11-18 23:20)` (165 open questions across 20 docs unchanged all day).
- **Owner decisions pending / suite-wide calls made for him:**
  - 05:05 dream posted at `1795003522.538789` (205 commits, 77 h): (1) EMB-112 by its synthetic route, (2) EMB-208 keep-or-revert on atlas `fetch-text`, (3) an attended leg for the two bench tasks. The 11:20 leg posted a quiet repeat (`1795025835.324839`) against `--dream-check`'s ASK because the one commit since was the dream's own fold (`f16ab330`); filed **EMB-210** (Backlog, `Scope: fleet`) for the race. EMB-209 (day fold drops the spread-sweep line) is in the owner's lane.
  - **EMB-208 resolved by the owner:** keep `fetch-text`; "never fetches" now means "never fetches a document it distils" (`atlas/084`).
  - EMB-112 and EMB-85 sent back to Backlog (needs a real hierarchical export; Promptu step 3 forks wait on the owner). Burndown ended 05:07 (queue empty); normal caps since.
  - **EMB-207** (Backlog): desk draft-revision durable-decision question; partly absorbed by `desk/039` and `desk/040` amending decisions 88 and 89 (no new number). `desk/040` reverses one line of `desk/039` (a `github_replies` draft now has a version history).
  - `atlas/077` landed `fetch-text` against the repo's `DESIGN.md` (network verb in a "never fetches" tool) with a one-line unreconciled note; reconciled by `atlas/084`.
  - No `features.d/` row for atlas units since `atlas/076` (`build_features.py` has no `atlas` section); the owner has not settled it.
- **Traps:** `drive_desk.py` needs `EMBARCH_DESK_BIN` pointed at a fresh build (the main-checkout debug binary predates EMB-173 and knows no `github_replies`). A hook asked a worker to file a throwaway-job issue in the `THR` team after inline Python; neither worker nor supervisor did. A cached clippy replay (0.33 s) in `desk/040` is not a fresh compile. The 2026-11-18 history scan and day fold were owed to the first unit after midnight.
- **Owed, owner-side** (no board; real-artifact runs): one real Send of a reply draft from the Desk tab to a test PR; reload of the desk MCP server and one real revise of an owner-edited draft (Desk tab shows neither `agent_body` nor the diff, no UI issue filed); `q stacks` on the real build to confirm two 0x400 B per-instance stacks appear; `atlas cad` and `board-diff` on a real Altium project (nine format assumptions in `DESIGN.md` "Native EDA project" unchecked); `atlas build` on a real Zephyr 4.x image then `q shell-commands` vs the console `help` (about 5 min; unchecked: `device_area` names, `*_area` section names, `nm -l` Thumb addresses); `rc_timing` against a real board's atlas; `decode` on a real datasheet (no translate step emits `frame` or `transfer` records yet); `fetch-text` on a real blocked page; `pdf pages` on a real scanned PDF.

### Units

**atlas/086 (cut off 23:28):** claimed `23d755d1`, dispatched 23:23, worker in flight at hand-back. No `**Reviewer:**` line (leg-level).
**Merged:** nothing yet.
**Blocked:** nothing.
**Hardware debts:** none new; bench `api/059`, `dev-bench/038` stay `open`.

**desk/040 revise-one-reply-of-a-github-replies-draft (23:24)** — EMB-212: `comment_id` on `POST /drafts/{id}/revise` and `desk_revise_draft` replaces one reply whole; owner-edited reply is a 409.
**Merged:** `agent/desk/040-revise-one-reply-of-a-github-replies-draft` (code `bc5749a`; doc `0c649fa5`, the worker's `8144009e` cherry-picked onto `23d755d1`). `cargo test` 296 passed, clippy green, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**atlas/085 list-per-instance-driver-thread-stacks (23:22, re-land)** — EMB-27: `STACK_NAME` takes an optional `_<digits>` instance suffix.
**Merged:** `agent/atlas/085-list-per-instance-driver-thread-stacks` (code `ba6366f`; doc `e319a16a`, the worker's `226aeca7` and `e319a16a`). `pytest` 956 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. A rerun of `q stacks` on the owner's real build would confirm the two 0x400 B stacks now appear; the fixture only models them.

**Leg cut off 16:37 (atlas/085, desk/040):** split Fleet Ready in `2d9e7169`, claimed `a4cb8ce3` (`atlas/085`) and `2bb300d0` (`desk/040`), announced `1795044886.216409`, dispatched 16:35. No `**Reviewer:**` line (leg-level). Both re-landed by the 23:17 leg, above.
**Hardware debts:** none new; bench `api/059`, `dev-bench/038` untouched.

**desk/039 keep-a-pending-drafts-versions (16:31, re-land)** — decision 88 amended: version history (cap 50, version 1 kept) for agent revisions and owner edits; `github_replies` not versioned (reversed by `desk/040`). Set `desk/040` `open`.
**Merged:** `agent/desk/039-keep-a-pending-drafts-versions` (code `0536138`; doc `5f556105`, the worker's `9e368315` cherry-picked onto `3fd7aa81`). `cargo test` 295 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**atlas/084 narrow-never-fetches-to-the-document-pipeline (16:30, re-land)** — EMB-208 answered. The 15:51-era cut-off leg split in `4a5bd1b4` (EMB-208, EMB-27, EMB-211, EMB-212) and `a545f603` (EMB-159 into `atlas/086`), claimed `2eebd58c` (`atlas/084`) and `b5e73bf8` (`desk/039`), then wrote no entry.
**Merged:** `agent/atlas/084-narrow-never-fetches-to-the-document-pipeline` (code `f50a8c8`; doc `3fd7aa81`, the worker's `3baf9f9f` cherry-picked onto `b5e73bf8`). `pytest` 955 passed, 3 skipped. Doc-only; I corrected "below" to "above" in `design.md`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**Leg 11:20, no units (queue empty, quiet repeat posted)** — `embarch-doc` `main` stayed at `f16ab330`; posted `1795025835.324839`; EMB-210 filed. Leg-level, no `**Reviewer:**` line.
**Merged:** nothing.
**Blocked:** nothing.
**Hardware debts:** none new. Bench `api/059` and `dev-bench/038` stay `open` (neither role attached 11:19).

**atlas/083 diff-cad-netlist-against-pdf-atlas (05:05)** — EMB-88 part two: `board-diff --cad`. Queue emptied; burndown cleared; dream posted `1795003522.538789`.
**Merged:** `agent/atlas/083-diff-cad-netlist-against-pdf-atlas` (code `3718836`; doc `b596e0a0`). `pytest` 955 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one `board-diff` run on a real Altium project against the atlas built from its PDF, together with `atlas/082`'s `cad` run; both have run only on synthetic fixtures.

**atlas/082 read-altium-schdoc-project (04:57, re-land)** — EMB-88 part one: `embarch-atlas cad` via `olefile` (new optional extra `cad`). Cut-off 04:17 leg split in `67d8d482`, claimed `66d94dfb`, dispatched `ee35b02b`; its sweep time `2026-11-18 04:18` is a lower bound.
**Merged:** `agent/atlas/082-read-altium-schdoc-project` (code `b7edc78`; doc `dbe031c6`). `pytest` 948 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one `embarch-atlas cad <real project> --variant <name>` run on a real Altium project, compared with its PDF-built atlas; `DESIGN.md` "Native EDA project" lists nine format assumptions, none checked against a real `.SchDoc`.

**atlas/081 strain-sensor-signal-budget (04:16)** — EMB-139: `derive strain-budget`, CLI only. Leg close 4 of 4, all landed.
**Merged:** `agent/atlas/081-strain-sensor-signal-budget` (code `402fda4`; doc `1e412f8f`, the worker's `2dd2b710` cherry-picked onto `036bd321`). `pytest` 938 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**atlas/080 inventory-shell-commands-in-a-pinned-build (04:09)** — EMB-157: `shell.json`, MCP `shell_commands`, `q shell-commands` (lookups 22 to 23). Worker sent back once before landing (wrong Zephyr 4.x shell table layout, verified against upstream 4.3.0 `shell.h`).
**Merged:** `agent/atlas/080-inventory-shell-commands-in-a-pinned-build` (code `4676e84`, two commits, first push `ec7b3a6`; doc `92f3be5a`, the worker's `989fe22e` and `a8515fce` cherry-picked onto `a52f025a`). `pytest` 927 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one `atlas build` on a real Zephyr 4.x image, then `q shell-commands` against what the console's `help` prints, about 5 minutes; the synthetic ELF only proves the parser matches the layout encoded in it. Still unchecked against a real image: `struct device` names via `device_area`, the `*_area` output section names, and `nm -l` addresses for Thumb functions. Open risk: the 24-byte `shell_static_entry` padding is inferred from an x86-64 ELF only, so a 64-bit `native_sim` on an ARM64 host would be walked with the wrong stride.

**atlas/079 worst-case-rc-threshold-crossing-time (03:57)** — EMB-195: `q rc_timing` and MCP `rc_timing` (lookups 21 to 22). The EIA temperature-class table is the worker's own and unverified against datasheets (labelled assumed).
**Merged:** `agent/atlas/079-worst-case-rc-threshold-crossing-time` (code `e063b48`; doc `a0f1eb8a`, the worker's `6c5955b8` cherry-picked onto `e92b7fc8`). `pytest` 917 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one run against a real board's atlas; the regulator match reads `sym` `VOUT`/`VO` or a `param` naming output voltage, so a real distillation naming it otherwise (an adjustable part, `VOUT(nom)`) gives a named gap rather than an answer.

**atlas/078 decode-a-command-then-read-sensor-reply (03:49)** — EMB-177: `q decode` and MCP `decode` (lookups 20 to 21), new `frame` and `transfer` record kinds. Fleet Ready split in `10b3f65a` (EMB-177, EMB-195, EMB-157, EMB-139), announced 03:45 `1794998453.538449`. Spread sweep skipped on source commits `1579353b`, `2ee1b7e5`, `955dcf18`, `4a2b259a`, `bc8b9817` (atlas `design.md` paragraphs only).
**Merged:** `agent/atlas/078-decode-a-command-then-read-sensor-reply` (code `2e80f57`; doc `f1aab5d6`). `pytest` 908 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: no translate step emits `frame` or `transfer` records yet, so the verb answers only for hand- or LLM-written records until `atlas-translate-docs` learns them; and one run on a real part's datasheet, since the record shape was designed with no real datasheet behind it.

**atlas/077 turn-a-fetched-page-into-text (03:35)** — EMB-135: `fetch-text` (exit 3 on a blocked page). Landed against the repo's `DESIGN.md` "never fetches"; kept rather than reverted, one-sentence unreconciled note added to `embarch-atlas/design.md`, EMB-208 filed (undo routes: narrow line 15 and the "Never" bullet, or revert `ef79b2f` and `4a2b259a`). Reconciled later by `atlas/084`.
**Merged:** `agent/atlas/077-turn-a-fetched-page-into-text` (code `ef79b2f`; doc `4a2b259a`, the worker's `c726de41` cherry-picked onto `1b7a8cf7`, claim `46b2b300`). `pytest` 894 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-208
**Hardware debts:** none. Owed, owner-side: the EMB-208 call; and one run against a real blocked page, since the interstitial phrases are a short fixed list.

**ui/110 desk-tab-renders-github-replies-drafts (03:32)** — EMB-205: Desk tab card for `github_replies` drafts; `tasks/desk/038`'s `Unparks when:` loses the EMB-205 clause.
**Merged:** `agent/ui/110-desk-tab-renders-github-replies-drafts` (code `d824791`; doc `26f69da7`, the worker's `0617772b` cherry-picked onto `b6ec918a`). `cargo test` 317 passed, 4 ignored. Worker's headless-Firefox check not re-run by the supervisor.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one real Send of a reply draft from the Desk tab to a test PR. Trap for whoever re-runs `drive_desk.py`: the desk debug binary built in the main checkout, `embarch-desk/target/debug/embarch-desk`, predates EMB-173 and knows no `github_replies`; point `EMBARCH_DESK_BIN` at a fresh build.

**desk/037 revise-a-pending-draft-keeping-the-owners-edits (03:29)** — EMB-165: `agent_body` beside `body`, `desk_revise_draft`, `desk_get_draft` diff. `interfaces.md` MCP inventory moved to `interfaces/mcp-tools.md`; `tasks/desk/036` closed `done`; `spec.md` in reserve (9,186 of 10,240 B), `tasks/desk/038-compact-desk.md` `blocked`, due 2026-12-01. EMB-207 filed. One unreproduced 1-of-292 `cargo test` failure in the worker's runs (possible flaky test in `embarch-desk`).
**Merged:** `agent/desk/037-revise-a-pending-draft-keeping-the-owners-edits` (code `f0f6b98`; doc `207ca98b`, the worker's `3471d439` cherry-picked onto `46b2b300`). `cargo test` 292 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: a reload of the desk's MCP server to pick up the two tools, and one real revise of a draft he has edited on the Desk tab. The Desk tab shows neither `agent_body` nor the diff; no UI issue is filed for that yet.

**atlas/076 render-pdf-pages-for-an-image-read (03:27)** — EMB-138: `pdf pages`. Fleet Ready split in `4ecb2c7c` (EMB-205, EMB-165, EMB-138, EMB-135), announced 03:18 `1794997111.757099`. This unit carried the 2026-11-17 day fold (38 units), the roll of 2026-11-13 into `log-archive/`, and the once-per-day `check-client-names.py --suite --history` (every repo clean). The 40-character text-layer threshold could misread a thin OCR layer as text.
**Merged:** `agent/atlas/076-render-pdf-pages-for-an-image-read` (code `696ee62`; doc `955dcf18`). `pytest` 885 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, owner-side: one run on a real scanned PDF read back with the image `Read` tool; the tests prove only that PNGs of the right size are produced from generated PDFs, so the first Done-when box ("reads legibly at the default settings") is unproven in practice.

---
*Days 2026-11-17 to 2026-11-17 rolled to [log-archive/supervisor-log-2026-11-17-to-2026-11-17.md](log-archive/supervisor-log-2026-11-17-to-2026-11-17.md).*
