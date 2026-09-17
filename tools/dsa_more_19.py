# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 19 — strings, stacks, searches and a BFS.
#
#   longest-palindromic-substring   expand around each of the 2n − 1 centres
#   first-missing-positive          the array is its own hash table: value v lives at index v − 1
#   basic-calculator                a stack only at parentheses, holding (result, sign)
#   remove-duplicate-letters        a monotonic stack that pops only what will come again
#   single-element-sorted-array     pairs start on even indices until the single one
#   longest-turbulent-subarray      two running lengths: ending on a rise, ending on a fall
#   queue-reconstruction-by-height  tallest first, each inserted at position k
#   minimum-knight-moves            BFS layers are move counts; symmetry folds the board
# ===========================================================================

_p(
    "longest-palindromic-substring", "Longest Palindromic Substring", "Medium",
    topics=["Strings", "Two Pointers"], subtopics=["Palindromes", "Expand Around Centre"], companies=["Amazon", "Microsoft"],
    shape="str", ret="String", todo="expand outward from every centre — each character, and each gap between two",
    description=(
        "Print the longest substring of `s` that reads the same forwards and backwards. If several "
        "have the maximum length, print the one that starts **leftmost**.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe longest palindromic substring."
    ),
    constraints="1 ≤ |s| ≤ 1000\ns consists of lowercase letters and digits",
    hints=[
        "Checking every substring is O(n²) substrings × O(n) each = O(n³).",
        "Every palindrome has a centre: a single character (odd length) or the gap between two (even length).",
        "From each of the 2n − 1 centres, grow outward while both ends match. Keep the longest; replace it only on a strictly longer find.",
    ],
    opt=("O(n²)", "O(1)", "2n − 1 centres, each expanding at most n/2 steps; only indices are stored."),
    editorial=(
        "## The one thing this teaches\n**Enumerate by the centre, not by the ends.** Choosing "
        "both ends gives n² substrings to check. Choosing a centre gives 2n − 1 starting points, "
        "and growing outward checks each longer palindrome in O(1) — one new pair of characters.\n\n"
        "## Approach\n```java\nint bestLo = 0, bestLen = 1;\nfor (int i = 0; i < n; i++)\n"
        "    for (int w = 0; w < 2; w++) {                 // w = 0: centre i; w = 1: gap after i\n"
        "        int lo = i, hi = i + w;\n"
        "        while (lo >= 0 && hi < n && s.charAt(lo) == s.charAt(hi)) { lo--; hi++; }\n"
        "        int len = hi - lo - 1;\n"
        "        if (len > bestLen) { bestLen = len; bestLo = lo + 1; }\n    }\n"
        "return s.substring(bestLo, bestLo + bestLen);\n```\n\n"
        "## Why strict `>` gives the leftmost\nTwo palindromes of equal length have the same "
        "parity, so they come from the same kind of centre — and for a fixed length, a later "
        "centre means a later start. The first one found is the leftmost; `>=` would keep the last.\n\n"
        "## Beyond O(n²)\nManacher's algorithm reuses the mirror image of palindromes already "
        "found to reach O(n). It is rarely expected in an interview; the centre expansion is."
    ),
    py='''
def solve(s):
    n = len(s)
    for length in range(n, 0, -1):
        for i in range(n - length + 1):
            t = s[i:i + length]
            if t == t[::-1]:
                return t
''',
    java='''
    static String solve(String s) {
        int n = s.length(), bestLo = 0, bestLen = 1;
        for (int i = 0; i < n; i++)
            for (int w = 0; w < 2; w++) {
                int lo = i, hi = i + w;
                while (lo >= 0 && hi < n && s.charAt(lo) == s.charAt(hi)) { lo--; hi++; }
                int len = hi - lo - 1;
                if (len > bestLen) { bestLen = len; bestLo = lo + 1; }
            }
        return s.substring(bestLo, bestLo + bestLen);
    }
''',
    examples=[("Example 1", "babad\n"), ("Example 2", "cbbd\n")],
    hidden=[
        ("Single character", "a\n"),
        ("No repeats: the first character", "abcde\n"),
        ("Whole string", "aaaa\n"),
        ("Long even palindrome inside", "forgeeksskeegfor\n"),
        ("Reversed copy is not a palindrome", "abacdfgdcaba\n"),
    ],
    expl=[
        "\"bab\" and \"aba\" both have length 3; \"bab\" starts first.",
        "\"bb\" is centred on the gap between the two b's.",
    ],
    prereqs=[
        ("two_pointers", "Two indices moving outward from a centre while the characters match."),
        ("string_basics", "Substrings by index range, and palindromes of odd and even length."),
    ],
)

