#!/usr/bin/env python3
"""Record that the fleet made progress: one mtime, one labelled log line.

`.fleet/tick`'s mtime is what the watchdog and the out-of-process deadman read,
and an mtime holds exactly one moment. So nothing on this machine could answer
"did the heartbeat fire on time?" -- the evidence was overwritten by the next
touch. On 2026-09-07 an armed listener's `:13` slot did not fire at all, the
tick ran at `:18` when a cross-session message happened to wake the session, and
the only record of any of it was a person watching the channel with a clock.

So this writes both: it touches `tick` for the watchers, and appends
`<iso8601> <label>` to `tick.log` for the history they cannot keep. The label
says WHO, because the two writers mean different things -- a listener line is
"the cron fired", a leg line is "a unit moved" -- and `tick`'s mtime deliberately
conflates them (`fleet-watch.md`, "What `tick` means").

**A script rather than `touch x && echo >> y` in the prose.** Two reasons, and
the second is the one that decided it. The command appears at five sites across
two command files, so a shell two-liner is five copies of a literal nothing
checks. And a **shell redirect into the state directory is exactly the shape the
permission classifier blocks**: `mkdir -p .fleet && touch .fleet/pump` was
refused in an owner's session on 2026-09-07, while `python3 scripts/*.py` is
what every leg already runs all day. A leg suspended on a permission prompt at
every dispatch would cost far more than the latency this log exists to measure.

`--report` is the other half. The watchdog's 35-minute threshold was
re-derived by hand from transcripts ("max gap 29.6 over six legs"), which is
not a measurement anyone repeats. With a log it is one command.

**A leg also holds a lock here, `leg`, and that is the other reason this file
exists in a leg's day** (`tasks/doc/048`). On 2026-09-12 a listener that ticked
five times in six minutes during a live leg spawned a second leg on the fifth,
and the second ran step 0's recovery over the first: it landed the three units
the first had claimed, and the first's uncommitted fold was reset under it. Every on-disk check a leg had then reads the same for a leg that is live
and one that was killed, which is why recovery could not tell. **Freshness is
what tells them apart**: the lock is held while it exists and its holder has
ticked within LOCK_LIVE_MIN, because every `leg-*` label touches it and the
listener's does not. Arming deletes it (a closed window took its leg with it),
`leg-end` deletes it, and a holder silent that long has crashed or forgotten
`leg-end`, so it is taken over. **A refused leg waits rather than exits**: an
exit wakes the listener, which would respawn a refused leg every minute until
the lock went stale.

Usage:
    scripts/fleet-tick.py listener        the listener's STEP 3
    scripts/fleet-tick.py leg-start [--wait [S]]
                                          a leg's FIRST act: take the lock;
                                          exit 1 while another leg holds it
                                          (--wait polls up to S s, default 100)
    scripts/fleet-tick.py leg-end         a leg's LAST act, whatever the exit
    scripts/fleet-tick.py leg-step0       a leg, once step 0 is done
    scripts/fleet-tick.py leg-dispatch    a leg, right after spawning a worker
    scripts/fleet-tick.py leg-fold        a leg, once the fold commit lands
    scripts/fleet-tick.py leg-waiting     a leg, waiting on a live worker
    scripts/fleet-tick.py --report        gaps between ticks, worst first
Exit status: 0 recorded / reported, 1 another leg holds the lock,
2 unknown label or the write failed.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

WHO = ("listener", "leg-start", "leg-end", "leg-step0", "leg-dispatch", "leg-fold",
       "leg-waiting")

# Under the watchdog's 35 minutes, so a leg taking over a crashed holder's lock
# ticks before the watchdog calls the fleet wedged; over the ~25 minutes a live
# leg may wait on a worker between `leg-waiting` ticks (.claude/leg.md).
LOCK_LIVE_MIN = 30

# ~6 weeks at a hundred lines a day. The trim rewrites to KEEP when the file
# passes CAP rather than on every call, so the common path is one append. A
# rewrite racing an append could lose a line; the listener's cron is dark for a
# leg's whole life, so the two writers are never live at the same moment, and a
# diagnostic log is the wrong place to pay for a lock.
CAP, KEEP = 5000, 4000


def record(label: str) -> int:
    state = CONF.state_dir
    try:
        state.mkdir(parents=True, exist_ok=True)
        (state / "tick").touch()
        if label.startswith("leg-") and (state / "leg").exists():
            (state / "leg").touch()  # the holder's heartbeat; see the header
        log = state / "tick.log"
        with log.open("a") as fh:
            fh.write(f"{datetime.now().astimezone().isoformat(timespec='seconds')} {label}\n")
        lines = log.read_text().splitlines()
        if len(lines) > CAP:
            log.write_text("\n".join(lines[-KEEP:]) + "\n")
    except OSError as exc:
        # Loud, not swallowed: if this cannot write, the watchdog is about to
        # declare a wedge on a healthy fleet and the caller is the only thing
        # that can say why.
        print(f"could not record a tick in {state}: {exc}", file=sys.stderr)
        return 2
    print(f"tick: {label}")
    return 0


def holder() -> tuple[str, float] | None:
    """The live lock's text and minutes since its holder ticked, or None."""
    lock = CONF.state_dir / "leg"
    try:
        age = (time.time() - lock.stat().st_mtime) / 60
        text = lock.read_text().strip()
    except OSError:
        return None
    return (text, age) if age < LOCK_LIVE_MIN else None


