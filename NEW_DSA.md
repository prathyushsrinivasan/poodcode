Phase 1 - Foundation
Arrays
Strings
Array patterns
Hashing
Sorting
Binary search
Phase 2 — Linear Data Structures
Linked lists
Stack
Queue
Deque
Monotonic stack
Monotonic queue
Phase 3 — Recursion
Recursion
Recursion trees
Divide and conquer
Backtracking
Phase 4 — Trees
Binary trees
Tree traversals
BST
Heaps
Priority queues
AVL trees
Red-black trees
Trie
Phase 5 — Core Algorithmic Patterns
Two pointers
Sliding window
Prefix sums
Difference arrays
Fast/slow pointers
Binary search on answer
Greedy
Phase 6 — Graphs
Graph representations
BFS
DFS
Connected components
Cycle detection
Bipartite graphs
Topological sort
DAG algorithms
DSU
MST
Dijkstra
Bellman-Ford
Floyd-Warshall
Phase 7 — Dynamic Programming
DP fundamentals
Memoization
Tabulation
1D DP
2D DP
Knapsack
Subset DP
LIS
LCS
Edit distance
Grid DP
Interval DP
Tree DP
Bitmask DP
Digit DP
Phase 8 — Range Queries
Prefix sums
Fenwick tree
Segment tree
Lazy propagation
Sparse table
Binary lifting
LCA
Euler tour
Phase 9 — Advanced Graphs
SCC
Bridges
Articulation points
Eulerian paths
Network flow
Bipartite matching
0-1 BFS
A*
Advanced shortest paths
Phase 10 — Advanced Trees
Heavy-light decomposition
Centroid decomposition
Treaps
Splay trees
Persistent segment trees
Link-cut trees
Wavelet trees
Phase 11 — Advanced Strings
KMP
Z algorithm
Rabin-Karp
Rolling hash
Aho-Corasick
Manacher
Suffix array
LCP
Suffix automaton
Suffix tree
Phase 12 — Mathematics
Number theory
GCD
Sieve
Prime factorization
Modular arithmetic
Modular inverse
Fast exponentiation
Combinatorics
Probability
Matrix exponentiation
Linear algebra
XOR basis
Phase 13 — Advanced Competitive Programming
Mo's algorithm
Sweep line
Coordinate compression
Meet in the middle
Convex Hull Trick
Li Chao Tree
Divide-and-conquer DP
Knuth optimization
CDQ divide and conquer
Parallel binary search
FFT
NTT
Min-cost max-flow
Hungarian algorithm
Advanced matching

---

# Curriculum structure — one template for every topic

The list above is the syllabus and stays as it is. This is the shape every
topic on it takes. Each topic is a self-contained learning unit, and every
unit has the same 16 sections in the same order.

```
TOPIC
│
├── 1. Concept
├── 2. Mental Model
├── 3. TypeScript Fundamentals
├── 4. Syntax & Patterns
├── 5. When to Use It
├── 6. When NOT to Use It
├── 7. Step-by-Step Examples
├── 8. Implementation
├── 9. Complexity
├── 10. Common Mistakes
├── 11. Problem Recognition
├── 12. Guided Practice
├── 13. Independent Practice
├── 14. Variations
├── 15. Review
└── 16. Mastery
```

**The principle.** Don't teach the learner an algorithm and then ask them to
memorise it. Teach them to understand it, recognise when it applies,
implement it in TypeScript and understand its tradeoffs, until they can
derive the solution themselves.

**The progression every topic follows:**

```
Understand → See → Copy → Complete → Implement → Recognize → Apply → Combine → Master
```

## 1. Concept

Explain the concept from zero:

- What it is
- What problem it solves
- Why it exists
- How it works conceptually
- Important terminology
- Internal behaviour, where relevant
- A simple real-world analogy, when useful

The learner should understand the idea before seeing any code.

## 2. Mental Model

Give the learner a way to picture it.

```
Input
  ↓
[ processing area ]
  ↓
Output
```

- **Data structures:** what is stored, how the elements relate, and what
  changes when each operation runs.
- **Algorithms:** the initial state, each step, and the final state.

This section answers *"What should I picture in my head while solving this?"*

## 3. TypeScript Fundamentals

Teach only the TypeScript this topic needs, and nothing more. For example:

```ts
const nums: number[] = [];
```

Then explain whichever of these apply: `number[]`, indexing, the relevant
array methods, `Map`, `Set`, interfaces, generics, classes, tuples,
`null` / `undefined`.

The learner should never have to think *"I understand the algorithm, but I
don't know how to express this in TypeScript."*

