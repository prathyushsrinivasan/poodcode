# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 20 — DP, searching an answer, number bases and ordered structure.
#
#   min-cost-tickets              dp over calendar days: each pass looks back 1, 7 or 30
#   min-insertions-palindrome     interval DP; equivalently n − longest palindromic subsequence
#   kth-smallest-pair-distance    binary search the distance, count pairs with two pointers
#   reduce-array-size-half        remove the most frequent values first
#   sum-two-integers-bits         XOR adds without carries; AND << 1 is the carry
#   excel-column-title            bijective base 26: subtract one before each digit
#   nth-digit                     skip whole blocks of 1-digit, 2-digit, 3-digit numbers
#   longest-path-dag              relax edges in topological order, keeping the maximum
#   longest-subarray-sum-k        the FIRST index of each prefix sum gives the longest span
#   bst-from-preorder             each subtree is a run of values below a bound
# ===========================================================================

_p(
    "min-cost-tickets", "Minimum Cost for Tickets", "Medium",
    topics=["Dynamic Programming", "Arrays"], subtopics=["1D DP"], companies=["Amazon", "Google"],
    shape="arr2", ret="int", todo="cost[d] for every calendar day: a non-travel day copies d − 1; a travel day tries all three passes",
    description=(
        "You travel on the given days of a year (numbered 1 to 365). Three passes are sold:\n\n"
        "- a **1-day** pass for `costs[0]`,\n- a **7-day** pass for `costs[1]`,\n- a **30-day** pass for `costs[2]`.\n\n"
        "A pass bought on day `d` covers `d` through `d + length − 1`. Print the minimum total "
        "cost to cover every travel day.\n\n"
        "### Input\n- Line 1: `n`, the number of travel days.\n- Line 2: the travel days, strictly increasing.\n"
        "- Line 3: `3`.\n- Line 4: the three costs.\n\n"
        "### Output\nThe minimum cost."
    ),
    constraints="1 ≤ n ≤ 365\n1 ≤ day ≤ 365\n1 ≤ cost ≤ 1000",
    hints=[
        "Greedy fails: a 7-day pass is worth it only if enough travel days fall inside it.",
        "Let cost[d] be the cheapest way to cover every travel day up to day d. On a day you do not travel, cost[d] = cost[d − 1].",
        "On a travel day, the last pass bought covers d: cost[d] = min(cost[d−1] + c1, cost[max(0, d−7)] + c7, cost[max(0, d−30)] + c30).",
    ],
    opt=("O(365)", "O(365)", "One entry per calendar day, three choices each."),
    editorial=(
        "## The one thing this teaches\n**Decide on the last choice, and let it look back.** The "
        "pass covering the final travel day was bought at most 1, 7 or 30 days earlier. Whatever "
        "came before that pass is the same problem on a shorter calendar.\n\n"
        "## Approach\n```java\nboolean[] travel = new boolean[366];\nfor (int d : days) travel[d] = true;\n"
        "int[] cost = new int[366];\nfor (int d = 1; d <= 365; d++) {\n"
        "    if (!travel[d]) { cost[d] = cost[d - 1]; continue; }\n"
        "    cost[d] = Math.min(cost[d - 1] + c[0],\n"
        "              Math.min(cost[Math.max(0, d - 7)] + c[1], cost[Math.max(0, d - 30)] + c[2]));\n}\n"
        "return cost[365];\n```\n\n"
        "## Why `max(0, d − 7)`\nA 7-day pass ending on day 5 would have started before day 1. "
        "Clamping to day 0 — cost 0 — means \"this pass covers everything so far\".\n\n"
        "## Walkthrough (Example 1)\nDays `1 4 6 7 8 20`, costs `2 7 15`. A 1-day pass on day 1 "
        "(2), a 7-day pass covering days 4–10 (7), a 1-day pass on day 20 (2): 11. The 30-day "
        "pass at 15 alone is dearer."
    ),
    py='''
def solve(a, b):
    import bisect
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def cheapest(i):
        if i >= len(a):
            return 0
        return min(c + cheapest(bisect.bisect_left(a, a[i] + length)) for c, length in zip(b, (1, 7, 30)))

    return cheapest(0)
''',
    java='''
    static int solve(int[] days, int[] c) {
        boolean[] travel = new boolean[366];
        for (int d : days) travel[d] = true;
        int[] cost = new int[366];
        for (int d = 1; d <= 365; d++) {
            if (!travel[d]) { cost[d] = cost[d - 1]; continue; }
            cost[d] = Math.min(cost[d - 1] + c[0],
                      Math.min(cost[Math.max(0, d - 7)] + c[1], cost[Math.max(0, d - 30)] + c[2]));
        }
        return cost[365];
    }
''',
    examples=[
        ("Example 1", "6\n1 4 6 7 8 20\n3\n2 7 15\n"),
        ("Example 2", "12\n1 2 3 4 5 6 7 8 9 10 30 31\n3\n2 7 15\n"),
    ],
    hidden=[
        ("A longer pass is cheaper", "1\n365\n3\n5 3 10\n"),
        ("Far apart days", "3\n1 100 200\n3\n4 20 50\n"),
        ("A whole month", "30\n1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30\n3\n1 7 20\n"),
        ("Two weekly passes", "14\n1 2 3 4 5 6 7 8 9 10 11 12 13 14\n3\n3 10 40\n"),
    ],
    expl=[
        "1-day pass on day 1, 7-day pass for days 4–10, 1-day pass on day 20: 2 + 7 + 2 = 11.",
        "A 30-day pass for days 1–30 and a 1-day pass on day 31: 15 + 2 = 17.",
    ],
    prereqs=[
        ("dp", "A table over calendar days where each entry looks back by a pass length."),
        ("array_patterns", "Marking travel days in a boolean array indexed by day."),
    ],
)

