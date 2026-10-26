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

## 2026-10-26 04:00 — api/142 the client and the enroll result say when an enrol moved a role

**Decided:** nothing beyond the worker's new decision 87 (`embarch-api/decisions/hardware-selection.md`,
index row): `EnrollProbeResponse` in `embarch-core-client` gains `displaced`, `vacated` (`EnrolledBoard`)
and `vacated_kept`, all `Option` + `#[serde(default)]` + skipped when `None` (decision 58's rule; the
bare body re-serialises byte-identical, tested), and a shared `moved_roles_note()` that `enroll-probe`
and the MCP tool append; their JSON adds the three fields and `moved` only when a role moved. Read the
shared-crate diff before merging: additive; only Core builds that type by struct literal, and Core has
its own. **One supervisor fix on top, `9e4ca14`:** the new field's doc comment cited "`embarch-api`
decision 85" (the open desk) for the omit-when-absent rule; it now cites 87. Decision 87 landed in
`hardware-selection.md`, not the reserved `client-crate.md`, as the filing note asked; no file entered
reserve. **Filed `tasks/ui/091`** (the Enroll tab names a moved role) from the worker's drop. **My slip:**
I pushed the agent branch with a redundant `-f`; it was a fast-forward onto the worker's `7d0f859`, so
nothing was rewritten.
**Merged:** `agent/api/142-enroll-response-surfaces-a-moved-role` (code `9e4ca14`, ff onto origin/main
from `7e6d88c`, worker commit `7d0f859` plus the citation fix; doc `45b8f577`, cherry-picked from
`1654d56f`). Gate re-run on the merge, against topology `62c188d`: build, `cargo test --workspace` 262
pass, clippy `--workspace --all-targets -D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; no live enrol that moves a role was run. Not deployed: the MCP binary and CLI
on this machine predate this unit.
**Budget:** PROCEED, weekly 59.2%, wave 6.
**Least sure about:** `moved_roles_note()` words a `vacated` row with `vacated_kept` absent as "its row
is removed"; that reads Core decision 87's omission as "not kept", which holds only while Core always
sends `vacated_kept` alongside `vacated`.

## 2026-10-26 03:57 — topology/059 a probe moved to another chip family is refused by name before any attach

**Decided:** nothing beyond the worker's new decision 44 (`embarch-topology/decisions/validation.md`,
index row): additive `hardware::check_requested_chip(&EnrolledBoard, &str)` (pure; case-insensitive,
trimmed; empty either side passes) and `hardware::validate_serial_for_chip(serial, chip)`, which finds
the row, compares, and only then opens the probe; a differing chip is a downcastable
`RequestedChipMismatch` naming probe, enrolled role or bench board, both chips, "Nothing was attached"
and the `enroll_probe` fix. `validate_serial`/`validate_serial_timed` untouched; read the shared-crate
diff before merging, additive only. **Dispatched topology half only**, by my note: Core's four call
sites are filed as **`tasks/core/111`** from the worker's drop (`hardware.rs:180`, `:391`, `live.rs:93`,
`:141`). In-unit compaction as dispatched: `spec.md`'s "What each consumer owns now" split verbatim
into `embarch-topology/spec/consumers.md` (spec 81.7%, out of reserve), struck off `tasks/topology/060`'s
`Compacts:` line; 060 stays blocked on `decisions/enrollment.md` (243 B left, due 2026-11-01), now
waiting only on `suite/046`. **Leg start, for the record:** `inbox/` empty; `validate dev-bench` (MCP):
probe `001057729826` not attached, not a mismatch, so `api/059`, `dev-bench/035`, `dev-bench/038` stay
`open`; `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`); overdue ledger re-read, nothing
payable (`suite/030` blocked on `tasks/doc/045`, `study-designer/026` unpark unmet, `doc/031` owner's);
atlas still undispatchable (`tasks/doc/089`). Dispatched `api/142`, `core/106`, `topology/059`, `ui/083`
at once; all four reported within 11 minutes.
**Merged:** `agent/topology/059-moved-probe-refused-as-chip-mismatch` (code `62c188d`, ff onto
origin/main from `7c1ef59`; doc `9f827af8`, cherry-picked from `de40e3e7`). Gate re-run on the merge:
build, `cargo test --all-features` 108 pass, clippy `-D warnings` clean (default and all features),
wire-only build and clippy (`--no-default-features --features software,wire`) clean, client names
clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none until `core/111` lands; then a flash through a probe enrolled on another chip
family, on the bench, is the verify-only check.
**Budget:** PROCEED, weekly 58.5% at leg start, 59.1% here, wave 6.
**Least sure about:** the comparison assumes a project's `chip` and an enrolled `chip` spell the family
the same up to case; a `_cpuapp`-style variant would be refused once Core calls this, and `core/111`
carries that check.

## 2026-10-26 03:38 — ui/082 a live run's badge says running and counts its step

**Decided:** nothing beyond the worker's paragraph under decision 33 (`embarch-ui/decisions/
live-study.md`): Live Study reads the job status once before following and seeds the session's
status and `total_steps` from it, then broadcasts a `status` frame (a browser that connected before
the read returned otherwise kept a `pending` snapshot with no frame due to correct it); a completed
step promotes `pending` to `running` even when that read failed; a seed never replaces a terminal
status, `interrupted` included (api/137's decision 48). `follow_study` itself unchanged, no inbox
drop. `stub_core.py` now holds its terminal frame 1.5 s so the browser check can see the running
window. `spec.md` and `open.md` untouched. **Leg close, for the next leg:** this leg ran
`umbrella/092`, `desk/004`, `core/110`, `ui/082`, all green on first gate, all reviewers clean.
New in the queue: `api/142` (client mirror and enroll text for core decision 87; `client-crate.md`
is in reserve). `inbox/` is empty. Bench still unattached (`validate dev-bench` at leg start). Overdue
ledger: nothing payable. `suite/046`-`049` still open and unannounced: no leg has opened a window
for them. `fold-day.py --status`: 2026-10-26 still today, two rollable days not rolled. Not
deployed anywhere: live Core, the desk on :4891 and the UI binary all predate this leg's units.
The owner's uncommitted `embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone,
which is why `git pull --rebase` in `embarch-fleet` refuses at step 0; fetch and push still work.
Two slips, both harmless: `leg-dispatch` was ticked after the four spawns returned rather than
right after spawning, and two `fold-commit.py` calls were refused (my Edit anchored on a heading
time the previous fold had restamped) before anything was committed; no push was chained to them.
**Merged:** `agent/ui/082-live-run-badge-says-running-and-names-its-step` (code `5928bdb`, ff onto
origin/main from `ca0caf8`; doc `ec2653df`, cherry-picked from `394add5a`). Gate re-run on the
merge, against api `7e6d88c`: build, `cargo test` 184 pass / 4 ignored (+5 in the other test
targets), clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the badge fix is measured against `stub_core.py`, not a live Core run.
**Budget:** PROCEED, weekly 57.5%, wave 6.
**Least sure about:** the worker saw one browser run show `pending` before it added the seed
broadcast and could not attribute it at the time; the broadcast is its best explanation, and four
later runs passed, but the earlier failure was not reproduced and then fixed.

## 2026-10-26 03:37 — core/110 the enroll response reports the row a probe vacated

**Decided:** nothing beyond the worker's new decision 87 (`embarch-core/decisions/enrollment.md`,
index row; `interfaces/topology.md`'s `POST /probes/enroll` row): Core calls
`hardware::enroll_reporting` (public since `topology/065`) and the response gains `displaced`,
`vacated` and `vacated_kept`, each omitted when empty (`vacated_kept` only alongside `vacated`),
built by a pure `enroll_response(board, upserted)` so role-to-role is tested without a probe. Read
the wire diff before merging: additive only. Wire check (worker's, from the first dispatch, re-stated):
`embarch-api`'s `EnrollProbeResponse` mirror and every enroll type in api and ui carry no
`deny_unknown_fields`, so nothing breaks; the fields are silently dropped there until a client half
lands. **Drained the worker's inbox drop as `tasks/api/142`** (client mirror plus enroll CLI/MCP
text names the moved role; a UI half after it), with a note that `client-crate.md` is in reserve.
Second dispatch of this task: the first bounced on the topology gap last leg.
**Merged:** `agent/core/110-enroll-response-reports-vacated-row` (code `9b0d016`, ff onto origin/main
from `fb993b1`; doc `bc3d0263`, cherry-picked from `9aa520e1`). Gate re-run on the merge, against
topology `7c1ef59`: build, `cargo test` 292 pass / 2 ignored, clippy `-D warnings` clean, client
names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** native Windows build of `embarch-core` (owner runs it); no live enrol run. Not
deployed: the live Core still returns the old shape.
**Budget:** PROCEED, weekly 57.5%, wave 6.
**Least sure about:** `displaced` and `vacated` serialise the whole `EnrolledBoard`, so a future
field on that topology type appears in Core's enroll response without any Core change or decision.

## 2026-10-26 03:36 — desk/004 a tile from an earlier day proposes its gap against that day's current Harvest

**Decided:** nothing beyond the worker's new decision 62 (`embarch-desk/decisions/desks.md`, index
row; decision 41's fetch schedule amended): the sync loop re-reads each earlier day that has an open
tile every 10 minutes (`PAST_DAY_REFRESH_MS`, marked chosen; one read per distinct day, never per
tile; a failed day backs off the same interval). ✓ re-reads the tile's day before computing what to
send: with no typed override it sends the fresh gap; with a typed override (decision 61) it sends
what was typed but refuses once with a 400 naming the old gap, the new gap and the typed hours when
the re-read moved the gap, and the next ✓ goes through. A failed Harvest read at ✓ falls back to
the stored read, as before. One spec refresh row. This closes the double-log the review found
(time typed into Harvest the next morning, dated the day before).
**Merged:** `agent/desk/004-past-day-harvest-gap` (code `670debc`, ff onto origin/main from
`da354f8`; doc `4594195f`, cherry-picked from `099a4e01`). Gate re-run on the merge: build,
`cargo test` 125 pass, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Live debt: a ✓ against real Harvest with an entry added after the day
ended has not run. Not deployed: the desk service on :4891 is the owner's to rebuild, and it now
carries `desk/003`, `ui/090`'s counterpart and this.
**Budget:** PROCEED, weekly 57.5%, wave 6.
**Least sure about:** the task's first Done box asked for "a test with a stubbed Harvest"; the worker
ticked it with pure-function tests (`past_days_due`, `gap_moved_under_override`) because
`harvest.rs` hardcodes its base URL, so the refresh and the ✓ re-read are not driven end to end.

