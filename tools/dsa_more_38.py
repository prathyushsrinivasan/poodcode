# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 38 — the syllabus roadmap, stage 8 (optional): beyond the core.
#
#   count-pattern-occurrences  every match, overlapping, in O(n + m) with the Z-function
#   repeated-dna-sequences     a rolling hash: the next window's code from the last one's
#   longest-duplicate-substring  binary search on the length, rolling hash to test it
#   string-period              the shortest repeating unit is n − pi[n − 1]
#   range-sum-point-update     a Fenwick tree: prefix sums that survive an update
#   range-min-queries          a segment tree, for an operation with no inverse
#   count-smaller-after-self   a Fenwick tree over value ranks, scanned right to left
#   range-add-range-sum        two Fenwick trees turn range updates into point updates
#   euler-path-exists          degrees and connectivity decide it; no search needed
#   articulation-points        DFS low-links: a vertex whose child cannot climb past it
#   count-scc                  Tarjan: one DFS, a stack, and a low-link per vertex
#   reconstruct-itinerary      Hierholzer: walk until stuck, then prepend
#   subset-xor-sum-total       2^n subsets as the integers 0 … 2^n − 1
#   min-cost-assignment        a mask of taken jobs is the whole state
#   shortest-path-visit-all    BFS over (node, visited mask)
# ===========================================================================

_p(
    "count-pattern-occurrences", "Count Every Occurrence", "Easy",
    topics=["Strings"], subtopics=["String Matching", "Z-Function"], companies=["Google"],
    shape="str2", ret="long", todo="compute the Z-array of pattern + '$' + text and count positions whose Z-value equals the pattern length",
    description=(
        "Count how many times the pattern `t` occurs in the text `s`. Occurrences may **overlap**: "
        "`aa` occurs three times in `aaaa`.\n\n"
        "### Input\nLine 1: the text `s`.\nLine 2: the pattern `t`.\n\n"
        "### Output\nThe number of occurrences."
    ),
    constraints="1 ≤ |s|, |t| ≤ 10^5\nLowercase English letters",
    hints=[
        "Checking every start is O(n·m) in the worst case.",
        "The Z-function: z[i] is the length of the longest substring starting at i that matches a prefix of the string.",
        "Build z for `t + \"$\" + s`. A position in the `s` part with z = |t| is an occurrence; the `$` stops a match running past the pattern.",
    ],
    opt=("O(n + m)", "O(n + m)", "One Z-array over pattern, separator and text."),
    editorial=(
        "## The one thing this teaches\n**Matching as a property of one combined string.** Glue the "
        "pattern in front of the text with a separator that appears in neither, and \"does the "
        "pattern occur at i?\" becomes \"does the prefix match at i?\" — which the Z-array answers "
        "for every i at once.\n\n"
        "## The Z-function\n```java\nint[] z = new int[n];\nfor (int i = 1, l = 0, r = 0; i < n; i++) {\n"
        "    if (i < r) z[i] = Math.min(r - i, z[i - l]);          // reuse the known box [l, r)\n"
        "    while (i + z[i] < n && c[z[i]] == c[i + z[i]]) z[i]++;\n"
        "    if (i + z[i] > r) { l = i; r = i + z[i]; }\n}\n```\n\n"
        "## Why it is linear\n`r` only moves right, and every successful character comparison in the "
        "`while` moves it. Comparisons that fail happen at most once per i.\n\n"
        "## KMP or Z?\nThey solve the same problems in the same time. KMP is a streaming matcher; Z is "
        "easier to reason about when you need \"how much matches starting here\"."
    ),
    py='''
def solve(s, t):
    c = t + "$" + s
    n = len(c)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and c[z[i]] == c[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    m = len(t)
    return sum(1 for i in range(m + 1, n) if z[i] == m)
''',
    java='''
    static long solve(String s, String t) {
        long count = 0;
        for (int i = 0; i + t.length() <= s.length(); i++)
            if (s.regionMatches(i, t, 0, t.length())) count++;
        return count;
    }
''',
    examples=[("Example 1", "aaaa\naa\n"), ("Example 2", "abcabcab\nabcab\n"), ("Example 3", "short\nlonger\n")],
    hidden=[
        ("Whole text", "xyz\nxyz\n"),
        ("Single letters", "banana\na\n"),
        ("No overlap possible", "abababab\nba\n"),
        ("Periodic", "aabaabaab\naab\n"),
    ],
    expl=[
        "Matches start at 0, 1 and 2.",
        "Matches start at 0 and 3, overlapping on `ab`.",
        "The pattern is longer than the text.",
    ],
    prereqs=[
        ("string_basics", "Substrings and prefixes."),
        ("two_pointers", "A window [l, r) that only moves right."),
    ],
)

_p(
    "repeated-dna-sequences", "Repeated Ten-Letter Sequences", "Medium",
    topics=["Strings", "Hashing", "Bit Manipulation"], subtopics=["Rolling Hash", "Sliding Window"], companies=["LinkedIn", "Amazon"],
    shape="str", ret="String", todo="encode each letter in 2 bits; slide a 20-bit code along the string and count codes seen twice",
    description=(
        "A DNA string uses the letters `A`, `C`, `G`, `T`. Print every 10-letter sequence that "
        "occurs **more than once** (occurrences may overlap), in alphabetical order, separated by "
        "spaces — or `NONE`.\n\n"
        "### Input\nOne line: the string.\n\n"
        "### Output\nThe repeated sequences, sorted, or `NONE`."
    ),
    constraints="1 ≤ length ≤ 10^5\nOnly A, C, G, T",
    hints=[
        "Putting every 10-letter substring in a hash set works, but builds and hashes a new 10-character string at every position.",
        "Four letters need 2 bits each, so a 10-letter window fits in a 20-bit integer.",
        "Roll it: code = ((code << 2) | letter) & ((1 << 20) − 1) drops the oldest letter and adds the newest in O(1). Count codes in an array of size 2^20.",
    ],
    opt=("O(n)", "O(4^10)", "A rolling 20-bit code per window, counted in a fixed-size array."),
    editorial=(
        "## The one thing this teaches\n**A rolling hash computes the next window's code from the "
        "last one.** Hashing each window from scratch costs O(L) per position. Shifting out the "
        "oldest symbol and shifting in the newest costs O(1), so the scan is O(n) for any window "
        "length.\n\n"
        "## Approach\n```java\nint code = 0, mask = (1 << 20) - 1;\nbyte[] seen = new byte[1 << 20];\n"
        "for (int i = 0; i < n; i++) {\n    code = ((code << 2) | idx(s.charAt(i))) & mask;   // roll\n"
        "    if (i >= 9 && seen[code] < 2 && ++seen[code] == 2)\n        found.add(s.substring(i - 9, i + 1));\n}\n```\n\n"
        "## Why this hash has no collisions\nTwo bits per letter and ten letters is an *exact* "
        "encoding: different windows get different codes. General text needs a polynomial rolling "
        "hash modulo a large prime, where collisions are possible and matches should be verified.\n\n"
        "## The general form\n`h(i+1) = (h(i) − s[i]·B^(L−1)) · B + s[i+L]` — Rabin–Karp. The bit "
        "shift above is the same formula with B = 4."
    ),
    py='''
def solve(s):
    counts = Counter(s[i:i + 10] for i in range(len(s) - 9))
    rep = sorted(k for k, v in counts.items() if v > 1)
    return " ".join(rep) if rep else "NONE"
''',
    java='''
    static int idx(char c) { return c == 'A' ? 0 : c == 'C' ? 1 : c == 'G' ? 2 : 3; }

    static String solve(String s) {
        int n = s.length(), code = 0, mask = (1 << 20) - 1;
        byte[] seen = new byte[1 << 20];
        TreeSet<String> found = new TreeSet<>();
        for (int i = 0; i < n; i++) {
            code = ((code << 2) | idx(s.charAt(i))) & mask;
            if (i >= 9 && seen[code] < 2 && ++seen[code] == 2) found.add(s.substring(i - 9, i + 1));
        }
        return found.isEmpty() ? "NONE" : String.join(" ", found);
    }
''',
    examples=[("Example 1", "ACGTACGTACGTACGTAC\n"), ("Example 2", "GATTACA\n")],
    hidden=[
        ("All one letter", "AAAAAAAAAAAA\n"),
        ("Exactly ten letters", "ACGTACGTAC\n"),
        ("Two repeats far apart", "CCCCCGGGGGTTTTTCCCCCGGGGGAAAAACCCCCGGGGG\n"),
        ("Eleven letters, one overlap", "AAAAAAAAAAA\n"),
    ],
    expl=[
        "Every 10-letter window starting within the first four positions reappears four letters later.",
        "Shorter than ten letters, so nothing can repeat.",
    ],
    prereqs=[
        ("hashing", "Counting windows by a code instead of by the string."),
        ("bit_manip", "Two bits per letter, shifted and masked."),
    ],
)

