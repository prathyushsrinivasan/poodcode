# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 6 — Optimisation, and one more structure.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# The final stage is about problems that ask for the BEST answer rather than an
# answer, and there are only two ways to get one: commit to a local choice and
# prove it was safe (greedy), or evaluate every choice while never recomputing
# a subproblem (dynamic programming). Greedy comes first because the honest way
# to teach DP is as the thing you fall back on when the greedy proof fails.
#
# Intervals sit between them deliberately: it is the clearest family where
# sorting plus a greedy rule is provably optimal, so it is where the proof
# obligation stops being abstract.
#
# The trie closes the curriculum — the last structure in the bank, and the one
# that makes the point that a data structure can be the whole algorithm.
# ---------------------------------------------------------------------------

_S6 = _stage(
    "advanced", "Optimisation & Advanced Structures", "🏔️",
    "Best answers: prove a shortcut, or search exhaustively without repeating.",
    """
Everything up to here computes *an* answer. This stage computes the *best* one,
and the entire stage turns on one question:

> Can I decide now, or must I keep my options open?

If a local choice is provably safe, take it — that is **greedy**, and it is O(n)
or O(n log n). If it is not, you must consider every option, and the only way to
afford that is to never solve the same subproblem twice — that is **dynamic
programming**.

Getting this call right is the highest-value judgement in algorithmic
interviewing. The stage teaches both, teaches the counterexample habit that
tells them apart, and finishes with the trie, where the structure *is* the
algorithm.
""")


# --- Unit 28 — Greedy -------------------------------------------------------

