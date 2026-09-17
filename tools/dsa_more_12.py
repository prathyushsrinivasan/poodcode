# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 12 — backtracking, tries, and DP extra practice.
#
#   matchsticks-to-square          fill four sides; sort descending so failures come early
#   partition-k-equal-subsets      the same search with k buckets and symmetry pruning
#   beautiful-arrangement          place positions from the most constrained end
#   unique-permutations-count      sort, and skip a value equal to an unused earlier twin
#   map-sum-pairs                  a trie whose nodes store the sum below them
#   longest-palindromic-subseq     interval DP: match the ends or drop one
#   maximal-square                 a cell's square is limited by its three neighbours
#   unique-paths-obstacles         grid path counting where a blocked cell contributes zero
#   stock-with-cooldown            a DP over three states per day
#   number-of-lis                  carry a count alongside each LIS length
# ===========================================================================

_p(
    "matchsticks-to-square", "Matchsticks to Square", "Medium",
    topics=["Recursion & DP"], subtopics=["Backtracking", "Pruning"], companies=["Microsoft", "Rackspace"],
    shape="arr", ret="String", todo="backtrack each stick into one of four sides of length total/4; sort descending and prune",
    description=(
        "Use **every** matchstick exactly once, without breaking any, to form a square. Is it "
        "possible?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` stick lengths.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 15\n1 ≤ length ≤ 10^8",
    hints=[
        "The total must be divisible by 4, and no stick may exceed a side. Check those first.",
        "Assign sticks one at a time to one of four sides, never letting a side exceed total / 4.",
        "Sort descending so long sticks fail fast, and skip a side whose current length equals a side already tried for this stick.",
    ],
    opt=("O(4ⁿ)", "O(n)", "At most four choices per stick; the pruning removes most branches in practice."),
    editorial=(
        "## The one thing this teaches\n**Backtracking lives or dies by its pruning.** The raw "
        "search is 4¹⁵ ≈ 10⁹ assignments. Three cheap rules cut it to almost nothing: reject early "
        "on arithmetic, place the largest sticks first, and never try two sides that are "
        "currently the same length.\n\n"
        "## Approach\n```java\nboolean place(int i) {\n    if (i == n) return true;          // every stick placed, all sides ≤ target, total fits\n"
        "    for (int s = 0; s < 4; s++) {\n"
        "        if (side[s] + a[i] > target) continue;\n"
        "        if (s > 0 && side[s] == side[s - 1]) continue;   // same state as the side before\n"
        "        side[s] += a[i];\n        if (place(i + 1)) return true;\n        side[s] -= a[i];\n    }\n    return false;\n}\n```\n\n"
        "## Why equal sides can be skipped\nPutting the stick on either of two equally long sides "
        "leads to identical subproblems with the sides relabelled. Trying both doubles the work "
        "for nothing — and at the first stick all four sides are 0, so this alone divides the "
        "search by 24.\n\n"
        "## Why descending\nA long stick has few legal sides, so it fails in the first few levels "
        "instead of after the short sticks have filled the tree."
    ),
    py='''
def solve(a):
    total = sum(a)
    if total % 4:
        return "NO"
    target = total // 4
    a = sorted(a, reverse=True)
    if a[0] > target:
        return "NO"
    side = [0] * 4

    def place(i):
        if i == len(a):
            return True
        for s in range(4):
            if side[s] + a[i] > target:
                continue
            if s > 0 and side[s] == side[s - 1]:
                continue
            side[s] += a[i]
            if place(i + 1):
                return True
            side[s] -= a[i]
        return False

    return "YES" if place(0) else "NO"
''',
    java='''
    static long[] side = new long[4];
    static long target;
    static Integer[] sticks;

    static boolean place(int i) {
        if (i == sticks.length) return true;
        for (int s = 0; s < 4; s++) {
            if (side[s] + sticks[i] > target) continue;
            if (s > 0 && side[s] == side[s - 1]) continue;
            side[s] += sticks[i];
            if (place(i + 1)) return true;
            side[s] -= sticks[i];
        }
        return false;
    }

    static String solve(int[] a) {
        long total = 0;
        for (int x : a) total += x;
        if (total % 4 != 0) return "NO";
        target = total / 4;
        sticks = new Integer[a.length];
        for (int i = 0; i < a.length; i++) sticks[i] = a[i];
        Arrays.sort(sticks, Collections.reverseOrder());
        if (sticks[0] > target) return "NO";
        return place(0) ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "5\n1 1 2 2 2\n"), ("Example 2", "5\n3 3 3 3 4\n")],
    hidden=[
        ("Four equal sticks", "4\n1 1 1 1\n"),
        ("A stick longer than a side", "6\n2 2 2 2 2 6\n"),
        ("Pairs make sides", "8\n5 5 5 5 4 4 4 4\n"),
        ("Twos cannot complete the threes", "6\n3 3 3 3 2 2\n"),
    ],
    expl=[
        "Sides of 2: `2`, `2`, `2`, `1+1`.",
        "The total, 16, splits into sides of 4, but no 3 can pair with anything to make 4.",
    ],
    prereqs=[
        ("backtracking", "Placing each stick on a side, undoing the choice when it leads nowhere."),
        ("pruning", "Sorting descending and skipping equal sides removes symmetric branches."),
    ],
)

_p(
    "partition-k-equal-subsets", "Partition to K Equal Sum Subsets", "Medium",
    topics=["Recursion & DP"], subtopics=["Backtracking", "Pruning"], companies=["LinkedIn", "Amazon"],
    shape="arr_k", ret="String", todo="backtrack each number into one of k buckets of size total/k, with the same pruning as matchsticks",
    description=(
        "Can the array be divided into `k` non-empty groups with **equal sums**? Every element "
        "must be used.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` positive integers.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ k ≤ n ≤ 16\n1 ≤ a[i] ≤ 10^4",
    hints=[
        "This is Matchsticks to Square with k sides instead of 4.",
        "Check total % k == 0 and max ≤ total / k before searching.",
        "Sort descending; skip a bucket equal to the previous bucket; if a number does not fit in an EMPTY bucket, it will not fit in any.",
    ],
    opt=("O(kⁿ)", "O(n)", "Exponential in the worst case; the pruning rules make it fast for n ≤ 16."),
    editorial=(
        "## The one thing this teaches\n**A search you have written once generalises.** The "
        "matchsticks search places items into four equal bins; this is k bins. The pruning rules "
        "carry over unchanged, and one more becomes available: if an item cannot start a fresh "
        "bucket, no later bucket will do better.\n\n"
        "## Approach\n```java\nboolean place(int i) {\n    if (i == n) return true;\n"
        "    for (int b = 0; b < k; b++) {\n"
        "        if (bucket[b] + a[i] > target) continue;\n"
        "        if (b > 0 && bucket[b] == bucket[b - 1]) continue;\n"
        "        bucket[b] += a[i];\n        if (place(i + 1)) return true;\n        bucket[b] -= a[i];\n"
        "        if (bucket[b] == 0) break;          // failed in an empty bucket: every empty bucket fails\n"
        "    }\n    return false;\n}\n```\n\n"
        "## The bitmask alternative\nDP over subsets: `dp[mask]` = the fill of the current bucket "
        "after using the elements in `mask`, reachable or not. O(n · 2ⁿ) time, guaranteed — "
        "worth reaching for when the pruned search has bad cases."
    ),
    py='''
def solve(a, k):
    total = sum(a)
    if total % k:
        return "NO"
    target = total // k
    a = sorted(a, reverse=True)
    if a[0] > target:
        return "NO"
    bucket = [0] * k

    def place(i):
        if i == len(a):
            return True
        for b in range(k):
            if bucket[b] + a[i] > target:
                continue
            if b > 0 and bucket[b] == bucket[b - 1]:
                continue
            bucket[b] += a[i]
            if place(i + 1):
                return True
            bucket[b] -= a[i]
            if bucket[b] == 0:
                break
        return False

    return "YES" if place(0) else "NO"
''',
    java='''
    static int[] nums;
    static long[] bucket;
    static long target;

    static boolean place(int i) {
        if (i == nums.length) return true;
        for (int b = 0; b < bucket.length; b++) {
            if (bucket[b] + nums[i] > target) continue;
            if (b > 0 && bucket[b] == bucket[b - 1]) continue;
            bucket[b] += nums[i];
            if (place(i + 1)) return true;
            bucket[b] -= nums[i];
            if (bucket[b] == 0) break;
        }
        return false;
    }

    static String solve(int[] a, long k) {
        long total = 0;
        for (int x : a) total += x;
        if (total % k != 0) return "NO";
        target = total / k;
        nums = a.clone();
        Arrays.sort(nums);
        for (int i = 0, j = nums.length - 1; i < j; i++, j--) { int t = nums[i]; nums[i] = nums[j]; nums[j] = t; }
        if (nums[0] > target) return "NO";
        bucket = new long[(int) k];
        return place(0) ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "7 4\n4 3 2 3 5 2 1\n"), ("Example 2", "4 3\n1 2 3 4\n")],
    hidden=[
        ("One group", "1 1\n5\n"),
        ("Total not divisible", "6 4\n2 2 2 2 3 3\n"),
        ("One big, many small", "6 2\n1 1 1 1 1 5\n"),
        ("Big and small together", "4 2\n2 2 2 6\n"),
        ("No subset reaches the target", "4 2\n3 3 3 1\n"),
    ],
    expl=[
        "`[5]`, `[1,4]`, `[2,3]`, `[2,3]` all sum to 5.",
        "The total, 10, is not divisible by 3.",
    ],
    prereqs=[
        ("backtracking", "Assigning each number to one of k buckets and undoing on failure."),
        ("pruning", "Skipping equal buckets and stopping after a failure in an empty bucket."),
    ],
)

