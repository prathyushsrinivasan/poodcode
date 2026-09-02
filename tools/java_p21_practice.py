# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 21 practice - type parameters and generic classes.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[21]`.
#
# Generic METHODS and bounds are module 22, wildcards module 23 - so nothing
# here declares `<T>` on a method, and no signature mentions `? extends`. Every
# exercise is a class that takes a type argument, or a main that uses one.
#
# A List's toString is specified as "[a, b, c]", and each class below defines a
# toString of its own, so printing any of them is safe to assert on.
# ---------------------------------------------------------------------------


_P21_BOX = """
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

_P21_PAIR = """
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

_P21_BAG = """
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


def _p21ex(eid, title, difficulty, prompt, body, tests, hints, types=_P21_BOX):
    """A practice challenge: the helper class is given, you write main's body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types.strip("\n"), body),
                body, tests, hints)


def _p21cls(eid, title, difficulty, prompt, types, body, tests, hints):
    """The other way round: main is given, you write the generic class."""
    return _jch(eid, title, difficulty, prompt, _joop(types.strip("\n"), body),
                types.strip("\n"), tests, hints)


def _w21(ws, out):
    return _case("\n".join([str(len(ws)), " ".join(ws)]), out)


def _wq21(ws, q, out):
    return _case("\n".join([str(len(ws)), " ".join(ws), q]), out)


def _n21(xs, out):
    return _case("\n".join([str(len(xs)), " ".join(str(x) for x in xs)]), out)


