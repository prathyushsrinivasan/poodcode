# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 33 — eight short lessons across the curriculum.
#
#   tribonacci                      three rolling variables instead of a memo table
#   sum-of-powers-of-three          distinct powers of three ⇔ base-3 digits are all 0 or 1
#   sum-of-left-leaves              the parent knows whether a child is a left child
#   splitting-string-descending     choose the first number, then every later number is forced
#   left-right-sum-differences      total, running left sum, and right = total − left − a[i]
#   merge-strings-alternately       one index, two strings, append the leftover
#   min-cost-move-chips             only parity costs anything
#   house-robber-iv                 binary search the capability; greedy counts houses
# ===========================================================================

_p(
    "tribonacci", "N-th Tribonacci Number", "Easy",
    topics=["Recursion", "Dynamic Programming"], subtopics=["Memoisation", "Rolling Variables"], companies=["Coursera"],
    shape="n", ret="long", todo="T0 = 0, T1 = 1, T2 = 1; roll three variables forward n times",
    description=(
        "The Tribonacci sequence is `T0 = 0`, `T1 = 1`, `T2 = 1`, and "
        "`T(n) = T(n−1) + T(n−2) + T(n−3)` for `n ≥ 3`. Print `T(n)`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\n`T(n)`."
    ),
    constraints="0 ≤ n ≤ 60",
    hints=[
        "The direct recursion calls itself three times per level — roughly 1.84^n calls.",
        "Each value depends only on the previous three. Memoising them removes the repetition.",
        "Keep just three variables and roll them forward; T(60) needs a long.",
    ],
    opt=("O(n)", "O(1)", "n steps, three variables."),
    editorial=(
        "## The one thing this teaches\n**When a recurrence looks back a fixed distance, keep a "
        "fixed window.** Fibonacci keeps two values; Tribonacci keeps three. The table a memo "
        "would build is never needed beyond its last three entries.\n\n"
        "## Approach\n```java\nif (n == 0) return 0;\nlong a = 0, b = 1, c = 1;          // T(i−2), T(i−1), T(i) for i = 2\n"
        "for (int i = 3; i <= n; i++) {\n    long next = a + b + c;\n    a = b; b = c; c = next;\n}\nreturn c;\n```\n\n"
        "## Why the naive recursion explodes\n`T(n)` calls `T(n−1)`, `T(n−2)` and `T(n−3)`, which "
        "call overlapping sets again. The number of calls grows like the sequence itself — "
        "about 2.5·10^15 at n = 60.\n\n"
        "## Small n\nThe loop starts at 3; `T(1)` and `T(2)` are both 1 and come straight from the "
        "initial values."
    ),
    py='''
def solve(n):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def t(i):
        if i == 0:
            return 0
        if i <= 2:
            return 1
        return t(i - 1) + t(i - 2) + t(i - 3)

    return t(n)
''',
    java='''
    static long solve(long nn) {
        int n = (int) nn;
        if (n == 0) return 0;
        long a = 0, b = 1, c = 1;
        for (int i = 3; i <= n; i++) {
            long next = a + b + c;
            a = b;
            b = c;
            c = next;
        }
        return c;
    }
''',
    examples=[("Example 1", "4\n"), ("Example 2", "25\n")],
    hidden=[
        ("Zero", "0\n"),
        ("One", "1\n"),
        ("Two", "2\n"),
        ("Largest", "60\n"),
    ],
    expl=[
        "0, 1, 1, 2, 4.",
        "The sequence grows quickly: T(25) = 1389537.",
    ],
    prereqs=[
        ("recurrence", "A sequence defined by its previous three terms."),
        ("recursion", "Why the naive recursive version repeats work, and how memoising fixes it."),
    ],
)