_p(
    "first-missing-positive", "First Missing Positive", "Hard",
    topics=["Arrays", "Hashing"], subtopics=["Cyclic Sort", "In-place Hashing"], companies=["Amazon", "Google", "Microsoft"],
    shape="arr", ret="int", todo="swap each value v in 1..n to index v − 1; the first index i holding the wrong value gives i + 1",
    description=(
        "Find the smallest **positive** integer that does not appear in the array.\n\n"
        "Aim for O(n) time and O(1) extra space — you may rearrange the array.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe smallest missing positive integer."
    ),
    constraints="1 ≤ n ≤ 10^5\n-2^31 ≤ a[i] ≤ 2^31 − 1",
    hints=[
        "A hash set solves it in O(n) time — but uses O(n) extra space.",
        "With n numbers, the answer is between 1 and n + 1. Values outside 1..n can never change it.",
        "Use the array as the set: move each value v in 1..n to index v − 1 by swapping. Then scan for the first index i with a[i] ≠ i + 1.",
    ],
    opt=("O(n)", "O(1)", "Each swap puts one value in its final place, so there are at most n swaps in total."),
    editorial=(
        "## The one thing this teaches\n**When the values index the array, the array is the hash "
        "table.** The answer lies in `1..n+1`, so only values in `1..n` matter, and each has a "
        "natural home: index `v − 1`.\n\n"
        "## Approach\n```java\nfor (int i = 0; i < n; i++)\n"
        "    while (a[i] >= 1 && a[i] <= n && a[a[i] - 1] != a[i]) {\n"
        "        int j = a[i] - 1;\n        int t = a[j]; a[j] = a[i]; a[i] = t;   // a[i] goes home\n    }\n"
        "for (int i = 0; i < n; i++)\n    if (a[i] != i + 1) return i + 1;\nreturn n + 1;\n```\n\n"
        "## Why the nested loop is O(n)\nEvery swap places one value at its home, and a value at "
        "home is never moved again. At most n swaps happen across the whole run, however the "
        "`while` iterations are distributed.\n\n"
        "## The duplicate trap\nThe condition is `a[a[i] − 1] != a[i]`, not `a[i] != i + 1`. With "
        "`2 2`, the second 2 is not at home but its home already holds a 2 — swapping them would "
        "loop forever."
    ),
    py='''
def solve(a):
    seen = set(a)
    i = 1
    while i in seen:
        i += 1
    return i
''',
    java='''
    static int solve(int[] a) {
        int n = a.length;
        for (int i = 0; i < n; i++)
            while (a[i] >= 1 && a[i] <= n && a[a[i] - 1] != a[i]) {
                int j = a[i] - 1;
                int t = a[j]; a[j] = a[i]; a[i] = t;
            }
        for (int i = 0; i < n; i++)
            if (a[i] != i + 1) return i + 1;
        return n + 1;
    }
''',
    examples=[("Example 1", "3\n1 2 0\n"), ("Example 2", "4\n3 4 -1 1\n")],
    hidden=[
        ("Nothing small", "5\n7 8 9 11 12\n"),
        ("Just one", "1\n1\n"),
        ("Duplicates", "5\n2 2 2 1 1\n"),
        ("A full permutation", "4\n4 3 2 1\n"),
        ("Extremes", "4\n-2147483648 2147483647 0 1\n"),
    ],
    expl=[
        "1 and 2 are present; 3 is not.",
        "1, 3 and 4 are present; 2 is missing.",
    ],
    prereqs=[
        ("hashing", "The set-membership question, answered with the array as the table."),
        ("array_patterns", "In-place swapping that moves each value to the index it names."),
    ],
)