## 2026-10-26 03:35 — umbrella/092 doctor reads a busy bench as busy, not broken

**Decided:** nothing beyond the worker's amendment of decision 19 (`decisions/dev-bench-firmware.md`,
"busy bench" paragraph): a `503` or `409` from `GET /dev-bench/hello` is a new `HelloOutcome::Busy`;
check 13 gives a Warn with new code `busy`, quoting Core's plain-text body whole (Core names the
holder in prose and has no structured holder field to cite, so it is quoted, not parsed); check 11's
bench leg says "busy (HTTP …)" for the same two. `502`, other statuses and transport errors keep the
generic skip; `404` still passes as not plugged in. `--json` keys unchanged. Built on top of
`umbrella/091`'s dirty-checkout arm with nothing to rebase. **Leg start, for the record:** `inbox/`
was empty. `validate dev-bench`: probe `001057729826` not attached, not a mismatch; the three bench
tasks stay `open`. `fleet-hardware.py`'s buffer is 48 days stale (`--refresh` crash is
`tasks/doc/041`). Overdue ledger re-checked: `suite/030` and `study-designer/026` are blocked with
their unpark conditions unmet, `doc/031` is the owner's; nothing payable. Dispatched `core/110`,
`ui/082`, `umbrella/092`, `desk/004` at once; all four reported within eight minutes and gated green.
**Merged:** `agent/umbrella/092-doctor-check-13-reads-hello-503-409-as-busy` (code `9d27e12`, ff onto
origin/main from `c75200d`; doc `0d229bf3`, cherry-picked from `129ff9c4`). Gate re-run on the
merge: build, `cargo test` 237 pass, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run; the busy arm is unit-tested on injected outcomes with realistic
bodies, never against a live Core holding `hw_lock` or `study_lock`.
**Budget:** PROCEED, weekly 57.5%, wave 6.
**Least sure about:** quoting Core's body whole couples doctor's output to Core's prose, so a Core
rewording changes what doctor prints without any test failing on either side.

## 2026-10-26 03:20 — ui/090 the tile dialog sends hours only when a person changed them

