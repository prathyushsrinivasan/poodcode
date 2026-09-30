# -*- coding: utf-8 -*-
"""Sliding window, sections 1-8: Concept → Implementation.

The "Understand → See → Copy → Complete → Implement" half of the progression.
"""

from new_dsa_kit import code, exercise, md, multi, quiz
import new_dsa_sw_refs as R

T = "ndsa:sliding-window"


# ---------------------------------------------------------------------------
# 1. Concept
# ---------------------------------------------------------------------------

CONCEPT = {
    "body": md("""
        ### What it is

        A **sliding window** is a contiguous range `[lo, hi]` of an array or a
        string that you move from left to right, while keeping a small **summary**
        of what is inside it up to date: a sum, a count per character, the number
        of zeros.

        ### What problem it solves

        A whole family of questions is about **every contiguous subarray** (or
        substring): the longest one with some property, the shortest one, or how
        many there are. An array of length `n` has `n(n + 1) / 2` of them. That is
        about 5 billion when `n = 100 000`. Inspecting each one from scratch is
        hopeless.

        ### Why it exists

        Neighbouring windows **overlap almost entirely**. `[2, 7]` and `[3, 8]`
        share five of their six elements, and recomputing the shared part is the
        waste. A sliding window pays only for what *changes*: one element enters on
        the right, and sometimes one or more leave on the left.

        ### How it works

        Two indices, `lo` and `hi`, that **only ever move forward**.

        1. **Expand**: move `hi` one step right and *absorb* the new element into
           the summary.
        2. **Repair**: while the window breaks the rule, *release* `a[lo]` from the
           summary and move `lo` right.
        3. **Measure**: `[lo, hi]` is now a valid window. Compare it with the best
           so far.

        Neither index ever moves back, so each moves at most `n` times: at most
        `2n` steps in total, which is O(n).

        ### Internal behaviour: why skipping windows is allowed

        The technique looks at only `n` of the `n^2 / 2` windows, yet it never misses
        the answer. That works because of one property of the rule:
        **validity survives shrinking**. If a window is valid, every smaller window
        inside it is valid too. *"At most k distinct characters"*, *"no repeated
        character"* and *"sum ≤ S when every number is non-negative"* all have
        it.

        So when absorbing `a[hi]` breaks the window, no window that starts at or
        before the current `lo` and ends at `hi` can be valid. `lo` may only move
        right, and it never needs to come back. When a rule does **not** have this
        property, the technique does not apply (see section 6).
    """),
    "terms": [
        {"term": "Window", "meaning": "The contiguous range `[lo, hi]` currently under consideration, both ends inclusive. Its length is `hi − lo + 1`."},
        {"term": "`lo` / `hi`", "meaning": "The left and right edges. Also called `left`/`right` or `start`/`end`. Both only increase."},
        {"term": "Summary (window state)", "meaning": "What you keep about the window so you never re-read it: a running sum, a `Map` of counts, a count of zeros."},
        {"term": "Absorb / release", "meaning": "Update the summary when an element enters (on the right) or leaves (on the left)."},
        {"term": "Valid", "meaning": "The window satisfies the problem's rule: at most k distinct, sum ≤ limit, no repeats…"},
        {"term": "Fixed-size window", "meaning": "Every window has length exactly k. Each step, one element enters and one leaves."},
        {"term": "Variable-size window", "meaning": "The window grows on the right every step and shrinks on the left only when the rule demands it."},
        {"term": "Monotone rule", "meaning": "A rule where validity survives shrinking. The whole technique rests on it."},
        {"term": "Amortised O(1)", "meaning": "One step may release many elements, but across the whole run every element is released at most once."},
    ],
    "analogy": md("""
        **A caterpillar crawling along a branch.** Its head (`hi`) reaches forward
        one leaf at a time and eats it. When its body gets too long or too heavy
        for the rule, the tail (`lo`) pulls in until it is comfortable again. It
        never crawls backwards, so it crosses the branch in one pass, however
        many leaves it tries along the way.
    """),
}


# ---------------------------------------------------------------------------
# 2. Mental model
# ---------------------------------------------------------------------------

STEP_INPUT = "abcabcbb"

