# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 8 — Beyond the core (optional).
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Everything in stages 1-7 is interview core. This stage is not: string hashing
# and the Z-function, Fenwick and segment trees, Tarjan's low-links and Euler
# paths, bitmask DP. They come up — at some companies, in some rounds, and
# constantly in contests — but far less often, and a learner should not be told
# the course is unfinished because they skipped them.
#
# So the stage is OPTIONAL: `_stage(..., optional=True)`. The app leaves it out of
# the course's overall progress and never sends "Continue" here until the core
# is done. Its units are otherwise ordinary — the same teaching beats, the same
# lints, verified references for every problem.
#
# Each unit gathers problems the syllabus audit found stranded: placed in a core
# unit (`critical-connections` in graph traversal, `partition-k-equal-subsets` in
# backtracking) whose technique that unit never teaches.
# ---------------------------------------------------------------------------

_S8 = _stage(
    "beyond", "Beyond the Core", "🚀",
    "Optional: the techniques that come up less often, taught properly.",
    """
**This stage is optional.** Finishing stages 1–7 is finishing the interview
core; nothing here is needed for it, and the course's progress does not count it.

What is here are ten techniques that turn up in harder rounds and in contests,
each solving something the core toolkit cannot do efficiently:

| Unit | What it adds |
| --- | --- |
| **String matching** | every occurrence in linear time; substrings compared by hash; suffix and LCP arrays |
| **Range queries** | prefix sums that survive updates; range *updates* by lazy propagation; O(1) static minimums |
| **Advanced graphs** | cut vertices, strongly connected components, Euler paths |
| **Bitmask DP** | a subset of up to ~20 things as the state |
| **Tree queries** | a fixed tree, preprocessed: Euler tour, binary lifting, LCA |
| **Advanced bits** | an order where one bit changes; a basis for everything a set can XOR to |
| **Advanced DP** | a state made of digits; a transition made cheaper; an exponent halved |
| **Flows & matching** | pairing things up, and the max-flow min-cut duality |
| **Geometry** | one integer expression, and orientation, area, intersection and hulls from it |
| **Randomized** | expected versus worst case, Las Vegas versus Monte Carlo, and sampling |

Each opens with an easier problem and builds to a hard one, like every other unit.

The first four came from the syllabus audit — techniques whose problems were
already in the bank, stranded in units that never taught them. The last six came
from the 107-topic audit in `DSA_ROADMAP.md`, and their problems were authored
for them.
""",
    optional=True,
)


# --- Unit 37 — String matching -----------------------------------------------

