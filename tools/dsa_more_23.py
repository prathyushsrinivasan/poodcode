# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 23 — bits, recursion, binary search trees and a queue.
#
#   hamming-distance              XOR marks the differing bits; count them
#   bitwise-and-of-range          the answer is the common binary prefix of the two ends
#   single-number-ii              count each bit position modulo 3
#   max-product-word-lengths      a 26-bit mask per word makes "no shared letter" one AND
#   permutation-sequence          the factorial number system picks each digit directly
#   predict-the-winner            minimax as a score difference over an interval
#   verify-preorder-bst           a stack of open ancestors and a rising lower bound
#   unique-bst-count              choose the root; the two sides multiply (Catalan numbers)
#   largest-bst-subtree           post-order returns (is BST, min, max, size)
#   first-negative-in-window      a queue holding only the negatives still in the window
# ===========================================================================

_p(
    "hamming-distance", "Hamming Distance", "Easy",
    topics=["Bit Manipulation"], subtopics=["XOR", "Popcount"], companies=["Meta", "Adobe"],
    shape="two", ret="int", todo="x ^ y has a 1 exactly where the bits differ; count the 1 bits",
    description=(
        "The **Hamming distance** between two integers is the number of bit positions where "
        "their binary representations differ. Print it.\n\n"
        "### Input\nOne line: `x y`.\n\n"
        "### Output\nThe Hamming distance."
    ),
    constraints="0 ≤ x, y ≤ 2^31 − 1",
    hints=[
        "Compare the numbers bit by bit: shift both right 31 times, checking the lowest bits.",
        "XOR produces a 1 exactly in the positions where the two bits differ.",
        "Count the 1 bits of x ^ y. The trick v &= v − 1 clears the lowest 1 bit, so the loop runs once per 1.",
    ],
    opt=("O(1)", "O(1)", "At most 31 iterations — one per set bit with v &= v − 1."),
    editorial=(
        "## The one thing this teaches\n**XOR is \"where do these differ\".** Any question "
        "comparing two bit patterns position by position starts with `x ^ y`; what remains is "
        "counting.\n\n"
        "## Approach\n```java\nlong v = x ^ y;\nint count = 0;\nwhile (v != 0) {\n"
        "    v &= v - 1;      // clear the lowest set bit\n    count++;\n}\nreturn count;\n```\n\n"
        "## Why v & (v − 1) clears one bit\nSubtracting 1 turns the lowest 1 into 0 and every 0 "
        "below it into 1. AND-ing with the original keeps everything above that bit and zeroes "
        "the rest: `1011000 & 1010111 = 1010000`.\n\n"
        "## In practice\n`Long.bitCount(x ^ y)` does the same, usually with a single CPU "
        "instruction."
    ),
    py='''
def solve(x, y):
    return bin(x ^ y).count("1")
''',
    java='''
    static int solve(long x, long y) {
        long v = x ^ y;
        int count = 0;
        while (v != 0) {
            v &= v - 1;
            count++;
        }
        return count;
    }
''',
    examples=[("Example 1", "1 4\n"), ("Example 2", "3 1\n")],
    hidden=[
        ("Both zero", "0 0\n"),
        ("Every bit differs", "2147483647 0\n"),
        ("Equal numbers", "5 5\n"),
        ("One high bit", "0 1073741824\n"),
    ],
    expl=[
        "001 and 100 differ in two positions.",
        "11 and 01 differ only in the second bit.",
    ],
    prereqs=[
        ("bit_manip", "XOR, and clearing the lowest set bit with v & (v − 1)."),
        ("iteration", "A loop that runs once per set bit."),
    ],
)

