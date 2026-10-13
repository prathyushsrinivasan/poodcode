# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Solved Examples for the "Cost & Core Patterns" stage.
#
# exec'd by tools/dsa_curriculum.py after the stage files, in the same
# namespace, so `_UNITS`, `_md` and `_trace` are already defined. Each unit key
# below gets its `solved_examples` set; the page renders them on the
# "Solved Examples" tab, between Toolkit and Practice.
#
# A solved example is the step between reading the skeleton and climbing the
# ladder on your own: one problem, taken from the statement through the naive
# attempt, the signals that point at this unit's technique, the code, a
# line-by-line explanation, a trace on a sample input and the cost. Three per
# unit, easy to harder.
#
# The code is Java (the curriculum's language) and is CHECKED:
# tools/verify_dsa_solved.py compiles every `code` block with a `main` that
# prints `sample_call` and compares the output with `sample_output`, so the
# sample shown on the page is the sample the code really produces.
# ---------------------------------------------------------------------------


def _solved(title, difficulty, problem, naive, signals, code, steps, sample_call,
            sample_output, trace, complexity, slug=""):
    """One fully worked problem (see `SolvedExample` in src/types.ts).

      * `problem`   — the statement, with constraints.
      * `naive`     — the first idea, and exactly why it falls short.
      * `signals`   — the words in the statement that point at this technique.
      * `code`      — the Java solution, static method(s) only.
      * `steps`     — the explanation, one markdown entry per step / line group.
      * `sample_call` / `sample_output` — a Java expression yielding a String,
        and what it prints (checked by tools/verify_dsa_solved.py).
      * `trace`     — the state on the sample, one row per step (`_trace`).
      * `complexity`— time and space, with the reason.
    """
    assert difficulty in ("Easy", "Medium", "Hard"), difficulty
    return {"title": title, "difficulty": difficulty, "slug": slug,
            "problem": _md(problem), "naive": _md(naive), "signals": _md(signals),
            "code": code.lstrip("\n").rstrip() + "\n",
            "steps": [_md(s) for s in steps],
            "sample_call": sample_call, "sample_output": sample_output,
            "trace": trace, "complexity": _md(complexity)}


_SOLVED = {}

# ------------------------------------------------------------ complexity

