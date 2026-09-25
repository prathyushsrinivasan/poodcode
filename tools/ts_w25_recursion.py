# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 25 — recursion & backtracking.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THIS WEEK DEEPENS; IT DOES NOT INTRODUCE.
#
# Week 20 introduced recursion on trees, because a tree's type refers to itself
# and teaching it any other way was contorted. So this file opens, as TS_ROADMAP
# asks, with "you have been recursing over trees since week 20; here is the whole
# story" — and every earlier recursion is named where it is reused:
#
#   week 20   depth(), the traversals, pathTo() — which already BACKTRACKS: it
#             returns null to mean "not in this subtree" so the caller tries the
#             next branch. Lesson 7 names the pattern the learner has used.
#   week 20   the RangeError `fix` (a recursion with no floor)
#   week 21   fib's 15 / 177 / 1973 calls, and "the recursion stack is space"
#   week 22   binary search — rewritten recursively in lesson 2
#   week 24   merge sort and quicksort: divide and conquer, and quicksort's
#             depth-n worst case
#
# ---------------------------------------------------------------------------
# THREE TYPESCRIPT FACTS THE WEEK IS BUILT ON, all verified against the checker:
#
#   TS7023  a recursive function with NO return annotation — its return type
#           depends on itself, so inference gives up and calls it `any`. The
#           rule "annotate recursive functions" is taught through the error.
#   TS2366  the forgotten `return` on the recursive branch: the call happens,
#           its value is thrown away, and the function falls off the end.
#   A recursive TYPE — `type Nested = number | readonly Nested[]` — is legal,
#           and a `// @ts-expect-error` line in a `_design` harness proves the
#           learner's type rejects `[1, "two"]` (an `any` would make that
#           directive unused, which is itself an error, TS2578).
#
# ---------------------------------------------------------------------------
# THE ONE RUNTIME FACT: a 100,000-deep recursion over a linked list dies with
# `RangeError: Maximum call stack size exceeded` on the judge's Node — verified.
# The exact frame limit is NOT printed anywhere (it varies with frame size and
# engine flags); only "a loop survives where the recursion did not" is, which is
# the same on every machine. Week 17's determinism rule, applied to the stack.
#
# The month-7 idiom continues month 6's: backtracking exercises print the number
# of calls (nodes visited), so "pruning helps" is a count, not a claim.
# ---------------------------------------------------------------------------

_LIST100K = (
    'interface N {\n'
    '  readonly value: number;\n'
    '  readonly next: N | null;\n}\n'
    'let head: N | null = null;\n'
    'for (let i = 0; i < 100000; i = i + 1) {\n'
    '  head = { value: i, next: head };\n}\n'
)

_NESTED = 'type Nested = number | readonly Nested[];\n'

_TOTAL = (
    'function total(x: Nested): number {\n'
    '  if (typeof x === "number") {\n'
    '    return x;\n  }\n'
    '  let s = 0;\n'
    '  for (const item of x) {\n'
    '    s = s + total(item);\n  }\n'
    '  return s;\n}\n'
)

_QUEENS = (
    'function queens(n: number): number {\n'
    '  const cols = new Set<number>();\n'
    '  const d1 = new Set<number>();\n'
    '  const d2 = new Set<number>();\n'
    '  let count = 0;\n'
    '  function place(r: number): void {\n'
    '    if (r === n) {\n'
    '      count = count + 1;\n'
    '      return;\n    }\n'
    '    for (let c = 0; c < n; c = c + 1) {\n'
    '      if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) {\n'
    '        continue;\n      }\n'
    '      cols.add(c);\n'
    '      d1.add(r + c);\n'
    '      d2.add(r - c);\n'
    '      place(r + 1);\n'
    '      cols.delete(c);\n'
    '      d1.delete(r + c);\n'
    '      d2.delete(r - c);\n    }\n  }\n'
    '  place(0);\n'
    '  return count;\n}\n'
)