_p(
    "bitwise-and-of-range", "Bitwise AND of a Range", "Medium",
    topics=["Bit Manipulation"], subtopics=["Common Prefix"], companies=["Amazon", "Microsoft"],
    shape="two", ret="long", todo="shift both ends right until they are equal, then shift back — only the common prefix survives",
    description=(
        "Print the bitwise AND of every integer from `left` to `right`, inclusive.\n\n"
        "### Input\nOne line: `left right`.\n\n"
        "### Output\nThe AND of the range."
    ),
    constraints="0 ≤ left ≤ right ≤ 2^31 − 1",
    hints=[
        "Looping over the range takes up to two billion steps.",
        "Counting from left to right, any bit below the highest position where left and right differ must flip at some point — so it becomes 0 in the AND.",
        "The answer is the common binary prefix of left and right, followed by zeros. Shift both right until they are equal, counting the shifts, then shift back.",
    ],
    opt=("O(log right)", "O(1)", "At most 31 shifts."),
    editorial=(
        "## The one thing this teaches\n**Reason about which bits survive, not about the numbers.** "
        "A bit is 1 in the AND only if it is 1 in *every* number of the range. Counting upward "
        "flips low bits constantly; only a prefix shared by both ends is untouched.\n\n"
        "## Approach\n```java\nint shifts = 0;\nwhile (left != right) {\n"
        "    left >>= 1;\n    right >>= 1;\n    shifts++;\n}\nreturn left << shifts;\n```\n\n"
        "## Why the differing bit forces zeros below it\nLet bit `b` be the highest position "
        "where `left` and `right` differ: `left` has 0 there, `right` has 1. Somewhere in between "
        "lies the number with the common prefix, then 1, then all zeros — so every bit below "
        "`b` is 0 in at least one number, and bit `b` itself is 0 in `left`.\n\n"
        "## Walkthrough: 5 to 7\n`101`, `111` → `10`, `11` → `1`, `1`: equal after 2 shifts. "
        "`1 << 2 = 100` = 4."
    ),
    py='''
def solve(x, y):
    result = 0
    for b in range(31):
        if (x >> b) & 1 and (x | ((1 << b) - 1)) >= y:
            result |= 1 << b
    return result
''',
    java='''
    static long solve(long left, long right) {
        int shifts = 0;
        while (left != right) {
            left >>= 1;
            right >>= 1;
            shifts++;
        }
        return left << shifts;
    }
''',
    examples=[("Example 1", "5 7\n"), ("Example 2", "0 0\n"), ("Example 3", "1 2147483647\n")],
    hidden=[
        ("Aligned block", "12 15\n"),
        ("Single number", "8 8\n"),
        ("Top of the range", "2147483646 2147483647\n"),
        ("Adjacent numbers", "6 7\n"),
        ("High bit shared", "1073741824 2147483647\n"),
    ],
    expl=[
        "101 & 110 & 111 = 100.",
        "The range holds only 0.",
        "The range crosses every power of two, so every bit is 0 somewhere.",
    ],
    prereqs=[
        ("bit_manip", "Shifts, and the binary structure of consecutive integers."),
        ("math_digits", "Common prefixes of two numbers written in base 2."),
    ],
)

_p(
    "single-number-ii", "Single Number II", "Medium",
    topics=["Bit Manipulation", "Arrays"], subtopics=["Bit Counting"], companies=["Google", "Amazon"],
    shape="arr", ret="int", todo="for each of the 32 bit positions, count the 1s across all numbers; count % 3 is the single number's bit",
    description=(
        "Every value appears **exactly three times** except one, which appears once. Find it "
        "using O(1) extra space.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe value that appears once."
    ),
    constraints="1 ≤ n ≤ 3·10^4, n ≡ 1 (mod 3)\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "XOR cancels pairs, not triples — Single Number's trick does not apply directly.",
        "Look at one bit position. The triples contribute a multiple of 3 ones there.",
        "So (number of 1s at bit b) % 3 is bit b of the answer. Do this for all 32 bits; in Java, setting bit 31 makes the int negative, as it should.",
    ],
    opt=("O(32 · n)", "O(1)", "32 counting passes, or one pass with 32 counters."),
    editorial=(
        "## The one thing this teaches\n**Cancel per bit, modulo the repetition count.** XOR is "
        "addition modulo 2 on each bit, which is why it cancels pairs. For triples, add each bit "
        "column modulo 3 instead.\n\n"
        "## Approach\n```java\nint result = 0;\nfor (int b = 0; b < 32; b++) {\n    int ones = 0;\n"
        "    for (int x : a) ones += (x >> b) & 1;\n"
        "    if (ones % 3 != 0) result |= 1 << b;\n}\nreturn result;\n```\n\n"
        "## Negative numbers\nIn two's complement a negative number has bit 31 set. Counting "
        "that bit like any other and setting `1 << 31` rebuilds the negative value exactly — the "
        "sign needs no special handling.\n\n"
        "## The generalisation\nIf every value appears `k` times except one, use `% k`. The "
        "same column-sum idea also underlies the constant-time two-variable state machine "
        "(`ones`, `twos`) often shown for this problem."
    ),
    py='''
def solve(a):
    return next(v for v, c in Counter(a).items() if c == 1)
''',
    java='''
    static int solve(int[] a) {
        int result = 0;
        for (int b = 0; b < 32; b++) {
            int ones = 0;
            for (int x : a) ones += (x >> b) & 1;
            if (ones % 3 != 0) result |= 1 << b;
        }
        return result;
    }
''',
    examples=[("Example 1", "4\n2 2 3 2\n"), ("Example 2", "7\n0 1 0 1 0 1 99\n")],
    hidden=[
        ("Only element, negative", "1\n-4\n"),
        ("Negative single", "4\n-2 -2 -2 -7\n"),
        ("Extremes", "7\n2147483647 5 2147483647 5 2147483647 5 -2147483648\n"),
        ("Zero is the single", "4\n9 0 9 9\n"),
    ],
    expl=[
        "2 appears three times; 3 once.",
        "0 and 1 each appear three times; 99 once.",
    ],
    prereqs=[
        ("bit_manip", "Extracting a bit with (x >> b) & 1 and setting one with |= 1 << b."),
        ("modulo", "Cancelling triples by summing each bit column modulo 3."),
    ],
)

