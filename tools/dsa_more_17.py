# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 17 — extra practice for the units that had none.
#
#   circular-deque                 a ring buffer with a head index and a size
#   dota2-senate                   two queues of turns; the earlier senator bans and requeues
#   ways-to-add-parentheses        split at every operator and combine both sides' results
#   find-kth-bit                   recurse on the half that contains k, flipping on the right
#   pairs-sum-less-than-target     sort, then count pairs from both ends
#   two-sum-bst                    in-order gives a sorted list; two pointers finish it
#   closest-value-bst              one walk down, keeping the best so far
#   city-fewest-neighbours         all-pairs shortest paths, then count within a threshold
#   repeated-substring-pattern     s is periodic exactly when it appears inside (s + s) trimmed
#   smallest-string-with-swaps     each connected group of indices can be sorted freely
#   lca-deepest-leaves             post-order returning (depth, lca) pairs
# ===========================================================================

_p(
    "circular-deque", "Design Circular Deque", "Medium",
    topics=["Design", "Data Structures"], subtopics=["Queue", "Design"], companies=["Amazon", "Microsoft"],
    shape="ops", ret="String", todo="a fixed array with a head index and a size; index arithmetic mod capacity",
    description=(
        "Implement a double-ended queue with a fixed capacity `k`:\n\n"
        "- `insertFront v`, `insertLast v` — print `true`, or `false` if full.\n"
        "- `deleteFront`, `deleteLast` — print `true`, or `false` if empty.\n"
        "- `getFront`, `getRear` — print the value, or `-1` if empty.\n"
        "- `isEmpty`, `isFull` — print `true` or `false`.\n\n"
        "### Input\n- Line 1: `q`.\n- The first operation is `init k`; the rest are as above.\n\n"
        "### Output\nOne line per operation after `init`."
    ),
    constraints="2 ≤ q ≤ 3000\n1 ≤ k ≤ 1000\n0 ≤ v ≤ 1000",
    hints=[
        "Store the elements in an array of size k and never move them.",
        "Track the head index and the size. The tail is (head + size − 1) mod k.",
        "insertFront moves head back one: (head − 1 + k) mod k. Add k before taking the modulus so it never goes negative.",
    ],
    opt=("O(1) per operation", "O(k)", "A fixed array and two integers."),
    editorial=(
        "## The one thing this teaches\n**A ring buffer.** An array whose ends wrap around never "
        "shifts elements: inserting at either end just moves an index. `ArrayDeque` is exactly "
        "this, plus resizing.\n\n"
        "## Approach\n```java\nint[] buf = new int[k];\nint head = 0, size = 0;\n\n"
        "boolean insertFront(int v) {\n    if (size == k) return false;\n"
        "    head = (head - 1 + k) % k;\n    buf[head] = v;\n    size++;\n    return true;\n}\n"
        "boolean insertLast(int v) {\n    if (size == k) return false;\n"
        "    buf[(head + size) % k] = v;\n    size++;\n    return true;\n}\n"
        "boolean deleteFront() { if (size == 0) return false; head = (head + 1) % k; size--; return true; }\n"
        "boolean deleteLast()  { if (size == 0) return false; size--; return true; }\n"
        "int getRear() { return size == 0 ? -1 : buf[(head + size - 1) % k]; }\n```\n\n"
        "## Head and size, not head and tail\nWith separate head and tail indices, an empty buffer "
        "and a full one both have `head == tail`, and you need a spare slot or a flag to tell them "
        "apart. Storing the size removes the ambiguity."
    ),
    py='''
def solve(ops):
    k = int(ops[0][1])
    d = []
    out = []
    for op in ops[1:]:
        name = op[0]
        if name == "insertFront":
            ok = len(d) < k
            if ok:
                d.insert(0, int(op[1]))
            out.append("true" if ok else "false")
        elif name == "insertLast":
            ok = len(d) < k
            if ok:
                d.append(int(op[1]))
            out.append("true" if ok else "false")
        elif name == "deleteFront":
            out.append("true" if d else "false")
            if d:
                d.pop(0)
        elif name == "deleteLast":
            out.append("true" if d else "false")
            if d:
                d.pop()
        elif name == "getFront":
            out.append(str(d[0]) if d else "-1")
        elif name == "getRear":
            out.append(str(d[-1]) if d else "-1")
        elif name == "isEmpty":
            out.append("true" if not d else "false")
        else:
            out.append("true" if len(d) == k else "false")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        int k = Integer.parseInt(ops[0][1]);
        int[] buf = new int[k];
        int head = 0, size = 0;
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i < ops.length; i++) {
            String name = ops[i][0], res;
            switch (name) {
                case "insertFront":
                    if (size == k) res = "false";
                    else { head = (head - 1 + k) % k; buf[head] = Integer.parseInt(ops[i][1]); size++; res = "true"; }
                    break;
                case "insertLast":
                    if (size == k) res = "false";
                    else { buf[(head + size) % k] = Integer.parseInt(ops[i][1]); size++; res = "true"; }
                    break;
                case "deleteFront":
                    if (size == 0) res = "false"; else { head = (head + 1) % k; size--; res = "true"; }
                    break;
                case "deleteLast":
                    if (size == 0) res = "false"; else { size--; res = "true"; }
                    break;
                case "getFront": res = size == 0 ? "-1" : String.valueOf(buf[head]); break;
                case "getRear": res = size == 0 ? "-1" : String.valueOf(buf[(head + size - 1) % k]); break;
                case "isEmpty": res = String.valueOf(size == 0); break;
                default: res = String.valueOf(size == k);
            }
            if (sb.length() > 0) sb.append('\\n');
            sb.append(res);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "10\ninit 3\ninsertLast 1\ninsertLast 2\ninsertFront 3\ninsertFront 4\ngetRear\nisFull\ndeleteLast\ninsertFront 4\ngetFront\n"),
        ("Example 2", "5\ninit 1\ngetFront\nisEmpty\ninsertFront 7\ngetRear\n"),
    ],
    hidden=[
        ("Wrap both ways", "9\ninit 2\ninsertFront 1\ninsertFront 2\ndeleteLast\ninsertFront 3\ngetFront\ngetRear\ndeleteFront\ngetFront\n"),
        ("Delete from empty", "4\ninit 3\ndeleteFront\ndeleteLast\nisEmpty\n"),
    ],
    expl=[
        "The deque fills with 3 1 2; the fourth insert fails; after deleting 2, 4 fits at the front.",
        "Empty at first, then holds 7 at both ends.",
    ],
    prereqs=[
        ("queue", "A deque as a ring buffer: fixed storage, moving indices."),
        ("modulo", "Wrapping indices with (i ± 1 + k) mod k."),
    ],
)

_p(
    "dota2-senate", "Dota2 Senate", "Medium",
    topics=["Data Structures", "Greedy"], subtopics=["Queue", "Greedy", "Simulation"], companies=["Valve", "Amazon"],
    shape="str", ret="String", todo="a queue of indices per party; the earlier index bans the other and rejoins at index + n",
    description=(
        "Senators from two parties, `R` (Radiant) and `D` (Dire), vote in rounds in the order given. "
        "On their turn, a senator who still has rights **bans** one opposing senator (permanently). "
        "Rounds repeat until one party remains. Assuming everyone plays optimally, which party "
        "wins?\n\n"
        "### Input\nOne line: the string of `R`s and `D`s.\n\n### Output\n`Radiant` or `Dire`."
    ),
    constraints="1 ≤ n ≤ 10^4",
    hints=[
        "The best ban is always the NEXT opposing senator to act — they are the most immediate threat.",
        "Put the indices of each party in its own queue. Compare the two fronts: the smaller index acts first.",
        "The winner of the comparison rejoins its queue at index + n (next round); the loser is removed.",
    ],
    opt=("O(n)", "O(n)", "Each comparison removes one senator; there are at most n − 1 removals."),
    editorial=(
        "## The one thing this teaches\n**A queue models turn order across rounds.** Adding `n` to a "
        "senator's index when they finish their turn places them after everyone still waiting in "
        "this round, which is exactly when they act again.\n\n"
        "## Approach\n```java\nDeque<Integer> r = new ArrayDeque<>(), d = new ArrayDeque<>();\n"
        "for (int i = 0; i < n; i++) (s.charAt(i) == 'R' ? r : d).add(i);\n"
        "while (!r.isEmpty() && !d.isEmpty()) {\n    int a = r.poll(), b = d.poll();\n"
        "    if (a < b) r.add(a + n);   // Radiant acts first and bans b\n    else d.add(b + n);\n}\n"
        "return r.isEmpty() ? \"Dire\" : \"Radiant\";\n```\n\n"
        "## Why ban the next opponent\nBanning an opponent who acts later leaves the next one free "
        "to ban one of yours first. The nearest threat is the only one that can hurt you before "
        "your next turn — the greedy choice that makes the simulation well-defined."
    ),
    py='''
def solve(s):
    senators = list(s)
    banned = [False] * len(s)
    ban_r = ban_d = 0
    while True:
        alive_r = alive_d = False
        for i, p in enumerate(senators):
            if banned[i]:
                continue
            if p == "R":
                if ban_r > 0:
                    ban_r -= 1
                    banned[i] = True
                else:
                    ban_d += 1
                    alive_r = True
            else:
                if ban_d > 0:
                    ban_d -= 1
                    banned[i] = True
                else:
                    ban_r += 1
                    alive_d = True
        if not alive_d:
            return "Radiant"
        if not alive_r:
            return "Dire"
''',
    java='''
    static String solve(String s) {
        int n = s.length();
        ArrayDeque<Integer> r = new ArrayDeque<>(), d = new ArrayDeque<>();
        for (int i = 0; i < n; i++) (s.charAt(i) == 'R' ? r : d).add(i);
        while (!r.isEmpty() && !d.isEmpty()) {
            int a = r.poll(), b = d.poll();
            if (a < b) r.add(a + n); else d.add(b + n);
        }
        return r.isEmpty() ? "Dire" : "Radiant";
    }
''',
    examples=[("Example 1", "RD\n"), ("Example 2", "RDD\n")],
    hidden=[
        ("Single senator", "R\n"),
        ("Majority in front", "DDRRR\n"),
        ("Late majority", "RRDDD\n"),
        ("Alternating", "DRDRDRDR\n"),
    ],
    expl=[
        "R bans D before D can act.",
        "R bans the first D, the second D bans R.",
    ],
    prereqs=[
        ("queue", "Each party's senators queued in turn order, re-queued for the next round."),
        ("greedy", "Always banning the next opponent to act."),
    ],
)

_p(
    "ways-to-add-parentheses", "Different Ways to Add Parentheses", "Medium",
    topics=["Recursion", "Strings"], subtopics=["Recurrence", "Backtracking"], companies=["Google", "Samsung"],
    shape="str", ret="String", todo="for each operator, recursively evaluate both sides and combine every pair of results",
    description=(
        "An expression uses non-negative integers and the operators `+`, `-` and `*`. Print every "
        "value it can take under some full parenthesisation, **sorted ascending** (keep duplicates: "
        "one value per parenthesisation).\n\n"
        "### Input\nOne line: the expression, with no spaces.\n\n### Output\nAll results, separated by spaces."
    ),
    constraints="1 ≤ length ≤ 20\nNumbers are in [0, 99]; there are at most 10 operators.",
    hints=[
        "Every parenthesisation has a LAST operator applied — the one at the top of the expression tree.",
        "Choosing operator i as last splits the expression into a left and a right part, each parenthesised independently.",
        "So results(expr) = { l op r : l in results(left), r in results(right) } over every operator. A lone number is its own result.",
    ],
    opt=("O(Catalan(k) · k)", "O(Catalan(k))", "The number of results is the Catalan number of the operator count."),
    editorial=(
        "## The one thing this teaches\n**Divide and conquer on the last operation.** Enumerating "
        "parenthesisations directly is confusing; choosing which operator is applied *last* splits "
        "the problem into two independent smaller problems whose answers combine by a cross "
        "product.\n\n"
        "## Approach\n```java\nList<Integer> ways(String e) {\n    List<Integer> res = new ArrayList<>();\n"
        "    for (int i = 0; i < e.length(); i++) {\n        char c = e.charAt(i);\n"
        "        if (c != '+' && c != '-' && c != '*') continue;\n"
        "        for (int l : ways(e.substring(0, i)))\n            for (int r : ways(e.substring(i + 1)))\n"
        "                res.add(c == '+' ? l + r : c == '-' ? l - r : l * r);\n    }\n"
        "    if (res.isEmpty()) res.add(Integer.parseInt(e));   // no operator: a number\n    return res;\n}\n```\n\n"
        "## Memoisation\nThe same substring is evaluated from many splits. Caching `ways` by "
        "substring turns repeated work into lookups — the step from recursion to interval DP.\n\n"
        "## How many results\nWith k operators there are Catalan(k) parenthesisations: 1, 2, 5, 14, "
        "42, … That growth is why the length is capped."
    ),
    py='''
def solve(s):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def ways(e):
        res = []
        for i, ch in enumerate(e):
            if ch in "+-*":
                for l in ways(e[:i]):
                    for r in ways(e[i + 1:]):
                        res.append(l + r if ch == "+" else l - r if ch == "-" else l * r)
        return tuple(res) if res else (int(e),)

    return " ".join(map(str, sorted(ways(s))))
''',
    java='''
    static List<Long> ways(String e) {
        List<Long> res = new ArrayList<>();
        for (int i = 0; i < e.length(); i++) {
            char c = e.charAt(i);
            if (c != '+' && c != '-' && c != '*') continue;
            for (long l : ways(e.substring(0, i)))
                for (long r : ways(e.substring(i + 1)))
                    res.add(c == '+' ? l + r : c == '-' ? l - r : l * r);
        }
        if (res.isEmpty()) res.add(Long.parseLong(e));
        return res;
    }

    static String solve(String s) {
        List<Long> res = ways(s);
        Collections.sort(res);
        StringBuilder sb = new StringBuilder();
        for (long v : res) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "2-1-1\n"), ("Example 2", "2*3-4*5\n")],
    hidden=[
        ("A lone number", "5\n"),
        ("One operator", "1+2\n"),
        ("Two-digit numbers", "10*2-3\n"),
        ("Five results with duplicates", "1+1+1+1\n"),
    ],
    expl=[
        "`(2-1)-1 = 0` and `2-(1-1) = 2`.",
        "Five parenthesisations: −34, −14, −10, −10, 10.",
    ],
    prereqs=[
        ("recursion", "Splitting at the last-applied operator into two independent subproblems."),
        ("dp", "Memoising results by substring avoids recomputing shared parts."),
    ],
)

