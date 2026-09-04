#!/usr/bin/env python3
"""Claude Code status line that also caches the rate-limit numbers to disk.

Claude Code hands a status line command a JSON blob on stdin that includes
``rate_limits.five_hour`` / ``rate_limits.seven_day`` -- each with a
``used_percentage`` (0-100) and a ``resets_at`` (unix epoch seconds). That blob
is the only first-party source of "how much of my limit is left"; nothing on
disk can tell you, because quota state only ever arrives over the wire.

So this script does two jobs:

1. Prints a compact status line (what a status line is for).
2. Writes the rate-limit numbers to ``~/.claude/usage-cache.json`` so a process
   that is NOT the status line -- e.g. embarch-doc's supervisor, via
   ``scripts/usage-budget.py`` -- can read them.

``rate_limits`` is present only for Claude.ai Pro/Max subscribers and only
after the first API response of a session, and each window disappears once its
``resets_at`` passes. Every read here treats it as optional; the cache records
``cached_at`` so a reader can reject a stale one rather than trust it.

Pair this with ``statusLine.refreshInterval`` in settings.json. The event-driven
triggers go quiet while a session sits idle waiting on background subagents --
which is exactly what the supervisor does -- so without a timer the cache would
freeze at whatever it read before the wait started.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time

CACHE = os.path.expanduser("~/.claude/usage-cache.json")


def pct(node):
    """used_percentage out of a rate-limit window, or None if absent."""
    if not isinstance(node, dict):
        return None
    v = node.get("used_percentage")
    return v if isinstance(v, (int, float)) else None


def write_cache(data):
    """Atomically record the rate limits. Never raise -- a status line that
    crashes costs the user their status line, and this half is a side effect."""
    try:
        limits = data.get("rate_limits")
        if not isinstance(limits, dict):
            return
        payload = {
            "cached_at": int(time.time()),
            "session_id": data.get("session_id"),
            "rate_limits": limits,
        }
        d = os.path.dirname(CACHE)
        fd, tmp = tempfile.mkstemp(dir=d, prefix=".usage-cache.")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        os.replace(tmp, CACHE)
    except Exception:
        pass


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("")
        return 0

    write_cache(data)

    parts = []
    model = (data.get("model") or {}).get("display_name")
    if model:
        parts.append(model)

    ctx = pct(data.get("context_window"))
    if ctx is not None:
        parts.append(f"ctx {ctx:.0f}%")

    limits = data.get("rate_limits") or {}
    for label, key in (("5h", "five_hour"), ("7d", "seven_day")):
        v = pct(limits.get(key))
        if v is None:
            continue
        # 🟢 <50  🟡 50-80  🔴 >=80 -- the same bands the community scripts use.
        color = "32" if v < 50 else ("33" if v < 80 else "31")
        parts.append(f"\033[{color}m{label} {v:.0f}%\033[0m")

    cost = (data.get("cost") or {}).get("total_cost_usd")
    if isinstance(cost, (int, float)) and cost >= 0.01:
        parts.append(f"${cost:.2f}")

    branch = (data.get("workspace") or {}).get("git_worktree")
    if branch:
        parts.append(branch)

    print(" · ".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
