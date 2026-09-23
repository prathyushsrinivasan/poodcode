# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 60 — Trees & Graphs round 3: patterns the stage teaches in prose and
# no problem forced.
#
#   count-univalue-subtrees   bottom-up boolean, plus a counter
#   insufficient-nodes-prune  sum passed down, "keep me?" passed up; the root can go
#   bst-range-count           the pruned range walk, counting
#   inorder-predecessor       the successor's mirror, by one descent
#   max-unique-split          backtracking over splits with a used-set
#   split-into-fibonacci      the first two numbers decide everything
#   gene-mutation-steps       BFS over strings restricted to a bank
#   regions-by-slashes        every cell is four triangles; union-find joins them
#   portal-maze               grid BFS where a letter is also an edge to its twin
#
# Defines the shapes `tree_k_out` and `str2_list`.
# ===========================================================================

# a tree line, then an integer; a tree out
_SHAPES["tree_k_out"] = dict(
    py=_LEVEL_PY + "\n" + _TREE_PY + "k = int(L[1])\n", py_params="root, k",
    js=_TREE_JS + _LEVEL_JS + "const k = Number(L[1]);\n", js_params="root, k",
    java_members=_TREE_JAVA_MEMBERS + "\n" + _LEVEL_JAVA,
    java=_TREE_JAVA_READ + "        int k = Integer.parseInt(sc.nextLine().trim());\n",
    java_params="TreeNode root, int k", java_args="root, k", wrap="level",
)
# two tokens, then k, then k tokens
_SHAPES["str2_list"] = dict(
    py="d = sys.stdin.read().split()\ns, t = d[0], d[1]\nk = int(d[2])\nwords = d[3:3 + k]\n",
    py_params="s, t, words",
    js=_JS_NUMS + "const s = d[0], t = d[1], k = Number(d[2]);\nconst words = d.slice(3, 3 + k);\n",
    js_params="s, t, words",
    java="        String s = sc.next(), t = sc.next();\n        int k = sc.nextInt();\n"
         "        String[] words = new String[k];\n        for (int i = 0; i < k; i++) words[i] = sc.next();\n",
    java_params="String s, String t, String[] words", java_args="s, t, words",
)


_p(
    "count-univalue-subtrees", "Single-Colour Branches", "Medium",
    topics=["Tree"], subtopics=["Tree", "Post-order", "Tree DP"],
    companies=["Google", "Amazon"],
    shape="tree", ret="int",
    todo="post-order: a subtree is uni-valued if both children are and each existing child has the node's value; count those",
    description=(
        "A subtree (a node with everything below it) is **uni-valued** if every node in it has the "
        "same value. Count the uni-valued subtrees. Every leaf is one.\n\n"
        "### Input\nOne line: the tree in level order.\n\n### Output\nThe count."
    ),
    constraints="1 ≤ nodes ≤ 3000\n0 ≤ value ≤ 9",
    hints=[
        "Checking every subtree from scratch is O(n²). Each node's answer depends only on its children's.",
        "Return a boolean \"my subtree is uni-valued\" and increment a counter when it is true.",
        "Call both children *before* combining — a short-circuit `&&` skips the right child's count.",
    ],
    opt=("O(n)", "O(h)", "One post-order pass."),
    editorial=(
        "## The one thing this teaches\n**Return one thing, count another** — the same shape as "
        "diameter, with a boolean.\n\n"
        "## Approach\n```java\nboolean uni(TreeNode n) {\n    if (n == null) return true;\n"
        "    boolean l = uni(n.left), r = uni(n.right);          // both, always\n"
        "    if (!l || !r) return false;\n    if (n.left != null && n.left.val != n.val) return false;\n"
        "    if (n.right != null && n.right.val != n.val) return false;\n    count++;\n    return true;\n}\n```\n\n"
        "## The short-circuit trap\n`return uni(n.left) && uni(n.right) && …` never visits the "
        "right subtree when the left fails, and its uni-valued subtrees go uncounted."
    ),
    py='''
def solve(root):
    order, st = [], [root]
    while st:
        n = st.pop()
        order.append(n)
        if n.left:
            st.append(n.left)
        if n.right:
            st.append(n.right)
    uni, count = {}, 0
    for n in reversed(order):
        ok = all(uni[c] and c.val == n.val for c in (n.left, n.right) if c)
        uni[n] = ok
        count += ok
    return count
''',
    java='''
    static int count = 0;

    static boolean uni(TreeNode n) {
        if (n == null) return true;
        boolean l = uni(n.left), r = uni(n.right);
        if (!l || !r) return false;
        if (n.left != null && n.left.val != n.val) return false;
        if (n.right != null && n.right.val != n.val) return false;
        count++;
        return true;
    }

    static int solve(TreeNode root) {
        uni(root);
        return count;
    }
''',
    examples=[
        ("Example 1", "4 1 4 1 1 null 4\n"),
        ("Example 2", "2 2 2 2 2 2\n"),
    ],
    hidden=[
        ("One node", "7\n"),
        ("Left fails, right counts", "1 2 1 null null 1 1\n"),
        ("A chain of equals", _chain_line([3] * 6, "Z") + "\n"),
        ("Random", _rand_tree_line(300, 471, 0, 1) + "\n"),
        ("Large", _rand_tree_line(3000, 472, 0, 2) + "\n"),
    ],
    expl=[
        "The three leaves, the 1-subtree (1 with children 1 and 1) and the right 4-subtree (4 with child 4): 5.",
        "Every one of the six subtrees is all 2s.",
    ],
    prereqs=[
        ("tree_dp", "Each node returns a boolean built from its children's."),
        ("tree_traversal", "Post-order: both children before the node."),
    ],
)