_p(
    "beautiful-arrangement", "Beautiful Arrangement", "Medium",
    topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Google"],
    shape="n", ret="long", todo="fill positions n down to 1, trying each unused number that divides or is divided by the position",
    description=(
        "A permutation `p` of `1..n` is **beautiful** if for every position `i` (1-indexed), "
        "`p[i]` is divisible by `i` or `i` is divisible by `p[i]`. How many beautiful "
        "permutations are there?\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe count."
    ),
    constraints="1 ≤ n ≤ 15",
    hints=[
        "Generating all n! permutations and checking them is 1.3·10¹² at n = 15.",
        "Build the permutation position by position, and only place a number that is legal at that position.",
        "Fill from position n down to 1: large positions accept few numbers, so the tree narrows at the top.",
    ],
    opt=("O(k)", "O(n)", "k is the number of legal partial arrangements, far below n!; a bitmask DP gives O(n · 2ⁿ)."),
    editorial=(
        "## The one thing this teaches\n**Check constraints as you build, and build the most "
        "constrained part first.** Validating whole permutations wastes all the work before the "
        "first bad position. Checking at each placement cuts the branch immediately — and "
        "starting from the positions with the fewest legal numbers keeps the tree thin near the "
        "root, where cuts save the most.\n\n"
        "## Approach\n```java\nint count(int pos) {                 // fill positions n..1\n"
        "    if (pos == 0) return 1;\n    int total = 0;\n"
        "    for (int v = 1; v <= n; v++)\n"
        "        if (!used[v] && (v % pos == 0 || pos % v == 0)) {\n"
        "            used[v] = true;\n            total += count(pos - 1);\n            used[v] = false;\n        }\n"
        "    return total;\n}\n```\n\n"
        "## Why from the top\nPosition 1 accepts every number; position 13 accepts only 1 and 13. "
        "Deciding position 1 first gives n branches that all survive to deep levels. Deciding "
        "position 13 first gives 2."
    ),
    py='''
def solve(n):
    used = [False] * (n + 1)

    def count(pos):
        if pos == 0:
            return 1
        total = 0
        for v in range(1, n + 1):
            if not used[v] and (v % pos == 0 or pos % v == 0):
                used[v] = True
                total += count(pos - 1)
                used[v] = False
        return total

    return count(n)
''',
    java='''
    static boolean[] used;
    static int N;

    static long count(int pos) {
        if (pos == 0) return 1;
        long total = 0;
        for (int v = 1; v <= N; v++)
            if (!used[v] && (v % pos == 0 || pos % v == 0)) {
                used[v] = true;
                total += count(pos - 1);
                used[v] = false;
            }
        return total;
    }

    static long solve(long n) {
        N = (int) n;
        used = new boolean[N + 1];
        return count(N);
    }
''',
    examples=[("Example 1", "2\n"), ("Example 2", "1\n")],
    hidden=[
        ("Three", "3\n"),
        ("Six", "6\n"),
        ("Ten", "10\n"),
        ("Twelve", "12\n"),
    ],
    expl=[
        "`[1, 2]` and `[2, 1]` both work.",
        "`[1]`.",
    ],
    prereqs=[
        ("backtracking", "Building the permutation one position at a time with a used-array."),
        ("pruning", "Only numbers legal at the position are tried, starting from the most constrained positions."),
    ],
)

