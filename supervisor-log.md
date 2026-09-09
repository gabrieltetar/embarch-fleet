# Supervisor log

**Status:** active, 2026-09-03. Three batches ran before the relay ([protocol.md](protocol.md) §6) replaced them; entries below `batch 003` are per-batch, and everything after is per-unit.

One entry per **unit** — one task landed or blocked — **newest first**. Written
by the supervisor as part of landing that unit
([protocol.md](protocol.md) §6 step 4), and read by
the owner as the review surface for work that landed without approval (§11).

**It is also the relay handoff.** A leg dies after four units and the listener
spawns a successor whose step 0 reads these entries cold, with no other memory of
its predecessor at all. So an entry that omits something — a rebase that has not
settled, a `suite` task parked with a live 30-minute window, a failure likely to
recur — is a fact the next leg cannot recover, and it will act confidently
without it.

**Per unit rather than per leg** because a leg can be killed at any moment;
closing VS Code is a normal thing to do. An entry written at the end of a leg is
an entry that does not exist for the leg that got killed.

What *shipped* is not restated here — the workers' own `changelog.d` fragments
carry that into `history/<scope>.md`. This file carries what was **decided**,
what did not land, and what still needs a board.

**Folded daily.** On its first unit after local midnight a supervisor folds the
previous day's unit entries into one dated entry, keeping every SHA and every
debt. Per-unit entries would otherwise hit the roll cap every few days and the
handoff would get shorter and shorter — the opposite of what a relay needs.

Past **40 KB** the oldest whole days roll into `log-archive/` —
`scripts/fold-day.py --roll`, which never splits a day and always leaves the two
newest. The line was 25 KB and named the instance's `history/archive/`; neither
was right. This log lives in this repo, and 25 KB could not hold one folded day
(the `2026-09-04` entry below is 25 KB on its own), so nothing ever rolled it.

## Entry shape

The example below uses placeholders on purpose. It once used a real-looking date
and real-looking SHAs, and step 0 — which reads the newest entries as its
handoff — picked the *template* up as work that had run, complete with a hardware
debt that never existed. Second instance of the same root cause as batch 001's
recovery greps: documentation shaped exactly like the data it documents.

```markdown
## <yyyy-mm-dd HH:MM> — <scope>/<NNN> <slug>

**Decided:** anything the supervisor approved on the owner's behalf, suite-wide
first. If it decided nothing, say "nothing" — an empty line here is ambiguous.
**Merged:** `agent/<scope>/<task>` (code `<sha>`, doc `<sha>`). Always both SHAs —
under `embarch-dev-workflow.md` §6 there is no merge commit and no surviving
branch name, so the SHA is the only handle a revert has.
**Blocked:** `agent/<scope>/<task>` — why, and what state the task was left in.
**Reviewer:** `no findings` / `N finding — <inbox file>` / `skipped (<why>)`.
Exactly one of the three, always, and **collected before this entry is written**
rather than predicted — the reviewer is spawned at the merge and waited for
here, which is the only point in the unit where waiting costs anything and the
only point where the line can be true. Never `pending`, and never a fourth form:
whether per-unit review is worth double the spawns is undecided, and this line
is the only evidence that will settle it.
**Hardware debts:** what needs a board, and what board.
**Budget:** verdict at start and end, and the wave size it produced.
**Least sure about:** one sentence. Not optional.
```

**The heading's date and time are the wall clock at the fold, and
`fold-commit.py` writes them.** Do not type them and do not work them out — it
stamps the newest entry from the machine clock just before it commits, and says
so when what you wrote was more than five minutes out. Nothing used to do this
and nothing checked it, so the field was a guess: measured 2026-09-06 across all
63 entries, **41 were more than five minutes ahead of the fold that wrote them,
the worst by 63 minutes**, and the error grows monotonically within a leg and
resets at the next one — the signature of reading a clock once and estimating
from there. It is not cosmetic. `fold-day.py` groups a day by *this* date, so an
entry written at 23:50 and stamped 00:15 folds into the wrong day and nothing
says so; and under a full delegate this log is the only review surface
([protocol.md](protocol.md) §11), where a heading an hour out correlates with
nothing — not Slack, not `.fleet/tick`, not `git log`.

**Entries before 2026-09-06 17:00 carry the old estimated times**, and they are
not corrected: they are true in every other respect, and rewriting this file
wholesale is exactly what `fold-day.py`'s refusals exist to prevent. Read them as
±1 hour, and use the fold commit's own timestamp when the minute matters.

Every one of those seven markers is written literally, as `**Field:**` at the
start of a line, and `fold-commit.py` refuses a fold whose entry drops one or
bends one. That is newer than most of this file: `umbrella/010` below opens its
debt with `**Hardware debts: one, and it is free.**`, bolding the whole phrase,
which is invisible to the fold's own ledger — three of 2026-09-05's ten entries
lost a field that way. The shape is data, not decoration.

A folded day collapses that into one entry with the same fields, listing every
unit under **Merged** and **Blocked**:

```markdown
## <yyyy-mm-dd> — <N> units
```

---

## 2026-09-09 01:03 — core/023 a true sentence written by the wrong hand, and an inference now hedged in two docs

**Decided:** five.

**(1) `embarch-token.md` §2 no longer claims something Core does not do.** It said *"Core creates
the directory and file with owner-restricted permissions."* `embarch-core/src/token_store.rs` calls
`restrict_token_file_permissions(path)` with the **token file**, and its `icacls` invocation names
that file as its sole target; the parent directory is created a few lines earlier by a plain
`create_dir_all` with no ACL call at all. So only the file is locked down. The new wording says
that, says the `icacls` call names the file only, and **explicitly declines to assert what the
directory's default ACL concretely grants** — which matters because nobody looked and nobody here
can: a WSL session cannot read a Windows ACL, and the task forbade the attempt. The reviewer
re-read the source independently and confirmed both the claim and that the hedge is real.

**(2) The ownership check went red and it was right to.** `check-ownership.py --scope core` refused
`embarch-token.md` — a shared suite-level doc `protocol.md` §3 reserves to me, whose worker-side
route is a `status.d/core-*` fragment. **The worker did not err: the task file told it that path was
in scope, and it obeyed, reported the failing check plainly, and pre-labelled it a task-authorized
exception.** The defect is that **a task file is prose and nothing validates its scope claims
against §3**, so a worker takes it as authority and the check fires only after the branch exists. I
read the diff, judged it, and **adopted the edit as my own write** rather than sending it back —
the content is mine to own and it replaces a false statement with a true one. Filed as
**`tasks/doc/029`** (`Owner: required` — the fix lives in `scripts/` or `tasks/README.md`), and it
is explicitly the sibling of `tasks/doc/028`: two legs running, a task file has asserted something
mechanical that no script checks. That is a class.

**(3) The reviewer found the one sentence that had smuggled an unobserved fact back in, and I
hedged it.** The new text explained *why* the loose directory is structurally necessary: it is what
lets `embarch-topology`'s `enrollment.toml` be read and written by both the Core service account
and an unprivileged CLI. **That consequence is an inference** — from "Core never restricts the
directory" to "therefore two accounts can use it" — inherited verbatim from `embarch-topology`
decision 23, which makes the same leap, and **never checked against a real ACL by anything in this
suite.** It was stated as fact in a doc whose whole point this unit was to make honest. I rewrote it
to attribute the conclusion to decision 23 and to say in the doc itself that it is not measured.
`embarch-token.md` is 8,911 B, nowhere near its cap.

**(4) Decision 23's citation holds in the other direction too.** The reviewer read
`embarch-topology/decisions/storage.md`: decision 23 already carries its 2026-09-07 correction
("not admin-owned, which was the original wording's error") and already names
`embarch-token.md`'s old "directory and file" phrasing as the error being fixed here. The two
documents now agree and neither is the stale one — which is worth stating, because this doc **is
where topology's original wrong idea came from**, and a leg that corrected one side and not the
other would have left the loop.

**(5) A numbered `embarch-core` decision is owed and was deliberately not written**, burndown
forbidding it. The reviewer checked `embarch-core/decisions.md`, `decisions/handshake.md` and
`decisions/surfaces.md` and confirms **nothing on Core's own decision log records that the shared
directory's permissiveness is deliberately preserved.** Topology records the dependency from
topology's side only, so **a future core-side change tightening `%ProgramData%\embarch`'s ACL would
silently break the cross-repo sharing with nothing in this repo to catch it.** That is the second
owed decision this burndown has produced (`outpost/015` was the first) and it is the owner's to
author.

**Merged:** `agent/core/023-token-dir-acl-doc` (doc **`2d070a8`**, fold **this commit**). The code
branch `agent/core/023-token-dir-acl` carried **zero commits** — verified, not taken on report. Gate
re-run by me on the merge result: `python3 scripts/check-docs.py` **all 10 green** (before and after
my hedge in (3)); `check-ownership.py --scope core` **red by design, see (2)**;
`check-client-names.py` clean. **No `cargo` gate and no native Windows build** — the unit changed no
code, and the standing debt that this fleet cannot build `embarch-core` for Windows is untouched and
unaffected, since nothing about `token_store.rs` changed.

**No `changelog.d/` fragment**, on the worker's judgement that a wording correction ships nothing.
I let that stand; the substantive record is this entry. Flagging it because a future reader looking
for this fix in `history/core.md` will not find it.

**Blocked:** nothing.

**Reviewer:** no findings.

**Hardware debts:** none new. Leg 058's list carries forward unchanged — including that a native
Windows build of `embarch-core` is owed and the fleet cannot run one.

**Budget:** `PROCEED` / **BURNDOWN** — weekly **95.3%** against the 97% cap at the leg's start,
5-hour 33.6%, no 429. Wave suggested 12, used 4.

**Least sure about:** **whether adopting the out-of-map edit was the right call rather than sending
it back through `status.d/`.** Adopting it landed a true sentence tonight and cost one task file;
bouncing it would have honoured §3 exactly and cost a whole unit to reland the same three
paragraphs. I chose the content, and I am aware that "the supervisor adopted it" is a precedent that
makes §3 softer every time it is used — which is exactly why `tasks/doc/029` exists and why I would
not do this twice in one leg.

---

## 2026-09-09 01:01 — study-designer/024 a verified claim whose converse was false, caught in one reviewer pass

**Decided:** four.

**(1) `embarch-study-designer/README.md` no longer documents a feature set that does not exist.**
The Features section listed a `core-validation` Cargo feature and a `signal` module holding
`SignalCheck` / `PostHocValidation` / `ContentValidity` — **decision 48 removed all of it outright**
(`decisions/removed.md`), and there is no `src/signal.rs` or `src/validation.rs`. It also never
mentioned `gatt-extract`, `study-ui` or `eap-parse`, three real features `Cargo.toml` has carried
for a while. The section now lists `alloc`, `std`, `ffi`, `gatt-extract`, `study-ui`, `eap-parse`
with one-line descriptions taken from `spec.md §3` and the `Cargo.toml` feature comments.

**(2) The worker verified all three live claims against the tree before editing, and named the
greps.** I asked for that in the spawn prompt because this task was **filed by a unit whose own diff
had already invalidated one of its four claims**. The mechanism worked: it re-confirmed the struck
`PowerSampleWindow` sub-claim was genuinely stale rather than quietly re-deriving it.

**(3) The finding, and it is a shape to remember: a checked claim and its converse are two
claims.** The worker left the Layout table alone on the verified basis that **every module the table
lists exists in `src/`** — true, and reported in words that read like "the table is correct". The
reviewer checked the converse in one pass and found it false: **the table omits about a dozen
modules that do exist**, including the ones backing the three features this very unit had just
finished documenting. So the README briefly had a Features section naming a capability and a module
map that would not tell you where it lives. **Filed as `tasks/study-designer/025`, not fixed here** —
a different edit from the one this task authorised, and the reviewer confirmed no decision governs a
README's module table, so it is an accuracy task rather than a design question.

**(4) `spec.md` and `open.md` are untouched, so `study-designer`'s two reserve debts are exactly
where leg 058 left them** (`spec.md` 640 B, `open.md` 458 B, both filed under the *open*
`tasks/study-designer/006`). I told the worker not to compact them: an open compaction task is
somebody's future unit, not this one's tax.

**Merged:** `agent/study-designer/024-readme` (code **`c4ff144`** in `embarch-study-designer`, a
README-only 19/6 diff; doc **`4a33e54`**, fold **this commit**). Gate re-run by me on the merge
result: `cargo build`, `cargo test --all-features`, `cargo clippy --all-targets --all-features --
-D warnings` all green; `check-client-names.py --repo embarch-study-designer` clean;
`python3 scripts/check-docs.py` **all 10 green**; `check-ownership.py --scope study-designer` green,
2 paths. **No consumer rebuild, deliberately** — `embarch-api`, `embarch-core`, `embarch-ui` and
`embarch-umbrella` all path-depend on this shared crate and the diff touches `README.md` only, so
there is no declaration for a consumer to see.

**Blocked:** nothing.

**Reviewer:** no findings.

**Hardware debts:** none new. Leg 058's standing list carries forward unchanged.

**Budget:** `PROCEED` / **BURNDOWN** — weekly **95.3%** against a 97% cap at the leg's start,
5-hour 33.6%, no 429 at any point. Wave suggested 12, used 4.

**Least sure about:** **whether filing `025` rather than fixing it was right at 01:20 on the last
night of a burndown window.** The edit is small, the information was in front of me, and burndown
exists to spend an allowance that expires in six hours — but the task authorised a Features rewrite,
the Layout table is a separate surface, and a supervisor widening a landed unit's scope on its own
judgement is how a diff stops matching the task that justified it. I would make the same call again
and I am not certain it is the throughput-maximising one.

---

## 2026-09-09 00:57 — ui/018 a split that conserved every sentence and still lost an invariant

