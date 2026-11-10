# The usage budget

**Split out of [ops.md](ops.md) §2 on 2026-09-07**, when adding the measured
wave below took that file past its ratchet. A split rather than a squeeze on
purpose: it restates nothing, so no argument here had to be shortened to make
room for a new one — [DOC-COMPACTION.md](../embarch-doc/DOC-COMPACTION.md) §2's
own preference. `ops.md` §2 is now a pointer, so every `§2` reference elsewhere
still resolves.

This is the answer to one question: **may the supervisor dispatch more workers
right now, and how many?** [`scripts/usage-budget.py`](scripts/usage-budget.py)
implements it and its docstring carries the mechanics; what is here is why the
numbers are what they are.

The fleet exists because the seat is under-used (§1), so "how much is left" is an input to a leg. **Both thresholds are 90% since 2026-09-07, at the owner's call: full speed below 80%, taper 80→90, hard stop at 90.** `suggest()` already had exactly that shape, so the policy is two numbers plus `taper` (0.111 × 90 = a 10-point band) rather than any code. They were weekly **70%** and 5-hour **85%** — and the evening they changed, `/usage` read weekly **76%**, so the old weekly would have HELD the fleet outright with a fifth of the week unspent, invisibly, because this gate has never once had a percentage to read.

**The two windows are still not the same kind of thing.** The weekly is the real budget. The 5-hour one is a lockout — burning it to 100% stops *the owner* working, not just the fleet — but it refills on a clock, so **a 5-hour window resetting within `five_hour_grace_min` (60) is ignored entirely**, for the verdict and for the wave. Holding on it with minutes left buys nothing and costs the fleet those minutes; the exposure is bounded by the same clock that justifies the grace, since ignoring it with N minutes to go risks at most an N-minute lockout. The weekly is never graced.

**The percentages come from asking the login, since 2026-11-04.** A Claude Code process in `stream-json` mode sends a `rate_limit_event` on its first turn, and its `unifiedWindows` holds both windows as the account sees them. So [`scripts/fleet-usage-cache.py`](scripts/fleet-usage-cache.py), on a `*/4` cron, runs one very small `claude -p` on the armed login, about 500 tokens, and writes `usage-cache.json` in **that login's config folder**. `*/4` and not `*/5` because the reader rejects a cache older than 300 s. It probes only while the pump is latched, because a 5-hour window opens with the first message after an idle gap and a probe would open one.

**Which login.** A leg reads the cache of its own `CLAUDE_CONFIG_DIR`, inherited from the listener, and a cron reads the login the listener recorded when it was armed. A status line, where one runs, writes the same file for its own login. The VS Code extension runs none. **The 429 check and the burn read that same login's `projects` folder, since 2026-11-09.** Until then they read `~/.claude/projects` whatever the login, so a 429 the personal login hit held a fleet running on the work login, whose own reading had headroom. Each login is its own account, so another login's 429 says nothing about this one. The HOLD line now names the login it came from.

**What it replaced.** From 2026-09-07 the percentages were derived: a `/usage` reading pinned the seat's allowance, and the transcripts' token sum was divided by it. Two logins ended that, because they share one `projects` folder, so the numerator summed both accounts. On the day it was retired the cache said 2.5% of the week where the login said 25%. **What this relies on:** `unifiedWindows` is a field Claude Code marks internal. If an update removes it, the script falls back to the one limit the event names, then writes nothing, and it never writes an empty `rate_limits`, which would pass the reader's validity check and yield "PROCEED with 0 workers".

So the gate degrades rather than blocking: `usage-budget.py` exits `0` PROCEED, `1` HOLD, `2` DEGRADED — treating DEGRADED as HOLD would mean the fleet never starts. `--strict` restores refuse-without-numbers.

**DEGRADED's wave is the constant `degraded_workers` again, since 2026-11-04.** From 2026-09 it was measured: `--burn` summed billable tokens over the trailing five hours against `[limits] five_hour_token_ceiling`, calibrated from one seat's `/usage` readings. That calibration belongs to one seat, and the sum mixed two logins until 2026-11-09, so the ceiling is 0, which restores the constant. The code stays for a machine with one login.

**What actually protects the seat is the hard signal, not the estimate.** A throttled request appears as `"error":"rate_limit"` with `apiErrorStatus: 429`, and `--check-429` turns any verdict into HOLD. It reads the timestamp as **UTC**, ignores a 429 whose own `quotaLimits.resetsAt` has already passed, and decides on **parsed fields** rather than a substring so a session that merely quotes the marker cannot stop the fleet — three defects fixed 2026-09-07, each costing idle fleet hours, written up in `tasks/doc/023`. Five real 429s so far, most recently 2026-09-07 03:29Z.

**The backstop needs no percentage at all.** If a worker dies with a real rate-limit error: stop dispatching, land what is done, write the log entries, exit. That is what keeps this safe when the numbers are wrong.


# Burndown

**The mode whose goal is to reach the ceiling.** The weekly window is
use-it-or-lose-it, so on the last evening of a week the policy above is exactly
backwards. [burndown.md](burndown.md) is that argument: four config numbers, one
deadlined latch, and the three refusals that keep it from becoming the fleet
with its safeties off.

---

# Still open

Moved here from [open.md](open.md) on 2026-09-07, verbatim apart from this heading: the question is about this doc's own mechanism, and `open.md` had 61 bytes of headroom while this file had 8 KB. A split, so nothing was restated.

## Why the quota percentages never arrive

**Mostly closed 2026-09-07, and the part that closed is the part that mattered.**
The wave is no longer calibrated against nothing: [budget.md](budget.md) derives
it from a measured five-hour token burn against a ceiling calibrated on observed
429 behaviour. The feeder half was already closed.

**What is still open** is only the diagnosis of why `rate_limits` reaches a status line and
no transcript. Nothing depends on it now, as the gate reads `rate_limit_event` instead.
