# -*- coding: utf-8 -*-
"""Sliding window, sections 9-16: Complexity → Mastery.

The "Recognize → Apply → Combine → Master" half of the progression.
"""

from new_dsa_kit import code, exercise, md, quiz
import new_dsa_sw_refs as R

T = "ndsa:sliding-window"


# ---------------------------------------------------------------------------
# 9. Complexity
# ---------------------------------------------------------------------------

COMPLEXITY = {
    "time": "O(n)",
    "space": "O(1) for a sum or a counter · O(min(n, σ)) for a Map or Set (σ = alphabet size)",
    "body": md("""
        ### Where the O(n) comes from

        A `while` inside a `for` looks like O(n²). It is not, and the reason is
        worth being able to say out loud: **count pointer moves, not loop
        nesting.**

        - `hi` moves forward exactly `n` times, once per `for` iteration.
        - Every pass through the `while` body moves `lo` forward once, and `lo`
          never moves back and never passes `n`. So across the **whole run**
          the `while` body executes at most `n` times, however those runs are
          spread over the steps.

        That is at most `2n` pointer moves, each doing O(1) work on the summary:
        **O(n) total**. Any single step can be expensive (one step may release
        many elements), but the cost averages out. That is what *amortised O(1)
        per step* means.

        ### Where the space comes from

        The window's contents are never copied, because they are already in the
        array. Only the summary costs memory. A running sum or a zero counter is
        O(1). A `Map` of counts holds at most one key per distinct value in the
        window: bounded by the window length and by the alphabet, so
        O(min(n, σ)). For lowercase letters that is at most 26: effectively O(1).
    """),
    "compare": [
        {"approach": "Every window, re-summed from scratch", "time": "O(n³)", "space": "O(1)",
         "note": "n²/2 windows × up to n reads each."},
        {"approach": "Every start, extend with a running sum", "time": "O(n²)", "space": "O(1)",
         "note": "Reuses the sum while extending one start, but still visits every window."},
        {"approach": "Sliding window", "time": "O(n)", "space": "O(1) – O(σ)",
         "note": "Reuses the overlap between neighbours *and* skips windows that cannot win."},
    ],
    "why_improved": md("""
        Two separate savings. **Reuse** takes O(n³) down to O(n²): a window's
        summary is updated from its neighbour's, not rebuilt. **Skipping** takes
        O(n²) down to O(n): because the rule survives shrinking, once `[lo, hi]`
        is invalid no window starting at or before `lo` and ending later can be
        valid, so `lo` only moves forward. At `n = 10^5` that is the difference
        between 10¹⁰ steps (minutes) and 2·10⁵ (about a millisecond).
    """),
    "rewrite": {
        "slow": code("""
            // O(n · k): rebuilds each window
            for (let hi = k - 1; hi < nums.length; hi++) {
              const sum = nums.slice(hi - k + 1, hi + 1).reduce((a, b) => a + b, 0);
              best = Math.max(best, sum);
            }
        """),
        "fast": code("""
            // O(n): updates the window
            for (let hi = 0; hi < nums.length; hi++) {
              sum += nums[hi];
              if (hi >= k) sum -= nums[hi - k];
              if (hi >= k - 1) best = Math.max(best, sum);
            }
        """),
        "edit": "Replace the rebuild (`slice` + `reduce`, O(k)) with one add and one subtract (O(1)).",
    },
    "questions": [
        quiz(
            "What is the time complexity of this function?",
            ["O(n)", "O(n²)", "O(n log n)", "O(n · k)"],
            0,
            """
                `lo` only moves forward and never passes `n`, so the `while` body
                runs at most `n` times **in total** over the whole run, not per
                step. `n` moves of `hi` plus at most `n` of `lo` is O(n).
            """,
            why_not={
                1: "That would be true if `lo` restarted from 0 on each iteration. It never moves back, so the inner loop's work is shared across all steps.",
                2: "Nothing is sorted or halved here.",
                3: "There is no `k` in this rule. The shrink is bounded by `n` moves overall.",
            },
            code_src="""
                function f(nums: number[], limit: number): number {
                  let lo = 0, sum = 0, best = 0;
                  for (let hi = 0; hi < nums.length; hi++) {
                    sum += nums[hi];
                    while (sum > limit) sum -= nums[lo++];
                    best = Math.max(best, hi - lo + 1);
                  }
                  return best;
                }
            """,
        ),
        quiz(
            "And this one? (n = nums.length)",
            ["O(n · k)", "O(n)", "O(k)", "O(n²) regardless of k"],
            0,
            """
                There are about `n − k + 1` windows, and each builds a fresh
                `slice` of length `k` and sums it: O(n · k). It is correct, but it
                is not a sliding window. Nothing is carried from one step to the
                next.
            """,
            why_not={
                1: "`slice` and `reduce` are hidden loops: each costs O(k) per step.",
                2: "That is the cost of *one* window, not of all of them.",
                3: "When k ≈ n/2 it is quadratic, but for small k it is nearly linear. The honest answer mentions k.",
            },
            code_src="""
                for (let hi = k - 1; hi < nums.length; hi++) {
                  const w = nums.slice(hi - k + 1, hi + 1);
                  best = Math.max(best, w.reduce((a, b) => a + b, 0));
                }
            """,
        ),
        quiz(
            "`longestKDistinct(s, k)` with a `Map` of counts, where `s` is lowercase letters. What is the extra space?",
            ["O(min(k, σ)): at most k + 1 keys, and never more than the 26 letters",
             "O(n): the Map can hold the whole string",
             "O(k²)",
             "O(1) whatever the alphabet"],
            0,
            """
                The Map holds one key per distinct character **in the window**. The
                repair keeps that at most `k` (briefly `k + 1` before shrinking),
                and it can never exceed the alphabet size σ.
            """,
            why_not={
                1: "Keys are distinct characters, not positions. `\"aaaa…\"` of any length is one key.",
                2: "Nothing is quadratic here. There is one key per distinct character.",
                3: "It is O(1) only *because* the alphabet is fixed at 26. For arbitrary numbers it would be O(k).",
            },
        ),
    ],
}


# ---------------------------------------------------------------------------
# 10. Common mistakes
# ---------------------------------------------------------------------------