**Decided:** five.

**(1) `embarch-ui/spec.md` is out of reserve by a split, not a squeeze** — 9,613 B → **8,568 B
(83.7%)**. The worker ran `check-duplication.py embarch-ui` first as the task asked, found only the
expected spec/decisions overlap and no true duplicate, and moved the *reference* half of "The trace
chart" — the reference-dut capture numbers, the `/api/trace/.../bins` endpoint shape, and the two
served view caps (`MAX_ROWS`, `MAX_STREAM_NAME_LEN`) — into a new **`embarch-ui/interfaces.md`**,
following the `embarch-core` precedent. It checked the seam for inbound links before cutting and
found only whole-file references, and it caught one sentence the split itself had duplicated.

**(2) The finding worth carrying forward: a split can conserve every sentence verbatim and still
lose an invariant, because *where* a fact lives is part of the fact.** The reviewer's conservation
check came back clean — every moved sentence byte-identical, typo included — and the unit was still
wrong. Of the two invariants the worker believed it had kept in `spec.md`, only the bounded SVG
element count survived **as an assertion**; the second, *filtering changes the drawing and nothing
else — the load repartition stays computed across every lane*, went across whole, and `spec.md` was
left **naming it as a topic that points elsewhere**. `DOC-COMPACTION.md` §3 assigns
invariants-as-a-list to `spec.md` specifically, and its hot/cold test calls this exact kind of fact
hot: it is what someone has to hold in their head *before* they touch lane filtering. **This is a
fourth instance of the `tasks/doc/026` class** (a compaction cutting something load-bearing while
honestly believing it was texture) and the first one where the mechanism was **demotion rather than
deletion** — which is worse, because a conservation check passes it. `doc/026` counts three
occurrences of the deletion form; the next leg to touch it should add this one, since a check that
diffs for lost *text* cannot see it.

**(3) Fixed in this fold rather than filed.** I restored the invariant to `spec.md` as a stated
fact with its reasoning cited (`decisions/trace-chart.md`), and — so the split still restates
nothing — replaced it in `interfaces.md` with an explicit statement that the invariant lives in
`spec.md` and why a reference file is the wrong home for it. `spec.md` is 8,568 B, still well clear.

**(4) I fixed a broken relative link the owner shipped 20 minutes before this leg started, because
it was red on `main` and would have blocked every unit of this leg.**
`changelog.d/ui-brand-token.added.md` (his commit `2e3b749`) links `decision 25` as
`embarch-ui/decisions/shell.md` from inside `changelog.d/`, which resolves to
`changelog.d/embarch-ui/...` — the target file exists, the link is missing its `../`. One character.
`check-docs.py` went from 9/10 to **all 10 green** on the merge result. Worth knowing that **leg
058 reported all 10 green and was telling the truth**: his commit landed during its final fold.

**(5) The owner's own `inbox/` drop about this unit is satisfied and consumed, not filed.**
`inbox/ui-brand-clause-must-survive-018.md` asked that `spec.md` still state that `--brand` carries
the logo's red and is never the accent, since `018` carried no `Must not delete:` list and was
claimed after that sentence landed. Verified by grep on the merge result: the clause is **untouched
and complete** at `spec.md:80` — the split only ever entered "The trace chart". Both its `Done when`
boxes are met, so I deleted the drop rather than filing a task that was already closed. Naming it
here is the not-silent half of that.

**Merged:** `agent/ui/018-compact-spec-doc` (doc **`09d745f`**, fold **`0028100`**). **Read those as
the rebased SHAs and know why.** My push was rejected non-fast-forward: the owner pushed `e314c64`
to `main` while I was folding ("ui: decision 25 records the traced header glyph and why it is not a
bitmap") — the same shared-`main` race leg 058 hit an hour earlier, from the same person, in the
same sub-project. I fetched and rebased my two commits over his, never forced; the gate was re-run
green after the rebase. Pre-rebase they were `bffdba4` and `a533e18`; a revert should use the
rebased pair. Same trees either way. The code
branch `agent/ui/018-compact-spec` carried **zero commits** — pushed unchanged, as instructed, and
verified by `rev-list --count origin/main..` = 0. Gate re-run by me on the merge result:
`python3 scripts/check-docs.py` **all 10 green** (after (4)); `check-ownership.py --scope ui` green,
4 paths; `check-client-names.py --repo embarch-ui` clean against 7 denylist entries. No `cargo`
gate — this unit changed no code, so there is nothing for one to be a gate on.

**Blocked:** nothing.

**Reviewer:** 1 finding — inbox/ui-018-load-repartition-invariant-lost-from-spec.md (real; fixed in
this fold per (3), and the drop consumed).

**Hardware debts:** none new, and none possible — no unit this leg touches hardware, and burndown
forbids bench work outright. Every standing debt from leg 058's entry carries forward unchanged.

**Budget:** `PROCEED` / **BURNDOWN** — 5-hour 33.6%, weekly **95.3%** against a 97% cap, resetting
in ~6h. Suggested wave **12**; I dispatched **4**, the leg's unit cap, all four simultaneously.

**Least sure about:** **whether my worktrees are in the wrong place and it matters.** `git -C <repo>
worktree add .worktrees/...` resolves the relative path against the *repo* directory, not my cwd,
so all eight of this leg's worktrees were created **inside** their repos
(`embarch-core/.worktrees/...`), which `.claude/leg.md` says to keep outside every repo tree, and
**`.worktrees` is in no repo's `.gitignore`**. Two workers found the real trees themselves and the
`core` one had to make its own sibling symlinks, because mine went to the path I *thought* I had
created. Nothing has been committed from a nested tree and every landed diff is clean, but a
repo-walking scan reading three copies of the same source is exactly the failure
`embarch-study-designer` decision 57 records. **The next leg must use absolute paths for
`worktree add`.**

---

## 2026-09-09 00:40 — study-designer/018 a 32-file citation sweep, and a reviewer that greppped for what was left instead of trusting "done"

**Decided:** six. **This is leg 058's fourth and last unit; the leg ends here at its cap, not on a
fault, a stop or a budget verdict. The burndown latch stands and expires on its own at 06:59.**

**(1) Every stale `design.md` citation in `embarch-study-designer` is gone, and the file count was
larger than the task knew.** The task was filed against **290 occurrences in 23 files** in `src/`;
the worker found and swept **32 files, 522 insertions / 534 deletions**, adding occurrences in
`Cargo.toml`, `tests/`, `tools/`, the two `.eap` fixtures and `.github/workflows/test.yml` — places
a `src/`-scoped grep never reaches. `design.md` was split into `spec.md`/`open.md`/`decisions/*` on
2026-09-04 with **no section numbering carried forward**, so every `design.md §N.N` in this repo had
been pointing at nothing for five days, and `decision 68` keeps `cargo doc` warnings out of the gate
so nothing would ever have caught them.

**(2) I verified the diff was comment-only myself rather than taking it on report, because this is a
shared crate.** §10 requires reading the diff before merging one, and 32 files is too much to read
line by line — so I read it structurally instead: `git diff -U0 -- '*.rs' | grep` for changed lines
that are **not** comments returned **nothing at all**, and I then read the whole of the
`Cargo.toml`, workflow and `.eap` fixture diffs by hand, since those are the files where a "comment"
is not syntactically obvious. That is the cheap version of the expensive check and I recommend it to
the next leg that lands a sweep.

**(3) The reviewer did the two things a sweep actually needs, and neither is re-reading the diff.**
First, it **sampled 12+ citations across the own-repo cases and six cross-repo targets and resolved
every number against the current decisions index** — the failure mode of a mechanical sweep is that
stripping `design.md §3` off an already-wrong number leaves a wrong number that now reads as
authoritative, and none were renumbered or retired-without-tombstone. Second, it **ran the task's own
grep at the merge SHA and confirmed zero `design.md` references remain repo-wide**, which is the
check that distinguishes a finished sweep from one that leaves a tail — a tail is worse than a
reported tail, because the next person greps `src/`, finds nothing, and closes it.

**(4) The deletions were audited for claims rather than pointers, which is the half this log keeps
having to insist on.** 534 deletions is a lot of room to lose something, and three legs running a
doc-editing change has under-described its own cuts. The reviewer confirmed every dropped bare-section
pointer was **genuinely dead** — there are **zero `milestone-*.md` files anywhere in the suite**, so
`milestone-9`, `milestone-11` and `ui-milestone-1` references were pointing at files that do not
exist — and that the surviving prose kept its claims. I read the `Cargo.toml` `study-ui` hunk myself
for the same reason: it lost three milestone citations in one edit and the sentence that survives
still says what the retired binary was and what replaced it.

**(5) The `.eap` fixtures are parsed inputs, not prose, and that was checked as a grammar question
rather than assumed.** The reviewer confirmed `#` is a comment marker in `eap_parse.rs`'s own
grammar, so those edits cannot change what the parser sees — and the `eap-parse` test suites pass.
Worth recording because "it's only a comment" is a claim about a parser, and this repo owns that
parser.

**(6) I corrected a stale sub-claim inside a task the same unit filed, which is a shape I have not
seen before.** The worker found `README.md` describing a feature set that no longer exists and
correctly filed `tasks/study-designer/024` rather than fixing it — that is a content rewrite, not a
citation fix, and refusing to widen its own scope was right. But one of that task's claims — that
the Layout table "still lists `PowerSampleWindow`" — **was already false when it was written,
because the same commit had just removed it.** The reviewer caught it and flagged it directly
instead of filing, which was the right call. I struck the claim in place rather than deleting it,
with the `grep` that disproves it, so nobody re-derives it; the task's other three claims (missing
`core-validation` feature, undocumented `gatt-extract`/`study-ui`/`eap-parse`) were verified accurate.
**A task filed by a unit can be stale on arrival if the unit's own diff moved the ground under it**,
and nothing checks that.

**Merged:** `agent/study-designer/018-design-md-citations-sweep` (code **`f2bc361`** in
`embarch-study-designer`; doc **`c657d60`**, fold **`af37164`**). Both fast-forwards; doc branch
rebased over `ui/004`'s fold first.