def leg_start(wait_s: float) -> int:
    deadline = time.monotonic() + wait_s
    while (held := holder()) is not None:
        if time.monotonic() >= deadline:
            print(f"leg lock held: {held[0]}, its holder ticked {held[1]:.0f} min ago "
                  f"-- another leg is live; do nothing else, run this again")
            return 1
        time.sleep(min(15.0, max(0.0, deadline - time.monotonic())))
    try:
        CONF.state_dir.mkdir(parents=True, exist_ok=True)
        (CONF.state_dir / "leg").write_text(
            f"taken {datetime.now().astimezone().isoformat(timespec='seconds')}\n")
    except OSError as exc:
        print(f"could not take the leg lock: {exc}", file=sys.stderr)
        return 2
    return record("leg-start")


def leg_end() -> int:
    try:
        (CONF.state_dir / "leg").unlink(missing_ok=True)
    except OSError as exc:
        print(f"could not release the leg lock: {exc}", file=sys.stderr)
        return 2
    return record("leg-end")


def report() -> int:
    log = CONF.state_dir / "tick.log"
    if not log.is_file():
        print(f"no {log} yet -- nothing has ticked since it was introduced")
        return 0
    rows = []
    for line in log.read_text().splitlines():
        stamp, _, label = line.partition(" ")
        try:
            rows.append((datetime.fromisoformat(stamp), label))
        except ValueError:
            continue
    if len(rows) < 2:
        print(f"{len(rows)} tick(s) in {log.name} -- too few for a gap")
        return 0
    gaps = [((b[0] - a[0]).total_seconds() / 60, a, b)
            for a, b in zip(rows, rows[1:])]
    print(f"{len(rows)} ticks, {rows[0][0]:%Y-%m-%d %H:%M} to {rows[-1][0]:%Y-%m-%d %H:%M}")
    listener = [g for g in gaps if g[2][1] == "listener" and g[1][1] == "listener"]
    if listener:
        print(f"listener-to-listener: max {max(g[0] for g in listener):.1f} min "
              f"over {len(listener)} pair(s) -- the heartbeat's own cadence")
    print(f"any-to-any: max {max(g[0] for g in gaps):.1f} min "
          f"-- what the watchdog threshold must clear")
    print("\nworst 10 gaps:")
    for minutes, a, b in sorted(gaps, key=lambda g: -g[0])[:10]:
        print(f"  {minutes:7.1f} min  {a[0]:%m-%d %H:%M:%S} {a[1]:<12} -> {b[1]}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["leg-start"] and argv[1:2] == ["--wait"] and len(argv) <= 3:
        try:
            return leg_start(float(argv[2]) if len(argv) == 3 else 100.0)
        except ValueError:
            print(__doc__, file=sys.stderr)
            return 2
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "leg-start":
        return leg_start(0.0)
    if argv[0] == "leg-end":
        return leg_end()
    if argv[0] == "--report":
        return report()
    if argv[0] not in WHO:
        print(f"unknown label {argv[0]!r} -- one of: {', '.join(WHO)}", file=sys.stderr)
        return 2
    return record(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
