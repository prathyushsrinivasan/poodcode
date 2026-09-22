# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 51 — Numbers, Bits & Grids, part 2: bit manipulation.
#
#   light-panel             an int as a set of 32 switches (the on-ramp)
#   range-xor               XOR of 0..n repeats with period 4
#   set-bits-up-to-n        count every set bit in 1..n, one bit position at a time
#   next-same-popcount      Gosper's hack: the next mask with the same number of bits
#   budget-subsets          every subset's sum, each built from a smaller mask
#   missing-and-duplicate   split the XOR by one bit where the two answers differ
#   pair-xor-total          per-bit contribution: ones x zeros x 2^b
#   max-and-pair            greedy from the top bit, keeping the survivors
# ===========================================================================


def _ops_case(lines):
    """An `ops`-shape input: the count, then one command per line."""
    return f"{len(lines)}\n" + "".join(l + "\n" for l in lines)


_p(
    "light-panel", "The Light Panel", "Intro",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "Bitmask", "Simulation"],
    companies=["Amazon", "Microsoft"],
    shape="ops", ret="String",
    todo="keep one int mask; on → mask |= 1 << i, off → mask &= ~(1 << i), flip → mask ^= 1 << i, check → (mask >> i) & 1, count → Integer.bitCount(mask)",
    description=(
        "A panel has 32 lights numbered `0` to `31`, all off. Process a list of commands:\n\n"
        "| Command | Effect |\n| --- | --- |\n"
        "| `on i` | switch light `i` on |\n| `off i` | switch light `i` off |\n"
        "| `flip i` | toggle light `i` |\n| `check i` | print `ON` or `OFF` for light `i` |\n"
        "| `count` | print how many lights are on |\n| `show` | print the whole panel as one integer: "
        "the sum of `2^i` over the lights that are on |\n\n"
        "Store the panel in a **single** integer.\n\n"
        "### Input\nLine 1: `q`.\nNext `q` lines: one command each.\n\n### Output\nOne line for "
        "each `check`, `count` and `show`, in order. There is at least one."
    ),
    constraints="1 ≤ q ≤ 100000\n0 ≤ i ≤ 31",
    hints=[
        "Light i is bit i of the integer. `1 << i` is a number with only that bit set.",
        "Set with `|`, clear with `& ~`, toggle with `^`, and test with `(mask >> i) & 1`.",
        "Light 31 is the sign bit of an `int`. For `show`, keep the panel in a `long`, or print `mask & 0xFFFFFFFFL`.",
    ],
    opt=("O(q)", "O(1)",
         "Every command is one or two machine instructions."),
    editorial=(
        "## The one thing this teaches\n**An int is 32 booleans.** Every later bit trick — "
        "subsets as masks, XOR folds, bitmask DP — assumes you can read and write one bit "
        "without thinking.\n\n"
        "## The four idioms\n```java\nmask |= 1L << i;          // on\n"
        "mask &= ~(1L << i);       // off\nmask ^= 1L << i;          // flip\n"
        "boolean on = (mask >> i & 1) == 1;   // check\n```\n\n"
        "`count` is `Long.bitCount(mask)`. `show` prints the mask itself.\n\n"
        "## The one trap\nLight 31 is bit 31 — the **sign bit** of an `int`. With `int mask`, "
        "turning it on makes the panel negative, and `show` would print `-2147483648` instead "
        "of `2147483648`. Using a `long` (and `1L << i`) keeps every value non-negative."
    ),
    py='''
def solve(ops):
    mask = 0
    out = []
    for op in ops:
        c = op[0]
        if c == "count":
            out.append(str(bin(mask).count("1")))
        elif c == "show":
            out.append(str(mask))
        else:
            i = int(op[1])
            if c == "on":
                mask |= 1 << i
            elif c == "off":
                mask &= ~(1 << i)
            elif c == "flip":
                mask ^= 1 << i
            else:
                out.append("ON" if mask >> i & 1 else "OFF")
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        long mask = 0;
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            String c = op[0];
            String line = null;
            if (c.equals("count")) line = String.valueOf(Long.bitCount(mask));
            else if (c.equals("show")) line = String.valueOf(mask);
            else {
                int i = Integer.parseInt(op[1]);
                if (c.equals("on")) mask |= 1L << i;
                else if (c.equals("off")) mask &= ~(1L << i);
                else if (c.equals("flip")) mask ^= 1L << i;
                else line = ((mask >> i) & 1) == 1 ? "ON" : "OFF";
            }
            if (line != null) {
                if (sb.length() > 0) sb.append('\\n');
                sb.append(line);
            }
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "7\non 0\non 3\ncheck 3\nflip 0\ncheck 0\ncount\nshow\n"),
        ("Example 2", "4\nflip 5\nflip 5\noff 2\nshow\n"),
    ],
    hidden=[
        ("Only a query", "1\ncount\n"),
        ("The sign bit", "3\non 31\nshow\ncheck 31\n"),
        ("Every light", _ops_case([f"on {i}" for i in range(32)] + ["count", "show"])),
        ("Off twice is still off", "5\non 7\noff 7\noff 7\ncheck 7\nshow\n"),
        ("Flip everything twice", _ops_case([f"flip {i}" for i in range(32)] + ["show"]
                                            + [f"flip {i}" for i in range(0, 32, 2)] + ["show"])),
        ("Long mixed", "12\non 1\non 2\non 30\nflip 2\ncheck 2\ncheck 30\noff 1\non 31\ncount\nshow\nflip 31\nshow\n"),
    ],
    expl=[
        "After `on 0` and `on 3` light 3 is on. `flip 0` turns light 0 off. One light is on, and the panel is 2³ = 8.",
        "Flipping light 5 twice leaves it off, and turning off a light that is already off changes nothing.",
    ],
    prereqs=[
        ("bit_manip", "Set, clear, toggle and test one bit with `|`, `& ~`, `^` and `>> i & 1`."),
        ("overflow", "Bit 31 is the sign bit of an int — use a long so the panel prints as a positive number."),
    ],
)


_p(
    "range-xor", "XOR of a Range", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "XOR", "Prefix XOR"],
    companies=["Google", "Amazon"],
    shape="two", ret="long",
    todo="f(n) = XOR of 0..n is n, 1, n + 1, 0 for n % 4 = 0, 1, 2, 3; the answer is f(r) ^ f(l - 1)",
    description=(
        "Compute `l ^ (l + 1) ^ (l + 2) ^ … ^ r`, where `^` is bitwise XOR.\n\n"
        "### Input\nOne line: `l r`.\n\n### Output\nThe XOR of every integer from `l` to `r` inclusive."
    ),
    constraints="0 ≤ l ≤ r ≤ 10^18",
    hints=[
        "A loop is up to 10¹⁸ steps. XOR is its own inverse — so, like a prefix sum, XOR(l..r) = XOR(0..r) ^ XOR(0..l−1).",
        "Write out f(n) = XOR(0..n) for n = 0 … 12 and look at it next to n mod 4.",
        "f(n) is n when n % 4 == 0, 1 when n % 4 == 1, n + 1 when n % 4 == 2, and 0 when n % 4 == 3. Take f(−1) = 0.",
    ],
    opt=("O(1)", "O(1)",
         "Two lookups in a period-4 pattern."),
    editorial=(
        "## The one thing this teaches\n**Prefix XOR works like a prefix sum**, because x ^ x = 0 "
        "cancels the shared part: XOR(l..r) = f(r) ^ f(l − 1) with f(n) = XOR(0..n).\n\n"
        "## Why f has period 4\nPair each even number 2k with 2k + 1: they differ only in the "
        "last bit, so 2k ^ (2k + 1) = 1. From 0, the pairs (0,1), (2,3), … each contribute a 1, "
        "and two 1s cancel. So:\n\n"
        "| n mod 4 | f(n) | why |\n| --- | --- | --- |\n"
        "| 0 | n | an even count of pairs, then n on its own |\n"
        "| 1 | 1 | an odd count of complete pairs |\n"
        "| 2 | n + 1 | 1 ^ n, and n is even so this sets the last bit |\n"
        "| 3 | 0 | an even count of complete pairs |\n\n"
        "```java\nstatic long f(long n) {\n    switch ((int) (n & 3)) {\n"
        "        case 0: return n;\n        case 1: return 1;\n        case 2: return n + 1;\n"
        "        default: return 0;\n    }\n}\n// answer: f(r) ^ (l == 0 ? 0 : f(l - 1))\n```\n\n"
        "## Check it by brute force\nA loop for r ≤ 1000 against the formula is five lines "
        "and catches an off-by-one in the table immediately."
    ),
    py='''