# --- Week 25 --------------------------------------------------------------
_WEEKS.append(_week(
    25, 7, _M7,
    "Recursion & Backtracking",
    "You have been recursing over trees since week 20. Here is the whole story — the call stack, its limit, turning recursion into a loop — and then backtracking: choose, explore, un-choose, and prune.",
    """
You have been recursing since week 20. `depth(t)` called itself on each child;
the base case was the `null` the type told you about. This week is the rest of
the story.

## What you already did without naming it

Week 20's `pathTo` looked for a category, and when a subtree did not contain it,
returned `null` so the caller could **try the next child**. That is
**backtracking**: go down a path, and when it fails, back up and try another. By
lesson 7 you will have written it a dozen times on purpose.

## The plan

1. **The call stack** — what a frame holds, and why "on the way down" and "on the
   way back up" print in opposite orders.
2. **Designing a recursion** — the smallest case, the smaller problem, the
   combination — and recursive *types*, which TypeScript is happy to express.
3. **Depth** — the stack runs out, and every recursion can become a loop.
4. **Subsets**, 5. **permutations** — generating every possibility.
6. **Pruning** — generating fewer, and counting how many fewer.
7. **Recognising it** — and where it stops being enough (week 26).

## Counted, as in month 6

Backtracking is exponential by nature — 2ⁿ subsets, n! permutations — so every
generator this week reports **how many calls** it made. Pruning then shows up as a
smaller number, not as an adjective.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say what a stack frame holds, and trace a recursion's calls and returns",
        "Predict whether work before or after the recursive call runs first",
        "Annotate a recursive function's return type, and say why TypeScript needs it",
        "Design a recursion from its base case, its smaller problem and its combination",
        "Write and recurse over a recursive type",
        "Say why deep recursion fails, and rewrite a recursion as a loop",
        "Generate every subset with choose / explore / un-choose",
        "Generate permutations, and skip duplicates on sorted input",
        "Copy a path before storing it, and say what goes wrong if you do not",
        "Prune a search, and show with a count how much it saved",
        "Solve N-Queens with sets of attacked columns and diagonals",
        "Recognise a backtracking problem, and one that needs memoisation instead",
    ],
    why="Backtracking is how you answer every 'find all …' question in an interview — subsets, permutations, combinations, placements, paths — and it is one template with small variations. Understanding the call stack underneath it is what lets you debug it, bound its depth, and know when to turn it into a loop. And seeing the same subproblem solved twice is exactly the doorway into next week's dynamic programming.",
    est_minutes=480,
    glossary=[
        _gloss("recursion", "A function that solves a problem by calling itself on a smaller version of it."),
        _gloss("base case", "The input small enough to answer directly. Every recursion needs one it will reach."),
        _gloss("stack frame", "One call's own parameters, locals and return point. Every pending call has one."),
        _gloss("call stack", "The frames of every call that has started and not yet returned."),
        _gloss("unwinding", "Returning back up through the frames — where 'after the call' code runs."),
        _gloss("RangeError", "What Node throws when the call stack runs out: 'Maximum call stack size exceeded'."),
        _gloss("accumulator", "A parameter that carries the answer-so-far down, so nothing is left to do on the way up."),
        _gloss("explicit stack", "An array used as a stack to replace recursion with a loop."),
        _gloss("recursive type", "A type that mentions itself: type Nested = number | readonly Nested[]."),
        _gloss("backtracking", "Build a candidate step by step; when a step cannot work, undo it and try the next."),
        _gloss("choose / explore / un-choose", "push, recurse, pop — the whole template."),
        _gloss("decision tree", "The tree of choices a backtracking search walks. Its leaves are the candidates."),
        _gloss("pruning", "Refusing to explore a branch that cannot lead to an answer."),
        _gloss("nodes visited", "How many calls the search made. The honest measure of a backtracking cost."),
        _gloss("memoisation", "Remember each subproblem's answer so it is computed once. Week 26's subject."),
    ],
    cheatsheet="""
```ts
// ---- a recursion: base case, smaller problem, combine --------------------
function sum(xs: readonly number[]): number {        // ANNOTATE: else TS7023
  if (xs.length === 0) { return 0; }                   // the base case
  return (xs[0] ?? 0) + sum(xs.slice(1));              // RETURN it: else TS2366
}

// before the call runs on the way DOWN, after the call on the way back UP
function down(n: number): void { if (n === 0) { return; } console.log(n); down(n - 1); }  // 3 2 1
function up(n: number): void   { if (n === 0) { return; } up(n - 1); console.log(n); }    // 1 2 3

// ---- a recursive type ---------------------------------------------------
type Nested = number | readonly Nested[];

// ---- too deep: ~10k frames is typical; 100k is a RangeError ---------------
// accumulator form -> a loop
let acc = 0;
while (n > 0) { acc = acc + n; n = n - 1; }
// or an explicit stack (week 18) for anything branching
const stack: Nested[] = [data];
while (stack.length > 0) { const top = stack.pop(); /* … push its children … */ }

// ---- backtracking: choose, explore, un-choose ----------------------------
const path: number[] = [];
const out: number[][] = [];
function go(start: number): void {
  out.push([...path]);                          // COPY — `path` keeps changing
  for (let j = start; j < xs.length; j = j + 1) {
    path.push(xs[j] ?? 0);                      // choose
    go(j + 1);                                  // explore
    path.pop();                                 // un-choose
  }
}

// ---- permutations: a `used` flag per element ----------------------------
if (used[i]) { continue; }
used[i] = true; path.push(x); go(); path.pop(); used[i] = false;

// duplicates: SORT first, then skip an equal value whose twin is unused
if (i > 0 && xs[i] === xs[i - 1] && !used[i - 1]) { continue; }

// ---- pruning on sorted input ---------------------------------------------
if (sum + x > target) { break; }                // everything after is bigger too

// ---- N-Queens: attacked columns and diagonals as Sets --------------------
if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) { continue; }
```

| generates | count | calls (no pruning) |
|---|---|---|
| subsets of n | 2ⁿ | 2ⁿ⁺¹ - 1 |
| permutations of n | n! | about e·n! |
| combinations n choose k | n!/(k!(n-k)!) | fewer, with a `start` index |
""",
    self_check=[
        "Can you say what a stack frame holds?",
        "Can you predict the output order of code before and after a recursive call?",
        "Can you say why TypeScript needs a recursive function's return type written down?",
        "Can you name the base case, the smaller problem and the combination of a recursion?",
        "Can you write a recursive type and a function that walks it?",
        "Can you say roughly how deep Node will recurse, and why you should not rely on a number?",
        "Can you turn an accumulator recursion into a while loop?",
        "Can you replace a branching recursion with an explicit stack?",
        "Can you write the subsets template from memory?",
        "Can you say why `out.push(path)` without a copy prints empty arrays?",
        "Can you generate permutations without duplicates?",
        "Can you prune a combination search, and say why it needs sorted input?",
        "Can you place N queens using three Sets?",
        "Can you tell a 'find all' problem from a 'how many ways' one?",
    ],
    review=[
        _q("A stack frame holds…",
           ["the whole program", "one call's parameters, locals and where to return", "the heap",
            "only the return value"], 1,
           "One per pending call."),
        _q("Code AFTER the recursive call runs…",
           ["first", "on the way back up, in reverse order of the calls", "never", "in parallel"], 1,
           "Which is why countUp prints 1 2 3."),
        _q("TS7023 on a recursive function means…",
           ["infinite recursion", "its return type depends on itself — annotate it", "a missing base case",
            "a type error in the body"], 1,
           "Write `: number` and it goes away."),
        _q("TS2366 on a recursive function usually means…",
           ["no base case", "the recursive branch computes a value and forgets to return it",
            "wrong parameter", "too deep"], 1,
           "The call happens; its answer is thrown away."),
        _q("A 100,000-deep recursion in Node…",
           ["works", "throws RangeError: Maximum call stack size exceeded", "is slow", "is a type error"], 1,
           "The stack is finite; a loop is not limited that way."),
        _q("Any recursion can be turned into a loop with…",
           ["a Map", "an explicit stack", "a Set", "a sort"], 1,
           "It is doing what the call stack did."),
        _q("The backtracking template is…",
           ["sort, search, stop", "choose, explore, un-choose", "split, recurse, merge", "push, push, pop"], 1,
           "push, recurse, pop."),
        _q("`out.push(path)` instead of `out.push([...path])` gives…",
           ["the right answer", "every entry is the SAME array — empty by the end", "a type error",
            "duplicates"], 1,
           "One array, pushed many times, emptied by the un-chooses."),
        _q("The subsets of n elements number…",
           ["n", "n²", "2ⁿ", "n!"], 2,
           "Each element is in or out."),
        _q("The permutations of n distinct elements number…",
           ["2ⁿ", "n!", "n²", "n"], 1,
           "4! = 24."),
        _q("Skipping duplicate permutations needs the input…",
           ["reversed", "sorted, so equal values are adjacent", "unique", "in a Set"], 1,
           "Week 24 pays off."),
        _q("`if (sum + x > target) break;` is only correct when…",
           ["always", "the candidates are sorted ascending", "the target is positive", "there are no duplicates"], 1,
           "Otherwise a smaller value later is skipped."),
        _q("N-Queens tracks the two diagonals by…",
           ["row", "r + c and r - c", "c only", "a 2-D array"], 1,
           "Each is constant along one diagonal."),
        _q("\"How many ways…\" with repeated subproblems points at…",
           ["more backtracking", "memoisation — week 26", "sorting", "a heap"], 1,
           "Backtracking lists; DP counts."),
    ],
    milestone="Interview rep #25 — every combination that sums to a target, each candidate used once, duplicates in the input but never in the output. Sorted input makes the pruning legal and the duplicate skip possible, and the report counts the calls the search made — so the effect of both is a number on the page, not a claim.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w25-stack", "The call stack",
            "You have been recursing since week 20. Here is what was happening underneath.",
            """
Week 20's `depth(t)` called itself on each child and it worked. Here is *how*.

## One frame per call

Every call gets a **stack frame**: its own parameters, its own local variables,
and a note of where to return to. A recursive call does not overwrite the
caller's `n` — it gets a new frame with a new `n`, stacked on top. When it
returns, its frame is thrown away and the caller carries on with its own `n`
untouched.

```ts
function down(n: number, depth: number): void {
  const pad = "  ".repeat(depth);
  console.log(`${pad}enter ${n}`);
  if (n > 0) { down(n - 1, depth + 1); }
  console.log(`${pad}leave ${n}`);
}
```

`down(2, 0)`:

```
enter 2
  enter 1
    enter 0
    leave 0
  leave 1
leave 2
```

The indentation *is* the stack: three frames alive at the deepest point, and
they leave in the reverse of the order they arrived. Week 18 called that LIFO.

## Before the call, after the call

Everything before the recursive call runs **on the way down**; everything after
it runs **on the way back up**:

```ts
function countDown(n: number): void { if (n === 0) { return; } console.log(n); countDown(n - 1); }  // 3 2 1
function countUp(n: number): void   { if (n === 0) { return; } countUp(n - 1); console.log(n); }    // 1 2 3
```

Same calls, opposite order. Week 20's traversals are this exactly: pre-order does
its work before recursing, post-order after.

## Returning values

A value comes back up the same way. `fact(4)` cannot finish until `fact(3)` has,
so the **first** result computed is `fact(1)`, and each frame multiplies on the
way back:

```
fact(1)=1  fact(2)=2  fact(3)=6  fact(4)=24
```

## The mistake the compiler catches

```ts
function sumTo(n: number): number {
  if (n === 0) { return 0; }
  n + sumTo(n - 1);                       // computed... and thrown away
}
```

```
TS2366: Function lacks ending return statement and return type does not
        include 'undefined'.
```

The recursive call happens, its answer is discarded, and the function falls off
the end. Without the `: number` annotation this would *run* and print
`undefined` — the annotation is what turns a silent bug into an error.

> ⚠️ **Common mistakes:** forgetting to `return` the recursive result; expecting
> code after the call to run before the deeper calls; and thinking the callee
> can change the caller's local variables.
""",
            warmup=[
                _q("A recursive call's `n`…",
                   ["overwrites the caller's", "is a new variable in a new frame", "is global", "is shared"], 1,
                   "Each frame has its own."),
                _q("Frames leave the stack…",
                   ["in the order they arrived", "in reverse order — last in, first out", "all at once",
                    "randomly"], 1,
                   "Week 18's LIFO."),
                _q("`countUp(3)` prints its numbers after the recursive call, so it prints…",
                   ["3 2 1", "1 2 3", "3 only", "nothing"], 1,
                   "The deepest call prints first."),
                _q("The first `fact` call to FINISH is…",
                   ["fact(4)", "fact(1)", "fact(2)", "all together"], 1,
                   "Everything above it is waiting on it."),
            ],
            exercises=[
                _ex("tscourse-w25-st-1", "Watch the frames",
                    "Recurse one level deeper, one indent further in.",
                    _LINE +
                    'function down(n: number, depth: number): void {\n'
                    '  const pad = "  ".repeat(depth);\n'
                    '  console.log(`${pad}enter ${n}`);\n'
                    '  if (n > 0) {\n'
                    '    down(n - 1, depth + 1);\n  }\n'
                    '  console.log(`${pad}leave ${n}`);\n}\n'
                    'down(Number(line), 0);\n',
                    '    down(n - 1, depth + 1);',
                    [("2", "enter 2\n  enter 1\n    enter 0\n    leave 0\n  leave 1\nleave 2"),
                     ("0", "enter 0\nleave 0")],
                    hints=["A smaller n, one level deeper.",
                           "Write down(n - 1, depth + 1);"],
                    difficulty="Easy"),
                _ex("tscourse-w25-st-2", "On the way back up",
                    "Print 1 to n by doing the printing AFTER the recursive call.",
                    _LINE +
                    'function countUp(n: number): void {\n'
                    '  if (n === 0) {\n'
                    '    return;\n  }\n'
                    '  countUp(n - 1);\n'
                    '  console.log(n);\n}\n'
                    'countUp(Number(line));\n',
                    '  countUp(n - 1);',
                    [("3", "1\n2\n3"), ("1", "1")],
                    hints=["Everything smaller has to be printed before n is.",
                           "Write countUp(n - 1); above the print."],
                    difficulty="Easy"),
                _ex("tscourse-w25-st-3", "How many frames at once",
                    "Track how many calls are alive, and the most there ever were.",
                    _LINE +
                    'let live = 0;\n'
                    'let deepest = 0;\n'
                    'function sumTo(n: number): number {\n'
                    '  live = live + 1;\n'
                    '  deepest = Math.max(deepest, live);\n'
                    '  const result = n === 0 ? 0 : n + sumTo(n - 1);\n'
                    '  live = live - 1;\n'
                    '  return result;\n}\n'
                    'const total = sumTo(Number(line));\n'
                    'console.log(`total=${total} deepest=${deepest} live=${live}`);\n',
                    '  live = live - 1;',
                    [("5", "total=15 deepest=6 live=0"), ("0", "total=0 deepest=1 live=0")],
                    hints=["A frame ends when its call returns.",
                           "Write live = live - 1; just before the return.",
                           "sumTo(5) has six frames at its deepest: 5, 4, 3, 2, 1 and 0."],
                    difficulty="Medium"),
                _ex("tscourse-w25-st-4", "Values come back up",
                    "Compute each factorial from the one below it, printing as each call finishes.",
                    _LINE +
                    'function fact(n: number): number {\n'
                    '  const result = n <= 1 ? 1 : n * fact(n - 1);\n'
                    '  console.log(`fact(${n})=${result}`);\n'
                    '  return result;\n}\n'
                    'fact(Number(line));\n',
                    '  const result = n <= 1 ? 1 : n * fact(n - 1);',
                    [("4", "fact(1)=1\nfact(2)=2\nfact(3)=6\nfact(4)=24"), ("1", "fact(1)=1")],
                    hints=["The base case is n <= 1; otherwise it is n times the factorial below.",
                           "Write const result = n <= 1 ? 1 : n * fact(n - 1);"],
                    difficulty="Easy"),
                _diagnose("tscourse-w25-st-d1", "The answer that was thrown away",
                          "TS2366: Function lacks ending return statement and return type does not include 'undefined'.",
                          'function sumTo(n: number): number {\n'
                          '  if (n === 0) {\n'
                          '    return 0;\n  }\n'
                          '  n + sumTo(n - 1);\n}\n'
                          'console.log(sumTo(3));\n',
                          'function sumTo(n: number): number {\n'
                          '  if (n === 0) {\n'
                          '    return 0;\n  }\n'
                          '  return n + sumTo(n - 1);\n}\n'
                          'console.log(sumTo(3));\n',
                          [("", "6")],
                          hints=["The last line computes a number. What happens to it?",
                                 "A recursive result has to be RETURNED to reach the caller.",
                                 "Write return n + sumTo(n - 1);"],
                          difficulty="Easy"),
                _fix("tscourse-w25-st-fix1", "Fix the countdown that counts up",
                     "This should print `3 2 1` for 3 and prints `1 2 3`: the print sits AFTER the recursive call, so it runs on the way back up, deepest call first.",
                     _LINE +
                     'function countDown(n: number): void {\n'
                     '  if (n === 0) {\n'
                     '    return;\n  }\n'
                     '  countDown(n - 1);\n'
                     '  console.log(n);\n}\n'
                     'countDown(Number(line));\n',
                     _LINE +
                     'function countDown(n: number): void {\n'
                     '  if (n === 0) {\n'
                     '    return;\n  }\n'
                     '  console.log(n);\n'
                     '  countDown(n - 1);\n}\n'
                     'countDown(Number(line));\n',
                     [("3", "3\n2\n1"), ("2", "2\n1")],
                     hints=["Which runs first: the code before the call, or the code after it?",
                            "To print n before the smaller numbers, print on the way DOWN.",
                            "Move console.log(n) above the recursive call."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Pre-order and post-order traversals (week 20) differ in…",
                   ["the tree", "whether the work is before or after the recursive calls", "speed", "the base case"], 1,
                   "Down versus back up."),
                _q("Without `: number`, the TS2366 program would…",
                   ["crash", "run and print undefined", "print 6", "loop for ever"], 1,
                   "The annotation turns a silent bug into an error."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w25-shape", "Designing a recursion",
            "Three questions, one leap of faith, and a type that refers to itself.",
            """
Every recursion answers three questions:

1. **What is the smallest input**, and its answer? (the base case)
2. **How do I make the problem smaller?** (it must *strictly* shrink)
3. **How do I build my answer from the smaller one?**

```ts
function sum(xs: readonly number[]): number {
  if (xs.length === 0) { return 0; }                  // 1. empty: 0
  return (xs[0] ?? 0) + sum(xs.slice(1));             // 2. the rest   3. add the first
}
```

## The leap of faith

Do not trace `sum` all the way down in your head. **Assume** `sum(xs.slice(1))`
returns the right total of the rest — then the only question is whether adding
`xs[0]` makes it the total of the whole. It does, and the base case is right, so
the function is right. That is induction, and it is the only way to write a
recursion over a tree of any size.

## Making it smaller, faster

Shrinking by one gives n calls. Shrinking by **half** gives log n:

```ts
function pow(x: number, n: number): number {
  if (n === 0) { return 1; }
  const half = pow(x, Math.floor(n / 2));             // ONE call, reused
  return n % 2 === 0 ? half * half : half * half * x;
}
```

`pow(2, 10)` makes **5** calls (10, 5, 2, 1, 0) where the obvious version makes
11; `pow(2, 30)` makes 6. And `half` is computed once and used twice — calling
`pow` twice instead would quietly make it linear again.

Binary search (week 22) has the same shape and is often written recursively:
check the middle, recurse into one half.

## TypeScript wants the return type

```ts
function sumTo(n: number) {                           // no annotation
  if (n === 0) { return 0; }
  return n + sumTo(n - 1);
}
```

```
TS7023: 'sumTo' implicitly has return type 'any' because it does not have a
        return type annotation and is referenced directly or indirectly in one
        of its return expressions.
```

To infer `sumTo`'s return type the compiler needs `sumTo`'s return type. It
refuses to guess. **Annotate every recursive function** — you would want to
anyway, since the annotation is also what caught TS2366 in lesson 1.

## Recursive types

A type can refer to itself too, and it is the natural description of any nested
data:

```ts
type Nested = number | readonly Nested[];
const data: Nested = [1, [2, [3, 4]], 5];
```

A function over it follows the type exactly — one branch per member of the union,
and the recursion happens precisely where the type recurses:

```ts
function total(x: Nested): number {
  if (typeof x === "number") { return x; }            // the base case IS the non-recursive member
  let s = 0;
  for (const item of x) { s = s + total(item); }
  return s;
}
```

Week 20's `T | null` tree was exactly this, with `null` as the base case.

> ⚠️ **Common mistakes:** a "smaller" problem that is not smaller (`n + 1`,
> or a slice that includes everything); calling the recursion twice when once
> would do; and leaving the return type to inference.
""",
            warmup=[
                _q("The three questions of a recursion are…",
                   ["loop, test, return", "smallest case, how to shrink, how to combine", "input, output, type",
                    "push, recurse, pop"], 1,
                   "Answer all three and it is written."),
                _q("The leap of faith means…",
                   ["guess", "assume the smaller call is right, and check only this level", "trace every call",
                    "skip the base case"], 1,
                   "Induction."),
                _q("Halving the problem each call gives…",
                   ["n calls", "about log n calls", "2ⁿ calls", "n² calls"], 1,
                   "pow(2, 30) makes 6."),
                _q("TS7023 is fixed by…",
                   ["a base case", "annotating the return type", "a loop", "`any`"], 1,
                   "The compiler will not guess a type that depends on itself."),
            ],
            exercises=[
                _ex("tscourse-w25-sh-1", "The first, plus the rest",
                    "Sum an array recursively: the first element plus the sum of the others.",
                    _NUMS +
                    'function sum(xs: readonly number[]): number {\n'
                    '  if (xs.length === 0) {\n'
                    '    return 0;\n  }\n'
                    '  return (xs[0] ?? 0) + sum(xs.slice(1));\n}\n'
                    'console.log(sum(nums));\n',
                    '  return (xs[0] ?? 0) + sum(xs.slice(1));',
                    [("1 2 3 4", "10"), ("7", "7")],
                    hints=["`xs.slice(1)` is everything but the first element — strictly smaller.",
                           "Write return (xs[0] ?? 0) + sum(xs.slice(1));"],
                    difficulty="Easy"),
                _ex("tscourse-w25-sh-2", "The smallest palindrome",
                    "A string of length 0 or 1 is a palindrome. Say so.",
                    _LINE +
                    'function isPal(s: string): boolean {\n'
                    '  if (s.length <= 1) {\n'
                    '    return true;\n  }\n'
                    '  return s.charAt(0) === s.charAt(s.length - 1) && isPal(s.slice(1, -1));\n}\n'
                    'console.log(isPal(line));\n',
                    '  if (s.length <= 1) {\n'
                    '    return true;\n  }',
                    [("racecar", "true"), ("abca", "false"), ("abba", "true")],
                    hints=["Both an even and an odd length eventually shrink to 0 or 1 characters.",
                           "Return true when s.length <= 1."],
                    difficulty="Easy"),
                _ex("tscourse-w25-sh-3", "Halve it",
                    "Compute a power with one recursive call on half the exponent, and count the calls.",
                    _LINE +
                    'let calls = 0;\n'
                    'function pow(x: number, n: number): number {\n'
                    '  calls = calls + 1;\n'
                    '  if (n === 0) {\n'
                    '    return 1;\n  }\n'
                    '  const half = pow(x, Math.floor(n / 2));\n'
                    '  return n % 2 === 0 ? half * half : half * half * x;\n}\n'
                    'const n = Number(line);\n'
                    'console.log(`${pow(2, n)} calls=${calls}`);\n',
                    '  const half = pow(x, Math.floor(n / 2));',
                    [("10", "1024 calls=5"), ("30", "1073741824 calls=6"), ("0", "1 calls=1")],
                    hints=["x^n is (x^(n/2))², times one more x when n is odd.",
                           "Write const half = pow(x, Math.floor(n / 2));"],
                    difficulty="Medium"),
                _ex("tscourse-w25-sh-4", "Recurse where the type recurses",
                    "Total a nested list: a number is itself, a list is the total of its items.",
                    _NESTED + _TOTAL +
                    'const data: Nested = [1, [2, [3, 4]], 5];\n'
                    'console.log(total(data));\n',
                    '    s = s + total(item);',
                    [("", "15")],
                    hints=["Each item is itself a Nested — a number or another list.",
                           "Write s = s + total(item);"],
                    difficulty="Medium"),
                _design("tscourse-w25-sh-des1", "Design the nested type",
                        "The function below walks a value that is either a number or a read-only list of "
                        "such values, nested to any depth. Write the type. The checker also confirms it "
                        "REJECTS `[1, \"two\"]` — so `any` will not do.",
                        _NESTED + _TOTAL +
                        'const data: Nested = [1, [2, [3, [4]]]];\n'
                        'console.log(total(data));\n',
                        'type Nested = number | readonly Nested[];',
                        'const _ok1: Nested = 5;\n'
                        'const _ok2: Nested = [1, [2, [3, [4]]]];\n'
                        '// @ts-expect-error — a string is not a Nested\n'
                        'const _bad: Nested = [1, "two"];\n',
                        [("", "10")],
                        hints=["It is a union of two members, and one of them mentions the type itself.",
                               "The list is read-only — `total` never changes it.",
                               "type Nested = number | readonly Nested[];"],
                        difficulty="Medium"),
                _ex("tscourse-w25-sh-5", "Binary search, recursively",
                    "Recurse into whichever half can still hold the target.",
                    _NUMS +
                    'function find(xs: readonly number[], target: number, lo: number, hi: number): number {\n'
                    '  if (lo > hi) {\n'
                    '    return -1;\n  }\n'
                    '  const mid = Math.floor((lo + hi) / 2);\n'
                    '  const v = xs[mid] ?? 0;\n'
                    '  if (v === target) {\n'
                    '    return mid;\n  }\n'
                    '  return v < target ? find(xs, target, mid + 1, hi) : find(xs, target, lo, mid - 1);\n}\n'
                    'console.log(find(nums, 7, 0, nums.length - 1));\n',
                    '  return v < target ? find(xs, target, mid + 1, hi) : find(xs, target, lo, mid - 1);',
                    [("1 3 5 7 9", "3"), ("2 4", "-1"), ("7", "0")],
                    hints=["If the middle is too small, the target is to its right — and vice versa.",
                           "Week 22's inclusive row: mid + 1 and mid - 1.",
                           "Write return v < target ? find(xs, target, mid + 1, hi) : find(xs, target, lo, mid - 1);"],
                    difficulty="Medium"),
                _diagnose("tscourse-w25-sh-d1", "The return type that depends on itself",
                          "TS7023: 'sumTo' implicitly has return type 'any' because it does not have a return type annotation and is referenced directly or indirectly in one of its return expressions.",
                          _LINE +
                          'function sumTo(n: number) {\n'
                          '  if (n === 0) {\n'
                          '    return 0;\n  }\n'
                          '  return n + sumTo(n - 1);\n}\n'
                          'console.log(sumTo(Number(line)));\n',
                          _LINE +
                          'function sumTo(n: number): number {\n'
                          '  if (n === 0) {\n'
                          '    return 0;\n  }\n'
                          '  return n + sumTo(n - 1);\n}\n'
                          'console.log(sumTo(Number(line)));\n',
                          [("3", "6"), ("0", "0")],
                          hints=["To infer what sumTo returns, the compiler would need to know what sumTo returns.",
                                 "Tell it.",
                                 "Write function sumTo(n: number): number {"],
                          difficulty="Easy"),
                _fix("tscourse-w25-sh-fix1", "Fix the problem that grows",
                     "This dies with `RangeError: Maximum call stack size exceeded` for any positive input. The base case is 0, and the recursive call is on `n + 1` — moving AWAY from it.",
                     _LINE +
                     'function sumTo(n: number): number {\n'
                     '  if (n === 0) {\n'
                     '    return 0;\n  }\n'
                     '  return n + sumTo(n + 1);\n}\n'
                     'console.log(sumTo(Number(line)));\n',
                     _LINE +
                     'function sumTo(n: number): number {\n'
                     '  if (n === 0) {\n'
                     '    return 0;\n  }\n'
                     '  return n + sumTo(n - 1);\n}\n'
                     'console.log(sumTo(Number(line)));\n',
                     [("3", "6"), ("4", "10")],
                     hints=["Ask question 2: is the recursive call's problem smaller?",
                            "It has to move TOWARDS the base case, every time.",
                            "Write sumTo(n - 1)."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why is `half` computed once and used twice in `pow`?",
                   ["style", "calling pow twice would double the calls at every level — linear again",
                    "types", "it is required"], 1,
                   "Two calls on n/2 is n calls in total."),
                _q("In `total(x: Nested)`, the base case corresponds to…",
                   ["the list", "the non-recursive member of the union — `number`", "an empty list", "nothing"], 1,
                   "The function follows the type."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w25-loops", "Depth, and turning recursion into a loop",
            "The stack is finite. A loop is not limited the same way.",
            """
Every pending call holds a frame, and the call stack has a fixed size. Go deep
enough and Node stops you:

```
RangeError: Maximum call stack size exceeded
```

Week 21 said a recursion's depth **is** space. Here is where the space runs out.

## How deep is too deep

Typically around ten thousand frames — but **do not rely on a number.** It
depends on how big each frame is, the engine and its flags. What you can rely
on: a recursion whose depth grows with the input will fail on *some* input. A
tree of a thousand nodes is fine because its depth is about log n; a **linked list
of 100,000 nodes** recursed over one node per call is 100,000 frames, and it
fails (verified).

Balanced structures are safe; **long chains are not** — a linked list, a
degenerate BST (week 20), quicksort on sorted input (week 24).

## Accumulators: nothing left to do on the way up

```ts
function sumTo(n: number, acc: number): number {
  if (n === 0) { return acc; }
  return sumTo(n - 1, acc + n);           // the call is the LAST thing
}
```

The answer travels **down** in `acc`, so after the recursive call there is
nothing left to do. Some languages turn that into a loop for you (tail-call
optimisation); **JavaScript engines do not**, so you do it yourself — and the
accumulator form makes it mechanical:

```ts
let acc = 0;
while (n > 0) { acc = acc + n; n = n - 1; }
```

The parameters become variables; the recursive call becomes the next iteration.

## Branching recursion: an explicit stack

When a call makes *several* recursive calls (a tree, a nested list), there is no
single accumulator. Do what the call stack was doing, with an array (week 18):

```ts
const stack: Nested[] = [data];
while (stack.length > 0) {
  const top = stack.pop();
  if (top === undefined) { continue; }
  if (typeof top === "number") { total = total + top; }
  else { for (const item of top) { stack.push(item); } }
}
```

Week 20 did exactly this for its traversals, and pushed the **right** child before
the left so the left would come off first.

## When to bother

Recursion is clearer for trees and backtracking, and the depth there is modest.
Convert when **the depth grows with n** and n can be large. That is a design
decision, not an optimisation.

> ⚠️ **Common mistakes:** recursing once per element of a long list; assuming
> the engine eliminates tail calls; and pushing children in the wrong order
> when the traversal order matters.
""",
            warmup=[
                _q("A recursion over a 100,000-node linked list…",
                   ["is fine", "exhausts the call stack", "is O(1)", "is a type error"], 1,
                   "One frame per node."),
                _q("A balanced tree of a million nodes, recursed over, reaches a depth of about…",
                   ["a million", "20", "1,000", "2"], 1,
                   "log2 of a million."),
                _q("JavaScript engines eliminate tail calls…",
                   ["always", "no — you convert to a loop yourself", "in strict mode", "for arrow functions"], 1,
                   "Which is why the accumulator form matters."),
                _q("A branching recursion becomes a loop with…",
                   ["an accumulator", "an explicit stack", "a Set", "a counter"], 1,
                   "Doing the call stack's job by hand."),
            ],
            exercises=[
                _ex("tscourse-w25-lp-1", "Carry the answer down",
                    "Pass the total so far into the next call, so nothing is left to do on the way up.",
                    _LINE +
                    'function sumTo(n: number, acc: number): number {\n'
                    '  if (n === 0) {\n'
                    '    return acc;\n  }\n'
                    '  return sumTo(n - 1, acc + n);\n}\n'
                    'console.log(sumTo(Number(line), 0));\n',
                    '  return sumTo(n - 1, acc + n);',
                    [("4", "10"), ("0", "0")],
                    hints=["The smaller problem, with n added to the accumulator.",
                           "Write return sumTo(n - 1, acc + n);"],
                    difficulty="Easy"),
                _ex("tscourse-w25-lp-2", "The same thing, as a loop",
                    "Turn the accumulator recursion into a while loop — and use a depth no recursion would survive.",
                    _LINE +
                    'let n = Number(line);\n'
                    'let acc = 0;\n'
                    'while (n > 0) {\n'
                    '  acc = acc + n;\n'
                    '  n = n - 1;\n}\n'
                    'console.log(acc);\n',
                    '  acc = acc + n;\n'
                    '  n = n - 1;',
                    [("100000", "5000050000"), ("4", "10")],
                    hints=["The parameters become variables; the recursive call becomes the next iteration.",
                           "acc = acc + n; then n = n - 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w25-lp-3", "An explicit stack",
                    "Total a nested list without recursion: push a list's items, add a number.",
                    _NESTED +
                    'const data: Nested = [1, [2, [3, [4, [5]]]], 6];\n'
                    'let total = 0;\n'
                    'const stack: Nested[] = [data];\n'
                    'while (stack.length > 0) {\n'
                    '  const top = stack.pop();\n'
                    '  if (top === undefined) {\n'
                    '    continue;\n  }\n'
                    '  if (typeof top === "number") {\n'
                    '    total = total + top;\n'
                    '  } else {\n'
                    '    for (const item of top) {\n'
                    '      stack.push(item);\n    }\n  }\n}\n'
                    'console.log(total);\n',
                    '    for (const item of top) {\n'
                    '      stack.push(item);\n    }',
                    [("", "21")],
                    hints=["A list's items still need processing — put them on the stack.",
                           "Loop over `top` and push each item."],
                    difficulty="Medium"),
                _ex("tscourse-w25-lp-4", "A long list, walked with a loop",
                    "Count 100,000 nodes with a cursor rather than a recursion.",
                    _LIST100K +
                    'let count = 0;\n'
                    'let cur: N | null = head;\n'
                    'while (cur !== null) {\n'
                    '  count = count + 1;\n'
                    '  cur = cur.next;\n}\n'
                    'console.log(count);\n',
                    '  cur = cur.next;',
                    [("", "100000")],
                    hints=["Move the cursor to the next node.",
                           "Write cur = cur.next;"],
                    difficulty="Easy"),
                _ex("tscourse-w25-lp-5", "Same order, no recursion",
                    "Pre-order a tree with an explicit stack, pushing the right child first so the left comes off first.",
                    'interface T {\n'
                    '  readonly value: number;\n'
                    '  readonly left: T | null;\n'
                    '  readonly right: T | null;\n}\n'
                    'function leaf(value: number): T {\n'
                    '  return { value, left: null, right: null };\n}\n'
                    'const tree: T = {\n'
                    '  value: 1,\n'
                    '  left: { value: 2, left: leaf(4), right: leaf(5) },\n'
                    '  right: leaf(3),\n};\n'
                    'function pre(t: T | null, out: number[]): void {\n'
                    '  if (t === null) {\n'
                    '    return;\n  }\n'
                    '  out.push(t.value);\n'
                    '  pre(t.left, out);\n'
                    '  pre(t.right, out);\n}\n'
                    'const viaCalls: number[] = [];\n'
                    'pre(tree, viaCalls);\n'
                    'const viaStack: number[] = [];\n'
                    'const stack: T[] = [tree];\n'
                    'while (stack.length > 0) {\n'
                    '  const t = stack.pop();\n'
                    '  if (t === undefined) {\n'
                    '    continue;\n  }\n'
                    '  viaStack.push(t.value);\n'
                    '  if (t.right !== null) {\n'
                    '    stack.push(t.right);\n  }\n'
                    '  if (t.left !== null) {\n'
                    '    stack.push(t.left);\n  }\n}\n'
                    'console.log(`${viaCalls.join(",")} ${viaStack.join(",")} same=${viaCalls.join(",") === viaStack.join(",")}`);\n',
                    '  if (t.right !== null) {\n'
                    '    stack.push(t.right);\n  }\n'
                    '  if (t.left !== null) {\n'
                    '    stack.push(t.left);\n  }',
                    [("", "1,2,4,5,3 1,2,4,5,3 same=true")],
                    hints=["A stack gives back the LAST thing pushed.",
                           "To visit left first, push it last: right, then left."],
                    difficulty="Medium"),
                _fix("tscourse-w25-lp-fix1", "Fix the recursion that ran out of stack",
                     "This dies with `RangeError: Maximum call stack size exceeded`. `len` makes one call per node, and 100,000 nodes is 100,000 frames. The recursion is correct; the stack is simply not that deep. Walk the list with a loop instead.",
                     _LIST100K +
                     'function len(n: N | null): number {\n'
                     '  return n === null ? 0 : 1 + len(n.next);\n}\n'
                     'console.log(len(head));\n',
                     _LIST100K +
                     'function len(n: N | null): number {\n'
                     '  let count = 0;\n'
                     '  let cur = n;\n'
                     '  while (cur !== null) {\n'
                     '    count = count + 1;\n'
                     '    cur = cur.next;\n  }\n'
                     '  return count;\n}\n'
                     'console.log(len(head));\n',
                     [("", "100000")],
                     hints=["The depth of this recursion equals the length of the list.",
                            "A loop keeps one cursor, however long the list is.",
                            "Count with a while loop that follows `.next`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why not print 'the maximum recursion depth' as an exercise?",
                   ["it is secret", "it varies with frame size and engine, so the output would not be deterministic",
                    "it is always 10,000", "it is infinite"], 1,
                   "Week 17's rule, applied to the stack."),
                _q("Which of these is at risk of a stack overflow?",
                   ["a balanced BST of a million nodes", "quicksort (last pivot) on a large SORTED array",
                    "merge sort on a million elements", "binary search"], 1,
                   "Its depth is n, not log n."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w25-subsets", "Backtracking: every subset",
            "Choose, explore, un-choose.",
            """
"Every subset of `[1, 2, 3]`." For each element there are two choices — **in**
or **out** — and the choices form a tree:

```
                     []
            in 1 /         \\ out 1
             [1]              []
        in 2 /  \\        in 2 /  \\
        [1,2]   [1]        [2]    []
        ...
```

Eight leaves, one per subset. Walking that tree is **backtracking**.

## The template

```ts
const path: number[] = [];
function go(i: number): void {
  if (i === xs.length) {                     // a leaf: every element decided
    console.log(`[${path.join(",")}]`);
    return;
  }
  path.push(xs[i] ?? 0);                     // choose:  i is in
  go(i + 1);                                 // explore
  path.pop();                                // un-choose
  go(i + 1);                                 // explore:  i is out
}
```

**One** `path` array, shared by every call, is extended before each exploration
and restored after it. The `pop` is what makes the sibling branch start from the
same state its parent had — without it, choices from one branch leak into the next.

## Counting it

n elements, **2ⁿ** subsets, and the tree has **2ⁿ⁺¹ − 1** nodes (calls): 8
leaves and 15 calls for n = 3, 32 and 63 for n = 5. Exponential — add one element
and the work doubles. Backtracking is only ever feasible for small n (about 20),
which is exactly the range interview problems use.

## The loop form

Often cleaner, and the one that generalises to combinations:

```ts
function go(start: number): void {
  out.push([...path]);                       // every node is a subset
  for (let j = start; j < xs.length; j = j + 1) {
    path.push(xs[j] ?? 0);
    go(j + 1);                               // only LATER elements, so no repeats
    path.pop();
  }
}
```

`start` is what stops `[1,2]` and `[2,1]` both appearing: each call only
considers elements after the last one chosen. Stop when `path.length === k` and
you have **combinations** of size k.

## The copy

```ts
out.push([...path]);      // ✓ a snapshot
out.push(path);           // ✗ the SAME array, again and again
```

Push `path` itself and every entry of `out` is one array — which, after the last
`pop`, is empty. Eight subsets print as eight `[]`s. Week 13's aliasing, at its
most confusing.

## Lazily, with a generator

Week 20's `yield*` fits backtracking perfectly: `yield [...path]` at a leaf,
`yield*` into each branch, and the caller can stop after the first few without
the rest ever being generated.

> ⚠️ **Common mistakes:** forgetting the `pop`; storing `path` instead of a
> copy; and a loop that starts at 0 instead of `start`, generating every order.
""",
            warmup=[
                _q("The subsets of 4 elements number…",
                   ["4", "8", "16", "24"], 2,
                   "2⁴."),
                _q("`path.pop()` after exploring exists to…",
                   ["save memory", "restore the state for the sibling branch", "end the recursion",
                    "print"], 1,
                   "Un-choose."),
                _q("`out.push(path)` without a copy leaves `out` holding…",
                   ["the subsets", "the same array many times — empty at the end", "nothing", "copies"], 1,
                   "Aliasing."),
                _q("In the loop form, starting at `start` rather than 0 prevents…",
                   ["recursion", "the same set appearing in two orders", "empty sets", "duplicates in the input"], 1,
                   "Combinations, not arrangements."),
            ],
            exercises=[
                _ex("tscourse-w25-sb-1", "Un-choose",
                    "Undo the choice before exploring the branch without it.",
                    _NUMS +
                    'const path: number[] = [];\n'
                    'function go(i: number): void {\n'
                    '  if (i === nums.length) {\n'
                    '    console.log(`[${path.join(",")}]`);\n'
                    '    return;\n  }\n'
                    '  path.push(nums[i] ?? 0);\n'
                    '  go(i + 1);\n'
                    '  path.pop();\n'
                    '  go(i + 1);\n}\n'
                    'go(0);\n',
                    '  path.pop();',
                    [("1 2 3", "[1,2,3]\n[1,2]\n[1,3]\n[1]\n[2,3]\n[2]\n[3]\n[]"), ("7", "[7]\n[]")],
                    hints=["The branch without element i must start from the same path the caller had.",
                           "Write path.pop();"],
                    difficulty="Medium"),
                _ex("tscourse-w25-sb-2", "Count the tree",
                    "Count every call, and every leaf.",
                    _NUMS +
                    'let calls = 0;\n'
                    'let leaves = 0;\n'
                    'function go(i: number): void {\n'
                    '  calls = calls + 1;\n'
                    '  if (i === nums.length) {\n'
                    '    leaves = leaves + 1;\n'
                    '    return;\n  }\n'
                    '  go(i + 1);\n'
                    '  go(i + 1);\n}\n'
                    'go(0);\n'
                    'console.log(`leaves=${leaves} calls=${calls}`);\n',
                    '    leaves = leaves + 1;',
                    [("1 2 3", "leaves=8 calls=15"), ("1 2 3 4 5", "leaves=32 calls=63")],
                    hints=["A leaf is a call where every element has been decided.",
                           "Write leaves = leaves + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w25-sb-3", "Subsets that hit a target",
                    "Carry the running sum down, and count the leaves where it equals the target.",
                    _NUMS +
                    'const target = 10;\n'
                    'let found = 0;\n'
                    'function go(i: number, sum: number): void {\n'
                    '  if (i === nums.length) {\n'
                    '    if (sum === target) {\n'
                    '      found = found + 1;\n    }\n'
                    '    return;\n  }\n'
                    '  go(i + 1, sum + (nums[i] ?? 0));\n'
                    '  go(i + 1, sum);\n}\n'
                    'go(0, 0);\n'
                    'console.log(found);\n',
                    '    if (sum === target) {\n'
                    '      found = found + 1;\n    }',
                    [("2 3 5 7", "2"), ("10", "1"), ("1 2", "0")],
                    hints=["Only a complete decision — a leaf — is a subset.",
                           "Count it when its sum equals the target."],
                    difficulty="Medium"),
                _ex("tscourse-w25-sb-4", "Combinations of size two",
                    "Loop over the later elements: choose one, explore, un-choose.",
                    _NUMS +
                    'const k = 2;\n'
                    'const path: number[] = [];\n'
                    'function go(start: number): void {\n'
                    '  if (path.length === k) {\n'
                    '    console.log(path.join(","));\n'
                    '    return;\n  }\n'
                    '  for (let j = start; j < nums.length; j = j + 1) {\n'
                    '    path.push(nums[j] ?? 0);\n'
                    '    go(j + 1);\n'
                    '    path.pop();\n  }\n}\n'
                    'go(0);\n',
                    '    path.push(nums[j] ?? 0);\n'
                    '    go(j + 1);\n'
                    '    path.pop();',
                    [("1 2 3 4", "1,2\n1,3\n1,4\n2,3\n2,4\n3,4"), ("5 6", "5,6")],
                    hints=["Choose element j, then explore only the elements after it.",
                           "Push, recurse with j + 1, pop."],
                    difficulty="Medium"),
                _ex("tscourse-w25-sb-5", "Only as many as you need",
                    "Yield each subset from a generator, and stop after the first three.",
                    _NUMS +
                    'function* subsets(xs: readonly number[], i: number, path: number[]): Generator<readonly number[]> {\n'
                    '  if (i === xs.length) {\n'
                    '    yield [...path];\n'
                    '    return;\n  }\n'
                    '  path.push(xs[i] ?? 0);\n'
                    '  yield* subsets(xs, i + 1, path);\n'
                    '  path.pop();\n'
                    '  yield* subsets(xs, i + 1, path);\n}\n'
                    'let taken = 0;\n'
                    'for (const s of subsets(nums, 0, [])) {\n'
                    '  console.log(s.join(","));\n'
                    '  taken = taken + 1;\n'
                    '  if (taken === 3) {\n'
                    '    break;\n  }\n}\n',
                    '    yield [...path];',
                    [("1 2 3", "1,2,3\n1,2\n1,3"), ("4 5 6 7 8 9", "4,5,6,7,8,9\n4,5,6,7,8\n4,5,6,7,9")],
                    hints=["At a leaf, hand out a SNAPSHOT of the path.",
                           "Write yield [...path];"],
                    difficulty="Medium"),
                _fix("tscourse-w25-sb-fix1", "Fix the choice that was never undone",
                     "For `1 2` this prints `[1,2]`, `[1,2]`, `[1,2,2]`, `[1,2,2]` — the choices pile up, because nothing takes element i back out before the branch that is supposed to skip it.",
                     _NUMS +
                     'const path: number[] = [];\n'
                     'function go(i: number): void {\n'
                     '  if (i === nums.length) {\n'
                     '    console.log(`[${path.join(",")}]`);\n'
                     '    return;\n  }\n'
                     '  path.push(nums[i] ?? 0);\n'
                     '  go(i + 1);\n'
                     '  go(i + 1);\n}\n'
                     'go(0);\n',
                     _NUMS +
                     'const path: number[] = [];\n'
                     'function go(i: number): void {\n'
                     '  if (i === nums.length) {\n'
                     '    console.log(`[${path.join(",")}]`);\n'
                     '    return;\n  }\n'
                     '  path.push(nums[i] ?? 0);\n'
                     '  go(i + 1);\n'
                     '  path.pop();\n'
                     '  go(i + 1);\n}\n'
                     'go(0);\n',
                     [("1 2", "[1,2]\n[1]\n[2]\n[]"), ("5", "[5]\n[]")],
                     hints=["Choose, explore — and then?",
                            "The second exploration is the branch where element i is OUT.",
                            "Add path.pop(); between the two calls."],
                     difficulty="Easy"),
                _fix("tscourse-w25-sb-fix2", "Fix the subsets that all came out empty",
                     "This prints `[]` four times for `1 2`. Each leaf stores `path` itself — the one shared array — so `out` holds four references to it, and by the time they are printed every choice has been popped back off.",
                     _NUMS +
                     'const path: number[] = [];\n'
                     'const out: number[][] = [];\n'
                     'function go(i: number): void {\n'
                     '  if (i === nums.length) {\n'
                     '    out.push(path);\n'
                     '    return;\n  }\n'
                     '  path.push(nums[i] ?? 0);\n'
                     '  go(i + 1);\n'
                     '  path.pop();\n'
                     '  go(i + 1);\n}\n'
                     'go(0);\n'
                     'for (const s of out) {\n'
                     '  console.log(`[${s.join(",")}]`);\n}\n',
                     _NUMS +
                     'const path: number[] = [];\n'
                     'const out: number[][] = [];\n'
                     'function go(i: number): void {\n'
                     '  if (i === nums.length) {\n'
                     '    out.push([...path]);\n'
                     '    return;\n  }\n'
                     '  path.push(nums[i] ?? 0);\n'
                     '  go(i + 1);\n'
                     '  path.pop();\n'
                     '  go(i + 1);\n}\n'
                     'go(0);\n'
                     'for (const s of out) {\n'
                     '  console.log(`[${s.join(",")}]`);\n}\n',
                     [("1 2", "[1,2]\n[1]\n[2]\n[]"), ("3", "[3]\n[]")],
                     hints=["How many different arrays does `out` actually contain?",
                            "Week 13: pushing an array stores a reference, not its contents.",
                            "Store a snapshot: out.push([...path]);"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Backtracking over subsets is practical up to about…",
                   ["n = 1,000", "n = 20", "n = 100,000", "any n"], 1,
                   "2²⁰ is a million; 2³⁰ is a billion."),
                _q("Stopping when `path.length === k` in the loop form generates…",
                   ["subsets", "combinations of size k", "permutations", "pairs only"], 1,
                   "n choose k of them."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w25-perms", "Permutations",
            "Every order — and every order only once.",
            """
A subset decides *whether*. A permutation decides *where*: every element is used,
and the question is the order.

## A `used` flag per element

```ts
const used: boolean[] = xs.map(() => false);
function go(): void {
  if (path.length === xs.length) { out.push(path.join("")); return; }
  for (let i = 0; i < xs.length; i = i + 1) {
    if (used[i]) { continue; }
    used[i] = true;  path.push(xs[i] ?? "");       // choose
    go();                                           // explore
    path.pop();      used[i] = false;               // un-choose — BOTH halves
  }
}
```

The loop starts at **0** every time — unlike subsets, an earlier element can come
later — and `used` says which are already placed. Un-choosing is two statements
now, and forgetting the second one is the classic bug: nothing is ever free again,
and you get exactly one permutation.

`"abc"` gives `abc acb bac bca cab cba`: **3! = 6**. Four elements: 24 leaves, and
65 calls altogether (1 + 4 + 12 + 24 + 24). n! grows faster than 2ⁿ — ten
elements is 3.6 million orders.

## Duplicates

`"aab"` generates `aab` twice (the two `a`s swapped), `aba` twice, `baa` twice.
The fix needs week 24:

1. **Sort** the input, so equal values sit next to each other.
2. Skip a value equal to the one before it **when that one is not in use**:

```ts
if (i > 0 && xs[i] === xs[i - 1] && !used[i - 1]) { continue; }
```

That rule means "equal values are only ever placed in their original left-to-right
order", so each distinct arrangement is built once. `"aab"` gives `aab aba baa`.

## Typing it generically

A permutation function does not care what it is permuting, which is week 10's
cue for a type parameter:

```ts
function permutations<T>(xs: readonly T[]): T[][]
```

`readonly` on the way in (it never changes its input), a fresh mutable array out
(the caller owns it).

> ⚠️ **Common mistakes:** resetting `path` but not `used`; skipping duplicates on
> unsorted input; and starting the loop at `start` as if it were subsets.
""",
            warmup=[
                _q("The permutations of 4 distinct elements number…",
                   ["16", "24", "8", "12"], 1,
                   "4 × 3 × 2 × 1."),
                _q("Unlike subsets, the permutation loop starts at…",
                   ["start", "0 every time", "i + 1", "the end"], 1,
                   "An earlier element can be placed later."),
                _q("Un-choosing in permutations is…",
                   ["path.pop() only", "path.pop() AND used[i] = false", "used[i] = false only", "nothing"], 1,
                   "Two pieces of state, two undos."),
                _q("Skipping duplicate permutations needs the input…",
                   ["reversed", "sorted", "a Set", "unique"], 1,
                   "Equal values must be adjacent."),
            ],
            exercises=[
                _ex("tscourse-w25-pm-1", "Free it again",
                    "Undo both halves of the choice after exploring.",
                    _LINE +
                    'const xs = [...line];\n'
                    'const used: boolean[] = xs.map(() => false);\n'
                    'const path: string[] = [];\n'
                    'function go(): void {\n'
                    '  if (path.length === xs.length) {\n'
                    '    console.log(path.join(""));\n'
                    '    return;\n  }\n'
                    '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                    '    if (used[i]) {\n'
                    '      continue;\n    }\n'
                    '    used[i] = true;\n'
                    '    path.push(xs[i] ?? "");\n'
                    '    go();\n'
                    '    path.pop();\n'
                    '    used[i] = false;\n  }\n}\n'
                    'go();\n',
                    '    path.pop();\n'
                    '    used[i] = false;',
                    [("abc", "abc\nacb\nbac\nbca\ncab\ncba"), ("ab", "ab\nba")],
                    hints=["Two things were changed when choosing; both must be undone.",
                           "path.pop(); then used[i] = false;"],
                    difficulty="Medium"),
                _ex("tscourse-w25-pm-2", "n! leaves, and the calls to reach them",
                    "Count every call the permutation search makes.",
                    _LINE +
                    'const xs = [...line];\n'
                    'const used: boolean[] = xs.map(() => false);\n'
                    'let placed = 0;\n'
                    'let calls = 0;\n'
                    'let perms = 0;\n'
                    'function go(): void {\n'
                    '  calls = calls + 1;\n'
                    '  if (placed === xs.length) {\n'
                    '    perms = perms + 1;\n'
                    '    return;\n  }\n'
                    '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                    '    if (used[i]) {\n'
                    '      continue;\n    }\n'
                    '    used[i] = true;\n'
                    '    placed = placed + 1;\n'
                    '    go();\n'
                    '    placed = placed - 1;\n'
                    '    used[i] = false;\n  }\n}\n'
                    'go();\n'
                    'console.log(`perms=${perms} calls=${calls}`);\n',
                    '  calls = calls + 1;',
                    [("abcd", "perms=24 calls=65"), ("abc", "perms=6 calls=16")],
                    hints=["Every call counts, not just the leaves.",
                           "Write calls = calls + 1; as the first line of go."],
                    difficulty="Easy"),
                _ex("tscourse-w25-pm-3", "Each arrangement once",
                    "On sorted input, skip a value equal to the one before it when that one is not in use.",
                    _LINE +
                    'const xs = [...line].sort();\n'
                    'const used: boolean[] = xs.map(() => false);\n'
                    'const path: string[] = [];\n'
                    'function go(): void {\n'
                    '  if (path.length === xs.length) {\n'
                    '    console.log(path.join(""));\n'
                    '    return;\n  }\n'
                    '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                    '    if (used[i]) {\n'
                    '      continue;\n    }\n'
                    '    if (i > 0 && xs[i] === xs[i - 1] && !used[i - 1]) {\n'
                    '      continue;\n    }\n'
                    '    used[i] = true;\n'
                    '    path.push(xs[i] ?? "");\n'
                    '    go();\n'
                    '    path.pop();\n'
                    '    used[i] = false;\n  }\n}\n'
                    'go();\n',
                    '    if (i > 0 && xs[i] === xs[i - 1] && !used[i - 1]) {\n'
                    '      continue;\n    }',
                    [("aab", "aab\naba\nbaa"), ("bba", "abb\nbab\nbba"), ("abc", "abc\nacb\nbac\nbca\ncab\ncba")],
                    hints=["Equal values must only ever be placed in their left-to-right order.",
                           "Skip xs[i] when it equals xs[i - 1] and xs[i - 1] is not currently used."],
                    difficulty="Hard"),
                _retype("tscourse-w25-pm-r1", "Type the permutations",
                        "This works and its types say nothing. Make `permutations` generic: it takes a "
                        "`readonly T[]` and returns a fresh `T[][]`, so permuting strings gives `string[][]` and "
                        "permuting numbers gives `number[][]`. Every `any` must go.",
                        'function permutations(xs: any): any {\n'
                        '  if (xs.length <= 1) {\n'
                        '    return [[...xs]];\n  }\n'
                        '  const out: any = [];\n'
                        '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                        '    const rest = [...xs.slice(0, i), ...xs.slice(i + 1)];\n'
                        '    for (const p of permutations(rest)) {\n'
                        '      out.push([xs[i], ...p]);\n    }\n  }\n'
                        '  return out;\n}\n'
                        'console.log(permutations(["a", "b", "c"]).map((p: any) => p.join("")).join(" "));\n',
                        'function permutations<T>(xs: readonly T[]): T[][] {\n'
                        '  if (xs.length <= 1) {\n'
                        '    return [[...xs]];\n  }\n'
                        '  const out: T[][] = [];\n'
                        '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                        '    const first = xs[i];\n'
                        '    if (first === undefined) {\n'
                        '      continue;\n    }\n'
                        '    const rest = [...xs.slice(0, i), ...xs.slice(i + 1)];\n'
                        '    for (const p of permutations(rest)) {\n'
                        '      out.push([first, ...p]);\n    }\n  }\n'
                        '  return out;\n}\n'
                        'console.log(permutations(["a", "b", "c"]).map((p) => p.join("")).join(" "));\n',
                        'const _s = permutations(["x", "y"]);\n'
                        'type _1 = Expect<Equal<typeof _s, string[][]>>;\n'
                        'const _n = permutations([1, 2]);\n'
                        'type _2 = Expect<Equal<typeof _n, number[][]>>;\n',
                        [("", "abc acb bac bca cab cba")],
                        hints=["One type parameter, T, for the element type.",
                               "`xs[i]` is `T | undefined` under this course's strictness — guard it before using it.",
                               "function permutations<T>(xs: readonly T[]): T[][]"],
                        difficulty="Hard"),
                _fix("tscourse-w25-pm-fix1", "Fix the permutations that stopped after one",
                     "This prints only `abc`. The path is popped after each exploration, but `used[i]` is never set back to false — so after the first full arrangement every element is permanently taken and no other branch can place anything.",
                     _LINE +
                     'const xs = [...line];\n'
                     'const used: boolean[] = xs.map(() => false);\n'
                     'const path: string[] = [];\n'
                     'function go(): void {\n'
                     '  if (path.length === xs.length) {\n'
                     '    console.log(path.join(""));\n'
                     '    return;\n  }\n'
                     '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                     '    if (used[i]) {\n'
                     '      continue;\n    }\n'
                     '    used[i] = true;\n'
                     '    path.push(xs[i] ?? "");\n'
                     '    go();\n'
                     '    path.pop();\n  }\n}\n'
                     'go();\n',
                     _LINE +
                     'const xs = [...line];\n'
                     'const used: boolean[] = xs.map(() => false);\n'
                     'const path: string[] = [];\n'
                     'function go(): void {\n'
                     '  if (path.length === xs.length) {\n'
                     '    console.log(path.join(""));\n'
                     '    return;\n  }\n'
                     '  for (let i = 0; i < xs.length; i = i + 1) {\n'
                     '    if (used[i]) {\n'
                     '      continue;\n    }\n'
                     '    used[i] = true;\n'
                     '    path.push(xs[i] ?? "");\n'
                     '    go();\n'
                     '    path.pop();\n'
                     '    used[i] = false;\n  }\n}\n'
                     'go();\n',
                     [("abc", "abc\nacb\nbac\nbca\ncab\ncba"), ("xy", "xy\nyx")],
                     hints=["Choosing changed two things. How many does un-choosing undo?",
                            "An element that stays `used` can never be placed anywhere else.",
                            "Add used[i] = false; after the pop."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Ten distinct elements have how many permutations?",
                   ["1,024", "about 3.6 million", "100", "3,628"], 1,
                   "10! = 3,628,800."),
                _q("The duplicate-skip rule `!used[i - 1]` means equal values are placed…",
                   ["randomly", "only in their original left-to-right order", "last", "never"], 1,
                   "So each arrangement is built exactly once."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w25-prune", "Pruning",
            "Do not explore a branch that cannot work — and count what that saved.",
            """
A backtracking search visits every node of its decision tree unless you tell it
not to. **Pruning** is telling it not to: cut a branch the moment it provably
cannot lead to an answer.

## On sorted input, `break`

"Every set of distinct candidates summing to 8." Sort the candidates first, and
this becomes legal:

```ts
for (let j = start; j < xs.length; j = j + 1) {
  const x = xs[j] ?? 0;
  if (sum + x > target) { break; }       // everything after x is bigger too
  go(j + 1, sum + x);
}
```

Not `continue` — **`break`**, because sorted means every later candidate would
overshoot as well. One comparison discards a whole range of siblings and all of
their descendants.

**The pruning depends on the sort.** On unsorted input `[5, 1, 2, 3]` with target 3,
the loop meets the 5 first, breaks, and never sees `1 + 2` or `3`. It reports no
answers and no error. An optimisation that is only valid under a precondition has
to be written next to the code that establishes it.

## Counting it

On `1 … 8` with target 8 there are 6 answers. The count of calls — nodes visited
— with and without the `break` is the evidence, and lesson 6's first two
exercises print both.

## N-Queens

Place n queens on an n×n board so none attacks another. One queen per row, so
the search chooses a **column** for each row in turn — and prunes any column that
is already attacked:

```ts
if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) { continue; }
```

Three `Set`s (week 19), because every square on one diagonal shares `r + c`, and
every square on the other shares `r - c`. The check is O(1) instead of scanning
the board. Choose adds to all three; un-choose deletes from all three.

n = 4 has **2** solutions, n = 5 has **10**, n = 6 has **4**, n = 8 has **92**.

## Generate only what is valid

Balanced parentheses of n pairs: rather than generating all 2²ⁿ strings and
filtering, only ever add a `(` while fewer than n are open, and only a `)` while
it would close something (`close < open`). Every leaf is then valid by
construction — 5 for n = 3, where filtering would have looked at 64.

> ⚠️ **Common mistakes:** `break` on unsorted input; `continue` where `break`
> is valid (correct, but it prunes nothing); and un-choosing only one of the three
> Sets.
""",
            warmup=[
                _q("Pruning means…",
                   ["deleting answers", "not exploring a branch that cannot succeed", "sorting", "memoising"], 1,
                   "Fewer nodes visited, same answers."),
                _q("`if (sum + x > target) break;` requires…",
                   ["positive targets", "the candidates sorted ascending", "a Set", "no duplicates"], 1,
                   "Otherwise a smaller candidate later is skipped."),
                _q("Two queens share a diagonal when they share…",
                   ["a row", "r + c, or r - c", "c", "r × c"], 1,
                   "Constant along each diagonal."),
                _q("Generating balanced parentheses, a `)` may be added when…",
                   ["always", "close < open", "open < n", "close < n"], 1,
                   "It must close something."),
            ],
            exercises=[
                _ex("tscourse-w25-pr-1", "Stop at the first candidate too big",
                    "On sorted candidates, abandon the rest of the loop once one overshoots.",
                    _NUMS +
                    'const target = 8;\n'
                    'const xs = [...nums].sort((a, b) => a - b);\n'
                    'let visited = 0;\n'
                    'let found = 0;\n'
                    'function go(start: number, sum: number): void {\n'
                    '  visited = visited + 1;\n'
                    '  if (sum === target) {\n'
                    '    found = found + 1;\n'
                    '    return;\n  }\n'
                    '  for (let j = start; j < xs.length; j = j + 1) {\n'
                    '    const x = xs[j] ?? 0;\n'
                    '    if (sum + x > target) {\n'
                    '      break;\n    }\n'
                    '    go(j + 1, sum + x);\n  }\n}\n'
                    'go(0, 0);\n'
                    'console.log(`found=${found} visited=${visited}`);\n',
                    '    if (sum + x > target) {\n'
                    '      break;\n    }',
                    [("1 2 3 4 5 6 7 8", "found=6 visited=25"), ("8 1 7", "found=2 visited=5")],
                    hints=["Sorted, so if x overshoots, every later candidate does too.",
                           "if (sum + x > target) { break; }"],
                    difficulty="Medium"),
                _ex("tscourse-w25-pr-2", "What the break saved",
                    "Run the same search with and without pruning, and report both counts.",
                    'const target = 8;\n'
                    'const xs = [1, 2, 3, 4, 5, 6, 7, 8];\n'
                    'let visited = 0;\n'
                    'let found = 0;\n'
                    'function go(start: number, sum: number, prune: boolean): void {\n'
                    '  visited = visited + 1;\n'
                    '  if (sum === target) {\n'
                    '    found = found + 1;\n'
                    '    return;\n  }\n'
                    '  for (let j = start; j < xs.length; j = j + 1) {\n'
                    '    const x = xs[j] ?? 0;\n'
                    '    if (prune && sum + x > target) {\n'
                    '      break;\n    }\n'
                    '    go(j + 1, sum + x, prune);\n  }\n}\n'
                    'go(0, 0, true);\n'
                    'const pruned = visited;\n'
                    'visited = 0;\n'
                    'found = 0;\n'
                    'go(0, 0, false);\n'
                    'console.log(`found=${found} pruned=${pruned} unpruned=${visited}`);\n',
                    'go(0, 0, false);',
                    [("", "found=6 pruned=25 unpruned=223")],
                    hints=["The same search, with pruning switched off.",
                           "Write go(0, 0, false);"],
                    difficulty="Easy"),
                _ex("tscourse-w25-pr-3", "Is the square attacked?",
                    "Skip any column already attacked along its column or either diagonal.",
                    _QUEENS +
                    'for (const n of [4, 5, 6]) {\n'
                    '  console.log(`n=${n} solutions=${queens(n)}`);\n}\n',
                    '      if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) {\n'
                    '        continue;\n      }',
                    [("", "n=4 solutions=2\nn=5 solutions=10\nn=6 solutions=4")],
                    hints=["Three things can attack a square: its column, and its two diagonals.",
                           "r + c names one diagonal, r - c the other.",
                           "if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) { continue; }"],
                    difficulty="Hard"),
                _ex("tscourse-w25-pr-4", "Eight queens",
                    "Un-choose all three: free the column and both diagonals after exploring.",
                    _LINE +
                    _QUEENS +
                    'console.log(queens(Number(line)));\n',
                    '      cols.delete(c);\n'
                    '      d1.delete(r + c);\n'
                    '      d2.delete(r - c);',
                    [("8", "92"), ("4", "2"), ("1", "1")],
                    hints=["Everything added when choosing must be removed when un-choosing.",
                           "Delete c, r + c and r - c from their Sets."],
                    difficulty="Medium"),
                _ex("tscourse-w25-pr-5", "Only valid strings",
                    "Add a closing bracket only when it would close something.",
                    _LINE +
                    'const n = Number(line);\n'
                    'const out: string[] = [];\n'
                    'function go(s: string, open: number, close: number): void {\n'
                    '  if (s.length === 2 * n) {\n'
                    '    out.push(s);\n'
                    '    return;\n  }\n'
                    '  if (open < n) {\n'
                    '    go(s + "(", open + 1, close);\n  }\n'
                    '  if (close < open) {\n'
                    '    go(s + ")", open, close + 1);\n  }\n}\n'
                    'go("", 0, 0);\n'
                    'console.log(out.join(" "));\n',
                    '  if (close < open) {\n'
                    '    go(s + ")", open, close + 1);\n  }',
                    [("3", "((())) (()()) (())() ()(()) ()()()"), ("1", "()")],
                    hints=["A `)` is only valid while there is an unmatched `(`.",
                           'if (close < open) { go(s + ")", open, close + 1); }'],
                    difficulty="Medium"),
                _fix("tscourse-w25-pr-fix1", "Fix the pruning that ran on unsorted input",
                     "For `5 1 2 3` with a target of 3 this reports `found=0`. There are two answers, `3` and `1+2`. The loop meets the 5 first, sees it overshoot, and breaks — which is only valid if everything after it is bigger. Nothing sorted the candidates.",
                     _NUMS +
                     'const target = 3;\n'
                     'const xs = [...nums];\n'
                     'let found = 0;\n'
                     'function go(start: number, sum: number): void {\n'
                     '  if (sum === target) {\n'
                     '    found = found + 1;\n'
                     '    return;\n  }\n'
                     '  for (let j = start; j < xs.length; j = j + 1) {\n'
                     '    const x = xs[j] ?? 0;\n'
                     '    if (sum + x > target) {\n'
                     '      break;\n    }\n'
                     '    go(j + 1, sum + x);\n  }\n}\n'
                     'go(0, 0);\n'
                     'console.log(`found=${found}`);\n',
                     _NUMS +
                     'const target = 3;\n'
                     'const xs = [...nums].sort((a, b) => a - b);\n'
                     'let found = 0;\n'
                     'function go(start: number, sum: number): void {\n'
                     '  if (sum === target) {\n'
                     '    found = found + 1;\n'
                     '    return;\n  }\n'
                     '  for (let j = start; j < xs.length; j = j + 1) {\n'
                     '    const x = xs[j] ?? 0;\n'
                     '    if (sum + x > target) {\n'
                     '      break;\n    }\n'
                     '    go(j + 1, sum + x);\n  }\n}\n'
                     'go(0, 0);\n'
                     'console.log(`found=${found}`);\n',
                     [("5 1 2 3", "found=2"), ("3 2 1", "found=2")],
                     hints=["`break` claims every later candidate is at least as big. Is that true here?",
                            "The claim needs the candidates in ascending order.",
                            "Sort a copy numerically before searching."],
                     difficulty="Medium"),
                _fix("tscourse-w25-pr-fix2", "Fix the brackets that did not balance",
                     "For n = 3 this reports `20` strings where there are 5 balanced ones. A `)` is allowed whenever fewer than n have been written — including when nothing is open, so `)(` and `())(()` get through.",
                     _LINE +
                     'const n = Number(line);\n'
                     'let count = 0;\n'
                     'function go(len: number, open: number, close: number): void {\n'
                     '  if (len === 2 * n) {\n'
                     '    count = count + 1;\n'
                     '    return;\n  }\n'
                     '  if (open < n) {\n'
                     '    go(len + 1, open + 1, close);\n  }\n'
                     '  if (close < n) {\n'
                     '    go(len + 1, open, close + 1);\n  }\n}\n'
                     'go(0, 0, 0);\n'
                     'console.log(count);\n',
                     _LINE +
                     'const n = Number(line);\n'
                     'let count = 0;\n'
                     'function go(len: number, open: number, close: number): void {\n'
                     '  if (len === 2 * n) {\n'
                     '    count = count + 1;\n'
                     '    return;\n  }\n'
                     '  if (open < n) {\n'
                     '    go(len + 1, open + 1, close);\n  }\n'
                     '  if (close < open) {\n'
                     '    go(len + 1, open, close + 1);\n  }\n}\n'
                     'go(0, 0, 0);\n'
                     'console.log(count);\n',
                     [("3", "5"), ("2", "2"), ("4", "14")],
                     hints=["What must be true for a `)` to be valid at this point?",
                            "It has to close a `(` that is still open.",
                            "The condition is close < open."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Using `continue` where `break` would be valid is…",
                   ["a bug", "correct, but it prunes nothing — every sibling is still tested", "faster",
                    "a type error"], 1,
                   "Right answers, wasted work."),
                _q("Balanced-bracket generation that only builds valid prefixes looks at how many leaves for n = 3?",
                   ["64", "5", "20", "8"], 1,
                   "Every leaf is an answer."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w25-recognise", "Recognising it — and where it stops",
            "'Find all' is backtracking. 'How many ways' often is not.",
            """
## You have been backtracking since week 20

```ts
function pathTo(c: Cat, name: string): readonly string[] | null {
  if (c.name === name) { return [c.name]; }
  for (const kid of c.kids) {
    const below = pathTo(kid, name);
    if (below !== null) { return [c.name, ...below]; }    // found: stop
  }
  return null;                                           // dead end: back up
}
```

`return null` **is** the backtrack: this subtree failed, so the caller tries its
next child. With an explicit `path` array the same search is choose (`push`),
explore, un-choose (`pop`) — this lesson's first exercise writes it that way.

## The wording that gives it away

| the question says | reach for |
|---|---|
| "all subsets / combinations / permutations" | backtracking |
| "every way to…", "list every…" | backtracking |
| "place n … so that none …" | backtracking with pruning |
| "any one path / is it possible" | backtracking that stops at the first success |
| "**how many** ways" / "the **best** way" | often **not** — see below |

## Where it stops being enough

"How many ways to climb 20 stairs, one or two at a time?" A backtracking search
walks every way — and the answer is **10,946** ways, so it makes **21,891** calls.
Worse, look at what it is doing: the number of ways to finish from stair 15 is
computed again every time any path reaches stair 15.

Remember each answer the first time — a `Map` from stair to ways — and the same
question costs **39** calls:

```ts
const known = memo.get(n);
if (known !== undefined) { return known; }
const result = ways(n - 1) + ways(n - 2);
memo.set(n, result);
```

That is **memoisation**, and it only works when the subproblems *repeat* and the
answer is a number rather than a list. Backtracking **lists** the ways; this
**counts** them. Week 26 is entirely about that second kind of question — and it
starts from exactly this example, week 21's `fib`, and this Map.

> ⚠️ **Common mistakes:** backtracking to *count* when the subproblems repeat;
> memoising a search whose state includes the path (nothing ever repeats); and
> storing a memo entry under the wrong key.
""",
            warmup=[
                _q("Week 20's `pathTo` returning `null` is…",
                   ["an error", "the backtrack — this subtree failed, try the next", "the base case only",
                    "memoisation"], 1,
                   "You were already doing it."),
                _q("\"List every combination\" points at…",
                   ["DP", "backtracking", "sorting", "a heap"], 1,
                   "Listing is generating."),
                _q("Counting stair-climbing ways by backtracking recomputes…",
                   ["nothing", "the ways from each stair, every time a path reaches it", "the target", "the sort"], 1,
                   "Repeated subproblems."),
                _q("Memoisation works when…",
                   ["always", "subproblems repeat and have a single answer each", "the input is sorted",
                    "the depth is small"], 1,
                   "A path-dependent state never repeats."),
            ],
            exercises=[
                _ex("tscourse-w25-rc-1", "pathTo, with a path",
                    "Find a category and report the path to it, un-choosing on every dead end.",
                    _LINE +
                    'interface Cat {\n'
                    '  readonly name: string;\n'
                    '  readonly kids: readonly Cat[];\n}\n'
                    'function cat(name: string, kids: readonly Cat[]): Cat {\n'
                    '  return { name, kids };\n}\n'
                    'const root = cat("all", [\n'
                    '  cat("home", [cat("rent", []), cat("power", [])]),\n'
                    '  cat("food", [cat("groceries", []), cat("cafe", [])]),\n]);\n'
                    'const path: string[] = [];\n'
                    'function find(c: Cat, target: string): boolean {\n'
                    '  path.push(c.name);\n'
                    '  if (c.name === target) {\n'
                    '    return true;\n  }\n'
                    '  for (const kid of c.kids) {\n'
                    '    if (find(kid, target)) {\n'
                    '      return true;\n    }\n  }\n'
                    '  path.pop();\n'
                    '  return false;\n}\n'
                    'console.log(find(root, line) ? path.join(" > ") : "not found");\n',
                    '  path.pop();',
                    [("cafe", "all > food > cafe"), ("rent", "all > home > rent"), ("travel", "not found")],
                    hints=["This category and nothing under it matched — take it back off the path.",
                           "Write path.pop(); before returning false."],
                    difficulty="Medium"),
                _ex("tscourse-w25-rc-2", "Letters for digits",
                    "Every string you can type on a phone keypad for the given digits.",
                    _LINE +
                    'const keys: Record<string, string> = {\n'
                    '  "2": "abc", "3": "def", "4": "ghi", "5": "jkl",\n'
                    '  "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",\n};\n'
                    'const out: string[] = [];\n'
                    'function go(i: number, s: string): void {\n'
                    '  if (i === line.length) {\n'
                    '    out.push(s);\n'
                    '    return;\n  }\n'
                    '  for (const letter of keys[line.charAt(i)] ?? "") {\n'
                    '    go(i + 1, s + letter);\n  }\n}\n'
                    'go(0, "");\n'
                    'console.log(out.join(" "));\n',
                    '  for (const letter of keys[line.charAt(i)] ?? "") {\n'
                    '    go(i + 1, s + letter);\n  }',
                    [("23", "ad ae af bd be bf cd ce cf"), ("7", "p q r s")],
                    hints=["Each digit offers a few letters; try each one for position i.",
                           "The string is rebuilt on every call (`s + letter`), so there is nothing to un-choose."],
                    difficulty="Medium"),
                _ex("tscourse-w25-rc-3", "Where backtracking stops being enough",
                    "Count stair-climbing ways twice — naively, and remembering each answer — and compare the calls.",
                    'let naiveCalls = 0;\n'
                    'function ways(n: number): number {\n'
                    '  naiveCalls = naiveCalls + 1;\n'
                    '  return n <= 1 ? 1 : ways(n - 1) + ways(n - 2);\n}\n'
                    'const memo = new Map<number, number>();\n'
                    'let memoCalls = 0;\n'
                    'function fastWays(n: number): number {\n'
                    '  memoCalls = memoCalls + 1;\n'
                    '  if (n <= 1) {\n'
                    '    return 1;\n  }\n'
                    '  const known = memo.get(n);\n'
                    '  if (known !== undefined) {\n'
                    '    return known;\n  }\n'
                    '  const result = fastWays(n - 1) + fastWays(n - 2);\n'
                    '  memo.set(n, result);\n'
                    '  return result;\n}\n'
                    'console.log(`ways=${ways(20)} naive=${naiveCalls} fast=${fastWays(20)} memo=${memoCalls}`);\n',
                    '  memo.set(n, result);',
                    [("", "ways=10946 naive=21891 fast=10946 memo=39")],
                    hints=["Remember the answer for n before returning it.",
                           "Write memo.set(n, result);"],
                    difficulty="Medium"),
                _ex("tscourse-w25-rc-4", "Read the question",
                    "Map each kind of question to the technique it calls for.",
                    _NUMS +
                    'function technique(kind: number): string {\n'
                    '  if (kind === 1) {\n'
                    '    return "backtracking";\n  }\n'
                    '  if (kind === 2) {\n'
                    '    return "backtracking with pruning";\n  }\n'
                    '  if (kind === 3) {\n'
                    '    return "memoisation";\n  }\n'
                    '  return "a loop";\n}\n'
                    'for (const k of nums) {\n'
                    '  console.log(`${k} ${technique(k)}`);\n}\n',
                    '  if (kind === 3) {\n'
                    '    return "memoisation";\n  }',
                    [("1 2 3 4", "1 backtracking\n2 backtracking with pruning\n3 memoisation\n4 a loop")],
                    hints=["Kind 3 is 'how many ways', where the same subproblem keeps recurring.",
                           'Write if (kind === 3) { return "memoisation"; }'],
                    difficulty="Easy"),
                _fix("tscourse-w25-rc-fix1", "Fix the memo stored under the wrong key",
                     "There are 89 ways to climb 10 stairs, and this prints `ways=384`. The result for n is stored under `n - 1`, so the next lookup of n - 1 gets the answer for n, and the error compounds all the way up. A cache that is wrong is worse than no cache: it is fast AND wrong.",
                     _LINE +
                     'const memo = new Map<number, number>();\n'
                     'function ways(n: number): number {\n'
                     '  if (n <= 1) {\n'
                     '    return 1;\n  }\n'
                     '  const known = memo.get(n);\n'
                     '  if (known !== undefined) {\n'
                     '    return known;\n  }\n'
                     '  const result = ways(n - 1) + ways(n - 2);\n'
                     '  memo.set(n - 1, result);\n'
                     '  return result;\n}\n'
                     'console.log(`ways=${ways(Number(line))}`);\n',
                     _LINE +
                     'const memo = new Map<number, number>();\n'
                     'function ways(n: number): number {\n'
                     '  if (n <= 1) {\n'
                     '    return 1;\n  }\n'
                     '  const known = memo.get(n);\n'
                     '  if (known !== undefined) {\n'
                     '    return known;\n  }\n'
                     '  const result = ways(n - 1) + ways(n - 2);\n'
                     '  memo.set(n, result);\n'
                     '  return result;\n}\n'
                     'console.log(`ways=${ways(Number(line))}`);\n',
                     [("10", "ways=89"), ("5", "ways=8")],
                     hints=["What key is the answer read back under? What key is it written under?",
                            "They must be the same — the question the answer belongs to.",
                            "Write memo.set(n, result);"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Memoising a subsets search whose state includes the whole path…",
                   ["is the standard fix", "saves nothing — no two calls share a state", "is a type error",
                    "halves the calls"], 1,
                   "Memoisation needs repeated subproblems."),
                _q("Naive stair-climbing for 20 stairs makes 21,891 calls; memoised, 39. The gap grows…",
                   ["linearly", "exponentially — naive is exponential, memoised is linear", "not at all",
                    "logarithmically"], 1,
                   "Week 26 starts here."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Interview rep #25 — combinations to a target",
        """
Every combination of the candidates that sums to the target. Each candidate may be
used **once**; the input may contain **duplicates**; the output must not.

Input: the candidates on the first line, the target on the second.

```
10 1 2 7 6 1 5
8
```

```
1+1+6
1+2+5
1+7
2+6
found 4  visited 17
```

**The rules:**

* Each combination is printed in ascending order, joined with `+`, and the
  combinations appear in ascending (lexicographic) order — which is exactly the
  order a search over **sorted** candidates produces them in.
* `visited` is the number of calls the search made, **including** the first one.
* When nothing sums to the target, print `none` before the counts.
* An empty candidate line, or a target of 0 or less, makes no call at all:
  `none`, then `found 0  visited 0`.

**What makes it a rep:** sorting does two jobs at once. It makes the
`break`-on-overshoot pruning legal (lesson 6), and it puts equal candidates next to
each other so the duplicate skip — `j > start && xs[j] === xs[j - 1]` — can stop
`1+7` being found once per `1` (lesson 5's rule, in its combination form). The first
test contains two 1s: without the skip, `1+7` and `1+2+5` each appear twice.
""",
        _ch("tscourse-w25-capstone", "Interview rep #25", "Hard",
            "List every combination of the candidates summing to the target, each candidate used "
            "once, with no duplicate combinations — and count the calls.",
            _FS +
            'const lines = fs.readFileSync(0, "utf8").split("\\n");\n'
            'const xs: readonly number[] = (lines[0] ?? "")\n'
            '  .trim()\n'
            '  .split(/\\s+/)\n'
            '  .filter((s) => s !== "")\n'
            '  .map(Number)\n'
            '  .sort((a, b) => a - b);\n'
            'const target = Number((lines[1] ?? "").trim() || "0");\n'
            'const path: number[] = [];\n'
            'const found: string[] = [];\n'
            'let visited = 0;\n'
            'function go(start: number, remaining: number): void {\n'
            '  visited = visited + 1;\n'
            '  if (remaining === 0) {\n'
            '    found.push(path.join("+"));\n'
            '    return;\n  }\n'
            '  for (let j = start; j < xs.length; j = j + 1) {\n'
            '    const x = xs[j] ?? 0;\n'
            '    if (j > start && x === (xs[j - 1] ?? 0)) {\n'
            '      continue;\n    }\n'
            '    if (x > remaining) {\n'
            '      break;\n    }\n'
            '    path.push(x);\n'
            '    go(j + 1, remaining - x);\n'
            '    path.pop();\n  }\n}\n'
            'if (xs.length > 0 && target > 0) {\n'
            '  go(0, target);\n}\n'
            'for (const f of found) {\n'
            '  console.log(f);\n}\n'
            'if (found.length === 0) {\n'
            '  console.log("none");\n}\n'
            'console.log(`found ${found.length}  visited ${visited}`);\n',
            'function go(start: number, remaining: number): void {\n'
            '  visited = visited + 1;\n'
            '  if (remaining === 0) {\n'
            '    found.push(path.join("+"));\n'
            '    return;\n  }\n'
            '  for (let j = start; j < xs.length; j = j + 1) {\n'
            '    const x = xs[j] ?? 0;\n'
            '    if (j > start && x === (xs[j - 1] ?? 0)) {\n'
            '      continue;\n    }\n'
            '    if (x > remaining) {\n'
            '      break;\n    }\n'
            '    path.push(x);\n'
            '    go(j + 1, remaining - x);\n'
            '    path.pop();\n  }\n}',
            [("10 1 2 7 6 1 5\n8", "1+1+6\n1+2+5\n1+7\n2+6\nfound 4  visited 17"),
             ("2 5 2 1 2\n5", "1+2+2\n5\nfound 2  visited 7"),
             ("3 4\n2", "none\nfound 0  visited 1"),
             ("4 4 4 4\n8", "4+4\nfound 1  visited 3"),
             ("\n5", "none\nfound 0  visited 0")],
            hints=["Sort first. Every other part of the solution depends on it.",
                   "Carry the REMAINING amount down; a call with 0 remaining has found a combination.",
                   "Skip a candidate equal to the previous one — but only when it is not the first choice at this level (`j > start`).",
                   "`break`, not `continue`, when a candidate exceeds what remains: everything after it is bigger.",
                   "`4 4 4 4` with target 8 has exactly one answer, and the duplicate skip is what makes it one rather than six.",
                   "Count the call before anything else in it, so the first call counts too."]),
        example_io="1+1+6\n1+2+5\n1+7\n2+6\nfound 4  visited 17",
        rubric=["candidates are sorted once, before the search",
                "choose / explore / un-choose, with a single shared path",
                "duplicates are skipped only after the first choice at each level",
                "an overshooting candidate ends the loop with `break`",
                "every call is counted, including the first",
                "combinations print in ascending order without being sorted afterwards",
                "empty input or a non-positive target makes no call",
                "no index access is asserted with `!`"],
        stretch=_ch("tscourse-w25-capstone-stretch", "Interview rep #25 (stretch)", "Hard",
                    "N-Queens, reported. Read n. Print the **first** solution found (rows top to bottom, "
                    "columns tried left to right) as a board of `.` and `Q`, then "
                    "`solutions S  visited V`, where V counts every call to the placing function. If there "
                    "is no solution, print `no solution` instead of a board. n of 0 or less makes no call.",
                    _FS +
                    'const n = Number(fs.readFileSync(0, "utf8").trim() || "0");\n'
                    'const cols = new Set<number>();\n'
                    'const d1 = new Set<number>();\n'
                    'const d2 = new Set<number>();\n'
                    'const queenAt: number[] = [];\n'
                    'const boards: (readonly number[])[] = [];\n'
                    'let solutions = 0;\n'
                    'let visited = 0;\n'
                    'function place(r: number): void {\n'
                    '  visited = visited + 1;\n'
                    '  if (r === n) {\n'
                    '    solutions = solutions + 1;\n'
                    '    if (boards.length === 0) {\n'
                    '      boards.push([...queenAt]);\n    }\n'
                    '    return;\n  }\n'
                    '  for (let c = 0; c < n; c = c + 1) {\n'
                    '    if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) {\n'
                    '      continue;\n    }\n'
                    '    cols.add(c);\n'
                    '    d1.add(r + c);\n'
                    '    d2.add(r - c);\n'
                    '    queenAt.push(c);\n'
                    '    place(r + 1);\n'
                    '    queenAt.pop();\n'
                    '    cols.delete(c);\n'
                    '    d1.delete(r + c);\n'
                    '    d2.delete(r - c);\n  }\n}\n'
                    'if (n > 0) {\n'
                    '  place(0);\n}\n'
                    'const first = boards[0];\n'
                    'if (first === undefined) {\n'
                    '  console.log("no solution");\n'
                    '} else {\n'
                    '  for (const c of first) {\n'
                    '    console.log(".".repeat(c) + "Q" + ".".repeat(n - c - 1));\n  }\n}\n'
                    'console.log(`solutions ${solutions}  visited ${visited}`);\n',
                    'function place(r: number): void {\n'
                    '  visited = visited + 1;\n'
                    '  if (r === n) {\n'
                    '    solutions = solutions + 1;\n'
                    '    if (boards.length === 0) {\n'
                    '      boards.push([...queenAt]);\n    }\n'
                    '    return;\n  }\n'
                    '  for (let c = 0; c < n; c = c + 1) {\n'
                    '    if (cols.has(c) || d1.has(r + c) || d2.has(r - c)) {\n'
                    '      continue;\n    }\n'
                    '    cols.add(c);\n'
                    '    d1.add(r + c);\n'
                    '    d2.add(r - c);\n'
                    '    queenAt.push(c);\n'
                    '    place(r + 1);\n'
                    '    queenAt.pop();\n'
                    '    cols.delete(c);\n'
                    '    d1.delete(r + c);\n'
                    '    d2.delete(r - c);\n  }\n}',
                    [("4", ".Q..\n...Q\nQ...\n..Q.\nsolutions 2  visited 17"),
                     ("1", "Q\nsolutions 1  visited 2"),
                     ("3", "no solution\nsolutions 0  visited 6"),
                     ("0", "no solution\nsolutions 0  visited 0")],
                    hints=["Record each row's column in a path array; a snapshot of it IS a board.",
                           "Keep only the first snapshot — later solutions still count, but are not stored.",
                           "Store the snapshot in an array rather than a `let first = null`: TypeScript does not see an assignment made inside a nested function, and would narrow `first` to `null` for ever.",
                           "Row r has its queen at column c: c dots, a Q, then n - c - 1 dots."]),
    ),
))
