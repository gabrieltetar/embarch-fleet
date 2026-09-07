#!/usr/bin/env python3
"""Notice, from outside Claude, that the fleet can no longer run.

Why this exists: every other liveness check in this repo is itself a Claude
session. `/fleet-watch` reads `.fleet/tick` and alerts when it goes stale --
but it runs on the same OAuth credential as the thing it watches, so **the one
failure it cannot see is the one that logs the machine out.** On 2026-09-07
that happened: all three windows died mid-leg at 02:06, the watchdog died with
them, and the fleet sat down for seven hours until the owner opened a laptop.
Two units were in flight; one had landed in `embarch-api` and not in
`embarch-doc`, which is the expensive shape.

So this file is deliberately not a Claude anything. It is a cron job. It reads
mtimes and one JSON file, and it reaches Slack through `fleet-post.py`'s bot
token -- a separate credential an expired Claude session does not touch.

**It never reads a token.** From the credentials file it takes exactly two
integers, `expiresAt` and `refreshTokenExpiresAt`, and ignores every other
field. Nothing it prints or posts can contain a secret.

What it watches, and why each is separate:

  logged_out       the credentials file is gone, empty or unparseable. Claude
                   Code clears it when the OAuth service rejects a refresh, so
                   this is the logout itself, caught within one tick.
  refresh_failing  the access token is past its expiry and nothing rewrote the
                   file. The refresh is not happening: the session is dead and
                   the processes have not found out yet.
  silent           `.fleet/tick` is stale while the pump is latched **and a
                   claude process is still alive**. Alive-with-no-progress is
                   the auth-death shape; processes *gone* is the owner closing
                   VS Code, which is the kill switch and must stay silent
                   (`ops.md` section 3). That is the whole reason this check
                   looks at the process table at all.
  expiry_soon      the refresh token is near its own end. The only one of these
                   that can be seen coming, so it is the only one that gets a
                   nudge before rather than an alarm after.

**It can alert and do nothing else.** It cannot start a leg, write a repo file,
or delete the pump latch. `/fleet-watch` unlatches on a declared wedge; this
does not, because a cron job that can stop the fleet is a cron job that stops
the fleet at 3am for a reason nobody is awake to read.

It also keeps `credential-history.tsv`: one line per credential change **and
one per window opening or closing**, so the question "how often does this
machine actually get logged out, and after what" stops being answered from
memory. A refresh moves the access expiry; a login moves the refresh expiry
too; the window rows are there because the binary's own text names a process
that "exited mid-refresh" as a way to poison the stored token, and that failure
only surfaces at the *next* refresh, hours later. Without the window timeline
underneath, the kill and the logout cannot be told apart from coincidence.

Install (the owner's, once):
    scripts/fleet-deadman.py --install-cron

Usage:
    scripts/fleet-deadman.py              one pass; alerts if anything is wrong
    scripts/fleet-deadman.py --check      print the state table, send nothing
    scripts/fleet-deadman.py --dry-run    print what would be sent, send nothing
Exit status: 0 nothing to do or alert sent - 1 a send failed - 2 not configured.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF  # noqa: E402

import argparse  # noqa: E402
import datetime  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402

HERE = Path(__file__).resolve().parent
CREDENTIALS = Path.home() / ".claude" / ".credentials.json"
STATE = CONF.state_dir / "deadman-state.json"
PUMP = CONF.state_dir / "pump"
HISTORY = CONF.state_dir / "credential-history.tsv"
TICK = CONF.state_dir / "tick"

# 35 minutes matches `/fleet-watch`; ops.md section 3 re-derived it on
# 2026-09-06 from a max gap of 29.6 over six legs. One number, two watchers.
STALE_MIN = 35
# How far past `expiresAt` the file may sit before a missing refresh is real
# rather than a clock skew or a slow renewal.
REFRESH_GRACE_MIN = 15
# Lead times on the refresh token's own expiry: one to plan around, one last
# call. Each fires once per token, because the stamp is keyed by the expiry.
LEAD_HOURS = (48, 6)


def now() -> datetime.datetime:
    return datetime.datetime.now().astimezone()


def hhmm(t: datetime.datetime) -> str:
    return t.strftime("%H:%M")


def age_min(p: Path) -> float | None:
    try:
        return (time.time() - p.stat().st_mtime) / 60
    except OSError:
        return None


def expiries() -> tuple[int | None, int | None, float | None]:
    """The two expiry stamps, in ms, and the credential file's own mtime.

    Every other field -- both tokens above all -- is dropped on the floor here
    and never reaches a caller, a log line or a Slack post.
    """
    try:
        raw = json.loads(CREDENTIALS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None, None
    oauth = raw.get("claudeAiOauth")
    if not isinstance(oauth, dict):
        return None, None, None
    acc = oauth.get("expiresAt")
    ref = oauth.get("refreshTokenExpiresAt")
    mt = CREDENTIALS.stat().st_mtime
    return (acc if isinstance(acc, int) else None,
            ref if isinstance(ref, int) else None, mt)


def claude_alive() -> list[int]:
    """PIDs of live Claude Code processes.

    The distinction this buys is the whole design: a stale tick with these
    still running is an auth death, and a stale tick with none is the owner
    having closed VS Code on purpose.
    """
    pids = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            argv = (entry / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        for a in argv[:2]:
            name = os.path.basename(a.decode("utf-8", "replace"))
            if name == "claude":
                pids.append(int(entry.name))
                break
    return sorted(pids)


def claims_standing() -> list[str]:
    """Tasks a dead leg left `claimed`, named so the alert can count them."""
    out = []
    tasks = CONF.doc_repo / "tasks"
    for f in sorted(tasks.glob("*/*.md")):
        if f.name == "README.md":
            continue
        try:
            head = f.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            continue
        for line in head.splitlines():
            if line.lstrip("*").lower().startswith("state:") and "claimed" in line:
                out.append(f"{f.parent.name}/{f.name.split('-')[0]}")
                break
    return out


def record(acc_ms: int | None, ref_ms: int | None, mt: float | None,
           pids: int) -> None:
    """Append one line whenever the credential or the window count changes.

    Nobody can currently say how often this machine is actually logged out.
    Transcripts are kept 30 days and a `/login` is not a transcript message;
    the extension logs carry no auth lines; the credentials file keeps only its
    last write. So the cadence in `risks.md` is a guess drawn from the two
    failures that happened to land while a session was recording.

    This makes it measurable, and the events are distinguishable: **a refresh
    moves `expiresAt` alone, a login also pushes `refreshTokenExpiresAt` a
    month out.** The window rows are here because the client's own text names a
    process that "exited mid-refresh" as a way to poison the stored token, and
    that failure surfaces only at the *next* refresh, hours later — without a
    window timeline underneath, a kill and a logout cannot be told apart from
    coincidence.

    **Rows are compared field by field, never by a packed key.** The first
    version of this packed the two expiries into a trailing stamp, and the
    first edit to that stamp's shape made an unchanged credential read as a
    refresh — a fabricated event in the one file whose whole job is to say what
    really happened. Two integers, a count, no token.
    """
    def iso(ms: float | None) -> str:
        if not ms:
            return "-"
        return datetime.datetime.fromtimestamp(ms / 1000).astimezone().isoformat(
            timespec="seconds")

    vals = (iso(mt * 1000 if mt else None), iso(acc_ms), iso(ref_ms), str(pids))
    try:
        last = HISTORY.read_text(encoding="utf-8").rstrip("\n").rsplit("\n", 1)[-1]
    except OSError:
        last = ""
    cols = last.split("\t")
    prev = tuple(cols[2:6]) if len(cols) >= 6 else None
    if prev == vals:
        return

    if prev is None:
        kind = "first-seen"
    elif prev[1:3] == vals[1:3]:
        kind = ("window-opened" if int(vals[3]) > int(prev[3])
                else "window-closed" if int(vals[3]) < int(prev[3])
                else "rewritten")
    elif mt is None:
        kind = "cleared"
    elif prev[2] != vals[2]:
        kind = "login"
    else:
        kind = "refresh"

    with HISTORY.open("a", encoding="utf-8") as f:
        f.write("\t".join((now().isoformat(timespec="seconds"), kind, *vals)) + "\n")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(st: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(st, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(STATE)


def post(message: str, action: str, detail: str, dry: bool) -> int:
    """One alert, through the fleet's own voice.

    `fleet-post.py` owns the identity and the thread; `--action` is the only
    thing that notifies, and every condition here is by definition one the
    owner must act on.
    """
    cmd = [sys.executable, str(HERE / "fleet-post.py"), message,
           "--action", action, "--detail", detail]
    if dry:
        cmd.append("--dry-run")
    return subprocess.run(cmd).returncode


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="print what this pass sees and exit, sending nothing")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the alerts that would be sent, send nothing")
    ap.add_argument("--force", action="store_true",
                    help="ignore the once-per-episode stamps and re-send")
    ap.add_argument("--stale-after", type=int, default=STALE_MIN, metavar="MIN")
    ap.add_argument("--install-cron", action="store_true",
                    help="add the every-5-minutes crontab line and exit")
    args = ap.parse_args()

    if args.install_cron:
        return install_cron()

    latched = PUMP.exists()
    tick = age_min(TICK)
    acc_ms, ref_ms, cred_mt = expiries()
    pids = claude_alive()

    if not args.check and not args.dry_run:
        record(acc_ms, ref_ms, cred_mt, len(pids))

    conds: list[tuple[str, str, str, str, str]] = []  # key, id, msg, action, detail

    relogin = "run /login in a Claude Code window, then say fleet start"
    cred_state = "present" if cred_mt else "MISSING or unreadable"
    base = (f"pump latch: {'present' if latched else 'absent'}\n"
            f"tick: {'never' if tick is None else f'{tick:.0f} min old'}\n"
            f"claude processes: {len(pids)} {pids if pids else ''}\n"
            f"credentials file: {cred_state}")

    # 1. The logout itself. Claude Code clears the file when a refresh is
    #    rejected, so an absent file while the fleet is meant to be running is
    #    not a missing config -- it is the moment the session died.
    if latched and cred_mt is None:
        conds.append((
            "logged_out", "missing",
            "Claude Code is logged out on this machine, so the fleet has stopped.",
            relogin, base))

    # 2. The refresh that did not happen. Nothing rewrote the file after the
    #    access token's own expiry passed, which is what "could not be
    #    refreshed" looks like from outside the process.
    elif latched and pids and acc_ms and cred_mt:
        acc = datetime.datetime.fromtimestamp(acc_ms / 1000).astimezone()
        overdue = (now() - acc).total_seconds() / 60
        if overdue > REFRESH_GRACE_MIN and cred_mt < acc_ms / 1000:
            conds.append((
                "refresh_failing", str(acc_ms),
                "Claude Code's login expired and did not renew itself, so the "
                "fleet is about to stop.",
                relogin,
                base + f"\naccess token expired {hhmm(acc)}, "
                       f"{overdue:.0f} min ago, and nothing rewrote the file"))

    # 3. The deadman proper. Stale tick, latch on, windows still open.
    if latched and pids and tick is not None and tick >= args.stale_after:
        last = datetime.datetime.fromtimestamp(TICK.stat().st_mtime).astimezone()
        claims = claims_standing()
        held = (f"\nclaims standing: {len(claims)}"
                + (f" ({', '.join(claims)})" if claims else ""))
        conds.append((
            "silent", f"{TICK.stat().st_mtime:.0f}",
            f"The fleet has made no progress since {hhmm(last)} and its windows "
            f"are still open.",
            "look at the listener window; if it is logged out, run /login and "
            "say fleet start",
            base + held))

    # 4. The one that can be seen coming.
    if ref_ms:
        ref = datetime.datetime.fromtimestamp(ref_ms / 1000).astimezone()
        left_h = (ref - now()).total_seconds() / 3600
        for lead in LEAD_HOURS:
            if 0 < left_h <= lead:
                conds.append((
                    "expiry_soon", f"{ref_ms}:{lead}",
                    f"Claude Code's login expires in {left_h:.0f} hours, on "
                    f"{ref:%A %d %B at %H:%M}.",
                    "run /login before then, so the fleet does not stop while "
                    "you are not watching",
                    base + f"\nrefresh token expires {ref:%Y-%m-%d %H:%M %Z}"))
                break

    if args.check:
        print(f"latched={latched} tick={tick and round(tick)}min "
              f"claude_pids={pids}")
        if acc_ms:
            a = datetime.datetime.fromtimestamp(acc_ms / 1000).astimezone()
            print(f"access token expires {a:%Y-%m-%d %H:%M %Z}")
        if ref_ms:
            r = datetime.datetime.fromtimestamp(ref_ms / 1000).astimezone()
            print(f"refresh token expires {r:%Y-%m-%d %H:%M %Z} "
                  f"({(r - now()).days}d away)")
        print("would alert:", [c[0] for c in conds] or "nothing")
        return 0

    st = load_state()
    fired = {c[0] for c in conds}
    for gone in [k for k in st if k not in fired]:
        del st[gone]  # the episode ended; let the next one speak

    rc = 0
    for key, ident, msg, action, detail in conds:
        if not args.force and st.get(key, {}).get("id") == ident:
            continue
        r = post(msg, action, detail, args.dry_run)
        if r == 2:
            print("fleet-deadman: no Slack credential configured; "
                  "nothing was sent", file=sys.stderr)
            return 2
        if r not in (0, 3):
            rc = 1
            continue
        if not args.dry_run:
            st[key] = {"id": ident, "at": now().isoformat(timespec="seconds")}
    if not args.dry_run:
        save_state(st)
    return rc


def install_cron() -> int:
    """Add the crontab line, idempotently.

    Every five minutes: the checks are four stat calls and one small JSON
    parse, and five minutes is the difference between finding out at breakfast
    and finding out seven hours late.
    """
    line = (f"*/5 * * * * {sys.executable} {Path(__file__).resolve()} "
            f">> {CONF.state_dir / 'deadman.log'} 2>&1")
    cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = cur.stdout if cur.returncode == 0 else ""
    if str(Path(__file__).resolve()) in existing:
        print("fleet-deadman: already in the crontab")
        return 0
    block = existing.rstrip("\n")
    block += ("\n\n# The fleet's out-of-process deadman. Not a Claude session on\n"
              "# purpose: it has to survive the credential that everything else\n"
              "# shares. See embarch-fleet/scripts/fleet-deadman.py.\n" + line + "\n")
    p = subprocess.run(["crontab", "-"], input=block.lstrip("\n"), text=True)
    if p.returncode != 0:
        return 1
    print("fleet-deadman: installed\n  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
