# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 22 - Generic methods and bounded type parameters.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# The second half of module 21's static story: a METHOD can declare its own type
# parameter, which is how a static utility works on any type at all. Then bounds
# (`<T extends Comparable<T>>`), because an unbounded `T` can only be handed
# around - the moment you want to CALL something on it, you have to promise what
# it is.
#
# Wildcards stay reserved for module 23, so every signature here is written with
# a named type parameter. Lambdas are banned course-wide, so a `Comparator` is
# always a named class (module 20's rule, restated).
# ---------------------------------------------------------------------------

_M22 = []


def _j22(helpers, body):
    """Static helper methods above a Scanner-opening `main`, module 9's shape."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }"
    )


def _j22t(types, helpers, body):
    """Top-level types AND static helpers - for the exercises that need both."""
    return _jp(
        _IMPORTS + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


_RD_WORDS22 = ("        int n = sc.nextInt();\n"
               "        List<String> words = new ArrayList<>();\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            words.add(sc.next());\n"
               "        }\n")

_RD_NUMS22 = ("        int n = sc.nextInt();\n"
              "        List<Integer> nums = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            nums.add(sc.nextInt());\n"
              "        }\n")

_WORDS22 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
            ["alpha", "beta", "gamma", "d"])

_NUMS22 = ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])


def _wcase22(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _ncase22(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jlist22(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


# --- 22.1 Generic methods ----------------------------------------------------

_M22.append(_jlesson(
    "m22-method", "Generic methods",
    "`static <T> ...` - a method with its own type parameter.",
    """
Module 21 ended on a rule: a `static` member cannot use the *class's* type
parameter, because `T` belongs to an instance. The way out is for the **method**
to declare a type parameter of its own.

```java
static <T> void printAll(List<T> items) {
    for (T item : items) {
        System.out.println(item);
    }
}
```

Read the header left to right: `static`, then `<T>` - **the declaration** -
then the return type `void`, then the name. The angle brackets go *between the
modifiers and the return type*, and nowhere else. That position is the whole
syntax of this lesson, and getting it wrong is the most common generics compile
error there is:

```java
static void printAll(List<T> items)      // cannot find symbol: class T
static <T> void printAll(List<T> items)  // correct
```

The type parameter lives for the length of one call. On the next call `T` can be
something else entirely:

```java
printAll(names);    // T is String here
printAll(scores);   // T is Integer here
```

**You do not write the type argument at the call site.** The compiler *infers*
it from the arguments - the same inference the diamond uses. When it cannot (an
empty list, or a return type it has nothing to work from), you can supply it
explicitly with a **type witness**:

```java
String s = Main.<String>first(names);   // rarely needed, but this is the syntax
```

**A generic method may be static or not, and may live in a plain class or a
generic one.** A generic class does not make its methods generic - and a static
generic method is exactly what module 21's `Bag` could not have.

**The return type can be the type parameter too**, which is what makes these
useful rather than merely tidy:

```java
static <T> T last(List<T> items) {
    return items.get(items.size() - 1);
}

String name = last(names);   // comes back as a String. No cast.
```