**Decided:** nothing beyond the worker's decision 59 (`embarch-ui/decisions/shell.md`, index row in
`decisions.md`): `assets/desk.js` keeps the prefilled hours and `computed_hours` on the field
(`data-orig`, `data-computed`) and sends `hours` in `PATCH /tiles/{id}` only when the value differs
from the prefill; a new "Use computed" button fills `computed_hours` and sends `"hours": null`, and
typing again cancels that. One clause in `spec/tabs.md`; `spec.md` and `open.md` untouched. This
completes `desk/003` (desk decision 61): until the owner rebuilds the desk service on :4891, the
live Desk tab still talks to the old desk. **Leg close, for the next leg:** this leg ran
`topology/065` (filed mid-leg), `api/137`, `umbrella/091`, `ui/090`; `core/110` bounced on the
topology gap and is `open` again with its plan written in the task file, so it is the cheapest
dispatch in the queue. Now unblocked by this leg: `ui/082` (live-run badge; must render the new
`interrupted` status, api/137's entry) and `umbrella/092` (check 13, on top of 091). Filed
`tasks/doc/091` (owner's). `inbox/` is empty. Overdue ledger: still nothing payable. Bench still
unattached. `fold-day.py --status`: 2026-10-26 is 32 unfolded units (fold it after midnight), two
rollable days, not rolled. The owner's uncommitted `embarch-fleet/templates/.claude/commands/
fleet-watch.md` was left alone. The `embarch-fleet` checkout's `main` has no upstream, so a bare
`git push` there fails: push `origin main` explicitly. `core/110`'s code branch (at base, no commits)
is still on `embarch-core`'s remote; not deleted by hand.
**Merged:** `agent/ui/090-tile-hours-only-when-typed` (code `ca0caf8`, ff onto origin/main from
`e111712`; doc `a9debee9`, cherry-picked from `6a6f0d21`). Gate re-run on the merge, against topology
`7c1ef59` and api `7e6d88c`, no workaround: build, `cargo test` 186 pass / 4 ignored, clippy `-D
warnings` clean, client names clean, `check-docs.py` 11/11. The worker's scratch UI and mock desk
ports (:48901, :48911) are closed.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the browser check ran against the worker's mock desk, not the real one
(needs the owner's rebuild of :4891).
**Budget:** PROCEED, weekly 57.4%, wave 6.
**Least sure about:** "Use computed" is offered on every tile because the tile JSON does not carry
`hours_override`, so the dialog cannot tell whether an override exists; sending `null` when none
does is harmless but the button reads as if there were one.

## 2026-10-26 03:17 — umbrella/091 doctor and uninstall verdicts say what the docs say

**Decided:** nothing beyond the worker's amendments of decisions 19 (`decisions/dev-bench-firmware.md`)
and 25 (`decisions/setup-reversal.md`). `setup --uninstall` exits 1 naming each attempted step that
failed, and `setup`'s own failed-install arm exits 1 too (decision 7's fallback). Check 1's
suite-manifest mismatch is a Warn, code `manifest-mismatch` kept (decision 14 already said so).
Check 13: a local `X-dirty` against a bench flashed from clean `X` is a Warn, new code
`dirty-checkout`, fix line "commit or stash, or rebuild with `west build -p always`"; dirty against
dirty on one commit still passes as `match`, and decision 19 says what that does not prove. Check 2's
`wsl-host`/`remote` fix line now carries `install --bind <addr>` from `recommended_bind_address`,
the call `setup` uses, with a test that fails if they diverge. `--json` keys unchanged. Built green
with **no** feature workaround, against topology `7c1ef59` and api `7e6d88c`: the first consumer
proof that `topology/065` fixed `main`. `umbrella/092` (check 13 reading hello's 503/409 as busy)
touches the same check and lands on top of this. **My slip, recorded:** my first `fold-commit.py`
for this unit was refused (entry not yet written) and a pipe masked it, so the chained `git push`
sent the cherry-picked doc commit `c508a4a6` to `origin/main` a few minutes ahead of this fold, a
false `leg-fold` tick was written, and the Slack "landed" line went out before the fold. Nothing was
lost; `tasks/doc/086` is this exact class, and the last leg hit it too.
**Merged:** `agent/umbrella/091-doctor-and-uninstall-verdicts-match-their-docs` (code `c75200d`, ff
onto origin/main from `1e52116`; doc `c508a4a6`, cherry-picked from `3c830dd4`). Gate re-run on the
merge: build, `cargo test` 236 pass, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run; check 13's `dirty-checkout` arm is unit-tested against a temp git
repo, never against a flashed bench.
**Budget:** PROCEED, weekly 57.4%, wave 6.
**Least sure about:** `dirty-checkout` is a Warn, so an unflashed firmware edit now shows only as a
warning; and a dirty checkout against a bench flashed from an *older* commit still reports `stale`.

## 2026-10-26 03:15 — api/137 a follow ends on an unknown or interrupted study instead of waiting forever

**Decided:** nothing beyond the worker's amendment of decision 48 (`decisions/study-events.md`): a
404 from the opening poll is fatal even with a stream open (Core's SSE route opens for any id, so
nothing would ever arrive), now a typed `UnknownStudyError` in `embarch-core-client`; any other
opening-poll failure still follows live. `interrupted` joins `is_terminal_status`. CLI: unknown id
exits non-zero naming it; `interrupted` exits 1 with `success: false` in `--json` (shared with
timeout, told apart by the summary), while `failed` still exits 0. MCP `study_watch`: unknown id
errors at once; `interrupted` returns `complete: true`, `status: "interrupted"` and a new `note`.
`study_status`'s description lists `interrupted`. Read the shared-crate diff before merging:
additive type, one more terminal status, one new early `Err`. **Consumer effect, by reading:**
`embarch-ui`'s Live Study (`live_study.rs` ~:996-1060) now ends a watch of an interrupted study with
status `interrupted` and re-reads the record, where it used to wait forever, and shows an unknown id
as "watching this study stopped". `ui/082` (the live-run badge, same path) should render
`interrupted`; not filed separately, since 082 is open and names this task. The ui and umbrella
gates below build against this commit.
**Merged:** `agent/api/137-study-follow-ends-on-unknown-or-interrupted-study` (code `7e6d88c`, ff
onto origin/main from `9ba2714`; doc `ea13842d`, cherry-picked from `0839bc01`). Gate re-run on the
merge, against topology `7c1ef59`: build, `cargo test` 261 pass (workspace default-members), clippy
`-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run; the mock Core's 404 and `interrupted` replies are modelled on the
task's reading of Core, not captured from a live one.
**Budget:** PROCEED, weekly 57.4%, wave 6.
**Least sure about:** the worker's unknown-id `--json` output is the existing `error_result` object,
not the `summary` line the task's "Done when" asked for; its test checks content, not shape.

## 2026-10-26 03:13 — topology/065 the wire-only build compiles again and enroll_reporting is public

**Decided:** filed this task myself, mid-leg, from three inbox drops written by three of this
leg's four workers within minutes of each other: `topology/063` (`6732ad6`, last leg) re-exported
`Upserted` from `hardware/mod.rs` unconditionally while the struct is `#[cfg(feature =
"hardware")]`, so **every consumer built without `hardware` was red on `main`**: `embarch-api`'s
`embarch-core-client`, `embarch-ui`, `embarch-umbrella`. Last leg's gate ran topology's default
features and `--all-features` and neither is the `software,wire` set those consumers use. The same
landing left `validate::enroll_reporting` unreachable (private module), which bounced `core/110`.
Landed this first, ahead of the three finished consumer units, so their gates run against a fixed
`main` instead of a workaround (the workers used a feature flag or a HEAD~1 copy). Read the
shared-crate diff before merging: one `cfg` on the re-export and a documented `hardware::
enroll_reporting` wrapper beside `enroll`; no type, wire or dependency change. The `software,wire`
build is now named as a gate item in topology's `Cargo.toml` feature comment, nowhere enforced;
filed `tasks/doc/091` (owner's: `gate.md` should say how a shared crate's gate covers its consumers'
feature sets). **`core/110` reclaimed to `open`**, not logged as a blocked unit: its worker committed only a
`## Blocked` note in the task file (cherry-picked here) with a ready plan; its code branch is at
base. It is dispatchable now. **Leg start, for the record:** `inbox/` was empty. `validate
dev-bench`: probe `001057729826` not attached, not a mismatch; the three bench tasks stay `open`.
`fleet-hardware.py --refresh` crashes (`AttributeError` at :214), already `tasks/doc/041`. Overdue
ledger: nothing payable (`suite/030`, `doc/031` owner's; `study-designer/026` paid under cap).
Atlas still undispatchable (`doc/089`). Dispatched `ui/090`, `core/110`, `api/137`, `umbrella/091`
at once, then this.
**Merged:** `agent/topology/065-wire-only-build-and-enroll-reporting-reachable` (code `7c1ef59`, ff
onto origin/main from `6732ad6`; doc `321c78d6`, cherry-picked from `34774116`). Gate re-run on the
merge for default, `--all-features` and `--no-default-features --features software,wire`: build,
`cargo test` 15 / 110 / 21 pass, clippy `-D warnings` clean on all three; client names clean;
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 56.6% at leg start, 57.4% here, wave 6.
**Least sure about:** the gate item is a `Cargo.toml` comment; nothing makes the next topology unit
build the `software,wire` set, and the merge gate in `gate.md` does not name it either, so the same
class can land again.

## 2026-10-26 02:52 — umbrella/090 embarch-umbrella/open.md out of reserve by wording only

**Decided:** the unpark (see topology/063's entry): flux rewritten to `no` with the check-15
bullet (decision 56, `binary_sha256`) fenced off, since only that bullet is being rewritten by
queued work; target was the 3,920 B reserve line, not the task's stale "under 90%". The worker
shortened two bullets and retired none: the decision-26 `--prune` bullet now links
`decisions/prune-policy.md` for its detail, and the check-5 parenthetical keeps its conclusion
(Core enumerates the probe itself once udev rules are back, so `no-probe-found` cannot occur) in
one clause. Every `Hardware debt:` sentence untouched. Reviewer confirmed no unresolved item or debt
dropped; the `study_results/` 803 MiB measurement is now gone from `embarch-umbrella/` but still in
`embarch-api/decisions/target-json.md`. Human question: yes, `spec.md` alone answers current work.
Task retired. **Leg close, for the next leg:** `inbox/` is empty. New and open this leg: `core/110`
(enroll response carries the vacated row), `ui/090` (Desk tab sends hours only when typed),
`topology/064` (`link-declares.md` 11,155 B in reserve, due 2026-11-09, `In flux: no`). The overdue
ledger has **no payable entry left**: `suite/030` and `doc/031` are the owner's and
`study-designer/026` has nothing to pay. Next due 2026-11-01: `topology/060` (a verbatim split of
decision 41 out of `enrollment.md` needs no unpark) and `dev-bench/040`. `suite/046`–`049` still
open and unannounced. Bench still unattached. `fold-day.py --status`: two rollable days, not rolled;
2026-10-26 becomes foldable after midnight. One false `leg-fold` tick at about 02:49 (a
`fold-commit.py` refusal masked by a pipe); the fold itself landed a minute later. Scratch worktree
`.worktrees/smp-check/` (detached core, used to test Core against the smp branch) removed at leg end.
The owner's uncommitted `embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/umbrella/090-compact-open-md` (doc `a053cd7e`, cherry-picked from `bcbdf34d`; no
code). `open.md` 4,048 to 3,672 B (71.7%). Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the check-13, check-15, decision-51 and check-5 debts in `open.md`
stand.
**Budget:** PROCEED, weekly 56.0% at leg start, 56.6% here, wave 6.
**Least sure about:** the "no payable overdue entry" call rests on the previous legs' reading of
`study-designer/026`; I did not re-read that file's bullets myself.

## 2026-10-26 02:51 — desk/003 a tile's hours are set by hand only when a person typed them

**Decided:** nothing beyond the worker's decision 61 (`embarch-desk/decisions/cockpit.md`): ✓ writes
a new `Tile.sent_hours` instead of `hours_override`; `reopen_tiles_of_entry` (deleting a ✓'d entry)
clears `sent_hours` and keeps a typed override; `PATCH /tiles/{id}` with `"hours": null` clears the
override, an absent key leaves it; an approved tile still reports what it sent. Decision 57's
self-close now reads only the typed override. Tiles already stored with a ✓-written override keep it
until cleared with `null`; no migration. Filed the worker's drop as `ui/090` (the tile dialog sends
`hours` only when edited, and offers "use computed"): until it lands, opening a tile in the Desk tab
still freezes its hours.
**Merged:** `agent/desk/003-hours-set-by-hand` (code `da354f8`, ff onto origin/main from `41d9ff2`;
doc `16a5dc4b`, cherry-picked from `b1f03b2a`). Gate re-run on the merge: build, `cargo test` 124
pass, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not deployed: the desk service on :4891 is the owner's to rebuild.
**Budget:** PROCEED, weekly 56.0%, wave 6.
**Least sure about:** the one test sets the state ✓ leaves and calls the real reopen function; the
Harvest-calling handlers (`approve_tile`, `remove_entry`) are not driven end to end.

## 2026-10-26 02:49 — smp/001 an upload that moves without progressing ends, naming its offsets

**Decided:** nothing beyond the worker's rewording of decision 9 (`embarch-smp/decisions.md`, now
"five places it deliberately differs"): within `max_stalls` (5), an upload is abandoned on five
replies at one offset (the old rule), five replies that do not pass the highest offset reached since
the last restart, or more than five restarts to offset 0; the error names the last ten offsets. One
restart still re-sends `len`/`image`/`upgrade` without `sha`. Public API unchanged (`Error::Upload`
reused). Read the diff before merging, since Core consumes the crate: error paths only, request
building untouched. **I ran Core's `cargo test` against the smp branch before pushing** (scratch
detached worktree at `.worktrees/smp-check/`, siblings linked): 290 pass / 2 ignored. I set
`embarch.md`'s merge-gate row for `embarch-smp` to "yes, since `smp/001`": this unit is the first the
fleet gated there. `spec.md`'s status line now names Core's `POST /bootload` as the built consumer.
First `history/smp.md`.
**Merged:** `agent/smp/001-upload-ends-without-progress` (code `fe68a41`, ff onto origin/main from
`9236362`; doc `f9138c24`, cherry-picked from `13f400b2`). Gate re-run on the merge: build,
`cargo test --all-features` green, clippy `-D warnings` clean (default and all features), client
names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; no real MCUboot has answered this client yet (`open.md`).
**Budget:** PROCEED, weekly 56.0%, wave 6.
**Least sure about:** the five-restart bound is assumed, not measured, like the stall count before
it; a real bootloader that legitimately restarts more than five times in one upload would now fail.

## 2026-10-26 02:46 — topology/063 a probe moving roles never loses an enrolled row silently

**Decided:** nothing beyond the worker's decisions 42 (`decisions/link-declares.md`: a probe moving
role to role, or role to bench board, reports the role it vacated in `Upserted { displaced, vacated,
vacated_kept }`; the vacated role keeps `name`/`chip`/link facts with its probe half cleared, the
`NoProbeBound` state; a moved probe inherits link facts only under the same role) and 43
(`decisions/storage.md`: `save_at` writes `enrollment.toml.tmp`, `sync_all`, renames over the store).
Read the shared-crate diff before merging: `enrollment::upsert` was replaced by `upsert_reporting`,
but `enrollment` is a private module and nothing in core, api, ui or umbrella called it; `enroll` keeps
its signature, `enroll_reporting` and `hardware::Upserted` are additive; no serialized type changed,
so no wire bump. Filed the worker's drop as `core/110` (enroll response carries the vacated row).
`enrollment.md` was not written, so `topology/060`'s split did not fire; decision 42 put
`link-declares.md` in reserve (11,155 B) and the worker filed `topology/064` (`In flux: no`, due
2026-11-09). **Leg start, for the record:** `inbox/` was empty. `validate dev-bench`: probe
`001057729826` not attached, not a mismatch; the three bench tasks stay `open`. Overdue ledger's
payable head was `umbrella/090`, unparked with flux `no` and the check-15 bullet fenced off. Four
workers dispatched at once: `umbrella/090`, `topology/063`, `smp/001` (the fleet's first `smp`
unit), `desk/003`; all four reported within about four minutes.
**Merged:** `agent/topology/063-enrollment-never-loses-a-row` (code `6732ad6`, ff onto origin/main
from `93a83d9`; doc `14571823`, cherry-picked from `49114c93`). Gate re-run on the merge: build,
`cargo test --all-features` 105 + 5 pass, clippy `-D warnings` clean (default and all features),
client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none run; decision 43 assumes NTFS rename atomicity on the Windows Core host,
untested.
**Budget:** PROCEED, weekly 56.0%, wave 6.
**Least sure about:** decision 27 still says re-enrol carries link facts "keyed on probe serial";
decision 42 narrows that to the same role and says so, but 27's own wording now reads slightly stale.

## 2026-10-26 02:32 — umbrella/084 decisions/projects.md out of reserve by a verbatim split

