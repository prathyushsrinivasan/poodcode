# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 27 - Collecting and reducing.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `.collect(`, `Collectors`, `.reduce(`, `IntStream` and `mapToInt` become legal
# here. `Optional` stays gated to module 28, and that constraint shaped the
# whole module rather than fighting it:
#
#   * `reduce(identity, op)` is taught; the ONE-argument `reduce(op)` returns an
#     Optional and is deferred, which is honest - it is deferred because an
#     empty stream has no answer, which is exactly module 28's subject.
#   * `sum()` returns an int, so it is here. `average()`, `max()` and `min()` on
#     a stream return Optionals, so the module uses `summaryStatistics()`
#     instead - whose getters return plain values. That is also the better tool
#     when you want more than one of them.
#
# DETERMINISM: a `HashMap` and a `HashSet` have no specified iteration order, so
# nothing here ever prints one. Grouping collectors are given `TreeMap::new`, and
# the `toSet` exercise prints only a size. This is not fussiness - printing a
# HashMap is exactly the kind of test that passes for years and then fails on a
# JDK upgrade.
# ---------------------------------------------------------------------------

_M27 = []

_IMPORTS27 = ("import java.util.*;\n"
              "import java.util.function.*;\n"
              "import java.util.stream.*;\n")


def _j27s(body):
    """Scanner-opening main, no helpers."""
    return _jscan(body, imports=_IMPORTS27)


def _j27(helpers, body):
    """Static helper methods above a Scanner-opening main."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS27,
    )


_RD_W27 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N27 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_RD_WN27 = _RD_W27 + ("        int m = sc.nextInt();\n"
                      "        List<Integer> nums = new ArrayList<>();\n"
                      "        for (int i = 0; i < m; i++) {\n"
                      "            nums.add(sc.nextInt());\n"
                      "        }\n")

_W27 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
        ["alpha", "beta", "gamma", "d"])

# Sums divide evenly, so every printed average is a short exact double and there
# is no chance of a Java/Python formatting disagreement.
_N27 = ([3, 1, 2], [5], [-4, -8, -3], [10, 10, 4], [7, 2, 9, 4])

_DUP27 = (["ada", "bo", "ada", "cy"], ["solo", "solo"], ["x", "yy", "x", "x"],
          ["pear", "fig", "pear"], ["a", "b", "a", "b", "c"])


def _w27(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n27(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wn27(ws, xs, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                            " ".join(str(x) for x in xs)]), out)


def _jl27(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _jmap27(pairs):
    """Exactly what a Java `Map.toString()` prints, given ordered pairs."""
    return "{" + ", ".join(f"{k}={v}" for (k, v) in pairs) + "}"


def _bylen27(ws):
    """groupingBy(String::length, TreeMap::new, toList()) - keys ascending,
    values in encounter order."""
    groups = {}
    for w in ws:
        groups.setdefault(len(w), []).append(w)
    return _jmap27([(k, _jl27(groups[k])) for k in sorted(groups)])


def _countlen27(ws):
    """The same grouping, with counting() downstream."""
    groups = {}
    for w in ws:
        groups[len(w)] = groups.get(len(w), 0) + 1
    return _jmap27([(k, groups[k]) for k in sorted(groups)])


def _jdouble27(x):
    """How Java prints a double that happens to be exact to one decimal."""
    return str(float(x))


# --- 27.1 collect ------------------------------------------------------------

_M27.append(_jlesson(
    "m27-collect", "`collect` - getting the results back",
    "The terminal that builds a container instead of printing one.",
    """
Module 26 could filter and map, but the only way to see the result was to print
it element by element. **`collect`** is the terminal that hands you the whole
thing:

```java
List<String> longWords = words.stream()
        .filter(w -> w.length() > 3)
        .collect(Collectors.toList());
```

`collect` takes a **`Collector`**, and `Collectors` is a class full of ready-made
ones. Four cover most days:

| Collector | Gives you |
|---|---|
| `Collectors.toList()` | a `List` of the elements |
| `Collectors.toSet()` | a `Set` - duplicates gone, **order unspecified** |
| `Collectors.joining(", ")` | one `String`, the elements glued together |
| `Collectors.counting()` | a `Long` |

```java
String line = words.stream()
        .map(String::toUpperCase)
        .collect(Collectors.joining(", "));      // "ADA, BO, CY"
```

`joining` also takes a prefix and suffix - `joining(", ", "[", "]")` - which is
how you build a bracketed list without a `StringBuilder` (module 8) doing it by
hand.

**`toSet` gives you a `HashSet`, so its iteration order is not defined.** That
is module 18's rule and it has teeth here: printing a collected set is a test
that passes today and fails on a JDK upgrade. Ask it for its `size()`, or
collect to something ordered.

**`counting()` versus `count()`.** These answer the same question:

```java
words.stream().filter(w -> w.length() > 3).count();                       // long
words.stream().filter(w -> w.length() > 3).collect(Collectors.counting()); // Long
```

