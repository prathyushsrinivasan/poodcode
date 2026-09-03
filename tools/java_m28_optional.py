# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 28 - Optional.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# CLOSES PART 8, AND THE TRACK. `Optional` becomes legal here, which is why
# modules 26 and 27 kept saying "that returns an Optional - module 28": the
# one-argument `reduce`, `findFirst`, `max`, `min` and `average` were all
# deferred for the same single reason, and this module is that reason.
#
# TEACHING SPINE: an Optional is a container of nought or one. Everything else
# follows - `map`/`filter` work because it is a container, `flatMap` exists
# because a function may return another one, and `orElse` exists because
# eventually somebody has to decide what absence means.
#
# THE POINT OF THE MODULE IS NOT THE API. It is that `get()` reintroduces
# exactly the failure Optional was created to remove, only with a different
# exception name. Lesson 28.5 is the design lesson - where NOT to use it - and
# it is the one that separates people who have read the API from people who have
# used it.
#
# JUDGING NOTES:
#   * `Optional.toString()` is "Optional[x]" / "Optional.empty", which is stable.
#   * Exception NAMES only, never messages (they move between JDK versions).
#   * `orElseThrow()` with no argument is Java 10+, and `Optional.isEmpty()` is
#     Java 11+, so neither appears in a program here - the Supplier form of
#     `orElseThrow` and `!isPresent()` work everywhere Part 8 does.
#   * `max`/`min` data is chosen so the extreme is UNIQUE. `BinaryOperator.maxBy`
#     keeps the earlier element on a tie, but leaning on that in a test would be
#     leaning on an implementation detail.
# ---------------------------------------------------------------------------

_M28 = []

_IMPORTS28 = ("import java.util.*;\n"
              "import java.util.function.*;\n"
              "import java.util.stream.*;\n")


def _j28s(body):
    """Scanner-opening main, no helpers."""
    return _jscan(body, imports=_IMPORTS28)


def _j28(helpers, body):
    """Static helper methods above a Scanner-opening main."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS28,
    )


_RD_W28 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N28 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

# Every list has a UNIQUE longest word, so `max(comparing(String::length))` has
# one right answer that does not depend on tie-breaking. Two of the five have no
# word over three characters at all, so the empty case is exercised properly.
_W28 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
        ["alpha", "beta", "gam", "d"])

# Sums divide evenly, so every printed average is short and exact.
_N28 = ([3, 1, 2], [5], [-4, -8, -3], [10, 10, 4], [7, 2, 9, 4])

# (words, limit) - the limit is 3 throughout so "longer than the limit" is empty
# for two of the five lists.
_WL28 = tuple((ws, 3) for ws in _W28)

# The reusable search helper, present in most of the module's programs.
_FIND28 = ("    static Optional<String> firstLongerThan(List<String> items, int limit) {\n"
           "        for (String item : items) {\n"
           "            if (item.length() > limit) {\n"
           "                return Optional.of(item);\n"
           "            }\n"
           "        }\n"
           "        return Optional.empty();\n"
           "    }")


def _w28(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n28(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wl28(ws, limit, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(limit)]), out)


def _jl28(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


def _found28(ws, limit=3):
    """The first word longer than `limit`, or None."""
    for w in ws:
        if len(w) > limit:
            return w
    return None


def _jopt28(value):
    """Exactly what `Optional.toString()` prints."""
    return "Optional.empty" if value is None else f"Optional[{value}]"


# --- 28.1 What an Optional is ------------------------------------------------

_M28.append(_jlesson(
    "m28-why", "The value that might not be there",
    "A container of nought or one - and a return type that says so.",
    """
Tony Hoare called the null reference his billion-dollar mistake. The problem is
not that a value can be absent - it is that **the type never says so**:

```java
static String firstLongerThan(List<String> items, int limit) { ... }

String found = firstLongerThan(words, 3);
System.out.println(found.length());     // NullPointerException, some day
```

Nothing in that signature warns you. The caller has to *know*, from
documentation or from being bitten.

**`Optional<T>` is a container holding either one value or none**, and using it
as a return type moves the warning into the type:

```java
static Optional<String> firstLongerThan(List<String> items, int limit) {
    for (String item : items) {
        if (item.length() > limit) {
            return Optional.of(item);
        }
    }
    return Optional.empty();
}
```

Now the compiler will not let the caller forget. That is the entire value
proposition - not fewer crashes by magic, but a signature that cannot lie.

**Three ways to make one:**

| Call | Meaning |
|---|---|
| `Optional.of(value)` | definitely present - **throws NPE if you pass null** |
| `Optional.ofNullable(value)` | present if non-null, empty if null |
| `Optional.empty()` | definitely absent |

`of` throwing on null looks unhelpful and is deliberate: it is an assertion. Use
`of` when you know there is a value, `ofNullable` when you are wrapping
something that might be null - typically a result from older code.

**Asking whether it is there** is `isPresent()`. Printing an Optional shows
`Optional[ada]` or `Optional.empty`, which is useful in a lesson and not
something to do in real output.

