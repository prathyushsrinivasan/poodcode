# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 10 — arrays, complexity, recursion.
#
#   leaders-in-array            scan from the right carrying the maximum
#   plus-one-digits             carry propagates; a new leading digit only when every digit was 9
#   set-mismatch                a count array finds the duplicate and the missing value at once
#   pairs-divisible-60          count remainders instead of checking pairs
#   sum-all-subarray-sums       each element's contribution: (i + 1)(n − i) subarrays contain it
#   count-valid-triangles       sort, fix the longest side, two-pointer the other two
#   count-and-say               each term is a description of the previous term
#   kth-symbol-grammar          the answer is the parent's symbol, flipped or not
#   nested-list-depth-sum       a recursive descent parser, one call per bracket
#   gray-code                   reflect-and-prefix: two copies of the smaller answer
# ===========================================================================

_p(
    "leaders-in-array", "Leaders in an Array", "Easy",
    topics=["Arrays"], subtopics=["Traversal", "Prefix Max"], companies=["Amazon", "Adobe"],
    shape="arr", ret="String", todo="scan from the right, keeping the maximum seen; an element above it is a leader",
    description=(
        "An element is a **leader** if it is strictly greater than every element to its right. "
        "The last element is always a leader. Print all leaders in their original order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe leaders, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Checking everything to the right of each element is O(n²).",
        "\"Greater than everything to the right\" only needs the maximum of the right side.",
        "Walk from the end carrying that maximum. Collect leaders, then reverse them into original order.",
    ],
    opt=("O(n)", "O(n)", "One right-to-left pass; the output list is the extra space."),
    editorial=(
        "## The one thing this teaches\n**Choose the direction that makes the state small.** "
        "From the left, \"is this bigger than everything after it?\" needs the whole future. From "
        "the right, the same question needs one number — the maximum seen so far.\n\n"
        "## Approach\n```java\nList<Integer> out = new ArrayList<>();\nlong best = Long.MIN_VALUE;\n"
        "for (int i = n - 1; i >= 0; i--)\n    if (a[i] > best) { out.add(a[i]); best = a[i]; }\n"
        "Collections.reverse(out);\n```\n\n"
        "## Strictly greater\nWith `2 2 2 2`, only the last `2` is a leader: each earlier one has "
        "an equal value to its right. Using `>=` would print all four."
    ),
    py='''
def solve(a):
    out = []
    best = None
    for x in reversed(a):
        if best is None or x > best:
            out.append(x)
            best = x
    return " ".join(map(str, reversed(out)))
''',
    java='''
    static String solve(int[] a) {
        List<Integer> out = new ArrayList<>();
        long best = Long.MIN_VALUE;
        for (int i = a.length - 1; i >= 0; i--)
            if (a[i] > best) { out.add(a[i]); best = a[i]; }
        StringBuilder sb = new StringBuilder();
        for (int i = out.size() - 1; i >= 0; i--) { if (sb.length() > 0) sb.append(' '); sb.append(out.get(i)); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n16 17 4 3 5 2\n"), ("Example 2", "4\n1 2 3 4\n")],
    hidden=[
        ("Single element", "1\n7\n"),
        ("Strictly decreasing", "5\n5 4 3 2 1\n"),
        ("All equal", "4\n2 2 2 2\n"),
        ("Negative values", "4\n-5 -9 -2 -7\n"),
    ],
    expl=[
        "17 beats everything after it, as do 5 and the final 2.",
        "Only the last element has nothing larger to its right.",
    ],
    prereqs=[
        ("prefix_max", "A running maximum, carried from the right end."),
        ("iteration", "A reversed loop, with the results reversed back into order."),
    ],
)

_p(
    "plus-one-digits", "Plus One", "Easy",
    topics=["Arrays", "Math"], subtopics=["Digits"], companies=["Google"],
    shape="arr", ret="String", todo="add one at the last digit and carry left; if every digit was 9, prepend a 1",
    description=(
        "A non-negative integer is given as its digits, most significant first, with no leading "
        "zeros (except the number 0 itself). Add one and print the digits of the result.\n\n"
        "### Input\n- Line 1: `n`, the number of digits.\n- Line 2: the digits.\n\n"
        "### Output\nThe digits of the number plus one, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 100\n0 ≤ digit ≤ 9",
    hints=[
        "The number can have 100 digits — converting it to a long is not an option.",
        "Walk from the last digit. A digit below 9 just increases, and you are done.",
        "A 9 becomes 0 and the carry moves left. If the carry falls off the front, the answer is 1 followed by zeros.",
    ],
    opt=("O(n)", "O(n)", "At most one pass of carrying; a new array only when the length grows."),
    editorial=(
        "## The one thing this teaches\n**Arithmetic on a digit array is the schoolbook "
        "algorithm.** Numbers too big for any primitive type are arrays of digits, and adding "
        "one is the carry you learned by hand.\n\n"
        "## Approach\n```java\nfor (int i = n - 1; i >= 0; i--) {\n"
        "    if (d[i] < 9) { d[i]++; return d; }   // no carry: finished\n"
        "    d[i] = 0;                             // 9 + 1 = 10: write 0, carry\n}\n"
        "int[] bigger = new int[n + 1];\nbigger[0] = 1;                           // all 9s\nreturn bigger;\n```\n\n"
        "## Why the early return is enough\nThe carry stops at the first digit below 9, so most "
        "calls touch one digit. Only an all-9s input reaches the end of the loop, and its answer "
        "is always `1 0 0 … 0` — which is why a fresh zero-filled array needs just its first "
        "digit set."
    ),
    py='''
def solve(a):
    d = list(a)
    for i in range(len(d) - 1, -1, -1):
        if d[i] < 9:
            d[i] += 1
            return " ".join(map(str, d))
        d[i] = 0
    return " ".join(map(str, [1] + d))
''',
    java='''
    static String solve(int[] d) {
        int n = d.length;
        int[] res = null;
        for (int i = n - 1; i >= 0; i--) {
            if (d[i] < 9) { d[i]++; res = d; break; }
            d[i] = 0;
        }
        if (res == null) { res = new int[n + 1]; res[0] = 1; }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < res.length; i++) { if (i > 0) sb.append(' '); sb.append(res[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "1\n9\n")],
    hidden=[
        ("All nines", "4\n9 9 9 9\n"),
        ("Carry once", "2\n1 9\n"),
        ("Zero", "1\n0\n"),
        ("Too long for a long", "20\n9 2 2 3 3 7 2 0 3 6 8 5 4 7 7 5 8 0 7 9\n"),
    ],
    expl=[
        "123 + 1 = 124.",
        "9 + 1 = 10: one more digit.",
    ],
    prereqs=[
        ("math_digits", "Adding with a carry, digit by digit, from the least significant end."),
        ("overflow", "The number may have 100 digits, so it never becomes a primitive integer."),
    ],
)

_p(
    "set-mismatch", "Set Mismatch", "Easy",
    topics=["Arrays", "Hashing"], subtopics=["Counting"], companies=["Amazon"],
    shape="arr", ret="String", todo="count occurrences of 1..n; the value seen twice and the value seen zero times",
    description=(
        "An array should contain each of `1` to `n` exactly once, but one value was duplicated, "
        "overwriting another. Find the duplicated value and the missing one.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\n`duplicate missing`."
    ),
    constraints="2 ≤ n ≤ 10^4\n1 ≤ a[i] ≤ n\nExactly one value appears twice and exactly one is missing.",
    hints=[
        "The values are 1..n, so they can index an array directly.",
        "Count occurrences into an array of size n + 1.",
        "The duplicate has count 2 and the missing value has count 0 — one scan finds both.",
    ],
    opt=("O(n)", "O(n)", "A count array of size n + 1; sign-marking in place makes it O(1) extra space."),
    editorial=(
        "## The one thing this teaches\n**Values in 1..n are indices in disguise.** Whenever an "
        "array holds values that fit inside its own length, a count array — or the array itself, "
        "marked in place — replaces a hash set.\n\n"
        "## Approach\n```java\nint[] count = new int[n + 1];\nfor (int x : a) count[x]++;\n"
        "int dup = 0, missing = 0;\nfor (int v = 1; v <= n; v++) {\n"
        "    if (count[v] == 2) dup = v;\n    if (count[v] == 0) missing = v;\n}\n```\n\n"
        "## Two other routes\n- **Arithmetic:** the sum is off by `dup − missing` and the sum of "
        "squares by `dup² − missing²`; two equations, two unknowns. Watch for overflow.\n"
        "- **In place:** for each `x`, negate `a[|x| − 1]`; finding it already negative means `x` "
        "is the duplicate, and the index still positive at the end is the missing value."
    ),
    py='''
def solve(a):
    n = len(a)
    count = [0] * (n + 1)
    for x in a:
        count[x] += 1
    dup = next(v for v in range(1, n + 1) if count[v] == 2)
    missing = next(v for v in range(1, n + 1) if count[v] == 0)
    return f"{dup} {missing}"
''',
    java='''
    static String solve(int[] a) {
        int n = a.length;
        int[] count = new int[n + 1];
        for (int x : a) count[x]++;
        int dup = 0, missing = 0;
        for (int v = 1; v <= n; v++) {
            if (count[v] == 2) dup = v;
            if (count[v] == 0) missing = v;
        }
        return dup + " " + missing;
    }
''',
    examples=[("Example 1", "4\n1 2 2 4\n"), ("Example 2", "2\n1 1\n")],
    hidden=[
        ("Missing the smallest", "2\n2 2\n"),
        ("Missing the largest", "5\n3 2 3 4 1\n"),
        ("Unsorted", "6\n1 5 3 2 2 6\n"),
    ],
    expl=[
        "2 appears twice and 3 never.",
        "1 appears twice and 2 never.",
    ],
    prereqs=[
        ("hashing", "A count array indexed by value, since every value is in 1..n."),
        ("array_patterns", "Using the value range to replace a set with direct indexing."),
    ],
)

_p(
    "pairs-divisible-60", "Pairs of Songs Divisible by 60", "Easy",
    topics=["Arrays", "Hashing"], subtopics=["Counting", "Complement Lookup"], companies=["Amazon", "Goldman Sachs"],
    shape="arr", ret="long", todo="count each remainder mod 60; each song pairs with the earlier songs of the complementary remainder",
    description=(
        "Count pairs of songs `i < j` whose total duration is divisible by 60.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` durations.\n\n### Output\nThe number of pairs."
    ),
    constraints="1 ≤ n ≤ 6·10^4\n1 ≤ duration ≤ 500",
    hints=[
        "Checking every pair is O(n²) — about 1.8·10⁹ at the limit.",
        "(a + b) is divisible by 60 exactly when (a mod 60) + (b mod 60) is 0 or 60.",
        "Keep counts of remainders seen so far. A song with remainder r pairs with every earlier song of remainder (60 − r) mod 60.",
    ],
    opt=("O(n)", "O(1)", "One pass and a 60-slot count array."),
    editorial=(
        "## The one thing this teaches\n**Replace pairs with counts of what a partner must look "
        "like.** Only the remainder mod 60 matters, so there are just 60 kinds of song. Counting "
        "each kind turns \"check every pair\" into \"look up how many earlier songs are the right "
        "kind\".\n\n"
        "## Approach\n```java\nlong[] seen = new long[60];\nlong pairs = 0;\nfor (int t : time) {\n"
        "    int r = t % 60;\n    pairs += seen[(60 - r) % 60];\n    seen[r]++;\n}\n```\n\n"
        "## The `% 60` on the complement\nA song of remainder 0 needs a partner of remainder 0, "
        "not 60. `(60 − 0) % 60` is 0, which handles it without a special case.\n\n"
        "## The count type\n6·10⁴ songs all of remainder 0 form about 1.8·10⁹ pairs — past an "
        "`int`. This is the complexity unit's lesson with a hash table's shape: two-sum, but "
        "counting instead of finding."
    ),
    py='''
def solve(a):
    seen = [0] * 60
    pairs = 0
    for t in a:
        r = t % 60
        pairs += seen[(60 - r) % 60]
        seen[r] += 1
    return pairs
''',
    java='''
    static long solve(int[] time) {
        long[] seen = new long[60];
        long pairs = 0;
        for (int t : time) {
            int r = t % 60;
            pairs += seen[(60 - r) % 60];
            seen[r]++;
        }
        return pairs;
    }
''',
    examples=[("Example 1", "5\n30 20 150 100 40\n"), ("Example 2", "3\n60 60 60\n")],
    hidden=[
        ("Single song", "1\n30\n"),
        ("Complements", "4\n1 59 2 58\n"),
        ("Several thirties", "6\n30 30 30 90 150 10\n"),
    ],
    expl=[
        "(30, 150), (20, 100) and (20, 40).",
        "Every pair of the three songs works.",
    ],
    prereqs=[
        ("complement", "The partner of remainder r is remainder (60 − r) mod 60."),
        ("big_o", "Counting remainders replaces an O(n²) pair check with O(n)."),
    ],
)

_p(
    "sum-all-subarray-sums", "Sum of All Subarray Sums", "Easy",
    topics=["Arrays", "Math"], subtopics=["Counting"], companies=["Amazon"],
    shape="arr", ret="long", todo="a[i] appears in (i + 1)·(n − i) subarrays; add a[i] times that",
    description=(
        "Add up the sums of **every** contiguous subarray of the array.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\nThe total."
    ),
    constraints="1 ≤ n ≤ 10^4\n-10^4 ≤ a[i] ≤ 10^4",
    hints=[
        "Enumerating subarrays and summing each is O(n³); with a running sum it is O(n²).",
        "Turn it around: how many subarrays contain a[i]?",
        "A subarray containing index i starts at one of i + 1 positions and ends at one of n − i. So a[i] is counted (i + 1)(n − i) times.",
    ],
    opt=("O(n)", "O(1)", "One pass adding each element times the number of subarrays that contain it."),
    editorial=(
        "## The one thing this teaches\n**Count contributions, not structures.** There are "
        "n(n+1)/2 subarrays but only n elements, and the total is the same whether you sum by "
        "subarray or by element. By element, each term is a closed-form count.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int i = 0; i < n; i++) total += (long) a[i] * (i + 1) * (n - i);\n```\n\n"
        "## The count\nA subarray `[l, r]` contains `i` when `l ≤ i ≤ r`: `l` has `i + 1` choices "
        "(0…i) and `r` has `n − i` choices (i…n−1), independently.\n\n"
        "## Three prices for one answer\nO(n³) re-sums each subarray, O(n²) extends a running sum, "
        "O(n) counts contributions. The same technique, with a harder count, solves Sum of "
        "Subarray Minimums in the stacks unit."
    ),
    py='''
def solve(a):
    n = len(a)
    return sum(x * (i + 1) * (n - i) for i, x in enumerate(a))
''',
    java='''
    static long solve(int[] a) {
        int n = a.length;
        long total = 0;
        for (int i = 0; i < n; i++) total += (long) a[i] * (i + 1) * (n - i);
        return total;
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "2\n-1 1\n")],
    hidden=[
        ("Single element", "1\n5\n"),
        ("All ones", "4\n1 1 1 1\n"),
        ("Mixed signs", "5\n-2 0 3 -1 4\n"),
        ("Large values", "3\n10000 10000 10000\n"),
    ],
    expl=[
        "Subarray sums 1, 2, 3, 3, 5, 6 total 20.",
        "−1 + 1 + 0 = 0.",
    ],
    prereqs=[
        ("big_o", "The same total computed in O(n³), O(n²) or O(n) depending on what is counted."),
        ("overflow", "Each contribution multiplies three factors, so the product is taken in long."),
    ],
)

_p(
    "count-valid-triangles", "Valid Triangle Number", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers", "Sorting"], companies=["LinkedIn", "ByteDance"],
    shape="arr", ret="long", todo="sort; for each largest side k, two pointers count pairs i < j < k with a[i] + a[j] > a[k]",
    description=(
        "Count the triples of positions `i < j < k` whose values can be the side lengths of a "
        "triangle — the sum of any two sides strictly greater than the third.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` non-negative integers.\n\n### Output\nThe number of triples."
    ),
    constraints="1 ≤ n ≤ 1000\n0 ≤ a[i] ≤ 1000",
    hints=[
        "Checking every triple is O(n³) — 1.7·10⁸ at the limit.",
        "After sorting, only one inequality matters: the two smaller sides must sum to more than the largest.",
        "Fix the largest side at k. With l = 0 and r = k − 1: if a[l] + a[r] > a[k], every l' in [l, r) works with r — add r − l and move r left; otherwise move l right.",
    ],
    opt=("O(n²)", "O(1)", "A sort, then an O(n) two-pointer count for each largest side."),
    editorial=(
        "## The one thing this teaches\n**Sorting deletes constraints.** Three triangle inequalities "
        "become one when you know which side is largest, and sorted order tells you. Then fixing "
        "the largest side leaves a two-pointer counting problem.\n\n"
        "## Approach\n```java\nArrays.sort(a);\nlong count = 0;\nfor (int k = n - 1; k >= 2; k--) {\n"
        "    int l = 0, r = k - 1;\n    while (l < r) {\n"
        "        if (a[l] + a[r] > a[k]) { count += r - l; r--; }   // every l' in [l, r) pairs with r\n"
        "        else l++;\n    }\n}\n```\n\n"
        "## Counting a whole range at once\nWhen `a[l] + a[r] > a[k]`, increasing `l` only makes "
        "the sum bigger, so all `r − l` choices of the smaller side work with this `r`. Adding "
        "them in one step is what keeps each `k` linear.\n\n"
        "## Zeros\nA side of length 0 can never form a triangle: `0 + x > y` needs `x > y`, but "
        "`y` is the largest. The strict inequality handles it with no special case."
    ),
    py='''
def solve(a):
    a = sorted(a)
    n = len(a)
    count = 0
    for k in range(n - 1, 1, -1):
        l, r = 0, k - 1
        while l < r:
            if a[l] + a[r] > a[k]:
                count += r - l
                r -= 1
            else:
                l += 1
    return count
''',
    java='''
    static long solve(int[] a) {
        Arrays.sort(a);
        long count = 0;
        for (int k = a.length - 1; k >= 2; k--) {
            int l = 0, r = k - 1;
            while (l < r) {
                if (a[l] + a[r] > a[k]) { count += r - l; r--; }
                else l++;
            }
        }
        return count;
    }
''',
    examples=[("Example 1", "4\n2 2 3 4\n"), ("Example 2", "4\n4 2 3 4\n")],
    hidden=[
        ("Degenerate", "3\n1 2 3\n"),
        ("Zeros", "3\n0 0 0\n"),
        ("All equal", "5\n5 5 5 5 5\n"),
        ("Repeats", "6\n1 1 1 2 2 3\n"),
    ],
    expl=[
        "(2, 3, 4) twice — once per 2 — and (2, 2, 3).",
        "Four of the four triples work.",
    ],
    prereqs=[
        ("two_pointers", "Counting pairs above a threshold in O(n) on a sorted prefix."),
        ("sorting", "With sides sorted, only the largest side's inequality needs checking."),
    ],
)

_p(
    "count-and-say", "Count and Say", "Medium",
    topics=["Strings", "Recursion"], subtopics=["Recurrence"], companies=["Meta", "Apple"],
    shape="n", ret="String", todo="term(1) = \"1\"; term(n) reads term(n − 1) aloud as run lengths followed by digits",
    description=(
        "The count-and-say sequence starts with `1`. Each later term **describes** the previous "
        "one: `1` is \"one 1\" → `11`; `11` is \"two 1s\" → `21`; `21` is \"one 2, one 1\" → `1211`.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe `n`-th term."
    ),
    constraints="1 ≤ n ≤ 30",
    hints=[
        "The n-th term is defined only in terms of the (n − 1)-th — a recurrence with base case n = 1.",
        "To describe a string, scan it in runs of equal digits, emitting the run length then the digit.",
        "Build with a StringBuilder; the 30th term has over 4000 characters.",
    ],
    opt=("O(total length)", "O(L)", "Each term is produced by one pass over the previous term."),
    editorial=(
        "## The one thing this teaches\n**A recursive definition, computed iteratively.** "
        "`say(n) = describe(say(n − 1))` is naturally recursive, and the recursion is a straight "
        "chain — one call per level with no branching — so a loop computes it with no stack at "
        "all.\n\n"
        "## Approach\n```java\nString cur = \"1\";\nfor (int k = 2; k <= n; k++) {\n"
        "    StringBuilder next = new StringBuilder();\n"
        "    for (int i = 0; i < cur.length(); ) {\n        int j = i;\n"
        "        while (j < cur.length() && cur.charAt(j) == cur.charAt(i)) j++;\n"
        "        next.append(j - i).append(cur.charAt(i));\n        i = j;\n    }\n    cur = next.toString();\n}\n```\n\n"
        "## Run-length encoding again\n`describe` is the run-length encoder from the strings unit "
        "with count and character swapped. Recognising an old tool inside a new definition is "
        "most of the problem.\n\n"
        "## A curiosity\nNo term ever contains a digit above 3, and each term is about 30% longer "
        "than the one before (Conway's constant, ≈ 1.3036)."
    ),
    py='''
def solve(n):
    cur = "1"
    for _ in range(n - 1):
        out = []
        i = 0
        while i < len(cur):
            j = i
            while j < len(cur) and cur[j] == cur[i]:
                j += 1
            out.append(str(j - i) + cur[i])
            i = j
        cur = "".join(out)
    return cur
''',
    java='''
    static String solve(long n) {
        String cur = "1";
        for (int k = 2; k <= n; k++) {
            StringBuilder next = new StringBuilder();
            int i = 0;
            while (i < cur.length()) {
                int j = i;
                while (j < cur.length() && cur.charAt(j) == cur.charAt(i)) j++;
                next.append(j - i).append(cur.charAt(i));
                i = j;
            }
            cur = next.toString();
        }
        return cur;
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "4\n")],
    hidden=[
        ("Second term", "2\n"),
        ("Fifth term", "5\n"),
        ("Tenth term", "10\n"),
    ],
    expl=[
        "The base case.",
        "1 → 11 → 21 → 1211.",
    ],
    prereqs=[
        ("recurrence", "Each term defined from the previous one, computed bottom-up."),
        ("string_basics", "Scanning runs of equal characters and building the next term with a StringBuilder."),
    ],
)