Use `count()` when it is the whole question. `counting()` earns its keep as a
**downstream** collector - a collector you hand to *another* collector - which
is the next lesson.
""",
    warmup=[
        _jq("`collect` is…",
            ["a terminal operation", "an intermediate operation",
             "a source", "a Collector"],
            0,
            "It produces the result and runs the pipeline, like every terminal."),
        _jq("Why should you not print a `Collectors.toSet()` result?",
            ["A HashSet has no specified iteration order",
             "It is always empty", "It is not a collection", "It throws"],
            0,
            "Module 18's rule. Print the size, or collect to something ordered."),
    ],
    exercises=[
        _je("j27-col-tolist", "Back into a list",
            "Collect the words longer than three characters into a real `List`, then "
            "print it and its size. Replace `____` with the terminal that builds it.",
            _j27s(_RD_W27
                  + "        List<String> longWords = words.stream()\n"
                    "                .filter(w -> w.length() > 3)\n"
                    "                .collect(Collectors.toList());\n"
                    "        System.out.println(longWords);\n"
                    "        System.out.println(longWords.size());"),
            "                .collect(Collectors.toList());",
            [_w27(ws, _nl(_jl27([w for w in ws if len(w) > 3]),
                          sum(1 for w in ws if len(w) > 3)))
             for ws in _W27],
            hints=["`collect` is the terminal; `Collectors.toList()` is the recipe you "
                   "hand it.",
                   "`.collect(Collectors.toList());`",
                   "The result is an ordinary `List<String>` - it has a `size()`, which "
                   "the stream never did.",
                   "When nothing matches, the collected list prints as `[]` and its size "
                   "is 0."],
            difficulty="Easy"),

        _je("j27-col-joining", "One string out of many",
            "Join the words, in capitals, into a single comma-and-space separated line. "
            "Replace `____` with the collector that does it.",
            _j27s(_RD_W27
                  + "        String line = words.stream()\n"
                    "                .map(String::toUpperCase)\n"
                    "                .collect(Collectors.joining(\", \"));\n"
                    "        System.out.println(line);\n"
                    "        System.out.println(words.size());"),
            "                .collect(Collectors.joining(\", \"));",
            [_w27(ws, _nl(", ".join(w.upper() for w in ws), len(ws))) for ws in _W27],
            hints=["`Collectors.joining` takes the separator as its argument.",
                   "`.collect(Collectors.joining(\", \"));`",
                   "The separator goes BETWEEN elements, so a one-word list has none at "
                   "all.",
                   "This is `String.join` from module 7, reached through a pipeline."],
            difficulty="Easy"),

        _je("j27-col-counting", "Counting as a collector",
            "Count the words longer than three characters using a *collector* rather "
            "than the `count()` terminal - the form that will nest inside `groupingBy` "
            "in the next lesson. Replace `____` with it.",
            _j27s(_RD_W27
                  + "        long total = words.stream()\n"
                    "                .filter(w -> w.length() > 3)\n"
                    "                .collect(Collectors.counting());\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(words.size());"),
            "                .collect(Collectors.counting());",
            [_w27(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws))) for ws in _W27],
            hints=["`Collectors.counting()` takes no arguments.",
                   "`.collect(Collectors.counting());`",
                   "It produces a `Long`, which unboxes into the `long` variable.",
                   "`count()` would have given the same answer more directly - the point "
                   "is that this form can be handed to another collector."],
            difficulty="Medium"),

        _jch("j27-col-toset", "How many are distinct", "Medium",
             "Collect the words into a `Set` to drop duplicates, then print how many "
             "survived and how many there were. Print the SIZE, never the set itself - "
             "a `HashSet` has no defined iteration order.",
             _j27s(_RD_W27
                   + "        Set<String> unique = words.stream()\n"
                     "                .collect(Collectors.toSet());\n"
                     "        System.out.println(unique.size());\n"
                     "        System.out.println(words.size());"),
             "        Set<String> unique = words.stream()\n"
             "                .collect(Collectors.toSet());\n"
             "        System.out.println(unique.size());\n"
             "        System.out.println(words.size());",
             [_w27(ws, _nl(len(set(ws)), len(ws))) for ws in _DUP27],
             hints=["`Collectors.toSet()` takes no arguments and returns a `Set<String>`.",
                    "Duplicates are removed by `equals`/`hashCode`, exactly as in module "
                    "18.",
                    "Printing `unique` directly would be a real bug: the order is not "
                    "specified anywhere.",
                    "`.distinct().count()` from module 26 answers the same question "
                    "without the set.",
                    "Two printed lines: the distinct count, then the original size."]),
    ],
    quiz=[
        _jq("`Collectors.joining(\", \")` on a single-element stream produces…",
            ["just that element, with no separator", "the element and a comma",
             "an empty string", "a list"],
            0,
            "A separator goes between elements; one element has no between."),
        _jq("`counting()` is preferable to `count()` when…",
            ["you need to hand it to another collector as a downstream",
             "always", "never", "the stream is empty"],
            0,
            "As a standalone terminal, `count()` is the simpler tool."),
    ],
))


# --- 27.2 Grouping -----------------------------------------------------------

_M27.append(_jlesson(
    "m27-grouping", "`groupingBy`, `partitioningBy`, `toMap`",
    "Turning a stream into a map - and the downstream collector that makes it powerful.",
    """
**`groupingBy`** is the one you will reach for most. Give it a function that
computes a key, and it buckets the elements:

```java
Map<Integer, List<String>> byLength = words.stream()
        .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList()));
// {1=[d], 4=[beta], 5=[alpha, gamma]}
```

The plain two-argument form gives you a `HashMap`, whose order is undefined -
so every example here passes **`TreeMap::new`** as the map factory and gets keys
in sorted order. That third argument is the **downstream collector**: what to do
with each bucket. `toList()` keeps the elements; `counting()` counts them:

```java
Map<Integer, Long> howMany = words.stream()
        .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));
// {1=1, 4=1, 5=2}
```