There is also a `get()`. Do not reach for it - lesson 28.5 explains why it
recreates the exact problem this module exists to solve.
""",
    warmup=[
        _jq("`Optional.of(null)` does what?",
            ["Throws NullPointerException", "Returns Optional.empty",
             "Returns Optional[null]", "Does not compile"],
            0,
            "It is an assertion that a value is there. Use `ofNullable` when it may "
            "not be."),
        _jq("The main benefit of returning `Optional<String>` is…",
            ["the signature tells the caller absence is possible",
             "it is faster", "it prevents all NullPointerExceptions",
             "it avoids boxing"],
            0,
            "A `String` return type cannot say 'or nothing'; this one can."),
    ],
    exercises=[
        _je("j28-why-ofnullable", "Wrapping something that might be null",
            "The loop leaves `found` either set or null. Wrap it in an `Optional` "
            "without assuming which, then print whether it is present and the container "
            "itself. Replace `____` with the wrapping.",
            _j28s(_RD_W28
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
                    "        System.out.println(words.size());"),
            "        Optional<String> maybe = Optional.ofNullable(found);",
            [_w28(ws, _nl(_jbool(_found28(ws) is not None),
                          _jopt28(_found28(ws)), len(ws)))
             for ws in _W28],
            hints=["`found` may legitimately be null here, so `Optional.of` would "
                   "throw.",
                   "`Optional.ofNullable(found)` turns null into `Optional.empty()`.",
                   "Printing an Optional shows `Optional[value]` or `Optional.empty`.",
                   "Two of the five inputs have no word longer than three characters."],
            difficulty="Easy"),

        _jfix("j28-why-ofnull", "The assertion that fired",
              "This wraps a possibly-null value with `Optional.of`, which throws "
              "`NullPointerException` the moment nothing was found - the very failure "
              "Optional exists to prevent. Use the factory that accepts null instead.",
              _j28s(_RD_W28
                    + "        String found = null;\n"
                      "        for (String w : words) {\n"
                      "            if (w.length() > 3) {\n"
                      "                found = w;\n"
                      "                break;\n"
                      "            }\n"
                      "        }\n"
                      "        Optional<String> maybe = Optional.of(found);\n"
                      "        System.out.println(maybe.isPresent());\n"
                      "        System.out.println(maybe);"),
              _j28s(_RD_W28
                    + "        String found = null;\n"
                      "        for (String w : words) {\n"
                      "            if (w.length() > 3) {\n"
                      "                found = w;\n"
                      "                break;\n"
                      "            }\n"
                      "        }\n"
                      "        Optional<String> maybe = Optional.ofNullable(found);\n"
                      "        System.out.println(maybe.isPresent());\n"
                      "        System.out.println(maybe);"),
              [_w28(ws, _nl(_jbool(_found28(ws) is not None), _jopt28(_found28(ws))))
               for ws in _W28],
              hints=["`Optional.of` is an assertion: it demands a non-null value.",
                     "It works fine for the inputs that DO contain a long word, and "
                     "throws for the ones that do not.",
                     "One word changes: `ofNullable`.",
                     "`Optional.ofNullable(found)` maps null to `Optional.empty()`.",
                     "Keep `of` for values you know are there - it documents that "
                     "knowledge, and fails loudly when you are wrong."],
              difficulty="Medium"),

        _je("j28-why-of", "When you know there is one",
            "The list is never empty here, so its first word certainly exists. Build an "
            "`Optional` that asserts as much. Replace `____` with it.",
            _j28s(_RD_W28
                  + "        Optional<String> firstWord = Optional.of(words.get(0));\n"
                    "        System.out.println(firstWord.isPresent());\n"
                    "        System.out.println(firstWord);\n"
                    "        System.out.println(words.size());"),
            "        Optional<String> firstWord = Optional.of(words.get(0));",
            [_w28(ws, _nl("true", _jopt28(ws[0]), len(ws))) for ws in _W28],
            hints=["`ofNullable` would also work, and would say something weaker.",
                   "`Optional.of(words.get(0))` states that the value is definitely "
                   "there.",
                   "If that assumption were ever wrong, this line would throw - which is "
                   "the point of choosing it.",
                   "`isPresent()` is therefore always `true` here."],
            difficulty="Easy"),

        _jch("j28-why-search", "A signature that cannot lie", "Medium",
             "Write `firstLongerThan`, returning the first word longer than a limit - or "
             "an empty `Optional` when there is none. `main` prints whether it found one "
             "and the container itself.",
             _j28(_FIND28,
                  _RD_W28
                  + "        int limit = sc.nextInt();\n"
                    "        Optional<String> found = firstLongerThan(words, limit);\n"
                    "        System.out.println(found.isPresent());\n"
                    "        System.out.println(found);\n"
                    "        System.out.println(words.size());"),
             _FIND28,
             [_wl28(ws, limit, _nl(_jbool(_found28(ws, limit) is not None),
                                   _jopt28(_found28(ws, limit)), len(ws)))
              for (ws, limit) in _WL28],
             hints=["The return type is `Optional<String>` - that is the whole point of "
                    "the exercise.",
                    "Return `Optional.of(item)` from inside the loop as soon as one "
                    "matches.",
                    "`return Optional.empty();` after the loop, for the case where "
                    "nothing did.",
                    "`of` is right inside the loop because `item` is certainly not "
                    "null.",
                    "A `String` return type would have had to use null, and the caller "
                    "would have had no warning."]),
    ],
    quiz=[
        _jq("An Optional is best described as…",
            ["a container of nought or one value", "a null wrapper",
             "a collection", "an annotation"],
            0,
            "Which is why it has `map` and `filter` like any other container."),
        _jq("Use `Optional.of` rather than `ofNullable` when…",
            ["you know the value is there and want to fail loudly if not",
             "always", "the value may be null", "never"],
            0,
            "It is an assertion, and assertions are useful."),
    ],
))


# --- 28.2 Getting the value out ----------------------------------------------

_M28.append(_jlesson(
    "m28-unwrap", "Getting the value out",
    "`orElse`, `orElseGet`, `orElseThrow`, `ifPresent` - and the trap in the middle.",
    """
Eventually somebody has to decide what absence means. Four ways, in rough order
of how often you want them:

```java
found.orElse("none");                                  // a default value
found.orElseGet(Main::expensiveDefault);               // a default, computed lazily
found.orElseThrow(() -> new IllegalStateException(""));// absence is a bug - say so
found.ifPresent(w -> System.out.println(w));           // do something, or nothing
```

**`orElse` versus `orElseGet` is the one people get wrong.** `orElse` takes a
*value*, so its argument is evaluated **every time** - present or not:

```java
found.orElse(expensive());      // expensive() ALWAYS runs
found.orElseGet(Main::expensive);   // runs only when found is empty
```

If the default is a constant, `orElse` is clearer. If computing it costs
anything - a database call, a new object, a log line - use `orElseGet`, or you
have added work to the *happy* path.

**`ifPresent`** takes a `Consumer` and runs it only when there is a value. It is
the replacement for `if (x != null) { ... }`, and it returns nothing, so it is
the end of the line.

**`orElseThrow(Supplier)`** is what to use when absence really is an error. It
says so at the point it matters, with an exception you chose, instead of a
`NullPointerException` three frames later.