MENTAL_MODEL = {
    "body": md("""
        Picture **two fingers on the array** and a notebook beside it.

        ```
        index:   0   1   2   3   4   5   6   7
        value:   a   b   c   a   b   c   b   b
                         ▲       ▲
                         lo      hi          window = s[2..4] = "cab"

        notebook (summary):  { c, a, b }     best so far: 3
        ```

        - **What is stored:** the two indices, the summary of what lies between
          them, and the best answer seen so far. The window's *contents* are never
          copied, because they are already in the array.
        - **How the elements relate:** everything between the fingers is "in",
          everything outside is "out". The summary must always describe exactly
          the "in" part.
        - **What changes on each operation:**

        ```
        ┌─► hi += 1
        │      │
        │      ▼
        │   absorb a[hi]
        │      │
        │      ▼
        │   window invalid? ──yes──► release a[lo]; lo += 1 ─┐
        │      │        ▲                                    │
        │      no       └────────────────────────────────────┘
        │      ▼
        └── measure [lo, hi]
        ```

        **The picture to hold while solving:** the right finger always moves. The
        left finger moves only when the notebook says the window is broken, and
        it moves just far enough to fix it.
    """),
    "stepper": {
        "title": "Step through it: longest substring with no repeated character",
        "input_label": f's = "{STEP_INPUT}"',
        "cells": list(STEP_INPUT),
        "state_label": "Characters in the window",
        "frames": R.unique_frames(STEP_INPUT),
    },
}


# ---------------------------------------------------------------------------
# 3. TypeScript fundamentals
# ---------------------------------------------------------------------------