_unit(
    "string-matching", "String Matching & Hashing", "🧵", _S8,
    "Every occurrence in linear time — and substrings compared in O(1).",
    weight=1,
    prereqs=["strings", "hashing", "binary-search"],
    why="""
The strings unit taught the KMP prefix function for finding one pattern. This
unit covers the three tools that answer the harder questions: *all* occurrences,
*periods and repeats* inside one string, and *are these two substrings equal?* in
O(1) — the question that lets binary search find the longest repeated substring.

None of them is needed often. When one is needed, the naive alternative is
quadratic on exactly the inputs the problem is built around.
""",
    model="""
### Borders and periods

A **border** is a proper prefix that is also a suffix. The prefix function
`pi[i]` is the longest border of `s[0..i]`. If the whole string has a border of
length b, shifting it by `n − b` lines it up with itself, so:

> the smallest period of s is `n − pi[n − 1]`.

`s` is an exact repetition of a smaller block when that period divides n.

### The Z-function

`z[i]` = the length of the longest substring starting at i that matches a
**prefix** of the string. Computed in O(n) by reusing the rightmost match found
so far, `[l, r)`:

```java
for (int i = 1, l = 0, r = 0; i < n; i++) {
    if (i < r) z[i] = Math.min(r - i, z[i - l]);      // inside a known match
    while (i + z[i] < n && c[z[i]] == c[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
}
```

To find every occurrence of pattern `t` in text `s`, compute z for
`t + "$" + s`: each position in the text part with `z = |t|` is a match. The
separator stops a match running past the pattern.

### Rolling hash (Rabin–Karp)

Treat a window as a number in base B modulo a large prime P. Sliding the window
drops the outgoing character and adds the incoming one in O(1):

```java
h = (h - c[i] * pow % P + P) % P;       // remove s[i], worth B^(L-1)
h = (h * B + c[i + L]) % P;             // shift, add s[i + L]
```

Equal strings always have equal hashes. Unequal strings *usually* do not — so a
hash match is a candidate, confirmed by comparing the characters when an exact
answer matters.

When the alphabet is tiny the hash can be **exact**: four DNA letters take 2 bits
each, so a 10-letter window is a 20-bit integer with no collisions at all.

### Binary search on a length

"Longest substring that occurs twice" is monotone: a repeat of length L contains
a repeat of length L − 1. Binary-search L; test each L with one rolling-hash pass.
O(n log n) expected.

### Suffix arrays

All of the above answer questions about *one* pattern, or about one length. The
**suffix array** answers questions about every substring at once: it is the n
suffixes of `s`, sorted, stored as their starting positions.

It is built by **doubling**. Sort the suffixes by their first character and give
each a rank. Now the first *two* characters of suffix i are the pair
`(rank[i], rank[i+1])` — so sorting by that pair ranks every suffix by its first
two characters, in one sort of integers, with no string comparison at all. Repeat
and the compared length doubles: 1, 2, 4, 8 … `⌈log₂ n⌉` rounds in total.

```java
for (int k = 1; k < n; k <<= 1) {
    // key(i) = (rank[i], i + k < n ? rank[i + k] : -1)
    sort sa by key;                 // O(n log n), or O(n) with a radix sort
    rank = ranksFrom(sa, key);      // equal keys MUST get equal ranks
}
```

The `-1` for a suffix that runs off the end is what makes a shorter suffix sort
before a longer one that extends it: `an` before `ana`.

### The LCP array, and Kasai

`lcp[i]` is the length of the longest common prefix of `sa[i-1]` and `sa[i]` —
adjacent suffixes in sorted order. Kasai computes all of them in **one linear
pass**, by walking the suffixes in order of *starting position* rather than rank:

```java
int h = 0;
for (int i = 0; i < n; i++) {
    if (pos[i] == 0) { h = 0; continue; }
    int j = sa[pos[i] - 1];
    while (i + h < n && j + h < n && s.charAt(i + h) == s.charAt(j + h)) h++;
    lcp[pos[i]] = h;
    if (h > 0) h--;                 // dropping a character costs at most one
}
```

That last line is the whole argument: `h` falls by at most 1 per step and rises
at most n times in total, so the inner loop is O(1) amortized.

### What the LCP array is for

| Question | Answer |
| --- | --- |
| Longest repeated substring | `max(lcp)` |
| Number of distinct substrings | `n(n+1)/2 − Σ lcp[i]` |
| Longest substring common to k strings | sliding window over the LCP of their concatenation |
| Does pattern t occur in s? | two binary searches over the suffix array, O(|t| log n) |

The distinct-substring count is the cleanest of these: every substring is a
prefix of some suffix, there are n(n+1)/2 of those, and the ones counted twice
are exactly the shared prefixes of *adjacent* sorted suffixes.
""",
    signals=[
        _sig("“count all occurrences”, overlapping allowed", "Z-function on pattern + $ + text",
             "Or KMP, counting every time the match length reaches |t|."),
        _sig("“is the string a repetition of a block?”, “shortest period”", "n − pi[n − 1]",
             "A border of length b means period n − b."),
        _sig("“substrings of length L that repeat”", "Rolling hash over windows",
             "O(1) per step instead of O(L) to rebuild each window."),
        _sig("“longest substring occurring twice”", "Binary search L + rolling hash",
             "Existence of a repeat is monotone in L."),
        _sig("A small alphabet and a short fixed window", "An exact bit-packed code",
             "No collisions to worry about."),
        _sig("Comparing many substring pairs for equality", "Prefix hashes",
             "`hash(l, r)` in O(1) after an O(n) precomputation."),
        _sig("“how many distinct substrings”, “longest repeated substring”, exactly",
             "Suffix array + LCP array",
             "One structure answers the whole family, with no collision caveat."),
        _sig("Many patterns against one fixed text", "Suffix array, binary searched",
             "O(|t| log n) per pattern after an O(n log n) build."),
    ],
    skeletons=[
        _sk("Z-function",
            "All occurrences; how much matches a prefix at each position.",
            """
static int[] zFunction(char[] c) {
    int n = c.length;
    int[] z = new int[n];
    for (int i = 1, l = 0, r = 0; i < n; i++) {
        if (i < r) z[i] = Math.min(r - i, z[i - l]);
        while (i + z[i] < n && c[z[i]] == c[i + z[i]]) z[i]++;
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
    return z;
}
""",
            "For matching, run it on `(pattern + \"$\" + text).toCharArray()`."),
        _sk("Prefix function and period",
            "Borders, periods, repetition tests.",
            """
int[] pi = new int[n];
for (int i = 1, k = 0; i < n; i++) {
    while (k > 0 && s.charAt(i) != s.charAt(k)) k = pi[k - 1];
    if (s.charAt(i) == s.charAt(k)) k++;
    pi[i] = k;
}
int period = n - pi[n - 1];
boolean exactRepeat = period < n && n % period == 0;
""",
            "The same loop as KMP's, run on the string against itself."),
        _sk("Rolling hash over windows",
            "Fixed-length windows compared or counted by hash.",
            """
final long P = 1_000_000_007L, B = 131;
long h = 0, pow = 1;
for (int i = 0; i < L; i++) h = (h * B + s.charAt(i)) % P;
for (int i = 1; i < L; i++) pow = pow * B % P;            // B^(L-1)
for (int i = 0; ; i++) {
    // h is the hash of s[i, i + L)
    if (i + L == s.length()) break;
    h = (h - s.charAt(i) * pow % P + P) % P;
    h = (h * B + s.charAt(i + L)) % P;
}
""",
            "Verify matching windows by comparing characters when the answer must be exact."),
        _sk("Suffix array by doubling",
            "Every substring question at once, exactly.",
            """
Integer[] sa = indicesSortedBy(i -> s.charAt(i));
int[] rank = ranksFrom(sa);                       // equal characters -> equal ranks

for (int k = 1; k < n; k <<= 1) {
    final int kk = k;
    Arrays.sort(sa, (x, y) -> {
        if (rank[x] != rank[y]) return Integer.compare(rank[x], rank[y]);
        int rx = x + kk < n ? rank[x + kk] : -1;   // -1: a shorter suffix sorts first
        int ry = y + kk < n ? rank[y + kk] : -1;
        return Integer.compare(rx, ry);
    });
    rank = ranksFrom(sa, kk);
    if (rank[sa[n - 1]] == n - 1) break;           // all distinct, nothing left to separate
}
""",
            "`ranksFrom` must give equal ranks to equal keys, or the next round's pairs are wrong."),
        _sk("LCP array (Kasai)",
            "Distinct substrings, longest repeat, longest common substring.",
            """
int[] pos = new int[n];                            // inverse of sa
for (int i = 0; i < n; i++) pos[sa[i]] = i;

int h = 0;
for (int i = 0; i < n; i++) {
    if (pos[i] == 0) { h = 0; continue; }
    int j = sa[pos[i] - 1];
    while (i + h < n && j + h < n && s.charAt(i + h) == s.charAt(j + h)) h++;
    lcp[pos[i]] = h;
    if (h > 0) h--;
}
""",
            "Linear because `h` drops by at most one per step. Remove the `h--` and it is quadratic."),
    ],
    traces=[
        _trace(
            "Prefix function of \"aabaaab\"",
            "`k` is the length of the border being extended. On a mismatch it falls back to "
            "`pi[k − 1]` — the next shorter border — instead of restarting at 0.",
            ["i", "s[i]", "k before", "Fallbacks", "pi[i]"],
            [
                ["0", "a", "—", "—", "0"],
                ["1", "a", "0", "none; a = s[0]", "**1**"],
                ["2", "b", "1", "b ≠ s[1] → k = pi[0] = 0; b ≠ s[0]", "0"],
                ["3", "a", "0", "none; a = s[0]", "1"],
                ["4", "a", "1", "none; a = s[1]", "2"],
                ["5", "a", "2", "a ≠ s[2] = b → k = pi[1] = 1; a = s[1]", "**2**"],
                ["6", "b", "2", "none; b = s[2]", "**3**"],
            ],
            "At i = 5 the border `aa` could not grow into `aab`, so it fell back to the border "
            "of `aa` — `a` — and grew that instead: no character before i was re-read. The "
            "final value 3 is the border `aab`, so the period is 7 − 3 = 4: `aaba` repeated "
            "and cut off.",
        ),
    ],
    costs=[
        _cost("Z-function / prefix function", "O(n)", "O(n)", "Every comparison either extends r / k or ends a step."),
        _cost("All occurrences via Z", "O(n + m)", "O(n + m)", "One array over pattern + separator + text."),
        _cost("Rolling hash over all windows", "O(n)", "O(1)", "Plus verification when hashes match."),
        _cost("Longest repeated substring", "O(n log n) expected", "O(n)", "Binary search over L, one hash pass each."),
        _cost("Naive matching", "O(n · m)", "O(1)", "What all of these replace."),
        _cost("Suffix array (doubling)", "O(n log² n)", "O(n)", "O(n log n) with a radix sort."),
        _cost("LCP array (Kasai)", "O(n)", "O(n)", "Given the suffix array."),
        _cost("Distinct substrings", "O(n log² n)", "O(n)", "n(n+1)/2 − Σ lcp; never builds a substring."),
        _cost("Pattern search in a suffix array", "O(|t| log n)", "O(1)", "Two binary searches for the range of matches."),
    ],
    pitfalls=[
        _pit("A match is reported that runs past the pattern",
             "Pattern and text were concatenated without a separator for the Z-function.",
             "Join them with a character that occurs in neither, like `$`."),
        _pit("A rolling hash goes negative",
             "`h - c * pow` was reduced with `%`, which keeps the sign in Java.",
             "Add P before the final `% P`."),
        _pit("Occasional wrong answers on large inputs",
             "Two different windows collided on the same hash and were trusted.",
             "Verify candidates by comparing characters, or use two independent moduli."),
        _pit("The period test says `abab a` repeats",
             "The period was computed but its divisibility of n was not checked.",
             "An exact repetition needs `period < n && n % period == 0`."),
        _pit("Binary search on the length finds nothing",
             "The search range started at 0 and the check for length 0 always succeeds, or ended at n.",
             "Search L in [1, n − 1]: a repeat is at most n − 1 long."),
        _pit("A suffix array is subtly out of order on strings like `aab`",
             "The doubling round gave each position a fresh rank instead of giving equal keys "
             "equal ranks — or the off-the-end sentinel was 0 rather than −1.",
             "Ranks come from comparing consecutive keys, and the sentinel must be below every "
             "real rank so `an` sorts before `ana`."),
        _pit("Kasai's LCP pass is quadratic",
             "The `if (h > 0) h--;` at the end of the loop is missing, so `h` restarts at 0 "
             "for every suffix.",
             "That one line is the amortized argument. Without it the inner `while` re-reads "
             "the same characters n times."),
        _pit("The distinct-substring count overflows",
             "n(n+1)/2 at n = 10⁵ is 5·10⁹, past `int`.",
             "Accumulate in a `long`, and cast before the multiplication, not after."),
    ],
    lessons=["string_basics", "hashing", "binary_search"],
    checks=[
        _chk("How does the prefix function give a string's smallest period?",
             "pi[n − 1] is the longest border. Shifting the string by n − pi[n − 1] aligns it "
             "with itself, and no smaller shift can, so that is the smallest period."),
        _chk("Why does the Z-function need a separator between pattern and text?",
             "Without it, a match starting in the text could extend beyond |t| characters, "
             "blurring \"matches the whole pattern\" with \"matches a longer prefix\"."),
        _chk("What makes a rolling hash O(1) per step?",
             "The next window's value is the old one minus the outgoing character's weight "
             "B^(L−1), times B, plus the incoming character — no loop over the window."),
        _chk("Why is \"a repeated substring of length L exists\" monotone in L?",
             "Dropping the last character of a repeated substring leaves a repeated substring "
             "one shorter. So the answer is the boundary a binary search can find."),
        _chk("Why does the doubling construction never compare two suffixes character by "
             "character after the first round?",
             "Because after a round ranking by the first k characters, the first 2k characters "
             "of suffix i are the *pair* (rank[i], rank[i+k]) — two integers. Comparing "
             "integers replaces comparing strings, which is what removes the factor of n."),
        _chk("Why is the number of distinct substrings n(n+1)/2 − Σ lcp?",
             "Every substring is a prefix of some suffix, and the suffixes have n(n+1)/2 "
             "prefixes in total. Sorting puts identical prefixes next to each other, so the "
             "duplicates are exactly the lcp[i] prefixes each suffix shares with the one before "
             "it in sorted order."),
        _chk("Kasai's inner `while` can run n times. Why is the whole pass O(n)?",
             "`h` increases by one per successful comparison and decreases by at most one per "
             "outer step, so there are at most n decreases and therefore at most 2n increases "
             "in total — the amortized argument, with `h` as the potential."),
    ],
    bigo=[
        _bigo(r"""
for (int i = 1, l = 0, r = 0; i < n; i++) {     // Z-function, string length n
    if (i < r) z[i] = Math.min(r - i, z[i - l]);
    while (i + z[i] < n && c[z[i]] == c[i + z[i]]) z[i]++;
    if (i + z[i] > r) { l = i; r = i + z[i]; }
}
""", "O(n)", ["O(n)", "O(n²)", "O(n log n)", "O(n√n)"],
            "Every successful comparison in the `while` pushes r right, and r never moves "
            "left — at most n of those in total, plus one failed comparison per i."),
        _bigo(r"""
Set<String> seen = new HashSet<>();             // text length n, window length L
for (int i = 0; i + L <= n; i++)
    seen.add(s.substring(i, i + L));
""", "O(n·L)", ["O(n·L)", "O(n)", "O(n log n)", "O(L²)"],
            "Each `substring` copies L characters and hashing reads them all again. A rolling "
            "hash computes the same keys in O(1) each."),
        _bigo(r"""
int lo = 1, hi = n - 1;                          // longest repeated substring
while (lo <= hi) {
    int mid = (lo + hi) >>> 1;
    if (hasRepeat(s, mid)) lo = mid + 1;         // rolling hash, O(n) expected
    else hi = mid - 1;
}
""", "O(n log n)", ["O(n log n)", "O(n²)", "O(n² log n)", "O(n)"],
            "log n candidate lengths, each checked by one linear pass. Checking every length "
            "in order would be O(n²)."),
        _bigo(r"""
int count = 0;                                   // text n, pattern m
for (int i = 0; i + m <= n; i++)
    if (s.regionMatches(i, t, 0, m)) count++;
""", "O(n·m)", ["O(n·m)", "O(n + m)", "O(n)", "O(m log n)"],
            "Up to m comparisons at each of n − m + 1 starts — `aaaa…a` against `aa…ab` hits "
            "the bound. The Z-function answers the same question in O(n + m)."),
        _bigo(r"""
int h = 0;                                       // Kasai, given the suffix array
for (int i = 0; i < n; i++) {
    if (pos[i] == 0) { h = 0; continue; }
    int j = sa[pos[i] - 1];
    while (i + h < n && j + h < n && c[i + h] == c[j + h]) h++;
    lcp[pos[i]] = h;
    if (h > 0) h--;
}
""", "O(n)", ["O(n)", "O(n log n)", "O(n²)", "O(n√n)"],
            "The inner `while` looks like it can run n times, and on one step it can. But `h` "
            "only ever falls by one per outer step, so there are at most n decreases and "
            "therefore at most 2n increases over the whole loop. Delete the `if (h > 0) h--;` "
            "and the same code really is O(n²)."),
        _bigo(r"""
for (int k = 1; k < n; k <<= 1) {                // suffix array by doubling
    Arrays.sort(sa, byRankPair(k));              // comparison sort of n integers pairs
    rank = ranksFrom(sa, k);
}
""", "O(n log² n)", ["O(n log n)", "O(n log² n)", "O(n²)", "O(n² log n)"],
            "log n doubling rounds, each an O(n log n) sort — the two logs come from different "
            "places and multiply. Replacing the comparison sort with a two-pass radix sort "
            "makes each round O(n) and the whole build O(n log n)."),
    ],
    interview="""
These come up as follow-ups: "your solution compares substrings — can you make
that O(1)?" The answer is a rolling hash, with the collision caveat stated
unprompted. For "does this string repeat a block?", the prefix-function period
is a two-line answer that sounds like it took a week to learn.
""",
    rungs=[
        _rung("Warm up", "Every occurrence, overlapping, in linear time.",
              ["count-pattern-occurrences"],
              {"count-pattern-occurrences": "Z-function on pattern + $ + text. Then do it with KMP and compare: the same linear bound from two directions."}),
        _rung("Core", "A string compared with itself, and windows compared by hash.",
              ["string-period", "repeated-dna-sequences"],
              {"string-period": "One prefix-function pass; the answer is n − pi[n − 1]. Check it against brute force on `abaabaabb`.",
               "repeated-dna-sequences": "Two bits per letter make the window code exact. Shift, mask, count."}),
        _rung("Suffix arrays", "Sort every suffix once, and stop answering one question at a time.",
              ["suffix-array-order"],
              {"suffix-array-order": "Build it by doubling. Write out the ranks for `banana` after k = 1, 2 and 4 by hand before you code it — the sentinel −1 is the part that will bite."}),
        _rung("Stretch", "The two hardest substring questions, from the two directions.",
              ["longest-duplicate-substring", "distinct-substrings-large"],
              {"longest-duplicate-substring": "Search L in [1, n − 1]. Group windows by hash, verify characters, keep the smallest match at the final length.",
               "distinct-substrings-large": "The trie version of this is in `tries`; it is O(n²) and dies at n = 10⁵. Here it is n(n+1)/2 minus the LCP sum — solve it both ways and compare the two shapes."}),
    ],
    next_up="""
Strings compared by precomputation. The next unit precomputes over arrays — and
keeps the precomputation valid while the array changes.
""",
)


