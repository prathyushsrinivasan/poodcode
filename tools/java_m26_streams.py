# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 26 - Streams: the pipeline.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# `.stream()` and `Stream<` become legal here and nowhere earlier. Module 25
# hand-wrote `countMatching`, `mapAll` and `each` - filter, map and forEach with
# the loop spelled out - so this module has something concrete to replace.
#
# DELIBERATELY NOT HERE: `collect`, `Collectors`, `reduce` and the primitive
# streams are module 27; `Optional` (and therefore `findFirst`, `min`, `max`) is
# module 28. The scope linter enforces all of it. So every pipeline in this
# module ends in `forEach`, `count` or one of the three matchers - which is
# enough to make the SHAPE of a pipeline the only new idea on the page.
#
# JUDGING NOTE: sequential streams process one element through the whole
# pipeline before starting the next, and preserve encounter order, so the
# interleaved output in the laziness lesson is fully deterministic. Nothing here
# uses a parallel stream, where none of that would hold.
# ---------------------------------------------------------------------------

_M26 = []

_IMPORTS26 = ("import java.util.*;\n"
              "import java.util.function.*;\n"
              "import java.util.stream.*;\n")


def _j26s(body):
    """Scanner-opening main, no helpers."""
    return _jscan(body, imports=_IMPORTS26)


def _j26(helpers, body):
    """Static helper methods above a Scanner-opening main."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS26,
    )


_RD_W26 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N26 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_W26 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
        ["alpha", "beta", "gamma", "d"])

_N26 = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

# Lists that repeat, so `distinct` has something to remove.
_DUP26 = (["ada", "bo", "ada", "cy"], ["solo", "solo"], ["x", "yy", "x", "x"],
          ["pear", "fig", "pear"], ["a", "b", "a", "b", "c"])


def _w26(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n26(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jl26(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _dedup26(ws):
    """What `distinct()` leaves: first occurrences, in encounter order."""
    return list(dict.fromkeys(ws))


# --- 26.1 What a stream is ---------------------------------------------------

_M26.append(_jlesson(
    "m26-pipeline", "Source, pipeline, terminal",
    "A stream is not a collection - it is a plan that runs when you ask for an answer.",
    """
Module 25 ended with three hand-written methods: `countMatching`, `mapAll` and
`each`. Here is all three, chained, with no loop at all:

```java
words.stream()                       // SOURCE
     .filter(w -> w.length() > 3)    // intermediate
     .map(String::toUpperCase)       // intermediate
     .forEach(System.out::println);  // TERMINAL
```

Every pipeline has exactly that shape:

* a **source** - `collection.stream()`, and the collection is never modified;
* any number of **intermediate operations** - each returns a *new stream*, so
  they chain;
* exactly one **terminal operation** - which produces a result and runs the
  whole thing.

**A stream is not a collection.** It stores nothing. It has no `size()`, no
`get(i)`, and you cannot look at it twice. It is a description of work.

**Nothing happens until the terminal.** Intermediate operations are **lazy** -
they build the plan and return immediately. This prints `built` *first*:

```java
Stream<String> pipeline = words.stream().filter(w -> {
    System.out.println("testing " + w);
    return w.length() > 3;
});
System.out.println("built");        // prints before any "testing"
pipeline.forEach(System.out::println);
```

And when it does run, it runs **element at a time, not stage at a time** -
each word goes through the whole pipeline before the next one starts. So the
"testing" lines interleave with the results rather than all coming first.

**A stream is single-use.** Once a terminal operation has run, the stream is
spent:

```java
Stream<String> s = words.stream();
s.forEach(System.out::println);
System.out.println(s.count());   // IllegalStateException: already operated upon
```