_p(
    "unique-permutations-count", "Unique Permutations", "Medium",
    topics=["Recursion & DP"], subtopics=["Backtracking"], companies=["Microsoft", "LinkedIn"],
    shape="arr", ret="long", todo="sort; at each position skip a value equal to the previous one if that twin is unused",
    description=(
        "The array may contain duplicates. Count its **distinct** permutations by generating them "
        "with backtracking, never producing the same permutation twice.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe number of distinct permutations."
    ),
    constraints="1 ≤ n ≤ 8\n-10 ≤ a[i] ≤ 10",
    hints=[
        "Generating all n! and deduplicating with a set works, but produces every duplicate first.",
        "Sort, so equal values are adjacent. Treat equal values as if they must be used left to right.",
        "At a position, skip a[i] when a[i] == a[i − 1] and a[i − 1] is not currently used.",
    ],
    opt=("O(n · P)", "O(n)", "P is the number of distinct permutations; each is built in O(n) with no duplicate branches."),
    editorial=(
        "## The one thing this teaches\n**Deduplicate the search, not the output.** Collecting "
        "results in a set generates every duplicate and throws it away. Imposing an order on equal "
        "values — the first copy must be placed before the second — makes each distinct "
        "permutation reachable by exactly one branch.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong count(int depth) {\n    if (depth == n) return 1;\n    long total = 0;\n"
        "    for (int i = 0; i < n; i++) {\n        if (used[i]) continue;\n"
        "        if (i > 0 && a[i] == a[i - 1] && !used[i - 1]) continue;   // twin not placed yet\n"
        "        used[i] = true;\n        total += count(depth + 1);\n        used[i] = false;\n    }\n    return total;\n}\n```\n\n"
        "## Reading the skip rule\n`!used[i − 1]` means the earlier copy is still available, so "
        "choosing this later copy now would create a permutation that the branch choosing the "
        "earlier copy also creates. Forcing copies to be used in index order leaves one branch "
        "per distinct arrangement.\n\n"
        "The count equals n! / (c₁! c₂! …) for value multiplicities cᵢ — a good check, not the "
        "exercise."
    ),
    py='''
def solve(a):
    a = sorted(a)
    n = len(a)
    used = [False] * n

    def count(depth):
        if depth == n:
            return 1
        total = 0
        for i in range(n):
            if used[i]:
                continue
            if i > 0 and a[i] == a[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            total += count(depth + 1)
            used[i] = False
        return total

    return count(0)
''',
    java='''
    static int[] vals;
    static boolean[] taken;

    static long count(int depth) {
        if (depth == vals.length) return 1;
        long total = 0;
        for (int i = 0; i < vals.length; i++) {
            if (taken[i]) continue;
            if (i > 0 && vals[i] == vals[i - 1] && !taken[i - 1]) continue;
            taken[i] = true;
            total += count(depth + 1);
            taken[i] = false;
        }
        return total;
    }

    static long solve(int[] a) {
        vals = a.clone();
        Arrays.sort(vals);
        taken = new boolean[vals.length];
        return count(0);
    }
''',
    examples=[("Example 1", "3\n1 1 2\n"), ("Example 2", "3\n1 2 3\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All equal", "4\n2 2 2 2\n"),
        ("Three pairs", "6\n1 1 2 2 3 3\n"),
        ("All distinct, eight", "8\n1 2 3 4 5 6 7 8\n"),
    ],
    expl=[
        "`112`, `121`, `211`.",
        "All 3! orders are distinct.",
    ],
    prereqs=[
        ("backtracking", "Permutations built with a used-array, one position at a time."),
        ("sorting", "Sorting puts equal values side by side, which the skip rule relies on."),
    ],
)