That is a frequency table - module 18's `getOrDefault` idiom, in one line.

**`partitioningBy`** is `groupingBy` for a yes/no question. It takes a
`Predicate` and always returns a two-entry map keyed `false` and `true` - both
present, even when one is empty, which is the difference from grouping on a
boolean:

```java
Map<Boolean, List<String>> parts =
        words.stream().collect(Collectors.partitioningBy(w -> w.length() > 3));
parts.get(true);    // the long ones
parts.get(false);   // the rest
```

**`toMap`** builds a map from two functions - one for the key, one for the
value:

```java
Collectors.toMap(w -> w, String::length)
```

and it has a trap worth meeting once: **duplicate keys throw
`IllegalStateException`**. If two elements can produce the same key you must
supply a **merge function** saying which wins:

```java
Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new)
//                                        ^ keep the first    ^ ordered map
```

`groupingBy` never has this problem, because collisions are the whole point of
it.
""",
    warmup=[
        _jq("`groupingBy` with no map factory returns…",
            ["a HashMap - order undefined", "a TreeMap", "a LinkedHashMap",
             "a List"],
            0,
            "Which is why printing one directly is a latent bug."),
        _jq("`toMap` when two elements produce the same key…",
            ["throws IllegalStateException unless you pass a merge function",
             "keeps the first", "keeps the last", "makes a list"],
            0,
            "The merge function is how you say which one wins."),
    ],
    exercises=[
        _je("j27-grp-bylength", "Bucketing by a key",
            "Group the words by their length into a `TreeMap`, so the keys come out in "
            "ascending order, then print the map and how many groups there are. Replace "
            "`____` with the collector.",
            _j27s(_RD_W27
                  + "        Map<Integer, List<String>> byLength = words.stream()\n"
                    "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList()));\n"
                    "        System.out.println(byLength);\n"
                    "        System.out.println(byLength.size());"),
            "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList()));",
            [_w27(ws, _nl(_bylen27(ws), len(set(len(w) for w in ws)))) for ws in _W27],
            hints=["Three arguments: the key function, the map factory, and the "
                   "downstream collector.",
                   "`String::length` is the key function - module 25's unbound method "
                   "reference.",
                   "`TreeMap::new` is a constructor reference, and it is what makes the "
                   "output printable at all.",
                   "`Collectors.toList()` downstream keeps the words in each bucket, in "
                   "encounter order.",
                   "A Java map prints as `{key=value, key=value}`."],
            difficulty="Medium"),

        _je("j27-grp-counting", "A frequency table in one line",
            "Count how many words there are of each length, keys ascending. Replace "
            "`____` with the downstream collector - the rest of the call is already "
            "there.",
            _j27s(_RD_W27
                  + "        Map<Integer, Long> howMany = words.stream()\n"
                    "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));\n"
                    "        System.out.println(howMany);\n"
                    "        System.out.println(howMany.size());"),
            "Collectors.counting()",
            [_w27(ws, _nl(_countlen27(ws), len(set(len(w) for w in ws))))
             for ws in _W27],
            hints=["The downstream collector decides what each bucket becomes.",
                   "`Collectors.counting()` turns each bucket into a `Long`.",
                   "That is why the map's value type is `Long` rather than "
                   "`List<String>`.",
                   "This is module 18's frequency-count idiom, in one line."],
            difficulty="Medium"),

        _je("j27-grp-partition", "Yes and no",
            "Split the words into those longer than three characters and the rest, then "
            "print the long ones, the short ones and the total. Replace `____` with the "
            "collector that splits on a yes/no question.",
            _j27s(_RD_W27
                  + "        Map<Boolean, List<String>> parts = words.stream()\n"
                    "                .collect(Collectors.partitioningBy(w -> w.length() > 3));\n"
                    "        System.out.println(parts.get(true));\n"
                    "        System.out.println(parts.get(false));\n"
                    "        System.out.println(words.size());"),
            "                .collect(Collectors.partitioningBy(w -> w.length() > 3));",
            [_w27(ws, _nl(_jl27([w for w in ws if len(w) > 3]),
                          _jl27([w for w in ws if len(w) <= 3]),
                          len(ws)))
             for ws in _W27],
            hints=["`partitioningBy` takes a `Predicate`, not a key function.",
                   "`.collect(Collectors.partitioningBy(w -> w.length() > 3));`",
                   "Both keys always exist, so `get(true)` is `[]` rather than null when "
                   "nothing matches.",
                   "That guarantee is exactly what `groupingBy` on a boolean would not "
                   "give you."],
            difficulty="Medium"),

        _jfix("j27-grp-tomap", "The map that refused duplicate keys",
              "This builds a map from word to length, and the input repeats a word - so "
              "`toMap` throws `IllegalStateException: Duplicate key`. Supply a merge "
              "function that keeps the first value, and a `TreeMap` factory so the "
              "result prints in a defined order. Then print the map and its size.",
              _j27s(_RD_W27
                    + "        Map<String, Integer> lengths = words.stream()\n"
                      "                .collect(Collectors.toMap(w -> w, String::length));\n"
                      "        System.out.println(lengths);\n"
                      "        System.out.println(lengths.size());"),
              _j27s(_RD_W27
                    + "        Map<String, Integer> lengths = words.stream()\n"
                      "                .collect(Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new));\n"
                      "        System.out.println(lengths);\n"
                      "        System.out.println(lengths.size());"),
              [_w27(ws, _nl(_jmap27([(w, len(w)) for w in sorted(set(ws))]),
                            len(set(ws))))
               for ws in _DUP27],
              hints=["The two-argument `toMap` has no answer when two elements collide, "
                     "so it refuses.",
                     "The third argument is the merge function: given the existing value "
                     "and the new one, which wins.",
                     "`(a, b) -> a` keeps the first. Here both values are equal anyway, "
                     "because the key IS the word.",
                     "The fourth argument is the map factory - `TreeMap::new`, without "
                     "which the printed order is undefined.",
                     "The map has one entry per DISTINCT word, so its size is smaller "
                     "than the list's."],
              difficulty="Hard"),
    ],
    quiz=[
        _jq("The third argument to `groupingBy(f, TreeMap::new, ...)` is…",
            ["the downstream collector - what each bucket becomes",
             "a comparator", "the value type", "a merge function"],
            0,
            "`toList()` keeps them, `counting()` counts them."),
        _jq("`partitioningBy` differs from grouping on a boolean because…",
            ["both true and false keys always exist, even when empty",
             "it is faster", "it returns a List", "it cannot be nested"],
            0,
            "No null checks needed on either side."),
    ],
))


# --- 27.3 reduce -------------------------------------------------------------

_M27.append(_jlesson(
    "m27-reduce", "`reduce` - folding to a single value",
    "Start from an identity, combine two at a time, end with one.",
    """