_p(
    "min-insertions-palindrome", "Minimum Insertions to Make a Palindrome", "Hard",
    topics=["Dynamic Programming", "Strings"], subtopics=["2D DP", "Interval DP", "Palindromes"], companies=["Google", "Amazon"],
    shape="str", ret="int", todo="dp[i][j] = insertions for s[i..j]: matching ends cost dp[i+1][j−1], otherwise 1 + the cheaper side",
    description=(
        "Insert characters anywhere in `s`, as few as possible, so that it becomes a palindrome. "
        "Print the minimum number of insertions.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe minimum number of insertions."
    ),
    constraints="1 ≤ |s| ≤ 500\ns consists of lowercase English letters",
    hints=[
        "Look at the two ends. If they match, they already pair up — solve the inside.",
        "If they differ, one of them needs a partner inserted on the other side: 1 + (answer without the left end) or 1 + (answer without the right end).",
        "Fill dp[i][j] by increasing length. Alternatively: the characters that pair with each other form a palindromic subsequence, so the answer is n − LPS.",
    ],
    opt=("O(n²)", "O(n²)", "One entry per substring, each computed in O(1)."),
    editorial=(
        "## The one thing this teaches\n**Interval DP decides at the ends.** For a substring "
        "`s[i..j]`, only the outermost characters are special: they either match each other, or "
        "one of them gets a newly inserted mirror.\n\n"
        "## Approach\n```java\nint[][] dp = new int[n][n];              // length-1 substrings: 0\n"
        "for (int len = 2; len <= n; len++)\n    for (int i = 0; i + len - 1 < n; i++) {\n"
        "        int j = i + len - 1;\n"
        "        if (s.charAt(i) == s.charAt(j)) dp[i][j] = len == 2 ? 0 : dp[i + 1][j - 1];\n"
        "        else dp[i][j] = 1 + Math.min(dp[i + 1][j], dp[i][j - 1]);\n    }\nreturn dp[0][n - 1];\n```\n\n"
        "## The same answer, another way\nEvery character either pairs with an existing "
        "character or with an inserted one. The characters that pair among themselves form a "
        "palindromic subsequence, so the fewest insertions is `n − (longest palindromic "
        "subsequence)` — itself the LCS of `s` and its reverse.\n\n"
        "## Walkthrough: mbadm\nThe longest palindromic subsequence is `mam` (or `mdm`), length 3, "
        "so 5 − 3 = 2 insertions: `mbdadbm`."
    ),
    py='''
def solve(s):
    n = len(s)
    r = s[::-1]
    lcs = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(n):
            lcs[i + 1][j + 1] = lcs[i][j] + 1 if s[i] == r[j] else max(lcs[i][j + 1], lcs[i + 1][j])
    return n - lcs[n][n]
''',
    java='''
    static int solve(String s) {
        int n = s.length();
        int[][] dp = new int[n][n];
        for (int len = 2; len <= n; len++)
            for (int i = 0; i + len - 1 < n; i++) {
                int j = i + len - 1;
                if (s.charAt(i) == s.charAt(j)) dp[i][j] = len == 2 ? 0 : dp[i + 1][j - 1];
                else dp[i][j] = 1 + Math.min(dp[i + 1][j], dp[i][j - 1]);
            }
        return dp[0][n - 1];
    }
''',
    examples=[("Example 1", "zzazz\n"), ("Example 2", "mbadm\n"), ("Example 3", "leetcode\n")],
    hidden=[
        ("Single character", "a\n"),
        ("Two different", "ab\n"),
        ("All distinct", "abcd\n"),
        ("Two pairs", "aabb\n"),
        ("Four letters", "race\n"),
    ],
    expl=[
        "Already a palindrome.",
        "\"mbdadbm\" — insert a d and a b.",
        "The longest palindromic subsequence has length 3 (such as \"eee\"), so 8 − 3 = 5.",
    ],
    prereqs=[
        ("dp2d", "A table over (start, end) filled by increasing substring length."),
        ("string_basics", "Palindromes, subsequences and reversing a string."),
    ],
)

