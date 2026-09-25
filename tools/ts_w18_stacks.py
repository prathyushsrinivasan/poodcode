# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 18 — stacks & queues.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THIS WEEK DEEPENS, IT DOES NOT INTRODUCE. Week 6 already taught `.push()`,
# `.pop()`, `.shift()` and `.unshift()` as array methods — the `_SCOPE_RULES`
# table gates `.push(` at 6 and says nothing about the other three, because week
# 6 uses all of them. So the lesson text is written as "you have had the
# operations for twelve weeks; here is what they are FOR, and what they cost",
# never as first contact.
#
# What is genuinely new is the *discipline*: a stack is not an array, it is an
# array you have agreed to only touch at one end — and lesson 2 makes that
# agreement enforceable with a class (week 11) and a type parameter (week 10).
#
# ---------------------------------------------------------------------------
# THE CONSTRAINT THAT SHAPED THE WEEK: NO `Map`, NO `Set`.
#
# Both are gated at week **19**, one week later, so nothing here may use them.
# That is not an inconvenience to work around — it is the ladder working. Every
# lookup in this week is an array scan or a `Record`, which is exactly the cost
# week 19 then arrives to remove. Two consequences worth knowing before adding
# anything here:
#
#   * The bracket matcher's pair table is a `Record<string, string>` (week 10),
#     and every read of it takes a `?? ""` because of noUncheckedIndexedAccess.
#   * The monotonic-stack lesson keeps INDICES on the stack rather than values,
#     which is how the real pattern is written anyway.
#
# ---------------------------------------------------------------------------
# THE O(n) SHIFT TRAP, TAUGHT WITHOUT A CLOCK.
#
# "`shift()` is O(n)" is the week's one genuinely important performance fact, and
# it cannot honestly be demonstrated by timing anything — a four-element array is
# instant on every machine, and a big enough array to measure would make the
# exercise about the judge's timeout. The same rule as week 17 applies: **nothing
# prints elapsed time.**
#
# So lesson 5 has the learner WRITE the loop that `shift()` hides — copy every
# remaining element down one slot — and count the copies. Draining a 4-element
# queue costs `3 + 2 + 1 + 0 = 6` moves, printed as a number, identical on every
# machine. Lesson 6 replaces the whole thing with a head index and the same
# program prints `moves 0`. The contrast IS the lesson, and it is arithmetic
# rather than a stopwatch.
#
# ---------------------------------------------------------------------------
# ONE TRAP THIS WEEK WALKED INTO, AND THE VERIFIER CAUGHT.
#
# `constructor(private readonly limit: number) {}` — a **parameter property** —
# type-checks and then dies at run time:
#
#   SyntaxError [ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX]: TypeScript parameter
#   property is not supported in strip-only mode
#
# That is decision 5 in TS_ROADMAP, and week 11 already knows it: week 11 teaches
# parameter properties with `judge_mode: "types"` precisely because they cannot
# run. Lesson 7's `History` class was written with one and had to be rewritten as
# an explicit field plus an assignment in the constructor. Any class in a RUNNABLE
# exercise, here or later, has to be written the long way.
# ---------------------------------------------------------------------------
#
# One detail that keeps that loop honest under `noUncheckedIndexedAccess`:
# `items[i - 1] = items[i]` does not compile (TS2322 — `number | undefined` into
# `number`), so the element is bound and checked first. That is week 16 lesson 7
# being paid forward, and it ships as a `diagnose`.
# ---------------------------------------------------------------------------

# The generic stack the week builds in lesson 2 and then reuses. Written out in
# full wherever it is needed rather than hoisted into a prefix: it is the subject,
# not scaffolding, and a learner who cannot see it cannot reason about it.
_STACK = (
    'class Stack<T> {\n'
    '  private readonly items: T[] = [];\n'
    '  push(value: T): void {\n'
    '    this.items.push(value);\n  }\n'
    '  pop(): T | undefined {\n'
    '    return this.items.pop();\n  }\n'
    '  peek(): T | undefined {\n'
    '    return this.items[this.items.length - 1];\n  }\n'
    '  get size(): number {\n'
    '    return this.items.length;\n  }\n'
    '  isEmpty(): boolean {\n'
    '    return this.items.length === 0;\n  }\n'
    '}\n'
)