_p(
    "map-sum-pairs", "Map Sum Pairs", "Medium",
    topics=["Data Structures", "Strings"], subtopics=["Trie", "Hashing"], companies=["Akuna Capital"],
    shape="ops", ret="String", todo="a trie whose nodes store the total value of keys below; insert adds the change in value along the path",
    description=(
        "Support two operations:\n\n"
        "- `insert key val` — set the value of `key` (replacing any earlier value).\n"
        "- `sum prefix` — print the total value of all keys that start with `prefix`.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: operations.\n\n### Output\nOne line per `sum`."
    ),
    constraints="1 ≤ q ≤ 50\n1 ≤ |key|, |prefix| ≤ 50, lowercase letters\n1 ≤ val ≤ 1000",
    hints=[
        "Scanning every key on each `sum` works for 50 operations but not in general.",
        "In a trie, every key with a given prefix lies under that prefix's node. Store at each node the total below it.",
        "On insert, add (new value − old value) along the path — overwriting a key must not double-count.",
    ],
    opt=("O(L) per operation", "O(total key length)", "Each operation walks one path of at most L characters."),
    editorial=(
        "## The one thing this teaches\n**Store the answer in the structure.** A trie groups keys by "
        "prefix; if each node also stores the sum of the values in its subtree, `sum(prefix)` is "
        "a walk to one node and a read — no traversal of the subtree.\n\n"
        "## Approach\n```java\nMap<String, Integer> value = new HashMap<>();\nNode root = new Node();   // node.sum, node.next[26]\n\n"
        "void insert(String key, int val) {\n"
        "    int delta = val - value.getOrDefault(key, 0);\n    value.put(key, val);\n"
        "    Node cur = root;\n    for (char c : key.toCharArray()) {\n"
        "        if (cur.next[c - 'a'] == null) cur.next[c - 'a'] = new Node();\n"
        "        cur = cur.next[c - 'a'];\n        cur.sum += delta;\n    }\n}\n"
        "int sum(String prefix) {\n    Node cur = root;\n"
        "    for (char c : prefix.toCharArray()) { cur = cur.next[c - 'a']; if (cur == null) return 0; }\n"
        "    return cur.sum;\n}\n```\n\n"
        "## The overwrite\nInserting `apple` with 3 and then 2 must leave 2, not 5. Adding the "
        "*difference* to every node on the path keeps all the stored sums correct, which is why "
        "the plain map of current values is needed alongside the trie."
    ),
    py='''
def solve(ops):
    value = {}
    root = {"sum": 0}
    out = []
    for op in ops:
        if op[0] == "insert":
            key, val = op[1], int(op[2])
            delta = val - value.get(key, 0)
            value[key] = val
            cur = root
            for ch in key:
                cur = cur.setdefault(ch, {"sum": 0})
                cur["sum"] += delta
        else:
            cur = root
            for ch in op[1]:
                cur = cur.get(ch)
                if cur is None:
                    break
            out.append(str(cur["sum"] if cur else 0))
    return "\\n".join(out)
''',
    java='''
    static class Node {
        long sum;
        Node[] next = new Node[26];
    }

    static String solve(String[][] ops) {
        Map<String, Integer> value = new HashMap<>();
        Node root = new Node();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("insert")) {
                String key = op[1];
                int val = Integer.parseInt(op[2]);
                int delta = val - value.getOrDefault(key, 0);
                value.put(key, val);
                Node cur = root;
                for (int i = 0; i < key.length(); i++) {
                    int c = key.charAt(i) - 'a';
                    if (cur.next[c] == null) cur.next[c] = new Node();
                    cur = cur.next[c];
                    cur.sum += delta;
                }
            } else {
                Node cur = root;
                String p = op[1];
                for (int i = 0; i < p.length() && cur != null; i++) cur = cur.next[p.charAt(i) - 'a'];
                if (sb.length() > 0) sb.append('\\n');
                sb.append(cur == null ? 0 : cur.sum);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4\ninsert apple 3\nsum ap\ninsert app 2\nsum ap\n"),
        ("Example 2", "5\ninsert apple 3\ninsert apple 2\nsum ap\nsum apple\nsum b\n"),
    ],
    hidden=[
        ("Prefix is itself a key", "3\ninsert a 1\ninsert ab 2\nsum a\n"),
        ("Prefix longer than any key", "2\ninsert abc 5\nsum abcd\n"),
        ("Overwrite in the middle of a path", "6\ninsert x 1\ninsert xy 2\ninsert xyz 3\nsum xy\ninsert xy 10\nsum x\n"),
    ],
    expl=[
        "First only `apple` (3); then `app` adds 2.",
        "The second insert replaces 3 with 2. No key starts with `b`.",
    ],
    prereqs=[
        ("trie", "Keys sharing a prefix share a trie path, and every node can store an aggregate of its subtree."),
        ("hashing", "A map of current values, so an overwrite adds only the change."),
    ],
)

_p(
    "longest-palindromic-subseq", "Longest Palindromic Subsequence", "Medium",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP"], companies=["Amazon", "Uber"],
    shape="str", ret="int", todo="dp[i][j] over substrings: equal ends add 2 to dp[i+1][j−1], else max of dropping either end",
    description=(
        "Find the length of the longest **subsequence** of `s` that is a palindrome.\n\n"
        "### Input\nOne line: `s`.\n\n### Output\nThe length."
    ),
    constraints="1 ≤ |s| ≤ 1000\ns consists of lowercase English letters.",
    hints=[
        "Unlike a substring, a subsequence may skip characters.",
        "For s[i..j]: if s[i] == s[j], both ends can wrap the best inside: dp[i+1][j−1] + 2. Otherwise drop one end.",
        "Fill by increasing length, or by i from the end. Equivalently: the LCS of s and reversed s.",
    ],
    opt=("O(n²)", "O(n)", "n² intervals, O(1) each; one row of state if filled carefully."),
    editorial=(
        "## The one thing this teaches\n**Interval DP.** The state is a substring `s[i..j]`, and "
        "each state depends on strictly shorter substrings, so filling by length (or `i` from the "
        "right, `j` from the left) always has the answers it needs.\n\n"
        "## Approach\n```java\nint[][] dp = new int[n][n];\nfor (int i = n - 1; i >= 0; i--) {\n    dp[i][i] = 1;\n"
        "    for (int j = i + 1; j < n; j++)\n"
        "        dp[i][j] = s.charAt(i) == s.charAt(j)\n"
        "                 ? dp[i + 1][j - 1] + 2\n                 : Math.max(dp[i + 1][j], dp[i][j - 1]);\n}\nreturn dp[0][n - 1];\n```\n\n"
        "## Why matching the ends is always safe\nIf `s[i] == s[j]`, some optimal palindrome uses "
        "both: take any optimal palindrome inside and wrap it — it is never worse than one that "
        "uses only one of the two ends.\n\n"
        "## The LCS view\nA palindromic subsequence reads the same forwards and backwards, so it "
        "is a common subsequence of `s` and `reverse(s)` — and the longest common one is always a "
        "palindrome. Same O(n²), different derivation."
    ),
    py='''
def solve(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
''',
    java='''
    static int solve(String s) {
        int n = s.length();
        String t = new StringBuilder(s).reverse().toString();
        int[] prev = new int[n + 1], cur = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++)
                cur[j] = s.charAt(i - 1) == t.charAt(j - 1) ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]);
            int[] tmp = prev; prev = cur; cur = tmp;
        }
        return prev[n];
    }