_p(
    "longest-duplicate-substring", "Longest Repeated Substring", "Hard",
    topics=["Strings", "Binary Search", "Hashing"], subtopics=["Rolling Hash", "Binary Search on the Answer"], companies=["Google", "Microsoft"],
    shape="str", ret="String", todo="binary-search the length; a length works if a rolling hash finds two equal windows of it (verify the match)",
    description=(
        "Find the longest substring that occurs **at least twice** in `s` (occurrences may overlap). "
        "If several have that length, print the alphabetically smallest. If no substring repeats, "
        "print `NONE`.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe substring, or `NONE`."
    ),
    constraints="2 ≤ |s| ≤ 3·10^4\nLowercase English letters",
    hints=[
        "If some substring of length L repeats, then so does one of length L − 1 (drop its last letter). So \"a repeat of length L exists\" is monotone in L.",
        "Binary-search L. For a fixed L, a rolling hash visits all windows in O(n); two equal hashes are a candidate repeat.",
        "Hashes can collide, so confirm a candidate by comparing the actual substrings. Keep the smallest confirmed repeat at the final length.",
    ],
    opt=("O(n log n)", "O(n)", "log n binary-search steps, each an O(n) rolling-hash scan (expected, with verification)."),
    editorial=(
        "## The one thing this teaches\n**Binary search on the answer, with a linear check.** "
        "\"Is there a repeat of length L?\" is monotone, so the longest L takes log n checks — and a "
        "rolling hash makes each check O(n) instead of O(n·L).\n\n"
        "## Approach\n```java\nint lo = 1, hi = n - 1;\nString best = null;\nwhile (lo <= hi) {\n"
        "    int mid = (lo + hi) >>> 1;\n    String r = repeatOfLength(s, mid);    // smallest verified repeat, or null\n"
        "    if (r != null) { best = r; lo = mid + 1; } else hi = mid - 1;\n}\n```\n\n"
        "## The rolling check\nHash every window of length L with `h = h·B + c mod P`, dropping the "
        "outgoing character with `− c·B^(L−1)`. Group start indices by hash; within a group, "
        "compare real substrings before believing a match.\n\n"
        "## Why verify\nA polynomial hash mod 10^9 + 7 over 3·10^4 windows will usually be "
        "collision-free — and \"usually\" is not a proof. Verifying keeps the answer exact at an "
        "expected cost that stays linear.\n\n"
        "## The heavyweight alternative\nA suffix array with LCP gives O(n log n) deterministically. "
        "It is rarely expected in an interview; the binary search is."
    ),
    py='''
def solve(s):
    n = len(s)

    def repeat(L):
        seen, dup = set(), None
        for i in range(n - L + 1):
            sub = s[i:i + L]
            if sub in seen and (dup is None or sub < dup):
                dup = sub
            seen.add(sub)
        return dup

    lo, hi, best = 1, n - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        r = repeat(mid)
        if r is not None:
            best, lo = r, mid + 1
        else:
            hi = mid - 1
    return best if best is not None else "NONE"
''',
    java='''
    static String repeat(String s, int L) {
        final long MOD = 1_000_000_007L, B = 131;
        long h = 0, pow = 1;
        for (int i = 0; i < L; i++) h = (h * B + s.charAt(i)) % MOD;
        for (int i = 1; i < L; i++) pow = pow * B % MOD;
        Map<Long, List<Integer>> seen = new HashMap<>();
        String best = null;
        for (int i = 0; ; i++) {
            List<Integer> starts = seen.computeIfAbsent(h, x -> new ArrayList<>());
            for (int j : starts)
                if (s.regionMatches(j, s, i, L)) {
                    String c = s.substring(i, i + L);
                    if (best == null || c.compareTo(best) < 0) best = c;
                    break;
                }
            starts.add(i);
            if (i + L >= s.length()) break;
            h = (h - s.charAt(i) * pow % MOD + MOD) % MOD;
            h = (h * B + s.charAt(i + L)) % MOD;
        }
        return best;
    }

    static String solve(String s) {
        int lo = 1, hi = s.length() - 1;
        String best = null;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            String r = repeat(s, mid);
            if (r != null) { best = r; lo = mid + 1; } else hi = mid - 1;
        }
        return best == null ? "NONE" : best;
    }
''',
    examples=[("Example 1", "abracadabra\n"), ("Example 2", "wxyz\n")],
    hidden=[
        ("Overlapping repeat", "aaaaa\n"),
        ("Tie broken alphabetically", "xyzabcxyzabd\n"),
        ("Two letters", "zz\n"),
        ("Repeat at the ends", "mnopqrmnop\n"),
        ("Two candidates, same length", "cabxcabyab\n"),
    ],
    expl=[
        "`abra` appears at 0 and 7; no 5-letter substring repeats.",
        "All letters are distinct, so nothing repeats.",
    ],
    prereqs=[
        ("binary_search", "Searching for the largest length that still works."),
        ("hashing", "A rolling hash to compare windows in O(1)."),
    ],
)

_p(
    "string-period", "Shortest Repeating Unit", "Medium",
    topics=["Strings"], subtopics=["Prefix Function", "Periodicity"], companies=["Google"],
    shape="str", ret="long", todo="compute the prefix function; the shortest period is n − pi[n − 1]",
    description=(
        "A string has period `p` if `s[i] = s[i + p]` for every valid `i` — equivalently, `s` is a "
        "prefix of its first `p` letters repeated forever. Print the **smallest** period. (The whole "
        "length `n` is always a period.)\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe smallest period."
    ),
    constraints="1 ≤ |s| ≤ 10^5\nLowercase English letters",
    hints=[
        "Trying each p and checking the whole string is O(n²).",
        "If s has period p, the prefix of length n − p equals the suffix of length n − p — a border.",
        "The longest border is pi[n − 1] from the prefix function, so the shortest period is n − pi[n − 1].",
    ],
    opt=("O(n)", "O(n)", "One prefix-function pass."),
    editorial=(
        "## The one thing this teaches\n**Periods and borders are the same fact.** A border is a "
        "proper prefix that is also a suffix. If `s` has a border of length b, sliding `s` by n − b "
        "lines it up with itself, so n − b is a period — and the longest border gives the shortest "
        "period.\n\n"
        "## Approach\n```java\nint[] pi = new int[n];\nfor (int i = 1, k = 0; i < n; i++) {\n"
        "    while (k > 0 && s.charAt(i) != s.charAt(k)) k = pi[k - 1];\n"
        "    if (s.charAt(i) == s.charAt(k)) k++;\n    pi[i] = k;\n}\nreturn n - pi[n - 1];\n```\n\n"
        "## Example\n`abcabcab`: the longest border is `abcab` (length 5), so the period is 8 − 5 = 3: "
        "`abc` repeated and cut off.\n\n"
        "## A related question\n\"Is s *exactly* a repetition of a smaller block?\" — yes when the "
        "period p is less than n and divides n."
    ),
    py='''
def solve(s):
    n = len(s)
    pi = [0] * n
    k = 0
    for i in range(1, n):
        while k and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return n - pi[n - 1]
''',
    java='''
    static long solve(String s) {
        int n = s.length();
        for (int p = 1; p <= n; p++) {
            boolean ok = true;
            for (int i = 0; i + p < n && ok; i++) ok = s.charAt(i) == s.charAt(i + p);
            if (ok) return p;
        }
        return n;
    }
''',
    examples=[("Example 1", "abcabcab\n"), ("Example 2", "abcd\n"), ("Example 3", "zzzz\n")],
    hidden=[
        ("One letter", "q\n"),
        ("Exact repetition", "xyxyxy\n"),
        ("Near miss at the end", "abaabaabb\n"),
        ("Border overlaps itself", "aabaaab\n"),
    ],
    expl=[
        "The longest border is `abcab`; 8 − 5 = 3, and `abc` repeated gives `abcabcab`.",
        "No border, so the only period is the whole length.",
        "Every letter equals the next, so the period is 1.",
    ],
    prereqs=[
        ("string_basics", "Prefixes, suffixes, and shifting a string against itself."),
        ("two_pointers", "The prefix function's fallback pointer."),
    ],
)