_p(
    "find-kth-bit", "Find K-th Bit in the N-th Binary String", "Medium",
    topics=["Recursion", "Strings"], subtopics=["Recurrence"], companies=["Amazon"],
    shape="two", ret="int", todo="S(n) = S(n−1) + '1' + reverse(invert(S(n−1))); recurse on the half containing k",
    description=(
        "`S₁ = \"0\"`, and `Sₙ = Sₙ₋₁ + \"1\" + reverse(invert(Sₙ₋₁))`, where invert flips every bit. "
        "So `S₂ = \"011\"`, `S₃ = \"0111001\"`. Print the `k`-th bit (1-indexed) of `Sₙ`.\n\n"
        "### Input\nOne line: `n k`.\n\n### Output\n`0` or `1`."
    ),
    constraints="1 ≤ n ≤ 20\n1 ≤ k ≤ 2^n − 1",
    hints=[
        "Sₙ has length 2ⁿ − 1, and its middle bit, at position 2ⁿ⁻¹, is always 1.",
        "Left of the middle is exactly Sₙ₋₁, so the answer is the same as for (n − 1, k).",
        "Right of the middle, position k mirrors position 2ⁿ − k of Sₙ₋₁ — inverted.",
    ],
    opt=("O(n)", "O(n)", "One recursive step per level; iteratively O(1) space."),
    editorial=(
        "## The one thing this teaches\n**A recursive definition answers point queries without being "
        "built.** Sₙ has a million characters at n = 20, but each character's value is determined "
        "by one position in Sₙ₋₁. Following that one position down the levels is O(n).\n\n"
        "## Approach\n```java\nint bit(int n, long k) {\n    if (n == 1) return 0;\n"
        "    long mid = 1L << (n - 1);\n    if (k == mid) return 1;\n"
        "    if (k < mid) return bit(n - 1, k);\n"
        "    return 1 - bit(n - 1, (1L << n) - k);      // mirrored and inverted\n}\n```\n\n"
        "## The mirror index\nSₙ has length L = 2ⁿ − 1. Position k on the right corresponds, after "
        "reversal, to position L + 1 − k = 2ⁿ − k of Sₙ₋₁. Getting that off by one is the only "
        "real risk — check it on S₃ by hand."
    ),
    py='''
def solve(x, y):
    n, k = x, y
    s = "0"
    for _ in range(n - 1):
        inv = "".join("1" if c == "0" else "0" for c in s)
        s = s + "1" + inv[::-1]
    return int(s[k - 1])
''',
    java='''
    static int bit(long n, long k) {
        if (n == 1) return 0;
        long mid = 1L << (n - 1);
        if (k == mid) return 1;
        if (k < mid) return bit(n - 1, k);
        return 1 - bit(n - 1, (1L << n) - k);
    }

    static int solve(long n, long k) {
        return bit(n, k);
    }
''',
    examples=[("Example 1", "3 1\n"), ("Example 2", "4 11\n")],
    hidden=[
        ("Base string", "1 1\n"),
        ("Second level", "2 3\n"),
        ("Middle of S20", "20 524288\n"),
        ("Last bit of S20", "20 1048575\n"),
    ],
    expl=[
        "S₃ = 0111001; the first bit is 0.",
        "S₄ = 011100110110001; the 11th bit is 1.",
    ],
    prereqs=[
        ("recursion", "Following one position down the recursive definition instead of building the string."),
        ("bit_manip", "Lengths and midpoints as powers of two."),
    ],
)

