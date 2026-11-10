#!/usr/bin/env python3
"""Turn the pump on or off, and say whether it can be.

The latch has one job, and a window, a UI or a person in a shell all want to flip
it. Each would otherwise restate the same three rules, so they live here:

- **Start only with a listener to read the latch.** A latch nothing reads is a
  fleet that looks started and is not. A stamp records what a window was armed
  with, not that the window is still open, so the test is recent evidence: armed
  or ticked inside `OPEN_WINDOW_MIN`, or a leg holding a live lock, because a
  listener's cron is dark for a leg's whole life (slack.md section 2).
- **Stop finishes the unit.** It deletes the latch, which ends the relay, and if a
  leg is running it leaves a `stop` marker that the leg reads at its next unit
  boundary (`.claude/leg.md`). With no leg running nothing would read a marker, and
  a marker left behind would stop the next leg, so none is written.
- **Start undoes a stop that has not landed**, by removing the marker. A leg that
  has not read it yet simply carries on, which is what pressing Start asked for.

Usage:
  scripts/fleet-pump.py                        what is true now
  scripts/fleet-pump.py --json                 the same, for a program
  scripts/fleet-pump.py --start [--scope a,b]  latch the pump
  scripts/fleet-pump.py --start --no-gate      latch it with the usage gate off
  scripts/fleet-pump.py --stop                 unlatch it, finishing the unit
Exit status: 0 done or printed, 1 refused.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import tempfile
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import (ARMED_PROMPTS, CONF, GATE_OFF_LINE, armed_login,  # noqa: E402
                       armed_stamp, login_name)

HERE = Path(__file__).resolve().parent
LISTENER = ARMED_PROMPTS[0]
# Two heartbeat slots and a margin, as a slot has been measured five minutes late.
OPEN_WINDOW_MIN = 25
SCHEDULE_RE = re.compile(r"`(\d+)-59/(\d+) \* \* \* \*`")
PUMP = CONF.state_dir / "pump"
STOP = CONF.state_dir / "stop"
CACHE_NAME = "usage-cache.json"


def leg_holder() -> tuple[str, float] | None:
    tick = SourceFileLoader("fleet_tick", str(HERE / "fleet-tick.py")).load_module()
    return tick.holder()


def mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def last_listener_tick() -> float | None:
    """When the listener last ticked, from the log an mtime cannot keep."""
    try:
        lines = (CONF.state_dir / "tick.log").read_text().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        at, _, who = line.partition(" ")
        if who.strip() == "listener":
            try:
                return datetime.datetime.fromisoformat(at).timestamp()
            except ValueError:
                return None
    return None


def next_heartbeat(now: float) -> float | None:
    """The next slot of the schedule `fleet.md` arms, or None if it cannot be read.

    Read from the file rather than restated. It is an estimate either way: the
    cron fires only while the listener is idle.
    """
    try:
        found = SCHEDULE_RE.search((CONF.doc_repo / LISTENER).read_text())
    except OSError:
        return None
    if not found:
        return None
    first, every = int(found.group(1)), int(found.group(2))
    start = datetime.datetime.fromtimestamp(now).replace(second=0, microsecond=0)
    for ahead in range(1, 61):
        slot = start + datetime.timedelta(minutes=ahead)
        if slot.minute >= first and (slot.minute - first) % every == 0:
            return slot.timestamp()
    return None


def usage_of(login: Path | None) -> dict | None:
    """The armed login's newest reading, as the cache holds it."""
    if login is None:
        return None
    try:
        data = json.loads((login / CACHE_NAME).read_text())
        limits = data["rate_limits"]
        read_at = int(data["cached_at"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return {"read_at_s": read_at, "windows": {
        key: limits[key] for key in ("five_hour", "seven_day") if isinstance(limits.get(key), dict)}}


def status(now: float | None = None) -> dict:
    now = time.time() if now is None else now
    stamped = mtime(armed_stamp(LISTENER))
    tick = last_listener_tick()
    leg = leg_holder()
    latch = CONF.pump()
    login = armed_login()
    seen = max((t for t in (stamped, tick) if t is not None), default=None)
    recent = seen is not None and now - seen < OPEN_WINDOW_MIN * 60
    looks_open = stamped is not None and (recent or leg is not None)
    if latch is not None:
        why_not = "the pump is already on"
    elif stamped is None:
        why_not = "no listener is armed: run /fleet start in a window"
    elif not looks_open:
        minutes = int((now - seen) / 60)
        why_not = (f"the listener was last heard from {minutes} min ago, so its window "
                   "looks closed: run /fleet start in a window")
    else:
        why_not = ""
    due = next_heartbeat(now)
    return {
        "now_s": int(now),
        "pump_on": latch is not None,
        "mode": (latch or {}).get("mode", ""),
        "gate_off": CONF.gate_off(),
        "stop_requested": STOP.exists(),
        "leg_live": leg is not None,
        "login": login_name(login) if login else "",
        "armed": stamped is not None,
        "armed_at_s": int(stamped) if stamped else None,
        "listener_tick_s": int(tick) if tick else None,
        "looks_open": looks_open,
        "can_start": not why_not,
        "why_not": why_not,
        "next_heartbeat_s": int(due) if due else None,
        "usage": usage_of(login),
    }


def write_atomically(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.")
    with os.fdopen(fd, "w") as fh:
        fh.write(text)
    os.replace(tmp, path)


def start(scope: str | None, no_gate: bool = False) -> tuple[bool, str]:
    now = status()
    if not now["can_start"]:
        return False, now["why_not"]
    lines = ["mode=normal", f"started_at={time.strftime('%Y-%m-%dT%H:%M:%S%z')}"]
    if scope:
        lines.append(f"scope={scope}")
    if no_gate:
        lines.append(GATE_OFF_LINE)
    STOP.unlink(missing_ok=True)
    write_atomically(PUMP, "\n".join(lines) + "\n")
    return True, ("pump on: the listener starts a leg on its next heartbeat"
                  + (", usage gate off until the latch goes" if no_gate else ""))


def stop() -> tuple[bool, str]:
    leg = leg_holder()
    PUMP.unlink(missing_ok=True)
    if leg is None:
        STOP.unlink(missing_ok=True)
        return True, "pump off: no leg is running"
    write_atomically(STOP, f"stop requested {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n")
    return True, "pump off: the running leg finishes its unit, then stops"


def human(s: dict) -> str:
    rows = [f"pump:     {'on' if s['pump_on'] else 'off'}" + (f" ({s['mode']})" if s["mode"] else "")
            + (", usage gate OFF" if s["gate_off"] else ""),
            f"leg:      {'running' if s['leg_live'] else 'none'}"
            + (", told to stop" if s["stop_requested"] else ""),
            f"login:    {s['login'] or 'none recorded'}",
            f"listener: {'looks open' if s['looks_open'] else 'not armed or looks closed'}"]
    if s["why_not"]:
        rows.append(f"start:    {s['why_not']}")
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--start", action="store_true", help="latch the pump")
    g.add_argument("--stop", action="store_true", help="unlatch it, finishing the unit")
    ap.add_argument("--scope", help="with --start, sub-projects recorded in the latch")
    ap.add_argument("--no-gate", action="store_true", dest="no_gate",
                    help="with --start, write gate=off: usage-budget.py answers "
                         "PROCEED until the latch is deleted")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()
    if a.scope and not a.start:
        ap.error("--scope goes with --start")
    if a.no_gate and not a.start:
        ap.error("--no-gate goes with --start")

    if not (a.start or a.stop):
        s = status()
        print(json.dumps(s) if a.as_json else human(s))
        return 0
    done, said = start(a.scope, a.no_gate) if a.start else stop()
    print(json.dumps({"done": done, "said": said}) if a.as_json else said)
    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
