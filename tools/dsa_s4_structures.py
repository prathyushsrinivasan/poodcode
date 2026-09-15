# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Stage 4 — Linear data structures.
#
# exec()'d by tools/dsa_curriculum.py inside its namespace.
#
# Stages 1-3 used exactly one container: the array. This stage adds the four
# that change what is cheap — a stack (last in, first out), a queue/deque
# (both ends, O(1)), a linked list (O(1) splice, O(n) access) and a heap (O(1)
# minimum) — and then closes with DESIGN, the only unit in the curriculum whose
# problems have no algorithm at all. Their difficulty is entirely in choosing
# and composing the structures from the four units before it, which is why it
# sits last and is the best rehearsal for a real interview.
#
# WHY THIS STAGE TEACHES INTERNALS AND THE OTHERS DO NOT.
#
# A unit about a technique can stop at "here is the shape and here is the
# cost". A unit about a STRUCTURE cannot, because the cost is a consequence of
# a layout, and a learner who has not seen the layout is memorising the cost.
# "Heap insert is O(log n)" is trivia until you have seen the array, the
# `(i-1)/2` parent index and the sift-up loop; then it is obvious and
# un-forgettable. So every unit here carries three things the earlier stages
# do not need:
#
#   * `internals` — the layout, the operations on it, and which Java class
#     really implements it (plus the ones that look right and are not:
#     `Stack`, `LinkedList`-as-a-queue).
#   * `traces`    — the state, one row per step. Every hard thing in this stage
#     is state changing over time, which prose is bad at and a table is good
#     at: what the monotonic stack holds when an element is popped, where
#     `prev`/`cur` point after each line of a reversal, which half of the two
#     heaps an element lands in, what the LRU list looks like after each get.
#   * `build_it`  — write the structure from scratch once. It is the only
#     thing that converts a memorised cost into an understood one, and each
#     one here is deliberately small enough for a single sitting.
#
# ORDERING: stacks → queues/deques → linked lists → heaps → design. Queues
# come second because BFS in stage 5 depends on them and because the monotonic
# DEQUE is the direct sequel to the monotonic STACK — teaching them apart
# would hide that they are one idea. Design comes last because it composes all
# four.
# ---------------------------------------------------------------------------

_S4 = _stage(
    "structures", "Linear Data Structures", "🧰",
    "Pick the container whose costs match the question.",
    """
Every structure here is a deliberate trade. A stack gives up random access and
gets perfect nesting. A deque gives up the middle and gets both ends. A linked
list gives up indexing and gets O(1) insertion. A heap gives up total order and
gets the minimum for almost nothing.

The recurring exam question is therefore not "how does a heap work?" but
**"which one, and what does it cost?"** — and the design unit at the end of the
stage is that question asked five different ways.

| Structure | O(1) | O(log n) | O(n) | Java |
| --- | --- | --- | --- | --- |
| Array | index, append\\* | — | insert, search | `int[]`, `ArrayList` |
| Stack | push, pop, peek | — | search | `ArrayDeque` |
| Queue / Deque | add/remove at **either** end | — | search, index | `ArrayDeque` |
| Linked list | insert/delete at a **known** node | — | index, search | hand-rolled |
| Heap | peek min | push, pop | search, arbitrary delete | `PriorityQueue` |
| Hash map | get, put | — | (worst case only) | `HashMap` |

\\* amortised — see the stacks unit's internals for what that word is buying.

Each unit here also asks you to **build the structure once**, from scratch, on
a plain array. That is not ceremony: until you have written the sift-down loop
or the ring buffer's wrap-around, its cost is a fact you memorised rather than
one you can re-derive at a whiteboard.
""")


# --- Unit 16 — Stacks -------------------------------------------------------

