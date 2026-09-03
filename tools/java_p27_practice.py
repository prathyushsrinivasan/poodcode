# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 27 practice - collecting and reducing.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[27]`.
#
# Same two constraints as the module file, and for the same reasons:
#
#   * `Optional` is module 28, so `reduce` always gets an identity, and the
#     numeric summaries come from `summaryStatistics()` (plain getters) rather
#     than `average()` / `max()` / `min()` (which return Optionals).
#   * NOTHING prints a HashMap or a HashSet. Every grouping collector is given
#     `TreeMap::new`, and the set exercises print a size. An unspecified
#     iteration order is not a test, it is a coin flip.
#
# Averages are only ever taken over lists whose sum divides evenly, so every
# printed double is short and exact.
# ---------------------------------------------------------------------------

_IMPORTS27P = ("import java.util.*;\n"
               "import java.util.function.*;\n"
               "import java.util.stream.*;\n")


def _p27prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS27P,
    )


def _p27m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p27prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p27b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p27prog(helpers, body),
                body, tests, hints)


def _p27s(eid, title, difficulty, prompt, body, tests, hints):
    """No helpers - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan(body, imports=_IMPORTS27P), body, tests, hints)


_RD_W27P = ("        int n = sc.nextInt();\n"
            "        List<String> words = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words.add(sc.next());\n"
            "        }\n")

_RD_N27P = ("        int n = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")

_WS27P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS27P = ([3, 1, 2], [5], [-4, -8, -3], [10, 10, 4], [7, 2, 9, 4])

_DUP27P = (["ada", "bo", "ada", "cy"], ["solo", "solo"], ["x", "yy", "x", "x"],
           ["pear", "fig", "pear"], ["a", "b", "a", "b", "c"])


def _w27p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n27p(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jl27p(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _jm27p(pairs):
    return "{" + ", ".join(f"{k}={v}" for (k, v) in pairs) + "}"


def _grouplist27p(ws, key):
    groups = {}
    for w in ws:
        groups.setdefault(key(w), []).append(w)
    return _jm27p([(k, _jl27p(groups[k])) for k in sorted(groups)])


def _groupcount27p(ws, key):
    groups = {}
    for w in ws:
        groups[key(w)] = groups.get(key(w), 0) + 1
    return _jm27p([(k, groups[k]) for k in sorted(groups)])


def _prod27p(xs):
    total = 1
    for x in xs:
        total *= x
    return total


# --- Family A - collect ------------------------------------------------------

_P27_A = _jfam(
    "p27-collect", "`collect` and the everyday collectors",
    "Getting a container back instead of printing one element at a time.",
    """
```java
.collect(Collectors.toList())        // a List
.collect(Collectors.toSet())         // a Set - order UNDEFINED, never print it
.collect(Collectors.joining(", "))   // one String
.collect(Collectors.counting())      // a Long
```

`collect` is the terminal; `Collectors` is the factory class of recipes it
follows.

`joining` also takes a prefix and suffix - `joining(", ", "[", "]")` - which
builds a bracketed list without touching a `StringBuilder`.