**And the trap: `get()`.** It returns the value, or throws
`NoSuchElementException` if there is none. An unchecked `get()` is exactly the
`NullPointerException` you started with, wearing a different name - all of the
risk, none of the warning, and now with extra ceremony. Lesson 28.5 comes back
to this; for now, treat every `get()` as a bug.
""",
    warmup=[
        _jq("`found.orElse(expensive())` when `found` IS present…",
            ["still calls expensive() - the argument is evaluated first",
             "skips expensive()", "throws", "returns the default"],
            0,
            "It is an argument, not a lambda. Use `orElseGet` when it costs anything."),
        _jq("`ifPresent` takes…",
            ["a Consumer, run only when a value is there", "a Supplier",
             "a default value", "a Predicate"],
            0,
            "It is the replacement for a null check with a body."),
    ],
    exercises=[
        _je("j28-un-orelse", "A default value",
            "Print the first word longer than the limit, or the text `none` when there "
            "is none. Replace `____` with that line.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        System.out.println(found.orElse(\"none\"));\n"
                   "        System.out.println(words.size());"),
            "        System.out.println(found.orElse(\"none\"));",
            [_wl28(ws, limit, _nl(_found28(ws, limit) or "none", len(ws)))
             for (ws, limit) in _WL28],
            hints=["`orElse` takes the value to use when the Optional is empty.",
                   "`found.orElse(\"none\")`",
                   "The default is a constant here, so `orElse` is the right choice - "
                   "nothing is computed.",
                   "Two of the five inputs print `none`."],
            difficulty="Easy"),

        _je("j28-un-ifpresent", "Doing something, or nothing",
            "Print the found word in capitals if there is one, and nothing at all if "
            "there is not - then print `done` either way. Replace `____` with the "
            "conditional action.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        found.ifPresent(w -> System.out.println(w.toUpperCase()));\n"
                   "        System.out.println(\"done\");"),
            "        found.ifPresent(w -> System.out.println(w.toUpperCase()));",
            [_wl28(ws, limit,
                   _nl(*(([_found28(ws, limit).upper()] if _found28(ws, limit) else [])
                         + ["done"])))
             for (ws, limit) in _WL28],
            hints=["`ifPresent` takes a `Consumer<String>` - module 25's shape.",
                   "`found.ifPresent(w -> System.out.println(w.toUpperCase()));`",
                   "It returns nothing, so it cannot be chained onto.",
                   "When the Optional is empty the lambda never runs, so only `done` "
                   "prints."],
            difficulty="Easy"),

        _je("j28-un-orelsethrow", "When absence is an error",
            "Here a missing word is a real failure. Unwrap it with an exception of your "
            "own, catch it, and print the exception's simple name. Replace `____` with "
            "the unwrapping.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        try {\n"
                   "            System.out.println(found.orElseThrow(() -> new IllegalStateException(\"missing\")));\n"
                   "        } catch (IllegalStateException e) {\n"
                   "            System.out.println(e.getClass().getSimpleName());\n"
                   "        }\n"
                   "        System.out.println(words.size());"),
            "found.orElseThrow(() -> new IllegalStateException(\"missing\"))",
            [_wl28(ws, limit,
                   _nl(_found28(ws, limit) or "IllegalStateException", len(ws)))
             for (ws, limit) in _WL28],
            hints=["`orElseThrow` takes a `Supplier` that builds the exception - it is "
                   "only called when the Optional is empty.",
                   "`found.orElseThrow(() -> new IllegalStateException(\"missing\"))`",
                   "The lambda takes no arguments, so its parameter list is `()`.",
                   "This is far better than `get()`: the exception says what was "
                   "expected and why.",
                   "The name is printed rather than the message, which varies between "
                   "JDK versions."],
            difficulty="Medium"),

        _jch("j28-un-lazy", "`orElse` versus `orElseGet`", "Hard",
             "`fallback()` announces itself when it runs. Print the found word (or the "
             "fallback) twice - first with `orElse`, then with `orElseGet` and a method "
             "reference - and watch how many times `computing` appears.",
             _j28("    static String fallback() {\n"
                  "        System.out.println(\"computing\");\n"
                  "        return \"none\";\n"
                  "    }\n"
                  "\n"
                  + _FIND28,
                  _RD_W28
                  + "        int limit = sc.nextInt();\n"
                    "        Optional<String> found = firstLongerThan(words, limit);\n"
                    "        System.out.println(found.orElse(fallback()));\n"
                    "        System.out.println(found.orElseGet(Main::fallback));"),
             "        System.out.println(found.orElse(fallback()));\n"
             "        System.out.println(found.orElseGet(Main::fallback));",
             [_wl28(ws, limit,
                    _nl(*(["computing", _found28(ws, limit), _found28(ws, limit)]
                          if _found28(ws, limit)
                          else ["computing", "none", "computing", "none"])))
              for (ws, limit) in _WL28],
             hints=["`orElse` takes a VALUE, so `fallback()` is called before `orElse` "
                    "even runs - every single time.",
                    "`orElseGet` takes a `Supplier`, so `Main::fallback` is only invoked "
                    "when the Optional is empty.",
                    "`Main::fallback` is a static method reference from module 25.",
                    "When a word IS found: `computing` prints once (from the eager "
                    "argument), then the word twice.",
                    "When none is found: `computing` prints twice, once for each call.",
                    "That difference is the whole reason `orElseGet` exists."]),
    ],
    quiz=[
        _jq("`orElseGet` is preferable when…",
            ["computing the default costs something",
             "always", "the Optional is present", "never"],
            0,
            "`orElse`'s argument is evaluated even on the happy path."),
        _jq("`get()` on an empty Optional…",
            ["throws NoSuchElementException - the old bug with a new name",
             "returns null", "returns empty", "does not compile"],
            0,
            "Which is why an unguarded `get()` defeats the entire point."),
    ],
))


# --- 28.3 Chaining -----------------------------------------------------------

_M28.append(_jlesson(
    "m28-chain", "`map`, `filter`, `flatMap`",
    "It is a container, so it composes - and the nested `if` disappears.",
    """
Because an Optional is a container, it has the operations every container has -
and they let you describe the whole computation before deciding what absence
means:

```java
String shout = found.map(String::toUpperCase).orElse("NONE");
```

**`map`** applies a function *if there is a value*, and gives back an Optional of
the result. If it was empty, it stays empty and the function never runs. That
one sentence removes a great many null checks:

```java
// before
String shout = "NONE";
if (found != null) {
    shout = found.toUpperCase();
}
// after
String shout = found.map(String::toUpperCase).orElse("NONE");
```

**`filter`** takes a `Predicate` and empties the Optional when the value fails
it - turning "present but unsuitable" into plain "absent", which is usually what
you wanted:

```java
found.filter(w -> w.length() > 4).orElse("none");
```

They chain, and the chain reads as one sentence:

```java
found.filter(w -> w.length() > 4)
     .map(String::toUpperCase)
     .orElse("none");
```

**`flatMap`** is for when the function *itself* returns an Optional. Using `map`
there gives you an `Optional<Optional<String>>`, which nobody wants:

```java
found.map(Main::firstLetter);       // Optional<Optional<String>>
found.flatMap(Main::firstLetter);   // Optional<String>
```