_unit(
    "stacks", "Stacks & Monotonic Stacks", "🥞", _S4,
    "Last in, first out — and the trick that makes “next greater” linear.",
    prereqs=["arrays-first-pass", "strings"],
    why="""
A stack is the right structure whenever the most recent unfinished thing is the
one you need next. Bracket matching is the obvious case; the important one is
the **monotonic stack**, which answers *"for each element, what is the next
larger one to its right?"* in a single pass instead of n scans.

That pattern is worth real effort. It is the difference between O(n²) and O(n)
on a whole family of Medium and Hard problems — daily temperatures, stock
spans, histogram rectangles — and all of them are the same fifteen lines with
one comparison changed.
""",
    model="""
### The structure

Push, pop, peek — all O(1), all at one end.

```java
Deque<Integer> st = new ArrayDeque<>();
st.push(x);  st.peek();  st.pop();  st.isEmpty();
```

### Matching and nesting

A stack *is* a nesting checker. Push openers, and on a closer check that the
top is its partner:

```java
for (char c : s.toCharArray()) {
    if (isOpen(c)) st.push(c);
    else if (st.isEmpty() || !matches(st.pop(), c)) return false;
}
return st.isEmpty();      // leftovers mean unclosed brackets
```

Both failure modes matter: a closer with an empty stack, and a non-empty stack
at the end. Forgetting the second is the classic half-right solution.

### The monotonic stack

Keep the stack **sorted by construction** — here, decreasing — and store
*indices*, not values:

```java
Deque<Integer> st = new ArrayDeque<>();          // indices, values decreasing
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && a[st.peek()] < a[i]) {
        int j = st.pop();
        res[j] = i - j;         // a[i] is the next greater element for index j
    }
    st.push(i);
}
```

The insight to internalise: **when you pop something, you have just found its
answer.** An element sits on the stack precisely while its answer is still
unknown; the moment something bigger arrives, it is resolved and leaves. The
trace below is that sentence, executed.

Cost is O(n) despite the nested `while`, for the same amortised reason as the
sliding window: every index is pushed once and popped at most once.

Change the comparison and you change the question:

| Comparison in the `while` | Answers |
| --- | --- |
| `a[st.peek()] < a[i]` | next **greater** to the right |
| `a[st.peek()] > a[i]` | next **smaller** to the right |
| iterate right-to-left | the same two questions, to the **left** |

### Histogram rectangles

The hardest common application, and it is the same loop: while the stack's top
bar is taller than the current one, pop it and compute the rectangle whose
height is that bar — its width running from the new stack top up to the current
index, **exclusive at both ends**. Push a sentinel height of 0 at the end and
every remaining bar is flushed with no special-case code.
""",
    internals="""
### What is under `ArrayDeque`

A plain `Object[]` plus two indices, used as a **ring buffer**. Pushing writes
at one index and steps it; popping reads and steps back. No node is allocated,
nothing is linked, and both operations are a couple of array accesses — which
is why "O(1)" here really is a handful of instructions rather than a pointer
chase through memory.

When the array fills, it allocates one of double the size and copies. That copy
is O(n), so a single push can be expensive — but it happens only after n cheap
ones, and doubling means the total copying across n pushes is
`n/2 + n/4 + … < n`. Spread over the pushes, the cost per push is constant.
That is what **amortised O(1)** means, and it is the same argument the
monotonic stack's `while` loop uses; being able to give it in one sentence is
worth more than the code.

### The Java toolbox

| Want | Use | Not |
| --- | --- | --- |
| A stack | `ArrayDeque` (`push`/`pop`/`peek`) | `Stack` — see below |
| A stack of primitives, hot loop | `int[] st; int top = -1;` | boxing every value |
| Fixed, known capacity | a plain array + a `top` index | anything with a header |

**Never `java.util.Stack`.** It extends `Vector`, so every method is
synchronised (a lock you are not using, on every single operation), and — the
part that actually causes bugs — **it iterates bottom-to-top**, the opposite of
`ArrayDeque`. Code that prints a `Stack` gets the reverse of what the author
expected. It survives only for compatibility.

`ArrayDeque` also **rejects `null`**, because `null` is its "empty" signal from
`peek()`/`poll()`. That is a feature: it turns "I stored a null" into an
immediate `NullPointerException` at the `push` rather than a mystery later.

### The stack you did not declare

The **call stack** is this structure — one frame pushed per call, popped on
return. That is why recursion depth is a memory cost (stage 5), and why *any*
recursion can be rewritten with an explicit stack: you are just taking over the
bookkeeping the JVM was doing. When a recursive DFS overflows on 10⁵ nodes,
that rewrite is the fix.
""",
    signals=[
        _sig("“valid parentheses”, “balanced”, “nested”", "A plain stack",
             "Push openers, match on closers, require empty at the end."),
        _sig("“next greater / warmer / higher”", "Monotonic decreasing stack",
             "Pop when something bigger arrives; the popped element's answer is now known."),
        _sig("“previous smaller”, “span”", "Monotonic stack, indices",
             "Same loop; the surviving stack top is the previous smaller element."),
        _sig("“largest rectangle”, “maximum area under bars”", "Monotonic increasing stack",
             "Each popped bar is the limiting height of a rectangle."),
        _sig("“undo”, “back button”, “most recent”", "A stack (or two)",
             "Back-and-forward is one stack per direction."),
        _sig("“evaluate the expression”, “nested encoding”", "Operand stack, operator stack",
             "Nesting again — the parser's shape."),
        _sig("Recursive DFS that overflows the stack", "The same DFS with an explicit stack",
             "You take over the bookkeeping the call stack was doing."),
    ],
    skeletons=[
        _sk("Bracket matching",
            "Balanced parentheses, tag nesting, expression validity.",
            """
Deque<Character> st = new ArrayDeque<>();
for (char c : s.toCharArray()) {
    switch (c) {
        case '(': case '[': case '{': st.push(c); break;
        default:
            if (st.isEmpty() || !pairs(st.pop(), c)) return false;
    }
}
return st.isEmpty();
""",
            "Two failure modes: closer with nothing open, and openers left at the end."),
        _sk("Monotonic stack (next greater)",
            "Daily temperatures, next greater element, spans.",
            """
Deque<Integer> st = new ArrayDeque<>();     // indices; values decreasing
int[] res = new int[n];
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && a[st.peek()] < a[i]) res[st.pop()] = i;
    st.push(i);
}
// indices still on the stack have no next greater element
""",
            "Store indices — you almost always need the distance, not just the value."),
        _sk("Histogram rectangle",
            "Largest rectangle; maximal square; area under bars.",
            """
Deque<Integer> st = new ArrayDeque<>();
long best = 0;
for (int i = 0; i <= n; i++) {
    int cur = (i == n) ? 0 : h[i];                 // sentinel flushes the stack
    while (!st.isEmpty() && h[st.peek()] >= cur) {
        int height = h[st.pop()];
        int left = st.isEmpty() ? -1 : st.peek();
        best = Math.max(best, (long) height * (i - left - 1));
    }
    st.push(i);
}
""",
            "The width runs from the new stack top to the current index, exclusive both ends."),
        _sk("Recursion, de-recursed",
            "A DFS too deep for the call stack.",
            """
Deque<Integer> st = new ArrayDeque<>();
st.push(start);
while (!st.isEmpty()) {
    int u = st.pop();
    if (seen[u]) continue;
    seen[u] = true;
    for (int v : adj(u)) if (!seen[v]) st.push(v);
}
""",
            "Same traversal, same order of *discovery* reversed per node — and no stack limit."),
    ],
    traces=[
        _trace(
            "Monotonic stack on [73, 74, 72, 76]",
            "“Days until a warmer temperature.” The stack holds indices whose answer is "
            "still unknown, top first. Watch the pops: every pop writes one answer.",
            ["i", "a[i]", "Stack before (top→)", "Action", "Stack after", "Answers written"],
            [
                ["0", "73", "(empty)", "nothing smaller to resolve · push 0", "0", "—"],
                ["1", "74", "0", "74 > a[0]=73 → pop 0", "1", "res[0] = 1 − 0 = **1**"],
                ["2", "72", "1", "72 < a[1]=74 → push 2", "2, 1", "—"],
                ["3", "76", "2, 1", "76 > a[2]=72 → pop 2; 76 > a[1]=74 → pop 1", "3", "res[2] = **1**, res[1] = **2**"],
                ["end", "—", "3", "index 3 never resolved", "—", "res[3] = **0**"],
            ],
            "Four indices pushed, three popped, one left over — seven operations for n = 4. "
            "The `while` never makes it quadratic because nothing is pushed twice.",
        ),
        _trace(
            "Histogram widths on heights [2, 1, 5, 6, 2]",
            "The confusing part is never the popping — it is the width. After popping bar "
            "`j`, the rectangle of height `h[j]` extends from just after the NEW stack top "
            "to just before `i`: width = `i − left − 1`.",
            ["i", "cur", "Popped bar", "Height", "left (new top)", "Width = i − left − 1", "Area"],
            [
                ["1", "1", "index 0", "2", "−1 (empty)", "1 − (−1) − 1 = 1", "2"],
                ["4", "2", "index 3", "6", "2", "4 − 2 − 1 = 1", "6"],
                ["4", "2", "index 2", "5", "1", "4 − 1 − 1 = 2", "**10**"],
                ["5", "0 (sentinel)", "index 4", "2", "1", "5 − 1 − 1 = 3", "6"],
                ["5", "0 (sentinel)", "index 1", "1", "−1 (empty)", "5 − (−1) − 1 = 5", "5"],
            ],
            "The winner (10) is a bar of height 5 spanning two columns — a rectangle that "
            "belongs to no single bar's own width, which is exactly why the naive "
            "per-bar expansion is O(n²) and this is not.",
        ),
    ],
    costs=[
        _cost("push / pop / peek", "O(1) amortised", "—", "`ArrayDeque`; the doubling copy is the only exception."),
        _cost("Monotonic stack pass", "O(n)", "O(n)", "Each index pushed once, popped at most once."),
        _cost("Brute-force next greater", "O(n²)", "O(1)", "What the stack replaces."),
        _cost("Bracket matching", "O(n)", "O(n)", "Worst case: all openers."),
        _cost("Search for a value in a stack", "O(n)", "—", "It has no index; if you need one, it is the wrong structure."),
    ],
    pitfalls=[
        _pit("“Valid” is returned for a string with unclosed brackets",
             "The final `st.isEmpty()` check is missing.",
             "Leftovers on the stack mean unmatched openers — the answer is false."),
        _pit("`NoSuchElementException` from `pop`",
             "A closer arrived with an empty stack.",
             "Test `isEmpty()` before every pop."),
        _pit("The monotonic stack gives values but you need distances",
             "Values were pushed instead of indices.",
             "Push indices; read the value as `a[st.peek()]`."),
        _pit("The answer is missing for the last few elements",
             "Elements still on the stack at the end were never resolved.",
             "Either handle the leftovers explicitly or push a sentinel that flushes them."),
        _pit("Iterating a stack prints it upside down",
             "The legacy `Stack` extends `Vector` and iterates bottom-to-top.",
             "Use `ArrayDeque`, whose iterator runs top-to-bottom."),
        _pit("`NullPointerException` on `push`",
             "`ArrayDeque` rejects `null`, because `null` is its empty signal.",
             "Push a sentinel object or an index instead of a null."),
        _pit("Duplicate heights are counted twice in the histogram",
             "The comparison used `>` where `>=` was needed (or vice versa).",
             "Decide how ties are handled and keep the comparison consistent; with `>=` an "
             "equal bar is popped early and the later one recovers the full width."),
    ],
    lessons=["stack", "queue"],
    checks=[
        _chk("Why is a monotonic-stack pass O(n) when it contains a `while` loop?",
             "Each index is pushed exactly once and popped at most once, so the total number "
             "of inner iterations across the whole run is at most n."),
        _chk("What does it mean, semantically, when an element is popped?",
             "Its answer has just been found. Elements remain on the stack only while their "
             "next-greater (or next-smaller) element is still unknown."),
        _chk("What is `ArrayDeque` actually made of, and what does “amortised” buy?",
             "An `Object[]` ring buffer with two indices. When it fills it doubles and copies "
             "— O(n) once, after n cheap pushes, so the cost spread over all pushes is "
             "constant."),
        _chk("Why `ArrayDeque` instead of `Stack` in Java?",
             "`Stack` extends `Vector`: synchronised on every call, slower, and it iterates "
             "bottom-to-top, which is rarely what the author meant."),
        _chk("In bracket matching, what do leftovers on the stack mean?",
             "Openers that were never closed — the string is invalid, even though no "
             "mismatch was ever detected during the scan."),
        _chk("After popping bar j in the histogram, why is the width `i − left − 1` rather "
             "than `i − j`?",
             "Bar j's rectangle extends left past j, over every bar already popped because "
             "it was taller. The new stack top is the first bar too short to be included, so "
             "the span is everything strictly between it and i."),
    ],
    interview="""
The monotonic stack is one of the few patterns an interviewer will accept as a
complete answer the moment you name it — but only with the amortisation
argument attached. "Each index enters and leaves the stack once, so the pass is
O(n)" is the sentence. Without it, the nested `while` reads as O(n²) and you
will be asked to defend it anyway. The same sentence, in its other form —
"`ArrayDeque` doubles and copies, so push is amortised O(1)" — is the answer to
the follow-up about the structure itself.
""",
    build_it="""
**Write a stack on a raw array.** `int[] data; int top = -1;` with `push`, `pop`,
`peek` and `isEmpty` — twenty lines, no generics, no library.

Then make it grow: when `top + 1 == data.length`, allocate `data.length * 2` and
`System.arraycopy`. Now add a counter for elements copied, push a million values,
and print it. You will get **fewer than two million copies for a million pushes**
— under two per push, no matter how large n gets. That number is what "amortised
O(1)" means, and having produced it yourself is why you will still be able to
explain it under pressure.

Then try growth by `+1` instead of `×2` and watch the counter become ~n²/2.
""",
    rungs=[
        _rung("Core", "Nesting, then the monotonic pass.",
              ["valid-parentheses", "next-greater-element", "daily-temperatures"],
              {"valid-parentheses": "Get both failure modes right: closer-on-empty, and openers left over.",
               "next-greater-element": "The bare template. Solve it first with two nested loops so you can feel what the stack removes.",
               "daily-temperatures": "The monotonic template with distances. Push indices, not temperatures — and check your answer against the trace above."}),
        _rung("Stretch", "The same stack, with a harder thing to compute at the pop.",
              ["largest-rectangle-histogram", "longest-valid-parentheses"],
              {"largest-rectangle-histogram": "Push a sentinel 0 at the end so the flush needs no special case, and re-read the width trace before you start — `i − left − 1` is the whole problem.",
               "longest-valid-parentheses": "Push indices and keep a base index on the stack; the O(n) DP solution is worth writing afterwards for contrast, since the two answer the same question from opposite ends."}),
    ],
    next_up="""
A stack reverses the order things arrive in. The next structure preserves it —
and then, by opening its other end, does something a stack cannot.
""",
)


# --- Unit 17 — Queues and deques --------------------------------------------

