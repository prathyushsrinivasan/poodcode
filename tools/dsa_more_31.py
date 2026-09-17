# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 31 — contribution counting, string borders, bounds and small structures.
#
#   sum-odd-length-subarrays        each element sits in ⌈(i + 1)(n − i) / 2⌉ odd-length subarrays
#   maximum-number-of-balloons      the scarcest letter, adjusted for letters used twice
#   shortest-palindrome             KMP on s + '#' + reverse(s) finds the longest palindromic prefix
#   count-binary-substrings         adjacent run lengths contribute min(left, right)
#   count-subarrays-fixed-bounds    track the last minK, last maxK and last out-of-range index
#   search-rotated-duplicates       binary search; shrink both ends when they equal the middle
#   kth-missing-positive            a[i] − (i + 1) numbers are missing before index i
#   min-add-parentheses-valid       unmatched ')' plus unmatched '('
#   smallest-infinite-set           a pointer for the untouched tail plus a set of returned numbers
#   remove-nodes-greater-right      keep a node only if it is ≥ everything after it
#   cousins-in-binary-tree          same depth, different parents
#   last-stone-weight-ii            smashing stones is splitting them into two groups
# ===========================================================================

_p(
    "sum-odd-length-subarrays", "Sum of All Odd-Length Subarrays", "Easy",
    topics=["Arrays", "Math"], subtopics=["Contribution Technique"], companies=["LinkedIn"],
    shape="arr", ret="long", todo="a[i] belongs to (i + 1)(n − i) subarrays, and ⌈that / 2⌉ of them have odd length",
    description=(
        "Print the sum of the elements of every **odd-length** contiguous subarray (each "
        "subarray's sum added once).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe total."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 1000",
    hints=[
        "Enumerating odd-length subarrays and summing each is O(n³), or O(n²) with prefix sums.",
        "Instead, ask how many odd-length subarrays contain a[i]: its contribution is a[i] times that count.",
        "There are (i + 1) choices of start and (n − i) of end — (i + 1)(n − i) subarrays in all, and the odd-length ones are ((i + 1)(n − i) + 1) / 2.",
    ],
    opt=("O(n)", "O(1)", "One formula per element."),
    editorial=(
        "## The one thing this teaches\n**Swap the order of summation.** \"Sum over subarrays of "
        "the sum of elements\" equals \"sum over elements of (element × number of subarrays "
        "containing it)\". The second form needs no enumeration, only counting.\n\n"
        "## Approach\n```java\nlong total = 0;\nfor (int i = 0; i < n; i++) {\n"
        "    long containing = (long) (i + 1) * (n - i);\n    long odd = (containing + 1) / 2;\n"
        "    total += odd * a[i];\n}\n```\n\n"
        "## Why half, rounded up\nA start `s ≤ i` and an end `e ≥ i` give an odd length exactly "
        "when `s` and `e` have the same parity. With p = i + 1 starts and q = n − i ends, that is "
        "`⌈p/2⌉·⌈q/2⌉ + ⌊p/2⌋·⌊q/2⌋` pairs — which always equals `⌈p·q / 2⌉`.\n\n"
        "## Walkthrough: 1 4 2 5 3\nCounts of containing subarrays: 5, 8, 9, 8, 5 → odd ones 3, "
        "4, 5, 4, 3. Total `1·3 + 4·4 + 2·5 + 5·4 + 3·3 = 58`."
    ),
    py='''
def solve(a):
    total = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if (j - i) % 2 == 0:
                total += s
    return total
''',
    java='''
    static long solve(int[] a) {
        int n = a.length;
        long total = 0;
        for (int i = 0; i < n; i++) {
            long containing = (long) (i + 1) * (n - i);
            total += (containing + 1) / 2 * a[i];
        }
        return total;
    }
''',
    examples=[("Example 1", "5\n1 4 2 5 3\n"), ("Example 2", "2\n1 2\n"), ("Example 3", "3\n10 11 12\n")],
    hidden=[
        ("Single element", "1\n7\n"),
        ("All ones", "4\n1 1 1 1\n"),
        ("Six elements", "6\n1 2 3 4 5 6\n"),
        ("Large values", "5\n1000 1000 1000 1000 1000\n"),
    ],
    expl=[
        "Five single elements (15), three triples (7 + 11 + 10 = 28) and the whole array (15): 58.",
        "Only the single elements have odd length: 1 + 2.",
        "10 + 11 + 12 + (10 + 11 + 12) = 66.",
    ],
    prereqs=[
        ("big_o", "Replacing enumeration of subarrays with a per-element count."),
        ("math_digits", "Counting start–end pairs and halving by parity."),
    ],
)

_p(
    "maximum-number-of-balloons", "Maximum Number of Balloons", "Easy",
    topics=["Hashing", "Strings"], subtopics=["Counting"], companies=["Microsoft", "Wayfair"],
    shape="str", ret="int", todo="count letters; the answer is the minimum of b, a, n and l/2, o/2",
    description=(
        "Using each character of `text` at most once, how many copies of the word `balloon` can "
        "you form?\n\n"
        "### Input\nOne line: `text`.\n\n"
        "### Output\nThe maximum number of copies."
    ),
    constraints="1 ≤ |text| ≤ 10^4\nLowercase English letters",
    hints=[
        "Only the letters b, a, l, o and n matter.",
        "Each copy needs one b, one a, one n — but two l's and two o's.",
        "The answer is limited by the scarcest requirement: min(b, a, n, l / 2, o / 2).",
    ],
    opt=("O(n)", "O(1)", "One counting pass over a 26-letter table."),
    editorial=(
        "## The one thing this teaches\n**A bottleneck is the minimum of supply ÷ demand.** Each "
        "letter can support `count / needed` copies; the word needs all of them, so the smallest "
        "ratio wins.\n\n"
        "## Approach\n```java\nint[] c = new int[26];\nfor (char ch : text.toCharArray()) c[ch - 'a']++;\n"
        "return Math.min(Math.min(c['b' - 'a'], c['a' - 'a']),\n"
        "       Math.min(c['n' - 'a'], Math.min(c['l' - 'a'] / 2, c['o' - 'a'] / 2)));\n```\n\n"
        "## Generalising\nFor any target word, count the target's letters too and take "
        "`min over letters of have[x] / need[x]`. Hard-coding the twos is fine for one word; the "
        "general form avoids mistakes when the word changes.\n\n"
        "## Integer division\n`l / 2` rounds down: three l's support only one copy."
    ),
    py='''
def solve(s):
    left = Counter(s)
    copies = 0
    while True:
        for ch in "balloon":
            if left[ch] == 0:
                return copies
            left[ch] -= 1
        copies += 1
''',
    java='''
    static int solve(String text) {
        int[] c = new int[26];
        for (int i = 0; i < text.length(); i++) c[text.charAt(i) - 'a']++;
        return Math.min(Math.min(c['b' - 'a'], c['a' - 'a']),
               Math.min(c['n' - 'a'], Math.min(c['l' - 'a'] / 2, c['o' - 'a'] / 2)));
    }
''',
    examples=[("Example 1", "nlaebolko\n"), ("Example 2", "loonbalxballpoon\n"), ("Example 3", "leetcode\n")],
    hidden=[
        ("Exactly one", "balloon\n"),
        ("Odd l count", "balllooonn\n"),
        ("Many copies", "balloonballoonballoonballoon\n"),
        ("Missing b", "alloonalloon\n"),
    ],
    expl=[
        "One of each letter, with two l's and two o's.",
        "Enough for two copies.",
        "No b, a or n.",
    ],
    prereqs=[
        ("hashing", "A fixed-size letter count."),
        ("math_digits", "Integer division as \"how many full copies\"."),
    ],
)

_p(
    "shortest-palindrome", "Shortest Palindrome", "Hard",
    topics=["Strings"], subtopics=["KMP", "Palindromes"], companies=["Google", "Amazon"],
    shape="str", ret="String", todo="the longest palindromic prefix has length pi[last] of s + '#' + reverse(s); prepend the reverse of the rest",
    description=(
        "Add characters **only in front of** `s` to make it a palindrome. Print the shortest "
        "palindrome that can be made.\n\n"
        "### Input\nOne line: `s`.\n\n"
        "### Output\nThe shortest palindrome."
    ),
    constraints="1 ≤ |s| ≤ 5·10^4\nLowercase English letters",
    hints=[
        "Whatever you add, the original s must end the palindrome. The part of s that can stay unmirrored is its longest palindromic prefix.",
        "If s[0..L) is a palindrome, the answer is reverse(s[L..]) + s. Checking each prefix directly is O(n²).",
        "A palindromic prefix of s is a prefix of s that equals a suffix of reverse(s). The KMP prefix function of s + '#' + reverse(s) gives the longest such match in O(n).",
    ],
    opt=("O(n)", "O(n)", "One prefix-function computation over a string of length 2n + 1."),
    editorial=(
        "## The one thing this teaches\n**Rephrase a palindrome condition as a border.** "
        "\"`s[0..L)` is a palindrome\" means `s[0..L)` equals the reverse of itself — the last L "
        "characters of `reverse(s)`. So the question becomes \"longest prefix of s that is also a "
        "suffix of reverse(s)\", which is exactly what the prefix function measures.\n\n"
        "## Approach\n```java\nString rev = new StringBuilder(s).reverse().toString();\n"
        "String t = s + \"#\" + rev;                 // '#' stops a match from crossing over\n"
        "int[] pi = prefixFunction(t);\nint keep = pi[t.length() - 1];              // longest palindromic prefix\n"
        "return rev.substring(0, s.length() - keep) + s;\n```\n\n"
        "## Why the separator\nWithout `#`, a border could extend past the end of s into rev and "
        "report a length longer than s itself.\n\n"
        "## Walkthrough: aacecaaa\nThe longest palindromic prefix is `aacecaa` (7 characters). "
        "The leftover `a` is reversed and prepended: `a` + `aacecaaa` = `aaacecaaa`."
    ),
    py='''
def solve(s):
    for length in range(len(s), 0, -1):
        prefix = s[:length]
        if prefix == prefix[::-1]:
            return s[length:][::-1] + s
''',
    java='''
    static String solve(String s) {
        String rev = new StringBuilder(s).reverse().toString();
        String t = s + "#" + rev;
        int[] pi = new int[t.length()];
        for (int i = 1, k = 0; i < t.length(); i++) {
            while (k > 0 && t.charAt(i) != t.charAt(k)) k = pi[k - 1];
            if (t.charAt(i) == t.charAt(k)) k++;
            pi[i] = k;
        }
        int keep = pi[t.length() - 1];
        return rev.substring(0, s.length() - keep) + s;
    }
''',
    examples=[("Example 1", "aacecaaa\n"), ("Example 2", "abcd\n")],
    hidden=[
        ("Single character", "a\n"),
        ("Already a palindrome", "racecar\n"),
        ("Two different", "ab\n"),
        ("Repeating pattern", "abab\n"),
        ("Palindromic prefix after fallback", "aabba\n"),
    ],
    expl=[
        "aacecaa is already a palindrome; mirror the final a in front.",
        "Only a is a palindromic prefix, so dcb goes in front.",
    ],
    prereqs=[
        ("string_basics", "Palindromes, prefixes and reversal."),
        ("two_pointers", "The KMP prefix function's fallback pointer."),
    ],
)

_p(
    "count-binary-substrings", "Count Binary Substrings", "Easy",
    topics=["Strings"], subtopics=["Run-Length Grouping"], companies=["Helix", "Amazon"],
    shape="str", ret="int", todo="compress the string into run lengths; each adjacent pair of runs contributes min(left, right)",
    description=(
        "Count the non-empty substrings that have the same number of 0s and 1s, with all the 0s "
        "grouped together and all the 1s grouped together (such as `0011` or `10`). Substrings at "
        "different positions count separately.\n\n"
        "### Input\nOne line: a binary string `s`.\n\n"
        "### Output\nThe count."
    ),
    constraints="1 ≤ |s| ≤ 10^5",
    hints=[
        "A valid substring always straddles exactly one boundary between a run of 0s and a run of 1s.",
        "At a boundary between a run of length p and a run of length q, the valid substrings centred there have half-lengths 1, 2, …, min(p, q).",
        "Compute run lengths and add min(prev, cur) for each adjacent pair — keeping only the previous run's length.",
    ],
    opt=("O(n)", "O(1)", "One pass tracking the previous and current run lengths."),
    editorial=(
        "## The one thing this teaches\n**Compress into runs when the answer only depends on "
        "runs.** The positions of individual characters do not matter here — only how long each "
        "block of equal characters is and which blocks are neighbours.\n\n"
        "## Approach\n```java\nint prev = 0, cur = 1, count = 0;\nfor (int i = 1; i < n; i++) {\n"
        "    if (s.charAt(i) == s.charAt(i - 1)) cur++;\n"
        "    else { count += Math.min(prev, cur); prev = cur; cur = 1; }\n}\ncount += Math.min(prev, cur);\n```\n\n"
        "## Walkthrough: 00110011\nRuns 2, 2, 2, 2. Boundaries contribute min(2,2) three times: 6 "
        "— `0011`, `01`, `1100`, `10`, `0011`, `01`.\n\n"
        "## Why the last pair is added after the loop\nThe loop adds a pair only when a run ends "
        "at a change of character. The final run ends at the end of the string instead."
    ),
    py='''
def solve(s):
    count = 0
    for i in range(len(s)):
        for j in range(i + 2, len(s) + 1, 2):
            half = (j - i) // 2
            left, right = s[i:i + half], s[i + half:j]
            if len(set(left)) == 1 and len(set(right)) == 1 and left[0] != right[0]:
                count += 1
    return count
''',
    java='''
    static int solve(String s) {
        int prev = 0, cur = 1, count = 0;
        for (int i = 1; i < s.length(); i++) {
            if (s.charAt(i) == s.charAt(i - 1)) cur++;
            else { count += Math.min(prev, cur); prev = cur; cur = 1; }
        }
        return count + Math.min(prev, cur);
    }
''',
    examples=[("Example 1", "00110011\n"), ("Example 2", "10101\n")],
    hidden=[
        ("Single character", "0\n"),
        ("One boundary", "000111\n"),
        ("Growing runs", "0110001111\n"),
        ("No boundary", "1111\n"),
    ],
    expl=[
        "0011, 01, 1100, 10, 0011 and 01.",
        "10, 01, 10 and 01.",
    ],
    prereqs=[
        ("string_basics", "Grouping a string into runs of equal characters."),
        ("array_patterns", "Keeping only the previous group's size during a scan."),
    ],
)

_p(
    "count-subarrays-fixed-bounds", "Count Subarrays With Fixed Bounds", "Hard",
    topics=["Sliding Window", "Arrays"], subtopics=["Last Occurrence Tracking"], companies=["Google", "Amazon"],
    shape="arr_xy", ret="long", todo="for each right end, remember the last index of minK, of maxK and of an out-of-range value; add max(0, min(lastMin, lastMax) − lastBad)",
    description=(
        "Count the contiguous subarrays whose **minimum is exactly `minK`** and whose **maximum "
        "is exactly `maxK`**.\n\n"
        "### Input\n- Line 1: `n minK maxK`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe count."
    ),
    constraints="2 ≤ n ≤ 10^5\n1 ≤ a[i], minK, maxK ≤ 10^6",
    hints=[
        "Any element outside [minK, maxK] can never be inside a valid subarray — it splits the array.",
        "Fix the right end r. A valid subarray ending at r must start after the last bad index and at or before both the last minK and the last maxK.",
        "So the number of valid starts is max(0, min(lastMin, lastMax) − lastBad). Update the three indices as you scan.",
    ],
    opt=("O(n)", "O(1)", "Three remembered indices per step."),
    editorial=(
        "## The one thing this teaches\n**Count subarrays by their right end, using the latest "
        "positions of what matters.** A valid subarray ending at `r` needs a `minK` and a `maxK` "
        "inside it and no out-of-range value. The latest occurrences of those three things "
        "describe exactly which starts work.\n\n"
        "## Approach\n```java\nlong count = 0;\nint lastMin = -1, lastMax = -1, lastBad = -1;\n"
        "for (int r = 0; r < n; r++) {\n    if (a[r] < minK || a[r] > maxK) lastBad = r;\n"
        "    if (a[r] == minK) lastMin = r;\n    if (a[r] == maxK) lastMax = r;\n"
        "    count += Math.max(0, Math.min(lastMin, lastMax) - lastBad);\n}\n```\n\n"
        "## Reading the formula\nStarts must be in `(lastBad, min(lastMin, lastMax)]`. That "
        "interval has `min(lastMin, lastMax) − lastBad` integers, or none if a bad value is more "
        "recent than one of the bounds.\n\n"
        "## minK = maxK\nWhen both bounds are the same value, `lastMin` and `lastMax` update "
        "together and the formula counts runs of that value correctly."
    ),
    py='''
def solve(a, x, y):
    count = 0
    for i in range(len(a)):
        lo = hi = a[i]
        for j in range(i, len(a)):
            lo = min(lo, a[j])
            hi = max(hi, a[j])
            if lo < x or hi > y:
                break
            if lo == x and hi == y:
                count += 1
    return count
''',
    java='''
    static long solve(int[] a, long minK, long maxK) {
        long count = 0;
        int lastMin = -1, lastMax = -1, lastBad = -1;
        for (int r = 0; r < a.length; r++) {
            if (a[r] < minK || a[r] > maxK) lastBad = r;
            if (a[r] == minK) lastMin = r;
            if (a[r] == maxK) lastMax = r;
            count += Math.max(0, Math.min(lastMin, lastMax) - lastBad);
        }
        return count;
    }
''',
    examples=[("Example 1", "6 1 5\n1 3 5 2 7 5\n"), ("Example 2", "4 1 1\n1 1 1 1\n")],
    hidden=[
        ("Bounds at the ends", "3 1 3\n1 2 3\n"),
        ("Alternating bounds", "5 1 5\n5 1 5 1 5\n"),
        ("Bad values split", "7 2 4\n2 3 1 4 3 2 5\n"),
        ("Bounds never both present", "4 1 9\n1 2 3 4\n"),
    ],
    expl=[
        "[1, 3, 5] and [1, 3, 5, 2]; the 7 blocks anything longer.",
        "All 10 subarrays have minimum and maximum 1.",
    ],
    prereqs=[
        ("sliding_window", "Counting subarrays by their right end with remembered boundaries."),
        ("array_patterns", "Last-occurrence indices updated during a scan."),
    ],
)

_p(
    "search-rotated-duplicates", "Search in Rotated Sorted Array II", "Medium",
    topics=["Binary Search", "Arrays"], subtopics=["Rotated Array", "Duplicates"], companies=["LinkedIn", "Meta"],
    shape="arr_k", ret="String", todo="binary search; if a[lo], a[mid] and a[hi] are all equal, shrink both ends; otherwise one half is sorted — test the target against it",
    description=(
        "A non-decreasing array (which **may contain duplicates**) was rotated at an unknown "
        "point. Print `YES` if `target` is in the array, otherwise `NO`.\n\n"
        "### Input\n- Line 1: `n target`.\n- Line 2: `n` integers.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ n ≤ 5000\n-10^4 ≤ a[i], target ≤ 10^4",
    hints=[
        "Without duplicates: one of the halves [lo, mid] and [mid, hi] is always sorted, and a range check tells whether the target can be in it.",
        "With duplicates, a[lo] == a[mid] == a[hi] hides which half is sorted (1 0 1 1 1 versus 1 1 1 0 1).",
        "In that case only, discard both ends (lo++, hi−−) — neither can be the only copy of the target, since a[mid] equals them. Worst case O(n).",
    ],
    opt=("O(log n) average, O(n) worst", "O(1)", "Equal ends force one-step shrinking."),
    editorial=(
        "## The one thing this teaches\n**Find the case that breaks the invariant, and handle "
        "only that case slowly.** Rotated binary search depends on telling which half is sorted. "
        "Only the all-equal triple makes that impossible; every other step still halves the range.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n - 1;\nwhile (lo <= hi) {\n    int mid = (lo + hi) / 2;\n"
        "    if (a[mid] == target) return true;\n"
        "    if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; }\n"
        "    else if (a[lo] <= a[mid]) {                      // left half sorted\n"
        "        if (a[lo] <= target && target < a[mid]) hi = mid - 1; else lo = mid + 1;\n"
        "    } else {                                         // right half sorted\n"
        "        if (a[mid] < target && target <= a[hi]) lo = mid + 1; else hi = mid - 1;\n    }\n}\nreturn false;\n```\n\n"
        "## Why dropping both ends is safe\nBoth equal `a[mid]`, which is not the target. So "
        "neither end is the target either.\n\n"
        "## Compared with the minimum problem\nFinding the minimum compares only with `a[hi]`; "
        "searching for a value needs both ends to decide which half is sorted."
    ),
    py='''
def solve(a, k):
    return "YES" if k in a else "NO"
''',
    java='''
    static String solve(int[] a, long target) {
        int lo = 0, hi = a.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) / 2;
            if (a[mid] == target) return "YES";
            if (a[lo] == a[mid] && a[mid] == a[hi]) { lo++; hi--; }
            else if (a[lo] <= a[mid]) {
                if (a[lo] <= target && target < a[mid]) hi = mid - 1; else lo = mid + 1;
            } else {
                if (a[mid] < target && target <= a[hi]) lo = mid + 1; else hi = mid - 1;
            }
        }
        return "NO";
    }
''',
    examples=[("Example 1", "7 0\n2 5 6 0 0 1 2\n"), ("Example 2", "7 3\n2 5 6 0 0 1 2\n")],
    hidden=[
        ("Hidden among equals, absent", "5 2\n1 0 1 1 1\n"),
        ("Hidden among equals, present", "5 0\n1 0 1 1 1\n"),
        ("Single element", "1 5\n5\n"),
        ("Present on the right", "5 0\n1 1 1 0 1\n"),
        ("Not rotated", "6 4\n1 2 2 3 4 4\n"),
    ],
    expl=[
        "0 appears after the rotation point.",
        "3 is not in the array.",
    ],
    prereqs=[
        ("binary_search", "Rotated-array binary search: decide which half is sorted, then range-check."),
        ("array_patterns", "Discarding elements that provably cannot be the answer."),
    ],
)

_p(
    "kth-missing-positive", "Kth Missing Positive Number", "Easy",
    topics=["Binary Search", "Arrays"], subtopics=["Binary Search on Index"], companies=["Meta", "Microsoft"],
    shape="arr_k", ret="long", todo="a[i] − (i + 1) positives are missing before a[i]; binary search the first index where that reaches k, answer k + index",
    description=(
        "The array is strictly increasing and holds positive integers. Print the `k`-th positive "
        "integer that is **missing** from it.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe k-th missing positive integer."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ a[i] ≤ 10^9, strictly increasing\n1 ≤ k ≤ 10^9",
    hints=[
        "Walking upward from 1 and counting gaps can take k steps.",
        "If nothing were missing, a[i] would equal i + 1. So exactly a[i] − (i + 1) numbers are missing before a[i] — and that count never decreases.",
        "Binary search for the first index i where a[i] − (i + 1) ≥ k. Then the answer is k + i (the k missing numbers plus the i array values below it).",
    ],
    opt=("O(log n)", "O(1)", "A binary search over indices."),
    editorial=(
        "## The one thing this teaches\n**Binary search a derived monotone quantity.** The array "
        "values themselves are not what you search for. The *number missing so far*, "
        "`a[i] − (i + 1)`, is monotone, and the answer sits just before the first index where it "
        "reaches k.\n\n"
        "## Approach\n```java\nint lo = 0, hi = n;                          // first i with missing(i) >= k, or n\n"
        "while (lo < hi) {\n    int mid = (lo + hi) / 2;\n"
        "    if (a[mid] - (mid + 1) >= k) hi = mid; else lo = mid + 1;\n}\nreturn (long) k + lo;\n```\n\n"
        "## Why k + lo\nThe answer is larger than exactly `lo` array values (those before index "
        "`lo`) and is the k-th number not in the array, so it is the `(k + lo)`-th positive "
        "integer.\n\n"
        "## Walkthrough: 2 3 4 7 11, k = 5\nMissing counts: 1, 1, 1, 3, 6. The first ≥ 5 is at "
        "index 4. Answer 5 + 4 = 9 (missing: 1, 5, 6, 8, 9)."
    ),
    py='''
def solve(a, k):
    for i, v in enumerate(a):
        if v - (i + 1) >= k:
            return k + i
    return k + len(a)
''',
    java='''
    static long solve(int[] a, long k) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (a[mid] - (mid + 1) >= k) hi = mid; else lo = mid + 1;
        }
        return k + lo;
    }
''',
    examples=[("Example 1", "5 5\n2 3 4 7 11\n"), ("Example 2", "4 2\n1 2 3 4\n")],
    hidden=[
        ("Nothing missing before", "1 1\n1\n"),
        ("Huge k", "3 1000000000\n1 2 3\n"),
        ("Missing at the start", "3 3\n5 6 7\n"),
        ("Between values", "4 3\n1 3 5 7\n"),
    ],
    expl=[
        "Missing: 1, 5, 6, 8, 9, … — the 5th is 9.",
        "Nothing is missing up to 4, so the 2nd missing number is 6.",
    ],
    prereqs=[
        ("binary_search", "Searching for the first index where a monotone count reaches k."),
        ("overflow", "k + index can exceed an int."),
    ],
)

_p(
    "min-add-parentheses-valid", "Minimum Add to Make Parentheses Valid", "Medium",
    topics=["Stacks", "Strings", "Greedy"], subtopics=["Balance Counter"], companies=["Meta", "Amazon"],
    shape="str", ret="int", todo="track open count; a ')' with no open '(' needs an insertion; at the end, the remaining opens need closers",
    description=(
        "Insert as few parentheses as possible (anywhere) to make the string valid. Print the "
        "number of insertions.\n\n"
        "### Input\nOne line: a string of `(` and `)`.\n\n"
        "### Output\nThe minimum number of insertions."
    ),
    constraints="1 ≤ |s| ≤ 1000",
    hints=[
        "Match parentheses as a stack would — but you only need the stack's size.",
        "A ')' when nothing is open can never be matched by anything later: it needs an inserted '(' before it.",
        "Count those, and add the number of '(' still open at the end.",
    ],
    opt=("O(n)", "O(1)", "Two counters."),
    editorial=(
        "## The one thing this teaches\n**Unmatched brackets come in two independent kinds.** A "
        "`)` that arrives with nothing open, and a `(` still open at the end. Neither can fix the "
        "other — a later `(` cannot close an earlier `)` — so the answer is their sum.\n\n"
        "## Approach\n```java\nint open = 0, inserts = 0;\nfor (char ch : s.toCharArray()) {\n"
        "    if (ch == '(') open++;\n    else if (open > 0) open--;\n    else inserts++;          // unmatched ')'\n}\n"
        "return inserts + open;                        // plus unmatched '('\n```\n\n"
        "## Why greedy matching is optimal\nMatching a `)` with the most recent open `(` never "
        "hurts: any valid completion can be rearranged to use that pairing.\n\n"
        "## Walkthrough: ()))((\n`()` matches. Next two `)` are unmatched (2). The final `((` "
        "stay open (2). Total 4."
    ),
    py='''
def solve(s):
    while "()" in s:
        s = s.replace("()", "")
    return len(s)
''',
    java='''
    static int solve(String s) {
        int open = 0, inserts = 0;
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '(') open++;
            else if (open > 0) open--;
            else inserts++;
        }
        return inserts + open;
    }
''',
    examples=[("Example 1", "())\n"), ("Example 2", "(((\n")],
    hidden=[
        ("Already valid", "()\n"),
        ("Both kinds", "()))((\n"),
        ("Reversed pair", ")(\n"),
        ("Nested and valid", "(()())\n"),
    ],
    expl=[
        "One ')' has no partner.",
        "Three '(' are never closed.",
    ],
    prereqs=[
        ("stack", "Bracket matching, reduced to a counter of open brackets."),
        ("greedy", "Matching each ')' with the most recent unmatched '('."),
    ],
)

_p(
    "smallest-infinite-set", "Smallest Number in Infinite Set", "Medium",
    topics=["Design", "Heaps", "Ordered Set"], subtopics=["Pointer Plus Set"], companies=["Google"],
    shape="ops", ret="String", todo="a counter marks where the untouched numbers begin; a sorted set holds smaller numbers added back",
    description=(
        "A set initially contains **every positive integer**. Support:\n\n"
        "- `pop` — remove and print the smallest number in the set;\n"
        "- `add x` — put `x` back if it is not already in the set.\n\n"
        "### Input\n- Line 1: `q`.\n- Next `q` lines: the operations.\n\n"
        "### Output\nOne line per `pop`."
    ),
    constraints="1 ≤ q ≤ 10^4\n1 ≤ x ≤ 1000",
    hints=[
        "The set is infinite, so it cannot be stored. But it only differs from \"all positive integers\" in a small way.",
        "Everything from some number `next` upward has never been popped. Below `next`, only numbers added back are present.",
        "Keep `next` and a sorted set (or min-heap without duplicates) of added-back numbers below it. Pop from that set first; otherwise return next++.",
    ],
    opt=("O(log q) per operation", "O(q)", "The added-back set holds at most as many numbers as have been popped."),
    editorial=(
        "## The one thing this teaches\n**Represent an infinite structure by its difference from "
        "a simple one.** The set is `{next, next + 1, …}` plus a few returned numbers below "
        "`next`. Those two pieces are finite and support both operations directly.\n\n"
        "## Approach\n```java\nint next = 1;\nTreeSet<Integer> returned = new TreeSet<>();\n\n"
        "int pop() {\n    if (!returned.isEmpty()) return returned.pollFirst();   // always smaller than next\n"
        "    return next++;\n}\n\n"
        "void add(int x) {\n    if (x < next) returned.add(x);     // x ≥ next is already present\n}\n```\n\n"
        "## Why returned numbers are smaller than next\n`add` only stores `x < next`, and `next` "
        "only grows — so everything in `returned` stays below it.\n\n"
        "## Duplicates\nA set ignores a second `add` of the same number. With a heap, keep a "
        "separate membership set to avoid pushing duplicates."
    ),
    py='''
def solve(ops):
    popped = set()
    out = []
    for op in ops:
        if op[0] == "add":
            popped.discard(int(op[1]))
        else:
            v = 1
            while v in popped:
                v += 1
            popped.add(v)
            out.append(str(v))
    return "\\n".join(out)
''',
    java='''
    static String solve(String[][] ops) {
        int next = 1;
        TreeSet<Integer> returned = new TreeSet<>();
        StringBuilder sb = new StringBuilder();
        for (String[] op : ops) {
            if (op[0].equals("add")) {
                int x = Integer.parseInt(op[1]);
                if (x < next) returned.add(x);
            } else {
                int v = returned.isEmpty() ? next++ : returned.pollFirst();
                if (sb.length() > 0) sb.append('\\n');
                sb.append(v);
            }
        }
        return sb.toString();
    }
''',
    examples=[("Example 1", "8\nadd 2\npop\npop\npop\nadd 1\npop\npop\npop\n")],
    hidden=[
        ("Only pops", "3\npop\npop\npop\n"),
        ("Add back twice", "5\npop\npop\nadd 1\nadd 1\npop\n"),
        ("Add a large number", "4\nadd 1000\npop\npop\npop\n"),
        ("Return several", "8\npop\npop\npop\nadd 3\nadd 1\npop\npop\npop\n"),
    ],
    expl=[
        "2 is already present. Pops give 1, 2, 3; 1 is added back and popped again, then 4 and 5.",
    ],
    prereqs=[
        ("design_ds", "A finite representation of an infinite set."),
        ("heap", "A min-structure over the numbers added back."),
    ],
)

_p(
    "remove-nodes-greater-right", "Remove Nodes From Linked List", "Medium",
    topics=["Linked Lists", "Stacks"], subtopics=["Monotonic Stack", "Reverse"], companies=["Amazon"],
    shape="list", ret="ListNode", todo="reverse the list, keep nodes that are ≥ the running maximum, and reverse back",
    description=(
        "Remove every node that has a node with a **strictly greater** value anywhere to its "
        "right. Print the remaining list.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: the `n` values.\n\n"
        "### Output\nThe list after removals."
    ),
    constraints="1 ≤ n ≤ 10^5\n1 ≤ value ≤ 10^5",
    hints=[
        "A node survives if it is at least as large as everything after it — the leaders of the array.",
        "From the right, that is a running maximum. But a singly linked list only walks left to right.",
        "Reverse the list, keep nodes whose value is ≥ the running maximum, then reverse the result. Or use a monotonic stack walking forward.",
    ],
    opt=("O(n)", "O(1)", "Two reversals and one filtering pass, all relinking in place."),
    editorial=(
        "## The one thing this teaches\n**Reverse a list to get the direction you need.** The "
        "survival rule looks right, but a singly linked list only moves left to right. Reversing "
        "is O(n) and O(1) space — cheaper than copying into an array.\n\n"
        "## Approach\n```java\nhead = reverse(head);\nListNode keep = head;             // the last node always survives\n"
        "for (ListNode p = head; p.next != null; ) {\n"
        "    if (p.next.val < keep.val) p.next = p.next.next;    // smaller than something to its right\n"
        "    else { p = p.next; keep = p; }\n}\nreturn reverse(head);\n```\n\n"
        "## The stack alternative\nWalk forward pushing nodes; before pushing, pop every node "
        "with a smaller value — it has just found a greater node to its right. The stack, bottom "
        "to top, is the answer.\n\n"
        "## Strictly greater\nEqual values survive: in `1 1 1 1` nothing has a *greater* value "
        "to its right."
    ),
    py='''
def solve(head):
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    kept = []
    best = 0
    for v in reversed(vals):
        if v >= best:
            kept.append(v)
            best = v
    return build(kept[::-1])
''',
    java='''
    static ListNode reverse(ListNode head) {
        ListNode prev = null;
        while (head != null) { ListNode next = head.next; head.next = prev; prev = head; head = next; }
        return prev;
    }

    static ListNode solve(ListNode head) {
        head = reverse(head);
        ListNode p = head;
        while (p.next != null) {
            if (p.next.val < p.val) p.next = p.next.next;
            else p = p.next;
        }
        return reverse(head);
    }
''',
    examples=[("Example 1", "5\n5 2 13 3 8\n"), ("Example 2", "4\n1 1 1 1\n")],
    hidden=[
        ("Single node", "1\n7\n"),
        ("Increasing", "4\n1 2 3 4\n"),
        ("Decreasing", "4\n4 3 2 1\n"),
        ("Mixed", "7\n3 9 2 9 4 1 4\n"),
    ],
    expl=[
        "5 and 2 are smaller than 13; 3 is smaller than 8.",
        "No value is strictly greater than another.",
    ],
    prereqs=[
        ("list_reversal", "Reversing a list in place, twice."),
        ("prefix_max", "A running maximum that decides which nodes survive."),
    ],
)

_p(
    "cousins-in-binary-tree", "Cousins in Binary Tree", "Easy",
    topics=["Trees", "BFS"], subtopics=["Depth and Parent"], companies=["Amazon", "Meta"],
    shape="tree_xy", ret="String", todo="find each value's depth and parent in one traversal; cousins have equal depths and different parents",
    description=(
        "Two nodes are **cousins** if they are at the same depth but have different parents. "
        "Given a tree with distinct values and two values `x` and `y` in it, print `YES` if they "
        "are cousins, otherwise `NO`.\n\n"
        "### Input\n- Line 1: the tree in level order, `null` for a missing child.\n- Line 2: `x y`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="2 ≤ nodes ≤ 100\n1 ≤ value ≤ 100, distinct\nx ≠ y, both in the tree",
    hints=[
        "Two facts decide it: each node's depth and each node's parent.",
        "Any traversal can record both — pass the parent and depth down, or visit level by level.",
        "Answer YES exactly when depth[x] == depth[y] and parent[x] != parent[y].",
    ],
    opt=("O(n)", "O(n)", "One traversal; the stack or queue may hold O(n) nodes."),
    editorial=(
        "## The one thing this teaches\n**Carry the context a question needs down the "
        "traversal.** A node does not know its depth or parent, but its caller does. Passing "
        "`(node, parent, depth)` together records both facts in one pass.\n\n"
        "## Approach\n```java\nArrayDeque<Object[]> st = new ArrayDeque<>();\nst.push(new Object[]{root, null, 0});\n"
        "while (!st.isEmpty()) {\n    Object[] e = st.pop();\n    TreeNode t = (TreeNode) e[0];\n"
        "    if (t.val == x) { px = (TreeNode) e[1]; dx = (int) e[2]; }\n"
        "    if (t.val == y) { py = (TreeNode) e[1]; dy = (int) e[2]; }\n"
        "    push children with (child, t, depth + 1);\n}\nreturn dx == dy && px != py;\n```\n\n"
        "## Siblings are not cousins\nIn `1 2 3`, nodes 2 and 3 are at the same depth but share "
        "the parent 1.\n\n"
        "## The BFS view\nIn level-order traversal, check each level: both values present, and "
        "not as two children of the same node."
    ),
    py='''
def solve(root, x, y):
    info = {}
    level = [(root, None)]
    depth = 0
    while level:
        nxt = []
        for node, parent in level:
            info[node.val] = (depth, parent)
            for child in (node.left, node.right):
                if child:
                    nxt.append((child, node.val))
        level = nxt
        depth += 1
    (dx, px), (dy, py) = info[x], info[y]
    return "YES" if dx == dy and px != py else "NO"
''',
    java='''
    static String solve(TreeNode root, int x, int y) {
        int dx = -1, dy = -2;
        TreeNode px = null, py = null;
        ArrayDeque<Object[]> st = new ArrayDeque<>();
        st.push(new Object[]{root, null, 0});
        while (!st.isEmpty()) {
            Object[] e = st.pop();
            TreeNode t = (TreeNode) e[0];
            int d = (int) e[2];
            if (t.val == x) { px = (TreeNode) e[1]; dx = d; }
            if (t.val == y) { py = (TreeNode) e[1]; dy = d; }
            if (t.left != null) st.push(new Object[]{t.left, t, d + 1});
            if (t.right != null) st.push(new Object[]{t.right, t, d + 1});
        }
        return dx == dy && px != py ? "YES" : "NO";
    }
''',
    examples=[
        ("Example 1", "1 2 3 4\n4 3\n"),
        ("Example 2", "1 2 3 null 4 null 5\n5 4\n"),
        ("Example 3", "1 2 3 null 4\n2 3\n"),
    ],
    hidden=[
        ("Siblings", "1 2 3\n2 3\n"),
        ("Different depths", "1 2 3 4 5 6 7 8\n8 7\n"),
        ("Deep cousins", "1 2 3 4 5 6 7\n5 6\n"),
        ("Root and child", "1 2\n1 2\n"),
    ],
    expl=[
        "4 is at depth 2 and 3 at depth 1.",
        "Both are at depth 2, with parents 2 and 3.",
        "2 and 3 share the parent 1.",
    ],
    prereqs=[
        ("tree_traversal", "A traversal that carries each node's parent and depth."),
        ("bfs", "Level-order traversal, where one level is one depth."),
    ],
)

_p(
    "last-stone-weight-ii", "Last Stone Weight II", "Medium",
    topics=["Dynamic Programming", "Math"], subtopics=["Subset Sum", "Knapsack"], companies=["Google", "Amazon"],
    shape="arr", ret="int", todo="the result is |sum(A) − sum(B)| for some split into two groups; find the reachable subset sum closest to total / 2",
    description=(
        "Repeatedly pick two stones with weights `x ≤ y` and smash them: if equal both vanish, "
        "otherwise a stone of weight `y − x` remains. At the end at most one stone is left. "
        "Print the smallest possible weight of that stone (0 if none).\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` weights.\n\n"
        "### Output\nThe smallest possible final weight."
    ),
    constraints="1 ≤ n ≤ 30\n1 ≤ weight ≤ 100",
    hints=[
        "Follow a stone through the smashes: its weight ends up added or subtracted in the final result.",
        "Any sequence of smashes gives |sum of one group − sum of the other| for some split of the stones, and every split is achievable.",
        "So minimise |total − 2·S| over reachable subset sums S ≤ total / 2 — a 0/1 knapsack over sums up to 1500.",
    ],
    opt=("O(n · total)", "O(total)", "A boolean subset-sum table."),
    editorial=(
        "## The one thing this teaches\n**Look for the invariant under a messy process.** The "
        "smashing order seems to matter, but the final weight is always a signed sum of the "
        "original weights — one group minus the other. The process disappears and a subset-sum "
        "problem remains.\n\n"
        "## Approach\n```java\nint total = sum(a);\nboolean[] reach = new boolean[total / 2 + 1];\nreach[0] = true;\n"
        "for (int w : a)\n    for (int s = total / 2; s >= w; s--)      // downward: each stone once\n"
        "        reach[s] |= reach[s - w];\nfor (int s = total / 2; ; s--) if (reach[s]) return total - 2 * s;\n```\n\n"
        "## Why every split is achievable\nRepeatedly smash a stone from the heavier group with one "
        "from the lighter group; the difference stays with the heavier group. When one group "
        "empties, the other holds the difference.\n\n"
        "## Walkthrough: 2 7 4 1 8 1\nTotal 23. A subset summing to 11 exists (2 + 8 + 1), so the "
        "answer is 23 − 22 = 1."
    ),
    py='''
def solve(a):
    sums = {0}
    for w in a:
        sums |= {s + w for s in sums}
    total = sum(a)
    return min(abs(total - 2 * s) for s in sums)
''',
    java='''
    static int solve(int[] a) {
        int total = 0;
        for (int w : a) total += w;
        boolean[] reach = new boolean[total / 2 + 1];
        reach[0] = true;
        for (int w : a)
            for (int s = total / 2; s >= w; s--) reach[s] |= reach[s - w];
        for (int s = total / 2; s >= 0; s--) if (reach[s]) return total - 2 * s;
        return total;
    }
''',
    examples=[("Example 1", "6\n2 7 4 1 8 1\n"), ("Example 2", "5\n31 26 33 21 40\n")],
    hidden=[
        ("Single stone", "1\n5\n"),
        ("Equal pair", "2\n3 3\n"),
        ("Powers of two", "6\n1 2 4 8 16 32\n"),
        ("All equal, odd count", "5\n7 7 7 7 7\n"),
    ],
    expl=[
        "Split into {2, 8, 1} and {7, 4, 1}: 11 against 12.",
        "Split into {40, 33} = 73 and {31, 26, 21} = 78: a difference of 5.",
    ],
    prereqs=[
        ("dp", "A 0/1 subset-sum table, filled downward."),
        ("complement", "Minimising |total − 2S| over subset sums S."),
    ],
)