# --- Unit 38 — Range queries -------------------------------------------------

_unit(
    "range-queries", "Range Queries: Fenwick & Segment Trees", "📏", _S8,
    "Prefix sums that survive updates, and ranges combined in O(log n).",
    weight=2,
    prereqs=["prefix-sums", "bit-manipulation", "trees"],
    why="""
Prefix sums answer any range sum in O(1) — until the array changes, and the whole
prefix array must be rebuilt. The raw array is the opposite: O(1) to change,
O(n) to sum. When updates and queries are interleaved, both are O(n) per
operation and 10⁵ of each is 10¹⁰.

Two structures meet in the middle at O(log n) for both. A **Fenwick tree** is
twelve lines and handles sums (anything with an inverse). A **segment tree** is a
little longer and handles minimum, maximum, gcd — anything associative — and,
with more work, updates to whole ranges.
""",
    model="""
### Fenwick tree (binary indexed tree)

Store at 1-based index i the sum of a block of length `i & -i` (the lowest set
bit of i) ending at i. Then:

- a **prefix sum** walks down: `i -= i & -i` — each step drops a bit, so O(log n);
- a **point update** walks up: `i += i & -i` — each step visits the next block
  that covers i, so O(log n).

```java
void add(int i, long delta) { for (i++; i <= n; i += i & -i) tree[i] += delta; }
long prefix(int i)          { long s = 0; for (i++; i > 0; i -= i & -i) s += tree[i]; return s; }
long sum(int l, int r)      { return prefix(r) - (l > 0 ? prefix(l - 1) : 0); }
```

A range sum is two prefix sums subtracted — which is why a Fenwick tree needs an
operation with an inverse. "Set a[i] = v" is `add(i, v − a[i])`, so keep the
plain array too.

### Segment tree

A complete binary tree over the array, each node storing the combined value of
its range. Iteratively, leaves live at `size + i`, a parent at `p / 2`:

```java
void set(int i, long v) { for (t[i += size] = v; i > 1; i >>= 1) t[i >> 1] = Math.min(t[i], t[i ^ 1]); }
long min(int l, int r) {                          // inclusive
    long res = Long.MAX_VALUE;
    for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
        if ((l & 1) == 1) res = Math.min(res, t[l++]);
        if ((r & 1) == 1) res = Math.min(res, t[--r]);
    }
    return res;
}
```

Any range is covered by O(log n) stored nodes, so any associative combine works
— no inverse needed.

### Range updates

"Add v to a[l..r]" is two point updates on a **difference array**. Summing a
range of the original array then needs a weighted prefix sum, which splits into
two ordinary ones — two Fenwick trees:

`prefix(i) = (i + 1) · Σ d[j] − Σ d[j] · j`

### Lazy propagation

The difference-array trick works because addition is *linear in the update*: the
effect of "add v to [l, r]" on a prefix is a linear function of v. **Assignment
is not** — "set [l, r] to v" destroys whatever was there, and how much it
destroys depends on the current contents. So no pair of Fenwick trees can do it.

A segment tree can, by being lazy: when a node's range lies entirely inside the
update range, **apply the update to that node and stop**, leaving a note that its
children still owe the change.

```java
void apply(int node, int lo, int hi, long v) {   // assign v to this whole range
    sum[node]     = v * (hi - lo + 1);
    lazyVal[node] = v;
    lazy[node]    = true;                        // a boolean, NOT a sentinel value
}

void push(int node, int lo, int hi) {            // pay the children before descending
    if (!lazy[node]) return;
    int mid = (lo + hi) >>> 1;
    apply(2 * node,     lo,      mid, lazyVal[node]);
    apply(2 * node + 1, mid + 1, hi,  lazyVal[node]);
    lazy[node] = false;
}
```

`push` goes at the top of **both** `update` and `query`, before either descends.
Only the O(log n) nodes on the path are ever pushed, which is why a range update
costs the same as a point update.

The boolean matters: `v` may legitimately be 0, so a sentinel cannot tell
"assign 0" from "nothing pending".

Two pending *assignments* do not combine — the later one wins, so `apply`
overwrites. Two pending *additions* must be summed, and a tree carrying both
needs a defined order (an assignment cancels every addition beneath it). That
composition rule is where lazy trees actually go wrong.

### Sparse table: O(1), when nothing changes

For a static array and an **idempotent** combine — `min`, `max`, `gcd`, where
`f(x, x) = x` — you can do better than a segment tree's O(log n).

Precompute `table[j][i]`, the combine of the block of length 2^j starting at i,
each level from the one below. Then cover `[l, r]` with **two overlapping**
blocks of the largest power that fits:

```java
int j = 31 - Integer.numberOfLeadingZeros(r - l + 1);      // floor(log2(len))
return Math.min(table[j][l], table[j][r - (1 << j) + 1]);
```

The overlap is free precisely because the operation is idempotent — which is
also why there is no O(1) sparse table for *sums*: counting the middle twice
would be wrong.

This is binary lifting's jump table with `min` in place of "follow the pointer".
Same build, same query, same reason it works.

### Counting with ranks

"How many elements to the right are smaller?" — scan right to left, and keep a
Fenwick tree of counts indexed by **value rank** (sort the distinct values, use
positions). Each element queries the ranks below its own, then adds itself.
""",
    signals=[
        _sig("Range sums, with point updates in between", "Fenwick tree",
             "O(log n) for both; twelve lines."),
        _sig("Range min / max / gcd, with updates", "Segment tree",
             "No inverse, so prefix subtraction does not work."),
        _sig("“add v to every element in [l, r]”, then range sums", "Two Fenwick trees on a difference array",
             "Or a lazy segment tree."),
        _sig("“how many smaller elements after / before i”", "Fenwick tree over value ranks",
             "Scan in the right direction; compress the values first."),
        _sig("No updates at all, and the question is a sum", "Prefix sums",
             "O(n) to build, O(1) to answer. Do not build a tree you do not need."),
        _sig("No updates at all, and the question is a min / max / gcd", "Sparse table",
             "O(1) per query, because the combine is idempotent so blocks may overlap."),
        _sig("“set every element of [l, r] to v”, then range sums", "Lazy segment tree",
             "Assignment is not linear in the update, so the two-Fenwick trick cannot express it."),
        _sig("Counting inversions with updates, or online", "Fenwick tree of counts",
             "Merge sort only works offline."),
    ],
    skeletons=[
        _sk("Fenwick tree",
            "Point update, range sum.",
            """
long[] tree = new long[n + 1];                   // 1-based inside

void add(int i, long delta) {                    // a[i] += delta, i 0-based
    for (i++; i <= n; i += i & -i) tree[i] += delta;
}

long prefix(int i) {                             // a[0] + … + a[i]
    long s = 0;
    for (i++; i > 0; i -= i & -i) s += tree[i];
    return s;
}
""",
            "Build in O(n log n) with n calls to `add`, one per element."),
        _sk("Iterative segment tree (min)",
            "Point update, range min/max/gcd.",
            """
long[] t = new long[2 * size];                   // leaves at size + i
for (int i = 0; i < size; i++) t[size + i] = a[i];
for (int p = size - 1; p > 0; p--) t[p] = Math.min(t[2 * p], t[2 * p + 1]);

void set(int i, long v) {
    for (t[i += size] = v; i > 1; i >>= 1) t[i >> 1] = Math.min(t[i], t[i ^ 1]);
}

long query(int l, int r) {                       // inclusive
    long res = Long.MAX_VALUE;
    for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
        if ((l & 1) == 1) res = Math.min(res, t[l++]);
        if ((r & 1) == 1) res = Math.min(res, t[--r]);
    }
    return res;
}
""",
            "Swap `Math.min` and the identity (`MAX_VALUE`) for any associative operation."),
        _sk("Range add, range sum (two Fenwicks)",
            "Updates to whole ranges.",
            """
void rangeAdd(int l, int r, long v) {            // a[l..r] += v
    add(b1, l, v);        add(b1, r + 1, -v);
    add(b2, l, v * l);    add(b2, r + 1, -v * (r + 1));
}

long prefix(int i) {                             // a[0] + … + a[i]
    return query(b1, i) * (i + 1) - query(b2, i);
}
""",
            "Guard `r + 1 < n` if the trees are sized exactly n."),
        _sk("Lazy segment tree (range assign, range sum)",
            "A range UPDATE, where the update is not linear in its argument.",
            """
void update(int node, int lo, int hi, int l, int r, long v) {
    if (r < lo || hi < l) return;                      // disjoint
    if (l <= lo && hi <= r) { apply(node, lo, hi, v); return; }   // fully inside: stop here
    push(node, lo, hi);                                // pay the children first
    int mid = (lo + hi) >>> 1;
    update(2 * node,     lo,      mid, l, r, v);
    update(2 * node + 1, mid + 1, hi,  l, r, v);
    sum[node] = sum[2 * node] + sum[2 * node + 1];     // and pull back up
}

long query(int node, int lo, int hi, int l, int r) {
    if (r < lo || hi < l) return 0;
    if (l <= lo && hi <= r) return sum[node];
    push(node, lo, hi);                                // the line people forget
    int mid = (lo + hi) >>> 1;
    return query(2 * node, lo, mid, l, r) + query(2 * node + 1, mid + 1, hi, l, r);
}
""",
            "`push` in `query` too. Leaving it out is correct until the first range update and "
            "silently wrong afterwards."),
        _sk("Sparse table (static range min)",
            "No updates, and an idempotent combine.",
            """
int[][] table = new int[LOG][n];
table[0] = a.clone();
for (int j = 1; j < LOG; j++)
    for (int i = 0; i + (1 << j) <= n; i++)
        table[j][i] = Math.min(table[j - 1][i], table[j - 1][i + (1 << (j - 1))]);

int query(int l, int r) {                              // inclusive
    int j = logs[r - l + 1];                           // floor(log2(len)), precomputed
    return Math.min(table[j][l], table[j][r - (1 << j) + 1]);
}
""",
            "Precompute `logs[i] = logs[i >> 1] + 1`; `Math.log` per query is slower and rounds "
            "wrongly at exact powers of two."),
    ],
    traces=[
        _trace(
            "A Fenwick tree over [3, 1, 4, 1, 5]",
            "1-based `tree[i]` covers `i & -i` elements ending at i: tree[1] = a[0], "
            "tree[2] = a[0..1], tree[3] = a[2], tree[4] = a[0..3], tree[5] = a[4]. Every walk "
            "below jumps by the lowest set bit.",
            ["Operation", "1-based indices visited", "Values touched", "Result"],
            [
                ["build", "—", "tree = [3, 4, 4, 9, 5]", "—"],
                ["prefix(4) = a[0..4]", "5 → 4 → 0", "tree[5] + tree[4] = 5 + 9", "**14**"],
                ["add(2, +6)  (a[2]: 4 → 10)", "3 → 4 → 8 (past n, stop)", "tree[3] = 10, tree[4] = 15", "—"],
                ["prefix(3) = a[0..3]", "4 → 0", "tree[4] = 15", "15"],
                ["prefix(0) = a[0]", "1 → 0", "tree[1] = 3", "3"],
                ["sum(1, 3) = prefix(3) − prefix(0)", "—", "15 − 3", "**12**"],
            ],
            "The update touched two cells and the queries at most two — for n = 10⁵ those "
            "walks are at most 17 steps. `sum(1, 3)` = 1 + 10 + 1 = 12 without ever reading "
            "a[1] or a[3] individually.",
        ),
    ],
    costs=[
        _cost("Fenwick update / prefix sum", "O(log n)", "O(n)", "Build by n updates: O(n log n)."),
        _cost("Segment tree update / query", "O(log n)", "O(n)", "2n array cells, iteratively."),
        _cost("Two-Fenwick range add + range sum", "O(log n) each", "O(n)", "Four point updates per range add."),
        _cost("Count smaller after self", "O(n log n)", "O(n)", "Sort for ranks, then n Fenwick operations."),
        _cost("Prefix-sum array with updates", "O(n) per update", "O(n)", "What the trees replace."),
        _cost("Lazy segment tree range update / query", "O(log n)", "O(n)", "Only the O(log n) nodes on the path are pushed."),
        _cost("Sparse table build", "O(n log n)", "O(n log n)", "log n levels of n blocks."),
        _cost("Sparse table query", "O(1)", "—", "Two lookups and one combine — needs idempotence."),
        _cost("Static prefix sums", "O(1) query, O(n) build", "O(n)", "The baseline; unbeatable when nothing changes."),
    ],
    pitfalls=[
        _pit("A Fenwick tree loops forever or skips elements",
             "It was indexed from 0, and `0 & -0` is 0.",
             "Shift to 1-based inside `add` and `prefix` (`i++`)."),
        _pit("A `set` operation doubles the value",
             "`add(i, v)` was called instead of adding the difference.",
             "`add(i, v − a[i])`, keeping a plain copy of the array."),
        _pit("Range minimum from a Fenwick tree is wrong",
             "`prefix(r) − prefix(l − 1)` has no meaning for min.",
             "Use a segment tree: minimum has no inverse."),
        _pit("Count-smaller counts equal values",
             "The query included the element's own rank.",
             "Query ranks strictly below: `prefix(rank − 1)`."),
        _pit("Range sums overflow",
             "Sums of 10⁵ values up to 10⁹ were kept in `int`.",
             "Store the trees as `long[]`."),
        _pit("A lazy tree is right until the first range update, then wrong",
             "`push` is called in `update` but not in `query`, so a query descends through a "
             "node with a pending change and reads stale children.",
             "`push` at the top of every recursive call that descends — both of them."),
        _pit("“Assign 0” behaves as “no update pending”",
             "The pending value doubles as the flag, with 0 or −1 meaning “nothing”.",
             "Keep a separate `boolean[] lazy`. The value and the fact that there is a value "
             "are two different pieces of state."),
        _pit("A lazy tree mixing range-add and range-assign gives nonsense",
             "The two pending kinds were composed in the wrong order — an assignment arriving "
             "on top of a pending addition must cancel it, not add to it.",
             "Define composition explicitly: assign clears any pending add; add accumulates "
             "onto a pending assign's value."),
        _pit("A sparse table gives wrong sums",
             "It was built for `+`, so the overlap between the two blocks is counted twice.",
             "Sparse tables need an idempotent combine (min, max, gcd). For sums, use prefix "
             "sums if static or a Fenwick tree if not."),
    ],
    lessons=["prefix_sum", "bit_manip", "tree_basics"],
    checks=[
        _chk("What does `tree[i]` store in a Fenwick tree?",
             "The sum of the `i & -i` elements ending at index i (1-based) — a block whose "
             "length is i's lowest set bit."),
        _chk("Why can a Fenwick tree answer range sums but not range minimums?",
             "It builds a range from two prefixes by subtraction, and minimum has no inverse. "
             "A segment tree combines covering nodes directly instead."),
        _chk("How do you add v to every element of [l, r] with Fenwick trees?",
             "Keep a difference array: +v at l and −v at r + 1. For range sums, add a second "
             "tree holding d[j]·j, since prefix(i) = (i + 1)·Σd − Σd·j."),
        _chk("How does \"count smaller elements to the right\" become a Fenwick problem?",
             "Scan right to left so the elements to the right are the ones already inserted; "
             "index the tree by value rank and query how many inserted ranks are below the current one."),
        _chk("Why can the two-Fenwick trick do range *addition* but not range *assignment*?",
             "Because the effect of \"+v on [l, r]\" on any prefix is a linear function of v, so "
             "it can be recorded as two point updates on a difference array. Assignment's effect "
             "depends on what was already there, which no difference array records. That is what "
             "lazy propagation is for."),
        _chk("Where must `push` be called in a lazy segment tree, and what breaks if you miss one?",
             "At the top of both `update` and `query`, before either descends. Missing it in "
             "`query` gives correct answers until the first range update and stale ones after — "
             "a bug small tests do not reach."),
        _chk("Why does a sparse table answer in O(1) while a segment tree needs O(log n)?",
             "Because it covers the range with two *overlapping* blocks instead of a disjoint "
             "decomposition, and `min(x, x) = x` makes the overlap harmless. Sums are not "
             "idempotent, so the same trick would double-count."),
        _chk("Given a static array and 10⁶ range-sum queries, which structure?",
             "Prefix sums. O(n) to build and O(1) per query, with no tree at all — building a "
             "Fenwick or segment tree here is more code for a worse constant."),
    ],
    bigo=[
        _bigo(r"""
for (int i = idx + 1; i <= n; i += i & -i)       // Fenwick update, n elements
    tree[i] += delta;
""", "O(log n)", ["O(log n)", "O(n)", "O(1)", "O(√n)"],
            "Each step moves to an index whose lowest set bit is strictly higher, and there "
            "are only log n bits."),
        _bigo(r"""
long[] prefix = new long[n + 1];                  // q operations, each a set or a sum
for (String[] op : ops) {
    if (op[0].equals("set")) { a[i] = v; for (int j = 0; j < n; j++) prefix[j + 1] = prefix[j] + a[j]; }
    else out.add(prefix[r + 1] - prefix[l]);
}
""", "O(q·n)", ["O(q·n)", "O(q + n)", "O(q log n)", "O(n log n)"],
            "Every `set` rebuilds the prefix array. With q and n both 10⁵ that is 10¹⁰ — a "
            "Fenwick tree makes both operations O(log n)."),
        _bigo(r"""
for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {   // segment tree query
    if ((l & 1) == 1) res = Math.min(res, t[l++]);
    if ((r & 1) == 1) res = Math.min(res, t[--r]);
}
""", "O(log n)", ["O(log n)", "O(r − l)", "O(n)", "O(log² n)"],
            "Both ends climb one level per iteration and take at most one node per level each, "
            "however wide the range."),
        _bigo(r"""
int[] sorted = Arrays.stream(a).distinct().sorted().toArray();   // n values
for (int i = n - 1; i >= 0; i--) {
    int rank = Arrays.binarySearch(sorted, a[i]);
    res[i] = (int) prefix(rank - 1);               // Fenwick
    add(rank, 1);
}
""", "O(n log n)", ["O(n log n)", "O(n²)", "O(n)", "O(n log² n)"],
            "One sort, then n binary searches and 2n Fenwick operations, each O(log n)."),
    ],
    interview="""
Offer the prefix-sum answer first and name its failure: "updates make me rebuild
it". Then the Fenwick tree, with the one-sentence explanation of `i & -i`. If the
operation is a minimum, say that a Fenwick tree cannot do it and why — that
distinction is what shows you understand the structure rather than its code.
""",
    rungs=[
        _rung("Warm up", "The baseline every structure here is measured against.",
              ["static-range-sums"],
              {"static-range-sums": "Prefix sums, O(1) per query. Then ask what one update would cost — that answer is the reason for the rest of this unit."}),
        _rung("Core", "Point updates with range sums, range minimums, and the static shortcut.",
              ["range-sum-point-update", "range-min-queries", "sparse-table-range-min"],
              {"range-sum-point-update": "A Fenwick tree. `set` is an add of the difference, so keep the plain array too.",
               "range-min-queries": "A segment tree, because minimum has no inverse. Write the iterative version.",
               "sparse-table-range-min": "The same question as the one above with the updates removed — and removing them buys O(1). Say out loud why the two blocks may overlap."}),
        _rung("Stretch", "Counting by rank, and updates to whole ranges.",
              ["count-smaller-after-self", "range-add-range-sum", "range-assign-range-sum"],
              {"count-smaller-after-self": "Right to left, a Fenwick tree over value ranks, and query strictly below your own rank.",
               "range-add-range-sum": "A difference array in two Fenwick trees. Derive `(i + 1)·Σd − Σd·j` before coding.",
               "range-assign-range-sum": "The one the Fenwick trick cannot reach. Write `apply` and `push` first, then the two recursions — and put `push` in the query."}),
    ],
    next_up="""
Trees over arrays. The next unit returns to graphs, for the questions a plain
traversal cannot answer: which vertex is a single point of failure, which groups
reach each other, and whether every edge can be walked exactly once.
""",
)


