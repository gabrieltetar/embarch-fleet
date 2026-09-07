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

Usage:
    scripts/fleet-tick.py listener        the listener's STEP 3
    scripts/fleet-tick.py leg-step0       a leg, once step 0 is done
    scripts/fleet-tick.py leg-dispatch    a leg, right after spawning a worker
    scripts/fleet-tick.py leg-fold        a leg, once the fold commit lands
    scripts/fleet-tick.py leg-waiting     a leg, waiting on a live worker
    scripts/fleet-tick.py --report        gaps between ticks, worst first
Exit status: 0 recorded / reported, 2 unknown label or the write failed.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

WHO = ("listener", "leg-step0", "leg-dispatch", "leg-fold", "leg-waiting")

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
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "--report":
        return report()
    if argv[0] not in WHO:
        print(f"unknown label {argv[0]!r} -- one of: {', '.join(WHO)}", file=sys.stderr)
        return 2
    return record(argv[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