def _jl21(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"


_WS21 = (["ada", "bo", "cy"], ["solo"], ["x", "yy", "zzz"], ["pear", "fig"],
         ["alpha", "beta", "gamma", "d"])

_RD_W21 = ("        int n = sc.nextInt();\n"
           "        List<String> words = new ArrayList<>();\n"
           "        for (int i = 0; i < n; i++) {\n"
           "            words.add(sc.next());\n"
           "        }\n")


# --- Family A - one value, one type parameter --------------------------------

_P21_A = _jfam(
    "p21-box", "Boxing one value",
    "A class with a single type parameter, used at several type arguments.",
    """
```java
class Box<T> {
    private T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
    void set(T value) { this.value = value; }
}
```

`<T>` after the class name **declares** a type parameter; `Box<String>`
**supplies** one. Inside the class `T` is a perfectly ordinary type name - it is
just not decided until the use site.

```java
Box<String> a = new Box<>("ada");   // <> is the diamond: inferred from the left
Box<Integer> b = new Box<>(7);      // wrapper, never Box<int>
String s = a.get();                 // no cast - the box remembers
```

Two things to keep straight in every exercise below:

* **Type arguments are reference types.** `Box<int>` does not compile; `int`
  autoboxes into a `Box<Integer>` on the way in and unboxes on the way out.
* **One class, many parameterizations.** `Box<String>` and `Box<Integer>` are
  the same class seen twice, checked separately - and unrelated to each other by
  inheritance.
""",
    [
        _p21ex("j21-pa-word", "Box a word", "Intro",
               "Read one word into a `Box<String>`. Print the value, then its length.",
               """
        String w = sc.next();
        Box<String> box = new Box<>(w);
        System.out.println(box.get());
        System.out.println(box.get().length());
""",
               [_case(w, _nl(w, len(w)))
                for w in ("ada", "bo", "generics", "x", "typeparam")],
               ["`Box<String> box = new Box<>(w);` - the diamond infers the argument.",
                "`get()` comes back as a `String` already, so no cast is needed.",
                "`.length()` is legal precisely because the box remembered its type.",
                "Two printed lines."]),

        _p21ex("j21-pa-num", "Box a number", "Intro",
               "Read one integer into a box. Print the value plus one, then the value "
               "squared.",
               """
        int n = sc.nextInt();
        Box<Integer> box = new Box<>(n);
        System.out.println(box.get() + 1);
        System.out.println(box.get() * box.get());
""",
               [_case(str(n), _nl(n + 1, n * n)) for n in (3, 0, -4, 10, 7)],
               ["`Box<int>` is not legal - use the wrapper.",
                "`Box<Integer> box = new Box<>(n);`",
                "`n` autoboxes on the way in; `box.get()` unboxes in the arithmetic.",
                "Squaring a negative gives a positive, which case three checks."]),

        _p21ex("j21-pa-set", "Replace the contents", "Intro",
               "Read two words. Box the first, print it, then `set` the second and "
               "print that.",
               """
        String a = sc.next();
        String b = sc.next();
        Box<String> box = new Box<>(a);
        System.out.println(box.get());
        box.set(b);
        System.out.println(box.get());
""",
               [_case(f"{a} {b}", _nl(a, b))
                for (a, b) in (("ada", "bo"), ("x", "y"), ("one", "two"),
                               ("same", "same"), ("first", "second"))],
               ["One box, two values over its lifetime.",
                "`set` takes a `T`, which here means a `String`.",
                "Print between the two, not after both.",
                "Case four sets the same word again, and must still print it twice."]),

        _p21ex("j21-pa-swap", "Swap two boxes", "Easy",
               "Read two words into two boxes, then exchange their contents. Print the "
               "first box, then the second.",
               """
        String a = sc.next();
        String b = sc.next();
        Box<String> one = new Box<>(a);
        Box<String> two = new Box<>(b);
        String temp = one.get();
        one.set(two.get());
        two.set(temp);
        System.out.println(one.get());
        System.out.println(two.get());
""",
               [_case(f"{a} {b}", _nl(b, a))
                for (a, b) in (("ada", "bo"), ("x", "y"), ("one", "two"),
                               ("same", "same"), ("first", "second"))],
               ["Save one value before overwriting it, exactly as with two variables.",
                "The temporary's type is `String` here, because both boxes are "
                "`Box<String>`.",
                "`one.set(two.get());` then `two.set(temp);`",
                "The boxes are swapped, not the variables - both still refer to the "
                "same objects."]),

        _p21ex("j21-pa-list", "A list of boxes", "Medium",
               "Read `n` words and put each into its own `Box<String>`, collected in a "
               "list. Print how many boxes there are, then the total number of "
               "characters they hold.",
               """
        int n = sc.nextInt();
        List<Box<String>> boxes = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            boxes.add(new Box<>(sc.next()));
        }
        int total = 0;
        for (Box<String> box : boxes) {
            total += box.get().length();
        }
        System.out.println(boxes.size());
        System.out.println(total);
""",
               [_w21(ws, _nl(len(ws), sum(len(w) for w in ws))) for ws in _WS21],
               ["The element type is itself parameterized: `List<Box<String>>`.",
                "`boxes.add(new Box<>(sc.next()));` - the diamond infers `String`.",
                "An enhanced `for` gives you a `Box<String>` each time, so "
                "`box.get()` is a `String`.",
                "Size first, then the total - two lines."]),
    ])


# --- Family B - two type parameters ------------------------------------------

_P21_B = _jfam(
    "p21-pair", "Two values, two type parameters",
    "`Pair<A, B>` - and reading type arguments that nest.",
    """
```java
class Pair<A, B> {
    private final A first;
    private final B second;
    Pair(A first, B second) { this.first = first; this.second = second; }
    A getFirst()  { return first; }
    B getSecond() { return second; }
    @Override public String toString() { return first + "=" + second; }
}
```

The arguments fill the parameters **in order**: in `Pair<String, Integer>`, `A`
is `String` and `B` is `Integer`. Getting them the wrong way round is a compile
error, which is exactly the improvement over the pre-generics world where it was
a crash much later.

A type argument may itself be parameterized, and it reads outside-in:

```java
List<Pair<String, Integer>> rows = new ArrayList<>();   // a list, of pairs
```

Printing that list prints `[ada=3, bo=2]`, because `List.toString` calls each
element's `toString` - the one the class above defines.
""",
    [
        _p21ex("j21-pb-build", "Name and score", "Intro",
               "Read a word and a number into a `Pair<String, Integer>`. Print the "
               "pair, then the number plus one.",
               """
        String name = sc.next();
        int score = sc.nextInt();
        Pair<String, Integer> p = new Pair<>(name, score);
        System.out.println(p);
        System.out.println(p.getSecond() + 1);
""",
               [_case(f"{w} {n}", _nl(f"{w}={n}", n + 1))
                for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                               ("gamma", 1))],
               ["The arguments go in the order the constructor takes them.",
                "`Pair<String, Integer> p = new Pair<>(name, score);`",
                "Printing `p` uses the class's own `toString`.",
                "`getSecond()` unboxes into the addition."],
               types=_P21_PAIR),

        _p21ex("j21-pb-halves", "Both halves, separately", "Intro",
               "Read a word and a number into a pair, then print the word in upper "
               "case and the number doubled.",
               """
        String name = sc.next();
        int score = sc.nextInt();
        Pair<String, Integer> p = new Pair<>(name, score);
        System.out.println(p.getFirst().toUpperCase());
        System.out.println(p.getSecond() * 2);
""",
               [_case(f"{w} {n}", _nl(w.upper(), n * 2))
                for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                               ("gamma", 1))],
               ["`getFirst()` is a `String`, so String methods work with no cast.",
                "`getSecond()` is an `Integer`, and unboxes in arithmetic.",
                "That no-cast property is the entire point of the type parameters.",
                "Two lines out."],
               types=_P21_PAIR),

        _p21ex("j21-pb-rows", "Word and length", "Easy",
               "Read `n` words and build a `List<Pair<String, Integer>>` pairing each "
               "word with its length. Print the list.",
               """
        int n = sc.nextInt();
        List<Pair<String, Integer>> rows = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String w = sc.next();
            rows.add(new Pair<>(w, w.length()));
        }
        System.out.println(rows);
""",
               [_w21(ws, "[" + ", ".join(f"{w}={len(w)}" for w in ws) + "]")
                for ws in _WS21],
               ["The declaration nests: `List<Pair<String, Integer>>`.",
                "`rows.add(new Pair<>(w, w.length()));` - the length autoboxes.",
                "Printing the list calls each pair's `toString`.",
                "One line of output, in the `[ada=3, bo=2]` form."],
               types=_P21_PAIR),

        _p21ex("j21-pb-upper", "A pair of two strings", "Easy",
               "Read one word into a `Pair<String, String>` holding the word and its "
               "upper-case form. Print the pair, then the first half only.",
               """
        String w = sc.next();
        Pair<String, String> p = new Pair<>(w, w.toUpperCase());
        System.out.println(p);
        System.out.println(p.getFirst());
""",
               [_case(w, _nl(f"{w}={w.upper()}", w))
                for w in ("ada", "bo", "generics", "x", "typeparam")],
               ["Both type arguments can be the same type - `Pair<String, String>`.",
                "The second value is computed, not read: `w.toUpperCase()`.",
                "`toString` joins them with `=`.",
                "Two lines out."],
               types=_P21_PAIR),

        _p21ex("j21-pb-count", "Count the long ones", "Medium",
               "Read `n` words, pair each with its length, then read a number `k` and "
               "print how many pairs have a second value greater than `k`. Print the "
               "list first.",
               """
        int n = sc.nextInt();
        List<Pair<String, Integer>> rows = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String w = sc.next();
            rows.add(new Pair<>(w, w.length()));
        }
        int k = sc.nextInt();
        System.out.println(rows);
        int count = 0;
        for (Pair<String, Integer> p : rows) {
            if (p.getSecond() > k) {
                count++;
            }
        }
        System.out.println(count);
""",
               [_case("\n".join([str(len(ws)), " ".join(ws), str(k)]),
                      _nl("[" + ", ".join(f"{w}={len(w)}" for w in ws) + "]",
                          sum(1 for w in ws if len(w) > k)))
                for (ws, k) in ((["ada", "bo", "cy"], 2), (["solo"], 9),
                                (["x", "yy", "zzz"], 1), (["pear", "fig"], 0),
                                (["alpha", "beta", "gamma", "d"], 4))],
               ["Read `k` after the words, before printing anything.",
                "The enhanced `for` gives you a `Pair<String, Integer>` each time.",
                "`p.getSecond() > k` unboxes the Integer for the comparison.",
                "Strictly greater, so a length equal to `k` does not count.",
                "Two lines: the list, then the count."],
               types=_P21_PAIR),
    ])