## 4. Syntax & Patterns

The code shapes the learner will meet again and again, starting general:

```ts
for (let i = 0; i < nums.length; i++) {
    // ...
}
```

and then the topic-specific ones: standard syntax, common variations,
idiomatic TypeScript, useful built-ins, and reusable code structures.

Goal: recognise this code on sight, and be able to write it yourself.

## 5. When to Use It

One of the most important sections: the signals in a problem statement.

```
If you see:
- contiguous
- subarray
- substring
- longest
- shortest
- at most K

→ Consider this technique.
```

This is not a rigid rule. Explain **why** each word is a clue.

## 6. When NOT to Use It

Equally important: situations that look the same but need something else.

```
Looks like X
      ↓
But constraint Y changes the problem
      ↓
Use Z instead
```

This keeps pattern memorisation from turning into pattern misuse.

## 7. Step-by-Step Examples

Start extremely simple, and explain less with each example.

1. **Basic.** Explain every line.
2. **Slight variation.** The learner identifies what changed.
3. **Real problem.** Demonstrate the complete technique.

## 8. Implementation

Four stages, each with less support than the one before:

- **A — Read code.** A completed implementation.
- **B — Complete code.** The important pieces are removed:

  ```ts
  function solve(nums: number[]): number {
      let ___ = 0;

      // ...
  }
  ```

- **C — Pseudocode → TypeScript.** The algorithm in plain English or
  pseudocode; the learner converts it.
- **D — From scratch.** No scaffold.

## 9. Complexity

Every topic states time and space explicitly, for example **Time O(n),
Space O(1)**, and explains *where* each bound comes from rather than just
stating it. Compare the alternatives as well:

```
Approach A → O(n²)
Approach B → O(n)

Why did we improve?
```

## 10. Common Mistakes

A dedicated section covering logic mistakes, boundary mistakes, off-by-one
errors, incorrect initialisation, TypeScript-specific mistakes, complexity
mistakes, misuse of built-ins, and incorrect assumptions. Each entry has:

- ❌ **Mistake**
- **Why it happens**
- **How to recognise it**
- ✅ **Correct approach**

## 11. Problem Recognition

Separate from *When to Use It*. This section trains the learner to name the
underlying technique behind an unfamiliar problem. Give short scenarios,
such as *"You need to find the first occurrence…"*, and ask *"What
technique or data structure should you consider?"*

No coding yet. This builds recognition on its own.

## 12. Guided Practice

Problems in which the curriculum still actively teaches:

```
Problem
 ↓
Understand the input/output
 ↓
Identify relevant concept
 ↓
Choose approach
 ↓
Pseudocode
 ↓
Implementation
 ↓
Test
```

Hints are layered, each one revealed only on request:

1. **Hint 1:** a small conceptual nudge.
2. **Hint 2:** the approach.
3. **Hint 3:** the algorithm's steps.
4. **Hint 4:** a code-level hint.
5. **Solution:** a complete explanation, plus code.

## 13. Independent Practice

The scaffolding is gone. The learner gets the problem, examples,
constraints, and a function signature, and nothing else. Hints may exist,
but they are never shown automatically.

## 14. Variations

Once the basic technique is understood, change the problem on purpose:

```
Basic version
      ↓
Different input
      ↓
Additional constraint
      ↓
Optimization requirement
      ↓
Combination with another technique
```

This stops the learner from memorising one solution.

## 15. Review

A compact review at the end.

**Must know:** definition, core idea, syntax, recognition clues, complexity.

**Must be able to:** implement it, explain it, recognise it, and apply it to
a new problem.

**Quick reference:**

```
Pattern:
Typical syntax:
Time:
Space:
Think of this when:
Be careful about:
```

## 16. Mastery

Finishing a topic's lessons does not make it complete. Mastery tests
several separate abilities:

```
                    TOPIC MASTERY
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Understanding    Implementation    Recognition
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                    Application
                         ↓
                    New Problems
```

| Ability | Test |
| --- | --- |
| Understanding | Explain what the technique does |
| Syntax | Complete a TypeScript implementation |
| Recognition | Identify the technique from a problem |
| Implementation | Implement it from scratch |
| Application | Solve an unfamiliar problem |

---

# The template against the app as it stands

What a unit in `seeds/dsa_curriculum.json` already carries, section by
section. There are **46 units**, and the counts show how many of them have
each field filled in. Problems come from `seeds/problems.json` (799, every
one with a TypeScript starter, so the judge side is ready).

