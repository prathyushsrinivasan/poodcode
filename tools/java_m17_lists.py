# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 17 - Lists.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Opens Part 6. `ArrayList`, `LinkedList`, `List<` and `Iterator` become legal
# at this module; Sets and Maps are 18, Queues and Deques are 19, and
# `Comparable` / `Comparator` / `Collections.` are 20. Lambdas and streams stay
# banned course-wide (Part 8 is not authored).
#
# OUTPUT STABILITY: a List's toString is specified as "[a, b, c]", so printing a
# list directly is safe to assert on. (Sets and Maps are not, which is why
# module 18 is careful about iteration order.)
# ---------------------------------------------------------------------------

_M17 = []


# --- 17.1 ArrayList ---------------------------------------------------------

_M17.append(_jlesson(
    "m17-arraylist", "`ArrayList`",
    "An array that grows.",
    """
An array's length is fixed the moment it is created. Module 12's `Playlist` had
to take a capacity up front and refuse anything past it — which is exactly the
problem `ArrayList` solves.

```java
List<String> names = new ArrayList<>();
names.add("Ada");
names.add("Bo");
System.out.println(names.size());     // 2
System.out.println(names.get(0));     // Ada
System.out.println(names);            // [Ada, Bo]
```

**Declare the variable as `List`, construct an `ArrayList`.** That is module
14's "program to an interface" rule applied: `List` is the contract, `ArrayList`
one implementation. Swapping to a `LinkedList` later then changes one line.

The `<>` on the right is the **diamond**: Java infers the type argument from the
left-hand side, so you write it once.

**The methods worth knowing cold:**

| Call | Does |
|---|---|
| `add(x)` | append |
| `add(i, x)` | insert at `i`, shifting the rest right |
| `get(i)` | read |
| `set(i, x)` | overwrite, returns the old value |
| `remove(i)` | remove by **index**, shifting left |
| `size()` | how many |
| `isEmpty()` | `size() == 0` |
| `contains(x)` | uses `equals`, not `==` |
| `indexOf(x)` | first index, or `-1` |
| `clear()` | empty it |

**Note the naming inconsistency**, which trips everyone once: arrays use
`a.length`, `String` uses `s.length()`, and collections use `list.size()`. Three
words for one idea.

**`contains` and `indexOf` use `equals`.** So they work correctly on `String`
and on your own classes *only if* you overrode `equals` — module 13's lesson,
now with consequences.

**Printing a list is specified**: `[Ada, Bo]`, with comma and space. You can
assert on it, which is why every exercise here does.
""",
    warmup=[
        _jq("Why declare the variable as `List` rather than `ArrayList`?",
            ["It is the interface, so the implementation can be swapped without changing callers",
             "It is faster",
             "ArrayList cannot be a variable type",
             "To avoid generics"],
            0,
            "Module 14's 'program to an interface' rule, applied to the collections "
            "framework."),
        _jq("Which does `contains` use to compare?",
            ["equals", "==", "compareTo", "hashCode only"],
            0,
            "Which is why your own classes need an `equals` override to work properly "
            "inside a collection."),
    ],
    exercises=[
        _je("j17-al-create", "Make one and fill it",
            "Read `n` words and print the list. Replace `____` with the declaration "
            "that creates an empty list of strings.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(names);"),
            "List<String> names = new ArrayList<>();",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), "[" + ", ".join(ws) + "]")
             for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                        ["one", "two", "three", "four"])],
            hints=["Declare the variable as the interface `List<String>`.",
                   "Construct the implementation: `new ArrayList<>()`.",
                   "The `<>` diamond infers `String` from the left-hand side.",
                   "`List<String> names = new ArrayList<>();`"],
            difficulty="Intro"),

        _je("j17-al-size", "How many, and what is first",
            "Print the list's size, then its first element. Replace `____` with the "
            "call that reports how many elements it holds.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(names.size());\n"
                   "        System.out.println(names.get(0));"),
            "names.size()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(len(ws), ws[0]))
             for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                        ["one", "two", "three"])],
            hints=["Arrays use `.length`, Strings use `.length()`, collections use "
                   "something else again.",
                   "`names.size()`",
                   "`get(0)` reads the first element, exactly like `a[0]`."],
            difficulty="Intro"),

        _jfix("j17-al-remove-shift", "Removing while counting up",
              "This should remove every occurrence of the word `x`, but removing shifts "
              "everything left while the index keeps rising, so alternate matches are "
              "skipped. Fix it by walking the list **backwards**.",
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> names = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        for (int i = 0; i < names.size(); i++) {\n"
                     '            if (names.get(i).equals("x")) {\n'
                     "                names.remove(i);\n"
                     "            }\n"
                     "        }\n"
                     "        System.out.println(names);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> names = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        for (int i = names.size() - 1; i >= 0; i--) {\n"
                     '            if (names.get(i).equals("x")) {\n'
                     "                names.remove(i);\n"
                     "            }\n"
                     "        }\n"
                     "        System.out.println(names);"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]),
                     "[" + ", ".join(w for w in ws if w != "x") + "]")
               for ws in (["x", "x", "a"], ["a", "x", "x", "b"], ["x"],
                          ["a", "b"], ["x", "x", "x"])],
              hints=["After `remove(i)` the element that was at `i + 1` is now at "
                     "`i` — and the loop then moves to `i + 1`, skipping it.",
                     "Two adjacent matches therefore lose the second one. Case one is "
                     "exactly that.",
                     "Walking backwards fixes it, because removing at `i` never moves "
                     "anything before `i`.",
                     "`for (int i = names.size() - 1; i >= 0; i--)`",
                     "The alternative is an `Iterator` with its own `remove()`, which "
                     "lesson 17.3 covers."],
              difficulty="Medium"),

        _jch("j17-al-insert", "Insert in the middle", "Medium",
             "Read `n` words, then an index and a word. Insert that word at that index "
             "and print the list, then the list's size.",
             _jscan("        int n = sc.nextInt();\n"
                    "        List<String> names = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            names.add(sc.next());\n"
                    "        }\n"
                    "        int at = sc.nextInt();\n"
                    "        String w = sc.next();\n"
                    "        names.add(at, w);\n"
                    "        System.out.println(names);\n"
                    "        System.out.println(names.size());"),
             "        names.add(at, w);\n"
             "        System.out.println(names);\n"
             "        System.out.println(names.size());",
             [_case("\n".join([str(len(ws)), " ".join(ws), f"{at} {w}"]),
                    _nl("[" + ", ".join(ws[:at] + [w] + ws[at:]) + "]", len(ws) + 1))
              for (ws, at, w) in ((["a", "b", "c"], 1, "z"),
                                  (["a"], 0, "z"),
                                  (["a", "b"], 2, "z"),
                                  (["x", "y", "z"], 3, "w"),
                                  (["p", "q"], 1, "r"))],
             hints=["`add(index, element)` inserts BEFORE the element currently at "
                    "that index, shifting the rest right.",
                    "An index equal to `size()` appends — case three and four rely on "
                    "that.",
                    "The size goes up by exactly one.",
                    "Printing the list directly gives the `[a, z, b, c]` form."]),
    ],
    quiz=[
        _jq("`list.remove(i)` on a `List<String>` removes by…",
            ["index", "value", "both", "neither"],
            0,
            "For a `List<String>` there is no ambiguity. For a `List<Integer>` there "
            "very much is - the next lesson covers it."),
        _jq("Why does removing inside a forward index loop skip elements?",
            ["Removal shifts everything left while the index still advances",
             "The list is immutable",
             "size() is cached",
             "It does not"],
            0,
            "Walk backwards, or use an Iterator's own remove()."),
    ],
))