**A single type parameter used twice means the same type in both places.**
`static <T> int countEqual(List<T> items, T target)` will not let you count
Strings in a list of Integers - the compiler has to find one `T` that fits
both.
""",
    warmup=[
        _jq("Where do the angle brackets go in a generic method?",
            ["Between the modifiers and the return type",
             "After the method name",
             "After the parameter list",
             "Before `static`"],
            0,
            "`static <T> T last(...)`. Anywhere else and `T` is an unknown class."),
        _jq("At the call site `printAll(names)`, who decides what `T` is?",
            ["The compiler, by inferring it from the argument",
             "The JVM at run time", "You, always explicitly", "It stays Object"],
            0,
            "Inference, exactly like the diamond. A type witness is only needed when "
            "there is nothing to infer from."),
    ],
    exercises=[
        _je("j22-gm-header", "Declare the method's parameter",
            "`printAll` should print any list, whatever it holds. Replace `____` with "
            "its full signature line.",
            _j22("    static <T> void printAll(List<T> items) {\n"
                 "        for (T item : items) {\n"
                 "            System.out.println(item);\n"
                 "        }\n"
                 "    }",
                 _RD_WORDS22 + "        printAll(words);"),
            "    static <T> void printAll(List<T> items) {",
            [_wcase22(ws, _nl(*ws)) for ws in _WORDS22],
            hints=["The method needs a type parameter of its own - the class has none.",
                   "It is declared between `static` and the return type.",
                   "`static <T> void printAll(List<T> items) {`",
                   "Without the `<T>` the compiler reads `T` as the name of a class it "
                   "cannot find."],
            difficulty="Easy"),

        _je("j22-gm-return", "A generic return type",
            "`last` hands back the final element, already of the right type - no cast "
            "at the call site. Replace `____` with its signature line.",
            _j22("    static <T> T last(List<T> items) {\n"
                 "        return items.get(items.size() - 1);\n"
                 "    }",
                 _RD_WORDS22
                 + "        String tail = last(words);\n"
                 "        System.out.println(tail);\n"
                 "        System.out.println(tail.length());"),
            "    static <T> T last(List<T> items) {",
            [_wcase22(ws, _nl(ws[-1], len(ws[-1]))) for ws in _WORDS22],
            hints=["Declare the parameter first, then use it as the return type.",
                   "`static <T> T last(...)` - the first `T` declares, the second uses.",
                   "`static <T> T last(List<T> items) {`",
                   "`main` assigns the result straight into a `String`, which only "
                   "compiles because `T` is inferred as `String`."],
            difficulty="Easy"),

        _jfix("j22-gm-undeclared", "A type that was never declared",
              "This does not compile: *cannot find symbol - class T*. The method uses "
              "`T` without ever declaring it, so the compiler is looking for a class "
              "with that name. Declare the type parameter in the right place.",
              _j22("    static T firstOf(List<T> items) {\n"
                   "        return items.get(0);\n"
                   "    }",
                   _RD_WORDS22
                   + "        System.out.println(firstOf(words));\n"
                     "        System.out.println(words.size());"),
              _j22("    static <T> T firstOf(List<T> items) {\n"
                   "        return items.get(0);\n"
                   "    }",
                   _RD_WORDS22
                   + "        System.out.println(firstOf(words));\n"
                     "        System.out.println(words.size());"),
              [_wcase22(ws, _nl(ws[0], len(ws))) for ws in _WORDS22],
              hints=["The error names `T` three times - once for each place it is used.",
                     "Nothing in the file declares `T`, and a method has to declare its "
                     "own.",
                     "The declaration goes between `static` and the return type.",
                     "`static <T> T firstOf(List<T> items) {`",
                     "Nothing else changes: the call site infers `T` from `words`."],
              difficulty="Easy"),

        _jch("j22-gm-count", "One parameter, used twice", "Medium",
             "Write `countEqual`, a generic method that counts how many elements of a "
             "list equal a given value. Both the list's element type and the value's "
             "type are the same `T`. `main` uses it once on words and once on numbers.",
             _j22("    static <T> int countEqual(List<T> items, T target) {\n"
                  "        int count = 0;\n"
                  "        for (T item : items) {\n"
                  "            if (item.equals(target)) {\n"
                  "                count++;\n"
                  "            }\n"
                  "        }\n"
                  "        return count;\n"
                  "    }",
                  _RD_WORDS22
                  + "        String q = sc.next();\n"
                    "        System.out.println(countEqual(words, q));\n"
                    "        List<Integer> nums = new ArrayList<>();\n"
                    "        nums.add(words.size());\n"
                    "        nums.add(words.size());\n"
                    "        System.out.println(countEqual(nums, words.size()));"),
             "    static <T> int countEqual(List<T> items, T target) {\n"
             "        int count = 0;\n"
             "        for (T item : items) {\n"
             "            if (item.equals(target)) {\n"
             "                count++;\n"
             "            }\n"
             "        }\n"
             "        return count;\n"
             "    }",
             [_case("\n".join([str(len(ws)), " ".join(ws), q]),
                    _nl(sum(1 for w in ws if w == q), 2))
              for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                              (["x", "x", "x"], "x"), (["pear", "fig"], "fig"),
                              (["a", "b", "c"], "d"))],
             hints=["The signature is `static <T> int countEqual(List<T> items, "
                    "T target)` - one `T`, used in both parameters.",
                    "Compare with `.equals`, never `==` - module 17's rule, and the "
                    "reason this works for wrappers as well as Strings.",
                    "An enhanced `for` over `List<T>` gives you a `T` each time.",
                    "The count is an ordinary `int` - only the element type is generic.",
                    "The second call infers `T` as `Integer`, and `words.size()` "
                    "autoboxes to match."]),
    ],
    quiz=[
        _jq("`static void f(List<T> xs)` fails with 'cannot find symbol: class T'. Why?",
            ["The method never declared `T`",
             "T must be imported", "T must be a class", "Lists cannot be parameters"],
            0,
            "Add `<T>` between `static` and the return type and the symbol exists."),
        _jq("What is `Main.<String>first(xs)`?",
            ["A type witness - the type argument supplied explicitly",
             "A cast", "A wildcard", "A static import"],
            0,
            "Rarely needed, because inference nearly always has something to work "
            "from - but that is the syntax."),
    ],
))


# --- 22.2 Bounded type parameters --------------------------------------------

_M22.append(_jlesson(
    "m22-bounds", "Bounded type parameters",
    "`<T extends Comparable<T>>` - promising what `T` can do.",
    """
An unbounded `T` is almost useless *inside* the method. You can store it, pass
it on, put it in a list - but you cannot call anything on it except the handful
of methods every object has (`equals`, `hashCode`, `toString`), because the
compiler has no idea what it is.

```java
static <T> T max(List<T> items) {
    T best = items.get(0);
    for (T item : items) {
        if (item.compareTo(best) > 0) { ... }   // cannot find symbol: compareTo
    }
}
```

A **bound** fixes that by narrowing what may be substituted for `T`:

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

Now `T` may only be a type that implements `Comparable<T>` - and in exchange the
compiler lets you call `compareTo` on it. **A bound is a two-way deal: it
restricts the caller and it enables the method.**

**`extends` means "extends or implements".** There is no `implements` keyword in
a bound: `<T extends Comparable<T>>` names an interface, `<T extends Number>`
names a class, and the same word covers both.

`<T extends Number>` is the other bound you will actually use. Every numeric
wrapper extends `Number`, which promises `intValue()`, `doubleValue()` and
friends:

```java
static <T extends Number> double total(List<T> items) {
    double sum = 0;
    for (T item : items) {
        sum += item.doubleValue();
    }
    return sum;
}
```

**Multiple bounds** are joined with `&`, and a class bound (if any) must come
first:

```java
static <T extends Comparable<T> & CharSequence> T longest(List<T> items) { ... }
```

`String` satisfies both, so `longest` accepts a `List<String>` and can call both
`length()` and `compareTo` inside.

