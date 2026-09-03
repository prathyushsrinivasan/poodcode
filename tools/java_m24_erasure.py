# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 24 - Erasure, and what it costs.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Closes Part 7. Modules 21-23 taught generics as the compiler sees them; this
# one shows what survives to run time, which is nothing - and then works through
# every consequence that shows up in real code: the three illegal moves, the
# unchecked cast that fails somewhere else entirely, two overloads that collide,
# the bridge method that throws, and the `Class<T>` token you pass when you need
# the type back.
#
# TEACHING SPINE: erasure is not a wart to memorise, it is one decision
# (generics are a compile-time device, and the JVM never learned about them)
# with a fan of consequences. Every lesson here derives from that one sentence,
# so the module is a chain rather than a list of gotchas.
#
# JUDGING NOTE: erasure is a compile-time story, so most programs here make it
# OBSERVABLE at run time instead - `getClass()` comparisons, and the
# ClassCastException that erasure defers to the point of use. Exception MESSAGES
# vary between JDK versions, so nothing here ever prints `getMessage()`; only
# `e.getClass().getSimpleName()`, which is stable.
# ---------------------------------------------------------------------------

_M24 = []


def _j24(helpers, body):
    """Static helper methods above a Scanner-opening `main`."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


def _j24t(types, helpers, body):
    """Top-level types above `Main`, with optional helpers inside it."""
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


_RD_W24 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")

# The same read, but counted with `m` - for programs that read a list of words
# FIRST and so have already used `n`.
_RD_N24 = ("        int m = sc.nextInt();\n"
           "        List<Integer> nums = new ArrayList<>();\n"
           "        for (int i = 0; i < m; i++) {\n"
           "            nums.add(sc.nextInt());\n"
           "        }\n")

_RD_NUMS24 = ("        int n = sc.nextInt();\n"
              "        List<Integer> nums = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            nums.add(sc.nextInt());\n"
              "        }\n")

_RD_WN24 = _RD_W24 + _RD_N24

# Building one `List<Object>` out of both, which is how the type-token lessons
# get a list worth filtering.
_MIX24 = ("        List<Object> mixed = new ArrayList<>();\n"
          "        for (String w : words) {\n"
          "            mixed.add(w);\n"
          "        }\n"
          "        for (int x : nums) {\n"
          "            mixed.add(x);\n"
          "        }\n")

_W24 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
        ["alpha", "beta", "gamma", "d"])

_N24 = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])

# Single word / single number pairs, for the programs that need one of each.
_WX24 = (("ada", 3), ("solo", 5), ("zzz", -4), ("pear", 10), ("generics", 7))


def _w24(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _n24(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _wn24(ws, xs, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), str(len(xs)),
                            " ".join(str(x) for x in xs)]), out)


def _jl24(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- 24.1 What the compiler actually emits -----------------------------------

_M24.append(_jlesson(
    "m24-erasure", "Erasure - what survives to run time",
    "The type arguments are a compile-time device. None of them reach the JVM.",
    """
Three modules of generics, and now the fact underneath all of them: **the JVM
has never heard of them.** The compiler checks your type arguments, and then
**erases** them.

```java
List<String> words = new ArrayList<>();
List<Integer> nums  = new ArrayList<>();
System.out.println(words.getClass() == nums.getClass());   // true
```

Both are an `ArrayList` at run time. Not a similar class - *the same class
object*. `List<String>` and `List<Integer>` are one type, `ArrayList`, once the
compiler is done.

**What erasure actually does**, in three rules:

| You wrote | The compiler emits |
|---|---|
| `List<String>` | `List` |
| `class Box<T>` (unbounded) | every `T` becomes `Object` |
| `<T extends Number>` | every `T` becomes `Number` - the **bound** |

and then it **inserts the casts** you never wrote. This:

```java
List<String> words = new ArrayList<>();
String first = words.get(0);
```

compiles to something much closer to this:

```java
List words = new ArrayList();
String first = (String) words.get(0);   // the cast the compiler wrote for you
```

That is the whole trick. `List<String>` is a raw `List` plus a promise that the
compiler enforces at every call site, and a cast it silently adds on the way
out. Generics cost nothing at run time because at run time they are not there.

**Erasure erases the type ARGUMENT, not the object.** The values themselves keep
their identity - it is only the *container's* type argument that vanishes:

```java
static <T extends Number> String kindOf(T value) {
    return value.getClass().getSimpleName();
}
kindOf(42);      // "Integer" — the object knows what it is
kindOf(3.5);     // "Double"
```

The list has forgotten what it holds; the things inside it have not.