_p(
    "max-product-word-lengths", "Maximum Product of Word Lengths", "Medium",
    topics=["Bit Manipulation", "Strings"], subtopics=["Bitmask"], companies=["Google"],
    shape="words", ret="long", todo="build a 26-bit letter mask per word; pairs with (mask[i] & mask[j]) == 0 share no letter",
    description=(
        "Print the largest value of `length(a) × length(b)` over pairs of words from the list "
        "that share **no common letter**, or `0` if no such pair exists.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` words.\n\n"
        "### Output\nThe maximum product."
    ),
    constraints="2 ≤ n ≤ 1000\n1 ≤ word length ≤ 1000\nLowercase English letters",
    hints=[
        "Comparing two words letter by letter costs O(L) per pair.",
        "There are only 26 letters. A word's letter set fits in the bits of one int.",
        "Two words share no letter exactly when their masks AND to 0 — an O(1) test. Try all pairs.",
    ],
    opt=("O(n² + total length)", "O(n)", "Masks in one pass over the letters, then O(1) per pair."),
    editorial=(
        "## The one thing this teaches\n**A small set is an integer.** A subset of 26 letters is "
        "a 26-bit number; union is `|`, intersection is `&`, and \"disjoint\" is `== 0`. The "
        "per-pair cost drops from O(L) to one machine instruction.\n\n"
        "## Approach\n```java\nint[] mask = new int[n];\nfor (int i = 0; i < n; i++)\n"
        "    for (char ch : words[i].toCharArray()) mask[i] |= 1 << (ch - 'a');\n"
        "long best = 0;\nfor (int i = 0; i < n; i++)\n    for (int j = i + 1; j < n; j++)\n"
        "        if ((mask[i] & mask[j]) == 0)\n"
        "            best = Math.max(best, (long) words[i].length() * words[j].length());\n```\n\n"
        "## Masks forget counts\n`foo` and `fo` have the same mask. That is exactly right here — "
        "sharing letters is about which letters, not how many — but it means a mask cannot "
        "answer questions like \"is this an anagram\".\n\n"
        "## A small speedup\nWords with the same mask can keep only the longest: at most 2^26 "
        "masks, and in practice far fewer than n."
    ),
    py='''
def solve(words):
    sets = [set(w) for w in words]
    best = 0
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            if not (sets[i] & sets[j]):
                best = max(best, len(words[i]) * len(words[j]))
    return best
''',
    java='''
    static long solve(String[] words) {
        int n = words.length;
        int[] mask = new int[n];
        for (int i = 0; i < n; i++)
            for (char ch : words[i].toCharArray()) mask[i] |= 1 << (ch - 'a');
        long best = 0;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if ((mask[i] & mask[j]) == 0)
                    best = Math.max(best, (long) words[i].length() * words[j].length());
        return best;
    }
''',
    examples=[
        ("Example 1", "6\nabcw baz foo bar xtfn abcdef\n"),
        ("Example 2", "7\na ab abc d cd bcd abcd\n"),
        ("Example 3", "4\na aa aaa aaaa\n"),
    ],
    hidden=[
        ("Two disjoint words", "2\nab cd\n"),
        ("Duplicate words", "3\nabc abc def\n"),
        ("Repeated letters", "3\nzzzz yy zy\n"),
        ("Every letter used", "2\nabcdefghijklm nopqrstuvwxyz\n"),
    ],
    expl=[
        "abcw and xtfn share no letter: 4 × 4 = 16.",
        "ab and cd: 2 × 2 = 4 (abc and d give only 3).",
        "Every word contains a.",
    ],
    prereqs=[
        ("bit_manip", "A set of letters stored as bits, tested with &."),
        ("overflow", "Two lengths of 1000 multiply safely, but the habit of a long product is worth keeping."),
    ],
)