**Read the doc SHA above as the rebased one, and know why it changed** — this is the only rebase in
this leg that moved a SHA *after* it had been written down. My push of this fold was rejected
non-fast-forward: **the owner pushed `2e3b749` to `main` while I was folding** ("ui: decision 25
records the brand-vs-accent split, and the icon now exists"), which is exactly the shared-`main`
race the leg worktree exists to keep out of his working tree and cannot keep out of the ref. I
fetched and rebased my two commits over his — never forced — so the doc merge that this entry first
recorded as `e5725f5` is now **`c657d60`** and the fold is **`af37164`**. Both are the same trees.
The entry was corrected in a follow-up log commit; a revert should use the rebased SHAs. Gate re-run by me on the merge result: `cargo build`, `cargo test --all-features`
(green, including the `.eap` suites), `cargo clippy --all-targets --all-features -- -D warnings`
clean; `python3 scripts/check-docs.py` **all 10 green**; `check-ownership.py --scope study-designer`
green (3 doc paths, base `61d31c34b055`); `check-client-names.py --repo embarch-study-designer`
clean. **No consumer rebuild** — `embarch-api`, `embarch-core`, `embarch-ui` and `embarch-umbrella`
all path-depend on this crate, and I did not rebuild them, deliberately: the diff changes no
declaration, only comments, which is exactly what the non-comment grep in (2) establishes.

**Blocked:** nothing. **Four units dispatched, four landed, none blocked.**

**Reviewer:** no findings.

**Hardware debts:** **none new.** No unit this leg touched hardware; none could. Standing debts
carried forward in full: a native Windows build of `embarch-core` is owed and the fleet cannot run
one (`core/028`, `core/015`, `core/010`); `umbrella/037`'s corrected check 13 has never met the
bench; `embarch-outpost`'s Zephyr `tests/unit` cannot be built here; `embarch-dev-bench`'s
west/Zephyr toolchain is likewise absent; the four DUT-gated bench tasks are unchanged; `core/028`'s
`[assumed]` ESP32-C5 USB-enumeration fact still needs one look at one board; `dev-bench/002`'s
17-to-64-step study has never been attempted on the bench. **Plus one gate debt recorded new this
leg**, under `outpost/005`: `embarch-outpost`'s `tests/cross_decoder.py` **SKIPs in every worktree
the fleet creates**, because the sibling repos it cross-checks against are not beside it — a gate
that skips is indistinguishable from a gate that passes, and only running it in the main checkout
revealed that it genuinely passes.

**Budget:** `PROCEED` / **BURNDOWN** — 5-hour **30.8% → 32.0%**, weekly **94.8% → 95.0%**, both
against a 97% cap, weekly resetting in 6h21m. Suggested wave **12** throughout; I used **4**,
dispatched simultaneously, because 4 is the leg's unit cap and therefore the binding constraint.
**No 429 at any point**, so the mode is not cleared and the latch stands. **45 tasks dispatchable**
as this leg ends, down from 46 — four consumed, three filed (`outpost/015`, `doc/028`,
`study-designer/024`, plus `outpost/014` and `ui/021` as parks).

**Least sure about:** **that four reviewers in one leg found four different things and none of them
was a contradiction, which is either the system working or the reviewers converging on the
supervisor's own questions.** Every one of the four spawn prompts named, in prose, the specific place
I thought that unit could be wrong — and in three cases that is exactly where the reviewer's most
valuable output came from: reproducing the 1.5 KB measurement, finding `--allow-build-id-mismatch`'s
sibling gap, greping repo-wide for a sweep's tail. **That is a good outcome and a worrying
mechanism**, because it means the review's coverage is a function of how well the supervisor guessed
in advance, and a leg that wrote four generic prompts would have got four generic answers. The
`**Reviewer:**` tally this log keeps is measuring whether review is worth its cost; it is not
measuring whether the *steering* is doing the work, and after this leg I think that is the more
interesting question.

---

## 2026-09-09 00:33 — ui/004 a cap kept on purpose, a number I refused to believe, and a reviewer that reran the experiment

**Decided:** six.

**(1) The 250,000-row view cap is now a measured decision instead of an inherited one, and the
outcome is that it does not move.** `embarch-ui/open.md` had said for weeks that the cap "is now the
only term left, and the reason it was set is gone", and that any change to it *"should be made
against a measurement at the new number rather than by extrapolating this one"*. The unit built
`scratch_view::synth_capture` — an in-memory CSV shaped like the committed
`outpost-native-sim-stamped` fixture — and an `#[ignore]`d `measure_the_row_cap_at_scale`, run by
`cargo test --release measure_the_row_cap_at_scale -- --ignored --nocapture`, needing no file on
disk. Measured, release build:

| rows | decode | view JSON | `/bins` JSON @ width 1170 |
|---|---|---|---|
| 250,000 | 257 ms | 4.48 MB | 165 KB |
| 500,000 | 604 ms | 9.03 MB | 180 KB |
| 1,000,000 | 1.69 s | 18.1 MB | **1.5 KB** |

**Cap kept at 250,000, with the measurement as the stated reason** — which the task named as a
complete and legitimate outcome, and which is the honest one: decode time and resident view JSON
both grow somewhat worse than linearly, so the cost of raising it is server time and memory.

**(2) That 1.5 KB is the number the whole table rests on and I did not believe it.** A `/bins`
payload that *drops two orders of magnitude* between 500k and 1M rows is exactly what an
off-by-one, an early return, an empty-result path, or a synthesiser that goes degenerate at scale
looks like — and if the synthesiser's rows collapse at 1M then that entire row of the table measures
the harness rather than the viewer. **So I told the reviewer that in as many words and asked it to
settle whether the number is a property of the data or an artifact.** It **re-ran the measurement
itself and reproduced 165 KB / 180 KB / 1.5 KB exactly**, then traced the cause: at 1M rows the
density passes the `below_resolution` merge threshold and each lane collapses to a single run,
while the sparser IRQ lanes do *not* collapse — which is the merge property working, not a bug.
**This is the strongest thing a reviewer has done in this log**: it did not read the code and agree,
it reproduced the experiment.

**(3) So decision 18 holds much further out than it was ever tested, and that is the reusable
finding.** `decisions/trace-transfer.md` 18 says the payload no longer tracks dataset size; the
measurement shows it flat-to-*shrinking* across a 4× row increase. **The cost of raising the cap is
not what reaches the browser** — it is decode time and server memory, and those are the two terms a
future argument about the cap has to be about.

**(4) The refactor was the only part that could have broken the shipped product, and it is
clean.** `parse()` was split into a thin wrapper over a new `parse_with_cap(..., cap: usize)` so the
cap could be a parameter. The reviewer confirmed **`parse_with_cap` is test-only and production
still goes through `parse()` at `MAX_ROWS = 250_000`** — a measurement unit that silently changed the
product's row cap would have been a very quiet defect.

**(5) The `open.md` rewrite was checked for what it dropped, not just what it added.** That bullet
was the *source* this task was filed from, so a rewrite could easily have answered one question and
deleted another. The reviewer confirmed the rewrite is complete and honest, that decisions 18 and 21
are correctly distinguished in it, and that what remains open is genuinely what the worker said
remains open: whether **1.69 s** of decode is acceptable against the `/study/{id}/streams`
request-path budget, which nobody has measured. That is a better-stated open question than the one it
replaced.

**(6) I corrected `tasks/ui/021-compact-ui.md` from `open` to `blocked`, which is the fourth
instance in two legs of the class `tasks/doc/028` was filed for two units ago.** The worker's
`open.md` edit spent the file's reserve — 3,630 → **4,191 B** against `DOC-BUDGET.md`'s 3,920 B
`RESERVE_FLOOR`, still 929 B under the 5,120 B cap — and it correctly filed the debt in the same
commit, with a genuinely good `In flux:` block arguing bullet by bullet that the file is in flux and
a `Must not delete:` list that **already warns off all nine measured numbers** (the reviewer checked
that, since a compaction pass shaving them out would undo this whole unit). But `.claude/leg.md` is
explicit that `In flux: yes` means `blocked` and must name what unparks it, and an `open` one means
the filer got it wrong — so this was a wrong state field, not a different judgement. Unparks on
`tasks/ui/007` landing, or on a later reading that finds the other bullets settled. **Note the
percentage display is misleading here and cost me a minute**: `--pressure` prints this file at
**81.9%** while counting it as in reserve, because the reserve line is a byte floor rather than a
percentage of the cap. A supervisor who trusts the percentage column concludes the worker filed a
debt that did not exist.

**Merged:** `agent/ui/004-measure-the-row-cap` (code **`442b98a`** in `embarch-ui`, one file
`src/trace.rs` +162/−2; doc **`f1a14e1`**). Doc branch rebased over `outpost/005`'s fold, then a
fast-forward. Gate re-run by me on the merge result: `cargo build`, `cargo test` (**101 passed, 0
failed, 3 ignored** plus 2 in the second suite — the new measurement is one of the ignored, by
design), `cargo clippy --all-targets -- -D warnings` clean (the worker fixed one
`manual_is_multiple_of` hit); `python3 scripts/check-docs.py` **all 10 green**;
`check-ownership.py --scope ui` green (4 doc paths, base `6618e5129ab5`);
`check-client-names.py --repo embarch-ui` clean. **No native Windows build** — standing debt, and
this unit is a host-side test.

**Blocked:** nothing. `tasks/ui/021-compact-ui.md` was *filed* blocked by me, which is a park rather
than a blocked unit.

**Reviewer:** no findings.

**Hardware debts:** **none new.** All standing debts unchanged from this leg's earlier entries,
including the `cross_decoder.py`-skips-in-every-worktree gate debt recorded under `outpost/005`.

**Budget:** `PROCEED` / **BURNDOWN** — 5-hour **29.2% → 30.8%**, weekly **94.5% → 94.8%**, against a
97% cap, weekly resetting in 6h27m. Suggested wave **12**, 4 dispatched. **No 429**; the mode stands.

**Least sure about:** **that the 1M-row figure will be misread by whoever reads it next, despite
being correct.** "The payload gets *smaller* at 1M rows" is true, reproduced twice, and explained —
and it is also a sentence that sounds like good news about raising the cap, when the actual finding
is that the two costs which *do* grow are the ones nobody has budgeted. The `open.md` bullet says
this properly. The one-line changelog entry and this table do not, and the table is what someone
will quote.

---

## 2026-09-09 00:28 — outpost/005 an invariant the docs asserted and the reference decoder never implemented, and the first visible cost of the no-new-decisions rule

**Decided:** six.

**(1) `spec.md:61`'s invariant is now implemented by the one tool an engineer runs by hand.** That
line says *"A join that cannot be verified stamps nothing"* and explains why — a trace shifted by
three frames is readable, wrong, and indistinguishable from a correct one. `scripts/decode_outpost.py`
read columns 0 and 1 out of the arrival CSV, dropped `frame_bytes` on the floor, and stamped
whatever the row said. It now counts each frame's actual delimiter-separated chunk length **the same
way `decode_stream` counts `frame_index`** — every non-empty chunk, before COBS and CRC checks, so a
bad-CRC frame still occupies its index, which is the detail that makes the comparison meaningful
rather than off by however many frames were corrupt — and on the first disagreement leaves
`rx_utc_ms` empty for the **whole** capture with a stderr line naming the diverging index.

**(2) The default changed, so I had the reviewer measure the blast radius rather than reason about
it.** It grepped every mention of `rx_utc_ms` suite-wide and confirmed **no other document promises
a stamped `rx_utc_ms` unconditionally**, which is why this unit correctly wrote no `status.d/`
fragment — the absence of one would itself have been the finding if any suite-level claim had been
made false. It also confirmed the degrade path is real and tested, not merely documented: an older
**two-column** arrival CSV — the shape that exists in the wild — still decodes, still stamps, and
says on stderr that it did so unverified.

**(3) The reviewer found the thing I asked it to look for, and it is the first visible cost of this
leg's own constraint.** I told it plainly that "an existing decision covers it" is exactly the
attractive reading when a leg forbids new decisions, and to say so if the coverage was convenient
rather than genuine. It was convenient. **`decisions/clocks.md` decision 18 covers the
verify-then-refuse mechanism completely** — keying by frame index, checking claimed against actual,
*"when neither fits, nothing is stamped and the stream index says why"* — and says nothing about an
operator override that stamps anyway after verification has failed. The new
`--allow-unverified-join` is a design choice about this project's safety posture, and it landed in
`spec.md` prose, `README.md` and a changelog fragment with no numbered decision anywhere.

**(4) The reviewer then did the thing that makes a finding useful instead of merely correct: it
checked whether the practice was already established, and found the sibling.**
`--allow-build-id-mismatch` — decision 9's analogue in `decisions/manifest.md` — has the **identical
gap**, and decision 9 likewise states its refusal with no carve-out while `spec.md:60` repeats it.
So this is one posture recorded nowhere, twice, not one unit's slip. **I filed both in a single
task**, `tasks/outpost/015`, precisely so nobody fixes them one at a time and leaves the suite with
two overrides recorded two different ways — which is the defect `outpost/009` spent a whole unit
undoing yesterday. The drop is drained.

**(5) Nothing on disk needed correcting, and I checked that rather than assuming it.** The
inaccurate claim — "decision 18 already covers the design" — was in the worker's **commit message**,
which is not a document anyone reads for truth. `spec.md:61` as landed says the flag "stamps anyway,
mirroring `--allow-build-id-mismatch`'s posture toward decision 9", which *describes* the gap
instead of papering over it. So `outpost/015` says in as many words: something needs adding, nothing
needs correcting, and do not "fix" `spec.md:61` by deleting that clause.

**(6) The worker left its completed task file at `State: claimed`, which is the third instance of
that failure in two legs, so I have filed the class.** Leg 057 hit it twice, fixed both by hand,
filed nothing, and wrote in its own closing line that *if a later leg meets any of these again, the
honest reading is that it under-filed* and the right move is one task naming the whole class. This
leg met it inside forty minutes. `tasks/doc/028` is that task, `Owner: required` because every
plausible fix is a reserved path — a checker in `scripts/`, the worker contract in `.claude/`, or
`leg.md` itself. **The failure with teeth is not the tidiness**: a task left `claimed` after a leg
dies is indistinguishable from a live claim, recovery correctly reclaims it to `open`, and the next
leg re-dispatches a unit that already landed. The task names the cheapest fix as
`fold-commit.py` refusing a fold whose unit is not in a terminal state, since that is the moment the
truth is known and that script already refuses two other things.

**(7) This unit's fold landed in two commits, for the second time in two legs, and the cause is now
clearly a pattern rather than an accident.** `fold-commit.py` committed the log (`85784fe`) and then
refused its own `git rm` of the retired task file, because that file carried **my own unstaged
correction** — the `State: claimed` → `done` fix from (6). Leg 057 hit the identical refusal on
`api/034` for the identical reason: a supervisor that corrects a task file's state at the fold
leaves that file dirty, and the fold then cannot retire it. I finished the instance half by hand as
**`6618e51`** with the paths exactly matching `fold-commit.py`'s `--path` list and the reason in the
commit message, then re-ran the gate green. **This is a second argument for `tasks/doc/028`'s
option 1** and it points at a cheaper variant: whatever refuses a non-terminal state at the fold
should also stage the correction, because the two failures are the same edit seen from either side.
This note was appended to the entry after the log commit, so the log carries a small follow-up
commit rather than a single one.

**Merged:** `agent/outpost/005-verify-the-arrival-join` (code **`81cbba2`** in `embarch-outpost`;
doc **`dab753a`**, **fold `6618e51`, log `85784fe`** — two commits, see (7)). Doc branch rebased over `api/033`'s fold, then a fast-forward. **No Rust
anywhere in `embarch-outpost`** — it is a Zephyr module plus pure Python — so the gate is the Python
suites and the doc wrapper: `tests/decoder_unit.py` **29 tests, all pass** (9 new, covering match,
divergence, the escape hatch, missing column and short column, plus the two new helpers directly);
`tests/cross_decoder.py` **PASS on all 831 rows of 41 frames**, header line included. **That second
one matters more than its one line suggests**: it *SKIPs* in a worker's worktree, because the
sibling repos it cross-checks against are not checked out beside it, so the worker could only re-run
its logic by hand — **I ran it in the main checkout after the merge, where it genuinely passes.** A
gate that skips looks exactly like a gate that passes, and this one skips in every worktree the
fleet creates. `python3 scripts/check-docs.py` **all 10 green**; `check-ownership.py --scope
outpost` green (5 paths, base `9640260e2378`); `check-client-names.py --repo embarch-outpost` clean.

**Blocked:** nothing.

**Reviewer:** 1 finding — inbox/outpost-decision-18-escape-hatch-gap.md
Drained into `tasks/outpost/015` and deleted, so it is gone from `inbox/`; its substance is in that
task, widened to cover `--allow-build-id-mismatch` as well, which is the half the reviewer found on
its own initiative.

**Hardware debts:** **none new**, and one existing debt got worse in a way worth naming: the fleet
still cannot build `embarch-outpost`'s Zephyr `tests/unit` here, and this unit adds host-side Python
tests that do not touch that gap. `cross_decoder.py` skipping in every fleet worktree is a **gate**
debt rather than a hardware one, recorded above. All other standing debts unchanged from this leg's
first entry: the native Windows build of `embarch-core` (`core/028`, `core/015`, `core/010`);
`umbrella/037`'s corrected check 13 has never met the bench; `embarch-dev-bench`'s west/Zephyr
toolchain is absent; the four DUT-gated bench tasks; `core/028`'s `[assumed]` ESP32-C5
USB-enumeration fact; `dev-bench/002`'s 17-to-64-step study.

**Budget:** `PROCEED` / **BURNDOWN** — 5-hour **27.7% → 29.2%**, weekly **94.2% → 94.5%**, against a
97% cap, weekly resetting in 6h31m. Suggested wave **12**, 4 dispatched. **No 429**; the mode stands.

**Least sure about:** **whether `tasks/outpost/015` should have been a decision I wrote myself
instead.** I am a full delegate for design, including suite-wide, and the only thing stopping me was
this leg's burndown guardrail — which is a rule about *volume optimisation*, not about my authority,
and the reviewer had just handed me a clean statement of the posture and both its instances. I
followed the guardrail because a mode that lets its own occupant decide when the guardrail does not
apply has no guardrail, and because the sibling flag means this was never a same-day emergency. But
the outcome is that a design choice landed in prose tonight and its record waits for an attended
leg, and someone reading `spec.md:61` in the meantime is reading an honest sentence about an
undecided thing.

---

## 2026-09-09 00:23 — api/033 a guard hole closed by narrowing the claim rather than widening it, and a fourth wording I chose not to write

**Decided:** five. **This is leg 058's first unit. The leg is in burndown; the latch stands and
expires on its own at 06:59.**

**(1) The bypass is closed, and the interesting half is that the doc claim got *smaller*.**
`crates/embarch-core-client/src/version.rs`'s `reject_tree_mutating_command` returned `Ok(())` for
any program whose file stem was not `git`, so `version_command = ["bash","-lc","git checkout main
&& git describe"]` walked straight through a guard whose whole job is that somebody's uncommitted
work survives a version derivation. It now flattens a wrapper's argv when the program is one of
`sh`/`bash`/`zsh`/`dash`/`env`/`cmd`/`powershell`/`pwsh` — splitting a `-c`/`-lc` script string
word by word — and refuses on a visible `git` token alongside a mutating-subcommand token.
**`spec.md` §2 used to say "This crate never runs `git checkout`. … Enforced against the config
file too"; it now says the crate never *knowingly* runs a tree-mutating `git` subcommand, "named
directly or behind a shell/exec wrapper", and names what is still out of reach** — an opaque program
of the config's own (`./scripts/version.sh clean`) never shows this rule a `git` token to notice,
because it reads argv and not a script's contents. That is a weaker claim than the one that shipped
before, and it is the first one that is true.

**(2) All three copies of the rule were checked against each other, wording for wording, because
this suite has now paid twice for the alternative.** `decisions/studies.md` decision 40 mirrors
`spec.md` §2 by design — the decision file says so explicitly — so the worker updated both, and I
had the reviewer verify that the two say the same thing rather than becoming a third variant. It
did, and also confirmed the pre-existing test `src/reflash.rs`'s `the_reflash_path_never_moves_the_tree`
now asserts the wrapper case as well as the bare one.

**(3) I deliberately left a fourth occurrence alone, and this is the judgement in this unit most
worth disagreeing with.** The reviewer found `embarch-api/interfaces/studies.md:11` still carrying
the flat phrase "building the tree **as it stands** — never `git checkout`", untouched by the diff,
and correctly did not file it. **I read it, and it is describing a different thing:** that sentence
is about what `run_study`'s `reflash` parameter does, and reflash genuinely never runs `git
checkout` — it is not making the *coverage* claim about `version_command` that this unit had to
narrow. So editing it would have produced a fourth wording of a rule whose other three copies now
agree, which is exactly the defect `outpost/009` spent a unit undoing yesterday. **Left as is, and
recorded here rather than in a task**, because filing it would ask a future worker to change a true
sentence.

**(4) The over-rejection is real and I checked it against this repo's own blessed config shape
before landing.** The guard now refuses a `git` token plus any mutating-subcommand token anywhere
in a flattened wrapper argv, and `config.example.toml` and `interfaces/config.md` both bless
`["bash","-lc","…"]` as a normal shape — so a false positive here is somebody's working config
breaking, not a hypothetical. The reviewer confirmed the guard applies only to `version_command`
and not to `build_command`, where the blessed shell-wrapper shape actually lives, and that a
read-only `bash -lc "git describe --always --dirty"` still passes (there is a test pinning exactly
that). The posture is unchanged and deliberate: a false positive costs renaming an argument.

**(5) The `embarch-api` reserve was respected, for the second leg running, by the same cheap
intervention.** That sub-project has five files inside the last 10% of their caps and every one is
filed against a **blocked** compaction task a worker may not do — `decisions/tool-wrapping.md` at
**66 B**, `decisions/core-link.md` 212 B, `open.md` 318 B, `spec.md` 890 B, `decisions/build.md`
1,154 B. I put that table in the task file before dispatch, said which single file the edit belonged
in, and said in as many words that the "update spec.md/decisions.md/open.md" line in its own
Done-when was boilerplate rather than a checklist. **It touched `spec.md` and `decisions/studies.md`
and nothing else**, and both edits were replacements rather than additions, so no api file moved
into or deeper into reserve. Naming the byte counts in the task file is the whole trick and it has
now worked twice.

**(6) Two pieces of leg bookkeeping landed in this commit and the next leg should know where they
went.** `2026-09-08` is folded — **32 unit entries into one dated entry**, done by an
`embarch-log-folder` subagent so the day never entered my context, keeping 94 SHAs, 34 reviewer
lines and all 30 debt-carrying lines. That took the log 288,181 B → 131,104 B, still over the 40 KB
line, so `fold-day.py --roll` moved `2026-09-07` (61,917 B) into
`log-archive/supervisor-log-2026-09-07-to-2026-09-07.md` and the log is now **68,931 B and at its
floor** — the two newest days always stay, so nothing more can roll until `2026-09-09` is over.
**`fold-commit.py` stages only `supervisor-log.md` on the fleet side**, so I staged the new archive
file by hand before folding; a future leg that rolls a day must do the same or the archive is
written and never committed.

**Merged:** `agent/api/033-shell-wrapper-git-guard` (code **`a5ade7a`** in `embarch-api`; doc
**`b8706f7`**). Both fast-forwards; `embarch-api`'s local `main` needed a `--ff-only` to
`origin/main` first, the same staleness leg 057 recorded twice. **I read the code diff before
merging** rather than merging on green, because it touches `embarch-core-client`, which §10 names as
a shared crate. Gate re-run by me on the merge result: `cargo build`, `cargo test` (**40 passed, 0
failed**, including two new tests pinning the wrapper refusals and one pinning that a read behind a
wrapper still passes), `cargo clippy --all-targets -- -D warnings` clean; `python3
scripts/check-docs.py` **all 10 green**; `check-ownership.py --scope api` green on the doc branch (4
paths, base `61afb1ce7d9c`) and the code repo is whole-tree owned;
`check-client-names.py --repo embarch-api` clean against 7 denylist entries. **No native Windows
build** — that debt is standing, the fleet cannot pay it, and this unit is host-side Rust in a crate
Core does not link.

**Blocked:** nothing.

**Reviewer:** no findings.

**Hardware debts:** **none new.** This unit touched no hardware and could not. Standing debts
carried forward unchanged: a native Windows build of `embarch-core` is owed and the fleet cannot run
one (`core/028`, `core/015`, `core/010`); `umbrella/037`'s corrected check 13 has never met the
bench; `embarch-outpost`'s Zephyr `tests/unit` cannot be built here; `embarch-dev-bench`'s
west/Zephyr toolchain is likewise absent; the four DUT-gated bench tasks are unchanged; `core/028`'s
`[assumed]` ESP32-C5 USB-enumeration fact still needs one look at one board; `dev-bench/002`'s
17-to-64-step study has never been attempted on the bench.

**Budget:** `PROCEED` / **BURNDOWN** — 5-hour **23.2% → 27.7%**, weekly **93.3% → 94.2%**, both
against a 97% cap, weekly resetting in 6h36m. Suggested wave **12**; I dispatched **4**
simultaneously, which is the leg's unit cap and therefore the binding constraint, not the wave.
**No 429**, so the mode stands.

**Least sure about:** **that `queue-status.py --refill-owed` is permanently unsatisfiable in
burndown, and that I skipped the sweep on that reading.** It reported refill owed because the
dispatchable tasks span **9 distinct scopes against a wave of 12** — but 9 *is* the whole suite,
so no sweep can ever widen it, and with 46 tasks dispatchable a sweep would have bought nothing but
tokens. I am confident the reading is right and much less confident that skipping was, because the
rule that gate replaced was skipping-when-not-empty and it was changed on measured evidence of
starvation. **The honest framing is that the second half of that gate compares a suite-wide constant
against a mode-dependent variable, and in burndown the variable exceeds the constant by
construction.** I have not filed it: it is one leg's observation, `scripts/` is the owner's, and
leg 057's closing worry was already that it had handed him three `Owner: required` items in a
single leg. If a later burndown leg meets it again, that is two, and it should be filed.

---

## 2026-09-09 00:01 — api/034 a doc premise that finally has a test, and two paid ledger items nobody was closing

**Decided:** five. **This is leg 057's fourth and last unit; the leg ends here at its cap, not on a
fault, a stop or a budget verdict. The burndown latch stands and expires on its own at 06:59.**

**(1) `interfaces/tools.md:5`'s premise is now checked instead of asserted.** That file opens by
saying "one table, because these are two front-ends over one implementation — not two surfaces to
keep in sync", and nothing had ever tested it. `embarch-api/tests/tool_subcommand_parity.rs` (188
lines) now derives the MCP tool list from `include_str!("../src/tools.rs")` and the subcommand list
from `include_str!("../src/main.rs")` and asserts one-for-one kebab-case correspondence. The missing
`reset_dev_bench` row — the defect that prompted the task, and a command `suite/studies-guide.md`
already tells an engineer to run — is in the table.

**(2) The test asserts a superset, not a bijection, which is the distinction I asked the reviewer to
check and the one that would have made it wrong.** `spec.md` §1 claims the CLI is a *superset* with
`versions` having no tool. A test asserting a strict bijection would be asserting something the docs
do not, and would fail the first legitimate CLI-only subcommand. The reviewer counted the actual
source at the merge SHA — **24 `#[tool]` functions, 24 `Commands` variants** — and confirmed the only
two mismatches are the two the named `DOCUMENTED_ASYMMETRIES` constant encodes: `versions` as
`CliOnly`, `study_watch` as `ToolReachedAs("study-status")` because it is a `--follow` flag rather
than its own variant. Both verified in `cli.rs`. **So the constant is exhaustive today, not merely
plausible.**

**(3) The parser's weak point was guarded rather than hoped away, and that is worth recording
because it is the failure mode this kind of test usually has.** It ties itself to the
`#[tool(description = ...)]`-immediately-precedes-`async fn` adjacency, and **a parity test that
quietly stops seeing half the surface is worse than no test.** The reviewer checked all 24 sites hold
that adjacency today, and — the part that matters — the file carries an `assert!(tools.len() > 20)`
tripwire with a matching variant-count guard, so a formatting change that broke the adjacency
collapses the count and **trips**, rather than passing with three tools. The worker also verified the
test catches real drift by temporarily renaming an exception entry and confirming the failure
message.

**(4) The api reserve was respected exactly, which is the first time a unit dispatched into
`embarch-api` has managed that without spending it.** That sub-project is the tightest in the suite —
`decisions/tool-wrapping.md` has **66 B** of headroom, `core-link.md` 212 B, `open.md` 318 B,
`spec.md` 890 B, all five behind `blocked` compaction tasks a worker may not do. I put the table of
those five files and their headroom in the task file before dispatch, told the worker
`interfaces/tools.md` was where its edit belonged, and told it explicitly that the
"update spec.md/decisions.md/open.md" line in its own Done-when was boilerplate rather than a
checklist. **It touched none of the five**, and the reviewer confirmed that against `git show
--stat`. The cheap intervention was naming the byte counts in the task file rather than leaving the
worker to discover them.

**(5) I closed two paid size-ledger items that had been nagging with nobody closing them, and one of
them is a park that had quietly stopped meaning anything.** `check-doc-size.py --pressure` prints
`PAID … close its item` for a file that is out of reserve while its task still claims it:
- `tasks/api/043-compact-api.md` was `blocked` on `In flux: yes` for `decisions/surface.md`, which
  `api/036`'s verbatim split took to **5,609 B against a 12,288 B cap (45.6%)**. Its last open
  checkbox was "every `Must not delete:` item is still readable, wherever it ends up", and I
  **verified all three at their new addresses myself** rather than ticking it on the note's word:
  decision 41's routine-knob-versus-unrecoverable-`erase` distinction and decision 52's two rejected
  alternatives plus the `host_type_schema_version`/`schema_version` collision are in
  `decisions/tool-wrapping.md`; decision 57's four-bare/one-wrong-number finding is still in
  `surface.md`. Closed `done`. **The park's question moved rather than went away** —
  `tool-wrapping.md` is the file that now takes every per-tool addition, it is the 66 B file, and
  `tasks/api/047` is where a future unit says `In flux: no`.
- `tasks/dev-bench/012`'s `decisions/ble.md` item is paid (**7,902 B, 64.3%**) and is now struck off
  its `Compacts:` line, with a note that the task's two remaining items — `spec.md` 92.4% and
  `open.md` 93.4% — were added by the 2026-09-07 reserve-floor change and are **not** covered by that
  task's `In flux: yes` block, which is about `ble.md`. Same shape as leg 056's `study-designer/006`
  correction, and the third time this leg has found a task-file state field that no script verifies.

**(6) This unit's fold landed in two commits and the log entry is the older half, which the next leg
should know how to read.** `fold-commit.py` committed this entry (`00b0cf6`) and then **failed
before staging the instance side**, for two reasons at once: `check-doc-size.py` went red because
the note I had written onto `tasks/dev-bench/012`'s `**Compacts:**` line struck the paid path through
with `~~…~~` and prose, and **the parser stopped recognising the line at all** — so the two paths
that genuinely remain were reported as *in reserve with no debt filed*; and its `git rm` of the
now-`done` `tasks/api/043` refused because that file had unstaged edits. **That is precisely the
ordering `fold-commit.py` is built to leave** — "an entry for a fold that did not happen", never "a
fold nobody logged" — and it is the first time this log has recorded the recovery actually being
used. I fixed the `Compacts:` line (the paid path is *removed* from it and the explanation moved to
prose below it, because **that line is data**), re-ran the gate green, and committed the instance
side by hand as `0ea2f63`, saying so in the commit message. `fold-commit.py` correctly refused a
second run rather than double-committing.

**Merged:** `agent/api/034-tools-md-reset-dev-bench` (code **`0e6bb51`** in `embarch-api`, one new
test file; doc **`8897efa`**; **fold `0ea2f63`, log `00b0cf6`** — two commits, see (6)). Doc branch rebased over `ui/011`'s fold, then a fast-forward. **The
code merge traversed two commits already on `origin/main`** — `embarch-api`'s *local* `main` was
behind, the same staleness that made a `git branch -d` refuse in this leg's first entry — so the
`3 files changed` git printed is misleading; `git log a0950ec..HEAD` is the single new commit and I
checked it. Gate re-run by me on the merge result: `cargo build`, `cargo test` (**all suites green,
including the new one**), `cargo clippy --all-targets -- -D warnings` clean;
`python3 scripts/check-docs.py` **all 10 green**; `check-ownership.py --scope api` green on both
branches (3 doc paths, base `3125b83b4a14`; code repo whole-tree owned);
`check-client-names.py --repo embarch-api` clean. **No native Windows build** — that debt is
standing and the fleet cannot pay it, and this unit adds a test rather than platform code.

**Blocked:** nothing. Four units dispatched, **four landed, none blocked** — this leg's only red was
a reviewer finding on `ui/011`, fixed in its own fold.

**Reviewer:** no findings.

**Hardware debts:** **none new.** No unit this leg touched hardware. Standing debts, carried forward
in full: a native Windows build of `embarch-core` is owed and the fleet cannot run one (`core/028`,
`core/015`, `core/010`); `umbrella/037`'s corrected check 13 has never met the bench;
`embarch-outpost`'s Zephyr `tests/unit` cannot be built here, which `outpost/009` met again;
`embarch-dev-bench`'s west/Zephyr toolchain is likewise absent; the four DUT-gated bench tasks are
unchanged; `core/028`'s `[assumed]` ESP32-C5 USB-enumeration fact still needs one look at one board;
`dev-bench/002`'s 17-to-64-step study has never been attempted on the bench.

**Budget:** `PROCEED` / **BURNDOWN** at start and end — 5-hour **17.1% → 22.4%**, weekly **92.1% →
93.2%**, both against a 97% cap, weekly resetting in 6h58m. Suggested wave **12** throughout, and I
used **4**, dispatched simultaneously. **No 429 at any point**, so the mode is not cleared and the
latch stands. **46 tasks dispatchable** as this leg ends, down from 52.

**Least sure about:** **that the fleet is now finding structural defects faster than it can file
them, and that I chose not to file three of them.** This leg found four things no script checks: an
`In flux: yes` task sitting `open` (twice), a completed task left at `State: claimed` (twice), a paid
ledger item nobody was closing (twice), and a squeeze that lost an invariant while honestly believing
it was texture (once, and that one *is* filed, into `tasks/doc/026`). Every one of the first three is
the same class — **a task file's state is written by hand and verified by nobody** — and I fixed each
instance and filed none of them, on the reasoning that one leg's observation is not a finding. But
six instances in one leg is not one observation, and the reason I did not file is partly that leg
056's own closing worry was that it had handed the owner three `Owner: required` items in a single
leg. **If a later leg meets any of these again, the honest reading is that I under-filed to avoid
adding to a queue the fleet has one pair of hands for**, and the right move is a single task naming
the whole class rather than three narrow ones.

---

## 2026-09-08 — 32 units

*Folded by a supervisor leg (`embarch-log-folder`) on 2026-09-09, per protocol.md §11. Dropped:
the per-unit narrative reasoning behind each accepted judgement, and every "least sure about"
self-critique — git and the day's own commits hold the diffs, and each unit's own entry (now in
`log-archive/` after the next roll) holds the argument if anyone wants it. Kept below: every SHA,
every `**Reviewer:**` line, every `**Hardware debts:**` line that names a board or a standing
hardware debt, and — first, out of ledger order — the handful of things the day decided on the
owner's behalf, left mid-flight, or found recurring, which is what a leg picking up tomorrow
actually needs.*

### What the next leg cannot recover from git alone

- **Three `Owner: required` doc tasks were filed today, on top of one closed by the owner mid-day
  (`doc/025`):** `tasks/doc/026` (a squeeze's own description of its cuts is never complete — three
  proposed fixes, no preference smuggled in), `tasks/doc/027` (`check-decision-refs.py` needs to
  resolve a decision-link *href* against the file it names, not just the number — full spec
  written), and `inbox/worker-inbox-drops-land-in-a-worktree-that-is-deleted.md` /
  `tasks/doc/025-worker-inbox-drops-land-in-a-deleted-worktree.md` (a worker's `inbox/` drop dies
  with its worktree unless a supervisor happens to go looking). A supervisor flagged that filing
  three reserved-path items in one day may be a rate problem rather than three individually
  justified ones.
- **`ui/011`'s fold landed `embarch-ui/decisions/study-designer.md` at 11,007 B against an 11,059 B
  reserve line — 53 bytes of clearance, deliberately not trimmed further.** Expect
  `check-doc-size.py` to re-file this one immediately.
- **Two workers left their task file at `State: claimed` after finishing** (`topology/021`,
  `outpost/009`) — both would have been indistinguishable from an abandoned claim under a dead
  supervisor. No mechanism checks this; a third instance is the finding worth filing.
- **A second push after a first was already landed** (`outpost/012`) stranded finished work on a
  live branch past its own fold; caught only by an end-of-leg remote sweep, not by anything
  mechanical. Third time this shape has occurred (after legs 035, 055).
- **33 stale local `agent/*` branches** (all already on `origin/main`) were deleted suite-wide with
  `git branch -d` to unblock a deferred framework deploy pinned at `9acf44a93b`; one
  (`embarch-study-designer`'s `agent/study-designer/019-...`) refused because that repo's local
  `main` is stale, a false positive. `fold-commit.py` prunes the *remote* branch on landing but
  never the local copy — nine legs' worth had accumulated.
- **Two `In flux: yes` tasks were found sitting `open`** (`umbrella/038`, `dev-bench/014`) and moved
  to `blocked`; conversely `study-designer/006` was correctly unparked because its flux condition
  (the `crate.md` FFI content) had been paid. Nothing checks that `In flux: yes` implies `blocked`.
- **`api/030`'s UTF-8 fix left a design amendment sitting in the wrong decision** on purpose —
  burndown forbids authoring a new one — and the reviewer's finding was deliberately left in
  `inbox/api-030-review-finding.md` rather than fixed, for a later non-burndown leg to file as its
  own numbered decision in `embarch-api/decisions/build.md`.
- **Reserve-driven placement recurred all day**: decisions were routed away from full files
  (`tool-wrapping.md` at 66 B, `ble.md` at 6 B of headroom) toward the file with room, each time with
  the argument written into the task *before* dispatch rather than found afterward to agree with the
  byte count — a pattern now logged across several consecutive legs and still unresolved as a rule.
- **`check-decision-refs.py`/`check-links.py` blind spots hit three times today**: a citation that
  *resolves* to the wrong file inside a sub-project (`umbrella/042`, `api/048`'s
  `study-events.md`→`surface.md`), and a decision citing a transient `status.d/` fragment filename
  that the very fold consuming it deletes. None of this is fixed — `scripts/` is the owner's.
  `suite/021`'s own unit hit the same class again re-titling stale CI decisions.
- **`embarch-dev-bench/decisions/ble.md` was split** (`dev-bench/012`) after being found at *six
  bytes* of headroom — the tightest file in the suite — dispatched as a split-only exception to an
  `In flux: yes` compaction task, on the reading that a verbatim split restates nothing so the bar
  doesn't apply to it. Not settled as a rule; flagged for the owner or `.claude/leg.md`.
  `embarch-dev-bench/open.md` (338 B left) and `spec.md` (780 B left) remain `In flux: yes` squeezes
  on the same task, unresolved.
- **A `suite`-scope unit (`suite/021`) exposed that `embarch-dev-bench` and `embarch-outpost` have no
  CI and no `Cargo.toml`**, so the fleet's own merge gate cannot reach either repo at all — a change
  there is checked by a human/agent diff-read and nothing else.
- **`fold-commit.py` has no clean path for a `suite` unit**: it `git rm`s a closed task file that
  always has local modifications (fails — remove it by hand first), commits the log before settling
  instance paths (a failure there leaves the log committed and the instance half not — recover by
  hand-committing the staged instance paths with the same message, do not write a second entry), and
  `--check` requires a merge SHA a `suite` unit never has (the fold commit itself, `ac20966`, is the
  only honest answer). None of this is fixed; it cost one leg three retries.
- **`umbrella/026` and `api/036` landed on `main` on 2026-09-07 under leg 047 and were never logged**
  — leg 047 was killed (`fleet stop` at 21:06) between merge and fold. Reconstructed today rather
  than re-run: `umbrella/026` — `embarch-umbrella` `95f2975`, `embarch-doc` `2156553`, merged
  `2b29d67`; `api/036` — `embarch-api` `95c1954`, `embarch-doc` `cf12cae` then `8005396`. These four
  SHAs existed nowhere but `git log` until this entry. Recorded as a reconstruction, not a review —
  nothing was re-gated.
- **A supervisor corrected worker prose at two folds and was wrong once** (`core/028`): a
  cross-repo relative doc link it added at the merge was the exact shape `decisions/platform.md`
  decision 46 already rejected; caught by the reviewer, fixed in `11f5dc3`. Lesson recorded: any
  supervisor correction at a fold now goes into the reviewer's prompt, not just the merge.
  Separately, `core/028` sharpened an `[assumed]` ESP32-C5 USB-enumeration hardware "fact" whose
  provenance was circular (two task files citing each other, neither a measurement) rather than
  letting it launder into a third document as settled.
- **Standing hardware debts carried across the whole day, repeated in nearly every unit's own
  `**Hardware debts:**` line below:** a native Windows build of `embarch-core` is owed and the
  fleet cannot run one (stacked behind `core/028`, `core/015`, `core/010`); `umbrella/037`'s
  corrected check 13 has never met the dev-bench board; `embarch-outpost`'s Zephyr `tests/unit`
  cannot be built here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own
  commit; the ESP32-C5 USB-enumeration fact tagged `[assumed]` needs one look at one board;
  `dev-bench/002`'s 17-to-64-step study has never been attempted on the bench, newly written down
  today as a real, unexercised silent-failure gap.

### Per-unit ledger

**ui/011** — reflash-selector squeeze cut the `allow_version_mismatch` override out of decision 11
entirely (a false statement about a live API), while `open.md`'s carry-forward of the same decision
still names it; also fixed `decisions.md`'s missing decision-22 routing row.
Merged: `agent/ui/011-compact-ui-study-designer-decisions` (code no commits, `embarch-ui` unchanged;
doc `f3054e1`, corrected in this fold). Ownership check base `0f58c163dd9b`.
**Reviewer:** 1 finding — inbox/ui-011-mismatch-override-dropped.md
**Hardware debts:** **none new.** All standing debts unchanged from this leg's first entry.

**outpost/009** — `src/outpost_priv.h`'s top comment wrongly said any wire-format change bumps
`OUTPOST_RECORD_LAYOUT_VERSION`; corrected to say only shape changes do, matching `interfaces/wire.md`
and the file's own lower block. Also: two workers in a row (this one and `topology/021`) left their
task file `State: claimed` after finishing.
Merged: `agent/outpost/009-outpost-priv-layout-version-comment` (code `dd8cb22`, doc `b841489`).
Ownership check base `df11eaa4f469`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** `embarch-outpost`'s Zephyr `tests/unit` still cannot be built
here. All other standing debts unchanged.

**topology/021** — `decisions/crate.md` split (93.4%→63.3%, `PAID`), decision 23 moved verbatim into
new `decisions/storage.md`, byte-diff confirmed by the reviewer. First unit of a leg that opened by
reclaiming 33 stale local `agent/*` branches suite-wide (see above) and correcting two
misclassified `In flux: yes` tasks to `blocked`.
Merged: `agent/topology/021-compact-topology` (code no commits, `embarch-topology` unchanged at
`b722895`; doc `8b0e87c`). Ownership check base `f80786a8b869`. Two `In flux: yes` tasks corrected
to `blocked` in commit `133076d`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** Standing debts carried forward unchanged from leg 056's last
entry: a native Windows build of `embarch-core` is owed and the fleet cannot run one (`core/028`,
`core/015`, `core/010`); `umbrella/037`'s corrected check 13 has never met the bench;
`embarch-outpost`'s Zephyr `tests/unit` cannot be built here; `embarch-dev-bench`'s west/Zephyr
toolchain is absent; the four DUT-gated bench tasks are unchanged; `core/028`'s `[assumed]`
ESP32-C5 USB-enumeration fact still needs one look at one board; `dev-bench/002`'s 17-to-64-step
study has never been attempted on the bench.

**outpost/012 (continuation)** — the same task's worker kept working after its first push was
landed; found alive with unlanded finished work at `ce98982` during an end-of-leg branch sweep,
landed as a second entry rather than folded silently into the first. `spec.md` 9,187→8,987 B
(87.8%), `decisions/transport.md` 7,114→6,978 B (85.2%), task fully closed.
Merged: `agent/outpost/012-compact-outpost` (code no commits, `embarch-outpost` unchanged at
`2f6aba3`; doc `0d4ae25`). Ownership check base `21e6b8a6620f`.
**Reviewer:** skipped (leg ending at its unit cap — a reviewer spawned here would outlive the leg).
**Hardware debts:** **none new.**

**doc/022** — task wanted a gate rule plus a corpus sweep so a decision-link can't survive a
mission split still naming the old topic file; both halves are outside a `doc` worker's or a
supervisor's write set (`scripts/`, `history/*.md` has no ownership-map row at all), so 22
hand-edited links were reverted without committing and the follow-up (`doc/027`) was filed instead.
Also corrected a landed sentence claiming `scripts/` is writable by "supervisor and owner" — it is
never/never/write for both.
Merged: `agent/doc/022-decision-link-mission-split` (code none; doc `553a582`). Ownership check base
`49702cb3a369`.
**Reviewer:** 1 finding — inbox/doc-022-review-scripts-ownership-misstatement.md
**Hardware debts:** **none new.** No unit this leg touched hardware; all four were doc-side.
Standing debts, carried forward in full: a native Windows build of `embarch-core` is owed and the
fleet cannot run one (`core/028`, `core/015`, `core/010`); `umbrella/037`'s corrected check 13 has
never met the bench; `embarch-outpost`'s Zephyr `tests/unit` cannot be built here, which `outpost/012`
met again; `embarch-dev-bench`'s west/Zephyr toolchain is likewise absent; the four DUT-gated bench
tasks are unchanged; `core/028`'s `[assumed]` ESP32-C5 USB-enumeration fact still needs one look at
one board; `dev-bench/002`'s 17-to-64-step study has never been attempted on the bench.

**study-designer/019** — `decisions/registry.md` squeezed 11,827→10,074 B (four decisions, one
mission, no seam); cut two sentences beyond its own commit message's description (a ranking claim
and a design maxim) — the second occurrence of an under-described squeeze this leg, which is what
turned the note into `tasks/doc/026`. `spec.md` gained two sentences on the registry, 9,136→9,600 B
(93.8%). Unparked `study-designer/006` as a state correction (its flux ended when `crate.md` was
paid).
Merged: `agent/study-designer/019-compact-study-designer` (code no commits, `embarch-study-designer`
unchanged; doc `f6c307b`). Ownership check base `9e70e5bea0b3`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** A doc compaction touches no hardware. Standing debts carry forward
unchanged from the entries below.

**topology/017** — `decisions/validation.md` split (decision 26 → new `decisions/validate-timing.md`,
91.0%→71.4%); `spec.md` squeezed 97.3%→87.8% (1,245 B left) — the first under-described squeeze this
leg, four named deletion categories verified but two further sentences and a caveat also went,
unnamed in the commit message. Task fully closed.
Merged: `agent/topology/017-compact-topology` (code no commits, `embarch-topology` unchanged at
`b722895`; doc `f7506fa`). Ownership check base `097e96a37e61`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** A doc compaction touches no hardware. Standing debts carry forward
unchanged from the entries below.

**outpost/012** — `decisions/module.md` split (decision 22 → new `decisions/testing.md`, byte-diff
verified) and `open.md` squeezed (four bullets deleted against named homes): 8,192→3,632 B (44.3%)
and 5,120→3,606 B (70.4%). Repointed all inbound references across both `embarch-doc` and
`embarch-outpost` (`README.md`, `tests/run-all.sh`, `tests/vocab_check.py`). Task left `open` (two
of four `Compacts:` files unpaid, crossed the reserve line on the 2026-09-07 rule change rather than
on an edit).
Merged: `agent/outpost/012-compact-outpost` (code `2f6aba3`, doc `a620d08`). Ownership check base
`b7a88e4243e2`. Recovery commit for a stale `State: claimed` on `ui/019` (landed at `412b541` last
leg) and the `doc/025` inbox drop, both `2abd45c`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** Standing debts carry forward unchanged from the entries below: a
native Windows build of `embarch-core` is owed and the fleet cannot run one; `umbrella/037`'s
corrected check 13 has never met the bench; `embarch-outpost`'s Zephyr `tests/unit` cannot be built
here, which this unit met again; `embarch-dev-bench`'s west/Zephyr toolchain is likewise absent; the
four DUT-gated bench tasks are unchanged; `core/028`'s `[assumed]` ESP32-C5 USB-enumeration fact
still needs one look at one board; `dev-bench/002`'s 17-to-64-step study has never been attempted.

**topology/014** — `open.md` delete pass (no split seam available): three of eleven open-question
bullets deleted, each verified against the decision or `spec.md` line it had quietly become a
duplicate of (decision 24, decision 21, `spec.md:103`). 5,016→3,669 B (98.0%→71.7%), out of reserve.
Merged: `agent/topology/014-compact-topology` (code no commits, `embarch-topology` unchanged at
`b722895`; doc `ec0e42f`). Ownership check base `10f2d37896e8`; diffed against pre-image `10f2d37`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** A doc compaction touches no hardware. Standing debts, unchanged and
carried forward in full: a native Windows build of `embarch-core` is owed and the fleet cannot run one
(`core/028`, `core/015`, `core/010`); `umbrella/037`'s corrected check 13 has never met the bench;
`embarch-outpost`'s Zephyr `tests/unit` cannot be built here (no `west`, no `ZEPHYR_BASE`);
`embarch-dev-bench`'s west/Zephyr toolchain is likewise absent, so `dev-bench/002` ran no firmware
test; the four DUT-gated bench tasks are unchanged; `core/028`'s `[assumed]` ESP32-C5
USB-enumeration fact still needs one look at one board; **new this leg**, `dev-bench/002` recorded
that a 17-to-64-step study is accepted by the host and unrunnable on the bench, and nobody has ever
tried one.

**dev-bench/002** — `decisions/link.md` decision 35 said the 16-step local cap was removed; firmware
(`app/src/serial_protocol.h:55,714`, both encode/decode refusal paths, a pinning ztest) proves it was
never built. Amended (not retired) as "not implemented as of 2026-09-08" with the live consequence:
crate cap is 64, bench cap is 16, so a 17–64-step study the host accepts is silently unrunnable on
this board. Pushed `decisions/link.md` to 91.5% (1,047 B left); filed `tasks/dev-bench/014`, `In
flux: yes`.
Merged: `agent/dev-bench/002-decision-35-step-cap` (code no commits, `embarch-dev-bench` unchanged;
doc `84243a3`). Ownership check base `412b541756cb`.
**Reviewer:** no findings.
**Hardware debts:** **one restated, none new.** The 17-to-64-step gap is a real bench fact that is
now written down and has never been exercised — a study with more than 16 steps has not been
attempted against this board, and doing so is what would confirm the failure is silent rather than a
clean refusal. That needs the bench and an attended leg; burndown forbids bench work outright. Prior
debts carry forward unchanged from the entries below.

**ui/019** — `decisions/trace-chart.md` split (decision 23 → new `decisions/outcome-decode.md`,
11,833→8,801 B, nothing deleted). Reviewer caught the split was not verbatim (a closing sentence
gained a link); reverted in the fold rather than softening the "verbatim" claim.
Merged: `agent/ui/019-compact-ui-trace-chart` (code no commits, `embarch-ui` unchanged at `34210c0`;
doc `0470b61`), plus this fold's own revert. Ownership check base `1638b96afd41`; decision 23 diffed
against its pre-move text at `1638b96`.
**Reviewer:** 1 finding — inbox/ui-019-verbatim-split-drift.md
**Hardware debts:** **none new.** A decisions-file split touches no hardware and needs none. All
prior debts carry forward unchanged from the entry below.

**outpost/013** — `README.md`'s Status section called measured instrumentation overhead
"deliberately uncharacterised" against a `spec.md` §4 measurement standing since 2026-08-27; restated
with the real figures (1.6% DUT CPU, misread as 78.1% on host clock). Fixed a broken relative link in
`tasks/api/051` (one `../` short) as the supervisor's own error. Flagged (not fixed — `scripts/` is
reserved) that `--refill-owed` fires unconditionally in burndown against only 10 dispatchable scopes,
making it unsatisfiable by construction at a wave of 12.
Merged: `agent/outpost/013-readme-overhead-status` (code `ea2273e`, doc `b13901f`). Ownership check
bases: doc `b4d8a7d9f64d`, code `9621112764f6`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** This unit asserts a hardware measurement but took none — it cites
one `spec.md` already carried. All prior debts carry forward unchanged: a native Windows build of
`embarch-core` is owed and the fleet cannot run one (`core/028`, `core/015`, `core/010`);
`umbrella/037`'s corrected check 13 has never met the bench; `embarch-outpost`'s Zephyr `tests/unit`
cannot be built here (no `west`, no `ZEPHYR_BASE`); the four DUT-gated bench tasks are unchanged; and
`core/028`'s `[assumed]` ESP32-C5 USB-enumeration fact still needs one look at one board.