Get a fresh one from the source instead. This catches everybody once.
""",
    warmup=[
        _jq("`words.stream().filter(w -> w.length() > 3);` with no terminal…",
            ["does nothing at all - intermediates are lazy",
             "filters the list", "prints the matches", "throws"],
            0,
            "It builds a plan and returns. Only a terminal runs it."),
        _jq("Calling a second terminal on the same stream…",
            ["throws IllegalStateException", "works", "returns null",
             "restarts the pipeline"],
            0,
            "Streams are single-use. Ask the source for a new one."),
    ],
    exercises=[
        _je("j26-pipe-count", "The shortest pipeline",
            "Count how many words are longer than three characters with a stream rather "
            "than module 25's hand-written loop, then show the source list is unchanged. "
            "Replace `____` with the pipeline.",
            _j26s(_RD_W26
                  + "        System.out.println(words.stream().filter(w -> w.length() > 3).count());\n"
                    "        System.out.println(words.size());"),
            "        System.out.println(words.stream().filter(w -> w.length() > 3).count());",
            [_w26(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws))) for ws in _W26],
            hints=["Source, one intermediate, one terminal: `words.stream()`, "
                   "`.filter(...)`, `.count()`.",
                   "The filter takes a `Predicate<String>` - the same lambda module 25 "
                   "passed to `countMatching`.",
                   "`words.stream().filter(w -> w.length() > 3).count()`",
                   "`count()` returns a `long`, which prints exactly like an int here.",
                   "The second line proves the source list was never touched."],
            difficulty="Easy"),

        _je("j26-pipe-lazy", "Nothing runs until you ask",
            "Build a filtering pipeline whose predicate announces every element it "
            "tests, print `built`, and only then run it. Replace `____` with the pipeline "
            "declaration - and watch where `built` lands in the output.",
            _j26s(_RD_W26
                  + "        Stream<String> pipeline = words.stream().filter(w -> {\n"
                    "            System.out.println(\"testing \" + w);\n"
                    "            return w.length() > 3;\n"
                    "        });\n"
                    "        System.out.println(\"built\");\n"
                    "        pipeline.forEach(System.out::println);"),
            "        Stream<String> pipeline = words.stream().filter(w -> {\n"
            "            System.out.println(\"testing \" + w);\n"
            "            return w.length() > 3;\n"
            "        });",
            [_w26(ws, _nl(*(["built"]
                            + [line for w in ws
                               for line in (["testing " + w] + ([w] if len(w) > 3 else []))])))
             for ws in _W26],
            hints=["The variable's type is `Stream<String>` - an intermediate operation "
                   "returns a new stream, not a list.",
                   "The lambda needs a braced body, because it both prints and returns.",
                   "`built` prints BEFORE any `testing` line: the filter has not run "
                   "yet.",
                   "When it does run, each word goes through the whole pipeline before "
                   "the next starts - so a match prints immediately after its own "
                   "`testing` line.",
                   "Words that fail the test print a `testing` line and nothing else."],
            difficulty="Hard"),

        _jfix("j26-pipe-reuse", "The stream you cannot use twice",
              "This runs two terminal operations on one stream, and the second throws "
              "`IllegalStateException: stream has already been operated upon or closed`. "
              "Take a fresh stream from the source for the second question.",
              _j26s(_RD_W26
                    + "        Stream<String> pipeline = words.stream();\n"
                      "        pipeline.forEach(System.out::println);\n"
                      "        System.out.println(pipeline.count());"),
              _j26s(_RD_W26
                    + "        words.stream().forEach(System.out::println);\n"
                      "        System.out.println(words.stream().count());"),
              [_w26(ws, _nl(*(list(ws) + [len(ws)]))) for ws in _W26],
              hints=["A stream is single-use: one terminal operation and it is spent.",
                     "The list, on the other hand, can hand out as many streams as you "
                     "like.",
                     "Call `words.stream()` twice - once per question.",
                     "There is no way to 'reset' a stream, and no reason to want one; "
                     "the source is right there.",
                     "The output is every word, then the count."],
              difficulty="Medium"),

        _jch("j26-pipe-source", "The source is never touched", "Easy",
             "Print every word longer than three characters through a stream, then print "
             "the original list and its size - showing a pipeline reads its source and "
             "changes nothing.",
             _j26s(_RD_W26
                   + "        words.stream().filter(w -> w.length() > 3).forEach(System.out::println);\n"
                     "        System.out.println(words);\n"
                     "        System.out.println(words.size());"),
             "        words.stream().filter(w -> w.length() > 3).forEach(System.out::println);\n"
             "        System.out.println(words);\n"
             "        System.out.println(words.size());",
             [_w26(ws, _nl(*([w for w in ws if len(w) > 3]
                             + [_jl26(ws), len(ws)])))
              for ws in _W26],
             hints=["`forEach` takes a `Consumer`, so `System.out::println` fits it.",
                    "Filtering produces a new stream; it never removes anything from the "
                    "list.",
                    "For a list where nothing matches, the first section of output is "
                    "simply empty.",
                    "The printed list is in the original input order, unchanged.",
                    "Compare with `removeIf`, which really would modify the list."]),
    ],
    quiz=[
        _jq("How many terminal operations may a pipeline have?",
            ["Exactly one", "As many as you like", "At most two", "None"],
            0,
            "It is what produces the result and runs the plan."),
        _jq("An intermediate operation returns…",
            ["a new Stream", "a List", "the same Stream", "void"],
            0,
            "Which is exactly why they chain."),
    ],
))


# --- 26.2 filter and map -----------------------------------------------------

_M26.append(_jlesson(
    "m26-filtermap", "`filter` and `map`",
    "Keep some of them; turn each into something else.",
    """
Two intermediate operations do most of the work, and you wrote both by hand in
module 25.

**`filter(Predicate<T>)`** keeps the elements that answer `true`. The stream
gets shorter; the element type does not change:

```java
words.stream()
     .filter(w -> w.length() > 3)
     .forEach(System.out::println);
```