| # | Section | Existing field(s) | Units | Status |
| --- | --- | --- | --- | --- |
| 1 | Concept | `why`, `internals` | 46, 23 | **Have** |
| 2 | Mental Model | `model`, `invariant` | 46, 20 | **Have** |
| 3 | TypeScript Fundamentals | — | 0 | **Missing** |
| 4 | Syntax & Patterns | `skeletons` (228) | 46 | **Partial**: Java only |
| 5 | When to Use It | `signals` — `when` / `reach_for` / `why` (340) | 46 | **Have** |
| 6 | When NOT to Use It | stage `router[].not_when` (67), `variants[].gotcha` | stage level | **Partial** |
| 7 | Step-by-Step Examples | `traces` (114), `walkthrough` | 46, 16 | **Partial** |
| 8 | Implementation A–D | A `skeletons`/`walkthrough` · B — · C — · D `build_it`, `lab` | 29, 11 | **Partial**: B and C missing |
| 9 | Complexity | `costs` (275), `bigo` (294), `rewrites` slow→fast (72) | 46, 46, 22 | **Have** |
| 10 | Common Mistakes | `pitfalls` — `symptom` / `cause` / `fix` (330), `edge_cases`, `bug` quizzes (52) | 46 | **Partial** |
| 11 | Problem Recognition | `model` quizzes (17) | a few | **Thin** |
| 12 | Guided Practice | *Warm up* / *Core* rungs, problem `hints`, `stuck` | 46 | **Partial** |
| 13 | Independent Practice | *Extra practice* / *Stretch* rungs | 46 | **Have** |
| 14 | Variations | `variants` (203), *Variations* rung, `followups` | 22, 25, 8 | **Partial** |
| 15 | Review | `checks` (327), `interview`, stage `cheatsheet` | 46, 46, 3 stages | **Partial** |
| 16 | Mastery | status comes from Core problems solved (`src/lib/curriculum.ts`) | — | **Missing** |

## What each gap actually is

- **3 · TypeScript Fundamentals.** There is no field for it, and the unit
  prose teaches Java: `Scanner`, `int` overflow, `StringBuilder`, `TreeMap`.
  Much of it has to be rewritten, not just added to. In TypeScript, overflow
  is a `Number.MAX_SAFE_INTEGER` / `bigint` question, and there is no
  built-in sorted map or priority queue.
- **4 · Syntax & Patterns.** Every skeleton is Java. They need TypeScript
  versions.
- **6 · When NOT to Use It.** The "looks like X, but use Z" contrasts exist,
  but only in the stage `router`, where they are spread across units. Each
  unit needs its own list, in the `looks_like` / `but` / `use_instead` shape.
- **7 · Step-by-Step Examples.** `traces` are state tables for a single
  example. The template wants three examples (basic, slight variation, real
  problem), with the explanation thinning out from one to the next.
- **8 · Implementation B and C.** All 115 `drills` are short-answer; none of
  them has a code blank. Stage B needs fill-in-the-blank TypeScript that the
  type checker verifies (the TS Mastery course's `tscheck` already does
  this). Stage C, pseudocode → TypeScript, has no counterpart at all.
- **10 · Common Mistakes.** `symptom` / `cause` / `fix` maps onto *recognise
  / why / correct*. What's missing is a ❌/✅ code pair and any
  TypeScript-specific mistakes.
- **11 · Problem Recognition.** Only 17 `model` quizzes exist in the whole
  curriculum. Every unit needs its own set of scenario → technique questions,
  with no code.
- **12 · Guided Practice.** Problems carry 3 hints (592 of them) or 4 (187),
  and those hints aren't in *nudge → approach → steps → code* order. For
  example, `count-equal-pairs` ends its hints at the brute force. There is
  also no *understand → identify → choose → pseudocode* walk before the
  editor opens.
- **14 · Variations.** Only 22 units have `variants`, and the ones that exist
  list alternatives rather than the *different input → extra constraint →
  optimisation → combination* sequence.
- **15 · Review.** There is no per-unit quick-reference card in the fixed
  *Pattern / Typical syntax / Time / Space / Think of this when / Be careful
  about* shape.
- **16 · Mastery.** A unit is *solid* at 60% of its Core problems solved and
  *complete* at 100%, and both decay over time. That measures Application
  only. Understanding, Syntax, Recognition and Implementation-from-scratch
  need gates of their own, which sections 8, 11 and 15 can supply.

## One mismatch to settle first