_p(
    "basic-calculator", "Basic Calculator", "Hard",
    topics=["Stacks", "Strings"], subtopics=["Expression Evaluation"], companies=["Google", "Meta", "Amazon"],
    shape="line", ret="long", todo="keep a running result and sign; at '(' push both and start fresh, at ')' pop and combine",
    description=(
        "Evaluate an expression made of non-negative integers, `+`, `-`, parentheses and spaces.\n\n"
        "A `-` may also be **unary**: at the very start of the expression or directly after `(` "
        "(ignoring spaces), as in `-(2 + 3)` or `(-4)`.\n\n"
        "### Input\nOne line: the expression.\n\n"
        "### Output\nIts value."
    ),
    constraints="1 ≤ length ≤ 3·10^5\nThe expression is valid; numbers have no leading zeros\nEvery intermediate value fits in a signed 32-bit integer",
    hints=[
        "Without parentheses, keep `result` and the `sign` of the number being read; add `sign * num` whenever an operator or the end arrives.",
        "A '(' starts a fresh sub-expression. You need to remember the result so far and the sign in front of the parenthesis.",
        "Push (result, sign) at '('. At ')', finish the inner result, multiply it by the saved sign and add the saved result.",
    ],
    opt=("O(n)", "O(depth)", "One pass; the stack grows only with the nesting depth."),
    editorial=(
        "## The one thing this teaches\n**Only save what the nested part will interrupt.** With "
        "just `+` and `-`, there is no precedence to manage — a running sum is enough. "
        "Parentheses are the only interruption, and they need exactly two numbers saved: the sum "
        "so far and the sign in front of the bracket.\n\n"
        "## Approach\n```java\nlong result = 0, num = 0;\nint sign = 1;\nDeque<Long> st = new ArrayDeque<>();\n"
        "for (char c : s.toCharArray()) {\n"
        "    if (Character.isDigit(c)) num = num * 10 + (c - '0');\n"
        "    else if (c == '+' || c == '-') { result += sign * num; num = 0; sign = c == '+' ? 1 : -1; }\n"
        "    else if (c == '(') { st.push(result); st.push((long) sign); result = 0; sign = 1; }\n"
        "    else if (c == ')') { result += sign * num; num = 0; result *= st.pop(); result += st.pop(); }\n}\n"
        "return result + sign * num;\n```\n\n"
        "## Unary minus is free\nAt the start (or right after `(`) `result` is 0, so `-5` is "
        "read as `0 - 5`. No special case.\n\n"
        "## The pop order\nThe sign was pushed last, so it comes off first: multiply the inner "
        "result by it, then add the outer result underneath."
    ),
    py='''
def solve(s):
    return eval(s.strip(), {"__builtins__": {}}, {})
''',
    java='''
    static long solve(String s) {
        long result = 0, num = 0;
        int sign = 1;
        ArrayDeque<Long> st = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (Character.isDigit(c)) num = num * 10 + (c - '0');
            else if (c == '+' || c == '-') { result += sign * num; num = 0; sign = c == '+' ? 1 : -1; }
            else if (c == '(') { st.push(result); st.push((long) sign); result = 0; sign = 1; }
            else if (c == ')') { result += sign * num; num = 0; result *= st.pop(); result += st.pop(); }
        }
        return result + sign * num;
    }
''',
    examples=[("Example 1", "1 + 1\n"), ("Example 2", "(1+(4+5+2)-3)+(6+8)\n")],
    hidden=[
        ("Surrounding spaces", " 2-1 + 2 \n"),
        ("Unary minus at the start", "-(2 + 3)\n"),
        ("Nested subtraction", "10 - (4 - (3 - 1))\n"),
        ("Unary minus after a bracket", "1-(     -2)\n"),
        ("One large number", "2147483647\n"),
        ("Deep nesting", "((((((7))))))-(((((8)))))\n"),
    ],
    expl=[
        "1 + 1 = 2.",
        "(4 + 5 + 2) = 11, so the first bracket is 1 + 11 − 3 = 9, and 9 + 14 = 23.",
    ],
    prereqs=[
        ("stack", "Saving the outer state at '(' and restoring it at ')'."),
        ("string_basics", "Reading multi-digit numbers one character at a time."),
    ],
)

