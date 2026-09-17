# -*- coding: utf-8 -*-
# ===========================================================================
# Batch 1 — two pointers and sliding window.
#
# Authored with tools/dsa_more_kit.py; placed by tools/dsa_placements.py.
#
#   squares-of-sorted-array           fill from the back: the largest square is at an end
#   valid-palindrome-alnum            two pointers that skip what does not count
#   three-sum-count                   fix one, two-pointer the rest, skip duplicates
#   sort-colors                       three pointers, one pass, in place
#   permutation-in-string             a fixed window compared as counts
#   longest-repeating-replacement     a window whose validity is "length − top count ≤ k"
#   subarray-product-less-k           the count-all-windows shape, with a product
# ===========================================================================

_p(
    "squares-of-sorted-array", "Squares of a Sorted Array", "Easy",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Amazon", "Uber"],
    shape="arr", ret="String", todo="fill the result from the back with the larger square at either end",
    description=(
        "Given an array sorted in non-decreasing order, which may contain negative numbers, "
        "print the squares of every element, also in non-decreasing order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers, sorted.\n\n"
        "### Output\nThe `n` squares in non-decreasing order, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\n-10^4 ≤ a[i] ≤ 10^4\nThe input is sorted in non-decreasing order.",
    hints=[
        "Squaring and then sorting is correct and O(n log n). The input is already sorted — use that.",
        "Negative numbers make the squares decrease and then increase: the largest square is at one of the two ends.",
        "Compare the two ends, write the larger square into the LAST free slot of the result, and move that end inward.",
    ],
    opt=("O(n)", "O(n)", "One pass with a pointer at each end, writing the result from the back."),
    editorial=(
        "## The one thing this teaches\n**When the extremes are at the ends, fill from the back.** "
        "The squares of a sorted array form a valley: big on the left (large negatives), small "
        "in the middle, big on the right. The *smallest* square could be anywhere, but the "
        "*largest* is always at `l` or `r`.\n\n"
        "## Approach\n```java\nint l = 0, r = n - 1;\n"
        "for (int w = n - 1; w >= 0; w--) {\n"
        "    if (Math.abs(a[l]) > Math.abs(a[r])) out[w] = a[l] * a[l++];\n"
        "    else                                 out[w] = a[r] * a[r--];\n}\n```\n\n"
        "## Why not from the front\nTo fill from the front you would need to find where the "
        "valley bottoms out — a search for the first non-negative element — and then merge "
        "outward in two directions. Filling from the back needs no search, because both "
        "candidates for \"largest remaining\" are already under a pointer."
    ),
    py='''
def solve(a):
    n = len(a)
    out = [0] * n
    l, r = 0, n - 1
    for w in range(n - 1, -1, -1):
        if abs(a[l]) > abs(a[r]):
            out[w] = a[l] * a[l]
            l += 1
        else:
            out[w] = a[r] * a[r]
            r -= 1
    return " ".join(map(str, out))
''',
    java='''
    static String solve(int[] a) {
        int n = a.length;
        long[] out = new long[n];
        int l = 0, r = n - 1;
        for (int w = n - 1; w >= 0; w--) {
            if (Math.abs((long) a[l]) > Math.abs((long) a[r])) { out[w] = (long) a[l] * a[l]; l++; }
            else { out[w] = (long) a[r] * a[r]; r--; }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) { if (i > 0) sb.append(' '); sb.append(out[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "5\n-4 -1 0 3 10\n"), ("Example 2", "5\n-7 -3 2 3 11\n")],
    hidden=[
        ("All negative", "4\n-5 -4 -2 -1\n"),
        ("Single element", "1\n-3\n"),
        ("All positive", "3\n1 2 3\n"),
        ("Mirror duplicates", "4\n-2 -2 2 2\n"),
    ],
    expl=[
        "Squares are 16 1 0 9 100; sorted, 0 1 9 16 100.",
        "Squares are 49 9 4 9 121; sorted, 4 9 9 49 121.",
    ],
    prereqs=[
        ("two_pointers", "A pointer at each end, because the largest remaining square is always at one of them."),
        ("sorting", "The input's order is what makes the ends the extremes — the output is a merge, not a sort."),
    ],
)

_p(
    "valid-palindrome-alnum", "Valid Palindrome (Letters and Digits)", "Easy",
    topics=["Strings", "Two Pointers"], subtopics=["Two Pointers"], companies=["Meta", "Microsoft"],
    shape="line", ret="String", todo="move two pointers inward, skipping characters that are not letters or digits",
    description=(
        "A phrase is a palindrome if, after **ignoring every character that is not a letter or a "
        "digit** and ignoring case, it reads the same forwards and backwards.\n\n"
        "### Input\nOne line: the phrase (it may contain spaces and punctuation, and may be empty).\n\n"
        "### Output\n`YES` if it is a palindrome, otherwise `NO`."
    ),
    constraints="0 ≤ |s| ≤ 2·10^5\ns consists of printable ASCII characters.",
    hints=[
        "Building a cleaned, lower-cased copy and comparing it with its reverse works, and costs O(n) extra memory.",
        "Instead, put a pointer at each end. Skip any character that does not count before comparing.",
        "Compare lower-cased characters. A phrase with nothing that counts is a palindrome.",
    ],
    opt=("O(n)", "O(1)", "Each pointer moves only inward, and no copy of the string is made."),
    editorial=(
        "## The one thing this teaches\n**Two pointers that skip.** The comparison loop is the "
        "palindrome check you already know; the only change is that each pointer steps past "
        "characters that do not count *before* the comparison happens.\n\n"
        "## Approach\n```java\nint l = 0, r = s.length() - 1;\nwhile (l < r) {\n"
        "    if (!Character.isLetterOrDigit(s.charAt(l))) l++;\n"
        "    else if (!Character.isLetterOrDigit(s.charAt(r))) r--;\n"
        "    else if (Character.toLowerCase(s.charAt(l)) != Character.toLowerCase(s.charAt(r))) return \"NO\";\n"
        "    else { l++; r--; }\n}\nreturn \"YES\";\n```\n\n"
        "Each iteration moves exactly one pointer or both, so the loop runs at most n times.\n\n"
        "## The case people miss\nDigits count. `0P` is **not** a palindrome: `0` and `p` differ, "
        "and a check that only keeps letters would wrongly compare `p` with itself."
    ),
    py='''
def solve(s):
    l, r = 0, len(s) - 1
    while l < r:
        if not s[l].isalnum():
            l += 1
        elif not s[r].isalnum():
            r -= 1
        elif s[l].lower() != s[r].lower():
            return "NO"
        else:
            l += 1
            r -= 1
    return "YES"
''',
    java='''
    static String solve(String s) {
        int l = 0, r = s.length() - 1;
        while (l < r) {
            char a = s.charAt(l), b = s.charAt(r);
            if (!Character.isLetterOrDigit(a)) l++;
            else if (!Character.isLetterOrDigit(b)) r--;
            else if (Character.toLowerCase(a) != Character.toLowerCase(b)) return "NO";
            else { l++; r--; }
        }
        return "YES";
    }
''',
    examples=[("Example 1", "A man, a plan, a canal: Panama\n"), ("Example 2", "race a car\n")],
    hidden=[
        ("Only punctuation", " .,! \n"),
        ("A digit is not a letter", "0P\n"),
        ("Underscore is skipped", "ab_a\n"),
        ("Mixed case with quotes", "No 'x' in Nixon\n"),
    ],
    expl=[
        "The letters read `amanaplanacanalpanama`, the same backwards.",
        "`raceacar` reversed is `racaecar`.",
    ],
    prereqs=[
        ("two_pointers", "Converging pointers, each skipping characters that do not take part in the comparison."),
        ("string_basics", "Classifying and lower-casing characters one at a time instead of building a cleaned copy."),
    ],
)

_p(
    "three-sum-count", "3Sum — Count Distinct Triplets", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers", "Sorting"], companies=["Meta", "Amazon", "Google"],
    shape="arr", ret="long", todo="sort, fix each first element, two-pointer the rest, skip duplicate values",
    description=(
        "Count the **distinct** triplets of values `(x, y, z)` with `x + y + z = 0` that can be formed "
        "from three different positions in the array. Two triplets are the same if they contain "
        "the same values, in any order.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` integers.\n\n"
        "### Output\nThe number of distinct zero-sum triplets."
    ),
    constraints="1 ≤ n ≤ 3000\n-10^5 ≤ a[i] ≤ 10^5",
    hints=[
        "Three nested loops are O(n³) and still have to deduplicate. Sort first.",
        "Fix the smallest element a[i]. The other two must sum to −a[i] — that is two-sum on a sorted suffix.",
        "Skip an a[i] equal to the previous one. After a match, advance l past every copy of the value you just used.",
    ],
    opt=("O(n²)", "O(1)", "An O(n log n) sort, then an O(n) two-pointer scan for each of the n first elements."),
    editorial=(
        "## The one thing this teaches\n**Reduce k-sum to (k−1)-sum.** Fixing one element turns "
        "3-sum into two-sum on the rest of a sorted array, which the two-pointer scan solves in "
        "O(n). Doing that for every first element gives O(n²).\n\n"
        "## Approach\n```java\nArrays.sort(a);\nfor (int i = 0; i < n; i++) {\n"
        "    if (i > 0 && a[i] == a[i - 1]) continue;          // same first value, same triplets\n"
        "    int l = i + 1, r = n - 1;\n"
        "    while (l < r) {\n        long s = (long) a[i] + a[l] + a[r];\n"
        "        if (s < 0) l++;\n        else if (s > 0) r--;\n"
        "        else {\n            count++;\n            l++; r--;\n"
        "            while (l < r && a[l] == a[l - 1]) l++;     // same second value\n"
        "        }\n    }\n}\n```\n\n"
        "## Deduplication, precisely\nThe sort puts equal values side by side, so a triplet is "
        "repeated only when the *same value* is chosen again at a position. Skipping repeats of "
        "`a[i]` and, after a match, of `a[l]` removes every repeat — the third value is then "
        "forced, so it needs no skip of its own. Deduplicating with a `HashSet` of triplets also "
        "works, and hides an O(n²) memory bill."
    ),
    py='''
def solve(a):
    a = sorted(a)
    n = len(a)
    count = 0
    for i in range(n):
        if i > 0 and a[i] == a[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                count += 1
                l += 1
                r -= 1
                while l < r and a[l] == a[l - 1]:
                    l += 1
    return count
''',
    java='''
    static long solve(int[] a) {
        Arrays.sort(a);
        int n = a.length;
        long count = 0;
        for (int i = 0; i < n; i++) {
            if (i > 0 && a[i] == a[i - 1]) continue;
            int l = i + 1, r = n - 1;
            while (l < r) {
                long s = (long) a[i] + a[l] + a[r];
                if (s < 0) l++;
                else if (s > 0) r--;
                else {
                    count++;
                    l++; r--;
                    while (l < r && a[l] == a[l - 1]) l++;
                }
            }
        }
        return count;
    }
''',
    examples=[("Example 1", "6\n-1 0 1 2 -1 -4\n"), ("Example 2", "3\n0 0 0\n")],
    hidden=[
        ("No triplet", "3\n0 1 1\n"),
        ("Many zeros are one triplet", "4\n0 0 0 0\n"),
        ("Several with repeats", "8\n-2 0 1 1 2 -1 -1 3\n"),
        ("Too short", "2\n1 -1\n"),
    ],
    expl=[
        "`[-1, -1, 2]` and `[-1, 0, 1]`. The second −1 would repeat both.",
        "Only one triplet exists: `[0, 0, 0]`.",
    ],
    prereqs=[
        ("two_pointers", "Two-sum on a sorted suffix, run once per fixed first element."),
        ("sorting", "Sorting both enables the scan and puts duplicates next to each other so they can be skipped."),
    ],
)

_p(
    "sort-colors", "Sort Colors (Dutch National Flag)", "Medium",
    topics=["Arrays", "Two Pointers"], subtopics=["Two Pointers"], companies=["Microsoft", "Meta"],
    shape="arr", ret="String", todo="keep three regions — 0s before lo, 2s after hi — and classify a[mid]",
    description=(
        "The array contains only `0`, `1` and `2`. Sort it **in one pass, in place**, without "
        "counting.\n\n"
        "### Input\n- Line 1: `n`.\n- Line 2: `n` values, each 0, 1 or 2.\n\n"
        "### Output\nThe sorted values, separated by spaces."
    ),
    constraints="1 ≤ n ≤ 10^5\na[i] ∈ {0, 1, 2}",
    hints=[
        "Counting the three values and rewriting the array is two passes. Aim for one.",
        "Keep three regions: [0, lo) holds 0s, [lo, mid) holds 1s, (hi, n−1] holds 2s. [mid, hi] is unknown.",
        "A 0 swaps to lo and both lo and mid advance. A 2 swaps to hi and only hi retreats — the value swapped in is still unknown.",
    ],
    opt=("O(n)", "O(1)", "Every iteration shrinks the unknown region [mid, hi] by one."),
    editorial=(
        "## The one thing this teaches\n**An invariant with three regions.** Dijkstra's Dutch "
        "national flag keeps the array partitioned as `0s | 1s | unknown | 2s` and shrinks the "
        "unknown part by one element per step.\n\n"
        "## Approach\n```java\nint lo = 0, mid = 0, hi = n - 1;\nwhile (mid <= hi) {\n"
        "    if (a[mid] == 0)      swap(a, lo++, mid++);\n"
        "    else if (a[mid] == 1) mid++;\n"
        "    else                  swap(a, mid, hi--);   // mid does NOT advance\n}\n```\n\n"
        "## The asymmetry is the whole bug surface\nWhen `a[mid]` is 0, the element swapped in "
        "from `lo` came from the 1s region (or is `mid` itself), so it is already classified and "
        "`mid` can move on. When `a[mid]` is 2, the element swapped in from `hi` came from the "
        "*unknown* region, so it must be examined before `mid` moves. Advancing `mid` there "
        "leaves an unsorted value behind — on `2 0 1` it outputs `0 2 1`.\n\n"
        "The same partition is the heart of three-way quicksort, which is how sorting stays fast "
        "on arrays full of equal keys."
    ),
    py='''
def solve(a):
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]
            lo += 1
            mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]
            hi -= 1
    return " ".join(map(str, a))
''',
    java='''
    static String solve(int[] a) {
        int lo = 0, mid = 0, hi = a.length - 1;
        while (mid <= hi) {
            if (a[mid] == 0) { int t = a[lo]; a[lo] = a[mid]; a[mid] = t; lo++; mid++; }
            else if (a[mid] == 1) mid++;
            else { int t = a[hi]; a[hi] = a[mid]; a[mid] = t; hi--; }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(' '); sb.append(a[i]); }
        return sb.toString();
    }
''',
    examples=[("Example 1", "6\n2 0 2 1 1 0\n"), ("Example 2", "3\n2 0 1\n")],
    hidden=[
        ("Single element", "1\n1\n"),
        ("All twos", "5\n2 2 2 2 2\n"),
        ("Already sorted", "4\n0 0 1 1\n"),
        ("Mixed", "7\n1 2 0 2 1 0 0\n"),
    ],
    expl=[
        "Two of each colour, in order: `0 0 1 1 2 2`.",
        "The 2 is swapped to the back, and the 1 it brings to the front must be examined again.",
    ],
    prereqs=[
        ("two_pointers", "Three pointers maintaining regions that are known 0s, known 1s, unknown and known 2s."),
        ("array_patterns", "In-place partitioning by swapping, with an invariant that says what each region holds."),
    ],
)

_p(
    "permutation-in-string", "Permutation in String", "Medium",
    topics=["Strings", "Sliding Window"], subtopics=["Sliding Window", "Fixed Window"], companies=["Microsoft", "Amazon"],
    shape="str2", ret="String", todo="slide a window of length |p| over t, comparing letter counts",
    description=(
        "Does the text `t` contain, as a contiguous substring, some **rearrangement** of the "
        "pattern `p`?\n\n"
        "### Input\n- Line 1: the pattern `p`.\n- Line 2: the text `t`.\n\n"
        "### Output\n`YES` or `NO`."
    ),
    constraints="1 ≤ |p|, |t| ≤ 10^4\nBoth strings consist of lowercase English letters.",
    hints=[
        "A substring is a rearrangement of p exactly when it has the same letter counts as p.",
        "Every candidate has length |p|, so this is a FIXED-size window.",
        "Slide it: add the entering letter's count, subtract the leaving one's, and compare 26 counts.",
    ],
    opt=("O(26·|t|)", "O(1)", "Two 26-slot count arrays; each step updates two counts and compares 26."),
    editorial=(
        "## The one thing this teaches\n**Permutation means equal counts.** You never generate "
        "rearrangements — there can be |p|! of them. Two strings are rearrangements of each "
        "other exactly when every letter occurs the same number of times.\n\n"
        "## Approach\nA fixed window of length `k = |p|` over `t`, carrying its counts:\n\n"
        "```java\nint[] need = new int[26], win = new int[26];\n"
        "for (char c : p.toCharArray()) need[c - 'a']++;\n"
        "for (int i = 0; i < t.length(); i++) {\n"
        "    win[t.charAt(i) - 'a']++;\n"
        "    if (i >= k) win[t.charAt(i - k) - 'a']--;\n"
        "    if (i >= k - 1 && Arrays.equals(win, need)) return \"YES\";\n}\nreturn \"NO\";\n```\n\n"
        "## Getting to O(|t|)\nComparing 26 counts per step is a constant, so this is already "
        "linear. The textbook refinement keeps a `matches` counter — how many of the 26 letters "
        "currently agree — and adjusts it only for the two letters that changed. It is worth "
        "knowing, and rarely worth the extra bug surface."
    ),
    py='''
def solve(s, t):
    p = s
    k = len(p)
    if k > len(t):
        return "NO"
    need = [0] * 26
    for ch in p:
        need[ord(ch) - 97] += 1
    win = [0] * 26
    for i, ch in enumerate(t):
        win[ord(ch) - 97] += 1
        if i >= k:
            win[ord(t[i - k]) - 97] -= 1
        if i >= k - 1 and win == need:
            return "YES"
    return "NO"
''',
    java='''
    static String solve(String p, String t) {
        int k = p.length();
        if (k > t.length()) return "NO";
        int[] need = new int[26], win = new int[26];
        for (int i = 0; i < k; i++) need[p.charAt(i) - 'a']++;
        for (int i = 0; i < t.length(); i++) {
            win[t.charAt(i) - 'a']++;
            if (i >= k) win[t.charAt(i - k) - 'a']--;
            if (i >= k - 1 && Arrays.equals(win, need)) return "YES";
        }
        return "NO";
    }
''',
    examples=[("Example 1", "ab\neidbaooo\n"), ("Example 2", "ab\neidboaoo\n")],
    hidden=[
        ("Pattern longer than text", "abc\nab\n"),
        ("Single letter", "a\na\n"),
        ("At the end", "adc\ndcda\n"),
        ("Same letters, never adjacent", "hello\nooolleoooleh\n"),
    ],
    expl=[
        "`ba` at positions 3-4 is a rearrangement of `ab`.",
        "`b` and `a` both occur, but never next to each other.",
    ],
    prereqs=[
        ("sliding_window", "A fixed-size window whose counts are updated for the one letter entering and the one leaving."),
        ("hashing", "Letter counts as the canonical form of a permutation, so no rearrangement is ever generated."),
    ],
)

_p(
    "longest-repeating-replacement", "Longest Repeating Character Replacement", "Medium",
    topics=["Strings", "Sliding Window"], subtopics=["Sliding Window"], companies=["Google", "Amazon"],
    shape="str_k", ret="int", todo="grow the window; shrink while its length minus its top letter count exceeds k",
    description=(
        "You may change at most `k` characters of `s` to any other uppercase letter. Find the "
        "length of the longest substring that can be made of a **single repeated letter**.\n\n"
        "### Input\n- Line 1: the string `s`.\n- Line 2: `k`.\n\n"
        "### Output\nThe maximum length."
    ),
    constraints="1 ≤ |s| ≤ 10^5\n0 ≤ k ≤ |s|\ns consists of uppercase English letters.",
    hints=[
        "For a fixed window, the cheapest fix keeps its most frequent letter and changes everything else.",
        "So a window is valid when (length − count of its most frequent letter) ≤ k.",
        "Grow the right edge; shrink the left while invalid. The top count may go stale when shrinking — and the answer is still right.",
    ],
    opt=("O(n)", "O(1)", "Each index enters and leaves the window once; the counts are a 26-slot array."),
    editorial=(
        "## The one thing this teaches\n**Validity as a formula.** A window needs "
        "`length − maxCount` changes to become one letter, so \"at most k changes\" becomes a "
        "budget the sliding window can maintain, like the zero-flips problem with the "
        "most-frequent letter playing the part of the 1s.\n\n"
        "## Approach\n```java\nint[] count = new int[26];\nint left = 0, maxf = 0, best = 0;\n"
        "for (int r = 0; r < n; r++) {\n"
        "    maxf = Math.max(maxf, ++count[s.charAt(r) - 'A']);\n"
        "    while (r - left + 1 - maxf > k) count[s.charAt(left++) - 'A']--;\n"
        "    best = Math.max(best, r - left + 1);\n}\n```\n\n"
        "## Why a stale `maxf` is fine\nShrinking the window can lower the true top count, and "
        "`maxf` is never decreased. That can only make the window look *more* valid than it is — "
        "but `best` only grows when a window of a new length is reached with that `maxf`, and "
        "`maxf` was genuinely achieved by some earlier window of that length or less. So no "
        "invalid length is ever recorded. Recomputing the max over 26 counts each step is also "
        "O(n), if you would rather not rely on the argument."
    ),
    py='''
def solve(s, k):
    count = [0] * 26
    left = 0
    maxf = 0
    best = 0
    for r, ch in enumerate(s):
        i = ord(ch) - 65
        count[i] += 1
        maxf = max(maxf, count[i])
        while (r - left + 1) - maxf > k:
            count[ord(s[left]) - 65] -= 1
            left += 1
        best = max(best, r - left + 1)
    return best
''',
    java='''
    static int solve(String s, int k) {
        int[] count = new int[26];
        int left = 0, maxf = 0, best = 0;
        for (int r = 0; r < s.length(); r++) {
            maxf = Math.max(maxf, ++count[s.charAt(r) - 'A']);
            while (r - left + 1 - maxf > k) count[s.charAt(left++) - 'A']--;
            best = Math.max(best, r - left + 1);
        }
        return best;
    }
''',
    examples=[("Example 1", "ABAB\n2\n"), ("Example 2", "AABABBA\n1\n")],
    hidden=[
        ("Single letter", "A\n0\n"),
        ("Nothing to change", "AAAA\n0\n"),
        ("All distinct", "ABCDE\n1\n"),
        ("Budget covers both ends", "BAAAB\n2\n"),
    ],
    expl=[
        "Change both `A`s (or both `B`s) and the whole string is one letter: 4.",
        "Change the middle `B` of `AABA` to get `AAAA`: 4.",
    ],
    prereqs=[
        ("sliding_window", "A budget as the window's invariant: length minus the top letter count stays within k."),
        ("hashing", "A 26-slot count array for the window, updated as letters enter and leave."),
    ],
)

_p(
    "subarray-product-less-k", "Subarray Product Less Than K", "Medium",
    topics=["Arrays", "Sliding Window"], subtopics=["Sliding Window", "Counting"], companies=["Amazon", "Yatra"],
    shape="arr_k", ret="long", todo="for each right end, divide out from the left until product < k, then add the window length",
    description=(
        "Count the contiguous subarrays of **positive** integers whose product is strictly less "
        "than `k`.\n\n"
        "### Input\n- Line 1: `n k`.\n- Line 2: `n` positive integers.\n\n"
        "### Output\nThe number of qualifying subarrays."
    ),
    constraints="1 ≤ n ≤ 3·10^4\n1 ≤ a[i] ≤ 1000\n0 ≤ k ≤ 10^6",
    hints=[
        "Multiplying by a positive integer never decreases a product — so the count-all-windows shape applies.",
        "For each right end, shrink from the left (dividing out) until the product is below k.",
        "Then every subarray ending at r and starting in [left, r] qualifies: add r − left + 1. Handle k ≤ 1 first.",
    ],
    opt=("O(n)", "O(1)", "Both pointers only move forward; the product stays below k·max(a) so it fits in a long."),
    editorial=(
        "## The one thing this teaches\n**The count-all-windows shape with a product.** "
        "Positivity plays the role non-negativity plays for sums: extending a window never makes "
        "the product smaller, so the valid left ends for a fixed right end are a contiguous "
        "range, and `left` never has to move back.\n\n"
        "## Approach\n```java\nif (k <= 1) return 0;\nlong prod = 1, count = 0;\nint left = 0;\n"
        "for (int r = 0; r < n; r++) {\n    prod *= a[r];\n"
        "    while (prod >= k) prod /= a[left++];\n    count += r - left + 1;\n}\n```\n\n"
        "## The k ≤ 1 guard\nEvery product is at least 1, so with `k ≤ 1` nothing qualifies — "
        "and without the guard the `while` divides the window empty and then keeps going, "
        "`left` running past `r` and dividing by elements that were never multiplied in.\n\n"
        "## Why division is exact\n`prod` is always the product of exactly `a[left..r]`, so "
        "dividing by `a[left]` is exact integer division. The same trick with sums would be "
        "subtraction; with a product that might contain 0 it would be undefined — which is why "
        "the statement says *positive*."
    ),
    py='''
def solve(a, k):
    if k <= 1:
        return 0
    prod = 1
    left = 0
    count = 0
    for r, x in enumerate(a):
        prod *= x
        while prod >= k:
            prod //= a[left]
            left += 1
        count += r - left + 1
    return count
''',
    java='''
    static long solve(int[] a, long k) {
        if (k <= 1) return 0;
        long prod = 1, count = 0;
        int left = 0;
        for (int r = 0; r < a.length; r++) {
            prod *= a[r];
            while (prod >= k) prod /= a[left++];
            count += r - left + 1;
        }
        return count;
    }
''',
    examples=[("Example 1", "4 100\n10 5 2 6\n"), ("Example 2", "3 0\n1 2 3\n")],
    hidden=[
        ("k of one", "3 1\n1 1 1\n"),
        ("All ones", "5 1000\n1 1 1 1 1\n"),
        ("First element too big", "4 10\n10 9 1 2\n"),
        ("Single element", "1 5\n4\n"),
    ],
    expl=[
        "`[10]`, `[5]`, `[2]`, `[6]`, `[10,5]`, `[5,2]`, `[2,6]`, `[5,2,6]` — 8. `[10,5,2]` is exactly 100.",
        "No product of positive integers is below 0.",
    ],
    prereqs=[
        ("sliding_window", "Counting all valid windows: for each right end, the valid left ends form a range."),
        ("overflow", "The running product stays below k times the largest element, which a long holds comfortably."),
    ],
)
