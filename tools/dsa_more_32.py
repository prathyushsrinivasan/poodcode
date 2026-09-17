# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 32 — quick wins and a few structural ideas.
#
#   jewels-and-stones                 a set of jewels makes each stone an O(1) check
#   rotate-string                     every rotation of s is a substring of s + s
#   reverse-vowels                    two pointers that skip consonants
#   find-highest-altitude             the highest prefix sum, including the start at 0
#   xor-queries-subarray              prefix XOR: a range is P[r + 1] ^ P[l]
#   number-complement                 XOR with a mask of ones as wide as the number
#   max-product-after-k-increments    always increment the smallest value
#   maximum-level-sum                 sum per depth, earliest depth wins ties
#   max-length-unique-concatenation   backtrack over words with 26-bit masks
#   min-vertices-reach-all            exactly the nodes with no incoming edge
#   similar-string-groups             union words that differ by one swap
#   maximum-swap                      swap the first digit with the last occurrence of a larger digit
# ===========================================================================

_p(
    "jewels-and-stones", "Jewels and Stones", "Easy",
    topics=["Hashing", "Strings"], subtopics=["Set Membership"], companies=["Amazon", "Adobe"],
    shape="str2", ret="int", todo="put the jewel letters in a set (or a boolean table); count the stones that are in it",
    description=(
        "Each letter of `jewels` is a type of jewel (letters are case-sensitive and distinct). "
        "Each letter of `stones` is a stone you have. Print how many of your stones are jewels.\n\n"
        "### Input\n- Line 1: `jewels`.\n- Line 2: `stones`.\n\n"
        "### Output\nThe number of jewel stones."
    ),
    constraints="1 ≤ |jewels|, |stones| ≤ 50\nEnglish letters",
    hints=[
        "Checking each stone against every jewel is O(|jewels| · |stones|).",
        "Membership questions are what sets are for.",
        "Store the jewels in a boolean array indexed by character code, then count in one pass over the stones.",
    ],
    opt=("O(|jewels| + |stones|)", "O(1)", "A 128-entry table for all ASCII letters."),
    editorial=(
        "## The one thing this teaches\n**Turn repeated searches into one lookup table.** The "
        "question \"is this stone a jewel?\" is asked once per stone. Building the answer table "
        "first makes each question O(1).\n\n"
        "## Approach\n```java\nboolean[] isJewel = new boolean[128];\n"
        "for (char ch : jewels.toCharArray()) isJewel[ch] = true;\nint count = 0;\n"
        "for (char ch : stones.toCharArray()) if (isJewel[ch]) count++;\n```\n\n"
        "## Case matters\n`a` and `A` are different jewels. Indexing by the character code keeps "
        "them apart automatically.\n\n"
        "## When a HashSet is better\nFor arbitrary Unicode or multi-character items, use a "
        "`HashSet`; for a small fixed alphabet an array is faster and simpler."
    ),
    py='''
def solve(s, t):
    return sum(1 for stone in t if stone in s)
''',
    java='''
    static int solve(String jewels, String stones) {
        boolean[] isJewel = new boolean[128];
        for (int i = 0; i < jewels.length(); i++) isJewel[jewels.charAt(i)] = true;
        int count = 0;
        for (int i = 0; i < stones.length(); i++) if (isJewel[stones.charAt(i)]) count++;
        return count;
    }
''',
    examples=[("Example 1", "aA\naAAbbbb\n"), ("Example 2", "z\nZZ\n")],
    hidden=[
        ("All jewels", "abc\ncabbac\n"),
        ("No jewels", "xyz\nabcABC\n"),
        ("Case sensitive", "B\nbBbB\n"),
    ],
    expl=[
        "a, A and A are jewels; the b's are not.",
        "Z is not the jewel z.",
    ],
    prereqs=[
        ("hashing", "A lookup table built before the scan."),
        ("string_basics", "Characters as array indices."),
    ],
)

