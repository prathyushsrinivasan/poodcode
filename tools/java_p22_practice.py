# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 22 practice - generic methods and bounded type parameters.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[22]`.
#
# Wildcards are module 23, so every signature here names its type parameter -
# `<T>`, `<T extends Comparable<T>>`, `<T extends Number>` - and nothing writes
# `? extends`. Lambdas are banned course-wide, so a Comparator is a named class.
#
# Most of these ask for the METHOD rather than the main: the signature is the
# thing being drilled, and getting `<T>` into the right position is most of it.
# ---------------------------------------------------------------------------


def _p22prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


def _p22tprog(types, helpers, body):
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


def _p22m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p22prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p22b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p22prog(helpers, body),
                body, tests, hints)


def _p22c(eid, title, difficulty, prompt, types, body, tests, hints, helpers=""):
    """Write the generic CLASS; main is given."""
    return _jch(eid, title, difficulty, prompt, _p22tprog(types, helpers, body),
                types.strip("\n"), tests, hints)


def _p22t(eid, title, difficulty, prompt, types, body, tests, hints, helpers=""):
    """The class is given; write main's BODY."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p22tprog(types, helpers, body),
                body, tests, hints)


_RD_W22 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

_RD_N22 = ("        int n = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_WS22P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS22P = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])


def _w22(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _wq22(ws, q, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), q]), out)


def _n22(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jl22(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- Family A - the plain generic method -------------------------------------

_P22_A = _jfam(
    "p22-method", "The plain generic method",
    "`<T>` between the modifiers and the return type.",
    """
```java
static <T> T first(List<T> items) {
    return items.get(0);
}
```

Three positions to keep straight, and only the first is new:

| Position | What it is |
|---|---|
| `static **<T>**` | the **declaration** - the method's own type parameter |
| `<T> **T** first` | the **return type**, using it |
| `List<**T**> items` | a parameter type, using it |

Leave the declaration out and you get *cannot find symbol: class T* - the
single most common generics compile error there is.

**The call site says nothing.** `first(words)` infers `T` as `String` from the
argument, exactly as the diamond does. A type witness (`Main.<String>first(xs)`)
exists for the rare case where there is nothing to infer from.

**One `T` used twice means the same type twice.** `static <T> int
countEqual(List<T> items, T target)` will not let you look for a String in a
list of Integers - the compiler has to find one `T` that fits both parameters.

Nothing here needs a bound, because nothing is *called* on a `T` beyond what
every object has: `equals`, `hashCode`, `toString`.
""",
    [
        _p22m("j22-pa-first", "first", "Intro",
              "Write `first`, which returns element 0 of any list, already typed.",
              """
    static <T> T first(List<T> items) {
        return items.get(0);
    }
""",
              _RD_W22
              + "        String w = first(words);\n"
                "        System.out.println(w);\n"
                "        System.out.println(w.length());",
              [_w22(ws, _nl(ws[0], len(ws[0]))) for ws in _WS22P],
              ["`static <T> T first(List<T> items) {`",
               "The declaration goes between `static` and the return type.",
               "The body is one line: `return items.get(0);`.",
               "`main` assigns the result straight into a `String`, which only "
               "compiles because `T` was inferred as `String`."]),

        _p22m("j22-pa-last", "last", "Intro",
              "Write `last`, which returns the final element of any list.",
              """
    static <T> T last(List<T> items) {
        return items.get(items.size() - 1);
    }
""",
              _RD_W22
              + "        System.out.println(last(words));\n"
                "        System.out.println(words.size());",
              [_w22(ws, _nl(ws[-1], len(ws))) for ws in _WS22P],
              ["Same signature shape as `first`, different index.",
               "`static <T> T last(List<T> items) {`",
               "`items.get(items.size() - 1)`",
               "A one-element list returns that element, which case two checks."]),

        _p22m("j22-pa-printall", "printAll", "Intro",
              "Write `printAll`, which prints every element of any list on its own "
              "line.",
              """
    static <T> void printAll(List<T> items) {
        for (T item : items) {
            System.out.println(item);
        }
    }