_unit(
    "queues-and-deques", "Queues & Deques", "🎟️", _S4,
    "First in, first out — and the deque that answers “max of every window”.",
    prereqs=["arrays-first-pass"],
    why="""
A stack hands back the most recent item. A **queue** hands back the oldest, and
that single difference is the whole reason BFS finds shortest paths: processing
in arrival order means processing in distance order. Every graph traversal in
stage 5 runs on this structure, so the cost of getting it wrong compounds.

A **deque** — a double-ended queue — opens both ends, and unlocks the pattern
this unit exists for: the **monotonic deque**, which gives you the maximum of
every sliding window in O(n) total. It is the direct sequel to the monotonic
stack, with one addition: elements now also expire from the *front* because
they have fallen out of the window.
""",
    model="""
### One class, three roles

`ArrayDeque` is a stack, a queue and a deque depending on which methods you
call. Pick one vocabulary per use and stay in it:

| Role | Add | Remove | Inspect |
| --- | --- | --- | --- |
| **Stack** (LIFO) | `push` | `pop` | `peek` |
| **Queue** (FIFO) | `offer` / `addLast` | `poll` / `pollFirst` | `peekFirst` |
| **Deque** | `offerFirst` / `offerLast` | `pollFirst` / `pollLast` | `peekFirst` / `peekLast` |

Mixing `push` (which adds at the **front**) with `poll` (which removes from the
front) silently gives you a stack when you wanted a queue. If BFS returns a
non-shortest path, this is the first thing to check.

### The queue, in BFS

```java
Queue<Integer> q = new ArrayDeque<>();
q.offer(src);
while (!q.isEmpty()) {
    int u = q.poll();
    for (int v : adj(u)) if (!seen[v]) { seen[v] = true; q.offer(v); }
}
```

Arrival order is distance order — that is the entire justification for BFS's
shortest-path property, and it is a property of the *queue*, not of the graph.

### The monotonic deque

Keep the deque holding indices whose values are **decreasing**. Then the front
is always the maximum of the current window:

```java
Deque<Integer> dq = new ArrayDeque<>();          // indices, values decreasing
for (int i = 0; i < n; i++) {
    if (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();   // expired
    while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast(); // dominated
    dq.offerLast(i);
    if (i >= k - 1) out[i - k + 1] = a[dq.peekFirst()];
}
```

Two evictions, for two different reasons, and confusing them is the bug:

- **From the front — expiry.** That index has left the window. It is about
  *position*.
- **From the back — domination.** A new element that is larger *and* newer makes
  everything smaller behind it permanently useless: it will leave the window
  later and it is bigger now, so no future window can ever prefer them. It is
  about *value*.

That domination argument is the one to say aloud. It is why the answer is always
at the front, and why the structure never needs to look at its middle.

Still O(n): every index is added once and removed once, by exactly one of the
two rules.

### Circular buffers

A queue on a fixed array wraps around:

```java
int[] buf = new int[cap]; int head = 0, size = 0;
void offer(int x) { buf[(head + size) % cap] = x; size++; }
int  poll()       { int x = buf[head]; head = (head + 1) % cap; size--; return x; }
```

Keep an explicit `size`. The tempting alternative — two indices and "empty when
`head == tail`" — cannot distinguish empty from full, since both look identical.
The classic workarounds are a `size` field or leaving one slot permanently
unused; the field is clearer.

### A queue of timestamps

"How many events in the last five minutes" is a queue used as a **sliding
window over time**: append each event, then drop from the front while the front
is older than the cutoff. Every event is added once and dropped once, so despite
the inner `while` the whole thing is amortised O(1) per query.
""",
    internals="""
### The ring buffer

`ArrayDeque` is an `Object[]` with a `head` and a `tail` index, and it is
*circular*: when an index runs off the end it wraps to 0. That is the whole
trick, and it is why adding at the front is as cheap as adding at the back —
"the front" is just wherever `head` currently points, not physical slot 0.

Java sizes the array to a power of two so the wrap is a bit-mask,
`(i + 1) & (capacity - 1)`, rather than a `%` — division is far slower than a
mask, and this runs on every single operation. When it fills, it doubles and
copies, giving the same amortised O(1) as the stack.

### Why never `LinkedList` as a queue

`LinkedList` implements `Queue`, so it compiles and it works, and it is still
the wrong answer:

| | `ArrayDeque` | `LinkedList` |
| --- | --- | --- |
| Per element | one array slot | a **node object**: header, value, two pointers |
| Memory | ~1 reference | ~4-6× that |
| Locality | contiguous — cache-friendly | scattered — a cache miss per step |
| Allocation | one array, rarely | one object per `offer`, plus GC pressure |

Same O(1) on paper; several times slower in practice, which is exactly the case
where Big-O has to be supplemented with "and the constant matters".

### The Java toolbox

| Want | Use | Note |
| --- | --- | --- |
| FIFO queue | `ArrayDeque` via `Queue` | `offer` / `poll` / `peek` |
| Both ends | `ArrayDeque` via `Deque` | `First` / `Last` suffixes throughout |
| Fixed capacity, no allocation | `int[]` + head + size | the circular buffer above |
| Priority order, not arrival order | `PriorityQueue` | a heap — next unit; **not** FIFO |
| Blocking / cross-thread | `ArrayBlockingQueue` | outside this curriculum |

Two API traps. The `add`/`remove`/`element` family **throws** on an empty or
full queue; the `offer`/`poll`/`peek` family returns `false`/`null` instead.
Prefer the second and check the result. And `ArrayDeque` forbids `null`, for
the same reason the stack does: `null` is the "nothing there" answer from
`poll`.

`PriorityQueue` also implements `Queue`, so a misplaced import gives you a
structure that compiles as a queue and delivers in *sorted* order — a BFS that
returns wrong distances with no error anywhere.
""",
    signals=[
        _sig("“first in, first out”, “in the order they arrive”", "Queue",
             "Arrival order is the requirement, so a stack is wrong."),
        _sig("“shortest path”, “fewest steps”, unweighted", "Queue (BFS)",
             "Arrival order is distance order — the reason BFS works."),
        _sig("“maximum / minimum of every window of size k”", "Monotonic deque",
             "Front holds the answer; back evicts the dominated."),
        _sig("“last N events”, “hits in the past 5 minutes”", "Queue of timestamps",
             "Drop from the front while the front has expired."),
        _sig("“round robin”, “take a turn and go to the back”", "Queue",
             "Re-offering is the literal operation."),
        _sig("“both ends”, “add to front or back”", "Deque",
             "One structure instead of two."),
        _sig("Fixed capacity, no allocation allowed", "Circular buffer",
             "Array plus head plus size — the wrap is `% cap`."),
    ],
    skeletons=[
        _sk("FIFO queue",
            "BFS, level order, task processing.",
            """
Queue<Integer> q = new ArrayDeque<>();
q.offer(start);
while (!q.isEmpty()) {
    int u = q.poll();
    process(u);
    for (int v : next(u)) q.offer(v);
}
""",
            "`offer`/`poll` for a queue. `push` adds at the FRONT and turns it into a stack."),
        _sk("Monotonic deque (window maximum)",
            "Sliding-window max/min, and any “best in the last k”.",
            """
Deque<Integer> dq = new ArrayDeque<>();          // indices, values decreasing
for (int i = 0; i < n; i++) {
    if (!dq.isEmpty() && dq.peekFirst() <= i - k) dq.pollFirst();     // expired
    while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();  // dominated
    dq.offerLast(i);
    if (i >= k - 1) out[i - k + 1] = a[dq.peekFirst()];
}
""",
            "Front = expiry (position). Back = domination (value). Two rules, two ends."),
        _sk("Circular buffer",
            "Fixed-capacity queue with no allocation.",
            """
int[] buf = new int[cap];
int head = 0, size = 0;

void offer(int x) {
    if (size == cap) throw new IllegalStateException("full");
    buf[(head + size) % cap] = x;
    size++;
}
int poll() {
    int x = buf[head];
    head = (head + 1) % cap;
    size--;
    return x;
}
""",
            "Track `size` explicitly — `head == tail` cannot tell empty from full."),
        _sk("Queue from two stacks",
            "Amortised O(1) FIFO built out of LIFO parts.",
            """
Deque<Integer> in = new ArrayDeque<>(), out = new ArrayDeque<>();

void push(int x) { in.push(x); }
int pop() {
    if (out.isEmpty()) while (!in.isEmpty()) out.push(in.pop());   // reverses
    return out.pop();
}
""",
            "Pour only when `out` is empty. Each element crosses at most once ⇒ amortised O(1)."),
        _sk("Expiring window of events",
            "Hit counters, rate limits, “in the last N seconds”.",
            """
Deque<Integer> times = new ArrayDeque<>();

void hit(int t) { times.offerLast(t); }
int countSince(int t, int window) {
    while (!times.isEmpty() && times.peekFirst() <= t - window) times.pollFirst();
    return times.size();
}
""",
            "Each timestamp is appended once and dropped once — amortised O(1)."),
    ],
    traces=[
        _trace(
            "Monotonic deque on [1, 3, -1, -3, 5], k = 3",
            "Indices in the deque, front first; the values behind them are always "
            "decreasing. Watch which end each eviction happens at, and why.",
            ["i", "a[i]", "Expire front?", "Evict back (dominated)", "Deque after (front→)", "Window max"],
            [
                ["0", "1", "no", "—", "0 → [1]", "window not full"],
                ["1", "3", "no", "a[0]=1 ≤ 3 → drop 0", "1 → [3]", "window not full"],
                ["2", "−1", "no", "a[1]=3 > −1 → keep", "1, 2 → [3, −1]", "**3**"],
                ["3", "−3", "no (front is 1, > 3−3=0)", "a[2]=−1 > −3 → keep", "1, 2, 3 → [3, −1, −3]", "**3**"],
                ["4", "5", "no (front is 1, > 4−3=1? no → **drop 1**)", "5 dominates all → drop 3, 2", "4 → [5]", "**5**"],
            ],
            "At i = 4 both rules fire: index 1 leaves because it expired (position), then "
            "3 and 2 leave because 5 dominates them (value). Five indices in, five out — "
            "O(n), even though one step did four evictions.",
        ),
        _trace(
            "Queue from two stacks: push 1, 2, 3 then pop, pop, push 4, pop",
            "`in` takes every push; `out` is filled only when it runs dry, and the pour "
            "reverses the order — which is what turns LIFO into FIFO.",
            ["Operation", "in (top→)", "out (top→)", "Returned", "Cost"],
            [
                ["push 1, 2, 3", "3, 2, 1", "(empty)", "—", "O(1) each"],
                ["pop", "(empty)", "2, 3 → pours 1, 2, 3", "**1**", "O(n) — the pour"],
                ["pop", "(empty)", "3", "**2**", "O(1)"],
                ["push 4", "4", "3", "—", "O(1)"],
                ["pop", "4", "(empty)", "**3**", "O(1)"],
            ],
            "One pop cost O(n) and the rest cost O(1). Element 4 will cross to `out` exactly "
            "once, later — no element is ever poured twice, which is the amortisation "
            "argument in full.",
        ),
    ],
    costs=[
        _cost("offer / poll / peek, either end", "O(1) amortised", "—", "`ArrayDeque` ring buffer."),
        _cost("Monotonic deque pass", "O(n)", "O(k)", "Each index added once, removed once."),
        _cost("Sliding-window max, naive", "O(n · k)", "O(1)", "What the deque replaces."),
        _cost("Sliding-window max, heap", "O(n log k)", "O(k)", "Correct but beaten by the deque."),
        _cost("Queue from two stacks", "O(1) amortised", "O(n)", "A single pop can be O(n)."),
        _cost("Circular buffer op", "O(1) worst case", "O(cap)", "No resize, so no amortisation needed."),
        _cost("Index into a queue", "O(n)", "—", "It has no random access; that is the trade."),
    ],
    pitfalls=[
        _pit("BFS returns a path that is not shortest",
             "`push` was used instead of `offer` — `push` adds at the front, so the "
             "structure is a stack and the traversal is a DFS.",
             "Use `offer`/`poll` for a queue, and never mix the two vocabularies."),
        _pit("Distances are wrong and nothing throws",
             "The queue is actually a `PriorityQueue`, which delivers in sorted rather than "
             "arrival order — often a stray IDE import.",
             "Declare it as `Queue<…> q = new ArrayDeque<>();` and check the import."),
        _pit("The sliding-window maximum is stale",
             "The front index was never checked for having left the window.",
             "Expire from the front *before* reading the answer: `peekFirst() <= i - k`."),
        _pit("The deque grows to n instead of k",
             "The back eviction is missing, so dominated indices are kept forever.",
             "Pop from the back while `a[peekLast()] <= a[i]`."),
        _pit("`NoSuchElementException` from `remove()` on an empty queue",
             "The throwing API family was used where the returning one was meant.",
             "Prefer `poll`/`peek`, which return `null`, and test the result."),
        _pit("A circular buffer reports empty when it is full",
             "`head == tail` is true in both states and cannot tell them apart.",
             "Keep an explicit `size` field (or leave one slot unused)."),
        _pit("The queue is technically O(1) but the program is slow",
             "`LinkedList` was used, allocating a node per element and scattering them "
             "across memory.",
             "`ArrayDeque`. Same complexity, several times the speed."),
    ],
    lessons=["queue", "stack", "bfs", "sliding_window"],
    checks=[
        _chk("Why does BFS find shortest paths, in terms of the queue?",
             "A queue returns elements in arrival order, and nodes arrive in increasing "
             "order of distance — so the first time a node is reached, it has been reached "
             "by the fewest edges. The property belongs to the queue, not to the graph."),
        _chk("In the monotonic deque, the two evictions happen at different ends. Why?",
             "The front evicts by **position** — that index has fallen out of the window. "
             "The back evicts by **value** — a new element that is both larger and newer "
             "makes the smaller older ones permanently useless."),
        _chk("Justify the back eviction precisely.",
             "If `a[j] <= a[i]` and `j < i`, then j leaves the window no later than i and is "
             "no larger, so no future window can ever have j as its maximum while i is "
             "present. It can be discarded immediately."),
        _chk("Why is `ArrayDeque` preferred over `LinkedList` for a queue?",
             "Same O(1), but a ring buffer over an array: no node object per element, no "
             "allocation per `offer`, and contiguous memory instead of a cache miss per step."),
        _chk("Why can't a circular buffer detect fullness from `head` and `tail` alone?",
             "Both empty and full satisfy `head == tail`. Keep a `size` field, or deliberately "
             "waste one slot so full is `(tail + 1) % cap == head`."),
        _chk("“Queue from two stacks” — O(1) or O(n) per pop?",
             "O(n) in the worst case for a single pop, O(1) **amortised**, because each "
             "element is poured from `in` to `out` at most once in its lifetime."),
    ],
    interview="""
Two sentences carry this unit. For BFS: *"a queue returns things in arrival
order, and arrival order is distance order — that is why the first time we
reach a node is via a shortest path."* For the window maximum: *"an element
that is smaller and older than the one arriving can never be the answer again,
so I drop it from the back; the front only ever leaves because it expired."*

Interviewers also like the `ArrayDeque`-versus-`LinkedList` question precisely
because both are O(1) — it separates people who read the complexity table from
people who know what the structure is made of.
""",
    build_it="""
**Write a circular buffer.** `int[] buf`, `int head`, `int size`, with `offer`,
`poll`, `isEmpty` and `isFull`. Deliberately try the version with `head` and
`tail` and no `size` first, fill it completely, and watch `isEmpty()` return
true — the ambiguity is much more memorable once you have shipped it.

Then make it grow when full: allocate double, and **copy the elements in logical
order, not physical order** (walk `(head + i) % cap` for i in `0…size`). That
one loop is the difference between a working deque and a scrambled one, and it
is the exact code `ArrayDeque` runs when it doubles.
""",
    rungs=[
        _rung("Warm up", "Build one discipline out of the other, and meet amortisation again.",
              ["implement-queue-stacks", "implement-stack-queues"],
              {"implement-queue-stacks": "The pour reverses the order — that is the whole idea. Be ready to defend “amortised O(1)” with the trace above.",
               "implement-stack-queues": "The other direction, and deliberately worse: one operation has to be O(n) here, and it is worth working out which and why."}),
        _rung("Core", "A queue whose front expires.",
              ["design-circular-queue", "hit-counter"],
              {"design-circular-queue": "Fixed capacity and wrap-around arithmetic. Decide how you distinguish empty from full before writing a line.",
               "hit-counter": "A queue of timestamps: append on hit, drop from the front while expired. The `while` looks O(n) and is amortised O(1) — same argument, third time."}),
        _rung("Stretch", "Both ends at once.",
              ["sliding-window-maximum"],
              {"sliding-window-maximum": "The monotonic deque. Solve it with a heap first (O(n log k), and correct) so the deque's O(n) is a comparison rather than a recipe — then check yourself against the trace above."}),
    ],
    next_up="""
Arrays, stacks and deques all sit in one contiguous block, which is what makes
them fast and what fixes their shape. The next structure gives that up.
""",
)


