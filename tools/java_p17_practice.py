# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 17 practice - lists.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[17]`.
#
# Sets and Maps are module 18, queues module 19, Comparable/Comparator and
# Collections.* module 20 - so nothing here sorts, and every de-duplication is
# done with a list.
#
# A List's toString is specified as "[a, b, c]", so printing one directly is
# safe to assert on.
# ---------------------------------------------------------------------------


_RD_WORDS = ("        int n = sc.nextInt();\n"
             "        List<String> words = new ArrayList<>();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            words.add(sc.next());\n"
             "        }\n")

_RD_NUMS = ("        int n = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")


def _p17ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_WORDS):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


def _wcase(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _wkcase(ws, k, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(k)]), out)


def _ncase(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jlist(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


_WS = (["a", "b", "c"], ["solo"], ["x", "x", "y"], ["p", "q"],
       ["one", "two", "three", "four"])


# --- Family A - building and reading -----------------------------------------

_P17_A = _jfam(
    "p17-build", "Building and reading",
    "The API you will use every day.",
    """
```java
List<String> names = new ArrayList<>();     // interface left, implementation right
names.add("Ada");            // append
names.add(0, "Bo");          // insert, shifting the rest right
names.get(0);                // read
names.set(0, "Cy");          // overwrite, returns the OLD value
names.remove(0);             // remove by index, shifting left
names.size();                // how many
names.isEmpty();
names.contains("Ada");       // uses equals, O(n)
names.indexOf("Ada");        // first index, or -1
```

**Three words for one idea**, and getting them confused is a compile error every
Java programmer meets:

| Thing | Ask with |
|---|---|
| array | `a.length` — a field |
| `String` | `s.length()` — a method |
| collection | `list.size()` |

**`contains` and `indexOf` use `equals`**, so they work on `String` out of the
box and on your own classes only if you overrode it (module 13).

**Printing a list is specified**: `[Ada, Bo]`, brackets, comma and space. That
makes it safe to assert on, which is why these exercises print lists directly.

**Declare the variable as `List`.** The implementation is a decision you may
want to revisit; the interface is the contract your code depends on. Module 14's
argument, applied to the collection you use most.
""",
    [
        _p17ex("j17-pr-build", "Read them in", "Intro",
               "Print the list, then its size.",
               """
        System.out.println(words);
        System.out.println(words.size());
""",
               [_wcase(ws, _nl(_jlist(ws), len(ws))) for ws in _WS],
               ["The list is already built by the given code.",
                "Printing it directly gives the `[a, b, c]` form.",
                "`size()` for the count — not `.length` and not `.length()`.",
                "Two lines of output."]),

        _p17ex("j17-pr-ends", "First and last", "Intro",
               "Print the first element, then the last.",
               """
        System.out.println(words.get(0));
        System.out.println(words.get(words.size() - 1));
""",
               [_wcase(ws, _nl(ws[0], ws[-1])) for ws in _WS],
               ["`get(0)` is the first, exactly like `a[0]`.",
                "The last index is `size() - 1`.",
                "A one-element list has the same element at both ends — case two "
                "checks it.",
                "There is no `getLast()` on `List` (that is `Deque`, module 19)."]),

        _p17ex("j17-pr-indexof", "Where is it?", "Easy",
               "Read the words, then one more to search for. Print its first index, or "
               "`-1`.",
               """
        String q = sc.next();
        System.out.println(words.indexOf(q));
""",
               [_wkcase(ws, q, ws.index(q) if q in ws else -1)
                for (ws, q) in ((["a", "b", "c"], "b"), (["solo"], "solo"),
                                (["x", "x", "y"], "x"), (["p", "q"], "z"),
                                (["one", "two"], "two"))],
               ["`indexOf` returns the FIRST index, or `-1` when absent — the same "
                "convention as `String.indexOf`.",
                "It compares with `equals`, so it works on Strings correctly.",
                "No loop is needed.",
                "Case three has two matches and must report the first."]),

        _p17ex("j17-pr-set", "Overwrite one", "Easy",
               "Read the words, then an index and a replacement word. Print the value "
               "that was there before, then the list.",
               """
        int at = sc.nextInt();
        String w = sc.next();
        System.out.println(words.set(at, w));
        System.out.println(words);
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), f"{at} {w}"]),
                      _nl(ws[at], _jlist(ws[:at] + [w] + ws[at + 1:])))
                for (ws, at, w) in ((["a", "b", "c"], 1, "z"),
                                    (["solo"], 0, "z"),
                                    (["x", "y"], 1, "w"),
                                    (["p", "q", "r"], 2, "s"),
                                    (["one", "two"], 0, "zero"))],
               ["`set` overwrites rather than inserting, so the size does not change.",
                "It RETURNS the value that was there — print that first.",
                "`add(index, element)` would insert instead and grow the list.",
                "The index must already exist; `set` cannot extend the list."]),

        _p17ex("j17-pr-clear", "Empty it out", "Easy",
               "Print the size, then empty the list, then print the size and whether it "
               "is empty.",
               """
        System.out.println(words.size());
        words.clear();
        System.out.println(words.size());
        System.out.println(words.isEmpty());
""",
               [_wcase(ws, _nl(len(ws), 0, "true")) for ws in _WS],
               ["`clear()` removes everything and returns nothing.",
                "The size afterwards is `0` for every input.",
                "`isEmpty()` reads better than `size() == 0` and means the same "
                "thing.",
                "Print the boolean directly."]),
    ])


# --- Family B - generics and boxing -------------------------------------------

_P17_B = _jfam(
    "p17-boxing", "Generics and boxing",
    "`List<int>` does not exist, and that has consequences.",
    """
Collections hold **objects**, so a type argument must be a reference type:

```java
List<Integer> nums = new ArrayList<>();     // not List<int>
nums.add(5);                                // autoboxed:   int -> Integer
int first = nums.get(0);                    // auto-unboxed: Integer -> int
```

Autoboxing hides the conversion almost everywhere. The three places it does not:

**1. `remove(int)` versus `remove(Object)`.**

```java
nums.remove(1);                      // removes INDEX 1
nums.remove(Integer.valueOf(1));     // removes the VALUE 1
```

Both overloads exist and an `int` literal picks the index one. `List<Integer>` is
the only element type where this ambiguity arises, which is exactly why it
catches people.

**2. `==` on wrappers compares references.** Java caches boxed values from
`-128` to `127`, so it appears to work for small numbers and fails for large
ones:

```java
Integer a = 127, b = 127;   a == b;   // true
Integer x = 128, y = 128;   x == y;   // FALSE
```

Use `.equals`. It is module 6's `String` pool trap in a new costume.

**3. Unboxing `null` throws.** An `Integer` may be `null`; an `int` may not. So
`int v = list.get(i);` throws `NullPointerException` on a null element.

**Generics are erased at run time.** The compiler checks that only `Integer`s go
into a `List<Integer>` and then removes the type information — which is why you
cannot write `new T[]`.
""",
    [
        _p17ex("j17-pr-nums", "A list of numbers", "Intro",
               "Print the list, then the total of its elements.",
               """
        int total = 0;
        for (int v : nums) {
            total += v;
        }
        System.out.println(nums);
        System.out.println(total);
""",
               [_ncase(xs, _nl(_jlist(xs), sum(xs)))
                for xs in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [5, 4, 3])],
               ["The enhanced `for` may declare an `int` and let Java unbox each "
                "element.",
                "`total += v;` then works on primitives.",
                "Print the list first, then the total.",
                "This would throw on a `null` element — which cannot happen here, but "
                "is worth knowing."],
               read=_RD_NUMS),

        _p17ex("j17-pr-remove-index", "Remove by index", "Easy",
               "Read the numbers, then `k`. Remove the element AT index `k` and print "
               "the list.",
               """
        int k = sc.nextInt();
        nums.remove(k);
        System.out.println(nums);
""",
               [_case("\n".join([str(len(xs)), " ".join(str(x) for x in xs), str(k)]),
                      _jlist(xs[:k] + xs[k + 1:]))
                for (xs, k) in (([10, 20, 30], 1), ([7], 0), ([1, 2], 1),
                                ([5, 5, 5], 0), ([1, 2, 3, 4], 3))],
               ["`k` is an `int`, so `nums.remove(k)` picks the remove-by-INDEX "
                "overload.",
                "That is what the brief wants here.",
                "The elements after it shift left, so the size drops by one.",
                "Case one removes the `20`, not the value `1`."],
               read=_RD_NUMS),

        _p17ex("j17-pr-remove-value", "Remove by value", "Medium",
               "Read the numbers, then `k`. Remove the first element whose VALUE is `k` "
               "and print the list. If `k` is absent, the list is unchanged.",
               """
        int k = sc.nextInt();
        nums.remove(Integer.valueOf(k));
        System.out.println(nums);
""",
               [_case("\n".join([str(len(xs)), " ".join(str(x) for x in xs), str(k)]),
                      _jlist(xs[:xs.index(k)] + xs[xs.index(k) + 1:]
                             if k in xs else xs))
                for (xs, k) in (([10, 20, 30], 20), ([7], 7), ([1, 2, 3], 9),
                                ([5, 5, 5], 5), ([0, 1], 0))],
               ["`nums.remove(k)` with an `int` would remove by index — the wrong "
                "overload.",
                "Force the object overload by boxing explicitly.",
                "`nums.remove(Integer.valueOf(k))`",
                "It removes only the FIRST match and returns a boolean you can "
                "ignore.",
                "Case three removes nothing at all."],
               read=_RD_NUMS),

        _p17ex("j17-pr-equals-wrappers", "Compare boxed values", "Medium",
               "Read two integers into `Integer` variables. Print `a == b`, then "
               "`a.equals(b)`.",
               """
        Integer x = sc.nextInt();
        Integer y = sc.nextInt();
        System.out.println(x == y);
        System.out.println(x.equals(y));
""",
               [_case(f"{a} {b}", _nl(_jbool(a == b and -128 <= a <= 127),
                                      _jbool(a == b)))
                for (a, b) in ((127, 127), (128, 128), (5, 6), (1000, 1000),
                               (-129, -129))],
               ["Declare both as `Integer`, not `int`, so boxing is visible.",
                "`==` compares references. Java caches `-128` to `127`, so case one "
                "prints `true` and case two prints `false` — for identical-looking "
                "code.",
                "`.equals` compares values and is right every time.",
                "That gap is why the rule is 'always use equals for wrappers'.",
                "Cases four and five are outside the cache in both directions."],
               read=""),

        _p17ex("j17-pr-max-boxed", "Largest in a list", "Easy",
               "Print the largest number in the list. Do not sort.",
               """
        int best = nums.get(0);
        for (int v : nums) {
            if (v > best) {
                best = v;
            }
        }
        System.out.println(best);
""",
               [_ncase(xs, max(xs))
                for xs in ([1, 2, 3], [7], [-2, -3, -1], [5, 4, 3], [0, 0])],
               ["Module 1's running maximum, over a list instead of an array.",
                "Seed with `nums.get(0)`, never with `0` — case three is all "
                "negative.",
                "The enhanced `for` unboxes each element into an `int`.",
                "`Collections.max` exists but is module 20."],
               read=_RD_NUMS),
    ])


# --- Family C - iterating and removing ----------------------------------------

_P17_C = _jfam(
    "p17-iterate", "Iterating, and removing while you do",
    "Three loops, and the exception that catches everyone once.",
    """
```java
for (String s : names) { ... }                    // default — no index needed
for (int i = 0; i < names.size(); i++) { ... }    // when you need the position

Iterator<String> it = names.iterator();           // when you need to REMOVE
while (it.hasNext()) {
    String s = it.next();                         // returns AND advances
    if (...) it.remove();
}
```

**Modifying a list while an iterator walks it throws
`ConcurrentModificationException`** — and the enhanced `for` is an iterator
underneath, so this throws:

```java
for (String s : names) {
    if (s.equals("x")) names.remove(s);           // throws
}
```

No threads are involved despite the name. It is the collection saying *you
changed me while I was walking you*.

**The three safe removals:**

1. **`it.remove()`** on an explicit `Iterator` — the iterator stays consistent.
   It removes whatever `next()` last returned, and must be called exactly once
   per `next()`.
2. **A backwards index loop** — removing at `i` never disturbs anything before
   `i`.
3. **Build a new list** of survivors. Usually the clearest, and it leaves the
   original intact.

**A forward index loop that removes is the silent one.** It does not throw; it
just skips. After `remove(i)` the next element slides into position `i`, and the
loop then moves to `i + 1` — so two adjacent matches lose the second. That bug
survives casual testing, because it only shows up on adjacent duplicates.
""",
    [
        _p17ex("j17-pr-foreach", "One per line", "Intro",
               "Print each word on its own line.",
               """
        for (String s : words) {
            System.out.println(s);
        }
""",
               [_wcase(ws, _nl(*ws)) for ws in _WS],
               ["The enhanced `for` reads 'for each String s in words'.",
                "No index is needed at all.",
                "`for (String s : words) {`",
                "One line of output per element."]),

        _p17ex("j17-pr-numbered", "Number them", "Easy",
               "Print each word as `<index>: <word>`, one per line.",
               """
        for (int i = 0; i < words.size(); i++) {
            System.out.println(i + ": " + words.get(i));
        }
""",
               [_wcase(ws, _nl(*[f"{i}: {w}" for (i, w) in enumerate(ws)]))
                for ws in _WS],
               ["You need the position, so an index loop is right.",
                "The bound is `words.size()`.",
                "Read each element with `get(i)`.",
                "Mind the separator: a colon and then a space."]),

        _p17ex("j17-pr-iterator-remove", "Remove as you walk", "Medium",
               "Read the words, then one to drop. Remove EVERY occurrence using an "
               "explicit `Iterator`, then print the list.",
               """
        String drop = sc.next();
        Iterator<String> it = words.iterator();
        while (it.hasNext()) {
            if (it.next().equals(drop)) {
                it.remove();
            }
        }
        System.out.println(words);
""",
               [_wkcase(ws, d, _jlist([w for w in ws if w != d]))
                for (ws, d) in ((["x", "x", "a"], "x"), (["a", "x", "b"], "x"),
                                (["solo"], "solo"), (["p", "q"], "z"),
                                (["x", "y", "x"], "x"))],
               ["Removing through the LIST here would throw "
                "ConcurrentModificationException.",
                "`it.remove()` removes whatever `next()` last returned, so call "
                "`next()` exactly once per iteration.",
                "Storing the result of `next()` or comparing it inline both work — "
                "just do not call it twice.",
                "Case one has two adjacent matches, which is where a forward index "
                "loop would fail silently.",
                "Case three removes everything and prints `[]`."]),

        _p17ex("j17-pr-backwards", "Walk backwards instead", "Medium",
               "Same task, but use a BACKWARDS index loop rather than an iterator.",
               """
        String drop = sc.next();
        for (int i = words.size() - 1; i >= 0; i--) {
            if (words.get(i).equals(drop)) {
                words.remove(i);
            }
        }
        System.out.println(words);
""",
               [_wkcase(ws, d, _jlist([w for w in ws if w != d]))
                for (ws, d) in ((["x", "x", "a"], "x"), (["a", "x", "b"], "x"),
                                (["solo"], "solo"), (["p", "q"], "z"),
                                (["x", "y", "x"], "x"))],
               ["Start at `size() - 1` and count down to `0`.",
                "Removing at `i` shifts only the elements AFTER `i`, which you have "
                "already passed.",
                "So nothing is ever skipped, unlike a forward loop.",
                "`remove(i)` here is remove-by-index, which is what you want.",
                "Compare with the iterator version: same answer, different route."]),

        _p17ex("j17-pr-newlist", "Build the survivors", "Easy",
               "Same task again, but build a NEW list of the words that are not "
               "dropped, and print that. The original must be printed unchanged first.",
               """
        String drop = sc.next();
        System.out.println(words);
        List<String> kept = new ArrayList<>();
        for (String s : words) {
            if (!s.equals(drop)) {
                kept.add(s);
            }
        }
        System.out.println(kept);
""",
               [_wkcase(ws, d, _nl(_jlist(ws), _jlist([w for w in ws if w != d])))
                for (ws, d) in ((["x", "x", "a"], "x"), (["a", "x", "b"], "x"),
                                (["solo"], "solo"), (["p", "q"], "z"),
                                (["x", "y", "x"], "x"))],
               ["Nothing is removed at all, so no iterator can be upset.",
                "Print the original BEFORE building the new list.",
                "Keep the words that do NOT match, so the test is `!s.equals(drop)`.",
                "This is usually the clearest of the three, and it leaves the "
                "original available.",
                "Case three keeps nothing and prints `[]`."]),
    ])


# --- Family D - transforming ---------------------------------------------------

_P17_D = _jfam(
    "p17-transform", "Transforming a list",
    "Module 1 and 4's array patterns, with a list underneath.",
    """
Nothing new here — the loops are the ones you already know, with `get(i)` where
`a[i]` used to be and `size()` where `length` used to be. What changes is that
the output list does **not** need its length decided in advance:

```java
List<String> out = new ArrayList<>();
for (String s : in) {
    if (keep(s)) out.add(s);        // no write cursor, no counting pass
}
```

Module 4's two-cursor compaction existed because an array's length is fixed. With
a list, `add` is the whole thing.

**In place or into a new list?** The same question as module 1's aliasing
lesson. `set(i, x)` modifies the original; building a second list leaves it
intact. Say which you want before you start.

**`List<String> b = a;` is an alias, not a copy.** Both names reach the same
list, and adding through either is visible through both. A real copy is
`new ArrayList<>(a)`.

**Reversing** has no `List` method — `Collections.reverse` exists but is module
20, so the two-pointer swap from module 4 is what you write here, with
`set` doing the assignment.
""",
    [
        _p17ex("j17-pr-upper", "Shout them", "Intro",
               "Print a new list with every word in upper case. The original is "
               "printed first, unchanged.",
               """
        System.out.println(words);
        List<String> loud = new ArrayList<>();
        for (String s : words) {
            loud.add(s.toUpperCase());
        }
        System.out.println(loud);
""",
               [_wcase(ws, _nl(_jlist(ws), _jlist([w.upper() for w in ws])))
                for ws in _WS],
               ["Build a second list and `add` the transformed values.",
                "`toUpperCase()` returns a new String; it cannot modify one.",
                "Print the original first to prove it was not touched.",
                "No length needs deciding in advance — that is the advantage over an "
                "array."]),

        _p17ex("j17-pr-filter-length", "Only the long ones", "Easy",
               "Read the words, then `k`. Print a list of the words with more than `k` "
               "characters, in their original order.",
               """
        int k = sc.nextInt();
        List<String> kept = new ArrayList<>();
        for (String s : words) {
            if (s.length() > k) {
                kept.add(s);
            }
        }
        System.out.println(kept);
""",
               [_wkcase(ws, k, _jlist([w for w in ws if len(w) > k]))
                for (ws, k) in ((["a", "bb", "ccc"], 1), (["solo"], 10),
                                (["x", "y"], 0), (["one", "two", "three"], 3),
                                (["p"], 1))],
               ["One pass, one `if`, one `add`.",
                "**Strictly** more than `k`, so a word of exactly `k` characters is "
                "excluded.",
                "Case two keeps nothing and prints `[]`.",
                "The order of the survivors is the original order, because you add "
                "them as you meet them."],
               read=_RD_WORDS),

        _p17ex("j17-pr-reverse-list", "Reverse it in place", "Medium",
               "Reverse the list in place using `set`, then print it. "
               "`Collections.reverse` is module 20 — do it yourself.",
               """
        for (int i = 0; i < words.size() / 2; i++) {
            String tmp = words.get(i);
            words.set(i, words.get(words.size() - 1 - i));
            words.set(words.size() - 1 - i, tmp);
        }
        System.out.println(words);
""",
               [_wcase(ws, _jlist(list(reversed(ws)))) for ws in _WS],
               ["Module 4's two-pointer swap, with `get`/`set` instead of `a[i]`.",
                "Stop at `size() / 2`, or every pair is swapped twice and nothing "
                "changes.",
                "The partner of `i` is `size() - 1 - i`.",
                "A swap still needs a temporary variable.",
                "Odd lengths need no special case — the middle element pairs with "
                "itself."]),

        _p17ex("j17-pr-dedupe", "Drop the repeats", "Medium",
               "Print a list of the words with duplicates removed, keeping the FIRST "
               "occurrence of each and the original order. Sets are module 18 — use "
               "`contains`.",
               """
        List<String> seen = new ArrayList<>();
        for (String s : words) {
            if (!seen.contains(s)) {
                seen.add(s);
            }
        }
        System.out.println(seen);
""",
               [_wcase(ws, _jlist([w for (i, w) in enumerate(ws) if w not in ws[:i]]))
                for ws in (["a", "b", "a"], ["solo"], ["x", "x", "x"],
                           ["p", "q", "r"], ["a", "b", "a", "b"])],
               ["`contains` on the output list answers 'have I kept this already'.",
                "It uses `equals`, so it compares the text correctly.",
                "Add only when it is not already there, which keeps the first "
                "occurrence.",
                "This is O(n^2), because each `contains` is a scan. Module 18's "
                "`HashSet` makes it O(n) — and that comparison is the point of "
                "meeting it this way first."]),

        _p17ex("j17-pr-interleave-lists", "Alternate two lists", "Hard",
               "Read two lists of words. Print a single list alternating between them, "
               "starting with the first; when one runs out, append the rest of the "
               "other.",
               """
        int m = sc.nextInt();
        List<String> other = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            other.add(sc.next());
        }
        List<String> out = new ArrayList<>();
        int limit = words.size();
        if (other.size() > limit) {
            limit = other.size();
        }
        for (int i = 0; i < limit; i++) {
            if (i < words.size()) {
                out.add(words.get(i));
            }
            if (i < other.size()) {
                out.add(other.get(i));
            }
        }
        System.out.println(out);
""",
               [_case("\n".join([str(len(a)), " ".join(a), str(len(b)), " ".join(b)]),
                      _jlist([x for i in range(max(len(a), len(b)))
                              for x in ([a[i]] if i < len(a) else [])
                              + ([b[i]] if i < len(b) else [])]))
                for (a, b) in ((["a", "b"], ["x", "y"]),
                               (["a"], ["x", "y", "z"]),
                               (["a", "b", "c"], ["x"]),
                               (["p"], ["q"]),
                               (["1", "2"], ["3", "4", "5", "6"]))],
               ["Loop up to the LONGER of the two sizes.",
                "Guard each `add` with its own bounds check, so the shorter list "
                "simply stops contributing.",
                "That handles the leftover tail with no second loop.",
                "`Math.max` would tidy the limit calculation; the explicit `if` keeps "
                "it obvious.",
                "The second list is read after the first, with its own count."]),
    ])


# --- Family E - implementations and copying ------------------------------------

_P17_E = _jfam(
    "p17-impl", "Implementations, copies and views",
    "Same interface, different costs — and what is not really a list.",
    """
| | `ArrayList` | `LinkedList` |
|---|---|---|
| `get(i)` | **O(1)** | O(n) |
| `add` at the end | O(1)* | O(1) |
| `add(0, x)` / `remove(0)` | O(n) | **O(1)** |
| Memory per element | low | higher |

\\* amortised — occasional resizes averaged over many adds

**`ArrayList` is the default and it is not close.** Random access dominates real
code, and contiguous memory is far friendlier to the CPU cache than chasing node
pointers. Because both implement `List`, switching is one line.

**The trap is an index loop over a `LinkedList`:**

```java
for (int i = 0; i < list.size(); i++) process(list.get(i));   // O(n^2)!
```

Each `get(i)` walks from an end. The enhanced `for` avoids it entirely, which is
another reason to prefer it.

**Copying versus aliasing** — module 1's lesson again:

```java
List<String> b = a;                      // ALIAS: one list, two names
List<String> b = new ArrayList<>(a);     // a real (shallow) copy
```

**Two things that look like lists and are not:**

- **`Arrays.asList(...)`** is a fixed-size *view* backed by the array. `set`
  works; `add` and `remove` throw `UnsupportedOperationException`.
- **`List.of(...)`** is fully immutable — even `set` throws.

For a modifiable copy of either: `new ArrayList<>(List.of(...))`.
""",
    [
        _p17ex("j17-pr-linked", "The other implementation", "Intro",
               "Build the same words into a `LinkedList` instead and print it and its "
               "size. Only the constructor differs.",
               """
        List<String> other = new LinkedList<>(words);
        System.out.println(other);
        System.out.println(other.size());
""",
               [_wcase(ws, _nl(_jlist(ws), len(ws))) for ws in _WS],
               ["Every implementation has a constructor taking another collection.",
                "`new LinkedList<>(words)` copies the elements across.",
                "The variable is still declared as `List`, so nothing else changes.",
                "That is the payoff of programming to the interface."]),

        _p17ex("j17-pr-alias", "Two names, one list", "Medium",
               "Take a second reference to the same list (not a copy), add the word "
               "`extra` through it, then print BOTH — they will match.",
               """
        List<String> same = words;
        same.add("extra");
        System.out.println(words);
        System.out.println(same);
""",
               [_wcase(ws, _nl(_jlist(list(ws) + ["extra"]),
                               _jlist(list(ws) + ["extra"]))) for ws in _WS],
               ["Plain assignment copies the REFERENCE, not the contents.",
                "So both names reach one list, and the addition is visible through "
                "both.",
                "The two printed lines are always identical.",
                "This is module 1's array aliasing, with a collection."]),

        _p17ex("j17-pr-copy", "A real copy", "Medium",
               "Make an independent copy, add `extra` to the COPY only, then print the "
               "original and then the copy.",
               """
        List<String> copy = new ArrayList<>(words);
        copy.add("extra");
        System.out.println(words);
        System.out.println(copy);
""",
               [_wcase(ws, _nl(_jlist(ws), _jlist(list(ws) + ["extra"])))
                for ws in _WS],
               ["`List<String> copy = words;` would alias — you need a new object.",
                "The `ArrayList` constructor takes another collection and copies its "
                "elements.",
                "`new ArrayList<>(words)`",
                "It is a SHALLOW copy: a new list holding the same element "
                "references. For immutable `String`s that is enough.",
                "The first line must be unchanged."]),

        _p17ex("j17-pr-fixed-size", "The list that will not grow", "Medium",
               "Read one word. Build a modifiable list from `Arrays.asList(\"a\", "
               "\"b\")`, add the word, and print it. `Arrays.asList` alone is "
               "fixed-size, so it must be wrapped.",
               """
        String w = sc.next();
        List<String> fixed = new ArrayList<>(Arrays.asList("a", "b"));
        fixed.add(w);
        System.out.println(fixed);
""",
               [_case(w, f"[a, b, {w}]") for w in ("c", "z", "x", "hello", "q")],
               ["`Arrays.asList` returns a fixed-size view backed by the array — "
                "`add` throws `UnsupportedOperationException` on it.",
                "Copy it into a genuine `ArrayList` with the collection constructor.",
                "`new ArrayList<>(Arrays.asList(\"a\", \"b\"))`",
                "`List.of(...)` is stricter still: even `set` throws.",
                "Then `add` works normally."],
               read=""),

        _p17ex("j17-pr-swap-impl", "Same code, either implementation", "Hard",
               "Read the words, then `0` or `1`. Build an `ArrayList` for `0` and a "
               "`LinkedList` for `1` — into the SAME `List` variable — then add `end`, "
               "insert `start` at the front, and print the result.",
               """
        int kind = sc.nextInt();
        List<String> chosen;
        if (kind == 0) {
            chosen = new ArrayList<>(words);
        } else {
            chosen = new LinkedList<>(words);
        }
        chosen.add("end");
        chosen.add(0, "start");
        System.out.println(chosen);
""",
               [_wkcase(ws, k, _jlist(["start"] + list(ws) + ["end"]))
                for (ws, k) in ((["a", "b"], 0), (["a", "b"], 1), (["solo"], 0),
                                (["x", "y", "z"], 1), (["p"], 1))],
               ["Declare `chosen` as `List<String>` once, before the `if`.",
                "Both branches assign a different implementation to it.",
                "Every line after that is identical — which is the whole point.",
                "The output is the same for both, because the interface is the same. "
                "Only the COSTS differ: `add(0, x)` is O(n) on the ArrayList and O(1) "
                "on the LinkedList.",
                "Java's definite-assignment rule is satisfied because both branches "
                "assign."]),
    ])


_PRACTICE[17] = [_P17_A, _P17_B, _P17_C, _P17_D, _P17_E]