TS_FUNDAMENTALS = {
    "intro": md("""
        Only the TypeScript this topic needs. Every item below appears in the
        code later in this topic.
    """),
    "items": [
        {
            "name": "Arrays of numbers: `number[]`",
            "code": code("""
                const nums: number[] = [2, 1, 5, 1, 3];
                nums.length;      // 5
                nums[0];          // 2 — indexing is O(1)
                nums[nums.length - 1]; // 3 — the last element
            """),
            "explain": md("""
                `number[]` is an array of numbers; `nums.length` is its size.
                Reading `nums[i]` for an `i` outside `0 … length − 1` does not
                throw. It quietly gives `undefined`, and `undefined + 1` is `NaN`.
                A window index that runs one past the end shows up as `NaN`, not
                as an error. Under the stricter `noUncheckedIndexedAccess` option,
                TypeScript types `nums[i]` as `number | undefined` to warn you about
                exactly that. This topic uses plain `strict`, where it is `number`.
            """),
        },
        {
            "name": "Strings: characters are strings too",
            "code": code("""
                const s = "abca";
                s.length;               // 4
                s[1];                   // "b" — a string of length 1, not a char type
                s[1] === "b";           // true
                s.charCodeAt(1) - 97;   // 1 — 'a' is 97, so letters map to 0..25
            """),
            "explain": md("""
                TypeScript has no `char` type: `s[i]` is a one-character `string`,
                and you compare it with `===`. For a lowercase letter,
                `s.charCodeAt(i) - 97` turns it into an index `0 … 25`, which is
                how a fixed-size count array is indexed.
            """),
        },
        {
            "name": "`Map<string, number>`: counting what is in the window",
            "code": code("""
                const counts = new Map<string, number>();

                // absorb c
                counts.set(c, (counts.get(c) ?? 0) + 1);

                // release c
                const left = counts.get(c)! - 1;
                if (left === 0) counts.delete(c);
                else counts.set(c, left);

                counts.size;   // how many DISTINCT keys are in the window
            """),
            "explain": md("""
                `counts.get(c)` returns `number | undefined`: `undefined` when `c`
                was never added. `?? 0` means "use 0 if it is missing". The `!` in
                the release says "I know it is there". That is true, because you only
                release what you absorbed.

                **Delete keys that reach zero.** `counts.size` counts keys, not
                positive counts. A key left at `0` still counts as a distinct
                character in the window.
            """),
        },
        {
            "name": "`Set<string>`: is it inside?",
            "code": code("""
                const inWindow = new Set<string>();
                inWindow.add("a");
                inWindow.has("a");     // true
                inWindow.delete("a");
                inWindow.size;         // 0
            """),
            "explain": md("""
                When the only question is *"is this element in the window?"*, a
                `Set` is simpler than a `Map`. `add`, `has` and `delete` are all
                O(1) on average.
            """),
        },
        {
            "name": "A fixed-size count array",
            "code": code("""
                const counts: number[] = new Array<number>(26).fill(0);
                counts[s.charCodeAt(i) - 97]++;
            """),
            "explain": md("""
                When the alphabet is small and known (26 lowercase letters), an
                array of 26 counters is faster than a `Map` and needs no `?? 0`.
                `new Array<number>(26)` alone is 26 *holes*, and `holes + 1` is
                `NaN`. The `.fill(0)` is not optional.
            """),
        },
        {
            "name": "`let` vs `const`",
            "code": code("""
                let lo = 0;                           // reassigned: let
                let best = 0;                         // reassigned: let
                const counts = new Map<string, number>(); // never reassigned: const
                counts.set("a", 1);                   // …but still mutable inside
            """),
            "explain": md("""
                `const` means the *variable* is never pointed at something else,
                not that the object is frozen. The indices and the best answer
                change, so they are `let`. The `Map` or `Set` is the same object for
                the whole run, so it is `const`.
            """),
        },
        {
            "name": "Functions with typed parameters",
            "code": code("""
                function longestKDistinct(s: string, k: number): number {
                  // ...
                  return 0;
                }
            """),
            "explain": md("""
                Every exercise in this topic asks for exactly one function like
                this. The checker calls it and prints what it returns, so you never
                write input or output code. The `: number` after the parentheses is
                the return type: returning a string by mistake is a compile error,
                not a wrong answer.
            """),
        },
        {
            "name": "`Math.max`, `Math.min` and `Infinity`",
            "code": code("""
                best = Math.max(best, hi - lo + 1);   // longest
                let shortest = Infinity;              // "nothing found yet"
                shortest = Math.min(shortest, hi - lo + 1);
                return shortest === Infinity ? 0 : shortest;
            """),
            "explain": md("""
                A *maximum* starts at `0` (or the first window). A *minimum* must
                start **above** any real answer, and `Infinity` is a real
                `number` in TypeScript, so it type-checks. Convert it back before
                returning.
            """),
        },
        {
            "name": "A queue you can pop from the front in O(1)",
            "code": code("""
                const dq: number[] = [];
                let head = 0;              // dq[head] is the front
                dq.push(7);                // push back:  O(1)
                const front = dq[head++];  // pop front: O(1)
                dq.pop();                  // pop back:  O(1)
                // dq.shift() also pops the front — but it is O(n)
            """),
            "explain": md("""
                TypeScript has no built-in deque. `shift()` re-indexes the whole
                array on every call, which turns an O(n) window into O(n²). Keep a
                `head` index instead. You only need this for the
                "maximum of every window" variation in section 14.
            """),
        },
    ],
    "drills": [
        exercise(
            f"{T}:ts:map-count",
            "Count with a Map",
            """
            Return how many times the **most frequent** character appears in `s`
            (0 for an empty string). Fill in the one blank: add `c` to the
            `Map`, starting from 0 when it is not there yet.
            """,
            fn="maxCharCount",
            params=[("s", "string")],
            ret="int",
            starter="""
                function maxCharCount(s: string): number {
                  const counts = new Map<string, number>();
                  let best = 0;
                  for (let i = 0; i < s.length; i++) {
                    const c = s[i];
                    counts.set(c, ____);
                    best = Math.max(best, counts.get(c)!);
                  }
                  return best;
                }
            """,
            solution="""
                function maxCharCount(s: string): number {
                  const counts = new Map<string, number>();
                  let best = 0;
                  for (let i = 0; i < s.length; i++) {
                    const c = s[i];
                    counts.set(c, (counts.get(c) ?? 0) + 1);
                    best = Math.max(best, counts.get(c)!);
                  }
                  return best;
                }
            """,
            cases=[("banana",), ("",), ("abc",), ("zzzz",), ("mississippi",)],
            ref=R.max_char_count,
            hints=[
                "counts.get(c) is undefined the first time you see c.",
                "?? 0 turns that undefined into 0; then add 1.",
            ],
            kind="drill",
        ),
        exercise(
            f"{T}:ts:count-array",
            "Count with a fixed array",
            """
            `s` holds only lowercase letters. Return how many **different**
            letters it contains, using a 26-slot count array rather than a `Set`.
            Fill in the two blanks.
            """,
            fn="distinctLetters",
            params=[("s", "string")],
            ret="int",
            starter="""
                function distinctLetters(s: string): number {
                  const counts: number[] = new Array<number>(26).fill(0);
                  let distinct = 0;
                  for (let i = 0; i < s.length; i++) {
                    const idx = ____;
                    if (counts[idx] === 0) distinct++;
                    ____;
                  }
                  return distinct;
                }
            """,
            solution="""
                function distinctLetters(s: string): number {
                  const counts: number[] = new Array<number>(26).fill(0);
                  let distinct = 0;
                  for (let i = 0; i < s.length; i++) {
                    const idx = s.charCodeAt(i) - 97;
                    if (counts[idx] === 0) distinct++;
                    counts[idx]++;
                  }
                  return distinct;
                }
            """,
            cases=[("banana",), ("",), ("abcdefghijklmnopqrstuvwxyz",), ("zzz",), ("window",)],
            ref=R.distinct_letters,
            hints=[
                "'a' has char code 97, so subtracting 97 maps a..z to 0..25.",
                "After checking whether this letter is new, increase its counter.",
            ],
            kind="drill",
        ),
    ],
}


# ---------------------------------------------------------------------------
# 4. Syntax & patterns
# ---------------------------------------------------------------------------