def solve(x, y):
    def f(n):
        if n < 0:
            return 0
        return (n, 1, n + 1, 0)[n % 4]
    return f(y) ^ f(x - 1)
''',
    java='''
    static long f(long n) {
        if (n < 0) return 0;
        switch ((int) (n & 3)) {
            case 0: return n;
            case 1: return 1;
            case 2: return n + 1;
            default: return 0;
        }
    }

    static long solve(long l, long r) { return f(r) ^ f(l - 1); }
''',
    examples=[
        ("Example 1", "3 6\n"),
        ("Example 2", "0 7\n"),
    ],
    hidden=[
        ("Zero", "0 0\n"),
        ("A single number", "123456789 123456789\n"),
        ("Starts at one", "1 10\n"),
        ("Each remainder", "4 9\n"),
        ("Wide", "1 1000000000000000000\n"),
        ("Near the top", "999999999999999990 1000000000000000000\n"),
        ("Odd to odd", "7 21\n"),
    ],
    expl=[
        "3 ^ 4 ^ 5 ^ 6 = 7 ^ 5 ^ 6 = 2 ^ 6 = 4.",
        "0…7 is four complete pairs, each XOR-ing to 1, and four 1s cancel: 0.",
    ],
    prereqs=[
        ("bit_manip", "x ^ x = 0 makes XOR(l..r) = XOR(0..r) ^ XOR(0..l−1)."),
        ("prefix_sum", "The same subtraction as a prefix sum, with XOR as the operation."),
    ],
)


_p(
    "set-bits-up-to-n", "Counting Every Set Bit", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "Counting", "Math"],
    companies=["Adobe", "Amazon"],
    shape="n", ret="long",
    todo="for each bit b, the numbers 0..n cycle in blocks of 2^(b+1): (n+1) / 2^(b+1) full blocks give 2^b ones each, plus max(0, (n+1) % 2^(b+1) - 2^b)",
    description=(
        "Write every number from `1` to `n` in binary. How many `1` digits did you write in "
        "total?\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThe total number of set bits over `1, 2, …, n`."
    ),
    constraints="1 ≤ n ≤ 10^15",
    hints=[
        "Calling bitCount for each number is 10¹⁵ calls. Count by **bit position** instead of by number.",
        "Bit b of the numbers 0, 1, 2, … reads 0 (2ᵇ times), 1 (2ᵇ times), 0, 1, … — a cycle of length 2^(b+1).",
        "Among 0…n there are (n + 1) / 2^(b+1) complete cycles, each with 2ᵇ ones, plus a partial cycle of r = (n + 1) % 2^(b+1) numbers contributing max(0, r − 2ᵇ).",
    ],
    opt=("O(log n)", "O(1)",
         "One closed-form count per bit position — about 50 of them."),
    editorial=(
        "## The one thing this teaches\n**Swap the order of counting.** “For each number, count "
        "its bits” is n × 50 work. “For each bit position, count the numbers that have it” is "
        "50 closed-form counts, because each bit position is a perfectly regular square wave.\n\n"
        "## Bit b as a wave\nOver 0, 1, 2, …, bit b is 0 for 2ᵇ numbers, then 1 for 2ᵇ numbers, "
        "repeating with period 2^(b+1).\n\n"
        "```java\nlong total = 0, m = n + 1;             // count over 0..n; 0 adds nothing\n"
        "for (int b = 0; (1L << b) <= n; b++) {\n    long cycle = 1L << (b + 1), half = 1L << b;\n"
        "    total += m / cycle * half;          // complete cycles\n"
        "    total += Math.max(0, m % cycle - half);   // the partial one\n}\n```\n\n"
        "## Check\nFor n = 5 (1, 10, 11, 100, 101): bit 0 → 6/2·1 + max(0, 0 − 1) = 3; bit 1 → "
        "6/4·2 + max(0, 2 − 2) = 2; bit 2 → 6/8·4 + max(0, 6 − 4) = 2. Total 7.\n\n"
        "## Related\n`count-bits` computes the per-number counts for every i ≤ n with a DP — "
        "O(n), which is right when you need all of them and wrong when you only need their sum."
    ),
    py='''