''',
    examples=[("Example 1", "bbbab\n"), ("Example 2", "cbbd\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("All distinct", "abcde\n"),
        ("Skips needed", "agbdba\n"),
        ("All equal", "aaaa\n"),
    ],
    expl=[
        "`bbbb`.",
        "`bb`.",
    ],
    prereqs=[
        ("dp2d", "A table over substrings, filled so shorter intervals come first."),
        ("dp", "Choosing between matching both ends and dropping one of them."),
    ],
)

_p(
    "maximal-square", "Maximal Square", "Medium",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP", "Grid"], companies=["Meta", "Apple", "Airbnb"],
    shape="grid", ret="int", todo="side[i][j] = 1 + min(up, left, up-left) for a 1-cell; answer is the largest side squared",
    description=(
        "In a grid of `0`s and `1`s, find the **area** of the largest square containing only `1`s.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n### Output\nThe area."
    ),
    constraints="1 ≤ r, c ≤ 300",
    hints=[
        "Let side[i][j] be the largest all-1 square whose BOTTOM-RIGHT corner is (i, j).",
        "Such a square of side k needs squares of side k − 1 ending at the cell above, the cell to the left, and the cell up-left.",
        "So side[i][j] = 1 + min(side[i−1][j], side[i][j−1], side[i−1][j−1]) when the cell is 1, else 0.",
    ],
    opt=("O(r·c)", "O(c)", "One pass; each cell reads three neighbours, all in the current or previous row."),
    editorial=(
        "## The one thing this teaches\n**Choose the state so that it composes.** \"Largest square "
        "anywhere\" does not combine from neighbours; \"largest square ending exactly here\" does, "
        "because a square at (i, j) is the union of three smaller squares at its up, left and "
        "diagonal neighbours plus the corner itself.\n\n"
        "## Approach\n```java\nint[][] side = new int[r + 1][c + 1];     // padded, so row/column 0 are zeros\nint best = 0;\n"
        "for (int i = 1; i <= r; i++)\n    for (int j = 1; j <= c; j++)\n"
        "        if (g[i - 1][j - 1] == '1') {\n"
        "            side[i][j] = 1 + Math.min(side[i - 1][j - 1], Math.min(side[i - 1][j], side[i][j - 1]));\n"
        "            best = Math.max(best, side[i][j]);\n        }\nreturn best * best;\n```\n\n"
        "## Why the minimum\nThe square can grow only as far as its weakest neighbour allows. If "
        "the cell above supports side 3 but the diagonal only 1, a side-3 square here would need a "
        "1-square at the diagonal of side 2 — which does not exist.\n\n"
        "## Area, not side\nThe answer is the *area*: square the side at the end."
    ),
    py='''