_SOLVED["complexity"] = [
    _solved(
        "Does any value repeat?", "Easy",
        """
Given an array `a` of `n` integers (`1 ≤ n ≤ 10⁵`), return `true` if some value
appears at least twice.
""",
        """
Compare every pair `(i, j)` with `i < j`. That is n(n−1)/2 comparisons: at
`n = 10⁵` about **5 × 10⁹**, fifty times the ~10⁸ operations a judge allows in
a second. Correct, but it times out.
""",
        """
- `n ≤ 10⁵` rules out O(n²) before you write anything (table: 10⁵ wants
  O(n log n) or better).
- "Appears twice" only needs equal values to be found, and **sorting puts
  equal values next to each other**, so one pass over neighbours suffices.
""",
        """
static boolean hasDuplicate(int[] a) {
    int[] b = a.clone();                 // do not reorder the caller's array
    java.util.Arrays.sort(b);            // O(n log n)
    for (int i = 1; i < b.length; i++) {
        if (b[i] == b[i - 1]) return true;   // equal values are now adjacent
    }
    return false;
}
""",
        [
            "`a.clone()` copies the input (O(n)) so the caller's order survives.",
            "`Arrays.sort(b)` costs O(n log n): about 1.7 × 10⁶ steps at n = 10⁵.",
            "After sorting, any repeated value sits in a block, so comparing each element with the one before it (`b[i] == b[i - 1]`) sees every repeat.",
            "If the loop finishes without a match, no two neighbours are equal, so no value repeats: return `false`.",
        ],
        "String.valueOf(hasDuplicate(new int[]{4, 1, 3, 1}))", "true",
        _trace("hasDuplicate([4, 1, 3, 1])", "After sorting, b = [1, 1, 3, 4].",
               ["i", "b[i-1]", "b[i]", "Equal?"],
               [["1", "1", "1", "yes: return true"]],
               "The repeat was found on the first comparison because sorting made it adjacent."),
        """
**Time O(n log n)** (the sort dominates the O(n) scan). **Space O(n)** for the
copy. A `HashSet` would give O(n) time; the point here is reading the budget:
both fit, O(n²) does not.
""",
    ),
    _solved(
        "Remove duplicates, keep the order (the hidden quadratic)", "Medium",
        """
Given `a` (`n ≤ 10⁵`), return the values in order of first appearance, each
once. `[3, 1, 3, 2, 1]` → `[3, 1, 2]`.
""",
        """
```java
List<Integer> out = new ArrayList<>();
for (int x : a) if (!out.contains(x)) out.add(x);
```

It *looks* like one loop, O(n). But `out.contains(x)` scans the whole list, up
to `n` elements, so the real cost is O(n²): the nesting hides behind a method
name.
""",
        """
- A **call inside a loop counts**: price `contains` on a `List` (O(n)) before
  you trust the single `for`.
- The inner question is *"have I seen x?"*, which a `HashSet` answers in O(1).
""",
        """
static java.util.List<Integer> dedupe(int[] a) {
    java.util.Set<Integer> seen = new java.util.HashSet<>();
    java.util.List<Integer> out = new java.util.ArrayList<>();
    for (int x : a) {
        if (seen.add(x)) out.add(x);   // add() returns false if x was already there
    }
    return out;
}
""",
        [
            "`seen` remembers every value passed so far; `out` keeps the order.",
            "`seen.add(x)` does the membership test **and** the insert in one O(1) call; it returns `true` only the first time `x` is added.",
            "Only on that first time is `x` appended to `out`, so each value appears once, in first-appearance order.",
        ],
        "String.valueOf(dedupe(new int[]{3, 1, 3, 2, 1}))", "[3, 1, 2]",
        _trace("dedupe([3, 1, 3, 2, 1])", "",
               ["x", "seen.add(x)", "seen after", "out after"],
               [["3", "true", "{3}", "[3]"],
                ["1", "true", "{1, 3}", "[3, 1]"],
                ["3", "false", "{1, 3}", "[3, 1]"],
                ["2", "true", "{1, 2, 3}", "[3, 1, 2]"],
                ["1", "false", "{1, 2, 3}", "[3, 1, 2]"]],
               "Every row is O(1) work, so five rows is five units of work, not 5 × |out|."),
        """
**Time O(n)**: n iterations of O(1) average work. **Space O(n)** for the set.
The fix changed one data structure, and the cost dropped from O(n²) to O(n).
""",
    ),
    _solved(
        "Next greater element (amortized O(n))", "Hard",
        """
For each index `i` of `a` (`n ≤ 10⁵`), output the first value to its right that
is larger than `a[i]`, or `-1` if there is none. `[2, 1, 4, 3]` → `[4, 4, -1, -1]`.
""",
        """
For each `i`, walk right until something bigger appears. In the worst case
(a decreasing array) each walk goes to the end: n + (n−1) + … ≈ n²/2 steps,
5 × 10⁹ at n = 10⁵. Too slow.
""",
        """
- `n ≤ 10⁵` again demands better than O(n²).
- Elements still *waiting* for their answer are always in decreasing order
  (a bigger one would have answered the smaller ones), which is a **stack**.
- The code will have a `while` inside a `for`; the amortized argument
  (each index pushed once, popped at most once) is what proves it linear.
""",
        """
static int[] nextGreater(int[] a) {
    int n = a.length;
    int[] ans = new int[n];
    java.util.Arrays.fill(ans, -1);              // default: no greater element
    java.util.Deque<Integer> st = new java.util.ArrayDeque<>();  // indices waiting
    for (int i = 0; i < n; i++) {
        while (!st.isEmpty() && a[st.peek()] < a[i]) {
            ans[st.pop()] = a[i];                // a[i] answers everyone smaller
        }
        st.push(i);                              // i now waits for its own answer
    }
    return ans;
}
""",
        [
            "`ans` starts as all `-1`: anything never answered keeps it.",
            "`st` holds indices whose answer is not known yet. Their values are decreasing from bottom to top.",
            "When `a[i]` arrives, every waiting index with a smaller value has found its first greater element: pop it and record `a[i]`.",
            "Then push `i`; it waits until something larger shows up.",
            "Counting: each index is pushed exactly once and popped at most once, so the `while` runs at most n times **in total**, not n times per `i`.",
        ],
        "java.util.Arrays.toString(nextGreater(new int[]{2, 1, 4, 3}))", "[4, 4, -1, -1]",
        _trace("nextGreater([2, 1, 4, 3])", "Stack shows values (bottom → top).",
               ["i", "a[i]", "Popped (answered)", "Stack after"],
               [["0", "2", "none", "[2]"],
                ["1", "1", "none", "[2, 1]"],
                ["2", "4", "1 → 4, 2 → 4", "[4]"],
                ["3", "3", "none", "[4, 3]"]],
               "Four pushes and two pops in total: 6 stack operations for n = 4, at most 2n in general."),
        """
**Time O(n) amortized**: at most n pushes and n pops overall. **Space O(n)** for
the stack and the answer. Nested loops do not automatically mean O(n²); count
the total work of the whole run.
""",
    ),
]

# ------------------------------------------------------------ hashing

