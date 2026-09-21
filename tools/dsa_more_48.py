# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 48 — Order & Search, part 3: greedy and intervals.
#
#   cheapest-first-budget      the smallest greedy there is, and why it is right
#   weighted-completion-order  Smith's rule: an exchange argument becomes a comparator
#   min-max-lateness           earliest deadline first
#   job-deadlines-profit       latest free slot (or a heap of kept profits)
#   make-values-unique         sort, then push each value just past its neighbour
#   covered-length-union       merge, then add up the blocks
#   subtract-interval          insert-interval's three phases, trimming instead of growing
#   busiest-moment             a ±1 sweep that also reports WHEN
#   weighted-job-scheduling    where "sort by end" stops being greedy and becomes DP
#
# The greedy unit taught the exchange argument with no problem that needed one;
# the intervals unit never reached the weighted case, where greedy fails. These
# fill both.
# ===========================================================================


# --------------------------------------------------------------------- greedy

_p(
    "cheapest-first-budget", "Spend the Gift Card", "Easy",
    topics=["Greedy", "Sorting"], subtopics=["Greedy", "Sorting"],
    companies=["Amazon", "Walmart"],
    shape="arr_k", ret="long",
    todo="sort the prices and buy from the cheapest while the budget lasts",
    description=(
        "A gift card holds `k` credits. The shop has `n` different items with prices "
        "`p[i]`, one of each. Return the **maximum number of items** you can buy without "
        "going over the card's balance.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` prices.\n\n### Output\nThe maximum number of items."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ k ≤ 10^15\n1 ≤ p[i] ≤ 10^9",
    hints=[
        "To buy as many items as possible, which items should you prefer?",
        "Sort by price and buy from the cheapest until the next one does not fit. Stop there — every later item costs at least as much.",
        "The running total can reach 2·10¹⁴: keep it in a `long`.",
    ],
    opt=("O(n log n)", "O(1)",
         "One sort and one pass."),
    editorial=(
        "## The one thing this teaches\n**The exchange argument, at its smallest.** Suppose an "
        "optimal basket skips a cheap item c but contains a pricier item e. Swap e for c: the "
        "basket has the same size and costs less, so it is still within budget. Repeat, and "
        "some optimal basket is exactly the cheapest items — which is what the greedy buys.\n\n"
        "## Approach\n```java\nArrays.sort(p);\nlong spent = 0; int bought = 0;\n"
        "for (int x : p) {\n    if (spent + x > k) break;      // every later item is at least as dear\n"
        "    spent += x; bought++;\n}\n```\n\n"
        "## Why `break` and not `continue`\nThe array is sorted, so if x does not fit, nothing "
        "after it fits either. `continue` is still correct — just pointless work.\n\n"
        "## Counting sort?\nIf prices were small (say ≤ 10⁵), a counting sort would make this "
        "O(n + max). With prices up to 10⁹, the comparison sort is the right call.\n\n"
        "## Where it stops being this easy\nMaximise the *value* of the basket instead of the "
        "count and the greedy is wrong: that is 0/1 knapsack, and the exchange no longer "
        "preserves the objective."
    ),
    py='''
def solve(a, k):
    spent = bought = 0
    for x in sorted(a):
        if spent + x > k:
            break
        spent += x
        bought += 1
    return bought
''',
    java='''
    static long solve(int[] a, long k) {
        int[] p = a.clone();
        Arrays.sort(p);
        long spent = 0, bought = 0;
        for (int x : p) {
            if (spent + x > k) break;
            spent += x;
            bought++;
        }
        return bought;
    }
''',
    examples=[
        ("Example 1", "6 20\n8 3 12 5 1 9\n"),
        ("Example 2", "3 2\n5 3 4\n"),
    ],
    hidden=[
        ("Buy everything", "4 1000000000000000\n1000000000 1000000000 1000000000 1000000000\n"),
        ("Exactly the budget", "3 6\n1 2 3\n"),
        ("One item, too dear", "1 9\n10\n"),
        ("Duplicates", "7 10\n2 2 2 2 2 2 2\n"),
        ("Large total", "5 3000000000\n1000000000 999999999 1000000000 2 1\n"),
    ],
    expl=[
        "Buy 1, 3, 5 and 8 for 17 credits. The next cheapest, 9, would make it 26.",
        "The cheapest item costs 3, more than the card holds.",
    ],
    prereqs=[
        ("greedy", "Cheapest first; an exchange argument shows it is optimal."),
        ("sorting", "Sorting makes “cheapest remaining” a pointer, not a search."),
    ],
)


_p(
    "weighted-completion-order", "Order the Repairs", "Medium",
    topics=["Greedy", "Sorting"], subtopics=["Exchange Argument", "Custom Comparator", "Scheduling"],
    companies=["Google", "Amazon"],
    shape="pairs", ret="long",
    todo="sort jobs so x precedes y when t[x]·w[y] < t[y]·w[x] (cross-multiply in long), then total w·finish time",
    description=(
        "A single technician must do `n` repairs, one after another, starting at time 0. "
        "Repair `i` takes `t[i]` hours, and each hour a customer waits costs `w[i]` — so if "
        "repair `i` finishes at time `C[i]`, it costs `w[i] · C[i]`.\n\n"
        "Choose the order of repairs to **minimise the total cost** `Σ w[i] · C[i]`, and "
        "return that minimum.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `t w`.\n\n### Output\nThe minimum total cost."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ t[i], w[i] ≤ 1000",
    hints=[
        "Try every order? n! of them. Instead, compare just two **adjacent** repairs x then y in some order. Swapping them affects nobody else — why?",
        "Everyone before them finishes at the same time either way, and so does everyone after (the pair takes t_x + t_y either way). So only the pair's own cost changes. x first costs extra w_y · t_x; y first costs extra w_x · t_y.",
        "So x should go first exactly when t_x · w_y < t_y · w_x. Sort by that comparator — cross-multiplied, in `long`, never as a `double` ratio.",
    ],
    opt=("O(n log n)", "O(n)",
         "One comparator sort, then one pass accumulating finish times."),
    editorial=(
        "## The one thing this teaches\n**How to turn an exchange argument into a "
        "comparator.** For any “in what order?” problem where swapping two neighbours affects "
        "only those two, compare the two orders of the pair directly and sort by whichever is "
        "cheaper. This is Smith's rule (1956).\n\n"
        "## The swap\nLet x and y be adjacent, with S the time when the first of them starts.\n\n"
        "| Order | x finishes | y finishes | Pair's cost |\n| --- | --- | --- | --- |\n"
        "| x, y | S + t_x | S + t_x + t_y | w_x(S + t_x) + w_y(S + t_x + t_y) |\n"
        "| y, x | S + t_y + t_x | S + t_y | w_y(S + t_y) + w_x(S + t_y + t_x) |\n\n"
        "Subtract: x-first minus y-first = w_y·t_x − w_x·t_y. So x first is better iff "
        "**t_x · w_y < t_y · w_x** — equivalently t_x / w_x < t_y / w_y, “shortest weighted "
        "time first”.\n\n"
        "## Approach\n```java\nInteger[] idx = ...;   // 0..n-1\n"
        "Arrays.sort(idx, (x, y) -> Long.compare((long) t[x] * w[y], (long) t[y] * w[x]));\n"
        "long time = 0, cost = 0;\nfor (int j : idx) { time += t[j]; cost += (long) w[j] * time; }\n```\n\n"
        "## Why not compare ratios as doubles?\nTwo different ratios can round to the same "
        "double, and equal ratios can round differently; neither breaks *this* answer much, but "
        "an inconsistent comparator can make Timsort throw. Cross-multiplication is exact.\n\n"
        "## Ties\nEqual ratios cost the same in either order — the difference above is zero — "
        "so the tie-break does not affect the answer.\n\n"
        "## Magnitude\nFinish times reach 10⁵ · 10³ = 10⁸, each cost term 10¹¹, the total "
        "10¹⁶. `long` throughout."
    ),
    py='''
def solve(p):
    from functools import cmp_to_key
    def cmp(x, y):
        a, b = x[0] * y[1], y[0] * x[1]
        return (a > b) - (a < b)
    time = cost = 0
    for t, w in sorted(p, key=cmp_to_key(cmp)):
        time += t
        cost += w * time
    return cost
''',
    java='''
    static long solve(int[][] p) {
        int n = p.length;
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        Arrays.sort(idx, (x, y) -> Long.compare((long) p[x][0] * p[y][1], (long) p[y][0] * p[x][1]));
        long time = 0, cost = 0;
        for (int j : idx) {
            time += p[j][0];
            cost += (long) p[j][1] * time;
        }
        return cost;
    }
''',
    examples=[
        ("Example 1", "3\n3 1\n1 2\n2 2\n"),
        ("Example 2", "2\n4 4\n2 2\n"),
    ],
    hidden=[
        ("One repair", "1\n1000 1000\n"),
        ("All weights equal: shortest first", "4\n5 1\n1 1\n3 1\n2 1\n"),
        ("All times equal: heaviest first", "4\n1 3\n1 9\n1 1\n1 5\n"),
        ("Ratio beats both keys", "3\n10 9\n1 1\n6 5\n"),
        ("Largest values", "3\n1000 1000\n1000 1\n1 1000\n"),
        ("Mixed", "6\n7 3\n2 8\n5 5\n9 1\n1 1\n4 6\n"),
    ],
    expl=[
        "Ratios t/w: 3, 0.5, 1. Order (1,2), (2,2), (3,1) finishes at 1, 3, 6: cost 2 + 6 + 6 = 14.",
        "Both repairs have ratio 1, so either order costs the same: 2·2 + 4·6 = 28.",
    ],
    prereqs=[
        ("greedy", "The exchange argument on an adjacent pair decides the comparator."),
        ("sorting", "A comparator that compares cross-products, not a key."),
        ("overflow", "Costs reach 10^16; cross-products must be computed in long."),
    ],
)


_p(
    "min-max-lateness", "Least Late", "Medium",
    topics=["Greedy", "Sorting"], subtopics=["Exchange Argument", "Scheduling", "Earliest Deadline First"],
    companies=["Amazon", "Microsoft"],
    shape="pairs", ret="long",
    todo="run the tasks in order of deadline; track the finish time and the largest (finish − deadline)",
    description=(
        "You have `n` tasks. Task `i` takes `d[i]` hours and is due at hour `due[i]`. You work "
        "on one task at a time, starting at hour 0, with no breaks. A task's **lateness** is "
        "`max(0, finish − due)`.\n\n"
        "Choose an order that **minimises the largest lateness**, and return that value.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `d due`.\n\n### Output\nThe minimum possible "
        "maximum lateness."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ d[i] ≤ 10^4\n0 ≤ due[i] ≤ 2·10^9",
    hints=[
        "Shortest task first? Try d = [1, 10] with due = [100, 10] — it makes the long task late for no reason.",
        "Compare two adjacent tasks where the one with the later deadline goes first. Swapping them cannot make the maximum lateness worse — the pair finishes at the same time either way, and the task with the earlier deadline now finishes sooner.",
        "So sort by deadline (earliest deadline first) and simulate. Lateness depends only on the order, not on durations beyond their sum.",
    ],
    opt=("O(n log n)", "O(n)",
         "A sort by deadline and one pass."),
    editorial=(
        "## The one thing this teaches\n**The exchange argument decides the sort key, and the "
        "obvious key is often wrong.** Shortest-first minimises the *sum* of completion times; "
        "it does nothing for the *worst* lateness. Earliest deadline first (EDF) does.\n\n"
        "## The exchange\nTake any order with an *inversion*: adjacent tasks x then y with "
        "due_x > due_y. Swap them. Everyone else is unaffected. After the swap, y finishes "
        "earlier than before, and x finishes at the time y used to — the pair's end, F. So x's "
        "new lateness is F − due_x < F − due_y, which was y's old lateness. The maximum cannot "
        "rise. Removing inversions one at a time turns any optimal order into EDF without making "
        "it worse, so EDF is optimal.\n\n"
        "## Approach\n```java\nArrays.sort(tasks, Comparator.comparingInt(t -> t[1]));   // by due\n"
        "long time = 0, worst = 0;\nfor (int[] t : tasks) {\n    time += t[0];\n"
        "    worst = Math.max(worst, time - t[1]);\n}\nreturn worst;\n```\n\n"
        "## Magnitude\nTotal work is at most 2·10⁵ · 10⁴ = 2·10⁹ hours, and deadlines reach "
        "2·10⁹. Both overflow `int` arithmetic — `long` for the clock.\n\n"
        "## Related\nIf tasks may be *skipped* and you maximise the number finished on time, "
        "EDF alone is not enough: you also drop the longest task whenever you fall behind "
        "(Moore–Hodgson, a heap). That is the regret variant from the heaps unit."
    ),
    py='''
def solve(p):
    time = worst = 0
    for d, due in sorted(p, key=lambda x: x[1]):
        time += d
        worst = max(worst, time - due)
    return worst
''',
    java='''
    static long solve(int[][] p) {
        int[][] t = p.clone();
        Arrays.sort(t, (x, y) -> Integer.compare(x[1], y[1]));
        long time = 0, worst = 0;
        for (int[] x : t) {
            time += x[0];
            worst = Math.max(worst, time - x[1]);
        }
        return worst;
    }
''',
    examples=[
        ("Example 1", "4\n3 6\n2 8\n1 9\n4 9\n"),
        ("Example 2", "2\n1 100\n10 10\n"),
    ],
    hidden=[
        ("One task, on time", "1\n5 5\n"),
        ("One task, late", "1\n5 2\n"),
        ("All due at zero", "3\n2 0\n3 0\n1 0\n"),
        ("Generous deadlines", "3\n1 2000000000\n1 2000000000\n1 2000000000\n"),
        ("Shortest-first would lose", "3\n1 50\n8 8\n4 13\n"),
        ("Large clock", "3\n10000 0\n10000 5000\n10000 25000\n"),
    ],
    expl=[
        "By deadline: finish at 3, 5, 6, 10 against 6, 8, 9, 9. Only the last is late, by 1.",
        "Do the 10-hour task first: it finishes exactly at 10, and the short task finishes at 11, long before 100.",
    ],
    prereqs=[
        ("greedy", "An exchange argument on inverted neighbours proves earliest-deadline-first."),
        ("sorting", "Sort by deadline, not by duration."),
    ],
)


_p(
    "job-deadlines-profit", "Paid Before the Deadline", "Medium",
    topics=["Greedy", "Sorting"], subtopics=["Scheduling", "Latest Free Slot", "Union-Find"],
    companies=["Amazon", "Flipkart"],
    shape="pairs", ret="long",
    todo="take jobs by profit descending, each into the latest free hour on or before its deadline",
    description=(
        "You have `n` one-hour jobs. Job `i` pays `profit[i]` if it is done in some hour slot "
        "`1 … deadline[i]` (slot `s` covers the hour ending at time `s`). You can do one job per "
        "slot, and you may skip jobs. Return the **maximum total profit**.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `deadline profit`.\n\n### Output\nThe maximum "
        "total profit."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ deadline[i] ≤ 100000\n1 ≤ profit[i] ≤ 10^9",
    hints=[
        "Consider jobs from the most profitable down. A job should be taken if any slot on or before its deadline is still free.",
        "Which free slot? The **latest** one on or before the deadline. Taking an early slot could block a later job with an early deadline; taking the latest blocks as little as possible.",
        "Scanning backwards for the latest free slot is O(deadline) per job. A union-find where each slot points to the latest free slot at or before it makes it nearly O(1).",
    ],
    opt=("O(n log n)", "O(n + D)",
         "A sort by profit, then near-constant union-find lookups over D = max deadline slots."),
    editorial=(
        "## The one thing this teaches\n**A greedy order plus a greedy placement — and both "
        "matter.** Taking jobs by profit is only optimal if each is placed where it hurts the "
        "future least: the latest free slot before its deadline.\n\n"
        "## Approach A: latest free slot\n```java\nsort jobs by profit, descending\n"
        "for each job (dl, pr):\n    s = latest free slot <= dl      // union-find: find(dl)\n"
        "    if (s > 0) { take it; union s with s - 1 }\n```\n"
        "`find(s)` returns the latest free slot ≤ s. When slot s is used, link it to s − 1, so "
        "the next search skips it — path compression makes every lookup nearly O(1).\n\n"
        "## Approach B: a heap of kept profits\nSort by **deadline**. Keep a min-heap of the "
        "profits of accepted jobs. Push each job; if the heap now holds more jobs than the "
        "current deadline allows, pop the smallest profit. At the end, the heap is the best "
        "set. This is the “regret” greedy — accept tentatively, evict the worst when a "
        "constraint breaks — and it gives the same answer.\n\n"
        "## Why latest, not earliest\nJobs A (deadline 2, profit 10) and B (deadline 1, profit "
        "9). By profit, A comes first. Put A in slot 1 and B has nowhere to go: 10. Put A in slot "
        "2 and B fits in slot 1: 19.\n\n"
        "## Magnitude\nUp to 10⁵ jobs of 10⁹ each: 10¹⁴. `long`."
    ),
    py='''
def solve(p):
    # heap-of-kept-profits formulation (independent of the Java reference's union-find)
    kept = []
    for dl, pr in sorted(p):
        heapq.heappush(kept, pr)
        if len(kept) > dl:
            heapq.heappop(kept)
    return sum(kept)
''',
    java='''
    static int[] parent;

    static int find(int s) {
        while (parent[s] != s) { parent[s] = parent[parent[s]]; s = parent[s]; }
        return s;
    }

    static long solve(int[][] p) {
        int maxD = 0;
        for (int[] j : p) maxD = Math.max(maxD, j[0]);
        parent = new int[maxD + 1];
        for (int i = 0; i <= maxD; i++) parent[i] = i;
        int[][] jobs = p.clone();
        Arrays.sort(jobs, (x, y) -> Integer.compare(y[1], x[1]));
        long total = 0;
        for (int[] j : jobs) {
            int s = find(j[0]);
            if (s > 0) {
                total += j[1];
                parent[s] = s - 1;
            }
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "5\n2 40\n1 25\n2 30\n3 10\n1 50\n"),
        ("Example 2", "2\n2 10\n1 9\n"),
    ],
    hidden=[
        ("One job", "1\n1 1000000000\n"),
        ("All share deadline 1", "4\n1 5\n1 9\n1 2\n1 7\n"),
        ("Room for everything", "3\n5 1\n5 2\n5 3\n"),
        ("Late deadlines, few jobs", "3\n100000 7\n100000 8\n99999 9\n"),
        ("Crowded", "7\n3 20\n1 5\n3 15\n2 10\n2 25\n3 1\n1 30\n"),
        ("Large profits", "4\n2 1000000000\n2 1000000000\n2 999999999\n4 1000000000\n"),
    ],
    expl=[
        "Take 50 (slot 1), 40 (slot 2) and 10 (slot 3): 100. The 30 and 25 jobs cannot fit before their deadlines once the better jobs are placed.",
        "Put the 10 in slot 2 — its latest possible slot — and the 9 still fits in slot 1: 19.",
    ],
    prereqs=[
        ("greedy", "Profit order, latest-free-slot placement."),
        ("union_find", "Each used slot links to the one before it, so the next free slot is one find() away."),
        ("heap", "The alternative: keep accepted profits in a min-heap and evict the smallest on overflow."),
    ],
)


_p(
    "make-values-unique", "Every Badge Number Distinct", "Medium",
    topics=["Greedy", "Sorting"], subtopics=["Greedy", "Sorting"],
    companies=["Google", "Amazon"],
    shape="arr", ret="long",
    todo="sort; walk left to right keeping `need` = previous value + 1, raise each value to at least `need`, summing the raises",
    description=(
        "Employees have badge numbers `a[i]`, and several may share one. In one step you "
        "may **increase** one badge number by 1 (numbers can never decrease). Return the "
        "**minimum number of steps** to make all badge numbers distinct.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe minimum number of steps."
    ),
    constraints="1 ≤ n ≤ 200000\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "After sorting, each value must end strictly above the final value of the one before it.",
        "Raise each value only as far as it has to go: to `max(a[i], previous final + 1)`. Raising further never helps anyone after it.",
        "The total can reach about n²/2 ≈ 2·10¹⁰ — `long`.",
    ],
    opt=("O(n log n)", "O(1) extra",
         "A sort and one pass."),
    editorial=(
        "## The one thing this teaches\n**Sort, then make the cheapest locally forced "
        "move.** In sorted order, the i-th value has to end above the (i − 1)-th, and pushing "
        "it the minimum amount leaves the most room for everything after it — a stays-ahead "
        "argument: after each step, the greedy's last value is as small as any valid "
        "assignment's could be.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong steps = 0, need = Long.MIN_VALUE;\n"
        "for (int x : a) {\n    long v = Math.max(x, need);     // lowest legal final value\n"
        "    steps += v - x;\n    need = v + 1;\n}\n```\n\n"
        "## Why sorting does not change the answer\nThe values are a multiset — only how many "
        "of each matter, not where they sit — so any order may be processed. Sorted order is "
        "the one where “the previous final value” is the only constraint.\n\n"
        "## Counting-sort variant\nIf values were ≤ 10⁵, count them and carry the excess "
        "upward: `extra = cnt[v] − 1` duplicates move to v + 1, costing `extra` steps each "
        "level. O(n + max), no sort.\n\n"
        "## Overflow\n2·10⁵ copies of the same value need 0 + 1 + … + (n − 1) ≈ 2·10¹⁰ steps."
    ),
    py='''
def solve(a):
    steps = 0
    need = -1
    for x in sorted(a):
        v = max(x, need)
        steps += v - x
        need = v + 1
    return steps
''',
    java='''
    static long solve(int[] a) {
        int[] s = a.clone();
        Arrays.sort(s);
        long steps = 0, need = Long.MIN_VALUE;
        for (int x : s) {
            long v = Math.max(x, need);
            steps += v - x;
            need = v + 1;
        }
        return steps;
    }
''',
    examples=[
        ("Example 1", "6\n4 1 4 2 1 7\n"),
        ("Example 2", "3\n9 3 6\n"),
    ],
    hidden=[
        ("One badge", "1\n0\n"),
        ("All the same", "5\n2 2 2 2 2\n"),
        ("Near the top", "3\n1000000000 1000000000 1000000000\n"),
        ("Cascade", "6\n0 0 1 1 2 2\n"),
        ("Gaps absorb duplicates", "5\n1 1 10 10 20\n"),
        ("Unsorted input", "7\n5 3 5 3 5 3 0\n"),
    ],
    expl=[
        "Sorted: 1 1 2 4 4 7 → 1 2 3 4 5 7. The raises are 0+1+1+0+1+0 = 3.",
        "Already distinct: 0 steps.",
    ],
    prereqs=[
        ("greedy", "Raise each value only as far as the previous one forces."),
        ("sorting", "In sorted order the only constraint on a value is its predecessor."),
    ],
)


# ------------------------------------------------------------------ intervals

_p(
    "covered-length-union", "Painted Length of the Fence", "Easy",
    topics=["Intervals", "Sorting"], subtopics=["Merge Intervals", "Union Length"],
    companies=["Google", "Amazon"],
    shape="pairs", ret="long",
    todo="sort by start, merge overlapping [s, e) stretches, and add up the merged lengths",
    description=(
        "`n` painters each painted a stretch `[s, e)` of a long fence (from mark `s` up to, "
        "but not including, mark `e`). Stretches may overlap. Return the **total length of "
        "fence that has paint on it**.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `s e`.\n\n### Output\nThe painted length."
    ),
    constraints="1 ≤ n ≤ 200000\n0 ≤ s < e ≤ 10^9",
    hints=[
        "Adding up every `e − s` counts overlapping parts more than once.",
        "Merge first: sort by start, then extend the current block while the next stretch starts at or before its end.",
        "The answer is the sum of the merged blocks' lengths. With half-open stretches, [1, 3) and [3, 5) touch but do not overlap — merging them or not gives the same total.",
    ],
    opt=("O(n log n)", "O(1) extra",
         "A sort by start, then one merging pass that adds each finished block's length."),
    editorial=(
        "## The one thing this teaches\n**Merge, then read the answer off the merged "
        "blocks.** Union length, free time and “is point x covered?” are all questions about "
        "the merged set, never about the raw intervals.\n\n"
        "## Approach\n```java\nArrays.sort(iv, Comparator.comparingInt(x -> x[0]));\n"
        "long total = 0;\nlong curS = iv[0][0], curE = iv[0][1];\nfor (int[] x : iv) {\n"
        "    if (x[0] <= curE) curE = Math.max(curE, x[1]);  // extend (max: nesting)\n"
        "    else { total += curE - curS; curS = x[0]; curE = x[1]; }\n}\n"
        "total += curE - curS;                               // the last block\n```\n\n"
        "## Two classic slips\n1. `curE = x[1]` instead of `Math.max` — a stretch nested "
        "inside the current block would *shrink* it.\n2. Forgetting to add the final block "
        "after the loop.\n\n"
        "## The sweep alternative\nEvents `+1` at s and `−1` at e, sorted; add the gap to the "
        "next event whenever the active count is positive. Same O(n log n), and it generalises "
        "to “length covered by at least k painters”.\n\n"
        "## Magnitude\nThe union is at most 10⁹, but summing raw lengths (the wrong answer) "
        "could reach 2·10¹⁴ — a hint that `long` is the habit to keep."
    ),
    py='''
def solve(p):
    iv = sorted(p)
    total = 0
    cs, ce = iv[0]
    for s, e in iv[1:]:
        if s <= ce:
            ce = max(ce, e)
        else:
            total += ce - cs
            cs, ce = s, e
    return total + ce - cs
''',
    java='''
    static long solve(int[][] p) {
        int[][] iv = p.clone();
        Arrays.sort(iv, (x, y) -> Integer.compare(x[0], y[0]));
        long total = 0, cs = iv[0][0], ce = iv[0][1];
        for (int[] x : iv) {
            if (x[0] <= ce) ce = Math.max(ce, x[1]);
            else { total += ce - cs; cs = x[0]; ce = x[1]; }
        }
        return total + ce - cs;
    }
''',
    examples=[
        ("Example 1", "4\n2 7\n10 12\n5 9\n11 15\n"),
        ("Example 2", "3\n0 10\n3 4\n6 8\n"),
    ],
    hidden=[
        ("One stretch", "1\n0 1000000000\n"),
        ("Touching", "3\n1 3\n3 5\n5 9\n"),
        ("Disjoint", "3\n40 50\n0 5\n20 21\n"),
        ("Identical", "4\n7 9\n7 9\n7 9\n7 9\n"),
        ("Unsorted with nesting", "6\n50 60\n1 100\n20 30\n150 151\n99 150\n0 1\n"),
        ("Huge, overlapping", "3\n0 1000000000\n0 1000000000\n500000000 1000000000\n"),
    ],
    expl=[
        "[2, 7) and [5, 9) merge into [2, 9), length 7; [10, 12) and [11, 15) into [10, 15), length 5. Total 12.",
        "Both short stretches lie inside [0, 10), so the answer is 10.",
    ],
    prereqs=[
        ("intervals", "Merge overlapping intervals, then sum the merged lengths."),
        ("sorting", "Sort by start so only the last block can overlap the next."),
    ],
)


_p(
    "subtract-interval", "Cancel a Block of Time", "Medium",
    topics=["Intervals"], subtopics=["Insert Interval", "Interval Subtraction"],
    companies=["Google", "Microsoft"],
    shape="pairs_xy", ret="String",
    todo="walk the sorted list: keep what lies outside [x, y), trimming an overlapping interval into up to two pieces",
    description=(
        "A calendar is a list of **sorted, disjoint** busy blocks `[a, b)`. You cancel "
        "everything in `[x, y)`. Return the busy blocks that remain, still sorted.\n\n"
        "A block that overlaps `[x, y)` keeps only its parts outside it — which may be "
        "nothing, one piece, or two pieces.\n\n"
        "### Input\nLine 1: `n x y`.\nNext `n` lines: `a b`, sorted, disjoint, `a < b`.\n\n"
        "### Output\nOne remaining block per line, as `a b`. If nothing remains, print `empty`."
    ),
    constraints="1 ≤ n ≤ 200000\n0 ≤ a < b ≤ 10^9\n0 ≤ x < y ≤ 10^9",
    hints=[
        "The list is already sorted and disjoint — do not sort it again. One pass is enough.",
        "For each block, the part before the cut is `[a, min(b, x))` and the part after is `[max(a, y), b)`. Emit each only if it is non-empty.",
        "That one rule handles every case: a block entirely before or after the cut survives whole, a block inside it vanishes, and a block around it splits in two.",
    ],
    opt=("O(n)", "O(n) output",
         "One pass over a list that is already in order."),
    editorial=(
        "## The one thing this teaches\n**Insert-interval's three phases, turned inside out.** "
        "Inserting *grows* the overlapping block; subtracting *trims* it. Both exploit the same "
        "guarantee — the input is sorted and disjoint — and neither needs a sort.\n\n"
        "## One rule for every block\n```java\nfor (int[] blk : cal) {\n"
        "    int a = blk[0], b = blk[1];\n"
        "    if (a < Math.min(b, x)) out.add(new int[]{ a, Math.min(b, x) });   // left piece\n"
        "    if (Math.max(a, y) < b) out.add(new int[]{ Math.max(a, y), b });   // right piece\n}\n```\n"
        "A block entirely left of the cut has `min(b, x) = b`, so the left piece is the whole "
        "block and the right piece is empty. A block entirely right of it is the mirror. A "
        "block covering the cut produces both pieces — in order, left first, so the output "
        "stays sorted.\n\n"
        "## Half-open intervals\nWith `[a, b)`, the pieces `[a, x)` and `[y, b)` are exactly "
        "what remains; no ±1 adjustments anywhere. That is the argument for half-open ranges: "
        "the arithmetic of cutting and joining has no special cases.\n\n"
        "## The three-phase view\nIf you prefer the insert-interval structure: copy blocks "
        "ending at or before x, trim the ones overlapping `[x, y)`, copy the rest. The single "
        "rule above is those three loops collapsed — correct because the trim formulae are "
        "harmless on the blocks that do not overlap."
    ),
    py='''
def solve(p, x, y):
    out = []
    for a, b in p:
        if a < min(b, x):
            out.append(f"{a} {min(b, x)}")
        if max(a, y) < b:
            out.append(f"{max(a, y)} {b}")
    return "\\n".join(out) if out else "empty"
''',
    java='''
    static String solve(int[][] p, int x, int y) {
        StringBuilder sb = new StringBuilder();
        for (int[] blk : p) {
            int a = blk[0], b = blk[1];
            int l = Math.min(b, x);
            if (a < l) sb.append(sb.length() > 0 ? "\\n" : "").append(a).append(' ').append(l);
            int r = Math.max(a, y);
            if (r < b) sb.append(sb.length() > 0 ? "\\n" : "").append(r).append(' ').append(b);
        }
        return sb.length() == 0 ? "empty" : sb.toString();
    }
''',
    examples=[
        ("Example 1", "4 5 12\n1 3\n4 7\n9 10\n11 20\n"),
        ("Example 2", "1 3 6\n0 10\n"),
    ],
    hidden=[
        ("Cut misses everything", "2 50 60\n0 10\n70 80\n"),
        ("Cut removes everything", "3 0 1000000000\n1 2\n5 9\n100 200\n"),
        ("Cut touches edges only", "2 10 20\n5 10\n20 25\n"),
        ("Exactly one block", "3 4 8\n1 2\n4 8\n9 12\n"),
        ("Cut inside a gap", "2 5 7\n0 5\n7 9\n"),
        ("Clips both ends", "3 3 14\n0 5\n6 8\n12 20\n"),
    ],
    expl=[
        "[1, 3) survives; [4, 7) keeps [4, 5); [9, 10) vanishes; [11, 20) keeps [12, 20).",
        "The cut lies inside the one block, which splits into [0, 3) and [6, 10).",
    ],
    prereqs=[
        ("intervals", "Sorted, disjoint input: one pass, like insert-interval."),
    ],
)


_p(
    "busiest-moment", "The Busiest Moment", "Medium",
    topics=["Intervals", "Sorting"], subtopics=["Sweep Line", "Peak Concurrency"],
    companies=["Amazon", "Uber"],
    shape="pairs", ret="String",
    todo="sweep ±1 events sorted by time with ends before starts; record the peak and the first time it is reached",
    description=(
        "A server logs `n` sessions, each active during `[s, e)`. Find the **largest number "
        "of sessions active at the same moment**, and the **earliest moment** at which that "
        "many are active.\n\n"
        "A session ending at time `t` is no longer active at `t`; one starting at `t` is.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `s e`.\n\n### Output\nOne line: `peak time`."
    ),
    constraints="1 ≤ n ≤ 200000\n0 ≤ s < e ≤ 10^9",
    hints=[
        "The number of active sessions changes only at a start or an end. Turn each session into two events: `+1` at s and `−1` at e.",
        "Sort events by time; at equal times process the `−1`s first, because a session ending at t is not active at t.",
        "Walk the events keeping a running count. When it exceeds the best so far, record the count *and the event's time*. Using strictly greater keeps the earliest time.",
    ],
    opt=("O(n log n)", "O(n)",
         "Sorting 2n events, then one pass."),
    editorial=(
        "## The one thing this teaches\n**A sweep answers *when*, not just *how many*.** The "
        "heap-of-end-times method computes the peak but loses the moment; the event sweep "
        "visits moments in order, so the moment is simply the current event's time.\n\n"
        "## Approach\n```java\nlong[] ev = new long[2 * n];\nfor (int i = 0; i < n; i++) {\n"
        "    ev[2 * i]     = (long) s[i] * 2 + 1;   // start: odd  → sorts after an end at s\n"
        "    ev[2 * i + 1] = (long) e[i] * 2;       // end:   even\n}\nArrays.sort(ev);\n"
        "int cur = 0, best = 0; long when = 0;\nfor (long x : ev) {\n"
        "    if ((x & 1) == 1) { if (++cur > best) { best = cur; when = x / 2; } }\n"
        "    else cur--;\n}\n```\n"
        "Packing (time, type) into one `long` — `time · 2 + type` — sorts by time and puts ends "
        "(type 0) before starts (type 1) at the same time, with a primitive sort and no "
        "comparator.\n\n"
        "## Why the peak is reached at a start\nThe count only rises at starts, so the first "
        "moment of any maximum is a start time. That is why recording on `+1` events is "
        "enough.\n\n"
        "## The tie rule, again\nProcess a start before an end at the same time and back-to-"
        "back sessions look concurrent: the peak can be one too high and the moment wrong."
    ),
    py='''
def solve(p):
    ev = []
    for s, e in p:
        ev.append((s, 1))
        ev.append((e, 0))
    ev.sort()
    cur = best = 0
    when = 0
    for t, kind in ev:
        if kind == 1:
            cur += 1
            if cur > best:
                best, when = cur, t
        else:
            cur -= 1
    return f"{best} {when}"
''',
    java='''
    static String solve(int[][] p) {
        int n = p.length;
        long[] ev = new long[2 * n];
        for (int i = 0; i < n; i++) {
            ev[2 * i] = (long) p[i][0] * 2 + 1;
            ev[2 * i + 1] = (long) p[i][1] * 2;
        }
        Arrays.sort(ev);
        int cur = 0, best = 0;
        long when = 0;
        for (long x : ev) {
            if ((x & 1) == 1) {
                if (++cur > best) { best = cur; when = x / 2; }
            } else cur--;
        }
        return best + " " + when;
    }
''',
    examples=[
        ("Example 1", "5\n1 6\n2 4\n5 9\n3 7\n8 10\n"),
        ("Example 2", "3\n0 5\n5 10\n10 15\n"),
    ],
    hidden=[
        ("One session", "1\n42 43\n"),
        ("All identical", "4\n3 9\n3 9\n3 9\n3 9\n"),
        ("Peak reached twice", "4\n1 3\n2 4\n10 13\n11 14\n"),
        ("Nested", "4\n0 100\n10 90\n20 80\n30 70\n"),
        ("Unsorted input", "5\n50 60\n0 10\n55 70\n5 58\n57 59\n"),
        ("Large times", "3\n999999998 1000000000\n0 999999999\n999999997 999999999\n"),
    ],
    expl=[
        "At time 3, sessions [1, 6), [2, 4) and [3, 7) are all active — 3 at once, the most ever. It happens first at 3.",
        "Each session ends exactly when the next starts, so no two ever overlap: peak 1, first at time 0.",
    ],
    prereqs=[
        ("intervals", "A ±1 sweep over the endpoints: the count changes only there."),
        ("sorting", "Sort events by time, ends before starts at equal times."),
    ],
)


def _wjs_big():
    s_ = _lcg_ints(31, 3000, 0, 10**9 - 1)
    ln = _lcg_ints(37, 3000, 1, 5 * 10**6)
    w = _lcg_ints(41, 3000, 1, 10**9)
    rows = [(s, min(10**9, s + l), x) for s, l, x in zip(s_, ln, w)]
    return "3000\n" + "".join(f"{a} {b} {c}\n" for a, b, c in rows)


_p(
    "weighted-job-scheduling", "Most Valuable Bookings", "Hard",
    topics=["Intervals", "Dynamic Programming", "Binary Search"],
    subtopics=["Weighted Interval Scheduling", "Binary Search", "1D DP"],
    companies=["Google", "Amazon", "Airbnb"],
    shape="triples", ret="long",
    todo="sort by end; best[i] = max(best[i-1], w_i + best[j]) where j = number of bookings ending at or before start_i (binary search)",
    description=(
        "A hall receives `n` booking requests. Request `i` wants the hall during `[s, e)` "
        "and pays `w`. Accept a set of requests that **do not overlap** (one ending at `t` and "
        "another starting at `t` is fine) and **maximise the total payment**.\n\n"
        "### Input\nLine 1: `n`.\nNext `n` lines: `s e w`.\n\n### Output\nThe maximum total payment."
    ),
    constraints="1 ≤ n ≤ 100000\n0 ≤ s < e ≤ 10^9\n1 ≤ w ≤ 10^9",
    hints=[
        "Sort by end time and keep the most bookings? That maximises the *count*. One long booking paying 100 can beat three short ones paying 1 each — greedy is wrong here.",
        "Sort by end. Let best[i] be the best total using only the first i bookings. Booking i is either skipped — best[i − 1] — or taken, together with the best total among bookings that end by the time it starts.",
        "Because the ends are sorted, “bookings ending at or before s_i” is a prefix, and its length j is one binary search (upper bound of s_i in the ends). best[i] = max(best[i − 1], w_i + best[j]).",
    ],
    opt=("O(n log n)", "O(n)",
         "A sort, then one binary search and one `max` per booking."),
    editorial=(
        "## The one thing this teaches\n**Where greedy stops.** Unweighted interval "
        "scheduling is greedy by end time; add weights and no local rule works. The fix keeps "
        "everything else — the sort by end, the idea of a compatible prefix — and replaces the "
        "greedy choice with a `max`.\n\n"
        "## The recurrence\nSort by end: e₁ ≤ e₂ ≤ … ≤ eₙ. Let p(i) be the number of bookings "
        "whose end is ≤ sᵢ — they are exactly the ones compatible with taking booking i, and "
        "because ends are sorted they form the prefix 1 … p(i).\n\n"
        "```\nbest[0] = 0\nbest[i] = max(best[i − 1],          // skip booking i\n"
        "              wᵢ + best[p(i)])       // take it\n```\n\n"
        "## Approach\n```java\nArrays.sort(b, Comparator.comparingInt(x -> x[1]));\n"
        "int[] ends = ...;                      // b[i][1], sorted\nlong[] best = new long[n + 1];\n"
        "for (int i = 1; i <= n; i++) {\n    int j = upperBound(ends, b[i - 1][0]);   // # ends <= start\n"
        "    best[i] = Math.max(best[i - 1], b[i - 1][2] + best[j]);\n}\nreturn best[n];\n```\n\n"
        "## The boundary\nUpper bound, not lower: a booking ending exactly at sᵢ is compatible "
        "and must be in the prefix. With lower bound it is excluded, and back-to-back bookings "
        "are never combined.\n\n"
        "## Why not greedy by value, or by value per hour?\nBy value: one 10-paying booking "
        "can block two 9-paying ones. By value per hour: a short, dense booking can block a "
        "long one worth more in total. Every local rule has a counterexample — which is the "
        "signal that the choice needs a table.\n\n"
        "## Magnitude\n10⁵ bookings of 10⁹: totals to 10¹⁴. `long`."
    ),
    py='''
def solve(t):
    b = sorted(t, key=lambda x: x[1])
    ends = [x[1] for x in b]
    best = [0] * (len(b) + 1)
    for i, (s, e, w) in enumerate(b, 1):
        j = bisect_right(ends, s)
        best[i] = max(best[i - 1], w + best[j])
    return best[-1]
''',
    java='''
    static long solve(int[][] t) {
        int n = t.length;
        int[][] b = t.clone();
        Arrays.sort(b, (x, y) -> Integer.compare(x[1], y[1]));
        int[] ends = new int[n];
        for (int i = 0; i < n; i++) ends[i] = b[i][1];
        long[] best = new long[n + 1];
        for (int i = 1; i <= n; i++) {
            int s = b[i - 1][0];
            int lo = 0, hi = n;                 // first index with ends[idx] > s
            while (lo < hi) {
                int mid = (lo + hi) >>> 1;
                if (ends[mid] <= s) lo = mid + 1; else hi = mid;
            }
            best[i] = Math.max(best[i - 1], b[i - 1][2] + best[lo]);
        }
        return best[n];
    }
''',
    examples=[
        ("Example 1", "6\n1 4 5\n3 6 6\n5 8 5\n2 10 15\n7 11 4\n9 12 3\n"),
        ("Example 2", "3\n0 3 4\n3 6 4\n6 9 4\n"),
    ],
    hidden=[
        ("One booking", "1\n0 1000000000 1000000000\n"),
        ("One heavy beats many light", "4\n0 10 100\n0 2 30\n2 5 30\n5 10 30\n"),
        ("Many light beat one heavy", "4\n0 10 80\n0 2 30\n2 5 30\n5 10 30\n"),
        ("All overlapping", "4\n0 10 5\n1 11 7\n2 12 6\n3 13 4\n"),
        ("Back to back only", "3\n0 5 1\n5 10 1\n10 15 1\n"),
        ("Identical intervals", "3\n4 8 2\n4 8 9\n4 8 5\n"),
        ("3000 random bookings", _wjs_big()),
    ],
    expl=[
        "[2, 10) alone pays 15. The most bookings that fit — [1, 4), [5, 8), [9, 12) — pay only 13.",
        "The three bookings touch end to start, so all fit: 12.",
    ],
    prereqs=[
        ("intervals", "Sorting by end makes every compatible set a prefix."),
        ("binary_search", "The prefix length is an upper bound over the sorted ends."),
        ("dp", "best[i] = max(skip, take) — the choice greedy cannot make."),
    ],
)
