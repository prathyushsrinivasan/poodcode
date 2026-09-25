# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 32 — mock interview week. The last week of the course.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _typed, _predict, _diagnose,
# _retype, _design, _q, _gloss, _cap_auto, _cap_brief, _mk, _TYPE_PRELUDE) and
# every shared program prefix (_FS, _NUMS, _WORDS, _LINE) is already defined.
# This file only appends its week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THE OPEN QUESTION TS_ROADMAP LEFT, AND HOW IT IS SETTLED.
#
# "The app has no timer, so 'under time' cannot be enforced. Either make this a
#  `brief` (unjudged) capstone with a self-scored rubric … or lean on the Mastery
#  track's judged final."
#
# Both, each where it is strong:
#
#   * The LESSONS are five judged "rounds" of interview problems, written with
#     `_fn` — the learner writes only the function, a hidden driver calls it, and the
#     RETURN VALUE is graded, which is how interviewers actually pose problems.
#     Every prompt states a time box. The judge cannot enforce it; the learner can,
#     and lesson 1 says how.
#   * The CAPSTONE is a `_cap_brief` — the course's first — describing the full
#     90-minute mock loop, with a self-scoring rubric and a reference write-up that
#     narrates a strong answer. Its STRETCH is judged, so the week still ends on a
#     graded problem.
#   * Lesson 1 points at the Mastery track's timed final for anyone who wants a
#     clock the app does keep.
#
# EVERY PROBLEM IS REVIEW, NOT NEW MATERIAL: each round names the weeks it draws on.
# The only genuinely new content is method — how to run a problem in forty-five
# minutes — and the TypeScript round's interview staples (exhaustiveness with
# `never`, `unknown` versus `any`).
#
# Determinism: every problem with more than one acceptable answer pins one in its
# prompt (top-k ties by value; two-sum returns the first pair found in index order).
# ---------------------------------------------------------------------------