_p(
    "kth-symbol-grammar", "K-th Symbol in Grammar", "Medium",
    topics=["Recursion", "Bit Manipulation"], subtopics=["Recurrence"], companies=["Meta", "Amazon"],
    shape="two", ret="int", todo="the k-th symbol of row n comes from symbol ceil(k/2) of row n−1, flipped if k is even",
    description=(
        "Row 1 is `0`. Each later row replaces every `0` of the previous row with `01` and every "
        "`1` with `10`: row 2 is `01`, row 3 is `0110`, row 4 is `01101001`.\n\n"
        "What is the `k`-th symbol (1-indexed) of row `n`?\n\n"
        "### Input\nOne line: `n k`.\n\n### Output\n`0` or `1`."
    ),
    constraints="1 ≤ n ≤ 30\n1 ≤ k ≤ 2^(n−1)",
    hints=[
        "Row 30 has over 500 million symbols — do not build it.",
        "Symbol k of row n was produced by symbol ceil(k / 2) of row n − 1.",
        "An odd k is the first symbol of its pair (same as the parent), an even k the second (flipped). Recurse down to row 1.",
    ],
    opt=("O(n)", "O(n)", "One recursive call per row; O(1) space iteratively. The answer is also the parity of the set bits of k − 1."),
    editorial=(
        "## The one thing this teaches\n**Recurse on the index, not the data.** Each row is twice "
        "the length of the last, so building rows is exponential. But every symbol has exactly "
        "one parent, and following parents is a halving recursion — log of the row length, which "
        "is n.\n\n"
        "## Approach\n```java\nint kth(int n, long k) {\n    if (n == 1) return 0;\n"
        "    int parent = kth(n - 1, (k + 1) / 2);\n"
        "    return k % 2 == 1 ? parent : 1 - parent;\n}\n```\n\n"
        "## The closed form\nWriting `k − 1` in binary, each 1-bit is a step where the position "
        "was the second of its pair — a flip. So the symbol is the parity of the number of set "
        "bits: `Long.bitCount(k − 1) % 2`. The recursion is what lets you *find* that; the bit "
        "count is what you would ship."
    ),
    py='''
def solve(x, y):
    n, k = x, y
    flips = 0
    while n > 1:
        if k % 2 == 0:
            flips ^= 1
        k = (k + 1) // 2
        n -= 1
    return flips
''',
    java='''
    static int kth(long n, long k) {
        if (n == 1) return 0;
        int parent = kth(n - 1, (k + 1) / 2);
        return k % 2 == 1 ? parent : 1 - parent;
    }

    static int solve(long n, long k) {
        return kth(n, k);
    }
''',
    examples=[("Example 1", "1 1\n"), ("Example 2", "2 2\n")],
    hidden=[
        ("First symbol of a row", "2 1\n"),
        ("Row four", "4 5\n"),
        ("Last symbol of row 30", "30 536870912\n"),
        ("Start of row 30", "30 1\n"),
    ],
    expl=[
        "Row 1 is `0`.",
        "Row 2 is `01`.",
    ],
    prereqs=[
        ("recursion", "Following each symbol to its parent in the previous row."),
        ("bit_manip", "The number of flips is the number of set bits in k − 1."),
    ],
)