_unit(
    "greedy", "Greedy Algorithms", "💰", _S6,
    "Take the best local move — and be able to prove it was safe.",
    prereqs=["sorting"],
    why="""
Greedy algorithms are the shortest, fastest solutions in the whole bank, and
the most dangerous. The code for "best answer" is often one pass with a running
maximum; the difficulty is entirely in knowing whether that is *correct*, because
a greedy algorithm that is wrong is wrong silently and usually passes the small
tests.

So this unit is mostly about the proof obligation. Two arguments cover almost
every case, and if you cannot make one of them, the answer is dynamic
programming.
""",
    model="""
### The two proof patterns

**Exchange argument.** Take any optimal solution. Show that you can swap one of
its choices for the greedy choice without making it worse. Therefore some
optimal solution contains the greedy choice, so taking it loses nothing.

*Buy and sell a stock*: the best profit ending today uses the lowest price seen
so far. Any optimal pair `(buy, sell)` can have its buy moved to the minimum
before `sell` without reducing the profit.

**Stays-ahead argument.** Show that after each step, the greedy solution is at
least as far along as any other. *Jump game*: track the furthest index
reachable; no other strategy can be further ahead after the same number of
indices, so if greedy cannot reach the end, nothing can.

### When greedy fails

The moment a choice that looks worse now enables something better later. Coin
change with `{1, 3, 4}` and amount 6: greedy takes 4, then 1, then 1 — three
coins. The optimum is 3 + 3 — two. Nothing in the greedy step could have seen
that, which is why the honest test is **construct a counterexample**. If you
cannot, and you can make one of the two arguments above, proceed.

### The usual shapes

| Shape | Greedy rule |
| --- | --- |
| Best profit / best difference | Track the running minimum (or maximum) |
| Reachability | Track the furthest point reachable |
| Scheduling non-overlapping items | Sort by **end** time, take greedily |
| Fewest groups covering everything | Sort by end, extend while it still covers |
| Repeatedly take the extreme | A heap (see the heaps unit) |

Sorting by **end** time rather than start is the classic result: finishing
earliest leaves the most room for everything after it.

### Greedy versus DP, in practice

Try greedy first — it is O(n) and simple. Spend sixty seconds trying to break
it. If you find a counterexample, the failure usually tells you the DP state:
*"the choice depends on how much is left"* means the remaining amount is a
dimension of the table.
""",
    signals=[
        _sig("“maximum profit from one buy and one sell”", "Running minimum",
             "Best sale today uses the cheapest day so far."),
        _sig("“can you reach the end?”", "Furthest reachable index",
             "Stays-ahead: nothing can be further along."),
        _sig("“maximum non-overlapping …”", "Sort by end time, take greedily",
             "Finishing earliest preserves the most room."),
        _sig("“fewest jumps / groups / arrows”", "Extend the current reach; count when forced",
             "Take a new group only when the current one cannot cover."),
        _sig("“repeatedly take the largest”", "Heap-driven greedy",
             "The heaps unit's loop."),
        _sig("A local choice can be regretted later", "Not greedy — DP",
             "Construct the counterexample; it names the DP state."),
    ],
    skeletons=[
        _sk("Running extreme",
            "Best profit, largest gap, maximum difference.",
            """
int minSoFar = a[0], best = 0;
for (int x : a) {
    best = Math.max(best, x - minSoFar);     // sell today, having bought at the min
    minSoFar = Math.min(minSoFar, x);
}
""",
            "Evaluate before updating: you cannot buy and sell on the same tick."),
        _sk("Furthest reach",
            "Jump game, reachability, coverage.",
            """
int reach = 0;
for (int i = 0; i < n; i++) {
    if (i > reach) return false;             // a gap nothing can cross
    reach = Math.max(reach, i + a[i]);
}
return true;
""",
            "One pass, no memory — the stays-ahead argument in four lines."),
        _sk("Fewest groups (interval jumps)",
            "Minimum jumps, fewest arrows, fewest refuels.",
            """
int jumps = 0, curEnd = 0, farthest = 0;
for (int i = 0; i < n - 1; i++) {
    farthest = Math.max(farthest, i + a[i]);
    if (i == curEnd) { jumps++; curEnd = farthest; }   // forced to commit
}
""",
            "Count only when the current group is exhausted — that is what makes it minimal."),
        _sk("Schedule by end time",
            "Maximum non-overlapping intervals; minimum removals.",
            """
Arrays.sort(iv, (x, y) -> Integer.compare(x[1], y[1]));   // by END
int end = Integer.MIN_VALUE, kept = 0;
for (int[] v : iv)
    if (v[0] >= end) { kept++; end = v[1]; }
""",
            "By end, not by start. Sorting by start is the classic wrong answer."),
    ],
    costs=[
        _cost("Single-pass greedy", "O(n)", "O(1)", "Running extreme, furthest reach."),
        _cost("Sort-then-greedy", "O(n log n)", "O(1)", "Scheduling, intervals."),
        _cost("Heap-driven greedy", "O(n log n)", "O(n)", "Repeatedly take the extreme."),
        _cost("The DP alternative", "O(n · states)", "O(states)", "What you fall back to when the proof fails."),
    ],
    pitfalls=[
        _pit("Correct on the examples, wrong on a hidden test",
             "The greedy rule is not actually optimal; no counterexample was sought.",
             "Spend a minute trying to break it. Failing that, state which of the two "
             "arguments applies."),
        _pit("Intervals were sorted by start time",
             "Scheduling optimality depends on finishing earliest.",
             "Sort by end time for maximum non-overlapping selection."),
        _pit("Profit of 0 where a loss was expected (or vice versa)",
             "The problem allows no transaction, or requires exactly one — the two have "
             "different answers.",
             "Re-read whether doing nothing is permitted."),
        _pit("The running minimum is updated before it is used",
             "Buying and selling collapse onto the same element.",
             "Evaluate the candidate answer first, then update the running extreme."),
        _pit("Greedy coin change gives too many coins",
             "The denominations are not canonical.",
             "Use the coin-change DP in the next unit."),
        _pit("Jump counting is one too many",
             "The loop ran to `n` rather than `n - 1`, counting an arrival at the end.",
             "Stop before the last index: reaching it needs no further jump."),
    ],
    lessons=["greedy", "intervals", "heap_greedy"],
    checks=[
        _chk("What are the two standard ways to justify a greedy algorithm?",
             "An exchange argument (any optimal solution can be modified to contain the "
             "greedy choice without getting worse) and a stays-ahead argument (greedy is "
             "never behind any alternative after the same number of steps)."),
        _chk("Give a coin system where greedy change is wrong.",
             "`{1, 3, 4}` for amount 6: greedy gives 4+1+1 = three coins; the optimum is "
             "3+3 = two."),
        _chk("Why sort by end time rather than start time when scheduling?",
             "The interval that finishes earliest leaves the largest remaining window, so "
             "choosing it never rules out a better solution."),
        _chk("What should you do when you find a counterexample to your greedy rule?",
             "Switch to dynamic programming — and read the counterexample for the state: "
             "whatever the greedy step could not see is usually the missing dimension."),
    ],
    interview="""
The trap is that greedy code is short, so it is tempting to write it and move
on. Interviewers are listening for the justification. Two sentences settle it:
*"sorting by end time is safe because the earliest finish leaves the most room"*,
or *"I tried to construct a case where a worse local choice pays off later and
could not"*. If neither is available, say so and switch to DP — that judgement
is itself the thing being tested.
""",
    rungs=[
        _rung("Warm up", "A sort order, a local rule, and the exchange argument that joins them.",
              ["activity-selection-small"],
              {"activity-selection-small": "The canonical greedy. Produce the counterexamples that kill sorting by start time and by duration — that is how you check a rule you just invented."}),
        _rung("Core", "One pass, one running value, one proof.",
              ["best-time-buy-sell", "jump-game"],
              {"best-time-buy-sell": "Say the exchange argument out loud before coding. The code is four lines; the reasoning is the exercise.",
               "jump-game": "Stays-ahead. Track the furthest reachable index and fail the moment you stand past it."}),
        _rung("Stretch", "Greedy where the counting is the subtle part.",
              ["jump-game-ii"],
              {"jump-game-ii": "Count a jump only when the current reach is exhausted, and stop before the last index."}),
    ],
    next_up="""
Intervals are the family where “sort, then be greedy” is provably right — and
where the sweep from the prefix-sums unit comes back.
""",
)