""",
              _RD_W22 + "        printAll(words);",
              [_w22(ws, _nl(*ws)) for ws in _WS22P],
              ["The return type is `void`, and `<T>` still goes before it.",
               "`static <T> void printAll(List<T> items) {`",
               "The loop variable can be a `T`.",
               "`println` calls each element's own `toString`."]),

        _p22m("j22-pa-count", "countEqual", "Easy",
              "Write `countEqual`, which counts how many elements of a list equal a "
              "target. Both the elements and the target are the same `T`.",
              """
    static <T> int countEqual(List<T> items, T target) {
        int count = 0;
        for (T item : items) {
            if (item.equals(target)) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_W22
              + "        String q = sc.next();\n"
                "        System.out.println(countEqual(words, q));",
              [_wq22(ws, q, sum(1 for w in ws if w == q))
               for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                               (["x", "x", "x"], "x"), (["pear", "fig"], "fig"),
                               (["a", "b", "c"], "d"))],
              ["`static <T> int countEqual(List<T> items, T target) {` - one `T`, two "
               "parameters.",
               "The count itself is an ordinary `int`; only the element type is "
               "generic.",
               "Compare with `.equals`, never `==`.",
               "An absent target gives 0, which case two and five check."]),

        _p22m("j22-pa-has", "has", "Easy",
              "Write `has`, which reports whether a list contains a value, without "
              "calling the list's own `contains`.",
              """
    static <T> boolean has(List<T> items, T target) {
        for (T item : items) {
            if (item.equals(target)) {
                return true;
            }
        }
        return false;
    }
""",
              _RD_W22
              + "        String q = sc.next();\n"
                "        System.out.println(has(words, q));\n"
                "        System.out.println(words.size());",
              [_wq22(ws, q, _nl(_jbool(q in ws), len(ws)))
               for (ws, q) in ((["ada", "bo", "cy"], "bo"), (["solo"], "zzz"),
                               (["x", "yy", "zzz"], "x"), (["pear", "fig"], "fig"),
                               (["alpha", "beta"], "gamma"))],
              ["`static <T> boolean has(List<T> items, T target) {`",
               "Return `true` from inside the loop the moment a match is found.",
               "The final `return false;` runs only if the loop finished.",
               "`.equals`, not `==` - the same rule as always."]),
    ])


# --- Family B - the Comparable bound -----------------------------------------

