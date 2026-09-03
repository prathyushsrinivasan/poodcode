# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 26 practice - streams: the pipeline.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[26]`.
#
# Same gate as the module file: no `collect`, no `Collectors`, no `reduce`, no
# primitive streams (module 27) and no `Optional` (module 28). Every pipeline
# here ends in `forEach`, `count` or one of the three matchers, which is enough
# to drill the SHAPE without borrowing from a module that has not been written.
#
# The five families are the four lessons plus one that chains them: the pipeline
# itself (laziness, single-use, the untouched source), `filter`/`map`, the
# shaping operations, the terminals, and finally full pipelines.
#
# All sequential, so encounter order and the element-at-a-time interleaving in
# family A are deterministic.
# ---------------------------------------------------------------------------

_IMPORTS26P = ("import java.util.*;\n"
               "import java.util.function.*;\n"
               "import java.util.stream.*;\n")


def _p26prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS26P,
    )


def _p26m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p26prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p26b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p26prog(helpers, body),
                body, tests, hints)


def _p26s(eid, title, difficulty, prompt, body, tests, hints):
    """No helpers - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan(body, imports=_IMPORTS26P), body, tests, hints)


_RD_W26P = ("        int n = sc.nextInt();\n"
            "        List<String> words = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words.add(sc.next());\n"
            "        }\n")

_RD_N26P = ("        int n = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")

_WS26P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS26P = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

_DUP26P = (["ada", "bo", "ada", "cy"], ["solo", "solo"], ["x", "yy", "x", "x"],
           ["pear", "fig", "pear"], ["a", "b", "a", "b", "c"])


def _w26p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n26p(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jl26p(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _dd26p(ws):
    return list(dict.fromkeys(ws))


# --- Family A - the pipeline itself ------------------------------------------

_P26_A = _jfam(
    "p26-pipeline", "Source, intermediates, terminal",
    "A plan that does nothing until you ask it for an answer.",
    """
```java
words.stream()                       // SOURCE - never modifies the collection
     .filter(w -> w.length() > 3)    // intermediate - lazy, returns a Stream
     .forEach(System.out::println);  // TERMINAL - exactly one; runs everything
```

Three facts drive this whole family:

* **Intermediates are lazy.** They build the plan and return immediately, so a
  `println` written after the pipeline still prints first.
* **It runs element at a time.** Once the terminal starts, each element goes
  through the whole pipeline before the next begins - so tracing output
  interleaves rather than arriving in stages.
* **A stream is single-use.** A second terminal on the same stream throws
  `IllegalStateException`. Ask the source for a fresh one.
""",
    [
        _p26s("j26-pa-count", "The shortest pipeline", "Intro",
              "Print how many elements the stream has, then the list's own size - the "
              "same number by two different routes.",
              _RD_W26P
              + "        System.out.println(words.stream().count());\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(len(ws), len(ws))) for ws in _WS26P],
              ["`count()` is a terminal operation returning a `long`.",
               "`words.stream().count()`",
               "With no intermediate operations the count is just the size.",
               "A stream has no `size()` of its own - only a terminal can answer."]),

        _p26s("j26-pa-filtercount", "Counting survivors", "Intro",
              "Print how many words are longer than three characters, then the list "
              "size - showing the filter changed the count but not the list.",
              _RD_W26P
              + "        System.out.println(words.stream().filter(w -> w.length() > 3).count());\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(sum(1 for w in ws if len(w) > 3), len(ws)))
               for ws in _WS26P],
              ["Source, one intermediate, one terminal.",
               "`filter` takes a `Predicate<String>`.",
               "`words.stream().filter(w -> w.length() > 3).count()`",
               "The second line proves nothing was removed from the list."]),

        _p26s("j26-pa-lazy", "Nothing runs until you ask", "Hard",
              "Build a filtering pipeline whose predicate prints `testing ` and the word "
              "before deciding, print `built`, and only then run it with `forEach`. Watch "
              "where `built` lands.",
              _RD_W26P
              + "        Stream<String> pipeline = words.stream().filter(w -> {\n"
                "            System.out.println(\"testing \" + w);\n"
                "            return w.length() > 3;\n"
                "        });\n"
                "        System.out.println(\"built\");\n"
                "        pipeline.forEach(System.out::println);",
              [_w26p(ws, _nl(*(["built"]
                               + [line for w in ws
                                  for line in (["testing " + w]
                                               + ([w] if len(w) > 3 else []))])))
               for ws in _WS26P],
              ["The variable's type is `Stream<String>` - an intermediate returns a "
               "stream, not a list.",
               "The lambda prints AND returns, so it needs a braced body.",
               "`built` comes first: the filter has not run when the variable is "
               "assigned.",
               "Then each word is tested and, if it passes, printed immediately - "
               "before the next word is tested.",
               "Words that fail print only their `testing` line."]),

        _p26s("j26-pa-fresh", "Two questions, two streams", "Easy",
              "Print every word, then print the count - taking a FRESH stream for each, "
              "because one stream allows only one terminal.",
              _RD_W26P
              + "        words.stream().forEach(System.out::println);\n"
                "        System.out.println(words.stream().count());",
              [_w26p(ws, _nl(*(list(ws) + [len(ws)]))) for ws in _WS26P],
              ["Reusing one stream would throw *IllegalStateException: stream has "
               "already been operated upon or closed*.",
               "Call `words.stream()` twice - the list will hand out as many as you "
               "want.",
               "`forEach` takes a `Consumer`, so `System.out::println` fits.",
               "There is no way to reset a stream, and no need for one."]),

        _p26s("j26-pa-source", "The source is untouched", "Easy",
              "Print the words longer than three characters through a stream, then print "
              "the original list and its size.",
              _RD_W26P
              + "        words.stream().filter(w -> w.length() > 3).forEach(System.out::println);\n"
                "        System.out.println(words);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*([w for w in ws if len(w) > 3]
                               + [_jl26p(ws), len(ws)])))
               for ws in _WS26P],
              ["A pipeline reads its source; it never edits it.",
               "`removeIf` would be the method that really does modify the list.",
               "When nothing matches, the pipeline prints nothing at all.",
               "The list prints in its original input order."]),
    ])


# --- Family B - filter and map -----------------------------------------------

_P26_B = _jfam(
    "p26-filtermap", "`filter` and `map`",
    "Which ones, and what each becomes.",
    """