MISTAKES = [
    {
        "title": "Measuring before repairing (longest variant)",
        "category": "Logic",
        "wrong": code("""
            absorb(nums[hi]);
            best = Math.max(best, hi - lo + 1);   // window may be invalid here
            while (invalid()) release(nums[lo++]);
        """),
        "why": "It feels natural to record right after growing.",
        "recognise": "The answer is sometimes one too big: it counts a window that breaks the rule.",
        "right": code("""
            absorb(nums[hi]);
            while (invalid()) release(nums[lo++]);
            best = Math.max(best, hi - lo + 1);   // valid by construction
        """),
    },
    {
        "title": "Measuring after the loop (shortest variant)",
        "category": "Logic",
        "wrong": code("""
            while (sum >= target) sum -= nums[lo++];
            best = Math.min(best, hi - lo + 1);   // the window is now INVALID
        """),
        "why": "Copying the longest-variant template without flipping where you measure.",
        "recognise": "Answers are one too short, or you report windows whose sum is below target.",
        "right": code("""
            while (sum >= target) {
              best = Math.min(best, hi - lo + 1); // measure while still valid
              sum -= nums[lo++];
            }
        """),
    },
    {
        "title": "Length off by one",
        "category": "Off-by-one",
        "wrong": code("best = Math.max(best, hi - lo);"),
        "why": "`hi − lo` is the distance between the edges, not the number of elements.",
        "recognise": "Every answer is exactly one short. A one-element window measures as 0.",
        "right": code("best = Math.max(best, hi - lo + 1);   // both ends inclusive"),
    },
    {
        "title": "`if` instead of `while` when shrinking",
        "category": "Boundary",
        "wrong": code("if (sum > limit) sum -= nums[lo++];"),
        "why": "Usually one release is enough, so tests on small inputs pass.",
        "recognise": "Fails when one large element enters: after one release the window is still invalid, and gets measured anyway.",
        "right": code("while (sum > limit) sum -= nums[lo++];"),
    },
    {
        "title": "Measuring a fixed window before it is full",
        "category": "Boundary",
        "wrong": code("""
            sum += nums[hi];
            if (hi >= k) sum -= nums[hi - k];
            best = Math.max(best, sum);          // measures windows of size 1..k-1
        """),
        "why": "The guard on the release looks sufficient.",
        "recognise": "Wrong only when a partial window happens to win, for example with negative numbers, where a short prefix beats every full window.",
        "right": code("if (hi >= k - 1) best = Math.max(best, sum);"),
    },
    {
        "title": "Starting a minimum at 0",
        "category": "Initialisation",
        "wrong": code("""
            let best = 0;
            best = Math.min(best, hi - lo + 1);  // always 0
        """),
        "why": "Copied from the maximum version, where 0 is a fine start.",
        "recognise": "The function returns 0 on every input.",
        "right": code("""
            let best = Infinity;
            // …
            return best === Infinity ? 0 : best;
        """),
    },
    {
        "title": "`counts.get(c) + 1`",
        "category": "TypeScript",
        "wrong": code("counts.set(c, counts.get(c) + 1);"),
        "why": "In JavaScript it would give `NaN` the first time. TypeScript stops it at compile time.",
        "recognise": "Compile error TS2532: *Object is possibly 'undefined'*. (Silencing it with `!` just brings the `NaN` back.)",
        "right": code("counts.set(c, (counts.get(c) ?? 0) + 1);"),
    },
    {
        "title": "Leaving zero counts in the Map",
        "category": "Built-ins",
        "wrong": code("counts.set(out, counts.get(out)! - 1);   // may leave out → 0"),
        "why": "Decrementing feels like the whole job.",
        "recognise": "`counts.size` keeps growing. The window shrinks far too much, and answers come out too small.",
        "right": code("""
            const left = counts.get(out)! - 1;
            if (left === 0) counts.delete(out);
            else counts.set(out, left);
        """),
    },
    {
        "title": "Rebuilding the window every step",
        "category": "Complexity",
        "wrong": code("""
            // inside the loop:
            if (new Set(s.slice(lo, hi + 1)).size > k) { /* … */ }
        """),
        "why": "`slice` and `new Set` look like single operations.",
        "recognise": "Correct on the examples, then *Time limit exceeded*: the loop is O(n · window).",
        "right": code("// keep a Map summary and update it by one element per step"),
    },
    {
        "title": "`shift()` as a queue",
        "category": "Built-ins",
        "wrong": code("const front = dq.shift();   // re-indexes the whole array"),
        "why": "It reads like a deque's pop-front.",
        "recognise": "The deque variation times out on large inputs even though the algorithm is O(n).",
        "right": code("const front = dq[head++];    // O(1): keep a head index"),
    },
    {
        "title": "`for … in` over a string",
        "category": "TypeScript",
        "wrong": code("""
            for (const i in s) {
              best = Math.max(best, i - lo + 1);   // i is "0", "1", … — a string
            }
        """),
        "why": "`for … in` loops over *keys*, and array/string keys are strings.",
        "recognise": "TS2362: *The left-hand side of an arithmetic operation must be of type 'any', 'number', …*. In plain JavaScript, `\"1\" + 1` would give `\"11\"`.",
        "right": code("for (let hi = 0; hi < s.length; hi++) { /* … */ }"),
    },
    {
        "title": "Assuming the values are non-negative",
        "category": "Assumptions",
        "wrong": code("""
            // "subarray sum ≤ limit" when nums may contain negatives
            while (sum > limit) sum -= nums[lo++];
        """),
        "why": "The template worked on the last three problems.",
        "recognise": "Wrong answers only on tests with negative numbers. Read the constraints line before choosing.",
        "right": code("// negatives break “validity survives shrinking” — use prefix sums instead"),
    },
]


# ---------------------------------------------------------------------------
# 11. Problem recognition
# ---------------------------------------------------------------------------

FIXED = "Sliding window: fixed size"
VAR = "Sliding window: variable size"
PREFIX = "Prefix sums + hash map"
TWO_PTR = "Two pointers from both ends (sorted input)"
DP = "Dynamic programming"
HASH = "Hash set / map, no window"
BINARY = "Binary search"
DEQUE = "Sliding window + monotonic deque"

