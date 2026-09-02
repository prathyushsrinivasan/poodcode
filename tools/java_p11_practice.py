# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 11 practice - classes and objects.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[11]`.
#
# Module 11 scope: classes and objects, fields, instance methods, `this`,
# constructors and `this(...)` chaining, the default constructor, `static`,
# `final`, arrays of objects.
#
# NOT YET AVAILABLE, and the scope linter enforces it: `private` and
# `protected` are module 12, `extends` / `super` / `@Override` are module 13,
# `abstract` / `interface` / `implements` are module 14. So every field here is
# package-private (no modifier at all), and objects describe themselves through
# a `describe()` method rather than `toString()` - because `toString()` is an
# override, and overriding has not been taught yet.
# ---------------------------------------------------------------------------


def _p11ex(eid, title, difficulty, prompt, types, body, tests, hints):
    """The blanked region is the CLASS (or classes) above `main`."""
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


# --- Family A - a class with fields and a constructor ------------------------

_P11_A = _jfam(
    "p11-first", "Fields, a constructor, a method",
    "The three parts every class starts with.",
    """
A class is a **template**; an object is one thing built from it.

```java
class Point {
    int x;                          // FIELDS: what each Point knows
    int y;

    Point(int x, int y) {           // CONSTRUCTOR: how one gets built
        this.x = x;
        this.y = y;
    }

    String describe() {             // INSTANCE METHOD: what one can do
        return "(" + x + ", " + y + ")";
    }
}

Point p = new Point(3, 4);
System.out.println(p.describe());   // (3, 4)
```

Three things to notice, because they are what makes a class different from the
methods of module 9:

**Fields belong to the object, not the class.** Two `Point`s have two separate
`x`s. That is the whole reason objects exist — module 9's `static` counter had
exactly one copy, shared by everybody.

**A constructor has no return type**, not even `void`, and its name must match
the class exactly. Write `void Point(...)` by mistake and it silently becomes an
ordinary method, the constructor you wanted never exists, and `new Point(3, 4)`
stops compiling — a genuinely baffling error the first time.

**Instance methods read the fields without being passed them.** `describe()`
takes no parameters yet knows `x` and `y`, because it is called *on* an object.
There is no `static` on it, and that is deliberate: `static` would mean "belongs
to the class", and then there would be no object to read the fields from.

> Fields here have **no access modifier**, which makes them package-private.
> Module 12 makes them `private` and explains why that is almost always right.
""",
    [
        _p11ex("j11-pr-point", "A Point class", "Intro",
               "Write a `Point` class with `int x` and `int y`, a constructor taking "
               "both, and `String describe()` returning `(x, y)` — with a comma and a "
               "space. `main` reads two integers and prints the description.",
               """
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    String describe() {
        return "(" + x + ", " + y + ")";
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point p = new Point(px, py);
        System.out.println(p.describe());""",
               [_case(f"{x} {y}", f"({x}, {y})")
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["Two fields, declared at the top of the class with no modifier.",
                "The constructor has NO return type and is named exactly `Point`.",
                "`this.x = x;` assigns the parameter to the field — without `this.` "
                "you would assign the parameter to itself.",
                "`describe()` is an instance method: no `static`, no parameters, and "
                "it reads the fields directly.",
                "Mind the exact format: `(3, 4)` has a comma AND a space."]),

        _p11ex("j11-pr-rect", "A Rect that can measure itself", "Intro",
               "Write a `Rect` class with `int w` and `int h`, a constructor taking both, "
               "and `int area()` returning `w * h`. `main` reads two integers and prints "
               "the area.",
               """
class Rect {
    int w;
    int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    int area() {
        return w * h;
    }
}
""",
               """        int rw = sc.nextInt();
        int rh = sc.nextInt();
        Rect r = new Rect(rw, rh);
        System.out.println(r.area());""",
               [_case(f"{w} {h}", w * h)
                for (w, h) in ((3, 4), (1, 1), (0, 5), (12, 12), (7, 0))],
               ["Same three parts: fields, constructor, method.",
                "`area()` returns an `int` and takes no parameters.",
                "It uses the object's own `w` and `h` — there is nothing to pass "
                "in.",
                "A zero side gives zero area, which needs no special case."]),

        _p11ex("j11-pr-counter", "An object that remembers", "Easy",
               "Write a `Counter` class with `int count` starting at `0`, a no-argument "
               "constructor, `void increment()` and `int value()`. `main` reads `k` and "
               "increments the counter `k` times, then prints its value.",
               """
class Counter {
    int count;

    Counter() {
        this.count = 0;
    }

    void increment() {
        count = count + 1;
    }

    int value() {
        return count;
    }
}
""",
               """        int k = sc.nextInt();
        Counter c = new Counter();
        for (int i = 0; i < k; i++) {
            c.increment();
        }
        System.out.println(c.value());""",
               [_case(str(k), k) for k in (5, 0, 1, 100, 3)],
               ["A no-argument constructor is written `Counter() { ... }` — empty "
                "parentheses, still no return type.",
                "`increment()` returns `void`; it changes the object rather than "
                "handing anything back.",
                "`value()` returns the field.",
                "This is module 9's static counter done properly: the state now "
                "belongs to an object, so you could have two independent counters.",
                "`k` of `0` leaves it at its initial `0`."]),

        _p11ex("j11-pr-temperature", "A class that converts", "Easy",
               "Write a `Temperature` class with `int celsius`, a constructor taking it, "
               "and `int fahrenheit()` returning `celsius * 9 / 5 + 32` using integer "
               "arithmetic in that order.",
               """
class Temperature {
    int celsius;

    Temperature(int celsius) {
        this.celsius = celsius;
    }

    int fahrenheit() {
        return celsius * 9 / 5 + 32;
    }
}
""",
               """        int c = sc.nextInt();
        Temperature t = new Temperature(c);
        System.out.println(t.fahrenheit());""",
               [_case(str(c), _jdiv(c * 9, 5) + 32)
                for c in (100, 0, -40, 37, 25)],
               ["One field, one constructor parameter, one method.",
                "Follow the order exactly: multiply by 9, then divide by 5, then "
                "add 32.",
                "Doing `celsius / 5 * 9` instead would lose precision to integer "
                "division and give different answers.",
                "Case three is -40, the temperature where both scales agree."]),

        _p11ex("j11-pr-book", "A class with a String field", "Easy",
               "Write a `Book` class with `String title` and `int pages`, a constructor "
               "taking both, and `String summary()` returning `title (pages pages)` — "
               "for example `Dune (412 pages)`. `main` reads a one-word title then a "
               "number.",
               """
class Book {
    String title;
    int pages;

    Book(String title, int pages) {
        this.title = title;
        this.pages = pages;
    }

    String summary() {
        return title + " (" + pages + " pages)";
    }
}
""",
               """        String bt = sc.next();
        int bp = sc.nextInt();
        Book b = new Book(bt, bp);
        System.out.println(b.summary());""",
               [_case(f"{t} {p}", f"{t} ({p} pages)")
                for (t, p) in (("Dune", 412), ("x", 1), ("Java", 0),
                               ("Emma", 474), ("It", 1138))],
               ["Fields may be any type, including `String`.",
                "The constructor takes both and assigns both with `this.`.",
                "Build the summary with `+`; the exact shape is "
                "`title + \" (\" + pages + \" pages)\"`.",
                "Watch the spacing and the brackets — the judge compares exactly."]),
    ])


# --- Family B - this, and constructors ---------------------------------------

_P11_B = _jfam(
    "p11-this", "`this`, and more than one constructor",
    "Disambiguating, and delegating.",
    """
## `this` disambiguates

```java
Point(int x, int y) {
    this.x = x;        // field = parameter
    this.y = y;
}
```

The parameter `x` **shadows** the field `x` inside the constructor, so a bare
`x = x;` assigns the parameter to itself and leaves the field at its default of
`0`. The compiler does not complain — it is legal, just useless — so this is a
silent bug, and one of the most common in early Java.

`this.` is only *required* where a name is shadowed. Elsewhere the field is
visible without it, which is why `describe()` can say plain `x`. Many codebases
write `this.` everywhere anyway, for consistency.

## `this(...)` delegates

A class may have several constructors, distinguished exactly like overloaded
methods — by their parameter lists. One can call another:

```java
class Point {
    int x, y;

    Point(int x, int y) { this.x = x; this.y = y; }   // the real one
    Point(int v)        { this(v, v); }               // delegates
    Point()             { this(0, 0); }               // delegates
}
```

**`this(...)` must be the first statement** in the constructor, and a
constructor may not call itself in a cycle. Putting the real work in one
constructor and having the others delegate means validation lives in exactly one
place — which matters enormously once module 12 adds invariants.

## The default constructor

If you write **no** constructor at all, Java supplies a no-argument one that
leaves every field at its default (`0`, `false`, `null`). The moment you write
**any** constructor, that free one disappears — so adding `Point(int, int)`
breaks every existing `new Point()`. That surprise is worth meeting once
deliberately.
""",
    [
        _p11ex("j11-pr-shadow", "Assign the field, not the parameter", "Intro",
               "Write a `Box` class with `int size`, a constructor `Box(int size)` that "
               "must assign the field correctly despite the shadowing, and "
               "`int get()`.",
               """
class Box {
    int size;

    Box(int size) {
        this.size = size;
    }

    int get() {
        return size;
    }
}
""",
               """        int v = sc.nextInt();
        Box b = new Box(v);
        System.out.println(b.get());""",
               [_case(str(v), v) for v in (5, 0, -3, 100, 1)],
               ["The parameter and the field have the same name, so inside the "
                "constructor the plain name means the PARAMETER.",
                "`size = size;` would assign the parameter to itself and leave the "
                "field at `0`.",
                "`this.size` names the field explicitly.",
                "This is the single most common silent bug in early Java, which is "
                "why every constructor in this course writes `this.`."]),

        _p11ex("j11-pr-delegate", "One real constructor, one shortcut", "Medium",
               "Write a `Rect` class with `int w, h`, a two-argument constructor, and a "
               "one-argument constructor for a square that **delegates** with "
               "`this(...)` rather than assigning the fields again. Add `int area()`. "
               "`main` builds one of each.",
               """
class Rect {
    int w;
    int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    Rect(int side) {
        this(side, side);
    }

    int area() {
        return w * h;
    }
}
""",
               """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Rect r = new Rect(a1, b1);
        Rect sq = new Rect(a1);
        System.out.println(r.area());
        System.out.println(sq.area());""",
               [_case(f"{w} {h}", _nl(w * h, w * w))
                for (w, h) in ((3, 4), (1, 1), (0, 5), (12, 2), (7, 7))],
               ["Two constructors differing only in parameter count — the same "
                "overloading rule as module 9.",
                "The one-argument version must be `this(side, side);` and nothing "
                "else.",
                "`this(...)` has to be the FIRST statement in the constructor.",
                "Assigning the fields directly in both would work but duplicates the "
                "logic — the point is that there is one real constructor."]),

        _p11ex("j11-pr-noarg", "A default of your own", "Easy",
               "Write a `Config` class with `int retries` and `String mode`, a "
               "two-argument constructor, and a no-argument constructor delegating to it "
               "with `3` and `\"fast\"`. Add `String describe()` returning "
               "`mode/retries`. `main` prints both objects' descriptions.",
               """
class Config {
    int retries;
    String mode;

    Config(int retries, String mode) {
        this.retries = retries;
        this.mode = mode;
    }

    Config() {
        this(3, "fast");
    }

    String describe() {
        return mode + "/" + retries;
    }
}
""",
               """        int cr = sc.nextInt();
        String cm = sc.next();
        Config custom = new Config(cr, cm);
        Config fallback = new Config();
        System.out.println(custom.describe());
        System.out.println(fallback.describe());""",
               [_case(f"{r} {m}", _nl(f"{m}/{r}", "fast/3"))
                for (r, m) in ((5, "slow"), (0, "x"), (1, "safe"), (9, "fast"),
                               (2, "debug"))],
               ["The no-argument constructor supplies the defaults by delegating.",
                "`this(3, \"fast\");` — first statement, nothing before it.",
                "The second printed line is the same for every input, since it "
                "always uses the defaults.",
                "Note that writing ANY constructor removes the free one Java would "
                "have given you, which is exactly why this one has to be written "
                "out."]),

        _p11ex("j11-pr-derived", "A field computed at construction", "Medium",
               "Write a `Circle` class with `int radius` and `int diameter`, where the "
               "constructor takes only the radius and computes the diameter. Add "
               "`String describe()` returning `r=<radius> d=<diameter>`.",
               """
class Circle {
    int radius;
    int diameter;

    Circle(int radius) {
        this.radius = radius;
        this.diameter = radius * 2;
    }

    String describe() {
        return "r=" + radius + " d=" + diameter;
    }
}
""",
               """        int rr = sc.nextInt();
        Circle c = new Circle(rr);
        System.out.println(c.describe());""",
               [_case(str(r), f"r={r} d={r * 2}") for r in (5, 0, 1, 100, 7)],
               ["Not every field needs a constructor parameter.",
                "The constructor takes one value and derives the other.",
                "Assign `this.radius` first, then compute the diameter from it.",
                "Storing a derived value like this is a trade: it is fast to read "
                "but must be kept in step if the radius ever changes. Module 12 "
                "returns to that."]),

        _p11ex("j11-pr-validate", "A constructor that refuses bad values", "Medium",
               "Write an `Account` class with `int balance`, whose constructor **clamps** "
               "a negative starting balance to `0`. Add `int get()`. `main` reads one "
               "integer.",
               """
class Account {
    int balance;

    Account(int balance) {
        if (balance < 0) {
            this.balance = 0;
        } else {
            this.balance = balance;
        }
    }

    int get() {
        return balance;
    }
}
""",
               """        int ab = sc.nextInt();
        Account acc = new Account(ab);
        System.out.println(acc.get());""",
               [_case(str(v), max(v, 0)) for v in (100, 0, -50, 1, -1)],
               ["The constructor is the right place for this: it runs before anyone "
                "can see the object.",
                "Clamp rather than reject — the brief says a negative becomes `0`.",
                "Assign `this.balance` on both branches, or one route leaves the "
                "field unset.",
                "This is the beginning of a class INVARIANT: 'balance is never "
                "negative'. Module 12 makes that idea complete."]),
    ])


# --- Family C - static versus instance ---------------------------------------

_P11_C = _jfam(
    "p11-static", "`static` versus instance",
    "One copy for the class, or one copy per object.",
    """
```java
class Robot {
    static int built = 0;        // ONE copy, shared by the whole class
    int id;                      // one copy PER OBJECT

    Robot() {
        built = built + 1;       // the shared counter goes up
        this.id = built;         // this robot's own number
    }
}
```

**A `static` field belongs to the class.** Every `Robot` sees the same `built`.
An instance field belongs to the object: every `Robot` has its own `id`.

**A `static` method has no `this`.** That is the entire rule, and everything else
follows from it:

- A static method **cannot** read instance fields — there is no object to read
  them from. That is the *"non-static variable cannot be referenced from a static
  context"* error.
- An instance method **can** read static fields, because the class exists
  whenever an object does.

**Call them differently:**

```java
Robot.reset();              // static: on the CLASS
r.describe();               // instance: on an OBJECT
```

Calling a static member through an object (`r.built`) compiles but is misleading
and most tools warn about it — it hides that the value is shared.

**`static final` is a constant.** One copy, never reassigned, conventionally
named in capitals:

```java
static final int MAX = 100;
```

`main` itself is `static`, which is why module 9's helper methods all had to be
— there was no object in play at all.
""",
    [
        _p11ex("j11-pr-instances", "Count how many were made", "Medium",
               "Write a `Robot` class with a `static int built` starting at `0`, an "
               "instance field `int id`, and a no-argument constructor that increments "
               "`built` and sets this robot's `id` to the new value. Add `int getId()`. "
               "`main` builds `k` robots and prints the last one's id and the total.",
               """
class Robot {
    static int built = 0;
    int id;

    Robot() {
        built = built + 1;
        this.id = built;
    }

    int getId() {
        return id;
    }
}
""",
               """        int k = sc.nextInt();
        Robot last = null;
        for (int i = 0; i < k; i++) {
            last = new Robot();
        }
        System.out.println(last.getId());
        System.out.println(Robot.built);""",
               [_case(str(k), _nl(k, k)) for k in (5, 1, 3, 100, 2)],
               ["`built` is `static`, so there is exactly one of it however many "
                "robots exist.",
                "`id` has no `static`, so each robot gets its own.",
                "Increment the shared counter FIRST, then copy it into `this.id`, so "
                "the first robot is `1`.",
                "`Robot.built` is read through the class name, because that is what "
                "it belongs to.",
                "Every test has `k >= 1`, so `last` is never null when it is used."]),

        _p11ex("j11-pr-constant", "A shared constant", "Easy",
               "Write a `Limits` class with `static final int MAX = 100;` and a static "
               "method `static int clamp(int v)` returning `v` capped at `MAX` and "
               "floored at `0`. `main` reads one integer and prints the clamped value "
               "and then `MAX`.",
               """
class Limits {
    static final int MAX = 100;

    static int clamp(int v) {
        if (v < 0) {
            return 0;
        }
        if (v > MAX) {
            return MAX;
        }
        return v;
    }
}
""",
               """        int v = sc.nextInt();
        System.out.println(Limits.clamp(v));
        System.out.println(Limits.MAX);""",
               [_case(str(v), _nl(min(max(v, 0), 100), 100))
                for v in (50, -10, 150, 0, 100)],
               ["`static final` makes it a constant: one copy, never reassigned.",
                "The convention is to name constants in capitals.",
                "`clamp` is `static` because it needs no object — it works purely "
                "from its argument.",
                "Both are reached through the class name, `Limits.clamp(...)` and "
                "`Limits.MAX`.",
                "The class has no fields and no constructor at all, which is "
                "perfectly legal for a pure utility."]),

        _p11ex("j11-pr-static-vs-instance", "One of each", "Medium",
               "Write a `Tally` class with `static int total = 0;` and an instance field "
               "`int mine = 0;`. Give it `void add(int n)` which adds `n` to BOTH, and "
               "`int getMine()`. `main` makes two tallies, adds to each, and prints "
               "each one's own total and then the shared total.",
               """
class Tally {
    static int total = 0;
    int mine = 0;

    void add(int n) {
        total = total + n;
        mine = mine + n;
    }

    int getMine() {
        return mine;
    }
}
""",
               """        int x = sc.nextInt();
        int y = sc.nextInt();
        Tally a = new Tally();
        Tally b = new Tally();
        a.add(x);
        b.add(y);
        System.out.println(a.getMine());
        System.out.println(b.getMine());
        System.out.println(Tally.total);""",
               [_case(f"{x} {y}", _nl(x, y, x + y))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (10, 10), (100, 1))],
               ["`add` is an INSTANCE method, so it has a `this` and can touch both "
                "kinds of field.",
                "`total` is shared: both objects' additions land in the same "
                "variable.",
                "`mine` is per-object: each tally keeps its own.",
                "So the third line is always the sum of the first two.",
                "Initialising a field at its declaration (`= 0`) is allowed and runs "
                "before the constructor body."]),

        _p11ex("j11-pr-factory", "A static method that builds objects", "Medium",
               "Write a `Point` class with `int x, y`, a constructor, a "
               "`static Point origin()` returning a point at `(0, 0)`, and "
               "`String describe()` returning `(x, y)`. `main` prints a read point and "
               "then the origin.",
               """
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    static Point origin() {
        return new Point(0, 0);
    }

    String describe() {
        return "(" + x + ", " + y + ")";
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        System.out.println(new Point(px, py).describe());
        System.out.println(Point.origin().describe());""",
               [_case(f"{x} {y}", _nl(f"({x}, {y})", "(0, 0)"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["`origin()` is `static` because there is no existing Point to call "
                "it on — it MAKES one.",
                "It returns `new Point(0, 0)`.",
                "Call it through the class: `Point.origin()`.",
                "This is the static factory pattern, and it is why you write "
                "`List.of(...)` rather than a constructor in modern Java.",
                "A static method may create instances; what it cannot do is read "
                "instance fields without one."]),

        _p11ex("j11-pr-static-error", "Which fields can a static method see?", "Medium",
               "Write a `Meter` class with instance field `int reading` and static field "
               "`static int calls = 0;`. Give it a constructor taking the reading, an "
               "instance method `int read()` that increments `calls` and returns "
               "`reading`, and a static method `static int getCalls()` returning `calls`. "
               "`main` reads a value, calls `read()` twice, then prints the reading and "
               "the call count.",
               """
class Meter {
    int reading;
    static int calls = 0;

    Meter(int reading) {
        this.reading = reading;
    }

    int read() {
        calls = calls + 1;
        return reading;
    }

    static int getCalls() {
        return calls;
    }
}
""",
               """        int v = sc.nextInt();
        Meter m = new Meter(v);
        m.read();
        System.out.println(m.read());
        System.out.println(Meter.getCalls());""",
               [_case(str(v), _nl(v, 2)) for v in (5, 0, -3, 100, 1)],
               ["`read()` is an instance method, so it can touch BOTH `reading` and "
                "`calls`.",
                "`getCalls()` is static, so it may only touch `calls`. Adding "
                "`return reading;` there would not compile at all.",
                "That asymmetry is the rule: instance methods see everything, static "
                "methods see only static things.",
                "`read()` is called twice, so the count is always `2`."]),
    ])


# --- Family D - arrays of objects --------------------------------------------

_P11_D = _jfam(
    "p11-arrays", "Arrays of objects",
    "Everything from module 1, with objects in the slots.",
    """
```java
Item[] items = new Item[n];        // n slots, ALL null so far
for (int i = 0; i < n; i++) {
    items[i] = new Item(...);      // now each slot holds an object
}
```

**`new Item[n]` does not create any items.** It creates an array of `n`
*references*, every one of them `null`. Forgetting the second step and calling
`items[0].price()` gives you a `NullPointerException`, which is the single most
common runtime error in Java.

Once populated, every pattern from module 1 works unchanged — the only
difference is that the comparison reads a field or calls a method instead of
looking at the value directly:

```java
Item best = items[0];                       // seed with a real element
for (int i = 1; i < items.length; i++) {
    if (items[i].price > best.price) {      // compare a FIELD
        best = items[i];
    }
}
```

The running maximum, the counter, the accumulator — all identical in shape to
the `int[]` versions, which is the point. Learning objects does not mean
relearning loops.

**The enhanced `for` is especially nice here**, because you almost never need
the index:

```java
int total = 0;
for (Item it : items) total += it.price;
```
""",
    [
        _p11ex("j11-pr-build-array", "Build them and describe them", "Easy",
               "Write an `Item` class with `String name` and `int price`, a constructor, "
               "and `String describe()` returning `name:price`. `main` reads `n`, then "
               "`n` pairs of a one-word name and a price, and prints each item's "
               "description on its own line.",
               """
class Item {
    String name;
    int price;

    Item(String name, int price) {
        this.name = name;
        this.price = price;
    }

    String describe() {
        return name + ":" + price;
    }
}
""",
               """        int n = sc.nextInt();
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            items[i] = new Item(sc.next(), sc.nextInt());
        }
        for (int i = 0; i < n; i++) {
            System.out.println(items[i].describe());
        }""",
               [_case("\n".join([str(len(rows))] + [f"{nm} {pr}" for (nm, pr) in rows]),
                      _nl(*[f"{nm}:{pr}" for (nm, pr) in rows]))
                for rows in ([("apple", 3), ("pear", 5)],
                             [("x", 0)],
                             [("a", 1), ("b", 2), ("c", 3)],
                             [("solo", 99)],
                             [("p", -1), ("q", 10)])],
               ["Two fields, a constructor assigning both, one `describe()`.",
                "`main` is already written and does the allocating and filling.",
                "Note what it does: `new Item[n]` makes the slots, and the loop "
                "fills them. Skipping the second step would give a "
                "NullPointerException.",
                "The format is `name:price` with no spaces."]),

        _p11ex("j11-pr-total", "Total them up", "Easy",
               "Write the same `Item` class, plus `int getPrice()`. `main` reads the "
               "items and prints the total of their prices.",
               """
class Item {
    String name;
    int price;

    Item(String name, int price) {
        this.name = name;
        this.price = price;
    }

    int getPrice() {
        return price;
    }
}
""",
               """        int n = sc.nextInt();
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            items[i] = new Item(sc.next(), sc.nextInt());
        }
        int total = 0;
        for (Item it : items) {
            total += it.getPrice();
        }
        System.out.println(total);""",
               [_case("\n".join([str(len(rows))] + [f"{nm} {pr}" for (nm, pr) in rows]),
                      sum(pr for (_nm, pr) in rows))
                for rows in ([("apple", 3), ("pear", 5)],
                             [("x", 0)],
                             [("a", 1), ("b", 2), ("c", 3)],
                             [("solo", 99)],
                             [("p", -1), ("q", 10)])],
               ["Module 1's accumulator, with `it.getPrice()` where `a[i]` used to "
                "be.",
                "The enhanced `for` works over an object array exactly as over an "
                "`int[]`.",
                "`getPrice()` is an instance method returning the field.",
                "The loop in `main` is given; your job is the class."]),

        _p11ex("j11-pr-max-object", "The most expensive one", "Medium",
               "Write the same `Item` class with `getPrice()` and `getName()`. `main` "
               "prints the name of the most expensive item, first on a tie.",
               """
class Item {
    String name;
    int price;

    Item(String name, int price) {
        this.name = name;
        this.price = price;
    }

    int getPrice() {
        return price;
    }

    String getName() {
        return name;
    }
}
""",
               """        int n = sc.nextInt();
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            items[i] = new Item(sc.next(), sc.nextInt());
        }
        Item best = items[0];
        for (int i = 1; i < n; i++) {
            if (items[i].getPrice() > best.getPrice()) {
                best = items[i];
            }
        }
        System.out.println(best.getName());""",
               [_case("\n".join([str(len(rows))] + [f"{nm} {pr}" for (nm, pr) in rows]),
                      max(rows, key=lambda r: r[1])[0])
                for rows in ([("apple", 3), ("pear", 5)],
                             [("x", 0)],
                             [("a", 1), ("b", 3), ("c", 3)],
                             [("solo", 99)],
                             [("p", -1), ("q", 10)])],
               ["The class needs two getters this time.",
                "`main` runs module 1's running maximum, but the variable it keeps "
                "is an `Item`, not an `int`.",
                "Seeding with `items[0]` is what makes negative prices work.",
                "A strict `>` keeps the first of equal prices — case three has two "
                "items at 3 and wants `b`."]),

        _p11ex("j11-pr-count-matching", "How many are over the line?", "Easy",
               "Write the same `Item` class with `boolean costsMoreThan(int k)` returning "
               "whether this item's price is strictly greater than `k`. `main` reads the "
               "items, then `k`, and prints how many match.",
               """
class Item {
    String name;
    int price;

    Item(String name, int price) {
        this.name = name;
        this.price = price;
    }

    boolean costsMoreThan(int k) {
        return price > k;
    }
}
""",
               """        int n = sc.nextInt();
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            items[i] = new Item(sc.next(), sc.nextInt());
        }
        int k = sc.nextInt();
        int count = 0;
        for (Item it : items) {
            if (it.costsMoreThan(k)) {
                count++;
            }
        }
        System.out.println(count);""",
               [_case("\n".join([str(len(rows))] + [f"{nm} {pr}" for (nm, pr) in rows]
                                + [str(k)]),
                      sum(1 for (_nm, pr) in rows if pr > k))
                for (rows, k) in (([("apple", 3), ("pear", 5)], 4),
                                  ([("x", 0)], 0),
                                  ([("a", 1), ("b", 2), ("c", 3)], 0),
                                  ([("solo", 99)], 100),
                                  ([("p", -1), ("q", 10)], -5))],
               ["The method takes a parameter AND reads a field — it can do both, "
                "because it is an instance method.",
                "`return price > k;` returns the boolean directly; no `if` is "
                "needed.",
                "**Strictly** greater, so an item priced exactly `k` does not "
                "count.",
                "Putting the test on the object rather than in the loop is the point "
                "— the loop no longer needs to know what 'expensive' means."]),

        _p11ex("j11-pr-cheapest-name", "Cheapest, and its price", "Medium",
               "Write the same `Item` class with `getPrice()` and `getName()`. `main` "
               "prints the cheapest item's name and price on one line separated by a "
               "space, taking the first on a tie.",
               """
class Item {
    String name;
    int price;

    Item(String name, int price) {
        this.name = name;
        this.price = price;
    }

    int getPrice() {
        return price;
    }

    String getName() {
        return name;
    }
}
""",
               """        int n = sc.nextInt();
        Item[] items = new Item[n];
        for (int i = 0; i < n; i++) {
            items[i] = new Item(sc.next(), sc.nextInt());
        }
        Item best = items[0];
        for (int i = 1; i < n; i++) {
            if (items[i].getPrice() < best.getPrice()) {
                best = items[i];
            }
        }
        System.out.println(best.getName() + " " + best.getPrice());""",
               [_case("\n".join([str(len(rows))] + [f"{nm} {pr}" for (nm, pr) in rows]),
                      (lambda b: f"{b[0]} {b[1]}")(min(rows, key=lambda r: r[1])))
                for rows in ([("apple", 3), ("pear", 5)],
                             [("x", 0)],
                             [("a", 3), ("b", 1), ("c", 1)],
                             [("solo", 99)],
                             [("p", -1), ("q", 10)])],
               ["Same class as the maximum variant — the difference is entirely in "
                "`main`'s comparison.",
                "A strict `<` keeps the first of equal prices; case three has two "
                "items at 1 and wants `b`.",
                "Keeping the whole `Item` rather than just the price is what lets "
                "you print both fields at the end.",
                "That is the real advantage of objects over parallel arrays: the "
                "name and price cannot drift apart."]),
    ])


# --- Family E - final, references and identity -------------------------------

_P11_E = _jfam(
    "p11-refs", "References, copies and `final`",
    "Two names for one object, and a field that never changes.",
    """
Module 1 made this point about arrays. It applies to **every** object, and it
matters more now.

```java
Point a = new Point(1, 2);
Point b = a;            // NOT a copy — a second name for the same object
b.x = 99;
System.out.println(a.x);  // 99
```

An object variable holds a **reference**. Assignment copies the reference, not
the object, so both names reach the same thing. To get a genuine copy you must
build one — a **copy constructor** is the usual way:

```java
Point(Point other) {
    this(other.x, other.y);
}
```

**`==` on objects compares references**, exactly as it did on arrays and
Strings:

```java
Point p = new Point(1, 2);
Point q = new Point(1, 2);
p == q;                   // false — two different objects
p.x == q.x && p.y == q.y; // true  — same contents
```

Comparing contents properly means overriding `equals`, which is module 13. Until
then, compare the fields by hand.

**`final` on a field** means it must be assigned exactly once — at its
declaration or in every constructor — and never again:

```java
class Point {
    final int x;
    Point(int x) { this.x = x; }     // fine
    void move() { x = 5; }           // does not compile
}
```

It buys you a guarantee the compiler enforces. Note carefully what it does *not*
do: `final Point p` means the **reference** cannot be repointed, not that the
object cannot change. `p.x = 9;` is still legal if `x` is not itself final.
""",
    [
        _p11ex("j11-pr-alias-obj", "Two names, one object", "Easy",
               "Write a `Point` class with `int x, y`, a constructor, and "
               "`String describe()` returning `(x, y)`. `main` makes one point, takes a "
               "second reference to it, changes `x` through the second, and prints "
               "**both** descriptions — which will match.",
               """
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    String describe() {
        return "(" + x + ", " + y + ")";
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = a;
        b.x = 99;
        System.out.println(a.describe());
        System.out.println(b.describe());""",
               [_case(f"{x} {y}", _nl(f"(99, {y})", f"(99, {y})"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["`Point b = a;` copies the reference, so both names reach one "
                "object.",
                "Writing `b.x = 99` therefore changes what `a` sees too.",
                "Both printed lines are identical, whatever was read.",
                "The original `x` is gone entirely — this is module 1's array "
                "aliasing, now with objects."]),

        _p11ex("j11-pr-copy-ctor", "A real copy", "Medium",
               "Write a `Point` class with `int x, y`, a two-argument constructor, a "
               "**copy constructor** `Point(Point other)` that delegates with "
               "`this(...)`, and `String describe()`. `main` copies a point, changes the "
               "copy, and prints both — and the original must be unchanged.",
               """
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    Point(Point other) {
        this(other.x, other.y);
    }

    String describe() {
        return "(" + x + ", " + y + ")";
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = new Point(a);
        b.x = 99;
        System.out.println(a.describe());
        System.out.println(b.describe());""",
               [_case(f"{x} {y}", _nl(f"({x}, {y})", f"(99, {y})"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["A copy constructor takes an object of the same class.",
                "It can read `other.x` directly, because code inside a class may "
                "reach another instance's fields.",
                "Delegate with `this(other.x, other.y);` so the real constructor "
                "still does the work.",
                "Now the two objects are independent and only the copy changes.",
                "Compare with the previous variant, which differs by one word in "
                "`main`."]),

        _p11ex("j11-pr-identity", "Same contents, different objects", "Medium",
               "Write a `Point` class with `int x, y`, a constructor, and "
               "`boolean sameAs(Point other)` comparing both fields. `main` builds two "
               "points from the same numbers and prints `a == b` and then "
               "`a.sameAs(b)`.",
               """
class Point {
    int x;
    int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    boolean sameAs(Point other) {
        return this.x == other.x && this.y == other.y;
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = new Point(px, py);
        System.out.println(a == b);
        System.out.println(a.sameAs(b));""",
               [_case(f"{x} {y}", _nl("false", "true"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["`==` asks whether they are the SAME object, which two separate "
                "`new` calls never are — so the first line is always `false`.",
                "`sameAs` compares the fields, so the second line is always `true`.",
                "Compare `int` fields with `==`; that is correct for primitives.",
                "The proper solution is to override `equals`, which is module 13. "
                "This is the hand-rolled version of it.",
                "This is the same identity-versus-value distinction as `==` on "
                "Strings in module 6."]),

        _p11ex("j11-pr-final-field", "A field that never changes", "Easy",
               "Write an `Id` class with `final int value`, a constructor that assigns "
               "it, and `int get()`. `main` builds one and prints its value.",
               """
class Id {
    final int value;

    Id(int value) {
        this.value = value;
    }

    int get() {
        return value;
    }
}
""",
               """        int v = sc.nextInt();
        Id id = new Id(v);
        System.out.println(id.get());""",
               [_case(str(v), v) for v in (5, 0, -3, 100, 1)],
               ["`final` on a field means it is assigned exactly once.",
                "A final field may be set at its declaration OR in the constructor — "
                "here it is the constructor.",
                "Adding a method that assigns `value` again would not compile, which "
                "is the guarantee you are buying.",
                "There is no setter, and there cannot be one."]),

        _p11ex("j11-pr-null-default", "Empty slots and default values", "Medium",
               "Write a `Slot` class with `int number` and `String label`, and a "
               "no-argument constructor that assigns **nothing at all**. Add "
               "`String describe()` returning `number/label`. `main` builds one and "
               "prints its description — showing Java's defaults.",
               """
class Slot {
    int number;
    String label;

    Slot() {
    }

    String describe() {
        return number + "/" + label;
    }
}
""",
               """        int ignored = sc.nextInt();
        Slot s = new Slot();
        System.out.println(s.describe());
        Slot[] arr = new Slot[2];
        System.out.println(arr[0] == null);""",
               [_case(str(v), _nl("0/null", "true")) for v in (5, 0, -3, 100, 1)],
               ["The constructor body is genuinely empty — Java initialises the "
                "fields for you.",
                "An `int` field defaults to `0` and a `String` field to `null`.",
                "Concatenating a null String gives the four characters `null` rather "
                "than throwing, which is why the first line is `0/null`.",
                "`new Slot[2]` creates two NULL references, not two Slots — hence "
                "the second line.",
                "That is the NullPointerException waiting in every array of objects "
                "you forget to fill."]),
    ])


_PRACTICE[11] = [_P11_A, _P11_B, _P11_C, _P11_D, _P11_E]
