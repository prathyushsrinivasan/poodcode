# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 2 — strings and hashing.
#
#   is-subsequence            one pointer per string, the text pointer always advances
#   isomorphic-strings        a mapping must be a function in BOTH directions
#   longest-palindrome-build  count letters; pairs go on the outside, one odd in the middle
#   reverse-words             split on runs of spaces, not on single spaces
#   string-to-integer         a parser: skip, sign, digits, clamp
#   happy-number              a set (or two pointers) to detect a cycle of values
#   ransom-note               a count array as a bag of available letters
#   unique-occurrences        counting the counts
#   pairs-with-difference-k   look up the partner; k = 0 is a different question
# ===========================================================================

_p(
    "is-subsequence", "Is Subsequence", "Easy",
    topics=["Strings", "Two Pointers"], subtopics=["Two Pointers"], companies=["Pinterest", "Amazon"],
    shape="str2", ret="String", todo="walk t once, advancing a pointer into s on every match",
    description=(
        "Is `s` a **subsequence** of `t` — can `s` be obtained by deleting some characters of `t` "
        "without reordering the rest?\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t`.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| ≤ 100\n1 ≤ |t| ≤ 10^4\nBoth consist of lowercase English letters.",
    hints=[
        "Match s's characters in order. Taking the earliest possible match in t is never worse than a later one.",
        "Keep a pointer i into s. Walk t; whenever t[j] == s[i], advance i.",
        "s is a subsequence exactly when i reaches the end of s.",
    ],
    opt=("O(|t|)", "O(1)", "One pass over t with a pointer into s."),
    editorial=(
        "## The one thing this teaches\n**Greedy matching is safe for subsequences.** If `s[i]` "
        "can be matched at several positions of `t`, matching it at the *earliest* leaves the "
        "most of `t` for the rest of `s`, so there is never a reason to wait.\n\n"
        "## Approach\n```java\nint i = 0;\nfor (int j = 0; j < t.length() && i < s.length(); j++)\n"
        "    if (s.charAt(i) == t.charAt(j)) i++;\nreturn i == s.length() ? \"YES\" : \"NO\";\n```\n\n"
        "## The follow-up\nWith a *billion* different `s` queries against one `t`, one pass per query "
        "is too slow. Precompute, for each letter, the sorted list of its positions in `t`, and "
        "match each character of `s` by binary-searching for the first position after the "
        "previous match: O(|s| log |t|) per query."
    ),
    py='''
def solve(s, t):
    i = 0
    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1
    return "YES" if i == len(s) else "NO"
''',
    java='''
    static String solve(String s, String t) {
        int i = 0;
        for (int j = 0; j < t.length() && i < s.length(); j++)
            if (s.charAt(i) == t.charAt(j)) i++;
        return i == s.length() ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "abc\nahbgdc\n"), ("Example 2", "axc\nahbgdc\n")],
    hidden=[
        ("Needs more copies than t has", "aaa\naa\n"),
        ("Single letter in the middle", "b\nabc\n"),
        ("Every other letter", "ace\nabcde\n"),
        ("Equal strings", "abc\nabc\n"),
    ],
    expl=[
        "`a`, `b`, `c` appear in that order in `ahbgdc`.",
        "There is no `x` in `t`.",
    ],
    prereqs=[
        ("two_pointers", "One pointer per string, moving forward only; the text pointer always advances."),
        ("greedy", "Matching each character at its earliest possible position never rules out a later match."),
    ],
)

_p(
    "isomorphic-strings", "Isomorphic Strings", "Easy",
    topics=["Strings", "Hashing"], subtopics=["Hashing"], companies=["LinkedIn", "Google"],
    shape="str2", ret="String", todo="map s→t and t→s; any conflict in either direction means NO",
    description=(
        "Two strings of equal length are **isomorphic** if the characters of `s` can be replaced to "
        "get `t`, where every occurrence of a character is replaced by the same character and no "
        "two different characters map to the same one.\n\n"
        "### Input\n- Line 1: `s`.\n- Line 2: `t` (same length).\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |s| = |t| ≤ 5·10^4\nBoth consist of lowercase English letters.",
    hints=[
        "Record, for each character of s, which character of t it maps to. A second, different target is a conflict.",
        "One map is not enough: `ab` → `cc` passes the s→t check but maps two letters to one.",
        "Keep a second map t→s, or check that the mapping's targets are all distinct.",
    ],
    opt=("O(n)", "O(1)", "Two 26-slot arrays; one pass comparing each position."),
    editorial=(
        "## The one thing this teaches\n**A bijection needs checking both ways.** The condition is "
        "that the mapping is a function (each `s` letter has one image) *and* injective (no two "
        "`s` letters share an image). Each direction is one lookup table.\n\n"
        "## Approach\n```java\nint[] st = new int[26], ts = new int[26];   // 0 = unmapped, else letter + 1\n"
        "for (int i = 0; i < n; i++) {\n"
        "    int a = s.charAt(i) - 'a', b = t.charAt(i) - 'a';\n"
        "    if (st[a] == 0 && ts[b] == 0) { st[a] = b + 1; ts[b] = a + 1; }\n"
        "    else if (st[a] != b + 1 || ts[b] != a + 1) return \"NO\";\n}\nreturn \"YES\";\n```\n\n"
        "## Another way to see it\nReplace every character by the index of its *first* occurrence: "
        "`paper` → `0 1 0 3 4`, `title` → `0 1 0 3 4`. Two strings are isomorphic exactly when "
        "those patterns match — a canonical form, the same trick as sorting letters for anagrams."
    ),
    py='''
def solve(s, t):
    st, ts = {}, {}
    for a, b in zip(s, t):
        if st.get(a, b) != b or ts.get(b, a) != a:
            return "NO"
        st[a] = b
        ts[b] = a
    return "YES"
''',
    java='''
    static String solve(String s, String t) {
        int[] st = new int[26], ts = new int[26];
        for (int i = 0; i < s.length(); i++) {
            int a = s.charAt(i) - 'a', b = t.charAt(i) - 'a';
            if (st[a] == 0 && ts[b] == 0) { st[a] = b + 1; ts[b] = a + 1; }
            else if (st[a] != b + 1 || ts[b] != a + 1) return "NO";
        }
        return "YES";
    }
''',
    examples=[("Example 1", "egg\nadd\n"), ("Example 2", "foo\nbar\n")],
    hidden=[
        ("Longer match", "paper\ntitle\n"),
        ("Fails only the reverse check", "ab\naa\n"),
        ("Crossed pairs", "badc\nbaba\n"),
        ("Single letters", "a\nb\n"),
    ],
    expl=[
        "`e→a`, `g→d`, consistently in both directions.",
        "`o` would have to map to both `a` and `r`.",
    ],
    prereqs=[
        ("hashing", "Two lookup tables, one per direction, so the mapping is checked to be a bijection."),
        ("canonical", "Each string reduces to the pattern of first-occurrence indices; isomorphic strings share it."),
    ],
)

_p(
    "longest-palindrome-build", "Longest Palindrome You Can Build", "Easy",
    topics=["Strings", "Hashing"], subtopics=["Counting"], companies=["Google"],
    shape="str", ret="int", todo="count letters; use every pair, plus one leftover letter for the centre",
    description=(
        "Using the letters of `s` (each at most once), what is the length of the longest "
        "palindrome you can build? Letters are **case-sensitive**: `A` and `a` are different.\n\n"
        "### Input\nOne line: `s`.\n\n### Output\nThe maximum length."
    ),
    constraints="1 ≤ |s| ≤ 2000\ns consists of English letters.",
    hints=[
        "You do not need to build it — only to know which letters could be placed.",
        "A palindrome is pairs mirrored around a centre. Every pair of equal letters can be used.",
        "At most one letter can sit alone in the middle. Add 1 if any letter was left over.",
    ],
    opt=("O(n)", "O(1)", "One counting pass over a 52-letter alphabet."),
    editorial=(
        "## The one thing this teaches\n**Answer the question the structure asks, not the one it "
        "suggests.** \"Longest palindrome\" sounds like search. But a palindrome is just mirrored "
        "pairs plus an optional centre, so the answer depends only on letter *counts*.\n\n"
        "## Approach\n```java\nint[] count = new int[128];\nfor (char c : s.toCharArray()) count[c]++;\n"
        "int len = 0;\nboolean odd = false;\nfor (int c : count) {\n"
        "    len += c / 2 * 2;\n    if (c % 2 == 1) odd = true;\n}\nreturn len + (odd ? 1 : 0);\n```\n\n"
        "## The detail\nA letter occurring 5 times contributes 4 to the pairs, not 0 — odd counts "
        "are not wasted, only their last copy is. And only *one* leftover can be the centre, "
        "however many letters had odd counts."
    ),
    py='''
def solve(s):
    count = Counter(s)
    length = sum(c // 2 * 2 for c in count.values())
    if any(c % 2 == 1 for c in count.values()):
        length += 1
    return length
''',
    java='''
    static int solve(String s) {
        int[] count = new int[128];
        for (int i = 0; i < s.length(); i++) count[s.charAt(i)]++;
        int len = 0;
        boolean odd = false;
        for (int c : count) {
            len += c / 2 * 2;
            if (c % 2 == 1) odd = true;
        }
        return len + (odd ? 1 : 0);
    }
''',
    examples=[("Example 1", "abccccdd\n"), ("Example 2", "a\n"),],
    hidden=[
        ("Case matters", "Aa\n"),
        ("All pairs", "aabbcc\n"),
        ("All distinct", "abc\n"),
        ("Odd count is not wasted", "zzzzz\n"),
    ],
    expl=[
        "`dccaccd`: pairs of `c`, `c`, `d` around one `a` — length 7.",
        "A single letter is a palindrome.",
    ],
    prereqs=[
        ("hashing", "Counting letters is all the problem needs; the palindrome itself is never constructed."),
        ("math_digits", "Integer division by 2 splits each count into usable pairs and a possible leftover."),
    ],
)

_p(
    "reverse-words", "Reverse Words in a Sentence", "Medium",
    topics=["Strings"], subtopics=["Traversal", "Two Pointers"], companies=["Microsoft", "Apple"],
    shape="line", ret="String", todo="split on runs of spaces, reverse the words, join with single spaces",
    description=(
        "Reverse the order of the **words** in a sentence. Words are separated by one or more "
        "spaces, and the sentence may have leading or trailing spaces. Print the words in reverse "
        "order separated by exactly one space.\n\n"
        "### Input\nOne line: the sentence.\n\n### Output\nThe reversed sentence."
    ),
    constraints="1 ≤ |s| ≤ 10^4\ns contains letters, digits and spaces, and at least one word.",
    hints=[
        "Splitting on a single space produces empty strings between repeated spaces.",
        "In Java, `s.trim().split(\"\\\\s+\")` splits on runs of whitespace after removing the ends.",
        "Without split: scan from the end, find each word's boundaries, and append it.",
    ],
    opt=("O(n)", "O(n)", "One scan to find words and one to build the output."),
    editorial=(
        "## The one thing this teaches\n**Tokenising is where string bugs live.** Reversing a list "
        "of words is trivial; producing that list correctly from `\"  the sky   is blue \"` is "
        "the actual problem.\n\n"
        "## Approach — scan from the end\n```java\nStringBuilder out = new StringBuilder();\n"
        "int i = s.length() - 1;\nwhile (i >= 0) {\n"
        "    while (i >= 0 && s.charAt(i) == ' ') i--;       // skip spaces\n"
        "    if (i < 0) break;\n    int end = i;\n"
        "    while (i >= 0 && s.charAt(i) != ' ') i--;       // find the word's start\n"
        "    if (out.length() > 0) out.append(' ');\n"
        "    out.append(s, i + 1, end + 1);\n}\n```\n\n"
        "## Why `split(\" \")` fails\n`\"a  b\".split(\" \")` is `[\"a\", \"\", \"b\"]`: the empty "
        "token between two spaces survives, and joining gives two spaces. `split(\"\\\\s+\")` "
        "treats a run as one separator, but a *leading* run still yields a leading empty token — "
        "which is why the `trim()` comes first.\n\n"
        "## The in-place version\nWith a mutable character array: reverse the whole array, then "
        "reverse each word back. O(1) extra space, and the classic follow-up."
    ),
    py='''
def solve(s):
    return " ".join(reversed(s.split()))
''',
    java='''
    static String solve(String s) {
        StringBuilder out = new StringBuilder();
        int i = s.length() - 1;
        while (i >= 0) {
            while (i >= 0 && s.charAt(i) == ' ') i--;
            if (i < 0) break;
            int end = i;
            while (i >= 0 && s.charAt(i) != ' ') i--;
            if (out.length() > 0) out.append(' ');
            out.append(s, i + 1, end + 1);
        }
        return out.toString();
    }
''',
    examples=[("Example 1", "the sky is blue\n"), ("Example 2", "  hello world  \n")],
    hidden=[
        ("Runs of spaces", "a good   example\n"),
        ("Single word", "word\n"),
        ("Single word with padding", "   padded   \n"),
        ("Digits are words", "1 22 333\n"),
    ],
    expl=[
        "Four words, in reverse order.",
        "Leading and trailing spaces disappear; one space between the two words.",
    ],
    prereqs=[
        ("string_basics", "Finding word boundaries by scanning for runs of spaces, and building output with a StringBuilder."),
        ("two_pointers", "Each word is the span between two indices found by scanning backwards."),
    ],
)

_p(
    "string-to-integer", "String to Integer (atoi)", "Medium",
    topics=["Strings", "Math"], subtopics=["State Machine"], companies=["Amazon", "Meta", "Microsoft"],
    shape="line", ret="long", todo="skip spaces, read one optional sign, read digits, clamp to the 32-bit range",
    description=(
        "Parse an integer from the start of a line, the way C's `atoi` does:\n\n"
        "1. Skip leading spaces.\n"
        "2. Read one optional `+` or `-`.\n"
        "3. Read digits until a non-digit or the end of the line. No digits means the value is 0.\n"
        "4. Clamp the result to the 32-bit range `[−2³¹, 2³¹ − 1]`.\n\n"
        "### Input\nOne line.\n\n### Output\nThe parsed integer."
    ),
    constraints="0 ≤ |s| ≤ 200\ns contains English letters, digits, spaces, '+', '-' and '.'.",
    hints=[
        "Do the four steps in order with one index moving forward — each step stops where the next begins.",
        "Only ONE sign is allowed: `+-12` is 0, because after the `+`, `-` is not a digit.",
        "Accumulate in a long and stop once the value passes 2³¹; the clamp handles the rest.",
    ],
    opt=("O(n)", "O(1)", "A single left-to-right scan."),
    editorial=(
        "## The one thing this teaches\n**Write a parser as phases.** Every rule in the statement "
        "is a phase — spaces, sign, digits — and each phase is a `while` or `if` that advances one "
        "shared index and stops exactly where the next phase starts. Most wrong answers merge "
        "phases and accept `\" - 5\"` or `\"12 34\"` as something.\n\n"
        "## Approach\n```java\nint i = 0, n = s.length();\n"
        "while (i < n && s.charAt(i) == ' ') i++;\nint sign = 1;\n"
        "if (i < n && (s.charAt(i) == '+' || s.charAt(i) == '-')) sign = s.charAt(i++) == '-' ? -1 : 1;\n"
        "long val = 0;\nwhile (i < n && Character.isDigit(s.charAt(i))) {\n"
        "    val = val * 10 + (s.charAt(i++) - '0');\n    if (val > (1L << 31)) break;   // already out of range\n}\n"
        "val *= sign;\nreturn Math.max(Integer.MIN_VALUE, Math.min(Integer.MAX_VALUE, val));\n```\n\n"
        "## Overflow, deliberately\nA `long` holds far more than 2³¹, but not arbitrarily many "
        "digits — `\"99999999999999999999\"` overflows a `long` too. Breaking out once the value "
        "exceeds 2³¹ keeps it small; the clamp then maps it to the boundary. Without `long`, the "
        "check is `val > (Integer.MAX_VALUE − d) / 10` *before* multiplying."
    ),
    py='''
def solve(s):
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        if s[i] == "-":
            sign = -1
        i += 1
    val = 0
    while i < n and "0" <= s[i] <= "9":
        val = val * 10 + (ord(s[i]) - 48)
        i += 1
        if val > 2 ** 31:
            break
    val *= sign
    return max(-2 ** 31, min(2 ** 31 - 1, val))
''',
    java='''
    static long solve(String s) {
        int i = 0, n = s.length();
        while (i < n && s.charAt(i) == ' ') i++;
        int sign = 1;
        if (i < n && (s.charAt(i) == '+' || s.charAt(i) == '-')) {
            if (s.charAt(i) == '-') sign = -1;
            i++;
        }
        long val = 0;
        while (i < n && s.charAt(i) >= '0' && s.charAt(i) <= '9') {
            val = val * 10 + (s.charAt(i) - '0');
            i++;
            if (val > (1L << 31)) break;
        }
        val *= sign;
        return Math.max(Integer.MIN_VALUE, Math.min(Integer.MAX_VALUE, val));
    }
''',
    examples=[("Example 1", "42\n"), ("Example 2", "   -042abc\n")],
    hidden=[
        ("Letters first", "words and 987\n"),
        ("Below the range", "-91283472332\n"),
        ("Two signs", "+-12\n"),
        ("Just above the range", "2147483648\n"),
        ("Stops at the first space", "  +0 123\n"),
    ],
    expl=[
        "Plain digits.",
        "Spaces skipped, `-` read, `042` read as 42, stopped at `a`.",
    ],
    prereqs=[
        ("overflow", "Accumulating in a long and clamping, so an oversized number cannot wrap around."),
        ("string_basics", "Classifying characters one at a time while a single index moves through the phases."),
    ],
)

_p(
    "happy-number", "Happy Number", "Easy",
    topics=["Hashing", "Math"], subtopics=["Hash Set", "Digits"], companies=["Airbnb", "Uber"],
    shape="n", ret="String", todo="repeat the digit-square sum, remembering values seen, until 1 or a repeat",
    description=(
        "Start from `n` and repeatedly replace the number by the **sum of the squares of its "
        "digits**. If this reaches 1, `n` is *happy*. Otherwise the sequence loops forever.\n\n"
        "### Input\nOne integer `n`.\n\n### Output\n`YES` if `n` is happy, otherwise `NO`."
    ),
    constraints="1 ≤ n ≤ 2^31 − 1",
    hints=[
        "The sequence either reaches 1 or repeats a value — and once it repeats, it cycles forever.",
        "Keep a set of values already seen. Stop at 1 (YES) or at a value seen before (NO).",
        "The values quickly fall below 243 (the digit-square sum of 999), so the set stays tiny.",
    ],
    opt=("O(log n)", "O(1)", "After the first step every value is below a few hundred, so the loop is short and the set is bounded."),
    editorial=(
        "## The one thing this teaches\n**A hash set detects a cycle in any sequence.** \"Loops "
        "forever\" is not something you can wait for; \"produced a value it produced before\" "
        "is, and a set answers it in O(1).\n\n"
        "## Approach\n```java\nSet<Long> seen = new HashSet<>();\n"
        "while (n != 1 && seen.add(n)) n = next(n);   // add returns false for a repeat\n"
        "return n == 1 ? \"YES\" : \"NO\";\n```\n\n"
        "## Why it must end\nA number with d digits maps to at most 81·d, which for d ≥ 4 is far "
        "smaller than the number itself. So every sequence drops below 1000 within a step or two "
        "and stays there, where only finitely many values exist — a repeat is forced.\n\n"
        "## The O(1)-space version\nThe sequence is a linked list whose `next` is the digit-square "
        "function, so Floyd's slow/fast pointers find the cycle without a set: move `slow` one "
        "step and `fast` two, and see whether they meet at 1."
    ),
    py='''
def solve(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return "YES" if n == 1 else "NO"
''',
    java='''
    static long next(long n) {
        long s = 0;
        while (n > 0) { long d = n % 10; s += d * d; n /= 10; }
        return s;
    }

    static String solve(long n) {
        Set<Long> seen = new HashSet<>();
        while (n != 1 && seen.add(n)) n = next(n);
        return n == 1 ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "19\n"), ("Example 2", "2\n")],
    hidden=[
        ("One is happy", "1\n"),
        ("Seven", "7\n"),
        ("Four cycles", "4\n"),
        ("A power of ten", "100\n"),
    ],
    expl=[
        "19 → 82 → 68 → 100 → 1.",
        "2 → 4 → 16 → 37 → 58 → 89 → 145 → 42 → 20 → 4, a cycle that never reaches 1.",
    ],
    prereqs=[
        ("visited_set", "A set of values already produced; the first repeat proves the sequence cycles."),
        ("math_digits", "Taking digits off with % 10 and / 10 to compute the next value."),
    ],
)

_p(
    "ransom-note", "Ransom Note", "Easy",
    topics=["Hashing", "Strings"], subtopics=["Counting"], companies=["Microsoft", "Apple"],
    shape="str2", ret="String", todo="count the magazine's letters, then spend one per letter of the note",
    description=(
        "Can the note be written using letters cut from the magazine? Each letter of the magazine "
        "can be used at most once.\n\n"
        "### Input\n- Line 1: the note.\n- Line 2: the magazine.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |note|, |magazine| ≤ 10^5\nBoth consist of lowercase English letters.",
    hints=[
        "Order does not matter at all — only how many of each letter is available.",
        "Count the magazine's letters into a 26-slot array.",
        "Walk the note, decrementing; a count going below zero means a missing letter.",
    ],
    opt=("O(|note| + |magazine|)", "O(1)", "Two passes and a fixed 26-slot array."),
    editorial=(
        "## The one thing this teaches\n**A count array is a bag.** When a question is about "
        "*availability* — enough of each item, in any order — a multiset is the model, and for "
        "26 letters the multiset is an `int[26]`.\n\n"
        "## Approach\n```java\nint[] have = new int[26];\n"
        "for (char c : magazine.toCharArray()) have[c - 'a']++;\n"
        "for (char c : note.toCharArray()) if (--have[c - 'a'] < 0) return \"NO\";\nreturn \"YES\";\n```\n\n"
        "## Why not `indexOf` and delete\nFinding each note letter in the magazine and removing it "
        "is O(|note| · |magazine|) and allocates a new string per deletion. The counts discard "
        "exactly the information — positions — that the question never needed."
    ),
    py='''
def solve(s, t):
    have = Counter(t)
    for ch in s:
        have[ch] -= 1
        if have[ch] < 0:
            return "NO"
    return "YES"
''',
    java='''
    static String solve(String note, String magazine) {
        int[] have = new int[26];
        for (int i = 0; i < magazine.length(); i++) have[magazine.charAt(i) - 'a']++;
        for (int i = 0; i < note.length(); i++)
            if (--have[note.charAt(i) - 'a'] < 0) return "NO";
        return "YES";
    }
''',
    examples=[("Example 1", "aa\naab\n"), ("Example 2", "aa\nab\n")],
    hidden=[
        ("Missing letter", "a\nb\n"),
        ("Any order", "abc\ncba\n"),
        ("Exactly enough", "aab\nbaa\n"),
        ("Magazine too short", "zz\nz\n"),
    ],
    expl=[
        "The magazine has two `a`s.",
        "Only one `a` is available.",
    ],
    prereqs=[
        ("hashing", "A 26-slot count array as a multiset of available letters."),
        ("string_basics", "Mapping each character to an index with c − 'a'."),
    ],
)

_p(
    "unique-occurrences", "Unique Number of Occurrences", "Easy",
    topics=["Hashing", "Arrays"], subtopics=["Counting", "Hash Set"], companies=["Amazon"],
    shape="arr", ret="String", todo="count each value, then check that no two values share a count",
    description=(
        "Is the number of occurrences of each value in the array **unique** — no two different "
        "values occurring the same number of times?\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 1000\n-1000 ≤ a[i] ≤ 1000",
    hints=[
        "First count how often each value occurs.",
        "Then the question is about those counts: are they all different?",
        "Put the counts into a set. They are unique exactly when the set is as large as the number of distinct values.",
    ],
    opt=("O(n)", "O(n)", "One counting pass, then one pass over the distinct values."),
    editorial=(
        "## The one thing this teaches\n**Count, then count the counts.** Many frequency "
        "questions have two levels: the values, and then the frequencies of those values' "
        "frequencies. Each level is one map or set.\n\n"
        "## Approach\n```java\nMap<Integer, Integer> freq = new HashMap<>();\n"
        "for (int x : a) freq.merge(x, 1, Integer::sum);\n"
        "Set<Integer> counts = new HashSet<>(freq.values());\n"
        "return counts.size() == freq.size() ? \"YES\" : \"NO\";\n```\n\n"
        "## The size comparison\n`new HashSet<>(freq.values())` removes duplicate counts, so "
        "it shrinks exactly when two values share a frequency. Comparing sizes turns \"are these "
        "all different?\" into one line — the same idea as `Contains Duplicate`, one level up."
    ),
    py='''
def solve(a):
    freq = Counter(a)
    return "YES" if len(set(freq.values())) == len(freq) else "NO"
''',
    java='''
    static String solve(int[] a) {
        Map<Integer, Integer> freq = new HashMap<>();
        for (int x : a) freq.merge(x, 1, Integer::sum);
        Set<Integer> counts = new HashSet<>(freq.values());
        return counts.size() == freq.size() ? "YES" : "NO";
    }
''',
    examples=[("Example 1", "6\n1 2 2 1 1 3\n"), ("Example 2", "2\n1 2\n")],
    hidden=[
        ("Negatives and zero", "10\n-3 0 1 -3 1 1 1 -3 10 0\n"),
        ("Single element", "1\n5\n"),
        ("Two values, same count", "4\n7 7 8 8\n"),
    ],
    expl=[
        "1 occurs 3 times, 2 twice and 3 once — all different.",
        "Both values occur once.",
    ],
    prereqs=[
        ("hashing", "A frequency map of the values, then a set of the frequencies."),
        ("canonical", "Collapsing duplicates into a set and comparing sizes to detect a repeat."),
    ],
)

_p(
    "pairs-with-difference-k", "Distinct Pairs With Difference K", "Medium",
    topics=["Hashing", "Arrays"], subtopics=["Hashing", "Complement Lookup"], companies=["Amazon", "Salesforce"],
    shape="arr_k", ret="long", todo="count the values; for k > 0 check x + k exists, for k = 0 check x repeats",
    description=(
        "Count the **distinct pairs of values** `(x, y)` in the array with `y − x = k`. A pair is "
        "counted once however many times its values occur, and it must use two different "
        "positions.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n### Output\nThe number of distinct pairs."
    ),
    constraints="1 ≤ n ≤ 10^4\n-10^7 ≤ a[i] ≤ 10^7\n0 ≤ k ≤ 10^7",
    hints=[
        "Duplicates do not create new pairs, so work with the distinct values and how often each occurs.",
        "For k > 0, each distinct x forms a pair exactly when x + k is also present.",
        "For k = 0, the pair (x, x) needs x at two positions: count values occurring at least twice.",
    ],
    opt=("O(n)", "O(n)", "One pass to count, one pass over the distinct values with O(1) lookups."),
    editorial=(
        "## The one thing this teaches\n**Look up the partner — and notice when the partner is "
        "yourself.** For k > 0, the partner of `x` is `x + k`, a single hash lookup. For k = 0, "
        "the partner is `x` itself, and \"is it in the set?\" is always yes — the right question "
        "becomes \"does it occur twice?\"\n\n"
        "## Approach\n```java\nMap<Long, Integer> freq = new HashMap<>();\n"
        "for (int x : a) freq.merge((long) x, 1, Integer::sum);\nlong pairs = 0;\n"
        "for (Map.Entry<Long, Integer> e : freq.entrySet()) {\n"
        "    if (k == 0) { if (e.getValue() >= 2) pairs++; }\n"
        "    else if (freq.containsKey(e.getKey() + k)) pairs++;\n}\n```\n\n"
        "## Counting each pair once\nLooking only for `x + k` — never `x − k` — means each pair is "
        "found from its smaller value only. Checking both directions double-counts. And iterating "
        "over *distinct* values is what makes `[1, 1, 3]` with k = 2 one pair rather than two.\n\n"
        "The sorted two-pointer version is O(n log n) with O(1) extra space, and has to skip "
        "duplicates by hand."
    ),
    py='''
def solve(a, k):
    freq = Counter(a)
    if k == 0:
        return sum(1 for c in freq.values() if c >= 2)
    return sum(1 for x in freq if x + k in freq)
''',
    java='''
    static long solve(int[] a, long k) {
        Map<Long, Integer> freq = new HashMap<>();
        for (int x : a) freq.merge((long) x, 1, Integer::sum);
        long pairs = 0;
        for (Map.Entry<Long, Integer> e : freq.entrySet()) {
            if (k == 0) { if (e.getValue() >= 2) pairs++; }
            else if (freq.containsKey(e.getKey() + k)) pairs++;
        }
        return pairs;
    }
''',
    examples=[("Example 1", "5 2\n3 1 4 1 5\n"), ("Example 2", "5 1\n1 2 3 4 5\n")],
    hidden=[
        ("k is zero", "5 0\n1 3 1 5 4\n"),
        ("No pairs", "3 10\n1 2 3\n"),
        ("k is zero, several repeats", "6 0\n2 2 2 3 3 4\n"),
        ("Negative values", "4 3\n-1 2 5 -4\n"),
    ],
    expl=[
        "`(1, 3)` and `(3, 5)`. The second 1 does not make another pair.",
        "`(1,2)`, `(2,3)`, `(3,4)`, `(4,5)`.",
    ],
    prereqs=[
        ("complement", "The partner of x is x + k, found with one hash lookup."),
        ("hashing", "A frequency map, needed because k = 0 asks whether a value occurs twice rather than whether it exists."),
    ],
)
