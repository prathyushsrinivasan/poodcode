# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 7 — Dynamic programming, and the capstone.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# The last core stage. Greedy — decide now and prove it safe — moved to stage 3,
# beside the sort that makes its rules provable. What is left is the other way to
# get a best answer: consider every option, and never solve a subproblem twice.
#
# DP used to be two units, split by the number of indices, which is not how the
# problems divide. The knapsack lived half in each, and interval and state-machine
# DP had no rung at all. It is now four units, split by the SHAPE of the state:
#
#   dp-1d               one index along a sequence (take/skip, Kadane, prefixes)
#   dp-knapsack         an item index plus a remaining capacity (and counting mod p)
#   dp-2d               a grid, or a prefix of each of two sequences
#   dp-intervals-states a range [i, j] filled by length, or a small machine per step
#
# Tries follow, then DESIGN closes the core curriculum: its problems combine
# hashing, linked lists, heaps, binary search and ordered maps, so it is the one
# unit that needs everything before it.
# ---------------------------------------------------------------------------

_S7 = _stage(
    "dp-and-design", "Dynamic Programming & Design", "🏔️",
    "Consider every option without repeating work — then combine everything.",
    """
Greedy takes a local choice and proves it safe. When no such proof exists, you
must keep every option open — and the only way to afford that is to never solve
the same subproblem twice. That is **dynamic programming**, and this stage
teaches it as four families, distinguished by what the state has to remember:

| Unit | The state remembers |
| --- | --- |
| **Linear** | a position along one sequence |
| **Knapsack** | which items are considered, and how much capacity is left |
| **Grids & two sequences** | a cell, or how far into each of two strings |
| **Intervals & states** | a range still to solve, or which situation you are in |

Recognising the family is most of the work: once the state is named, the
recurrence and the fill order follow. The stage ends with **tries** — a
structure that is its own algorithm — and **design**, where the only skill is
combining everything the curriculum has taught at the right cost.
""")


# --- Unit 31 — 1-D dynamic programming ---------------------------------------

_unit(
    "dp-1d", "Dynamic Programming I: Linear", "🧩", _S7,
    "Define the state, write the recurrence, and never compute it twice.",
    weight=3,
    prereqs=["recursion", "complexity"],
    why="""
Dynamic programming is where most people stall, and the reason is almost always
that it gets taught as a list of problems rather than as a procedure. It is a
procedure, and it has four steps. Follow them and the code writes itself;
skip the first one and no amount of staring at the array will help.

The unit covers the linear case — a single index moving along one sequence —
because that is where the four steps are visible. Every problem here is a
recursion you have already learned to write, plus a cache. The three units after
it keep the procedure and change only what the state has to remember.
""",
    model="""
### The four steps

1. **Define the state.** *"`dp[i]` is the answer for the first i elements"* —
   or "ending at i", which is a different definition and often the right one.
   Write the sentence down. If it is vague, everything after it will be wrong.
2. **Write the recurrence.** How does `dp[i]` follow from smaller entries?
   This is the choice you are making at step i.
3. **Base cases.** `dp[0]`, and whatever else the recurrence cannot reach.
4. **Order of evaluation.** Every entry the recurrence reads must already be
   computed — which for 1-D usually means left to right.

### "For the first i" versus "ending at i"

This distinction is the single most useful thing in the unit.

- **House robber** — `dp[i]` = best over the *first* i houses. The answer is
  `dp[n]`, and the recurrence chooses: `max(dp[i-1], dp[i-2] + a[i])`.
- **Maximum subarray** — `dp[i]` = best sum of a subarray *ending at* i, because
  a subarray must be contiguous. The recurrence is `max(a[i], dp[i-1] + a[i])` —
  extend, or start fresh — and the answer is the maximum over **all** `dp[i]`,
  not `dp[n]`.

If your recurrence needs "and it must include element i", the state ends at i,
and the answer is a maximum over the whole table.

### Top-down or bottom-up

They compute the same thing:

```java
// top-down: recursion + memo. Mirrors how you think.
long f(int i) {
    if (i < 0) return 0;
    if (memo[i] != -1) return memo[i];
    return memo[i] = Math.max(f(i - 1), f(i - 2) + a[i]);
}

// bottom-up: a loop. No stack risk, easier to optimise for space.
dp[0] = a[0]; dp[1] = Math.max(a[0], a[1]);
for (int i = 2; i < n; i++) dp[i] = Math.max(dp[i - 1], dp[i - 2] + a[i]);
```

Write top-down when you are deriving the recurrence; convert to bottom-up when
you want the space optimisation or are worried about stack depth.

### Rolling the array away

If `dp[i]` reads only the last one or two entries, you do not need the array:

```java
int prev2 = 0, prev1 = 0;
for (int x : a) {
    int cur = Math.max(prev1, prev2 + x);
    prev2 = prev1; prev1 = cur;
}
```

O(1) space. Do this **after** the O(n) version works, and only if asked — the
array version is much easier to debug.

### When a choice uses up a resource

Coins, capacities and budgets add a second thing to remember — how much is left —
and with it the loop-direction rule that separates reusing an item from using it
once. That is the next unit, *Knapsack & Subsets*.
""",
    signals=[
        _sig("“maximum / minimum / number of ways”, with choices at each step", "DP",
             "The trio of words that names the technique."),
        _sig("“contiguous subarray with the largest sum”", "`dp[i]` ending at i (Kadane)",
             "Extend or restart — the arrays unit's run counter, generalised."),
        _sig("“cannot take two adjacent”", "`dp[i] = max(dp[i-1], dp[i-2] + a[i])`",
             "Take it and skip back two, or skip it."),
        _sig("“can the string be split into dictionary words?”", "`dp[i]` over prefixes",
             "`dp[i]` true if some `j` has `dp[j]` true and `s[j..i]` is a word."),
        _sig("Greedy gave a counterexample", "DP, with the missing information as state",
             "Whatever greedy could not see is the dimension."),
    ],
    skeletons=[
        _sk("Kadane (ending at i)",
            "Maximum subarray, maximum product, best run.",
            """
long best = a[0], cur = a[0];
for (int i = 1; i < n; i++) {
    cur = Math.max(a[i], cur + a[i]);     // start fresh, or extend
    best = Math.max(best, cur);           // answer is over ALL i
}
""",
            "Seed from `a[0]`, not 0 — an all-negative array must return its largest element."),
        _sk("Take-or-skip (first i)",
            "House robber, weighted interval scheduling.",
            """
int prev2 = 0, prev1 = 0;
for (int x : a) {
    int cur = Math.max(prev1, prev2 + x);
    prev2 = prev1; prev1 = cur;
}
return prev1;
""",
            "Write the O(n) array version first; roll it up only once it is right."),
        _sk("Prefix-splitting DP",
            "Word break, decode ways, palindrome partitioning.",
            """
boolean[] dp = new boolean[n + 1];
dp[0] = true;                            // the empty prefix is always reachable
for (int i = 1; i <= n; i++)
    for (int j = 0; j < i; j++)
        if (dp[j] && isWord(s, j, i)) { dp[i] = true; break; }
""",
            "`dp[i]` is about the first i characters, so the answer is `dp[n]`."),
    ],
    costs=[
        _cost("1-D DP, O(1) transition", "O(n)", "O(n) → O(1) rolled", "Kadane, house robber."),
        _cost("1-D DP, O(n) transition", "O(n²)", "O(n)", "Word break, LIS by DP."),
        _cost("Memoised recursion", "O(states × transition)", "O(states) + stack", "Same bound, easier to derive."),
        _cost("Naive recursion without a memo", "O(2ⁿ)", "O(n)", "What the cache removes."),
    ],
    pitfalls=[
        _pit("The answer is `dp[n]` but should be the maximum over all `dp[i]`",
             "The state was defined as *ending at* i, where the answer can occur anywhere.",
             "Match the reported answer to the state definition you wrote in step 1."),
        _pit("Kadane returns 0 on an all-negative array",
             "`cur` and `best` were seeded with 0, implying an empty subarray is allowed.",
             "Seed both from `a[0]` unless the problem explicitly permits an empty subarray."),
        _pit("`ArrayIndexOutOfBoundsException` at i = 1",
             "The recurrence reads `dp[i-2]` before the base cases cover index 1.",
             "Set every base case the recurrence cannot reach, or offset the array by one."),
        _pit("The “minimum” answer comes back as a huge number",
             "An infinity sentinel was added to and never guarded.",
             "Check for the sentinel before adding, or compare against it at the end."),
        _pit("`StackOverflowError` in the memoised version",
             "Top-down recursion n deep on a large input.",
             "Convert to bottom-up iteration."),
    ],
    lessons=["dp", "recurrence", "alg_recurrences"],
    checks=[
        _chk("What are the four steps of writing a DP?",
             "Define the state in one sentence; write the recurrence; set the base cases; "
             "choose an evaluation order in which every entry read is already computed."),
        _chk("Why is maximum-subarray's state “ending at i” rather than “first i”?",
             "The subarray must be contiguous, so the decision at i is whether to extend the "
             "run ending at i−1 or start a new one. The answer is then the maximum over all "
             "i, not the last entry."),
        _chk("When should you roll a DP array down to a couple of variables?",
             "Only after the array version is correct, and only when the recurrence reads a "
             "fixed number of recent entries. It saves space and costs debuggability."),
    ],
    interview="""
Say the state definition out loud before writing anything: *"`dp[i]` is the
maximum sum of a subarray ending at index i"*. Interviewers accept a correct
recurrence immediately and reject a correct-looking table with no stated
meaning, because the second cannot be checked. Then offer the space
optimisation as a follow-up rather than writing it first — showing you know it
exists is worth as much as using it, and the array version is what you can
actually debug on a whiteboard.
""",
    traces=[
        _trace(
            "House Robber on [2, 7, 9, 3, 1] — the two candidates, per cell",
            "`dp[i]` = the best total using only houses `0…i`. The two middle columns are "
            "the recurrence written out: at every house you either skip it and keep what "
            "you had, or take it and add what you had two houses ago.",
            ["i", "a[i]", "skip = dp[i−1]", "take = dp[i−2] + a[i]", "dp[i] = max", "Table"],
            [
                ["0", "2", "— (nothing before)", "0 + 2 = 2", "**2**", "[2]"],
                ["1", "7", "2", "0 + 7 = 7", "**7**", "[2, 7]"],
                ["2", "9", "7", "2 + 9 = 11", "**11**", "[2, 7, 11]"],
                ["3", "3", "11", "7 + 3 = 10", "**11**", "[2, 7, 11, 11]"],
                ["4", "1", "11", "11 + 1 = 12", "**12**", "[2, 7, 11, 11, 12]"],
            ],
            "Row 3 is the one worth staring at: taking house 3 *loses*, so `dp[3]` repeats "
            "`dp[2]`. A 1-D table whose values never decrease is not a bug — it is the "
            "\"skip\" branch winning. And note that only `dp[i-1]` and `dp[i-2]` are ever "
            "read, so two variables would do; the array exists so you can see it.",
        ),
    ],
    build_it="""
### Convert a memoised recursion into a table, by hand, once

Bottom-up DP looks like a different technique from recursion, and it is not:
the table *is* the memo, with the call stack unrolled into a loop. Doing that
conversion by hand once makes every later "should this be top-down or
bottom-up?" question answerable in a sentence.

Take Climbing Stairs. Start from the honest recursion:

```java
static long ways(int n) {
    if (n == 0) return 1;      // one way to have made no moves
    if (n < 0)  return 0;      // overshot the top
    return ways(n - 1) + ways(n - 2);
}
```

**Step 1 — measure the damage.** Add a counter to `ways` and call it for
n = 30. You will see roughly 2.7 million calls for a function with 31 distinct
inputs. That ratio is the whole motivation.

**Step 2 — memoise.** One array and two lines:

```java
static long[] memo;            // sized n + 1, filled with -1

static long ways(int n) {
    if (n == 0) return 1;
    if (n < 0)  return 0;
    if (memo[n] != -1) return memo[n];     // ← added
    return memo[n] = ways(n - 1) + ways(n - 2);   // ← added
}
```

Count the calls again: 31 distinct computations. Same answer, exponential to
linear, two lines.

**Step 3 — write down the order the memo was filled in.** Instrument the
assignment to print `n` as each cell is written. You will see
`1, 2, 3, …, n` — increasing, every time. That is not a coincidence: `ways(n)`
cannot return until the smaller values have, so the memo is *necessarily*
completed from small to large.

**Step 4 — delete the recursion.** If the order is always increasing, write the
loop that produces it and the function calls become array reads:

```java
long[] dp = new long[n + 1];
dp[0] = 1;
for (int i = 1; i <= n; i++) {
    dp[i] = dp[i - 1] + (i >= 2 ? dp[i - 2] : 0);
}
```

The `n < 0` base case became the `i >= 2` guard — the same fact, relocated from
"a call that returns 0" to "a term that is not added".

### What you now know, that you did not before

- **Top-down and bottom-up compute identical tables.** They differ only in who
  decides the order: the call stack, or you.
- **Bottom-up needs you to know the order in advance.** When you cannot state
  it — a DP over subsets, a game tree, a graph with no obvious layering —
  memoised recursion is not the lazy option, it is the correct one.
- **Top-down costs stack depth.** n = 10⁶ overflows recursively and is fine
  iteratively; that alone decides some problems.
- **Bottom-up makes space optimisation visible.** The loop above reads only two
  cells back, so two `long`s replace the array. You cannot see that from the
  recursion, which is one reason to convert.

Do this same four-step walk on `house-robber` before you move on. It is the
last time it will feel like work.
""",
    rungs=[
        _rung("Warm up", "The three questions, where all three answers are obvious.",
              ["stair-ways-table"],
              {"stair-ways-table": "Print the whole table, not just the last cell. Seeing `1 1 2 3 5 8` come out is what makes the recurrence yours."}),
        _rung("Core", "One state, one choice, O(1) transition.",
              ["climbing-stairs", "min-cost-climbing-stairs", "house-robber"],
              {"climbing-stairs": "Fibonacci wearing a hat. Write the state sentence anyway — the habit is the point.",
               "house-robber": "Take-or-skip. The template for every “no two adjacent” problem."}),
        _rung("Variations", "States that end at i, and pseudo-polynomial tables.",
              ["maximum-subarray", "max-subarray-fn", "coin-change", "coin-change-ways"],
              {"maximum-subarray": "Kadane. Note that the answer is a maximum over the whole table, not the last cell.",
               "coin-change-ways": "Same table as coin-change, summing instead of minimising, base case 1."}),
        _rung("Stretch", "Transitions that are themselves a loop, or need two tracked values.",
              ["maximum-product-subarray", "decode-ways", "word-break"],
              {"maximum-product-subarray": "Track the minimum as well as the maximum: a negative times the smallest becomes the largest.",
               "decode-ways": "The 0 cases are the whole difficulty. Enumerate them before coding.",
               "word-break": "`dp[i]` over prefixes with an inner split loop — O(n²), and the same shape as palindrome partitioning."}),
    ],
    next_up="""
A single index stops being enough the moment a choice uses something up. The next
unit adds the amount left as a second dimension — and finds that one loop's
direction decides whether an item can be used twice.
""",
)