_p(
    "range-sum-point-update", "Range Sums With Updates", "Medium",
    topics=["Data Structures", "Prefix Sums"], subtopics=["Fenwick Tree", "Binary Indexed Tree"], companies=["Google", "Amazon"],
    shape="arr_ops", ret="String", todo="a Fenwick tree: `set` adds the difference at i; `sum l r` is prefix(r) − prefix(l − 1)",
    description=(
        "Process `q` operations on an array:\n\n- `set i v` — set `a[i] = v`.\n"
        "- `sum l r` — print `a[l] + … + a[r]` (inclusive, 0-based).\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` values.\nLine 3: `q`.\nNext `q` lines: an operation.\n\n"
        "### Output\nOne line per `sum`."
    ),
    constraints="1 ≤ n, q ≤ 10^5\n|values| ≤ 10^9\nAt least one `sum`",
    hints=[
        "A prefix-sum array answers `sum` in O(1) but must be rebuilt in O(n) after every `set`.",
        "Aim for O(log n) for both. A Fenwick tree stores, at index i, the sum of a block whose length is i's lowest set bit.",
        "Update: `for (i++; i <= n; i += i & -i) tree[i] += delta`. Prefix sum: `for (i++; i > 0; i -= i & -i) s += tree[i]`.",
    ],
    opt=("O((n + q) log n)", "O(n)", "A Fenwick tree: O(log n) point update and O(log n) prefix sum."),
    editorial=(
        "## The one thing this teaches\n**Prefix sums that survive updates.** A prefix-sum array is "
        "all queries and no updates; the raw array is all updates and no queries. A Fenwick tree "
        "splits the difference: each index covers a block sized by its lowest set bit, so both "
        "operations touch O(log n) blocks.\n\n"
        "## Approach\n```java\nlong[] tree = new long[n + 1];              // 1-based\n\n"
        "void add(int i, long delta) {                 // a[i] += delta\n"
        "    for (i++; i <= n; i += i & -i) tree[i] += delta;\n}\n\n"
        "long prefix(int i) {                           // a[0] + … + a[i]\n"
        "    long s = 0;\n    for (i++; i > 0; i -= i & -i) s += tree[i];\n    return s;\n}\n\n"
        "// set i v:   add(i, v - a[i]); a[i] = v;\n// sum l r:   prefix(r) - (l > 0 ? prefix(l - 1) : 0)\n```\n\n"
        "## Why `i & -i`\nIn two's complement, `-i` flips every bit above the lowest set bit, so the "
        "AND keeps exactly that bit. Adding it jumps to the next block that covers i; subtracting it "
        "jumps to the block just before i's.\n\n"
        "## `set` is an `add`\nThe tree stores sums, so a new value goes in as the *difference* from "
        "the old — which means you also keep the plain array."
    ),
    py='''
def solve(a, ops):
    a = list(a)
    out = []
    for op in ops:
        if op[0] == "set":
            a[int(op[1])] = int(op[2])
        else:
            l, r = int(op[1]), int(op[2])
            out.append(str(sum(a[l:r + 1])))
    return "\\n".join(out)
''',
    java='''
    static long[] tree;
    static int N;

    static void add(int i, long delta) { for (i++; i <= N; i += i & -i) tree[i] += delta; }

    static long prefix(int i) {
        long s = 0;
        for (i++; i > 0; i -= i & -i) s += tree[i];
        return s;
    }

    static String solve(int[] a, String[][] ops) {
        N = a.length;
        tree = new long[N + 1];
        long[] cur = new long[N];
        for (int i = 0; i < N; i++) { cur[i] = a[i]; add(i, a[i]); }
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("set")) {
                int i = Integer.parseInt(op[1]);
                long v = Long.parseLong(op[2]);
                add(i, v - cur[i]);
                cur[i] = v;
            } else {
                int l = Integer.parseInt(op[1]), r = Integer.parseInt(op[2]);
                if (sb.length() > 0) sb.append('\\n');
                sb.append(prefix(r) - (l > 0 ? prefix(l - 1) : 0));
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n3 1 4 1 5\n4\nsum 0 4\nset 2 10\nsum 1 3\nsum 2 2\n"),
        ("Example 2", "1\n-7\n2\nsum 0 0\nset 0 7\n"),
    ],
    hidden=[
        ("Updates only at the ends", "4\n1 2 3 4\n5\nset 0 100\nset 3 -100\nsum 0 3\nsum 1 2\nsum 0 0\n"),
        ("Large values", "3\n1000000000 1000000000 1000000000\n2\nsum 0 2\nsum 1 1\n"),
        ("Many sets on one index", "3\n0 0 0\n6\nset 1 5\nset 1 9\nset 1 -2\nsum 0 2\nset 1 0\nsum 1 1\n"),
    ],
    expl=[
        "3 + 1 + 4 + 1 + 5 = 14. After a[2] = 10: 1 + 10 + 1 = 12, and a[2] alone is 10.",
        "A single sum of −7; the later set prints nothing.",
    ],
    prereqs=[
        ("prefix_sum", "A range sum as the difference of two prefix sums."),
        ("bit_manip", "`i & -i` isolates the lowest set bit."),
    ],
)

_p(
    "range-min-queries", "Range Minimum With Updates", "Medium",
    topics=["Data Structures", "Trees"], subtopics=["Segment Tree"], companies=["Google", "Uber"],
    shape="arr_ops", ret="String", todo="a segment tree over the array: `set` rewrites a leaf and its ancestors; `min l r` combines O(log n) nodes",
    description=(
        "Process `q` operations on an array:\n\n- `set i v` — set `a[i] = v`.\n"
        "- `min l r` — print the minimum of `a[l] … a[r]` (inclusive, 0-based).\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` values.\nLine 3: `q`.\nNext `q` lines: an operation.\n\n"
        "### Output\nOne line per `min`."
    ),
    constraints="1 ≤ n, q ≤ 10^5\n|values| ≤ 10^9\nAt least one `min`",
    hints=[
        "A Fenwick tree answers a range *sum* as prefix(r) − prefix(l − 1). Minimum has no subtraction, so prefixes cannot be combined that way.",
        "A segment tree stores the minimum of every node's range; a query range is covered by O(log n) nodes.",
        "Iterative version: leaves at `size + i`, parent `p/2`, children `2p` and `2p + 1`. Query by walking l and r up towards each other.",
    ],
    opt=("O((n + q) log n)", "O(n)", "A segment tree: O(log n) update and O(log n) range query."),
    editorial=(
        "## The one thing this teaches\n**A segment tree works for any associative combine, not only "
        "sums.** A Fenwick tree needs an inverse (sums subtract), and minimum has none. A segment tree "
        "never subtracts: it covers `[l, r]` exactly with O(log n) stored ranges and combines them.\n\n"
        "## Approach (iterative, bottom-up)\n```java\nint size = n;\nlong[] t = new long[2 * size];\n"
        "for (int i = 0; i < n; i++) t[size + i] = a[i];\n"
        "for (int p = size - 1; p > 0; p--) t[p] = Math.min(t[2 * p], t[2 * p + 1]);\n\n"
        "void set(int i, long v) {\n    for (t[i += size] = v; i > 1; i >>= 1) t[i >> 1] = Math.min(t[i], t[i ^ 1]);\n}\n\n"
        "long min(int l, int r) {                       // inclusive\n    long res = Long.MAX_VALUE;\n"
        "    for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {\n"
        "        if ((l & 1) == 1) res = Math.min(res, t[l++]);\n"
        "        if ((r & 1) == 1) res = Math.min(res, t[--r]);\n    }\n    return res;\n}\n```\n\n"
        "## Picking the structure\n| Need | Use |\n| --- | --- |\n| Range sum, point update | Fenwick |\n"
        "| Range min/max/gcd, point update | Segment tree |\n| Range update and range query | Segment tree with lazy propagation (or two Fenwicks for sums) |\n"
        "| No updates at all | Prefix sums, or a sparse table for min |"
    ),
    py='''
def solve(a, ops):
    a = list(a)
    out = []
    for op in ops:
        if op[0] == "set":
            a[int(op[1])] = int(op[2])
        else:
            out.append(str(min(a[int(op[1]):int(op[2]) + 1])))
    return "\\n".join(out)
''',
    java='''
    static String solve(int[] a, String[][] ops) {
        int size = a.length;
        long[] t = new long[2 * size];
        for (int i = 0; i < size; i++) t[size + i] = a[i];
        for (int p = size - 1; p > 0; p--) t[p] = Math.min(t[2 * p], t[2 * p + 1]);
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("set")) {
                int i = Integer.parseInt(op[1]) + size;
                t[i] = Long.parseLong(op[2]);
                for (; i > 1; i >>= 1) t[i >> 1] = Math.min(t[i], t[i ^ 1]);
            } else {
                int l = Integer.parseInt(op[1]) + size, r = Integer.parseInt(op[2]) + size + 1;
                long res = Long.MAX_VALUE;
                for (; l < r; l >>= 1, r >>= 1) {
                    if ((l & 1) == 1) res = Math.min(res, t[l++]);
                    if ((r & 1) == 1) res = Math.min(res, t[--r]);
                }
                if (sb.length() > 0) sb.append('\\n');
                sb.append(res);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6\n5 2 8 6 3 7\n4\nmin 0 5\nmin 2 3\nset 1 9\nmin 0 2\n"),
        ("Example 2", "1\n4\n1\nmin 0 0\n"),
    ],
    hidden=[
        ("Odd length, full range", "7\n9 8 7 6 5 4 3\n3\nmin 0 6\nmin 0 3\nmin 4 5\n"),
        ("Lowering then raising a value", "4\n10 10 10 10\n4\nset 2 -5\nmin 1 3\nset 2 50\nmin 1 3\n"),
        ("Negative extremes", "3\n-1000000000 0 1000000000\n2\nmin 1 2\nmin 0 2\n"),
    ],
    expl=[
        "The minimum overall is 2, and of [8, 6] is 6. After a[1] = 9, [5, 9, 8] has minimum 5.",
        "A one-element range.",
    ],
    prereqs=[
        ("tree_basics", "A complete binary tree stored in an array."),
        ("bit_manip", "Parents and siblings by shifting and XOR."),
    ],
)