_SOLVED["hashing"] = [
    _solved(
        "Two Sum", "Easy",
        """
Given `nums` and `target`, return the indices `[i, j]` (`i < j`) of the two
numbers that add up to `target`. Exactly one answer exists; `n ≤ 10⁵`.
""",
        """
Try every pair: O(n²), about 5 × 10⁹ checks at the limit. The inner loop is
*searching* for one specific value, `target − nums[i]`.
""",
        """
- "Find a pair with a given sum" in an **unsorted** array whose indices matter.
- The inner loop asks *"have I seen value v, and where?"*: an index map,
  `HashMap<value, index>`.
""",
        """
static int[] twoSum(int[] nums, int target) {
    java.util.Map<Integer, Integer> seen = new java.util.HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];             // the partner we would need
        Integer j = seen.get(need);
        if (j != null) return new int[]{j, i};   // partner already passed
        seen.put(nums[i], i);                    // record AFTER checking
    }
    return new int[0];
}
""",
        [
            "`seen` maps each value already passed to its index.",
            "For `nums[i]`, the only partner that works is `need = target − nums[i]`.",
            "`seen.get(need)` checks in O(1) whether that partner appeared earlier; if so, return both indices.",
            "Only then store `nums[i]`, so an element can never pair with itself (e.g. target 6, value 3).",
        ],
        "java.util.Arrays.toString(twoSum(new int[]{2, 7, 11, 15}, 9))", "[0, 1]",
        _trace("twoSum([2, 7, 11, 15], 9)", "",
               ["i", "nums[i]", "need", "In seen?", "seen after"],
               [["0", "2", "7", "no", "{2: 0}"],
                ["1", "7", "2", "yes, at 0: return [0, 1]", "{2: 0}"]],
               ""),
        "**Time O(n)**, one pass with O(1) lookups. **Space O(n)** for the map.",
    ),
    _solved(
        "Group anagrams", "Medium",
        """
Given a list of lowercase words, group the words that are anagrams of each
other (same letters, same counts), keeping groups in order of first appearance.
""",
        """
Compare every pair of words by sorting both and checking equality: O(n²) pairs,
each O(m log m) for words of length m. With n = 10⁴ that is 10⁸ comparisons of
sorted strings: too slow.
""",
        """
- "Group by some equivalence" means: **find a canonical form**, a key that is
  identical for every member of a group, and hash it.
- Sorted letters are such a key: `"eat"`, `"tea"`, `"ate"` all become `"aet"`.
""",
        """
static java.util.List<java.util.List<String>> groupAnagrams(String[] words) {
    java.util.Map<String, java.util.List<String>> groups = new java.util.LinkedHashMap<>();
    for (String w : words) {
        char[] cs = w.toCharArray();
        java.util.Arrays.sort(cs);
        String key = new String(cs);                         // canonical form
        groups.computeIfAbsent(key, k -> new java.util.ArrayList<>()).add(w);
    }
    return new java.util.ArrayList<>(groups.values());
}
""",
        [
            "`LinkedHashMap` keeps keys in insertion order, so groups come out in first-appearance order.",
            "Sorting the letters of `w` produces its canonical key; anagrams produce the same key.",
            "`computeIfAbsent` creates an empty list the first time a key is seen, then `add(w)` appends the word.",
            "The values of the map are the groups.",
        ],
        'String.valueOf(groupAnagrams(new String[]{"eat", "tea", "tan", "ate", "nat"}))',
        "[[eat, tea, ate], [tan, nat]]",
        _trace("groupAnagrams([eat, tea, tan, ate, nat])", "",
               ["Word", "Key", "Groups after"],
               [["eat", "aet", "aet: [eat]"],
                ["tea", "aet", "aet: [eat, tea]"],
                ["tan", "ant", "aet: [eat, tea], ant: [tan]"],
                ["ate", "aet", "aet: [eat, tea, ate], ant: [tan]"],
                ["nat", "ant", "aet: [eat, tea, ate], ant: [tan, nat]"]],
               "Each word is touched once; the map does the grouping."),
        """
**Time O(n · m log m)** for n words of length up to m (sorting each word).
A 26-count signature key makes it O(n · m). **Space O(n · m)** for the map.
""",
    ),
    _solved(
        "Longest consecutive sequence", "Hard",
        """
Given an unsorted array, return the length of the longest run of consecutive
integers (e.g. 1, 2, 3, 4) that can be formed from its values, in O(n).
`[100, 4, 200, 1, 3, 2]` → `4`.
""",
        """
Sort and scan for runs: O(n log n), which the "in O(n)" requirement forbids.
Or, for each value, count upward with repeated `contains` on the array: O(n²).
""",
        """
- Repeated *"is x + 1 present?"* questions: a `HashSet` makes each O(1).
- To avoid counting the same run many times, **start counting only at a run's
  first value**, the one whose `x − 1` is absent.
""",
        """
static int longestRun(int[] a) {
    java.util.Set<Integer> set = new java.util.HashSet<>();
    for (int x : a) set.add(x);
    int best = 0;
    for (int x : set) {
        if (set.contains(x - 1)) continue;   // not the start of a run
        int len = 1;
        while (set.contains(x + len)) len++; // walk the run upward
        best = Math.max(best, len);
    }
    return best;
}
""",
        [
            "Put every value in a set: O(n), and duplicates disappear.",
            "For each value, if `x − 1` exists, `x` is in the middle of some run; skip it.",
            "Otherwise `x` starts a run: count `x + 1`, `x + 2`, … while present.",
            "Each value is walked over by exactly one `while` (the one from its run's start), so all the `while`s together cost O(n).",
        ],
        "String.valueOf(longestRun(new int[]{100, 4, 200, 1, 3, 2}))", "4",
        _trace("longestRun([100, 4, 200, 1, 3, 2])", "Set = {1, 2, 3, 4, 100, 200}.",
               ["x", "x−1 in set?", "Run counted", "best"],
               [["1", "no", "1, 2, 3, 4 (len 4)", "4"],
                ["2", "yes: skip", "", "4"],
                ["3", "yes: skip", "", "4"],
                ["4", "yes: skip", "", "4"],
                ["100", "no", "100 (len 1)", "4"],
                ["200", "no", "200 (len 1)", "4"]],
               "Only the starts 1, 100 and 200 did any walking."),
        "**Time O(n)** amortized (each value is visited by one walk). **Space O(n)** for the set.",
    ),
]