# --- Unit 32 — Knapsack and subsets ------------------------------------------

_unit(
    "dp-knapsack", "Dynamic Programming II: Knapsack & Subsets", "🎒", _S7,
    "When a choice uses something up, the amount left is part of the state.",
    weight=2,
    prereqs=["dp-1d", "math-number-theory"],
    why="""
Coins that make an amount, items that fit a bag, numbers that reach a target, a
budget, a weight limit — a whole family of problems makes a choice per item where
each choice **consumes a resource**. The linear unit's single index cannot
describe that: after the same items, having 3 units of capacity left and having
7 left are different situations with different futures.

So the state gains the amount left, and three questions share one table:
*the best value* (max), *whether it is reachable* (or), and *how many ways*
(sum — usually modulo a prime, which the math unit taught). The difference
between them is one operator. The difference between using an item once and
using it freely is one loop direction, and getting that backwards is the single
most common DP bug there is.
""",
    model="""
### The state

`dp[i][c]` = the answer using only the first i items with capacity c. For each
item there are two choices:

```java
dp[i][c] = max(dp[i - 1][c],                       // skip item i
               dp[i - 1][c - w[i]] + v[i]);        // take it, if w[i] <= c
```

Row i reads only row i − 1, so one array is enough — **if** you do not overwrite
what you still need.

### 0/1: each item once — capacity descending

```java
for (int[] item : items)
    for (int c = W; c >= item.w; c--)             // DESCENDING
        best[c] = Math.max(best[c], best[c - item.w] + item.v);
```

Going downwards, `best[c − w]` has not been touched in this item's pass, so it
still means "without this item". The trace below shows the ascending version
quietly packing the same item twice.

### Unbounded: reuse allowed — capacity ascending

```java
for (int c : coins)
    for (int a = c; a <= amount; a++)             // ASCENDING
        fewest[a] = Math.min(fewest[a], fewest[a - c] + 1);
```

Going upwards, `fewest[a − c]` may already include coin c — which is exactly
what "use it again" means. Coin change, perfect squares, rod cutting.

### Three questions, one table

| Question | Combine | Base case | Unreachable |
| --- | --- | --- | --- |
| Best value within capacity | `max` | `best[·] = 0` | — |
| Fewest items to hit exactly | `min(…, +1)` | `dp[0] = 0` | an ∞ sentinel |
| Can a subset hit exactly? | `or` | `dp[0] = true` | `false` |
| How many ways? | `+`, mod p | `dp[0] = 1` | `0` |

The counting base case is 1 because there is exactly one way to reach 0: take
nothing. Every count is built by extending that one way.

### Counting orders versus counting sets

`coin-change-ways` counts **sets** of coins (1+2 and 2+1 are the same): coins in
the outer loop. Swap the loops — amounts outside, coins inside — and you count
**ordered sequences** instead, which is a different problem (combination sum IV).
The loop nesting is the definition.

### Disguised knapsacks

- *Partition into two equal halves* — can a subset reach `total / 2`?
- *Assign + and − signs to hit a target* — a subset must sum to
  `(total + target) / 2`.
- *Smash stones until one is left* — split into two groups as equal as possible:
  the largest reachable sum ≤ `total / 2`.

The work is the algebra that turns the story into "reach exactly s"; after that
it is the loop above.
""",
    signals=[
        _sig("“fewest coins / items to make exactly …”", "Unbounded knapsack, ascending",
             "Reuse allowed; initialise with an ∞ sentinel."),
        _sig("“each item at most once”, “weight limit”", "0/1 knapsack, capacity descending",
             "Descending is the whole 0/1 constraint."),
        _sig("“how many ways to make …”", "The same loop, summing, mod p",
             "Base case 1. Items outside for sets, amounts outside for sequences."),
        _sig("“split into two groups with equal / closest sums”", "Subset sum to total / 2",
             "Reachability of every sum up to half the total."),
        _sig("“assign + or − to each number”", "Subset sum to (total + target) / 2",
             "Check the parity and the sign before building anything."),
        _sig("Capacity or amount up to 10⁹", "Not this table",
             "Pseudo-polynomial: the table is as big as the number. Look for greedy or meet-in-the-middle."),
    ],
    skeletons=[
        _sk("0/1 knapsack (best value)",
            "Each item once, a capacity limit.",
            """
long[] best = new long[W + 1];                 // best value within capacity c
for (int i = 0; i < n; i++)
    for (int c = W; c >= w[i]; c--)            // descending
        best[c] = Math.max(best[c], best[c - w[i]] + v[i]);
return best[W];
""",
            "Write the 2-D `dp[i][c]` once, then roll it — and check the direction."),
        _sk("Unbounded knapsack (fewest coins)",
            "Reusable items: coin change, perfect squares.",
            """
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);                   // a sentinel above any real answer
dp[0] = 0;
for (int c : coins)
    for (int a = c; a <= amount; a++)          // ascending: reuse allowed
        dp[a] = Math.min(dp[a], dp[a - c] + 1);
return dp[amount] > amount ? -1 : dp[amount];
""",
            "`amount + 1` as infinity cannot overflow when 1 is added to it."),
        _sk("Count subsets reaching a sum, mod p",
            "Number of ways; target sum with signs.",
            """
final long MOD = 1_000_000_007L;
long[] ways = new long[target + 1];
ways[0] = 1;                                   // the empty subset
for (int x : nums)
    for (int s = target; s >= x; s--)          // descending: each number once
        ways[s] = (ways[s] + ways[s - x]) % MOD;
return ways[target];
""",
            "Reduce after every addition. For coin *combinations* (reuse allowed) iterate ascending."),
        _sk("Subset-sum reachability",
            "Equal partition, closest split.",
            """
boolean[] can = new boolean[half + 1];
can[0] = true;
for (int x : nums)
    for (int s = half; s >= x; s--)
        can[s] |= can[s - x];
// equal partition: can[half];  closest split: the largest s with can[s]
""",
            "Odd totals cannot split equally — return before allocating anything."),
    ],
    traces=[
        _trace(
            "One item (weight 2, value 3), capacity 4 — descending versus ascending",
            "Start from `best = [0, 0, 0, 0, 0]` and apply the single item once. Both loops "
            "compute `best[c] = max(best[c], best[c − 2] + 3)`; the only difference is which "
            "`best[c − 2]` they read. Rows are listed in each loop's own order.",
            ["Order", "c", "reads best[c − 2]", "best[c] becomes", "best[] after"],
            [
                ["descending", "4", "best[2] = 0 (untouched)", "3", "[0, 0, 0, 0, 3]"],
                ["descending", "3", "best[1] = 0", "3", "[0, 0, 0, 3, 3]"],
                ["descending", "2", "best[0] = 0", "3", "[0, 0, 3, 3, 3]"],
                ["ascending", "2", "best[0] = 0", "3", "[0, 0, 3, 0, 0]"],
                ["ascending", "3", "best[1] = 0", "3", "[0, 0, 3, 3, 0]"],
                ["ascending", "4", "best[2] = **3** (already includes the item)", "**6**", "[0, 0, 3, 3, **6**]"],
            ],
            "With one item worth 3 the true best is 3. Ascending reports 6 because by the "
            "time it reaches capacity 4, capacity 2 has *already* taken the item — so it is "
            "taken again. That is correct for coins and wrong for a bag: the loop direction "
            "is the problem statement.",
        ),
        _trace(
            "Coin change table for coins {1, 3, 4}, amount 6 — every last coin",
            "`dp[a]` = fewest coins making exactly `a`. One column per coin, because the "
            "recurrence considers *every* possible last coin rather than committing to "
            "one. This is the table the greedy algorithm refuses to build.",
            ["a", "last = 1 → dp[a−1]+1", "last = 3 → dp[a−3]+1", "last = 4 → dp[a−4]+1", "dp[a]"],
            [
                ["1", "dp[0]+1 = **1**", "—", "—", "**1**"],
                ["2", "dp[1]+1 = **2**", "—", "—", "**2**"],
                ["3", "dp[2]+1 = 3", "dp[0]+1 = **1**", "—", "**1**"],
                ["4", "dp[3]+1 = 2", "dp[1]+1 = 2", "dp[0]+1 = **1**", "**1**"],
                ["5", "dp[4]+1 = **2**", "dp[2]+1 = 3", "dp[1]+1 = **2**", "**2**"],
                ["6", "dp[5]+1 = 3", "dp[3]+1 = **2**", "dp[2]+1 = 3", "**2**"],
            ],
            "`dp[6] = 2`, via 3 + 3. Greedy takes the 4 first and finishes at three coins, "
            "because it committed to a last coin it could not reconsider. The cost of the "
            "table is exactly the price of that reconsideration: O(amount × coins) instead "
            "of O(coins log coins), for an answer that is actually right.",
        ),
    ],
    costs=[
        _cost("0/1 knapsack, rolled", "O(n · W)", "O(W)", "Pseudo-polynomial in the capacity."),
        _cost("Coin change", "O(amount × coins)", "O(amount)", "Pseudo-polynomial."),
        _cost("Counting subsets mod p", "O(n · target)", "O(target)", "One addition and one `%` per cell."),
        _cost("Trying every subset", "O(2ⁿ · n)", "O(n)", "What the table replaces — and what wins when W is huge."),
        _cost("Perfect squares", "O(n √n)", "O(n)", "Unbounded knapsack over the √n squares."),
    ],
    pitfalls=[
        _pit("Each item is used more than once in a 0/1 knapsack",
             "The capacity loop ran ascending, so an item could be re-consumed in its own pass.",
             "Iterate capacity **descending** for 0/1; ascending is the unbounded case."),
        _pit("A counting DP returns 0 for everything",
             "The base case `ways[0]` was left at 0.",
             "`ways[0] = 1`: one way to reach zero — take nothing."),
        _pit("Coin combinations are counted as orderings (or vice versa)",
             "The loops were nested the wrong way round.",
             "Coins outside counts sets; amounts outside counts sequences. Decide which the problem wants."),
        _pit("The “minimum” answer comes back as a huge number",
             "An infinity sentinel was added to and never guarded.",
             "Use `amount + 1` as infinity, or check for the sentinel before adding."),
        _pit("A count is wrong only on big inputs",
             "The additions were not reduced modulo p and overflowed.",
             "`% MOD` after every addition."),
        _pit("Target-sum with signs gives wrong answers for some targets",
             "`(total + target)` was odd or negative, and the division silently rounded.",
             "Return 0 when `total + target` is odd or `|target| > total`, before building the table."),
    ],
    lessons=["dp", "dp2d", "modulo"],
    checks=[
        _chk("What changes between unbounded and 0/1 knapsack?",
             "Only the inner loop direction. Ascending capacity allows an item to be reused "
             "within its own pass (unbounded); descending prevents it (0/1)."),
        _chk("How does a counting DP differ from an optimising one?",
             "It sums the transitions instead of taking a max or min, and the base case is 1 "
             "— there is exactly one way to do nothing."),
        _chk("Coin combinations versus coin sequences — what decides which one you count?",
             "The loop nesting. Coins outside, amounts inside counts each multiset once; "
             "amounts outside, coins inside counts every ordering separately."),
        _chk("How does \"split the array into two groups with equal sums\" become a knapsack?",
             "Each group must sum to total / 2, so ask whether some subset reaches exactly that "
             "— after rejecting an odd total."),
        _chk("Why is knapsack DP called pseudo-polynomial?",
             "It is O(n · W): polynomial in the *value* W, but W can need only 30 bits to write. "
             "When W is 10⁹ the table cannot be built at all."),
    ],
    bigo=[
        _bigo(r"""
int[] dp = new int[n + 1];                // perfect squares: fewest squares summing to n
Arrays.fill(dp, Integer.MAX_VALUE);
dp[0] = 0;
for (int s = 1; s * s <= n; s++)
    for (int a = s * s; a <= n; a++)
        dp[a] = Math.min(dp[a], dp[a - s * s] + 1);
""", "O(n√n)", ["O(n√n)", "O(n²)", "O(n log n)", "O(√n)"],
            "√n squares, each swept over n amounts. An unbounded knapsack whose \"coins\" are the "
            "squares."),
        _bigo(r"""
long[] ways = new long[k + 1];            // n numbers, target k
ways[0] = 1;
for (int x : a)
    for (int s = k; s >= x; s--)
        ways[s] = (ways[s] + ways[s - x]) % MOD;
""", "O(n·k)", ["O(n·k)", "O(2ⁿ)", "O(n + k)", "O(n·k·log k)"],
            "n passes over at most k sums, O(1) each — the `%` does not change the class. The "
            "answer can be astronomically large; the work stays n·k."),
    ],
    interview="""
Name the family before the code: "each item is used at most once and there is a
capacity, so it is a 0/1 knapsack over the capacity — iterating capacity
downwards". The loop direction is the question interviewers most often ask
about, so volunteer why it is descending. For counting variants, say the base
case out loud (one way to make zero) and reduce modulo p on every addition.
""",
    rungs=[
        _rung("Warm up", "The 0/1 knapsack itself, with small numbers.",
              ["knapsack-01-max-value"],
              {"knapsack-01-max-value": "Write the 2-D table first, then roll it into one array iterating capacity downwards — and check the example greedy gets wrong."}),
        _rung("Core", "Reuse allowed, counting, and the first disguise.", []),
        _rung("Variations", "Subsets that must hit a sum exactly — counted, split, or reached.",
              ["count-subsets-sum-k"],
              {"count-subsets-sum-k": "The 0/1 loop with `+` instead of `max`, base case 1, and a `% MOD` on every addition."}),
    ],
    next_up="""
Knapsack tables index items and capacity. The next unit indexes two *sequences* —
or two coordinates of a grid — where the same four steps build diff tools and
spell-checkers.
""",
)


