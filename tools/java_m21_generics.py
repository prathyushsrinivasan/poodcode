# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 21 - Type parameters and generic classes.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Opens Part 7. Modules 17-20 CONSUMED generics (`List<String>`) without ever
# explaining them; this is where the learner writes their own. Declaring a type
# parameter (`<T>`, `<A, B>`) becomes legal at this module - the scope linter
# reserves those tokens for it - and wildcards (`? extends`, `? super`, `<?>`)
# stay reserved for module 23.
#
# The order is deliberate: the COST of not having generics (lesson 21.1: an
# Object field, a cast, and a ClassCastException at run time) before the cure.
# Every later idea in the part is a variation on "a class can take a type the
# way a method takes a value".
# ---------------------------------------------------------------------------

_M21 = []


# The plain-Object container lesson 21.1 argues against, and the generic one
# every later lesson builds on. Kept as module-level text so the same class body
# is reused verbatim across exercises rather than re-typed (and re-mistyped).
_OBJECT_BOX = """
class ObjectBox {
    private Object value;

    ObjectBox(Object value) {
        this.value = value;
    }

    Object get() {
        return value;
    }
}
"""

_BOX = """
class Box<T> {
    private T value;

    Box(T value) {
        this.value = value;
    }

    T get() {
        return value;
    }

    void set(T value) {
        this.value = value;
    }
}
"""

_PAIR = """
class Pair<A, B> {
    private final A first;
    private final B second;

    Pair(A first, B second) {
        this.first = first;
        this.second = second;
    }

    A getFirst() {
        return first;
    }

    B getSecond() {
        return second;
    }

    @Override
    public String toString() {
        return first + "=" + second;
    }
}
"""

_BAG = """
class Bag<T> {
    private final List<T> items = new ArrayList<>();

    void add(T item) {
        items.add(item);
    }

    T get(int i) {
        return items.get(i);
    }

    int size() {
        return items.size();
    }

    boolean contains(T item) {
        return items.contains(item);
    }

    @Override
    public String toString() {
        return items.toString();
    }
}
"""


def _j21(types, body):
    """Helper class(es) above a Scanner-opening main - the Part 7 program shape."""
    return _joop(types.strip("\n"), body)


_WORDS = (["ada", "bo"], ["solo"], ["x", "yy", "zzz"], ["one", "two"],
          ["alpha", "beta", "gamma", "d"])