`collect` builds a container. **`reduce`** builds a single value, by combining
elements two at a time:

```java
int total = nums.stream().reduce(0, (a, b) -> a + b);
```

Read it as a fold: start at `0`, combine with the first element, combine that
result with the second, and so on. Two arguments:

* the **identity** - the starting value, and the answer for an empty stream;
* a **`BinaryOperator<T>`** - two values in, one of the same type out.

```java
nums.stream().reduce(0, (a, b) -> a + b);        // sum,     identity 0
nums.stream().reduce(1, (a, b) -> a * b);        // product, identity 1
words.stream().reduce("", (a, b) -> a + b);      // concat,  identity ""
```

**The identity must be neutral.** `0` for `+`, `1` for `*`, `""` for
concatenation - combining it with anything must give that thing back. Pick a
non-neutral identity and you get a wrong answer rather than an error, which is
what makes this worth stating: `reduce(1, (a, b) -> a + b)` silently returns one
too many.

**The operator should be associative** - `(a op b) op c` must equal
`a op (b op c)` - because that is what lets the same code run in parallel. Sum
and product are; subtraction is not.

**There is a one-argument `reduce(op)`**, with no identity. It cannot return a
plain value, because an empty stream would have no answer at all - so it returns
an `Optional`, and that is module 28's subject. Until then, always give an
identity.

**When not to use it.** `reduce` is general enough to do almost anything, which
is not the same as being the clearest way. Summing a list of lengths reads
better as `mapToInt(String::length).sum()` - the next lesson - and building a
String with `reduce("", (a, b) -> a + b)` is the O(n²) concatenation module 8
warned about, in new clothes. Reach for `reduce` when there is no named
operation that already says what you mean.
""",
    warmup=[
        _jq("`nums.stream().reduce(0, (a, b) -> a + b)` on an EMPTY stream returns…",
            ["0 - the identity", "null", "an exception", "an Optional"],
            0,
            "That is exactly what the identity is for."),
        _jq("Why must the identity be neutral for the operator?",
            ["Otherwise it silently changes the answer",
             "It would throw", "For parallelism only", "It need not be"],
            0,
            "`reduce(1, (a, b) -> a + b)` returns one too many - and never complains."),
    ],
    exercises=[
        _je("j27-red-sum", "Folding to a total",
            "Add up the numbers with `reduce`, then print the total and the count. "
            "Replace `____` with the fold.",
            _j27s(_RD_N27
                  + "        int total = nums.stream().reduce(0, (a, b) -> a + b);\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(nums.size());"),
            "        int total = nums.stream().reduce(0, (a, b) -> a + b);",
            [_n27(xs, _nl(sum(xs), len(xs))) for xs in _N27],
            hints=["Two arguments: the identity, then the operator.",
                   "The neutral value for addition is `0`.",
                   "`nums.stream().reduce(0, (a, b) -> a + b)`",
                   "The result is an `Integer`, unboxed into the `int` variable."],
            difficulty="Easy"),

        _je("j27-red-product", "A different identity",
            "Multiply the numbers together with `reduce`. The identity is not zero this "
            "time - a zero would make every answer zero. Replace `____` with the fold.",
            _j27s(_RD_N27
                  + "        int product = nums.stream().reduce(1, (a, b) -> a * b);\n"
                    "        System.out.println(product);\n"
                    "        System.out.println(nums.size());"),
            "        int product = nums.stream().reduce(1, (a, b) -> a * b);",
            [_n27(xs, _nl(eval("*".join(str(x) for x in xs)), len(xs))) for xs in _N27],
            hints=["The neutral value for multiplication is `1`.",
                   "`nums.stream().reduce(1, (a, b) -> a * b)`",
                   "Starting from `0` would return `0` for every input, with no error at "
                   "all.",
                   "One of these lists has an odd number of negatives, so its product is "
                   "negative."],
            difficulty="Medium"),

        _je("j27-red-concat", "Folding strings",
            "Glue all the words together into one string with `reduce`, then print it "
            "and its length. Replace `____` with the fold.",
            _j27s(_RD_W27
                  + "        String joined = words.stream().reduce(\"\", (a, b) -> a + b);\n"
                    "        System.out.println(joined);\n"
                    "        System.out.println(joined.length());"),
            "        String joined = words.stream().reduce(\"\", (a, b) -> a + b);",
            [_w27(ws, _nl("".join(ws), sum(len(w) for w in ws))) for ws in _W27],
            hints=["The neutral value for concatenation is the empty string.",
                   "`words.stream().reduce(\"\", (a, b) -> a + b)`",
                   "There is no separator, so the words run together.",
                   "`Collectors.joining()` is the better tool for this - it uses a "
                   "StringBuilder internally, where this fold builds a new String every "
                   "step.",
                   "That is module 8's O(n²) concatenation, wearing a stream."],
            difficulty="Medium"),

        _jch("j27-red-longest", "Folding to a choice", "Hard",
             "A fold does not have to combine - it can choose. Use `reduce` to find the "
             "longest word, keeping the earlier one when two tie, then print it and its "
             "length.",
             _j27s(_RD_W27
                   + "        String longest = words.stream()\n"
                     "                .reduce(\"\", (a, b) -> b.length() > a.length() ? b : a);\n"
                     "        System.out.println(longest);\n"
                     "        System.out.println(longest.length());"),
             "        String longest = words.stream()\n"
             "                .reduce(\"\", (a, b) -> b.length() > a.length() ? b : a);\n"
             "        System.out.println(longest);\n"
             "        System.out.println(longest.length());",
             [_w27(ws, _nl(max(ws, key=len) if ws else "",
                           len(max(ws, key=len)) if ws else 0))
              for ws in _W27],
             hints=["The identity is `\"\"` - length zero, so any real word beats it.",
                    "The operator returns one of its two arguments rather than combining "
                    "them.",
                    "`(a, b) -> b.length() > a.length() ? b : a`",
                    "Strictly greater keeps the EARLIER word on a tie, which is what the "
                    "prompt asks for.",
                    "`max(Comparator)` would say this more directly - but it returns an "
                    "Optional, which is module 28."]),
    ],
    quiz=[
        _jq("`words.stream().reduce(\"\", (a, b) -> a + b)` compared with `Collectors.joining()`…",
            ["builds a new String at every step - the O(n²) trap from module 8",
             "is faster", "is identical", "does not compile"],
            0,
            "`joining` uses a StringBuilder internally."),
        _jq("The one-argument `reduce(op)` returns an `Optional` because…",
            ["an empty stream has no answer without an identity",
             "it is deprecated", "of erasure", "it may throw"],
            0,
            "Which is why this module always supplies one."),
    ],
))


# --- 27.4 Primitive streams --------------------------------------------------

_M27.append(_jlesson(
    "m27-primitive", "Primitive streams",
    "`Stream<Integer>` boxes every element. `IntStream` does not - and it can add up.",
    """