_p(
    "insufficient-nodes-prune", "Prune the Weak Branches", "Medium",
    topics=["Tree"], subtopics=["Tree", "Top-down and Bottom-up"],
    companies=["Amazon", "Google"],
    shape="tree_k_out", ret="TreeNode",
    todo="pass the path sum down; a leaf survives if sum >= limit; an inner node survives if at least one child survives",
    description=(
        "A node is **insufficient** if every root-to-leaf path through it has a sum below `limit`. "
        "Delete every insufficient node (all at once) and print what is left in level order, or "
        "`EMPTY`.\n\n"
        "### Input\nLine 1: the tree in level order.\nLine 2: `limit`.\n\n### Output\nThe pruned tree."
    ),
    constraints="1 ≤ nodes ≤ 3000\n-10^5 ≤ value ≤ 10^5\n-10^9 ≤ limit ≤ 10^9",
    hints=[
        "A node's fate depends on the paths *through* it: the sum above it (top-down) and the best continuation below (bottom-up).",
        "Recurse with the running sum. At a leaf, keep it iff the full sum reaches the limit.",
        "An inner node is kept iff at least one child is kept after pruning — delete the children that return null first.",
    ],
    opt=("O(n)", "O(h)", "One traversal carrying a sum down and a verdict up."),
    editorial=(
        "## The one thing this teaches\n**Information in both directions.** The sum above a node "
        "flows down as a parameter; whether any path below succeeds flows up as the return value.\n\n"
        "## Approach\n```java\nTreeNode prune(TreeNode n, long sum) {\n    sum += n.val;\n"
        "    if (n.left == null && n.right == null) return sum >= limit ? n : null;\n"
        "    if (n.left != null) n.left = prune(n.left, sum);\n    if (n.right != null) n.right = prune(n.right, sum);\n"
        "    return (n.left == null && n.right == null) ? null : n;   // all paths failed\n}\n```\n\n"
        "## The subtle case\nAn inner node whose children are all pruned becomes a leaf — but it is "
        "deleted, not re-tested as a leaf: every path through it was already too small."
    ),
    py='''
def solve(root, k):
    sys.setrecursionlimit(20000)

    def prune(n, s):
        s += n.val
        if n.left is None and n.right is None:
            return n if s >= k else None
        if n.left:
            n.left = prune(n.left, s)
        if n.right:
            n.right = prune(n.right, s)
        return None if n.left is None and n.right is None else n

    return prune(root, 0)
''',
    java='''
    static int LIMIT;

    static TreeNode prune(TreeNode n, long s) {
        s += n.val;
        if (n.left == null && n.right == null) return s >= LIMIT ? n : null;
        if (n.left != null) n.left = prune(n.left, s);
        if (n.right != null) n.right = prune(n.right, s);
        return (n.left == null && n.right == null) ? null : n;
    }

    static TreeNode solve(TreeNode root, int k) {
        LIMIT = k;
        return prune(root, 0);
    }
''',
    examples=[
        ("Example 1", "6 2 9 -8 5 null 1 3\n10\n"),
        ("Example 2", "1 -3 4 5 null -2 6\n4\n"),
    ],
    hidden=[
        ("One node kept", "5\n5\n"),
        ("One node dropped", "5\n6\n"),
        ("Everything goes", "1 2 3\n100\n"),
        ("A child pruned, parent kept", "10 -20 5\n14\n"),
        ("Random", _rand_tree_line(300, 481, -20, 20) + "\n0\n"),
        ("Large", _rand_tree_line(3000, 482, -100, 100) + "\n50\n"),
    ],
    expl=[
        "6 + 2 + (−8) + 3 = 3 falls short, so 3 and then −8 go; 6 → 2 → 5 (13) and 6 → 9 → 1 (16) survive.",
        "1 − 3 + 5 = 3 and 1 + 4 − 2 = 3 are both below 4, so −3, 5 and −2 go; 1 + 4 + 6 = 11 keeps the root, 4 and 6.",
    ],
    prereqs=[
        ("tree_traversal", "A top-down parameter and a bottom-up return in the same recursion."),
        ("recursion", "Each call returns the (possibly deleted) subtree to its parent."),
    ],
)


