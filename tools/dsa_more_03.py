# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 3 — prefix sums, sorting, bits.
#
#   pivot-index                    total − left − a[i] is the right sum; no second array
#   contiguous-array               ±1 turns "equal counts" into "prefix seen before"
#   subarray-sums-divisible-k      prefix sums modulo k, with a non-negative modulus
#   range-addition                 a difference array: O(1) per update, one prefix pass
#   custom-sort-string             sorting by a rank you were given
#   largest-number                 a comparator that compares concatenations
#   h-index                        sorted descending, the answer is where rank passes value
#   best-meeting-point-line        the median minimises total absolute distance
#   single-number-iii              split by one differing bit
# ===========================================================================

_p(
    "pivot-index", "Find Pivot Index", "Easy",
    topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum"], companies=["Amazon", "Adobe"],
    shape="arr", ret="int", todo="walk with a running left sum; the right sum is total − left − a[i]",
    description=(
        "Find the **leftmost** index `i` where the sum of the elements strictly to its left equals "
        "the sum of the elements strictly to its right. An empty side sums to 0.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe pivot index, or `-1` if there is none."
    ),
    constraints="1 ≤ n ≤ 10^4\n-1000 ≤ a[i] ≤ 1000",
    hints=[
        "Recomputing both sides for every i is O(n²).",
        "Compute the total once. Then, walking left to right, keep the sum of everything before i.",
        "The right sum is total − left − a[i]. Update left AFTER the comparison.",
    ],
    opt=("O(n)", "O(1)", "One pass for the total and one with a running left sum."),
    editorial=(
        "## The one thing this teaches\n**A total plus a running prefix gives you both sides.** "
        "You do not need a prefix array *and* a suffix array: the suffix is whatever the total "
        "has left after the prefix and the current element.\n\n"
        "## Approach\n```java\nlong total = 0, left = 0;\nfor (int x : a) total += x;\n"
        "for (int i = 0; i < n; i++) {\n"
        "    if (left == total - left - a[i]) return i;\n    left += a[i];\n}\nreturn -1;\n```\n\n"
        "## Order of operations\nThe comparison must happen *before* `a[i]` joins the left sum — "
        "otherwise the element is counted on the left side of itself. With negative numbers "
        "there can be several pivots, which is why \"leftmost\" is in the statement, and why the "
        "loop returns at the first one."
    ),
    py='''
def solve(a):
    total = sum(a)
    left = 0
    for i, x in enumerate(a):
        if left == total - left - x:
            return i
        left += x
    return -1
''',
    java='''
    static int solve(int[] a) {
        long total = 0, left = 0;
        for (int x : a) total += x;
        for (int i = 0; i < a.length; i++) {
            if (left == total - left - a[i]) return i;
            left += a[i];
        }
        return -1;
    }
''',
    examples=[("Example 1", "6\n1 7 3 6 5 6\n"), ("Example 2", "3\n1 2 3\n")],
    hidden=[
        ("Pivot at index 0", "3\n2 1 -1\n"),
        ("Single element", "1\n5\n"),
        ("Negatives", "4\n-1 -1 -1 0\n"),
        ("All zeros, leftmost wins", "5\n0 0 0 0 0\n"),
    ],
    expl=[
        "Left of index 3: 1 + 7 + 3 = 11. Right: 5 + 6 = 11.",
        "No index balances the two sides.",
    ],
    prereqs=[
        ("prefix_sum", "A running left sum, with the right sum derived from the total."),
        ("iteration", "Comparing before updating, so the current element belongs to neither side."),
    ],
)