`Stream<Integer>` holds *objects*. Every `int` that goes in is autoboxed, and
every one that comes out is unboxed - and the stream has no `sum()`, because
`Stream<T>` cannot know how to add an arbitrary `T`.

**`mapToInt`** switches to an `IntStream`, which does:

```java
int total = words.stream()
        .mapToInt(String::length)     // Stream<String> -> IntStream
        .sum();
```

`IntStream` (and `LongStream`, `DoubleStream`) hold primitives, so no boxing
happens, and they add the numeric operations `Stream` cannot have: `sum()`,
`average()`, `max()`, `min()`, `summaryStatistics()`.

**`summaryStatistics()` gives you everything at once**, in one pass:

```java
IntSummaryStatistics stats = nums.stream().mapToInt(Integer::intValue).summaryStatistics();
stats.getCount();     // long
stats.getSum();       // long
stats.getMin();       // int
stats.getMax();       // int
stats.getAverage();   // double
```

Every one of those getters returns a plain value. That matters: `average()`,
`max()` and `min()` called directly on an `IntStream` return `OptionalDouble`
and `OptionalInt`, because an empty stream has no average and no maximum - and
that is module 28. `summaryStatistics()` sidesteps it, and is the better choice
anyway whenever you want more than one of the five.

**`boxed()` goes back the other way**, turning an `IntStream` into a
`Stream<Integer>` so you can `collect` it - because a stream of primitives has
nothing to put in a `List`:

```java
List<Integer> lengths = words.stream()
        .mapToInt(String::length)
        .boxed()
        .collect(Collectors.toList());
```