_p(
    "bst-range-count", "How Many in the Range", "Easy",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Pruning"],
    companies=["Amazon", "Microsoft"],
    shape="tree_xy", ret="int",
    todo="count n if lo <= n.val <= hi; go left only if n.val > lo, right only if n.val < hi",
    description=(
        "Count the values of a BST (distinct values) that lie in `[lo, hi]`, visiting as few "
        "nodes as the BST rule allows.\n\n"
        "### Input\nLine 1: the BST in level order.\nLine 2: `lo hi`.\n\n### Output\nThe count."
    ),
    constraints="1 ≤ nodes ≤ 5000\nValues distinct, |value| ≤ 10^5\nlo ≤ hi",
    hints=[
        "Counting every node in range is a plain traversal. The BST rule lets you skip whole subtrees.",
        "If n.val ≤ lo, nothing in the left subtree can be in range (all smaller). If n.val ≥ hi, skip the right.",
        "The nodes visited are the in-range ones plus O(h) boundary nodes.",
    ],
    opt=("O(h + k)", "O(h)", "k = the number of values in range."),
    editorial=(
        "## The one thing this teaches\n**Pruning by the invariant.** The same walk as "
        "`range-sum-bst`, counting instead of summing — and the two conditions that decide which "
        "sides are worth visiting.\n\n"
        "## Approach\n```java\nint count(TreeNode n) {\n    if (n == null) return 0;\n"
        "    int c = (lo <= n.val && n.val <= hi) ? 1 : 0;\n    if (n.val > lo) c += count(n.left);\n"
        "    if (n.val < hi) c += count(n.right);\n    return c;\n}\n```"
    ),
    py='''
def solve(root, x, y):
    c, st = 0, [root]
    while st:
        n = st.pop()
        if n is None:
            continue
        if x <= n.val <= y:
            c += 1
        if n.val > x:
            st.append(n.left)
        if n.val < y:
            st.append(n.right)
    return c
''',
    java='''
    static int solve(TreeNode root, int x, int y) {
        int c = 0;
        ArrayDeque<TreeNode> st = new ArrayDeque<>();
        st.push(root);
        while (!st.isEmpty()) {
            TreeNode n = st.pop();
            if (x <= n.val && n.val <= y) c++;
            if (n.val > x && n.left != null) st.push(n.left);
            if (n.val < y && n.right != null) st.push(n.right);
        }
        return c;
    }
''',
    examples=[
        ("Example 1", _bst_line([10, 5, 15, 3, 7, 18]) + "\n6 15\n"),
        ("Example 2", _bst_line([4, 2, 6]) + "\n7 9\n"),
    ],
    hidden=[
        ("Everything", _bst_line([4, 2, 6, 1, 3]) + "\n-100 100\n"),
        ("A single value", _bst_line([4, 2, 6, 1, 3]) + "\n3 3\n"),
        ("Chain", _bst_line(list(range(1, 2001))) + "\n500 700\n"),
        ("Large", _bst_line([v * 7 - 17000 for v in _perm(5000, 491)]) + "\n-3000 9000\n"),
    ],
    expl=["7, 10 and 15 lie in [6, 15].", "Nothing lies in [7, 9]."],
    prereqs=[
        ("bst", "The BST rule tells you which subtrees cannot hold values in range."),
        ("tree_traversal", "An iterative DFS with pruning."),
    ],
)


_p(
    "inorder-predecessor", "The Value Just Below", "Medium",
    topics=["Tree", "Binary Search Tree"], subtopics=["Binary Search Tree", "Descent"],
    companies=["Microsoft", "Amazon"],
    shape="tree_k", ret="long",
    todo="descend: when k > n.val, n is a candidate (remember it) and go right; otherwise go left",
    description=(
        "In a BST of distinct values, print the largest value **strictly smaller** than `k` "
        "(`k` itself may or may not be in the tree), or `-1000000000` if there is none.\n\n"
        "### Input\nLine 1: the BST in level order.\nLine 2: `k`.\n\n### Output\nThe predecessor value."
    ),
    constraints="1 ≤ nodes ≤ 5000\nValues distinct, |value| ≤ 10^5\n|k| ≤ 10^5",
    hints=[
        "An in-order walk finds it in O(n). One descent is enough.",
        "At node n: if n.val < k, n is a candidate — but something larger and still below k may be in its right subtree. Remember n, go right.",
        "If n.val ≥ k, the answer is in the left subtree. The last candidate remembered is the answer.",
    ],
    opt=("O(h)", "O(1)", "One root-to-leaf descent."),
    editorial=(
        "## The one thing this teaches\n**The successor's mirror, with no parent pointers.** Every "
        "time the descent turns right, the node it leaves is smaller than k and larger than every "
        "earlier candidate — so the last one is the predecessor.\n\n"
        "## Approach\n```java\nlong best = -1_000_000_000L;\nfor (TreeNode n = root; n != null; ) {\n"
        "    if (n.val < k) { best = n.val; n = n.right; }\n    else n = n.left;\n}\n```"
    ),
    py='''
def solve(root, k):
    best, n = -10**9, root
    while n:
        if n.val < k:
            best = n.val
            n = n.right
        else:
            n = n.left
    return best
''',
    java='''
    static long solve(TreeNode root, int k) {
        long best = -1_000_000_000L;
        for (TreeNode n = root; n != null; ) {
            if (n.val < k) { best = n.val; n = n.right; }
            else n = n.left;
        }
        return best;
    }
''',
    examples=[
        ("Example 1", _bst_line([20, 10, 30, 5, 15, 25, 35]) + "\n25\n"),
        ("Example 2", _bst_line([20, 10, 30]) + "\n10\n"),
    ],
    hidden=[
        ("k absent, between values", _bst_line([20, 10, 30, 5, 15]) + "\n17\n"),
        ("Predecessor is an ancestor", _bst_line([20, 10, 30, 15, 12]) + "\n12\n"),
        ("k above everything", _bst_line([3, 1, 5]) + "\n100\n"),
        ("Chain", _bst_line(list(range(0, 4000, 2))) + "\n1001\n"),
        ("Large", _bst_line([v * 3 - 7000 for v in _perm(5000, 501)]) + "\n1234\n"),
    ],
    expl=["The descent turns right at 20 (a candidate), then left at 30 and at 25 (both too big): 20 is the answer.", "Nothing in the tree is smaller than 10."],
    prereqs=[
        ("bst", "Each comparison discards a subtree; a right turn records a candidate."),
        ("binary_search", "The descent is a binary search for the last value < k."),
    ],
)