_p(
    "permutation-sequence", "Permutation Sequence", "Hard",
    topics=["Math", "Recursion"], subtopics=["Factorial Number System"], companies=["Google", "Twitter"],
    shape="two", ret="String", todo="with k − 1 zero-indexed, each position's digit index is k / (remaining − 1)!; remove that digit and keep the remainder",
    description=(
        "List the permutations of `1, 2, …, n` in lexicographic order. Print the `k`-th one "
        "(1-indexed) as a string of digits.\n\n"
        "### Input\nOne line: `n k`.\n\n"
        "### Output\nThe k-th permutation."
    ),
    constraints="1 ≤ n ≤ 9\n1 ≤ k ≤ n!",
    hints=[
        "Generating permutations one by one takes up to 9! = 362880 steps, each O(n). There is a direct route.",
        "The permutations starting with 1 are the first (n − 1)!; those starting with 2 are the next (n − 1)!; and so on.",
        "Use k − 1. The first digit is the (k − 1) / (n − 1)!-th smallest remaining number; continue with k − 1 modulo (n − 1)! for the next position.",
    ],
    opt=("O(n²)", "O(n)", "n positions, each removing one digit from a list of up to n."),
    editorial=(
        "## The one thing this teaches\n**Skip whole blocks of a recursion without entering them.** "
        "Generating permutations recursively fixes the first digit and recurses on the rest. "
        "Each first digit owns a block of exactly `(n − 1)!` permutations, so division tells you "
        "which block holds the k-th — recursion by arithmetic.\n\n"
        "## Approach\n```java\nList<Integer> digits = [1..n];\nint[] fact = factorials 0!..(n−1)!;\n"
        "k--;                                     // zero-indexed\nStringBuilder sb = new StringBuilder();\n"
        "for (int i = n; i >= 1; i--) {\n    int block = fact[i - 1];\n"
        "    sb.append(digits.remove(k / block));  // the (k / block)-th remaining digit\n    k %= block;\n}\n```\n\n"
        "## Walkthrough: n = 4, k = 9\nk − 1 = 8. Blocks of 3! = 6: index 1 → digit `2`, k = 2. "
        "Blocks of 2! = 2 over `1 3 4`: index 1 → `3`, k = 0. Blocks of 1 over `1 4`: index 0 → "
        "`1`. Then `4`. Answer `2314`.\n\n"
        "## Why k − 1\nWith zero-indexing, the digit indices are exactly the digits of k − 1 in "
        "the factorial number system. One-indexed k would put the last permutation of each block "
        "into the next block."
    ),
    py='''
def solve(x, y):
    from itertools import islice, permutations
    return "".join(map(str, next(islice(permutations(range(1, x + 1)), y - 1, None))))
''',
    java='''
    static String solve(long nn, long kk) {
        int n = (int) nn, k = (int) kk - 1;
        List<Integer> digits = new ArrayList<>();
        for (int i = 1; i <= n; i++) digits.add(i);
        int[] fact = new int[n + 1];
        fact[0] = 1;
        for (int i = 1; i <= n; i++) fact[i] = fact[i - 1] * i;
        StringBuilder sb = new StringBuilder();
        for (int i = n; i >= 1; i--) {
            int block = fact[i - 1];
            sb.append(digits.remove(k / block));
            k %= block;
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "3 3\n"), ("Example 2", "4 9\n"), ("Example 3", "3 1\n")],
    hidden=[
        ("One digit", "1 1\n"),
        ("Last of nine", "9 362880\n"),
        ("First of nine", "9 1\n"),
        ("Middle block", "5 60\n"),
    ],
    expl=[
        "123, 132, 213: the third is 213.",
        "Six permutations start with 1. Those starting with 2 begin 2134, 2143, 2314 — so the 9th overall is 2314.",
        "The first permutation is the sorted order.",
    ],
    prereqs=[
        ("recursion", "Fixing one position and recursing on the rest — here skipped by counting."),
        ("math_digits", "Digits in the factorial number system, via division and remainder."),
    ],
)

_p(
    "predict-the-winner", "Predict the Winner", "Medium",
    topics=["Recursion", "Dynamic Programming"], subtopics=["Minimax", "Interval DP"], companies=["Google", "Amazon"],
    shape="arr", ret="String", todo="best(i, j) = the most the player to move can finish ahead on a[i..j]: max(a[i] − best(i+1, j), a[j] − best(i, j−1))",
    description=(
        "Two players take turns removing a number from **either end** of the array, adding it to "
        "their score. Player 1 moves first, and both play optimally. Print `YES` if player 1's "
        "final score is **at least** player 2's, otherwise `NO`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 20\n0 ≤ a[i] ≤ 10^7",
    hints=[
        "Greedily taking the larger end loses: in 1 5 233 7, taking 7 hands 233 to the opponent.",
        "Track one number instead of two scores: how far ahead the player to move can finish.",
        "diff(i, j) = max(a[i] − diff(i + 1, j), a[j] − diff(i, j − 1)) — after your pick, the opponent is the player to move. Player 1 wins when diff(0, n − 1) ≥ 0.",
    ],
    opt=("O(n²)", "O(n)", "One value per interval, filled by length with a rolling row."),
    editorial=(
        "## The one thing this teaches\n**In a zero-sum game, one number per state is enough.** "
        "Tracking both scores doubles the state. The *difference* from the mover's point of view "
        "captures it, and the opponent's best is simply subtracted — minimax without the two "
        "separate maximise/minimise branches.\n\n"
        "## Approach\n```java\nlong[] diff = a copy of a;   // diff[i] for the interval [i, j], length 1 initially\n"
        "for (int len = 2; len <= n; len++)\n    for (int i = 0; i + len - 1 < n; i++) {\n"
        "        int j = i + len - 1;\n"
        "        diff[i] = Math.max(a[i] - diff[i + 1], a[j] - diff[i]);   // diff[i+1] is [i+1, j], diff[i] is [i, j−1]\n    }\n"
        "return diff[0] >= 0;\n```\n\n"
        "## The recursion first\nWithout the table the same recurrence is exponential — every "
        "interval is reached along many move orders. Memoising on `(i, j)` gives O(n²) states, "
        "and the table above is that memo filled in order.\n\n"
        "## Walkthrough: 1 5 233 7\nPlayer 1 takes 1. Whichever end player 2 takes, 233 becomes "
        "available: 1 + 233 = 234 against 5 + 7 = 12."
    ),
    py='''
def solve(a):
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def best_score(i, j):
        # the most the player to move can collect from a[i..j]
        if i > j:
            return 0
        total = sum(a[i:j + 1])
        return max(total - best_score(i + 1, j), total - best_score(i, j - 1))

    first = best_score(0, len(a) - 1)
    return "YES" if 2 * first >= sum(a) else "NO"
''',
    java='''
    static String solve(int[] a) {
        int n = a.length;
        long[] diff = new long[n];
        for (int i = 0; i < n; i++) diff[i] = a[i];
        for (int len = 2; len <= n; len++)
            for (int i = 0; i + len - 1 < n; i++) {
                int j = i + len - 1;
                diff[i] = Math.max(a[i] - diff[i + 1], a[j] - diff[i]);
            }
        return diff[0] >= 0 ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "3\n1 5 2\n"), ("Example 2", "4\n1 5 233 7\n")],
    hidden=[
        ("Single number", "1\n0\n"),
        ("Tie goes to player 1", "2\n3 3\n"),
        ("Big prize in the middle", "5\n2 4 55 6 8\n"),
        ("Odd length, one big value", "7\n1 1 1 1 100 1 1\n"),
        ("Player 1 wins by one","5\n10 1 1 10 1\n"),
    ],
    expl=[
        "Player 1 takes 1 or 2, and player 2 takes 5 either way: at best 3 against 5.",
        "Player 1 takes 1, then 233 after player 2's move: 234 against 12.",
    ],
    prereqs=[
        ("recursion", "Minimax: your best is the value of your move minus the opponent's best reply."),
        ("dp2d", "Memoising on the interval (i, j), filled by increasing length."),
    ],
)