# --- Unit 18 — Linked lists -------------------------------------------------

_unit(
    "linked-lists", "Linked Lists", "🔗", _S4,
    "Pointer surgery: reversal, fast-and-slow, and the dummy head.",
    prereqs=["two-pointers"],
    why="""
Linked lists are rare in production Java and common in interviews, for a reason
that is actually fair: they test whether you can hold a mutable pointer
structure in your head and modify it without losing half of it. There is no
library call to hide behind and no index to fall back on — only `next`.

Three techniques cover nearly every question: **reversal**, **two pointers at
different speeds**, and the **dummy head** that removes every special case about
the first node.
""",
    model="""
### The node

```java
class ListNode { int val; ListNode next; }
```

That is all. `head` is a reference to the first node; `null` is the end. There
is no length, no index, no backwards link. Anything you want to know requires
walking, and walking costs O(n).

### Reversal — the one to memorise

```java
ListNode prev = null, cur = head;
while (cur != null) {
    ListNode next = cur.next;   // 1. save what is ahead
    cur.next = prev;            // 2. flip the link
    prev = cur;                 // 3. advance prev
    cur = next;                 // 4. advance cur
}
return prev;                    // prev is the new head
```

Four lines, in that order. Saving `next` first is what stops you from losing the
rest of the list; every other ordering drops it on the floor. The trace below
shows all four pointers after each iteration.

### Fast and slow pointers

Advance one pointer by one and another by two:

- When fast reaches the end, **slow is at the middle**.
- If there is a cycle, **fast catches slow** — it gains exactly one position per
  step, so it cannot jump over.
- To find where the cycle *starts*: after they meet, reset one pointer to the
  head and advance both one step at a time. They meet at the entry. Why: if the
  tail before the cycle is `a` and they meet `b` into a cycle of length `c`,
  fast has gone twice as far, so `2(a + b) = a + b + mc`, giving `a = mc − b` —
  exactly the distance from the meeting point back round to the entry.
- To find the **k-th from the end**: advance fast by k first, then move both
  until fast hits the end.

### The dummy head

Any operation that might remove or replace the first node is full of special
cases — unless you prepend a fake node:

```java
ListNode dummy = new ListNode();
dummy.next = head;
ListNode prev = dummy;
...                                  // delete, insert, splice freely
return dummy.next;                   // the real head, possibly a new one
```

Use it every time you build or filter a list. It removes an entire class of
`if (head == null)` branches.

### Merging and splitting

Merging two sorted lists is the two-pointer merge from stage 2, with `next`
assignments instead of array writes — and a dummy head to hold the result. The
inverse, splitting a list in half, is the fast/slow midpoint. Both appear inside
reorder-list, palindrome checks and merge sort on lists.
""",
    internals="""
### What a node costs

An `int[]` of a million values is one allocation and four megabytes,
contiguous. A linked list of a million `ListNode`s is a **million separate
objects**, each carrying an object header (~12-16 bytes), the `int`, a
reference to the next node, and padding — roughly 32 bytes each, scattered
wherever the allocator put them.

The consequence is not the memory; it is the **locality**. Walking an array
reads sequential cache lines and the CPU prefetches ahead of you. Walking a
linked list is a dependent pointer chase: each node's address is unknown until
the previous one has been loaded, so the prefetcher cannot help and every step
risks a cache miss. Traversal is O(n) for both, and in practice the array is
often an order of magnitude faster.

This is why "use a linked list for fast insertion" is usually wrong advice:
`ArrayList.add(middle)` shifts memory at gigabytes per second, while
`LinkedList` must first *walk* to the position — O(n) either way, and the walk
loses.

### So when does a list actually win?

Exactly one situation, and it is worth naming precisely: you **already hold a
reference to the node**, and you want to splice it out or move it. Then it is
genuinely O(1) with no shifting and no reallocation, and no array can match it.

That is not a hypothetical — it is exactly the LRU cache in the design unit,
where a hash map hands you the node and the list reorders it in O(1). Notice
that it needs a **doubly** linked list: unlinking a node in O(1) requires its
predecessor, and a singly linked list cannot produce one without walking.

### The trick every problem here is really testing

You cannot un-follow a pointer. Every bug in this unit is a reference that was
overwritten while it was still the only way back to something. The cure is
mechanical: before any line that assigns to a `next` field, ask *"is this the
last reference to that node?"* — and if so, save it first.

### The Java toolbox

In real code: `ArrayList` for a sequence, `ArrayDeque` for a queue or stack.
`java.util.LinkedList` exists, is a doubly linked list, and is almost never the
right choice — `get(i)` walks, so a `for (int i…) list.get(i)` loop over one is
quietly O(n²). Interview linked-list problems are hand-rolled nodes precisely
because the library type hides the pointers being examined.
""",
    signals=[
        _sig("“reverse the list” / “reverse a part of it”", "The four-line reversal",
             "Save next, flip, advance, advance."),
        _sig("“middle of the list”, “second half”", "Fast and slow",
             "Fast moves two, slow moves one; one pass, no length count."),
        _sig("“does it have a cycle?”", "Floyd's tortoise and hare",
             "Fast gains one per step, so a meeting is guaranteed."),
        _sig("“where does the cycle start?”", "Meet, then reset one pointer to the head",
             "`a = mc − b` — the algebra above."),
        _sig("“k-th from the end”", "Gap of k, then advance together",
             "A single pass, no length needed."),
        _sig("“remove / insert nodes, possibly the first”", "Dummy head",
             "Removes every head-is-special branch."),
        _sig("“is it a palindrome?” (a list)", "Middle, reverse half, compare",
             "O(1) space; copying to an array is the O(n)-space alternative."),
        _sig("“reorder”, “interleave”, “split then recombine”", "Compose: middle + reverse + merge",
             "Three known pieces; the difficulty is holding them together."),
    ],
    skeletons=[
        _sk("Iterative reversal",
            "The single most reused piece of code in this unit.",
            """
ListNode prev = null, cur = head;
while (cur != null) {
    ListNode next = cur.next;
    cur.next = prev;
    prev = cur;
    cur = next;
}
return prev;
""",
            "Save `next` before you overwrite it — that is the whole trick."),
        _sk("Fast and slow",
            "Middle, cycle detection, k-th from the end.",
            """
ListNode slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) { /* cycle */ }
}
// fast == null ⇒ even length; fast.next == null ⇒ odd. slow is the middle.
""",
            "Both null checks are required, and in that order."),
        _sk("Cycle entry",
            "Not just “is there a cycle” but “where does it begin”.",
            """
// after slow == fast inside the cycle:
ListNode p = head;
while (p != slow) { p = p.next; slow = slow.next; }
return p;                       // the entry node
""",
            "Both move one step at a time now — the algebra makes them meet at the entry."),
        _sk("Dummy head",
            "Any build, filter, delete or splice.",
            """
ListNode dummy = new ListNode(), tail = dummy;
while (...) {
    tail.next = pick();
    tail = tail.next;
}
tail.next = null;
return dummy.next;
""",
            "Never special-case the first node again."),
        _sk("Merge two sorted lists",
            "The merge step, in pointer form.",
            """
ListNode dummy = new ListNode(), tail = dummy;
while (a != null && b != null) {
    if (a.val <= b.val) { tail.next = a; a = a.next; }
    else                { tail.next = b; b = b.next; }
    tail = tail.next;
}
tail.next = (a != null) ? a : b;      // attach the whole remaining tail
""",
            "The final line replaces the two drain loops an array merge needs."),
    ],
    traces=[
        _trace(
            "Reversing 1 → 2 → 3, one iteration per row",
            "The four assignments, in order, with every pointer shown after the iteration "
            "completes. `next` is the saved reference — the one that stops the list being "
            "lost.",
            ["Iteration", "next = cur.next", "cur.next = prev", "prev", "cur", "List so far"],
            [
                ["start", "—", "—", "null", "1", "1 → 2 → 3"],
                ["1", "saves 2", "1 → null", "1", "2", "1 (reversed part) · 2 → 3"],
                ["2", "saves 3", "2 → 1", "2", "3", "2 → 1 · 3"],
                ["3", "saves null", "3 → 2", "3", "null", "3 → 2 → 1 · (done)"],
                ["exit", "—", "—", "**3 = new head**", "null ⇒ loop ends", "3 → 2 → 1"],
            ],
            "Delete the first assignment and follow the table again: at iteration 1, "
            "`cur.next = prev` makes 1 point at null, and the only reference to node 2 is "
            "gone. The list becomes a single node — which is the truncation bug, exactly.",
        ),
        _trace(
            "Fast and slow on 1 → 2 → 3 → 4 → 5 → 3 (cycle back to node 3)",
            "Slow moves one, fast moves two. The gap between them inside the cycle shrinks "
            "by exactly one per step, so fast cannot jump over slow.",
            ["Step", "slow", "fast", "Note"],
            [
                ["0", "1", "1", "both at the head"],
                ["1", "2", "3", "fast enters the cycle"],
                ["2", "3", "5", "both in the cycle now"],
                ["3", "4", "4", "**they meet** — a cycle exists"],
                ["reset", "4", "1 (p, back to head)", "now both step by one"],
                ["+1", "5", "2", "still apart"],
                ["+2", "3", "3", "**meet at node 3** — the cycle entry"],
            ],
            "Without a cycle, fast would simply reach null — which is why the same loop is "
            "also the cycle *test*, not just the entry finder.",
        ),
    ],
    costs=[
        _cost("Access the k-th element", "O(k)", "O(1)", "No indexing — you must walk."),
        _cost("Insert / delete at a **known** node", "O(1)", "O(1)", "Doubly linked; the only thing lists win at."),
        _cost("Insert / delete at a known node, singly linked", "O(n)", "O(1)", "You must walk to find the predecessor."),
        _cost("Reverse", "O(n)", "O(1)", "Iteratively. Recursion costs O(n) stack."),
        _cost("Cycle detection", "O(n)", "O(1)", "Versus O(n) space with a visited set."),
        _cost("Merge two sorted lists", "O(n + m)", "O(1)", "Only pointers move."),
        _cost("Traversal, in practice", "O(n) with cache misses", "—", "Often ~10× an array scan of the same length."),
    ],
    pitfalls=[
        _pit("`NullPointerException` in a fast/slow loop",
             "`fast.next.next` evaluated when `fast.next` is already null.",
             "Guard with `while (fast != null && fast.next != null)` — both, in that order."),
        _pit("The list is truncated after a reversal",
             "`cur.next` was overwritten before `next` was saved.",
             "Save, flip, advance, advance — never reorder those four lines."),
        _pit("Deleting the head needs its own branch",
             "No dummy node, so the first node is genuinely a special case.",
             "Prepend a dummy and return `dummy.next`."),
        _pit("The program hangs",
             "A cycle was created by linking a node back into an earlier part of the list.",
             "Draw the pointers for a 3-node example before trusting the code."),
        _pit("Off by one on “k-th from the end”",
             "The gap was opened as k − 1 or k + 1 nodes.",
             "Advance fast exactly k times, then move both until fast is null."),
        _pit("The reversed half corrupts the original list",
             "A palindrome check reversed in place and never restored it.",
             "Restore the list afterwards if the caller still needs it — and say so."),
        _pit("A `LinkedList` loop is unexpectedly quadratic",
             "`for (int i…) list.get(i)` walks from the head on every call.",
             "Iterate with the iterator or a `for-each`, or use `ArrayList`."),
    ],
    lessons=["list_basics", "list_reversal", "fast_slow"],
    checks=[
        _chk("Why must `next` be saved before `cur.next = prev`?",
             "The assignment destroys the only reference to the rest of the list. Saving it "
             "first is the difference between reversing and truncating."),
        _chk("Why is a fast pointer guaranteed to catch a slow one inside a cycle?",
             "The gap between them shrinks by exactly one per step, so it cannot be jumped "
             "over — it must eventually reach zero."),
        _chk("Why does resetting one pointer to the head find the cycle's entry?",
             "With tail length a, meeting point b into a cycle of length c, fast travelled "
             "twice as far: 2(a+b) = a+b+mc, so a = mc − b — the distance from the meeting "
             "point round to the entry equals the distance from the head to it."),
        _chk("What problem does the dummy head solve?",
             "It makes the first node ordinary. Insertions and deletions at the head then "
             "need no special branch, and the real head is `dummy.next` at the end."),
        _chk("A linked list has O(1) insertion. Why is `ArrayList` still usually faster?",
             "Because O(1) applies only when you already hold the node. Reaching it costs "
             "O(n), and the walk is a dependent pointer chase that defeats the cache, while "
             "an array shift is a fast contiguous memcpy."),
        _chk("Name the one case where a linked list is genuinely the right structure.",
             "When something else already hands you the node — a hash map, say — and you "
             "need to splice or move it in O(1). That is the LRU cache, and it needs the "
             "list to be doubly linked."),
    ],
    interview="""
Linked-list questions are about care, not insight, and interviewers watch for
one specific habit: drawing the pointers. Sketch three nodes, execute your loop
on them by hand, and say which pointer is where after each line — the reversal
trace above is exactly what they want to see you produce. Candidates who do
this get the code right the first time; candidates who type from memory spend
the rest of the slot debugging.
""",
    build_it="""
**Write a doubly linked list with sentinels.** A `head` and `tail` node that
never hold data, wired to each other at construction, plus `addFirst(node)`,
`remove(node)` and `removeLast()` — each exactly two pointer assignments, with
**no null checks anywhere**, because the sentinels guarantee every real node has
both neighbours.

That is about fifteen lines, and it is literally half of the LRU cache two units
from now. Write it here, in isolation, where a bug is obvious; then the design
problem is only about keeping the map and the list agreeing.

Check yourself: remove the sentinels and count how many `if (x == null)` branches
you have to add back. Four is the usual answer.
""",
    rungs=[
        _rung("Warm up", "Walk the list; count what you see.",
              ["list-length", "list-get-nth"],
              {"list-length": "There is no `.size()`. Walking is the only way, and that is the point.",
               "list-get-nth": "O(k) access, in your hands. This is what “no random access” actually costs."}),
        _rung("Core", "The three techniques, one at a time.",
              ["reverse-linked-list", "middle-of-list", "remove-duplicates-sorted-list",
               "merge-two-sorted-lists"],
              {"reverse-linked-list": "Memorise this. Half the unit's remaining problems call it as a step — and check your pointers against the trace above.",
               "middle-of-list": "Fast and slow. Decide up front which of the two middles an even-length list should return.",
               "remove-duplicates-sorted-list": "The first splice. Note you do *not* need a dummy here — the head can never be removed — and say why.",
               "merge-two-sorted-lists": "Dummy head plus the stage-2 merge. Attach the remaining tail in one assignment rather than draining it."}),
        _rung("Variations", "Two techniques combined, or applied at a distance.",
              ["odd-even-list", "add-two-numbers-list", "remove-nth-from-end",
               "palindrome-linked-list", "has-cycle", "cycle-start-index"],
              {"odd-even-list": "Two tails built in one pass, then joined. Keep a reference to the second head before you start moving anything.",
               "add-two-numbers-list": "Digit arithmetic from stage 1 with a carry, on pointers. The carry surviving past the last node is the case people miss.",
               "remove-nth-from-end": "Gap of k, then advance together — and a dummy head, because the node removed may be the first.",
               "palindrome-linked-list": "Middle, reverse the second half, compare. Restoring the list afterwards is the detail that separates a good answer from a correct one.",
               "has-cycle": "Floyd's. The O(n)-space `HashSet` version is also worth writing, so the O(1) claim has something to beat.",
               "cycle-start-index": "After the meeting, reset one pointer to the head and step both by one. Read the algebra once; it is two lines."}),
        _rung("Stretch", "Several techniques composed under pressure.",
              ["reorder-list", "reverse-k-group"],
              {"reorder-list": "Find the middle, reverse the second half, then interleave. Three known pieces — the difficulty is holding them together without losing a tail.",
               "reverse-k-group": "Reversal with a boundary check in front of it. Do it iteratively with a dummy head, and decide what happens to a final group of fewer than k *before* coding."}),
    ],
    next_up="""
Stacks, queues and lists all order by *arrival*. The next structure orders by
**value** — and that is what makes “the k largest” cheap.
""",
)


