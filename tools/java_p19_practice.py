# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 19 practice - queues, deques, stacks and heaps.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[19]`.
#
# Comparable / Comparator / Collections.* are module 20, so every PriorityQueue
# here holds Integers or Strings and uses natural ordering only.
#
# OUTPUT STABILITY: an ArrayDeque iterates head to tail, so printing one is
# deterministic. A PriorityQueue's toString is HEAP order, which is only
# partially sorted - so no exercise prints one. They are always drained with
# poll(), which is the only ordered access.
# ---------------------------------------------------------------------------


_RD_W19 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")


def _p19ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_W19):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


def _w19(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _w19k(ws, k, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(k)]), out)


def _jdq(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


_WS19 = (["a", "b", "c"], ["solo"], ["x", "y"], ["p", "q", "r", "s"],
         ["one", "two", "three"])

_NS19 = ([5, 1, 3], [7], [2, 2, 1], [-1, 0, 1], [9, 8, 7, 6])


def _ncase19(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _nkcase19(xs, k, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs), str(k)]), out)


_RD_N19 = ("        int n = sc.nextInt();\n"
           "        int[] a = new int[n];\n"
           "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n")


def _ends_split(ws):
    """Odd-length words go to the FRONT (so they end up reversed), even-length
    ones to the back in order - what addFirst/addLast produce."""
    front = [w for w in ws if len(w) % 2 == 1]
    back = [w for w in ws if len(w) % 2 == 0]
    return list(reversed(front)) + back


def _undo_run(cmds):
    """Stack simulation: push on `add`, pop on `undo`, then drain top first."""
    stack = []
    out = []
    for c in cmds:
        parts = c.split(" ")
        if parts[0] == "add":
            stack.insert(0, parts[1])
        elif not stack:
            out.append("nothing to undo")
        else:
            stack.pop(0)
    out.extend(stack)
    return out


def _jobs_run(cmds):
    """Queue simulation: offer on `add`, poll on `run`, then report the rest."""
    q = []
    out = []
    for c in cmds:
        parts = c.split(" ")
        if parts[0] == "add":
            q.append(parts[1])
        elif not q:
            out.append("idle")
        else:
            out.append("running " + q.pop(0))
    out.append("left=" + str(len(q)))
    return out


def _recent_k19(words, k):
    """Most-recently-used list of at most k distinct words, newest first."""
    recent = []
    for w in words:
        if w in recent:
            recent.remove(w)
        recent.insert(0, w)
        if len(recent) > k:
            recent.pop()
    return recent


# --- Family A - queues ---------------------------------------------------------