_p(
    "verify-preorder-bst", "Verify Preorder Sequence of a BST", "Medium",
    topics=["Trees", "Stacks"], subtopics=["BST", "Monotonic Stack"], companies=["Google", "Zenefits"],
    shape="arr", ret="String", todo="keep a stack of ancestors and a lower bound; popping smaller ancestors raises the bound, and a value below it is invalid",
    description=(
        "Given distinct values, print `YES` if they could be the **preorder** traversal of some "
        "binary search tree, otherwise `NO`.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` distinct integers.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 10^4\n1 ≤ value ≤ 10^9",
    hints=[
        "Preorder: node, then its left subtree (smaller values), then its right subtree (larger).",
        "Once the sequence moves into some node's right subtree, no later value may be smaller than that node.",
        "Walk the values with a stack of ancestors. A value larger than the top means you went right: pop every smaller ancestor, and the last popped becomes a lower bound for everything after.",
    ],
    opt=("O(n)", "O(n)", "Each value is pushed and popped at most once."),
    editorial=(
        "## The one thing this teaches\n**A monotonic stack can replay a traversal.** The stack "
        "holds the path of ancestors whose right subtrees have not started. A larger value closes "
        "those subtrees by popping them — and the closed nodes set a floor that nothing later "
        "may go under.\n\n"
        "## Approach\n```java\nDeque<Integer> stack = new ArrayDeque<>();\nlong low = Long.MIN_VALUE;\n"
        "for (int x : a) {\n    if (x < low) return false;                      // below a node we already passed on the right\n"
        "    while (!stack.isEmpty() && stack.peek() < x) low = stack.pop();\n"
        "    stack.push(x);\n}\nreturn true;\n```\n\n"
        "## Walkthrough: 5 2 6 1 3\nPush 5, push 2. The 6 pops 2 and 5: low = 5. The 1 is below "
        "5 — but it came after the right turn at 5, so it cannot be in the tree. `NO`.\n\n"
        "## The O(n) space question\nThe stack can be simulated inside the input array itself, "
        "reusing a prefix as the stack — O(1) extra space if modifying the input is allowed."
    ),
    py='''
def solve(a):
    val, left, right = [], {}, {}
    for i, x in enumerate(a):
        val.append(x)
        if i == 0:
            continue
        cur = 0
        while True:
            side = left if x < val[cur] else right
            if cur in side:
                cur = side[cur]
            else:
                side[cur] = i
                break
    order = []
    stack = [0]
    while stack:
        u = stack.pop()
        order.append(val[u])
        if u in right:
            stack.append(right[u])
        if u in left:
            stack.append(left[u])
    return "YES" if order == list(a) else "NO"
''',
    java='''
    static String solve(int[] a) {
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        long low = Long.MIN_VALUE;
        for (int x : a) {
            if (x < low) return "NO";
            while (!stack.isEmpty() && stack.peek() < x) low = stack.pop();
            stack.push(x);
        }
        return "YES";
    }
''',
    examples=[("Example 1", "5\n5 2 1 3 6\n"), ("Example 2", "5\n5 2 6 1 3\n")],
    hidden=[
        ("Single value", "1\n1\n"),
        ("Right chain", "4\n1 2 3 4\n"),
        ("Left chain", "4\n4 3 2 1\n"),
        ("Small value after a right turn", "3\n2 3 1\n"),
        ("Deep right subtree", "7\n10 5 1 7 40 50 45\n"),
    ],
    expl=[
        "The tree 5 → (2 → 1, 3), 6 has exactly this preorder.",
        "After 6, everything belongs to 5's right subtree, so 1 cannot appear.",
    ],
    prereqs=[
        ("bst", "Preorder of a BST: a node, its smaller values, then its larger values."),
        ("stack", "A monotonic stack of ancestors whose right subtrees are still open."),
    ],
)

_p(
    "unique-bst-count", "Unique Binary Search Trees", "Medium",
    topics=["Trees", "Dynamic Programming", "Math"], subtopics=["BST", "Catalan Numbers"], companies=["Amazon", "Google"],
    shape="n", ret="long", todo="G[i] = sum over roots r of G[r − 1] × G[i − r]; G[0] = 1",
    description=(
        "How many structurally different binary search trees store exactly the values "
        "`1, 2, …, n`?\n\n"
        "### Input\nOne line: `n`.\n\n"
        "### Output\nThe number of distinct BSTs."
    ),
    constraints="1 ≤ n ≤ 19",
    hints=[
        "Pick the root r. The BST property decides everything else about which values go where.",
        "Values 1..r−1 form the left subtree and r+1..n the right. Their counts depend only on their sizes.",
        "G[i] = Σ over r = 1..i of G[r − 1] · G[i − r], with G[0] = 1 for the empty tree.",
    ],
    opt=("O(n²)", "O(n)", "n table entries, each a sum over up to n roots."),
    editorial=(
        "## The one thing this teaches\n**Choose the root, and independent sides multiply.** "
        "Once the root is fixed, the left and right subtrees are separate problems whose shapes "
        "combine freely — so their counts multiply, and summing over roots gives the total.\n\n"
        "## Approach\n```java\nlong[] G = new long[n + 1];\nG[0] = 1;\n"
        "for (int i = 1; i <= n; i++)\n    for (int r = 1; r <= i; r++)\n"
        "        G[i] += G[r - 1] * G[i - r];      // left has r − 1 values, right has i − r\nreturn G[n];\n```\n\n"
        "## Why only the size matters\nThe values 4, 5, 6 can form exactly as many BSTs as 1, 2, "
        "3 — relabelling preserves order. That is what lets one table serve every subrange.\n\n"
        "## Catalan numbers\nThese are the Catalan numbers, `C(2n, n) / (n + 1)`: 1, 1, 2, 5, 14, "
        "42, … They also count balanced parenthesis strings and ways to triangulate a polygon — "
        "all problems that split into two independent parts around a chosen element."
    ),
    py='''
def solve(n):
    from math import comb
    return comb(2 * n, n) // (n + 1)
''',
    java='''
    static long solve(long nn) {
        int n = (int) nn;
        long[] G = new long[n + 1];
        G[0] = 1;
        for (int i = 1; i <= n; i++)
            for (int r = 1; r <= i; r++)
                G[i] += G[r - 1] * G[i - r];
        return G[n];
    }
''',
    examples=[("Example 1", "3\n"), ("Example 2", "1\n")],
    hidden=[
        ("Four values", "4\n"),
        ("Ten values", "10\n"),
        ("Largest", "19\n"),
        ("Two values", "2\n"),
    ],
    expl=[
        "Root 1: two shapes on the right. Root 2: one. Root 3: two on the left. Total 5.",
        "A single node.",
    ],
    prereqs=[
        ("bst", "Fixing the root decides which values go left and which go right."),
        ("dp", "A table indexed by subtree size, built from smaller sizes."),
    ],
)

_p(
    "largest-bst-subtree", "Largest BST Subtree", "Medium",
    topics=["Trees"], subtopics=["BST", "Tree DP"], companies=["Microsoft", "Meta"],
    shape="tree", ret="int", todo="post-order: each node learns from its children whether they are BSTs and their min, max and size",
    description=(
        "A **subtree** here is a node together with all of its descendants. Print the number of "
        "nodes in the largest subtree that is a binary search tree (left values strictly smaller, "
        "right values strictly larger, at every node).\n\n"
        "### Input\nOne line: the tree in level order, `null` for a missing child (empty for an empty tree).\n\n"
        "### Output\nThe size of the largest BST subtree (0 for an empty tree)."
    ),
    constraints="0 ≤ nodes ≤ 1000\n-10^4 ≤ value ≤ 10^4",
    hints=[
        "Validating the subtree at every node separately costs O(n) each — O(n²) overall.",
        "A node's subtree is a BST exactly when both children's subtrees are BSTs, the left maximum is below the node, and the right minimum is above it.",
        "Return four facts from each call — is BST, min, max, size — so a parent decides in O(1).",
    ],
    opt=("O(n)", "O(h)", "One post-order pass; recursion depth is the height."),
    editorial=(
        "## The one thing this teaches\n**Return a summary, not a yes/no.** A child saying \"I am "
        "a BST\" is not enough for its parent, which also needs the range of values below. "
        "Returning `(isBST, min, max, size)` lets every node decide in constant time.\n\n"
        "## Approach\n```java\n// returns {isBST (1/0), min, max, size}\nint[] visit(TreeNode t) {\n"
        "    if (t == null) return new int[]{1, Integer.MAX_VALUE, Integer.MIN_VALUE, 0};\n"
        "    int[] L = visit(t.left), R = visit(t.right);\n"
        "    if (L[0] == 1 && R[0] == 1 && L[2] < t.val && t.val < R[1]) {\n"
        "        int size = L[3] + R[3] + 1;\n        best = Math.max(best, size);\n"
        "        return new int[]{1, Math.min(L[1], t.val), Math.max(R[2], t.val), size};\n    }\n"
        "    return new int[]{0, 0, 0, 0};\n}\n```\n\n"
        "## The empty-subtree sentinel\nAn empty child reports min = +∞ and max = −∞, so the "
        "comparisons `L.max < val < R.min` pass automatically — no null checks in the parent.\n\n"
        "## Why checking children alone is wrong\nIn `10 5 15 1 12`, every node is ordered "
        "correctly against its own children — yet 12 sits in 10's left subtree. Comparing 10 "
        "with the left subtree's *maximum* (12), not its child (5), catches it. The largest BST "
        "is `5 → 1, 12`, with 3 nodes."
    ),
    py='''
def solve(root):
    def inorder(t, out):
        if t:
            inorder(t.left, out)
            out.append(t.val)
            inorder(t.right, out)
        return out

    best = 0
    stack = [root] if root else []
    while stack:
        t = stack.pop()
        vals = inorder(t, [])
        if all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)):
            best = max(best, len(vals))
        if t.left:
            stack.append(t.left)
        if t.right:
            stack.append(t.right)
    return best
''',
    java='''
    static int best;

    static int[] visit(TreeNode t) {
        if (t == null) return new int[]{1, Integer.MAX_VALUE, Integer.MIN_VALUE, 0};
        int[] L = visit(t.left), R = visit(t.right);
        if (L[0] == 1 && R[0] == 1 && L[2] < t.val && t.val < R[1]) {
            int size = L[3] + R[3] + 1;
            best = Math.max(best, size);
            return new int[]{1, Math.min(L[1], t.val), Math.max(R[2], t.val), size};
        }
        return new int[]{0, 0, 0, 0};
    }

    static int solve(TreeNode root) {
        best = 0;
        visit(root);
        return best;
    }
''',
    examples=[("Example 1", "10 5 15 1 8 null 7\n"), ("Example 2", "3 2 4 null null 1\n")],
    hidden=[
        ("Grandchild out of range", "10 5 15 1 12\n"),
        ("Empty tree", "\n"),
        ("Single node", "1\n"),
        ("Whole tree", "2 1 3\n"),
        ("Only leaves qualify", "1 2 3\n"),
        ("Duplicate breaks it", "2 2 3\n"),
    ],
    expl=[
        "The subtree 5 → 1, 8 is a BST of 3 nodes; the subtree at 15 has 7 on its right, so it is not.",
        "4 → 1 is a BST of 2 nodes. The whole tree is not: 1 sits in 3's right subtree.",
    ],
    prereqs=[
        ("bst", "The BST condition as a range check against the subtrees' minimum and maximum."),
        ("tree_dp", "A post-order pass returning several facts about each subtree."),
    ],
)

_p(
    "first-negative-in-window", "First Negative in Every Window", "Easy",
    topics=["Queues", "Sliding Window"], subtopics=["Deque"], companies=["Amazon"],
    shape="arr_k", ret="String", todo="queue the indices of negative numbers; drop those left of the window; the front is the answer",
    description=(
        "For every window of `k` consecutive elements, print the **first negative number** in "
        "it, or `0` if the window has none.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe `n − k + 1` answers, separated by spaces."
    ),
    constraints="1 ≤ k ≤ n ≤ 10^5\n-10^5 ≤ a[i] ≤ 10^5",
    hints=[
        "Scanning each window is O(n · k).",
        "Only negative numbers can be answers, and they are needed in the order they appeared.",
        "Keep a queue of the indices of negatives. When the window moves past the front index, remove it. The front of the queue is the answer.",
    ],
    opt=("O(n)", "O(k)", "Each index enters and leaves the queue at most once."),
    editorial=(
        "## The one thing this teaches\n**Keep only the candidates, in arrival order.** A queue "
        "of candidates is the gentle version of the monotonic deque: here no candidate ever makes "
        "another useless, so nothing is removed from the back — only expired ones from the front.\n\n"
        "## Approach\n```java\nDeque<Integer> neg = new ArrayDeque<>();\n"
        "for (int i = 0; i < n; i++) {\n    if (a[i] < 0) neg.addLast(i);\n"
        "    if (!neg.isEmpty() && neg.peekFirst() <= i - k) neg.pollFirst();   // left the window\n"
        "    if (i >= k - 1) out.add(neg.isEmpty() ? 0 : a[neg.peekFirst()]);\n}\n```\n\n"
        "## Why one removal per step is enough\nThe window slides by one, so at most one index "
        "leaves it each step — and only the oldest queued index can be that one.\n\n"
        "## Compared with the sliding maximum\nFor the maximum, a new large value makes older "
        "smaller ones useless, so they are popped from the back. \"First negative\" has no such "
        "dominance: an older negative always wins while it is inside the window."
    ),
    py='''
def solve(a, k):
    out = []
    for i in range(len(a) - k + 1):
        out.append(next((x for x in a[i:i + k] if x < 0), 0))
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a, long kk) {
        int n = a.length, k = (int) kk;
        ArrayDeque<Integer> neg = new ArrayDeque<>();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (a[i] < 0) neg.addLast(i);
            if (!neg.isEmpty() && neg.peekFirst() <= i - k) neg.pollFirst();
            if (i >= k - 1) {
                if (sb.length() > 0) sb.append(' ');
                sb.append(neg.isEmpty() ? 0 : a[neg.peekFirst()]);
            }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "8 3\n12 -1 -7 8 -15 30 16 28\n"), ("Example 2", "5 2\n-8 2 3 -6 10\n")],
    hidden=[
        ("No negatives", "1 1\n5\n"),
        ("Window is the whole array", "3 3\n-1 -2 -3\n"),
        ("Window of one", "4 1\n-1 2 -3 4\n"),
        ("Negatives at the edges", "6 4\n-5 1 2 3 4 -6\n"),
    ],
    expl=[
        "Windows: [12 −1 −7] → −1, [−1 −7 8] → −1, [−7 8 −15] → −7, [8 −15 30] → −15, [−15 30 16] → −15, [30 16 28] → 0.",
        "[−8 2] → −8, [2 3] → 0, [3 −6] → −6, [−6 10] → −6.",
    ],
    prereqs=[
        ("queue", "A FIFO of candidate indices, expired from the front."),
        ("sliding_window", "A fixed-size window moving one step at a time."),
    ],
)