And `toSet` gives you a `HashSet`, whose iteration order is not specified
anywhere. Ask it for its `size()`.
""",
    [
        _p27s("j27-pa-tolist", "Into a list", "Intro",
              "Collect the words longer than three characters into a `List`, then print "
              "it and its size.",
              _RD_W27P
              + "        List<String> longWords = words.stream()\n"
                "                .filter(w -> w.length() > 3)\n"
                "                .collect(Collectors.toList());\n"
                "        System.out.println(longWords);\n"
                "        System.out.println(longWords.size());",
              [_w27p(ws, _nl(_jl27p([w for w in ws if len(w) > 3]),
                             sum(1 for w in ws if len(w) > 3)))
               for ws in _WS27P],
              ["`collect` is the terminal, `Collectors.toList()` the recipe.",
               "The result is a real `List` - it has a `size()`, which the stream did "
               "not.",
               "An empty result prints as `[]`.",
               "Two printed lines."]),

        _p27s("j27-pa-joining", "Into one string", "Intro",
              "Join the words in capitals into a single comma-and-space separated line, "
              "then print the list size.",
              _RD_W27P
              + "        String line = words.stream()\n"
                "                .map(String::toUpperCase)\n"
                "                .collect(Collectors.joining(\", \"));\n"
                "        System.out.println(line);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(", ".join(w.upper() for w in ws), len(ws)))
               for ws in _WS27P],
              ["`Collectors.joining(\", \")` takes the separator.",
               "Map to capitals before joining.",
               "A one-word list produces no separator at all.",
               "This is `String.join` from module 7, through a pipeline."]),

        _p27s("j27-pa-brackets", "With a prefix and suffix", "Easy",
              "Join the words into a single string wrapped in angle brackets and "
              "separated by ` | `, then print the list size.",
              _RD_W27P
              + "        String line = words.stream()\n"
                "                .collect(Collectors.joining(\" | \", \"<\", \">\"));\n"
                "        System.out.println(line);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl("<" + " | ".join(ws) + ">", len(ws))) for ws in _WS27P],
              ["`joining` is overloaded with three arguments: separator, prefix, "
               "suffix.",
               "`Collectors.joining(\" | \", \"<\", \">\")`",
               "The prefix and suffix appear even for a one-element stream.",
               "No `StringBuilder` anywhere, which is the point."]),

        _p27s("j27-pa-toset", "How many are distinct", "Easy",
              "Collect the words into a `Set` and print how many survived, then how many "
              "there were. Print sizes only - a `HashSet` has no defined order.",
              _RD_W27P
              + "        Set<String> unique = words.stream()\n"
                "                .collect(Collectors.toSet());\n"
                "        System.out.println(unique.size());\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(len(set(ws)), len(ws))) for ws in _DUP27P],
              ["`Collectors.toSet()` takes no arguments.",
               "Duplicates go by `equals`/`hashCode` - module 18.",
               "Printing the set itself would be a real bug: the order is unspecified.",
               "`.distinct().count()` answers the same question without the set."]),

        _p27s("j27-pa-counting", "Counting as a collector", "Medium",
              "Count the words longer than three characters with `Collectors.counting()` "
              "rather than `count()`, then print the list size.",
              _RD_W27P
              + "        long total = words.stream()\n"
                "                .filter(w -> w.length() > 3)\n"
                "                .collect(Collectors.counting());\n"
                "        System.out.println(total);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws)))
               for ws in _WS27P],
              ["`Collectors.counting()` takes no arguments and produces a `Long`.",
               "It unboxes into the `long` variable.",
               "`count()` would be the simpler tool standing alone.",
               "The reason to know this form is that it nests inside `groupingBy`."]),
    ])


# --- Family B - grouping -----------------------------------------------------

_P27_B = _jfam(
    "p27-grouping", "`groupingBy`, `partitioningBy`, `toMap`",
    "A stream into a map - and the downstream collector that decides what a bucket becomes.",
    """
```java
Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList())
// {1=[d], 4=[beta], 5=[alpha, gamma]}
Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting())
// {1=1, 4=1, 5=2}     <- a frequency table
```

The third argument is the **downstream collector**. `TreeMap::new` is the second,
and it is not optional styling: the two-argument form gives a `HashMap` whose
print order is undefined.

**`partitioningBy(predicate)`** always returns exactly two keys, `false` and
`true`, both present even when one bucket is empty.

**`toMap(keyFn, valueFn)`** throws `IllegalStateException` on a duplicate key.
Add a merge function - and a map factory if you intend to print it:

```java
Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new)
```
""",
    [
        _p27s("j27-pb-bylength", "Grouped by length", "Easy",
              "Group the words by length into a `TreeMap` so the keys are ascending, "
              "then print the map and how many groups there are.",
              _RD_W27P
              + "        Map<Integer, List<String>> byLength = words.stream()\n"
                "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList()));\n"
                "        System.out.println(byLength);\n"
                "        System.out.println(byLength.size());",
              [_w27p(ws, _nl(_grouplist27p(ws, len), len(set(len(w) for w in ws))))
               for ws in _WS27P],
              ["Three arguments: key function, map factory, downstream collector.",
               "`String::length` for the key, `TreeMap::new` for defined order.",
               "`Collectors.toList()` downstream keeps the words in encounter order.",
               "A Java map prints as `{key=value, key=value}`."]),

        _p27s("j27-pb-frequency", "A frequency table", "Easy",
              "Count how many words there are of each length, keys ascending, then print "
              "the map and the list size.",
              _RD_W27P
              + "        Map<Integer, Long> howMany = words.stream()\n"
                "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));\n"
                "        System.out.println(howMany);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(_groupcount27p(ws, len), len(ws))) for ws in _WS27P],
              ["Only the downstream collector changes from the previous problem.",
               "`Collectors.counting()` makes each bucket a `Long`.",
               "So the map's value type is `Long`, not `List<String>`.",
               "This is module 18's `getOrDefault` frequency idiom in one line."]),

        _p27s("j27-pb-firstletter", "Grouped by first letter", "Medium",
              "Group the words by their first character into a `TreeMap`, then print the "
              "map and how many groups there are.",
              _RD_W27P
              + "        Map<Character, List<String>> byFirst = words.stream()\n"
                "                .collect(Collectors.groupingBy(w -> w.charAt(0), TreeMap::new, Collectors.toList()));\n"
                "        System.out.println(byFirst);\n"
                "        System.out.println(byFirst.size());",
              [_w27p(ws, _nl(_grouplist27p(ws, lambda w: w[0]),
                             len(set(w[0] for w in ws))))
               for ws in _WS27P],
              ["The key is a `Character`, so the map is `Map<Character, "
               "List<String>>`.",
               "`w -> w.charAt(0)` is the key function - a lambda, since there is no "
               "method reference for it.",
               "`Character` is `Comparable`, so a `TreeMap` orders the keys "
               "alphabetically.",
               "Words sharing a first letter land in one bucket, in encounter order."]),

        _p27s("j27-pb-partition", "Yes and no", "Medium",
              "Split the words into those longer than three characters and the rest. "
              "Print the long ones, the short ones, and the total.",
              _RD_W27P
              + "        Map<Boolean, List<String>> parts = words.stream()\n"
                "                .collect(Collectors.partitioningBy(w -> w.length() > 3));\n"
                "        System.out.println(parts.get(true));\n"
                "        System.out.println(parts.get(false));\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(_jl27p([w for w in ws if len(w) > 3]),
                             _jl27p([w for w in ws if len(w) <= 3]),
                             len(ws)))
               for ws in _WS27P],
              ["`partitioningBy` takes a `Predicate`, not a key function.",
               "Both keys always exist, so an empty side is `[]` rather than null.",
               "Fetch each side with `parts.get(true)` and `parts.get(false)`.",
               "Printing the whole map would work here too - but explicit gets say what "
               "you mean."]),

        _p27s("j27-pb-tomap", "Word to length", "Hard",
              "Build a map from each distinct word to its length. The input repeats "
              "words, so supply a merge function keeping the first, and a `TreeMap` "
              "factory. Print the map and its size.",
              _RD_W27P
              + "        Map<String, Integer> lengths = words.stream()\n"
                "                .collect(Collectors.toMap(w -> w, String::length, (a, b) -> a, TreeMap::new));\n"
                "        System.out.println(lengths);\n"
                "        System.out.println(lengths.size());",
              [_w27p(ws, _nl(_jm27p([(w, len(w)) for w in sorted(set(ws))]),
                             len(set(ws))))
               for ws in _DUP27P],
              ["Without a merge function this throws *IllegalStateException: Duplicate "
               "key*.",
               "`(a, b) -> a` keeps the existing value - here both are equal anyway.",
               "The fourth argument, `TreeMap::new`, is what makes the print order "
               "defined.",
               "`w -> w` is the key function; `String::length` the value function.",
               "The map has one entry per distinct word, so its size is below the "
               "list's."]),
    ])


# --- Family C - reduce -------------------------------------------------------

_P27_C = _jfam(
    "p27-reduce", "`reduce` - folding to one value",
    "An identity, an operator, and one answer at the end.",
    """
