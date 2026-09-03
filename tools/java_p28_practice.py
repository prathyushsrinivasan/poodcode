# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 28 practice - Optional.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[28]`.
#
# The last practice file in the course. Nothing is gated any more, so these
# problems draw freely on Part 8: lambdas and method references from 25,
# pipelines from 26, collectors from 27.
#
# Two rules held throughout, both inherited from the module file:
#   * NO `get()` in any reference solution. The point of the module is that
#     every use of it is a question left unanswered.
#   * `orElseThrow()` with no argument (Java 10+) and `Optional.isEmpty()`
#     (Java 11+) do not appear. The Supplier form of `orElseThrow` and
#     `!isPresent()` work wherever the rest of Part 8 does.
#
# Word lists have a UNIQUE longest element so `max(comparing(length))` has one
# right answer; number lists divide evenly so every average prints exactly.
# ---------------------------------------------------------------------------

_IMPORTS28P = ("import java.util.*;\n"
               "import java.util.function.*;\n"
               "import java.util.stream.*;\n")


def _p28prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS28P,
    )


def _p28m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p28prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p28b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p28prog(helpers, body),
                body, tests, hints)


def _p28s(eid, title, difficulty, prompt, body, tests, hints):
    """No helpers - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt,
                _jscan(body, imports=_IMPORTS28P), body, tests, hints)


_RD_W28P = ("        int n = sc.nextInt();\n"
            "        List<String> words = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words.add(sc.next());\n"
            "        }\n")

_RD_N28P = ("        int n = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")

_WS28P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gam", "d"])

_NS28P = ([3, 1, 2], [5], [-4, -8, -3], [10, 10, 4], [7, 2, 9, 4])

_WL28P = tuple((ws, 3) for ws in _WS28P)

_FIND28P = ("    static Optional<String> firstLongerThan(List<String> items, int limit) {\n"
            "        for (String item : items) {\n"
            "            if (item.length() > limit) {\n"
            "                return Optional.of(item);\n"
            "            }\n"
            "        }\n"
            "        return Optional.empty();\n"
            "    }")


def _w28p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n28p(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wl28p(ws, limit, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(limit)]), out)


def _jl28p(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _f28p(ws, limit=3):
    for w in ws:
        if len(w) > limit:
            return w
    return None


def _jo28p(value):
    return "Optional.empty" if value is None else f"Optional[{value}]"


# --- Family A - making one ---------------------------------------------------

_P28_A = _jfam(
    "p28-making", "Making an Optional",
    "`of`, `ofNullable`, `empty` - and a return type that admits absence.",
    """
| Call | Meaning |
|---|---|
| `Optional.of(value)` | definitely present - **throws NPE on null** |
| `Optional.ofNullable(value)` | present, or empty if null |
| `Optional.empty()` | definitely absent |

`of` throwing on null is deliberate: it is an assertion, and it fails loudly
where you were wrong rather than quietly later.

The real move is in the signature. `Optional<String> find(...)` cannot be
mistaken for a method that always has an answer, and `String find(...)`
returning null always can be.