def solve(n):
    m = n + 1
    total = 0
    b = 0
    while (1 << b) <= n:
        cycle, half = 1 << (b + 1), 1 << b
        total += m // cycle * half + max(0, m % cycle - half)
        b += 1
    return total
''',
    java='''
    static long solve(long n) {
        long total = 0, m = n + 1;
        for (int b = 0; (1L << b) <= n; b++) {
            long cycle = 1L << (b + 1), half = 1L << b;
            total += m / cycle * half;
            total += Math.max(0, m % cycle - half);
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "5\n"),
        ("Example 2", "16\n"),
    ],
    hidden=[
        ("One", "1\n"),
        ("Two", "2\n"),
        ("One below a power of two", "1023\n"),
        ("A power of two", "1024\n"),
        ("Million", "1000000\n"),
        ("Large", "999999999999999\n"),
        ("Largest", "1000000000000000\n"),
    ],
    expl=[
        "1, 10, 11, 100, 101 have 1 + 1 + 2 + 1 + 2 = 7 ones.",
        "1…15 contribute 32 ones (each of the 4 low bits is set in 8 of 0…15), and 16 = 10000 adds one more: 33.",
    ],
    prereqs=[
        ("bit_manip", "Bit b of consecutive integers is a square wave of period 2^(b+1)."),
        ("arithmetic", "Count complete cycles with division and the partial one with the remainder."),
    ],
)