**When to bother.** For a handful of elements the boxing costs nothing and
`mapToInt` is just the clearest way to say "now these are numbers". For large
volumes it is a real difference - no `Integer` object per element. Either way,
`mapToInt(...).sum()` reads better than `reduce(0, Integer::sum)`.
""",
    warmup=[
        _jq("Why does `Stream<Integer>` have no `sum()`?",
            ["`Stream<T>` cannot know how to add an arbitrary T",
             "It was forgotten", "It is deprecated", "It does have one"],
            0,
            "`mapToInt` gives you an `IntStream`, which does."),
        _jq("`boxed()` exists to…",
            ["turn an IntStream back into a Stream<Integer> so it can be collected",
             "improve performance", "remove nulls", "sort the stream"],
            0,
            "A primitive stream has nothing to put in a `List`."),
    ],
    exercises=[
        _je("j27-prim-sum", "Adding up lengths",
            "Total the lengths of all the words. Replace `____` with the operation that "
            "turns the stream of Strings into a stream of numbers.",
            _j27s(_RD_W27
                  + "        int total = words.stream()\n"
                    "                .mapToInt(String::length)\n"
                    "                .sum();\n"
                    "        System.out.println(total);\n"
                    "        System.out.println(words.size());"),
            "                .mapToInt(String::length)",
            [_w27(ws, _nl(sum(len(w) for w in ws), len(ws))) for ws in _W27],
            hints=["`map(String::length)` would give a `Stream<Integer>`, which has no "
                   "`sum()`.",
                   "`mapToInt` produces an `IntStream`, which does.",
                   "`.mapToInt(String::length)`",
                   "`sum()` returns a plain `int` - no Optional anywhere."],
            difficulty="Easy"),

        _je("j27-prim-stats", "Five answers in one pass",
            "Report the count, sum, minimum, maximum and average of the numbers. Replace "
            "`____` with the line that computes all five at once.",
            _j27s(_RD_N27
                  + "        IntSummaryStatistics stats = nums.stream().mapToInt(Integer::intValue).summaryStatistics();\n"
                    "        System.out.println(stats.getCount());\n"
                    "        System.out.println(stats.getSum());\n"
                    "        System.out.println(stats.getMin());\n"
                    "        System.out.println(stats.getMax());\n"
                    "        System.out.println(stats.getAverage());"),
            "        IntSummaryStatistics stats = nums.stream().mapToInt(Integer::intValue).summaryStatistics();",
            [_n27(xs, _nl(len(xs), sum(xs), min(xs), max(xs),
                          _jdouble27(sum(xs) / len(xs))))
             for xs in _N27],
            hints=["`Integer::intValue` is the unbound method reference that unboxes "
                   "each element.",
                   "`summaryStatistics()` is a terminal returning an "
                   "`IntSummaryStatistics`.",
                   "Every getter returns a plain value - `getAverage()` is a `double`, "
                   "not an OptionalDouble.",
                   "Calling `.average()` directly would return an `OptionalDouble`, "
                   "which is module 28.",
                   "The averages here all come out exact, so they print with a single "
                   "decimal place."],
            difficulty="Medium"),

        _je("j27-prim-boxed", "Back to objects",
            "Collect the word lengths into a `List<Integer>`. An `IntStream` cannot be "
            "collected, so it has to become a stream of objects first. Replace `____` "
            "with that step.",
            _j27s(_RD_W27
                  + "        List<Integer> lengths = words.stream()\n"
                    "                .mapToInt(String::length)\n"
                    "                .boxed()\n"
                    "                .collect(Collectors.toList());\n"
                    "        System.out.println(lengths);\n"
                    "        System.out.println(lengths.size());"),
            "                .boxed()",
            [_w27(ws, _nl(_jl27([len(w) for w in ws]), len(ws))) for ws in _W27],
            hints=["A `List` holds objects, and an `IntStream` holds primitives.",
                   "`.boxed()` takes no arguments and returns a `Stream<Integer>`.",
                   "Only then does `.collect(Collectors.toList())` become available.",
                   "`map(String::length)` would have avoided the round trip entirely - "
                   "this route is worth doing once to see why `boxed` exists."],
            difficulty="Medium"),

        _jch("j27-prim-report", "Numbers from both lists", "Medium",
             "Print four lines: the sum of the numbers, the sum of the word lengths, the "
             "longest word's length, and how many words there are.",
             _j27s(_RD_WN27
                   + "        System.out.println(nums.stream().mapToInt(Integer::intValue).sum());\n"
                     "        System.out.println(words.stream().mapToInt(String::length).sum());\n"
                     "        System.out.println(words.stream().mapToInt(String::length).summaryStatistics().getMax());\n"
                     "        System.out.println(words.size());"),
             "        System.out.println(nums.stream().mapToInt(Integer::intValue).sum());\n"
             "        System.out.println(words.stream().mapToInt(String::length).sum());\n"
             "        System.out.println(words.stream().mapToInt(String::length).summaryStatistics().getMax());\n"
             "        System.out.println(words.size());",
             [_wn27(ws, xs, _nl(sum(xs), sum(len(w) for w in ws),
                                max(len(w) for w in ws), len(ws)))
              for (ws, xs) in zip(_W27, _N27)],
             hints=["`Integer::intValue` unboxes; `String::length` extracts - both give "
                    "an `IntStream`.",
                    "Each question needs its own fresh stream.",
                    "`summaryStatistics().getMax()` returns a plain `int`; "
                    "`IntStream.max()` would return an `OptionalInt`.",
                    "For a single statistic either reads fine - the summary object earns "
                    "its keep when you want several.",
                    "Four printed lines."]),
    ],
    quiz=[
        _jq("`nums.stream().mapToInt(Integer::intValue).average()` returns…",
            ["an OptionalDouble - an empty stream has no average",
             "a double", "an int", "a Double"],
            0,
            "Which is why this module uses `summaryStatistics().getAverage()`."),
        _jq("`mapToInt(String::length).sum()` versus `reduce(0, Integer::sum)`…",
            ["the first avoids boxing and says what it means",
             "they are identical", "the second is faster",
             "the first does not compile"],
            0,
            "Reach for `reduce` when no named operation already says it."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M27_CAP_BODY = (
    _RD_W27
    + "        System.out.println(words.stream()\n"
      "                .filter(w -> w.length() > 2)\n"
      "                .collect(Collectors.toList()));\n"
      "        System.out.println(words.stream()\n"
      "                .map(String::toUpperCase)\n"
      "                .collect(Collectors.joining(\", \")));\n"
      "        System.out.println(words.stream()\n"
      "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting())));\n"
      "        System.out.println(words.stream().reduce(\"\", (a, b) -> a + b));\n"
      "        System.out.println(words.stream().mapToInt(String::length).sum());\n"
      "        System.out.println(words.size());"
)


def _m27_cap_case(ws):
    return _w27(ws, _nl(_jl27([w for w in ws if len(w) > 2]),
                        ", ".join(w.upper() for w in ws),
                        _countlen27(ws),
                        "".join(ws),
                        sum(len(w) for w in ws),
                        len(ws)))


_M27_CAP = _jcap(
    "The word ledger",
    """