_P22_B = _jfam(
    "p22-comparable", "Bounded by `Comparable`",
    "The bound that lets the body call `compareTo`.",
    """
An unbounded `T` cannot be compared - the compiler does not know what it is, so
only `Object`'s methods are available. A bound is the promise that unlocks it:

```java
static <T extends Comparable<T>> T max(List<T> items) {
    T best = items.get(0);
    for (T item : items) {
        if (item.compareTo(best) > 0) {
            best = item;
        }
    }
    return best;
}
```

Read the bound as **"T, which is comparable to its own type"**. `String`,
`Integer`, `Double` and every well-behaved class satisfy it.

* `extends` covers *implements* too - there is no `implements` in a bound.
* `Comparable<T>`, not raw `Comparable`: the raw form would hand back
  `compareTo(Object)` and throw the type checking away again.
* `compareTo` returns **negative / zero / positive**, never specifically -1 and
  1. Compare it against 0 and nothing else.

Seed the running best with element 0 and use a **strict** comparison, so ties
keep the earlier element - the same stability instinct as module 20.
""",
    [
        _p22m("j22-pb-max", "max", "Easy",
              "Write `max`, returning the largest element of a list by natural order.",
              """
    static <T extends Comparable<T>> T max(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }
""",
              _RD_N22 + "        System.out.println(max(nums));",
              [_n22(xs, max(xs)) for xs in _NS22P],
              ["`static <T extends Comparable<T>> T max(List<T> items) {`",
               "Without the bound, `compareTo` is *cannot find symbol*.",
               "Seed `best` with `items.get(0)`.",
               "`item.compareTo(best) > 0` means item is larger."]),

        _p22m("j22-pb-min", "min", "Easy",
              "Write `min`, returning the smallest element by natural order. On words "
              "that means dictionary order.",
              """
    static <T extends Comparable<T>> T min(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) < 0) {
                best = item;
            }
        }
        return best;
    }
""",
              _RD_W22 + "        System.out.println(min(words));",
              [_w22(ws, min(ws)) for ws in _WS22P],
              ["Same bound as `max`; only the comparison flips.",
               "`item.compareTo(best) < 0`",
               "`String`'s natural order is dictionary order, so `alpha` beats `beta`.",
               "One line of output."]),

        _p22m("j22-pb-sorted", "isSorted", "Medium",
              "Write `isSorted`, reporting whether a list is in non-decreasing natural "
              "order. A list of one element is sorted.",
              """
    static <T extends Comparable<T>> boolean isSorted(List<T> items) {
        for (int i = 1; i < items.size(); i++) {
            if (items.get(i).compareTo(items.get(i - 1)) < 0) {
                return false;
            }
        }
        return true;
    }
""",
              _RD_N22
              + "        System.out.println(isSorted(nums));\n"
                "        System.out.println(nums.size());",
              [_n22(xs, _nl(_jbool(all(xs[i] >= xs[i - 1] for i in range(1, len(xs)))),
                            len(xs)))
               for xs in ([1, 2, 3], [5], [3, 1, 2], [2, 2, 4], [7, 2, 9, 4])],
              ["Start the loop at index 1 and compare each element with the one before "
               "it.",
               "`items.get(i).compareTo(items.get(i - 1)) < 0` means out of order.",
               "Equal neighbours are fine - non-decreasing, not strictly increasing.",
               "A single-element list never enters the loop and returns `true`."]),

        _p22m("j22-pb-greater", "countGreater", "Medium",
              "Write `countGreater`, counting how many elements are strictly greater "
              "than a given bound.",
              """
    static <T extends Comparable<T>> int countGreater(List<T> items, T bound) {
        int count = 0;
        for (T item : items) {
            if (item.compareTo(bound) > 0) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_W22
              + "        String q = sc.next();\n"
                "        System.out.println(countGreater(words, q));",
              [_wq22(ws, q, sum(1 for w in ws if w > q))
               for (ws, q) in ((["ada", "bo", "cy"], "bo"), (["solo"], "aaa"),
                               (["x", "yy", "zzz"], "zzz"), (["pear", "fig"], "a"),
                               (["alpha", "beta", "gamma", "d"], "c"))],
              ["The bound is the same type as the elements, so it is a `T` too.",
               "`static <T extends Comparable<T>> int countGreater(List<T> items, "
               "T bound) {`",
               "Strictly greater: `compareTo(bound) > 0`, so an equal element does not "
               "count.",
               "Case three's bound equals the largest word, so the answer is 0."]),

        _p22m("j22-pb-span", "span", "Medium",
              "Write `max` and `min` (both bounded), then `main` prints the largest "
              "word, the smallest word, and whether they are equal.",
              """
    static <T extends Comparable<T>> T max(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) > 0) {
                best = item;
            }
        }
        return best;
    }

    static <T extends Comparable<T>> T min(List<T> items) {
        T best = items.get(0);
        for (T item : items) {
            if (item.compareTo(best) < 0) {
                best = item;
            }
        }
        return best;
    }
""",
              _RD_W22
              + "        System.out.println(max(words));\n"
                "        System.out.println(min(words));\n"
                "        System.out.println(max(words).equals(min(words)));",
              [_w22(ws, _nl(max(ws), min(ws), _jbool(max(ws) == min(ws))))
               for ws in _WS22P],
              ["Two methods, the same bound, opposite comparisons.",
               "Both seed with element 0 and walk the whole list.",
               "A one-element list has the same max and min, so the third line is "
               "`true` there.",
               "Compare the two results with `.equals`, not `==`."]),
    ])


# --- Family C - the Number bound ---------------------------------------------

_P22_C = _jfam(
    "p22-number", "Bounded by `Number`",
    "One method that serves `Integer`, `Double` and every other wrapper.",
    """
```java
static <T extends Number> double total(List<T> items) {
    double sum = 0;
    for (T item : items) {
        sum += item.doubleValue();
    }
    return sum;
}
```

`Number` is the abstract class every numeric wrapper extends, and the bound is
what makes its methods callable:

| Call | Gives |
|---|---|
| `intValue()` | the value as an `int`, truncating |
| `doubleValue()` | the value as a `double` |
| `longValue()`, `floatValue()` | the obvious |

A **class** bound and an **interface** bound are written identically -
`extends` covers both.

Two habits worth forming here:

* Accumulate in a `double` when the element type is unknown; anything narrower
  silently loses information for a `Double` input.
* A `double` result prints with a decimal point - `6.0`, not `6` - which the
  expected output reflects.
""",
    [
        _p22m("j22-pc-total", "total", "Easy",
              "Write `total`, summing any list of numbers as a `double`.",
              """
    static <T extends Number> double total(List<T> items) {
        double sum = 0;
        for (T item : items) {
            sum += item.doubleValue();
        }
        return sum;
    }