PATTERNS = {
    "intro": md("""
        Every sliding window is one of these few shapes, and each differs from
        the others in one or two lines. Learn to recognise them on sight. The
        general loop comes first:

        ```ts
        for (let hi = 0; hi < nums.length; hi++) {
          // absorb nums[hi]
          // while (window is invalid) release nums[lo++]
          // measure
        }
        ```
    """),
    "items": [
        {
            "name": "Fixed size k",
            "when": "“every window of size k”, “k consecutive”, “substring of length k”",
            "code": code("""
                let sum = 0;
                let best = -Infinity;
                for (let hi = 0; hi < nums.length; hi++) {
                  sum += nums[hi];                   // enters
                  if (hi >= k) sum -= nums[hi - k];  // leaves
                  if (hi >= k - 1) best = Math.max(best, sum); // full: measure
                }
            """),
            "note": "No `lo` at all: the leaving index is always `hi − k`. Measure only once the window is full.",
        },
        {
            "name": "Variable size: longest valid",
            "when": "“longest”, “maximum length”, with an at-most rule",
            "code": code("""
                let lo = 0;
                let best = 0;
                for (let hi = 0; hi < nums.length; hi++) {
                  absorb(nums[hi]);
                  while (invalid()) release(nums[lo++]);
                  best = Math.max(best, hi - lo + 1);  // AFTER the repair
                }
            """),
            "note": "Shrink **while invalid**, then measure. Every measured window is valid.",
        },
        {
            "name": "Variable size: shortest valid",
            "when": "“shortest”, “minimum length”, with an at-least rule",
            "code": code("""
                let lo = 0;
                let best = Infinity;
                for (let hi = 0; hi < nums.length; hi++) {
                  absorb(nums[hi]);
                  while (valid()) {
                    best = Math.min(best, hi - lo + 1); // INSIDE the loop
                    release(nums[lo++]);
                  }
                }
                return best === Infinity ? 0 : best;
            """),
            "note": "The mirror image: shrink **while still valid**, and measure before each release.",
        },
        {
            "name": "Count the valid windows",
            "when": "“how many subarrays …” with an at-most rule",
            "code": code("""
                let count = 0;
                for (let hi = 0; hi < nums.length; hi++) {
                  absorb(nums[hi]);
                  while (invalid()) release(nums[lo++]);
                  count += hi - lo + 1;   // every start in [lo, hi] works
                }
            """),
            "note": "`[lo, hi]` valid ⇒ `[lo+1, hi]`, …, `[hi, hi]` are valid too: `hi − lo + 1` windows end at `hi`.",
        },
        {
            "name": "Exactly k = at most k − at most (k − 1)",
            "when": "“exactly k distinct / odd / …”",
            "code": code("""
                function atMost(k: number): number { /* count pattern above */ }
                return atMost(k) - atMost(k - 1);
            """),
            "note": "“Exactly” does not survive shrinking, but “at most” does. Subtract two counts that each do.",
        },
        {
            "name": "Choosing the summary",
            "when": "What does `invalid()` need to know?",
            "code": code("""
                let sum = 0;                                // sums with non-negative values
                const counts = new Map<string, number>();   // distinct / frequencies
                const counts26 = new Array<number>(26).fill(0); // lowercase letters
                let zeros = 0;                              // a budget: “at most k zeros”
                const inWindow = new Set<string>();         // “no repeats”
            """),
            "note": "Pick the smallest summary that answers “is the window valid?” in O(1).",
        },
    ],
}


# ---------------------------------------------------------------------------
# 5. When to use it
# ---------------------------------------------------------------------------

WHEN_TO_USE = {
    "intro": md("""
        No single word guarantees a sliding window. What the words below have in
        common is that each one tells you **the answer is a contiguous range**
        and **the rule can be checked incrementally**. Read each *why* column.
        That reasoning carries over to problems whose wording you have never
        seen.
    """),
    "clues": [
        {"clue": "“contiguous”, “subarray”, “substring”, “consecutive”",
         "why": "The answer is a range `[lo, hi]`, and a window can only describe ranges. Watch out for **subsequence**, which may skip elements and is a different problem."},
        {"clue": "“of size k”, “every k consecutive”, “length exactly k”",
         "why": "The width is given, so no rule decides when to shrink: the **fixed** window. Each step, one element enters and one leaves."},
        {"clue": "“longest”, “maximum length”",
         "why": "Grow as far as the rule allows, and measure **after** repairing. The variable window's *longest* shape."},
        {"clue": "“shortest”, “minimum length”, “smallest”",
         "why": "Once valid, shrink as far as it stays valid, and measure **inside** the shrink. The *shortest* shape."},
        {"clue": "“at most k” (distinct, zeros, changes, cost)",
         "why": "An at-most budget is exactly a rule that survives shrinking: removing an element never uses *more* of the budget."},
        {"clue": "“all values are positive / non-negative” in the constraints",
         "why": "With no negative numbers, a sum only grows as the window grows. That makes “sum ≤ S” and “sum ≥ S” monotone. Setters add this line precisely so that a window works."},
        {"clue": "“count the subarrays where …” with an at-most rule",
         "why": "Every valid window ending at `hi` starts in `[lo, hi]`: add `hi − lo + 1` per step instead of listing them."},
        {"clue": "`n` up to 10⁵ or 10⁶ and the question is about all subarrays",
         "why": "O(n²) is 10¹⁰ steps, far too slow. An O(n) scan over ranges usually means a window (or prefix sums)."},
    ],
    "test": md("""
        **The real test is not the wording.** Ask: *"If I shrink a valid window,
        is it still valid?"* If yes, a variable window works. If the width is
        fixed, a fixed window works. If neither holds, see the next section.
    """),
}


