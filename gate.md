# EmbArch: fleet merge gate

**Status:** active, 2026-10-25. **Split out of [protocol.md](protocol.md) §10 on 2026-10-25**, which had 9 of its bytes left when the first npm repo (`embarch-chat`) needed a gate line — the seam [README.md](README.md) had named for it in advance. The text below moved **verbatim**, plus that one bullet. Bare `§N` references are sections of [protocol.md](protocol.md); a `§10` among them means this doc.

Run by the worker, then **re-run independently by the supervisor** on the merge result — not on the branch:

- `cargo build`, `cargo test`, `cargo clippy --all-targets -- -D warnings` in the touched repo — which reach **only the packages they select**, never an in-repo non-member crate ([embarch.md](../embarch-doc/embarch.md) §5). **The native Windows build is a debt, not a gate item**, unrunnable from a worktree twice over — `hidapi`'s `build.rs` wants an MSVC `cc` WSL lacks, and Windows `cargo.exe` cannot follow a worktree's Linux symlinks to its path-dep siblings. It takes 52 s from the main checkout [2026-09-06], so a unit touching `embarch-core` records the debt; the owner runs it.
- **An npm repo runs npm, not `cargo`** — `embarch-chat`, the first, since 2026-10-25: `npm ci` in the worktree, then `npm run build`, `npm run typecheck`, `npm test` and `npm run test:webview`, the four its `CLAUDE.md` names. `typecheck` stands where `clippy` does: esbuild builds code that does not type-check, so `build` alone passes it. A test that skips for want of an outside binary (`EMBARCH_DESK_BIN`) skips on the branch too, and a skip is not a red.
- **A Python repo runs `pytest` in a venv of its own** — `embarch-atlas`, the first, since 2026-10-29: `uv venv && uv pip install -e '.[dev,tokens,mcp]'` in the worktree (the extras its CI installs), then `.venv/bin/pytest -q`, the command its `CLAUDE.md` names, plus the client-name check below, which that `CLAUDE.md` wants before every commit. **Never the main checkout's `.venv`**: its install is editable and resolves to the main checkout's `src/`, so run from a worktree it imports and passes `main`'s code, not the branch's [measured 2026-10-29]. A skip for want of a real west workspace or a built atlas is expected. **A `test_public_guard` skip is a red**: its denylist check did not run, because the worktree's parent lacks the `.atlas-local` link `.claude/leg.md` makes.
- The whole `embarch-doc` gate as **one command, `python3 scripts/check-docs.py`** — **which names its own checks, and this doc does not.** The enumeration here went stale twice in two days, and a supervisor triaging a red against a short list is triaging blind. `CHECKS` in that file is the list; no count is restated anywhere.
- **`check-client-names.py --repo <path>` on the code repo too**, alongside `cargo`. The wrapper covers only `embarch-doc`, a fifth of the suite's bytes, and 2026-09-04's leak was mostly on the other side. Per repo, never one pass over the siblings — a leg and a worker run from `embarch/.worktrees/`, where a sibling walk finds other worktrees. It reads a denylist kept outside every repo and **never prints what it matched**; its header carries the gaps it leaves.
- **`build_features.py --check` validates the fragments only.** The byte-equality assertion `--check-assembled` is deliberately **not** in a branch gate: `suite/features.md` is `never` for a worker in §3's table, so asserting it per branch left a feature-shipping worker unable to be green on this and `check-ownership.py` at once (leg 009, twice). It is asserted on `main`, by CI and the fold.
- **`check-ownership.py --scope <sub-project>`** on both branches, `--code-repo` added on the code one — the mechanical form of §3. Either `core` or `embarch-core` is accepted; **`suite` is refused outright, because a cross-repo change is §8's.** Without it §3 is prose nothing reads: a worker's edit to [embarch.md](../embarch-doc/embarch.md)'s status table is *plausible by construction*, so `check-staleness.py` (which only flags a row disagreeing with a sub-project doc) passes it, and the collision §9 prevents happens anyway.

That is [embarch-dev-workflow.md](../embarch-doc/embarch-dev-workflow.md) §6's standard applied per branch, not per commit. Nothing here licenses a lower bar because an agent wrote it.

**A reviewer reads for intent, alongside landing, and gates no merge.** When a
unit's branches merge, the supervisor spawns an `embarch-reviewer` on the diff
against that sub-project's decisions and the reversals index. Findings land in
`inbox/` and in the unit's log entry; a confirmed contradiction is reverted by
SHA — the first thing that ever uses the SHAs §11 requires.
**Merge-on-green is unchanged**: a blocking reviewer would make every unit a
two-agent serial dependency, and the owner chose progress over caution here as
elsewhere.

**A reviewer reads the leg's worktree, or a SHA — never the tree it is spawned
into.** It lands in the owner's checkout, which a leg never advances, so a
relative read answers about the commit the leg *started* at: one unit stale on
its first review, three on its last, and it never errors. What that produces is a
confidently wrong **`pre-existing`** label on precisely the contradictions this
leg introduced, which is the one class §10 exists to catch. So the supervisor
passes both worktree paths in the spawn, and a reviewer given neither says so
rather than reading what is under it.

**It is the last thing the fold waits for, and that is not the same as gating.**
"Spawn it and never wait" was the rule until 2026-09-05 and was incoherent with
§11: the `**Reviewer:**` line rides *inside* the fold commit, which lands a
minute or two after the merge, while a reviewer reports in ninety seconds to
three. The line was required to state a fact that did not exist yet, and three
of leg 011's were true by luck. So the merge does not wait and the *entry* does:
spawn at merge, do the rest of the fold, collect the reviewer immediately before
writing the entry. The wait is under a minute against a twenty-minute worker,
and it is what makes the tally evidence rather than a guess.

**A reviewer does not count against the worker wave.** The rule that said it did
was self-defeating: ninety seconds of reading cost a whole slot out of a
DEGRADED wave of two — this machine's steady state — so eight entries in,
one had run and six were skipped for the wave alone. **The question the tally
exists to answer could not be answered under the rule governing it.** Skip only
on a HOLD, a recent 429, or a leg ending at its unit cap where the reviewer would
outlive it, and **the log says which**: "no findings" and "no reviewer ran" are
different facts.

**The gate is mechanical and catches broken, not wrong.** The one judgement the supervisor adds: read the diff before merging when the change touches a shared crate (`embarch-study-designer`, `embarch-topology`, and `embarch-core-client` — inside `embarch-api` but path-depended on by `embarch-ui`, so an `api` worker can change `ui`'s dependency without owning `ui`), a wire type, or retires a decision. That is where passing and correct diverge most expensively; everything else merges on green.

**Merge order** is shared crates first, then consumers, then `embarch-doc` — §6's cross-repo sequencing applied to a leg's independent passes. Within a tier, oldest branch first, so nothing sits.