**Why it was done this way.** Generics arrived in Java 5, ten years into the
language's life, and had to work with every class file already compiled. Erasure
is what made a `List<String>` and an old raw `List` the same type to the JVM -
so old code and new code could keep calling each other. The whole rest of this
module is the bill for that decision.
""",
    warmup=[
        _jq("`new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()` is…",
            ["true - both are just ArrayList at run time", "false",
             "a compile error", "true only for empty lists"],
            0,
            "Erasure leaves one class. The type argument is checked and then thrown away."),
        _jq("`<T extends Number>` erases `T` to…",
            ["Number - the bound", "Object", "T", "the type argument at the call site"],
            0,
            "An unbounded T erases to Object; a bounded one erases to its bound."),
    ],
    exercises=[
        _je("j24-era-sameclass", "One class, two type arguments",
            "Build a `List<String>` and a `List<Integer>`, then prove they are the same "
            "class at run time. Replace `____` with the line that compares them.",
            _jscan(_RD_WN24
                   + "        System.out.println(words.getClass() == nums.getClass());\n"
                     "        System.out.println(words.getClass().getSimpleName());\n"
                     "        System.out.println(words.size() + nums.size());"),
            "System.out.println(words.getClass() == nums.getClass());",
            [_wn24(ws, xs, _nl("true", "ArrayList", len(ws) + len(xs)))
             for (ws, xs) in zip(_W24, _N24)],
            hints=["`getClass()` returns the run-time class, which is where the type "
                   "argument is already gone.",
                   "Compare the two class objects with `==` - there is only one "
                   "`ArrayList` class, so they are the same reference.",
                   "`System.out.println(words.getClass() == nums.getClass());`",
                   "It prints `true`, which is the whole point of the module."],
            difficulty="Easy"),

        _je("j24-era-kind", "The object still knows",
            "Erasure erases the *type argument*, not the objects. `kindOf` reports what a "
            "value really is at run time. Replace `____` with its signature line, bounded "
            "so the method takes any kind of number.",
            _j24("    static <T extends Number> String kindOf(T value) {\n"
                 "        return value.getClass().getSimpleName();\n"
                 "    }",
                 _RD_NUMS24
                 + "        System.out.println(kindOf(nums.get(0)));\n"
                   "        System.out.println(kindOf(nums.get(0) / 2.0));\n"
                   "        System.out.println(nums.size());"),
            "    static <T extends Number> String kindOf(T value) {",
            [_n24(xs, _nl("Integer", "Double", len(xs))) for xs in _N24],
            hints=["This is module 22's bounded type parameter: `<T extends Number>`.",
                   "`static <T extends Number> String kindOf(T value) {`",
                   "Inside the method `T` has erased to `Number` - but "
                   "`value.getClass()` asks the OBJECT, not the type parameter.",
                   "`nums.get(0)` is an `Integer`; `nums.get(0) / 2.0` is a `double` "
                   "that autoboxes to a `Double`."],
            difficulty="Medium"),

        _jfix("j24-era-rawcast", "Writing the cast the compiler usually writes",
              "A raw `List` has no type argument, so `get` returns `Object` and this does "
              "not compile: *incompatible types: Object cannot be converted to String*. "
              "Add the cast by hand - the very cast `List<String>` would have inserted "
              "for you.",
              _jscan("        String word = sc.next();\n"
                     "        List raw = new ArrayList();\n"
                     "        raw.add(word);\n"
                     "        String first = raw.get(0);\n"
                     "        System.out.println(first);\n"
                     "        System.out.println(first.length());"),
              _jscan("        String word = sc.next();\n"
                     "        List raw = new ArrayList();\n"
                     "        raw.add(word);\n"
                     "        String first = (String) raw.get(0);\n"
                     "        System.out.println(first);\n"
                     "        System.out.println(first.length());"),
              [_case(w, _nl(w, len(w)))
               for w in ("ada", "solo", "zzz", "pear", "generics")],
              hints=["A raw `List` is what a `List<String>` erases to, so its `get` "
                     "returns `Object`.",
                     "One cast fixes it: `(String) raw.get(0)`.",
                     "`String first = (String) raw.get(0);`",
                     "Had the list been declared `List<String>`, the compiler would have "
                     "emitted exactly this cast and you would never have seen it.",
                     "The cast is unchecked at compile time but very much checked at run "
                     "time - it is a real `checkcast`."],
              difficulty="Medium"),

        _jch("j24-era-name", "The run-time name", "Easy",
             "Write `erasedName`, which returns the full run-time class name of any list. "
             "`main` calls it on an `ArrayList<String>` and a `LinkedList<String>` - "
             "proving that what survives erasure is the *implementation*, never the "
             "element type.",
             _j24("    static String erasedName(List<?> items) {\n"
                  "        return items.getClass().getName();\n"
                  "    }",
                  _RD_W24
                  + "        List<String> linked = new LinkedList<>();\n"
                    "        for (String w : words) {\n"
                    "            linked.add(w);\n"
                    "        }\n"
                    "        System.out.println(erasedName(words));\n"
                    "        System.out.println(erasedName(linked));\n"
                    "        System.out.println(linked.size());"),
             "    static String erasedName(List<?> items) {\n"
             "        return items.getClass().getName();\n"
             "    }",
             [_w24(ws, _nl("java.util.ArrayList", "java.util.LinkedList", len(ws)))
              for ws in _W24],
             hints=["The parameter takes a list of anything, so it is `List<?>` - "
                    "module 23.",
                    "`getName()` gives the fully qualified name; `getSimpleName()` would "
                    "drop the package.",
                    "`static String erasedName(List<?> items) {` then "
                    "`return items.getClass().getName();`",
                    "Both lists hold Strings, and neither class name mentions it.",
                    "`java.util.ArrayList` and `java.util.LinkedList` - the element type "
                    "is nowhere in either."]),
    ],
    quiz=[
        _jq("`List<String>` at run time is…",
            ["a plain List - the type argument is gone",
             "a List<String> object", "an Object[]", "a raw type only if you say so"],
            0,
            "Erasure leaves the raw type plus compiler-inserted casts."),
        _jq("Why was erasure chosen over reified generics?",
            ["Backward compatibility with pre-generics class files",
             "It is faster", "It is simpler to specify", "To allow wildcards"],
            0,
            "Generics arrived in Java 5 and had to interoperate with every raw-typed "
            "library already compiled."),
    ],
))


# --- 24.2 What erasure makes illegal -----------------------------------------

_M24.append(_jlesson(
    "m24-illegal", "The moves erasure forbids",
    "`new T()`, `new T[]`, `static T`, and `instanceof List<String>` - one cause, four refusals.",
    """
Module 21 listed three things a type parameter cannot do. Now you can see why:
each one needs the type argument to exist at run time, and it does not.

**1. `new T()` - the constructor is not there.**

```java
class Slot<T> {
    private T value;
    Slot() { this.value = new T(); }   // COMPILE ERROR
}
```

At run time `T` is `Object`. `new T()` would have to mean "call whatever
constructor the caller's type argument has", and there is nothing left to ask.
The fix is always the same: **take the value in**, as a constructor or method
parameter.

**2. `new T[n]` - the array cannot check its own stores.**

Arrays are covariant and check every store at run time (module 23), which needs
a real element type. A `T[]` has none. The standard workaround is to store
`Object[]` and cast on the way out:

```java
class Buffer<T> {
    private Object[] items = new Object[16];

    @SuppressWarnings("unchecked")
    T get(int index) {
        return (T) items[index];     // unchecked, but sound: only T ever went in
    }
}
```

That is not a hack anyone should be ashamed of - it is exactly what
`ArrayList` does internally.

**3. `static T` - one class, shared by every parameterization.**

```java
class Cell<T> {
    private static T last;      // COMPILE ERROR
}
```

There is **one** `Cell` class, shared by `Cell<String>` and `Cell<Integer>`
alike. A static field belongs to that one class, so it cannot have a type that
differs per parameterization. Static *methods* may declare their own `<T>`
(module 22) - what they cannot do is use the class's.

**4. `instanceof List<String>` - there is nothing to test.**

```java
if (item instanceof List<String>) { ... }   // COMPILE ERROR
if (item instanceof List<?>) { ... }        // fine - asks only "is it a List?"
```

