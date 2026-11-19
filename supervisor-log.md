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

## 2026-11-19 00:15 — atlas/088 read-ti-width-prefixed-binary-resets

**Decided:** nothing numbered (`embarch-atlas` keeps none). Dispatched in the foreground like `atlas/087`, for the reason that entry gives; back in 3.2 minutes. EMB-33, the cause: the TI layout printed three forms the template did not know, so every reset was `None` and `_check_document` had nothing to compare, hence no `conflict`. The field-table cell `1b0` / `2b10` failed `RESET_TOK`'s `(?![\w])` lookahead after the `b`; the diagram token `R/W-1b0` (and `R-X`) matched nothing in `FIGTOK`; the heading `[Reset = 0x11]` fell through `_reset_spec` to a text note because `0x` hex was not a value. `HEAD`, `TABLE_HDR` and the capital `R` were already fine. Fix in `regparse.py`: `RESET_TOK`, `FIGTOK` and `_bits_value` read `<width>b<bits>`; `_heading_reset` and `_reset_spec` read `0x..`; `[Reset = X]` and `R-X` read as unknown, no reset and no conflict. A width-prefixed cell whose digit count disagrees with its width reads as unknown and writes a `conflict` `<REG>.<FIELD>.reset_width` from the field table; in a diagram it conflicts only where the table gives that field a value. Synthetic part `SYN880` (consistent, heading-vs-fields conflict, `[Reset = X]`, bad width). `DESIGN.md`'s `doc regparse` row names the cause and the form.
**Merged:** `agent/atlas/088-read-ti-width-prefixed-binary-resets` (code `85ee2b9`, ff on `origin/main`; doc `503fc4a6`, the worker's `22f8ea03` cherry-picked onto `14960676`). `pytest` 964 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: `doc regparse --template ti` on the real datasheet, to see its resets and its 3 conflicts, which this unit does not claim.
**Budget:** PROCEED, 5-hour 61%, weekly 20%, wave 6 at the dispatch; one worker, atlas the only scope with work.
**Least sure about:** the fixture was built from the issue's description of one register, so whether the real pages put the access-reset tokens on one line under the bit numbers, as `FIGTOK` assumes, is untested.

---

## 2026-11-19 00:09 — atlas/087 read-a-nordic-style-reference-manual

**Decided:** nothing numbered (`embarch-atlas` keeps none). **A leg-mechanics choice, and the next leg should know it:** I dispatched this worker in the foreground (the leg blocks on it) rather than in the background. The three legs before this one each dispatched in the background, ended their turn to wait, and were cut off, so each landed only its predecessor's re-lands. With atlas the only scope holding dispatchable work the wave is one wide, so blocking on the one worker costs no concurrency; it came back in 3.4 minutes and reported to this leg. EMB-32: `mcu rm-outline` drops a lone unnumbered level-1 root that has at least two level-2 children (`rm.unroot_toc`), so its level-2 entries become chapters and `outline.json` records the root as `root`; a numbered single root (an ST one-chapter outline) and two or more level-1 entries are left alone. A `...Registers` container whose numbered children carry bare upper-case names (`BARE_REG_RE`) flags them as register sections, and `vote.parse_nordic_fields` reads the `Bit number`, `ID` and `Reset` rows and the field table into the same register record the ST layout yields, uncovered bits as `Reserved`. `DESIGN.md` gains "Reference-manual layouts read"; `rm-procedure.md` and `embarch-doc/embarch-atlas/design.md` name no layouts, so both are unchanged. Fixtures synthetic, invented names.
**Merged:** `agent/atlas/087-read-a-nordic-style-reference-manual` (code `1948a8c`, ff on `origin/main`; doc `27a2efb5`, the worker's `19c8f474` cherry-picked onto `1439f6ea`). `pytest` 962 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none needing a board. Owner-side, in the task file: one `mcu rm-outline` and one `mcu vote` run on the real nRF54L-series datasheet; the `ID` row's real column alignment, multi-letter field IDs and table rows unlike the issue's shape are unverified.
**Budget:** PROCEED, 5-hour 50%, weekly 19%, wave 6 at the dispatch; one worker, since atlas is the only scope with work.
**Least sure about:** `parse_nordic_fields` places each field by the nearest bit-number column of the `ID` row, which the synthetic pages align exactly; a real text layer that shifts a letter by one column would mis-range a field and nothing here would notice.

---

## 2026-11-19 00:02 — atlas/086 check-the-pdo-decode-against-the-standards-tables

**Decided:** nothing numbered (`embarch-atlas` keeps none). **A re-land, the third leg running:** the 23:17 leg dispatched this at 23:23 and was cut off (its leg entry, now in 2026-11-18's fold). I was spawned at 23:28 into its fresh lock, waited it out with `leg-start --wait` until it went stale (23:55), found both worktrees clean and the branch pushed in both repos, and gated and landed it. No `leg-reported` tick, since this leg never ticked its `leg-dispatch`. EMB-159: `_pdo` in `src/embarch_atlas/fwcheck.py` checked field by field against USB PD R3.2 V1.2 from the layout the owner gave; positions and units all agreed. Three fixes, the dispatch notes' three guesses: a fixed PDO above 5 V decodes only `mv`, `ma` and source `peak`, its vSafe5V flag fields `None`; a sink EPR AVS APDO's B7..0 lands in new `max_w`, `pdp_w` `None` for a sink; SPR AVS `ma_15v`/`ma_20v` renamed `ma_9_15v`/`ma_15_20v`, `__str__` says "for 9-15 V". Only the unit test and `DESIGN.md` used the old names. Tests pin one known word per PDO and APDO type, source and sink. This unit also folded 2026-11-18 (17 units, by `embarch-log-folder`) and rolled 2026-11-14 into `log-archive/`.
**Merged:** `agent/atlas/086-check-the-pdo-decode-against-the-standards-tables` (code `69bf11f`, ff on `origin/main`; doc `2098422f`, the worker's `d0196cb2` cherry-picked onto `b74bfd51`). `pytest` 957 passed, 3 skipped (west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12. `check-client-names.py --suite --history` clean on all 15 repos.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059`, `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 23:56 refresh.
**Budget:** PROCEED at this leg's start, 5-hour 42%, weekly 18%, wave 6 (normal mode, pump latched 23:17, no stop marker, 0 actionable in the channel at 23:56). Fleet Ready empty; `finish` moved nothing. Refill gate fired spread-only; no source commit since the 23:20 spread sweep, so skipped. Atlas is still the only scope with dispatchable work, so one worker at a time.
**Least sure about:** the vSafe5V test keys on the voltage (`mv == 5000`) rather than the PDO's position in the list; that holds only while a 5 V fixed PDO appears nowhere but first, which the decode cannot see from one word.

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
## 2026-11-17 — 38 units

*Folded 2026-11-18 by an `embarch-log-folder` agent for the supervisor leg: per-unit narrative reasoning, gate-run detail, Budget lines and leg-close boilerplate dropped; git holds them. Kept: every SHA, every Reviewer line, every Hardware debts line, and what the next leg cannot recover.*

**Open at end of day (carry forward):**
- **Fold owed:** the first leg to run a unit on 2026-11-18 owes the 2026-11-17 fold's successor day (this one is done) and the client-name history scan.
- **Nothing dispatchable as a task file at 23:59.** Fleet Ready held 11 issues (8 `atlas`, 1 `desk`, 1 `chat`, plus EMB-205 `ui` once a leg reads it). EMB-85 (`chat`) needs Promptu's weekly pass built first: two repos in sequence, not one task. Bench `api/059` and `dev-bench/038` wait for an attended leg. `tasks/doc/098` (owner-only) still reads `done` and is unretired.
- **Budget:** burndown PROCEED until 2026-11-18 06:00. Last leg left the 5-hour window at 95% (cap 97%), weekly 69%; the window resets about 03:10. Two units took it from 88% to 95%, which is why the last leg stopped at two.
- **Dispatch shape:** background workers were orphaned twice today (the 18:29 and 19:17 legs; their notifications went to the listener). The 22:36, 23:03 and 23:23 legs dispatched all workers as foreground in one call, and all reports came back. Keep that shape.
- **Decisions made on the owner's behalf:** (1) EMB-190 (the owner's, `Scope: suite`) split into four single-repo tasks (`umbrella/098`, `core/127`, `api/160`, `topology/069`) rather than a `suite` pass, commit `dda025dd`, announced 22:36 (`1794980207.273419`); nothing runs until the owner pushes a tag, so no 30-minute window was owed. (2) `api/157` and `api/158` were kept despite confirmed reviewer findings (EMB-202, EMB-203), forward fix over revert, both fixed by `api/158` and `api/159`; a literal `gate.md` revert-by-SHA reading would revert `9e4a99f`+`95ba8548` and `3479afa`+`206a5584`. (3) `chat/028` was reverted (`3288cf6`) on a confirmed reviewer contradiction (EMB-200) and re-landed fixed (`7a9aaf1`).
- **Filed this day, owner's to read:** EMB-206 (Backlog, decision: first draft kind that writes outside Linear; `direct_writes` now covering GitHub posts; partial send; three options), EMB-205 (Fleet Ready, `ui`: Desk tab does not render `github_replies` drafts), EMB-199 (Backlog decision: desk refusal when Linear is unreachable), EMB-200 to EMB-204 as per the units below.
- **Size debts filed (all `blocked` on `In flux: yes` unless noted):** `tasks/promptu/008` (`decisions/patterns.md`, due 2026-11-24), `tasks/dev-bench/049` (`spec.md` 9,275/10,240 B, due 2026-12-01), `tasks/desk/032` (paid by `desk/033`'s check; `interfaces.md` 14,128/15,360 B, due 2026-12-01), `tasks/desk/036` (`interfaces.md` 1,227 B left, due 2026-12-01, unparks when EMB-205 lands). `desk/030`, `api/161`, `topology/070`, `chat/027`, `chat/031` paid earlier ones.
- **Owed by the owner, workflow side:** `actionlint` on all five signing workflows (`release.yml` x4, `assemble-suite.yml`); new signed component tags in `suite.toml` before the first suite tag (its verify step fails by design otherwise); the first signed tag, which is the only test the workflows have; the `cosign-installer` major is `@v4` in `core/127` and `@v3` in the other three, one may not accept `cosign-release: v3.0.4`; the `release` environment must be tag-only (the `api/160` job has no tag `if:` guard); a re-run of the `aarch64-apple-darwin` leg of `build-check.yml` run 44217599100 (cancelled, no log; not blocked on).
- **Owed by the owner, deploy side:** desk rebuild and redeploy plus MCP reload (`desk/029`, `031`, `033`, `034`, `035`; `plugin.json` version bump and push for `desk/029`'s SKILL.md); `embarch-api` rebuild and redeploy (`api/157`..`159`); extension rebuild and reinstall (`chat/028`..`032`); Promptu rebuild and reinstall plus plugin reinstall (`promptu/006`, `007`, `009`, `010`; the installed `promptu` lacks `original`, so `chat/029`'s action fails here until then); `install.py` re-install of skills for `atlas/067` and `atlas/068`; Core native Windows build debt per `embarch-dev-workflow.md` §4a.
- **Owed by the owner, first real runs (only synthetic fixtures have exercised them):** `q parts`, `net-find`, `schematic_text`, a first module-schematic atlas (`atlas/070`, `071`), an atlas with a datasheet library set, `scripts/replay.py` (atlas/066, carried), ten real `/promptu` prompts then `promptu stats` to pick the rewrite model and wait, `wire-probe.mjs --send ...` against a real login, one real `github_pr_threads` and one real reply Send to a test PR, one real restack through a live session.
- **Loose ends for the next unit touching the file:** `promptu` decision 5 (`decisions/memory.md`) still says the hook runs on "Write, Edit and MultiEdit" (incomplete, not contradicted); a `src/main.rs` comment cites §9 where the heading is §12; `embarch-atlas` DESIGN.md's record-schema row (about line 337) still reads "check L: the item and the level are in it"; a recovered pad name has no mark in the graph UI, `nets.md` and `parts.md`; `query.py:229` banner says "nineteen"; `desk` `interfaces.md` says "two or more" threads, code accepts one; `dev-bench` `spec.md` calls `--check` "the gate's step"; no test lists `desk/034`'s new tools in the MCP router.
- **Doc-half merge note:** `umbrella/100`, `chat/031` and the next two folds' doc merges reached `origin/main` with `chat/031`'s fold push (23:32), a few minutes before their own folds. Mid-day at 14:35 the owner pushed `b671c249` and `fb0ac2eb` (doc/098, desk decision 87) mid-fold and the leg rebased.
- **Split and claim commits (revert handles for the queue, and Slack announcement `ts` values):** 18:06 leg split EMB-197 and EMB-89 (`fb235f51`), claimed `chat/029`, `atlas/070`, `api/157`, `dev-bench/048` (`4c3034ed`, `4a1b08f1`, `d902e9d8`, `1afcf9a1`). The leg that took the lock at 18:29 split EMB-203, EMB-188, EMB-156, EMB-187, EMB-192 into `api/158`, `atlas/071`, `atlas/072`, `promptu/010`, `umbrella/097` (`bc796f1a`), claimed four (`67d0fd27`, `49f75121`, `b6f52955`, `82d74a80`). The 19:17 leg split EMB-203, EMB-176, EMB-168 into `api/159`, `desk/033`, `chat/030` (`87a3112e`), claimed those and `atlas/072` (`9e97eb10`, `aa05525c`, `28efac10`, `a93b940a`). Leg beginning `56d15c36` (fleet `de21520`) split `59649796` (`atlas/068` etc.). Mid-day recovery: branches carried `1898a43` and `6301f43` where `main` carries `7a9aaf1` and `39b34b5`. 22:36 leg: `dda025dd`, announced `1794980207.273419`. 22:59: EMB-96, EMB-163 split (`254d777f`), announced `1794981627.569739`. 23:20: EMB-194, EMB-186, EMB-142 split (`c883004f`), announced `1794982869.801729`. 23:42: EMB-180, EMB-173 split (`cded264e`), announced `1794984200.077469`. `fleet.toml` `fleet_writable` has held `status.d/` since `2b4ad6b` (2026-11-17), so `check-ownership.py --supervisor` passes a worker's `status.d/` request.

### Units (newest first)

**desk/035 (23:59), post approved replies to GitHub review threads.** EMB-173: MCP tool `github_draft_review_replies`, draft kind `github_replies`, Send checks every comment id against the PR first; stub GitHub server only.
**Merged:** `agent/desk/035-post-approved-replies-to-github-review-threads` (code `0ef9c20`, ff on `origin/main`; doc `1b49754f`, the worker's `c3bd07c7` cherry-picked onto `2ee1b7e5`). `cargo test` 282 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one real Send of a reply draft to a test PR, and a desk MCP reload; until EMB-205 lands the Desk tab shows the draft as a blank Linear comment.
**Least sure about:** whether keeping `direct_writes` over GitHub posts is what the owner wants (EMB-206).

**atlas/075 (23:57), q parts returns tolerance and rating by reference.** EMB-180.
**Merged:** `agent/atlas/075-q-parts-returns-tolerance-and-rating-by-reference` (code `fabd08e`, ff on `origin/main`; doc `2ee1b7e5`, the worker's `0c63ba45` cherry-picked onto `93022cb6`). `pytest` 871 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one `q parts` against a real atlas's BOM; only synthetic records have exercised the description parser.
**Least sure about:** the description parser's coverage; a BOM written another way reads `unknown`.

**desk/034 (23:39), restack a stacked branch onto its moved base.** EMB-142: four MCP tools in `src/restack.rs`, no CLI, no route.
**Merged:** `agent/desk/034-restack-a-stacked-branch-onto-its-moved-base` (code `d052160`, ff on `origin/main`; doc `6c6a502c`, the worker's `1694243a` cherry-picked onto `add1d065`). `cargo test` 278 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one real restack through a live session, and a desk MCP reload; only throwaway temp repos have exercised them.
**Least sure about:** hunk detection splits wrongly on a file holding its own `=======` line.

**atlas/074 (23:38), atlas-use shows q config takes several symbols.** EMB-186, skill text only.
**Merged:** `agent/atlas/074-atlas-use-shows-q-config-takes-several-symbols` (code `8a93e35`, ff on `origin/main`; doc `add1d065`, the worker's `d627b75c` cherry-picked onto `39b3dc1c`). `pytest` 867 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**umbrella/100 (23:34), README says LLM coding agent.** EMB-194 split as one `umbrella` task; the wider "LLM, not AI" sweep is filed separately.
**Merged:** `agent/umbrella/100-readme-says-llm-coding-agent` (code `ed5d14b`, ff on `origin/main`; doc `39b3dc1c`, the worker's `30429c13` cherry-picked onto `6eb6e22a`). `cargo test` 273 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**chat/031 (23:31), compact-chat.** Doc-only.
**Merged:** `agent/chat/031-compact-chat` (code: none; doc `6eb6e22a`, ff on `91e8a0ce`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**chat/032 (23:14), a wire probe asks the live Claude one question.** EMB-163.
**Merged:** `agent/chat/032-a-wire-probe-asks-the-live-claude-one-question` (code `bea6282`, ff on `origin/main`; doc `ae78775e`, the worker's `963e9097` cherry-picked onto `1579353b`). `npm test` 312 passed, 78 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the live path never run: `node build.mjs --tests`, then `node tools/wire-probe.mjs --send '{"type":"user","message":{"role":"user","content":"hi"}}@500'` against a real login.

**atlas/073 (23:14), net-find lists nets by name pattern.** EMB-96.
**Merged:** `agent/atlas/073-net-find-lists-nets-by-name-pattern` (code `efc2c7f`, ff on `origin/main`; doc `1579353b`, the worker's `6b747081` cherry-picked onto `f9c948d7`). `pytest` 867 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one `net-find` against a real atlas's boards.

**api/161 (23:13), compact-api.** `spec/implementation.md` §4 moved verbatim to `spec/deployment.md`; paid `api/160`'s size debt.
**Merged:** `agent/api/161-compact-api` (code: none; doc `f9c948d7`, the worker's `297c759a` cherry-picked onto `1d5246d4`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**topology/070 (23:13), compact-topology.** Paid `topology/069`'s size debt.
**Merged:** `agent/topology/070-compact-topology` (code: none; doc `1d5246d4`, ff on `e6a62177`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**umbrella/098 (22:52), suite release verifies components and signs a hashed manifest.** EMB-190, umbrella's part. Folded step 1 out of `embarch-release-signing-proposal.md`. Manifests published per target as `embarch-manifest-<target>.json` (worker's call, kept; a user renames before `embarch verify-release`).
**Merged:** `agent/umbrella/098-suite-release-verifies-components-and-signs-a-hashed-manifest` (code `85e6e65`, ff on `41cbf56d`; doc `6f0d05cc`, the worker's `a8297793` cherry-picked onto `44a207b8`). `cargo test` 273 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint` on `assemble-suite.yml` and `release.yml`; new signed component tags in `suite.toml` before the first suite tag; check `suite.toml`'s tags are the remotes' newest.
**Least sure about:** the untested Python heredoc, `gh api repos/<repo>/commits/<tag>` and `attest-build-provenance@v2` `subject-path`.

**api/160 (22:51), release workflow signs every archive.** EMB-190.
**Merged:** `agent/api/160-release-workflow-signs-every-archive` (code `0d93709`, ff on `0f6fb6c7`; doc `40a05f4c` and `44a207b8`, the worker's `b8bd7459` and `49a6e6cc` cherry-picked onto `737e204a`). `cargo test` 413 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint`; the first signed tag (also shows whether `merge-multiple` lays archives where `archives/*` looks).
**Least sure about:** no tag `if:` guard, so a `workflow_dispatch` run reaches signing with a branch ref; the `release` environment is tag-only, unchecked.

**core/127 (22:50), release workflow signs every archive.** EMB-190.
**Merged:** `agent/core/127-release-workflow-signs-every-archive` (code `d4c9564`, ff on `c0d2a7eb`; doc `737e204a`, the worker's `9e0917c1` cherry-picked onto `371ee24b`). `cargo test` 391 and 2 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the native Windows build (no Rust changed); `actionlint`; the first signed tag.
**Least sure about:** `cosign-installer@v4` here against `@v3` elsewhere.

**topology/069 (22:49), release workflow signs every archive.** EMB-190; the split and foreground dispatch are in the carry-forward above.
**Merged:** `agent/topology/069-release-workflow-signs-every-archive` (code `ee45b6c`, ff on `b905523e`; doc `371ee24b`, ff on `7362aa0e`). `cargo test` 15 passed under default, `--no-default-features` with `software,wire`, and `hardware`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint` (not installed here); the first signed tag.

**chat/030 (22:24), a login pick says which Claude Code surfaces need a reload.** EMB-168; decision 106's body amended, not replaced. Offers Reload Window, never reloads unasked.
**Merged:** `agent/chat/030-a-login-pick-says-which-claude-code-surfaces-need-a-reload` (code `581048d`, ff on `f79c167`; doc `dff4624b`, the worker's `2f9eb369` cherry-picked onto `4cb94685`). `npm test` 308 passed, 78 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** extension rebuild and reinstall, then one real pick in a window on the other login; the reload path is not covered by the test mock.
**Least sure about:** the fix rests on Claude Code 2.1.326 exposing no re-read command.

**desk/033 (22:21), a desk tool returns a PR's review threads.** EMB-176: `github_pr_threads`.
**Merged:** `agent/desk/033-a-desk-tool-returns-a-prs-review-threads` (code `6785411`, ff on `640cb0c`; doc `d2b80b48`, the worker's `9a8f00cc` cherry-picked onto `3ff120e5`). `cargo test` 271 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** desk rebuild and redeploy, then one `github_pr_threads` on a real PR.
**Least sure about:** a thread answered in a review body or resolved without a reply still reads as awaiting.

**api/159 (22:19), bundle recover line states only what Core decided.** EMB-203's forward fix.
**Merged:** `agent/api/159-bundle-recover-line-states-only-what-core-decided` (code `0f6fb6c`, ff on `3479afa`; doc `4b424223`, the worker's `c39f7384` cherry-picked onto `76201b0d`). `cargo test` 228 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new. The `api/157` debt stands, now unblocked on the wording side: `embarch-api bundle` on a real nRF54L sysbuild directory, then flash its hex with the README's program command. **Owed, owner-side:** `embarch-api` rebuild and redeploy before a bench engineer sees the corrected README.

**atlas/072 (22:18), search schematic PDF pages.** EMB-156 second half: `schematic_text`.
**Merged:** `agent/atlas/072-search-schematic-pdf-pages` (code `c4e2601`, ff on `56e1cee`; doc `09b149a3`, ff on `a93b940a`). `pytest` 865 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one `schematic_text` search against a real board's PDFs.
**Least sure about:** `pdftotext` runs on every PDF on every call, uncached.

**umbrella/097 (19:15), embarch verify-release.** Folded step 3 out of the signing proposal. CI: `build-check.yml` run `44217599100` passed on `aarch64-unknown-linux-gnu`, `x86_64-unknown-linux-gnu`, `x86_64-pc-windows-msvc`; `aarch64-apple-darwin` cancelled, not blocked on.
**Merged:** `agent/umbrella/097-embarch-verify-release` (code `41cbf56`, ff on `47feb0f`; doc `52a81f11`, the worker's `3a6d8404` cherry-picked onto `ecf10a06`). `cargo test` 272 passed (offline).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a re-run of run 44217599100's macOS leg, or a look at the next push's.
**Least sure about:** whether `sigstore-verify` binds identity to the certificate's SAN alone or also to the extensions.

**promptu/010 (19:13), shell writes to a memory index get checked.** EMB-187: the PreToolUse hook also matches `Bash`; warns, never refuses.
**Merged:** `agent/promptu/010-shell-writes-to-a-memory-index-get-checked` (code `2a1750d`, ff on `20063c7`; doc `04e5dff2`, the worker's `22f46dcb` cherry-picked onto `b5201cec`). `cargo test --all-targets` 127 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** decision 5 (`decisions/memory.md`) says "Write, Edit and MultiEdit" only. **Owed, owner-side:** plugin reinstall for the `Bash` matcher; `tasks/promptu/008` stays `blocked` (`decisions/patterns.md` 11,138 of 12,288 B, due 2026-11-24).
**Least sure about:** an extra process per Bash call, unmeasured.

**atlas/071 (19:11), checks flag module pads left without a port.** EMB-188, EMB-156's `checks.md` half: `pad-without-name`, `dt-pin-unresolved`.
**Merged:** `agent/atlas/071-checks-flag-module-pads-left-without-a-port` (code `56e1cee`, ff on `e815f43`; doc `78932c3d`, the worker's `139ce5e9` cherry-picked onto `5ce81ee3`). `pytest` 863 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a first atlas of a real module schematic.
**Least sure about:** whether `pad-without-name` is noisy on a real board.

**api/158 (19:10), bundle README commands match Core's decisions.** Kept despite a confirmed finding (EMB-203); fixed by `api/159`.
**Merged:** `agent/api/158-bundle-readme-commands-match-cores-decisions` (code `3479afa`, ff on `9e4a99f`; doc `206a5584`, ff on `82d74a80`). `cargo test` 228 passed.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-203
**Hardware debts:** none new. The `api/157` debt stands: `embarch-api bundle` on a real nRF54L sysbuild directory, then flash its hex with the README's program command once EMB-203 has corrected the Recover line. **Owed, owner-side:** `embarch-api` rebuild and redeploy.
**Least sure about:** two findings in a row on the same README line say it was written from the decisions' summaries.

**chat/029 (18:28), the Promptu card restores the original prompt.** EMB-197.
**Merged:** `agent/chat/029-the-promptu-card-restores-the-original-prompt` (code `f79c167`, ff on `7a9aaf1`; doc `f47ffc83` and `72730863`, cherry-picked onto `0c1f3f47`). `npm test` 307 passed, 78 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the installed `promptu` predates `promptu original`, so the action fails here until Promptu is rebuilt and reinstalled; extension rebuild and reinstall.

**api/157 (18:21), bundle a build for a bench engineer.** Kept despite a confirmed finding (EMB-202): the README's nRF54L program command used `ERASE_ALL` while claiming to be Core's record (Core decision 36); fixed by `api/158`/`api/159`.
**Merged:** `agent/api/157-bundle-a-build-for-a-bench-engineer` (code `9e4a99f`, ff on `54d4035`; doc `95ba8548`, cherry-picked onto `0d1af7d3`). `cargo test` 413 passed; new `features.d/api-328-bundle.md` row.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-202
**Hardware debts:** `embarch-api bundle` on a real finished nRF54L sysbuild directory, then flash its hex with the README's program command once EMB-202 has corrected it. Needs any nRF54L board. Only a synthetic `zephyr.dts` (32-bit `reg` cells assumed) and a synthetic hex have exercised it. **Owed, owner-side:** a rebuild and redeploy before the verb or tool exists anywhere.
**Least sure about:** keeping rather than reverting; the revert would be `9e4a99f` and `95ba8548`.

**atlas/070 (18:18), recover rotated module pad names from the text layer.** EMB-89.
**Merged:** `agent/atlas/070-recover-rotated-module-pad-names-from-the-text-layer` (code `e815f43`, ff on `39b34b5`; doc `fe56b8ea`, cherry-picked onto `dcd820c9`). `pytest` 861 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** a recovered name has no mark in the graph UI, `nets.md`, `parts.md`. **Owed, owner-side:** a first run on a real module schematic.
**Least sure about:** `PAD_NUMBER_REACH` at 20 pt is a guess.

**dev-bench/048 (18:15), check and refresh patch sums.** EMB-146: `scripts/patch-sums.py`.
**Merged:** `agent/dev-bench/048-check-and-refresh-patch-sums` (code `60ab42c`, ff on `0aaf5d68`; doc `dfb81491`, cherry-picked onto `1afcf9a1`). `test_patch_sums.py` 5 passed. Size debt `tasks/dev-bench/049` filed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** `spec.md` calls `--check` "the gate's step"; the repo's `CLAUDE.md` makes it manual.

**desk/031 (18:05), read a desk route's shape.** EMB-137: `embarch-desk get`.
**Merged:** `agent/desk/031-read-a-desk-routes-shape` (code `640cb0c`, ff on `0a62c64`; doc `d2000b58`, cherry-picked onto `8d391395`). `cargo test --all-targets` 268 passed. Size debt `tasks/desk/032` filed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** desk rebuild and redeploy.
**Least sure about:** `--post` lets a shell send a body to any route from a verb documented as a read.

**promptu/009 (18:03), list an earlier run's questions and answers.** EMB-185: `promptu prior`.
**Merged:** `agent/promptu/009-list-an-earlier-runs-questions-and-answers` (code `20063c7`, ff on `946207b`; doc `e566e70f`, cherry-picked onto `7b81f4eb`). `cargo test --all-targets` 125 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** rebuild and reinstall; `tasks/promptu/008` stays `blocked`.

**atlas/069 (18:02), check L verifies the level-words column.** EMB-160.
**Merged:** `agent/atlas/069-check-l-verifies-the-level-words-column` (code `39b34b5`, ff on `90f70f2`, the recovery commit `6301f43` reworded; doc `caacee9f`, `4f5e516d` and `c97c1e1f` cherry-picked onto `083b875f` as `40f72d4e` and `caacee9f`). `pytest` 858 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** DESIGN.md's record-schema row still reads "check L: the item and the level are in it".

**chat/028 (18:01), read where a dead session stopped (re-land).** Re-land of the reverted build plus the EMB-200 fix.
**Merged:** `agent/chat/028-read-where-a-dead-session-stopped` (code `7a9aaf1`, ff on `3288cf6`, carrying `c55f218`, the revert of the revert; doc `78a723b3`, `88f845e7` and `e9b0e2a8` cherry-picked onto `ce5d34ba` as `1792667a` and `78a723b3`). `npm test` 306 passed, 78 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** extension rebuild and reinstall.
**Least sure about:** `hostHooks` wiring has no test of its own.

**chat/028 (14:47), read where a dead session stopped (first landing, reverted).** Reverted on a confirmed contradiction: EMB-200, `last_session` read the extension host's login, not the chat's, against decision 101.
**Merged:** nothing net. Code `97cf346` landed (ff on `61ceee2`) and was reverted by `3288cf6` on `embarch-chat` `main`. Doc half `88f845e7` (cherry-picked as `d67da2d7`, never pushed) dropped; it survives on `origin/agent/chat/028-read-where-a-dead-session-stopped` in `embarch-doc`.
**Blocked:** `chat/028` left `open`: re-dispatchable as is, `git revert 3288cf6` plus the login fix.
**Reviewer:** 1 finding — EMB-200
**Hardware debts:** none.

**atlas/068 (14:37), a shared datasheet library and a copy of each file used.** EMB-198.
**Merged:** `agent/atlas/068-a-shared-datasheet-library-and-a-copy-of-each-file-used` (code `90f70f2`, ff on `c63849c`; doc `3b7f50c7`, cherry-picked onto `899528ad`). `pytest` 856 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** no test drives the schematic ingest's copy; `join` and `build` do not refresh the manifest. **Owed, owner-side:** a first real run with a library set; skills reach sessions after re-install.

**promptu/007 (14:35), rewrite the rough prompt and log the original.** EMB-196, owner decision 42.
**Merged:** `agent/promptu/007-rewrite-the-rough-prompt-and-log-the-original` (code `946207b`, ff on `e8b58c7`; doc `9621d6f0`, cherry-picked onto `8a6f8d5b`). `cargo test` 121 passed. desk/030's doc landed as `5c9e44c8` (fold `8a6f8d5b`), not `1ce40c48`.
**Blocked:** nothing. Size debt `tasks/promptu/008` filed.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** ten real `/promptu` prompts, then `promptu stats`; plugin not reinstalled; the weekly loop (step 4) is unbuilt.

**desk/030 (14:31), compact-desk.** Doc only.
**Merged:** `agent/desk/030-compact-desk` (doc only, `1ce40c48`, ff over `b3028c0f`; later `5c9e44c8` in the fold).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**atlas/067 (14:21), worktree sessions find the main clone's atlas.** EMB-90.
**Merged:** `agent/atlas/067-worktree-sessions-find-the-main-clones-atlas` (code `c63849c`, ff on `ce0c899`; doc `a984cfb2`, cherry-picked onto `f4ae7c4a`). `pytest` 844 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `install.py` re-install for the new `atlas-use` trigger.

**promptu/006 (14:20), count tool calls and result characters per subagent.** EMB-149.
**Merged:** `agent/promptu/006-count-tool-calls-and-result-characters-per-subagent` (code `e8b58c7`, ff on `95f0d69`; doc `9fd7c031`, cherry-picked onto `2b01ca82`). `cargo test --all-targets` 115 passed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**desk/029 (14:18), a key from the opening prompt must name a real issue.** EMB-9; Withheld decision EMB-199.
**Merged:** `agent/desk/029-a-key-from-the-opening-prompt-must-name-a-real-issue` (code `59691f7`, ff on `02f9f5a`; doc `af948af6`, cherry-picked onto `a765bb6a`). `cargo test` 264 passed. Size debt `tasks/desk/030` filed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `plugin.json` version bump and push for the SKILL.md change; desk redeploy.

**chat/027 (14:17), compact-chat.** Doc only.
**Merged:** `agent/chat/027-compact-chat` (doc only, `a5f8c1e3`, ff over `d87f81a1`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
*Days 2026-11-14 to 2026-11-14 rolled to [log-archive/supervisor-log-2026-11-14-to-2026-11-14.md](log-archive/supervisor-log-2026-11-14-to-2026-11-14.md).*