```java
.filter(Predicate<T>)    // WHICH - fewer elements, same type
.map(Function<T, R>)     // WHAT  - same count, and the TYPE MAY CHANGE
```

`map` is where a pipeline changes shape: `map(String::length)` turns a
`Stream<String>` into a `Stream<Integer>`, and everything after it works on
numbers.

**Filter early.** These give the same answer:

```java
.filter(w -> w.length() > 3).map(String::toUpperCase)
.map(String::toUpperCase).filter(w -> w.length() > 3)
```

but the first calls `toUpperCase` only on the words that survived.
""",
    [
        _p26s("j26-pb-filter", "Keeping some", "Intro",
              "Print only the words starting with `a`, then the list size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .filter(w -> w.startsWith(\"a\"))\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*([w for w in ws if w.startswith("a")] + [len(ws)])))
               for ws in _WS26P],
              ["`filter` takes a `Predicate<String>`.",
               "`.filter(w -> w.startsWith(\"a\"))`",
               "`startsWith` is module 7's, unchanged.",
               "Lists with no match print only the size."]),

        _p26s("j26-pb-map", "Turning each into something else", "Intro",
              "Print every word in capitals using a method reference, then the list "
              "size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .map(String::toUpperCase)\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*([w.upper() for w in ws] + [len(ws)]))) for ws in _WS26P],
              ["`map` takes a `Function<String, String>` here.",
               "`String::toUpperCase` is module 25's unbound reference.",
               "`map` replaces every element; it never removes any.",
               "The stream is the same length afterwards."]),

        _p26s("j26-pb-type", "Changing the element type", "Easy",
              "Print the length of every word, then the list size. After the map the "
              "pipeline is a stream of numbers.",
              _RD_W26P
              + "        words.stream()\n"
                "             .map(String::length)\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*([len(w) for w in ws] + [len(ws)]))) for ws in _WS26P],
              ["`String::length` extracts an `int`, boxed to `Integer`.",
               "The pipeline is now a `Stream<Integer>`.",
               "`.map(String::length)`",
               "`println` is overloaded for every type, so `forEach` still fits."]),

        _p26s("j26-pb-chain", "Filter first, then map", "Medium",
              "Print the words longer than three characters, in capitals, then the list "
              "size - chained in the order that does the least work.",
              _RD_W26P
              + "        words.stream()\n"
                "             .filter(w -> w.length() > 3)\n"
                "             .map(String::toUpperCase)\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*([w.upper() for w in ws if len(w) > 3] + [len(ws)])))
               for ws in _WS26P],
              ["Filter before mapping so `toUpperCase` runs only on survivors.",
               "One operation per line reads better once there are three.",
               "The semicolon belongs at the end of the whole chain.",
               "Reversing the two prints the same thing after more work."]),

        _p26s("j26-pb-numbers", "The same two on numbers", "Easy",
              "Print each positive number doubled, then the list size.",
              _RD_N26P
              + "        nums.stream()\n"
                "            .filter(x -> x > 0)\n"
                "            .map(x -> x * 2)\n"
                "            .forEach(System.out::println);\n"
                "        System.out.println(nums.size());",
              [_n26p(xs, _nl(*([x * 2 for x in xs if x > 0] + [len(xs)])))
               for xs in _NS26P],
              ["The stream is a `Stream<Integer>`; the lambdas unbox automatically.",
               "`.filter(x -> x > 0)` then `.map(x -> x * 2)`.",
               "The result of `x * 2` is an `int`, re-boxed on the way back into the "
               "stream.",
               "A list with no positives prints only the size."]),
    ])


# --- Family C - shaping ------------------------------------------------------

_P26_C = _jfam(
    "p26-shaping", "`sorted`, `distinct`, `limit`, `skip`",
    "Reordering, de-duplicating and paging.",
    """