The rule is the same one as in streams: **`map` when your function returns a
plain value, `flatMap` when it returns another container.** One level of nesting
is removed for you.
""",
    warmup=[
        _jq("`empty.map(String::toUpperCase)` runs the function…",
            ["never - it stays empty", "once", "and throws", "and returns null"],
            0,
            "`map` only applies to a value that is there."),
        _jq("Your function returns an `Optional`. You should use…",
            ["flatMap", "map", "filter", "ifPresent"],
            0,
            "`map` would nest one Optional inside another."),
    ],
    exercises=[
        _je("j28-ch-map", "Transforming what might be there",
            "Print the found word in capitals, or `NONE` when there is none - without "
            "an `if` anywhere. Replace `____` with the chain.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        System.out.println(found.map(String::toUpperCase).orElse(\"NONE\"));\n"
                   "        System.out.println(words.size());"),
            "        System.out.println(found.map(String::toUpperCase).orElse(\"NONE\"));",
            [_wl28(ws, limit,
                   _nl(_found28(ws, limit).upper() if _found28(ws, limit) else "NONE",
                       len(ws)))
             for (ws, limit) in _WL28],
            hints=["`map` takes a `Function` and applies it only when a value is "
                   "present.",
                   "`String::toUpperCase` is module 25's unbound method reference.",
                   "`found.map(String::toUpperCase).orElse(\"NONE\")`",
                   "When the Optional is empty, `toUpperCase` never runs - there is "
                   "nothing to run it on.",
                   "The default is only decided at the very end of the chain."],
            difficulty="Easy"),

        _je("j28-ch-filter", "Present, but not good enough",
            "Print the found word only if it is longer than four characters, and `none` "
            "otherwise - treating 'present but too short' as absent. Replace `____` with "
            "the chain.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        System.out.println(found.filter(w -> w.length() > 4).orElse(\"none\"));\n"
                   "        System.out.println(words.size());"),
            "        System.out.println(found.filter(w -> w.length() > 4).orElse(\"none\"));",
            [_wl28(ws, limit,
                   _nl(_found28(ws, limit)
                       if (_found28(ws, limit) and len(_found28(ws, limit)) > 4)
                       else "none",
                       len(ws)))
             for (ws, limit) in _WL28],
            hints=["`filter` takes a `Predicate` and empties the Optional when it "
                   "fails.",
                   "`found.filter(w -> w.length() > 4)`",
                   "An already-empty Optional stays empty; the predicate never runs.",
                   "`solo` and `pear` are exactly four characters, so they do NOT "
                   "survive a strict `> 4`.",
                   "Only `alpha` is long enough."],
            difficulty="Medium"),

        _je("j28-ch-chain", "The whole sentence",
            "Chain both: keep the found word only if it is longer than three "
            "characters, capitalise it, and fall back to `none`. Replace `____` with the "
            "two chained operations.",
            _j28(_FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        System.out.println(found\n"
                   "                .filter(w -> w.length() > 3)\n"
                   "                .map(String::toUpperCase)\n"
                   "                .orElse(\"none\"));\n"
                   "        System.out.println(words.size());"),
            "                .filter(w -> w.length() > 3)\n"
            "                .map(String::toUpperCase)",
            [_wl28(ws, limit,
                   _nl(_found28(ws, limit).upper()
                       if (_found28(ws, limit) and len(_found28(ws, limit)) > 3)
                       else "none",
                       len(ws)))
             for (ws, limit) in _WL28],
            hints=["Filter first, then map - the same habit as a stream pipeline.",
                   "Each operation returns another `Optional`, which is what lets them "
                   "chain.",
                   "`.filter(w -> w.length() > 3)` then `.map(String::toUpperCase)`.",
                   "`orElse` at the end is the only place absence is finally decided.",
                   "Nothing here needs an `if` or a null check."],
            difficulty="Medium"),

        _jch("j28-ch-flatmap", "When the function returns one too", "Hard",
             "`firstLetter` returns an `Optional<String>` of its own. Use it on the found "
             "word without ending up with an Optional inside an Optional, then fall back "
             "to `none`.",
             _j28("    static Optional<String> firstLetter(String value) {\n"
                  "        if (value.length() == 0) {\n"
                  "            return Optional.empty();\n"
                  "        }\n"
                  "        return Optional.of(value.substring(0, 1));\n"
                  "    }\n"
                  "\n"
                  + _FIND28,
                  _RD_W28
                  + "        int limit = sc.nextInt();\n"
                    "        Optional<String> found = firstLongerThan(words, limit);\n"
                    "        System.out.println(found.flatMap(Main::firstLetter).orElse(\"none\"));\n"
                    "        System.out.println(words.size());"),
             "        System.out.println(found.flatMap(Main::firstLetter).orElse(\"none\"));",
             [_wl28(ws, limit,
                    _nl(_found28(ws, limit)[0] if _found28(ws, limit) else "none",
                        len(ws)))
              for (ws, limit) in _WL28],
             hints=["`map(Main::firstLetter)` would give an "
                    "`Optional<Optional<String>>`, which `orElse(\"none\")` would not "
                    "even compile against.",
                    "`flatMap` unwraps the inner container for you.",
                    "`found.flatMap(Main::firstLetter).orElse(\"none\")`",
                    "`Main::firstLetter` is a static method reference.",
                    "The rule is the same as in streams: `flatMap` when the function "
                    "returns a container."]),
    ],
    quiz=[
        _jq("`found.map(String::toUpperCase).orElse(\"NONE\")` replaces…",
            ["a null check with a body and a default",
             "a try/catch", "a loop", "a cast"],
            0,
            "The transformation is described first, absence decided last."),
        _jq("`filter` on an Optional turns…",
            ["'present but unsuitable' into 'absent'",
             "absent into present", "an Optional into a boolean", "nothing"],
            0,
            "Which is usually exactly the question being asked."),
    ],
))


# --- 28.4 The stream terminals that return one -------------------------------

_M28.append(_jlesson(
    "m28-stream", "The terminals modules 26 and 27 could not use",
    "Every deferred operation was deferred for the same reason.",
    """
Modules 26 and 27 kept stopping at the same wall. Here is all of it, resolved:

| Terminal | Returns | Because |
|---|---|---|
| `findFirst()` | `Optional<T>` | the stream may be empty |
| `max(cmp)` / `min(cmp)` | `Optional<T>` | no elements, no maximum |
| `reduce(op)` (no identity) | `Optional<T>` | nothing to start from |
| `average()` on an `IntStream` | `OptionalDouble` | no elements, no average |

Every one is the same sentence: **an empty stream has no answer, and the return
type has to say so.** That is why module 27 always supplied an identity to
`reduce`, and why it reached for `summaryStatistics()` rather than `average()` -
neither had a way to talk about absence yet.

```java
words.stream().filter(w -> w.length() > 3).findFirst().orElse("none");
words.stream().max(Comparator.comparing(String::length)).orElse("none");
nums.stream().reduce((a, b) -> a + b).orElse(0);
nums.stream().mapToInt(Integer::intValue).average().orElse(0.0);
```

**`OptionalInt`, `OptionalLong` and `OptionalDouble`** are the primitive
versions, and exist for the same reason `IntStream` does - no boxing. They have
`orElse` and `isPresent` but not `map` or `filter`, so they are less useful; when
you want to chain, `boxed()` first.

