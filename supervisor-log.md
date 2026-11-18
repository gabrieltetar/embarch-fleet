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

## 2026-11-18 03:29 — desk/037 revise-a-pending-draft-keeping-the-owners-edits

**Decided:** nothing numbered (burndown). Second unit of this leg (see `atlas/076` for the split and dispatch). EMB-165: a pending draft now stores `agent_body`, the agent's own version, beside the `body` the owner edits; a draft made before this unit uses its body at first revision as the agent version. `POST /drafts/{id}/revise` and the MCP tool `desk_revise_draft` apply one change to both, a section replaced by heading or an append, and keep the owner's other edits; a replace over a section the owner edited is refused with 409 naming the section and giving both texts, a section missing or doubled is 400, a draft not open is 404, and a `github_replies` draft is 400. `GET /drafts/{id}` and `desk_get_draft` work in any state and return `agent_body`, `owner_diff` and `owner_edited`, so after Send the diff is the owner's edits alone. `plugin/skills/desk/SKILL.md` gains a line on revising instead of rewriting. The desk-side shape the issue's Direction preferred; the voice skill that keeps a local baseline today is outside the suite and untouched. **Withheld decision filed as EMB-207** (Backlog): the reviewer found no contradiction with decisions 29, 30, 69 or 75 but read the stored agent version and the diff rule as a durable choice that arguably needs a number; it also carries the worker's two open questions, a full owner-edit history and per-reply revise of `github_replies`. `interfaces.md` came out of reserve by a verbatim move of the MCP tool inventory to `interfaces/mcp-tools.md` (now 12,549 of 15,360 B), so `tasks/desk/036` closes `done` with its `In flux: yes` left as written; `spec.md` went into reserve (9,186 of 10,240 B) and the worker filed `tasks/desk/038-compact-desk.md` `blocked`, due 2026-12-01. `features.d/desk-082-revise-pending-draft.md` adds the row. With this fold no task names EMB-165, so `finish` should close it.
**Merged:** `agent/desk/037-revise-a-pending-draft-keeping-the-owners-edits` (code `f0f6b98`, ff on `origin/main`; doc `207ca98b`, the worker's `3471d439` cherry-picked onto `46b2b300`). `cargo build`, `cargo test` (292 passed), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a reload of the desk's MCP server to pick up the two tools, and one real revise of a draft he has edited on the Desk tab. The Desk tab shows neither `agent_body` nor the diff; no UI issue is filed for that yet.
**Budget:** PROCEED in burndown, 5-hour 12%, weekly 71% at the previous fold.
**Least sure about:** the worker saw one `cargo test` run fail 1 of 292 and could not reproduce or name it in six more runs; my one run was green. A flaky test in `embarch-desk` is possible and unidentified.

---

## 2026-11-18 03:27 — atlas/076 render-pdf-pages-for-an-image-read

**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). First unit of this leg. Fleet Ready split this leg in `4ecb2c7c`: EMB-205 into `ui/110`, EMB-165 into `desk/037`, EMB-138 into `atlas/076`, EMB-135 into `atlas/077` (dispatched once this unit's atlas slot freed), announced at 03:18 (`1794997111.757099`). **EMB-85 left in Fleet Ready, unsplit:** its first box is Promptu build step 4, and `embarch-promptu/spec.md` says step 3 is built but unreviewed with its forks waiting for the owner, so step 4 would build on undecided ground; an attended pass should take it. EMB-138: `embarch-atlas pdf pages <file> [--pages 4-7|9-|1,3] [--dpi 80] [--tiles CxR] [--crop X,Y,W,H] [--out dir]` renders a page range of any PDF to PNGs in a scratch directory, no atlas needed, poppler only (`pdfinfo`, `pdftotext`, `pdftoppm`). Per page and first it prints `pN: text layer yes|no (N chars)` (yes at 40 or more non-space characters), then one line per PNG with page, tile, pixel size and path. `--crop` is PDF points from the displayed top-left; tiles divide the crop and the last row and column take the remainder; rotated pages use their displayed size. Bad input exits 2 with one line. Not an MCP tool, so no tool count moved. The worker left the task's `State:` as its claim line; I set it `done` at the fold. This unit also carries the 2026-11-17 day fold (38 units, by an `embarch-log-folder`), the roll of 2026-11-13 into `log-archive/`, and the once-per-day `check-client-names.py --suite --history`: every repo clean.
**Merged:** `agent/atlas/076-render-pdf-pages-for-an-image-read` (code `696ee62`, ff on `origin/main`; doc `955dcf18`, ff on the leg worktree). `pytest` 885 passed, 3 skipped (env-gated; `test_public_guard` ran and passed), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one run on a real scanned PDF read back with the image `Read` tool; the tests prove only that PNGs of the right size are produced from generated PDFs, so the first Done-when box ("reads legibly at the default settings") is unproven in practice.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00) at leg start, 5-hour 7%, weekly 71%, suggested wave 6; 12% / 71% at this fold. Spread-only refill gate skipped: the two source commits since the 19:22 `Spread sweep: nothing filed` line (`1579353b`, `2ee1b7e5`) each add a descriptive paragraph to `embarch-atlas/design.md` outside its open-questions section, so a sweep would read what that one read.
**Least sure about:** the 40-character threshold for "has a text layer": a scanned page with a thin OCR layer of page numbers or headers would read `yes` and send a caller to `pdftotext` for text that is not there.

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
*Days 2026-11-13 to 2026-11-13 rolled to [log-archive/supervisor-log-2026-11-13-to-2026-11-13.md](log-archive/supervisor-log-2026-11-13-to-2026-11-13.md).*