_p(
    "nested-list-depth-sum", "Nested List Weight Sum", "Medium",
    topics=["Recursion", "Strings"], subtopics=["Recurrence", "Stack"], companies=["LinkedIn"],
    shape="line", ret="long", todo="parse recursively: '[' descends a level, ']' returns, a number adds value × depth",
    description=(
        "A nested list is written like `[1,[4,[6]],-2]`. Each integer is multiplied by its "
        "**depth** — the number of brackets around it, so the outer list is depth 1 — and the "
        "products are summed.\n\n"
        "### Input\nOne line: the nested list, with no spaces.\n\n### Output\nThe weighted sum."
    ),
    constraints="2 ≤ length ≤ 10^4\nThe list is well-formed; integers are in [-100, 100]; nesting depth ≤ 50.",
    hints=[
        "The structure is recursive: a list contains integers and lists.",
        "Parse with one function per list: it reads items until ']', calling itself at every '['.",
        "Or scan with a depth counter: '[' increments, ']' decrements, and a number is added times the current depth.",
    ],
    opt=("O(length)", "O(depth)", "Every character is read once; the recursion is as deep as the nesting."),
    editorial=(
        "## The one thing this teaches\n**The shape of the recursion is the shape of the input.** "
        "A grammar like `list := '[' item (',' item)* ']'` and `item := number | list` turns "
        "directly into code: one function per rule, a recursive call where the rule refers to "
        "itself. That is a recursive descent parser.\n\n"
        "## Approach — recursive descent\n```java\nint pos = 0;\nlong list(int depth) {          // at '['\n"
        "    pos++;\n    long sum = 0;\n    while (s.charAt(pos) != ']') {\n"
        "        if (s.charAt(pos) == ',') pos++;\n"
        "        else if (s.charAt(pos) == '[') sum += list(depth + 1);\n"
        "        else sum += number() * depth;\n    }\n    pos++;                      // past ']'\n    return sum;\n}\n```\n\n"
        "## Approach — a counter\nBecause the answer only needs each number's depth, a single "
        "counter replaces the recursion: `[` is `depth++`, `]` is `depth--`. That works *here* "
        "because nothing is built. The moment you need the structure itself — its size, a "
        "flattened copy — the recursive version is the one that extends.\n\n"
        "## The number parser\nNumbers can be negative and more than one digit: read an optional "
        "`-`, then digits until a non-digit."
    ),
    py='''
def solve(s):
    total = 0
    depth = 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "[":
            depth += 1
            i += 1
        elif ch == "]":
            depth -= 1
            i += 1
        elif ch == ",":
            i += 1
        else:
            j = i + 1
            while j < len(s) and s[j].isdigit():
                j += 1
            total += int(s[i:j]) * depth
            i = j
    return total
''',
    java='''
    static String src;
    static int pos;

    static long number() {
        int sign = 1;
        if (src.charAt(pos) == '-') { sign = -1; pos++; }
        long v = 0;
        while (Character.isDigit(src.charAt(pos))) v = v * 10 + (src.charAt(pos++) - '0');
        return sign * v;
    }

    static long list(int depth) {
        pos++;
        long sum = 0;
        while (src.charAt(pos) != ']') {
            char c = src.charAt(pos);
            if (c == ',') pos++;
            else if (c == '[') sum += list(depth + 1);
            else sum += number() * depth;
        }
        pos++;
        return sum;
    }

    static long solve(String s) {
        src = s.trim();
        pos = 0;
        return list(1);
    }
''',
    examples=[("Example 1", "[[1,1],2,[1,1]]\n"), ("Example 2", "[1,[4,[6]]]\n")],
    hidden=[
        ("Empty list", "[]\n"),
        ("Single value", "[5]\n"),
        ("Negative, deeply nested", "[[[-3]],2]\n"),
        ("Empty inner lists", "[[],[[]],7]\n"),
        ("Multi-digit values", "[100,[-100,[12]]]\n"),
    ],
    expl=[
        "Four 1s at depth 2 and one 2 at depth 1: 8 + 2 = 10.",
        "1·1 + 4·2 + 6·3 = 27.",
    ],
    prereqs=[
        ("recursion", "One recursive call per nested list, carrying the depth."),
        ("stack", "The call stack mirrors the open brackets; a depth counter is the stack's height."),
    ],
)

