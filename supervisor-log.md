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

## 2026-11-17 14:37 — atlas/068 a-shared-datasheet-library-and-a-copy-of-each-file-used

**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). Builds the owner's 2026-11-17 decision in `DESIGN.md` "Where documents come from" (EMB-198): optional `[project] library` in `atlas.toml` (unset is byte-for-byte today's behaviour; a set folder that does not exist is an error); `src/embarch_atlas/library.py` scans it and admits a file to the manifest only when tied to a board part, the MCU role, a confirmation or a `[[boards]] pdf`, marked `library: true` (not the issue's `origin = "library"`, which already holds the Zone.Identifier host); `inventory/library-index.json` stops re-hashing; `doc prep`, `schematic` and `inventory` (for earlier-prepped docs) copy what they read to `<atlas>/files/<sha256>/<name>` and `doc.json` `path` names the copy; never a write into the library, never the network. One existing test changed to expect the copy. At the fold I added a "Left open" sentence to `embarch-doc/embarch-atlas/design.md` so the follow-ups outlive the retired task file.
**Merged:** `agent/atlas/068-a-shared-datasheet-library-and-a-copy-of-each-file-used` (code `90f70f2`, ff on `c63849c`; doc `3b7f50c7`, cherry-picked onto `899528ad`). `pytest` 856 passed, 3 skipped (env-gated; `test_public_guard` ran), client names clean, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** no test drives the schematic ingest's copy or a library-only board PDF (no synthetic Smart PDF exists); a schematic's `source_file` still names the original; `join` and `build` do not refresh the manifest, so a library file is tied only at the next `inventory` or `missing`. **Owed, owner-side:** a first real run with a library set; skills reach sessions only after a re-install (`atlas-translate-docs` changed).
**Budget:** PROCEED in burndown, 5-hour 63%, weekly 45% at leg start.
**Least sure about:** whether `missing` re-running `inventory` whenever a library is set is cheap enough on a large library; the index is meant to make it so and only a synthetic test measures it.

---

## 2026-11-17 14:35 — promptu/007 rewrite-the-rough-prompt-and-log-the-original

**Decided:** nothing numbered (burndown). Builds owner decision 42 (EMB-196): `promptu render` makes one rewrite call after the structured render and the rewrite is the draft; footer gains `rewritten=yes`; a brief, a run with no pattern, an offline run and `rewrite = "off"` are not rewritten; a failed call falls back to the verbatim render and records `rewrite_skipped` in the log. Log: `<state>/log/<run>.json`, never pruned (original, rendered, model, effort, `rewrite_ms`, `wait_ms`). Read-back verb for EMB-197: **`promptu original <run> [--json]`** (stdout the original as typed, exit 2 for no entry), contract §8.4 to §8.6 and `interfaces.md`. `promptu stats` prints p50/p95. Settings `rewrite_model` (default `sonnet`, as decision 9's pass), `rewrite_effort` (`low`), `rewrite_timeout_s` (30); the choice stays open in `open.md`. "Amended by 42" pointers added to decisions 13 and 14. At the fold I repointed `tasks/promptu/008`'s `Unparks when:` and an `open.md` line from the retiring task file to `open.md`.
**Merged:** `agent/promptu/007-rewrite-the-rough-prompt-and-log-the-original` (code `946207b`, ff on `e8b58c7`; doc `9621d6f0`, cherry-picked onto `8a6f8d5b`). `cargo test` 121 passed (71, 18, 32), clippy green, client names clean, `check-docs.py` 12/12. desk/030's doc landed as `5c9e44c8` (fold `8a6f8d5b`), not the `1ce40c48` its entry names: the owner pushed `b671c249` and `fb0ac2eb` (doc/098, desk decision 87) mid-fold and the leg rebased.
**Blocked:** nothing. The worker filed size debt `tasks/promptu/008-compact-promptu.md`, `blocked`, `In flux: yes` (`decisions/patterns.md` 11,138 of 12,288 B, due 2026-11-24); it unparks when the owner settles model and wait, or EMB-197 lands.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** ten real `/promptu` prompts, then `promptu stats`, to pick the rewrite model and the acceptable wait; the rewrite has only met a fake `claude`, and the plugin is not reinstalled. The weekly loop (step 4) is unbuilt, so "edits compared against the rewrite" is a contract (the log's `rendered`), not running code.
**Budget:** PROCEED in burndown, 5-hour 63%, weekly 45% at leg start.
**Least sure about:** whether a never-pruned per-run log holding every original prompt verbatim needs a retention rule; no decision covers it and the reviewer found none either.

---

## 2026-11-17 14:31 — desk/030 compact-desk

**Decided:** nothing. Verbatim move: `embarch-desk/spec.md` §5 ("What it deliberately does not do") to `embarch-desk/spec/non-goals.md`, with a one-line pointer; one link rewritten for the new depth (`decisions.md` to `../decisions.md`). At the fold I reworded the pointer's "no in-desk Linear writes" to the moved bullet's own words (comments, issue creation, PR review or merge), since the desk does write to Linear (decision 30's status moves and Send). Worker's answer to the human question: yes, `spec.md` alone still answers what someone needs today. `spec.md` 9,168 to about 8,700 B, out of reserve.
**Merged:** `agent/desk/030-compact-desk` (doc only, `1ce40c48`, fast-forward over `b3028c0f`; no code branch). `check-docs.py` 12/12 green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00), 5-hour 63%, weekly 45%, suggested wave 6; 4 dispatched, one per unit. Leg began at `56d15c36` (fleet `de21520`); split commit `59649796` ( atlas/068 from EMB-198, promptu/007 from EMB-196, chat/028 from EMB-189) and four claim commits. Fleet Ready now 32 unsplit; EMB-197 waits for promptu/007's read-back verb.
**Least sure about:** whether the worker's "byte-identical" box should have been ticked with a rewritten link; the reviewer read it as correct for a move one directory deeper.

---

## 2026-11-17 14:21 — atlas/067 worktree-sessions-find-the-main-clones-atlas

**Decided:** nothing numbered. EMB-90, the issue's direction kept: `common.atlas_dir()` takes `--atlas-dir` first, the worktree's own `embarch/atlas` second, then the main clone's (`common.main_clone_atlas`: git common dir named `.git` and not the toplevel itself, folder exists); every CLI and MCP entry point and `build.resolve_atlas_dir`'s default use it. `skills/atlas-use/SKILL.md` gained an "In a git worktree" section and a wider trigger; `DESIGN.md` "How a session sees the atlas" gives the lookup order. Left as is: `CLAUDE.local.md`'s `@embarch/atlas/MAP.md` import still does not resolve in a worktree; the skill tells the session to read the main clone's MAP.
**Merged:** `agent/atlas/067-worktree-sessions-find-the-main-clones-atlas` (code `c63849c`, ff on `ce0c899`; doc `a984cfb2`, cherry-picked onto `f4ae7c4a`). `pytest` 844 passed, 3 skipped (env-gated: real west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `install.py` copies skills into `~/.claude/skills/`, so sessions see the new `atlas-use` trigger only after a re-install from an updated checkout.
**Budget:** PROCEED in burndown at start (5-hour 57%, weekly 45%) and end (5-hour 63%, weekly 45%); suggested wave 6. Leg close: 4 of 4 units, all the dead 13:38 leg's dispatches; nothing new dispatched or split. Fleet Ready holds 35 unsplit issues, so `queue-status.py` reads 36 dispatchable (those plus `tasks/desk/030`, size debt due 2026-11-24); no refill sweep ran, since the next leg has more to split than it can dispatch. `doc/098` (owner-only, `DOC-CONVENTIONS.md`) falls due today.
**Least sure about:** whether the `@embarch/atlas/MAP.md` import failing silently in a worktree still leaves a session that never invokes the skill grepping PDFs; the fix reaches the skill and the CLI, not the import.

---

## 2026-11-17 14:20 — promptu/006 count-tool-calls-and-result-characters-per-subagent

**Decided:** nothing. EMB-149: `promptu calls <session> [--subagent <id>] [--class <name>] [--json]`, read-only, per thread (main and each subagent with its `meta.json` description) and per class (`git`, `build`, `config`, `source`, `other`), the class rules one table in `src/calls.rs` `classify`, pinned by a test; contract §12. No withheld decision.
**Merged:** `agent/promptu/006-count-tool-calls-and-result-characters-per-subagent` (code `e8b58c7`, ff on `95f0d69`; doc `9fd7c031`, cherry-picked onto `2b01ca82`). `cargo test --all-targets` 115 passed (69, 18, 28), clippy green, client names clean.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. A comment in `src/main.rs` cites the new contract section as §9 where the heading is §12; a typo, left for the next promptu unit to touch that file.
**Budget:** PROCEED in burndown, 5-hour 57%, weekly 45% at leg start.
**Least sure about:** whether the worker reused `src/used.rs`'s transcript walker as the task asked; `src/calls.rs` is 300 new lines and I did not read it for that.

---

## 2026-11-17 14:18 — desk/029 a-key-from-the-opening-prompt-must-name-a-real-issue

**Decided:** nothing numbered (burndown). The worker found the premise half stale: `ensure_item` already refused a key with no card by a 404 (EMB-9); the card-exists path skips the lookup, correctly. Now `adopt_key` names the workspaces asked in the 404, Linear failing to answer stays a 502 that adopts nothing, and the skill, MCP instructions, two tool replies and the hook text say the desk checks. **Withheld decision filed: EMB-199** (Backlog, `Type: decision`): the unreachable-Linear and mixed-answer refusal. The reviewer's loose end, decision 7's sentence in `decisions/cockpit.md` that no longer describes the code, is a Finding comment on EMB-199.
**Merged:** `agent/desk/029-a-key-from-the-opening-prompt-must-name-a-real-issue` (code `59691f7`, ff on `02f9f5a`; doc `af948af6`, cherry-picked onto `a765bb6a`). `cargo test` 264 passed, clippy green, client names clean. The worker filed size debt `tasks/desk/030-compact-desk.md` (`embarch-desk/spec.md` 9,168 of 10,240 B, due 2026-11-24, `open`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `plugin/skills/desk/SKILL.md` changed, so the installed plugin needs a `plugin.json` version bump and push before sessions see the new text; plus the desk's own redeploy for the server change.
**Budget:** PROCEED in burndown, 5-hour 57%, weekly 45% at leg start.
**Least sure about:** what a session does with the 502 during a Linear outage, retry or fall back to `untracked`; nothing in the tool text tells it which.

---

## 2026-11-17 14:17 — chat/027 compact-chat

**Recovery, read first.** The 13:38 leg claimed and dispatched `chat/027`, `desk/029`, `promptu/006` and `atlas/067`, then was cut short by the harness at about 13:44: no `leg-end`, no entry, nothing landed. All four workers finished and pushed both branches. This leg waited out its lock (stale at 14:14, per `leg-start`'s rule), took it, and lands those four as its own four units; it dispatches nothing new. The 2026-11-14 day fold and the 2026-11-12 roll that leg's log-folder left uncommitted ride in this commit. Client-name history scan (`--suite --history`): all 16 repos clean. Those four dispatches predate this leg's `leg-start`, so this leg ticks no `leg-reported` for them.
**Decided:** nothing. Verbatim moves only: decisions 94 and 54 to a new group file `embarch-chat/decisions/rail.md`; the desk-calls table to `interfaces/desk.md`; "Structural limits" to `open/limits.md`; the handoff bullet and three input invariants to `spec/handoff.md` and `spec/input.md`. Decision 109's lines untouched. Worker's answer to the human question: yes, `spec.md` alone still answers what someone needs today; the moved parts are one hop away behind pointers.
**Merged:** `agent/chat/027-compact-chat` (doc only, `a5f8c1e3`, fast-forward over `d87f81a1`; no code branch). All four files out of reserve; `check-docs.py` 12/12 green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00), 5-hour 57%, weekly 45%, suggested wave 6; this leg runs no wave.
**Least sure about:** whether a leg that waits out a dead predecessor's lock should also tick `leg-reported` for that predecessor's dispatches; `leg-start` resets the count, so I did not.

---

## 2026-11-14 — 7 units (4 unit entries, 3 leg-level zero-unit entries)

*Folded 2026-11-17 by an `embarch-log-folder` agent for the supervisor leg: per-unit narrative reasoning, gate-run detail, budget readings and leg-close boilerplate dropped; git holds them. Kept: every SHA, every Reviewer line, every Hardware debts line, the open dream asks with their `ts`, and what the next leg cannot recover.*

**Open at end of day (carry forward):**
- **Dream asks unanswered, three in a row** (2026-11-13 13:58, 11:40, 17:46, 23:57). The newest, **`ts` `1794725821.199969`** (`crystal_ball`, `--action`, posted 23:57): (1) plug in the bench for `api/059` and `dev-bench/038`; (2) approve one read of Claude Code's hook documentation so a `promptu` unit can record the unmeasured parts of `embarch-promptu`'s hook contract §3.9, a yes approving the web fetch; (3) owner greps his real configs for `artifact_path_for_core`, and if none carries it one `api` unit refuses it by name (`embarch-api/open.md`, decision 64). Thread also carries EMB-159, EMB-160, the `no_std` CI cell, the PD shields' connector kinds and `doc/098`'s due date.
- Earlier asks this day, superseded by the 23:57 one: **`ts` `1794681603.529909`** (11:40: bench; read UM2891/SNK1M1 to correct the PD shields' connector kinds in `embarch-ui/open/bench.md`, a yes approving that web lookup; keep or drop `embarch-study-designer`'s `no_std` CI cell) and **`ts` `1794703571.384789`** (17:46: bench; move EMB-160 to Fleet Ready; the `no_std` cell). The 6-hour gate holds new spawns into an empty queue until about 05:57 on 2026-11-15.
- **EMB-183** (Backlog, `Scope: fleet`, `--from audit`): an unanswered dream re-pages every 6 hours over unchanged sources, against `ops.md` §7's "asks, once". A rule question, the owner's; nothing changed about how dreams are made beyond the new proposals.
- **Queue:** zero dispatchable; bench `api/059`, `dev-bench/038` (neither `dev-bench` nor `dut` attached through 23:54); hw-gated `core/119`, `dev-bench/039`; owner-only `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17); four blocked. Refill sources re-read in full at 11:38 and 23:5x (all 162 questions, roadmap, reversals): everything left is hardware-gated, owner-only, an owner fork, trigger-gated or recorded as not-work. Spread sweeps filed nothing.
- **Budget:** 5-hour window climbed 23% to 60% in about twenty minutes during the unit leg (66% at 11:37); weekly 56% (resets about 20:00 on 2026-11-15). Watch the 90% HOLD.
- **Fold owed:** the first leg to run a unit on 2026-11-15 would have folded this day and run the client-name history scan.
- **Owed by the owner:** first real `scripts/replay.py` run (atlas/066); a real worktree-session build (api/155); deploy debts from earlier legs (the desk, decision 85 plus a plugin version bump; the UI service, decision 102; Core per `embarch-dev-workflow.md` §4a).
- **Decision made on the owner's behalf-ish:** `embarch-api` decision 106 (worker's): a worktree that lacks a project's `source_path` refuses startup for the whole server, loud over wrong; the reviewer noted it applies to every CLI subcommand that loads a config, a wider blast radius than the wording says.
- Remote branches `agent/api/155-*` (both repos) and `agent/atlas/066-*` (`embarch-atlas`) were the usual one-fold lag; `agent/ui/059-diff-new-lines-republish` on `embarch-doc`'s origin, older, left alone.

### Units (leg began at `b69b1db2`, fleet `6df0c08`; 4 of 4 from Fleet Ready; ownership OK)

**api/154 (11:20), which tree a worktree session's build builds.** EMB-128 answered by a run: `west` runs in the config's `source_path` verbatim, so a worktree session builds the main clone. Bug EMB-181 filed by the worker. Reviewer finding EMB-182 (a "never" invariant worded in `spec.md`) fixed by my reword at the fold, before the doc half reached `main`; EMB-182's task `tasks/api/156` was filed `done` at its split and retired at the api/155 fold. Split commits: `api/154` `8e4dd179`; `atlas/065` and `atlas/066` `1b7b0aad`.
**Merged:** `agent/api/154-which-tree-a-worktree-session-build-builds` (code `4707020`, ff on `d97985f`; doc `12670bf9`, cherry-picked onto `c80b45ee`, plus the reword). `cargo test` 402 passed.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-182
**Hardware debts:** none.
**Least sure about:** whether a worktree's `settings.local.json` `env` reaches the MCP server process; desk side, so EMB-181's fix may need a desk half.

**atlas/065 (11:23), schematic writes its extraction issues to a readable file.** EMB-179: `boards/<label>/issues.md`, named in `MAP.md`; `smartpdf.classify_issue` is pattern-based, so a reworded extractor message falls to `other` silently. A board extracted before the change gets the file only on re-run (recorded debt, not a contradiction).
**Merged:** `agent/atlas/065-schematic-writes-its-issues-to-a-readable-file` (code `ceb64ac`, ff on `d0c2f12`; doc `f293ce41`, cherry-picked onto `e9120d26`). `pytest` 829 passed, 3 skipped.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

**atlas/066 (11:31), a replay harness for atlas lookups against recorded sessions.** EMB-148: `scripts/replay.py`, script only because it reads private transcripts; a recorded command is parsed, never run (`grep` and `diff` only, read by me).
**Merged:** `agent/atlas/066-a-replay-harness-for-atlas-lookups` (code `1e6a07b`, ff on `ceb64ac`; doc `7b25c952`, cherry-picked onto `51893a2d`). `pytest` 836 passed, 3 skipped (env-gated).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the first real `scripts/replay.py --project <name> --atlas-dir <atlas> --build-dir <build> --report`; the parsers are narrow and may match fewer calls than atlas task 003's throwaway script.
**Least sure about:** whether `q config --build` writes into the build dir during a replay; neither code nor `DESIGN.md` says and the byte-identical test may not cover it.

**api/155 (11:33), a worktree session's build builds that worktree, or refuses.** EMB-181: decision 106 (above); `src/worktree.rs` rebases `source_path` and `build_dir_root` (`worktree-<dir>-<8 hex FNV-1a>`); `api/154`'s pinning test deleted; `embarch-ui` not built.
**Merged:** `agent/api/155-a-worktree-session-build-builds-the-worktree` (code `54d4035`, ff on `4707020`; doc `1ddd14b6`, cherry-picked onto `0188da88`). `cargo test` 404 passed, clippy green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none for a board. **Owed, owner-side:** a real build asked from a Start work worktree session, to see it take the worktree's tree and its own build directory; unit tests only so far. It depends on the MCP server's working directory being the worktree, which is `embarch-desk`'s side and was not assumed.

### Leg-level entries (zero units, no Reviewer line by design)

- **11:41**, after api/155: `embarch-doc` `main` `86233fd0` (fleet `7ecf19c`). Dreamed (`ts` `1794681603.529909`). Detail's "queue at 11:45" / "attached at 11:40" were both readings from about 11:38. **Merged:** nothing. **Blocked:** nothing. **Hardware debts:** none new; `api/059` and `dev-bench/038` stay open, neither role attached at 11:38.
- **17:47**, third dream (`ts` `1794703571.384789`; fleet `d9160f6`): not re-read, no commit since 11:38. **Merged:** nothing. **Blocked:** nothing. **Hardware debts:** none new; benches unchanged at 17:45.
- **23:58**, fourth dream (`ts` `1794725821.199969`; fleet `040da0e`): full re-read since `--refill-owed` fired on depth; `main` still `86233fd0`. Least sure: whether a docs read suffices for the owner to settle the hook contract points, or he wants each observed in a real session. **Merged:** nothing. **Blocked:** nothing. **Hardware debts:** none new; benches unchanged at 23:54.
## 2026-11-13 — 8 units

*Folded by an embarch-log-folder agent on 2026-11-14 (leg fold). Dropped: per-unit narrative reasoning, gate transcripts and worker-answer commentary; git holds them. Kept: every SHA, every Reviewer line, every hardware-debt line, and what the next leg cannot recover.*

**Carry forward (read first):**
- **Dream open:** posted 13:58:12 (`ts` `1794603492.409399`, `crystal_ball`), three proposals (plug in the bench for `api/059` and `dev-bench/038`; move EMB-160 and EMB-159 to Fleet Ready). Owner has not answered; the 6-hour dream gate holds until about 20:00. No second dream was posted by the 14:02 leg.
- **EMB-175 (Backlog, `Scope: fleet`):** `fleet-read.py --leg-gate` counts the queue in the owner's `CONF.doc_repo` checkout without a fetch, and legs push from a detached worktree, so the checkout was stale (`90ffd7fa`) and read landed tasks as 2 dispatchable, returning SPAWN before the dream check. Until fixed, a leg that lands the last open tasks and then dreams is followed by one empty leg. Filed `--from audit` to Backlog deliberately (Fleet Ready counts in the same gate). Unproven whether it explains all three of `tasks/doc/096`'s earlier post-dream spawns.
- **Unnamed flaky atlas test:** one atlas test failed once at `atlas/063`'s gate (824 passed, 1 failed) and passed alone; its name was lost. If it recurs, run `pytest -q -rf` the first time.
- **Budget:** 5-hour window 8% at 13:22 to 86% at 14:02 (resets about 16:10), weekly 38% to 44%; the next spawn is likely to meet the 90% HOLD.
- **Queue left:** zero dispatchable; bench `api/059`, `dev-bench/038` (no role attached at 14:01); hw-gated `core/119`, `dev-bench/039`; owner-only `doc/098` (`DOC-CONVENTIONS.md`, due 2026-11-17); four blocked. Both compactions (`api/150`, `core/126`) landed, so no size debt besides `doc/098`.
- **Deploy debts owed by the owner, unchanged:** the desk (decision 85 plus a plugin version bump), the UI service (decision 102), Core per `embarch-dev-workflow.md` §4a.
- **Open owner questions / leftovers:** the other copy of the R3.2 patch outside the suite is untouched (`embarch-dev-bench/open.md`); remote branch `agent/ui/059-diff-new-lines-republish` still on `embarch-doc`'s origin, left alone. Reusable trick: `west update --path-cache` from the main checkout's `native_sim` workspace makes a fresh pd-bench workspace a few minutes (2.7 GB per unit worktree).
- **Recovery done:** the 2026-11-12 20:04 leg died mid-fold; I reset its leg worktree to `origin/main` and landed `api/152` and `atlas/063` as ordinary units (063's code `3f3d77c` was already on atlas main). Day fold of 2026-11-12 and roll of 2026-11-10 to `log-archive/` done at 13:26. Client-name history scan: all 16 repos clean.
- **Decisions:** none numbered all day. `atlas/064` recorded a design choice in `embarch-atlas/design.md` (a cross-document page cite contributes to no frozen set; accepted cost: a change to the other document's page no longer thaws the unit). Fleet `cb2b4df` at the first leg, `ed64e0f` at the later two; no `suite` task, nothing deployed; the dream was the only alert sent.

### 14:02 — leg after dev-bench/047: no units, queue empty, spawned past a standing dream
Zero units; a leg-level entry, so no unit Reviewer line (no unit ran). `embarch-doc` `main` stayed at `b69b1db2`. Depth sweep was a diff, not a re-read (only `api/150`, `core/126`, `atlas/064` design section since 13:38); nothing filed.
**Merged:** nothing.
**Blocked:** nothing.
**Hardware debts:** none new. Bench `api/059` and `dev-bench/038` stay `open`: Core reachable, neither `dev-bench` nor `dut` attached at 14:01 (`fleet-hardware.py --refresh`).
**Least sure about:** whether EMB-175 explains all three earlier post-dream spawns.

### 13:57 — dev-bench/047 the carried R3.2 patch's usbc_pd.h includes zephyr/toolchain.h
EMB-147, toolchain unit run by the leg's own hands: `usbc-pd-r32.patch` gained one hunk adding `#include <zephyr/toolchain.h>`; patch edited by hand, post-image blob id `273904975c1`, `patches.yml` sha256sum updated, `pd_logic.h` workaround dropped. Red first, then 13 of 13 on `native_sim`, both shields built.
**Merged:** `agent/dev-bench/047-usbc-pd-header-compiles-on-its-own` (code `0aaf5d6`, ff on `50579d3`; doc `dc24b67c`; later fold `b69b1db2`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; both shield builds are build-only, as decision 59 has it.

### 13:51 — core/126 core's open.md split by mission
Verbatim split: seven `## Never exercised` bullets moved to `embarch-core/open/never-exercised.md`; `open.md` 4,314 to about 2,670 B.
**Merged:** `agent/core/126-compact-core` (doc only: `cd20175e`, cherry-picked onto `1d2af482`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.

### 13:50 — api/150 split api's open.md by mission
Verbatim split: seven verification-debt bullets moved to `embarch-api/open/bench-verification.md`; `open.md` 4,502 to 3,076 B.
**Merged:** `agent/api/150-compact-api` (doc only: `e1c6b57f`, ff on the claim `afd23f2b`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the moved bullets carry the existing ones unchanged.
**Least sure about:** I did not read `spec.md` to judge the worker's compaction answer.

### 13:45 — api/153 test scratch directories named from a counter, not the clock
EMB-169: `support::unique_dir(tag)` (pid plus `AtomicUsize`) used by ten clock-named test files; `src/main.rs` got an inline counter. 500 loaded runs, 0 failures; 401 passed on the merge result.
**Merged:** `agent/api/153-test-scratch-dirs-named-from-the-clock` (code `d97985f`, ff on `af2ea2b`; doc `82c27cda`, cherry-picked onto `94d7a010`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** the `src/main.rs` counter had no load run of its own.

### 13:40 — atlas/064 freeze leaves a cite of another document out of the citing document's pages
EMB-109: a cross-document page cite contributes to no frozen set; `check.find_sibling` now shared with `freeze.own_cited_pages()`. `pytest -q` 826 passed, 3 skipped.
**Merged:** `agent/atlas/064-freeze-files-a-cross-document-cite-under-its-own-document` (code `d0c2f12`, ff on `3f3d77c`; doc `57d06376`, cherry-picked onto `893d0440`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** whether "none" is what the issue's author wanted; a unit resting on a changed page of another document now stays frozen silently.

### 13:39 — atlas/063 check K holds a record to the group its cond names
EMB-113: check K picks a record's table group by the condition its `cond` names; an unmatched `cond` is reported (`K_cond: unmatched`). Gate: 824 passed, 1 failed (flake, name lost, see carry-forward). Spread sweep since the `2026-11-09 17:34` marker: nothing filed (13:38).
**Merged:** `agent/atlas/063-check-k-holds-a-record-to-its-conditions-group` (code `3f3d77c`, ff on `78fe5b4`, landed by the 2026-11-12 20:04 leg before it died; doc `d31ba2ec`, cherry-picked onto `4eedc6ad`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.

### 13:26 — api/152 CLI tests fail when cargo test runs from outside the repo
EMB-158: `EMBARCH_REQUIRE_LEASE=1` leaked into five subprocess tests; `support::api_command` calls `env_remove` on it. Not the same bug as EMB-169. Gate run with the variable exported: 401 passed.
**Merged:** `agent/api/152-cli-tests-fail-from-outside-the-repo` (code `af2ea2b`, ff on `e4957c5`; doc `8cbd3642`, cherry-picked onto `5914a007`). Recovered from the 2026-11-12 20:04 leg, which had pushed both branches; that leg's `core/126` split of EMB-169 went in at `5acbaa19` and `core/126` was released at `ff933079`. This leg began at `ff933079`.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Least sure about:** I did not re-run from the suite root itself, only proved the variable no longer reaches the binary.

---
*Days 2026-11-12 to 2026-11-12 rolled to [log-archive/supervisor-log-2026-11-12-to-2026-11-12.md](log-archive/supervisor-log-2026-11-12-to-2026-11-12.md).*