**Why `Comparable<T>` and not just `Comparable`?** The raw version would hand
you `compareTo(Object)` and lose the checking again - module 21's whole
complaint. `T extends Comparable<T>` says "comparable **to its own type**",
which is what `String`, `Integer` and every well-behaved class actually
implement.
""",
    warmup=[
        _jq("Why can't an unbounded `T` call `compareTo`?",
            ["The compiler has no idea what T is, so it only allows Object's methods",
             "compareTo is private",
             "T is always a String",
             "Generic methods cannot call methods"],
            0,
            "A bound is how you tell the compiler what T can do."),
        _jq("In `<T extends Comparable<T>>`, what does `extends` mean?",
            ["Extends OR implements - a bound uses the same word for both",
             "Only class inheritance",
             "Only interface implementation",
             "Nothing; it is optional"],
            0,
            "There is no `implements` keyword in a bound."),
    ],
    exercises=[
        _je("j22-bd-max", "Bound it so you can compare it",
            "`max` walks a list and keeps the largest element. Replace `____` with the "
            "signature that promises `T` is comparable to itself.",
            _j22("    static <T extends Comparable<T>> T max(List<T> items) {\n"
                 "        T best = items.get(0);\n"
                 "        for (T item : items) {\n"
                 "            if (item.compareTo(best) > 0) {\n"
                 "                best = item;\n"
                 "            }\n"
                 "        }\n"
                 "        return best;\n"
                 "    }",
                 _RD_NUMS22 + "        System.out.println(max(nums));"),
            "    static <T extends Comparable<T>> T max(List<T> items) {",
            [_ncase22(xs, max(xs)) for xs in _NUMS22],
            hints=["The body calls `compareTo`, so the bound has to promise it.",
                   "The interface is `Comparable`, parameterized on `T` itself.",
                   "`static <T extends Comparable<T>> T max(List<T> items) {`",
                   "`Integer` implements `Comparable<Integer>`, so a `List<Integer>` "
                   "satisfies the bound."],
            difficulty="Medium"),

        _jfix("j22-bd-missing", "The bound that was left out",
              "This does not compile: *cannot find symbol - method compareTo(T)*. `T` "
              "is unbounded, so the compiler will only let you call `Object`'s methods "
              "on it. Add the bound that makes `compareTo` legal.",
              _j22("    static <T> T smallest(List<T> items) {\n"
                   "        T best = items.get(0);\n"
                   "        for (T item : items) {\n"
                   "            if (item.compareTo(best) < 0) {\n"
                   "                best = item;\n"
                   "            }\n"
                   "        }\n"
                   "        return best;\n"
                   "    }",
                   _RD_WORDS22
                   + "        System.out.println(smallest(words));\n"
                     "        System.out.println(words.size());"),
              _j22("    static <T extends Comparable<T>> T smallest(List<T> items) {\n"
                   "        T best = items.get(0);\n"
                   "        for (T item : items) {\n"
                   "            if (item.compareTo(best) < 0) {\n"
                   "                best = item;\n"
                   "            }\n"
                   "        }\n"
                   "        return best;\n"
                   "    }",
                   _RD_WORDS22
                   + "        System.out.println(smallest(words));\n"
                     "        System.out.println(words.size());"),
              [_wcase22(ws, _nl(min(ws), len(ws))) for ws in _WORDS22],
              hints=["The body is correct. The signature is not promising enough.",
                     "Only the type parameter declaration changes.",
                     "`<T extends Comparable<T>>`",
                     "`String` implements `Comparable<String>`, so the call site still "
                     "compiles unchanged.",
                     "Smallest by `compareTo` on Strings means dictionary order, not "
                     "length."],
              difficulty="Medium"),

        _je("j22-bd-number", "A bound that is a class",
            "`total` adds up any list of numbers, whatever the wrapper. Replace `____` "
            "with the call that turns one element into a `double`.",
            _j22("    static <T extends Number> double total(List<T> items) {\n"
                 "        double sum = 0;\n"
                 "        for (T item : items) {\n"
                 "            sum += item.doubleValue();\n"
                 "        }\n"
                 "        return sum;\n"
                 "    }",
                 _RD_NUMS22 + "        System.out.println(total(nums));"),
            "item.doubleValue()",
            [_ncase22(xs, str(float(sum(xs)))) for xs in _NUMS22],
            hints=["`Number` is an abstract class every wrapper extends, and the bound "
                   "is what lets you call its methods.",
                   "It promises `intValue()`, `doubleValue()`, `longValue()` and "
                   "`floatValue()`.",
                   "`item.doubleValue()`",
                   "The running total is a `double`, so the printed result ends in "
                   "`.0`."],
            difficulty="Easy"),

        _jch("j22-bd-both", "Largest and smallest", "Medium",
             "Write `max` and `min` as two bounded generic methods, then print the "
             "largest word and the smallest word (dictionary order, via `compareTo`).",
             _j22("    static <T extends Comparable<T>> T max(List<T> items) {\n"
                  "        T best = items.get(0);\n"
                  "        for (T item : items) {\n"
                  "            if (item.compareTo(best) > 0) {\n"
                  "                best = item;\n"
                  "            }\n"
                  "        }\n"
                  "        return best;\n"
                  "    }\n"
                  "\n"
                  "    static <T extends Comparable<T>> T min(List<T> items) {\n"
                  "        T best = items.get(0);\n"
                  "        for (T item : items) {\n"
                  "            if (item.compareTo(best) < 0) {\n"
                  "                best = item;\n"
                  "            }\n"
                  "        }\n"
                  "        return best;\n"
                  "    }",
                  _RD_WORDS22
                  + "        System.out.println(max(words));\n"
                    "        System.out.println(min(words));"),
             "    static <T extends Comparable<T>> T max(List<T> items) {\n"
             "        T best = items.get(0);\n"
             "        for (T item : items) {\n"
             "            if (item.compareTo(best) > 0) {\n"
             "                best = item;\n"
             "            }\n"
             "        }\n"
             "        return best;\n"
             "    }\n"
             "\n"
             "    static <T extends Comparable<T>> T min(List<T> items) {\n"
             "        T best = items.get(0);\n"
             "        for (T item : items) {\n"
             "            if (item.compareTo(best) < 0) {\n"
             "                best = item;\n"
             "            }\n"
             "        }\n"
             "        return best;\n"
             "    }",
             [_wcase22(ws, _nl(max(ws), min(ws))) for ws in _WORDS22],
             hints=["Both methods have the same bound; only the comparison flips.",
                    "`static <T extends Comparable<T>> T max(List<T> items) {`",
                    "Seed `best` with element 0 and walk the whole list - the first "
                    "element compared with itself is harmless.",
                    "Use `> 0` for max and `< 0` for min, so ties keep the earlier "
                    "element.",
                    "Two lines out: the largest word, then the smallest."]),
    ],
    quiz=[
        _jq("What does a bound give the METHOD?",
            ["Permission to call the bound type's methods on `T`",
             "Faster code", "A cast", "A default value for T"],
            0,
            "And it costs the caller: only types satisfying the bound may be "
            "substituted."),
        _jq("Which bound lets you call `doubleValue()`?",
            ["<T extends Number>", "<T extends Comparable<T>>", "<T>", "<T extends Object>"],
            0,
            "`Number` is the abstract class every numeric wrapper extends."),
    ],
))


# --- 22.3 Generic classes with bounds, and generic interfaces ----------------

_M22.append(_jlesson(
    "m22-types", "Bounds on classes, and generic interfaces",
    "The same two ideas, moved from a method onto a type.",
    """
