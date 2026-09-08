#!/usr/bin/env python3
"""Load fleet.toml -- the one file that is instance rather than framework.

Every other script in this repo is portable: it names no path, no channel and
no person. They get those from here, so standing a fleet up on a second machine
is editing one file rather than grepping five.

Resolution order, first hit wins:
  1. $EMBARCH_FLEET_CONF, a path to the file itself
  2. fleet.toml beside this script's parent (the normal case: a checkout)
  3. $EMBARCH_FLEET_ROOT/embarch-fleet/fleet.toml

A missing config is fatal and says which paths were tried. Guessing a default
root would put a fleet's state directory somewhere the owner did not choose,
and the failure would be silent until something wrote there.

Usage:
  from fleetconf import CONF
  CONF.root                 # Path, absolute
  CONF.doc_repo             # Path, absolute
  CONF.state_dir            # Path, absolute -- holds the pump latch and webhook
  CONF.owner                # Slack user id
  CONF["limits"]["max_workers"]
"""
from __future__ import annotations

import datetime
import os
import sys
import time
import tomllib
from pathlib import Path


def parse_instant(raw: str) -> float | None:
    """An epoch from an ISO-8601 instant, or None. Naive input is LOCAL time.

    Local rather than UTC because the only human who types one of these reads
    his reset instant off `/usage`, which prints it in his own timezone. The
    opposite convention is what put a six-hour error into every 429 age this
    repo measured (`tasks/doc/023`), so the choice is stated rather than
    inherited: a `Z` or an offset is honoured when present, and its absence
    means the clock on the wall next to the person typing.
    """
    raw = (raw or "").strip().replace(" ", "T")
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt.timestamp()

_HERE = Path(__file__).resolve().parent
_CANDIDATES = (
    os.environ.get("EMBARCH_FLEET_CONF"),
    _HERE.parent / "fleet.toml",
    (Path(os.environ["EMBARCH_FLEET_ROOT"]) / "embarch-fleet" / "fleet.toml"
     if os.environ.get("EMBARCH_FLEET_ROOT") else None),
)


class Conf:
    def __init__(self, path: Path, data: dict):
        self.path = path
        self._d = data

    def __getitem__(self, k):
        return self._d[k]

    def get(self, k, default=None):
        return self._d.get(k, default)

    @property
    def root(self) -> Path:
        return Path(self._d["fleet"]["root"])

    @property
    def doc_repo(self) -> Path:
        return self.root / self._d["fleet"]["doc_repo"]

    @property
    def state_dir(self) -> Path:
        return self.root / self._d["fleet"]["state_dir"]

    @property
    def worktree_root(self) -> Path:
        return self.root / self._d["fleet"]["worktree_root"]

    @property
    def client_denylist(self) -> Path:
        """Where check-client-names.py reads its names. Relative to state_dir --
        which is outside every repo, and is the whole point: the file names the
        clients, so committing it would be the leak the check exists to stop."""
        v = self._d["fleet"].get("client_denylist", "client-names")
        return Path(v) if Path(v).is_absolute() else self.state_dir / v

    @property
    def owner(self) -> str:
        return self._d["slack"]["owner"]

    @property
    def channel(self) -> str:
        return self._d["slack"]["channel"]

    @property
    def units_per_leg(self) -> int:
        return int(self._d["limits"]["units_per_leg"])

    @property
    def degraded_workers(self) -> int:
        """The wave size when the quota percentages are unavailable, which on
        this machine is the steady state (ops.md section 2). Read here rather
        than restated, so a caller that needs a default wave gets the same
        number usage-budget.py would have suggested."""
        return int(self._d["limits"]["degraded_workers"])

    def pump(self) -> dict[str, str] | None:
        """The pump latch, parsed. `None` when the fleet is stopped.

        The latch has always carried content -- `fleet start core,ui` records a
        scope filter in it -- but nothing parsed it: every reader asked
        `exists()` and a human read the rest. Burndown needs one machine-read
        field (`mode`), so this is the one parser, here rather than in the
        script that writes it, because `usage-budget.py` reads the latch it
        never writes.

        Format is `key=value`, one per line. **Anything else in the file is
        kept and ignored** -- the latch is also a note to whoever opens it, and
        a parser that rejected prose would turn a scope filter written by hand
        into a stopped fleet.
        """
        path = self.state_dir / "pump"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
        out: dict[str, str] = {}
        for line in text.splitlines():
            k, sep, v = line.partition("=")
            k = k.strip()
            if sep and k and all(c.isalnum() or c == "_" for c in k):
                out[k.lower()] = v.strip()
        return out

    def burndown(self) -> tuple[dict[str, str] | None, str | None]:
        """(latch, None) while a burndown is live, or (None, why-it-is-not).

        Live means all three: the pump is latched, its `mode` is `burndown`, and
        its `until` is a parseable instant still in the future. **An expired
        deadline is not an error and not a burndown** -- the mode is defined by
        the deadline it races, so passing that instant ends it whether or not
        anyone was watching. The caller reverts to the normal caps and says so.
        """
        latch = self.pump()
        if latch is None:
            return None, "the pump is not latched"
        if latch.get("mode") != "burndown":
            return None, "the pump latch is in normal mode"
        raw = latch.get("until", "")
        when = parse_instant(raw)
        if when is None:
            # Refuse rather than assume: a burndown whose deadline cannot be
            # read has no end, and an unreadable date must never widen a wave.
            return None, f"burndown latch has an unreadable `until` ({raw!r})"
        if when <= time.time():
            return None, (f"the burndown deadline ({raw}) has passed; "
                          "normal caps apply")
        return latch, None

    @property
    def reserved(self) -> tuple[str, ...]:
        return tuple(self._d["ownership"]["reserved"])

    @property
    def fleet_writable(self) -> tuple[str, ...]:
        return tuple(self._d["ownership"]["fleet_writable"])

    def substitutions(self) -> dict[str, str]:
        """The `{{name}}` placeholders install.py expands in a template.

        Kept here rather than in install.py so that adding a config value and
        making it available to the templates is one edit, not two that can
        disagree.
        """
        f, s, lim = self._d["fleet"], self._d["slack"], self._d["limits"]
        return {
            "FLEET_ROOT": str(self.root),
            "DOC_REPO": str(self.doc_repo),
            "DOC_REPO_NAME": f["doc_repo"],
            # This checkout, not a guess from the instance root. A second
            # instance need not put the framework beside its own root, and
            # when it did not, FLEET_REPO pointed at a directory that did
            # not exist while FLEET_REL -- computed from __file__ -- pointed
            # at the real one. Two placeholders for one thing, disagreeing.
            "FLEET_REPO": str(_HERE.parent),
            "STATE_DIR": str(self.state_dir),
            "WORKTREE_ROOT": str(self.worktree_root),
            "SLACK_CHANNEL": s["channel"],
            "SLACK_CHANNEL_NAME": s["channel_name"],
            "SLACK_OWNER": s["owner"],
            "SLACK_CLOUD_CHANNEL": s["cloud_channel"],
            "UNITS_PER_LEG": str(lim["units_per_leg"]),
            "MAX_WORKERS": str(lim["max_workers"]),
            "BURNDOWN_MAX_WORKERS": str(
                self._d.get("burndown", {}).get("max_workers",
                                                lim["max_workers"])),
        }