_p(
    "remove-duplicate-letters", "Remove Duplicate Letters", "Medium",
    topics=["Stacks", "Greedy", "Strings"], subtopics=["Monotonic Stack"], companies=["Google", "Amazon"],
    shape="str", ret="String", todo="stack of letters; pop a larger top only if it occurs again later and the new letter is not already kept",
    description=(
        "Delete letters from `s` so that every distinct letter appears **exactly once**. Among all "
        "possible results, print the lexicographically smallest.\n\n"
        "The result is a subsequence of `s` — the kept letters stay in their original order.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe smallest result."
    ),
    constraints="1 ≤ |s| ≤ 10^4\ns consists of lowercase English letters",
    hints=[
        "Build the answer left to right. A smaller letter wants to be as early as possible.",
        "If the letter on top of your partial answer is larger than the current one AND appears again later, removing it now costs nothing — it can be picked up later.",
        "Record each letter's last index. Skip letters already in the stack; otherwise pop while the top is larger and its last index is ahead, then push.",
    ],
    opt=("O(n)", "O(1)", "Each letter is pushed and popped at most once per occurrence; the stack holds at most 26 letters."),
    editorial=(
        "## The one thing this teaches\n**A monotonic stack with a veto.** The usual rule — pop "
        "anything larger than the newcomer — produces the smallest sequence. Here a pop is "
        "vetoed when the popped letter will never appear again, because every letter must be "
        "kept once.\n\n"
        "## Approach\n```java\nint[] last = new int[26];\nfor (int i = 0; i < n; i++) last[s.charAt(i) - 'a'] = i;\n"
        "boolean[] kept = new boolean[26];\nStringBuilder st = new StringBuilder();\n"
        "for (int i = 0; i < n; i++) {\n    char c = s.charAt(i);\n    if (kept[c - 'a']) continue;\n"
        "    while (st.length() > 0) {\n        char top = st.charAt(st.length() - 1);\n"
        "        if (top <= c || last[top - 'a'] < i) break;   // smaller, or last chance: keep it\n"
        "        kept[top - 'a'] = false;\n        st.setLength(st.length() - 1);\n    }\n"
        "    st.append(c);\n    kept[c - 'a'] = true;\n}\n```\n\n"
        "## Why skip letters already kept\nIn `cbacdcbc`, when the second `c` arrives (index 5) "
        "the stack is `a c d`. The kept `c` survived every push after it, so it already sits in "
        "its best position; a second copy would break \"exactly once\". Later, the `b` at index "
        "6 cannot pop `d` — index 4 was the last `d` — which is why the answer ends `…d b`.\n\n"
        "## Walkthrough: bcabc\n`b` → `b`; `c` → `bc`; `a` pops `c` (seen again) and `b` (seen "
        "again) → `a`; `b` → `ab`; `c` → `abc`."
    ),
    py='''
def solve(s):
    out = []
    while s:
        need = set(s)
        for c in sorted(need):
            i = s.index(c)
            if set(s[i:]) == need:
                out.append(c)
                s = s[i + 1:].replace(c, "")
                break
    return "".join(out)
''',
    java='''
    static String solve(String s) {
        int n = s.length();
        int[] last = new int[26];
        for (int i = 0; i < n; i++) last[s.charAt(i) - 'a'] = i;
        boolean[] kept = new boolean[26];
        StringBuilder st = new StringBuilder();
        for (int i = 0; i < n; i++) {
            char c = s.charAt(i);
            if (kept[c - 'a']) continue;
            while (st.length() > 0) {
                char top = st.charAt(st.length() - 1);
                if (top <= c || last[top - 'a'] < i) break;
                kept[top - 'a'] = false;
                st.setLength(st.length() - 1);
            }
            st.append(c);
            kept[c - 'a'] = true;
        }
        return st.toString();
    }
''',
    examples=[("Example 1", "bcabc\n"), ("Example 2", "cbacdcbc\n")],
    hidden=[
        ("Single letter", "a\n"),
        ("One letter repeated", "aaaa\n"),
        ("Decreasing, no repeats", "zyxw\n"),
        ("Repeat of a kept letter", "abacb\n"),
        ("Pop vetoed", "bcab\n"),
        ("Last chance for e", "ecbacba\n"),
    ],
    expl=[
        "Both b and c appear again after the a, so they can wait: \"abc\".",
        "The d appears only once, so it cannot be popped for the later b: \"acdb\".",
    ],
    prereqs=[
        ("stack", "A monotonic stack whose pops are conditional on a later occurrence."),
        ("greedy", "Putting the smallest possible letter first whenever doing so loses nothing."),
    ],
)

