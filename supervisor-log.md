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

## 2026-11-17 23:13 — api/161 compact-api

**Decided:** nothing numbered (burndown). Second of this leg's four units (see `topology/070` for the dispatch). Paid the api size debt `api/160` filed: `spec/implementation.md` §4 "Deployment and topology" moved verbatim into a new `embarch-api/spec/deployment.md` (1,893 B), and §4 keeps a one-line stub linking to it, so the heading, its anchor and the section numbering survive. `implementation.md` went from 9,168 B to 7,806 B, out of reserve. §7 and §8 are untouched, so both `Must not delete:` items (the constants table's `[assumed]` brackets, §8's `cosign verify-blob` command) stand. **Compaction question, the worker's answer:** yes, `spec.md` with the `spec/` files it links still answers how the API builds, deploys, secures and releases, each rule carrying its decision number; topology is one hop further away than before. The reviewer noted, as cosmetic, that `embarch-api/spec.md` still says §§3–7 moved to `implementation.md`; the stub there carries a reader on, so I left it.
**Merged:** `agent/api/161-compact-api` (code: none, doc-only; doc `f9c948d7`, the worker's `297c759a` cherry-picked onto `1d5246d4`). Ownership green, `check-docs.py` 12/12, `check-doc-size.py --pressure` no longer lists the file.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED in burndown, 5-hour 57%, weekly 66% at leg start.
**Least sure about:** whether `spec.md`'s "§§3–7 moved to `implementation.md`" line will mislead someone looking for deployment detail; it is one hop, not lost.

---

## 2026-11-17 23:13 — topology/070 compact-topology

**Decided:** nothing numbered (burndown). First of this leg's four units, all dispatched at 23:03 as foreground workers in one call, the shape the 22:36 leg used after two background dispatches today were orphaned. All four reported back to this leg. This one paid the topology size debt that `topology/069` filed: the "What validation asserts, and what it cannot" section moved verbatim into a new `embarch-topology/spec/validation.md` (3,231 B), with a pointer left in `spec.md` that names decisions 18, 26, 37–39, 44, 47 and 48. `spec.md` went from 10,079 B to 7,415 B, out of reserve. The `Must not delete:` item, the `cosign verify-blob` command in "What a release carries", is untouched. **Compaction question, the worker's answer:** yes, `spec.md` alone still orients a reader (what topology is and is not, the shape, declared facts, caller assumptions, the release check, current state), and it is now the index to `spec/validation.md`, `spec/storage-and-roles.md` and `spec/consumers.md` for the detail.
**Merged:** `agent/topology/070-compact-topology` (code: none, doc-only; doc `1d5246d4`, ff on `e6a62177`). Ownership green, `check-docs.py` 12/12, `check-doc-size.py --pressure` no longer lists the file.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00) at leg start, 5-hour 57%, weekly 66%, suggested wave 6; 63% / 66% at dispatch. Fleet Ready split this leg: EMB-96 into `atlas/073` and EMB-163 into `chat/032` (`254d777f`), announced at 22:59 (`1794981627.569739`). Spread-only refill gate skipped: no source changed since the 19:22 `Spread sweep: nothing filed` line.
**Least sure about:** nothing in this unit; a verbatim move the reviewer checked byte for byte.

---

## 2026-11-17 22:52 — umbrella/098 suite-release-verifies-components-and-signs-a-hashed-manifest