```java
.sorted()                                      // natural order (Comparable)
.sorted(Comparator.comparing(String::length))  // by an extracted key
.distinct()                                    // equals/hashCode, keeps the first
.skip(1).limit(2)                              // a page
```

**`sorted` and `distinct` are stateful**: `sorted` cannot emit anything until it
has seen every element, and `distinct` must remember everything so far. That is
why the "element at a time" story stops at a `sorted`, and one more reason to
filter before you sort.

**`limit` short-circuits** - it stops the pipeline as soon as it has enough.
""",
    [
        _p26s("j26-pc-sorted", "Alphabetical", "Intro",
              "Print the words in natural order, then print the source list to show it "
              "was not reordered.",
              _RD_W26P
              + "        words.stream()\n"
                "             .sorted()\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words);",
              [_w26p(ws, _nl(*(sorted(ws) + [_jl26p(ws)]))) for ws in _WS26P],
              ["No argument means the natural ordering - `String.compareTo`.",
               "`.sorted()`",
               "The list afterwards is still in input order.",
               "`words.sort(...)` is the one that would really reorder it."]),

        _p26s("j26-pc-bykey", "By length", "Easy",
              "Print the words shortest first using `Comparator.comparing` and a method "
              "reference, then the list size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .sorted(Comparator.comparing(String::length))\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(sorted(ws, key=len) + [len(ws)]))) for ws in _WS26P],
              ["`sorted` is overloaded - no argument, or one `Comparator`.",
               "`Comparator.comparing(String::length)` from module 25.",
               "Stable, so equal-length words keep their input order.",
               "One word per line, then the count."]),

        _p26s("j26-pc-distinct", "Removing repeats", "Easy",
              "The input repeats some words. Print each one once in the order it first "
              "appeared, then the ORIGINAL list size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .distinct()\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(_dd26p(ws) + [len(ws)]))) for ws in _DUP26P],
              ["`distinct()` takes no arguments and uses `equals`/`hashCode`.",
               "It keeps the FIRST occurrence, so first-seen order survives.",
               "`.distinct()`",
               "The size printed at the end still counts the duplicates."]),

        _p26s("j26-pc-limit", "Just the first two", "Easy",
              "Print at most the first two words in alphabetical order, then the list "
              "size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .sorted()\n"
                "             .limit(2)\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(sorted(ws)[:2] + [len(ws)]))) for ws in _WS26P],
              ["Sort first, then take - the other order would take two arbitrary words "
               "and sort those.",
               "`.limit(2)` keeps at most two; a shorter list simply yields fewer.",
               "`limit` short-circuits once it has enough.",
               "A one-word list prints that one word."]),

        _p26s("j26-pc-page", "A page of results", "Medium",
              "Print a page of the sorted words: skip the first, then take at most two. "
              "Print the list size at the end.",
              _RD_W26P
              + "        words.stream()\n"
                "             .sorted()\n"
                "             .skip(1)\n"
                "             .limit(2)\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(sorted(ws)[1:3] + [len(ws)]))) for ws in _WS26P],
              ["Order them the way you would say it: sort, skip, take.",
               "`.skip(1)` then `.limit(2)`.",
               "A one-word list prints nothing from the pipeline - skipping one leaves "
               "none.",
               "Swapping `skip` and `limit` asks a completely different question."]),
    ])


# --- Family D - terminals ----------------------------------------------------

_P26_D = _jfam(
    "p26-terminal", "The terminal operation",
    "`forEach`, `count`, and the three matchers.",
    """