_p(
    "single-element-sorted-array", "Single Element in a Sorted Array", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search on Predicate"], companies=["Google", "Microsoft"],
    shape="arr", ret="int", todo="binary search on even indices: a[mid] == a[mid + 1] means the single element is to the right",
    description=(
        "A sorted array contains every value **exactly twice**, except one value that appears "
        "once. Find that value in O(log n) time.\n\n"
        "### Input\n- Line 1: `n` (odd).\n- Line 2: `n` integers in non-decreasing order.\n\n"
        "### Output\nThe value that appears once."
    ),
    constraints="1 ≤ n ≤ 10^5, n odd\n-10^9 ≤ a[i] ≤ 10^9",
    hints=[
        "XOR of everything gives the answer in O(n). The sorted order promises something faster.",
        "Before the single element, each pair starts at an even index. After it, each pair starts at an odd index.",
        "Look only at even indices mid: if a[mid] == a[mid + 1], everything up to mid + 1 is paired normally — go right. Otherwise the single is at mid or to its left.",
    ],
    opt=("O(log n)", "O(1)", "A binary search over the even indices."),
    editorial=(
        "## The one thing this teaches\n**Binary search needs a monotone predicate, not a target "
        "value.** There is nothing to compare against here — but \"the pair starting at this "
        "even index is intact\" is true up to the single element and false from it onward.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo < hi) {\n"
        "    int mid = (lo + hi) / 2;\n    if (mid % 2 == 1) mid--;          // land on an even index\n"
        "    if (a[mid] == a[mid + 1]) lo = mid + 2;   // intact pair: single is later\n"
        "    else hi = mid;                            // broken: single is here or earlier\n}\n"
        "return a[lo];\n```\n\n"
        "## Why mid + 1 is always in range\n`lo < hi` and both are even, so `hi ≥ lo + 2 > mid`. "
        "The even-index `mid` is strictly below `hi`, leaving room for `mid + 1`.\n\n"
        "## Walkthrough: 1 1 2 3 3 4 4 8 8\nmid = 4 (`3`, next `4`): broken → hi = 4. mid = 2 "
        "(`2`, next `3`): broken → hi = 2. mid = 0 (`1`, next `1`): intact → lo = 2. Answer `a[2] = 2`."
    ),
    py='''
def solve(a):
    x = 0
    for v in a:
        x ^= v
    return x
''',
    java='''
    static int solve(int[] a) {
        int lo = 0, hi = a.length - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (mid % 2 == 1) mid--;
            if (a[mid] == a[mid + 1]) lo = mid + 2;
            else hi = mid;
        }
        return a[lo];
    }
''',
    examples=[("Example 1", "9\n1 1 2 3 3 4 4 8 8\n"), ("Example 2", "7\n3 3 7 7 10 11 11\n")],
    hidden=[
        ("Only element", "1\n5\n"),
        ("Single at the end", "3\n1 1 2\n"),
        ("Single at the start", "3\n1 2 2\n"),
        ("Negative values", "5\n-3 -3 -1 0 0\n"),
        ("Wide values", "7\n-1000000000 -1000000000 0 0 999999999 1000000000 1000000000\n"),
    ],
    expl=[
        "Every value except 2 appears twice.",
        "10 is the only value without a partner.",
    ],
    prereqs=[
        ("binary_search", "Searching for the first index where a monotone predicate turns false."),
        ("bit_manip", "The O(n) XOR baseline this improves on."),
    ],
)

