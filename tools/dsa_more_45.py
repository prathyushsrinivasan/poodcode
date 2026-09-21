# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 45 — what the two existing stage-8 units were missing.
#
#   static-range-sums         the Easy on-ramp `range-queries` never had
#   sparse-table-range-min    O(1) queries when nothing ever changes
#   range-assign-range-sum    lazy propagation: a range UPDATE, not a point one
#   suffix-array-order        every suffix, sorted
#   distinct-substrings-large the same question as the trie problem, one size up
#
# `range-queries` opened at Medium and named the sparse table and lazy
# propagation without building either; `string-matching` taught hashing and the
# Z-function but had no suffix array. These five close both gaps.
# ===========================================================================

_p(
    "static-range-sums", "Totals That Never Change", "Easy",
    topics=["Arrays"], subtopics=["Prefix Sums", "Range Queries"],
    companies=["Amazon", "Google"],
    shape="arr_q", ret="String",
    todo="build prefix[i+1] = prefix[i] + a[i] once, then answer each query as prefix[r+1] - prefix[l]",
    description=(
        "An array of `n` numbers never changes. Answer `q` questions, each asking for the sum "
        "of `a[l] … a[r]` inclusive, 0-based.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\nLine 3: `q`.\nNext `q` lines: `l r`.\n\n"
        "### Output\nOne line per query: the sum."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n-10^9 ≤ a[i] ≤ 10^9\n"
                "0 ≤ l ≤ r < n",
    hints=[
        "Adding up the range per query is O(n) each, so 200000 queries over 200000 elements is 4·10¹⁰ additions.",
        "Precompute one array: `prefix[i]` = the sum of the first `i` elements, with `prefix[0] = 0`.",
        "Then every query is one subtraction: `prefix[r + 1] - prefix[l]`. The `+1` and the extra leading zero are what make the l = 0 case need no special handling.",
    ],
    opt=("O(n + q)", "O(n)",
         "One pass to build the prefix array, then O(1) per query."),
    editorial=(
        "## The one thing this teaches\n**When nothing changes, precompute.** This is the "
        "baseline every structure in this unit is measured against, and it is unbeatable: O(n) "
        "to build, O(1) to answer, O(n) memory.\n\n"
        "## Approach\n```java\nlong[] prefix = new long[n + 1];\n"
        "for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];\n"
        "// query (l, r):\nprefix[r + 1] - prefix[l]\n```\n\n"
        "## Why the array is n + 1 long\n`prefix[0] = 0` is the sum of nothing. Without it, "
        "`l == 0` needs an `if`, and that `if` is where off-by-one bugs live. One extra slot "
        "removes the special case entirely.\n\n"
        "## What breaks it\nA single update. Changing `a[i]` invalidates every prefix from i "
        "onwards, so a rebuild is O(n) and a workload of interleaved updates and queries is "
        "O(n·q) again. That is the exact problem the rest of this unit exists to solve — "
        "a Fenwick tree gives up the O(1) query to make an update O(log n).\n\n"
        "## Choosing\n| Workload | Structure |\n| --- | --- |\n| No updates | Prefix sums — "
        "this problem |\n| Point updates, range sums | Fenwick tree |\n| Range updates, range "
        "sums | Two Fenwicks, or a lazy segment tree |\n| No updates, range *minimum* | Sparse "
        "table |\n\nBuilding a segment tree for a static array is not wrong, it is just eight "
        "times the code for a worse constant.\n\n"
        "## Overflow\n200000 values of 10⁹ reach 2·10¹⁴. The prefix array is "
        "`long`; an `int` one wraps long before the last element."
    ),
    py='''
def solve(a, queries):
    n = len(a)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + a[i]
    return "\\n".join(str(prefix[r + 1] - prefix[l]) for l, r in queries)
''',
    java='''
    static String solve(int[] a, int[][] queries) {
        int n = a.length;
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + a[i];
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < queries.length; i++) {
            if (i > 0) sb.append('\\n');
            sb.append(prefix[queries[i][1] + 1] - prefix[queries[i][0]]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n1 2 3 4 5\n3\n0 4\n1 3\n2 2\n"),
        ("Example 2", "4\n-1 -2 -3 -4\n2\n0 1\n2 3\n"),
    ],
    hidden=[
        ("A single element", "1\n7\n2\n0 0\n0 0\n"),
        ("Mixed signs", "6\n5 -3 2 -8 4 1\n4\n0 5\n1 2\n3 4\n5 5\n"),
        ("Large values", "5\n1000000000 1000000000 1000000000 1000000000 1000000000\n2\n0 4\n2 4\n"),
        ("Every prefix", "5\n2 4 6 8 10\n5\n0 0\n0 1\n0 2\n0 3\n0 4\n"),
        ("Every suffix", "4\n1 10 100 1000\n4\n0 3\n1 3\n2 3\n3 3\n"),
    ],
    expl=[
        "The whole array is 15, the middle three are 2 + 3 + 4 = 9, and a single element is itself.",
        "Two pairs from a negative array.",
    ],
    prereqs=[
        ("prefix_sum", "Cumulative sums, and the sentinel zero in front."),
        ("overflow", "10^9 values summed over 2·10^5 elements."),
    ],
)


_p(
    "sparse-table-range-min", "The Lowest in Any Stretch", "Medium",
    topics=["Arrays"], subtopics=["Sparse Table", "Range Queries", "Bit Manipulation"],
    companies=["Google", "Amazon"],
    shape="arr_q", ret="String",
    todo="precompute the minimum of every block of length 2^j; answer (l, r) with two overlapping blocks of the largest fitting power",
    description=(
        "An array of `n` numbers never changes. Answer `q` questions, each asking for the "
        "**minimum** of `a[l] … a[r]` inclusive, 0-based.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\nLine 3: `q`.\nNext `q` lines: `l r`.\n\n"
        "### Output\nOne line per query: the minimum."
    ),
    constraints="1 ≤ n ≤ 200000\n1 ≤ q ≤ 200000\n-10^9 ≤ a[i] ≤ 10^9\n"
                "0 ≤ l ≤ r < n",
    hints=[
        "Prefix sums do not work: a minimum cannot be undone, so there is nothing to subtract. A segment tree would answer in O(log n) — but with no updates, you can do better.",
        "Precompute `table[j][i]` = the minimum of the block of length 2^j starting at i. Each level is built from the one below by combining two half-blocks.",
        "A minimum does not care about double counting. So cover [l, r] with **two overlapping** blocks of the largest power 2^j that fits, one from l and one ending at r — one comparison per query.",
    ],
    opt=("O(n log n) build, O(1) per query", "O(n log n)",
         "log n levels of n blocks, then two lookups and a `min` per query."),
    editorial=(
        "## The one thing this teaches\n**Idempotence buys you O(1).** `min(x, x) = x`, so a "
        "range can be covered by two *overlapping* blocks and the overlap does no harm. Sums are "
        "not idempotent, which is exactly why there is no O(1) sparse table for sums.\n\n"
        "## The build\n```java\nint LOG = 1;\nwhile ((1 << LOG) <= n) LOG++;\n"
        "int[][] table = new int[LOG][n];\ntable[0] = a;\n"
        "for (int j = 1; j < LOG; j++)\n"
        "    for (int i = 0; i + (1 << j) <= n; i++)\n"
        "        table[j][i] = Math.min(table[j-1][i], table[j-1][i + (1 << (j-1))]);\n```\n\n"
        "## The query\n```java\nint len = r - l + 1;\n"
        "int j = 31 - Integer.numberOfLeadingZeros(len);   // floor(log2(len))\n"
        "return Math.min(table[j][l], table[j][r - (1 << j) + 1]);\n```\n"
        "The two blocks each have length 2^j ≥ len/2, so together they cover [l, r] "
        "completely — and they overlap in the middle, which costs nothing.\n\n"
        "## Computing the log fast\n`Integer.numberOfLeadingZeros` is a single instruction. "
        "A precomputed `log[1..n]` table (`log[i] = log[i/2] + 1`) is the portable version and "
        "just as fast; calling `Math.log` per query is neither, and its rounding is wrong at "
        "exact powers of two.\n\n"
        "## Where this sits\nBinary lifting's jump table, the k-th ancestor table and this one "
        "are the same idea: **precompute powers of two, combine at most two of them.** Once you "
        "see that, the sparse table is the k-th-ancestor table with `min` instead of \"follow "
        "the pointer\".\n\n"
        "## When not to use it\nAny update at all. A single change to `a[i]` invalidates "
        "O(log n) entries on every level and there is no cheap repair — that is a segment "
        "tree's job."
    ),
    py='''
def solve(a, queries):
    n = len(a)
    LOG = 1
    while (1 << LOG) <= n:
        LOG += 1
    table = [list(a)]
    for j in range(1, LOG):
        prev = table[j - 1]
        half = 1 << (j - 1)
        row = [0] * n
        span = 1 << j
        for i in range(n - span + 1):
            x, y = prev[i], prev[i + half]
            row[i] = x if x < y else y
        table.append(row)
    logs = [0] * (n + 1)
    for i in range(2, n + 1):
        logs[i] = logs[i >> 1] + 1
    out = []
    for l, r in queries:
        j = logs[r - l + 1]
        x, y = table[j][l], table[j][r - (1 << j) + 1]
        out.append(str(x if x < y else y))
    return "\\n".join(out)
''',
    java='''
    static String solve(int[] a, int[][] queries) {
        int n = a.length;
        int LOG = 1;
        while ((1 << LOG) <= n) LOG++;
        int[][] table = new int[LOG][];
        table[0] = a.clone();
        for (int j = 1; j < LOG; j++) {
            table[j] = new int[n];
            int half = 1 << (j - 1), span = 1 << j;
            for (int i = 0; i + span <= n; i++)
                table[j][i] = Math.min(table[j - 1][i], table[j - 1][i + half]);
        }
        int[] logs = new int[n + 1];
        for (int i = 2; i <= n; i++) logs[i] = logs[i >> 1] + 1;
        StringBuilder sb = new StringBuilder();
        for (int t = 0; t < queries.length; t++) {
            int l = queries[t][0], r = queries[t][1];
            int j = logs[r - l + 1];
            if (t > 0) sb.append('\\n');
            sb.append(Math.min(table[j][l], table[j][r - (1 << j) + 1]));
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6\n5 2 8 1 9 3\n3\n0 5\n0 2\n3 5\n"),
        ("Example 2", "4\n7 7 7 7\n2\n1 2\n0 3\n"),
    ],
    hidden=[
        ("A single element", "1\n-5\n2\n0 0\n0 0\n"),
        ("Already sorted", "5\n1 2 3 4 5\n4\n0 4\n1 4\n2 4\n4 4\n"),
        ("Descending", "5\n5 4 3 2 1\n3\n0 0\n0 2\n0 4\n"),
        ("Negative values", "6\n-1 -9 3 -4 8 -2\n4\n0 5\n1 1\n2 4\n4 5\n"),
        ("Exact powers of two", "8\n8 3 6 1 7 2 5 4\n5\n0 7\n0 3\n4 7\n2 5\n1 6\n"),
        ("Large values", "5\n1000000000 -1000000000 1000000000 -999999999 1000000000\n2\n0 4\n2 4\n"),
    ],
    expl=[
        "The whole array's minimum is 1; the first three are 5, 2, 8 with minimum 2; the last three are 1, 9, 3.",
        "Every element is the same, so every answer is 7.",
    ],
    prereqs=[
        ("bit_manip", "The largest power of two not exceeding a length."),
        ("dp", "Each level built from the level below."),
        ("prefix_max", "A running extremum over a block."),
    ],
)


_p(
    "range-assign-range-sum", "Repaint a Stretch, Then Total It", "Hard",
    topics=["Arrays"], subtopics=["Segment Tree", "Lazy Propagation", "Range Queries"],
    companies=["Google", "Meta"],
    shape="arr_ops", ret="String",
    todo="a segment tree where a node may carry a pending assignment for its whole range; push it down before descending",
    description=(
        "Process `q` operations on an array:\n\n"
        "- `assign l r v` — set **every** `a[i]` for `l ≤ i ≤ r` to `v`.\n"
        "- `sum l r` — print `a[l] + … + a[r]`.\n\n"
        "Ranges are inclusive and 0-based.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` starting values.\nLine 3: `q`.\n"
        "Next `q` lines: an operation.\n\n"
        "### Output\nOne line per `sum`."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ q ≤ 100000\n"
                "-10^9 ≤ a[i], v ≤ 10^9\n0 ≤ l ≤ r < n",
    hints=[
        "A Fenwick tree cannot do this. “Add v to a range” survives as a difference array; “set a range to v” destroys whatever was there, and the amount destroyed depends on the current contents.",
        "Use a segment tree, but do not walk down to the leaves: when a node's range is entirely inside [l, r], record the assignment **on that node** and stop. Its stored sum becomes `v × length`.",
        "That pending mark must be pushed to both children before you ever descend through the node again — otherwise a later query reads a stale child. Push down at the top of every recursive call.",
    ],
    opt=("O((n + q) log n)", "O(n)",
         "Each operation touches O(log n) nodes; a pending assignment is pushed one level at a time, only where it is needed."),
    editorial=(
        "## The one thing this teaches\n**Lazy propagation: do the work on the highest node "
        "that fully fits, and remember that you owe the children.** It is what turns a "
        "point-update tree into a range-update tree, and it is the reason a segment tree is more "
        "general than a Fenwick tree.\n\n"
        "## The node\n```java\nlong[] sum;      // the total of this node's range\n"
        "long[] lazyVal;  // the value its whole range was assigned\n"
        "boolean[] lazy;  // whether such an assignment is pending\n```\n"
        "A separate `boolean` is needed because `v` may legitimately be 0 — a sentinel value "
        "cannot distinguish \"assign 0\" from \"nothing pending\".\n\n"
        "## Apply and push\n```java\nvoid apply(int node, int lo, int hi, long v) {\n"
        "    sum[node] = v * (hi - lo + 1);\n    lazyVal[node] = v;\n    lazy[node] = true;\n}\n\n"
        "void push(int node, int lo, int hi) {\n    if (!lazy[node]) return;\n"
        "    int mid = (lo + hi) >>> 1;\n    apply(2*node, lo, mid, lazyVal[node]);\n"
        "    apply(2*node+1, mid+1, hi, lazyVal[node]);\n    lazy[node] = false;\n}\n```\n\n"
        "## Why assignment is easier than addition\nTwo pending assignments do not accumulate — "
        "the later one simply wins, so `apply` overwrites. Pending *additions* must be summed, "
        "and a tree that mixes both needs a defined composition order (an assignment cancels "
        "every pending addition beneath it). Getting that order wrong is the classic lazy bug.\n\n"
        "## Where `push` goes\nAt the top of every recursive `update` and `query`, before "
        "either descends. Forgetting it in `query` alone produces answers that are correct until "
        "the first range assignment and wrong afterwards — which small tests will not "
        "catch.\n\n"
        "## Why not two Fenwicks\nThe two-Fenwick trick for range-add-range-sum works because "
        "addition is linear in the update: the effect on a prefix is a linear function of the "
        "added value. Assignment is not — its effect depends on what was there. When the "
        "update is not an abelian-group operation, a lazy segment tree is the general tool, and "
        "that is precisely what the routing table meant."
    ),
    py='''
def solve(a, ops):
    n = len(a)
    size = 1
    while size < n:
        size <<= 1
    total = [0] * (2 * size)
    lazy_val = [0] * (2 * size)
    lazy_on = [False] * (2 * size)
    for i in range(n):
        total[size + i] = a[i]
    for i in range(size - 1, 0, -1):
        total[i] = total[2 * i] + total[2 * i + 1]

    def apply_node(node, lo, hi, v):
        total[node] = v * (hi - lo + 1)
        lazy_val[node] = v
        lazy_on[node] = True

    def push(node, lo, hi):
        if not lazy_on[node]:
            return
        mid = (lo + hi) // 2
        apply_node(2 * node, lo, mid, lazy_val[node])
        apply_node(2 * node + 1, mid + 1, hi, lazy_val[node])
        lazy_on[node] = False

    def update(node, lo, hi, l, r, v):
        if r < lo or hi < l:
            return
        if l <= lo and hi <= r:
            apply_node(node, lo, hi, v)
            return
        push(node, lo, hi)
        mid = (lo + hi) // 2
        update(2 * node, lo, mid, l, r, v)
        update(2 * node + 1, mid + 1, hi, l, r, v)
        total[node] = total[2 * node] + total[2 * node + 1]

    def query(node, lo, hi, l, r):
        if r < lo or hi < l:
            return 0
        if l <= lo and hi <= r:
            return total[node]
        push(node, lo, hi)
        mid = (lo + hi) // 2
        return query(2 * node, lo, mid, l, r) + query(2 * node + 1, mid + 1, hi, l, r)

    out = []
    for op in ops:
        if not op:
            continue
        if op[0] == "assign":
            update(1, 0, size - 1, int(op[1]), int(op[2]), int(op[3]))
        else:
            out.append(str(query(1, 0, size - 1, int(op[1]), int(op[2]))))
    return "\\n".join(out)
''',
    java='''
    static long[] total, lazyVal;
    static boolean[] lazyOn;
    static int segSize;

    static void applyNode(int node, int lo, int hi, long v) {
        total[node] = v * (hi - lo + 1);
        lazyVal[node] = v;
        lazyOn[node] = true;
    }

    static void push(int node, int lo, int hi) {
        if (!lazyOn[node]) return;
        int mid = (lo + hi) >>> 1;
        applyNode(2 * node, lo, mid, lazyVal[node]);
        applyNode(2 * node + 1, mid + 1, hi, lazyVal[node]);
        lazyOn[node] = false;
    }

    static void update(int node, int lo, int hi, int l, int r, long v) {
        if (r < lo || hi < l) return;
        if (l <= lo && hi <= r) { applyNode(node, lo, hi, v); return; }
        push(node, lo, hi);
        int mid = (lo + hi) >>> 1;
        update(2 * node, lo, mid, l, r, v);
        update(2 * node + 1, mid + 1, hi, l, r, v);
        total[node] = total[2 * node] + total[2 * node + 1];
    }

    static long query(int node, int lo, int hi, int l, int r) {
        if (r < lo || hi < l) return 0;
        if (l <= lo && hi <= r) return total[node];
        push(node, lo, hi);
        int mid = (lo + hi) >>> 1;
        return query(2 * node, lo, mid, l, r) + query(2 * node + 1, mid + 1, hi, l, r);
    }

    static String solve(int[] a, String[][] ops) {
        int n = a.length;
        segSize = 1;
        while (segSize < n) segSize <<= 1;
        total = new long[2 * segSize];
        lazyVal = new long[2 * segSize];
        lazyOn = new boolean[2 * segSize];
        for (int i = 0; i < n; i++) total[segSize + i] = a[i];
        for (int i = segSize - 1; i >= 1; i--) total[i] = total[2 * i] + total[2 * i + 1];
        StringBuilder sb = new StringBuilder();
        boolean first = true;
        for (String[] op : ops) {
            if (op.length == 0 || op[0].isEmpty()) continue;
            if (op[0].equals("assign")) {
                update(1, 0, segSize - 1, Integer.parseInt(op[1]), Integer.parseInt(op[2]),
                       Long.parseLong(op[3]));
            } else {
                if (!first) sb.append('\\n');
                first = false;
                sb.append(query(1, 0, segSize - 1, Integer.parseInt(op[1]), Integer.parseInt(op[2])));
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n1 2 3 4 5\n4\nsum 0 4\nassign 1 3 10\nsum 0 4\nsum 1 2\n"),
        ("Example 2", "3\n7 7 7\n2\nassign 0 2 0\nsum 0 2\n"),
    ],
    hidden=[
        ("A single element", "1\n5\n3\nsum 0 0\nassign 0 0 -3\nsum 0 0\n"),
        ("Overlapping assignments", "6\n1 1 1 1 1 1\n6\nassign 0 3 5\nassign 2 5 2\nsum 0 5\nsum 0 1\nsum 2 3\nsum 4 5\n"),
        ("Assign zero, which a sentinel would miss", "4\n9 9 9 9\n4\nassign 1 2 0\nsum 0 3\nsum 1 2\nsum 0 0\n"),
        ("Negative values", "5\n-1 -2 -3 -4 -5\n3\nsum 0 4\nassign 0 4 -1000000000\nsum 0 4\n"),
        ("Queries between every assignment", "8\n1 2 3 4 5 6 7 8\n7\nsum 0 7\nassign 0 0 100\nsum 0 3\nassign 4 7 -1\nsum 4 7\nsum 0 7\nsum 3 4\n"),
        ("A non-power-of-two length", "7\n1 1 1 1 1 1 1\n4\nassign 2 5 3\nsum 0 6\nsum 2 5\nsum 5 6\n"),
    ],
    expl=[
        "The array starts summing to 15. After setting positions 1 to 3 to 10 it is 1, 10, 10, 10, 5 — total 36, and positions 1 and 2 total 20.",
        "Assigning zero must actually store zero, not be mistaken for “no assignment pending”.",
    ],
    prereqs=[
        ("tree_basics", "A segment tree's node ranges."),
        ("recursion", "Descending, then combining the children."),
        ("overflow", "10^9 assigned across 10^5 positions."),
    ],
)


_p(
    "suffix-array-order", "Every Suffix, Sorted", "Medium",
    topics=["Strings", "Sorting"], subtopics=["Suffix Array", "Doubling", "Radix Sort"],
    companies=["Google", "Amazon"],
    shape="str", ret="String",
    todo="sort by first character, then repeatedly sort by (rank, rank at i + 2^k) until every rank is distinct",
    description=(
        "Print the **suffix array** of `s`: the starting positions of all `n` suffixes, "
        "ordered by the suffixes themselves in dictionary order.\n\n"
        "For `banana` the suffixes sort as `a`, `ana`, `anana`, `banana`, `na`, `nana`, so the "
        "answer is `5 3 1 0 4 2`.\n\n"
        "### Input\nOne line: `s`, lowercase letters.\n\n"
        "### Output\nThe `n` starting positions, separated by single spaces."
    ),
    constraints="1 ≤ |s| ≤ 100000\n`s` consists of lowercase English letters.",
    hints=[
        "Sorting the suffixes as strings is O(n² log n): each comparison can read n characters. The fix is to never compare characters after the first round.",
        "Sort by the first character and assign each suffix a rank. Now a suffix's first two characters are the pair `(rank[i], rank[i+1])` — sort by the pair and you have ranks for length 2.",
        "Double each round: length-2k ranks come from pairs of length-k ranks. After ⌈log₂ n⌉ rounds every rank is distinct, and each round is one sort of integer pairs.",
    ],
    opt=("O(n log² n)", "O(n)",
         "log n doubling rounds, each an O(n log n) sort of integer pairs; a radix sort makes it O(n log n)."),
    editorial=(
        "## The one thing this teaches\n**Doubling: compute the order for length 1, and every "
        "round squares the length you can compare in O(1).** The same trick as binary lifting "
        "and the sparse table, applied to \"how much of this suffix do I already know how to "
        "compare?\"\n\n"
        "## Approach\n```java\nInteger[] sa = indices sorted by s.charAt(i);\n"
        "int[] rank = ranksFrom(sa, single characters);\n\n"
        "for (int k = 1; k < n; k <<= 1) {\n"
        "    // key(i) = (rank[i], i + k < n ? rank[i + k] : -1)\n"
        "    sort sa by key;\n    rank = ranksFrom(sa, key);\n"
        "    if (rank[sa[n-1]] == n - 1) break;     // all distinct: nothing left to separate\n"
        "}\n```\n\n"
        "## Why the sentinel is −1\nA suffix that runs off the end has no second half. Giving "
        "it a rank *below* every real rank makes the shorter suffix sort first, which is exactly "
        "dictionary order: `an` comes before `ana`. Using 0 instead makes it tie with the "
        "lowest real rank and the order silently breaks on strings like `aab`.\n\n"
        "## Why equal ranks must stay equal\nRanks are assigned by *comparing consecutive keys*, "
        "not by position — two suffixes with the same first 2k characters must receive the "
        "same rank, or the next round's pairs are wrong. This is the step to check first when a "
        "suffix array comes out subtly mis-ordered.\n\n"
        "## The early exit\nOnce all n ranks are distinct, the order is final and further "
        "rounds change nothing. On a string of n distinct characters that is after round zero.\n\n"
        "## Why it is worth building\nWith a suffix array, \"does t occur in s?\" is two binary "
        "searches, the longest repeated substring is one pass over the LCP array, and so is the "
        "count of distinct substrings — the next problem. A rolling hash answers some of "
        "these; a suffix array answers all of them without a collision caveat."
    ),
    py='''
def solve(s):
    n = len(s)
    sa = sorted(range(n), key=lambda i: s[i])
    rank = [0] * n
    r = 0
    for idx in range(n):
        if idx > 0 and s[sa[idx]] != s[sa[idx - 1]]:
            r += 1
        rank[sa[idx]] = r
    k = 1
    while k < n and r < n - 1:
        def key(i, k=k):
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new_rank = [0] * n
        r = 0
        new_rank[sa[0]] = 0
        for idx in range(1, n):
            if key(sa[idx]) != key(sa[idx - 1]):
                r += 1
            new_rank[sa[idx]] = r
        rank = new_rank
        k <<= 1
    return " ".join(str(i) for i in sa)
''',
    java='''
    static int[] suffixArray(String s) {
        int n = s.length();
        Integer[] sa = new Integer[n];
        for (int i = 0; i < n; i++) sa[i] = i;
        final int[] rank = new int[n];
        for (int i = 0; i < n; i++) rank[i] = s.charAt(i);
        Arrays.sort(sa, (x, y) -> Integer.compare(rank[x], rank[y]));
        int[] cur = new int[n];
        int r = 0;
        cur[sa[0]] = 0;
        for (int i = 1; i < n; i++) {
            if (rank[sa[i]] != rank[sa[i - 1]]) r++;
            cur[sa[i]] = r;
        }
        System.arraycopy(cur, 0, rank, 0, n);
        for (int k = 1; k < n && r < n - 1; k <<= 1) {
            final int kk = k;
            Arrays.sort(sa, (x, y) -> {
                if (rank[x] != rank[y]) return Integer.compare(rank[x], rank[y]);
                int rx = x + kk < n ? rank[x + kk] : -1;
                int ry = y + kk < n ? rank[y + kk] : -1;
                return Integer.compare(rx, ry);
            });
            int[] next = new int[n];
            r = 0;
            next[sa[0]] = 0;
            for (int i = 1; i < n; i++) {
                int a = sa[i], b = sa[i - 1];
                int ra = a + kk < n ? rank[a + kk] : -1;
                int rb = b + kk < n ? rank[b + kk] : -1;
                if (rank[a] != rank[b] || ra != rb) r++;
                next[a] = r;
            }
            System.arraycopy(next, 0, rank, 0, n);
        }
        int[] out = new int[n];
        for (int i = 0; i < n; i++) out[i] = sa[i];
        return out;
    }

    static String solve(String s) {
        int[] sa = suffixArray(s);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < sa.length; i++) {
            if (i > 0) sb.append(' ');
            sb.append(sa[i]);
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "banana\n"), ("Example 2", "abcd\n")],
    hidden=[
        ("One character", "z\n"),
        ("All the same character", "aaaaa\n"),
        ("A shorter suffix is a prefix of a longer one", "aab\n"),
        ("Reverse alphabetical", "dcba\n"),
        ("A repeated block", "abababab\n"),
        ("Mixed", "mississippi\n"),
    ],
    expl=[
        "`a` < `ana` < `anana` < `banana` < `na` < `nana`, starting at 5, 3, 1, 0, 4, 2.",
        "Every suffix starts with a different letter, so one sort by first character is already final.",
    ],
    prereqs=[
        ("sorting", "Sorting by a key that is a pair."),
        ("string_basics", "Suffixes and dictionary order."),
        ("canonical", "Ranks as a canonical form for a prefix of a suffix."),
    ],
)


_p(
    "distinct-substrings-large", "Count the Substrings, at Scale", "Hard",
    topics=["Strings"], subtopics=["Suffix Array", "LCP Array", "Kasai's Algorithm", "Counting"],
    companies=["Google", "Amazon"],
    shape="str", ret="long",
    todo="build the suffix array and its LCP array; the answer is n(n+1)/2 minus the sum of the LCP array",
    description=(
        "Count the **distinct** non-empty substrings of `s`.\n\n"
        "This is the same question as the trie problem of the same name, with `|s|` up to "
        "100000 — a trie of every substring would hold 5·10⁹ nodes.\n\n"
        "### Input\nOne line: `s`, lowercase letters.\n\n"
        "### Output\nThe number of distinct non-empty substrings."
    ),
    constraints="1 ≤ |s| ≤ 100000\n`s` consists of lowercase English letters.",
    hints=[
        "Every substring is a prefix of some suffix. There are n(n+1)/2 such prefixes in total, so the only question is how many are counted twice.",
        "Sort the suffixes. Two suffixes share a prefix of length `lcp` — and if they are **adjacent in sorted order**, those `lcp` prefixes are exactly the ones already counted by the earlier suffix.",
        "So the answer is `n(n+1)/2 − Σ lcp[i]` over adjacent pairs. Build the LCP array with Kasai's algorithm, which is one pass.",
    ],
    opt=("O(n log² n)", "O(n)",
         "Dominated by the suffix array; Kasai's LCP pass and the sum are linear."),
    editorial=(
        "## The one thing this teaches\n**Count everything, then subtract the duplicates — "
        "and the sorted order tells you exactly where the duplicates are.** Sorting the suffixes "
        "puts every repeated prefix next to the only other place it is counted.\n\n"
        "## The formula\nEach suffix `sa[i]` contributes its `n − sa[i]` prefixes, but the "
        "first `lcp[i]` of them are shared with `sa[i-1]` and were already counted:\n\n"
        "> `answer = Σ (n − sa[i]) − Σ lcp[i] = n(n+1)/2 − Σ lcp[i]`\n\n"
        "## Kasai's algorithm\n```java\nint[] pos = inverse(sa);      // pos[i] = where suffix i sits\n"
        "int h = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    if (pos[i] == 0) { h = 0; continue; }\n"
        "    int j = sa[pos[i] - 1];\n"
        "    while (i + h < n && j + h < n && s.charAt(i + h) == s.charAt(j + h)) h++;\n"
        "    lcp[pos[i]] = h;\n    if (h > 0) h--;                 // the key line\n}\n```\n\n"
        "## Why Kasai is linear\nIt walks the suffixes by **starting position**, not by rank. "
        "Dropping the first character of a suffix can reduce its LCP with its neighbour by at "
        "most one — so `h` decreases at most n times in total and increases at most n times, "
        "and the inner `while` is O(1) amortized. Remove the `h--` and it is still correct and "
        "quadratic.\n\n"
        "## Why adjacent pairs are enough\nIn sorted order, the LCP of any two suffixes is the "
        "*minimum* of the LCPs along the run between them. So a prefix shared by three suffixes "
        "is shared by each adjacent pair too, and subtracting only the adjacent overlaps removes "
        "it exactly once per duplicate occurrence — not once per pair.\n\n"
        "## The scale\nn = 100000 gives n(n+1)/2 ≈ 5·10⁹ candidate substrings and an "
        "answer that does not fit in an `int`. The trie version of this problem enumerates them; "
        "this one never builds a single substring.\n\n"
        "## The follow-up\n\"Longest repeated substring\" is `max(lcp)`, and \"longest substring "
        "appearing in k strings\" is a sliding window over the LCP array of the concatenation. "
        "Once the LCP array exists, that whole family is a one-liner."
    ),
    py='''
def solve(s):
    n = len(s)
    sa = sorted(range(n), key=lambda i: s[i])
    rank = [0] * n
    r = 0
    for idx in range(n):
        if idx > 0 and s[sa[idx]] != s[sa[idx - 1]]:
            r += 1
        rank[sa[idx]] = r
    k = 1
    while k < n and r < n - 1:
        def key(i, k=k):
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new_rank = [0] * n
        r = 0
        new_rank[sa[0]] = 0
        for idx in range(1, n):
            if key(sa[idx]) != key(sa[idx - 1]):
                r += 1
            new_rank[sa[idx]] = r
        rank = new_rank
        k <<= 1
    pos = [0] * n
    for i, p in enumerate(sa):
        pos[p] = i
    h = 0
    lcp_total = 0
    for i in range(n):
        if pos[i] == 0:
            h = 0
            continue
        j = sa[pos[i] - 1]
        while i + h < n and j + h < n and s[i + h] == s[j + h]:
            h += 1
        lcp_total += h
        if h > 0:
            h -= 1
    return n * (n + 1) // 2 - lcp_total
''',
    java='''
    static int[] suffixArray(String s) {
        int n = s.length();
        Integer[] sa = new Integer[n];
        for (int i = 0; i < n; i++) sa[i] = i;
        final int[] rank = new int[n];
        for (int i = 0; i < n; i++) rank[i] = s.charAt(i);
        Arrays.sort(sa, (x, y) -> Integer.compare(rank[x], rank[y]));
        int[] cur = new int[n];
        int r = 0;
        cur[sa[0]] = 0;
        for (int i = 1; i < n; i++) {
            if (rank[sa[i]] != rank[sa[i - 1]]) r++;
            cur[sa[i]] = r;
        }
        System.arraycopy(cur, 0, rank, 0, n);
        for (int k = 1; k < n && r < n - 1; k <<= 1) {
            final int kk = k;
            Arrays.sort(sa, (x, y) -> {
                if (rank[x] != rank[y]) return Integer.compare(rank[x], rank[y]);
                int rx = x + kk < n ? rank[x + kk] : -1;
                int ry = y + kk < n ? rank[y + kk] : -1;
                return Integer.compare(rx, ry);
            });
            int[] next = new int[n];
            r = 0;
            next[sa[0]] = 0;
            for (int i = 1; i < n; i++) {
                int a = sa[i], b = sa[i - 1];
                int ra = a + kk < n ? rank[a + kk] : -1;
                int rb = b + kk < n ? rank[b + kk] : -1;
                if (rank[a] != rank[b] || ra != rb) r++;
                next[a] = r;
            }
            System.arraycopy(next, 0, rank, 0, n);
        }
        int[] out = new int[n];
        for (int i = 0; i < n; i++) out[i] = sa[i];
        return out;
    }

    static long solve(String s) {
        int n = s.length();
        int[] sa = suffixArray(s);
        int[] pos = new int[n];
        for (int i = 0; i < n; i++) pos[sa[i]] = i;
        long lcpTotal = 0;
        int h = 0;
        for (int i = 0; i < n; i++) {
            if (pos[i] == 0) { h = 0; continue; }
            int j = sa[pos[i] - 1];
            while (i + h < n && j + h < n && s.charAt(i + h) == s.charAt(j + h)) h++;
            lcpTotal += h;
            if (h > 0) h--;
        }
        return (long) n * (n + 1) / 2 - lcpTotal;
    }
''',
    examples=[("Example 1", "abab\n"), ("Example 2", "aaaa\n")],
    hidden=[
        ("One character", "q\n"),
        ("All distinct characters", "abcdef\n"),
        ("banana", "banana\n"),
        ("A repeated block", "abcabcabc\n"),
        ("Two characters only", "abbabbabba\n"),
        ("A longer mixed string", "mississippiriverbank\n"),
    ],
    expl=[
        "`a`, `b`, `ab`, `ba`, `aba`, `bab`, `abab` — seven distinct substrings out of ten prefixes of suffixes.",
        "Only `a`, `aa`, `aaa`, `aaaa`: four distinct, where a naive count would say ten.",
    ],
    prereqs=[
        ("sorting", "The suffix array underneath."),
        ("string_basics", "Every substring is a prefix of a suffix."),
        ("overflow", "n(n+1)/2 at n = 100000 exceeds an int."),
    ],
)