# ---------------------------------------------------------------------------
# 6. When NOT to use it
# ---------------------------------------------------------------------------

WHEN_NOT = {
    "intro": md("""
        Each of these looks like a sliding window problem. In each, one detail
        breaks the rule "validity survives shrinking", or the question is not
        really about a sweeping range at all.
    """),
    "cases": [
        {"looks_like": "“Count the subarrays whose sum equals k.”",
         "but": "The values **can be negative**.",
         "use_instead": "Prefix sums + a hash map of prefix sums seen so far",
         "why": "Removing a negative number *raises* the sum, so shrinking can turn a too-small window into a valid one, or the reverse. `lo` would need to move back. Prefix sums reduce every range to `prefix[hi+1] − prefix[lo]`, whatever the signs."},
        {"looks_like": "“Find the longest … substring …”",
         "but": "It actually says **subsequence**: elements may be skipped.",
         "use_instead": "Dynamic programming (LIS / LCS family) or greedy",
         "why": "A window is contiguous by definition. A subsequence has no `[lo, hi]` to slide."},
        {"looks_like": "“Maximum sum of a subarray.”",
         "but": "There is **no size and no budget**, and the values can be negative.",
         "use_instead": "Kadane's algorithm (1-D DP)",
         "why": "Without a rule, nothing tells `lo` when to move. Kadane restarts the range whenever the running sum goes negative. That is a different decision, based on the sum's sign rather than a budget."},
        {"looks_like": "“Count subarrays with exactly k distinct values.”",
         "but": "**Exactly** k does not survive shrinking: removing an element can take k down to k − 1.",
         "use_instead": "Still windows, but twice: `atMost(k) − atMost(k − 1)`",
         "why": "Change the rule until it *is* monotone, then subtract. A window on the “exactly” rule directly undercounts."},
        {"looks_like": "“Answer many queries: the sum of range [l, r].”",
         "but": "The ranges are **given and arbitrary**. Nothing is swept left to right.",
         "use_instead": "Prefix sums (O(1) per query after O(n) setup)",
         "why": "A window is a single left-to-right pass. Arbitrary ranges that jump around need random access to any range's total."},
        {"looks_like": "“Find two numbers in the array that add up to the target.”",
         "but": "The answer is a **pair of elements**, not a range.",
         "use_instead": "A hash map of seen values, or two pointers from both ends if sorted",
         "why": "Two pointers is not always a window. Moving inward from both ends searches pairs, not ranges."},
        {"looks_like": "“Shortest subarray with sum at least k.”",
         "but": "The values **can be negative**.",
         "use_instead": "Prefix sums + a monotonic deque",
         "why": "The plain shortest-window shape assumes shrinking only lowers the sum. With negatives it can raise it, so the valid starts are not a contiguous block."},
    ],
}


# ---------------------------------------------------------------------------
# 7. Step-by-step examples
# ---------------------------------------------------------------------------

EX1_CODE = code("""
    function maxSumWindow(nums: number[], k: number): number {
      let windowSum = 0;
      for (let i = 0; i < k; i++) {
        windowSum += nums[i];
      }
      let best = windowSum;
      for (let hi = k; hi < nums.length; hi++) {
        windowSum += nums[hi];
        windowSum -= nums[hi - k];
        best = Math.max(best, windowSum);
      }
      return best;
    }
""")

EX2_CODE = code("""
    function countGoodWindows(nums: number[], k: number, threshold: number): number {
      const target = k * threshold;
      let windowSum = 0;
      let count = 0;
      for (let hi = 0; hi < nums.length; hi++) {
        windowSum += nums[hi];
        if (hi >= k) windowSum -= nums[hi - k];
        if (hi >= k - 1 && windowSum >= target) count++;
      }
      return count;
    }
""")

