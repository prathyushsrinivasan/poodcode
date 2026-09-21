# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 40 — the two bit topics the roadmap had nothing for.
#
#   gray-code-sequence         the reflected binary code, and why i ^ (i >> 1) is it
#   max-xor-subset             the linear basis over GF(2)
#   count-distinct-xor-values  2^rank — the basis spans, so the count is structural
#   kth-smallest-subset-xor    the reduced basis, indexed by the bits of k - 1
#
# `bit-manipulation` teaches masks, XOR's self-inverse and submask enumeration.
# These are the level above: treating the numbers as VECTORS and asking what
# their span looks like.
# ===========================================================================

_p(
    "gray-code-sequence", "One Switch at a Time", "Easy",
    topics=["Bit Manipulation", "Math"], subtopics=["Gray Code", "Constructive"],
    companies=["Amazon", "Intel"],
    shape="n", ret="String",
    todo="print i ^ (i >> 1) for i = 0 .. 2^n - 1",
    description=(
        "A control panel has `n` switches, so it has `2^n` states, each written as an "
        "`n`-bit number. You must visit **every** state exactly once, starting at `0`, and you "
        "may only flip **one switch** between consecutive states.\n\n"
        "Print such an order. When several are possible, print the **reflected binary code**: "
        "the sequence whose i-th entry is `i XOR (i >> 1)`.\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe `2^n` states in order, separated by single spaces, on one line."
    ),
    constraints="1 ≤ n ≤ 14",
    hints=[
        "Try n = 1 (0, 1) and n = 2 (0, 1, 3, 2) by hand. Notice how the n = 2 list is the n = 1 list, then the n = 1 list backwards with the new bit set.",
        "That reflection is the construction: G(n) = G(n-1), then reverse(G(n-1)) each with bit n-1 set. Mirroring means the two halves join on a single flip of the new bit.",
        "The closed form for the same sequence is `i ^ (i >> 1)` — no recursion and no list building.",
    ],
    opt=("O(2^n)", "O(1) beyond the output",
         "One XOR and one shift per state; nothing is stored."),
    editorial=(
        "## The one thing this teaches\n**A Gray code is a Hamiltonian path on the hypercube:** "
        "an order of all n-bit numbers in which neighbours differ in exactly one bit. Whenever a "
        "problem asks you to move through every configuration changing one thing at a time, this "
        "is the order.\n\n"
        "## Approach\n```java\nStringBuilder sb = new StringBuilder();\n"
        "for (int i = 0; i < (1 << n); i++) {\n"
        "    if (i > 0) sb.append(' ');\n    sb.append(i ^ (i >> 1));\n}\n```\n\n"
        "## Why `i ^ (i >> 1)` works\nGo from `i` to `i + 1`. Binary addition flips a run of "
        "trailing 1s to 0s and the 0 above them to 1 — several bits at once. In "
        "`g = i ^ (i >> 1)` each output bit is `bit_k(i) XOR bit_{k+1}(i)`, so a *run* of flips "
        "in `i` mostly cancels in the XOR: every pair of adjacent changes cancels, and exactly "
        "one bit survives. That is the single flip.\n\n"
        "## Going back: the inverse\nFrom a Gray code `g`, recover its index by XOR-ing the "
        "running prefix:\n```java\nint i = g;\nfor (int s = 1; s < 32; s <<= 1) i ^= i >> s;\n```\n"
        "Encoding is a difference; decoding is a prefix XOR — the same relationship prefix "
        "sums have with difference arrays.\n\n"
        "## Where it is used\nRotary encoders and ADCs: if two bits changed at once, a reading "
        "taken mid-transition could be wildly wrong. With one bit changing, the worst a "
        "mid-transition read can be is one of the two neighbours."
    ),
    py='''
def solve(n):
    n = int(n)
    return " ".join(str(i ^ (i >> 1)) for i in range(1 << n))
''',
    java='''
    static String solve(long n) {
        StringBuilder sb = new StringBuilder();
        int total = 1 << (int) n;
        for (int i = 0; i < total; i++) {
            if (i > 0) sb.append(' ');
            sb.append(i ^ (i >> 1));
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "2\n"), ("Example 2", "3\n")],
    hidden=[
        ("One switch", "1\n"),
        ("Four switches", "4\n"),
        ("Five switches", "5\n"),
        ("The largest panel", "14\n"),
    ],
    expl=[
        "0, 1, 3, 2 in binary is 00, 01, 11, 10 — one bit changes each step, and 10 back to 00 would also be one bit.",
        "000, 001, 011, 010, 110, 111, 101, 100: the first four are the n = 2 answer, the last four are it reversed with the top bit on.",
    ],
    prereqs=[
        ("bit_manip", "XOR and a right shift on the same value."),
        ("loops_basic", "Counting to 2^n."),
    ],
)


_p(
    "max-xor-subset", "The Loudest Combination", "Medium",
    topics=["Bit Manipulation", "Math"], subtopics=["XOR Basis", "Linear Algebra", "Greedy"],
    companies=["Google", "Jane Street"],
    shape="arr", ret="long",
    todo="build a basis: reduce each value by the basis vectors above it, keep it at its leading bit; then greedily XOR in whatever raises the answer",
    description=(
        "You may switch on any subset of `n` amplifiers, including none. Switching on a set "
        "produces the **XOR** of their values. Print the largest value obtainable.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe maximum XOR of any subset (`0` if the best choice is to switch none on)."
    ),
    constraints="1 ≤ n ≤ 100000\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "There are 2ⁿ subsets, so they cannot be enumerated. But XOR has no carries: every bit is independent, which is a strong hint that linear algebra applies.",
        "Treat each number as a vector of bits over GF(2), where addition is XOR. Build a basis: keep at most one vector per leading bit, reducing each new value by the ones already kept.",
        "The basis spans exactly the same set of achievable values. Then go greedily from the top bit down: if XOR-ing in the basis vector at that bit makes the answer bigger, do it.",
    ],
    opt=("O(n · B)", "O(B)",
         "B = 30 bit positions; each value is reduced against at most B basis vectors."),
    editorial=(
        "## The one thing this teaches\n**XOR is addition in a vector space, so a set of numbers "
        "has a *basis*.** At most 30 vectors describe everything 100000 numbers can reach, and "
        "once you have them the answer is greedy.\n\n"
        "## Building the basis\n```java\nlong[] basis = new long[31];          // basis[b] has "
        "leading bit b, or 0\nfor (long x : a) {\n    long cur = x;\n"
        "    for (int b = 30; b >= 0; b--) {\n"
        "        if (((cur >> b) & 1) == 0) continue;\n"
        "        if (basis[b] == 0) { basis[b] = cur; break; }   // new direction\n"
        "        cur ^= basis[b];                                // reduce and keep looking\n"
        "    }\n    // cur == 0 means x was already reachable; it adds nothing\n}\n```\n\n"
        "## Reading off the maximum\n```java\nlong best = 0;\n"
        "for (int b = 30; b >= 0; b--)\n    if ((best ^ basis[b]) > best) best ^= basis[b];\n"
        "return best;\n```\n\n"
        "## Why greedy is optimal here\nEach basis vector owns a distinct leading bit, so "
        "XOR-ing in `basis[b]` flips bit b and touches nothing above it. Turning on the highest "
        "possible bit is therefore never a mistake: no later choice can take it away, and every "
        "value with that bit set beats every value without it.\n\n"
        "## Why duplicates cost nothing\nA value that reduces to 0 was already in the span — "
        "`{4, 4, 4}` has the same reachable set as `{4}`. That is why n can be 100000 while the "
        "basis is at most 30 vectors, and it is also the whole content of the next problem."
    ),
    py='''
def solve(a):
    BITS = 31
    basis = [0] * BITS
    for x in a:
        cur = x
        for b in range(BITS - 1, -1, -1):
            if not (cur >> b) & 1:
                continue
            if basis[b] == 0:
                basis[b] = cur
                break
            cur ^= basis[b]
    best = 0
    for b in range(BITS - 1, -1, -1):
        if basis[b] and (best ^ basis[b]) > best:
            best ^= basis[b]
    return best
''',
    java='''
    static long solve(int[] a) {
        final int BITS = 31;
        long[] basis = new long[BITS];
        for (int x : a) {
            long cur = x;
            for (int b = BITS - 1; b >= 0; b--) {
                if (((cur >> b) & 1L) == 0L) continue;
                if (basis[b] == 0) { basis[b] = cur; break; }
                cur ^= basis[b];
            }
        }
        long best = 0;
        for (int b = BITS - 1; b >= 0; b--)
            if (basis[b] != 0 && (best ^ basis[b]) > best) best ^= basis[b];
        return best;
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "4\n8 1 2 4\n")],
    hidden=[
        ("Every value the same", "3\n4 4 4\n"),
        ("All zeros", "4\n0 0 0 0\n"),
        ("One value", "1\n1000000000\n"),
        ("Overlapping high bits", "6\n536870912 805306368 268435456 3 5 6\n"),
        ("Powers of two plus noise", "7\n1 2 4 8 16 31 15\n"),
    ],
    expl=[
        "1 and 2 are independent; 3 is their XOR and adds nothing. The reachable values are 0, 1, 2, 3.",
        "Four independent bits, so every value from 0 to 15 is reachable and 15 is the best.",
    ],
    prereqs=[
        ("bit_manip", "Leading bit, and XOR as a bitwise operation."),
        ("greedy", "Take the highest bit whenever it is available."),
    ],
)