RECOGNITION = {
    "intro": md("""
        No code. Read each scenario and name the tool you would reach for
        **before** thinking about how to write it. Several are deliberately
        *not* sliding windows. A wrong answer shows why that option does not
        fit.
    """),
    "questions": [
        quiz("A delivery log records how many parcels arrived each minute. Find the busiest stretch of exactly 60 consecutive minutes.",
             [FIXED, VAR, PREFIX, DP], 0,
             "“Exactly 60 consecutive” fixes the width. One minute enters and one leaves per step.",
             why_not={1: "Nothing decides when to shrink: the width is given.",
                      2: "It would work (each window is a prefix difference), but a fixed window needs no extra array and states the problem directly.",
                      3: "No choices to combine, just one sum per window."}),
        quiz("Find the longest stretch of days in which you spent at most B dollars in total. Spending is never negative.",
             [VAR, FIXED, PREFIX, BINARY], 0,
             "Longest + at-most budget + non-negative values. Shrinking never breaks “≤ B”, so this is the variable window.",
             why_not={1: "The length is what you are looking for, so it cannot be fixed.",
                      2: "Needed if spending could be negative. It cannot, so the window is simpler and O(1) space.",
                      3: "Binary search on the length plus a check works in O(n log n). The window is O(n)."}),
        quiz("Count the subarrays whose sum is exactly K. The values can be negative.",
             [PREFIX, VAR, FIXED, TWO_PTR], 0,
             "Negatives break the window's monotone rule. Count pairs of prefix sums that differ by K with a hash map.",
             why_not={1: "With negative values, shrinking can raise the sum, so `lo` would have to move back.",
                      2: "No width is given.",
                      3: "Nothing is sorted, and the answer is a range, not a pair."}),
        quiz("In a sorted array, find two numbers that add up to the target.",
             [TWO_PTR, VAR, FIXED, DP], 0,
             "A pair, not a range, in sorted input: move inward from both ends.",
             why_not={1: "The answer is two elements, not a contiguous run between them.",
                      2: "There is no range of size k here.",
                      3: "No overlapping subproblems. One linear scan decides it."}),
        quiz("Find the length of the longest strictly increasing subsequence (elements need not be adjacent).",
             [DP, VAR, FIXED, HASH], 0,
             "“Subsequence” allows gaps, so there is no contiguous window. This is LIS, a DP problem.",
             why_not={1: "A window is contiguous by definition. Skipping elements is exactly what it cannot do.",
                      2: "No fixed width, and elements may be skipped.",
                      3: "Membership does not capture order."}),
        quiz("For every window of 30 consecutive temperature readings, report the maximum.",
             [DEQUE, FIXED, VAR, BINARY], 0,
             "A fixed window whose summary is a **maximum**, which cannot be un-added when an element leaves. A monotonic deque keeps the candidates in O(1) amortised.",
             why_not={1: "Close, but a running max has no “subtract”: when the maximum leaves, you would have to rescan the window, O(n · k).",
                      2: "The width is fixed at 30.",
                      3: "Nothing is sorted."}),
        quiz("Does the text contain a substring that is a rearrangement (anagram) of the pattern “abc”?",
             [FIXED, VAR, HASH, DP], 0,
             "Every anagram of the pattern has the pattern's length: a fixed window of letter counts, compared with the pattern's counts.",
             why_not={1: "The candidate length is known in advance (3), so nothing needs to grow or shrink by a rule.",
                      2: "A set of whole substrings would be O(n · m). The window updates counts by one letter per step.",
                      3: "There is nothing to optimise, only a yes/no per window."}),
        quiz("Find the shortest run of consecutive songs whose total length is at least 60 minutes.",
             [VAR, FIXED, PREFIX, TWO_PTR], 0,
             "Shortest + at-least + positive lengths: the variable window's shortest shape, measured inside the shrink.",
             why_not={1: "The length is the unknown.",
                      2: "Works, but needs an extra array or a search. Positive lengths make the window enough.",
                      3: "It is a range, not a pair."}),
        quiz("Has any value appeared twice anywhere in the array?",
             [HASH, VAR, FIXED, BINARY], 0,
             "No range, no order: one pass with a Set answers it.",
             why_not={1: "The question is about the whole array, not a range inside it.",
                      2: "No width is involved.",
                      3: "Sorting first and scanning neighbours works in O(n log n). A Set is O(n)."}),
        quiz("You need to find the first occurrence of a value ≥ x in a sorted array.",
             [BINARY, VAR, FIXED, HASH], 0,
             "Sorted + first position satisfying a monotone condition: binary search (lower bound), O(log n).",
             why_not={1: "Scanning with a window would be O(n) and ignores that the input is sorted.",
                      2: "No range of fixed width is involved.",
                      3: "A hash lookup finds equal values, not the first one ≥ x."}),
    ],
}


# ---------------------------------------------------------------------------
# 12. Guided practice
# ---------------------------------------------------------------------------