# --- 17.2 generics and boxing ------------------------------------------------

_M17.append(_jlesson(
    "m17-generics", "Generics and boxing",
    "Why `List<int>` does not exist.",
    """
```java
List<String> a = new ArrayList<>();
List<Integer> b = new ArrayList<>();
List<int> c;                            // does NOT compile
```

**Collections hold objects, never primitives.** The type argument in `<...>`
must be a reference type, so `int` becomes its wrapper class `Integer`.

| Primitive | Wrapper |
|---|---|
| `int` | `Integer` |
| `double` | `Double` |
| `char` | `Character` |
| `boolean` | `Boolean` |
| `long` | `Long` |

**Autoboxing makes it invisible — nearly.**

```java
List<Integer> nums = new ArrayList<>();
nums.add(5);                 // autoboxed: int -> Integer
int first = nums.get(0);     // auto-unboxed: Integer -> int
```

Three consequences that do bite:

**1. `remove(int)` versus `remove(Object)`.** This is the classic:

```java
List<Integer> nums = new ArrayList<>();
nums.add(10); nums.add(20); nums.add(30);

nums.remove(1);                       // removes INDEX 1 -> the 20
nums.remove(Integer.valueOf(20));     // removes the VALUE 20
```

Both overloads exist, and an `int` literal picks the index one. Every other
element type is unambiguous; `Integer` is the one that is not.

**2. `==` on wrappers compares references.** Java caches `Integer` objects from
`-128` to `127`, so small numbers appear to work and larger ones do not:

```java
Integer a = 127, b = 127;   a == b;   // true  (cached)
Integer x = 128, y = 128;   x == y;   // FALSE (two objects)
```

Always use `.equals` for wrappers. This is exactly module 6's `String` pool
trap, in a new costume.

**3. Unboxing `null` throws.** An `Integer` may be `null`; an `int` may not. So
`int v = list.get(i);` throws `NullPointerException` if that slot holds `null`.

**Generics are checked at compile time and erased at run time.** The compiler
guarantees only `String`s go into a `List<String>`, then removes the type
information from the bytecode. That is why you cannot write `new T[]` and why an
unchecked-cast warning exists at all.
""",
    warmup=[
        _jq("`List<Integer> nums` holding 10, 20, 30. What does `nums.remove(1)` do?",
            ["Removes index 1, so the 20", "Removes the value 1",
             "Removes the 10", "Does not compile"],
            0,
            "An `int` literal selects the `remove(int index)` overload. Use "
            "`remove(Integer.valueOf(1))` to remove by value."),
        _jq("Why is `Integer a = 128, b = 128; a == b` false?",
            ["`==` compares references, and only -128..127 are cached",
             "128 is too large for Integer",
             "Autoboxing failed",
             "It is true"],
            0,
            "Use `.equals` for wrappers, always. The cache makes the bug hide for small "
            "values."),
    ],
    exercises=[
        _je("j17-gen-declare", "A list of numbers",
            "`List<int>` does not compile. Replace `____` with the correct declaration "
            "of a list holding integers.",
            _jscan(_RD_ARR
                   + "        List<Integer> nums = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            nums.add(a[i]);\n"
                     "        }\n"
                     "        System.out.println(nums);"),
            "List<Integer> nums = new ArrayList<>();",
            [_acase(a, "[" + ", ".join(str(x) for x in a) + "]")
             for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3], [5, 4, 3, 2, 1])],
            hints=["A type argument must be a reference type, so `int` is not "
                   "allowed.",
                   "Use the wrapper class instead.",
                   "`List<Integer> nums = new ArrayList<>();`",
                   "`nums.add(a[i])` then autoboxes each `int` for you."],
            difficulty="Intro"),

        _je("j17-gen-remove-value", "Remove by value, not by index",
            "Read numbers and a value `k`, then remove the FIRST occurrence of the "
            "value `k` (not the element at index `k`). Replace `____` with the call "
            "that does that.",
            _jscan(_RD_ARR
                   + "        int k = sc.nextInt();\n"
                     "        List<Integer> nums = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            nums.add(a[i]);\n"
                     "        }\n"
                     "        nums.remove(Integer.valueOf(k));\n"
                     "        System.out.println(nums);"),
            "nums.remove(Integer.valueOf(k))",
            [_akcase(a, k, "[" + ", ".join(
                str(x) for x in (a[:a.index(k)] + a[a.index(k) + 1:]) if True) + "]"
                if k in a else "[" + ", ".join(str(x) for x in a) + "]")
             for (a, k) in (([10, 20, 30], 20), ([1, 2, 3], 1), ([5, 5, 5], 5),
                            ([1, 2, 3], 9), ([0, 1], 0))],
            hints=["`nums.remove(k)` with `k` an `int` picks the remove-by-INDEX "
                   "overload.",
                   "To pick the remove-by-value one, the argument must be an "
                   "`Integer` object.",
                   "`Integer.valueOf(k)` boxes it explicitly.",
                   "`nums.remove(Integer.valueOf(k))`",
                   "Removing a value that is not present changes nothing and returns "
                   "`false`."],
            difficulty="Medium"),

        _jfix("j17-gen-equals", "Comparing wrappers with ==",
              "This compares two boxed values with `==`, so it is `true` for small "
              "numbers and `false` for large ones. Fix it to compare values properly.",
              _jscan("        int x = sc.nextInt();\n"
                     "        int y = sc.nextInt();\n"
                     "        Integer a = x;\n"
                     "        Integer b = y;\n"
                     "        System.out.println(a == b);"),
              _jscan("        int x = sc.nextInt();\n"
                     "        int y = sc.nextInt();\n"
                     "        Integer a = x;\n"
                     "        Integer b = y;\n"
                     "        System.out.println(a.equals(b));"),
              [_case(f"{x} {y}", _jbool(x == y))
               for (x, y) in ((127, 127), (128, 128), (5, 6), (1000, 1000),
                              (-129, -129))],
              hints=["`==` on two `Integer`s asks whether they are the same OBJECT.",
                     "Java caches boxed values from -128 to 127, so `127 == 127` is "
                     "true and `128 == 128` is false — cases one and two prove it.",
                     "Compare values with `.equals`.",
                     "`a.equals(b)`",
                     "This is module 6's String-pool trap wearing different clothes."],
              difficulty="Medium"),

        _jch("j17-gen-sum", "Total a list of Integers", "Easy",
             "Read numbers into a `List<Integer>` and print their total. Let autoboxing "
             "and unboxing do the conversions.",
             _jscan(_RD_ARR
                    + "        List<Integer> nums = new ArrayList<>();\n"
                      "        for (int i = 0; i < n; i++) {\n"
                      "            nums.add(a[i]);\n"
                      "        }\n"
                      "        int total = 0;\n"
                      "        for (int v : nums) {\n"
                      "            total += v;\n"
                      "        }\n"
                      "        System.out.println(total);"),
             "        int total = 0;\n"
             "        for (int v : nums) {\n"
             "            total += v;\n"
             "        }\n"
             "        System.out.println(total);",
             [_acase(a, sum(a)) for a in ([1, 2, 3], [7], [0, 0], [-1, 2, -3],
                                          [5, 4, 3, 2, 1])],
             hints=["The enhanced `for` works over any collection.",
                    "You may declare the loop variable as `int` and let Java unbox "
                    "each `Integer` automatically.",
                    "Declaring it as `Integer` would work too, and `+=` would unbox "
                    "at each step.",
                    "This would throw a NullPointerException if any element were "
                    "`null` — which cannot happen here, but is worth knowing."]),
    ],
    quiz=[
        _jq("Why can a collection not hold `int` directly?",
            ["Generics require a reference type, so primitives use their wrapper classes",
             "Because int is too small",
             "It can",
             "Because of erasure"],
            0,
            "Autoboxing hides the conversion, but the list really is holding `Integer` "
            "objects."),
        _jq("What is type erasure?",
            ["Generic type information is checked at compile time and removed from the bytecode",
             "Deleting a list's contents",
             "Converting Integer back to int",
             "A garbage collection step"],
            0,
            "Which is why you cannot create `new T[]` and why unchecked-cast warnings "
            "exist."),
    ],
))