_p(
    "longest-turbulent-subarray", "Longest Turbulent Subarray", "Medium",
    topics=["Arrays", "Dynamic Programming", "Sliding Window"], subtopics=["Running Length"], companies=["Amazon"],
    shape="arr", ret="int", todo="track the longest turbulent run ending here on a rise and on a fall; each extends the other",
    description=(
        "A subarray is **turbulent** if the comparison between neighbours flips at every step: "
        "`a[i] > a[i+1] < a[i+2] > …` or `a[i] < a[i+1] > a[i+2] < …`. Equal neighbours break "
        "turbulence. A single element is turbulent.\n\n"
        "Print the length of the longest turbulent subarray.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe maximum length."
    ),
    constraints="1 ≤ n ≤ 4·10^4\n0 ≤ a[i] ≤ 10^9",
    hints=[
        "Extending from every start is O(n²).",
        "A turbulent run ending at i either ends with a rise (a[i−1] < a[i]) or with a fall.",
        "A run ending in a rise extends a run that ended in a fall, and vice versa: up = down + 1 or down = up + 1. Equal neighbours reset both to 1.",
    ],
    opt=("O(n)", "O(1)", "Two running lengths updated per element."),
    editorial=(
        "## The one thing this teaches\n**When the rule alternates, keep one state per phase.** "
        "\"Longest run ending here\" is not enough on its own — whether it can grow depends on "
        "the direction of its last step. Two numbers, one per direction, carry exactly that.\n\n"
        "## Approach\n```java\nint up = 1, down = 1, best = 1;\nfor (int i = 1; i < n; i++) {\n"
        "    if (a[i] > a[i - 1])      { up = down + 1; down = 1; }\n"
        "    else if (a[i] < a[i - 1]) { down = up + 1; up = 1; }\n"
        "    else                      { up = 1; down = 1; }\n"
        "    best = Math.max(best, Math.max(up, down));\n}\n```\n\n"
        "## Walkthrough: 9 4 2 10 7 8 8 1 9\n| i | step | up | down |\n|---|---|---|---|\n"
        "| 1 | 9→4 fall | 1 | 2 |\n| 2 | 4→2 fall | 1 | 2 |\n| 3 | 2→10 rise | 3 | 1 |\n"
        "| 4 | 10→7 fall | 1 | 4 |\n| 5 | 7→8 rise | 5 | 1 |\n| 6 | 8→8 equal | 1 | 1 |\n"
        "| 7 | 8→1 fall | 1 | 2 |\n| 8 | 1→9 rise | 3 | 1 |\n\nThe best is 5: `4 2 10 7 8`.\n\n"
        "## As a sliding window\nThe same answer comes from a window whose left edge jumps to "
        "the break point whenever the alternation fails — the two views are the same pass."
    ),
    py='''
def solve(a):
    n = len(a)
    best = 1
    for i in range(n):
        j = i
        while j + 1 < n and a[j] != a[j + 1] and (j == i or (a[j - 1] < a[j]) != (a[j] < a[j + 1])):
            j += 1
        best = max(best, j - i + 1)
    return best
''',
    java='''
    static int solve(int[] a) {
        int up = 1, down = 1, best = 1;
        for (int i = 1; i < a.length; i++) {
            if (a[i] > a[i - 1]) { up = down + 1; down = 1; }
            else if (a[i] < a[i - 1]) { down = up + 1; up = 1; }
            else { up = 1; down = 1; }
            best = Math.max(best, Math.max(up, down));
        }
        return best;
    }
''',
    examples=[("Example 1", "9\n9 4 2 10 7 8 8 1 9\n"), ("Example 2", "4\n4 8 12 16\n")],
    hidden=[
        ("Single element", "1\n100\n"),
        ("All equal", "3\n5 5 5\n"),
        ("Whole array", "6\n1 3 2 4 3 5\n"),
        ("Ends on an equal pair", "5\n2 1 2 1 1\n"),
        ("Two equal values", "2\n7 7\n"),
    ],
    expl=[
        "4 > 2 < 10 > 7 < 8 has length 5; the next step, 8 → 8, breaks it.",
        "Every step is a rise, so any two neighbours are the longest turbulent run.",
    ],
    prereqs=[
        ("dp", "Two running states that feed each other, one per direction of the last step."),
        ("sliding_window", "The equivalent window view, restarting at each break."),
    ],
)