# --- Family C - writing the class --------------------------------------------

_P21_C = _jfam(
    "p21-write", "Writing the class",
    "main is given; you supply the generic type it needs.",
    """
The other direction, and the one that actually proves you can write generics:
`main` is fixed, and you write the class that makes it compile.

A checklist for every one of these:

1. **Declare the parameters** on the class header - `class Name<T>` or
   `class Name<A, B>`.
2. **Use them as ordinary types** inside: field types, constructor parameters,
   method parameters, return types.
3. **Nothing may be `static`** if it mentions a type parameter. `static T
   first()` does not compile; nor does `private static T cached;`.
4. **`new T()` and `new T[10]` are illegal** - the class does not know what `T`
   really is. Hold a `List<T>` instead, or take the value as a constructor
   argument.
5. If `main` prints the object directly, it needs a **`toString`** - and the
   expected output tells you its exact shape.

Only `Main` may be `public` in a file called `Main.java`, so every class you
write here is package-private: just `class Name<T> { ... }`.
""",
    [
        _p21cls("j21-pc-box", "Write Box", "Easy",
                "Write `Box<T>`: one private field of type `T`, a constructor taking "
                "one, `T get()`, and `void set(T)`.",
                _P21_BOX,
                """
        String w = sc.next();
        Box<String> box = new Box<>(w);
        System.out.println(box.get());
        box.set(w + w);
        System.out.println(box.get());
""",
                [_case(w, _nl(w, w + w))
                 for w in ("ada", "bo", "generics", "x", "hi")],
                ["`class Box<T> {` declares the parameter.",
                 "The field is `private T value;` and the constructor assigns it with "
                 "`this.value = value;`.",
                 "`T get()` returns it; `void set(T value)` replaces it.",
                 "Nothing is static, and nothing mentions `String`."]),

        _p21cls("j21-pc-pair", "Write Pair", "Easy",
                "Write `Pair<A, B>`: two private final fields, a two-argument "
                "constructor, `getFirst()`, `getSecond()`, and a `toString()` printing "
                "`first=second`.",
                _P21_PAIR,
                """
        String name = sc.next();
        int score = sc.nextInt();
        Pair<String, Integer> p = new Pair<>(name, score);
        System.out.println(p);
        System.out.println(p.getFirst());
        System.out.println(p.getSecond() + 1);
""",
                [_case(f"{w} {n}", _nl(f"{w}={n}", w, n + 1))
                 for (w, n) in (("ada", 42), ("bo", 0), ("x", -3), ("zed", 7),
                                ("gamma", 1))],
                ["Two parameters in one pair of brackets: `class Pair<A, B> {`.",
                 "`getFirst` returns `A`, `getSecond` returns `B` - not `Object`.",
                 "`toString` returns `first + \"=\" + second;`, and is marked "
                 "`@Override`.",
                 "The fields can be `final`, since nothing ever replaces them."]),

        _p21cls("j21-pc-counter", "Write Counter", "Medium",
                "Write `Counter<T>`: it holds one value of type `T` and an `int` "
                "count starting at zero. `bump()` adds one to the count, `getCount()` "
                "returns it, and `toString()` prints `value:count`.",
                """
class Counter<T> {
    private final T value;
    private int count;

    Counter(T value) {
        this.value = value;
    }

    void bump() {
        count++;
    }

    int getCount() {
        return count;
    }

    @Override
    public String toString() {
        return value + ":" + count;
    }
}
""",
                """
        String w = sc.next();
        int times = sc.nextInt();
        Counter<String> c = new Counter<>(w);
        for (int i = 0; i < times; i++) {
            c.bump();
        }
        System.out.println(c);
        System.out.println(c.getCount());
""",
                [_case(f"{w} {t}", _nl(f"{w}:{t}", t))
                 for (w, t) in (("ada", 3), ("bo", 0), ("x", 1), ("zed", 5),
                                ("gamma", 2))],
                ["Only the held value is generic; the count is an ordinary `int`.",
                 "`private final T value;` and `private int count;` - an int field "
                 "starts at 0 without help.",
                 "The constructor takes only the value.",
                 "`toString` returns `value + \":\" + count;`.",
                 "Case two bumps zero times, so the count must genuinely start at 0."]),

        _p21cls("j21-pc-bag", "Write Bag", "Medium",
                "Write `Bag<T>`: it holds a private final `List<T>` and offers "
                "`add(T)`, `T get(int)`, `int size()` and a `toString()` that "
                "delegates to the list.",
                """
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

    @Override
    public String toString() {
        return items.toString();
    }
}
""",
                _RD_W21
                + "        Bag<String> bag = new Bag<>();\n"
                  "        for (String w : words) {\n"
                  "            bag.add(w);\n"
                  "        }\n"
                  "        System.out.println(bag);\n"
                  "        System.out.println(bag.size());\n"
                  "        System.out.println(bag.get(0));",
                [_w21(ws, _nl(_jl21(ws), len(ws), ws[0])) for ws in _WS21],
                ["The inner list's element type is the class's own parameter: "
                 "`List<T>`.",
                 "Declare it as the interface, construct an `ArrayList`, and make it "
                 "`final`.",
                 "`T get(int i)` - generic return type, ordinary int parameter.",
                 "`toString` returns `items.toString()`, which gives the `[a, b]` "
                 "form."]),

        _p21cls("j21-pc-pile", "Write Pile", "Hard",
                "Write `Pile<T>`, a last-in-first-out pile built on a `List<T>`: "
                "`push(T)` adds to the end, `T pop()` removes and returns the last "
                "element, `int size()`, and `boolean isEmpty()`.",
                """
class Pile<T> {
    private final List<T> items = new ArrayList<>();

    void push(T item) {
        items.add(item);
    }

    T pop() {
        return items.remove(items.size() - 1);
    }

    int size() {
        return items.size();
    }

    boolean isEmpty() {
        return items.isEmpty();
    }
}
""",
                _RD_W21
                + "        Pile<String> pile = new Pile<>();\n"
                  "        for (String w : words) {\n"
                  "            pile.push(w);\n"
                  "        }\n"
                  "        System.out.println(pile.size());\n"
                  "        System.out.println(pile.pop());\n"
                  "        System.out.println(pile.size());\n"
                  "        while (!pile.isEmpty()) {\n"
                  "            pile.pop();\n"
                  "        }\n"
                  "        System.out.println(pile.isEmpty());",
                [_w21(ws, _nl(len(ws), ws[-1], len(ws) - 1, "true")) for ws in _WS21],
                ["Hold the elements in a `private final List<T>`.",
                 "`push` appends with `items.add(item)`.",
                 "`pop` removes the LAST element: "
                 "`items.remove(items.size() - 1)`, which returns what it removed.",
                 "That `remove(int)` overload takes an index - module 17's trap, and "
                 "here it is the one you want.",
                 "`isEmpty()` can delegate straight to the list."]),
    ])