The syllabus above lists about 120 topics in 13 phases, and the app has 46
units. Many topics currently exist only as a rung inside a larger unit
(*Difference arrays* inside `prefix-sums`, *Fast/slow pointers* inside
`linked-lists`). Others are only mentioned, not taught: AVL and red-black
trees appear as the "balance caveat" in `bst`. And some have no unit and no
problems at all yet: all of Phase 10, Aho-Corasick and suffix automata /
trees in Phase 11, and most of Phase 13 (Mo's, Li Chao, Knuth, CDQ, NTT).
Applying the template topic by topic means splitting the shared units and
writing the missing ones.

---

# First topic built: Sliding Window

One topic end to end, to settle the format before scaling it. It is in the
app at **Library → “NEW DSA: Sliding Window”** (route
`/library/topic/sliding-window`, also in the command palette). It is a
separate course, so the Java curriculum is untouched.

## What each section contains

| # | Section | In the topic |
| --- | --- | --- |
| 1 | Concept | What / why / how / skipping argument, 9 terms, an analogy |
| 2 | Mental Model | ASCII picture + the loop diagram, and a **step-through stepper** (25 frames of `"abcabcbb"`) |
| 3 | TypeScript Fundamentals | 9 snippets (`number[]`, strings, `Map`, `Set`, count arrays, `let`/`const`, signatures, `Infinity`, an O(1) queue) + 2 judged fill-in drills |
| 4 | Syntax & Patterns | 6 shapes: fixed, longest, shortest, count, exactly-k, choosing the summary |
| 5 | When to Use It | 8 clues, each with *why* it is a clue, + the one real test |
| 6 | When NOT to Use It | 7 “looks like X → but Y → use Z” cases |
| 7 | Step-by-Step Examples | Basic (every line explained + trace), Variation (“what changed?” multi-select), Real problem (trace + notes only) |
| 8 | Implementation | A read (annotated) → B complete (4 blanks) → C pseudocode → TS → D from scratch; B–D judged |
| 9 | Complexity | Where O(n) and the space come from, 3-approach comparison, slow/fast rewrite, 3 pricing questions |
| 10 | Common Mistakes | 12 mistakes, filterable by category, each ❌ code / why / how to recognise / ✅ code |
| 11 | Problem Recognition | 10 scenarios, no code; 5 of them are deliberately *not* windows; every wrong option says why |
| 12 | Guided Practice | 2 problems walked understand → identify → approach → pseudocode → implement → test, with 4 labelled hint layers |
| 13 | Independent Practice | 5 problem-bank problems (solved in the normal Solve view), nudges hidden |
| 14 | Variations | Basic → different input → added constraint → optimisation (a hidden n = 300 000 case that O(n·k) cannot pass) → combination |
| 15 | Review | Must know, must be able to, quick-reference card |
| 16 | Mastery | 5 gates: Understanding sitting (4/5), Syntax fill-in, Recognition sitting (5/6), from-scratch implementation, 2 of 3 unfamiliar problems |

## How it is built

- **Content:** `tools/new_dsa.py` (the template's rules, enforced at
  generation), `tools/new_dsa_kit.py` (exercise/question builders),
  `tools/new_dsa_sw_learn.py` (sections 1–8), `tools/new_dsa_sw_practice.py`
  (9–16), and `tools/new_dsa_sw_refs.py` (brute-force Python references).
  Output: `src-tauri/seeds/new_dsa.json`.
- **Correctness:** every expected output comes from a brute-force reference,
  never from the TypeScript under test. `tools/verify_new_dsa.py` type-checks
  and runs all 12 solutions and confirms every starter fails.
  `src-tauri/tests/verify_new_dsa.rs` proves the same through the app's real
  judge at its 6-second limit.
- **App:** `src/pages/NewDsaTopic.tsx` (one section at a time, with a rail
  like the Library's), `src/components/newdsa/Parts.tsx` (question, sitting,
  stepper, layered hints, guided walk), `src/lib/newDsa.ts` (progress and
  mastery, with tests).
- **Progress:** no new table. Marks go into `solved_exercises` as
  `ndsa:<topic>:…`, and linked problems count through their solved status.
  Lessons (1–15) and mastery (16) are shown as two separate bars. Finishing
  the lessons reads *“Lessons done · not yet mastered”*.

## Decisions taken without asking (open to change)

- **TypeScript only**, as the template says. The Java curriculum stays as it
  is, alongside.
- **Mastery sittings reveal no answers on a fail.** They flag which questions
  were wrong, and a retake reshuffles the options. Learning-section questions
  explain on the spot and allow a retry.
- **Reading sections** (1, 2, 4, 5, 6, 10, 15) count as done when you press
  *Done · next*. There is no quiz on them, because recognition and
  understanding are tested in 11 and 16.
- **Nothing is locked.** The order is the recommended curve, not a gate. Only
  the guided walk opens its steps one at a time.