**`findFirst` versus `findAny`.** On a sequential stream they do the same thing.
On a parallel one, `findAny` may return any matching element and is therefore
faster, while `findFirst` must respect encounter order. Use `findFirst` unless
you have measured a reason not to - which, for this course, you have not.

And now the module-26 comparison completes: `anyMatch(p)` answers *is there
one?*; `filter(p).findFirst()` answers *which one?* Use the first when you only
need the boolean.
""",
    warmup=[
        _jq("`stream.max(comparator)` returns an Optional because…",
            ["an empty stream has no maximum", "the comparator may fail",
             "of erasure", "it may be parallel"],
            0,
            "The same reason `reduce` without an identity does."),
        _jq("`average()` on an `IntStream` returns…",
            ["OptionalDouble", "double", "Optional<Double>", "Double"],
            0,
            "The primitive Optional - no boxing, and no `map`."),
    ],
    exercises=[
        _je("j28-st-findfirst", "The first one that matches",
            "Print the first word longer than three characters, or `none` - no "
            "hand-written loop this time. Replace `____` with the terminal that turns "
            "the pipeline into an `Optional`.",
            _j28s(_RD_W28
                  + "        System.out.println(words.stream()\n"
                    "                .filter(w -> w.length() > 3)\n"
                    "                .findFirst()\n"
                    "                .orElse(\"none\"));\n"
                    "        System.out.println(words.size());"),
            "                .findFirst()",
            [_w28(ws, _nl(_found28(ws) or "none", len(ws))) for ws in _W28],
            hints=["The `orElse` on the next line only makes sense if what precedes it "
                   "is an `Optional`.",
                   "`findFirst()` is a short-circuiting terminal returning an "
                   "`Optional<String>`.",
                   "`.findFirst()`",
                   "This replaces the whole `firstLongerThan` helper from lesson 28.1.",
                   "If you only needed a yes/no, `anyMatch` would be the right tool."],
            difficulty="Easy"),

        _je("j28-st-max", "The longest word",
            "Print the longest word, or `none` for a list with none. Replace `____` with "
            "the terminal that finds it.",
            _j28s(_RD_W28
                  + "        System.out.println(words.stream()\n"
                    "                .max(Comparator.comparing(String::length))\n"
                    "                .orElse(\"none\"));\n"
                    "        System.out.println(words.size());"),
            "                .max(Comparator.comparing(String::length))",
            [_w28(ws, _nl(max(ws, key=len), len(ws))) for ws in _W28],
            hints=["`max` takes a `Comparator` and returns an `Optional<String>`.",
                   "`Comparator.comparing(String::length)` from module 25.",
                   "`.max(Comparator.comparing(String::length))`",
                   "Module 27 had to fold this by hand with `reduce` and a sentinel, "
                   "because it could not talk about the empty case.",
                   "Every list here has a unique longest word, so there is no tie to "
                   "worry about."],
            difficulty="Medium"),

        _je("j28-st-reduce", "`reduce` without an identity",
            "Sum the numbers with the ONE-argument `reduce` - the form module 27 had to "
            "defer - falling back to zero. Replace `____` with it.",
            _j28s(_RD_N28
                  + "        System.out.println(nums.stream().reduce((a, b) -> a + b).orElse(0));\n"
                    "        System.out.println(nums.size());"),
            "        System.out.println(nums.stream().reduce((a, b) -> a + b).orElse(0));",
            [_n28(xs, _nl(sum(xs), len(xs))) for xs in _N28],
            hints=["With no identity there is nothing to return for an empty stream, so "
                   "the result is an `Optional<Integer>`.",
                   "`nums.stream().reduce((a, b) -> a + b)`",
                   "`.orElse(0)` supplies the answer the identity used to.",
                   "Module 27's `reduce(0, (a, b) -> a + b)` says the same thing sooner - "
                   "prefer it when a neutral identity exists."],
            difficulty="Medium"),

        _jch("j28-st-primitive", "The primitive Optionals", "Hard",
             "Print the average of the numbers (falling back to `0.0`), then the largest "
             "(falling back to `0`), then how many there are - using the `IntStream` "
             "terminals module 27 had to avoid.",
             _j28s(_RD_N28
                   + "        OptionalDouble average = nums.stream().mapToInt(Integer::intValue).average();\n"
                     "        System.out.println(average.orElse(0.0));\n"
                     "        OptionalInt largest = nums.stream().mapToInt(Integer::intValue).max();\n"
                     "        System.out.println(largest.orElse(0));\n"
                     "        System.out.println(nums.size());"),
             "        OptionalDouble average = nums.stream().mapToInt(Integer::intValue).average();\n"
             "        System.out.println(average.orElse(0.0));\n"
             "        OptionalInt largest = nums.stream().mapToInt(Integer::intValue).max();\n"
             "        System.out.println(largest.orElse(0));\n"
             "        System.out.println(nums.size());",
             [_n28(xs, _nl(str(float(sum(xs) / len(xs))), max(xs), len(xs)))
              for xs in _N28],
             hints=["`average()` returns an `OptionalDouble`, not an "
                    "`Optional<Double>`.",
                    "`max()` on an `IntStream` returns an `OptionalInt`.",
                    "Both have `orElse`, taking a primitive - `0.0` and `0` "
                    "respectively.",
                    "Neither has `map` or `filter`; `boxed()` first if you need to "
                    "chain.",
                    "Module 27 used `summaryStatistics()` to get these without an "
                    "Optional - both are fine, and the summary wins when you want "
                    "several."]),
    ],
    quiz=[
        _jq("Module 27 supplied an identity to `reduce` because…",
            ["the identity-free form returns an Optional, which it could not use yet",
             "it is faster", "identities are required", "of boxing"],
            0,
            "Every deferral in modules 26 and 27 was this one reason."),
        _jq("`findFirst` versus `findAny`…",
            ["identical on a sequential stream; findAny may be faster in parallel",
             "findAny is always faster", "findFirst is deprecated",
             "findAny returns a List"],
            0,
            "Prefer `findFirst` unless you have measured a reason."),
    ],
))


# --- 28.5 Where not to use it ------------------------------------------------

_M28.append(_jlesson(
    "m28-design", "Where *not* to use it",
    "Optional was designed for one job. Most of its bad reputation comes from the others.",
    """
`Optional` was added for **return types**, where a method may genuinely have no
answer. Almost every complaint about it comes from using it somewhere else.

**Not as a field.** It adds an object per instance, it is not serialisable, and
a null field is not solved by wrapping it - `null` can still be the *value of the
Optional field itself*, which is the worst of both worlds. Use a nullable field
and a getter returning an `Optional` if you like.

