# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 35 — the syllabus roadmap, stages 2–4: matching, halves, and moduli.
#
#   find-pattern-index            first occurrence in O(n + m) with the KMP prefix function
#   count-palindromic-substrings  expand around every centre — 2n − 1 of them
#   merge-sort-array              divide and conquer, written out: split, recurse, merge
#   counting-sort-ages            a sort that never compares, because the values are small
#   power-mod                     square-and-multiply, reducing after every multiplication
#   ncr-mod-queries               factorials once, inverses by Fermat, each query O(1)
# ===========================================================================

_p(
    "find-pattern-index", "Find a Pattern in Text", "Easy",
    topics=["Strings"], subtopics=["String Matching", "KMP"], companies=["Microsoft", "Amazon"],
    shape="str2", ret="long", todo="build the prefix function of the pattern, then scan the text reusing it on every mismatch",
    description=(
        "Given a text `s` and a pattern `t`, print the index of the **first** position where `t` "
        "occurs in `s` as a contiguous substring, or `-1` if it never does.\n\n"
        "The naive check restarts from scratch after every mismatch. Aim for O(n + m).\n\n"
        "### Input\nLine 1: the text `s`.\nLine 2: the pattern `t`.\n\n"
        "### Output\nThe 0-based index of the first occurrence, or `-1`."
    ),
    constraints="1 ≤ |s|, |t| ≤ 10^5\nLowercase English letters only",
    hints=[
        "Checking every start position against the whole pattern is O(n·m) — on `aaaa…ab` against `aaa…ab` it really does that much work.",
        "When a match fails after k characters, those k characters of the text are already known: they equal the pattern's first k. How far can the pattern shift without re-reading them?",
        "Precompute pi[i] = the length of the longest proper prefix of t[0..i] that is also a suffix of it. On a mismatch, fall back to k = pi[k − 1] instead of 0.",
    ],
    opt=("O(n + m)", "O(m)", "The prefix function of the pattern, then one pass over the text that never moves backwards."),
    editorial=(
        "## The one thing this teaches\n**A failed match still tells you something.** After "
        "matching k characters, the last k characters of the text are exactly the pattern's first "
        "k. The prefix function precomputes how much of that survives a shift, so the text pointer "
        "never moves backwards.\n\n"
        "## The prefix function\n`pi[i]` is the length of the longest proper prefix of `t[0..i]` "
        "that is also a suffix of it. For `abcaby`: `pi = [0, 0, 0, 1, 2, 0]` — at index 4 the "
        "prefix `ab` reappears as a suffix of `abcab`.\n\n"
        "## Approach\n```java\nint[] pi = new int[m];\nfor (int i = 1, k = 0; i < m; i++) {\n"
        "    while (k > 0 && t.charAt(i) != t.charAt(k)) k = pi[k - 1];\n"
        "    if (t.charAt(i) == t.charAt(k)) k++;\n    pi[i] = k;\n}\n"
        "for (int i = 0, k = 0; i < n; i++) {\n"
        "    while (k > 0 && s.charAt(i) != t.charAt(k)) k = pi[k - 1];   // fall back, do not restart\n"
        "    if (s.charAt(i) == t.charAt(k)) k++;\n    if (k == m) return i - m + 1;\n}\nreturn -1;\n```\n\n"
        "## Why it is linear\n`k` rises by at most one per character and every fallback lowers "
        "it, so the total number of fallbacks is at most n. The same amortised argument as the "
        "monotonic stack.\n\n"
        "## The two loops are the same loop\nBuilding `pi` is matching the pattern against "
        "itself. Once you see that, you only have one loop to remember."
    ),
    py='''
def solve(s, t):
    m = len(t)
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k and t[i] != t[k]:
            k = pi[k - 1]
        if t[i] == t[k]:
            k += 1
        pi[i] = k
    k = 0
    for i, ch in enumerate(s):
        while k and ch != t[k]:
            k = pi[k - 1]
        if ch == t[k]:
            k += 1
        if k == m:
            return i - m + 1
    return -1
''',
    java='''
    static long solve(String s, String t) {
        return s.indexOf(t);
    }
''',
    examples=[("Example 1", "abxabcabcaby\nabcaby\n"), ("Example 2", "aaaaab\naab\n"), ("Example 3", "hello\nworld\n")],
    hidden=[
        ("Pattern longer than the text", "ab\nabc\n"),
        ("Whole text", "abc\nabc\n"),
        ("Match at the very start", "aaaa\na\n"),
        ("Fallback needed mid-match", "abababca\nabca\n"),
        ("Match at the very end", "xyzxyzxyzq\nxyzq\n"),
    ],
    expl=[
        "`abcab` matches at index 3 and fails on `c`; the prefix function keeps `ab` and resumes. The full pattern starts at 6.",
        "The pattern starts at index 3: `aab`.",
        "`world` never appears.",
    ],
    prereqs=[
        ("string_basics", "Indexing characters and comparing substrings."),
        ("two_pointers", "A text pointer that only moves forward while a pattern pointer falls back."),
    ],
)