EX3_CODE = code("""
    function longestUnique(s: string): number {
      const inWindow = new Set<string>();
      let lo = 0;
      let best = 0;
      for (let hi = 0; hi < s.length; hi++) {
        const c = s[hi];
        while (inWindow.has(c)) {
          inWindow.delete(s[lo]);
          lo++;
        }
        inWindow.add(c);
        best = Math.max(best, hi - lo + 1);
      }
      return best;
    }
""")

EX1_NUMS, EX1_K = [2, 1, 5, 1, 3, 2], 3
EX3_S = "abcabcbb"

EXAMPLES = [
    {
        "level": "Basic",
        "title": "Largest sum of any k consecutive numbers",
        "problem": md(f"""
            Given `nums` and `k` (1 ≤ k ≤ nums.length), return the largest sum of
            any `k` consecutive elements. For `nums = {EX1_NUMS}`, `k = {EX1_K}`
            the answer is **{R.max_sum_window(EX1_NUMS, EX1_K)}** (`5 + 1 + 3`).
        """),
        "code": EX1_CODE,
        "lines": [
            {"code": "let windowSum = 0;", "explain": "The summary. This window only needs to remember its total."},
            {"code": "for (let i = 0; i < k; i++) windowSum += nums[i];", "explain": "Build the **first** window, `[0, k − 1]`, the slow way. This happens once only."},
            {"code": "let best = windowSum;", "explain": "The first window is a real candidate, so it is the best so far. Starting at `0` would be wrong when every number is negative."},
            {"code": "for (let hi = k; hi < nums.length; hi++)", "explain": "`hi` is the index that **enters**. It starts at `k`, just past the first window."},
            {"code": "windowSum += nums[hi];", "explain": "Absorb the entering element."},
            {"code": "windowSum -= nums[hi - k];", "explain": "Release the element that falls off the left. The window `[hi − k + 1, hi]` still has exactly `k` elements, so the leaver is `hi − k`."},
            {"code": "best = Math.max(best, windowSum);", "explain": "Measure. Each step cost two additions, however large `k` is."},
            {"code": "return best;", "explain": "Every window of size k was measured exactly once."},
        ],
        "trace": {
            "headers": ["hi", "enters", "leaves", "window", "windowSum", "best"],
            "rows": R.max_sum_rows(EX1_NUMS, EX1_K),
        },
        "takeaway": md("""
            **Two reads per step instead of k.** Recomputing each window would be
            O(n·k). Sliding it is O(n).
        """),
    },
    {
        "level": "Slight variation",
        "title": "How many windows of size k have average ≥ threshold?",
        "problem": md(f"""
            Same input shape, but now count the windows of size `k` whose
            **average** is at least `threshold`. For `nums = [2, 2, 2, 2, 5, 5, 5, 8]`,
            `k = 3`, `threshold = 4` the answer is
            **{R.count_good_windows([2, 2, 2, 2, 5, 5, 5, 8], 3, 4)}**.
        """),
        "code": EX2_CODE,
        "question": multi(
            "Compare this with Example 1. Which of these changed? Select every one that did.",
            [
                "The measure step: it counts windows that pass a test instead of keeping a maximum",
                "The first window is built inside the main loop, guarded by `hi >= k - 1`",
                "The average is compared as `sum >= k * threshold`, with no division",
                "What enters and what leaves the window each step",
                "The time complexity",
            ],
            [0, 1, 2],
            """
                Three things changed and two did not. The **enter/leave** mechanics
                (`+= nums[hi]`, `-= nums[hi - k]`) are identical: that is the
                technique. What changed is the *measure* (count instead of max), how
                the first window is built (one loop with a guard instead of a
                separate loop; both are common), and a small trick. Comparing
                `sum ≥ k · threshold` avoids dividing, so no floating point is
                involved. The cost is still O(n).
            """,
            why_not={
                3: "It is the same pair of lines: `+= nums[hi]` and `-= nums[hi - k]`. That did not change.",
                4: "Still one pass with O(1) work per step: O(n).",
            },
        ),
        "notes": [
            "The `hi >= k` guard stops a leaver being released before the window is full.",
            "The `hi >= k - 1` guard stops a *partial* window from being measured. Without it, the first k − 1 steps count short windows.",
        ],
    },
    {
        "level": "Real problem",
        "title": "Longest substring without repeating characters",
        "problem": md(f"""
            Return the length of the longest substring of `s` with no repeated
            character. For `s = "{EX3_S}"` the answer is **{R.longest_unique(EX3_S)}**
            (`"abc"`). The width is not given, so this is a **variable** window.
            The rule, "no repeats", survives shrinking.
        """),
        "code": EX3_CODE,
        "trace": {
            "headers": ["hi", "c", "released", "window", "length", "best"],
            "rows": R.unique_rows(EX3_S),
        },
        "notes": [
            "Here the repair runs **before** the absorb: the rule is about the *incoming* character, so the window is cleared of `c` first. That is equivalent to absorbing, then shrinking while `c` appears twice.",
            "`lo` jumps several places at once at `hi = 6`: the `while` released two characters. It is still at most `n` releases over the whole run.",
        ],
    },
]