# --- Unit 33 — 2-D dynamic programming ---------------------------------------

_unit(
    "dp-2d", "Dynamic Programming III: Grids & Two Sequences", "🗺️", _S7,
    "Two indices, a table, and a fill order that respects the recurrence.",
    weight=2,
    prereqs=["dp-1d", "simulation-and-matrix"],
    why="""
The step from 1-D to 2-D is smaller than it looks: the procedure is identical,
and only the state gains an index. What changes is that the fill order now
matters in two directions at once, and that most of these problems compare **two
sequences** — where the recurrence always has the same shape.

Edit distance and longest common subsequence are worth real time. They are the
templates for a whole family (diff tools, spell-checkers, DNA alignment), they
are asked constantly, and once one of them is genuinely understood the others
fall out as small variations.
""",
    model="""
### Two sequences: the universal shape

`dp[i][j]` = the answer for the first i characters of `a` and the first j of
`b`. Then:

```java
if (a.charAt(i - 1) == b.charAt(j - 1))
    dp[i][j] = dp[i - 1][j - 1] + 1;                  // characters match
else
    dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);  // drop one from either
```

That is longest common subsequence. Edit distance is the same table with a
different else-branch — the three operations, each costing one:

```java
dp[i][j] = 1 + Math.min(dp[i - 1][j - 1],       // replace
                Math.min(dp[i - 1][j],          // delete from a
                         dp[i][j - 1]));        // insert into a
```

**Use 1-based indices for the table and 0-based for the strings.** `dp[0][j]`
and `dp[i][0]` are then the empty-prefix base cases, which for edit distance are
`i` and `j` — deleting everything. That offset removes every boundary special
case, and the `- 1` in the character access is the price.

### Grid DP

`dp[i][j]` = the answer for the cell `(i, j)`, built from the cells you are
allowed to arrive from:

```java
dp[i][j] = dp[i - 1][j] + dp[i][j - 1];        // paths from above and from the left
```

The first row and column are the base cases. Fill top-to-bottom, left-to-right,
and every entry read is already done.

### Not every two-index table is this unit

A table indexed by **(item, capacity)** is the knapsack family, from the previous
unit. A table indexed by **(start, end)** of one string — palindromes, burst
balloons — must be filled by length, and is the next unit. Both have two indices;
what they remember is different, and so is the fill order.

### When the table is too big

Longest increasing subsequence has an O(n²) DP — for each i, scan every j < i —
but also an O(n log n) solution: keep the smallest possible tail for each length
and binary-search the position of each new element. The array is **not** the
subsequence; it only gives the correct length. That is the pattern to know:
sometimes a DP is replaced by a cleverer structure rather than optimised.

### Rolling to one row

If `dp[i][*]` only reads `dp[i-1][*]`, keep two rows — or one, if the reads go
in a direction that does not clobber what you still need. Same advice as in 1-D:
correctness first, space second.
""",
    signals=[
        _sig("“two strings”, “common”, “transform into”", "`dp[i][j]` over both prefixes",
             "LCS and edit distance are the same table."),
        _sig("“paths on a grid”, “only right and down”", "`dp[i][j]` from above and left",
             "The first row and column are the base cases."),
        _sig("“longest increasing subsequence”", "O(n²) DP, or O(n log n) tails + binary search",
             "Know both, and that the tails array is not the answer itself."),
        _sig("Two things vary independently", "Two dimensions",
             "One index per independent quantity — that is what makes it 2-D."),
    ],
    skeletons=[
        _sk("Two-sequence table (LCS)",
            "Common subsequence, diff, alignment.",
            """
int[][] dp = new int[n + 1][m + 1];          // 1-based table, 0-based strings
for (int i = 1; i <= n; i++)
    for (int j = 1; j <= m; j++)
        dp[i][j] = (a.charAt(i - 1) == b.charAt(j - 1))
                 ? dp[i - 1][j - 1] + 1
                 : Math.max(dp[i - 1][j], dp[i][j - 1]);
return dp[n][m];
""",
            "Row 0 and column 0 stay 0 — the empty-prefix base case, for free."),
        _sk("Edit distance",
            "Levenshtein; the same table with three operations.",
            """
for (int i = 0; i <= n; i++) dp[i][0] = i;      // delete everything
for (int j = 0; j <= m; j++) dp[0][j] = j;      // insert everything
for (int i = 1; i <= n; i++)
    for (int j = 1; j <= m; j++)
        dp[i][j] = (a.charAt(i-1) == b.charAt(j-1))
                 ? dp[i-1][j-1]
                 : 1 + Math.min(dp[i-1][j-1], Math.min(dp[i-1][j], dp[i][j-1]));
""",
            "The three neighbours are replace, delete and insert — name them when explaining."),
        _sk("LIS in O(n log n)",
            "Longest increasing subsequence, when O(n²) is too slow.",
            """
List<Integer> tails = new ArrayList<>();
for (int x : a) {
    int pos = lowerBound(tails, x);          // first tail >= x
    if (pos == tails.size()) tails.add(x);
    else tails.set(pos, x);
}
return tails.size();                         // the LENGTH, not the subsequence
""",
            "`tails` is not a valid subsequence — only its size is meaningful."),
    ],
    costs=[
        _cost("Two-sequence DP", "O(n · m)", "O(n · m) → O(min(n,m)) rolled", "LCS, edit distance."),
        _cost("Grid DP", "O(rows · cols)", "O(cols) rolled", "One row at a time."),
        _cost("LIS", "O(n²) or O(n log n)", "O(n)", "Tails array plus binary search."),
    ],
    pitfalls=[
        _pit("`ArrayIndexOutOfBoundsException` on the first row or column",
             "The table is 1-based but the string access forgot the `- 1`, or the table was "
             "sized `n` instead of `n + 1`.",
             "Size `n + 1` by `m + 1`, and access `charAt(i - 1)`."),
        _pit("Edit distance returns 0 for two different strings",
             "The base cases were left as zeros instead of `i` and `j`.",
             "`dp[i][0] = i` and `dp[0][j] = j` — converting to or from an empty string costs "
             "one operation per character."),
        _pit("The LIS tails array is reported as the subsequence",
             "It is a per-length minimum tail, not a real subsequence.",
             "Only its length is the answer; reconstructing the sequence needs predecessor "
             "links."),
        _pit("`MemoryLimitExceeded` on a large two-sequence DP",
             "The full n × m table was allocated when only two rows are ever read.",
             "Roll to two rows — but only once the full version is correct."),
    ],
    lessons=["dp2d", "dp", "binary_search"],
    checks=[
        _chk("What do LCS and edit distance have in common?",
             "The same `dp[i][j]` over prefixes of two strings and the same match case. Only "
             "the mismatch branch differs: a max of two neighbours versus 1 + a min of three."),
        _chk("Why use a 1-based table with 0-based strings?",
             "Row 0 and column 0 then represent the empty prefixes, which are the base cases. "
             "Every boundary special case disappears; the cost is the `- 1` in `charAt`."),
        _chk("What does the LIS tails array actually contain?",
             "For each length, the smallest possible final value of an increasing "
             "subsequence of that length. Its size is the LIS length, but its contents are "
             "not necessarily a subsequence of the input."),
        _chk("LCS and edit distance both read `dp[i-1][j-1]`. Why can a rolled version not "
             "simply overwrite one row left to right?",
             "By the time `dp[j]` is written, `dp[j-1]` already holds the new row's value, but "
             "the diagonal needs the old one. Save it in a variable before overwriting."),
    ],
    interview="""
Two-sequence DP is asked constantly and is one of the few places where being
able to *draw the table* wins the interview. Fill a 3×3 example by hand while
explaining the three neighbours as replace, delete and insert; it takes ninety
seconds and it proves the recurrence in a way that code cannot. Offer the
rolled-row space optimisation at the end, after the table is right.
""",
    traces=[
        _trace(
            "Grid paths, one row at a time, on a 3 × 4 grid",
            "`dp[i][j]` = routes from the top-left to `(i, j)` moving only right or down. "
            "Each cell reads the one above and the one to the left, which is what makes "
            "row-by-row a legal fill order — and diagonal-outward not.",
            ["Row", "j = 0", "j = 1", "j = 2", "j = 3", "Rule in play"],
            [
                ["i = 0", "**1**", "0 + 1 = **1**", "0 + 1 = **1**", "0 + 1 = **1**",
                 "nothing above; only from the left"],
                ["i = 1", "1 + 0 = **1**", "1 + 1 = **2**", "1 + 2 = **3**", "1 + 3 = **4**",
                 "above + left"],
                ["i = 2", "1 + 0 = **1**", "1 + 2 = **3**", "3 + 3 = **6**", "4 + 6 = **10**",
                 "above + left"],
            ],
            "The first row and column come out all 1s with no special case, because the "
            "missing term contributes 0. And notice what row `i = 2` reads: only row "
            "`i = 1` and the cell to its own left — so if you only want the final number, "
            "**one row of storage is enough** and the O(H·W) space collapses to O(W).",
        ),
        _trace(
            "Reading the table BACKWARDS: recovering the LCS of \"ABC\" and \"BC\"",
            "The length was one cell. The *answer* is a walk back through the whole table "
            "from the bottom-right, and this is the half that gets skipped — which is why "
            "\"how long is it?\" and \"which one is it?\" need different amounts of memory.",
            ["At (i, j)", "s[i−1], t[j−1]", "dp[i][j]", "Move", "Subsequence so far"],
            [
                ["(3, 2)", "C, C", "2", "match → take it, go to (2, 1)", "C"],
                ["(2, 1)", "B, B", "1", "match → take it, go to (1, 0)", "BC"],
                ["(1, 0)", "A, —", "0", "j = 0 → stop", "**BC**"],
            ],
            "Built backwards, so reverse it at the end. When the characters do *not* "
            "match you step toward whichever of `dp[i-1][j]` / `dp[i][j-1]` the value came "
            "from — that is the same comparison the forward pass made, replayed. The "
            "consequence for space is concrete: the one-row trick works for the length and "
            "is useless for reconstruction, because the walk needs cells the row-reuse "
            "already overwrote.",
        ),
    ],
    rungs=[
        _rung("Warm up", "The same table, with the fill order made visible.",
              ["grid-paths-table"],
              {"grid-paths-table": "No obstacles, so the only new idea over 1-D is which orders are legal. Then read the printed table backwards and reconstruct an actual path."}),
        _rung("Core", "A table filled from two directions.",
              ["unique-paths"],
              {"unique-paths": "The gentlest 2-D problem: base row and column of ones, then sum from above and left."}),
        _rung("Variations", "Two sequences, one table.",
              ["longest-common-subsequence"],
              {"longest-common-subsequence": "Learn this one properly — edit distance is the same table with a different mismatch branch."}),
        _rung("Stretch", "Harder base cases, and a structural alternative to the table.",
              ["edit-distance", "longest-increasing-subsequence"],
              {"edit-distance": "Draw a 3×3 table by hand before coding. The base cases are `i` and `j`, not zeros.",
               "longest-increasing-subsequence": "Do the O(n²) DP first, then the O(n log n) tails version — and be clear about what the tails array is not."}),
    ],
    next_up="""
Two more shapes of state are left: a range of one sequence that must be solved
from the inside out, and a small machine whose situation changes each step.
""",
)