**`map(Function<T, R>)`** replaces each element with the result of applying a
function. The length stays the same; the **element type can change**:

```java
words.stream()
     .map(String::toUpperCase)     // Stream<String> -> Stream<String>
     .forEach(System.out::println);

words.stream()
     .map(String::length)          // Stream<String> -> Stream<Integer>
     .forEach(System.out::println);
```

That second one is the important half: `map` is where a pipeline changes shape.
`Stream<String>` becomes `Stream<Integer>` and everything downstream now works
on numbers.

**Order matters, and not only for the answer.** These give the same result:

```java
.filter(w -> w.length() > 3).map(String::toUpperCase)
.map(String::toUpperCase).filter(w -> w.length() > 3)
```

but the first calls `toUpperCase` only on the words that survived, and the
second calls it on all of them. **Filter early** - it is the one pipeline habit
worth having from day one.

A useful way to hold it: `filter` answers *which*, `map` answers *what*.
""",
    warmup=[
        _jq("`map(String::length)` turns a `Stream<String>` into…",
            ["Stream<Integer>", "Stream<String>", "List<Integer>", "int"],
            0,
            "`map` is where the element type changes."),
        _jq("Why filter before mapping?",
            ["The map then runs only on the elements that survived",
             "It is required", "The result differs", "For laziness"],
            0,
            "Same answer either way; less work one way."),
    ],
    exercises=[
        _je("j26-fm-filter", "Keeping some of them",
            "Print only the words that start with `a`. Replace `____` with the "
            "intermediate operation that keeps them.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .filter(w -> w.startsWith(\"a\"))\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "             .filter(w -> w.startsWith(\"a\"))",
            [_w26(ws, _nl(*([w for w in ws if w.startswith("a")] + [len(ws)])))
             for ws in _W26],
            hints=["`filter` takes a `Predicate<String>` - a question about one word.",
                   "`startsWith` is module 7's, unchanged.",
                   "`.filter(w -> w.startsWith(\"a\"))`",
                   "Lists where nothing starts with `a` print only the size."],
            difficulty="Easy"),

        _je("j26-fm-map", "Turning each into something else",
            "Print every word in capitals, using a method reference for the "
            "transformation. Replace `____` with the intermediate operation.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .map(String::toUpperCase)\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "             .map(String::toUpperCase)",
            [_w26(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _W26],
            hints=["`map` takes a `Function<String, String>` here.",
                   "`String::toUpperCase` is module 25's unbound method reference.",
                   "`.map(String::toUpperCase)`",
                   "The stream is the same length afterwards - `map` replaces, it never "
                   "removes."],
            difficulty="Easy"),

        _je("j26-fm-type", "Changing the element type",
            "Print the length of every word. This is where the pipeline stops being a "
            "stream of Strings. Replace `____` with the operation that changes its type.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .map(String::length)\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "             .map(String::length)",
            [_w26(ws, _nl(*([len(w) for w in ws] + [len(ws)]))) for ws in _W26],
            hints=["After this operation the pipeline is a `Stream<Integer>`.",
                   "`String::length` extracts the key; the boxing to `Integer` is "
                   "automatic.",
                   "`.map(String::length)`",
                   "`forEach(System.out::println)` still fits, because `println` is "
                   "overloaded for every type."],
            difficulty="Medium"),

        _jch("j26-fm-chain", "Filter first, then map", "Medium",
             "Print the long words - those over three characters - in capitals. Chain "
             "the two operations in the order that does the least work, then print the "
             "original size.",
             _j26s(_RD_W26
                   + "        words.stream()\n"
                     "             .filter(w -> w.length() > 3)\n"
                     "             .map(String::toUpperCase)\n"
                     "             .forEach(System.out::println);\n"
                     "        System.out.println(words.size());"),
             "        words.stream()\n"
             "             .filter(w -> w.length() > 3)\n"
             "             .map(String::toUpperCase)\n"
             "             .forEach(System.out::println);\n"
             "        System.out.println(words.size());",
             [_w26(ws, _nl(*([w.upper() for w in ws if len(w) > 3] + [len(ws)])))
              for ws in _W26],
             hints=["Filter before mapping, so `toUpperCase` runs only on survivors.",
                    "Each operation on its own line reads better once there are three of "
                    "them.",
                    "The terminal is `.forEach(System.out::println);` - note the "
                    "semicolon ends the whole chain.",
                    "Reversing the two would print the same thing, just after more "
                    "work.",
                    "The final line is the untouched source size."]),
    ],
    quiz=[
        _jq("`filter` can change…",
            ["how many elements there are, but not their type",
             "the type, but not the count", "both", "neither"],
            0,
            "`map` is the one that changes type."),
        _jq("`words.stream().map(String::length)` has type…",
            ["Stream<Integer>", "Stream<String>", "List<Integer>", "IntStream"],
            0,
            "Boxed, because `map` produces a Stream of a reference type."),
    ],
))


# --- 26.3 Shaping the stream -------------------------------------------------

_M26.append(_jlesson(
    "m26-shaping", "`sorted`, `distinct`, `limit`, `skip`",
    "Four more intermediates, and the two that have to see everything.",
    """
