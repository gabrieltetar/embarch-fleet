#!/usr/bin/env python3
"""Refuse a commit that carries a client's name into any EmbArch repo.

On 2026-09-04 the owner settled a question `open.md` had asked as "is the
framework's prose portable": EmbArch references are correct, because the fleet
*is* part of EmbArch -- but **a client's name must never appear in any of these
repos**, and one did. The scrub was an exported type, a config value, board
identifiers, 43 files of prose and 1,540 committed build artifacts leaking a
client workspace path, across all ten repos, plus a history rewrite. It was
found by a grep somebody thought to run. This is that grep, run every time.

**The denylist lives outside every repo**, in the fleet's state directory
beside the alert webhook, and its location is named in `fleet.toml` rather than
here. That is not tidiness: a committed list of the names you are hiding is the
leak it exists to prevent. Nothing in any repo, this file included, ever holds
one.

**A hit never prints the name.** A red gate is read in a terminal, quoted into
a supervisor's log entry and sometimes into a commit message, so a check that
echoed the match would carry the name into the very places it is guarding. Each
hit names the file, the line, and the denylist's own line number; the excerpt
has the match replaced. Whoever is fixing it can open the denylist -- and
whoever is reading the log later cannot.

**It also reads what a file *encodes*, not only what it spells** (2026-09-06).
`embarch-dev-bench`'s ztest suite carries a captured Core frame as a `0x..`
array, and the 2026-09-04 scrub rewrote the string literal the test compares
against while leaving the bytes it decodes untouched. So a denylisted name sat
committed in that file for two days with this check reporting the repo clean --
the name never appears as text. Every tracked file's `0xHH`, `\\xHH` and bare
`HH` runs, and its base64-looking runs, are therefore decoded and scanned as
well, with each hit mapped back to the source line that holds the literal. False
positives are structurally near-impossible: a run is only ever *reported* when a
denylist entry matches what it decodes to, so the decoders can afford to be
generous.

**Two gaps, stated rather than papered over.**

- **It is dark in CI.** GitHub Actions checks out one repo and has no state
  directory, so there is no denylist there and this check skips. It guards what
  the fleet lands locally, which is every unit the fleet has ever landed; it
  does not guard a push made by hand from a machine with no `.fleet/`. Closing
  that means a repository secret and an Actions job, which is a separate
  decision about whether these repos ever go public.
- **A denylist of names cannot catch a name nobody thought to add.** This makes
  the *second* leak of a known name impossible. The *first* leak of a new one
  still needs somebody to think of the grep, exactly as in September 2026. Add
  a name here on the day a client engagement starts, not on the day it leaks.

**Absent or empty denylist fails; absent fleet skips.** `fleet-alert.py`'s precedent --
"a muted alarm that looks fine is worse than no alarm" -- says exit 2 and say
so. But applying that everywhere would make `docs-ci.yml` permanently red, and
`install.py`'s own header names the failure that follows: a gate with a standing
exception teaches an agent to triage reds, which is the judgement a gate exists
to remove. So the two cases are told apart by whether a fleet is configured at
all: **a state directory holding no usable denylist is a configured fleet
running a dark check, which is a defect and exits 2**; no state directory is not
this machine and skips. On the machine the fleet runs on the outcome is
therefore always PASS or RED, never a SKIP line somebody scrolls past.

**An empty denylist fails alongside a missing one**, and that is not pedantry:
`check-docs.py` discards a passing check's stdout, so a warning printed beside
an exit 0 would be invisible in the one place anybody reads it, and the gate
would report nine green while the ninth did nothing. A fleet with genuinely no
names to hide should remove this check from its gate rather than leave it dark.

**What it scans**, per repo, from `git ls-files` so that ignore files and
worktrees are honoured (a naive repo-wide walk finds `.claude/worktrees/`
copies and over-extracts -- `embarch-study-designer` decision 57):

- every tracked file's **contents**, as bytes, so a compiled artifact is
  searched the same way as prose -- the 1,540 artifacts were the largest part
  of the 2026-09-04 leak and no text-only scan would have seen them;
- every tracked file's **path**, since a directory named for a client leaks
  without any file containing the name;
- every **commit message** on this branch since its merge-base with `main`.
  This is the one leak a later fix cannot make cheaply: a name in file content
  is one commit to remove, a name in a landed commit message needs the history
  rewrite that September's scrub had to do across ten repos.

**On `main` that last range is empty, and the suite commits straight to
`main`** (`embarch-dev-workflow.md` §6). So until 2026-10-29 no gate and no hook
ever read a message on `main`, and the tree scan never read a file a later commit
had removed: five messages reached public `main` that way, and on 2026-10-20 five
histories were rewritten and force-pushed for it (`tasks/suite/050`). Two modes
close it, both reading commits rather than the tree:

- **`--pre-push REMOTE`**, what the pre-push hook runs: git's stdin names each
  ref being pushed, and every commit the remote lacks is read -- its message,
  every path it touched, and every blob the remote does not have yet, through the
  same decoders as the tree. Detail and the one deliberate limit:
  `pre_push_revs()`.
- **`--history`**, every reachable commit the same way, and **`--suite
  --history`** for every repo under the fleet root at once -- ~25 s for the
  whole suite on 2026-10-29, run daily by the first leg after midnight. It finds
  what the hook cannot: a name added to the denylist after the push that carried
  it, and a push made from anywhere the hook is not installed. Its first run
  found one the 2026-10-20 rewrite's text search could not see -- the
  2026-09-06 hex-encoded leak below is still in `embarch-dev-bench`'s public
  history.

The whole suite is 583 tracked files and 5.9 MB, so a full scan of all ten
repos is milliseconds and there is no reason to sample.

**Why per repo and not one pass over the siblings.** `DOC-PROTOCOL.md` §2
guarantees every repo is a sibling of `embarch-doc`, so one invocation could
walk them all -- and would be wrong from exactly the trees the fleet runs in. A
worker and a leg both work in `embarch/.worktrees/<repo>/<slug>/`, where sibling
resolution finds other worktrees rather than the repos, so the scan would silently
cover `main` instead of the branch under gate. That is the class of defect
`open.md`'s second-instance test found three of: a value derived from the wrong
source. So the repo is an argument, and the caller says which. **`--suite` is
the one exception, and it is history-only:** it walks the main checkouts under
the configured root by absolute path, never siblings of the cwd, and a worktree
shares its main checkout's refs, so for history the two are the same answer.

Denylist format: one name per line, `#` comments and blank lines ignored. A
plain name matches case-insensitively with any run of up to three non-alphanumeric
characters allowed between its words, so `Acme Corp` also finds `acme-corp`,
`AcmeCorp`, `acme_corp` and `acme/corp`. A line beginning `re:` is used as a
regular expression verbatim, for a name that needs a word boundary. An entry
shorter than four characters is refused at load: it would match half the corpus,
and a permanently red gate is worse than a dark one.

Usage:
  scripts/check-client-names.py                 scan the repo containing the cwd
  scripts/check-client-names.py --repo PATH     scan that repo
  scripts/check-client-names.py --no-commits    tree only, skip commit messages
  scripts/check-client-names.py --base REF      override the merge-base
  scripts/check-client-names.py --history       plus every reachable commit
  scripts/check-client-names.py --suite --history   that, for every repo
  scripts/check-client-names.py --pre-push REMOTE   plus what a push sends (stdin)
Exit status: 0 clean or skipped, 1 hits found, 2 misconfigured.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fleetconf import CONF  # noqa: E402

# check-ownership.py already solved "which commit is this branch actually
# descended from", twice, against two real red-on-clean failures (batch 003 and
# leg 010). Its filename has a dash so it cannot be `import`ed by name; loading
# it by path keeps one implementation rather than a second held equal by nobody.
_spec = importlib.util.spec_from_file_location(
    "_check_ownership", HERE / "check-ownership.py")
_own = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_own)

MIN_LEN = 4
# Encoded spellings of a byte. A captured wire frame lands in a fixture as one
# of these, and the name inside it is invisible to a text scan.
HEX_TOKEN = re.compile(rb"0[xX]([0-9a-fA-F]{2})|\\x([0-9a-fA-F]{2})")
BARE_BYTE = re.compile(rb"(?<![0-9A-Za-z])([0-9a-fA-F]{2})(?![0-9A-Za-z])")
B64_RUN = re.compile(rb"[A-Za-z0-9+/]{16,}={0,2}")
# A bare `HH` run is only a byte array if it is a long one; `de` and `ad` are
# words. The prefixed spellings need no such floor -- `0x` is unambiguous.
MIN_BARE_RUN = 8
SEP = rb"[^A-Za-z0-9]{0,3}"
# Per pattern per file. A leak is usually one or two literals; a file with
# hundreds is a committed artifact, and listing every offset there would bury
# the ones somebody can act on.
MAX_HITS_PER_PATTERN = 20


def _runs(data: bytes, token: re.Pattern, min_run: int):
    """Maximal runs of `token` separated by nothing alphanumeric.

    Yields (decoded bytes, [source offset per decoded byte]). Keeping the
    offsets is what lets a hit name the line somebody has to open.
    """
    out, offs, prev_end = bytearray(), [], None
    for m in token.finditer(data):
        gap = data[prev_end:m.start()] if prev_end is not None else b""
        if prev_end is not None and (re.search(rb"[0-9A-Za-z]", gap) or not gap):
            if len(out) >= min_run:
                yield bytes(out), offs
            out, offs = bytearray(), []
        out.append(int(next(g for g in m.groups() if g), 16))
        offs.append(m.start())
        prev_end = m.end()
    if len(out) >= min_run:
        yield bytes(out), offs


def decoded_views(data: bytes):
    """Every (decoded bytes, offsets, how) view a tracked file encodes."""
    for dec, offs in _runs(data, HEX_TOKEN, 1):
        yield dec, offs, "hex"
    for dec, offs in _runs(data, BARE_BYTE, MIN_BARE_RUN):
        yield dec, offs, "hex"
    for m in B64_RUN.finditer(data):
        try:
            dec = base64.b64decode(m.group(0), validate=True)
        except (binascii.Error, ValueError):
            continue
        if dec:
            yield dec, [m.start()] * len(dec), "base64"


def repo_root(start: Path) -> Path | None:
    r = subprocess.run(["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    return Path(r.stdout.strip()) if r.returncode == 0 else None


def load_denylist(path: Path) -> list[tuple[int, re.Pattern]]:
    """(denylist line number, compiled bytes pattern) for every entry.

    The line number is the handle every message uses, so that a report can be
    acted on without ever restating the name it is about.
    """
    pats: list[tuple[int, re.Pattern]] = []
    problems: list[str] = []
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            body = line[3:].strip()
            if not body:
                problems.append(f"entry #{n}: empty `re:`")
                continue
            try:
                pats.append((n, re.compile(body.encode("utf-8"), re.IGNORECASE)))
            except re.error as e:
                problems.append(f"entry #{n}: bad regex ({e})")
            continue
        if len(line.replace(" ", "")) < MIN_LEN:
            problems.append(
                f"entry #{n}: shorter than {MIN_LEN} characters. It would match "
                "most of the corpus, and a permanently red gate is worse than a "
                "dark one -- use an `re:` entry with a word boundary instead")
            continue
        toks = [re.escape(t.encode("utf-8")) for t in re.split(r"[^A-Za-z0-9]+", line) if t]
        pats.append((n, re.compile(SEP.join(toks), re.IGNORECASE)))
    if problems:
        print(f"denylist at {path} is not usable:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        sys.exit(2)
    return pats


def redact(blob: bytes, m: re.Match, entry: int, width: int = 100) -> str:
    """One line of context with the match itself replaced by its entry number."""
    start = blob.rfind(b"\n", 0, m.start()) + 1
    end = blob.find(b"\n", m.end())
    end = len(blob) if end < 0 else end
    line = blob[start:m.start()] + f"[redacted:#{entry}]".encode() + blob[m.end():end]
    text = line.decode("utf-8", "replace").strip()
    return text if len(text) <= width else text[:width] + " ..."


def line_of(blob: bytes, offset: int) -> int:
    return blob.count(b"\n", 0, offset) + 1


def scan_bytes(label: str, data: bytes, pats) -> list[str]:
    """Every hit in one file's bytes, as text and as what it encodes.

    `label` is what a hit names: a tracked path for the tree scan, a blob id and
    the path it was first seen at for the history scan. One body for both, so a
    decoder added for the tree is a decoder the history has too.
    """
    hits: list[str] = []
    binary = b"\0" in data[:8192]
    for entry, pat in pats:
        # EVERY occurrence, not the first. Reporting one match per pattern
        # turns a cleanup into whack-a-mole -- the 2026-09-05 embarch-api
        # find had two in one file and the second only appeared after the
        # first was fixed, which is exactly how a scrub misses one.
        ms = list(pat.finditer(data))
        for m in ms[:MAX_HITS_PER_PATTERN]:
            if binary:
                hits.append(f"  {label} (binary, byte {m.start()})  denylist entry #{entry}")
            else:
                hits.append(f"  {label}:{line_of(data, m.start())}  denylist entry #{entry}\n"
                            f"      {redact(data, m, entry)}")
        if len(ms) > MAX_HITS_PER_PATTERN:
            hits.append(f"  {label}  ... and {len(ms) - MAX_HITS_PER_PATTERN} more "
                        f"for entry #{entry}")
    # What the file *encodes*. Reported separately: the fix is different --
    # the literal on that line is not the name, it is what produces it.
    seen = set()
    for dec, offs, how in decoded_views(data):
        for entry, pat in pats:
            for m in list(pat.finditer(dec))[:MAX_HITS_PER_PATTERN]:
                line = line_of(data, offs[m.start()])
                if (entry, line, how) in seen:
                    continue
                seen.add((entry, line, how))
                hits.append(f"  {label}:{line}  denylist entry #{entry}, "
                            f"{how}-encoded -- the bytes decode to it, so no "
                            f"text scan sees it")
    return hits


def scan_paths(paths, pats, what: str = "the PATH itself") -> list[str]:
    hits = []
    for raw in paths:
        if not raw:
            continue
        for entry, pat in pats:
            if pat.search(raw):
                rel = raw.decode("utf-8", "surrogateescape")
                hits.append(f"  {rel}  <- {what}, denylist entry #{entry}")
    return hits


def scan_tree(root: Path, pats) -> list[str]:
    """The tracked files as they sit on disk: paths and contents."""
    hits: list[str] = []
    files = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                           capture_output=True).stdout.split(b"\0")
    hits += scan_paths(files, pats)
    for raw in files:
        if not raw:
            continue
        rel = raw.decode("utf-8", "surrogateescape")
        try:
            data = (root / rel).read_bytes()
        except OSError:
            continue  # a deleted-but-still-indexed path is not this check's problem
        hits += scan_bytes(rel, data, pats)
    return hits


def scan_messages(root: Path, pats, revs: list[str], seen: set | None = None) -> list[str]:
    hits: list[str] = []
    seen = set() if seen is None else seen  # commit ids already read
    log = subprocess.run(
        ["git", "-C", str(root), "log", "--format=%H%x00%B%x00%x00", *revs, "--"],
        capture_output=True).stdout
    for rec in log.split(b"\0\0"):
        if b"\0" not in rec:
            continue
        sha, _, msg = rec.strip(b"\n").partition(b"\0")
        if sha in seen:
            continue
        seen.add(sha)
        for entry, pat in pats:
            m = pat.search(msg)
            if m:
                hits.append(
                    f"  commit {sha.decode()[:12]} message  denylist entry #{entry}\n"
                    f"      {redact(msg, m, entry)}")
    return hits


def scan_history(root: Path, pats, revs: list[str], seen: dict | None = None) -> list[str]:
    """Every commit `revs` selects: its message, the paths it touched, and every
    blob reachable from it that is not reachable from what `revs` excludes.

    `revs` is a rev-list spelling -- `["--all"]` for the whole history,
    `[local, "^" + remote]` for what one pushed ref sends. The blobs come from
    `rev-list --objects`, so each is read once however many commits carry it,
    and an object the remote already has is not read at all. Paths come from
    `log --name-only` rather than from the object walk, which prints each blob
    under the first path it meets and would miss a known blob moved to a new
    name. `seen` spans the refs of one push so an overlap is read once.
    """
    seen = {"commit": set(), "path": set(), "blob": set()} if seen is None else seen
    hits = scan_messages(root, pats, revs, seen["commit"])
    names = subprocess.run(
        ["git", "-C", str(root), "log", "--format=", "--name-only", "-z",
         "--diff-merges=first-parent", *revs, "--"], capture_output=True).stdout
    paths = sorted({n.strip(b"\n") for n in names.split(b"\0")} - {b""} - seen["path"])
    seen["path"].update(paths)
    hits += scan_paths(paths, pats, "a PATH in history")
    objs = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--objects", "--filter=object:type=blob",
         *revs, "--"], capture_output=True).stdout
    want: list[tuple[bytes, bytes]] = []
    for line in objs.splitlines():
        sha, _, path = line.partition(b" ")
        if path and sha not in seen["blob"]:  # no path: a commit, not a blob
            seen["blob"].add(sha)
            want.append((sha, path))
    if not want:
        return hits
    # One `cat-file --batch` for the lot: a process per blob is most of the
    # cost of a history scan otherwise.
    out = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"],
                         input=b"".join(s + b"\n" for s, _ in want),
                         capture_output=True).stdout
    pos = 0
    for sha, path in want:
        nl = out.index(b"\n", pos)
        head = out[pos:nl].split()
        if len(head) < 3 or head[1] == b"missing":
            pos = nl + 1
            continue
        size = int(head[2])
        data = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        label = f"blob {sha.decode()[:12]} ({path.decode('utf-8', 'surrogateescape')})"
        hits += scan_bytes(label, data, pats)
    return hits


ZERO = re.compile(rb"^0+$")


def pre_push_revs(root: Path, remote: str, stdin: bytes) -> list[list[str]]:
    """The rev-list spelling of what each ref in a push sends.

    git hands a pre-push hook one line per ref:
    `<local ref> <local sha> <remote ref> <remote sha>`. A deleted ref sends
    nothing. A ref the remote already has sends `remote..local`. A NEW ref, or
    a remote sha this clone never fetched (a force-push over work done
    elsewhere), sends every commit the remote lacks: its tip, less everything
    under `refs/remotes/<remote>/`. For a new repo, or a push to a bare URL,
    that is nothing, so the whole history is read.

    **Not the whole history of every new branch, deliberately.** Every worker
    pushes two new branches per unit, and the whole of `embarch-doc`'s history
    was 104 MB of blobs and 21 s to scan on 2026-10-29; what those pushes send
    is a few commits. A name already public on another branch is not taken
    back by refusing a new one -- `--history`, run daily, is what finds it.
    """
    out = []
    for line in stdin.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        _lref, lsha, _rref, rsha = parts
        if ZERO.match(lsha):
            continue
        known = (not ZERO.match(rsha)) and subprocess.run(
            ["git", "-C", str(root), "cat-file", "-e", rsha.decode() + "^{commit}"],
            capture_output=True).returncode == 0
        out.append([lsha.decode(), "^" + rsha.decode()] if known
                   else [lsha.decode(), "--not", f"--remotes={remote}"] if remote
                   else [lsha.decode()])
    return out


def suite_repos(root: Path) -> list[Path]:
    """Every git repo directly under the fleet root, once each.

    A worktree there shares its main checkout's object store and refs, so its
    history is the same history; it is skipped by comparing git common dirs.
    """
    repos, common = [], set()
    for d in sorted(root.iterdir()):
        if not (d / ".git").exists():
            continue
        r = subprocess.run(["git", "-C", str(d), "rev-parse", "--git-common-dir"],
                           capture_output=True, text=True)
        c = (d / r.stdout.strip()).resolve()
        if r.returncode == 0 and c not in common:
            common.add(c)
            repos.append(d)
    return repos


def scan_repo(root: Path, pats, scan_commits: bool, base: str | None,
              history: list[list[str]] | None = None) -> list[str]:
    hits = scan_tree(root, pats)
    if history is not None:
        # A history scan subsumes the branch's own messages: every commit it
        # selects is read, the branch's included.
        seen: dict = {"commit": set(), "path": set(), "blob": set()}
        for revs in history:
            hits += scan_history(root, pats, revs, seen)
        return hits
    if not scan_commits:
        return hits
    picked = base or _own.pick_base(str(root))
    if picked is None:
        print("no base ref (tried main, origin/main); commit messages not scanned",
              file=sys.stderr)
        return hits
    return hits + scan_messages(root, pats, [f"{picked}..HEAD"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", help="repo to scan (default: the one containing the cwd)")
    ap.add_argument("--no-commits", action="store_true",
                    help="scan the tree only, not this branch's commit messages")
    ap.add_argument("--base", help="override the merge-base for commit scanning")
    ap.add_argument("--history", action="store_true",
                    help="also scan every reachable commit's message, paths and blobs")
    ap.add_argument("--pre-push", metavar="REMOTE",
                    help="also scan what a push to REMOTE sends, from git's pre-push stdin")
    ap.add_argument("--suite", action="store_true",
                    help="every repo under the fleet root, each on its own (with --history)")
    args = ap.parse_args()
    if args.suite and (args.repo or args.pre_push is not None or not args.history):
        print("--suite is history-only: --suite --history, no --repo, no --pre-push",
              file=sys.stderr)
        return 2

    state, deny = CONF.state_dir, CONF.client_denylist
    if not state.is_dir():
        # Not the machine this fleet runs on: CI, a fresh clone, a second
        # instance not yet installed. Nothing here is being guarded, so failing
        # would buy a standing exception rather than any safety.
        print(f"SKIP: no state directory at {state}; nothing to check against.")
        return 0
    pats = load_denylist(deny) if deny.is_file() else []
    if not pats:
        # Absent and empty are the same state -- this check is dark -- so they
        # get the same answer. An earlier draft let an empty file pass with a
        # printed warning, which is worse than either: `check-docs.py` discards
        # a passing check's stdout, so the warning would have been invisible in
        # the one place anyone reads it, and the gate would have reported nine
        # green while the ninth was doing nothing.
        what = "is empty" if deny.is_file() else "does not exist"
        print(f"the client denylist at {deny} {what}\n\n"
              "A configured fleet with this check dark is the failure it exists to\n"
              "prevent -- a muted alarm that looks fine is worse than no alarm, and\n"
              "the whole point of the file living outside every repo is that nothing\n"
              "in a repo can supply a default. Write it: one name per line, `#` for\n"
              "comments, `re:` for a pattern. It must never be committed anywhere.\n\n"
              f"    umask 077 && $EDITOR {deny}\n\n"
              "A fleet with genuinely no names to hide does not want this check in\n"
              "its gate; remove it from check-docs.py rather than leaving it dark.",
              file=sys.stderr)
        return 2

    if args.suite:
        roots = suite_repos(CONF.root)
    else:
        root = repo_root(Path(args.repo).resolve() if args.repo else Path.cwd())
        if root is None:
            print(f"not a git repo: {args.repo or Path.cwd()}", file=sys.stderr)
            return 2
        roots = [root]
    history = None
    if args.pre_push is not None:
        history = pre_push_revs(roots[0], args.pre_push, sys.stdin.buffer.read())
    elif args.history:
        history = [["--all"]]

    rc = 0
    for root in roots:
        hits = scan_repo(root, pats, not args.no_commits, args.base, history)
        if hits:
            rc = 1
            print(f"{len(hits)} client-name hit(s) in {root}:\n")
            for h in hits:
                print(h)
            print()
        else:
            print(f"OK: {root.name} clean against {len(pats)} denylist entr"
                  f"{'y' if len(pats) == 1 else 'ies'}"
                  f"{', history included' if history is not None else ''}.")
    if rc:
        print(f"The name is not printed. Open {deny} at the entry number to see\n"
              "which one, and do not paste it into a commit message, a log entry or\n"
              "an agent transcript -- that is the leak, not the fix. A blob hit\n"
              "names the path it was first seen at; `git log --all --find-object=<blob>`\n"
              "names the commits that carry it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