def _load() -> Conf:
    tried = []
    for c in _CANDIDATES:
        if c is None:
            continue
        p = Path(c)
        tried.append(str(p))
        if p.is_file():
            with p.open("rb") as fh:
                return Conf(p.resolve(), tomllib.load(fh))
    print("no fleet.toml found; tried:\n  " + "\n  ".join(tried) +
          "\n\nSet $EMBARCH_FLEET_CONF, or run from an embarch-fleet checkout.",
          file=sys.stderr)
    sys.exit(2)


CONF = _load()


if __name__ == "__main__":
    print(f"config: {CONF.path}")
    for k, v in CONF.substitutions().items():
        print(f"  {k:22} {v}")


# --- the armed cron prompts -------------------------------------------------
#
# A live cron job keeps the prompt it was armed with, so editing the file it
# came from changes nothing until the window is re-armed. Nothing recorded what
# any window was armed WITH, so `deploy.py` had to infer it from the repo -- and
# on 2026-09-07 that inference was wrong in the one direction that costs
# something: a hand-run `install.py` made the comparison read new-against-new,
# no re-arm was reported, and the listener spent twenty minutes spawning legs
# with a tick prompt that pointed them at the wrong file.
#
# So arming now leaves evidence. The stamp is the block itself rather than a
# hash of it: a human can read what the live job carries, and a stale one shows
# up as a diff instead of two unequal hex strings.

ARMED_PROMPTS = (".claude/commands/fleet.md", ".claude/commands/fleet-watch.md")


def cron_block(text: str) -> str:
    """The blockquote a window is armed with, as text, and nothing around it.

    One implementation, imported by `deploy.py` and `fleet-armed.py`. It was
    two for a day, which this repo's whole premise says is one too many.
    """
    return "\n".join(ln for ln in text.splitlines() if ln.startswith(">"))


def armed_stamp(rel: str) -> Path:
    """Where the block a window was armed with is recorded.

    Under the state directory, not either repo: it is machine state like the
    pump latch, it is per-window, and committing it would say a checkout was
    armed when only one machine's window ever was.
    """
    return CONF.state_dir / "armed" / (rel.replace("/", "%") + ".block")