_p(
    "sum-of-powers-of-three", "Check if Number is a Sum of Powers of Three", "Medium",
    topics=["Math"], subtopics=["Number Bases"], companies=["Amazon"],
    shape="n", ret="String", todo="write n in base 3; it is a sum of distinct powers of three exactly when no digit is 2",
    description=(
        "Can `n` be written as a sum of **distinct** powers of three (`1, 3, 9, 27, …`)? Print "
        "`YES` or `NO`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 10^15",
    hints=[
        "Every number has a unique base-3 representation with digits 0, 1 and 2.",
        "A sum of distinct powers of three uses each power 0 or 1 times — a base-3 representation with no digit 2.",
        "Read the base-3 digits with n % 3 and n / 3; any 2 means NO.",
    ],
    opt=("O(log n)", "O(1)", "About 32 divisions by 3 for n near 10^15."),
    editorial=(
        "## The one thing this teaches\n**\"Distinct powers of b\" is base b with digits 0 and 1.** "
        "Base-3 representations are unique. If the representation needs a 2 somewhere, no other "
        "choice of distinct powers can produce the same number.\n\n"
        "## Approach\n```java\nwhile (n > 0) {\n    if (n % 3 == 2) return false;\n    n /= 3;\n}\nreturn true;\n```\n\n"
        "## Walkthrough: 21\n21 = 2·9 + 1·3 + 0·1, so base 3 is `210`. The 2 means 9 would be "
        "needed twice — NO. For 91 = 81 + 9 + 1, base 3 is `10101` — YES.\n\n"
        "## The greedy view\nSubtracting the largest power of three not exceeding n, repeatedly, "
        "succeeds exactly when each power is used at most once — the same condition, discovered "
        "from the top digit down."
    ),
    py='''
def solve(n):
    power = 1
    while power * 3 <= n:
        power *= 3
    while power >= 1:
        if n >= power:
            n -= power
        power //= 3
    return "YES" if n == 0 else "NO"
''',
    java='''
    static String solve(long n) {
        while (n > 0) {
            if (n % 3 == 2) return "NO";
            n /= 3;
        }
        return "YES";
    }
''',
    examples=[("Example 1", "12\n"), ("Example 2", "91\n"), ("Example 3", "21\n")],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("Power of ten", "1000000000000\n"),
        ("Large sum of powers", "205891132094892\n"),
    ],
    expl=[
        "12 = 9 + 3.",
        "91 = 81 + 9 + 1.",
        "21 would need 9 twice.",
    ],
    prereqs=[
        ("math_digits", "Base conversion with % and /."),
        ("iteration", "A loop that stops early on the first bad digit."),
    ],
)

_p(
    "sum-of-left-leaves", "Sum of Left Leaves", "Easy",
    topics=["Trees"], subtopics=["Tree DFS"], companies=["Adobe", "Amazon"],
    shape="tree", ret="long", todo="traverse; when a node's left child exists and has no children, add its value",
    description=(
        "Print the sum of all **left leaves**: leaves that are the left child of their parent.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child (empty for an empty tree).\n\n"
        "### Output\nThe sum (0 if there are none)."
    ),
    constraints="0 ≤ nodes ≤ 1000\n-1000 ≤ value ≤ 1000",
    hints=[
        "A leaf does not know whether it is a left child — its parent does.",
        "Check from the parent: is node.left non-null with no children of its own?",
        "Or pass a flag into the recursion saying whether the current node is a left child.",
    ],
    opt=("O(n)", "O(h)", "One traversal; the stack depth is the height."),
    editorial=(
        "## The one thing this teaches\n**Decide at the level that has the information.** "
        "\"Leaf\" is a property of the node; \"left\" is a property of the edge from its parent. "
        "Checking from the parent sees both.\n\n"
        "## Approach\n```java\nlong sum = 0;\nDeque<TreeNode> st = new ArrayDeque<>();\nif (root != null) st.push(root);\n"
        "while (!st.isEmpty()) {\n    TreeNode t = st.pop();\n"
        "    if (t.left != null && t.left.left == null && t.left.right == null) sum += t.left.val;\n"
        "    if (t.left != null) st.push(t.left);\n    if (t.right != null) st.push(t.right);\n}\n```\n\n"
        "## The root is not a left leaf\nA single-node tree has a leaf with no parent, so the "
        "answer is 0.\n\n"
        "## Right leaves do not count\nIn `3 9 20 null null 15 7`, the leaves are 9, 15 and 7; "
        "only 9 and 15 are left children."
    ),
    py='''
def solve(root):
    def walk(node, is_left):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return node.val if is_left else 0
        return walk(node.left, True) + walk(node.right, False)
    return walk(root, False)
''',
    java='''
    static long solve(TreeNode root) {
        long sum = 0;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        if (root != null) st.push(root);
        while (!st.isEmpty()) {
            TreeNode t = st.pop();
            if (t.left != null && t.left.left == null && t.left.right == null) sum += t.left.val;
            if (t.left != null) st.push(t.left);
            if (t.right != null) st.push(t.right);
        }
        return sum;
    }
''',
    examples=[("Example 1", "3 9 20 null null 15 7\n"), ("Example 2", "1\n")],
    hidden=[
        ("Two left leaves", "1 2 3 4 5\n"),
        ("Empty tree", "\n"),
        ("Negative left chain", "0 -1 null -2\n"),
        ("Right leaves only", "1 null 2 null 3\n"),
    ],
    expl=[
        "9 and 15 are left leaves: 24.",
        "The root alone is not a left child.",
    ],
    prereqs=[
        ("tree_traversal", "A traversal that inspects each node's children."),
        ("tree_basics", "What makes a node a leaf, and a child left or right."),
    ],
)

