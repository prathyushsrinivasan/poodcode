# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 19 - Queues, deques, stacks and heaps.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `Comparable` / `Comparator` / `Collections.` are module 20, so every
# PriorityQueue here holds Integers or Strings and relies on natural ordering
# only.
#
# OUTPUT STABILITY: an ArrayDeque iterates head to tail, so printing one is
# deterministic. A PriorityQueue's toString is HEAP order, not sorted order -
# only `poll()` is ordered - so no exercise ever prints one directly. That is
# stated in the prose, because it is one of the module's real lessons.
# ---------------------------------------------------------------------------

_M19 = []


def _brackets_ok(s):
    """Mirror of the stack algorithm: push openers, match on close, and the
    stack must be EMPTY at the end."""
    partner = {")": "(", "]": "[", "}": "{"}
    stack = []
    for c in s:
        if c in "([{":
            stack.append(c)
        else:
            if not stack or stack.pop() != partner[c]:
                return False
    return not stack


# --- 19.1 Queue -------------------------------------------------------------

_M19.append(_jlesson(
    "m19-queue", "`Queue`",
    "First in, first out - and the two families of method.",
    """
```java
Queue<String> q = new ArrayDeque<>();
q.offer("a");                  // add at the TAIL
q.offer("b");
System.out.println(q.peek());  // "a"  — look at the HEAD, do not remove
System.out.println(q.poll());  // "a"  — remove and return the head
System.out.println(q.size());  // 1
```

**FIFO**: things leave in the order they arrived. That is the whole idea, and it
is the shape of every waiting line, job queue and breadth-first search.

## The two families

Every `Queue` operation comes in two versions that differ **only in how they
fail**:

| Job | Throws on failure | Returns a special value |
|---|---|---|
| insert | `add(x)` | `offer(x)` → `false` |
| remove head | `remove()` | `poll()` → `null` |
| inspect head | `element()` | `peek()` → `null` |

For an unbounded queue like `ArrayDeque` insertion never fails, so `add` and
`offer` are the same. The difference that matters daily is **`poll` versus
`remove` on an empty queue**: `poll()` gives you `null`, `remove()` throws
`NoSuchElementException`.

**Prefer `offer`/`poll`/`peek`.** Returning a value lets you write the empty
case as an ordinary `if`, which is almost always what you want:

```java
while (!q.isEmpty()) {
    process(q.poll());
}
```

**`ArrayDeque` is the implementation to use.** `LinkedList` also implements
`Queue` and works, but `ArrayDeque` is faster and uses less memory. Do **not**
use `java.util.Stack` or `Vector` — both are legacy, synchronised for no reason,
and `Stack` extends `Vector`, which is module 14's `Stack extends ArrayList`
mistake shipped in the standard library.

> `ArrayDeque` rejects `null` elements outright, and that is deliberate:
> `poll()` returning `null` has to mean *empty*, so a `null` element would make
> the answer ambiguous.
""",
    warmup=[
        _jq("What does `poll()` return on an empty queue?",
            ["null", "It throws NoSuchElementException", "0", "an empty string"],
            0,
            "`remove()` is the one that throws. That is the only difference between "
            "the two families."),
        _jq("Why does ArrayDeque forbid null elements?",
            ["Because poll() returning null must unambiguously mean 'empty'",
             "To save memory", "Because of generics", "It does not"],
            0,
            "A null element would make the empty test impossible to write correctly."),
    ],
    exercises=[
        _je("j19-q-create", "A queue of names",
            "Read `n` words into a queue and print how many it holds. Replace `____` "
            "with the declaration of an empty queue of strings.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Queue<String> q = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            q.offer(sc.next());\n"
                   "        }\n"
                   "        System.out.println(q.size());"),
            "Queue<String> q = new ArrayDeque<>();",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), len(ws))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three", "four"])],
            hints=["Declare the variable as the `Queue` interface.",
                   "Construct an `ArrayDeque`, the recommended implementation.",
                   "`Queue<String> q = new ArrayDeque<>();`",
                   "`offer` adds at the tail."],
            difficulty="Intro"),

        _je("j19-q-drain", "Serve them in order",
            "Print the words in the order they arrived, emptying the queue as you go. "
            "Replace `____` with the call that removes and returns the head.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Queue<String> q = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            q.offer(sc.next());\n"
                   "        }\n"
                   "        while (!q.isEmpty()) {\n"
                   "            System.out.println(q.poll());\n"
                   "        }"),
            "q.poll()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*ws))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three"])],
            hints=["`peek` looks without removing, so the loop would never end.",
                   "`poll` removes AND returns the head.",
                   "`q.poll()`",
                   "FIFO means the output order is the input order."],
            difficulty="Intro"),

        _jfix("j19-q-empty", "Draining one too many",
              "This calls `remove()` one extra time and throws "
              "`NoSuchElementException` on the empty queue. Rewrite the draining so it "
              "stops when the queue is empty, printing each word on its own line.",
              _jscan("        int n = sc.nextInt();\n"
                     "        Queue<String> q = new ArrayDeque<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            q.offer(sc.next());\n"
                     "        }\n"
                     "        for (int i = 0; i <= n; i++) {\n"
                     "            System.out.println(q.remove());\n"
                     "        }"),
              _jscan("        int n = sc.nextInt();\n"
                     "        Queue<String> q = new ArrayDeque<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            q.offer(sc.next());\n"
                     "        }\n"
                     "        while (!q.isEmpty()) {\n"
                     "            System.out.println(q.poll());\n"
                     "        }"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*ws))
               for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                          ["one", "two"])],
              hints=["The counted loop runs `n + 1` times because of the `<=`.",
                     "Rather than fixing the bound, drive the loop from the queue "
                     "itself.",
                     "`while (!q.isEmpty())` cannot overrun, whatever `n` says.",
                     "Switch `remove()` to `poll()` too — with the emptiness already "
                     "checked, either works, but `poll` is the idiomatic pair.",
                     "That combination is the standard draining loop."],
              difficulty="Easy"),

        _jch("j19-q-rotate", "Send the front to the back", "Medium",
             "Read `n` words, then `k`. Move the front word to the back `k` times, then "
             "print the queue's contents from head to tail, one per line.",
             _jscan("        int n = sc.nextInt();\n"
                    "        Queue<String> q = new ArrayDeque<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            q.offer(sc.next());\n"
                    "        }\n"
                    "        int k = sc.nextInt();\n"
                    "        for (int i = 0; i < k; i++) {\n"
                    "            q.offer(q.poll());\n"
                    "        }\n"
                    "        while (!q.isEmpty()) {\n"
                    "            System.out.println(q.poll());\n"
                    "        }"),
             "        for (int i = 0; i < k; i++) {\n"
             "            q.offer(q.poll());\n"
             "        }\n"
             "        while (!q.isEmpty()) {\n"
             "            System.out.println(q.poll());\n"
             "        }",
             [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                    _nl(*(list(ws)[k % len(ws):] + list(ws)[:k % len(ws)])))
              for (ws, k) in ((["a", "b", "c"], 1), (["a", "b", "c"], 0),
                              (["solo"], 5), (["x", "y"], 3),
                              (["p", "q", "r", "s"], 2))],
             hints=["Taking from the head and adding at the tail is a rotation: "
                    "`q.offer(q.poll())`.",
                    "One statement per step, `k` times.",
                    "A `k` larger than the size just goes round again — case three "
                    "and four rely on that, and no modulo is needed because each step "
                    "is independent.",
                    "Then drain with the standard `while (!q.isEmpty())` loop."]),
    ],
    quiz=[
        _jq("Which pair should you prefer for a queue you might drain empty?",
            ["offer / poll / peek - they return a value instead of throwing",
             "add / remove / element",
             "They are identical",
             "push / pop"],
            0,
            "Returning a value lets the empty case be an ordinary `if` rather than a "
            "try/catch."),
        _jq("Which implementation should you use for a Queue?",
            ["ArrayDeque", "java.util.Stack", "Vector", "TreeSet"],
            0,
            "LinkedList works but is slower; Stack and Vector are legacy and "
            "needlessly synchronised."),
    ],
))