_p(
    "max-unique-split", "The Most Different Pieces", "Medium",
    topics=["Backtracking", "String"], subtopics=["Backtracking", "String Split"],
    companies=["Google", "Amazon"],
    shape="str", ret="int",
    todo="choose where the next piece ends; skip a piece already used; track the best count; prune if count + remaining chars <= best",
    description=(
        "Split a string into non-empty pieces so that **no two pieces are equal**. Print the largest "
        "possible number of pieces.\n\n"
        "### Input\nOne string of lowercase letters.\n\n### Output\nThe maximum number of pieces."
    ),
    constraints="1 ≤ length ≤ 16",
    hints=[
        "Choose the first piece's end, then split the rest the same way — backtracking over split points.",
        "Keep a set of pieces used on the current path; add before recursing, remove after.",
        "Bound: even if every remaining character became its own piece, count + remaining ≤ best means stop.",
    ],
    opt=("O(2ⁿ · n) worst case", "O(n)", "2ⁿ⁻¹ ways to split, pruned by the bound."),
    editorial=(
        "## The one thing this teaches\n**Backtracking with a used-set and a bound.** The set is "
        "shared state (add / remove around the recursion); the bound is the pruning that makes "
        "n = 16 instant.\n\n"
        "## Approach\n```java\nvoid dfs(int i, int count) {\n    if (count + (n - i) <= best) return;          // cannot beat best\n"
        "    if (i == n) { best = count; return; }\n    for (int j = i + 1; j <= n; j++) {\n"
        "        String p = s.substring(i, j);\n        if (used.add(p)) { dfs(j, count + 1); used.remove(p); }\n    }\n}\n```"
    ),
    py='''
def solve(s):
    n, used, best = len(s), set(), [0]

    def dfs(i, cnt):
        if cnt + (n - i) <= best[0]:
            return
        if i == n:
            best[0] = cnt
            return
        for j in range(i + 1, n + 1):
            p = s[i:j]
            if p not in used:
                used.add(p)
                dfs(j, cnt + 1)
                used.discard(p)

    dfs(0, 0)
    return best[0]
''',
    java='''
    static String S;
    static int best = 0;
    static Set<String> used = new HashSet<>();

    static void dfs(int i, int cnt) {
        int n = S.length();
        if (cnt + (n - i) <= best) return;
        if (i == n) { best = cnt; return; }
        for (int j = i + 1; j <= n; j++) {
            String p = S.substring(i, j);
            if (used.add(p)) { dfs(j, cnt + 1); used.remove(p); }
        }
    }

    static int solve(String s) {
        S = s;
        dfs(0, 0);
        return best;
    }
''',
    examples=[("Example 1", "abacab\n"), ("Example 2", "zz\n")],
    hidden=[
        ("One letter", "q\n"),
        ("All different", "abcdefghijklmnop\n"),
        ("All the same", "aaaaaaaaaaaaaaaa\n"),
        ("Mixed", "abababababababab\n"),
        ("Random", "".join(chr(97 + x % 3) for x in _lcg_ints(511, 16, 0, 99)) + "\n"),
    ],
    expl=["a | b | ac | ab: four different pieces. Five would need a split into pieces of total length 6 with at most one of length 2, which forces a repeated letter.", "z | z repeats, so the only split is \"zz\" itself."],
    prereqs=[
        ("backtracking", "Choose a split point, recurse, undo the choice."),
        ("pruning", "Stop when even the best possible finish cannot beat the best so far."),
    ],
)


