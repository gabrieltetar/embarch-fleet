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

## 2026-11-23 15:04 — atlas/101 design-records-the-mcp-server-as-atlas-transport

**Decided:** nothing suite-wide. **Filed by this leg, not split from an issue:** the depth-and-spread refill gate fired at 0 dispatchable, and a fresh read of `collect-open-questions.py` found `embarch-atlas/design.md` still listing the atlas's transport as "unresolved" (a tool on `embarch-api`'s MCP surface or its own server), with a 2026-08-25 paragraph leaving it for whoever resumed the work, while `embarch-atlas mcp` (`mcp_server.py`, the `mcp` extra, registered per project in `.mcp.json`) ships. I filed `tasks/atlas/101` (`fddca96d`), claimed it (`ad6638c9`) and dispatched one foreground worker. It replaced the open question and the status paragraph with a short "Transport" section: settled as its own stdio MCP server; the one checkable fact is that the engine is Python and `embarch-api` is Rust and gains no dependency; it says plainly that no written deliberation exists, so it records the outcome only. It dropped the old paragraph's "second process for the C#/WPF GUI's future debug-facing mode" as moot (the reviewer agreed: `embarch-ui`'s Atlas tab reads files, not the server). **I folded the worker's `status.d` fragment into `embarch.md` §2 myself**: "it is paused rather than dropped. It will resurface as `embarch-atlas` ... MCP is a plausible transport" now reads that it resurfaced as `embarch-atlas`, answering over its own MCP server and its CLI alike, not a tool on `embarch-api`'s surface. **Leg, to carry:** step 0 recovered nothing (no claim, no unit worktree, no stop marker, no unfolded `status.d`; pump latched). Fleet Ready holds EMB-228 (the owner is writing it on `feature/emb-228-hil-guide`, its progress comment says a leg leaves it alone; EMB-246 and EMB-247 wait on it), EMB-178 and EMB-112 (need a real hierarchical schematic export), unsplit as before. The full sweep (every `open.md`, the roadmap and reversals unchanged since 2026-11-11) found only this one; everything else is hardware-gated, an owner's call, or under `scripts/`. **This leg ends at one unit and dreamt**: `--dream-check` said `ASK` (main moved by the deploy and this leg's two commits since the 14:56 dream), so I posted, ts `1795471472.393629`, with `--action` and `crystal_ball`: the 14:56 asks stand, plus three smaller ones (compact `embarch-core` decision 110, 6.5 KB against the 4 KB per-decision cap, unpinned; make `embarch-ui`'s legacy `/api/topology/profiles` routes refuse a non-slug path; add a `promptu` section to `scripts/build_features.py`, the owner's). None is in the queue.
**Merged:** `agent/atlas/101-design-records-the-mcp-server-as-atlas-transport` (code none, the branch had no commits; doc `4edf440a`, ff from `ad6638c9`). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. No pytest: no code or `DESIGN.md` changed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at the start (5-hour 73%, weekly 28%, wave 6; the 5-hour window resets inside the hour, so ignored) and at this fold (5-hour 75%, weekly 28%).
**Least sure about:** the new section's "engine is Python, `embarch-api` is Rust" as what settled the transport: it is a true, checkable fact, but whoever built `mcp_server.py` may have chosen for another reason nobody wrote down. The reviewer also noted `embarch-atlas/design.md`'s head still calls the doc a placeholder awaiting resumed design work, which was stale before this unit and is left as it was.

---

## 2026-11-23 14:55 — atlas/097 prior-art-search-returns-a-hit-table

