# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 26 — dynamic programming.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# WHERE THIS WEEK STARTS: exactly where week 25 stopped. Stair-climbing for 20
# stairs is 21,891 calls naively and 39 memoised; week 21 printed fib's 15 / 177 /
# 1973 calls and promised "week 26 fixes exactly this". So lesson 1 is that fix,
# generalised: the memo key must be the WHOLE state, and a two-parameter state is
# keyed with week 19's canonical-key trick (`${r},${c}`).
#
# The month-6 counting idiom continues: memoised calls and table cells are counted,
# so "DP is polynomial" is a number beside the exponential one.
#
# ---------------------------------------------------------------------------
# THREE TYPESCRIPT FACTS, all verified against the checker and the runner:
#
#   1. `new Array(n).fill(0)` is `any[]`. Every DP table in every tutorial is
#      built that way, and the checker then accepts `dp[0] = "oops"`. Shipped as
#      a `_predict` whose answer is `any[]`, with `new Array<number>(n)` as the
#      cure — the kind of thing only a TypeScript course would teach.
#   2. `memo.has(n)` does NOT narrow `memo.get(n)`: returning it is TS2322
#      ('number | undefined' is not assignable to 'number'). The fix is the
#      get-then-compare-to-undefined idiom week 19 already taught.
#   3. `new Array(r).fill(new Array(c).fill(0))` puts the SAME row in every slot
#      (week 13's aliasing): writing one cell writes a whole column. A 2-D table is
#      built with `Array.from({ length: r }, () => …)` so each row is new.
#
# ---------------------------------------------------------------------------
# One correctness pair carries lesson 3: counting coin COMBINATIONS needs the coin
# loop outside the amount loop; swapping them counts ORDERED sequences instead
# (4 against 9 for amount 5 with coins 1, 2, 5). Both run, both look plausible,
# and only the loop order differs — so it ships as a `fix`. Lesson 6 has the same
# shape for 0/1 knapsack: iterating capacity FORWARDS reuses an item.
# ---------------------------------------------------------------------------

# 2-D table helpers. Every grid and two-sequence exercise uses them, so index
# safety under noUncheckedIndexedAccess is paid once rather than in every cell.
_GRID = (
    'function makeGrid(rows: number, cols: number): number[][] {\n'
    '  return Array.from({ length: rows }, () => new Array<number>(cols).fill(0));\n}\n'
    'function at(g: readonly (readonly number[])[], r: number, c: number): number {\n'
    '  return g[r]?.[c] ?? 0;\n}\n'
    'function put(g: number[][], r: number, c: number, v: number): void {\n'
    '  const row = g[r];\n'
    '  if (row !== undefined) {\n'
    '    row[c] = v;\n  }\n}\n'
)

# Two input lines, for the two-sequence lessons.
_TWO = (
    _FS +
    'const lines = fs.readFileSync(0, "utf8").split("\\n");\n'
    'const a = (lines[0] ?? "").trim();\n'
    'const b = (lines[1] ?? "").trim();\n'
)

_GRIDLINES = (
    _FS +
    'const rows: readonly (readonly number[])[] = fs.readFileSync(0, "utf8")\n'
    '  .trim()\n'
    '  .split("\\n")\n'
    '  .map((l) => l.trim().split(/\\s+/).map(Number));\n'
    'const R = rows.length;\n'
    'const C = rows[0]?.length ?? 0;\n'
)


