# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 27 — lists, a trie, counting DPs and graph edges with direction.
#
#   insertion-sort-list          splice each node into a sorted prefix behind a dummy head
#   delete-middle-node           fast pointer starts two ahead so slow stops before the middle
#   double-number-list           a digit's carry depends only on the NEXT digit being ≥ 5
#   maximum-xor-with-element     sort queries by limit; insert values into a binary trie as they qualify
#   count-unreachable-pairs      pairs across components: sum of size × (nodes seen before)
#   knight-dialer                DP over the last digit pressed
#   domino-tromino-tiling        f(n) = 2 f(n−1) + f(n−3)
#   broken-calculator            work backwards from the target: halve when even
#   min-reorder-roads            orient the tree from 0 and count edges pointing away
#   reachable-nodes-subdivided   Dijkstra on the original nodes; each edge contributes from both ends
# ===========================================================================

_p(
    "insertion-sort-list", "Insertion Sort List", "Medium",
    topics=["Linked Lists", "Sorting"], subtopics=["Insertion Sort"], companies=["Microsoft"],
    shape="list", ret="ListNode", todo="detach each node and walk a dummy-headed sorted list to find where it belongs",
    description=(
        "Sort a singly linked list using **insertion sort**: take nodes one at a time and splice "
        "each into its place in a growing sorted list.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\nThe sorted list, values separated by spaces (or `EMPTY`)."
    ),
    constraints="0 ≤ n ≤ 5000\n-5000 ≤ value ≤ 5000",
    hints=[
        "An array insertion sort shifts elements; a list just relinks one node.",
        "Keep a dummy node in front of the sorted part, so inserting before the first node is not a special case.",
        "For each node: save next, walk from the dummy while the following value is smaller, splice the node in, continue with the saved next.",
    ],
    opt=("O(n²)", "O(1)", "Each insertion scans the sorted prefix; no extra nodes are created."),
    editorial=(
        "## The one thing this teaches\n**A dummy head removes the \"insert at the front\" case.** "
        "Every splice needs the node *before* the insertion point. With a dummy in front, that "
        "node always exists — even when the new value is the smallest so far.\n\n"
        "## Approach\n```java\nListNode dummy = new ListNode(0, null);\nListNode cur = head;\n"
        "while (cur != null) {\n    ListNode next = cur.next;               // save before relinking\n"
        "    ListNode p = dummy;\n    while (p.next != null && p.next.val < cur.val) p = p.next;\n"
        "    cur.next = p.next;                      // splice between p and p.next\n    p.next = cur;\n"
        "    cur = next;\n}\nreturn dummy.next;\n```\n\n"
        "## Equal values\nThe scan above uses `<`, so a node is inserted *before* equal values "
        "already placed. Scanning with `<=` inserts it after them instead, keeping equal values in "
        "their original order — a stable sort. For plain integers the output is identical; for "
        "records sorted by a key, only `<=` preserves their order.\n\n"
        "## When it is the right tool\nInsertion sort is O(n) on nearly sorted input. For "
        "general lists, merge sort reaches O(n log n) with the same O(1) relinking."
    ),
    py='''
def solve(head):
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    return build(sorted(vals))
''',
    java='''
    static ListNode solve(ListNode head) {
        ListNode dummy = new ListNode(0, null);
        ListNode cur = head;
        while (cur != null) {
            ListNode next = cur.next;
            ListNode p = dummy;
            while (p.next != null && p.next.val <= cur.val) p = p.next;
            cur.next = p.next;
            p.next = cur;
            cur = next;
        }
        return dummy.next;
    }
''',
    examples=[("Example 1", "4\n4 2 1 3\n"), ("Example 2", "5\n-1 5 3 4 0\n")],
    hidden=[
        ("Single node", "1\n1\n"),
        ("Empty list", "0\n"),
        ("Duplicates", "5\n2 2 1 3 1\n"),
        ("Already sorted", "4\n1 2 3 4\n"),
        ("Reverse sorted", "5\n5 4 3 2 1\n"),
    ],
    expl=[
        "Insert 4; 2 goes before it; 1 before both; 3 between 2 and 4.",
        "Negative and zero values sort like any others.",
    ],
    prereqs=[
        ("list_basics", "Relinking a node with a saved next pointer and a dummy head."),
        ("sorting", "Insertion sort: growing a sorted prefix one element at a time."),
    ],
)