_p(
    "count-distinct-xor-values", "How Many Different Sounds", "Medium",
    topics=["Bit Manipulation", "Math"], subtopics=["XOR Basis", "Linear Algebra", "Counting"],
    companies=["Google", "Citadel"],
    shape="arr", ret="long",
    todo="build the XOR basis; the answer is 2 to the power of its size",
    description=(
        "The same amplifiers. Switching on a subset produces the XOR of its values, and the "
        "empty subset produces `0`. Count how many **distinct** values are obtainable.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe number of distinct achievable XOR values."
    ),
    constraints="1 ≤ n ≤ 100000\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "There are 2ⁿ subsets but far fewer values: `{4, 4}` has four subsets and two values.",
        "Build the XOR basis, exactly as for the maximum. A value that reduces to 0 was already reachable and changes nothing.",
        "Different subsets *of the basis* always give different XORs — if two agreed, their XOR would be a nonzero combination equal to 0, which a basis forbids. So the answer is 2^r where r is the basis size.",
    ],
    opt=("O(n · B)", "O(B)",
         "One basis build; the count is 2 to the power of its size."),
    editorial=(
        "## The one thing this teaches\n**The reachable set is a linear subspace, and a subspace "
        "of dimension r over GF(2) has exactly 2^r elements.** No enumeration, no hash set — "
        "the count falls out of the structure.\n\n"
        "## Approach\n```java\nlong[] basis = new long[31];\nint rank = 0;\n"
        "for (int x : a) {\n    long cur = x;\n"
        "    for (int b = 30; b >= 0 && cur != 0; b--) {\n"
        "        if (((cur >> b) & 1) == 0) continue;\n"
        "        if (basis[b] == 0) { basis[b] = cur; rank++; break; }\n"
        "        cur ^= basis[b];\n    }\n}\nreturn 1L << rank;\n```\n\n"
        "## Why the values are exactly 2^r\nEvery reachable value is some XOR of basis vectors, "
        "so there are at most 2^r. And no two distinct basis subsets collide: if "
        "`XOR(S) == XOR(T)` then `XOR(S △ T) == 0` with `S △ T` non-empty, which "
        "contradicts independence. At most 2^r and at least 2^r, so exactly.\n\n"
        "## The empty subset counts\n`0` is always reachable, which is why the answer is 2^r and "
        "not 2^r − 1. With every input zero, the rank is 0 and the answer is 1.\n\n"
        "## The scale of the compression\nn = 100000 values over 30 bits: 2¹⁰⁰⁰⁰⁰ "
        "subsets collapse to at most 2³⁰ values, and 30 numbers describe all of them. "
        "That is what a basis buys."
    ),
    py='''
def solve(a):
    BITS = 31
    basis = [0] * BITS
    rank = 0
    for x in a:
        cur = x
        for b in range(BITS - 1, -1, -1):
            if not (cur >> b) & 1:
                continue
            if basis[b] == 0:
                basis[b] = cur
                rank += 1
                break
            cur ^= basis[b]
    return 1 << rank
''',
    java='''
    static long solve(int[] a) {
        final int BITS = 31;
        long[] basis = new long[BITS];
        int rank = 0;
        for (int x : a) {
            long cur = x;
            for (int b = BITS - 1; b >= 0; b--) {
                if (((cur >> b) & 1L) == 0L) continue;
                if (basis[b] == 0) { basis[b] = cur; rank++; break; }
                cur ^= basis[b];
            }
        }
        return 1L << rank;
    }
''',
    examples=[("Example 1", "3\n1 2 3\n"), ("Example 2", "3\n4 4 4\n")],
    hidden=[
        ("All zeros", "4\n0 0 0 0\n"),
        ("Independent powers of two", "5\n1 2 4 8 16\n"),
        ("Duplicates and a dependency", "6\n7 7 3 4 4 3\n"),
        ("One large value", "1\n999999999\n"),
        ("Dependent triple, then a new direction", "5\n5 6 3 1024 2048\n"),
    ],
    expl=[
        "The basis is {1, 2} because 3 = 1 XOR 2. Two independent directions give 2² = 4 values: 0, 1, 2, 3.",
        "One direction only, so two values: 0 and 4.",
    ],
    prereqs=[
        ("bit_manip", "XOR, and a value's leading bit."),
        ("math_digits", "Powers of two as a count of combinations."),
    ],
)