# --- 19.2 Deque -------------------------------------------------------------

_M19.append(_jlesson(
    "m19-deque", "`Deque`",
    "Both ends, so one type covers queues and stacks.",
    """
A **deque** ("deck") is a double-ended queue: add and remove at either end. Every
operation names its end explicitly.

```java
Deque<String> d = new ArrayDeque<>();
d.addFirst("a");    d.addLast("z");
d.peekFirst();      d.peekLast();
d.pollFirst();      d.pollLast();
```

That is the whole API, doubled from `Queue` and with the same throw-versus-return
split (`removeFirst` throws, `pollFirst` returns `null`).

**Because it does both ends, one class covers both classic structures:**

| Structure | Add | Remove |
|---|---|---|
| **Queue** (FIFO) | `addLast` | `pollFirst` |
| **Stack** (LIFO) | `addFirst` | `pollFirst` |

Only the *insertion* end changes. That is worth pausing on: a stack and a queue
differ by exactly one method call.

`Deque` also provides `push`/`pop`/`peek` as stack-flavoured aliases —
`push` is `addFirst`, `pop` is `removeFirst`. They read well, and they are why
`ArrayDeque` is the recommended stack.

**Iteration goes head to tail**, so printing an `ArrayDeque` is deterministic and
shows the order things would come out in. For a deque used as a stack, that means
the most recently pushed element prints first.

> **`ArrayDeque` is a circular array**, not a linked list — despite living next
> to `LinkedList` in every tutorial. That is why it is fast at both ends and
> cache-friendly in the middle.
""",
    warmup=[
        _jq("Using a Deque as a stack, which pair do you use?",
            ["addFirst and pollFirst", "addLast and pollFirst",
             "addFirst and pollLast", "addLast and pollLast"],
            0,
            "Both operations at the same end is LIFO. Opposite ends is FIFO."),
        _jq("What is `push` an alias for on a Deque?",
            ["addFirst", "addLast", "offer", "peek"],
            0,
            "And `pop` is `removeFirst`. They exist so stack code reads like stack "
            "code."),
    ],
    exercises=[
        _je("j19-dq-stack", "Use it as a stack",
            "Read `n` words and print them in REVERSE order by pushing each and then "
            "draining. Replace `____` with the call that adds at the head.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Deque<String> d = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            d.addFirst(sc.next());\n"
                   "        }\n"
                   "        while (!d.isEmpty()) {\n"
                   "            System.out.println(d.pollFirst());\n"
                   "        }"),
            "d.addFirst(sc.next())",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*reversed(ws)))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three"])],
            hints=["Draining uses `pollFirst`, so adding at the same end gives LIFO.",
                   "`d.addFirst(sc.next())`",
                   "`push` would do the same thing, since it is an alias for "
                   "`addFirst`.",
                   "Adding at the tail instead would print the original order."],
            difficulty="Easy"),

        _je("j19-dq-queue", "Use it as a queue",
            "Same drain, but print the words in their ORIGINAL order. Replace `____` "
            "with the call that adds at the tail.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Deque<String> d = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            d.addLast(sc.next());\n"
                   "        }\n"
                   "        while (!d.isEmpty()) {\n"
                   "            System.out.println(d.pollFirst());\n"
                   "        }"),
            "d.addLast(sc.next())",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*ws))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three"])],
            hints=["The draining end is unchanged, so only the insertion end decides "
                   "the order.",
                   "`d.addLast(sc.next())`",
                   "Opposite ends is FIFO; the same end is LIFO.",
                   "One method call is the entire difference between a stack and a "
                   "queue."],
            difficulty="Intro"),

        _jfix("j19-dq-ends", "Wrong end",
              "This is meant to print the words in their original order, but it adds "
              "and removes at the same end, so it reverses them. Fix it by changing the "
              "removal to take from the other end.",
              _jscan("        int n = sc.nextInt();\n"
                     "        Deque<String> d = new ArrayDeque<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            d.addFirst(sc.next());\n"
                     "        }\n"
                     "        while (!d.isEmpty()) {\n"
                     "            System.out.println(d.pollFirst());\n"
                     "        }"),
              _jscan("        int n = sc.nextInt();\n"
                     "        Deque<String> d = new ArrayDeque<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            d.addFirst(sc.next());\n"
                     "        }\n"
                     "        while (!d.isEmpty()) {\n"
                     "            System.out.println(d.pollLast());\n"
                     "        }"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*ws))
               for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                          ["one", "two", "three"])],
              hints=["Adding at the head and removing at the head is LIFO, which "
                     "reverses.",
                     "The brief says not to change the insertion, so change the "
                     "removal.",
                     "`d.pollLast()` takes from the opposite end, giving FIFO.",
                     "A one-word input looks the same either way — case two and four "
                     "will not tell you if you got it right."],
              difficulty="Easy"),

        _jch("j19-dq-palindrome", "Same from both ends", "Medium",
             "Read one word. Push every character onto a `Deque<Character>`, then "
             "compare from both ends to decide whether it is a palindrome. Print `true` "
             "or `false`.",
             _jscan("        String s = sc.next();\n"
                    "        Deque<Character> d = new ArrayDeque<>();\n"
                    "        for (int i = 0; i < s.length(); i++) {\n"
                    "            d.addLast(s.charAt(i));\n"
                    "        }\n"
                    "        boolean same = true;\n"
                    "        while (d.size() > 1) {\n"
                    "            if (d.pollFirst() != d.pollLast().charValue()) {\n"
                    "                same = false;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(same);"),
             "        boolean same = true;\n"
             "        while (d.size() > 1) {\n"
             "            if (d.pollFirst() != d.pollLast().charValue()) {\n"
             "                same = false;\n"
             "            }\n"
             "        }\n"
             "        System.out.println(same);",
             [_case(w, _jbool(w == w[::-1]))
              for w in ("racecar", "a", "hello", "abba", "abca")],
             hints=["Take one character from each end and compare, until fewer than "
                    "two remain.",
                    "`while (d.size() > 1)` handles both odd and even lengths — an "
                    "odd middle character is left over and needs no comparison.",
                    "The elements are `Character` objects, so `!=` would compare "
                    "references. Force one side to a primitive with `.charValue()` so "
                    "the comparison unboxes.",
                    "That is module 17's wrapper trap again, in a new place.",
                    "A flag that starts `true` and is only knocked down."]),
    ],
    quiz=[
        _jq("What single change turns a Deque-based queue into a stack?",
            ["Insert at the same end you remove from",
             "Use push instead of offer",
             "Change to LinkedList",
             "Reverse the input"],
            0,
            "Opposite ends is FIFO, same end is LIFO. Nothing else differs."),
        _jq("What data structure is ArrayDeque actually built on?",
            ["A circular array", "A doubly linked list", "A hash table",
             "A red-black tree"],
            0,
            "Which is why it is fast at both ends and far more cache-friendly than "
            "LinkedList."),
    ],
))