**umbrella/025** — four user-visible strings (`doctor.rs` check 1/check 9, an `install.rs` marker
written into `~/.bashrc`, two `embarch.toml` init comments) named documents a four-file split had
deleted; repointed and all resolved verified by the reviewer against real files. `install.rs` gained
a `LEGACY_MARKER` constant, verified byte-identical to the prior value so an uninstall on a
pre-change machine still removes its own comment. Merge process note: `git merge --ff-only <worktree
path>` fails and `set -e` did not abort the script — merge by branch name and read the merge output,
not just the gate's.
Merged: `agent/umbrella/025-stale-doc-pointers` (code `db08b1e`, doc `01ecd2e`). Ownership check base
`13df60743463`.
**Reviewer:** no findings.
**Hardware debts:** **none new, and one deliberately not incurred.** This unit changes what `doctor`
and `install` print; exercised only via `cargo test`, never against the owner's real installation —
no `install`, no `uninstall`, no live `doctor`, no service operation, per burndown's ban on bench
work. All prior debts carry forward unchanged: a native Windows build of `embarch-core` is owed and
the fleet cannot run one (`core/028`, `core/015`, `core/010`); `umbrella/037`'s corrected check 13
has never met the bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit` cannot be
built here (no `west`, no `ZEPHYR_BASE`); the four DUT-gated bench tasks are unchanged; and the
ESP32-C5 USB-enumeration fact `core/028` tagged `[assumed]` still needs one look at one board. **A
real uninstall on a pre-change machine is the only way the legacy-marker path is ever exercised end
to end** — not a hardware debt, but a debt, owed to an attended session.

**api/030** — `src/build.rs`'s log drain used `next_line()`, which decodes UTF-8 per line and treats
the first bad byte as EOF — one latin-1 path silently dropped the rest of a build log, worst on
failing builds. Now reads raw bytes via `read_until`, falls back to `from_utf8_lossy` only for the
failing line, names substituted lines by number. Reviewer said the fix should have been its own
decision rather than an amendment to decision 18 (truncation) — agreed, but burndown forbids
authoring one, so the finding was left in `inbox/` rather than fixed, for a later non-burndown leg to
file properly. Pushed `decisions/build.md` from 10,934→11,134 B (crossed 11,059 B reserve);
`tasks/api/050` filed in the same commit, blocked, `In flux: yes`.
Merged: `agent/api/030-build-log-utf8` (code `a0950ec`, doc `d2ab624`). Ownership check base
`2e58fb9694c0`.
**Reviewer:** 1 finding — inbox/api-030-review-finding.md
**Hardware debts:** **none new.** A build-log drain is host-side and exercised against a real child
process in-crate. Prior debts carry forward unchanged from the two entries above — including that a
native Windows build of `embarch-core` is owed and the fleet cannot run one.

**study-designer/010** — `AstProtocol`'s public shape changed (line numbers threaded through error
paths; `sources`/`session` grew a 4th tuple field, `line: u32` added) after confirming no consumer
outside the crate exists, independently by the supervisor and the reviewer. `validate_protocol`'s
protocol-wide errors report at the `protocol` line by design, not a shortcut. Supervisor edited
`interfaces/eap.md` in the fold to correct "Every error carries its source line" (the false claim this
whole task existed to fix), over the reviewer's own read that it was out of scope for a finding.
Merged: `agent/study-designer/010-eap-error-lines` (code `9089feb`, doc `2fd192f`), plus this fold's
own edit to `embarch-study-designer/interfaces/eap.md`. Ownership check base `2fd192f3a015`.
**Reviewer:** no findings.
**Hardware debts:** **none new.** This unit is a host-side parser change in a `no_std`-adjacent crate
and touched no board. Prior debts carry forward unchanged from the `topology/022` entry above. The
`.eap` interpreter this parser feeds has a firmware half on dev-bench pinned against this module by
a literal frame; nothing in this unit exercised that side, so no bench debt is owed but the question
is recorded rather than left absent.

**topology/022** — first burndown leg of the day (re-armed 22:06, deadline 06:59, 97%/97% caps, wave
12; a 4-unit leg cap makes wave 12 unreachable by construction). `decisions/crate.md` decision 4 —
the token mirror in `embarch-umbrella/src/token.rs` closed, no longer live — corrected against
source (worker found 3 call sites, reviewer re-derived and found 4; commit-message-only discrepancy,
nothing on disk wrong). Reviewer's own finding — `open.md`'s mirrors bullet had gone stale one layer
down from this same diff — fixed in the fold: `open.md` now 5,016/5,120 B (104 B left, tightest the
file has been).
Merged: `agent/topology/022-crate-md-mirror-retired` (code none — dispatched doc-only; doc `e420bf5`),
plus this fold's own edits to `embarch-topology/open.md` and `tasks/topology/014-compact-topology.md`.
Ownership check base `10f8e75a35a8`. Dispatch note for this leg (announced at 22:06) misattributed
as "leg 053" in four claim commits, left uncorrected once workers were live; leg is actually 054.
**Reviewer:** 1 finding — inbox/topology-open-md-line-27-stale-token-mirror.md
**Hardware debts:** **none new, and none possible** — this unit changed documentation only and
touched no code repo and no board. All prior debts carry forward unchanged: a native Windows build
of `embarch-core` is owed and the fleet cannot run one (`core/028`, `core/015`, `core/010`);
`umbrella/037`'s corrected check 13 has never met the bench that found its defects; `embarch-outpost`'s
Zephyr `tests/unit` cannot be built here (no `west`, no `ZEPHYR_BASE`); the four DUT-gated bench
tasks are unchanged; and the ESP32-C5 USB-enumeration fact `core/028` tagged `[assumed]` still needs
one look at one board. Burndown forbids bench units outright, including by the supervisor's own
hands, so none of these could have been touched regardless.

**core/029** — split `decisions.md` along the file's real seam rather than the task's suggested one:
`platform.md` keeps decisions 1,2,3,4,7,14,15,17 (5,820 B); new `embarch-core/decisions/auth.md`
takes 5,6,11,42,46 (6,627 B), both out of reserve, byte-identity re-derived independently by the
reviewer including the three protected passages (decision 1/2/7/17's Corrected paragraph, decision
3's SCM handshake detail, decision 46's rejected `include_str!` arm). Reviewer's finding — a stale
`history/core.md` link naming `decisions/platform.md` directly for a decision that moved to
`auth.md` — fixed in the fold.
Merged: `agent/core/029-compact-core-platform` (code none — dispatched doc-only; doc `5c55b4b`), plus
this fold's own one-line edit to `history/core.md`. Ownership check base `608c7223f81b`.
**Reviewer:** 1 finding — inbox/doc-history-core-decision-42-link-stale-after-029-split.md
**Hardware debts:** **none new, and none possible** — this unit changed documentation only and
touched no code repo and no board. All prior debts carried forward unchanged: a native Windows build
of `embarch-core` is owed and the fleet cannot run one (`core/028`, `core/015`, `core/010`);
`umbrella/037`'s corrected check 13 has never met the bench that found its defects; `embarch-outpost`'s
Zephyr `tests/unit` cannot be built here (no `west`, no `ZEPHYR_BASE`); the four DUT-gated bench
tasks are unchanged; the bench queue is parked by the owner's own commit; and the ESP32-C5
USB-enumeration fact `core/028` tagged `[assumed]` still needs one look at one board.

**suite/021** — a `suite`-scope unit (no worker, whole diff the supervisor's, announced and parked
31 minutes with no objection). Re-measured the task's own evidence and found it incomplete in three
places (`embarch-doc`'s `docs-ci.yml`, `embarch-umbrella`'s manual `assemble-suite.yml`, and
`embarch-outpost` never having had `.github` either — task had only asserted the last of
`embarch-dev-bench`). Both `embarch-core` decision 1/2/7/17 and `embarch-dev-bench` decision 9 gained
dated **Corrected 2026-09-08** paragraphs retiring the CI-implemented claim, keeping the reasoning.
Surfaced that `embarch-dev-bench` and `embarch-outpost` have no CI and no `Cargo.toml`, so the
fleet's own merge gate cannot reach either at all. Pushed `embarch-core/decisions/platform.md` into
reserve (11,701/12,288 B) and filed `tasks/core/029` in the same commit, split-first, dispatchable.
Merged: doc `ac20966` — **the fold commit itself, not a merge** (a `suite` unit has no branch and no
worker). Announced and parked at `ts` `1788917508.792199` (2026-09-08 19:31:48), 31 minutes with no
objection before executing.
**Reviewer:** no findings.
**Hardware debts:** **none new, and none possible** — this unit changed three documents and touched
no code repo. All prior debts carried forward unchanged: a native Windows build of `embarch-core` is
owed and the fleet cannot run one (`core/028` added to it, `core/015` and `core/010` behind it);
`umbrella/037`'s corrected check 13 has never met the bench that found its defects; `embarch-outpost`'s
Zephyr `tests/unit` cannot be built here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by
the owner's own commit; and the ESP32-C5 USB-enumeration fact `core/028` tagged `[assumed]` needs one
look at one board.

**core/028** — `embarch-core/README.md` documented four env overrides
(`EMBARCH_DEV_BENCH_PORT`/`_SERIAL`/`_PRODUCT`/`_INTERFACE`) that `decisions/probes.md` decision 23
had already removed with no replacement knob; replaced with prose naming the real mechanism
(`embarch_topology::hardware::resolve_dev_bench_port`, `POST /probes/enroll`, `POST
/dev-bench/link`). Supervisor over-tightened worker prose at the merge, introducing a wrong noun and
then a relative cross-repo link the reviewer caught as the exact shape decision 46 rejects — fixed in
`11f5dc3` (noun fix in `4e0e7f4`). Reviewer's second flag — an `[assumed]` ESP32-C5 USB-enumeration
hardware "fact" with circular provenance across two task files, neither a measurement — rewritten to
say so plainly rather than being landed as fact.
Merged: `agent/core/028-readme-env-overrides` (code `fec6841`, doc `74cbc87`), plus two supervisor
follow-ups on `embarch-core`: `4e0e7f4` (noun correction) and `11f5dc3` (relative link → URL), and
this fold's own edit to `embarch-core/open.md`.
**Reviewer:** 1 finding — inbox/core-readme-relative-doc-link-contradicts-decision-46.md
**Hardware debts:** **one, and it is the standing `embarch-core` one, now owed by this unit too.**
The native Windows build was not run — `hidapi`'s `build.rs` wants an MSVC `cc` WSL lacks, and
Windows `cargo.exe` cannot follow this worktree's Linux symlinks. It takes ~52 s from the main
checkout and it is the owner's; the diff is `README.md` only, no `src/` change. Newly sharpened
rather than added: the ESP32-C5 USB-enumeration fact now carries an `[assumed]` tag and a named
discharge — one board, one look. Carried forward unchanged: `umbrella/037`'s corrected check 13 has
never met the bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit` cannot be built
here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own commit.