GUIDED = [
    {
        "key": "max-vowels",
        "title": "Maximum vowels in a substring of length k",
        "problem": md("""
            Given a lowercase string `s` and an integer `k`
            (`1 ≤ k ≤ s.length ≤ 10^5`), return the **maximum number of vowels**
            (`a e i o u`) in any substring of length `k`.
        """),
        "examples": [
            {"input": 's = "abciiidef", k = 3', "output": str(R.max_vowels("abciiidef", 3)), "note": '"iii"'},
            {"input": 's = "aeiou", k = 2', "output": str(R.max_vowels("aeiou", 2)), "note": "any two letters"},
            {"input": 's = "leetcode", k = 3', "output": str(R.max_vowels("leetcode", 3)), "note": '"lee", "eet" or "ode"'},
        ],
        "understand": quiz(
            'For s = "rhythms", k = 4, what should the function return?',
            ["0", "1", "4", "Nothing: it should throw"], 0,
            "No substring contains a vowel, so the maximum is 0. The input is valid, and 0 is a real answer.",
            why_not={1: "Count the vowels in “rhythms”: there are none (y is not in the list).",
                     2: "4 is the window length, not the vowel count.",
                     3: "1 ≤ k ≤ length holds, so the input is valid. It just has no vowels."},
        ),
        "identify": quiz(
            "Which technique fits?",
            [FIXED, VAR, PREFIX, DP], 0,
            "“Substring of length k” fixes the width. Every candidate has the same size, and one letter enters and one leaves per step.",
            why_not={1: "Nothing makes the window shrink. The width is given.",
                     2: "A prefix count of vowels would work, but it is an extra array. The window keeps the count in one variable.",
                     3: "There is no choice to optimise over, only one count per window."},
        ),
        "approach": quiz(
            "What is the smallest summary the window needs?",
            ["The number of vowels inside it", "The substring itself", "A Map of every letter's count", "The index of the last vowel"], 0,
            "One integer: +1 if the entering letter is a vowel, −1 if the leaving one is.",
            why_not={1: "Keeping the substring means rebuilding it every step: O(k) per step.",
                     2: "It works, but it is more than the question needs. Only vowels matter.",
                     3: "It cannot tell you how many vowels are inside."},
        ),
        "pseudocode": code("""
            count ← 0;  best ← 0
            for hi from 0 to n − 1:
                if s[hi] is a vowel:          count ← count + 1   ▸ enters
                if hi ≥ k and s[hi − k] is a vowel: count ← count − 1   ▸ leaves
                if hi ≥ k − 1:               best ← max(best, count)  ▸ full: measure
            return best
        """),
        "hints": [
            {"label": "Nudge", "text": "Every candidate substring has the same length. What changes between one candidate and the next?"},
            {"label": "Approach", "text": "A fixed window of width `k`. Its summary is a single number: how many vowels are inside."},
            {"label": "Steps", "text": "For each `hi`: add 1 if `s[hi]` is a vowel. If `hi ≥ k`, subtract 1 if `s[hi − k]` is a vowel. Once `hi ≥ k − 1`, compare the count with the best."},
            {"label": "Code", "text": "A vowel test that type-checks cleanly: `\"aeiou\".includes(s[hi])`. The leaver is `s[hi - k]`."},
        ],
        "exercise": exercise(
            f"{T}:guided:max-vowels",
            "Implement maxVowels",
            "Implement `maxVowels(s, k)` as described above.",
            fn="maxVowels",
            params=[("s", "string"), ("k", "int")],
            ret="int",
            starter="""
                function maxVowels(s: string, k: number): number {
                  return 0;
                }
            """,
            solution="""
                function maxVowels(s: string, k: number): number {
                  const isVowel = (c: string): boolean => "aeiou".includes(c);
                  let count = 0;
                  let best = 0;
                  for (let hi = 0; hi < s.length; hi++) {
                    if (isVowel(s[hi])) count++;
                    if (hi >= k && isVowel(s[hi - k])) count--;
                    if (hi >= k - 1) best = Math.max(best, count);
                  }
                  return best;
                }
            """,
            cases=[("abciiidef", 3), ("aeiou", 2), ("leetcode", 3), ("rhythms", 4), ("bcdaei", 3), ("a", 1), ("zzzzzzzzza", 10)],
            ref=R.max_vowels,
        ),
        "tests": [
            {"case": "No vowels at all", "input": 's = "rhythms", k = 4', "expected": "0", "why": "`best` must start at 0, and nothing may go negative."},
            {"case": "k equals the length", "input": 's = "zzzzzzzzza", k = 10', "expected": "1", "why": "Exactly one window, and it is only measured on the last index."},
            {"case": "The best window is the last one", "input": 's = "bcdaei", k = 3', "expected": "3", "why": "Catches a loop that stops one step early."},
            {"case": "k = 1", "input": 's = "a", k = 1', "expected": "1", "why": "The smallest window: enters and leaves on consecutive steps."},
        ],
    },
    {
        "key": "product-less",
        "title": "Count subarrays with product less than k",
        "problem": md("""
            Given an array of **positive** integers `nums` (`1 ≤ nums[i] ≤ 1000`,
            `n ≤ 3·10^4`) and an integer `k` (`0 ≤ k ≤ 10^6`), return how many
            contiguous subarrays have a product **strictly less than** `k`.
        """),
        "examples": [
            {"input": "nums = [10, 5, 2, 6], k = 100", "output": str(R.count_product_less([10, 5, 2, 6], 100)), "note": "[10] [5] [2] [6] [10,5] [5,2] [2,6] [5,2,6]"},
            {"input": "nums = [1, 2, 3], k = 0", "output": str(R.count_product_less([1, 2, 3], 0)), "note": "no product is below 0"},
        ],
        "understand": quiz(
            "For nums = [2, 3], k = 7, how many subarrays qualify?",
            ["3", "2", "1", "4"], 0,
            "[2] → 2, [3] → 3, [2, 3] → 6. All three are below 7.",
            why_not={1: "Don't forget the whole array [2, 3]: its product is 6 < 7.",
                     2: "Every single element qualifies on its own.",
                     3: "An array of two elements has exactly three non-empty contiguous subarrays."},
        ),
        "identify": quiz(
            "Which technique fits?",
            [VAR, FIXED, PREFIX, DP], 0,
            "Because every value is ≥ 1, a product only grows as the window grows. “Product < k” survives shrinking, so it is a variable window, in its **count** shape.",
            why_not={1: "The subarrays have every possible length.",
                     2: "Prefix *products* overflow quickly, and the monotone window makes them unnecessary.",
                     3: "No choices to combine. It is a counting sweep."},
        ),
        "approach": quiz(
            "After the repair, [lo, hi] is valid. How many valid subarrays END at hi?",
            ["hi − lo + 1", "1", "hi − lo", "(hi − lo + 1)(hi − lo + 2) / 2"], 0,
            "Any start between lo and hi gives a sub-window of a valid window, which is valid too (products only fall when you remove elements ≥ 1). That is hi − lo + 1 starts.",
            why_not={1: "That counts only [lo, hi] itself. The shorter windows ending at hi are valid too.",
                     2: "Off by one: the window [hi, hi] counts.",
                     3: "That counts every sub-window of [lo, hi], but most of those end before hi and were already counted on earlier steps."},
        ),
        "pseudocode": code("""
            if k ≤ 1: return 0                 ▸ no product of positive integers is < 1
            lo ← 0;  product ← 1;  count ← 0
            for hi from 0 to n − 1:
                product ← product × nums[hi]
                while product ≥ k:
                    product ← product ÷ nums[lo]
                    lo ← lo + 1
                count ← count + (hi − lo + 1)
            return count
        """),
        "hints": [
            {"label": "Nudge", "text": "With every value ≥ 1, what happens to a product when you add an element? When you remove one?"},
            {"label": "Approach", "text": "A variable window whose rule is `product < k`, and you **count** windows instead of measuring one."},
            {"label": "Steps", "text": "Multiply in `nums[hi]`. While `product ≥ k`, divide out `nums[lo]` and move `lo`. Then add `hi − lo + 1`. Handle `k ≤ 1` first."},
            {"label": "Code", "text": "Start with `if (k <= 1) return 0;`. Without it, `k = 1` makes the `while` divide out elements past `hi`, and `nums[lo]` becomes `undefined`."},
        ],
        "exercise": exercise(
            f"{T}:guided:product-less",
            "Implement countProductLess",
            "Implement `countProductLess(nums, k)` as described above.",
            fn="countProductLess",
            params=[("nums", "int[]"), ("k", "int")],
            ret="int",
            starter="""
                function countProductLess(nums: number[], k: number): number {
                  return 0;
                }
            """,
            solution="""
                function countProductLess(nums: number[], k: number): number {
                  if (k <= 1) return 0;
                  let lo = 0;
                  let product = 1;
                  let count = 0;
                  for (let hi = 0; hi < nums.length; hi++) {
                    product *= nums[hi];
                    while (product >= k) {
                      product /= nums[lo];
                      lo++;
                    }
                    count += hi - lo + 1;
                  }
                  return count;
                }
            """,
            cases=[([10, 5, 2, 6], 100), ([1, 2, 3], 0), ([1, 1, 1], 1), ([1, 1, 1], 2), ([2, 3], 7), ([1000, 1000, 1000], 1000000), ([5, 1, 1, 1, 5], 6)],
            ref=R.count_product_less,
        ),
        "tests": [
            {"case": "k = 0", "input": "nums = [1, 2, 3], k = 0", "expected": "0", "why": "The early return: no loop at all."},
            {"case": "k = 1", "input": "nums = [1, 1, 1], k = 1", "expected": "0", "why": "Without the guard, `1 ≥ 1` shrinks past `hi` and divides by `undefined`."},
            {"case": "All ones", "input": "nums = [1, 1, 1], k = 2", "expected": "6", "why": "The window never shrinks: 1 + 2 + 3 windows."},
            {"case": "A single element hits k", "input": "nums = [1000, 1000, 1000], k = 1000000", "expected": "5", "why": "The window shrinks to exclude the oldest element: products must be *strictly* less."},
        ],
    },
]


