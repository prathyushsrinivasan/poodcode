# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 23 practice - wildcards.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[23]`.
#
# The last module of Part 7, so everything through module 22 is fair game:
# collections, Comparable/Comparator (as NAMED classes - lambdas are banned
# course-wide), generic classes, generic methods and bounds.
#
# Each family drills one wildcard: `<?>` when the element type is irrelevant,
# `? extends` for a producer, `? super` for a consumer, and the two together in
# the PECS copy signature. The last family mixes them, and includes the JDK
# signature the learner has been calling since module 20 - sort(Comparator<?
# super E>).
# ---------------------------------------------------------------------------


def _p23prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


def _p23tprog(types, helpers, body):
    return _jp(
        _IMPORTS + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + (helpers.rstrip("\n") + "\n\n" if helpers.strip() else "")
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _p23m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p23prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p23b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p23prog(helpers, body),
                body, tests, hints)


def _p23t(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """A top-level type is given too; write main's BODY."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p23tprog(types, helpers, body),
                body, tests, hints)


_RD_W23 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N23 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_RD_WN23 = _RD_W23 + (
    "        int m = sc.nextInt();\n"
    "        List<Integer> nums = new ArrayList<>();\n"
    "        for (int i = 0; i < m; i++) {\n"
    "            nums.add(sc.nextInt());\n"
    "        }\n")

_WS23P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS23P = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])


def _w23(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n23(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wn23(ws, xs, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                            " ".join(str(x) for x in xs)]), out)


def _jl23(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


_PAIRS23 = tuple(zip(_WS23P, _NS23P))


# --- Family A - the unbounded wildcard ---------------------------------------

_P23_A = _jfam(
    "p23-unknown", "`List<?>` - when the element type is irrelevant",
    "A list of something, where the something never comes up.",
    """
```java
static void report(List<?> items) {
    System.out.println(items.size());
}
```

`List<?>` accepts a list of *anything*. A `List<Object>` parameter would not -
generics are invariant, so a `List<String>` is not a `List<Object>` and never
was.

Inside such a method:

* **anything that does not mention the element type is fine** - `size()`,
  `isEmpty()`, `clear()`, `toString()`;
* **reads come back as `Object`**, which is enough for `toString()` and
  `equals`;
* **nothing can be added** except `null`. The list has one real element type;
  the compiler just does not know which, so every write is refused.

`List<?>` is the opposite of a raw `List`: the raw type switches checking off,
the wildcard keeps it on and admits it cannot name the type.
""",
    [
        _p23m("j23-pa-size", "howMany", "Intro",
              "Write `howMany`, which returns the size of a list of anything at all.",
              """
    static int howMany(List<?> items) {
        return items.size();
    }
""",
              _RD_W23 + "        System.out.println(howMany(words));",
              [_w23(ws, len(ws)) for ws in _WS23P],
              ["`static int howMany(List<?> items) {`",
               "A `List<Object>` parameter would reject the `List<String>` argument.",
               "`size()` does not mention the element type, so it is allowed.",
               "One line of output."]),

        _p23m("j23-pa-print", "printAll", "Intro",
              "Write `printAll`, printing every element of any list on its own line.",
              """
    static void printAll(List<?> items) {
        for (Object item : items) {
            System.out.println(item);
        }
    }
""",
              _RD_W23 + "        printAll(words);",
              [_w23(ws, _nl(*ws)) for ws in _WS23P],
              ["The parameter is `List<?>`; the loop variable is the most specific "
               "type you can name.",
               "That type is `Object` - whatever the unknown element type is, it is "
               "one of those.",
               "`for (Object item : items) {`",
               "`println(Object)` calls the element's own `toString`."]),

        _p23m("j23-pa-length", "totalLength", "Easy",
              "Write `totalLength`, adding up the number of characters in the printed "
              "form of every element. `main` calls it on words and on numbers.",
              """
    static int totalLength(List<?> items) {
        int total = 0;
        for (Object item : items) {
            total += item.toString().length();
        }
        return total;
    }
""",
              _RD_WN23
              + "        System.out.println(totalLength(words));\n"
                "        System.out.println(totalLength(nums));",
              [_wn23(ws, xs, _nl(sum(len(w) for w in ws),
                                 sum(len(str(x)) for x in xs)))
               for (ws, xs) in _PAIRS23],
              ["Only a `List<?>` parameter accepts both call sites.",
               "Every object has `toString()`, so `Object` is enough here.",
               "`total += item.toString().length();`",
               "A negative number's minus sign counts as a character."]),

        _p23m("j23-pa-match", "countPrinting", "Medium",
              "Write `countPrinting`, counting how many elements of any list print as "
              "a given piece of text.",
              """
    static int countPrinting(List<?> items, String text) {
        int count = 0;
        for (Object item : items) {
            if (item.toString().equals(text)) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_W23
              + "        String q = sc.next();\n"
                "        System.out.println(countPrinting(words, q));",
              [_case("\n".join([str(len(ws)), " ".join(ws), q]),
                     sum(1 for w in ws if w == q))
               for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                               (["x", "x", "x"], "x"), (["pear", "fig"], "fig"),
                               (["a", "b", "c"], "d"))],
              ["The element type is unknown, but the text to compare against is a "
               "plain `String`.",
               "`static int countPrinting(List<?> items, String text) {`",
               "Compare `item.toString()` with `.equals(text)`.",
               "The answer may be zero."]),

        _p23b("j23-pa-two", "One method, two lists", "Easy",
              "`howMany` is written. Read words and numbers, then print the size of "
              "each list and the two added together - three lines.",
              """
    static int howMany(List<?> items) {
        return items.size();
    }
""",
              _RD_WN23
              + "        System.out.println(howMany(words));\n"
                "        System.out.println(howMany(nums));\n"
                "        System.out.println(howMany(words) + howMany(nums));",
              [_wn23(ws, xs, _nl(len(ws), len(xs), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS23],
              ["Both calls compile because the parameter names no element type.",
               "`howMany(words)` then `howMany(nums)`.",
               "The third line adds the two `int` results.",
               "Three printed lines."]),
    ])


# --- Family B - producers ----------------------------------------------------

_P23_B = _jfam(
    "p23-extends", "`? extends T` - producers",
    "A list you only read from can hold any subtype.",
    """
```java
static double total(List<? extends Number> items) {
    double sum = 0;
    for (Number item : items) {
        sum += item.doubleValue();
    }
    return sum;
}
```

"A list of some unknown type, which is `Number` or below." That accepts
`List<Integer>`, `List<Double>` and `List<Number>` alike - and a plain
`List<Number>` parameter would accept only the last of the three.

* **Reads come back at the bound**, so the loop variable is a `Number` and
  `doubleValue()` is available.
* **Writes are still refused.** The unknown subtype might be `Double`, and an
  `Integer` does not belong in a `List<Double>`.

Module 22's `<T extends Number>` says exactly the same thing. The rule of thumb:
if the type parameter would be used **once**, prefer the wildcard; if you need
to name the same `T` twice, keep the parameter.
""",
    [
        _p23m("j23-pb-total", "total", "Easy",
              "Write `total`, summing any list of numbers as a `double`, using a "
              "wildcard rather than a type parameter.",
              """
    static double total(List<? extends Number> items) {
        double sum = 0;
        for (Number item : items) {
            sum += item.doubleValue();
        }
        return sum;
    }
""",
              _RD_N23 + "        System.out.println(total(nums));",
              [_n23(xs, str(float(sum(xs)))) for xs in _NS23P],
              ["`static double total(List<? extends Number> items) {`",
               "The bound is what lets the loop variable be a `Number`.",
               "Accumulate in a `double` starting at 0.",
               "Whole sums therefore print with `.0`."]),

        _p23m("j23-pb-smallest", "smallest", "Easy",
              "Write `smallest`, returning the least value of any list of numbers as a "
              "`double`.",
              """
    static double smallest(List<? extends Number> items) {
        double best = items.get(0).doubleValue();
        for (Number item : items) {
            if (item.doubleValue() < best) {
                best = item.doubleValue();
            }
        }
        return best;
    }
""",
              _RD_N23 + "        System.out.println(smallest(nums));",
              [_n23(xs, str(float(min(xs)))) for xs in _NS23P],
              ["Seed with `items.get(0).doubleValue()` - a real element, so an "
               "all-negative list still works.",
               "`for (Number item : items)`",
               "`static double smallest(List<? extends Number> items) {`",
               "The result prints as a double."]),

        _p23m("j23-pb-negative", "countNegative", "Easy",
              "Write `countNegative`, counting the elements below zero in any list of "
              "numbers.",
              """
    static int countNegative(List<? extends Number> items) {
        int count = 0;
        for (Number item : items) {
            if (item.doubleValue() < 0) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_N23
              + "        System.out.println(countNegative(nums));\n"
                "        System.out.println(nums.size());",
              [_n23(xs, _nl(sum(1 for x in xs if x < 0), len(xs)))
               for xs in ([3, 1, 2], [5], [-4, -9, -1], [10, 0, -2], [7, -2, 9, 0])],
              ["The count is an ordinary `int`; the wildcard is only on the parameter.",
               "`item.doubleValue() < 0`",
               "Zero is not negative, which cases four and five check.",
               "Two printed lines."]),

        _p23m("j23-pb-ints", "sumInts", "Medium",
              "Write `sumInts`, which sums any list of numbers using their `int` view "
              "and returns an `int`. `main` calls it on whole numbers and then on a "
              "list of halves, where the truncation shows.",
              """
    static int sumInts(List<? extends Number> items) {
        int sum = 0;
        for (Number item : items) {
            sum += item.intValue();
        }
        return sum;
    }
""",
              _RD_N23
              + "        List<Double> halves = new ArrayList<>();\n"
                "        for (int x : nums) {\n"
                "            halves.add(x / 2.0);\n"
                "        }\n"
                "        System.out.println(sumInts(nums));\n"
                "        System.out.println(sumInts(halves));",
              [_n23(xs, _nl(sum(xs), sum(int(x / 2.0) for x in xs)))
               for xs in ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])],
              ["`intValue()` is the other method the `Number` bound promises.",
               "`static int sumInts(List<? extends Number> items) {`",
               "It truncates toward zero: 1.5 becomes 1, and -4.5 becomes -4.",
               "The same method serves both lists, which a `List<Number>` parameter "
               "could not."]),

        _p23b("j23-pb-spread", "Use the producer twice", "Medium",
              "`total` and `smallest` are written. Read the numbers, build a list of "
              "their halves as `Double`s, and print: the total of the whole numbers, "
              "the total of the halves, and the smallest half.",
              """
    static double total(List<? extends Number> items) {
        double sum = 0;
        for (Number item : items) {
            sum += item.doubleValue();
        }
        return sum;
    }

    static double smallest(List<? extends Number> items) {
        double best = items.get(0).doubleValue();
        for (Number item : items) {
            if (item.doubleValue() < best) {
                best = item.doubleValue();
            }
        }
        return best;
    }
""",
              _RD_N23
              + "        List<Double> halves = new ArrayList<>();\n"
                "        for (int x : nums) {\n"
                "            halves.add(x / 2.0);\n"
                "        }\n"
                "        System.out.println(total(nums));\n"
                "        System.out.println(total(halves));\n"
                "        System.out.println(smallest(halves));",
              [_n23(xs, _nl(str(float(sum(xs))), str(sum(x / 2.0 for x in xs)),
                            str(min(x / 2.0 for x in xs))))
               for xs in ([3, 1, 2], [5], [-4, -8, -2], [10, 10, 2], [7, 2, 9, 4])],
              ["`List<Double> halves = new ArrayList<>();` and `halves.add(x / 2.0);`.",
               "Both methods accept both lists, because `Integer` and `Double` are "
               "each below `Number`.",
               "Neither could be called if the parameter said `List<Number>`.",
               "Three printed lines, all doubles."]),
    ])


# --- Family C - consumers ----------------------------------------------------

_P23_C = _jfam(
    "p23-super", "`? super T` - consumers",
    "A list you only write into can be a list of any supertype.",
    """
```java
static void fill(List<? super String> target, List<String> src) {
    for (String item : src) {
        target.add(item);
    }
}
```

"Some unknown type, which is `String` or above." A `List<String>` qualifies and
so does a `List<Object>` - both can certainly hold a `String`.

The mirror of the producer, in both directions:

| Wildcard | You may | You may not |
|---|---|---|
| `? extends T` | read as `T` | add anything |
| `? super T` | add a `T` | read as anything but `Object` |

Reading gives you `Object`, because the list might really be a `List<Object>`.

**PECS - Producer Extends, Consumer Super.** Ask what the parameter does *for
the method*: if the method pushes values into it, it is a consumer, and it takes
`? super`.
""",
    [
        _p23m("j23-pc-fill", "fill", "Medium",
              "Write `fill`, copying every word of a source list into a target list "
              "that is guaranteed able to hold Strings. `main` passes a "
              "`List<Object>`.",
              """
    static void fill(List<? super String> target, List<String> src) {
        for (String item : src) {
            target.add(item);
        }
    }
""",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        fill(any, words);\n"
                "        System.out.println(any);\n"
                "        System.out.println(any.size());",
              [_w23(ws, _nl(_jl23(ws), len(ws))) for ws in _WS23P],
              ["The method only ADDS to `target`, which makes it a consumer.",
               "`static void fill(List<? super String> target, List<String> src) {`",
               "A `List<String>` parameter would reject `main`'s `List<Object>`.",
               "The body is an enhanced `for` and a single `target.add(item);`."]),

        _p23m("j23-pc-count", "addCount", "Medium",
              "Write `addCount`, which appends the numbers 1 to `n` to a list able to "
              "hold Integers.",
              """
    static void addCount(List<? super Integer> target, int n) {
        for (int i = 1; i <= n; i++) {
            target.add(i);
        }
    }
""",
              """
        int n = sc.nextInt();
        List<Object> any = new ArrayList<>();
        addCount(any, n);
        System.out.println(any);
        System.out.println(any.size());
""",
              [_case(str(n), _nl(_jl23(list(range(1, n + 1))), n))
               for n in (3, 1, 5, 2, 4)],
              ["`static void addCount(List<? super Integer> target, int n) {`",
               "`target.add(i)` autoboxes the `int` into an `Integer`, which any "
               "supertype list can hold.",
               "Count from 1 to `n` inclusive.",
               "The list prints in the `[1, 2, 3]` form."]),

        _p23m("j23-pc-repeat", "addTimes", "Medium",
              "Write `addTimes`, which appends the same word to a target list a given "
              "number of times.",
              """
    static void addTimes(List<? super String> target, String word, int times) {
        for (int i = 0; i < times; i++) {
            target.add(word);
        }
    }
""",
              """
        String w = sc.next();
        int times = sc.nextInt();
        List<Object> any = new ArrayList<>();
        addTimes(any, w, times);
        System.out.println(any);
        System.out.println(any.size());
""",
              [_case(f"{w} {t}", _nl(_jl23([w] * t), t))
               for (w, t) in (("ada", 3), ("bo", 1), ("x", 0), ("zed", 2),
                              ("gamma", 4))],
              ["Three parameters: the consumer list, the word, and the count.",
               "`static void addTimes(List<? super String> target, String word, "
               "int times) {`",
               "Zero times must add nothing and print `[]`, which case three checks.",
               "Only the target list needs a wildcard - the word is an ordinary "
               "`String`."]),

        _p23m("j23-pc-upper", "addUpper", "Medium",
              "Write `addUpper`, copying every word of a source list into a target "
              "list in upper case.",
              """
    static void addUpper(List<? super String> target, List<String> src) {
        for (String item : src) {
            target.add(item.toUpperCase());
        }
    }
""",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        addUpper(any, words);\n"
                "        System.out.println(any);",
              [_w23(ws, _jl23([w.upper() for w in ws])) for ws in _WS23P],
              ["The target consumes Strings, so it takes `? super String`.",
               "`target.add(item.toUpperCase());`",
               "The source is a concrete `List<String>`, so its elements come out as "
               "Strings already.",
               "One printed line."]),

        _p23b("j23-pc-both", "Two consumers, one list", "Medium",
              "`fill` and `addCount` are written. Read words and a number `k`, pour "
              "the words into a `List<Object>`, then append 1 to `k` to the SAME list. "
              "Print the list and its size.",
              """
    static void fill(List<? super String> target, List<String> src) {
        for (String item : src) {
            target.add(item);
        }
    }

    static void addCount(List<? super Integer> target, int n) {
        for (int i = 1; i <= n; i++) {
            target.add(i);
        }
    }
""",
              _RD_W23
              + "        int k = sc.nextInt();\n"
                "        List<Object> any = new ArrayList<>();\n"
                "        fill(any, words);\n"
                "        addCount(any, k);\n"
                "        System.out.println(any);\n"
                "        System.out.println(any.size());",
              [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                     _nl(_jl23(list(ws) + list(range(1, k + 1))), len(ws) + k))
               for (ws, k) in ((["ada", "bo", "cy"], 2), (["solo"], 1),
                               (["x", "yy", "zzz"], 0), (["pear", "fig"], 3),
                               (["alpha", "beta", "gamma", "d"], 1))],
              ["One `List<Object>` satisfies both `? super String` and "
               "`? super Integer` - which is the whole reason the wildcards are there.",
               "Read `k` after the words.",
               "Call `fill` first, then `addCount`, so the words come first in the "
               "output.",
               "A `k` of zero adds nothing."]),
    ])


# --- Family D - PECS together ------------------------------------------------

_P23_D = _jfam(
    "p23-pecs", "PECS - both wildcards in one signature",
    "`copy(List<? super T> dest, List<? extends T> src)`.",
    """
```java
static <T> void copy(List<? super T> dest, List<? extends T> src) {
    for (T item : src) {     // src PRODUCES Ts
        dest.add(item);      // dest CONSUMES Ts
    }
}
```

Three parts, and all three are load bearing:

* **`<T>`** - a named type parameter is still needed, because the two
  parameters have to be related to *each other*.
* **`? super T` on the destination** - it consumes, so any supertype list will
  do.
* **`? extends T` on the source** - it produces, so any subtype list will do.

`copy(objects, words)` then infers `T` as `String`. Written as `copy(List<T>,
List<T>)` the same call is rejected, because no single `T` is both `Object` and
`String`.

**Never put a wildcard in a return type.** It only moves the unknown type onto
every caller. Return `List<T>`, or nothing at all.
""",
    [
        _p23m("j23-pd-copy", "copy", "Medium",
              "Write `copy`, moving every element of a source list into a destination "
              "list, with PECS on both parameters.",
              """
    static <T> void copy(List<? super T> dest, List<? extends T> src) {
        for (T item : src) {
            dest.add(item);
        }
    }
""",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        copy(any, words);\n"
                "        System.out.println(any);\n"
                "        System.out.println(any.size());",
              [_w23(ws, _nl(_jl23(ws), len(ws))) for ws in _WS23P],
              ["The signature is "
               "`static <T> void copy(List<? super T> dest, List<? extends T> src)`.",
               "The loop variable is a `T`, because the source produces `T`s.",
               "`dest.add(item);` is legal because the destination consumes them.",
               "`T` is inferred as `String` at the call site."]),

        _p23m("j23-pd-moved", "moveAll", "Medium",
              "Write `moveAll`, the same copy but returning how many elements it "
              "moved.",
              """
    static <T> int moveAll(List<? super T> dest, List<? extends T> src) {
        int moved = 0;
        for (T item : src) {
            dest.add(item);
            moved++;
        }
        return moved;
    }
""",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        System.out.println(moveAll(any, words));\n"
                "        System.out.println(any);",
              [_w23(ws, _nl(len(ws), _jl23(ws))) for ws in _WS23P],
              ["Same two parameters, an `int` return type instead of `void`.",
               "`static <T> int moveAll(List<? super T> dest, "
               "List<? extends T> src) {`",
               "Count in an ordinary `int` - only the element types are generic.",
               "The count prints before the list, because it is evaluated first."]),

        _p23m("j23-pd-twice", "copyTwice", "Medium",
              "Write `copyTwice`, appending every element of the source to the "
              "destination two times each.",
              """
    static <T> void copyTwice(List<? super T> dest, List<? extends T> src) {
        for (T item : src) {
            dest.add(item);
            dest.add(item);
        }
    }
""",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        copyTwice(any, words);\n"
                "        System.out.println(any);\n"
                "        System.out.println(any.size());",
              [_w23(ws, _nl(_jl23([w for w in ws for _ in (0, 1)]), 2 * len(ws)))
               for ws in _WS23P],
              ["Same PECS signature; the body adds twice per element.",
               "Each element appears twice IN A ROW, not the whole list twice.",
               "The destination ends up with double the size.",
               "`static <T> void copyTwice(List<? super T> dest, "
               "List<? extends T> src) {`"]),

        _p23m("j23-pd-first", "copyFirst", "Hard",
              "Write `copyFirst`, copying only the first `k` elements of the source - "
              "or all of them if the source is shorter.",
              """
    static <T> void copyFirst(List<? super T> dest, List<? extends T> src, int k) {
        int limit = Math.min(k, src.size());
        for (int i = 0; i < limit; i++) {
            dest.add(src.get(i));
        }
    }
""",
              _RD_W23
              + "        int k = sc.nextInt();\n"
                "        List<Object> any = new ArrayList<>();\n"
                "        copyFirst(any, words, k);\n"
                "        System.out.println(any);\n"
                "        System.out.println(any.size());",
              [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                     _nl(_jl23(list(ws)[:min(k, len(ws))]), min(k, len(ws))))
               for (ws, k) in ((["ada", "bo", "cy"], 2), (["solo"], 3),
                               (["x", "yy", "zzz"], 0), (["pear", "fig"], 2),
                               (["alpha", "beta", "gamma", "d"], 1))],
              ["An index loop this time, because you are counting.",
               "`Math.min(k, src.size())` guards a `k` larger than the source - case "
               "two.",
               "`src.get(i)` comes back as the source's unknown subtype, which is "
               "still a `T`.",
               "`static <T> void copyFirst(List<? super T> dest, "
               "List<? extends T> src, int k) {`",
               "A `k` of zero copies nothing and prints `[]`."]),

        _p23b("j23-pd-ledger", "One ledger, two element types", "Medium",
              "`copy` is written. Read words and numbers, pour both into the same "
              "`List<Object>` ledger - words first - then print the ledger and its "
              "size.",
              """
    static <T> void copy(List<? super T> dest, List<? extends T> src) {
        for (T item : src) {
            dest.add(item);
        }
    }
""",
              _RD_WN23
              + "        List<Object> ledger = new ArrayList<>();\n"
                "        copy(ledger, words);\n"
                "        copy(ledger, nums);\n"
                "        System.out.println(ledger);\n"
                "        System.out.println(ledger.size());",
              [_wn23(ws, xs, _nl(_jl23(list(ws) + list(xs)), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS23],
              ["The first call infers `T` as `String`, the second as `Integer`.",
               "The same `List<Object>` is a legal destination for both, because "
               "`Object` is a supertype of each.",
               "Words first, then numbers - the ledger prints in insertion order.",
               "Two printed lines."]),
    ])


# --- Family E - choosing, and the JDK's own signatures -----------------------

_BYLEN23 = """
class ByLength implements Comparator<Object> {
    @Override
    public int compare(Object a, Object b) {
        return Integer.compare(a.toString().length(), b.toString().length());
    }
}
"""

_P23_E = _jfam(
    "p23-choose", "Choosing a wildcard - and reading the JDK's",
    "Where these signatures have been all along.",
    """
The rules, in the order you apply them:

1. **Does the method touch the element type at all?** No - `List<?>`.
2. **Does it only read?** `List<? extends T>`.
3. **Does it only write?** `List<? super T>`.
4. **Does it need to name the same type twice** - two parameters that must
   match, or a return type that matches a parameter? Then a named `<T>`, with
   wildcards only where each list is one-directional.
5. **Return types never get a wildcard.**

You have been calling these since module 17 without reading them:

```java
list.sort(Comparator<? super E> c);        // the comparator only CONSUMES
list.addAll(Collection<? extends E> c);    // the source only PRODUCES
```

The first is why a `Comparator<Object>` can sort a `List<String>`: sorting only
hands elements *to* the comparator, so any comparator that can accept a `String`
will do. Written `Comparator<E>` it would not compile - and every one of your
own general-purpose comparators would have to be duplicated per element type.
""",
    [
        _p23b("j23-pe-widen", "Widening by hand", "Easy",
              "You cannot assign a `List<String>` to a `List<Object>`, but you can "
              "copy the elements. Build that copy, print it, then print the original "
              "to show it is untouched.",
              "",
              _RD_W23
              + "        List<Object> any = new ArrayList<>();\n"
                "        for (String w : words) {\n"
                "            any.add(w);\n"
                "        }\n"
                "        System.out.println(any);\n"
                "        System.out.println(words);",
              [_w23(ws, _nl(_jl23(ws), _jl23(ws))) for ws in _WS23P],
              ["Element by element is always legal - a `String` IS an `Object`.",
               "It is only the whole-list assignment that invariance forbids.",
               "`List<Object> any = new ArrayList<>();` then an enhanced `for`.",
               "The two printed lines look identical, and are two different lists."]),

        _p23t("j23-pe-sort", "A comparator of Object, sorting Strings", "Medium",
              "`ByLength` is a `Comparator<Object>`. Read `n` words, sort them by "
              "length with it, and print the list - the sort compiles because "
              "`sort` takes a `Comparator<? super E>`.",
              _BYLEN23,
              "",
              _RD_W23
              + "        words.sort(new ByLength());\n"
                "        System.out.println(words);",
              [_w23(ws, _jl23(sorted(ws, key=len))) for ws in _WS23P],
              ["`words.sort(new ByLength());` - one line.",
               "It compiles because the parameter is `Comparator<? super String>`, and "
               "`Object` is a supertype of `String`.",
               "`List.sort` is stable, so equally long words keep their input order.",
               "Print the list afterwards; it was sorted in place."]),

        _p23m("j23-pe-sizes", "Two unknown lists", "Easy",
              "Write `totalSize`, returning the combined size of two lists whose "
              "element types are irrelevant and need not match.",
              """
    static int totalSize(List<?> a, List<?> b) {
        return a.size() + b.size();
    }
""",
              _RD_WN23 + "        System.out.println(totalSize(words, nums));",
              [_wn23(ws, xs, len(ws) + len(xs)) for (ws, xs) in _PAIRS23],
              ["Two separate `?`s mean two separate unknown types - which is exactly "
               "right here.",
               "`static int totalSize(List<?> a, List<?> b) {`",
               "A named `<T>` would wrongly force both lists to hold the same type.",
               "One printed line."]),

        _p23m("j23-pe-merged", "merged", "Hard",
              "Write `merged`, which returns a NEW list containing everything from two "
              "source lists, first list first. Both sources are producers; the return "
              "type must name the type, never a wildcard.",
              """
    static <T> List<T> merged(List<? extends T> a, List<? extends T> b) {
        List<T> out = new ArrayList<>();
        for (T item : a) {
            out.add(item);
        }
        for (T item : b) {
            out.add(item);
        }
        return out;
    }
""",
              _RD_WN23
              + "        List<Object> all = merged(words, nums);\n"
                "        System.out.println(all);\n"
                "        System.out.println(all.size());",
              [_wn23(ws, xs, _nl(_jl23(list(ws) + list(xs)), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS23],
              ["The return type is `List<T>` - a wildcard there would only push the "
               "unknown onto the caller.",
               "Both parameters are producers: `List<? extends T>`.",
               "`static <T> List<T> merged(List<? extends T> a, "
               "List<? extends T> b) {`",
               "Build a `new ArrayList<>()` and copy each source in turn.",
               "`main` assigns the result to a `List<Object>`, so `T` is inferred as "
               "`Object` - which both a `List<String>` and a `List<Integer>` are below."]),

        _p23b("j23-pe-all", "All three, one program", "Hard",
              "`howMany`, `total` and `copy` are written - one of each wildcard. Read "
              "words and numbers and print: how many words, how many numbers, the "
              "total of the numbers, the ledger built by copying both lists into a "
              "`List<Object>` (words first), and finally how many entries the ledger "
              "has.",
              """
    static int howMany(List<?> items) {
        return items.size();
    }

    static double total(List<? extends Number> items) {
        double sum = 0;
        for (Number item : items) {
            sum += item.doubleValue();
        }
        return sum;
    }

    static <T> void copy(List<? super T> dest, List<? extends T> src) {
        for (T item : src) {
            dest.add(item);
        }
    }
""",
              _RD_WN23
              + "        System.out.println(howMany(words));\n"
                "        System.out.println(howMany(nums));\n"
                "        System.out.println(total(nums));\n"
                "        List<Object> ledger = new ArrayList<>();\n"
                "        copy(ledger, words);\n"
                "        copy(ledger, nums);\n"
                "        System.out.println(ledger);\n"
                "        System.out.println(howMany(ledger));",
              [_wn23(ws, xs, _nl(len(ws), len(xs), str(float(sum(xs))),
                                 _jl23(list(ws) + list(xs)), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS23],
              ["`howMany` takes `List<?>`, so it accepts the words, the numbers and "
               "the ledger alike.",
               "`total` only accepts the numbers - `String` is not below `Number`.",
               "Two `copy` calls, words first, into the same `List<Object>`.",
               "The total prints as a double, with `.0` on whole sums.",
               "Five printed lines, in the order the prompt lists them."]),
    ])


_PRACTICE[23] = [_P23_A, _P23_B, _P23_C, _P23_D, _P23_E]
