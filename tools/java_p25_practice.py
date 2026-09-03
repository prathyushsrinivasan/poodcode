# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 25 practice - lambdas, functional interfaces and method references.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[25]`.
#
# No streams anywhere: `.stream()` is gated to module 26, so every family here
# drives its lambdas with an ordinary loop. That is deliberate - the lambda is
# the thing being drilled, and a pipeline would hide it.
#
# The five families are the five lessons: the arrow itself against a Comparator
# the learner already wrote by hand, the four java.util.function shapes,
# declaring the interface yourself, capture and closures, and method references.
# ---------------------------------------------------------------------------

_IMPORTS25P = "import java.util.*;\nimport java.util.function.*;\n"


def _p25prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS25P,
    )


def _p25tprog(types, helpers, body):
    return _jp(
        _IMPORTS25P + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + (helpers.rstrip("\n") + "\n\n" if helpers.strip() else "")
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _p25m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p25prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p25b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p25prog(helpers, body),
                body, tests, hints)


def _p25s(eid, title, difficulty, prompt, body, tests, hints):
    """No helpers - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan(body, imports=_IMPORTS25P), body, tests, hints)


def _p25t(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """A top-level type is given; write main's BODY."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p25tprog(types, helpers, body),
                body, tests, hints)


def _p25c(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """Write the top-level TYPE(s); main is given."""
    return _jch(eid, title, difficulty, prompt, _p25tprog(types, helpers, body),
                types.strip("\n"), tests, hints)


def _p25tm(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """A top-level type is given AND a helper method is written - blank the
    method. Needed whenever the helper's signature mentions an interface that
    has to be declared above `Main`."""
    return _jch(eid, title, difficulty, prompt, _p25tprog(types, helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


_TRANSFORM25P = """
@FunctionalInterface
interface Transform {
    String apply(String value);
}
"""

_FILTER25P = """
@FunctionalInterface
interface Filter {
    boolean keep(String value);
}
"""


_RD_W25P = ("        int n = sc.nextInt();\n"
            "        List<String> words = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words.add(sc.next());\n"
            "        }\n")

_RD_N25P = ("        int n = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")

_WS25P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS25P = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

_WL25P = ((["ada", "bo", "cy"], 2), (["solo"], 3), (["x", "yy", "zzz"], 1),
          (["pear", "fig"], 3), (["alpha", "beta", "gamma", "d"], 4))

# (word list, prefix) pairs for the prefix-capturing family.
_WP25P = ((["ada", "bo", "ash"], "a"), (["solo"], "s"), (["x", "yy", "zzz"], "z"),
          (["pear", "fig", "plum"], "p"), (["alpha", "beta", "d"], "b"))


def _w25p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n25p(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wl25p(ws, limit, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(limit)]), out)


def _wp25p(ws, prefix, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), prefix]), out)