def _wcase21(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


# --- 21.1 The cost of no generics -------------------------------------------

_M21.append(_jlesson(
    "m21-why", "What generics are for",
    "An `Object` field, a cast, and a crash at run time - the problem generics remove.",
    """
You have been using generics since module 17 without writing one. `List<String>`
means "a list whose elements are Strings", and the `<String>` is a **type
argument** - a type handed to a class the way an argument is handed to a method.

To see why that matters, write a container without it.

```java
class ObjectBox {
    private Object value;
    ObjectBox(Object value) { this.value = value; }
    Object get() { return value; }
}
```

`Object` is the root of every reference type (module 13), so this holds
anything. It also *forgets* what it holds:

```java
ObjectBox box = new ObjectBox("ada");
String s = (String) box.get();   // the cast is the tax you pay
```

Two problems, and the second is the serious one:

1. **Every read needs a cast.** Noise, on every single use.
2. **The compiler cannot check the cast.** `get()` returns `Object`, so
   `(Integer) box.get()` compiles perfectly and throws `ClassCastException`
   when it runs. The mistake is made at compile time and discovered in
   production.

The generic version moves the discovery back to compile time:

```java
class Box<T> {
    private T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}

Box<String> box = new Box<>("ada");
String s = box.get();            // no cast
Integer n = box.get();           // COMPILE ERROR, not a run-time crash
```

**That is the whole point of generics: turn a class of run-time
`ClassCastException`s into compile errors, and delete the casts.**

Before generics (Java 4 and earlier) the collections were raw, and every
`list.get(i)` came back as `Object`. Raw types still compile today for backward
compatibility:

```java
List names = new ArrayList();    // RAW - legal, and a bad idea
names.add("ada");
names.add(42);                   // the compiler has nothing to object to
```

A raw type is not "a list of anything" - it is a list that has switched its
type checking off. `javac` warns (`unchecked call`) and then lets you walk into
the crash. **Never write one in new code.**

**The conventional single-letter names** - they are only conventions, but
everybody follows them:

| Letter | Means |
|---|---|
| `T` | Type |
| `E` | Element (used by the collections) |
| `K`, `V` | Key, Value (used by `Map`) |
| `A`, `B` | when two types have no better names |
| `R` | Return type |
""",
    warmup=[
        _jq("`ObjectBox` holds an `Object`. What does `(Integer) box.get()` do when the "
            "box actually holds a String?",
            ["Compiles, then throws ClassCastException at run time",
             "Fails to compile",
             "Returns null",
             "Returns 0"],
            0,
            "The compiler only knows the static type is `Object`, so it lets the cast "
            "through and the JVM checks it - too late."),
        _jq("What does the `<String>` in `List<String>` supply?",
            ["A type argument - a type passed to a class",
             "A cast", "A subclass", "A constructor parameter"],
            0,
            "A class can take types the way a method takes values. That is the whole "
            "idea of the part."),
    ],
    exercises=[
        _je("j21-why-cast", "The cast tax",
            "`ObjectBox.get()` returns `Object`, so the value has to be cast back "
            "before you can use it as a String. Replace `____` with that cast "
            "expression.",
            _j21(_OBJECT_BOX,
                 "        String word = sc.next();\n"
                 "        ObjectBox box = new ObjectBox(word);\n"
                 "        String out = (String) box.get();\n"
                 "        System.out.println(out.toUpperCase());\n"
                 "        System.out.println(out.length());"),
            "(String) box.get()",
            [_case(w, _nl(w.upper(), len(w)))
             for w in ("ada", "bo", "generics", "x", "typeparam")],
            hints=["`get()` is declared to return `Object`, and an `Object` cannot be "
                   "assigned to a `String` without a cast.",
                   "A cast is the target type in parentheses, before the expression.",
                   "`(String) box.get()`",
                   "This line is exactly what a generic `Box<String>` would let you "
                   "delete."],
            difficulty="Intro"),

        _jfix("j21-why-cce", "The cast the compiler cannot check",
              "This casts the box's contents to `Integer`, and the box holds a String. "
              "The compiler accepts it - `get()` returns `Object`, so any cast is "
              "plausible - and the JVM throws `ClassCastException` when it runs. Fix "
              "it to read the String out and print it, then print its length.",
              _j21(_OBJECT_BOX,
                   "        String word = sc.next();\n"
                   "        ObjectBox box = new ObjectBox(word);\n"
                   "        Integer out = (Integer) box.get();\n"
                   "        System.out.println(out);\n"
                   "        System.out.println(out + 1);"),
              _j21(_OBJECT_BOX,
                   "        String word = sc.next();\n"
                   "        ObjectBox box = new ObjectBox(word);\n"
                   "        String out = (String) box.get();\n"
                   "        System.out.println(out);\n"
                   "        System.out.println(out.length());"),
              [_case(w, _nl(w, len(w)))
               for w in ("ada", "bo", "generics", "x", "typeparam")],
              hints=["Run it as it stands and read the exception: the JVM refuses to "
                     "call a String an Integer.",
                     "The declared type of `out` and the cast both have to become "
                     "`String`.",
                     "`String out = (String) box.get();`",
                     "The second line then prints `out.length()` rather than `out + 1`.",
                     "A `Box<String>` would have rejected the Integer version at "
                     "compile time - that is the improvement this whole part is about."],
              difficulty="Medium"),

        _jfix("j21-why-raw", "A raw list lets anything in",
              "`List names = new ArrayList();` is a **raw** type: type checking is "
              "switched off, so the stray `names.add(42)` compiles and the cast in the "
              "loop blows up. Parameterize the list as `List<String>`, delete the stray "
              "add and the now-unnecessary cast, and print each word in upper case.",
              _jscan("        int n = sc.nextInt();\n"
                     "        List names = new ArrayList();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        names.add(42);\n"
                     "        for (Object o : names) {\n"
                     "            String s = (String) o;\n"
                     "            System.out.println(s.toUpperCase());\n"
                     "        }"),
              _jscan("        int n = sc.nextInt();\n"
                     "        List<String> names = new ArrayList<>();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            names.add(sc.next());\n"
                     "        }\n"
                     "        for (String s : names) {\n"
                     "            System.out.println(s.toUpperCase());\n"
                     "        }"),
              [_wcase21(ws, _nl(*[w.upper() for w in ws])) for ws in _WORDS],
              hints=["The words do print - and then the program dies on the 42.",
                     "`List<String> names = new ArrayList<>();` makes `add(42)` a "
                     "compile error rather than a time bomb.",
                     "Once the list is parameterized the loop variable can be a "
                     "`String`, so the cast goes away.",
                     "`for (String s : names)`",
                     "Deleting `names.add(42)` is part of the fix - it was never "
                     "supposed to be there."],
              difficulty="Medium"),

        _jch("j21-why-typed", "Same job, no casts", "Easy",
             "Read `n` words into a `List<String>`, print the list, then print the "
             "total number of characters across all of them. No `Object` and no casts "
             "anywhere.",
             _jscan("        int n = sc.nextInt();\n"
                    "        List<String> words = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            words.add(sc.next());\n"
                    "        }\n"
                    "        int total = 0;\n"
                    "        for (String w : words) {\n"
                    "            total += w.length();\n"
                    "        }\n"
                    "        System.out.println(words);\n"
                    "        System.out.println(total);"),
             "        int total = 0;\n"
             "        for (String w : words) {\n"
             "            total += w.length();\n"
             "        }\n"
             "        System.out.println(words);\n"
             "        System.out.println(total);",
             [_wcase21(ws, _nl("[" + ", ".join(ws) + "]", sum(len(w) for w in ws)))
              for ws in _WORDS],
             hints=["The list is already declared as `List<String>`, so the loop "
                    "variable can be a `String` directly.",
                    "An enhanced `for` reads best here.",
                    "`total += w.length();`",
                    "Print the list first, then the total - two lines."]),
    ],
    quiz=[
        _jq("What is a **raw type**?",
            ["A generic type used with no type argument, which turns its type checking off",
             "A primitive type",
             "A type with no methods",
             "A type declared outside a package"],
            0,
            "`List` rather than `List<String>`. It still compiles for backward "
            "compatibility, with an unchecked warning."),
        _jq("Generics move a certain class of error...",
            ["from run time to compile time", "from compile time to run time",
             "from the JVM to the OS", "nowhere - they are only documentation"],
            0,
            "`ClassCastException` becomes a compile error. That is the entire "
            "justification."),
    ],
))


# --- 21.2 Writing a generic class -------------------------------------------

_M21.append(_jlesson(
    "m21-class", "Writing a generic class",
    "`class Box<T>` - a class that takes a type the way a method takes a value.",
    """
```java
class Box<T> {
    private T value;

    Box(T value) {
        this.value = value;
    }

    T get() {
        return value;
    }

    void set(T value) {
        this.value = value;
    }
}
```

`<T>` after the class name **declares a type parameter**. Inside the braces `T`
is then a real type name: a field type, a parameter type, a return type, a
local variable type. It just is not decided yet.

The decision happens at the *use* site:

```java
Box<String> a = new Box<>("ada");
Box<Integer> b = new Box<>(7);
String s = a.get();     // T is String here
int n = b.get();        // T is Integer here, and unboxes
```

`Box<String>` is called a **parameterized type**. Note the vocabulary:
`T` is the type *parameter* (in the declaration), `String` is the type
*argument* (at the use site) - the same distinction as a method's parameters
and arguments in module 9.

**The diamond `<>`** on the right-hand side means "the same type argument as the
left-hand side". `new Box<String>("ada")` is legal and identical; the diamond is
just the version you write.

**Type arguments must be reference types.** `Box<int>` does not compile - there
is no such thing. Use the wrapper, `Box<Integer>`, and autoboxing (module 17)
does the conversion:

```java
Box<Integer> b = new Box<>(7);   // 7 autoboxes to Integer.valueOf(7)
int n = b.get() + 1;             // and unboxes on the way out
```

**One class, many parameterizations.** There is exactly one `Box` class;
`Box<String>` and `Box<Integer>` are two views of it, checked separately by the
compiler. They are *not* related by inheritance - a `Box<String>` is not a
`Box<Object>`, which is module 23's subject.

**A generic class can use `T` anywhere a type is allowed** *except* in a
`static` member - lesson 21.4.
""",
    warmup=[
        _jq("What does `Box<int>` do?",
            ["Fails to compile - a type argument must be a reference type",
             "Works, and is faster than Box<Integer>",
             "Works, but boxes on every call",
             "Compiles with a warning"],
            0,
            "Primitives are not types a generic can be parameterized on. `Box<Integer>` "
            "plus autoboxing is the way."),
        _jq("In `class Box<T>` used as `Box<String>`, which is the type ARGUMENT?",
            ["String", "T", "Box", "Both T and String"],
            0,
            "`T` is the parameter in the declaration; `String` is the argument supplied "
            "at the use site."),
    ],
    exercises=[
        _je("j21-box-header", "Declare the parameter",
            "This `Box` should work for any type. Replace `____` with the class "
            "header that declares one type parameter named `T`.",
            _j21(_BOX,
                 "        String word = sc.next();\n"
                 "        Box<String> box = new Box<>(word);\n"
                 "        System.out.println(box.get());\n"
                 "        box.set(word + word);\n"
                 "        System.out.println(box.get());"),
            "class Box<T> {",
            [_case(w, _nl(w, w + w)) for w in ("ada", "bo", "generics", "x", "hi")],
            hints=["The type parameter is declared in angle brackets right after the "
                   "class name.",
                   "One parameter, conventionally named `T`.",
                   "`class Box<T> {`",
                   "Every `T` in the body then refers to it."],
            difficulty="Intro"),

        _je("j21-box-wrapper", "A box of numbers",
            "Boxes hold reference types, so a box of numbers is parameterized on the "
            "wrapper. Replace `____` with the declaration that creates a box holding "
            "the number `n`.",
            _j21(_BOX,
                 "        int n = sc.nextInt();\n"
                 "        Box<Integer> box = new Box<>(n);\n"
                 "        System.out.println(box.get() * 2);\n"
                 "        box.set(box.get() + 1);\n"
                 "        System.out.println(box.get());"),
            "Box<Integer> box = new Box<>(n);",
            [_case(str(n), _nl(n * 2, n + 1)) for n in (3, 0, -4, 10, 7)],
            hints=["`Box<int>` is not a thing.",
                   "Use the wrapper class for `int`.",
                   "`Box<Integer> box = new Box<>(n);`",
                   "`n` autoboxes on the way in and unboxes on the way out, which is "
                   "why `box.get() * 2` compiles."],
            difficulty="Intro"),

        _jfix("j21-box-primitive", "A primitive type argument",
              "This tries to parameterize the box on `int`. That is not legal Java - a "
              "type argument has to be a reference type. Fix the two places that "
              "mention the type.",
              _j21(_BOX,
                   "        int n = sc.nextInt();\n"
                   "        Box<int> box = new Box<>(n);\n"
                   "        System.out.println(box.get() + 1);\n"
                   "        Box<int> other = new Box<>(n * 2);\n"
                   "        System.out.println(other.get());"),
              _j21(_BOX,
                   "        int n = sc.nextInt();\n"
                   "        Box<Integer> box = new Box<>(n);\n"
                   "        System.out.println(box.get() + 1);\n"
                   "        Box<Integer> other = new Box<>(n * 2);\n"
                   "        System.out.println(other.get());"),
              [_case(str(n), _nl(n + 1, n * 2)) for n in (3, 0, -4, 10, 7)],
              hints=["It does not even compile - read the error, it names the offending "
                     "type.",
                     "Every primitive has a wrapper class: `int` has `Integer`.",
                     "Both declarations need the same change.",
                     "`Box<Integer>` in both places.",
                     "Nothing else changes, because autoboxing handles the conversions."],
              difficulty="Easy"),

        _jch("j21-box-two", "Two parameterizations, one class", "Easy",
             "Read a word and a number. Put the word in a `Box<String>` and the number "
             "in a `Box<Integer>`, then print the word, the number, and finally the "
             "word's length plus the number - three lines.",
             _j21(_BOX,
                  "        String word = sc.next();\n"
                  "        int n = sc.nextInt();\n"
                  "        Box<String> a = new Box<>(word);\n"
                  "        Box<Integer> b = new Box<>(n);\n"
                  "        System.out.println(a.get());\n"
                  "        System.out.println(b.get());\n"
                  "        System.out.println(a.get().length() + b.get());"),
             "        Box<String> a = new Box<>(word);\n"
             "        Box<Integer> b = new Box<>(n);\n"
             "        System.out.println(a.get());\n"
             "        System.out.println(b.get());\n"
             "        System.out.println(a.get().length() + b.get());",
             [_case(f"{w} {n}", _nl(w, n, len(w) + n))
              for (w, n) in (("ada", 3), ("bo", 0), ("generics", -2), ("x", 10),
                             ("typeparam", 5))],
             hints=["There is only one `Box` class - you are creating two different "
                    "parameterizations of it.",
                    "`Box<String> a = new Box<>(word);` and the Integer equivalent.",
                    "`a.get()` is already a `String`, so `.length()` works with no cast.",
                    "`b.get()` unboxes to an `int` in the addition."]),
    ],
    quiz=[
        _jq("`new Box<>(x)` - what is the `<>`?",
            ["The diamond: infer the type argument from the left-hand side",
             "A raw type", "A wildcard", "An empty array"],
            0,
            "It saves repeating the type argument you already wrote on the declaration."),
        _jq("How many `Box` classes exist after using `Box<String>` and `Box<Integer>`?",
            ["One", "Two", "Three", "One per method"],
            0,
            "One class, two parameterizations of it, checked separately at compile time."),
    ],
))


# --- 21.3 More than one type parameter ---------------------------------------

_M21.append(_jlesson(
    "m21-pair", "More than one type parameter",
    "`Pair<A, B>` - and what a type argument that is itself generic looks like.",
    """
A class can declare as many type parameters as it needs, comma separated:

```java
class Pair<A, B> {
    private final A first;
    private final B second;

    Pair(A first, B second) { this.first = first; this.second = second; }

    A getFirst()  { return first; }
    B getSecond() { return second; }

    @Override
    public String toString() { return first + "=" + second; }
}
```

Every parameter is filled in at the use site, in order:

```java
Pair<String, Integer> score = new Pair<>("ada", 42);
String who = score.getFirst();
int what   = score.getSecond();
```

`Map.Entry<K, V>` in the standard library is exactly this class with better
names, which is why `K` and `V` are conventional for key/value pairs.

**Order matters and the compiler enforces it.** `Pair<Integer, String> p = new
Pair<>("ada", 42)` does not compile: the arguments are the wrong way round. In
the pre-generics world that mistake ran fine until something downstream cast it.

**A type argument can itself be parameterized.** Nesting reads exactly the way
it looks:

```java
List<Pair<String, Integer>> scores = new ArrayList<>();
scores.add(new Pair<>("ada", 42));
```

`scores` is a list, of pairs, of String and Integer. Printing it prints
`[ada=42]`, because `List.toString` calls `toString` on each element (module 13's
contract, doing real work).

**Methods can return a parameterized type built from the class's own
parameters** - here a `Pair<B, A>` with the halves swapped:

```java
Pair<B, A> swapped() {
    return new Pair<>(second, first);
}
```

Read that return type carefully: on a `Pair<String, Integer>` it means
`Pair<Integer, String>`. The parameters travel with the call.

**`String` concatenation inside `toString`** works for any `A` and `B`, because
`+` on an object calls its `toString` - and every type has one (module 13).
""",
    warmup=[
        _jq("`Pair<String, Integer> p = new Pair<>(\"ada\", 42);` - what is `B` here?",
            ["Integer", "String", "Object", "int"],
            0,
            "The arguments fill the parameters in order: A is String, B is Integer."),
        _jq("What does `List<Pair<String, Integer>>` describe?",
            ["A list whose elements are pairs of String and Integer",
             "A pair of lists",
             "A list of lists",
             "A raw list"],
            0,
            "Type arguments nest; read them outside in."),
    ],
    exercises=[
        _je("j21-pair-header", "Two parameters",
            "This class carries two values of possibly different types. Replace `____` "
            "with the class header that declares both type parameters, `A` then `B`.",
            _j21(_PAIR,
                 "        String name = sc.next();\n"
                 "        int score = sc.nextInt();\n"
                 "        Pair<String, Integer> p = new Pair<>(name, score);\n"
                 "        System.out.println(p);\n"
                 "        System.out.println(p.getFirst());\n"
                 "        System.out.println(p.getSecond() + 1);"),
            "class Pair<A, B> {",
            [_case(f"{w} {n}", _nl(f"{w}={n}", w, n + 1))
             for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                            ("generics", 1))],
            hints=["Two parameters go in the same angle brackets, separated by a comma.",
                   "The fields are declared `A first` and `B second`, so those are the "
                   "names.",
                   "`class Pair<A, B> {`",
                   "Printing `p` calls the `toString` below, which prints `first=second`."],
            difficulty="Intro"),

        _je("j21-pair-nest", "A list of pairs",
            "Each word is paired with its own length, and the pairs are collected. "
            "Replace `____` with the declaration of that list.",
            _j21(_PAIR,
                 "        int n = sc.nextInt();\n"
                 "        List<Pair<String, Integer>> pairs = new ArrayList<>();\n"
                 "        for (int i = 0; i < n; i++) {\n"
                 "            String w = sc.next();\n"
                 "            pairs.add(new Pair<>(w, w.length()));\n"
                 "        }\n"
                 "        System.out.println(pairs);\n"
                 "        int total = 0;\n"
                 "        for (Pair<String, Integer> p : pairs) {\n"
                 "            total += p.getSecond();\n"
                 "        }\n"
                 "        System.out.println(total);"),
            "List<Pair<String, Integer>> pairs = new ArrayList<>();",
            [_wcase21(ws, _nl("[" + ", ".join(f"{w}={len(w)}" for w in ws) + "]",
                              sum(len(w) for w in ws)))
             for ws in _WORDS],
            hints=["The element type is itself parameterized - it goes inside the "
                   "list's own angle brackets.",
                   "The loop below already tells you the element type: "
                   "`Pair<String, Integer>`.",
                   "`List<Pair<String, Integer>> pairs = new ArrayList<>();`",
                   "The diamond on the right still infers everything."],
            difficulty="Easy"),

        _jfix("j21-pair-order", "The arguments are the wrong way round",
              "The pair is built from a name and a score, but it is declared as "
              "`Pair<Integer, String>`. Swap the type arguments so the declaration "
              "matches the values - and notice that this is a compile error rather "
              "than a crash later.",
              _j21(_PAIR,
                   "        String name = sc.next();\n"
                   "        int score = sc.nextInt();\n"
                   "        Pair<Integer, String> p = new Pair<>(name, score);\n"
                   "        System.out.println(p);\n"
                   "        System.out.println(p.getSecond());"),
              _j21(_PAIR,
                   "        String name = sc.next();\n"
                   "        int score = sc.nextInt();\n"
                   "        Pair<String, Integer> p = new Pair<>(name, score);\n"
                   "        System.out.println(p);\n"
                   "        System.out.println(p.getFirst());"),
              [_case(f"{w} {n}", _nl(f"{w}={n}", w))
               for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                              ("generics", 1))],
              hints=["The constructor is handed `(name, score)` - a String then an int.",
                     "So the declaration has to read `Pair<String, Integer>`.",
                     "The second line must print the name, which is now `getFirst()`.",
                     "`System.out.println(p.getFirst());`",
                     "A raw `Pair` would have compiled and then failed somewhere far "
                     "away. This is generics doing their job."],
              difficulty="Easy"),

        _jch("j21-pair-swap", "Swap the halves", "Medium",
             "Add a `swapped()` method to `Pair` that returns a new pair with the two "
             "values exchanged. Its return type is the pair's own parameters in the "
             "other order. The `main` below prints the pair, then the swapped pair.",
             _j21("""
class Pair<A, B> {
    private final A first;
    private final B second;

    Pair(A first, B second) {
        this.first = first;
        this.second = second;
    }

    A getFirst() {
        return first;
    }

    B getSecond() {
        return second;
    }

    Pair<B, A> swapped() {
        return new Pair<>(second, first);
    }

    @Override
    public String toString() {
        return first + "=" + second;
    }
}
""",
                  "        String name = sc.next();\n"
                  "        int score = sc.nextInt();\n"
                  "        Pair<String, Integer> p = new Pair<>(name, score);\n"
                  "        System.out.println(p);\n"
                  "        System.out.println(p.swapped());\n"
                  "        System.out.println(p.swapped().getFirst() + score);"),
             "    Pair<B, A> swapped() {\n"
             "        return new Pair<>(second, first);\n"
             "    }",
             [_case(f"{w} {n}", _nl(f"{w}={n}", f"{n}={w}", n + n))
              for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                             ("generics", 1))],
             hints=["The method takes no parameters - everything it needs is already a "
                    "field.",
                    "Its return type is a `Pair` whose parameters are in the opposite "
                    "order: `Pair<B, A>`.",
                    "`return new Pair<>(second, first);` - the diamond infers `<B, A>` "
                    "from the declared return type.",
                    "On a `Pair<String, Integer>` the result is a `Pair<Integer, "
                    "String>`, so `swapped().getFirst()` is the Integer.",
                    "That is why the last line adds two numbers rather than "
                    "concatenating strings."]),
    ],
    quiz=[
        _jq("`Pair<B, A> swapped()` on a `Pair<String, Integer>` returns...",
            ["Pair<Integer, String>", "Pair<String, Integer>", "Pair<Object, Object>",
             "a raw Pair"],
            0,
            "The parameters are substituted at the use site, in the order the return "
            "type names them."),
        _jq("Why are `K` and `V` conventional for a map-like pair?",
            ["They stand for Key and Value, following Map.Entry<K, V>",
             "The compiler requires them",
             "They are reserved words",
             "They make the class faster"],
            0,
            "Single letters are convention only - but following the standard library's "
            "convention is free readability."),
    ],
))