_P19_A = _jfam(
    "p19-queue", "Queues",
    "First in, first out, and two families of method.",
    """
```java
Queue<String> q = new ArrayDeque<>();
q.offer("a");           // add at the TAIL
q.peek();               // look at the HEAD, do not remove
q.poll();               // remove and return the head
q.isEmpty();  q.size();
```

**Every operation comes in two versions**, differing only in how they fail:

| Job | Throws | Returns a value |
|---|---|---|
| insert | `add(x)` | `offer(x)` → `false` |
| remove head | `remove()` | `poll()` → `null` |
| inspect head | `element()` | `peek()` → `null` |

For an unbounded queue insertion never fails, so `add` and `offer` are the same.
The difference that matters daily is on an **empty** queue: `poll()` gives
`null`, `remove()` throws `NoSuchElementException`.

**Prefer `offer`/`poll`/`peek`**, because the empty case then reads as an
ordinary `if` rather than a try/catch. The standard drain is:

```java
while (!q.isEmpty()) {
    process(q.poll());
}
```

Driving the loop from the queue rather than a counter is what makes it
impossible to overrun.

**Use `ArrayDeque`.** `LinkedList` also implements `Queue` but is slower and
heavier. `ArrayDeque` forbids `null` elements deliberately: `poll()` returning
`null` must unambiguously mean *empty*.
""",
    [
        _p19ex("j19-pr-drain", "Serve them in order", "Intro",
               "Put the words into a queue and print them, one per line, in the order "
               "they arrived.",
               """
        Queue<String> q = new ArrayDeque<>(words);
        while (!q.isEmpty()) {
            System.out.println(q.poll());
        }
""",
               [_w19(ws, _nl(*ws)) for ws in _WS19],
               ["`ArrayDeque` has a constructor taking another collection.",
                "`poll` removes AND returns the head; `peek` would loop forever.",
                "Drive the loop from `!q.isEmpty()` rather than a counter.",
                "FIFO means the output order is the input order."]),

        _p19ex("j19-pr-peek-size", "Look without taking", "Intro",
               "Put the words into a queue. Print the head without removing it, then "
               "the size.",
               """
        Queue<String> q = new ArrayDeque<>(words);
        System.out.println(q.peek());
        System.out.println(q.size());
""",
               [_w19(ws, _nl(ws[0], len(ws))) for ws in _WS19],
               ["`peek` inspects the head and leaves it in place, so the size is "
                "unchanged.",
                "The head is the FIRST word added.",
                "`poll` would have removed it and made the size one smaller.",
                "`peek` returns `null` on an empty queue rather than throwing."]),

        _p19ex("j19-pr-rotate", "Front to the back", "Medium",
               "Read the words, then `k`. Move the head to the tail `k` times, then "
               "print the queue's contents one per line.",
               """
        int k = sc.nextInt();
        Queue<String> q = new ArrayDeque<>(words);
        for (int i = 0; i < k; i++) {
            q.offer(q.poll());
        }
        while (!q.isEmpty()) {
            System.out.println(q.poll());
        }
""",
               [_w19k(ws, k, _nl(*(list(ws)[k % len(ws):] + list(ws)[:k % len(ws)])))
                for (ws, k) in ((["a", "b", "c"], 1), (["a", "b", "c"], 0),
                                (["solo"], 5), (["x", "y"], 3),
                                (["p", "q", "r", "s"], 2))],
               ["Taking from the head and adding at the tail is one rotation step.",
                "`q.offer(q.poll());` does both in one statement.",
                "A `k` larger than the size just goes round again — no modulo is "
                "needed, because each step is independent.",
                "Then drain with the standard loop."]),

        _p19ex("j19-pr-alternate", "Take every other one", "Medium",
               "Put the words into a queue. Repeatedly discard the head and then print "
               "the next head, until the queue is empty.",
               """
        Queue<String> q = new ArrayDeque<>(words);
        while (!q.isEmpty()) {
            q.poll();
            if (!q.isEmpty()) {
                System.out.println(q.poll());
            }
        }
""",
               [_w19(ws, _nl(*[w for (i, w) in enumerate(ws) if i % 2 == 1]))
                for ws in _WS19],
               ["Two polls per round: discard the first, print the second.",
                "Check `isEmpty()` again before the second poll, or an odd-length "
                "queue would poll an empty one.",
                "`poll` on empty returns `null` rather than throwing, but printing "
                "`null` would be wrong output.",
                "A one-word queue prints nothing at all — case two."]),

        _p19ex("j19-pr-empty-safe", "Drain one too many, safely", "Easy",
               "Put the words into a queue, drain it printing each, then print what "
               "`poll()` returns on the now-empty queue.",
               """
        Queue<String> q = new ArrayDeque<>(words);
        while (!q.isEmpty()) {
            System.out.println(q.poll());
        }
        System.out.println(q.poll());
""",
               [_w19(ws, _nl(*(list(ws) + ["null"]))) for ws in _WS19],
               ["`poll` on an empty queue returns `null` — it does not throw.",
                "`println(null)` prints the four characters `null`.",
                "`remove()` in the same position would throw "
                "`NoSuchElementException` instead.",
                "That difference is the whole distinction between the two method "
                "families."]),
    ])


# --- Family B - deques ---------------------------------------------------------