**Not as a parameter.** It forces every caller to wrap:

```java
void greet(Optional<String> name)       // callers write greet(Optional.of("ada"))
void greet(String name)                 // and an overload greet()
```

The caller already knows whether it has a value; make them say so with an
overload, not with ceremony.

**Not for collections.** An empty list already means "nothing here":

```java
Optional<List<String>> find()   // now there are TWO ways to say empty
List<String> find()             // return an empty list
```

Two representations of nothing is one too many, and every caller has to handle
both.

**And not `get()`.** This is the big one:

```java
if (found.isPresent()) {
    System.out.println(found.get());     // "safe" - and still the old shape
}
System.out.println(found.get());         // NoSuchElementException
```

The first is just a null check with extra syntax; `map`/`orElse` say it better.
The second is the `NullPointerException` you were trying to avoid, renamed. If
you find yourself writing `get()`, the question to ask is what you want to happen
when it is absent - and then use `orElse`, `orElseGet`, `orElseThrow` or
`ifPresent`, all of which make you answer it.

**So the rule that survives:** an `Optional` is a *return type* saying "there may
be no answer, and you must decide what that means". Everywhere else, it is
usually ceremony.
""",
    warmup=[
        _jq("A method that finds no matching records should return…",
            ["an empty List", "Optional<List>", "null", "Optional.empty()"],
            0,
            "An empty collection already means 'nothing here'."),
        _jq("`if (o.isPresent()) { o.get(); }` is…",
            ["a null check with more syntax - `map`/`orElse` say it better",
             "the recommended style", "required", "faster"],
            0,
            "The shape you were trying to leave behind."),
    ],
    exercises=[
        _jfix("j28-de-get", "The `get()` that threw",
              "This calls `get()` without checking, and throws `NoSuchElementException` "
              "for every input where nothing was found - the very failure Optional was "
              "meant to prevent. Replace it with a default of `none`.",
              _j28(_FIND28,
                   _RD_W28
                   + "        int limit = sc.nextInt();\n"
                     "        Optional<String> found = firstLongerThan(words, limit);\n"
                     "        System.out.println(found.get());\n"
                     "        System.out.println(words.size());"),
              _j28(_FIND28,
                   _RD_W28
                   + "        int limit = sc.nextInt();\n"
                     "        Optional<String> found = firstLongerThan(words, limit);\n"
                     "        System.out.println(found.orElse(\"none\"));\n"
                     "        System.out.println(words.size());"),
              [_wl28(ws, limit, _nl(_found28(ws, limit) or "none", len(ws)))
               for (ws, limit) in _WL28],
              hints=["`get()` returns the value or throws - it never asks what you want "
                     "instead.",
                     "It works for the inputs that DO contain a long word, which is "
                     "exactly what makes it dangerous.",
                     "`found.orElse(\"none\")` states the answer for the empty case.",
                     "Wrapping it in `if (found.isPresent())` would also work and would "
                     "still be the old null-check shape.",
                     "Every `get()` is a question you have not answered yet."],
              difficulty="Medium"),

        _jch("j28-de-collection", "An empty list is already empty", "Medium",
             "Write `longerThan`, returning every word longer than a limit. It returns a "
             "plain `List<String>` - **not** an `Optional<List<String>>` - because an "
             "empty list already means 'nothing matched'. `main` prints the list and its "
             "size.",
             _j28("    static List<String> longerThan(List<String> items, int limit) {\n"
                  "        List<String> out = new ArrayList<>();\n"
                  "        for (String item : items) {\n"
                  "            if (item.length() > limit) {\n"
                  "                out.add(item);\n"
                  "            }\n"
                  "        }\n"
                  "        return out;\n"
                  "    }",
                  _RD_W28
                  + "        int limit = sc.nextInt();\n"
                    "        List<String> matches = longerThan(words, limit);\n"
                    "        System.out.println(matches);\n"
                    "        System.out.println(matches.size());"),
             "    static List<String> longerThan(List<String> items, int limit) {\n"
             "        List<String> out = new ArrayList<>();\n"
             "        for (String item : items) {\n"
             "            if (item.length() > limit) {\n"
             "                out.add(item);\n"
             "            }\n"
             "        }\n"
             "        return out;\n"
             "    }",
             [_wl28(ws, limit,
                    _nl(_jl28([w for w in ws if len(w) > limit]),
                        sum(1 for w in ws if len(w) > limit)))
              for (ws, limit) in _WL28],
             hints=["The return type is `List<String>`, with no Optional anywhere.",
                    "Return the list even when it is empty - that is the whole point.",
                    "An `Optional<List<String>>` would give callers two different ways "
                    "to spell 'nothing', and force them to handle both.",
                    "The empty result prints as `[]` and has size 0, which every caller "
                    "already knows how to handle.",
                    "Contrast lesson 28.1's `firstLongerThan`: ONE value may genuinely "
                    "be absent, so there an Optional earns its place."]),

        _je("j28-de-param", "Plain parameters, unwrapped by the caller",
            "`shout` takes a plain `String` - not an `Optional` - because the caller "
            "already knows whether it has one. Call it through the Optional, so it only "
            "runs when there is a value. Replace `____` with that line.",
            _j28("    static String shout(String value) {\n"
                 "        return value.toUpperCase();\n"
                 "    }\n"
                 "\n"
                 + _FIND28,
                 _RD_W28
                 + "        int limit = sc.nextInt();\n"
                   "        Optional<String> found = firstLongerThan(words, limit);\n"
                   "        System.out.println(found.map(Main::shout).orElse(\"none\"));\n"
                   "        System.out.println(words.size());"),
            "        System.out.println(found.map(Main::shout).orElse(\"none\"));",
            [_wl28(ws, limit,
                   _nl(_found28(ws, limit).upper() if _found28(ws, limit) else "none",
                       len(ws)))
             for (ws, limit) in _WL28],
            hints=["`shout` should not have to know about Optionals - it just "
                   "capitalises a String.",
                   "`map` is what applies it only when a value is present.",
                   "`found.map(Main::shout).orElse(\"none\")`",
                   "Had `shout` taken an `Optional<String>`, every caller would have had "
                   "to wrap - including the ones that certainly have a value.",
                   "This is the division of labour: the method does the work, the caller "
                   "decides about absence."],
            difficulty="Medium"),

        _jch("j28-de-final", "Saying it all in one chain", "Hard",
             "Find the first word longer than the limit, keep it only if it is longer "
             "than four characters, capitalise it, and print it or `none` - one chain, "
             "no `if`, no `get()`. Then print how many words there were.",
             _j28s(_RD_W28
                   + "        int limit = sc.nextInt();\n"
                     "        System.out.println(words.stream()\n"
                     "                .filter(w -> w.length() > limit)\n"
                     "                .findFirst()\n"
                     "                .filter(w -> w.length() > 4)\n"
                     "                .map(String::toUpperCase)\n"
                     "                .orElse(\"none\"));\n"
                     "        System.out.println(words.size());"),
             "        System.out.println(words.stream()\n"
             "                .filter(w -> w.length() > limit)\n"
             "                .findFirst()\n"
             "                .filter(w -> w.length() > 4)\n"
             "                .map(String::toUpperCase)\n"
             "                .orElse(\"none\"));\n"
             "        System.out.println(words.size());",
             [_wl28(ws, limit,
                    _nl(_found28(ws, limit).upper()
                        if (_found28(ws, limit) and len(_found28(ws, limit)) > 4)
                        else "none",
                        len(ws)))
              for (ws, limit) in _WL28],
             hints=["The first `filter` is a STREAM filter; `findFirst` then turns the "
                    "pipeline into an `Optional`.",
                    "The second `filter` is an OPTIONAL filter - same name, same idea, "
                    "different container.",
                    "That switch is worth noticing: `filter`, `map` and `flatMap` mean "
                    "the same thing in both.",
                    "`.map(String::toUpperCase)` then `.orElse(\"none\")` at the very "
                    "end.",
                    "Only `alpha` is longer than four characters, so most inputs print "
                    "`none`.",
                    "`limit` is captured by the lambda and never reassigned - "
                    "effectively final, module 25."]),
    ],
    quiz=[
        _jq("`Optional` as a method PARAMETER…",
            ["forces every caller to wrap - use an overload instead",
             "is recommended", "prevents nulls", "is required for streams"],
            0,
            "The caller already knows whether it has a value."),
        _jq("The single job Optional was designed for is…",
            ["a return type where absence is a real outcome",
             "fields", "parameters", "collections"],
            0,
            "Everywhere else it is usually ceremony."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M28_CAP_HELPERS = (
    "    static Optional<String> firstLongerThan(List<String> items, int limit) {\n"
    "        for (String item : items) {\n"
    "            if (item.length() > limit) {\n"
    "                return Optional.of(item);\n"
    "            }\n"
    "        }\n"
    "        return Optional.empty();\n"
    "    }\n"
    "\n"
    "    static List<String> allLongerThan(List<String> items, int limit) {\n"
    "        List<String> out = new ArrayList<>();\n"
    "        for (String item : items) {\n"
    "            if (item.length() > limit) {\n"
    "                out.add(item);\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }"
)

_M28_CAP_BODY = (
    _RD_W28
    + "        int limit = sc.nextInt();\n"
      "        System.out.println(firstLongerThan(words, limit).orElse(\"none\"));\n"
      "        System.out.println(firstLongerThan(words, limit)\n"
      "                .map(String::toUpperCase)\n"
      "                .orElse(\"NONE\"));\n"
      "        System.out.println(allLongerThan(words, limit));\n"
      "        System.out.println(words.stream()\n"
      "                .max(Comparator.comparing(String::length))\n"
      "                .orElse(\"none\"));\n"
      "        System.out.println(words.size());"
)


def _m28_cap_case(ws, limit):
    found = _found28(ws, limit)
    return _wl28(ws, limit,
                 _nl(found or "none",
                     found.upper() if found else "NONE",
                     _jl28([w for w in ws if len(w) > limit]),
                     max(ws, key=len),
                     len(ws)))


_M28_CAP = _jcap(
    "The lookup desk",
    """