# --- 21.4 A generic container of your own ------------------------------------

_M21.append(_jlesson(
    "m21-bag", "A generic container of your own",
    "Wrapping a `List<T>`, and the three things a type parameter cannot do.",
    """
Most generic classes you write are not `Box` - they are containers that *hold* a
collection and add rules to it. The type parameter simply travels inward:

```java
class Bag<T> {
    private final List<T> items = new ArrayList<>();

    void add(T item)        { items.add(item); }
    T get(int i)            { return items.get(i); }
    int size()              { return items.size(); }
    boolean contains(T x)   { return items.contains(x); }

    @Override
    public String toString() { return items.toString(); }
}
```

`Bag<String>` makes the inner list a `List<String>` too. Module 14's
**composition over inheritance** in its most common form: hold a list, expose
the four methods you actually want, and keep the other thirty out of your API.

**What a type parameter cannot do.** Three limits, all of which have the same
root cause - one class object is shared by every parameterization (module 24
explains why; for now, learn the rules):

| Illegal | Why, in one line |
|---|---|
| `static T first()` | `T` belongs to an *instance*; a static member has no instance to get it from |
| `new T()` | The class does not know which constructor to call |
| `new T[10]` | The array would not know its own element type |

The first one bites soonest, and its error message is worth recognising:
*non-static type variable T cannot be referenced from a static context*. The
cure is either to make the method an instance method - or to give the **method**
its own type parameter, which is module 22.

**A static field is the same rule.** `private static T cached;` does not compile
either, and it is a good thing: `Bag<String>` and `Bag<Integer>` would have had
to share it.

**`contains` uses `equals`,** so your own types need module 13's override to be
findable inside a `Bag`. Generics check types; they do not supply behaviour.
""",
    warmup=[
        _jq("Why does `static T first()` fail to compile inside `class Bag<T>`?",
            ["T belongs to an instance, and a static member has no instance",
             "T is not imported",
             "static methods cannot return objects",
             "It needs a cast"],
            0,
            "The error even says so: 'non-static type variable T cannot be referenced "
            "from a static context'."),
        _jq("`class Bag<T>` holds a `List<T>`. In a `Bag<String>`, that list is a...",
            ["List<String>", "List<Object>", "raw List", "List<T>"],
            0,
            "The type argument travels inward to every use of `T` in the class."),
    ],
    exercises=[
        _je("j21-bag-field", "The inner list",
            "`Bag` keeps its elements in a list of the same type it was parameterized "
            "on. Replace `____` with that field declaration, already initialised to an "
            "empty `ArrayList`.",
            _j21(_BAG,
                 "        int n = sc.nextInt();\n"
                 "        Bag<String> bag = new Bag<>();\n"
                 "        for (int i = 0; i < n; i++) {\n"
                 "            bag.add(sc.next());\n"
                 "        }\n"
                 "        System.out.println(bag);\n"
                 "        System.out.println(bag.size());"),
            "private final List<T> items = new ArrayList<>();",
            [_wcase21(ws, _nl("[" + ", ".join(ws) + "]", len(ws))) for ws in _WORDS],
            hints=["The element type is the class's own type parameter.",
                   "Declare the variable as the interface, construct an `ArrayList` "
                   "(module 17's rule).",
                   "`final` because the bag never swaps its list for another one.",
                   "`private final List<T> items = new ArrayList<>();`"],
            difficulty="Easy"),

        _je("j21-bag-method", "A method that returns T",
            "Reading an element out of the bag hands back whatever type the bag was "
            "parameterized on. Replace `____` with that method's signature line.",
            _j21(_BAG,
                 "        int n = sc.nextInt();\n"
                 "        Bag<String> bag = new Bag<>();\n"
                 "        for (int i = 0; i < n; i++) {\n"
                 "            bag.add(sc.next());\n"
                 "        }\n"
                 "        System.out.println(bag.get(0));\n"
                 "        System.out.println(bag.get(bag.size() - 1));"),
            "    T get(int i) {",
            [_wcase21(ws, _nl(ws[0], ws[-1])) for ws in _WORDS],
            hints=["The index parameter is an ordinary `int`; only the RETURN type is "
                   "generic.",
                   "On a `Bag<String>` this method returns a `String` - with no cast at "
                   "the call site.",
                   "`T get(int i) {`",
                   "Four spaces of indentation, since it is a member of the class."],
            difficulty="Easy"),

        _jfix("j21-bag-static", "A static method reaching for T",
              "`first()` was written `static`, and it does not compile: *non-static "
              "type variable T cannot be referenced from a static context*. A type "
              "parameter belongs to an instance. Make it an instance method.",
              _j21("""
class Bag<T> {
    private final List<T> items = new ArrayList<>();

    void add(T item) {
        items.add(item);
    }

    static T first() {
        return items.get(0);
    }

    int size() {
        return items.size();
    }

    @Override
    public String toString() {
        return items.toString();
    }
}
""",
                   "        int n = sc.nextInt();\n"
                   "        Bag<String> bag = new Bag<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            bag.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(bag.first());\n"
                   "        System.out.println(bag.size());"),
              _j21("""
class Bag<T> {
    private final List<T> items = new ArrayList<>();

    void add(T item) {
        items.add(item);
    }

    T first() {
        return items.get(0);
    }

    int size() {
        return items.size();
    }

    @Override
    public String toString() {
        return items.toString();
    }
}
""",
                   "        int n = sc.nextInt();\n"
                   "        Bag<String> bag = new Bag<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            bag.add(sc.next());\n"
                   "        }\n"
                   "        System.out.println(bag.first());\n"
                   "        System.out.println(bag.size());"),
              [_wcase21(ws, _nl(ws[0], len(ws))) for ws in _WORDS],
              hints=["The method also touches `items`, which is an instance field - a "
                     "second symptom of the same mistake.",
                     "Deleting one keyword fixes both errors.",
                     "`T first() {`",
                     "`main` already calls it on an instance (`bag.first()`), so no "
                     "call site changes.",
                     "If it genuinely had to be static, it would need its own type "
                     "parameter - that is module 22."],
              difficulty="Medium"),

        _jch("j21-bag-use", "Drive the bag", "Easy",
             "Read `n` words into a `Bag<String>`, then a query word. Print the bag, "
             "its size, whether it contains the query word, and its first element - "
             "four lines.",
             _j21(_BAG,
                  "        int n = sc.nextInt();\n"
                  "        Bag<String> bag = new Bag<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            bag.add(sc.next());\n"
                  "        }\n"
                  "        String q = sc.next();\n"
                  "        System.out.println(bag);\n"
                  "        System.out.println(bag.size());\n"
                  "        System.out.println(bag.contains(q));\n"
                  "        System.out.println(bag.get(0));"),
             "        String q = sc.next();\n"
             "        System.out.println(bag);\n"
             "        System.out.println(bag.size());\n"
             "        System.out.println(bag.contains(q));\n"
             "        System.out.println(bag.get(0));",
             [_case("\n".join([str(len(ws)), " ".join(ws), q]),
                    _nl("[" + ", ".join(ws) + "]", len(ws), _jbool(q in ws), ws[0]))
              for (ws, q) in ((["ada", "bo"], "bo"), (["solo"], "zzz"),
                              (["x", "yy", "zzz"], "x"), (["one", "two"], "three"),
                              (["alpha", "beta"], "beta"))],
             hints=["`bag.toString()` delegates to the inner list, so printing the bag "
                    "gives the `[a, b]` form.",
                    "`contains` prints as `true` or `false`.",
                    "`get(0)` comes back as a `String` already - the bag remembers its "
                    "type argument, so no cast.",
                    "Four printed lines, in the order the prompt lists them."]),
    ],
    quiz=[
        _jq("Which of these is legal inside `class Bag<T>`?",
            ["private final List<T> items = new ArrayList<>();",
             "static T first() { ... }",
             "T made = new T();",
             "private static T cached;"],
            0,
            "A field, parameter or return type may use `T`; a static member or a `new "
            "T()` may not."),
        _jq("`Bag` holds a `List<T>` rather than extending `ArrayList<T>`. That is...",
            ["composition over inheritance - it exposes only the API it wants",
             "slower", "required by the compiler", "the same thing"],
            0,
            "Module 14's rule. Extending the list would leak thirty methods the bag "
            "never meant to promise."),
    ],
))