# --- 17.3 iterating ---------------------------------------------------------

_M17.append(_jlesson(
    "m17-iterate", "Iterating, and removing while you do",
    "Three ways round a list, and the exception that catches you out.",
    """
**The enhanced `for` is the default.** It works on any `Iterable`, reads
cleanly, and cannot go out of bounds:

```java
for (String s : names) {
    System.out.println(s);
}
```

**An index loop** is for when you need the position:

```java
for (int i = 0; i < names.size(); i++) {
    System.out.println(i + ": " + names.get(i));
}
```

**An explicit `Iterator`** is for when you need to *remove* as you go:

```java
Iterator<String> it = names.iterator();
while (it.hasNext()) {
    String s = it.next();
    if (s.equals("x")) {
        it.remove();            // the ONLY safe removal during iteration
    }
}
```

`hasNext()` asks whether anything is left; `next()` returns the element **and
advances**. Calling `next()` twice in one loop body consumes two elements, which
is a common accident.

## ConcurrentModificationException

```java
for (String s : names) {
    if (s.equals("x")) names.remove(s);     // throws
}
```

The enhanced `for` is an `Iterator` underneath, and the iterator notices that
the list changed behind its back. The name is misleading — no threads are
involved. It is the collection saying *you modified me while I was walking you*.

**The three ways to remove safely:**

1. `it.remove()` on an explicit `Iterator` — the iterator stays consistent.
2. A **backwards** index loop — removal never disturbs anything before `i`.
3. Build a **new list** of survivors and use that instead. Often the clearest.

**`it.remove()` removes the element `next()` last returned**, and must be called
exactly once per `next()`. Calling it before any `next()`, or twice in a row,
throws `IllegalStateException` — module 16's type, doing exactly its job.
""",
    warmup=[
        _jq("What does ConcurrentModificationException actually mean?",
            ["The collection was structurally modified while an iterator was walking it",
             "Two threads used the list at once",
             "The list is immutable",
             "An index was out of bounds"],
            0,
            "No threads are needed. The name is unfortunate."),
        _jq("How many elements does calling `next()` twice in one loop body consume?",
            ["Two", "One", "None", "It throws"],
            0,
            "`next()` returns the element AND advances, so store it in a variable and "
            "reuse that."),
    ],
    exercises=[
        _je("j17-it-foreach", "Walk it the simple way",
            "Print each word on its own line. Replace `____` with the enhanced `for` "
            "header.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(sc.next());\n"
                   "        }\n"
                   "        for (String s : names) {\n"
                   "            System.out.println(s);\n"
                   "        }"),
            "for (String s : names) {",
            [_case("\n".join([str(len(ws)), " ".join(ws)]), _nl(*ws))
             for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                        ["one", "two", "three"])],
            hints=["The enhanced `for` reads 'for each String s in names'.",
                   "The element type comes first, then the variable, then a colon.",
                   "`for (String s : names) {`",
                   "No index and no `get` call is needed."],
            difficulty="Intro"),

        _je("j17-it-iterator", "Remove as you walk",
            "Remove every occurrence of `x` using an explicit `Iterator`. Replace "
            "`____` with the call that safely removes the element just returned.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new ArrayList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(sc.next());\n"
                   "        }\n"
                   "        Iterator<String> it = names.iterator();\n"
                   "        while (it.hasNext()) {\n"
                   "            String s = it.next();\n"
                   '            if (s.equals("x")) {\n'
                   "                it.remove();\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(names);"),
            "it.remove()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join(w for w in ws if w != "x") + "]")
             for ws in (["x", "x", "a"], ["a", "x", "b"], ["x"], ["a", "b"],
                        ["x", "x", "x"])],
            hints=["Removing through the LIST while iterating throws "
                   "ConcurrentModificationException.",
                   "Removing through the ITERATOR keeps it consistent.",
                   "`it.remove()` — it takes no argument, because it removes whatever "
                   "`next()` last returned.",
                   "It must be called exactly once per `next()`, or you get an "
                   "IllegalStateException."],
            difficulty="Medium"),

        _jfix("j17-it-cme", "Modified while walking",
              "This throws `ConcurrentModificationException`, because it removes from "
              "the list during an enhanced `for`. Rewrite it to build a new list of the "
              "words that are not `x`, and print that instead.",
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> names = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        for (String s : names) {\n"
                     '            if (s.equals("x")) {\n'
                     "                names.remove(s);\n"
                     "            }\n"
                     "        }\n"
                     "        System.out.println(names);"),
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> names = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        List<String> kept = new ArrayList<>();\n"
                     "        for (String s : names) {\n"
                     '            if (!s.equals("x")) {\n'
                     "                kept.add(s);\n"
                     "            }\n"
                     "        }\n"
                     "        System.out.println(kept);"),
              [_case("\n".join([str(len(ws)), " ".join(ws)]),
                     "[" + ", ".join(w for w in ws if w != "x") + "]")
               for ws in (["x", "x", "a"], ["a", "x", "b"], ["x"], ["a", "b"],
                          ["x", "y", "x"])],
              hints=["The enhanced `for` uses an iterator internally, and it notices "
                     "the list changing underneath it.",
                     "Building a second list avoids the problem entirely — you never "
                     "modify the one you are walking.",
                     "Keep the words that do NOT equal `x`, so the test flips to "
                     "`!s.equals(\"x\")`.",
                     "Print the new list, not the original.",
                     "`it.remove()` or a backwards index loop would also work; this is "
                     "usually the clearest."],
              difficulty="Medium"),

        _jch("j17-it-index", "Number them", "Easy",
             "Print each word prefixed by its index and a colon and a space, like "
             "`0: Ada`. You need the position, so use an index loop.",
             _jscan("        int n = sc.nextInt();\n"
                    "        List<String> names = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            names.add(sc.next());\n"
                    "        }\n"
                    "        for (int i = 0; i < names.size(); i++) {\n"
                    '            System.out.println(i + ": " + names.get(i));\n'
                    "        }"),
             "        for (int i = 0; i < names.size(); i++) {\n"
             '            System.out.println(i + ": " + names.get(i));\n'
             "        }",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    _nl(*[f"{i}: {w}" for (i, w) in enumerate(ws)]))
              for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                         ["one", "two", "three"])],
             hints=["The enhanced `for` gives you elements but not positions, so an "
                    "index loop is right here.",
                    "The bound is `names.size()`, not `.length`.",
                    "Read each element with `names.get(i)`.",
                    "Mind the exact separator: colon then a space."]),
    ],
    quiz=[
        _jq("Which removal during iteration is safe?",
            ["it.remove() on an explicit Iterator",
             "list.remove(s) inside an enhanced for",
             "list.clear() inside the loop",
             "None"],
            0,
            "A backwards index loop and building a new list are the other two safe "
            "options."),
        _jq("What does `it.remove()` remove?",
            ["The element the last `next()` returned", "The first element",
             "The element at the current index", "Nothing - it needs an argument"],
            0,
            "Which is why it must be called exactly once per `next()`."),
    ],
))