""",
              _RD_N22 + "        System.out.println(total(nums));",
              [_n22(xs, str(float(sum(xs)))) for xs in _NS22P],
              ["`static <T extends Number> double total(List<T> items) {`",
               "Without the bound, `doubleValue()` is *cannot find symbol*.",
               "Accumulate in a `double`, starting at 0.",
               "The printed result therefore ends in `.0` for whole sums."]),

        _p22m("j22-pc-biggest", "biggest", "Easy",
              "Write `biggest`, returning the largest value in any list of numbers as "
              "a `double`.",
              """
    static <T extends Number> double biggest(List<T> items) {
        double best = items.get(0).doubleValue();
        for (T item : items) {
            if (item.doubleValue() > best) {
                best = item.doubleValue();
            }
        }
        return best;
    }
""",
              _RD_N22 + "        System.out.println(biggest(nums));",
              [_n22(xs, str(float(max(xs)))) for xs in _NS22P],
              ["Seed with `items.get(0).doubleValue()`.",
               "Compare in `double`s, since that is the only view the bound promises.",
               "`static <T extends Number> double biggest(List<T> items) {`",
               "All-negative input still works, because the seed is a real element - "
               "case three."]),

        _p22m("j22-pc-positive", "countPositive", "Easy",
              "Write `countPositive`, counting the elements of a number list that are "
              "greater than zero.",
              """
    static <T extends Number> int countPositive(List<T> items) {
        int count = 0;
        for (T item : items) {
            if (item.doubleValue() > 0) {
                count++;
            }
        }
        return count;
    }
""",
              _RD_N22
              + "        System.out.println(countPositive(nums));\n"
                "        System.out.println(nums.size());",
              [_n22(xs, _nl(sum(1 for x in xs if x > 0), len(xs)))
               for xs in ([3, 1, 2], [5], [-4, -9, -1], [10, 0, 2], [7, -2, 9, 0])],
              ["The count is an ordinary `int`; only the element type needs the bound.",
               "`item.doubleValue() > 0`",
               "Zero is not positive - cases four and five depend on it.",
               "Two lines: the count, then the size."]),

        _p22m("j22-pc-squares", "sumOfSquares", "Medium",
              "Write `sumOfSquares`, returning the sum of every element multiplied by "
              "itself, as a `double`.",
              """
    static <T extends Number> double sumOfSquares(List<T> items) {
        double sum = 0;
        for (T item : items) {
            sum += item.doubleValue() * item.doubleValue();
        }
        return sum;
    }
""",
              _RD_N22 + "        System.out.println(sumOfSquares(nums));",
              [_n22(xs, str(float(sum(x * x for x in xs)))) for xs in _NS22P],
              ["Convert once per element, then multiply.",
               "`sum += item.doubleValue() * item.doubleValue();`",
               "Squares of negatives are positive, which case three checks.",
               "The result is a `double`, so it prints with `.0`."]),

        _p22b("j22-pc-both", "One method, two element types", "Medium",
              "`total` is written for you. Read `n` integers, build a second list of "
              "their halves as `Double`s, then print the total of each list and the "
              "two added together.",
              """
    static <T extends Number> double total(List<T> items) {
        double sum = 0;
        for (T item : items) {
            sum += item.doubleValue();
        }
        return sum;
    }
""",
              _RD_N22
              + "        List<Double> halves = new ArrayList<>();\n"
                "        for (int x : nums) {\n"
                "            halves.add(x / 2.0);\n"
                "        }\n"
                "        System.out.println(total(nums));\n"
                "        System.out.println(total(halves));\n"
                "        System.out.println(total(nums) + total(halves));",
              [_n22(xs, _nl(str(float(sum(xs))), str(sum(x / 2.0 for x in xs)),
                            str(float(sum(xs)) + sum(x / 2.0 for x in xs))))
               for xs in ([3, 1, 2], [5], [-4, -8, -2], [10, 10, 2], [7, 2, 9, 4])],
              ["`List<Double> halves = new ArrayList<>();`",
               "`x / 2.0` is a `double`, which autoboxes into the list.",
               "The same bounded method accepts both lists - `Integer` and `Double` "
               "both extend `Number`.",
               "Three lines, all doubles."]),
    ])


# --- Family D - utilities that modify -----------------------------------------

_P22_D = _jfam(
    "p22-utils", "Utility methods that modify",
    "The real reason generic methods exist.",
    """