def solve(g):
    r, c = len(g), len(g[0])
    side = [[0] * (c + 1) for _ in range(r + 1)]
    best = 0
    for i in range(1, r + 1):
        for j in range(1, c + 1):
            if g[i - 1][j - 1] == "1":
                side[i][j] = 1 + min(side[i - 1][j], side[i][j - 1], side[i - 1][j - 1])
                best = max(best, side[i][j])
    return best * best
''',
    java='''
    static int solve(char[][] g) {
        int r = g.length, c = g[0].length, best = 0;
        int[][] side = new int[r + 1][c + 1];
        for (int i = 1; i <= r; i++)
            for (int j = 1; j <= c; j++)
                if (g[i - 1][j - 1] == '1') {
                    side[i][j] = 1 + Math.min(side[i - 1][j - 1], Math.min(side[i - 1][j], side[i][j - 1]));
                    best = Math.max(best, side[i][j]);
                }
        return best * best;
    }
''',
    examples=[("Example 1", "4 5\n10100\n10111\n11111\n10010\n"), ("Example 2", "2 2\n01\n10\n")],
    hidden=[
        ("No ones", "1 1\n0\n"),
        ("Full grid", "3 3\n111\n111\n111\n"),
        ("Offset square", "3 4\n0111\n0111\n0111\n"),
        ("Rectangle is not a square", "2 4\n1111\n1111\n"),
    ],
    expl=[
        "A 2×2 square of ones at rows 1–2, columns 2–3: area 4.",
        "No two adjacent ones: area 1.",
    ],
    prereqs=[
        ("dp2d", "The largest square ending at each cell, built from three neighbours."),
        ("grid", "A padded table so the first row and column need no special case."),
    ],
)

_p(
    "unique-paths-obstacles", "Unique Paths With Obstacles", "Medium",
    topics=["Dynamic Programming", "Matrix"], subtopics=["2D DP", "Grid"], companies=["Amazon", "Bloomberg"],
    shape="grid", ret="long", todo="ways[j] += ways[j − 1] per row; an obstacle cell sets ways[j] = 0",
    description=(
        "Move from the top-left to the bottom-right cell of a grid, only **right** or **down**. "
        "Cells marked `1` are obstacles. Count the paths modulo `10^9 + 7`.\n\n"
        "### Input\n- Line 1: `r c`.\n- Next `r` lines: a row of `0`s and `1`s.\n\n"
        "### Output\nThe number of paths, mod `10^9 + 7`."
    ),
    constraints="1 ≤ r, c ≤ 100",
    hints=[
        "Without obstacles, paths(i, j) = paths(i − 1, j) + paths(i, j − 1).",
        "An obstacle has 0 paths through it — and that zero flows into every cell after it.",
        "If the start or the end is an obstacle, the answer is 0. One row of state is enough.",
    ],
    opt=("O(r·c)", "O(c)", "One pass over the grid with a rolling row."),
    editorial=(
        "## The one thing this teaches\n**An obstacle is a zero in the recurrence.** The unobstructed "
        "counting DP needs no special logic for blocked cells: set their count to 0 and the "
        "addition does the rest, including blocking everything that could only be reached "
        "through them.\n\n"
        "## Approach\n```java\nlong[] ways = new long[c];\nways[0] = g[0][0] == '0' ? 1 : 0;\n"
        "for (int i = 0; i < r; i++)\n    for (int j = 0; j < c; j++) {\n"
        "        if (g[i][j] == '1') ways[j] = 0;\n"
        "        else if (j > 0) ways[j] = (ways[j] + ways[j - 1]) % MOD;   // above + left\n    }\nreturn ways[c - 1];\n```\n\n"
        "## The first row and column\nIn the unobstructed version they are all 1s. With obstacles, "
        "everything *after* a blocked cell in the first row is 0 — which the rolling update "
        "produces automatically, and which a hard-coded \"first row = 1\" gets wrong."
    ),
    py='''