```java
nums.stream().reduce(0, (a, b) -> a + b);      // sum
nums.stream().reduce(1, (a, b) -> a * b);      // product
words.stream().reduce("", (a, b) -> a + b);    // concatenation
```

Two arguments: the **identity** (the starting value, and the answer for an empty
stream) and a **binary operator** (two in, one of the same type out).

**The identity must be neutral.** `0` for `+`, `1` for `*`, `""` for
concatenation. A non-neutral one gives a wrong answer and never complains.

The fold does not have to *combine* - it can **choose**, returning one of its two
arguments, which is how you pick a maximum without `max()` (whose Optional is
module 28).
""",
    [
        _p27s("j27-pc-sum", "Folding to a total", "Intro",
              "Add up the numbers with `reduce`, then print the total and the count.",
              _RD_N27P
              + "        int total = nums.stream().reduce(0, (a, b) -> a + b);\n"
                "        System.out.println(total);\n"
                "        System.out.println(nums.size());",
              [_n27p(xs, _nl(sum(xs), len(xs))) for xs in _NS27P],
              ["The neutral value for addition is `0`.",
               "`nums.stream().reduce(0, (a, b) -> a + b)`",
               "The result is an `Integer`, unboxed into the `int`.",
               "On an empty stream this would return the identity."]),

        _p27s("j27-pc-product", "A different identity", "Easy",
              "Multiply the numbers together with `reduce`, then print the product and "
              "the count.",
              _RD_N27P
              + "        int product = nums.stream().reduce(1, (a, b) -> a * b);\n"
                "        System.out.println(product);\n"
                "        System.out.println(nums.size());",
              [_n27p(xs, _nl(_prod27p(xs), len(xs))) for xs in _NS27P],
              ["The neutral value for multiplication is `1`, never `0`.",
               "Starting from `0` would return `0` every time, silently.",
               "`nums.stream().reduce(1, (a, b) -> a * b)`",
               "One list has an odd count of negatives, so its product is negative."]),

        _p27s("j27-pc-concat", "Folding strings", "Easy",
              "Glue all the words together with `reduce`, no separator, then print the "
              "result and its length.",
              _RD_W27P
              + "        String joined = words.stream().reduce(\"\", (a, b) -> a + b);\n"
                "        System.out.println(joined);\n"
                "        System.out.println(joined.length());",
              [_w27p(ws, _nl("".join(ws), sum(len(w) for w in ws))) for ws in _WS27P],
              ["The neutral value for concatenation is `\"\"`.",
               "`words.stream().reduce(\"\", (a, b) -> a + b)`",
               "`Collectors.joining()` does this better - it uses a StringBuilder "
               "inside.",
               "This fold allocates a new String at every step: module 8's O(n^2) trap."]),

        _p27s("j27-pc-longest", "Folding to a choice", "Medium",
              "Use `reduce` to find the longest word, keeping the earlier one on a tie, "
              "then print it and its length.",
              _RD_W27P
              + "        String longest = words.stream()\n"
                "                .reduce(\"\", (a, b) -> b.length() > a.length() ? b : a);\n"
                "        System.out.println(longest);\n"
                "        System.out.println(longest.length());",
              [_w27p(ws, _nl(max(ws, key=len), len(max(ws, key=len))))
               for ws in _WS27P],
              ["The identity `\"\"` has length zero, so any word beats it.",
               "The operator returns one of its arguments rather than combining them.",
               "`(a, b) -> b.length() > a.length() ? b : a`",
               "STRICTLY greater keeps the earlier word when two tie.",
               "`max(Comparator)` says this more directly but returns an Optional - "
               "module 28."]),

        _p27s("j27-pc-largest", "The maximum, by folding", "Medium",
              "Find the largest number with `reduce`, using the smallest possible "
              "identity, then print it and the count.",
              _RD_N27P
              + "        int largest = nums.stream().reduce(Integer.MIN_VALUE, (a, b) -> b > a ? b : a);\n"
                "        System.out.println(largest);\n"
                "        System.out.println(nums.size());",
              [_n27p(xs, _nl(max(xs), len(xs))) for xs in _NS27P],
              ["The identity has to be neutral for 'maximum', which means smaller than "
               "anything possible.",
               "`Integer.MIN_VALUE` is that value.",
               "Starting from `0` would be wrong for the all-negative list - a silent "
               "bug.",
               "`(a, b) -> b > a ? b : a` chooses rather than combines.",
               "`IntStream.max()` exists but returns an `OptionalInt`."]),
    ])


# --- Family D - primitive streams --------------------------------------------

_P27_D = _jfam(
    "p27-primitive", "Primitive streams",
    "`mapToInt` to stop boxing - and to get the numeric operations.",
    """