_p(
    "contiguous-array", "Contiguous Array (Equal 0s and 1s)", "Medium",
    topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum", "Hashing"], companies=["Meta", "Amazon"],
    shape="arr", ret="int", todo="treat 0 as −1; record the first index of each prefix sum; a repeat bounds a balanced subarray",
    description=(
        "The array contains only `0`s and `1`s. Find the length of the longest contiguous "
        "subarray with **equally many 0s and 1s**.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` values, each 0 or 1.\n\n"
        "### Output\nThe maximum length, or 0 if there is none."
    ),
    constraints="1 ≤ n ≤ 10^5\na[i] ∈ {0, 1}",
    hints=[
        "Count a 1 as +1 and a 0 as −1. \"Equally many\" becomes \"sums to 0\".",
        "A subarray (i, j] sums to 0 exactly when the prefix sums at i and j are equal.",
        "Remember the FIRST index at which each prefix sum occurs; a later repeat gives the longest span. Seed sum 0 at index −1.",
    ],
    opt=("O(n)", "O(n)", "One pass; the map holds at most 2n + 1 distinct prefix sums."),
    editorial=(
        "## The one thing this teaches\n**Re-encode until the question is one you know.** \"Equal "
        "numbers of 0s and 1s\" is not a prefix-sum question until 0 becomes −1. Then it is "
        "\"longest subarray summing to 0\", and a zero-sum subarray is two equal prefix sums.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> first = new HashMap<>();\nfirst.put(0, -1);\n"
        "int run = 0, best = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    run += a[i] == 1 ? 1 : -1;\n"
        "    Integer j = first.putIfAbsent(run, i);          // keeps the earliest index\n"
        "    if (j != null) best = Math.max(best, i - j);\n}\n```\n\n"
        "## First, not last\nFor the *longest* span ending at `i`, the other end should be as far "
        "left as possible — so each prefix sum's earliest index is the only one worth storing. "
        "Overwriting it with later indices (a plain `put`) finds balanced subarrays and returns "
        "the shortest ones. The `{0: -1}` seed covers subarrays starting at index 0.\n\n"
        "Since the sum stays in `[−n, n]`, an `int[2n + 1]` array works as the map."
    ),
    py='''
def solve(a):
    first = {0: -1}
    run = 0
    best = 0
    for i, x in enumerate(a):
        run += 1 if x == 1 else -1
        if run in first:
            best = max(best, i - first[run])
        else:
            first[run] = i
    return best
''',
    java='''
    static int solve(int[] a) {
        int n = a.length;
        int[] first = new int[2 * n + 1];
        Arrays.fill(first, -2);
        first[n] = -1;
        int run = 0, best = 0;
        for (int i = 0; i < n; i++) {
            run += a[i] == 1 ? 1 : -1;
            if (first[run + n] != -2) best = Math.max(best, i - first[run + n]);
            else first[run + n] = i;
        }
        return best;
    }
''',
    examples=[("Example 1", "2\n0 1\n"), ("Example 2", "3\n0 1 0\n")],
    hidden=[
        ("No zeros", "1\n1\n"),
        ("Long balanced middle", "8\n0 0 1 0 0 0 1 1\n"),
        ("Whole array", "4\n1 1 0 0\n"),
        ("Nothing balanced", "5\n1 1 1 1 1\n"),
    ],
    expl=[
        "The whole array has one 0 and one 1.",
        "`[0, 1]` or `[1, 0]` — length 2; all three elements are unbalanced.",
    ],
    prereqs=[
        ("prefix_sum", "Two equal prefix sums bound a subarray that sums to zero."),
        ("hashing", "A map from each prefix sum to the first index it appeared at."),
    ],
)