# --- Unit 39 — Advanced graphs -----------------------------------------------

_unit(
    "advanced-graphs", "Advanced Graphs", "🗺️", _S8,
    "Cut vertices, bridges, strongly connected components and Euler paths — each in one DFS.",
    weight=1,
    prereqs=["graph-traversal", "topological-sort"],
    why="""
The core graph units answer "can I reach it", "in what order", "is it connected"
and "how far". Three more questions need something extra from a DFS:

- **Which vertex or edge, if removed, disconnects the graph?** Single points of
  failure in a network.
- **Which vertices can all reach each other?** Strongly connected components of
  a directed graph — the cycles, condensed.
- **Can every edge be walked exactly once?** An Euler path, and how to build it.

The first two are answered by the same trick — recording, for each vertex, how
high up the DFS tree its subtree can climb with one back edge. The third is
decided by counting degrees, and built by a DFS that records vertices on the way
back.
""",
    model="""
### Discovery times and low-links

Run a DFS numbering vertices in visit order: `disc[u]`. Then `low[u]` is the
smallest `disc` reachable from u's subtree using tree edges down and **one** back
edge up.

```java
void dfs(int u, int parent) {
    disc[u] = low[u] = ++timer;
    for (int v : adj[u]) {
        if (v == parent) continue;
        if (disc[v] != 0) low[u] = Math.min(low[u], disc[v]);   // back edge
        else { dfs(v, u); low[u] = Math.min(low[u], low[v]); }
    }
}
```

- **Articulation point**: a non-root u with a child v where `low[v] ≥ disc[u]` —
  v's subtree cannot get above u without it. The root is one only if it has two or
  more DFS children.
- **Bridge**: a tree edge u–v with `low[v] > disc[u]` — strictly greater, because
  v's subtree cannot even reach u without that edge.

### Strongly connected components (Tarjan)

In a directed graph, keep visited-but-unassigned vertices on a stack. When a
vertex finishes with `low[u] == disc[u]`, nothing below it reaches anything
earlier that is still unassigned — u is the root of a component, and the
component is the stack down to u.

```java
if (low[u] == disc[u]) {
    int x;
    do { x = stack.pop(); onStack[x] = false; comp[x] = count; } while (x != u);
    count++;
}
```

Only vertices **still on the stack** may lower `low[u]`: an edge into an
already-finished component is one-way.

**Kosaraju** is the alternative: DFS for finish order, reverse every edge, DFS
again in decreasing finish order; each second-pass tree is a component.

### Euler paths

A trail using every edge exactly once exists (undirected) when:

1. all vertices with edges are in one component, and
2. 0 or 2 vertices have odd degree — 0 means it can be a closed circuit; with 2,
   it must start at one odd vertex and end at the other.

Directed: every vertex has in = out, except possibly one with out − in = 1 (the
start) and one with in − out = 1 (the end).

**Hierholzer** builds it: walk, consuming edges, until stuck; the vertex you are
stuck at goes on the *front* of the route. Detours discovered later are spliced in
automatically because the route is built from the end backwards.

```java
void visit(String a) {
    PriorityQueue<String> q = out.get(a);
    while (q != null && !q.isEmpty()) visit(q.poll());
    route.addFirst(a);
}
```

With a priority queue per vertex, the result is the lexicographically smallest
Euler path.
""",
    signals=[
        _sig("“critical router / junction”, “single point of failure”", "Articulation points (low-link DFS)",
             "Child subtree with low ≥ disc of the parent."),
        _sig("“critical connection / bridge”", "Bridges: low[v] > disc[u]",
             "Strictly greater — the edge itself is the only way up."),
        _sig("“groups that can all reach each other”, directed", "Strongly connected components",
             "Tarjan (one DFS + stack) or Kosaraju (two passes)."),
        _sig("“use every edge / ticket exactly once”", "Euler path — Hierholzer",
             "Check degrees first; build by prepending on the way back."),
        _sig("“draw without lifting the pen”", "Degree parity + connectivity",
             "0 or 2 odd vertices; no search needed."),
        _sig("A directed graph with cycles, and a DAG algorithm wanted", "Condense the SCCs",
             "The component graph is always a DAG."),
    ],
    skeletons=[
        _sk("Articulation points and bridges",
            "Undirected; one DFS computes both.",
            """
void dfs(int u, int parent) {
    disc[u] = low[u] = ++timer;
    int children = 0;
    for (int v : adj.get(u)) {
        if (v == parent) continue;
        if (disc[v] != 0) { low[u] = Math.min(low[u], disc[v]); continue; }
        children++;
        dfs(v, u);
        low[u] = Math.min(low[u], low[v]);
        if (parent != -1 && low[v] >= disc[u]) cut[u] = true;
        if (low[v] > disc[u]) bridges.add(new int[]{u, v});
    }
    if (parent == -1 && children > 1) cut[u] = true;
}
""",
            "With repeated edges, skip the parent by edge id rather than by vertex."),
        _sk("Tarjan's SCC",
            "Directed; components found as their roots finish.",
            """
void dfs(int u) {
    disc[u] = low[u] = ++timer;
    stack.push(u); onStack[u] = true;
    for (int v : adj.get(u)) {
        if (disc[v] == 0) { dfs(v); low[u] = Math.min(low[u], low[v]); }
        else if (onStack[v]) low[u] = Math.min(low[u], disc[v]);
    }
    if (low[u] == disc[u]) {
        int x;
        do { x = stack.pop(); onStack[x] = false; comp[x] = comps; } while (x != u);
        comps++;
    }
}
""",
            "Recursion depth can reach V; switch to an explicit stack for very large graphs."),
        _sk("Hierholzer (iterative)",
            "Euler path through every edge; smallest order with priority queues.",
            """
Deque<String> st = new ArrayDeque<>();
LinkedList<String> route = new LinkedList<>();
st.push(start);
while (!st.isEmpty()) {
    PriorityQueue<String> q = out.get(st.peek());
    if (q != null && !q.isEmpty()) st.push(q.poll());   // take an unused edge
    else route.addFirst(st.pop());                       // stuck: record, back up
}
""",
            "The route comes out in order because vertices are prepended as the walk unwinds."),
    ],
    traces=[
        _trace(
            "Low-links on edges 0–1, 1–2, 2–0, 1–3, 3–4, DFS from 0",
            "Visit order 0, 1, 2 (back edge to 0), then 3, 4. `low` is final, after every "
            "child has returned. The deciding comparison is child low against parent disc.",
            ["Vertex", "disc", "low", "Deciding comparison", "Articulation point?"],
            [
                ["0", "1", "1", "root with one DFS child (1)", "no"],
                ["1", "2", "1", "child 3: low[3] = 4 ≥ disc[1] = 2", "**yes**"],
                ["2", "3", "1", "back edge 2 → 0 lowers it to disc[0]", "no (leaf of the DFS tree)"],
                ["3", "4", "4", "child 4: low[4] = 5 ≥ disc[3] = 4", "**yes**"],
                ["4", "5", "5", "no children", "no"],
            ],
            "Vertex 1's child 2 has low 1 < 2 — the triangle climbs above 1 — so that child "
            "alone would not make 1 critical. Child 3 cannot, and one such child is enough. "
            "The edges 1–3 and 3–4 are also bridges: low[3] = 4 > disc[1] = 2 and "
            "low[4] = 5 > disc[3] = 4.",
        ),
    ],
    costs=[
        _cost("Articulation points / bridges", "O(V + E)", "O(V)", "One DFS."),
        _cost("Tarjan SCC", "O(V + E)", "O(V)", "One DFS and a stack."),
        _cost("Kosaraju SCC", "O(V + E)", "O(V + E)", "Two DFS passes and a reversed graph."),
        _cost("Euler path, Hierholzer", "O(E log E)", "O(E)", "O(E) without the lexicographic priority queues."),
        _cost("Remove each vertex and re-traverse", "O(V · (V + E))", "O(V)", "What low-links replace."),
    ],
    pitfalls=[
        _pit("Every vertex on a cycle is reported as critical",
             "The parent check skipped every edge back to the parent, including legitimate back edges in multigraphs — or low was updated with `low[v]` for a visited v.",
             "For visited neighbours use `disc[v]`; skip only the tree edge to the parent (by edge id with repeated edges)."),
        _pit("The DFS root is always (or never) critical",
             "The general `low[v] ≥ disc[u]` rule was applied to the root.",
             "The root is critical exactly when it has two or more DFS children."),
        _pit("Two SCCs are merged",
             "`low[u]` was lowered through an edge into an already-assigned component.",
             "Only neighbours that are still on the stack count."),
        _pit("An Euler path is reported for two separate cycles",
             "Degrees were checked but connectivity was not.",
             "All vertices with edges must be in one component."),
        _pit("The itinerary strands tickets",
             "The walk greedily appended vertices in visit order.",
             "Hierholzer: append when stuck, to the *front* of the route."),
        _pit("`StackOverflowError` on a long path graph",
             "Recursive DFS depth reached V.",
             "Run the DFS with an explicit stack, or increase the thread stack size."),
    ],
    lessons=["graph_repr", "graph_cycle", "topo"],
    checks=[
        _chk("What does `low[u]` mean?",
             "The smallest discovery time reachable from u's DFS subtree using tree edges "
             "downwards and at most one back edge."),
        _chk("Why does an articulation point use `≥` and a bridge `>`?",
             "For a vertex u, the subtree reaching u itself is still cut off without u. For an "
             "edge u–v, reaching u from v's subtree by another route means the edge is not needed."),
        _chk("In Tarjan's algorithm, why must `low` ignore vertices no longer on the stack?",
             "They belong to components already completed; an edge into one is one-way, so "
             "using it would merge vertices that cannot reach each other."),
        _chk("When does an undirected graph have an Euler path?",
             "When every vertex with an edge is in one component and 0 or 2 vertices have odd degree."),
        _chk("Why does Hierholzer prepend vertices when it gets stuck?",
             "The first vertex it gets stuck at must be the end of the path. Building from the "
             "end backwards lets unused detours be spliced in as the walk unwinds."),
    ],
    bigo=[
        _bigo(r"""
for (int skip = 0; skip < V; skip++)             // V vertices, E edges
    if (components(graphWithout(skip)) > base)   // BFS over the rest
        critical.add(skip);
""", "O(V·(V + E))", ["O(V·(V + E))", "O(V + E)", "O(E log V)", "O(V²·E)"],
            "A full traversal per removed vertex. The low-link DFS finds every articulation "
            "point in a single O(V + E) pass."),
        _bigo(r"""
void dfs(int u) {                                // Tarjan SCC, V vertices, E edges
    disc[u] = low[u] = ++timer; stack.push(u); onStack[u] = true;
    for (int v : adj.get(u)) {
        if (disc[v] == 0) { dfs(v); low[u] = Math.min(low[u], low[v]); }
        else if (onStack[v]) low[u] = Math.min(low[u], disc[v]);
    }
    if (low[u] == disc[u]) { /* pop one component */ }
}
""", "O(V + E)", ["O(V + E)", "O(V²)", "O(V·E)", "O((V + E) log V)"],
            "Each vertex is visited once and pushed and popped once; each edge is examined "
            "once from its tail."),
        _bigo(r"""
int odd = 0;                                     // Euler path check
for (int v = 0; v < V; v++) if (deg[v] % 2 == 1) odd++;
boolean connected = oneComponentAmongNonIsolated(adj);   // one BFS
""", "O(V + E)", ["O(V + E)", "O(E!)", "O(V²)", "O(2^E)"],
            "Counting degrees and one traversal. Searching for the trail directly would be "
            "backtracking over edge orders — the theorem is the whole speed-up."),
        _bigo(r"""
st.push(start);                                  // Hierholzer, E tickets
while (!st.isEmpty()) {
    PriorityQueue<String> q = out.get(st.peek());
    if (q != null && !q.isEmpty()) st.push(q.poll());
    else route.addFirst(st.pop());
}
""", "O(E log E)", ["O(E log E)", "O(E²)", "O(E)", "O(E!)"],
            "Every edge is pushed and polled exactly once; the priority queues add a log for "
            "the alphabetical order. Plain lists would make it O(E)."),
    ],
    interview="""
"Find the critical connections" is the one that appears in interviews, and the
answer is Tarjan's low-links — name it, define low in one sentence, and state the
`low[v] > disc[u]` condition before writing the DFS. For itinerary-style problems,
say "Eulerian path" and explain why a plain greedy walk strands tickets; the
prepend-when-stuck idea is what they want to hear.
""",
    rungs=[
        _rung("Warm up", "A search problem that turns out to be two counts.",
              ["euler-path-exists"],
              {"euler-path-exists": "Degree parity and one connectivity check. Two separate triangles are the counterexample to checking degrees alone."}),
        _rung("Core", "Low-links for cut vertices, and Tarjan for components.",
              ["articulation-points", "count-scc"],
              {"articulation-points": "disc, low, and the root rule. Check your answer against removing each vertex by brute force on small graphs.",
               "count-scc": "Tarjan with an on-stack flag. The hidden case with an edge into a finished component is the one that catches a missing check."}),
        _rung("Stretch", "Bridges, and building an Euler path.",
              ["reconstruct-itinerary"],
              {"reconstruct-itinerary": "Hierholzer with a priority queue per airport: walk until stuck, prepend on the way back."}),
    ],
    next_up="""
One unit left: when a problem has at most twenty things and the question is which
subset, the subset itself can be the DP state.
""",
)