_P19_B = _jfam(
    "p19-deque", "Deques",
    "Both ends, so one type covers queues and stacks.",
    """
```java
Deque<String> d = new ArrayDeque<>();
d.addFirst(x)   d.addLast(x)
d.pollFirst()   d.pollLast()
d.peekFirst()   d.peekLast()
```

Every operation names its end, and the same throw-versus-return split applies
(`removeFirst` throws, `pollFirst` returns `null`).

**One class, both structures:**

| Structure | Add | Remove |
|---|---|---|
| **Queue** (FIFO) | `addLast` | `pollFirst` |
| **Stack** (LIFO) | `addFirst` | `pollFirst` |

Only the insertion end changes. That is worth saying out loud: a stack and a
queue differ by exactly one method call.

`push` and `pop` exist as stack-flavoured aliases — `push` is `addFirst`, `pop`
is `removeFirst` — so stack code reads like stack code.

**Iteration goes head to tail**, so printing an `ArrayDeque` is deterministic and
shows the order things would come out in. For a deque used as a stack, the most
recently pushed element prints first.

**`ArrayDeque` is a circular array**, not a linked list, which is why it is fast
at both ends and cache-friendly in between.
""",
    [
        _p19ex("j19-pr-both-ends", "Add at both ends", "Easy",
               "Read the words, then add each one at the FRONT if its length is odd and "
               "at the BACK otherwise, in input order. Print the deque.",
               """
        Deque<String> d = new ArrayDeque<>();
        for (String w : words) {
            if (w.length() % 2 == 1) {
                d.addFirst(w);
            } else {
                d.addLast(w);
            }
        }
        System.out.println(d);
""",
               [_w19(ws, _jdq(_ends_split(ws))) for ws in _WS19],
               ["`addFirst` prepends, so odd-length words end up in REVERSE order at "
                "the front.",
                "`addLast` appends, so even-length words keep their order at the "
                "back.",
                "Printing an `ArrayDeque` walks head to tail, which is deterministic.",
                "Case one is three one-letter words, all odd, so it comes out "
                "reversed."]),

        _p19ex("j19-pr-as-stack", "Use it as a stack", "Intro",
               "Add each word at the head, then drain from the head — so they come out "
               "reversed. Print one per line.",
               """
        Deque<String> d = new ArrayDeque<>();
        for (String w : words) {
            d.addFirst(w);
        }
        while (!d.isEmpty()) {
            System.out.println(d.pollFirst());
        }
""",
               [_w19(ws, _nl(*reversed(ws))) for ws in _WS19],
               ["Adding and removing at the SAME end is LIFO.",
                "`addFirst` then `pollFirst`.",
                "`push` and `pop` are aliases for exactly those two.",
                "The last word added is the first printed."]),

        _p19ex("j19-pr-as-queue", "Use it as a queue", "Intro",
               "Same drain from the head, but add at the tail — so the words come out "
               "in their original order.",
               """
        Deque<String> d = new ArrayDeque<>();
        for (String w : words) {
            d.addLast(w);
        }
        while (!d.isEmpty()) {
            System.out.println(d.pollFirst());
        }
""",
               [_w19(ws, _nl(*ws)) for ws in _WS19],
               ["The draining end is unchanged, so only the insertion end decides the "
                "order.",
                "Opposite ends is FIFO; the same end is LIFO.",
                "One method call is the entire difference from the previous variant.",
                "A one-word input looks the same either way, so it proves nothing — "
                "check against case one."]),

        _p19ex("j19-pr-peek-ends", "Look at both ends", "Easy",
               "Build a deque in input order and print its first element, then its "
               "last, then its size.",
               """
        Deque<String> d = new ArrayDeque<>(words);
        System.out.println(d.peekFirst());
        System.out.println(d.peekLast());
        System.out.println(d.size());
""",
               [_w19(ws, _nl(ws[0], ws[-1], len(ws))) for ws in _WS19],
               ["The collection constructor adds in iteration order, so the head is "
                "the first word.",
                "`peekFirst` and `peekLast` inspect without removing.",
                "So the size is unchanged.",
                "A one-word deque reports the same element twice."]),

        _p19ex("j19-pr-palindrome-dq", "Same from both ends", "Medium",
               "Read one word. Push its characters into a `Deque<Character>` and compare "
               "from both ends to decide whether it is a palindrome. Print `true` or "
               "`false`.",
               """
        Deque<Character> d = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            d.addLast(s.charAt(i));
        }
        boolean same = true;
        while (d.size() > 1) {
            if (d.pollFirst() != d.pollLast().charValue()) {
                same = false;
            }
        }
        System.out.println(same);
""",
               [_case(w, _jbool(w == w[::-1]))
                for w in ("racecar", "a", "hello", "abba", "abca")],
               ["Take one character from each end and compare, until fewer than two "
                "remain.",
                "`while (d.size() > 1)` handles odd and even lengths — a lone middle "
                "character needs no comparison.",
                "The elements are `Character` objects, so `!=` would compare "
                "references. `.charValue()` on one side forces the comparison to "
                "unbox.",
                "That is module 17's wrapper trap in a new place.",
                "A flag that starts `true` and is only knocked down."],
               read="        String s = sc.next();\n"),
    ])