_p(
    "pairs-sum-less-than-target", "Count Pairs With Sum Less Than Target", "Easy",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers", "Sorting"], companies=["Amazon"],
    shape="arr_k", ret="long", todo="sort; if a[l] + a[r] < target, all pairs (l, l+1..r) count — add r − l and move l",
    description=(
        "Count pairs of indices `i < j` with `a[i] + a[j] < target`.\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` integers.\n\n### Output\nThe number of pairs."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i], target ≤ 10^9",
    hints=[
        "Checking all pairs is O(n²).",
        "The count does not depend on order, so sort. Then use pointers l = 0 and r = n − 1.",
        "If a[l] + a[r] < target, then a[l] pairs with every index up to r: add r − l and move l. Otherwise move r left.",
    ],
    opt=("O(n log n)", "O(1)", "A sort and one two-pointer pass."),
    editorial=(
        "## The one thing this teaches\n**Count a range of pairs in one step.** After sorting, once "
        "`a[l] + a[r]` is below the target, so is `a[l]` plus anything between `l` and `r`. Adding "
        "`r − l` counts all of them without listing them — the move that turns O(n²) into O(n).\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong count = 0;\nint l = 0, r = n - 1;\nwhile (l < r) {\n"
        "    if ((long) a[l] + a[r] < target) { count += r - l; l++; }\n    else r--;\n}\n```\n\n"
        "## Pricing it\nThe brute force is the complexity unit's lesson in miniature: n² pairs at "
        "n = 10⁵ is 5·10⁹ checks. Sorting first costs n log n and makes the count linear."
    ),
    py='''
def solve(a, k):
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] < k)
''',
    java='''
    static long solve(int[] a, long target) {
        Arrays.sort(a);
        long count = 0;
        int l = 0, r = a.length - 1;
        while (l < r) {
            if ((long) a[l] + a[r] < target) { count += r - l; l++; }
            else r--;
        }
        return count;
    }
''',
    examples=[("Example 1", "5 2\n-1 1 2 3 1\n"), ("Example 2", "7 -2\n-6 2 5 -2 -7 -1 3\n")],
    hidden=[
        ("Single element", "1 5\n1\n"),
        ("Every pair", "4 100\n1 2 3 4\n"),
        ("No pair", "3 0\n0 0 0\n"),
        ("Large values", "3 0\n-1000000000 -1000000000 1000000000\n"),
    ],
    expl=[
        "(−1, 1), (−1, 2) and (−1, 1).",
        "Ten pairs sum below −2.",
    ],
    prereqs=[
        ("two_pointers", "Counting a whole range of pairs when the smallest and largest already qualify."),
        ("big_o", "Sorting first turns an O(n²) pair check into an O(n) count."),
    ],
)