_p(
    "queue-reconstruction-by-height", "Queue Reconstruction by Height", "Medium",
    topics=["Greedy", "Sorting", "Arrays"], subtopics=["Sort then Insert"], companies=["Google", "Amazon"],
    shape="pairs", ret="String", todo="sort by height descending (k ascending on ties), then insert each person at index k",
    description=(
        "People stood in a queue, and each wrote down a pair `h k`: their height `h`, and `k`, the "
        "number of people **in front of them** whose height is **at least** `h`. The pairs are "
        "now shuffled. Rebuild the queue.\n\n"
        "### Input\n- Line 1: `n`.\n- Next `n` lines: `h k`.\n\n"
        "### Output\n`n` lines: the pairs `h k` in queue order, front first."
    ),
    constraints="1 ≤ n ≤ 2000\n0 ≤ h ≤ 10^6\n0 ≤ k < n\nThe pairs always describe a valid queue",
    hints=[
        "Shorter people are invisible to taller people's counts. Place the tall ones first.",
        "Once everyone at least as tall as h is placed, a person (h, k) must go where exactly k of them are ahead — index k in the list so far.",
        "Sort by height descending and, for equal heights, k ascending. Insert each at index k.",
    ],
    opt=("O(n²)", "O(n)", "n inserts into a list, each O(n). A Fenwick tree reaches O(n log n)."),
    editorial=(
        "## The one thing this teaches\n**Process in the order that freezes the constraint.** A "
        "person's `k` counts only people at least as tall. Insert from tallest to shortest, and "
        "when a person arrives, *every* person who can affect their count is already in the "
        "list — and everyone inserted later is shorter, so it cannot change it.\n\n"
        "## Approach\n```java\nArrays.sort(p, (x, y) -> x[0] != y[0] ? y[0] - x[0] : x[1] - y[1]);\n"
        "List<int[]> q = new ArrayList<>();\nfor (int[] person : p) q.add(person[1], person);\n```\n\n"
        "## Why k ascending on ties\nTwo people of equal height count each other. With `(5, 0)` "
        "and `(5, 2)`, the `(5, 0)` must be inserted first so that it is one of the people ahead "
        "of `(5, 2)`. Inserting in the other order would put `(5, 0)` in front after the fact "
        "and silently raise the other's count.\n\n"
        "## Walkthrough (Example 1)\nSorted: `7 0, 7 1, 6 1, 5 0, 5 2, 4 4`. Insert at k: "
        "`[7 0]` → `[7 0, 7 1]` → `[7 0, 6 1, 7 1]` → `[5 0, 7 0, 6 1, 7 1]` → "
        "`[5 0, 7 0, 5 2, 6 1, 7 1]` → `[5 0, 7 0, 5 2, 6 1, 4 4, 7 1]`."
    ),
    py='''
def solve(p):
    left = list(p)
    placed = []
    while left:
        ready = [x for x in left if sum(1 for q in placed if q[0] >= x[0]) == x[1]]
        nxt = min(ready)
        placed.append(nxt)
        left.remove(nxt)
    return "\\n".join(f"{h} {k}" for h, k in placed)
''',
    java='''
    static String solve(int[][] p) {
        Arrays.sort(p, (x, y) -> x[0] != y[0] ? Integer.compare(y[0], x[0]) : Integer.compare(x[1], y[1]));
        List<int[]> q = new ArrayList<>();
        for (int[] person : p) q.add(person[1], person);
        StringBuilder sb = new StringBuilder();
        for (int[] person : q) {
            if (sb.length() > 0) sb.append('\\n');
            sb.append(person[0]).append(' ').append(person[1]);
        }
        return sb.toString();
    }
''',
    examples=[
        ("Example 1", "6\n7 0\n4 4\n7 1\n5 0\n6 1\n5 2\n"),
        ("Example 2", "6\n6 0\n5 0\n4 0\n3 2\n2 2\n1 4\n"),
    ],
    hidden=[
        ("One person", "1\n5 0\n"),
        ("Equal heights", "3\n5 2\n5 0\n5 1\n"),
        ("Tallest first", "3\n1 2\n3 0\n2 1\n"),
        ("Shortest first", "4\n4 0\n1 0\n3 0\n2 0\n"),
    ],
    expl=[
        "Check 4 4: of 5, 7, 5, 6 ahead of them, all four are at least 4.",
        "Check 2 2: of 4 and 5 ahead, both are at least 2; 3 2 has only 4 and 5 counting.",
    ],
    prereqs=[
        ("greedy", "An insertion order in which each placement can never be invalidated."),
        ("sorting", "A two-key comparator: height descending, then k ascending."),
    ],
)