**`sorted()`** puts the stream in natural order - the `Comparable` ordering from
module 20. **`sorted(Comparator)`** uses one you supply, and pairs perfectly
with `Comparator.comparing` and a method reference:

```java
words.stream().sorted().forEach(System.out::println);
words.stream().sorted(Comparator.comparing(String::length)).forEach(System.out::println);
```

**`distinct()`** removes duplicates, using `equals` and `hashCode` - which is
module 18's contract, and the reason a class with a broken `equals` will produce
duplicates here that you swear are identical. It keeps the **first** occurrence,
so encounter order survives.

**`limit(n)`** keeps the first `n` and **`skip(n)`** drops the first `n`. In that
order they are a page of results:

```java
words.stream().skip(2).limit(3).forEach(System.out::println);   // items 3, 4, 5
```

**Two of these are stateful, and it matters.** `filter` and `map` can decide
about an element the moment they see it. `sorted` and `distinct` cannot -
`sorted` has to consume the *entire* stream before it can emit anything, and
`distinct` has to remember everything it has already seen. So the neat
"element at a time" story from lesson 26.1 holds right up until a `sorted`
appears, which is one more reason to filter before you sort rather than after.

`limit` is the opposite: it **short-circuits**, stopping the whole pipeline as
soon as it has enough - which is why it can even work on an infinite stream.
""",
    warmup=[
        _jq("`distinct()` decides two elements are the same using…",
            ["equals and hashCode", "==", "compareTo", "toString"],
            0,
            "Module 18's contract, showing up again."),
        _jq("Which operation must consume the whole stream before emitting anything?",
            ["sorted", "filter", "map", "limit"],
            0,
            "It cannot know the first element until it has seen the last."),
    ],
    exercises=[
        _je("j26-sh-sorted", "Natural order",
            "Print the words in alphabetical order. Replace `____` with the operation "
            "that sorts them.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .sorted()\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words);"),
            "             .sorted()",
            [_w26(ws, _nl(*(sorted(ws) + [_jl26(ws)]))) for ws in _W26],
            hints=["With no argument it uses the natural ordering - `String`'s own "
                   "`compareTo`, from module 20.",
                   "`.sorted()`",
                   "The source list is printed afterwards and is still in input order: "
                   "sorting the stream sorted nothing else.",
                   "Compare with `words.sort(...)`, which really does reorder the list."],
            difficulty="Easy"),

        _je("j26-sh-comparator", "Sorted by a key",
            "Print the words shortest first, using `Comparator.comparing` and a method "
            "reference. Replace `____` with that operation.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .sorted(Comparator.comparing(String::length))\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "             .sorted(Comparator.comparing(String::length))",
            [_w26(ws, _nl(*(sorted(ws, key=len) + [len(ws)]))) for ws in _W26],
            hints=["`sorted` is overloaded: no argument for natural order, or one "
                   "`Comparator`.",
                   "Module 25's `Comparator.comparing(String::length)` drops straight "
                   "in.",
                   "`.sorted(Comparator.comparing(String::length))`",
                   "The sort is stable, so equal-length words keep their input order."],
            difficulty="Medium"),

        _je("j26-sh-distinct", "Removing repeats",
            "The input repeats some words. Print each one once, in the order it first "
            "appeared. Replace `____` with the operation that does it.",
            _j26s(_RD_W26
                  + "        words.stream()\n"
                    "             .distinct()\n"
                    "             .forEach(System.out::println);\n"
                    "        System.out.println(words.size());"),
            "             .distinct()",
            [_w26(ws, _nl(*(_dedup26(ws) + [len(ws)]))) for ws in _DUP26],
            hints=["`distinct()` takes no arguments and uses `equals`/`hashCode`.",
                   "`.distinct()`",
                   "It keeps the FIRST occurrence, so the order is the order things "
                   "first showed up.",
                   "The final size is the ORIGINAL list's, which still holds the "
                   "duplicates."],
            difficulty="Easy"),

        _jch("j26-sh-page", "One page of results", "Medium",
             "Print a page of the sorted words: skip the first one, then take at most "
             "two. Sort alphabetically first, and print the source size at the end.",
             _j26s(_RD_W26
                   + "        words.stream()\n"
                     "             .sorted()\n"
                     "             .skip(1)\n"
                     "             .limit(2)\n"
                     "             .forEach(System.out::println);\n"
                     "        System.out.println(words.size());"),
             "        words.stream()\n"
             "             .sorted()\n"
             "             .skip(1)\n"
             "             .limit(2)\n"
             "             .forEach(System.out::println);\n"
             "        System.out.println(words.size());",
             [_w26(ws, _nl(*(sorted(ws)[1:3] + [len(ws)]))) for ws in _W26],
             hints=["Order the operations the way you would say them: sort, then skip, "
                    "then take.",
                    "`.skip(1)` drops the first; `.limit(2)` keeps at most two of what "
                    "is left.",
                    "`limit` takes a `long`, but writing `2` is fine.",
                    "A one-word list prints nothing at all from the pipeline - skipping "
                    "one leaves none.",
                    "Putting `limit` before `skip` would be a different question "
                    "entirely."]),
    ],
    quiz=[
        _jq("`sorted()` with no argument uses…",
            ["the natural ordering (Comparable)", "insertion order",
             "hashCode order", "reverse order"],
            0,
            "Module 20's `compareTo`."),
        _jq("`limit(3)` on a long pipeline…",
            ["short-circuits - the pipeline stops once it has three",
             "runs everything then trims", "sorts first", "throws if there are fewer"],
            0,
            "Which is how it can work on an infinite stream."),
    ],
))


# --- 26.4 Terminal operations ------------------------------------------------

_M26.append(_jlesson(
    "m26-terminal", "The terminal operation",
    "The one that produces an answer - and runs everything.",
    """