# --- Unit 29 — Intervals ----------------------------------------------------

_unit(
    "intervals", "Intervals", "📅", _S6,
    "Sort by the right endpoint, then sweep.",
    prereqs=["sorting", "greedy"],
    why="""
Meetings, bookings, ranges, flights, free time — an enormous number of practical
problems are pairs of numbers with an overlap rule. Almost all of them are
solved by one decision (**sort by start, or sort by end?**) followed by a single
pass, and getting that decision right is the difference between three lines and
an hour.

The family also contains the cleanest example of the sweep from the prefix-sums
unit: turning each interval into a `+1` at its start and a `−1` at its end
answers every "how many at once" question without ever comparing intervals to
one another.
""",
    model="""
### The one decision

| Question | Sort by | Then |
| --- | --- | --- |
| Merge overlapping | **start** | Extend the current interval, or emit and restart |
| Maximum non-overlapping / fewest removals | **end** | Keep if it starts after the last kept end |
| How many overlap at once | either — use a **sweep** | `+1` at start, `−1` at end, in time order |
| Insert one interval | already sorted | Three phases: before, merged, after |
| Intersect two sorted lists | already sorted | Two pointers |

Merging wants earliest **start** because you build left to right. Scheduling
wants earliest **end** because finishing early leaves the most room. These are
different questions and the wrong sort is the single most common interval bug.

### Merging

```java
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    int[] last = out.isEmpty() ? null : out.get(out.size() - 1);
    if (last != null && cur[0] <= last[1]) last[1] = Math.max(last[1], cur[1]);
    else out.add(cur.clone());
}
```

`Math.max` matters: the current interval may be entirely inside the previous
one, and overwriting the end would shrink it.

### The overlap test

Two intervals `[a1, a2]` and `[b1, b2]` overlap iff `a1 <= b2 && b1 <= a2`.
Whether touching endpoints count is a specification question — `[1,2]` and
`[2,3]`. Decide it from the problem statement (a meeting ending at 2 usually
does *not* clash with one starting at 2) and keep the comparison consistent.

### The sweep

```java
// minimum meeting rooms: the maximum number concurrently active
int[] starts = ..., ends = ...;
Arrays.sort(starts); Arrays.sort(ends);
int rooms = 0, best = 0, j = 0;
for (int i = 0; i < n; i++) {
    while (j < n && ends[j] <= starts[i]) { rooms--; j++; }   // frees first
    rooms++;
    best = Math.max(best, rooms);
}
```

Process an ending **before** a start at the same instant, or a room is counted
twice. The heap version — a min-heap of end times, polled while the earliest end
is ≤ the current start — is equivalent and often easier to explain.

### Two sorted lists: intersect with two pointers

The intersection of `[a1,a2]` and `[b1,b2]` is
`[max(a1,b1), min(a2,b2)]`, valid when the start is ≤ the end. Then advance
whichever interval **ends first**, because it can have no further intersections.
""",
    signals=[
        _sig("“merge overlapping”", "Sort by start",
             "Build left to right, extending with `max`."),
        _sig("“maximum meetings”, “fewest removals”", "Sort by end",
             "Earliest finish leaves the most room."),
        _sig("“minimum rooms / platforms / servers”", "Sweep or a min-heap of end times",
             "The answer is the peak concurrency."),
        _sig("“insert into a sorted list of intervals”", "Three phases",
             "Everything before, the merged block, everything after."),
        _sig("“intersection of two interval lists”", "Two pointers",
             "Advance whichever ends first."),
        _sig("“free time”, “gaps”", "Merge everything, then read the gaps",
             "The complement of the merged set."),
    ],
    skeletons=[
        _sk("Merge overlapping",
            "The base operation almost everything else builds on.",
            """
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    if (!out.isEmpty() && cur[0] <= out.get(out.size() - 1)[1])
        out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
    else out.add(cur.clone());
}
""",
            "`max` on the end — the new interval may be nested inside the last."),
        _sk("Insert one interval",
            "Into an already-sorted, non-overlapping list.",
            """
int i = 0, n = iv.length;
while (i < n && iv[i][1] < ni[0]) out.add(iv[i++]);          // strictly before
while (i < n && iv[i][0] <= ni[1]) {                         // overlapping
    ni[0] = Math.min(ni[0], iv[i][0]);
    ni[1] = Math.max(ni[1], iv[i][1]);
    i++;
}
out.add(ni);
while (i < n) out.add(iv[i++]);                              // strictly after
""",
            "Three loops, each with a clear job. Do not try to fuse them."),
        _sk("Peak concurrency (heap)",
            "Minimum meeting rooms, maximum simultaneous anything.",
            """
Arrays.sort(iv, (a, b) -> Integer.compare(a[0], b[0]));
PriorityQueue<Integer> ends = new PriorityQueue<>();
for (int[] v : iv) {
    if (!ends.isEmpty() && ends.peek() <= v[0]) ends.poll();  // a room freed
    ends.offer(v[1]);
}
int rooms = ends.size();
""",
            "The heap size is the number of rooms in use; its peak is the answer."),
        _sk("Intersect two sorted lists",
            "Overlap of two schedules.",
            """
int i = 0, j = 0;
while (i < a.length && j < b.length) {
    int lo = Math.max(a[i][0], b[j][0]), hi = Math.min(a[i][1], b[j][1]);
    if (lo <= hi) out.add(new int[]{ lo, hi });
    if (a[i][1] < b[j][1]) i++; else j++;         // advance the earlier end
}
""",
            "Advancing the earlier end is what makes the single pass sufficient."),
    ],
    costs=[
        _cost("Sort", "O(n log n)", "O(n)", "Dominates every interval algorithm."),
        _cost("Merge / greedy scan after sorting", "O(n)", "O(n)", "One pass."),
        _cost("Sweep of ±1 events", "O(n log n)", "O(n)", "Sorting the events."),
        _cost("Heap of end times", "O(n log n)", "O(n)", "Same bound, easier to explain."),
        _cost("Insert into a sorted list", "O(n)", "O(n)", "No sort needed — it is already ordered."),
    ],
    pitfalls=[
        _pit("Maximum non-overlapping selection is too small",
             "The intervals were sorted by start time.",
             "Sort by end. This is the single most common interval mistake."),
        _pit("A merged interval is shorter than one it contains",
             "The end was overwritten rather than maximised.",
             "`last[1] = Math.max(last[1], cur[1])` — nested intervals are real."),
        _pit("One room too many",
             "A start was processed before an end at the same timestamp.",
             "Release first: use `ends[j] <= starts[i]` in the sweep."),
        _pit("Touching intervals are treated inconsistently",
             "`[1,2]` and `[2,3]` were merged in one place and separated in another.",
             "Decide from the statement whether contact counts, and use the same comparison "
             "everywhere."),
        _pit("Sorting an already-sorted input",
             "An extra O(n log n) where the list was given in order.",
             "Insert-into-sorted is O(n); check what the input guarantees."),
        _pit("The sort comparator overflows",
             "`(a, b) -> a[0] - b[0]` with coordinates near `Integer.MAX_VALUE`.",
             "`Integer.compare(a[0], b[0])`."),
    ],
    lessons=["intervals", "sorting", "heap"],
    checks=[
        _chk("Merging wants one sort order and scheduling wants another. Which and why?",
             "Merging sorts by **start**, because it builds the result left to right. "
             "Maximum non-overlapping scheduling sorts by **end**, because finishing "
             "earliest leaves the most room for what follows."),
        _chk("Write the overlap test for [a1,a2] and [b1,b2].",
             "`a1 <= b2 && b1 <= a2`. Whether the endpoints touching counts as overlap is a "
             "specification decision and must be applied consistently."),
        _chk("Why must an end event be processed before a start at the same time?",
             "Otherwise a resource that is being released at that instant is not yet "
             "available, and the peak count is one too high."),
        _chk("How do you compute free time across many busy intervals?",
             "Merge all the busy intervals, then emit the gaps between consecutive merged "
             "blocks."),
    ],
    interview="""
Interval questions are a gift when you state the sort rule first: *"merging, so
I sort by start"* or *"maximum non-overlapping, so I sort by end — earliest
finish leaves the most room"*. Then raise the endpoint question before the
interviewer does — does a meeting ending at 2 clash with one starting at 2? —
because it is the ambiguity the test cases are built around.
""",
    rungs=[
        _rung("Warm up", "The overlap test, applied once.",
              ["can-attend-meetings"],
              {"can-attend-meetings": "Sort by start and compare neighbours. Decide what touching endpoints mean before you code."}),
        _rung("Core", "Merging, and the two-pointer intersection.",
              ["merge-intervals", "insert-interval", "interval-intersections"],
              {"merge-intervals": "The base operation. `Math.max` on the end, because intervals nest.",
               "insert-interval": "Three phases. Trying to write it as one loop is how this becomes hard."}),
        _rung("Variations", "Sweeps and end-time greed.",
              ["min-meeting-rooms", "car-pooling", "non-overlapping-remove", "min-arrows-balloons"],
              {"min-meeting-rooms": "Solve it twice — a ±1 sweep and a heap of end times — and notice they are the same algorithm.",
               "non-overlapping-remove": "Sort by end and keep greedily; the removals are everything you did not keep."}),
        _rung("Stretch", "Merge first, then read the complement.",
              ["employee-free-time"],
              {"employee-free-time": "Flatten every schedule, merge, and emit the gaps. A heap-based k-way merge avoids sorting everything."}),
    ],
    next_up="""
When no local rule is safe, you have to consider every option — affordably.
""",
)