Six lines, one per tool this module added.

1. **`collect(toList())`** - the words longer than two characters, as a real
   `List`.
2. **`collect(joining(", "))`** - all of them in capitals, on one line.
3. **`groupingBy(..., TreeMap::new, counting())`** - a frequency table of word
   lengths, keys ascending.
4. **`reduce("", ...)`** - every word glued together, no separator.
5. **`mapToInt(...).sum()`** - the total number of characters.
6. The source list's size, unchanged.

Two details are the point of the exercise. The grouping passes **`TreeMap::new`**
because a `HashMap`'s iteration order is not specified and printing one is a bug
waiting for a JDK upgrade. And line 4 uses `reduce` where line 2 uses `joining` -
the same job done two ways, one of which builds a new String at every step.
""",
    _jch("j27-cap-ledger", "The word ledger", "Hard",
         "Write the six lines described in the brief, in order.",
         _j27s(_M27_CAP_BODY),
         _M27_CAP_BODY,
         [_m27_cap_case(ws) for ws in _DUP27],
         hints=["Every line needs its own fresh stream - one terminal each.",
                "Line 1: `.filter(w -> w.length() > 2).collect(Collectors.toList())`.",
                "Line 2: `.map(String::toUpperCase).collect(Collectors.joining(\", \"))`.",
                "Line 3: `groupingBy(String::length, TreeMap::new, "
                "Collectors.counting())` - three arguments, and the TreeMap is what "
                "makes the output defined.",
                "Line 4: `reduce(\"\", (a, b) -> a + b)` - identity first, then the "
                "operator.",
                "Line 5: `mapToInt(String::length).sum()`, not `map(...)`, which would "
                "have no `sum()`.",
                "The input repeats words, so the frequency table's counts are larger "
                "than the number of distinct words.",
                "Line 6 is just `words.size()` - nothing in the pipeline changed it."]),
    example_io="stdin:  4\n        ada bo ada cy\n\n"
               "stdout: [ada, ada]\n        ADA, BO, ADA, CY\n        {2=2, 3=2}\n"
               "        adaboadacy\n        10\n        4",
    rubric=[
        "Each of the six lines builds its own stream from the source.",
        "`toList` and `joining` are used through `collect`, not hand-rolled.",
        "The grouping passes `TreeMap::new`, so the printed key order is defined.",
        "`counting()` is used as the downstream collector, giving a `Long` per bucket.",
        "`reduce` supplies an identity of `\"\"` and a binary operator.",
        "The character total uses `mapToInt(...).sum()`, not `reduce`.",
        "Nothing prints a `HashMap` or a `HashSet`.",
        "The six lines appear in the order the brief lists them.",
    ],
)


_MODULES.append(_jmod(
    27, 8, "Java 8+",
    "Collecting and reducing",
    "The terminals that give you something back: a container via `collect`, a single "
    "value via `reduce`, and the primitive streams that can add up.",
    """
Module 26 could shape a stream but could only print the result. This module is
the other half - the terminals that hand you an answer.

* **`collect`** takes a `Collector`. `toList()`, `toSet()`, `joining(", ")` and
  `counting()` cover most days.
* **`groupingBy`** buckets by a key, and its third argument - the **downstream
  collector** - decides what each bucket becomes: `toList()` to keep them,
  `counting()` for a frequency table in one line. **`partitioningBy`** is the
  yes/no version, and always has both keys. **`toMap`** throws on duplicate keys
  unless you pass a merge function.
* **`reduce(identity, op)`** folds to a single value. The identity must be
  neutral, and it is the answer for an empty stream. (The one-argument form
  returns an `Optional` - module 28.)
* **`mapToInt`** gives an `IntStream`, which does not box and which has the
  numeric operations `Stream<Integer>` cannot: `sum()` and
  `summaryStatistics()`. `boxed()` goes back so you can collect.