The compiler rejects the first outright rather than let you write a test that
could never be honest. The wildcard form is allowed because it asks exactly the
question the run time can answer.
""",
    warmup=[
        _jq("`new T()` inside a generic class is illegal because…",
            ["at run time T is erased, so there is no constructor to call",
             "T might be abstract", "it would be slow", "it needs a cast"],
            0,
            "The type argument is not there to ask. Pass the value in instead."),
        _jq("Which of these compiles?",
            ["item instanceof List<?>", "item instanceof List<String>",
             "item instanceof T", "all three"],
            0,
            "Only the wildcard form asks a question the run time can answer."),
    ],
    exercises=[
        _je("j24-ill-instanceof", "The only legal `instanceof`",
            "`shape` reports whether an object is a list or a plain value. "
            "`instanceof List<String>` would not compile - erasure left nothing to test. "
            "Replace `____` with the form that does compile.",
            _j24("    static String shape(Object item) {\n"
                 "        if (item instanceof List<?>) {\n"
                 "            return \"list\";\n"
                 "        }\n"
                 "        return \"value\";\n"
                 "    }",
                 _RD_W24
                 + "        System.out.println(shape(words));\n"
                   "        System.out.println(shape(words.get(0)));\n"
                   "        System.out.println(words.size());"),
            "        if (item instanceof List<?>) {",
            [_w24(ws, _nl("list", "value", len(ws))) for ws in _W24],
            hints=["Naming an element type is exactly what erasure made impossible.",
                   "The unbounded wildcard asks only 'is this a List at all?'.",
                   "`if (item instanceof List<?>) {`",
                   "A raw `item instanceof List` also compiles, but warns - the wildcard "
                   "is the modern spelling."],
            difficulty="Easy"),

        _jfix("j24-ill-newt", "The constructor that is not there",
              "`Slot` tries to build its own value with `new T()`, which does not "
              "compile: at run time `T` has erased away and there is no constructor to "
              "call. Take the value in through the constructor instead, and pass the word "
              "from `main`.",
              _j24t("class Slot<T> {\n"
                    "    private T value;\n"
                    "\n"
                    "    Slot() {\n"
                    "        this.value = new T();\n"
                    "    }\n"
                    "\n"
                    "    T get() {\n"
                    "        return value;\n"
                    "    }\n"
                    "}", "",
                    "        String word = sc.next();\n"
                    "        Slot<String> slot = new Slot<>();\n"
                    "        System.out.println(slot.get());\n"
                    "        System.out.println(word.length());"),
              _j24t("class Slot<T> {\n"
                    "    private T value;\n"
                    "\n"
                    "    Slot(T value) {\n"
                    "        this.value = value;\n"
                    "    }\n"
                    "\n"
                    "    T get() {\n"
                    "        return value;\n"
                    "    }\n"
                    "}", "",
                    "        String word = sc.next();\n"
                    "        Slot<String> slot = new Slot<>(word);\n"
                    "        System.out.println(slot.get());\n"
                    "        System.out.println(word.length());"),
              [_case(w, _nl(w, len(w)))
               for w in ("ada", "solo", "zzz", "pear", "generics")],
              hints=["The error is *unexpected type: type parameter T* on the `new`.",
                     "There is no way to construct a `T`; the only way to get one is to "
                     "be given one.",
                     "Give the constructor a parameter: `Slot(T value)`.",
                     "`main` then has to hand it over: `new Slot<>(word)`.",
                     "This is why so many generic classes are built from a value or a "
                     "factory rather than constructing their own."],
              difficulty="Medium"),

        _je("j24-ill-array", "Storing what you cannot allocate",
            "`Buffer<T>` cannot write `new T[capacity]` - an array checks its stores at "
            "run time and `T` is gone by then. Replace `____` with the allocation it uses "
            "instead, the one `ArrayList` itself uses.",
            _j24t("class Buffer<T> {\n"
                  "    private Object[] items;\n"
                  "    private int count;\n"
                  "\n"
                  "    Buffer(int capacity) {\n"
                  "        this.items = new Object[capacity];\n"
                  "    }\n"
                  "\n"
                  "    void add(T item) {\n"
                  "        items[count] = item;\n"
                  "        count++;\n"
                  "    }\n"
                  "\n"
                  "    @SuppressWarnings(\"unchecked\")\n"
                  "    T get(int index) {\n"
                  "        return (T) items[index];\n"
                  "    }\n"
                  "\n"
                  "    int size() {\n"
                  "        return count;\n"
                  "    }\n"
                  "}", "",
                  "        int n = sc.nextInt();\n"
                  "        Buffer<String> buffer = new Buffer<>(n);\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            buffer.add(sc.next());\n"
                  "        }\n"
                  "        System.out.println(buffer.get(0));\n"
                  "        System.out.println(buffer.size());"),
            "        this.items = new Object[capacity];",
            [_w24(ws, _nl(ws[0], len(ws))) for ws in _W24],
            hints=["`new T[capacity]` is a compile error - *generic array creation*.",
                   "Store the loosest thing there is and cast on the way out.",
                   "`this.items = new Object[capacity];`",
                   "`get` then casts to `T`, which is unchecked but sound: `add(T)` is "
                   "the only way anything got in.",
                   "The `@SuppressWarnings(\"unchecked\")` on `get` is the honest label "
                   "for that trade."],
            difficulty="Medium"),

        _jfix("j24-ill-static", "One class, one static field",
              "`Cell` declares `private static T last;` and a `static T lastSeen()`, and "
              "neither compiles - there is only ONE `Cell` class behind every "
              "parameterization, so a static member cannot have a per-parameterization "
              "type. Widen both to `Object`, which is what the field really is.",
              _j24t("class Cell<T> {\n"
                    "    private T value;\n"
                    "    private static T last;\n"
                    "\n"
                    "    Cell(T value) {\n"
                    "        this.value = value;\n"
                    "        last = value;\n"
                    "    }\n"
                    "\n"
                    "    T get() {\n"
                    "        return value;\n"
                    "    }\n"
                    "\n"
                    "    static T lastSeen() {\n"
                    "        return last;\n"
                    "    }\n"
                    "}", "",
                    "        String word = sc.next();\n"
                    "        int n = sc.nextInt();\n"
                    "        Cell<String> first = new Cell<>(word);\n"
                    "        Cell<Integer> second = new Cell<>(n);\n"
                    "        System.out.println(first.get());\n"
                    "        System.out.println(second.get());\n"
                    "        System.out.println(Cell.lastSeen());"),
              _j24t("class Cell<T> {\n"
                    "    private T value;\n"
                    "    private static Object last;\n"
                    "\n"
                    "    Cell(T value) {\n"
                    "        this.value = value;\n"
                    "        last = value;\n"
                    "    }\n"
                    "\n"
                    "    T get() {\n"
                    "        return value;\n"
                    "    }\n"
                    "\n"
                    "    static Object lastSeen() {\n"
                    "        return last;\n"
                    "    }\n"
                    "}", "",
                    "        String word = sc.next();\n"
                    "        int n = sc.nextInt();\n"
                    "        Cell<String> first = new Cell<>(word);\n"
                    "        Cell<Integer> second = new Cell<>(n);\n"
                    "        System.out.println(first.get());\n"
                    "        System.out.println(second.get());\n"
                    "        System.out.println(Cell.lastSeen());"),
              [_case(f"{w}\n{x}", _nl(w, x, x)) for (w, x) in _WX24],
              hints=["The error is *non-static type variable T cannot be referenced from "
                     "a static context* - twice.",
                     "`Cell<String>` and `Cell<Integer>` are the same class at run time, "
                     "so they share one static field.",
                     "Both the field and the method's return type become `Object`.",
                     "`private static Object last;` and `static Object lastSeen() {`",
                     "Watch the output: the `Cell<Integer>` overwrote what the "
                     "`Cell<String>` stored, because there is only one field. That is the "
                     "whole reason it cannot be typed `T`."],
              difficulty="Medium"),
    ],
    quiz=[
        _jq("Why can a generic class not declare `static T last;`?",
            ["There is one class for every parameterization, so one static field",
             "Statics cannot be private",
             "T is always Object",
             "It would need a cast"],
            0,
            "`Cell<String>` and `Cell<Integer>` share the field - it cannot be two types."),
        _jq("The standard workaround for `new T[n]` is…",
            ["an Object[] plus an unchecked cast on the way out",
             "a List<T> only", "reflection", "there is none"],
            0,
            "Exactly what ArrayList does. The cast is sound because only Ts ever go in."),
    ],
))


# --- 24.3 Unchecked casts, warnings and heap pollution -----------------------

_M24.append(_jlesson(
    "m24-unchecked", "Unchecked casts and heap pollution",
    "The cast that fails is never the one you wrote.",
    """
Because the type argument is erased, a cast **to** a generic type cannot be
checked:

```java
List<?> items = ...;
List<String> words = (List<String>) items;   // warning: unchecked cast
```

At run time that line does nothing at all. It is not a check - it is a
**promise**, and the compiler is telling you it cannot verify it. If the promise
is false, nothing happens *there*. The failure lands later, at the point where
the compiler's own inserted cast finally runs:

```java
String first = words.get(0);   // ClassCastException HERE, not above
```

That distance between the lie and the crash is what makes unchecked casts worth
taking seriously. **Heap pollution** is the name for the state in between: a
`List<String>` that in fact contains an `Integer`.

**Raw types are the usual way in.** Anything raw switches the checking off:

```java
List raw = new ArrayList();
raw.add("ada");
raw.add(42);                  // nobody stopped you
List<String> words = raw;     // unchecked conversion
for (String w : words) { }    // ClassCastException on the 42
```

**`@SuppressWarnings("unchecked")`** silences the warning. Use it only when
*you* can see the invariant the compiler cannot - like `Buffer.get` in the last
lesson, where `add(T)` is the only door in. Put it on the smallest possible
scope, never on a whole class, and treat every use as a claim you would defend
in review.

**Generic varargs are the sharp edge.** `T...` is compiled as `T[]`, and you
already know a `T[]` cannot exist - so the compiler creates an `Object[]` and
warns at every call site about possible heap pollution:

```java
@SafeVarargs
static <T> int countAll(List<T>... lists) { ... }
```

`@SafeVarargs` is your signature on the claim that the method never stores
anything into that array and never lets it escape. It is allowed only on methods
that cannot be overridden - `static`, `final` or `private` - because otherwise
someone else's override could break the promise you signed.