_p(
    "count-palindromic-substrings", "Count Palindromic Substrings", "Medium",
    topics=["Strings", "Two Pointers"], subtopics=["Expand Around Centre", "Palindromes"], companies=["Meta", "LinkedIn"],
    shape="str", ret="long", todo="for each of the 2n − 1 centres, expand outwards while both ends match, counting each step",
    description=(
        "Count the substrings of `s` that are palindromes. Substrings at different positions count "
        "separately, even if they spell the same thing.\n\n"
        "### Input\nOne line: the string `s`.\n\n"
        "### Output\nThe number of palindromic substrings."
    ),
    constraints="1 ≤ |s| ≤ 2000\nLowercase English letters",
    hints=[
        "There are O(n²) substrings, and checking each is O(n) — O(n³) in total.",
        "Every palindrome has a centre. Grow outwards from it and you meet every palindrome with that centre, shortest first.",
        "There are 2n − 1 centres: each character (odd lengths) and each gap between neighbours (even lengths). Expand while s[l] == s[r].",
    ],
    opt=("O(n²)", "O(1)", "2n − 1 centres, each expanded at most n/2 steps, with no extra memory."),
    editorial=(
        "## The one thing this teaches\n**Enumerate palindromes by their centre, not by their "
        "ends.** Choosing both ends gives O(n²) candidates that each need an O(n) check. Choosing a "
        "centre and growing outwards checks each candidate in O(1), because the inner part was "
        "confirmed one step earlier.\n\n"
        "## Approach\n```java\nlong count = 0;\nfor (int c = 0; c < 2 * n - 1; c++) {\n"
        "    int l = c / 2, r = l + c % 2;          // even c: a letter; odd c: a gap\n"
        "    while (l >= 0 && r < n && s.charAt(l) == s.charAt(r)) {\n"
        "        count++;\n        l--; r++;\n    }\n}\n```\n\n"
        "## Why the gaps matter\n`abba` has no middle letter. Expanding only from letters finds "
        "`a`, `b`, `b`, `a` and misses `bb` and `abba`.\n\n"
        "## Beyond this\nThe same loop, keeping the longest expansion instead of counting, is "
        "*longest palindromic substring*. Manacher's algorithm makes it O(n) by reusing mirror "
        "images, and is rarely expected in an interview."
    ),
    py='''
def solve(s):
    n = len(s)
    count = 0
    for c in range(2 * n - 1):
        l, r = c // 2, c // 2 + c % 2
        while l >= 0 and r < n and s[l] == s[r]:
            count += 1
            l -= 1
            r += 1
    return count
''',
    java='''
    static long solve(String s) {
        int n = s.length();
        long count = 0;
        for (int i = 0; i < n; i++)
            for (int j = i; j < n; j++) {
                int l = i, r = j;
                while (l < r && s.charAt(l) == s.charAt(r)) { l++; r--; }
                if (l >= r) count++;
            }
        return count;
    }
''',
    examples=[("Example 1", "abcb\n"), ("Example 2", "zzz\n")],
    hidden=[
        ("One letter", "z\n"),
        ("Even centre", "abba\n"),
        ("Odd centre", "racecar\n"),
        ("Mixed", "aabaacdc\n"),
    ],
    expl=[
        "Four single letters, plus `bcb`.",
        "Three singles, two `zz` and one `zzz`.",
    ],
    prereqs=[
        ("two_pointers", "Two indices moving outwards from a centre."),
        ("string_basics", "Palindromes as a symmetry of indices."),
    ],
)