def _jl25p(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- Family A - the arrow ----------------------------------------------------

_P25_A = _jfam(
    "p25-lambda", "The lambda, against a Comparator you already know",
    "Module 20's named class, collapsed to one line - five times.",
    """
```java
words.sort((a, b) -> Integer.compare(a.length(), b.length()));
```

`Comparator<String>` has one abstract method taking two Strings and returning an
`int`, so that is what the lambda's parameters and result must be. Nothing had
to be declared.

* **Expression body** - a single expression, whose value *is* the result. No
  `return`, no braces, no semicolon inside.
* **Block body** - braces, one or more statements, and `return` is required to
  produce a value.

And module 20's rule survives intact: compare with `Integer.compare(a, b)`,
never `a - b`, because the subtraction overflows.
""",
    [
        _p25s("j25-pa-length", "Shortest first", "Intro",
              "Sort the words by length with a lambda, then print the list and its "
              "size.",
              _RD_W25P
              + "        words.sort((a, b) -> Integer.compare(a.length(), b.length()));\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(_jl25p(sorted(ws, key=len)), len(ws))) for ws in _WS25P],
              ["`list.sort` wants a `Comparator<String>`, whose method takes two "
               "Strings.",
               "`(a, b) -> Integer.compare(a.length(), b.length())`",
               "An expression body needs no `return`.",
               "The sort is stable, so equal lengths keep their input order."]),

        _p25s("j25-pa-alpha", "Alphabetically", "Intro",
              "Sort the words into alphabetical order with a lambda that delegates to "
              "`compareTo`, then print the list and its first element.",
              _RD_W25P
              + "        words.sort((a, b) -> a.compareTo(b));\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.get(0));",
              [_w25p(ws, _nl(_jl25p(sorted(ws)), sorted(ws)[0])) for ws in _WS25P],
              ["`String` is already `Comparable`, so the body is one call.",
               "`(a, b) -> a.compareTo(b)`",
               "After sorting, `get(0)` is the alphabetically first word.",
               "`words.sort(null)` would also work, using natural order - but the "
               "lambda says what it means."]),

        _p25s("j25-pa-desc", "Largest first", "Easy",
              "Sort the numbers descending with a lambda, then print the list and its "
              "largest element.",
              _RD_N25P
              + "        nums.sort((a, b) -> Integer.compare(b, a));\n"
                "        System.out.println(nums);\n"
                "        System.out.println(nums.get(0));",
              [_n25p(xs, _nl(_jl25p(sorted(xs, reverse=True)),
                             sorted(xs, reverse=True)[0]))
               for xs in _NS25P],
              ["Descending is ascending with the arguments swapped.",
               "`(a, b) -> Integer.compare(b, a)` - `b` first.",
               "Never `b - a`: for large values the subtraction overflows.",
               "`nums.get(0)` is then the maximum."]),

        _p25s("j25-pa-block", "Two keys, so two statements", "Medium",
              "Sort by length, breaking ties alphabetically. That needs a braced lambda "
              "body. Print the list and its size.",
              _RD_W25P
              + "        words.sort((a, b) -> {\n"
                "            if (a.length() != b.length()) {\n"
                "                return Integer.compare(a.length(), b.length());\n"
                "            }\n"
                "            return a.compareTo(b);\n"
                "        });\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(_jl25p(sorted(ws, key=lambda w: (len(w), w))), len(ws)))
               for ws in _WS25P],
              ["Braces mean statements, and statements mean `return`.",
               "Compare the first key; only fall through when it ties.",
               "`a.compareTo(b)` is the tie-break.",
               "Do not forget the `);` that closes the `sort` call after the brace.",
               "With ties broken explicitly the result no longer depends on input "
               "order."]),

        _p25s("j25-pa-lastchar", "By last letter", "Medium",
              "Sort the words by their final character, then print the list and its "
              "size.",
              _RD_W25P
              + "        words.sort((a, b) -> Character.compare(a.charAt(a.length() - 1), b.charAt(b.length() - 1)));\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(_jl25p(sorted(ws, key=lambda w: w[-1])), len(ws)))
               for ws in _WS25P],
              ["The last character of `a` is `a.charAt(a.length() - 1)`.",
               "`Character.compare` is the `char` equivalent of `Integer.compare`.",
               "Subtracting chars would work for ASCII and is still the wrong habit.",
               "Stability means words sharing a last letter keep their input order."]),
    ])


# --- Family B - the four shapes ----------------------------------------------