**The honest alternative** to one unchecked cast of a whole collection is a
*checked* cast per element - `instanceof` then cast - which costs a loop and
buys certainty.
""",
    warmup=[
        _jq("`List<String> words = (List<String>) unknownList;` at run time…",
            ["does nothing - the cast cannot be checked, so failure comes later",
             "throws immediately if wrong",
             "copies the list",
             "does not compile"],
            0,
            "It is a promise, not a check. The ClassCastException arrives at the first "
            "`get`."),
        _jq("`@SafeVarargs` may be applied to…",
            ["static, final or private methods", "any method", "only constructors",
             "only generic classes"],
            0,
            "An overridable method could have its promise broken by an override."),
    ],
    exercises=[
        _je("j24-unc-suppress", "Signing for the cast",
            "`asWords` casts a `List<?>` back to a `List<String>`. The compiler cannot "
            "check that, so it warns - and here the caller genuinely knows better. "
            "Replace `____` with the annotation that says so.",
            _j24("    @SuppressWarnings(\"unchecked\")\n"
                 "    static List<String> asWords(List<?> items) {\n"
                 "        return (List<String>) items;\n"
                 "    }",
                 _RD_W24
                 + "        List<?> unknown = words;\n"
                   "        List<String> back = asWords(unknown);\n"
                   "        System.out.println(back.get(0));\n"
                   "        System.out.println(back.size());"),
            "    @SuppressWarnings(\"unchecked\")",
            [_w24(ws, _nl(ws[0], len(ws))) for ws in _W24],
            hints=["The warning is *unchecked cast*, and the annotation names exactly "
                   "that category.",
                   "`@SuppressWarnings(\"unchecked\")`, on the method - the smallest "
                   "scope that covers the cast.",
                   "It suppresses the WARNING, not the risk: if the list really held "
                   "Integers this would still blow up at the first `get`.",
                   "Here `main` built the list itself, so the promise is true."],
            difficulty="Medium"),

        _je("j24-unc-raw", "Where the exception actually lands",
            "A raw `List` takes both a word and a number, and is then handed to a "
            "`List<String>` variable - heap pollution. The loop is where it finally "
            "fails. Replace `____` with the catch that names the exception erasure "
            "deferred to this point.",
            _jscan("        String word = sc.next();\n"
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
                   "        System.out.println(words.size());"),
            "        } catch (ClassCastException e) {",
            [_case(f"{w}\n{x}", _nl(w, "ClassCastException", 2)) for (w, x) in _WX24],
            hints=["Nothing threw at `List<String> words = raw;` - that line only "
                   "warned.",
                   "The enhanced `for` is compiled with a cast to `String` on every "
                   "element, and the second element is an `Integer`.",
                   "`} catch (ClassCastException e) {`",
                   "Note the output order: the first word prints, THEN the failure - the "
                   "list was already half-consumed.",
                   "`getSimpleName()` is printed rather than the message, because the "
                   "message text differs between JDK versions."],
            difficulty="Hard"),

        _je("j24-unc-safevarargs", "Signing for the varargs array",
            "`countAll` takes any number of lists. `List<T>...` compiles to an array of a "
            "type that cannot exist, so every call site warns about heap pollution - "
            "unless the method vouches for itself. Replace `____` with the annotation "
            "that does that.",
            _j24("    @SafeVarargs\n"
                 "    static <T> int countAll(List<T>... lists) {\n"
                 "        int total = 0;\n"
                 "        for (List<T> list : lists) {\n"
                 "            total += list.size();\n"
                 "        }\n"
                 "        return total;\n"
                 "    }",
                 _RD_W24
                 + "        List<String> shouts = new ArrayList<>();\n"
                   "        for (String w : words) {\n"
                   "            shouts.add(w.toUpperCase());\n"
                   "        }\n"
                   "        System.out.println(countAll(words, shouts));\n"
                   "        System.out.println(shouts.get(0));"),
            "    @SafeVarargs",
            [_w24(ws, _nl(2 * len(ws), ws[0].upper())) for ws in _W24],
            hints=["The warning at the call site mentions *possible heap pollution from "
                   "parameterized vararg type*.",
                   "`@SafeVarargs` - and it is legal here because the method is "
                   "`static`.",
                   "The method only READS `lists`; it never stores into the array and "
                   "never lets it escape, which is precisely the claim being signed.",
                   "Both arguments are `List<String>`, so `T` infers as `String`.",
                   "The count is both lists added together."],
            difficulty="Medium"),

        _jch("j24-unc-checked", "The honest alternative", "Medium",
             "Instead of promising that a mixed list is really a `List<String>`, check "
             "each element and keep the ones that are. Write `onlyWords`, which returns a "
             "new `List<String>` holding just the Strings from a list of anything.",
             _j24("    static List<String> onlyWords(List<?> items) {\n"
                  "        List<String> out = new ArrayList<>();\n"
                  "        for (Object item : items) {\n"
                  "            if (item instanceof String) {\n"
                  "                out.add((String) item);\n"
                  "            }\n"
                  "        }\n"
                  "        return out;\n"
                  "    }",
                  "        String word = sc.next();\n"
                  "        int n = sc.nextInt();\n"
                  "        List<Object> mixed = new ArrayList<>();\n"
                  "        mixed.add(word);\n"
                  "        mixed.add(n);\n"
                  "        System.out.println(onlyWords(mixed));\n"
                  "        System.out.println(onlyWords(mixed).size());\n"
                  "        System.out.println(mixed.size());"),
             "    static List<String> onlyWords(List<?> items) {\n"
             "        List<String> out = new ArrayList<>();\n"
             "        for (Object item : items) {\n"
             "            if (item instanceof String) {\n"
             "                out.add((String) item);\n"
             "            }\n"
             "        }\n"
             "        return out;\n"
             "    }",
             [_case(f"{w}\n{x}", _nl(f"[{w}]", 1, 2)) for (w, x) in _WX24],
             hints=["The parameter is `List<?>` - it accepts any list at all.",
                    "Read each element as `Object`, which is all a `List<?>` promises.",
                    "`if (item instanceof String) {` then `out.add((String) item);` - a "
                    "CHECKED cast, one element at a time.",
                    "No `@SuppressWarnings` is needed anywhere: nothing here is "
                    "unchecked.",
                    "The number is dropped, so the result holds one element while the "
                    "input still holds two."]),
    ],
    quiz=[
        _jq("Heap pollution is…",
            ["a List<String> that actually contains something else",
             "running out of heap", "too many objects", "a memory leak"],
            0,
            "The state an unchecked cast can leave behind, discovered later."),
        _jq("`@SuppressWarnings(\"unchecked\")` should go…",
            ["on the smallest scope that contains the cast",
             "on the class", "on main", "anywhere - it is the same"],
            0,
            "A class-wide suppression hides every future unchecked cast too."),
    ],
))


# --- 24.4 Signature clashes and bridge methods -------------------------------

_M24.append(_jlesson(
    "m24-signatures", "Clashes, and the methods you never wrote",
    "Two overloads can erase to one signature - and overriding a generic method quietly adds a method.",
    """
Erasure rewrites signatures, so two methods that look different to you can end
up identical to the JVM:

```java
static int count(List<String> items)  { ... }
static int count(List<Integer> items) { ... }
```

Both erase to `count(List)`. The compiler rejects the pair outright - *name
clash: both methods have the same erasure*. There is no clever fix; **give them
different names**, which is better code anyway. Overloads that differ only in a
type argument were never going to read well at the call site.

**The methods the compiler adds for you.** Take a generic class and a subclass
that fixes the type argument:

```java
class Holder<T> {
    void set(T value) { ... }        // erases to set(Object)
}

class WordHolder extends Holder<String> {
    @Override
    void set(String value) { ... }   // this is set(String)
}
```

After erasure the superclass method is `set(Object)` and the subclass method is
`set(String)`. Those are *different signatures* - so the override would not
actually override anything, and polymorphism would break.

The compiler fixes it by generating a **bridge method** into `WordHolder`:

```java
void set(Object value) {           // synthesized; you never wrote this
    set((String) value);
}
```

Dynamic dispatch now works. But look at the cast inside it, and what happens if
a raw reference sneaks the wrong type past the compiler:

```java
Holder raw = new WordHolder();
raw.set(Integer.valueOf(7));       // compiles - raw type, checking off
```

The call lands in the bridge method, the cast fails, and you get a
`ClassCastException` whose stack trace points at a method that does not exist in
your source. That is not a mystery once you know what a bridge method is - and
it is the standard interview answer to "how does overriding survive erasure?".
""",
    warmup=[
        _jq("`count(List<String>)` and `count(List<Integer>)` in the same class…",
            ["do not compile - same erasure",
             "are ordinary overloads", "compile with a warning",
             "compile if one is static"],
            0,
            "Both erase to `count(List)`. Give them different names."),
        _jq("A bridge method exists to…",
            ["make an override with an erased parameter type still dispatch correctly",
             "speed up calls", "allow wildcards", "replace a constructor"],
            0,
            "It is the `set(Object)` that forwards to your `set(String)`."),
    ],
    exercises=[
        _jfix("j24-sig-clash", "Two methods, one signature",
              "These two overloads look distinct but both erase to `count(List)`, so the "
              "class does not compile: *name clash: count(List<Integer>) and "
              "count(List<String>) have the same erasure*. Give them names that say what "
              "they count, and update the two calls.",
              _j24("    static int count(List<String> items) {\n"
                   "        return items.size();\n"
                   "    }\n"
                   "\n"
                   "    static int count(List<Integer> items) {\n"
                   "        return items.size();\n"
                   "    }",
                   _RD_WN24
                   + "        System.out.println(count(words));\n"
                     "        System.out.println(count(nums));"),
              _j24("    static int countWords(List<String> items) {\n"
                   "        return items.size();\n"
                   "    }\n"
                   "\n"
                   "    static int countNums(List<Integer> items) {\n"
                   "        return items.size();\n"
                   "    }",
                   _RD_WN24
                   + "        System.out.println(countWords(words));\n"
                     "        System.out.println(countNums(nums));"),
              [_wn24(ws, xs, _nl(len(ws), len(xs))) for (ws, xs) in zip(_W24, _N24)],
              hints=["The type argument is the ONLY difference, and it is exactly what "
                     "erasure removes.",
                     "No annotation or cast can rescue this - the two methods are the "
                     "same method.",
                     "`countWords` and `countNums`.",
                     "Both call sites change too.",
                     "A single `countAny(List<?>)` would also have worked, and is often "
                     "the better design."],
              difficulty="Medium"),

        _je("j24-sig-bridge", "The method you never wrote",
            "`WordHolder` overrides `set(String)`, so the compiler generates a bridge "
            "`set(Object)` that casts and forwards. A raw `Holder` reference then slips "
            "an `Integer` past the compiler, and the bridge's cast is what fails. Replace "
            "`____` with the catch that names it.",
            _j24t("class Holder<T> {\n"
                  "    private T value;\n"
                  "\n"
                  "    void set(T value) {\n"
                  "        this.value = value;\n"
                  "    }\n"
                  "\n"
                  "    T get() {\n"
                  "        return value;\n"
                  "    }\n"
                  "}\n"
                  "\n"
                  "class WordHolder extends Holder<String> {\n"
                  "    @Override\n"
                  "    void set(String value) {\n"
                  "        super.set(value.toUpperCase());\n"
                  "    }\n"
                  "}", "",
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
                  "        System.out.println(holder.get());"),
            "        } catch (ClassCastException e) {",
            [_case(w, _nl(w.upper(), "ClassCastException", w.upper()))
             for w in ("ada", "solo", "zzz", "pear", "generics")],
            hints=["`raw.set(...)` calls the erased `set(Object)` - which in "
                   "`WordHolder` is the generated bridge.",
                   "The bridge body is `set((String) value);`, and `value` is an "
                   "`Integer`.",
                   "`} catch (ClassCastException e) {`",
                   "The held value is unchanged by the failed call, so the last line "
                   "prints the same word as the first.",
                   "In a real stack trace this exception points at `WordHolder.set` with "
                   "a signature you never typed."],
            difficulty="Hard"),

        _je("j24-sig-override", "Overriding at the fixed type",
            "`WordStore` implements `Store<String>`, so it overrides `put` at the "
            "concrete type and the compiler bridges the rest. Replace `____` with that "
            "override's signature line - remembering that an interface method must be "
            "implemented `public`.",
            _j24t("interface Store<T> {\n"
                  "    void put(T item);\n"
                  "\n"
                  "    int size();\n"
                  "}\n"
                  "\n"
                  "class WordStore implements Store<String> {\n"
                  "    private List<String> items = new ArrayList<>();\n"
                  "\n"
                  "    @Override\n"
                  "    public void put(String item) {\n"
                  "        items.add(item);\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public int size() {\n"
                  "        return items.size();\n"
                  "    }\n"
                  "}", "",
                  "        int n = sc.nextInt();\n"
                  "        Store<String> store = new WordStore();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            store.put(sc.next());\n"
                  "        }\n"
                  "        System.out.println(store.size());\n"
                  "        System.out.println(store.getClass().getSimpleName());"),
            "    public void put(String item) {",
            [_w24(ws, _nl(len(ws), "WordStore")) for ws in _W24],
            hints=["The interface fixes `T` to `String`, so the override names `String` "
                   "directly.",
                   "Interface methods are public, and an implementation may not reduce "
                   "visibility - module 14.",
                   "`public void put(String item) {`",
                   "The compiler adds a bridge `put(Object)` so a call through "
                   "`Store<String>` still reaches this method.",
                   "`getSimpleName()` reports the real class behind the interface "
                   "reference."],
            difficulty="Medium"),

        _jch("j24-sig-names", "Three counters that coexist", "Easy",
             "Write the three counting methods `main` calls. Two of them take lists that "
             "erase to the same thing, so they cannot share a name; the third takes a "
             "list of anything at all.",
             _j24("    static int countWords(List<String> items) {\n"
                  "        return items.size();\n"
                  "    }\n"
                  "\n"
                  "    static int countNums(List<Integer> items) {\n"
                  "        return items.size();\n"
                  "    }\n"
                  "\n"
                  "    static int countAny(List<?> items) {\n"
                  "        return items.size();\n"
                  "    }",
                  _RD_WN24
                  + "        System.out.println(countWords(words));\n"
                    "        System.out.println(countNums(nums));\n"
                    "        System.out.println(countAny(words) + countAny(nums));"),
             "    static int countWords(List<String> items) {\n"
             "        return items.size();\n"
             "    }\n"
             "\n"
             "    static int countNums(List<Integer> items) {\n"
             "        return items.size();\n"
             "    }\n"
             "\n"
             "    static int countAny(List<?> items) {\n"
             "        return items.size();\n"
             "    }",
             [_wn24(ws, xs, _nl(len(ws), len(xs), len(ws) + len(xs)))
              for (ws, xs) in zip(_W24, _N24)],
             hints=["`countWords(List<String>)` and `countNums(List<Integer>)` - distinct "
                    "names, because their erasures are identical.",
                    "`countAny` takes `List<?>` and so accepts both.",
                    "All three bodies are a single `return items.size();`.",
                    "`countAny` could have replaced the other two entirely - which is "
                    "usually the right call when only the size is wanted.",
                    "Three printed lines; the third is the two sizes added."]),
    ],
    quiz=[
        _jq("Why does `WordHolder` end up with a `set(Object)` it never declared?",
            ["A bridge method, so the override still dispatches after erasure",
             "Because Object has one", "To allow raw types", "It is a compiler bug"],
            0,
            "Without it, `set(String)` would not override the erased `set(Object)`."),
        _jq("The only fix for two overloads with the same erasure is…",
            ["different names", "a cast", "@SuppressWarnings", "making one static"],
            0,
            "They are the same method to the JVM; nothing at the call site can help."),
    ],
))


# --- 24.5 Class<T> type tokens -----------------------------------------------

_M24.append(_jlesson(
    "m24-tokens", "`Class<T>` - handing the type back",
    "If the compiler erased it and you still need it, pass it in.",
    """