_p(
    "next-same-popcount", "Next Number, Same Bits", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "Gosper's Hack", "Combinations"],
    companies=["Google", "Microsoft"],
    shape="n", ret="long",
    todo="c = n & -n; r = n + c; answer = r | (((n ^ r) >> 2) / c)",
    description=(
        "Given `n`, find the smallest integer **greater** than `n` whose binary form has exactly as "
        "many `1` bits as `n` does.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\nThat integer."
    ),
    constraints="1 ≤ n ≤ 10^15",
    hints=[
        "Counting up from n + 1 can take a very long time: from 2⁴⁹, the next number with one set bit is 2⁵⁰.",
        "Find the lowest block of consecutive 1s. Its top 1 must move up one place — into the 0 just above the block — to make the number larger by as little as possible.",
        "The rest of that block (one fewer 1) moves all the way down to bit 0, to make the result as small as possible. In bit operations: c = n & −n, r = n + c, answer = r | (((n ^ r) >> 2) / c).",
    ],
    opt=("O(1)", "O(1)",
         "Five word operations (Gosper's hack)."),
    editorial=(
        "## The one thing this teaches\n**Adding the lowest set bit ripples a carry through the "
        "lowest block of 1s.** That one addition does most of the work of finding the next "
        "combination — which is why this is how subsets of a fixed size are enumerated in order.\n\n"
        "## Gosper's hack\n```java\nlong c = n & -n;            // lowest set bit\n"
        "long r = n + c;             // carry clears the lowest block, sets the bit above it\n"
        "long ones = (n ^ r) >> 2;   // the bits that changed, minus the two that stay accounted for\n"
        "ones /= c;                  // slide them down to bit 0\nreturn r | ones;\n```\n\n"
        "## Walk it on n = 0b1011100 (92)\n- c = 0b100 (4). The lowest block of 1s is bits 2–4.\n"
        "- r = 92 + 4 = 0b1100000 (96): the carry cleared bits 2–4 and set bit 5.\n"
        "- n ^ r = 0b0111100: the four bits that changed (bits 2–5).\n"
        "- >> 2 gives 0b1111; / 4 gives 0b11 — two 1s, which is the block's three minus the one "
        "that moved up.\n- r | 0b11 = 0b1100011 (99). Four 1s, like 92.\n\n"
        "## Why the smallest\nAny larger number with the same count must move some 1 up into a "
        "0. Moving the lowest movable 1 by one place changes the highest bit possible by the least, "
        "and packing the remaining low 1s at the bottom makes the tail as small as it can be."
    ),
    py='''
def solve(n):
    c = n & -n
    r = n + c
    return r | (((n ^ r) >> 2) // c)
''',
    java='''
    static long solve(long n) {
        long c = n & -n;
        long r = n + c;
        return r | (((n ^ r) >> 2) / c);
    }
''',
    examples=[
        ("Example 1", "92\n"),
        ("Example 2", "6\n"),
    ],
    hidden=[
        ("One", "1\n"),
        ("All ones", "7\n"),
        ("A power of two", "562949953421312\n"),
        ("Alternating", "682\n"),
        ("Low block at the bottom", "1000000000000000\n"),
        ("Large all ones", "562949953421311\n"),
        ("Two far-apart bits", "562949953421313\n"),
    ],
    expl=[
        "92 = 1011100 has four 1s. The next is 99 = 1100011.",
        "6 = 110. 7 = 111 has three 1s, 8 = 1000 has one, 9 = 1001 has two: the answer is 9.",
    ],
    prereqs=[
        ("bit_manip", "`n & -n` isolates the lowest set bit; adding it ripples a carry through a block of 1s."),
        ("arithmetic", "Division by a power of two is a right shift that slides bits down."),
    ],
)