_P25_B = _jfam(
    "p25-functional", "`Predicate`, `Function`, `Consumer`, `Supplier`",
    "Four interfaces, four method names, and behaviour as a value.",
    """
| Interface | Method | Shape |
|---|---|---|
| `Predicate<T>` | `test(T)` | T in, `boolean` out |
| `Function<T, R>` | `apply(T)` | T in, R out |
| `Consumer<T>` | `accept(T)` | T in, nothing out |
| `Supplier<T>` | `get()` | nothing in, T out |

They live in **`java.util.function`**, which `import java.util.*` does not
cover.

You invoke a lambda by its interface's own method name - `test`, `apply`,
`accept`, `get` - because a lambda is an object, not a function.

The payoff is a parameter: once a method takes a `Predicate`, one loop answers
every question you have not thought of yet.
""",
    [
        _p25s("j25-pb-predicate", "A question as a value", "Intro",
              "Hold the question `is this word longer than three characters` in a "
              "`Predicate`, count the words that satisfy it, and print the count then "
              "the list size.",
              _RD_W25P
              + "        Predicate<String> isLong = w -> w.length() > 3;\n"
                "        int count = 0;\n"
                "        for (String w : words) {\n"
                "            if (isLong.test(w)) {\n"
                "                count++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws)))
               for ws in _WS25P],
              ["`Predicate<String>` - a String in, a boolean out.",
               "One parameter needs no parentheses: `w -> w.length() > 3`.",
               "Ask it with `isLong.test(w)`, not `isLong(w)`.",
               "`count` is a plain local mutated by the LOOP, not by the lambda."]),

        _p25s("j25-pb-function", "A transformation as a value", "Intro",
              "Hold the transformation `word to its length` in a `Function`, add up "
              "every length, and print the total then the list size.",
              _RD_W25P
              + "        Function<String, Integer> length = w -> w.length();\n"
                "        int total = 0;\n"
                "        for (String w : words) {\n"
                "            total += length.apply(w);\n"
                "        }\n"
                "        System.out.println(total);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(sum(len(w) for w in ws), len(ws))) for ws in _WS25P],
              ["`Function<T, R>` names the input type first, the result second.",
               "A type argument must be a reference type, so the result is `Integer`.",
               "`Function<String, Integer> length = w -> w.length();`",
               "`total +=` unboxes the `Integer` back to an `int`."]),

        _p25s("j25-pb-consumer", "An action as a value", "Easy",
              "Hold the action `print this word in capitals` in a `Consumer`, run it "
              "against every word, then print the list size.",
              _RD_W25P
              + "        Consumer<String> shout = w -> System.out.println(w.toUpperCase());\n"
                "        for (String w : words) {\n"
                "            shout.accept(w);\n"
                "        }\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _WS25P],
              ["A `Consumer<T>` returns nothing, so the body is a statement.",
               "`Consumer<String> shout = w -> System.out.println(w.toUpperCase());`",
               "Call it with `.accept(w)`.",
               "One line per word, then the count."]),

        _p25s("j25-pb-supplier", "A factory as a value", "Easy",
              "Hold `make me a new empty list` in a `Supplier`, use it to build a copy "
              "of the words, then print the copy and its size.",
              _RD_W25P
              + "        Supplier<List<String>> maker = () -> new ArrayList<>();\n"
                "        List<String> copy = maker.get();\n"
                "        for (String w : words) {\n"
                "            copy.add(w);\n"
                "        }\n"
                "        System.out.println(copy);\n"
                "        System.out.println(copy.size());",
              [_w25p(ws, _nl(_jl25p(ws), len(ws))) for ws in _WS25P],
              ["A `Supplier<T>` takes nothing, so the parameter list is empty "
               "parentheses.",
               "`Supplier<List<String>> maker = () -> new ArrayList<>();`",
               "Call it with `.get()` - and each call would make a NEW list.",
               "The copy holds the same words in the same order."]),

        _p25m("j25-pb-higher", "countMatching", "Medium",
              "Write `countMatching`, which counts the elements of a list satisfying a "
              "`Predicate` passed in. `main` calls it twice with different questions.",
              """
    static int countMatching(List<String> items, Predicate<String> test) {
        int count = 0;
        for (String item : items) {
            if (test.test(item)) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_W25P
              + "        System.out.println(countMatching(words, w -> w.length() > 3));\n"
                "        System.out.println(countMatching(words, w -> w.startsWith(\"a\")));\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(sum(1 for w in ws if len(w) > 3),
                             sum(1 for w in ws if w.startswith("a")),
                             len(ws)))
               for ws in _WS25P],
              ["The behaviour is the second parameter: `Predicate<String> test`.",
               "Inside, ask it with `test.test(item)`.",
               "One loop, written once; the two call sites differ only in the lambda.",
               "Three printed lines."]),
    ])


# --- Family C - your own functional interface --------------------------------

_P25_C = _jfam(
    "p25-own", "Declaring the interface yourself",
    "One abstract method is the whole requirement.",
    """
```java
@FunctionalInterface
interface Transform {
    String apply(String value);
}

Transform shout = w -> w.toUpperCase();
```

The method's name is yours to choose. `@FunctionalInterface` does not make the
interface functional - having exactly one abstract method does - it asks the
compiler to *check*, so the error lands on the interface the day someone adds a
second method rather than on every lambda that used it.

`default` and `static` interface methods (module 14) have bodies, so they are
not abstract and do not count against the budget.

Declare your own when the name carries meaning: `Transform` and `Combiner` read
better at a call site than `Function<String, String>` and
`BinaryOperator<Integer>`.
""",
    [
        _p25c("j25-pc-transform", "Transform", "Easy",
              "Write the functional interface `main` needs: `Transform`, with one "
              "abstract method `apply` taking a String and returning a String, annotated "
              "so the compiler enforces the single-method rule.",
              _TRANSFORM25P, "",
              _RD_W25P
              + "        Transform shout = w -> w.toUpperCase();\n"
                "        for (String w : words) {\n"
                "            System.out.println(shout.apply(w));\n"
                "        }\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _WS25P],
              ["Interface methods are implicitly public and abstract - one line, ending "
               "in a semicolon.",
               "`String apply(String value);`",
               "`@FunctionalInterface` goes directly above the declaration.",
               "Only `Main` may be `public`."]),

        _p25c("j25-pc-combiner", "Combiner", "Easy",
              "Write `Combiner`, a functional interface folding two `int`s into one, "
              "which `main` uses to total the numbers.",
              """
@FunctionalInterface
interface Combiner {
    int combine(int a, int b);
}
""", "",
              _RD_N25P
              + "        Combiner add = (a, b) -> a + b;\n"
                "        int total = 0;\n"
                "        for (int x : nums) {\n"
                "            total = add.combine(total, x);\n"
                "        }\n"
                "        System.out.println(total);\n"
                "        System.out.println(nums.size());",
              [_n25p(xs, _nl(sum(xs), len(xs))) for xs in _NS25P],
              ["`int combine(int a, int b);` - primitives are fine in your own "
               "interface.",
               "A `Function<Integer, Integer>` could not take two arguments, and would "
               "box.",
               "`@FunctionalInterface` above it.",
               "The fold starts at 0 and combines one number at a time."]),

        _p25tm("j25-pc-mapall", "mapAll", "Medium",
               "`Transform` is declared for you. Write `mapAll`, applying it to every "
               "element and returning the results as a NEW list. `main` calls it with "
               "two different lambdas.",
               _TRANSFORM25P,
               """
    static List<String> mapAll(List<String> items, Transform t) {
        List<String> out = new ArrayList<>();
        for (String item : items) {
            out.add(t.apply(item));
        }
        return out;
    }
""",
               _RD_W25P
               + "        System.out.println(mapAll(words, w -> w.toUpperCase()));\n"
                 "        System.out.println(mapAll(words, w -> w + \"!\"));\n"
                 "        System.out.println(words);",
               [_w25p(ws, _nl(_jl25p([w.upper() for w in ws]),
                              _jl25p([w + "!" for w in ws]),
                              _jl25p(ws)))
                for ws in _WS25P],
               ["The interface `Transform` is declared for you above `Main`.",
                "Build a new list rather than modifying the input.",
                "`out.add(t.apply(item));`",
                "The third line proves the source list is untouched."]),

        _p25tm("j25-pc-keepall", "keepAll", "Medium",
               "`Filter` is declared for you, with one method `keep`. Write `keepAll`, "
               "returning a new list of the elements it keeps.",
               _FILTER25P,
               """
    static List<String> keepAll(List<String> items, Filter f) {
        List<String> out = new ArrayList<>();
        for (String item : items) {
            if (f.keep(item)) {
                out.add(item);
            }
        }
        return out;
    }
""",
               _RD_W25P
               + "        System.out.println(keepAll(words, w -> w.length() > 3));\n"
                 "        System.out.println(keepAll(words, w -> w.startsWith(\"a\")));\n"
                 "        System.out.println(words.size());",
               [_w25p(ws, _nl(_jl25p([w for w in ws if len(w) > 3]),
                              _jl25p([w for w in ws if w.startswith("a")]),
                              len(ws)))
                for ws in _WS25P],
               ["`Filter` has one abstract method, `boolean keep(String value)`.",
                "The shape is `Predicate` with a domain name - which is the reason to "
                "declare your own.",
                "Guard with `if (f.keep(item))` before adding.",
                "An empty result prints as `[]`."]),

        _p25t("j25-pc-use", "Using a given interface", "Easy",
              "`Transform` is declared for you. Build two transforms - one that "
              "capitalises and one that appends an exclamation mark - apply each to the "
              "first word, and print both results and the list size.",
              _TRANSFORM25P, "",
              _RD_W25P
              + "        Transform shout = w -> w.toUpperCase();\n"
                "        Transform excite = w -> w + \"!\";\n"
                "        System.out.println(shout.apply(words.get(0)));\n"
                "        System.out.println(excite.apply(words.get(0)));\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(ws[0].upper(), ws[0] + "!", len(ws))) for ws in _WS25P],
              ["Two variables of the same interface type, holding different behaviour.",
               "`Transform shout = w -> w.toUpperCase();`",
               "`Transform excite = w -> w + \"!\";`",
               "Both are invoked with `.apply(...)`, the name the interface chose."]),
    ])


# --- Family D - capture and closures -----------------------------------------

_P25_D = _jfam(
    "p25-capture", "Capture, and behaviour built to order",
    "A lambda may read the locals around it - if they never change.",
    """
```java
int limit = sc.nextInt();
Predicate<String> longer = w -> w.length() > limit;    // fine: effectively final
```

A captured local must be **final or effectively final** - never assigned after
initialisation - because capture is **by value** and the lambda may outlive the
method. So this is refused:

```java
int count = 0;
Consumer<String> tally = w -> count++;    // ERROR
```

The fix is almost always to stop mutating: count in a loop, or have the lambda
*answer* rather than *accumulate*.

A method parameter is effectively final too, which is what makes a **closure**
work - a method that builds behaviour out of its arguments and returns it:

```java
static Predicate<String> longerThan(int limit) {
    return w -> w.length() > limit;
}
```
""",
    [
        _p25s("j25-pd-capture", "Capturing a limit", "Easy",
              "Read a limit after the words, then count the words longer than it using a "
              "predicate that captures it. Print the count and then the limit.",
              _RD_W25P
              + "        int limit = sc.nextInt();\n"
                "        Predicate<String> longer = w -> w.length() > limit;\n"
                "        int count = 0;\n"
                "        for (String w : words) {\n"
                "            if (longer.test(w)) {\n"
                "                count++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);\n"
                "        System.out.println(limit);",
              [_wl25p(ws, limit, _nl(sum(1 for w in ws if len(w) > limit), limit))
               for (ws, limit) in _WL25P],
              ["`limit` is read once and never reassigned, so it is effectively final.",
               "`Predicate<String> longer = w -> w.length() > limit;`",
               "The lambda reads `limit`; only the loop writes `count`.",
               "Strictly greater than, so a word of exactly `limit` characters does not "
               "count."]),

        _p25m("j25-pd-longerthan", "longerThan", "Medium",
              "Write `longerThan`, which takes a limit and RETURNS a predicate testing "
              "against it. `main` builds one and counts with it.",
              """
    static Predicate<String> longerThan(int limit) {
        return w -> w.length() > limit;
    }
""",
              _RD_W25P
              + "        int limit = sc.nextInt();\n"
                "        Predicate<String> test = longerThan(limit);\n"
                "        int count = 0;\n"
                "        for (String w : words) {\n"
                "            if (test.test(w)) {\n"
                "                count++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);\n"
                "        System.out.println(limit);",
              [_wl25p(ws, limit, _nl(sum(1 for w in ws if len(w) > limit), limit))
               for (ws, limit) in _WL25P],
              ["The return TYPE is the behaviour: `Predicate<String>`.",
               "The body is a single `return` of a lambda.",
               "A parameter is effectively final unless you assign to it, so capturing "
               "`limit` is legal.",
               "The lambda outlives the call, carrying the captured value - a closure."]),

        _p25m("j25-pd-shorterthan", "shorterThan", "Medium",
              "Write `shorterThan`, the mirror image: it returns a predicate matching "
              "words STRICTLY shorter than the limit.",
              """
    static Predicate<String> shorterThan(int limit) {
        return w -> w.length() < limit;
    }
""",
              _RD_W25P
              + "        int limit = sc.nextInt();\n"
                "        Predicate<String> test = shorterThan(limit);\n"
                "        int count = 0;\n"
                "        for (String w : words) {\n"
                "            if (test.test(w)) {\n"
                "                count++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);\n"
                "        System.out.println(words.size());",
              [_wl25p(ws, limit, _nl(sum(1 for w in ws if len(w) < limit), len(ws)))
               for (ws, limit) in _WL25P],
              ["Same shape as `longerThan`, with the comparison turned around.",
               "`return w -> w.length() < limit;`",
               "Strictly shorter, so a word of exactly `limit` characters does not "
               "count.",
               "Two printed lines: the count, then the whole list's size."]),

        _p25m("j25-pd-prefix", "startingWith", "Medium",
              "Write `startingWith`, which captures a String rather than an int and "
              "returns a predicate matching words that begin with it.",
              """
    static Predicate<String> startingWith(String prefix) {
        return w -> w.startsWith(prefix);
    }
""",
              _RD_W25P
              + "        String prefix = sc.next();\n"
                "        Predicate<String> test = startingWith(prefix);\n"
                "        int count = 0;\n"
                "        for (String w : words) {\n"
                "            if (test.test(w)) {\n"
                "                count++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(count);\n"
                "        System.out.println(prefix);",
              [_wp25p(ws, prefix,
                      _nl(sum(1 for w in ws if w.startswith(prefix)), prefix))
               for (ws, prefix) in _WP25P],
              ["A `String` parameter captures exactly like an `int` one.",
               "`return w -> w.startsWith(prefix);`",
               "Strings are immutable, so there is no way the captured value can change "
               "underneath the lambda.",
               "`startsWith` is module 7's."]),

        _p25b("j25-pd-usefactory", "Using a factory", "Easy",
              "`longerThan` is written for you. Read the limit, build a predicate with "
              "it, and print how many words match, how many do not, and the limit.",
              """
    static Predicate<String> longerThan(int limit) {
        return w -> w.length() > limit;
    }
""",
              _RD_W25P
              + "        int limit = sc.nextInt();\n"
                "        Predicate<String> test = longerThan(limit);\n"
                "        int yes = 0;\n"
                "        int no = 0;\n"
                "        for (String w : words) {\n"
                "            if (test.test(w)) {\n"
                "                yes++;\n"
                "            } else {\n"
                "                no++;\n"
                "            }\n"
                "        }\n"
                "        System.out.println(yes);\n"
                "        System.out.println(no);\n"
                "        System.out.println(limit);",
              [_wl25p(ws, limit, _nl(sum(1 for w in ws if len(w) > limit),
                                     sum(1 for w in ws if len(w) <= limit),
                                     limit))
               for (ws, limit) in _WL25P],
              ["One predicate, asked once per word, with both branches counted.",
               "`Predicate<String> test = longerThan(limit);`",
               "Both counters are locals mutated by the loop - the lambda never touches "
               "them.",
               "The two counts always add up to the list size."]),
    ])


# --- Family E - method references --------------------------------------------

_P25_E = _jfam(
    "p25-methodref", "Method references",
    "When the lambda only forwards, name the method.",
    """
| Kind | Written | Equivalent lambda |
|---|---|---|
| static | `Integer::parseInt` | `s -> Integer.parseInt(s)` |
| bound instance | `System.out::println` | `s -> System.out.println(s)` |
| unbound instance | `String::toUpperCase` | `s -> s.toUpperCase()` |
| constructor | `ArrayList::new` | `() -> new ArrayList<>()` |

The unbound kind is the one to look at twice: the lambda's parameter becomes the
**receiver**, not an argument.

Two places they pay off immediately:

```java
words.sort(Comparator.comparing(String::length));   // sort by an extracted key
words.forEach(System.out::println);                 // Iterable.forEach - no stream
```

If the lambda does anything besides forward, it is not a method reference, and
forcing one reads worse.
""",
    [
        _p25s("j25-pe-foreach", "Printing with a reference", "Intro",
              "Print every word using `forEach` and a bound method reference, then print "
              "the list size.",
              _RD_W25P
              + "        words.forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(*(list(ws) + [len(ws)]))) for ws in _WS25P],
              ["`w -> System.out.println(w)` forwards and does nothing else.",
               "`System.out` is a specific object, so the receiver is fixed - the BOUND "
               "kind.",
               "`words.forEach(System.out::println);`",
               "`forEach` here is `Iterable.forEach`; no stream is involved."]),

        _p25s("j25-pe-comparing", "Sorting by a key", "Easy",
              "Sort the words by length using `Comparator.comparing` and an unbound "
              "method reference, then print the list and its size.",
              _RD_W25P
              + "        words.sort(Comparator.comparing(String::length));\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(_jl25p(sorted(ws, key=len)), len(ws))) for ws in _WS25P],
              ["`Comparator.comparing` takes a `Function` extracting the sort key.",
               "`String::length` is that function, as an unbound reference.",
               "`words.sort(Comparator.comparing(String::length));`",
               "Same answer as the two-parameter lambda, said once instead of twice."]),

        _p25s("j25-pe-parse", "A static method as a value", "Medium",
              "The input is numeric tokens read as text. Hold `Integer.parseInt` in a "
              "`Function` via a static method reference, total the values, and print the "
              "total and the count.",
              _RD_W25P
              + "        Function<String, Integer> parse = Integer::parseInt;\n"
                "        int total = 0;\n"
                "        for (String w : words) {\n"
                "            total += parse.apply(w);\n"
                "        }\n"
                "        System.out.println(total);\n"
                "        System.out.println(words.size());",
              [_w25p([str(x) for x in xs], _nl(sum(xs), len(xs))) for xs in _NS25P],
              ["The lambda would be `s -> Integer.parseInt(s)` - pure forwarding.",
               "`Integer::parseInt` names the class, then the static method.",
               "`Function<String, Integer> parse = Integer::parseInt;`",
               "`parseInt` handles a leading minus sign."]),

        _p25s("j25-pe-upper", "The unbound reference", "Medium",
              "Build a list of the words in capitals using a `Function` written as an "
              "unbound method reference, print each result with `forEach`, then print "
              "the new list's size.",
              _RD_W25P
              + "        Function<String, String> up = String::toUpperCase;\n"
                "        List<String> shouts = new ArrayList<>();\n"
                "        for (String w : words) {\n"
                "            shouts.add(up.apply(w));\n"
                "        }\n"
                "        shouts.forEach(System.out::println);\n"
                "        System.out.println(shouts.size());",
              [_w25p(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _WS25P],
              ["`String::toUpperCase` looks like it is missing an argument - it is not.",
               "The `Function`'s parameter becomes the RECEIVER the method is called "
               "on.",
               "`Function<String, String> up = String::toUpperCase;`",
               "Then `shouts.forEach(System.out::println);` for the printing."]),

        _p25s("j25-pe-both", "Two references, one program", "Medium",
              "Sort the words by length with `Comparator.comparing` and a method "
              "reference, print them with `forEach` and another one, then print the "
              "size.",
              _RD_W25P
              + "        words.sort(Comparator.comparing(String::length));\n"
                "        words.forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w25p(ws, _nl(*(sorted(ws, key=len) + [len(ws)]))) for ws in _WS25P],
              ["One unbound reference for the key, one bound reference for the "
               "printing.",
               "`words.sort(Comparator.comparing(String::length));`",
               "`words.sort` modifies the list in place, so `forEach` then sees the "
               "sorted order.",
               "Stable, so equal-length words keep their input order.",
               "Not a lambda anywhere in the program."]),
    ])


_PRACTICE[25] = [_P25_A, _P25_B, _P25_C, _P25_D, _P25_E]