A utility that rearranges a list needs no bound at all - it never *inspects* an
element, only moves it:

```java
static <T> void swap(List<T> items, int i, int j) {
    T temp = items.get(i);
    items.set(i, items.get(j));
    items.set(j, temp);
}
```

Three things carry through every exercise in this family:

* **The temporary's type is `T`.** That is the only reason a generic method can
  do this at all; written against `List<Object>` it would not accept a
  `List<String>` (module 23's invariance).
* **Lists are passed by reference.** Module 9's rule: the method receives a copy
  of the *reference*, so modifying the object it points at is visible to the
  caller. Reassigning the parameter would not be.
* **`set` overwrites and returns the old value**; `add(i, x)` inserts and
  shifts. Two different jobs, easily confused.

A method that *returns* a new list rather than modifying its argument is often
the kinder design - and its return type is `List<T>`.
""",
    [
        _p22m("j22-pd-swap", "swap", "Easy",
              "Write `swap`, exchanging two positions of any list in place.",
              """
    static <T> void swap(List<T> items, int i, int j) {
        T temp = items.get(i);
        items.set(i, items.get(j));
        items.set(j, temp);
    }
""",
              _RD_W22
              + "        swap(words, 0, words.size() - 1);\n"
                "        System.out.println(words);",
              [_w22(ws, _jl22([ws[-1]] + ws[1:-1] + [ws[0]]) if len(ws) > 1
                    else _jl22(ws))
               for ws in _WS22P],
              ["`static <T> void swap(List<T> items, int i, int j) {`",
               "Save `items.get(i)` in a `T temp` before overwriting it.",
               "Then `items.set(i, items.get(j));` and `items.set(j, temp);`.",
               "The caller sees the change, because the list is the same object."]),

        _p22m("j22-pd-reverse", "reverse", "Medium",
              "Write `reverse`, reversing any list in place with a two-pointer swap.",
              """
    static <T> void reverse(List<T> items) {
        int left = 0;
        int right = items.size() - 1;
        while (left < right) {
            T temp = items.get(left);
            items.set(left, items.get(right));
            items.set(right, temp);
            left++;
            right--;
        }
    }
""",
              _RD_W22
              + "        reverse(words);\n"
                "        System.out.println(words);",
              [_w22(ws, _jl22(list(reversed(ws)))) for ws in _WS22P],
              ["Module 4's two-pointer reversal, now on a list and for any element "
               "type.",
               "`int left = 0;` and `int right = items.size() - 1;`, closing in while "
               "`left < right`.",
               "The temporary is a `T`.",
               "The loop condition being strict means an odd middle element stays "
               "put."]),

        _p22m("j22-pd-indexof", "indexOfFirst", "Medium",
              "Write `indexOfFirst`, returning the index of the first element equal to "
              "a target, or -1 if there is none.",
              """
    static <T> int indexOfFirst(List<T> items, T target) {
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).equals(target)) {
                return i;
            }
        }
        return -1;
    }
""",
              _RD_W22
              + "        String q = sc.next();\n"
                "        System.out.println(indexOfFirst(words, q));",
              [_wq22(ws, q, ws.index(q) if q in ws else -1)
               for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                               (["x", "yy", "zzz"], "zzz"), (["pear", "fig"], "fig"),
                               (["a", "b", "c"], "d"))],
              ["An index loop, because the index is the answer.",
               "`static <T> int indexOfFirst(List<T> items, T target) {`",
               "Return as soon as a match is found - that is what makes it the FIRST.",
               "`return -1;` after the loop, for the absent case."]),

        _p22m("j22-pd-rotate", "rotateLeft", "Medium",
              "Write `rotateLeft`, moving the first element of a list to the end, in "
              "place.",
              """
    static <T> void rotateLeft(List<T> items) {
        T head = items.remove(0);
        items.add(head);
    }
""",
              _RD_W22
              + "        rotateLeft(words);\n"
                "        System.out.println(words);",
              [_w22(ws, _jl22(list(ws[1:]) + [ws[0]])) for ws in _WS22P],
              ["`remove(0)` returns what it removed - keep it in a `T`.",
               "`static <T> void rotateLeft(List<T> items) {`",
               "Then `items.add(head);` appends it.",
               "A one-element list is removed and re-added, ending up unchanged."]),

        _p22m("j22-pd-twice", "twice", "Hard",
              "Write `twice`, returning a NEW list in which every element of the "
              "original appears twice in a row. The original must be left alone.",
              """
    static <T> List<T> twice(List<T> items) {
        List<T> out = new ArrayList<>();
        for (T item : items) {
            out.add(item);
            out.add(item);
        }
        return out;
    }