**Decided:** the unpark (see study-designer/076's entry): flux rewritten to `no` for a verbatim split,
decision 26's wording fenced off. The worker moved decision 26 (`study_results/` retention and
build-directory pruning, the file's in-flux half and off its "integrating a firmware repo" title)
verbatim into a new `embarch-umbrella/decisions/prune-policy.md`, routed from `decisions.md`, with
`spec.md`'s cite repointed. Reviewer confirmed byte-verbatim and all five Must-not-delete facts intact.
I repointed the two `embarch-api/decisions/target-json.md` links that meant decision 26 in this fold
(the worker had dropped `inbox/umbrella-084-repoint-decision-26-links.md` for them; answered and
deleted). One dated line in `history/umbrella.md` still links `projects.md` for 26; left, history is
append-only. The reviewer guessed `decision-size-baseline.json` would now flag decision 26 as OVER;
`check-doc-size.py --decisions` does not list it. Task retired. **Leg close, for the next leg:**
filed `api/141` from the core/109 drop (`inbox/` now empty). New this leg and open: `ui/089`
(`spec.md` 9,099 B, in reserve, due 2026-11-09, `In flux: no`) and `api/141`. Overdue ledger's
payable head is now `umbrella/090` (`open.md` 4,048 B; its reserve line is 3,920 B because the 1,200 B
floor dominates a 5 KB file, so it is in reserve, not closable as the last leg guessed). The four
`suite/046`–`049` tasks are open and unannounced; each reads as a multi-repo feature, and splitting one
into sequenced single-repo tasks (§8) may serve better than running it by hand as a last unit. Bench
still unattached. `fold-day.py --status`: two rollable days, not rolled. The owner's uncommitted
`embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/umbrella/084-compact-projects-md` (doc `b91291cd`, cherry-picked from `2b890be4`;
no code). `projects.md` 11,116 to 6,782 B (55.2%), `prune-policy.md` 4,801 B. Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 55.4% at leg start, 56.0% here, wave 6.
**Least sure about:** the name `prune-policy.md` holds a decision whose retention half (`study_results/`)
is already Core's count-bounded sweep, not a prune; it is accurate for what 26 defers, but a future
retention decision would have to choose between it and a new file.

## 2026-10-26 02:30 — ui/084 a saved study is never written into another repo or stripped of its taps

**Decided:** nothing new in ui's decisions; the fixes apply 14 and 40. The firmware_version
write-back takes the repo captured at submit time instead of re-reading the open project; an
unparseable `_embarch_ui_taps` sidecar refuses the load with a `400` naming the file (a missing one
still recovers from `Study.streams`); `.eap` delete scans every declared block, resolved or not, and
the stem when none resolve. **Spec fix by me, twice.** The worker made room in `spec.md` (3 B under
its reserve line) by dropping two clauses from the destructive-edit invariant. I restored "leaving the
form filled" on its branch before landing (`092fc6f5`); the reviewer then found the second, "a
directory it cannot fully read is not permission to delete", stated nowhere else in `embarch-ui/`. I
restored it in this fold, which puts `spec.md` at 9,099 B, in reserve, and filed `ui/089` (`In flux:
no`, due 2026-11-09, split-first toward the existing `spec/` files). The reviewer's drop is
answered by this fold and deleted.
**Merged:** `agent/ui/084-saved-study-not-written-elsewhere` (code `e111712`, ff onto origin/main
from `aa5ffda`; doc `02f058da` cherry-picked from `5c59f1c1`, plus my `092fc6f5`). Gate re-run on the
merge: build, `cargo test` 181 pass / 4 ignored, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** 1 finding — inbox/ui-spec-restore-unreadable-dir-clause.md
**Hardware debts:** none.
**Budget:** PROCEED, weekly 55.4%, wave 6.
**Least sure about:** the write-back test calls `update_saved_firmware_version` with repo A's path
directly rather than switching projects mid-`submit_run`; it proves the function no longer reads the
open project, not the whole run path.

## 2026-10-26 02:28 — core/109 POST /study refuses an empty record magic

**Decided:** nothing beyond the worker's decision 86 (`decisions/study-record.md`): `validate_study`
calls study-designer's `validate_record_checks` after `validate_taps` and returns its Display text as
the `400`; the trace CSV's step-name blanking delegates to `csv_cell_ok` (so CR and LF now blank too);
the warn for a capture whose records do not all verify reads "no records found, or has records that
do not verify", since `all_verified()` is false at zero records. This closes study-designer/072's
least-sure point: decision 81's refusal now guards `POST /study`. The worker dropped
`inbox/api-zero-record-wording.md` for api's "0 of 0 records verified" print; left for the next drain.
**Merged:** `agent/core/109-call-validate-record-checks` (code `fb993b1`, ff onto origin/main from
`35d9859`; doc `1b1242e7`, cherry-picked from `91f07e4d`). Gate re-run on the merge, against
study-designer `3ec19b9`: build, `cargo test` 290 pass / 2 ignored, clippy `-D warnings` clean,
client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 55.4%, wave 6.
**Least sure about:** a saved study with an empty magic that Core used to accept is now refused at
`POST /study`; nothing in the suite writes one, but a hand-written study on the owner's disk would
start failing with the crate's error text.

## 2026-10-26 02:26 — study-designer/076 GPIO records are named in Core's trace CSV

**Decided:** nothing beyond the worker's decision 82 (`decisions/streams.md`): `OutpostManifest`
reads schema 2's `devices` and `functions` as `#[serde(default)]` maps, `label()` names kind 9 from
`devices` and kind 10 from `functions` with bit 0 masked, an unnamed address stays empty. Read the
shared-crate diff before merging: two new pub fields, no struct-literal construction outside the
crate's own tests (grepped core, ui, api), no serialized type changed, so no wire bump. A GPIO-bearing
cross-decoder fixture is noted in decision 82 as `embarch-outpost`'s; no drop filed. **Leg start, for
the record:** `inbox/` was empty. `validate dev-bench`: probe `001057729826` not attached, not a
mismatch; the three bench tasks stay `open`. Overdue ledger head was `umbrella/084` (the entries
ahead are owner-only or have nothing to pay); unparked with flux `no` for a verbatim split of
decision 26. Four workers dispatched at once: `umbrella/084`, `core/109`, `ui/084`,
`study-designer/076`; all four reported within about four minutes.
**Merged:** `agent/study-designer/076-outpost-manifest-gpio-names` (code `3ec19b9`, ff onto
origin/main from `b19c841`; doc `cd255701`, cherry-picked from `bce31f0`). Gate re-run on the merge:
build, `cargo test` and `--all-features` green, clippy `-D warnings` clean (default and all
features), client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; the tests use literal JSON, not a capture from GPIO-traced firmware.
**Budget:** PROCEED, weekly 55.4%, wave 6.
**Least sure about:** the reviewer could not find the generator's `0x%08x` key format in the
outpost docs, only in the task's citation of `gen_outpost_manifest.py`; the two agree by reading,
and no fixture proves it.

## 2026-10-26 02:15 — suite/004 reversals index and studies guide out of reserve by wording only

**Decided:** ran `suite/004` with my own hands after its §4 window: announced 01:40 (`ts`
`1793000429.737099`), no reply in the thread or the channel by 02:10, started 02:11. Re-read both
files' flux reasons first: the reversals index had one edit since 2026-09-25 and the studies guide
none, so neither was being rewritten; rewrote `In flux:` to `no`. Wording only, no split, no new
file. `embarch-decision-reversals.md` 9,633 to 9,004 B (the reserve line is 9,011 B under the
1.2 KB floor, not the 9,216 B the task carried): every shape and row number and every citation kept,
one duplicate `umb` decision 17 link dropped. `suite/studies-guide.md` 24,783 to 22,872 B: §3a/§3b
fix-history compacted (decision 45's misreport story, the pre-decision-46 address-path gate, a stale
`tasks/dev-bench/009` pointer, a restated log-sink sentence, a client-firmware command list), and a
sentence that a decision-46 insertion had split mid-way repaired. Human question, adapted to a
guide: can it alone still tell a study author what to do? Yes; every instruction and dated
measurement stays. Task retired. **Leg close, for the next leg:** `inbox/` is empty. New and open:
`core/109`, `umbrella/092`, `api/140` (the last has no `Size debt due:`, legal while it is `open`).
Overdue ledger's payable head is now `umbrella/084` (`projects.md` 1,172 B left) and `umbrella/090`
(`open.md` at 79.1%, below its reserve line, so probably closable rather than payable); `suite/030`
and `doc/031` stay the owner's, `study-designer/026` has nothing to pay. No `suite` task announced
or parked. Bench still unattached. `leg.md`'s worktree link table omits `embarch-smp` for
`embarch-core` (core path-depends on it; the link already exists under `.worktrees/embarch-core/`).
`fold-day.py --status` shows two rollable days (2026-09-28, 2026-09-29); not rolled. The owner's
uncommitted `embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** supervisor commit, doc `267dc107` (no code). Gate on it: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 54.4% at leg start, 55.2% here, wave 6.
**Least sure about:** the reversals index clears its reserve line by 7 bytes, so the next shape
edit puts it back in reserve; the studies guide has 168 B of margin.

## 2026-10-26 01:50 — umbrella/079 decisions/install.md out of reserve by a verbatim split

**Decided:** the unpark (see api/139's entry): flux rewritten to `no` with decision 28 fenced off,
and the dispatch note allowed either a split along a real seam or shortening. The worker split:
decisions 21 (`setup --dry-run`) and 25 (`setup --uninstall`) moved verbatim to a new
`embarch-umbrella/decisions/setup-reversal.md` (2,734 B), routed from `decisions.md`; 3, 4, 5, 14,
28, 54 stay. Decision 14 stayed because `embarch-api` and `embarch-ui` docs cite `install.md` for it
and the worker could not fix links outside its scope; nothing cited 21 or 25 by file. Reviewer
confirmed the move is byte-verbatim apart from the new file's header and that every reference
(bare "decision 21" in umbrella code comments and `spec.md`) still reads right. Task retired.
**Merged:** `agent/umbrella/079-compact-install-md` (doc `4a7007e0`, cherry-picked from
`e1015583`; no code). `install.md` 12,071 to 9,660 B (78.6%). Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; decision 28's Windows verification debt stands.
**Budget:** PROCEED, weekly 54.4%, wave 6.
**Least sure about:** the new file name `setup-reversal.md` covers a preview (21) and an undo (25);
it is accurate for both, but a third setup decision would have to choose between it and
`install.md` on a seam the name only half states.

## 2026-10-26 01:49 — core/108 the hello lock test can no longer reach a real bench

**Decided:** nothing. The worker added a seam rather than a decision: `hello_handler` now calls
`hello_with(state, resolve_dev_bench_port)`, and the test passes its own resolvers (one that panics
if reached, for the refused-`409` case; one that errors, for the free-link case, asserting the hold
is `HELLO_HOLDER` while it runs and gone afterwards). No test calls `hello_handler` any more. The
`AppState` comment in `src/api.rs` now states the order `study_lock` then `hw_lock`. No changelog
fragment (not reader-facing). This closes core/104's warning: the owner's native Windows build may
now run `cargo test` with the dev-bench plugged in, as far as this test goes; the reviewer did not
audit the other `resolve_dev_bench_port` callers (`src/main.rs`, `src/api.rs`, `src/study.rs`) for
test reachability.
**Merged:** `agent/core/108-hello-lock-test-no-bench` (code `35d9859`, ff onto origin/main from
`8e29f06`; doc `696488bb`, cherry-picked from `6cb252ca`, task close only). Gate re-run on the
merge: build, `cargo test` 289 pass / 2 ignored, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 54.4%, wave 6.
**Least sure about:** whether any other test reaches a resolver that enumerates real USB; this unit
only fixed the one the core/104 reviewer named.

## 2026-10-26 01:47 — api/139 the exchange fields an older Core does not send are Option

**Decided:** nothing beyond the worker's application of decision 58 (`decisions/client-crate.md`,
"Applied api/139" paragraph): `bytes_read`, `echo_seen`, `written`, `port_lost` are `Option` and
skipped when absent, `wire_notes` says "this Core did not say whether the line was written" for an
old silent reply, and `FlashResponse.erased` is `Option<Vec<_>>` too, because an empty list after
`erase: true` would claim "nothing erased", which Core never said (side effect: flash JSON carries
`"erased": null` against an old Core rather than omitting the key). Decision 82's "false means
unknown" caveat removed. Read the shared-crate diff before merging; grepped `embarch-ui` and
`embarch-umbrella` myself: neither names either type or any of the five fields. The worker filed
`api/140` (`decisions/client-crate.md` now 11,581 B, in reserve, `In flux: no`). **Leg start, for
the record:** drained two inbox drops as `core/109` and `umbrella/092` (`4e507c0f`). **Announced
`suite/004`** (`ts` `1793000429.737099`, 01:40, window closes 02:10; plan: shorten
`embarch-decision-reversals.md` and `suite/studies-guide.md` under their reserve lines by wording
only, no split), task set `open` with the `ts` in it; I mean to run it as this leg's last unit.
Unparked `umbrella/079` (overdue ledger head after the owner-only and announce-gated entries) with
its flux rewritten to `no`, decision 28 fenced off. `validate dev-bench`: probe `001057729826` not
attached, not a mismatch; the three bench tasks stay `open`. `fleet-hardware.py --refresh` still
crashes on the unattached DUT (`tasks/doc/041`, owner's). Three workers dispatched at once:
`umbrella/079`, `core/108`, `api/139`; all three reported within about three minutes.
**Merged:** `agent/api/139-exchange-fields-option` (code `9ba2714`, ff onto origin/main from
`dd49a1f`; doc `3bca3c75`, cherry-picked from `4c412021`). Gate re-run on the merge: build,
`cargo test --workspace` green, clippy `-D warnings` clean, client names clean, `check-docs.py`
11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the fields are still tested on JSON bodies only (core/098's bench debt
covers the Core side).
**Budget:** PROCEED, weekly 54.4%, wave 6.
**Least sure about:** `"erased": null` in the flash JSON is a visible output change for any script
that read `erased` as a list; nothing in the suite does, but the owner's own tooling was not checked.

## 2026-10-26 01:34 — ui/078 embarch-ui/spec.md out of reserve by a verbatim split

**Decided:** unparked `ui/078` (overdue since 2026-10-13, the ledger's oldest payable entry; the
five ahead of it are owner-only `suite/030` and `doc/031`, `study-designer/026` with nothing left to
pay, and `suite/004`, which needs the §4 announcement). Its `In flux: yes` was ui/077's single
paragraph edit of 2026-09-29; I rewrote it to `no` and kept the protection on the `Must not delete`
list. The worker split rather than squeezed: `## Verification technique` moved verbatim into a new
`embarch-ui/spec/verification.md` (the pattern `spec/tabs.md` and `spec/capture-rendering.md`
already set), and `spec.md` keeps the "Tested in Rust, never looked at" rule and a pointer. Task
retired. **Leg close, for the next leg:** two drops wait in `inbox/` —
`core-call-validate-record-checks-and-csv-cell-ok.md` (core, from study-designer/072) and
`core-doctor-check-13-reads-hello-503-409-as-busy.md` (**umbrella**, despite its name, from
core/104). New this leg and open: `api/139` (exchange fields as `Option`, decision 58) and
`core/108` (a core/104 test that would reach a real bench). The overdue ledger's payable head is now
the three umbrella parks (`079` `install.md` 217 B left, `084`, `090`), each `In flux: yes` and
worth reading against the split-first rule with `--decisions`; `suite/004` still needs its §4
announcement before anyone runs it, and nobody has posted one. Bench still unattached. No `suite`
task announced or parked. The owner's uncommitted
`embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone. One false tick: a
refused `fold-commit.py` (entry not yet written) exited without stopping the `&&` chain behind it, so
`leg-fold` was ticked once for a fold that had not happened — the `tasks/doc/086` defect, live.
**Merged:** `agent/ui/078-compact-ui-spec` (doc `32ede839` the split and `3f644d7d` the state line,
cherry-picked from `dabb1a2b`, `5c85d5a3`; no code). `spec.md` 9,516 to 8,986 B. Gate on the merge:
11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 53.8% at leg start, 54.3% at the last fold, wave 6.
**Least sure about:** the split file is classified `legacy` with a 25 KB cap by `check-doc-size.py`,
like its two siblings; a `spec/` directory that grows by splits is a seam nobody has decided is the
right home, it is just the one that already existed.

## 2026-10-26 01:32 — core/104 the dev-bench gate and hello take the locks they share

**Decided:** nothing beyond the worker's amendments to decisions 4/14/15 (`decisions/platform.md`):
the identity gate takes `hw_lock` for its probe attach and drops it on return (held across into the
outpost pre-flight it would deadlock, since the pre-flight takes the lock itself); hello holds
`study_lock` as `GET /dev-bench/hello` for its whole handshake, released by a drop guard; a study
arriving meanwhile is refused `409` naming hello; the order is always `study_lock` then `hw_lock`,
and the reviewer confirmed no route takes them the other way round. **I filed `core/108` from the
reviewer's below-bar notes**: the new test that calls `hello_handler` with a free link "fails later
(no bench here)", but on a machine with a dev-bench attached it would resolve the real port, attach
the real probe and send `Hello` — a host test that can drive hardware; plus an `AppState` comment
in `src/api.rs` that still calls the two locks separate. Not reverted: harmless on every machine
the fleet gates on (WSL has no USB). Two follow-up drops left in `inbox/` for the next drain:
`core-doctor-check-13-reads-hello-503-409-as-busy.md` (scope umbrella despite its name) and
study-designer/072's `core-call-validate-record-checks-and-csv-cell-ok.md`.
**Merged:** `agent/core/104-dev-bench-gate-and-hello-take-locks` (code `8e29f06`, ff onto
origin/main; doc `da2dd1a8`, cherry-picked). Gate re-run on the merge, against study-designer
`b19c841`: build, `cargo test` 289 pass / 2 ignored, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two. (1) Native Windows build of `embarch-core`, owner's, from the main
checkout — and run it before `core/108` lands only with the dev-bench unplugged if it includes
`cargo test`. (2) Hello's `503` is tested through the gate function only; reaching it through the
handler needs a bench to resolve the dev-bench port.
**Budget:** PROCEED, weekly 54.2%, wave 6.
**Least sure about:** the gate now waits on `hw_lock` before a study starts, so a study queued
behind a long flash answers `503` where it used to start; that is the task's intent, but doctor's
check 13 and any caller that retried on `502` have not been checked against it.

## 2026-10-26 01:30 — api/138 signal_exchange and signal-exchange say what Core saw on the wire

**Decided:** the worker's amendment to decision 82 (`decisions/failure-reporting.md`: a `port_lost`
reply exits 5, checked before exit 3, because 3 reads as "send it again" for a line that already
ran; a silent reply stays 4 and its notes carry the port identity and core state; the MCP result
gains `wire_notes`). Read the shared-crate hunk (`embarch-core-client`) before merging: additive, no
struct-literal construction in `embarch-ui` or `embarch-umbrella`. **I filed `api/139` from the
reviewer's below-bar note, reading it as a real contradiction of decision 58**
(`decisions/client-crate.md`: a field Core may not yet send is `Option`, never a fabricated default):
`bytes_read`, `echo_seen`, `written`, `port_lost` are bare defaults, so against the live Core (older
than core decision 85 until the owner redeploys) every exchange reports `written: false` and
`bytes_read: 0` beside real text. Filed rather than reverted: nothing reads the fields yet but this
crate's own CLI and MCP text, and `wire_notes` says nothing false.
**Merged:** `agent/api/138-signal-exchange-prints-wire-fields` (code `dd49a1f`, ff onto
origin/main; doc `d5e90265`, cherry-picked). Gate re-run on the merge, against study-designer
`b19c841`: build, `cargo test --workspace` green, clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the fields are tested on JSON bodies only, never against a Core that
sends them (core/098's bench debt covers the Core side).
**Budget:** PROCEED, weekly 54.2%, wave 6.
**Least sure about:** whether `FlashResponse.erased` (api/134, a bare `Vec` default) breaks
decision 58 the same way; `api/139` asks its worker to decide and record it.

## 2026-10-26 01:28 — study-designer/072 a step name cannot shift CSV columns; zero records is not all verified

**Decided:** nothing beyond the worker's decision 81 (`decisions/seals.md`: one crate rule
`csv_cell_ok` refuses a comma, quote, CR or LF; `Sample::to_csv_row` blanks such a name rather than
dropping the sample, the GATT renderer still refuses through the same predicate, `build_study`
refuses with `BuildStudyError::NameBreaksCsv`; `validate_record_checks` refuses an empty magic;
`RecordReport::all_verified()` is false at zero records). Read the shared-crate diff before merging:
additive except `all_verified()`'s meaning at zero records, which is the task's point; no consumer
matches `BuildStudyError` exhaustively; no serialized type changed, so no wire bump (reviewer agreed
against decision 12). **Leg start, for the record:** drained two inbox drops from `core/098` as
`api/138` and `atlas/022` (`84992d10`), then folded `atlas/022` into `atlas/014`, of which it was a
subset, and retired `core/091` (its only file, `core/decisions/surfaces.md`, 11,042 B, under the
reserve line) in `4cd0a885`. `validate dev-bench`: probe `001057729826` not attached, not a mismatch;
`api/059`, `dev-bench/035`, `dev-bench/038` stay `open`. Atlas still undispatchable (`tasks/doc/089`,
owner's). Four units dispatched at once: `ui/078` (overdue ledger, unparked), `api/138`, `core/104`,
`study-designer/072`.
**Merged:** `agent/study-designer/072-csv-step-name-and-empty-record-check` (code `b19c841`, ff onto
origin/main; doc `5f42a4ab`, cherry-picked from `ea1934ad`). Gate re-run on the merge: build,
`cargo test` and `--all-features` green, clippy `-D warnings` clean (default and all features),
client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none.
**Budget:** PROCEED, weekly 53.8% at leg start, 54.2% here, wave 6.
**Least sure about:** the empty-magic refusal guards nothing until Core calls
`validate_record_checks` at `POST /study`, and Core's own step-name blanking still misses CR; both
are the worker's drop `inbox/core-call-validate-record-checks-and-csv-cell-ok.md`, left for the next
leg's drain.

## 2026-10-26 01:13 — umbrella/009 decisions/bind.md out of reserve by compacting decision 22's retired halves

**Decided:** unparked `umbrella/009` (overdue since 2026-10-06, the ledger's oldest payable entry).
`--decisions` showed `bind.md` is one decision: 22 is 10,713 B, 92% of the file, pinned over the
4 KB per-decision cap, so `DOC-BUDGET.md`'s own worked example applied (compact that entry, or make
it two decisions); the flux line was rewritten to say so. The worker compacted the settled parts
only (the split-history header, and the wording of the retired 22(b) firewall and 22(c) disk-space
entries, each keeping its retirement reason, the 809 MiB measurement and its losing argument), and
did not split 22: it is one argument with amendments, and `reporting.md` and `user-guide.md` link it
by number. Task retired: its only `Compacts:` file is out of reserve. **Leg close, for the next
leg:** two drops wait in `inbox/`, both from `core/098` (see its entry); the overdue ledger's payable
head is now `ui/078` (`embarch-ui/spec.md`, 724 B left, its flux reason a month old) and the three
umbrella parks (`079` `install.md` 217 B left, `084`, `090`); `suite/030`, `doc/031` stay the
owner's, `suite/004` needs the §4 announcement; `suite/046`-`049` are open and unannounced. Bench
still unattached. No `suite` task announced or parked. The owner's uncommitted
`embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/umbrella/009-compact-docs` (doc `3b923ec1`, cherry-picked from `bc5988ac`; no
code). `bind.md` 11,555 to 10,904 B (88.7%). Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; 22's own (check 17's Fail branches against a real narrow-bound Core)
stand.
**Budget:** PROCEED, weekly 52.8% at leg start, 53.6% at the last fold, wave 6.
**Least sure about:** the `DOC-COMPACTION-PASS.md` human question was answered for what runs (yes,
`spec.md`'s doctor table says built versus unbuilt) but no pass on `spec.md` itself was made.

## 2026-10-26 01:12 — core/098 an exchange says what happened on the wire

**Decided:** nothing beyond the worker's decision 85 (`decisions/signal-exchange.md`: the answer adds
`bytes_read`, `echo_seen`, `written`, `port_lost`; a read error after a successful write is a `200`
with `port_lost` and the partial text, never a `500`, because a state-changing command that answered
`500` was sent again; a mid-line `until` match reads on to a line end, a 40 ms quiet gap or the
deadline; a silent reply adds `port_identity` and a `core_state` decoded from two `DHCSR` reads
through the guarded attach, never halting; a spent `port_wait_ms` puts the same `core_state` in its
`409`; decision 79 amended by a pointer only, being over the per-decision cap). Read the wire-type
diff before merging: additive, and the client's `SignalExchangeResponse` has no
`deny_unknown_fields`. **Two supervisor edits:** (1) a commit on the code branch (`de5e82a`) fixed
eleven code comments citing "decision 98", the task number, to decision 85, the `api/132` /
`chat/003` class; re-gated after. (2) In the fold, one sentence in decision 85 from the reviewer's
below-bar note: on a silent reply or a spent port wait the probe attach runs after the deadline, so
79's bound grows by one guarded attach (unmeasured), about 5 s of headroom left at the 10 s cap.
**Merged:** `agent/core/098-exchange-says-what-happened-on-the-wire` (code `de5e82a`, ff onto
origin/main, worker commit `c0b665c` beneath it; doc `6735517f`, cherry-picked from `c9209ff8`). Gate
re-run on the merge, after study-designer/070 landed: build, `cargo test` 286 pass / 2 ignored,
clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two, from this unit; the task is retired with its bench box unticked and this is
the record. (1) Bench check of decision 85 on a real board: an exchange to a board held in reset
(`S_RESET_ST`) and to one halted by a debugger (`S_HALT`) each name the state; a command that drops
the CDC ACM port answers `port_lost` with its first output line; the guarded attach leaves a running
core undisturbed; 40 ms `QUIET_GAP` is enough for a real shell. (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 52.8%, wave 6.
**Least sure about:** the 40 ms quiet gap is a guess applied to every prompt-terminated exchange; a
shell slower than one UART burst between a marker and its line end would now be cut at 40 ms rather
than at the deadline. Follow-ups are two drops left in `inbox/` for the next leg's drain:
`api-signal-exchange-prints-wire-fields.md` and `atlas-shell-prints-exchange-wire-fields.md`.

## 2026-10-26 01:08 — api/123 signal-exchange fails loudly when no reply came back

**Decided:** nothing beyond the worker's amendment to decision 82 (`decisions/failure-reporting.md`:
`signal-exchange` exits 3 when `--until` was given and never seen, 4 on zero bytes (outranks the
others, with or without `--until`), 5 on `truncated`, each with one stderr line and the reply still
printed; a deadline stop without `--until` is normal and exits 0; `--json` stdout unchanged but the
codes apply; `--clean` is a Rust port of the atlas `live.clean()`, taking the prompt from `--until`).
In the fold I added one clause to decision 50 (`decisions/surface.md`), whose "the exit code stays a
single `1`" read as absolute; it now names 82's carve-out. The reviewer raised that below its bar.
Not fixed: decision 50 still says exit-code granularity is "open again in open.md", and `open.md`
has had no such bullet since September (pre-existing, not this unit's).
**Merged:** `agent/api/123-signal-exchange-cli-silent-on-no-reply` (code `e5da1c4`, ff onto
origin/main; doc `fcbc89c4`, cherry-picked from `d40d36fa`). Gate re-run on the merge, after
study-designer/070 landed: build, `cargo test --workspace` green, clippy `-D warnings` clean, client
names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `core/098` (landing next) adds wire fields this CLI does not print yet; its
drop `inbox/api-signal-exchange-prints-wire-fields.md` is the follow-up.
**Budget:** PROCEED, weekly 52.8%, wave 6.
**Least sure about:** `--clean` matches the Python `clean()` on five fixtures only; a console with
other escape sequences could diverge from the atlas output without any test noticing.

## 2026-10-26 01:06 — study-designer/070 host-run study model

**Decided:** nothing beyond the worker's decision 80 (`decisions/study.md`: `HostStudy`,
`HostStep`, `HostAction` (`Exchange`/`Prompt`/`Instrument`/`Wait`) and `HostStepResult`, JSON only,
`deny_unknown_fields` on every type so no step can carry an expected value or range; `teardown`
validated like `steps` and runs to the end even when one of its steps fails; `Exchange.refused_on`
is a settled text marker that makes the step `Fail`, never a compared value; `MAX_HOST_STEPS` 128 and
five sibling caps, all assumed from one field sequence). **`HOST_TYPE_SCHEMA_VERSION` deliberately
not bumped** (still 19): nothing crosses the API-Core hop yet, and decision 80 hands the bump to the
Core unit that accepts `HostStudy`; the reviewer checked it against decision 12 and agreed. Read the
shared-crate diff before merging: additive (new module, re-exports, constants); grepped core, api,
ui and umbrella for glob imports or clashing names, none. **Leg start, for the record:** inbox empty;
`validate dev-bench`: probe `001057729826` not attached, not a mismatch (`api/059`, `dev-bench/035`,
`dev-bench/038` stay `open`); four units dispatched at once: `umbrella/009` (overdue ledger, unparked),
`study-designer/070`, `api/123`, `core/098`.
**Merged:** `agent/study-designer/070-host-study-model` (code `ba3ad46`, ff onto origin/main; doc
`30a18cdb`, ff). Gate re-run on the merge: build, `cargo test` and `--all-features` green, clippy
`-D warnings` clean (default and all features), client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. The fixture is the field PD source sequence (49 steps, 2-step teardown);
nothing runs it until Core accepts host studies.
**Budget:** PROCEED, weekly 52.8% at leg start, wave 6.
**Least sure about:** the new tests are `alloc`-gated, so plain `cargo test` skips them; a future
gate that runs only default features would never exercise decision 80's checks.

## 2026-10-26 00:51 — ui/074 embarch-ui/open.md off its cap by deleting settled halves

**Decided:** unparked `ui/074` (overdue since 2026-10-05; the ledger's oldest *payable* entry, the
three ahead of it being owner-only or parked with nothing payable). Same reasoning as `api/113`:
`DOC-BUDGET.md` names a role-capped 5 KB `open.md` as the case with no seam, so the pass deletes
answered halves and shortens nothing live; the flux line was rewritten to say so. The worker reached
4,366 B, not the 3,920 B floor, and stopped because the 11 remaining bullets are all live with their
own triggers; I accepted that (the task's Done-when allows a dated reason). It filed `tasks/ui/088`
(blocked, `In flux: yes`, due 2026-11-26) for the reserve that remains; 088 was free on `main`.
**Leg close, for the next leg:** the overdue ledger's payable head is now `umbrella/009`
(`decisions/bind.md`, split-first) and `ui/078` (`ui/spec.md`); `suite/004` (reversals,
studies-guide) is `suite` scope, so it needs the §4 announcement before anyone runs it; `suite/030`
and `doc/031` stay the owner's. Bench still unattached. No `suite` task announced or parked. The
owner's uncommitted `embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/ui/074-compact-ui-open` (doc `2d29cfa9`, cherry-picked from `cb4ecd14`; no code).
`open.md` 5,117 to 4,366 B: six settled halves removed, each checked by the reviewer against its home
(user-guide §3 / studies-guide §4, decisions 21, 34, 37, 38), and the Debug-level 0-vs-7,440-byte
result moved into decision 32 (`decisions/live-study.md`). Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; the bullets keep their own (stale-prefix replay, a refused flash
mid-run, the traced live Time chart).
**Budget:** PROCEED, weekly 52.3% at leg start, 52.7% at the last fold, wave 6.
**Least sure about:** `DOC-COMPACTION-PASS.md`'s human question went unanswered for `spec.md` — the
worker did not re-read it, so whether `spec.md` alone serves a newcomer to `embarch-ui` is unknown.

## 2026-10-26 00:51 — desk/002 fold and approve edges

**Decided:** nothing beyond the worker's decision 60 (`decisions/cockpit.md`: a fold goes only into a
strictly later real `YYYY-MM-DD` day, else 400 and nothing changes; every tile route refuses a tile id
whose date part is not a real day; ✓ with an empty note sends the target's and the folded tiles'
lines, oldest first; a folded row's `hours`/`computed_hours`/`captured_hours` report the gap it
carried, frozen at the fold, while `logged_hours` stays that day's Harvest — 3 h captured, 0.5 h
logged reports 2.5 h where it used to report 2.0). The reviewer checked the Desk tab's `desk.js`: ids
and fold targets come from the server, so nothing it sends is newly refused.
**Merged:** `agent/desk/002-fold-and-approve-edges` (code `41d9ff2`, ff onto `3f56975`; doc
`0f73bb27`, two commits cherry-picked from `6082323f`). Gate re-run on the merge: build, `cargo test`
123 pass, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not deployed: the desk service on :4891 is the owner's to rebuild.
**Budget:** PROCEED, weekly 52.7%, wave 6.
**Least sure about:** the fold refusal is tested at the store and `split_tile_id` level, not through an
HTTP call (no route harness exists); `/day/{date}` and other date-taking routes were not tightened.

## 2026-10-26 00:50 — api/134 flash results carry the erased ranges

**Decided:** nothing beyond the worker's change (`FlashResponse.erased: Vec<String>`,
`#[serde(default)]`, in the shared `embarch-core-client`; every flash result's JSON carries `erased`,
the CLI text appends `; erased <ranges>`; the `erase` descriptions follow `embarch-core` decision 84).
Read the shared-crate hunk before merging: additive, and no consumer builds `FlashResponse` by struct
literal (grepped `embarch-ui`, `embarch-umbrella`). In the fold I amended api decision 41
(`decisions/tool-wrapping.md`) by one sentence: it still required the description to say
"destructive full-chip erase", which decision 84 made false; the reviewer flagged it below its bar.
**Merged:** `agent/api/134-flash-print-erased-ranges` (code `765ff8e`, ff onto `2f3749b`; doc
`719a0d42`, two commits cherry-picked from `37012484`). Gate re-run on the merge: build, `cargo test`
green across the workspace (client 48), clippy `-D warnings` clean, client names clean,
`check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none of its own; decision 84's STM32G0B1VE bench check (core/096) still owed.
**Budget:** PROCEED, weekly 52.7%, wave 6.
**Least sure about:** only the client parse is tested; the `erased` key in the MCP and CLI JSON is
covered by compilation, not by a mock-Core test.

## 2026-10-26 00:49 — core/107 one timeout_ms covers an exchange's write and read

**Decided:** nothing beyond the worker's amendment to decision 79 (one deadline starts with the write;
the read gets what the write left, and always one read pass; the write's per-call port timeout is the
remaining budget; bound `timeout_ms` + one 50 ms poll + `port_wait_ms`; cap 10,000 and its 15 s
rationale unchanged). In the fold I moved core/097's "Measured: only against a fake port…" sentence
back onto the 097 amendment (the worker had re-homed it onto 107's paragraph, where it duplicated
107's own measured line) and marked 097's "read's own deadline starts after the write" as superseded.
**Leg start, for the record:** the previous leg (spawned ~00:30) died before any claim, tick or
commit; nothing to reclaim. Inbox empty. `validate dev-bench`: probe `001057729826` not attached, not
a mismatch; `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`. `fleet-hardware.py --refresh`
still crashes (`measured: None` on the dut entry, line 214) — `tasks/doc/041`, owner's. Four units
dispatched at once: `ui/074` (overdue ledger, unparked), `core/107`, `api/134`, `desk/002`.
**Merged:** `agent/core/107-exchange-twice-its-timeout` (code `476e3e7`, ff onto `3dba64b`; doc
`2fa9f645`, cherry-picked from `f93730a1`). Gate re-run on the merge: build, `cargo test` 280 pass /
2 ignored, clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two. (1) On a real CDC ACM port, confirm a blocking `write` honours the shortened
per-call timeout (folds into core/097's STM32G0 960-character check). (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 52.3% at start, 52.7% here, wave 6.
**Least sure about:** the new test's 250 ms slack is wall-clock, so a loaded CI host could flake it.

## 2026-10-26 00:28 — desk/001 Harvest and Linear reads page past their first page

**Decided:** nothing beyond the worker's decision 59 (a shared `take_capped` pages Harvest entries at
`per_page=100` to 2,000 per account and Linear's assigned issues at 50 a page to 500 per workspace;
both caps `[chosen]`; `POST /harvest/entries` and `GET /linear/mine` carry `truncated`, and a cut
entries answer notes `total_hours` is a lower bound; `/pickup`, the 45-day polish read and a day's
`logged_hours` ignore the flag). The fleet's first `desk` unit: linked `embarch-doc` and
`embarch-fleet` beside it at `.worktrees/embarch-desk/`; the assembler created `history/desk.md`.
**Leg close, for the next leg:** `ui/open.md` is 5,117 of 5,120 B and `ui/074` is parked, so any
`ui` worker that adds a bullet there must compact it inside its own unit; `chat/004` now holds
`embarch-chat/decisions/timeline.md` (12,144 of 12,288 B); the overdue ledger's next entries are
owner-only (`suite/030`, `doc/031`) or parked with nothing payable (`study-designer/026`), then
`ui/074`. `embarch-smp` has no links under `.worktrees/` yet. The owner's uncommitted
`embarch-fleet/templates/.claude/commands/fleet-watch.md` was left alone.
**Merged:** `agent/desk/001-connector-reads-past-first-page` (code `3f56975`, ff onto `880d970`; doc
`58b0ee4f`, cherry-picked). Gate re-run on the merge: build, `cargo test` 120 pass, clippy
`-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not run against the live APIs: Harvest `/time_entries` paging and Linear's
`viewer.assignedIssues` cursor follow the shapes `targets` and `scope_issues` already use, tested on
synthetic pages only. Not deployed: the desk service on :4891 is the owner's to rebuild.
**Budget:** PROCEED, weekly 51.1% at start; end figure in the leg's final report.
**Least sure about:** the HTTP paging loops themselves never ran; the tests drive `take_capped` with
canned pages, so a wrong `next_page`/`endCursor` read would pass every test.