# --- Week 26 --------------------------------------------------------------
_WEEKS.append(_week(
    26, 7, _M7,
    "Dynamic Programming",
    "When the same subproblem keeps coming back, solve it once. Memoise the recursion, then fill the table directly — and learn to find the state, which is the whole difficulty.",
    """
Week 21 counted `fib(15)`: **1,973 calls**. Week 25 counted stair-climbing for 20
stairs: **21,891 calls** — and then, with a `Map` remembering each answer, **39**.

That `Map` is this week.

## The idea in one sentence

**If a recursion solves the same subproblem more than once, solve each one once
and remember it.** That is dynamic programming. The name is historical and
unhelpful; "remembered recursion" is the whole of it.

## Two ways to write it

* **Top-down (memoisation)** — write the recursion, add a cache. The recursion
  decides which subproblems are needed.
* **Bottom-up (tabulation)** — work out the order the subproblems depend on each
  other, and fill a table in that order with a loop. No recursion, no depth limit
  (week 25), and often less memory.

Same answers, same complexity. Top-down is easier to get right; bottom-up is
usually what the finished solution looks like.

## The hard part is not the code

Every DP solution is twenty lines. The difficulty is **the state**: what, exactly,
does a subproblem need to know? Get the state right and the code writes itself; get
it wrong and no amount of code helps. Lesson 3 is a recipe for finding it, and every
lesson after it is that recipe applied.

## Where it applies

Two conditions, and a question needs both:

1. **Overlapping subproblems** — the same smaller question recurs. (Merge sort's
   halves never overlap, which is why it is divide-and-conquer and not DP.)
2. **Optimal substructure** — the best answer is built from best answers to the
   smaller questions.

"How many ways", "the fewest", "the longest", "can it be done" — over sequences,
grids, amounts and budgets. That covers a remarkable share of interview questions.

⏱️ Budget about **nine hours** — the longest week of the month, because the
recipe only sticks with repetition.
""",
    objectives=[
        "Say what makes a problem a DP problem: overlapping subproblems and optimal substructure",
        "Memoise a recursion, keying the cache on the whole state",
        "Read a Map entry without assuming `has` narrowed `get`",
        "Fill a table bottom-up in dependency order",
        "Reduce a table to a couple of rolling variables when only the last rows are needed",
        "Define a state, a transition, a base case and where the answer lives",
        "Count coin combinations and coin sequences, and say which loop order gives which",
        "Build a 2-D table without aliasing its rows, and type it as number[][]",
        "Solve grid-path and minimum-path problems with a table",
        "Compute the longest common subsequence and the edit distance of two strings",
        "Reconstruct the answer itself, not just its size, by walking the table back",
        "Solve 0/1 knapsack, and say why the 1-D version iterates capacity backwards",
        "Show a greedy answer failing where DP succeeds",
    ],
    why="DP questions are the ones candidates fear most and the ones that most reward a method. Once you can name the state and the transition, 'coin change', 'edit distance', 'knapsack' and 'longest increasing subsequence' stop being four memorised tricks and become one idea applied four times. It is also the clearest demonstration in the course that an exponential algorithm and a polynomial one can compute the same answer.",
    est_minutes=540,
    glossary=[
        _gloss("dynamic programming", "Solve each overlapping subproblem once and reuse the answer."),
        _gloss("overlapping subproblems", "The same smaller question recurs many times in the naive recursion."),
        _gloss("optimal substructure", "The best answer is built from best answers to smaller questions."),
        _gloss("memoisation", "Top-down: the recursion, plus a cache consulted before computing."),
        _gloss("tabulation", "Bottom-up: fill a table in dependency order with a loop."),
        _gloss("state", "Everything a subproblem needs to know. The memo key; the table's indices."),
        _gloss("transition", "How a state's answer is built from smaller states' answers."),
        _gloss("base case", "The states answered directly, which the table is seeded with."),
        _gloss("rolling array", "Keep only the last row(s) of a table when nothing older is read."),
        _gloss("reconstruction", "Walk the table back from the answer to recover WHICH choices produced it."),
        _gloss("LCS", "Longest common subsequence: the longest sequence both strings contain in order."),
        _gloss("edit distance", "The fewest single-character inserts, deletes and substitutions turning a into b."),
        _gloss("0/1 knapsack", "Each item taken at most once, within a weight budget, maximising value."),
        _gloss("unbounded", "Each item (or coin) may be used any number of times."),
        _gloss("greedy", "Take the locally best choice every time. Sometimes optimal, often not — DP never guesses."),
        _gloss("pseudo-polynomial", "Polynomial in the NUMERIC value of the budget, e.g. O(n × capacity)."),
    ],
    cheatsheet="""
```ts
// ---- top-down: the recursion, plus a cache --------------------------------
const memo = new Map<string, number>();
function paths(r: number, c: number): number {
  if (r === 0 || c === 0) { return 1; }
  const key = `${r},${c}`;                      // the WHOLE state (week 19's key trick)
  const known = memo.get(key);
  if (known !== undefined) { return known; }      // has() does NOT narrow get(): TS2322
  const result = paths(r - 1, c) + paths(r, c - 1);
  memo.set(key, result);
  return result;
}

// ---- bottom-up: a table, filled in dependency order -----------------------
const dp: number[] = [0, 1];                     // base cases
for (let i = 2; i <= n; i = i + 1) {
  dp.push((dp[i - 1] ?? 0) + (dp[i - 2] ?? 0));   // only reads what is already filled
}
// rolling: if only the last two are read, keep only two variables

// ---- tables that are typed ----------------------------------------------
new Array(n).fill(0);                            // any[]   ⚠️ accepts "oops"
new Array<number>(n).fill(0);                    // number[]
Array.from({ length: r }, () => new Array<number>(c).fill(0));   // r DIFFERENT rows
new Array(r).fill(new Array(c).fill(0));         // ⚠️ ONE row, r times

// ---- coins ---------------------------------------------------------------
// fewest:        dp[a] = min over coins of dp[a - coin] + 1
// combinations:  for (coin) { for (a = coin..amount) ways[a] += ways[a - coin] }
// sequences:     for (a) { for (coin) ways[a] += ways[a - coin] }      ← loop order!

// ---- two strings: an (m+1) × (n+1) table, row/column 0 is the empty prefix -
// LCS:   a[i-1] === b[j-1] ? dp[i-1][j-1] + 1 : max(dp[i-1][j], dp[i][j-1])
// edit:  a[i-1] === b[j-1] ? dp[i-1][j-1]     : 1 + min(sub, delete, insert)

// ---- 0/1 knapsack in one row: capacity BACKWARDS -------------------------
for (const item of items) {
  for (let cap = budget; cap >= item.w; cap = cap - 1) {
    best[cap] = Math.max(best[cap] ?? 0, (best[cap - item.w] ?? 0) + item.v);
  }
}
// forwards reuses the item — which is exactly right for the UNBOUNDED version
```

**The recipe:** state → transition → base case → order → where the answer is.
""",
    self_check=[
        "Can you name the two conditions that make a problem suitable for DP?",
        "Can you memoise a recursion with two parameters, and say what the key must contain?",
        "Can you explain why `if (memo.has(n)) return memo.get(n);` does not compile?",
        "Can you rewrite a memoised recursion as a loop over a table?",
        "Can you say when a table can shrink to two variables?",
        "Can you state a DP's state, transition, base case and answer location before coding it?",
        "Can you say which loop order counts coin combinations and which counts sequences?",
        "Can you say what type `new Array(n).fill(0)` has, and how to fix it?",
        "Can you build a 2-D table whose rows are really separate?",
        "Can you fill the LCS table and read the answer from its corner?",
        "Can you recover the LCS string itself?",
        "Can you compute an edit distance?",
        "Can you say why 0/1 knapsack in one row goes backwards?",
        "Can you give an input where greedy coin change fails?",
    ],
    review=[
        _q("Dynamic programming needs…",
           ["recursion", "overlapping subproblems and optimal substructure", "a sorted input", "a Map"], 1,
           "Both, or it is something else."),
        _q("Merge sort is not DP because…",
           ["it is fast", "its subproblems never overlap", "it is recursive", "it sorts"], 1,
           "Divide-and-conquer on disjoint halves."),
        _q("A memo key must include…",
           ["the first parameter", "everything the answer depends on — the whole state", "the result",
            "the call count"], 1,
           "Leave part out and different questions share an answer."),
        _q("`if (memo.has(n)) { return memo.get(n); }` in a function returning number is…",
           ["fine", "TS2322 — has() does not narrow get()", "TS2532", "a runtime error"], 1,
           "Get, then compare against undefined."),
        _q("Bottom-up DP fills the table…",
           ["in any order", "so every entry's dependencies are filled before it", "backwards always",
            "randomly"], 1,
           "The dependency order."),
        _q("`new Array(5).fill(0)` has the type…",
           ["number[]", "any[]", "0[]", "unknown[]"], 1,
           "Write new Array<number>(5)."),
        _q("`new Array(3).fill(new Array(3).fill(0))` makes…",
           ["a 3×3 grid", "three references to ONE row", "an error", "nine arrays"], 1,
           "Use Array.from with a function."),
        _q("Counting coin COMBINATIONS puts which loop outside?",
           ["the amount", "the coins", "either", "neither"], 1,
           "Amount outside counts ordered sequences."),
        _q("The LCS table for strings of length m and n is…",
           ["m × n", "(m+1) × (n+1)", "m + n", "n²"], 1,
           "Row and column 0 are the empty prefix — a sentinel."),
        _q("Edit distance when a[i-1] === b[j-1] is…",
           ["dp[i-1][j-1] + 1", "dp[i-1][j-1]", "0", "dp[i][j-1]"], 1,
           "Matching characters cost nothing."),
        _q("0/1 knapsack in a single row iterates capacity…",
           ["forwards", "backwards, so each item is counted once", "twice", "from the middle"], 1,
           "Forwards is the unbounded version."),
        _q("Greedy coin change with coins 1, 3, 4 for amount 6 gives…",
           ["2 coins", "3 coins (4+1+1), where 3+3 is 2", "1 coin", "no answer"], 1,
           "DP never commits to a choice it has not compared."),
        _q("Knapsack's O(n × capacity) is called pseudo-polynomial because…",
           ["it is slow", "it grows with the budget's VALUE, not its size in digits", "it is recursive",
            "it is approximate"], 1,
           "A billion-unit budget is a billion columns."),
        _q("DP can recover WHICH choices were made by…",
           ["storing everything", "walking the table back from the answer", "rerunning", "a heap"], 1,
           "Reconstruction."),
    ],
    milestone="Interview rep #26 — the coin report. For one set of coins and one amount: the fewest coins and which ones, what greedy would have chosen instead (and whether it even reaches the amount), and how many distinct combinations exist. Three DP questions over the same table, and one input where greedy is wrong and DP is right, printed side by side.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w26-memo", "Remembered recursion",
            "Week 25's Map, generalised: the key is the whole state.",
            """
Week 25 ended here:

```ts
const memo = new Map<number, number>();
function ways(n: number): number {
  if (n <= 1) { return 1; }
  const known = memo.get(n);
  if (known !== undefined) { return known; }        // asked before: answer at once
  const result = ways(n - 1) + ways(n - 2);
  memo.set(n, result);                               // first time: remember it
  return result;
}
```

21,891 calls became 39. Each `n` from 2 to 20 is now *computed* once; every
other call is a Map lookup. Exponential became linear, and the only change was
two lines around the recursion.

## `has` does not narrow `get`

The obvious way to write the lookup does not compile:

```ts
if (memo.has(n)) { return memo.get(n); }
```

```
TS2322: Type 'number | undefined' is not assignable to type 'number'.
```

`has` returning true tells *you* the key exists; it tells the type checker
nothing, because `get` is a separate call that could in principle see a different
Map. Week 19's idiom — `get`, then compare to `undefined` — is one lookup instead of
two, and it narrows.

## The key is the whole state

Count the paths from the top-left of a grid to cell `(r, c)`, moving only right or
down. Two numbers decide the answer, so both go in the key — as a string, week 19's
canonical-key trick, because two arrays `[r, c]` would be two different Map keys:

```ts
const key = `${r},${c}`;
```

Key on `r` alone and `paths(2, 1)` and `paths(2, 5)` share one cached answer.
Nothing crashes. The numbers are simply wrong, and there is no clue why — which is
the single commonest memoisation bug.

## Counting the saving

`fib(40)` naively makes over 300 million calls. Memoised: **79**. Week 21's
exponential row and linear row, for the same function, separated by a Map.

> ⚠️ **Common mistakes:** a key that omits part of the state; `has` then `get`;
> and memoising a function whose answer depends on something outside its
> parameters.
""",
            warmup=[
                _q("Memoisation turns naive fib from…",
                   ["O(n) to O(1)", "O(2ⁿ) to O(n)", "O(n²) to O(n)", "O(log n) to O(1)"], 1,
                   "Each n computed once."),
                _q("`memo.has(n)` followed by `return memo.get(n)`…",
                   ["compiles", "is TS2322 — get still returns number | undefined", "throws", "loops"], 1,
                   "has() does not narrow."),
                _q("For a two-parameter recursion, the memo key is…",
                   ["the first parameter", "both, e.g. `${r},${c}`", "an array [r, c]", "the result"], 1,
                   "An array would be a new key every time."),
                _q("A key that omits part of the state gives…",
                   ["a crash", "wrong answers, silently", "slower code", "a type error"], 1,
                   "Different questions share one answer."),
            ],
            exercises=[
                _ex("tscourse-w26-mm-1", "Remember it the first time",
                    "Store each answer before returning it, and count the calls.",
                    _LINE +
                    'const memo = new Map<number, number>();\n'
                    'let calls = 0;\n'
                    'function fib(n: number): number {\n'
                    '  calls = calls + 1;\n'
                    '  if (n < 2) {\n'
                    '    return n;\n  }\n'
                    '  const known = memo.get(n);\n'
                    '  if (known !== undefined) {\n'
                    '    return known;\n  }\n'
                    '  const result = fib(n - 1) + fib(n - 2);\n'
                    '  memo.set(n, result);\n'
                    '  return result;\n}\n'
                    'const n = Number(line);\n'
                    'console.log(`fib(${n})=${fib(n)} calls=${calls}`);\n',
                    '  memo.set(n, result);',
                    [("40", "fib(40)=102334155 calls=79"), ("10", "fib(10)=55 calls=19")],
                    hints=["Without storing it, the next request recomputes the whole subtree.",
                           "Write memo.set(n, result);"],
                    difficulty="Easy"),
                _diagnose("tscourse-w26-mm-d1", "has() is not a guard",
                          "TS2322: Type 'number | undefined' is not assignable to type 'number'.",
                          _LINE +
                          'const memo = new Map<number, number>();\n'
                          'function fib(n: number): number {\n'
                          '  if (n < 2) {\n'
                          '    return n;\n  }\n'
                          '  if (memo.has(n)) {\n'
                          '    return memo.get(n);\n  }\n'
                          '  const result = fib(n - 1) + fib(n - 2);\n'
                          '  memo.set(n, result);\n'
                          '  return result;\n}\n'
                          'console.log(fib(Number(line)));\n',
                          _LINE +
                          'const memo = new Map<number, number>();\n'
                          'function fib(n: number): number {\n'
                          '  if (n < 2) {\n'
                          '    return n;\n  }\n'
                          '  const known = memo.get(n);\n'
                          '  if (known !== undefined) {\n'
                          '    return known;\n  }\n'
                          '  const result = fib(n - 1) + fib(n - 2);\n'
                          '  memo.set(n, result);\n'
                          '  return result;\n}\n'
                          'console.log(fib(Number(line)));\n',
                          [("10", "55"), ("30", "832040")],
                          hints=["`has` and `get` are two separate calls; the checker does not connect them.",
                                 "Read once with get, and test THAT value.",
                                 "const known = memo.get(n); if (known !== undefined) { return known; }"],
                          difficulty="Easy"),
                _ex("tscourse-w26-mm-2", "Key on the whole state",
                    "Count grid paths with a memo keyed on both coordinates.",
                    _NUMS +
                    'const memo = new Map<string, number>();\n'
                    'function paths(r: number, c: number): number {\n'
                    '  if (r === 0 || c === 0) {\n'
                    '    return 1;\n  }\n'
                    '  const key = `${r},${c}`;\n'
                    '  const known = memo.get(key);\n'
                    '  if (known !== undefined) {\n'
                    '    return known;\n  }\n'
                    '  const result = paths(r - 1, c) + paths(r, c - 1);\n'
                    '  memo.set(key, result);\n'
                    '  return result;\n}\n'
                    'console.log(paths((nums[0] ?? 1) - 1, (nums[1] ?? 1) - 1));\n',
                    '  const key = `${r},${c}`;',
                    [("3 3", "6"), ("10 10", "48620"), ("1 5", "1")],
                    hints=["Both coordinates decide the answer, so both belong in the key.",
                           "A string, because two arrays with the same contents are different Map keys.",
                           "Write const key = `${r},${c}`;"],
                    difficulty="Medium"),
                _ex("tscourse-w26-mm-3", "One, two or three steps",
                    "Count the ways to climb n stairs taking 1, 2 or 3 at a time.",
                    _LINE +
                    'const memo = new Map<number, number>();\n'
                    'function ways(n: number): number {\n'
                    '  if (n < 0) {\n'
                    '    return 0;\n  }\n'
                    '  if (n === 0) {\n'
                    '    return 1;\n  }\n'
                    '  const known = memo.get(n);\n'
                    '  if (known !== undefined) {\n'
                    '    return known;\n  }\n'
                    '  const result = ways(n - 1) + ways(n - 2) + ways(n - 3);\n'
                    '  memo.set(n, result);\n'
                    '  return result;\n}\n'
                    'console.log(ways(Number(line)));\n',
                    '  const result = ways(n - 1) + ways(n - 2) + ways(n - 3);',
                    [("4", "7"), ("10", "274"), ("1", "1")],
                    hints=["The last step was 1, 2 or 3 stairs — so add the ways to reach each of those points.",
                           "Write const result = ways(n - 1) + ways(n - 2) + ways(n - 3);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-mm-4", "The fewest coins, top-down",
                    "The fewest coins for an amount is one coin plus the fewest for what remains — for the best choice of coin.",
                    _LINE +
                    'const coins = [1, 3, 4];\n'
                    'const memo = new Map<number, number>();\n'
                    'function fewest(amount: number): number {\n'
                    '  if (amount === 0) {\n'
                    '    return 0;\n  }\n'
                    '  const known = memo.get(amount);\n'
                    '  if (known !== undefined) {\n'
                    '    return known;\n  }\n'
                    '  let best = Infinity;\n'
                    '  for (const c of coins) {\n'
                    '    if (c <= amount) {\n'
                    '      best = Math.min(best, 1 + fewest(amount - c));\n    }\n  }\n'
                    '  memo.set(amount, best);\n'
                    '  return best;\n}\n'
                    'console.log(fewest(Number(line)));\n',
                    '      best = Math.min(best, 1 + fewest(amount - c));',
                    [("6", "2"), ("7", "2"), ("0", "0")],
                    hints=["Try every coin that fits; each leaves a smaller amount to solve.",
                           "Write best = Math.min(best, 1 + fewest(amount - c));"],
                    difficulty="Medium"),
                _fix("tscourse-w26-mm-fix1", "Fix the key that forgot a coordinate",
                     "For a 3 × 3 grid this reports 7 paths; there are 6. The memo is keyed on `r` alone, so every cell in a row shares one cached answer — whichever column happened to be computed first.",
                     _NUMS +
                     'const memo = new Map<string, number>();\n'
                     'function paths(r: number, c: number): number {\n'
                     '  if (r === 0 || c === 0) {\n'
                     '    return 1;\n  }\n'
                     '  const key = `${r}`;\n'
                     '  const known = memo.get(key);\n'
                     '  if (known !== undefined) {\n'
                     '    return known;\n  }\n'
                     '  const result = paths(r - 1, c) + paths(r, c - 1);\n'
                     '  memo.set(key, result);\n'
                     '  return result;\n}\n'
                     'console.log(paths((nums[0] ?? 1) - 1, (nums[1] ?? 1) - 1));\n',
                     _NUMS +
                     'const memo = new Map<string, number>();\n'
                     'function paths(r: number, c: number): number {\n'
                     '  if (r === 0 || c === 0) {\n'
                     '    return 1;\n  }\n'
                     '  const key = `${r},${c}`;\n'
                     '  const known = memo.get(key);\n'
                     '  if (known !== undefined) {\n'
                     '    return known;\n  }\n'
                     '  const result = paths(r - 1, c) + paths(r, c - 1);\n'
                     '  memo.set(key, result);\n'
                     '  return result;\n}\n'
                     'console.log(paths((nums[0] ?? 1) - 1, (nums[1] ?? 1) - 1));\n',
                     [("3 3", "6"), ("3 7", "28")],
                     hints=["What does the answer depend on? What does the key contain?",
                            "Two different questions must never share a key.",
                            "Key on both: `${r},${c}`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is `${r},${c}` used instead of `[r, c]` as a Map key?",
                   ["it is shorter", "two arrays with equal contents are different keys", "arrays are slow",
                    "types"], 1,
                   "Week 19: SameValueZero."),
                _q("Memoised `fib(40)` makes 79 calls because…",
                   ["luck", "each n from 2 to 40 is computed once, and makes two calls", "40 × 2", "it is cached globally"], 1,
                   "1 + 2 × 39."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w26-table", "Filling the table",
            "Bottom-up: no recursion, no depth limit, and often less memory.",
            """
The memoised recursion asks for `fib(40)`, which asks for 39 and 38, and so on down
to the base cases, then fills the cache on the way back up. **Bottom-up skips the
asking** and fills the cache directly, smallest first:

```ts
const dp: number[] = [0, 1];                           // the base cases
for (let i = 2; i <= n; i = i + 1) {
  dp.push((dp[i - 1] ?? 0) + (dp[i - 2] ?? 0));
}
// dp[n] is the answer
```

## The order is the whole trick

Each entry reads entries that must **already be filled**. For `fib` that is "the
two before me", so a loop going up works. Fill in the wrong order and the entries
you read are still zero: the loop runs, the program prints a number, and the
number is wrong. The dependency direction decides the loop direction — always
check it before writing the loop.

## Why bother, when memoisation works?

* **No recursion**, so no stack limit. `fib(100000)` recursively is week 25's
  `RangeError`; as a loop it is nothing.
* **Space can shrink.** `fib` only ever reads the last two entries, so the table can
  be two variables:

```ts
let prev = 0;
let cur = 1;
for (let i = 2; i <= n; i = i + 1) {
  const next = prev + cur;
  prev = cur;
  cur = next;
}
```

O(n) time, **O(1)** space. A "rolling" table: keep only what will be read again.

## House robber

"Houses in a row hold these amounts; rob any set of houses, never two
neighbours." The state is "the best total from the first i houses", and house i
is either robbed (then i − 1 was not) or skipped:

```ts
best[i] = Math.max(best[i - 1], best[i - 2] + x[i])
```

`[2, 7, 9, 3, 1]` → **12** (2 + 9 + 1). Also two rolling variables.

## Kadane is DP too

Week 23-style "largest sum of any contiguous run" with negatives allowed: the state
is "the best run **ending here**", and it either extends the previous one or starts
fresh: `endHere = Math.max(x, endHere + x)`. `[-2,1,-3,4,-1,2,1,-5,4]` → **6**. A
one-variable DP, and one of the most-asked interview questions there is.

> ⚠️ **Common mistakes:** filling in an order that reads unfilled entries;
> forgetting the base cases; and keeping a whole table when two variables would do.
""",
            warmup=[
                _q("Bottom-up DP avoids…",
                   ["loops", "recursion — and so the stack limit", "tables", "base cases"], 1,
                   "Week 25's RangeError cannot happen."),
                _q("Filling a table in the wrong order…",
                   ["throws", "reads unfilled entries and prints a wrong number", "is slower", "is a type error"], 1,
                   "Silent."),
                _q("fib's table can shrink to…",
                   ["n/2 entries", "two variables", "one variable", "nothing"], 1,
                   "It only reads the last two."),
                _q("Kadane's state is…",
                   ["the best run so far", "the best run ENDING at this element", "the total", "the max element"], 1,
                   "Extend it or start fresh."),
            ],
            exercises=[
                _ex("tscourse-w26-tb-1", "Fill it upwards",
                    "Each entry is the sum of the two before it.",
                    _LINE +
                    'const n = Number(line);\n'
                    'const dp: number[] = [0, 1];\n'
                    'for (let i = 2; i <= n; i = i + 1) {\n'
                    '  dp.push((dp[i - 1] ?? 0) + (dp[i - 2] ?? 0));\n}\n'
                    'console.log(dp[n] ?? 0);\n',
                    '  dp.push((dp[i - 1] ?? 0) + (dp[i - 2] ?? 0));',
                    [("10", "55"), ("50", "12586269025"), ("1", "1")],
                    hints=["dp[i] is dp[i - 1] + dp[i - 2], and both already exist when i is reached.",
                           "Write dp.push((dp[i - 1] ?? 0) + (dp[i - 2] ?? 0));"],
                    difficulty="Easy"),
                _ex("tscourse-w26-tb-2", "Two variables are enough",
                    "Roll the last two values forward instead of keeping the table.",
                    _LINE +
                    'const n = Number(line);\n'
                    'let prev = 0;\n'
                    'let cur = 1;\n'
                    'for (let i = 2; i <= n; i = i + 1) {\n'
                    '  const next = prev + cur;\n'
                    '  prev = cur;\n'
                    '  cur = next;\n}\n'
                    'console.log(n === 0 ? 0 : cur);\n',
                    '  const next = prev + cur;\n'
                    '  prev = cur;\n'
                    '  cur = next;',
                    [("10", "55"), ("50", "12586269025"), ("0", "0")],
                    hints=["Compute the next value, then shift both variables along by one.",
                           "Order matters: save `next` before overwriting `prev`."],
                    difficulty="Medium"),
                _ex("tscourse-w26-tb-3", "Never two neighbours",
                    "The best haul from the first i houses: skip house i, or rob it and skip i - 1.",
                    _NUMS +
                    'let skipLast = 0;\n'
                    'let best = 0;\n'
                    'for (const x of nums) {\n'
                    '  const next = Math.max(best, skipLast + x);\n'
                    '  skipLast = best;\n'
                    '  best = next;\n}\n'
                    'console.log(best);\n',
                    '  const next = Math.max(best, skipLast + x);',
                    [("2 7 9 3 1", "12"), ("1 2 3 1", "4"), ("5", "5")],
                    hints=["Either the best so far without this house, or this house plus the best that ended before its neighbour.",
                           "Write const next = Math.max(best, skipLast + x);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-tb-4", "Cheapest way up",
                    "Each step has a cost; you may climb one or two at a time and start on step 0 or 1.",
                    _NUMS +
                    'const dp: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cost = nums[i] ?? 0;\n'
                    '  dp.push(i < 2 ? cost : cost + Math.min(dp[i - 1] ?? 0, dp[i - 2] ?? 0));\n}\n'
                    'const n = dp.length;\n'
                    'console.log(Math.min(dp[n - 1] ?? 0, dp[n - 2] ?? 0));\n',
                    '  dp.push(i < 2 ? cost : cost + Math.min(dp[i - 1] ?? 0, dp[i - 2] ?? 0));',
                    [("10 15 20", "15"), ("1 100 1 1 1 100 1 1 100 1", "6")],
                    hints=["Reaching step i costs its own price plus the cheaper of the two steps below.",
                           "Steps 0 and 1 can be started on, so they cost only themselves."],
                    difficulty="Medium"),
                _ex("tscourse-w26-tb-5", "The best run ending here",
                    "Kadane: extend the previous run or start a new one at this element.",
                    _NUMS +
                    'let endHere = nums[0] ?? 0;\n'
                    'let best = endHere;\n'
                    'for (let i = 1; i < nums.length; i = i + 1) {\n'
                    '  const x = nums[i] ?? 0;\n'
                    '  endHere = Math.max(x, endHere + x);\n'
                    '  best = Math.max(best, endHere);\n}\n'
                    'console.log(best);\n',
                    '  endHere = Math.max(x, endHere + x);',
                    [("-2 1 -3 4 -1 2 1 -5 4", "6"), ("-3 -1 -2", "-1"), ("5 4 -1 7 8", "23")],
                    hints=["A run ending at x either includes the best run ending just before it, or is x alone.",
                           "Write endHere = Math.max(x, endHere + x);"],
                    difficulty="Medium"),
                _fix("tscourse-w26-tb-fix1", "Fix the table filled from the wrong end",
                     "This prints `0` for fib(10). The loop fills from the top down, so every entry reads two entries that are still zero — and the program has no way to notice.",
                     _LINE +
                     'const n = Number(line);\n'
                     'const dp: number[] = new Array<number>(n + 1).fill(0);\n'
                     'dp[1] = 1;\n'
                     'for (let i = n; i >= 2; i = i - 1) {\n'
                     '  dp[i] = (dp[i - 1] ?? 0) + (dp[i - 2] ?? 0);\n}\n'
                     'console.log(dp[n] ?? 0);\n',
                     _LINE +
                     'const n = Number(line);\n'
                     'const dp: number[] = new Array<number>(n + 1).fill(0);\n'
                     'dp[1] = 1;\n'
                     'for (let i = 2; i <= n; i = i + 1) {\n'
                     '  dp[i] = (dp[i - 1] ?? 0) + (dp[i - 2] ?? 0);\n}\n'
                     'console.log(dp[n] ?? 0);\n',
                     [("10", "55"), ("5", "5")],
                     hints=["Which entries does dp[i] read? Have they been filled when i is reached?",
                            "The dependencies point DOWN, so the loop must go UP.",
                            "for (let i = 2; i <= n; i = i + 1)"],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Memoisation or tabulation for fib(100000)?",
                   ["memoisation", "tabulation — the recursion would exhaust the stack", "either", "neither"], 1,
                   "Week 25."),
                _q("House robber needs how many rolling variables?",
                   ["one", "two", "n", "three"], 1,
                   "The best up to i-1, and up to i-2."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w26-state", "Finding the state",
            "The recipe: state, transition, base case, order, answer.",
            """
Every DP solution is written by answering five questions, in this order. Do it on
paper first; the code is transcription.

| | the question | coin change: fewest coins |
|---|---|---|
| **state** | what does a subproblem need to know? | the amount `a` still to make |
| **transition** | how is it built from smaller states? | `dp[a] = min over coins c ≤ a of dp[a − c] + 1` |
| **base case** | which states are answered directly? | `dp[0] = 0` |
| **order** | what must be filled first? | smaller amounts first |
| **answer** | where does it end up? | `dp[amount]` |

```ts
const dp: number[] = [0];
for (let a = 1; a <= amount; a = a + 1) {
  let best = Infinity;
  for (const c of coins) {
    if (c <= a) { best = Math.min(best, (dp[a - c] ?? Infinity) + 1); }
  }
  dp.push(best);
}
```

`Infinity` means "unreachable", and it composes: `Infinity + 1` is still
`Infinity`, and `Math.min` ignores it. Coins `[5, 3]` cannot make 7, and `dp[7]` is
`Infinity` — print `-1` for it at the end, not in the middle.

## The same table, a different question

"How many **combinations** of coins make the amount?" Same state, different
transition — add instead of min:

```ts
const ways: number[] = [1, 0, 0, …];          // one way to make 0: no coins
for (const c of coins) {                      // coins OUTSIDE
  for (let a = c; a <= amount; a = a + 1) {
    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);
  }
}
```

Amount 5, coins 1, 2, 5: **4** — `5`, `2+2+1`, `2+1+1+1`, `1+1+1+1+1`.

## The loop order is the meaning

Swap the two loops — amounts outside, coins inside — and it still runs, and prints
**9**. It is now counting **ordered sequences**: `1+2+2`, `2+1+2` and `2+2+1` are
three different answers. With coins outside, each coin's contribution is complete
before the next coin is considered, so a combination can only be built in one order.

Neither is wrong. They answer different questions, and the only difference in the
code is which `for` comes first. Read the question, then choose.

## A typing trap in every DP tutorial

```ts
const dp = new Array(n + 1).fill(0);
```

That is **`any[]`**. `new Array(n)` has no idea what it will hold, `fill` does not
change its mind, and the checker will now accept `dp[0] = "oops"`. Write
`new Array<number>(n + 1).fill(0)` — or annotate the variable — and the table is
typed again.

> ⚠️ **Common mistakes:** coding before the state is written down; the loop order
> for combinations versus sequences; and `new Array(n).fill(0)` untyped.
""",
            warmup=[
                _q("The five questions are…",
                   ["input, output, loop, test, print", "state, transition, base case, order, answer",
                    "memo, key, get, set, return", "sort, search, sweep, stop, print"], 1,
                   "In that order."),
                _q("`Infinity` works as 'unreachable' because…",
                   ["it is big", "Infinity + 1 is Infinity, and min ignores it", "it is falsy", "it is a type"], 1,
                   "It composes."),
                _q("With the COIN loop outside, the table counts…",
                   ["sequences", "combinations", "coins", "amounts"], 1,
                   "Each combination built in one order."),
                _q("`new Array(5).fill(0)` is typed…",
                   ["number[]", "any[]", "0[]", "never[]"], 1,
                   "Add the type argument."),
            ],
            exercises=[
                _ex("tscourse-w26-st-1", "The fewest coins, bottom-up",
                    "For each amount, try every coin that fits and keep the best.",
                    _LINE +
                    'const coins = [1, 3, 4];\n'
                    'const amount = Number(line);\n'
                    'const dp: number[] = [0];\n'
                    'for (let a = 1; a <= amount; a = a + 1) {\n'
                    '  let best = Infinity;\n'
                    '  for (const c of coins) {\n'
                    '    if (c <= a) {\n'
                    '      best = Math.min(best, (dp[a - c] ?? Infinity) + 1);\n    }\n  }\n'
                    '  dp.push(best);\n}\n'
                    'console.log(dp[amount] ?? 0);\n',
                    '      best = Math.min(best, (dp[a - c] ?? Infinity) + 1);',
                    [("6", "2"), ("7", "2"), ("0", "0")],
                    hints=["Using coin c leaves a - c, whose answer is already in the table.",
                           "Write best = Math.min(best, (dp[a - c] ?? Infinity) + 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-st-2", "When the amount cannot be made",
                    "Report -1 for an unreachable amount — at the end, not in the middle.",
                    _LINE +
                    'const coins = [5, 3];\n'
                    'const amount = Number(line);\n'
                    'const dp: number[] = [0];\n'
                    'for (let a = 1; a <= amount; a = a + 1) {\n'
                    '  let best = Infinity;\n'
                    '  for (const c of coins) {\n'
                    '    if (c <= a) {\n'
                    '      best = Math.min(best, (dp[a - c] ?? Infinity) + 1);\n    }\n  }\n'
                    '  dp.push(best);\n}\n'
                    'const answer = dp[amount] ?? Infinity;\n'
                    'console.log(answer === Infinity ? -1 : answer);\n',
                    'console.log(answer === Infinity ? -1 : answer);',
                    [("7", "-1"), ("11", "3"), ("9", "3")],
                    hints=["Infinity is the table's word for 'unreachable'; -1 is the report's.",
                           "Write console.log(answer === Infinity ? -1 : answer);"],
                    difficulty="Easy"),
                _ex("tscourse-w26-st-3", "How many combinations",
                    "Coins outside, amounts inside: each combination is counted once.",
                    _LINE +
                    'const coins = [1, 2, 5];\n'
                    'const amount = Number(line);\n'
                    'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
                    'ways[0] = 1;\n'
                    'for (const c of coins) {\n'
                    '  for (let a = c; a <= amount; a = a + 1) {\n'
                    '    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n  }\n}\n'
                    'console.log(ways[amount] ?? 0);\n',
                    '    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);',
                    [("5", "4"), ("11", "11"), ("0", "1")],
                    hints=["Every way to make a - c becomes a way to make a, by adding coin c.",
                           "Write ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-st-4", "How many sequences",
                    "Amounts outside, coins inside: order now matters, so 1+2 and 2+1 both count.",
                    _LINE +
                    'const coins = [1, 2, 5];\n'
                    'const amount = Number(line);\n'
                    'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
                    'ways[0] = 1;\n'
                    'for (let a = 1; a <= amount; a = a + 1) {\n'
                    '  for (const c of coins) {\n'
                    '    if (c <= a) {\n'
                    '      ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n    }\n  }\n}\n'
                    'console.log(ways[amount] ?? 0);\n',
                    'for (let a = 1; a <= amount; a = a + 1) {\n'
                    '  for (const c of coins) {',
                    [("5", "9"), ("3", "3"), ("0", "1")],
                    hints=["For each amount, the last coin could have been any coin that fits.",
                           "Amounts in the outer loop, coins in the inner one."],
                    difficulty="Medium"),
                _predict("tscourse-w26-st-p1", "What a filled array is",
                         'const n = 5;\n'
                         'const dp = new Array(n + 1).fill(0);\n',
                         "dp", "any[]",
                         why="Every DP tutorial builds its table this way. Is it typed?",
                         hints=["`new Array(n)` has not been told what it will hold.",
                                "`fill(0)` returns the same array type it was called on.",
                                "Write any[]."]),
                _fix("tscourse-w26-st-fix1", "Fix the combinations that were counted in every order",
                     "The question is how many COMBINATIONS of 1s, 2s and 5s make the amount — `1+2+2` and `2+1+2` are the same combination. For 5 this prints 9; the answer is 4. Every line of the arithmetic is right; the two loops are the wrong way round.",
                     _LINE +
                     'const coins = [1, 2, 5];\n'
                     'const amount = Number(line);\n'
                     'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
                     'ways[0] = 1;\n'
                     'for (let a = 1; a <= amount; a = a + 1) {\n'
                     '  for (const c of coins) {\n'
                     '    if (c <= a) {\n'
                     '      ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n    }\n  }\n}\n'
                     'console.log(ways[amount] ?? 0);\n',
                     _LINE +
                     'const coins = [1, 2, 5];\n'
                     'const amount = Number(line);\n'
                     'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
                     'ways[0] = 1;\n'
                     'for (const c of coins) {\n'
                     '  for (let a = c; a <= amount; a = a + 1) {\n'
                     '    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n  }\n}\n'
                     'console.log(ways[amount] ?? 0);\n',
                     [("5", "4"), ("4", "3")],
                     hints=["With amounts outside, the last coin can be any coin — so every order is a new answer.",
                            "Finish one coin's contribution completely before considering the next.",
                            "Put the coin loop outside, and start the amount loop at c."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("Coins 1 and 2, amount 3: combinations and sequences are…",
                   ["2 and 2", "2 and 3", "3 and 3", "1 and 3"], 1,
                   "{1+1+1, 1+2} against 1+1+1, 1+2, 2+1."),
                _q("Where should -1 for 'unreachable' be produced?",
                   ["in the table", "only when reporting — inside the table Infinity composes and -1 would not",
                    "in the base case", "anywhere"], 1,
                   "-1 + 1 is 0, a very wrong answer."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w26-grid", "Tables in two dimensions",
            "Grid paths — and the one-line bug that makes every row the same row.",
            """
Paths from the top-left to the bottom-right of an `R × C` grid, moving right or
down. Lesson 1 memoised it; here is the table:

* **state**: `(r, c)` — the number of ways to reach this cell
* **transition**: `dp[r][c] = dp[r-1][c] + dp[r][c-1]` — you arrived from above or
  from the left
* **base**: the first row and the first column are all 1
* **order**: row by row, left to right — both dependencies are already filled
* **answer**: `dp[R-1][C-1]`

A 3 × 7 grid has **28** paths.

## Building the table

```ts
const dp = Array.from({ length: R }, () => new Array<number>(C).fill(0));
```

`Array.from` calls the function **once per row**, so every row is a new array.
The tempting version is not:

```ts
const dp = new Array(R).fill(new Array(C).fill(0));     // ⚠️
```

`fill` puts **the same value** in every slot — and here the value is one array. Every
"row" is that array. Write `dp[0][0] = 5` and the whole first column says 5. It is
week 13's aliasing again, and a DP built on it produces confident, wrong numbers.

## Three helpers, written once

Under `noUncheckedIndexedAccess`, `dp[r][c]` is two possibly-undefined reads. This
week's grid exercises share three helpers so the indexing tax is paid once:

```ts
at(g, r, c)        // g[r]?.[c] ?? 0
put(g, r, c, v)    // writes only if the row exists
makeGrid(R, C)     // Array.from, rows really separate
```

## Minimum path sum, and obstacles

Replace `+` with `min`, add the cell's own cost, and you have the cheapest path
(the grid `1 3 1 / 1 5 1 / 4 2 1` costs **7**). Mark some cells blocked and set their
count to 0, and paths route around them. Same table, different transition — which
is the whole of the recipe.

## One row is enough

Each cell reads the cell above and the cell to its left. The cell above is *the same
index in the previous row*, so a single row updated in place,
`row[c] = row[c] + row[c - 1]`, holds exactly what is needed. O(C) space instead
of O(R × C).

> ⚠️ **Common mistakes:** `new Array(R).fill(row)`; forgetting the first row
> and column's base cases; and reading `dp[r - 1]` when r is 0.
""",
            warmup=[
                _q("A grid-path cell's count is…",
                   ["its row × column", "the cell above plus the cell to the left", "1", "the max of its neighbours"], 1,
                   "You arrived from one of the two."),
                _q("`new Array(3).fill(new Array(3).fill(0))` has how many distinct row arrays?",
                   ["3", "1", "9", "0"], 1,
                   "fill uses one value for every slot."),
                _q("`Array.from({ length: 3 }, () => [0, 0, 0])` has how many distinct rows?",
                   ["1", "3", "0", "9"], 1,
                   "The function runs once per row."),
                _q("The grid-paths table can shrink to…",
                   ["one cell", "one row", "two rows always", "nothing"], 1,
                   "Above is the same index in the previous row."),
            ],
            exercises=[
                _ex("tscourse-w26-gr-1", "Above, plus left",
                    "Fill each cell from the two cells you could have come from.",
                    _NUMS + _GRID +
                    'const R = nums[0] ?? 1;\n'
                    'const C = nums[1] ?? 1;\n'
                    'const dp = makeGrid(R, C);\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (r === 0 || c === 0) {\n'
                    '      put(dp, r, c, 1);\n'
                    '    } else {\n'
                    '      put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));\n    }\n  }\n}\n'
                    'console.log(at(dp, R - 1, C - 1));\n',
                    '      put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));',
                    [("3 7", "28"), ("3 3", "6"), ("1 1", "1")],
                    hints=["Every path into (r, c) came from (r - 1, c) or (r, c - 1).",
                           "Write put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));"],
                    difficulty="Medium"),
                _ex("tscourse-w26-gr-2", "The cheapest path",
                    "Each cell costs its own value plus the cheaper of the two ways in.",
                    _GRIDLINES + _GRID +
                    'const dp = makeGrid(R, C);\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    const own = at(rows, r, c);\n'
                    '    if (r === 0 && c === 0) {\n'
                    '      put(dp, r, c, own);\n'
                    '    } else if (r === 0) {\n'
                    '      put(dp, r, c, own + at(dp, r, c - 1));\n'
                    '    } else if (c === 0) {\n'
                    '      put(dp, r, c, own + at(dp, r - 1, c));\n'
                    '    } else {\n'
                    '      put(dp, r, c, own + Math.min(at(dp, r - 1, c), at(dp, r, c - 1)));\n    }\n  }\n}\n'
                    'console.log(at(dp, R - 1, C - 1));\n',
                    '      put(dp, r, c, own + Math.min(at(dp, r - 1, c), at(dp, r, c - 1)));',
                    [("1 3 1\n1 5 1\n4 2 1", "7"), ("1 2 3\n4 5 6", "12"), ("5", "5")],
                    hints=["The same shape as counting paths, with min instead of +, plus the cell's own cost.",
                           "Write put(dp, r, c, own + Math.min(at(dp, r - 1, c), at(dp, r, c - 1)));"],
                    difficulty="Medium"),
                _ex("tscourse-w26-gr-3", "Around the obstacles",
                    "A blocked cell (1 in the input) has no paths through it.",
                    _GRIDLINES + _GRID +
                    'const dp = makeGrid(R, C);\n'
                    'for (let r = 0; r < R; r = r + 1) {\n'
                    '  for (let c = 0; c < C; c = c + 1) {\n'
                    '    if (at(rows, r, c) === 1) {\n'
                    '      put(dp, r, c, 0);\n'
                    '    } else if (r === 0 && c === 0) {\n'
                    '      put(dp, r, c, 1);\n'
                    '    } else {\n'
                    '      put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));\n    }\n  }\n}\n'
                    'console.log(at(dp, R - 1, C - 1));\n',
                    '    if (at(rows, r, c) === 1) {\n'
                    '      put(dp, r, c, 0);',
                    [("0 0 0\n0 1 0\n0 0 0", "2"), ("0 1\n0 0", "1"), ("0 0\n1 1", "0")],
                    hints=["A blocked cell contributes nothing to the cells after it.",
                           "Set its count to 0 before anything else is considered."],
                    difficulty="Medium"),
                _ex("tscourse-w26-gr-4", "One row, updated in place",
                    "The cell above is the same index in the row you already have.",
                    _NUMS +
                    'const R = nums[0] ?? 1;\n'
                    'const C = nums[1] ?? 1;\n'
                    'const row = new Array<number>(C).fill(1);\n'
                    'for (let r = 1; r < R; r = r + 1) {\n'
                    '  for (let c = 1; c < C; c = c + 1) {\n'
                    '    row[c] = (row[c] ?? 0) + (row[c - 1] ?? 0);\n  }\n}\n'
                    'console.log(row[C - 1] ?? 0);\n',
                    '    row[c] = (row[c] ?? 0) + (row[c - 1] ?? 0);',
                    [("3 7", "28"), ("10 10", "48620")],
                    hints=["Before the write, row[c] still holds the value from the row above; row[c - 1] already holds this row's.",
                           "Write row[c] = (row[c] ?? 0) + (row[c - 1] ?? 0);"],
                    difficulty="Medium"),
                _fix("tscourse-w26-gr-fix1", "Fix the table whose rows were all one row",
                     "This prints the whole table, and every row comes out as the LAST row: `fill` put the SAME array into every slot of `dp`. "
                     "The corner is even right — with one shared row, this particular loop happens to become lesson 4's one-row version — "
                     "which is exactly why the bug survives until someone reads any other cell. A table you cannot trust away from its corner "
                     "is not a table.",
                     _NUMS + _GRID +
                     'const R = nums[0] ?? 1;\n'
                     'const C = nums[1] ?? 1;\n'
                     'const dp: number[][] = new Array(R).fill(new Array<number>(C).fill(0));\n'
                     'for (let r = 0; r < R; r = r + 1) {\n'
                     '  for (let c = 0; c < C; c = c + 1) {\n'
                     '    if (r === 0 || c === 0) {\n'
                     '      put(dp, r, c, 1);\n'
                     '    } else {\n'
                     '      put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));\n    }\n  }\n}\n'
                     'for (const row of dp) {\n'
                     '  console.log(row.join(","));\n}\n',
                     _NUMS + _GRID +
                     'const R = nums[0] ?? 1;\n'
                     'const C = nums[1] ?? 1;\n'
                     'const dp: number[][] = makeGrid(R, C);\n'
                     'for (let r = 0; r < R; r = r + 1) {\n'
                     '  for (let c = 0; c < C; c = c + 1) {\n'
                     '    if (r === 0 || c === 0) {\n'
                     '      put(dp, r, c, 1);\n'
                     '    } else {\n'
                     '      put(dp, r, c, at(dp, r - 1, c) + at(dp, r, c - 1));\n    }\n  }\n}\n'
                     'for (const row of dp) {\n'
                     '  console.log(row.join(","));\n}\n',
                     [("3 3", "1,1,1\n1,2,3\n1,3,6"), ("2 4", "1,1,1,1\n1,2,3,4")],
                     hints=["How many different row arrays does `dp` contain?",
                            "`fill` evaluates its argument once and reuses it for every slot.",
                            "Build each row separately: makeGrid(R, C), which uses Array.from."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why does the one-row version read `row[c]` before overwriting it?",
                   ["style", "before the write it still holds the row above's value", "it is 0", "types"], 1,
                   "Order within the row matters."),
                _q("A 2-D table of numbers should be typed…",
                   ["any[][]", "number[][]", "number[]", "unknown"], 1,
                   "new Array<number>(C) inside Array.from."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w26-strings", "Two sequences",
            "LCS and edit distance: one table, one row and column of sentinels.",
            """
The biggest family of DP questions compares **two** sequences. The state is a pair:
`(i, j)` — "the first i characters of `a` against the first j of `b`".

## The table is one bigger in both directions

```
        ""  a  c  e
    ""   0  0  0  0
    a    0  1  1  1
    b    0  1  1  1
    c    0  1  2  2
    d    0  1  2  2
    e    0  1  2  3      ← LCS("abcde", "ace") = 3
```

Row 0 and column 0 are the **empty prefix** — the LCS of anything with "" is 0.
Week 23's prefix-sum sentinel and week 24's counting-sort `starts` array, again: one
extra row and column so the transition never needs an `if (i === 0)`. And it means
character `i` of the prefix is `a[i - 1]` — the off-by-one every two-string DP has.

## Longest common subsequence

```ts
if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;       // extend a match
else                       dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);   // drop one char
```

## Getting the string, not just its length

The table only stores lengths. To recover the subsequence itself, **walk back** from
the corner: where the characters match, that character is in the answer and you
step diagonally; otherwise step toward the larger neighbour. The characters come out
in reverse, so collect them and reverse once. This is **reconstruction**, and every
DP that asks "which" rather than "how many" ends with it.

## Edit distance

The fewest single-character edits — insert, delete, substitute — turning `a` into
`b`:

```ts
if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1];           // free
else dp[i][j] = 1 + Math.min(
  dp[i - 1][j - 1],     // substitute
  dp[i - 1][j],         // delete from a
  dp[i][j - 1],         // insert into a
);
```

with row 0 = `j` (insert everything) and column 0 = `i` (delete everything).
`kitten` → `sitting` is **3**. It is what spell-checkers and `diff` are built on.

> ⚠️ **Common mistakes:** comparing `a[i]` instead of `a[i - 1]`; forgetting the
> base row and column of edit distance (they are not zero); and reversing the
> reconstruction twice, or not at all.
""",
            warmup=[
                _q("The LCS table for strings of length 5 and 3 is…",
                   ["5 × 3", "6 × 4", "8 × 8", "15"], 1,
                   "Plus one for the empty prefix, both ways."),
                _q("At table position (i, j), the characters compared are…",
                   ["a[i] and b[j]", "a[i - 1] and b[j - 1]", "a[j] and b[i]", "a[0] and b[0]"], 1,
                   "Row i is the first i characters."),
                _q("Edit distance's first row is…",
                   ["all zeros", "0, 1, 2, … — insert j characters", "all ones", "undefined"], 1,
                   "Turning \"\" into b[0..j] takes j inserts."),
                _q("Reconstruction walks the table…",
                   ["forwards from (0, 0)", "back from the corner", "row by row", "randomly"], 1,
                   "Then reverses what it collected."),
            ],
            exercises=[
                _ex("tscourse-w26-sq-1", "Extend a match",
                    "When the two characters agree, the LCS grows by one from the diagonal.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);\n'
                    '    } else {\n'
                    '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'console.log(at(dp, a.length, b.length));\n',
                    '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);',
                    [("abcde\nace", "3"), ("abc\ndef", "0"), ("abc\nabc", "3")],
                    hints=["A matching character extends the best subsequence of both shorter prefixes.",
                           "Write put(dp, i, j, at(dp, i - 1, j - 1) + 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-sq-2", "Drop one character",
                    "When they differ, the best comes from dropping the last character of one string or the other.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);\n'
                    '    } else {\n'
                    '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'console.log(at(dp, a.length, b.length));\n',
                    '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));',
                    [("abcde\nace", "3"), ("aggtab\ngxtxayb", "4")],
                    hints=["The better of: a without its last character, or b without its last character.",
                           "Write put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));"],
                    difficulty="Medium"),
                _ex("tscourse-w26-sq-3", "Walk it back",
                    "Recover the subsequence itself from the finished table.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);\n'
                    '    } else {\n'
                    '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'const out: string[] = [];\n'
                    'let i = a.length;\n'
                    'let j = b.length;\n'
                    'while (i > 0 && j > 0) {\n'
                    '  if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '    out.push(a.charAt(i - 1));\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;\n'
                    '  } else if (at(dp, i - 1, j) >= at(dp, i, j - 1)) {\n'
                    '    i = i - 1;\n'
                    '  } else {\n'
                    '    j = j - 1;\n  }\n}\n'
                    'console.log(out.reverse().join("") || "(none)");\n',
                    '  if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '    out.push(a.charAt(i - 1));\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;',
                    [("abcde\nace", "ace"), ("abc\ndef", "(none)"), ("xaybz\nabz", "abz")],
                    hints=["A matching pair is part of the answer — take it and step diagonally.",
                           "Characters are collected last-first, which is why the result is reversed at the end."],
                    difficulty="Hard"),
                _ex("tscourse-w26-sq-4", "Edit distance",
                    "When the characters differ, pay one edit and take the cheapest of substitute, delete or insert.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 0; i <= a.length; i = i + 1) {\n'
                    '  put(dp, i, 0, i);\n}\n'
                    'for (let j = 0; j <= b.length; j = j + 1) {\n'
                    '  put(dp, 0, j, j);\n}\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1));\n'
                    '    } else {\n'
                    '      put(dp, i, j, 1 + Math.min(at(dp, i - 1, j - 1), at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'console.log(at(dp, a.length, b.length));\n',
                    '      put(dp, i, j, 1 + Math.min(at(dp, i - 1, j - 1), at(dp, i - 1, j), at(dp, i, j - 1)));',
                    [("kitten\nsitting", "3"), ("horse\nros", "3"), ("abc\nabc", "0")],
                    hints=["Diagonal is a substitution, up is a deletion, left is an insertion.",
                           "Write put(dp, i, j, 1 + Math.min(at(dp, i - 1, j - 1), at(dp, i - 1, j), at(dp, i, j - 1)));"],
                    difficulty="Hard"),
                _ex("tscourse-w26-sq-5", "The empty prefix is not free",
                    "Seed edit distance's first column: turning i characters into nothing takes i deletions.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 0; i <= a.length; i = i + 1) {\n'
                    '  put(dp, i, 0, i);\n}\n'
                    'for (let j = 0; j <= b.length; j = j + 1) {\n'
                    '  put(dp, 0, j, j);\n}\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1));\n'
                    '    } else {\n'
                    '      put(dp, i, j, 1 + Math.min(at(dp, i - 1, j - 1), at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'console.log(at(dp, a.length, b.length));\n',
                    'for (let i = 0; i <= a.length; i = i + 1) {\n'
                    '  put(dp, i, 0, i);\n}',
                    [("abc\n", "3"), ("kitten\nsitting", "3")],
                    hints=["Column 0 is 'turn the first i characters of a into the empty string'.",
                           "That is i deletions, for every i from 0 to a.length."],
                    difficulty="Medium"),
                _fix("tscourse-w26-sq-fix1", "Fix the characters compared one place off",
                     "For `abc` against `xbc` this prints 3 — longer than either shared run. Row i of the table means 'the first i characters', whose last character is at index i - 1, but the comparison reads index i: it never looks at the first characters, and at the very last cell both `charAt` calls run off the end and return `\"\"` — and `\"\" === \"\"` is a match. "
                     "On `abcde` against `ace` those two errors cancel and it prints the right answer, which is what makes this bug so hard to see.",
                     _TWO + _GRID +
                     'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                     'for (let i = 1; i <= a.length; i = i + 1) {\n'
                     '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                     '    if (a.charAt(i) === b.charAt(j)) {\n'
                     '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);\n'
                     '    } else {\n'
                     '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                     'console.log(at(dp, a.length, b.length));\n',
                     _TWO + _GRID +
                     'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                     'for (let i = 1; i <= a.length; i = i + 1) {\n'
                     '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                     '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                     '      put(dp, i, j, at(dp, i - 1, j - 1) + 1);\n'
                     '    } else {\n'
                     '      put(dp, i, j, Math.max(at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                     'console.log(at(dp, a.length, b.length));\n',
                     [("abc\nxbc", "2"), ("axc\nbyc", "1"), ("abcde\nace", "3")],
                     hints=["Row 1 is the one-character prefix. Which index holds that character?",
                            "The table is shifted by one against the strings, because of the empty-prefix row.",
                            "Compare a.charAt(i - 1) with b.charAt(j - 1)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The longest palindromic subsequence of s is…",
                   ["s reversed", "the LCS of s and s reversed", "the longest palindrome substring", "s itself"], 1,
                   "\"bbbab\" gives 4."),
                _q("Edit distance is used by…",
                   ["sorting", "spell-checkers and diff tools", "hash maps", "binary search"], 1,
                   "Nearest word, smallest change."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w26-knapsack", "Choices with a budget",
            "0/1 knapsack, and why one row goes backwards.",
            """
Items have a **weight** and a **value**; the bag holds at most `W`. Take each item
**at most once**. What is the most value that fits?

Greedy fails here too (highest value, or best value per weight, both have
counter-examples), and trying every subset is week 25's 2ⁿ. DP:

* **state**: `(i, cap)` — the best value using the first i items with capacity cap
* **transition**: skip item i, or take it if it fits:
  `best[i][cap] = max(best[i-1][cap], best[i-1][cap - w] + v)`
* **base**: no items, or no capacity — value 0
* **answer**: `best[n][W]`

Weights `1 3 4 5`, values `1 4 5 7`, capacity 7 → **9** (the 3 and the 4).

## One row, backwards

Row i only reads row i − 1, so one array can hold it — **if** you iterate capacity
from high to low:

```ts
for (const item of items) {
  for (let cap = W; cap >= item.w; cap = cap - 1) {
    best[cap] = Math.max(best[cap] ?? 0, (best[cap - item.w] ?? 0) + item.v);
  }
}
```

Going **down**, `best[cap - item.w]` has not been updated for this item yet, so it
still means "without this item". Going **up**, it has — the item has already been
added at a smaller capacity, and adding it again takes it **twice**. One item,
weight 2, value 3, capacity 6: backwards gives 3, forwards gives **9**.

Forwards is not wrong in general — it is exactly right for the **unbounded**
knapsack, where each item may be taken any number of times. It is the same trap as
lesson 3's coin loops: the direction of a loop is part of the meaning.

## Subset sum

"Can some subset of these numbers make exactly T?" is knapsack with booleans:
`can[t] = can[t] || can[t - x]`, backwards for the same reason.

## Pseudo-polynomial

The table is `n × (W + 1)`. That is polynomial in the **value** of W, not in the
number of digits it takes to write it — a capacity of a billion is a billion
columns. DP for knapsack is fast when the budget is small, and not otherwise.

> ⚠️ **Common mistakes:** iterating capacity forwards in the 0/1 version; greedy
> by value or by ratio; and a capacity so large the table cannot be allocated.
""",
            warmup=[
                _q("0/1 knapsack means each item is taken…",
                   ["any number of times", "at most once", "exactly once", "in order"], 1,
                   "In or out."),
                _q("The one-row 0/1 version iterates capacity…",
                   ["forwards", "backwards", "either", "twice"], 1,
                   "So best[cap - w] still means 'without this item'."),
                _q("Iterating forwards solves…",
                   ["nothing", "the unbounded knapsack", "subset sum", "LCS"], 1,
                   "Items may be reused."),
                _q("Knapsack's table has…",
                   ["n cells", "n × (W + 1) cells", "2ⁿ cells", "W cells always"], 1,
                   "Pseudo-polynomial."),
            ],
            exercises=[
                _ex("tscourse-w26-ks-1", "Can it be made exactly?",
                    "Subset sum: a target is reachable if it was already, or if target minus this number was.",
                    _NUMS +
                    'const target = 9;\n'
                    'const can: boolean[] = new Array<boolean>(target + 1).fill(false);\n'
                    'can[0] = true;\n'
                    'for (const x of nums) {\n'
                    '  for (let t = target; t >= x; t = t - 1) {\n'
                    '    can[t] = (can[t] ?? false) || (can[t - x] ?? false);\n  }\n}\n'
                    'console.log(can[target] ?? false);\n',
                    '    can[t] = (can[t] ?? false) || (can[t - x] ?? false);',
                    [("3 34 4 12 5 2", "true"), ("1 2 3", "false"), ("9", "true")],
                    hints=["Either t was already reachable, or t - x was and x gets there.",
                           "Write can[t] = (can[t] ?? false) || (can[t - x] ?? false);"],
                    difficulty="Medium"),
                _ex("tscourse-w26-ks-2", "Skip it or take it",
                    "The 2-D 0/1 knapsack: the better of leaving item i out, or putting it in if it fits.",
                    _GRID +
                    'const weights = [1, 3, 4, 5];\n'
                    'const values = [1, 4, 5, 7];\n'
                    'const W = 7;\n'
                    'const n = weights.length;\n'
                    'const best = makeGrid(n + 1, W + 1);\n'
                    'for (let i = 1; i <= n; i = i + 1) {\n'
                    '  const w = weights[i - 1] ?? 0;\n'
                    '  const v = values[i - 1] ?? 0;\n'
                    '  for (let cap = 0; cap <= W; cap = cap + 1) {\n'
                    '    const skip = at(best, i - 1, cap);\n'
                    '    const take = w <= cap ? at(best, i - 1, cap - w) + v : 0;\n'
                    '    put(best, i, cap, Math.max(skip, take));\n  }\n}\n'
                    'console.log(at(best, n, W));\n',
                    '    const take = w <= cap ? at(best, i - 1, cap - w) + v : 0;',
                    [("", "9")],
                    hints=["Taking item i leaves cap - w for the first i - 1 items — and adds v.",
                           "Write const take = w <= cap ? at(best, i - 1, cap - w) + v : 0;"],
                    difficulty="Hard"),
                _ex("tscourse-w26-ks-3", "One row, backwards",
                    "The same answer from a single row, iterating capacity downwards.",
                    'const weights = [1, 3, 4, 5];\n'
                    'const values = [1, 4, 5, 7];\n'
                    'const W = 7;\n'
                    'const best: number[] = new Array<number>(W + 1).fill(0);\n'
                    'for (let i = 0; i < weights.length; i = i + 1) {\n'
                    '  const w = weights[i] ?? 0;\n'
                    '  const v = values[i] ?? 0;\n'
                    '  for (let cap = W; cap >= w; cap = cap - 1) {\n'
                    '    best[cap] = Math.max(best[cap] ?? 0, (best[cap - w] ?? 0) + v);\n  }\n}\n'
                    'console.log(best[W] ?? 0);\n',
                    '  for (let cap = W; cap >= w; cap = cap - 1) {',
                    [("", "9")],
                    hints=["Downwards, so best[cap - w] has not yet been updated for this item.",
                           "Write for (let cap = W; cap >= w; cap = cap - 1) {"],
                    difficulty="Medium"),
                _ex("tscourse-w26-ks-4", "When reuse is allowed",
                    "Run the one-row knapsack both ways and report both: forwards is the unbounded version.",
                    'const weights = [2, 3];\n'
                    'const values = [3, 5];\n'
                    'const W = 7;\n'
                    'function solve(forwards: boolean): number {\n'
                    '  const best: number[] = new Array<number>(W + 1).fill(0);\n'
                    '  for (let i = 0; i < weights.length; i = i + 1) {\n'
                    '    const w = weights[i] ?? 0;\n'
                    '    const v = values[i] ?? 0;\n'
                    '    if (forwards) {\n'
                    '      for (let cap = w; cap <= W; cap = cap + 1) {\n'
                    '        best[cap] = Math.max(best[cap] ?? 0, (best[cap - w] ?? 0) + v);\n      }\n'
                    '    } else {\n'
                    '      for (let cap = W; cap >= w; cap = cap - 1) {\n'
                    '        best[cap] = Math.max(best[cap] ?? 0, (best[cap - w] ?? 0) + v);\n      }\n    }\n  }\n'
                    '  return best[W] ?? 0;\n}\n'
                    'console.log(`once=${solve(false)} unbounded=${solve(true)}`);\n',
                    '      for (let cap = w; cap <= W; cap = cap + 1) {',
                    [("", "once=8 unbounded=11")],
                    hints=["Upwards, an item added at a small capacity can be added again at a larger one.",
                           "Write for (let cap = w; cap <= W; cap = cap + 1) {"],
                    difficulty="Medium"),
                _fix("tscourse-w26-ks-fix1", "Fix the item that was packed twice",
                     "There is ONE item — weight 2, value 3 — and a capacity of 6, so the answer is 3. This prints 9: capacity is walked upwards, so by the time cap reaches 4, best[2] already includes the item, and it is added again, and again.",
                     'const weights = [2];\n'
                     'const values = [3];\n'
                     'const W = 6;\n'
                     'const best: number[] = new Array<number>(W + 1).fill(0);\n'
                     'for (let i = 0; i < weights.length; i = i + 1) {\n'
                     '  const w = weights[i] ?? 0;\n'
                     '  const v = values[i] ?? 0;\n'
                     '  for (let cap = w; cap <= W; cap = cap + 1) {\n'
                     '    best[cap] = Math.max(best[cap] ?? 0, (best[cap - w] ?? 0) + v);\n  }\n}\n'
                     'console.log(best[W] ?? 0);\n',
                     'const weights = [2];\n'
                     'const values = [3];\n'
                     'const W = 6;\n'
                     'const best: number[] = new Array<number>(W + 1).fill(0);\n'
                     'for (let i = 0; i < weights.length; i = i + 1) {\n'
                     '  const w = weights[i] ?? 0;\n'
                     '  const v = values[i] ?? 0;\n'
                     '  for (let cap = W; cap >= w; cap = cap - 1) {\n'
                     '    best[cap] = Math.max(best[cap] ?? 0, (best[cap - w] ?? 0) + v);\n  }\n}\n'
                     'console.log(best[W] ?? 0);\n',
                     [("", "3")],
                     hints=["When cap = 4 is updated, what does best[2] already contain?",
                            "It must still mean 'without this item'.",
                            "Walk capacity downwards: for (let cap = W; cap >= w; cap = cap - 1)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Subset sum iterates its target backwards because…",
                   ["it is faster", "each number may be used only once", "it is sorted", "of booleans"], 1,
                   "The same reason as 0/1 knapsack."),
                _q("A capacity of one billion makes knapsack DP…",
                   ["instant", "infeasible — a billion columns", "logarithmic", "unchanged"], 1,
                   "Pseudo-polynomial."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w26-choose", "Recognising DP",
            "Greedy, backtracking or DP — and the input that decides.",
            """
## Greedy is the first thing to try — and to test

Coin change with real-world coins (1, 5, 10, 25) works greedily: take the largest
coin that fits, repeat. So it is tempting to think it always does. Coins **1, 3, 4**,
amount **6**:

```
greedy:  4 + 1 + 1   = 3 coins
DP:      3 + 3       = 2 coins
```

Greedy commits to the 4 and never reconsiders. DP compares every choice at every
amount. That is the whole difference, and it is why a greedy answer to a DP
question needs a **proof**, not a hunch — or a counter-example, which is usually
faster to find.

## The two conditions, as questions

1. **Does the naive recursion repeat itself?** Draw two levels of calls. If the same
   arguments appear twice, it does.
2. **Is the best whole made of best parts?** The shortest route through a city
   passes through the shortest route to each point on it. The *longest simple*
   path does not — which is why that one is not a DP.

## Which one, from the wording

| the question | reach for |
|---|---|
| "list all …" | backtracking (week 25) |
| "how many ways …", "fewest …", "longest …", "can it be …" | DP |
| "…and the choice is provably safe" | greedy |
| "contiguous" with a simple running condition | a window (week 23) — or Kadane |

## One more classic: longest increasing subsequence

`dp[i]` = the longest increasing subsequence **ending at i**:

```ts
dp[i] = 1 + max(dp[j] for j < i where xs[j] < xs[i])     // or 1 if none
```

O(n²). `10 9 2 5 3 7 101 18` → **4** (2, 3, 7, 18). ("Ending at i" is the same
state-shaping move as Kadane's "best run ending here" — the answer is then the
maximum over all i.)

## Word break

"Can `leetcode` be split into dictionary words?" State: `ok[i]` — can the first i
characters be split? `ok[i]` is true if some `j < i` has `ok[j]` and `s.slice(j, i)`
in the dictionary. A prefix table again, with week 19's `Set` for the lookups.

> ⚠️ **Common mistakes:** trusting greedy without a counter-example check; DP where
> the substructure is not optimal; and forgetting to take the max over all end
> positions for "ending at i" states.
""",
            warmup=[
                _q("Greedy coin change with coins 1, 3, 4 for 6 gives…",
                   ["2", "3", "6", "none"], 1,
                   "4 + 1 + 1."),
                _q("A greedy answer to a DP-looking problem needs…",
                   ["nothing", "a proof — or a hunt for a counter-example", "memoisation", "sorting"], 1,
                   "Counter-examples are usually quicker."),
                _q("LIS's state is…",
                   ["the LIS so far", "the longest increasing subsequence ENDING at i", "the max", "a Set"], 1,
                   "Then take the max over i."),
                _q("\"List all valid splits\" points at…",
                   ["DP", "backtracking", "greedy", "a heap"], 1,
                   "Listing is generating; DP would answer 'can it'."),
            ],
            exercises=[
                _ex("tscourse-w26-ch-1", "What greedy does",
                    "Take the largest coin that fits, repeatedly, and report how many it took.",
                    _LINE +
                    'const coins = [4, 3, 1];\n'
                    'let left = Number(line);\n'
                    'const used: number[] = [];\n'
                    'for (const c of coins) {\n'
                    '  while (left >= c) {\n'
                    '    used.push(c);\n'
                    '    left = left - c;\n  }\n}\n'
                    'console.log(`${used.length} ${used.join("+")}`);\n',
                    '  while (left >= c) {\n'
                    '    used.push(c);\n'
                    '    left = left - c;\n  }',
                    [("6", "3 4+1+1"), ("8", "2 4+4")],
                    hints=["Keep taking this coin while it still fits.",
                           "Push it and reduce what is left, inside a while loop."],
                    difficulty="Easy"),
                _ex("tscourse-w26-ch-2", "Longest increasing subsequence",
                    "The longest increasing run ending at i extends the best one ending at any smaller earlier value.",
                    _NUMS +
                    'const dp: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  let best = 1;\n'
                    '  for (let j = 0; j < i; j = j + 1) {\n'
                    '    if ((nums[j] ?? 0) < (nums[i] ?? 0)) {\n'
                    '      best = Math.max(best, (dp[j] ?? 0) + 1);\n    }\n  }\n'
                    '  dp.push(best);\n}\n'
                    'console.log(Math.max(...dp));\n',
                    '      best = Math.max(best, (dp[j] ?? 0) + 1);',
                    [("10 9 2 5 3 7 101 18", "4"), ("5 4 3", "1"), ("1 2 3", "3")],
                    hints=["A smaller value at j can be followed by nums[i].",
                           "Write best = Math.max(best, (dp[j] ?? 0) + 1);"],
                    difficulty="Hard"),
                _ex("tscourse-w26-ch-3", "Word break",
                    "The first i characters can be split if some shorter splittable prefix is followed by a dictionary word.",
                    _WORDS +
                    'const text = words[0] ?? "";\n'
                    'const dict = new Set(words.slice(1));\n'
                    'const ok: boolean[] = new Array<boolean>(text.length + 1).fill(false);\n'
                    'ok[0] = true;\n'
                    'for (let i = 1; i <= text.length; i = i + 1) {\n'
                    '  for (let j = 0; j < i; j = j + 1) {\n'
                    '    if ((ok[j] ?? false) && dict.has(text.slice(j, i))) {\n'
                    '      ok[i] = true;\n    }\n  }\n}\n'
                    'console.log(ok[text.length] ?? false);\n',
                    '    if ((ok[j] ?? false) && dict.has(text.slice(j, i))) {',
                    [("leetcode leet code", "true"), ("catsandog cats dog sand and cat", "false"),
                     ("applepenapple apple pen", "true")],
                    hints=["Split point j: the part before it must be splittable, the part after it a word.",
                           "Write if ((ok[j] ?? false) && dict.has(text.slice(j, i))) {"],
                    difficulty="Hard"),
                _ex("tscourse-w26-ch-4", "Name the technique",
                    "Map each kind of question to the technique that answers it.",
                    _NUMS +
                    'function technique(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "backtracking";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "dynamic programming";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "greedy, with a proof";\n  }\n'
                    '  return "sliding window";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${technique(k)}`);\n}\n',
                    '  if (kind === 2) {\n'
                    '    return "dynamic programming";\n  }',
                    [("1 2 3 4", "1 backtracking\n2 dynamic programming\n3 greedy, with a proof\n4 sliding window")],
                    hints=["Kind 2 is 'how many ways / the fewest', with repeated subproblems.",
                           'Write if (kind === 2) { return "dynamic programming"; }'],
                    difficulty="Easy"),
                _fix("tscourse-w26-ch-fix1", "Fix the greedy that was not optimal",
                     "With coins 1, 3 and 4, this reports 3 coins for 6 — it takes the 4 and is stuck with 1 + 1. The fewest is 2 (3 + 3). Greedy never reconsiders a choice; replace it with a table that compares every coin at every amount.",
                     _LINE +
                     'const coins = [4, 3, 1];\n'
                     'let left = Number(line);\n'
                     'let count = 0;\n'
                     'for (const c of coins) {\n'
                     '  while (left >= c) {\n'
                     '    left = left - c;\n'
                     '    count = count + 1;\n  }\n}\n'
                     'console.log(count);\n',
                     _LINE +
                     'const coins = [4, 3, 1];\n'
                     'const amount = Number(line);\n'
                     'const dp: number[] = [0];\n'
                     'for (let a = 1; a <= amount; a = a + 1) {\n'
                     '  let best = Infinity;\n'
                     '  for (const c of coins) {\n'
                     '    if (c <= a) {\n'
                     '      best = Math.min(best, (dp[a - c] ?? Infinity) + 1);\n    }\n  }\n'
                     '  dp.push(best);\n}\n'
                     'console.log(dp[amount] ?? 0);\n',
                     [("6", "2"), ("10", "3"), ("4", "1")],
                     hints=["Greedy's first choice for 6 is 4. Is that choice part of the best answer?",
                            "The fewest coins for a is 1 + the fewest for a - c, for the BEST c.",
                            "Build dp from 0 up to the amount, trying every coin at every amount."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is 'longest simple path' not a DP problem?",
                   ["it is too easy", "the longest path is not built from longest sub-paths — no optimal substructure",
                    "it has no subproblems", "it is a graph"], 1,
                   "The second condition fails."),
                _q("LIS in O(n²) takes the answer as…",
                   ["dp[n - 1]", "the maximum of dp over all i", "dp[0]", "n"], 1,
                   "The best subsequence can end anywhere."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #26 — the coin report",
        """
Three DP questions about one set of coins and one amount, plus the answer greedy
would have given.

Input: the coin values on the first line (any order), the amount on the second.

```
1 3 4
6
```

```
Fewest:    2  3+3
Greedy:    3  4+1+1
Ways:      4
```

**The rows:**

* **Fewest** — the minimum number of coins, then the coins themselves, largest
  first, joined with `+`. Recover them by recording, for each amount, which coin
  achieved its minimum (trying coins in ascending order and keeping the first
  strictly better one), then walking back from the amount.
* **Greedy** — repeatedly take the largest coin that fits. Report its count and
  coins the same way, or `none` if it gets stuck before reaching zero.
* **Ways** — the number of distinct **combinations** (order does not matter).

When the amount cannot be made at all, **Fewest** is `none`. An amount of 0 is made
with no coins: `0  -` for both Fewest and Greedy, and exactly 1 way.

Label padded to 11. The count and coins are separated by two spaces.

**What makes it a rep:** the second test is an input where greedy **fails to reach
the amount at all** while DP succeeds; the first is one where greedy reaches it
badly. Ways uses the coin-outside loop from lesson 3, and a solution with the loops
swapped gets the first test wrong.
""",
        _ch("tscourse-w26-capstone", "Interview rep #26", "Hard",
            "Report the fewest coins and which ones, greedy's answer, and the number of "
            "combinations — for one set of coins and one amount.",
            _FS +
            'const lines = fs.readFileSync(0, "utf8").split("\\n");\n'
            'const coins: readonly number[] = (lines[0] ?? "")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number)\n'
            '  .sort((a, b) => a - b);\n'
            'const amount = Number((lines[1] ?? "").trim() || "0");\n'
            'function row(label: string, text: string): string {\n'
            '  return `${(label + ":").padEnd(11)}${text}`;\n}\n'
            'function describe(used: readonly number[]): string {\n'
            '  const parts = [...used].sort((a, b) => b - a);\n'
            '  return `${parts.length}  ${parts.length === 0 ? "-" : parts.join("+")}`;\n}\n'
            'const fewest: number[] = [0];\n'
            'const choice: number[] = [0];\n'
            'for (let a = 1; a <= amount; a = a + 1) {\n'
            '  let best = Infinity;\n'
            '  let pick = 0;\n'
            '  for (const c of coins) {\n'
            '    if (c <= a && (fewest[a - c] ?? Infinity) + 1 < best) {\n'
            '      best = (fewest[a - c] ?? Infinity) + 1;\n'
            '      pick = c;\n    }\n  }\n'
            '  fewest.push(best);\n'
            '  choice.push(pick);\n}\n'
            'if ((fewest[amount] ?? Infinity) === Infinity) {\n'
            '  console.log(row("Fewest", "none"));\n'
            '} else {\n'
            '  const used: number[] = [];\n'
            '  let a = amount;\n'
            '  while (a > 0) {\n'
            '    const c = choice[a] ?? 0;\n'
            '    used.push(c);\n'
            '    a = a - c;\n  }\n'
            '  console.log(row("Fewest", describe(used)));\n}\n'
            'const greedy: number[] = [];\n'
            'let left = amount;\n'
            'for (const c of [...coins].reverse()) {\n'
            '  while (c > 0 && left >= c) {\n'
            '    greedy.push(c);\n'
            '    left = left - c;\n  }\n}\n'
            'console.log(row("Greedy", left === 0 ? describe(greedy) : "none"));\n'
            'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
            'ways[0] = 1;\n'
            'for (const c of coins) {\n'
            '  for (let a = c; a <= amount; a = a + 1) {\n'
            '    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n  }\n}\n'
            'console.log(row("Ways", String(ways[amount] ?? 0)));\n',
            'const fewest: number[] = [0];\n'
            'const choice: number[] = [0];\n'
            'for (let a = 1; a <= amount; a = a + 1) {\n'
            '  let best = Infinity;\n'
            '  let pick = 0;\n'
            '  for (const c of coins) {\n'
            '    if (c <= a && (fewest[a - c] ?? Infinity) + 1 < best) {\n'
            '      best = (fewest[a - c] ?? Infinity) + 1;\n'
            '      pick = c;\n    }\n  }\n'
            '  fewest.push(best);\n'
            '  choice.push(pick);\n}\n'
            'if ((fewest[amount] ?? Infinity) === Infinity) {\n'
            '  console.log(row("Fewest", "none"));\n'
            '} else {\n'
            '  const used: number[] = [];\n'
            '  let a = amount;\n'
            '  while (a > 0) {\n'
            '    const c = choice[a] ?? 0;\n'
            '    used.push(c);\n'
            '    a = a - c;\n  }\n'
            '  console.log(row("Fewest", describe(used)));\n}\n'
            'const greedy: number[] = [];\n'
            'let left = amount;\n'
            'for (const c of [...coins].reverse()) {\n'
            '  while (c > 0 && left >= c) {\n'
            '    greedy.push(c);\n'
            '    left = left - c;\n  }\n}\n'
            'console.log(row("Greedy", left === 0 ? describe(greedy) : "none"));\n'
            'const ways: number[] = new Array<number>(amount + 1).fill(0);\n'
            'ways[0] = 1;\n'
            'for (const c of coins) {\n'
            '  for (let a = c; a <= amount; a = a + 1) {\n'
            '    ways[a] = (ways[a] ?? 0) + (ways[a - c] ?? 0);\n  }\n}\n'
            'console.log(row("Ways", String(ways[amount] ?? 0)));',
            [("1 3 4\n6", "Fewest:    2  3+3\nGreedy:    3  4+1+1\nWays:      4"),
             ("5 3\n9", "Fewest:    3  3+3+3\nGreedy:    none\nWays:      1"),
             ("2\n3", "Fewest:    none\nGreedy:    none\nWays:      0"),
             ("5 2 1\n11", "Fewest:    3  5+5+1\nGreedy:    3  5+5+1\nWays:      11"),
             ("1 2\n0", "Fewest:    0  -\nGreedy:    0  -\nWays:      1")],
            hints=["Sort the coins once; ascending order makes 'the first strictly better coin' well defined.",
                   "Keep a second array beside the table recording which coin achieved each minimum — that is what reconstruction walks.",
                   "Infinity means unreachable inside the table; turn it into `none` only when printing.",
                   "Greedy walks the coins largest first and reports `none` if anything is left over.",
                   "Ways puts the coin loop OUTSIDE the amount loop, so each combination is counted once.",
                   "Print the coins largest first, whatever order the reconstruction found them in."]),
        example_io="Fewest:    2  3+3\nGreedy:    3  4+1+1\nWays:      4",
        rubric=["the fewest-coins table is built bottom-up, with Infinity for unreachable amounts",
                "the coins used are reconstructed from a recorded choice per amount, not searched for again",
                "greedy is implemented honestly, including getting stuck",
                "combinations are counted with the coin loop outside",
                "unreachable and zero amounts are both handled",
                "tables are typed number[], never any[]",
                "no index access is asserted with `!`"],
        stretch=_ch("tscourse-w26-capstone-stretch", "Interview rep #26 (stretch)", "Hard",
                    "Edit distance, explained. Read two words. Print `distance N`, then the edits that "
                    "achieve it, first to last, one per line: `sub x>y`, `del x` or `ins y`. Reconstruct by "
                    "walking back from the corner, preferring — at each cell — a free match, then a "
                    "substitution, then a deletion, then an insertion. Matched characters print nothing.",
                    _TWO + _GRID +
                    'const dp = makeGrid(a.length + 1, b.length + 1);\n'
                    'for (let i = 0; i <= a.length; i = i + 1) {\n'
                    '  put(dp, i, 0, i);\n}\n'
                    'for (let j = 0; j <= b.length; j = j + 1) {\n'
                    '  put(dp, 0, j, j);\n}\n'
                    'for (let i = 1; i <= a.length; i = i + 1) {\n'
                    '  for (let j = 1; j <= b.length; j = j + 1) {\n'
                    '    if (a.charAt(i - 1) === b.charAt(j - 1)) {\n'
                    '      put(dp, i, j, at(dp, i - 1, j - 1));\n'
                    '    } else {\n'
                    '      put(dp, i, j, 1 + Math.min(at(dp, i - 1, j - 1), at(dp, i - 1, j), at(dp, i, j - 1)));\n    }\n  }\n}\n'
                    'const edits: string[] = [];\n'
                    'let i = a.length;\n'
                    'let j = b.length;\n'
                    'while (i > 0 || j > 0) {\n'
                    '  const here = at(dp, i, j);\n'
                    '  if (i > 0 && j > 0 && a.charAt(i - 1) === b.charAt(j - 1) && here === at(dp, i - 1, j - 1)) {\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;\n'
                    '  } else if (i > 0 && j > 0 && here === at(dp, i - 1, j - 1) + 1) {\n'
                    '    edits.push(`sub ${a.charAt(i - 1)}>${b.charAt(j - 1)}`);\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;\n'
                    '  } else if (i > 0 && here === at(dp, i - 1, j) + 1) {\n'
                    '    edits.push(`del ${a.charAt(i - 1)}`);\n'
                    '    i = i - 1;\n'
                    '  } else {\n'
                    '    edits.push(`ins ${b.charAt(j - 1)}`);\n'
                    '    j = j - 1;\n  }\n}\n'
                    'console.log(`distance ${at(dp, a.length, b.length)}`);\n'
                    'for (const e of edits.reverse()) {\n'
                    '  console.log(e);\n}\n',
                    'const edits: string[] = [];\n'
                    'let i = a.length;\n'
                    'let j = b.length;\n'
                    'while (i > 0 || j > 0) {\n'
                    '  const here = at(dp, i, j);\n'
                    '  if (i > 0 && j > 0 && a.charAt(i - 1) === b.charAt(j - 1) && here === at(dp, i - 1, j - 1)) {\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;\n'
                    '  } else if (i > 0 && j > 0 && here === at(dp, i - 1, j - 1) + 1) {\n'
                    '    edits.push(`sub ${a.charAt(i - 1)}>${b.charAt(j - 1)}`);\n'
                    '    i = i - 1;\n'
                    '    j = j - 1;\n'
                    '  } else if (i > 0 && here === at(dp, i - 1, j) + 1) {\n'
                    '    edits.push(`del ${a.charAt(i - 1)}`);\n'
                    '    i = i - 1;\n'
                    '  } else {\n'
                    '    edits.push(`ins ${b.charAt(j - 1)}`);\n'
                    '    j = j - 1;\n  }\n}',
                    [("kitten\nsitting", "distance 3\nsub k>s\nsub e>i\nins g"),
                     ("horse\nros", "distance 3\nsub h>r\ndel r\ndel e"),
                     ("\nab", "distance 2\nins a\nins b"),
                     ("same\nsame", "distance 0")],
                    hints=["Fill the table exactly as in lesson 5; the new part is only the walk back.",
                           "At each cell, test the four moves in the stated order and take the first whose arithmetic matches.",
                           "Guard every move: a deletion needs i > 0, an insertion j > 0, and the diagonal both.",
                           "Edits are found last-first, so reverse them before printing."]),
    ),
))
