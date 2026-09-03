# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 24 practice - erasure, and what it costs.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[24]`.
#
# The last module of the course as it currently ships, so everything is fair
# game: collections, Comparable/Comparator as NAMED classes, generic classes and
# methods, bounds and wildcards.
#
# Each family drills one consequence of the single fact that type arguments do
# not survive compilation: what you can still observe at run time, what erasure
# forbids outright, the unchecked cast and where it detonates, the signatures
# that collide, and the `Class<T>` token that hands the type back.
#
# As in the module file, nothing here ever prints an exception MESSAGE - only
# `getClass().getSimpleName()`, which is stable across JDK versions.
# ---------------------------------------------------------------------------


def _p24prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


def _p24tprog(types, helpers, body):
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


def _p24m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD; main is given."""
    return _jch(eid, title, difficulty, prompt, _p24prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p24b(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write main's BODY; the method is given."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p24prog(helpers, body),
                body, tests, hints)


def _p24s(eid, title, difficulty, prompt, body, tests, hints):
    """No helper methods at all - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(body), body, tests, hints)


def _p24t(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """A top-level type is given too; write main's BODY."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _p24tprog(types, helpers, body),
                body, tests, hints)


def _p24c(eid, title, difficulty, prompt, types, helpers, body, tests, hints):
    """Write the top-level TYPE(s); main is given."""
    return _jch(eid, title, difficulty, prompt, _p24tprog(types, helpers, body),
                types.strip("\n"), tests, hints)


_RD_W24P = ("        int n = sc.nextInt();\n"
            "        List<String> words = new ArrayList<>();\n"
            "        for (int i = 0; i < n; i++) {\n"
            "            words.add(sc.next());\n"
            "        }\n")

_RD_N24P = ("        int m = sc.nextInt();\n"
            "        List<Integer> nums = new ArrayList<>();\n"
            "        for (int i = 0; i < m; i++) {\n"
            "            nums.add(sc.nextInt());\n"
            "        }\n")

_RD_WN24P = _RD_W24P + _RD_N24P

_MIX24P = ("        List<Object> mixed = new ArrayList<>();\n"
           "        for (String w : words) {\n"
           "            mixed.add(w);\n"
           "        }\n"
           "        for (int x : nums) {\n"
           "            mixed.add(x);\n"
           "        }\n")

_WS24P = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
          ["alpha", "beta", "gamma", "d"])

_NS24P = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

_WX24P = (("ada", 3), ("solo", 5), ("zzz", -4), ("pear", 10), ("generics", 7))


def _w24p(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n24p(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wn24p(ws, xs, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                            " ".join(str(x) for x in xs)]), out)


def _jl24p(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


_PAIRS24 = tuple(zip(_WS24P, _NS24P))


# --- Family A - what survives to run time ------------------------------------

_P24_A = _jfam(
    "p24-runtime", "Erasure, as seen from run time",
    "The type argument is gone; the class and the objects are not.",
    """
```java
List<String> words = new ArrayList<>();
List<Integer> nums  = new ArrayList<>();
words.getClass() == nums.getClass()     // true
```

After compilation there is one `ArrayList` class, and both lists are instances
of it. The type argument was checked and then discarded.

Two things do survive, and they are easy to confuse with the type argument:

* **the implementation class** - `ArrayList` versus `LinkedList` is still
  visible, because that is the object's real class;
* **the elements themselves** - a `String` in the list still knows it is a
  `String`. Erasure forgot what the *container* holds, not what each object
  *is*.

And a raw `List` is simply what a `List<String>` erases to - which is why its
`get` returns `Object` and you have to write the cast the compiler would
otherwise have written for you.
""",
    [
        _p24m("j24-pa-same", "sameClass", "Intro",
              "Write `sameClass`, which reports whether two lists have the same run-time "
              "class. `main` compares two lists with different element types, then two "
              "with different implementations.",
              """
    static boolean sameClass(List<?> a, List<?> b) {
        return a.getClass() == b.getClass();
    }
""",
              _RD_WN24P
              + "        List<String> linked = new LinkedList<>();\n"
                "        for (String w : words) {\n"
                "            linked.add(w);\n"
                "        }\n"
                "        System.out.println(sameClass(words, nums));\n"
                "        System.out.println(sameClass(words, linked));",
              [_wn24p(ws, xs, _nl("true", "false")) for (ws, xs) in _PAIRS24],
              ["Both parameters accept any list at all, so both are `List<?>`.",
               "`return a.getClass() == b.getClass();` - two class objects compared by "
               "reference.",
               "`List<String>` and `List<Integer>` are the same class: the type "
               "argument is gone.",
               "`ArrayList` and `LinkedList` are not: the implementation is real and "
               "survives."]),

        _p24m("j24-pa-name", "erasedName", "Intro",
              "Write `erasedName`, returning the short run-time class name of any list. "
              "`main` calls it on a list of words and a list of numbers.",
              """
    static String erasedName(List<?> items) {
        return items.getClass().getSimpleName();
    }
""",
              _RD_WN24P
              + "        System.out.println(erasedName(words));\n"
                "        System.out.println(erasedName(nums));\n"
                "        System.out.println(words.size() + nums.size());",
              [_wn24p(ws, xs, _nl("ArrayList", "ArrayList", len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["`getSimpleName()` drops the package; `getName()` would print "
               "`java.util.ArrayList`.",
               "`static String erasedName(List<?> items) {`",
               "Both answers are the same, and neither mentions String or Integer.",
               "The third line is just the two sizes added."]),

        _p24s("j24-pa-rawcast", "The cast you have to write", "Easy",
              "A raw `List` is the erased form of `List<String>`, so its `get` returns "
              "`Object`. Read one word, put it in a raw list, take it back out with an "
              "explicit cast, then print it and its length.",
              "        String word = sc.next();\n"
              "        List raw = new ArrayList();\n"
              "        raw.add(word);\n"
              "        String first = (String) raw.get(0);\n"
              "        System.out.println(first);\n"
              "        System.out.println(first.length());",
              [_case(w, _nl(w, len(w))) for w in
               ("ada", "solo", "zzz", "pear", "generics")],
              ["`List raw = new ArrayList();` - no type argument anywhere.",
               "`raw.get(0)` is an `Object`, so it will not assign to a `String`.",
               "`String first = (String) raw.get(0);`",
               "That cast is exactly what `List<String>` would have inserted for you.",
               "Two printed lines: the word, then its length."]),

        _p24m("j24-pa-kind", "kindOfFirst", "Easy",
              "Erasure forgot what the list holds, but each element still knows what it "
              "is. Write `kindOfFirst`, returning the run-time class name of a list's "
              "first element.",
              """
    static String kindOfFirst(List<?> items) {
        return items.get(0).getClass().getSimpleName();
    }
""",
              _RD_WN24P
              + "        System.out.println(kindOfFirst(words));\n"
                "        System.out.println(kindOfFirst(nums));",
              [_wn24p(ws, xs, _nl("String", "Integer")) for (ws, xs) in _PAIRS24],
              ["A `List<?>` gives its elements back as `Object` - which is enough, "
               "because `getClass()` is declared on `Object`.",
               "`items.get(0).getClass().getSimpleName()`",
               "The list cannot say what it holds; the element can say what it is.",
               "The numbers were autoboxed on the way in, so the answer is `Integer`, "
               "not `int`."]),

        _p24b("j24-pa-mixed", "One class for all of them", "Medium",
              "`erasedName` is written. Build a `List<Object>` holding every word and "
              "then every number, and print its class name, whether that class is the "
              "same one the `List<String>` has, and its size.",
              """
    static String erasedName(List<?> items) {
        return items.getClass().getSimpleName();
    }
""",
              _RD_WN24P + _MIX24P
              + "        System.out.println(erasedName(mixed));\n"
                "        System.out.println(mixed.getClass() == words.getClass());\n"
                "        System.out.println(mixed.size());",
              [_wn24p(ws, xs, _nl("ArrayList", "true", len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["`List<Object>`, `List<String>` and `List<Integer>` are three names for "
               "one run-time class.",
               "Add the words with an enhanced `for`, then the numbers - autoboxing "
               "turns each `int` into an `Integer`.",
               "`mixed.getClass() == words.getClass()` is `true`, which is the whole "
               "point.",
               "Three printed lines."]),
    ])


# --- Family B - the moves erasure forbids ------------------------------------

_P24_B = _jfam(
    "p24-illegal", "What erasure forbids, and what you write instead",
    "`new T()`, `new T[]`, `static T`, `instanceof T` - and the four replacements.",
    """
Each of these needs the type argument to exist at run time, and it does not:

| Illegal | Write instead |
|---|---|
| `new T()` | take the value in as a parameter |
| `new T[n]` | `new Object[n]`, plus a cast on the way out |
| `static T last;` | `static Object last;` |
| `x instanceof List<String>` | `x instanceof List<?>` |

The array workaround deserves its label rather than an apology - it is what
`ArrayList` itself does:

```java
private Object[] items = new Object[capacity];

@SuppressWarnings("unchecked")
T get(int index) {
    return (T) items[index];      // sound: add(T) is the only way in
}
```

And the static one is worth saying out loud: there is **one** class behind
`Cell<String>` and `Cell<Integer>` alike, so a static field is shared by both.
That is not a restriction on top of erasure, it *is* erasure.
""",
    [
        _p24m("j24-pb-instanceof", "shape", "Intro",
              "Write `shape`, returning `\"list\"` when its argument is a list and "
              "`\"value\"` otherwise - using the only `instanceof` form erasure allows.",
              """
    static String shape(Object item) {
        if (item instanceof List<?>) {
            return "list";
        }
        return "value";
    }
""",
              _RD_W24P
              + "        System.out.println(shape(words));\n"
                "        System.out.println(shape(words.get(0)));\n"
                "        System.out.println(words.size());",
              [_w24p(ws, _nl("list", "value", len(ws))) for ws in _WS24P],
              ["`item instanceof List<String>` does not compile - there is nothing left "
               "to test.",
               "`if (item instanceof List<?>) {`",
               "The wildcard asks only 'is this a List at all?', which the run time can "
               "answer.",
               "Three printed lines."]),

        _p24c("j24-pb-slot", "Slot", "Easy",
              "Write `Slot<T>`: a generic holder with a private `T` field, a constructor "
              "that takes the value (because `new T()` is impossible) and a `get()`. "
              "`main` builds one of Strings and one of Integers.",
              """
class Slot<T> {
    private T value;

    Slot(T value) {
        this.value = value;
    }

    T get() {
        return value;
    }
}
""", "",
              "        String word = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        Slot<String> a = new Slot<>(word);\n"
              "        Slot<Integer> b = new Slot<>(n);\n"
              "        System.out.println(a.get());\n"
              "        System.out.println(b.get());",
              [_case(f"{w}\n{x}", _nl(w, x)) for (w, x) in _WX24P],
              ["The class cannot build a `T`, so it has to be handed one: "
               "`Slot(T value)`.",
               "`private T value;` and `T get() { return value; }`.",
               "Only `Main` may be `public`; `Slot` is package-private.",
               "`new Slot<>(n)` autoboxes the `int` into an `Integer`.",
               "Two printed lines."]),

        _p24c("j24-pb-buffer", "Buffer", "Medium",
              "Write `Buffer<T>`: a growable-free holder backed by an `Object[]` (because "
              "`new T[]` is illegal), with `add(T)`, a cast-on-read `get(int)` and "
              "`size()`. `main` fills one with words.",
              """
class Buffer<T> {
    private Object[] items;
    private int count;

    Buffer(int capacity) {
        this.items = new Object[capacity];
    }

    void add(T item) {
        items[count] = item;
        count++;
    }

    @SuppressWarnings("unchecked")
    T get(int index) {
        return (T) items[index];
    }

    int size() {
        return count;
    }
}
""", "",
              "        int n = sc.nextInt();\n"
              "        Buffer<String> buffer = new Buffer<>(n);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            buffer.add(sc.next());\n"
              "        }\n"
              "        System.out.println(buffer.get(0));\n"
              "        System.out.println(buffer.get(buffer.size() - 1));\n"
              "        System.out.println(buffer.size());",
              [_w24p(ws, _nl(ws[0], ws[-1], len(ws))) for ws in _WS24P],
              ["`new T[capacity]` is *generic array creation* - the storage has to be "
               "`Object[]`.",
               "`add(T item)` stores into it and bumps the count.",
               "`get` casts back: `return (T) items[index];`, which is unchecked.",
               "Annotate `get` with `@SuppressWarnings(\"unchecked\")` - the cast is "
               "sound because `add(T)` is the only door in.",
               "For a one-word list the first and last elements are the same."]),

        _p24c("j24-pb-cell", "Cell", "Medium",
              "Write `Cell<T>`: a holder that also remembers the last value ANY cell was "
              "built with. That memory has to be `static Object`, never `static T` - "
              "there is one class behind every parameterization, so one field.",
              """
class Cell<T> {
    private T value;
    private static Object last;

    Cell(T value) {
        this.value = value;
        last = value;
    }

    T get() {
        return value;
    }

    static Object lastSeen() {
        return last;
    }
}
""", "",
              "        String word = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        Cell<String> first = new Cell<>(word);\n"
              "        Cell<Integer> second = new Cell<>(n);\n"
              "        System.out.println(first.get());\n"
              "        System.out.println(second.get());\n"
              "        System.out.println(Cell.lastSeen());",
              [_case(f"{w}\n{x}", _nl(w, x, x)) for (w, x) in _WX24P],
              ["`private static T last;` does not compile: *non-static type variable T "
               "cannot be referenced from a static context*.",
               "Both the field and `lastSeen()` widen to `Object`.",
               "The constructor sets the instance field AND the shared static one.",
               "The `Cell<Integer>` is built second, so it is what `lastSeen()` reports "
               "- the `Cell<String>` wrote to the very same field.",
               "`Cell.lastSeen()` is called on the class, with no type argument."]),

        _p24t("j24-pb-fill", "Filling the buffer", "Easy",
              "`Buffer<T>` is written for you, `Object[]` storage and all. Read the "
              "words into a `Buffer<String>` and print the first element, the last "
              "element and the size.",
              """
class Buffer<T> {
    private Object[] items = new Object[16];
    private int count;

    void add(T item) {
        items[count] = item;
        count++;
    }

    @SuppressWarnings("unchecked")
    T get(int index) {
        return (T) items[index];
    }

    int size() {
        return count;
    }
}
""", "",
              "        int n = sc.nextInt();\n"
              "        Buffer<String> buffer = new Buffer<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            buffer.add(sc.next());\n"
              "        }\n"
              "        System.out.println(buffer.get(0));\n"
              "        System.out.println(buffer.get(buffer.size() - 1));\n"
              "        System.out.println(buffer.size());",
              [_w24p(ws, _nl(ws[0], ws[-1], len(ws))) for ws in _WS24P],
              ["`Buffer<String> buffer = new Buffer<>();` - the diamond infers the type "
               "argument.",
               "`buffer.add(sc.next())` inside the counted loop.",
               "`get` returns a `T`, which here is a `String`, so no cast is needed at "
               "the call site.",
               "The last index is `buffer.size() - 1`.",
               "Three printed lines."]),
    ])


# --- Family C - unchecked casts and heap pollution ---------------------------

_P24_C = _jfam(
    "p24-unchecked", "Unchecked casts, and where they detonate",
    "A cast to a generic type is a promise; the crash arrives somewhere else.",
    """
```java
List<String> words = (List<String>) unknown;   // warning: unchecked cast
String first = words.get(0);                   // ClassCastException HERE
```

The cast itself does **nothing** at run time - there is no type argument left to
check. It is a promise. If the promise is false, the failure surfaces at the
first place the compiler inserted a cast of its own, which can be a long way
away. The state in between is **heap pollution**.

Three tools, in descending order of how much they ask you to trust yourself:

* **a checked cast per element** - `instanceof` then cast. Costs a loop, buys
  certainty, needs no annotation at all.
* **`@SuppressWarnings("unchecked")`** - your signature that the invariant holds.
  Smallest possible scope, never a whole class.
* **`@SafeVarargs`** - the same signature for a generic varargs method, and only
  legal on `static`, `final` or `private` methods, because an override could
  break the promise you signed.
""",
    [
        _p24m("j24-pc-suppress", "asWords", "Easy",
              "Write `asWords`, which casts a `List<?>` back to a `List<String>` and "
              "returns it. The compiler cannot check that, so the method has to sign for "
              "it with the right annotation.",
              """
    @SuppressWarnings("unchecked")
    static List<String> asWords(List<?> items) {
        return (List<String>) items;
    }
""",
              _RD_W24P
              + "        List<?> unknown = words;\n"
                "        List<String> back = asWords(unknown);\n"
                "        System.out.println(back.get(0));\n"
                "        System.out.println(back.size());",
              [_w24p(ws, _nl(ws[0], len(ws))) for ws in _WS24P],
              ["The body is one line: `return (List<String>) items;`.",
               "The warning is *unchecked cast*, so the annotation is "
               "`@SuppressWarnings(\"unchecked\")`.",
               "Put it on the method, which is the smallest scope containing the cast.",
               "Here the promise is true - `main` built the list out of Strings itself.",
               "Two printed lines."]),

        _p24s("j24-pc-raw", "Poisoning a list", "Medium",
              "Read a word and a number into a RAW list, hand it to a `List<String>` "
              "variable, then loop over it inside a `try`. Print each word as it comes "
              "out, print the exception's simple name when the loop fails, and finally "
              "print the list's size.",
              "        String word = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        List raw = new ArrayList();\n"
              "        raw.add(word);\n"
              "        raw.add(Integer.valueOf(n));\n"
              "        List<String> words = raw;\n"
              "        try {\n"
              "            for (String w : words) {\n"
              "                System.out.println(w);\n"
              "            }\n"
              "        } catch (ClassCastException e) {\n"
              "            System.out.println(e.getClass().getSimpleName());\n"
              "        }\n"
              "        System.out.println(words.size());",
              [_case(f"{w}\n{x}", _nl(w, "ClassCastException", 2))
               for (w, x) in _WX24P],
              ["A raw `List` accepts anything; `List<String> words = raw;` is an "
               "unchecked conversion and does not throw.",
               "The enhanced `for` casts each element to `String` - that is where it "
               "breaks.",
               "Catch `ClassCastException` and print `e.getClass().getSimpleName()`, "
               "never the message.",
               "The first word prints before the failure, so the list was already "
               "half-consumed.",
               "The size is still 2 - the list itself is intact, it is just wrong."]),

        _p24m("j24-pc-safe", "countAll", "Medium",
              "Write `countAll`, a varargs method that adds up the sizes of any number "
              "of lists. `List<T>...` compiles to an array of a type that cannot exist, "
              "so the method must vouch for itself with the right annotation.",
              """
    @SafeVarargs
    static <T> int countAll(List<T>... lists) {
        int total = 0;
        for (List<T> list : lists) {
            total += list.size();
        }
        return total;
    }
""",
              _RD_W24P
              + "        List<String> shouts = new ArrayList<>();\n"
                "        for (String w : words) {\n"
                "            shouts.add(w.toUpperCase());\n"
                "        }\n"
                "        System.out.println(countAll(words, shouts));\n"
                "        System.out.println(shouts.get(0));",
              [_w24p(ws, _nl(2 * len(ws), ws[0].upper())) for ws in _WS24P],
              ["The warning is *possible heap pollution from parameterized vararg type*.",
               "`@SafeVarargs` - legal here because the method is `static`.",
               "The claim being signed: the method only reads the array, never stores "
               "into it and never lets it escape.",
               "Loop the varargs parameter like any array and add up `list.size()`.",
               "Both arguments are `List<String>`, so the total is twice the word "
               "count."]),

        _p24m("j24-pc-checked", "onlyWords", "Medium",
              "Write `onlyWords`, the honest alternative to one unchecked cast: check "
              "each element and keep the Strings, returning a new `List<String>`.",
              """
    static List<String> onlyWords(List<?> items) {
        List<String> out = new ArrayList<>();
        for (Object item : items) {
            if (item instanceof String) {
                out.add((String) item);
            }
        }
        return out;
    }
""",
              "        String word = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        List<Object> mixed = new ArrayList<>();\n"
              "        mixed.add(word);\n"
              "        mixed.add(n);\n"
              "        System.out.println(onlyWords(mixed));\n"
              "        System.out.println(onlyWords(mixed).size());\n"
              "        System.out.println(mixed.size());",
              [_case(f"{w}\n{x}", _nl(f"[{w}]", 1, 2)) for (w, x) in _WX24P],
              ["The parameter is `List<?>`, so any list at all can be filtered.",
               "Each element arrives as an `Object`; `instanceof String` is a real "
               "run-time check.",
               "`out.add((String) item);` inside the guard - a CHECKED cast.",
               "No annotation is needed anywhere, which is exactly the difference from "
               "an unchecked cast.",
               "The number is dropped, so the result is one element shorter than the "
               "input."]),

        _p24b("j24-pc-clean", "Cleaning up after a raw list", "Hard",
              "`onlyWords` is written. Build a RAW list holding the word, the number and "
              "the word again, filter it into a real `List<String>`, then print that "
              "list, its size, and the raw list's size.",
              """
    static List<String> onlyWords(List<?> items) {
        List<String> out = new ArrayList<>();
        for (Object item : items) {
            if (item instanceof String) {
                out.add((String) item);
            }
        }
        return out;
    }
""",
              "        String word = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        List raw = new ArrayList();\n"
              "        raw.add(word);\n"
              "        raw.add(Integer.valueOf(n));\n"
              "        raw.add(word);\n"
              "        List<String> kept = onlyWords(raw);\n"
              "        System.out.println(kept);\n"
              "        System.out.println(kept.size());\n"
              "        System.out.println(raw.size());",
              [_case(f"{w}\n{x}", _nl(f"[{w}, {w}]", 2, 3)) for (w, x) in _WX24P],
              ["`List raw = new ArrayList();` takes all three values without complaint.",
               "A raw `List` is an acceptable argument for a `List<?>` parameter.",
               "`onlyWords` does the checking, so nothing here needs a suppression.",
               "The word went in twice, so it comes out twice.",
               "The raw list still holds all three - filtering copied rather than "
               "removed."]),
    ])


# --- Family D - erased signatures --------------------------------------------

_P24_D = _jfam(
    "p24-signatures", "Erased signatures, clashes and bridges",
    "Two methods can become one, and one override can become two.",
    """
Erasure rewrites signatures, and two things follow.

**Overloads can collide.** `count(List<String>)` and `count(List<Integer>)` both
erase to `count(List)`, so they are the same method and the class will not
compile. No cast or annotation helps - **use different names**, or one
`count(List<?>)` that serves both.

**Overrides get help.** When a subclass fixes the type argument:

```java
class WordHolder extends Holder<String> {
    void set(String value) { ... }
}
```

the superclass method erased to `set(Object)` while this one is `set(String)` -
different signatures, so it would not override anything. The compiler
synthesizes a **bridge method**:

```java
void set(Object value) { set((String) value); }   // you never wrote this
```

which is why a raw-typed call that slips the wrong type past the compiler throws
`ClassCastException` from a method that is not in your source.
""",
    [
        _p24m("j24-pd-names", "countWords and countNums", "Intro",
              "Write two counting methods, one for a list of words and one for a list of "
              "numbers. They cannot share a name - both parameter types erase to the "
              "same `List`.",
              """
    static int countWords(List<String> items) {
        return items.size();
    }

    static int countNums(List<Integer> items) {
        return items.size();
    }
""",
              _RD_WN24P
              + "        System.out.println(countWords(words));\n"
                "        System.out.println(countNums(nums));",
              [_wn24p(ws, xs, _nl(len(ws), len(xs))) for (ws, xs) in _PAIRS24],
              ["Naming both `count` fails with *name clash: both methods have the same "
               "erasure*.",
               "`countWords(List<String>)` and `countNums(List<Integer>)`.",
               "Each body is a single `return items.size();`.",
               "Two printed lines."]),

        _p24m("j24-pd-any", "countAny", "Easy",
              "The two methods of the last problem exist only because their parameters "
              "differ. Write the single method that replaces both by naming no element "
              "type at all.",
              """
    static int countAny(List<?> items) {
        return items.size();
    }
""",
              _RD_WN24P
              + "        System.out.println(countAny(words));\n"
                "        System.out.println(countAny(nums));\n"
                "        System.out.println(countAny(words) + countAny(nums));",
              [_wn24p(ws, xs, _nl(len(ws), len(xs), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["`List<?>` accepts a list of anything - module 23.",
               "`static int countAny(List<?> items) {`",
               "A `List<Object>` parameter would have rejected both arguments, because "
               "generics are invariant.",
               "One method, both call sites, and no clash to worry about."]),

        _p24t("j24-pd-bridge", "The bridge method throws", "Hard",
              "`Holder<T>` and `WordHolder extends Holder<String>` are given. Set a word "
              "through the typed reference and print what is held; then alias the holder "
              "as a RAW `Holder`, try to set an `Integer` inside a `try`, print the "
              "exception's simple name, and print the held value again.",
              """
class Holder<T> {
    private T value;

    void set(T value) {
        this.value = value;
    }

    T get() {
        return value;
    }
}

class WordHolder extends Holder<String> {
    @Override
    void set(String value) {
        super.set(value.toUpperCase());
    }
}
""", "",
              "        String word = sc.next();\n"
              "        WordHolder holder = new WordHolder();\n"
              "        holder.set(word);\n"
              "        System.out.println(holder.get());\n"
              "        Holder raw = holder;\n"
              "        try {\n"
              "            raw.set(Integer.valueOf(7));\n"
              "            System.out.println(\"accepted\");\n"
              "        } catch (ClassCastException e) {\n"
              "            System.out.println(e.getClass().getSimpleName());\n"
              "        }\n"
              "        System.out.println(holder.get());",
              [_case(w, _nl(w.upper(), "ClassCastException", w.upper()))
               for w in ("ada", "solo", "zzz", "pear", "generics")],
              ["`WordHolder` upper-cases on the way in, so the first line is the word "
               "in capitals.",
               "`Holder raw = holder;` - a raw type, which switches the checking off.",
               "`raw.set(Integer.valueOf(7));` compiles, and lands in the generated "
               "bridge `set(Object)`.",
               "The bridge's `(String)` cast is what throws, so `\"accepted\"` never "
               "prints.",
               "The failed call stored nothing, so the last line matches the first."]),

        _p24t("j24-pd-store", "Filling a generic store", "Medium",
              "`Store<T>` and `WordStore implements Store<String>` are given. Read the "
              "words into a store held through the INTERFACE type, then print how many "
              "it holds and the real class behind the reference.",
              """
interface Store<T> {
    void put(T item);

    int size();
}

class WordStore implements Store<String> {
    private List<String> items = new ArrayList<>();

    @Override
    public void put(String item) {
        items.add(item);
    }

    @Override
    public int size() {
        return items.size();
    }
}
""", "",
              "        int n = sc.nextInt();\n"
              "        Store<String> store = new WordStore();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            store.put(sc.next());\n"
              "        }\n"
              "        System.out.println(store.size());\n"
              "        System.out.println(store.getClass().getSimpleName());",
              [_w24p(ws, _nl(len(ws), "WordStore")) for ws in _WS24P],
              ["Declare the variable as `Store<String>` and construct a `WordStore` - "
               "programming to the interface, from module 14.",
               "`store.put(sc.next())` inside the counted loop.",
               "The call goes through a bridge `put(Object)` the compiler generated.",
               "`getSimpleName()` reports `WordStore`, not `Store` - the reference type "
               "is a compile-time thing."]),

        _p24c("j24-pd-impl", "Store and WordStore", "Hard",
              "Write the generic interface `Store<T>` (a `put(T)` and a `size()`) and a "
              "`WordStore` that implements `Store<String>` over an inner `List<String>`. "
              "`main` fills it through the interface type.",
              """
interface Store<T> {
    void put(T item);

    int size();
}

class WordStore implements Store<String> {
    private List<String> items = new ArrayList<>();

    @Override
    public void put(String item) {
        items.add(item);
    }

    @Override
    public int size() {
        return items.size();
    }
}
""", "",
              "        int n = sc.nextInt();\n"
              "        Store<String> store = new WordStore();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            store.put(sc.next());\n"
              "        }\n"
              "        System.out.println(store.size());\n"
              "        System.out.println(store.getClass().getSimpleName());",
              [_w24p(ws, _nl(len(ws), "WordStore")) for ws in _WS24P],
              ["The interface declares the type parameter: `interface Store<T>`.",
               "`WordStore implements Store<String>` fixes `T` once and for all.",
               "Its overrides must be `public` - an implementation may not reduce an "
               "interface method's visibility.",
               "`put` erases to `put(Object)` in the interface, so the compiler bridges "
               "it to `put(String)`.",
               "Only `Main` may be `public`; the interface and the class are both "
               "package-private."]),
    ])


# --- Family E - Class<T> type tokens -----------------------------------------

_P24_E = _jfam(
    "p24-tokens", "`Class<T>` - handing the type back",
    "If the compiler erased it and you still need it, pass it in as a value.",
    """
```java
static <T> List<T> allOf(List<?> items, Class<T> type) {
    List<T> out = new ArrayList<>();
    for (Object item : items) {
        if (type.isInstance(item)) {
            out.add(type.cast(item));
        }
    }
    return out;
}

allOf(mixed, String.class);      // String.class is a Class<String>, so T = String
```

A **type token** is nothing more than a `Class<T>` passed as an argument. It
carries at run time what erasure removed, and its two useful methods are exactly
the two things erasure took away:

| Impossible | Type token |
|---|---|
| `item instanceof T` | `type.isInstance(item)` |
| `(T) item` | `type.cast(item)` |

And `cast` is *checked* - it throws at the point of the cast rather than leaving
heap pollution behind - so a method built this way needs no
`@SuppressWarnings` at all.
""",
    [
        _p24m("j24-pe-count", "countOf", "Easy",
              "Write `countOf`, which counts how many elements of a list are of a given "
              "type. The type arrives as a value, because erasure means the method "
              "cannot ask `T` anything.",
              """
    static <T> int countOf(List<?> items, Class<T> type) {
        int total = 0;
        for (Object item : items) {
            if (type.isInstance(item)) {
                total++;
            }
        }
        return total;
    }
""",
              _RD_WN24P + _MIX24P
              + "        System.out.println(countOf(mixed, String.class));\n"
                "        System.out.println(countOf(mixed, Integer.class));\n"
                "        System.out.println(mixed.size());",
              [_wn24p(ws, xs, _nl(len(ws), len(xs), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["`static <T> int countOf(List<?> items, Class<T> type) {`",
               "`item instanceof T` is illegal; `type.isInstance(item)` is the run-time "
               "equivalent.",
               "Elements come out of a `List<?>` as `Object`, which is all `isInstance` "
               "needs.",
               "The mixed list holds every word and then every number."]),

        _p24m("j24-pe-all", "allOf", "Medium",
              "Write `allOf`, collecting every element of a given type into a properly "
              "typed `List<T>` - using the type token's own checked cast, so no "
              "suppression is needed anywhere.",
              """
    static <T> List<T> allOf(List<?> items, Class<T> type) {
        List<T> out = new ArrayList<>();
        for (Object item : items) {
            if (type.isInstance(item)) {
                out.add(type.cast(item));
            }
        }
        return out;
    }
""",
              _RD_WN24P + _MIX24P
              + "        System.out.println(allOf(mixed, String.class));\n"
                "        System.out.println(allOf(mixed, Integer.class));\n"
                "        System.out.println(mixed.size());",
              [_wn24p(ws, xs, _nl(_jl24p(ws), _jl24p(xs), len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["The return type is `List<T>`, which the `Class<T>` parameter makes "
               "honest.",
               "Guard with `type.isInstance(item)`, then `out.add(type.cast(item));`.",
               "`cast` returns a `T`, so it goes straight into the `List<T>` with no "
               "cast of your own.",
               "The elements keep the order they were added in.",
               "Nothing here is unchecked, so there is no annotation to write."]),

        _p24m("j24-pe-first", "firstOf", "Medium",
              "Write `firstOf`, returning the first element of a list that is of a given "
              "type, or `null` if there is none. `main` adds the numbers first and the "
              "words after.",
              """
    static <T> T firstOf(List<?> items, Class<T> type) {
        for (Object item : items) {
            if (type.isInstance(item)) {
                return type.cast(item);
            }
        }
        return null;
    }
""",
              _RD_WN24P
              + "        List<Object> mixed = new ArrayList<>();\n"
                "        for (int x : nums) {\n"
                "            mixed.add(x);\n"
                "        }\n"
                "        for (String w : words) {\n"
                "            mixed.add(w);\n"
                "        }\n"
                "        System.out.println(firstOf(mixed, String.class));\n"
                "        System.out.println(firstOf(mixed, Integer.class));\n"
                "        System.out.println(mixed.size());",
              [_wn24p(ws, xs, _nl(ws[0], xs[0], len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["The return type is a bare `T` - this is the shape a type token exists "
               "for.",
               "Return `type.cast(item)` from inside the loop as soon as the guard "
               "passes.",
               "`return null;` after the loop; `null` is a legal value of every "
               "reference type.",
               "The numbers were added first, but the first STRING is still the first "
               "word.",
               "Three printed lines."]),

        _p24b("j24-pe-use", "Splitting a mixed list", "Medium",
              "`allOf` is written. Build the mixed list, split it into a `List<String>` "
              "and a `List<Integer>`, and print each one's size and then the first word.",
              """
    static <T> List<T> allOf(List<?> items, Class<T> type) {
        List<T> out = new ArrayList<>();
        for (Object item : items) {
            if (type.isInstance(item)) {
                out.add(type.cast(item));
            }
        }
        return out;
    }
""",
              _RD_WN24P + _MIX24P
              + "        List<String> justWords = allOf(mixed, String.class);\n"
                "        List<Integer> justNums = allOf(mixed, Integer.class);\n"
                "        System.out.println(justWords.size());\n"
                "        System.out.println(justNums.size());\n"
                "        System.out.println(justWords.get(0));",
              [_wn24p(ws, xs, _nl(len(ws), len(xs), ws[0]))
               for (ws, xs) in _PAIRS24],
              ["`allOf(mixed, String.class)` returns a real `List<String>` - no cast at "
               "the call site.",
               "`String.class` and `Integer.class` are the two type tokens.",
               "The results are properly typed, so `justWords.get(0)` is a `String` "
               "already.",
               "Three printed lines."]),

        _p24b("j24-pe-audit", "The type-token report", "Hard",
              "`erasedName`, `countOf` and `allOf` are all written. Build the mixed list "
              "and print five lines: its run-time class name, how many Strings it holds, "
              "how many Integers, the Strings themselves, and its size.",
              """
    static String erasedName(List<?> items) {
        return items.getClass().getSimpleName();
    }

    static <T> int countOf(List<?> items, Class<T> type) {
        int total = 0;
        for (Object item : items) {
            if (type.isInstance(item)) {
                total++;
            }
        }
        return total;
    }

    static <T> List<T> allOf(List<?> items, Class<T> type) {
        List<T> out = new ArrayList<>();
        for (Object item : items) {
            if (type.isInstance(item)) {
                out.add(type.cast(item));
            }
        }
        return out;
    }
""",
              _RD_WN24P + _MIX24P
              + "        System.out.println(erasedName(mixed));\n"
                "        System.out.println(countOf(mixed, String.class));\n"
                "        System.out.println(countOf(mixed, Integer.class));\n"
                "        System.out.println(allOf(mixed, String.class));\n"
                "        System.out.println(mixed.size());",
              [_wn24p(ws, xs, _nl("ArrayList", len(ws), len(xs), _jl24p(ws),
                                  len(ws) + len(xs)))
               for (ws, xs) in _PAIRS24],
              ["`erasedName(mixed)` says `ArrayList` - the element type is long gone.",
               "The two `countOf` calls differ only in their type token.",
               "`allOf(mixed, String.class)` prints as a list, in insertion order.",
               "Words were added before numbers, so the Strings come out in the "
               "original order.",
               "Five printed lines, in the order the prompt lists them."]),
    ])


_PRACTICE[24] = [_P24_A, _P24_B, _P24_C, _P24_D, _P24_E]