_p(
    "split-into-fibonacci", "Digits That Grow Like Rabbits", "Medium",
    topics=["Backtracking", "String"], subtopics=["Backtracking", "Constraint Search"],
    companies=["Amazon", "Google"],
    shape="str", ret="String",
    todo="try every length for the first two numbers; after that each next number is forced — check the string continues with it",
    description=(
        "Split a digit string into a sequence of at least three numbers where each number is the "
        "sum of the two before it. No number may have a leading zero (a single `0` is fine) and "
        "every number must be at most `2³¹ − 1`. Try the first number's length shortest first, then "
        "the second's; print the first sequence found, space-separated, or `NONE`.\n\n"
        "### Input\nOne string of digits.\n\n### Output\nThe sequence, or `NONE`."
    ),
    constraints="1 ≤ length ≤ 200",
    hints=[
        "Only the first two numbers are choices: once they are fixed, every later number is their sum — forced.",
        "So loop over the lengths of the first and second numbers (with leading-zero and overflow checks) and verify the rest by generating sums and matching the string.",
        "Stop a number's length loop once it exceeds 2³¹ − 1; compare with long.",
    ],
    opt=("O(n³) at most", "O(n)", "O(n²) choices of the first two, each checked in O(n)."),
    editorial=(
        "## The one thing this teaches\n**Find the real choices.** It looks like a search over "
        "every split point; in fact only two numbers are free and the rest is verification.\n\n"
        "## Approach\n```java\nfor (int i = 1; i <= n; i++) {                       // first number = s[0, i)\n"
        "    if (i > 1 && s.charAt(0) == '0') break;\n    long a = parse(0, i); if (a > MAX) break;\n"
        "    for (int j = i + 1; j < n; j++) {                // second = s[i, j)\n"
        "        if (j - i > 1 && s.charAt(i) == '0') break;\n        long b = parse(i, j); if (b > MAX) break;\n"
        "        List<Long> seq = check(a, b, j);             // extend with sums, match text\n"
        "        if (seq != null) return seq;\n    }\n}\n```"
    ),
    py='''
def solve(s):
    n, MAX = len(s), 2**31 - 1
    for i in range(1, n):
        if i > 1 and s[0] == "0":
            break
        a = int(s[:i])
        if a > MAX:
            break
        for j in range(i + 1, n):
            if j - i > 1 and s[i] == "0":
                break
            b = int(s[i:j])
            if b > MAX:
                break
            seq, x, y, pos = [a, b], a, b, j
            while pos < n:
                z = x + y
                if z > MAX:
                    break
                t = str(z)
                if not s.startswith(t, pos):
                    break
                seq.append(z)
                pos += len(t)
                x, y = y, z
            if pos == n and len(seq) >= 3:
                return " ".join(map(str, seq))
    return "NONE"
''',
    java='''
    static String solve(String s) {
        int n = s.length();
        long MAX = Integer.MAX_VALUE;
        for (int i = 1; i < n; i++) {
            if (i > 1 && s.charAt(0) == '0') break;
            if (i > 10) break;
            long a = Long.parseLong(s.substring(0, i));
            if (a > MAX) break;
            for (int j = i + 1; j < n; j++) {
                if (j - i > 1 && s.charAt(i) == '0') break;
                if (j - i > 10) break;
                long b = Long.parseLong(s.substring(i, j));
                if (b > MAX) break;
                List<Long> seq = new ArrayList<>(List.of(a, b));
                long x = a, y = b;
                int pos = j;
                while (pos < n) {
                    long z = x + y;
                    if (z > MAX) break;
                    String t = Long.toString(z);
                    if (!s.startsWith(t, pos)) break;
                    seq.add(z);
                    pos += t.length();
                    x = y;
                    y = z;
                }
                if (pos == n && seq.size() >= 3) {
                    StringBuilder sb = new StringBuilder();
                    for (int k = 0; k < seq.size(); k++) { if (k > 0) sb.append(' '); sb.append(seq.get(k)); }
                    return sb.toString();
                }
            }
        }
        return "NONE";
    }
''',
    examples=[("Example 1", "1235813\n"), ("Example 2", "1234\n")],
    hidden=[
        ("Zeros", "000\n"),
        ("A leading zero is not allowed", "0123\n"),
        ("Two digits only", "11\n"),
        ("Long", "11235813213455891442333776109871597258441816765\n"),
        ("Overflow", "214748364721474836424294967289\n"),
        ("Wider first numbers", "123456579\n"),
    ],
    expl=["1, 2, 3, 5, 8, 13.", "No choice of the first two numbers makes the rest follow."],
    prereqs=[
        ("backtracking", "Two real choices; the rest is forced verification."),
        ("overflow", "Every number must fit in a signed 32-bit int — compare in long."),
    ],
)