# ------------------------------------------------------------ two pointers

_SOLVED["two-pointers"] = [
    _solved(
        "Valid palindrome", "Easy",
        """
Given a string `s`, return `true` if, after ignoring every character that is
not a letter or digit and ignoring case, it reads the same forwards and
backwards. `"A man, a plan, a canal: Panama"` → `true`.
""",
        """
Build a cleaned, lower-cased copy, then a reversed copy, and compare. It works
in O(n) time but uses O(n) extra memory for two new strings.
""",
        """
- "Reads the same from both ends" compares position `l` from the left with
  position `r` from the right: **converging pointers**.
- Skipping unwanted characters is just moving a pointer past them, so no copy
  is needed: O(1) space.
""",
        """
static boolean isPalindrome(String s) {
    int l = 0, r = s.length() - 1;
    while (l < r) {
        char a = s.charAt(l), b = s.charAt(r);
        if (!Character.isLetterOrDigit(a)) { l++; continue; }
        if (!Character.isLetterOrDigit(b)) { r--; continue; }
        if (Character.toLowerCase(a) != Character.toLowerCase(b)) return false;
        l++; r--;
    }
    return true;
}
""",
        [
            "Start `l` at the first character and `r` at the last.",
            "If either side is punctuation or a space, step past it and try again.",
            "Compare the two letters case-insensitively; one mismatch proves it is not a palindrome.",
            "On a match, move both inward. When they meet, every pair matched.",
        ],
        'String.valueOf(isPalindrome("race a car"))', "false",
        _trace('isPalindrome("race a car")', "Indices 0..9; position 4 is a space.",
               ["l", "r", "s[l]", "s[r]", "Action"],
               [["0", "9", "r", "r", "match, move in"],
                ["1", "8", "a", "a", "match, move in"],
                ["2", "7", "c", "c", "match, move in"],
                ["3", "6", "e", " ", "space on the right, r--"],
                ["3", "5", "e", "a", "mismatch: return false"]],
               ""),
        "**Time O(n)**: each step moves at least one pointer. **Space O(1)**.",
    ),
    _solved(
        "Two Sum II (sorted input)", "Medium",
        """
`numbers` is sorted ascending. Return the **1-based** indices `[i, j]` of the
two numbers adding to `target`, using only O(1) extra space.
""",
        """
The hash-map Two Sum works in O(n) time but uses O(n) space, which the
statement forbids. Checking every pair is O(1) space but O(n²) time.
""",
        """
- **Sorted** + **find a pair** + **O(1) space**: converging pointers. Sortedness
  tells you which pointer to move.
""",
        """
static int[] twoSumSorted(int[] numbers, int target) {
    int l = 0, r = numbers.length - 1;
    while (l < r) {
        int sum = numbers[l] + numbers[r];
        if (sum == target) return new int[]{l + 1, r + 1};
        if (sum < target) l++;     // need bigger: drop the smallest
        else r--;                  // need smaller: drop the largest
    }
    return new int[0];
}
""",
        [
            "Start with the smallest (`l`) and largest (`r`) values.",
            "If the sum is too small, `numbers[l]` is useless: even paired with the largest value left it falls short. Drop it with `l++`.",
            "If too big, `numbers[r]` is useless for the mirror reason: `r--`.",
            "Each step removes one candidate, so the loop runs at most n − 1 times.",
        ],
        "java.util.Arrays.toString(twoSumSorted(new int[]{2, 3, 4, 7, 11}, 10))", "[2, 4]",
        _trace("twoSumSorted([2, 3, 4, 7, 11], 10)", "",
               ["l", "r", "sum", "Decision"],
               [["0", "4", "2 + 11 = 13", "too big, r--"],
                ["0", "3", "2 + 7 = 9", "too small, l++"],
                ["1", "3", "3 + 7 = 10", "found: return [2, 4]"]],
               ""),
        "**Time O(n)**. **Space O(1)**: two integers, no map.",
    ),
    _solved(
        "Container with most water", "Hard",
        """
`height[i]` is the height of a vertical line at position `i`. Choose two lines
that, with the x-axis, hold the most water. Area = `(j − i) × min(height[i],
height[j])`. `n ≤ 10⁵`.
""",
        """
Try every pair: O(n²) ≈ 5 × 10⁹ at the limit. Sorting does not help, because
positions matter.
""",
        """
- A pair `(i, j)` scored by width and the *shorter* side.
- Start with the widest pair. Moving the **taller** side inward can only shrink
  the width without raising the limiting height, so it is never useful: always
  move the shorter side. Each move discards one line for good: converging
  pointers, without needing sorted input.
""",
        """
static int maxArea(int[] height) {
    int l = 0, r = height.length - 1, best = 0;
    while (l < r) {
        int area = (r - l) * Math.min(height[l], height[r]);
        best = Math.max(best, area);
        if (height[l] < height[r]) l++;   // the shorter side limits the area
        else r--;
    }
    return best;
}
""",
        [
            "Begin at maximum width, `l = 0`, `r = n − 1`.",
            "Score the current pair and keep the best.",
            "The shorter line is the bottleneck. Any other pair using it is narrower and still capped by it, so it can never beat the current area: discard it.",
            "Repeat until the pointers meet: n − 1 steps.",
        ],
        "String.valueOf(maxArea(new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7}))", "49",
        _trace("maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7])", "",
               ["l", "r", "Area", "best", "Move"],
               [["0", "8", "8 × 1 = 8", "8", "h[0]=1 shorter, l++"],
                ["1", "8", "7 × 7 = 49", "49", "h[8]=7 shorter, r--"],
                ["1", "7", "6 × 3 = 18", "49", "h[7]=3 shorter, r--"],
                ["1", "6", "5 × 8 = 40", "49", "tie, r--"],
                ["1", "5", "4 × 4 = 16", "49", "r--"],
                ["1", "4", "3 × 5 = 15", "49", "r--"],
                ["1", "3", "2 × 2 = 4", "49", "r--"],
                ["1", "2", "1 × 6 = 6", "49", "r--, pointers meet"]],
               "Eight pairs scored instead of 36."),
        "**Time O(n)**. **Space O(1)**.",
    ),
]