""",
              _RD_W22
              + "        List<String> doubled = twice(words);\n"
                "        System.out.println(doubled);\n"
                "        System.out.println(words);",
              [_w22(ws, _nl(_jl22([w for w in ws for _ in (0, 1)]), _jl22(ws)))
               for ws in _WS22P],
              ["The return type is a parameterized type built from the method's own "
               "parameter: `List<T>`.",
               "`static <T> List<T> twice(List<T> items) {`",
               "Build a new `ArrayList<>()` and add each element twice.",
               "Never touch `items`, so the second printed line shows the original "
               "unchanged.",
               "`main` assigns the result to a `List<String>`, which works because `T` "
               "was inferred as `String`."]),
    ])


# --- Family E - bounds on types ----------------------------------------------

_RANGE22 = """
class Range<T extends Comparable<T>> {
    private final T low;
    private final T high;

    Range(T low, T high) {
        this.low = low;
        this.high = high;
    }

    boolean contains(T value) {
        return low.compareTo(value) <= 0 && high.compareTo(value) >= 0;
    }

    @Override
    public String toString() {
        return low + ".." + high;
    }
}
"""

_CONTAINER22 = """
interface Container<T> {
    void put(T item);

    T get(int i);

    int size();
}

class ListContainer<T> implements Container<T> {
    private final List<T> items = new ArrayList<>();

    @Override
    public void put(T item) {
        items.add(item);
    }

    @Override
    public T get(int i) {
        return items.get(i);
    }

    @Override
    public int size() {
        return items.size();
    }
}
"""

_MINMAX22 = """
class MinMax<T extends Comparable<T>> {
    private T low;
    private T high;

    void accept(T value) {
        if (low == null || value.compareTo(low) < 0) {
            low = value;
        }
        if (high == null || value.compareTo(high) > 0) {
            high = value;
        }
    }

    T getLow() {
        return low;
    }

    T getHigh() {
        return high;
    }
}
"""

_P22_E = _jfam(
    "p22-types", "Bounds on classes, and generic interfaces",
    "The same two ideas, moved from a method onto a type.",
    """
A class carries a bound in exactly the same syntax, and it is checked wherever
the class is parameterized:

```java
class Range<T extends Comparable<T>> { ... }
new Range<>(1, 10);        // fine
new Range<>("ada", "zed"); // fine
// Range<Scanner> — rejected at the declaration, not deep inside a method
```

Interfaces are generic the same way, and a class implementing one has a choice:

```java
class ListContainer<T> implements Container<T>    // stays generic
class WordContainer  implements Container<String> // fixes T to String
```

Two rules from earlier modules still apply, unchanged:

* the implementing methods must be **`public`** - an override may not narrow
  access (module 14);
* nothing inside a generic class may be **`static`** and mention `T` (module
  21).

The `null` comparisons in `MinMax` below are the standard "no value yet" idiom;
`==` is right there, because it is a reference comparison against `null` rather
than a value comparison.
""",
    [
        _p22t("j22-pe-range", "Use a bounded class", "Easy",
              "The `Range` class is written. Read a low, a high and a query integer, "
              "then print the range and whether it contains the query.",
              _RANGE22,
              """
        int lo = sc.nextInt();
        int hi = sc.nextInt();
        int q = sc.nextInt();
        Range<Integer> r = new Range<>(lo, hi);
        System.out.println(r);
        System.out.println(r.contains(q));
""",
              [_case(f"{lo} {hi} {q}", _nl(f"{lo}..{hi}", _jbool(lo <= q <= hi)))
               for (lo, hi, q) in ((1, 10, 5), (1, 10, 10), (0, 3, 4), (-5, -1, -3),
                                   (2, 2, 2))],
              ["`Range<Integer>` satisfies the bound, because `Integer` implements "
               "`Comparable<Integer>`.",
               "The diamond infers the type argument: `new Range<>(lo, hi)`.",
               "Printing the range uses its `toString`, which gives `low..high`.",
               "`contains` prints as `true` or `false`; the bounds are inclusive."]),

        _p22t("j22-pe-words", "The same class, another type", "Easy",
              "Using the same `Range` class, read a low word, a high word and a query "
              "word, and print the range and whether it contains the query in "
              "dictionary order.",
              _RANGE22,
              """
        String lo = sc.next();
        String hi = sc.next();
        String q = sc.next();
        Range<String> r = new Range<>(lo, hi);
        System.out.println(r);
        System.out.println(r.contains(q));