## 2026-10-26 00:27 — chat/002 a background Agent's card shows the subagent's report

**Decided:** nothing beyond the worker's decision 90 (the card's result is the hand-back, read from
the `isMeta` peer line carrying `origin.handback` before the meta drop, falling back to the
subagent's last reply with `parent_tool_use_id`; the launch reply's `agentId` fills `tasks` so a
reload finds the card; the stream-json hand-back shape is marked assumed). `chat/003` rode in the
same branch, as it asked. **Worth the owner's eye:** trying to record a real hand-back, the worker
launched a subagent run with `--permission-mode bypassPermissions`; the auto-mode classifier refused
it ("Create Unsafe Agents") and the worker did not retry. Nothing in the landed diff launches a
process. The worker filed `tasks/chat/004` (blocked, `In flux: yes`, due 2026-11-02):
`decisions/timeline.md` is at 12,144 of 12,288 B.
**Merged:** `agent/chat/002-agent-card-shows-the-hand-back` (code `90c6707`, ff onto `82b82e0`; doc
`4b340782`, two commits cherry-picked onto `59712c51`). Gate re-run on the merge: `npm ci`, build,
typecheck, `npm test`, `test:webview` all green, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Owed, not hardware: record a hand-back on the live stream-json wire from an
owner session where a subagent calls SubagentHandback (written into the retired task and decision
90). Not installed: the `.vsix` is the owner's to rebuild.
**Budget:** PROCEED, weekly 51.1%, wave 6.
**Least sure about:** decision 90's primary path has never been seen on the wire, only in a
transcript; if stream-json never emits the hand-back line, the card shows the fallback (the
subagent's last reply), which a reload cannot rebuild.

## 2026-10-26 00:23 — core/097 a console exchange's write survives a throttling device

**Decided:** nothing beyond the worker's amendment to decision 79 (the write retries
`TimedOut`/`WouldBlock`/`Interrupted`/zero-length results until the request's `timeout_ms`, resuming
from the reported count, and past it the exchange fails naming how many bytes were taken; the port
timeout is `timeout_ms` for the write and back to 50 ms for the read poll). Retired the task with its
bench box unticked, as `core/096` was: the debt below is the record. Filed `tasks/core/107` from the
reviewer's below-bar note: the read's deadline now starts after the write, so one exchange can take
`2 × timeout_ms` plus `port_wait_ms`, past the 15 s client timeout decision 79's cap was sized under.
**Merged:** `agent/core/097-exchange-write-throttled-device` (code `3dba64b`, ff onto `0d712cd`; doc
`bae8d660`, cherry-picked). Gate re-run on the merge: build, `cargo test` 279 pass / 2 ignored, clippy
`-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** three, all from this unit. (1) On the STM32G0 Zephyr CDC ACM board (the field
board, not this bench): send a 960-character line through `POST /signals/{name}/exchange` with shell
echo on and `timeout_ms` ≥ 2000; the device's own byte count must be 960. (2) Confirm Windows
`serialport` honours `set_timeout` mid-session (assumed, not measured). (3) Native Windows build of
`embarch-core`, owner's, from the main checkout.
**Budget:** PROCEED, weekly 51.1%, wave 6.
**Least sure about:** the `set_timeout` switch between write and read is the whole fix on the real
port and only a fake port has exercised it; if Windows ignores a mid-session change the field bug is
untouched while every test passes.

## 2026-10-26 00:21 — api/113 embarch-api/open.md out of reserve by deleting answered questions

**Decided:** unparked `api/113` (overdue since 2026-10-01; the ledger's oldest *payable* entry, since
`suite/030` waits on the owner's `tasks/doc/045` and `doc/031` is owner-only). Its `In flux: yes`
argued against shortening live prose, but `DOC-BUDGET.md` names a 5 KB `open.md` as a role cap with
no seam, whose remedy is deleting answered questions, which shortens nothing live; the flux line was
rewritten to say so. **Leg start, for the record:** drained 42 inbox drops (`df57ce53`: api/133-137,
atlas/017-021, core/104-106, desk/001-004 and smp/001 as two new scopes, dev-bench/041-044,
outpost/026-027, study-designer/072-076, topology/061-063, ui/079-087, umbrella/091). Completed
`api/134`'s header (the worker's drop had no `State:`); reclassified `outpost/027` `none` to
`toolchain` (native_sim builds against a Zephyr tree no worktree carries). Day-fold of 2026-10-25
done by an `embarch-log-folder` (30,538 to 29,802 B), riding in this commit. Atlas still not
dispatched (`tasks/doc/089`).
**Merged:** `agent/api/113-compact-api-open` (doc `12c59b8d`, cherry-picked from `988469e7`; no code).
`open.md` 4,714 to 3,780 B, under the 3,891 B floor: five answered items went, with the facts that had
no other home moved first into decision 70 and `interfaces/config.md`. Gate on the merge: 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `validate dev-bench` at step 0: probe `001057729826` not attached, not a
mismatch; `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`.
**Budget:** PROCEED, weekly 51.1%, wave 6 (four units dispatched at once).
**Least sure about:** `interfaces/config.md` is now 10,063 B and `decisions/hardware-selection.md`
about 10.4 KB; both outside reserve today, but this pass moved bytes rather than removing them.

## 2026-10-26 00:00 — core/096 flash `erase: true` skips alias and option-byte regions

**Decided:** nothing beyond the worker's decision 84 (erase touches only non-alias, writable NVM
regions; every kept region is checked for a flash algorithm before anything is erased; `POST /flash`
answers `{flashed, chip, erased}`; never a chip-erase fallback, consistent with decisions 32 and
36). The API half (print the erased ranges) is the worker's drop `inbox/api-flash-print-erased-ranges.md`.
Filed `tasks/doc/090` (owner): `embarch-core` now path-depends on `../embarch-smp`, which
`.claude/leg.md`'s link table omits; the worker made the link itself and I left it in place at
`.worktrees/embarch-core/embarch-smp`.
**Merged:** `agent/core/096-flash-erase-skips-alias-regions` (code `0d712cd`, ff; doc `ec80c3d3`,
cherry-picked from `8f0b1ac2`). Gate re-run on the merge: build, `cargo test` 277 pass / 2 ignored,
clippy `-D warnings` clean, client names clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** two, both from this unit. (1) STM32G0B1VE bench check: write a non-erased word in
a partition the image does not cover, flash with `erase: true`, `mem-read` it back as `0xFFFFFFFF`,
confirm `erased` is `["0x08000000..0x08080000"]` and the image boots; the algorithm-selector check
was tested only on a synthetic memory map. (2) Native Windows build of `embarch-core`, owner's, from
the main checkout.
**Budget:** PROCEED, weekly 47.5%, wave 6.
**Least sure about:** my own `check-docs.py | tail -1 && fold-commit.py` let the chat/001 fold commit
over a red gate (the `| tail` masks the exit, `tasks/doc/086`'s shape, which I knew about): caught
before the push and amended (`7da4011c`). Run the gate unpiped before every fold.

## 2026-10-25 — 3 units

*Folded by the supervisor's fold agent on 2026-10-26: per-unit decision narrative, gate-re-run detail and "least sure about" reasoning went; git holds them.*

**Carry forward:**
- Leg start: first leg after a 26-day gap; drained all 50 inbox drops into the queue (`ee7d80c1`, numbers in its message; doc/089 added: `gate.md` has no Python bullet, so no `atlas` task was dispatched). Folded 2026-09-29 and rolled 2026-09-17 (`3030aed`).
- Linked `embarch-dev-bench` beside the doc worktrees (`.worktrees/embarch-doc/embarch-dev-bench`): clears the worktree-only `check-links` red on `decisions/pd-bench.md` (`tasks/doc/085`'s shape).
- Tasks filed: `topology/060` and `dev-bench/040` (both `blocked`, due 2026-11-01, split-first) for three reserve files the owner's 2026-10-06..13 commits left unfiled (`embarch-topology/decisions/enrollment.md`, `embarch-topology/spec.md`, `embarch-dev-bench/spec.md`), which the over-cap red had masked; `api/132` (new `zephyr.rs` comments cite decision 64, about retired config keys, a wrong citation `check-decision-refs.py` passes); `chat/003` (a CSS comment cites nonexistent decision 90; fold into chat/002).
- `study-designer/026` unparked (its condition fired 2026-09-17 on owner commit `685b691c`, which pushed `open.md` 327 B over cap; overdue since 2026-10-04, made `check-doc-size.py` red on main), paid, and re-parked `blocked` (nothing live payable; the debt stays overdue on a park).
- First `chat` unit: set up `.worktrees/embarch-chat/` with `embarch-doc`, `embarch-fleet`, `embarch-desk` links. `history/chat.md` created by the assembler. `tasks/chat/002` (hand-back card) now unblocked.
- Open caveats: api/122 checked against Zephyr's `dts.cmake` only, an existing test's expectation changed from empty-`Ok` to the new error (reviewer traced in-crate callers, not `embarch-ui`); chat/001's idle-turn case (CLI never starts a turn) unrecorded, decision 89 marks it assumed.
- Budget: PROCEED, weekly 47.5%, wave 6 throughout.

**Decisions made on the owner's behalf:** none beyond the workers' own: decision 86 (api/122: shortened `<board>.dts` stem accepted only for a one-SoC `board.yml`, refused for multi-SoC and for both stems present; "boards found, every candidate dropped" is `ScanError::AllBoardsDropped`, never `Ok(vec![])`) and decision 89 (chat/001: a CLI-sent `user` line is a `note` row, never an owner bubble; panel-written `turnOrigin: "sdk"` lines with no `origin` stay the owner's). Decision 75 plus the authoring decision's RunProtocol amendment and `interfaces/eap.md` carry what study-designer/026 removed from `open.md`.

### study-designer/026 open.md under its cap; main's doc gate green again
**Merged:** `agent/study-designer/026-compact-open-md` (doc `3f33bc0c`, `91294f77`, ff; no code). `open.md` 5,447 -> 4,473 B. Gate 11/11 green.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. `validate dev-bench` at step 0: probe `001057729826` not attached, not a mismatch; Core sees only J-Link `000852006107`. `api/059`, `dev-bench/035` stay `open`.

### chat/001 a message the CLI sends Claude is never an owner bubble
**Merged:** `agent/chat/001-cli-turns-are-not-the-owners` (code `82b82e0`, ff; doc `c25be23c`, cherry-picked from `98c6ec25`). Gate: build, typecheck clean, `npm test` 216 pass / 0 fail / 67 skipped (no `EMBARCH_DESK_BIN`), `test:webview` pass, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Not installed: the `.vsix` is the owner's to rebuild.

### api/122 zephyr-west accepts a single-SoC board's shortened `<board>.dts`
**Merged:** `agent/api/122-zephyr-west-single-soc-dts` (code `2f3749b`, ff; doc `c98c1a40`, cherry-picked from `e303a1f8`). Gate: build, test green, clippy `-D warnings` clean, `check-docs.py` 11/11.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none. Checked against Zephyr's `dts.cmake` source only, not a real build of a single-SoC board through `list_targets`; the field repo that reported it is the natural first use.
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