# ------------------------------------------------------------ sliding window

_SOLVED["sliding-window"] = [
    _solved(
        "Maximum sum of a window of size k", "Easy",
        """
Given `a` (`n ≤ 10⁵`) and `k` (`1 ≤ k ≤ n`), return the largest sum of any `k`
consecutive elements.
""",
        """
For each of the n − k + 1 starting positions, add up `k` elements: O(n · k),
which is O(n²) when `k` is about n/2 (2.5 × 10⁹ at the limit).
""",
        """
- "**Consecutive** elements" + "**every window of size k**": a fixed-size window.
- Neighbouring windows share k − 1 elements, so update the sum instead of
  recomputing it.
""",
        """
static int maxWindowSum(int[] a, int k) {
    int sum = 0, best = Integer.MIN_VALUE;
    for (int r = 0; r < a.length; r++) {
        sum += a[r];                       // a[r] enters
        if (r >= k) sum -= a[r - k];       // a[r - k] leaves
        if (r >= k - 1) best = Math.max(best, sum);   // window is full
    }
    return best;
}
""",
        [
            "`r` is the right edge; the window is `a[r−k+1..r]`.",
            "Each step adds the entering element.",
            "Once the window would exceed `k` elements (`r ≥ k`), subtract the one that just fell off the left, `a[r − k]`.",
            "From `r = k − 1` on, the window holds exactly `k` elements: record its sum.",
            "`best` starts at `MIN_VALUE` so all-negative arrays still work.",
        ],
        "String.valueOf(maxWindowSum(new int[]{2, 1, 5, 1, 3, 2}, 3))", "9",
        _trace("maxWindowSum([2, 1, 5, 1, 3, 2], k = 3)", "",
               ["r", "Enters", "Leaves", "sum", "best"],
               [["0", "2", "", "2", "(not full)"],
                ["1", "1", "", "3", "(not full)"],
                ["2", "5", "", "8", "8"],
                ["3", "1", "2", "7", "8"],
                ["4", "3", "1", "9", "9"],
                ["5", "2", "5", "6", "9"]],
               "Two operations per step, whatever k is."),
        "**Time O(n)**. **Space O(1)**.",
    ),
    _solved(
        "Longest substring without repeating characters", "Medium",
        """
Given a string `s` (`n ≤ 5 × 10⁴`), return the length of the longest substring
with no repeated character. `"abcabcbb"` → `3` (`"abc"`).
""",
        """
Check every substring for repeats: O(n²) substrings × O(n) to check each =
O(n³), about 10¹⁴ at the limit.
""",
        """
- "Longest **substring**" (contiguous) with a rule ("no repeats").
- The rule is monotone: if a window has no repeats, neither does any part of
  it. So when a repeat appears, shrinking from the left fixes it: a
  **variable-size window**.
""",
        """
static int longestUnique(String s) {
    int[] count = new int[128];          // occurrences of each ASCII char in the window
    int l = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        char c = s.charAt(r);
        count[c]++;                      // extend right
        while (count[c] > 1) {           // invalid: c appears twice
            count[s.charAt(l)]--;        // shrink from the left
            l++;
        }
        best = Math.max(best, r - l + 1);   // window is valid here
    }
    return best;
}
""",
        [
            "Window state: `count[c]`, how many times `c` is in `s[l..r]`.",
            "Add `s[r]`. Only the character just added can have become a repeat.",
            "While it is repeated, remove `s[l]` and advance `l`; this stops right after the earlier copy of `c` leaves.",
            "Now the window is valid; its length `r − l + 1` is a candidate.",
            "`l` and `r` only move right, so the total work is at most 2n steps.",
        ],
        'String.valueOf(longestUnique("abcabcbb"))', "3",
        _trace('longestUnique("abcabcbb")', "",
               ["r", "s[r]", "Shrink?", "Window", "best"],
               [["0", "a", "no", "a", "1"],
                ["1", "b", "no", "ab", "2"],
                ["2", "c", "no", "abc", "3"],
                ["3", "a", "drop a", "bca", "3"],
                ["4", "b", "drop b", "cab", "3"],
                ["5", "c", "drop c", "abc", "3"],
                ["6", "b", "drop a, b", "cb", "3"],
                ["7", "b", "drop c, b", "b", "3"]],
               ""),
        "**Time O(n)** (each character enters and leaves once). **Space O(1)**: a fixed 128-entry table.",
    ),
    _solved(
        "Shortest subarray with sum at least target", "Hard",
        """
Given **positive** integers `a` (`n ≤ 10⁵`) and `target`, return the length of
the shortest contiguous subarray whose sum is `≥ target`, or `0` if none.
""",
        """
For every start, extend until the sum reaches `target`: O(n²) in the worst
case (5 × 10⁹ at the limit).
""",
        """
- "Shortest **subarray**" with a sum condition.
- All values are **positive**, so growing a window raises its sum and shrinking
  lowers it: the condition behaves monotonically, which a window needs.
- *Shortest* means: record the answer **inside** the shrink loop, while the
  window is still valid.
""",
        """
static int minSubarrayLen(int target, int[] a) {
    int l = 0, sum = 0, best = Integer.MAX_VALUE;
    for (int r = 0; r < a.length; r++) {
        sum += a[r];                         // grow until it is big enough
        while (sum >= target) {              // valid: try to make it shorter
            best = Math.min(best, r - l + 1);
            sum -= a[l++];
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}
""",
        [
            "Grow the window to the right, adding each element.",
            "As soon as the sum reaches `target`, the window is a candidate: record its length.",
            "Then shrink from the left while it stays valid, recording each shorter candidate. Positivity guarantees no shorter window ending at `r` was missed.",
            "If nothing ever qualified, `best` is untouched: return 0.",
        ],
        "String.valueOf(minSubarrayLen(7, new int[]{2, 3, 1, 2, 4, 3}))", "2",
        _trace("minSubarrayLen(7, [2, 3, 1, 2, 4, 3])", "",
               ["r", "a[r]", "sum after add", "Shrinks (length recorded)", "best"],
               [["0", "2", "2", "", "∞"],
                ["1", "3", "5", "", "∞"],
                ["2", "1", "6", "", "∞"],
                ["3", "2", "8", "len 4, drop 2 → 6", "4"],
                ["4", "4", "10", "len 4, drop 3 → 7; len 3, drop 1 → 6", "3"],
                ["5", "3", "9", "len 3, drop 2 → 7; len 2, drop 4 → 3", "2"]],
               "The answer [4, 3] was found while shrinking, which is where shortest-window answers live."),
        """
**Time O(n)**: `l` and `r` each move at most n times. **Space O(1)**. With
negative numbers this breaks (shrinking could raise the sum); use prefix sums.
""",
    ),
]