_p(
    "merge-sort-array", "Merge Sort, By Hand", "Medium",
    topics=["Sorting", "Recursion"], subtopics=["Divide and Conquer", "Merge Sort"], companies=["Amazon", "Microsoft"],
    shape="arr", ret="String", todo="split in half, sort each half recursively, then merge the two sorted halves with two pointers",
    description=(
        "Sort the array into non-decreasing order **by writing merge sort**: split in half, sort "
        "both halves, merge. Do not call a library sort — the point is the recursion.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe sorted values, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ value ≤ 10^9",
    hints=[
        "Trust the recursive call: assume `sort(left)` and `sort(right)` already work.",
        "Merging two sorted arrays is the two-pointer merge — always take the smaller front element.",
        "Allocate one buffer up front and merge into it, rather than allocating new arrays at every level.",
    ],
    opt=("O(n log n)", "O(n)", "log n levels of halving; each level merges n elements in total."),
    editorial=(
        "## The one thing this teaches\n**Divide and conquer is a recurrence you can read off the "
        "code.** Two calls on halves plus a linear merge is `T(n) = 2T(n/2) + O(n)`, which is "
        "O(n log n): there are log n levels, and the merges on each level touch every element once.\n\n"
        "## Approach\n```java\nstatic void sort(int[] a, int[] buf, int lo, int hi) {   // [lo, hi)\n"
        "    if (hi - lo < 2) return;                          // base: 0 or 1 element\n"
        "    int mid = (lo + hi) >>> 1;\n    sort(a, buf, lo, mid);\n    sort(a, buf, mid, hi);\n"
        "    int i = lo, j = mid, k = lo;\n    while (i < mid && j < hi) buf[k++] = a[i] <= a[j] ? a[i++] : a[j++];\n"
        "    while (i < mid) buf[k++] = a[i++];\n    while (j < hi) buf[k++] = a[j++];\n"
        "    System.arraycopy(buf, lo, a, lo, hi - lo);\n}\n```\n\n"
        "## Details that matter\n- `<=` in the merge keeps equal elements in their original "
        "order, which is what makes merge sort **stable**.\n- `(lo + hi) >>> 1` cannot overflow.\n"
        "- One shared buffer: allocating inside the recursion costs O(n log n) allocations.\n\n"
        "## Where this goes next\nThe merge step sees every pair that crosses the midpoint. "
        "Counting those pairs instead of just merging them is *count inversions*, in the sorting unit."
    ),
    py='''
def solve(a):
    def sort(lo, hi):
        if hi - lo < 2:
            return a[lo:hi]
        mid = (lo + hi) // 2
        left, right = sort(lo, mid), sort(mid, hi)
        out, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                out.append(left[i]); i += 1
            else:
                out.append(right[j]); j += 1
        out.extend(left[i:])
        out.extend(right[j:])
        return out
    return " ".join(map(str, sort(0, len(a))))
''',
    java='''
    static String solve(int[] a) {
        int[] b = a.clone();
        java.util.Arrays.sort(b);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < b.length; i++) { if (i > 0) sb.append(' '); sb.append(b[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n5 2 9 1 5 6\n"), ("Example 2", "1\n42\n")],
    hidden=[
        ("Already sorted", "5\n1 2 3 4 5\n"),
        ("Reverse sorted", "6\n6 5 4 3 2 1\n"),
        ("Negatives and duplicates", "8\n0 -3 7 -3 2 2 -1000000000 1000000000\n"),
        ("Two elements", "2\n9 -9\n"),
    ],
    expl=[
        "Halves [5 2 9] and [1 5 6] sort to [2 5 9] and [1 5 6]; merging gives 1 2 5 5 6 9.",
        "A single element is already sorted — the base case.",
    ],
    prereqs=[
        ("recursion", "Two recursive calls on halves, trusted rather than traced."),
        ("alg_efficient_sorts", "Merge sort's split, recurse and merge."),
    ],
)

_p(
    "counting-sort-ages", "Sort Ages Without Comparing", "Easy",
    topics=["Sorting"], subtopics=["Counting Sort"], companies=["Google"],
    shape="arr", ret="String", todo="count how many people have each age 0..150, then write each age out as many times as it was counted",
    description=(
        "A census lists `n` ages, each between 0 and 150. Print them in non-decreasing order.\n\n"
        "The values are tiny compared with how many there can be. Sort them in O(n + 151) without "
        "comparing any two ages.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` ages.\n\n"
        "### Output\nThe ages in sorted order, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^6\n0 ≤ age ≤ 150",
    hints=[
        "A comparison sort cannot beat O(n log n) — but that bound is for sorts that learn only from comparisons.",
        "Here you can use the value itself as an array index.",
        "count[age]++ for every person, then walk ages 0..150 and emit each one count[age] times.",
    ],
    opt=("O(n + k)", "O(k)", "k = 151 possible ages: one counting pass and one output pass."),
    editorial=(
        "## The one thing this teaches\n**The O(n log n) lower bound is about comparisons.** A sort "
        "that uses each value as an index learns more than a comparison does, and when the value "
        "range k is small it is O(n + k).\n\n"
        "## Approach\n```java\nint[] count = new int[151];\nfor (int x : a) count[x]++;\n"
        "StringBuilder sb = new StringBuilder();\nfor (int age = 0; age <= 150; age++)\n"
        "    for (int c = 0; c < count[age]; c++) sb.append(age).append(' ');\n```\n\n"
        "## When it stops working\nCounting sort needs an array of size k. For ages k = 151 is "
        "nothing; for arbitrary 32-bit integers k is four billion. Radix sort is the fix: counting "
        "sort applied one digit at a time.\n\n"
        "## Output is part of the cost\nWith n up to 10^6, building the output with string `+=` "
        "is quadratic. Use a `StringBuilder`."
    ),
    py='''
def solve(a):
    count = [0] * 151
    for x in a:
        count[x] += 1
    out = []
    for age in range(151):
        out.extend([str(age)] * count[age])
    return " ".join(out)
''',
    java='''
    static String solve(int[] a) {
        int[] count = new int[151];
        for (int x : a) count[x]++;
        StringBuilder sb = new StringBuilder();
        for (int age = 0; age <= 150; age++)
            for (int c = 0; c < count[age]; c++) {
                if (sb.length() > 0) sb.append(' ');
                sb.append(age);
            }
        return sb.toString();
    }
''',
    examples=[("Example 1", "7\n34 2 90 34 0 150 18\n"), ("Example 2", "3\n5 5 5\n")],
    hidden=[
        ("One person", "1\n77\n"),
        ("Both extremes", "4\n150 0 150 0\n"),
        ("Descending", "6\n60 50 40 30 20 10\n"),
    ],
    expl=[
        "Counting gives one each of 0, 2, 18, 90, 150 and two of 34.",
        "Every age is equal; count[5] = 3.",
    ],
    prereqs=[
        ("alg_non_comparison_sorts", "Using a value as an index instead of comparing it."),
        ("array_patterns", "A frequency array indexed by value."),
    ],
)

_p(
    "power-mod", "Power Modulo a Prime", "Easy",
    topics=["Math"], subtopics=["Modular Arithmetic", "Fast Exponentiation"], companies=["Google", "Adobe"],
    shape="two", ret="long", todo="reduce the base mod 1e9+7, then square-and-multiply, reducing after every multiplication",
    description=(
        "Print `a^b mod (10^9 + 7)`. By convention `0^0 = 1`.\n\n"
        "### Input\nOne line: `a b`.\n\n"
        "### Output\nThe value of `a^b` modulo 1 000 000 007."
    ),
    constraints="0 ≤ a ≤ 10^18\n0 ≤ b ≤ 10^18",
    hints=[
        "Multiplying `a` by itself b times is up to 10^18 steps.",
        "a^b = (a^(b/2))² when b is even, and a · (a^(b/2))² when it is odd — about 60 steps for b ≤ 10^18.",
        "Two numbers below 10^9 + 7 multiply to below 2^63, so a `long` holds the product. Reduce `a` first: 10^18 · 10^18 does not fit.",
    ],
    opt=("O(log b)", "O(1)", "Square-and-multiply over the bits of b, every product reduced mod p."),
    editorial=(
        "## The one thing this teaches\n**Reduce after every multiplication, and before the first "
        "one.** `(x · y) mod p = ((x mod p) · (y mod p)) mod p`, so you may reduce whenever you "
        "like — and you must reduce often enough that no intermediate product overflows.\n\n"
        "## Approach\n```java\nstatic final long MOD = 1_000_000_007L;\n\n"
        "long result = 1 % MOD, base = a % MOD;         // reduce the base first\n"
        "while (b > 0) {\n    if ((b & 1) == 1) result = result * base % MOD;\n"
        "    base = base * base % MOD;\n    b >>= 1;\n}\nreturn result;\n```\n\n"
        "## Why a `long` is enough\nBoth factors are below 10^9 + 7 < 2^30, so the product is below "
        "2^60 < 2^63. Skip `a % MOD` and the first `base * base` is (10^18)², which overflows silently.\n\n"
        "## Where this is used\nEvery \"answer modulo 10^9 + 7\" problem, and the modular inverse: "
        "by Fermat's little theorem `x^(p−2) mod p` is the inverse of `x` when `p` is prime."
    ),
    py='''
def solve(x, y):
    return pow(x, y, 1_000_000_007)
''',
    java='''
    static long solve(long a, long b) {
        final long MOD = 1_000_000_007L;
        long result = 1, base = a % MOD;
        while (b > 0) {
            if ((b & 1) == 1) result = result * base % MOD;
            base = base * base % MOD;
            b >>= 1;
        }
        return result;
    }
''',
    examples=[("Example 1", "2 10\n"), ("Example 2", "3 0\n"), ("Example 3", "2 40\n")],
    hidden=[
        ("Zero to the zero", "0 0\n"),
        ("Zero base", "0 5\n"),
        ("Base equal to the modulus", "1000000007 3\n"),
        ("Huge exponent", "123456789 1000000000000000000\n"),
        ("Huge base", "1000000000000000000 1000000000000000000\n"),
    ],
    expl=[
        "2^10 = 1024, which is already below the modulus.",
        "Anything to the power 0 is 1.",
        "2^40 = 1 099 511 627 776, and 1 099 511 627 776 mod 1 000 000 007 = 511 620 083.",
    ],
    prereqs=[
        ("modulo", "Reducing after each multiplication so values stay small."),
        ("overflow", "Why the base must be reduced before it is squared."),
    ],
)

_p(
    "ncr-mod-queries", "Binomial Coefficients Modulo a Prime", "Medium",
    topics=["Math"], subtopics=["Modular Arithmetic", "Combinatorics", "Modular Inverse"], companies=["Google", "Amazon"],
    shape="pairs", ret="String", todo="precompute factorials and inverse factorials mod p up to the largest N; each answer is fact[N]·inv[R]·inv[N−R]",
    description=(
        "Answer `q` queries. Each gives `N` and `R`; print `C(N, R) mod (10^9 + 7)` — the number of "
        "ways to choose `R` items from `N`, or `0` if `R > N`.\n\n"
        "### Input\nLine 1: `q`.\nNext `q` lines: `N R`.\n\n"
        "### Output\nOne line per query."
    ),
    constraints="1 ≤ q ≤ 10^5\n0 ≤ N, R ≤ 10^6",
    hints=[
        "Pascal's triangle up to 10^6 is 10^12 cells.",
        "C(N, R) = N! / (R! (N − R)!). Precompute factorials mod p once; each query is then three lookups — except that you cannot divide mod p.",
        "p is prime, so x^(p−2) is x's inverse (Fermat). Compute inv(N!) once with power-mod, then inv((i−1)!) = inv(i!) · i walking downwards.",
    ],
    opt=("O(M + q)", "O(M)", "M = the largest N: factorials up, one Fermat inverse, inverse factorials down."),
    editorial=(
        "## The one thing this teaches\n**Division mod a prime is multiplication by an inverse.** "
        "Mod p you cannot divide, but when p is prime every nonzero x has an inverse x^(p−2) "
        "(Fermat's little theorem), so `a / b` becomes `a · b^(p−2)`.\n\n"
        "## Approach\n```java\nlong[] fact = new long[M + 1], inv = new long[M + 1];\nfact[0] = 1;\n"
        "for (int i = 1; i <= M; i++) fact[i] = fact[i - 1] * i % MOD;\n"
        "inv[M] = power(fact[M], MOD - 2);                 // one O(log p) inverse\n"
        "for (int i = M; i > 0; i--) inv[i - 1] = inv[i] * i % MOD;   // the rest for free\n\n"
        "long nCr(int n, int r) {\n    if (r < 0 || r > n) return 0;\n"
        "    return fact[n] * inv[r] % MOD * inv[n - r] % MOD;\n}\n```\n\n"
        "## Why walk the inverses downwards\n`1/(i−1)! = i / i!`, so one inverse at the top gives "
        "every other one by multiplication. Computing each inverse separately is O(M log p).\n\n"
        "## Two bugs to avoid\n- `fact[n] * inv[r] * inv[n - r] % MOD` overflows: reduce after "
        "*each* product.\n- `R > N` must be 0, not an out-of-bounds read."
    ),
    py='''
def solve(p):
    MOD = 1_000_000_007
    top = max((max(n, r) for n, r in p), default=0)
    fact = [1] * (top + 1)
    for i in range(1, top + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (top + 1)
    inv[top] = pow(fact[top], MOD - 2, MOD)
    for i in range(top, 0, -1):
        inv[i - 1] = inv[i] * i % MOD
    out = []
    for n, r in p:
        out.append(str(0 if r > n else fact[n] * inv[r] % MOD * inv[n - r] % MOD))
    return "\\n".join(out)
''',
    java='''
    static final long MOD = 1_000_000_007L;

    static long power(long b, long e) {
        long r = 1;
        b %= MOD;
        while (e > 0) {
            if ((e & 1) == 1) r = r * b % MOD;
            b = b * b % MOD;
            e >>= 1;
        }
        return r;
    }

    static String solve(int[][] p) {
        StringBuilder sb = new StringBuilder();
        for (int[] q : p) {
            int n = q[0], r = q[1];
            if (sb.length() > 0) sb.append('\\n');
            if (r > n) { sb.append(0); continue; }
            r = Math.min(r, n - r);
            long num = 1, den = 1;
            for (int i = 0; i < r; i++) {
                num = num * (n - i) % MOD;
                den = den * (i + 1) % MOD;
            }
            sb.append(num * power(den, MOD - 2) % MOD);
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3\n5 2\n10 0\n3 5\n"), ("Example 2", "2\n52 5\n100 50\n")],
    hidden=[
        ("Edges of the row", "4\n0 0\n7 7\n7 1\n1 0\n"),
        ("Larger than a long before reduction", "3\n1000 500\n999 1\n60 30\n"),
        ("Near the top of the range", "2\n200000 100000\n200000 199999\n"),
    ],
    expl=[
        "C(5,2) = 10; C(10,0) = 1; choosing 5 from 3 is impossible, so 0.",
        "C(52,5) = 2 598 960 (poker hands). C(100,50) is about 10^29, so only its remainder is printed.",
    ],
    prereqs=[
        ("modulo", "Reducing after every product, and dividing by multiplying with an inverse."),
        ("number_theory", "Fermat's little theorem for inverses modulo a prime."),
    ],
)