# --- Capstone ----------------------------------------------------------------

def _m21_cap_case(ws, q):
    body = "[" + ", ".join(f"{w}={len(w)}" for w in ws) + "]"
    found = next((f"{w}={len(w)}" for w in ws if w == q), "missing")
    return _case("\n".join([str(len(ws)), " ".join(ws), q]),
                 _nl(body, len(ws), sum(len(w) for w in ws), found))


_M21_CAP_TYPES = """
class Pair<A, B> {
    private final A first;
    private final B second;

    Pair(A first, B second) {
        this.first = first;
        this.second = second;
    }

    A getFirst() {
        return first;
    }

    B getSecond() {
        return second;
    }

    @Override
    public String toString() {
        return first + "=" + second;
    }
}

class Bag<T> {
    private final List<T> items = new ArrayList<>();

    void add(T item) {
        items.add(item);
    }

    T get(int i) {
        return items.get(i);
    }

    int size() {
        return items.size();
    }
}
"""

_M21_CAP_BODY = (
    "        int n = sc.nextInt();\n"
    "        Bag<Pair<String, Integer>> bag = new Bag<>();\n"
    "        for (int i = 0; i < n; i++) {\n"
    "            String w = sc.next();\n"
    "            bag.add(new Pair<>(w, w.length()));\n"
    "        }\n"
    "        String q = sc.next();\n"
    "        List<Pair<String, Integer>> all = new ArrayList<>();\n"
    "        for (int i = 0; i < bag.size(); i++) {\n"
    "            all.add(bag.get(i));\n"
    "        }\n"
    "        System.out.println(all);\n"
    "        System.out.println(bag.size());\n"
    "        int total = 0;\n"
    "        for (int i = 0; i < bag.size(); i++) {\n"
    "            total += bag.get(i).getSecond();\n"
    "        }\n"
    "        System.out.println(total);\n"
    "        String found = \"missing\";\n"
    "        for (int i = 0; i < bag.size(); i++) {\n"
    "            if (bag.get(i).getFirst().equals(q)) {\n"
    "                found = bag.get(i).toString();\n"
    "                break;\n"
    "            }\n"
    "        }\n"
    "        System.out.println(found);"
)