_p(
    "kth-smallest-subset-xor", "The k-th Quietest Combination", "Hard",
    topics=["Bit Manipulation", "Math"], subtopics=["XOR Basis", "Linear Algebra", "Constructive"],
    companies=["Jane Street", "Google"],
    shape="arr_k", ret="long",
    todo="build the basis, fully reduce it so each pivot appears in exactly one vector, sort it, then let the bits of k-1 pick vectors",
    description=(
        "The same amplifiers again. List every **distinct** XOR value a subset can produce, "
        "sorted from smallest to largest — the list always starts with `0`, from the empty "
        "subset. Print the `k`-th entry, counting from 1.\n\n"
        "If there are fewer than `k` distinct values, print `-1`.\n\n"
        "### Input\nLine 1: `n k`.\nLine 2: `n` integers.\n\n"
        "### Output\nThe `k`-th smallest achievable XOR, or `-1`."
    ),
    constraints="1 ≤ n ≤ 100000\n1 ≤ k ≤ 10^9\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "The previous problem showed there are exactly 2^r values, so first check whether k exceeds that — and be careful, 2^r can overflow a 32-bit int.",
        "Build the basis, then **fully reduce** it: for every basis vector, clear its leading bit out of all the others. Now each pivot bit appears in exactly one vector.",
        "Sort the reduced vectors ascending. Because their pivots are distinct and cleared elsewhere, XOR-ing in the i-th one always *increases* the value and never disturbs an earlier choice — so reading the bits of k-1 from the bottom picks the k-th smallest.",
    ],
    opt=("O(n · B + B²)", "O(B)",
         "The basis build dominates; the reduction is 30² steps and the answer is a walk over its bits."),
    editorial=(
        "## The one thing this teaches\n**A reduced basis turns a subspace into a counter.** "
        "Once each pivot bit lives in exactly one vector, the sorted list of 2^r values is "
        "*indexed* by the binary representation of the position — the r vectors behave like r "
        "independent digits.\n\n"
        "## Approach\n```java\n// 1. ordinary basis build (see max-xor-subset)\n"
        "// 2. full reduction: no pivot bit survives in any other vector\n"
        "for (int b = 0; b <= 30; b++) {\n    if (basis[b] == 0) continue;\n"
        "    for (int h = b + 1; h <= 30; h++)\n"
        "        if (basis[h] != 0 && ((basis[h] >> b) & 1) == 1) basis[h] ^= basis[b];\n}\n\n"
        "// 3. the surviving vectors, ascending\nlong[] v = nonZeroAscending(basis);\n"
        "if (k > (1L << v.length)) return -1;\n\nlong ans = 0, idx = k - 1;\n"
        "for (int i = 0; i < v.length; i++)\n"
        "    if (((idx >> i) & 1) == 1) ans ^= v[i];\nreturn ans;\n```\n\n"
        "## Why reduction is the whole trick\nWithout it, XOR-ing in a vector can *lower* the "
        "value by clearing a bit some earlier vector set, and the correspondence with counting "
        "breaks. After it, vector i is the only one holding pivot i, so including it strictly "
        "raises the result — and the order of the 2^r values matches the order of the 2^r "
        "masks. Sorting the reduced vectors is the same as sorting by pivot.\n\n"
        "## The off-by-one\n`k` is 1-based and the smallest value is `0` (the empty subset), so "
        "the mask to use is `k - 1`, not `k`. k = 1 must give 0.\n\n"
        "## The overflow\nWith r = 30, `1 << r` is a billion — still an `int`, barely. Write "
        "`1L << r` anyway: the shift is where the comparison against k lives, and a negative "
        "count silently answers `-1` for every k."
    ),
    py='''
def solve(a, k):
    BITS = 31
    basis = [0] * BITS
    for x in a:
        cur = x
        for b in range(BITS - 1, -1, -1):
            if not (cur >> b) & 1:
                continue
            if basis[b] == 0:
                basis[b] = cur
                break
            cur ^= basis[b]
    for b in range(BITS):
        if basis[b] == 0:
            continue
        for h in range(b + 1, BITS):
            if basis[h] and (basis[h] >> b) & 1:
                basis[h] ^= basis[b]
    vals = sorted(v for v in basis if v)
    r = len(vals)
    if k > (1 << r):
        return -1
    idx = k - 1
    res = 0
    for i in range(r):
        if (idx >> i) & 1:
            res ^= vals[i]
    return res
''',
    java='''
    static long solve(int[] a, long k) {
        final int BITS = 31;
        long[] basis = new long[BITS];
        for (int x : a) {
            long cur = x;
            for (int b = BITS - 1; b >= 0; b--) {
                if (((cur >> b) & 1L) == 0L) continue;
                if (basis[b] == 0) { basis[b] = cur; break; }
                cur ^= basis[b];
            }
        }
        for (int b = 0; b < BITS; b++) {
            if (basis[b] == 0) continue;
            for (int h = b + 1; h < BITS; h++)
                if (basis[h] != 0 && ((basis[h] >> b) & 1L) == 1L) basis[h] ^= basis[b];
        }
        List<Long> vals = new ArrayList<>();
        for (long v : basis) if (v != 0) vals.add(v);
        Collections.sort(vals);
        int r = vals.size();
        if (k > (1L << r)) return -1;
        long idx = k - 1, res = 0;
        for (int i = 0; i < r; i++) if (((idx >> i) & 1L) == 1L) res ^= vals.get(i);
        return res;
    }
''',
    examples=[("Example 1", "3 3\n1 2 3\n"), ("Example 2", "3 5\n1 2 3\n")],
    hidden=[
        ("The empty subset is first", "3 1\n7 9 11\n"),
        ("All zeros, k past the end", "4 2\n0 0 0 0\n"),
        ("Independent powers of two", "5 11\n1 2 4 8 16\n"),
        ("Duplicates collapse the count", "6 3\n4 4 4 9 9 9\n"),
        ("A dependency in the middle", "5 6\n5 6 3 1024 2048\n"),
        ("Large values", "4 4\n999999999 536870912 123456789 1\n"),
    ],
    expl=[
        "The reachable values are 0, 1, 2, 3; the third smallest is 2.",
        "Only four values exist, so there is no fifth.",
    ],
    prereqs=[
        ("bit_manip", "Pivot bits, and reading the bits of an index."),
        ("sorting", "The reduced basis, ascending."),
        ("overflow", "2^r against k needs a long shift."),
    ],
)