**study-designer/008** — `DeclaredGatt`, `Study.gatt`, `MAX_DECLARED_SERVICES` never existed at any
commit (`git log -S` empty); withdrew all three from `interfaces/types.md`, `spec.md`, and a fourth
document the worker found unprompted — `decisions/seals.md`, which listed `gatt` among fields
outside the study's integrity seals despite the field never existing. Decision 45's tombstone kept
its reasoning, opened "Designed, never built," and named the real types (`GattServiceInfo`,
`GattCharacteristicInfo`) it would reuse if ever built — reviewer confirmed both types are real.
Merged: `agent/study-designer/008-declaredgatt` (doc `ffed7ca`; no code SHA — doc-only unit).
**Reviewer:** no findings.
**Hardware debts:** **none new, and none possible** — this unit removed descriptions of code that has
never existed. All prior debts carried forward unchanged and none was touched: a native Windows build
of `embarch-core` is owed and the fleet cannot run one (`core/015`, `core/010` behind it);
`umbrella/037`'s corrected check 13 has never met the bench that found its defects; `embarch-outpost`'s
Zephyr `tests/unit` cannot be built here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by
the owner's own commit.

**umbrella/036** — narrowed a three-mirror task to one before dispatch (WSL2 token detection only);
`src/token.rs` (245 lines) deleted, `embarch-umbrella` now calls
`embarch_core_client::token_discovery::resolve_token` in process, closing a promise `topology/020`
had made in `decisions/crate.md`. `decisions/mirrors.md` decision 20's cost argument (declining a
shared crate as "more machinery than the problem justifies") had a four-day shelf life —
`embarch-api/crates/embarch-core-client` already existed for exactly this function — amended to say
so. Task left **partially done**: `CoreConfig`/`ProjectConfig` mirror drift and `doctor` check 6's
title still open. Reviewer flagged (unprompted) that `topology/020`'s own qualification of
`crate.md`, written one leg earlier, was made false by this same diff hours later — filed as
`tasks/topology/022` rather than fixed here.
Merged: `agent/umbrella/036-token-mirror` (code `e1a5e7c`, doc `444f84d`).
**Reviewer:** no findings.
**Hardware debts:** **none new, and none possible** — this is a dependency swap and comment
repointing, host-side throughout, and no board can observe it. All prior debts carried forward
unchanged and none was touched: a native Windows build of `embarch-core` is owed and the fleet
cannot run one (`core/015`, `core/010` behind it); `umbrella/037`'s corrected check 13 has never met
the bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit` cannot be built here (no
`west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own commit.