_p(
    "delete-middle-node", "Delete the Middle Node of a Linked List", "Medium",
    topics=["Linked Lists", "Two Pointers"], subtopics=["Fast and Slow Pointers"], companies=["Amazon", "Microsoft"],
    shape="list", ret="ListNode", todo="start fast two nodes ahead so slow stops just before the middle; unlink slow.next",
    description=(
        "Delete the middle node of the list and print the result. For a list of length `n`, the "
        "middle node is at index `⌊n / 2⌋` (0-based).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\nThe list after deletion (or `EMPTY`)."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ value ≤ 10^5",
    hints=[
        "Counting the length and walking again takes two passes. One is enough.",
        "A slow pointer moving one step while a fast pointer moves two reaches the middle when fast reaches the end.",
        "To delete, you need the node BEFORE the middle. Start fast two nodes ahead of slow, and handle n = 1 separately.",
    ],
    opt=("O(n)", "O(1)", "One pass with two pointers."),
    editorial=(
        "## The one thing this teaches\n**Offset the fast pointer to land one node earlier.** "
        "Middle of the List stops slow *on* the middle. Deleting needs the predecessor, so give "
        "fast a head start of one extra step and slow ends up exactly one node behind.\n\n"
        "## Approach\n```java\nif (head.next == null) return null;            // n = 1\n"
        "ListNode slow = head, fast = head.next.next;\n"
        "while (fast != null && fast.next != null) {\n    slow = slow.next;\n    fast = fast.next.next;\n}\n"
        "slow.next = slow.next.next;                     // unlink the middle\nreturn head;\n```\n\n"
        "## Checking the index\n| n | middle ⌊n/2⌋ | slow stops at |\n|---|---|---|\n"
        "| 2 | 1 | 0 |\n| 4 | 2 | 1 |\n| 7 | 3 | 2 |\n\n"
        "Slow always stops at index `⌊n/2⌋ − 1`, the predecessor.\n\n"
        "## The one-node list\nThere is no predecessor to relink, and the result is empty — the "
        "only case the loop cannot handle."
    ),
    py='''
def solve(head):
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    del vals[len(vals) // 2]
    return build(vals)
''',
    java='''
    static ListNode solve(ListNode head) {
        if (head.next == null) return null;
        ListNode slow = head, fast = head.next.next;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        slow.next = slow.next.next;
        return head;
    }
''',
    examples=[("Example 1", "7\n1 3 4 7 1 2 6\n"), ("Example 2", "4\n1 2 3 4\n"), ("Example 3", "2\n2 1\n")],
    hidden=[
        ("Single node", "1\n5\n"),
        ("Three nodes", "3\n1 2 3\n"),
        ("Five nodes", "5\n10 20 30 40 50\n"),
    ],
    expl=[
        "n = 7, so index 3 (the 7) is removed.",
        "n = 4, so index 2 (the 3) is removed.",
        "n = 2, so index 1 (the 1) is removed.",
    ],
    prereqs=[
        ("fast_slow", "Two pointers at different speeds, with a head start that shifts where slow stops."),
        ("list_basics", "Unlinking a node through its predecessor."),
    ],
)

_p(
    "double-number-list", "Double a Number Represented as a Linked List", "Medium",
    topics=["Linked Lists", "Math"], subtopics=["Carry"], companies=["Amazon"],
    shape="list", ret="ListNode", todo="each digit becomes (2d) % 10 plus 1 if the next digit is ≥ 5; prepend a 1 if the first digit is ≥ 5",
    description=(
        "The list holds the digits of a non-negative number, most significant first, with no "
        "leading zeros (except the number 0 itself). Double the number and print its digits.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` digits.\n\n"
        "### Output\nThe digits of twice the number."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ digit ≤ 9",
    hints=[
        "Carries move toward the head, but the list only moves toward the tail. Reversing it is one fix.",
        "When doubling, the carry into a digit is 0 or 1 — and it is 1 exactly when the next digit is at least 5 (2 · 5 = 10).",
        "So a single forward pass works: digit = (2 · digit) % 10 + (next ≥ 5 ? 1 : 0). A new leading 1 is needed when the first digit is ≥ 5.",
    ],
    opt=("O(n)", "O(1)", "One pass; at most one new node."),
    editorial=(
        "## The one thing this teaches\n**Find how far a carry can travel.** Adding two arbitrary "
        "numbers can carry through a long run of 9s. Doubling cannot: `2 · 9 + 1 = 19` still "
        "carries only 1, and whether a carry arrives depends on the next digit alone — so no "
        "reversal is needed.\n\n"
        "## Approach\n```java\nif (head.val >= 5) head = new ListNode(0, head);   // room for the new leading 1\n"
        "for (ListNode p = head; p != null; p = p.next) {\n"
        "    int carry = (p.next != null && p.next.val >= 5) ? 1 : 0;\n"
        "    p.val = (p.val * 2) % 10 + carry;\n}\nreturn head;\n```\n\n"
        "## Why the carry never overflows the digit\n`(2d) % 10` is even — at most 8 — so adding a "
        "carry of 1 gives at most 9.\n\n"
        "## Walkthrough: 9 9 9\nPrepend 0 (first digit ≥ 5): `0 9 9 9`. Then 0 → 0 + 1, "
        "9 → 8 + 1, 9 → 8 + 1, 9 → 8 + 0: `1 9 9 8`."
    ),
    py='''
def solve(head):
    digits = []
    while head:
        digits.append(str(head.val))
        head = head.next
    doubled = 2 * int("".join(digits))
    return build([int(ch) for ch in str(doubled)])
''',
    java='''
    static ListNode solve(ListNode head) {
        if (head.val >= 5) head = new ListNode(0, head);
        for (ListNode p = head; p != null; p = p.next) {
            int carry = (p.next != null && p.next.val >= 5) ? 1 : 0;
            p.val = (p.val * 2) % 10 + carry;
        }
        return head;
    }
''',
    examples=[("Example 1", "3\n1 8 9\n"), ("Example 2", "3\n9 9 9\n")],
    hidden=[
        ("Zero", "1\n0\n"),
        ("Carry creates a digit", "1\n5\n"),
        ("No carries", "4\n1 2 3 4\n"),
        ("Long number", "20\n4 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 9 5\n"),
    ],
    expl=[
        "189 × 2 = 378.",
        "999 × 2 = 1998.",
    ],
    prereqs=[
        ("list_basics", "Walking a list while looking one node ahead."),
        ("math_digits", "Carries in doubling are at most 1 and depend only on the next digit."),
    ],
)

_p(
    "maximum-xor-with-element", "Maximum XOR With an Element From Array", "Hard",
    topics=["Tries", "Bit Manipulation", "Sorting"], subtopics=["Binary Trie", "Offline Queries"], companies=["Google"],
    shape="arr_q", ret="String", todo="sort values and queries by limit; insert values ≤ limit into a binary trie, then walk it greedily preferring the opposite bit",
    description=(
        "For each query `(x, m)`, print the maximum of `x XOR a[j]` over all elements with "
        "`a[j] ≤ m`, or `-1` if no element is at most `m`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n- Line 3: `q`.\n- Next `q` lines: `x m`.\n\n"
        "### Output\n`q` lines: the answers in query order."
    ),
    constraints="1 ≤ n, q ≤ 10^5\n0 ≤ a[j], x, m ≤ 10^9",
    hints=[
        "Without the limit m, this is Maximum XOR Pair: a binary trie, walked from the top bit, choosing the opposite bit whenever possible.",
        "The limit changes per query. Answer queries in increasing order of m, so the set of allowed values only grows.",
        "Sort values and queries by limit. Before each query, insert every value ≤ m into the trie. If the trie is empty, answer −1. Store answers by original query index.",
    ],
    opt=("O((n + q) · 30 + n log n + q log q)", "O(n · 30)", "Sorting, then 30 trie steps per insert and per query."),
    editorial=(
        "## The one thing this teaches\n**Offline queries: reorder them so the data only grows.** "
        "A trie supports inserts cheaply but not \"ignore values above m\". Sorting the queries "
        "by m turns the filter into a sequence of inserts, and the original order is restored "
        "at the end.\n\n"
        "## Approach\n```java\nsort a ascending;\nsort query indices by m;\nint next = 0;\n"
        "for (int qi : sortedQueries) {\n"
        "    while (next < n && a[next] <= m[qi]) insert(a[next++]);\n"
        "    answer[qi] = next == 0 ? -1 : bestXor(x[qi]);\n}\n\n"
        "int bestXor(int x) {\n    Node node = root; int result = 0;\n"
        "    for (int b = 29; b >= 0; b--) {\n        int want = ((x >> b) & 1) ^ 1;          // the opposite bit makes this bit 1\n"
        "        if (node.child[want] != null) { result |= 1 << b; node = node.child[want]; }\n"
        "        else node = node.child[want ^ 1];\n    }\n    return result;\n}\n```\n\n"
        "## Why greedy from the top bit\nA 1 in bit b outweighs every lower bit combined "
        "(2^b > 2^b − 1). So whenever the opposite bit exists, taking it is always right.\n\n"
        "## 30 bits\nValues up to 10^9 < 2^30 fit in bits 29..0."
    ),
    py='''
def solve(a, queries):
    out = []
    for x, m in queries:
        allowed = [v for v in a if v <= m]
        out.append(str(max(x ^ v for v in allowed)) if allowed else "-1")
    return "\\n".join(out)
''',
    java='''
    static int[][] child;
    static int nodes;

    static void insert(int v) {
        int cur = 0;
        for (int b = 29; b >= 0; b--) {
            int bit = (v >> b) & 1;
            if (child[cur][bit] == 0) child[cur][bit] = ++nodes;
            cur = child[cur][bit];
        }
    }

    static int bestXor(int x) {
        int cur = 0, result = 0;
        for (int b = 29; b >= 0; b--) {
            int want = ((x >> b) & 1) ^ 1;
            if (child[cur][want] != 0) { result |= 1 << b; cur = child[cur][want]; }
            else cur = child[cur][want ^ 1];
        }
        return result;
    }

    static String solve(int[] a, int[][] queries) {
        int n = a.length, q = queries.length;
        int[] sorted = a.clone();
        Arrays.sort(sorted);
        child = new int[n * 30 + 1][2];
        nodes = 0;
        Integer[] order = new Integer[q];
        for (int i = 0; i < q; i++) order[i] = i;
        Arrays.sort(order, (i, j) -> Integer.compare(queries[i][1], queries[j][1]));
        long[] answer = new long[q];
        int next = 0;
        for (int qi : order) {
            while (next < n && sorted[next] <= queries[qi][1]) insert(sorted[next++]);
            answer[qi] = next == 0 ? -1 : bestXor(queries[qi][0]);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < q; i++) { if (i > 0) sb.append('\\n'); sb.append(answer[i]); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n0 1 2 3 4\n3\n3 1\n1 3\n5 6\n"),
        ("Example 2", "6\n5 2 4 6 6 3\n3\n12 4\n8 1\n6 3\n"),
    ],
    hidden=[
        ("Limit below everything", "2\n7 9\n2\n5 6\n5 7\n"),
        ("Single value", "1\n0\n2\n0 0\n1000000000 1000000000\n"),
        ("Large values", "3\n1000000000 536870912 123456789\n3\n0 1000000000\n1073741823 600000000\n999999999 100\n"),
        ("Queries out of order", "4\n1 2 4 8\n4\n15 8\n15 1\n15 4\n0 2\n"),
    ],
    expl=[
        "Query (3, 1): values 0 and 1 give 3 and 2, so 3. Query (1, 3): 1 XOR 2 = 3. Query (5, 6): 5 XOR 2 = 7.",
        "Query (12, 4): 12 XOR 3 = 15. Query (8, 1): nothing is ≤ 1. Query (6, 3): 6 XOR 3 = 5.",
    ],
    prereqs=[
        ("trie", "A binary trie over the bits of the values, walked greedily from the top."),
        ("sorting", "Answering queries offline in order of their limit."),
    ],
)

_p(
    "count-unreachable-pairs", "Count Unreachable Pairs of Nodes", "Medium",
    topics=["Union-Find", "Graphs"], subtopics=["Component Sizes"], companies=["Amazon"],
    shape="graph", ret="long", todo="find component sizes; each component pairs with all nodes in components counted before it",
    description=(
        "An undirected graph has `n` nodes. Print the number of pairs of distinct nodes `{u, v}` "
        "with **no path** between them.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`.\n\n"
        "### Output\nThe number of unreachable pairs."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ m ≤ 2·10^5\nNo self-loops or repeated edges",
    hints=[
        "Two nodes are unreachable exactly when they are in different components.",
        "If the component sizes are s1, s2, …, the answer depends only on those sizes.",
        "Process components one by one: a component of size s forms s × (nodes already processed) new pairs. Use long — with no edges the answer is about 5·10^9.",
    ],
    opt=("O(n + m · α(n))", "O(n)", "Union-find over the edges, then one pass over component sizes."),
    editorial=(
        "## The one thing this teaches\n**Count pairs across groups with a running total.** The "
        "direct formula is `C(n, 2) − Σ C(s, 2)`; the running form `Σ s × seen` avoids the "
        "subtraction and never builds a quadratic term per group.\n\n"
        "## Approach\n```java\n// union every edge, then count component sizes by root\nlong seen = 0, pairs = 0;\n"
        "for (int size : componentSizes) {\n    pairs += size * seen;     // this component with every earlier one\n    seen += size;\n}\n```\n\n"
        "## The complement check\nFor sizes 4, 2, 1 with n = 7: all pairs `21`, reachable pairs "
        "`6 + 1 + 0 = 7`, so `14` unreachable. The running form gives `0 + 2·4 + 1·6 = 14`.\n\n"
        "## Overflow\n`size * seen` must be computed in 64 bits: `50000 × 50000` already exceeds "
        "an int."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    sizes = []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack, size = [s], 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        sizes.append(size)
    return n * (n - 1) // 2 - sum(s * (s - 1) // 2 for s in sizes)
''',
    java='''
    static int find(int[] p, int x) {
        while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
        return x;
    }

    static long solve(int n, int[][] edges) {
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int[] e : edges) {
            int a = find(parent, e[0]), b = find(parent, e[1]);
            if (a != b) parent[a] = b;
        }
        long[] size = new long[n];
        for (int i = 0; i < n; i++) size[find(parent, i)]++;
        long seen = 0, pairs = 0;
        for (long s : size) {
            if (s == 0) continue;
            pairs += s * seen;
            seen += s;
        }
        return pairs;
    }
''',
    examples=[
        ("Example 1", "3 3\n0 1\n0 2\n1 2\n"),
        ("Example 2", "7 5\n0 2\n0 5\n2 4\n1 6\n5 4\n"),
    ],
    hidden=[
        ("Single node", "1 0\n"),
        ("No edges", "4 0\n"),
        ("A path and a loner", "5 3\n0 1\n1 2\n2 3\n"),
        ("Many isolated nodes", "100000 0\n"),
    ],
    expl=[
        "Every node reaches every other.",
        "Components {0, 2, 4, 5}, {1, 6} and {3}: 4·2 + 4·1 + 2·1 = 14 pairs.",
    ],
    prereqs=[
        ("union_find", "Grouping nodes and reading each component's size."),
        ("overflow", "Products of component sizes that exceed an int."),
    ],
)

_p(
    "knight-dialer", "Knight Dialer", "Medium",
    topics=["Dynamic Programming"], subtopics=["1D DP", "State Transitions"], companies=["Google", "Twilio"],
    shape="n", ret="long", todo="count[d] = ways to end on digit d; each step, count'[d] = sum of count over digits a knight can jump from",
    description=(
        "A chess knight stands on a phone keypad:\n\n"
        "```\n1 2 3\n4 5 6\n7 8 9\n  0\n```\n\n"
        "It dials a number of length `n` by starting on any digit and making `n − 1` knight moves "
        "(two squares one way, one square perpendicular), landing only on digits. Print how many "
        "distinct numbers of length `n` can be dialled, modulo `10^9 + 7`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe count modulo 10^9 + 7."
    ),
    constraints="1 ≤ n ≤ 5000",
    hints=[
        "List the moves from each digit: 0 → 4, 6; 1 → 6, 8; 2 → 7, 9; 3 → 4, 8; 4 → 0, 3, 9; 5 → none; 6 → 0, 1, 7; 7 → 2, 6; 8 → 1, 3; 9 → 2, 4.",
        "The number of ways to finish on a digit depends only on the counts for each digit one step earlier.",
        "Keep 10 counts. Each step, the new count for d sums the old counts of the digits that jump to d. Reduce modulo 10^9 + 7.",
    ],
    opt=("O(n)", "O(1)", "Ten counters updated n − 1 times."),
    editorial=(
        "## The one thing this teaches\n**DP over \"where am I now\".** Counting sequences "
        "becomes easy when the future depends only on the current position — here, the last "
        "digit. The whole history collapses into ten numbers.\n\n"
        "## Approach\n```java\nint[][] moves = {{4, 6}, {6, 8}, {7, 9}, {4, 8}, {0, 3, 9}, {}, {0, 1, 7}, {2, 6}, {1, 3}, {2, 4}};\n"
        "long[] count = new long[10];\nArrays.fill(count, 1);\n"
        "for (int step = 1; step < n; step++) {\n    long[] next = new long[10];\n"
        "    for (int d = 0; d < 10; d++)\n        for (int to : moves[d]) next[to] = (next[to] + count[d]) % MOD;\n"
        "    count = next;\n}\nreturn sum(count) % MOD;\n```\n\n"
        "## Why moves are symmetric\nA knight move reversed is a knight move, so \"jump from d to "
        "e\" and \"jump from e to d\" are the same list. Either direction of the update works.\n\n"
        "## The 5 key\nNo knight move reaches or leaves 5. It counts only for n = 1."
    ),
    py='''
def solve(n):
    MOD = 10**9 + 7
    pad = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2), 7: (2, 0), 8: (2, 1), 9: (2, 2), 0: (3, 1)}
    at = {pos: d for d, pos in pad.items()}
    jumps = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    ways = {d: 1 for d in pad}
    for _ in range(n - 1):
        nxt = {d: 0 for d in pad}
        for d, (r, c) in pad.items():
            for dr, dc in jumps:
                e = at.get((r + dr, c + dc))
                if e is not None:
                    nxt[e] = (nxt[e] + ways[d]) % MOD
        ways = nxt
    return sum(ways.values()) % MOD
''',
    java='''
    static long solve(long nn) {
        final long MOD = 1_000_000_007L;
        int n = (int) nn;
        int[][] moves = {{4, 6}, {6, 8}, {7, 9}, {4, 8}, {0, 3, 9}, {}, {0, 1, 7}, {2, 6}, {1, 3}, {2, 4}};
        long[] count = new long[10];
        Arrays.fill(count, 1);
        for (int step = 1; step < n; step++) {
            long[] next = new long[10];
            for (int d = 0; d < 10; d++)
                for (int to : moves[d]) next[to] = (next[to] + count[d]) % MOD;
            count = next;
        }
        long total = 0;
        for (long c : count) total = (total + c) % MOD;
        return total;
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "2\n"), ("Example 3", "3131\n")],
    hidden=[
        ("Three digits", "3\n"),
        ("Ten digits", "10\n"),
        ("Largest", "5000\n"),
    ],
    expl=[
        "Any single digit, including 5.",
        "The number of knight moves between digits: 2+2+2+2+3+0+3+2+2+2 = 20.",
        "Reduced modulo 10^9 + 7.",
    ],
    prereqs=[
        ("dp", "Counts per ending state, advanced one step at a time."),
        ("modulo", "Reducing sums modulo 10^9 + 7."),
    ],
)

_p(
    "domino-tromino-tiling", "Domino and Tromino Tiling", "Medium",
    topics=["Dynamic Programming"], subtopics=["1D DP", "Tiling"], companies=["Google"],
    shape="n", ret="long", todo="full[n] = full[n−1] + full[n−2] + 2 · partial[n−1]; partial[n] = partial[n−1] + full[n−2] (or f(n) = 2 f(n−1) + f(n−3))",
    description=(
        "Tile a `2 × n` board using `2 × 1` dominoes and L-shaped trominoes (three squares), each "
        "of which may be rotated. Print the number of tilings modulo `10^9 + 7`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe number of tilings modulo 10^9 + 7."
    ),
    constraints="1 ≤ n ≤ 1000",
    hints=[
        "With dominoes only, the count is Fibonacci: the last column is a vertical domino or the last two columns are two horizontal ones.",
        "Trominoes leave a column half-filled. Track two states: the board filled up to column i, and filled with one square of column i sticking out.",
        "full[i] = full[i−1] + full[i−2] + 2·partial[i−1]; partial[i] = partial[i−1] + full[i−2]. (These combine to f(n) = 2 f(n−1) + f(n−3).)",
    ],
    opt=("O(n)", "O(1)", "A constant number of previous values per step."),
    editorial=(
        "## The one thing this teaches\n**When pieces leave ragged edges, add a state for the "
        "ragged edge.** A flat boundary is not the only shape a partial tiling can end with. "
        "Naming the other shape — one cell protruding — makes the transitions local again.\n\n"
        "## Approach\n```java\nlong[] full = new long[n + 1], part = new long[n + 1];\n"
        "full[0] = 1; full[1] = 1; part[1] = 0;\nfor (int i = 2; i <= n; i++) {\n"
        "    full[i] = (full[i - 1] + full[i - 2] + 2 * part[i - 1]) % MOD;\n"
        "    part[i] = (part[i - 1] + full[i - 2]) % MOD;\n}\nreturn full[n];\n```\n\n"
        "## The transitions\n- **full[i]**: end with a vertical domino (from full[i−1]), two "
        "horizontal dominoes (from full[i−2]), or a tromino closing a protrusion (from "
        "part[i−1], top or bottom — hence the 2).\n"
        "- **part[i]** (one cell of column i filled): a tromino on a flat edge (from full[i−2]), "
        "or a horizontal domino extending a protrusion (from part[i−1]).\n\n"
        "## Walkthrough: n = 3\nfull[2] = 2 and part[2] = part[1] + full[0] = 1, so "
        "full[3] = full[2] + full[1] + 2·part[2] = 2 + 1 + 2 = 5."
    ),
    py='''
def solve(n):
    MOD = 10**9 + 7
    # profile DP: mask of which cells of the current column are already covered
    ways = {0: 1}
    for _ in range(n):
        nxt = {}

        def add(mask, v):
            nxt[mask] = (nxt.get(mask, 0) + v) % MOD

        for mask, v in ways.items():
            if mask == 0:
                add(0, v)        # vertical domino
                add(3, v)        # two horizontal dominoes
                add(1, v)        # tromino covering both cells here and the top of the next column
                add(2, v)        # tromino covering both cells here and the bottom of the next column
            elif mask == 3:
                add(0, v)
            elif mask == 1:      # top covered: fill bottom with a horizontal domino or a tromino
                add(2, v)
                add(3, v)
            else:                # bottom covered
                add(1, v)
                add(3, v)
        ways = nxt
    return ways.get(0, 0)
''',
    java='''
    static long solve(long nn) {
        final long MOD = 1_000_000_007L;
        int n = (int) nn;
        long[] full = new long[n + 2], part = new long[n + 2];
        full[0] = 1;
        full[1] = 1;
        for (int i = 2; i <= n; i++) {
            full[i] = (full[i - 1] + full[i - 2] + 2 * part[i - 1]) % MOD;
            part[i] = (part[i - 1] + full[i - 2]) % MOD;
        }
        return full[n];
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "1\n")],
    hidden=[
        ("Two columns", "2\n"),
        ("Four columns", "4\n"),
        ("Five columns", "5\n"),
        ("Thirty columns", "30\n"),
        ("Largest", "1000\n"),
    ],
    expl=[
        "Three domino-only tilings and two made of a pair of trominoes.",
        "A single vertical domino.",
    ],
    prereqs=[
        ("dp", "Two interlocking state arrays: flat edge and protruding edge."),
        ("recurrence", "Deriving transitions by the piece that ends the tiling."),
    ],
)

_p(
    "broken-calculator", "Broken Calculator", "Medium",
    topics=["Greedy", "Math"], subtopics=["Work Backwards"], companies=["Amazon"],
    shape="two", ret="long", todo="from target: halve when even, add one when odd, until it drops to start or below; then add start − target",
    description=(
        "A calculator shows `start`. It has two buttons: **double** the number, or **subtract 1**. "
        "Print the minimum number of presses to show `target`.\n\n"
        "### Input\nOne line: `start target`.\n\n"
        "### Output\nThe minimum number of operations."
    ),
    constraints="1 ≤ start, target ≤ 10^9",
    hints=[
        "Going forward, it is unclear when to double and when to subtract.",
        "Reverse the operations: from target, you may halve (if even) or add 1.",
        "Backwards the choice is forced: an odd number cannot be halved, so add 1; an even number above start should be halved. Once target ≤ start, only +1 steps remain: start − target of them.",
    ],
    opt=("O(log target)", "O(1)", "Every two backward steps at least halve the target."),
    editorial=(
        "## The one thing this teaches\n**Reverse a process when the reverse choices are "
        "forced.** Forwards, doubling early multiplies every later subtraction's effect — a hard "
        "trade-off. Backwards, halving is only possible on even numbers, and when it is possible "
        "it is always at least as good.\n\n"
        "## Approach\n```java\nlong ops = 0;\nwhile (target > start) {\n"
        "    target = target % 2 == 0 ? target / 2 : target + 1;\n    ops++;\n}\nreturn ops + (start - target);\n```\n\n"
        "## Why halving first is right\nTwo +1 steps then a halve reach `(t + 2) / 2 = t/2 + 1`. "
        "A halve then one +1 reaches the same number in two steps instead of three. Delaying a "
        "halve never helps.\n\n"
        "## Walkthrough: 3 → 10\nBackwards: 10 → 5 (halve) → 6 (+1) → 3 (halve). Three "
        "operations: forwards 3 → 6 → 5 → 10."
    ),
    py='''
def solve(x, y):
    from collections import deque
    limit = 2 * max(x, y) + 2
    dist = {x: 0}
    q = deque([x])
    while q:
        v = q.popleft()
        if v == y:
            return dist[v]
        for w in (v * 2, v - 1):
            if 0 < w <= limit and w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
''',
    java='''
    static long solve(long start, long target) {
        long ops = 0;
        while (target > start) {
            target = target % 2 == 0 ? target / 2 : target + 1;
            ops++;
        }
        return ops + (start - target);
    }
''',
    examples=[("Example 1", "2 3\n"), ("Example 2", "5 8\n"), ("Example 3", "3 10\n")],
    hidden=[
        ("Only subtraction", "10 1\n"),
        ("Already equal", "7 7\n"),
        ("Many doublings", "1 100000\n"),
        ("Odd targets", "4 31\n"),
    ],
    expl=[
        "Double to 4, subtract to 3.",
        "Subtract to 4, double to 8.",
        "Double to 6, subtract to 5, double to 10.",
    ],
    prereqs=[
        ("greedy", "A forced choice at every step once the process is reversed."),
        ("bit_manip", "Halving and parity as the backward operations."),
    ],
)

_p(
    "min-reorder-roads", "Reorder Routes to Make All Paths Lead to City Zero", "Medium",
    topics=["Graphs", "DFS", "Trees"], subtopics=["Edge Direction"], companies=["Google", "Amazon"],
    shape="graph", ret="int", todo="traverse the undirected tree from 0; an original edge pointing from the visited node to the new one must be reversed",
    description=(
        "`n` cities are joined by `n − 1` one-way roads, and ignoring direction they form a "
        "tree. Reverse as few roads as possible so that every city can reach city `0`. Print "
        "the number of reversals.\n\n"
        "### Input\n- Line 1: `n m` (with `m = n − 1`).\n- Next `m` lines: `u v`, a road from `u` to `v`.\n\n"
        "### Output\nThe minimum number of roads to reverse."
    ),
    constraints="2 ≤ n ≤ 5·10^4\nThe roads form a tree when directions are ignored",
    hints=[
        "In a tree, the path from each city to 0 is unique — so every road has one correct direction: toward 0.",
        "Explore outward from 0 over the roads as if they were two-way, remembering each road's real direction.",
        "When the exploration crosses a road from a known city to a new one, the road should point back toward the known city. If it points outward, count it.",
    ],
    opt=("O(n)", "O(n)", "One traversal of the tree."),
    editorial=(
        "## The one thing this teaches\n**Store direction as an edge attribute and traverse "
        "undirected.** Directed edges hide half the tree from a directed search. Adding every "
        "road in both directions, tagged with whether it is original, lets one traversal see "
        "everything and judge each road.\n\n"
        "## Approach\n```java\n// adj[u] holds {v, 1} for an original road u → v and {v, 0} for the reverse view\n"
        "boolean[] seen = new boolean[n];\nDeque<Integer> stack = new ArrayDeque<>(List.of(0));\nseen[0] = true;\nint flips = 0;\n"
        "while (!stack.isEmpty()) {\n    int u = stack.pop();\n    for (int[] e : adj[u]) {\n"
        "        if (seen[e[0]]) continue;\n        seen[e[0]] = true;\n"
        "        flips += e[1];               // original road points away from 0\n        stack.push(e[0]);\n    }\n}\n```\n\n"
        "## Why no choices exist\nEach road lies on the unique path between its far endpoint and "
        "0, so its correct direction is fixed. The answer is simply the number of roads pointing "
        "the wrong way.\n\n"
        "## Depth view\nEquivalently, with depths from 0 in the undirected tree, a road `u → v` "
        "needs reversing exactly when `v` is deeper than `u`."
    ),
    py='''
def solve(n, edges):
    from collections import deque
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    depth = [-1] * n
    depth[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if depth[v] < 0:
                depth[v] = depth[u] + 1
                q.append(v)
    return sum(1 for u, v in edges if depth[v] > depth[u])
''',
    java='''
    static int solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(new int[]{e[1], 1});
            adj.get(e[1]).add(new int[]{e[0], 0});
        }
        boolean[] seen = new boolean[n];
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        stack.push(0);
        seen[0] = true;
        int flips = 0;
        while (!stack.isEmpty()) {
            int u = stack.pop();
            for (int[] e : adj.get(u)) {
                if (seen[e[0]]) continue;
                seen[e[0]] = true;
                flips += e[1];
                stack.push(e[0]);
            }
        }
        return flips;
    }
''',
    examples=[
        ("Example 1", "6 5\n0 1\n1 3\n2 3\n4 0\n4 5\n"),
        ("Example 2", "5 4\n1 0\n1 2\n3 2\n3 4\n"),
        ("Example 3", "3 2\n1 0\n2 0\n"),
    ],
    hidden=[
        ("Two cities, wrong way", "2 1\n0 1\n"),
        ("Two cities, right way", "2 1\n1 0\n"),
        ("Star pointing out", "5 4\n0 1\n0 2\n0 3\n0 4\n"),
        ("Deep chain", "5 4\n0 1\n1 2\n2 3\n3 4\n"),
    ],
    expl=[
        "Roads 0 → 1, 1 → 3 and 4 → 5 point away from 0.",
        "Roads 1 → 2 and 3 → 4 point away from 0.",
        "Both roads already lead to 0.",
    ],
    prereqs=[
        ("graph_repr", "An adjacency list whose entries carry the original direction."),
        ("tree_traversal", "Visiting a tree from a chosen root without revisiting parents."),
    ],
)

_p(
    "reachable-nodes-subdivided", "Reachable Nodes in Subdivided Graph", "Hard",
    topics=["Graphs", "Shortest Paths", "Heaps"], subtopics=["Dijkstra"], companies=["Google"],
    shape="wgraph_k", ret="long", todo="Dijkstra with edge weight cnt + 1; count original nodes within k, plus min(cnt, leftover from u + leftover from v) per edge",
    description=(
        "Start with an undirected graph on nodes `0..n−1`. Each edge `u v cnt` is **subdivided**: "
        "replaced by a chain of `cnt` new nodes between `u` and `v`, so it becomes `cnt + 1` "
        "edges. Starting at node `0`, how many nodes of the new graph (original or new) can be "
        "reached in at most `k` moves?\n\n"
        "### Input\n- Line 1: `n m k`.\n- Next `m` lines: `u v cnt`.\n\n"
        "### Output\nThe number of reachable nodes."
    ),
    constraints="1 ≤ n ≤ 3000\n0 ≤ m ≤ 10^4\n0 ≤ cnt ≤ 10^4\n0 ≤ k ≤ 10^9\nNo parallel edges or self-loops",
    hints=[
        "Building the subdivided graph could create 10^8 nodes. Work on the original graph instead.",
        "Travelling across a subdivided edge costs cnt + 1 moves. Dijkstra gives the fewest moves to each original node.",
        "An original node counts if its distance ≤ k. On edge (u, v, cnt), from u you can walk max(0, k − dist[u]) new nodes inward, from v likewise; that edge contributes min(cnt, both together).",
    ],
    opt=("O(m log n)", "O(n + m)", "Dijkstra on the original graph, then one pass over edges."),
    editorial=(
        "## The one thing this teaches\n**Count on the compressed graph, then add what lies "
        "inside the edges.** The subdivided nodes on an edge are reached from its two ends only, "
        "by walking inward with leftover moves. Shortest distances to original nodes decide "
        "everything.\n\n"
        "## Approach\n```java\nlong[] dist = dijkstra(from 0, edge weight cnt + 1);\nlong count = 0;\n"
        "for (int v = 0; v < n; v++) if (dist[v] <= k) count++;\n"
        "for (int[] e : edges) {\n    long fromU = Math.max(0, k - dist[e[0]]);   // dist may be infinity\n"
        "    long fromV = Math.max(0, k - dist[e[1]]);\n    count += Math.min(e[2], fromU + fromV);\n}\n```\n\n"
        "## Why min(cnt, fromU + fromV)\nWalkers from both ends may cover the whole chain and "
        "overlap. The chain has only `cnt` new nodes, so the overlap is capped.\n\n"
        "## Unreachable ends\nWith `dist = ∞`, `k − dist` is very negative and `max(0, …)` "
        "turns it into 0 — use a large sentinel that cannot overflow when subtracted."
    ),
    py='''
def solve(n, edges, k):
    from collections import deque
    adj = defaultdict(list)
    next_id = n
    for u, v, cnt in edges:
        chain = [u] + list(range(next_id, next_id + cnt)) + [v]
        next_id += cnt
        for a, b in zip(chain, chain[1:]):
            adj[a].append(b)
            adj[b].append(a)
    dist = {0: 0}
    q = deque([0])
    while q:
        x = q.popleft()
        if dist[x] == k:
            continue
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)
    return len(dist)
''',
    java='''
    static long solve(int n, int[][] edges, int k) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            adj.get(e[0]).add(new int[]{e[1], e[2] + 1});
            adj.get(e[1]).add(new int[]{e[0], e[2] + 1});
        }
        final long INF = Long.MAX_VALUE / 4;
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[0] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((x, y) -> Long.compare(x[0], y[0]));
        pq.add(new long[]{0, 0});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            int u = (int) cur[1];
            if (cur[0] > dist[u]) continue;
            for (int[] e : adj.get(u)) {
                long nd = cur[0] + e[1];
                if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
            }
        }
        long count = 0;
        for (int v = 0; v < n; v++) if (dist[v] <= k) count++;
        for (int[] e : edges) {
            long fromU = Math.max(0, k - dist[e[0]]);
            long fromV = Math.max(0, k - dist[e[1]]);
            count += Math.min(e[2], fromU + fromV);
        }
        return count;
    }
''',
    examples=[
        ("Example 1", "3 3 6\n0 1 10\n0 2 1\n1 2 2\n"),
        ("Example 2", "4 4 10\n0 1 4\n1 2 6\n0 2 8\n1 3 1\n"),
        ("Example 3", "5 5 17\n1 2 4\n1 4 5\n1 3 1\n2 3 4\n3 4 5\n"),
    ],
    hidden=[
        ("No moves", "2 1 0\n0 1 3\n"),
        ("Edge fully covered", "2 1 10\n0 1 3\n"),
        ("Stops inside an edge", "2 1 2\n0 1 5\n"),
        ("No subdivisions", "3 2 1\n0 1 0\n1 2 0\n"),
    ],
    expl=[
        "Nodes 0, 1 and 2, plus 7 new nodes on edge 0–1 (6 walked from 0, 1 from 1), 1 on edge 0–2 and 2 on edge 1–2: 13.",
        "All four original nodes and 19 of the new ones.",
        "Node 0 has no edges, so only it is reachable.",
    ],
    prereqs=[
        ("dijkstra", "Shortest distances with weights cnt + 1 on the original graph."),
        ("graph_repr", "Reasoning about a subdivided edge without building it."),
    ],
)