# ---------------------------------------------------------------------------
# 13. Independent practice — the problem bank, judged in the Solve view
# ---------------------------------------------------------------------------

INDEPENDENT = {
    "intro": md("""
        No teaching from here on. Each problem opens in the normal Solve view
        with its statement, examples, constraints and a TypeScript signature.
        The hints there stay hidden until you ask. So does the one-line nudge
        below each problem.
    """),
    "problems": [
        {"slug": "permutation-in-string", "nudge": "Every rearrangement of the pattern has the pattern's length."},
        {"slug": "longest-repeating-replacement", "nudge": "A window is fixable when its length minus its most frequent letter's count is ≤ k."},
        {"slug": "max-sum-distinct-window", "nudge": "A fixed window that also carries value counts, so you know when every value is distinct."},
        {"slug": "count-nice-subarrays", "nudge": "Exactly k = at most k − at most (k − 1)."},
        {"slug": "longest-ones-after-deleting", "nudge": "A window with at most one zero, and the deletion makes it one shorter."},
    ],
}


# ---------------------------------------------------------------------------
# 14. Variations
# ---------------------------------------------------------------------------

BIG_N, BIG_K, BIG_SEED = 300000, 150000, 7
_big = R.minstd(BIG_N, BIG_SEED)
_big_answer = sum(R.window_maxima_fast(_big, BIG_K)) % 1000000007

MAXIMA_HARNESS = code(r"""
    // ---- checker: reads the arguments, calls your function, prints the result ----
    import * as __ndFs from "fs";
    const __ndIn: string[] = __ndFs.readFileSync(0, "utf8").split("\n");
    const __ndLine = (i: number): string => (__ndIn[i] ?? "").replace(/\r$/, "");
    if (__ndLine(0).startsWith("gen ")) {
      // A large generated case: n = 300 000, k = 150 000. An O(n·k) solution
      // needs over 10^10 steps here; the deque needs about 6·10^5.
      const [, n, k, seed] = __ndLine(0).split(" ").map(Number);
      const nums: number[] = [];
      let x = seed;
      for (let i = 0; i < n; i++) {
        x = (x * 48271) % 2147483647;
        nums.push(x % 1000);
      }
      let sum = 0;
      for (const m of windowMaxima(nums, k)) sum = (sum + m) % 1000000007;
      console.log(String(sum));
    } else {
      const __ndA0 = (__ndLine(0).trim() === "" ? [] : __ndLine(0).trim().split(/\s+/).map(Number));
      const __ndA1 = Number(__ndLine(1).trim());
      console.log(windowMaxima(__ndA0, __ndA1).join(" "));
    }
""")