_p(
    "budget-subsets", "Shopping Within Budget", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "Subset Enumeration", "Bitmask"],
    companies=["Amazon", "Uber"],
    shape="arr_k", ret="long",
    todo="sum[mask] = sum[mask & (mask - 1)] + price[lowest set bit of mask]; count masks with sum <= budget",
    description=(
        "A shop has `n` items with the given prices. How many **subsets** of the items — including "
        "buying nothing — cost at most the budget `B` in total?\n\n"
        "### Input\nLine 1: `n B`.\nLine 2: `n` prices.\n\n### Output\nThe number of affordable "
        "subsets."
    ),
    constraints="1 ≤ n ≤ 20\n1 ≤ price ≤ 10^9\n0 ≤ B ≤ 2 × 10^10",
    hints=[
        "n ≤ 20 means 2²⁰ ≈ 10⁶ subsets — few enough to try every one. A subset is a mask: bit i set means item i is bought.",
        "Summing each subset from scratch is 2ⁿ · n. Every mask differs from `mask & (mask − 1)` by exactly one item — its lowest set bit.",
        "So sum[mask] = sum[mask & (mask − 1)] + price[Long.numberOfTrailingZeros(mask)], and the smaller mask was computed earlier. Totals reach 2·10¹⁰: use long.",
    ],
    opt=("O(2ⁿ)", "O(2ⁿ)",
         "One addition per subset, each reusing a smaller subset's total."),
    editorial=(
        "## The one thing this teaches\n**Masks are ordered so that every mask's “smaller self” "
        "comes first.** `mask & (mask − 1)` removes the lowest set bit, giving a smaller number, "
        "so iterating masks upward means it is always ready. That turns 2ⁿ · n into 2ⁿ — the "
        "first step of every bitmask DP.\n\n"
        "## Approach\n```java\nlong[] sum = new long[1 << n];\nlong count = 1;                    // the empty subset: sum 0 ≤ B\n"
        "for (int mask = 1; mask < (1 << n); mask++) {\n"
        "    int low = Integer.numberOfTrailingZeros(mask);\n"
        "    sum[mask] = sum[mask & (mask - 1)] + price[low];\n"
        "    if (sum[mask] <= B) count++;\n}\n```\n\n"
        "## Beyond n = 20\nAt n = 40, 2⁴⁰ is too many. *Meet in the middle*: enumerate each half's "
        "2²⁰ sums, sort one side, and for each sum on the other side binary-search how many "
        "partners fit — O(2^(n/2) · n)."
    ),
    py='''
def solve(a, k):
    sums = [0]
    for p in a:
        sums += [s + p for s in sums]
    return sum(1 for s in sums if s <= k)
''',
    java='''
    static long solve(int[] a, long budget) {
        int n = a.length;
        long[] sum = new long[1 << n];
        long count = 1;
        for (int mask = 1; mask < (1 << n); mask++) {
            sum[mask] = sum[mask & (mask - 1)] + a[Integer.numberOfTrailingZeros(mask)];
            if (sum[mask] <= budget) count++;
        }
        return count;
    }
''',
    examples=[
        ("Example 1", "3 5\n2 3 4\n"),
        ("Example 2", "2 0\n1 1\n"),
    ],
    hidden=[
        ("Everything affordable", "4 100\n1 2 3 4\n"),
        ("Nothing but the empty set", "3 4\n5 6 7\n"),
        ("Equal prices", "10 5\n" + " ".join(["1"] * 10) + "\n"),
        ("Large prices", "5 3000000000\n1000000000 1000000000 1000000000 999999999 2\n"),
        ("Twenty items", "20 5000\n" + " ".join(str(v) for v in _lcg_ints(515, 20, 1, 1000)) + "\n"),
        ("Twenty large items", "20 5000000000\n" + " ".join(str(v) for v in _lcg_ints(516, 20, 1, 1000000000)) + "\n"),
    ],
    expl=[
        "{}, {2}, {3}, {4} and {2, 3} cost at most 5 — five subsets. {2, 4} costs 6.",
        "Only the empty subset costs 0.",
    ],
    prereqs=[
        ("bit_manip", "A mask is a subset; `mask & (mask − 1)` drops its lowest element."),
        ("dp", "Each subset's total is built from one smaller, already-computed subset."),
    ],
)