# ---------------------------------------------------------------------------
# 8. Implementation: read → complete → pseudocode → scratch
# ---------------------------------------------------------------------------

READ_CODE = code("""
    function longestSumAtMost(nums: number[], limit: number): number {
      let lo = 0;
      let windowSum = 0;
      let best = 0;
      for (let hi = 0; hi < nums.length; hi++) {
        windowSum += nums[hi];
        while (windowSum > limit) {
          windowSum -= nums[lo];
          lo++;
        }
        best = Math.max(best, hi - lo + 1);
      }
      return best;
    }
""")

IMPLEMENTATION = {
    "read": {
        "title": "Longest subarray with sum ≤ limit (all values ≥ 0)",
        "problem": md("""
            Given non-negative `nums` and a `limit`, return the length of the
            longest contiguous subarray whose sum is at most `limit` (0 if none).
        """),
        "code": READ_CODE,
        "notes": [
            {"line": 2, "text": "`lo` is the left edge. The window starts empty."},
            {"line": 3, "text": "The summary: the sum of `nums[lo..hi]`."},
            {"line": 6, "text": "**Absorb.** The window is now `[lo, hi]`, possibly invalid."},
            {"line": 7, "text": "**Repair**, with `while` rather than `if`. One large entrant can require several releases."},
            {"line": 8, "text": "**Release** `nums[lo]`, then move the edge. The order matters: subtract first, then `lo++`."},
            {"line": 11, "text": "**Measure.** After the loop the window is valid, possibly empty (`lo = hi + 1`, length 0) if `nums[hi] > limit` alone."},
            {"line": 13, "text": "Every index entered once and left at most once: 2n steps."},
        ],
        "why_it_works": md("""
            Because every value is ≥ 0, shrinking can only lower the sum. Once
            `[lo, hi]` is too heavy, every window starting at or before `lo` and
            ending at `hi` is too heavy as well. Moving `lo` past them loses
            nothing.
        """),
    },
    "complete": exercise(
        f"{T}:impl:complete",
        "Complete it: longest substring with at most k distinct characters",
        """
        Return the length of the longest substring of `s` that contains **at
        most `k` distinct characters** (`0 ≤ k`). The window, the loop and the
        release are written. Fill in the four blanks.

        Example: `s = "eceba"`, `k = 2` → `3` (`"ece"`).
        """,
        fn="longestKDistinct",
        params=[("s", "string"), ("k", "int")],
        ret="int",
        starter="""
            function longestKDistinct(s: string, k: number): number {
              const counts = new Map<string, number>();
              let lo = 0;
              let best = 0;
              for (let hi = 0; hi < s.length; hi++) {
                const c = s[hi];
                counts.set(c, ____);
                while (____) {
                  const out = s[lo];
                  const left = counts.get(out)! - 1;
                  if (left === 0) ____;
                  else counts.set(out, left);
                  lo++;
                }
                best = ____;
              }
              return best;
            }
        """,
        solution="""
            function longestKDistinct(s: string, k: number): number {
              const counts = new Map<string, number>();
              let lo = 0;
              let best = 0;
              for (let hi = 0; hi < s.length; hi++) {
                const c = s[hi];
                counts.set(c, (counts.get(c) ?? 0) + 1);
                while (counts.size > k) {
                  const out = s[lo];
                  const left = counts.get(out)! - 1;
                  if (left === 0) counts.delete(out);
                  else counts.set(out, left);
                  lo++;
                }
                best = Math.max(best, hi - lo + 1);
              }
              return best;
            }
        """,
        cases=[("eceba", 2), ("aa", 1), ("", 3), ("abc", 0), ("abaccc", 2), ("abcadcacacaca", 3), ("aabbcc", 1)],
        ref=R.longest_k_distinct,
        hints=[
            "Absorb: the same Map update as the TypeScript fundamentals drill.",
            "The window is invalid when it holds more than k distinct characters; counts.size tells you how many it holds.",
            "A count that reaches zero must leave the Map entirely, or size keeps counting it.",
            "Measure the longest variant after the repair: the window length is hi - lo + 1.",
        ],
        kind="drill",
        explanation="""
            The four blanks are the four decisions in every variable window:
            **absorb** (`?? 0` + 1), **invalid?** (`counts.size > k`),
            **clean release** (`delete` at zero, so `size` stays honest) and
            **measure** after the repair.
        """,
    ),
    "pseudocode": {
        "title": "Pseudocode → TypeScript: shortest subarray with sum ≥ target",
        "problem": md("""
            Given **positive** integers `nums` and a `target`, return the length of
            the shortest contiguous subarray whose sum is **at least** `target`,
            or `0` if there is none.
        """),
        "pseudocode": code("""
            lo ← 0;  sum ← 0;  best ← ∞
            for hi from 0 to n − 1:
                sum ← sum + nums[hi]
                while sum ≥ target:               ▸ valid: try to make it shorter
                    best ← min(best, hi − lo + 1) ▸ measure INSIDE the loop
                    sum ← sum − nums[lo]
                    lo ← lo + 1
            return 0 if best is still ∞, else best
        """),
        "exercise": exercise(
            f"{T}:impl:pseudocode",
            "Translate the pseudocode",
            """
            Turn the pseudocode above into TypeScript, line by line. Examples:
            `nums = [2, 3, 1, 2, 4, 3]`, `target = 7` → `2` (`[4, 3]`);
            `nums = [1, 1, 1]`, `target = 5` → `0`.
            """,
            fn="minLenSumAtLeast",
            params=[("nums", "int[]"), ("target", "int")],
            ret="int",
            starter="""
                function minLenSumAtLeast(nums: number[], target: number): number {
                  // lo ← 0; sum ← 0; best ← ∞
                  // for hi …
                  return 0;
                }
            """,
            solution="""
                function minLenSumAtLeast(nums: number[], target: number): number {
                  let lo = 0;
                  let sum = 0;
                  let best = Infinity;
                  for (let hi = 0; hi < nums.length; hi++) {
                    sum += nums[hi];
                    while (sum >= target) {
                      best = Math.min(best, hi - lo + 1);
                      sum -= nums[lo];
                      lo++;
                    }
                  }
                  return best === Infinity ? 0 : best;
                }
            """,
            cases=[([2, 3, 1, 2, 4, 3], 7), ([1, 1, 1], 5), ([1, 4, 4], 4), ([5], 5), ([1, 2, 3, 4, 5], 11), ([1, 1, 1, 1, 1, 1, 1, 1], 11), ([10, 2, 3], 6)],
            ref=R.min_len_sum_at_least,
            hints=[
                "∞ is Infinity in TypeScript, and it is a number, so best can start there.",
                "The pseudocode's while becomes a while; the measurement goes before the release, inside it.",
                "Convert Infinity back to 0 on the way out.",
            ],
        ),
    },
    "scratch": exercise(
        f"{T}:impl:scratch",
        "From scratch: longest run of 1s with at most k flips",
        """
        `bits` holds only `0`s and `1`s. You may flip **at most `k`** zeros into
        ones. Return the length of the longest run of consecutive 1s you can
        get.

        - `bits = [1,1,1,0,0,0,1,1,1,1,0]`, `k = 2` → `6`
        - `bits = [0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1]`, `k = 3` → `10`

        Constraints: `0 ≤ k ≤ bits.length ≤ 10^5`. O(n) expected.
        """,
        fn="longestOnesKFlips",
        params=[("bits", "int[]"), ("k", "int")],
        ret="int",
        starter="""
            function longestOnesKFlips(bits: number[], k: number): number {
              return 0;
            }
        """,
        solution="""
            function longestOnesKFlips(bits: number[], k: number): number {
              let lo = 0;
              let zeros = 0;
              let best = 0;
              for (let hi = 0; hi < bits.length; hi++) {
                if (bits[hi] === 0) zeros++;
                while (zeros > k) {
                  if (bits[lo] === 0) zeros--;
                  lo++;
                }
                best = Math.max(best, hi - lo + 1);
              }
              return best;
            }
        """,
        cases=[
            ([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2),
            ([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3),
            ([0, 0, 0], 0),
            ([1, 1, 1], 0),
            ([0, 0, 0], 5),
            ([], 0),
            ([1, 0, 1, 0, 1], 1),
        ],
        ref=R.longest_ones_k_flips,
        hints=[
            "You never decide which zeros to flip. Any window with at most k zeros can be made all ones.",
            "So the rule is: zeros in the window ≤ k. Keep a zeros counter as the summary.",
        ],
        difficulty="Medium",
        explanation="""
            The reframing is the skill: *"which zeros should I flip?"* sounds
            like a search, but any window with ≤ k zeros **can** be made all
            ones. So the choice disappears, and the budget becomes the window's
            rule.
        """,
    ),
}