One habit runs through all of it: **never print a `HashMap` or a `HashSet`.**
Their iteration order is unspecified, so every grouping example here passes
`TreeMap::new`.
""",
    _M27,
    capstone=_M27_CAP,
    objectives=[
        "Use `collect` with `toList`, `toSet`, `joining` and `counting`.",
        "Say why a collected `Set` or a `HashMap` must not be printed, and what to do instead.",
        "Group by a key with `groupingBy`, and choose the downstream collector.",
        "Build a frequency table with `groupingBy` plus `counting`.",
        "Use `partitioningBy`, and say how it differs from grouping on a boolean.",
        "Use `toMap`, and fix the duplicate-key failure with a merge function.",
        "Fold with `reduce(identity, op)`, and explain why the identity must be neutral.",
        "Say why the one-argument `reduce` returns an `Optional`.",
        "Use `mapToInt`, `sum`, `summaryStatistics` and `boxed`, and say what boxing costs.",
    ],
    why="`collect` and `groupingBy` are where streams stop being a nicer loop and start "
        "replacing whole methods - a frequency table that was fifteen lines in module 18 "
        "is one line here. Interviews ask for exactly this: group these records by a "
        "field, count them, and give me a map. The `reduce` identity and the duplicate-key "
        "`toMap` failure are both standard follow-up questions, and both have precise "
        "answers.",
    est_minutes=330,
    glossary=[
        _jg("collect", "The terminal operation that accumulates elements into a "
                       "container, driven by a `Collector`."),
        _jg("Collector", "The recipe `collect` follows. `Collectors` is a factory class "
                         "full of them."),
        _jg("joining", "A collector producing one String, optionally with a separator, "
                       "prefix and suffix."),
        _jg("groupingBy", "A collector that buckets elements by a key function, "
                          "producing a Map."),
        _jg("downstream collector", "The collector applied to each bucket - `toList()` "
                                    "keeps the elements, `counting()` counts them."),
        _jg("partitioningBy", "`groupingBy` for a predicate: always exactly two keys, "
                              "`false` and `true`, both present."),
        _jg("toMap", "A collector building a Map from a key function and a value "
                     "function. Throws on duplicate keys without a merge function."),
        _jg("merge function", "The third argument to `toMap`, deciding which value wins "
                              "when two elements produce the same key."),
        _jg("reduce", "The fold: an identity plus a binary operator, combining the stream "
                      "down to one value."),
        _jg("identity", "`reduce`'s starting value, and its answer for an empty stream. "
                        "Must be neutral for the operator."),
        _jg("IntStream", "A stream of primitive ints - no boxing, and it has `sum()`, "
                         "`average()` and `summaryStatistics()`."),
        _jg("boxed", "Turns a primitive stream back into a `Stream<Integer>` so it can be "
                     "collected."),
    ],
    cheatsheet="""
```java
// --- collect --------------------------------------------------------------
.collect(Collectors.toList())
.collect(Collectors.toSet())            // HashSet - NEVER print it, order undefined
.collect(Collectors.joining(", "))      // one String; also joining(sep, prefix, suffix)
.collect(Collectors.counting())         // Long - use count() unless nesting it

// --- to a map -------------------------------------------------------------
Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList())
// {1=[d], 4=[beta], 5=[alpha, gamma]}
Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting())
// {1=1, 4=1, 5=2}    <- a frequency table, in one line

Collectors.partitioningBy(w -> w.length() > 3)   // always has BOTH false and true
Collectors.toMap(w -> w, String::length)         // IllegalStateException on a dup key
Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new)   // merge + ordered

// TreeMap::new is not optional styling - a HashMap's print order is undefined.

// --- reduce ---------------------------------------------------------------
nums.stream().reduce(0, (a, b) -> a + b);      // identity 0   - and the empty answer
nums.stream().reduce(1, (a, b) -> a * b);      // identity 1
words.stream().reduce("", (a, b) -> a + b);    // O(n^2) - prefer joining()
// reduce(op) with no identity -> Optional -> module 28

// --- primitive streams ----------------------------------------------------
words.stream().mapToInt(String::length).sum();          // int   (Stream has no sum)
nums.stream().mapToInt(Integer::intValue).summaryStatistics();
    // .getCount() .getSum() .getMin() .getMax() .getAverage()   all plain values
.average() / .max() / .min()      // OptionalDouble / OptionalInt -> module 28
.boxed().collect(Collectors.toList())   // IntStream -> Stream<Integer> -> List
```
""",
    self_check=[
        "Can you collect a filtered stream into a List, and say why the stream had no `size()`?",
        "Can you say why printing a collected `Set` is a latent bug?",
        "Can you write a frequency table with `groupingBy` and `counting` in one line?",
        "Can you say what the third argument to `groupingBy` does?",
        "Can you say how `partitioningBy` differs from grouping on a boolean?",
        "Can you fix a `toMap` that throws on duplicate keys?",
        "Can you explain what `reduce`'s identity is for, and what a non-neutral one does?",
        "Can you say why the one-argument `reduce` returns an `Optional`?",
        "Can you say why `Stream<Integer>` has no `sum()`, and what `boxed()` is for?",
    ],
    review=[
        _jq("```java\nwords.stream().collect(Collectors.groupingBy(String::length));\n```\nWhat is wrong with printing the result?",
            ["It is a HashMap - the iteration order is unspecified",
             "It does not compile", "It is always empty", "Nothing"],
            0,
            "Pass `TreeMap::new` when the output has to be defined."),
        _jq("`Collectors.toMap(w -> w, String::length)` on a list with a repeated word…",
            ["throws IllegalStateException", "keeps the first", "keeps the last",
             "returns an empty map"],
            0,
            "Supply a merge function to say which value wins."),
        _jq("`nums.stream().reduce(1, (a, b) -> a + b)` returns…",
            ["the sum plus one - a non-neutral identity, and no error",
             "the sum", "the product", "a compile error"],
            0,
            "Which is what makes the neutrality rule worth stating."),
        _jq("Why use `mapToInt(String::length).sum()` rather than `map(String::length)`?",
            ["`Stream<Integer>` has no `sum()`, and mapToInt avoids boxing",
             "It is shorter", "map is deprecated", "They are the same"],
            0,
            "`Stream<T>` cannot know how to add an arbitrary `T`."),
    ],
    milestone="You can turn a pipeline into an answer: a list, a joined line, a grouped "
              "or partitioned map, a folded value, or a set of statistics - and you know "
              "which of those quietly depend on an unspecified iteration order, and how "
              "to pin them down.",
))