| Terminal | Gives you |
|---|---|
| `forEach(Consumer)` | nothing - an action per element |
| `count()` | `long` |
| `anyMatch(p)` / `allMatch(p)` / `noneMatch(p)` | `boolean`, all short-circuiting |

**A pipeline with no terminal does nothing at all** - silently, with no warning
and no output. It is the most common streams mistake there is.

**On an empty stream**, `allMatch` and `noneMatch` are both `true` while
`anyMatch` is `false`. "All of nothing" is vacuously true.

`anyMatch(p)` beats `filter(p).count() > 0`: the matcher stops at the first
match, the count has to see everything.
""",
    [
        _p26s("j26-pd-any", "Is there one?", "Intro",
              "Print whether any word is longer than three characters, then the list "
              "size.",
              _RD_W26P
              + "        System.out.println(words.stream().anyMatch(w -> w.length() > 3));\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(_jbool(any(len(w) > 3 for w in ws)), len(ws)))
               for ws in _WS26P],
              ["`anyMatch` takes a `Predicate` and returns a `boolean`.",
               "`words.stream().anyMatch(w -> w.length() > 3)`",
               "It short-circuits at the first match rather than scanning everything.",
               "This is the right tool where `filter(...).count() > 0` would also "
               "work."]),

        _p26s("j26-pd-all", "Are they all?", "Intro",
              "Print whether every word is at least two characters long, then the list "
              "size.",
              _RD_W26P
              + "        System.out.println(words.stream().allMatch(w -> w.length() >= 2));\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(_jbool(all(len(w) >= 2 for w in ws)), len(ws)))
               for ws in _WS26P],
              ["`allMatch` short-circuits on the first element that FAILS.",
               "`words.stream().allMatch(w -> w.length() >= 2)`",
               "Two of these lists contain a one-character word.",
               "On an empty stream this would be `true`."]),

        _p26s("j26-pd-none", "Is there none?", "Easy",
              "Print whether no word is a single character, then the list size.",
              _RD_W26P
              + "        System.out.println(words.stream().noneMatch(w -> w.length() == 1));\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(_jbool(not any(len(w) == 1 for w in ws)), len(ws)))
               for ws in _WS26P],
              ["`noneMatch` is the negation of `anyMatch`, and short-circuits the same "
               "way.",
               "`words.stream().noneMatch(w -> w.length() == 1)`",
               "It returns `true` when nothing matches - including on an empty stream.",
               "Writing `!anyMatch(...)` would work and reads worse."]),

        _p26s("j26-pd-counts", "Two counts", "Easy",
              "Print how many words are longer than three characters, how many remain "
              "after removing duplicates, and the original size.",
              _RD_W26P
              + "        System.out.println(words.stream().filter(w -> w.length() > 3).count());\n"
                "        System.out.println(words.stream().distinct().count());\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(sum(1 for w in ws if len(w) > 3),
                             len(_dd26p(ws)), len(ws)))
               for ws in _DUP26P],
              ["Each question needs its own fresh stream.",
               "`count()` returns a `long` and prints like an int.",
               "`distinct().count()` is the number of unique words.",
               "The third line still counts the duplicates."]),

        _p26s("j26-pd-report", "Four answers about numbers", "Medium",
              "Using the numbers, print: how many are positive, whether any is negative, "
              "whether all are above minus ten, and the list size.",
              _RD_N26P
              + "        System.out.println(nums.stream().filter(x -> x > 0).count());\n"
                "        System.out.println(nums.stream().anyMatch(x -> x < 0));\n"
                "        System.out.println(nums.stream().allMatch(x -> x > -10));\n"
                "        System.out.println(nums.size());",
              [_n26p(xs, _nl(sum(1 for x in xs if x > 0),
                             _jbool(any(x < 0 for x in xs)),
                             _jbool(all(x > -10 for x in xs)),
                             len(xs)))
               for xs in _NS26P],
              ["Four questions, four fresh streams.",
               "`filter(...).count()` for the first; a matcher for each boolean.",
               "One list contains exactly minus nine - check the boundary rather than "
               "guessing.",
               "Four printed lines."]),
    ])


# --- Family E - whole pipelines ----------------------------------------------

_P26_E = _jfam(
    "p26-combined", "Whole pipelines",
    "Several stages, in the order that does the least work.",
    """