_M21_CAP = _jcap(
    "The word ledger",
    """
Write the two generic classes that make the `main` below compile and run. It is
the shape of a hundred real programs: a small container, a small pair, and a
type argument that is itself parameterized.

* **`Pair<A, B>`** - two private final fields, a two-argument constructor,
  `getFirst()`, `getSecond()`, and a `toString()` that prints `first=second`.
* **`Bag<T>`** - a private final `List<T>` inside, with `add(T)`, `get(int)`
  returning `T`, and `size()`.

`main` builds a `Bag<Pair<String, Integer>>` - a bag of pairs - and prints the
whole ledger, the number of entries, the total number of characters, and the
entry matching the query word, or `missing`.
""",
    _jch("j21-cap-ledger", "The word ledger", "Medium",
         "Write `Pair<A, B>` and `Bag<T>` exactly as the brief describes, so the "
         "given `main` compiles and produces the four lines.",
         _j21(_M21_CAP_TYPES, _M21_CAP_BODY),
         _M21_CAP_TYPES.strip("\n"),
         [_m21_cap_case(ws, q) for (ws, q) in (
             (["ada", "bo"], "bo"),
             (["solo"], "zzz"),
             (["x", "yy", "zzz"], "x"),
             (["one", "two", "three"], "three"),
             (["alpha", "beta", "gamma", "d"], "gamma"),
         )],
         hints=["Two top-level classes above `Main`, neither of them `public` - only "
                "`Main` may be public in a file called Main.java.",
                "`Pair` declares two type parameters: `class Pair<A, B> {`.",
                "Its fields are `private final A first;` and `private final B second;`, "
                "assigned in the constructor with `this.`.",
                "`toString` returns `first + \"=\" + second;` - the `+` calls each "
                "value's own toString.",
                "`Bag` declares one: `class Bag<T> {`, holding "
                "`private final List<T> items = new ArrayList<>();`.",
                "`T get(int i)` returns `items.get(i)` - generic return type, ordinary "
                "int parameter.",
                "Nothing in either class may be `static` - a static member cannot "
                "mention `T`.",
                "The printed ledger comes from the `List`'s toString calling each "
                "`Pair`'s toString: `[ada=3, bo=2]`."]),
    example_io="stdin:  2\n        ada bo\n        bo\n\n"
               "stdout: [ada=3, bo=2]\n        2\n        5\n        bo=2",
    rubric=[
        "`Pair` declares two type parameters and `Bag` declares one.",
        "Pair's fields are private and final, and assigned in the constructor.",
        "`getFirst` returns `A` and `getSecond` returns `B` - not `Object`.",
        "Pair's `toString` prints `first=second`, and is marked `@Override`.",
        "Bag holds a `List<T>`, declared as the interface and constructed as an ArrayList.",
        "`Bag.get` returns `T`, so `main` needs no casts anywhere.",
        "Neither class uses `static` with a type parameter.",
        "All four output lines appear, in order.",
    ],
)