**study-designer/023** — `interfaces/limits.md`'s `MAX_DISCOVERED_SERVICES` row credited one decision
(57, static source extraction) with both a 3-service figure it validates and a 7-service figure that
belongs to a different, live-discovery decision (44) behind an encrypted link — split into two
correctly-credited clauses. No code SHA, doc-only, one table row.
Merged: `agent/study-designer/023-limits-row-provenance` (doc `46ac546`; no code SHA — doc-only
unit).
**Reviewer:** no findings.
**Hardware debts:** **none new, and none possible** — one table row. All prior debts carried forward
unchanged and none was touched: a native Windows build of `embarch-core` is owed and the fleet cannot
run one (`core/015`, `core/010` behind it); `umbrella/037`'s corrected check 13 has never met the
bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit` cannot be built here (no
`west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own commit. This leg touched no
hardware and incurred no hardware debt in any of its four units.

**api/049** — `dev_bench_hello()`'s CLI success object named a key `schema_version`, which
`json_out::stamped()` unconditionally overwrites with the crate's own envelope constant — the
dev-bench handshake's real compat number reached no machine reader. Renamed to
`dev_bench_schema_version`. The existing test suite could not have caught it (it drives every
subcommand against a closed port, so `dev-bench-hello` only ever builds its error object); a new
`tests/dev_bench_hello_success.rs` drives the real subprocess against a `MockCore` with a
deliberately distinct handshake number. Supervisor mutation-tested the new test by reverting the fix
locally and confirming it fails.
Merged: `agent/api/049-json-schema-collision` (code `4ceedc8`, doc `739b19f`).
**Reviewer:** no findings.
**Hardware debts:** **none new.** This is host-side throughout and no board can see it; confirming
the *rendered* value against a real Core is possible but adds nothing the mock does not already
establish. All prior debts carried forward unchanged: a native Windows build of `embarch-core` is
owed and the fleet cannot run one (`core/015`, `core/010` behind it); `umbrella/037`'s corrected
check 13 has never met the bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit`
cannot be built here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own
commit.

**dev-bench/012** — `embarch-dev-bench/decisions/ble.md` found at 12,282/12,288 B (six bytes of
headroom, the tightest file in the corpus) despite a size-debt date two weeks out; dispatched a
split-only exception against its `In flux: yes` compaction task on the reasoning that a verbatim
split restates nothing so the bar doesn't forbid it. Split into pairing/security (decisions 11, 15,
33, 34, 37, stayed) and a new `decisions/scanning.md` (17, 23, 31, 32, 44) along a "before a
connection exists" seam. Supervisor mechanically diffed every `###`-delimited section pre/post split
(9/9 identical) rather than trusting the report.
Merged: `agent/dev-bench/012-split-ble` (doc `ec5cdf4`; no code SHA — doc-only unit).
**Reviewer:** no findings.
**Hardware debts:** **none new, and none possible** — this unit moved text between two files. All
prior debts carried forward unchanged: a native Windows build of `embarch-core` is owed and the fleet
cannot run one (`core/015`, `core/010` stacked behind it); `umbrella/037`'s corrected check 13 has
never met the bench that found its defects; `embarch-outpost`'s Zephyr `tests/unit` cannot be built
here (no `west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own commit. `ble.md`
went 12,282 B (99.95%)→64.3% of cap, out of reserve, marked PAID; `open.md` (338 B left) and
`spec.md` (780 B left) remain `In flux: yes` squeezes, untouched.

**topology/020** — `decisions/crate.md` decisions 4 and 8 claimed linking the shared crate leaves
"nothing left to mirror" and "no way for the two to disagree" — true of the crate, false of callers:
`api/038` had already found `embarch-core-client` linking the crate while still running its own
narrower `is_wsl2` check beside a `detect_wsl2` call it never made. Qualified (not reversed) with
dated paragraphs; `open.md` gained a bullet recording that no cheap detector exists for a caller
writing a second predicate beside a call it never makes. Reviewer flagged one thing it could not
verify (an `embarch-api` SHA, unreachable from a doc-repo reviewer) — supervisor verified it by hand:
`861f30f api/038: token_discovery's WSL2 check delegates to embarch_topology::detect_wsl2`.
Merged: `agent/topology/020-crate-md-uniqueness` (doc `a8a35a0`; no code SHA — doc-only unit).
**Reviewer:** no findings.
**Hardware debts:** **none new, and nothing here can incur one** — the whole unit is two paragraphs
in a decisions file and one bullet in an `open.md`. Carried forward unchanged from the last leg: a
native Windows build of `embarch-core` is owed and the fleet cannot run one, with `core/015` and
`core/010` stacked behind it; `umbrella/037`'s corrected check 13 has never met the bench that found
its defects; `embarch-outpost`'s Zephyr `tests/unit` suite cannot be built from this environment (no
`west`, no `ZEPHYR_BASE`); the bench queue is parked by the owner's own commit. Pushed
`decisions/crate.md` into reserve (91.9%, 998 B left); `tasks/topology/021` records it — now four
open compaction tasks in the `topology` scope (`014`, `017`, `019`, `021`).