Printing an Optional shows `Optional[ada]` or `Optional.empty` - handy in a
drill, not something to do in real output.
""",
    [
        _p28s("j28-pa-ofnullable", "Wrapping a maybe-null", "Intro",
              "The loop leaves `found` set or null. Wrap it without assuming which, then "
              "print whether it is present, the container itself, and the list size.",
              _RD_W28P
              + "        String found = null;\n"
                "        for (String w : words) {\n"
                "            if (w.length() > 3) {\n"
                "                found = w;\n"
                "                break;\n"
                "            }\n"
                "        }\n"
                "        Optional<String> maybe = Optional.ofNullable(found);\n"
                "        System.out.println(maybe.isPresent());\n"
                "        System.out.println(maybe);\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl(_jbool(_f28p(ws) is not None), _jo28p(_f28p(ws)), len(ws)))
               for ws in _WS28P],
              ["`Optional.of` would throw here - `found` may legitimately be null.",
               "`Optional.ofNullable(found)` turns null into `Optional.empty()`.",
               "An Optional prints as `Optional[value]` or `Optional.empty`.",
               "Two of the five inputs have no word longer than three characters."]),

        _p28s("j28-pa-of", "Asserting presence", "Intro",
              "The list is never empty, so its first word certainly exists. Build an "
              "Optional that says so, then print whether it is present, the container, "
              "and the size.",
              _RD_W28P
              + "        Optional<String> firstWord = Optional.of(words.get(0));\n"
                "        System.out.println(firstWord.isPresent());\n"
                "        System.out.println(firstWord);\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl("true", _jo28p(ws[0]), len(ws))) for ws in _WS28P],
              ["`ofNullable` would work and would claim less.",
               "`Optional.of(words.get(0))` asserts the value is there.",
               "If the assumption were wrong this line would throw - which is why you "
               "choose it.",
               "`isPresent()` is therefore always true."]),

        _p28m("j28-pa-find", "firstLongerThan", "Easy",
              "Write `firstLongerThan`, returning the first word longer than a limit, or "
              "an empty Optional when there is none.",
              """
    static Optional<String> firstLongerThan(List<String> items, int limit) {
        for (String item : items) {
            if (item.length() > limit) {
                return Optional.of(item);
            }
        }
        return Optional.empty();
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.isPresent());\n"
                "        System.out.println(found);\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit, _nl(_jbool(_f28p(ws, limit) is not None),
                                     _jo28p(_f28p(ws, limit)), len(ws)))
               for (ws, limit) in _WL28P],
              ["The return type is `Optional<String>`.",
               "`return Optional.of(item);` from inside the loop.",
               "`return Optional.empty();` after it.",
               "`of` is right inside the loop - `item` is certainly not null."]),

        _p28m("j28-pa-shortest", "firstShorterThan", "Easy",
              "Write the mirror image: the first word STRICTLY shorter than a limit, or "
              "an empty Optional.",
              """
    static Optional<String> firstShorterThan(List<String> items, int limit) {
        for (String item : items) {
            if (item.length() < limit) {
                return Optional.of(item);
            }
        }
        return Optional.empty();
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstShorterThan(words, limit);\n"
                "        System.out.println(found.isPresent());\n"
                "        System.out.println(found);\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_jbool(any(len(w) < limit for w in ws)),
                          _jo28p(next((w for w in ws if len(w) < limit), None)),
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["Same shape, comparison reversed.",
               "Strictly shorter, so a word of exactly `limit` characters does not "
               "match.",
               "`return Optional.of(item);` on the first match.",
               "One list has no word under three characters at all."]),

        _p28m("j28-pa-startingwith", "firstStartingWith", "Medium",
              "Write `firstStartingWith`, returning the first word beginning with a "
              "given prefix, or an empty Optional.",
              """
    static Optional<String> firstStartingWith(List<String> items, String prefix) {
        for (String item : items) {
            if (item.startsWith(prefix)) {
                return Optional.of(item);
            }
        }
        return Optional.empty();
    }
""",
              _RD_W28P
              + "        String prefix = sc.next();\n"
                "        Optional<String> found = firstStartingWith(words, prefix);\n"
                "        System.out.println(found.isPresent());\n"
                "        System.out.println(found.orElse(\"none\"));\n"
                "        System.out.println(prefix);",
              [_case("\n".join([str(len(ws)), " ".join(ws), prefix]),
                     _nl(_jbool(any(w.startswith(prefix) for w in ws)),
                         next((w for w in ws if w.startswith(prefix)), "none"),
                         prefix))
               for (ws, prefix) in ((["ada", "bo", "cy"], "a"), (["solo"], "z"),
                                    (["x", "yy", "zzz"], "y"),
                                    (["pear", "fig"], "f"),
                                    (["alpha", "beta", "gam", "d"], "b"))],
              ["`startsWith` is module 7's.",
               "The parameter is a plain `String`, not an Optional - the caller knows "
               "it has one.",
               "`return Optional.of(item);` on the first match.",
               "One input has no match at all, and prints `none`."]),
    ])


# --- Family B - unwrapping ---------------------------------------------------

_P28_B = _jfam(
    "p28-unwrap", "Getting the value out",
    "`orElse`, `orElseGet`, `orElseThrow`, `ifPresent` - never `get`.",
    """
```java
found.orElse("none");                                   // a constant default
found.orElseGet(Main::expensive);                       // a computed one, lazily
found.orElseThrow(() -> new IllegalStateException("")); // absence is a bug
found.ifPresent(w -> System.out.println(w));            // act, or do nothing
```

**`orElse` takes a value, so its argument is evaluated every time** - present or
absent. `orElseGet` takes a `Supplier` and only calls it when empty. If the
default costs anything, that difference is real work added to the happy path.

`get()` appears nowhere in this family, on purpose. Every `get()` is a question
about absence that has not been answered.
""",
    [
        _p28b("j28-pb-orelse", "A default value", "Intro",
              "`firstLongerThan` is written. Print the word it finds, or `none`, then "
              "the list size.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit, _nl(_f28p(ws, limit) or "none", len(ws)))
               for (ws, limit) in _WL28P],
              ["`orElse` takes the value to use when empty.",
               "`found.orElse(\"none\")`",
               "The default is a constant, so `orElse` is the right choice.",
               "Two inputs print `none`."]),

        _p28b("j28-pb-ifpresent", "Act, or do nothing", "Easy",
              "Print the found word in capitals if there is one and nothing at all if "
              "there is not, then print `done` either way.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        found.ifPresent(w -> System.out.println(w.toUpperCase()));\n"
                "        System.out.println(\"done\");",
              [_wl28p(ws, limit,
                      _nl(*(([_f28p(ws, limit).upper()] if _f28p(ws, limit) else [])
                            + ["done"])))
               for (ws, limit) in _WL28P],
              ["`ifPresent` takes a `Consumer<String>`.",
               "`found.ifPresent(w -> System.out.println(w.toUpperCase()));`",
               "It returns nothing, so nothing can be chained after it.",
               "When empty, the lambda never runs and only `done` prints."]),

        _p28b("j28-pb-orelsethrow", "When absence is an error", "Medium",
              "Unwrap with an `IllegalStateException` of your own inside a `try`, "
              "printing the word on success and the exception's simple name on failure. "
              "Then print the list size.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        try {\n"
                "            System.out.println(found.orElseThrow(() -> new IllegalStateException(\"missing\")));\n"
                "        } catch (IllegalStateException e) {\n"
                "            System.out.println(e.getClass().getSimpleName());\n"
                "        }\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit) or "IllegalStateException", len(ws)))
               for (ws, limit) in _WL28P],
              ["`orElseThrow` takes a `Supplier` building the exception, called only "
               "when empty.",
               "The lambda takes no arguments: `() -> new "
               "IllegalStateException(\"missing\")`.",
               "This beats `get()` because the exception says what was expected.",
               "Print the exception's NAME, never its message."]),

        _p28b("j28-pb-lazy", "`orElse` versus `orElseGet`", "Hard",
              "`fallback()` announces itself. Print the result with `orElse` and then "
              "with `orElseGet` plus a method reference, and watch how often `computing` "
              "appears.",
              """
    static String fallback() {
        System.out.println("computing");
        return "none";
    }

"""
              + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.orElse(fallback()));\n"
                "        System.out.println(found.orElseGet(Main::fallback));",
              [_wl28p(ws, limit,
                      _nl(*(["computing", _f28p(ws, limit), _f28p(ws, limit)]
                            if _f28p(ws, limit)
                            else ["computing", "none", "computing", "none"])))
               for (ws, limit) in _WL28P],
              ["`orElse` takes a value, so `fallback()` runs before `orElse` is even "
               "called.",
               "`orElseGet` takes a `Supplier`, so it only runs when empty.",
               "`Main::fallback` is a static method reference - module 25.",
               "Present: `computing` once, then the word twice.",
               "Absent: `computing` twice, once per call."]),

        _p28m("j28-pb-method", "describe", "Medium",
              "Write `describe`, which turns an Optional into a printable String: the "
              "value in capitals when present, and `NONE` when not - without `get()` and "
              "without an `if`.",
              """
    static String describe(Optional<String> value) {
        return value.map(String::toUpperCase).orElse("NONE");
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        System.out.println(describe(words.stream().filter(w -> w.length() > limit).findFirst()));\n"
                "        System.out.println(describe(Optional.empty()));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit).upper() if _f28p(ws, limit) else "NONE",
                          "NONE", len(ws)))
               for (ws, limit) in _WL28P],
              ["One expression: `map` then `orElse`.",
               "`return value.map(String::toUpperCase).orElse(\"NONE\");`",
               "An `Optional` PARAMETER is normally poor design - it is justified here "
               "only because describing an Optional is literally the method's job.",
               "The second call passes `Optional.empty()` directly, so it always prints "
               "`NONE`."]),
    ])