```java
words.stream()
     .filter(w -> w.length() > 2)    // shrink first
     .map(String::toUpperCase)       // then transform what is left
     .distinct()                     // then de-duplicate
     .sorted()                       // sort the smallest stream you can
     .forEach(System.out::println);  // one terminal
```

The order is not decoration. `filter` first means every later stage does less
work; `sorted` last means the stage that has to see *everything* sees as little
as possible. And a `map` before a `distinct` changes what counts as a duplicate
- capitalising first makes `ada` and `ADA` the same element.
""",
    [
        _p26s("j26-pe-sortfilter", "Filter, then sort", "Easy",
              "Print the words longer than two characters in alphabetical order, then "
              "the list size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .filter(w -> w.length() > 2)\n"
                "             .sorted()\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(sorted([w for w in ws if len(w) > 2]) + [len(ws)])))
               for ws in _WS26P],
              ["Filter before sorting: the sort then has fewer elements to order.",
               "`.filter(w -> w.length() > 2)` then `.sorted()`.",
               "`sorted` must see every element that reaches it before it emits any.",
               "Lists where nothing survives print only the size."]),

        _p26s("j26-pe-mapdistinct", "Map, then de-duplicate", "Medium",
              "Print how many distinct word LENGTHS there are, then the list size.",
              _RD_W26P
              + "        System.out.println(words.stream()\n"
                "             .map(String::length)\n"
                "             .distinct()\n"
                "             .count());\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(len(set(len(w) for w in ws)), len(ws)))
               for ws in _WS26P],
              ["Map to lengths first, then de-duplicate those.",
               "After the map the stream is a `Stream<Integer>`, and `distinct` uses "
               "`Integer.equals`.",
               "`.map(String::length).distinct().count()`",
               "Two words of the same length collapse to one entry."]),

        _p26s("j26-pe-full", "Four stages", "Medium",
              "Print the words longer than two characters, in capitals, de-duplicated "
              "and alphabetically ordered - then the list size.",
              _RD_W26P
              + "        words.stream()\n"
                "             .filter(w -> w.length() > 2)\n"
                "             .map(String::toUpperCase)\n"
                "             .distinct()\n"
                "             .sorted()\n"
                "             .forEach(System.out::println);\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(*(sorted(_dd26p([w.upper() for w in ws if len(w) > 2]))
                               + [len(ws)])))
               for ws in _DUP26P],
              ["The order is filter, map, distinct, sorted, forEach.",
               "Filtering first means the map runs on fewer words.",
               "Capitalising before de-duplicating means case differences collapse.",
               "Sorting last means it handles the smallest stream possible.",
               "One terminal ends the chain."]),

        _p26s("j26-pe-numbers", "A pipeline over numbers", "Medium",
              "Print the positive numbers in ascending order, then how many there were, "
              "then the list size.",
              _RD_N26P
              + "        nums.stream()\n"
                "            .filter(x -> x > 0)\n"
                "            .sorted()\n"
                "            .forEach(System.out::println);\n"
                "        System.out.println(nums.stream().filter(x -> x > 0).count());\n"
                "        System.out.println(nums.size());",
              [_n26p(xs, _nl(*(sorted([x for x in xs if x > 0])
                               + [sum(1 for x in xs if x > 0), len(xs)])))
               for xs in _NS26P],
              ["`Integer` is `Comparable`, so `.sorted()` needs no argument.",
               "The count needs its own fresh stream - the first one is spent.",
               "A list with no positives prints nothing, then `0`, then its size.",
               "Three sections of output."]),

        _p26m("j26-pe-method", "longWordCount", "Medium",
              "Write `longWordCount`, which returns how many elements of a list are "
              "longer than a given limit - using a stream rather than a loop. `main` "
              "calls it twice with different limits.",
              """
    static long longWordCount(List<String> items, int limit) {
        return items.stream().filter(w -> w.length() > limit).count();
    }
""",
              _RD_W26P
              + "        System.out.println(longWordCount(words, 1));\n"
                "        System.out.println(longWordCount(words, 3));\n"
                "        System.out.println(words.size());",
              [_w26p(ws, _nl(sum(1 for w in ws if len(w) > 1),
                             sum(1 for w in ws if len(w) > 3),
                             len(ws)))
               for ws in _WS26P],
              ["`count()` returns a `long`, so that is the return type.",
               "The lambda captures `limit`, which is a parameter and so effectively "
               "final - module 25.",
               "`return items.stream().filter(w -> w.length() > limit).count();`",
               "One expression, no loop, and the list is untouched."]),
    ])


_PRACTICE[26] = [_P26_A, _P26_B, _P26_C, _P26_D, _P26_E]