**api/038** — `status.d/api-038-...` fragment named the wrong mechanism (a shared suite-level doc
fragment for a change to a sub-project decisions file `check-ownership.py` has no allow-list row for
at all); converted into `tasks/topology/020` instead of folded. Decision 62 as landed cited a
`status.d/` filename that didn't match the actual fragment and, more importantly, that fragments are
transient — consumed and deleted by the very fold that lands the citing decision, so it was born
pointing at nothing (third instance of this class this leg) — repointed at the durable
`tasks/topology/020`. `token_discovery::is_wsl2` narrowed to delegate to
`embarch_topology::software::detect_wsl2` (accepts only "microsoft" ∪ `$WSL_DISTRO_NAME`, strictly
less accepting than the old "microsoft" ∪ "wsl" union) — accepted as an honestly-hedged decision, with
a real narrow surviving failure case named.
Merged: `agent/api/038-wsl2-predicate` (code `861f30f`, doc `bbceeae`).
**Reviewer:** no findings.
**Hardware debts:** **none new.** Nothing here needs a board: the predicate is host-side, the tests
are host-side, and no token was read from a real install. One inherited debt is sharper: this change
alters where `embarch-api` looks for the token on a WSL2 host, and nobody has run it against a real
deployed Core. Carried forward unchanged: a native Windows build of `embarch-core` is owed and the
fleet cannot run one, with two changes now stacked behind it (`core/015` and this leg's `core/010`);
`umbrella/037`'s corrected check 13 has never met the bench that found its defects; `embarch-outpost`'s
Zephyr `tests/unit` suite cannot be built from this environment (no `west`, no `ZEPHYR_BASE`). The
bench queue is still parked by the owner's own commit.

**study-designer/020** — `tasks/study-designer/007` cited a sentence in
`embarch-study-designer/open.md` that has never carried it; the bullet lives in
`embarch-dev-bench/open.md` under "Never exercised" and was amended 2026-09-07 to record leg 039's
stopped attempt. Re-quoted with the full amended sentence. Supervisor added a merge-time assertion
reading `007`'s `State:` line before merging, to confirm an owner-parked task (`blocked` since
2026-09-07) wasn't silently unparked by a unit that just noticed the old quote was wrong.
Merged: `agent/study-designer/020-source-cites-wrong-open-md` (doc `bc211fa`; doc-only, no code SHA).
Ownership check base `ac88483f1d8f`.
**Reviewer:** no findings.
**Hardware debts:** **none new, and one deliberately not discharged.** This unit's whole subject is a
bench debt — bond clearing has never been observed firing on real hardware, decision 11's clearing
step has only been reasoned about — and the correct outcome was to fix the citation and leave the
debt exactly where it is. It needs the bench, the bench queue is parked by the owner's own commit,
and `study-designer/007` stays `blocked`. Carried forward unchanged: a native Windows build of
`embarch-core` is owed and the fleet cannot run one, now with two changes stacked behind it
(`core/015` and this leg's `core/010`); `umbrella/037`'s corrected check 13 has never met the bench
that found its defects; `embarch-outpost`'s Zephyr `tests/unit` suite cannot be built from this
environment (no `west`, no `ZEPHYR_BASE`).

**core/010** — supervisor mis-provisioned this unit's doc worktree inside `embarch-core` itself
(wrong-repo `cd`); the first worker correctly wrote/committed/pushed nothing and reported it, cost
one wasted spawn. `src/flash_backend.rs`'s cited line numbers had aged out (`locate()` at :270-274
not :270-272, unreachable arm at :308 not :273-274) — third consecutive leg a task file's own
numbers were stale. Deleted (rather than resurrected) the dead `.with_context("...is not a known
backend")` unreachable arm on the argument that keeping a fallible arm there would be a second lie
about an unreachable path; reviewer independently confirmed the other `build()` call site (the
non-forced `preferred_for` loop) keeps its own guard untouched.
Merged: `agent/core/010-flash-backend-unknown-name` (code `b278e96`, doc `b51abda`).
**Reviewer:** no findings.
**Hardware debts:** **one new, and it is the ordinary Windows one rather than a board.**
`embarch-core` changed, so a native Windows build is owed before anything ships — the fleet cannot
run one, and this is the second `embarch-core` change now stacked behind it (`core/015` is the
other). Nothing here needs a probe: every new test is host-side, no flash was performed. Carried
forward unchanged: `umbrella/037`'s corrected check 13 has never met the bench that found its
defects and needs only the dev-bench board; `embarch-outpost`'s Zephyr `tests/unit` suite cannot be
built from this environment (no `west`, no `ZEPHYR_BASE`) and no leg can currently claim it green.
The bench queue is still parked by the owner's own commit.