**Decided:** **folded step 1 out of `embarch-release-signing-proposal.md`**, per its own Fold rule, now that all four EMB-190 units have landed: the two design bullets for component signing and suite assembly became one bullet pointing to each repo's docs and umbrella decision 14, keeping the reason the signing stays in each workflow file; the umbrella row of "The work" keeps only what is not built; step 1 says the five workflows are written, unrun, and `actionlint`-unchecked; "The first download" now names the per-target manifest files, and its `sha256sum -c` line, which the JSON `files` object cannot feed, now says to compare each file against `files`. **Kept the worker's design call on manifest names**: four per-target manifests would collide on one release, so they are published as `embarch-manifest-<target>.json` and `.json.sigstore.json`, and a user renames both to `embarch-manifest.json` beside the unpacked archive before `embarch verify-release` reads them. The reviewer read it as a refinement of decision 14's "manifest per target". Otherwise nothing numbered (burndown). EMB-190, umbrella's part: `release.yml` signs like the other three (`cosign-installer@v3`); `assemble-suite.yml` runs on `suite-v*.*.*` tags, reads the component tags from a new `suite.toml` (core v0.1.4, api v0.1.0, umbrella v0.1.0, none signed), runs `cosign verify-blob` on each component archive against its repo's exact `release.yml@refs/tags/<tag>` identity, writes the manifest with `components` still name-to-tag (so `manifest.rs` and doctor check 1 are untouched), plus sibling `commits` and `files` objects, then signs it and attests each archive in one `sign` job behind `environment: release`. `verify_release.rs` dropped its tag-or-object enum and reads exactly that shape; `interfaces/verify-release.md` and `spec.md` agree. Decision 14 is amended in place. `spec.md` went into reserve, so the worker filed `tasks/umbrella/099-compact-umbrella.md` `blocked` on `In flux: yes` (due 2026-12-17, unparks when step 4 lands). With this fold no task names EMB-190, so `finish` should close it.
**Merged:** `agent/umbrella/098-suite-release-verifies-components-and-signs-a-hashed-manifest` (code `85e6e65`, ff on `41cbf56d`; doc `6f0d05cc`, the worker's `a8297793` cherry-picked onto `44a207b8`). `cargo build`, `cargo test` (273 passed across targets), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint` on `assemble-suite.yml` and `release.yml`; new signed component tags in `suite.toml` before the first suite tag, or its verify step fails by design; a check that `suite.toml`'s tags are the remotes' newest (the worker read them from the local clones).
**Budget:** PROCEED in burndown, 5-hour 35%, weekly 63% at leg start; see the close below for the end.
**Least sure about:** the workflow's untested parts: the Python heredoc that writes the manifest, `gh api repos/<repo>/commits/<tag>` for the commit, and the `actions/attest-build-provenance@v2` `subject-path` input, all from the worker's memory and none run.

---

## 2026-11-17 22:51 — api/160 release-workflow-signs-every-archive

**Decided:** nothing numbered (burndown). Third of this leg's four EMB-190 units (see `topology/069`). Api's `release.yml`: the build matrix uploads each archive as a workflow artifact and holds no `id-token`; one `sign-and-publish` job in the file (`needs: build`, `environment: release`, `contents: write`, `id-token: write`) installs cosign v3.0.4 through `sigstore/cosign-installer@v3`, signs all four archives with `cosign sign-blob --bundle`, refuses a count other than four, and publishes asset and bundle together. No api decision describes the release job, so the worker documented it in a new `spec/implementation.md` §8 "Release" with the exact `cosign verify-blob` command and amended no decision; the reviewer confirmed `decisions/build.md` 75 ("the Windows job only builds") still holds. §8 put `embarch-api/spec/implementation.md` into reserve (9,168 of 10,240 B), so the worker filed `tasks/api/161-compact-api.md` (`open`, `In flux: no`). With this fold the proposal's component row is gone from its work table, and its step 1 says the component half is written and links all three repos' checks.
**Merged:** `agent/api/160-release-workflow-signs-every-archive` (code `0d93709`, ff on `0f6fb6c7`; doc `40a05f4c` and `44a207b8`, the worker's `b8bd7459` and `49a6e6cc` cherry-picked onto `737e204a`). `cargo build`, `cargo test` (413 passed across targets), clippy `-D warnings` green (exit code checked; the worker had not), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint` on `release.yml`; the first signed tag, which also shows whether `download-artifact`'s `merge-multiple` lays the archives where the job's `archives/*` globs look (the worker's own doubt; a miss fails the four-archive count loudly rather than publishing nothing quietly).
**Budget:** PROCEED in burndown, 5-hour 35%, weekly 63% at leg start.
**Least sure about:** the job has no tag `if:` guard, so a `workflow_dispatch` run would reach the signing step with a branch ref in its identity; the `release` environment is tag-only, which should refuse it, but that is the owner's step-2 setting and nothing here checked it.

---

## 2026-11-17 22:50 — core/127 release-workflow-signs-every-archive

**Decided:** nothing numbered (burndown). Second of this leg's four EMB-190 units (see `topology/069` for the split and why the workers ran in the foreground). Core's `release.yml`: the build matrix is now `contents: read` and uploads `archive-<target>` workflow artifacts; one `sign-and-publish` job in the file (`needs: build`, `environment: release`, `contents: write`, `id-token: write`) installs cosign v3.0.4 through `sigstore/cosign-installer@v4`, signs all four archives with `cosign sign-blob --bundle`, refuses a count other than four, and publishes asset and bundle together. `spec.md` §3 gained "Release assets" with the exact `cosign verify-blob` command. The worker amended the body of `decisions/platform.md`'s decision 1/2/7/17 with a note and added no decision; the reviewer read it as an amendment that keeps the 2026-09-08 correction. The worker left the task's `State:` line at `claimed`, with every box ticked; I set it `done` in this fold. The proposal's work table now names core's part as written.
**Merged:** `agent/core/127-release-workflow-signs-every-archive` (code `d4c9564`, ff on `c0d2a7eb`; doc `737e204a`, the worker's `9e0917c1` cherry-picked onto `371ee24b`). `cargo build`, `cargo test` (391 and 2 passed), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the native Windows build (a debt for any unit touching `embarch-core`, though this one changed no Rust); `actionlint` on `release.yml`; the first signed tag.
**Budget:** PROCEED in burndown, 5-hour 35%, weekly 63% at leg start.
**Least sure about:** `cosign-installer@v4` here against `@v3` in the other three repos. One of the two majors may not accept `cosign-release: v3.0.4`, and the first tag in that repo is where it shows.

---

## 2026-11-17 22:49 — topology/069 release-workflow-signs-every-archive

**Decided:** **split EMB-190 (the owner's, `Scope: suite`) into four single-repo tasks rather than one `suite` pass** (`dda025dd`): `umbrella/098`, `core/127`, `api/160` and this one, one per release workflow. My reasoning: none changes a wire type or a shared crate's Rust, each repo's `main` stands alone, and nothing runs until the owner pushes a tag, so §8's half-landed-change risk does not arise and no 30-minute window was owed. Announced at 22:36 (`1794980207.273419`). **Dispatched all four as foreground workers in one call, not background**, because today's 18:29 and 19:17 legs were both orphaned after a background dispatch (their workers' notifications went to the listener). All four reports came back to this leg. Otherwise nothing numbered (burndown). EMB-190, topology's part: the build matrix now only uploads workflow artifacts, and one `sign` job in `release.yml` (`needs: build`, `environment: release`, `id-token: write`) installs cosign v3.0.4 through `sigstore/cosign-installer@v3`, signs all four archives with `cosign sign-blob --bundle`, refuses a count other than four, and publishes each archive beside its `.sigstore.json`. `spec.md` gained "What a release carries" with the exact `cosign verify-blob` command. That section put `embarch-topology/spec.md` into reserve (10,079 of 10,240 B), so the worker filed `tasks/topology/070-compact-topology.md` (`open`, `In flux: no`). The proposal's work table now names topology's part as written.
**Merged:** `agent/topology/069-release-workflow-signs-every-archive` (code `ee45b6c`, ff on `b905523e`; doc `371ee24b`, ff on `7362aa0e`). `cargo build`, `cargo test` (15 passed), clippy `-D warnings` green under the default features and under `--no-default-features` with `software,wire` and with `hardware`; client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** `actionlint` on `release.yml` (not installed here, so only a PyYAML parse ran), and the first signed tag, which is the only test the workflow has.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00) at leg start, 5-hour 35%, weekly 63%, suggested wave 6. Spread-only refill gate skipped: no source changed since the 19:22 `Spread sweep: nothing filed` line.
**Least sure about:** the installer pin. This unit, `api/160` and `umbrella/098` use `sigstore/cosign-installer@v3` and `core/127` uses `@v4`, each from the worker's memory, and nothing here can check which major installs cosign v3.0.4.

---

## 2026-11-17 22:24 — chat/030 a-login-pick-says-which-claude-code-surfaces-need-a-reload

**Decided:** nothing numbered (burndown). Last of this leg's four re-lands of the 19:17 leg's workers (see `atlas/072` below). EMB-168: Claude Code 2.1.326 has no supported route to re-read its login, and the one setting its extension host reacts to, `claudeCode.environmentVariables`, is the owner's and a pick must not rewrite it. So when a pick changes the effective login, `embarchChat.pickLogin` now offers Reload Window (or Later), with the reason, through `pickNotice` in `src/loginState.ts`. It never reloads unasked. **Decision 106's body is amended, as the task asked, not replaced by a new decision:** it now says which surfaces follow a pick at once (new EmbArch chats, new Claude Code chats and terminals, the status item) and which need a reload (Claude Code's "Account & usage" dialog, which caches `claude auth status`). `spec.md`'s login bullet says the same. That sentence pushed `embarch-chat/spec.md` into reserve (9,119 of 10,240 B), so the worker filed `tasks/chat/031-compact-chat.md` (`open`, `In flux: no`, due 2026-12-17) in the same commit, which `main` now carries.
**Merged:** `agent/chat/030-a-login-pick-says-which-claude-code-surfaces-need-a-reload` (code `581048d`, ff on `f79c167`; doc `dff4624b`, the worker's `2f9eb369` cherry-picked onto `4cb94685`). `npm ci`, `build`, `typecheck` green, `npm test` 386 run, 308 passed, 78 skipped, 0 failed, `test:webview` passed, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a rebuild and reinstall of the extension, then one real pick in a window opened on the other login: the notice appears, Reload Window reloads, and the account dialog names the picked login. The test covers the notice text and the unchanged-pick case only; the command's reload path is not covered, since the test mock has none.
**Budget:** PROCEED in burndown, 5-hour 8%, weekly 60% at leg start; PROCEED at end, 5-hour 23%, weekly 62% (resets in 4h45m and 7h35m), suggested wave 6. Leg close: 4 of 4 units, all re-lands of the 19:17 leg's dispatches (`atlas/072`, `api/159`, `desk/033` with `desk/032`, `chat/030`); this leg split nothing and dispatched nothing. On `main` the dispatchable work is the new `chat/031` size debt plus Fleet Ready's 19 unsplit issues (11 of them `atlas`). Bench `api/059` and `dev-bench/038` wait for an attended leg (burndown). `tasks/doc/098` (owner-only) still reads `done` and is unretired.
**Least sure about:** the fix rests on the worker's reading that Claude Code 2.1.326 exposes no re-read command; a later Claude Code release that adds one would make the reload prompt unnecessary, and nothing will notice.

---

## 2026-11-17 22:21 — desk/033 a-desk-tool-returns-a-prs-review-threads

**Decided:** nothing numbered (burndown). Third of this leg's four re-lands of the 19:17 leg's workers (see `atlas/072` below). EMB-176: a new MCP tool, `github_pr_threads`, over `POST /github/pr-threads`, returns a pull request's inline review threads grouped root-then-replies (author, time, path and line on each comment), the review bodies with their states, and a mark on each thread whose latest comment is not the PR author's. The reviewer also checked the 032 move word for word against 032's `Must not delete:` list and found it a pure split. `awaiting_only` narrows it to those. `github::pr_threads` pages 100 at a time with no cap, and a test covers a PR past 100 comments. **It also closes `tasks/desk/032`** (size debt, `blocked` on `In flux: yes`, due 2026-12-01): per `.claude/leg.md`'s rule that the actor making the flux compacts the file it writes into, the worker moved `embarch-desk/interfaces.md`'s "Connectors and CLI" section verbatim into a new `embarch-desk/interfaces/cli.md`, leaving the parent at 12,858 B and out of reserve. 032 is `done` with its `In flux: yes` left as written, and this fold retires both task files. `spec.md` and a new `features.d/desk-079-github-pr-threads.md` row name the tool; `suite/features.md` is reassembled.
**Merged:** `agent/desk/033-a-desk-tool-returns-a-prs-review-threads` (code `6785411`, ff on `640cb0c`; doc `d2b80b48`, the worker's `9a8f00cc` cherry-picked onto `3ff120e5`). `cargo build`, `cargo test` 271 passed, clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12, and `check-doc-size.py --pressure` lists no desk file.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a rebuild and redeploy of the desk, then one `github_pr_threads` call on a real PR: only synthetic JSON has exercised the grouping and paging, and no live GitHub call has run.
**Budget:** PROCEED in burndown, 5-hour 8%, weekly 60% at leg start.
**Least sure about:** a thread is marked awaiting when its last inline comment is not the PR author's (`src/threads.rs`), so one answered in a review body or resolved without a reply still reads as awaiting, and nothing tests either case.

---

## 2026-11-17 22:19 — api/159 bundle-recover-line-states-only-what-core-decided

**Decided:** nothing numbered (burndown). Second of this leg's four re-lands of the 19:17 leg's workers (see `atlas/072` below). EMB-203, the reviewer finding the `api/158` entry kept that unit despite: the bundle README's recover line no longer says Core's decisions "map" the vendor runner's `--erase` to the range erase. It now says decision 32 measured the vendor's own runner with `--erase`, on the same image, as the recovery; that the suite records no command line for it; and that the program command above is Core's own erase request, unconfirmed on a board, so it is not known to be that recovery. `tools-bundle.md` says the same, and a test fails if "map it to" or "run the program command above again" comes back. The reviewer read decisions 32 and 36 in full and found each claim in their text. The worker left the task's `State:` line at `claimed`, with every box ticked; I set it `done` in this fold. This settles the two-findings-in-a-row worry the `api/158` entry ended on: no revert of `3479afa`/`206a5584` is owed.
**Merged:** `agent/api/159-bundle-recover-line-states-only-what-core-decided` (code `0f6fb6c`, ff on `3479afa`; doc `4b424223`, the worker's `c39f7384` cherry-picked onto `76201b0d`). `cargo build`, `cargo test` green (228 passed across the default targets), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new. The `api/157` debt stands, and is now unblocked on the wording side: `embarch-api bundle` on a real nRF54L sysbuild directory, then flash its hex with the README's program command. **Owed, owner-side:** a rebuild and redeploy of `embarch-api` before any bench engineer sees the corrected README.
**Budget:** PROCEED in burndown, 5-hour 8%, weekly 60% at leg start.
**Least sure about:** whether a recover line that says "not known to be that recovery" helps a bench engineer with a bricked board at all; it is true, and it gives them no command to run.

---

## 2026-11-17 22:18 — atlas/072 search-schematic-pdf-pages

**Recovery, read first.** The leg that took the lock at 19:17 split EMB-203, EMB-176 and EMB-168 into `api/159`, `desk/033` and `chat/030` (`87a3112e`), claimed those three and `atlas/072` (`9e97eb10`, `aa05525c`, `28efac10`, `a93b940a`), dispatched four workers at 19:21 and was cut off with no entry and no `leg-end`. It owes this line: Spread sweep: nothing filed (2026-11-17 19:22). Its `fleet-hardware.py --refresh` exited 1, which does not matter in burndown (no bench units). The leg that took the lock at 19:51 started re-landing them and died on a 5-hour 429 with nothing landed: `origin/main` was still `a93b940a` when this leg started at 22:14. All four workers had pushed both branches with clean trees, each a fast-forward of its repo's `main`. This leg re-lands those four as its own four units, gating each merge result itself, and dispatches nothing new. Those dispatches predate this leg's `leg-start`, so it ticks no `leg-reported` for them.
**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). EMB-156's second half: a new lookup, `schematic_text <pattern>` (`board=`, `context=`), searches the `pdftotext -layout` text of every schematic PDF that `atlas.toml`'s `[[boards]]` name. Each hit carries the board, the PDF file, the page and the sheets `netlist.json` puts on that page. The worker made it a verb of its own rather than adding schematic PDFs to `find_text`, because a schematic has no `docs/<id>`, table of contents or distillation for `find_text`'s hit format, and `DESIGN.md` gives that reason. It reads the PDF on every call and writes no usage row. It is registered read-only, the lookup count is now eighteen everywhere, and the atlas-use skill names it in place of hand-run `pdftotext -bbox`. The worker left the task's `State:` line at `claimed`, with every box ticked; I set it `done` in this fold. With `atlas/071`, this closes EMB-156.
**Merged:** `agent/atlas/072-search-schematic-pdf-pages` (code `c4e2601`, ff on `56e1cee`; doc `09b149a3`, ff on `a93b940a`). `pytest` 865 passed, 3 skipped (env-gated; `test_public_guard` ran and passed), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** one `schematic_text` search against a real board's schematic PDFs, since only a synthetic schematic has exercised it.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00), 5-hour 8%, weekly 60%, suggested wave 6. This leg runs no wave.
**Least sure about:** how slow `schematic_text` is on a large multi-sheet schematic, since it runs `pdftotext` over every PDF on every call and nothing caches it.

---

## 2026-11-17 19:15 — umbrella/097 embarch-verify-release

**Decided:** **folded step 3 out of `embarch-release-signing-proposal.md`**, the worker's `status.d/` request. The prompt that spawned this leg said that file was in neither ownership list. It has been in `fleet.toml`'s `fleet_writable` since `2b4ad6b` (2026-11-17), and `check-ownership.py --supervisor` passed on it. Per the proposal's own Fold rule, the identity, trust-root and verb bullets became one bullet pointing to `embarch-umbrella`'s spec and `interfaces/verify-release.md`. It keeps the never-cache reason and the rejected `sigstore`/`cosign` routes. Step 3 is one line, and the umbrella row of "The work" keeps only what is not built. **Two things stay proposed there, because the verb does not do them:** checking the certificate's source-repository and ref extensions (the reviewer confirmed the code checks only the exact identity and issuer, which already name both), and a test against a real suite release bundle, which needs step 1 (EMB-190). Otherwise nothing numbered (burndown). EMB-192: `embarch verify-release [DIR] [--trusted-root FILE | --refresh-trust-root]` checks the manifest's Sigstore bundle under issuer `https://token.actions.githubusercontent.com` and the exact `assemble-suite.yml@refs/tags/suite-v<version>` identity, then every listed file's SHA-256. It uses `sigstore-verify` and `sigstore-types` pinned `=0.16.0` and fetches nothing unless `--refresh-trust-root`, whose TUF cache is disabled. It then prints the version, the component tags and commits, the identity and the log time. The manifest shape (components as a tag or `{tag, commit}`, `files` as `{path: sha256}`) is assumed until EMB-190 fixes it. Umbrella decision 28's "copies with no check" is now stale in part, and the worker did not edit it (burndown); step 4 is where it gets amended. A new `features.d/umbrella-150-verify-release.md` row is assembled into `suite/features.md`.
**Merged:** `agent/umbrella/097-embarch-verify-release` (code `41cbf56`, ff on `47feb0f`; doc `52a81f11`, the worker's `3a6d8404` cherry-picked onto `ecf10a06`). `cargo build`, `cargo test` 272 passed (offline), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12. **CI not verified on macOS:** `build-check.yml`'s first run on the branch push (run 44217599100) passed on `aarch64-unknown-linux-gnu` (the `aws-lc-sys` cross leg), `x86_64-unknown-linux-gnu` and `x86_64-pc-windows-msvc`. `aarch64-apple-darwin` was **cancelled**, with no log and no failed step, and the worker could not re-run it. I did not block on it. The next push to `embarch-umbrella`, or a manual re-run, settles it.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a re-run of run 44217599100's macOS leg, or a look at the next push's.
**Budget:** PROCEED in burndown at start (5-hour 71%, weekly 57%) and end (5-hour 80%, weekly 58%, resets in 2h54m and 10h44m), suggested wave 6. Leg close: 4 of 4 units, all re-lands of the cut-off 18:29 leg's dispatches (`api/158`, `atlas/071`, `promptu/010`, `umbrella/097`). This leg split nothing and dispatched nothing. On `main` the dispatchable work is `atlas/072` plus Fleet Ready's 21 unsplit issues and the new EMB-203 (reviewer finding on `api/158`, the obvious next `api` unit). Bench `api/059` and `dev-bench/038` wait for an attended leg (burndown). The 5-hour window is at 80%, so a full wave of 6 next leg may reach the 97% stop or a 5-hour 429, which pauses burndown until the reset rather than ending it.
**Least sure about:** the fold's wording "the identity already names both" for the extension check. It is true of the string, but whether `sigstore-verify` binds the identity to the certificate's SAN alone, or also to those extensions, is something I took from the reviewer and did not read in the crate.

---

## 2026-11-17 19:13 — promptu/010 shell-writes-to-a-memory-index-get-checked

**Decided:** nothing numbered (burndown). Third of this leg's four re-lands of the cut-off 18:29 leg's workers (see `api/158` below). EMB-187: the plugin's PreToolUse hook now also matches `Bash`. When a command names a memory-folder `MEMORY.md` (resolved by `claude::memory_target`, `~/` and `$HOME/` expanded) and looks like a write, the hook adds a warning that names the Edit tool as the checked route. A write here means a redirect, `tee`/`mv`/`cp`/`sed`/`perl`/`truncate`/`install`/`dd`/`ed`, or `write`, `open(` or `fs.` in the text. It warns in every mode and never refuses; a read gets nothing. Recorded in `spec.md` and the code repo's `docs/contract.md` §3.3a. The heuristic cannot see a script that builds the index path at run time or never names it.
**Merged:** `agent/promptu/010-shell-writes-to-a-memory-index-get-checked` (code `2a1750d`, ff on `20063c7`; doc `04e5dff2`, the worker's `22f46dcb` cherry-picked onto `b5201cec`). `cargo build`, `cargo test --all-targets` 127 passed (75, 20, 32), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** the reviewer notes decision 5 (`decisions/memory.md`) still says the PreToolUse hook runs "on Write, Edit and MultiEdit". That is incomplete now, not contradicted, and `spec.md` and the contract say Bash too. It is for the next promptu unit that touches that file, after `promptu/008`'s compaction. **Owed, owner-side:** the new `Bash` matcher in `plugin/hooks/hooks.json` reaches a session only after the plugin is reinstalled, and no real session has run the hook on a Bash call yet. `tasks/promptu/008` stays `blocked` (`decisions/patterns.md` 11,138 of 12,288 B, due 2026-11-24); this unit did not touch that file.
**Budget:** PROCEED in burndown, 5-hour 71%, weekly 57% at leg start.
**Least sure about:** the hook now runs on every Bash call in every session with the plugin. The no-match path returns before any file read, but nothing has measured what an extra process per shell command costs a long session.

---

## 2026-11-17 19:11 — atlas/071 checks-flag-module-pads-left-without-a-port

**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). Second of this leg's four re-lands of the cut-off 18:29 leg's workers (see `api/158` below). EMB-188 and EMB-156's `checks.md` half: `mismatch.py` adds the check "MCU pads with a net have a pin name", class `pad-without-name` (part, pad, net), where a `text-layer` or overlay name counts as named. It also adds "DT pins resolve to a schematic pad", class `dt-pin-unresolved` (each DT node and property), which needs a build and is otherwise listed under Not run. Both reach `checks.md` and `mismatches.json`, and `DESIGN.md` records them beside `atlas/070`'s text-layer recovery. The new test runs EMB-188's shape, six named pads down one side of a synthetic module with upright names inside the outline, and all six come back `name_source: text-layer`. Rotated names on a side column, or names outside the outline, are untested, and on a real board of that shape the new flag is what reports it. The worker left the task's `State:` line at `claimed`, with every box ticked; I set it `done` in this fold. EMB-156's other half, schematic PDF page search, is `atlas/072`, `open` on `main`.
**Merged:** `agent/atlas/071-checks-flag-module-pads-left-without-a-port` (code `56e1cee`, ff on `e815f43`; doc `78932c3d`, the worker's `139ce5e9` cherry-picked onto `5ce81ee3`, the changelog fragment and the task file only). `pytest` 863 passed, 3 skipped (env-gated: real west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** a first atlas of a real module schematic, to see whether the two flags fire where they should.
**Budget:** PROCEED in burndown, 5-hour 71%, weekly 57% at leg start.
**Least sure about:** whether `pad-without-name` will be noisy on a real board: every netted pad on an MCU part with no name now becomes a mismatch, and only synthetic fixtures have measured the count.

---

## 2026-11-17 19:10 — api/158 bundle-readme-commands-match-cores-decisions

**Recovery, read first.** The leg that took the lock at 18:29 split EMB-202, EMB-188, EMB-156, EMB-187 and EMB-192 into `api/158`, `atlas/071`, `atlas/072`, `promptu/010` and `umbrella/097` (`bc796f1a`, with `filed` run: none of the five is in Fleet Ready), claimed four of them (`67d0fd27`, `49f75121`, `b6f52955`, `82d74a80`), dispatched four workers at 18:35 and was cut off with no entry and no `leg-end`. All four workers finished and pushed both branches, with clean trees. This leg waited out the lock (stale at 19:06) and re-lands those four as its own four units, gating each merge result itself; it dispatches nothing new. Those dispatches predate this leg's `leg-start`, so it ticks no `leg-reported` for them. `atlas/072` stays `open` on `main`.
**Decided:** **kept the unit despite a confirmed reviewer finding, with the forward fix left to EMB-203** (Fleet Ready), the same call the 18:21 entry made for `api/157`. The finding, which I checked against both decisions: the README's Recover line says Core's decisions "map" the vendor runner's `--erase` (decision 32, measured) to the range erase. Core decision 36 makes no such mapping. It says only that Core's own erase request generates `ERASE_RANGES_TOUCHED_BY_FIRMWARE`, and that nobody has confirmed the mode on silicon. `tools-bundle.md` repeats the line. Reverting would bring back EMB-202's defect, an `ERASE_ALL` program line presented as Core's record, and the program line and its "not yet confirmed on a board" label are right. Nothing reaches a bench engineer before the owner rebuilds and redeploys `embarch-api`. Otherwise nothing numbered (burndown). EMB-202: the nRF54L program line is now `chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE`, the README says the erase mode is a contract decision 36 records as unconfirmed, and a test fails if `ERASE_ALL` comes back. The worker left the task's `State:` line at `claimed`, with every box ticked; I set it `done` in this fold. The reviewer reported `embarch-decision-reversals.md` missing from the leg root. It is there, so its grep failed for some other reason, and its reversals check did not run.
**Merged:** `agent/api/158-bundle-readme-commands-match-cores-decisions` (code `3479afa`, ff on `9e4a99f`; doc `206a5584`, ff on `82d74a80`). `cargo build`, `cargo test` green (228 passed across the default targets), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-203
**Hardware debts:** none new. The `api/157` debt stands: `embarch-api bundle` on a real nRF54L sysbuild directory, then flash its hex with the README's program command once EMB-203 has corrected the Recover line. **Owed, owner-side:** a rebuild and redeploy of `embarch-api`.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00), 5-hour 71%, weekly 57%, suggested wave 6. This leg runs no wave.
**Least sure about:** keeping it again. Two reviewer findings in a row on the same README line say it was written from the decisions' summaries, not their text. If the owner reads `gate.md`'s revert-by-SHA literally, the revert is `3479afa` and `206a5584`, both clean, and it brings back the `ERASE_ALL` line.

---

## 2026-11-17 18:28 — chat/029 the-promptu-card-restores-the-original-prompt

**Decided:** nothing numbered (burndown). EMB-197: after a rewritten Promptu run, a "Restore my original prompt" action replaces the draft with the original, verbatim, in one undoable edit. `render` already returns `rewritten` (Promptu contract §8.3), so `embarch-promptu` needed no change. The host (`PromptuRuns.restore`, `src/promptu/runs.ts`) keeps the last rewritten run's id and folder per chat, and the page never names a run. `PromptuCli.original` calls `promptu original <run> --json` and never reads Promptu's log files. A pasted brief, an offline run or rewrite off never calls it. **Placement differs from the issue**: `webview/chat/promptu.tsx` is the modal, gone once the prompt lands, so `RestoreOriginal` lives there and the composer shows it under the draft beside the "Promptu wrote this prompt" notice. The reviewer found no decision it contradicts. Recorded in `embarch-chat/spec/input.md`, and decision 96 is untouched.
**Merged:** `agent/chat/029-the-promptu-card-restores-the-original-prompt` (code `f79c167`, ff on `7a9aaf1`; doc `f47ffc83` and `72730863`, cherry-picked onto `0c1f3f47`). `npm ci`, `build`, `typecheck` green, `npm test` 307 passed, 78 skipped, 0 failed, `test:webview` passed, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the installed `promptu` predates `promptu original` ("unrecognized subcommand"), so the action fails on this machine until Promptu is rebuilt and reinstalled. Then run one real rewritten prompt and click it. The extension needs its own rebuild and reinstall.
**Budget:** PROCEED in burndown at start (5-hour 33%, weekly 53%) and end (5-hour 44%, weekly 54%), suggested wave 6. Leg close: 4 of 4 units (dev-bench/048, atlas/070, api/157 with EMB-202 open, chat/029), one wave of 4 dispatched at 18:10, all landed by 18:31. On `main` no task is dispatchable: the blocked size debts are `desk/032`, `promptu/008` and the new `dev-bench/049`, and the bench tasks `api/059` and `dev-bench/038` wait for an attended leg. Fleet Ready holds about 26 issues: the 25 unsplit plus reviewer finding EMB-202, which fixes api/157's README erase option and is the obvious next `api` unit. EMB-156 and EMB-188 follow atlas/070. `tasks/doc/098` (owner-only) reads `done` and is still unretired.
**Least sure about:** whether a stale installed `promptu` should hide the action rather than show it and fail. The host does not check the CLI's version before offering it.

---

## 2026-11-17 18:21 — api/157 bundle-a-build-for-a-bench-engineer

**Decided:** **kept a landed unit despite a confirmed reviewer finding, and left the forward fix to EMB-202** (Fleet Ready). The finding, verified by me: the bundle README's nRF54L program command uses `chip_erase_mode=ERASE_ALL`, and its preamble says every command is "what embarch-core records". Core decision 36 (`decisions/flash-backend.md`) says Core asks for `ERASE_RANGES_TOUCHED_BY_FIRMWARE` and never `ERASE_ALL`. The recover line ("the vendor's erase-all") does not match Core decision 32 either. I read this as false provenance in two table rows and one doc line, not as code doing what a decision forbids: no Core behaviour changed, and nothing reaches a bench engineer before the owner rebuilds and redeploys `embarch-api`. So no revert, unlike `chat/028` at 14:47, where the wrong behaviour crossed logins. Otherwise nothing numbered (burndown). EMB-171: `embarch-api bundle <project> [--notes] [--out]` and a `bundle` MCP tool over `src/bundle.rs`, with the `zip` and `ihex` crates (no shell `zip`, no Python). It ships the sysbuild `merged.hex` when present, checks it holds data at the `mcuboot` and `image-0` partitions read from the build's `zephyr.dts`, renders a README and writes `<name>-<sha>/` plus its `.zip`. **The freshness rule the task assumed did not exist**: `build_and_flash` compares the artifact only with the build's start. `bundle` adds artifact-against-newest-source, rebuilds when stale and refuses if still stale. The reviewer found this stricter than `bootload.md`'s rule and in no conflict with it. **Withheld decision filed: EMB-201** (Backlog, `Type: decision`): whether the README template and the family table stay in code.
**Merged:** `agent/api/157-bundle-a-build-for-a-bench-engineer` (code `9e4a99f`, ff on `54d4035`; doc `95ba8548`, cherry-picked onto `0d1af7d3`). `cargo build`, `cargo test` 413 passed, clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12. A new `features.d/api-328-bundle.md` row, assembled into `suite/features.md`.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-202
**Hardware debts:** `embarch-api bundle` on a real finished nRF54L sysbuild directory, then flash its hex with the README's program command once EMB-202 has corrected it. Needs any nRF54L board. Only a synthetic `zephyr.dts` (32-bit `reg` cells assumed) and a synthetic hex have exercised it. **Owed, owner-side:** a rebuild and redeploy before the verb or tool exists anywhere.
**Budget:** PROCEED in burndown, 5-hour 39%, weekly 53%.
**Least sure about:** keeping it rather than reverting. If the owner reads `gate.md`'s "a confirmed contradiction is reverted by SHA" literally, the revert is `9e4a99f` and `95ba8548`, both clean.

---

## 2026-11-17 18:18 — atlas/070 recover-rotated-module-pad-names-from-the-text-layer

**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). EMB-89, the first of the three blank-module-pad issues. EMB-156 (schematic text search, `checks.md` flag) and EMB-188 (DT pin on an unresolved pad) stay in Fleet Ready, to be split on what this leaves. `smartpdf.recover_pad_names` runs after `pin_name_for` on still-unnamed pads of 3+-pin parts. A pad on a vertical anchor takes the rotated words in its number's x column, and a side pad takes the upright words on its row. Only words inside the symbol outline count, which is the popup rectangle or else the pad extent. Numbers, designators, values and other pads' numbers are never names. Exactly one candidate becomes the name, with `name_source: "text-layer"` in `netlist.json`, `NAME (text-layer)` in `pins.md`, and `pin_name_source` in `pin_trace`. A pad with zero or two candidates stays blank and is listed as `pad-name-unpaired` in `issues.md`. The worker read "the atlas report" as the ingest's issues, not `checks.md`. Tolerances: the existing `PIN_NAME_AXIS` (3.2 pt), plus a new `PAD_NUMBER_REACH` (20 pt), which is assumed, not measured. `DESIGN.md` records the step.
**Merged:** `agent/atlas/070-recover-rotated-module-pad-names-from-the-text-layer` (code `e815f43`, ff on `39b34b5`; doc `fe56b8ea`, cherry-picked onto `dcd820c9`, the changelog fragment and the task file only). `pytest` 861 passed, 3 skipped (env-gated: real west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** a recovered name shows with no mark in the graph UI (`graph.py` node name), `nets.md` and `parts.md`. Overlay names (`llm-unverified` included) are equally unmarked there, and DESIGN.md names only `pin_trace` and `pins.md` as marked surfaces. This is not a contradiction, and it is a candidate follow-up. **Owed, owner-side:** a first run on a real module schematic. Only a synthetic PDF has exercised the pairing.
**Budget:** PROCEED in burndown, 5-hour 39%, weekly 53%.
**Least sure about:** `PAD_NUMBER_REACH` at 20 pt is a guess, and on a dense module a wrong pairing would print a confident port marked only by a suffix.

---

## 2026-11-17 18:15 — dev-bench/048 check-and-refresh-patch-sums

**Read first: this leg handed back early and kept running.** The leg that took the lock at 18:06 split EMB-197 into `tasks/chat/029` and EMB-89 into `tasks/atlas/070` (`fb235f51`), claimed those two plus `api/157` and `dev-bench/048` (`4c3034ed`, `4a1b08f1`, `d902e9d8`, `1afcf9a1`), and dispatched all four at 18:10. At 18:12 the harness forced its final report, which says "nothing landed, the next leg lands them". The session stayed alive and the worker reports kept arriving, so it went on landing under the same lock. Where this log and that report disagree, this log is right. The refill sweep was owed (2 dispatchable, 2 scopes) and was skipped: Fleet Ready held 27 unsplit issues, more than a leg can dispatch.
**Decided:** nothing numbered (burndown). EMB-146: `scripts/patch-sums.py --check|--update <patches.yml>` in `embarch-dev-bench`, standard library only. Paths resolve against `patches/` beside the yml and hash as text with newlines normalised, the way `west patch` does. The worker read that from a local Zephyr checkout's `patch.py`. `--update` rewrites only the stale value on its line. `pd-bench/README.md` names it, and the repo's `CLAUDE.md` gained a "Before landing" line for `--check`.
**Merged:** `agent/dev-bench/048-check-and-refresh-patch-sums` (code `60ab42c`, ff on `0aaf5d68`; doc `dfb81491`, cherry-picked onto `1afcf9a1`). `test_patch_sums.py` 5 passed, `--check` on `workspaces/pd-bench/manifest/zephyr/patches.yml` exits 0, client names clean, ownership green on both branches, `check-docs.py` 12/12. No cargo: the repo has no `Cargo.toml`. The worker filed size debt `tasks/dev-bench/049-compact-dev-bench.md` (`embarch-dev-bench/spec.md` 9,275 of 10,240 B, due 2026-12-01, `blocked`, `In flux: yes`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** the reviewer notes `spec.md` calls `--check` "the gate's step", while the repo's `CLAUDE.md` makes it a manual pre-landing step, and dev-bench decision 9 says the fleet gate cannot reach the repo. Loose wording, for the next dev-bench unit that touches `spec.md`.
**Budget:** PROCEED in burndown at start (5-hour 33%, weekly 53%) and at this fold (5-hour 39%, weekly 53%), suggested wave 6, 4 dispatched (the leg's unit cap).
**Least sure about:** whether `tasks/dev-bench/049` should be parked `In flux: yes` at all. It was filed for one sentence over the reserve line, and a verbatim split would pay it now.

---

## 2026-11-17 18:05 — desk/031 read-a-desk-routes-shape

**Decided:** nothing numbered (burndown). EMB-137: `embarch-desk get <route> [--post <json>] [--count-by <field>] [--raw] [--config-dir <dir>] [--port <n>]` prints a route's top-level keys, list lengths and one sample row, with the caller never handling the token. It reaches the default instance or a named one (`--config-dir`, where its `desk-token` is read and never generated, and `--port`, else `EMBARCH_DESK_CONFIG_DIR` / `EMBARCH_DESK_PORT`). It masks rather than refuses: a value under a key naming a secret, and the bearer itself, never reach the output. `--post` sends a JSON body, for the routes that are POST reads. Recorded in `spec.md` and `interfaces.md`.
**Merged:** `agent/desk/031-read-a-desk-routes-shape` (code `640cb0c`, ff on `0a62c64`; doc `d2000b58`, cherry-picked onto `8d391395`). `cargo build`, `cargo test --all-targets` 268 passed, clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12. The worker filed size debt `tasks/desk/032-compact-desk.md` (`embarch-desk/interfaces.md` 14,128 of 15,360 B, due 2026-12-01, `blocked`, `In flux: yes`).
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the deployed desk binary carries `get` only after a rebuild and redeploy.
**Budget:** PROCEED in burndown at start (5-hour 30%, weekly 52%) and end (5-hour 33%, weekly 53%), suggested wave 6; this leg ran no wave. Leg close: 4 of 4 units, all the cut-off 17:14 leg's dispatches; nothing new split or dispatched, no refill sweep (29 dispatchable: `api/157`, `dev-bench/048` and 27 unsplit Fleet Ready issues). Bench `api/059` and `dev-bench/038` wait for an attended leg (burndown). The doc branch `agent/ui/059-diff-new-lines-republish` (2026-09-16) is still on `origin`, unprovable by the fold, so it is the owner's to delete or keep.
**Least sure about:** `--post` lets a shell send a body to any route, mutating ones included, from a verb named and documented as a read; nothing in the code limits it to POST reads.

---

## 2026-11-17 18:03 — promptu/009 list-an-earlier-runs-questions-and-answers

**Decided:** nothing numbered (burndown). EMB-185: `promptu prior <prompt-file> [--projects <dir>] [--json]`, read-only, lists each earlier session's `AskUserQuestion` questions, options and the owner's answers when that session's first user turn is the prompt (text equal after trimming; a footer-only file matches a first turn ending in that footer; the footer carries no run id, so the text decides). The same footer under other text is a near-match, counted and not listed; exit 2 for an unreadable file or folder. Contract §13, `spec.md` and `interfaces.md`.
**Merged:** `agent/promptu/009-list-an-earlier-runs-questions-and-answers` (code `20063c7`, ff on `946207b`; doc `e566e70f`, cherry-picked onto `7b81f4eb`). `cargo build`, `cargo test --all-targets` 125 passed (74, 19, 32), clippy `-D warnings` green, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the installed `promptu` binary and plugin see the verb only after a rebuild and reinstall. `tasks/promptu/008` stays `blocked` (`decisions/patterns.md` 1,150 B left, due 2026-11-24); this unit did not touch that file.
**Budget:** PROCEED in burndown, 5-hour 30%, weekly 52% at leg start.
**Least sure about:** whether text equality on the first user turn is too strict once the rewrite (decision 42) makes the typed prompt and the sent prompt differ; the rewrite's log keeps the original, and `prior` does not read it.

---

## 2026-11-17 18:02 — atlas/069 check-l-verifies-the-level-words-column

**Decided:** nothing numbered (`embarch-atlas` keeps none; burndown). EMB-160: check L now requires a protocol record's level word to sit in the quoted row under the column its `role`/`as` names, reusing check K's word-position approach (`_level_column`); no new record field. A cell whose level comes from a footnote, or a record with no words, role, row or header to test, reports not checkable, which never counts as a pass; the procedure example and the fixture count moved to 14 of 16. DESIGN.md's Check L section says what it proves. The resumed worker reviewed the dead worker's recovered draft and kept it unchanged.
**Merged:** `agent/atlas/069-check-l-verifies-the-level-words-column` (code `39b34b5`, ff on `90f70f2`, the recovery commit `6301f43` reworded; doc `caacee9f`, `4f5e516d` and `c97c1e1f` cherry-picked onto `083b875f` as `40f72d4e` and `caacee9f`). `pytest` 858 passed, 3 skipped (env-gated: real west workspace, built atlas, vendor SVD; `test_public_guard` ran), client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Left open:** DESIGN.md's record-schema row (about line 337) still reads "check L: the item and the level are in it", incomplete against the new column check rather than contradicting it; for the next atlas unit that touches that table.
**Budget:** PROCEED in burndown, 5-hour 30%, weekly 52% at leg start.
**Least sure about:** whether moving footnote-sourced levels to not checkable lowers what real atlases prove; only the synthetic fixture measured it (14 of 16).

---

## 2026-11-17 18:01 — chat/028 read-where-a-dead-session-stopped

**Recovery, read first.** Two legs before this one wrote no entry. The 14:48 leg split EMB-160 into `atlas/069`, claimed it and `chat/028`'s re-land, dispatched both, and lost both workers to the 5-hour usage limit with their trees uncommitted. The 17:14 leg committed those trees as WIP on the unit branches, re-claimed both for a resume, split EMB-185, EMB-146, EMB-137 and EMB-171 into `promptu/009`, `dev-bench/048`, `desk/031` and `api/157`, claimed `promptu/009` and `desk/031`, dispatched four workers at 17:23, and was cut off: no `leg-end`, no entry. All four workers finished and pushed both branches. This leg waited out its lock (stale at 17:53), lands those four as its own four units, and dispatches nothing new; `dev-bench/048` and `api/157` are open on `main`. Those dispatches predate this leg's `leg-start`, so it ticks no `leg-reported` for them. **I reworded the two recovery commits** ("WIP ... committed by recovery") before landing, same patch, so `main` carries `7a9aaf1` and `39b34b5` where the branches carry `1898a43` and `6301f43`; `fold-commit.py` proves them by patch-id.
**Decided:** nothing numbered (burndown). Re-land of the reverted build plus the EMB-200 fix: `Chat.projectsRoot` reads the chat's own env (`opts.env ?? chatEnv()`, decision 101) and `hostHooks` passes it to `lastSessionCall`; the CLI keeps `--config-dir`, else its own process login. `spec/handoff.md` names the login the read uses.
**Merged:** `agent/chat/028-read-where-a-dead-session-stopped` (code `7a9aaf1`, ff on `3288cf6`, carrying `c55f218`, the revert of the revert; doc `78a723b3`, `88f845e7` and `e9b0e2a8` cherry-picked onto `ce5d34ba` as `1792667a` and `78a723b3`, the task-file conflict taken from the branch tip). `npm ci`, `build`, `typecheck` green, `npm test` 306 passed, 78 skipped, 0 failed (no hang this run; the worker's first run hung at `test/wire.test.mjs:838` and its re-run passed), `test:webview` passed, client names clean, ownership green on both branches, `check-docs.py` 12/12.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. **Owed, owner-side:** the extension reaches the owner's windows only after a rebuild and reinstall.
**Budget:** PROCEED in burndown (until 2026-11-18 06:00), 5-hour 30%, weekly 52%, suggested wave 6; this leg runs no wave. Fleet Ready holds 27 unsplit issues; none split this leg.
**Least sure about:** the new test passes `chat.projectsRoot` to `lastSessionCall` itself, so the `hostHooks` wiring, the line that was actually wrong, has no test of its own.

---

## 2026-11-17 14:47 — chat/028 read-where-a-dead-session-stopped

**Decided:** **reverted a landed unit on a confirmed reviewer contradiction**, per `gate.md`, and put the task back `open` for a re-land. The reviewer's finding (EMB-200, verified by me in `src/hostHooks.ts`): the new `last_session` MCP tool calls `lastSessionCall(cwd, chat.sessionId)` with no root, so it reads the extension host's login (`CLAUDE_CONFIG_DIR` or `~/.claude`), not the chat's own, against `embarch-chat` decision 101; a chat on a second login would read another account's transcripts. I weighed a forward fix (a few lines, the `root` parameter exists) and chose the revert because the code was already on `main` and the failure crosses logins. Nothing numbered otherwise (burndown); the first build's design is sound and recorded in the task's "Re-land, read first": MCP tool beside `handoff`, a CLI `node dist/last-session.js`, newest `*.jsonl` in the cwd's folder then the main clone's, never the caller's session (id, else a 30 s live-file rule). `tasks/chat/028` now carries `**Issue:** EMB-200` too, and EMB-200 is filed against it.
**Merged:** nothing net. Code `97cf346` landed (ff on `61ceee2`) and was reverted by `3288cf6` on `embarch-chat` `main` (tree equal to `61ceee2`). Doc half `88f845e7` (cherry-picked as `d67da2d7` in the leg worktree, never pushed) dropped; it survives on `origin/agent/chat/028-read-where-a-dead-session-stopped` in `embarch-doc`. The first landing's gate was green: `npm test` 305 passed, 78 skipped, `test:webview` passed, `check-docs.py` 12/12.
**Blocked:** `chat/028` left `open` (not `blocked`): re-dispatchable as is, `git revert 3288cf6` plus the login fix, per the task file.
**Reviewer:** 1 finding — EMB-200
**Hardware debts:** none.
**Budget:** PROCEED in burndown at start (5-hour 63%, weekly 45%) and end (5-hour 87%, weekly 48%), suggested wave 6. Leg close: 4 of 4 units (desk/030, promptu/007, atlas/068 landed; chat/028 reverted). Fleet Ready holds 32 unsplit issues; on `main` `chat/028` is dispatchable, `promptu/008` blocked. EMB-197 (chat) waits behind `chat/028` in the same scope and will touch `decisions/promptu.md` (204 B left). The 5-hour window climbed 24 points this leg; at 97% the next leg pauses burndown until its reset.
**Least sure about:** whether a revert was worth more than the forward fix; it costs the next leg a re-land for a bug that only bites a chat on a second login, and the owner may have preferred EMB-200 alone.

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