# --- Unit 19 — Heaps --------------------------------------------------------

_unit(
    "heaps", "Heaps & Priority Queues", "⛰️", _S4,
    "The smallest element, always, for O(log n) a move.",
    prereqs=["sorting", "complexity"],
    why="""
Sorting gives you every element in order, which is more than most problems need
and costs O(n log n) to produce. A heap gives you only the extreme one — but
gives it continuously, as elements arrive and leave, for O(log n) per change.

That is exactly the right trade for three enormous families: **top-k** (keep a
heap of size k and the answer stays inside it), **streaming** (data arrives and
you must answer at any moment), and **greedy scheduling** (repeatedly take the
best available option). It is also the engine inside Dijkstra's algorithm two
units from now.
""",
    model="""
### What a heap is and is not

A binary heap is a complete tree stored in an array, where every parent is ≤ its
children. That gives O(1) access to the minimum and O(log n) insert and remove.
It gives you **nothing else**: the rest of the heap is not sorted, searching for
an arbitrary element is O(n), and iterating a `PriorityQueue` does *not* produce
sorted order. Only `poll()` does.

```java
PriorityQueue<Integer> min = new PriorityQueue<>();                       // min-heap
PriorityQueue<Integer> max = new PriorityQueue<>(Comparator.reverseOrder());
min.offer(x);  min.peek();  min.poll();
```

Java's `PriorityQueue` is a **min-heap by default**. Half of all heap bugs are
that sentence being forgotten.

### Top-k: the counter-intuitive part

To keep the **k largest**, use a **min**-heap of size k. The smallest of your
current best k sits on top, so the moment something bigger arrives you evict it
in O(log k):

```java
PriorityQueue<Integer> pq = new PriorityQueue<>();   // min-heap
for (int x : a) {
    pq.offer(x);
    if (pq.size() > k) pq.poll();       // drop the smallest of the k+1
}
// pq now holds the k largest; pq.peek() is the k-th largest
```

O(n log k) time, O(k) space — better than sorting when k ≪ n, and it works on a
stream that does not fit in memory.

### Two heaps: the running median

A max-heap of the lower half and a min-heap of the upper half, kept balanced so
their sizes differ by at most one. The median is then a peek (or the average of
two peeks). Insert, rebalance, answer — all O(log n). The trace below is the
rebalancing, which is the only part that is fiddly.

### Heap + greedy

"Repeatedly take the largest, do something, put the result back" is a heap loop:
stone smashing, task scheduling by remaining count, connecting ropes by cost.
The pattern is: while more than one element remains, poll the extremes, combine,
offer the result.

### Merging k sorted sequences

Put the head of each sequence in a heap. Poll the smallest, output it, and push
that sequence's next element. O(N log k) for N items across k sequences.

### Lazy deletion

Heaps cannot remove an arbitrary element cheaply. The standard workaround is to
leave stale entries in and skip them on the way out — check on `poll()` whether
the entry is still valid, and if not, discard and poll again. That is how
Dijkstra avoids needing a decrease-key operation.
""",
    internals="""
### It is an array, not a tree of objects

A heap is a **complete** binary tree — every level full except possibly the
last, which fills left to right — and that completeness means it can be stored
in a flat array with no pointers at all. The tree structure is pure arithmetic:

```
parent(i) = (i - 1) / 2
left(i)   = 2 * i + 1
right(i)  = 2 * i + 2
```

So `a[0]` is the root (the minimum), and no node object, no `left`/`right`
field and no allocation exists anywhere. That is why a heap is fast in a way the
same tree built from linked nodes would not be: it is one contiguous block, and
a parent-to-child step is a multiply.

### The two operations everything is built from

**Sift up** (after inserting at the end): while the new element is smaller than
its parent, swap with the parent. It rises at most the height of the tree.

```java
void siftUp(int i) {
    while (i > 0 && a[i] < a[(i - 1) / 2]) {
        swap(i, (i - 1) / 2);
        i = (i - 1) / 2;
    }
}
```

**Sift down** (after removing the root): move the *last* element to the root,
then repeatedly swap it with its **smaller** child until both children are
larger.

```java
void siftDown(int i) {
    while (2 * i + 1 < size) {
        int c = 2 * i + 1;
        if (c + 1 < size && a[c + 1] < a[c]) c++;    // the smaller child
        if (a[i] <= a[c]) break;
        swap(i, c); i = c;
    }
}
```

Swapping with the *larger* child instead is the classic bug: it puts a value
above something smaller and silently breaks the invariant. There is no crash —
just wrong answers later.

A complete tree of n nodes has height ⌊log₂ n⌋, so both loops are O(log n).
That is where the complexity comes from; it is not a fact to memorise once you
have seen the array.

### Why building a heap is O(n), not O(n log n)

`new PriorityQueue<>(collection)` heapifies in **linear** time, which surprises
people. Sift-down from the bottom up: half the nodes are leaves and sift down
zero levels, a quarter sift down at most one, an eighth at most two. The sum
`Σ n/2^(h+1) · h` converges to n. Inserting one at a time really is O(n log n) —
so when you have all the data up front, hand it to the constructor.

### The Java toolbox

| Want | Use |
| --- | --- |
| Min-heap | `new PriorityQueue<>()` |
| Max-heap | `new PriorityQueue<>(Comparator.reverseOrder())` |
| By a computed key | `new PriorityQueue<>(Comparator.comparingInt(f))` |
| Bulk build from a collection | `new PriorityQueue<>(list)` — O(n) |
| Heap of primitives, hot path | hand-rolled `int[]` — no boxing |

`PriorityQueue` implements `Queue`, so it can be passed anywhere a queue is
expected — including, accidentally, into a BFS, where it silently produces
sorted rather than arrival order. Its `remove(Object)` is O(n) because it must
search the array; `iterator()` returns heap order, which is not sorted order.
""",
    signals=[
        _sig("“k largest / smallest / closest / most frequent”", "Size-k heap of the opposite kind",
             "Min-heap for k largest; max-heap for k smallest."),
        _sig("“median of a stream”", "Two heaps, balanced",
             "Max-heap below, min-heap above."),
        _sig("“repeatedly take the largest and …”", "Max-heap loop",
             "Poll, combine, offer back."),
        _sig("“merge k sorted lists / arrays”", "Heap of the k current heads",
             "O(N log k), not O(N log N)."),
        _sig("“schedule tasks with cooldown”", "Max-heap by remaining count",
             "Always do the most urgent thing that is legal."),
        _sig("“the smallest thing next, and the set keeps changing”", "Heap",
             "This is Dijkstra's inner loop, and Prim's."),
        _sig("You need the whole order, not just the extreme", "Sort instead",
             "A heap gives one end; paying O(n log n) once may be simpler."),
    ],
    skeletons=[
        _sk("Top-k with a size-k heap",
            "k largest, k closest, k most frequent.",
            """
PriorityQueue<Integer> pq = new PriorityQueue<>();   // MIN-heap for k LARGEST
for (int x : a) {
    pq.offer(x);
    if (pq.size() > k) pq.poll();
}
int kthLargest = pq.peek();
""",
            "The heap's top is the weakest survivor — that is what makes eviction O(log k)."),
        _sk("Custom-ordered heap",
            "Ordering by a computed key, or over objects.",
            """
PriorityQueue<int[]> pq = new PriorityQueue<>(
        (p, q) -> Integer.compare(p[1], q[1]));     // by the second field
PriorityQueue<String> byFreq = new PriorityQueue<>(
        Comparator.<String>comparingInt(freq::get).thenComparing(Comparator.reverseOrder()));
""",
            "Same comparator rules as sorting — never subtract unbounded values."),
        _sk("Two heaps for a median",
            "Any streaming order statistic in the middle.",
            """
PriorityQueue<Integer> lo = new PriorityQueue<>(Comparator.reverseOrder());  // max
PriorityQueue<Integer> hi = new PriorityQueue<>();                           // min

lo.offer(x);
hi.offer(lo.poll());                       // pass the largest of the low half up
if (hi.size() > lo.size()) lo.offer(hi.poll());   // keep lo ≥ hi in size
double median = (lo.size() > hi.size()) ? lo.peek() : (lo.peek() + hi.peek()) / 2.0;
""",
            "Always push through the other heap; it keeps the halves correctly partitioned."),
        _sk("Merge k sorted sequences",
            "k lists, k arrays, k streams.",
            """
PriorityQueue<int[]> pq = new PriorityQueue<>((p, q) -> Integer.compare(p[0], q[0]));
for (int i = 0; i < k; i++)
    if (lists[i].length > 0) pq.offer(new int[]{ lists[i][0], i, 0 });

while (!pq.isEmpty()) {
    int[] cur = pq.poll();                 // {value, which list, index in it}
    out.add(cur[0]);
    if (cur[2] + 1 < lists[cur[1]].length)
        pq.offer(new int[]{ lists[cur[1]][cur[2] + 1], cur[1], cur[2] + 1 });
}
""",
            "The heap never holds more than k entries."),
        _sk("Lazy deletion",
            "When an entry's priority changes — Dijkstra, schedulers.",
            """
while (!pq.isEmpty()) {
    int[] top = pq.poll();
    if (top[0] > best[top[1]]) continue;      // stale: a better entry superseded it
    ...
}
""",
            "Push the improved copy and skip the outdated one on the way out."),
    ],
    traces=[
        _trace(
            "Sift-up: inserting 2 into the min-heap [1, 5, 6, 9, 7]",
            "The new value goes at the end, then rises while it is smaller than its parent. "
            "Indices, not values, drive the walk: `parent(i) = (i − 1) / 2`.",
            ["Step", "Array", "i", "parent(i)", "Compare", "Action"],
            [
                ["append", "1, 5, 6, 9, 7, **2**", "5", "(5−1)/2 = 2", "2 < 6", "swap"],
                ["after 1 swap", "1, 5, **2**, 9, 7, 6", "2", "(2−1)/2 = 0", "2 > 1", "stop"],
                ["final", "**1, 5, 2, 9, 7, 6**", "—", "—", "parent ≤ child everywhere", "done"],
            ],
            "Two comparisons for six elements. The array is not sorted at the end — and it "
            "does not need to be. Only `a[0]` is guaranteed, and that is the entire contract.",
        ),
        _trace(
            "Two heaps: the running median of 5, 15, 1, 3",
            "Every value enters `lo` first, then its maximum is passed up to `hi`, then the "
            "sizes are rebalanced. The invariant: everything in `lo` ≤ everything in `hi`, "
            "and `lo.size()` is equal to or one more than `hi.size()`.",
            ["Insert", "lo (max-heap)", "hi (min-heap)", "Rebalance", "Median"],
            [
                ["5", "[5]", "[]", "hi took 5, lo empty → pull back", "**5**"],
                ["15", "[5]", "[15]", "sizes 1 and 1 — fine", "(5+15)/2 = **10**"],
                ["1", "[5, 1]", "[15]", "lo 2, hi 1 — fine", "**5**"],
                ["3", "[3, 1]", "[5, 15]", "hi grew to 2 → pull 5 back into lo", "(3+5)/2 = **4**"],
            ],
            "Note the last row: 3 entered `lo`, but pushing through `hi` moved 5 across, "
            "which is what keeps the halves correctly split. Inserting straight into "
            "whichever heap “looks right” is the bug this ritual prevents.",
        ),
    ],
    costs=[
        _cost("peek", "O(1)", "—", "The extreme element only."),
        _cost("offer / poll", "O(log n)", "—", "Sift up / sift down — the tree's height."),
        _cost("Build a heap from n elements", "O(n)", "O(n)",
              "`new PriorityQueue<>(collection)`; inserting one by one is O(n log n)."),
        _cost("Top-k over n elements", "O(n log k)", "O(k)", "Beats sorting when k ≪ n."),
        _cost("Merge k sequences of N items", "O(N log k)", "O(k)", "Versus O(N log N) if concatenated and sorted."),
        _cost("Search / remove an arbitrary element", "O(n)", "—", "Use lazy deletion instead."),
        _cost("Heapsort (poll everything)", "O(n log n)", "O(1)", "In-place, but slower in practice than quicksort."),
    ],
    pitfalls=[
        _pit("The k largest come out as the k smallest",
             "Java's `PriorityQueue` is a min-heap by default.",
             "For a max-heap pass `Comparator.reverseOrder()` — and remember top-k uses the "
             "*opposite* heap to the one you expect."),
        _pit("Iterating the queue gives unsorted output",
             "Only `poll()` respects the ordering; the backing array is heap order.",
             "Poll repeatedly, or copy and sort if you need the whole order."),
        _pit("The comparator overflows",
             "`(a, b) -> a[0] - b[0]` with large values.",
             "`Integer.compare(a[0], b[0])`."),
        _pit("Removing an updated element is O(n)",
             "`pq.remove(x)` searches linearly.",
             "Leave the stale entry in and skip it when polled — lazy deletion."),
        _pit("Two-heap median drifts out of balance",
             "An element was pushed to a half directly instead of through the other heap.",
             "Always offer into one, poll it into the other, then rebalance the sizes."),
        _pit("The heap grows to n when only k are needed",
             "The `if (pq.size() > k) pq.poll();` step is missing.",
             "Evict on every insert; the memory bound is the point of the pattern."),
        _pit("A hand-rolled heap returns wrong values with no crash",
             "Sift-down swapped with the larger child rather than the smaller one.",
             "Pick the smaller child first, then compare; the invariant breaks silently "
             "otherwise."),
        _pit("Building the heap dominates the runtime",
             "n separate `offer` calls where the data was available up front.",
             "Pass the collection to the constructor — that path is O(n)."),
    ],
    lessons=["heap", "top_k", "two_heaps", "heap_greedy"],
    checks=[
        _chk("To keep the k *largest* elements, which kind of heap, and why?",
             "A **min**-heap of size k. Its top is the smallest of the current best k, so it "
             "is exactly the element to evict when a bigger one arrives."),
        _chk("Where are a heap node's children, and why does that matter?",
             "At `2i + 1` and `2i + 2` in a flat array — the tree is implied by arithmetic, "
             "so a heap needs no node objects and no pointers, and lives in one contiguous "
             "block."),
        _chk("Why are insert and remove O(log n)?",
             "Both walk one root-to-leaf path of a complete tree, whose height is ⌊log₂ n⌋. "
             "Sift-up on insert, sift-down on remove."),
        _chk("Why is building a heap from n elements O(n) rather than O(n log n)?",
             "Sifting down from the bottom up, half the nodes move zero levels, a quarter at "
             "most one, an eighth at most two; the series Σ n·h/2^(h+1) converges to n. "
             "Inserting one at a time really is O(n log n)."),
        _chk("Does iterating a `PriorityQueue` yield sorted order?",
             "No. Only the head is guaranteed. Sorted output requires polling until empty."),
        _chk("How do you delete an arbitrary element from a heap?",
             "You usually do not. Mark it stale and discard it when it surfaces at `poll` — "
             "lazy deletion, the same trick Dijkstra uses instead of decrease-key."),
        _chk("What keeps the two-heap median correct?",
             "Every element enters through the opposite heap before rebalancing, which "
             "guarantees every value in the low half is ≤ every value in the high half."),
    ],
    interview="""
Heaps are the standard answer to "k largest" and the standard *follow-up* to a
sorting solution, so the cleanest thing you can do is offer both and price them:
"sorting is O(n log n); a size-k min-heap is O(n log k) and streams". Then be
ready for the third step — quickselect at O(n) average — and for why you might
still not choose it (worst-case O(n²), and it needs the whole array in memory).

If asked how a heap works, answer with the array, not with a picture of a tree:
`2i+1`, `2i+2`, sift up, sift down, height log n. That answer also gets you the
O(n) build-heap question for free, which is a common follow-up precisely because
most candidates assume it is O(n log n).
""",
    build_it="""
**Write a binary min-heap on an `int[]`.** `siftUp`, `siftDown`, `offer`, `poll`,
`peek` — about forty lines, and the only tricky one is choosing the *smaller*
child in `siftDown`.

Then prove it to yourself two ways. Push a thousand random values, poll them all,
and check the output is sorted — that is heapsort, and it is the strongest test
there is. Then deliberately swap with the larger child in `siftDown` and watch
the output come out *almost* sorted: no exception, no crash, just wrong. That
silence is why the invariant has to be maintained by construction rather than
checked.

Finally, use it for top-k over a million values with k = 10 and confirm the array
never grows past 10.
""",
    rungs=[
        _rung("Warm up", "A heap used as “give me the extreme, repeatedly”.",
              ["kth-largest-in-stream", "last-stone-weight"],
              {"kth-largest-in-stream": "The size-k min-heap, stated as plainly as it ever gets.",
               "last-stone-weight": "A max-heap greedy loop: poll two, combine, offer the remainder back."}),
        _rung("Core", "Top-k in its three most common disguises.",
              ["kth-largest-in-array", "k-closest-distances", "top-k-frequent-words"],
              {"kth-largest-in-array": "You solved this by sorting in the sorting unit. Redo it in O(n log k) and compare — then look up quickselect for the O(n) third answer.",
               "k-closest-distances": "The key you order by is not the value itself. Put the computation in the comparator, not in the data.",
               "top-k-frequent-words": "Count first, then heap by (frequency, word) — the tie-break lives in the comparator, and getting its direction right is the exercise."}),
        _rung("Variations", "Heap as the engine of a greedy loop.",
              ["task-scheduler", "ugly-number-ii", "reorganize-string"],
              {"task-scheduler": "Always schedule the most-remaining task that is legal right now. The heap makes “most remaining” free.",
               "ugly-number-ii": "A heap generating values in order, with a set to suppress duplicates. The three-pointer O(n) solution afterwards is a good lesson in when a heap is *not* needed.",
               "reorganize-string": "Greedy by remaining count, holding the previous character back for one round so it cannot repeat."}),
        _rung("Stretch", "Several heaps, or a heap over sequences.",
              ["merge-k-sorted", "median-from-stream", "smallest-range-k-lists"],
              {"merge-k-sorted": "O(N log k). Holding only the k heads is what keeps the memory bounded — say that number out loud before coding.",
               "median-from-stream": "The two-heap pattern. Getting the rebalance right is the whole problem; the trace above is the version to copy.",
               "smallest-range-k-lists": "Merge-k plus a running maximum — the range is between the heap's minimum and the largest value pushed so far."}),
    ],
    next_up="""
You now have six containers. The last unit of the stage asks the question an
interviewer really wants answered: can you *combine* them?
""",
)