Exactly one terminal ends every pipeline. This module uses the ones that need
nothing you have not met:

| Terminal | Gives you | Note |
|---|---|---|
| `forEach(Consumer)` | nothing | runs an action per element |
| `count()` | `long` | how many survived |
| `anyMatch(Predicate)` | `boolean` | **short-circuits** on the first `true` |
| `allMatch(Predicate)` | `boolean` | short-circuits on the first `false` |
| `noneMatch(Predicate)` | `boolean` | short-circuits on the first `true` |

```java
words.stream().anyMatch(w -> w.length() > 3);    // is there one?
words.stream().allMatch(w -> w.length() > 1);    // are they all?
words.stream().noneMatch(String::isEmpty);       // is there none?
```

**The three matchers short-circuit**, which is worth knowing for more than
speed: `anyMatch` stops at the first match, so a pipeline with an expensive
`map` in front of it may only run that map once.

**A pipeline with no terminal produces nothing** - not an empty result, but no
work at all. This is the single most common streams mistake, and it fails
silently:

```java
words.stream().map(String::toUpperCase);   // does nothing whatsoever
```

There is no warning, no output, no error. If a stream "did not work", check that
it ends in a terminal before you check anything else.

**The two edge cases worth memorising**, because interviews ask: on an **empty**
stream, `allMatch` returns `true` and `noneMatch` returns `true`, while
`anyMatch` returns `false`. "All of nothing" is vacuously true - the same
convention as mathematics, and occasionally a real bug.