_p(
    "count-smaller-after-self", "Smaller Values to the Right", "Hard",
    topics=["Data Structures", "Sorting"], subtopics=["Fenwick Tree", "Coordinate Compression"], companies=["Google", "Amazon"],
    shape="arr", ret="String", todo="compress values to ranks; scan from the right, query how many ranks below a[i] are present, then add a[i]",
    description=(
        "For every index `i`, count how many elements to its **right** are strictly smaller than "
        "`a[i]`.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe `n` counts, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "Scanning everything to the right is O(n²).",
        "Walk from the right. Then \"elements to my right\" is \"elements seen so far\", and the question is how many seen elements are smaller.",
        "Replace each value by its rank among the distinct values. A Fenwick tree over ranks counts seen elements with rank < r in O(log n).",
    ],
    opt=("O(n log n)", "O(n)", "Sort for ranks, then one right-to-left pass of Fenwick queries and updates."),
    editorial=(
        "## The one thing this teaches\n**Scan order turns \"to my right\" into \"already seen\", and "
        "ranks turn values into indices.** A Fenwick tree indexed by value would need 2·10^9 slots; "
        "indexed by *rank* it needs n.\n\n"
        "## Approach\n```java\nint[] sorted = Arrays.stream(a).distinct().sorted().toArray();\n"
        "long[] tree = new long[sorted.length + 1];\nint[] res = new int[n];\n"
        "for (int i = n - 1; i >= 0; i--) {\n    int r = Arrays.binarySearch(sorted, a[i]);      // 0-based rank\n"
        "    res[i] = (int) prefix(tree, r - 1);          // seen with a smaller rank\n"
        "    add(tree, r, 1);\n}\n```\n\n"
        "## Strictly smaller\nQuery ranks `0 … r − 1`, not `0 … r`: an equal value to the right does "
        "not count. That off-by-one is the usual wrong answer on inputs with duplicates.\n\n"
        "## The other O(n log n)\nMerge sort, counting for each left-half element how many right-half "
        "elements were placed before it — the count-inversions merge, tracked per original index."
    ),
    py='''
def solve(a):
    seen, out = [], []
    for x in reversed(a):
        out.append(bisect_left(seen, x))
        seen.insert(bisect_left(seen, x), x)
    return " ".join(map(str, reversed(out)))
''',
    java='''
    static void add(long[] t, int i, long d) { for (i++; i < t.length; i += i & -i) t[i] += d; }

    static long prefix(long[] t, int i) {
        long s = 0;
        for (i++; i > 0; i -= i & -i) s += t[i];
        return s;
    }

    static String solve(int[] a) {
        int n = a.length;
        int[] sorted = Arrays.stream(a).distinct().sorted().toArray();
        long[] tree = new long[sorted.length + 1];
        int[] res = new int[n];
        for (int i = n - 1; i >= 0; i--) {
            int r = Arrays.binarySearch(sorted, a[i]);
            res[i] = (int) prefix(tree, r - 1);
            add(tree, r, 1);
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(res[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "5\n7 3 9 3 1\n"), ("Example 2", "3\n1 2 3\n")],
    hidden=[
        ("One element", "1\n42\n"),
        ("Descending", "5\n5 4 3 2 1\n"),
        ("All equal", "4\n6 6 6 6\n"),
        ("Extremes", "4\n1000000000 -1000000000 0 -1000000000\n"),
    ],
    expl=[
        "Right of 7 are 3, 9, 3, 1: three are smaller. Right of the first 3, only 1 is smaller — the other 3 is equal.",
        "Ascending, so nothing to the right is smaller.",
    ],
    prereqs=[
        ("prefix_sum", "Counting as a prefix sum over ranks."),
        ("sorting", "Coordinate compression: values to ranks."),
    ],
)

_p(
    "range-add-range-sum", "Range Additions and Range Sums", "Hard",
    topics=["Data Structures", "Prefix Sums"], subtopics=["Fenwick Tree", "Difference Array"], companies=["Google"],
    shape="arr_ops", ret="String", todo="two Fenwick trees B1, B2: add v on [l, r] updates both at l and r + 1; prefix(i) = sum(B1, i)·(i + 1) − sum(B2, i)",
    description=(
        "Process `q` operations on an array:\n\n- `add l r v` — add `v` to every `a[l] … a[r]`.\n"
        "- `sum l r` — print `a[l] + … + a[r]`.\n\nRanges are inclusive and 0-based.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` values.\nLine 3: `q`.\nNext `q` lines: an operation.\n\n"
        "### Output\nOne line per `sum`."
    ),
    constraints="1 ≤ n, q ≤ 10^5\n|a[i]| ≤ 10^9\n|v| ≤ 10^4\nAt least one `sum`",
    hints=[
        "A difference array makes a range add O(1) — but then every sum needs a prefix of a prefix.",
        "Keep the difference array d in a Fenwick tree. a[i] = d[0] + … + d[i], so prefix(i) = Σ_{j ≤ i} d[j]·(i − j + 1).",
        "Split that into (i + 1)·Σ d[j] − Σ d[j]·j. Two Fenwick trees hold d[j] and d[j]·j; a range add is two point updates to each.",
    ],
    opt=("O((n + q) log n)", "O(n)", "Two Fenwick trees over the difference array and its index-weighted version."),
    editorial=(
        "## The one thing this teaches\n**Change what you store until the operation becomes a point "
        "update.** A range add is two point updates to a difference array; a range sum over a "
        "difference array is a weighted prefix sum; and a weighted prefix sum is two ordinary ones.\n\n"
        "## The algebra\nWith `a[i] = Σ_{j≤i} d[j]`:\n\n"
        "`prefix(i) = Σ_{j≤i} d[j]·(i + 1 − j) = (i + 1)·Σ d[j] − Σ d[j]·j`\n\n"
        "## Approach\n```java\nlong[] b1 = new long[n + 1], b2 = new long[n + 1];\n\n"
        "void rangeAdd(int l, int r, long v) {\n    add(b1, l, v);        add(b1, r + 1, -v);\n"
        "    add(b2, l, v * l);    add(b2, r + 1, -v * (r + 1));\n}\n\n"
        "long prefix(int i) {\n    return query(b1, i) * (i + 1) - query(b2, i);\n}\n```\n\n"
        "Load the initial array as n range adds of length one, or keep its plain prefix sums alongside.\n\n"
        "## When to reach for a lazy segment tree instead\nWhen the update or query is not a sum — "
        "\"set every value in a range\", or range add with range minimum."
    ),
    py='''
def solve(a, ops):
    a = list(a)
    out = []
    for op in ops:
        l, r = int(op[1]), int(op[2])
        if op[0] == "add":
            v = int(op[3])
            for i in range(l, r + 1):
                a[i] += v
        else:
            out.append(str(sum(a[l:r + 1])))
    return "\\n".join(out)
''',
    java='''
    static int N;
    static long[] b1, b2;

    static void upd(long[] t, int i, long d) { for (i++; i <= N; i += i & -i) t[i] += d; }

    static long qry(long[] t, int i) {
        long s = 0;
        for (i++; i > 0; i -= i & -i) s += t[i];
        return s;
    }

    static void rangeAdd(int l, int r, long v) {
        upd(b1, l, v);
        upd(b2, l, v * l);
        if (r + 1 < N) { upd(b1, r + 1, -v); upd(b2, r + 1, -v * (r + 1)); }
    }

    static long prefix(int i) { return i < 0 ? 0 : qry(b1, i) * (i + 1) - qry(b2, i); }

    static String solve(int[] a, String[][] ops) {
        N = a.length;
        b1 = new long[N + 1];
        b2 = new long[N + 1];
        for (int i = 0; i < N; i++) rangeAdd(i, i, a[i]);
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            int l = Integer.parseInt(op[1]), r = Integer.parseInt(op[2]);
            if (op[0].equals("add")) rangeAdd(l, r, Long.parseLong(op[3]));
            else {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(prefix(r) - prefix(l - 1));
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "5\n1 2 3 4 5\n4\nsum 0 4\nadd 1 3 10\nsum 0 4\nsum 2 2\n"),
        ("Example 2", "3\n0 0 0\n3\nadd 0 2 -4\nadd 1 1 4\nsum 0 2\n"),
    ],
    hidden=[
        ("Whole-array adds", "4\n5 5 5 5\n4\nadd 0 3 1\nadd 0 3 1\nsum 0 3\nsum 3 3\n"),
        ("Overlapping ranges", "6\n0 0 0 0 0 0\n5\nadd 0 3 2\nadd 2 5 3\nsum 0 1\nsum 2 3\nsum 4 5\n"),
        ("Large initial values", "3\n1000000000 -1000000000 1000000000\n3\nadd 0 1 10000\nsum 0 2\nsum 1 1\n"),
    ],
    expl=[
        "15 at first; adding 10 to three elements makes it 45; a[2] is now 13.",
        "The array becomes [−4, 0, −4], summing to −8.",
    ],
    prereqs=[
        ("prefix_sum", "The difference array: a range add as two point changes."),
        ("bit_manip", "Fenwick-tree index jumps with `i & -i`."),
    ],
)

