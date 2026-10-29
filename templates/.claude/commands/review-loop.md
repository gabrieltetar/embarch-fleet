---
description: Run an independent reviewer loop on a branch before it goes out for review - delta rounds, one context pack, a findings ledger, and a stop rule.
argument-hint: "<base ref> [--reviewers N] [--cap N] [--name NAME]"
---

**A pre-PR review loop, run from the session that owns the branch.** Not
`{{FLEET_REPO}}/gate.md`'s merge-time `embarch-reviewer`, which is unchanged:
that one reads one landed unit for intent; this one hunts defects on a branch
round after round until the rounds stop paying.

Arguments: `$ARGUMENTS` — the base the branch is reviewed against (required),
reviewers per round (default 2), the round cap (default 6), and a loop name
(default: the branch).

**Why it is shaped like this** — measured on one field project, 2026-09-09 to
2026-10-20: fresh reviewers were **54 % of review-loop cost**, every one
re-read the whole branch and a free-text handled list that grew each round,
rounds 4–11 of one loop found no high for 59 M units, and the state in `/tmp`
was lost twice. `{{FLEET_REPO}}/scripts/review-loop.py`'s header has the rest,
the ledger format and the stop rule. Call it `RL` below.

## Once per loop

1. `python3 RL init --repo . --base <base> [--cap N] [--name NAME]` prints the
   loop directory, `LOOP`. **It already exists → this is a resume:**
   `python3 RL status LOOP` and pick up at the round it shows open. The ledger
   sits in the project's ignored `embarch/` folder, or inside `.git` — never
   `/tmp`, never tracked.
2. **Write `LOOP/context.md` once, and keep it under ~20 KB**: a map of the
   files the branch touches and what each is for; the spec sections in scope
   **as extracted text with page cites** (from `embarch/atlas/` when the
   project has one); the project's rules (its `CLAUDE.md`, decisions it must
   not contradict). Every reviewer reads this instead of re-deriving it, which
   is most of what a fresh reviewer used to spend.

## Each round

3. `python3 RL round LOOP` prints the brief. Round 1 reads the whole branch;
   every later round is the diff since the last reviewed SHA, the functions it
   touches and their call sites. `--full` for a final whole-branch round before
   the PR; `--verify` when step 6 says so. It snapshots the tree, so you may keep
   working while reviewers read.
4. **Spawn the reviewers in one message**, `embarch-loop-reviewer`, each given
   the brief path, `LOOP/context.md` and **one lens** — e.g. correctness,
   conformance to the spec in the pack, concurrency and lifetimes. Two lenses
   beat two copies of one. `--verify` takes exactly one reviewer.
5. **Ingest every report** — write it to a file first (quoted heredoc), then
   `python3 RL ingest LOOP --reviewer <lens> --tokens <the agent's total
   tokens> < <file>`. It parses the `FINDING` lines, merges the same finding
   from two reviewers, and records the tokens so `status` answers "are the rounds
   converging?" without anyone having to ask.
6. **Answer every row**, then end the round. Fix and commit, then
   `close LOOP F<n> fixed <sha>`; or `close LOOP F<n> rejected <why>`; or
   `decision <why>` for a design call — and record that decision wherever the
   project keeps them. A rejected row goes into every later brief, so it is not
   reported twice. `python3 RL end LOOP` refuses while a row is open, then
   prints the decision:
   - `continue` → step 3;
   - `verify` → step 3 with `--verify` and one reviewer, then `end`;
   - `stop` → `python3 RL status LOOP`, and report it.

## Reporting

`status` is the report: one row per round (reviewers, tokens, severities, the
decision) and one per finding. Quote it; do not re-summarise it. **The first
real run is also the replay `tasks/suite/051` asked for** — say how its
per-reviewer tokens compare with the field's ~2.5 M per reviewer.