# ------------------------------------------------------------ prefix sums

_SOLVED["prefix-sums"] = [
    _solved(
        "Many range-sum queries", "Easy",
        """
Given `a` (`n ≤ 10⁵`) and `q ≤ 10⁵` queries `(l, r)`, return the sum of
`a[l..r]` for each.
""",
        """
Loop from `l` to `r` per query: up to O(n) each, O(n · q) = 10¹⁰ in total.
""",
        """
- **Many** questions about **ranges** of a **fixed** array: precompute once,
  answer each in O(1) with `pre[r + 1] − pre[l]`.
""",
        """
static long[] rangeSums(int[] a, int[][] queries) {
    long[] pre = new long[a.length + 1];          // pre[0] = 0
    for (int i = 0; i < a.length; i++) pre[i + 1] = pre[i] + a[i];
    long[] out = new long[queries.length];
    for (int k = 0; k < queries.length; k++) {
        int l = queries[k][0], r = queries[k][1];
        out[k] = pre[r + 1] - pre[l];             // indices l..r
    }
    return out;
}
""",
        [
            "`pre` has `n + 1` entries; `pre[i]` is the sum of the first `i` elements.",
            "Each `pre[i + 1]` is the previous total plus `a[i]`: one pass.",
            "A query subtracts the total before `l` from the total through `r`.",
            "`long` avoids overflow: 10⁵ values of 10⁹ exceed `int`.",
        ],
        "java.util.Arrays.toString(rangeSums(new int[]{3, 1, 4, 1, 5}, new int[][]{{1, 3}, {0, 4}, {2, 2}}))",
        "[6, 14, 4]",
        _trace("rangeSums([3, 1, 4, 1, 5])", "pre = [0, 3, 4, 8, 9, 14].",
               ["Query", "pre[r+1]", "pre[l]", "Answer"],
               [["(1, 3)", "pre[4] = 9", "pre[1] = 3", "6"],
                ["(0, 4)", "pre[5] = 14", "pre[0] = 0", "14"],
                ["(2, 2)", "pre[3] = 8", "pre[2] = 4", "4"]],
               ""),
        "**Time O(n + q)**. **Space O(n)** for `pre`.",
    ),
    _solved(
        "Count subarrays summing to k (with negatives)", "Medium",
        """
Given `a` (values may be **negative**, `n ≤ 2 × 10⁴`) and `k`, count the
contiguous subarrays whose sum is exactly `k`.
""",
        """
Every `(l, r)` pair with a running sum: O(n²) = 4 × 10⁸, borderline at best.
A sliding window does not apply: with negatives, shrinking can raise the sum.
""",
        """
- "Count **subarrays** with sum exactly k" + **negative numbers**: prefix sums
  plus a hash map.
- `sum(a[l..r]) = pre[r+1] − pre[l] = k` means `pre[l] = pre[r+1] − k`: a
  *complement* lookup, exactly like Two Sum, but over prefix values.
""",
        """
static int countSumK(int[] a, int k) {
    java.util.Map<Long, Integer> seen = new java.util.HashMap<>();
    seen.put(0L, 1);                     // the empty prefix
    long run = 0;
    int count = 0;
    for (int x : a) {
        run += x;                                    // pre of everything so far
        count += seen.getOrDefault(run - k, 0);      // earlier prefixes that complete k
        seen.merge(run, 1, Integer::sum);            // record this prefix
    }
    return count;
}
""",
        [
            "`seen` counts how many earlier prefixes had each total.",
            "`seen.put(0L, 1)`: the empty prefix exists, so a subarray starting at index 0 can be counted.",
            "At each element, every earlier prefix equal to `run − k` starts a subarray ending here with sum `k`.",
            "Record `run` afterwards, so a subarray is never empty.",
        ],
        "String.valueOf(countSumK(new int[]{1, -1, 1, 1}, 1))", "5",
        _trace("countSumK([1, -1, 1, 1], k = 1)", "",
               ["x", "run", "run − k", "Found", "count", "seen after"],
               [["1", "1", "0", "1", "1", "{0:1, 1:1}"],
                ["-1", "0", "-1", "0", "1", "{0:2, 1:1}"],
                ["1", "1", "0", "2", "3", "{0:2, 1:2}"],
                ["1", "2", "1", "2", "5", "{0:2, 1:2, 2:1}"]],
               "The five subarrays: [1] (index 0), [1, -1, 1], [-1, 1, 1], [1] (index 2), [1] (index 3)."),
        "**Time O(n)**. **Space O(n)** for the map.",
    ),
    _solved(
        "Apply many range additions (difference array)", "Hard",
        """
Start with `n` zeros. Apply `u ≤ 10⁵` updates `(l, r, v)`: add `v` to every
index in `l..r`. Return the final array. `n ≤ 10⁵`.
""",
        """
Loop over `l..r` for each update: O(n) per update, O(n · u) = 10¹⁰ in total.
""",
        """
- **Many range updates**, and the result is only read **at the end**: record
  each update at its two edges, then take a single prefix sum.
- It is prefix sums run backwards: a difference array is what you take the
  prefix sum *of*.
""",
        """
static long[] applyUpdates(int n, int[][] updates) {
    long[] diff = new long[n + 1];
    for (int[] u : updates) {
        diff[u[0]] += u[2];          // +v starts at l
        diff[u[1] + 1] -= u[2];      // and stops after r
    }
    long[] out = new long[n];
    long run = 0;
    for (int i = 0; i < n; i++) {
        run += diff[i];              // prefix sum turns edges into ranges
        out[i] = run;
    }
    return out;
}
""",
        [
            "`diff[i]` stores how much the value *changes* when stepping onto index `i`.",
            "An update adds `v` from `l` onward and cancels it from `r + 1` onward: two O(1) writes.",
            "The running sum of `diff` is the actual value at each index.",
            "`diff` has `n + 1` slots so `r + 1 = n` needs no special case.",
        ],
        "java.util.Arrays.toString(applyUpdates(5, new int[][]{{1, 3, 2}, {2, 4, 3}, {0, 2, -2}}))",
        "[-2, 0, 3, 5, 3]",
        _trace("applyUpdates(5, [(1,3,+2), (2,4,+3), (0,2,−2)])",
               "diff after the updates = [−2, 2, 3, 2, −2, −3].",
               ["i", "diff[i]", "run = out[i]"],
               [["0", "-2", "-2"], ["1", "2", "0"], ["2", "3", "3"],
                ["3", "2", "5"], ["4", "-2", "3"]],
               ""),
        "**Time O(n + u)**. **Space O(n)**.",
    ),
]