_p(
    "splitting-string-descending", "Splitting a String Into Descending Consecutive Values", "Medium",
    topics=["Backtracking", "Strings"], subtopics=["Forced Choices"], companies=["Google"],
    shape="str", ret="String", todo="try every first piece; after that each next piece must equal previous − 1, so recurse only on matching prefixes",
    description=(
        "Can the digit string `s` be split into **two or more** non-empty pieces whose numeric "
        "values (leading zeros allowed) are strictly decreasing by exactly 1 from each piece to "
        "the next? Print `YES` or `NO`.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| ≤ 18\ns consists of digits",
    hints=[
        "Once the first number is chosen, every later number is determined: previous − 1.",
        "So the only real choice is where the first piece ends — at most 17 options.",
        "For each first piece, walk the rest recursively, trying the prefixes whose value equals the needed number. Leading zeros mean several prefixes can match (0, 00, 000).",
    ],
    opt=("O(n²)", "O(n)", "At most n first pieces; each continuation checks a few prefixes per level."),
    editorial=(
        "## The one thing this teaches\n**Backtracking collapses when choices are forced.** The "
        "search looks exponential, but after the first cut the value of every piece is fixed. "
        "Only leading zeros leave any freedom in where a piece ends.\n\n"
        "## Approach\n```java\nboolean go(String s, int i, long prev) {\n    if (i == s.length()) return true;\n"
        "    long v = 0;\n    for (int j = i; j < s.length(); j++) {\n        v = v * 10 + (s.charAt(j) - '0');\n"
        "        if (v > prev - 1) break;               // only grows from here\n"
        "        if (v == prev - 1 && go(s, j + 1, v)) return true;\n    }\n    return false;\n}\n"
        "// try each first piece s[0..k] for k < n − 1\n```\n\n"
        "## Why break when v exceeds prev − 1\nDigits only add to the value as the piece grows, so "
        "once it is too large, longer pieces are too large as well.\n\n"
        "## Walkthrough: 050043\nFirst piece `05` = 5. Next must be 4: `004` = 4. Next must be 3: "
        "`3`. The whole string is used — YES."
    ),
    py='''
def solve(s):
    def rest(i, prev):
        if i == len(s):
            return True
        return any(int(s[i:j]) == prev - 1 and rest(j, prev - 1) for j in range(i + 1, len(s) + 1))
    return "YES" if any(rest(k, int(s[:k])) for k in range(1, len(s))) else "NO"
''',
    java='''
    static boolean go(String s, int i, long prev) {
        if (i == s.length()) return true;
        long v = 0;
        for (int j = i; j < s.length(); j++) {
            v = v * 10 + (s.charAt(j) - '0');
            if (v > prev - 1) break;
            if (v == prev - 1 && go(s, j + 1, v)) return true;
        }
        return false;
    }

    static String solve(String s) {
        long first = 0;
        for (int k = 0; k < s.length() - 1; k++) {
            first = first * 10 + (s.charAt(k) - '0');
            if (go(s, k + 1, first)) return "YES";
        }
        return "NO";
    }
''',
    examples=[("Example 1", "1234\n"), ("Example 2", "050043\n"), ("Example 3", "9080701\n"), ("Example 4", "10009998\n")],
    hidden=[
        ("Single digit", "1\n"),
        ("Two digits", "21\n"),
        ("Leading zeros everywhere", "0090089\n"),
        ("Zeros cannot descend", "001\n"),
        ("Ten to zero", "10\n"),
        ("Leading zeros in later parts", "200100\n"),
    ],
    expl=[
        "The digits increase, so no split descends.",
        "05, 004, 3 → 5, 4, 3.",
        "No split works: 90, 80, 70, 1 are not consecutive.",
        "100, 099, 98.",
    ],
    prereqs=[
        ("backtracking", "Recursion over split points, pruned when a value overshoots."),
        ("math_digits", "Building a number digit by digit, leading zeros included."),
    ],
)

_p(
    "left-right-sum-differences", "Left and Right Sum Differences", "Easy",
    topics=["Prefix Sums", "Arrays"], subtopics=["Running Sum"], companies=["Amazon"],
    shape="arr", ret="String", todo="compute the total; walk with a running left sum, right = total − left − a[i], output |left − right|",
    description=(
        "For each index `i`, let `left` be the sum of elements before `i` and `right` the sum of "
        "elements after `i`. Print `|left − right|` for every index.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\n`n` values separated by spaces."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ a[i] ≤ 10^5",
    hints=[
        "Summing both sides for every index is O(n²).",
        "The elements before i, the element i itself and the elements after i together make the total.",
        "Keep a running left sum; right = total − left − a[i].",
    ],
    opt=("O(n)", "O(n)", "One pass for the total, one pass for the answers."),
    editorial=(
        "## The one thing this teaches\n**Three parts make the whole.** Left, the element, and "
        "right sum to the total, so knowing two gives the third. A running left sum is all the "
        "extra state needed.\n\n"
        "## Approach\n```java\nlong total = sum(a), left = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    long right = total - left - a[i];\n    output(Math.abs(left - right));\n    left += a[i];\n}\n```\n\n"
        "## Update order\n`left` must exclude `a[i]` when the answer for `i` is computed, so it is "
        "updated *after* output.\n\n"
        "## Walkthrough: 10 4 8 3\nLeft sums 0, 10, 14, 22; right sums 15, 11, 3, 0. Differences "
        "15, 1, 11, 22."
    ),
    py='''
def solve(a):
    return " ".join(str(abs(sum(a[:i]) - sum(a[i + 1:]))) for i in range(len(a)))
''',
    java='''
    static String solve(int[] a) {
        long total = 0, left = 0;
        for (int x : a) total += x;
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) {
            long right = total - left - a[i];
            if (i > 0) sb.append(' ');
            sb.append(Math.abs(left - right));
            left += a[i];
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "4\n10 4 8 3\n"), ("Example 2", "1\n1\n")],
    hidden=[
        ("Symmetric", "3\n5 1 5\n"),
        ("Increasing", "5\n1 2 3 4 5\n"),
        ("Large values", "2\n100000 100000\n"),
    ],
    expl=[
        "Left sums 0, 10, 14, 22 against right sums 15, 11, 3, 0.",
        "Both sides are empty.",
    ],
    prereqs=[
        ("prefix_sum", "A running left sum and the total."),
        ("array_patterns", "Updating state after using it for the current index."),
    ],
)

_p(
    "merge-strings-alternately", "Merge Strings Alternately", "Easy",
    topics=["Two Pointers", "Strings"], subtopics=["Interleaving"], companies=["Uber", "Amazon"],
    shape="str2", ret="String", todo="take one character from each string in turn; when one runs out, append the rest of the other",
    description=(
        "Merge two strings by taking characters alternately, starting with the first string. "
        "When one string runs out, append the remainder of the other.\n\n"
        "### Input\n- Line 1: `word1`.\n- Line 2: `word2`.\n\n"
        "### Output\nThe merged string."
    ),
    constraints="1 ≤ |word1|, |word2| ≤ 100\nLowercase English letters",
    hints=[
        "Walk an index i from 0 while either string still has a character at i.",
        "At each i, append word1[i] if it exists, then word2[i] if it exists.",
        "Use a StringBuilder rather than repeated string concatenation.",
    ],
    opt=("O(m + n)", "O(m + n)", "Each character is appended once."),
    editorial=(
        "## The one thing this teaches\n**Let the loop run to the longer length and guard each "
        "read.** Instead of a main loop plus two cleanup loops, one index over the longer length "
        "with a bounds check per string handles every case.\n\n"
        "## Approach\n```java\nStringBuilder sb = new StringBuilder();\n"
        "for (int i = 0; i < Math.max(a.length(), b.length()); i++) {\n"
        "    if (i < a.length()) sb.append(a.charAt(i));\n    if (i < b.length()) sb.append(b.charAt(i));\n}\n```\n\n"
        "## Why a StringBuilder\n`result += ch` in a loop copies the whole string each time — "
        "O(n²) total. A builder appends in amortised O(1).\n\n"
        "## Order within a round\nThe first string's character always comes first, including in "
        "the last round when both still have characters."
    ),
    py='''
def solve(s, t):
    out = []
    for i in range(max(len(s), len(t))):
        out.append(s[i:i + 1])
        out.append(t[i:i + 1])
    return "".join(out)
''',
    java='''
    static String solve(String a, String b) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < Math.max(a.length(), b.length()); i++) {
            if (i < a.length()) sb.append(a.charAt(i));
            if (i < b.length()) sb.append(b.charAt(i));
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "abc\npqr\n"), ("Example 2", "ab\npqrs\n"), ("Example 3", "abcd\npq\n")],
    hidden=[
        ("Single letters", "a\nb\n"),
        ("Second much longer", "x\nyyyyy\n"),
        ("First much longer", "zzzz\ny\n"),
    ],
    expl=[
        "a p b q c r.",
        "a p b q, then the leftover rs.",
        "a p b q, then the leftover cd.",
    ],
    prereqs=[
        ("two_pointers", "Advancing through two sequences in lockstep."),
        ("string_basics", "Building strings efficiently with a StringBuilder."),
    ],
)