# --- Family C - stacks ---------------------------------------------------------

_P19_C = _jfam(
    "p19-stack", "Stacks",
    "Last in, first out, and the problems that shape fits.",
    """
```java
Deque<Character> stack = new ArrayDeque<>();
stack.push(c);         // addFirst
stack.peek();          // null if empty
stack.pop();           // THROWS if empty -> guard with isEmpty()
```

**Use `ArrayDeque`, never `java.util.Stack`.** The old class extends `Vector`,
so it is synchronised for no reason *and* inherits every list method — meaning
`stack.add(0, x)` inserts at the bottom of your stack. It is module 14's
`Stack extends ArrayList` disaster, shipped in the standard library and kept
only for compatibility.

**Bracket matching** is the canonical use, and it is three rules:

1. An opening bracket → **push** it.
2. A closing bracket → the stack must be **non-empty** and its top must be the
   matching opener; **pop** it. Otherwise fail.
3. **At the end the stack must be empty.**

Rule 3 is the forgotten one: `"(("` passes every per-character check and is
still unbalanced.

**`([)]` is the input that matters.** Every kind of bracket is balanced by count,
but the nesting is wrong — so a counting solution passes and only a stack
notices. If a bracket problem's tests do not include it, they are not testing
much.

**Reversal is the giveaway.** "In reverse order", "the most recent", "the
innermost" — all of them mean a stack.
""",
    [
        _p19ex("j19-pr-reverse-stack", "Reverse with a stack", "Intro",
               "Push every word and pop them all, printing one per line.",
               """
        Deque<String> stack = new ArrayDeque<>();
        for (String w : words) {
            stack.push(w);
        }
        while (!stack.isEmpty()) {
            System.out.println(stack.pop());
        }
""",
               [_w19(ws, _nl(*reversed(ws))) for ws in _WS19],
               ["`push` is `addFirst` and `pop` is `removeFirst`.",
                "LIFO gives reversal for free.",
                "Guard with `!stack.isEmpty()`, because `pop` throws on an empty "
                "stack.",
                "`poll()` would return `null` instead of throwing, if you prefer."]),

        _p19ex("j19-pr-top", "What is on top?", "Intro",
               "Push every word, then print the top without removing it, then the "
               "size.",
               """
        Deque<String> stack = new ArrayDeque<>();
        for (String w : words) {
            stack.push(w);
        }
        System.out.println(stack.peek());
        System.out.println(stack.size());
""",
               [_w19(ws, _nl(ws[-1], len(ws))) for ws in _WS19],
               ["`peek` leaves the stack alone, so the size is the full count.",
                "The top is the LAST word pushed.",
                "`pop` would have removed it.",
                "`peek` returns `null` on an empty stack rather than throwing."]),

        _p19ex("j19-pr-parens", "Balanced parentheses", "Medium",
               "Read one line of `(` and `)` only. Print `true` if the brackets are "
               "balanced, `false` otherwise — remembering the end-of-input check.",
               """
        Deque<Character> stack = new ArrayDeque<>();
        boolean ok = true;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') {
                stack.push(c);
            } else {
                if (stack.isEmpty()) {
                    ok = false;
                } else {
                    stack.pop();
                }
            }
        }
        if (!stack.isEmpty()) {
            ok = false;
        }
        System.out.println(ok);
""",
               [_case(s, _jbool(_brackets_ok(s)))
                for s in ("()", "((", "(())", "())(", "(()")],
               ["Push every opener; on a closer, the stack must be non-empty — pop "
                "it.",
                "Check `isEmpty()` BEFORE popping, or a leading closer throws.",
                "After the loop, anything left is an unclosed opener: "
                "`if (!stack.isEmpty()) ok = false;`",
                "Cases two and five end with leftovers; case four closes too early.",
                "A flag that starts `true` and is only knocked down."],
               read="        String s = sc.next();\n"),

        _p19ex("j19-pr-brackets3", "Three kinds of bracket", "Hard",
               "Read one line of `()[]{}` only. Print `true` if correctly balanced AND "
               "nested, `false` otherwise.",
               """
        Deque<Character> stack = new ArrayDeque<>();
        boolean ok = true;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c);
            } else {
                if (stack.isEmpty()) {
                    ok = false;
                } else {
                    char open = stack.pop();
                    if (c == ')' && open != '(') {
                        ok = false;
                    }
                    if (c == ']' && open != '[') {
                        ok = false;
                    }
                    if (c == '}' && open != '{') {
                        ok = false;
                    }
                }
            }
        }
        if (!stack.isEmpty()) {
            ok = false;
        }
        System.out.println(ok);
""",
               [_case(s, _jbool(_brackets_ok(s)))
                for s in ("()[]{}", "([{}])", "(]", "([)]", "{{}")],
               ["Push openers; on a closer, pop and check the popped opener MATCHES.",
                "`([)]` is the case that separates a real stack from counting — every "
                "kind is balanced by count, but the nesting is wrong.",
                "Store the popped opener in a `char` so the comparison unboxes.",
                "Do not forget the final emptiness check for unclosed openers.",
                "One flag, knocked down by any of the three failure modes."],
               read="        String s = sc.next();\n"),

        _p19ex("j19-pr-undo", "Undo the last one", "Medium",
               "Read `n` commands. `add <word>` pushes a word; `undo` removes the most "
               "recent, or prints `nothing to undo` if there is none. At the end print "
               "the stack from top to bottom, one per line.",
               """
        int n = Integer.parseInt(sc.nextLine());
        Deque<String> stack = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ");
            if (parts[0].equals("add")) {
                stack.push(parts[1]);
            } else {
                if (stack.isEmpty()) {
                    System.out.println("nothing to undo");
                } else {
                    stack.pop();
                }
            }
        }
        while (!stack.isEmpty()) {
            System.out.println(stack.pop());
        }
""",
               [_case("\n".join([str(len(cmds))] + list(cmds)) + "\n",
                      _nl(*_undo_run(cmds)))
                for cmds in (["add a", "add b", "undo"],
                             ["undo"],
                             ["add x", "undo", "undo"],
                             ["add p", "add q"],
                             ["add a", "undo", "add b"])],
               ["A stack is exactly the shape of undo: the most recent action is the "
                "one you take back.",
                "`push` on `add`, `pop` on `undo`.",
                "Guard the pop with `isEmpty()` and print the message instead.",
                "Draining at the end prints top to bottom, which is most recent "
                "first.",
                "Check `parts[0]` with `.equals`, and read `parts[1]` only for "
                "`add`."],
               read=""),
    ])