VARIATIONS = [
    {
        "step": "Basic version",
        "title": "Longest substring without repeating characters",
        "change": md("The template problem from section 7, Example 3: a `Set` summary, the *longest* shape."),
        "insight": md("Everything below is this loop with **one thing changed**. Name the change before you write any code."),
    },
    {
        "step": "Different input",
        "title": "Longest subarray with all distinct values: numbers, not letters",
        "change": md("""
            The input is `number[]` with values up to `10^9` instead of a string.
            A 26-slot count array no longer fits the values. The `Set` still
            works unchanged, because it does not care what the elements are.
        """),
        "insight": md("The summary depends on the **values' range**, not on the technique. Small known range → array; anything else → `Set`/`Map`."),
        "exercise": exercise(
            f"{T}:var:distinct-values",
            "longestDistinctValues",
            """
            Return the length of the longest contiguous subarray of `nums` whose
            values are all different. `0 ≤ nums.length ≤ 10^5`,
            `−10^9 ≤ nums[i] ≤ 10^9`.
            """,
            fn="longestDistinctValues",
            params=[("nums", "int[]")],
            ret="int",
            starter="""
                function longestDistinctValues(nums: number[]): number {
                  return 0;
                }
            """,
            solution="""
                function longestDistinctValues(nums: number[]): number {
                  const inWindow = new Set<number>();
                  let lo = 0;
                  let best = 0;
                  for (let hi = 0; hi < nums.length; hi++) {
                    while (inWindow.has(nums[hi])) {
                      inWindow.delete(nums[lo]);
                      lo++;
                    }
                    inWindow.add(nums[hi]);
                    best = Math.max(best, hi - lo + 1);
                  }
                  return best;
                }
            """,
            cases=[([1, 2, 3, 1, 2, 3, 4],), ([],), ([5, 5, 5],), ([1000000000, -1000000000, 7, 1000000000],), ([4, 2, 4, 5, 6],)],
            ref=R.longest_distinct_values,
        ),
    },
    {
        "step": "Additional constraint",
        "title": "Count subarrays with exactly k distinct values",
        "change": md("""
            *Exactly* instead of *at most*, and **count** instead of longest.
            “Exactly k” does not survive shrinking, so write the count-window for
            *at most* and subtract: `atMost(k) − atMost(k − 1)`.
        """),
        "insight": md("When the rule is not monotone, look for **two monotone rules whose difference is it**."),
        "exercise": exercise(
            f"{T}:var:exactly-k",
            "countExactlyKDistinct",
            """
            Return how many contiguous subarrays of `nums` contain **exactly `k`**
            distinct values. `1 ≤ k ≤ nums.length ≤ 2·10^4`.

            Example: `nums = [1, 2, 1, 2, 3]`, `k = 2` → `7`.
            """,
            fn="countExactlyKDistinct",
            params=[("nums", "int[]"), ("k", "int")],
            ret="int",
            starter="""
                function countExactlyKDistinct(nums: number[], k: number): number {
                  return 0;
                }
            """,
            solution="""
                function countExactlyKDistinct(nums: number[], k: number): number {
                  const atMost = (limit: number): number => {
                    const counts = new Map<number, number>();
                    let lo = 0;
                    let total = 0;
                    for (let hi = 0; hi < nums.length; hi++) {
                      counts.set(nums[hi], (counts.get(nums[hi]) ?? 0) + 1);
                      while (counts.size > limit) {
                        const left = counts.get(nums[lo])! - 1;
                        if (left === 0) counts.delete(nums[lo]);
                        else counts.set(nums[lo], left);
                        lo++;
                      }
                      total += hi - lo + 1;
                    }
                    return total;
                  };
                  return atMost(k) - atMost(k - 1);
                }
            """,
            cases=[([1, 2, 1, 2, 3], 2), ([1, 2, 1, 3, 4], 3), ([1, 1, 1], 1), ([1, 2, 3], 3), ([1, 2, 3], 1), ([2, 1, 2, 1, 2, 1], 2)],
            ref=R.exactly_k_distinct,
            hints=[
                "Counting windows with at most k distinct values is the count pattern from section 4.",
                "Subtract the windows with at most k - 1 distinct values: what is left has exactly k.",
            ],
        ),
    },
    {
        "step": "Optimization requirement",
        "title": "Maximum of every window of size k, in O(n)",
        "change": md("""
            A fixed window whose summary is a **maximum**, and a maximum cannot
            be “subtracted” when it leaves. Rescanning the window is O(n · k),
            and the hidden test has `n = 300 000, k = 150 000`. Keep a
            **deque of indices** whose values decrease from front to back:
            pop smaller values off the back before pushing, and drop the front
            when it falls out of the window. The front is always the maximum.
        """),
        "insight": md("An optimisation requirement often means **a smarter summary**, not a different loop. The loop here is the plain fixed window."),
        "exercise": exercise(
            f"{T}:var:window-maxima",
            "windowMaxima",
            """
            Return an array with the maximum of every window of size `k`, left
            to right. `1 ≤ k ≤ nums.length ≤ 3·10^5`. One hidden test is
            generated at the full size, so O(n · k) will time out.

            Example: `nums = [1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3` →
            `[3, 3, 5, 5, 6, 7]`.
            """,
            fn="windowMaxima",
            params=[("nums", "int[]"), ("k", "int")],
            ret="int[]",
            starter="""
                function windowMaxima(nums: number[], k: number): number[] {
                  const out: number[] = [];
                  return out;
                }
            """,
            solution="""
                function windowMaxima(nums: number[], k: number): number[] {
                  const dq: number[] = [];   // indices; their values decrease
                  let head = 0;
                  const out: number[] = [];
                  for (let hi = 0; hi < nums.length; hi++) {
                    while (dq.length > head && nums[dq[dq.length - 1]] <= nums[hi]) dq.pop();
                    dq.push(hi);
                    if (dq[head] <= hi - k) head++;
                    if (hi >= k - 1) out.push(nums[dq[head]]);
                  }
                  return out;
                }
            """,
            cases=[([1, 3, -1, -3, 5, 3, 6, 7], 3), ([4], 1), ([9, 8, 7, 6], 2), ([1, 2, 3, 4], 4), ([2, 2, 2, 1], 2)],
            ref=R.window_maxima,
            hints=[
                "Store indices in the deque, not values: you need the index to know when the front has left the window.",
                "Before pushing hi, pop every index from the back whose value is <= nums[hi]; it can never be a maximum again.",
                "Use a head index instead of shift() for the front, or the deque itself becomes O(n) per pop.",
            ],
            extra_tests=[{"input": f"gen {BIG_N} {BIG_K} {BIG_SEED}\n", "output": f"{_big_answer}\n"}],
            harness_src=MAXIMA_HARNESS,
        ),
    },
    {
        "step": "Combination with another technique",
        "title": "Minimum window substring: a window plus a “need” counter",
        "change": md("""
            The shortest window of `s` containing every character of `t`, with
            multiplicity. The window is the *shortest* shape. The new idea is the
            validity test: comparing two `Map`s each step would be O(σ), so keep
            **one integer**, how many of `t`'s required counts are currently met,
            and update it only when a count crosses its requirement.
        """),
        "insight": md("Windows combine with **hash-map counting** so that “is it valid?” stays O(1) even when validity involves many characters."),
        "slug": "min-window-length",
    },
]