A **class** can carry a bound too, and it means the same thing: everything
inside may rely on it.

```java
class Range<T extends Comparable<T>> {
    private final T low;
    private final T high;

    Range(T low, T high) { this.low = low; this.high = high; }

    boolean contains(T value) {
        return low.compareTo(value) <= 0 && high.compareTo(value) >= 0;
    }
}
```

`new Range<>(1, 10)` and `new Range<>("ada", "zed")` both work, because
`Integer` and `String` are each comparable to themselves. `Range<Scanner>` does
not compile - the bound rejects it at the declaration, not deep inside a method.

**Interfaces are generic in exactly the same way**, and this is how the whole
collections framework is built:

```java
interface Container<T> {
    void put(T item);
    T get(int i);
    int size();
}
```

A class implements it by **supplying the type argument**, and there are two very
different ways to do that:

```java
class ListContainer<T> implements Container<T>   // still generic: T passes through
class WordContainer implements Container<String> // fixed: T is String, forever
```

The first stays open, so `ListContainer<Integer>` is possible; the second closes
the type down and its methods are written with `String` spelled out. Both are
legitimate - pick the one that matches how much freedom the class actually
needs.

**The implementing methods must be `public`** - module 14's rule, unchanged:
everything in an interface is public, and an override may not narrow access.

```java
class ListContainer<T> implements Container<T> {
    private final List<T> items = new ArrayList<>();

    @Override
    public void put(T item) { items.add(item); }
}
```

**A mismatched type argument is a compile error, and a clear one.** Writing
`class ListContainer<T> implements Container<String>` while the methods take `T`
fails with *ListContainer is not abstract and does not override abstract method
put(String)* - the class promised one thing and implemented another.
""",
    warmup=[
        _jq("`class Range<T extends Comparable<T>>` - when is `Range<Scanner>` rejected?",
            ["At the declaration, because Scanner does not satisfy the bound",
             "At run time", "Never", "Only if contains() is called"],
            0,
            "A bound on a class is checked wherever the class is parameterized."),
        _jq("`class WordContainer implements Container<String>` - is WordContainer generic?",
            ["No - it fixes T to String", "Yes, it has one type parameter",
             "Yes, two", "Only if the interface is"],
            0,
            "Supplying a concrete type argument closes the type down. Both styles are "
            "legal."),
    ],
    exercises=[
        _je("j22-cls-bound", "A bound on the class",
            "`Range` compares values, so its type parameter has to promise it is "
            "comparable. Replace `____` with the class header.",
            _j22t("""
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
""",
                  "",
                  "        int lo = sc.nextInt();\n"
                  "        int hi = sc.nextInt();\n"
                  "        int q = sc.nextInt();\n"
                  "        Range<Integer> r = new Range<>(lo, hi);\n"
                  "        System.out.println(r);\n"
                  "        System.out.println(r.contains(q));"),
            "class Range<T extends Comparable<T>> {",
            [_case(f"{lo} {hi} {q}", _nl(f"{lo}..{hi}", _jbool(lo <= q <= hi)))
             for (lo, hi, q) in ((1, 10, 5), (1, 10, 10), (0, 3, 4), (-5, -1, -3),
                                 (2, 2, 2))],
            hints=["The body calls `compareTo` on `low` and `high`, so the bound has to "
                   "promise it.",
                   "It is the same bound a generic method would use.",
                   "`class Range<T extends Comparable<T>> {`",
                   "`Range<Integer>` then satisfies it, because `Integer` implements "
                   "`Comparable<Integer>`."],
            difficulty="Medium"),

        _je("j22-iface-impl", "Implementing a generic interface",
            "`ListContainer` implements `Container` while staying generic itself - the "
            "type parameter passes straight through. Replace `____` with its class "
            "header.",
            _j22t("""
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
""",
                  "",
                  _RD_WORDS22
                  + "        Container<String> box = new ListContainer<>();\n"
                    "        for (String w : words) {\n"
                    "            box.put(w);\n"
                    "        }\n"
                    "        System.out.println(box.size());\n"
                    "        System.out.println(box.get(0));"),
            "class ListContainer<T> implements Container<T> {",
            [_wcase22(ws, _nl(len(ws), ws[0])) for ws in _WORDS22],
            hints=["The class stays open, so it declares its own `T` and hands the same "
                   "one to the interface.",
                   "`class Name<T> implements Interface<T> {`",
                   "`class ListContainer<T> implements Container<T> {`",
                   "`main` declares the variable as the interface `Container<String>` "
                   "and constructs the implementation - module 14's rule with a type "
                   "argument attached."],
            difficulty="Medium"),

        _jfix("j22-iface-mismatch", "Promised String, implemented T",
              "This says `implements Container<String>` while its methods take and "
              "return `T`, so it implements nothing the interface asked for: *is not "
              "abstract and does not override abstract method put(String)*. Make the "
              "class hand its own type parameter to the interface.",
              _j22t("""
interface Container<T> {
    void put(T item);

    T get(int i);

    int size();
}

