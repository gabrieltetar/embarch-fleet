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

The fleet exists because the seat is under-used (§1), so "how much is left" is an input to a leg. **Two thresholds, deliberately different:** weekly **70%**, the real budget; 5-hour **85%**, not a budget but a lockout — burning it to 100% stops *the owner* working, not just the fleet, and it refills in hours, so a leg that waits loses nothing.

**On this machine the percentages never arrive, and that is the normal case.** Quota state comes over the wire, so only a status line sees it. One *is* configured and correct — `statusLine` running the versioned `scripts/statusline-usage.py` at `refreshInterval: 60` — and given a payload carrying `rate_limits` it writes `~/.claude/usage-cache.json` correctly. **What is missing is `rate_limits` in the payload**; a 2026-09-07 search found that field recorded nowhere on disk. **"Never ran" and "ran with no numbers" are indistinguishable on disk**, since `write_cache` returns early without it, so narrowing further needs a payload capture. `refreshInterval` stays **required**: the event-driven triggers go quiet exactly while a session waits on background subagents, which is what a supervisor does.

So the gate degrades rather than blocking: `usage-budget.py` exits `0` PROCEED, `1` HOLD, `2` DEGRADED — treating DEGRADED as HOLD would mean the fleet never starts. `--strict` restores refuse-without-numbers.

**DEGRADED's wave is measured now, not a constant.** It was a flat 2 against a cap of 6 whatever the seat had left — too slow on an empty window, too fast on a spent one. Every request's own `message.usage` *is* on disk, so `--burn` sums billable tokens (input + output + cache writes; cache reads bill at ~10% and are excluded) over the trailing five hours, and the wave comes off that: full width below 25% of `[limits] five_hour_token_ceiling`, then linear to one worker at the ceiling. That ceiling is **calibrated, not derived** — 15.4M billable in a window that did not 429, 17.7M in the one that did — so it sits at 16M, the low side, because being wrong costs a lockout that stops the owner too. **It is a feedback loop with a five-hour memory:** each leg re-reads the burn its predecessor produced, so too wide a wave narrows within one leg — about forty minutes — with the 429 check underneath. A rolling five-hour sum is five times the hourly rate at steady state, so `ceiling / 5` is the sustainable rate, printed beside the observed one.

**What actually protects the seat is the hard signal, not the estimate.** A throttled request appears as `"error":"rate_limit"` with `apiErrorStatus: 429`, and `--check-429` turns any verdict into HOLD. It reads the timestamp as **UTC**, ignores a 429 whose own `quotaLimits.resetsAt` has already passed, and decides on **parsed fields** rather than a substring so a session that merely quotes the marker cannot stop the fleet — three defects fixed 2026-09-07, each costing idle fleet hours, written up in `tasks/doc/023`. Five real 429s so far, most recently 2026-09-07 03:29Z.

**The backstop needs no percentage at all.** If a worker dies with a real rate-limit error: stop dispatching, land what is done, write the log entries, exit. That is what keeps this safe when the numbers are wrong.

---

# Still open

Moved here from [open.md](open.md) on 2026-09-07, verbatim apart from this heading: the question is about this doc's own mechanism, and `open.md` had 61 bytes of headroom while this file had 8 KB. A split, so nothing was restated.

## Why the quota percentages never arrive

**Mostly closed 2026-09-07, and the part that closed is the part that mattered.**
The wave is no longer calibrated against nothing: [budget.md](budget.md) derives
it from a measured five-hour token burn against a ceiling calibrated on observed
429 behaviour. The feeder half was already closed.

**What is still open** is only the diagnosis: `rate_limits` reaches a status
line and nothing else, and a search of every transcript on disk finds it
recorded nowhere. Narrowing *why* needs a payload capture, not more code — it
arrives only for a Pro/Max seat, only after a session's first API response, and
each window disappears once its `resets_at` passes. The percentages would still
be better than the burn estimate; nothing depends on them any more.