# --- Unit 20 — Design -------------------------------------------------------

_unit(
    "design", "Data Structure Design", "🏗️", _S4,
    "No algorithm — just the right combination, at the right cost.",
    prereqs=["hashing", "linked-lists"],
    why="""
Design problems give you an interface and a performance target: *"implement
`get` and `put`, both in O(1)"*. There is no clever insight to find. The work is
choosing structures whose costs add up to the target, and keeping them
consistent with one another as the data changes.

This is the closest thing in the problem bank to real engineering, and it is why
these questions are so common in interviews — they test whether you know what
your tools cost, not whether you have seen a trick.
""",
    model="""
### The method

1. **Write the operations and their required costs.** That table is the spec.
2. **For each operation, name a structure that achieves it alone.** O(1) lookup
   by key → hash map. Ordered by value → heap or tree. O(1) insert/remove at a
   known position → doubly linked list.
3. **Combine them, and decide what each one stores.** Usually one structure owns
   the data and the others hold *references into it*.
4. **Check every operation again** against the combined design — the failure is
   almost always an operation that now has to update two structures and only
   updates one.

### The canonical combination

**Hash map + doubly linked list** gives O(1) lookup *and* O(1) reordering, which
is exactly what an LRU cache needs:

- the list holds entries in recency order, most-recent at the head;
- the map holds `key → node`, so any node can be found instantly;
- a doubly linked list is required because unlinking a node in O(1) needs its
  *predecessor*, which a singly linked list cannot give you.

`get` moves a node to the front; `put` inserts at the front and, if over
capacity, drops the tail. Every step is O(1), and the tail is the least recently
used item by construction. The trace below is a capacity-2 cache, operation by
operation.

LFU is the same idea one level up: map by key, plus buckets keyed by frequency,
plus a pointer to the minimum frequency.

### Carrying an auxiliary invariant

Min-stack keeps a second stack of "minimum at or below this depth", pushed in
lockstep with the main one. Popping drops both, so the minimum is always on top:
an extra O(n) memory buys an O(1) query. That "store the answer alongside the
data" move is the most transferable idea in the unit — the same trick turns
`stock-spanner` into the monotonic stack you already know, wrapped in a class
and fed one value at a time.

### Time-ordered data

When entries are appended with non-decreasing timestamps, the list per key is
already sorted — so *"the value at time t"* is a binary search, and no extra
ordering structure is needed. Recognising that the data arrives sorted is the
insight; the rest is the stage-3 template.

### Two rules that prevent most of the bugs

**One owner.** Exactly one structure holds the real data; the others hold keys
or references into it. Two structures that both think they own an entry will
eventually disagree.

**Every mutation touches every structure.** Write the list down — "an eviction
must: unlink the node, remove the map key, decrement the size" — and check each
operation against it. Design bugs are almost never wrong algorithms; they are a
missing line in one of three places.
""",
    internals="""
### Why sentinels, always

Splice code without sentinel nodes is a thicket of null checks: removing the
head is special, removing the tail is special, removing the only node is
special. With a permanent `head` and `tail` that never hold data, **every real
node is guaranteed to have both a predecessor and a successor**, and `remove`
becomes two unconditional assignments:

```java
n.prev.next = n.next;
n.next.prev = n.prev;
```

No branches, no null checks, no special cases. This is the same idea as the
dummy head from the linked-list unit, applied at both ends — and it is worth
building the habit, because the LRU cache is where a missed null check is
hardest to debug.

### What "O(1) amortised" means to an interviewer

Three different structures in this stage claim O(1) for slightly different
reasons, and being able to separate them is a real signal:

| Claim | Kind | Why |
| --- | --- | --- |
| `ArrayDeque.push` | amortised | doubling spreads the copy over n pushes |
| `HashMap.get` | average case | good hash distribution; O(n) if everything collides |
| LRU `get`/`put` | genuinely worst-case | a fixed number of pointer writes, no resize, no search |

The LRU cache is the strongest of the three, and saying so — "this is worst-case
O(1), not amortised" — is the kind of precision that ends the follow-up
questions.

### Hash maps, the part that matters here

A `HashMap` is an array of buckets; a key's hash picks the bucket, and
collisions chain within it (Java converts a long chain to a balanced tree, so
the pathological case is O(log n) rather than O(n)). Load factor 0.75 triggers a
resize and a full rehash — O(n), amortised away like the deque's doubling.

The consequence for design problems: `HashMap` gives you **O(1) lookup by key
and nothing else**. No order, no minimum, no range. Every structure you bolt
onto it in this unit exists to supply exactly one of those missing properties.
""",
    signals=[
        _sig("“O(1) get and put with eviction”", "Hash map + doubly linked list",
             "The map finds the node; the list orders it."),
        _sig("“get the minimum in O(1)” alongside push/pop", "A parallel stack of minima",
             "Store the answer next to the data."),
        _sig("“implement X using only Y”", "Two of Y, and an amortised argument",
             "Pouring between two stacks reverses the order."),
        _sig("“value at a given timestamp”", "Map to a sorted list + binary search",
             "Appends arrive in time order, so the list is already sorted."),
        _sig("“most recent k”, “feed”, “top posts”", "Heap over per-user lists",
             "Merge-k, restricted to k results."),
        _sig("“span”, “consecutive smaller before this one”", "A monotonic stack in a class",
             "The stacks unit's pattern, fed one value at a time."),
        _sig("Two operations want two different orders", "Two structures, one owner",
             "One holds the data; the other holds references into it."),
    ],
    skeletons=[
        _sk("Hash map + doubly linked list (LRU)",
            "Any cache with O(1) access and eviction by recency.",
            """
class Node { int key, val; Node prev, next; }
Map<Integer, Node> map = new HashMap<>();
Node head = new Node(), tail = new Node();      // sentinels
{ head.next = tail; tail.prev = head; }

void remove(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
void addFirst(Node n) {
    n.next = head.next; n.prev = head;
    head.next.prev = n; head.next = n;
}
// get: remove(n); addFirst(n);
// put over capacity: Node lru = tail.prev; remove(lru); map.remove(lru.key);
""",
            "Sentinel head and tail nodes remove every null check from the splice code."),
        _sk("Parallel minimum stack",
            "Min-stack, max-stack, any “extreme so far” query.",
            """
Deque<Integer> st = new ArrayDeque<>(), mins = new ArrayDeque<>();

void push(int x) {
    st.push(x);
    mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
}
void pop() { st.pop(); mins.pop(); }
int getMin() { return mins.peek(); }
""",
            "Push to both, pop from both — the invariant maintains itself."),
        _sk("Time-keyed store",
            "Versioned values, “state at time t”.",
            """
Map<String, List<int[]>> store = new HashMap<>();   // key → [(time, value)…]

void set(String k, int v, int t) {
    store.computeIfAbsent(k, x -> new ArrayList<>()).add(new int[]{ t, v });
}
// get: binary-search the list for the LAST entry with time <= t
""",
            "Appends come in increasing time order, so the list is sorted for free."),
        _sk("A pattern, wrapped in a class",
            "Stock spanner, streaming versions of an offline algorithm.",
            """
Deque<int[]> st = new ArrayDeque<>();        // {price, span}, prices decreasing

int next(int price) {
    int span = 1;
    while (!st.isEmpty() && st.peek()[0] <= price) span += st.pop()[1];
    st.push(new int[]{ price, span });
    return span;
}
""",
            "The monotonic stack, fed one element at a time — popped spans are absorbed."),
    ],
    traces=[
        _trace(
            "LRU cache, capacity 2: put(1,A), put(2,B), get(1), put(3,C)",
            "The list is recency order, most-recent first. Watch the last row: 2 is evicted "
            "because `get(1)` moved 1 to the front, which is the entire behaviour being "
            "tested.",
            ["Operation", "List (front → back)", "Map keys", "Returned", "Evicted"],
            [
                ["put(1, A)", "1", "{1}", "—", "—"],
                ["put(2, B)", "2, 1", "{1, 2}", "—", "—"],
                ["get(1)", "1, 2", "{1, 2}", "**A**", "— (1 moved to the front)"],
                ["put(3, C)", "3, 1", "{1, 3}", "—", "**2** — now the tail"],
                ["get(2)", "3, 1", "{1, 3}", "**−1**", "— (already evicted)"],
            ],
            "Two structures changed on every row and had to agree on every row. The eviction "
            "step is where they usually stop agreeing: unlinking the tail node without also "
            "removing its map key leaves a key pointing at a node no longer in the list.",
        ),
        _trace(
            "Min-stack: push 5, push 2, push 7, pop, getMin",
            "The two stacks move in lockstep, so `mins.peek()` is always the minimum of "
            "exactly the elements currently in `st`.",
            ["Operation", "st (top →)", "mins (top →)", "getMin"],
            [
                ["push 5", "5", "5", "5"],
                ["push 2", "2, 5", "2, 5", "2"],
                ["push 7", "7, 2, 5", "**2**, 2, 5", "2 — 7 pushes min(7, 2) = 2"],
                ["pop", "2, 5", "2, 5", "2"],
                ["pop", "5", "5", "**5** — restored automatically"],
            ],
            "The third row is the one to understand: `mins` stores a *duplicate* 2 rather "
            "than skipping the push. That is what makes `pop` a plain pop from both stacks "
            "instead of a conditional — and conditionals are where this problem goes wrong.",
        ),
    ],
    costs=[
        _cost("Hash map + linked list (LRU)", "O(1) worst case", "O(capacity)", "No search, no resize on the hot path."),
        _cost("Min-stack", "O(1) all operations", "O(n)", "Extra stack of minima."),
        _cost("Time-keyed get", "O(log n)", "O(n)", "Binary search over the key's history."),
        _cost("Feed of k most recent over u sources", "O(u log u + k log u)", "O(u)", "Merge-k, truncated at k."),
        _cost("LFU cache", "O(1) get/put", "O(capacity)", "Frequency buckets plus a minimum-frequency pointer."),
        _cost("Stock spanner", "O(1) amortised", "O(n)", "Each price pushed once, popped once."),
    ],
    pitfalls=[
        _pit("The cache returns stale or missing entries",
             "One structure was updated and the other was not — usually an eviction that "
             "unlinked the node but left the map key.",
             "Write the mutation checklist down: every change must touch *every* structure "
             "that references the entry."),
        _pit("Unlinking a node is O(n)",
             "A singly linked list cannot reach a node's predecessor.",
             "Use a doubly linked list; that requirement is the reason for the design."),
        _pit("Null-pointer errors all over the splice code",
             "Head and tail are real nodes, so every operation special-cases the ends.",
             "Use sentinel head and tail nodes that never hold data."),
        _pit("`put` on an existing key inserts a duplicate",
             "The update path assumed the key was new.",
             "On `put`, check for the key first: update the value and move the node, rather "
             "than inserting a second one."),
        _pit("Min-stack's `pop` corrupts the minimum",
             "`mins` was only pushed when a new minimum appeared, so the two stacks no "
             "longer align.",
             "Push to `mins` on every push, duplicating the current minimum when necessary."),
        _pit("The heap-based feed is rebuilt on every query",
             "All posts are re-merged instead of only the k most recent per source.",
             "Bound the work by k: only the head of each source can be next."),
        _pit("Binary search returns the wrong version",
             "An upper-bound search was needed but a lower-bound one was written.",
             "You want the last entry with `time <= t` — `upperBound(t) - 1`."),
    ],
    lessons=["design_ds", "stack", "queue", "hashing"],
    checks=[
        _chk("Why must an LRU cache use a *doubly* linked list?",
             "Eviction and reordering unlink a node in O(1), which requires its predecessor. "
             "A singly linked list would need an O(n) scan to find it."),
        _chk("Is an LRU cache's `get` amortised O(1) or worst-case O(1)?",
             "Worst case. It is a fixed number of pointer writes plus a hash lookup — no "
             "resize, no search, no doubling. That distinguishes it from `ArrayDeque.push`, "
             "which is amortised."),
        _chk("Why does min-stack push a duplicate minimum instead of skipping the push?",
             "So the two stacks stay the same height and `pop` can be unconditional. Pushing "
             "only on a new minimum means `pop` must decide whether to pop `mins` too, which "
             "is exactly where the bug appears."),
        _chk("What do sentinel nodes buy you?",
             "Every real node has both neighbours, so `remove` and `addFirst` are "
             "unconditional two-line assignments with no null checks and no special cases "
             "for the first or last element."),
        _chk("What is the method when a design problem gives you cost targets?",
             "List the operations with their required costs, pick a structure that achieves "
             "each one alone, combine them with one owning the data, then re-check every "
             "operation against the combination."),
        _chk("A `HashMap` gives O(1) lookup. What does it *not* give you, and how is that "
             "usually fixed?",
             "No ordering, no minimum, no range queries. Each is supplied by bolting on a "
             "second structure that holds references into the map's data — a list for "
             "recency, a heap for extremes, a sorted list for time."),
    ],
    interview="""
Design questions are where the interview stops being a quiz. Talk through the
operation/cost table out loud before writing anything — it is the reasoning
being assessed, and it is also how you catch the impossible requirement early.
Three sentences worth having ready: *"a hash map gives me O(1) lookup and a
doubly linked list gives me O(1) reordering, so together they give me both"*,
*"that is amortised O(1), because each element moves at most once"*, and — for
the LRU itself — *"this one is worst-case O(1), not amortised"*.
""",
    build_it="""
**Build the LRU cache from the pieces you already wrote.** You have the
sentinel doubly linked list from the linked-list unit; add a `HashMap<Integer,
Node>` and the two operations.

Then do the thing that actually teaches it: write a `checkInvariants()` method
that walks the list, counts the nodes, and asserts that the count equals
`map.size()`, that every node in the list is in the map, and that every map
value is reachable from `head`. Call it after every `get` and `put` in a test
with capacity 2 and a few hundred random operations.

It will fail, and where it fails is the lesson — almost always the eviction path,
which unlinks the node and forgets the map key. That failure *is* the unit: a
design bug is a missing line in one of several places, not a wrong algorithm.
""",
    rungs=[
        _rung("Warm up", "Build the primitives themselves.",
              ["design-hashset", "design-hashmap"],
              {"design-hashset": "Buckets and a hash. The simplest version of the structure every other problem in this unit leans on.",
               "design-hashmap": "Buckets plus chaining. Writing it once explains every “O(1) average” claim you have made since stage 2 — including why a bad hash makes it O(n)."}),
        _rung("Core", "Carry an extra invariant alongside the data.",
              ["min-stack", "design-linked-list", "browser-history"],
              {"min-stack": "The parallel-stack idea, which transfers to far harder problems. Push a duplicate minimum rather than making `pop` conditional.",
               "design-linked-list": "Every splice case in one class. Use a sentinel and watch the null checks disappear.",
               "browser-history": "Two stacks, or one list with a cursor. Decide which before you type — and note that a forward history is *discarded* on a new visit, which the two-stack version gets right for free."}),
        _rung("Variations", "A structure chosen because the data arrives in a helpful order.",
              ["stock-spanner", "time-based-kv"],
              {"stock-spanner": "The monotonic stack from the stacks unit, wrapped in a class and fed one value at a time. Store (price, span) so a popped entry's span is absorbed rather than recomputed.",
               "time-based-kv": "Timestamps arrive increasing, so each key's list is already sorted — binary-search it. You want the last entry `<= t`, which is upper bound minus one."}),
        _rung("Stretch", "Two or three structures kept consistent with each other.",
              ["lru-cache", "design-twitter", "lfu-cache"],
              {"lru-cache": "The canonical design problem. Use sentinel nodes, handle `put` on an existing key, and get every operation to worst-case O(1).",
               "design-twitter": "Merge-k over followees' timelines, truncated at 10. Only the head of each list can be next — that is what stops it being O(total tweets).",
               "lfu-cache": "LRU with a second dimension: frequency buckets, each an LRU list of its own, plus a minimum-frequency pointer. Draw the three structures and their invariants before coding."}),
    ],
    next_up="""
Linear structures are done — six of them, and the judgement to pick between
them. The next stage is about structures, and problems, that branch.
""",
)