_p(
    "kth-smallest-pair-distance", "K-th Smallest Pair Distance", "Hard",
    topics=["Binary Search", "Two Pointers", "Sorting"], subtopics=["Binary Search on Answer"], companies=["Google"],
    shape="arr_k", ret="long", todo="sort; binary search the distance d, counting pairs with difference ≤ d by a sliding left pointer",
    description=(
        "The distance of a pair `(i, j)` with `i < j` is `|a[i] − a[j]|`. Among all "
        "`n(n − 1)/2` pairs, print the `k`-th smallest distance.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe k-th smallest distance."
    ),
    constraints="2 ≤ n ≤ 10^4\n0 ≤ a[i] ≤ 10^6\n1 ≤ k ≤ n(n − 1)/2",
    hints=[
        "Listing all pairs is O(n²) distances — 5·10^7 at n = 10^4, and then a sort.",
        "Flip the question: for a distance d, how many pairs have distance ≤ d? That count grows with d.",
        "Sort the array. For each right end, the left ends within d form a contiguous range, found with a pointer that only moves right. Binary search the smallest d whose count reaches k.",
    ],
    opt=("O(n log n + n log W)", "O(1)", "A sort, then O(log W) counting passes of O(n), where W is the value range."),
    editorial=(
        "## The one thing this teaches\n**Counting is easier than selecting.** Picking the k-th "
        "smallest of n² values directly is expensive. Counting how many are ≤ d is one linear "
        "pass, and that count is monotone in d — which is all binary search needs.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong lo = 0, hi = a[n - 1] - a[0];\n"
        "while (lo < hi) {\n    long mid = (lo + hi) / 2;\n    long count = 0;\n"
        "    for (int right = 0, left = 0; right < n; right++) {\n"
        "        while (a[right] - a[left] > mid) left++;\n        count += right - left;   // pairs (left..right−1, right)\n    }\n"
        "    if (count >= k) hi = mid; else lo = mid + 1;\n}\nreturn lo;\n```\n\n"
        "## Why the answer is a real distance\nThe search finds the smallest `d` with at least k "
        "pairs ≤ d. If `d` were not an actual distance, `d − 1` would have the same count and "
        "would have been chosen instead.\n\n"
        "## Why sorting is allowed\nThe multiset of pair distances does not depend on the order "
        "of the array, so sorting changes nothing about the answer."
    ),
    py='''
def solve(a, k):
    d = sorted(abs(a[i] - a[j]) for i in range(len(a)) for j in range(i + 1, len(a)))
    return d[k - 1]
''',
    java='''
    static long solve(int[] a, long k) {
        int n = a.length;
        Arrays.sort(a);
        long lo = 0, hi = a[n - 1] - a[0];
        while (lo < hi) {
            long mid = (lo + hi) / 2;
            long count = 0;
            for (int right = 0, left = 0; right < n; right++) {
                while (a[right] - a[left] > mid) left++;
                count += right - left;
            }
            if (count >= k) hi = mid; else lo = mid + 1;
        }
        return lo;
    }
''',
    examples=[("Example 1", "3 1\n1 3 1\n"), ("Example 2", "3 3\n1 6 1\n")],
    hidden=[
        ("One pair", "2 1\n4 9\n"),
        ("All equal", "4 6\n1 1 1 1\n"),
        ("Fourth of ten", "5 4\n1 2 3 4 5\n"),
        ("Fifth of ten", "5 5\n1 2 3 4 5\n"),
        ("Largest distance", "6 15\n0 100 5 7 60 1000000\n"),
    ],
    expl=[
        "The distances are 2, 0 and 2; the smallest is 0.",
        "The distances are 5, 0 and 5; sorted 0, 5, 5, so the third is 5.",
    ],
    prereqs=[
        ("binary_search", "Searching the answer space for the smallest d whose count reaches k."),
        ("two_pointers", "Counting pairs within a distance with a left pointer that never moves back."),
    ],
)