Every earlier lesson ended in the same place: at run time, the type is gone. So
when you genuinely need it, the fix is not to recover it - it is to **carry it
along as an ordinary value**.

`Class<T>` is that value. `String.class` has type `Class<String>`,
`Integer.class` has type `Class<Integer>`, and passing one is called a **type
token**:

```java
static <T> int countOf(List<?> items, Class<T> type) {
    int total = 0;
    for (Object item : items) {
        if (type.isInstance(item)) {
            total++;
        }
    }
    return total;
}

countOf(mixed, String.class);    // T inferred as String
```

Two methods on `Class<T>` do all the work, and both are the run-time answer to
something erasure took away:

| You wanted | You write |
|---|---|
| `item instanceof T` | `type.isInstance(item)` |
| `(T) item` | `type.cast(item)` |

`isInstance` is a real run-time check. `cast` is a *checked* cast - it throws
`ClassCastException` immediately rather than leaving heap pollution for a later
`get` to find. So a type token turns yesterday's unchecked cast into today's
checked one:

```java
static <T> List<T> allOf(List<?> items, Class<T> type) {
    List<T> out = new ArrayList<>();
    for (Object item : items) {
        if (type.isInstance(item)) {
            out.add(type.cast(item));    // checked, and no warning
        }
    }
    return out;
}
```

No `@SuppressWarnings` anywhere, because nothing here is a promise - it is all
verified.

**This is a real pattern, not a curiosity.** The JDK uses it wherever a method
must return a type the caller chooses:
`Collections.checkedList(list, String.class)` wraps a list so that a raw-typed
write fails *at the write* instead of far away. When you meet a `Class<T>`
parameter in a library, this is always what it is for.
""",
    warmup=[
        _jq("`String.class` has type…",
            ["Class<String>", "Class<?>", "Class", "String"],
            0,
            "Which is what lets a `Class<T>` parameter infer `T` from the argument."),
        _jq("`type.cast(item)` differs from `(T) item` because…",
            ["it is checked at run time and throws there and then",
             "it is faster", "it never throws", "it works on primitives"],
            0,
            "The unchecked cast does nothing at run time; `cast` really checks."),
    ],
    exercises=[
        _je("j24-tok-header", "Taking the type as an argument",
            "`countOf` counts how many elements of a list are of a given type. Erasure "
            "means it cannot ask `T` anything, so the type arrives as a value. Replace "
            "`____` with its signature line.",
            _j24("    static <T> int countOf(List<?> items, Class<T> type) {\n"
                 "        int total = 0;\n"
                 "        for (Object item : items) {\n"
                 "            if (type.isInstance(item)) {\n"
                 "                total++;\n"
                 "            }\n"
                 "        }\n"
                 "        return total;\n"
                 "    }",
                 "        String word = sc.next();\n"
                 "        int n = sc.nextInt();\n"
                 "        List<Object> mixed = new ArrayList<>();\n"
                 "        mixed.add(word);\n"
                 "        mixed.add(n);\n"
                 "        mixed.add(word);\n"
                 "        System.out.println(countOf(mixed, String.class));\n"
                 "        System.out.println(countOf(mixed, Integer.class));\n"
                 "        System.out.println(mixed.size());"),
            "    static <T> int countOf(List<?> items, Class<T> type) {",
            [_case(f"{w}\n{x}", _nl(2, 1, 3)) for (w, x) in _WX24],
            hints=["The list can be anything, so it is `List<?>`; the type comes in as a "
                   "`Class<T>`.",
                   "`static <T> int countOf(List<?> items, Class<T> type) {`",
                   "`String.class` is a `Class<String>`, so `T` infers at the call site.",
                   "The list holds the word twice and the number once."],
            difficulty="Medium"),

        _je("j24-tok-cast", "The checked cast",
            "`allOf` collects every element of a given type into a properly typed list. "
            "The element is an `Object`, so it has to become a `T` somehow - and a plain "
            "`(T)` cast would be unchecked. Replace `____` with the checked alternative.",
            _j24("    static <T> List<T> allOf(List<?> items, Class<T> type) {\n"
                 "        List<T> out = new ArrayList<>();\n"
                 "        for (Object item : items) {\n"
                 "            if (type.isInstance(item)) {\n"
                 "                out.add(type.cast(item));\n"
                 "            }\n"
                 "        }\n"
                 "        return out;\n"
                 "    }",
                 _RD_WN24 + _MIX24
                 + "        System.out.println(allOf(mixed, String.class));\n"
                   "        System.out.println(allOf(mixed, Integer.class));\n"
                   "        System.out.println(mixed.size());"),
            "                out.add(type.cast(item));",
            [_wn24(ws, xs, _nl(_jl24(ws), _jl24(xs), len(ws) + len(xs)))
             for (ws, xs) in zip(_W24, _N24)],
            hints=["`Class<T>` has a method that casts and checks in one go.",
                   "`type.cast(item)` returns a `T`, so it can go straight into the "
                   "`List<T>`.",
                   "`out.add(type.cast(item));`",
                   "Because the `isInstance` guard ran first, the cast can never actually "
                   "fail here.",
                   "No `@SuppressWarnings` is needed - which is the difference from "
                   "lesson 24.3."],
            difficulty="Medium"),

        _jfix("j24-tok-instanceof", "Testing a type parameter",
              "This tries `item instanceof T`, which does not compile - `T` is erased, so "
              "there is no type there to test against. The method already receives the "
              "type as a value; use it.",
              _j24("    static <T> int countOf(List<?> items, Class<T> type) {\n"
                   "        int total = 0;\n"
                   "        for (Object item : items) {\n"
                   "            if (item instanceof T) {\n"
                   "                total++;\n"
                   "            }\n"
                   "        }\n"
                   "        return total;\n"
                   "    }",
                   _RD_WN24 + _MIX24
                   + "        System.out.println(countOf(mixed, String.class));\n"
                     "        System.out.println(countOf(mixed, Integer.class));\n"
                     "        System.out.println(mixed.size());"),
              _j24("    static <T> int countOf(List<?> items, Class<T> type) {\n"
                   "        int total = 0;\n"
                   "        for (Object item : items) {\n"
                   "            if (type.isInstance(item)) {\n"
                   "                total++;\n"
                   "            }\n"
                   "        }\n"
                   "        return total;\n"
                   "    }",
                   _RD_WN24 + _MIX24
                   + "        System.out.println(countOf(mixed, String.class));\n"
                     "        System.out.println(countOf(mixed, Integer.class));\n"
                     "        System.out.println(mixed.size());"),
              [_wn24(ws, xs, _nl(len(ws), len(xs), len(ws) + len(xs)))
               for (ws, xs) in zip(_W24, _N24)],
              hints=["The error is *illegal generic type for instanceof*.",
                     "`T` does not exist at run time; the `Class<T>` parameter does.",
                     "`if (type.isInstance(item)) {`",
                     "`isInstance` is the run-time replacement for `instanceof` whenever "
                     "the type is a value rather than a name.",
                     "The signature does not change at all - only the test inside."],
              difficulty="Medium"),

        _jch("j24-tok-first", "The first of its kind", "Hard",
             "Write `firstOf`, which returns the first element of a list that is of a "
             "given type, or `null` if there is none. `main` builds a list with the "
             "numbers first and the words after, then asks for one of each.",
             _j24("    static <T> T firstOf(List<?> items, Class<T> type) {\n"
                  "        for (Object item : items) {\n"
                  "            if (type.isInstance(item)) {\n"
                  "                return type.cast(item);\n"
                  "            }\n"
                  "        }\n"
                  "        return null;\n"
                  "    }",
                  _RD_WN24
                  + "        List<Object> mixed = new ArrayList<>();\n"
                    "        for (int x : nums) {\n"
                    "            mixed.add(x);\n"
                    "        }\n"
                    "        for (String w : words) {\n"
                    "            mixed.add(w);\n"
                    "        }\n"
                    "        System.out.println(firstOf(mixed, String.class));\n"
                    "        System.out.println(firstOf(mixed, Integer.class));\n"
                    "        System.out.println(mixed.size());"),
             "    static <T> T firstOf(List<?> items, Class<T> type) {\n"
             "        for (Object item : items) {\n"
             "            if (type.isInstance(item)) {\n"
             "                return type.cast(item);\n"
             "            }\n"
             "        }\n"
             "        return null;\n"
             "    }",
             [_wn24(ws, xs, _nl(ws[0], xs[0], len(ws) + len(xs)))
              for (ws, xs) in zip(_W24, _N24)],
             hints=["The return type is `T` - the type token is what makes that "
                    "honest.",
                    "`static <T> T firstOf(List<?> items, Class<T> type) {`",
                    "Guard with `type.isInstance(item)`, then `return type.cast(item);`.",
                    "`return null;` after the loop - `null` is a legal value of every "
                    "reference type, including `T`.",
                    "The numbers were added first, so the first String is still the first "
                    "WORD, and the first Integer is the first number.",
                    "This is the shape `Class<T>` exists for: a return type the caller "
                    "chooses."]),
    ],
    quiz=[
        _jq("A type token is…",
            ["a Class<T> passed as an ordinary argument, carrying the type erasure removed",
             "an annotation", "a wildcard", "a cast"],
            0,
            "If the compiler erased it and you still need it, pass it in."),
        _jq("`Collections.checkedList(list, String.class)` exists to…",
            ["make a bad write fail at the write, instead of far away",
             "sort a list", "copy a list", "make a list immutable"],
            0,
            "It moves the failure back to the line that caused it."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M24_CAP_HELPERS = (
    "    static String erasedName(List<?> items) {\n"
    "        return items.getClass().getSimpleName();\n"
    "    }\n"
    "\n"
    "    static <T> List<T> allOf(List<?> items, Class<T> type) {\n"
    "        List<T> out = new ArrayList<>();\n"
    "        for (Object item : items) {\n"
    "            if (type.isInstance(item)) {\n"
    "                out.add(type.cast(item));\n"
    "            }\n"
    "        }\n"
    "        return out;\n"
    "    }\n"
    "\n"
    "    @SuppressWarnings(\"unchecked\")\n"
    "    static String firstAsWord(List<?> items) {\n"
    "        try {\n"
    "            List<String> words = (List<String>) items;\n"
    "            return words.get(0);\n"
    "        } catch (ClassCastException e) {\n"
    "            return e.getClass().getSimpleName();\n"
    "        }\n"
    "    }"
)

_M24_CAP_BODY = (
    _RD_WN24
    + _MIX24
    + "        List<Object> onlyNums = new ArrayList<>();\n"
      "        for (int x : nums) {\n"
      "            onlyNums.add(x);\n"
      "        }\n"
      "        System.out.println(erasedName(mixed));\n"
      "        System.out.println(allOf(mixed, String.class));\n"
      "        System.out.println(allOf(mixed, Integer.class));\n"
      "        System.out.println(firstAsWord(mixed));\n"
      "        System.out.println(firstAsWord(onlyNums));\n"
      "        System.out.println(mixed.size());"
)


def _m24_cap_case(ws, xs):
    return _wn24(ws, xs,
                 _nl("ArrayList", _jl24(ws), _jl24(xs), ws[0],
                     "ClassCastException", len(ws) + len(xs)))


_M24_CAP = _jcap(
    "The erasure audit",
    """
