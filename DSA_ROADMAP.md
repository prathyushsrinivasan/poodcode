# DSA Curriculum — remediation roadmap

Findings from an audit of `seeds/dsa_curriculum.json` (6 stages, 33 units, 243
problems), its generator (`tools/dsa_curriculum.py` + `dsa_s1…s6.py`), the
hydration layer (`src/lib/curriculum.ts`) and the two pages that render it
(`src/pages/Library.tsx`, `src/pages/CurriculumUnit.tsx`).

Ordered as commits. Each step lands green — generator lints and
`src-tauri/tests/verify_dsa_curriculum.rs` pass — before the next begins.
Steps 1-3 are self-contained and cheap; 4-6 are the pedagogical core; 7 is
cleanup that can be done at any time.

---

## Step 1 — Real prerequisites (a DAG, not a chain)

**Problem.** All 33 units form a straight chain: each unit's only prereq is the
unit textually before it. So `tries` "builds on" `dp-2d` and `union-find`
"builds on" `topological-sort`. The `ready` flag and the "builds on …" banner in
[CurriculumUnit.tsx:92-98](src/pages/CurriculumUnit.tsx#L92-L98) assert
something false.

**Work.**

1. In each `dsa_s*.py`, replace the `prereqs=` of every unit with its true
   dependencies. Starting set (all point backwards, so the existing lint at
   `dsa_curriculum.py:265-268` still passes):

   | unit | prereqs |
   |---|---|
   | `sliding-window` | `two-pointers`, `hashing` |
   | `prefix-sums` | `arrays-first-pass`, `hashing` |
   | `strings` | `arrays-first-pass`, `hashing` |
   | `binary-search` | `sorting`, `complexity` |
   | `simulation-and-matrix` | `arrays-first-pass`, `loops-and-digits` |
   | `design` | `hashing`, `linked-lists` |
   | `queues-and-deques` | `arrays-first-pass` |
   | `heaps` | `sorting`, `complexity` |
   | `trees` | `recursion` |
   | `bst` | `trees`, `binary-search` |
   | `backtracking` | `recursion`, `strings` |
   | `graph-traversal` | `queues-and-deques`, `recursion` |
   | `topological-sort` | `graph-traversal` |
   | `union-find` | `graph-traversal` |
   | `shortest-paths` | `graph-traversal`, `heaps` |
   | `greedy` | `sorting` |
   | `intervals` | `sorting`, `greedy` |
   | `dp-1d` | `recursion`, `complexity` |
   | `dp-2d` | `dp-1d`, `simulation-and-matrix` |
   | `tries` | `trees`, `strings` |

2. New lint in `_check_curriculum`: reject a prereq list that is exactly
   `[previous unit]` for more than N consecutive units — the failure mode that
   produced this bug is invisible otherwise. (Foundations legitimately chains;
   scope the lint to stages 2+.)
3. `curriculum.ts` needs no change — `ready` already folds over a list.

**Payoff.** The "builds on" banner becomes true; unlocks Step 6's skip-ahead
routing; enables a dependency-graph view on `/library`.

---

## Step 2 — On-ramps: every unit opens below its ceiling

**Problem.** The `rungs climb` lint compares each rung's *hardest* problem
([dsa_curriculum.py:290-295](tools/dsa_curriculum.py#L290-L295)), so a unit that
starts at Medium passes cleanly. Eight units have **zero** Easy or Intro
problems: `backtracking` (12 problems, 10 M + 2 H), `union-find` (11),
`dp-1d` (10), `tries` (7), `dp-2d` (6, of which 4 Hard), `graph-traversal`,
`topological-sort`, `shortest-paths`, `greedy`. `binary-search` is 3 Medium.
`sliding-window` is 1 Medium + 1 Hard.

**Work.**

1. Author the missing entry problems in `tools/gen_seed.py` (reference solution
   + computed expected outputs, per the bank's existing contract). Minimum one
   Easy per starved unit:
   - `sliding-window` — fixed-window maximum sum; first window containing all
     of a small char set.
   - `binary-search` — plain `lower_bound` on a sorted array; first-true on a
     boolean predicate.
   - `graph-traversal` — count connected components on an adjacency list.
   - `topological-sort` — detect a cycle in a tiny DAG.
   - `shortest-paths` — BFS distance on an unweighted grid (the Dijkstra
     warm-up that shows why weights change the algorithm).
   - `union-find` — count components with union by size, no compression.
   - `backtracking` — generate all subsets of ≤4 elements.
   - `dp-1d` — climbing stairs / min-cost-to-reach, 1-D table by hand.
   - `dp-2d` — grid unique-paths with no obstacles.
   - `tries` — insert + exact-match lookup only.
   - `greedy` — activity selection on 4 intervals.
2. Place each on a new opening rung ("Warm up") in its unit.
3. New lint: for any unit with >4 problems, the easiest problem on its **first**
   rung must rank at least one below the unit's hardest problem. Fails the
   build.

**Payoff.** "Warm up → core → variations → stretch" stops being a label on a
ladder that actually starts mid-height.

---

## Step 3 — Rebalance unit weight against interview yield

**Problem.** "Every problem placed exactly once" is a good rule for
*reachability* but it lets the bank's accidental distribution define the
syllabus. Current skew:

| starved | n | overweight | n |
|---|---|---|---|
| `sliding-window` | 2 | `trees` | 16 |
| `complexity`, `recursion`, `greedy`, `binary-search` | 3 | `linked-lists` | 14 |
| `sorting`, `graph-traversal`, `topological-sort`, `shortest-paths` | 4 | `simulation-and-matrix` | 12 |

**Work.**

1. Add a `weight` (1-3) to `_unit()` expressing interview yield, and a target
   band per weight (e.g. weight 3 → 8-14 problems, weight 2 → 5-9, weight 1 →
   3-6).
2. Lint the band as a **warning printed at generation time**, not an assertion —
   it is a content-debt ledger, and failing the build on it would block every
   unrelated change.
3. Author toward the bands, highest weight first: `sliding-window`,
   `binary-search`, `graph-traversal`, `dp-1d`, `greedy`, `shortest-paths`.
4. Do **not** delete the overweight units' problems. Demote the surplus to a
   "Extra practice" rung marked optional, so `total` still reflects what the
   unit asks of you. Requires a per-rung `optional: bool` and a `curriculum.ts`
   change: optional rungs count toward `total` only when started.

**Payoff.** The course spends learner time in proportion to what the time is
worth.

---

## Step 4 — Depth beats beyond the linear-structures stage

**Problem.** `internals`, `traces` and `build_it` are populated only in the five
`structures` units (~2000 chars of internals each); the other 28 units have
`0`. The "why are these the costs?" question the README uses to justify the
asymmetry is *also* unanswered where the state is hardest to hold in prose.

**Work.** Author, in priority order:

1. **Traces** (highest value — all of these are state changing over time, which
   is exactly what `_trace` exists for):
   - `dp-1d` — the table filling cell by cell, with the recurrence in a column.
   - `dp-2d` — one row of the grid at a time, and the same table read backwards
     to reconstruct the answer.
   - `union-find` — the forest before/after each union, then the same sequence
     with path compression, so flattening is visible rather than asserted.
   - `shortest-paths` — the priority queue's contents as Dijkstra settles each
     node, including the stale entry that must be skipped.
   - `backtracking` — the recursion stack: push, explore, **undo**, one row per
     frame.
   - `binary-search` — `lo`/`hi`/`mid` per iteration on a missing target, which
     is where the off-by-one lives.
2. **Internals**: `trees` (why a skewed BST degrades to a linked list, and what
   balancing buys), `tries` (`children[26]` vs `HashMap<Character,Node>` —
   memory against alphabet size), `binary-search` (`lo + (hi-lo)/2` and the
   overflow it avoids), `hashing` (load factor, and what `HashMap` does *not*
   promise about order).
3. **Build it**: `union-find` and `tries` — both ~30 lines, neither understood
   until typed. `dp-1d`: convert a memoised recursion to a table by hand.
4. Extend the structures-stage lint (`internals` + `traces` + `build_it`
   required) to cover the units above once authored, so they cannot regress.

---

## Step 5 — Retention: spacing and decay

**Problem.** Nothing ever comes back. `src/lib/revision.ts` already implements
an SM-2 ladder (`LADDER = [1, 3, 7, 14, 30, 90]`) and the app has `CardStudy`
and Flashcards, but the curriculum touches none of it:

- A unit reaches `solid` at 60% and stays there permanently
  ([curriculum.ts:86-92](src/lib/curriculum.ts#L86-L92)). No decay, so at month
  three a green unit and a remembered unit are indistinguishable.
- ~150 authored self-checks across 33 units are reveal-the-answer only — no
  grading, no scheduling. They are already the ideal deck and they are inert.

**Work.**

1. **Self-checks as cards.** Feed `unit.checks` into the existing card pipeline,
   keyed `dsa-check:<unit>:<index>`, graded remembered/forgot, scheduled by
   `dueAfterReview`. No new table: reuse whatever backs `CardStudy`.
2. **Unit decay.** Add a derived `stale` flag to `HydratedUnit`: a unit that was
   `solid`/`complete` but whose problems' last-solved dates are all older than
   its ladder interval renders with a muted badge and a "re-practice" action.
   Keep it derived — the no-progress-table property is worth preserving.
3. **A review lane on `/library`.** One button: "Due today — N checks,
   M problems", drawing from the units you have cleared.

---

## Step 6 — Recognition: interleaving and placement

**Problem, part one.** All practice is blocked and labelled. You solve a
sliding-window problem on the page titled Sliding Window. The Signals tables
exist precisely to train prompt → technique routing, and nothing ever tests
that routing — which is the skill that actually fails under interview pressure.

**Work.**

1. **Stage-end mixed set.** A new unit-like page per stage: problems drawn
   unlabelled from any unit in that stage and earlier. Before the editor opens,
   ask "which technique does this prompt want?" with distractors drawn from
   sibling units' `signals[].reach_for`. Score the routing answer separately
   from the solve — recognition and implementation are different failures and
   deserve different numbers.
2. **Time-to-solve.** The curriculum's own thesis is reflex speed ("your hands
   start typing a sliding window before you have finished the sentence"), but
   `solid` counts correctness alone. Record elapsed solve time and surface
   "solved, slowly" as a re-practice signal in Step 5's review lane.

**Problem, part two.** The course starts at `System.out.println` for everyone.
Units open regardless of readiness, which is right, but there is no honest way
to *skip*.

3. **Placement diagnostic.** Per stage: one signal-routing question plus one
   representative problem. Clearing both marks the stage cleared (derived, like
   everything else), so an experienced learner lands in `heaps` rather than
   scrolling past four Intro units. Entry point on `/library` above the stage
   list.

---

## Step 7 — Small, independent fixes

- **`complexity` unit has 3 problems and no complexity exercises**, while
  `src/lib/complexity.ts` already exists. Add "what is the Big-O of this
  snippet?" items, graded, to the unit.
- **`bit-manipulation` links 1 Learn lesson**; peer units link 3-4. Under-served.
- **`alg_pattern_recognition` and `alg_what_is` are the only two `alg_*`/`ds_*`
  concepts no unit links** — and pattern recognition is the curriculum's whole
  thesis. Link them (stage-2 goal, or a short routing unit), then add a lint
  mirroring the problem rule: every `alg_*`/`ds_*` concept must be linked by at
  least one unit.
- **[Library.tsx:15](src/pages/Library.tsx#L15) says "thirty-two units"**; there
  are 33. Derive the count or drop the number. Audit README's counts at the same
  time (`README.md:164-250`).

---

---

# Part B — quality of life

Part A is content and pedagogy. This part is the day-to-day friction of using
the curriculum: loading, navigating, finding things, and the small dishonesties
in what the UI reports. Independent of Part A and of each other unless noted, so
these can be picked off in any order — roughly cheapest-first within each group.

## B1 — Loading and caching

**The badge costs a megabyte.** `TaughtIn`
([CurriculumData.tsx:54-68](src/components/CurriculumData.tsx#L54-L68)) fetches
the entire 455 KB `dsa_curriculum.json` and runs a full `hydrate()` against an
empty problem list — building all 33 units, every rung, every trace — to render
one "Taught in Heaps" badge. It does this on every Solve page open.

- Add a `dsa_unit_for_slug` command (or a slug → `{key, title, icon, tagline}`
  index emitted alongside the seed at generation time) and have `TaughtIn` read
  that.
- Cheaper interim fix: memoise the `unitBySlug` map in a module-level promise so
  the second Solve page reuses the first one's parse.

**Every page re-fetches everything.** `useCurriculumData`
([CurriculumData.tsx:13-25](src/components/CurriculumData.tsx#L13-L25)) loads
curriculum + all 243 problems on every mount of all three Library pages. Unit →
back → different unit is three full loads. The comment defends this as freshness
insurance, which is right about the *problems* and wrong about the *curriculum* —
the seed never changes at runtime. Split the two: cache the curriculum in a
module-level promise, keep re-fetching problems, and expose `reload` (already
returned, currently unused) for after a solve.

**An unloadable curriculum shows "Loading…" forever.**
[CurriculumUnit.tsx:34](src/pages/CurriculumUnit.tsx#L34) checks `if (!data)`
and never reads `error`, which `useCurriculumData` does return and `Library.tsx`
does handle. A failed fetch leaves the unit page spinning with no explanation.
Handle `error` the way Library does. *(This one is a bug, not a polish item.)*

**"Loading…" at 20vh** on both pages is a blank screen for a 455 KB parse. A
skeleton of the stage list costs little and stops the page from looking broken.

## B2 — Navigation and addressability

**The 33 units are not in the command palette.** It offers exactly two
curriculum entries — "Go to the DSA Curriculum" and "Browse all problems"
([CommandPalette.tsx:81-82](src/components/CommandPalette.tsx#L81-L82)) — while
the weekly courses register a command *per authored week*
([CommandPalette.tsx:27-40](src/components/CommandPalette.tsx#L27-L40)). Register
one per unit (`"Heaps & Priority Queues — DSA unit 19"`), using the same builder.
Highest ratio of value to effort on this whole list.

**No section deep links.** Sections are collapsible and their open state is
remembered, but there is no `/library/unit/heaps#pitfalls`. The pitfalls table is
the thing you want to reach mid-debug, from outside the app, in one click. Give
each `Section` an `id`, honour the hash on mount by force-opening that section,
and scroll to it.

**No keyboard paging between units.** The prev/next buttons exist
([CurriculumUnit.tsx:58-67](src/pages/CurriculumUnit.tsx#L58-L67)) but nothing is
bound. `[` / `]` for prev/next unit, `g l` back to the curriculum.

**No stage context on the unit page.** The header is icon + title + tagline; you
cannot tell whether you are in stage 2 or stage 5 without going back. Add a
`Stage 4 of 6 · Linear Data Structures` breadcrumb, linking to the stage section.

**Solving does not continue the ladder.** After a solve you are on the Solve
page, whose only route back is `TaughtIn` → the unit page → rescan the rungs for
the next unsolved row. Put "Next in this rung →" on the Solve page, sourced from
the same walk that produces `HydratedUnit.next`.

**Nothing remembers where you were.** `data.next` is computed
([curriculum.ts:171-175](src/lib/curriculum.ts#L171-L175)) as the first
unfinished *ready* unit — which is a reasonable default and not the same as the
unit you had open yesterday. Store a last-opened unit key and offer "Resume
Backtracking" beside "Up next".

## B3 — Finding things

**Search is unranked and unexplained.** `searchUnits`
([curriculum.ts:219-238](src/lib/curriculum.ts#L219-L238)) concatenates fields
into one haystack and returns `filter` order, so a title match ranks below an
incidental prose match, and the result card never shows *why* it matched.
Searching `"infinite loop"` returns unit cards with no hint that the hit was a
pitfall symptom — the one line you actually wanted.

- Return match provenance (`field`, and the matching snippet) and render it on
  the card.
- Rank: title > tagline > signal wording > pitfall symptom > skeleton name >
  internals prose.
- Widen the haystack — it currently omits `why`, `model`, `checks[].q`,
  `costs[].op`, `build_it`, and the rungs' problem titles and notes. "amortised"
  and "load factor" live in `costs` and `checks`; neither is searchable today.

**Browse cannot filter by unit or stage.** It gained a unit *column* and a
"mine only" toggle for unplaced problems
([LibraryBrowse.tsx:54-61](src/pages/LibraryBrowse.tsx#L54-L61)), but there is no
"show me every problem in `graph-traversal`" or "everything in stage 5" — the
obvious query once the column is there. Add unit and stage to `ProblemFilter`.

## B4 — Honest, useful progress

**Nothing can be marked known.** The only lever on a unit's state is solving its
problems, so someone who learned heaps elsewhere either re-solves eleven
problems or watches the Library sit at 20% forever. Add a per-unit
"I know this — skip it" toggle that reads as cleared for `ready`/`next` purposes
and renders distinctly from earned green. (Pairs with Part A step 6's
diagnostic, but is worth having on its own and is far cheaper.)

**A unit's size says nothing about its cost.** The card shows `11 problems`
([Library.tsx:183-187](src/pages/Library.tsx#L183-L187)), which reads identically
for 11 Intro problems and for 10 Medium + 2 Hard. Show the difficulty mix — a
small stacked bar, or `E2 · M6 · H3` — and optionally an estimated time.

**Every stage opens by default.** `useCollapse("dsa-stage", true)`
([Library.tsx:27](src/pages/Library.tsx#L27)) renders all 33 unit cards in a
two-column grid on first paint, so the page opens several screens tall and the
unit you want is rarely visible. Default to: current stage open, cleared stages
collapsed, later stages collapsed.

**Section preferences are per unit.** Collapse state is keyed
`dsa-unit:${key}` ([CurriculumUnit.tsx:28](src/pages/CurriculumUnit.tsx#L28)), so
"I always want pitfalls open and motivation closed" has to be re-expressed 33
times. Key the default by *section type* and let a per-unit override win over it.

**`next` treats attempted and untouched alike.** The walk takes the first
unsolved problem in rung order ([curriculum.ts:130-137](src/lib/curriculum.ts#L130-L137)),
so a problem you fought with yesterday and one you have never opened are
interchangeable. Prefer the attempted one — it is the one with context still
loaded — or make it a setting.

## B5 — Working with the content

**The playbook cannot be used.** The instruction is "copy each of these out by
hand once" ([CurriculumUnit.tsx:162-165](src/pages/CurriculumUnit.tsx#L162-L165))
and the page offers no copy button and nowhere to type. Add both: a copy control
per skeleton, and "open in a scratch editor" wired to the existing editor so the
retyping happens in-app against a compiler.

**Self-checks have no revision mode.** Each is individually revealable, which is
right for study and wrong for the month-later scan. Add "reveal all" / "hide all"
for the section. (Grading and scheduling are Part A step 5.)

**Traces are static.** A step-through — one row revealed at a time, with the
predicted next state hidden — is the version that tests rather than shows. Worth
doing once Part A step 4 has authored enough traces to justify the control.

**Rungs cannot be launched as a session.** A rung is explicitly "a group of
problems drilling the same twist", but there is no "work this rung" that queues
its unsolved problems and advances through them. This is the natural home for
B2's "next in rung" plumbing.

## Cheapest first

If you want a single QOL commit that is felt immediately: the `error` handling
fix (B1), unit commands in the palette (B2), collapsed-by-default stages (B1/B4),
copy buttons on skeletons (B5), and the difficulty mix on unit cards (B4). None
touches the seed schema or the generator.

---

## Sequencing notes

- **Independent, any order:** Steps 1, 4, 7.
- **Step 2 before Step 3** — author the on-ramps first, then rebalance, so the
  new problems count toward the target bands.
- **Step 5 before Step 6** — the mixed set draws from cleared units, which is
  what decay defines.
- **Schema changes:** Step 3 adds `weight` to a unit and `optional` to a rung;
  Step 6 adds a stage-level mixed set and per-problem solve time. Both touch
  `src/types.ts`, `src-tauri/src/models.rs` and the Rust verifier — batch them
  to avoid two rounds of seed regeneration.
- Every step regenerates with `python tools/gen_seed.py` and must keep
  `cargo test --test verify_dsa_curriculum` and `npm test` green.
- **Part B is independent of Part A**, with two exceptions worth ordering:
  B4's "I know this" toggle wants doing *before* A6's diagnostic (the toggle is
  the diagnostic's storage mechanism, and is useful alone), and B5's trace
  step-through wants doing *after* A4 has authored the traces to step through.
  Everything else in Part B can land today against the current seed.