_p(
    "rotate-string", "Rotate String", "Easy",
    topics=["Strings"], subtopics=["Rotation", "Doubling"], companies=["Google", "Amazon"],
    shape="str2", ret="String", todo="goal is a rotation of s exactly when the lengths match and goal occurs in s + s",
    description=(
        "A **shift** moves the first character of `s` to the end. Can `s` become `goal` after "
        "some number of shifts? Print `YES` or `NO`.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `goal`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s|, |goal| ≤ 100\nLowercase English letters",
    hints=[
        "Trying every rotation and comparing is O(n²) — fine here, but there is a neater view.",
        "Write s twice in a row. Every rotation of s appears as a length-n window of s + s.",
        "So check that the lengths are equal and that goal is a substring of s + s.",
    ],
    opt=("O(n)", "O(n)", "With a linear-time substring search such as KMP; library contains() is O(n²) worst case."),
    editorial=(
        "## The one thing this teaches\n**Doubling turns wrap-around into a contiguous window.** "
        "A rotation starts somewhere inside s and wraps past the end. In `s + s`, that wrapped "
        "sequence is just an ordinary substring.\n\n"
        "## Approach\n```java\nreturn s.length() == goal.length() && (s + s).contains(goal);\n```\n\n"
        "## Why the length check\nWithout it, `goal = \"a\"` would be found inside `\"aa\" + \"aa\"`, "
        "though `\"a\"` is not a rotation of `\"aa\"`.\n\n"
        "## The same trick elsewhere\nCircular arrays (Next Greater Element II) and repeated "
        "patterns (Repeated Substring Pattern) are handled by the same doubling idea."
    ),
    py='''
def solve(s, t):
    return "YES" if any(s[i:] + s[:i] == t for i in range(len(s))) else "NO"
''',
    java='''
    static String solve(String s, String goal) {
        return s.length() == goal.length() && (s + s).contains(goal) ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "abcde\ncdeab\n"), ("Example 2", "abcde\nabced\n")],
    hidden=[
        ("Single letter", "a\na\n"),
        ("Different lengths", "aa\na\n"),
        ("Half rotation", "abab\nbaba\n"),
        ("No shift needed", "xyz\nxyz\n"),
    ],
    expl=[
        "Two shifts: abcde → bcdea → cdeab.",
        "No rotation swaps the last two letters.",
    ],
    prereqs=[
        ("string_basics", "Substrings and concatenation."),
        ("modulo", "Rotations as indices taken modulo n."),
    ],
)

_p(
    "reverse-vowels", "Reverse Vowels of a String", "Easy",
    topics=["Two Pointers", "Strings"], subtopics=["Converging Pointers"], companies=["Google", "Amazon"],
    shape="str", ret="String", todo="pointers from both ends; move each past consonants, then swap the two vowels and step inward",
    description=(
        "Reverse only the vowels (`a e i o u`, in either case) of `s`, leaving every other "
        "character where it is.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe resulting string."
    ),
    constraints="1 ≤ |s| ≤ 3·10^5\nEnglish letters",
    hints=[
        "Reversing a whole string swaps the first and last characters, then moves inward.",
        "Here only vowels take part. Let each pointer skip characters that are not vowels.",
        "When both pointers rest on vowels, swap them and move both inward.",
    ],
    opt=("O(n)", "O(n)", "Each pointer moves at most n steps; a char array holds the result."),
    editorial=(
        "## The one thing this teaches\n**Converging pointers can filter as they go.** The "
        "reversal pattern stays the same; each pointer just skips the positions that do not take "
        "part.\n\n"
        "## Approach\n```java\nchar[] c = s.toCharArray();\nint lo = 0, hi = c.length - 1;\n"
        "while (lo < hi) {\n    while (lo < hi && !isVowel(c[lo])) lo++;\n"
        "    while (lo < hi && !isVowel(c[hi])) hi--;\n"
        "    char t = c[lo]; c[lo] = c[hi]; c[hi] = t;\n    lo++; hi--;\n}\nreturn new String(c);\n```\n\n"
        "## Uppercase vowels\n`A E I O U` count too — a lookup string such as `\"aeiouAEIOU\"` "
        "covers both cases.\n\n"
        "## Why `lo < hi` inside the skips\nWithout it, a pointer could run past the other when "
        "the middle has no vowels, and the final swap would undo an earlier one."
    ),
    py='''
def solve(s):
    vowels = [ch for ch in s if ch in "aeiouAEIOU"]
    out = []
    for ch in s:
        out.append(vowels.pop() if ch in "aeiouAEIOU" else ch)
    return "".join(out)
''',
    java='''
    static boolean isVowel(char ch) { return "aeiouAEIOU".indexOf(ch) >= 0; }

    static String solve(String s) {
        char[] c = s.toCharArray();
        int lo = 0, hi = c.length - 1;
        while (lo < hi) {
            while (lo < hi && !isVowel(c[lo])) lo++;
            while (lo < hi && !isVowel(c[hi])) hi--;
            char t = c[lo]; c[lo] = c[hi]; c[hi] = t;
            lo++;
            hi--;
        }
        return new String(c);
    }
''',
    examples=[("Example 1", "IceCreAm\n"), ("Example 2", "leetcode\n")],
    hidden=[
        ("No vowels", "bcdfg\n"),
        ("Two vowels", "aA\n"),
        ("Classic", "hello\n"),
        ("All vowels", "aeiou\n"),
    ],
    expl=[
        "The vowels I, e, e, A become A, e, e, I.",
        "The vowels e, e, o, e become e, o, e, e.",
    ],
    prereqs=[
        ("two_pointers", "Converging pointers that skip non-participating positions."),
        ("string_basics", "Working on a char array and building the string back."),
    ],
)

_p(
    "find-highest-altitude", "Find the Highest Altitude", "Easy",
    topics=["Prefix Sums", "Arrays"], subtopics=["Running Sum"], companies=["Amazon"],
    shape="arr", ret="long", todo="keep a running altitude starting at 0 and track its maximum, including the starting 0",
    description=(
        "A biker starts at altitude 0. The array gives the net gain in altitude between "
        "consecutive points of the trip. Print the highest altitude reached (the start counts).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` gains.\n\n"
        "### Output\nThe highest altitude."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^4 ≤ gain ≤ 10^4",
    hints=[
        "The altitude at each point is a prefix sum of the gains.",
        "The answer is the largest prefix sum — but the empty prefix (altitude 0) is also a point on the trip.",
        "Start the maximum at 0, not at the first gain.",
    ],
    opt=("O(n)", "O(1)", "One running sum and one maximum."),
    editorial=(
        "## The one thing this teaches\n**Prefix sums have an empty prefix.** The altitude "
        "sequence is `0, g0, g0 + g1, …`. Forgetting the leading 0 gives the wrong answer "
        "whenever every gain is negative.\n\n"
        "## Approach\n```java\nlong altitude = 0, best = 0;\nfor (int g : gains) {\n"
        "    altitude += g;\n    best = Math.max(best, altitude);\n}\nreturn best;\n```\n\n"
        "## Walkthrough: −5 1 5 0 −7\nAltitudes 0, −5, −4, 1, 1, −6. The highest is 1.\n\n"
        "## The same off-by-one elsewhere\nSubarray-sum problems store prefix 0 at index −1 for "
        "the same reason: a subarray may start at the very beginning."
    ),
    py='''
def solve(a):
    from itertools import accumulate
    return max([0] + list(accumulate(a)))
''',
    java='''
    static long solve(int[] gains) {
        long altitude = 0, best = 0;
        for (int g : gains) {
            altitude += g;
            best = Math.max(best, altitude);
        }
        return best;
    }
''',
    examples=[("Example 1", "5\n-5 1 5 0 -7\n"), ("Example 2", "7\n-4 -3 -2 -1 4 3 2\n")],
    hidden=[
        ("All negative", "3\n-1 -2 -3\n"),
        ("All positive", "3\n1 2 3\n"),
        ("Peak in the middle", "4\n10000 10000 -30000 5\n"),
    ],
    expl=[
        "Altitudes 0, −5, −4, 1, 1, −6: the highest is 1.",
        "Altitudes fall to −10 and climb back to exactly 0, which the start already reached.",
    ],
    prereqs=[
        ("prefix_sum", "Running sums, starting from the empty prefix."),
        ("prefix_max", "Tracking the maximum of a running value."),
    ],
)

_p(
    "xor-queries-subarray", "XOR Queries of a Subarray", "Medium",
    topics=["Bit Manipulation", "Prefix Sums"], subtopics=["Prefix XOR"], companies=["Airtel"],
    shape="arr_q", ret="String", todo="P[i + 1] = P[i] ^ a[i]; the XOR of a[l..r] is P[r + 1] ^ P[l]",
    description=(
        "Answer each query `l r` with the XOR of `a[l] ^ a[l+1] ^ … ^ a[r]` (0-indexed, "
        "inclusive).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n- Line 3: `q`.\n- Next `q` lines: `l r`.\n\n"
        "### Output\n`q` lines: the answers."
    ),
    constraints="1 ≤ n, q ≤ 3·10^4\n1 ≤ a[i] ≤ 10^9\n0 ≤ l ≤ r < n",
    hints=[
        "XOR-ing each range directly is O(n) per query.",
        "Prefix sums answer range sums with one subtraction because subtraction undoes addition. What undoes XOR?",
        "XOR is its own inverse: x ^ x = 0. So with P[i] = a[0] ^ … ^ a[i − 1], the range XOR is P[r + 1] ^ P[l].",
    ],
    opt=("O(n + q)", "O(n)", "One prefix pass, then O(1) per query."),
    editorial=(
        "## The one thing this teaches\n**Prefix sums work for any operation with an inverse.** "
        "Addition has subtraction; XOR is its own inverse. Everything before `l` appears in both "
        "`P[r + 1]` and `P[l]` and cancels.\n\n"
        "## Approach\n```java\nint[] P = new int[n + 1];\nfor (int i = 0; i < n; i++) P[i + 1] = P[i] ^ a[i];\n"
        "for (int[] q : queries) output(P[q[1] + 1] ^ P[q[0]]);\n```\n\n"
        "## Why it cancels\n`P[r + 1] = (a0 ^ … ^ a(l−1)) ^ (al ^ … ^ ar)` and `P[l] = a0 ^ … ^ a(l−1)`. "
        "XOR-ing them leaves `al ^ … ^ ar`.\n\n"
        "## What does not work\nRange maximum has no inverse — knowing the maximum of a prefix "
        "and of a longer prefix does not reveal the maximum of the difference. That needs a "
        "sparse table or a segment tree."
    ),
    py='''
def solve(a, queries):
    out = []
    for l, r in queries:
        x = 0
        for v in a[l:r + 1]:
            x ^= v
        out.append(str(x))
    return "\\n".join(out)
''',
    java='''
    static String solve(int[] a, int[][] queries) {
        int n = a.length;
        int[] P = new int[n + 1];
        for (int i = 0; i < n; i++) P[i + 1] = P[i] ^ a[i];
        StringBuilder sb = new StringBuilder();
        for (int[] q : queries) {
            if (sb.length() > 0) sb.append('\\n');
            sb.append(P[q[1] + 1] ^ P[q[0]]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "4\n1 3 4 8\n4\n0 1\n1 2\n0 3\n3 3\n"),
        ("Example 2", "4\n4 8 2 10\n4\n2 3\n1 3\n0 0\n0 3\n"),
    ],
    hidden=[
        ("Single element", "1\n7\n1\n0 0\n"),
        ("Pairs cancel", "4\n5 5 5 5\n3\n0 1\n0 2\n0 3\n"),
        ("Large values", "3\n1000000000 999999999 123456789\n2\n0 2\n1 2\n"),
    ],
    expl=[
        "1 ^ 3 = 2, 3 ^ 4 = 7, 1 ^ 3 ^ 4 ^ 8 = 14, and 8.",
        "2 ^ 10 = 8, 8 ^ 2 ^ 10 = 0, 4, and 4 ^ 8 ^ 2 ^ 10 = 4.",
    ],
    prereqs=[
        ("bit_manip", "XOR as its own inverse."),
        ("prefix_sum", "Range queries from prefix values and an inverse operation."),
    ],
)

_p(
    "number-complement", "Number Complement", "Easy",
    topics=["Bit Manipulation"], subtopics=["Masks"], companies=["Cloudera"],
    shape="n", ret="long", todo="build a mask of 1s as wide as n's binary representation and XOR n with it",
    description=(
        "The **complement** of a positive integer flips every bit of its binary representation, "
        "ignoring leading zeros — `5` is `101`, whose complement `010` is `2`. Print the "
        "complement of `n`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe complement."
    ),
    constraints="1 ≤ n < 2^31",
    hints=[
        "~n flips all 32 or 64 bits, including the leading zeros — too many.",
        "XOR with 1 flips a bit. XOR with a mask of ones flips exactly the bits covered by the mask.",
        "The mask is 2^L − 1 where L is the bit length of n: shift a 1 left until it exceeds n, then subtract 1.",
    ],
    opt=("O(log n)", "O(1)", "At most 31 shifts to size the mask."),
    editorial=(
        "## The one thing this teaches\n**Masks select which bits an operation touches.** Bitwise "
        "NOT flips everything. Combining XOR with a mask of exactly the right width flips only "
        "the meaningful bits.\n\n"
        "## Approach\n```java\nlong mask = 1;\nwhile (mask <= n) mask <<= 1;     // smallest power of two above n\n"
        "mask -= 1;                         // ones in every position n uses\nreturn n ^ mask;\n```\n\n"
        "## Walkthrough: n = 10\n`1010` has 4 bits, so the mask is `1111`. `1010 ^ 1111 = 0101` = 5.\n\n"
        "## Library help\n`Integer.highestOneBit(n)` gives the top bit directly: the mask is "
        "`(highestOneBit(n) << 1) − 1`. Use long, since for n near 2^31 the shift passes an int."
    ),
    py='''
def solve(n):
    bits = bin(n)[2:]
    flipped = "".join("1" if b == "0" else "0" for b in bits)
    return int(flipped, 2)
''',
    java='''
    static long solve(long n) {
        long mask = 1;
        while (mask <= n) mask <<= 1;
        mask -= 1;
        return n ^ mask;
    }
''',
    examples=[("Example 1", "5\n"), ("Example 2", "1\n")],
    hidden=[
        ("All ones", "7\n"),
        ("Alternating", "10\n"),
        ("Largest", "2147483647\n"),
        ("Large", "1000000000\n"),
    ],
    expl=[
        "101 → 010 = 2.",
        "1 → 0.",
    ],
    prereqs=[
        ("bit_manip", "XOR with a mask, and shifting to size the mask."),
        ("overflow", "The mask for values near 2^31 needs a long."),
    ],
)

_p(
    "max-product-after-k-increments", "Maximum Product After K Increments", "Medium",
    topics=["Heaps", "Greedy", "Math"], subtopics=["Always Raise the Minimum"], companies=["Amazon"],
    shape="arr_k", ret="long", todo="k times: pop the smallest value, add 1, push it back; then multiply everything modulo 10^9 + 7",
    description=(
        "You may perform at most `k` operations; each adds 1 to one element. Print the maximum "
        "possible product of all elements, modulo `10^9 + 7` (maximise the true product, then "
        "take the remainder).\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` non-negative integers.\n\n"
        "### Output\nThe maximum product modulo 10^9 + 7."
    ),
    constraints="1 ≤ n, k ≤ 10^5\n0 ≤ a[i] ≤ 10^6",
    hints=[
        "Adding 1 to x multiplies the product by (x + 1) / x. That ratio is largest when x is smallest.",
        "So each increment should go to the current minimum — a min-heap gives it in O(log n).",
        "Reduce modulo 10^9 + 7 only when multiplying at the end: comparing values must use the real numbers, not remainders.",
    ],
    opt=("O((n + k) log n)", "O(n)", "k heap updates, then one multiplication pass."),
    editorial=(
        "## The one thing this teaches\n**Greedy by marginal gain.** Each unit of budget should go "
        "where it helps most right now. For a product, raising x by one gains a factor "
        "`1 + 1/x` — biggest for the smallest x, and still smallest-first after every step.\n\n"
        "## Approach\n```java\nPriorityQueue<Long> heap = new PriorityQueue<>();\nfor (int x : a) heap.add((long) x);\n"
        "for (int i = 0; i < k; i++) heap.add(heap.poll() + 1);\nlong product = 1;\n"
        "for (long x : heap) product = product * (x % MOD) % MOD;\n```\n\n"
        "## Why never reduce the heap values modulo\nThe heap compares actual magnitudes. Values "
        "stay below 1.1·10^6 anyway; only the product is reduced.\n\n"
        "## The water-filling view\nThe greedy raises the smallest values to a common level L and "
        "then gives the leftover increments to some of the elements at L — computable directly "
        "with a sort, without k heap operations."
    ),
    py='''
def solve(a, k):
    MOD = 10**9 + 7
    vals = sorted(a)
    lo, hi = vals[0], vals[0] + k
    while lo < hi:                      # highest common level reachable with k increments
        mid = (lo + hi + 1) // 2
        if sum(max(0, mid - v) for v in vals) <= k:
            lo = mid
        else:
            hi = mid - 1
    level = lo
    leftover = k - sum(max(0, level - v) for v in vals)
    raised = [max(v, level) for v in vals]
    for i in range(len(raised)):
        if leftover and raised[i] == level:
            raised[i] += 1
            leftover -= 1
    product = 1
    for v in raised:
        product = product * v % MOD
    return product
''',
    java='''
    static long solve(int[] a, long kk) {
        final long MOD = 1_000_000_007L;
        PriorityQueue<Long> heap = new PriorityQueue<>();
        for (int x : a) heap.add((long) x);
        for (long i = 0; i < kk; i++) heap.add(heap.poll() + 1);
        long product = 1;
        for (long x : heap) product = product * (x % MOD) % MOD;
        return product;
    }
''',
    examples=[("Example 1", "2 5\n0 4\n"), ("Example 2", "4 2\n6 3 3 2\n")],
    hidden=[
        ("Single zero", "1 3\n0\n"),
        ("Equal values", "3 3\n1 1 1\n"),
        ("Product needs the modulus", "2 1\n1000000 1000000\n"),
        ("Six values", "6 54\n24 5 64 53 26 38\n"),
    ],
    expl=[
        "Five increments on 0 make 5 · 4 = 20.",
        "Raise 2 to 3 and one 3 to 4: 6 · 4 · 3 · 3 = 216.",
    ],
    prereqs=[
        ("heap", "A min-heap that repeatedly exposes the smallest value."),
        ("modulo", "Reducing a product modulo 10^9 + 7 without affecting comparisons."),
    ],
)

_p(
    "maximum-level-sum", "Maximum Level Sum of a Binary Tree", "Medium",
    topics=["Trees", "BFS"], subtopics=["Level Order"], companies=["Amazon", "Microsoft"],
    shape="tree", ret="int", todo="sum the values level by level (root is level 1); keep the first level with the strictly largest sum",
    description=(
        "The root is at level 1, its children at level 2, and so on. Print the **smallest** level "
        "whose values have the largest sum.\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child.\n\n"
        "### Output\nThe level number."
    ),
    constraints="1 ≤ nodes ≤ 10^4\n-10^5 ≤ value ≤ 10^5",
    hints=[
        "Level-order traversal visits one level at a time.",
        "Sum each level; values can be negative, so start the best sum at the smallest possible value, not 0.",
        "Replace the best only on a strictly larger sum, so ties keep the smaller level.",
    ],
    opt=("O(n)", "O(w)", "One BFS; the queue holds at most one level (w nodes)."),
    editorial=(
        "## The one thing this teaches\n**Process a BFS queue one level at a time.** Recording "
        "the queue size before draining it separates the levels without storing depths.\n\n"
        "## Approach\n```java\nlong best = Long.MIN_VALUE;\nint bestLevel = 0, level = 0;\n"
        "Deque<TreeNode> q = new ArrayDeque<>(List.of(root));\nwhile (!q.isEmpty()) {\n    level++;\n    long sum = 0;\n"
        "    for (int size = q.size(); size > 0; size--) {\n        TreeNode t = q.poll();\n        sum += t.val;\n"
        "        if (t.left != null) q.add(t.left);\n        if (t.right != null) q.add(t.right);\n    }\n"
        "    if (sum > best) { best = sum; bestLevel = level; }\n}\n```\n\n"
        "## Negative sums\nIn a tree whose values are all negative, starting `best` at 0 would "
        "never update and report level 0.\n\n"
        "## The DFS alternative\nA DFS that passes the depth and adds each value to `sums[depth]` "
        "gives the same per-level totals."
    ),
    py='''
def solve(root):
    sums = []
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth == len(sums):
            sums.append(0)
        sums[depth] += node.val
        for child in (node.left, node.right):
            if child:
                stack.append((child, depth + 1))
    best = max(sums)
    return sums.index(best) + 1
''',
    java='''
    static int solve(TreeNode root) {
        long best = Long.MIN_VALUE;
        int bestLevel = 0, level = 0;
        ArrayDeque<TreeNode> q = new ArrayDeque<>();
        q.add(root);
        while (!q.isEmpty()) {
            level++;
            long sum = 0;
            for (int size = q.size(); size > 0; size--) {
                TreeNode t = q.poll();
                sum += t.val;
                if (t.left != null) q.add(t.left);
                if (t.right != null) q.add(t.right);
            }
            if (sum > best) { best = sum; bestLevel = level; }
        }
        return bestLevel;
    }
''',
    examples=[
        ("Example 1", "1 7 0 7 -8 null null\n"),
        ("Example 2", "989 null 10250 98693 -89388 null null null -32127\n"),
    ],
    hidden=[
        ("Single node", "-5\n"),
        ("All negative", "-1 -2 -3\n"),
        ("Tie keeps the first", "3 1 2\n"),
        ("Deep best level", "1 2 3 4 5 6 7\n"),
    ],
    expl=[
        "Level sums: 1, 7, −1. Level 2 is largest.",
        "Level sums: 989, 10250, 9305, −32127. Level 2 is largest.",
    ],
    prereqs=[
        ("bfs", "Level-order traversal that drains one level per iteration."),
        ("tree_traversal", "Collecting a value per depth."),
    ],
)

_p(
    "max-length-unique-concatenation", "Maximum Length of a Concatenated String with Unique Characters", "Medium",
    topics=["Backtracking", "Bit Manipulation"], subtopics=["Bitmask Subsets"], companies=["Microsoft", "Amazon"],
    shape="words", ret="int", todo="drop words with repeated letters; DFS over words carrying the used-letter mask, adding a word only if its mask is disjoint",
    description=(
        "Choose some of the words (in their given order, each at most once) and concatenate them. "
        "The result must contain **no repeated letter**. Print the maximum possible length.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` words.\n\n"
        "### Output\nThe maximum length."
    ),
    constraints="1 ≤ n ≤ 16\n1 ≤ word length ≤ 26\nLowercase English letters",
    hints=[
        "Order does not affect which letters are used, so this is a choice of a subset of words.",
        "A word that repeats a letter internally can never be used. Every other word is a 26-bit letter mask.",
        "DFS through the words, carrying the mask of letters used. Include a word only if its mask AND the current mask is 0.",
    ],
    opt=("O(2^n)", "O(n)", "At most 2^n subsets, each extension an O(1) mask test."),
    editorial=(
        "## The one thing this teaches\n**Subsets of small sets are bitmasks, and so are sets of "
        "letters.** The search is over subsets of words; the constraint is on sets of letters. "
        "Representing both as bits makes each check a single AND.\n\n"
        "## Approach\n```java\nList<Integer> masks = new ArrayList<>();          // words with distinct letters only\n"
        "int best = 0;\nvoid dfs(int i, int used) {\n    best = Math.max(best, Integer.bitCount(used));\n"
        "    for (int j = i; j < masks.size(); j++)\n        if ((masks.get(j) & used) == 0) dfs(j + 1, used | masks.get(j));\n}\n```\n\n"
        "## Length from the mask\nSince no letter repeats, the concatenation's length is the "
        "number of set bits in `used` — no strings need to be built.\n\n"
        "## The iterative version\nStart with a list `[0]`. For each valid word mask, append "
        "`m | w` for every existing mask `m` disjoint from `w`. The list holds every reachable "
        "letter set."
    ),
    py='''
def solve(words):
    from itertools import combinations
    best = 0
    for size in range(len(words) + 1):
        for chosen in combinations(words, size):
            s = "".join(chosen)
            if len(set(s)) == len(s):
                best = max(best, len(s))
    return best
''',
    java='''
    static int best;
    static List<Integer> masks;

    static void dfs(int i, int used) {
        best = Math.max(best, Integer.bitCount(used));
        for (int j = i; j < masks.size(); j++)
            if ((masks.get(j) & used) == 0) dfs(j + 1, used | masks.get(j));
    }

    static int solve(String[] words) {
        masks = new ArrayList<>();
        for (String w : words) {
            int m = 0;
            boolean ok = true;
            for (char ch : w.toCharArray()) {
                int bit = 1 << (ch - 'a');
                if ((m & bit) != 0) { ok = false; break; }
                m |= bit;
            }
            if (ok) masks.add(m);
        }
        best = 0;
        dfs(0, 0);
        return best;
    }
''',
    examples=[
        ("Example 1", "3\nun iq ue\n"),
        ("Example 2", "4\ncha r act ers\n"),
        ("Example 3", "1\nabcdefghijklmnopqrstuvwxyz\n"),
    ],
    hidden=[
        ("Words with repeats", "2\naa bb\n"),
        ("Overlapping pair", "3\nab ba cd\n"),
        ("Single letters", "5\na b c a b\n"),
        ("Choose the longer", "3\nabcd ae fgh\n"),
    ],
    expl=[
        "un + iq or iq + ue: length 4.",
        "cha + ers or act + ers: length 6.",
        "The single word already uses every letter once.",
    ],
    prereqs=[
        ("backtracking", "Subset enumeration by DFS with a start index."),
        ("bit_manip", "Letter sets as 26-bit masks, tested with AND and counted with bitCount."),
    ],
)

_p(
    "min-vertices-reach-all", "Minimum Number of Vertices to Reach All Nodes", "Medium",
    topics=["Graphs", "Topological Sort"], subtopics=["In-Degree"], companies=["Google"],
    shape="graph", ret="String", todo="a node must be chosen exactly when nothing points to it; print the in-degree-0 nodes in increasing order",
    description=(
        "A directed acyclic graph has nodes `0` to `n − 1`. Print the smallest set of nodes from "
        "which every node is reachable, in increasing order. (This set is unique.)\n\n"
        "### Input\n- Line 1: `n m`.\n- Next `m` lines: `u v`, an edge from `u` to `v`.\n\n"
        "### Output\nThe nodes, separated by spaces."
    ),
    constraints="2 ≤ n ≤ 10^5\n1 ≤ m ≤ 10^5\nThe graph is acyclic",
    hints=[
        "A node with an incoming edge can be reached from its predecessor.",
        "A node with no incoming edge cannot be reached from anywhere else — it has to be chosen.",
        "In a DAG, every node is reachable from some in-degree-0 node. So the answer is exactly the set of nodes with in-degree 0.",
    ],
    opt=("O(n + m)", "O(n)", "One pass over edges to mark targets."),
    editorial=(
        "## The one thing this teaches\n**Sometimes the whole answer is a degree count.** No "
        "search is needed: nodes without incoming edges are forced into the set, and in an "
        "acyclic graph they already reach everything.\n\n"
        "## Approach\n```java\nboolean[] hasIncoming = new boolean[n];\nfor (int[] e : edges) hasIncoming[e[1]] = true;\n"
        "for (int v = 0; v < n; v++) if (!hasIncoming[v]) output(v);\n```\n\n"
        "## Why these suffice\nWalk backwards from any node along incoming edges. With no "
        "cycles, the walk cannot go on forever, so it stops at a node with no incoming edge — "
        "which then reaches the starting node.\n\n"
        "## Where cycles would break it\nIn a directed cycle every node has in-degree ≥ 1, yet "
        "one of them must still be chosen. Handling that needs strongly connected components."
    ),
    py='''
def solve(n, edges):
    targets = {v for _, v in edges}
    return " ".join(str(v) for v in range(n) if v not in targets)
''',
    java='''
    static String solve(int n, int[][] edges) {
        boolean[] hasIncoming = new boolean[n];
        for (int[] e : edges) hasIncoming[e[1]] = true;
        StringBuilder sb = new StringBuilder();
        for (int v = 0; v < n; v++)
            if (!hasIncoming[v]) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6 5\n0 1\n0 2\n2 5\n3 4\n4 2\n"),
        ("Example 2", "5 5\n0 1\n2 1\n3 1\n1 4\n2 4\n"),
    ],
    hidden=[
        ("Chain", "4 3\n0 1\n1 2\n2 3\n"),
        ("Reverse chain", "4 3\n3 2\n2 1\n1 0\n"),
        ("Isolated node", "3 1\n0 1\n"),
    ],
    expl=[
        "0 reaches 1, 2 and 5; 3 reaches 4 (and 2). Nothing reaches 0 or 3.",
        "0, 2 and 3 have no incoming edges; together they reach 1 and 4.",
    ],
    prereqs=[
        ("topo", "In-degrees, and why in a DAG every node traces back to a source."),
        ("graph_repr", "Scanning an edge list without building adjacency."),
    ],
)

_p(
    "similar-string-groups", "Similar String Groups", "Hard",
    topics=["Union-Find", "Strings", "Graphs"], subtopics=["Connected Components"], companies=["Google"],
    shape="words", ret="int", todo="union every pair of words that are equal or differ in exactly two positions; count the components",
    description=(
        "All words are anagrams of each other. Two words are **similar** if they are equal or "
        "swapping two letters of one gives the other. Groups are formed by chains of similarity: "
        "a word belongs to a group if it is similar to at least one word in it. Print the number "
        "of groups.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` words.\n\n"
        "### Output\nThe number of groups."
    ),
    constraints="1 ≤ n ≤ 300\n1 ≤ word length ≤ 300\nAll words are anagrams of each other",
    hints=[
        "\"Groups formed by chains\" means connected components of a graph whose edges are similar pairs.",
        "Because the words are anagrams, two words are similar exactly when they differ in 0 or 2 positions.",
        "Compare every pair (O(n² · L)) and union similar ones; the number of components is the answer.",
    ],
    opt=("O(n² · L · α(n))", "O(n)", "All pairs compared once, with union-find for the components."),
    editorial=(
        "## The one thing this teaches\n**Transitive grouping is connected components.** \"Similar\" "
        "is not transitive — `tars ~ rats ~ arts`, yet `tars` and `arts` differ in more than a "
        "swap. Groups are the closure of the relation, which is what union-find computes.\n\n"
        "## Approach\n```java\nfor (int i = 0; i < n; i++)\n    for (int j = i + 1; j < n; j++)\n"
        "        if (similar(words[i], words[j]) && union(i, j)) groups--;\n\n"
        "boolean similar(String a, String b) {\n    int diff = 0;\n"
        "    for (int k = 0; k < a.length(); k++)\n        if (a.charAt(k) != b.charAt(k) && ++diff > 2) return false;\n"
        "    return diff == 0 || diff == 2;\n}\n```\n\n"
        "## Why two differences mean one swap\nThe words are anagrams, so if they differ in exactly "
        "positions i and j, the letters there must be `(x, y)` and `(y, x)` — a swap.\n\n"
        "## Stopping early\nThe comparison returns as soon as a third difference appears, which "
        "keeps most pair checks far below O(L)."
    ),
    py='''
def solve(words):
    from collections import deque
    n = len(words)

    def similar(a, b):
        diffs = [k for k in range(len(a)) if a[k] != b[k]]
        return not diffs or (len(diffs) == 2 and a[diffs[0]] == b[diffs[1]] and a[diffs[1]] == b[diffs[0]])

    seen = [False] * n
    groups = 0
    for s in range(n):
        if seen[s]:
            continue
        groups += 1
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for v in range(n):
                if not seen[v] and similar(words[u], words[v]):
                    seen[v] = True
                    q.append(v)
    return groups
''',
    java='''
    static int find(int[] p, int x) {
        while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; }
        return x;
    }

    static boolean similar(String a, String b) {
        int diff = 0;
        for (int k = 0; k < a.length(); k++)
            if (a.charAt(k) != b.charAt(k) && ++diff > 2) return false;
        return diff == 0 || diff == 2;
    }

    static int solve(String[] words) {
        int n = words.length, groups = n;
        int[] parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (similar(words[i], words[j])) {
                    int a = find(parent, i), b = find(parent, j);
                    if (a != b) { parent[a] = b; groups--; }
                }
        return groups;
    }
''',
    examples=[("Example 1", "4\ntars rats arts star\n"), ("Example 2", "2\nomv ovm\n")],
    hidden=[
        ("One word", "1\nabc\n"),
        ("Chain through a middle word", "3\nabc acb bca\n"),
        ("Identical words", "3\nab ab ab\n"),
        ("All separate", "3\nabcd badc cdab\n"),
    ],
    expl=[
        "tars ~ rats ~ arts form one group; star is similar to none of them.",
        "Swapping the last two letters of omv gives ovm.",
    ],
    prereqs=[
        ("union_find", "Merging similar pairs and counting components."),
        ("string_basics", "Comparing two strings position by position with an early exit."),
    ],
)

_p(
    "maximum-swap", "Maximum Swap", "Medium",
    topics=["Greedy", "Math"], subtopics=["Digits"], companies=["Meta", "Google"],
    shape="n", ret="long", todo="record the last position of each digit; at the first position where a larger digit appears later, swap with that digit's last occurrence",
    description=(
        "You may swap two digits of `n` **at most once**. Print the largest number you can get.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe largest possible number."
    ),
    constraints="0 ≤ n ≤ 10^8",
    hints=[
        "Trying all pairs of positions is O(L²) — tiny here, but the greedy is instructive.",
        "The earliest position that can be improved should be improved, with the largest digit that appears after it.",
        "If that largest digit appears several times later, swap with its LAST occurrence — that keeps a larger digit earlier.",
    ],
    opt=("O(L)", "O(1)", "A 10-entry table of last positions and one scan over L digits."),
    editorial=(
        "## The one thing this teaches\n**Greedy on the most significant position first.** A "
        "digit further left outweighs everything to its right, so the swap must fix the first "
        "position that can grow — and grow it as much as possible.\n\n"
        "## Approach\n```java\nchar[] d = String.valueOf(n).toCharArray();\nint[] last = new int[10];\n"
        "for (int i = 0; i < d.length; i++) last[d[i] - '0'] = i;\n"
        "for (int i = 0; i < d.length; i++)\n    for (int big = 9; big > d[i] - '0'; big--)\n"
        "        if (last[big] > i) {                    // a larger digit appears later\n"
        "            swap(d, i, last[big]);\n            return Long.parseLong(new String(d));\n        }\nreturn n;\n```\n\n"
        "## Why the last occurrence\nIn `1993`, swapping the 1 with the *first* 9 gives `9193`; "
        "with the last 9 it gives `9913`. The earlier 9 stays in front.\n\n"
        "## No beneficial swap\nIf the digits never increase from left to right, the number is "
        "already the largest arrangement reachable with one swap."
    ),
    py='''
def solve(n):
    digits = list(str(n))
    best = n
    for i in range(len(digits)):
        for j in range(i + 1, len(digits)):
            d = digits[:]
            d[i], d[j] = d[j], d[i]
            best = max(best, int("".join(d)))
    return best
''',
    java='''
    static long solve(long n) {
        char[] d = String.valueOf(n).toCharArray();
        int[] last = new int[10];
        for (int i = 0; i < d.length; i++) last[d[i] - '0'] = i;
        for (int i = 0; i < d.length; i++)
            for (int big = 9; big > d[i] - '0'; big--)
                if (last[big] > i) {
                    char t = d[i]; d[i] = d[last[big]]; d[last[big]] = t;
                    return Long.parseLong(new String(d));
                }
        return n;
    }
''',
    examples=[("Example 1", "2736\n"), ("Example 2", "9973\n")],
    hidden=[
        ("Zero", "0\n"),
        ("Last occurrence", "1993\n"),
        ("Middle swap", "98368\n"),
        ("Zero digit", "10\n"),
        ("Largest input", "100000000\n"),
    ],
    expl=[
        "Swap 2 and 7.",
        "The digits never increase, so no swap helps.",
    ],
    prereqs=[
        ("greedy", "Improving the most significant position first."),
        ("math_digits", "Digits as characters, with a table of last positions."),
    ],
)