_p(
    "missing-and-duplicate", "The Swapped Tag", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "XOR", "Partitioning"],
    companies=["Amazon", "Microsoft"],
    shape="arr", ret="String",
    todo="x = XOR of all values and of 1..n = dup ^ missing; split everything by the lowest set bit of x into two XOR buckets; the value found in the array is the duplicate",
    description=(
        "The `n` boxes in a warehouse should carry the tags `1, 2, …, n`, once each. One tag was "
        "misprinted: it duplicates another tag, so one number is missing. Find both.\n\n"
        "Use O(1) extra space.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: the `n` tags, in any order.\n\n### Output\nOne line: "
        "the duplicated number, then the missing number."
    ),
    constraints="2 ≤ n ≤ 100000\nExactly one value appears twice and exactly one of 1…n is missing.",
    hints=[
        "XOR every tag and every number 1…n together. Everything present once in each list cancels, leaving x = dup ^ missing — which is not 0, because they differ.",
        "Pick any bit where dup and missing differ, for example the lowest set bit of x. Split every tag and every number 1…n into two groups by that bit.",
        "Each group XORs down to one of the two answers. Whichever of the two actually appears among the tags is the duplicate.",
    ],
    opt=("O(n)", "O(1)",
         "Three passes, and two XOR accumulators."),
    editorial=(
        "## The one thing this teaches\n**When XOR leaves two unknowns mixed together, split by a "
        "bit where they differ.** x = dup ^ missing has a 1 exactly where the two differ, so "
        "any set bit of x separates them into different groups — and within each group, "
        "everything else still cancels in pairs.\n\n"
        "## Approach\n```java\nint x = 0;\nfor (int i = 0; i < n; i++) x ^= a[i] ^ (i + 1);   // = dup ^ missing\n"
        "int bit = x & -x;\nint p = 0, q = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    if ((a[i] & bit) != 0) p ^= a[i]; else q ^= a[i];\n"
        "    if (((i + 1) & bit) != 0) p ^= i + 1; else q ^= i + 1;\n}\n"
        "// p and q are {dup, missing} in some order\nfor (int v : a) if (v == p) return p + \" \" + q;\n"
        "return q + \" \" + p;\n```\n\n"
        "## Why the groups work\nInside one group, every number other than dup and missing "
        "appears exactly twice (once in 1…n, once among the tags). dup appears three times "
        "(twice as a tag, once in 1…n) and missing once — odd counts, so each survives in its "
        "own group.\n\n"
        "## The alternatives\nA boolean array is O(n) space. The sum and sum-of-squares system "
        "also works in O(1) space but needs care with overflow — the XOR version has none. "
        "Marking by negating `a[|v| − 1]` is O(1) space too, but mutates the input."
    ),
    py='''
def solve(a):
    n = len(a)
    x = 0
    for i, v in enumerate(a, 1):
        x ^= v ^ i
    bit = x & -x
    p = q = 0
    for i, v in enumerate(a, 1):
        if v & bit:
            p ^= v
        else:
            q ^= v
        if i & bit:
            p ^= i
        else:
            q ^= i
    return f"{p} {q}" if p in a else f"{q} {p}"
''',
    java='''
    static String solve(int[] a) {
        int n = a.length, x = 0;
        for (int i = 0; i < n; i++) x ^= a[i] ^ (i + 1);
        int bit = x & -x, p = 0, q = 0;
        for (int i = 0; i < n; i++) {
            if ((a[i] & bit) != 0) p ^= a[i]; else q ^= a[i];
            if (((i + 1) & bit) != 0) p ^= i + 1; else q ^= i + 1;
        }
        for (int v : a) if (v == p) return p + " " + q;
        return q + " " + p;
    }
''',
    examples=[
        ("Example 1", "6\n4 1 6 2 4 5\n"),
        ("Example 2", "2\n2 2\n"),
    ],
    hidden=[
        ("Two boxes, other way", "2\n1 1\n"),
        ("Adjacent values", "5\n1 2 3 3 5\n"),
        ("Missing the last", "4\n1 2 3 3\n"),
        ("Missing the first", "5\n2 3 4 5 5\n"),
        ("Far apart", "8\n8 7 6 5 4 3 2 8\n"),
        ("Large shuffled", "100000\n" + " ".join(str(v) for v in
            (lambda n: (lambda perm: [perm[i] if perm[i] != 31337 else 77777 for i in range(n)])(
                sorted(range(1, n + 1), key=lambda v: (v * 7919) % 100003)))(100000)) + "\n"),
    ],
    expl=[
        "4 appears twice and 3 is missing.",
        "Two boxes, both tagged 2: tag 1 is missing.",
    ],
    prereqs=[
        ("bit_manip", "XOR cancels pairs; a set bit of dup ^ missing separates the two."),
        ("array_patterns", "Read the array without modifying it, in O(1) extra space."),
    ],
)