The terminals that give you a *collection* back - `collect` and `toList` - are
module 27, along with `reduce`. The ones that may find nothing and so return an
`Optional` - `findFirst`, `min`, `max` - are module 28.
""",
    warmup=[
        _jq("`words.stream().map(String::toUpperCase);` prints…",
            ["nothing - there is no terminal operation",
             "every word in capitals", "the first word", "an error"],
            0,
            "It builds a plan nobody ran. Silent, which is what makes it a trap."),
        _jq("`allMatch` on an EMPTY stream returns…",
            ["true", "false", "null", "it throws"],
            0,
            "Vacuously true, the same convention as mathematics."),
    ],
    exercises=[
        _je("j26-tm-matchers", "Three questions, three booleans",
            "Answer three questions about the words: is any longer than three "
            "characters, are they all non-empty, and is none of them a single "
            "character. Replace `____` with the three lines.",
            _j26s(_RD_W26
                  + "        System.out.println(words.stream().anyMatch(w -> w.length() > 3));\n"
                    "        System.out.println(words.stream().allMatch(w -> w.length() > 0));\n"
                    "        System.out.println(words.stream().noneMatch(w -> w.length() == 1));\n"
                    "        System.out.println(words.size());"),
            "        System.out.println(words.stream().anyMatch(w -> w.length() > 3));\n"
            "        System.out.println(words.stream().allMatch(w -> w.length() > 0));\n"
            "        System.out.println(words.stream().noneMatch(w -> w.length() == 1));",
            [_w26(ws, _nl(_jbool(any(len(w) > 3 for w in ws)),
                          _jbool(all(len(w) > 0 for w in ws)),
                          _jbool(not any(len(w) == 1 for w in ws)),
                          len(ws)))
             for ws in _W26],
            hints=["All three take a `Predicate<String>` and return a `boolean`.",
                   "Each needs its own fresh stream - one terminal per stream.",
                   "`anyMatch`, `allMatch`, `noneMatch`, in that order.",
                   "All three short-circuit, so none of them necessarily sees every "
                   "word.",
                   "The last list has a one-character word in it, which changes the "
                   "third answer."],
            difficulty="Medium"),

        _je("j26-tm-count", "Counting what survived",
            "Print how many words are longer than three characters, and how many are "
            "left after removing duplicates. Replace `____` with the second of those "
            "pipelines.",
            _j26s(_RD_W26
                  + "        System.out.println(words.stream().filter(w -> w.length() > 3).count());\n"
                    "        System.out.println(words.stream().distinct().count());\n"
                    "        System.out.println(words.size());"),
            "        System.out.println(words.stream().distinct().count());",
            [_w26(ws, _nl(sum(1 for w in ws if len(w) > 3),
                          len(_dedup26(ws)), len(ws)))
             for ws in _DUP26],
            hints=["`count()` is a terminal returning a `long`.",
                   "`distinct()` first, then count what is left.",
                   "`words.stream().distinct().count()`",
                   "The third line is the original size, which still counts the "
                   "duplicates."],
            difficulty="Easy"),

        _jfix("j26-tm-noterminal", "The pipeline that never ran",
              "This builds a pipeline and never runs it, so it prints nothing but the "
              "size - no error, no warning. Add the terminal operation that prints each "
              "element.",
              _j26s(_RD_W26
                    + "        words.stream()\n"
                      "             .filter(w -> w.length() > 3)\n"
                      "             .map(String::toUpperCase);\n"
                      "        System.out.println(words.size());"),
              _j26s(_RD_W26
                    + "        words.stream()\n"
                      "             .filter(w -> w.length() > 3)\n"
                      "             .map(String::toUpperCase)\n"
                      "             .forEach(System.out::println);\n"
                      "        System.out.println(words.size());"),
              [_w26(ws, _nl(*([w.upper() for w in ws if len(w) > 3] + [len(ws)])))
               for ws in _W26],
              hints=["`filter` and `map` are both intermediate - they return a stream "
                     "and do no work.",
                     "Nothing in this program ever asked for a result.",
                     "`.forEach(System.out::println)` is the terminal that prints each "
                     "element.",
                     "Watch the semicolon: it moves from the end of `.map(...)` to the "
                     "end of the new last line.",
                     "This failure mode is silent, which is exactly why it is worth "
                     "meeting once deliberately."],
              difficulty="Medium"),

        _jch("j26-tm-report", "Four answers about one list", "Medium",
             "Using the numbers, print: how many are positive, whether any is negative, "
             "whether all are above minus ten, and the size of the list.",
             _j26s(_RD_N26
                   + "        System.out.println(nums.stream().filter(x -> x > 0).count());\n"
                     "        System.out.println(nums.stream().anyMatch(x -> x < 0));\n"
                     "        System.out.println(nums.stream().allMatch(x -> x > -10));\n"
                     "        System.out.println(nums.size());"),
             "        System.out.println(nums.stream().filter(x -> x > 0).count());\n"
             "        System.out.println(nums.stream().anyMatch(x -> x < 0));\n"
             "        System.out.println(nums.stream().allMatch(x -> x > -10));\n"
             "        System.out.println(nums.size());",
             [_n26(xs, _nl(sum(1 for x in xs if x > 0),
                           _jbool(any(x < 0 for x in xs)),
                           _jbool(all(x > -10 for x in xs)),
                           len(xs)))
              for xs in _N26],
             hints=["The stream is a `Stream<Integer>`, so the lambdas take an `Integer` "
                    "- comparisons unbox it automatically.",
                    "Each question needs its own `nums.stream()`.",
                    "`filter(...).count()` for the first; a matcher for each of the next "
                    "two.",
                    "One list contains exactly minus nine, which is above minus ten - "
                    "check the boundary rather than guessing.",
                    "Four printed lines."]),
    ],
    quiz=[
        _jq("Which of these is NOT a terminal operation?",
            ["map", "count", "forEach", "anyMatch"],
            0,
            "`map` returns a stream, so it is intermediate."),
        _jq("A pipeline with no terminal operation…",
            ["does nothing, silently", "throws", "warns at compile time",
             "runs anyway"],
            0,
            "The most common streams mistake, and the hardest to see."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M26_CAP_BODY = (
    _RD_W26
    + "        System.out.println(words.stream().count());\n"
      "        System.out.println(words.stream().distinct().count());\n"
      "        words.stream()\n"
      "             .filter(w -> w.length() > 2)\n"
      "             .map(String::toUpperCase)\n"
      "             .distinct()\n"
      "             .sorted()\n"
      "             .forEach(System.out::println);\n"
      "        System.out.println(words.stream().anyMatch(w -> w.length() > 3));\n"
      "        System.out.println(words);"
)


def _m26_cap_case(ws):
    shaped = sorted(_dedup26([w.upper() for w in ws if len(w) > 2]))
    return _w26(ws, _nl(*([len(ws), len(_dedup26(ws))]
                          + shaped
                          + [_jbool(any(len(w) > 3 for w in ws)), _jl26(ws)])))


_M26_CAP = _jcap(
    "The word report",
    """