Two helper methods whose **return types are the lesson**, and a `main` that
never writes `get()` and never writes `if`.

* **`firstLongerThan(items, limit)`** returns an `Optional<String>`. One value,
  which may genuinely not be there - so the signature says so.
* **`allLongerThan(items, limit)`** returns a plain `List<String>`. A collection
  already has a way to say "nothing", so wrapping it would give callers two.

That contrast is the whole module in two signatures. `main` then prints five
lines: the found word or a default, the same word capitalised through `map`, the
full list of matches, the longest word via the stream terminal that returns an
Optional, and the source size.
""",
    _jch("j28-cap-lookup", "The lookup desk", "Hard",
         "Write the two methods described in the brief so the given `main` compiles and "
         "prints its five lines.",
         _j28(_M28_CAP_HELPERS, _M28_CAP_BODY),
         _M28_CAP_HELPERS,
         [_m28_cap_case(ws, limit) for (ws, limit) in _WL28],
         hints=["`firstLongerThan` returns `Optional<String>`: `Optional.of(item)` from "
                "inside the loop, `Optional.empty()` after it.",
                "`allLongerThan` returns `List<String>` - just build it and return it, "
                "empty or not.",
                "Never `Optional<List<String>>`: an empty list already means nothing "
                "matched.",
                "Line two chains `.map(String::toUpperCase)` before `.orElse(\"NONE\")`, "
                "so the transformation only runs when there is a value.",
                "Line four is `words.stream().max(Comparator.comparing(String::length))` "
                "- a terminal that returns an Optional because an empty stream has no "
                "maximum.",
                "No `get()` anywhere, and no `if` in `main`.",
                "Two of the five inputs have no word longer than the limit, so they "
                "print the defaults and an empty list."]),
    example_io="stdin:  3\n        ada bo cy\n        3\n\n"
               "stdout: none\n        NONE\n        []\n        ada\n        3",
    rubric=[
        "`firstLongerThan` returns `Optional<String>`, using `of` inside the loop and `empty` after it.",
        "`allLongerThan` returns a plain `List<String>`, never an `Optional` of one.",
        "`main` contains no call to `get()`.",
        "`main` contains no `if` - absence is handled by `orElse` and `map`.",
        "The capitalisation happens through `map`, so it never runs on an absent value.",
        "The longest word comes from a stream terminal returning an Optional.",
        "The five lines are printed in the order the brief lists them.",
    ],
)


_MODULES.append(_jmod(
    28, 8, "Java 8+",
    "Optional",
    "A container of nought or one - and a return type that admits a method may have no "
    "answer, instead of returning null and hoping.",
    """
This module is the answer to a question modules 26 and 27 kept postponing. Every
deferral - the one-argument `reduce`, `findFirst`, `max`, `min`, `average` - was
the same sentence: **an empty stream has no answer, and the return type has to
say so.**

* **`Optional<T>` holds one value or none.** `of` asserts presence (and throws on
  null), `ofNullable` accepts null, `empty` is the absent one.