**dev-bench/005** — README's espressif section still instructed setting the dead
`EMBARCH_DEV_BENCH_PORT`; removed rather than replaced, since the ESP32-C5-WROOM-1 DK enumerates as
a plain USB Serial/JTAG device with no VCOM — no `link_port_interface` exists to state, and inventing
one would have been an inferred hardware fact. Filed the resulting gap (`tasks/core/028`). A
`manifest/west.yml` NCS-pin caveat was also removed on the argument the nordic board has since been
enrolled/flashed/run repeatedly — not independently verified that the specific pin used matches those
runs.
Merged: `agent/dev-bench/005-readme-board-and-links` (code `8854f3e`, doc `37efe77`). Ownership check
bases: code `973483ef1e67`, doc `2bddaba24832`.
**Reviewer:** no findings.
**Hardware debts:** **none new, and one narrowed.** This unit needed no board and took none. What it
did do is write the enrolment fact an operator cannot infer — `link_port_interface = 2`, because the
DK's console is VCOM1 and detection's lowest-index fallback lands on a port that accepts bytes and
never answers — into the build instructions, scoped to the nRF54L15DK, never promoted to measured.
Carried forward unchanged: `core/015`'s native Windows build of `embarch-core` is the owner's and
still outstanding; `umbrella/037`'s corrected check 13 has never met the bench that found its
defects; `embarch-outpost`'s Zephyr `tests/unit` suite cannot be built from this environment (no
`west`, no `ZEPHYR_BASE`) and no leg can currently claim it green. The bench queue is still parked by
the owner's own commit.

**outpost/004** — 22 mechanical-looking `design.md`→`decisions.md` reference fixes across 14 files,
re-derived (task's 22 had aged to 26) and split into genuinely-mechanical decision-number citations
vs. section citations needing the target file opened. Comment-only verified by the supervisor
(`git diff -U0` filtering comment-prefixed lines returned nothing) since the Zephyr `tests/unit`
ztest suite cannot run in this environment (no `west`/`ZEPHYR_BASE`) — a real, opened debt. Reviewer
line qualified by the supervisor as possibly manufactured: the worker had already found the stale
"deliberately uncharacterised" README sentence and logged it as out-of-scope; the supervisor told the
reviewer to file a drop if it agreed, and it did.
Merged: `agent/outpost/004-design-md-citations` (code `9621112`, doc `a06da6f`). Ownership check
bases: code `0517e598f8c1`, doc `6fd3210ba83b`.
**Reviewer:** 1 finding — inbox/outpost-readme-status-overhead-stale.md
**Hardware debts:** **one new, and it is a toolchain rather than a board.** `embarch-outpost`'s
Zephyr `tests/unit` ztest suite has not been built or run by this unit, and cannot be from the
fleet's environment — no `west`, no `ZEPHYR_BASE`. It is owed in a session that has the Zephyr
toolchain; no leg can currently claim that suite is green after any `embarch-outpost` change. Carried
forward unchanged: `core/015`'s native Windows build of `embarch-core` is the owner's and still
outstanding, and is also what would deploy `core/020`'s rename; `umbrella/037`'s corrected check 13
has never met the bench that found its defects and needs only the dev-bench board. The bench queue
is still parked by the owner's own commit.

**umbrella/042** — one-line fix, dispatched as one on purpose (`embarch-umbrella`'s stale
`decisions/surface.md` citation for decision 52, which had moved to `decisions/shape.md`). Widened
the acceptance grep to every `embarch-api/decisions/` path cited under `embarch-umbrella/` rather
than only the task-named file, since `api/048` had split a decision into `shape.md` an hour earlier
in this same leg. Surfaced the underlying gate gap: `check-decision-refs.py` resolves a decision
number and falls back to "defined somewhere in this sub-project," so a citation naming the wrong file
still resolves — third unit this leg to hit the same blind spot.
Merged: `agent/umbrella/042-schema-skew-path` (code none — docs-only, zero diff in `embarch-umbrella`;
doc `640012c`). Ownership check base `893a62977f05`; the doc branch's pre-rebase tip `2030a07` is not
a revert handle.
**Reviewer:** no findings.
**Hardware debts:** none owed by this unit — a documentation citation, no board, no build. Carried
forward unchanged: `core/015`'s native Windows build of `embarch-core` is the owner's and still
outstanding, and is also what would deploy `core/020`'s rename; `umbrella/037`'s corrected check 13
has never met the bench that found its defects and needs only the dev-bench board. The bench queue is
still parked by the owner's own commit.

**api/048** — directed the worker to the CLI-subcommand arm of a two-arm task (restoring CLI ⊇ MCP)
rather than the decision-amendment arm, since `suite/features.md` already claimed the superset as
shipped. Landed two adjacent one-line repairs (`interfaces/tools.md`'s "no CLI twin" line;
`decisions/study-events.md`'s stale link to a decision that had since moved). Pre-picked
`decisions/shape.md` over the blocked, near-empty `tool-wrapping.md` for the new decision 61, with the
argument written into the task before dispatch. Reviewer found the same `schema_version`-overwrite
collision that became `api/049` — supervisor verified the overwrite mechanism in `src/json_out.rs`
before filing rather than fixing it in the fold, since the fix needed a mock-Core test to be real.
Merged: `agent/api/048-cli-superset` (code `4bd3b5e`, doc `13b5bf6`). Ownership check bases: code
`ddd820ec7cd9`, doc `a29b5cfae5aa` after the rebase; the doc branch's pre-rebase tip `9e1ba86` is not
a revert handle.
**Reviewer:** 1 finding — inbox/api-dev-bench-hello-json-schema-version-collision.md
**Hardware debts:** none owed by this unit. It adds a reason to care about an existing one:
`api/049`'s missing test wants a mock Core, not a board — while the human check that
`dev-bench-hello` renders sensibly against a real Core still rides on `core/015`'s native Windows
build, which is the owner's and still outstanding, and which is also what would deploy `core/020`'s
`self_reported_hardware_id` rename this whole tool chain is written around. Carried forward
unchanged: `umbrella/037`'s corrected check 13 has never met the bench that found its defects and
needs only the dev-bench board. The bench queue is still parked by the owner's own commit.

**study-designer/022** — worker deliberately not sent to read `reference-dut-fw` source (the same
shortcut that created the original defect); restored a citation to decision 57 in
`src/limits.rs:80-84` rather than re-deriving a number. Reviewer caught a misattribution the
supervisor's own four pre-asked questions had missed: the landed row credited decision 57 with both a
3-service figure (correct) and a 7-service figure that belongs to decision 44 (live discovery behind
an encrypted link, a different mechanism) — filed as `tasks/study-designer/023` rather than
hand-patched a third time from memory.
Merged: `agent/study-designer/022-limits-service-count` (code `c58f592`, doc `4ff55eb`). Ownership
check base `345f0978cee8`.
**Reviewer:** 1 finding — inbox/study-designer-022-decision-57-cited-for-a-number-it-does-not-state.md
**Hardware debts:** none owed by this unit — a citation fix, no board touched, and the worker was
directed away from the one action that would have needed one. Carried forward unchanged: `core/015`'s
native Windows build of `embarch-core` is the owner's and still outstanding; `umbrella/037`'s
corrected check 13 has never met the bench that found its defects and needs only the dev-bench
board. The bench queue is still parked by the owner's own commit.

**umbrella/026** — a reconstruction, not a re-run: leg 047 had merged and pushed both `umbrella/026`
and `api/036` to `main` on 2026-09-07 and was killed (`fleet stop` 21:06) before folding either. The
work was correct on `main` already; what was missing was the bookkeeping (`changelog.d/` fragments
never consumed, `suite/features.md` never reassembled, `tasks/umbrella/026` still reading
`State: claimed — leg 046`). Every Done-when box was ticked by the worker's own record; nothing was
re-run or re-read for intent, and the task file's state line says so explicitly. Also corrected the
prior day's closing note: `api/036`'s `inbox/` drop was not lost — the owner rescued it as
`tasks/umbrella/042-schema-skew-cites-a-moved-api-decision-path.md`, `State: open`.
Merged: nothing by this unit's actor. SHAs recorded because they had none anywhere until this entry:
`umbrella/026` — `embarch-umbrella` `95f2975`, `embarch-doc` `2156553`, merged to `main` as `2b29d67`.
`api/036` — `embarch-api` `95c1954`, `embarch-doc` `cf12cae` then `8005396`.
**Reviewer:** skipped (no diff of mine to review — this fold consumes two already-merged units'
fragments and corrects one task's state).
**Hardware debts:** none owed by this recovery. Carried forward unchanged from the 2026-09-07 fold:
`core/015`'s native Windows build of `embarch-core` is still outstanding and is the owner's, and it
is load-bearing twice over — it is also what would deploy `core/020`'s `self_reported_hardware_id`
rename; `umbrella/037`'s corrected check 13 has never been run against the bench that found its
defects, and needs only the dev-bench board. The bench queue is still parked by the owner's own
commit.
*Days 2026-09-07 to 2026-09-07 rolled to [log-archive/supervisor-log-2026-09-07-to-2026-09-07.md](log-archive/supervisor-log-2026-09-07-to-2026-09-07.md).*