# --- Unit 34 — Intervals and state machines ----------------------------------

_unit(
    "dp-intervals-states", "Dynamic Programming IV: Intervals & State Machines", "🎛️", _S7,
    "Solve a range from the inside out, or track which situation you are in.",
    weight=2,
    prereqs=["dp-2d"],
    why="""
Two DP shapes do not fit a left-to-right scan, and both are common enough to
deserve their own rung.

**Interval DP.** Some problems can only be split *inside* a range: which balloon
bursts last, which triangle sits on a polygon edge, whether the two ends of a
string match. The state is a range `[i, j]`, the answer for a range is built
from strictly shorter ranges, and so the table has to be filled **by length** —
the only order that guarantees both halves are ready.

**State-machine DP.** Some problems are a sequence of days or steps where what
you are *allowed* to do depends on your situation: holding a share or not, just
sold or free to buy. The state is the step plus the situation, each situation has
a handful of transitions, and a rule change — a fee, a cooldown — is a change to
one arrow rather than a new algorithm.
""",
    model="""
### Interval DP: choose the split, fill by length

The state `dp[i][j]` is the answer for the range `i..j`. The transition picks
something that **must exist** inside the range and splits around it:

```java
for (int len = 2; len < n; len++)                   // shortest ranges first
    for (int i = 0; i + len < n; i++) {
        int j = i + len;
        dp[i][j] = INF;
        for (int k = i + 1; k < j; k++)             // the piece that must exist
            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + cost(i, k, j));
    }
```

What "must exist" means is the whole problem:

| Problem | The chosen k is … |
| --- | --- |
| Triangulate a polygon | the third vertex of the triangle on edge (i, j) |
| Burst balloons | the **last** balloon burst in (i, j) — so its neighbours are i and j |
| Merge adjacent piles | the split point of the final merge |
| Palindromic subsequence | no k: compare the two ends, shrink by one |

Choosing the *last* balloon rather than the first is what makes the halves
independent: the first burst changes both halves' neighbours, the last changes
neither.

### Palindromes are interval DP too

`lps[i][j]` = the longest palindromic subsequence of `s[i..j]`:

```java
if (s.charAt(i) == s.charAt(j)) lps[i][j] = lps[i + 1][j - 1] + 2;
else lps[i][j] = Math.max(lps[i + 1][j], lps[i][j - 1]);
```

It reads a shorter range, so it is filled by length. "Fewest insertions to make a
palindrome" is `n − lps[0][n−1]`.

### Two-player games on a range

"Players take from either end; can the first player win?" is interval DP where
`dp[i][j]` is the best *score difference* the player to move can force on `i..j`:
`max(a[i] − dp[i+1][j], a[j] − dp[i][j−1])`. Subtracting the opponent's best is
what encodes the alternating turns.

### State machines: the situation is the state

Buying and selling a stock with at most one share:

```java
long free = 0, hold = Long.MIN_VALUE / 2;
for (int p : prices) {
    long prevFree = free;
    free = Math.max(free, hold + p);                // rest, or sell
    hold = Math.max(hold, prevFree - p);            // rest, or buy
}
```

Draw the machine first — circles for situations, arrows for actions, a price on
each arrow — and the code is one line per arrow. Rule changes are arrow changes:

| Rule | Change |
| --- | --- |
| A fee per trade | subtract it on the sell arrow |
| A one-day cooldown after selling | a third state, "just sold", that can only rest |
| At most k trades | one pair of states per trade count |

Use yesterday's values on the right-hand side (hence `prevFree`). Updating in
place lets a sale and a purchase happen on the same step, which some rules
forbid.
""",
    signals=[
        _sig("“burst / merge / remove, and the cost depends on the neighbours”", "Interval DP; choose the LAST action",
             "The last one in a range sees the range's fixed boundaries."),
        _sig("“palindromic subsequence”, “fewest insertions to make a palindrome”", "`dp[i][j]` over the ends, by length",
             "Match the ends, or drop one of them."),
        _sig("“both players play optimally, taking from either end”", "Interval DP on the score difference",
             "`max(a[i] − dp[i+1][j], a[j] − dp[i][j−1])`."),
        _sig("“triangulate”, “matrix chain”, “split into parts at a cost”", "Try every split point k in (i, j)",
             "O(n³) — n ≤ a few hundred is the hint."),
        _sig("“buy and sell”, “cooldown”, “fee”, “at most k transactions”", "State-machine DP",
             "Holding / not holding (/ just sold), updated per day."),
        _sig("What you may do depends on what you just did", "Add the situation to the state",
             "One variable per situation; one transition per allowed action."),
    ],
    skeletons=[
        _sk("Interval DP by length",
            "Triangulation, burst balloons, merging piles.",
            """
long[][] dp = new long[n][n];                 // dp[i][i+1] = 0 base cases
for (int len = 2; len < n; len++)
    for (int i = 0; i + len < n; i++) {
        int j = i + len;
        dp[i][j] = Long.MAX_VALUE;
        for (int k = i + 1; k < j; k++)
            dp[i][j] = Math.min(dp[i][j], dp[i][k] + dp[k][j] + cost(i, k, j));
    }
return dp[0][n - 1];
""",
            "Fill by increasing length — `i` and `j` in plain nested order read unfilled cells."),
        _sk("Longest palindromic subsequence",
            "Palindromic subsequences, fewest insertions or deletions.",
            """
int[][] lps = new int[n][n];
for (int i = n - 1; i >= 0; i--) {            // i descending, j ascending: also a valid order
    lps[i][i] = 1;
    for (int j = i + 1; j < n; j++)
        lps[i][j] = s.charAt(i) == s.charAt(j)
                  ? lps[i + 1][j - 1] + 2
                  : Math.max(lps[i + 1][j], lps[i][j - 1]);
}
return lps[0][n - 1];
""",
            "Any order where `i+1` is done before `i` and `j−1` before `j` works; by length is the one that always does."),
        _sk("Stock state machine",
            "Buy/sell with fees, cooldowns, or a transaction limit.",
            """
long free = 0, hold = -prices[0], sold = Long.MIN_VALUE / 2;   // sold: only for cooldown
for (int i = 1; i < n; i++) {
    long f = free, h = hold, s = sold;
    free = Math.max(f, s);                    // rest, or finish a cooldown
    hold = Math.max(h, f - prices[i]);        // keep, or buy
    sold = h + prices[i];                     // sell today (subtract a fee here)
}
return Math.max(free, sold);
""",
            "Copy yesterday's values first; every right-hand side reads them."),
    ],
    traces=[
        _trace(
            "Two-state machine on prices [3, 8, 2, 6, 9, 4]",
            "`free` = best cash while not holding, `hold` = best cash while holding one share. "
            "Each day both are rebuilt from yesterday's pair: rest, sell (free), or buy (hold).",
            ["Day", "Price", "free = max(free, hold + p)", "hold = max(hold, free − p)", "free", "hold"],
            [
                ["0", "3", "max(0, −∞) = 0", "max(−∞, 0 − 3) = −3", "0", "−3"],
                ["1", "8", "max(0, −3 + 8) = **5**", "max(−3, 0 − 8) = −3", "5", "−3"],
                ["2", "2", "max(5, −3 + 2) = 5", "max(−3, 5 − 2) = **3**", "5", "3"],
                ["3", "6", "max(5, 3 + 6) = **9**", "max(3, 5 − 6) = 3", "9", "3"],
                ["4", "9", "max(9, 3 + 9) = **12**", "max(3, 9 − 9) = 3", "12", "3"],
                ["5", "4", "max(12, 3 + 4) = 12", "max(3, 12 − 4) = **8**", "12", "8"],
            ],
            "Day 3 sells at 6 for 9, and day 4 then does better *from the same hold of 3*: "
            "the machine never had to decide whether day 3's sale was final, because `hold` "
            "kept the bought-at-2 option alive. That is what a greedy seller cannot do once a "
            "fee makes each sale cost something.",
        ),
        _trace(
            "Triangulating values [4, 1, 5, 2] — filled by length",
            "`dp[i][j]` = cheapest triangulation of vertices i..j. A triangle scores the product "
            "of its vertices; each range tries every third vertex k strictly between i and j.",
            ["Range", "k tried", "dp[i][k] + dp[k][j] + v[i]·v[k]·v[j]", "dp[i][j]"],
            [
                ["[0, 2]", "1", "0 + 0 + 4·1·5 = 20", "**20**"],
                ["[1, 3]", "2", "0 + 0 + 1·5·2 = 10", "**10**"],
                ["[0, 3]", "1", "dp[0][1] + dp[1][3] + 4·1·2 = 0 + 10 + 8 = **18**", "—"],
                ["[0, 3]", "2", "dp[0][2] + dp[2][3] + 4·5·2 = 20 + 0 + 40 = 60", "**18**"],
            ],
            "Both length-2 ranges were finished before `[0, 3]` read them — the reason for "
            "filling by length. The choice of k is the triangle sitting on edge (0, 3): with "
            "vertex 1 it scores 8 and leaves the cheap range [1, 3]; with vertex 2 it scores 40.",
        ),
    ],
    costs=[
        _cost("Interval DP with a split loop", "O(n³)", "O(n²)", "n² ranges × n split points."),
        _cost("Interval DP, ends only", "O(n²)", "O(n²)", "Palindromic subsequence, end-taking games."),
        _cost("State machine, s states", "O(n · s)", "O(s)", "Rolled to a few variables."),
        _cost("At most k transactions", "O(n · k)", "O(k)", "Two states per transaction count."),
        _cost("Trying every split order", "O(Catalan(n)) ≈ O(4ⁿ)", "O(n)", "What the table replaces."),
    ],
    pitfalls=[
        _pit("Interval DP reads cells that are still zero",
             "The loops iterated `i` then `j` in plain order while the recurrence reads shorter ranges.",
             "Loop on length outermost (or `i` descending with `j` ascending)."),
        _pit("Burst balloons gives the wrong answer with the right recurrence shape",
             "k was chosen as the *first* balloon burst, so the halves' neighbours depend on each other.",
             "Choose the *last* balloon in (i, j); pad the array with 1s at both ends."),
        _pit("A game DP reports a total instead of who wins",
             "It summed the current player's picks and ignored the opponent's replies.",
             "Store the score *difference* for the player to move, and subtract the sub-result."),
        _pit("A stock machine sells and buys on the same day when it should not",
             "States were updated in place, so the new `free` fed the new `hold`.",
             "Copy yesterday's values before computing today's."),
        _pit("Cooldown DP allows buying the day after a sale",
             "Only two states were kept, so \"just sold\" and \"free\" were merged.",
             "Add the third state; from \"just sold\" the only move is to rest into \"free\"."),
    ],
    lessons=["dp2d", "dp", "recurrence"],
    checks=[
        _chk("Why must interval DP be filled by increasing length?",
             "`dp[i][j]` depends on strictly shorter ranges inside it, so all of them must "
             "already be computed."),
        _chk("In burst balloons, why choose the last balloon rather than the first?",
             "The last balloon in (i, j) bursts with i and j as its neighbours — fixed "
             "boundaries — so the two sides are independent subproblems. The first one's "
             "removal changes both sides' neighbours."),
        _chk("How is \"fewest insertions to make a string a palindrome\" solved?",
             "`n − (longest palindromic subsequence)`: every character not in that subsequence "
             "needs a partner inserted."),
        _chk("How does a transaction fee change the stock state machine?",
             "Only the sell transition: `free = max(free, hold + price − fee)`. The states and "
             "every other arrow stay the same."),
        _chk("Why does a cooldown need a third state?",
             "After selling you may not buy tomorrow, so \"not holding\" splits into \"just "
             "sold\" (can only rest) and \"free\" (may buy)."),
    ],
    bigo=[
        _bigo(r"""
for (int i = n - 1; i >= 0; i--)          // longest palindromic subsequence
    for (int j = i + 1; j < n; j++)
        lps[i][j] = s.charAt(i) == s.charAt(j) ? lps[i + 1][j - 1] + 2
                                               : Math.max(lps[i + 1][j], lps[i][j - 1]);
""", "O(n²)", ["O(n²)", "O(n³)", "O(2ⁿ)", "O(n log n)"],
            "n²/2 ranges, O(1) each, because the transition only looks at the ends. Interval DP "
            "is O(n³) only when it has to try a split point."),
        _bigo(r"""
long free = 0, hold = -p[0], sold = Long.MIN_VALUE / 2;   // n days
for (int i = 1; i < n; i++) {
    long f = free, h = hold, s = sold;
    free = Math.max(f, s); hold = Math.max(h, f - p[i]); sold = h + p[i];
}
""", "O(n)", ["O(n)", "O(n²)", "O(3ⁿ)", "O(n log n)"],
            "Three states, O(1) transitions, n days — O(n) time and O(1) space. Enumerating "
            "every buy/sell/rest sequence would be 3ⁿ."),
        _bigo(r"""
int best(int i, int j) {                  // NO memo; players take from either end
    if (i > j) return 0;
    return Math.max(a[i] - best(i + 1, j), a[j] - best(i, j - 1));
}
""", "O(2ⁿ)", ["O(2ⁿ)", "O(n²)", "O(n)", "O(n!)"],
            "Two calls per level, n levels deep. There are only n² distinct (i, j) pairs, so a "
            "memo table turns it into O(n²)."),
    ],
    interview="""
For interval DP, say what the state range means and which element you are
choosing inside it — "k is the last balloon burst in (i, j), so its neighbours
are i and j" — then say "filled by length" before writing a loop; it is the part
people get wrong. For stock-style problems, draw the machine on the whiteboard
first. An interviewer can check three circles and five arrows in ten seconds,
and the code is then one line per arrow.
""",
    rungs=[
        _rung("Warm up", "A two-state machine, with nothing in the way.",
              ["stock-buy-sell-unlimited"],
              {"stock-buy-sell-unlimited": "Draw holding / not holding, write one line per arrow. Then compare with summing every rise — and ask what a fee would break."}),
        _rung("Core", "Machines with one extra rule, and ranges split around a chosen piece.",
              ["stock-with-fee", "min-score-triangulation"],
              {"stock-with-fee": "The same machine with a cost on the sell arrow. Greedy fails here; find the counterexample in the statement.",
               "min-score-triangulation": "The triangle on edge (i, j) needs a third vertex k. Fill by length, and trace the four-vertex example by hand first."}),
        _rung("Stretch", "Choosing the last action in a range, and ends that must match.", []),
    ],
    next_up="""
Four shapes of state, one procedure. The next unit turns from computing to
indexing: a tree whose paths are prefixes, so every prefix question is a walk.
""",
)