_MODULES.append(_jmod(
    21, 7, "Generics",
    "Type parameters and generic classes",
    "Write the thing you have been using since module 17: a class that takes a type "
    "argument. Why generics exist, `class Box<T>`, several type parameters at once, "
    "and the three places a type parameter is not allowed.",
    """
Part 7 turns a consumer of generics into an author of them.

Modules 17 to 20 wrote `List<String>` constantly without ever asking what the
angle brackets were. They are a **type argument** - a type handed to a class the
way an argument is handed to a method - and the class that receives it declares
a **type parameter**, `class Box<T>`.

The reason to care is narrow and worth being precise about: generics turn a
class of run-time `ClassCastException`s into compile errors, and delete the
casts that used to be needed on the way out of every container. Everything else
- the diamond, the letters `T`, `E`, `K`, `V`, the nesting - is spelling.

The limits are worth learning as rules now and understanding later: a type
parameter belongs to an *instance*, so no `static` member may mention it; and
`new T()` and `new T[10]` do not compile, because the class does not know what
`T` really is at run time. Module 22 gives *methods* their own type parameters,
which is the missing half of the static story.
""",
    _M21,
    capstone=_M21_CAP,
    objectives=[
        "Explain what a raw type is and why it is a bad idea in new code.",
        "Say precisely what generics buy: compile errors instead of ClassCastException.",
        "Declare a generic class with `class Box<T>` and use `T` as a field, parameter and return type.",
        "Distinguish a type parameter from a type argument.",
        "Use wrapper classes as type arguments, and explain why `Box<int>` is illegal.",
        "Declare and use a class with two type parameters, and read nested type arguments.",
        "Return a parameterized type built from the class's own parameters.",
        "Name the three things a type parameter cannot do, and recognise the static-context error.",
    ],
    why="Every collection you touch is generic, so reading `Map<String, List<Integer>>` "
        "fluently is a daily skill - and interviews reliably ask what generics actually "
        "buy you. Writing your own container is also the cleanest way to see that a type "
        "parameter is just a hole in a class, filled at the use site.",
    est_minutes=300,
    glossary=[
        _jg("generics", "Types parameterized by other types, checked at compile time."),
        _jg("type parameter", "The placeholder in a declaration: the `T` in `class Box<T>`."),
        _jg("type argument", "The real type supplied at the use site: the `String` in "
                             "`Box<String>`."),
        _jg("parameterized type", "A generic type with its arguments filled in, e.g. "
                                  "`Box<String>`."),
        _jg("raw type", "A generic type used with no type argument, e.g. `List`. Type "
                        "checking is off; unchecked warnings follow."),
        _jg("diamond", "The `<>` on the right-hand side, letting the compiler infer the "
                       "type argument."),
        _jg("ClassCastException", "The run-time failure generics exist to prevent."),
        _jg("T, E, K, V", "Conventional parameter names: Type, Element, Key, Value."),
        _jg("static context", "A member belonging to the class rather than an instance - "
                              "and therefore unable to mention a type parameter."),
    ],
    cheatsheet="""
```java
// --- declaring ------------------------------------------------------------
class Box<T> {                       // one type parameter
    private T value;                 // field
    Box(T value) { this.value = value; }
    T get() { return value; }        // generic return type
    void set(T value) { this.value = value; }
}

class Pair<A, B> { ... }             // two, comma separated
Pair<B, A> swapped() { ... }         // a return type built from them

// --- using ----------------------------------------------------------------
Box<String> a = new Box<>("ada");    // <> is the diamond: inferred
Box<Integer> b = new Box<>(7);       // wrapper, never Box<int>
String s = a.get();                  // no cast, ever
List<Pair<String, Integer>> rows = new ArrayList<>();   // arguments nest

// --- illegal --------------------------------------------------------------
Box<int> b;                          // primitives cannot be type arguments
static T first() { ... }             // T belongs to an instance
private static T cached;             // same rule
T made = new T();                    // the class cannot know the constructor
T[] arr = new T[10];                 // the array cannot know its element type

// --- raw types (legacy only) ----------------------------------------------
List names = new ArrayList();        // RAW: checking off, unchecked warning
names.add(42);                       // compiles; crashes later at the cast
```
""",
    self_check=[
        "Can you say, in one sentence, what generics buy you?",
        "Can you explain what a raw type switches off, and why it still compiles?",
        "Can you write `class Box<T>` from memory, with a field, a getter and a setter?",
        "Can you say which of `T` and `String` is the parameter and which the argument?",
        "Can you explain why `Box<int>` does not compile, and what to write instead?",
        "Can you read `List<Pair<String, Integer>>` out loud and say what it holds?",
        "Can you give the three things a type parameter cannot do?",
        "Can you recognise 'non-static type variable T cannot be referenced from a static context' and fix it?",
    ],
    review=[
        _jq("```java\nObjectBox b = new ObjectBox(\"ada\");\nInteger n = (Integer) b.get();\n```\nWhat happens?",
            ["It compiles and throws ClassCastException at run time",
             "It fails to compile", "It prints 0", "It returns null"],
            0,
            "`get()` is declared to return `Object`, so the compiler cannot object. The "
            "JVM finds out instead."),
        _jq("Which line does NOT compile?",
            ["static T first() { return null; }",
             "T get() { return value; }",
             "void set(T v) { this.value = v; }",
             "private T value;"],
            0,
            "A static member has no instance, and `T` belongs to one."),
        _jq("`Pair<String, Integer> p = new Pair<>(name, score);` - what is the `<>` doing?",
            ["Inferring `<String, Integer>` from the left-hand side",
             "Declaring two new type parameters", "Making the pair raw",
             "Creating a wildcard"],
            0,
            "The diamond copies the type arguments you already wrote."),
        _jq("In the capstone, why does `main` need no casts?",
            ["`Bag.get` is declared to return `T`, which is `Pair<String, Integer>` here",
             "Because of autoboxing", "Because the classes are not public",
             "Because `main` is static"],
            0,
            "The bag remembers its type argument, which is the entire improvement over "
            "an Object-based container."),
    ],
    milestone="You can write a generic class rather than only use one, and say exactly "
              "which mistakes the type parameter is preventing.",
))
