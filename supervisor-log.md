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

## 2026-11-27 01:04 — umbrella/122 install-core-on-linux-makes-cores-logs-folder

**Decided:** nothing suite-wide. **Umbrella decision 70 amended in place**: on Linux `step_store` also makes `<data dir>/logs/` as `embarch:embarch-users` `0750`, like `study_results/`, so the engineer (in `embarch-users`) can read the core log when Core is down but not write it; `LinPaths` gains `logs`, the dry-run plan names it, a golden assertion covers it. The worker re-read `embarch-core/src` and 70 now states Core's only data-dir-root accesses are `study_results/`, `logs/` and the read of `installed-release.json`. **Size debt paid by a verbatim split, as I directed at dispatch:** decisions 69 and 70 moved into a new `decisions/install-core-platforms.md` (6,794 B after 70's amendment; the reviewer confirmed 69 byte-identical and 70 changed only in its deviations paragraph), 61 and 71 stay in `install-core.md` (11,774 to 5,855 B, out of reserve); index rows for both; `interfaces/install-core.md` links the decisions index, since `check-decision-refs.py` rejects a link into a split topic file. `tasks/umbrella/123` closed `done` in this fold with its `In flux: yes` left as written; every `Must not delete:` item survives. The two stale lines the `umbrella/121` reviewer found are corrected: `spec/commands.md` row 9 (`setup` registers nothing and names `install-core`) and `decisions/setup-reversal.md`'s dry-run line. `open.md` 3,762 to 3,759 B.
**Merged:** `agent/umbrella/122-install-core-on-linux-makes-cores-logs-folder` (code `bdf9f54`, ff from `af433bb`; doc `c4ed552a`, the worker's `6997da79` rebased onto `58623bfd`). Re-gated on the merge result: `cargo build`, `cargo test` (415 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** added to `umbrella/120`'s Linux debt (owner-run, scratch systemd distro): after `sudo embarch install-core <release>`, `/var/lib/embarch/logs/` is `embarch:embarch-users` `0750`, holds a dated core log, and `GET /logs/recent` returns lines.
**Budget:** PROCEED (5-hour 87%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the Windows half has the same question unanswered: a service Core under `NT SERVICE\com.embarch.core` writes `logs/` and `study_results/` under `%ProgramData%\embarch`, which keeps the ACL Windows gave it (69's deviation), and nobody has read whether a virtual service account can create folders there.

---

## 2026-11-27 01:03 — core/187 the-call-log-has-a-quota-the-agent-meets-first

**Decided:** nothing suite-wide. **New core decision 161** (new topic file `decisions/call-log-quota.md`, 2,936 B; index row; `decisions/call-log.md` 158's "Quota: EMB-329" now "a quota (161)"; `interfaces/call-log.md`; `interfaces.md` lists the route; `open.md` 3,915 B, out of reserve by 5 B): `call-log.jsonl` has a byte quota kept in `call-log-quota.json` beside it, read at start, default 1 GiB when absent or unreadable; the size is the log's length on disk. From 90 % a gated call with the agent's token answers `503` naming the size, the quota, `PUT /call-log/quota` and the person's token; at 100 % the person's calls are refused too; the cancel route is served at any size; a quota refusal is not entered (as 158's free-space refusal). `start`, `stop` and `safe_off` entries bypass the gate, so the safe-off lands past the quota. `PUT /call-log/quota {quota_bytes}` (minimum 1): the agent's token gets `403` on every Core, development included (`QUOTA_ROUTES`, `QUOTA_REFUSAL` in `token_store.rs`); lease-open and not gated, so a full log's person can still reach it; enters a `quota` entry first, then writes the file by temp and rename; returns `{quota_bytes, previous_bytes, size_bytes}`. `GET /call-log` adds `size_bytes` and `quota_bytes`. Route count 73 to 74. 1 GiB, 90 % and 100 % are the owner's chosen values, not measured, and 161 says so. **The worker's own choice, recorded in 161:** a host study's per-step `cannot_log()` uses the person's 100 % mark, so a study the agent started is not cut off at 90 %. No client sends the new route yet (`open.md`, a follow-up for a client scope). Feature row `features.d/core-403-call-log-quota.md` (new), assembled in this fold.
**Merged:** `agent/core/187-the-call-log-has-a-quota-the-agent-meets-first` (code `3d68b0a`, ff from `4805d97`; doc `58623bfd`, ff from `8bbb6735`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (669 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree. Read before merging for wire impact: `embarch-core-client` has no `deny_unknown_fields`, and api's `verify` filters run-log entries by `type`, so the added `GET` fields and the `quota` entry type break no reader I found.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none; no hardware path. The native Windows build of Core (no Windows arm touched). **Deploy debt:** the installed Core.
**Budget:** PROCEED at this dispatch (5-hour 85%, inside the 60-minute reset grace, weekly 43%); PROCEED at this fold (5-hour 87%, weekly 43%).
**Least sure about:** whether a study the agent started should run on past 90 %: the worker chose the person's 100 % mark for `cannot_log()` so a study is not cut off mid-run, which keeps the agent's 10 % margin open to every step of an agent-started study, and nothing in the issue decided it either way.

---

## 2026-11-27 00:52 — umbrella/121 setup-and-doctor-stop-naming-a-core-install-that-registers-nothing

**Decided:** nothing suite-wide. **New umbrella decision 71** (`decisions/install-core.md`, now 11,774 of 12,288 B, in reserve; index row; `interfaces/doctor-chain.md` row 2; `open.md` 3,818 to 3,762 B): `setup` runs no `embarch-core install` at all, since `install --service` needs a record only a verified signed release writes and `setup` holds none. The Local arm no longer says "Installed and started."; it says nothing was registered and names `sudo embarch install-core <release>`, and a real run exits 1 (a dry run keeps its exit); macOS says `install-core` is not built there. The `wsl-host` and `remote` arms name `install-core` (the elevated Windows form for `wsl-host`), then the installed binary's `install --service --bind 0.0.0.0`, because `install-core` binds the `Local` address (69) and Core refuses a binary the record does not list. Doctor check 2 and check 17 fix lines name the same two routes; check 17 no longer offers `embarch setup`; the `up` failure and the non-WSL2 `deploy-core` messages corrected too. Shared text lives in `setup.rs` (`registration_route`, `rebind_route`). **Size debt filed:** `tasks/umbrella/123-compact-umbrella.md`, blocked, `In flux: yes`, due 2026-12-18. **Correction to `core/188`'s entry:** its spread-sweep line should read Spread sweep: nothing filed (2026-11-27 00:42) — I typed a time 14 minutes ahead of the fold's stamp, and this line is the newest, so it governs.
**Merged:** `agent/umbrella/121-setup-and-doctor-stop-naming-a-core-install-that-registers-nothing` (code `af433bb`, ff from `b641c2a`; doc `b2b26d5e`, the worker's `94a6203e` rebased onto `d063b4bb`). Re-gated on the merge result: `cargo build`, `cargo test` (415 passed), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** none new; text only, nothing registered. `open.md`'s existing check 17 live-verification debt (owner-run, reinstalls the service) now names the `--service` form.
**Budget:** PROCEED (5-hour 82%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the reviewer found two stale lines this unit did not touch — `embarch-umbrella/spec/commands.md` row 9 still says `setup` will "install Core as a service", and `decisions/setup-reversal.md` line 23 has the dry run naming `embarch-core install --bind`; I handed both to `umbrella/122`, the next umbrella unit, rather than file an issue, so if that unit misses them nothing else will.

---

## 2026-11-27 00:51 — core/188 every-probe-open-steps-around-cores-own-hold

**Decided:** nothing suite-wide. Split at leg start, at `1e79bff0`: EMB-592 into `tasks/core/188` (`verify-only`), EMB-593 into `core/189`, EMB-594 into `umbrella/122`; all `filed`, Fleet Working; picks announced before any claim (ts `1795765384.910169`). Spread sweep: nothing filed (2026-11-27 01:05) — a delta read: only `embarch-umbrella/open.md` changed since the 00:25 sweep (`umbrella/119`, `120` rewording their own debts), nothing new in another scope. **Core decision 159 amended in place** (`decisions/port-hold.md`): a new `probe_hold::around_role(role, f)` looks up the role's enrolled probe serial and runs `around` on it, or runs `f` unchanged when the role has none; `POST /validate` (role and serial), `POST /probes/enroll` with a `probe_serial`, `enforce_dev_bench_gate` (which covers `GET /dev-bench/hello` and `POST /study`, so `study.rs`'s other two sites needed no edit) and the test executor's `validated_id` now close and reopen the held probe. **Named uncovered in 159:** `POST /probes/enroll` with no `probe_serial`, which learns the serial only by opening the one attached probe. The worker grepped every caller of `validate_*`, `open_probe`, `attach::attach` and `enroll_reporting`; the reviewer re-grepped and agrees. No change to `interfaces/hardware.md`, `open.md` or `spec.md`.
**Merged:** `agent/core/188-every-probe-open-steps-around-cores-own-hold` (code `4805d97`, ff from `364cf99`; doc `d063b4bb`, ff from `29eb92d7`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (665 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** on a real J-Link and a CMSIS-DAP or ST-Link, with the probe held by a lease: `POST /validate` by role and by serial; `POST /study` and `GET /dev-bench/hello`; `POST /probes/enroll` with a `probe_serial` — each succeeds and logs the close and reopen. Whether a second open of a held probe fails on each probe kind is still unmeasured. The native Windows build of Core. **Deploy debt:** the installed Core; `core/184`'s "do not deploy past `576cb04` until EMB-592 lands" is now discharged at `4805d97`, subject to the bench check above.
**Budget:** PROCEED at leg start (5-hour 80%, weekly 42%, wave 6; only two scopes dispatchable, so a wave of 2); PROCEED at this fold (5-hour 82%, inside the 60-minute reset grace, weekly 43%).
**Least sure about:** the new test drives `around_role` with the fake opener, not the `POST /validate` or study-gate handlers under a live lease, because the identity gate needs the topology store and a real probe; the wiring at each handler is read, not run.

---

## 2026-11-27 00:38 — umbrella/120 install-core-gives-core-a-user-and-a-protected-store-on-linux

**Decided:** nothing suite-wide. **New umbrella decision 70** (`decisions/install-core.md`, now 9,385 B; index row; `interfaces/install-core.md`; `spec/commands.md`): on Linux, `install-core` runs one generated POSIX `sh` script as the root calling process (`sh -s`, script on stdin, no file written, no `sudo` re-launch), reusing `umbrella/119`'s `parse_transcript` and `Host` seam, so the steps and transcript lines match Windows; Windows behaviour unchanged. Step 0 refuses before any write when not root, `systemctl` is missing, the engineer account is missing, or `store/` is a link, not a folder, or not owned by `embarch`. Then the `embarch` system user and `embarch-users` group, `/opt/embarch/core/<version>/`, `store/` `embarch` `0700`, firmware `staging/` `root:embarch-users` `0770`, token files `0640 embarch:embarch-users` when absent, `install --service --bind`, start and `core-fingerprint`. Core's unit writer already sets `User=embarch` on Linux (`service.rs`), so no Core task was needed for that. **Deviations, written into 70:** the engineer is `$SUDO_USER`, validated as a plain account name that is not `root` or `embarch`, unset refused; the unit name `com.embarch.core` is assumed; only the default data dir; the engineer needs a fresh login for the new group; and `study_results/` is created `embarch:embarch-users` `0750` because the data dir stays `root` `0755` and Core writes run directories there (core 129). The reviewer found the same case for `logs/`, which 70 misses: **EMB-594**. `embarch-token.md` §5 still true (nothing service-validated), so no status fragment. `open.md` 3,915 to 3,818 B.
**Merged:** `agent/umbrella/120-install-core-gives-core-a-user-and-a-protected-store-on-linux` (code `b641c2a`, ff from `060380b`; doc `a793da53`, the worker's `474a89df` rebased onto `1e41a6bb`). Re-gated: `cargo build`, `cargo test` (412 passed), `clippy --all-targets -D warnings` clean; the script checked with `sh -n` and the store refusal run for real against a temp dir by the worker. `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-594
**Hardware debts:** owner-run, in a scratch systemd distro: `sudo embarch install-core <a signed release>` reports all seven steps OK; `systemctl cat com.embarch.core` shows `User=embarch`; `store/` is `embarch` `0700`; both token files are `0640 embarch:embarch-users` and the engineer reads `token` after logging in again; `core-fingerprint` equals `/status`'s `keyid`; a root-made `store/` is refused with nothing written. Assumed, not measured: `useradd --system --user-group`, `usermod -aG`, GNU `stat -c`, the unit file name, Core accepting `0640` token files it did not create.
**Budget:** PROCEED (5-hour 78%, weekly 42%, resets in 1h12m).
**Least sure about:** whether `logs/` is the last data-dir-root write a service Core makes as `embarch`; the reviewer read `embarch-core/src` and found no other, but the only proof is the first install in a scratch distro, and on Windows the same question is answered by `%ProgramData%`'s default ACL, which nobody has read for a virtual service account.

---

## 2026-11-27 00:35 — core/185 a-service-core-takes-firmware-only-from-its-staging-folder

**Decided:** nothing suite-wide. **New core decision 160** (`decisions/flashing.md`, now 8,134 B; index row "10, 18, 21, 32, 82, 84, 160"; a 48-byte note in `interfaces/hardware.md`, now 11,055 B, kept out of reserve): under `run --service`, `/flash`'s JSON `firmware_path` and `manifest_path` are read only through `staging::read` (`src/staging.rs`, the one helper a later path-taking route must call), which resolves each component under `<data dir>/staging/` and answers `400` before opening for a symlink, a junction or other reparse point, a hardlink (link count above 1), `..`, or an absolute path outside; a missing staging folder is refused, never created. The bytes are read from the opened handle, written to a temp file and flashed from there, so the flashed-image record's path reads `(uploaded)` as for multipart. Multipart and a development Core are unchanged. Decisions 10 and 18 were not amended; the reviewer found nothing in them that 160 contradicts. The staging folder matches what `umbrella/119` (umbrella decision 69) now creates on Windows.
**Merged:** `agent/core/185-a-service-core-takes-firmware-only-from-its-staging-folder` (code `364cf99`, ff from `576cb04`; doc `401c0070`, ff from `fe60332d`). Re-gated: `cargo build`, `cargo test --no-fail-fast` (664 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; the Windows branches of `staging.rs` type-checked by the worker in a throwaway crate (hidapi blocks the whole crate under WSL). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-593
**Hardware debts:** on the Windows host with a `run --service` Core and `%ProgramData%\embarch\staging\` present: a staged file flashes by name; a path through a `mklink /J` junction, a `mklink` symlink and a `mklink /H` hardlink each answer `400`. The native Windows build of Core. **Deploy debt:** the installed Core (and see `core/184`'s entry: not past `576cb04` until EMB-592 lands).
**Budget:** PROCEED (5-hour 75%, weekly 42%).
**Least sure about:** decision 160 says a link swapped in after the check is never followed, and EMB-593 shows that holds only for a flat name: `staging::read` lstat-checks each component and then opens the joined path with a no-follow flag that covers the last component alone, so a nested parent swapped for a link in between is followed (it needs a writer inside `staging/`). The worker reported the stronger claim; I kept the merge (additive, gate green) and left the fix, or a narrowed 160, to the next core unit.

---

## 2026-11-27 00:27 — umbrella/119 install-core-puts-core-under-its-own-account-on-windows

**Decided:** nothing suite-wide. **New umbrella decision 69** (`decisions/install-core.md`, now 6,293 B; index row; `interfaces/install-core.md`; `spec/commands.md`): on Windows, `install-core` follows its verify-and-stage half with one generated PowerShell script, run elevated through `Start-Process -Verb RunAs` and logged from inside, in the issue's order: step 0 refuses a store owned by anyone but Administrators, SYSTEM or the service SID; then the binary into `%ProgramFiles%\EmbArch\core\<version>\`, `store\`, the firmware `staging\`, the token files when absent (32 random bytes as 64 hex, which matches Core's own token shape), `install --service --bind`, then start and `core-fingerprint`. The transcript parser fails a silent step, a missing `=== done ===`, a bad fingerprint or a missing transcript. `installed-release.json` gains `binary_sha256` (array of the staged `embarch-core` hash, `binaries` kept, `serde(default)` so old records read), which Core's `install --service` (157) needs. **Deviations, written into 69:** verify-and-stage still runs unelevated (self-elevation stays a later unit; the engineer's SID is `whoami` there); only the default data dir gets the Windows half; `--bind` is the topology's `Local` address (wrong for a WSL2 host, which 61 already defers); `%ProgramData%\embarch` keeps the ACL Windows gave it. **Size debt paid:** `open.md` 4,634 to 3,915 B, out of reserve with `umbrella/111`'s `Must not delete:` list intact, so I closed `umbrella/111` `done` in this fold (its `In flux: yes` left as written). **My own edit in this fold:** `embarch-core/interfaces/installed-release.md` no longer says the record's writer is a later task; it names `install-core` (decisions 61, 69).
**Merged:** `agent/umbrella/119-install-core-puts-core-under-its-own-account-on-windows` (code `060380b`, ff from `5533608`; doc `4180be6a`, the worker's `8fe2f8fc` rebased onto `878605cc`). Re-gated: `cargo build`, `cargo test` (395 passed), `clippy --all-targets -D warnings` clean; Windows code type-checked by the worker in a throwaway crate (`aws-lc-sys` blocks the whole crate under WSL). `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** owner-run, elevated Windows shell: `install-core <signed release> --data-dir <temp>` writes the record and the staging ACL lists only Administrators and SYSTEM, a tampered release writes nothing; a default-dir install reports all six steps OK, `sc qc com.embarch.core` shows `NT SERVICE\com.embarch.core`, the store ACL is the service, SYSTEM and Administrators, `core-fingerprint` equals `/status`'s `keyid`; an engineer-made store is refused at step 0. Assumed and never run: the `sc showsid` parse, PowerShell 5.1's handling of native stderr, Core accepting the script-written tokens.
**Budget:** PROCEED (5-hour 72%, weekly 42%).
**Least sure about:** the whole Windows half has run only as text against a fake host; the first elevated install is the first time any of its six steps meets a real ACL or service manager, and `sc showsid`'s output parse is the step I would bet on failing first.

---

## 2026-11-27 00:25 — core/184 core-holds-its-probes-while-a-lease-or-study-holds-the-bench

**Decided:** nothing suite-wide. Split at leg start, at `6f0a39a9`: EMB-339 into `tasks/umbrella/119` (the elevated Windows step) and `umbrella/121` (`setup` and `doctor` stop naming `install --bind`, the finding comment `core/183` left on EMB-339), EMB-340 into `umbrella/120`, EMB-329 into `core/187`; all `filed`, Fleet Working; picks announced before any claim (ts `1795763673.393199`). Found while splitting: umbrella's `installed-release.json` had a `binaries` map and no `binary_sha256`, which Core's `install --service` (157) requires, so `umbrella/119` was told to add it. Spread sweep: nothing filed (2026-11-27 00:25) — a delta read: only `embarch-api/open.md` and `embarch-core/open.md` changed since the 2026-11-26 19:55 sweep, and neither names new work outside core. **New core decision 159** (`decisions/port-hold.md`, now 6,123 B; index row "130, 159"; `interfaces/signing.md` gains `observed.probes_held`): the decision-130 holder also opens each enrolled board's probe at lease take or study start, keyed by serial. **Deviation from the issue's direction, written into 159:** a Core call does not borrow the held probe, it closes and reopens it (`probe_hold::around`), because the topology identity gate opens the probe itself and probe-rs 0.31's `Session` consumes the `Probe`; the windows between are named as not covered. A failed open at the take, or a failed reopen, drops the probe from the hold and the record, logged only. **Filed from the review: EMB-592** (Fleet Ready, core): `POST /validate`, `test_executor.rs` and the dev-bench identity gate open the probe without `around`, so under a lease they run against Core's own hold.
**Merged:** `agent/core/184-core-holds-its-probes-while-a-lease-or-study-holds-the-bench` (code `576cb04`, ff from `8b7dbe1`; doc `b2387867`, ff from `c7936e5b`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (659 passed, 2 ignored, plus 2), `clippy --all-targets -D warnings` clean; `check-docs.py` 12/12; ownership green on both branches; client names clean on the code worktree.
**Blocked:** nothing.
**Reviewer:** 1 finding — EMB-592
**Hardware debts:** on a real J-Link and a CMSIS-DAP or ST-Link under a lease: a second Core cannot open the held probe; `probes_held` lists its serial in the signed record; an `nrfutil` flash on the nRF54L15 closes and reopens the probe as logged; whether a second open fails on Windows is assumed. Also, per EMB-592, validation under a lease and a study started under a lease. The native Windows build of Core. **Deploy debt:** the installed Core, and **do not deploy a Core at or past `576cb04` to the bench until EMB-592 lands** — under a lease, a study's dev-bench gate may fail against Core's own probe hold.
**Budget:** PROCEED at leg start (5-hour 64%, weekly 41%, wave 6); PROCEED after wave 1 (5-hour 72%, weekly 42%).
**Least sure about:** whether a second open of a held probe actually fails on the bench's probes; if it does not, EMB-592 is only a coverage gap, and if it does, `576cb04` breaks studies under a lease until it lands — the fake opener cannot tell which.

---

## 2026-11-27 00:07 — core/182 core-refuses-a-hardware-call-it-cannot-log

**Decided:** nothing suite-wide. Split at `a1798eb0` (see `api/218`'s entry in the 2026-11-26 fold), dispatched alone as wave 2 once `core/183` had landed. **New core decision 158** (`decisions/call-log.md`, 10,990 of 12,288 B; index row; 122's "Not here" line now points to it; `interfaces/call-log.md`; `open.md`): Core keeps a **cannot-log** state, set when an append fails (any error, a chain that does not verify included) or when free space falls below the reserved tail, cleared by the next append that succeeds with room left; the space check is redone at each gated call. In that state every gated route answers `503` naming the call log and the reason, except `POST /study/{id}/cancel`; the gate sits inside auth and outside the lease layer, and the lease-open routes (`GET /call-log` among them) are not gated. After a failed write, the first refusal once the writer recovers is itself entered and serves as the probe; a refusal for lack of space is not entered, so the tail stays for the safe-off. A host study asks the gate before each step, `Repeat` pass and teardown step; a cannot-log answer stops the step list and Core's safe-off (156) runs in place of the teardown, `events.json` carrying `teardown_replaced` and the stop reason. `start`, `stop` and the new per-result `safe_off` entries bypass the gate. **Reserved tail:** (declared safe-off lines + signals + 2) × 8,192 B, read from the declarations at each gate; the 8,192 B per entry is assumed, not measured, and 158 says so. A `Store` trait in `call_log.rs` is the seam (append and free space: `statvfs` on Unix, `GetDiskFreeSpaceExW` on Windows, with the `Win32_Storage_FileSystem` feature added to `windows-sys`). **Two deviations, both written into 158 and `open.md`:** a device study is not stopped by the cannot-log state (its steps run in the bench firmware and Core can only ask it to stop); a call whose entry fails after its handler ran is still served, and the next call is the first refused. Feature row `features.d/core-402-call-log-fails-closed.md` (new). **Unblocks in Linear:** EMB-329 (the call log's quota) once `finish` moves EMB-328 to Done. **Day fold in this unit:** an `embarch-log-folder` subagent folded 2026-11-26's 51 unit entries into one (186 SHAs, 51 reviewer lines, 11 debt lines kept; its first `--apply` was refused for 17 dropped SHAs and it added a reference-points line); I rolled 2026-11-24 into `log-archive/` (log 133,479 to 92,676 B). `check-client-names.py --suite --history`: every repo clean.
**Merged:** `agent/core/182-core-refuses-a-hardware-call-it-cannot-log` (code `8b7dbe1`, ff from `4ae97c6`; doc `60c0fe66`, the worker's `5bf4061e` rebased onto `264c57bc`). Re-gated on the merge result: `cargo build`, `cargo test --no-fail-fast` (654 passed, 2 ignored, 0 failed, plus 2), `clippy --all-targets -D warnings` clean. `check-docs.py` 12/12; ownership green on both branches (7 doc paths); client names clean on the code worktree. The feature row assembled into `suite/features.md` in this fold.
**Blocked:** nothing.
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core, now also owed for the `GetDiskFreeSpaceExW` call and the new `windows-sys` feature, which no compiler has built. A real full disk under a live Core; a real host study whose teardown is replaced by the safe-off against a real instrument. **Deploy debt:** the installed Core.
**Budget:** PROCEED at leg start (5-hour 51%, weekly 39%, wave 6, capped at 4 units); PROCEED at this dispatch (5-hour 59%, weekly 40%).
**Least sure about:** decision 95's "Teardown always runs" (`decisions/host-study.md` line 17) is now narrowed by 158 but not amended, which the reviewer called a doc-consistency gap rather than a contradiction; 95 is already 799 B over the per-decision cap, so I left it rather than grow it, and the next compaction of 95 should carry 158's exception.

---

## 2026-11-26 — 51 units

*Folded by an embarch-log-folder agent on 2026-11-27: per-unit narrative reasoning, gate transcripts (test counts, clippy and check-docs runs), budget lines and "least sure about" notes dropped; git holds the diffs and the decisions themselves. Every SHA, reviewer line, board-naming debt and blocked line kept, one block per unit, newest first, each with a one-to-three-line gist of what it decided. The day's twelve "Leg end, to carry" paragraphs are folded into the carry-forward below.*

**Carry forward (state at the last leg's end, 23:55).**
- **Four clear legs, 51 units, one blocked half.** Every leg landed 4 of 4; only `ui/124`'s prompt-modal half was left `blocked` (14:18, since landed at 18:08). Budget at the last recorded leg end: PROCEED, 5-hour about 53%, weekly about 40%.
- **Suite-level decisions made on the owner's behalf (the owner's to strike):** three parked tasks run by a leg's own hands after a silent announcement window. `suite/064` (21:56): `suite/agent-guide.md` §1.1 places all 64 registered tools (allow gains `run_test`, `test_status`, `test_show`, `test_pending`, `test_plan`, `test_propose`, `cancel_study`, `export_audio`; ask gains `test_add`; `ledger_*` gone; retired stub `embarch-api/interfaces/tools-ledger.md` deleted). `suite/065` (22:48): `embarch-core-client`'s `StudyEvent::PromptPending` gains optional `prompt_kind` (api decision 137 amended in place; ui 113's "no kind until EMB-577" line corrected). `api/217` (22:36) folded `resume_test` into the agent guide's allow list, now 65 tools. `api/206` (17:36): one cross-repo landing by my own hands (`embarch-ui` consumer commit `59c5e5a`) after a 30-minute announcement with no reply; a new `pub` field on a struct a consumer builds by literal is not "additive". Also marked the owner's to strike: dev-bench decision 69 (`pd times`, `dev-bench/053`) and EMB-461's `chat/050` (container login; plan choices 11 and 22).
- **Recurring worker and dispatch faults:** workers cited the task number instead of the decision number in code comments three times across two legs (`api/216`, `core/172`, `core/168`); landing fixed each. A dispatch note should **quote a field's source, never paraphrase its meaning** (`api/216`'s "`U` is `k x u`" was my error and printed `U` doubled until the reviewer caught it: EMB-590, closed by the fix `419d020` / `13c683e7`). `api/213`'s worker guessed Core's `n_of_m` shape from a stale main checkout (fixed at landing). The gate's `<this repo>/scripts/desk-gate-bin.py` is the framework repo's, not the instance's (`embarch-fleet/scripts/`); a wrong path returns an empty desk binary and a silent `npm test`. Shell `for` and `until ... done` loops are unallowlistable: claim and poll one command per task. A 150-minute barrier at 14:29 (`chat/048`'s flake hunt) left three landed-ready units waiting; the foreground call ticks nothing while open.
- **Open reviewer note, not filed:** `api/208`'s copied `judge` reads an empty reply with no `reply_bytes` as TimedOut, so an older `events.json` that places its steps but predates `reply_bytes` and recorded Fail would fail `verify` check 2; whether such a zip exists was not checked. Known consequence of `core/183`: no path in the suite can register a Core service until EMB-339 or EMB-340 lands (`embarch setup` on a Local topology prints "Installed and started." while registering nothing); the owner's existing Windows service is untouched.
- **Dispatchable now:** `tasks/core/182` (EMB-328, `hw:none`), `core/184` (EMB-327), `core/185` (EMB-330, `verify-only`) are filed, with `core/183` landed; Fleet Ready: core EMB-324 (unblocks 339, 340, then 342) and EMB-329 (waits behind EMB-325, now Done); the next leg owes a split. The `Scope: suite` audit issues (EMB-295, 302, 305, 306, 307, 314, 332) are §8 work, none taken; EMB-303 was split as two single-scope tasks (`chat/052`, `ui/129`, both landed) rather than run as `suite`, and the other doc-only ones may split the same way where each half stays inside one ownership row. EMB-332 is genuinely two code repos and stays §8.
- **Hardware / bench:** hardware buffer last refreshed 22:52: Core reachable, dev-bench and DUT not attached; bench tasks `api/059` and `dev-bench/038` stay `open`. Debts owed this day are in the per-unit lines (largest: `core/181`'s five bench steps, `core/183`'s first elevated install, the PD bench's two characterisation sessions, and the native Windows build of Core, never compiled here, owed by `core/168`, `169`, `170`, `167`, `178`, `180`, `181`, `183`).
- **Deploy debts:** the installed Core runs none of today's Core work until redeployed (no Test-run record signing, no amended study record, no smoke check, no output safe-off at start or stop, no `install --service` registration). `core/183`: a plain `install --bind` from a new build registers nothing and names `embarch deploy-core`.
- **Size debts:** none overdue. Reserve files all filed and parked: `umbrella/111`, `dev-bench/052`; `api/218` (paid in this fold's last leg) and `core/186-compact-core.md` (`spec.md` 9,082 B, `decisions/platform.md` 11,527 of 12,288 B, due 2026-12-10, `open`). Chat decision 123 is 36 B under the per-decision cap.
- **Stale, the owner's:** `embarch-analog-capture-proposal.md` is in neither `reserved` nor `fleet_writable` (`check-ownership.py --supervisor`), unclassified all day.
- **Refill and spread:** Spread sweep: nothing filed (2026-11-26 19:55) is the newest; every other leg split Fleet Ready instead of sweeping. The 19:55 sweep read 15 source files changed since 2026-11-24 00:23 and found nothing host-side and dispatchable in a new scope.
- **Reference points, kept because the ledger counts them:** the leg-start split commits (the log's `Split ... at` SHAs): `dbf2088a` (14:29 leg), `6967737b` (14:02), `a429277b` (17:43), `e2ff47f5` (18:14), `17282b6d` (19:24), `28d227f9` (19:56), `7ba4ce56` (21:15), `b3b44903` (20:58), `1f421053` (21:22), `abdacdc8` (22:02), `af80de62` (11:33); also `b31a7d8b`, `b65f3f9c`, and `7391457` (the `hil_check.rs` hunk of the reverted `study-designer/099`, applied by the worker in a throwaway crate worktree to prove `api/204`'s fix). `#embarch-fleet` thread timestamps of the announcement windows: `1795750706` (`suite/064`), `1795753355` (`suite/065`), `1795755747`, `1795758923` (leg picks).

---

### 23:55 — core/183 install-service-registers-only-a-listed-release-under-cores-own-account
New core decision 157 (`decisions/platform.md`, index row; new `interfaces/installed-release.md` with a row in `interfaces.md`; `spec.md` §3): `install --service --bind <addr>` hashes its own binary and refuses, before any elevation or service-manager call, unless `<data …
**Merged:** `agent/core/183-install-service-registers-only-a-listed-release-under-cores-own-account` (code `4ae97c6`, ff from `c0a1b43`; doc `83d1d58f`, the worker's `bc761904` rebased onto `2d216b1e`).
**Reviewer:** no findings.
**Hardware debts:** the first elevated install on Windows and on Linux: `sc qc` and `systemctl cat` show the account and `run --service --bind`; `update` refuses a `--service` registration; the in-place rewrite still sets the account; the virtual account can write `store/` (EMB-339's part). The Windows-gated code (`apply_windows_account`, the registry read in `registered_command`) has not been type-checked: `cargo check --target x86_64-pc-windows-msvc` fails in hidapi's `build.rs` under WSL, the known limit, so the native Windows build of Core is owed. **Deploy debt:** the installed Core; note that a plain `install --bind` from a new build registers nothing.

### 23:54 — ui/129 ui-points-at-chats-launcher-decisions
The second half of EMB-303 (first half `chat/052`, chat decision 123). Ui decision 28 is now a one-line pointer to chat 123 (heading kept); decision 3's first paragraph says the launcher lives in `embarch-chat` (chat 29) and points at 123 for the thin-launcher stance, keeping ui's own `.vsix` and …
**Merged:** `agent/ui/129-ui-points-at-chats-launcher-decisions` (doc `971c32d6`, the worker's `1d5e74eb` rebased onto `db3fad7c`; code: the worker touched none, and my comment fix is code `db0562e` on embarch-ui main, ff from `7575d64`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:51 — api/218 compact-api
Split at leg start, at `a1798eb0`: EMB-328 into `tasks/core/182`, EMB-324 into `core/183`, EMB-327 into `core/184`, EMB-330 into `core/185` (all `filed`, Fleet Working); picks announced before any claim (ts `1795761780.530059`) …
**Merged:** `agent/api/218-compact-api` (code none, embarch-api untouched; doc `db3fad7c`, ff from `8595cfb3`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:36 — chat/052 chat-records-the-vs-code-launchers-decisions
New chat decision 123 (`decisions/launcher.md`, a new topic file, 4,060 B against the 4,096 B per-decision cap; index row): the VS Code launcher's behaviour, moved from `embarch-ui` decisions 3, 28 and 101 and restated in chat's voice …
**Merged:** `agent/chat/052-chat-records-the-vs-code-launchers-decisions` (code `edc9d5e`, ff; doc `d5a390ab`, the worker's `52b671db` cherry-picked onto `e332c13a`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:35 — core/181 core-switches-every-declared-output-off-at-start-and-graceful-stop
New core decision 156 (`decisions/call-log.md`, beside 122; index row; `interfaces/call-log.md` gives the `start` and `stop` entry shapes and the safe-off result shape exactly, for EMB-328 and EMB-329 to build on …
**Merged:** `agent/core/181-core-switches-every-declared-output-off-at-start-and-graceful-stop` (code `c0a1b43`, ff; doc `2a793a4f`, the worker's `d5256043` cherry-picked onto `bb2cdea7`).
**Reviewer:** no findings.
**Hardware debts:** five steps written in the task file for a real instrument and bench board: the safe-off at start with outputs switched on first; SIGTERM, Ctrl-C and SCM Stop with outputs on, timing the SCM stop; `kill -9` then the next start; an unplugged instrument at start; a stop mid host study. The native Windows build of Core (the `cfg(not(unix))` arm of `shutdown_signal` was not compiled here). **Deploy debt:** the installed Core.

### 23:34 — api/219 verify-judges-a-refused-exchange-step-under-its-recorded-target
New api decision 149 (`decisions/verify-test-run.md`, beside 146; index row "146, 149"; `interfaces/verify.md` check 3 row; 146's "what the zip cannot give" paragraph points to it): `verify` check 3 judges an `Exchange` step row carrying `target` `"dut"` or `"bench"` (core 155) under that target …
**Merged:** `agent/api/219-verify-judges-a-refused-exchange-step-under-its-recorded-target` (code `5b9f71f`, ff; doc `32fc7721` and `f91e2f7f`, the worker's `fb56c4e3` and `8be34e76` cherry-picked onto `4bc0e35e`).
**Reviewer:** no findings.
**Hardware debts:** none

### 23:33 — ui/128 the-prompt-modal-takes-a-test-run-prompts-kind-from-the-event
Split this leg, at `39559d93`: EMB-591 into this task, EMB-589 into `api/219`, EMB-325 into `core/181`, EMB-303 into `chat/052` plus `tasks/ui/129` (blocked on `chat/052`; ui scope already had this unit in the wave, and 129 needs 052's decision number). All `filed`, Fleet Working …
**Merged:** `agent/ui/128-the-prompt-modal-takes-a-test-run-prompts-kind-from-the-event` (code `7575d64`, ff; doc `a5ab8480`, ff).
**Reviewer:** no findings.
**Hardware debts:** none

### 22:48 — suite/065 the-core-client-reads-a-prompt-events-kind
suite-level, on the owner's behalf, after a silent window: `embarch-core-client`'s `StudyEvent::PromptPending` gains an optional `prompt_kind` (`PromptKind`, `#[serde(default, skip_serializing_if = "Option::is_none")]`), and `as_pending_prompt` and `prompt_pending` carry it both ways, so a Test run's event parsed by the client names its kind without the `GET /study/{id}` poll …
**Merged:** no branch merge: my own commits on each `main`, sequenced shared crate first: api `5ba0749` (ff from `2b54d0d`), then ui `0b08867` (ff), then doc `ffcbc725`, then this fold.
**Reviewer:** no findings.
**Hardware debts:** none

### 22:36 — api/217 embarch-api-resumes-an-interrupted-test-run
suite-level fold, on the owner's behalf: `suite/agent-guide.md` §1.1 places the new MCP tool `resume_test` in allow, beside `run_test`, and now counts 65 tools (65 `#[tool(` attributes in `src/tools.rs` on `origin/main`, 64 before this unit); the paragraph under it says `run_test` and `resume_test` both only prepare, the go being the engineer's on Core's card …
**Merged:** `agent/api/217-embarch-api-resumes-an-interrupted-test-run` (code `2b54d0d`, ff from `419d020`; doc `65b94f7c`, ff from `2490adb7`).
**Reviewer:** no findings.
**Hardware debts:** none

### 22:23 — core/180 a-test-runs-exchange-steps-record-their-target-in-the-signed-files
New core decision 155 (`decisions/test-run-target.md`, a new topic file; index row; `interfaces/host-studies.md` names the fields): each `Exchange` step row of `events.json` gains `signal` (the signal name) and `target` (`"dut"` or `"bench"`), on `Exchange` rows only, both `Option` with …
**Merged:** `agent/core/180-a-test-runs-exchange-steps-record-their-target-in-the-signed-files` (code `ef7416a`, ff from `b85a419`; doc `f82ed294`, the worker's `23275059` cherry-picked onto `e8aecf77`).
**Reviewer:** no findings.
**Hardware debts:** a real Test run on the bench whose study addresses a DUT signal and a bench-board signal: only fake-backend tests have exercised the live topology lookup that now writes `target`. The native Windows build of Core. **Deploy debt:** the installed Core.

### 22:22 — api/216 a-test-report-prints-each-limits-decision-rule-and-verify-rebuilds-it
New api decision 147 (`decisions/publish-test-limits.md`, index row): the Test PDF gains a "Limits and decision rule" section after the tests table, one row per limit of core decision 154's `limits` (measurement, bounds and unit, rule and its `w` multiple, `w`, `U` with its `k`), "U not declared" …
**Merged:** `agent/api/216-a-test-report-prints-each-limits-decision-rule-and-verify-rebuilds-it` (code `002ecc2`, ff from `48634b0`, then my `419d020`; doc `e8aecf77`, ff from `fef9c736`, then my `13c683e7`).
**Reviewer:** 1 finding — EMB-590
**Hardware debts:** none

### 21:56 — suite/064 the-agent-guide-places-the-test-tools
suite-wide, on the owner's behalf, after a silent window: `suite/agent-guide.md` §1.1 now places all 64 tools `embarch-api/src/tools.rs` registers on `origin/main` (`48634b0`; checked by diffing the registered names against the two lists: same set, each once) …
**Merged:** no branch: the leg's own commit `b3df6724` on `main`, then this fold. `check-docs.py` 12/12 on the result; `check-ownership.py --supervisor` over the leg's diff: nothing owner-reserved.
**Reviewer:** no findings.
**Hardware debts:** none

### 21:53 — core/179 a-test-runs-report-data-states-each-limits-decision-rule
New core decision 154 (`decisions/test-run-publish.md`, beside 148, which is not grown; index row; `interfaces/publish.md`'s field list): each `tests[]` entry of a Test run's `report-data.json` gains `decision_rule` (`{kind, w_multiple}`) and `limits` (each `measurement`, `unit`, `lower`, `upper` …
**Merged:** `agent/core/179-a-test-runs-report-data-states-each-limits-decision-rule` (code `b85a419`, ff from `478d61a`; doc `110d673c`, ff).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:45 — api/215 verify-checks-a-test-runs-zip-and-recomputes-its-verdicts
New api decision 146 (`decisions/verify-test-run.md`, index row; `interfaces/verify.md` says per check what a Test zip gets): a zip with `test-run.dsse.json` and `run.json` and no `record.dsse.json` is a Test run's, anything else a Study's, which verifies exactly as before (check 3's "not …
**Merged:** `agent/api/215-verify-checks-a-test-runs-zip-and-recomputes-its-verdicts` (code `48634b0`, ff from `aa15a2f`; doc `96617ba2`, the worker's `3a634493` cherry-picked onto `327d3e31`).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:44 — core/178 an-interrupted-test-run-keeps-its-verdicts-and-resumes-as-a-new-run
New core decision 153 (`decisions/test-run-resume.md`, index row): the executor writes `test-runs/<id>.checkpoint.json` (every `TestResult` so far plus the smoke findings, tmp-and-rename) after each test through a new `Env::checkpoint` hook …
**Merged:** `agent/core/178-an-interrupted-test-run-keeps-its-verdicts-and-resumes-as-a-new-run` (code `478d61a`, ff from `0a19be0`; doc `327d3e31`, ff). Also: `96617ba2`
**Reviewer:** no findings.
**Hardware debts:** a real Core restart under a Test run on the bench: the checkpoint, the interrupted seal, the resume and its go have met only unit tests. The native Windows build of Core. **Deploy debt:** the installed Core.

### 21:15 — api/214 a-test-runs-zip-carries-junit-and-ocp-exports-mapped-from-its-verdicts
New api decision 145 (`decisions/publish-test-export.md`, a new topic file; 144 amended to "five files" and its "Not done" list no longer names the exports, 199 B left; `interfaces/publish.md` …
**Merged:** `agent/api/214-a-test-runs-zip-carries-junit-and-ocp-exports-mapped-from-its-verdicts` (code `aa15a2f`, ff from `fc8059a`; doc `a45655ba`, the worker's `1652eaca` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 21:13 — core/168 core-keeps-the-host-awake-through-a-test-run
New core decision 152 (`decisions/test-run-awake.md`, a new topic file pointing at 135 to 137; `decisions.md` index row): a `KeepAwake` trait (`hold`, `release`) and a `Hold` drop guard in the new `src/keep_awake.rs` …
**Merged:** `agent/core/168-core-keeps-the-host-awake-through-a-test-run` (code `03579dc`, ff from `c21e9e6`, then my `0a19be0`: three comments cited "decision 151" (`core/172`'s) for 152, which the reviewer noted; doc `12bcbba0`, the worker's `550ac813` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** **the native Windows build of Core is the first test of the `cfg(windows)` half** (never compiled here). On the first Test run on the bench host: the host stays awake through an idle timeout while a run holds the lease, and sleeps normally after it ends; whether the request holds a Windows service's host awake at all is inferred, not measured. **Deploy debt:** the installed Core.

### 20:58 — api/213 a-test-run-publishes-as-one-zip
New api decision 144 (`decisions/publish-test-run.md`, a new topic file; `interfaces/publish.md` gains "A Test run's zip" and its `run_id` row is now true …
**Merged:** `agent/api/213-a-test-run-publishes-as-one-zip` (code `fc8059a`, ff from `1ae13b1`: the worker's `50e7bcc` plus my fix; doc `fdd06e23` and `c28ec796`, the worker's `9542e118` and my `dcd7d4d9` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:56 — core/172 a-test-runs-prompt-pending-event-names-its-kind-without-a-collision
New core decision 151 (`decisions/host-prompt.md`, beside 138; index row in `decisions.md`; `interfaces/host-studies.md` names the key): on the `PromptPending` event only, a Test run's prompt kind is written as `prompt_kind` through a `serialize_with` on the flattened field, so the event carries …
**Merged:** `agent/core/172-a-test-runs-prompt-pending-event-names-its-kind-without-a-collision` (code `c21e9e6`, ff from `ecfdea2`: the worker's `2020a2c` plus my comment fix; doc `b32d48c3`, the worker's `c85cddb2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:31 — api/212 the-identity-tools-name-the-persons-surfaces-on-a-refusal
New api decision 143 (`decisions/identity-acts.md`; a "Who makes an identity act" table in `interfaces/tools-topology.md`, which the instruments, bootload and dev-bench interface docs point to): a new `src/identity_act.rs` holds the ten identity acts …
**Merged:** `agent/api/212-the-identity-tools-name-the-persons-surfaces-on-a-refusal` (code `1ae13b1`, ff from `fe0f8b1`; doc `65720b7d`, the worker's `7281eda0` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:28 — core/177 core-serves-a-test-runs-revision-files
New core decision 150 (`decisions/test-run-publish.md`, with 149's "Not done" line pointing to it; `interfaces/publish.md`, the `interfaces.md` Publish row): `GET /test-runs/{run_id}/publish/{revision}/files/{*name}` (`test_file_handler` in `src/test_publish.rs`), same auth and lease stance as the …
**Merged:** `agent/core/177-core-serves-a-test-runs-revision-files` (code `ecfdea2`, ff from `5cd938b`; doc `4149f1db`, the worker's `37341cd2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:16 — api/211 the-test-ledger-reads-cores-run-log
New api decision 142 (`decisions/test-ledger.md`; `interfaces/tools-test-ledger.md`, the `tools.md` row): `test_show`, `test_pending` and `test_add` (MCP tools; CLI `test-show`, `test-pending`, `test-add`) replace `ledger_*`, removed with no alias (`src/ledger.rs` became `src/test_ledger.rs`) …
**Merged:** `agent/api/211-the-test-ledger-reads-cores-run-log` (code `fe0f8b1`, ff from `d53ab44`, two commits; doc `7613c32b`, the worker's `d7504ba3` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 20:14 — core/176 discard-refuses-the-agent-on-a-study-a-published-test-run-rests-on
Split this leg, at `28d227f9`: EMB-582 into this task, EMB-581 into `core/177`, EMB-379 into `api/211`, EMB-335 into `api/212` (all `filed`, Fleet Working) …
**Merged:** `agent/core/176-discard-refuses-the-agent-on-a-study-a-published-test-run-rests-on` (code `5cd938b`, ff from `062b48d`; doc `1dd95525`, the worker's `948fff4c` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:50 — ui/126 compact-ui
Size debt paid: `embarch-ui/spec/tabs.md` 9,334 to 9,034 B, out of reserve (threshold 9,039; the task said 9,160, it had grown since). The worker cut the file's provenance paragraph to "Split from ../spec.md." and "no Slack bar since 2026-10-29;" from the Desk row (ui decision 63's tombstone …
**Merged:** `agent/ui/126-compact-ui` (doc only, `3ad3b506`, the worker's `753078d0` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green; `check-doc-size.py --pressure` no longer lists the file.
**Reviewer:** no findings.
**Hardware debts:** none

### 19:48 — chat/051 compact-chat
Size debt paid, both files: `embarch-chat/spec.md` 9,318 to 9,015 B (threshold 9,039) and `open.md` 4,298 to 3,913 B (threshold 3,919), both out of reserve per `check-doc-size.py --pressure` on the merge result …
**Merged:** `agent/chat/051-compact-chat` (doc only, `1232366d`, the worker's `fe7e6fa5` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green.
**Reviewer:** no findings.
**Hardware debts:** none

### 19:47 — core/175 core-publishes-a-test-run
New core decisions 148 and 149 (`decisions/test-run-publish.md`, a new topic file: adding them to `decisions/publish.md` would have put that file at 15 KB against its 12 KB cap, so the worker split rather than grew it …
**Merged:** `agent/core/175-core-publishes-a-test-run` (code `062b48d`, ff from `ea7609c`; doc `2646346b`, the worker's `d36d35d6` cherry-picked).
**Reviewer:** 1 finding — EMB-582
**Hardware debts:** none

### 19:45 — api/210 the-person-acts-from-the-terminal
New api decision 141 (`decisions/person-verb.md`, a new topic file; `interfaces/tools-person.md`, linked from `interfaces/tools.md`): `embarch-api person confirm <hash> | go <run> | answer <run> <prompt> [value] [--cancel] | unit <key> --serial --revision | name <name>` …
**Merged:** `agent/api/210-the-person-acts-from-the-terminal` (code `d53ab44`, ff from `ee8dd30`; doc `b2567178`, the worker's `93f4de85` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:18 — ui/127 the-core-identity-line-reads-the-mode-core-reports
Ui decision 112 amended in place (`decisions/core-identity.md`, its index line too): the identity line's mode is now read from `StatusResponse.mode` (api decision 139), not derived from the attestation's match; `None` reads `mode unknown`, never `service` …
**Merged:** `agent/ui/127-the-core-identity-line-reads-the-mode-core-reports` (code `83d32db`, ff from `62dd46a`; doc `8fd09b95`, the worker's `3e3063a7` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:16 — chat/050 a-container-login-starts-claude-inside-the-agent-container
New chat decision 122 (`decisions/logins.md`): a login may be `embarchChat.logins.<name>.container = { record, manifestPath? }`, where `record` is the agent's `container.toml` (what `embarch agent` writes), re-read at every chat start or resume …
**Merged:** `agent/chat/050-a-container-login-starts-claude-inside-the-agent-container` (code `fc235ad`, ff from `b7e37c8`; doc `262d08f7`, the worker's `a6bd023b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** the first container session on the owner's machine (`Hardware: verify-only`, written in the retired task): a chat starts in the container; its transcript is found under the exchange folder and resumes after an idle close and after a window reload; a handoff stays in the container; no host hook runs; a stopped container shows the `embarch agent up` line (Podman's "not running" text unverified); rewind and the interrupted-step rerun in a container chat.

### 19:14 — api/208 verify-re-evaluates-step-outcomes-and-re-parses-step-numbers
New api decision 140 (`decisions/verify.md`; 120 amended so it no longer says check 2 is always partial; `interfaces/verify.md` row 2): `verify`'s check 2 finds each `events.json` step in the signed `study.json` by `list`, `index` and `inner_index` and recomputes an Exchange step's outcome from its …
**Merged:** `agent/api/208-verify-re-evaluates-step-outcomes-and-re-parses-step-numbers` (code `ee8dd30`, ff from `94be2fa`; doc `87500ca6`, the worker's `92f6c9f2` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 19:12 — core/174 core-keeps-a-manual-verdict-a-units-serial-and-the-persons-name
New core decision 147 (`decisions/manual-verdicts.md`, a new topic file, with `interfaces/manual-verdicts.md`): a manual verdict, a unit's serial and board revision, and the person's name are each a run-log entry, so the chain recomputes over them and a later declaration is a new entry whose GET …
**Merged:** `agent/core/174-core-keeps-a-manual-verdict-a-units-serial-and-the-persons-name` (code `ea7609c`, ff from `018a6e7`; doc `512fd1b7`, the worker's `564586d3` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:47 — ui/123 compact-ui
Size debt paid: `embarch-ui/decisions/live-study.md` 11,539 to 10,999 B, out of reserve (threshold 11,059). Cuts are rationale prose only, in decisions 31, 32, 33, 60 and 64; 109 untouched; no number or heading changed …
**Merged:** `agent/ui/123-compact-ui` (doc only, `dbfc81ad`, the worker's `babbda92` cherry-picked; no code branch). `check-docs.py` 12/12 on the merge result; ownership green; `check-doc-size.py --pressure` no longer lists the file.
**Reviewer:** no findings.
**Hardware debts:** none

### 18:45 — chat/049 the-ghost-text-pause-check-passes-under-load
New chat decision 121 (`decisions/assistant.md`, beside 120, the same page-clock mechanism): the webview stand-in stamps every post with `performance.now()` and records the page's last `input` event, and the check asserts the first ghost post comes at least 300 ms after the last keystroke, in one …
**Merged:** `agent/chat/049-the-ghost-text-pause-check-passes-under-load` (code `b7e37c8`, ff from `f54c3b8`; doc `0c058ca2`, the worker's `3b606437` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:43 — api/207 the-client-status-carries-cores-mode-and-keyid
New api decision 139 (`decisions/client-crate.md`): the shared client's `StatusResponse` gains `mode` and `keyid` (core decision 129), each `Option<String>` with `#[serde(default)]`; `None` means a Core that predates them and reads as unknown, never `service` …
**Merged:** `agent/api/207-the-client-status-carries-cores-mode-and-keyid` (code `94be2fa`, ff from `37e5289`; doc `895aeec3`, the worker's `e5b4863e` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:42 — core/173 a-test-runs-amended-study-record-is-bound-in-the-run-log
New core decision 146 (`decisions/test-run-record.md`), fixing the contradiction the `core/170` reviewer found (EMB-579): the amend stays and the amended hash is bound in the chain …
**Merged:** `agent/core/173-a-test-runs-amended-study-record-is-bound-in-the-run-log` (code `018a6e7`, ff from `b2e195d`; doc `33667240`, the worker's `bcb22408` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:08 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind
New ui decision 113 (`decisions/operator-prompt.md`, now 10,701 B, out of reserve): the prompt's kind is read from `GET /study/{id}`'s `pending_prompt`, not the event (api decision 137, until EMB-577 lands as `core/172`): on each `PromptPending`, `follow` spawns one `get_study_status` read, and …
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `62dd46a`, ff from `59c5e5a`; doc `95fedf4a`, the worker's `6c06a896` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 18:06 — dev-bench/053 pd-bench-reports-pd-timings-on-its-own-clock
New dev-bench decision 69 (`decisions/pd-bench.md`): a new `pd times` command, chosen over extra `pd status` lines so a test parsing one interval does not have to find it among unrelated lines (the owner may strike it) …
**Merged:** `agent/dev-bench/053-pd-bench-reports-pd-timings-on-its-own-clock` (code `e3a73a0`, ff from `06ef18d`; doc `41aa818c`, the worker's `5e5ab03e` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on each shield: compare `pd times` with a probe on CC (attach, `pd max`, `pd keepalive off` against a PPS source, then `pd times`); record which callback stamps each event and so what each interval includes; record the kernel tick's resolution on the G0B1 and switch to `k_cycle_get_32` if it is coarser than the 100 us a PD timing needs; confirm a Hard Reset the bench sends is never stamped as received, on both roles (`tasks/dev-bench/053`, retired in this fold).

### 18:03 — core/170 a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against
New core decision 145 (`decisions/test-run-record.md`, beside 144): a study is sealed before it is judged, so when a Test run ends Core amends each of its studies' `record.dsse.json` just before the run's own record (144) hashes it: `Sealer::amend_for_test` keeps every other byte of the Statement …
**Merged:** `agent/core/170-a-test-runs-study-record-carries-its-verdict-and-what-it-ran-against` (code `b2e195d`, ff from `81ab021`; doc `44740e1a`, the worker's `444a6b22` cherry-picked).
**Reviewer:** 1 finding — EMB-579
**Hardware debts:** one real Test run on a bench, under the lease: the DUT's and each bench board's image status, the identities and `*IDN?` replies, and an answered observation prompt's scope reach the amended record, and it still verifies. The native Windows build of Core. **Deploy debt:** the installed Core amends no study record until redeployed.

### 18:02 — api/205 declare-instrument-passes-metrology-and-calibration
New api decision 138 (`decisions/instruments.md`): `declare_instrument` takes `metrology` (a list), `calibration` and `clear_calibration`; `declare-instrument` takes `--metrology '<json>'` (repeatable), `--calibration '<json>'`, `--clear-metrology` and `--clear-calibration` …
**Merged:** `agent/api/205-declare-instrument-passes-metrology-and-calibration` (code `37e5289`, ff from `f2156f1`; doc `168f3fca`, the worker's `23285338` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:36 — api/206 the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value
one cross-repo landing by my own hands, announced and parked first (`#embarch-fleet` ts `1795737738.383629`, 30 minutes elapsed with no reply): adding `value` to `PromptAnswerRequest` and two fields to `StudyEvent::PromptPending` broke two struct literals in `embarch-ui`, so I landed `api/206` and then a three-line `embarch-ui` commit of my own (`value: None` in the answer route's literal …
**Merged:** `agent/api/206-the-client-prompt-types-carry-a-test-run-prompts-kind-and-answer-value` (code `f2156f1`, ff from `8f0ba84`; doc `0831bbc2`, the worker's `c88a9aba` cherry-picked). Consumer commit `embarch-ui` `59c5e5a` (ff from `e5edeac`), mine.
**Reviewer:** no findings.
**Hardware debts:** none

### 17:09 — chat/048 the-cards-checks-pass-under-load
New chat decision 120 (`decisions/assistant.md`): `waitAssist` is now one async script that polls the page's own posts against a deadline on the page's clock, 15 s. No product code changed …
**Merged:** `agent/chat/048-the-cards-checks-pass-under-load` (code `f54c3b8`, ff from `3f9a95f`; doc `e07a8173`, the worker's `4c7aa074` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:07 — ui/125 the-ui-shows-which-core-it-is-talking-to
New ui decision 112 (`decisions/core-identity.md`): one line under the top bar, so on every tab, built from the client's `attestation()` in the snapshot poll (`CoreIdentity::from_attestation`, `Snapshot.core_identity`): `Core: service|development, <16 hex>, matches the installed fingerprint|does …
**Merged:** `agent/ui/125-the-ui-shows-which-core-it-is-talking-to` (code `e5edeac`, ff from `1e49270`; doc `b3c27a83`, the worker's `b107d287` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 17:05 — core/169 a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test
New core decision 144 (`decisions/test-run-record.md`): a Test run is sealed as it ends — finish, cancel or deadline — before `end_run` releases the run lock, as `test-runs/<run_id>.test-run.dsse.json` (the worker added the `<run_id>.` prefix to the task's name), predicate …
**Merged:** `agent/core/169-a-test-run-leaves-a-signed-run-record-and-a-run-log-entry-per-test` (code `81ab021`, ff from `90a6cc9`; doc `d33cc7f6`, the worker's `49924869` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** one real Test run on a bench, under the lease, leaves `test-runs/<id>.test-run.dsse.json` and a `test_run` run-log entry, and a cancelled one names every selected test with a verdict or reason. The native Windows build of Core (nothing new is `cfg(windows)`). **Deploy debt:** the installed Core signs no Test run record until redeployed.

### 14:23 — dev-bench/051 pd-bench-has-an-idle-command-and-a-hello-line
New dev-bench decision 68 (`decisions/pd-bench.md`): `pd idle` puts keep-alive on, DR/PR/Request replies back to accept and the `pd max` choice, restores the devicetree's Source_Capabilities on the DRP1M1, drops any contract and ends `pd: ok`, or `pd: error <what>` when VBUS did not discharge or a …
**Merged:** `agent/dev-bench/051-pd-bench-has-an-idle-command-and-a-hello-line` (code `06ef18d`, ff from `5cff766`; doc `68444e79`, the worker's `3d104147` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** for the PD bench's characterisation session, on both shields: set `keepalive off`, `dr reject`, `pr reject`, `answer wait`, `srccaps` and `pps`, run `pd idle`, and read `pd status` and `pd srccaps` back at their defaults; a sink holding a PPS contract — `pd idle` sends the Hard Reset and renegotiates at the default choice; the DRP1M1 sourcing to a sink — VBUS under 0.6 V within tSafe0V and the port attaches again from scratch; `pd hello` prints the right version, commit (with `-dirty` when it was) and shield on each build (`tasks/dev-bench/051`, retired in this fold).

### 14:20 — chat/046 the-linker-offers-a-studys-capture-or-trace
New chat decision 119, in a new topic file `decisions/references-studies.md` (so `references-kinds.md` stays out of reserve): the 💡 linker reads `embarch-api --json list-studies --limit 20` through `chat/043`'s runner and offers one entry per tap, `trace` when its `encoding_kind` is …
**Merged:** `agent/chat/046-the-linker-offers-a-studys-capture-or-trace` (code `3f9a95f`, ff from `3587735`; doc `fe801c24`, the worker's `40a529d0` cherry-picked, no conflict).
**Reviewer:** no findings.
**Hardware debts:** none

### 14:18 — ui/124 the-ui-shows-a-go-card-and-a-prompts-kind
New ui decision 111 (`decisions/confirm-tab.md`): the go card lives in the Confirm tab (the worker's call, its reason in 111). New routes `GET /api/test-runs/{run_id}/card` and `POST /api/test-runs/{run_id}/go` …
**Merged:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind` (code `1e49270`, ff from `4a2e694`; doc `4d6ec789`, the worker's `31f54bc3` cherry-picked).
**Blocked:** `agent/ui/124-the-ui-shows-a-go-card-and-a-prompts-kind`'s prompt-modal half — waits on EMB-575 (client prompt fields); task `blocked` with `Unparks when:` EMB-575 landing. EMB-384 stays in Fleet Working.
**Reviewer:** no findings.
**Hardware debts:** none

### 14:15 — core/167 a-bench-is-smoke-checked-before-its-first-test
New core decision 143 (`decisions/smoke-check.md`): before a bench's first test, the first bench included, `drive` calls `Env::smoke_check`, which checks the bench's declared signals, roles and instruments, `validate` for the DUT and each bench board, each board's hello line (an echo alone is not …
**Merged:** `agent/core/167-a-bench-is-smoke-checked-before-its-first-test` (code `90a6cc9`, ff from `ca34d61`; doc `06b5099e`, the worker's `a93b889d` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** the smoke check once on a real bench, in a two-bench fixture run under the lease: a DUT, one bench board with a hello line, one instrument with a declared calibration (`tasks/core/167`, retired in this fold, lists what to confirm). `SMOKE_WAIT_MS` (2 s) and `SMOKE_PORT_WAIT_MS` (5 s) are chosen, not measured. The native Windows build of Core. **Deploy debt:** the installed Core runs no smoke check until redeployed.

### 13:55 — chat/047 the-long-chat-scroll-check-settles-before-it-reads
New chat decision 118 in `decisions/timeline.md`. The worker's evidence: a one-check copy failed 16 of 25 runs under 24 busy loops before the fix, 0 of 25 after; the full check passed 20 of 20 under a lighter `cargo test` load …
**Merged:** `agent/chat/047-the-long-chat-scroll-check-settles-before-it-reads` (code `3587735`, ff from `701a019`; doc `adc0f48d`, the worker's `7dd99028` cherry-picked, rebased over the owner's `6f6fcbd8`).
**Reviewer:** no findings.
**Hardware debts:** none

### 13:54 — study-designer/100 check-test-refuses-a-study-that-does-not-match-its-hash
The study-hash chain that `study-designer/099` started on 2026-11-25 is complete: `hil_check::check_test` now refuses a host study that does not hash to its test's `study.hash` by `hil_test::study_hash`, as `Rule::StudyHashMismatch` on `study.hash`, naming the study file and both hashes …
**Merged:** `agent/study-designer/100-check-test-refuses-a-study-that-does-not-match-its-hash` (code `8bd6bcc`, ff from `ebbaaca`; doc `e067e275`, the worker's `fcaeea23` cherry-picked, rebased over the owner's `6f6fcbd8`).
**Reviewer:** no findings.
**Hardware debts:** none

### 11:56 — api/204 test-propose-fills-a-studys-hash-with-study-hash
reversals row 118 added (`reversals/rows-115-115.md`): a Test's `study.hash` had three conventions across three repos (the file's bytes in `embarch-api`, whatever the fixture said in Core, `study_hash` in the crate), found when the crate's refusal turned two consumers red on 2026-11-25; all three now call `study_hash` …
**Merged:** `agent/api/204-test-propose-fills-a-studys-hash-with-study-hash` (code `8f0ba84`, ff from `fc1a33b`; doc `859faca3`, the worker's `85b9699b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none

### 11:54 — core/166 the-test-run-prepare-checks-each-study-against-its-hash
`POST /test-runs`'s prepare now hashes every premade study it was sent with the crate's `hil_test::study_hash` and compares it with its test's `study.hash`; a mismatch is refused `422` naming the test, the file and both hashes, and nothing is registered …
**Merged:** `agent/core/166-the-test-run-prepare-checks-each-study-against-its-hash` (code `ca34d61`, ff from `5964670`; doc `be9e5e76`, the worker's `1a756f99` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none
## 2026-11-25 — 64 units

*Folded by an embarch-log-folder agent on 2026-11-26 (the leg that follows the owner's `/fleet stop`): per-unit narrative reasoning, gate transcripts, budget lines and "least sure about" notes dropped; git holds the diffs and the changes themselves. Every SHA, reviewer line, board-naming debt and blocked line kept, one block per unit, newest first. The day's ten "Leg end, to carry" paragraphs are folded into the carry-forward below.*

**Carry forward (state at the last leg's end, 16:07).**
- **The fleet is stopped.** The owner's `/fleet stop` (about 16:01) ended the last leg; its `.fleet/stop` marker was deleted after landing, the pump latch is gone, and there was no channel message to reply in. Last leg: 4 of 4 landed (`study-designer/101`, `api/203`, `core/165`, `umbrella/118`), none blocked; budget PROCEED, 5-hour 24%, weekly 21%.
- **`study-designer/100` stays `blocked` until both `api/204` (EMB-570) and `core/166` (EMB-555's Core half) have landed**, and its landing leg must re-test `embarch-api` and `embarch-core` after `cargo clean -p embarch-study-designer`. Why: `study-designer/099` was landed, turned two consumers red (`embarch-api` hashes the study file's bytes into `study.hash`, Core's fixture does the same) and was reverted the same leg; `api` and Core `main` were red 15:14 to 15:28. The supervisor's consumer gate had not been real: swapped path dependencies were not rebuilt (mtime fingerprint), so both tested the old crate. **EMB-572** (fleet, shared-crate gate: a shared-crate unit's gate runs no consumer's tests) is the open fix, moved to Todo as `Scope: fleet`. `study-designer/101` landed the additive half (`study_hash` plus decision 113, no refusal); until `api/204` lands, `embarch-api`'s test-plans decision (`study.hash` is the file's bytes) and 113 disagree on what the field means.
- **Dispatchable now:** `api/204`, `core/166`, `chat/046` (captures and traces as linker kinds), `dev-bench/051` (`pd idle` and `pd hello`, verify-only), `ui/123` (compact `live-study.md`, due 2026-12-09) and `ui/124` (the go card, unparked by `api/203`); five scopes, `ui` twice. `api/201` (compact `embarch-api/spec.md`, due 2026-12-09) is `blocked`. Fleet Ready: 21 unsplit issues. New issues: EMB-571 (chat's webview scroll check fails under load; `chat/045` landed past it), EMB-572, EMB-570.
- **Hardware / bench:** bench tasks `api/059` and `dev-bench/038` stay `open`, no board; hardware buffer last refreshed 09:38, not refreshed since. Debts owed this day are in the per-unit lines below (`umbrella/118`'s five `deploy-core` runs on the Windows machine and `core/165`'s image readback per chip family are the largest).
- **Deploy debts:** the installed `embarch` binary keeps the old `deploy-core` behaviour until rebuilt from `main` (after that it no longer overwrites or restarts the service; new umbrella decision 68 in `decisions/deploy.md`, `--restore-service` to go back); the installed service Core still answers the old plain-text `422` for a missing measurements file until redeployed with `core/164` (`api/202` tolerates both).
- **Stale, the owner's:** `embarch-dev-workflow.md` §4a (and its step 3) still describes stop, copy over the service's binary, start and verify the service. `embarch-analog-capture-proposal.md` is in neither `reserved` nor `fleet_writable` (`check-ownership.py --supervisor`), still unclassified all day. `notes/hil/06-report-and-publish.md` line 36 still names `hil-run.md` for a Study's export and check (`fold-commit.py` refuses to stage `notes/`; resolves through the stub; not seen resolved by any later leg). `embarch-ui`'s committed `Cargo.lock` is behind `embarch-api`'s `embarch-core-client`, so any ui build rewrites it. Core decision 133 (`decisions/definitions.md`) is 233 B over its per-decision limit. `embarch-api/interfaces/tools-tests.md` still says of `run_test` that "no code path calls the go", less precise than api decision 135.
- **Decisions made on the owner's behalf (marked the owner's to strike in their entries):** two suite passes, both announced and run as a leg's last unit after a silent window: `suite/062` (host step parses a number, a prompt has a kind; `HOST_TYPE_SCHEMA_VERSION` 24 to 25, wire stays 17; study-designer decision 108; `number_grammar` moved from `pdf-text` to `std`) and `suite/063` (an instrument's declaration carries its metrology; topology decision 51; `Instrument` lost its `Eq` derive; plan choice 14, metrology in Core's own store, marked the owner's to strike). Deploy loop: umbrella decision 68 (above). Image readback: core decision 142 (per-chip `ImageLog` entry is an argument; the `EMBARCH_BENCH_FIRMWARE_LIST` variable's name is a recommendation). Nothing calls `readback` yet.
- **Linear:** flapped on the 2,500/hour cap through the morning legs (finished and filed through single calls), and the free-plan issue cap spooled up to 8 entries; by 13:40 the spool was empty and Linear answered. Two reviewer findings were left unfiled at the cap (`tasks/api/197`, and core `4ef12e6` fixed forward). Refill gate fired on depth and spread at the 15:39 leg; Fleet Ready was split rather than the `open.md` sources swept, so **no `Spread sweep` line was written this day** (the newest is `Spread sweep: nothing filed (2026-11-24 00:23)` in the 2026-11-24 entry).
- **Transient:** one `git push` to `embarch-api` refused with SSH `publickey` and went through on retry; if it recurs it is the agent's SSH access. The chat compaction-test flake (`wire.test.mjs`) hit again under the full run (fixed by `chat/045`).
- **The log carries `## 2026-11-24 — 43 units` twice** (about ten lines apart, the first apparently a partial copy of the second); left untouched, not part of this fold.

---

### 16:07 — umbrella/118 deploy-core-installs-a-development-core-beside-the-service
But this changes the owner's own deploy loop: once the umbrella binary is rebuilt from `main`, `embarch deploy-core` no longer overwrites and restarts the service.
**Merged:** `agent/umbrella/118-deploy-core-installs-a-development-core-beside-the-service` (code `5533608`, ff from `4d99988`; doc `7e726d5a`, the worker's `c3265055` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** five `deploy-core` runs on the Windows machine, each checked against `/status`: with the service running; refused with a study in flight; with `--cancel-run`; `--restore-service`; a second deploy while the development Core runs (from `tasks/umbrella/118`, retired in this fold). **Deploy debt:** the installed `embarch` binary keeps the old behaviour until rebuilt.

### 16:06 — core/165 core-reads-an-image-back-through-the-probe
New `src/readback.rs`: `readback(core, Board::{Dut, Bench}, entry, list) -> ImageStatus` reads each segment of a board's newest `flashed-images.jsonl` entry back through `CoreAccess` in chunks of `MAX_WORDS` (one …
**Merged:** `agent/core/165-core-reads-an-image-back-through-the-probe` (code `5964670`, ff from `74d3530`; doc `69ef51af`, the worker's `20878c42` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** whether a whole image reads back through the probe on each chip family Core flashes (nRF54L, nRF54H, STM32 G0 and F4, ESP32-C5), especially where Core flashes with the vendor tool rather than the probe library; recorded in `tasks/core/165` (retired in this fold, so the debt lives here and in decision 142). The native Windows build of Core.

### 16:05 — api/203 the-core-client-carries-a-person-only-go
`embarch-core-client` gains `CoreClient::test_run_go(run_id, run_hash, nonce)`, posting `{run_id, run_hash, nonce}` to `/test-runs/{id}/go` through `send` with whichever bearer the client was built with
**Merged:** `agent/api/203-the-core-client-carries-a-person-only-go` (code `fc1a33b`, ff from `7b45e83`; doc `5965c768`, the worker's `b31493ac` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the method has met a mock Core only. Owed with `ui/124`: one go given from the UI against a real Core with a prepared run.

### 16:04 — study-designer/101 study-hash-lands-alone
The additive half of the reverted `study-designer/099`: `hil_test::study_hash(&HostStudy)` (the `definition_hash` of the study, SHA-256 of its canonical JSON) is back, and `check_test` refuses nothing new (the `StudyHashMismatch` …
**Merged:** `agent/study-designer/101-study-hash-lands-alone` (code `ebbaaca`, ff from `1dfdae1` through the worker's `01f983e`, the revert of the revert; doc `d08a42a8`, the worker's `5c44041a` cherry-picked onto the owner's `ebab3222`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 15:39 — study-designer/099 one-function-fixes-a-premade-studys-hash
I landed this unit, it turned two consumers red, and I reverted it the same leg.
**Merged:** `agent/study-designer/099-one-function-fixes-a-premade-studys-hash` (code `7391457`, ff from `0caf76b`; doc `a9c73a20`, the worker's `1bc42244` cherry-picked), **then reverted**: code `1dfdae1`, doc `29869b13`.
**Reviewer:** 1 finding — EMB-570
**Hardware debts:** none.
*Also cited:* `8e89c85c`.

### 15:34 — chat/045 the-compaction-test-stops-racing-and-holding-the-run
Re-landed from the 429'd leg (see `core/164`'s entry). Only `test/wire.test.mjs` changed
**Merged:** `agent/chat/045-the-compaction-test-stops-racing-and-holding-the-run` (code `701a019`, ff from `1109bb0`; doc `40155087`, the worker's `2a51292b` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none.

### 15:33 — api/202 read-the-no-measurements-refusal-by-a-stable-code
Re-landed from the 429'd leg (see `core/164`'s entry). `embarch-core-client`'s `MeasurementsRefusal::NoMeasurements` is recognised by the `422` status alone, a body `code` of `"no_measurements"` (core decision 141) or none (an …
**Merged:** `agent/api/202-read-the-no-measurements-refusal-by-a-stable-code` (code `7b45e83`, ff from `9214394`; doc `cefcc941`, the worker's `6b507571` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the refusal has met a mock Core only. Owed against a real Core once redeployed with `core/164`: `study-measurements` on a run with no file reads as no-measurements from the JSON body.
*Also cited:* `1dfdae1`.

### 15:32 — core/164 the-measurements-route-serves-a-host-studys-file
Re-landed from the leg that claimed `chat/045`, `study-designer/099`, `api/202` and `core/164` at about 13:45 and died on a 429 (spend limit) before folding anything
**Merged:** `agent/core/164-the-measurements-route-serves-a-host-studys-file` (code `74d3530`, the worker's `c5a34af` rebased onto `3f41ff8`, the owner's EMB-563 commit; doc `939540af`, the worker's `47d39599` cherry-picked).
**Reviewer:** no findings.
**Hardware debts:** none to a board. The native Windows build of Core. **Deploy debt:** the installed service Core still answers the old plain-text `422` until redeployed; `api/202` tolerates both.
*Also cited:* `1dfdae1`, `5b8d493`.

### 13:40 — chat/044 the-linker-offers-a-linear-project-or-document
`RefIndex` gains optional `projects` and `documents` (`IndexProject`, `IndexDocument`), parsed by `DeskClient.refs()`, read as `[]` from a desk that omits them.
**Merged:** `agent/chat/044-the-linker-offers-a-linear-project-or-document` (code `1109bb0`, ff from `5f97b9f`; doc `b9f70a41`, the worker's `b55a7728` cherry-picked onto `6cdaa4a3`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the kinds have met only the invented index, never a real Linear workspace through a real desk.
*Also cited:* `b4766574`.

### 13:38 — ui/121 the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input
A resume of the unit that stopped on my split error: `api/199` added the client methods, and this leg put the worker on the old branches, `embarch-ui`'s fast-forwarded to `origin/main` and `embarch-doc`'s with `origin/main` …
**Merged:** `agent/ui/121-the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input` (code `68ab18f`, ff from `9e8f193`, then my `b3cfc4b`; doc `cefa026c`, the worker's `e76f38f0` cherry-picked onto `bf632cc4`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the tab has met a stub Core only and has not been opened in a browser. Owed: open Confirm against a Core holding an unconfirmed custom test, confirm one, and see the run log's `confirmed` entry record surface `ui`.
*Also cited:* `0caf76b`, `5b8d493`, `69223acd`, `9214394`.

### 13:36 — core/163 an-instruments-metrology-and-calibration-reach-its-measurements
`PUT /instruments` already took the shared crate's `Instrument` with `metrology` and `calibration` and already recorded its scope in `Declarations`, so `api.rs` is unchanged.
**Merged:** `agent/core/163-an-instruments-metrology-and-calibration-reach-its-measurements` (code `0ddfd05`, ff from `80f6798`; doc `39222b88`, the worker's `07b8e0ed` cherry-picked onto `c0c88cc1`).
**Reviewer:** no findings.
**Hardware debts:** a host study on a real bench with a declared instrument whose calibration is current, and one past due, to see both stamps in `measurements.json`. The native Windows build of Core. **Deploy debt:** the installed service Core stamps no metrology until redeployed. The `*IDN?` serial check waits for the smoke check (EMB-368).
*Also cited:* `0caf76b`, `5b8d493`.

### 13:35 — api/200 run-test-prepares-a-test-run-and-test-status-watches-it
New `src/hil_run.rs`: `run_test` (MCP tool, CLI `run-test`) turns a saved plan, or a suite with test ids, tags or `all`, into a plan through `hil_expand::expand` (a refusal there is the crate's, with Core not called), posts the …
**Merged:** `agent/api/200-run-test-prepares-a-test-run-and-test-status-watches-it` (code `9214394`, ff from `14ea8f3`; doc `b33d607e`, ff from `a42e1592`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the tools have met only a mock Core. Owed against a real Core (in `open/bench-verification.md`): that it reproduces the crate's `run.json` byte for byte, accepts the base studies a template needs beside the expanded ones, and serves a premade suite's studies at `GET /definitions/<study hash>`.

### 12:26 — chat/043 the-linker-offers-a-bench-instrument
Landed from a dead worker's uncommitted tree, gated by me — the next leg should know this unit's provenance.
**Merged:** `agent/chat/043-the-linker-offers-a-bench-instrument` (code `5f97b9f`, ff from `fd154a5`; doc `e6522cf1`, the recovered `14bc0506` cherry-picked onto `14e85de7` and reworded).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the kind has met only `test/fake-api.mjs`, so one draft naming an instrument in a chat folder with a real `embarch-api` and a declared bench is owed.
*Also cited:* `0facb46`, `9e10f685`.

### 12:00 — ui/122 a-running-study-has-a-cancel-button-in-the-ui
Re-landed from the leg killed at about 10:15 (its worker had pushed both branches).
**Merged:** `agent/ui/122-a-running-study-has-a-cancel-button-in-the-ui` (code `9e8f193`, ff from `508b1e6`; doc `6a967a4a`, the worker's `20bedac9` cherry-picked onto `68797785`).
**Reviewer:** no findings.
**Hardware debts:** none to a board; the button has met a stub Core only, so one real cancel of a running study from the UI against a live Core is owed.
*Also cited:* `0caf76b`, `14ea8f3`.

### 11:58 — core/162 a-test-run-opens-a-setup-window-between-benches
Re-landed from the leg killed at about 10:15 (its worker had pushed both branches).
**Merged:** `agent/core/162-a-test-run-opens-a-setup-window-between-benches` (code `80f6798`, ff from `9233136`; doc `384c208f`, the worker's `958de02a` cherry-picked onto `e12e81fc`).
**Reviewer:** no findings.
**Hardware debts:** a real two-bench fixture run on a bench, enrolling a board in the setup window between the two benches, in the person's session. The native Windows build of Core. **Deploy debt:** the installed service Core has no setup window until redeployed.
*Also cited:* `0caf76b`.

### 11:54 — api/199 the-core-client-calls-the-confirmation-routes
Re-landed from a killed leg: the leg that claimed `api/199`, `core/162`, `ui/122` and `chat/043` at 10:12 died with the Claude Code session at about 10:15 and folded nothing.
**Merged:** `agent/api/199-the-core-client-calls-the-confirmation-routes` (code `14ea8f3`, ff from `9f3f9e2`; doc `bdaaf7d9`, the worker's `666c137f` cherry-picked onto `17af2b2b`).
**Reviewer:** no findings.
**Hardware debts:** none; the methods have met only a mock Core.
*Also cited:* `047bb59d`, `0facb46`, `14bc0506`.

### 10:07 — ui/121 the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input
My split error, caught by the worker: Core serves the three confirmation routes, but `embarch-core-client` has no method for any of them, and its one-funnel test forbids the UI from sending around it, so the card cannot be built …
**Merged:** nothing in code. Doc: the worker's blocked note `4beb3058`, cherry-picked onto `a6586e07` as `c6713baf`, and my edit to it with the new task in this fold.
**Blocked:** `agent/ui/121-the-ui-shows-a-card-on-which-the-engineer-confirms-a-test-input` — the core client lacks the confirmation routes' methods; `blocked`, unparks when `api/199` lands. Its doc branch is pushed with the note; the `embarch-ui` branch never got a commit and was never pushed.
**Reviewer:** skipped (nothing landed: the unit stopped before writing code).
**Hardware debts:** none.

### 10:06 — umbrella/117 embarch-agent-starts-stops-and-checks-the-agents-container
New `src/agent_run.rs`: a `ContainerRuntime` trait (`build`, `image_exists`, `volume_create`, `run`, `stop`, `rm`, `exec`, `inspect`) over a `Process` seam, `CliRuntime` as Docker or Podman by binary alone (`docker()`/`podman()`, …
**Merged:** `agent/umbrella/117-embarch-agent-starts-stops-and-checks-the-agents-container` (code `4d99988`, ff from `82f5ef7`; doc `2988c6eb`, the worker's `b27e6987` cherry-picked onto `1fa92ad0`).
**Reviewer:** no findings.
**Hardware debts:** the owner's first container, with Docker or Podman installed and `init --container` run in a repo: `embarch agent up`; `embarch agent status`, every line `ok`; `embarch agent shell` and `shell --claude`; `docker inspect embarch-agent-<name>` against the vector in `container.toml`; `embarch agent down`, volume and exchange folder still there; then each from-memory item above. No runtime has ever run any of it.
*Also cited:* `0caf76b`, `9f3f9e2`.

### 10:04 — core/161 core-enforces-a-prompts-kind-by-the-tokens-scope
A prompt's kind is `run.json`'s `prompt_kinds` by step name, reaching the backend through a new `RunContext` passed to `run_study_blocking`
**Merged:** `agent/core/161-core-enforces-a-prompts-kind-by-the-tokens-scope` (code `9233136`, ff from `dc0bccc`: `c6ad3be` and `9233136`; doc `d6b058a1`, the worker's `84f2eee0` cherry-picked onto `e5f7df0d`).
**Reviewer:** no findings.
**Hardware debts:** a Test run on a real bench with a person answering an observation from a surface, the agent's token refused `403`, and a real instrument set listed as switched on. The native Windows build of Core. **Deploy debt:** the installed service Core enforces none of this until redeployed.
*Also cited:* `0caf76b`.

### 10:03 — api/198 a-tool-and-a-subcommand-cancel-a-running-study
`cancel_study` (MCP) and `cancel-study <study_id>` (CLI, `--json`) share `CoreClient::cancel_study`, new in `embarch-core-client` with `StudyCancelled {study_id, status}` (read before landing
**Merged:** `agent/api/198-a-tool-and-a-subcommand-cancel-a-running-study` (code `9f3f9e2`, ff from `0b36fcb`; doc `e5f7df0d`, ff from `dffe499b`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the tool has met only a mock Core.
*Also cited:* `1795624948`, `a1eff5c7`.

### 09:35 — umbrella/116 the-agents-container-makes-its-own-clone-on-first-start
`render_entrypoint_agent(&plan)` (and `_at(&plan, root)`, which puts every container path under a temp root for the shell test) in `src/agent.rs` renders the agent half of the entrypoint, run as uid 1000 after decision 63's root …
**Merged:** `agent/umbrella/116-the-agents-container-makes-its-own-clone-on-first-start` (code `82f5ef7`, ff from `dfad2a8`; doc `de5c194c`, the worker's `71a8ca94` cherry-picked onto `fd977ee4`).
**Reviewer:** no findings.
**Hardware debts:** the owner's first container: `git remote -v` shows one remote, `claude mcp list` from the clone shows `embarch`, `/work/.west/config` and `west list` look right, and an edit under `/outbox/embarch` survives a restart while a new person file arrives. The shell test ran on stub `git` and `claude`, so real git behaviour is unproven.
*Also cited:* `0b36fcb`, `0caf76b`, `be08040b`.

### 09:34 — core/160 core-runs-a-test-selection-test-by-test
New `src/test_executor.rs`: `drive` walks `run.json` against an `Env` trait (a fake in tests, `CoreEnv` on the real bench), bench by bench and test by test
**Merged:** `agent/core/160-core-runs-a-test-selection-test-by-test` (code `dc0bccc`, ff from `b0b10e7`; doc `fd977ee4`, ff from `67e9d52c`).
**Reviewer:** no findings.
**Hardware debts:** the real reset, the idle line and `run_study_blocking` have run over no bench: one run of a two-test fixture suite on a bench with a DUT and a board, through the person's go. The native Windows build of Core. **Deploy debt:** the installed service Core has neither the executor nor the route until redeployed.
*Also cited:* `0caf76b`.

### 09:17 — study-designer/097 compact-study-designer
A verbatim split, no text deleted: the "A Study's export and check" section (`run_status`, what a Study's run exports, the JUnit and OCP T&V exports, `verify`'s check table 0 to 9, what `verify` cannot recompute) moved from …
**Merged:** `agent/study-designer/097-compact-study-designer` (doc only, `9d167879`, the worker's `b9d305d6` cherry-picked onto `8d004762`; no code SHA).
**Reviewer:** no findings.
**Hardware debts:** none.

### 09:15 — api/197 test-files-are-written-through-the-person-writer
`hil_repo` has no file write of its own: `write_under_embarch` calls `ConfinedWriter::write_with`, a new form of the person writer that takes `overwrite` (false refuses an existing file, which keeps "a saved bench is never …
**Merged:** `agent/api/197-test-files-are-written-through-the-person-writer` (code `0b36fcb`, ff from `eb2f64d`: the worker's `f5ad7f2` and my `0b36fcb`; doc `8d004762`, ff from `047c959e`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the Windows branch of `person_writer` was edited and is unbuilt (already `tasks/api/193`'s debt).

### 08:52 — ui/120 a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted
New `src/bench/references.rs` scans `embarch/studies/*.json` (not recursive) and every `.json` under `embarch/tests/suites/` (the layout `api/196` pinned)
**Merged:** `agent/ui/120-a-config-a-saved-study-or-test-names-cannot-be-renamed-or-deleted` (code `508b1e6`, ff from `90668da`; doc `d318facc`, the worker's `6f029875` cherry-picked onto `efa8c712`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; the dialogs and the tweak to `tests/browser/drive_bench_configs.py` (Delete now waits on an async lookup) were not run in headless Firefox: one run of that script, plus a case with a fixture test naming a config.
*Also cited:* `0caf76b`, `eb2f64d`.

### 08:51 — umbrella/115 init-sets-up-the-agents-container-and-registers-the-repo
`embarch init --container [--runtime docker|podman]` renders `umbrella/112` to `114`'s outputs (Containerfile, `container.toml`, firewall script, a clone config template) into `~/.config/embarch/agents/<name>/` (Windows …
**Merged:** `agent/umbrella/115-init-sets-up-the-agents-container-and-registers-the-repo` (code `dfad2a8`, ff from `7b1c1f0`; doc `f3c21c52`, the worker's `53a497e5` cherry-picked onto `9cdb8dd2`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; native Windows is unrun (the `%APPDATA%`/`%LOCALAPPDATA%` folders are covered only by the pure resolver's test), and `west list` has never run against a real west workspace.
*Also cited:* `0caf76b`, `eb2f64d`.

### 08:49 — core/159 a-test-runs-go-takes-the-lease-and-starts-the-run
`POST /test-runs/{run_id}/go`, the person's token only (the agent's gets `403` from `person_middleware`, new `token_store::GO_ROUTES`)
**Merged:** `agent/core/159-a-test-runs-go-takes-the-lease-and-starts-the-run` (code `b0b10e7`, ff from `4ef12e6`; doc `b141b632`, the worker's `5fbc7e56` cherry-picked onto `01743947`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core. **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-366 and the person's terminal.
*Also cited:* `0caf76b`.

### 08:46 — api/196 test-plans-in-the-repo-and-proposals-sent-to-core
I pinned the tests layout across two scopes at the split, so `api/196` and `ui/120` could run in one wave
**Merged:** `agent/api/196-test-plans-in-the-repo-and-proposals-sent-to-core` (code `eb2f64d`, ff from `add96ab`; doc `44c88c7d`, ff from `3c9d68cb`).
**Reviewer:** 1 finding — `tasks/api/197` (unfiled: Linear refused at its issue cap; I wrote the task and dropped the spool entry so it is not filed twice)
**Hardware debts:** none from a board; everything ran against `MockCore`, a real Core's card should show the hash `TestDef::hash()` gives, and the Windows `std::fs` writes in `hil_repo` are unbuilt (all in `open/bench-verification.md`).
*Also cited:* `1795620494`, `97b00fdd`.

### 08:19 — chat/041 the-linker-offers-kconfig-symbols-and-devicetree-nodes
The 💡 linker offers two more kinds from `chat/040`'s one `embarch-atlas refs --json` read, with no second run
**Merged:** `agent/chat/041-the-linker-offers-kconfig-symbols-and-devicetree-nodes` (code `fd154a5`, ff from `4093c1a`; doc `4aa3d7e0`, the worker's `3171871b` cherry-picked onto `d52660fd`).
**Reviewer:** no findings.
**Hardware debts:** none; never seen against a real atlas or window (said in 115 and the feature row).

### 08:08 — umbrella/114 the-agents-container-image-and-west-workspace-mounts
`src/agent.rs` gains, pure: `render_containerfile(&plan)` (the plan gains `toolchain
**Merged:** `agent/umbrella/114-the-agents-container-image-and-west-workspace-mounts` (code `7b1c1f0`, ff from `d9a4b8a`; doc `318ec292`, the worker's `6b8fc8fa` cherry-picked onto `01032278`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; no image has been built, so every from-memory line and the nft backend of Debian's `iptables` under 63's rules are unverified until EMB-448's first build and start.
*Also cited:* `0caf76b`.

### 08:07 — core/158 core-prepares-a-test-run-and-serves-its-go-card
`POST /test-runs` (either token) takes `{run, plan, suite?, studies}`
**Merged:** `agent/core/158-core-prepares-a-test-run-and-serves-its-go-card` (code `4ef12e6`, ff from `2f25415`: the worker's `ec0e629`, my `128fe14` and `4ef12e6`; doc `01032278`, the worker's `f41e3f2d` cherry-picked onto `6bf2d218`).
**Reviewer:** 1 finding — fixed forward in core `4ef12e6` (unfiled: Linear refused at its issue cap, spool entry dropped once fixed).
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has neither route until redeployed; nothing calls them until EMB-376.
*Also cited:* `0caf76b`.

### 08:04 — study-designer/098 one-function-turns-a-tests-records-into-its-verdict
; I read the shared-crate diff before landing it (one `pub mod hil_judge` line in `lib.rs` behind `hil-test`, the rest new files
**Merged:** `agent/study-designer/098-one-function-turns-a-tests-records-into-its-verdict` (code `0caf76b`, ff from `2366f86`; doc `6bf2d218`, the worker's `efe831c9` cherry-picked onto `1c276399`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795617464`, `49acf3ad`.

### 07:30 — suite/063 an-instruments-declaration-carries-its-metrology
A suite pass, run by me as this leg's last unit, announced by the previous leg (ts `1795612302.163159`, 06:11
**Merged:** `agent/suite/063-an-instruments-declaration-carries-its-metrology`, landed in order, each ff from its `origin/main`: topology `5b8d493` (from `7b0b87d`), core `2f25415` (from `2e8a18b`), api `add96ab` (from `5e18cc3`), ui `90668da` (from `7d52207`); doc `9aad9194`, my own commit in the leg worktree.
**Reviewer:** no findings.
**Hardware debts:** none from the code; the native Windows build of Core. **Deploy debt:** the installed service Core accepts the new fields only once redeployed; nothing sends them yet.

### 07:11 — umbrella/113 the-agent-containers-firewall-and-cores-address-from-inside
`src/agent.rs` gains, pure: `render_entrypoint_root(&plan, core_host)`, a POSIX root script that drops IPv4 and IPv6 egress, allows loopback, established flows, DNS to the IPv4 resolvers in `/etc/resolv.conf`, TCP to Core's …
**Merged:** `agent/umbrella/113-the-agent-containers-firewall-and-cores-address-from-inside` (code `d9a4b8a`, ff from `aecbcf8`; doc `f6c24010`, the worker's `1447d4ae` cherry-picked onto `7bb1421c`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; every rule is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.

### 07:09 — core/157 core-keeps-definitions-premade-suites-and-confirmations
Core keeps HIL definitions and records confirmations: `POST /definitions` checks a test, suite or plan with the crate's `check` functions (and `hil_check::check_test` when the request carries a study and a bench), keeps it as …
**Merged:** `agent/core/157-core-keeps-definitions-premade-suites-and-confirmations` (code `2e8a18b`, ff from `22646fc`; doc `3f9ffd2f` and `40517a43`, the worker's `8baf99f5` and `2a6e2bfb` cherry-picked onto `d21d666e`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core has none of these routes until it is redeployed with this commit; nothing consumes a confirmation until EMB-364.
*Also cited:* `2366f86`.

### 07:07 — study-designer/096 expand-a-test-selection-into-the-resolved-run-file
; I read the shared-crate diff before landing it. Leg start, to carry
**Merged:** `agent/study-designer/096-expand-a-test-selection-into-the-resolved-run-file` (code `2366f86`, ff from `8ecf13e`; doc `4641e35a`, ff from `e5dce1e8`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795612302`, `1795614703`, `2cfd93a4`.

### 06:43 — umbrella/112 a-pure-renderer-for-the-agents-container
New `src/agent.rs`, pure, no I/O, nothing calling it yet (`#![allow(dead_code)]` until EMB-445 to EMB-448)
**Merged:** `agent/umbrella/112-a-pure-renderer-for-the-agents-container` (code `aecbcf8`, ff from `4715a1a`; doc `5e323a7d`, the worker's `c4f6790b` cherry-picked onto `eee38f71`).
**Reviewer:** no findings.
**Hardware debts:** none from a board; every flag and mount is unverified until a container starts (EMB-448), and the owner verifies `linux` and `wsl-host`.
*Also cited:* `1795612302`.

### 06:41 — core/156 a-service-core-refuses-identity-routes-to-the-agents-token
A `--service` Core answers `403` to the agent's token on the eleven identity routes (probe enrol, unenrol, set board, unenrol by serial, dev-bench link, signal declare and remove, instrument declare and remove, bootload ports set …
**Merged:** `agent/core/156-a-service-core-refuses-identity-routes-to-the-agents-token` (code `22646fc`, ff from `0108da1`; doc `a75984d9` and `eee38f71`, the worker's `358a23ab` and its anchor fix `3866852f` cherry-picked onto `c91f40c1`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build of Core (a worktree cannot build it). **Deploy debt:** the installed service Core refuses nothing new until it is redeployed with this commit.

### 06:39 — api/195 the-client-sends-cores-token-only-after-a-challenge
; I read the shared-crate diff (`embarch-core-client` gains a public `attest` module, `CoreClient::attestation()`, `CoreClient::new_with_stores(...)` and `CoreConfig::token_is_explicit(scope)`
**Merged:** `agent/api/195-the-client-sends-cores-token-only-after-a-challenge` (code `5e18cc3`, ff from `9f698e3`; doc `c91f40c1`, the worker's `152e1588` cherry-picked onto `cac9ad95`).
**Reviewer:** no findings.
**Hardware debts:** a live-Core check: install a `core-fingerprint` beside the token file and confirm a matching service Core gets the machine-wide token and a development Core gets the development store's, through WSL2 on the bench machine. **Deploy debt:** the MCP server and `embarch-ui` pick this up only when rebuilt; until a `core-fingerprint` exists on the machine nothing changes.

### 06:37 — study-designer/095 a-hil-test-is-checked-when-it-is-defined
; I read the shared-crate diff before landing it (one `pub mod hil_check` line in `lib.rs` behind `hil-test`, the rest new files
**Merged:** `agent/study-designer/095-a-hil-test-is-checked-when-it-is-defined` (code `8ecf13e`, ff from `faddb4c`; doc `cac9ad95`, the worker's `0ed109fa` cherry-picked onto `7e1e1206`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795612297`, `1795612302`, `bf0f6723`.

### 04:08 — chat/040 the-linker-offers-datasheet-and-spec-sections
The 💡 linker has an atlas section source on decision 112's interface
**Merged:** `agent/chat/040-the-linker-offers-datasheet-and-spec-sections` (code `4093c1a`, ff; doc `3962c9e0`, the worker's `0645b448` cherry-picked onto `86b58e9a`).
**Reviewer:** no findings.
**Hardware debts:** none (tested against a fake `embarch-atlas` only, and not seen in a real VS Code window; the feature row says so; the `cards-refs` model call was not re-recorded for the new `section` kind).
*Also cited:* `20fa59c`.

### 03:56 — api/194 compact-api
Nothing. `embarch-api/open.md` went from 4,292 to 3,779 B, out of reserve, by two verbatim moves with their relative links fixed
**Merged:** `agent/api/194-compact-api` (doc `06ae6b10`, the worker's `f1751160` cherry-picked onto `aae8a2d9` with its subject corrected; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none new; the moved live-log line still needs a bench with a lease.

### 03:53 — study-designer/094 types-for-a-hil-test-a-suite-and-a-plan
; I read the shared-crate diff before landing it (one new feature line in `Cargo.toml`, one `pub mod` line in `lib.rs`, the rest new files).
**Merged:** `agent/study-designer/094-types-for-a-hil-test-a-suite-and-a-plan` (code `faddb4c`, ff from `3e4e301`; doc `e973a520`, the worker's `870441c5` cherry-picked onto `e22bc4ee`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 03:43 — core/155 a-host-step-parses-its-number-and-writes-measurements
Split three Fleet Ready issues at leg start (`d68e30ab`): EMB-359 as `tasks/core/155`, EMB-353 as `tasks/study-designer/094` (HIL test, suite and plan types, the root of the HIL Test chain), EMB-411 as `tasks/chat/040` (atlas …
**Merged:** `agent/core/155-a-host-step-parses-its-number-and-writes-measurements` (code `0108da1`, ff from `d645ecd`; doc `ed57d5bb`, the worker's `da086fb0` cherry-picked onto `dfa05876`).
**Reviewer:** no findings.
**Hardware debts:** a host study with a `parse` run on a bench against a DUT console, a bench board's signal and a real instrument, checking `by`, `instrument` and the signed subject list; the native Windows build. **Deploy debt** carried from `suite/062`: Core, `embarch-api` and `embarch-ui` deploy together for host v25.
*Also cited:* `1795602826`.

### 03:26 — suite/062 a-host-step-parses-a-number-and-a-prompt-has-a-kind
A suite pass, run by me as this leg's last unit, and a host-schema bump, both announced (ts `1795597152.735759`, 01:59
**Merged:** `agent/suite/062-a-host-step-parses-a-number-and-a-prompt-has-a-kind`, landed in order: study-designer `3e4e301` (from `31b4408`), core `d645ecd` (from `cf5b661`), ui `7d52207` (from `d66e313`) (each ff from its `origin/main`); doc `df83f1b2`, my own commit in the leg worktree.
**Reviewer:** no findings.
**Hardware debts:** none from the code; a **deploy debt**: the host gate is a strict match both ways, so Core, `embarch-api` (MCP server restarted) and `embarch-ui` deploy together and `embarch-umbrella` is rebuilt, or `embarch doctor` check 11 warns. The installed Core already reports host v21 (`fleet-hardware.py`, 02:43), so it was behind before this unit. The native Windows build of Core.

### 03:05 — api/193 a-confined-writer-for-the-persons-embarch-folder
New `src/person_writer.rs` (`pub mod person_writer`): `ConfinedWriter::open(repo_root)` refuses a linked or non-folder `<repo>/embarch`
**Merged:** `agent/api/193-a-confined-writer-for-the-persons-embarch-folder` (code `9f698e3`, ff from `cd1f428`; doc `0e34d264`, the worker's `3856e88b` cherry-picked onto `7a16781f`).
**Reviewer:** no findings.
**Hardware debts:** `cargo test person_writer` on Windows from the main checkout (the whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `aws-lc-sys`'s C build before it reaches the module); a Windows symlink and junction fixture is still unwritten, since those fixtures are `#[cfg(unix)]`; the native Windows build.

### 03:04 — chat/039 the-linker-offers-branches-and-worktrees
The 💡 linker has its first new source on decision 112's interface
**Merged:** `agent/chat/039-the-linker-offers-branches-and-worktrees` (code `a70291c`, ff from `89b20a8`; doc `333e2799`, the worker's `52a0c771` cherry-picked onto `bb0b51d8`).
**Reviewer:** no findings.
**Hardware debts:** none (the feature has not been seen in a real VS Code window; the feature row says so).
*Also cited:* `1795600044`, `20fa59c`, `6d313db3`.

### 02:40 — core/154 core-holds-the-bench-ports-under-a-lease
I split EMB-326 mid-leg (`8cb884ea`; `filed` hit the rate limit at the status move and reached it on the retry, so the issue may carry its filed comment twice) and dispatched it beside `umbrella/110` as this leg's fourth unit, …
**Merged:** `agent/core/154-core-holds-the-bench-ports-under-a-lease` (code `cf5b661`, ff from `b539f6a`; doc `78090367`, the worker's `64c8cd99` cherry-picked onto `9d79ef78`).
**Reviewer:** no findings.
**Hardware debts:** on Windows COM ports, a second open of a held signal or instrument port must fail while Core's own exchange, instrument call and study tap still work (COM exclusivity assumed); on a real CDC ACM bench port, what a hold does across a DUT reset or re-enumeration (a held handle may go stale); that asserting DTR at hold time does not reset a board a plain open leaves alone; the native Windows build.
*Also cited:* `1795597152`.

### 02:40 — umbrella/110 install-core-verifies-a-signed-release-first
`embarch install-core <release dir or archive> [--allow-downgrade] [--dry-run] [--data-dir DIR] [--trusted-root FILE | --refresh-trust-root]` (new `src/install_core.rs`)
**Merged:** `agent/umbrella/110-install-core-verifies-a-signed-release-first` (code `4715a1a`, ff; doc `b3a8b0e8`, the worker's `62166429` cherry-picked onto `0d2c9c77`).
**Reviewer:** no findings.
**Hardware debts:** one elevated Windows run of `install-core` with a signed release and a tampered one, checking the staging folder's ACL lists only Administrators and SYSTEM (`open.md`'s line); the native Windows build.

### 02:28 — chat/038 the-linker-takes-references-of-any-kind
The 💡 linker takes references from any number of sources: `src/assistant/refsBase.ts` (entry and source types), `refsDesk.ts` (the desk's issues and PRs, the first source, line and text unchanged), `references.ts` …
**Merged:** `agent/chat/038-the-linker-takes-references-of-any-kind` (code `89b20a8`, ff from `695f46d`; doc `3dc7ccd8`, the worker's `6779dcf8` cherry-picked onto `99be4085`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795597152`, `20fa59c`.

### 02:26 — core/153 core-keeps-a-service-store-and-a-development-store
First normal-mode leg after the burndown ended, so new decisions are back in scope
**Merged:** `agent/core/153-core-keeps-a-service-store-and-a-development-store` (code `b539f6a`, ff from `9df9976`; doc `269dad6d`, the worker's `ca1b414f` cherry-picked onto `288f488a`).
**Reviewer:** no findings.
**Hardware debts:** the native Windows build (whole-crate `cargo check --target x86_64-pc-windows-msvc` fails in WSL at `hidapi`'s `build.rs`, as `gate.md` expects); the owner builds natively and runs `run --service` with no store (expect the refusal), then `run --store <dir>`. None of the new code is `cfg(windows)`-gated.
*Also cited:* `1795597146`, `1795597152`, `2b361b09`, `3dc22553`, `52de0e4d`, `a2da724a`.

### 01:51 — desk/045 the-reference-index-holds-linear-documents
And no new decision (burndown leg). The desk's reference index (`GET /refs`) now carries `documents
**Merged:** `agent/desk/045-the-reference-index-holds-linear-documents` (code `20fa59c`, ff from `2afbcbe`; doc `88c5ef48`, the worker's `15f5da00` cherry-picked onto `97b76588`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `009d3d63`, `1795596282`.

### 01:38 — suite/061 compact-studies-guide
Beyond the announced move, and no new decision (burndown leg).
**Merged:** no worker branch; my own commit, doc `3d291eed` on `47609410`, landed in this fold's push. Gate on the result:.
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795593942`.

### 01:35 — desk/044 the-reference-index-holds-linear-projects
And no new decision (burndown leg). The desk's reference index (`GET /refs`) now carries `projects
**Merged:** `agent/desk/044-the-reference-index-holds-linear-projects` (code `2afbcbe`, ff; doc `f2fde423`, the worker's `e888d977` cherry-picked onto `ae4f54a4`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:34 — api/192 a-list-studies-verb
And no new decision (burndown leg). `embarch-api [--json] list-studies [--limit N]` lists Core's retained studies newest first by `started_utc_ms` (no start time after, by id), each tap with Core's tagged `encoding` and a flat …
**Merged:** `agent/api/192-a-list-studies-verb` (code `cd1f428`, ff from `a3d0831`; doc `ae4f54a4`, the worker's `f9129c46` cherry-picked onto `28311ead`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:33 — atlas/109 a-refs-verb-lists-sections-symbols-and-nodes
And no new decision (burndown leg). `embarch-atlas refs [--json] [--atlas-dir D] [--atlas <id>]` (new `src/embarch_atlas/refs.py`, listed in `cli.py`) prints every translated document's sections, and the current atlas's Kconfig …
**Merged:** `agent/atlas/109-a-refs-verb-lists-sections-symbols-and-nodes` (code `b4c3c75`, ff from `d0b5ca5`; doc `28311ead`, the worker's `309356a3` cherry-picked onto `bf5d945c`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `08b3ca7a`, `1795594763`.

### 01:12 — promptu/025 compact-promptu
And no new decision (burndown leg). Unparked early for the verbatim move its task names, as the `promptu/024` entry suggested and `desk/038`'s entry explains.
**Merged:** `agent/promptu/025-compact-promptu` (doc `c18a2754`, the worker's `f54c6c73` cherry-picked onto `f2538f73`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:11 — umbrella/107 compact-umbrella
And no new decision (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says.
**Merged:** `agent/umbrella/107-compact-umbrella` (doc `f2538f73`, the worker's `a1c44420` cherry-picked onto `6a54b70b`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:11 — atlas/107 compact-atlas
And no new decision (burndown leg). Unparked early for a verbatim move, as `desk/038`'s entry says.
**Merged:** `agent/atlas/107-compact-atlas` (doc `6a54b70b`, the worker's `0fc7b04d` cherry-picked onto `99057054`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.

### 01:10 — desk/038 compact-desk
And no new decision (burndown leg). I unparked four size debts early, for the verbatim moves their own tasks name
**Merged:** `agent/desk/038-compact-desk` (doc `0ce75348` and `99057054`, the worker's `8bf257a8` and `7656f71a` cherry-picked onto `005334ad`; no code repo).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795593942`.

### 00:56 — atlas/108 the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture
And no new decision (burndown leg). `embarch-atlas/src/embarch_atlas/livelog.py` no longer keeps `UNGATED`
**Merged:** `agent/atlas/108-the-live-log-writer-drops-its-verb-list-and-meets-the-api-fixture` (code `d0b5ca5`, ff from `74048d8`; doc `347a28f4`, the worker's `31792f90` cherry-picked onto `0d7e8a3c`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `c254d15`.

### 00:54 — api/190 hil-guide-words-point-at-the-glossary
And no new decision (burndown leg). The HIL guide's Words entry for Study now reads "Study (the mode
**Merged:** `agent/api/190-hil-guide-words-point-at-the-glossary` (code `a3d0831`, ff from `c254d15`; doc `0d7e8a3c`, the worker's `b1e151df` cherry-picked onto `fcadb4c0`); the suite guide edit is in this fold commit.
**Reviewer:** no findings.
**Hardware debts:** none.

### 00:39 — promptu/024 the-contract-fixes-build-step-5s-shapes-and-forks
And no new decision (burndown leg; the issue itself says the forks hold the choices).
**Merged:** `agent/promptu/024-the-contract-fixes-build-step-5s-shapes-and-forks` (code `6d091a1`, ff from `dcb6588`, docs only; doc `076da6d2`, the worker's `15a24261` cherry-picked onto `0bf5cb47`).
**Reviewer:** no findings.
**Hardware debts:** none.

### 00:37 — api/191 a-shared-fixture-pins-the-live-log-rules
And no new decision (burndown leg). `embarch-api/tests/fixtures/live-log/` holds 19 plain-JSON cases pinning the five rules both live-log writers share (the 4096-byte answer cap with 2- and 4-byte characters at the cut, the board …
**Merged:** `agent/api/191-a-shared-fixture-pins-the-live-log-rules` (code `c254d15`, ff from `d755007`; doc `0bf5cb47`, the worker's `50b9ec81` cherry-picked onto `aed2c46d`).
**Reviewer:** no findings.
**Hardware debts:** none.
*Also cited:* `1795590679`, `39be7664`.
*Days 2026-11-24 to 2026-11-24 rolled to [log-archive/supervisor-log-2026-11-24-to-2026-11-24.md](log-archive/supervisor-log-2026-11-24-to-2026-11-24.md).*
