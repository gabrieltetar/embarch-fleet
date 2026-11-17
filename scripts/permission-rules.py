#!/usr/bin/env python3
"""Print the permission rules an agent started in an instance checkout runs under.

EMB-114: `.claude/leg.md` tells an unattended leg to "emit only shell a
permission rule can match", and nothing told it which rules exist. A leg read
the project's `settings.json` with inline Python, found no allow list there --
the instance's rules live in the user and local files -- and could not check a
command before running it. This merges every settings file that applies and
prints each rule with the file it came from.

Sources, highest precedence first, as Claude Code reads them:

  managed  /etc/claude-code/managed-settings.json
  local    <checkout>/.claude/settings.local.json   (untracked, the owner's)
  project  <checkout>/.claude/settings.json         (rendered by install.py)
  user     <login>/settings.json

`<checkout>` is fleet.toml's `doc_repo` unless `--checkout` says otherwise: a
leg or a worker is a subagent of the listener's session, which started there,
not in a leg worktree -- and a worktree has no `settings.local.json` at all.
`<login>` is the folder `fleetconf.login_dir()` names: `CLAUDE_CONFIG_DIR`, then
the login the listener was armed under, then `~/.claude`.

The mode is the highest-precedence `defaultMode`. A deny beats an ask beats an
allow, whatever file each is in. Command-line flags and an agent's frontmatter
are not files and are not shown.

Usage:
  scripts/permission-rules.py
  scripts/permission-rules.py --checkout <path> --login ~/.claude-work
  scripts/permission-rules.py --kind allow     one list only
  scripts/permission-rules.py --json
Exit status: 0 printed · 2 a settings file is not valid JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fleetconf import CONF, login_dir  # noqa: E402

MANAGED = Path("/etc/claude-code/managed-settings.json")
KINDS = ("deny", "ask", "allow")


def sources(checkout: Path, login: Path) -> list[tuple[str, Path]]:
    """(label, path) for every settings file, highest precedence first."""
    return [("managed", MANAGED),
            ("local", checkout / ".claude" / "settings.local.json"),
            ("project", checkout / ".claude" / "settings.json"),
            ("user", login / "settings.json")]


def read(srcs: list[tuple[str, Path]]) -> tuple[dict, list[str]]:
    """{label: permissions dict or None if absent}, and any unreadable files."""
    out, bad = {}, []
    for label, path in srcs:
        try:
            out[label] = json.loads(path.read_text()).get("permissions") or {}
        except FileNotFoundError:
            out[label] = None
        except (OSError, ValueError) as exc:
            bad.append(f"{path}: {exc}")
    return out, bad


def merged(srcs: list[tuple[str, Path]], perms: dict) -> dict:
    mode = next(((lbl, p["defaultMode"]) for lbl, _ in srcs
                 if (p := perms.get(lbl)) and p.get("defaultMode")), (None, "default"))
    rules = {k: [(r, lbl) for lbl, _ in srcs for r in (perms.get(lbl) or {}).get(k) or []]
             for k in KINDS}
    return {"mode": mode[1], "mode_from": mode[0], "rules": rules}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkout", type=Path, default=None,
                    help="the instance checkout (default: fleet.toml's doc_repo)")
    ap.add_argument("--login", type=Path, default=None,
                    help="the Claude config folder (default: fleetconf.login_dir())")
    ap.add_argument("--kind", choices=KINDS, help="print only this list")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    checkout = (args.checkout or CONF.doc_repo).expanduser().resolve()
    login = (args.login or login_dir()).expanduser()
    srcs = sources(checkout, login)
    perms, bad = read(srcs)
    if bad:
        print("not valid JSON, so the rules below would be incomplete:\n  "
              + "\n  ".join(bad), file=sys.stderr)
        return 2
    m = merged(srcs, perms)

    if args.json:
        print(json.dumps({"mode": m["mode"], "mode_from": m["mode_from"],
                          "sources": {lbl: (str(p) if perms[lbl] is not None else None)
                                      for lbl, p in srcs},
                          "rules": {k: [{"rule": r, "from": lbl} for r, lbl in v]
                                    for k, v in m["rules"].items()
                                    if not args.kind or k == args.kind}}, indent=2))
        return 0

    print("sources, highest precedence first:")
    for lbl, path in srcs:
        p = perms[lbl]
        what = ("absent" if p is None else
                ", ".join(f"{len(p.get(k) or [])} {k}" for k in KINDS)
                + (f", mode {p['defaultMode']}" if p.get("defaultMode") else ""))
        print(f"  {lbl:<8} {path}  ({what})")
    print(f"\nmode: {m['mode']}"
          + (f"  (from {m['mode_from']})" if m["mode_from"] else "  (no file sets one)"))
    for k in KINDS:
        if args.kind and k != args.kind:
            continue
        rows = m["rules"][k]
        print(f"\n{k} ({len(rows)}):")
        for rule, lbl in rows:
            print(f"  {lbl:<8} {rule}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