# --- 19.3 stacks ------------------------------------------------------------

_M19.append(_jlesson(
    "m19-stack", "Stacks",
    "Last in, first out, and the problems that shape fits.",
    """
```java
Deque<Character> stack = new ArrayDeque<>();
stack.push('(');            // addFirst
char top = stack.peek();    // peekFirst — look, do not remove
stack.pop();                // removeFirst — THROWS when empty
```

**Use `ArrayDeque`, not `java.util.Stack`.** The old `Stack` class extends
`Vector`, which means it is synchronised for no reason *and* inherits every list
method — so `stack.add(0, x)` inserts at the bottom of your stack. That is
precisely module 14's `class Stack extends ArrayList` disaster, shipped in the
standard library since 1.0 and kept only for compatibility.

**`pop()` and `peek()` differ in their empty behaviour**, following the two
families: `pop()` throws `NoSuchElementException`, `peek()` returns `null`. So
guard with `isEmpty()` before popping.

## Where stacks show up

**Matching brackets** is the canonical one, and the algorithm is three rules:

1. An opening bracket → push it.
2. A closing bracket → the stack must be non-empty and its top must be the
   matching opener; pop it. Otherwise, fail.
3. At the end, the stack must be **empty**.

Forgetting rule 3 is the classic bug: `"(("` passes every character check and is
still unbalanced.

**Undo** is a stack of past states. **Expression evaluation** uses one for
operands and one for operators. **The call stack itself** is a stack — which is
what module 10's recursion was pushing frames onto, and why a runaway recursion
gives you `StackOverflowError`.

**Reversal is the giveaway.** Any time a problem says "in reverse order", "the
most recent", or "the innermost", a stack is probably the answer.
""",
    warmup=[
        _jq("Why avoid java.util.Stack?",
            ["It extends Vector, so it is needlessly synchronised and exposes list methods like add(0, x)",
             "It is not generic",
             "It has no pop method",
             "It is faster but unsafe"],
            0,
            "It is the standard library's own example of inheritance misused. Use "
            "ArrayDeque."),
        _jq("In bracket matching, why must you check the stack is empty at the end?",
            ["Otherwise unclosed openers like \"((\" pass every per-character check",
             "To free memory",
             "To avoid an exception",
             "You do not need to"],
            0,
            "Every character can be individually fine and the string still unbalanced."),
    ],
    exercises=[
        _je("j19-st-push", "Push and peek",
            "Read `n` words, push each, then print the top of the stack without "
            "removing it. Replace `____` with the call that looks at the top.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Deque<String> stack = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            stack.push(sc.next());\n"
                   "        }\n"
                   "        System.out.println(stack.peek());\n"
                   "        System.out.println(stack.size());"),
            "stack.peek()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(ws[-1], len(ws)))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three"])],
            hints=["`peek` looks at the top without removing it, so the size is "
                   "unchanged.",
                   "`stack.peek()`",
                   "The top is the LAST word pushed.",
                   "`pop` would have removed it and made the size one smaller."],
            difficulty="Intro"),

        _je("j19-st-reverse", "Reverse with a stack",
            "Print the words in reverse order by popping them all. Replace `____` with "
            "the call that removes and returns the top.",
            _jscan("        int n = sc.nextInt();\n"
                   "        Deque<String> stack = new ArrayDeque<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            stack.push(sc.next());\n"
                   "        }\n"
                   "        while (!stack.isEmpty()) {\n"
                   "            System.out.println(stack.pop());\n"
                   "        }"),
            "stack.pop()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*reversed(ws)))
             for ws in (["a", "b"], ["solo"], ["x", "y", "z"], ["p"],
                        ["one", "two", "three"])],
            hints=["`pop` removes the top and returns it.",
                   "`stack.pop()`",
                   "The guard `!stack.isEmpty()` is what makes `pop` safe — it throws "
                   "on an empty stack.",
                   "LIFO gives reversal for free."],
            difficulty="Intro"),

        _jfix("j19-st-leftover", "The openers nobody closed",
              "This bracket checker handles every character correctly but forgets the "
              "final rule, so `((` is reported as balanced. Add the end-of-input check. "
              "The string contains only `(` and `)`.",
              _jscan("        String s = sc.next();\n"
                     "        Deque<Character> stack = new ArrayDeque<>();\n"
                     "        boolean ok = true;\n"
                     "        for (int i = 0; i < s.length(); i++) {\n"
                     "            char c = s.charAt(i);\n"
                     "            if (c == '(') {\n"
                     "                stack.push(c);\n"
                     "            } else {\n"
                     "                if (stack.isEmpty()) {\n"
                     "                    ok = false;\n"
                     "                } else {\n"
                     "                    stack.pop();\n"
                     "                }\n"
                     "            }\n"
                     "        }\n"
                     "        System.out.println(ok);"),
              _jscan("        String s = sc.next();\n"
                     "        Deque<Character> stack = new ArrayDeque<>();\n"
                     "        boolean ok = true;\n"
                     "        for (int i = 0; i < s.length(); i++) {\n"
                     "            char c = s.charAt(i);\n"
                     "            if (c == '(') {\n"
                     "                stack.push(c);\n"
                     "            } else {\n"
                     "                if (stack.isEmpty()) {\n"
                     "                    ok = false;\n"
                     "                } else {\n"
                     "                    stack.pop();\n"
                     "                }\n"
                     "            }\n"
                     "        }\n"
                     "        if (!stack.isEmpty()) {\n"
                     "            ok = false;\n"
                     "        }\n"
                     "        System.out.println(ok);"),
              [_case(s, _jbool(_brackets_ok(s)))
               for s in ("()", "((", "(())", "())(", "(()")],
              hints=["Every character can be individually valid and the string still "
                     "unbalanced.",
                     "After the loop, anything left on the stack is an opener that was "
                     "never closed.",
                     "Add `if (!stack.isEmpty()) { ok = false; }` before the print.",
                     "Cases two and five end with leftovers; case four closes too "
                     "early and is already caught by the existing check."],
              difficulty="Medium"),

        _jch("j19-st-brackets", "Match three kinds of bracket", "Hard",
             "Read one line containing only `(`, `)`, `[`, `]`, `{` and `}`. Print "
             "`true` if the brackets are correctly balanced and nested, `false` "
             "otherwise.",
             _jscan("        String s = sc.next();\n"
                    "        Deque<Character> stack = new ArrayDeque<>();\n"
                    "        boolean ok = true;\n"
                    "        for (int i = 0; i < s.length(); i++) {\n"
                    "            char c = s.charAt(i);\n"
                    "            if (c == '(' || c == '[' || c == '{') {\n"
                    "                stack.push(c);\n"
                    "            } else {\n"
                    "                if (stack.isEmpty()) {\n"
                    "                    ok = false;\n"
                    "                } else {\n"
                    "                    char open = stack.pop();\n"
                    "                    if (c == ')' && open != '(') {\n"
                    "                        ok = false;\n"
                    "                    }\n"
                    "                    if (c == ']' && open != '[') {\n"
                    "                        ok = false;\n"
                    "                    }\n"
                    "                    if (c == '}' && open != '{') {\n"
                    "                        ok = false;\n"
                    "                    }\n"
                    "                }\n"
                    "            }\n"
                    "        }\n"
                    "        if (!stack.isEmpty()) {\n"
                    "            ok = false;\n"
                    "        }\n"
                    "        System.out.println(ok);"),
             "        Deque<Character> stack = new ArrayDeque<>();\n"
             "        boolean ok = true;\n"
             "        for (int i = 0; i < s.length(); i++) {\n"
             "            char c = s.charAt(i);\n"
             "            if (c == '(' || c == '[' || c == '{') {\n"
             "                stack.push(c);\n"
             "            } else {\n"
             "                if (stack.isEmpty()) {\n"
             "                    ok = false;\n"
             "                } else {\n"
             "                    char open = stack.pop();\n"
             "                    if (c == ')' && open != '(') {\n"
             "                        ok = false;\n"
             "                    }\n"
             "                    if (c == ']' && open != '[') {\n"
             "                        ok = false;\n"
             "                    }\n"
             "                    if (c == '}' && open != '{') {\n"
             "                        ok = false;\n"
             "                    }\n"
             "                }\n"
             "            }\n"
             "        }\n"
             "        if (!stack.isEmpty()) {\n"
             "            ok = false;\n"
             "        }\n"
             "        System.out.println(ok);",
             [_case(s, _jbool(_brackets_ok(s)))
              for s in ("()[]{}", "([{}])", "(]", "([)]", "{{}")],
             hints=["Push every opener; on a closer, pop and check it MATCHES.",
                    "`([)]` is the case that separates a real stack solution from "
                    "merely counting — every kind is balanced by count, but the "
                    "nesting is wrong.",
                    "Check `isEmpty()` before popping, or a leading closer throws.",
                    "Store the popped opener in a `char` so the comparison unboxes.",
                    "Do not forget the final `!stack.isEmpty()` check for unclosed "
                    "openers.",
                    "A flag that starts `true` and is only knocked down keeps it "
                    "simple."]),
    ],
    quiz=[
        _jq("Which input distinguishes a stack solution from just counting brackets?",
            ["([)]", "()", "((", "))"],
            0,
            "Every kind appears twice, so counts match - but the nesting is wrong, and "
            "only a stack notices."),
        _jq("What throws when the structure is empty?",
            ["pop()", "peek()", "poll()", "isEmpty()"],
            0,
            "peek and poll return null; pop and remove throw. Same two families as the "
            "queue."),
    ],
))