_p(
    "pair-xor-total", "Total of All Pair XORs", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "XOR", "Contribution Technique"],
    companies=["Google", "Amazon"],
    shape="arr", ret="long",
    todo="for each bit b, ones = how many values have it; it is set in ones * (n - ones) pair XORs, each worth 2^b",
    description=(
        "For every pair of positions `i < j`, compute `a[i] ^ a[j]`. Report the sum of all of "
        "these values.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe sum over all pairs."
    ),
    constraints="1 ≤ n ≤ 100000\n0 ≤ a[i] < 2^30",
    hints=[
        "There are up to 5 × 10⁹ pairs — too many to visit. Break each XOR into its bits instead.",
        "Bit b of a[i] ^ a[j] is 1 exactly when one of the two has bit b and the other does not.",
        "If `ones` values have bit b set, then ones · (n − ones) pairs have it set in their XOR, each contributing 2ᵇ. Sum that over the 30 bits. The total can reach 5 × 10¹⁸ — it fits a long, just.",
    ],
    opt=("O(n · 30)", "O(1)",
         "One count per bit position; no pair is ever formed."),
    editorial=(
        "## The one thing this teaches\n**The contribution technique.** Instead of asking “what "
        "does each pair contribute?”, ask “in how many pairs does each *bit* contribute?”. The "
        "bits of a XOR are independent, so the double loop collapses to 30 counts.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int b = 0; b < 30; b++) {\n"
        "    long ones = 0;\n    for (int v : a) ones += (v >> b) & 1;\n"
        "    total += ones * (n - ones) * (1L << b);\n}\n```\n\n"
        "## Why ones · (n − ones)\nBit b is set in a[i] ^ a[j] when exactly one of the two has "
        "it: pick one of the `ones` values and one of the n − ones others.\n\n"
        "## Overflow check\nones · (n − ones) ≤ (n/2)² = 2.5 × 10⁹, times 2²⁹, summed over bits: "
        "the whole total is below 5 × 10⁹ · 2³⁰ ≈ 5.4 × 10¹⁸ < 2⁶³ ≈ 9.2 × 10¹⁸. The factors are "
        "`long` before they multiply.\n\n"
        "## The same idea elsewhere\nSum of pair ANDs (both have the bit: C(ones, 2)), sum of pair "
        "ORs (all pairs minus those where neither has it), and Hamming distances summed over all "
        "pairs — which is this problem with every 2ᵇ replaced by 1."
    ),
    py='''
def solve(a):
    n = len(a)
    total = 0
    for b in range(30):
        ones = sum((v >> b) & 1 for v in a)
        total += ones * (n - ones) << b
    return total
''',
    java='''
    static long solve(int[] a) {
        long n = a.length, total = 0;
        for (int b = 0; b < 30; b++) {
            long ones = 0;
            for (int v : a) ones += (v >> b) & 1;
            total += ones * (n - ones) * (1L << b);
        }
        return total;
    }
''',
    examples=[
        ("Example 1", "3\n1 2 3\n"),
        ("Example 2", "4\n5 5 5 5\n"),
    ],
    hidden=[
        ("One value", "1\n7\n"),
        ("Zero and max", "2\n0 1073741823\n"),
        ("Powers of two", "5\n1 2 4 8 16\n"),
        ("Half zeros, half max", "100000\n" + " ".join(["0", "1073741823"] * 50000) + "\n"),
        ("Random", "1000\n" + " ".join(str(v) for v in _lcg_ints(3030, 1000, 0, 1073741823)) + "\n"),
    ],
    expl=[
        "1^2 = 3, 1^3 = 2, 2^3 = 1: the total is 6.",
        "Equal values XOR to 0.",
    ],
    prereqs=[
        ("bit_manip", "Bit b of a XOR is set when exactly one operand has bit b."),
        ("overflow", "The total approaches 5.4 × 10¹⁸ — multiply in long."),
    ],
)