# ---------------------------------------------------------------------------
# 15. Review
# ---------------------------------------------------------------------------

REVIEW = {
    "must_know": [
        {"label": "Definition", "text": "A contiguous range `[lo, hi]` swept left to right, with a summary of its contents updated as elements enter and leave."},
        {"label": "Core idea", "text": "Neighbouring windows overlap, so update rather than rebuild. When the rule survives shrinking, `lo` never needs to move back."},
        {"label": "Syntax", "text": "`for (let hi …)` + absorb + `while (invalid) release(nums[lo++])` + measure. `Map` counts with `?? 0` and delete at zero."},
        {"label": "Recognition clues", "text": "Contiguous / subarray / substring · longest, shortest, count · at most k · of size k · non-negative values."},
        {"label": "Complexity", "text": "O(n) time, because each pointer moves at most n times. O(1) space, or O(min(n, σ)) for a Map/Set summary."},
    ],
    "must_do": [
        "Implement the fixed, longest, shortest and count shapes from memory.",
        "Explain why a `while` inside the `for` is still O(n).",
        "Recognise when “validity survives shrinking” fails, and name what to use instead.",
        "Apply it to a problem that does not say “window”, such as taking cards from both ends.",
    ],
    "quick_ref": {
        "pattern": "Expand hi → absorb → shrink lo while invalid (longest) / while valid (shortest) → measure",
        "syntax": code("""
            let lo = 0, best = 0;
            for (let hi = 0; hi < n; hi++) {
              absorb(a[hi]);
              while (invalid()) release(a[lo++]);
              best = Math.max(best, hi - lo + 1);
            }
        """),
        "time": "O(n): amortised, 2n pointer moves",
        "space": "O(1) for a sum or counter; O(min(n, σ)) for a Map or Set",
        "think_when": "a contiguous range + a rule that stays true when the range shrinks, or a fixed width",
        "careful": "negative numbers · “exactly” rules · measuring before the repair · `hi − lo + 1` · deleting zero counts",
    },
}


# ---------------------------------------------------------------------------
# 16. Mastery
# ---------------------------------------------------------------------------