_p(
    "min-cost-move-chips", "Minimum Cost to Move Chips to the Same Position", "Easy",
    topics=["Greedy", "Math"], subtopics=["Parity"], companies=["Morgan Stanley"],
    shape="arr", ret="int", todo="moves of 2 are free, so only parity matters: the answer is min(chips on even positions, chips on odd positions)",
    description=(
        "Chips sit at the given positions. Moving a chip by 2 in either direction is **free**; "
        "moving it by 1 costs **1**. Print the minimum cost to move all chips to one position.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` positions.\n\n"
        "### Output\nThe minimum cost."
    ),
    constraints="1 ≤ n ≤ 100\n1 ≤ position ≤ 10^9",
    hints=[
        "With free moves of 2, any chip can reach any position of the same parity at no cost.",
        "So the only question is how many chips must change parity, each paying 1.",
        "Gather everything on an even position or on an odd one — pay for the smaller group.",
    ],
    opt=("O(n)", "O(1)", "Two counters."),
    editorial=(
        "## The one thing this teaches\n**Find what the free operations cannot change.** Free "
        "moves by 2 preserve parity, and they connect every position of the same parity. What "
        "remains is a choice between two classes.\n\n"
        "## Approach\n```java\nint even = 0, odd = 0;\nfor (int p : position) {\n"
        "    if (p % 2 == 0) even++; else odd++;\n}\nreturn Math.min(even, odd);\n```\n\n"
        "## Why each switching chip pays exactly 1\nA chip that must change parity needs at least "
        "one odd-length step, costing 1; everything else is done in free steps of 2.\n\n"
        "## Positions do not matter\n`1` and `1000000000` cost the same as `1` and `2`: one chip "
        "must change parity."
    ),
    py='''
def solve(a):
    return min(sum(abs(p - target) % 2 for p in a) for target in set(a))
''',
    java='''
    static int solve(int[] position) {
        int even = 0, odd = 0;
        for (int p : position) {
            if (p % 2 == 0) even++; else odd++;
        }
        return Math.min(even, odd);
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "5\n2 2 2 3 3\n"), ("Example 3", "2\n1 1000000000\n")],
    hidden=[
        ("One chip", "1\n7\n"),
        ("All odd", "4\n1 3 5 7\n"),
        ("Balanced", "4\n1 2 3 4\n"),
    ],
    expl=[
        "Move 1 and 3 to each other for free; moving 2 costs 1.",
        "Move the two chips at 3 onto 2.",
        "One chip must change parity.",
    ],
    prereqs=[
        ("greedy", "Choosing the cheaper of two classes once the free moves are understood."),
        ("modulo", "Parity as the invariant of moves by 2."),
    ],
)

_p(
    "house-robber-iv", "House Robber IV", "Medium",
    topics=["Binary Search", "Greedy", "Dynamic Programming"], subtopics=["Binary Search on Answer"], companies=["Google"],
    shape="arr_k", ret="long", todo="binary search the capability c; greedily take every house ≤ c that is not next to the last one taken; check the count reaches k",
    description=(
        "A robber will steal from **at least `k`** houses and never from two adjacent houses. The "
        "robber's **capability** is the largest amount taken from a single house. Print the "
        "minimum possible capability.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: the `n` house values.\n\n"
        "### Output\nThe minimum capability."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ value ≤ 10^9\n1 ≤ k ≤ (n + 1) / 2",
    hints=[
        "Minimising a maximum: fix a capability c and ask whether k non-adjacent houses with values ≤ c exist.",
        "For a fixed c, taking an allowed house as early as possible never hurts — it leaves the most room to the right.",
        "The check is monotone in c, so binary search c over the house values.",
    ],
    opt=("O(n log W)", "O(1)", "A linear greedy check per step of a binary search over values up to W."),
    editorial=(
        "## The one thing this teaches\n**Minimise a maximum by searching a threshold.** The "
        "capability is the maximum of the chosen houses. Fixing that maximum turns the problem "
        "into a yes/no question with a simple greedy answer.\n\n"
        "## Approach\n```java\nlong lo = min(a), hi = max(a);\nwhile (lo < hi) {\n    long mid = (lo + hi) / 2;\n"
        "    if (canRob(a, k, mid)) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n\n"
        "boolean canRob(int[] a, long k, long cap) {\n    int count = 0;\n"
        "    for (int i = 0; i < a.length; i++)\n        if (a[i] <= cap) { count++; i++; }   // take it and skip the neighbour\n"
        "    return count >= k;\n}\n```\n\n"
        "## Why greedy-early is safe\nSwap the first chosen house of any valid selection for the "
        "earliest allowed house: it is no later, so it cannot conflict with the next choice.\n\n"
        "## The DP check\nA house-robber DP counting the maximum number of non-adjacent houses "
        "≤ c gives the same answer — slower by a constant, but a useful cross-check."
    ),
    py='''
def solve(a, k):
    for cap in sorted(set(a)):
        n = len(a)
        most = [0] * (n + 2)
        for i in range(n - 1, -1, -1):
            take = 1 + most[i + 2] if a[i] <= cap else 0
            most[i] = max(most[i + 1], take)
        if most[0] >= k:
            return cap
''',
    java='''
    static boolean canRob(int[] a, long k, long cap) {
        int count = 0;
        for (int i = 0; i < a.length; i++)
            if (a[i] <= cap) { count++; i++; }
        return count >= k;
    }

    static long solve(int[] a, long k) {
        long lo = Long.MAX_VALUE, hi = 0;
        for (int x : a) { lo = Math.min(lo, x); hi = Math.max(hi, x); }
        while (lo < hi) {
            long mid = (lo + hi) / 2;
            if (canRob(a, k, mid)) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "4 2\n2 3 5 9\n"), ("Example 2", "5 2\n2 7 9 3 1\n")],
    hidden=[
        ("One house", "1 1\n5\n"),
        ("Skip the middle", "3 2\n1 100 1\n"),
        ("Cheap houses alternate", "6 3\n5 1 5 1 5 1\n"),
        ("Forced choice", "7 4\n9 8 7 6 5 4 3\n"),
    ],
    expl=[
        "Robbing houses 0 and 2 (values 2 and 5) gives capability 5; any other valid pair is worse.",
        "Houses 0 and 4 hold 2 and 1: capability 2.",
    ],
    prereqs=[
        ("binary_search", "Searching for the smallest threshold that passes a monotone check."),
        ("greedy", "Taking the earliest allowed house in the feasibility check."),
    ],
)