def solve(g):
    MOD = 10 ** 9 + 7
    r, c = len(g), len(g[0])
    ways = [0] * c
    ways[0] = 1 if g[0][0] == "0" else 0
    for i in range(r):
        for j in range(c):
            if g[i][j] == "1":
                ways[j] = 0
            elif j > 0:
                ways[j] = (ways[j] + ways[j - 1]) % MOD
    return ways[c - 1]
''',
    java='''
    static long solve(char[][] g) {
        final long MOD = 1_000_000_007L;
        int r = g.length, c = g[0].length;
        long[][] dp = new long[r][c];
        for (int i = 0; i < r; i++)
            for (int j = 0; j < c; j++) {
                if (g[i][j] == '1') { dp[i][j] = 0; continue; }
                if (i == 0 && j == 0) { dp[i][j] = 1; continue; }
                long up = i > 0 ? dp[i - 1][j] : 0, left = j > 0 ? dp[i][j - 1] : 0;
                dp[i][j] = (up + left) % MOD;
            }
        return dp[r - 1][c - 1];
    }
''',
    examples=[("Example 1", "3 3\n000\n010\n000\n"), ("Example 2", "2 2\n01\n00\n")],
    hidden=[
        ("Start blocked", "1 1\n1\n"),
        ("End blocked", "2 2\n00\n01\n"),
        ("No obstacles", "3 4\n0000\n0000\n0000\n"),
        ("Wall in a single row", "1 5\n00100\n"),
        ("Large grid needs the modulus", "30 30\n" + ("0" * 30 + "\n") * 30),
    ],
    expl=[
        "Around the centre obstacle either way: 2 paths.",
        "Only down, then right.",
    ],
    prereqs=[
        ("dp2d", "Path counts from the cell above and the cell to the left, with obstacles as zeros."),
        ("modulo", "Path counts grow like binomial coefficients and are reported modulo 1e9+7."),
    ],
)

_p(
    "stock-with-cooldown", "Best Time to Buy and Sell Stock with Cooldown", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP", "State Machine"], companies=["Google", "Amazon"],
    shape="arr", ret="long", todo="three states per day — holding, just sold, resting — each from yesterday's states",
    description=(
        "Trade a stock with daily prices as many times as you like, holding at most one share. "
        "After you **sell**, you cannot buy on the **next** day. Maximise the profit.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` prices.\n\n### Output\nThe maximum profit."
    ),
    constraints="1 ≤ n ≤ 5000\n0 ≤ price ≤ 1000",
    hints=[
        "Describe each day's end by what you are doing: holding a share, having just sold, or resting with no share.",
        "hold = max(hold, rest − price); sold = hold + price; rest = max(rest, sold).",
        "Use yesterday's values on the right-hand side — update into temporaries.",
    ],
    opt=("O(n)", "O(1)", "Three numbers updated per day."),
    editorial=(
        "## The one thing this teaches\n**A state machine is a DP.** When the rules are about what "
        "you may do *next* depending on what you did, name the situations as states and write "
        "each state's best value from the states that can lead into it.\n\n"
        "## The states\n- **hold** — own a share at day's end: kept yesterday's, or bought today "
        "from `rest` (not from `sold` — that is the cooldown).\n"
        "- **sold** — sold today: yesterday's `hold` plus today's price.\n"
        "- **rest** — no share and free to buy tomorrow: rested yesterday, or sold yesterday.\n\n"
        "## Approach\n```java\nlong hold = Long.MIN_VALUE / 2, sold = 0, rest = 0;\nfor (int p : prices) {\n"
        "    long h = Math.max(hold, rest - p), s = hold + p, r = Math.max(rest, sold);\n"
        "    hold = h; sold = s; rest = r;\n}\nreturn Math.max(sold, rest);\n```\n\n"
        "## Why temporaries\nAll three updates must read *yesterday's* values. Updating `hold` in "
        "place and then computing `sold` from it would let you buy and sell on the same day.\n\n"
        "The whole stock-problem family — one transaction, k transactions, fees — is this machine "
        "with different states."
    ),
    py='''
def solve(a):
    hold, sold, rest = float("-inf"), 0, 0
    for p in a:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)