# --- Unit 30 — 1-D dynamic programming --------------------------------------

_unit(
    "dp-1d", "Dynamic Programming I: One Dimension", "🧩", _S6,
    "Define the state, write the recurrence, and never compute it twice.",
    prereqs=["recursion", "complexity"],
    why="""
Dynamic programming is where most people stall, and the reason is almost always
that it gets taught as a list of problems rather than as a procedure. It is a
procedure, and it has four steps. Follow them and the code writes itself;
skip the first one and no amount of staring at the array will help.

The unit covers the one-dimensional case — a single index of state — because
that is where the four steps are visible. Every problem here is a recursion you
have already learned to write, plus a cache.
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

### The two directions of iteration

Coin change has two flavours that differ by one loop order:

- **Unbounded** (each coin reusable): iterate coins outside, amounts ascending
  inside.
- **0/1** (each item once): iterate items outside, capacity **descending**
  inside, so an item cannot be reused within its own pass.

Getting this backwards is the classic knapsack bug, and it is worth writing both
once to feel the difference.

### Counting versus optimising

If the question is *"how many ways"*, the recurrence **sums** instead of taking
a max, and the base case is 1 (there is exactly one way to do nothing). If it is
*"minimum number of"*, initialise with an infinity sentinel and guard against
adding to it.
""",
    signals=[
        _sig("“maximum / minimum / number of ways”, with choices at each step", "DP",
             "The trio of words that names the technique."),
        _sig("“contiguous subarray with the largest sum”", "`dp[i]` ending at i (Kadane)",
             "Extend or restart — the arrays unit's run counter, generalised."),
        _sig("“cannot take two adjacent”", "`dp[i] = max(dp[i-1], dp[i-2] + a[i])`",
             "Take it and skip back two, or skip it."),
        _sig("“fewest coins to make an amount”", "Unbounded knapsack",
             "Coins outside, amounts ascending inside."),
        _sig("“how many ways to make”", "The same table, summing",
             "Base case 1: one way to make nothing."),
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
        _sk("Unbounded knapsack (coin change)",
            "Fewest coins, or the number of ways.",
            """
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);            // a sentinel above any real answer
dp[0] = 0;
for (int c : coins)
    for (int a = c; a <= amount; a++)   // ASCENDING ⇒ reuse allowed
        dp[a] = Math.min(dp[a], dp[a - c] + 1);
return dp[amount] > amount ? -1 : dp[amount];
""",
            "For counting ways: `dp[a] += dp[a - c]`, with `dp[0] = 1`."),
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
        _cost("Coin change", "O(amount × coins)", "O(amount)", "Pseudo-polynomial."),
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
        _pit("Each item is used more than once in a 0/1 knapsack",
             "The capacity loop ran ascending, so an item could be re-consumed in its own pass.",
             "Iterate capacity **descending** for 0/1; ascending is the unbounded case."),
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
        _chk("What changes between unbounded and 0/1 knapsack?",
             "Only the inner loop direction. Ascending capacity allows an item to be reused "
             "within its own pass (unbounded); descending prevents it (0/1)."),
        _chk("How does a counting DP differ from an optimising one?",
             "It sums the transitions instead of taking a max or min, and the base case is 1 "
             "— there is exactly one way to do nothing."),
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
Two sequences, or a value plus a capacity, means two indices — and a table.
""",
)


# --- Unit 31 — 2-D dynamic programming --------------------------------------

_unit(
    "dp-2d", "Dynamic Programming II: Two Dimensions", "🗺️", _S6,
    "Two indices, a table, and a fill order that respects the recurrence.",
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

### Subset sum / 0-1 knapsack

`dp[i][w]` = can the first i items reach exactly w? Rolled to one dimension it
is the 1-D unit's descending loop:

```java
boolean[] dp = new boolean[target + 1];
dp[0] = true;
for (int x : nums)
    for (int w = target; w >= x; w--)       // DESCENDING ⇒ each item used once
        dp[w] |= dp[w - x];
```

The descending order is the entire 0/1 constraint, in one character.

### Intervals over a string

Palindromic problems are indexed by **(start, end)** and must be filled by
increasing length, because `dp[i][j]` depends on `dp[i+1][j-1]` — a shorter
interval:

```java
for (int len = 2; len <= n; len++)
    for (int i = 0; i + len - 1 < n; i++) {
        int j = i + len - 1;
        dp[i][j] = s.charAt(i) == s.charAt(j) && (len == 2 || dp[i + 1][j - 1]);
    }
```

Iterating i ascending and j ascending would read cells that are not yet
computed. When a recurrence points *inwards*, iterate by length.

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
        _sig("“can a subset reach exactly …”", "Boolean knapsack, descending capacity",
             "Descending is what makes it 0/1."),
        _sig("“palindromic substring / partition”", "`dp[i][j]` by interval, filled by length",
             "The recurrence points inwards."),
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
        _sk("0/1 subset sum, rolled",
            "Partition into equal halves, target reachability.",
            """
boolean[] dp = new boolean[target + 1];
dp[0] = true;
for (int x : nums)
    for (int w = target; w >= x; w--)        // descending: one use per item
        dp[w] |= dp[w - x];
return dp[target];
""",
            "Ascending here would let one item be used repeatedly."),
        _sk("Interval DP by length",
            "Palindromes, matrix chains, burst-balloon style problems.",
            """
for (int len = 2; len <= n; len++)
    for (int i = 0; i + len - 1 < n; i++) {
        int j = i + len - 1;
        dp[i][j] = (s.charAt(i) == s.charAt(j)) && (len == 2 || dp[i + 1][j - 1]);
    }
""",
            "Length-first, because `dp[i][j]` depends on a shorter interval inside it."),
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
        _cost("Subset sum", "O(n · target)", "O(target)", "Pseudo-polynomial."),
        _cost("Interval DP", "O(n²) or O(n³)", "O(n²)", "Depends on the transition."),
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
        _pit("Interval DP reads uncomputed cells",
             "The loops iterated `i` then `j` while the recurrence points inwards.",
             "Iterate by increasing interval length."),
        _pit("Subset sum allows an item twice",
             "The rolled loop ran ascending.",
             "Descend the capacity."),
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
        _chk("Why must interval DP be filled by increasing length?",
             "`dp[i][j]` depends on `dp[i+1][j-1]` — a strictly shorter interval — so all "
             "shorter intervals must already be computed."),
        _chk("What does the LIS tails array actually contain?",
             "For each length, the smallest possible final value of an increasing "
             "subsequence of that length. Its size is the LIS length, but its contents are "
             "not necessarily a subsequence of the input."),
        _chk("Ascending versus descending inner loop in a rolled knapsack — what is the "
             "difference?",
             "Ascending lets an item be reused within the same pass (unbounded); descending "
             "reads only the previous item's values, enforcing one use (0/1)."),
    ],
    interview="""
Two-sequence DP is asked constantly and is one of the few places where being
able to *draw the table* wins the interview. Fill a 3×3 example by hand while
explaining the three neighbours as replace, delete and insert; it takes ninety
seconds and it proves the recurrence in a way that code cannot. Offer the
rolled-row space optimisation at the end, after the table is right.
""",
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
        _rung("Stretch", "Harder base cases, inward recurrences, and a structural alternative.",
              ["edit-distance", "longest-palindrome-length", "partition-equal-subset-sum",
               "longest-increasing-subsequence"],
              {"edit-distance": "Draw a 3×3 table by hand before coding. The base cases are `i` and `j`, not zeros.",
               "longest-palindrome-length": "Interval DP, filled by length. Also solvable by expanding around each centre — worth writing both.",
               "partition-equal-subset-sum": "Subset sum for half the total. Odd totals are impossible; return early.",
               "longest-increasing-subsequence": "Do the O(n²) DP first, then the O(n log n) tails version — and be clear about what the tails array is not."}),
    ],
    next_up="""
One structure left, and it closes the loop: a tree whose paths are prefixes.
""",
)


# --- Unit 32 — Tries --------------------------------------------------------

_unit(
    "tries", "Tries (Prefix Trees)", "🌴", _S6,
    "When the structure of the key is the structure of the index.",
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

This is the last idea in the curriculum, and it is a fair summary of it: a
greedy walk (stage 6) over a tree (stage 5) indexed by bits (stage 3).

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
That is the curriculum. Every technique in the bank has been taught and every
problem placed — so from here the work is **revision**: the spaced-repetition
queue, the weakness filters in Browse, and re-solving the stretch rungs from
memory rather than from notes.
""",
)