# --- Unit 40 — Bitmask DP ----------------------------------------------------

_unit(
    "bitmask-dp", "Bitmask Dynamic Programming", "🔣", _S8,
    "When n ≤ 20, a subset is an integer — and an integer can index a table.",
    weight=1,
    prereqs=["bit-manipulation", "dp-1d", "graph-traversal"],
    why="""
Assign n workers to n jobs, visit every room, split numbers into k equal groups:
brute force tries every ordering, n! of them. But usually the future does not
depend on the *order* of past choices — only on **which** items are used up. There
are 2ⁿ such sets, and for n = 16 that is 65,536 instead of 2·10¹³.

An `int` with n bits represents a set exactly: bit i set means item i is in.
Masks are array indices, set operations are single CPU instructions, and every
DP technique so far works with a mask as the state. The constraint "n ≤ 20" in a
problem is very often the author telling you to do exactly this.
""",
    model="""
### Sets as integers

| Operation | Code |
| --- | --- |
| Is item i in the set? | `(mask >> i & 1) == 1` |
| Add item i | `mask \\| 1 << i` |
| Remove item i | `mask & ~(1 << i)` |
| Size of the set | `Integer.bitCount(mask)` |
| The full set of n items | `(1 << n) − 1` |
| Every subset | `for (int mask = 0; mask < 1 << n; mask++)` |
| Every subset of `mask` | `for (int s = mask; s > 0; s = (s − 1) & mask)` |

### DP over subsets

The state is `dp[mask]` (sometimes with an extra index). Every transition adds a
bit, so it goes to a larger integer — looping masks upwards is always a valid
order.

**Assignment.** Give the jobs in `mask` to the first `bitCount(mask)` workers:

```java
dp[0] = 0;
for (int mask = 0; mask < 1 << n; mask++) {
    int worker = Integer.bitCount(mask);
    if (worker == n) continue;
    for (int j = 0; j < n; j++)
        if ((mask >> j & 1) == 0)
            dp[mask | 1 << j] = Math.min(dp[mask | 1 << j], dp[mask] + cost[worker][j]);
}
```

The worker index is not stored — it is implied by how many jobs are taken.

**Travelling-salesman shape.** `dp[mask][v]` = cheapest way to visit exactly the
set `mask`, ending at v. Transition to any w not in mask. O(2ⁿ · n²).

### BFS over (vertex, mask)

"Shortest walk visiting every node" in an unweighted graph is BFS where the state
is `(node, visited set)`. The same node with a different visited set is a
different state — which is exactly why BFS on nodes alone cannot solve it. Seed
every `(v, 1 << v)` at distance 0 to allow any start.

### Partitioning into k groups

"Split into k groups with equal sums": `dp[mask]` = the fill of the current,
partly built group after placing the items in `mask` (−1 if unreachable). Add an
item only if it fits in the current group's remaining space; a group is complete
when the fill reaches the target, and wraps to 0. O(2ⁿ · n).
""",
    signals=[
        _sig("n ≤ 16, 18 or 20, and “assign”, “choose a subset”, “visit all”", "Bitmask DP",
             "2ⁿ states is fine; n! orderings is not."),
        _sig("“shortest path visiting every node”", "BFS over (node, visited mask)",
             "Multi-source: every node with its own bit at distance 0."),
        _sig("“assign n workers to n jobs”", "dp[mask], worker = bitCount(mask)",
             "The worker index is implied by the mask."),
        _sig("“split into k groups with equal sums”, n ≤ 16", "dp[mask] = fill of the current group",
             "Wrap to 0 when a group reaches the target."),
        _sig("“sum / XOR / OR over all subsets”, n ≤ 20", "Enumerate masks 0 … 2ⁿ − 1",
             "Then look for the per-bit shortcut."),
        _sig("n up to 40", "Meet in the middle",
             "Two halves of 2²⁰ each, combined by sorting or hashing."),
    ],
    skeletons=[
        _sk("Enumerate subsets",
            "Every subset of n items; every submask of a mask.",
            """
for (int mask = 0; mask < (1 << n); mask++) {
    for (int i = 0; i < n; i++)
        if ((mask >> i & 1) == 1) { /* item i is in this subset */ }
}

for (int s = mask; s > 0; s = (s - 1) & mask) { /* s is a non-empty submask */ }
""",
            "Submask enumeration over every mask totals O(3ⁿ), not O(4ⁿ)."),
        _sk("Assignment over masks",
            "n workers, n jobs, one each.",
            """
long[] dp = new long[1 << n];
Arrays.fill(dp, Long.MAX_VALUE);
dp[0] = 0;
for (int mask = 0; mask < (1 << n); mask++) {
    if (dp[mask] == Long.MAX_VALUE) continue;
    int k = Integer.bitCount(mask);
    if (k == n) continue;
    for (int j = 0; j < n; j++)
        if ((mask >> j & 1) == 0)
            dp[mask | 1 << j] = Math.min(dp[mask | 1 << j], dp[mask] + cost[k][j]);
}
return dp[(1 << n) - 1];
""",
            "Skip unreachable masks before adding to them."),
        _sk("BFS over (node, mask)",
            "Shortest walk visiting all nodes.",
            """
int full = (1 << n) - 1;
int[][] dist = new int[n][1 << n];
for (int[] row : dist) Arrays.fill(row, -1);
ArrayDeque<int[]> q = new ArrayDeque<>();
for (int v = 0; v < n; v++) { dist[v][1 << v] = 0; q.add(new int[]{v, 1 << v}); }
while (!q.isEmpty()) {
    int[] s = q.poll();
    if (s[1] == full) return dist[s[0]][s[1]];
    for (int w : adj.get(s[0])) {
        int m = s[1] | 1 << w;
        if (dist[w][m] == -1) { dist[w][m] = dist[s[0]][s[1]] + 1; q.add(new int[]{w, m}); }
    }
}
""",
            "n · 2ⁿ states: fine at n = 12, too many at n = 25."),
    ],
    traces=[
        _trace(
            "Assignment DP on costs [[6, 2, 8], [3, 7, 4], [5, 9, 1]]",
            "`dp[mask]` = cheapest way to give the jobs in `mask` to workers 0 … bitCount − 1. "
            "Masks are written job 2, job 1, job 0 from left to right. Rows are in increasing "
            "mask order, which fills every state before anything reads it.",
            ["mask", "Jobs taken", "Worker who took the last job", "dp[mask]"],
            [
                ["000", "{}", "—", "0"],
                ["001", "{0}", "worker 0", "6"],
                ["010", "{1}", "worker 0", "2"],
                ["011", "{0, 1}", "worker 1", "min(6 + 7, 2 + 3) = **5**"],
                ["100", "{2}", "worker 0", "8"],
                ["101", "{0, 2}", "worker 1", "min(6 + 4, 8 + 3) = 10"],
                ["110", "{1, 2}", "worker 1", "min(2 + 4, 8 + 7) = **6**"],
                ["111", "all", "worker 2", "min(5 + 1, 10 + 9, 6 + 5) = **6**"],
            ],
            "Eight states instead of 3! = 6 orderings — no win at n = 3, but at n = 16 it is "
            "65,536 states against 2·10¹³ orderings. The answer, 6, comes from mask 011: "
            "workers 0 and 1 took jobs 1 and 0 for 5, and worker 2 took job 2 for 1.",
        ),
    ],
    costs=[
        _cost("Enumerating all subsets", "O(2ⁿ · n)", "O(1)", "n ≤ 20 is about 2·10⁷."),
        _cost("Assignment DP", "O(2ⁿ · n)", "O(2ⁿ)", "One state per subset of jobs."),
        _cost("TSP over (mask, end)", "O(2ⁿ · n²)", "O(2ⁿ · n)", "n ≤ 16 or so."),
        _cost("BFS over (node, mask)", "O(2ⁿ · n²)", "O(2ⁿ · n)", "Each state has up to n neighbours."),
        _cost("All submasks of all masks", "O(3ⁿ)", "O(2ⁿ)", "Each item is out, in the submask, or in the mask only."),
    ],
    pitfalls=[
        _pit("`1 << n` is negative or zero",
             "n reached 31 or 32 on an `int`.",
             "Bitmask DP is for n ≲ 20; use `1L <<` if a mask genuinely needs more bits."),
        _pit("A precedence bug makes the bit test always true",
             "`mask & 1 << i == 0` parses as `mask & ((1 << i) == 0)`.",
             "Parenthesise: `(mask >> i & 1) == 0` or `(mask & (1 << i)) == 0`."),
        _pit("The DP reads a state before it is final",
             "Masks were processed in an order where a transition went to a smaller integer.",
             "Transitions that only add bits make increasing mask order valid; check yours do."),
        _pit("BFS on nodes says the walk is impossible",
             "The visited set was per node, so a node could not be revisited with a different mask.",
             "Mark visited per (node, mask)."),
        _pit("Memory limit exceeded",
             "A `long[1 << 25][n]` table.",
             "Check 2ⁿ · (state size) before allocating; n ≈ 20 is the practical ceiling."),
    ],
    lessons=["bit_manip", "dp", "bfs"],
    checks=[
        _chk("Why is a bitmask a valid DP state for assignment problems?",
             "The cost of the remaining choices depends only on which jobs are taken, not on the "
             "order they were taken in — so 2ⁿ sets stand in for n! orderings."),
        _chk("Why is iterating masks in increasing order a valid fill order?",
             "Every transition sets an extra bit, producing a strictly larger integer, so every "
             "state a mask reads from was computed earlier."),
        _chk("Why must BFS for \"visit every node\" store the visited set in the state?",
             "Arriving at a node having seen {0, 1} and having seen {0, 2} have different futures. "
             "A visited flag per node alone would forbid the revisits the walk needs."),
        _chk("What constraint in a statement suggests bitmask DP?",
             "A small n — about 12 to 20 — alongside \"subset\", \"assign\" or \"visit all\"."),
    ],
    bigo=[
        _bigo(r"""
for (int mask = 0; mask < (1 << n); mask++)       // n items
    for (int i = 0; i < n; i++)
        if ((mask >> i & 1) == 1) sum += a[i];
""", "O(2ⁿ·n)", ["O(2ⁿ·n)", "O(n²)", "O(n!)", "O(2ⁿ)"],
            "2ⁿ masks, n bits checked in each. At n = 20 that is about 2·10⁷ — fine; at n = 30 it "
            "is 3·10¹⁰."),
        _bigo(r"""
int best = INF;                                    // n workers, n jobs
for (int[] perm : allPermutations(n))
    best = Math.min(best, costOf(perm));           // O(n) each
""", "O(n!·n)", ["O(n!·n)", "O(2ⁿ·n)", "O(n³)", "O(nⁿ)"],
            "Every ordering is tried. The mask DP replaces n! with 2ⁿ because it forgets the "
            "order in which jobs were taken."),
        _bigo(r"""
for (int mask = 1; mask < (1 << n); mask++)       // TSP: dp[mask][end]
    for (int v = 0; v < n; v++)
        for (int w = 0; w < n; w++)
            if ((mask >> w & 1) == 0)
                dp[mask | 1 << w][w] = Math.min(dp[mask | 1 << w][w], dp[mask][v] + d[v][w]);
""", "O(2ⁿ·n²)", ["O(2ⁿ·n²)", "O(2ⁿ·n)", "O(n!)", "O(n³)"],
            "2ⁿ masks × n end vertices × n next vertices."),
        _bigo(r"""
for (int mask = 0; mask < (1 << n); mask++)       // every submask of every mask
    for (int s = mask; s > 0; s = (s - 1) & mask)
        work(mask, s);                             // O(1)
""", "O(3ⁿ)", ["O(3ⁿ)", "O(4ⁿ)", "O(2ⁿ·n)", "O(2ⁿ)"],
            "Each item is in neither, in the mask only, or in both mask and submask: 3ⁿ pairs in "
            "total, not (2ⁿ)² = 4ⁿ."),
    ],
    interview="""
Point at the constraint: "n is at most 16, so 2ⁿ states is 65,536 — the state is
the set of jobs taken, and the worker is implied by its size." Then say why order
can be forgotten. For shortest-walk problems, say "BFS where the state is (node,
visited set)" before anything else; it is the step people miss.
""",
    rungs=[
        _rung("Warm up", "Subsets as the integers 0 … 2ⁿ − 1.",
              ["subset-xor-sum-total"],
              {"subset-xor-sum-total": "Enumerate every mask and XOR its bits. Then find the one-line shortcut — and notice the enumeration is what generalises."}),
        _rung("Core", "A subset as the DP state.",
              ["min-cost-assignment"],
              {"min-cost-assignment": "dp[mask], worker = bitCount(mask). Trace the 3×3 example against the table in this unit first."}),
        _rung("Stretch", "Subsets combined with a second dimension: a node, or a group being filled.",
              ["shortest-path-visit-all"],
              {"shortest-path-visit-all": "BFS over (node, mask), seeded from every node. The same node with a different mask is a different state."}),
    ],
    next_up="""
A subset as the state. The next unit keeps the tree fixed instead and moves the
work out of the query — the same bargain as a precomputed table, on a different
object.
""",
)