# --- 17.4 ArrayList vs LinkedList -------------------------------------------

_M17.append(_jlesson(
    "m17-implementations", "`ArrayList` versus `LinkedList`",
    "Same interface, very different costs.",
    """
Both implement `List`, so every method you have learned works on either. What
differs is what each operation *costs*.

| | `ArrayList` | `LinkedList` |
|---|---|---|
| Holds | an array, resized as needed | nodes, each pointing to the next and previous |
| `get(i)` | **O(1)** | **O(n)** — it walks there |
| `add(x)` at the end | O(1) amortised | O(1) |
| `add(0, x)` / `remove(0)` | O(n) — shifts everything | **O(1)** |
| Memory per element | low | higher — two references per node |

**`ArrayList` is the default, and it is not close.** Random access is the common
case, and the array's contiguous memory is far friendlier to the CPU cache than
chasing pointers. `LinkedList`'s theoretical advantage at the front is real but
narrow, and in practice `ArrayDeque` (module 19) beats it there too.

**The trap is `get(i)` in a loop over a `LinkedList`:**

```java
for (int i = 0; i < list.size(); i++) {
    process(list.get(i));      // O(n) each time -> O(n^2) overall
}
```

On an `ArrayList` that is O(n). On a `LinkedList` it is O(n²), and it looks
identical. **Use the enhanced `for`** and the problem disappears — it walks with
an iterator, which is O(1) per step on both.

**Amortised O(1)** is worth understanding for `ArrayList.add`. When the backing
array is full it allocates a bigger one (about 1.5x) and copies everything —
O(n) for that one call. But the copies are rare enough that the *average* over
many adds is constant. If you know the size in advance,
`new ArrayList<>(10000)` skips the regrowth entirely.

> **`Arrays.asList(...)` is not an `ArrayList`.** It is a fixed-size view backed
> by the array: `set` works, `add` throws `UnsupportedOperationException`.
> `List.of(...)` is fully immutable — even `set` throws. To get a modifiable
> copy, `new ArrayList<>(List.of(...))`.
""",
    warmup=[
        _jq("Which is O(n) on a LinkedList but O(1) on an ArrayList?",
            ["get(i)", "add at the end", "size()", "isEmpty()"],
            0,
            "A linked list has to walk from an end to reach index i."),
        _jq("Why does an index loop over a LinkedList become O(n^2)?",
            ["Each get(i) walks from the start, and there are n of them",
             "size() is O(n)",
             "It does not",
             "Because of boxing"],
            0,
            "The enhanced for avoids it entirely by walking with an iterator."),
    ],
    exercises=[
        _je("j17-impl-swap", "Same code, other implementation",
            "The variable is declared as the interface, so only the constructor "
            "changes. Replace `____` so the list is a `LinkedList` instead — every "
            "other line stays identical.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new LinkedList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(names);\n"
                   "        System.out.println(names.size());"),
            "new LinkedList<>()",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   _nl("[" + ", ".join(ws) + "]", len(ws)))
             for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                        ["one", "two"])],
            hints=["Only the right-hand side of the assignment changes.",
                   "`new LinkedList<>()`",
                   "Everything else compiles unchanged because the variable's type is "
                   "the `List` interface.",
                   "That is the payoff of programming to the interface: one line, and "
                   "no caller notices."],
            difficulty="Intro"),

        _je("j17-impl-front", "Build it backwards",
            "Insert each word at the FRONT, so the list ends up reversed. Replace "
            "`____` with the call that inserts at index 0.",
            _jscan("        int n = sc.nextInt();\n"
                   "        List<String> names = new LinkedList<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            names.add(0, sc.next());\n"
                   "        }\n"
                   "        System.out.println(names);"),
            "names.add(0, sc.next())",
            [_case("\n".join([str(len(ws)), " ".join(ws)]),
                   "[" + ", ".join(reversed(ws)) + "]")
             for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                        ["one", "two", "three"])],
            hints=["`add(index, element)` inserts before whatever is at that index.",
                   "Index `0` therefore prepends.",
                   "`names.add(0, sc.next())`",
                   "This is the one operation where `LinkedList` genuinely beats "
                   "`ArrayList`: O(1) instead of shifting everything right."],
            difficulty="Easy"),

        _jfix("j17-impl-immutable", "The list that will not grow",
              "`Arrays.asList` returns a FIXED-SIZE view of the array, so `add` throws "
              "`UnsupportedOperationException`. Wrap it in a real `ArrayList` so the "
              "extra word can be added.",
              _jscan("        String w = sc.next();\n"
                     '        List<String> names = Arrays.asList("a", "b");\n'
                     "        names.add(w);\n"
                     "        System.out.println(names);"),
              _jscan("        String w = sc.next();\n"
                     '        List<String> names = new ArrayList<>(Arrays.asList("a", "b"));\n'
                     "        names.add(w);\n"
                     "        System.out.println(names);"),
              [_case(w, f"[a, b, {w}]") for w in ("c", "z", "x", "hello", "q")],
              hints=["`Arrays.asList` gives a view backed by the original array, so "
                     "its size cannot change.",
                     "`set` would work; `add` and `remove` throw.",
                     "Copy it into a genuine `ArrayList` using the constructor that "
                     "takes a collection.",
                     "`new ArrayList<>(Arrays.asList(\"a\", \"b\"))`",
                     "`List.of(...)` is stricter still — even `set` throws on that "
                     "one."],
              difficulty="Medium"),

        _jch("j17-impl-copy", "Copy and keep both", "Medium",
             "Read `n` words into a list. Make an independent copy, add the word "
             "`extra` to the copy only, then print the original and then the copy.",
             _jscan("        int n = sc.nextInt();\n"
                    "        List<String> names = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            names.add(sc.next());\n"
                    "        }\n"
                    "        List<String> copy = new ArrayList<>(names);\n"
                    '        copy.add("extra");\n'
                    "        System.out.println(names);\n"
                    "        System.out.println(copy);"),
             "        List<String> copy = new ArrayList<>(names);\n"
             '        copy.add("extra");\n'
             "        System.out.println(names);\n"
             "        System.out.println(copy);",
             [_case("\n".join([str(len(ws)), " ".join(ws)]),
                    _nl("[" + ", ".join(ws) + "]",
                        "[" + ", ".join(list(ws) + ["extra"]) + "]"))
              for ws in (["Ada", "Bo"], ["solo"], ["a", "b", "c"], ["x", "y"],
                         ["one"])],
             hints=["`List<String> copy = names;` would alias, not copy — module 1's "
                    "lesson again.",
                    "The `ArrayList` constructor accepts another collection and copies "
                    "its elements.",
                    "`new ArrayList<>(names)`",
                    "This is a SHALLOW copy: a new list holding the same element "
                    "references. For immutable elements like `String` that is enough.",
                    "The first printed line must be unchanged."]),
    ],
    quiz=[
        _jq("Which should be your default List implementation?",
            ["ArrayList", "LinkedList", "Arrays.asList", "It never matters"],
            0,
            "Random access is the common case, and contiguous memory is far more "
            "cache-friendly than chasing node pointers."),
        _jq("What does `add` being 'amortised O(1)' on an ArrayList mean?",
            ["Occasional resizes cost O(n), but the average across many adds is constant",
             "It is always exactly O(1)",
             "It is O(n) every time",
             "It depends on the element type"],
            0,
            "Pre-sizing with `new ArrayList<>(n)` avoids the regrowth entirely when you "
            "know the count."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m17_run(words, drop, at, ins):
    kept = [w for w in words if w != drop]
    kept2 = list(kept)
    if 0 <= at <= len(kept2):
        kept2.insert(at, ins)
    return _nl("[" + ", ".join(words) + "]",
               "[" + ", ".join(kept) + "]",
               "[" + ", ".join(kept2) + "]",
               len(kept2),
               kept2[0] if kept2 else "empty")


def _m17_case(words, drop, at, ins):
    return _case("\n".join([str(len(words)), " ".join(words),
                            drop, f"{at} {ins}"]),
                 _m17_run(words, drop, at, ins))


_M17_CAP = _jcap(
    "Word list",
    """
A short pipeline that exercises every part of module 17: building a list,
filtering it without a `ConcurrentModificationException`, inserting by index,
and reporting.

## Input

```
n
<n words on one line>
<word to drop>
<index> <word to insert>
```

The insertion index is always between `0` and the size of the filtered list, so
it is always valid.

## Output, five lines

1. The original list
2. The list with **every** occurrence of the drop-word removed
3. That list again, with the insert-word placed at the given index
4. The final size
5. The first element of the final list, or `empty` if it has none

## What the hidden cases check

- **Every occurrence is dropped, including adjacent ones.** A forward index loop
  that removes as it goes will skip the second of a pair — build a new list, walk
  backwards, or use `it.remove()`.
- **`add(index, element)` inserts before that position**, and an index equal to
  the size appends.
- **The original list is printed unmodified first**, so the filtering must not
  have already happened when line 1 is printed.
- **An empty final list prints `empty`** on the last line rather than throwing —
  and it can be empty only when the insert did not happen, which cannot occur
  here, so the guard is there for the shape of the code rather than the data.
""",
    _jch("j17-cap-words", "Word list", "Hard",
         "Write the whole body where you see `____`: read the words, print the "
         "original, filter, insert, and print the four remaining lines.",
         _jscan("        int n = sc.nextInt();\n"
                "        List<String> words = new ArrayList<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            words.add(sc.next());\n"
                "        }\n"
                "        String drop = sc.next();\n"
                "        int at = sc.nextInt();\n"
                "        String ins = sc.next();\n"
                "        System.out.println(words);\n"
                "        List<String> kept = new ArrayList<>();\n"
                "        for (String w : words) {\n"
                "            if (!w.equals(drop)) {\n"
                "                kept.add(w);\n"
                "            }\n"
                "        }\n"
                "        System.out.println(kept);\n"
                "        kept.add(at, ins);\n"
                "        System.out.println(kept);\n"
                "        System.out.println(kept.size());\n"
                "        if (kept.isEmpty()) {\n"
                '            System.out.println("empty");\n'
                "        } else {\n"
                "            System.out.println(kept.get(0));\n"
                "        }"),
         "        int n = sc.nextInt();\n"
         "        List<String> words = new ArrayList<>();\n"
         "        for (int i = 0; i < n; i++) {\n"
         "            words.add(sc.next());\n"
         "        }\n"
         "        String drop = sc.next();\n"
         "        int at = sc.nextInt();\n"
         "        String ins = sc.next();\n"
         "        System.out.println(words);\n"
         "        List<String> kept = new ArrayList<>();\n"
         "        for (String w : words) {\n"
         "            if (!w.equals(drop)) {\n"
         "                kept.add(w);\n"
         "            }\n"
         "        }\n"
         "        System.out.println(kept);\n"
         "        kept.add(at, ins);\n"
         "        System.out.println(kept);\n"
         "        System.out.println(kept.size());\n"
         "        if (kept.isEmpty()) {\n"
         '            System.out.println("empty");\n'
         "        } else {\n"
         "            System.out.println(kept.get(0));\n"
         "        }",
         [_m17_case(ws, drop, at, ins) for (ws, drop, at, ins) in (
             (["a", "x", "b", "x"], "x", 1, "z"),
             (["x", "x", "a"], "x", 0, "z"),
             (["p", "q"], "z", 2, "r"),
             (["one"], "one", 0, "two"),
             (["a", "b", "c"], "b", 2, "d"),
         )],
         hints=["Declare the variables as `List<String>` and construct `ArrayList`s.",
                "Print the original BEFORE filtering — the first line must show every "
                "word.",
                "Filter by building a SECOND list of survivors. Removing from `words` "
                "inside an enhanced `for` would throw "
                "ConcurrentModificationException, and a forward index loop would skip "
                "adjacent matches.",
                "Compare words with `.equals`, never `==`.",
                "`kept.add(at, ins)` inserts before position `at`; an `at` equal to "
                "the size appends.",
                "`size()` for the count — not `.length` and not `.length()`.",
                "Guard the last line with `isEmpty()` before calling `get(0)`."]),
    example_io="stdin:  4\n        a x b x\n        x\n        1 z\n\n"
               "stdout: [a, x, b, x]\n        [a, b]\n        [a, z, b]\n        3\n"
               "        a",
    rubric=[
        "Variables are declared as `List<String>`, constructed as `ArrayList`.",
        "The original list is printed before any filtering happens.",
        "Filtering builds a new list rather than removing during iteration.",
        "Every occurrence of the drop-word is removed, including adjacent ones.",
        "Words are compared with `.equals`.",
        "`add(index, element)` is used for the insertion, and an index equal to the size appends.",
        "`size()` reports the count.",
        "`isEmpty()` guards the `get(0)` on the final line.",
    ],
)


_MODULES.append(_jmod(
    17, 6, "The collections framework",
    "Lists",
    "Trade the fixed-length array for a list that grows: `List` and `ArrayList`, the "
    "generics and boxing that come with it, safe iteration, and why `ArrayList` is "
    "almost always the right implementation.",
    """
Part 6 opens on the thing every real Java program uses constantly.

An array's length is decided when it is created, which is why module 12's
`Playlist` needed a capacity and a manual `size` field. `ArrayList` removes that
whole category of bookkeeping — and because it implements `List`, module 14's
advice applies directly: **declare the interface, construct the
implementation.**

The price of admission is **generics and boxing**. Collections hold objects, so
`int` becomes `Integer` and autoboxing hides the conversion — until it does not.
`remove(1)` on a `List<Integer>` removes an *index*; `==` on two `Integer`s
compares references and is quietly wrong above 127; and unboxing a `null`
throws. All three are the same shape of trap as `==` on Strings in module 6.

**Iteration** brings its own rule: modify a collection while an iterator is
walking it and you get `ConcurrentModificationException`. The three safe removals
— `it.remove()`, a backwards index loop, or building a new list — are worth
knowing before you need them.

Finally, `ArrayList` versus `LinkedList` is the first real *performance* choice
in this course. Same interface, same code, very different costs — and the honest
answer is that `ArrayList` wins nearly always.
""",
    _M17,
    capstone=_M17_CAP,
    objectives=[
        "Create and populate an `ArrayList`, declaring the variable as `List`.",
        "Use add, get, set, remove, size, isEmpty, contains and indexOf correctly.",
        "Explain why collections cannot hold primitives, and what autoboxing does.",
        "Avoid the `remove(int)` versus `remove(Object)` trap on a `List<Integer>`.",
        "Say why `==` on wrappers is wrong, and why it seems to work for small values.",
        "Iterate with the enhanced `for`, an index loop, and an explicit `Iterator`.",
        "Remove elements during iteration without a ConcurrentModificationException.",
        "Compare `ArrayList` and `LinkedList` by operation cost, and pick a default.",
    ],
    why="`List` is the collection you will use more than all the others put together. "
        "The boxing traps in this module are standard interview questions, and "
        "ConcurrentModificationException is one of the most common runtime failures in "
        "Java — all three are much easier to avoid once you have caused them "
        "deliberately.",
    est_minutes=330,
    glossary=[
        _jg("List", "The ordered-collection interface: indexed access, duplicates "
                    "allowed."),
        _jg("ArrayList", "A List backed by a resizable array. O(1) get, O(n) insert at "
                         "the front. The default choice."),
        _jg("LinkedList", "A List of doubly-linked nodes. O(1) at the ends, O(n) get."),
        _jg("generics", "The `<Type>` parameter that makes a collection type-safe at "
                        "compile time."),
        _jg("diamond", "The empty `<>` on the right-hand side, letting Java infer the "
                       "type argument."),
        _jg("autoboxing", "Automatic conversion between a primitive and its wrapper, "
                          "e.g. int to Integer."),
        _jg("wrapper class", "The object form of a primitive: Integer, Double, "
                             "Character, Boolean, Long."),
        _jg("type erasure", "Generic types are checked at compile time and removed from "
                            "the bytecode."),
        _jg("Iterator", "The object that walks a collection: hasNext(), next(), and the "
                        "only safe remove() during iteration."),
        _jg("ConcurrentModificationException", "Thrown when a collection is structurally "
                                               "modified while an iterator walks it. No "
                                               "threads involved."),
        _jg("amortised O(1)", "Occasional expensive operations averaged over many cheap "
                              "ones - ArrayList's add."),
    ],
    cheatsheet="""
```java
// --- create ---------------------------------------------------------------
List<String> a = new ArrayList<>();        // interface on the left, impl on the right
List<String> b = new LinkedList<>();       // same interface, different costs
List<String> c = new ArrayList<>(other);   // a shallow COPY of another collection
List<String> d = new ArrayList<>(1000);    // pre-sized, skips regrowth

// --- the API --------------------------------------------------------------
add(x)  add(i, x)  get(i)  set(i, x)  remove(i)
size()  isEmpty()  contains(x)  indexOf(x)  clear()
// length / length() / size()  ->  array / String / collection

// --- boxing traps ---------------------------------------------------------
List<Integer> nums = new ArrayList<>();
nums.remove(1);                     // by INDEX
nums.remove(Integer.valueOf(1));    // by VALUE
Integer x = 128, y = 128; x == y;   // FALSE  — use .equals for wrappers
int v = list.get(i);                // NPE if that element is null

// --- iterate --------------------------------------------------------------
for (String s : names) { ... }                 // default
for (int i = 0; i < names.size(); i++) { ... } // when you need the index

Iterator<String> it = names.iterator();        // when you need to remove
while (it.hasNext()) {
    String s = it.next();                      // returns AND advances
    if (...) it.remove();                      // exactly once per next()
}

// --- removing safely ------------------------------------------------------
// 1. it.remove()   2. backwards index loop   3. build a new list
for (String s : names) names.remove(s);   // ConcurrentModificationException

// --- not real ArrayLists --------------------------------------------------
Arrays.asList("a","b")     // fixed size: set OK, add throws
List.of("a","b")           // fully immutable: set throws too
new ArrayList<>(List.of("a","b"))   // a modifiable copy
```
""",
    self_check=[
        "Can you say why the variable should be `List` and the constructor `ArrayList`?",
        "Can you name the three different ways to ask 'how big' across arrays, Strings and collections?",
        "Can you explain what `nums.remove(1)` does on a `List<Integer>`, and how to remove by value?",
        "Can you say why `Integer a = 128, b = 128; a == b` is false but the 127 version is true?",
        "Can you list the three safe ways to remove during iteration?",
        "Can you explain what ConcurrentModificationException means without mentioning threads?",
        "Can you give the cost of `get(i)` on each implementation, and why an index loop over a LinkedList is O(n^2)?",
        "Can you say what `Arrays.asList` returns and why `add` throws on it?",
    ],
    review=[
        _jq("```java\nList<Integer> n = new ArrayList<>();\nn.add(10); n.add(20); n.add(30);\nn.remove(1);\nSystem.out.println(n);\n```\nWhat prints?",
            ["[10, 30]", "[20, 30]", "[10, 20, 30]", "[10, 20]"],
            0,
            "An `int` literal picks `remove(int index)`, so the element at index 1 - "
            "the 20 - is removed."),
        _jq("Which loop is safe for removing every matching element from an ArrayList?",
            ["A backwards index loop", "A forward index loop",
             "An enhanced for calling list.remove", "None of these"],
            0,
            "Removing at `i` never disturbs anything before `i`, so counting down "
            "cannot skip."),
        _jq("On a LinkedList, which is O(n)?",
            ["get(i)", "add at the end", "size()", "isEmpty()"],
            0,
            "It must walk from an end. That is what makes an index loop over one "
            "quadratic."),
        _jq("In the capstone, why build a second list instead of removing from the first?",
            ["Removing during an enhanced for throws, and a forward index loop skips adjacent matches",
             "It is faster",
             "Because the list is immutable",
             "To save memory"],
            0,
            "Both failure modes are in the test cases, and building a new list sidesteps "
            "each of them."),
    ],
    milestone="You can use the collection Java programs reach for most, avoid the "
              "boxing and iteration traps that come with it, and justify your choice "
              "of implementation by cost rather than habit.",
))