_p(
    "two-sum-bst", "Two Sum in a BST", "Easy",
    topics=["Trees", "Hashing"], subtopics=["BST", "Hash Set"], companies=["Samsung", "Amazon"],
    shape="tree_k", ret="String", todo="in-order walk into a sorted list, then two pointers — or a hash set during any traversal",
    description=(
        "Are there two **different** nodes in the binary search tree whose values sum to `k`?\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `k`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n-10^4 ≤ value ≤ 10^4, values distinct\n-10^5 ≤ k ≤ 10^5",
    hints=[
        "Any traversal plus a hash set of values seen works: look for k − value.",
        "Using the BST: an in-order traversal lists the values sorted.",
        "Then it is Two Sum II on a sorted array — two pointers from the ends.",
    ],
    opt=("O(n)", "O(n)", "One traversal; either a set or the sorted list takes O(n) space."),
    editorial=(
        "## The one thing this teaches\n**Reduce to a problem you have already solved.** A tree does "
        "not support two pointers, but its in-order traversal is a sorted array, and Two Sum II "
        "solves sorted arrays. Two familiar steps replace one new one.\n\n"
        "## Approach\n```java\nList<Integer> vals = new ArrayList<>();\ninorder(root, vals);          // sorted\n"
        "int l = 0, r = vals.size() - 1;\nwhile (l < r) {\n    int s = vals.get(l) + vals.get(r);\n"
        "    if (s == k) return \"YES\";\n    if (s < k) l++; else r--;\n}\nreturn \"NO\";\n```\n\n"
        "## Different nodes\n`l < r` guarantees two different nodes. The hash-set version must "
        "check the complement *before* adding the current value, or `k = 2 · value` matches a "
        "node with itself."
    ),
    py='''
def solve(root, k):
    seen = set()
    st = [root]
    while st:
        t = st.pop()
        if k - t.val in seen:
            return "YES"
        seen.add(t.val)
        if t.left:
            st.append(t.left)
        if t.right:
            st.append(t.right)
    return "NO"
''',
    java='''
    static void inorder(TreeNode t, List<Integer> out) {
        if (t == null) return;
        inorder(t.left, out);
        out.add(t.val);
        inorder(t.right, out);
    }

    static String solve(TreeNode root, int k) {
        List<Integer> vals = new ArrayList<>();
        inorder(root, vals);
        int l = 0, r = vals.size() - 1;
        while (l < r) {
            int s = vals.get(l) + vals.get(r);
            if (s == k) return "YES";
            if (s < k) l++; else r--;
        }
        return "NO";
    }
''',
    examples=[("Example 1", "5 3 6 2 4 null 7\n9\n"), ("Example 2", "5 3 6 2 4 null 7\n28\n")],
    hidden=[
        ("Single node", "1\n2\n"),
        ("Root and leaf", "2 1 3\n4\n"),
        ("Not the same node twice", "2 1 3\n2\n"),
        ("Negatives", "0 -3 5 -4 -1\n-4\n"),
    ],
    expl=[
        "2 + 7, 3 + 6 and 4 + 5 all make 9.",
        "The largest pair is 6 + 7 = 13.",
    ],
    prereqs=[
        ("bst", "An in-order walk produces the values in sorted order."),
        ("two_pointers", "Two Sum II on the sorted values."),
    ],
)

_p(
    "closest-value-bst", "Closest Value in a BST", "Easy",
    topics=["Trees"], subtopics=["BST"], companies=["Meta", "Google"],
    shape="tree_k", ret="int", todo="walk down toward the target, remembering the closest value seen (ties go to the smaller)",
    description=(
        "Find the value in the binary search tree closest to `target`. If two values are equally "
        "close, print the **smaller**.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `target`.\n\n"
        "### Output\nThe closest value."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n0 ≤ value ≤ 10^9, values distinct\n-10^9 ≤ target ≤ 2·10^9",
    hints=[
        "The closest value is on the path a search for the target would take.",
        "Walk down: left if target < node, right otherwise, updating the best candidate at every node.",
        "Compare distances with the tie rule, and compute them in long — the target can be 2·10⁹.",
    ],
    opt=("O(h)", "O(1)", "One root-to-leaf walk."),
    editorial=(
        "## The one thing this teaches\n**The search path contains the answer.** Leaving the path "
        "means moving away from the target in the BST order, and every value in a subtree you skip "
        "is farther than the node that sent you the other way.\n\n"
        "## Approach\n```java\nint best = root.val;\nfor (TreeNode t = root; t != null; t = target < t.val ? t.left : t.right) {\n"
        "    long d = Math.abs((long) t.val - target), bd = Math.abs((long) best - target);\n"
        "    if (d < bd || (d == bd && t.val < best)) best = t.val;\n}\n```\n\n"
        "## The tie rule\nWith target 6 and values 5 and 7, both are distance 1; the statement "
        "picks 5. Without the explicit `d == bd` branch, which one survives depends on the order "
        "the walk meets them."
    ),
    py='''
def solve(root, k):
    vals = []
    st = [root]
    while st:
        t = st.pop()
        vals.append(t.val)
        if t.left:
            st.append(t.left)
        if t.right:
            st.append(t.right)
    return min(vals, key=lambda v: (abs(v - k), v))
''',
    java='''
    static int solve(TreeNode root, int target) {
        int best = root.val;
        for (TreeNode t = root; t != null; t = target < t.val ? t.left : t.right) {
            long d = Math.abs((long) t.val - target), bd = Math.abs((long) best - target);
            if (d < bd || (d == bd && t.val < best)) best = t.val;
        }
        return best;
    }
''',
    examples=[("Example 1", "4 2 5 1 3\n4\n"), ("Example 2", "4 2 5 1 3\n6\n")],
    hidden=[
        ("Single node", "1\n4\n"),
        ("Closer on the left", "10 5 15\n12\n"),
        ("Tie goes to the smaller", "10 5 15 3 7\n6\n"),
        ("Below everything", "8 3 10\n-100\n"),
    ],
    expl=[
        "4 is in the tree.",
        "5 is the largest value and the closest.",
    ],
    prereqs=[
        ("bst", "The closest value lies on the search path toward the target."),
        ("overflow", "Distances computed in long since the target can exceed the int range."),
    ],
)

_p(
    "city-fewest-neighbours", "City With the Fewest Reachable Neighbours", "Medium",
    topics=["Graphs"], subtopics=["Dijkstra"], companies=["Amazon", "Uber"],
    shape="wgraph_k", ret="int", todo="Floyd–Warshall for all pairs; count cities within the threshold; ties go to the largest index",
    description=(
        "Cities `0..n−1` are joined by undirected weighted roads. For each city, count the other "
        "cities reachable with a shortest-path distance of **at most** the threshold. Print the "
        "city with the **fewest** such cities; on a tie, the **largest** index.\n\n"
        "### Input\n- Line 1: `n m threshold`.\n- Next `m` lines: `u v w`.\n\n### Output\nThe chosen city."
    ),
    constraints="2 ≤ n ≤ 100\n0 ≤ m ≤ n(n−1)/2\n1 ≤ w, threshold ≤ 10^4",
    hints=[
        "You need the distance between every pair of cities.",
        "With n ≤ 100, Floyd–Warshall's O(n³) is 10⁶ steps — simplest option.",
        "Count, for each city, the others with distance ≤ threshold. Iterate cities in increasing order and use ≤ so later ties win.",
    ],
    opt=("O(n³)", "O(n²)", "Floyd–Warshall over n ≤ 100 cities."),
    editorial=(
        "## The one thing this teaches\n**Pick the all-pairs algorithm by the size of n.** n "
        "Dijkstras cost O(n · m log n); Floyd–Warshall costs O(n³) and is four lines. At n = 100 "
        "both are instant, and the one with fewer places to make mistakes wins.\n\n"
        "## Approach\n```java\nlong[][] d = new long[n][n];   // INF except d[i][i] = 0 and the roads\n"
        "for (int k = 0; k < n; k++)\n    for (int i = 0; i < n; i++)\n        for (int j = 0; j < n; j++)\n"
        "            d[i][j] = Math.min(d[i][j], d[i][k] + d[k][j]);\n"
        "int best = -1, fewest = Integer.MAX_VALUE;\nfor (int i = 0; i < n; i++) {\n"
        "    int c = count of j != i with d[i][j] <= threshold;\n"
        "    if (c <= fewest) { fewest = c; best = i; }      // <= so the larger index wins ties\n}\n```\n\n"
        "## Two details\n- Roads are undirected: set both `d[u][v]` and `d[v][u]`, keeping the "
        "smaller weight if a pair repeats.\n"
        "- Use a large-but-safe `INF` so `d[i][k] + d[k][j]` cannot overflow."
    ),
    py='''
def solve(n, edges, k):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    best, fewest = -1, float("inf")
    for s in range(n):
        dist = [float("inf")] * n
        dist[s] = 0
        h = [(0, s)]
        while h:
            d, u = heapq.heappop(h)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                if d + w < dist[v]:
                    dist[v] = d + w
                    heapq.heappush(h, (d + w, v))
        c = sum(1 for j in range(n) if j != s and dist[j] <= k)
        if c <= fewest:
            fewest, best = c, s
    return best
''',
    java='''
    static int solve(int n, int[][] edges, int threshold) {
        final long INF = Long.MAX_VALUE / 4;
        long[][] d = new long[n][n];
        for (int i = 0; i < n; i++) { Arrays.fill(d[i], INF); d[i][i] = 0; }
        for (int[] e : edges) {
            d[e[0]][e[1]] = Math.min(d[e[0]][e[1]], e[2]);
            d[e[1]][e[0]] = Math.min(d[e[1]][e[0]], e[2]);
        }
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
        int best = -1, fewest = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            int c = 0;
            for (int j = 0; j < n; j++) if (j != i && d[i][j] <= threshold) c++;
            if (c <= fewest) { fewest = c; best = i; }
        }
        return best;
    }
''',
    examples=[
        ("Example 1", "4 4 4\n0 1 3\n1 2 1\n1 3 4\n2 3 1\n"),
        ("Example 2", "5 6 2\n0 1 2\n0 4 8\n1 2 3\n1 4 2\n2 3 1\n3 4 1\n"),
    ],
    hidden=[
        ("Road too long", "2 1 1\n0 1 2\n"),
        ("No roads", "3 0 5\n"),
        ("A chain", "3 2 10\n0 1 1\n1 2 1\n"),
    ],
    expl=[
        "Cities 0 and 3 each reach two others within distance 4; 3 has the larger index.",
        "City 0 reaches only city 1 within distance 2.",
    ],
    prereqs=[
        ("dijkstra", "Shortest distances from every city — by n Dijkstras or Floyd–Warshall."),
        ("graph_repr", "An adjacency matrix for the all-pairs dynamic programme."),
    ],
)

_p(
    "repeated-substring-pattern", "Repeated Substring Pattern", "Easy",
    topics=["Strings"], subtopics=["Matching"], companies=["Amazon", "Google"],
    shape="str", ret="String", todo="s is built from a repeated block exactly when s occurs in (s + s) with the first and last characters removed",
    description=(
        "Can `s` be built by concatenating copies of one of its proper substrings (at least two "
        "copies)?\n\n"
        "### Input\nOne line: `s`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| ≤ 10^4\ns consists of lowercase English letters.",
    hints=[
        "A repeating block's length must divide |s|. Try each such length and compare.",
        "A slicker test: if s is periodic, rotating it by one block gives s again.",
        "Every rotation of s appears in s + s. Remove the first and last character (the trivial rotations) and search for s.",
    ],
    opt=("O(n)", "O(n)", "With a linear-time string search (KMP); `contains` is fine in practice."),
    editorial=(
        "## The one thing this teaches\n**Periodicity is rotation invariance.** A string built from "
        "a block of length p equals itself rotated by p. Every rotation of `s` is a substring of "
        "`s + s`, so `s` is periodic exactly when it occurs in `s + s` at a position other than 0 "
        "or |s| — which trimming one character from each end enforces.\n\n"
        "## Approach\n```java\nString doubled = s + s;\nreturn doubled.substring(1, doubled.length() - 1).contains(s) ? \"YES\" : \"NO\";\n```\n\n"
        "## The direct version\nFor every length p that divides n with p < n, check `s` equals its "
        "first p characters repeated n/p times. O(n · d(n)), where d(n) is the number of divisors "
        "— small in practice, and easy to explain.\n\n"
        "The KMP failure function gives a third proof: s is periodic when `n % (n − lps[n−1]) == 0` "
        "and `lps[n−1] > 0`."
    ),
    py='''
def solve(s):
    n = len(s)
    for p in range(1, n // 2 + 1):
        if n % p == 0 and s[:p] * (n // p) == s:
            return "YES"
    return "NO"
''',
    java='''
    static String solve(String s) {
        String doubled = s + s;
        return doubled.substring(1, doubled.length() - 1).contains(s) ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "abab\n"), ("Example 2", "aba\n")],
    hidden=[
        ("Three blocks of three", "abcabcabcabc\n"),
        ("Single letter", "a\n"),
        ("One letter repeated", "aaaa\n"),
        ("Almost periodic", "abac\n"),
        ("Block with internal repeats", "abaababaab\n"),
    ],
    expl=[
        "`ab` twice.",
        "No proper block tiles `aba`.",
    ],
    prereqs=[
        ("string_basics", "Comparing a candidate block repeated against the string."),
        ("math_digits", "A block length must divide the string's length."),
    ],
)

_p(
    "smallest-string-with-swaps", "Smallest String With Swaps", "Medium",
    topics=["Graphs", "Strings"], subtopics=["Union-Find", "Sorting"], companies=["Amazon"],
    shape="str_pairs", ret="String", todo="union the index pairs; within each group, sort its characters into its sorted positions",
    description=(
        "Each pair `a b` allows swapping the characters at indices `a` and `b`, any number of times, "
        "in any order. Print the lexicographically smallest string reachable.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `m`.\n- Next `m` lines: `a b` (0-indexed).\n\n"
        "### Output\nThe smallest string."
    ),
    constraints="1 ≤ |s| ≤ 10^5\n0 ≤ m ≤ 10^5\ns consists of lowercase English letters.",
    hints=[
        "Swaps compose: if a↔b and b↔c are allowed, any arrangement of positions a, b, c is reachable.",
        "So indices form connected groups, and within a group the characters can be permuted freely.",
        "Group indices with union-find; for each group, place its characters in sorted order into its sorted indices.",
    ],
    opt=("O((n + m) α(n) + n log n)", "O(n)", "Union-find for groups, then sorting each group's characters."),
    editorial=(
        "## The one thing this teaches\n**Allowed swaps generate every permutation of a connected "
        "group.** Adjacent transpositions generate all permutations; so do the transpositions along "
        "any connected graph. The question \"what can I reach with these swaps?\" becomes \"which "
        "indices are connected?\" — a union-find question.\n\n"
        "## Approach\n```java\nfor (int[] p : pairs) union(p[0], p[1]);\n"
        "Map<Integer, List<Integer>> groups = indices grouped by find(i);   // indices ascend naturally\n"
        "char[] out = s.toCharArray();\nfor (List<Integer> idx : groups.values()) {\n"
        "    char[] cs = characters of s at idx, sorted;\n"
        "    for (int j = 0; j < idx.size(); j++) out[idx.get(j)] = cs[j];\n}\n```\n\n"
        "## Why sorted into sorted\nTo make the string smallest, the earliest position of each group "
        "should get its smallest character, the next position the next smallest, and so on — and "
        "groups do not interact, so each is optimised independently."
    ),
    py='''
def solve(s, p):
    n = len(s)
    adj = [[] for _ in range(n)]
    for a, b in p:
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    out = list(s)
    for start in range(n):
        if seen[start]:
            continue
        comp = []
        st = [start]
        seen[start] = True
        while st:
            u = st.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    st.append(v)
        comp.sort()
        chars = sorted(s[i] for i in comp)
        for i, ch in zip(comp, chars):
            out[i] = ch
    return "".join(out)
''',
    java='''
    static int[] parent;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static String solve(String s, int[][] pairs) {
        int n = s.length();
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int[] p : pairs) parent[find(p[0])] = find(p[1]);
        Map<Integer, List<Integer>> groups = new HashMap<>();
        for (int i = 0; i < n; i++) groups.computeIfAbsent(find(i), x -> new ArrayList<>()).add(i);
        char[] out = s.toCharArray();
        for (List<Integer> idx : groups.values()) {
            char[] cs = new char[idx.size()];
            for (int j = 0; j < cs.length; j++) cs[j] = s.charAt(idx.get(j));
            Arrays.sort(cs);
            for (int j = 0; j < cs.length; j++) out[idx.get(j)] = cs[j];
        }
        return new String(out);
    }
''',
    examples=[("Example 1", "dcab\n2\n0 3\n1 2\n"), ("Example 2", "dcab\n3\n0 3\n1 2\n0 2\n")],
    hidden=[
        ("Chain of swaps", "cba\n2\n0 1\n1 2\n"),
        ("Single letter", "a\n0\n"),
        ("No swaps", "zyx\n0\n"),
        ("Two groups", "zyxwv\n2\n0 4\n1 3\n"),
    ],
    expl=[
        "Groups {0,3} and {1,2}: `d,b` → `b,d` and `c,a` → `a,c` gives `bacd`.",
        "All four indices are connected, so the letters sort fully: `abcd`.",
    ],
    prereqs=[
        ("union_find", "Grouping indices that allowed swaps connect."),
        ("sorting", "Within a group, sorted characters go into sorted positions."),
    ],
)

_p(
    "lca-deepest-leaves", "Lowest Common Ancestor of Deepest Leaves", "Medium",
    topics=["Trees"], subtopics=["Tree DFS"], companies=["Meta", "Amazon"],
    shape="tree", ret="int", todo="post-order returning (depth of deepest leaf below, LCA of those leaves)",
    description=(
        "Find the lowest common ancestor of **all** the deepest leaves of a binary tree, and print "
        "its value. (If there is one deepest leaf, it is its own answer.)\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe value of that ancestor."
    ),
    constraints="1 ≤ nodes ≤ 1000\n0 ≤ value ≤ 1000, values distinct",
    hints=[
        "For each subtree, you need two things: how deep its deepest leaf is, and the LCA of the leaves at that depth.",
        "If both children reach the same depth, the current node is the LCA of all of them.",
        "Otherwise the deeper child's answer carries up unchanged, with its depth increased by one.",
    ],
    opt=("O(n)", "O(h)", "One post-order traversal returning a pair."),
    editorial=(
        "## The one thing this teaches\n**Return a pair to avoid a second pass.** The LCA depends on "
        "depths, and depths depend on the whole subtree. Returning `(depth, lca)` from each call "
        "lets every node decide from its children alone.\n\n"
        "## Approach\n```java\n// returns {depth, lcaValue}\nint[] dfs(TreeNode t) {\n"
        "    if (t == null) return new int[]{0, -1};\n    int[] l = dfs(t.left), r = dfs(t.right);\n"
        "    if (l[0] == r[0]) return new int[]{l[0] + 1, t.val};   // deepest leaves on both sides\n"
        "    return l[0] > r[0] ? new int[]{l[0] + 1, l[1]} : new int[]{r[0] + 1, r[1]};\n}\n```\n\n"
        "## Why equal depths mean \"here\"\nIf the deepest leaves on the left and right are equally "
        "deep, they are all deepest leaves of this subtree, and they sit on both sides — so no "
        "lower node contains them all. A leaf returns its own value, since both null children "
        "have depth 0."
    ),
    py='''
def solve(root):
    parent = {root: None}
    level = [root]
    while True:
        nxt = []
        for t in level:
            for c in (t.left, t.right):
                if c:
                    parent[c] = t
                    nxt.append(c)
        if not nxt:
            break
        level = nxt
    nodes = set(level)
    while len(nodes) > 1:
        nodes = {parent[t] for t in nodes}
    return next(iter(nodes)).val
''',
    java='''
    static int[] dfs(TreeNode t) {
        if (t == null) return new int[]{0, -1};
        int[] l = dfs(t.left), r = dfs(t.right);
        if (l[0] == r[0]) return new int[]{l[0] + 1, t.val};
        return l[0] > r[0] ? new int[]{l[0] + 1, l[1]} : new int[]{r[0] + 1, r[1]};
    }

    static int solve(TreeNode root) {
        return dfs(root)[1];
    }
''',
    examples=[("Example 1", "3 5 1 6 2 0 8 null null 7 4\n"), ("Example 2", "1\n")],
    hidden=[
        ("Deepest leaf alone", "0 1 3 null 2\n"),
        ("Two leaves at the same depth", "1 2 3\n"),
        ("One deep leaf", "1 2 3 4\n"),
        ("Deepest leaves under different subtrees", "1 2 3 4 null null 5\n"),
    ],
    expl=[
        "The deepest leaves are 7 and 4, both children of 2.",
        "A single node is its own deepest leaf.",
    ],
    prereqs=[
        ("tree_dp", "Each subtree returns its deepest-leaf depth and the LCA of those leaves."),
        ("tree_traversal", "A post-order traversal combining the children's pairs."),
    ],
)