# --- Family D - containers that hold a type ---------------------------------

_P21_D = _jfam(
    "p21-bag", "Driving a generic container",
    "The `Bag<T>` is written; use it.",
    """
```java
class Bag<T> {
    private final List<T> items = new ArrayList<>();
    void add(T item)      { items.add(item); }
    T get(int i)          { return items.get(i); }
    int size()            { return items.size(); }
    boolean contains(T x) { return items.contains(x); }
    @Override public String toString() { return items.toString(); }
}
```

A container that *holds* a `List<T>` and exposes only the four methods it means
to promise - module 14's composition over inheritance, with a type parameter
attached.

Two things carry over from the collections modules:

* `contains` uses **`equals`**, so it works on Strings and wrappers out of the
  box.
* `Bag<Integer>` holds boxed `Integer`s, which unbox automatically in
  arithmetic - but compare with `.equals`, never `==`.

And one thing is new: `bag.get(0)` comes back **already typed**. No cast, ever.
""",
    [
        _p21ex("j21-pd-fill", "Fill and report", "Intro",
               "Read `n` words into a `Bag<String>`. Print the bag, then its size.",
               _RD_W21
               + "        Bag<String> bag = new Bag<>();\n"
                 "        for (String w : words) {\n"
                 "            bag.add(w);\n"
                 "        }\n"
                 "        System.out.println(bag);\n"
                 "        System.out.println(bag.size());",
               [_w21(ws, _nl(_jl21(ws), len(ws))) for ws in _WS21],
               ["`new Bag<>()` takes no constructor argument - the list starts empty.",
                "The diamond infers `String` from the declared type on the left.",
                "Printing the bag delegates to the list's toString.",
                "Two lines out."],
               types=_P21_BAG),

        _p21ex("j21-pd-contains", "Is it in there", "Intro",
               "Read `n` words into a bag, then a query word. Print whether the bag "
               "contains it, then the bag's first element.",
               _RD_W21
               + "        String q = sc.next();\n"
                 "        Bag<String> bag = new Bag<>();\n"
                 "        for (String w : words) {\n"
                 "            bag.add(w);\n"
                 "        }\n"
                 "        System.out.println(bag.contains(q));\n"
                 "        System.out.println(bag.get(0));",
               [_wq21(ws, q, _nl(_jbool(q in ws), ws[0]))
                for (ws, q) in ((["ada", "bo", "cy"], "bo"), (["solo"], "zzz"),
                                (["x", "yy", "zzz"], "x"), (["pear", "fig"], "fig"),
                                (["alpha", "beta"], "gamma"))],
               ["Read the query word after the list of words.",
                "`contains` uses `equals`, which is why it works on Strings.",
                "It prints as `true` or `false`.",
                "`get(0)` is a `String` already - no cast."],
               types=_P21_BAG),

        _p21ex("j21-pd-ends", "First and last", "Easy",
               "Read `n` words into a bag and print its first and last elements.",
               _RD_W21
               + "        Bag<String> bag = new Bag<>();\n"
                 "        for (String w : words) {\n"
                 "            bag.add(w);\n"
                 "        }\n"
                 "        System.out.println(bag.get(0));\n"
                 "        System.out.println(bag.get(bag.size() - 1));",
               [_w21(ws, _nl(ws[0], ws[-1])) for ws in _WS21],
               ["The bag has no `last()` - compute the index.",
                "`bag.get(bag.size() - 1)`",
                "A one-element bag prints the same word twice, which case two checks.",
                "Both values come back typed, so no cast is needed."],
               types=_P21_BAG),

        _p21ex("j21-pd-count", "Count the matches", "Easy",
               "Read `n` words into a bag, then a query word, and print how many times "
               "it occurs. The bag offers only `get`, `size` and `contains`, so count "
               "with an index loop.",
               _RD_W21
               + "        String q = sc.next();\n"
                 "        Bag<String> bag = new Bag<>();\n"
                 "        for (String w : words) {\n"
                 "            bag.add(w);\n"
                 "        }\n"
                 "        int count = 0;\n"
                 "        for (int i = 0; i < bag.size(); i++) {\n"
                 "            if (bag.get(i).equals(q)) {\n"
                 "                count++;\n"
                 "            }\n"
                 "        }\n"
                 "        System.out.println(count);",
               [_wq21(ws, q, sum(1 for w in ws if w == q))
                for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                                (["x", "x", "x"], "x"), (["pear", "fig"], "fig"),
                                (["a", "b", "c"], "d"))],
               ["An index loop, because the bag exposes no iterator.",
                "`bag.get(i)` is a `String`, so `.equals(q)` compiles directly.",
                "Never `==` on Strings - module 6's rule, unchanged.",
                "One line: the count, which may be zero."],
               types=_P21_BAG),

        _p21ex("j21-pd-nums", "A bag of numbers", "Medium",
               "Read `n` integers into a `Bag<Integer>`. Print the bag, then the sum "
               "of its elements.",
               """
        int n = sc.nextInt();
        Bag<Integer> bag = new Bag<>();
        for (int i = 0; i < n; i++) {
            bag.add(sc.nextInt());
        }
        System.out.println(bag);
        int total = 0;
        for (int i = 0; i < bag.size(); i++) {
            total += bag.get(i);
        }
        System.out.println(total);
""",
               [_n21(xs, _nl(_jl21(xs), sum(xs)))
                for xs in ([3, 1, 2], [5], [-4, -9, -1], [10, 10, 2], [7, 2, 9, 4])],
               ["`Bag<Integer>`, never `Bag<int>`.",
                "`bag.add(sc.nextInt())` autoboxes on the way in.",
                "`total += bag.get(i)` unboxes on the way out.",
                "Two lines: the bag, then the sum."],
               types=_P21_BAG),
    ])