# --- Unit 35 — Tries ---------------------------------------------------------

_unit(
    "tries", "Tries (Prefix Trees)", "🌴", _S7,
    "When the structure of the key is the structure of the index.",
    weight=2,
    prereqs=["trees", "strings"],
    why="""
A hash map answers *"is this exact key present?"*. It cannot answer *"how many
keys start with `pre`?"*, because hashing deliberately destroys the relationship
between similar keys. A trie keeps it: the path from the root spells the key, so
every prefix is a node and prefix questions become a walk.

It is the final unit because it makes the curriculum's closing point — that
choosing the right structure *is* the algorithm. Autocomplete, dictionary
lookup, wildcard matching and even maximum-XOR (a trie over bits) are all the
same fifteen lines with a different walk.
""",
    model="""
### The node

```java
class Node {
    Node[] next = new Node[26];    // one slot per letter
    boolean word;                  // does a key END here?
    int count;                     // how many keys pass through (for prefix counts)
}
```

The `word` flag is essential: without it, inserting "car" would make "ca" appear
to be a stored word. A node marks *a place in the tree*, not necessarily a key.

### Insert and search

```java
void insert(String s) {
    Node cur = root;
    for (char c : s.toCharArray()) {
        int i = c - 'a';
        if (cur.next[i] == null) cur.next[i] = new Node();
        cur = cur.next[i];
        cur.count++;                       // keys passing through this prefix
    }
    cur.word = true;
}

boolean search(String s, boolean prefixOnly) {
    Node cur = root;
    for (char c : s.toCharArray()) {
        cur = cur.next[c - 'a'];
        if (cur == null) return false;
    }
    return prefixOnly || cur.word;         // the ONLY difference between the two
}
```

Both are O(length of the key) — **independent of how many keys are stored**.
That is the headline property: a million words do not slow a lookup down.

### Wildcards need backtracking

`.` matching any character turns the walk into a search: at a `.`, recurse into
every non-null child. Worst case O(26^dots), which is why these problems bound
the number of wildcards.

```java
boolean match(String s, int i, Node cur) {
    if (cur == null) return false;
    if (i == s.length()) return cur.word;
    char c = s.charAt(i);
    if (c != '.') return match(s, i + 1, cur.next[c - 'a']);
    for (Node child : cur.next)
        if (match(s, i + 1, child)) return true;
    return false;
}
```

### The bit trie

Replace 26 children with 2 and insert the bits of each number from the most
significant down. To maximise `x XOR y`, walk the trie taking the **opposite**
bit of x wherever it exists — each opposite bit taken contributes 2ᵏ, and the
higher bits dominate, so the greedy walk is optimal. That gives O(32n) for the
maximum XOR pair instead of O(n²).

It is a fair summary of the whole curriculum: a greedy walk (stage 3) over a
tree (stage 6) indexed by bits (stage 4).

### Trie or hash map?

| Need | Use |
| --- | --- |
| Exact lookup only | Hash map — less memory, simpler |
| Prefix counting, autocomplete | Trie |
| Wildcards inside the key | Trie |
| Longest matching prefix (routing, roots) | Trie |
| Maximum XOR pair | Bit trie |

A trie costs up to 26 pointers per node, which is substantial. Use a
`Map<Character, Node>` when the alphabet is large or sparse.
""",
    signals=[
        _sig("“words starting with …”, “autocomplete”", "Trie",
             "Prefix questions are what a hash map cannot answer."),
        _sig("“insert and search a dictionary”", "Trie with a `word` flag",
             "The flag distinguishes a key from a mere prefix."),
        _sig("“`.` matches any character”", "Trie + backtracking",
             "Recurse into every child at a wildcard."),
        _sig("“replace words by their root”", "Trie, stop at the first `word` node",
             "The shortest matching prefix is the first flag you meet."),
        _sig("“longest word built one letter at a time”", "Trie, only descend through `word` nodes",
             "Every prefix must itself be a key."),
        _sig("“maximum XOR of any pair”", "Bit trie, greedy opposite bits",
             "O(32n) instead of O(n²)."),
    ],
    skeletons=[
        _sk("The trie",
            "Insert, search, and prefix search — the whole structure.",
            """
class Node { Node[] next = new Node[26]; boolean word; int count; }
Node root = new Node();

void insert(String s) {
    Node cur = root;
    for (char c : s.toCharArray()) {
        int i = c - 'a';
        if (cur.next[i] == null) cur.next[i] = new Node();
        cur = cur.next[i];
        cur.count++;
    }
    cur.word = true;
}

Node walk(String s) {                      // null if the path does not exist
    Node cur = root;
    for (char c : s.toCharArray()) {
        cur = cur.next[c - 'a'];
        if (cur == null) return null;
    }
    return cur;
}
// contains(s)      : walk(s) != null && walk(s).word
// startsWith(p)    : walk(p) != null
// countPrefix(p)   : walk(p) == null ? 0 : walk(p).count
""",
            "One walk, three questions — the difference is only what you read at the end."),
        _sk("Wildcard search",
            "`.` matching any single character.",
            """
boolean match(String s, int i, Node cur) {
    if (cur == null) return false;
    if (i == s.length()) return cur.word;
    char c = s.charAt(i);
    if (c != '.') return match(s, i + 1, cur.next[c - 'a']);
    for (Node child : cur.next) if (match(s, i + 1, child)) return true;
    return false;
}
""",
            "The wildcard branch is the only place the walk becomes a search."),
        _sk("Shortest matching root",
            "Replace words by their dictionary root.",
            """
String rootOf(String w) {
    Node cur = root;
    StringBuilder sb = new StringBuilder();
    for (char c : w.toCharArray()) {
        cur = cur.next[c - 'a'];
        if (cur == null) return w;         // no root exists
        sb.append(c);
        if (cur.word) return sb.toString();  // the SHORTEST root wins
    }
    return w;
}
""",
            "Returning at the first `word` node is what makes it the shortest root."),
        _sk("Bit trie for maximum XOR",
            "Maximum XOR pair, in O(32n).",
            """
void insert(int x) {
    Node cur = root;
    for (int b = 31; b >= 0; b--) {
        int bit = (x >> b) & 1;
        if (cur.child[bit] == null) cur.child[bit] = new Node();
        cur = cur.child[bit];
    }
}

int best(int x) {
    Node cur = root; int res = 0;
    for (int b = 31; b >= 0; b--) {
        int want = 1 - ((x >> b) & 1);              // prefer the opposite bit
        if (cur.child[want] != null) { res |= (1 << b); cur = cur.child[want]; }
        else cur = cur.child[1 - want];
    }
    return res;
}
""",
            "Greedy from the most significant bit: a higher bit outweighs everything below it."),
    ],
    costs=[
        _cost("Insert / search", "O(L)", "O(total characters × 26)",
              "L = key length; independent of how many keys are stored."),
        _cost("Prefix count", "O(L)", "—", "With a `count` maintained on insert."),
        _cost("Wildcard search", "O(26^dots · L)", "O(L) stack", "Why the wildcard count is bounded."),
        _cost("Bit trie XOR query", "O(32)", "O(32n)", "Fixed-width keys."),
        _cost("Hash-map equivalent for prefixes", "O(n · L)", "O(n · L)", "Every key must be scanned."),
    ],
    pitfalls=[
        _pit("A prefix is reported as a stored word",
             "The `word` flag is missing, so any reachable node looks like a key.",
             "Set `word = true` only at the final node of an insert."),
        _pit("`NullPointerException` while walking",
             "A child was dereferenced before being checked for null.",
             "Test for null immediately after each descent."),
        _pit("Memory blows up",
             "26 pointers per node, times every node, on a large dictionary.",
             "Use a `Map<Character, Node>` for sparse or large alphabets."),
        _pit("The wildcard search is exponential",
             "Every `.` branches into 26 children.",
             "It is inherent; the problem bounds the wildcard count. Prune by depth where you "
             "can."),
        _pit("The root returned is not the shortest",
             "The walk continued past a `word` node looking for a longer match.",
             "Return at the first flag encountered."),
        _pit("Bit trie built from the least significant bit",
             "The greedy choice then optimises the wrong end of the number.",
             "Insert and query from bit 31 down — high bits dominate the value."),
    ],
    lessons=["trie", "hashing", "tree_basics"],
    checks=[
        _chk("What can a trie answer that a hash map cannot?",
             "Anything about prefixes — counts, autocomplete, longest matching root, "
             "wildcards. Hashing deliberately destroys the relationship between similar keys."),
        _chk("Why does a trie node need a `word` flag?",
             "A node marks a position in the tree, not necessarily a stored key. Without the "
             "flag, inserting “car” would make “ca” appear to be a word."),
        _chk("What is the cost of a trie lookup, and what is it *independent* of?",
             "O(L) in the key's length, independent of the number of keys stored. A million "
             "words does not slow it down."),
        _chk("Why is the greedy walk correct for maximum XOR?",
             "Bits are inserted most-significant first, and a single higher bit outweighs "
             "every lower bit combined. So taking the opposite bit whenever it exists is "
             "always optimal."),
    ],
    interview="""
Naming the trie is most of the marks — it is the expected answer for
autocomplete and dictionary problems, and candidates who have not met it tend to
propose scanning every word. Be ready for the trade-off question: a trie costs
far more memory than a hash set, so it earns its place only when prefixes,
wildcards or bit-greedy walks are actually needed.
""",
    internals="""
### The node is the whole design decision

```java
class Node {
    Node[] next = new Node[26];   // array of children
    boolean isWord;
}
```

versus

```java
class Node {
    Map<Character, Node> next = new HashMap<>();
    boolean isWord;
}
```

Same trie, very different memory. The array version allocates **26 references
per node whether or not they are used** — 26 × 8 bytes ≈ 208 bytes of pointers,
plus the array header, plus the object header: call it ~240 bytes per node even
for a node with one child. The map version pays a `HashMap` (its own object,
plus a bucket array, plus one `Entry` per child ≈ 32 bytes each) but only for
children that exist.

| | `Node[26]` | `HashMap<Character, Node>` |
|---|---|---|
| child lookup | one array index — a few ns | hash + bucket walk — tens of ns |
| memory, dense node (20 children) | ~240 B | ~800 B |
| memory, sparse node (1 child) | ~240 B | ~130 B |
| alphabet size | fixed at compile time | any, including Unicode |
| iterate children in order | free — index order is alphabetical | needs sorting |

The rule that falls out: **arrays win when the alphabet is small and known and
the trie is dense**; maps win when the alphabet is large, or when most nodes
have one or two children — which is what a trie of long, dissimilar words looks
like near its leaves.

For lowercase-only interview problems, take the array. It is faster, it is less
code, and `c - 'a'` is self-documenting. Say the trade-off out loud anyway; it
is the follow-up question, and "26 pointers per node regardless of use" is the
sentence that answers it.

### Where the memory actually goes

A trie's node count is the number of **distinct prefixes** across all inserted
words, not the number of words. Insert `car`, `card`, `care`, `cart` and you get
7 nodes, not 15 — the shared `car` path is stored once. That sharing is the
entire reason the structure exists, and it is also why a trie over random
strings is a disaster: nothing shares, so you allocate one node per character
and a `HashSet` beats you on every axis.

Rough arithmetic worth being able to do at a whiteboard: 10⁵ words averaging 10
characters with little sharing is ~10⁶ nodes; at 240 bytes each that is **240
MB** with the array layout, and a heap that does not fit. Switching to
`HashMap` children, or to one of the compressed variants below, is not a
micro-optimisation at that scale — it is the difference between running and
not.

### Why lookup does not depend on how much is stored

`insert` and `search` walk one node per character of the *query*, and that walk
is unaffected by how many other words the trie holds. A `HashSet<String>` is
also O(length) — it has to hash the whole string — so for exact lookup the trie
buys nothing.

What the trie buys is everything **prefix**-shaped, because the shared path is
still there to be read:

- how many stored words start with `ca` → one counter per node, maintained on
  insert
- the longest stored word that is a prefix of this string → stop at the last
  `isWord` you passed
- every completion of `ca` → the subtree under that node

A hash set destroys all of that when it hashes, which is the honest answer to
"why not just use a set?"

### The compressed variants, named

- **Radix tree / Patricia trie** — collapse any chain of single-child nodes into
  one edge holding the whole substring. Same queries, far fewer nodes; the code
  gets substantially harder because edges must be split on insert.
- **Ternary search tree** — three children per node (`<`, `=`, `>`) instead of
  26. Much less memory, slightly slower, and handles any alphabet.
- **DAWG / DAFSA** — also merge identical *suffixes*, turning the tree into a
  DAG. Minimal for a fixed dictionary, and effectively unmodifiable afterwards.

Nobody is asking you to implement these. Knowing the first one exists, and that
the problem it solves is "my trie is mostly single-child chains", is the useful
part.
""",
    build_it="""
### Write it from scratch, in about thirty lines

A trie is short enough that there is no excuse for not owning it, and every
other problem in this unit is this class with one method added.

```java
class Trie {
    private static class Node {
        Node[] next = new Node[26];
        boolean isWord;
        int passing;     // words whose path goes through here (this node included)
    }

    private final Node root = new Node();

    void insert(String w) {
        Node cur = root;
        cur.passing++;
        for (char c : w.toCharArray()) {
            int k = c - 'a';
            if (cur.next[k] == null) cur.next[k] = new Node();
            cur = cur.next[k];
            cur.passing++;
        }
        cur.isWord = true;
    }

    /** The node reached by walking `s`, or null if the path leaves the trie. */
    private Node walk(String s) {
        Node cur = root;
        for (char c : s.toCharArray()) {
            cur = cur.next[c - 'a'];
            if (cur == null) return null;
        }
        return cur;
    }

    boolean contains(String w) {
        Node n = walk(w);
        return n != null && n.isWord;
    }

    int countWithPrefix(String p) {
        Node n = walk(p);
        return n == null ? 0 : n.passing;
    }
}
```

### Four things to notice while typing it

1. **`walk` is the whole structure.** `contains`, `countWithPrefix`,
   `startsWith`, autocomplete — all of them are `walk` plus one read of the node
   it returns. Factor it out and the rest of the unit is three-line methods.
2. **`isWord` is not "has no children".** After inserting `car` and `card`, the
   node at `car` has a child *and* is a word. After inserting only `card`, the
   node at `car` exists and is not. `contains` must read the flag; nothing else
   is equivalent to it.
3. **`passing` is maintained on insert, never counted on query.** That is what
   makes `countWithPrefix` O(length) instead of O(subtree). Maintaining a
   counter during the write so the read stays cheap is the same move as
   Union-Find's component count.
4. **The root increments too.** `countWithPrefix("")` should be the total number
   of inserted words, and it is — for free — only if `root.passing` is bumped
   before the loop.

### Then extend it, in the order the rungs do

- **`longestPrefixOf(s)`** — walk `s`, remembering the depth of the last node
  with `isWord` set. Three lines, and it is the whole of the replace-words
  problem.
- **Wildcard search** — at a `.`, recurse into every non-null child. The
  *structure* does not change at all; only the traversal does, which is the
  point worth internalising.
- **Deletion** — insert `car` and `card`, then delete `card`. You must unset
  `isWord`, decrement `passing` along the path, and free only the nodes whose
  `passing` reached 0. Get this right and you understand why most interview
  tries do not support delete.
- **A binary trie over bits.** Replace 26 children with 2, and insert each
  number's 32 bits from the top. Walking greedily toward the *opposite* bit at
  each step gives the maximum XOR against a stored number — the last problem in
  the curriculum, and a trie with the alphabet set to `{0, 1}`.
""",
    rungs=[
        _rung("Warm up", "Insert and exact lookup, and the flag people forget.",
              ["trie-insert-lookup"],
              {"trie-insert-lookup": "`isWord` is not “has no children”: insert `card` and `car` becomes a node that exists and is not a word. Also be able to say why a HashSet would beat this — the answer is the rest of the unit."}),
        _rung("Core", "Build it, walk it, count with it.",
              ["implement-trie-ops", "word-in-dictionary", "prefix-counts"],
              {"implement-trie-ops": "Write the structure once from scratch. Everything else in this unit reuses it verbatim.",
               "prefix-counts": "Maintain `count` on insert; the query is then the same walk with a different final read."}),
        _rung("Variations", "Stop the walk on a condition.",
              ["replace-words-roots", "longest-buildable-word"],
              {"replace-words-roots": "Return at the first `word` node — that is what makes the root the shortest one.",
               "longest-buildable-word": "Only descend through nodes that are themselves words, so every prefix is buildable."}),
        _rung("Stretch", "The walk becomes a search, and the alphabet becomes bits.",
              ["word-dictionary-wildcard", "max-xor-pair"],
              {"word-dictionary-wildcard": "At a `.`, recurse into every non-null child. The structure is unchanged; only the traversal is.",
               "max-xor-pair": "A binary trie over the bits, walked greedily from bit 31. The last idea in the curriculum, and a summary of most of it."}),
    ],
    next_up="""
One unit left in the core curriculum, and it has no algorithm of its own: design,
where every structure so far is a part to be combined at the right cost.
""",
)