# --- Family D - priority queues ------------------------------------------------

_P19_D = _jfam(
    "p19-heap", "Priority queues",
    "The smallest first, and only through `poll`.",
    """
```java
Queue<Integer> pq = new PriorityQueue<>();
pq.offer(5); pq.offer(1); pq.offer(3);
pq.poll();      // 1
pq.poll();      // 3
```

Despite the name it is **not FIFO**. `poll()` always returns the **smallest**
remaining element by natural ordering. It is a binary heap:

| Operation | Cost |
|---|---|
| `offer` | O(log n) |
| `poll` | O(log n) |
| `peek` | **O(1)** |

**Only `poll` is ordered.** A heap is only *partially* ordered — each parent
below its children, which is enough to know the root is the minimum and nothing
more. `toString`, the enhanced `for` and `iterator()` all expose that internal
array order, so **never print one**. Every exercise here drains instead.

**The k-largest idiom** is the reason it earns its place:

```java
for (int v : a) {
    pq.offer(v);
    if (pq.size() > k) pq.poll();     // discard the smallest survivor
}
```

A **min**-heap capped at size `k` leaves the k largest, in O(n log k) time and
O(k) space — far better than sorting everything when `n` is huge and `k` is
small. Capping a min-heap to keep the *largest* feels backwards for about ten
seconds, and then never again.

**Natural ordering only, here.** Largest-first, or ordering by a field of your
own class, needs a `Comparator` — module 20.
""",
    [
        _p19ex("j19-pr-heap-drain", "Smallest first", "Easy",
               "Put the numbers into a priority queue and drain it, printing one per "
               "line in ascending order.",
               """
        Queue<Integer> pq = new PriorityQueue<>();
        for (int v : a) {
            pq.offer(v);
        }
        while (!pq.isEmpty()) {
            System.out.println(pq.poll());
        }
""",
               [_ncase19(xs, _nl(*sorted(xs))) for xs in _NS19],
               ["Declare it as `Queue<Integer>` — `PriorityQueue` implements "
                "`Queue`.",
                "Draining with `poll` gives ascending order.",
                "Printing the queue itself would give heap order, which is not "
                "sorted.",
                "Duplicates come out in the right place — case three has two twos."],
               read=_RD_N19),

        _p19ex("j19-pr-heap-peek", "Smallest right now", "Intro",
               "Put the numbers into a priority queue. Print the smallest without "
               "removing it, then the size.",
               """
        Queue<Integer> pq = new PriorityQueue<>();
        for (int v : a) {
            pq.offer(v);
        }
        System.out.println(pq.peek());
        System.out.println(pq.size());
""",
               [_ncase19(xs, _nl(min(xs), len(xs))) for xs in _NS19],
               ["`peek` is O(1) — the minimum is always at the root of the heap.",
                "It leaves the queue untouched, so the size is the full count.",
                "`poll` would have removed it.",
                "This is what makes a heap better than re-scanning or re-sorting."],
               read=_RD_N19),

        _p19ex("j19-pr-ksmallest", "The k smallest", "Medium",
               "Read the numbers, then `k` (with `1 <= k <= n`). Print the `k` smallest "
               "values in ascending order, one per line.",
               """
        int k = sc.nextInt();
        Queue<Integer> pq = new PriorityQueue<>();
        for (int v : a) {
            pq.offer(v);
        }
        for (int i = 0; i < k; i++) {
            System.out.println(pq.poll());
        }
""",
               [_nkcase19(xs, k, _nl(*sorted(xs)[:k]))
                for (xs, k) in (([5, 1, 3, 9, 7], 2), ([7], 1), ([1, 2, 3, 4], 4),
                                ([4, 4, 4], 2), ([-5, -1, -3], 2))],
               ["Offer everything, then poll exactly `k` times.",
                "Each poll gives the next smallest, so the output is already "
                "ascending.",
                "You do not need to drain the rest.",
                "Cost is O(n + k log n) — sorting everything would be O(n log n), "
                "which is fine here but worse when k is tiny and n is huge."],
               read=_RD_N19),

        _p19ex("j19-pr-klargest", "The k largest", "Hard",
               "Read the numbers, then `k`. Print the `k` LARGEST values in ascending "
               "order, keeping a heap of at most `k` elements.",
               """
        int k = sc.nextInt();
        Queue<Integer> pq = new PriorityQueue<>();
        for (int v : a) {
            pq.offer(v);
            if (pq.size() > k) {
                pq.poll();
            }
        }
        while (!pq.isEmpty()) {
            System.out.println(pq.poll());
        }
""",
               [_nkcase19(xs, k, _nl(*sorted(xs)[len(xs) - k:]))
                for (xs, k) in (([5, 1, 3, 9, 7], 2), ([7], 1), ([1, 2, 3, 4], 4),
                                ([4, 4, 4], 2), ([-5, -1, -3], 2))],
               ["A MIN-heap capped at `k`: the head is the smallest survivor, which "
                "is exactly the one least deserving of its place.",
                "Offer every element, then poll immediately if the size exceeds `k`.",
                "Whatever remains is the k largest.",
                "Draining a min-heap gives ascending order, which is what the brief "
                "asks for.",
                "O(n log k) time and O(k) space.",
                "Duplicates count separately — case four keeps two of the three "
                "fours."],
               read=_RD_N19),

        _p19ex("j19-pr-heap-words", "Alphabetically first", "Medium",
               "Put the words into a priority queue and drain it — `String` has a "
               "natural ordering, so they come out alphabetically. Print one per line.",
               """
        Queue<String> pq = new PriorityQueue<>(words);
        while (!pq.isEmpty()) {
            System.out.println(pq.poll());
        }
""",
               [_w19(ws, _nl(*sorted(ws))) for ws in _WS19],
               ["A `PriorityQueue` works on anything with a natural ordering, not "
                "just numbers.",
                "`String`'s ordering is alphabetical by character code.",
                "The collection constructor heapifies the whole list at once.",
                "Draining is still the only ordered access — printing the queue would "
                "show heap order.",
                "Duplicates are kept; a heap is not a set."]),
    ])