_p(
    "reduce-array-size-half", "Reduce Array Size to Half", "Medium",
    topics=["Greedy", "Hashing", "Sorting"], subtopics=["Frequency Counting"], companies=["Amazon"],
    shape="arr", ret="int", todo="count each value, sort the counts descending, and take them until at least half is removed",
    description=(
        "Choose a set of values and remove **every occurrence** of each from the array. Print the "
        "size of the smallest set that removes at least half of the array's elements.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe minimum number of values to choose."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^5\n\"At least half\" means 2 × removed ≥ n",
    hints=[
        "Choosing a value removes as many elements as it has occurrences.",
        "To reach a target with as few choices as possible, take the biggest ones first.",
        "Count frequencies, sort them in decreasing order, and add them up until twice the total reaches n.",
    ],
    opt=("O(n log n)", "O(n)", "Counting is O(n); sorting the counts dominates. Bucketing counts makes it O(n)."),
    editorial=(
        "## The one thing this teaches\n**When every choice costs the same, take the biggest.** "
        "Each chosen value costs 1 regardless of how many elements it removes, so any optimal set "
        "can swap a smaller count for a larger unused one without getting worse.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> freq = new HashMap<>();\n"
        "for (int x : a) freq.merge(x, 1, Integer::sum);\n"
        "List<Integer> counts = new ArrayList<>(freq.values());\ncounts.sort(Collections.reverseOrder());\n"
        "int removed = 0, chosen = 0;\nfor (int c : counts) {\n    removed += c; chosen++;\n"
        "    if (2 * removed >= n) break;\n}\nreturn chosen;\n```\n\n"
        "## The exchange argument\nSuppose an optimal set skips the largest count `C` but uses "
        "some count `c ≤ C`. Swapping `c` for `C` keeps the set size and removes at least as "
        "many elements. Repeating the swap turns any optimal set into the greedy one."
    ),
    py='''
def solve(a):
    from collections import Counter
    removed = 0
    for chosen, c in enumerate(sorted(Counter(a).values(), reverse=True), 1):
        removed += c
        if 2 * removed >= len(a):
            return chosen
''',
    java='''
    static int solve(int[] a) {
        int n = a.length;
        int[] freq = new int[100001];
        for (int x : a) freq[x]++;
        int[] countsOfCount = new int[n + 1];
        for (int f : freq) if (f > 0) countsOfCount[f]++;
        int removed = 0, chosen = 0;
        for (int f = n; f >= 1; f--)
            for (int t = 0; t < countsOfCount[f]; t++) {
                removed += f; chosen++;
                if (2 * removed >= n) return chosen;
            }
        return chosen;
    }
''',
    examples=[("Example 1", "10\n3 3 3 3 5 5 5 2 2 7\n"), ("Example 2", "6\n7 7 7 7 7 7\n")],
    hidden=[
        ("Two distinct", "2\n1 2\n"),
        ("All distinct, even", "4\n1 2 3 4\n"),
        ("All distinct, odd", "5\n1 2 3 4 5\n"),
        ("Ties in frequency", "8\n1 1 2 2 3 3 4 4\n"),
        ("One dominant value", "7\n9 9 9 9 1 2 3\n"),
    ],
    expl=[
        "Removing 3 (four copies) and 5 (three copies) removes 7 of 10 elements.",
        "Removing 7 empties the array.",
    ],
    prereqs=[
        ("hashing", "Counting how often each value occurs."),
        ("greedy", "Taking the largest counts first, justified by an exchange argument."),
    ],
)

_p(
    "sum-two-integers-bits", "Sum of Two Integers Without +", "Medium",
    topics=["Bit Manipulation", "Math"], subtopics=["XOR", "Carry"], companies=["Meta", "Microsoft"],
    shape="two", ret="int", todo="repeat: sum without carries is x ^ y, the carries are (x & y) << 1 — until there are no carries",
    description=(
        "Print `x + y`, computed **without** the `+` and `-` operators — only bitwise operations.\n\n"
        "The judge checks only the output; the constraint is the exercise.\n\n"
        "### Input\nOne line: `x y`.\n\n"
        "### Output\nTheir sum."
    ),
    constraints="-1000 ≤ x, y ≤ 1000",
    hints=[
        "Add two single bits: the sum bit is their XOR and the carry is their AND.",
        "That works across all bits at once: x ^ y is the sum ignoring carries, and (x & y) << 1 is every carry, moved into place.",
        "Now add those two numbers the same way. Repeat until the carry is zero. In 32-bit two's complement, negative numbers need no special case.",
    ],
    opt=("O(32)", "O(1)", "Each round moves every carry at least one position left; at most 32 rounds on an int."),
    editorial=(
        "## The one thing this teaches\n**Addition is XOR plus carries.** A half adder on one bit "
        "column produces `a ^ b` and carry `a & b`. Doing every column at once gives a partial "
        "sum and a carry word; adding those is the same problem again, with the carries one "
        "place further left.\n\n"
        "## Approach\n```java\nint a = x, b = y;\nwhile (b != 0) {\n"
        "    int carry = (a & b) << 1;\n    a ^= b;           // sum without carries\n    b = carry;        // carries still to add\n}\nreturn a;\n```\n\n"
        "## Why it stops\nEach round's carry word has at least one more trailing zero than the "
        "last, so after at most 32 rounds on an `int` it is 0 — the top carry falls off the end, "
        "which is exactly two's complement wrap-around.\n\n"
        "## Negative numbers\nTwo's complement exists so that one adder circuit handles signed "
        "and unsigned values alike. `-1 + 1` is `…1111 + …0001`: the carry ripples off the top "
        "and leaves 0. In Python, whose integers are unbounded, you would have to mask to 32 bits "
        "yourself; Java's `int` does it for you."
    ),
    py='''
def solve(x, y):
    return x + y
''',
    java='''
    static int solve(long x, long y) {
        int a = (int) x, b = (int) y;
        while (b != 0) {
            int carry = (a & b) << 1;
            a ^= b;
            b = carry;
        }
        return a;
    }
''',
    examples=[("Example 1", "1 2\n"), ("Example 2", "5 3\n")],
    hidden=[
        ("Cancels to zero", "-1 1\n"),
        ("Both negative", "-7 -8\n"),
        ("Extremes cancel", "1000 -1000\n"),
        ("Zeros", "0 0\n"),
        ("Negative result", "-1000 999\n"),
    ],
    expl=[
        "01 ^ 10 = 11 with no carries: 3.",
        "101 ^ 011 = 110, carry (101 & 011) << 1 = 010; then 110 ^ 010 = 100, carry 100; then 100 ^ 100 = 0, carry 1000; finally 1000.",
    ],
    prereqs=[
        ("bit_manip", "XOR, AND and left shift, and two's complement for negative values."),
        ("overflow", "Carries falling off the top bit are how 32-bit arithmetic wraps."),
    ],
)

_p(
    "excel-column-title", "Excel Column Title", "Easy",
    topics=["Math", "Strings"], subtopics=["Number Bases"], companies=["Microsoft", "Meta"],
    shape="n", ret="String", todo="loop: subtract one, take the remainder mod 26 as a letter, divide by 26; reverse at the end",
    description=(
        "Spreadsheet columns are named `A, B, …, Z, AA, AB, …, AZ, BA, …, ZZ, AAA, …`. Print the "
        "name of column number `n` (column 1 is `A`).\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe column title."
    ),
    constraints="1 ≤ n ≤ 2^31 − 1",
    hints=[
        "It looks like base 26, but there is no zero digit: Z is 26, and 27 is AA rather than A0.",
        "Shift the digits to 0..25 by subtracting 1 from n before taking each remainder.",
        "letter = 'A' + (n − 1) % 26, then n = (n − 1) / 26. Letters come out last-first.",
    ],
    opt=("O(log n)", "O(log n)", "One letter per base-26 digit."),
    editorial=(
        "## The one thing this teaches\n**Bijective numeration: digits 1..26 instead of 0..25.** "
        "Ordinary base 26 would need a zero digit. Column names skip it, so each step first "
        "subtracts 1 to map the digit range 1..26 onto 0..25, then proceeds as usual.\n\n"
        "## Approach\n```java\nStringBuilder sb = new StringBuilder();\nwhile (n > 0) {\n"
        "    n--;                                  // 1..26 → 0..25\n"
        "    sb.append((char) ('A' + n % 26));\n    n /= 26;\n}\nreturn sb.reverse().toString();\n```\n\n"
        "## Walkthrough: 28\nn = 28, decremented to 27: letter `'A' + 1 = B`, then n = 27 / 26 = 1. "
        "n = 1, decremented to 0: letter `A`, then n = 0. Reversed: `AB`.\n\n"
        "## The classic bug\nWithout the `n--`, 26 gives remainder 0 — printed as `A` — and a "
        "quotient of 1 that prints another letter: `BA` instead of `Z`."
    ),
    py='''
def solve(n):
    width, block = 1, 26
    while n > block:
        n -= block
        width += 1
        block *= 26
    n -= 1
    letters = []
    for _ in range(width):
        n, r = divmod(n, 26)
        letters.append(chr(ord("A") + r))
    return "".join(reversed(letters))
''',
    java='''
    static String solve(long n) {
        StringBuilder sb = new StringBuilder();
        while (n > 0) {
            n--;
            sb.append((char) ('A' + n % 26));
            n /= 26;
        }
        return sb.reverse().toString();
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "28\n"), ("Example 3", "701\n")],
    hidden=[
        ("Z", "26\n"),
        ("First two-letter title", "27\n"),
        ("ZZZ", "18278\n"),
        ("Largest int", "2147483647\n"),
    ],
    expl=[
        "Column 1 is A.",
        "26 columns A–Z, then AA is 27 and AB is 28.",
        "ZY: (26 × 26) + 25 = 701.",
    ],
    prereqs=[
        ("math_digits", "Extracting digits with % and /, adjusted for a base with no zero digit."),
        ("string_basics", "Building a string from characters and reversing it."),
    ],
)

_p(
    "nth-digit", "Nth Digit", "Medium",
    topics=["Math"], subtopics=["Counting", "Digits"], companies=["Google"],
    shape="n", ret="int", todo="skip blocks: 9 one-digit numbers, 90 two-digit, 900 three-digit … then index into the right number",
    description=(
        "Write the positive integers one after another: `123456789101112131415…`. Print the `n`-th "
        "digit of that sequence (the first digit is `1`).\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe digit."
    ),
    constraints="1 ≤ n ≤ 2^31 − 1",
    hints=[
        "Building the string is hopeless at n = 2·10^9.",
        "There are 9 one-digit numbers (9 digits), 90 two-digit numbers (180 digits), 900 three-digit numbers (2700 digits)…",
        "Subtract whole blocks while n is larger than the block. Then the number is start + (n − 1) / len, and the digit is at position (n − 1) % len in it.",
    ],
    opt=("O(log n)", "O(1)", "At most ten blocks to skip, then one number to inspect."),
    editorial=(
        "## The one thing this teaches\n**Count in blocks, then index.** Numbers of the same "
        "length contribute equally many digits, so the sequence splits into blocks you can skip "
        "with arithmetic instead of generating them.\n\n"
        "## Approach\n```java\nlong len = 1, count = 9, start = 1;\nwhile (n > len * count) {\n"
        "    n -= len * count;       // skip every len-digit number\n    len++; count *= 10; start *= 10;\n}\n"
        "long number = start + (n - 1) / len;\nreturn Long.toString(number).charAt((int) ((n - 1) % len)) - '0';\n```\n\n"
        "## Walkthrough: n = 1000\nSkip 9 (one-digit): n = 991. Skip 180 (two-digit): n = 811. "
        "811 ≤ 2700, so the digit is in a three-digit number: `100 + 810 / 3 = 370`, position "
        "`810 % 3 = 0` → `3`.\n\n"
        "## Use long\nAt the ten-digit block, `len * count` is 10 × 9·10⁹ = 9·10¹⁰ — far past an "
        "int, even though n itself fits in one."
    ),
    py='''
def solve(n):
    def digits_upto(x):
        total, length, low = 0, 1, 1
        while low <= x:
            total += (min(x, low * 10 - 1) - low + 1) * length
            length += 1
            low *= 10
        return total

    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if digits_upto(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return int(str(lo)[n - digits_upto(lo - 1) - 1])
''',
    java='''
    static int solve(long n) {
        long len = 1, count = 9, start = 1;
        while (n > len * count) {
            n -= len * count;
            len++;
            count *= 10;
            start *= 10;
        }
        long number = start + (n - 1) / len;
        return Long.toString(number).charAt((int) ((n - 1) % len)) - '0';
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "11\n")],
    hidden=[
        ("Last one-digit number", "9\n"),
        ("First digit of 10", "10\n"),
        ("Last digit of 99", "189\n"),
        ("First digit of 100", "190\n"),
        ("Inside 370", "1000\n"),
        ("Largest int", "2147483647\n"),
    ],
    expl=[
        "The third digit is the number 3.",
        "The sequence goes 1 2 … 9 1 0 1 1: the 11th digit is the 0 of 10.",
    ],
    prereqs=[
        ("math_digits", "How many digits the numbers of each length contribute."),
        ("overflow", "Block sizes that exceed an int before the loop stops."),
    ],
)

_p(
    "longest-path-dag", "Longest Path in a DAG", "Medium",
    topics=["Graphs", "Topological Sort", "Dynamic Programming"], subtopics=["DP on DAG"], companies=["Google", "Microsoft"],
    shape="wgraph", ret="long", todo="Kahn's order; when u is taken, best[v] = max(best[v], best[u] + w); the answer is the largest best",
    description=(
        "A directed **acyclic** graph has `n` nodes and weighted edges. Print the largest total "
        "weight of any path — it may start and end at any nodes. A path with no edges has weight 0.\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v w`, an edge from `u` to `v` of weight `w`.\n\n"
        "### Output\nThe maximum path weight."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 5·10^4\n0 ≤ u, v < n\n1 ≤ w ≤ 10^4\nThe graph has no directed cycle",
    hints=[
        "In a general graph, longest path is NP-hard. What does having no cycles buy you?",
        "In topological order, every edge into v comes from a node processed before v.",
        "Let best[v] be the heaviest path ending at v, starting at 0. Processing u in topological order, relax each edge: best[v] = max(best[v], best[u] + w).",
    ],
    opt=("O(n + m)", "O(n + m)", "Kahn's algorithm, with one relaxation per edge."),
    editorial=(
        "## The one thing this teaches\n**A topological order is a DP order.** DP needs "
        "subproblems solved before they are used. In a DAG, \"the best path ending at v\" depends "
        "only on its predecessors — and a topological order puts every predecessor first.\n\n"
        "## Approach\n```java\n// indegree counts, then a queue of indegree-0 nodes\nlong[] best = new long[n];   // a path may start anywhere\n"
        "while (!queue.isEmpty()) {\n    int u = queue.poll();\n    for (int[] e : adj[u]) {\n"
        "        best[e[0]] = Math.max(best[e[0]], best[u] + e[1]);\n"
        "        if (--indeg[e[0]] == 0) queue.add(e[0]);\n    }\n}\nreturn max(best);\n```\n\n"
        "## Why cycles break it\nWith a cycle of positive weight, a path could loop forever, and "
        "\"simple path\" makes the problem NP-hard. Without cycles, every path is automatically "
        "simple and the DP is exact.\n\n"
        "## The same trick elsewhere\nNegating the weights turns this into a shortest path, and "
        "the same one pass solves shortest paths in a DAG — even with negative edges, where "
        "Dijkstra would fail."
    ),
    py='''
def solve(n, edges):
    import sys
    from functools import lru_cache
    sys.setrecursionlimit(10000)
    out = [[] for _ in range(n)]
    for u, v, w in edges:
        out[u].append((v, w))

    @lru_cache(maxsize=None)
    def heaviest_from(u):
        return max([0] + [w + heaviest_from(v) for v, w in out[u]])

    return max(heaviest_from(u) for u in range(n))
''',
    java='''
    static long solve(int n, int[][] edges) {
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        int[] indeg = new int[n];
        for (int[] e : edges) { adj.get(e[0]).add(new int[]{e[1], e[2]}); indeg[e[1]]++; }
        ArrayDeque<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
        long[] best = new long[n];
        long answer = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            answer = Math.max(answer, best[u]);
            for (int[] e : adj.get(u)) {
                best[e[0]] = Math.max(best[e[0]], best[u] + e[1]);
                if (--indeg[e[0]] == 0) q.add(e[0]);
            }
        }
        return answer;
    }
''',
    examples=[
        ("Example 1", "5 5\n0 1 3\n0 2 2\n1 3 4\n2 3 6\n3 4 1\n"),
        ("Example 2", "3 0\n"),
    ],
    hidden=[
        ("Edge into node 0", "2 1\n1 0 7\n"),
        ("Edges listed out of order", "4 3\n0 1 1\n2 3 5\n1 2 1\n"),
        ("One heavy edge beats a long path", "4 4\n0 3 10\n0 1 1\n1 2 1\n2 3 1\n"),
        ("Parallel edges", "2 2\n0 1 4\n0 1 9\n"),
        ("Two components", "6 4\n0 1 2\n1 2 2\n3 4 1\n4 5 100\n"),
    ],
    expl=[
        "0 → 2 → 3 → 4 weighs 2 + 6 + 1 = 9; 0 → 1 → 3 → 4 weighs only 8.",
        "No edges, so every path is a single node of weight 0.",
    ],
    prereqs=[
        ("topo", "Kahn's algorithm, which yields every node after all of its predecessors."),
        ("dp", "best[v] built from best[u] of its predecessors."),
    ],
)

_p(
    "longest-subarray-sum-k", "Longest Subarray with Sum K", "Medium",
    topics=["Prefix Sums", "Hashing", "Arrays"], subtopics=["Prefix Sum + Hash Map"], companies=["Amazon", "Meta"],
    shape="arr_k", ret="int", todo="map each prefix sum to the FIRST index it occurs; at i, a match for prefix − k gives length i − first",
    description=(
        "Print the length of the **longest** contiguous subarray whose sum is exactly `k`, or `0` "
        "if there is none. Values may be negative.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe maximum length."
    ),
    constraints="1 ≤ n ≤ 2·10^5\n-10^4 ≤ a[i] ≤ 10^4\n-10^9 ≤ k ≤ 10^9",
    hints=[
        "Negative values rule out a sliding window: growing the window can shrink its sum.",
        "sum(a[j+1..i]) = prefix[i] − prefix[j]. You want prefix[j] = prefix[i] − k, with j as SMALL as possible.",
        "Store the first index of each prefix sum (starting with prefix 0 at index −1) and never overwrite it.",
    ],
    opt=("O(n)", "O(n)", "One pass with a hash map of first occurrences."),
    editorial=(
        "## The one thing this teaches\n**What you store decides what you can answer.** Subarray "
        "Sum Equals K stores a *count* per prefix sum to count subarrays. Here the question is "
        "the longest, so each prefix sum stores the *earliest* index it appeared — the farthest "
        "left a matching subarray could start.\n\n"
        "## Approach\n```java\nMap<Long, Integer> first = new HashMap<>();\nfirst.put(0L, -1);\n"
        "long prefix = 0;\nint best = 0;\nfor (int i = 0; i < n; i++) {\n    prefix += a[i];\n"
        "    Integer j = first.get(prefix - k);\n    if (j != null) best = Math.max(best, i - j);\n"
        "    first.putIfAbsent(prefix, i);   // keep the earliest\n}\n```\n\n"
        "## Two details that matter\n- `first.put(0L, -1)` lets a subarray start at index 0.\n"
        "- `putIfAbsent`, not `put`: overwriting with a later index would shorten every future match.\n\n"
        "## Walkthrough: 1 −1 5 −2 3, k = 3\nPrefixes: 1, 0, 5, 3, 6. At i = 3 the prefix is 3, "
        "and 3 − 3 = 0 first occurred at −1: length 4. At i = 4, 6 − 3 = 3 first occurred at "
        "3: length 1. The answer is 4."
    ),
    py='''
def solve(a, k):
    best = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s == k:
                best = max(best, j - i + 1)
    return best
''',
    java='''
    static int solve(int[] a, long k) {
        HashMap<Long, Integer> first = new HashMap<>();
        first.put(0L, -1);
        long prefix = 0;
        int best = 0;
        for (int i = 0; i < a.length; i++) {
            prefix += a[i];
            Integer j = first.get(prefix - k);
            if (j != null) best = Math.max(best, i - j);
            first.putIfAbsent(prefix, i);
        }
        return best;
    }
''',
    examples=[("Example 1", "5 3\n1 -1 5 -2 3\n"), ("Example 2", "4 1\n-2 -1 2 1\n")],
    hidden=[
        ("No subarray", "3 10\n1 2 3\n"),
        ("All zeros", "5 0\n0 0 0 0 0\n"),
        ("Alternating signs", "6 0\n1 -1 1 -1 1 -1\n"),
        ("Single negative element", "1 -5\n-5\n"),
        ("Longest of several matches", "7 7\n4 3 -3 3 -3 3 1\n"),
    ],
    expl=[
        "1 + (−1) + 5 + (−2) = 3, length 4.",
        "−1 + 2 = 1. No run of three or four elements sums to 1, so the answer is 2.",
    ],
    prereqs=[
        ("prefix_sum", "A subarray sum as the difference of two prefix sums."),
        ("hashing", "A map from prefix sum to the earliest index it occurred."),
    ],
)

_p(
    "bst-from-preorder", "BST from Preorder", "Medium",
    topics=["Trees", "Recursion"], subtopics=["BST", "Tree Construction"], companies=["Amazon", "Meta"],
    shape="arr", ret="String", todo="recurse with an upper bound: a subtree consumes the next values below its bound; emit each value after both children",
    description=(
        "The array is the **preorder** traversal of a binary search tree with distinct values. "
        "Rebuild the tree and print its **postorder** traversal.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the preorder values.\n\n"
        "### Output\nThe postorder values, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 1000\n1 ≤ value ≤ 10^8, values distinct\nThe input is the preorder of some BST",
    hints=[
        "Inserting each value into a BST one by one works, but costs O(n²) on sorted input.",
        "In preorder, a node is followed by its whole left subtree (all smaller values) and then its right subtree.",
        "Build with a bound: a call takes the next value only if it is below the bound, recurses left with the node's value as the bound, then right with the inherited bound.",
    ],
    opt=("O(n)", "O(h)", "Each value is consumed exactly once; recursion depth is the tree height."),
    editorial=(
        "## The one thing this teaches\n**Preorder plus the BST property is enough to rebuild the "
        "tree.** Preorder alone is ambiguous — but in a BST, where the left subtree ends is "
        "decided by the values themselves: it ends at the first value larger than the root.\n\n"
        "## Approach\n```java\nint idx = 0;\nvoid build(int bound) {\n"
        "    if (idx == n || a[idx] > bound) return;   // this subtree is empty\n"
        "    int val = a[idx++];\n    build(val);        // left: everything below val\n"
        "    build(bound);      // right: everything below the inherited bound\n"
        "    out.add(val);      // postorder: after both children\n}\nbuild(Integer.MAX_VALUE);\n```\n\n"
        "## Why no lower bound is needed\nPreorder visits the left subtree before the right. By the "
        "time the right call runs, every smaller value belonging here has already been "
        "consumed, so the next value is automatically above `val`.\n\n"
        "## No tree required\nSince the output is a traversal, the recursion can emit postorder "
        "directly — the tree exists only as the shape of the call stack."
    ),
    py='''
def solve(a):
    root = None
    left, right, val = {}, {}, {}
    for i, x in enumerate(a):
        val[i] = x
        if root is None:
            root = i
            continue
        cur = root
        while True:
            side = left if x < val[cur] else right
            if cur in side:
                cur = side[cur]
            else:
                side[cur] = i
                break
    out = []

    def post(u):
        if u in left:
            post(left[u])
        if u in right:
            post(right[u])
        out.append(val[u])

    post(root)
    return " ".join(map(str, out))
''',
    java='''
    static int idx;
    static StringBuilder out;

    static void build(int[] a, long bound) {
        if (idx == a.length || a[idx] > bound) return;
        int val = a[idx++];
        build(a, val);
        build(a, bound);
        if (out.length() > 0) out.append(' ');
        out.append(val);
    }

    static String solve(int[] a) {
        idx = 0;
        out = new StringBuilder();
        build(a, Long.MAX_VALUE);
        return out.toString();
    }
''',
    examples=[("Example 1", "6\n8 5 1 7 10 12\n"), ("Example 2", "2\n1 3\n")],
    hidden=[
        ("Single node", "1\n4\n"),
        ("Left chain", "4\n4 3 2 1\n"),
        ("Right chain", "4\n1 2 3 4\n"),
        ("Complete tree", "7\n50 30 20 40 70 60 80\n"),
    ],
    expl=[
        "The tree is 8 with children 5 (children 1 and 7) and 10 (right child 12).",
        "3 is the right child of 1.",
    ],
    prereqs=[
        ("bst", "Left subtrees hold smaller values, so the values themselves mark where a subtree ends."),
        ("tree_traversal", "Preorder and postorder, and emitting a traversal during recursion."),
    ],
)