* **Unwrap with intent**: `orElse` for a constant default, `orElseGet` when
  computing it costs something (its argument is lazy; `orElse`'s is not),
  `orElseThrow` when absence is a bug, `ifPresent` to act or not act.
* **It composes.** `map` transforms only when there is a value, `filter` turns
  "present but unsuitable" into absent, and `flatMap` is for functions that
  return an Optional themselves. A chain replaces a nest of null checks.
* **The stream terminals** that could not exist before are here:
  `findFirst`, `max`, `min`, `reduce(op)` and the primitive `OptionalInt` /
  `OptionalDouble` from `average()` and `max()`.
* **And the design rule**, which is the part that actually matters: Optional is
  for **return types**. Not fields, not parameters, not collections - and never
  `get()`, which is the `NullPointerException` you were avoiding, renamed.

This closes Part 8, and the track.
""",
    _M28,
    capstone=_M28_CAP,
    objectives=[
        "Say what problem Optional solves, and why it is about the signature rather than the crash.",
        "Choose correctly between `of`, `ofNullable` and `empty`.",
        "Unwrap with `orElse`, `orElseGet`, `orElseThrow` and `ifPresent`, and justify each.",
        "Explain why `orElse`'s argument is evaluated even when the value is present.",
        "Chain `map` and `filter`, and say when `flatMap` is required instead.",
        "Name the stream terminals that return an Optional, and give the single reason they all do.",
        "Use `OptionalInt` and `OptionalDouble`, and say how they differ from `Optional<T>`.",
        "Say where Optional should NOT be used - fields, parameters, collections - and why.",
        "Explain why an unguarded `get()` defeats the purpose of the type.",
    ],
    why="`Optional` is asked about in almost every modern Java interview, and the "
        "questions go past the API immediately: why not use it for fields, what is wrong "
        "with `get()`, what is the difference between `orElse` and `orElseGet`. Each has "
        "a precise answer, and each is really a question about whether you have used the "
        "type or only read about it. It also completes the streams picture - the reason "
        "`findFirst` and `max` return what they do is the same reason Optional exists at "
        "all.",
    est_minutes=330,
    glossary=[
        _jg("Optional<T>", "A container holding either one value or none, intended as a "
                           "return type where absence is a real outcome."),
        _jg("Optional.of", "Builds a present Optional. Throws NullPointerException if "
                           "given null - it is an assertion."),
        _jg("Optional.ofNullable", "Builds a present Optional, or an empty one if the "
                                   "value is null."),
        _jg("orElse", "The value to use when empty. Its argument is evaluated whether or "
                      "not it is needed."),
        _jg("orElseGet", "The same, but taking a `Supplier` that is only called when the "
                         "Optional is empty."),
        _jg("orElseThrow", "Unwrap, or throw an exception you supply - for when absence "
                           "really is an error."),
        _jg("ifPresent", "Runs a `Consumer` only when a value is there. The replacement "
                         "for a null check with a body."),
        _jg("flatMap", "`map` for a function that itself returns an Optional; removes one "
                       "level of nesting."),
        _jg("OptionalInt / OptionalDouble", "Primitive versions, avoiding boxing. They "
                                            "have `orElse` but not `map` or `filter`."),
        _jg("get", "Returns the value or throws NoSuchElementException. Treat every "
                   "unguarded use as a bug."),
    ],
    cheatsheet="""
```java
// --- making one -----------------------------------------------------------
Optional.of(value)          // asserts non-null; throws NPE on null
Optional.ofNullable(value)  // null becomes Optional.empty()
Optional.empty()            // definitely absent

// --- getting the value out ------------------------------------------------
found.orElse("none");                       // default VALUE - always evaluated
found.orElseGet(Main::expensive);           // default SUPPLIER - lazy
found.orElseThrow(() -> new IllegalStateException("missing"));
found.ifPresent(w -> System.out.println(w));   // act, or do nothing
found.get();                                // <- treat as a bug. Always.

// --- composing ------------------------------------------------------------
found.map(String::toUpperCase)              // transforms only if present
     .filter(w -> w.length() > 4)           // "present but unsuitable" -> absent
     .orElse("none");                       // decide about absence LAST
found.flatMap(Main::firstLetter);           // when the function returns an Optional

// --- the stream terminals that return one ---------------------------------
words.stream().filter(p).findFirst()        // Optional<String>
words.stream().max(Comparator.comparing(String::length))   // Optional<String>
nums.stream().reduce((a, b) -> a + b)       // Optional<Integer> - no identity
nums.stream().mapToInt(Integer::intValue).average()        // OptionalDouble
// all for ONE reason: an empty stream has no answer

// --- where NOT to use it --------------------------------------------------
class User { Optional<String> name; }       // NO - field
void greet(Optional<String> name)           // NO - parameter; overload instead
Optional<List<String>> find()               // NO - an empty List already means empty
Optional<String> find()                     // YES - one value that may not exist
```
""",
    self_check=[
        "Can you say what Optional actually fixes, given that it does not prevent crashes by itself?",
        "Can you say when to use `of` rather than `ofNullable`, and what `of(null)` does?",
        "Can you explain why `orElse(expensive())` calls `expensive()` even when the value is present?",
        "Can you rewrite a null check plus default as a `map`/`orElse` chain?",
        "Can you say when `flatMap` is needed instead of `map`?",
        "Can you name four stream terminals that return an Optional, and the one reason they all do?",
        "Can you say why `OptionalDouble` exists alongside `Optional<Double>`?",
        "Can you give the three places Optional should not be used, with a reason for each?",
        "Can you explain why `get()` defeats the purpose of the type?",
    ],
    review=[
        _jq("`Optional.of(maybeNull)` where the value is null…",
            ["throws NullPointerException", "returns Optional.empty",
             "returns Optional[null]", "compiles to ofNullable"],
            0,
            "It is an assertion. Use `ofNullable` when null is possible."),
        _jq("```java\nfound.orElse(buildDefault());\n```\nWhen `found` is present, `buildDefault()`…",
            ["still runs - it is an argument, evaluated first",
             "does not run", "runs twice", "throws"],
            0,
            "`orElseGet` takes a Supplier and is the lazy version."),
        _jq("A repository method that finds no matching rows should return…",
            ["an empty List", "Optional.empty()", "null", "Optional<List>"],
            0,
            "A collection already has a way to say 'nothing'."),
        _jq("`words.stream().max(cmp)` returns an Optional for the same reason that…",
            ["`reduce(op)` without an identity does - an empty stream has no answer",
             "streams are lazy", "of erasure", "it may be parallel"],
            0,
            "One sentence explains every deferral in modules 26 and 27."),
    ],
    milestone="You can write a signature that admits it may have no answer, and a caller "
              "that handles that without a single null check - and you know the three "
              "places Optional makes code worse, which is the half of the topic most "
              "people skip. That closes Part 8, and the Java track.",
))