**Decided:** **not to land a finished, green unit, and to send it to the owner as EMB-248** (Backlog, `Type: decision`). The worker built `embarch-atlas prior-art search` (new `priorart.py`, CLI only, standard library plus `fetchtext`'s block detection; one query POST then one bibliographic page per hit, at most 12 requests a run, 2 s apart, stop at 403, 429, 503 or a challenge page, exit 3) and read the source's rules first, as the task required: the terms of use forbid bulk downloads and over 5,000 requests a day, but the search host's robots exclusion file reads `User-agent: *` / `Disallow: /`. The worker judged a user-invoked query not to be crawling and wrapped it anyway, and asked for the owner's word. The task's own rule was that a source whose terms forbid automated queries is not wrapped, and a public repo shipping a tool that ignores a host's robots file is the owner's call, not a leg's, so the task is `blocked` with `Unparks when:` the owner's word on EMB-248. EMB-248's options, recommendation first: wrap an official patent API instead (a key the owner registers), land the branch as built, or drop the verb and close EMB-136. EMB-136 has a Blocked comment pointing at it. I did not fetch the robots file myself; the line is the worker's report. **The branches stay pushed and unlanded**: `agent/atlas/097-prior-art-search-returns-a-hit-table`, code `572bca3`, doc `fafa3f2c`; on a go, a leg gates and lands them as they stand. The doc branch also files `tasks/atlas/100-compact-atlas.md` (its new section puts `embarch-atlas/design.md` at 24,000 of 25,600 B), which is not on `main` because the section is not. Live requests made by the worker: 15 to the search host, 3 to the office's main site for the terms and robots file, generic terms only. **Leg end, to carry (added after this fold):** nothing a worker can take is left (confirmed with `queue-status.py --root` against `ls tasks/*/`, 13 task files, none dispatchable; Fleet Ready's EMB-228, EMB-178 and EMB-112 stay unsplit, as earlier legs left them). The refill gate fired on depth and spread; the last full sweep was about 12:45, and the only sources changed since were `embarch-api/open/bench-verification.md` (`api/175`), `embarch-core/open.md` (`core/138`) and `embarch-api/open.md` (`api/172`), which I read: bench debts and one removed owed item, nothing dispatchable. So this leg ends at two units and **dreamt**: `--dream-check` said `ASK` (35 commits since the unanswered 2.0-hour-old dream), and I posted three proposals with `--action` and `crystal_ball`, ts `1795470987.232699`: answer EMB-248; drop a real hierarchical schematic export for EMB-178 and EMB-112; plug in the bench for `api/059` and `dev-bench/038`. The pump stays latched. A framework deploy is queued in `.fleet/pending-deploy` (`1c25ce9`, foreground waves and `task-state.py`); this leg already dispatched in the foreground and claimed and closed with `task-state.py`, as that change says.
**Merged:** none (blocked before any merge). Re-gated on the branch, not merged: `.venv/bin/pytest -q` 994 passed, 4 skipped (real west workspace, built atlas, vendor SVD, the opt-in live smoke test; `test_public_guard` ran); ownership green on both branches; client names clean on the code repo.
**Blocked:** `agent/atlas/097-prior-art-search-returns-a-hit-table` — the robots-file question above; task `blocked` on EMB-248, worktrees removed, branches kept. `atlas/098` and `atlas/099` stay blocked behind it.
**Reviewer:** skipped (not landed: blocked on EMB-248 before any merge).
**Hardware debts:** none.
**Budget:** PROCEED at dispatch (5-hour 66%, weekly 27%, wave 6) and at this fold (5-hour 71%, weekly 27%; the 5-hour window resets inside the hour).
**Least sure about:** whether blocking was too cautious: the terms of use allow this volume and the robots file is commonly read as addressed to crawlers, so the owner may simply say land it; I chose the reading the task itself set, because the repo is public and a landed scraper is harder to take back than a parked branch.

---

## 2026-11-23 14:44 — atlas/096 translation-fills-a-module-pads-port

**Decided:** nothing suite-wide. **Recovered, not dispatched, by this leg:** the leg that took the lock at 14:05 split EMB-245 into `atlas/096` and EMB-136 into `atlas/097` to `099` (`b5c7ff65`), claimed 096 (`29f15e09`), dispatched its worker at 14:09 and handed back early with no log entry. The worker finished and pushed both branches; I gated and landed them from the pushed branches (presence rule), and waited out that leg's lock to 14:39 rather than take it over. The change: `skills/atlas-translate-docs/reference/datasheet-procedure.md` gains one pin-record rule for a module's pad table (`pin` the pad number, `name` the pad's printed name, `port` the SoC port the table prints, normalised `PA4` or `P1.05`, never inferred, left off a pad the table ties to no port); `DESIGN.md`'s pad-table paragraph and `embarch-atlas/design.md` say so and still say only synthetic records are tested. No new check: the record schema's `port` pattern already refuses a malformed value through `check` (that pattern accepts `P0.4` too; the join pads it). **The worker left the task's State line `claimed`**; I closed it `done` with `scripts/task-state.py` at this fold. Also this leg, before landing: **EMB-129 and EMB-151 closed** with `fleet-linear.py close`, both landed on `main` by the owner (`8ee6c6bb`; `8088d6e0` and fleet `1c25ce9`), as their own progress comments asked. Fleet Ready now holds EMB-228, EMB-178 and EMB-112, left unsplit as before. EMB-245 goes to Done at `finish` after this push.
**Merged:** `agent/atlas/096-translation-fills-a-module-pads-port` (code `2adf1cc`, ff from `dae31d4`; doc `6d42f66b`, the worker's `348abdc2` cherry-picked onto `6a5a36bc`). Re-gated on the merge result: `.venv/bin/pytest -q` 982 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Translate one real module datasheet with the skill and confirm `port` on its pad records (an engineer-supplied datasheet, no board); none sits in either repo.
**Budget:** PROCEED at the start (5-hour 63%, weekly 27%, wave 6) and at this fold (5-hour 66%, weekly 27%, wave 6).
**Least sure about:** whether a translator reading the new rule fills `port` from a real module pad table at all, since the rule has met no real datasheet. The reviewer left one point unread, the join's zero-padding of `P0.4`; I read it: `mcu_port` in `join.py` pads to two digits, as the procedure says.

---

## 2026-11-23 14:04 — atlas/095 atlas-live-tools-work-under-the-sessions-own-lease

**Decided:** nothing suite-wide. Atlas-only route, `embarch-api` untouched: every live MCP tool (`shell`, `shell_run`, `reg_read`, `reg_read_clear`, `reg_read_bank`, `live_stacks`, `core_state`) takes an optional `lease_token`, the value `lease_take` returned once. `live.lease(token)` holds it in a context variable for that call, `call_api` passes it as `EMBARCH_LEASE_TOKEN` in the `embarch-api` CLI child's environment only (never argv), and every CLI failure text is scrubbed of it; the atlas CLI's own `live` verbs inherit the shell's variable and take no argument. `_NOT_WRITTEN`, the "provably nothing was written" test, now also matches `\b409\b` and `\blease\b`, so a lease refusal reads as "did not run" (exit 1). **One correction to the worker's report:** it says the next console is not tried after a refusal; by the code, a `_NOT_WRITTEN` match moves to the next declared console, which a 409 also refuses, so the outcome is the same but the report is wrong on the mechanism. The 409's wording is assumed, not measured. **Leg end, to carry:** this is the fourth unit; nothing host-side is left in `tasks/`. Fleet Ready holds EMB-245 (new this leg, atlas: teach `atlas-translate-docs` to fill a module pad's `port`), EMB-136 (atlas patent search; large, needs live web endpoints, so the worker brief must say whether it may hit them) and the six no leg can take as written (EMB-112 and EMB-178 need a real hierarchical schematic export, which the owner asked to be asked for; EMB-85, EMB-228, EMB-129, EMB-151). Bench `api/059` and `dev-bench/038` stay `open`, no board attached.
**Merged:** `agent/atlas/095-atlas-live-tools-work-under-the-sessions-own-lease` (code `dae31d4`, ff from `64d2c5b`; doc `910c80c9`, ff from `b185dcac`). Re-gated on the merge result: `.venv/bin/pytest -q` 982 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** with the lease taken through the embarch-api MCP, atlas `shell` `device list` in the same session with `lease_token` set should return the device list, not a 409; and Core's real 409 text for a wrong or missing token should still match `409|lease`. Needs a live Core and a board (recorded in the task's Outcome, now retired).
**Budget:** PROCEED at this fold (5-hour 46%, weekly 25%, wave 6).
**Least sure about:** the widened `_NOT_WRITTEN`: any CLI error text containing the word `lease` or `409` now counts as provably unwritten and lets the next console be tried; that is safe only while Core checks the lease and its lock before it opens a port, which nobody here has read in Core's code or measured.

---

## 2026-11-23 13:57 — atlas/094 a-modules-pad-table-gives-unnamed-pads-their-port

**Decided:** nothing suite-wide. The worker added no new record kind: a module datasheet's existing `pin` record gains an optional `port` (`schemas/record.schema.json`), the pad number staying in `pin` and the module's pad name in `name`, keyed to the module like any pin record (the document covering its MPN, `package` as usual). `build_pin_map`'s port order is now the symbol's pin name, then that `port` (`port_source` `module pad table`, printed `P1.03 (from module pad table)`), then the datasheet pin number, then `atlas/092`'s port-named net. **The symbol wins over a disagreeing pad table**: `pins.json` carries `port_conflict` and `pins.md` prints `P0.04 (pad table says P0.09)`; the worker's call, one line in `build_pin_map` to flip. A port is normalised (`P1.3` to `P1.03`); `port_why` names a `port` on the pad-table record as the remedy. **EMB-243 is met for the record and the join, not for translation**: the `atlas-translate-docs` skill was not told to emit `port`, so the field is filled by hand or as an `engineer-declared` record until it is. I filed that remainder as **EMB-245** (Fleet Ready, gap, atlas). In this fold I changed one word in `embarch-atlas/design.md` ("the datasheet's pin name" to "pin number", matching `DESIGN.md` and the code), which the reviewer noted as cosmetic. EMB-243 goes to Done at `finish` after this push.
**Merged:** `agent/atlas/094-a-modules-pad-table-gives-unnamed-pads-their-port` (code `64d2c5b`, ff from `902f144`; doc `8f75e182`, ff from `a56d71f1`). Re-gated on the merge result: `.venv/bin/pytest -q` 978 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The pad-table source has met one synthetic module fixture; no real module datasheet has been translated with `port`.
**Budget:** PROCEED at this fold (5-hour 43%, weekly 25%, wave 6).
**Least sure about:** symbol-wins on a conflict: a module symbol drawn with a stale or copied pin name would keep the wrong port, flagged in `pins.md` but still printed first; nobody has decided which source an engineer trusts more on a module board.

---

## 2026-11-23 13:52 — atlas/093 shell-commands-help-text-and-kernel-subcommands

**Decided:** nothing suite-wide. Two causes, both read by the worker from Zephyr 4.4's own source (`shell.h`, `shell_utils.c`), no board image: the help pointer in 4.4 is `SHELL_HELP(description, usage)`, a `struct shell_cmd_help` whose first word is a magic number (the issue's garbage bytes are that word, little-endian), and `kernel`'s set is built by `SHELL_SUBCMD_SET_CREATE` plus `SHELL_SUBCMD_ADD`, a zero placeholder in `shell_subcmds` with the added entries laid after it, which `_walk` read as an empty set. In `shellcmds.py`, `_Image.help` decodes a plain string or the structured form and `_Image.text` gives "" for anything not printable ASCII, so help never prints bytes; a new `usage` field prints after the help; `_table` walks from just past the placeholder when the pointer is zero inside `shell_subcmds`, the old pointer-to-array form still read. `shell.json`'s `SCHEMA` goes from 1 to 2 so a cached record is recognisable; the reviewer checked that the old-record path in `query.py` reads `usage` with `.get`. `DESIGN.md` and `embarch-atlas/design.md` updated. EMB-234 goes to Done at `finish` after this push.
**Merged:** `agent/atlas/093-shell-commands-help-text-and-kernel-subcommands` (code `902f144`, ff from `893275d`; doc `ec22da7f`, the worker's `e800a878` cherry-picked onto `74e0cfb2`). Re-gated on the merge result: `.venv/bin/pytest -q` 977 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Both layouts have met only synthetic ELFs built from the 4.4 headers; `shell_commands command=kernel` and `command=i2c` on a real 4.4 image would confirm it, including the help struct's alignment on a 64-bit target.
**Budget:** PROCEED at this fold (5-hour 38%, weekly 24%, wave 6).
**Least sure about:** the placeholder rule keys on a zero pointer inside the `shell_subcmds` section; a Zephyr version that names or places that section differently would fall back to the old reading and list no subcommands again, silently.

---

## 2026-11-23 13:50 — api/175 build-verdict-reports-the-application-image-on-sysbuild

**Decided:** nothing suite-wide. `embarch-api` decision 128 (`decisions/log-capture.md`): `verdict::parse` keeps the **first** linker memory table in a build log instead of the last, on the evidence of the one sysbuild log in the issue, where the application's table (the default image `artifact_path` flashes) prints before MCUboot's. The worker chose this over one row per image because the `Linking C executable zephyr/zephyr.elf` line inside a sub-build names no image, and it did not read `domains.yaml`; `memory` stays flat, so the verdict's schema is unchanged. Decision 102 now points at 128; `interfaces/tools-build-flash.md` and `open/bench-verification.md` say "first table". Two consequences the decision records: a non-sysbuild log with several tables (a twister multi-build) now reports its first table, and the application-first order is assumed, not measured. `crates/embarch-firmware-build` is path-depended on by `embarch-ui`; I read the diff before landing (a guard on `verdict.memory.is_empty()` plus one test, no API change) and did not build `embarch-ui` against it. **Leg setup, to carry:** step 0 found nothing to recover (no claim, no unit worktree, no stop marker; pump latched). Fleet Ready held 11 issues. I split three atlas issues into `tasks/atlas/093` (EMB-234), `094` (EMB-243) and `095` (EMB-233, verify-only) in `e5d025c2`, filed them, and announced (ts `1795466178.988799`). **EMB-15 sent back to Backlog**: both of its boxes were met by EMB-94 (desk decision 77); the comment names the `store.rs` test that proves it and asks the owner to mark it Done. Left unsplit in Fleet Ready, as the last leg left them: EMB-112 and EMB-178 (both need a real hierarchical or repeated-channel schematic export; the owner asked to be asked for one when they come up), EMB-85 (Promptu step 3's forks still undecided), EMB-136 (patent search, large, needs live web endpoints), EMB-228, EMB-129, EMB-151 (owner-reserved paths or interactive). The refill gate fired spread-only (2 scopes, wave 6); the one source changed since the 13:10 line was `embarch-atlas/design.md` (`atlas/091`'s package section), which I read: no open question. Spread sweep: nothing filed (2026-11-23 13:35). No board attached at the 13:34 refresh, so bench `api/059` and `dev-bench/038` stay `open`. Workers went out as two foreground calls in one message (api, atlas) and both reported to the leg.
**Merged:** `agent/api/175-build-verdict-reports-the-application-image-on-sysbuild` (code `e68ce94`, ff from `de53e6e`; doc `ffe77a59`, ff from `9a539ba9`). Re-gated on the merge result: `cargo build`, `test`, `clippy --all-targets -D warnings` with default features and with `--no-default-features`, green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The first-table rule has met one synthetic two-table log shaped like the issue's; no real sysbuild build log has been parsed.
**Budget:** PROCEED at the start (5-hour 29%, weekly 23%, wave 6) and at this fold (5-hour 38%, weekly 24%, wave 6).
**Least sure about:** that a sysbuild log always prints the application's table first: ninja builds the images as separate sub-builds and their order in the log is not something anyone here has measured, and a build where only MCUboot relinks would report MCUboot's table (the reviewer's gap, already in `open/bench-verification.md`); if the order varies, the fix is to tie each table to its image by the sub-build line that precedes it, which the worker did not look for.

---

## 2026-11-23 13:30 — atlas/092 pin-table-fills-port-and-dt-use-for-every-module-pin

**Decided:** nothing suite-wide. **The cause was not the join the issue named.** Measured by the worker on a real module board (pads 15 to 31, 17 pads; nothing from that atlas entered either repo): the schematic symbol prints a pin name for only some module pads, the unnamed ones carry `name: None` in `netlist.json`, `port_of_key` reads that name, and the datasheet fallback has no row because the only translated datasheet is the SoC's, whose pin numbers are not the module's pads. No port meant no DT lookup and `pins.md` printed a blank. The change, in `build_pin_map` (`src/embarch_atlas/join.py`): a pad with no port takes one from a net named after a port, whole segment only (`P1.05/RX`), recorded as `port_source` in `pins.json` and printed `P1.05 (from net name)`, and the DT column then fills from pinctrl and gpios; a connected non-rail pad still without a port prints `(no port: …)` naming the remedy (`pin_names.json`, or translating the module's pad table); a port found through the datasheet pin number is now marked too. `DESIGN.md`'s "an empty port" line rewritten. **EMB-237 is only partly met, and the task says so in its Outcome:** pads whose nets are named for their function (the I2C pair, SPI lines, PWM gates on that board) still have no port, because no atlas input holds a module's pad-to-port map. The worker ticked the first box anyway; I left the task `done` (the rest needs a new record kind, not more of this unit) and filed the remainder as **EMB-243** (Fleet Ready, gap, atlas): translate a module's pad table. EMB-237 goes to Done at `finish`; EMB-243 carries the rest.
**Merged:** `agent/atlas/092-pin-table-fills-port-and-dt-use-for-every-module-pin` (code `893275d`, ff from `0180a9f`; doc `8d6a4755`, ff from `d8052972`). Re-gated on the merge result: `.venv/bin/pytest -q` 974 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The net-name fallback has met one generic module fixture; the real-board read was the worker's diagnosis, not a test.
**Budget:** PROCEED at this fold (5-hour 27%, weekly 23%, wave 6).
**Least sure about:** the net-name port is an inference: a net named after one port but wired to another pad would print a wrong port, labelled `(from net name)` but still wrong; the reviewer found it consistent with atlas's rule that an inferred fact is labelled, and nobody has decided whether it should be on by default.

---

## 2026-11-23 13:21 — desk/041 missing-embarch-api-line-names-every-missing-piece

**Decided:** nothing suite-wide. The worker extended `embarch-desk` decision 82 (`decisions/desks.md`) in place rather than filing a new one: `mcpreg.rs` `session_text` now lists the missing pieces in order (the register command, then `embarch init` in the repo's main clone, found by following a worktree's `.git` file, shown only when neither the main clone nor the folder has `embarch/embarch.toml` and the copied `--config` has no project with that `source_path`); says, when the copied `--config` belongs to another project and the repo has its own config, that the server still resolves the desk's repo through it; and ends by saying bench work goes through EmbArch only, so the session stops and asks the user rather than using `west flash`, `nrfutil`, `nrfjprog`, `JLinkExe`, `probe-rs` or `usbipd`. `folder_json` gains `init_in` and `own_config_used` when they apply (`interfaces.md`). `embarch-desk/spec.md` was not written, so it stays in reserve at 9,186 B and `tasks/desk/038` stays parked as it was. The new text reaches sessions only once the owner updates the installed desk. EMB-230's `finish` moves it to Done after this push.
**Merged:** `agent/desk/041-missing-embarch-api-line-names-every-missing-piece` (code `08214ff`, ff from `25b6877`; doc `28142601`, the worker's `64e84faf` cherry-picked onto `e06d6845`). Re-gated on the merge result: `cargo build`, `test` (302 pass), `clippy --all-targets -D warnings` green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at this fold (5-hour 25%, weekly 23%, wave 6).
**Least sure about:** the case the worker left alone: a folder whose login already has `embarch-api` registered but whose repo has no `embarch/embarch.toml` gets no line at all, so that session still meets `resolve`'s "run `embarch init`" error only when it first asks for a build; the issue asked only for the unregistered case.

---

## 2026-11-23 13:20 — api/174 zephyr-west-scan-takes-cpu-clusters-from-the-soc

**Decided:** nothing suite-wide. `embarch-api` decision 127 (`decisions/zephyr-scan.md`): when no variant of a SoC in `board.yml` names a CPU cluster, the zephyr-west scan reads that SoC's `cpuclusters` from a `soc.yml` and tries `<board>_<soc>_<cluster>.dts` (plus each named variant per cluster), each still passing the existing `.dts` check; a `board.yml` that names its clusters scans as before. It looks for `soc.yml` under `<source_path>/soc`, `<source_path>/zephyr/soc` and `<source_path>/../zephyr/soc`, six levels deep, taking any mapping with a `name` and `cpuclusters`; with none found, the drop message is today's plus "found no soc.yml defining soc <soc>". `interfaces/config-selection.md` gained one sentence. Two narrowings the decision states: a SoC defined by a module outside those three roots is not found, and a SoC that has clusters no longer offers the bare `<board>_<soc>.dts` target (Zephyr would not build it either). EMB-231's `finish` moves it to Done after this push.
**Merged:** `agent/api/174-zephyr-west-scan-takes-cpu-clusters-from-the-soc` (code `de53e6e`, ff from `97d58d8`; doc `5a56344c`, the worker's `3adab50a` cherry-picked onto `919e5327`). Re-gated on the merge result: `cargo build`, `test` (485 pass, 482 plus the three new), `clippy --all-targets -D warnings` with default features and with `--no-default-features`, green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The scan has met only a fixture `soc.yml` shaped like Zephyr's `soc/nordic` file, never a real Zephyr tree or the project that filed the issue; that project still runs `discovery = "static"` until someone switches it back.
**Budget:** PROCEED at this fold (5-hour 24%, weekly 22%, wave 6).
**Least sure about:** the six-level walk of three roots for every `soc.yml` on each scan of a SoC with no named clusters; on a full Zephyr tree that is likely well over decision 22's "low hundreds of files, under 100 ms" bound for a live scan, and nobody measured it. The reviewer read it as pressure on decision 22, not a contradiction; decision 22 already says to revisit caching if the scan turns perceptibly slow.

---

## 2026-11-23 13:18 — atlas/091 net-trace-uses-the-fitted-packages-pin-map

**Decided:** nothing suite-wide. The worker's design (recorded in `embarch-atlas/design.md`'s "Which package's pinout net_trace reads" and the code repo's `DESIGN.md`): when no package is declared in `bindings.json`, `Join.part_package_fitted` picks the fitted package from a component's `footprint`/`package` text naming exactly one package, else the one package whose pin names the schematic agrees with and none contradicts, else the one whose pin count matches; unresolved, `net_trace` shows the schematic pin name with "package not resolved: <reason>" and never takes the first package. The issue's exact `GND` misread was not reproduced (the old code already gave no record for an ambiguous pin, so the rail showed no source); the fix covers both. The footprint rule is untested on real data: no netlist writer emits a footprint yet. **Leg start, to carry:** the owner answered the 12:55 dream by moving 15 issues into Fleet Ready. I split five (EMB-231 → `api/174`, EMB-232 → `api/175`, EMB-236 → this task, EMB-237 → `atlas/092`, EMB-230 → `desk/041`; commit `4509d241`) and announced them (ts `1795464400.823999`). Left unsplit in Fleet Ready for later legs: EMB-15 (desk), EMB-234, EMB-233, EMB-178, EMB-136, EMB-112 (atlas); and four no leg can take as written: EMB-228 (a suite-level HIL guide whose body says "Interactive"), EMB-129 (`LINEAR-PROTOCOL.md`, owner-reserved), EMB-151 (`scripts/`, owner-reserved), EMB-85 (sent back 2026-11-18 because Promptu step 3 is unreviewed; `embarch-promptu/spec.md` still says so). The refill gate fired spread-only (3 scopes, wave 6). The previous leg's depth sweep (about 12:45) read every source; the only source changed since was `api/172`'s `embarch-api/open.md` edit, which I read: two hardware/real-Core debts, nothing dispatchable. Spread sweep: nothing filed (2026-11-23 13:10). Workers went out as three foreground calls in one message (api, atlas, desk), and all three reported to the leg. No board attached at the 11:43 refresh, so bench `api/059` and `dev-bench/038` stay `open`.
**Merged:** `agent/atlas/091-net-trace-uses-the-fitted-packages-pin-map` (code `0180a9f`, ff from `d80aa9f`; doc `b86eb5cc`, ff from `e01c28fb`). Re-gated on the merge result: `.venv/bin/pytest -q` 973 passed, 3 skipped (real west workspace, built atlas, vendor SVD; `test_public_guard` ran); `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The fitted-package inference has met only a generic two-package fixture, never a real board's atlas.
**Budget:** PROCEED at the start (5-hour 16%, weekly 22%, wave 6) and at this fold (5-hour 24%, weekly 22%, wave 6).
**Least sure about:** that the pin-name agreement rule picks the right package on a real distillation, where datasheet pin names and schematic symbol names are often spelled differently (`VOUT` against `OUT`); the worker's fixture used names that agree.

---

## 2026-11-23 12:55 — api/173 compact-api

**Decided:** nothing suite-wide. I unparked this task at `api/172`'s fold (its condition fired; `In flux:` set to `no` because a verbatim split restates nothing) and dispatched it here. The worker moved `embarch-api/interfaces/publish.md`'s `## verify` section byte for byte into a new `interfaces/verify.md` (4,370 B) and left a `## verify` heading with a one-line pointer so old anchors resolve; `publish.md` went from 11,070 to 6,951 of 12,288 B, out of reserve. One clause outside the moved text changed: `publish.md`'s status line now links `verify.md` instead of saying "the last section". Links retargeted in `embarch-api/spec.md`, `decisions/verify.md`, `decisions/verify-report.md` and `features.d/api-370-verify.md`. I checked the move myself before landing (20 removed lines, all in `verify.md` but the status line). **Does `spec.md` alone answer what someone needs to work on `embarch-api`'s publish and verify surfaces today?** The worker says no, by design: `spec.md` names what exists and the refusals; changing a check, the zip layout or revisions needs `interfaces/publish.md`, `interfaces/verify.md` and decisions 112 to 126. **Leg end, to carry:** nothing is dispatchable after this fold (confirmed with `queue-status.py --root` against `ls tasks/*/`), so this leg ends at three units and **dreamt**: `fleet-read.py --dream-check` said `ASK` (131 commits since the unanswered dream of 104 hours ago), and I posted three Backlog issues, each one worker unit and `Hardware: none` (EMB-231 api, EMB-236 atlas, EMB-230 desk), with `--action` and `crystal_ball`, ts `1795463694.766129`. The pump stays latched. Parked compactions `desk/038` and `dev-bench/049` fall due 2026-12-01 with their unpark conditions unmet; I left them.
**Merged:** `agent/api/173-compact-api` (doc only, no code branch; doc `7602bb15`, the worker's `66187c6e` cherry-picked onto `bf446f98`). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch; `check-doc-size.py --pressure` no longer lists the file.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at dispatch and at this fold (5-hour 13%, weekly 21%, wave 6).
**Least sure about:** unparking this task on my reading of its own condition ("the next unit that edits the `verify` section lands"); `api/172` edited one cell of the `verify` table, which is a narrow reading of "edits the section", but the move is verbatim and costs nothing to undo.

---

## 2026-11-23 12:51 — core/138 open-md-still-owes-verify-check-8

**Decided:** nothing suite-wide. I filed this task from the refill sweep: `embarch-core/open.md`'s run-log-tail bullet still said "Remains for M1.11: `verify` check 8 comparing the recorded head" after `api/170` built check 8. The worker replaced that clause with "`verify` check 8 (api decision 121) checks a zip's segment against the signed head; the publish's own entry is not checkable offline", keeping the bullet's "a tail cut after the last publish is not [detectable]". It grepped the rest of `open.md` and `open/*.md` for lines the verify decisions made false and found none; it did not search `embarch-core`'s code for a comment making the same claim. Its first wording pushed `open.md` into the reserve and it shortened it back out (3,915 B). The reviewer noted `embarch-core` decision 118 still calls check 8 "M1.11's", historical and not a contradiction. **Refill result, to carry:** this was the only thing the sweep found. The previous sweep (11:49) had read the same sources; the one source change since was `embarch-core/open.md`'s retention-sweep line, already covered by `api/172`. Roadmap Next unchanged since 2026-11-11, reversals the same.
**Merged:** `agent/core/138-open-md-still-owes-verify-check-8` (doc only, no code branch; doc `f3bf0c1d`, the worker's `c187939b` cherry-picked onto `4397f813`). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at this fold (5-hour 11%, weekly 21%, wave 6); the leg started DEGRADED on a stale cache (wave 2).
**Least sure about:** the bullet now cites "api decision 121" in a short form the reserve forced, where this repo's other cross-references spell out `embarch-api`; `check-decision-refs.py` passed it, but a reader may not resolve it at a glance.

---

## 2026-11-23 12:51 — api/172 republish-a-swept-run-from-the-earlier-zip

**Decided:** nothing suite-wide. `embarch-api` decision 126 (`decisions/publish-revisions.md`): when Core answers `report-data` with `409` for a swept run, `publish` takes the highest earlier zip, `PUT`s `manifest.dsse.json` first and then each Core subject the manifest names (skipping `report-data.*` and the segment), and asks `report-data` again; with no earlier zip it refuses, naming the folder and the zip names it looked for, and sends Core nothing. Decision 117 now points at 126. The shared crate `embarch-core-client` gained one method, `CoreClient::restore_file` (`PUT /study/{id}/restore/{name}`, reusing `study_timeout`, assumed); I read the diff before landing it, additive only, and did not build `embarch-ui` or `embarch-umbrella` against it. Also fixed in this unit: decision 110's stale "`main.rs` does not yet" line, decision 123, `open.md` and `verify_report.rs`'s comment now agreeing with `hil-pdf.md`'s 8 to 16 mm band, and check 5's stale "`adopted` recomputed" cell. **Leg setup, to carry:** the 11:52 leg was cut off when its login (personal) hit the 5-hour limit at 12:08; this unit's worker died with it, its tree uncommitted. The owner re-armed the pump on the work login at 12:33. I committed the dead worker's tree as found (`97d58d8`), pushed it, removed both worktrees, reclaimed (`f31b1850`) and resumed onto the same branch; the resumed worker built it, found it complete, changed no code and wrote the docs. **`tasks/api/173` unparked here, set `open`**: its condition (the next unit editing `verify`'s section) fired, but the compaction rode in only halfway. The worker moved a publish section verbatim to `interfaces/publish-pending-reads.md` and reported 11,040 B; `check-doc-size.py` reads 11,070, 11 B inside the reserve. I set `In flux:` to `no` on the split-first rule (a verbatim split of the `verify` section restates nothing). Workers this leg went out as foreground calls in one message (EMB-214's shape), so both reported to the leg. Fleet Ready empty; refill on depth swept every `open.md` and filed `tasks/core/138` (one stale line); bench `api/059` and `dev-bench/038` stay `open`, no board attached at the 11:43 refresh.
**Merged:** `agent/api/172-republish-a-swept-run-from-the-earlier-zip` (code `97d58d8`, ff from `2804e41`; doc `4397f813`, ff from `f31b1850`). Re-gated on the merge result: `cargo build`, `test` (482 pass), `clippy --all-targets -D warnings` with default features and with `--no-default-features`, green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The restore path has met a mock Core only: Core's real `409` body and `restore` answers are unseen, and no real swept run has been republished. `restore_file`'s timeout is assumed.
**Budget:** start: the gate read DEGRADED (work login's cache 2.9 days old, wave 2); a live probe of the work login read 5-hour 5%, weekly 20%. At this fold PROCEED (5-hour 11%, weekly 21%, wave 6).
**Least sure about:** decision 126 takes the restore path on any `report-data` error whose text contains `409`, as the `404` match it replaces did; a `409` for another reason would send the earlier zip's files and Core would refuse them, so nothing is written, but the message the user sees would be the restore refusal, not the first cause.

---

## 2026-11-23 11:57 — core/137 a-republish-after-the-retention-sweep-takes-the-earlier-zips-files

**Decided:** nothing suite-wide. `embarch-core` decision 120: a swept run is restored by `PUT /study/{id}/restore/{name}`, one raw file at a time — `manifest.dsse.json` first, accepted only if its SHA-256 is a `published` entry's `manifest_sha256` for this run in Core's own log (`422` otherwise), then each Core file only if an accepted manifest lists it with that digest (`409` before a manifest; `422` for a non-subject, a revision output or a wrong digest; nothing written on a refusal). `report-data` on a swept or half-restored run now answers `409` naming what is missing, and runs unchanged once everything is back; the envelope's signature is not re-verified, the logged hash standing in for it. **Leg setup, to carry:** the previous leg ended with this unit pushed and not landed, so I landed it from its pushed branches (presence retires a worker), as that leg asked; its worktrees were clean and the task still read `claimed`, which I set `done` here. The worker's code comments cited "decision 126"; I corrected them to 120 (`6116b1e`, comments only). This fold sets `tasks/api/172` open and adds a dispatch line naming decision 120's route and refusals. Fleet Ready was empty; bench `api/059` and `dev-bench/038` stay `open`, neither board attached at the 11:43 refresh. The 2026-11-22 day fold and `check-client-names.py --suite --history` already ran today in `promptu/008`'s fold, so this unit did neither.
**Merged:** `agent/core/137-a-republish-after-the-retention-sweep-takes-the-earlier-zips-files` (code `606b267` and `6116b1e`, ff from `88aff23`; doc `84ff218a`, worker's `f68ff56a` cherry-picked onto `574e6411`). Re-gated on the merge result: `cargo build`, `test` (436 pass) and `clippy --all-targets -D warnings` green; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code repo.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`, unrun (a worktree cannot build natively). The restore route has met only Core's in-process HTTP tests; no real retention sweep has run on the Windows service, and embarch-api does not send the files until `api/172`.
**Budget:** PROCEED at the start (5-hour 65%, weekly 4%, wave 6) and at this fold (5-hour 81%, weekly 5%, wave 5); the 5-hour window resets about 15:50.
**Least sure about:** the 1 GiB restore body is read whole into memory before it is hashed (`axum::body::to_bytes`), so a capture near the cap costs Core that much RAM per call; nothing measured how large a real capture gets.

---

## 2026-11-23 11:50 — study-designer/089 the-footer-band-is-measured-on-a-typst-page

**Decided:** nothing suite-wide. I split EMB-242 (filed by `api/171`'s worker) into this one docs-only task and announced it before dispatch. `embarch-study-designer/interfaces/hil-pdf.md`'s admitted footer run is now **8 to 16 mm** above the bottom edge, marked measured narrowly: `extract_pages` over one Typst 0.15.1 page with embarch-api's footer wrapper, one font set, A4, baseline 14.96 mm at 11 pt and just over 15 mm at 9 pt, citing `embarch-api` decision 123; Letter stays assumed. The status line and decision 91's *Assumed, not measured* list (`decisions/hil-shapes.md`) now name the footer band and the 0.3 `size` word gap as met once by a real page; the 0.5 line break, `TICK_TARGET` 5 and the 5 mm centring stay assumed. The reviewer judged "measured once" for the word gap slightly generous (it was met unchanged, not adjusted) and not a contradiction. **The `embarch-api` side is not done**: `src/verify_report.rs`'s comment above `FOOTER_BASE_MAX_MM`, decision 123's "on the edge of `hil-pdf.md`'s 8 to 15 mm band … (filed against the doc)" and `embarch-api/open.md`'s first bullet still say the shared doc disagrees; this fold rewrites `tasks/api/172`'s dispatch note to say 089 has landed and those three are to be made to agree there. EMB-242's `finish` moves it to Done after this push.
**Merged:** `agent/study-designer/089-the-footer-band-is-measured-on-a-typst-page` (doc only, no code branch; doc `cf5145d5` and `f7b6260f`, the worker's `8543c1a3` and `7341d8a0` cherry-picked onto `c1d2b942`). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The band rests on one font set on one machine, A4 only; a Letter page and a font outside the embedded set are unmeasured.
**Budget:** PROCEED at dispatch (5-hour 10%, weekly 1%, wave 6) and at this fold (5-hour 48%, weekly 3%, wave 6).
**Least sure about:** the worker's first commit wrote `done,` on the State line and fixed it in a second commit; I landed both rather than squash, so `cf5145d5` alone leaves `check-task-state.py` red, which matters only to a revert that picks one SHA without the other.

---

## 2026-11-23 11:49 — promptu/008 compact-promptu

**Decided:** nothing suite-wide. **I unparked this task myself**: its `Unparks when:` read "the owner records the rewrite's model and wait …, or EMB-197 lands, whichever is first", and EMB-197 (the chat's Promptu card) landed in `embarch-chat` `f79c167` on 2026-11-17, four hours after the park was filed; nothing in this queue watches another repo's `main`, so it sat parked with its condition met and its size debt due 2026-11-24. I set `In flux:` to `no` on `DOC-BUDGET.md`'s split-first rule (a verbatim split restates nothing) and told the worker to leave 9, 13, 24 and 42 in place, since those move with the owner's rewrite settlement. The worker moved decisions 22, 23 and 25 to 28 byte for byte into a new `embarch-promptu/decisions/questions.md` (4,034 B); `decisions/patterns.md` went from 11,138 to 7,568 of 12,288 B, out of reserve; the index row in `decisions.md` split in two. I checked the move line by line before merging (12 removed lines, none missing from the new file). **Does `spec.md` alone answer what someone needs to work on `embarch-promptu` today?** The worker says no: the rewrite's model and wait are still owed (`open.md`), and decisions 9, 13, 24 and 42 move with that answer; it did not read the rest of `spec.md` against the question, so the answer is about the unsettled half only. **Leg setup, to carry:** step 0 found no claim, no unit worktree and no leg worktree (the 18:37 leg ended clean on a HOLD); the leg worktree is fresh at `ab50139f`. Fleet Ready held EMB-242, which I split into `tasks/study-designer/089` and filed. Refill fired on depth (1 dispatchable, 1 scope); I read every `open.md`, the roadmap's Next (unchanged since 2026-10-29) and the reversals index (unchanged since 2026-11-11), and filed nothing new beyond 089: the open items are hardware-gated, the owner's call, or a trigger that has not fired. I added two stale-line fixes to `tasks/api/172`'s dispatch notes instead of filing them apart: decision 110's "`main.rs` does not yet" call `render_report` (noted by three reviewers, never filed), and the three `embarch-api` mentions of `hil-pdf.md`'s old 8 to 15 mm band, once `study-designer/089` lands. This unit also commits the 2026-11-22 day fold (11 units, 57,741 to 32,553 B), rolls 2026-11-20 into `log-archive/` (28,143 B left), and ran `check-client-names.py --suite --history`: clean on all 16 repos. `core/137`, `study-designer/089` and this task dispatched at 11:46.
**Merged:** `agent/promptu/008-compact-promptu` (doc only, no code branch; doc `044c117c`, fast-forward from `60e002f0`). Re-gated on the merge result: `check-docs.py` 12/12; ownership green on the branch; `check-doc-size.py --pressure` no longer lists the file.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED at the start (5-hour 10%, weekly 1%, the weekly window reset; wave 6) and at this fold (5-hour 48%, weekly 3%, wave 6). The 5-hour reading rose 38 points in about 15 minutes with three workers, a log folder and a reviewer running.
**Least sure about:** unparking a task on a condition in another repo that the park's filer named: if the owner meant "EMB-197 lands" to wait for its install in his window, not its commit, the split went a little early; it moved only decisions nothing marks as moving, so it costs nothing to undo.

---

## 2026-11-22 — 11 units

*Folded by leg 010's log-folder on 2026-11-23: per-unit narrative reasoning, gate transcripts and budget readings went; every SHA, reviewer line and hardware debt stayed. Detail is in git and in each unit's decision files.*

**Carry forward (the next leg cannot recover these):**
- **EMB-226 (`verify`) is fully landed** with `api/171`; `finish` moves it to Done after that push. EMB-225 and EMB-223 landed earlier in the day.
- **`api/172` (blocked on `core/137`) must compact `embarch-api/interfaces/publish.md`** (11,437 of 12,288 B, in reserve; `api/173` filed blocked, `In flux: yes`) and fix check 5's stale "`adopted` recomputed" cell (now check 6's). `core/137` (open) is dispatchable: Core takes a swept run's earlier files back, closing the one place publish departs from `notes/hil/06` (decision 117 records a refusal).
- **EMB-242** waits in Fleet Ready (study-designer): amend `hil-pdf.md`'s footer band 8 to 15 mm; the first Typst PDF measured 14.96 mm, check 4 uses 8 to 16 mm, A4 width assumed.
- **Open owner question (`api/170`)**: `verify` takes `--public-key`, not a fingerprint (118); whether Core should serve the key instead is unasked.
- **Stale, untouched**: decision 110's "`main.rs` does not call `render_report`" sentence in `embarch-api`.
- **Failure likely to recur**: do not chain a gate through `| tail`; at `umbrella/102` the fold went ahead on `tail`'s exit and `origin/main` was red from `c1b23b9b` to `c10ea59a`, about a minute.
- **Shared crate changed**: `study-designer/088` added the off-by-default `pdf-text` feature, turned on by `embarch-api`'s `pdf` feature only; `api/170` turned on `reducers` and `ed25519-dalek`; `api/167` added four `CoreClient` methods (consumers `embarch-ui`, `embarch-umbrella` built green).
- Leg worktree at `00c50d0b` found clean at 13:14 leg setup; the owner closed `tasks/doc/098` in `b671c249`.
- **Budget**: the weekly window sat at 87 to 93%; the last leg ended on a 5-hour HOLD at 18:37 (5-hour 82%, weekly 93%, resetting about 20:00), three units of four. Bench `api/059` and `dev-bench/038` stay `open`, neither board attached at the 18:09 refresh.
- **Never exercised against real things**: no real Core zip verified or published (M1.14's first real publish is the check); footer band and A4 width rest on this machine's Typst only; the `rate_check` tolerance and `by`/clock choices of `core/132` have met no real capture.
- Spread sweep line (the refill gate reads it): `Spread sweep: nothing filed (2026-11-22 13:05)`

---

### 18:37 api/171 verify-the-pdf-text-report-data-and-pictures
`embarch-api` decisions 122 to 125: check 9 is a whitelist over `report.typ`'s syntax tree and `publish` refuses by it too; check 4 reads the PDF via `pdf-text` and stays `partial` because `appendix.typ` literals are unsigned; check 6 recomputes `report-data.json` independently of Core (two copies that can drift, in `open.md`). Least sure: a number embarch-api wrote wrongly into `appendix.typ` passes as `partial`.
**Merged:** `agent/api/171-verify-the-pdf-text-report-data-and-pictures` (code `2804e41`, ff from `3acf3e1`; doc `b71a55cc`, worker's `81d777c4` cherry-picked onto `0492e7fc`). Gated green, 481 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. No real Core zip verified; footer band and A4 width untested beyond this machine's Typst; fonts outside the embedded set or a number wrapped across a table cell untested.

### 18:19 study-designer/088 the-pdf-text-extractor-and-number-grammar
Decisions 101 to 103: `pdf-text` feature (`lopdf` default-features off, own content-stream interpreter, `DEFAULT_GLYPH_WIDTH_EM = 0.5` assumed, 0.3 `size` word gap assumed). Set `tasks/api/171` open. Shared crate: manifest and `lib.rs` diff read, additive and `cfg`-gated. Least sure: `lopdf`'s dependency weight in embarch-api's binary is unmeasured.
**Merged:** `agent/study-designer/088-the-pdf-text-extractor-and-number-grammar` (code `1fe70b8`, ff from `d6230ad`; doc `750a7fa3`, worker's `8f293b4f` cherry-picked onto `9c08dd4b`). Gated green under every consumer feature set.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Extractor has read only ten hand-assembled fixtures; the 0.3 gap and 0.5 em fallback stay assumed until a Typst PDF runs through it.

### 18:15 api/170 verify-a-published-zip-offline
Decisions 118 to 121 (`verify` CLI-only, `--public-key`, unattested origin passes with words, exit 1 only on `FAIL`, check 2 always `partial`, check 8 to the signed head). Leg setup: the 13:01 leg died on a 5-hour 429, both branches pushed and landed here; refill on depth filed `core/137` (open) and `api/172` (blocked on it). Least sure: decision 121's `serde_json`-bytes hash read from Core's source, not its interface doc.
**Merged:** `agent/api/170-verify-a-published-zip-offline` (code `3acf3e1`, ff from `b274114`; doc `d16a2d58`, worker's `d5374fac` cherry-picked onto `48c6d000`). Gated green, 471 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. `verify` has read only a mock-Core zip re-signed in tests; DSSE statement and run-log entry shapes came from Core's source, not a real zip.

### 13:34 api/168 publish-lists-every-number-and-writes-revisions
Decisions 115 to 117 (`decisions/publish-revisions.md`): lexical number oracle, never refuses on a number; `--prose*` params; revisions `-r<N>`; **a republish after the retention sweep refuses** (departs from `notes/hil/06`, closed by `core/137`). `open.md` out of reserve; `api/169` closed done. I added `b274114` (`cfg_attr` dead_code allow for `--no-default-features`).
**Merged:** `agent/api/168-publish-lists-every-number-and-writes-revisions` (code `db2b7e8` and `b274114`, ff from `a1eda4b`; doc `7fce65bc`, ff from `728e089b`). Gated green, 470 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. No real Core, swept run or `report.typ` through the oracle; OCP T&V lines unvalidated against the schema.

### 13:14 core/136 serve-a-pending-revisions-run-files
Decision 116 amended: the files route serves the run's own files at the pending revision; closes EMB-241. I folded `api/167`'s fragment into embarch-api docs myself and messaged `api/168`'s worker to rebase. Spread sweep: nothing filed (2026-11-22 13:05).
**Merged:** `agent/core/136-serve-a-pending-revisions-run-files` (code `88aff23`, ff from `768c20f`; doc `4923ff44`, ff from `9cd74798`). Gated green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of `embarch-core`, unrun (a worktree cannot build natively). The route has met only Core's in-process HTTP test, never embarch-api's `publish` against a real Core; M1.14's first real publish is the check.

### 08:38 api/167 publish-a-study-run-as-one-zip
Split EMB-225 into this and `api/168`. Decisions 112 to 114: `[publish] folder` config, zip naming, call order, CSVs are Core's own renderings. Touched `embarch-core-client` and `Config` additively; `embarch-ui` and `embarch-umbrella` built green against it (build only, not tests). Worker found EMB-241 (split to `core/136`); filed `api/169`. Leg ended on a 5-hour HOLD (92%).
**Merged:** `agent/api/167-publish-a-study-run-as-one-zip` (code `a1eda4b`, ff from `2f7550d`; doc `2b09bc78`, ff from `7b3ef7eb`). Gated green, 457 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. `publish` has met a mock Core only; OCP T&V unvalidated; the `.csv` name for an `OutpostTrace` tap's rendering is unconfirmed.

### 08:16 core/135 cores-side-of-publish
Split EMB-223. `embarch-core` decisions 116 to 119: two publish routes plus a files route, `POST /study/{id}/adopt` (scope and SHA-256, no text), `log_head` tail anchor, `report-data.json` with no clock and two attestation labels. `open.md` compacted in-unit; `tasks/core/133` closed done; `tasks/doc/098` retired. Spread sweep: nothing filed (2026-11-22 08:16). Least sure: attestation labels are the worker's reading of `notes/hil/06`; `run_status` comes from the `clean` flag, not recomputed from `events.json`.
**Merged:** `agent/core/135-cores-side-of-publish` (code `768c20f`, ff from `f16a35b`; doc `a6f48f16`, ff from `ee123c83`). Gated green, 433 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). The publish files under `study_results/` have no `icacls` lockdown, and the `signing-key` and `run-log.jsonl` lockdowns are still unrun on Windows. No real study has been published, and no third-party DSSE verifier has read the manifest; the tests check DSSE v1 with code written from the spec.

### 03:23 umbrella/102 init-on-an-initialised-repo-installs-what-it-lacks
`embarch-umbrella` decision 60: `init` on an initialised repo exits `0` (was `1`), installs the skill and exclude lines it lacks, does not repair MCP registration. Exit-code change: no caller outside the suite was searched. The fold landed with `check-doc-size.py` red (see carry-forward), fixed as `c10ea59a`.
**Merged:** `agent/umbrella/102-init-on-an-initialised-repo-installs-what-it-lacks` (code `27f43a5`, ff from `b3d0106`; doc `55c42437`, worker's `df48ddd8` cherry-picked onto `bc418c8a`). Gated green, 280 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. Not run against a real initialised firmware repo; skill path `.claude/skills/<name>/SKILL.md` unconfirmed in a live session: run `embarch init` twice in a scratch repo and confirm the agent lists `embarch-hil`.

### 03:22 ui/112 the-study-designer-keeps-a-studys-measurements
`embarch-ui` decision 104: the Study Designer keeps `measurements` without authoring them; `apply_measurements` beside `build_authored`; refusals `400` prefixed `measurements: `. I corrected the code comments citing decision 31 to 104 (`b1b1a24`, comments only). Least sure: the summary line may hide that the study carries uneditable declarations.
**Merged:** `agent/ui/112-the-study-designer-keeps-a-studys-measurements` (code `a9d7e95`, ff from `279c33f`, then `b1b1a24`; doc `fdfa45e8`, worker's `24f6be14` cherry-picked onto `c9cf3216`). Gated green twice, 320 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The `app.js` change has no test or browser drive; no agent-written study opened and saved through the tab.

### 03:20 api/165 compact-api
Verbatim split, no wording changed: `decisions/client-crate.md` 12,278 to 9,360 B (decisions 55 and 66 to `client-crate-funnel.md`), `interfaces/config.md` 11,368 to 7,945 B (to `config-selection.md`). Least sure: `client-crate.md` is 85% full with 58, 62 and 72 pinned by `history/` citations; nothing files moving them. `spec.md` alone omits that the repo hosts `embarch-core-client` and its two token scopes.
**Merged:** `agent/api/165-compact-api` (doc only; doc `6b448201` and `569ca60a`, worker's `54adc7d4` and `d6a708ee` cherry-picked onto `9cb0f77e`). `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 03:19 core/132 measurements-at-a-studys-end
`embarch-core` decisions 113 to 115: Core computes declared measurements at a study's end into the signed `measurements.json`; points on `core_rx_utc_ms`; marker is the first word of a `Text`-tap line; `rate_check` tolerance `0.05 + 2/(n-1)` **[assumed]**; `declared_by` carries the token scope. Leg setup: the 22:33 leg died on a 5-hour 429; four workers ran as foreground calls and all reported. Skipped the spread sweep without a fresh marker (newest was `2026-11-18 23:20`). Also committed the 2026-11-21 fold, rolled 2026-11-19, `check-client-names.py --suite --history` clean on 16 repos. Least sure: `rate_check` tolerance and the `n/T` rate reading high by one interval in `n-1`.
**Merged:** `agent/core/132-measurements-at-a-studys-end` (code `f16a35b`, ff from `99a3e7c`; doc `b134f58f`, worker's `71505591` cherry-picked onto `38b28a75`). Gated green, 426 tests.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). No real study's captures have been reduced: run a study with a `rate` and an `interval` over a bench console, then read `measurements.json` for the arrival granularity and the rate tolerance (recorded in `embarch-core/open/never-exercised.md`). A `study_value` scope from a person token has never been seen end to end.

---
## 2026-11-21 — 11 units

*Folded by the 2026-11-22 leg: per-unit narrative, gate lists and budget lines went; SHAs, reviewer lines and hardware debts kept, one line per unit. `git log` holds the reasoning.*

**Carry forward:**
- **Suite-wide, by the supervisor, under the 17:10 announcement (`ts 1795306202`; no reply, window closed 17:40): host-type schema bump, `HOST_TYPE_SCHEMA_VERSION` 21 to 22, wire 15 unchanged** (`suite/057`: `Study.measurements`, up to 32 `MeasurementDecl`, always compiled, nothing skipped when empty because `Study` travels as postcard). **A deploy, the owner's:** Core, `embarch-api` (restart the MCP server) and `embarch-ui` refuse each other across 21 and 22 until all three are rebuilt from `main`; `embarch-umbrella` `doctor` check 11 warns until it is too. The running MCP binary is stale from this commit on.
- **Deploy order: Core first.** The next `embarch-ui` deploy does not start without a readable person token, which a Core from `core/128` on writes at first start. Core before UI.
- Filed or opened this day: `tasks/ui/112` (the UI save handler drops a study's declarations), `tasks/core/132` open (calls `validate_measurements` at submission, window time bounds, what a marker is), `tasks/umbrella/102` open (an already-`init`ed repo gets no skill; the workaround deletes the engineer's config), `tasks/api/165` open (compact `client-crate.md`, `interfaces/config.md`, due 2026-11-28), `tasks/core/133` blocked (compact `open.md`), EMB-238 (now `api/166`, landed), EMB-239 (now `core/134`, landed). Owed and unfiled: `plot_ticks` into the shared crate (best with M1.11, which must call the Rust one); whether `run_host_study` takes an optional `project`; a missing-person-token banner in the UI.
- `fold-commit.py` does not stage `notes/` (already recorded 2026-11-20); the `api/164` fold's `notes/hil/06` edit landed apart as `dc7b3757`.
- Two decisions to remember: `embarch-core` decision 112, the first refusal by scope (the agent's token gets `403` discarding a failed, errored, inconclusive or published run's captures), proven so far only in Core's own tests; `POST /auth/challenge` takes no token and sits outside decision 42's route sweep. Signed-challenge step before a client sends any token (Core decision 110's route) is in no task; name it when M1.10 is split.
- Spread sweep, carried verbatim for the refill skip: `Spread sweep: nothing filed (2026-11-18 23:20)`. A later sweep this day (17:32 and 22:14 units) read only `embarch-api/open.md`, `embarch-core/open.md` and `embarch-token.md` since it, and filed `umbrella/101`, then `umbrella/102`.
- Recovery: the 17:01 leg died on a 5-hour 429 at about 17:38 before `fold-commit.py`; the 22:05 unit finished its dirty worktree. A leg that dies between merging code and folding docs leaves `history/` and `features.md` behind the shipped binary.
- Workers: foreground `Agent` calls in one message run concurrently and each reports to its own leg (EMB-214's pattern); background calls (22:08) also reported to this leg.

### Units

**suite/057 a-study-declares-its-derived-measurements (22:31)**
**Merged:** `agent/suite/057-a-study-declares-its-derived-measurements`, §8 order: `embarch-study-designer` `d6230ad` (ff from `1238def`), `embarch-core` `99a3e7c` (ff from `9a9d31a`), `embarch-api` `2f7550d` (ff from `069e892`); doc `9e5e5301` (`e4de7d76` cherry-picked onto `af0b4e7e`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** **a deploy, the owner's**: Core, `embarch-api` (restart the MCP server) and `embarch-ui` refuse each other across 21 and 22 until all three are rebuilt from the new `main`, and `embarch-umbrella`'s `doctor` check 11 warns until it is too. The running MCP binary is stale from this commit on. No board needed.
**Least sure about:** declaring values per measurement rather than per tap lets two declarations over one tap state different sample rates; nothing refuses the disagreement (`core/132` reports each `rate_check` separately).

**api/166 send-build-claims-when-a-study-starts (22:20)**
**Merged:** `agent/api/166-send-build-claims-when-a-study-starts`, code `069e892` (ff from `b2afdf5`); doc `9d20f924` (`e221d851` cherry-picked onto `1322a2eb`). `embarch-api` decision 111; `build_dirty` ignores untracked files.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The MCP `run_study` path is untested end to end (no harness drives the MCP subprocess; it shares `build_claims::for_project` with the CLI, which is tested against a mock Core), and nothing has sent a claim to a real Core.

**core/134 retention-holds-when-the-run-log-cannot-be-read (22:14)**
**Merged:** `agent/core/134-retention-holds-when-the-run-log-cannot-be-read`, code `9a9d31a` (ff from `c3414e4`); doc `d4b39eaf` (`5fd3437b` cherry-picked onto `0daa1ff6`). Leg setup claim `1822a2eb`. `GET /studies` answers `keep: 0` on an unreadable log, the opposite of what retention does; the UI does not read `keep`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build, unrun (a worktree cannot build natively). No board needed. The `error` log line itself is not asserted by a test (no log-capture crate in `embarch-core`).

**umbrella/101 init-installs-the-hil-skill (22:05, recovery fold)**
**Merged:** `agent/umbrella/101-init-installs-the-hil-skill`, code `b3d0106` (ff from `ed5d14b`, landed by the 17:01 leg); doc `7ca69785` (`305c0c0c` cherry-picked onto `2d8d5f1a`). `tasks/umbrella/099` closed `done`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. The skill path `.claude/skills/<name>/SKILL.md` is `[assumed]` and has not been loaded in a live Claude Code session: run `embarch init` in a scratch repo and confirm the agent lists `embarch-hil`.

**ui/111 ui-calls-core-with-the-person-token (17:37)**
**Merged:** `agent/ui/111-ui-calls-core-with-the-person-token`, code `279c33f` (ff from `d824791`); doc `4cca5341` (`f38d3517` cherry-picked onto `dc6dabeb`); note edit `dc7b3757`. No fallback to the agent's token; the UI stops at start naming the token's sources (worker's departure from the task, accepted).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none on a board. **A deploy ordering debt**: the next `embarch-ui` deploy does not start unless the UI can read a person token, which a Core from `core/128` on writes at its first start; deploy Core first. Not run against the installed `embarch-ui.service` or a real Core, and the missing-token test passes without checking the error on a machine that has a `person-token` file.

**api/164 render-a-report-to-pdf-offline (17:35)**
**Merged:** `agent/api/164-render-a-report-to-pdf-offline`, code `b2afdf5` (ff from `c9f0c79`); doc `9fa11640` (`1676e029` cherry-picked onto `4567439a`). Typst behind cargo feature `pdf`, default on; release binary 21.5 MB to 84.3 MB; `embarch-study-designer` decision 91 amended.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** byte identity across machines unmeasured, and `verify` (M1.11) rests on it; nothing schedules a second-machine render.

**core/131 hash-chained-run-log (17:32)**
**Merged:** `agent/core/131-hash-chained-run-log`, code `c3414e4` (ff from `4f5dcc4`); doc `13a86f36` (`a9ceacf8` cherry-picked onto `fbc0af1a`). `embarch-core` decisions 111 and 112; `tasks/core/130` closed `done`; `suite/057` announced at 17:10.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `run-log.jsonl`, unrun (a worktree cannot build natively). No board needed.

**api/162 core-client-resolves-both-token-scopes (12:41)**
**Merged:** `agent/api/162-core-client-resolves-both-token-scopes`, code `c9f0c79` (ff from `97577b6`); doc `b407e472` (`21f92513` cherry-picked onto `0eacb879`). `embarch-api` decision 109; no CLI flag selects the person scope.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The WSL2 `person-token` path has not met a live Core.

**study-designer/086 hil-verdict-rules (12:38)**
**Merged:** `agent/study-designer/086-hil-verdict-rules`, code `1238def` (ff from `17332cf`); doc `5d512fb4` (ff from `e559e851`). Decisions 95 to 98; `tasks/study-designer/087` paid and closed `done`. Decisions 97 and 98 meet real data first in the Test phase; a disagreeing reading costs a behaviour version.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**core/129 sign-study-run-records (12:27)**
**Merged:** `agent/core/129-sign-study-run-records`, code `4f5dcc4` (ff from `789cbfc`); doc `f85141d6` (`4ebfeb1e` cherry-picked onto `c75b26a2`). `embarch-core` decision 110, Ed25519 (`ed25519-dalek` 2); the declarations ledger is in memory, so a record after a Core restart vouches only from `witnessed_since_utc_ms` until M1.6's store persists it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build and the `icacls` lockdown on `signing-key`, unrun (a worktree cannot build natively); the task's closing note, now in `embarch-core/open.md`, says how to check both from the main checkout on Windows, and that a second start must reuse the key. No board needed.

**study-designer/085 hil-reducers (12:25)**
**Merged:** `agent/study-designer/085-hil-reducers`, code `17332cf` (ff from `f6cca94`); doc `ffe5c599` (ff from `731d60a0`). Decisions 92 to 94; the percentile's type-A convention is unmeasured. Also committed the 2026-11-20 fold; `check-client-names.py --suite --history` clean on all 16 repos. Spread of the HIL M1 issues in Fleet Ready (`d7ae8e5b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Bench `api/059` and `dev-bench/038` stay `open`: neither `dev-bench` nor `dut` attached at the 12:06 refresh.
*Days 2026-11-20 to 2026-11-20 rolled to [log-archive/supervisor-log-2026-11-20-to-2026-11-20.md](log-archive/supervisor-log-2026-11-20-to-2026-11-20.md).*