# --- 19.4 PriorityQueue -----------------------------------------------------

_M19.append(_jlesson(
    "m19-heap", "`PriorityQueue`",
    "Not a queue at all - the smallest comes out first.",
    """
```java
Queue<Integer> pq = new PriorityQueue<>();
pq.offer(5); pq.offer(1); pq.offer(3);
pq.poll();      // 1
pq.poll();      // 3
pq.poll();      // 5
```

Despite the name, a `PriorityQueue` is **not FIFO**. `poll()` always returns the
**smallest** remaining element by natural ordering. It is a binary **heap**:

| Operation | Cost |
|---|---|
| `offer` | O(log n) |
| `poll` | O(log n) |
| `peek` | **O(1)** |

That is the trade that makes it worth having. Keeping a sorted list would give
O(1) peek too, but O(n) insertion; sorting everything at the end is O(n log n)
but cannot answer "what is smallest *right now*".

## The trap: only `poll` is ordered

```java
System.out.println(pq);        // heap order — NOT sorted. Never rely on it.
```

The heap is only *partially* ordered: each parent is smaller than its children,
which is enough to know the root is the minimum and nothing more. `toString`,
the enhanced `for` and `iterator()` all expose that internal array order. **The
only ordered access is repeated `poll()`.** Every exercise here drains rather
than prints for exactly that reason.

**Natural ordering** means `Integer` ascending and `String` alphabetical. A
different order — largest first, or by a field of your own class — needs a
`Comparator`, which is module 20.

**The classic use is "k largest".** Keep a min-heap of size `k`: offer each
element, and whenever the size exceeds `k`, poll away the smallest. What remains
is the k largest, in O(n log k) time and O(k) space — much better than sorting
everything when `n` is huge and `k` is small.

> `PriorityQueue` implements `Queue`, so `offer`/`poll`/`peek` are the same
> methods you already know. Only the *order* they impose is different.
""",
    warmup=[
        _jq("What does `poll()` return from a PriorityQueue of Integers?",
            ["The smallest remaining element", "The first one added",
             "The last one added", "The largest"],
            0,
            "Natural ordering, smallest first. A largest-first heap needs a Comparator."),
        _jq("Why must you never print a PriorityQueue directly?",
            ["toString exposes heap order, which is only partially sorted",
             "It throws",
             "It is always empty",
             "It prints in sorted order, which is fine"],
            0,
            "Only repeated poll() gives ordered access."),
    ],
    exercises=[
        _je("j19-pq-create", "Smallest first",
            "Read `n` numbers and print them in ascending order by draining a heap. "
            "Replace `____` with the declaration of an empty priority queue of "
            "integers.",
            _jscan(_RD_ARR
                   + "        Queue<Integer> pq = new PriorityQueue<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            pq.offer(a[i]);\n"
                     "        }\n"
                     "        while (!pq.isEmpty()) {\n"
                     "            System.out.println(pq.poll());\n"
                     "        }"),
            "Queue<Integer> pq = new PriorityQueue<>();",
            [_acase(a, _nl(*sorted(a)))
             for a in ([5, 1, 3], [7], [2, 2, 1], [-1, 0, 1], [9, 8, 7, 6])],
            hints=["Declare it as `Queue<Integer>` — `PriorityQueue` implements "
                   "`Queue`.",
                   "`Queue<Integer> pq = new PriorityQueue<>();`",
                   "Draining with `poll` gives ascending order.",
                   "Printing the queue itself would give heap order instead, which is "
                   "not sorted."],
            difficulty="Easy"),

        _je("j19-pq-peek", "What is smallest right now",
            "Read the numbers, then print the smallest **without** removing it, then "
            "the size. Replace `____` with the call that inspects the head.",
            _jscan(_RD_ARR
                   + "        Queue<Integer> pq = new PriorityQueue<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            pq.offer(a[i]);\n"
                     "        }\n"
                     "        System.out.println(pq.peek());\n"
                     "        System.out.println(pq.size());"),
            "pq.peek()",
            [_acase(a, _nl(min(a), len(a)))
             for a in ([5, 1, 3], [7], [2, 2, 1], [-1, 0, 1], [9, 8, 7, 6])],
            hints=["`peek` looks at the head without removing it, so the size is "
                   "unchanged.",
                   "`pq.peek()`",
                   "It is O(1) — the minimum is always at the root of the heap.",
                   "`poll` would have removed it and made the size smaller."],
            difficulty="Intro"),

        _jfix("j19-pq-print", "Printing the heap",
              "This prints the priority queue directly, which exposes heap order rather "
              "than sorted order. Rewrite it to drain the queue with `poll`, printing "
              "one number per line in ascending order.",
              _jscan(_RD_ARR
                     + "        Queue<Integer> pq = new PriorityQueue<>();\n"
                       "        for (int i = 0; i < n; i++) {\n"
                       "            pq.offer(a[i]);\n"
                       "        }\n"
                       "        for (int v : pq) {\n"
                       "            System.out.println(v);\n"
                       "        }"),
              _jscan(_RD_ARR
                     + "        Queue<Integer> pq = new PriorityQueue<>();\n"
                       "        for (int i = 0; i < n; i++) {\n"
                       "            pq.offer(a[i]);\n"
                       "        }\n"
                       "        while (!pq.isEmpty()) {\n"
                       "            System.out.println(pq.poll());\n"
                       "        }"),
              [_acase(a, _nl(*sorted(a)))
               for a in ([5, 1, 3], [9, 8, 7, 6], [3, 1, 4, 1, 5],
                         [2, 2, 1], [10, 1, 9, 2])],
              hints=["The enhanced `for` uses `iterator()`, which walks the internal "
                     "array — partially ordered at best.",
                     "The only ordered access is repeated `poll()`.",
                     "Replace the loop with `while (!pq.isEmpty())` and print "
                     "`pq.poll()`.",
                     "This empties the queue, which is the price of ordered access.",
                     "Case one would print `1 5 3` from the iterator and must print "
                     "`1 3 5`."],
              difficulty="Medium"),

        _jch("j19-pq-klargest", "The k largest", "Hard",
             "Read `n` numbers, then `k` (with `1 <= k <= n`). Print the `k` largest "
             "values in ASCENDING order, one per line, keeping a heap of at most `k` "
             "elements.",
             _jscan(_RD_ARR
                    + "        int k = sc.nextInt();\n"
                      "        Queue<Integer> pq = new PriorityQueue<>();\n"
                      "        for (int i = 0; i < n; i++) {\n"
                      "            pq.offer(a[i]);\n"
                      "            if (pq.size() > k) {\n"
                      "                pq.poll();\n"
                      "            }\n"
                      "        }\n"
                      "        while (!pq.isEmpty()) {\n"
                      "            System.out.println(pq.poll());\n"
                      "        }"),
             "        Queue<Integer> pq = new PriorityQueue<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            pq.offer(a[i]);\n"
             "            if (pq.size() > k) {\n"
             "                pq.poll();\n"
             "            }\n"
             "        }\n"
             "        while (!pq.isEmpty()) {\n"
             "            System.out.println(pq.poll());\n"
             "        }",
             [_akcase(a, k, _nl(*sorted(a)[len(a) - k:]))
              for (a, k) in (([5, 1, 3, 9, 7], 2), ([7], 1), ([1, 2, 3, 4], 4),
                             ([4, 4, 4], 2), ([-5, -1, -3], 2))],
             hints=["A MIN-heap capped at size `k` is the trick: the smallest of the "
                    "survivors sits at the head, ready to be discarded.",
                    "Offer every element, then immediately poll if the size has grown "
                    "past `k`.",
                    "Whatever remains is the k largest.",
                    "Draining a min-heap gives ascending order, which is exactly what "
                    "the brief asks for.",
                    "Cost is O(n log k) and space is O(k) — far better than sorting "
                    "everything when n is huge and k is small.",
                    "Duplicates count separately: case four keeps two of the three "
                    "fours."]),
    ],
    quiz=[
        _jq("Which operation on a PriorityQueue is O(1)?",
            ["peek", "offer", "poll", "contains"],
            0,
            "The minimum is always at the root. Insertion and removal are O(log n)."),
        _jq("To keep the k LARGEST elements, what kind of heap do you cap at size k?",
            ["A min-heap - so the smallest survivor is the one you discard",
             "A max-heap",
             "Either works",
             "A sorted list"],
            0,
            "The head of a min-heap is exactly the element least deserving of its "
            "place."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m19_browser(home, cmds):
    back = []
    fwd = []
    cur = home
    out = []
    for c in cmds:
        parts = c.split(" ")
        if parts[0] == "visit":
            back.append(cur)
            cur = parts[1]
            fwd = []
            out.append("at " + cur)
        elif parts[0] == "back":
            if not back:
                out.append("cannot go back")
            else:
                fwd.append(cur)
                cur = back.pop()
                out.append("at " + cur)
        elif parts[0] == "forward":
            if not fwd:
                out.append("cannot go forward")
            else:
                back.append(cur)
                cur = fwd.pop()
                out.append("at " + cur)
        else:
            out.append("unknown")
    out.append("current=" + cur)
    out.append("back=" + str(len(back)) + " forward=" + str(len(fwd)))
    return _nl(*out)


def _m19_case(home, cmds):
    return _case("\n".join([home, str(len(cmds))] + list(cmds)) + "\n",
                 _m19_browser(home, cmds))


_M19_CAP = _jcap(
    "Browser history",
    """
Two stacks and a current page — the structure behind every browser's back and
forward buttons, and the clearest possible demonstration of why LIFO is the
right shape.

## Input

```
<home page>
n
<command>      x n
```

Commands are `visit <page>`, `back`, or `forward`.

## The rules

| Command | Behaviour |
|---|---|
| `visit p` | push the current page onto **back**, move to `p`, and **clear forward** |
| `back` | if back is empty, `cannot go back`; otherwise push current onto **forward** and pop from **back** |
| `forward` | if forward is empty, `cannot go forward`; otherwise push current onto **back** and pop from **forward** |
| anything else | `unknown` |

After a successful move, print `at <page>`.

## Output

One line per command, then:

```
current=<page>
back=<size> forward=<size>
```

## What the hidden cases check

- **`visit` clears the forward stack.** Once you branch off, the pages you had
  gone back from are unreachable — that is exactly how a real browser behaves,
  and forgetting it is the main bug in this problem.
- **Both empty cases are handled** without popping an empty stack.
- **A failed command changes nothing** — no page move, no stack change.
- **The two stacks mirror each other.** Every successful `back` pushes onto
  forward, and every successful `forward` pushes onto back.
""",
    _jch("j19-cap-history", "Browser history", "Hard",
         "Write the whole body where you see `____`: the two stacks, the command loop, "
         "and the two summary lines.",
         _jscan("        String home = sc.nextLine();\n"
                "        int n = Integer.parseInt(sc.nextLine());\n"
                "        Deque<String> back = new ArrayDeque<>();\n"
                "        Deque<String> forward = new ArrayDeque<>();\n"
                "        String cur = home;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            String line = sc.nextLine();\n"
                '            String[] parts = line.split(" ");\n'
                '            if (parts[0].equals("visit") && parts.length == 2) {\n'
                "                back.push(cur);\n"
                "                cur = parts[1];\n"
                "                forward.clear();\n"
                '                System.out.println("at " + cur);\n'
                '            } else if (parts[0].equals("back")) {\n'
                "                if (back.isEmpty()) {\n"
                '                    System.out.println("cannot go back");\n'
                "                } else {\n"
                "                    forward.push(cur);\n"
                "                    cur = back.pop();\n"
                '                    System.out.println("at " + cur);\n'
                "                }\n"
                '            } else if (parts[0].equals("forward")) {\n'
                "                if (forward.isEmpty()) {\n"
                '                    System.out.println("cannot go forward");\n'
                "                } else {\n"
                "                    back.push(cur);\n"
                "                    cur = forward.pop();\n"
                '                    System.out.println("at " + cur);\n'
                "                }\n"
                "            } else {\n"
                '                System.out.println("unknown");\n'
                "            }\n"
                "        }\n"
                '        System.out.println("current=" + cur);\n'
                '        System.out.println("back=" + back.size()\n'
                '            + " forward=" + forward.size());'),
         "        Deque<String> back = new ArrayDeque<>();\n"
         "        Deque<String> forward = new ArrayDeque<>();\n"
         "        String cur = home;\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            String line = sc.nextLine();\n"
         '            String[] parts = line.split(" ");\n'
         '            if (parts[0].equals("visit") && parts.length == 2) {\n'
         "                back.push(cur);\n"
         "                cur = parts[1];\n"
         "                forward.clear();\n"
         '                System.out.println("at " + cur);\n'
         '            } else if (parts[0].equals("back")) {\n'
         "                if (back.isEmpty()) {\n"
         '                    System.out.println("cannot go back");\n'
         "                } else {\n"
         "                    forward.push(cur);\n"
         "                    cur = back.pop();\n"
         '                    System.out.println("at " + cur);\n'
         "                }\n"
         '            } else if (parts[0].equals("forward")) {\n'
         "                if (forward.isEmpty()) {\n"
         '                    System.out.println("cannot go forward");\n'
         "                } else {\n"
         "                    back.push(cur);\n"
         "                    cur = forward.pop();\n"
         '                    System.out.println("at " + cur);\n'
         "                }\n"
         "            } else {\n"
         '                System.out.println("unknown");\n'
         "            }\n"
         "        }\n"
         '        System.out.println("current=" + cur);\n'
         '        System.out.println("back=" + back.size()\n'
         '            + " forward=" + forward.size());',
         [_m19_case(home, cmds) for (home, cmds) in (
             ("home", ["visit a", "visit b", "back", "forward"]),
             ("home", ["back"]),
             ("home", ["visit a", "back", "visit b", "forward"]),
             ("start", ["forward", "visit x", "back", "back"]),
             ("h", ["visit a", "visit b", "back", "back", "forward"]),
         )],
         hints=["Two `Deque<String>` stacks, both `ArrayDeque`, plus a `String cur`.",
                "`push` and `pop` are the stack aliases for `addFirst` and "
                "`removeFirst`.",
                "`visit` must push the CURRENT page (not the new one) onto back, then "
                "move, then clear forward.",
                "`forward.clear()` is the rule people forget — case three depends on "
                "it, where the `forward` after a `visit` must fail.",
                "Check `isEmpty()` before every `pop`, or it throws.",
                "`back` and `forward` are exact mirrors of each other: each pushes "
                "the current page onto the other stack.",
                "A failed command must print its message and change nothing at all.",
                "Compare the verb with `.equals`, and check `parts.length` before "
                "reading `parts[1]`."]),
    example_io="stdin:  home\n        4\n        visit a\n        visit b\n"
               "        back\n        forward\n\n"
               "stdout: at a\n        at b\n        at a\n        at b\n"
               "        current=b\n        back=2 forward=0",
    rubric=[
        "Two `ArrayDeque`s used as stacks, via push and pop.",
        "`visit` pushes the current page onto back before moving.",
        "`visit` clears the forward stack.",
        "Both empty cases print their message and change nothing.",
        "`back` and `forward` are exact mirrors of one another.",
        "`isEmpty()` guards every pop.",
        "An unrecognised command prints `unknown` and changes nothing.",
        "The two summary lines print exactly once, at the end.",
    ],
)


_MODULES.append(_jmod(
    19, 6, "The collections framework",
    "Queues, deques, stacks and heaps",
    "Add and remove at the ends rather than by index: FIFO queues, double-ended "
    "deques, LIFO stacks, and the heap that always hands you the smallest.",
    """
Lists, sets and maps answer *where*, *whether* and *what for*. This module is
about **order of service** — which element comes out next.

A **queue** is FIFO, and its API comes in two families that differ only in how
they fail: `add`/`remove`/`element` throw, and `offer`/`poll`/`peek` return a
value. Prefer the second, because the empty case then reads as an ordinary `if`.

A **deque** does both ends, and that single generalisation covers both classic
structures: insert at the opposite end from removal and you have a queue; insert
at the same end and you have a stack. One method call is the entire difference.

`ArrayDeque` is the implementation for all of it. Notably **not**
`java.util.Stack`, which extends `Vector` and therefore exposes every list
method on your stack — the standard library's own copy of module 14's
`Stack extends ArrayList` mistake, kept only for compatibility.

A **`PriorityQueue`** breaks the pattern: it is a binary heap, `poll` returns the
smallest rather than the oldest, and only `poll` is ordered — `toString` and
iteration expose heap order and must never be relied on. The k-largest idiom, a
min-heap capped at size k, is the reason it earns its place.
""",
    _M19,
    capstone=_M19_CAP,
    objectives=[
        "Use a `Queue` with offer, poll and peek, and say how they differ from add, remove and element.",
        "Explain why `ArrayDeque` forbids null elements.",
        "Use a `Deque` at either end, and turn a queue into a stack by changing one call.",
        "Use a stack for reversal and for bracket matching, including the final emptiness check.",
        "Say why `java.util.Stack` should be avoided.",
        "Use a `PriorityQueue`, and say why only `poll` gives ordered access.",
        "Implement the k-largest idiom with a size-capped min-heap.",
        "Give the cost of offer, poll and peek on a heap.",
    ],
    why="Queues and stacks are the backbone of graph traversal, expression parsing, "
        "undo, scheduling and every job pipeline. Bracket matching and k-largest are "
        "two of the most frequently asked interview problems there are, and both are "
        "short once you reach for the right structure.",
    est_minutes=330,
    glossary=[
        _jg("Queue", "FIFO: elements leave in the order they arrived."),
        _jg("offer / poll / peek", "The value-returning family: false / null / null on "
                                   "failure."),
        _jg("add / remove / element", "The throwing family. Same jobs, different failure "
                                      "behaviour."),
        _jg("Deque", "A double-ended queue - add and remove at either end."),
        _jg("ArrayDeque", "A circular array. The recommended implementation of both "
                          "Queue and Deque, and of stacks."),
        _jg("LIFO", "Last in, first out - a stack. Insert and remove at the same end."),
        _jg("push / pop", "Deque aliases for addFirst / removeFirst, so stack code reads "
                          "like stack code."),
        _jg("PriorityQueue", "A binary heap. poll() returns the smallest by natural "
                             "ordering, not the oldest."),
        _jg("heap order", "The partial ordering a heap maintains: each parent below its "
                          "children. Not sorted, which is why toString is unreliable."),
        _jg("k-largest idiom", "A min-heap capped at size k: offer everything, poll "
                               "whenever the size exceeds k. O(n log k)."),
    ],
    cheatsheet="""
```java
// --- Queue (FIFO) ---------------------------------------------------------
Queue<String> q = new ArrayDeque<>();
q.offer(x);   q.poll();   q.peek();       // false / null / null on failure
q.add(x);     q.remove();  q.element();   // THROW on failure
while (!q.isEmpty()) process(q.poll());   // the standard drain

// --- Deque (both ends) ----------------------------------------------------
Deque<String> d = new ArrayDeque<>();
d.addFirst(x)  d.addLast(x)
d.pollFirst()  d.pollLast()
d.peekFirst()  d.peekLast()

// queue  = addLast  + pollFirst      (opposite ends)
// stack  = addFirst + pollFirst      (same end)

// --- Stack ----------------------------------------------------------------
Deque<Character> s = new ArrayDeque<>();
s.push(c);          // addFirst
s.peek();           // null if empty
s.pop();            // THROWS if empty -> guard with isEmpty()
// NEVER java.util.Stack: it extends Vector and exposes add(0, x)

// --- bracket matching -----------------------------------------------------
// 1. opener  -> push
// 2. closer  -> stack must be non-empty AND top must match; pop
// 3. AT THE END the stack must be empty      <- the forgotten rule

// --- PriorityQueue (a heap) -----------------------------------------------
Queue<Integer> pq = new PriorityQueue<>();
pq.offer(x);        // O(log n)
pq.poll();          // O(log n) - the SMALLEST
pq.peek();          // O(1)
System.out.println(pq);   // HEAP order. Never rely on it. Drain instead.

// k largest, O(n log k):
for (int v : a) { pq.offer(v); if (pq.size() > k) pq.poll(); }
```
""",
    self_check=[
        "Can you say what each of poll, remove, peek and element does on an empty structure?",
        "Can you explain why ArrayDeque forbids null?",
        "Can you turn a Deque-based queue into a stack by changing one call?",
        "Can you write bracket matching including the end-of-input check?",
        "Can you say why `([)]` is the input that matters?",
        "Can you explain why java.util.Stack is a mistake, in module 14's terms?",
        "Can you say why printing a PriorityQueue is unreliable?",
        "Can you implement k-largest with a size-capped heap, and give its cost?",
    ],
    review=[
        _jq("```java\nQueue<Integer> q = new ArrayDeque<>();\nq.offer(1); q.offer(2);\nSystem.out.println(q.poll());\n```\nWhat prints?",
            ["1", "2", "null", "It throws"],
            0,
            "FIFO: the first one added is the first out."),
        _jq("Which turns a Deque into a stack?",
            ["Inserting at the same end you remove from",
             "Using offer instead of add",
             "Switching to LinkedList",
             "Calling reverse()"],
            0,
            "Opposite ends is FIFO; the same end is LIFO."),
        _jq("```java\nQueue<Integer> pq = new PriorityQueue<>();\npq.offer(5); pq.offer(1); pq.offer(3);\nSystem.out.println(pq.poll());\n```\nWhat prints?",
            ["1", "5", "3", "The smallest is not guaranteed"],
            0,
            "poll() always returns the smallest by natural ordering, regardless of "
            "insertion order."),
        _jq("In the capstone, why must `visit` clear the forward stack?",
            ["Branching to a new page makes the pages you had gone back from unreachable",
             "To free memory",
             "Because forward would otherwise throw",
             "It should not be cleared"],
            0,
            "It is exactly how a real browser behaves, and forgetting it is the main "
            "bug in this problem."),
    ],
    milestone="You can choose a structure by the order it serves things in, write the "
              "two classic stack problems from memory, and reach for a heap when you "
              "need the extreme element rather than all of them.",
))