`Stream<Integer>` holds boxed objects and has no `sum()`, because `Stream<T>`
cannot know how to add an arbitrary `T`. **`mapToInt`** produces an `IntStream`,
which holds primitives and does:

```java
words.stream().mapToInt(String::length).sum();          // int
nums.stream().mapToInt(Integer::intValue).summaryStatistics();
```

**`summaryStatistics()`** returns count, sum, min, max and average in one pass,
and every getter returns a plain value. That matters here: `average()`, `max()`
and `min()` called directly on an `IntStream` return Optionals, because an empty
stream has none of them - module 28.

**`boxed()`** turns an `IntStream` back into a `Stream<Integer>`, which is what
you need before you can `collect` it into a `List`.
""",
    [
        _p27s("j27-pd-sum", "Total characters", "Intro",
              "Add up the lengths of all the words, then print the total and the count.",
              _RD_W27P
              + "        int total = words.stream()\n"
                "                .mapToInt(String::length)\n"
                "                .sum();\n"
                "        System.out.println(total);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(sum(len(w) for w in ws), len(ws))) for ws in _WS27P],
              ["`map(String::length)` gives a `Stream<Integer>`, which has no `sum()`.",
               "`mapToInt` gives an `IntStream`, which does.",
               "`sum()` returns a plain `int`.",
               "Two printed lines."]),

        _p27s("j27-pd-sumnums", "Summing the numbers", "Intro",
              "Add up the numbers via an `IntStream`, then print the total and the "
              "count.",
              _RD_N27P
              + "        int total = nums.stream()\n"
                "                .mapToInt(Integer::intValue)\n"
                "                .sum();\n"
                "        System.out.println(total);\n"
                "        System.out.println(nums.size());",
              [_n27p(xs, _nl(sum(xs), len(xs))) for xs in _NS27P],
              ["The list is a `List<Integer>`, so each element must be unboxed.",
               "`Integer::intValue` is the unbound method reference that does it.",
               "`.mapToInt(Integer::intValue).sum()`",
               "This says what it means more clearly than `reduce(0, Integer::sum)`."]),

        _p27s("j27-pd-stats", "Five answers in one pass", "Medium",
              "Print the count, sum, minimum, maximum and average of the numbers, using "
              "a single summary object.",
              _RD_N27P
              + "        IntSummaryStatistics stats = nums.stream().mapToInt(Integer::intValue).summaryStatistics();\n"
                "        System.out.println(stats.getCount());\n"
                "        System.out.println(stats.getSum());\n"
                "        System.out.println(stats.getMin());\n"
                "        System.out.println(stats.getMax());\n"
                "        System.out.println(stats.getAverage());",
              [_n27p(xs, _nl(len(xs), sum(xs), min(xs), max(xs),
                             str(float(sum(xs) / len(xs)))))
               for xs in _NS27P],
              ["`summaryStatistics()` is a terminal returning an "
               "`IntSummaryStatistics`.",
               "Every getter returns a plain value - `getAverage()` is a `double`.",
               "`.average()` on its own would return an `OptionalDouble`.",
               "The averages here all divide evenly, so each prints with one decimal.",
               "Five printed lines."]),

        _p27s("j27-pd-boxed", "Back to objects", "Medium",
              "Collect the word lengths into a `List<Integer>`, then print it and its "
              "size. An `IntStream` cannot be collected directly.",
              _RD_W27P
              + "        List<Integer> lengths = words.stream()\n"
                "                .mapToInt(String::length)\n"
                "                .boxed()\n"
                "                .collect(Collectors.toList());\n"
                "        System.out.println(lengths);\n"
                "        System.out.println(lengths.size());",
              [_w27p(ws, _nl(_jl27p([len(w) for w in ws]), len(ws))) for ws in _WS27P],
              ["A `List` holds objects; an `IntStream` holds primitives.",
               "`.boxed()` returns a `Stream<Integer>`.",
               "Only then is `.collect(Collectors.toList())` available.",
               "`map(String::length)` would have skipped the round trip - this route "
               "shows why `boxed` exists."]),

        _p27m("j27-pd-method", "totalLength", "Medium",
              "Write `totalLength`, returning the total number of characters in a list "
              "of words, using a primitive stream. `main` calls it twice.",
              """
    static int totalLength(List<String> items) {
        return items.stream().mapToInt(String::length).sum();
    }
