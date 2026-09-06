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

import os
import sys
import tomllib
from pathlib import Path

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