_p(
    "subarray-sums-divisible-k", "Subarray Sums Divisible by K", "Medium",
    topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum", "Counting"], companies=["Twilio", "Amazon"],
    shape="arr_k", ret="long", todo="count prefix sums by their (non-negative) remainder mod k; each repeat adds pairs",
    description=(
        "Count the contiguous subarrays whose sum is divisible by `k`.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers (possibly negative).\n\n"
        "### Output\nThe number of such subarrays."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n-10^4 ≤ a[i] ≤ 10^4\n2 ≤ k ≤ 10^4",
    hints=[
        "A subarray (i, j] has a sum divisible by k exactly when prefix[i] and prefix[j] have the same remainder mod k.",
        "Count how many prefixes have each remainder so far; a new prefix pairs with every earlier one sharing its remainder.",
        "In Java, `-3 % 5` is −3, not 2. Use `Math.floorMod`, or two prefixes that should match will not.",
    ],
    opt=("O(n + k)", "O(k)", "One pass with a k-slot count array of remainders."),
    editorial=(
        "## The one thing this teaches\n**Equal remainders, not equal sums.** `(prefix[j] − "
        "prefix[i]) mod k == 0` is the same statement as `prefix[j] ≡ prefix[i] (mod k)`, so the "
        "\"subarray sum equals K\" technique carries over with the map keyed by remainder.\n\n"
        "## Approach\n```java\nlong[] seen = new long[k];\nseen[0] = 1;                 // the empty prefix\n"
        "long run = 0, count = 0;\nfor (int x : a) {\n"
        "    run += x;\n    int r = Math.floorMod(run, k);\n"
        "    count += seen[r];\n    seen[r]++;\n}\n```\n\n"
        "## The negative remainder\nJava's `%` keeps the sign of the dividend, so a running sum of "
        "−3 has remainder −3 while one of 2 has remainder 2 — the same class mod 5, stored in two "
        "different slots, and never counted as a pair. With negatives in the input this is the "
        "only bug that matters. `Math.floorMod` always returns a value in `[0, k)`."
    ),
    py='''
def solve(a, k):
    seen = [0] * k
    seen[0] = 1
    run = 0
    count = 0
    for x in a:
        run += x
        r = run % k
        count += seen[r]
        seen[r] += 1
    return count
''',
    java='''
    static long solve(int[] a, long k) {
        int kk = (int) k;
        long[] seen = new long[kk];
        seen[0] = 1;
        long run = 0, count = 0;
        for (int x : a) {
            run += x;
            int r = (int) Math.floorMod(run, (long) kk);
            count += seen[r];
            seen[r]++;
        }
        return count;
    }
''',
    examples=[("Example 1", "6 5\n4 5 0 -2 -3 1\n"), ("Example 2", "1 9\n5\n")],
    hidden=[
        ("Every subarray", "3 2\n2 2 2\n"),
        ("Negatives change the remainder", "4 3\n-1 2 9 -3\n"),
        ("All multiples", "5 7\n7 7 7 7 7\n"),
        ("Negative total", "3 4\n-4 -8 -1\n"),
    ],
    expl=[
        "Seven subarrays, including `[5]`, `[0]`, `[5, 0]` and `[4, 5, 0, -2, -3, 1]`.",
        "5 is not divisible by 9.",
    ],
    prereqs=[
        ("prefix_sum", "Pairs of prefix sums with equal remainders bound divisible subarrays."),
        ("modulo", "A non-negative remainder (floorMod), so negative running sums land in the right class."),
    ],
)

_p(
    "range-addition", "Range Addition (Difference Array)", "Medium",
    topics=["Arrays", "Prefix Sum"], subtopics=["Prefix Sum"], companies=["Google"],
    shape="updates", ret="String", todo="add v at l and subtract it at r + 1, then take one prefix sum",
    description=(
        "An array of `n` zeros receives `q` updates. Update `l r v` adds `v` to every index from "
        "`l` to `r` inclusive (0-based). Print the final array.\n\n"
        "### Input\n- Line 1: `n q`.\n- Next `q` lines: `l r v`.\n\n"
        "### Output\nThe `n` final values, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n0 ≤ q ≤ 10^5\n0 ≤ l ≤ r < n\n-10^4 ≤ v ≤ 10^4",
    hints=[
        "Applying each update index by index is O(n·q) in the worst case.",
        "Record only where each update starts and stops: diff[l] += v, diff[r + 1] −= v.",
        "The final value at i is the prefix sum of diff up to i. Size diff as n + 1 so r + 1 is always valid.",
    ],
    opt=("O(n + q)", "O(n)", "O(1) per update, then a single prefix-sum pass."),
    editorial=(
        "## The one thing this teaches\n**The difference array is prefix sums run backwards.** A "
        "prefix sum turns point values into range totals; a difference array lets you write a "
        "*range* change as two *point* changes, and one prefix sum at the end turns them back.\n\n"
        "## Approach\n```java\nlong[] diff = new long[n + 1];\n"
        "for (int[] u : ups) { diff[u[0]] += u[2]; diff[u[1] + 1] -= u[2]; }\n"
        "long run = 0;\nfor (int i = 0; i < n; i++) { run += diff[i]; out[i] = run; }\n```\n\n"
        "## Why it works\nAfter the prefix sum, index `i` receives `v` from every update with "
        "`l ≤ i` (the `+v` has been passed) except those with `r + 1 ≤ i` (their `−v` has been "
        "passed too). That is exactly the updates covering `i`.\n\n"
        "## Where it shows up\nCar pooling, booking systems, \"maximum number of overlapping "
        "intervals\": whenever many ranges are added and the totals are read once, at the end. "
        "If totals must be read *between* updates, a Fenwick tree is the next step."
    ),
    py='''
def solve(n, ups):
    diff = [0] * (n + 1)
    for l, r, v in ups:
        diff[l] += v
        diff[r + 1] -= v
    out = []
    run = 0
    for i in range(n):
        run += diff[i]
        out.append(run)
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int n, int[][] ups) {
        long[] diff = new long[n + 1];
        for (int[] u : ups) { diff[u[0]] += u[2]; diff[u[1] + 1] -= u[2]; }
        StringBuilder sb = new StringBuilder();
        long run = 0;
        for (int i = 0; i < n; i++) {
            run += diff[i];
            if (i > 0) sb.append(' ');
            sb.append(run);
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "5 3\n1 3 2\n2 4 3\n0 2 -2\n"), ("Example 2", "3 1\n0 2 5\n")],
    hidden=[
        ("Updates cancel", "1 2\n0 0 4\n0 0 -4\n"),
        ("No updates", "4 0\n"),
        ("Point update inside a range", "6 2\n0 5 1\n3 3 10\n"),
        ("Update touching the last index", "3 2\n2 2 7\n1 2 1\n"),
    ],
    expl=[
        "After all three updates: `-2 0 3 5 3`.",
        "One update covering everything.",
    ],
    prereqs=[
        ("prefix_sum", "The final values are the running sum of the recorded start and stop changes."),
        ("array_patterns", "Writing a range change as two point changes in an array one longer than the data."),
    ],
)

_p(
    "custom-sort-string", "Custom Sort String", "Easy",
    topics=["Sorting", "Strings"], subtopics=["Sorting", "Counting"], companies=["Meta"],
    shape="str2", ret="String", todo="count t's letters; emit them in order's sequence, then the rest in t's order",
    description=(
        "`order` lists some distinct letters in a custom order. Rearrange `t` so that its letters "
        "that appear in `order` come first, in that order. Letters of `t` that are **not** in "
        "`order` follow, in the order they appear in `t`.\n\n"
        "### Input\n- Line 1: `order`.\n- Line 2: `t`.\n\n### Output\nThe rearranged string."
    ),
    constraints="1 ≤ |order| ≤ 26, letters distinct\n1 ≤ |t| ≤ 10^4\nBoth consist of lowercase English letters.",
    hints=[
        "Sorting with a comparator that looks up each letter's rank works, in O(|t| log |t|).",
        "Faster: count the letters of t. Walk `order` and emit each of its letters as many times as it occurs.",
        "Then walk t once more and emit the letters that `order` does not contain.",
    ],
    opt=("O(|order| + |t|)", "O(1)", "A 26-slot count array; the sort is a counting sort by the given ranks."),
    editorial=(
        "## The one thing this teaches\n**A custom order is just a rank.** Once each letter has a "
        "rank, you are sorting by a key — and with 26 keys, counting beats comparing.\n\n"
        "## Approach\n```java\nint[] count = new int[26];\nboolean[] ranked = new boolean[26];\n"
        "for (char c : t.toCharArray()) count[c - 'a']++;\nStringBuilder out = new StringBuilder();\n"
        "for (char c : order.toCharArray()) {\n    ranked[c - 'a'] = true;\n"
        "    for (int i = 0; i < count[c - 'a']; i++) out.append(c);\n}\n"
        "for (char c : t.toCharArray()) if (!ranked[c - 'a']) out.append(c);\n```\n\n"
        "## The comparator version\n`Arrays.sort` on a `Character[]` with "
        "`Comparator.comparingInt(c -> rank[c - 'a'])` also works, and because Java's object sort "
        "is **stable**, unranked letters (all given the same rank) keep their original relative "
        "order — which is exactly what the statement asks. The counting version makes that "
        "ordering explicit instead of relying on stability."
    ),
    py='''
def solve(s, t):
    order = s
    rank = set(order)
    count = Counter(t)
    out = [ch * count[ch] for ch in order]
    out += [ch for ch in t if ch not in rank]
    return "".join(out)
''',
    java='''
    static String solve(String order, String t) {
        int[] count = new int[26];
        boolean[] ranked = new boolean[26];
        for (int i = 0; i < t.length(); i++) count[t.charAt(i) - 'a']++;
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < order.length(); i++) {
            char c = order.charAt(i);
            ranked[c - 'a'] = true;
            for (int j = 0; j < count[c - 'a']; j++) out.append(c);
        }
        for (int i = 0; i < t.length(); i++) if (!ranked[t.charAt(i) - 'a']) out.append(t.charAt(i));
        return out.toString();
    }
''',
    examples=[("Example 1", "cba\nabcd\n"), ("Example 2", "bcafg\nabcd\n")],
    hidden=[
        ("Nothing ranked", "xyz\nabc\n"),
        ("Repeated letter", "a\naaaa\n"),
        ("Reverse order with repeats", "zyx\nxyzxyz\n"),
        ("Unranked letter keeps its place at the end", "ba\nabcab\n"),
    ],
    expl=[
        "`c`, `b`, `a` in the given order, then `d`, which is unranked.",
        "`b`, `c`, `a` come first; `d` follows.",
    ],
    prereqs=[
        ("sorting", "Ordering by a supplied rank, done here as a counting sort over 26 letters."),
        ("hashing", "A count per letter, and a marker for which letters have a rank at all."),
    ],
)

_p(
    "largest-number", "Largest Number", "Medium",
    topics=["Sorting", "Strings"], subtopics=["Sorting"], companies=["Amazon", "Microsoft"],
    shape="arr", ret="String", todo="sort the numbers as strings so that x goes first when x+y > y+x",
    description=(
        "Arrange non-negative integers so that, concatenated, they form the **largest** possible "
        "number. Print it without leading zeros.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` non-negative integers.\n\n"
        "### Output\nThe largest number, as a string."
    ),
    constraints="1 ≤ n ≤ 100\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "Numeric order fails: 10 before 2 gives 102, not 210. Plain string order also fails — try 3 and 30 both ways.",
        "Decide the order of two numbers directly: x should come first when the string x+y is larger than y+x.",
        "If the result starts with '0', every number was 0 — print a single 0.",
    ],
    opt=("O(n log n · L)", "O(n · L)", "A comparison sort where each comparison builds two strings of length up to 2L, L ≤ 10 digits."),
    editorial=(
        "## The one thing this teaches\n**When no key exists, compare pairs directly.** There is "
        "no per-number value that sorts these correctly. But for any two numbers you can ask "
        "which concatenation is larger, and that pairwise rule is a valid ordering.\n\n"
        "## Approach\n```java\nString[] s = new String[n];\nfor (int i = 0; i < n; i++) s[i] = String.valueOf(a[i]);\n"
        "Arrays.sort(s, (x, y) -> (y + x).compareTo(x + y));\n"
        "if (s[0].equals(\"0\")) return \"0\";\nreturn String.join(\"\", s);\n```\n\n"
        "Comparing the two concatenations as strings is safe because they have the same length, "
        "so lexicographic order is numeric order.\n\n"
        "## Why it is a valid sort\nA comparator must be transitive, or `Arrays.sort` can throw "
        "\"Comparison method violates its general contract\". This one is: `x+y ≥ y+x` is "
        "equivalent to `x / (10^|x| − 1) ≥ y / (10^|y| − 1)`, a comparison of real numbers. You do "
        "not need to prove that in an interview, but you should know the question exists.\n\n"
        "## The zeros\n`[0, 0]` concatenates to `\"00\"`. After sorting, the largest element is "
        "first, so if it is `\"0\"` everything is."
    ),
    py='''
def solve(a):
    from functools import cmp_to_key
    xs = [str(x) for x in a]
    xs.sort(key=cmp_to_key(lambda x, y: (x + y < y + x) - (x + y > y + x)))
    return "0" if xs[0] == "0" else "".join(xs)
''',
    java='''
    static String solve(int[] a) {
        String[] s = new String[a.length];
        for (int i = 0; i < a.length; i++) s[i] = String.valueOf(a[i]);
        Arrays.sort(s, (x, y) -> (y + x).compareTo(x + y));
        if (s[0].equals("0")) return "0";
        return String.join("", s);
    }
''',
    examples=[("Example 1", "2\n10 2\n"), ("Example 2", "5\n3 30 34 5 9\n")],
    hidden=[
        ("All zeros", "3\n0 0 0\n"),
        ("Single number", "1\n1\n"),
        ("Shared prefixes", "4\n824 8247 0 9\n"),
        ("Prefix of itself", "3\n121 12 0\n"),
    ],
    expl=[
        "`2` before `10`: 210 beats 102.",
        "9, 5, 34, 3, 30 → 9534330. `3` goes before `30` because 330 > 303.",
    ],
    prereqs=[
        ("sorting", "A comparator defined on pairs, used when no single sort key exists."),
        ("string_basics", "Comparing equal-length strings lexicographically, which matches numeric order."),
    ],
)

_p(
    "h-index", "H-Index", "Medium",
    topics=["Sorting", "Arrays"], subtopics=["Sorting", "Counting"], companies=["Google", "Bloomberg"],
    shape="arr", ret="int", todo="sort descending; h is the last rank i+1 with citations ≥ i+1",
    description=(
        "A researcher's **h-index** is the largest `h` such that they have at least `h` papers "
        "each cited at least `h` times. Given the citation counts, compute it.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` citation counts.\n\n### Output\nThe h-index."
    ),
    constraints="1 ≤ n ≤ 5000\n0 ≤ c[i] ≤ 1000",
    hints=[
        "Sort the counts in descending order. The paper at rank i (0-based) has i + 1 papers at least as cited as it.",
        "h is the largest i + 1 for which c[i] ≥ i + 1.",
        "O(n) version: h can never exceed n, so bucket the counts with anything above n in bucket n.",
    ],
    opt=("O(n)", "O(n)", "Counting sort into n + 1 buckets, then a scan from the top accumulating papers."),
    editorial=(
        "## The one thing this teaches\n**After sorting, rank is a count.** In descending order, "
        "position `i` tells you how many papers are at least as good as this one: `i + 1`. The "
        "definition of h compares exactly that count with the citations, so it becomes a scan.\n\n"
        "## Approach — counting sort\nh is at most `n`, so citations above `n` are "
        "indistinguishable from `n`:\n\n"
        "```java\nint[] bucket = new int[n + 1];\nfor (int c : cites) bucket[Math.min(c, n)]++;\n"
        "int papers = 0;\nfor (int h = n; h >= 0; h--) {\n"
        "    papers += bucket[h];                 // papers with at least h citations\n"
        "    if (papers >= h) return h;\n}\nreturn 0;\n```\n\n"
        "## The sort version\n`Arrays.sort` then walk from the largest: O(n log n) and just as "
        "correct. The counting version is worth showing because the cap at `n` is an argument "
        "about the *answer's* range, not the input's — the same move that makes binary search on "
        "the answer possible."
    ),
    py='''
def solve(a):
    c = sorted(a, reverse=True)
    h = 0
    for i, x in enumerate(c):
        if x >= i + 1:
            h = i + 1
        else:
            break
    return h
''',
    java='''
    static int solve(int[] cites) {
        int n = cites.length;
        int[] bucket = new int[n + 1];
        for (int c : cites) bucket[Math.min(c, n)]++;
        int papers = 0;
        for (int h = n; h >= 0; h--) {
            papers += bucket[h];
            if (papers >= h) return h;
        }
        return 0;
    }
''',
    examples=[("Example 1", "5\n3 0 6 1 5\n"), ("Example 2", "3\n1 3 1\n")],
    hidden=[
        ("Uncited", "1\n0\n"),
        ("Capped by the paper count", "4\n100 100 100 100\n"),
        ("All zeros", "5\n0 0 0 0 0\n"),
        ("Unsorted", "6\n6 5 3 1 0 7\n"),
    ],
    expl=[
        "Three papers (6, 5, 3) have at least 3 citations; there are not four with at least 4.",
        "Only one paper has at least 2 citations, so h = 1.",
    ],
    prereqs=[
        ("sorting", "In descending order, a paper's rank counts how many papers are at least as cited."),
        ("big_o", "Capping values at n turns the sort into an O(n) counting pass."),
    ],
)

_p(
    "best-meeting-point-line", "Best Meeting Point on a Line", "Medium",
    topics=["Sorting", "Math"], subtopics=["Sorting"], companies=["Google", "Amazon"],
    shape="arr", ret="long", todo="sort; the median minimises the sum of distances",
    description=(
        "Friends live at integer positions on a line. Choose one integer meeting point that "
        "minimises the **total distance** everyone travels, and print that total.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` positions.\n\n### Output\nThe minimum total distance."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ x[i] ≤ 10^9",
    hints=[
        "Try moving the meeting point one step right: everyone to the left gets 1 farther, everyone to the right 1 closer.",
        "So moving right helps while more people are to the right than to the left — until you reach the middle.",
        "Any median minimises the total. Sort and take x[n/2], then sum the distances in a long.",
    ],
    opt=("O(n log n)", "O(1)", "Sorting dominates; quickselect finds the median in expected O(n)."),
    editorial=(
        "## The one thing this teaches\n**The median minimises absolute distance; the mean "
        "minimises squared distance.** It is worth knowing which is which, because \"average "
        "position\" is the first guess and it is wrong here: for 1, 2, 9 the mean is 4 (total 10) "
        "and the median is 2 (total 8).\n\n"
        "## Why the median\nStand at `p` and step right by one. Everyone at or left of `p` gets one "
        "farther and everyone right of `p` gets one closer, so the total changes by "
        "`(left count) − (right count)`. It keeps decreasing while more friends are to the right, "
        "and stops decreasing at the middle.\n\n"
        "## Approach\n```java\nArrays.sort(x);\nlong med = x[n / 2], total = 0;\n"
        "for (int v : x) total += Math.abs(v - med);\n```\n\n"
        "## Two dimensions\nOn a grid with Manhattan distance, the x and y coordinates are "
        "independent: take the median of each separately. That is the classic follow-up."
    ),
    py='''
def solve(a):
    x = sorted(a)
    med = x[len(x) // 2]
    return sum(abs(v - med) for v in x)
''',
    java='''
    static long solve(int[] x) {
        Arrays.sort(x);
        long med = x[x.length / 2], total = 0;
        for (int v : x) total += Math.abs(v - med);
        return total;
    }
''',
    examples=[("Example 1", "3\n1 2 9\n"), ("Example 2", "4\n1 10 2 9\n")],
    hidden=[
        ("Single friend", "1\n5\n"),
        ("Outlier does not drag the median", "5\n-5 -1 0 3 100\n"),
        ("Everyone together", "6\n7 7 7 7 7 7\n"),
        ("Extremes overflow an int", "2\n-1000000000 1000000000\n"),
    ],
    expl=[
        "Meet at 2: 1 + 0 + 7 = 8. Meeting at the mean, 4, costs 10.",
        "Any point from 2 to 9 costs 16.",
    ],
    prereqs=[
        ("sorting", "Sorting puts the median at index n/2."),
        ("overflow", "Distances up to 2·10⁹ each, summed over 10⁵ friends, need a long."),
    ],
)

_p(
    "single-number-iii", "Single Number III", "Medium",
    topics=["Bit Manipulation", "Arrays"], subtopics=["XOR", "Bit Manipulation"], companies=["Meta", "Amazon"],
    shape="arr", ret="String", todo="XOR everything; pick one set bit of the result; XOR each group separately",
    description=(
        "Every value in the array appears **exactly twice**, except two values that appear once. "
        "Find those two, using O(1) extra space.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe two single values, smaller first, separated by a space."
    ),
    constraints="2 ≤ n ≤ 3·10^4\n-2^31 ≤ a[i] ≤ 2^31 − 1\nExactly two values appear once; all others appear twice.",
    hints=[
        "XOR of everything cancels the pairs and leaves x ^ y, where x and y are the two singles.",
        "x ≠ y, so x ^ y has at least one set bit — a bit where x and y differ.",
        "Split all numbers by that bit. Each group contains one single plus whole pairs, so XOR each group.",
    ],
    opt=("O(n)", "O(1)", "Two passes of XOR and one bit test per element."),
    editorial=(
        "## The one thing this teaches\n**Split one hard problem into two easy ones.** Single "
        "Number (one unpaired value) is a single XOR. With two unpaired values the XOR gives "
        "`x ^ y`, which is not either answer — but any set bit of it separates `x` from `y`, and "
        "pairs always land in the same group.\n\n"
        "## Approach\n```java\nint xy = 0;\nfor (int v : a) xy ^= v;\n"
        "int bit = xy & -xy;                 // lowest set bit\nint x = 0;\n"
        "for (int v : a) if ((v & bit) != 0) x ^= v;\nint y = xy ^ x;\n```\n\n"
        "## `xy & -xy`\nIn two's complement, `-xy` is `~xy + 1`: every bit above the lowest set bit "
        "is flipped, and that bit survives. The AND isolates it. It works even when `xy` is "
        "`Integer.MIN_VALUE`, whose negation is itself and whose only set bit is the one wanted.\n\n"
        "## Why pairs cannot split\nBoth copies of a value have the same bits, so they fall in the "
        "same group and cancel there. Each group's XOR is therefore its single value."
    ),
    py='''
def solve(a):
    xy = 0
    for v in a:
        xy ^= v
    bit = xy & -xy
    x = 0
    for v in a:
        if v & bit:
            x ^= v
    y = xy ^ x
    lo, hi = min(x, y), max(x, y)
    return f"{lo} {hi}"
''',
    java='''
    static String solve(int[] a) {
        int xy = 0;
        for (int v : a) xy ^= v;
        int bit = xy & -xy;
        int x = 0;
        for (int v : a) if ((v & bit) != 0) x ^= v;
        int y = xy ^ x;
        return Math.min(x, y) + " " + Math.max(x, y);
    }
''',
    examples=[("Example 1", "6\n1 2 1 3 2 5\n"), ("Example 2", "2\n-1 0\n")],
    hidden=[
        ("Zero is a single", "4\n0 1 1 2\n"),
        ("Negative single", "6\n4 4 7 9 9 -8\n"),
        ("Opposite signs", "2\n1000 -1000\n"),
        ("Extremes", "4\n-2147483648 5 5 2147483647\n"),
    ],
    expl=[
        "1 and 2 are paired; 3 and 5 appear once.",
        "Both values appear once.",
    ],
    prereqs=[
        ("bit_manip", "XOR cancels pairs, and x & −x isolates the lowest set bit."),
        ("array_patterns", "Partitioning the elements into two groups by one bit, then solving each group alone."),
    ],
)
