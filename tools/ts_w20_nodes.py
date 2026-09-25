# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 20 — linked lists & trees. THE WEEK THAT CLOSES THE BUDGET BUDDY ARC.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ===========================================================================
# ONE SEQUENCING DECISION, TAKEN HERE AND RECORDED IN TS_ROADMAP.
# ===========================================================================
#
# Week 25 owns "Recursion & Backtracking", and no week before this one teaches
# recursion at all. But a tree is a *recursive data structure* — its type refers
# to itself — and the three honest options were:
#
#   (a) teach trees without recursion, using week 18's stack and queue only.
#       Contorted: `sum(node)` written as an explicit-stack loop teaches the
#       stack again and teaches nothing about trees.
#   (b) move week 25 forward. Breaks the month structure and orphans
#       backtracking.
#   (c) introduce recursion HERE, on the data structure where it is least
#       abstract, and let week 25 DEEPEN it.
#
# (c), and it is the same move weeks 13, 15 and 18 made — each deepens something
# an earlier week already used rather than pretending to introduce it. So:
#
#   * This week's lesson 5 introduces a recursive function on a recursive type,
#     and states the base case as "the null child", which is concrete rather
#     than a rule to memorise.
#   * Lesson 6 gives the SAME three traversals twice: recursively, and
#     iteratively with week 18's stack (depth-first) and queue (breadth-first).
#     That pairing is this week's best teaching, and it is only possible because
#     week 18 came first: DFS and BFS differ by ONE data structure, which is a
#     fact most people learn years later than they should.
#   * Week 25 then owns the call stack, recursion depth, recursion→iteration as a
#     technique, and backtracking. Its own file must be written as "you have been
#     recursing over trees since week 20; here is the whole story".
#
# ===========================================================================
# WHAT THE ENVIRONMENT ALLOWS, verified rather than assumed:
#
#   a self-referential `interface N { next: N | null }`      ✅ clean, runs
#   a recursive function over it                             ✅ clean, runs
#   `function*` / `yield` / `yield*`                         ✅ clean, runs
#   `[Symbol.iterator]()` returning an Iterator              ✅ clean, runs
#   a GENERATOR METHOD — `*[Symbol.iterator]()`              ✅ clean, runs
#
# Generators are runtime syntax, not type syntax, so Node's type stripping runs
# them untouched — which is what makes lesson 8 (`ts_iterators`, otherwise
# homeless per TS_ROADMAP) gradable as ordinary stdout.
#
# ONE TRAP, the same one week 18 hit: `constructor(readonly value: T) {}` is a
# parameter property and DIES at run time in strip-only mode. Every node class in
# this file declares its fields explicitly and assigns them in the constructor.
#
# ===========================================================================
# THE `strictNullChecks` TAX, which TS_ROADMAP flagged as this week's risk.
#
# It is real and it lands in exactly one place: a variable that walks a list has
# to be annotated, because inference narrows it too far.
#
#     let cur = head;             // inferred `N` if head is `N`…
#     cur = cur.next;             // ❌ …and then `N | null` will not assign
#     let cur: N | null = head;   // ✅ the annotation is load-bearing
#
# Same for the `next` binding inside `reverse`. Both ship as exercises rather
# than as footnotes, because every learner hits them within five minutes of
# starting. Node shapes are kept to two fields for the same reason.
# ---------------------------------------------------------------------------

# The singly linked node used across lessons 1-3. `next` is mutable on purpose —
# a list you cannot relink is not a list — while `value` is readonly, which is the
# honest split.
_NODE = (
    'interface N {\n'
    '  readonly value: number;\n'
    '  next: N | null;\n'
    '}\n'
)

# Build a list from an array, back to front, so each new node points at the one
# already built. Used often enough to be worth repeating verbatim.
_BUILD = (
    'function build(xs: readonly number[]): N | null {\n'
    '  let head: N | null = null;\n'
    '  for (let i = xs.length - 1; i >= 0; i = i - 1) {\n'
    '    head = { value: xs[i] ?? 0, next: head };\n  }\n'
    '  return head;\n}\n'
)

_SHOW = (
    'function show(head: N | null): string {\n'
    '  const out: number[] = [];\n'
    '  let cur: N | null = head;\n'
    '  while (cur !== null) {\n'
    '    out.push(cur.value);\n'
    '    cur = cur.next;\n  }\n'
    '  return out.join("->");\n}\n'
)

# The n-ary tree the category lessons and the capstone use.
_TREE = (
    'interface Cat {\n'
    '  readonly name: string;\n'
    '  readonly cents: number;\n'
    '  readonly kids: readonly Cat[];\n'
    '}\n'
)

