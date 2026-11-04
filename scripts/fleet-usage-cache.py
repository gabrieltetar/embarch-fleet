#!/usr/bin/env python3
"""Ask a login what its quota is, and write the cache the budget gate reads.

**The source.** A Claude Code process in `stream-json` mode sends a
`rate_limit_event` on its first turn, and the event's `unifiedWindows` carries
both windows as the account sees them: `{utilization 0..1, resetsAt}` for
`five_hour` and `seven_day`. One very small `claude -p` is therefore a first-party
reading of exactly the login it ran under, with nothing pasted and nothing
estimated. Measured 2026-11-04: a Haiku probe took about 500 tokens, and two
logins answered with their own numbers.

**Why this replaced the derived percentages.** Those divided the transcripts'
token sum by an allowance pinned from a `/usage` reading. With two logins on one
machine that stopped being a measurement: the logins share one `projects` folder,
so the numerator summed both accounts, and the pin belonged to whichever account
last ran `/usage`. On the day it was retired the cache said 2.5% of the week while
the login the fleet would run on said 25%.

**What it costs.** About 500 tokens per probe, so this runs only while the pump is
latched, and only on the armed login. An idle account is never probed, because a
5-hour window opens with the first message after an idle gap and a probe would
open one.

**What it relies on.** `unifiedWindows` is a field Claude Code marks internal. If
an update removes it, this falls back to the one limit the event names, then to
writing nothing. **It never writes an empty `rate_limits`**, which would pass the
reader's validity check and produce "PROCEED with 0 workers". With no cache, or an
old one, `usage-budget.py` reports DEGRADED and runs its capped wave.

The cron stays at **`*/4`**, not `*/5`: the reader rejects a cache older than 300 s,
so a five-minute cadence is sometimes one second too late.

Usage:
    scripts/fleet-usage-cache.py                 while the pump is on, probe and write
    scripts/fleet-usage-cache.py --force         probe and write with the pump off
    scripts/fleet-usage-cache.py --login DIR     a named config folder, not the armed one
    scripts/fleet-usage-cache.py --check         probe and print, write nothing
    scripts/fleet-usage-cache.py --install-cron  add the */4 entry, once
Exit status: 0 written, printed or nothing to do; 1 the probe gave no reading.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF, login_dir  # noqa: E402

HERE = Path(__file__).resolve().parent
CACHE_NAME = "usage-cache.json"
CRON = (f"*/4 * * * * /usr/bin/python3 {HERE / 'fleet-usage-cache.py'} "
        f">> {CONF.state_dir / 'usage-cache.log'} 2>&1")
PROBE_PROMPT = "Reply OK"
PROBE_TIMEOUT_S = 60
PROBE_MAX_OUTPUT_TOKENS = 16
PROBE_ARGV = ["-p", "--model", "haiku", "--output-format", "stream-json", "--verbose",
              "--tools", "", "--strict-mcp-config", "--setting-sources", "",
              "--system-prompt", PROBE_PROMPT, "--max-thinking-tokens", "0",
              "--no-session-persistence"]
# What the cache calls a window, from what the event may call it. The second
# weekly name is what a seat with overage reports.
WINDOW_NAMES = {"five_hour": "five_hour", "seven_day": "seven_day",
                "seven_day_overage_included": "seven_day"}


def window(node: object) -> dict | None:
    """One window as the cache holds it, or None if it says no share."""
    if not isinstance(node, dict):
        return None
    used = node.get("utilization")
    if isinstance(used, bool) or not isinstance(used, (int, float)):
        return None
    out = {"used_percentage": round(100 * max(0.0, min(1.0, float(used))), 1)}
    if isinstance(node.get("resetsAt"), (int, float)):
        out["resets_at"] = int(node["resetsAt"])
    return out


def limits_of(info: object) -> dict[str, dict]:
    """The cache's `rate_limits` from a `rate_limit_info`.

    Without `unifiedWindows`, the one limit the event names still says its own
    share. A rejected limit that gives no share is at its ceiling: that is what
    rejected means, and leaving it out would read as "not constraining".
    """
    if not isinstance(info, dict):
        return {}
    out: dict[str, dict] = {}
    unified = info.get("unifiedWindows")
    if isinstance(unified, dict):
        for name, key in WINDOW_NAMES.items():
            one = window(unified.get(name))
            if one and key not in out:
                out[key] = one
    key = WINDOW_NAMES.get(info.get("rateLimitType"))
    if key and key not in out:
        one = window(info)
        if not one and info.get("status") == "rejected":
            one = window({"utilization": 1.0, "resetsAt": info.get("resetsAt")})
        if one:
            out[key] = one
    return out


def reading(printed: str) -> dict[str, dict]:
    """The newest usable reading in what a probe printed."""
    out: dict[str, dict] = {}
    for line in printed.splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("type") == "rate_limit_event":
            out = limits_of(rec.get("rate_limit_info")) or out
    return out


def claude_binary() -> str | None:
    """`claude`, from a cron's short PATH as well as a shell's."""
    path = os.environ.get("PATH", "") + os.pathsep + str(Path.home() / ".local" / "bin")
    return shutil.which("claude", path=path)


def probe(login: Path) -> tuple[dict[str, dict], str]:
    """(the login's windows, why there are none)."""
    binary = claude_binary()
    if not binary:
        return {}, "no claude on PATH or in ~/.local/bin"
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(login), EMBARCH_DESK_INTERNAL="1",
               CLAUDE_CODE_MAX_OUTPUT_TOKENS=str(PROBE_MAX_OUTPUT_TOKENS))
    try:
        run = subprocess.run([binary, *PROBE_ARGV], input=PROBE_PROMPT, env=env,
                             cwd=tempfile.gettempdir(), capture_output=True, text=True,
                             timeout=PROBE_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {}, f"could not run the probe: {e}"
    limits = reading(run.stdout)
    if limits:
        return limits, ""
    tail = (run.stderr or run.stdout).strip().splitlines()[-1:] or ["no output"]
    return {}, f"no rate_limit_event with a window (exit {run.returncode}): {tail[0][:200]}"


def write(cache: Path, limits: dict[str, dict], now: float) -> None:
    payload = {"cached_at": int(now), "session_id": "probe:fleet-usage-cache.py",
               "rate_limits": limits}
    cache.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(cache.parent), prefix=".usage-cache.")
    with os.fdopen(fd, "w") as fh:
        json.dump(payload, fh)
    os.replace(tmp, cache)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="print, write nothing")
    ap.add_argument("--force", action="store_true", help="probe with the pump off")
    ap.add_argument("--login", type=Path, help="a config folder, not the armed login")
    ap.add_argument("--install-cron", action="store_true", help="add the */4 entry")
    args = ap.parse_args()

    if args.install_cron:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        if "fleet-usage-cache.py" in cur:
            print("already installed")
            return 0
        subprocess.run(["crontab", "-"], input=cur.rstrip("\n") + "\n" + CRON + "\n",
                       text=True, check=True)
        print(f"installed:\n  {CRON}")
        return 0

    if CONF.pump() is None and not (args.force or args.check):
        return 0

    login = args.login.expanduser() if args.login else login_dir()
    limits, why = probe(login)
    if not limits:
        print(f"{login.name}: {why}: writing no cache. An empty rate_limits would read "
              "as valid\nand produce 'PROCEED with 0 workers'.", file=sys.stderr)
        return 1
    now = time.time()
    if args.check:
        print(json.dumps({"login": str(login), "rate_limits": limits}, indent=2))
        return 0
    write(login / CACHE_NAME, limits, now)
    shares = ", ".join(f"{k} {v['used_percentage']:g}%" for k, v in sorted(limits.items()))
    print(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} {login.name}: {shares}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