MASTERY = {
    "intro": md("""
        Finishing the lessons is not the same as mastering the topic. This
        section tests five separate abilities, and the topic is **mastered** only
        when all five pass. The questions here are new: none of them appeared
        earlier in the topic.
    """),
    "understanding": {
        "pass": 4,
        "questions": [
            quiz("Why is the variable-size window O(n) even though it has a `while` inside a `for`?",
                 ["Each index enters the window once and leaves at most once, so there are at most 2n pointer moves in total",
                  "The `while` loop runs at most once per iteration",
                  "The window is never longer than k",
                  "JavaScript engines optimise nested loops"], 0,
                 "Count moves of `lo` and `hi`, not loop nesting. Neither moves back.",
                 why_not={1: "It can run many times on one step, when one entrant forces several releases.",
                          2: "Variable windows have no k bound, and the argument does not need one.",
                          3: "The bound is about the algorithm, not the engine."}),
            quiz("What property must the window's rule have for the variable-size technique to be correct?",
                 ["A valid window stays valid when you remove elements from its left end",
                  "The rule must involve a sum",
                  "The array must be sorted",
                  "The answer must be unique"], 0,
                 "“Validity survives shrinking” is what lets `lo` move forward without ever needing to come back.",
                 why_not={1: "Distinct counts, zero budgets and “no repeats” are not sums.",
                          2: "Windows work on unsorted data. Sorting would destroy contiguity.",
                          3: "The technique finds the optimal length, whether or not several windows achieve it."}),
            quiz("In “shortest subarray with sum ≥ target”, where must the answer be recorded?",
                 ["Inside the shrinking `while`, before each release",
                  "After the `while`, as in the longest variant",
                  "Only once, after the `for` loop",
                  "Before absorbing `nums[hi]`"], 0,
                 "The loop runs while the window is still valid. After it, the window is invalid, so the valid windows are only visible inside it.",
                 why_not={1: "After the loop the sum is below target, so you would be measuring an invalid window.",
                          2: "The best window can occur at any step. You must compare as you go.",
                          3: "Before absorbing, the window has not changed since the last step."}),
            quiz("Why does “sum ≤ limit” break the technique when values can be negative?",
                 ["Removing a negative number raises the sum, so shrinking can make a valid window invalid and `lo` would need to move back",
                  "Negative numbers cannot be stored in `number[]`",
                  "The sum might overflow",
                  "`Math.max` does not handle negatives"], 0,
                 "The rule no longer survives shrinking, so the skip argument fails.",
                 why_not={1: "`number[]` holds negatives fine.",
                          2: "Overflow is a separate concern, and it applies to positive values too.",
                          3: "`Math.max(-3, -5)` is `-3`, which is correct."}),
            quiz("In the count shape, why do you add `hi − lo + 1` at each step?",
                 ["Every start from lo to hi gives a valid window ending at hi, and there are hi − lo + 1 of them",
                  "It is the length of the longest window so far",
                  "It counts the elements released",
                  "It avoids an off-by-one in the longest variant"], 0,
                 "Sub-windows of a valid window are valid. Grouping them by their right end counts each window exactly once.",
                 why_not={1: "It is the *current* window's length, and here it is used as a count of windows ending at hi.",
                          2: "Releases are not counted anywhere.",
                          3: "It is not a correction. It is the count itself."}),
        ],
    },
    "syntax": exercise(
        f"{T}:mastery:syntax",
        "Syntax: complete the window",
        """
        Return the length of the longest substring of `s` in which **no
        character appears more than twice**. Fill in the three blanks.

        Example: `s = "bcbbbcba"` → `4` (`"bcba"`; `"bcbb"` has three `b`s).
        """,
        fn="longestAtMostTwice",
        params=[("s", "string")],
        ret="int",
        starter="""
            function longestAtMostTwice(s: string): number {
              const counts = new Map<string, number>();
              let lo = 0;
              let best = 0;
              for (let hi = 0; hi < s.length; hi++) {
                const c = s[hi];
                counts.set(c, (counts.get(c) ?? 0) + 1);
                while (____) {
                  const out = s[lo];
                  counts.set(out, ____);
                  lo++;
                }
                best = ____;
              }
              return best;
            }
        """,
        solution="""
            function longestAtMostTwice(s: string): number {
              const counts = new Map<string, number>();
              let lo = 0;
              let best = 0;
              for (let hi = 0; hi < s.length; hi++) {
                const c = s[hi];
                counts.set(c, (counts.get(c) ?? 0) + 1);
                while (counts.get(c)! > 2) {
                  const out = s[lo];
                  counts.set(out, counts.get(out)! - 1);
                  lo++;
                }
                best = Math.max(best, hi - lo + 1);
              }
              return best;
            }
        """,
        cases=[("bcbbbcba",), ("aaaa",), ("",), ("abcabc",), ("aabbaabb",), ("abacabad",)],
        ref=R.longest_at_most_twice,
        kind="drill",
    ),
    "recognition": {
        "pass": 5,
        "questions": [
            quiz("Find the longest run of a playlist that contains songs by at most 2 different artists.",
                 [VAR, FIXED, PREFIX, DP], 0,
                 "Longest + at-most-2-distinct: a variable window with a Map of artist counts.",
                 why_not={1: "The length is what you are looking for.",
                          2: "There is no sum involved.",
                          3: "One sweep decides it, with no subproblems."}),
            quiz("Report the average of every 7-day period of daily sales.",
                 [FIXED, VAR, DEQUE, HASH], 0,
                 "Every 7 consecutive days: a fixed window with a running sum, divided by 7.",
                 why_not={1: "The width is fixed at 7.",
                          2: "A sum can be subtracted when a day leaves. The deque is for maxima and minima.",
                          3: "Averages need the values, not membership."}),
            quiz("Count the subarrays whose sum is divisible by k. Values may be negative.",
                 [PREFIX, VAR, FIXED, TWO_PTR], 0,
                 "Two prefix sums with equal remainders mod k bound a divisible range: count remainders in a hash map.",
                 why_not={1: "Divisibility is not monotone. Adding an element can make the sum divisible or stop it being so.",
                          2: "No width is given.",
                          3: "The answer is ranges, and nothing is sorted."}),
            quiz("Find the minimum number of characters to delete so that a string becomes a palindrome.",
                 [DP, VAR, FIXED, HASH], 0,
                 "The deletions can be anywhere, so the kept characters form a subsequence: longest palindromic subsequence, which is DP.",
                 why_not={1: "The kept characters need not be contiguous.",
                          2: "No width is given.",
                          3: "Counts do not capture order, and palindromes depend on order."}),
            quiz("Find the smallest group of consecutive houses that contains at least 3 red ones.",
                 [VAR, FIXED, BINARY, TWO_PTR], 0,
                 "Shortest + at-least + a count that only grows with the window: the shortest shape, measured inside the shrink.",
                 why_not={1: "The group's size is the unknown.",
                          2: "Nothing is sorted. Searching on the length would add a log factor for nothing.",
                          3: "It is a range, not a pair."}),
            quiz("Count the subarrays that contain at most 5 odd numbers.",
                 [VAR, PREFIX, FIXED, DP], 0,
                 "At most 5 odd survives shrinking: the count shape, adding `hi − lo + 1` per step.",
                 why_not={1: "It would work with extra space. The window is simpler because the rule is monotone.",
                          2: "Subarrays of every length count.",
                          3: "No choices to combine."}),
        ],
    },
    "implementation": exercise(
        f"{T}:mastery:implementation",
        "Implementation: from scratch",
        """
        Return how many substrings of `s` of length **exactly `k`** contain no
        repeated character. `1 ≤ k`, `0 ≤ s.length ≤ 10^4`, lowercase letters.

        - `s = "havefunonleetcode"`, `k = 5` → `6`
        - `s = "home"`, `k = 5` → `0`
        """,
        fn="countKLenNoRepeat",
        params=[("s", "string"), ("k", "int")],
        ret="int",
        starter="""
            function countKLenNoRepeat(s: string, k: number): number {
              return 0;
            }
        """,
        solution="""
            function countKLenNoRepeat(s: string, k: number): number {
              const counts: number[] = new Array<number>(26).fill(0);
              let repeated = 0;   // letters whose count is ≥ 2
              let total = 0;
              for (let hi = 0; hi < s.length; hi++) {
                const inIdx = s.charCodeAt(hi) - 97;
                counts[inIdx]++;
                if (counts[inIdx] === 2) repeated++;
                if (hi >= k) {
                  const outIdx = s.charCodeAt(hi - k) - 97;
                  if (counts[outIdx] === 2) repeated--;
                  counts[outIdx]--;
                }
                if (hi >= k - 1 && repeated === 0) total++;
              }
              return total;
            }
        """,
        cases=[("havefunonleetcode", 5), ("home", 5), ("", 1), ("abcabc", 3), ("aaaa", 1), ("abcdefghijklmnopqrstuvwxyza", 26), ("abab", 2)],
        ref=R.count_k_len_no_repeat,
        difficulty="Medium",
    ),
    "application": {
        "need": 2,
        "intro": md("""
            Three problems that never say “window”. Each one turns into a
            sliding window once you see the right reframing. Solve any **two**.
        """),
        "problems": [
            {"slug": "max-points-from-cards", "reveal": "Taking k cards from the ends leaves a contiguous middle of n − k cards. Minimise that window's sum."},
            {"slug": "min-operations-reduce-x", "reveal": "Removing from both ends is keeping a middle: find the longest window with sum = total − x."},
            {"slug": "min-swaps-group-ones", "reveal": "Fix the target block's length (the number of 1s). The swaps needed are the zeros inside it. Slide it around the circle."},
        ],
    },
}