# --- Week 20 --------------------------------------------------------------
_WEEKS.append(_week(
    20, 5, _M5,
    "Linked Lists & Trees",
    "Data that points at data: a type that refers to itself, the lists and trees it describes, the traversals that visit them, and the generators that hand them out one at a time.",
    """
Every structure so far has been an array — values in a row, reachable by index.
This week the values point at **each other**, and the type that describes them
refers to itself:

```ts
interface N {
  readonly value: number;
  next: N | null;          // ← a node, or the end
}
```

That `| null` is not decoration. It is what makes the type **finite**: without a
way to say "no next one", no such value could ever be constructed.

## Why bother, when arrays exist

Mostly you should not — in TypeScript, an array is the right answer far more often
than a linked list. Two honest reasons to know them anyway:

* **Interviews ask.** Reverse a list, find the middle, detect a cycle. These are
  the questions, and they are pure pointer manipulation.
* **The idea generalises.** One `next` is a list; two children are a **binary
  tree**; many children are a **tree**; arbitrary links are a **graph** (week 27).
  All four are the same idea with different branching, and this week is where that
  clicks.

## The payoff week 18 set up

A depth-first traversal and a breadth-first traversal differ by **exactly one data
structure**:

```ts
const next = stack.pop();       // depth-first
const next = queue.shift();     // breadth-first
```

Same loop, same code, different structure, completely different shape of answer.
That is why stacks and queues came first.

## And recursion

A tree's type refers to itself, so the function that walks it does too:

```ts
function total(c: Cat): number {
  let sum = c.cents;
  for (const kid of c.kids) { sum = sum + total(kid); }   // ← itself
  return sum;
}
```

This is your first recursive function in this course, and a tree is the gentlest
possible place for it: the **base case is the node with no children**, which is not
a rule to remember but a thing you can see. Week 25 comes back for the call stack,
the depth limit, and turning any recursion into a loop.

⏱️ Budget about **nine hours**. This week closes the Budget Buddy arc.
""",
    objectives=[
        "Write a type that refers to itself, and say what makes it terminate",
        "Say why a list-walking variable needs an explicit `| null` annotation",
        "Build, traverse and measure a singly linked list",
        "Insert and delete in the middle, and reverse a list in one pass",
        "Say what a `prev` pointer buys and what it costs",
        "Model a binary tree, insert into a BST, and compute its depth",
        "Write a recursive function over a tree, and name its base case",
        "Produce pre-order, in-order and post-order traversals",
        "Say what single change turns a depth-first traversal into a breadth-first one",
        "Walk an n-ary tree and roll values up from the leaves",
        "Make your own type iterable, with `[Symbol.iterator]`",
        "Write a generator, and delegate to another with `yield*`",
    ],
    why="Linked structures are where the shape of the data starts doing the work. Once you can see that a list, a tree and a graph are one idea with different branching — and that depth-first and breadth-first differ by a single line — a whole category of interview problem stops being a set of tricks to memorise. The generator half is the other payoff: it is how you hand out a large or infinite sequence without building it.",
    est_minutes=540,
    glossary=[
        _gloss("node", "A value plus one or more links to other nodes."),
        _gloss("recursive type", "A type whose definition mentions itself. Needs a non-recursive case to terminate."),
        _gloss("head", "The first node. Losing it loses the list."),
        _gloss("null terminator", "`next: N | null` — the `null` is how a list ends."),
        _gloss("singly linked", "One link per node: forward only."),
        _gloss("doubly linked", "`prev` as well as `next`. Removal given a node becomes O(1)."),
        _gloss("relink", "Changing a `next` so the list skips or includes a node."),
        _gloss("in-place reversal", "Three pointers — prev, cur, next — and one pass."),
        _gloss("cycle", "A list whose links loop. Detected with a fast and a slow pointer."),
        _gloss("binary tree", "Up to two children per node: `left` and `right`."),
        _gloss("BST", "A binary tree ordered so that everything left of a node is smaller."),
        _gloss("leaf", "A node with no children. The base case of nearly every tree recursion."),
        _gloss("depth / height", "How far the deepest leaf is from the root."),
        _gloss("pre-order", "Node, then children. The order you would print a tree in."),
        _gloss("in-order", "Left, node, right. On a BST, this is sorted order."),
        _gloss("post-order", "Children, then node. What you need when a node's value depends on its children."),
        _gloss("depth-first (DFS)", "Follow one branch to the bottom first. A STACK."),
        _gloss("breadth-first (BFS)", "Visit a whole level before descending. A QUEUE."),
        _gloss("n-ary tree", "Any number of children: `kids: readonly Cat[]`."),
        _gloss("roll-up", "Aggregating from the leaves towards the root. A post-order sum."),
        _gloss("iterable", "Anything with a `[Symbol.iterator]` method. Works with for…of and spread."),
        _gloss("iterator", "The object with `next()` that an iterable hands out."),
        _gloss("generator", "`function*` — a function that produces values one at a time with `yield`."),
        _gloss("yield*", "Delegate to another iterable, which is how a recursive generator walks a tree."),
        _gloss("lazy", "A generator computes each value only when asked, so the sequence need not exist."),
    ],
    cheatsheet="""
```ts
// ---- the type that refers to itself -------------------------------------
interface N {
  readonly value: number;
  next: N | null;                  // the `| null` is what makes it finite
}

// ---- walking it — the annotation is LOAD-BEARING ------------------------
let cur: N | null = head;          // NOT `let cur = head`
while (cur !== null) {
  console.log(cur.value);
  cur = cur.next;                  // …or this assignment will not type-check
}

// ---- build, back to front ----------------------------------------------
let head: N | null = null;
for (let i = xs.length - 1; i >= 0; i = i - 1) {
  head = { value: xs[i] ?? 0, next: head };
}

// ---- relinking ---------------------------------------------------------
node.next = node.next?.next ?? null;        // delete the one after `node`
node.next = { value: 9, next: node.next };   // insert after `node`

// ---- reverse, in one pass ----------------------------------------------
let prev: N | null = null;
let cur: N | null = head;
while (cur !== null) {
  const next: N | null = cur.next;   // remember it before you overwrite it
  cur.next = prev;
  prev = cur;
  cur = next;
}
return prev;                          // the old tail

// ---- fast and slow: the middle, and cycle detection -------------------
let slow: N | null = head;
let fast: N | null = head;
while (fast !== null && fast.next !== null) {
  slow = slow?.next ?? null;
  fast = fast.next.next;
  if (slow === fast) { /* a cycle */ }
}

// ---- trees -------------------------------------------------------------
interface T { readonly value: number; left: T | null; right: T | null; }
interface Cat { readonly name: string; readonly cents: number;
                readonly kids: readonly Cat[]; }

function depth(t: T | null): number {                      // the base case is null
  if (t === null) { return 0; }
  return 1 + Math.max(depth(t.left), depth(t.right));
}
function total(c: Cat): number {                            // …or "no children"
  let sum = c.cents;
  for (const kid of c.kids) { sum = sum + total(kid); }
  return sum;
}

// pre-order: node, left, right      in-order: left, node, right  (BST ⇒ sorted)
// post-order: left, right, node     ← when a node depends on its children

// ---- DFS and BFS differ by ONE line ------------------------------------
const next = stack.pop();        // depth-first  (week 18's stack)
const next = queue[head++];      // breadth-first (week 18's queue)

// ---- iterable, and generators -----------------------------------------
class Bag<T> {
  private readonly items: T[] = [];
  *[Symbol.iterator](): Generator<T> {          // a generator METHOD
    for (const item of this.items) { yield item; }
  }
}
[...bag];                                        // works, because it is iterable

function* walk(c: Cat): Generator<Cat> {
  yield c;
  for (const kid of c.kids) { yield* walk(kid); }   // delegate — recursion, lazily
}
for (const c of walk(root)) { … }
```
""",
    self_check=[
        "Can you write a self-referential node type, and say what makes it terminate?",
        "Can you say why `let cur = head` does not work and `let cur: N | null = head` does?",
        "Can you build a list from an array without reversing anything?",
        "Can you delete the node after a given node?",
        "Can you reverse a list in one pass, and say why you have to save `next` first?",
        "Can you say what a `prev` pointer buys?",
        "Can you find the middle of a list in one pass?",
        "Can you compute a tree's depth, and name the base case?",
        "Can you give the three depth-first orders, and say which one a BST prints sorted?",
        "Can you say which order to use when a node's value depends on its children?",
        "Can you say what single change turns DFS into BFS?",
        "Can you make a class usable in a `for … of` loop?",
        "Can you write a recursive generator over a tree?",
    ],
    review=[
        _q("`interface N { next: N }` — what is wrong with it?",
           ["nothing", "no value can ever be built: there is no way to end", "it is circular",
            "it needs a class"], 1,
           "The `| null` is what makes it finite."),
        _q("`let cur = head` where `head: N | null` then `cur = cur.next` gives…",
           ["nothing", "a type error on the assignment", "undefined", "a crash"], 1,
           "The annotation is load-bearing."),
        _q("Building a list from an array back to front means…",
           ["it comes out reversed", "each new node points at the one already built",
            "you need two passes", "it is slower"], 1,
           "One pass, right order."),
        _q("`node.next = node.next?.next ?? null` does what?",
           ["inserts", "deletes the node after `node`", "reverses", "nothing"], 1,
           "Relinking past it."),
        _q("In an in-place reversal you must save `cur.next` because…",
           ["it is faster", "the next line overwrites it", "of types", "you need not"], 1,
           "Three pointers, in that order."),
        _q("A `prev` pointer makes which operation O(1)?",
           ["search", "removing a node you already hold", "insertion at the head", "reversal"], 1,
           "The cost is a second link per node to maintain."),
        _q("Finding the middle in one pass uses…",
           ["a counter", "a fast pointer and a slow one", "recursion", "a Map"], 1,
           "Fast moves two, slow moves one."),
        _q("A tree recursion's base case is usually…",
           ["the root", "the null child, or the node with no children", "the depth",
            "an array"], 1,
           "Which you can see, rather than having to remember."),
        _q("In-order traversal of a BST gives…",
           ["insertion order", "sorted order", "reverse order", "level order"], 1,
           "Which is the point of a BST."),
        _q("When a node's value depends on its children, use…",
           ["pre-order", "post-order", "in-order", "level order"], 1,
           "Children first, then the node."),
        _q("DFS becomes BFS when you change…",
           ["the recursion", "the stack to a queue", "the order of children", "the type"], 1,
           "One line."),
        _q("An object works in `for … of` when it has…",
           ["a length", "a [Symbol.iterator] method", "an index signature", "a next()"], 1,
           "That is the whole protocol."),
        _q("`yield*` does what?",
           ["yields an array", "delegates to another iterable", "returns", "throws"], 1,
           "Which is how a recursive generator walks a tree."),
        _q("A generator is lazy, meaning…",
           ["it is slow", "each value is computed only when asked for",
            "it caches", "it is async"], 1,
           "So the sequence need never exist all at once."),
    ],
    milestone="Budget Buddy ends where it started — a receipt line — and finishes as a **category tree**. Categories nest to any depth, each with its own spend; the report rolls every child's total up into its parent, indents the tree, flags the categories over budget, and hands the whole thing out through a generator so the printing code never sees a recursive call. Twenty weeks, one program.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w20-node", "A type that refers to itself",
            "And the `| null` that makes it possible.",
            """
```ts
interface N {
  readonly value: number;
  next: N | null;
}
```

`N` mentions `N`. That is legal, and it is the whole idea of this week.

## Why `| null` is not optional

```ts
interface Broken {
  readonly value: number;
  next: Broken;            // compiles — and no value of this type can be built
}
```

To construct one you would need a `next`, which needs a `next`, for ever. The type
is legal and **uninhabitable**. The `| null` gives the recursion a floor, exactly
as a base case does for a function — and it is worth noticing now, because lesson 5
needs the same instinct.

`| undefined` would work identically; `null` is the convention for "deliberately
nothing" (week 15), and a terminator is about as deliberate as it gets.

## Building one

```ts
const list: N = { value: 1, next: { value: 2, next: null } };
```

Nested literals are fine for two nodes and unreadable for five, so build from an
array — **backwards**, so each new node points at what you have already built:

```ts
let head: N | null = null;
for (let i = xs.length - 1; i >= 0; i = i - 1) {
  head = { value: xs[i] ?? 0, next: head };
}
```

## The annotation you cannot leave out

This is the one thing that catches everybody:

```ts
let cur = head;              // inferred as N | null if head is — but…
```

…if `head` is definitely an `N`, `cur` is inferred as `N`, and then:

```ts
cur = cur.next;              // ❌ TS2322: Type 'N | null' is not assignable to type 'N'
```

So **annotate the walking variable**:

```ts
let cur: N | null = head;
while (cur !== null) {
  console.log(cur.value);     // narrowed to N inside the loop
  cur = cur.next;             // ✅
}
```

Inside the `while`, control-flow analysis narrows `cur` to `N`, so `cur.value`
needs no guard of its own. That is `strictNullChecks` being genuinely helpful: the
one place a list walk can go wrong is the end, and the compiler makes you handle
exactly that.

## `readonly value`, mutable `next`

A deliberate split. The value a node carries does not change; which node comes next
is the entire point of a linked structure, and lesson 3 rewires it constantly.

> ⚠️ **Common mistakes:** a recursive type with no terminator; forgetting the `|
> null` on the walking variable; and losing the head pointer, which loses the list.
""",
            warmup=[
                _q("`interface N { next: N }` is…",
                   ["an error", "legal, and impossible to construct", "a class", "recursive and fine"], 1,
                   "There is no way to stop."),
                _q("`let cur = head; cur = cur.next;` where head is `N` gives…",
                   ["nothing", "a type error", "null", "a crash"], 1,
                   "`N | null` will not assign to `N`."),
                _q("Inside `while (cur !== null)`, `cur` is…",
                   ["N | null", "N", "null", "unknown"], 1,
                   "Narrowed, so no guard is needed per member access."),
                _q("Building a list from an array is done…",
                   ["front to back", "back to front", "with recursion", "with a Map"], 1,
                   "So each node points at one that exists already."),
            ],
            exercises=[
                _ex("tscourse-w20-nd-1", "The type that terminates",
                    "Give `next` the type that lets a list end.",
                    _NODE +
                    'const list: N = { value: 1, next: { value: 2, next: null } };\n'
                    'console.log(`${list.value} ${list.next?.value ?? 0}`);\n',
                    '  next: N | null;', [("", "1 2")],
                    hints=["A node, or nothing at all.",
                           "Write next: N | null;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-nd-2", "Annotate the walker",
                    "Declare the cursor so it can hold the end of the list as well as a node.",
                    _NODE + _BUILD +
                    'const head = build([1, 2, 3]);\n'
                    'let cur: N | null = head;\n'
                    'let sum = 0;\n'
                    'while (cur !== null) {\n'
                    '  sum = sum + cur.value;\n'
                    '  cur = cur.next;\n}\n'
                    'console.log(sum);\n',
                    'let cur: N | null = head;', [("", "6")],
                    hints=["Without the annotation the assignment at the bottom of the loop will not compile.",
                           "Write let cur: N | null = head;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-nd-3", "Build it back to front",
                    "Point each new node at the list built so far.",
                    _NUMS + _NODE + _SHOW +
                    'function build(xs: readonly number[]): N | null {\n'
                    '  let head: N | null = null;\n'
                    '  for (let i = xs.length - 1; i >= 0; i = i - 1) {\n'
                    '    head = { value: xs[i] ?? 0, next: head };\n  }\n'
                    '  return head;\n}\n'
                    'console.log(show(build(nums)));\n',
                    '    head = { value: xs[i] ?? 0, next: head };',
                    [("1 2 3", "1->2->3"), ("7", "7")],
                    hints=["The new node's `next` is whatever `head` currently points at.",
                           "Write head = { value: xs[i] ?? 0, next: head };"],
                    difficulty="Medium"),
                _ex("tscourse-w20-nd-4", "Count the nodes",
                    "Walk to the end, counting as you go.",
                    _NUMS + _NODE + _BUILD +
                    'function length(head: N | null): number {\n'
                    '  let n = 0;\n'
                    '  let cur: N | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    n = n + 1;\n'
                    '    cur = cur.next;\n  }\n'
                    '  return n;\n}\n'
                    'console.log(length(build(nums)));\n',
                    '    n = n + 1;', [("1 2 3 4", "4"), ("5", "1")],
                    hints=["One per node visited.",
                           "Write n = n + 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-nd-5", "Find a value",
                    "Return whether the list contains the target, stopping as soon as it is found.",
                    _NUMS + _NODE + _BUILD +
                    'function has(head: N | null, target: number): boolean {\n'
                    '  let cur: N | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    if (cur.value === target) {\n'
                    '      return true;\n    }\n'
                    '    cur = cur.next;\n  }\n'
                    '  return false;\n}\n'
                    'console.log(`${has(build(nums), 3)} ${has(build(nums), 99)}`);\n',
                    '      return true;', [("1 2 3", "true false"), ("9", "false false")],
                    hints=["Return the moment the value matches.",
                           "Write return true;"],
                    difficulty="Easy"),
                _predict("tscourse-w20-nd-p1", "What the end of a list looks like",
                         _NODE +
                         'const tail: N = { value: 3, next: null };\n'
                         'const got = tail.next;\n',
                         "got", "N | null",
                         why="The declared type of the member, not the type of what happens to be in it.",
                         hints=["A node, or the terminator.",
                                "Write N | null."]),
                _diagnose("tscourse-w20-nd-d1", "The walker that was too narrow",
                          "TS2322: Type 'N | null' is not assignable to type 'N'.",
                          _NODE +
                          'const head: N = { value: 1, next: { value: 2, next: null } };\n'
                          'let cur = head;\n'
                          'let sum = 0;\n'
                          'while (cur !== null) {\n'
                          '  sum = sum + cur.value;\n'
                          '  cur = cur.next;\n}\n'
                          'console.log(sum);\n',
                          _NODE +
                          'const head: N = { value: 1, next: { value: 2, next: null } };\n'
                          'let cur: N | null = head;\n'
                          'let sum = 0;\n'
                          'while (cur !== null) {\n'
                          '  sum = sum + cur.value;\n'
                          '  cur = cur.next;\n}\n'
                          'console.log(sum);\n',
                          [("", "3")],
                          hints=["`head` is definitely a node, so `cur` was inferred as one — and the list's end is not.",
                                 "The variable has to be able to hold the terminator.",
                                 "Annotate it `N | null`."],
                          difficulty="Medium"),
                # The compiler catches this one, and its message is the interesting
                # part: having proved `head` is `null` after the first loop, it types
                # the second walk's cursor as `never`. A narrowing error pointing at
                # a logic bug is worth more than the wrong answer would have been.
                _fix("tscourse-w20-nd-fix1", "Fix the walk that lost the head",
                     "The second loop will not compile: `TS2339: Property 'next' does not exist on type 'never'`. "
                     "That is the compiler telling you something true — the first loop advanced `head` itself to the "
                     "end of the list, so by the time the second one starts, `head` is provably `null` and its cursor "
                     "has no possible type. Walk a cursor, and leave the head where it is.",
                     _NUMS + _NODE + _BUILD +
                     'let head = build(nums);\n'
                     'let sum = 0;\n'
                     'while (head !== null) {\n'
                     '  sum = sum + head.value;\n'
                     '  head = head.next;\n}\n'
                     'let n = 0;\n'
                     'let cur: N | null = head;\n'
                     'while (cur !== null) {\n'
                     '  n = n + 1;\n'
                     '  cur = cur.next;\n}\n'
                     'console.log(`${sum} ${n}`);\n',
                     _NUMS + _NODE + _BUILD +
                     'const head = build(nums);\n'
                     'let sum = 0;\n'
                     'let walker: N | null = head;\n'
                     'while (walker !== null) {\n'
                     '  sum = sum + walker.value;\n'
                     '  walker = walker.next;\n}\n'
                     'let n = 0;\n'
                     'let cur: N | null = head;\n'
                     'while (cur !== null) {\n'
                     '  n = n + 1;\n'
                     '  cur = cur.next;\n}\n'
                     'console.log(`${sum} ${n}`);\n',
                     [("1 2 3", "6 3"), ("4", "4 1")],
                     hints=["After the first loop, `head` is `null` — the list is still in memory and nothing points at it.",
                            "The head is the handle on the whole list; never advance it.",
                            "Walk a separate cursor, and make `head` a `const` so this cannot happen again."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`| undefined` instead of `| null` as the terminator would…",
                   ["not work", "work identically — `null` is just the convention for a deliberate nothing",
                    "be faster", "be an error"], 1,
                   "Week 15's convention."),
                _q("Making the head a `const` prevents…",
                   ["mutation of values", "accidentally advancing it and losing the list", "nothing",
                    "relinking"], 1,
                   "The commonest beginner bug in this topic."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w20-list", "Lists, and what they are actually good at",
            "O(1) at the front, O(n) everywhere else.",
            """
| operation | array | singly linked list |
|---|---|---|
| read the i-th | **O(1)** | O(n) — you have to walk |
| add at the front | O(n) (`unshift`) | **O(1)** |
| add at the end | **O(1)** (`push`) | O(n), or O(1) with a tail pointer |
| remove a node you hold | O(n) (`splice`) | **O(1)** given `prev` (lesson 4) |
| memory | one block | a node per value, plus a link |

The honest summary: **an array wins almost everywhere**, and it wins harder than
this table suggests, because arrays are contiguous and caches exist. A linked list
is the right answer when you are inserting and removing at known positions and
never indexing — which in practice means a queue, an LRU cache, or an editor's
undo chain.

Know them because the *idea* generalises to trees and graphs, and because
interviewers ask.

## A tail pointer

Appending means walking to the end — unless you remember where the end is:

```ts
interface List {
  head: N | null;
  tail: N | null;                // ← and now append is O(1)
}
```

The cost is that every operation which can change the last node has to maintain
it, and forgetting one leaves a `tail` pointing at a node that is no longer last.
That is the whole trade of every cached pointer: speed, in exchange for an
invariant you now have to keep.

## Fast and slow pointers

Two cursors moving at different speeds answer several questions in one pass:

```ts
let slow: N | null = head;
let fast: N | null = head;
while (fast !== null && fast.next !== null) {
  slow = slow?.next ?? null;
  fast = fast.next.next;
}
// slow is now at the middle
```

The loop condition is the whole subtlety: `fast !== null` covers an odd length,
`fast.next !== null` an even one. Get it wrong and you either crash or stop one
node early.

The same trick detects a **cycle**: if the list loops, the fast pointer eventually
laps the slow one and they meet. If it does not loop, the fast one hits the end.
That is Floyd's algorithm, and it is O(1) extra memory — where the obvious solution
is a `Set` of visited nodes, which is O(n) and, given week 19, also perfectly
respectable.

> ⚠️ **Common mistakes:** indexing a list (that is what an array is for); a tail
> pointer that goes stale; and a fast-and-slow loop whose condition is wrong for
> even lengths.
""",
            warmup=[
                _q("Reading the i-th element of a linked list is…",
                   ["O(1)", "O(n)", "O(log n)", "free"], 1,
                   "You have to walk there."),
                _q("Adding at the front of a list is…",
                   ["O(n)", "O(1)", "O(log n)", "impossible"], 1,
                   "Which is the one thing it beats an array at."),
                _q("A tail pointer makes append O(1) and costs…",
                   ["memory only", "an invariant every mutation must maintain", "nothing",
                    "correctness"], 1,
                   "The trade of every cached pointer."),
                _q("Fast and slow pointers find the middle in…",
                   ["two passes", "one pass", "O(n log n)", "O(1)"], 1,
                   "Fast moves two nodes per step."),
            ],
            exercises=[
                _ex("tscourse-w20-ls-1", "Append, the slow way",
                    "Walk to the last node, then attach the new one.",
                    _NUMS + _NODE + _BUILD + _SHOW +
                    'function append(head: N | null, value: number): N | null {\n'
                    '  const node: N = { value, next: null };\n'
                    '  if (head === null) {\n'
                    '    return node;\n  }\n'
                    '  let cur: N = head;\n'
                    '  while (cur.next !== null) {\n'
                    '    cur = cur.next;\n  }\n'
                    '  cur.next = node;\n'
                    '  return head;\n}\n'
                    'console.log(show(append(build(nums), 9)));\n',
                    '  while (cur.next !== null) {',
                    [("1 2", "1->2->9"), ("", "0->9")],
                    hints=["Stop when there is no next node, not when the cursor is null.",
                           "Write while (cur.next !== null) {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-ls-2", "Prepend, the fast way",
                    "Put the new node in front of the current head.",
                    _NUMS + _NODE + _BUILD + _SHOW +
                    'function prepend(head: N | null, value: number): N {\n'
                    '  return { value, next: head };\n}\n'
                    'console.log(show(prepend(build(nums), 0)));\n',
                    '  return { value, next: head };', [("1 2", "0->1->2"), ("5", "0->5")],
                    hints=["One node, pointing at what used to be first.",
                           "Write return { value, next: head };"],
                    difficulty="Easy"),
                _ex("tscourse-w20-ls-3", "Keep a tail pointer",
                    "Maintain the tail as you append, so each append is O(1).",
                    _NUMS + _NODE + _SHOW +
                    'let head: N | null = null;\n'
                    'let tail: N | null = null;\n'
                    'for (const n of nums) {\n'
                    '  const node: N = { value: n, next: null };\n'
                    '  if (tail === null) {\n'
                    '    head = node;\n'
                    '  } else {\n'
                    '    tail.next = node;\n  }\n'
                    '  tail = node;\n}\n'
                    'console.log(show(head));\n',
                    '  tail = node;', [("1 2 3", "1->2->3"), ("7", "7")],
                    hints=["Whatever happened above, the node you just added is now last.",
                           "Write tail = node;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-ls-4", "The middle, in one pass",
                    "Advance the fast pointer two nodes per step.",
                    _NUMS + _NODE + _BUILD +
                    'function middle(head: N | null): number {\n'
                    '  let slow: N | null = head;\n'
                    '  let fast: N | null = head;\n'
                    '  while (fast !== null && fast.next !== null) {\n'
                    '    slow = slow?.next ?? null;\n'
                    '    fast = fast.next.next;\n  }\n'
                    '  return slow?.value ?? 0;\n}\n'
                    'console.log(middle(build(nums)));\n',
                    '    fast = fast.next.next;',
                    [("1 2 3", "2"), ("1 2 3 4", "3"), ("5", "5")],
                    hints=["The loop condition has already proved both `fast` and `fast.next` are there.",
                           "Write fast = fast.next.next;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-ls-5", "The k-th from the end",
                    "Start the fast pointer k nodes ahead, then move both together.",
                    _NODE + _BUILD +
                    'function fromEnd(head: N | null, k: number): number {\n'
                    '  let fast: N | null = head;\n'
                    '  for (let i = 0; i < k; i = i + 1) {\n'
                    '    fast = fast?.next ?? null;\n  }\n'
                    '  let slow: N | null = head;\n'
                    '  while (fast !== null) {\n'
                    '    fast = fast.next;\n'
                    '    slow = slow?.next ?? null;\n  }\n'
                    '  return slow?.value ?? 0;\n}\n'
                    'console.log(fromEnd(build([1, 2, 3, 4, 5]), 2));\n',
                    '  while (fast !== null) {', [("", "4")],
                    hints=["Once fast is k ahead, walk both until fast falls off the end.",
                           "Write while (fast !== null) {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-ls-6", "Detect a cycle with a Set",
                    "Remember the nodes you have visited — by identity, which is week 19's Map and Set rule.",
                    _NODE +
                    'function hasCycle(head: N | null): boolean {\n'
                    '  const seen = new Set<N>();\n'
                    '  let cur: N | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    if (seen.has(cur)) {\n'
                    '      return true;\n    }\n'
                    '    seen.add(cur);\n'
                    '    cur = cur.next;\n  }\n'
                    '  return false;\n}\n'
                    'const a: N = { value: 1, next: null };\n'
                    'const b: N = { value: 2, next: null };\n'
                    'a.next = b;\n'
                    'console.log(hasCycle(a));\n'
                    'b.next = a;\n'
                    'console.log(hasCycle(a));\n',
                    '  const seen = new Set<N>();', [("", "false\ntrue")],
                    hints=["A Set of nodes — keyed by identity, which is exactly what you want here.",
                           "Write const seen = new Set<N>();"],
                    difficulty="Medium"),
                _fix("tscourse-w20-ls-fix1", "Fix the middle of an even-length list",
                     "On `1 2 3 4` this prints `2` and should print `3`: the loop stops one step early because it only checks `fast`, so an even-length list never takes its last step.",
                     _NUMS + _NODE + _BUILD +
                     'function middle(head: N | null): number {\n'
                     '  let slow: N | null = head;\n'
                     '  let fast: N | null = head;\n'
                     '  while (fast !== null && fast.next !== null && fast.next.next !== null) {\n'
                     '    slow = slow?.next ?? null;\n'
                     '    fast = fast.next.next;\n  }\n'
                     '  return slow?.value ?? 0;\n}\n'
                     'console.log(middle(build(nums)));\n',
                     _NUMS + _NODE + _BUILD +
                     'function middle(head: N | null): number {\n'
                     '  let slow: N | null = head;\n'
                     '  let fast: N | null = head;\n'
                     '  while (fast !== null && fast.next !== null) {\n'
                     '    slow = slow?.next ?? null;\n'
                     '    fast = fast.next.next;\n  }\n'
                     '  return slow?.value ?? 0;\n}\n'
                     'console.log(middle(build(nums)));\n',
                     [("1 2 3 4", "3"), ("1 2 3", "2"), ("1 2", "2")],
                     hints=["The extra condition makes the loop stop before its last legal step.",
                            "Two conditions are enough: `fast` is there, and so is `fast.next`.",
                            "Drop the third clause."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("An array beats a list at nearly everything partly because…",
                   ["it is newer", "it is contiguous, and caches exist", "it is typed",
                    "of push"], 1,
                   "Which the O() table does not show."),
                _q("Floyd's cycle detection uses…",
                   ["a Set", "O(1) extra memory — two pointers", "recursion", "a Map"], 1,
                   "The Set version is O(n) and perfectly respectable."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w20-listops", "Relinking",
            "Insert, delete, reverse — three pointers and a lot of care.",
            """
Every list mutation is the same move: **change one `next` so the chain runs through
a different node.**

## Insert after a node

```ts
node.next = { value: 9, next: node.next };
```

Read it right to left: the new node points at whatever came after `node`, and then
`node` points at the new node. Getting those two in the wrong order loses the rest
of the list.

## Delete the node after a node

```ts
node.next = node.next?.next ?? null;
```

Nothing points at the removed node any more, so it is gone. The `?.` handles
`node` already being last, and the `?? null` turns the `undefined` that `?.`
produces into the `null` the type wants — a detail week 15 would recognise.

## Delete by value

Deleting requires the node **before** the one you are removing, which is the whole
weakness of a singly linked list:

```ts
function remove(head: N | null, value: number): N | null {
  if (head === null) { return null; }
  if (head.value === value) { return head.next; }     // the head is special
  let cur: N = head;
  while (cur.next !== null) {
    if (cur.next.value === value) {
      cur.next = cur.next.next;
      return head;
    }
    cur = cur.next;
  }
  return head;
}
```

The head case is separate because there is nothing before it. Every textbook
mentions a *sentinel* (a dummy node in front) to get rid of that special case, and
it is a genuinely good trick when a function has several such branches.

## Reverse, in one pass

The interview question, and three pointers:

```ts
let prev: N | null = null;
let cur: N | null = head;
while (cur !== null) {
  const next: N | null = cur.next;    // 1. remember what comes next
  cur.next = prev;                     // 2. turn this link around
  prev = cur;                          // 3. shuffle both forward
  cur = next;
}
return prev;                            // the old tail is the new head
```

**Line 1 is why it works.** Step 2 overwrites `cur.next`, so without saving it
first there is no way to continue — you would be holding a one-node list and have
lost everything after it. Write those four lines in that order, every time.

Note the annotation on `next` as well: `cur.next` is `N | null`, and inference from
the first iteration is not what you want.

> ⚠️ **Common mistakes:** the two assignments of an insert in the wrong order;
> forgetting the head is a special case when deleting; and reversing without saving
> `next`, which silently truncates the list to one node.
""",
            warmup=[
                _q("`node.next = { value: 9, next: node.next }` inserts…",
                   ["before node", "after node", "at the head", "at the tail"], 1,
                   "The new node adopts node's old successor."),
                _q("Deleting a node needs…",
                   ["the node itself", "the node BEFORE it", "the head", "its value"], 1,
                   "Which is the weakness a `prev` pointer fixes."),
                _q("In a reversal, saving `cur.next` first is…",
                   ["optional", "required — the next line overwrites it", "slower", "a style choice"], 1,
                   "Otherwise the rest of the list is lost."),
                _q("After reversing, the new head is…",
                   ["head", "prev — the old tail", "cur", "null"], 1,
                   "`cur` is null by then."),
            ],
            exercises=[
                _ex("tscourse-w20-op-1", "Insert after the head",
                    "Splice a new node in behind the first one.",
                    _NODE + _BUILD + _SHOW +
                    'const head = build([1, 3]);\n'
                    'if (head !== null) {\n'
                    '  head.next = { value: 2, next: head.next };\n}\n'
                    'console.log(show(head));\n',
                    '  head.next = { value: 2, next: head.next };', [("", "1->2->3")],
                    hints=["The new node takes over the head's old successor.",
                           "Write head.next = { value: 2, next: head.next };"],
                    difficulty="Medium"),
                _ex("tscourse-w20-op-2", "Delete the second node",
                    "Relink the head past the node after it.",
                    _NUMS + _NODE + _BUILD + _SHOW +
                    'const head = build(nums);\n'
                    'if (head !== null) {\n'
                    '  head.next = head.next?.next ?? null;\n}\n'
                    'console.log(show(head));\n',
                    '  head.next = head.next?.next ?? null;',
                    [("1 2 3", "1->3"), ("1", "1")],
                    hints=["Skip one, and cope with the head already being last.",
                           "Write head.next = head.next?.next ?? null;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-op-3", "Delete by value",
                    "Handle the head as its own case, since nothing precedes it.",
                    _NODE + _BUILD + _SHOW +
                    'function remove(head: N | null, value: number): N | null {\n'
                    '  if (head === null) {\n'
                    '    return null;\n  }\n'
                    '  if (head.value === value) {\n'
                    '    return head.next;\n  }\n'
                    '  let cur: N = head;\n'
                    '  while (cur.next !== null) {\n'
                    '    if (cur.next.value === value) {\n'
                    '      cur.next = cur.next.next;\n'
                    '      return head;\n    }\n'
                    '    cur = cur.next;\n  }\n'
                    '  return head;\n}\n'
                    'console.log(show(remove(build([1, 2, 3]), 1)));\n'
                    'console.log(show(remove(build([1, 2, 3]), 2)));\n'
                    'console.log(show(remove(build([1, 2, 3]), 9)));\n',
                    '  if (head.value === value) {\n    return head.next;\n  }',
                    [("", "2->3\n1->3\n1->2->3")],
                    hints=["Removing the first node just means returning the second.",
                           "Write if (head.value === value) { return head.next; }"],
                    difficulty="Medium"),
                _ex("tscourse-w20-op-4", "Reverse it",
                    "Save the next node before you overwrite the link.",
                    _NUMS + _NODE + _BUILD + _SHOW +
                    'function reverse(head: N | null): N | null {\n'
                    '  let prev: N | null = null;\n'
                    '  let cur: N | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    const next: N | null = cur.next;\n'
                    '    cur.next = prev;\n'
                    '    prev = cur;\n'
                    '    cur = next;\n  }\n'
                    '  return prev;\n}\n'
                    'console.log(show(reverse(build(nums))));\n',
                    '    const next: N | null = cur.next;',
                    [("1 2 3", "3->2->1"), ("1", "1")],
                    hints=["The very next line destroys `cur.next`, so read it now.",
                           "Write const next: N | null = cur.next;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-op-5", "Insert in order",
                    "Walk until the next value is larger, then splice in.",
                    _NODE + _BUILD + _SHOW +
                    'function insertSorted(head: N | null, value: number): N {\n'
                    '  if (head === null || value <= head.value) {\n'
                    '    return { value, next: head };\n  }\n'
                    '  let cur: N = head;\n'
                    '  while (cur.next !== null && cur.next.value < value) {\n'
                    '    cur = cur.next;\n  }\n'
                    '  cur.next = { value, next: cur.next };\n'
                    '  return head;\n}\n'
                    'let head: N | null = null;\n'
                    'for (const n of [3, 1, 4, 2]) {\n'
                    '  head = insertSorted(head, n);\n}\n'
                    'console.log(show(head));\n',
                    '  while (cur.next !== null && cur.next.value < value) {',
                    [("", "1->2->3->4")],
                    hints=["Stop when the following value is no longer smaller than the one being inserted.",
                           "Write while (cur.next !== null && cur.next.value < value) {"],
                    difficulty="Hard"),
                _ex("tscourse-w20-op-6", "A sentinel head",
                    "Put a dummy node in front, so deleting the first real node needs no special case.",
                    _NUMS + _NODE + _BUILD + _SHOW +
                    'function removeAll(head: N | null, value: number): N | null {\n'
                    '  const sentinel: N = { value: 0, next: head };\n'
                    '  let cur: N = sentinel;\n'
                    '  while (cur.next !== null) {\n'
                    '    if (cur.next.value === value) {\n'
                    '      cur.next = cur.next.next;\n'
                    '    } else {\n'
                    '      cur = cur.next;\n    }\n  }\n'
                    '  return sentinel.next;\n}\n'
                    'console.log(show(removeAll(build(nums), 2)));\n',
                    '  const sentinel: N = { value: 0, next: head };',
                    [("2 1 2 3 2", "1->3"), ("1 2", "1"), ("2", "")],
                    hints=["A node that is not part of the list, pointing at the real head.",
                           "Write const sentinel: N = { value: 0, next: head };"],
                    difficulty="Hard"),
                _fix("tscourse-w20-op-fix1", "Fix the reversal that lost the list",
                     "This prints `1` for every input: the link is turned around *before* the next node is remembered, so after the first step there is nothing left to walk.",
                     _NUMS + _NODE + _BUILD + _SHOW +
                     'function reverse(head: N | null): N | null {\n'
                     '  let prev: N | null = null;\n'
                     '  let cur: N | null = head;\n'
                     '  while (cur !== null) {\n'
                     '    cur.next = prev;\n'
                     '    const next: N | null = cur.next;\n'
                     '    prev = cur;\n'
                     '    cur = next;\n  }\n'
                     '  return prev;\n}\n'
                     'console.log(show(reverse(build(nums))));\n',
                     _NUMS + _NODE + _BUILD + _SHOW +
                     'function reverse(head: N | null): N | null {\n'
                     '  let prev: N | null = null;\n'
                     '  let cur: N | null = head;\n'
                     '  while (cur !== null) {\n'
                     '    const next: N | null = cur.next;\n'
                     '    cur.next = prev;\n'
                     '    prev = cur;\n'
                     '    cur = next;\n  }\n'
                     '  return prev;\n}\n'
                     'console.log(show(reverse(build(nums))));\n',
                     [("1 2 3", "3->2->1"), ("1 2", "2->1")],
                     hints=["By the time `next` is read, it has already been overwritten with `prev`.",
                            "The order of the four lines is the entire algorithm.",
                            "Read `cur.next` first, then turn the link around."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A sentinel node removes…",
                   ["the need for null", "the head's special case", "the tail", "recursion"], 1,
                   "Worth it when a function has several such branches."),
                _q("`?? null` after a `?.` chain is there because…",
                   ["of style", "`?.` produces undefined, and the field's type is `N | null`",
                    "it is faster", "of strict mode"], 1,
                   "Week 15's distinction, still load-bearing."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w20-doubly", "Two links per node",
            "What `prev` buys, and what it costs.",
            """
```ts
interface D {
  readonly value: number;
  prev: D | null;
  next: D | null;
}
```

One extra field, and one operation changes complexity: **removing a node you
already hold** becomes O(1), because you no longer have to find what precedes it.

```ts
function unlink(node: D): void {
  if (node.prev !== null) { node.prev.next = node.next; }
  if (node.next !== null) { node.next.prev = node.prev; }
  node.prev = null;
  node.next = null;
}
```

Four lines, and every one is necessary: two to heal the chain around the node, two
to detach the node itself so it cannot be reached and cannot keep its neighbours
alive.

## The cost is an invariant

Every mutation now has to keep **two** links consistent. A doubly linked list has
an invariant you can state:

> For every node `n`, if `n.next` is not null then `n.next.prev === n`.

and every insert and remove must preserve it. Break it once — usually by updating
`next` and forgetting `prev` — and the list walks correctly forwards and is corrupt
backwards, which is a genuinely unpleasant bug because half your tests pass.

## What it is actually for

**An LRU cache.** A `Map` for O(1) lookup (week 19), plus a doubly linked list for
O(1) "move this to the front". That combination is the standard answer, and it is a
common interview question precisely because it needs both halves of these two
weeks.

**A real deque.** Week 18's array-based deque had O(n) front operations; this is
where both ends become O(1), which is what "use a deque" means in a performance
discussion.

**An editor's undo chain, a browser's history, a playlist** — anything where you
move both ways from where you are.

## The honest note

You will almost never write one. `Array` covers most cases, and when it does not,
the answer is usually a library. Know the shape, know the invariant, and know that
the `Map` + doubly-linked-list pairing is the LRU answer.

> ⚠️ **Common mistakes:** updating `next` and forgetting `prev`; not detaching the
> removed node; and a doubly linked list where an array would have done.
""",
            warmup=[
                _q("A `prev` pointer makes O(1)…",
                   ["search", "removing a node you already hold", "append", "reversal"], 1,
                   "You no longer need to find the predecessor."),
                _q("The invariant is…",
                   ["nodes are sorted", "if n.next is not null then n.next.prev === n",
                    "length is even", "prev is never null"], 1,
                   "And every mutation must preserve it."),
                _q("Half-updating the links gives you a list that is…",
                   ["broken everywhere", "correct forwards and corrupt backwards", "empty",
                    "slower"], 1,
                   "Which is why half your tests would pass."),
                _q("The standard LRU cache is…",
                   ["a Map", "a Map plus a doubly linked list", "an array", "a Set"], 1,
                   "O(1) lookup and O(1) promotion."),
            ],
            exercises=[
                _ex("tscourse-w20-db-1", "Link both ways",
                    "Set the new node's back-pointer as well as the old node's forward one.",
                    'interface D {\n'
                    '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                    'const a: D = { value: 1, prev: null, next: null };\n'
                    'const b: D = { value: 2, prev: null, next: null };\n'
                    'a.next = b;\n'
                    'b.prev = a;\n'
                    'console.log(`${a.next.value} ${b.prev.value}`);\n',
                    'b.prev = a;', [("", "2 1")],
                    hints=["The invariant says b's predecessor must be a.",
                           "Write b.prev = a;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-db-2", "Unlink in O(1)",
                    "Heal the chain around the node without walking the list.",
                    'interface D {\n'
                    '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                    'function link(nodes: readonly D[]): void {\n'
                    '  for (let i = 0; i + 1 < nodes.length; i = i + 1) {\n'
                    '    const cur = nodes[i];\n'
                    '    const nxt = nodes[i + 1];\n'
                    '    if (cur !== undefined && nxt !== undefined) {\n'
                    '      cur.next = nxt;\n      nxt.prev = cur;\n    }\n  }\n}\n'
                    'function unlink(node: D): void {\n'
                    '  if (node.prev !== null) {\n'
                    '    node.prev.next = node.next;\n  }\n'
                    '  if (node.next !== null) {\n'
                    '    node.next.prev = node.prev;\n  }\n'
                    '  node.prev = null;\n'
                    '  node.next = null;\n}\n'
                    'function show(head: D | null): string {\n'
                    '  const out: number[] = [];\n'
                    '  let cur: D | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    out.push(cur.value);\n'
                    '    cur = cur.next;\n  }\n'
                    '  return out.join("->");\n}\n'
                    'const a: D = { value: 1, prev: null, next: null };\n'
                    'const b: D = { value: 2, prev: null, next: null };\n'
                    'const c: D = { value: 3, prev: null, next: null };\n'
                    'link([a, b, c]);\n'
                    'unlink(b);\n'
                    'console.log(show(a));\n',
                    '    node.next.prev = node.prev;', [("", "1->3")],
                    hints=["The node after this one must now point back past it.",
                           "Write node.next.prev = node.prev;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-db-3", "Walk it backwards",
                    "Start at the tail and follow `prev`.",
                    'interface D {\n'
                    '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                    'const a: D = { value: 1, prev: null, next: null };\n'
                    'const b: D = { value: 2, prev: null, next: null };\n'
                    'const c: D = { value: 3, prev: null, next: null };\n'
                    'a.next = b;\nb.prev = a;\nb.next = c;\nc.prev = b;\n'
                    'const out: number[] = [];\n'
                    'let cur: D | null = c;\n'
                    'while (cur !== null) {\n'
                    '  out.push(cur.value);\n'
                    '  cur = cur.prev;\n}\n'
                    'console.log(out.join("->"));\n',
                    '  cur = cur.prev;', [("", "3->2->1")],
                    hints=["The other link.",
                           "Write cur = cur.prev;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-db-4", "Check the invariant",
                    "Walk forwards and confirm every node's successor points back at it.",
                    'interface D {\n'
                    '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                    'function consistent(head: D | null): boolean {\n'
                    '  let cur: D | null = head;\n'
                    '  while (cur !== null && cur.next !== null) {\n'
                    '    if (cur.next.prev !== cur) {\n'
                    '      return false;\n    }\n'
                    '    cur = cur.next;\n  }\n'
                    '  return true;\n}\n'
                    'const a: D = { value: 1, prev: null, next: null };\n'
                    'const b: D = { value: 2, prev: null, next: null };\n'
                    'a.next = b;\n'
                    'b.prev = a;\n'
                    'console.log(consistent(a));\n'
                    'b.prev = null;\n'
                    'console.log(consistent(a));\n',
                    '    if (cur.next.prev !== cur) {', [("", "true\nfalse")],
                    hints=["Compare the successor's back-pointer against the node itself, by identity.",
                           "Write if (cur.next.prev !== cur) {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-db-5", "Move to the front",
                    "Unlink the node and relink it at the head — the promotion an LRU cache performs.",
                    'interface D {\n'
                    '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                    'function unlink(node: D): void {\n'
                    '  if (node.prev !== null) {\n'
                    '    node.prev.next = node.next;\n  }\n'
                    '  if (node.next !== null) {\n'
                    '    node.next.prev = node.prev;\n  }\n'
                    '  node.prev = null;\n'
                    '  node.next = null;\n}\n'
                    'function toFront(head: D, node: D): D {\n'
                    '  if (head === node) {\n'
                    '    return head;\n  }\n'
                    '  unlink(node);\n'
                    '  node.next = head;\n'
                    '  head.prev = node;\n'
                    '  return node;\n}\n'
                    'function show(head: D | null): string {\n'
                    '  const out: number[] = [];\n'
                    '  let cur: D | null = head;\n'
                    '  while (cur !== null) {\n'
                    '    out.push(cur.value);\n'
                    '    cur = cur.next;\n  }\n'
                    '  return out.join("->");\n}\n'
                    'const a: D = { value: 1, prev: null, next: null };\n'
                    'const b: D = { value: 2, prev: null, next: null };\n'
                    'const c: D = { value: 3, prev: null, next: null };\n'
                    'a.next = b;\nb.prev = a;\nb.next = c;\nc.prev = b;\n'
                    'console.log(show(toFront(a, c)));\n',
                    '  node.next = head;\n  head.prev = node;', [("", "3->1->2")],
                    hints=["Detach it first, then splice it in before the old head — both links.",
                           "Write node.next = head; head.prev = node;"],
                    difficulty="Hard"),
                _fix("tscourse-w20-db-fix1", "Fix the half-updated removal",
                     "Walking forwards this looks right — `1->3` — but the backward walk still visits the removed node, printing `3->2->1`. The removal healed `next` and forgot `prev`.",
                     'interface D {\n'
                     '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                     'function unlink(node: D): void {\n'
                     '  if (node.prev !== null) {\n'
                     '    node.prev.next = node.next;\n  }\n}\n'
                     'const a: D = { value: 1, prev: null, next: null };\n'
                     'const b: D = { value: 2, prev: null, next: null };\n'
                     'const c: D = { value: 3, prev: null, next: null };\n'
                     'a.next = b;\nb.prev = a;\nb.next = c;\nc.prev = b;\n'
                     'unlink(b);\n'
                     'const back: number[] = [];\n'
                     'let cur: D | null = c;\n'
                     'while (cur !== null) {\n'
                     '  back.push(cur.value);\n'
                     '  cur = cur.prev;\n}\n'
                     'console.log(back.join("->"));\n',
                     'interface D {\n'
                     '  readonly value: number;\n  prev: D | null;\n  next: D | null;\n}\n'
                     'function unlink(node: D): void {\n'
                     '  if (node.prev !== null) {\n'
                     '    node.prev.next = node.next;\n  }\n'
                     '  if (node.next !== null) {\n'
                     '    node.next.prev = node.prev;\n  }\n'
                     '  node.prev = null;\n'
                     '  node.next = null;\n}\n'
                     'const a: D = { value: 1, prev: null, next: null };\n'
                     'const b: D = { value: 2, prev: null, next: null };\n'
                     'const c: D = { value: 3, prev: null, next: null };\n'
                     'a.next = b;\nb.prev = a;\nb.next = c;\nc.prev = b;\n'
                     'unlink(b);\n'
                     'const back: number[] = [];\n'
                     'let cur: D | null = c;\n'
                     'while (cur !== null) {\n'
                     '  back.push(cur.value);\n'
                     '  cur = cur.prev;\n}\n'
                     'console.log(back.join("->"));\n',
                     [("", "3->1")],
                     hints=["The invariant is broken: c.prev still points at the node that was removed.",
                            "Heal both directions, then detach the removed node entirely.",
                            "Four lines: prev.next, next.prev, and null out both of the node's own links."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Detaching the removed node's own links matters because…",
                   ["of types", "it cannot be reached through, and stops keeping its neighbours alive",
                    "of speed", "it does not"], 1,
                   "Two of the four lines exist for this."),
                _q("You will write a doubly linked list…",
                   ["often", "almost never — know the shape and the LRU pairing", "never",
                    "for every queue"], 1,
                   "An array covers most cases."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w20-tree", "Trees, and your first recursion",
            "Two children instead of one, and a function that calls itself.",
            """
Change `next: N | null` into two links and you have a **binary tree**:

```ts
interface T {
  readonly value: number;
  left: T | null;
  right: T | null;
}
```

Nothing else about the type is new — it is the same self-reference with the same
`| null` floor. What is new is that walking it cannot be a `while` loop any more:
at every node there are **two** ways to go, and a single cursor cannot be in both.

## The function that calls itself

```ts
function depth(t: T | null): number {
  if (t === null) {
    return 0;                                      // the base case
  }
  return 1 + Math.max(depth(t.left), depth(t.right));
}
```

Two parts, and every recursive function you will ever write has exactly these two:

* **A base case** that returns without recursing. Here it is `null` — the empty
  tree is zero deep. It is not a rule you have to remember; it is the `| null` in
  the type, showing up in the code.
* **A recursive case** that calls itself on something **smaller**. `t.left` is a
  strictly smaller tree than `t`, which is why this terminates.

That is the whole of recursion, and a tree is the kindest place to meet it because
both parts are *visible in the type*. Week 25 comes back for the call stack, the
depth limit, and how to turn any recursion into a loop.

## Counting and summing, the same shape

```ts
function count(t: T | null): number {
  if (t === null) { return 0; }
  return 1 + count(t.left) + count(t.right);
}
function sum(t: T | null): number {
  if (t === null) { return 0; }
  return t.value + sum(t.left) + sum(t.right);
}
```

Identical skeleton, different combining step. Once you see that, "write a function
over a tree" becomes "what do I return for empty, and how do I combine the two
children's answers?"

## A binary search tree

A BST adds one rule: **everything to the left is smaller, everything to the right
is larger.**

```ts
function insert(t: T | null, value: number): T {
  if (t === null) { return { value, left: null, right: null }; }
  if (value < t.value) { t.left = insert(t.left, value); }
  else if (value > t.value) { t.right = insert(t.right, value); }
  return t;
}
```

That rule buys O(log n) search — halve the problem at every step — *when the tree
is balanced*. Insert `1, 2, 3, 4, 5` in order and every node goes right: you have
built a linked list with extra steps, and search is O(n) again. Keeping a tree
balanced is what AVL and red-black trees are for, and it is deliberately outside
this course.

The `contains` search follows the same rule and needs **no** recursion, because
there is only ever one direction to go:

```ts
let cur: T | null = t;
while (cur !== null) {
  if (value === cur.value) { return true; }
  cur = value < cur.value ? cur.left : cur.right;
}
return false;
```

> ⚠️ **Common mistakes:** a recursive function with no base case (which recurses
> until the stack gives out); recursing on something that is not smaller; and
> assuming a BST is balanced.
""",
            warmup=[
                _q("A binary tree node has…",
                   ["one link", "two links", "many links", "no links"], 1,
                   "Which is why a single cursor cannot walk it."),
                _q("Every recursive function needs…",
                   ["a loop", "a base case and a smaller recursive call", "a class", "an array"], 1,
                   "Both visible in a tree's type."),
                _q("The base case of a tree recursion is usually…",
                   ["the root", "null", "the depth", "a leaf's value"], 1,
                   "The `| null` from the type."),
                _q("A BST built by inserting 1,2,3,4,5 in order is…",
                   ["balanced", "a linked list with extra steps", "empty", "O(log n)"], 1,
                   "Which is why balancing schemes exist."),
            ],
            exercises=[
                _ex("tscourse-w20-tr-1", "The tree type",
                    "Give the node its two child links.",
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'const t: T = {\n'
                    '  value: 2,\n'
                    '  left: { value: 1, left: null, right: null },\n'
                    '  right: { value: 3, left: null, right: null },\n'
                    '};\n'
                    'console.log(`${t.left?.value ?? 0} ${t.value} ${t.right?.value ?? 0}`);\n',
                    '  left: T | null;\n  right: T | null;', [("", "1 2 3")],
                    hints=["Two fields, each a node or nothing.",
                           "Write left: T | null; and right: T | null;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-tr-2", "The base case",
                    "Return the answer for an empty tree, so the recursion can stop.",
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function count(t: T | null): number {\n'
                    '  if (t === null) {\n'
                    '    return 0;\n  }\n'
                    '  return 1 + count(t.left) + count(t.right);\n}\n'
                    'const t: T = {\n'
                    '  value: 2,\n'
                    '  left: { value: 1, left: null, right: null },\n'
                    '  right: null,\n'
                    '};\n'
                    'console.log(count(t));\n',
                    '  if (t === null) {\n    return 0;\n  }', [("", "2")],
                    hints=["An empty tree has no nodes in it.",
                           "Write if (t === null) { return 0; }"],
                    difficulty="Medium"),
                _ex("tscourse-w20-tr-3", "Sum the values",
                    "Combine this node's value with both children's answers.",
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function sum(t: T | null): number {\n'
                    '  if (t === null) {\n'
                    '    return 0;\n  }\n'
                    '  return t.value + sum(t.left) + sum(t.right);\n}\n'
                    'const t: T = {\n'
                    '  value: 2,\n'
                    '  left: { value: 1, left: null, right: null },\n'
                    '  right: { value: 3, left: null, right: null },\n'
                    '};\n'
                    'console.log(sum(t));\n',
                    '  return t.value + sum(t.left) + sum(t.right);', [("", "6")],
                    hints=["This node, plus whatever each side adds up to.",
                           "Write return t.value + sum(t.left) + sum(t.right);"],
                    difficulty="Medium"),
                _ex("tscourse-w20-tr-4", "How deep",
                    "One for this node, plus the deeper of the two sides.",
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function depth(t: T | null): number {\n'
                    '  if (t === null) {\n'
                    '    return 0;\n  }\n'
                    '  return 1 + Math.max(depth(t.left), depth(t.right));\n}\n'
                    'const t: T = {\n'
                    '  value: 2,\n'
                    '  left: { value: 1, left: { value: 0, left: null, right: null }, right: null },\n'
                    '  right: null,\n'
                    '};\n'
                    'console.log(depth(t));\n',
                    '  return 1 + Math.max(depth(t.left), depth(t.right));', [("", "3")],
                    hints=["The deeper side decides, and this node adds one.",
                           "Write return 1 + Math.max(depth(t.left), depth(t.right));"],
                    difficulty="Medium"),
                _ex("tscourse-w20-tr-5", "Insert into a BST",
                    "Send the value left when it is smaller, and rebuild that side.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function inOrder(t: T | null, out: number[]): void {\n'
                    '  if (t === null) {\n'
                    '    return;\n  }\n'
                    '  inOrder(t.left, out);\n'
                    '  out.push(t.value);\n'
                    '  inOrder(t.right, out);\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'inOrder(root, out);\n'
                    'console.log(out.join(" "));\n',
                    '    t.left = insert(t.left, value);',
                    [("3 1 4 1 5", "1 3 4 5"), ("2", "2")],
                    hints=["The left subtree is replaced by the result of inserting into it.",
                           "Write t.left = insert(t.left, value);"],
                    difficulty="Medium"),
                _ex("tscourse-w20-tr-6", "Search without recursing",
                    "There is only one direction to go at each step, so a loop is enough.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function contains(t: T | null, value: number): boolean {\n'
                    '  let cur: T | null = t;\n'
                    '  while (cur !== null) {\n'
                    '    if (value === cur.value) {\n'
                    '      return true;\n    }\n'
                    '    cur = value < cur.value ? cur.left : cur.right;\n  }\n'
                    '  return false;\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'console.log(`${contains(root, 4)} ${contains(root, 99)}`);\n',
                    '    cur = value < cur.value ? cur.left : cur.right;',
                    [("3 1 4 5", "true false"), ("1", "false false")],
                    hints=["The BST rule tells you which single child could hold the value.",
                           "Write cur = value < cur.value ? cur.left : cur.right;"],
                    difficulty="Medium"),
                _diagnose("tscourse-w20-tr-d1", "The child that might not be there",
                          "TS18047: 't.left' is possibly 'null'.",
                          'interface T {\n'
                          '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                          'const t: T = { value: 2, left: null, right: null };\n'
                          'console.log(t.left.value);\n',
                          'interface T {\n'
                          '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                          'const t: T = { value: 2, left: null, right: null };\n'
                          'console.log(t.left?.value ?? 0);\n',
                          [("", "0")],
                          hints=["A leaf's children are null, and the type says so.",
                                 "Chain past the absence and supply a default.",
                                 "Write t.left?.value ?? 0."],
                          difficulty="Easy"),
                _fix("tscourse-w20-tr-fix1", "Fix the recursion with no floor",
                     "This crashes with `RangeError: Maximum call stack size exceeded`: `sum` recurses on both children without ever checking for the empty tree, so it walks straight past the leaves.",
                     'interface T {\n'
                     '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                     'function sum(t: T | null): number {\n'
                     '  return (t?.value ?? 0) + sum(t?.left ?? null) + sum(t?.right ?? null);\n}\n'
                     'const t: T = { value: 2, left: null, right: null };\n'
                     'console.log(sum(t));\n',
                     'interface T {\n'
                     '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                     'function sum(t: T | null): number {\n'
                     '  if (t === null) {\n'
                     '    return 0;\n  }\n'
                     '  return t.value + sum(t.left) + sum(t.right);\n}\n'
                     'const t: T = { value: 2, left: null, right: null };\n'
                     'console.log(sum(t));\n',
                     [("", "2")],
                     hints=["The `?.` made every line safe and removed the only thing that could stop the recursion.",
                            "A base case is a `return` that does NOT recurse.",
                            "Check for null first, and then the rest needs no optional chaining at all."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A BST's O(log n) search assumes…",
                   ["nothing", "the tree is reasonably balanced", "sorted input", "recursion"], 1,
                   "Sorted input is the worst case, not the best."),
                _q("`contains` on a BST needs no recursion because…",
                   ["it is faster", "there is only ever one child worth looking in", "of the type",
                    "it is iterative"], 1,
                   "One direction per step is a loop."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w20-traverse", "Traversals, and the one-line difference",
            "Three depth-first orders, and the single change that makes it breadth-first.",
            """
There are three ways to visit a binary tree depth-first, and they differ only in
**where you handle the node** relative to its children.

```ts
function preOrder(t: T | null, out: number[]): void {
  if (t === null) { return; }
  out.push(t.value);                    // ← node FIRST
  preOrder(t.left, out);
  preOrder(t.right, out);
}
function inOrder(t: T | null, out: number[]): void {
  if (t === null) { return; }
  inOrder(t.left, out);
  out.push(t.value);                    // ← node in the MIDDLE
  inOrder(t.right, out);
}
function postOrder(t: T | null, out: number[]): void {
  if (t === null) { return; }
  postOrder(t.left, out);
  postOrder(t.right, out);
  out.push(t.value);                    // ← node LAST
}
```

One line moves. Three completely different answers.

## Which one, and when

* **Pre-order** — you need the node before its children: printing a tree with
  indentation, copying one, serialising one.
* **In-order** — on a **BST this is sorted order**, which is the single most useful
  fact about BSTs.
* **Post-order** — the node's answer *depends on* its children: totalling a
  category tree, computing depth, freeing a structure. Anything that rolls up.

"Which traversal?" is answered by "when do I know the node's answer?", and that is
worth more than memorising the three orders.

## Depth-first without recursion — week 18's stack

```ts
const stack: T[] = [root];
while (stack.length > 0) {
  const node = stack.pop();
  if (node === undefined) { continue; }
  out.push(node.value);
  if (node.right !== null) { stack.push(node.right); }   // right FIRST…
  if (node.left !== null) { stack.push(node.left); }     // …so left pops first
}
```

That is pre-order, and the push order is the subtlety: a stack reverses, so to
visit the left child first you must push it **last**.

## Breadth-first — change the structure, change everything

```ts
const queue: T[] = [root];
let head = 0;
while (head < queue.length) {
  const node = queue[head];
  head = head + 1;                               // week 18's O(1) dequeue
  if (node === undefined) { continue; }
  out.push(node.value);
  if (node.left !== null) { queue.push(node.left); }
  if (node.right !== null) { queue.push(node.right); }
}
```

**The loop is the same. `pop()` became a dequeue, and the answer changed shape
completely** — you now visit the tree level by level rather than branch by branch.

This is the payoff week 18 was setting up, and it is worth stating plainly:

> Depth-first and breadth-first are the same algorithm with a different container.
> A stack goes deep; a queue goes wide.

Everything in week 27 about graphs is this fact again, plus a visited set.

## Recursive or iterative?

Recursive, normally — it is shorter and it reads like the definition. Iterative
when the tree might be deep enough to exhaust the call stack (in Node, tens of
thousands of frames), or when you need to pause and resume the walk. BFS is
*always* iterative: there is no natural recursive form, because the next node to
visit is not related to the current one.

> ⚠️ **Common mistakes:** pushing children left-first onto a stack and getting a
> mirrored pre-order; using `shift()` for the BFS queue (week 18's O(n) trap); and
> reaching for in-order on a tree that is not a BST, where it means nothing in
> particular.
""",
            warmup=[
                _q("The three depth-first orders differ in…",
                   ["the children visited", "where the node is handled relative to its children",
                    "the data structure", "the base case"], 1,
                   "One line moves."),
                _q("In-order on a BST gives…",
                   ["insertion order", "sorted order", "level order", "reverse order"], 1,
                   "The most useful fact about BSTs."),
                _q("When a node's answer depends on its children, use…",
                   ["pre-order", "post-order", "in-order", "BFS"], 1,
                   "Children first."),
                _q("DFS becomes BFS by changing…",
                   ["the recursion", "the stack to a queue", "the base case", "the order of pushes"], 1,
                   "Same loop, different container."),
            ],
            exercises=[
                _ex("tscourse-w20-tv-1", "Pre-order",
                    "Handle the node before either child.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function preOrder(t: T | null, out: number[]): void {\n'
                    '  if (t === null) {\n'
                    '    return;\n  }\n'
                    '  out.push(t.value);\n'
                    '  preOrder(t.left, out);\n'
                    '  preOrder(t.right, out);\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'preOrder(root, out);\n'
                    'console.log(out.join(" "));\n',
                    '  out.push(t.value);\n'
                    '  preOrder(t.left, out);\n'
                    '  preOrder(t.right, out);',
                    [("2 1 3", "2 1 3"), ("3 1 4 2", "3 1 2 4")],
                    hints=["Node, then left, then right.",
                           "Write out.push(t.value); then the two recursive calls."],
                    difficulty="Medium"),
                _ex("tscourse-w20-tv-2", "In-order, which sorts a BST",
                    "Put the node's own value between the two recursive calls.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function inOrder(t: T | null, out: number[]): void {\n'
                    '  if (t === null) {\n'
                    '    return;\n  }\n'
                    '  inOrder(t.left, out);\n'
                    '  out.push(t.value);\n'
                    '  inOrder(t.right, out);\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'inOrder(root, out);\n'
                    'console.log(out.join(" "));\n',
                    '  inOrder(t.left, out);\n'
                    '  out.push(t.value);\n'
                    '  inOrder(t.right, out);',
                    [("3 1 4 2", "1 2 3 4"), ("5 9 1", "1 5 9")],
                    hints=["Left, node, right — and on a BST that comes out sorted.",
                           "Write the left call, the push, then the right call."],
                    difficulty="Medium"),
                _ex("tscourse-w20-tv-3", "Post-order, for a roll-up",
                    "Visit both children before the node, which is what a total needs.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'function postOrder(t: T | null, out: number[]): void {\n'
                    '  if (t === null) {\n'
                    '    return;\n  }\n'
                    '  postOrder(t.left, out);\n'
                    '  postOrder(t.right, out);\n'
                    '  out.push(t.value);\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'postOrder(root, out);\n'
                    'console.log(out.join(" "));\n',
                    '  out.push(t.value);\n}', [("2 1 3", "1 3 2"), ("3 1 4 2", "2 1 4 3")],
                    hints=["The node's own value goes last, after both calls.",
                           "Write out.push(t.value); as the final statement of the function."],
                    difficulty="Medium"),
                _ex("tscourse-w20-tv-4", "Depth-first with a stack",
                    "Push the right child before the left, so the left one is popped first.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'const stack: T[] = root === null ? [] : [root];\n'
                    'while (stack.length > 0) {\n'
                    '  const node = stack.pop();\n'
                    '  if (node === undefined) {\n'
                    '    continue;\n  }\n'
                    '  out.push(node.value);\n'
                    '  if (node.right !== null) {\n'
                    '    stack.push(node.right);\n  }\n'
                    '  if (node.left !== null) {\n'
                    '    stack.push(node.left);\n  }\n}\n'
                    'console.log(out.join(" "));\n',
                    '  if (node.right !== null) {\n'
                    '    stack.push(node.right);\n  }\n'
                    '  if (node.left !== null) {\n'
                    '    stack.push(node.left);\n  }',
                    [("2 1 3", "2 1 3"), ("3 1 4 2", "3 1 2 4")],
                    hints=["A stack reverses, so whichever child you push LAST is visited first.",
                           "Push right, then left."],
                    difficulty="Hard"),
                _ex("tscourse-w20-tv-5", "Breadth-first with a queue",
                    "Change the container and read from the front, so the tree is visited level by level.",
                    _NUMS +
                    'interface T {\n'
                    '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                    'function insert(t: T | null, value: number): T {\n'
                    '  if (t === null) {\n'
                    '    return { value, left: null, right: null };\n  }\n'
                    '  if (value < t.value) {\n'
                    '    t.left = insert(t.left, value);\n'
                    '  } else if (value > t.value) {\n'
                    '    t.right = insert(t.right, value);\n  }\n'
                    '  return t;\n}\n'
                    'let root: T | null = null;\n'
                    'for (const n of nums) {\n'
                    '  root = insert(root, n);\n}\n'
                    'const out: number[] = [];\n'
                    'const queue: T[] = root === null ? [] : [root];\n'
                    'let head = 0;\n'
                    'while (head < queue.length) {\n'
                    '  const node = queue[head];\n'
                    '  head = head + 1;\n'
                    '  if (node === undefined) {\n'
                    '    continue;\n  }\n'
                    '  out.push(node.value);\n'
                    '  if (node.left !== null) {\n'
                    '    queue.push(node.left);\n  }\n'
                    '  if (node.right !== null) {\n'
                    '    queue.push(node.right);\n  }\n}\n'
                    'console.log(out.join(" "));\n',
                    '  head = head + 1;',
                    [("3 1 4 2", "3 1 4 2"), ("5 3 8 1", "5 3 8 1")],
                    hints=["Week 18's O(1) dequeue: move the index, not the data.",
                           "Write head = head + 1;"],
                    difficulty="Hard"),
                _ex("tscourse-w20-tv-6", "Print it with indentation",
                    "Pre-order with a depth parameter, which is how a tree gets printed.",
                    _TREE +
                    'function print(c: Cat, depth: number): void {\n'
                    '  console.log(`${"  ".repeat(depth)}${c.name}`);\n'
                    '  for (const kid of c.kids) {\n'
                    '    print(kid, depth + 1);\n  }\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 325, kids: [{ name: "coffee", cents: 325, kids: [] }] },\n'
                    '    { name: "home", cents: 90000, kids: [] },\n'
                    '  ],\n};\n'
                    'print(root, 0);\n',
                    '    print(kid, depth + 1);',
                    [("", "all\n  food\n    coffee\n  home")],
                    hints=["Each child is one level deeper than its parent.",
                           "Write print(kid, depth + 1);"],
                    difficulty="Medium"),
                _fix("tscourse-w20-tv-fix1", "Fix the mirrored traversal",
                     "This iterative pre-order prints `3 4 1 2` for a tree whose recursive pre-order is `3 1 2 4` — the children go onto the stack in the wrong order, and a stack reverses whatever you give it.",
                     _NUMS +
                     'interface T {\n'
                     '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                     'function insert(t: T | null, value: number): T {\n'
                     '  if (t === null) {\n'
                     '    return { value, left: null, right: null };\n  }\n'
                     '  if (value < t.value) {\n'
                     '    t.left = insert(t.left, value);\n'
                     '  } else if (value > t.value) {\n'
                     '    t.right = insert(t.right, value);\n  }\n'
                     '  return t;\n}\n'
                     'let root: T | null = null;\n'
                     'for (const n of nums) {\n'
                     '  root = insert(root, n);\n}\n'
                     'const out: number[] = [];\n'
                     'const stack: T[] = root === null ? [] : [root];\n'
                     'while (stack.length > 0) {\n'
                     '  const node = stack.pop();\n'
                     '  if (node === undefined) {\n'
                     '    continue;\n  }\n'
                     '  out.push(node.value);\n'
                     '  if (node.left !== null) {\n'
                     '    stack.push(node.left);\n  }\n'
                     '  if (node.right !== null) {\n'
                     '    stack.push(node.right);\n  }\n}\n'
                     'console.log(out.join(" "));\n',
                     _NUMS +
                     'interface T {\n'
                     '  readonly value: number;\n  left: T | null;\n  right: T | null;\n}\n'
                     'function insert(t: T | null, value: number): T {\n'
                     '  if (t === null) {\n'
                     '    return { value, left: null, right: null };\n  }\n'
                     '  if (value < t.value) {\n'
                     '    t.left = insert(t.left, value);\n'
                     '  } else if (value > t.value) {\n'
                     '    t.right = insert(t.right, value);\n  }\n'
                     '  return t;\n}\n'
                     'let root: T | null = null;\n'
                     'for (const n of nums) {\n'
                     '  root = insert(root, n);\n}\n'
                     'const out: number[] = [];\n'
                     'const stack: T[] = root === null ? [] : [root];\n'
                     'while (stack.length > 0) {\n'
                     '  const node = stack.pop();\n'
                     '  if (node === undefined) {\n'
                     '    continue;\n  }\n'
                     '  out.push(node.value);\n'
                     '  if (node.right !== null) {\n'
                     '    stack.push(node.right);\n  }\n'
                     '  if (node.left !== null) {\n'
                     '    stack.push(node.left);\n  }\n}\n'
                     'console.log(out.join(" "));\n',
                     [("3 1 4 2", "3 1 2 4"), ("2 1 3", "2 1 3")],
                     hints=["The left child is pushed first and therefore popped LAST.",
                            "To visit left first, push it last.",
                            "Swap the two `if` blocks."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("BFS has no natural recursive form because…",
                   ["it is iterative", "the next node to visit is not related to the current one",
                    "of the queue", "it is faster"], 1,
                   "Which is why every BFS you will read is a loop."),
                _q("Using `shift()` for a BFS queue is…",
                   ["correct and O(n) per step — week 18's trap", "required", "O(1)", "faster"], 0,
                   "A head index keeps it O(1)."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w20-ntree", "Many children",
            "The shape most real trees actually have.",
            """
Two children is the special case. Real hierarchies — a file system, a category
tree, a comment thread, the DOM — have **any number**:

```ts
interface Cat {
  readonly name: string;
  readonly cents: number;
  readonly kids: readonly Cat[];
}
```

`readonly Cat[]` instead of two nullable fields, and the `| null` floor is gone —
its job is done by the **empty array**. A leaf is a node whose `kids` is `[]`, so
there is no absence to handle anywhere, and every traversal becomes a `for … of`.

That is a genuinely nicer type, and it is worth noticing why: "no children" is
better modelled as *none of them* than as *two of them missing*.

## Recursion over it

```ts
function total(c: Cat): number {
  let sum = c.cents;
  for (const kid of c.kids) {
    sum = sum + total(kid);          // post-order: children first
  }
  return sum;
}
```

The base case is invisible and still there: a node with no children never enters
the loop, so it returns its own `cents` without recursing. **An empty collection is
a base case** — which is the single most useful thing to know about recursion over
data.

## Counting, depth, and the roll-up

```ts
function count(c: Cat): number {
  let n = 1;
  for (const kid of c.kids) { n = n + count(kid); }
  return n;
}
function depth(c: Cat): number {
  let deepest = 0;
  for (const kid of c.kids) { deepest = Math.max(deepest, depth(kid)); }
  return 1 + deepest;
}
```

Same skeleton every time: an accumulator, a loop over the children, a combining
step. Once you have written it twice you stop thinking about it.

## Finding a path

The one genuinely new shape, and the capstone needs it:

```ts
function pathTo(c: Cat, name: string): readonly string[] | null {
  if (c.name === name) { return [c.name]; }
  for (const kid of c.kids) {
    const below = pathTo(kid, name);
    if (below !== null) { return [c.name, ...below]; }   // prepend on the way OUT
  }
  return null;                                            // not in this subtree
}
```

Two things worth reading twice:

* The answer is built **on the way back up** — each level adds its own name to
  whatever the level below returned.
* `return null` means "not in this subtree", and the loop above interprets it as
  "keep looking". That pattern — a search that reports failure so its caller can
  try the next branch — is exactly what backtracking is, and week 25 gives it a
  name.

## Flatten it

```ts
function flatten(c: Cat): readonly Cat[] {
  const out: Cat[] = [c];
  for (const kid of c.kids) { out.push(...flatten(kid)); }
  return out;
}
```

Useful, and worth knowing that lesson 8 does the same job **lazily** with a
generator, without building any of the intermediate arrays.

> ⚠️ **Common mistakes:** keeping `| null` on a `kids` array (`[]` already says
> "none"); building a path on the way *down* and having to undo it; and flattening
> a large tree when you only wanted the first match.
""",
            warmup=[
                _q("For an n-ary tree, `kids: readonly Cat[]` needs…",
                   ["| null", "nothing — `[]` means no children", "| undefined", "a class"], 1,
                   "The empty array is the floor."),
                _q("A leaf's recursion terminates because…",
                   ["of a null check", "the loop over its children never runs", "of the type",
                    "of depth"], 1,
                   "An empty collection IS a base case."),
                _q("A path is built…",
                   ["on the way down", "on the way back up, each level prepending its own name",
                    "with a stack", "with a Map"], 1,
                   "Which is why the return type is an array."),
                _q("Returning `null` from a subtree search means…",
                   ["an error", "not in this subtree — so the caller tries the next branch",
                    "empty tree", "found"], 1,
                   "That is backtracking, before it has a name."),
            ],
            exercises=[
                _ex("tscourse-w20-nt-1", "Roll the totals up",
                    "Add each child's total to this node's own amount.",
                    _TREE +
                    'function total(c: Cat): number {\n'
                    '  let sum = c.cents;\n'
                    '  for (const kid of c.kids) {\n'
                    '    sum = sum + total(kid);\n  }\n'
                    '  return sum;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 100, kids: [{ name: "coffee", cents: 225, kids: [] }] },\n'
                    '    { name: "home", cents: 90000, kids: [] },\n'
                    '  ],\n};\n'
                    'console.log(total(root));\n',
                    '    sum = sum + total(kid);', [("", "90325")],
                    hints=["Each child contributes its whole subtree.",
                           "Write sum = sum + total(kid);"],
                    difficulty="Medium"),
                _ex("tscourse-w20-nt-2", "Count the nodes",
                    "One for this node, plus every node below it.",
                    _TREE +
                    'function count(c: Cat): number {\n'
                    '  let n = 1;\n'
                    '  for (const kid of c.kids) {\n'
                    '    n = n + count(kid);\n  }\n'
                    '  return n;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 0, kids: [{ name: "coffee", cents: 0, kids: [] }] },\n'
                    '    { name: "home", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'console.log(count(root));\n',
                    '  let n = 1;', [("", "4")],
                    hints=["The accumulator starts at one, for the node you are standing on.",
                           "Write let n = 1;"],
                    difficulty="Easy"),
                _ex("tscourse-w20-nt-3", "How deep does it go",
                    "Take the deepest child and add one for this level.",
                    _TREE +
                    'function depth(c: Cat): number {\n'
                    '  let deepest = 0;\n'
                    '  for (const kid of c.kids) {\n'
                    '    deepest = Math.max(deepest, depth(kid));\n  }\n'
                    '  return 1 + deepest;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 0, kids: [{ name: "coffee", cents: 0, kids: [] }] },\n'
                    '    { name: "home", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'console.log(depth(root));\n',
                    '  return 1 + deepest;', [("", "3")],
                    hints=["The deepest branch decides; this node adds a level.",
                           "Write return 1 + deepest;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-nt-4", "The path to a category",
                    "Prepend this node's name to whatever the successful child returned.",
                    _LINE + _TREE +
                    'function pathTo(c: Cat, name: string): readonly string[] | null {\n'
                    '  if (c.name === name) {\n'
                    '    return [c.name];\n  }\n'
                    '  for (const kid of c.kids) {\n'
                    '    const below = pathTo(kid, name);\n'
                    '    if (below !== null) {\n'
                    '      return [c.name, ...below];\n    }\n  }\n'
                    '  return null;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 0, kids: [{ name: "coffee", cents: 0, kids: [] }] },\n'
                    '    { name: "home", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'const found = pathTo(root, line);\n'
                    'console.log(found === null ? "not found" : found.join("/"));\n',
                    '      return [c.name, ...below];',
                    [("coffee", "all/food/coffee"), ("home", "all/home"), ("rent", "not found")],
                    hints=["The child handed back the path from itself downwards; add your own name in front.",
                           "Write return [c.name, ...below];"],
                    difficulty="Hard"),
                _ex("tscourse-w20-nt-5", "Flatten the tree",
                    "Collect this node and everything beneath it into one array.",
                    _TREE +
                    'function flatten(c: Cat): readonly Cat[] {\n'
                    '  const out: Cat[] = [c];\n'
                    '  for (const kid of c.kids) {\n'
                    '    out.push(...flatten(kid));\n  }\n'
                    '  return out;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 0, kids: [{ name: "coffee", cents: 0, kids: [] }] },\n'
                    '    { name: "home", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'console.log(flatten(root).map((c) => c.name).join(" "));\n',
                    '    out.push(...flatten(kid));',
                    [("", "all food coffee home")],
                    hints=["Spread each child's flattened subtree into the accumulator.",
                           "Write out.push(...flatten(kid));"],
                    difficulty="Medium"),
                _ex("tscourse-w20-nt-6", "Leaves only",
                    "Collect the nodes that have no children.",
                    _TREE +
                    'function leaves(c: Cat): readonly string[] {\n'
                    '  if (c.kids.length === 0) {\n'
                    '    return [c.name];\n  }\n'
                    '  const out: string[] = [];\n'
                    '  for (const kid of c.kids) {\n'
                    '    out.push(...leaves(kid));\n  }\n'
                    '  return out;\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 0, kids: [{ name: "coffee", cents: 0, kids: [] }] },\n'
                    '    { name: "home", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'console.log(leaves(root).join(" "));\n',
                    '  if (c.kids.length === 0) {\n    return [c.name];\n  }',
                    [("", "coffee home")],
                    hints=["A leaf is a node with an empty `kids` array, and it contributes only itself.",
                           "Write if (c.kids.length === 0) { return [c.name]; }"],
                    difficulty="Medium"),
                _design("tscourse-w20-nt-des1", "Design the node",
                        "The traversal below is written; work out the type it walks. A category has a name, "
                        "an amount in cents and any number of children — and no field may be nullable.",
                        'interface Cat {\n'
                        '  readonly name: string;\n'
                        '  readonly cents: number;\n'
                        '  readonly kids: readonly Cat[];\n'
                        '}\n'
                        'function total(c: Cat): number {\n'
                        '  let sum = c.cents;\n'
                        '  for (const kid of c.kids) {\n'
                        '    sum = sum + total(kid);\n  }\n'
                        '  return sum;\n}\n'
                        'const root: Cat = {\n'
                        '  name: "all",\n  cents: 0,\n'
                        '  kids: [{ name: "food", cents: 325, kids: [] }],\n};\n'
                        'console.log(`${root.name} ${total(root)}`);\n',
                        'interface Cat {\n'
                        '  readonly name: string;\n'
                        '  readonly cents: number;\n'
                        '  readonly kids: readonly Cat[];\n'
                        '}',
                        'type _1 = Expect<Equal<typeof root.name, string>>;\n'
                        'type _2 = Expect<Equal<typeof root.kids, readonly Cat[]>>;\n',
                        [("", "all 325")],
                        hints=["Three members, and the third refers to the type being declared.",
                               "`readonly Cat[]` — an empty array is how a leaf says it has no children.",
                               "All three members are readonly."],
                        difficulty="Medium"),
                _fix("tscourse-w20-nt-fix1", "Fix the total that missed the root",
                     "The accumulator starts at zero instead of at this node's own amount, so every node's own spend is dropped and the answer only counts the leaves' parents. Start from the node.",
                     _TREE +
                     'function total(c: Cat): number {\n'
                     '  let sum = 0;\n'
                     '  for (const kid of c.kids) {\n'
                     '    sum = sum + total(kid);\n  }\n'
                     '  return sum;\n}\n'
                     'const root: Cat = {\n'
                     '  name: "all",\n  cents: 0,\n'
                     '  kids: [\n'
                     '    { name: "food", cents: 100, kids: [{ name: "coffee", cents: 225, kids: [] }] },\n'
                     '    { name: "home", cents: 90000, kids: [] },\n'
                     '  ],\n};\n'
                     'console.log(total(root));\n',
                     _TREE +
                     'function total(c: Cat): number {\n'
                     '  let sum = c.cents;\n'
                     '  for (const kid of c.kids) {\n'
                     '    sum = sum + total(kid);\n  }\n'
                     '  return sum;\n}\n'
                     'const root: Cat = {\n'
                     '  name: "all",\n  cents: 0,\n'
                     '  kids: [\n'
                     '    { name: "food", cents: 100, kids: [{ name: "coffee", cents: 225, kids: [] }] },\n'
                     '    { name: "home", cents: 90000, kids: [] },\n'
                     '  ],\n};\n'
                     'console.log(total(root));\n',
                     [("", "90325")],
                     hints=["A leaf returns zero, which is how the loss propagates upwards.",
                            "The node's own amount is part of its subtree's total.",
                            "Start the accumulator at `c.cents`."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("`readonly Cat[]` is a better model than two nullable children because…",
                   ["it is shorter", "'no children' is none of them, not two that are missing",
                    "it is faster", "of readonly"], 1,
                   "And every traversal becomes a for…of."),
                _q("The path search's `return null` is…",
                   ["an error", "'not in this subtree', which is backtracking before it has a name",
                    "a base case", "a failure"], 1,
                   "Week 25 names it."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w20-iterators", "Iterables and generators",
            "Handing out a sequence one value at a time.",
            """
`for … of` and `[...spread]` are not special-cased for arrays. They work on
anything that implements one method:

```ts
class Bag<T> {
  private readonly items: T[] = [];
  add(value: T): void { this.items.push(value); }

  [Symbol.iterator](): Iterator<T> {
    return this.items[Symbol.iterator]();      // delegate to the array's
  }
}

const bag = new Bag<string>();
bag.add("a");
for (const v of bag) { … }        // ✅ works
[...bag];                          // ✅ works
```

That is the **iterable protocol**, and it is worth knowing because it is how you
make your own types feel like built-in ones — week 18's `Stack` and `Queue` would
both be better with it.

## Generators write the iterator for you

Implementing `Iterator<T>` by hand means writing a `next()` that returns
`{ value, done }` and tracking your own position. A **generator** does it for you:

```ts
function* upTo(n: number): Generator<number> {
  for (let i = 1; i <= n; i = i + 1) {
    yield i;                       // hand one value out, and PAUSE here
  }
}
[...upTo(3)];                       // [1, 2, 3]
```

`function*` declares a generator; `yield` produces a value and suspends the
function, which resumes from that exact point when the next value is asked for.

A generator is both an iterator and an iterable, so it works directly in `for … of`
and in a spread.

## As a method

```ts
class Bag<T> {
  private readonly items: T[] = [];
  *[Symbol.iterator](): Generator<T> {
    for (const item of this.items) { yield item; }
  }
}
```

The `*` in front of the method name is the whole difference. This is the usual way
to make a collection iterable, because the body can do anything — filter, map,
walk a tree — rather than just forwarding to an array.

## `yield*` delegates, and that is how you walk a tree

```ts
function* walk(c: Cat): Generator<Cat> {
  yield c;
  for (const kid of c.kids) {
    yield* walk(kid);              // yield everything that recursive call yields
  }
}
for (const c of walk(root)) { … }
```

`yield*` hands out every value from another iterable. With a recursive call, that
is a full pre-order traversal **lazily** — the caller can stop after three values
and the rest of the tree is never visited.

Compare it to lesson 7's `flatten`, which builds an array of every node before the
caller sees any of them. The generator version allocates nothing and can be stopped
at will, which is the whole argument for generators:

> A generator separates *producing* a sequence from *deciding how much of it you
> need.*

## Laziness, made visible

```ts
function* naturals(): Generator<number> {
  let n = 1;
  for (;;) { yield n; n = n + 1; }         // infinite, and perfectly fine
}
const first3: number[] = [];
for (const n of naturals()) {
  if (first3.length === 3) { break; }
  first3.push(n);
}
```

An infinite sequence is only a problem if you try to build it. This one produces
three numbers and stops — and `break` in a `for … of` over a generator is what
tells it to.

> ⚠️ **Common mistakes:** forgetting the `*` (you get a normal function that
> returns undefined and a confusing error at the `yield`); spreading an infinite
> generator; and re-using a generator object, which is exhausted after one pass.
""",
            warmup=[
                _q("`for … of` works on any object with…",
                   ["a length", "a [Symbol.iterator] method", "an index signature", "next()"], 1,
                   "That is the whole protocol."),
                _q("`yield` does what?",
                   ["returns", "hands out one value and pauses the function there", "throws",
                    "loops"], 1,
                   "Resuming from that point when asked again."),
                _q("`yield*` does what?",
                   ["yields an array", "hands out every value from another iterable", "returns",
                    "recurses"], 1,
                   "Which makes a recursive generator a lazy traversal."),
                _q("A generator object, iterated twice…",
                   ["restarts", "is exhausted after the first pass", "throws", "caches"], 1,
                   "Call the generator function again for a fresh one."),
            ],
            exercises=[
                _ex("tscourse-w20-it-1", "Make a class iterable",
                    "Add the method that makes `for … of` and spread work.",
                    _WORDS +
                    'class Bag<T> {\n'
                    '  private readonly items: T[] = [];\n'
                    '  add(value: T): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  [Symbol.iterator](): Iterator<T> {\n'
                    '    return this.items[Symbol.iterator]();\n  }\n}\n'
                    'const bag = new Bag<string>();\n'
                    'for (const w of words) {\n'
                    '  bag.add(w);\n}\n'
                    'console.log([...bag].join(","));\n',
                    '  [Symbol.iterator](): Iterator<T> {',
                    [("a b c", "a,b,c"), ("solo", "solo")],
                    hints=["A computed method name, using the well-known symbol.",
                           "Write [Symbol.iterator](): Iterator<T> {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-it-2", "Write a generator",
                    "Declare it so that `yield` is legal, and hand out one value per step.",
                    _NUMS +
                    'function* upTo(n: number): Generator<number> {\n'
                    '  for (let i = 1; i <= n; i = i + 1) {\n'
                    '    yield i;\n  }\n}\n'
                    'console.log([...upTo(nums[0] ?? 0)].join(","));\n',
                    'function* upTo(n: number): Generator<number> {',
                    [("3", "1,2,3"), ("1", "1")],
                    hints=["The star goes between `function` and the name.",
                           "Write function* upTo(n: number): Generator<number> {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-it-3", "A generator method",
                    "Make the bag iterable with a generator, so the body can do more than forward.",
                    _NUMS +
                    'class Bag {\n'
                    '  private readonly items: number[] = [];\n'
                    '  add(value: number): void {\n'
                    '    this.items.push(value);\n  }\n'
                    '  *[Symbol.iterator](): Generator<number> {\n'
                    '    for (const item of this.items) {\n'
                    '      if (item > 0) {\n'
                    '        yield item;\n      }\n    }\n  }\n}\n'
                    'const bag = new Bag();\n'
                    'for (const n of nums) {\n'
                    '  bag.add(n);\n}\n'
                    'console.log([...bag].join(","));\n',
                    '  *[Symbol.iterator](): Generator<number> {',
                    [("1 -2 3", "1,3"), ("5", "5")],
                    hints=["One star in front of the computed method name.",
                           "Write *[Symbol.iterator](): Generator<number> {"],
                    difficulty="Medium"),
                _ex("tscourse-w20-it-4", "Delegate with `yield*`",
                    "Hand out everything the recursive call produces, which walks the whole tree lazily.",
                    _TREE +
                    'function* walk(c: Cat): Generator<Cat> {\n'
                    '  yield c;\n'
                    '  for (const kid of c.kids) {\n'
                    '    yield* walk(kid);\n  }\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "food", cents: 325, kids: [{ name: "coffee", cents: 325, kids: [] }] },\n'
                    '    { name: "home", cents: 90000, kids: [] },\n'
                    '  ],\n};\n'
                    'const names: string[] = [];\n'
                    'for (const c of walk(root)) {\n'
                    '  names.push(c.name);\n}\n'
                    'console.log(names.join(" "));\n',
                    '    yield* walk(kid);', [("", "all food coffee home")],
                    hints=["Not `yield walk(kid)` — that would hand out the generator itself.",
                           "Write yield* walk(kid);"],
                    difficulty="Medium"),
                _ex("tscourse-w20-it-5", "Stop early",
                    "Break out of the loop, so the rest of the infinite sequence is never produced.",
                    _NUMS +
                    'function* naturals(): Generator<number> {\n'
                    '  let n = 1;\n'
                    '  for (;;) {\n'
                    '    yield n;\n'
                    '    n = n + 1;\n  }\n}\n'
                    'const want = nums[0] ?? 0;\n'
                    'const out: number[] = [];\n'
                    'for (const n of naturals()) {\n'
                    '  if (out.length === want) {\n'
                    '    break;\n  }\n'
                    '  out.push(n);\n}\n'
                    'console.log(out.join(","));\n',
                    '    break;', [("3", "1,2,3"), ("0", "")],
                    hints=["The generator only produces a value when asked, so leaving the loop stops it.",
                           "Write break;"],
                    difficulty="Medium"),
                _ex("tscourse-w20-it-6", "Lazy beats eager",
                    "Count how many nodes the walk actually visits when the caller stops after the first two.",
                    _TREE +
                    'let visited = 0;\n'
                    'function* walk(c: Cat): Generator<Cat> {\n'
                    '  visited = visited + 1;\n'
                    '  yield c;\n'
                    '  for (const kid of c.kids) {\n'
                    '    yield* walk(kid);\n  }\n}\n'
                    'const root: Cat = {\n'
                    '  name: "all",\n  cents: 0,\n'
                    '  kids: [\n'
                    '    { name: "a", cents: 0, kids: [{ name: "b", cents: 0, kids: [] }] },\n'
                    '    { name: "c", cents: 0, kids: [] },\n'
                    '  ],\n};\n'
                    'const names: string[] = [];\n'
                    'for (const c of walk(root)) {\n'
                    '  if (names.length === 2) {\n'
                    '    break;\n  }\n'
                    '  names.push(c.name);\n}\n'
                    'console.log(`${names.join(" ")} visited ${visited}`);\n',
                    '  if (names.length === 2) {\n    break;\n  }',
                    [("", "all a visited 3")],
                    hints=["Stop once two names have been collected.",
                           "Write if (names.length === 2) { break; }"],
                    difficulty="Hard"),
                _diagnose("tscourse-w20-it-d1", "`yield` without the star",
                          "TS1163: A 'yield' expression is only allowed in a generator body.",
                          'function upTo(n: number): Generator<number> {\n'
                          '  for (let i = 1; i <= n; i = i + 1) {\n'
                          '    yield i;\n  }\n}\n'
                          'console.log([...upTo(3)].join(","));\n',
                          'function* upTo(n: number): Generator<number> {\n'
                          '  for (let i = 1; i <= n; i = i + 1) {\n'
                          '    yield i;\n  }\n}\n'
                          'console.log([...upTo(3)].join(","));\n',
                          [("", "1,2,3")],
                          hints=["`yield` is only a keyword inside a generator; anywhere else it is read as an identifier.",
                                 "One character is missing from the declaration.",
                                 "Write function* upTo(…)."],
                          difficulty="Easy"),
                _fix("tscourse-w20-it-fix1", "Fix the delegation that yielded generators",
                     "`yield walk(kid)` hands out the generator *object* rather than the values inside it — and the "
                     "widened return type does not save it: `TS2322: Type 'Generator<Cat | Generator<Cat>>' is not "
                     "assignable to type 'Cat | Generator<Cat>'`. The nesting grows one level per depth, which no "
                     "annotation can keep up with. One character fixes it.",
                     _TREE +
                     'function* walk(c: Cat): Generator<Cat | Generator<Cat>> {\n'
                     '  yield c;\n'
                     '  for (const kid of c.kids) {\n'
                     '    yield walk(kid);\n  }\n}\n'
                     'const root: Cat = {\n'
                     '  name: "all",\n  cents: 0,\n'
                     '  kids: [\n'
                     '    { name: "food", cents: 0, kids: [] },\n'
                     '    { name: "home", cents: 0, kids: [] },\n'
                     '  ],\n};\n'
                     'const out: string[] = [];\n'
                     'for (const c of walk(root)) {\n'
                     '  out.push("name" in c ? c.name : String(c));\n}\n'
                     'console.log(out.join(" "));\n',
                     _TREE +
                     'function* walk(c: Cat): Generator<Cat> {\n'
                     '  yield c;\n'
                     '  for (const kid of c.kids) {\n'
                     '    yield* walk(kid);\n  }\n}\n'
                     'const out: string[] = [];\n'
                     'const root: Cat = {\n'
                     '  name: "all",\n  cents: 0,\n'
                     '  kids: [\n'
                     '    { name: "food", cents: 0, kids: [] },\n'
                     '    { name: "home", cents: 0, kids: [] },\n'
                     '  ],\n};\n'
                     'for (const c of walk(root)) {\n'
                     '  out.push(c.name);\n}\n'
                     'console.log(out.join(" "));\n',
                     [("", "all food home")],
                     hints=["The return type is the clue: it had to be widened to admit the generators it was yielding.",
                            "One character turns 'yield this value' into 'yield all of that iterable's values'.",
                            "With `yield*` the return type collapses back to `Generator<Cat>` and the narrowing disappears."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A generator separates…",
                   ["types from values", "producing a sequence from deciding how much of it you need",
                    "sync from async", "nothing"], 1,
                   "Which is why an infinite one is fine."),
                _q("Week 18's Stack and Queue would be improved by…",
                   ["a Map", "implementing [Symbol.iterator]", "recursion", "a generator return type"], 1,
                   "Then they would work in for…of like built-ins."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #20 — the category tree",
        """
Twenty weeks ago Budget Buddy printed one receipt line. It ends as a **category
tree**: nested categories to any depth, each with its own spend and its own
budget, totals rolled up from the leaves, and the whole report handed out through
a generator.

Input: one category per line, indented with two spaces per level, as
`<name> <cents> <budget>`.

```
all 0 0
  food 0 1000
    coffee 325 400
    lunch 450 600
  home 90000 95000
```

```
all           $907.75 / $0.00  OVER
  food          $7.75 / $10.00
    coffee      $3.25 / $4.00
    lunch       $4.50 / $6.00
  home        $900.00 / $950.00
Categories:   5
Deepest:      3
Over budget:  all
Biggest leaf: home $900.00
```

**What it has to do:**

1. **Parse the indentation into a tree.** Two spaces per level. Keep a stack of
   the ancestors currently open (week 18): a line at depth `d` is a child of the
   node at the top of the stack once the stack has been trimmed to `d` entries.
   This is the week's two halves meeting — a stack, used to build a tree.
2. **Roll the totals up.** A category's total is its own spend plus every
   descendant's — a post-order sum (lesson 6).
3. **Print pre-order, indented**, with the rolled-up total against the budget,
   `OVER` where the total exceeds it. A budget of `0` counts as "no budget", and
   every non-zero total is over it.
4. **Walk the tree with a generator.** The report loop must be
   `for (const [cat, depth] of walk(root))` — the printing code never makes a
   recursive call (lesson 8).
5. **Summarise:** how many categories, how deep, which categories are over
   budget (names in tree order, comma-separated, or `none`), and the **leaf** with
   the biggest own spend, ties broken by first appearance.

The columns: the name is indented by `depth * 2` spaces and padded to 12
characters *including* that indentation; amounts are `$X.XX`.

Empty input prints `Categories:   0`, `Deepest:      0`, `Over budget:  none` and
`Biggest leaf: none`.
""",
        _ch("tscourse-w20-capstone", "Budget Buddy #20", "Hard",
            "Parse an indented category tree with a stack, roll the totals up, and report it "
            "through a generator.",
            _FS +
            'interface Cat {\n'
            '  readonly name: string;\n'
            '  readonly cents: number;\n'
            '  readonly budget: number;\n'
            '  readonly kids: Cat[];\n}\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'function parse(rows: readonly string[]): Cat | null {\n'
            '  let root: Cat | null = null;\n'
            '  const open: Cat[] = [];\n'
            '  for (const row of rows) {\n'
            '    const indent = row.length - row.trimStart().length;\n'
            '    const depth = Math.floor(indent / 2);\n'
            '    const parts = row.trim().split(/\\s+/);\n'
            '    if (parts.length !== 3) {\n'
            '      continue;\n    }\n'
            '    const node: Cat = {\n'
            '      name: parts[0] ?? "",\n'
            '      cents: Number(parts[1] ?? "0"),\n'
            '      budget: Number(parts[2] ?? "0"),\n'
            '      kids: [],\n    };\n'
            '    open.length = depth;\n'
            '    const parent = open[depth - 1];\n'
            '    if (parent === undefined) {\n'
            '      root = node;\n'
            '    } else {\n'
            '      parent.kids.push(node);\n    }\n'
            '    open.push(node);\n  }\n'
            '  return root;\n}\n'
            'function total(c: Cat): number {\n'
            '  let sum = c.cents;\n'
            '  for (const kid of c.kids) {\n'
            '    sum = sum + total(kid);\n  }\n'
            '  return sum;\n}\n'
            'function* walk(c: Cat, depth: number): Generator<[Cat, number]> {\n'
            '  yield [c, depth];\n'
            '  for (const kid of c.kids) {\n'
            '    yield* walk(kid, depth + 1);\n  }\n}\n'
            'function money(cents: number): string {\n'
            '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
            'const root = parse(lines);\n'
            'const over: string[] = [];\n'
            'let categories = 0;\n'
            'let deepest = 0;\n'
            'let bigLeaf = "none";\n'
            'let bigCents = -1;\n'
            'if (root !== null) {\n'
            '  for (const [cat, depth] of walk(root, 0)) {\n'
            '    categories = categories + 1;\n'
            '    deepest = Math.max(deepest, depth + 1);\n'
            '    const sum = total(cat);\n'
            '    const isOver = sum > cat.budget;\n'
            '    if (isOver) {\n'
            '      over.push(cat.name);\n    }\n'
            '    if (cat.kids.length === 0 && cat.cents > bigCents) {\n'
            '      bigLeaf = cat.name;\n      bigCents = cat.cents;\n    }\n'
            '    const label = `${"  ".repeat(depth)}${cat.name}`.padEnd(12);\n'
            '    console.log(`${label}${money(sum).padStart(8)} / ${money(cat.budget)}${isOver ? "  OVER" : ""}`);\n  }\n}\n'
            'console.log(`Categories:   ${categories}`);\n'
            'console.log(`Deepest:      ${deepest}`);\n'
            'console.log(`Over budget:  ${over.length === 0 ? "none" : over.join(", ")}`);\n'
            'console.log(bigCents < 0 ? "Biggest leaf: none" : `Biggest leaf: ${bigLeaf} ${money(bigCents)}`);\n',
            'function parse(rows: readonly string[]): Cat | null {\n'
            '  let root: Cat | null = null;\n'
            '  const open: Cat[] = [];\n'
            '  for (const row of rows) {\n'
            '    const indent = row.length - row.trimStart().length;\n'
            '    const depth = Math.floor(indent / 2);\n'
            '    const parts = row.trim().split(/\\s+/);\n'
            '    if (parts.length !== 3) {\n'
            '      continue;\n    }\n'
            '    const node: Cat = {\n'
            '      name: parts[0] ?? "",\n'
            '      cents: Number(parts[1] ?? "0"),\n'
            '      budget: Number(parts[2] ?? "0"),\n'
            '      kids: [],\n    };\n'
            '    open.length = depth;\n'
            '    const parent = open[depth - 1];\n'
            '    if (parent === undefined) {\n'
            '      root = node;\n'
            '    } else {\n'
            '      parent.kids.push(node);\n    }\n'
            '    open.push(node);\n  }\n'
            '  return root;\n}\n'
            'function total(c: Cat): number {\n'
            '  let sum = c.cents;\n'
            '  for (const kid of c.kids) {\n'
            '    sum = sum + total(kid);\n  }\n'
            '  return sum;\n}\n'
            'function* walk(c: Cat, depth: number): Generator<[Cat, number]> {\n'
            '  yield [c, depth];\n'
            '  for (const kid of c.kids) {\n'
            '    yield* walk(kid, depth + 1);\n  }\n}',
            [("all 0 0\n  food 0 1000\n    coffee 325 400\n    lunch 450 600\n  home 90000 95000",
              "all          $907.75 / $0.00  OVER\n"
              "  food         $7.75 / $10.00\n"
              "    coffee     $3.25 / $4.00\n"
              "    lunch      $4.50 / $6.00\n"
              "  home       $900.00 / $950.00\n"
              "Categories:   5\nDeepest:      3\nOver budget:  all\nBiggest leaf: home $900.00"),
             ("all 0 100000\n  food 500 400",
              "all            $5.00 / $1000.00\n"
              "  food         $5.00 / $4.00  OVER\n"
              "Categories:   2\nDeepest:      2\nOver budget:  food\nBiggest leaf: food $5.00"),
             ("solo 250 300",
              "solo           $2.50 / $3.00\n"
              "Categories:   1\nDeepest:      1\nOver budget:  none\nBiggest leaf: solo $2.50"),
             ("", "Categories:   0\nDeepest:      0\nOver budget:  none\nBiggest leaf: none")],
            hints=["`open.length = depth` trims the ancestor stack to the current level — week 18's array-clearing idiom, used as a stack of open parents.",
                   "The parent of a line at depth d is `open[depth - 1]`; when that is undefined, this line is the root.",
                   "`total` is a post-order sum: the node's own cents plus every descendant's.",
                   "`walk` yields a `[Cat, depth]` tuple, so the printing loop needs no recursion of its own.",
                   "`kids` is a mutable array here on purpose — the parser has to push into it as it goes.",
                   "The label is built as indentation + name and THEN padded to 12, so the padding absorbs the indent.",
                   "A leaf is `kids.length === 0`; a strict `>` on the comparison keeps the first of any tie."]),
        example_io="all          $907.75 / $0.00  OVER\n  food         $7.75 / $10.00\nCategories:   5\nDeepest:      3\nOver budget:  all\nBiggest leaf: home $900.00",
        rubric=["the tree is built with a stack of open ancestors, in one pass over the lines",
                "totals are rolled up post-order — each node reports its own spend plus its descendants'",
                "the report loop iterates a generator and makes no recursive call itself",
                "the generator yields the depth alongside the node, so printing needs no second walk",
                "`kids` is mutable for the parser and nothing else mutates it afterwards",
                "over-budget names come out in tree order, or `none`",
                "the biggest leaf considers own spend, not the rolled-up total, and breaks ties by first appearance",
                "empty input prints all four summary lines with zero values"],
        stretch=_ch("tscourse-w20-capstone-stretch", "Budget Buddy #20 (stretch)", "Hard",
                    "Add a path query. After the tree, a line containing only `?` is followed by "
                    "one category name per line; for each, print the path from the root as "
                    "`all/food/coffee` plus that category's rolled-up total, or `<name>: not found`. "
                    "Build the path on the way back up out of the recursion, and report how many "
                    "categories the search had to visit for the last query.",
                    _FS +
                    'interface Cat {\n'
                    '  readonly name: string;\n'
                    '  readonly cents: number;\n'
                    '  readonly kids: Cat[];\n}\n'
                    'const all = fs.readFileSync(0, "utf8").split("\\n");\n'
                    'const split = all.indexOf("?");\n'
                    'const treeRows = (split < 0 ? all : all.slice(0, split)).filter((l) => l.trim() !== "");\n'
                    'const queries = (split < 0 ? [] : all.slice(split + 1)).filter((l) => l.trim() !== "");\n'
                    'function parse(rows: readonly string[]): Cat | null {\n'
                    '  let root: Cat | null = null;\n'
                    '  const open: Cat[] = [];\n'
                    '  for (const row of rows) {\n'
                    '    const depth = Math.floor((row.length - row.trimStart().length) / 2);\n'
                    '    const parts = row.trim().split(/\\s+/);\n'
                    '    if (parts.length < 2) {\n'
                    '      continue;\n    }\n'
                    '    const node: Cat = { name: parts[0] ?? "", cents: Number(parts[1] ?? "0"), kids: [] };\n'
                    '    open.length = depth;\n'
                    '    const parent = open[depth - 1];\n'
                    '    if (parent === undefined) {\n'
                    '      root = node;\n'
                    '    } else {\n'
                    '      parent.kids.push(node);\n    }\n'
                    '    open.push(node);\n  }\n'
                    '  return root;\n}\n'
                    'function total(c: Cat): number {\n'
                    '  let sum = c.cents;\n'
                    '  for (const kid of c.kids) {\n'
                    '    sum = sum + total(kid);\n  }\n'
                    '  return sum;\n}\n'
                    'let visited = 0;\n'
                    'function pathTo(c: Cat, name: string): readonly string[] | null {\n'
                    '  visited = visited + 1;\n'
                    '  if (c.name === name) {\n'
                    '    return [c.name];\n  }\n'
                    '  for (const kid of c.kids) {\n'
                    '    const below = pathTo(kid, name);\n'
                    '    if (below !== null) {\n'
                    '      return [c.name, ...below];\n    }\n  }\n'
                    '  return null;\n}\n'
                    'function find(c: Cat, name: string): Cat | null {\n'
                    '  if (c.name === name) {\n'
                    '    return c;\n  }\n'
                    '  for (const kid of c.kids) {\n'
                    '    const hit = find(kid, name);\n'
                    '    if (hit !== null) {\n'
                    '      return hit;\n    }\n  }\n'
                    '  return null;\n}\n'
                    'const root = parse(treeRows);\n'
                    'for (const raw of queries) {\n'
                    '  const name = raw.trim();\n'
                    '  visited = 0;\n'
                    '  const path = root === null ? null : pathTo(root, name);\n'
                    '  if (path === null || root === null) {\n'
                    '    console.log(`${name}: not found`);\n'
                    '    continue;\n  }\n'
                    '  const node = find(root, name);\n'
                    '  console.log(`${path.join("/")} $${((node === null ? 0 : total(node)) / 100).toFixed(2)}`);\n}\n'
                    'console.log(`visited ${visited}`);\n',
                    'let visited = 0;\n'
                    'function pathTo(c: Cat, name: string): readonly string[] | null {\n'
                    '  visited = visited + 1;\n'
                    '  if (c.name === name) {\n'
                    '    return [c.name];\n  }\n'
                    '  for (const kid of c.kids) {\n'
                    '    const below = pathTo(kid, name);\n'
                    '    if (below !== null) {\n'
                    '      return [c.name, ...below];\n    }\n  }\n'
                    '  return null;\n}',
                    [("all 0\n  food 0\n    coffee 325\n  home 90000\n?\ncoffee\nhome\nrent",
                      "all/food/coffee $3.25\nall/home $900.00\nrent: not found\nvisited 4"),
                     ("all 100\n?\nall", "all $1.00\nvisited 1"),
                     ("all 100\n  food 200", "visited 0")],
                    hints=["Each level prepends its own name to the path the level below returned.",
                           "`return null` means 'not in this subtree', which lets the loop try the next child.",
                           "Reset the visit counter before each query, so the reported number is the last one's.",
                           "A query for a name that is not there visits every node — which is what makes the counter interesting."]),
    ),
))