One list, five questions, and no loop anywhere.

1. **How many words** there are - the shortest pipeline that exists.
2. **How many distinct words** there are.
3. **The report itself**: every word longer than two characters, in capitals,
   de-duplicated and sorted, one per line.
4. **Whether any word** is longer than three characters.
5. **The source list**, printed last to prove nothing in the pipeline touched
   it.

The third one is the exercise: four intermediates and a terminal, in an order
that matters. `filter` goes first so the later stages do less work; `map` before
`distinct` means words that differ only in case collapse together; `sorted` goes
last so it sorts the smallest stream it can - it is the stage that has to see
everything before it can emit anything.
""",
    _jch("j26-cap-report", "The word report", "Hard",
         "Write the five pipelines described in the brief, in order.",
         _j26s(_M26_CAP_BODY),
         _M26_CAP_BODY,
         [_m26_cap_case(ws) for ws in _DUP26],
         hints=["Each question needs its own stream - a stream is single-use.",
                "`words.stream().count()` and `words.stream().distinct().count()` are "
                "the first two lines.",
                "The report's order is filter, map, distinct, sorted, forEach.",
                "`filter(w -> w.length() > 2)` first, so the map runs on fewer words.",
                "`.map(String::toUpperCase)` then `.distinct()`, so the de-duplication "
                "happens on the capitalised forms.",
                "`.sorted()` last, then `.forEach(System.out::println)` to end the "
                "chain.",
                "`anyMatch(w -> w.length() > 3)` for the fourth line - it short-circuits "
                "on the first match.",
                "The final `System.out.println(words)` must show the list in its "
                "ORIGINAL order, with duplicates intact."]),
    example_io="stdin:  4\n        ada bo ada cy\n\n"
               "stdout: 4\n        3\n        ADA\n        false\n"
               "        [ada, bo, ada, cy]",
    rubric=[
        "Every question gets its own fresh stream from the source.",
        "The counts use `count()`, not `size()` on a collected result.",
        "The report filters before mapping, so the map runs only on survivors.",
        "`distinct` comes after `map`, so it de-duplicates the capitalised forms.",
        "`sorted` is the last intermediate, and `forEach` is the single terminal.",
        "`anyMatch` is used for the boolean, not `filter(...).count() > 0`.",
        "The source list prints last, unchanged and still in input order.",
    ],
)


_MODULES.append(_jmod(
    26, 8, "Java 8+",
    "Streams: the pipeline",
    "A source, any number of lazy intermediate operations, and exactly one terminal that "
    "produces the answer and runs the whole thing.",
    """
Module 25 hand-wrote `countMatching`, `mapAll` and `each`. This module is the
JDK's version of all three, chained:

```java
words.stream()                       // source - the collection is never modified
     .filter(w -> w.length() > 3)    // intermediate: which
     .map(String::toUpperCase)       // intermediate: what
     .forEach(System.out::println);  // terminal: the answer, and the work
```

* **A stream is not a collection.** It stores nothing, has no `size()`, and is
  **single-use** - a second terminal throws `IllegalStateException`.
* **Intermediates are lazy.** They build a plan and return. Nothing runs until
  the terminal, and then it runs **element at a time**, not stage at a time.
* **`filter` and `map`** answer *which* and *what*; only `map` changes the
  element type. Filter early.
* **`sorted`, `distinct`, `limit`, `skip`** shape the stream. `sorted` and
  `distinct` are stateful - `sorted` must see everything before emitting
  anything - while `limit` short-circuits.
* **The terminal** is `forEach`, `count`, or one of the three matchers. A
  pipeline with no terminal does nothing at all, silently, which is the mistake
  everyone makes once.