# --- Family E - nesting and no casts ----------------------------------------

_P21_E = _jfam(
    "p21-nest", "Nesting, and the casts you no longer write",
    "Type arguments that are themselves parameterized.",
    """
A type argument can be any reference type - including another parameterized
type. Read them outside-in:

```java
List<Pair<String, Integer>>       // a list, of pairs, of String and Integer
Bag<Pair<String, Integer>>        // a bag of the same pairs
Pair<Pair<String, Integer>, Integer>   // a pair whose first half is a pair
```

Nothing new is happening - `Pair<String, Integer>` is a type like any other, so
it can be handed to `List` or `Bag` as an argument.

The payoff is the same in every one of these: **no casts anywhere.**
`rows.get(0).getFirst()` is a `String`, and the compiler knows it. The
pre-generics version of the same line was
`((Pair) rows.get(0)).getFirst()` returning `Object`, needing another cast, and
failing at run time if either guess was wrong.
""",
    [
        _p21ex("j21-pe-raw", "Parameterize it", "Easy",
               "Read `n` words into a `List<String>` - not a raw `List` - and print "
               "each one in upper case, one per line. No `Object` and no casts.",
               """
        int n = sc.nextInt();
        List<String> words = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            words.add(sc.next());
        }
        for (String w : words) {
            System.out.println(w.toUpperCase());
        }
""",
               [_w21(ws, _nl(*[w.upper() for w in ws])) for ws in _WS21],
               ["A raw `List` would compile and then need a cast in the loop.",
                "`List<String> words = new ArrayList<>();`",
                "The loop variable can then be a `String` directly.",
                "One line of output per word."],
               types=_P21_PAIR),

        _p21ex("j21-pe-longest", "The longest word, as a pair", "Medium",
               "Read `n` words, pair each with its length, and print the pair with the "
               "largest length. If two are equally long, print the earlier one.",
               """
        int n = sc.nextInt();
        List<Pair<String, Integer>> rows = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String w = sc.next();
            rows.add(new Pair<>(w, w.length()));
        }
        Pair<String, Integer> best = rows.get(0);
        for (Pair<String, Integer> p : rows) {
            if (p.getSecond() > best.getSecond()) {
                best = p;
            }
        }
        System.out.println(best);
        System.out.println(best.getFirst());
""",
               [_w21(ws, _nl(f"{max(ws, key=len)}={len(max(ws, key=len))}",
                             max(ws, key=len)))
                for ws in _WS21],
               ["Seed `best` with element 0 and walk the whole list.",
                "Strictly greater keeps the earlier pair on a tie.",
                "`best.getSecond()` unboxes for the comparison.",
                "`best.getFirst()` is a `String` - no cast, which is the point.",
                "Two lines: the pair, then just its word."],
               types=_P21_PAIR),

        _p21ex("j21-pe-ledger", "A bag of pairs", "Medium",
               "Read `n` words into a `Bag<Pair<String, Integer>>` pairing each with "
               "its length. Print the bag, then the total of all the lengths.",
               """
        int n = sc.nextInt();
        Bag<Pair<String, Integer>> bag = new Bag<>();
        for (int i = 0; i < n; i++) {
            String w = sc.next();
            bag.add(new Pair<>(w, w.length()));
        }
        System.out.println(bag);
        int total = 0;
        for (int i = 0; i < bag.size(); i++) {
            total += bag.get(i).getSecond();
        }
        System.out.println(total);
""",
               [_w21(ws, _nl("[" + ", ".join(f"{w}={len(w)}" for w in ws) + "]",
                             sum(len(w) for w in ws)))
                for ws in _WS21],
               ["The bag's type argument is itself parameterized: "
                "`Bag<Pair<String, Integer>>`.",
                "`bag.add(new Pair<>(w, w.length()));`",
                "`bag.get(i)` is a `Pair<String, Integer>`, so `.getSecond()` compiles "
                "with no cast.",
                "Printing the bag prints the list, which prints each pair."],
               types=_P21_PAIR + "\n" + _P21_BAG),

        _p21ex("j21-pe-nested", "A pair inside a pair", "Medium",
               "Read one word. Build a `Pair<String, Integer>` of the word and its "
               "length, then wrap that in a `Pair<Pair<String, Integer>, Integer>` "
               "whose second value is the length doubled. Print the outer pair, then "
               "the inner word.",
               """
        String w = sc.next();
        Pair<String, Integer> inner = new Pair<>(w, w.length());
        Pair<Pair<String, Integer>, Integer> outer = new Pair<>(inner, w.length() * 2);
        System.out.println(outer);
        System.out.println(outer.getFirst().getFirst());
""",
               [_case(w, _nl(f"{w}={len(w)}={len(w) * 2}", w))
                for w in ("ada", "bo", "generics", "x", "typeparam")],
               ["Build the inner pair first, then hand it to the outer one.",
                "The outer type is `Pair<Pair<String, Integer>, Integer>`.",
                "`toString` prints `first=second`, and the first is itself a pair - so "
                "you get `ada=3=6`.",
                "`outer.getFirst()` is a `Pair<String, Integer>`; `.getFirst()` again "
                "is the word."],
               types=_P21_PAIR),

        _p21ex("j21-pe-nocast", "No casts anywhere", "Medium",
               "Read `n` words into a `List<Box<String>>`, then a query word. Print "
               "how many boxes hold it, and the contents of the last box.",
               """
        int n = sc.nextInt();
        List<Box<String>> boxes = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            boxes.add(new Box<>(sc.next()));
        }
        String q = sc.next();
        int count = 0;
        for (Box<String> box : boxes) {
            if (box.get().equals(q)) {
                count++;
            }
        }
        System.out.println(count);
        System.out.println(boxes.get(boxes.size() - 1).get());
""",
               [_wq21(ws, q, _nl(sum(1 for w in ws if w == q), ws[-1]))
                for (ws, q) in ((["ada", "bo", "ada"], "ada"), (["solo"], "zzz"),
                                (["x", "x", "y"], "x"), (["pear", "fig"], "fig"),
                                (["a", "b", "c"], "d"))],
               ["`List<Box<String>>` - a list whose elements are boxes.",
                "Read the query word after the `n` words.",
                "`box.get()` is a `String`, so `.equals(q)` needs no cast.",
                "The last element is at `boxes.size() - 1`, and `.get()` on it is the "
                "word.",
                "Two lines: the count, then the last word."],
               types=_P21_BOX),
    ])


_PRACTICE[21] = [_P21_A, _P21_B, _P21_C, _P21_D, _P21_E]