_p(
    "gray-code", "Gray Code", "Medium",
    topics=["Recursion", "Bit Manipulation"], subtopics=["Recurrence", "Bit Manipulation"], companies=["Amazon"],
    shape="n", ret="String", todo="G(n) = G(n−1) followed by G(n−1) reversed with the top bit set",
    description=(
        "An `n`-bit **Gray code** lists all `2^n` values so that consecutive values differ in "
        "exactly one bit. Print the **reflected** Gray code: start from `0 1` for one bit; for "
        "`n` bits, list the `(n−1)`-bit code, then the same code in reverse order with bit `n−1` "
        "set.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe `2^n` values in order, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10",
    hints=[
        "The definition is recursive: build the (n−1)-bit list first.",
        "Reversing the smaller list makes its last element meet its own last element — they are equal, so adding the top bit is the only change.",
        "Closed form: the i-th value is i ^ (i >> 1).",
    ],
    opt=("O(2ⁿ)", "O(2ⁿ)", "The output has 2ⁿ values; each is produced in O(1)."),
    editorial=(
        "## The one thing this teaches\n**Build the answer from two copies of the smaller "
        "answer.** The reflect step is the whole proof: inside each copy, neighbours already "
        "differ by one bit; across the seam, the last value of the first copy and the first value "
        "of the reversed copy are the *same* value, differing only in the new top bit.\n\n"
        "## Approach\n```java\nList<Integer> code = new ArrayList<>(List.of(0));\n"
        "for (int bit = 0; bit < n; bit++)\n    for (int i = code.size() - 1; i >= 0; i--)   // reversed\n"
        "        code.add(code.get(i) | (1 << bit));\n```\n\n"
        "Appending the reflected copy in place avoids building a second list.\n\n"
        "## Two calls, one of them reversed\nWritten recursively, `G(n)` uses `G(n−1)` twice, once "
        "forwards and once backwards — so the output doubles per level, which is unavoidable "
        "since the output *is* 2ⁿ values. The closed form `i ^ (i >> 1)` produces the same "
        "sequence without any recursion."
    ),
    py='''
def solve(n):
    code = [0]
    for bit in range(n):
        code += [x | (1 << bit) for x in reversed(code)]
    return " ".join(map(str, code))
''',
    java='''
    static String solve(long n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < (1 << n); i++) {
            if (i > 0) sb.append(' ');
            sb.append(i ^ (i >> 1));
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "1\n"), ("Example 2", "2\n")],
    hidden=[
        ("Three bits", "3\n"),
        ("Four bits", "4\n"),
    ],
    expl=[
        "The base case.",
        "`0 1`, then `1 0` reversed with bit 1 set: `3 2`.",
    ],
    prereqs=[
        ("recursion", "The n-bit code is two copies of the (n−1)-bit code, one reversed."),
        ("bit_manip", "Setting the new top bit with OR, and the closed form i ^ (i >> 1)."),
    ],
)