class ListContainer<T> implements Container<String> {
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
""",
                    "",
                    _RD_WORDS22
                    + "        Container<String> box = new ListContainer<>();\n"
                      "        for (String w : words) {\n"
                      "            box.put(w);\n"
                      "        }\n"
                      "        System.out.println(box.size());\n"
                      "        System.out.println(box.get(box.size() - 1));"),
              _j22t("""
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
""",
                    "",
                    _RD_WORDS22
                    + "        Container<String> box = new ListContainer<>();\n"
                      "        for (String w : words) {\n"
                      "            box.put(w);\n"
                      "        }\n"
                      "        System.out.println(box.size());\n"
                      "        System.out.println(box.get(box.size() - 1));"),
              [_wcase22(ws, _nl(len(ws), ws[-1])) for ws in _WORDS22],
              hints=["The methods are right; the `implements` clause is wrong.",
                     "The class already has a type parameter of its own - hand that one "
                     "to the interface.",
                     "`class ListContainer<T> implements Container<T> {`",
                     "`main` is unchanged: `new ListContainer<>()` infers `String` from "
                     "the `Container<String>` on the left.",
                     "Fixing it the other way - spelling `String` through every method "
                     "- would also compile, but would close the class down to one type."],
              difficulty="Medium"),

        _jch("j22-cls-two", "One bounded class, two parameterizations", "Medium",
             "Using the `Range` class already written, read a low and high word and a "
             "query word, then a low, high and query number. Print each range, and "
             "whether it contains its query - four lines: the word range, its answer, "
             "the number range, its answer.",
             _j22t("""
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
""",
                   "",
                   "        String wlo = sc.next();\n"
                   "        String whi = sc.next();\n"
                   "        String wq = sc.next();\n"
                   "        int lo = sc.nextInt();\n"
                   "        int hi = sc.nextInt();\n"
                   "        int q = sc.nextInt();\n"
                   "        Range<String> words = new Range<>(wlo, whi);\n"
                   "        Range<Integer> nums = new Range<>(lo, hi);\n"
                   "        System.out.println(words);\n"
                   "        System.out.println(words.contains(wq));\n"
                   "        System.out.println(nums);\n"
                   "        System.out.println(nums.contains(q));"),
             "        Range<String> words = new Range<>(wlo, whi);\n"
             "        Range<Integer> nums = new Range<>(lo, hi);\n"
             "        System.out.println(words);\n"
             "        System.out.println(words.contains(wq));\n"
             "        System.out.println(nums);\n"
             "        System.out.println(nums.contains(q));",
             [_case(f"{wlo} {whi} {wq}\n{lo} {hi} {q}",
                    _nl(f"{wlo}..{whi}", _jbool(wlo <= wq <= whi),
                        f"{lo}..{hi}", _jbool(lo <= q <= hi)))
              for (wlo, whi, wq, lo, hi, q) in (
                  ("ada", "zed", "moss", 1, 10, 5),
                  ("bo", "cy", "zed", 0, 3, 4),
                  ("a", "b", "a", -5, -1, -3),
                  ("mid", "mid", "mid", 2, 2, 2),
                  ("apple", "pear", "fig", 7, 9, 9))],
             hints=["One class, two parameterizations - `Range<String>` and "
                    "`Range<Integer>`.",
                    "Both satisfy the bound, which is why no cast or duplicate class is "
                    "needed.",
                    "`new Range<>(wlo, whi)` infers the type argument from the left.",
                    "Printing a range calls its `toString`, which gives `low..high`.",
                    "Four lines, in the order the prompt lists them."]),
    ],
    quiz=[
        _jq("Why must `public void put(T item)` be public in `ListContainer`?",
            ["Interface members are public, and an override may not narrow access",
             "Generics require it", "Because the field is private",
             "It does not have to be"],
            0,
            "Module 14's rule, unchanged by generics."),
        _jq("`class WordContainer implements Container<String>` closes T down. When is "
            "that the right call?",
            ["When the class genuinely only ever holds Strings",
             "Never", "Always - it is simpler", "Only for interfaces with one method"],
            0,
            "Passing `T` through keeps it open; supplying a concrete argument fixes it. "
            "Both are legitimate."),
    ],
))


# --- 22.4 Choosing between them ----------------------------------------------

_M22.append(_jlesson(
    "m22-choose", "Choosing, and the utility-method habit",
    "Generic method or generic class? A bound or a `Comparator`?",
    """
**Generic class or generic method?** The question is *what has the type*.

* A **class** is generic when its state has the type: a `Bag<T>` holds `T`s for
  its whole life.
* A **method** is generic when only one call has the type: `swap(list, i, j)`
  needs a `T` for a few lines and then forgets it.

When in doubt, prefer the method. It is smaller, it needs no object, and it can
be `static` - which module 21 showed a generic class's members cannot be.

```java
static <T> void swap(List<T> items, int i, int j) {
    T temp = items.get(i);
    items.set(i, items.get(j));
    items.set(j, temp);
}
```

That method is the reason `T` exists at all: written against `List<Object>` it
would not accept a `List<String>` (module 23's subject), and written three times
for three element types it would be three copies of the same bug.

**A bound or a `Comparator`?** Both let you order a `T`, and module 20 already
made the distinction: `Comparable` is the type's *natural* order, a `Comparator`
is an order chosen at the call site.

```java
static <T extends Comparable<T>> T max(List<T> items)      // natural order
static <T> T maxBy(List<T> items, Comparator<T> order)     // caller's order
```

The second needs no bound at all - the caller supplied the ability to compare,
so `T` can stay unbounded. **Ask for what you need and no more** is the general
rule, and it is exactly what module 23's wildcards refine.

Because lambdas are not part of this course, a `Comparator` here is a named
class, as in module 20:

```java
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
}
```

**Two bounds when you need two abilities.** `<T extends Comparable<T> &
CharSequence>` promises both ordering and `length()`; `String` satisfies it, and
a method can then break length ties by dictionary order without knowing it is
working on Strings.
""",
    warmup=[
        _jq("`swap(list, i, j)` - class or method?",
            ["A generic method: only the call has the type",
             "A generic class", "Both", "Neither - use Object"],
            0,
            "No state holds a `T` afterwards, so nothing needs to be an object."),
        _jq("`static <T> T maxBy(List<T> xs, Comparator<T> order)` has no bound. Why not?",
            ["The caller supplied the ability to compare, so T needs no promise of its own",
             "Comparators cannot be bounded",
             "It is a mistake",
             "Because T is always String"],
            0,
            "Ask for what you need and no more."),
    ],
    exercises=[
        _je("j22-ch-swap", "The swap utility",
            "`swap` exchanges two elements of any list. Replace `____` with the line "
            "that saves the first element before it is overwritten.",
            _j22("    static <T> void swap(List<T> items, int i, int j) {\n"
                 "        T temp = items.get(i);\n"
                 "        items.set(i, items.get(j));\n"
                 "        items.set(j, temp);\n"
                 "    }",
                 _RD_WORDS22
                 + "        swap(words, 0, words.size() - 1);\n"
                   "        System.out.println(words);"),
            "T temp = items.get(i);",
            [_wcase22(ws, _jlist22([ws[-1]] + ws[1:-1] + [ws[0]]) if len(ws) > 1
                      else _jlist22(ws))
             for ws in _WORDS22],
            hints=["Without a temporary, the first assignment destroys the value you "
                   "still need.",
                   "The temporary's type is the list's element type - the method's own "
                   "`T`.",
                   "`T temp = items.get(i);`",
                   "`set` overwrites and returns the old value, but the temporary is "
                   "clearer."],
            difficulty="Easy"),

        _jfix("j22-ch-swap-bug", "A swap that loses an element",
              "This swap overwrites position `i` before reading it, so both positions "
              "end up holding the same value. Fix it with a temporary of the right "
              "type.",
              _j22("    static <T> void swap(List<T> items, int i, int j) {\n"
                   "        items.set(i, items.get(j));\n"
                   "        items.set(j, items.get(i));\n"
                   "    }",
                   _RD_WORDS22
                   + "        swap(words, 0, words.size() - 1);\n"
                     "        System.out.println(words);"),
              _j22("    static <T> void swap(List<T> items, int i, int j) {\n"
                   "        T temp = items.get(i);\n"
                   "        items.set(i, items.get(j));\n"
                   "        items.set(j, temp);\n"
                   "    }",
                   _RD_WORDS22
                   + "        swap(words, 0, words.size() - 1);\n"
                     "        System.out.println(words);"),
              [_wcase22(ws, _jlist22([ws[-1]] + ws[1:-1] + [ws[0]]) if len(ws) > 1
                        else _jlist22(ws))
               for ws in _WORDS22],
              hints=["Trace it on `[a, b, c]`: after the first line position 0 holds "
                     "`c`, and the second line reads it back.",
                     "Save the old value first.",
                     "`T temp = items.get(i);` as the new first line.",
                     "Then the last line writes `temp`, not `items.get(i)`.",
                     "The single-element case looks identical either way, which is why "
                     "it is not a useful test on its own."],
              difficulty="Medium"),

        _je("j22-ch-maxby", "Order supplied by the caller",
            "`maxBy` takes the ordering as an argument, so `T` needs no bound at all. "
            "Replace `____` with its signature line.",
            _j22t("""
class ByLength implements Comparator<String> {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
}
""",
                  "    static <T> T maxBy(List<T> items, Comparator<T> order) {\n"
                  "        T best = items.get(0);\n"
                  "        for (T item : items) {\n"
                  "            if (order.compare(item, best) > 0) {\n"
                  "                best = item;\n"
                  "            }\n"
                  "        }\n"
                  "        return best;\n"
                  "    }",
                  _RD_WORDS22
                  + "        System.out.println(maxBy(words, new ByLength()));"),
            "    static <T> T maxBy(List<T> items, Comparator<T> order) {",
            [_wcase22(ws, max(ws, key=lambda w: len(w))) for ws in _WORDS22],
            hints=["Nothing is called on `T` itself - only on the comparator - so no "
                   "bound is needed.",
                   "Two parameters: the list, and a `Comparator<T>`.",
                   "`static <T> T maxBy(List<T> items, Comparator<T> order) {`",
                   "`order.compare(a, b) > 0` means `a` comes after `b`, so ties keep "
                   "the earlier element."],
            difficulty="Medium"),

        _jch("j22-ch-multibound", "Two bounds at once", "Hard",
             "Write `longest`, which returns the longest element of a list; if two are "
             "equally long, the one that is larger in dictionary order wins. It needs "
             "both `length()` and `compareTo`, so it declares two bounds joined by `&`.",
             _j22("    static <T extends Comparable<T> & CharSequence> T longest(List<T> items) {\n"
                  "        T best = items.get(0);\n"
                  "        for (T item : items) {\n"
                  "            if (item.length() > best.length()) {\n"
                  "                best = item;\n"
                  "            } else if (item.length() == best.length()\n"
                  "                    && item.compareTo(best) > 0) {\n"
                  "                best = item;\n"
                  "            }\n"
                  "        }\n"
                  "        return best;\n"
                  "    }",
                  _RD_WORDS22 + "        System.out.println(longest(words));"),
             "    static <T extends Comparable<T> & CharSequence> T longest(List<T> items) {\n"
             "        T best = items.get(0);\n"
             "        for (T item : items) {\n"
             "            if (item.length() > best.length()) {\n"
             "                best = item;\n"
             "            } else if (item.length() == best.length()\n"
             "                    && item.compareTo(best) > 0) {\n"
             "                best = item;\n"
             "            }\n"
             "        }\n"
             "        return best;\n"
             "    }",
             [_wcase22(ws, max(ws, key=lambda w: (len(w), w)))
              for ws in (["ada", "bo", "cy"], ["solo"], ["ax", "ay", "b"],
                         ["pear", "figs", "kiwi"], ["alpha", "beta", "gamma", "d"])],
             hints=["Two bounds are joined with `&`: "
                    "`<T extends Comparable<T> & CharSequence>`.",
                    "`CharSequence` is what promises `length()`; `String` implements "
                    "both interfaces, so a `List<String>` satisfies the whole bound.",
                    "Seed `best` with element 0 and compare every element against it.",
                    "Longer always wins; equal length falls through to "
                    "`compareTo(best) > 0`.",
                    "Using `>` rather than `>=` keeps the earlier element when two are "
                    "identical."]),
    ],
    quiz=[
        _jq("When should the CLASS be generic rather than the method?",
            ["When its state holds the type for the object's whole life",
             "Always", "When the method is static", "When there is a bound"],
            0,
            "A `Bag<T>` holds `T`s; `swap` only borrows one for a few lines."),
        _jq("`<T extends Comparable<T> & CharSequence>` promises…",
            ["both compareTo and length()", "only compareTo", "only length()",
             "nothing - `&` is illegal in a bound"],
            0,
            "Multiple bounds are joined with `&`; a class bound, if there is one, must "
            "come first."),
    ],
))


# --- Capstone ----------------------------------------------------------------

_M22_CAP_HELPERS = (
    "    static <T> T first(List<T> items) {\n"
    "        return items.get(0);\n"
    "    }\n"
    "\n"
    "    static <T extends Comparable<T>> T max(List<T> items) {\n"
    "        T best = items.get(0);\n"
    "        for (T item : items) {\n"
    "            if (item.compareTo(best) > 0) {\n"
    "                best = item;\n"
    "            }\n"
    "        }\n"
    "        return best;\n"
    "    }\n"
    "\n"
    "    static <T> int countEqual(List<T> items, T target) {\n"
    "        int count = 0;\n"
    "        for (T item : items) {\n"
    "            if (item.equals(target)) {\n"
    "                count++;\n"
    "            }\n"
    "        }\n"
    "        return count;\n"
    "    }\n"
    "\n"
    "    static <T> void swap(List<T> items, int i, int j) {\n"
    "        T temp = items.get(i);\n"
    "        items.set(i, items.get(j));\n"
    "        items.set(j, temp);\n"
    "    }"
)

_M22_CAP_BODY = (
    "        int n = sc.nextInt();\n"
    "        List<String> words = new ArrayList<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            words.add(sc.next());\n"
    "        }\n"
    "        String q = sc.next();\n"
    "        int m = sc.nextInt();\n"
    "        List<Integer> nums = new ArrayList<>();\n"
    "        for (int i = 0; i < m; i++) {\n"
    "            nums.add(sc.nextInt());\n"
    "        }\n"
    "        System.out.println(first(words));\n"
    "        System.out.println(max(words));\n"
    "        System.out.println(countEqual(words, q));\n"
    "        System.out.println(first(nums));\n"
    "        System.out.println(max(nums));\n"
    "        swap(words, 0, words.size() - 1);\n"
    "        System.out.println(words);"
)


def _m22_cap_case(ws, q, xs):
    swapped = list(ws)
    swapped[0], swapped[-1] = swapped[-1], swapped[0]
    return _case("\n".join([str(len(ws)), " ".join(ws), q, str(len(xs)),
                            " ".join(str(x) for x in xs)]),
                 _nl(ws[0], max(ws), sum(1 for w in ws if w == q),
                     xs[0], max(xs), _jlist22(swapped)))


_M22_CAP = _jcap(
    "The generic toolbox",
    """
Write the four static utility methods every Java codebase ends up with, once
each, working on any element type.

* **`first(list)`** - the element at index 0, returned as its own type.
* **`max(list)`** - the largest element by natural order. Needs a bound.
* **`countEqual(list, target)`** - how many elements equal the target. One type
  parameter, used in both parameters.
* **`swap(list, i, j)`** - exchange two positions in place.

`main` then runs all four over a `List<String>` **and** a `List<Integer>`
without a single cast, which is the whole point: one implementation, every
element type.
""",
    _jch("j22-cap-toolbox", "The generic toolbox", "Hard",
         "Write the four generic methods described in the brief so the given `main` "
         "compiles and prints its six lines.",
         _j22(_M22_CAP_HELPERS, _M22_CAP_BODY),
         _M22_CAP_HELPERS,
         [_m22_cap_case(ws, q, xs) for (ws, q, xs) in (
             (["ada", "bo", "cy"], "bo", [3, 1, 2]),
             (["solo"], "solo", [5]),
             (["x", "x", "y"], "x", [-4, -9, -1]),
             (["pear", "fig", "apple"], "kiwi", [10, 10, 2]),
             (["alpha", "beta", "gamma", "d"], "beta", [7, 2, 9, 4]),
         )],
         hints=["Every one of them declares its own type parameter between `static` and "
                "the return type.",
                "`static <T> T first(List<T> items)` - the return type is the parameter.",
                "`max` calls `compareTo`, so it alone needs a bound: "
                "`<T extends Comparable<T>>`.",
                "Seed `max` with element 0 and use `> 0`, so ties keep the earlier "
                "element.",
                "`countEqual` takes `(List<T> items, T target)` - one `T` in two "
                "places - and compares with `.equals`.",
                "`swap` needs a `T temp` before the first `set`, or the value at `i` is "
                "lost.",
                "None of the four mentions `String` or `Integer` anywhere; the call "
                "sites infer both.",
                "The single-element cases swap position 0 with itself, which must leave "
                "the list unchanged."]),
    example_io="stdin:  3\n        ada bo cy\n        bo\n        3\n        3 1 2\n\n"
               "stdout: ada\n        cy\n        1\n        3\n        3\n"
               "        [cy, bo, ada]",
    rubric=[
        "All four methods are static and declare their own type parameter.",
        "`first` and `max` return `T`, not Object.",
        "`max` is the only one with a bound, and it is `<T extends Comparable<T>>`.",
        "`countEqual` uses a single `T` for both the list element and the target.",
        "`countEqual` compares with `.equals`, not `==`.",
        "`swap` uses a temporary of type `T` and modifies the list in place.",
        "No method mentions String or Integer, and no call site needs a cast.",
        "All six lines are printed in order.",
    ],
)


_MODULES.append(_jmod(
    22, 7, "Generics",
    "Generic methods and bounded type parameters",
    "Give a method its own type parameter, then promise what that type can do. "
    "`static <T>`, inference, `<T extends Comparable<T>>`, multiple bounds, bounded "
    "classes and generic interfaces - and when to reach for each.",
    """
Module 21 left a hole: a `static` member cannot use its class's type parameter.
This module fills it. A **method** can declare a type parameter of its own,
written between the modifiers and the return type, and it lives for exactly one
call.

That unlocks the utility method - `first`, `last`, `swap`, `countEqual` - written
once and correct for every element type. It also immediately runs into the
limit of an unbounded `T`: you can move it around, but you cannot call anything
on it, because the compiler does not know what it is.

A **bound** is the answer, and it is a trade in both directions: `<T extends
Comparable<T>>` restricts what the caller may substitute and, in exchange, lets
the body call `compareTo`. `<T extends Number>` does the same for the numeric
wrappers, `&` joins two bounds when you need two abilities, and the same syntax
works on a class or an interface.

The judgement calls are worth as much as the syntax: a class is generic when its
*state* has the type, a method when only one *call* does - and if the caller can
hand you a `Comparator`, `T` needs no bound at all.
""",
    _M22,
    capstone=_M22_CAP,
    objectives=[
        "Write a generic method, with the type parameter in the correct position.",
        "Explain why a static method needs its own type parameter rather than the class's.",
        "Rely on inference at the call site, and write a type witness when inference has nothing to work from.",
        "Use one type parameter across several parameters to tie their types together.",
        "Add a bound so the body can call methods on `T`, and say what the bound costs the caller.",
        "Use `<T extends Comparable<T>>` and `<T extends Number>` correctly, and join bounds with `&`.",
        "Put a bound on a generic class, and implement a generic interface with or without passing `T` through.",
        "Choose between a generic class and a generic method, and between a bound and a Comparator.",
    ],
    why="Generic methods are where generics stop being something you read and become "
        "something you write: every utility class in every codebase is a pile of them. "
        "Bounds are also the interview question - 'what can you actually do with a `T`?' "
        "- and the answer, 'nothing you have not promised', is the whole model in six "
        "words.",
    est_minutes=330,
    glossary=[
        _jg("generic method", "A method declaring its own type parameter, e.g. "
                              "`static <T> T first(List<T> xs)`."),
        _jg("type inference", "The compiler working out a type argument from the "
                              "arguments or the target type."),
        _jg("type witness", "An explicitly supplied type argument at a call site: "
                            "`Main.<String>first(xs)`."),
        _jg("bounded type parameter", "`<T extends X>` - T may only be an X, and in "
                                      "exchange the body may use X's members."),
        _jg("upper bound", "The `extends X` half of a bound: X is the ceiling."),
        _jg("multiple bounds", "`<T extends A & B>` - two promises at once; a class "
                               "bound must come first."),
        _jg("Comparable<T>", "The natural-order interface, parameterized on the type "
                             "itself so `compareTo` is type-safe."),
        _jg("Number", "The abstract superclass of the numeric wrappers, promising "
                      "intValue(), doubleValue() and friends."),
        _jg("generic interface", "An interface with its own type parameters, e.g. "
                                 "`interface Container<T>`."),
    ],
    cheatsheet="""
```java
// --- generic method: <T> between the modifiers and the return type --------
static <T> void printAll(List<T> items) { ... }
static <T> T last(List<T> items) { ... }          // generic return type
static <T> int countEqual(List<T> xs, T target)   // one T tying two parameters

last(names);                    // T inferred as String
Main.<String>last(names);       // type witness, when inference has nothing

// --- bounds: restrict the caller, enable the body -------------------------
static <T extends Comparable<T>> T max(List<T> xs) { xs.get(0).compareTo(...); }
static <T extends Number> double total(List<T> xs) { ... doubleValue() ... }
static <T extends Comparable<T> & CharSequence> T longest(List<T> xs) { ... }
// `extends` covers implements too. A class bound comes first, before any &.

// --- bounds on types ------------------------------------------------------
class Range<T extends Comparable<T>> { ... }      // checked where it is used

interface Container<T> { void put(T item); T get(int i); }
class ListContainer<T> implements Container<T> { ... }    // T passes through
class WordContainer implements Container<String> { ... }  // T fixed to String
// implementing methods are public - an override may not narrow access

// --- choosing -------------------------------------------------------------
// state has the type   -> generic CLASS      (Bag<T> holds Ts for its life)
// one call has it      -> generic METHOD     (swap borrows a T for 3 lines)
// caller can order it  -> Comparator<T>, and T needs no bound at all
```
""",
    self_check=[
        "Can you write a generic method's header from memory, with `<T>` in the right place?",
        "Can you say why `static void f(List<T> xs)` fails, and what the error message is?",
        "Can you explain what a type witness is and when you would ever need one?",
        "Can you say what an unbounded `T` can and cannot do inside a method?",
        "Can you give the bound that lets you call `compareTo`, and the one for `doubleValue()`?",
        "Can you explain why it is `Comparable<T>` rather than raw `Comparable`?",
        "Can you write a class with a bound, and implement a generic interface both ways?",
        "Can you argue for a generic method over a generic class in a specific case?",
    ],
    review=[
        _jq("```java\nstatic <T> T pick(List<T> xs) { return xs.get(0); }\n```\n"
            "`String s = pick(names);` compiles because…",
            ["T was inferred as String from the argument",
             "of an implicit cast", "T defaults to String", "pick is overloaded"],
            0,
            "Inference reads the argument's type and substitutes it everywhere `T` "
            "appears, including the return type."),
        _jq("Which line does NOT compile?",
            ["static <T> T biggest(List<T> xs) { return xs.get(0).compareTo(...) > 0 ? ... ; }",
             "static <T extends Comparable<T>> T biggest(List<T> xs) { ... }",
             "static <T extends Number> double total(List<T> xs) { ... }",
             "class Range<T extends Comparable<T>> { ... }"],
            0,
            "An unbounded `T` has no `compareTo`. The other three all state the promise "
            "they rely on."),
        _jq("`static <T> T maxBy(List<T> xs, Comparator<T> order)` needs no bound because…",
            ["the caller supplies the comparison, so nothing is called on T itself",
             "Comparator is generic",
             "maxBy is static",
             "T is always Comparable anyway"],
            0,
            "Ask for what you need and no more - the same instinct wildcards refine in "
            "module 23."),
        _jq("In the capstone, why can one `max` serve both the words and the numbers?",
            ["String and Integer both implement Comparable of themselves, satisfying the bound",
             "Because both are objects",
             "Because max is static",
             "Because the lists are the same size"],
            0,
            "One implementation, every element type that keeps the promise."),
    ],
    milestone="You can write the utility methods a codebase actually needs - generic, "
              "bounded exactly as far as necessary, and needing no casts at any call "
              "site.",
))