# --- Family E - applied --------------------------------------------------------

_P19_E = _jfam(
    "p19-applied", "Putting them to work",
    "Where the shape of the structure IS the algorithm.",
    """
The point of this module is recognising which shape a problem wants. Three
signals:

**"In reverse", "the most recent", "the innermost" → a stack.** Undo, bracket
matching, back buttons, expression parsing, and the call stack itself.

**"In the order they arrived", "next in line" → a queue.** Job pipelines,
breadth-first search, buffering.

**"The smallest so far", "the top k" → a heap.** Scheduling, k-largest, merging
sorted streams, Dijkstra.

Two patterns worth having in your fingers:

**Two stacks make a queue.** Push onto one; when you need to dequeue, if the
second is empty, pour the whole first stack into it — reversing it once — and pop
from there. Each element moves at most twice, so it is amortised O(1).

**A deque is a sliding window.** Keeping the front as "oldest" and the back as
"newest" lets you drop from either end as the window moves.

And the recurring correctness rule from this whole module: **check `isEmpty()`
before every `pop` or `remove`**, or use `poll`/`peek` and handle the `null`.
Which of the two you choose should be a decision, not an accident.
""",
    [
        _p19ex("j19-pr-two-stacks", "A queue from two stacks", "Hard",
               "Push every word onto stack A. Then pour all of A into stack B and drain "
               "B — which prints them in their ORIGINAL order, because reversing twice "
               "restores it.",
               """
        Deque<String> a = new ArrayDeque<>();
        Deque<String> b = new ArrayDeque<>();
        for (String w : words) {
            a.push(w);
        }
        while (!a.isEmpty()) {
            b.push(a.pop());
        }
        while (!b.isEmpty()) {
            System.out.println(b.pop());
        }
""",
               [_w19(ws, _nl(*ws)) for ws in _WS19],
               ["Pushing onto A reverses the order once.",
                "Pouring A into B reverses it again, which restores the original.",
                "Draining B therefore prints FIFO order from two LIFO structures.",
                "This is how a queue is built from two stacks, and each element moves "
                "at most twice.",
                "Guard both drains with `isEmpty()`."]),

        _p19ex("j19-pr-window-max", "Largest in each window", "Hard",
               "Read the numbers, then a window width `k` (with `1 <= k <= n`). Print "
               "the largest value in each window of `k` consecutive numbers, one per "
               "line.",
               """
        int k = sc.nextInt();
        for (int i = 0; i + k <= n; i++) {
            int best = a[i];
            for (int j = i; j < i + k; j++) {
                if (a[j] > best) {
                    best = a[j];
                }
            }
            System.out.println(best);
        }
""",
               [_nkcase19(xs, k, _nl(*[max(xs[i:i + k])
                                       for i in range(len(xs) - k + 1)]))
                for (xs, k) in (([5, 1, 3, 9, 7], 2), ([7], 1), ([1, 2, 3, 4], 4),
                                ([4, 4, 4], 2), ([-5, -1, -3], 2))],
               ["There are `n - k + 1` windows, so the outer loop runs while "
                "`i + k <= n`.",
                "The straightforward version rescans each window: O(n * k).",
                "Seed `best` from the window's own first element, never `0` — case "
                "five is all negative.",
                "A deque-based solution does this in O(n) and is a classic interview "
                "question; the honest O(n * k) version is the right starting point.",
                "When `k == n` there is exactly one window."],
               read=_RD_N19),

        _p19ex("j19-pr-merge-heaps", "Merge two sorted streams", "Hard",
               "Read two groups of numbers. Print all of them in ascending order, one "
               "per line, by putting everything into one heap.",
               """
        int m = sc.nextInt();
        Queue<Integer> pq = new PriorityQueue<>();
        for (int v : a) {
            pq.offer(v);
        }
        for (int i = 0; i < m; i++) {
            pq.offer(sc.nextInt());
        }
        while (!pq.isEmpty()) {
            System.out.println(pq.poll());
        }
""",
               [_case("\n".join([str(len(x)), " ".join(str(v) for v in x),
                                 str(len(y)), " ".join(str(v) for v in y)]),
                      _nl(*sorted(list(x) + list(y))))
                for (x, y) in (([1, 3, 5], [2, 4, 6]), ([1], [2]),
                               ([5], [1]), ([1, 1], [1, 1]),
                               ([-3, 0], [-1, 2, 5]))],
               ["A heap does not care where the elements came from.",
                "Offer both groups, then drain once.",
                "The result is fully sorted, whatever order the inputs arrived in.",
                "For genuinely sorted inputs the two-pointer merge from module 5 is "
                "O(n + m) and better; the heap version generalises to any number of "
                "streams, which is why it is worth knowing."],
               read=_RD_N19),

        _p19ex("j19-pr-recent", "Most recently seen", "Hard",
               "Read the words, then `k`. Print the last `k` DISTINCT words in "
               "most-recent-first order, one per line. A repeat moves a word to the "
               "most recent position.",
               """
        int k = sc.nextInt();
        Deque<String> recent = new ArrayDeque<>();
        for (String w : words) {
            recent.remove(w);
            recent.addFirst(w);
            if (recent.size() > k) {
                recent.removeLast();
            }
        }
        while (!recent.isEmpty()) {
            System.out.println(recent.pollFirst());
        }
""",
               [_w19k(ws, k, _nl(*_recent_k19(ws, k)))
                for (ws, k) in ((["a", "b", "a", "c"], 2), (["solo"], 3),
                                (["x", "y", "z"], 2), (["p", "p", "p"], 1),
                                (["a", "b", "c", "d"], 3))],
               ["A deque gives both ends: most recent at the front, oldest at the "
                "back.",
                "`remove(w)` first drops any earlier position for the same word, so a "
                "repeat MOVES rather than duplicating. It is O(n), but the deque is "
                "tiny.",
                "Then `addFirst(w)` puts it at the most-recent end.",
                "Trim with `removeLast()` whenever the size exceeds `k`.",
                "Drain from the front so the most recent prints first.",
                "This is the shape of every 'recently opened files' list."]),

        _p19ex("j19-pr-sim", "A simple job queue", "Hard",
               "Read `n` commands. `add <word>` queues a job; `run` takes the next job "
               "and prints `running <word>`, or prints `idle` if there is none. At the "
               "end print `left=<how many remain>`.",
               """
        int n = Integer.parseInt(sc.nextLine());
        Queue<String> jobs = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            String[] parts = line.split(" ");
            if (parts[0].equals("add")) {
                jobs.offer(parts[1]);
            } else {
                if (jobs.isEmpty()) {
                    System.out.println("idle");
                } else {
                    System.out.println("running " + jobs.poll());
                }
            }
        }
        System.out.println("left=" + jobs.size());
""",
               [_case("\n".join([str(len(cmds))] + list(cmds)) + "\n",
                      _nl(*_jobs_run(cmds)))
                for cmds in (["add a", "add b", "run"],
                             ["run"],
                             ["add x", "run", "run"],
                             ["add p", "add q"],
                             ["add a", "run", "add b", "run"])],
               ["FIFO is the right shape: jobs run in the order they were queued.",
                "`offer` on `add`, `poll` on `run`.",
                "Guard the poll with `isEmpty()` and print `idle` instead.",
                "The summary counts whatever is still queued at the end.",
                "Compare with the stack-based undo exercise: the same command loop, "
                "the opposite order of service."],
               read=""),
    ])


_PRACTICE[19] = [_P19_A, _P19_B, _P19_C, _P19_D, _P19_E]