_p(
    "max-and-pair", "Strongest AND Pair", "Medium",
    topics=["Bit Manipulation"], subtopics=["Bit Manipulation", "Greedy", "Bitwise AND"],
    companies=["Google", "Uber"],
    shape="arr", ret="long",
    todo="from bit 29 down, try res | (1 << b): if at least two values contain every bit of that candidate, keep it",
    description=(
        "Choose two different positions `i ≠ j`. Report the largest possible value of "
        "`a[i] & a[j]`.\n\n"
        "### Input\nLine 1: `n`.\nLine 2: `n` integers.\n\n### Output\nThe maximum pair AND."
    ),
    constraints="2 ≤ n ≤ 100000\n0 ≤ a[i] < 2^30",
    hints=[
        "All pairs is 5 × 10⁹. But a high bit is worth more than all lower bits combined — so decide the answer's bits from the top.",
        "Can the answer have bit 29? Only if at least two numbers have bit 29. If so, bit 29 is in the answer, whatever else happens.",
        "Keep a candidate `res`. For each bit b from high to low, test `res | (1 << b)`: if at least two numbers contain *all* of its bits, keep it. Each test is one pass: O(30 · n).",
    ],
    opt=("O(30 · n)", "O(1)",
         "One counting pass per bit, deciding the answer greedily from the top."),
    editorial=(
        "## The one thing this teaches\n**Greedy bit by bit, from the top.** 2ᵇ is larger than "
        "2ᵇ⁻¹ + … + 1, so securing a higher bit is always worth giving up every lower one. That "
        "turns “maximise over pairs” into 30 yes/no questions.\n\n"
        "## Approach\n```java\nint res = 0;\nfor (int b = 29; b >= 0; b--) {\n"
        "    int cand = res | (1 << b), count = 0;\n"
        "    for (int v : a) if ((v & cand) == cand) count++;\n"
        "    if (count >= 2) res = cand;\n}\n```\n\n"
        "## Why test the whole candidate, not just bit b\nTwo numbers with bit b set are useless "
        "if they do not also share the higher bits already chosen. `(v & cand) == cand` asks "
        "for all of them at once.\n\n"
        "## The same shape elsewhere\nMaximum XOR of a pair is also decided from the top bit, but "
        "the check (“is there a partner with the opposite bit?”) needs a hash set of prefixes or "
        "a binary trie — see the tries unit."
    ),
    py='''
def solve(a):
    res = 0
    for b in range(29, -1, -1):
        cand = res | (1 << b)
        if sum(1 for v in a if v & cand == cand) >= 2:
            res = cand
    return res
''',
    java='''
    static long solve(int[] a) {
        int res = 0;
        for (int b = 29; b >= 0; b--) {
            int cand = res | (1 << b), count = 0;
            for (int v : a) if ((v & cand) == cand) count++;
            if (count >= 2) res = cand;
        }
        return res;
    }
''',
    examples=[
        ("Example 1", "4\n12 10 7 5\n"),
        ("Example 2", "3\n1 2 4\n"),
    ],
    hidden=[
        ("Two values", "2\n1073741823 1073741823\n"),
        ("Zeros", "3\n0 0 0\n"),
        ("High bit shared by exactly two", "4\n536870912 536870913 3 3\n"),
        ("Only low bits shared", "4\n8 4 3 3\n"),
        ("Large random", "2000\n" + " ".join(str(v) for v in _lcg_ints(6060, 2000, 0, 1073741823)) + "\n"),
        ("Duplicates of the largest", "5\n100 200 300 300 50\n"),
    ],
    expl=[
        "12 & 10 = 8 is the best: 1100 and 1010 share bit 3. 7 & 5 = 5 is smaller.",
        "No two of 1, 2, 4 share a bit.",
    ],
    prereqs=[
        ("bit_manip", "A higher bit outweighs all lower bits together."),
        ("greedy", "Decide the answer's bits from the top, each decision final."),
    ],
)