Three methods that between them show what erasure took away, what it left, and
what you do about it.

* **`erasedName(list)`** - returns the list's run-time class name. It will say
  `ArrayList` for a list of words and a list of numbers alike, because that is
  all that is left.
* **`allOf(list, type)`** - the type-token filter: every element of the given
  type, in a properly typed `List<T>`, using `isInstance` and `cast`. No
  unchecked anything.
* **`firstAsWord(list)`** - deliberately the other way. It makes an **unchecked**
  promise that the list is a `List<String>` and returns its first element,
  catching `ClassCastException` and returning the exception's simple name
  instead.

`main` calls `firstAsWord` twice: once on a list that really does start with a
word, and once on a list of numbers. The second call is the module in one line -
the cast that "fails" is not the one written in the source, it is the one the
compiler inserted on the `return`.
""",
    _jch("j24-cap-audit", "The erasure audit", "Hard",
         "Write the three methods described in the brief so the given `main` compiles and "
         "prints its six lines.",
         _j24(_M24_CAP_HELPERS, _M24_CAP_BODY),
         _M24_CAP_HELPERS,
         [_m24_cap_case(ws, xs) for (ws, xs) in zip(_W24, _N24)],
         hints=["`erasedName` takes `List<?>` and returns "
                "`items.getClass().getSimpleName()`.",
                "`allOf` is the type-token filter: `static <T> List<T> allOf(List<?> "
                "items, Class<T> type)`.",
                "Inside it, guard with `type.isInstance(item)` and add "
                "`type.cast(item)` - both checked, so no annotation is needed.",
                "`firstAsWord` casts the whole list: `List<String> words = (List<String>) "
                "items;`, which is an unchecked cast and needs "
                "`@SuppressWarnings(\"unchecked\")` on the method.",
                "That cast never throws. The throw comes from `return words.get(0);`, "
                "where the compiler inserted a cast to `String`.",
                "Catch `ClassCastException` and return `e.getClass().getSimpleName()` - "
                "never `getMessage()`, whose wording changes between JDK versions.",
                "The mixed list holds the words first and then the numbers, so "
                "`firstAsWord(mixed)` succeeds and `firstAsWord(onlyNums)` does not."]),
    example_io="stdin:  3\n        ada bo cy\n        3\n        3 1 2\n\n"
               "stdout: ArrayList\n        [ada, bo, cy]\n        [3, 1, 2]\n"
               "        ada\n        ClassCastException\n        6",
    rubric=[
        "`erasedName` takes a `List<?>` and reports the run-time class, not the element type.",
        "`allOf` declares `<T>` and takes a `Class<T>` type token.",
        "`allOf` uses `isInstance` to guard and `cast` to convert - no `(T)` cast, no suppression.",
        "`firstAsWord` performs an unchecked cast of the whole list and is annotated `@SuppressWarnings(\"unchecked\")`.",
        "`firstAsWord` catches `ClassCastException` and returns its simple name.",
        "Nothing prints an exception message, which is not stable across JDK versions.",
        "All six lines are printed in order.",
    ],
)


_MODULES.append(_jmod(
    24, 7, "Generics",
    "Erasure, and what it costs",
    "Type arguments are checked and then thrown away - and every generics rule that looks "
    "arbitrary (`new T()`, `static T`, unchecked casts, name clashes, bridge methods) "
    "follows from that one fact.",
    """