# --- Week 18 --------------------------------------------------------------
_WEEKS.append(_week(
    18, 5, _M5,
    "Stacks & Queues",
    "Two disciplines for one array: last-in-first-out and first-in-first-out. Build both as generic classes, find out what `shift()` really costs, and meet the monotonic stack.",
    """
You have had `push`, `pop`, `shift` and `unshift` since week 6. This week is about
what they are *for*.

## A stack and a queue are agreements, not data types

An array can be indexed anywhere, spliced in the middle, sorted, reversed. A
**stack** is an array you have agreed to touch only at the **end**; a **queue** is
one you add to at the end and take from the **front**. Nothing in the language
enforces either agreement — which is why lesson 2 makes it enforceable, with a
class whose array is `private`.

| | add | remove | order |
|---|---|---|---|
| **stack** | `push` | `pop` | last in, first out |
| **queue** | `push` | `shift` | first in, first out |

## Why a stack, specifically

Because a stack is the shape of **anything nested**. Brackets, tags, function
calls, undo history, a depth-first walk: in every case the thing you opened most
recently is the thing you must close first, and that is the definition of LIFO.
Once you see that, "use a stack" stops being a trick you memorise.

## And the cost nobody mentions

`array.shift()` removes the first element by **moving every other element down one
slot**. It is O(n), so a queue built on `shift` is O(n²) to drain. Lesson 5 has
you write that loop by hand and count the moves; lesson 6 replaces it with a head
index and the count goes to zero.

## What is not here yet

`Map` and `Set` arrive next week, so every lookup in this week is an array scan or
a `Record`. That is deliberate — the cost you feel here is exactly what week 19
removes.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Say what makes a structure a stack rather than an array you happen to push onto",
        "Use an array as a stack, and handle the empty case `pop()` hands you",
        "Write a generic `Stack<T>` whose array cannot be reached from outside",
        "Say why returning the private array defeats the point, and what to return instead",
        "Solve balanced brackets with a stack, and say what the final emptiness check is for",
        "Model undo/redo with two stacks, and say what a new action does to the redo stack",
        "Say what `shift()` costs and why, having counted the moves yourself",
        "Build an O(1) queue with a head index, and name what it trades away",
        "Write a `Deque<T>` and say which of a stack and a queue it can stand in for",
        "Recognise a monotonic-stack problem, and state the invariant the stack maintains",
        "Solve next-greater-element in one pass",
    ],
    why="Stacks and queues are the two structures interviewers assume you can build from nothing, and the two whose *shape* recurs everywhere — a parser, an undo feature, a breadth-first search, a task runner. The `shift()` cost is the other half: it is the most common accidental O(n²) in JavaScript, and the reason is invisible unless somebody shows you the loop hiding inside the method call.",
    est_minutes=480,
    glossary=[
        _gloss("stack", "Last in, first out. Add and remove at the same end."),
        _gloss("queue", "First in, first out. Add at one end, remove from the other."),
        _gloss("LIFO / FIFO", "The two orders. A stack reverses; a queue preserves."),
        _gloss("push", "Add to the end. O(1) for both structures."),
        _gloss("pop", "Remove from the end. O(1), and returns `T | undefined`."),
        _gloss("shift", "Remove from the FRONT. Returns `T | undefined`, and is O(n)."),
        _gloss("unshift", "Add at the front. Also O(n), for the same reason."),
        _gloss("peek / top", "Read the next item without removing it."),
        _gloss("underflow", "Popping an empty stack. In JavaScript it is `undefined`, not an error."),
        _gloss("encapsulation", "The array is `private`, so the only way in is the methods you wrote."),
        _gloss("leaking the buffer", "Returning the private array itself, so callers can bypass every method."),
        _gloss("defensive copy", "Returning `[...this.items]` instead, so a caller's mutation cannot reach you."),
        _gloss("balanced brackets", "The canonical stack problem: every closer matches the most recent opener."),
        _gloss("undo stack", "Actions taken. Popping one moves it to the redo stack."),
        _gloss("redo stack", "Actions undone. A NEW action clears it — the future has changed."),
        _gloss("head index", "A queue that never shifts: remember where the front is instead of moving everything."),
        _gloss("amortised O(1)", "Each operation is O(1) on average, even if one occasionally does more work."),
        _gloss("deque", "Double-ended queue. Add and remove at either end."),
        _gloss("monotonic stack", "A stack kept sorted by its own rule, so each element is pushed and popped once."),
        _gloss("next greater element", "For each item, the first later item bigger than it. One pass, one stack."),
        _gloss("invariant", "Something true of the stack before and after every step. What makes the pattern correct."),
    ],
    cheatsheet="""
```ts
// ---- an array as a stack (both ends the same end) ------------------------
const stack: number[] = [];
stack.push(1);
stack.push(2);
const top = stack[stack.length - 1];   // peek — number | undefined
const last = stack.pop();               // 2   — number | undefined, ALWAYS
stack.length === 0;                     // isEmpty

// ---- an array as a queue (add at the end, take from the front) -----------
const queue: string[] = [];
queue.push("a");
const first = queue.shift();            // "a" — and O(n): everything moved down

// ---- the generic class, so the agreement is enforced --------------------
class Stack<T> {
  private readonly items: T[] = [];            // private: the whole point
  push(value: T): void { this.items.push(value); }
  pop(): T | undefined { return this.items.pop(); }     // NOT `: T`
  peek(): T | undefined { return this.items[this.items.length - 1]; }
  get size(): number { return this.items.length; }
  isEmpty(): boolean { return this.items.length === 0; }
  all(): readonly T[] { return [...this.items]; }        // a COPY, never `this.items`
}

// ---- what shift() actually does ----------------------------------------
for (let i = 1; i < items.length; i = i + 1) {
  const v = items[i];
  if (v !== undefined) { items[i - 1] = v; }   // one move per element, every time
}
items.length = items.length - 1;                // draining n items costs O(n²)

// ---- …and the queue that does not do it -------------------------------
class Queue<T> {
  private readonly items: T[] = [];
  private head = 0;                              // where the front IS
  enqueue(v: T): void { this.items.push(v); }
  dequeue(): T | undefined {
    if (this.head >= this.items.length) { return undefined; }
    const v = this.items[this.head];
    this.head = this.head + 1;                   // move the INDEX, not the data
    return v;
  }
  get size(): number { return this.items.length - this.head; }
}

// ---- balanced brackets -------------------------------------------------
const PAIRS: Record<string, string> = { ")": "(", "]": "[", "}": "{" };
for (const ch of text) {
  if (ch === "(" || ch === "[" || ch === "{") { stack.push(ch); }
  else if (ch in PAIRS) {
    if (stack.pop() !== (PAIRS[ch] ?? "")) { return false; }
  }
}
return stack.length === 0;          // anything still open means unbalanced

// ---- undo / redo -------------------------------------------------------
undo.push(action);                  // did something
redo.length = 0;                    // …so the old future is gone
const back = undo.pop();            // undo: move it to redo
if (back !== undefined) { redo.push(back); }

// ---- monotonic stack: next greater element ----------------------------
const out: number[] = new Array(nums.length).fill(-1);
const idx: number[] = [];                        // INDICES, kept decreasing by value
for (let i = 0; i < nums.length; i = i + 1) {
  while (top of idx has a smaller value than nums[i]) { out[pop()] = nums[i]; }
  idx.push(i);
}
// each index is pushed once and popped at most once ⇒ O(n) overall
```
""",
    self_check=[
        "Can you say what distinguishes a stack from an array you only push onto?",
        "Can you say what `pop()` returns on an empty array, and what its type is?",
        "Can you write a generic `Stack<T>` with push, pop, peek, size and isEmpty?",
        "Can you say why `pop(): T` does not compile, and what the right signature is?",
        "Can you say what goes wrong if a method returns the private array itself?",
        "Can you solve balanced brackets, and say why the final `length === 0` check is needed?",
        "Can you say what a new action must do to the redo stack, and why?",
        "Can you say how many element moves draining a four-item shift-based queue costs?",
        "Can you write a queue that never shifts, and say what it trades away?",
        "Can you say which operations a deque adds over a queue?",
        "Can you state the invariant a monotonic stack maintains?",
        "Can you explain why next-greater-element is O(n) despite having a loop inside a loop?",
    ],
    review=[
        _q("A stack is…",
           ["a sorted array", "an array you only add to and remove from at one end",
            "a linked list", "a map"], 1,
           "The discipline is the structure."),
        _q("`[].pop()` gives…",
           ["an error", "undefined", "null", "0"], 1,
           "Underflow is silent in JavaScript."),
        _q("The type of `items.pop()` where items is `number[]` is…",
           ["number", "number | undefined", "unknown", "void"], 1,
           "Always, flags or no flags."),
        _q("`pop(): T { return this.items.pop(); }` gives…",
           ["nothing", "TS2322 — T | undefined is not assignable to T", "TS2532", "any"], 1,
           "The signature has to admit the empty case."),
        _q("Reading `s.items` from outside the class gives…",
           ["the array", "TS2341 — the property is private", "a copy", "undefined"], 1,
           "Which is what makes the agreement real."),
        _q("A method returning `this.items` directly…",
           ["is fine", "lets callers bypass every method you wrote", "is faster", "is readonly"], 1,
           "Return a copy, typed readonly."),
        _q("Brackets: `((` ends with…",
           ["balanced", "a non-empty stack, so unbalanced", "an error", "an empty stack"], 1,
           "Which is exactly what the final check catches."),
        _q("Brackets: `([)]` fails because…",
           ["the counts differ", "the closer does not match the most recent opener",
            "it is too short", "the stack is empty"], 1,
           "Counting brackets is not enough — order matters."),
        _q("`shift()` is O(n) because it…",
           ["searches", "moves every remaining element down one slot", "copies the array",
            "sorts"], 1,
           "The loop is inside the method call."),
        _q("Draining a 4-item queue with `shift` costs how many element moves?",
           ["4", "6", "0", "16"], 1,
           "3 + 2 + 1 + 0."),
        _q("A queue with a head index dequeues in…",
           ["O(n)", "O(1)", "O(log n)", "O(n²)"], 1,
           "Move the index, not the data."),
        _q("What the head-index queue trades away is…",
           ["correctness", "memory — the consumed slots are not reclaimed until you compact",
            "order", "type safety"], 1,
           "Which is usually a bargain, and worth knowing about."),
        _q("A deque…",
           ["is a sorted queue", "adds and removes at BOTH ends", "is a stack", "is immutable"], 1,
           "So it can stand in for either."),
        _q("A monotonic stack is O(n) overall because…",
           ["the inner loop is short", "each element is pushed once and popped at most once",
            "it is sorted", "it uses indices"], 1,
           "The total work is bounded by the number of elements, not by the nesting."),
        _q("In next-greater-element the stack holds…",
           ["values", "indices, so the answer can be written into the right slot",
            "pairs", "counts"], 1,
           "Which is why the pattern is written that way."),
    ],
    milestone="Budget Buddy gets undo and redo. Every command is applied to the ledger and pushed onto an undo stack; `undo` moves the top one back off and onto the redo stack; `redo` puts it back. And a new action after an undo clears the redo stack, because that future no longer exists — which is the rule every editor you have used implements and almost nobody can state.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w18-stack", "An array, used at one end",
            "LIFO, and the `undefined` that comes with it.",
            """
A stack needs two operations, and you have had both since week 6:

```ts
const stack: number[] = [];
stack.push(1);                     // add at the end
stack.push(2);
const last = stack.pop();          // remove from the end — 2
```

Add a third that does not remove anything:

```ts
const top = stack[stack.length - 1];      // peek
```

and a fourth that everybody forgets until it bites:

```ts
stack.length === 0;                        // isEmpty
```

## `pop()` is `T | undefined`, always

Not because of a compiler flag — because an empty array genuinely has nothing to
give you:

```ts
const items: number[] = [];
console.log(items.pop());          // undefined. No error, no warning.
```

So the type of `items.pop()` is `number | undefined` under *any* settings, and
reading a member off it directly is rejected:

```ts
items.pop().toFixed(1);
// ❌ TS2532: Object is possibly 'undefined'.
```

Handle it the way week 15 and week 16 taught — a guard, or a `??`:

```ts
const v = items.pop();
if (v !== undefined) { console.log(v.toFixed(1)); }
console.log((items.pop() ?? 0).toFixed(1));
```

This is not ceremony. "The stack was empty" is a real case in every stack
algorithm, and the bracket matcher in lesson 3 is *wrong* if it does not handle it.

## Why LIFO is the shape of nested things

```
(  [  {        →  push ( , push [ , push {
         }     →  pop must be {   ← the most recent opener
      ]        →  pop must be [
   )           →  pop must be (
```

Anything nested has this property: the thing opened most recently must be closed
first. Brackets, HTML tags, function calls, a depth-first walk of a tree, the undo
history of an editor. When you notice that shape, the answer is a stack — that is
the whole insight, and it is worth more than any individual algorithm.

## Reversal is free

A stack reverses whatever you put into it, which is occasionally the entire
algorithm:

```ts
const out: string[] = [];
while (stack.length > 0) {
  const v = stack.pop();
  if (v !== undefined) { out.push(v); }
}
```

> ⚠️ **Common mistakes:** forgetting that `pop()` may be `undefined`; using
> `stack[0]` for the top (that is the *bottom*); and reaching for a stack when the
> order you need is FIFO.
""",
            warmup=[
                _q("A stack's top is at…",
                   ["index 0", "index length - 1", "the middle", "either end"], 1,
                   "Push and pop both work at the end."),
                _q("`[].pop()` is…",
                   ["an error", "undefined", "null", "NaN"], 1,
                   "Silent underflow."),
                _q("`items.pop().toFixed(1)` gives…",
                   ["the number", "TS2532", "TS7006", "undefined"], 1,
                   "The absence has to be handled."),
                _q("A stack is the right structure for…",
                   ["a print queue", "anything nested — brackets, calls, undo",
                    "sorting", "a lookup"], 1,
                   "Most-recent-first is the definition."),
            ],
            exercises=[
                _ex("tscourse-w18-st-1", "Push and pop",
                    "Take the last value off the stack and print it.",
                    'const stack: number[] = [];\n'
                    'stack.push(1);\n'
                    'stack.push(2);\n'
                    'const last = stack.pop();\n'
                    'console.log(`${last ?? 0} ${stack.length}`);\n',
                    'const last = stack.pop();', [("", "2 1")],
                    hints=["The method that removes from the end.",
                           "Write const last = stack.pop();"]),
                _ex("tscourse-w18-st-2", "Peek without removing",
                    "Read the top of the stack while leaving it in place.",
                    _WORDS +
                    'const stack: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  stack.push(w);\n}\n'
                    'const top = stack[stack.length - 1];\n'
                    'console.log(`${top ?? "-"} ${stack.length}`);\n',
                    'const top = stack[stack.length - 1];',
                    [("a b c", "c 3"), ("solo", "solo 1")],
                    hints=["The top is the LAST index, not the first.",
                           "Write const top = stack[stack.length - 1];"],
                    difficulty="Easy"),
                _ex("tscourse-w18-st-3", "Handle the empty stack",
                    "Guard the popped value so the program says `empty` rather than crashing.",
                    'const stack: number[] = [];\n'
                    'const v = stack.pop();\n'
                    'if (v === undefined) {\n'
                    '  console.log("empty");\n'
                    '} else {\n'
                    '  console.log(v.toFixed(1));\n}\n',
                    'if (v === undefined) {', [("", "empty")],
                    hints=["`pop()` on an empty array hands back the absence rather than throwing.",
                           "Write if (v === undefined) {"],
                    difficulty="Easy"),
                _ex("tscourse-w18-st-4", "Reverse with a stack",
                    "Drain the stack into a second array, which reverses it for free.",
                    _WORDS +
                    'const stack: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  stack.push(w);\n}\n'
                    'const out: string[] = [];\n'
                    'while (stack.length > 0) {\n'
                    '  const v = stack.pop();\n'
                    '  if (v !== undefined) {\n'
                    '    out.push(v);\n  }\n}\n'
                    'console.log(out.join(" "));\n',
                    'while (stack.length > 0) {', [("a b c", "c b a"), ("one two", "two one")],
                    hints=["Keep going while there is anything left.",
                           "Write while (stack.length > 0) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-st-5", "Depth of the deepest nesting",
                    "Track the largest the stack ever gets, which is the deepest nesting in the input.",
                    _LINE +
                    'const stack: string[] = [];\n'
                    'let deepest = 0;\n'
                    'for (const ch of line) {\n'
                    '  if (ch === "(") {\n'
                    '    stack.push(ch);\n'
                    '    deepest = Math.max(deepest, stack.length);\n'
                    '  } else if (ch === ")") {\n'
                    '    stack.pop();\n  }\n}\n'
                    'console.log(deepest);\n',
                    '    deepest = Math.max(deepest, stack.length);',
                    [("(()(()))", "3"), ("()()", "1"), ("", "0")],
                    hints=["Check the height right after a push, because that is when it grows.",
                           "Write deepest = Math.max(deepest, stack.length);"],
                    difficulty="Medium"),
                _predict("tscourse-w18-st-p1", "What pop really gives you",
                         'const items: number[] = [1, 2, 3];\n'
                         'const got = items.pop();\n',
                         "got", "number | undefined",
                         why="The array is not empty *today*, but the method's signature cannot know that.",
                         hints=["The element type, plus the case where there was nothing to take.",
                                "Write number | undefined."]),
                _diagnose("tscourse-w18-st-d1", "The pop that might have been empty",
                          "TS2532: Object is possibly 'undefined'.",
                          'const items: number[] = [1, 2];\n'
                          'console.log(items.pop().toFixed(1));\n',
                          'const items: number[] = [1, 2];\n'
                          'console.log((items.pop() ?? 0).toFixed(1));\n',
                          [("", "2.0")],
                          hints=["`pop()` is typed for the empty case even when this array is not empty.",
                                 "Supply a fallback before calling a method on the result.",
                                 "Write (items.pop() ?? 0).toFixed(1)."],
                          difficulty="Easy"),
                _fix("tscourse-w18-st-fix1", "Fix the peek that read the bottom",
                     "This prints `a` — the first thing pushed — instead of `c`. `stack[0]` is the bottom of the stack; the top is the other end.",
                     _WORDS +
                     'const stack: string[] = [];\n'
                     'for (const w of words) {\n'
                     '  stack.push(w);\n}\n'
                     'console.log(stack[0] ?? "-");\n',
                     _WORDS +
                     'const stack: string[] = [];\n'
                     'for (const w of words) {\n'
                     '  stack.push(w);\n}\n'
                     'console.log(stack[stack.length - 1] ?? "-");\n',
                     [("a b c", "c"), ("solo", "solo")],
                     hints=["Push adds at the end, so the most recent item is at the end.",
                            "Index from the length, not from zero.",
                            "Write stack[stack.length - 1]."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("A stack reverses its input because…",
                   ["it sorts", "the last thing in is the first thing out", "of pop",
                    "arrays are backwards"], 1,
                   "Which is sometimes the whole algorithm."),
                _q("Handling `pop()`'s undefined is…",
                   ["ceremony", "the empty-stack case, which every stack algorithm really has",
                    "only for strict mode", "avoidable with `!`"], 1,
                   "The bracket matcher is wrong without it."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w18-class", "A generic `Stack<T>`",
            "Making the agreement enforceable.",
            """
Nothing stops a caller from `splice`-ing an array you were treating as a stack. A
class with a `private` field does:

```ts
class Stack<T> {
  private readonly items: T[] = [];

  push(value: T): void {
    this.items.push(value);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }
  get size(): number {
    return this.items.length;
  }
  isEmpty(): boolean {
    return this.items.length === 0;
  }
}
```

Week 10 gave you the `<T>`; week 11 gave you `private`, `readonly` and the getter.
This is those two weeks earning their place.

## Four details that are the whole lesson

**`private readonly items`** — `private` stops outside access (TS2341);
`readonly` stops *you* from reassigning the field. The array's contents are still
mutable, which is exactly right: `push` needs to work.

**`pop(): T | undefined`, not `pop(): T`.** Try the second and the compiler
explains itself:

```
TS2322: Type 'T | undefined' is not assignable to type 'T'.
        'T' could be instantiated with an arbitrary type which could be
        unrelated to 'T | undefined'.
```

A stack that promises to return a `T` is lying about the empty case. The
alternatives are to return the union (usual), or to throw (defensible, if
underflow is a bug in your program rather than a state your program has).

**`get size()`** — a getter, so callers write `s.size` rather than `s.size()`.
Worth it for something that is conceptually a property.

**Never return the array.**

```ts
all(): readonly T[] {
  return this.items;          // ❌ the caller can now cast it back and splice it
}
all(): readonly T[] {
  return [...this.items];     // ✅ a copy — week 13's rule
}
```

`readonly T[]` is a compile-time promise about a mutable array. Handing out the
real one means one `as T[]` defeats the entire class. The spread copy costs O(n)
and is almost always the right trade.

## Generic, so it is one class

```ts
const numbers = new Stack<number>();
const words = new Stack<string>();
const entries = new Stack<{ readonly desc: string }>();
```

One implementation, checked at every call site. A `Stack` of `any` would compile
too, and would tell you nothing at the moment you took something back out.

> ⚠️ **Common mistakes:** `pop(): T`; returning `this.items`; and making the field
> `public` "just for tests" — a test that reaches past the API is testing
> something the API does not promise.
""",
            warmup=[
                _q("`private readonly items: T[]` stops…",
                   ["all mutation", "outside access, and reassigning the field — not push",
                    "push", "nothing"], 1,
                   "The contents stay mutable on purpose."),
                _q("`pop(): T` gives…",
                   ["nothing", "TS2322", "TS2341", "TS2532"], 1,
                   "It cannot honour that signature when empty."),
                _q("`get size()` lets callers write…",
                   ["s.size()", "s.size", "size(s)", "s.length"], 1,
                   "A getter, for something that reads as a property."),
                _q("`return this.items` from a `readonly T[]` method…",
                   ["is safe", "hands out the real array, which one cast can mutate",
                    "copies it", "is an error"], 1,
                   "Return a spread copy."),
            ],
            exercises=[
                _ex("tscourse-w18-cl-1", "The type parameter",
                    "Make the stack generic, so one class serves every element type.",
                    'class Stack<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  push(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  pop(): T | undefined {\n'
                    '    return this.items.pop();\n  }\n}\n'
                    'const s = new Stack<string>();\n'
                    's.push("a");\n'
                    'console.log(s.pop() ?? "-");\n',
                    'class Stack<T> {', [("", "a")],
                    hints=["One type parameter, in angle brackets after the name.",
                           "Write class Stack<T> {"],
                    difficulty="Easy"),
                _ex("tscourse-w18-cl-2", "The honest pop signature",
                    "Annotate `pop` so it admits the empty case.",
                    _STACK +
                    'const s = new Stack<number>();\n'
                    's.push(5);\n'
                    'console.log(`${s.pop() ?? 0} ${s.pop() ?? 0}`);\n',
                    '  pop(): T | undefined {', [("", "5 0")],
                    hints=["The element type, or nothing at all.",
                           "Write pop(): T | undefined {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-cl-3", "A size getter",
                    "Expose the count as a property rather than a method.",
                    _STACK +
                    'const s = new Stack<string>();\n'
                    's.push("a");\n'
                    's.push("b");\n'
                    'console.log(`${s.size} ${s.isEmpty()}`);\n',
                    '  get size(): number {', [("", "2 false")],
                    hints=["One keyword in front of the method name.",
                           "Write get size(): number {"],
                    difficulty="Easy"),
                _ex("tscourse-w18-cl-4", "Hand out a copy",
                    "Return the contents in a form a caller cannot use to reach into the stack.",
                    'class Stack<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  push(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  all(): readonly T[] {\n'
                    '    return [...this.items];\n  }\n}\n'
                    'const s = new Stack<number>();\n'
                    's.push(1);\n'
                    's.push(2);\n'
                    'const snapshot = s.all();\n'
                    's.push(3);\n'
                    'console.log(`${snapshot.join(",")} | ${s.all().join(",")}`);\n',
                    '    return [...this.items];', [("", "1,2 | 1,2,3")],
                    hints=["A spread copy, so the snapshot cannot change under the caller's feet.",
                           "Write return [...this.items];"],
                    difficulty="Medium"),
                _ex("tscourse-w18-cl-5", "Use it on an object type",
                    "Instantiate the same stack for entries rather than numbers.",
                    _STACK +
                    'interface Entry {\n'
                    '  readonly desc: string;\n  readonly cents: number;\n}\n'
                    'const s = new Stack<Entry>();\n'
                    's.push({ desc: "coffee", cents: 325 });\n'
                    'const top = s.peek();\n'
                    'console.log(top === undefined ? "-" : `${top.desc} ${top.cents}`);\n',
                    'const s = new Stack<Entry>();', [("", "coffee 325")],
                    hints=["The type argument is whatever you are stacking.",
                           "Write const s = new Stack<Entry>();"],
                    difficulty="Easy"),
                _diagnose("tscourse-w18-cl-d1", "Reaching past the API",
                          "TS2341: Property 'items' is private and only accessible within class 'Stack'.",
                          'class Stack {\n'
                          '  private items: number[] = [];\n'
                          '  push(v: number): void {\n'
                          '    this.items.push(v);\n  }\n'
                          '  get size(): number {\n'
                          '    return this.items.length;\n  }\n}\n'
                          'const s = new Stack();\n'
                          's.push(1);\n'
                          'console.log(s.items.length);\n',
                          'class Stack {\n'
                          '  private items: number[] = [];\n'
                          '  push(v: number): void {\n'
                          '    this.items.push(v);\n  }\n'
                          '  get size(): number {\n'
                          '    return this.items.length;\n  }\n}\n'
                          'const s = new Stack();\n'
                          's.push(1);\n'
                          'console.log(s.size);\n',
                          [("", "1")],
                          hints=["The field is private precisely so that callers cannot do this.",
                                 "The class already offers what the caller wanted.",
                                 "Use the `size` getter."],
                          difficulty="Easy"),
                _diagnose("tscourse-w18-cl-d2", "A pop that promised too much",
                          "TS2322: Type 'T | undefined' is not assignable to type 'T'.",
                          'class Stack<T> {\n'
                          '  private items: T[] = [];\n'
                          '  push(v: T): void {\n'
                          '    this.items.push(v);\n  }\n'
                          '  pop(): T {\n'
                          '    return this.items.pop();\n  }\n}\n'
                          'const s = new Stack<number>();\n'
                          's.push(1);\n'
                          'console.log(s.pop());\n',
                          'class Stack<T> {\n'
                          '  private items: T[] = [];\n'
                          '  push(v: T): void {\n'
                          '    this.items.push(v);\n  }\n'
                          '  pop(): T | undefined {\n'
                          '    return this.items.pop();\n  }\n}\n'
                          'const s = new Stack<number>();\n'
                          's.push(1);\n'
                          'console.log(s.pop());\n',
                          [("", "1")],
                          hints=["An empty stack has no `T` to return, so the signature cannot promise one.",
                                 "Widen the return type to include the absence.",
                                 "Write pop(): T | undefined {"],
                          difficulty="Medium"),
                _fix("tscourse-w18-cl-fix1", "Fix the stack that leaked its buffer",
                     "`all()` returns the private array itself, so the snapshot taken before the third push shows three items — the caller is holding the stack's own storage. Hand back a copy.",
                     'class Stack<T> {\n'
                     '  private readonly items: T[] = [];\n'
                     '  push(value: T): void {\n'
                     '    this.items.push(value);\n  }\n'
                     '  all(): readonly T[] {\n'
                     '    return this.items;\n  }\n}\n'
                     'const s = new Stack<number>();\n'
                     's.push(1);\n'
                     's.push(2);\n'
                     'const snapshot = s.all();\n'
                     's.push(3);\n'
                     'console.log(snapshot.join(","));\n',
                     'class Stack<T> {\n'
                     '  private readonly items: T[] = [];\n'
                     '  push(value: T): void {\n'
                     '    this.items.push(value);\n  }\n'
                     '  all(): readonly T[] {\n'
                     '    return [...this.items];\n  }\n}\n'
                     'const s = new Stack<number>();\n'
                     's.push(1);\n'
                     's.push(2);\n'
                     'const snapshot = s.all();\n'
                     's.push(3);\n'
                     'console.log(snapshot.join(","));\n',
                     [("", "1,2")],
                     hints=["`readonly T[]` is a promise about what the CALLER may do, not a copy.",
                            "The snapshot and the stack are the same array.",
                            "Return a spread copy instead."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A `Stack<any>` compiles and is worse because…",
                   ["it is slower", "it tells you nothing at the moment you take something out",
                    "it cannot push", "of strict mode"], 1,
                   "The type parameter earns its keep at `pop`."),
                _q("Making the field public for a test is…",
                   ["good practice", "testing something the API does not promise", "required",
                    "faster"], 1,
                   "Test through the API."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w18-brackets", "Balanced brackets",
            "The canonical stack problem, and why counting is not enough.",
            """
Is `([]{})` balanced? Is `([)]`?

The tempting answer is to count: three openers, three closers, done. It is wrong —
`([)]` has matching counts and is not balanced, because **order** matters. What has
to be true is stronger:

> Every closer must match the **most recently unclosed** opener.

"Most recent" is a stack.

## The algorithm

```ts
const PAIRS: Record<string, string> = { ")": "(", "]": "[", "}": "{" };

function balanced(text: string): boolean {
  const stack: string[] = [];
  for (const ch of text) {
    if (ch === "(" || ch === "[" || ch === "{") {
      stack.push(ch);
    } else if (ch === ")" || ch === "]" || ch === "}") {
      if (stack.pop() !== (PAIRS[ch] ?? "")) {
        return false;
      }
    }
  }
  return stack.length === 0;
}
```

Four things in nine lines, and each is a case people forget:

1. **An opener is pushed.** Nothing else.
2. **A closer pops**, and the popped value must be its partner. If the stack was
   empty, `pop()` is `undefined`, which is not equal to any opener — so `)` on its
   own fails here without a special case. That is the empty-stack handling from
   lesson 1 doing real work.
3. **Characters that are neither are ignored**, so `a(b)c` is balanced.
4. **The final check.** `((` never fails inside the loop — nothing ever popped
   wrongly — and is still unbalanced. `return stack.length === 0` is what catches
   it, and leaving it off is the single most common bug in this problem.

## Why the table

A `Record<string, string>` from closer to opener replaces three `if`s, and adding
`<>` is one more entry rather than another branch. Note the `?? ""`: an index into
a `Record<string, string>` is `string | undefined` under
`noUncheckedIndexedAccess`, and the fallback makes the comparison total.

`Map` would be the more natural home for this table — and arrives next week.

## The same shape, elsewhere

* **Nesting depth** — the stack's height (lesson 1).
* **Matching tags** — push the opening tag name, compare on the closing one.
* **A calculator's parentheses** — push the pending operator.
* **Undo** — push the action; the most recent one is what `undo` means.

Recognising the shape is the skill. The code is nine lines every time.

> ⚠️ **Common mistakes:** counting instead of matching; forgetting the final
> emptiness check; and crashing on a closer that arrives with an empty stack.
""",
            warmup=[
                _q("`([)]` is unbalanced because…",
                   ["the counts differ", "a closer does not match the most recent opener",
                    "it is short", "of the brackets used"], 1,
                   "Counting cannot see this."),
                _q("`((` fails…",
                   ["inside the loop", "only at the final emptiness check", "never", "on the first char"], 1,
                   "Which is why that check is not optional."),
                _q("A closer arriving with an empty stack gives `pop()` =…",
                   ["an error", "undefined, which matches no opener", "the closer", "\"\""], 1,
                   "So it fails without a special case."),
                _q("`a(b)c` is…",
                   ["unbalanced", "balanced — non-bracket characters are ignored", "an error",
                    "empty"], 1,
                   "Only brackets take part."),
            ],
            exercises=[
                _ex("tscourse-w18-br-1", "Match the most recent opener",
                    "Compare the popped opener against the one this closer expects.",
                    _LINE +
                    'const PAIRS: Record<string, string> = { ")": "(", "]": "[", "}": "{" };\n'
                    'function balanced(text: string): boolean {\n'
                    '  const stack: string[] = [];\n'
                    '  for (const ch of text) {\n'
                    '    if (ch === "(" || ch === "[" || ch === "{") {\n'
                    '      stack.push(ch);\n'
                    '    } else if (ch === ")" || ch === "]" || ch === "}") {\n'
                    '      if (stack.pop() !== (PAIRS[ch] ?? "")) {\n'
                    '        return false;\n      }\n    }\n  }\n'
                    '  return stack.length === 0;\n}\n'
                    'console.log(balanced(line));\n',
                    '      if (stack.pop() !== (PAIRS[ch] ?? "")) {',
                    [("([]{})", "true"), ("([)]", "false"), ("a(b)c", "true")],
                    hints=["Pop once, and compare it to the table's entry for this closer.",
                           'The Record lookup needs its `?? ""` fallback.',
                           'Write if (stack.pop() !== (PAIRS[ch] ?? "")) {'],
                    difficulty="Medium"),
                _ex("tscourse-w18-br-2", "The check that catches `((`",
                    "Add the final condition, so an unclosed opener is reported.",
                    _LINE +
                    'const PAIRS: Record<string, string> = { ")": "(", "]": "[" };\n'
                    'function balanced(text: string): boolean {\n'
                    '  const stack: string[] = [];\n'
                    '  for (const ch of text) {\n'
                    '    if (ch === "(" || ch === "[") {\n'
                    '      stack.push(ch);\n'
                    '    } else if (ch === ")" || ch === "]") {\n'
                    '      if (stack.pop() !== (PAIRS[ch] ?? "")) {\n'
                    '        return false;\n      }\n    }\n  }\n'
                    '  return stack.length === 0;\n}\n'
                    'console.log(balanced(line));\n',
                    '  return stack.length === 0;',
                    [("(()", "false"), ("(())", "true"), ("", "true")],
                    hints=["Nothing popped wrongly, and yet something is still open.",
                           "Write return stack.length === 0;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-br-3", "One more pair, no new branch",
                    "Add angle brackets to the table and to the opener test.",
                    _LINE +
                    'const PAIRS: Record<string, string> = { ")": "(", "]": "[", ">": "<" };\n'
                    'function balanced(text: string): boolean {\n'
                    '  const stack: string[] = [];\n'
                    '  for (const ch of text) {\n'
                    '    if (ch === "(" || ch === "[" || ch === "<") {\n'
                    '      stack.push(ch);\n'
                    '    } else if (ch in PAIRS) {\n'
                    '      if (stack.pop() !== (PAIRS[ch] ?? "")) {\n'
                    '        return false;\n      }\n    }\n  }\n'
                    '  return stack.length === 0;\n}\n'
                    'console.log(balanced(line));\n',
                    'const PAIRS: Record<string, string> = { ")": "(", "]": "[", ">": "<" };',
                    [("<[()]>", "true"), ("<(>)", "false")],
                    hints=["The table maps closer to opener, so the new entry is `\">\": \"<\"`.",
                           'Write const PAIRS: Record<string, string> = { ")": "(", "]": "[", ">": "<" };'],
                    difficulty="Medium"),
                _ex("tscourse-w18-br-4", "Report where it broke",
                    "Return the 1-based position of the first bad character instead of a boolean.",
                    _LINE +
                    'const PAIRS: Record<string, string> = { ")": "(", "]": "[" };\n'
                    'function firstProblem(text: string): number {\n'
                    '  const stack: string[] = [];\n'
                    '  for (let i = 0; i < text.length; i = i + 1) {\n'
                    '    const ch = text.charAt(i);\n'
                    '    if (ch === "(" || ch === "[") {\n'
                    '      stack.push(ch);\n'
                    '    } else if (ch in PAIRS) {\n'
                    '      if (stack.pop() !== (PAIRS[ch] ?? "")) {\n'
                    '        return i + 1;\n      }\n    }\n  }\n'
                    '  return stack.length === 0 ? 0 : text.length + 1;\n}\n'
                    'console.log(firstProblem(line));\n',
                    '        return i + 1;',
                    [("([)]", "3"), ("(())", "0"), ("((", "3")],
                    hints=["The index is zero-based and the answer is one-based.",
                           "Write return i + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-br-5", "Matching tags, same shape",
                    "Push the opening tag's name and compare it when the closing tag arrives.",
                    _WORDS +
                    'function tagsMatch(tags: readonly string[]): boolean {\n'
                    '  const open: string[] = [];\n'
                    '  for (const tag of tags) {\n'
                    '    if (tag.startsWith("/")) {\n'
                    '      if (open.pop() !== tag.slice(1)) {\n'
                    '        return false;\n      }\n'
                    '    } else {\n'
                    '      open.push(tag);\n    }\n  }\n'
                    '  return open.length === 0;\n}\n'
                    'console.log(tagsMatch(words));\n',
                    '      if (open.pop() !== tag.slice(1)) {',
                    [("ul li /li /ul", "true"), ("ul li /ul /li", "false"), ("p /p", "true")],
                    hints=["The closing tag is the opener with a slash in front, so drop the slash before comparing.",
                           'Write if (open.pop() !== tag.slice(1)) {'],
                    difficulty="Medium"),
                _diagnose("tscourse-w18-br-d1", "The table lookup that might miss",
                          "TS2532: Object is possibly 'undefined'.",
                          'const PAIRS: Record<string, string> = { ")": "(" };\n'
                          'const closer = ")";\n'
                          'console.log(PAIRS[closer].length);\n',
                          'const PAIRS: Record<string, string> = { ")": "(" };\n'
                          'const closer = ")";\n'
                          'console.log((PAIRS[closer] ?? "").length);\n',
                          [("", "1")],
                          hints=["A Record claims nothing about which keys are present — week 16, lesson 7.",
                                 "Supply a fallback before reading a member of the result.",
                                 'Write (PAIRS[closer] ?? "").length.'],
                          difficulty="Easy"),
                _fix("tscourse-w18-br-fix1", "Fix the matcher that counted",
                     "This says `([)]` is balanced, because it only checks that the number of openers and closers agree. Counting cannot see order — match against the most recent opener instead.",
                     _LINE +
                     'function balanced(text: string): boolean {\n'
                     '  let open = 0;\n'
                     '  for (const ch of text) {\n'
                     '    if (ch === "(" || ch === "[") {\n'
                     '      open = open + 1;\n'
                     '    } else if (ch === ")" || ch === "]") {\n'
                     '      open = open - 1;\n'
                     '      if (open < 0) {\n'
                     '        return false;\n      }\n    }\n  }\n'
                     '  return open === 0;\n}\n'
                     'console.log(balanced(line));\n',
                     _LINE +
                     'const PAIRS: Record<string, string> = { ")": "(", "]": "[" };\n'
                     'function balanced(text: string): boolean {\n'
                     '  const stack: string[] = [];\n'
                     '  for (const ch of text) {\n'
                     '    if (ch === "(" || ch === "[") {\n'
                     '      stack.push(ch);\n'
                     '    } else if (ch in PAIRS) {\n'
                     '      if (stack.pop() !== (PAIRS[ch] ?? "")) {\n'
                     '        return false;\n      }\n    }\n  }\n'
                     '  return stack.length === 0;\n}\n'
                     'console.log(balanced(line));\n',
                     [("([)]", "false"), ("([])", "true"), ("(()", "false")],
                     hints=["A counter knows how many are open, not WHICH.",
                            "Keep the openers themselves, so a closer can be compared to the most recent one.",
                            "Push the opener; on a closer, pop and compare against the pair table."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The strong condition is…",
                   ["equal counts", "every closer matches the most recently unclosed opener",
                    "no nesting", "sorted brackets"], 1,
                   "Which is precisely what a stack gives you."),
                _q("Using a `Record` for the pair table rather than three `if`s…",
                   ["is slower", "makes adding a pair one entry instead of one branch",
                    "needs Map", "is unsafe"], 1,
                   "And next week it becomes a Map."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w18-undo", "Undo and redo, with two stacks",
            "The rule every editor implements and few people can state.",
            """
Undo is a stack: the action you want to reverse is the one you did most recently.
Redo is a *second* stack, and the interesting part is the rule connecting them.

```ts
const undoStack: string[] = [];
const redoStack: string[] = [];

function doAction(name: string): void {
  undoStack.push(name);
  redoStack.length = 0;        // ← the rule
}

function undo(): string | undefined {
  const action = undoStack.pop();
  if (action !== undefined) { redoStack.push(action); }
  return action;
}

function redo(): string | undefined {
  const action = redoStack.pop();
  if (action !== undefined) { undoStack.push(action); }
  return action;
}
```

## The rule

> **A new action clears the redo stack.**

Because the future you undid no longer exists. Type `a`, `b`, `c`, undo twice, then
type `x`: there is nothing sensible for redo to mean any more — `b` was undone from
a document that no longer exists. Every editor you have used does this, and
forgetting it produces a redo that resurrects an action into a state it was never
recorded against.

`redoStack.length = 0` is the idiom for emptying an array in place. (`redoStack =
[]` would need a `let` and would not be visible to anything holding a reference to
the old array.)

## What goes on the stack

Three designs, in increasing order of cost and capability:

* **The action's name.** Enough to *describe* history — what this lesson's
  exercises do.
* **The action, plus what it needs to be reversed.** "added entry #4", "removed
  entry {…}". This is what a real undo needs, and what the capstone builds: every
  command carries the information required to invert it.
* **A whole snapshot of the state.** Simplest to write, and the most memory —
  week 13's immutable-history capstone took this route, and it is a perfectly
  respectable choice when the state is small.

## Where the limits are

Real editors cap the undo stack (drop the oldest — which is a *queue* operation on
the bottom of a stack, and the reason a deque exists), and coalesce adjacent
actions so that typing twelve characters is not twelve undos.

> ⚠️ **Common mistakes:** forgetting to clear redo on a new action; pushing to redo
> even when the undo stack was empty; and storing only the action name when you
> need to reverse it.
""",
            warmup=[
                _q("A new action should…",
                   ["clear the undo stack", "clear the redo stack", "clear both", "clear neither"], 1,
                   "That future no longer exists."),
                _q("`undo()` moves the action…",
                   ["off both stacks", "from the undo stack to the redo stack", "to the front",
                    "nowhere"], 1,
                   "So redo can put it back."),
                _q("`arr.length = 0`…",
                   ["is an error", "empties the array in place", "sets one element", "sorts it"], 1,
                   "The idiom for clearing without reassigning."),
                _q("To actually reverse an action, the stack must hold…",
                   ["its name", "enough information to invert it", "a timestamp", "a boolean"], 1,
                   "Which is what the capstone builds."),
            ],
            exercises=[
                _ex("tscourse-w18-un-1", "Undo moves it across",
                    "Pop from the undo stack and push what you got onto the redo stack.",
                    'const undoStack: string[] = ["a", "b"];\n'
                    'const redoStack: string[] = [];\n'
                    'function undo(): string | undefined {\n'
                    '  const action = undoStack.pop();\n'
                    '  if (action !== undefined) {\n'
                    '    redoStack.push(action);\n  }\n'
                    '  return action;\n}\n'
                    'console.log(`${undo() ?? "-"} ${undoStack.join(",")} | ${redoStack.join(",")}`);\n',
                    '    redoStack.push(action);', [("", "b a | b")],
                    hints=["Only push if something actually came off.",
                           "Write redoStack.push(action);"],
                    difficulty="Easy"),
                _ex("tscourse-w18-un-2", "A new action clears the future",
                    "Empty the redo stack when a fresh action is performed.",
                    'const undoStack: string[] = [];\n'
                    'const redoStack: string[] = ["old"];\n'
                    'function doAction(name: string): void {\n'
                    '  undoStack.push(name);\n'
                    '  redoStack.length = 0;\n}\n'
                    'doAction("x");\n'
                    'console.log(`${undoStack.join(",")} | ${redoStack.length}`);\n',
                    '  redoStack.length = 0;', [("", "x | 0")],
                    hints=["Clear the array in place rather than reassigning it.",
                           "Write redoStack.length = 0;"],
                    difficulty="Easy"),
                _ex("tscourse-w18-un-3", "Nothing to undo",
                    "Return the absence rather than pushing `undefined` onto redo.",
                    'const undoStack: string[] = [];\n'
                    'const redoStack: string[] = [];\n'
                    'function undo(): string {\n'
                    '  const action = undoStack.pop();\n'
                    '  if (action === undefined) {\n'
                    '    return "nothing to undo";\n  }\n'
                    '  redoStack.push(action);\n'
                    '  return `undid ${action}`;\n}\n'
                    'console.log(undo());\n'
                    'console.log(`redo has ${redoStack.length}`);\n',
                    '  if (action === undefined) {', [("", "nothing to undo\nredo has 0")],
                    hints=["An empty undo stack must not put anything on the redo stack.",
                           "Write if (action === undefined) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-un-4", "The full cycle",
                    "Drive a session from stdin: each word is an action, `undo` or `redo`.",
                    _WORDS +
                    'const undoStack: string[] = [];\n'
                    'const redoStack: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  if (w === "undo") {\n'
                    '    const a = undoStack.pop();\n'
                    '    if (a !== undefined) {\n'
                    '      redoStack.push(a);\n    }\n'
                    '  } else if (w === "redo") {\n'
                    '    const a = redoStack.pop();\n'
                    '    if (a !== undefined) {\n'
                    '      undoStack.push(a);\n    }\n'
                    '  } else {\n'
                    '    undoStack.push(w);\n'
                    '    redoStack.length = 0;\n  }\n}\n'
                    'console.log(`${undoStack.join(",")} | ${redoStack.join(",")}`);\n',
                    '  } else if (w === "redo") {',
                    [("a b undo", "a | b"), ("a b undo redo", "a,b |"),
                     ("a b undo c", "a,c |"), ("undo redo a", "a |")],
                    hints=["Three cases: undo, redo, and anything else — which is a new action.",
                           'Write } else if (w === "redo") {'],
                    difficulty="Medium"),
                _ex("tscourse-w18-un-5", "Store enough to reverse it",
                    "Keep the amount alongside the action, so undoing actually restores the total.",
                    _NUMS +
                    'interface Change {\n'
                    '  readonly kind: "add";\n'
                    '  readonly cents: number;\n}\n'
                    'const undoStack: Change[] = [];\n'
                    'let total = 0;\n'
                    'for (const n of nums) {\n'
                    '  total = total + n;\n'
                    '  undoStack.push({ kind: "add", cents: n });\n}\n'
                    'const last = undoStack.pop();\n'
                    'if (last !== undefined) {\n'
                    '  total = total - last.cents;\n}\n'
                    'console.log(total);\n',
                    '  total = total - last.cents;', [("10 20 30", "30"), ("5", "0")],
                    hints=["The change carries the amount, which is exactly what reversing it needs.",
                           "Write total = total - last.cents;"],
                    difficulty="Medium"),
                _fix("tscourse-w18-un-fix1", "Fix the redo that came back from the dead",
                     "Type `a`, `b`, undo, then `c`: this still offers to redo `b`, into a document `b` was never recorded against. A new action has to discard the future.",
                     _WORDS +
                     'const undoStack: string[] = [];\n'
                     'const redoStack: string[] = [];\n'
                     'for (const w of words) {\n'
                     '  if (w === "undo") {\n'
                     '    const a = undoStack.pop();\n'
                     '    if (a !== undefined) {\n'
                     '      redoStack.push(a);\n    }\n'
                     '  } else {\n'
                     '    undoStack.push(w);\n  }\n}\n'
                     'console.log(`${undoStack.join(",")} | ${redoStack.join(",")}`);\n',
                     _WORDS +
                     'const undoStack: string[] = [];\n'
                     'const redoStack: string[] = [];\n'
                     'for (const w of words) {\n'
                     '  if (w === "undo") {\n'
                     '    const a = undoStack.pop();\n'
                     '    if (a !== undefined) {\n'
                     '      redoStack.push(a);\n    }\n'
                     '  } else {\n'
                     '    undoStack.push(w);\n'
                     '    redoStack.length = 0;\n  }\n}\n'
                     'console.log(`${undoStack.join(",")} | ${redoStack.join(",")}`);\n',
                     [("a b undo c", "a,c |"), ("a b undo", "a | b")],
                     hints=["The bug only shows when a new action follows an undo.",
                            "Redoing `b` now would apply it to a state it was never recorded against.",
                            "Clear the redo stack in the new-action branch."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Storing a whole state snapshot per action is…",
                   ["wrong", "simple and memory-hungry — a fine trade when the state is small",
                    "impossible", "the only way"], 1,
                   "Week 13's capstone took exactly that route."),
                _q("Capping the undo stack by dropping the oldest entry is…",
                   ["a stack operation", "a queue operation at the bottom of a stack — which is what a deque is for",
                    "impossible", "free"], 1,
                   "Lesson 7."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w18-queue", "Queues, and what `shift()` costs",
            "The most common accidental O(n²) in JavaScript.",
            """
A queue is first-in-first-out: add at one end, remove from the other.

```ts
const queue: string[] = [];
queue.push("a");
queue.push("b");
const first = queue.shift();       // "a"
```

Two lines, correct, and quietly expensive.

## What `shift()` does

An array's elements live at positions 0, 1, 2, …. Removing element 0 means every
other element has to **move down one slot**:

```ts
// what shift() does, written out:
for (let i = 1; i < items.length; i = i + 1) {
  const v = items[i];
  if (v !== undefined) {
    items[i - 1] = v;              // one move. Per element. Every time.
  }
}
items.length = items.length - 1;
```

That is **O(n)** per `shift`, so draining an n-element queue costs
`(n-1) + (n-2) + … + 0` moves — **O(n²)**. For four elements that is 6 moves; for
a thousand it is 499,500; for a hundred thousand it is five billion, and your
program appears to hang.

`unshift()` has the same cost for the same reason, in the other direction.

## Count it, do not time it

You are about to write that loop and count the moves. That is deliberate: the
number is **arithmetic**, identical on every machine, where a timing measurement
would be noise on a four-element array and a timeout on a large one. Lesson 6
rewrites the queue so the same program prints `moves 0`.

## `pop()` is not the same

```ts
items.pop();          // O(1) — nothing else has to move
items.shift();        // O(n) — everything has to move
```

Which is why a **stack** on an array is free and a **queue** on an array is not:
both of a stack's operations happen at the cheap end.

## The shapes that need a queue

* **Breadth-first search** — the frontier is a queue, and it is the difference
  between BFS and DFS (week 27).
* **A task runner** — jobs are served in the order they arrived.
* **Rate limiting, buffering, streaming** — anything where "first come, first
  served" is the requirement.

In every one of those, the queue is drained in a loop, which is exactly where the
O(n²) bites.

> ⚠️ **Common mistakes:** building a queue on `shift` and being surprised at scale;
> assuming `pop` and `shift` cost the same; and "fixing" it by reversing the array
> and popping, which makes *enqueue* the expensive end instead.
""",
            warmup=[
                _q("`shift()` removes…",
                   ["the last element", "the first element, moving everything down",
                    "a random element", "nothing"], 1,
                   "The move is the cost."),
                _q("`shift()` is…",
                   ["O(1)", "O(n)", "O(log n)", "free"], 1,
                   "One move per remaining element."),
                _q("Draining a 4-element queue with shift costs…",
                   ["4 moves", "6 moves", "0 moves", "16 moves"], 1,
                   "3 + 2 + 1 + 0."),
                _q("`pop()` costs…",
                   ["O(n)", "O(1) — nothing has to move", "O(log n)", "the same as shift"], 1,
                   "Which is why a stack on an array is free."),
            ],
            exercises=[
                _ex("tscourse-w18-q-1", "A queue with shift",
                    "Take from the front, so the words come out in the order they arrived.",
                    _WORDS +
                    'const queue: string[] = [];\n'
                    'for (const w of words) {\n'
                    '  queue.push(w);\n}\n'
                    'while (queue.length > 0) {\n'
                    '  const next = queue.shift();\n'
                    '  if (next !== undefined) {\n'
                    '    console.log(next);\n  }\n}\n',
                    '  const next = queue.shift();',
                    [("a b c", "a\nb\nc"), ("solo", "solo")],
                    hints=["FIFO takes from the front.",
                           "Write const next = queue.shift();"],
                    difficulty="Easy"),
                _ex("tscourse-w18-q-2", "Write the loop shift hides",
                    "Move every remaining element down one slot, which is what `shift()` does for you.",
                    'const items: number[] = [10, 20, 30];\n'
                    'let moves = 0;\n'
                    'const first = items[0];\n'
                    'for (let i = 1; i < items.length; i = i + 1) {\n'
                    '  const v = items[i];\n'
                    '  if (v !== undefined) {\n'
                    '    items[i - 1] = v;\n'
                    '    moves = moves + 1;\n  }\n}\n'
                    'items.length = items.length - 1;\n'
                    'console.log(`${first ?? 0} ${items.join(",")} moves ${moves}`);\n',
                    '    items[i - 1] = v;',
                    [("", "10 20,30 moves 2")],
                    hints=["Each element moves to the slot below its own.",
                           "Write items[i - 1] = v;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-q-3", "Count the cost of draining it",
                    "Drain the whole queue by hand and report the total number of element moves.",
                    _NUMS +
                    'const items: number[] = [...nums];\n'
                    'let moves = 0;\n'
                    'function dequeue(): number | undefined {\n'
                    '  const first = items[0];\n'
                    '  if (first === undefined) {\n'
                    '    return undefined;\n  }\n'
                    '  for (let i = 1; i < items.length; i = i + 1) {\n'
                    '    const v = items[i];\n'
                    '    if (v !== undefined) {\n'
                    '      items[i - 1] = v;\n'
                    '      moves = moves + 1;\n    }\n  }\n'
                    '  items.length = items.length - 1;\n'
                    '  return first;\n}\n'
                    'while (items.length > 0) {\n'
                    '  dequeue();\n}\n'
                    'console.log(`moves ${moves}`);\n',
                    'while (items.length > 0) {',
                    [("10 20 30 40", "moves 6"), ("1 2", "moves 1"), ("7", "moves 0")],
                    hints=["Keep dequeuing until nothing is left, then report the running total.",
                           "Write while (items.length > 0) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-q-4", "First come, first served",
                    "Serve the jobs in arrival order, printing each with its position.",
                    _WORDS +
                    'const queue: string[] = [...words];\n'
                    'let served = 0;\n'
                    'while (queue.length > 0) {\n'
                    '  const job = queue.shift();\n'
                    '  if (job === undefined) {\n'
                    '    break;\n  }\n'
                    '  served = served + 1;\n'
                    '  console.log(`${served}. ${job}`);\n}\n',
                    '  served = served + 1;',
                    [("wash dry fold", "1. wash\n2. dry\n3. fold")],
                    hints=["The counter goes up once per job actually served.",
                           "Write served = served + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w18-q-5", "Both ends, both costs",
                    "Show the asymmetry: pop from the end is free, shift from the front is not.",
                    'const items: number[] = [1, 2, 3, 4];\n'
                    'const fromEnd = items.pop();\n'
                    'const fromFront = items.shift();\n'
                    'console.log(`${fromEnd ?? 0} ${fromFront ?? 0} ${items.join(",")}`);\n',
                    'const fromFront = items.shift();', [("", "4 1 2,3")],
                    hints=["One removes the last, the other the first.",
                           "Write const fromFront = items.shift();"],
                    difficulty="Easy"),
                _diagnose("tscourse-w18-q-d1", "Moving a maybe-missing element",
                          "TS2322: Type 'number | undefined' is not assignable to type 'number'.",
                          'const items: number[] = [1, 2, 3];\n'
                          'for (let i = 1; i < items.length; i = i + 1) {\n'
                          '  items[i - 1] = items[i];\n}\n'
                          'console.log(items.join(" "));\n',
                          'const items: number[] = [1, 2, 3];\n'
                          'for (let i = 1; i < items.length; i = i + 1) {\n'
                          '  const v = items[i];\n'
                          '  if (v !== undefined) {\n'
                          '    items[i - 1] = v;\n  }\n}\n'
                          'console.log(items.join(" "));\n',
                          [("", "2 3 3")],
                          hints=["Reading `items[i]` gives `number | undefined`; the slot you are writing into holds a `number`.",
                                 "Bind the element and check it before storing it — week 16, lesson 7.",
                                 "Two extra lines: a `const v` and an `if`."],
                          difficulty="Medium"),
                _fix("tscourse-w18-q-fix1", "Fix the queue that was a stack",
                     "The jobs come out backwards — `fold`, `dry`, `wash` — because this takes from the same end it adds to. A queue takes from the other end.",
                     _WORDS +
                     'const queue: string[] = [...words];\n'
                     'while (queue.length > 0) {\n'
                     '  const job = queue.pop();\n'
                     '  if (job !== undefined) {\n'
                     '    console.log(job);\n  }\n}\n',
                     _WORDS +
                     'const queue: string[] = [...words];\n'
                     'while (queue.length > 0) {\n'
                     '  const job = queue.shift();\n'
                     '  if (job !== undefined) {\n'
                     '    console.log(job);\n  }\n}\n',
                     [("wash dry fold", "wash\ndry\nfold"), ("a b", "a\nb")],
                     hints=["`pop` takes from the end, which is LIFO — the opposite of what a queue promises.",
                            "One method call changes.",
                            "Write queue.shift()."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Reversing the array and popping instead…",
                   ["fixes the cost", "just moves the O(n) to enqueue", "is faster", "is O(1)"], 1,
                   "`unshift` is expensive for the same reason."),
                _q("Breadth-first search needs a queue because…",
                   ["it is faster", "the frontier must be served in arrival order — that is what makes it breadth-first",
                    "of memory", "stacks are slow"], 1,
                   "Swap the queue for a stack and you have DFS."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w18-fastqueue", "The queue that never shifts",
            "Move the index, not the data.",
            """
`shift()` is O(n) because it moves the data. So do not move the data — remember
where the front **is**:

```ts
class Queue<T> {
  private readonly items: T[] = [];
  private head = 0;                        // the index of the front

  enqueue(value: T): void {
    this.items.push(value);                // O(1)
  }
  dequeue(): T | undefined {
    if (this.head >= this.items.length) {
      return undefined;                    // empty
    }
    const value = this.items[this.head];
    this.head = this.head + 1;             // O(1) — one number changed
    return value;
  }
  peek(): T | undefined {
    return this.head < this.items.length ? this.items[this.head] : undefined;
  }
  get size(): number {
    return this.items.length - this.head;  // NOT items.length
  }
  isEmpty(): boolean {
    return this.size === 0;
  }
}
```

Both operations are now O(1), so draining n items is O(n) rather than O(n²). Run
lesson 5's counting program against this and it prints **`moves 0`**.

## What it trades away

**Memory.** The slots before `head` are still there, holding values nobody can
reach. A queue that has served a million items keeps a million dead slots.

For most programs that is irrelevant — the queue drains and is thrown away. For a
long-lived one it matters, and the fix is to **compact** occasionally:

```ts
private compact(): void {
  if (this.head > 32 && this.head * 2 > this.items.length) {
    this.items.splice(0, this.head);       // one O(n) move…
    this.head = 0;                          // …every O(n) dequeues
  }
}
```

Called from `dequeue`, that is **amortised O(1)**: one expensive operation spread
across many cheap ones, so the average cost per operation is still constant. It is
the same accounting that makes `push` O(1) even though the underlying array must
occasionally be reallocated.

## Two other ways, for completeness

* **A ring buffer** — a fixed-size array with `head` and `tail` indices that wrap
  around. Constant memory, and the shape every real queue implementation uses.
* **Two stacks** — push onto one; when you need to dequeue and the other is empty,
  pop everything across (which reverses it) and pop from there. A classic
  interview question, and also amortised O(1): each element moves across exactly
  once.

## Which to reach for

In real TypeScript, an array with a head index is almost always enough, and if a
queue is on the hot path you reach for a library. What matters is knowing that
`shift()` in a loop is a trap, and that "remember the index instead of moving the
data" is the way out.

> ⚠️ **Common mistakes:** `size` returning `items.length` (it must subtract
> `head`); forgetting the `head >= length` empty check; and compacting on every
> dequeue, which puts the O(n) straight back.
""",
            warmup=[
                _q("A head-index queue's dequeue is…",
                   ["O(n)", "O(1)", "O(log n)", "O(n²)"], 1,
                   "One number changes."),
                _q("`size` must be…",
                   ["items.length", "items.length - head", "head", "0"], 1,
                   "The consumed slots are still in the array."),
                _q("What it costs is…",
                   ["correctness", "memory — dead slots before head", "order", "type safety"], 1,
                   "Usually a bargain."),
                _q("Amortised O(1) means…",
                   ["always O(1)", "O(1) on average, even if one operation occasionally does O(n) work",
                    "O(n)", "unbounded"], 1,
                   "The same accounting that makes push O(1)."),
            ],
            exercises=[
                _ex("tscourse-w18-fq-1", "Move the index",
                    "Advance the head instead of moving every element.",
                    'class Queue<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  private head = 0;\n'
                    '  enqueue(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.head >= this.items.length) {\n'
                    '      return undefined;\n    }\n'
                    '    const value = this.items[this.head];\n'
                    '    this.head = this.head + 1;\n'
                    '    return value;\n  }\n}\n'
                    'const q = new Queue<string>();\n'
                    'q.enqueue("a");\n'
                    'q.enqueue("b");\n'
                    'console.log(`${q.dequeue() ?? "-"} ${q.dequeue() ?? "-"} ${q.dequeue() ?? "-"}`);\n',
                    '    this.head = this.head + 1;', [("", "a b -")],
                    hints=["Nothing in the array moves; only the marker does.",
                           "Write this.head = this.head + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-fq-2", "Size, minus what has gone",
                    "Report how many items are still waiting, not how many the array holds.",
                    'class Queue<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  private head = 0;\n'
                    '  enqueue(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.head >= this.items.length) {\n'
                    '      return undefined;\n    }\n'
                    '    const value = this.items[this.head];\n'
                    '    this.head = this.head + 1;\n'
                    '    return value;\n  }\n'
                    '  get size(): number {\n'
                    '    return this.items.length - this.head;\n  }\n}\n'
                    'const q = new Queue<number>();\n'
                    'q.enqueue(1);\n'
                    'q.enqueue(2);\n'
                    'q.dequeue();\n'
                    'console.log(q.size);\n',
                    '    return this.items.length - this.head;', [("", "1")],
                    hints=["The consumed slots are still in the array, so subtract them.",
                           "Write return this.items.length - this.head;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-fq-3", "The empty check",
                    "Return the absence when the head has caught up with the end.",
                    'class Queue<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  private head = 0;\n'
                    '  enqueue(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.head >= this.items.length) {\n'
                    '      return undefined;\n    }\n'
                    '    const value = this.items[this.head];\n'
                    '    this.head = this.head + 1;\n'
                    '    return value;\n  }\n}\n'
                    'const q = new Queue<number>();\n'
                    'console.log(q.dequeue() === undefined ? "empty" : "not empty");\n',
                    '    if (this.head >= this.items.length) {', [("", "empty")],
                    hints=["Empty is not `length === 0` any more — it is the head reaching the end.",
                           "Write if (this.head >= this.items.length) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-fq-4", "Zero moves",
                    "Drain the queue through the head index and report the move count, which is now nothing.",
                    _NUMS +
                    'class Queue<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  private head = 0;\n'
                    '  moves = 0;\n'
                    '  enqueue(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.head >= this.items.length) {\n'
                    '      return undefined;\n    }\n'
                    '    const value = this.items[this.head];\n'
                    '    this.head = this.head + 1;\n'
                    '    return value;\n  }\n'
                    '  get size(): number {\n'
                    '    return this.items.length - this.head;\n  }\n}\n'
                    'const q = new Queue<number>();\n'
                    'for (const n of nums) {\n'
                    '  q.enqueue(n);\n}\n'
                    'while (q.size > 0) {\n'
                    '  q.dequeue();\n}\n'
                    'console.log(`moves ${q.moves}`);\n',
                    'while (q.size > 0) {',
                    [("10 20 30 40", "moves 0"), ("1 2", "moves 0")],
                    hints=["Lesson 5's program printed `moves 6` for four items; this one moves nothing at all.",
                           "Write while (q.size > 0) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-fq-5", "Compact, occasionally",
                    "Reclaim the dead slots only when half the array is dead, so the O(n) is amortised away.",
                    'class Queue<T> {\n'
                    '  private items: T[] = [];\n'
                    '  private head = 0;\n'
                    '  compactions = 0;\n'
                    '  enqueue(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.head >= this.items.length) {\n'
                    '      return undefined;\n    }\n'
                    '    const value = this.items[this.head];\n'
                    '    this.head = this.head + 1;\n'
                    '    if (this.head * 2 > this.items.length) {\n'
                    '      this.items = this.items.slice(this.head);\n'
                    '      this.head = 0;\n'
                    '      this.compactions = this.compactions + 1;\n    }\n'
                    '    return value;\n  }\n}\n'
                    'const q = new Queue<number>();\n'
                    'for (const n of [1, 2, 3, 4]) {\n'
                    '  q.enqueue(n);\n}\n'
                    'for (let i = 0; i < 4; i = i + 1) {\n'
                    '  q.dequeue();\n}\n'
                    'console.log(`compactions ${q.compactions}`);\n',
                    '    if (this.head * 2 > this.items.length) {',
                    # Four items, compacting when more than half the array is dead:
                    # heads 1 and 2 are not past halfway, head 3 of 4 is (one
                    # compaction, leaving one item), then head 1 of 1 is (the second).
                    [("", "compactions 2")],
                    hints=["Compact when more than half the array is behind the head.",
                           "Write if (this.head * 2 > this.items.length) {"],
                    difficulty="Hard"),
                _ex("tscourse-w18-fq-6", "A queue from two stacks",
                    "Pour the inbox into the outbox — which reverses it — only when the outbox is empty.",
                    _WORDS +
                    'class TwoStackQueue<T> {\n'
                    '  private readonly inbox: T[] = [];\n'
                    '  private readonly outbox: T[] = [];\n'
                    '  enqueue(value: T): void {\n'
                    '    this.inbox.push(value);\n  }\n'
                    '  dequeue(): T | undefined {\n'
                    '    if (this.outbox.length === 0) {\n'
                    '      while (this.inbox.length > 0) {\n'
                    '        const v = this.inbox.pop();\n'
                    '        if (v !== undefined) {\n'
                    '          this.outbox.push(v);\n        }\n      }\n    }\n'
                    '    return this.outbox.pop();\n  }\n}\n'
                    'const q = new TwoStackQueue<string>();\n'
                    'for (const w of words) {\n'
                    '  q.enqueue(w);\n}\n'
                    'const out: string[] = [];\n'
                    'for (let i = 0; i < words.length; i = i + 1) {\n'
                    '  out.push(q.dequeue() ?? "-");\n}\n'
                    'console.log(out.join(" "));\n',
                    '      while (this.inbox.length > 0) {',
                    [("a b c", "a b c"), ("one two", "one two")],
                    hints=["Popping everything off one stack onto another reverses it, which turns LIFO into FIFO.",
                           "Only do it when the outbox has run dry, or the order breaks.",
                           "Write while (this.inbox.length > 0) {"],
                    difficulty="Hard"),
                _fix("tscourse-w18-fq-fix1", "Fix the size that never went down",
                     "This prints `2` after one dequeue. `items.length` counts the dead slots before the head as well — the array never shrinks, which is the whole point of the design.",
                     'class Queue<T> {\n'
                     '  private readonly items: T[] = [];\n'
                     '  private head = 0;\n'
                     '  enqueue(value: T): void {\n'
                     '    this.items.push(value);\n  }\n'
                     '  dequeue(): T | undefined {\n'
                     '    if (this.head >= this.items.length) {\n'
                     '      return undefined;\n    }\n'
                     '    const value = this.items[this.head];\n'
                     '    this.head = this.head + 1;\n'
                     '    return value;\n  }\n'
                     '  get size(): number {\n'
                     '    return this.items.length;\n  }\n}\n'
                     'const q = new Queue<number>();\n'
                     'q.enqueue(1);\n'
                     'q.enqueue(2);\n'
                     'q.dequeue();\n'
                     'console.log(q.size);\n',
                     'class Queue<T> {\n'
                     '  private readonly items: T[] = [];\n'
                     '  private head = 0;\n'
                     '  enqueue(value: T): void {\n'
                     '    this.items.push(value);\n  }\n'
                     '  dequeue(): T | undefined {\n'
                     '    if (this.head >= this.items.length) {\n'
                     '      return undefined;\n    }\n'
                     '    const value = this.items[this.head];\n'
                     '    this.head = this.head + 1;\n'
                     '    return value;\n  }\n'
                     '  get size(): number {\n'
                     '    return this.items.length - this.head;\n  }\n}\n'
                     'const q = new Queue<number>();\n'
                     'q.enqueue(1);\n'
                     'q.enqueue(2);\n'
                     'q.dequeue();\n'
                     'console.log(q.size);\n',
                     [("", "1")],
                     hints=["Nothing was removed from the array — that is the design.",
                            "The waiting items are the ones from `head` onwards.",
                            "Subtract the head."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A ring buffer differs from a head-index queue in that it…",
                   ["is slower", "wraps around a fixed-size array, so memory is constant",
                    "is unordered", "needs a class"], 1,
                   "Which is what real implementations use."),
                _q("The two-stack queue is amortised O(1) because…",
                   ["the stacks are small", "each element moves across exactly once",
                    "pop is free", "it compacts"], 1,
                   "Total work is bounded by the number of elements."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w18-deque", "Both ends: the deque",
            "One structure that can stand in for either.",
            """
A **deque** (pronounced "deck", for double-ended queue) adds and removes at both
ends:

```ts
class Deque<T> {
  private readonly items: T[] = [];
  pushBack(value: T): void { this.items.push(value); }
  pushFront(value: T): void { this.items.unshift(value); }
  popBack(): T | undefined { return this.items.pop(); }
  popFront(): T | undefined { return this.items.shift(); }
  get size(): number { return this.items.length; }
}
```

Use only `pushBack`/`popBack` and it is a stack. Use only `pushBack`/`popFront`
and it is a queue. That is the point: a deque is the general case, and both of
this week's structures are restrictions of it.

## The honest note about cost

This implementation's front operations are **O(n)**, because `unshift` and `shift`
are. A real deque is a ring buffer or a doubly linked list (week 20), where both
ends are O(1). For a small deque the array version is fine and clear — but the
gap is worth knowing, and it is the reason "use a deque" in a performance
discussion always means the ring-buffer kind.

## What a deque is actually for

**Capping a history.** Lesson 4 mentioned it: an undo stack with a limit pushes at
one end and drops from the other. That needs both ends, which is why a plain stack
cannot express it.

**Sliding-window problems.** The window's maximum can be maintained by a deque
holding *indices*, kept in decreasing order of value: push at the back, drop stale
indices from the front, and the front is always the answer. That is week 23's
sliding-window material, and this is where the structure it needs is built.

**Anything that is a queue with a priority exception** — an urgent job goes to the
front rather than the back.

## Restricting it is a feature

If a function only ever needs to take from the front, give it a parameter type
that only offers that:

```ts
interface Source<T> {
  popFront(): T | undefined;
}
function drain<T>(source: Source<T>): readonly T[] { … }
```

Week 12's structural typing means the `Deque` satisfies this without declaring
anything. Narrowing what a caller *can* do is the same instinct as keeping a
module's export surface small (week 16) — and here the compiler enforces it.

> ⚠️ **Common mistakes:** assuming the array-based front operations are O(1);
> reaching for a deque when a stack would say more about your intent; and
> forgetting that every one of the four methods has an empty case.
""",
            warmup=[
                _q("A deque supports…",
                   ["one end", "both ends, for add and remove", "the middle", "sorting"], 1,
                   "Hence double-ended."),
                _q("Using only `pushBack` and `popBack` makes it…",
                   ["a queue", "a stack", "a list", "a set"], 1,
                   "Both structures are restrictions of a deque."),
                _q("In the array implementation, front operations are…",
                   ["O(1)", "O(n)", "free", "O(log n)"], 1,
                   "`shift` and `unshift` move everything."),
                _q("Capping an undo history needs a deque because…",
                   ["it is faster", "you push at one end and drop from the other",
                    "of memory", "stacks cannot pop"], 1,
                   "A plain stack cannot express it."),
            ],
            exercises=[
                _ex("tscourse-w18-dq-1", "Push at the front",
                    "Add the urgent job at the front of the deque rather than the back.",
                    'class Deque<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  pushBack(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  pushFront(value: T): void {\n'
                    '    this.items.unshift(value);\n  }\n'
                    '  popFront(): T | undefined {\n'
                    '    return this.items.shift();\n  }\n'
                    '  get size(): number {\n'
                    '    return this.items.length;\n  }\n}\n'
                    'const d = new Deque<string>();\n'
                    'd.pushBack("normal");\n'
                    'd.pushFront("urgent");\n'
                    'console.log(`${d.popFront() ?? "-"} ${d.popFront() ?? "-"}`);\n',
                    '    this.items.unshift(value);', [("", "urgent normal")],
                    hints=["The method that adds at index 0.",
                           "Write this.items.unshift(value);"],
                    difficulty="Easy"),
                _ex("tscourse-w18-dq-2", "Use it as a stack",
                    "Take from the same end you added to.",
                    'class Deque<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  pushBack(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  popBack(): T | undefined {\n'
                    '    return this.items.pop();\n  }\n'
                    '  popFront(): T | undefined {\n'
                    '    return this.items.shift();\n  }\n}\n'
                    'const d = new Deque<number>();\n'
                    'd.pushBack(1);\n'
                    'd.pushBack(2);\n'
                    'console.log(`${d.popBack() ?? 0} ${d.popBack() ?? 0}`);\n',
                    'console.log(`${d.popBack() ?? 0} ${d.popBack() ?? 0}`);',
                    [("", "2 1")],
                    hints=["LIFO means both operations happen at the back.",
                           "Write console.log(`${d.popBack() ?? 0} ${d.popBack() ?? 0}`);"],
                    difficulty="Easy"),
                _ex("tscourse-w18-dq-3", "Cap the history",
                    "When the deque is full, drop the oldest item from the front before pushing the new one.",
                    _WORDS +
                    'class History {\n'
                    '  private readonly items: string[] = [];\n'
                    '  private readonly limit: number;\n'
                    '  constructor(limit: number) {\n'
                    '    this.limit = limit;\n  }\n'
                    '  record(action: string): void {\n'
                    '    this.items.push(action);\n'
                    '    if (this.items.length > this.limit) {\n'
                    '      this.items.shift();\n    }\n  }\n'
                    '  all(): readonly string[] {\n'
                    '    return [...this.items];\n  }\n}\n'
                    'const h = new History(3);\n'
                    'for (const w of words) {\n'
                    '  h.record(w);\n}\n'
                    'console.log(h.all().join(","));\n',
                    '      this.items.shift();',
                    [("a b c d e", "c,d,e"), ("a b", "a,b")],
                    hints=["The oldest item is at the front.",
                           "Write this.items.shift();"],
                    difficulty="Medium"),
                _ex("tscourse-w18-dq-4", "Only what the caller needs",
                    "Type the parameter as the one operation `drain` uses, so nothing else is reachable.",
                    _WORDS +
                    'interface Source<T> {\n'
                    '  popFront(): T | undefined;\n}\n'
                    'class Deque<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  pushBack(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  popFront(): T | undefined {\n'
                    '    return this.items.shift();\n  }\n}\n'
                    'function drain<T>(source: Source<T>): readonly T[] {\n'
                    '  const out: T[] = [];\n'
                    '  for (;;) {\n'
                    '    const v = source.popFront();\n'
                    '    if (v === undefined) {\n'
                    '      return out;\n    }\n'
                    '    out.push(v);\n  }\n}\n'
                    'const d = new Deque<string>();\n'
                    'for (const w of words) {\n'
                    '  d.pushBack(w);\n}\n'
                    'console.log(drain(d).join(" "));\n',
                    'function drain<T>(source: Source<T>): readonly T[] {',
                    [("a b c", "a b c")],
                    hints=["The parameter type is the interface, not the class — week 12's structural typing does the rest.",
                           "Write function drain<T>(source: Source<T>): readonly T[] {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-dq-5", "Front and back, alternately",
                    "Serve from alternate ends, so the output zig-zags inward.",
                    _WORDS +
                    'const items: string[] = [...words];\n'
                    'const out: string[] = [];\n'
                    'let front = true;\n'
                    'while (items.length > 0) {\n'
                    '  const v = front ? items.shift() : items.pop();\n'
                    '  if (v !== undefined) {\n'
                    '    out.push(v);\n  }\n'
                    '  front = !front;\n}\n'
                    'console.log(out.join(" "));\n',
                    '  const v = front ? items.shift() : items.pop();',
                    [("a b c d", "a d b c"), ("x", "x")],
                    hints=["One expression, choosing the end by the flag.",
                           "Write const v = front ? items.shift() : items.pop();"],
                    difficulty="Medium"),
                _fix("tscourse-w18-dq-fix1", "Fix the history that dropped the newest",
                     "The cap is enforced at the wrong end: recording five actions with a limit of three keeps `a,b,c` — the FIRST three — instead of the most recent three. The oldest item is the one to discard.",
                     _WORDS +
                     'class History {\n'
                     '  private readonly items: string[] = [];\n'
                     '  private readonly limit: number;\n'
                     '  constructor(limit: number) {\n'
                     '    this.limit = limit;\n  }\n'
                     '  record(action: string): void {\n'
                     '    this.items.push(action);\n'
                     '    if (this.items.length > this.limit) {\n'
                     '      this.items.pop();\n    }\n  }\n'
                     '  all(): readonly string[] {\n'
                     '    return [...this.items];\n  }\n}\n'
                     'const h = new History(3);\n'
                     'for (const w of words) {\n'
                     '  h.record(w);\n}\n'
                     'console.log(h.all().join(","));\n',
                     _WORDS +
                     'class History {\n'
                     '  private readonly items: string[] = [];\n'
                     '  private readonly limit: number;\n'
                     '  constructor(limit: number) {\n'
                     '    this.limit = limit;\n  }\n'
                     '  record(action: string): void {\n'
                     '    this.items.push(action);\n'
                     '    if (this.items.length > this.limit) {\n'
                     '      this.items.shift();\n    }\n  }\n'
                     '  all(): readonly string[] {\n'
                     '    return [...this.items];\n  }\n}\n'
                     'const h = new History(3);\n'
                     'for (const w of words) {\n'
                     '  h.record(w);\n}\n'
                     'console.log(h.all().join(","));\n',
                     [("a b c d e", "c,d,e"), ("a b c", "a,b,c")],
                     hints=["`pop` removes the action that was just recorded, which is the one you wanted to keep.",
                            "Drop from the other end.",
                            "Write this.items.shift();"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A real O(1)-at-both-ends deque is built on…",
                   ["an array", "a ring buffer or a doubly linked list", "a Map", "two arrays"], 1,
                   "Week 20 builds the linked list."),
                _q("Typing a parameter as `{ popFront(): T | undefined }` rather than `Deque<T>`…",
                   ["is slower", "offers the caller only what the function uses", "needs a class",
                    "is unsafe"], 1,
                   "The same instinct as a small export surface."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w18-monotonic", "The monotonic stack",
            "One pass, one stack, and an invariant that makes it work.",
            """
Some problems look as though they need a nested loop and do not. The clue is a
question of the form *"for each element, find the first later element that is
bigger/smaller"*.

## Next greater element

Given `[2, 1, 5, 3]`, for each element find the first element to its right that is
larger, or `-1`:

```
2 → 5
1 → 5
5 → -1
3 → -1
```

The obvious solution is O(n²): for each element, scan right. The stack solution is
O(n):

```ts
function nextGreater(nums: readonly number[]): readonly number[] {
  const out: number[] = new Array(nums.length).fill(-1);
  const idx: number[] = [];                      // INDICES, not values

  for (let i = 0; i < nums.length; i = i + 1) {
    const cur = nums[i];
    if (cur === undefined) { continue; }
    while (idx.length > 0) {
      const top = idx[idx.length - 1];
      if (top === undefined) { break; }
      const atTop = nums[top];
      if (atTop === undefined || atTop >= cur) { break; }
      out[top] = cur;                            // cur is the answer for idx top
      idx.pop();
    }
    idx.push(i);
  }
  return out;
}
```

## The invariant

> The values at the indices on the stack are in **decreasing** order, from bottom
> to top.

That is what "monotonic" means, and it is why the algorithm is correct: everything
on the stack is still waiting for its answer, and anything smaller than the current
element must have had its answer *found* — because the current element is the first
one bigger than it. Pop it and record it.

## Why it is O(n), despite a `while` inside a `for`

Count the *pushes*: exactly one per element, n in total. Count the *pops*: at most
one per element, because an index is pushed once and never returns. So the inner
loop runs at most n times **across the entire outer loop**, not per iteration. The
total is O(n).

This accounting — "count the total work, not the nesting" — is the same argument as
lesson 6's amortisation, and it is how you recognise the pattern in an interview
rather than being talked out of it.

## Why indices and not values

The answer has to be written into `out[top]` — the slot belonging to the element
being resolved. With values on the stack you would not know where that is.
Keeping indices and reading `nums[top]` when you need the value is the standard
form, and it is why every monotonic-stack solution you read looks like this.

## The variations

* **Decreasing instead of increasing** — flip the comparison, and you have
  next-*smaller*.
* **Distance rather than value** — write `i - top` into `out[top]` and you have
  "how many days until a warmer day", the classic *daily temperatures*.
* **Spans looking left** — walk the array backwards, or interpret the stack as
  "how far back until something bigger".
* **Largest rectangle in a histogram** — the hardest well-known member of the
  family, and the same invariant.

> ⚠️ **Common mistakes:** pushing values instead of indices; using `>` where `>=`
> was needed (which matters when elements are equal); and forgetting that
> everything left on the stack at the end has no answer, so `out` must be
> pre-filled with the default.
""",
            warmup=[
                _q("A monotonic stack keeps…",
                   ["the array sorted", "its own contents ordered by its rule", "one element",
                    "counts"], 1,
                   "Here, decreasing by value from bottom to top."),
                _q("The stack holds…",
                   ["values", "indices, so the answer can be written into the right slot",
                    "pairs", "booleans"], 1,
                   "The standard form."),
                _q("Next-greater-element is O(n) because…",
                   ["the inner loop is short", "each index is pushed once and popped at most once",
                    "it is sorted", "of the fill"], 1,
                   "Count the total work, not the nesting."),
                _q("Elements still on the stack at the end…",
                   ["are an error", "have no answer — hence the pre-filled default", "are the answer",
                    "are popped"], 1,
                   "Which is what `fill(-1)` is for."),
            ],
            exercises=[
                _ex("tscourse-w18-mo-1", "Pre-fill the answers",
                    "Start every slot at -1, so anything left on the stack keeps the default.",
                    _NUMS +
                    'const out: number[] = new Array(nums.length).fill(-1);\n'
                    'const idx: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cur = nums[i];\n'
                    '  if (cur === undefined) {\n'
                    '    continue;\n  }\n'
                    '  while (idx.length > 0) {\n'
                    '    const top = idx[idx.length - 1];\n'
                    '    if (top === undefined) {\n'
                    '      break;\n    }\n'
                    '    const atTop = nums[top];\n'
                    '    if (atTop === undefined || atTop >= cur) {\n'
                    '      break;\n    }\n'
                    '    out[top] = cur;\n'
                    '    idx.pop();\n  }\n'
                    '  idx.push(i);\n}\n'
                    'console.log(out.join(" "));\n',
                    'const out: number[] = new Array(nums.length).fill(-1);',
                    [("2 1 5 3", "5 5 -1 -1"), ("1 2 3", "2 3 -1"), ("3 2 1", "-1 -1 -1")],
                    hints=["An element whose answer is never found keeps whatever you pre-filled.",
                           "Write const out: number[] = new Array(nums.length).fill(-1);"],
                    difficulty="Medium"),
                _ex("tscourse-w18-mo-2", "Resolve the smaller ones",
                    "While the current element beats the value at the top of the stack, that element's answer is the current one.",
                    _NUMS +
                    'const out: number[] = new Array(nums.length).fill(-1);\n'
                    'const idx: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cur = nums[i];\n'
                    '  if (cur === undefined) {\n'
                    '    continue;\n  }\n'
                    '  while (idx.length > 0) {\n'
                    '    const top = idx[idx.length - 1];\n'
                    '    if (top === undefined) {\n'
                    '      break;\n    }\n'
                    '    const atTop = nums[top];\n'
                    '    if (atTop === undefined || atTop >= cur) {\n'
                    '      break;\n    }\n'
                    '    out[top] = cur;\n'
                    '    idx.pop();\n  }\n'
                    '  idx.push(i);\n}\n'
                    'console.log(out.join(" "));\n',
                    '    out[top] = cur;',
                    [("2 1 5 3", "5 5 -1 -1"), ("4 4 5", "5 5 -1")],
                    hints=["The slot belonging to the popped INDEX gets the current value.",
                           "Write out[top] = cur;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-mo-3", "Days until warmer",
                    "Write the distance instead of the value, which turns the same code into daily temperatures.",
                    _NUMS +
                    'const out: number[] = new Array(nums.length).fill(0);\n'
                    'const idx: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cur = nums[i];\n'
                    '  if (cur === undefined) {\n'
                    '    continue;\n  }\n'
                    '  while (idx.length > 0) {\n'
                    '    const top = idx[idx.length - 1];\n'
                    '    if (top === undefined) {\n'
                    '      break;\n    }\n'
                    '    const atTop = nums[top];\n'
                    '    if (atTop === undefined || atTop >= cur) {\n'
                    '      break;\n    }\n'
                    '    out[top] = i - top;\n'
                    '    idx.pop();\n  }\n'
                    '  idx.push(i);\n}\n'
                    'console.log(out.join(" "));\n',
                    '    out[top] = i - top;',
                    [("73 74 75 71 69 72 76 73", "1 1 4 2 1 1 0 0"), ("30 40 50 60", "1 1 1 0")],
                    hints=["The answer is how far away the warmer day is, not how warm it is.",
                           "Write out[top] = i - top;"],
                    difficulty="Medium"),
                _ex("tscourse-w18-mo-4", "Next smaller instead",
                    "Flip the comparison, so each element's answer is the first later element that is smaller.",
                    _NUMS +
                    'const out: number[] = new Array(nums.length).fill(-1);\n'
                    'const idx: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cur = nums[i];\n'
                    '  if (cur === undefined) {\n'
                    '    continue;\n  }\n'
                    '  while (idx.length > 0) {\n'
                    '    const top = idx[idx.length - 1];\n'
                    '    if (top === undefined) {\n'
                    '      break;\n    }\n'
                    '    const atTop = nums[top];\n'
                    '    if (atTop === undefined || atTop <= cur) {\n'
                    '      break;\n    }\n'
                    '    out[top] = cur;\n'
                    '    idx.pop();\n  }\n'
                    '  idx.push(i);\n}\n'
                    'console.log(out.join(" "));\n',
                    '    if (atTop === undefined || atTop <= cur) {',
                    [("2 1 5 3", "1 -1 3 -1"), ("1 2 3", "-1 -1 -1")],
                    hints=["The invariant is now increasing rather than decreasing, so the test reverses.",
                           "Write if (atTop === undefined || atTop <= cur) {"],
                    difficulty="Medium"),
                _ex("tscourse-w18-mo-5", "How many are still waiting",
                    "Report the stack's height at the end, which is how many elements never found an answer.",
                    _NUMS +
                    'const idx: number[] = [];\n'
                    'for (let i = 0; i < nums.length; i = i + 1) {\n'
                    '  const cur = nums[i];\n'
                    '  if (cur === undefined) {\n'
                    '    continue;\n  }\n'
                    '  while (idx.length > 0) {\n'
                    '    const top = idx[idx.length - 1];\n'
                    '    if (top === undefined) {\n'
                    '      break;\n    }\n'
                    '    const atTop = nums[top];\n'
                    '    if (atTop === undefined || atTop >= cur) {\n'
                    '      break;\n    }\n'
                    '    idx.pop();\n  }\n'
                    '  idx.push(i);\n}\n'
                    'console.log(`unresolved ${idx.length}`);\n',
                    'console.log(`unresolved ${idx.length}`);',
                    [("2 1 5 3", "unresolved 2"), ("3 2 1", "unresolved 3"), ("1 2 3", "unresolved 1")],
                    hints=["Whatever is left on the stack when the pass ends had no larger element after it.",
                           "Write console.log(`unresolved ${idx.length}`);"],
                    difficulty="Medium"),
                _fix("tscourse-w18-mo-fix1", "Fix the stack that held values",
                     "This pushes the values themselves, so when an element is resolved there is no way to know which slot the answer belongs in — it writes to the wrong index and prints `-1 5 -1 -1` for `2 1 5 3`. Keep indices instead.",
                     _NUMS +
                     'const out: number[] = new Array(nums.length).fill(-1);\n'
                     'const stack: number[] = [];\n'
                     'for (let i = 0; i < nums.length; i = i + 1) {\n'
                     '  const cur = nums[i];\n'
                     '  if (cur === undefined) {\n'
                     '    continue;\n  }\n'
                     '  while (stack.length > 0) {\n'
                     '    const top = stack[stack.length - 1];\n'
                     '    if (top === undefined || top >= cur) {\n'
                     '      break;\n    }\n'
                     '    out[top] = cur;\n'
                     '    stack.pop();\n  }\n'
                     '  stack.push(cur);\n}\n'
                     'console.log(out.join(" "));\n',
                     _NUMS +
                     'const out: number[] = new Array(nums.length).fill(-1);\n'
                     'const idx: number[] = [];\n'
                     'for (let i = 0; i < nums.length; i = i + 1) {\n'
                     '  const cur = nums[i];\n'
                     '  if (cur === undefined) {\n'
                     '    continue;\n  }\n'
                     '  while (idx.length > 0) {\n'
                     '    const top = idx[idx.length - 1];\n'
                     '    if (top === undefined) {\n'
                     '      break;\n    }\n'
                     '    const atTop = nums[top];\n'
                     '    if (atTop === undefined || atTop >= cur) {\n'
                     '      break;\n    }\n'
                     '    out[top] = cur;\n'
                     '    idx.pop();\n  }\n'
                     '  idx.push(i);\n}\n'
                     'console.log(out.join(" "));\n',
                     [("2 1 5 3", "5 5 -1 -1"), ("1 2 3", "2 3 -1")],
                     hints=["`out[top]` needs `top` to be a POSITION, and the starter is putting a value there.",
                            "Push `i`, and read `nums[top]` whenever you need the value at the top.",
                            "That means one extra binding inside the while loop, and its own undefined check."],
                     difficulty="Hard"),
            ],
            quiz=[
                _q("Using `>` where `>=` belongs matters when…",
                   ["never", "elements are equal", "the array is sorted", "the array is empty"], 1,
                   "Equal elements are where these solutions usually break."),
                _q("Largest rectangle in a histogram is…",
                   ["unrelated", "the hardest well-known member of this family, on the same invariant",
                    "O(n²)", "a queue problem"], 1,
                   "Same stack, more bookkeeping."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #18 — undo and redo",
        """
Budget Buddy gets a history. Commands arrive one per line and are applied to the
ledger; `undo` reverses the most recent one; `redo` puts it back.

```
add coffee 325
add rent 90000
undo
redo
add tea 200
undo
```

```
add coffee 325 -> total $3.25
add rent 90000 -> total $903.25
undo add rent -> total $3.25
redo add rent -> total $903.25
add tea 200 -> total $905.25
undo add tea -> total $903.25
Entries:  2
Total:    $903.25
History:  2 undoable, 0 redoable
```

**The commands:**

* `add <desc> <cents>` — append the entry. Print
  `add <desc> <cents> -> total $X.XX`.
* `remove` — drop the most recent entry. Print `remove <desc> -> total $X.XX`, or
  `remove (nothing to remove)` when the ledger is empty.
* `undo` — reverse the most recent command. Print `undo <what> -> total $X.XX`,
  where `<what>` is `add <desc>` or `remove <desc>`; print
  `undo (nothing to undo)` when there is nothing.
* `redo` — reapply the most recently undone command, with the same shape of
  output, or `redo (nothing to redo)`.

**What makes this the week's capstone rather than a string exercise:**

1. **Two stacks**, exactly as lesson 4 described — and the rule: `add` and
   `remove` both **clear the redo stack**, because that future no longer exists.
   `undo` and `redo` do not.
2. **Each history entry carries what reversing it needs.** Undoing an `add` means
   removing that entry; undoing a `remove` means putting the removed entry *back*.
   So the stack holds the entry itself, not just the command's name — the second
   of lesson 4's three designs.
3. **Every stack operation handles its empty case.** There is no `!` in the file:
   four commands, four possible underflows, all of them reachable from the tests.

The summary at the end reports the entry count, the total, and the height of both
stacks. Empty input prints only the summary, with a zero total and an empty
history.
""",
        _ch("tscourse-w18-capstone", "Budget Buddy #18", "Hard",
            "Apply the commands, keep an undo and a redo stack of reversible changes, and "
            "report the history at the end.",
            _FS +
            'interface Entry {\n'
            '  readonly desc: string;\n'
            '  readonly cents: number;\n}\n'
            'interface Change {\n'
            '  readonly kind: "add" | "remove";\n'
            '  readonly entry: Entry;\n}\n'
            'const entries: Entry[] = [];\n'
            'const undoStack: Change[] = [];\n'
            'const redoStack: Change[] = [];\n'
            'function total(): string {\n'
            '  let cents = 0;\n'
            '  for (const e of entries) {\n'
            '    cents = cents + e.cents;\n  }\n'
            '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
            'function apply(change: Change): void {\n'
            '  if (change.kind === "add") {\n'
            '    entries.push(change.entry);\n'
            '  } else {\n'
            '    entries.pop();\n  }\n}\n'
            'function invert(change: Change): Change {\n'
            '  return { kind: change.kind === "add" ? "remove" : "add", entry: change.entry };\n}\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'for (const line of lines) {\n'
            '  const parts = line.trim().split(/\\s+/);\n'
            '  const command = parts[0] ?? "";\n'
            '  if (command === "add") {\n'
            '    const desc = parts[1] ?? "";\n'
            '    const cents = Number(parts[2] ?? "0");\n'
            '    const change: Change = { kind: "add", entry: { desc, cents } };\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    redoStack.length = 0;\n'
            '    console.log(`add ${desc} ${cents} -> total ${total()}`);\n'
            '  } else if (command === "remove") {\n'
            '    const last = entries[entries.length - 1];\n'
            '    if (last === undefined) {\n'
            '      console.log("remove (nothing to remove)");\n'
            '      continue;\n    }\n'
            '    const change: Change = { kind: "remove", entry: last };\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    redoStack.length = 0;\n'
            '    console.log(`remove ${last.desc} -> total ${total()}`);\n'
            '  } else if (command === "undo") {\n'
            '    const change = undoStack.pop();\n'
            '    if (change === undefined) {\n'
            '      console.log("undo (nothing to undo)");\n'
            '      continue;\n    }\n'
            '    apply(invert(change));\n'
            '    redoStack.push(change);\n'
            '    console.log(`undo ${change.kind} ${change.entry.desc} -> total ${total()}`);\n'
            '  } else if (command === "redo") {\n'
            '    const change = redoStack.pop();\n'
            '    if (change === undefined) {\n'
            '      console.log("redo (nothing to redo)");\n'
            '      continue;\n    }\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    console.log(`redo ${change.kind} ${change.entry.desc} -> total ${total()}`);\n  }\n}\n'
            'console.log(`Entries:  ${entries.length}`);\n'
            'console.log(`Total:    ${total()}`);\n'
            'console.log(`History:  ${undoStack.length} undoable, ${redoStack.length} redoable`);\n',
            'for (const line of lines) {\n'
            '  const parts = line.trim().split(/\\s+/);\n'
            '  const command = parts[0] ?? "";\n'
            '  if (command === "add") {\n'
            '    const desc = parts[1] ?? "";\n'
            '    const cents = Number(parts[2] ?? "0");\n'
            '    const change: Change = { kind: "add", entry: { desc, cents } };\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    redoStack.length = 0;\n'
            '    console.log(`add ${desc} ${cents} -> total ${total()}`);\n'
            '  } else if (command === "remove") {\n'
            '    const last = entries[entries.length - 1];\n'
            '    if (last === undefined) {\n'
            '      console.log("remove (nothing to remove)");\n'
            '      continue;\n    }\n'
            '    const change: Change = { kind: "remove", entry: last };\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    redoStack.length = 0;\n'
            '    console.log(`remove ${last.desc} -> total ${total()}`);\n'
            '  } else if (command === "undo") {\n'
            '    const change = undoStack.pop();\n'
            '    if (change === undefined) {\n'
            '      console.log("undo (nothing to undo)");\n'
            '      continue;\n    }\n'
            '    apply(invert(change));\n'
            '    redoStack.push(change);\n'
            '    console.log(`undo ${change.kind} ${change.entry.desc} -> total ${total()}`);\n'
            '  } else if (command === "redo") {\n'
            '    const change = redoStack.pop();\n'
            '    if (change === undefined) {\n'
            '      console.log("redo (nothing to redo)");\n'
            '      continue;\n    }\n'
            '    apply(change);\n'
            '    undoStack.push(change);\n'
            '    console.log(`redo ${change.kind} ${change.entry.desc} -> total ${total()}`);\n  }\n}',
            [("add coffee 325\nadd rent 90000\nundo\nredo\nadd tea 200\nundo",
              "add coffee 325 -> total $3.25\nadd rent 90000 -> total $903.25\n"
              "undo add rent -> total $3.25\nredo add rent -> total $903.25\n"
              "add tea 200 -> total $905.25\nundo add tea -> total $903.25\n"
              "Entries:  2\nTotal:    $903.25\nHistory:  2 undoable, 1 redoable"),
             ("undo\nredo",
              "undo (nothing to undo)\nredo (nothing to redo)\n"
              "Entries:  0\nTotal:    $0.00\nHistory:  0 undoable, 0 redoable"),
             ("add coffee 325\nremove\nundo",
              "add coffee 325 -> total $3.25\nremove coffee -> total $0.00\n"
              "undo remove coffee -> total $3.25\n"
              "Entries:  1\nTotal:    $3.25\nHistory:  1 undoable, 1 redoable"),
             ("add a 100\nadd b 200\nundo\nadd c 300",
              "add a 100 -> total $1.00\nadd b 200 -> total $3.00\n"
              "undo add b -> total $1.00\nadd c 300 -> total $4.00\n"
              "Entries:  2\nTotal:    $4.00\nHistory:  2 undoable, 0 redoable"),
             ("remove",
              "remove (nothing to remove)\nEntries:  0\nTotal:    $0.00\n"
              "History:  0 undoable, 0 redoable"),
             ("", "Entries:  0\nTotal:    $0.00\nHistory:  0 undoable, 0 redoable")],
            hints=["A `Change` carries both the kind and the entry, which is what makes it reversible.",
                   "`invert` swaps `add` for `remove` and keeps the same entry — undoing an add removes it, undoing a remove puts it back.",
                   "`add` and `remove` clear the redo stack; `undo` and `redo` must NOT.",
                   "`remove` has to read the last entry BEFORE applying the change, because that is what it will need to reverse.",
                   "Every pop and every index access handles its undefined — there is no `!` anywhere in the reference.",
                   "The fourth test is the redo rule: `undo` then a new `add` leaves 0 redoable."]),
        example_io="add coffee 325 -> total $3.25\nadd rent 90000 -> total $903.25\nundo add rent -> total $3.25\nEntries:  1\nTotal:    $3.25\nHistory:  1 undoable, 1 redoable",
        rubric=["two stacks, holding reversible changes rather than command names",
                "`add` and `remove` clear the redo stack; `undo` and `redo` do not",
                "undoing a `remove` restores the removed entry, not a fresh one",
                "`remove` captures the entry before it applies the change",
                "all four commands handle the empty case, and none of them uses `!`",
                "the total is recomputed from the entries rather than tracked separately",
                "an unknown command is ignored rather than crashing",
                "empty input prints the summary alone"],
        stretch=_ch("tscourse-w18-capstone-stretch", "Budget Buddy #18 (stretch)", "Hard",
                    "Cap the undo history at three changes, dropping the oldest when a fourth "
                    "arrives — which is lesson 7's point that a bounded history needs BOTH ends. "
                    "Print `dropped <desc>` when one falls off, and report how many changes have "
                    "been forgotten at the end.",
                    _FS +
                    'interface Change {\n'
                    '  readonly kind: "add";\n'
                    '  readonly desc: string;\n'
                    '  readonly cents: number;\n}\n'
                    'const LIMIT = 3;\n'
                    'const history: Change[] = [];\n'
                    'let dropped = 0;\n'
                    'function record(change: Change): void {\n'
                    '  history.push(change);\n'
                    '  if (history.length > LIMIT) {\n'
                    '    const oldest = history.shift();\n'
                    '    if (oldest !== undefined) {\n'
                    '      dropped = dropped + 1;\n'
                    '      console.log(`dropped ${oldest.desc}`);\n    }\n  }\n}\n'
                    'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
                    'let total = 0;\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(/\\s+/);\n'
                    '  if ((parts[0] ?? "") !== "add") {\n'
                    '    continue;\n  }\n'
                    '  const desc = parts[1] ?? "";\n'
                    '  const cents = Number(parts[2] ?? "0");\n'
                    '  total = total + cents;\n'
                    '  record({ kind: "add", desc, cents });\n}\n'
                    'console.log(`Total:    $${(total / 100).toFixed(2)}`);\n'
                    'console.log(`History:  ${history.length} undoable, ${dropped} forgotten`);\n',
                    'function record(change: Change): void {\n'
                    '  history.push(change);\n'
                    '  if (history.length > LIMIT) {\n'
                    '    const oldest = history.shift();\n'
                    '    if (oldest !== undefined) {\n'
                    '      dropped = dropped + 1;\n'
                    '      console.log(`dropped ${oldest.desc}`);\n    }\n  }\n}',
                    [("add a 100\nadd b 200\nadd c 300\nadd d 400\nadd e 500",
                      "dropped a\ndropped b\nTotal:    $15.00\nHistory:  3 undoable, 2 forgotten"),
                     ("add a 100\nadd b 200",
                      "Total:    $3.00\nHistory:  2 undoable, 0 forgotten"),
                     ("", "Total:    $0.00\nHistory:  0 undoable, 0 forgotten")],
                    hints=["Push at the back as always, and drop from the FRONT when the limit is exceeded.",
                           "`shift()` is the O(n) operation lesson 5 warned about — at a limit of three, that is three moves, and clarity wins.",
                           "The dropped change is the oldest one, so its desc is what to report.",
                           "Count the drops as they happen rather than deriving the number afterwards."]),
    ),
))