_p(
    "minimum-knight-moves", "Minimum Knight Moves", "Medium",
    topics=["Graphs", "BFS"], subtopics=["Shortest Path in Unweighted Graph", "Implicit Graph"], companies=["Google", "Amazon"],
    shape="two", ret="int", todo="BFS from (0, 0) over knight moves; fold the target into the first quadrant and bound the search",
    description=(
        "A knight starts at `(0, 0)` on an **infinite** chessboard. Print the minimum number of "
        "moves to reach `(x, y)`.\n\n"
        "A knight moves two squares in one direction and one square perpendicular to it — eight "
        "possible moves.\n\n"
        "### Input\nOne line: `x y`.\n\n"
        "### Output\nThe minimum number of moves."
    ),
    constraints="-300 ≤ x, y ≤ 300\n|x| + |y| ≤ 300",
    hints=[
        "Squares are nodes and knight moves are edges, all of weight 1. Fewest moves = BFS.",
        "The board is infinite, so BFS needs a boundary. The answer for (x, y) equals the answer for (|x|, |y|) by symmetry.",
        "Search the first quadrant plus a margin of two squares, since an optimal path to a square near an axis may briefly step across it.",
    ],
    opt=("O(|x| · |y|)", "O(|x| · |y|)", "BFS over a bounded box around the rectangle from the origin to the target."),
    editorial=(
        "## The one thing this teaches\n**Implicit graphs still need a finite search space.** "
        "Nothing here is stored as a graph — the eight moves generate neighbours on demand — "
        "but BFS on an infinite board never ends unless you prove a region is enough.\n\n"
        "## Approach\n```java\nint tx = Math.abs(x), ty = Math.abs(y);\n"
        "// allow coordinates in [-2, tx + 2] × [-2, ty + 2]\nqueue.add(origin); dist[origin] = 0;\n"
        "while (!queue.isEmpty()) {\n    cell = queue.poll();\n    if (cell == target) return dist[cell];\n"
        "    for (move : eight moves) if (inside box && unseen) { dist[next] = dist[cell] + 1; queue.add(next); }\n}\n```\n\n"
        "## Why the margin\nReaching `(1, 1)` takes two moves, and every two-move route leaves "
        "the quadrant: `(2, −1)` then `(1, 1)`, for example. Squares near an axis need that room. "
        "A margin of two covers any single knight step across the axis.\n\n"
        "## Symmetry\nReflecting across either axis maps knight moves to knight moves, so "
        "`(x, y)`, `(−x, y)`, `(x, −y)` and `(−x, −y)` all need the same number of moves. Folding "
        "the target into one quadrant shrinks the box by a factor of four."
    ),
    py='''
def solve(x, y):
    from collections import deque
    m = max(abs(x), abs(y)) + 4
    moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    dist = {(0, 0): 0}
    dq = deque([(0, 0)])
    while dq:
        cx, cy = dq.popleft()
        if (cx, cy) == (x, y):
            return dist[(cx, cy)]
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if -m <= nx <= m and -m <= ny <= m and (nx, ny) not in dist:
                dist[(nx, ny)] = dist[(cx, cy)] + 1
                dq.append((nx, ny))
''',
    java='''
    static int solve(long x, long y) {
        int tx = (int) Math.abs(x), ty = (int) Math.abs(y);
        int w = tx + 5, h = ty + 5;               // coordinates -2..tx+2 shifted by 2
        int[][] dist = new int[w][h];
        for (int[] row : dist) Arrays.fill(row, -1);
        int[] dx = {1, 2, 2, 1, -1, -2, -2, -1}, dy = {2, 1, -1, -2, -2, -1, 1, 2};
        ArrayDeque<int[]> q = new ArrayDeque<>();
        dist[2][2] = 0;
        q.add(new int[]{0, 0});
        while (!q.isEmpty()) {
            int[] c = q.poll();
            int d = dist[c[0] + 2][c[1] + 2];
            if (c[0] == tx && c[1] == ty) return d;
            for (int i = 0; i < 8; i++) {
                int nx = c[0] + dx[i], ny = c[1] + dy[i];
                if (nx < -2 || ny < -2 || nx > tx + 2 || ny > ty + 2) continue;
                if (dist[nx + 2][ny + 2] != -1) continue;
                dist[nx + 2][ny + 2] = d + 1;
                q.add(new int[]{nx, ny});
            }
        }
        return -1;
    }
''',
    examples=[("Example 1", "2 1\n"), ("Example 2", "5 5\n")],
    hidden=[
        ("Already there", "0 0\n"),
        ("One diagonal step", "1 1\n"),
        ("One square away", "-1 0\n"),
        ("Two squares diagonally", "2 2\n"),
        ("Far and mixed signs", "100 -37\n"),
        ("Along an axis", "0 -150\n"),
    ],
    expl=[
        "(0, 0) → (2, 1) is a single knight move.",
        "(0, 0) → (2, 1) → (4, 2) → (3, 4) → (5, 5).",
    ],
    prereqs=[
        ("bfs", "Breadth-first search: the first time a square is dequeued, its distance is final."),
        ("grid", "Coordinate offsets, bounds checks and a shifted distance array."),
    ],
)