_p(
    "euler-path-exists", "Draw It Without Lifting the Pen", "Easy",
    topics=["Graphs"], subtopics=["Eulerian Path", "Degrees"], companies=["Google"],
    shape="graph", ret="String", todo="count odd-degree vertices (must be 0 or 2) and check every vertex with an edge is in one component",
    description=(
        "An undirected graph is drawn as dots and lines. Can you trace **every line exactly once** "
        "in one continuous stroke (you may pass through a dot many times)? Print `true` or `false`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: an edge `u v`. Repeated edges are separate lines "
        "to trace.\n\n"
        "### Output\n`true` or `false`."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ m ≤ 2·10^5\nNo self-loops",
    hints=[
        "Trying stroke orders is backtracking over m! possibilities. The answer depends only on two counts.",
        "Every time the stroke passes through a dot it uses two of its lines — one in, one out. Only the start and end can use an odd number.",
        "So: the number of odd-degree vertices is 0 or 2, and all vertices that have edges are connected. Isolated dots do not matter.",
    ],
    opt=("O(n + m)", "O(n)", "A degree count and one connectivity check."),
    editorial=(
        "## The one thing this teaches\n**Some search problems have a counting answer.** Euler's "
        "theorem replaces a search over stroke orders with two checks: degrees and connectivity.\n\n"
        "## Why degrees\nEach pass through a vertex consumes one edge in and one edge out, so interior "
        "visits use edges in pairs. A vertex with odd degree must therefore be where the stroke starts "
        "or ends — and there are only two ends. (With 0 odd vertices the stroke is a closed circuit.)\n\n"
        "## Approach\n```java\nint odd = 0;\nfor (int v = 0; v < n; v++) if (deg[v] % 2 == 1) odd++;\n"
        "if (odd != 0 && odd != 2) return false;\n"
        "// every vertex with deg > 0 must be reachable from any one of them\n"
        "return allEdgesInOneComponent(adj, deg);\n```\n\n"
        "## The connectivity trap\nTwo separate triangles have every degree even, and still cannot be "
        "drawn in one stroke. Check that the vertices with edges form one component — and ignore the "
        "isolated ones, which have nothing to draw.\n\n"
        "## Actually drawing it\nHierholzer's algorithm finds the stroke in O(m); *Rebuild the "
        "Itinerary* uses it."
    ),
    py='''
def solve(n, edges):
    deg = [0] * n
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        parent[find(u)] = find(v)
    if sum(1 for d in deg if d % 2) not in (0, 2):
        return "false"
    roots = {find(v) for v in range(n) if deg[v] > 0}
    return "true" if len(roots) <= 1 else "false"
''',
    java='''
    static String solve(int n, int[][] edges) {
        int[] deg = new int[n];
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) {
            deg[e[0]]++; deg[e[1]]++;
            adj.get(e[0]).add(e[1]);
            adj.get(e[1]).add(e[0]);
        }
        int odd = 0, start = -1, withEdges = 0;
        for (int v = 0; v < n; v++) {
            if (deg[v] % 2 == 1) odd++;
            if (deg[v] > 0) { withEdges++; if (start < 0) start = v; }
        }
        if (odd != 0 && odd != 2) return "false";
        boolean[] seen = new boolean[n];
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add(start);
        seen[start] = true;
        int reached = 0;
        while (!q.isEmpty()) {
            int u = q.poll();
            reached++;
            for (int v : adj.get(u)) if (!seen[v]) { seen[v] = true; q.add(v); }
        }
        return reached == withEdges ? "true" : "false";
    }
''',
    examples=[("Example 1", "4 5\n0 1\n1 2\n2 0\n0 3\n3 2\n"), ("Example 2", "4 3\n0 1\n0 2\n0 3\n")],
    hidden=[
        ("A single line", "2 1\n0 1\n"),
        ("Two separate triangles", "6 6\n0 1\n1 2\n2 0\n3 4\n4 5\n5 3\n"),
        ("Isolated dots are fine", "5 3\n1 2\n2 3\n3 1\n"),
        ("A doubled line", "3 3\n0 1\n0 1\n1 2\n"),
        ("Four odd vertices", "4 2\n0 1\n2 3\n"),
    ],
    expl=[
        "Vertices 1 and 3 have degree 2, 0 and 2 have degree 3 — exactly two odd ones, and the graph is connected: start at 0, end at 2.",
        "Vertex 0 has degree 3 and each leaf degree 1: four odd vertices.",
    ],
    prereqs=[
        ("graph_repr", "Degrees from an edge list."),
        ("union_find", "Checking that every edge lies in one component."),
    ],
)

_p(
    "articulation-points", "Critical Junctions", "Medium",
    topics=["Graphs"], subtopics=["Articulation Points", "DFS Low-Link"], companies=["Amazon", "Google"],
    shape="graph", ret="String", todo="DFS with discovery times and low-links; a non-root u is critical if some child v has low[v] ≥ disc[u]; the root if it has two DFS children",
    description=(
        "A road network is an undirected graph. A junction is **critical** if removing it (and its "
        "roads) leaves some other pair of junctions that were connected unable to reach each other. "
        "Print the critical junctions in increasing order, or `none`.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: a road `u v`.\n\n"
        "### Output\nThe critical junctions, separated by spaces, or `none`."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 2·10^4\nNo self-loops or repeated roads\nThe graph may be disconnected",
    hints=[
        "Removing each vertex and re-running a traversal is O(n·(n + m)).",
        "In a DFS tree, a vertex u matters when one of its subtrees has no edge climbing back above u.",
        "Track disc[u] (visit time) and low[u] (the earliest disc reachable from u's subtree with one back edge). Child v with low[v] ≥ disc[u] means u is critical — except at the root, which is critical only with 2+ DFS children.",
    ],
    opt=("O(n + m)", "O(n)", "One DFS computing discovery times and low-links."),
    editorial=(
        "## The one thing this teaches\n**One DFS knows which subtrees can escape.** `low[v]` is the "
        "earliest-discovered vertex that v's subtree can reach using tree edges down and one back "
        "edge up. If a child's subtree cannot get above u, removing u cuts it off.\n\n"
        "## Approach\n```java\nvoid dfs(int u, int parent) {\n    disc[u] = low[u] = ++timer;\n    int children = 0;\n"
        "    for (int v : adj[u]) {\n        if (v == parent) continue;\n"
        "        if (disc[v] != 0) { low[u] = Math.min(low[u], disc[v]); continue; }   // back edge\n"
        "        children++;\n        dfs(v, u);\n        low[u] = Math.min(low[u], low[v]);\n"
        "        if (parent != -1 && low[v] >= disc[u]) critical[u] = true;\n    }\n"
        "    if (parent == -1 && children > 1) critical[u] = true;           // root rule\n}\n```\n\n"
        "## Why the root is special\nThe root has nothing above it, so `low[v] ≥ disc[root]` always "
        "holds. It is critical exactly when the DFS had to start two separate subtrees from it.\n\n"
        "## Bridges are the same DFS\nAn *edge* u–v is a bridge when `low[v] > disc[u]` — strictly "
        "greater, because v's subtree cannot even reach u without that edge."
    ),
    py='''
def solve(n, edges):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    def components(skip):
        seen = [False] * n
        count = 0
        for s in range(n):
            if s == skip or seen[s]:
                continue
            count += 1
            seen[s] = True
            stack = [s]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y != skip and not seen[y]:
                        seen[y] = True
                        stack.append(y)
        return count

    base = components(-1)
    out = [str(v) for v in range(n) if adj[v] and components(v) > base]
    return " ".join(out) if out else "none"
''',
    java='''
    static List<List<Integer>> adj;
    static int[] disc, low;
    static boolean[] crit;
    static int timer;

    static void dfs(int u, int parent) {
        disc[u] = low[u] = ++timer;
        int children = 0;
        for (int v : adj.get(u)) {
            if (v == parent) continue;
            if (disc[v] != 0) { low[u] = Math.min(low[u], disc[v]); continue; }
            children++;
            dfs(v, u);
            low[u] = Math.min(low[u], low[v]);
            if (parent != -1 && low[v] >= disc[u]) crit[u] = true;
        }
        if (parent == -1 && children > 1) crit[u] = true;
    }

    static String solve(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }
        disc = new int[n]; low = new int[n]; crit = new boolean[n]; timer = 0;
        for (int v = 0; v < n; v++) if (disc[v] == 0) dfs(v, -1);
        StringBuilder sb = new StringBuilder();
        for (int v = 0; v < n; v++) if (crit[v]) { if (sb.length() > 0) sb.append(' '); sb.append(v); }
        return sb.length() == 0 ? "none" : sb.toString();
    }
''',
    examples=[("Example 1", "5 5\n0 1\n1 2\n2 0\n1 3\n3 4\n"), ("Example 2", "4 4\n0 1\n1 2\n2 3\n3 0\n")],
    hidden=[
        ("A path", "4 3\n0 1\n1 2\n2 3\n"),
        ("A star", "5 4\n0 1\n0 2\n0 3\n0 4\n"),
        ("Two triangles joined at a vertex", "5 6\n0 1\n1 2\n2 0\n2 3\n3 4\n4 2\n"),
        ("Disconnected pieces", "6 3\n0 1\n1 2\n4 5\n"),
        ("No roads", "3 0\n"),
    ],
    expl=[
        "Removing 1 cuts 3 and 4 off from 0 and 2; removing 3 cuts off 4.",
        "A cycle survives the loss of any one junction.",
    ],
    prereqs=[
        ("graph_repr", "Adjacency lists for an undirected graph."),
        ("graph_cycle", "Back edges in a DFS tree."),
    ],
)

_p(
    "count-scc", "Count Strongly Connected Groups", "Medium",
    topics=["Graphs"], subtopics=["Strongly Connected Components", "Tarjan's Algorithm"], companies=["Google", "Microsoft"],
    shape="graph", ret="long", todo="Tarjan: DFS with a stack; when low[u] == disc[u], pop the stack down to u — that is one component",
    description=(
        "In a directed graph, two vertices are in the same **strongly connected component** when "
        "each can reach the other. Print the number of components.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: a directed edge `u v`.\n\n"
        "### Output\nThe number of strongly connected components."
    ),
    constraints="1 ≤ n ≤ 10^4\n0 ≤ m ≤ 2·10^4",
    hints=[
        "Running a traversal from every vertex and pairing up mutual reachability is O(n·(n + m)).",
        "In a DFS, each component has a first-visited vertex — its root — and everything else in the component is visited below it.",
        "Tarjan: keep visited-but-unassigned vertices on a stack and a low-link per vertex (counting only vertices still on the stack). When low[u] == disc[u], pop down to u: one component.",
    ],
    opt=("O(n + m)", "O(n)", "One DFS with a stack and low-links (Tarjan), or two DFS passes (Kosaraju)."),
    editorial=(
        "## The one thing this teaches\n**A component is found when its root finishes.** In the DFS, "
        "the root of a strongly connected component is the first of its vertices visited. Nothing "
        "below it can reach anything visited earlier and still on the stack, so `low[root] == disc[root]` "
        "— and the component is exactly the stack above it.\n\n"
        "## Approach\n```java\nvoid dfs(int u) {\n    disc[u] = low[u] = ++timer;\n    stack.push(u); onStack[u] = true;\n"
        "    for (int v : adj[u]) {\n        if (disc[v] == 0) { dfs(v); low[u] = Math.min(low[u], low[v]); }\n"
        "        else if (onStack[v]) low[u] = Math.min(low[u], disc[v]);   // only unassigned vertices count\n    }\n"
        "    if (low[u] == disc[u]) {                      // u is a root\n"
        "        int x;\n        do { x = stack.pop(); onStack[x] = false; } while (x != u);\n"
        "        components++;\n    }\n}\n```\n\n"
        "## Why `onStack`\nAn edge to a vertex already assigned to an *earlier* component is a one-way "
        "street out; it must not lower `low[u]`. Checking only `disc[v] != 0` merges components that "
        "are not mutually reachable.\n\n"
        "## Kosaraju, for comparison\nDFS once to record finish order; reverse every edge; DFS again in "
        "decreasing finish order. Each second-pass tree is a component. Two passes, but no low-links."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    seen, order = [False] * n, []
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        stack = [(s, 0)]
        while stack:
            u, i = stack.pop()
            if i < len(adj[u]):
                stack.append((u, i + 1))
                v = adj[u][i]
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)
    comp = [-1] * n
    count = 0
    for s in reversed(order):
        if comp[s] != -1:
            continue
        comp[s] = count
        stack = [s]
        while stack:
            u = stack.pop()
            for v in radj[u]:
                if comp[v] == -1:
                    comp[v] = count
                    stack.append(v)
        count += 1
    return count
''',
    java='''
    static List<List<Integer>> adj;
    static int[] disc, low;
    static boolean[] onStack;
    static ArrayDeque<Integer> st;
    static int timer, comps;

    static void dfs(int u) {
        disc[u] = low[u] = ++timer;
        st.push(u);
        onStack[u] = true;
        for (int v : adj.get(u)) {
            if (disc[v] == 0) { dfs(v); low[u] = Math.min(low[u], low[v]); }
            else if (onStack[v]) low[u] = Math.min(low[u], disc[v]);
        }
        if (low[u] == disc[u]) {
            int x;
            do { x = st.pop(); onStack[x] = false; } while (x != u);
            comps++;
        }
    }

    static long solve(int n, int[][] edges) {
        adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) adj.get(e[0]).add(e[1]);
        disc = new int[n]; low = new int[n]; onStack = new boolean[n];
        st = new ArrayDeque<>();
        timer = 0; comps = 0;
        for (int v = 0; v < n; v++) if (disc[v] == 0) dfs(v);
        return comps;
    }
''',
    examples=[("Example 1", "5 6\n0 1\n1 2\n2 0\n1 3\n3 4\n4 3\n"), ("Example 2", "3 2\n0 1\n1 2\n")],
    hidden=[
        ("One vertex", "1 0\n"),
        ("One big cycle", "4 4\n0 1\n1 2\n2 3\n3 0\n"),
        ("Two cycles, one-way link", "6 7\n0 1\n1 0\n2 3\n3 4\n4 2\n1 2\n5 5\n"),
        ("Edge into a finished component", "4 4\n0 1\n1 0\n2 3\n3 1\n"),
    ],
    expl=[
        "{0, 1, 2} is a cycle and {3, 4} is a cycle; the edge 1 → 3 goes one way only.",
        "A path: no vertex can get back, so each is its own component.",
    ],
    prereqs=[
        ("graph_cycle", "Cycles in a directed graph found by DFS."),
        ("stack", "An explicit stack of vertices not yet assigned."),
    ],
)

_p(
    "reconstruct-itinerary", "Rebuild the Itinerary", "Hard",
    topics=["Graphs"], subtopics=["Eulerian Path", "Hierholzer's Algorithm"], companies=["Google", "Uber"],
    shape="tickets", ret="String", todo="Hierholzer: from the start, always take the alphabetically smallest unused ticket; when stuck, prepend the airport",
    description=(
        "You found `m` flight tickets `FROM TO` from one trip. The trip started at the departure "
        "airport of the **first** ticket listed and used every ticket exactly once. Several orders "
        "may be possible: print the one that is alphabetically smallest when read as a list of airport "
        "codes.\n\n"
        "### Input\nLine 1: `m`.\nNext `m` lines: `FROM TO` (three capital letters each).\n\n"
        "### Output\nThe airports in order, separated by spaces."
    ),
    constraints="1 ≤ m ≤ 10^4\nA valid itinerary is guaranteed",
    hints=[
        "Greedily flying to the smallest destination can strand you with tickets left over — try SAN→AAA, SAN→BBB, BBB→SAN.",
        "Using every ticket once is an Eulerian path. Hierholzer's algorithm builds one without backtracking.",
        "DFS that always takes the smallest remaining ticket; when an airport has no tickets left, append it to the route. The route comes out reversed: dead ends are added first.",
    ],
    opt=("O(m log m)", "O(m)", "Hierholzer over adjacency lists kept in priority queues."),
    editorial=(
        "## The one thing this teaches\n**Hierholzer: walk until stuck, and record airports on the way "
        "back.** The first airport you get stuck at is the itinerary's last. Any tickets skipped on the "
        "way out form a detour, and it is spliced in automatically because the route is built from "
        "the end.\n\n"
        "## Approach\n```java\nMap<String, PriorityQueue<String>> out = new HashMap<>();\n"
        "LinkedList<String> route = new LinkedList<>();\n\nvoid visit(String a) {\n"
        "    PriorityQueue<String> q = out.get(a);\n"
        "    while (q != null && !q.isEmpty()) visit(q.poll());   // use the ticket, then go\n"
        "    route.addFirst(a);                                     // stuck here: this comes last\n}\n```\n\n"
        "## Why greedy alone fails\nFrom SAN with tickets to AAA and BBB, the smallest is AAA — and AAA "
        "has no tickets out. The walk ends early, AAA is recorded first (so it lands *last*), and "
        "the unwinding picks up SAN → BBB → SAN before it. The route is SAN BBB SAN AAA.\n\n"
        "## Deep recursion\nWith 10^4 tickets the recursion can be 10^4 deep; an explicit stack "
        "avoids overflowing Java's default thread stack."
    ),
    py='''
def solve(tickets):
    out = defaultdict(list)
    for a, b in tickets:
        out[a].append(b)
    for a in out:
        out[a].sort()
    m = len(tickets)
    used = {a: [False] * len(out[a]) for a in out}
    route = [tickets[0][0]]

    def go(a):
        if len(route) == m + 1:
            return True
        prev = None
        for i, b in enumerate(out.get(a, [])):
            if used[a][i] or b == prev:
                continue
            prev = b
            used[a][i] = True
            route.append(b)
            if go(b):
                return True
            route.pop()
            used[a][i] = False
        return False

    go(tickets[0][0])
    return " ".join(route)
''',
    java='''
    static Map<String, PriorityQueue<String>> out = new HashMap<>();
    static LinkedList<String> route = new LinkedList<>();

    static void visit(String a) {
        ArrayDeque<String> st = new ArrayDeque<>();
        st.push(a);
        while (!st.isEmpty()) {
            PriorityQueue<String> q = out.get(st.peek());
            if (q != null && !q.isEmpty()) st.push(q.poll());
            else route.addFirst(st.pop());
        }
    }

    static String solve(String[][] tickets) {
        for (String[] t : tickets) out.computeIfAbsent(t[0], k -> new PriorityQueue<>()).add(t[1]);
        visit(tickets[0][0]);
        return String.join(" ", route);
    }
''',
    examples=[("Example 1", "3\nSAN AAA\nSAN BBB\nBBB SAN\n"), ("Example 2", "4\nOSL CPH\nCPH BER\nBER OSL\nOSL AMS\n")],
    hidden=[
        ("One ticket", "1\nLIS MAD\n"),
        ("A plain chain", "3\nNRT ICN\nICN PEK\nPEK HKG\n"),
        ("Two loops through a hub", "6\nDXB CAI\nCAI DXB\nDXB BOM\nBOM DXB\nDXB AUH\nAUH DXB\n"),
        ("Duplicate tickets", "4\nYYZ YUL\nYUL YYZ\nYYZ YUL\nYUL YYZ\n"),
    ],
    expl=[
        "Flying SAN → AAA first strands the BBB ticket. SAN → BBB → SAN → AAA uses all three.",
        "OSL → AMS would strand the rest, so the trip loops first: OSL CPH BER OSL AMS.",
    ],
    prereqs=[
        ("graph_repr", "Directed adjacency lists, kept in alphabetical order."),
        ("stack", "Recording airports as the walk unwinds."),
    ],
)

_p(
    "subset-xor-sum-total", "Total of Every Subset's XOR", "Easy",
    topics=["Bit Manipulation", "Backtracking"], subtopics=["Bitmask Enumeration"], companies=["Amazon"],
    shape="arr", ret="long", todo="loop mask from 0 to 2^n − 1; XOR the elements whose bits are set; add it up",
    description=(
        "For every subset of the array (including the empty one, whose XOR is 0), compute the XOR of "
        "its elements. Print the sum of all those XORs.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe total."
    ),
    constraints="1 ≤ n ≤ 12\n0 ≤ a[i] ≤ 20",
    hints=[
        "There are only 2^12 = 4096 subsets. Enumerate them all.",
        "An integer mask from 0 to 2^n − 1 *is* a subset: bit i set means a[i] is included.",
        "for mask: x = 0; for i: if ((mask >> i) & 1) x ^= a[i]; total += x.",
    ],
    opt=("O(2^n · n)", "O(1)", "Every mask, every bit."),
    editorial=(
        "## The one thing this teaches\n**The integers 0 … 2^n − 1 are the subsets of n items.** No "
        "recursion and no list-building: bit i of the mask says whether item i is in. This is the "
        "representation every bitmask DP starts from.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int mask = 0; mask < (1 << n); mask++) {\n"
        "    int x = 0;\n    for (int i = 0; i < n; i++)\n        if ((mask >> i & 1) == 1) x ^= a[i];\n"
        "    total += x;\n}\n```\n\n"
        "## The O(n) shortcut\nA bit is set in the OR of all elements exactly when some element has "
        "it — and then it is set in exactly half of the 2^n subset XORs. So the total is "
        "`(a[0] | … | a[n−1]) · 2^(n−1)`. Worth knowing; the enumeration is the transferable skill.\n\n"
        "## When enumeration stops working\n2^20 ≈ 10^6 is fine; 2^30 is not. \"n ≤ 20\" in the "
        "constraints is the signal for bitmasks."
    ),
    py='''
def solve(a):
    n = len(a)
    total = 0
    for mask in range(1 << n):
        x = 0
        for i in range(n):
            if mask >> i & 1:
                x ^= a[i]
        total += x
    return total
''',
    java='''
    static long solve(int[] a) {
        int or = 0;
        for (int x : a) or |= x;
        return (long) or << (a.length - 1);
    }
''',
    examples=[("Example 1", "2\n2 7\n"), ("Example 2", "3\n4 1 3\n")],
    hidden=[
        ("One element", "1\n7\n"),
        ("All zeros", "4\n0 0 0 0\n"),
        ("Largest", "12\n20 19 18 17 16 15 14 13 12 11 10 9\n"),
        ("Duplicates", "3\n2 2 2\n"),
    ],
    expl=[
        "Subsets {}, {2}, {7}, {2, 7} have XORs 0, 2, 7, 5: total 14.",
        "The eight subset XORs are 0, 4, 1, 3, 5, 7, 2, 6, summing to 28.",
    ],
    prereqs=[
        ("bit_manip", "Testing bit i of a mask with a shift and an AND."),
        ("backtracking", "Subsets, enumerated without recursion."),
    ],
)

_p(
    "min-cost-assignment", "Assign Every Job", "Medium",
    topics=["Dynamic Programming", "Bit Manipulation"], subtopics=["Bitmask DP", "Assignment"], companies=["Google", "Uber"],
    shape="matrix", ret="long", todo="dp[mask] = cheapest way to give the jobs in mask to the first popcount(mask) workers",
    description=(
        "`n` workers and `n` jobs; `cost[i][j]` is what worker `i` charges for job `j`. Give every "
        "worker exactly one job and every job to exactly one worker. Print the minimum total cost.\n\n"
        "### Input\nLine 1: `n n`.\nNext `n` lines: `n` costs.\n\n"
        "### Output\nThe minimum total cost."
    ),
    constraints="1 ≤ n ≤ 16\n0 ≤ cost ≤ 10^6",
    hints=[
        "Trying every assignment is n! — 2·10^13 at n = 16.",
        "Assign workers in order 0, 1, 2 …. After k workers, all that matters is *which* k jobs are taken, not who took them.",
        "dp[mask] = cheapest assignment of the jobs in mask to workers 0 … popcount(mask) − 1. From mask, worker k = popcount(mask) takes any free job j: dp[mask | 1<<j] = min(…, dp[mask] + cost[k][j]).",
    ],
    opt=("O(2^n · n)", "O(2^n)", "One state per subset of jobs, n transitions each."),
    editorial=(
        "## The one thing this teaches\n**When the order of past choices does not matter, a set is "
        "the state — and a set of up to 20 things is an integer.** n! orderings collapse to 2^n subsets "
        "because the cost so far depends only on which jobs are gone.\n\n"
        "## Approach\n```java\nlong[] dp = new long[1 << n];\nArrays.fill(dp, Long.MAX_VALUE);\ndp[0] = 0;\n"
        "for (int mask = 0; mask < (1 << n); mask++) {\n    if (dp[mask] == Long.MAX_VALUE) continue;\n"
        "    int worker = Integer.bitCount(mask);          // the next worker to assign\n"
        "    if (worker == n) continue;\n    for (int j = 0; j < n; j++)\n"
        "        if ((mask >> j & 1) == 0)\n"
        "            dp[mask | 1 << j] = Math.min(dp[mask | 1 << j], dp[mask] + cost[worker][j]);\n}\n"
        "return dp[(1 << n) - 1];\n```\n\n"
        "## Why increasing masks is a valid order\nEvery transition adds a bit, so it goes to a larger "
        "integer. Looping masks upwards finishes every state before anything reads it.\n\n"
        "## Scale\n2^16 · 16 ≈ 10^6 steps. The Hungarian algorithm solves assignment in O(n³) for large "
        "n; bitmask DP is the version you can write in an interview."
    ),
    py='''
def solve(m):
    from itertools import permutations
    n = len(m)
    return min(sum(m[i][p[i]] for i in range(n)) for p in permutations(range(n)))
''',
    java='''
    static long solve(int[][] cost) {
        int n = cost.length;
        long[] dp = new long[1 << n];
        Arrays.fill(dp, Long.MAX_VALUE);
        dp[0] = 0;
        for (int mask = 0; mask < (1 << n); mask++) {
            if (dp[mask] == Long.MAX_VALUE) continue;
            int worker = Integer.bitCount(mask);
            if (worker == n) continue;
            for (int j = 0; j < n; j++)
                if ((mask >> j & 1) == 0)
                    dp[mask | 1 << j] = Math.min(dp[mask | 1 << j], dp[mask] + cost[worker][j]);
        }
        return dp[(1 << n) - 1];
    }
''',
    examples=[("Example 1", "3 3\n6 2 8\n3 7 4\n5 9 1\n"), ("Example 2", "1 1\n7\n")],
    hidden=[
        ("Diagonal is best", "4 4\n1 9 9 9\n9 1 9 9\n9 9 1 9\n9 9 9 1\n"),
        ("Greedy per worker fails", "3 3\n1 2 100\n1 100 100\n100 2 3\n"),
        ("All equal", "5 5\n7 7 7 7 7\n7 7 7 7 7\n7 7 7 7 7\n7 7 7 7 7\n7 7 7 7 7\n"),
        ("Eight workers", "8 8\n5 8 1 9 3 7 2 6\n4 2 7 1 8 3 9 5\n9 1 3 6 2 8 5 7\n2 7 5 3 9 1 6 8\n8 3 9 2 5 6 1 4\n6 5 2 8 1 9 7 3\n1 9 6 4 7 2 8 5\n3 6 8 5 4 7 2 1\n"),
    ],
    expl=[
        "Worker 0 → job 1 (2), worker 1 → job 0 (3), worker 2 → job 2 (1): total 6.",
        "One worker, one job.",
    ],
    prereqs=[
        ("dp", "A state that forgets the order of earlier choices."),
        ("bit_manip", "A subset of jobs as the bits of an integer."),
    ],
)

_p(
    "shortest-path-visit-all", "Visit Every Room", "Hard",
    topics=["Graphs", "Bit Manipulation"], subtopics=["BFS", "Bitmask State"], companies=["Google", "Amazon"],
    shape="graph", ret="long", todo="BFS over (room, visited mask), starting from every room at once; the answer is the first time any mask is full",
    description=(
        "A building's `n` rooms are connected by corridors (an undirected, connected graph). Walking one "
        "corridor takes one step. Starting in any room you like, print the fewest steps needed to "
        "have **visited every room** at least once. Rooms and corridors may be reused.\n\n"
        "### Input\nLine 1: `n m`.\nNext `m` lines: a corridor `u v`.\n\n"
        "### Output\nThe minimum number of steps."
    ),
    constraints="1 ≤ n ≤ 12\n0 ≤ m ≤ n(n − 1)/2\nThe graph is connected",
    hints=[
        "BFS over rooms alone fails: arriving at a room having seen {0, 1} is a different situation from arriving having seen {0, 2}.",
        "Make the state (room, set of rooms visited). With n ≤ 12 the set is a 12-bit mask: 12 · 4096 states.",
        "Seed the BFS with (r, 1 << r) for every room r at distance 0. Moving to v gives (v, mask | 1 << v). The first state whose mask is full ends the search.",
    ],
    opt=("O(2^n · n²)", "O(2^n · n)", "BFS over n · 2^n states, each with up to n neighbours."),
    editorial=(
        "## The one thing this teaches\n**When where you have been matters, put it in the BFS state.** "
        "Shortest paths need states whose futures do not depend on the past. The room alone is not "
        "such a state; the room plus the visited set is.\n\n"
        "## Approach\n```java\nint full = (1 << n) - 1;\nint[][] dist = new int[n][1 << n];\n"
        "for (int[] row : dist) Arrays.fill(row, -1);\nArrayDeque<int[]> q = new ArrayDeque<>();\n"
        "for (int r = 0; r < n; r++) { dist[r][1 << r] = 0; q.add(new int[]{r, 1 << r}); }   // any start\n"
        "while (!q.isEmpty()) {\n    int[] s = q.poll();\n    int u = s[0], mask = s[1];\n"
        "    if (mask == full) return dist[u][mask];\n    for (int v : adj[u]) {\n"
        "        int next = mask | 1 << v;\n        if (dist[v][next] == -1) {\n"
        "            dist[v][next] = dist[u][mask] + 1;\n            q.add(new int[]{v, next});\n        }\n    }\n}\n```\n\n"
        "## Multi-source start\nPutting every (room, just-that-room) state in the queue at distance 0 is "
        "the same trick as rotting oranges: one BFS answers \"starting from anywhere\".\n\n"
        "## The TSP view\nThis is a shortest Hamiltonian *walk*: all-pairs distances plus "
        "`dp[mask][end]` gives the same answer, in O(2^n · n²)."
    ),
    py='''
def solve(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    full = (1 << n) - 1
    dist = {}
    q = deque()
    for r in range(n):
        dist[(r, 1 << r)] = 0
        q.append((r, 1 << r))
    while q:
        u, mask = q.popleft()
        if mask == full:
            return dist[(u, mask)]
        for v in adj[u]:
            state = (v, mask | 1 << v)
            if state not in dist:
                dist[state] = dist[(u, mask)] + 1
                q.append(state)
    return 0
''',
    java='''
    static long solve(int n, int[][] edges) {
        final int INF = 1_000_000;
        int[][] d = new int[n][n];
        for (int[] row : d) Arrays.fill(row, INF);
        for (int i = 0; i < n; i++) d[i][i] = 0;
        for (int[] e : edges) { d[e[0]][e[1]] = 1; d[e[1]][e[0]] = 1; }
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    d[i][j] = Math.min(d[i][j], d[i][k] + d[k][j]);
        int[][] dp = new int[1 << n][n];
        for (int[] row : dp) Arrays.fill(row, INF);
        for (int v = 0; v < n; v++) dp[1 << v][v] = 0;
        for (int mask = 1; mask < (1 << n); mask++)
            for (int v = 0; v < n; v++) {
                if (dp[mask][v] == INF) continue;
                for (int w = 0; w < n; w++)
                    if ((mask >> w & 1) == 0)
                        dp[mask | 1 << w][w] = Math.min(dp[mask | 1 << w][w], dp[mask][v] + d[v][w]);
            }
        int best = INF;
        for (int v = 0; v < n; v++) best = Math.min(best, dp[(1 << n) - 1][v]);
        return best;
    }
''',
    examples=[("Example 1", "5 4\n0 1\n0 2\n0 3\n0 4\n"), ("Example 2", "4 3\n0 1\n1 2\n2 3\n")],
    hidden=[
        ("One room", "1 0\n"),
        ("Two rooms", "2 1\n0 1\n"),
        ("A cycle", "5 5\n0 1\n1 2\n2 3\n3 4\n4 0\n"),
        ("Two branches off a corridor", "6 5\n0 1\n1 2\n2 3\n1 4\n2 5\n"),
        ("Complete graph", "5 10\n0 1\n0 2\n0 3\n0 4\n1 2\n1 3\n1 4\n2 3\n2 4\n3 4\n"),
    ],
    expl=[
        "A star: start at a leaf, e.g. 1 → 0 → 2 → 0 → 3 → 0 → 4 is 6 steps. Every move between leaves passes through the hub.",
        "A path: walk it end to end in 3 steps.",
    ],
    prereqs=[
        ("bfs", "Shortest paths in an unweighted state graph."),
        ("bit_manip", "A visited set packed into a mask."),
    ],
)