# --- Unit 36 — Design --------------------------------------------------------

_unit(
    "design", "Data Structure Design", "🏗️", _S7,
    "No algorithm — just the right combination, at the right cost.",
    weight=3,
    prereqs=["hashing", "linked-lists", "heaps", "bst"],
    why="""
Design problems give you an interface and a performance target: *"implement
`get` and `put`, both in O(1)"*. There is no clever insight to find. The work is
choosing structures whose costs add up to the target, and keeping them
consistent with one another as the data changes.

This is the closest thing in the problem bank to real engineering, and it is why
these questions are so common in interviews — they test whether you know what
your tools cost, not whether you have seen a trick.
""",
    model="""
### The method

1. **Write the operations and their required costs.** That table is the spec.
2. **For each operation, name a structure that achieves it alone.** O(1) lookup
   by key → hash map. Ordered by value → heap or tree. O(1) insert/remove at a
   known position → doubly linked list.
3. **Combine them, and decide what each one stores.** Usually one structure owns
   the data and the others hold *references into it*.
4. **Check every operation again** against the combined design — the failure is
   almost always an operation that now has to update two structures and only
   updates one.

### The canonical combination

**Hash map + doubly linked list** gives O(1) lookup *and* O(1) reordering, which
is exactly what an LRU cache needs:

- the list holds entries in recency order, most-recent at the head;
- the map holds `key → node`, so any node can be found instantly;
- a doubly linked list is required because unlinking a node in O(1) needs its
  *predecessor*, which a singly linked list cannot give you.

`get` moves a node to the front; `put` inserts at the front and, if over
capacity, drops the tail. Every step is O(1), and the tail is the least recently
used item by construction. The trace below is a capacity-2 cache, operation by
operation.

LFU is the same idea one level up: map by key, plus buckets keyed by frequency,
plus a pointer to the minimum frequency.

### Carrying an auxiliary invariant

Min-stack keeps a second stack of "minimum at or below this depth", pushed in
lockstep with the main one. Popping drops both, so the minimum is always on top:
an extra O(n) memory buys an O(1) query. That "store the answer alongside the
data" move is the most transferable idea in the unit — the same trick turns
`stock-spanner` into the monotonic stack you already know, wrapped in a class
and fed one value at a time.

### Time-ordered data

When entries are appended with non-decreasing timestamps, the list per key is
already sorted — so *"the value at time t"* is a binary search, and no extra
ordering structure is needed. Recognising that the data arrives sorted is the
insight; the rest is the stage-3 template.

### Two rules that prevent most of the bugs

**One owner.** Exactly one structure holds the real data; the others hold keys
or references into it. Two structures that both think they own an entry will
eventually disagree.

**Every mutation touches every structure.** Write the list down — "an eviction
must: unlink the node, remove the map key, decrement the size" — and check each
operation against it. Design bugs are almost never wrong algorithms; they are a
missing line in one of three places.
""",
    internals="""
### Why sentinels, always

Splice code without sentinel nodes is a thicket of null checks: removing the
head is special, removing the tail is special, removing the only node is
special. With a permanent `head` and `tail` that never hold data, **every real
node is guaranteed to have both a predecessor and a successor**, and `remove`
becomes two unconditional assignments:

```java
n.prev.next = n.next;
n.next.prev = n.prev;
```

No branches, no null checks, no special cases. This is the same idea as the
dummy head from the linked-list unit, applied at both ends — and it is worth
building the habit, because the LRU cache is where a missed null check is
hardest to debug.

### What "O(1) amortised" means to an interviewer

Three different structures in the linear-structures stage claim O(1) for slightly
different reasons, and being able to separate them is a real signal:

| Claim | Kind | Why |
| --- | --- | --- |
| `ArrayDeque.push` | amortised | doubling spreads the copy over n pushes |
| `HashMap.get` | average case | good hash distribution; O(n) if everything collides |
| LRU `get`/`put` | genuinely worst-case | a fixed number of pointer writes, no resize, no search |

The LRU cache is the strongest of the three, and saying so — "this is worst-case
O(1), not amortised" — is the kind of precision that ends the follow-up
questions.

### Hash maps, the part that matters here

A `HashMap` is an array of buckets; a key's hash picks the bucket, and
collisions chain within it (Java converts a long chain to a balanced tree, so
the pathological case is O(log n) rather than O(n)). Load factor 0.75 triggers a
resize and a full rehash — O(n), amortised away like the deque's doubling.

The consequence for design problems: `HashMap` gives you **O(1) lookup by key
and nothing else**. No order, no minimum, no range. Every structure you bolt
onto it in this unit exists to supply exactly one of those missing properties.
""",
    signals=[
        _sig("“O(1) get and put with eviction”", "Hash map + doubly linked list",
             "The map finds the node; the list orders it."),
        _sig("“get the minimum in O(1)” alongside push/pop", "A parallel stack of minima",
             "Store the answer next to the data."),
        _sig("“implement X using only Y”", "Two of Y, and an amortised argument",
             "Pouring between two stacks reverses the order."),
        _sig("“value at a given timestamp”", "Map to a sorted list + binary search",
             "Appends arrive in time order, so the list is already sorted."),
        _sig("“most recent k”, “feed”, “top posts”", "Heap over per-user lists",
             "Merge-k, restricted to k results."),
        _sig("“span”, “consecutive smaller before this one”", "A monotonic stack in a class",
             "The stacks unit's pattern, fed one value at a time."),
        _sig("Two operations want two different orders", "Two structures, one owner",
             "One holds the data; the other holds references into it."),
    ],
    skeletons=[
        _sk("Hash map + doubly linked list (LRU)",
            "Any cache with O(1) access and eviction by recency.",
            """
class Node { int key, val; Node prev, next; }
Map<Integer, Node> map = new HashMap<>();
Node head = new Node(), tail = new Node();      // sentinels
{ head.next = tail; tail.prev = head; }

void remove(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
void addFirst(Node n) {
    n.next = head.next; n.prev = head;
    head.next.prev = n; head.next = n;
}
// get: remove(n); addFirst(n);
// put over capacity: Node lru = tail.prev; remove(lru); map.remove(lru.key);
""",
            "Sentinel head and tail nodes remove every null check from the splice code."),
        _sk("Parallel minimum stack",
            "Min-stack, max-stack, any “extreme so far” query.",
            """
Deque<Integer> st = new ArrayDeque<>(), mins = new ArrayDeque<>();

void push(int x) {
    st.push(x);
    mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
}
void pop() { st.pop(); mins.pop(); }
int getMin() { return mins.peek(); }
""",
            "Push to both, pop from both — the invariant maintains itself."),
        _sk("Time-keyed store",
            "Versioned values, “state at time t”.",
            """
Map<String, List<int[]>> store = new HashMap<>();   // key → [(time, value)…]

void set(String k, int v, int t) {
    store.computeIfAbsent(k, x -> new ArrayList<>()).add(new int[]{ t, v });
}
// get: binary-search the list for the LAST entry with time <= t
""",
            "Appends come in increasing time order, so the list is sorted for free."),
        _sk("A pattern, wrapped in a class",
            "Stock spanner, streaming versions of an offline algorithm.",
            """
Deque<int[]> st = new ArrayDeque<>();        // {price, span}, prices decreasing

int next(int price) {
    int span = 1;
    while (!st.isEmpty() && st.peek()[0] <= price) span += st.pop()[1];
    st.push(new int[]{ price, span });
    return span;
}
""",
            "The monotonic stack, fed one element at a time — popped spans are absorbed."),
    ],
    traces=[
        _trace(
            "LRU cache, capacity 2: put(1,A), put(2,B), get(1), put(3,C)",
            "The list is recency order, most-recent first. Watch the last row: 2 is evicted "
            "because `get(1)` moved 1 to the front, which is the entire behaviour being "
            "tested.",
            ["Operation", "List (front → back)", "Map keys", "Returned", "Evicted"],
            [
                ["put(1, A)", "1", "{1}", "—", "—"],
                ["put(2, B)", "2, 1", "{1, 2}", "—", "—"],
                ["get(1)", "1, 2", "{1, 2}", "**A**", "— (1 moved to the front)"],
                ["put(3, C)", "3, 1", "{1, 3}", "—", "**2** — now the tail"],
                ["get(2)", "3, 1", "{1, 3}", "**−1**", "— (already evicted)"],
            ],
            "Two structures changed on every row and had to agree on every row. The eviction "
            "step is where they usually stop agreeing: unlinking the tail node without also "
            "removing its map key leaves a key pointing at a node no longer in the list.",
        ),
        _trace(
            "Min-stack: push 5, push 2, push 7, pop, getMin",
            "The two stacks move in lockstep, so `mins.peek()` is always the minimum of "
            "exactly the elements currently in `st`.",
            ["Operation", "st (top →)", "mins (top →)", "getMin"],
            [
                ["push 5", "5", "5", "5"],
                ["push 2", "2, 5", "2, 5", "2"],
                ["push 7", "7, 2, 5", "**2**, 2, 5", "2 — 7 pushes min(7, 2) = 2"],
                ["pop", "2, 5", "2, 5", "2"],
                ["pop", "5", "5", "**5** — restored automatically"],
            ],
            "The third row is the one to understand: `mins` stores a *duplicate* 2 rather "
            "than skipping the push. That is what makes `pop` a plain pop from both stacks "
            "instead of a conditional — and conditionals are where this problem goes wrong.",
        ),
    ],
    costs=[
        _cost("Hash map + linked list (LRU)", "O(1) worst case", "O(capacity)", "No search, no resize on the hot path."),
        _cost("Min-stack", "O(1) all operations", "O(n)", "Extra stack of minima."),
        _cost("Time-keyed get", "O(log n)", "O(n)", "Binary search over the key's history."),
        _cost("Feed of k most recent over u sources", "O(u log u + k log u)", "O(u)", "Merge-k, truncated at k."),
        _cost("LFU cache", "O(1) get/put", "O(capacity)", "Frequency buckets plus a minimum-frequency pointer."),
        _cost("Stock spanner", "O(1) amortised", "O(n)", "Each price pushed once, popped once."),
    ],
    pitfalls=[
        _pit("The cache returns stale or missing entries",
             "One structure was updated and the other was not — usually an eviction that "
             "unlinked the node but left the map key.",
             "Write the mutation checklist down: every change must touch *every* structure "
             "that references the entry."),
        _pit("Unlinking a node is O(n)",
             "A singly linked list cannot reach a node's predecessor.",
             "Use a doubly linked list; that requirement is the reason for the design."),
        _pit("Null-pointer errors all over the splice code",
             "Head and tail are real nodes, so every operation special-cases the ends.",
             "Use sentinel head and tail nodes that never hold data."),
        _pit("`put` on an existing key inserts a duplicate",
             "The update path assumed the key was new.",
             "On `put`, check for the key first: update the value and move the node, rather "
             "than inserting a second one."),
        _pit("Min-stack's `pop` corrupts the minimum",
             "`mins` was only pushed when a new minimum appeared, so the two stacks no "
             "longer align.",
             "Push to `mins` on every push, duplicating the current minimum when necessary."),
        _pit("The heap-based feed is rebuilt on every query",
             "All posts are re-merged instead of only the k most recent per source.",
             "Bound the work by k: only the head of each source can be next."),
        _pit("Binary search returns the wrong version",
             "An upper-bound search was needed but a lower-bound one was written.",
             "You want the last entry with `time <= t` — `upperBound(t) - 1`."),
    ],
    lessons=["design_ds", "stack", "queue", "hashing"],
    checks=[
        _chk("Why must an LRU cache use a *doubly* linked list?",
             "Eviction and reordering unlink a node in O(1), which requires its predecessor. "
             "A singly linked list would need an O(n) scan to find it."),
        _chk("Is an LRU cache's `get` amortised O(1) or worst-case O(1)?",
             "Worst case. It is a fixed number of pointer writes plus a hash lookup — no "
             "resize, no search, no doubling. That distinguishes it from `ArrayDeque.push`, "
             "which is amortised."),
        _chk("Why does min-stack push a duplicate minimum instead of skipping the push?",
             "So the two stacks stay the same height and `pop` can be unconditional. Pushing "
             "only on a new minimum means `pop` must decide whether to pop `mins` too, which "
             "is exactly where the bug appears."),
        _chk("What do sentinel nodes buy you?",
             "Every real node has both neighbours, so `remove` and `addFirst` are "
             "unconditional two-line assignments with no null checks and no special cases "
             "for the first or last element."),
        _chk("What is the method when a design problem gives you cost targets?",
             "List the operations with their required costs, pick a structure that achieves "
             "each one alone, combine them with one owning the data, then re-check every "
             "operation against the combination."),
        _chk("A `HashMap` gives O(1) lookup. What does it *not* give you, and how is that "
             "usually fixed?",
             "No ordering, no minimum, no range queries. Each is supplied by bolting on a "
             "second structure that holds references into the map's data — a list for "
             "recency, a heap for extremes, a sorted list for time."),
    ],
    interview="""
Design questions are where the interview stops being a quiz. Talk through the
operation/cost table out loud before writing anything — it is the reasoning
being assessed, and it is also how you catch the impossible requirement early.
Three sentences worth having ready: *"a hash map gives me O(1) lookup and a
doubly linked list gives me O(1) reordering, so together they give me both"*,
*"that is amortised O(1), because each element moves at most once"*, and — for
the LRU itself — *"this one is worst-case O(1), not amortised"*.
""",
    build_it="""
**Build the LRU cache from the pieces you already wrote.** You have the
sentinel doubly linked list from the linked-list unit; add a `HashMap<Integer,
Node>` and the two operations.

Then do the thing that actually teaches it: write a `checkInvariants()` method
that walks the list, counts the nodes, and asserts that the count equals
`map.size()`, that every node in the list is in the map, and that every map
value is reachable from `head`. Call it after every `get` and `put` in a test
with capacity 2 and a few hundred random operations.

It will fail, and where it fails is the lesson — almost always the eviction path,
which unlinks the node and forgets the map key. That failure *is* the unit: a
design bug is a missing line in one of several places, not a wrong algorithm.
""",
    rungs=[
        _rung("Warm up", "Build the primitives themselves.",
              ["design-hashset", "design-hashmap"],
              {"design-hashset": "Buckets and a hash. The simplest version of the structure every other problem in this unit leans on.",
               "design-hashmap": "Buckets plus chaining. Writing it once explains every “O(1) average” claim you have made since stage 2 — including why a bad hash makes it O(n)."}),
        _rung("Core", "Carry an extra invariant alongside the data.",
              ["min-stack", "design-linked-list", "browser-history"],
              {"min-stack": "The parallel-stack idea, which transfers to far harder problems. Push a duplicate minimum rather than making `pop` conditional.",
               "design-linked-list": "Every splice case in one class. Use a sentinel and watch the null checks disappear.",
               "browser-history": "Two stacks, or one list with a cursor. Decide which before you type — and note that a forward history is *discarded* on a new visit, which the two-stack version gets right for free."}),
        _rung("Variations", "A structure chosen because the data arrives in a helpful order.",
              ["stock-spanner", "time-based-kv"],
              {"stock-spanner": "The monotonic stack from the stacks unit, wrapped in a class and fed one value at a time. Store (price, span) so a popped entry's span is absorbed rather than recomputed.",
               "time-based-kv": "Timestamps arrive increasing, so each key's list is already sorted — binary-search it. You want the last entry `<= t`, which is upper bound minus one."}),
        _rung("Stretch", "Two or three structures kept consistent with each other.",
              ["lru-cache", "design-twitter", "lfu-cache"],
              {"lru-cache": "The canonical design problem. Use sentinel nodes, handle `put` on an existing key, and get every operation to worst-case O(1).",
               "design-twitter": "Merge-k over followees' timelines, truncated at 10. Only the head of each list can be next — that is what stops it being O(total tweets).",
               "lfu-cache": "LRU with a second dimension: frequency buckets, each an LRU list of its own, plus a minimum-frequency pointer. Draw the three structures and their invariants before coding."}),
    ],
    next_up="""
That is the core curriculum. Every interview-core technique has been taught — so
from here the work is **revision**: the stage-end mixed sets, the weakness
filters in Browse, and re-solving the stretch rungs from memory rather than from
notes. The optional stage after this one goes beyond the core: string hashing,
range-query trees, advanced graph algorithms and bitmask DP.
""",
)