def _gene_case(seed, k, L=6):
    rng = _Lcg(seed)
    alpha = "ACGT"
    words = ["".join(alpha[rng.randint(0, 3)] for _ in range(L)) for _ in range(k)]
    start = "".join(alpha[rng.randint(0, 3)] for _ in range(L))
    end = words[rng.randint(0, k - 1)]
    return f"{start} {end} {k} " + " ".join(words) + "\n"


_p(
    "gene-mutation-steps", "Mutate One Letter at a Time", "Medium",
    topics=["Graph", "Breadth-First Search", "String"], subtopics=["Breadth-First Search", "Implicit Graph"],
    companies=["Google", "Amazon"],
    shape="str2_list", ret="int",
    todo="BFS from start; neighbours are bank strings differing in exactly one position; stop at end",
    description=(
        "A gene is a string over `A C G T`. One **mutation** changes exactly one letter, and every "
        "gene after a mutation must be in the bank. Print the fewest mutations from `start` to "
        "`end`, or `-1`. (`start` need not be in the bank; `end` must be reached through it.)\n\n"
        "### Input\n`start end k` followed by the `k` bank genes, all of equal length.\n\n"
        "### Output\nThe fewest mutations, or `-1`."
    ),
    constraints="1 ≤ length ≤ 10\n0 ≤ k ≤ 2000",
    hints=[
        "Genes are vertices; one mutation is an edge. Every edge costs one: BFS.",
        "Neighbours: for each position try the other three letters and keep the results that are in the bank — 3L candidates, not k comparisons.",
        "Mark bank genes as visited when enqueued; if start == end the answer is 0.",
    ],
    opt=("O(k · L · 3)", "O(k · L)", "Each bank gene is enqueued once and generates 3L candidates."),
    editorial=(
        "## The one thing this teaches\n**Generate neighbours by rule and check membership** "
        "rather than comparing every pair — the word-ladder trick at small scale.\n\n"
        "## Approach\n```java\nSet<String> bank = new HashSet<>(Arrays.asList(words));\nqueue = [start]; dist = 0\n"
        "while queue not empty: for each gene in this layer:\n    if gene == end return dist\n"
        "    for each position p, each letter c != gene[p]:\n        next = gene with c at p; if bank.remove(next): enqueue\n    dist++\nreturn -1\n```"
    ),
    py='''
def solve(s, t, words):
    bank = set(words)
    if s == t:
        return 0
    q, steps = deque([s]), 0
    while q:
        steps += 1
        for _ in range(len(q)):
            g = q.popleft()
            for p in range(len(g)):
                for c in "ACGT":
                    if c == g[p]:
                        continue
                    nxt = g[:p] + c + g[p + 1:]
                    if nxt in bank:
                        if nxt == t:
                            return steps
                        bank.discard(nxt)
                        q.append(nxt)
    return -1
''',
    java='''
    static int solve(String s, String t, String[] words) {
        Set<String> bank = new HashSet<>(Arrays.asList(words));
        if (s.equals(t)) return 0;
        ArrayDeque<String> q = new ArrayDeque<>();
        q.add(s);
        int steps = 0;
        char[] al = {'A', 'C', 'G', 'T'};
        while (!q.isEmpty()) {
            steps++;
            for (int size = q.size(); size-- > 0; ) {
                char[] g = q.poll().toCharArray();
                for (int p = 0; p < g.length; p++) {
                    char orig = g[p];
                    for (char c : al) {
                        if (c == orig) continue;
                        g[p] = c;
                        String nxt = new String(g);
                        if (bank.contains(nxt)) {
                            if (nxt.equals(t)) return steps;
                            bank.remove(nxt);
                            q.add(nxt);
                        }
                    }
                    g[p] = orig;
                }
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "CATG GCTA 5 CATA CTTA GTTA GCTA GGGG\n"),
        ("Example 2", "AAAA CCCC 2 AAAC CCCC\n"),
    ],
    hidden=[
        ("Already there", "ACGT ACGT 1 TTTT\n"),
        ("One step", "ACGT ACGA 1 ACGA\n"),
        ("End not in bank", "AAAA AAAC 1 AAAG\n"),
        ("Empty bank", "AAAA AAAC 0\n"),
        ("Random", _gene_case(521, 400)),
        ("Large", _gene_case(522, 2000, 8)),
    ],
    expl=["AACCGGTT → AACCGGTA → AAACGGTA: two mutations.", "AAAC → CCCC changes three letters at once; no route."],
    prereqs=[
        ("bfs", "Breadth-first search over an implicit graph of strings."),
        ("hashing", "The bank as a HashSet: membership in O(L)."),
    ],
)


def _slash_case(n, seed):
    rng = _Lcg(seed)
    rows = ["".join(".\\/"[rng.randint(0, 2)] for _ in range(n)) for _ in range(n)]
    return f"{n} {n}\n" + "\n".join(rows) + "\n"


_p(
    "regions-by-slashes", "Slashed Tiles", "Medium",
    topics=["Union Find", "Matrix"], subtopics=["Union Find", "Grid", "Modelling"],
    companies=["Google", "Amazon"],
    shape="grid", ret="int",
    todo="split every cell into 4 triangles (top, right, bottom, left); join them by the cell's character and to neighbouring cells; count components",
    description=(
        "An `n × n` floor of square tiles; each tile is blank (`.`), or split by a diagonal wall "
        "`/` or `\\`. Walls divide the floor into regions. Count the regions.\n\n"
        "### Input\nLine 1: `n n`.\nNext `n` lines: `n` characters each from `.`, `/`, `\\`.\n\n"
        "### Output\nThe number of regions."
    ),
    constraints="1 ≤ n ≤ 30",
    hints=[
        "A cell is not the unit of connectivity — a slash cuts it in two. Split each cell into four triangles: top, right, bottom, left.",
        "`.` joins all four; `/` joins top–left and bottom–right; `\\` joins top–right and bottom–left.",
        "Across cell borders, a cell's bottom touches the next row's top, and its right touches the next column's left — always. Then count union-find components.",
    ],
    opt=("O(n² · α(n²))", "O(n²)", "4n² elements, a constant number of unions each."),
    editorial=(
        "## The one thing this teaches\n**Choose the vertices so the edges become obvious.** The "
        "hard part is the modelling: once each tile is four triangles, the rules are a handful of "
        "unions and the answer is a component count.\n\n"
        "## Approach\n```java\nint id(int r, int c, int k) { return 4 * (r * n + c) + k; }   // k: 0 top, 1 right, 2 bottom, 3 left\n"
        "for each cell:\n    if '.'  union 0-1, 1-2, 2-3\n    if '/'  union 0-3, 1-2\n    if '\\\\' union 0-1, 2-3\n"
        "    if r + 1 < n  union(id(r,c,2), id(r+1,c,0))\n    if c + 1 < n  union(id(r,c,1), id(r,c+1,3))\n"
        "answer = number of components\n```"
    ),
    py='''
def solve(g):
    n = len(g)
    parent = list(range(4 * n * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = [4 * n * n]

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[a] = b
            comps[0] -= 1

    for r in range(n):
        for c in range(n):
            b = 4 * (r * n + c)
            ch = g[r][c]
            if ch == ".":
                union(b, b + 1); union(b + 1, b + 2); union(b + 2, b + 3)
            elif ch == "/":
                union(b, b + 3); union(b + 1, b + 2)
            else:
                union(b, b + 1); union(b + 2, b + 3)
            if r + 1 < n:
                union(b + 2, 4 * ((r + 1) * n + c))
            if c + 1 < n:
                union(b + 1, 4 * (r * n + c + 1) + 3)
    return comps[0]
''',
    java='''
    static int[] parent;
    static int comps;

    static int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }

    static void union(int a, int b) {
        a = find(a); b = find(b);
        if (a != b) { parent[a] = b; comps--; }
    }

    static int solve(char[][] g) {
        int n = g.length;
        parent = new int[4 * n * n];
        for (int i = 0; i < parent.length; i++) parent[i] = i;
        comps = 4 * n * n;
        for (int r = 0; r < n; r++)
            for (int c = 0; c < n; c++) {
                int b = 4 * (r * n + c);
                char ch = g[r][c];
                if (ch == '.') { union(b, b + 1); union(b + 1, b + 2); union(b + 2, b + 3); }
                else if (ch == '/') { union(b, b + 3); union(b + 1, b + 2); }
                else { union(b, b + 1); union(b + 2, b + 3); }
                if (r + 1 < n) union(b + 2, 4 * ((r + 1) * n + c));
                if (c + 1 < n) union(b + 1, 4 * (r * n + c + 1) + 3);
            }
        return comps;
    }
''',
    examples=[("Example 1", "3 3\n/./\n./.\n/./\n"), ("Example 2", "2 2\n./\n..\n")],
    hidden=[
        ("One blank tile", "1 1\n.\n"),
        ("One slash", "1 1\n/\n"),
        ("A diamond of slashes", "3 3\n./\\\n/.\\\n\\./\n"),
        ("All blank", "4 4\n....\n....\n....\n....\n"),
        ("Random", _slash_case(12, 531)),
        ("Large", _slash_case(30, 532)),
    ],
    expl=["The three slashes on the anti-diagonal split the floor in two, and the slashes in the top-left and bottom-right tiles each cut off a corner triangle: 4 regions.", "One slash in a corner does not close anything off: 1 region."],
    prereqs=[
        ("union_find", "Components counted by successful unions."),
        ("grid", "Cell (r, c) and its right and bottom neighbours."),
    ],
)


_p(
    "portal-maze", "The Maze With Doors Between Doors", "Medium",
    topics=["Graph", "Breadth-First Search", "Matrix"], subtopics=["Grid BFS", "Teleport Edges"],
    companies=["Google", "Uber"],
    shape="grid", ret="int",
    todo="BFS over cells; from a lowercase letter you may also step to the other cell with the same letter (one move)",
    description=(
        "A maze has `S` (start), `T` (target), `#` walls and `.` floor. Some floor cells carry a "
        "lowercase letter; each letter appears **exactly twice**, marking a pair of portals. Each "
        "move goes to an adjacent open cell, or — from a portal — to its twin. Every move takes one "
        "second. Print the fewest seconds from `S` to `T`, or `-1`.\n\n"
        "### Input\nLine 1: `r c`.\nNext `r` lines: the maze.\n\n### Output\nThe fewest moves, or `-1`."
    ),
    constraints="1 ≤ r, c ≤ 200",
    hints=[
        "Every move costs one, so BFS still works; the portal is just one more neighbour.",
        "Precompute each letter's two positions so the twin is an O(1) lookup.",
        "Walking onto a portal does not force you through it — the twin is an option, not a rule.",
    ],
    opt=("O(r · c)", "O(r · c)", "Each cell is enqueued once and has at most five neighbours."),
    editorial=(
        "## The one thing this teaches\n**An extra edge type is still just an edge.** BFS does not "
        "care whether a neighbour is adjacent in space; a portal adds one more unit-cost edge and "
        "the algorithm is unchanged.\n\n"
        "## Approach\n```java\nfor each popped (i, j):\n    for each of the 4 neighbours: usual BFS step\n"
        "    if g[i][j] is a letter: twin = other[letter] of (i, j); usual BFS step to twin\n```"
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    where = defaultdict(list)
    for i in range(r):
        for j in range(c):
            ch = g[i][j]
            if ch == "S":
                s = (i, j)
            elif "a" <= ch <= "z":
                where[ch].append((i, j))
    dist = [[-1] * c for _ in range(r)]
    dist[s[0]][s[1]] = 0
    q = deque([s])
    while q:
        i, j = q.popleft()
        if g[i][j] == "T":
            return dist[i][j]
        nbrs = [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
        if "a" <= g[i][j] <= "z":
            a, b = where[g[i][j]]
            nbrs.append(b if a == (i, j) else a)
        for x, y in nbrs:
            if 0 <= x < r and 0 <= y < c and g[x][y] != "#" and dist[x][y] < 0:
                dist[x][y] = dist[i][j] + 1
                q.append((x, y))
    return -1
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length;
        int[][] first = new int[26][], second = new int[26][];
        int si = 0, sj = 0;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                char ch = g[i][j];
                if (ch == 'S') { si = i; sj = j; }
                else if (ch >= 'a' && ch <= 'z') {
                    if (first[ch - 'a'] == null) first[ch - 'a'] = new int[]{i, j};
                    else second[ch - 'a'] = new int[]{i, j};
                }
            }
        int[][] dist = new int[r][c];
        for (int[] row : dist) Arrays.fill(row, -1);
        dist[si][sj] = 0;
        ArrayDeque<int[]> q = new ArrayDeque<>();
        q.add(new int[]{si, sj});
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!q.isEmpty()) {
            int[] p = q.poll();
            int i = p[0], j = p[1];
            if (g[i][j] == 'T') return dist[i][j];
            List<int[]> nb = new ArrayList<>();
            for (int[] d : dirs) nb.add(new int[]{i + d[0], j + d[1]});
            char ch = g[i][j];
            if (ch >= 'a' && ch <= 'z') {
                int[] a = first[ch - 'a'], b = second[ch - 'a'];
                nb.add(a[0] == i && a[1] == j ? b : a);
            }
            for (int[] x : nb) {
                if (x[0] < 0 || x[0] >= r || x[1] < 0 || x[1] >= c || g[x[0]][x[1]] == '#') continue;
                if (dist[x[0]][x[1]] >= 0) continue;
                dist[x[0]][x[1]] = dist[i][j] + 1;
                q.add(x);
            }
        }
        return -1;
    }
''',
    examples=[
        ("Example 1", "3 7\nS.a#...\n#####..\nT.b#.ab\n"),
        ("Example 2", "1 5\nS.#.T\n"),
    ],
    hidden=[
        ("Adjacent", "1 2\nST\n"),
        ("A portal right away", "3 3\nSa#\n###\n.aT\n"),
        ("A portal shortcut in a corridor", "1 6\nSa..aT\n"),
        ("A portal into a dead end", "3 5\nSa#.T\n..#..\n###a.\n"),
        ("Walled off", "3 3\nS#.\n###\n.#T\n"),
        ("Big open field", "200 200\n" + "\n".join(("S" if i == 0 else ".") + "." * 198 + ("T" if i == 199 else ".") for i in range(200)) + "\n"),
    ],
    expl=["S → . → a (2 moves), through the portal to the other a (3), onto b (4), through to the other b (5), then two steps left to T: 7.", "The wall splits the corridor and there are no portals."],
    prereqs=[
        ("bfs", "Breadth-first search with one extra kind of edge."),
        ("grid", "Four-neighbour moves with bounds checks."),
    ],
)