# --- Week 32 --------------------------------------------------------------
_WEEKS.append(_week(
    32, 8, _M8,
    "Mock Interview Week",
    "Thirty-one weeks of material, used the way an interview uses it: a problem, a time box, and an answer you can explain. Five judged rounds, a TypeScript round, and a full self-run mock to finish.",
    """
This is the last week. It teaches almost nothing new — on purpose. Every problem
here is something the course has already given you the tools for; the skill being
practised is **using them under a clock, and explaining what you did**.

## How this week works

* **Five rounds** of problems, each graded on what your function **returns** — the
  way interviewers pose them: "implement `longestConsecutive(nums)`". Each round names
  the weeks it draws on.
* **Every problem has a time box** in its prompt. The app does not keep time, so you
  do: start a timer on your phone before you read the problem, and stop when it
  passes. Note your time. The number matters less than the trend across the week.
* **A TypeScript round**, because a TypeScript interview will also ask about the
  language: exhaustiveness with `never`, `unknown` versus `any`, generic signatures.
* **The capstone is a full mock**: three problems, ninety minutes, self-scored
  against a rubric. It is a *brief* — nothing is judged — because the point is the
  whole loop, including talking.

(If you want a clock the app does keep, the **Mastery track's final** is a timed,
judged assessment.)

## The one new thing: method

Lesson 1 is a seven-step routine for a single problem. It is the difference between
knowing the material and being able to show it.

⏱️ Budget about **ten hours** — most of it with a timer running.
""",
    objectives=[
        "Run one problem through clarify → examples → brute force → optimise → code → test → complexity",
        "State a brute force and its cost before optimising",
        "Solve array and hashing problems in a time box",
        "Solve two-pointer, window and binary-search problems in a time box",
        "Solve grid and graph problems in a time box",
        "Solve DP and counting problems in a time box",
        "Answer TypeScript-specific questions: exhaustiveness, unknown, generic signatures",
        "Run a full self-timed mock and score it honestly",
    ],
    why="Knowing thirty-one weeks of material and demonstrating it in forty-five minutes are different skills, and the second one is practised, not learned. A week of time-boxed problems — each one recognisable from the course — is how the first skill becomes the second.",
    est_minutes=600,
    glossary=[
        _gloss("time box", "A fixed time for one problem. Start the timer before reading."),
        _gloss("clarifying question", "Ask about input size, duplicates, empties and ties before writing anything."),
        _gloss("brute force", "The obvious correct solution, stated with its cost, BEFORE optimising."),
        _gloss("walkthrough", "Running your code by hand on an example, out loud."),
        _gloss("edge case", "Empty input, one element, all equal, negative, the largest allowed."),
        _gloss("exhaustiveness check", "A `never`-typed default that fails to compile when a union gains a member."),
        _gloss("unknown", "The safe top type: you must narrow before using it. `any` switches checking off."),
        _gloss("mock loop", "Several problems, a clock, and a scored review afterwards."),
    ],
    cheatsheet="""
**The routine, for every problem**

1. **Clarify** — sizes, duplicates, empty input, ties, what to return when nothing fits.
2. **Examples** — one normal, one edge. Write the expected answer for each.
3. **Brute force** — say it and its cost out loud. It is a correct answer; it is your floor.
4. **Optimise** — name the pattern (week 23's table, week 26's recipe, week 27's BFS/DFS).
5. **Code** — the optimised version, cleanly.
6. **Test** — walk the examples through your code by hand, including the edge case.
7. **Complexity** — time and space, and what dominates.

**Pattern → tool (the whole course on one card)**

| the question says | reach for | week |
|---|---|---|
| "consecutive", "contiguous", "longest … such that" | sliding window | 23 |
| "sorted", "find", "first/last position" | binary search / bounds | 22 |
| "pair", "sum to", "from both ends" | two pointers | 22 |
| "seen before", "count", "group" | Map / Set | 19 |
| "every subset / order / placement" | backtracking | 25 |
| "how many ways", "fewest", "longest" + overlap | DP | 26 |
| "fewest steps", "reachable", "prerequisites" | BFS / DFS / topo | 27 |
| "smallest so far", "top k", "rooms" | heap / intervals | 28 |

**TypeScript round**

```ts
function assertNever(x: never): never { throw new Error(`unexpected ${String(x)}`); }
// a switch whose default calls assertNever(s) stops compiling when a case is missing

const v: unknown = JSON.parse(raw);        // must narrow before use
const w: any = JSON.parse(raw);            // checking switched off — avoid
```
""",
    self_check=[
        "Can you recite the seven-step routine?",
        "Do you state a brute force and its cost before optimising?",
        "Did you time every problem this week, and does the trend improve?",
        "Can you name the pattern from the wording, before coding?",
        "Do you walk your code through an edge case before saying you are done?",
        "Can you state time and space complexity for every solution you wrote this week?",
        "Can you explain what `never` does in an exhaustive switch?",
        "Can you explain why `unknown` is safer than `any`?",
        "Have you run the full mock and scored it honestly?",
    ],
    review=[
        _q("The first thing to do with an interview problem is…",
           ["code", "clarify — sizes, duplicates, empties, ties", "optimise", "state the complexity"], 1,
           "Before examples, before code."),
        _q("Why state a brute force first?",
           ["to waste time", "it is a correct floor, and its cost shows what the optimisation must beat", "interviewers require it",
            "it is faster"], 1,
           "And it proves you understood the problem."),
        _q("\"The longest run of consecutive integers, in O(n)\" points at…",
           ["sorting", "a Set, starting only from run beginnings", "DP", "a heap"], 1,
           "Round 1."),
        _q("\"Search in a rotated sorted array in O(log n)\" points at…",
           ["linear scan", "binary search, deciding which half is sorted", "two pointers", "a Map"], 1,
           "Round 2."),
        _q("\"Can every course be taken?\" points at…",
           ["DP", "cycle detection / Kahn's algorithm", "binary search", "greedy"], 1,
           "Round 3."),
        _q("\"The fewest coins to make an amount\" points at…",
           ["greedy", "DP", "backtracking", "two pointers"], 1,
           "Round 4 — and week 26's counter-example to greedy."),
        _q("A switch with `default: return assertNever(s)`…",
           ["crashes", "stops compiling when the union gains a member nobody handles", "is slow", "is required"], 1,
           "Exhaustiveness."),
        _q("`unknown` differs from `any` in that…",
           ["it is slower", "you must narrow it before using it", "it is only for JSON", "nothing"], 1,
           "The safe top type."),
        _q("Walking your code through an example before saying 'done'…",
           ["wastes time", "is how most bugs are caught in an interview", "is optional", "is the interviewer's job"], 1,
           "Step 6."),
    ],
    milestone="The course ends on a full mock interview: three problems — one from the early rounds, one from the late rounds, one TypeScript question — in ninety minutes, run with the seven-step routine and scored against a rubric. Thirty-two weeks after your first line of code.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w32-method", "Forty-five minutes, one problem",
            "A routine that makes what you know visible.",
            """
Interviews are not exams. The interviewer is not only checking the answer; they are
watching **how you get there**, because that is what working with you would be like.
A routine makes that visible — and keeps you moving when you are stuck.

## The seven steps

1. **Clarify.** How large can the input be? Duplicates? Empty input? Ties? What if
   nothing qualifies? (Every problem this week pins these down in its prompt, which
   is a luxury an interview will not give you.)
2. **Examples.** One ordinary, one edge case, with the answer for each written down.
3. **Brute force.** Say it, and say its cost. It is a correct answer and a floor.
4. **Optimise.** Name the pattern — the cheat sheet maps wording to weeks — and the
   cost it gets you.
5. **Code** the optimised version.
6. **Test**, by walking your examples through the code by hand. Most interview bugs
   are caught here, by the candidate, which is exactly what the interviewer hopes to
   see.
7. **Complexity.** Time and space, and which part dominates.

## Timing

Start a timer **before** reading. A typical medium is 20-25 minutes of a 45-minute
slot; the rest is talk. If the brute force is taking more than ten minutes, say so
and write it anyway — a working O(n²) beats an unfinished O(n).

## This lesson's problems

The same question twice — brute force, then optimised — because step 3 before step
4 is the habit most worth building. Then a classic with a pinned tie-rule, since
"which pair?" is exactly the kind of thing to clarify.

> ⚠️ **Common mistakes:** coding before clarifying; optimising before having any
> correct answer; and saying "done" without walking an example through.
""",
            warmup=[
                _q("Step 3, before optimising, is…",
                   ["code", "the brute force and its cost", "complexity", "testing"], 1,
                   "Your floor."),
                _q("Most interview bugs are caught by…",
                   ["the interviewer", "walking your own examples through the code", "the compiler", "luck"], 1,
                   "Step 6."),
                _q("Ten minutes in with no brute force written, you should…",
                   ["keep thinking silently", "say so and write the brute force", "give up", "optimise anyway"], 1,
                   "A working O(n²) beats an unfinished O(n)."),
                _q("The timer starts…",
                   ["after reading", "before reading", "when coding", "never"], 1,
                   "Reading is part of the time."),
            ],
            exercises=[
                _fn("tscourse-w32-md-1", "Brute force first ⏱ 5 min",
                    "Return whether any two DIFFERENT positions in `nums` sum to `target`. Write the obvious "
                    "O(n²) version: every pair.",
                    "hasPairBrute", [("nums", "number[]"), ("target", "number")], "boolean",
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  for (let j = i + 1; j < nums.length; j = j + 1) {\n'
                    '    if ((nums[i] ?? 0) + (nums[j] ?? 0) === target) {\n'
                    '      return true;\n    }\n  }\n}\n'
                    'return false;\n',
                    [("2 7 11 15\n9", "true"), ("1 2 3\n7", "false"), ("5 5\n10", "true"), ("5\n10", "false")],
                    hints=["Every pair i < j, once.",
                           "Return true the moment a pair matches."],
                    difficulty="Easy"),
                _fn("tscourse-w32-md-2", "Then optimise ⏱ 10 min",
                    "The same question in O(n): one pass, remembering what you have seen (week 19).",
                    "hasPair", [("nums", "number[]"), ("target", "number")], "boolean",
                    'const seen = new Set<number>();\n'
                    'for (const x of nums) {\n'
                    '  if (seen.has(target - x)) {\n'
                    '    return true;\n  }\n'
                    '  seen.add(x);\n}\n'
                    'return false;\n',
                    [("2 7 11 15\n9", "true"), ("1 2 3\n7", "false"), ("5 5\n10", "true"), ("5\n10", "false")],
                    hints=["For each x, the partner it needs is target - x.",
                           "Check for the partner BEFORE adding x, so an element never pairs with itself."],
                    difficulty="Easy"),
                _fn("tscourse-w32-md-3", "Two sum, with the tie pinned ⏱ 10 min",
                    "Return the indices `[i, j]` (i < j) of two numbers summing to `target`. If several pairs "
                    "work, return the one whose SECOND index is smallest — the first one a single left-to-right "
                    "pass finds. If none does, return an empty array.",
                    "twoSum", [("nums", "number[]"), ("target", "number")], "number[]",
                    'const at = new Map<number, number>();\n'
                    'for (let j = 0; j < nums.length; j = j + 1) {\n'
                    '  const x = nums[j] ?? 0;\n'
                    '  const i = at.get(target - x);\n'
                    '  if (i !== undefined) {\n'
                    '    return [i, j];\n  }\n'
                    '  if (!at.has(x)) {\n'
                    '    at.set(x, j);\n  }\n}\n'
                    'return [];\n',
                    [("2 7 11 15\n9", "0 1"), ("3 2 4\n6", "1 2"), ("3 3\n6", "0 1"), ("1 2\n9", "")],
                    hints=["Store each value's FIRST index in a Map.",
                           "Look up the partner before storing the current value.",
                           "The first match found scanning j left to right has the smallest second index."],
                    difficulty="Medium"),
            ],
            quiz=[
                _q("Why does hasPair check before adding x?",
                   ["style", "so an element cannot pair with itself", "speed", "for duplicates only"], 1,
                   "[5] with target 10 must be false."),
                _q("\"If several pairs work, which one?\" is…",
                   ["a trick", "a clarifying question — ask it", "irrelevant", "the interviewer's problem"], 1,
                   "Step 1."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w32-round1", "Round 1: arrays & hashing",
            "Weeks 6, 19 and 21 — counting, remembering, and not recomputing.",
            """
Four problems. Before each, say which week's tool it needs — then start the timer.

* **Longest consecutive run** — a `Set`, and only start counting at the *beginning*
  of a run (a value whose predecessor is absent). That one condition is what makes it
  O(n) rather than O(n²).
* **Product of everything else** — no division. Two passes: the product of
  everything to the left, then multiply in everything to the right. A prefix
  computation (week 23), with products instead of sums.
* **Top k frequent** — week 19's counting Map, then a sort with a tie-break. The
  prompt pins the tie order, as an interviewer would if you asked.
* **First unique character** — count, then scan again in order.

> ⚠️ **Common mistakes:** counting a run from every element (quadratic); using
> division when a zero is present; and forgetting the tie-break.
""",
            warmup=[
                _q("Longest consecutive is O(n) because counting starts only where…",
                   ["the value is smallest", "the value's predecessor is absent — a run's beginning", "the Set is sorted", "always"], 1,
                   "Each run is walked once."),
                _q("Product-except-self without division uses…",
                   ["a Map", "a left-products pass and a right-products pass", "sorting", "recursion"], 1,
                   "Prefix and suffix."),
                _q("Top-k frequent is…",
                   ["a heap only", "a count, then a sort or a heap", "binary search", "two pointers"], 1,
                   "Week 19 or week 28."),
                _q("First unique character needs how many passes?",
                   ["one", "two — count, then find", "n", "log n"], 1,
                   "Count, then scan in order."),
            ],
            exercises=[
                _fn("tscourse-w32-r1-1", "Longest consecutive run ⏱ 15 min",
                    "Return the length of the longest run of consecutive integers that appear in `nums`, in any "
                    "order. O(n).",
                    "longestConsecutive", [("nums", "number[]")], "number",
                    'const set = new Set(nums);\n'
                    'let best = 0;\n'
                    'for (const x of set) {\n'
                    '  if (set.has(x - 1)) {\n'
                    '    continue;\n  }\n'
                    '  let len = 1;\n'
                    '  while (set.has(x + len)) {\n'
                    '    len = len + 1;\n  }\n'
                    '  best = Math.max(best, len);\n}\n'
                    'return best;\n',
                    [("100 4 200 1 3 2", "4"), ("0 3 7 2 5 8 4 6 0 1", "9"), ("5", "1"), ("", "0")],
                    hints=["Put everything in a Set.",
                           "Only start counting from x when x - 1 is absent.",
                           "Then count upward while x + len is present."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r1-2", "Product of everything else ⏱ 15 min",
                    "Return an array where each position holds the product of every OTHER element. No division.",
                    "productExceptSelf", [("nums", "number[]")], "number[]",
                    'const out = new Array<number>(nums.length).fill(1);\n'
                    'let left = 1;\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  out[i] = left;\n'
                    '  left = left * (nums[i] ?? 0);\n}\n'
                    'let right = 1;\n'
                    'for (let i = nums.length - 1; i >= 0; i = i - 1) {\n'
                    '  out[i] = (out[i] ?? 1) * right;\n'
                    '  right = right * (nums[i] ?? 0);\n}\n'
                    'return out;\n',
                    [("1 2 3 4", "24 12 8 6"), ("2 3", "3 2"), ("-1 1 0 -3 3", "0 0 9 0 0")],
                    hints=["out[i] = (product of everything left of i) × (product of everything right of i).",
                           "One pass left to right fills the left products; one pass right to left multiplies in the right ones."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r1-3", "Top k frequent ⏱ 15 min",
                    "Return the `k` most frequent values, most frequent first; equal frequencies in ascending "
                    "order of value.",
                    "topKFrequent", [("nums", "number[]"), ("k", "number")], "number[]",
                    'const counts = new Map<number, number>();\n'
                    'for (const x of nums) {\n'
                    '  counts.set(x, (counts.get(x) ?? 0) + 1);\n}\n'
                    'return [...counts.entries()]\n'
                    '  .sort((a, b) => b[1] - a[1] || a[0] - b[0])\n'
                    '  .slice(0, k)\n'
                    '  .map(([x]) => x);\n',
                    [("1 1 1 2 2 3\n2", "1 2"), ("4 4 5 5 6\n2", "4 5"), ("7\n1", "7")],
                    hints=["Count with a Map.",
                           "Sort entries by count descending, then value ascending (week 19's || tie-break).",
                           "Take the first k values."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r1-4", "First unique character ⏱ 10 min",
                    "Return the index of the first character that appears exactly once, or -1.",
                    "firstUnique", [("s", "string")], "number",
                    'const counts = new Map<string, number>();\n'
                    'for (const ch of s) {\n'
                    '  counts.set(ch, (counts.get(ch) ?? 0) + 1);\n}\n'
                    'for (let i = 0; i < s.length; i = i + 1) {\n'
                    '  if (counts.get(s.charAt(i)) === 1) {\n'
                    '    return i;\n  }\n}\n'
                    'return -1;\n',
                    [("leetcode", "0"), ("loveleetcode", "2"), ("aabb", "-1")],
                    hints=["Count every character first.",
                           "Then scan in order for the first with a count of 1."],
                    difficulty="Easy"),
            ],
            quiz=[
                _q("longestConsecutive iterates the SET rather than nums because…",
                   ["style", "duplicates would otherwise repeat work", "sets are sorted", "speed of has"], 1,
                   "Each distinct value once."),
                _q("productExceptSelf's extra space, not counting the output, is…",
                   ["O(n)", "O(1)", "O(log n)", "O(n²)"], 1,
                   "Two running products."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w32-round2", "Round 2: pointers, windows, search",
            "Weeks 22 and 23 — the patterns that turn O(n²) into O(n) and O(n) into O(log n).",
            """
* **Search a rotated array** — binary search, but first decide which half is still
  sorted; the target is either inside that half's range or in the other half.
* **Container with the most water** — two pointers from the ends; always move the
  shorter side, because the area is limited by it and keeping it can never help.
* **Longest substring without repeats** — week 23's `lastSeen` window.
* **Shortest subarray reaching a sum** — week 23's variable window, recording the
  width *inside* the shrink loop.

For each, say the brute force and its cost out loud first. All four have an O(n²) or
O(n) brute force that is a perfectly good opening sentence.

> ⚠️ **Common mistakes:** in the rotated search, comparing against the wrong end;
> moving the taller pointer; and recording a window's width outside the loop that
> makes it valid.
""",
            warmup=[
                _q("In a rotated sorted array, at any midpoint…",
                   ["both halves are sorted", "at least one half is sorted", "neither is sorted", "the left half is sorted"], 1,
                   "Decide which, then where the target can be."),
                _q("Container-with-most-water moves…",
                   ["the taller side", "the shorter side", "both", "the middle"], 1,
                   "The shorter side limits the area."),
                _q("Longest substring without repeats is a…",
                   ["fixed window", "variable window with last-seen indexes", "prefix sum", "binary search"], 1,
                   "Week 23."),
                _q("The shortest subarray with sum ≥ target records its width…",
                   ["after the loop", "inside the shrink loop", "before growing", "never"], 1,
                   "Meeting the condition is what qualifies it."),
            ],
            exercises=[
                _fn("tscourse-w32-r2-1", "Search a rotated array ⏱ 20 min",
                    "`nums` is a sorted array of distinct values rotated at some point. Return the index of "
                    "`target`, or -1. O(log n).",
                    "searchRotated", [("nums", "number[]"), ("target", "number")], "number",
                    'let lo = 0;\n'
                    'let hi = nums.length - 1;\n'
                    'while (lo <= hi) {\n'
                    '  const mid = Math.floor((lo + hi) / 2);\n'
                    '  const m = nums[mid] ?? 0;\n'
                    '  if (m === target) {\n'
                    '    return mid;\n  }\n'
                    '  const l = nums[lo] ?? 0;\n'
                    '  const h = nums[hi] ?? 0;\n'
                    '  if (l <= m) {\n'
                    '    if (l <= target && target < m) {\n'
                    '      hi = mid - 1;\n'
                    '    } else {\n'
                    '      lo = mid + 1;\n    }\n'
                    '  } else if (m < target && target <= h) {\n'
                    '    lo = mid + 1;\n'
                    '  } else {\n'
                    '    hi = mid - 1;\n  }\n}\n'
                    'return -1;\n',
                    [("4 5 6 7 0 1 2\n0", "4"), ("4 5 6 7 0 1 2\n3", "-1"), ("1\n1", "0"), ("3 1\n1", "1")],
                    hints=["If nums[lo] <= nums[mid], the left half is sorted; otherwise the right half is.",
                           "Check whether the target lies within the sorted half's range; if so go there, else the other way.",
                           "Week 22's inclusive row: lo <= hi, mid ± 1."],
                    difficulty="Hard"),
                _fn("tscourse-w32-r2-2", "Container with the most water ⏱ 15 min",
                    "Choose two lines; the water they hold is the distance between them times the shorter "
                    "height. Return the most water. O(n).",
                    "maxArea", [("heights", "number[]")], "number",
                    'let lo = 0;\n'
                    'let hi = heights.length - 1;\n'
                    'let best = 0;\n'
                    'while (lo < hi) {\n'
                    '  const a = heights[lo] ?? 0;\n'
                    '  const b = heights[hi] ?? 0;\n'
                    '  best = Math.max(best, (hi - lo) * Math.min(a, b));\n'
                    '  if (a < b) {\n'
                    '    lo = lo + 1;\n'
                    '  } else {\n'
                    '    hi = hi - 1;\n  }\n}\n'
                    'return best;\n',
                    [("1 8 6 2 5 4 8 3 7", "49"), ("1 1", "1"), ("4 3 2 1 4", "16")],
                    hints=["Start with the widest pair: both ends.",
                           "Moving the TALLER side can only lose width without raising the limit.",
                           "So always move the shorter one."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r2-3", "Longest substring without repeats ⏱ 15 min",
                    "Return the length of the longest substring with no repeated character.",
                    "longestNoRepeat", [("s", "string")], "number",
                    'const lastSeen = new Map<string, number>();\n'
                    'let start = 0;\n'
                    'let best = 0;\n'
                    'for (let i = 0; i < s.length; i = i + 1) {\n'
                    '  const ch = s.charAt(i);\n'
                    '  const prev = lastSeen.get(ch);\n'
                    '  if (prev !== undefined && prev >= start) {\n'
                    '    start = prev + 1;\n  }\n'
                    '  lastSeen.set(ch, i);\n'
                    '  best = Math.max(best, i - start + 1);\n}\n'
                    'return best;\n',
                    [("abcabcbb", "3"), ("bbbbb", "1"), ("pwwkew", "3"), ("", "0")],
                    hints=["Week 23, lesson 3.",
                           "Only a previous copy at or after `start` is a repeat inside the window."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r2-4", "Shortest subarray reaching a sum ⏱ 15 min",
                    "`nums` are positive. Return the length of the shortest contiguous subarray whose sum is at "
                    "least `target`, or 0 if none.",
                    "minSubarrayLen", [("target", "number"), ("nums", "number[]")], "number",
                    'let start = 0;\n'
                    'let sum = 0;\n'
                    'let best = Infinity;\n'
                    'for (let end = 0; end < nums.length; end = end + 1) {\n'
                    '  sum = sum + (nums[end] ?? 0);\n'
                    '  while (sum >= target) {\n'
                    '    best = Math.min(best, end - start + 1);\n'
                    '    sum = sum - (nums[start] ?? 0);\n'
                    '    start = start + 1;\n  }\n}\n'
                    'return best === Infinity ? 0 : best;\n',
                    [("7\n2 3 1 2 4 3", "2"), ("4\n1 4 4", "1"), ("11\n1 1 1 1", "0")],
                    hints=["Positive values make the window monotonic (week 23, lesson 2).",
                           "Record the width INSIDE the shrink loop — meeting the target is what qualifies it."],
                    difficulty="Medium"),
            ],
            quiz=[
                _q("Why must the rotated-array values be distinct?",
                   ["style", "with duplicates, nums[lo] === nums[mid] cannot say which half is sorted", "speed", "for -1"], 1,
                   "A good clarifying question."),
                _q("maxArea is O(n) because…",
                   ["it sorts", "each step moves one pointer inward, n steps in total", "of binary search", "of a Map"], 1,
                   "Week 22's two ends."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w32-round3", "Round 3: grids & graphs",
            "Weeks 20 and 27 — a visited set, and the right container.",
            """
* **Count islands** — a component count over grid cells (week 27, lesson 4), with an
  explicit stack so a large island cannot overflow the call stack.
* **Shortest path through a grid** — BFS from the corner; the first arrival at the
  far corner is the fewest moves.
* **Can every course be taken?** — Kahn's algorithm; output shorter than n is a
  cycle.
* **Count connected components** — a traversal from every unvisited node.

The rows of a grid arrive as strings — `"11000 11000 00100"` is three rows — and a
graph's edges arrive **flattened**: `[1, 0, 2, 1]` is the two edges `1-0` and `2-1`.
Reading an input format quickly and correctly is part of the skill.

> ⚠️ **Common mistakes:** recursing over a large grid; marking visited on dequeue;
> and misreading a flattened edge list by one position.
""",
            warmup=[
                _q("Counting islands is counting…",
                   ["cells", "connected components of land", "edges", "rows"], 1,
                   "Week 27."),
                _q("\"The fewest moves\" in a grid points at…",
                   ["DFS", "BFS", "DP", "a heap"], 1,
                   "First arrival is shortest."),
                _q("Kahn's output shorter than n means…",
                   ["an error", "a cycle", "disconnected", "undirected"], 1,
                   "Some courses wait forever."),
                _q("`[1, 0, 2, 1]` flattened is the edges…",
                   ["1-0 and 2-1", "1-2 and 0-1", "1-0-2-1", "four edges"], 0,
                   "Pairs, in order."),
            ],
            exercises=[
                _fn("tscourse-w32-r3-1", "Count the islands ⏱ 20 min",
                    "Each string in `grid` is a row of `1` (land) and `0` (water). Return the number of islands "
                    "(land connected up, down, left or right).",
                    "numIslands", [("grid", "string[]")], "number",
                    'const R = grid.length;\n'
                    'const C = (grid[0] ?? "").length;\n'
                    'const seen = new Set<string>();\n'
                    'let count = 0;\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if ((grid[r] ?? "").charAt(c) !== "1" || seen.has(`${r},${c}`)) {\n'
                    '      continue;\n    }\n'
                    '    count = count + 1;\n'
                    '    seen.add(`${r},${c}`);\n'
                    '    const stack: [number, number][] = [[r, c]];\n'
                    '    while (stack.length > 0) {\n'
                    '      const top = stack.pop();\n'
                    '      if (top === undefined) {\n'
                    '        continue;\n      }\n'
                    '      const [cr, cc] = top;\n'
                    '      const next: [number, number][] = [[cr - 1, cc], [cr + 1, cc], [cr, cc - 1], [cr, cc + 1]];\n'
                    '      for (const [nr, nc] of next) {\n'
                    '        if (nr < 0 || nr >= R || nc < 0 || nc >= C) {\n'
                    '          continue;\n        }\n'
                    '        if ((grid[nr] ?? "").charAt(nc) === "1" && !seen.has(`${nr},${nc}`)) {\n'
                    '          seen.add(`${nr},${nc}`);\n'
                    '          stack.push([nr, nc]);\n        }\n      }\n    }\n  }\n}\n'
                    'return count;\n',
                    [("11000 11000 00100 00011", "3"), ("111 010 111", "1"), ("000", "0")],
                    hints=["Each unvisited land cell starts a new island.",
                           "Flood it with an explicit stack, marking cells as you push them.",
                           "Bounds-check every neighbour."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r3-2", "Fewest moves across ⏱ 20 min",
                    "`grid` rows are `0` (open) and `1` (wall). Moving up, down, left or right, return the "
                    "fewest moves from the top-left to the bottom-right, or -1.",
                    "shortestPath", [("grid", "string[]")], "number",
                    'const R = grid.length;\n'
                    'const C = (grid[0] ?? "").length;\n'
                    'const open = (r: number, c: number): boolean =>\n'
                    '  r >= 0 && r < R && c >= 0 && c < C && (grid[r] ?? "").charAt(c) === "0";\n'
                    'if (!open(0, 0)) {\n'
                    '  return -1;\n}\n'
                    'const dist = new Map<string, number>([["0,0", 0]]);\n'
                    'const queue: [number, number][] = [[0, 0]];\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  const [r, c] = queue[head] ?? [0, 0];\n'
                    '  const d = dist.get(`${r},${c}`) ?? 0;\n'
                    '  if (r === R - 1 && c === C - 1) {\n'
                    '    return d;\n  }\n'
                    '  const next: [number, number][] = [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]];\n'
                    '  for (const [nr, nc] of next) {\n'
                    '    if (open(nr, nc) && !dist.has(`${nr},${nc}`)) {\n'
                    '      dist.set(`${nr},${nc}`, d + 1);\n'
                    '      queue.push([nr, nc]);\n    }\n  }\n}\n'
                    'return -1;\n',
                    [("000 110 000", "4"), ("01 10", "-1"), ("0", "0"), ("10 00", "-1")],
                    hints=["BFS from the corner with a head-index queue (week 18).",
                           "Mark a cell's distance when it is queued, not when it is taken off.",
                           "A blocked start is -1 at once."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r3-3", "Can every course be taken? ⏱ 20 min",
                    "There are `n` courses. `pairs` is flattened: `[a0, b0, a1, b1, …]`, each pair meaning course "
                    "b must be taken before course a. Return whether all n can be taken.",
                    "canFinish", [("n", "number"), ("pairs", "number[]")], "boolean",
                    'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
                    'const indegree = new Array<number>(n).fill(0);\n'
                    'for (let i = 0; i + 1 < pairs.length; i = i + 2) {\n'
                    '  const a = pairs[i] ?? 0;\n'
                    '  const b = pairs[i + 1] ?? 0;\n'
                    '  adj[b]?.push(a);\n'
                    '  indegree[a] = (indegree[a] ?? 0) + 1;\n}\n'
                    'const queue: number[] = [];\n'
                    'for (let u = 0; u < n; u = u + 1) {\n'
                    '  if (indegree[u] === 0) {\n'
                    '    queue.push(u);\n  }\n}\n'
                    'for (let head = 0; head < queue.length; head = head + 1) {\n'
                    '  for (const v of adj[queue[head] ?? 0] ?? []) {\n'
                    '    indegree[v] = (indegree[v] ?? 0) - 1;\n'
                    '    if (indegree[v] === 0) {\n'
                    '      queue.push(v);\n    }\n  }\n}\n'
                    'return queue.length === n;\n',
                    [("2\n1 0", "true"), ("2\n1 0 0 1", "false"), ("3\n", "true"), ("4\n1 0 2 1 3 2 1 3", "false")],
                    hints=["The edge goes from b (the prerequisite) to a.",
                           "Kahn's algorithm (week 27): start from in-degree 0.",
                           "If fewer than n are ever placed, a cycle blocks the rest."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r3-4", "Count the components ⏱ 15 min",
                    "An undirected graph has `n` nodes; `edges` is flattened `[u0, v0, u1, v1, …]`. Return the "
                    "number of connected components.",
                    "countComponents", [("n", "number"), ("edges", "number[]")], "number",
                    'const adj: number[][] = Array.from({ length: n }, (): number[] => []);\n'
                    'for (let i = 0; i + 1 < edges.length; i = i + 2) {\n'
                    '  const u = edges[i] ?? 0;\n'
                    '  const v = edges[i + 1] ?? 0;\n'
                    '  adj[u]?.push(v);\n'
                    '  adj[v]?.push(u);\n}\n'
                    'const seen = new Array<boolean>(n).fill(false);\n'
                    'let count = 0;\n'
                    'for (let s = 0; s < n; s = s + 1) {\n'
                    '  if (seen[s]) {\n'
                    '    continue;\n  }\n'
                    '  count = count + 1;\n'
                    '  seen[s] = true;\n'
                    '  const stack = [s];\n'
                    '  while (stack.length > 0) {\n'
                    '    const u = stack.pop() ?? 0;\n'
                    '    for (const v of adj[u] ?? []) {\n'
                    '      if (!seen[v]) {\n'
                    '        seen[v] = true;\n'
                    '        stack.push(v);\n      }\n    }\n  }\n}\n'
                    'return count;\n',
                    [("5\n0 1 1 2 3 4", "2"), ("3\n", "3"), ("4\n0 1 2 3 1 2", "1")],
                    hints=["Build an undirected adjacency list from the flattened pairs.",
                           "Every traversal started from an unvisited node is a new component."],
                    difficulty="Easy"),
            ],
            quiz=[
                _q("Why an explicit stack for islands?",
                   ["style", "a large island would be a deep recursion — week 25's overflow", "speed", "BFS"], 1,
                   "Grids can be big."),
                _q("canFinish's time complexity is…",
                   ["O(n²)", "O(n + number of pairs)", "O(n log n)", "O(2ⁿ)"], 1,
                   "Each node and edge once."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w32-round4", "Round 4: DP & counting",
            "Weeks 25 and 26 — find the state, then fill the table.",
            """
For each, write the **five answers** of week 26's recipe before any code: state,
transition, base case, order, and where the answer is. Saying them aloud is itself
the strongest signal you can give an interviewer on a DP problem.

* **Coin change** — fewest coins; `Infinity` for unreachable, `-1` only when
  reporting.
* **Longest common subsequence** — the `(m+1) × (n+1)` table with its empty-prefix
  row and column.
* **Word break** — `ok[i]`: can the first `i` characters be split?
* **Count subsets with a sum** — 0/1 counting; iterate the target **backwards** so
  each number is used once (week 26, lesson 6).

> ⚠️ **Common mistakes:** coding before the state is stated; `-1` inside the table;
> and a forwards loop where each item may be used only once.
""",
            warmup=[
                _q("Before coding a DP, state…",
                   ["the complexity", "state, transition, base case, order, answer", "the brute force only", "nothing"], 1,
                   "Week 26's recipe."),
                _q("Coin change uses what for 'unreachable' inside the table?",
                   ["-1", "Infinity", "0", "null"], 1,
                   "It composes with + 1 and min."),
                _q("Word break's state is…",
                   ["the word count", "whether the first i characters can be split", "the dictionary", "a Set"], 1,
                   "A prefix table."),
                _q("Counting subsets with each number used once iterates the target…",
                   ["forwards", "backwards", "twice", "randomly"], 1,
                   "Or a number is counted twice."),
            ],
            exercises=[
                _fn("tscourse-w32-r4-1", "Coin change ⏱ 20 min",
                    "Return the fewest coins that make `amount` (any coin may be used any number of times), or "
                    "-1 if it cannot be made.",
                    "coinChange", [("coins", "number[]"), ("amount", "number")], "number",
                    'const dp: number[] = [0];\n'
                    'for (let a = 1; a <= amount; a = a + 1) {\n'
                    '  let best = Infinity;\n'
                    '  for (const c of coins) {\n'
                    '    if (c <= a) {\n'
                    '      best = Math.min(best, (dp[a - c] ?? Infinity) + 1);\n    }\n  }\n'
                    '  dp.push(best);\n}\n'
                    'const answer = dp[amount] ?? Infinity;\n'
                    'return answer === Infinity ? -1 : answer;\n',
                    [("1 2 5\n11", "3"), ("2\n3", "-1"), ("1\n0", "0"), ("1 3 4\n6", "2")],
                    hints=["State: the amount. Transition: 1 + the best over coins that fit.",
                           "Infinity inside the table; -1 only when returning."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r4-2", "Longest common subsequence ⏱ 20 min",
                    "Return the length of the longest subsequence common to `a` and `b`.",
                    "lcsLength", [("a", "string"), ("b", "string")], "number",
                    'const dp: number[][] = Array.from({ length: a.length + 1 }, (): number[] => new Array<number>(b.length + 1).fill(0));\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  const row = dp[i] ?? [];\n'
                    '  const up = dp[i - 1] ?? [];\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    row[j] = a.charAt(i - 1) === b.charAt(j - 1)\n'
                    '      ? (up[j - 1] ?? 0) + 1\n'
                    '      : Math.max(up[j] ?? 0, row[j - 1] ?? 0);\n  }\n}\n'
                    'return dp[a.length]?.[b.length] ?? 0;\n',
                    [("abcde\nace", "3"), ("abc\ndef", "0"), ("aggtab\ngxtxayb", "4")],
                    hints=["An (m+1) × (n+1) table; row and column 0 are the empty prefix.",
                           "Characters at i - 1 and j - 1 — the table is shifted by one."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r4-3", "Word break ⏱ 20 min",
                    "Return whether `s` can be split into a sequence of words from `words` (each may be reused).",
                    "wordBreak", [("s", "string"), ("words", "string[]")], "boolean",
                    'const dict = new Set(words);\n'
                    'const ok = new Array<boolean>(s.length + 1).fill(false);\n'
                    'ok[0] = true;\n'
                    'for (let i = 1; i <= s.length; i = i + 1) {\n'
                    '  for (let j = 0; j < i; j = j + 1) {\n'
                    '    if (ok[j] && dict.has(s.slice(j, i))) {\n'
                    '      ok[i] = true;\n'
                    '      break;\n    }\n  }\n}\n'
                    'return ok[s.length] ?? false;\n',
                    [("leetcode\nleet code", "true"), ("catsandog\ncats dog sand and cat", "false"),
                     ("applepenapple\napple pen", "true")],
                    hints=["ok[i]: the first i characters can be split.",
                           "ok[i] is true if some ok[j] is true and s.slice(j, i) is a word."],
                    difficulty="Medium"),
                _fn("tscourse-w32-r4-4", "Count the subsets ⏱ 15 min",
                    "Return how many subsets of `nums` (positions distinct, values positive) sum to exactly "
                    "`target`.",
                    "countSubsets", [("nums", "number[]"), ("target", "number")], "number",
                    'const ways = new Array<number>(target + 1).fill(0);\n'
                    'ways[0] = 1;\n'
                    'for (const x of nums) {\n'
                    '  for (let t = target; t >= x; t = t - 1) {\n'
                    '    ways[t] = (ways[t] ?? 0) + (ways[t - x] ?? 0);\n  }\n}\n'
                    'return ways[target] ?? 0;\n',
                    [("2 3 5 7\n10", "2"), ("1 1 1\n2", "3"), ("5\n3", "0")],
                    hints=["Subset sum, counting instead of booleans.",
                           "Backwards over the target, so each number is used at most once."],
                    difficulty="Medium"),
            ],
            quiz=[
                _q("Saying the five DP answers aloud before coding…",
                   ["wastes time", "is the strongest signal on a DP problem", "is optional", "confuses interviewers"], 1,
                   "It shows the method, not a memorised answer."),
                _q("Word break by backtracking alone is…",
                   ["fine", "exponential on inputs like \"aaaa…b\"; the table makes it O(n²)", "linear", "O(n log n)"], 1,
                   "Overlapping subproblems."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w32-typescript", "Round 5: the TypeScript questions",
            "What a TypeScript interview asks about the language itself.",
            """
A TypeScript interview will usually include a few questions about the language.
They are rarely exotic. Three come up constantly.

## Exhaustiveness

```ts
type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r * s.r;
    case "square": return s.side * s.side;
    default: return assertNever(s);
  }
}
function assertNever(x: never): never { throw new Error(`unexpected ${String(x)}`); }
```

After both cases, `s` has been narrowed to `never`. Add a `triangle` to `Shape` and
forget its case, and `s` in the default is a triangle — which is not assignable to
`never` — so **the program stops compiling at the switch you forgot**. That is the
single most useful thing a discriminated union (week 9) does.

## `unknown` versus `any`

Both accept any value. `any` **switches checking off** — anything goes, including
calling methods that are not there. `unknown` **must be narrowed** before use (week
15): `'v' is of type 'unknown'` until a `typeof`, `instanceof` or guard says what it
is. Parsed input should be `unknown`.

## A generic signature on demand

"Write the signature of `groupBy`." The answer shows whether you can make types follow
values: `function groupBy<T, K extends PropertyKey>(xs: readonly T[], key: (x: T) => K):
Partial<Record<K, T[]>>`. The `Partial` is the honest part — not every possible key
will have a group.

> ⚠️ **Common mistakes:** a `default` that silently returns 0; `any` for parsed
> input; and a generic signature that returns `Record<string, any>`.
""",
            warmup=[
                _q("After handling every case of a union in a switch, the value in `default` is…",
                   ["unknown", "never", "any", "the last case"], 1,
                   "Which is what assertNever checks."),
                _q("`unknown` must be…",
                   ["cast", "narrowed before use", "annotated", "avoided"], 1,
                   "The safe top type."),
                _q("`any` differs from `unknown` in that…",
                   ["it is safer", "it switches type checking off", "it is newer", "nothing"], 1,
                   "Avoid it for input."),
                _q("groupBy's return type is `Partial<Record<K, T[]>>` because…",
                   ["style", "not every possible key will have a group", "speed", "K is a string"], 1,
                   "Honest types."),
            ],
            exercises=[
                _diagnose("tscourse-w32-ts-d1", "The case nobody wrote",
                          "TS2345: Argument of type '{ kind: \"triangle\"; base: number; height: number; }' is not assignable to parameter of type 'never'.",
                          'type Shape =\n'
                          '  | { kind: "circle"; r: number }\n'
                          '  | { kind: "square"; side: number }\n'
                          '  | { kind: "triangle"; base: number; height: number };\n'
                          'function assertNever(x: never): never {\n'
                          '  throw new Error(`unexpected ${String(x)}`);\n}\n'
                          'function area(s: Shape): number {\n'
                          '  switch (s.kind) {\n'
                          '    case "circle":\n'
                          '      return Math.round(Math.PI * s.r * s.r);\n'
                          '    case "square":\n'
                          '      return s.side * s.side;\n'
                          '    default:\n'
                          '      return assertNever(s);\n  }\n}\n'
                          'console.log(area({ kind: "triangle", base: 4, height: 3 }));\n',
                          'type Shape =\n'
                          '  | { kind: "circle"; r: number }\n'
                          '  | { kind: "square"; side: number }\n'
                          '  | { kind: "triangle"; base: number; height: number };\n'
                          'function assertNever(x: never): never {\n'
                          '  throw new Error(`unexpected ${String(x)}`);\n}\n'
                          'function area(s: Shape): number {\n'
                          '  switch (s.kind) {\n'
                          '    case "circle":\n'
                          '      return Math.round(Math.PI * s.r * s.r);\n'
                          '    case "square":\n'
                          '      return s.side * s.side;\n'
                          '    case "triangle":\n'
                          '      return (s.base * s.height) / 2;\n'
                          '    default:\n'
                          '      return assertNever(s);\n  }\n}\n'
                          'console.log(area({ kind: "triangle", base: 4, height: 3 }));\n',
                          [("", "6")],
                          hints=["What type does s have in the default branch now?",
                                 "A member of the union has no case.",
                                 "Add case \"triangle\": return (s.base * s.height) / 2;"],
                          difficulty="Medium"),
                _diagnose("tscourse-w32-ts-d2", "Input you have not looked at",
                          "TS18046: 'v' is of type 'unknown'.",
                          _LINE +
                          'function parse(raw: string): unknown {\n'
                          '  return JSON.parse(raw);\n}\n'
                          'const v = parse(line);\n'
                          'console.log(v.length);\n',
                          _LINE +
                          'function parse(raw: string): unknown {\n'
                          '  return JSON.parse(raw);\n}\n'
                          'const v = parse(line);\n'
                          'console.log(typeof v === "string" || Array.isArray(v) ? v.length : -1);\n',
                          [('"hello"', "5"), ("[1,2,3]", "3"), ("42", "-1")],
                          hints=["Only strings and arrays have a length. What is v, as far as the checker knows?",
                                 "Narrow first: typeof, or Array.isArray.",
                                 "Report -1 for anything without a length."],
                          difficulty="Easy"),
                _design("tscourse-w32-ts-des1", "Design groupBy's signature",
                        "The implementation is written. Declare the signature: generic over the element type and "
                        "the key type, returning a partial record — not every key has a group.",
                        'function groupBy<T, K extends PropertyKey>(xs: readonly T[], key: (x: T) => K): Partial<Record<K, T[]>> {\n'
                        '  const out: Partial<Record<K, T[]>> = {};\n'
                        '  for (const x of xs) {\n'
                        '    const k = key(x);\n'
                        '    (out[k] ??= []).push(x);\n  }\n'
                        '  return out;\n}\n'
                        'const byLen = groupBy(["a", "bb", "cc", "d"], (w) => w.length);\n'
                        'console.log(`${byLen[1]?.join(",")} | ${byLen[2]?.join(",")}`);\n',
                        'function groupBy<T, K extends PropertyKey>(xs: readonly T[], key: (x: T) => K): Partial<Record<K, T[]>> {',
                        'type _1 = Expect<Equal<typeof byLen, Partial<Record<number, string[]>>>>;\n'
                        'const _byKind = groupBy([{ k: "a" as const }], (x) => x.k);\n'
                        'type _2 = Expect<Equal<typeof _byKind, Partial<Record<"a", { k: "a" }[]>>>>;\n',
                        [("", "a,d | bb,cc")],
                        hints=["Two type parameters: the element T and the key K.",
                               "K must be usable as an object key: PropertyKey.",
                               "The return type is Partial<Record<K, T[]>>."],
                        difficulty="Hard"),
                _types("tscourse-w32-ts-t1", "Keys by value type",
                       "A classic warm-up question: write `KeysOfType<T, V>`, the union of T's keys whose values are assignable to V.",
                       'type KeysOfType<T, V> = { [K in keyof T]-?: T[K] extends V ? K : never }[keyof T];\n',
                       '{ [K in keyof T]-?: T[K] extends V ? K : never }[keyof T]',
                       """
interface User { id: number; name: string; email: string; age: number; admin: boolean }
type _1 = Expect<Equal<KeysOfType<User, string>, "name" | "email">>;
type _2 = Expect<Equal<KeysOfType<User, number>, "id" | "age">>;
type _3 = Expect<Equal<KeysOfType<User, Date>, never>>;
""",
                       hints=["Map each key to itself or never, then index by all keys (week 31's RequiredKeys shape).",
                              "{ [K in keyof T]-?: T[K] extends V ? K : never }[keyof T]"],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Why is `default: return 0;` worse than `default: return assertNever(s);`?",
                   ["it is not", "a new union member silently gets 0 instead of a compile error", "speed", "style"], 1,
                   "Fail loudly, at compile time."),
                _q("`JSON.parse` returns `any`. The honest move is…",
                   ["keep any", "type the result as unknown and narrow", "cast to the expected type", "ignore it"], 1,
                   "Week 15."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w32-last", "The last problems",
            "Clean types in an interview answer, and one hard problem to finish.",
            """
## Types are part of the answer

In a TypeScript interview, an answer typed with `any` is a worse answer, even when it
runs. The first exercise here is an interview solution that works and says nothing —
retype it, so its signature tells the reader exactly what it takes and returns.

## One hard problem

**Trapping rain water**: bars of given heights; how much water collects between them?
The water above each bar is `min(highest to its left, highest to its right) − its
height`. The brute force computes both maxima for every bar — O(n²). Two prefix
passes make it O(n) with O(n) space; **two pointers** make it O(n) with O(1): move
the side with the lower maximum, because that side's water level is already decided.

It combines week 22's two ends with week 23's running maxima, and it is a fair
example of what "Hard" means in an interview: nothing new, several old things at
once.

## After this week

The course ends here. What keeps the material alive is **spaced repetition**: redo a
problem from each round in a week, then a month. The Problem Library holds hundreds
more, filterable by the same patterns this course taught.
""",
            warmup=[
                _q("Water above a bar is…",
                   ["its height", "min(max left, max right) minus its height", "max left", "the average"], 1,
                   "Limited by the lower wall."),
                _q("Trapping rain water with two pointers moves…",
                   ["the higher side", "the side with the lower running maximum", "both", "the middle"], 1,
                   "Its level is already decided."),
                _q("An interview answer typed with `any`…",
                   ["is fine if it runs", "is a weaker answer in a TypeScript interview", "is required", "is faster"], 1,
                   "Types are part of the answer."),
                _q("Keeping the material alive after the course needs…",
                   ["nothing", "redoing problems at spaced intervals", "rereading the lessons", "memorising"], 1,
                   "Spaced repetition."),
            ],
            exercises=[
                _retype("tscourse-w32-ls-r1", "Type the interview answer",
                        "This two-sum works and its types say nothing. Give it an honest signature: it takes a "
                        "read-only array of numbers and a number target, and returns a tuple of two indices or "
                        "`null`. Every `any` must go.",
                        'function twoSum(nums: any, target: any): any {\n'
                        '  const at = new Map();\n'
                        '  for (let j = 0; j < nums.length; j = j + 1) {\n'
                        '    const i = at.get(target - nums[j]);\n'
                        '    if (i !== undefined) {\n'
                        '      return [i, j];\n    }\n'
                        '    at.set(nums[j], j);\n  }\n'
                        '  return null;\n}\n'
                        'console.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));\n',
                        'function twoSum(nums: readonly number[], target: number): [number, number] | null {\n'
                        '  const at = new Map<number, number>();\n'
                        '  for (let j = 0; j < nums.length; j = j + 1) {\n'
                        '    const x = nums[j] ?? 0;\n'
                        '    const i = at.get(target - x);\n'
                        '    if (i !== undefined) {\n'
                        '      return [i, j];\n    }\n'
                        '    at.set(x, j);\n  }\n'
                        '  return null;\n}\n'
                        'console.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));\n',
                        'type _1 = Expect<Equal<ReturnType<typeof twoSum>, [number, number] | null>>;\n'
                        'type _2 = Expect<Equal<Parameters<typeof twoSum>, [nums: readonly number[], target: number]>>;\n',
                        [("", "[0,1]")],
                        hints=["Parameters: readonly number[] and number.",
                               "The Map needs its own type arguments, or it is Map<any, any>.",
                               "Under this course's strictness nums[j] is number | undefined — take it into a const with ?? 0."],
                        difficulty="Medium"),
                _fn("tscourse-w32-ls-1", "Trapping rain water ⏱ 30 min",
                    "Bars have the given heights, each one unit wide. Return how many units of water are trapped "
                    "after rain. O(n) time, O(1) extra space.",
                    "trap", [("heights", "number[]")], "number",
                    'let lo = 0;\n'
                    'let hi = heights.length - 1;\n'
                    'let leftMax = 0;\n'
                    'let rightMax = 0;\n'
                    'let water = 0;\n'
                    'while (lo < hi) {\n'
                    '  const a = heights[lo] ?? 0;\n'
                    '  const b = heights[hi] ?? 0;\n'
                    '  if (a < b) {\n'
                    '    leftMax = Math.max(leftMax, a);\n'
                    '    water = water + (leftMax - a);\n'
                    '    lo = lo + 1;\n'
                    '  } else {\n'
                    '    rightMax = Math.max(rightMax, b);\n'
                    '    water = water + (rightMax - b);\n'
                    '    hi = hi - 1;\n  }\n}\n'
                    'return water;\n',
                    [("0 1 0 2 1 0 1 3 2 1 2 1", "6"), ("4 2 0 3 2 5", "9"), ("1 2 3", "0"), ("5", "0")],
                    hints=["Water over a bar = min(highest left, highest right) − its height.",
                           "Two pointers: whichever side is lower, its running maximum already decides its water.",
                           "Move that side inward, adding (running max − height)."],
                    difficulty="Hard"),
            ],
            quiz=[
                _q("Why does the two-pointer version move the LOWER side?",
                   ["style", "the lower side's water level is already bounded by its own running max", "speed", "it is arbitrary"], 1,
                   "The other side is at least as high."),
                _q("\"Hard\" in an interview usually means…",
                   ["a new algorithm", "several familiar techniques at once", "a trick", "a proof"], 1,
                   "Nothing new; more at once."),
            ],
        ),
    ],
    capstone=_cap_brief(
        "The full mock",
        """
Run a complete mock interview on yourself. Nothing here is judged — the point is the
whole loop, including the talking — so it is scored against the checklist below,
honestly.

**Set up (5 minutes)**

* Pick **three** problems you have *not* solved this week: one from rounds 1-2, one
  from rounds 3-4, and one TypeScript question from round 5 or weeks 29-31. The
  Problem Library filtered by pattern is a good source.
* Open a blank editor, a timer, and something to talk to — a friend, a recording, or
  a rubber duck. Speaking is the skill being practised.

**Run it (90 minutes, timer on)**

* ~35 minutes per algorithm problem, ~20 for the TypeScript question.
* For every problem, follow the seven steps **aloud**: clarify, examples, brute force
  with its cost, optimise, code, walk the examples through, complexity.
* When stuck for three minutes, say what you are stuck on and write the brute force.

**Review (15 minutes)**

* Score each checklist item 0, 1 or 2, per problem.
* Write one sentence on what to practise before the next mock.
* Run the code against your own examples and one edge case — did your hand walkthrough
  catch what the run catches?

**Afterwards:** a mock is most useful the second time. Book the next one a week out,
with three new problems, and compare the scores.
""",
        reference='// What a strong answer sounds like, written down, for round 1\'s longestConsecutive.\n'
                  '//\n'
                  '// 1. Clarify: "Can nums be empty? (Then 0.) Duplicates? (Count once.) Negative values? (Fine.)\n'
                  '//    Is O(n log n) acceptable, or do you want O(n)?" — the prompt said O(n).\n'
                  '// 2. Examples: [100, 4, 200, 1, 3, 2] -> 4 (1-2-3-4). Edge: [] -> 0. [5] -> 1.\n'
                  '// 3. Brute force: sort, then scan for runs. O(n log n) time — correct, and my floor.\n'
                  '// 4. Optimise: "Consecutive" and "seen before" — a Set (week 19). Count a run only from its\n'
                  '//    START (x - 1 absent), so each run is walked once: O(n).\n'
                  '// 5. Code:\n'
                  'function longestConsecutive(nums: readonly number[]): number {\n'
                  '  const set = new Set(nums);\n'
                  '  let best = 0;\n'
                  '  for (const x of set) {\n'
                  '    if (set.has(x - 1)) {\n'
                  '      continue;              // not the start of a run\n    }\n'
                  '    let len = 1;\n'
                  '    while (set.has(x + len)) {\n'
                  '      len = len + 1;\n    }\n'
                  '    best = Math.max(best, len);\n  }\n'
                  '  return best;\n}\n'
                  '// 6. Walkthrough: 100 starts a run of 1; 4 is skipped (3 present); 1 starts 1,2,3,4 -> 4. [] -> 0.\n'
                  '// 7. Complexity: O(n) time — every value is visited at most twice, once by the outer loop and\n'
                  '//    at most once by some while loop. O(n) space for the Set.\n'
                  'console.log(longestConsecutive([100, 4, 200, 1, 3, 2]));\n',
        rubric=["clarified size, duplicates, empty input and ties before writing code",
                "wrote an ordinary example and an edge case, with answers, first",
                "stated a brute force and its cost before optimising",
                "named the pattern and the week it came from",
                "wrote clean, typed code — no any",
                "walked the examples through the code by hand before calling it done",
                "stated time and space complexity, and what dominates",
                "said out loud when stuck, and kept moving",
                "finished within the time box — or knew exactly how far off it was"],
        stretch=_fn("tscourse-w32-capstone-stretch", "The full mock (stretch) ⏱ 35 min",
                    "One more judged problem to end on. Return the median of two SORTED arrays, as a number "
                    "(the average of the two middle values when the total length is even). An O(m + n) merge is "
                    "an acceptable answer — say that O(log(min(m, n))) exists, and why you chose not to write it "
                    "under time.",
                    "medianOfTwo", [("a", "number[]"), ("b", "number[]")], "number",
                    'const merged: number[] = [];\n'
                    'let i = 0;\n'
                    'let j = 0;\n'
                    'while (i < a.length || j < b.length) {\n'
                    '  const x = a[i];\n'
                    '  const y = b[j];\n'
                    '  if (y === undefined || (x !== undefined && x <= y)) {\n'
                    '    merged.push(x ?? 0);\n'
                    '    i = i + 1;\n'
                    '  } else {\n'
                    '    merged.push(y);\n'
                    '    j = j + 1;\n  }\n}\n'
                    'const n = merged.length;\n'
                    'if (n === 0) {\n'
                    '  return 0;\n}\n'
                    'const mid = Math.floor(n / 2);\n'
                    'return n % 2 === 1 ? merged[mid] ?? 0 : ((merged[mid - 1] ?? 0) + (merged[mid] ?? 0)) / 2;\n',
                    [("1 3\n2", "2"), ("1 2\n3 4", "2.5"), ("1 5 9\n2 3", "3"), ("7\n1", "4")],
                    hints=["Week 22's merge, then week 24's median.",
                           "Take from a while b is exhausted or a's front is no larger.",
                           "Odd total: the middle. Even: the average of the two middles."],
                    difficulty="Hard"),
    ),
))