# --- Family C - chaining -----------------------------------------------------

_P28_C = _jfam(
    "p28-chain", "`map`, `filter`, `flatMap`",
    "Describe the whole computation, then decide about absence once, at the end.",
    """
```java
found.filter(w -> w.length() > 4)
     .map(String::toUpperCase)
     .orElse("none");
```

* **`map`** applies a function only when a value is present, and keeps an empty
  Optional empty.
* **`filter`** turns "present but unsuitable" into plain absent.
* **`flatMap`** is for a function that returns an Optional itself - `map` there
  would give you `Optional<Optional<T>>`.

Same rule as streams: **`map` for a plain value, `flatMap` for another
container.**

The payoff is that the `if` disappears, and absence is decided in exactly one
place - the `orElse` at the end.
""",
    [
        _p28b("j28-pc-map", "Transforming a maybe", "Intro",
              "Print the found word in capitals, or `NONE` - with no `if` anywhere. Then "
              "print the list size.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.map(String::toUpperCase).orElse(\"NONE\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit).upper() if _f28p(ws, limit) else "NONE",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["`map` takes a `Function` and applies it only when present.",
               "`found.map(String::toUpperCase).orElse(\"NONE\")`",
               "When empty, `toUpperCase` never runs.",
               "Absence is decided once, at the end of the chain."]),

        _p28b("j28-pc-filter", "Present, but not good enough", "Easy",
              "Print the found word only when it is longer than four characters, and "
              "`none` otherwise. Then print the list size.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.filter(w -> w.length() > 4).orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit)
                          if (_f28p(ws, limit) and len(_f28p(ws, limit)) > 4)
                          else "none",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["`filter` empties the Optional when the predicate fails.",
               "An already-empty Optional stays empty and the predicate never runs.",
               "`solo` and `pear` are exactly four characters, so a strict `> 4` "
               "rejects them.",
               "Only `alpha` survives."]),

        _p28b("j28-pc-chain", "The whole sentence", "Medium",
              "Chain both: keep the found word only if it is longer than three "
              "characters, capitalise it, and fall back to `none`. Then print the list "
              "size.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found\n"
                "                .filter(w -> w.length() > 3)\n"
                "                .map(String::toUpperCase)\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit).upper()
                          if (_f28p(ws, limit) and len(_f28p(ws, limit)) > 3)
                          else "none",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["Filter first, then map - the same habit as a stream pipeline.",
               "Each operation returns another Optional, which is what lets them "
               "chain.",
               "`orElse` at the very end is the only place absence is decided.",
               "No `if` and no null check anywhere."]),

        _p28b("j28-pc-flatmap", "When the function returns one too", "Hard",
              "`firstLetter` returns an Optional of its own. Apply it to the found word "
              "without nesting one Optional inside another, falling back to `none`. Then "
              "print the list size.",
              """
    static Optional<String> firstLetter(String value) {
        if (value.length() == 0) {
            return Optional.empty();
        }
        return Optional.of(value.substring(0, 1));
    }

"""
              + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.flatMap(Main::firstLetter).orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit)[0] if _f28p(ws, limit) else "none", len(ws)))
               for (ws, limit) in _WL28P],
              ["`map(Main::firstLetter)` would give `Optional<Optional<String>>`.",
               "`flatMap` removes the extra layer.",
               "`found.flatMap(Main::firstLetter).orElse(\"none\")`",
               "The rule matches streams: `flatMap` when the function returns a "
               "container."]),

        _p28m("j28-pc-initial", "initialOf", "Medium",
              "Write `initialOf`, returning the capitalised first letter of the first "
              "word longer than a limit, or `-` when there is none - as one chain, with "
              "no `if` and no `get()`.",
              """
    static String initialOf(List<String> items, int limit) {
        return items.stream()
                .filter(w -> w.length() > limit)
                .findFirst()
                .map(w -> w.substring(0, 1))
                .map(String::toUpperCase)
                .orElse("-");
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        System.out.println(initialOf(words, limit));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit)[0].upper() if _f28p(ws, limit) else "-",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["`findFirst()` turns the pipeline into an `Optional<String>`.",
               "Two `map` calls chain fine - or combine them into one lambda.",
               "`.orElse(\"-\")` at the end decides the absent case.",
               "`limit` is a parameter, so capturing it in the lambda is legal - module "
               "25.",
               "No `if`, no `get()`, one expression."]),
    ])


# --- Family D - the stream terminals -----------------------------------------

_P28_D = _jfam(
    "p28-terminals", "The terminals that return one",
    "Everything modules 26 and 27 had to defer, and the single reason why.",
    """
| Terminal | Returns |
|---|---|
| `findFirst()` | `Optional<T>` |
| `max(cmp)` / `min(cmp)` | `Optional<T>` |
| `reduce(op)` with no identity | `Optional<T>` |
| `average()` on an `IntStream` | `OptionalDouble` |
| `max()` on an `IntStream` | `OptionalInt` |

One reason covers all of them: **an empty stream has no answer.** That is why
module 27 always gave `reduce` an identity, and why it used
`summaryStatistics()` rather than `average()`.

`OptionalInt` and `OptionalDouble` avoid boxing but have no `map` or `filter`.
Call `boxed()` first if you need to chain.
""",
    [
        _p28s("j28-pd-findfirst", "The first match", "Intro",
              "Print the first word longer than three characters, or `none`, then the "
              "list size - with a pipeline, not a loop.",
              _RD_W28P
              + "        System.out.println(words.stream()\n"
                "                .filter(w -> w.length() > 3)\n"
                "                .findFirst()\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl(_f28p(ws) or "none", len(ws))) for ws in _WS28P],
              ["`findFirst()` is a short-circuiting terminal returning an Optional.",
               "`.findFirst().orElse(\"none\")`",
               "This replaces the whole hand-written search helper.",
               "For a yes/no answer, `anyMatch` would be the right tool."]),

        _p28s("j28-pd-max", "The longest word", "Easy",
              "Print the longest word, or `none`, then the list size.",
              _RD_W28P
              + "        System.out.println(words.stream()\n"
                "                .max(Comparator.comparing(String::length))\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl(max(ws, key=len), len(ws))) for ws in _WS28P],
              ["`max` takes a `Comparator` and returns an `Optional<String>`.",
               "`Comparator.comparing(String::length)` - module 25.",
               "Every list here has a unique longest word.",
               "Module 27 had to fold this by hand with a sentinel value."]),

        _p28s("j28-pd-min", "The alphabetically first", "Easy",
              "Print the alphabetically first word, or `none`, then the list size.",
              _RD_W28P
              + "        System.out.println(words.stream()\n"
                "                .min(Comparator.naturalOrder())\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl(min(ws), len(ws))) for ws in _WS28P],
              ["`Comparator.naturalOrder()` is the built-in `Comparable` ordering.",
               "`min` returns an `Optional<String>` for the same reason `max` does.",
               "All the words are distinct, so there is no tie.",
               "`.orElse(\"none\")` handles the empty stream that cannot occur here."]),

        _p28s("j28-pd-reduce", "`reduce` without an identity", "Medium",
              "Sum the numbers with the one-argument `reduce` - the form module 27 "
              "deferred - falling back to zero. Then print the count.",
              _RD_N28P
              + "        System.out.println(nums.stream().reduce((a, b) -> a + b).orElse(0));\n"
                "        System.out.println(nums.size());",
              [_n28p(xs, _nl(sum(xs), len(xs))) for xs in _NS28P],
              ["With no identity there is nothing to return for an empty stream.",
               "So the result is an `Optional<Integer>`.",
               "`.orElse(0)` supplies what the identity used to.",
               "`reduce(0, (a, b) -> a + b)` says the same thing sooner - prefer it when "
               "a neutral identity exists."]),

        _p28s("j28-pd-primitive", "The primitive Optionals", "Hard",
              "Print the average of the numbers (default `0.0`), the largest (default "
              "`0`), and the count - using the `IntStream` terminals module 27 avoided.",
              _RD_N28P
              + "        OptionalDouble average = nums.stream().mapToInt(Integer::intValue).average();\n"
                "        System.out.println(average.orElse(0.0));\n"
                "        OptionalInt largest = nums.stream().mapToInt(Integer::intValue).max();\n"
                "        System.out.println(largest.orElse(0));\n"
                "        System.out.println(nums.size());",
              [_n28p(xs, _nl(str(float(sum(xs) / len(xs))), max(xs), len(xs)))
               for xs in _NS28P],
              ["`average()` returns an `OptionalDouble`, not an `Optional<Double>`.",
               "`max()` on an `IntStream` returns an `OptionalInt`.",
               "Their `orElse` takes a primitive: `0.0` and `0`.",
               "Neither has `map` or `filter` - `boxed()` first if you need to chain.",
               "Module 27 got these from `summaryStatistics()` instead."]),
    ])


# --- Family E - design -------------------------------------------------------

_P28_E = _jfam(
    "p28-design", "Where not to use it",
    "The half of the topic most people skip - and the half interviews ask about.",
    """
`Optional` is for **return types**, where a method may genuinely have no answer.

* **Not a field** - an object per instance, not serialisable, and the field
  itself can still be null.
* **Not a parameter** - it forces every caller to wrap. Use an overload.
* **Not for collections** - an empty `List` already means "nothing here", and two
  ways to say nothing is one too many.
* **Not `get()`** - it throws `NoSuchElementException`, which is the
  `NullPointerException` you were avoiding under a new name. Every `get()` is an
  unanswered question; `orElse`, `orElseGet`, `orElseThrow` and `ifPresent` all
  make you answer it.

The test to apply: *could this be one value that legitimately does not exist?*
If yes, Optional. If it is a collection, a field, or a parameter, no.
""",
    [
        _p28m("j28-pe-collection", "allLongerThan", "Easy",
              "Write `allLongerThan`, returning every word longer than a limit. Return a "
              "plain `List<String>` - never an `Optional<List<String>>`, because an "
              "empty list already means nothing matched.",
              """
    static List<String> allLongerThan(List<String> items, int limit) {
        List<String> out = new ArrayList<>();
        for (String item : items) {
            if (item.length() > limit) {
                out.add(item);
            }
        }
        return out;
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        List<String> matches = allLongerThan(words, limit);\n"
                "        System.out.println(matches);\n"
                "        System.out.println(matches.size());",
              [_wl28p(ws, limit, _nl(_jl28p([w for w in ws if len(w) > limit]),
                                     sum(1 for w in ws if len(w) > limit)))
               for (ws, limit) in _WL28P],
              ["The return type is `List<String>` with no Optional anywhere.",
               "Return the list even when empty - that is the whole point.",
               "An `Optional<List<String>>` would give callers two ways to spell "
               "'nothing'.",
               "The empty result prints as `[]` and has size 0."]),

        _p28m("j28-pe-param", "shout", "Easy",
              "Write `shout`, taking a plain `String` - not an Optional - and returning "
              "it capitalised. `main` applies it through `map`, so it only runs when "
              "there is a value.",
              """
    static String shout(String value) {
        return value.toUpperCase();
    }
""",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        System.out.println(words.stream()\n"
                "                .filter(w -> w.length() > limit)\n"
                "                .findFirst()\n"
                "                .map(Main::shout)\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit).upper() if _f28p(ws, limit) else "none",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["`shout` should know nothing about Optionals - it capitalises a String.",
               "`map` is what applies it only when a value is present.",
               "An `Optional<String>` parameter would force every caller to wrap.",
               "The method does the work; the caller decides about absence."]),

        _p28b("j28-pe-noget", "Without `get`", "Medium",
              "`firstLongerThan` is written. Print the found word or `none`, then "
              "whether one was found, then the size - without calling `get()` and "
              "without an `if`.",
              "\n" + _FIND28P + "\n",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        Optional<String> found = firstLongerThan(words, limit);\n"
                "        System.out.println(found.orElse(\"none\"));\n"
                "        System.out.println(found.isPresent());\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit, _nl(_f28p(ws, limit) or "none",
                                     _jbool(_f28p(ws, limit) is not None), len(ws)))
               for (ws, limit) in _WL28P],
              ["`orElse` answers the absence question directly.",
               "`isPresent()` is fine as a REPORT; it is only a smell when it guards a "
               "`get()`.",
               "`if (found.isPresent()) { found.get(); }` would be the shape to avoid.",
               "Three printed lines."]),

        _p28m("j28-pe-summary", "summarise", "Medium",
              "Write `summarise`, returning the longest word in capitals, or `EMPTY` for "
              "an empty list - one chain, no `if`, no `get()`.",
              """
    static String summarise(List<String> items) {
        return items.stream()
                .max(Comparator.comparing(String::length))
                .map(String::toUpperCase)
                .orElse("EMPTY");
    }
""",
              _RD_W28P
              + "        System.out.println(summarise(words));\n"
                "        System.out.println(summarise(new ArrayList<>()));\n"
                "        System.out.println(words.size());",
              [_w28p(ws, _nl(max(ws, key=len).upper(), "EMPTY", len(ws)))
               for ws in _WS28P],
              ["`max` returns an Optional, which is exactly what makes the empty case "
               "expressible.",
               "`.map(String::toUpperCase)` runs only when there is a value.",
               "`.orElse(\"EMPTY\")` handles the empty list.",
               "The second call passes a genuinely empty list, proving the branch "
               "works.",
               "No `if` anywhere in the method."]),

        _p28s("j28-pe-final", "The whole of Part 8, in one chain", "Hard",
              "Find the first word longer than the limit, keep it only if it is longer "
              "than four characters, capitalise it, and print it or `none`. Then print "
              "how many words there were.",
              _RD_W28P
              + "        int limit = sc.nextInt();\n"
                "        System.out.println(words.stream()\n"
                "                .filter(w -> w.length() > limit)\n"
                "                .findFirst()\n"
                "                .filter(w -> w.length() > 4)\n"
                "                .map(String::toUpperCase)\n"
                "                .orElse(\"none\"));\n"
                "        System.out.println(words.size());",
              [_wl28p(ws, limit,
                      _nl(_f28p(ws, limit).upper()
                          if (_f28p(ws, limit) and len(_f28p(ws, limit)) > 4)
                          else "none",
                          len(ws)))
               for (ws, limit) in _WL28P],
              ["The first `filter` is a STREAM filter; `findFirst` then gives an "
               "Optional.",
               "The second `filter` is an OPTIONAL filter - same name, same idea, "
               "different container.",
               "`map` and `flatMap` mean the same thing in both, which is not a "
               "coincidence.",
               "Only `alpha` is longer than four characters, so most inputs print "
               "`none`.",
               "`limit` is captured and never reassigned - effectively final."]),
    ])


_PRACTICE[28] = [_P28_A, _P28_B, _P28_C, _P28_D, _P28_E]