""",
              _RD_W27P
              + "        System.out.println(totalLength(words));\n"
                "        System.out.println(totalLength(new ArrayList<>()));\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(sum(len(w) for w in ws), 0, len(ws))) for ws in _WS27P],
              ["One expression: stream, `mapToInt`, `sum`.",
               "`return items.stream().mapToInt(String::length).sum();`",
               "`sum()` on an EMPTY stream is `0`, with no Optional in sight - which is "
               "why the second call is safe.",
               "That is the difference from `max()`, which would have nothing to "
               "return.",
               "Three printed lines."]),
    ])


# --- Family E - whole reports ------------------------------------------------

_P27_E = _jfam(
    "p27-reports", "Whole reports",
    "Several collectors in one program, the way real code uses them.",
    """
Most real uses are two or three of these together: filter, then group, then
count; or map, then collect, then join. The habits that carry across all of
them:

* **filter before you group** - the grouping then buckets fewer elements;
* **pass `TreeMap::new`** whenever the map will be printed or compared;
* **one terminal per stream** - every question needs a fresh one;
* **prefer the named operation**: `joining` over a concatenating `reduce`,
  `mapToInt(...).sum()` over `reduce(0, ...)`.
""",
    [
        _p27s("j27-pe-filtergroup", "Filter, then group", "Medium",
              "Group only the words longer than one character by their length, keys "
              "ascending, then print the map and the original list size.",
              _RD_W27P
              + "        Map<Integer, List<String>> byLength = words.stream()\n"
                "                .filter(w -> w.length() > 1)\n"
                "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList()));\n"
                "        System.out.println(byLength);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(_grouplist27p([w for w in ws if len(w) > 1], len),
                             len(ws)))
               for ws in _WS27P],
              ["Filter first so the grouping handles fewer elements.",
               "The filter goes before `.collect(...)`, as an ordinary intermediate.",
               "One list loses its single-character word entirely, so that key is "
               "absent.",
               "The final size is the untouched original."]),

        _p27s("j27-pe-mapjoin", "Map, then join", "Easy",
              "Print the lengths of the words as a comma-separated line, then the total "
              "of those lengths.",
              _RD_W27P
              + "        System.out.println(words.stream()\n"
                "                .map(String::length)\n"
                "                .map(String::valueOf)\n"
                "                .collect(Collectors.joining(\", \")));\n"
                "        System.out.println(words.stream().mapToInt(String::length).sum());",
              [_w27p(ws, _nl(", ".join(str(len(w)) for w in ws),
                             sum(len(w) for w in ws)))
               for ws in _WS27P],
              ["`joining` works on Strings only, so the numbers have to become text "
               "first.",
               "`String::valueOf` is a static method reference that does it.",
               "Two maps in a row is perfectly ordinary - each returns a new stream.",
               "The second line uses `mapToInt`, because the total is a number."]),

        _p27s("j27-pe-distinctgroup", "Distinct, then count by length", "Medium",
              "The input repeats words. Remove duplicates first, then count how many "
              "distinct words there are of each length, keys ascending. Print the map "
              "then the original size.",
              _RD_W27P
              + "        Map<Integer, Long> howMany = words.stream()\n"
                "                .distinct()\n"
                "                .collect(Collectors.groupingBy(String::length, TreeMap::new, Collectors.counting()));\n"
                "        System.out.println(howMany);\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(_groupcount27p(list(dict.fromkeys(ws)), len), len(ws)))
               for ws in _DUP27P],
              ["`.distinct()` is an ordinary intermediate - it goes before the "
               "collect.",
               "Then group by length with `counting()` downstream.",
               "The counts are of DISTINCT words, so they are lower than a plain "
               "grouping's.",
               "The final line still reports the full original size."]),

        _p27s("j27-pe-partitioncount", "Both sides, counted", "Medium",
              "Partition the words by whether they are longer than two characters, then "
              "print how many are on each side and the total.",
              _RD_W27P
              + "        Map<Boolean, List<String>> parts = words.stream()\n"
                "                .collect(Collectors.partitioningBy(w -> w.length() > 2));\n"
                "        System.out.println(parts.get(true).size());\n"
                "        System.out.println(parts.get(false).size());\n"
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(sum(1 for w in ws if len(w) > 2),
                             sum(1 for w in ws if len(w) <= 2),
                             len(ws)))
               for ws in _WS27P],
              ["Both keys always exist, so neither `get` can return null.",
               "`parts.get(true).size()` for the matching side.",
               "The two counts always add up to the list size.",
               "`partitioningBy(p, Collectors.counting())` would count them directly - "
               "either is fine."]),

        _p27s("j27-pe-ledger", "The full ledger", "Hard",
              "Print six lines: the words longer than two characters as a list; all of "
              "them in capitals joined by `, `; a frequency table of lengths with keys "
              "ascending; every word glued together with `reduce`; the total character "
              "count; and the list size.",
              _RD_W27P
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
                "        System.out.println(words.size());",
              [_w27p(ws, _nl(_jl27p([w for w in ws if len(w) > 2]),
                             ", ".join(w.upper() for w in ws),
                             _groupcount27p(ws, len),
                             "".join(ws),
                             sum(len(w) for w in ws),
                             len(ws)))
               for ws in _DUP27P],
              ["Six lines, six fresh streams.",
               "`TreeMap::new` on the grouping is what makes line three printable at "
               "all.",
               "Line four uses `reduce` where line two used `joining` - the same job, "
               "two ways.",
               "Line five is `mapToInt(String::length).sum()`, not a `reduce`.",
               "The input repeats words, so the frequency counts exceed the number of "
               "distinct words.",
               "Nothing in any pipeline changes the source list."]),
    ])


_PRACTICE[27] = [_P27_A, _P27_B, _P27_C, _P27_D, _P27_E]