The JVM has never heard of generics. The compiler checks your type arguments and
then **erases** them: `List<String>` becomes `List`, an unbounded `T` becomes
`Object`, a bounded one becomes its bound - and the casts you never wrote are
inserted for you. That is why generics are free at run time, and it is why
`new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()`.

Everything else in this module is the bill:

* **You cannot** `new T()`, `new T[]`, declare a `static T`, or test
  `instanceof List<String>` - each needs a type that is no longer there.
* **An unchecked cast is a promise, not a check**, so the
  `ClassCastException` lands at the point of *use*, not at the cast. That gap is
  heap pollution, and `@SuppressWarnings("unchecked")` / `@SafeVarargs` are how
  you sign for it.
* **Two overloads can erase to one signature**, which no cast can rescue - and
  overriding a generic method quietly generates a **bridge method**, which is
  where a raw-typed call's exception really comes from.
* **When you still need the type, pass it**: `Class<T>` as a type token, with
  `isInstance` and `cast` doing at run time what `instanceof` and `(T)` cannot.

This closes Part 7. You can now write generic classes and methods, bound them,
open them up with wildcards, and explain exactly what the compiler does with all
of it.
""",
    _M24,
    capstone=_M24_CAP,
    objectives=[
        "State what erasure does to a parameterized type, an unbounded `T` and a bounded `T`.",
        "Show that two parameterizations share one run-time class, and explain why.",
        "Explain why `new T()`, `new T[]` and `static T` are all illegal, from one cause.",
        "Write the `Object[]`-plus-cast workaround for a generic array, and justify the suppression.",
        "Say why `instanceof List<String>` is rejected and `instanceof List<?>` is not.",
        "Explain where an unchecked cast's `ClassCastException` actually surfaces, and what heap pollution means.",
        "Use `@SuppressWarnings(\"unchecked\")` and `@SafeVarargs` honestly, and say when each is allowed.",
        "Recognise a name clash from identical erasures, and explain what a bridge method is for.",
        "Use a `Class<T>` type token with `isInstance` and `cast` to recover a type erasure removed.",
    ],
    why="Erasure is the answer behind half the generics questions in interviews - why "
        "`new T()` fails, why two overloads clash, where a mysterious ClassCastException "
        "came from - and every one of them is the same answer. It is also the difference "
        "between suppressing a warning because you understand it and suppressing it "
        "because it was in the way, which is a habit worth forming well beyond Java.",
    est_minutes=330,
    glossary=[
        _jg("erasure", "The compiler's removal of type arguments after checking them: "
                       "`List<String>` becomes `List`."),
        _jg("reification", "The opposite - a type that survives to run time. Java's "
                           "arrays are reified; its generics are not."),
        _jg("raw type", "A generic type used with no type argument at all (`List`). "
                        "Switches off type checking; the erased form of the type."),
        _jg("unchecked cast", "A cast to a parameterized type that the run time cannot "
                              "verify. It is a promise, and it never throws itself."),
        _jg("heap pollution", "The state left by a broken promise: a `List<String>` that "
                              "actually holds something else."),
        _jg("@SuppressWarnings(\"unchecked\")", "Your signature on an unchecked cast. "
                                                "Applies to the smallest scope you put it on."),
        _jg("@SafeVarargs", "A promise that a generic varargs method never pollutes or "
                            "leaks its array. Allowed only on `static`, `final` or "
                            "`private` methods."),
        _jg("name clash", "Two methods whose erased signatures are identical. Rejected at "
                          "compile time; only different names fix it."),
        _jg("bridge method", "A method the compiler synthesizes so an override with a "
                             "narrowed parameter type still dispatches after erasure."),
        _jg("type token", "A `Class<T>` passed as an argument to carry a type erasure "
                          "would otherwise have removed."),
    ],
    cheatsheet="""
```java
// --- what erasure does ----------------------------------------------------
List<String>            ->  List                 // type argument removed
class Box<T>            ->  T becomes Object     // unbounded
<T extends Number>      ->  T becomes Number     // erased to the BOUND
String s = words.get(0);  // compiler inserts (String) for you

new ArrayList<String>().getClass() == new ArrayList<Integer>().getClass()  // true

// --- what it makes illegal ------------------------------------------------
new T()                     // no constructor at run time -> take the value in
new T[n]                    // -> Object[] + @SuppressWarnings cast on read
static T last;              // one class per generic type, so one static field
item instanceof List<String>   // -> item instanceof List<?>

// --- unchecked casts ------------------------------------------------------
List<String> ws = (List<String>) unknown;   // a PROMISE - never throws here
String first = ws.get(0);                   // ClassCastException lands HERE

@SuppressWarnings("unchecked")   // smallest scope; only when you know better
@SafeVarargs                     // static/final/private only; never leak the array

// --- erased signatures ----------------------------------------------------
int count(List<String>)   //  name clash: both erase to count(List)
int count(List<Integer>)  //  -> countWords / countNums

class WordHolder extends Holder<String> {
    void set(String v) { ... }       // compiler adds: void set(Object v) { set((String) v); }
}                                    //   <- a raw call throws from THIS bridge

// --- getting the type back ------------------------------------------------
static <T> List<T> allOf(List<?> items, Class<T> type) {
    if (type.isInstance(item))       // instead of  item instanceof T
        out.add(type.cast(item));    // instead of  (T) item   - and it is CHECKED
}
allOf(mixed, String.class);          // String.class is a Class<String>
```
""",
    self_check=[
        "Can you say what `List<String>`, an unbounded `T` and a `<T extends Number>` each erase to?",
        "Can you write the two lines that prove two parameterizations share one class?",
        "Can you explain `new T()`, `new T[]` and `static T` as three faces of one cause?",
        "Can you write the `Object[]` workaround and justify its `@SuppressWarnings`?",
        "Can you say which `instanceof` form compiles, and why the other cannot?",
        "Can you say where an unchecked cast's ClassCastException actually surfaces, and define heap pollution?",
        "Can you say which methods `@SafeVarargs` is allowed on, and why only those?",
        "Can you explain what a bridge method is and write the one the compiler generates for `Holder<String>`?",
        "Can you write a `Class<T>` type-token method using `isInstance` and `cast`?",
    ],
    review=[
        _jq("```java\nList<String> a = new ArrayList<>();\nList<Integer> b = new ArrayList<>();\nSystem.out.println(a.getClass() == b.getClass());\n```",
            ["true", "false", "compile error", "depends on contents"],
            0,
            "Erasure leaves one `ArrayList` class; the type argument is gone."),
        _jq("`private static T last;` inside `class Cell<T>` fails because…",
            ["there is one Cell class shared by every parameterization",
             "statics cannot be private",
             "T must be bounded",
             "it needs a cast"],
            0,
            "A static field belongs to the one class, so it cannot vary with `T`."),
        _jq("After `List<String> ws = (List<String>) rawList;` where the list holds an Integer, the exception is thrown…",
            ["at the first get that expects a String", "at the cast",
             "when the list is created", "never"],
            0,
            "The unchecked cast does nothing at run time. The inserted cast is what fails."),
        _jq("`static <T> T firstOf(List<?> items, Class<T> type)` needs the `Class<T>` because…",
            ["`instanceof T` and `(T)` are both impossible after erasure",
             "it is faster", "wildcards require it", "T must be bounded"],
            0,
            "The type token carries at run time what the compiler erased."),
    ],
    milestone="You can explain every generics rule that looks arbitrary as a consequence "
              "of one decision - that type arguments are checked and then thrown away - "
              "and you can work with, around and against erasure deliberately: the "
              "`Object[]` workaround, an honest `@SuppressWarnings`, and a `Class<T>` "
              "token when the type has to come back.",
))
