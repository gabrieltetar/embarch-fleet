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

## 2026-10-29 14:41 — core/124 install over a registered Windows service rewrites in place

**Decided:** nothing suite-wide. The worker's core decision 106 (`decisions/platform.md`): on Windows, `install`
over a registered service **rewrites it in place** (stop, rewrite `ImagePath` as `"<exe>" run --bind <bind>`,
merge `Environment`, apply failure actions, start) rather than refusing with "uninstall first", because
uninstall-then-install is the route that dropped `EMBARCH_SIGNAL_BAUD`. A reinstall keeps every existing
`Environment` entry (prints their names, never values) and replaces `EMBARCH_TOKEN` only when one is set; fresh
installs and rewrites both run `sc failure reset= 3600` with five `restart/5000` actions. Linux and macOS
unchanged. `embarch-core/open.md` compacted 4,804 B to 3,918 B (out of reserve) to pay for the debt line, and the
worker struck it off `core/112`'s `Compacts:` line; 112 stays blocked for `probes.md` and `spec.md`.
**`tasks/umbrella/095` is now dispatchable**: its fix lines can say `install --bind` rewrites a registration.
**Leg context (next leg, read this first):** this leg started 14:24 at `64976739`, clean recovery (no claims, no
leg tree; the owner's own `embarch-atlas-wt` worktree on `fix/field-findings`, dirty since 2026-10-08, left alone).
**The owner answered the 2026-10-28 dream "do 1"** (settle `tasks/doc/089`); he had already landed it himself
(`2e28b74d`, gate.md's Python bullet), so `atlas` is dispatchable and this leg runs the fleet's first atlas unit.
Inbox: three owner drops filed as `tasks/suite/053` (retire done task files), `054` (shed built pieces from the
root proposals), `055` (triage pre-October tasks), each announced (`ts` `1793305738.327939`, `1793305739.311079`,
`1793305740.224299`, windows close 14:58-14:59). **`suite/030` is overdue on the size ledger and now unparked**
(`tasks/doc/045`): announced `ts` `1793305727.873799`, window closes 14:58:47, planned as this leg's last unit.
Bench: `dut` attached (probe `000852006107`), `dev-bench` not attached, so `api/059`, `dev-bench/035`, `038`
stay open. Spread sweep: nothing filed (2026-10-29 14:30) — the only source changed since the 2026-10-28 22:13
full sweep is `embarch-umbrella/open.md`, whose new bullet is already `umbrella/095` + `core/124`. Dispatched
three at once: `core/124`, `outpost/018`, `atlas/008`; `umbrella/095` held for this unit. 2026-10-28 day-folded
(32 units, by the log-folder), 2026-10-25 rolled; `check-client-names.py --suite --history` all 14 repos clean.
**Merged:** `agent/core/124-install-over-a-registered-service` (code `80dfa0d` on `85846c4`, doc `baec9822` on
`e0a59709`; both ff). Gate on the merge result: core build, clippy `-D warnings`, test 385 + 2 pass, client names
clean, `check-docs.py` 12/12, ownership `core` OK on both branches. **`cargo check --target
x86_64-pc-windows-msvc` could not run** (`hidapi`'s C build needs MSVC headers), so I read the `cfg(windows)`
hunks by hand for imports and bindings; nothing found. Owner's core checkout fast-forwarded.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, in `embarch-core/open.md`: (1) native Windows build, since the `cfg(windows)`
registry and `sc failure` code has never been compiled; (2) a live `install --bind` over the registered service,
checking `EMBARCH_SIGNAL_BAUD` survives and `sc qfailure` shows five restarts.
**Budget:** PROCEED, weekly 22.2% at leg start, wave 6.
**Least sure about:** the Windows half compiling at all: a Linux gate, a hand read and a reviewer are all it has
had, and `main` now carries it.

## 2026-10-28 — 32 units

*Folded by an `embarch-log-folder` subagent for the next leg's first unit, 2026-10-29: the per-unit narrative reasoning, gate-result detail, budget lines and "least sure about" prose went; every SHA, every reviewer line and every owed hardware debt is kept below, and git holds the rest.*

**Carry forward (read this first):**
- **The queue is dry outside `atlas`.** `queue-status.py` counted 19 dispatchable at the day's end and every one is an `atlas` task, skipped per `tasks/doc/089` (no atlas gate). The listener may keep spawning legs because the script counts atlas as dispatchable; that gap is the owner's to close. A dream was posted (`ts` `1793248372.130149`): settle `tasks/doc/089`, start the `toolchain` lane by a leg's own hands (13 tasks), plug in the bench. **If no reply has arrived and `inbox/` is empty, do not dream again and do not invent work: end after step 0.**
- **Bench:** Core up, no probes; `validate dev-bench` and `validate dut` both not attached (not a mismatch). `api/059`, `dev-bench/035`, `dev-bench/038` open. `fleet-hardware.py --refresh` still crashes (`tasks/doc/041`). Overdue size ledger: `suite/030` (owner-blocked), `doc/031` (owner-only); `study-designer/026` retired this day.
- **Nothing from this day is deployed:** the live Core, the installed `embarch-api`, `embarch-ui` and `embarch` all predate it (`suite/046`-`049`, `api/125`, `api/128`, `api/129`, `api/130`, `core/116`-`121`, `ui/100`). An `embarch` built before `suite/047` reads the new `--version` lines as a manifest mismatch (doctor checks 1 and 15), so rebuild umbrella together with api and core.
- **Suite-wide cross-repo designs approved by the supervisor under protocol §8, announced windows closed with no reply:** `suite/046` (bench board owns signals; topology decision 48, core 103, api 95), `suite/049` (SCPI instruments; topology 49, core 104, api 97), `suite/047` (every binary names its commit, install replaces a running binary, doctor check 18, core-log check renumbered 19; umbrella 57, api 93, core 100), `suite/048` (operator prompt step; core 105, api 99, `embarch-core-client`; the answer route is deliberately **not** lease-gated, anyone holding Core's token may answer, checked by prompt id; step `timeout_ms` capped at one hour). None is a wire-schema bump. `GET /study/{id}` on a finished host study now carries `host_result` rather than `result`.
- **Open filings:** `tasks/umbrella/094` (compact `open.md`, blocked `In flux: yes`, due 2026-11-11); `tasks/ui/101`, `core/123`, `api/149` were filed and landed same day. Decision-compaction by verbatim split is the default remedy that `DOC-BUDGET.md` allows even over `In flux: yes` (used for `chat/004`, `topology/066`). **88 task files with `State: done` remain in `tasks/`**, not bulk-retired (docs may link them).
- **Recurring failures likely to repeat:** (1) the fold's `&&` chain running past a refused fold through a `| tail` (three units named it: `api/128`, `ui/098`, `core/121`, `api/144`); a spurious `leg-fold` tick and Slack line go out before the real fold. (2) Workers leave the task's `State:` at `claimed` after ticking boxes (`tasks/doc/050`; workaround: commit `done` before the fold). (3) `git -C <repo> worktree add` with a relative path creates trees inside the repo; use absolute paths under `embarch/.worktrees/`. `embarch-api/.worktrees/embarch-api/` holds two 2026-09-13 symlinks, left alone. (4) The core gate flaked about one run in four on two capture-timing tests until `core/122` fixed them. (5) A worker can report a comment it did not write (`core/123`); only the reviewer's diff read caught it.
- **A leg killed at ~17:35 left four claims in flight;** recovered by re-landing pushed branches (`topology/068`, `api/144`) and committing dead trees as WIP and re-claiming them as resumes (`ui/100` `cc29076`, `core/122` `a24c7d7`). Whether the owner wants resume rather than block next time is unasked.
- **Open design questions the units left:** counting an ambiguous role-less-board `need` as met (`api/149`); the answer route being lease-open (`suite/048`); a 3 s server-side poll opening a UI session per running study (`ui/100`, nothing measured eight follows); `ui/101`'s "no uncaught JavaScript error" check reads `window.__errs`, which the page never installs, so it cannot fail. This fold also carried the 2026-10-26 day-fold (85 units; 268/268 SHAs, 85 reviewer lines, 27/27 debts) and `--roll` of 2026-09-28 and 2026-09-29.

**Merged** (one line per unit; code SHA on its base, doc SHA rebased from the worker's; all ff unless stated; each gated on the merge result: build/test/clippy `-D warnings`, client names, `check-docs.py` 11/11, ownership):
- `chat/004` timeline.md split by mission, verbatim (decisions 15, 16, 67, 68, 69, 74, 85 to `readouts.md`; 13,806 to 10,535 B): doc `4949d467` (worker `172bd8a0`) onto `043bf14d`; no code. Budget 9.2%. Leg 22:13 closed 4 of 4 (`api/149`, `core/123`, `ui/101`, `chat/004`); dream `ts` `1793248372.130149`.
- `ui/101` modal driven headless against a stub Core (no rendering bug found): code `f6da709` on `9f5461e`, doc `7265c7e9` (worker `a525b68d`) onto `611c567e`.
- `core/123` pacing comments say end of exchange (`mark_sent` renamed `mark_exchanged`; I finished the worker's placeholder comment): code `12192cc` on `5a310bb`, then fix `85846c4`; doc `10865fa0` (worker `ff11ac91`) onto `0610f8ff`.
- `api/149` ledger needs match a role-less bench board by enrolled name (api decision 98 amended, `ambiguous_needs`): code `0f1f0d4` on `124f461`, doc `138d1a05` on `266d925c`, no rebase. Leg started 22:13 at `314ae07c`.
- `ui/100` operator-prompt modal on any tab (ui decision 69, `operator-prompt.md`; server-side 3 s poll, `MAX_SESSIONS` 8): code `9f5461e` on `4914db5` (WIP `cc29076` + resume), doc `1a63895d` (worker `4fd56e26`) onto `a652ae4e`.
- `core/122` capture-timing tests stop flaking (window `199..=10_000` ms): code `5a310bb` on `248a899` (WIP `a24c7d7` + resume), doc `5c89ff2f` (worker `bb26198f`) onto `e724500d`.
- `api/144` compact `embarch-api/open.md` (4,810 to 3,905 B): doc `b2daa5e9` (worker `a086aebc`) onto `a42269ff`; code none, api main stays `124f461`.
- `topology/068` `min_interval_ms` states Core's measurement point: code `eebc122` on `0803354`, doc `bb75de6e` (worker `f0135df7`) onto `2f2c7295`. Leg started 21:50 at `36923622`; resume re-claims `0d478fbe` (ui/100) and `2f2c7295` (core/122).
- `suite/048` operator prompt step (announced `ts` `1793226580.382079`, 16:29:40): core `248a899` on `52d4659`, api `124f461` on `f088971`, ui `4914db5` on `0b18d18`, doc `7a018932`; ff in that order 17:18-17:21, ui main uncompilable against api main about two minutes between.
- `ui/099` Study Designer tab shows protocol divergence (ui decision 68): code `0b18d18` on `7361c2b`, doc `35ad8443` (worker `77eb68ef`) onto `7e1fa488`.
- `api/128` hardware test ledger per project (api decision 98; `run_study` gained optional `test`): code `f088971` on `2a89a61`, doc `dc7fa414` (worker `993289fe`) onto `67e62b55`.
- `study-designer/080` pure reordering reported under the part that moved (decision 87 amended): code `d9dee0e` on `f0de25e`, doc `c5b6c58f`. Leg started 16:28 at `db81050d`; DUT role enrolled as an STM32G0B1VE, probe `000852006107`.
- `suite/049` SCPI bench instruments (announced `ts` `1793223204.666079`, 15:33:24): topology `0803354` on `76bd3d1`, core `52d4659` on `2fccb61`, api `2a89a61` on `9c7832b`, doc `afbaa12f` onto `eda0e50b`.
- `ui/098` signals table and dialog know a bench-board origin (ui decision 67): code `7361c2b` on `9d23e62`, doc `58cf8732` onto `7cd6a2e6`. Its Slack line names `6566cce6` (the `api/130` fold) as its fold by mistake; the real fold is the next commit.
- `api/130` `embarch-api stack plan|fold|restack` (api decision 96; backups under `refs/backup/`): code `9c7832b` on `943f89d`, doc `7cd6a2e6` onto `fcc7c739`.
- `study-designer/079` saved study told its protocol no longer matches the `.eap` (decision 87): code `f0de25e` on `302784c`, doc `fcc7c739`. Leg started 15:30 at `f9ef3f03`; announced `suite/049` `ts` `1793223204.666079`.
- `suite/046` bench board owns signals (announced `ts` `1793219633.062879`, 14:33:53): topology `462e92e` + `76bd3d1` on `b4d1b0a`, core `2fccb61` on `c54591a`, api `943f89d` on `8e25811`, doc `b199ab9e`.
- `core/121` bench study on a captured signal refused at submission (core decision 102): code `c54591a` on `c9bdfab`, doc `1ac397d3` (from `21d32f7d`) onto `e75e9c17`.
- `ui/097` bench box takes its label on the first draw: code `9d23e62` on `7a6d923`, doc `589fa4f9` (from `05ea89d6`) onto `1ae3b546`.
- `api/140` `decisions/client-crate.md` compacted (11,581 to 10,817 B): doc `a7d5dbec` onto `c20f1713`; no code. Leg started 14:53 at `70c9512b`.
- `core/120` `GET /serial-log` resolves a declared signal (core decision 101): code `c9bdfab` on `2d3532d`, doc `3c959c85` onto `c73f6519`.
- `ui/096` `drive_topology.py` isolates its state: code `7a6d923`, doc `9616e75e` onto `c7913c79`.
- `umbrella/093` `embarch setup` installs the desk service and plugin (umbrella decision 58): code `4c786fa` on `97b1358`, doc `8469ab5f` onto `aeb1f31d`.
- `api/125` `serial_log` reads a declared signal (api decision 94): code `8e25811` on `525cda7`, doc `213408cf` onto `ea68b4bc`.
- `suite/047` every suite binary names its commit (announced `ts` `1793216385.010889`, 13:39:45): api `525cda7` on `744b94b`, core `2d3532d` on `72bbd52`, umbrella `97b1358` on `9d27e12`, doc `1c65685f`.
- `ui/095` `time-chart.md` split verbatim (decision 37 to `time-chart-live.md`): doc `7aa213b0` onto `213bd3d0`; no code; `done` in `56550f47`.
- `api/132` `zephyr.rs` cites decision 86, not 64: code `744b94b`, doc `25f394d4` onto `b8ca7aa6`; `done` in `4767f859`.
- `core/118` `halt_count` takes the gate's share from `Validation.halts` (decision 97 amended): code `72bbd52`, doc `02869ae6` onto `4b128505`; `done` in `8f7e81f4`.
- `api/129` `embarch-api patches export|import|regroup` (api decision 92, new dependency `sha2`): code `0fdcf05`, doc `90e2cbeb` onto `dae32801`.
- `topology/066` links.md and enrollment.md split verbatim, `topology/060` paid early: doc `ccf66b1c` onto `5efffa07`; no code.
- `study-designer/078` decision 81 no longer claims a "0 of 0" print: doc `e35da7be` onto `bf6efa5d`; no code.
- `core/116` host study runs Repeat, per-pass line counts (core decision 99): code `29b552e`, doc `710dde87` onto `60f97214`.

**Blocked:** nothing, all 32 units. One reviewer finding (`core/121`) was fixed in its fold and its drop deleted.

**Reviewer** (one per unit, newest first):
**Reviewer:** chat/004 — no findings.
**Reviewer:** ui/101 — no findings.
**Reviewer:** core/123 — no findings (it caught the unwritten placeholder comment; fixed as `85846c4`).
**Reviewer:** api/149 — no findings.
**Reviewer:** ui/100 — no findings.
**Reviewer:** core/122 — no findings.
**Reviewer:** api/144 — no findings.
**Reviewer:** topology/068 — no findings.
**Reviewer:** suite/048 — no findings.
**Reviewer:** ui/099 — no findings.
**Reviewer:** api/128 — no findings.
**Reviewer:** study-designer/080 — no findings.
**Reviewer:** suite/049 — no findings.
**Reviewer:** ui/098 — no findings.
**Reviewer:** api/130 — no findings.
**Reviewer:** study-designer/079 — no findings.
**Reviewer:** suite/046 — no findings.
**Reviewer:** core/121 — 1 finding — inbox/core-decision-92-not-done-clause-stale-after-102.md (fixed in this fold, drop deleted)
**Reviewer:** ui/097 — no findings.
**Reviewer:** api/140 — no findings.
**Reviewer:** core/120 — no findings.
**Reviewer:** ui/096 — no findings.
**Reviewer:** umbrella/093 — no findings.
**Reviewer:** api/125 — no findings.
**Reviewer:** suite/047 — no findings.
**Reviewer:** ui/095 — no findings.
**Reviewer:** api/132 — no findings.
**Reviewer:** core/118 — no findings.
**Reviewer:** api/129 — no findings.
**Reviewer:** topology/066 — no findings.
**Reviewer:** study-designer/078 — no findings.
**Reviewer:** core/116 — no findings.

**Hardware debts owed** (14 of 32 units; the rest none or "none new"; each in the day's own words, unit named on the line above):
ui/101:
**Hardware debts:** one prompt answered from the UI against a live Core with the beep and desktop notification
heard (not exercisable headless); the installed `embarch-ui` predates `ui/100`.
core/123:
**Hardware debts:** native Windows build of `embarch-core` (comment-only change, so a formality).
ui/100:
**Hardware debts:** (1) the modal has never rendered in a browser (`tasks/ui/101`, host-side); (2) one prompt
answered from the UI against a live Core, with sound and notification heard, and the installed `embarch-ui`
predates this.
suite/048:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this (and `suite/049`
and `api/128`); (2) one prompt answered on a real bench from each surface, including a stale answer refused; (3)
native Windows build of `embarch-core`.
api/128:
**Hardware debts:** the task's bench box, written as three steps in the retired task and in `open.md`: a
`tests.toml` with one `dut` test and one needing an absent role gives one runnable and one grouped; `run-study --test`
lands a row that settles; amending a passed commit flags `commit-unreachable`. Needs a deployed Core and a rebuilt
`embarch-api` binary; nothing is deployed.
suite/049:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this; (2) the task's
bench check, owed: on the ET5410A+, `*IDN?`, `MEAS1:ALL?`, `CH1:SW ON`/`OFF` read back and `LOAD1:ABNO?`, time per
command recorded in core decision 104 (no instrument is declared; the bench was unattached this leg); (3) native
Windows build of `embarch-core`.
suite/046:
**Hardware debts:** (1) nothing deployed: the live Core and the installed `embarch-api` predate this; (2) one real
run on a bench board: `declare_signal origin_board=<its name>`, `mem_read probe_serial=`, `validate probe_serial=`,
and a reset resolved from that signal; (3) native Windows build of `embarch-core`.
core/121:
**Hardware debts:** (1) native Windows build of `embarch-core`; (2) once deployed, one bench study tapping a signal
while `POST /signals/{name}/capture` holds it: expect `409` and no flash. Not deployed.
core/120:
**Hardware debts:** (1) once deployed, one `serial_log signal=<name> port_wait_ms=~10000` across a DUT reset on
a CDC ACM console: expect 200, `port` the new name, lines at the signal's baud; one `signal=` on a `host-to-dut`
signal, expect 409; (2) native Windows build of `embarch-core`. Not deployed.
umbrella/093:
**Hardware debts:** owner run: one real `embarch setup` on a machine with `embarch-desk` and `claude`, both steps
reporting done (the service install restarts the live desk), then `setup --uninstall` removing both.
api/125:
**Hardware debts:** once `core/120` lands and Core is deployed, one `serial_log signal=<DUT console>
port_wait_ms=5000` across a DUT reset on a CDC ACM console, confirming lines arrive at the signal's baud.
Not deployed: the installed `embarch-api` does not have `signal` yet.
suite/047:
**Hardware debts:** (1) nothing is rebuilt, installed or deployed: the owner's installed `embarch-api`, the
live Core and `embarch` still print the old lines until rebuilt; **an `embarch` built before this reads the
new `--version` lines as a manifest mismatch (checks 1 and 15), so rebuild umbrella with the others**;
(2) `deploy-core`'s `WSLENV` hand-off has never run against the real service, so the first deploy should
confirm the service's `--version` names the commit; (3) Windows install over a running binary is stated,
not tested; (4) native Windows build of `embarch-core`.
core/118:
**Hardware debts:** (1) a real STM32G0 through `POST /live/core-state` on a running core should report
`halt_count == 1` by default and 2 with `halt=true`; (2) native Windows build of `embarch-core`. Not deployed.
core/116:
**Hardware debts:** (1) run the designer's fixture study (`host_pd_hard_reset_counts.json`, 8 Hard Resets, two
taps) on the PD bench and compare the per-pass counts against a hand count of the console dump — it checks the
assumption that a console line lands in the pass that caused it (a reply delayed past a pass's end counts in the
next pass); (2) native Windows build of `embarch-core`. Not deployed.
Not owed but unrun: ui/099, ui/098, ui/097 and ui/096 were never driven in a browser (`tests/browser/drive_topology.py` needs only geckodriver and a debug build; one headless look at an edited `.eap` study, one `declare_signal origin_board=` then a dialog re-save); `api/130`'s `stack` has met only throwaway fixture repos and needs git 2.38+; `api/129`'s `patches` has met only a synthetic 3-patch repo.
## 2026-10-26 — 85 units

*Folded by the 2026-10-28 leg's log-folder: the per-unit Decided / Gate / Leg-close / Budget / Least-sure-about narrative went (git holds it); every SHA, every reviewer line and every owed hardware debt below is kept.*

**Carry forward (the next leg cannot recover these):**
- **Owner `fleet stop` at 09:19** (`ts` `1793027967.518769`, relayed by the listener, acknowledged in thread). The last leg ran `topology/067`, `api/148`, `core/101`, `ui/086` to completion (all workers finished before the stop, all landed and folded, nothing dispatched after it); **all four reviewers were skipped, so those four units have had no intent read.** The pump latch was already gone. No units ran on 2026-10-27.
- **`suite/046`-`049` still open and unannounced** (`suite/052` was announced 08:09, `ts` `1793023741.728799`, no reply by 08:39, and landed as a supervisor-approved cross-repo shape change, protocol §8).
- **Overdue size ledger unchanged and judged unpayable:** `suite/030` blocked on `DOC-PROTOCOL.md`, `doc/031` owner's, `study-designer/026` every bullet live.
- **`atlas` tasks still skipped per `tasks/doc/089`** (19 queued at last count). **Bench unattached:** `validate dev-bench` not attached, not a mismatch, so `api/059`, `dev-bench/035`, `dev-bench/038` stay `open`; `fleet-hardware.py --refresh` crashes (`tasks/doc/041`) and its buffer was 48 days stale.
- **Next candidates:** `core/116` (unblocked by `core/101`; read its 08:09 note), `core/118` (small), `topology/066`, `study-designer/078`, `ui/095`. Filed by the last leg: `core/118`, `core/119` (`Hardware: required`), `ui/095`. `queue-status.py --count` 35, `inbox/` empty at close.
- **Nothing deployed:** the live Core, the MCP binary and the UI binary all predate `core/096`-`117`, `api/124`-`148` and the new UI; a new UI against an old Core sends `interface`, which the old Core ignores. `core/102`'s `HostStudy` accepts `HOST_TYPE_SCHEMA_VERSION` 20 (the landing bumped 19 to 20, schema-bump window announced `ts` `1793017849.375049`, closed 07:01 with no reply).
- **Failure likely to recur:** a shared-crate landing must build every feature configuration its `Cargo.toml` names; the 06:59 `topology/062` landing broke the `software,wire` build for five minutes (`tasks/doc/091`). Run `check-docs.py` unpiped before every fold: a `| tail` masked its exit and let a fold commit over a red gate once (caught and amended, `7da4011c`).
- `embarch-core/open.md` was 5,070 / 5,120 B at `core/099`, parked under `core/112` (`In flux: yes`); the next core unit that adds an open question must compact it in the same unit.
- `--refill-owed` fires on scope spread only (api, atlas, core, suite, ui, `tasks/doc/081`'s shape).

**Merged / Blocked (nothing was blocked; every unit merged; SHAs in each line are code, doc, rebase bases and gate pins; newest first):**

- 09:27 `ui/086` the Time chart says when a strip or mark lane is capped — `98d9263` `ecd00154` `68fc73ad` `1793027967`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:26 `core/101` a host study's console taps hold their ports for the whole study — `0ba23bf` `68fc73ad` `1a16bae7`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:25 `api/148` core_state tool and CLI — `b0d05a1` `1a16bae7` `1de05c25`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 09:25 `topology/067` the identity gate reports its halts — `b4d1b0a` `1de05c25`
**Reviewer:** skipped (fleet stop at 09:19, before the reviewer was spawned).
- 08:58 `suite/052` a direct signal route declares which serial interface carries it — `1793023741` `5f87333` `62d776e` `c495360` `9e8d8bd` `74c900e` `c126ae4` `02d38b9` `5d1a1fc` `95b7f7c1`
**Reviewer:** no findings.
- 08:36 `ui/093` the desk-Slack browser check waits for its toggle and names a setup failure — `c126ae4` `15e3c63` `954a24c` `417378f7` `4072f789`
**Reviewer:** no findings.
- 08:35 `core/103` Core reads where a running or hung core is without resetting it — `5d1a1fc` `71c65b0` `20cb0159` `66334a05`
**Reviewer:** no findings.
- 08:29 `api/141` the CLI says "no records found" for a zero-record report — `001057729826` `1793023741` `44733b77` `9e8d8bd` `b7701c9` `9ad7248a` `6d662297`
**Reviewer:** no findings.
- 08:03 `ui/089` embarch-ui/spec.md is out of reserve: the tab-navigation paragraph lives in spec/tabs.md — `2ffe19ec` `35b86fb5` `86247e1e`
**Reviewer:** no findings.
- 08:02 `core/117` an ambiguous declared serial reaches every Core caller with its candidate ports — `2ffe19ec` `71c65b0` `06f2d9c` `1cf9c8b3` `24a2a13d`
**Reviewer:** no findings.
- 07:57 `api/136` the MCP startup check is retracted, and a stream 404 keeps Core's own words — `b7701c9` `72f041f` `a55824c3` `49a7aefe`
**Reviewer:** no findings.
- 07:51 `api/133` one build per lock key holds across processes, not only inside one — `72f041f` `001057729826` `401c3c4` `ffcba366` `eb6aa75a`
**Reviewer:** no findings.
- 07:37 `api/147` bench_exchange orders lines by Core's receive times when Core sends them — `401c3c4` `903c76c` `d6af5526` `4485f2f1` `302784c`
**Reviewer:** no findings.
- 07:34 `core/102` Core runs host studies: send-and-read steps against a console, with teardown on every exit — `302784c` `1793017849` `903c76c` `954a24c` `06f2d9c` `731e875` `40b05d86` `44dfab48` `7828256`
**Reviewer:** no findings.
- 07:22 `ui/094` every browser drive script takes its ports from one convention, and the old names are refused — `820ca9d6` `954a24c` `81bde80` `1b9f0b0f` `903c76c`
**Reviewer:** no findings.
- 07:19 `api/146` an old Core's /status reads as unknown images, not as nothing flashed — `001057729826` `903c76c` `3625584` `8aa20c22` `7547221d`
**Reviewer:** no findings.
- 07:02 `ui/085` a Data card's table is re-fetched when it loads, so the post-run re-read is the full file — `1793017849` `81bde80` `35fa9da` `72b042d4` `95f74625` `3625584` `62d776e`
**Reviewer:** no findings.
- 07:01 `core/115` each line of a signal capture carries the time its first byte arrived — `731e875` `de77295` `97e23132` `26a337f8` `62d776e` `7828256`
**Reviewer:** no findings.
- 07:00 `api/145` sessions can take the bench lease and every Core call carries its token — `3625584` `6d615e7` `71db5e4d` `994f5e5e` `62d776e` `5063c0b`
**Reviewer:** 1 finding, filed in the fold as `tasks/api/146` (fix forward): `last_images` must be `Option<Vec<_>>` per client-crate decision 58, so an old Core reads as unknown, not as nothing flashed.
- 06:59 `topology/062` a direct route's declared serial on several ports is refused by name, not guessed — `1793017849` `9e465cb` `62d776e` `b771dd0` `8b41ab47` `a626c70b`
**Reviewer:** no findings; refusing serial-less same-VID ports does not contradict decision 20 (its text still says "kept, not replaced", left as is).
- 06:23 `ui/081` a Slack reply from the Desk goes to the message it was drafted for — `35fa9da` `69edcdd` `f7416058` `7bffd9fe` `6d615e7` `7828256`
**Reviewer:** no findings.
- 06:17 `api/131` one bench_exchange call drives console steps and returns every listened console as one filtered timeline — `6d615e7` `aa303c2` `31c5d788` `3e1284b9` `7828256` `b771dd0` `845f3ea`
**Reviewer:** no findings.
- 06:14 `core/099` a session can lease the bench, and other callers are refused by name while it holds it — `5063c0b` `96cc87a` `2a76ad9c` `12b9e498` `7828256` `b771dd0`
**Reviewer:** no findings.
- 06:12 `study-designer/071` a host study can repeat a block of steps and count matching console lines per pass — `001057729826` `7828256` `4da23d3` `e1f65391` `cd1b8848`
**Reviewer:** no findings.
- 05:54 `topology/064` link-declares.md is out of reserve: decision 36 has its own file — `34a4a478` `3815e56c` `004f70e4`
**Reviewer:** no findings.
- 05:52 `ui/092` drive_topology.py's sidebar checks describe the Desk shell — `69edcdd` `fd7f1b6` `f2243590` `6fb4dbe9` `aa303c2` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:49 `core/114` the capture routes are under the auth sweep and a split `.route(` fails the scan — `96cc87a` `845f3ea` `b61e5610` `597c4adb` `4da23d3` `b771dd0`
**Reviewer:** no findings; decision 42's prose still says "All 22 `.route(` registrations", left because `DOCUMENTED_ROUTE_COUNT` is the pin.
- 05:48 `api/143` capture_start, capture_read and capture_stop drive Core's background signal capture — `aa303c2` `001057729826` `c4a3434` `d70ac3dc` `49bb1cb5` `4da23d3` `b771dd0` `845f3ea`
**Reviewer:** no findings; noted `SignalCaptureResponse` defaults bare scalars where decision 58 prefers `Option<T>`, left (an older Core answers 404).
- 05:33 `ui/087` the validate summary never says passed over a warning or an empty bench, and enrol refuses an unanswerable chip itself — `fd7f1b6` `aefdc8b` `b4cc368b` `250305e0` `c4a3434` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:30 `core/100` a declared signal can be captured in the background while other hardware calls run — `845f3ea` `ffba91a` `c43051a8` `8ed023a3` `4da23d3` `b771dd0`
**Reviewer:** 1 finding (`inbox/core-capture-routes-outside-auth-sweep.md`): the capture routes' multi-line `.route(` escapes decision 42's scan, so no `AUTH_CASES` rows and `DOCUMENTED_ROUTE_COUNT` stays 32; filed as `tasks/core/114`, fix forward, no revert.
- 05:27 `api/135` serial_log tells its caller when Core cut the capture short — `c4a3434` `c49e9b2` `9fd8193c` `f1b9aef0` `4da23d3` `b771dd0`
**Reviewer:** no findings.
- 05:26 `study-designer/074` the GATT extractor ignores definitions inside C comments — `001057729826` `4da23d3` `f25533a` `096bd289` `37567d18`
**Reviewer:** no findings.
- 05:09 `ui/080` a console's unfinished line is capped instead of growing for the whole run — `aefdc8b` `f8b2f7e` `b6321925` `d1b36664` `f25533a` `b771dd0` `c49e9b2`
**Reviewer:** no findings.
- 05:07 `core/105` GET /load/spans is retired: nothing ever called it — `91b7fb1d` `ffba91a` `74c5e4d` `00939429` `f25533a` `b771dd0`
**Reviewer:** no findings.
- 05:05 `topology/061` the topology CLI's Core guard probes a named port, and the CLI enrols bench boards the way Core does — `b771dd0` `62c188d` `c66e648c` `ab2fd2a3`
**Reviewer:** no findings.
- 05:03 `study-designer/073` the .eap parser refuses three authoring errors it used to accept — `001057729826` `f25533a` `0fabb6b` `a8c18d70` `41e0223e`
**Reviewer:** no findings.
- 04:48 `ui/079` the build log says which board it built and why, and the stored log keeps it — `f8b2f7e` `26ed2ec` `17a9dc46` `7a3d59e4` `c49e9b2` `0fabb6b` `62c188d`
**Reviewer:** no findings.
- 04:47 `core/113` POST /study refuses a Notify or Indicate step with a wait budget of 0 — `74c5e4d` `359b8c7` `f4062527` `f769b137` `0fabb6b` `62c188d` `fe68a41`
**Reviewer:** no findings.
- 04:45 `api/124` signal_exchange can match a prompt on a console with echo off — `1ebf8c94` `c49e9b2` `9e4ca14` `fa571863` `0fabb6b` `62c188d`
**Reviewer:** no findings.
- 04:43 `study-designer/077` the alloc test cell compiles again — `001057729826` `0fabb6b` `5ea5ac9` `ceeb34d0` `39ec7a4a` `ba3ad46`
**Reviewer:** no findings.
- 04:28 `outpost/026` the reference decoder refuses a record layout it does not speak — `514d2c0` `2968f0c` `96d2f920` `b61a8ac0`
**Reviewer:** no findings.
- 04:27 `ui/091` the enrol dialog says when an enrol moved a role — `d414560` `26ed2ec` `ba311f8` `84b1400a` `7d2986f4` `9e4ca14` `5ea5ac9` `62c188d`
**Reviewer:** no findings.
- 04:24 `core/111` Core refuses a probe enrolled on another chip family before any attach — `5ea5ac9` `359b8c7` `cd01043` `42ebff05` `8d9012f6` `62c188d` `fe68a41`
**Reviewer:** no findings.
- 04:22 `study-designer/075` a Notify or Indicate row waits for its notification — `001057729826` `ba3ad46` `3ec19b9` `5ea5ac9` `d777103a` `0dbed7c4`
**Reviewer:** no findings.
- 04:05 `ui/083` Live Study renders only the study and the project that are open now — `ba311f8` `5928bdb` `4728bb02` `3c7ea06f` `9e4ca14` `62c188d`
**Reviewer:** no findings.
- 04:03 `core/106` a stream capture says when a write failed, and its sidecars stay on Core's clock and aligned — `cd01043` `9b0d016` `5ac6e2af` `07c339c2` `62c188d`
**Reviewer:** 1 finding (`inbox/core-decision-73-amend-for-88.md`).
- 04:00 `api/142` the client and the enroll result say when an enrol moved a role — `9e4ca14` `7d0f859` `7e6d88c` `45b8f577` `1654d56f` `62c188d`
**Reviewer:** no findings.
- 03:57 `topology/059` a probe moved to another chip family is refused by name before any attach — `001057729826` `62c188d` `7c1ef59` `9f827af8` `de40e3e7`
**Reviewer:** no findings.
- 03:38 `ui/082` a live run's badge says running and counts its step — `5928bdb` `ca0caf8` `ec2653df` `394add5a` `7e6d88c`
**Reviewer:** no findings.
- 03:37 `core/110` the enroll response reports the row a probe vacated — `9b0d016` `fb993b1` `bc3d0263` `9aa520e1` `7c1ef59`
**Reviewer:** no findings.
- 03:36 `desk/004` a tile from an earlier day proposes its gap against that day's current Harvest — `670debc` `da354f8` `4594195f` `099a4e01`
**Reviewer:** no findings.
- 03:35 `umbrella/092` doctor reads a busy bench as busy, not broken — `001057729826` `9d27e12` `c75200d` `0d229bf3` `129ff9c4`
**Reviewer:** no findings.
- 03:20 `ui/090` the tile dialog sends hours only when a person changed them — `ca0caf8` `e111712` `a9debee9` `6a6f0d21` `7c1ef59` `7e6d88c`
**Reviewer:** no findings.
- 03:17 `umbrella/091` doctor and uninstall verdicts say what the docs say — `7c1ef59` `7e6d88c` `c508a4a6` `c75200d` `1e52116` `3c830dd4`
**Reviewer:** no findings.
- 03:15 `api/137` a follow ends on an unknown or interrupted study instead of waiting forever — `7e6d88c` `9ba2714` `ea13842d` `0839bc01` `7c1ef59`
**Reviewer:** no findings.
- 03:13 `topology/065` the wire-only build compiles again and enroll_reporting is public — `6732ad6` `001057729826` `7c1ef59` `321c78d6` `34774116`
**Reviewer:** no findings.
- 02:52 `umbrella/090` embarch-umbrella/open.md out of reserve by wording only — `a053cd7e` `bcbdf34d`
**Reviewer:** no findings.
- 02:51 `desk/003` a tile's hours are set by hand only when a person typed them — `da354f8` `41d9ff2` `16a5dc4b` `b1f03b2a`
**Reviewer:** no findings.
- 02:49 `smp/001` an upload that moves without progressing ends, naming its offsets — `fe68a41` `9236362` `f9138c24` `13f400b2`
**Reviewer:** no findings.
- 02:46 `topology/063` a probe moving roles never loses an enrolled row silently — `001057729826` `6732ad6` `93a83d9` `14571823` `49114c93`
**Reviewer:** no findings.
- 02:32 `umbrella/084` decisions/projects.md out of reserve by a verbatim split — `b91291cd` `2b890be4`
**Reviewer:** no findings.
- 02:30 `ui/084` a saved study is never written into another repo or stripped of its taps — `092fc6f5` `e111712` `aa5ffda` `02f058da` `5c59f1c1`
**Reviewer:** 1 finding (`inbox/ui-spec-restore-unreadable-dir-clause.md`).
- 02:28 `core/109` POST /study refuses an empty record magic — `fb993b1` `35d9859` `1b1242e7` `91f07e4d` `3ec19b9`
**Reviewer:** no findings.
- 02:26 `study-designer/076` GPIO records are named in Core's trace CSV — `001057729826` `3ec19b9` `b19c841` `cd255701` `bce31f0`
**Reviewer:** no findings.
- 02:15 `suite/004` reversals index and studies guide out of reserve by wording only — `1793000429` `267dc107`
**Reviewer:** no findings.
- 01:50 `umbrella/079` decisions/install.md out of reserve by a verbatim split — `4a7007e0` `e1015583`
**Reviewer:** no findings.
- 01:49 `core/108` the hello lock test can no longer reach a real bench — `35d9859` `8e29f06` `696488bb` `6cb252ca`
**Reviewer:** no findings.
- 01:47 `api/139` the exchange fields an older Core does not send are Option — `4e507c0f` `1793000429` `001057729826` `9ba2714` `dd49a1f` `3bca3c75` `4c412021`
**Reviewer:** no findings.
- 01:34 `ui/078` embarch-ui/spec.md out of reserve by a verbatim split — `32ede839` `3f644d7d` `dabb1a2b` `5c85d5a3`
**Reviewer:** no findings.
- 01:32 `core/104` the dev-bench gate and hello take the locks they share — `8e29f06` `da2dd1a8` `b19c841`
**Reviewer:** no findings.
- 01:30 `api/138` signal_exchange and signal-exchange say what Core saw on the wire — `dd49a1f` `d5e90265` `b19c841`
**Reviewer:** no findings.
- 01:28 `study-designer/072` a step name cannot shift CSV columns; zero records is not all verified — `84992d10` `4cd0a885` `001057729826` `b19c841` `5f42a4ab` `ea1934ad`
**Reviewer:** no findings.
- 01:13 `umbrella/009` decisions/bind.md out of reserve by compacting decision 22's retired halves — `3b923ec1` `bc5988ac`
**Reviewer:** no findings.
- 01:12 `core/098` an exchange says what happened on the wire — `de5e82a` `c0b665c` `6735517f` `c9209ff8`
**Reviewer:** no findings.
- 01:08 `api/123` signal-exchange fails loudly when no reply came back — `e5da1c4` `fcbc89c4` `d40d36fa`
**Reviewer:** no findings.
- 01:06 `study-designer/070` host-run study model — `001057729826` `ba3ad46` `30a18cdb`
**Reviewer:** no findings.
- 00:51 `ui/074` embarch-ui/open.md off its cap by deleting settled halves — `2d29cfa9` `cb4ecd14`
**Reviewer:** no findings.
- 00:51 `desk/002` fold and approve edges — `41d9ff2` `3f56975` `0f73bb27` `6082323f`
**Reviewer:** no findings.
- 00:50 `api/134` flash results carry the erased ranges — `765ff8e` `2f3749b` `719a0d42` `37012484`
**Reviewer:** no findings.
- 00:49 `core/107` one timeout_ms covers an exchange's write and read — `001057729826` `476e3e7` `3dba64b` `2fa9f645` `f93730a1`
**Reviewer:** no findings.
- 00:28 `desk/001` Harvest and Linear reads page past their first page — `3f56975` `880d970` `58b0ee4f`
**Reviewer:** no findings.
- 00:27 `chat/002` a background Agent's card shows the subagent's report — `90c6707` `82b82e0` `4b340782` `59712c51`
**Reviewer:** no findings.
- 00:23 `core/097` a console exchange's write survives a throttling device — `3dba64b` `0d712cd` `bae8d660`
**Reviewer:** no findings.
- 00:21 `api/113` embarch-api/open.md out of reserve by deleting answered questions — `df57ce53` `12c59b8d` `988469e7` `001057729826`
**Reviewer:** no findings.
- 00:00 `core/096` flash `erase: true` skips alias and option-byte regions — `0d712cd` `ec80c3d3` `8f0b1ac2` `7da4011c`
**Reviewer:** no findings.

**Hardware debts owed (verbatim from the day):**

- `core/101` **Hardware debts:** (1) the PD-bench check: 8 Hard Resets from `pd-bench` with both consoles tapped, counts
compared against a direct read of the same ports; (2) no `gaps` across a Hard Reset on a real CDC ACM console, and
`\n` really terminates its lines; (3) the two consoles' arrival stamps order correctly against a known PD
exchange; (4) native Windows build of `embarch-core` (the capture opener's COM-port open is the only new
platform surface). Everything was shown over in-process fake serial pairs. Not deployed.
- `api/148` **Hardware debts:** `core_state` (default and `halt=true`) and `mem_read` have never met a live Core; the field
names are mirrored from source. Needs a running STM32G0 and a debugger-halted core, core decision 97's debts
(1) and (2). The MCP binary is not redeployed, so the owner's session does not have `core_state` yet.
- `topology/067` **Hardware debts:** a real STM32G0 identity read reporting `halts == 1` on a running core is unverified on a
board; carried by `tasks/core/118`.
- `suite/052` **Hardware debts:** a real device with two serial interfaces under one USB serial has never been declared
or resolved with an interface (fixture and stub only); whether the DUT board exposes one is still the open
bench fact in `embarch-topology/open.md`. Not deployed: live Core, the MCP binary and the UI binary predate
this; a new UI talking to an old Core sends `interface`, which an old Core ignores, leaving the route
ambiguous as before.
- `core/103` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Bench, on the STM32G0 PD board:
(1) running core, default mode returns PCs inside the image with `halt_count` 1 (the gate's), and
`halt=true` gives 2; (2) a debugger-halted core reads found and left halted, registers read, no resume,
`halt_count` 0; (3) `DWT_PCSR` exists on the part; also `CONTROL`/`PRIMASK` unpacking from probe-rs
register 20, taken from probe-rs source. Not deployed: live Core predates this and `core/099`-`117`.
- `core/117` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). An ambiguity has never been
produced by a real pair of ports sharing a USB serial. Not deployed: live Core predates this and
`core/099`-`115`, `core/102`.
- `core/102` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). The task's bench check: the PD
source sequence as a host study against `pd-bench` gives the bash run's contract lines, and teardown leaves
the partner at 5 V after a forced failure and after a cancel; needs an enrolled signal, the e-load and an
installed Core with this build. Cancel latency against a real load (an exchange in flight cannot be
interrupted, up to 10 s). Not deployed: live Core predates this and `core/099`, `100`, `105`, `106`, `110`,
`111`, `113`, `114`, `115`.
- `core/115` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). No real port has produced these
times: the bridge's read latency and cross-capture wall-clock error are assumed. Not deployed: live Core
predates this and `core/099`, `100`, `105`, `106`, `110`, `111`, `113`, `114`.
- `api/145` **Hardware debts:** on an installed Core at `5063c0b` or later with this client, two sessions: A takes the
lease and exports the token; B's `reset`/`flash` gets the `409` naming A; A's MCP server holds past a 30 s
TTL with no manual renew; an atlas live call with the variable works while B is refused; `last_images`
shows a real flash's `sha256`. Not deployed: the MCP binary predates this, `api/131`, `api/143`, `api/135`
and `api/124`.
- `api/131` **Hardware debts:** two-console order check (two declared direct signals on a real board pair, Core at
`845f3ea` or later; a run across a DUT reset for the port-lost markers and a concurrent-call `409`), and
the replay of one field role-swap check as one call (281 command characters against 3 to 4 helper
calls; result characters need the bench). Both are in `embarch-api/open.md`. Not deployed: the MCP
binary predates this, `api/143`, `api/135` and `api/124`.
- `core/099` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). A two-client check against an
installed Core with a real probe: a second session's `POST /reset` is `409` naming the first, renew and
release work, `last_images` shows the sha256 of a real flash and a real `POST /bootload`. Not deployed:
live Core predates this and `core/100`, `105`, `106`, `110`, `111`, `113`, `114`.
- `api/143` **Hardware debts:** the two-console bench run in the task's own words (capture the DUT console, exchange
on the bench console, read from `next_offset`, reset the DUT for `reopening` + a `gaps` entry, stop);
needs Core at `845f3ea` or later deployed. Not deployed: the MCP binary predates this, `api/135` and
`api/124`.
- `core/100` **Hardware debts:** six bench checks, listed in `embarch-core/open.md` (decision 92 "has never met a
port"): a capture on one console while the other is exchanged and either board flashed and reset; an
exchange on the captured signal; a boot log across a UART-bridge reset; a CDC ACM re-enumeration with
its gap marker and a changed COM name; a multi-minute capture polled with `GET`; Windows refusing a
second open cleanly. Native Windows build of `embarch-core` (owner runs it). Not deployed: live Core
predates this and `core/105`, `106`, `110`, `111`, `113`.
- `core/105` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: live Core still
predates `core/106`, `110`, `111`, `113` and this, so the live route still exists until a redeploy.
- `core/113` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: live Core
predates `core/106`, `core/110`, `core/111` and this.
- `api/124` **Hardware debts:** on a Zephyr USB CDC ACM shell declared as a direct bidirectional signal, `shell echo
off`, then `signal-exchange --until ':~$ ' --match-after-echo false` returns in tens of ms with
`until_seen: true`, and without the flag still runs to timeout. Not deployed: the MCP binary predates
this, so the tool parameter is not live until the owner rebuilds it.
- `core/111` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). A moved-probe run: enrol a
J-Link on one board, flash a project of another chip family through it, expect `409 chip-mismatch` and
no attach. Not deployed: live Core predates `core/106`, `core/110` and this.
- `study-designer/075` **Hardware debts:** a UI-built study with a Notify row against a DUT that notifies within the row's
timeout reports `Pass` (DUT + dev-bench, Core redeployed on this crate).
- `core/106` **Hardware debts:** native Windows build of `embarch-core` (owner runs it). Not deployed: the live Core
predates this and `core/110`.
- `core/110` **Hardware debts:** native Windows build of `embarch-core` (owner runs it); no live enrol run. Not
deployed: the live Core still returns the old shape.
- `core/109` **Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
- `core/108` **Hardware debts:** native Windows build of `embarch-core`, owner's, from the main checkout.
- `core/104` **Hardware debts:** two. (1) Native Windows build of `embarch-core`, owner's, from the main
checkout — and run it before `core/108` lands only with the dev-bench unplugged if it includes
`cargo test`. (2) Hello's `503` is tested through the gate function only; reaching it through the
handler needs a bench to resolve the dev-bench port.
- `core/098` **Hardware debts:** two, from this unit; the task is retired with its bench box unticked and this is
the record. (1) Bench check of decision 85 on a real board: an exchange to a board held in reset
(`S_RESET_ST`) and to one halted by a debugger (`S_HALT`) each name the state; a command that drops
the CDC ACM port answers `port_lost` with its first output line; the guarded attach leaves a running
core undisturbed; 40 ms `QUIET_GAP` is enough for a real shell. (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/107` **Hardware debts:** two. (1) On a real CDC ACM port, confirm a blocking `write` honours the shortened
per-call timeout (folds into core/097's STM32G0 960-character check). (2) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/097` **Hardware debts:** three, all from this unit. (1) On the STM32G0 Zephyr CDC ACM board (the field
board, not this bench): send a 960-character line through `POST /signals/{name}/exchange` with shell
echo on and `timeout_ms` ≥ 2000; the device's own byte count must be 960. (2) Confirm Windows
`serialport` honours `set_timeout` mid-session (assumed, not measured). (3) Native Windows build of
`embarch-core`, owner's, from the main checkout.
- `core/096` **Hardware debts:** two, both from this unit. (1) STM32G0B1VE bench check: write a non-erased word in
a partition the image does not cover, flash with `erase: true`, `mem-read` it back as `0xFFFFFFFF`,
confirm `erased` is `["0x08000000..0x08080000"]` and the image boots; the algorithm-selector check
was tested only on a synthetic memory map. (2) Native Windows build of `embarch-core`, owner's, from
the main checkout.
*Days 2026-10-25 to 2026-10-25 rolled to [log-archive/supervisor-log-2026-10-25-to-2026-10-25.md](log-archive/supervisor-log-2026-10-25-to-2026-10-25.md).*