# ------------------------------------------------------------ strings

_SOLVED["strings"] = [
    _solved(
        "Valid anagram", "Easy",
        """
Given lowercase strings `s` and `t`, return `true` if `t` is a rearrangement of
`s` (same letters, same counts).
""",
        """
Sort both and compare: O(n log n), fine but not optimal. Removing each letter
of `t` from a copy of `s` with `indexOf` is O(n²).
""",
        """
- **Lowercase letters only**: 26 possible keys, so an `int[26]` count table
  (`c − 'a'` as the index) beats both sorting and a `HashMap`.
""",
        """
static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] freq = new int[26];
    for (int i = 0; i < s.length(); i++) {
        freq[s.charAt(i) - 'a']++;      // count s up
        freq[t.charAt(i) - 'a']--;      // count t down
    }
    for (int f : freq) if (f != 0) return false;
    return true;
}
""",
        [
            "Different lengths can never be anagrams.",
            "`c − 'a'` turns a letter into a box 0..25.",
            "Add one for each letter of `s`, subtract one for each letter of `t`.",
            "Anagrams cancel out exactly, so every box must end at zero.",
        ],
        'String.valueOf(isAnagram("rat", "tar"))', "true",
        _trace('isAnagram("rat", "tar")', "Only the boxes a, r, t are shown.",
               ["i", "s[i] (+1)", "t[i] (−1)", "a, r, t after"],
               [["0", "r", "t", "0, 1, −1"],
                ["1", "a", "a", "0, 1, −1"],
                ["2", "t", "r", "0, 0, 0"]],
               "All zero: anagrams."),
        "**Time O(n)**. **Space O(1)**: 26 counters regardless of n.",
    ),
    _solved(
        "Run-length compression", "Medium",
        """
Compress a string by replacing each run of a repeated character with the
character followed by the run length: `"aaabccdddd"` → `"a3b1c2d4"`.
`n ≤ 10⁵`.
""",
        """
```java
String out = "";
for (...) out += c + count;
```

Correct, but each `+=` copies the whole output so far: O(n²) characters copied
in total, around 5 × 10⁹ at the limit.
""",
        """
- **Building** a string piece by piece in a loop: use a `StringBuilder`.
- "Runs" of equal characters: scan with an index and count while the next
  character matches.
""",
        """
static String compress(String s) {
    StringBuilder sb = new StringBuilder();
    int i = 0;
    while (i < s.length()) {
        char c = s.charAt(i);
        int j = i;
        while (j < s.length() && s.charAt(j) == c) j++;   // end of this run
        sb.append(c).append(j - i);                        // char + run length
        i = j;                                             // next run starts here
    }
    return sb.toString();
}
""",
        [
            "`i` marks the start of the current run.",
            "Advance `j` while the character equals `c`; `j − i` is the run length.",
            "Append `c` and the length to the builder: amortized O(1) per character appended.",
            "Jump `i` to `j`. Every index is visited once across both loops.",
        ],
        'compress("aaabccdddd")', "a3b1c2d4",
        _trace('compress("aaabccdddd")', "",
               ["i", "c", "j", "Appended", "sb"],
               [["0", "a", "3", "a3", "a3"],
                ["3", "b", "4", "b1", "a3b1"],
                ["4", "c", "6", "c2", "a3b1c2"],
                ["6", "d", "10", "d4", "a3b1c2d4"]],
               ""),
        "**Time O(n)**. **Space O(n)** for the output.",
    ),
    _solved(
        "Longest palindromic substring", "Hard",
        """
Given `s` (`n ≤ 1000`), return its longest substring that reads the same both
ways. `"babad"` → `"bab"` (`"aba"` is also correct; return the first found).
""",
        """
Check all O(n²) substrings, each in O(n): O(n³) = 10⁹ at n = 1000, too slow.
""",
        """
- Every palindrome has a **centre**: a character (odd length) or a gap between
  two characters (even length). There are 2n − 1 centres.
- Growing outward from a centre checks each longer palindrome in O(1), because
  the inside was already confirmed: O(n) per centre, O(n²) total, which fits
  `n ≤ 1000`.
""",
        """
static String longestPalindrome(String s) {
    int bestL = 0, bestLen = 0;
    for (int c = 0; c < s.length(); c++) {
        for (int odd = 1; odd >= 0; odd--) {        // centre on c, then on the gap after c
            int l = c, r = c + 1 - odd;
            while (l >= 0 && r < s.length() && s.charAt(l) == s.charAt(r)) {
                l--; r++;                           // grow while the ends match
            }
            int len = r - l - 1;                    // the last palindrome was l+1..r-1
            if (len > bestLen) { bestLen = len; bestL = l + 1; }
        }
    }
    return s.substring(bestL, bestL + bestLen);
}
""",
        [
            "For each index `c`, try two centres: the character itself (`l = r = c`) and the gap after it (`l = c`, `r = c + 1`).",
            "Grow outward while both ends exist and match.",
            "When the loop stops, the ends no longer match, so the palindrome is `l + 1 .. r − 1`, length `r − l − 1`.",
            "Keep the longest; take one `substring` at the very end (a single O(n) copy).",
        ],
        'longestPalindrome("babad")', "bab",
        _trace('longestPalindrome("babad")', "Only odd centres shown; even centres find nothing longer than 0 here.",
               ["Centre c", "Grows to", "Palindrome", "Best"],
               [["0 (b)", "0..0", "b", "b"],
                ["1 (a)", "0..2", "bab", "bab"],
                ["2 (b)", "1..3", "aba", "bab (not longer)"],
                ["3 (a)", "3..3", "a", "bab"],
                ["4 (d)", "4..4", "d", "bab"]],
               ""),
        "**Time O(n²)**: 2n − 1 centres, each growing at most n/2 steps. **Space O(1)** besides the answer.",
    ),
]


def _attach_solved():
    by_key = {u["key"]: u for u in _UNITS}
    for key, examples in _SOLVED.items():
        assert key in by_key, f"dsa_s2_solved.py: no unit {key!r}"
        assert len(examples) >= 3, f"{key}: want at least three solved examples"
        ranks = [("Easy", "Medium", "Hard").index(e["difficulty"]) for e in examples]
        assert ranks == sorted(ranks), f"{key}: solved examples must go easy → harder"
        for e in examples:
            if e["trace"]:
                hs = e["trace"]["headers"]
                assert all(len(r) == len(hs) for r in e["trace"]["rows"]), \
                    f"{key}/{e['title']}: a trace row does not match its headers"
        by_key[key]["solved_examples"] = list(examples)


_attach_solved()