''',
    java='''
    static long solve(int[] prices) {
        long hold = Long.MIN_VALUE / 2, sold = 0, rest = 0;
        for (int p : prices) {
            long h = Math.max(hold, rest - p), s = hold + p, r = Math.max(rest, sold);
            hold = h; sold = s; rest = r;
        }
        return Math.max(sold, rest);
    }
''',
    examples=[("Example 1", "5\n1 2 3 0 2\n"), ("Example 2", "1\n1\n")],
    hidden=[
        ("Falling prices", "3\n3 2 1\n"),
        ("Cooldown costs a trade", "4\n1 4 2 7\n"),
        ("Two separate climbs", "6\n1 2 4 1 7 8\n"),
    ],
    expl=[
        "Buy at 1, sell at 2, cool down, buy at 0, sell at 2: profit 3.",
        "One day: nothing to do.",
    ],
    prereqs=[
        ("dp", "Three states per day, each built from the previous day's states."),
        ("simulation", "Reading the trading rules as allowed transitions between states."),
    ],
)

_p(
    "number-of-lis", "Number of Longest Increasing Subsequences", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP", "Counting"], companies=["Meta", "Google"],
    shape="arr", ret="long", todo="for each i keep len[i] and cnt[i]; a longer extension resets the count, an equal one adds",
    description=(
        "Count the **longest strictly increasing subsequences** of the array (two subsequences are "
        "different if they use different positions).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of increasing subsequences of maximum length."
    ),
    constraints="1 ≤ n ≤ 2000\n-10^6 ≤ a[i] ≤ 10^6\nThe answer fits in a signed 64-bit integer.",
    hints=[
        "The O(n²) LIS DP computes len[i], the longest increasing subsequence ending at i.",
        "Carry cnt[i], the number of subsequences achieving len[i].",
        "For j < i with a[j] < a[i]: if len[j] + 1 > len[i], take len and count from j; if equal, add cnt[j]. Finally sum cnt over the maximal lengths.",
    ],
    opt=("O(n²)", "O(n)", "Two arrays over the classic quadratic LIS DP."),
    editorial=(
        "## The one thing this teaches\n**Counting optimal solutions rides along the optimisation "
        "DP.** Wherever the DP compares candidates, a count can follow: a strictly better "
        "candidate *replaces* the count, an equally good one *adds* to it.\n\n"
        "## Approach\n```java\nfor (int i = 0; i < n; i++) {\n    len[i] = 1; cnt[i] = 1;\n"
        "    for (int j = 0; j < i; j++) {\n        if (a[j] >= a[i]) continue;\n"
        "        if (len[j] + 1 > len[i]) { len[i] = len[j] + 1; cnt[i] = cnt[j]; }\n"
        "        else if (len[j] + 1 == len[i]) cnt[i] += cnt[j];\n    }\n}\n"
        "// answer: sum of cnt[i] over i with len[i] == max len\n```\n\n"
        "## The final sum\nThe longest subsequences can end at several different indices, so the "
        "answer is not `cnt` at the index of the maximum — it is the sum over every index "
        "achieving it. `2 2 2 2 2` has five longest subsequences, one ending at each position.\n\n"
        "The same replace-or-add rule counts shortest paths in Dijkstra, which is the Number of "
        "Shortest Paths problem."
    ),
    py='''
def solve(a):
    n = len(a)
    length = [1] * n
    cnt = [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                if length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    cnt[i] = cnt[j]
                elif length[j] + 1 == length[i]:
                    cnt[i] += cnt[j]
    best = max(length)
    return sum(c for l, c in zip(length, cnt) if l == best)
''',
    java='''
    static long solve(int[] a) {
        int n = a.length;
        int[] len = new int[n];
        long[] cnt = new long[n];
        int best = 0;
        for (int i = 0; i < n; i++) {
            len[i] = 1; cnt[i] = 1;
            for (int j = 0; j < i; j++) {
                if (a[j] >= a[i]) continue;
                if (len[j] + 1 > len[i]) { len[i] = len[j] + 1; cnt[i] = cnt[j]; }
                else if (len[j] + 1 == len[i]) cnt[i] += cnt[j];
            }
            best = Math.max(best, len[i]);
        }
        long total = 0;
        for (int i = 0; i < n; i++) if (len[i] == best) total += cnt[i];
        return total;
    }
''',
    examples=[("Example 1", "5\n1 3 5 4 7\n"), ("Example 2", "5\n2 2 2 2 2\n")],
    hidden=[
        ("Single element", "1\n1\n"),
        ("Strictly increasing", "4\n1 2 3 4\n"),
        ("Branching", "6\n1 2 4 3 5 4\n"),
        ("Pairs of choices", "6\n1 1 2 2 3 3\n"),
    ],
    expl=[
        "`1 3 4 7` and `1 3 5 7`.",
        "Each single element is a longest increasing subsequence.",
    ],
    prereqs=[
        ("dp", "The quadratic LIS recurrence, with a count carried beside each length."),
        ("array_patterns", "Summing counts over every index that ends a longest subsequence."),
    ],
)