`collect`, `Collectors` and `reduce` are module 27; the terminals that may find
nothing, and so return an `Optional`, are module 28.
""",
    _M26,
    capstone=_M26_CAP,
    objectives=[
        "Name the three parts of a pipeline and say which one does the work.",
        "Explain what laziness means, and predict the order of interleaved output from a filtered pipeline.",
        "Say why a stream cannot be reused, and what to do instead.",
        "Use `filter` and `map`, and say which one can change the element type.",
        "Justify filtering before mapping.",
        "Use `sorted`, `sorted(Comparator)`, `distinct`, `limit` and `skip`.",
        "Say which operations are stateful and which short-circuit, and why it matters.",
        "Choose between `forEach`, `count`, `anyMatch`, `allMatch` and `noneMatch`.",
        "Recognise a pipeline with no terminal operation, and say what it does.",
    ],
    why="Streams are the most visible thing about modern Java, and the thing most often "
        "written badly: pipelines with no terminal, streams reused after a terminal, "
        "`sorted` before `filter`, and `filter(...).count() > 0` where `anyMatch` was "
        "meant. Interviews ask for the difference between intermediate and terminal "
        "operations and for what laziness buys you, and both have precise answers. The "
        "pipeline idea also transfers directly - it is the same shape as a SQL query and "
        "as almost every data-processing API you will meet.",
    est_minutes=300,
    glossary=[
        _jg("stream", "A lazily-evaluated sequence of elements from a source. Not a "
                      "collection: it stores nothing and can be consumed once."),
        _jg("source", "Where a pipeline starts, usually `collection.stream()`. It is "
                      "never modified by the pipeline."),
        _jg("intermediate operation", "One that returns a new stream (`filter`, `map`, "
                                      "`sorted`, `distinct`, `limit`, `skip`) and does no "
                                      "work until a terminal runs."),
        _jg("terminal operation", "The single operation that produces a result and runs "
                                  "the pipeline (`forEach`, `count`, the matchers)."),
        _jg("laziness", "Intermediates build a plan rather than execute; nothing happens "
                        "until the terminal asks."),
        _jg("short-circuiting", "Stopping before the end of the stream: `limit`, "
                                "`anyMatch`, `allMatch`, `noneMatch`."),
        _jg("stateful operation", "One that must remember or see other elements - "
                                  "`sorted` (all of them) and `distinct` (everything so "
                                  "far)."),
        _jg("IllegalStateException", "What a stream throws when a second terminal "
                                     "operation is applied to it."),
    ],
    cheatsheet="""
```java
import java.util.stream.*;      // Stream lives here

// --- the shape ------------------------------------------------------------
words.stream()                       // SOURCE       (source is never modified)
     .filter(w -> w.length() > 3)    // intermediate (lazy, returns a Stream)
     .map(String::toUpperCase)       // intermediate
     .forEach(System.out::println);  // TERMINAL     (exactly one; runs everything)

// --- intermediates --------------------------------------------------------
.filter(Predicate<T>)     // which  - fewer elements, same type
.map(Function<T, R>)      // what   - same count, TYPE MAY CHANGE
.sorted()                 // natural order (Comparable)      STATEFUL
.sorted(Comparator.comparing(String::length))                STATEFUL
.distinct()               // equals/hashCode, keeps first     STATEFUL
.limit(n) / .skip(n)      // limit SHORT-CIRCUITS

// --- terminals available here ---------------------------------------------
.forEach(Consumer<T>)     // nothing
.count()                  // long
.anyMatch(p) .allMatch(p) .noneMatch(p)    // boolean, all short-circuit
// on an EMPTY stream:  allMatch -> true,  noneMatch -> true,  anyMatch -> false

// --- the three traps ------------------------------------------------------
words.stream().map(String::toUpperCase);   // NO TERMINAL: does nothing, silently
Stream<String> s = words.stream();
s.forEach(...); s.count();                 // IllegalStateException: single-use
.sorted().filter(...)                      // sorts things it then throws away
```
""",
    self_check=[
        "Can you name the three parts of a pipeline and say which one does the work?",
        "Can you predict which prints first: a `println` after building a pipeline, or the pipeline's own output?",
        "Can you say what happens on a second terminal operation, and why?",
        "Can you say which of `filter` and `map` can change the element type?",
        "Can you give the reason to filter before mapping, and before sorting?",
        "Can you say which operations are stateful, and what that costs?",
        "Can you say what `allMatch` returns on an empty stream, and why?",
        "Can you spot a pipeline with no terminal operation and say what it does?",
    ],
    review=[
        _jq("```java\nStream<String> s = words.stream().filter(w -> w.length() > 3);\nSystem.out.println(\"built\");\n```\nWhat has run?",
            ["Nothing but the println - intermediates are lazy",
             "The filter, on every word", "The filter, on the first word",
             "It does not compile"],
            0,
            "The pipeline is a plan until a terminal asks for an answer."),
        _jq("Calling `forEach` and then `count()` on the same stream…",
            ["throws IllegalStateException", "works", "returns 0", "recomputes"],
            0,
            "Streams are single-use; take a fresh one from the source."),
        _jq("Which pipeline does the least work?",
            [".filter(...).map(...).sorted()", ".sorted().map(...).filter(...)",
             ".map(...).sorted().filter(...)", "they are identical"],
            0,
            "Shrink the stream before doing per-element work, and sort last."),
        _jq("`words.stream().anyMatch(w -> w.length() > 3)` is better than `filter(...).count() > 0` because…",
            ["it short-circuits at the first match",
             "it is shorter only", "count is deprecated", "it handles null"],
            0,
            "The count has to examine every element; the matcher stops."),
    ],
    milestone="You can read and write a stream pipeline fluently: source, lazy "
              "intermediates, one terminal - and you can explain why nothing ran, why "
              "the second terminal threw, and why the `sorted` belongs after the "
              "`filter` rather than before it.",
))