""",
              [_case(f"{lo} {hi} {q}", _nl(f"{lo}..{hi}", _jbool(lo <= q <= hi)))
               for (lo, hi, q) in (("ada", "zed", "moss"), ("bo", "cy", "zed"),
                                   ("a", "b", "a"), ("mid", "mid", "mid"),
                                   ("apple", "pear", "fig"))],
              ["One class, a second parameterization - no new code at all.",
               "`Range<String> r = new Range<>(lo, hi);`",
               "`String` implements `Comparable<String>`, so the bound is satisfied.",
               "Dictionary order is what `compareTo` gives you for Strings."]),

        _p22c("j22-pe-writerange", "Write Range", "Medium",
              "Write `Range<T extends Comparable<T>>`: two private final fields, a "
              "two-argument constructor, `boolean contains(T)` (inclusive at both "
              "ends), and a `toString()` printing `low..high`.",
              _RANGE22,
              """
        int lo = sc.nextInt();
        int hi = sc.nextInt();
        int q = sc.nextInt();
        Range<Integer> r = new Range<>(lo, hi);
        System.out.println(r);
        System.out.println(r.contains(q));
        System.out.println(r.contains(lo));
""",
              [_case(f"{lo} {hi} {q}",
                     _nl(f"{lo}..{hi}", _jbool(lo <= q <= hi), "true"))
               for (lo, hi, q) in ((1, 10, 5), (1, 10, 10), (0, 3, 4), (-5, -1, -3),
                                   (2, 2, 2))],
              ["The class header carries the bound: "
               "`class Range<T extends Comparable<T>> {`.",
               "Without it, `low.compareTo(value)` would not compile.",
               "Inclusive means `low.compareTo(value) <= 0 && "
               "high.compareTo(value) >= 0`.",
               "`toString` returns `low + \"..\" + high;`.",
               "The last printed line checks that the low end is inside its own "
               "range."]),

        _p22t("j22-pe-container", "Use a generic interface", "Medium",
              "`Container<T>` and `ListContainer<T>` are written. Read `n` words into "
              "one, declaring the variable as the INTERFACE, then print the size, the "
              "first element and the last.",
              _CONTAINER22,
              _RD_W22
              + "        Container<String> box = new ListContainer<>();\n"
                "        for (String w : words) {\n"
                "            box.put(w);\n"
                "        }\n"
                "        System.out.println(box.size());\n"
                "        System.out.println(box.get(0));\n"
                "        System.out.println(box.get(box.size() - 1));",
              [_w22(ws, _nl(len(ws), ws[0], ws[-1])) for ws in _WS22P],
              ["Declare the interface, construct the implementation - module 14's rule "
               "with a type argument attached.",
               "`Container<String> box = new ListContainer<>();`",
               "The diamond infers `String` from the left-hand side.",
               "`box.get(0)` comes back as a `String`, so no cast is needed."]),

        _p22c("j22-pe-minmax", "Write MinMax", "Hard",
              "Write `MinMax<T extends Comparable<T>>`, which remembers the smallest "
              "and largest value it has been shown. `accept(T)` takes one value, and "
              "`getLow()` / `getHigh()` return the extremes. Before anything has been "
              "accepted both fields are `null`.",
              _MINMAX22,
              _RD_W22
              + "        MinMax<String> mm = new MinMax<>();\n"
                "        for (String w : words) {\n"
                "            mm.accept(w);\n"
                "        }\n"
                "        System.out.println(mm.getLow());\n"
                "        System.out.println(mm.getHigh());",
              [_w22(ws, _nl(min(ws), max(ws))) for ws in _WS22P],
              ["The class needs the `Comparable` bound, because `accept` compares.",
               "Two private fields of type `T`, neither of them final.",
               "`accept` handles the empty case with a null check: "
               "`if (low == null || value.compareTo(low) < 0)`.",
               "`==` against `null` is a reference comparison, which is exactly right "
               "here.",
               "Both getters return `T`, so `main` needs no casts.",
               "A one-word input makes the low and the high the same word."]),
    ])


_PRACTICE[22] = [_P22_A, _P22_B, _P22_C, _P22_D, _P22_E]
