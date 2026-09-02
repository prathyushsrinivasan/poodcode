# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 11 — Classes and objects.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`. Opens
# Part 4 of JAVA_ROADMAP.md, the heaviest section in Java and the one interviews
# probe hardest.
#
# Programs use `_joop(types, body)`: helper classes above `public class Main`,
# in the same file. `javac Main.java` compiles the lot and `java -cp . Main`
# runs it, so no build change was needed — only `Main` may be `public`.
#
# The through-line: a class is a TYPE you define, an object is one value of it,
# and a reference variable is neither. Module 1's aliasing lesson comes back
# here with objects instead of arrays, and it is the same lesson.
# ---------------------------------------------------------------------------

_M11 = []


# --- 11.1 Classes and objects ----------------------------------------------

_M11.append(_jlesson(
    "m11-class", "Classes, objects and references",
    "A type you define, a value of it, and the variable that points at one.",
    """
Everything so far has used types Java gave you — `int`, `String`, `int[]`. A
**class** is a type *you* define, bundling related data under one name.

```java
class Point {
    int x;              // a FIELD (also called an instance variable)
    int y;
}
```

That declares a type. It creates nothing. To make an actual **object** you use
`new`:

```java
Point p = new Point();      // one object on the heap
p.x = 3;                     // reach a field with a dot
p.y = 4;
System.out.println(p.x + "," + p.y);      // 3,4
```

Three words that are worth keeping separate:

| Word | What it is |
|---|---|
| **class** | the blueprint — a type, written once |
| **object** | one thing built from it, living on the heap |
| **reference** | the variable holding the object's address |

`new Point()` does two things: it allocates the object and it hands back a
reference to it. `Point p` is the variable that holds that reference.

**Fields get default values**, exactly like array slots: `0` for numeric types,
`false` for `boolean`, `null` for object types. A brand new `Point` is already
`(0, 0)` — never garbage.

**References behave exactly as array references did in module 1.**

```java
Point a = new Point();
a.x = 1;
Point b = a;            // b and a point at the SAME object
b.x = 99;
System.out.println(a.x);    // 99
```

One object, two names. This is module 1's aliasing lesson with a class instead
of an array, and it is why `==` on objects asks the wrong question — it compares
references, which is precisely the `String` trap from module 6, now generalised
to every type you will ever write.

```java
Point c = new Point();
Point d = new Point();      // two separate objects, both (0, 0)
c == d                       // false — different objects
```

**`null` means "this reference points at nothing".** Calling anything through it
is a `NullPointerException`:

```java
Point e = null;
e.x = 1;                    // NullPointerException at runtime
```

**Where classes go.** In this course, above `public class Main` in the same
file. Only one class per file may be `public`, and its name must match the
file — which is why `Main` is the public one and your types are not. Real
projects give each class its own file.
""",
    warmup=[
        _jq("```java\nclass Point { int x; int y; }\nPoint p = new Point();\nSystem.out.println(p.x);\n```",
            ["0", "null", "an unpredictable value", "NullPointerException"],
            0,
            "Fields get the same defaults as array slots — 0 for numeric types. Java never "
            "hands you an uninitialised field."),
        _jq("```java\nPoint a = new Point();\nPoint b = a;\nb.x = 99;\nSystem.out.println(a.x);\n```",
            ["99", "0", "It does not compile", "NullPointerException"],
            0,
            "`b = a` copies the reference, not the object. One object, two names — module 1's "
            "array aliasing, now with a class."),
    ],
    exercises=[
        _je("j11-cls-new", "Make one",
            "`Point` is declared for you. Read two numbers, put them in a new "
            "`Point`, and print them back as `x,y`. Replace `____` with the line "
            "that creates the object.",
            _joop("class Point {\n"
                  "    int x;\n"
                  "    int y;\n"
                  "}",
                  "        Point p = new Point();\n"
                  "        p.x = sc.nextInt();\n"
                  "        p.y = sc.nextInt();\n"
                  '        System.out.println(p.x + "," + p.y);'),
            "Point p = new Point();",
            [_case(f"{x}\n{y}", f"{x},{y}") for (x, y) in ((3, 4), (0, 0), (-2, 7))],
            hints=["`new` allocates the object and gives you a reference to it.",
                   "The variable's type is the class name.",
                   "`Point p = new Point();`"],
            difficulty="Intro"),

        _je("j11-cls-field", "Reach a field",
            "The `Point` is built and filled. Replace `____` with the expression "
            "that reads its `y` field.",
            _joop("class Point {\n"
                  "    int x;\n"
                  "    int y;\n"
                  "}",
                  "        Point p = new Point();\n"
                  "        p.x = sc.nextInt();\n"
                  "        p.y = sc.nextInt();\n"
                  "        System.out.println(p.y);"),
            "p.y",
            [_case(f"{x}\n{y}", y) for (x, y) in ((3, 4), (10, -5), (0, 9))],
            hints=["A dot reaches into an object.",
                   "The variable, then the field name.",
                   "`p.y`"],
            difficulty="Intro"),

        _je("j11-cls-two", "Two objects, not one",
            "Read four numbers into **two separate** `Point`s and print the "
            "distance between them along x, then along y. Replace `____` with the "
            "line that creates the second point — it must not be the first one "
            "under another name.",
            _joop("class Point {\n"
                  "    int x;\n"
                  "    int y;\n"
                  "}",
                  "        Point a = new Point();\n"
                  "        a.x = sc.nextInt();\n"
                  "        a.y = sc.nextInt();\n"
                  "        Point b = new Point();\n"
                  "        b.x = sc.nextInt();\n"
                  "        b.y = sc.nextInt();\n"
                  '        System.out.println((b.x - a.x) + " " + (b.y - a.y));'),
            "Point b = new Point();",
            [_case(f"{ax}\n{ay}\n{bx}\n{by}", f"{bx - ax} {by - ay}")
             for (ax, ay, bx, by) in ((1, 2, 4, 6), (0, 0, 0, 0), (5, 5, 1, 1))],
            hints=["`Point b = a;` would give the first object a second name.",
                   "You need a second `new`.",
                   "`Point b = new Point();`"]),

        _jfix("j11-cls-alias", "Two names for one object",
              "This should build two independent points and print `1 2` then "
              "`3 4`. It prints `3 4` twice — there is only one object.",
              _joop("class Point {\n"
                    "    int x;\n"
                    "    int y;\n"
                    "}",
                    "        Point a = new Point();\n"
                    "        a.x = sc.nextInt();\n"
                    "        a.y = sc.nextInt();\n"
                    "        Point b = a;\n"
                    "        b.x = sc.nextInt();\n"
                    "        b.y = sc.nextInt();\n"
                    '        System.out.println(a.x + " " + a.y);\n'
                    '        System.out.println(b.x + " " + b.y);'),
              _joop("class Point {\n"
                    "    int x;\n"
                    "    int y;\n"
                    "}",
                    "        Point a = new Point();\n"
                    "        a.x = sc.nextInt();\n"
                    "        a.y = sc.nextInt();\n"
                    "        Point b = new Point();\n"
                    "        b.x = sc.nextInt();\n"
                    "        b.y = sc.nextInt();\n"
                    '        System.out.println(a.x + " " + a.y);\n'
                    '        System.out.println(b.x + " " + b.y);'),
              [_case(f"{ax}\n{ay}\n{bx}\n{by}", _nl(f"{ax} {ay}", f"{bx} {by}"))
               for (ax, ay, bx, by) in ((1, 2, 3, 4), (0, 0, 9, 9), (-1, -2, -3, -4))],
              hints=["How many times does the program call `new`?",
                     "`Point b = a;` copies a reference, exactly like `int[] b = a;` did.",
                     "`Point b = new Point();`"]),

        _jch("j11-cls-array", "An array of objects", "Medium",
             "Read `n`, then `n` pairs of numbers, into an **array of `Point`s**. "
             "Print the sum of all the `x` values, then the sum of all the `y` "
             "values, on one line. Remember `new Point[n]` gives you `n` **null** "
             "slots — each one still needs its own `new Point()`. Write the whole "
             "block where you see `____`.",
             _joop("class Point {\n"
                   "    int x;\n"
                   "    int y;\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        Point[] ps = new Point[n];\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            ps[i] = new Point();\n"
                   "            ps[i].x = sc.nextInt();\n"
                   "            ps[i].y = sc.nextInt();\n"
                   "        }\n"
                   "        int sx = 0;\n"
                   "        int sy = 0;\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            sx += ps[i].x;\n"
                   "            sy += ps[i].y;\n"
                   "        }\n"
                   '        System.out.println(sx + " " + sy);'),
             "        Point[] ps = new Point[n];\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            ps[i] = new Point();\n"
             "            ps[i].x = sc.nextInt();\n"
             "            ps[i].y = sc.nextInt();\n"
             "        }\n"
             "        int sx = 0;\n"
             "        int sy = 0;\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            sx += ps[i].x;\n"
             "            sy += ps[i].y;\n"
             "        }\n"
             '        System.out.println(sx + " " + sy);',
             [_case(f"{len(pts)}\n" + "\n".join(f"{x}\n{y}" for (x, y) in pts),
                    f"{sum(x for (x, _) in pts)} {sum(y for (_, y) in pts)}")
              for pts in ([(1, 2), (3, 4)], [(5, 5)], [(1, 1), (2, 2), (3, 3)],
                          [(-1, 4), (1, -4)])],
             hints=["`new Point[n]` allocates the ARRAY. Every slot starts as `null`.",
                    "So the loop needs `ps[i] = new Point();` before it can touch `ps[i].x`.",
                    "Forgetting that line is a NullPointerException, which is the single most "
                    "common mistake with object arrays.",
                    "A second loop totals the two coordinates."]),
    ],
    quiz=[
        _jq("`Point[] ps = new Point[3];` — how many Point objects exist?",
            ["Zero — three null slots, each still needing its own `new Point()`",
             "Three", "One", "It does not compile"],
            0,
            "Only the array was allocated. Its element type is an object type, so the slots "
            "default to `null` — module 1's default-value table, still true."),
        _jq("What does `==` compare for two `Point` variables?",
            ["Their references — whether they point at the same object",
             "Their x and y fields",
             "Nothing; it does not compile",
             "Their hash codes"],
            0,
            "The same rule as `String` in module 6, generalised: `==` on any object type is "
            "reference identity. Comparing contents is `equals`, which module 12 makes you "
            "write."),
    ],
))

# --- 11.2 Instance methods and `this` --------------------------------------

_M11.append(_jlesson(
    "m11-methods", "Methods inside a class",
    "Behaviour that travels with the data — and what `this` actually refers to.",
    """
Fields are the data; **methods inside the class** are what the data can do.

```java
class Point {
    int x;
    int y;

    int distanceFromOriginSquared() {
        return x * x + y * y;         // fields are just in scope
    }

    void moveBy(int dx, int dy) {
        x += dx;
        y += dy;                       // an instance method CAN modify its object
    }
}

Point p = new Point();
p.x = 3; p.y = 4;
System.out.println(p.distanceFromOriginSquared());   // 25
```

Note what is missing: no `static`, and no parameter for the point itself. An
**instance method** is called *on* an object (`p.method()`), and inside it the
fields of that object are simply in scope.

**`this` is the object the method was called on.** It is an implicit parameter
you never declare:

```java
int distanceFromOriginSquared() {
    return this.x * this.x + this.y * this.y;    // same as before
}
```

Writing `this.` is optional when nothing is shadowing the field — and required
when something is:

```java
void setX(int x) {          // the parameter `x` shadows the field `x`
    x = x;                   // assigns the parameter to itself. Does NOTHING.
    this.x = x;              // field = parameter. Correct.
}
```

That is module 9's shadowing bug in the place it appears most often. `this.x = x`
is not a style choice; it is the only thing that works, and it is why you see it
in essentially every setter and constructor in Java.

**Instance versus static, stated once:**

| | Instance method | Static method |
|---|---|---|
| Belongs to | one object | the class |
| Called as | `p.move(1, 2)` | `Math.max(a, b)` |
| Can use fields | yes | no — there is no object |
| Can use `this` | yes | no |

A static method has no object, so it cannot touch instance fields — that is
exactly the *"non-static method cannot be referenced from a static context"*
error from module 9, now from the other side. `main` is static, which is why it
has to build objects before it can call anything on them.

**Methods can return objects**, which is how you write a version that leaves the
original alone:

```java
Point movedBy(int dx, int dy) {
    Point result = new Point();
    result.x = x + dx;
    result.y = y + dy;
    return result;             // a NEW point; this one is untouched
}
```

Mutate-in-place versus return-a-new-one is the same choice module 9 framed as
`sortInPlace(a)` versus `sorted(a)` — and the name should say which.
""",
    warmup=[
        _jq("```java\nvoid setX(int x) { x = x; }\n```\nAfter `p.setX(5)`, what is `p.x`?",
            ["Unchanged — the parameter was assigned to itself",
             "5", "0", "It does not compile"],
            0,
            "The parameter shadows the field, so both sides of the assignment are the "
            "parameter. `this.x = x;` is the fix, and the reason `this` exists."),
        _jq("Why can't a `static` method read an instance field?",
            ["It has no object — there is no particular field to read",
             "Because instance fields are private",
             "It can, with a cast",
             "Because static methods run before objects exist"],
            0,
            "Instance fields belong to objects, and a static method was not called on one. "
            "Same error as module 9, seen from the other direction."),
    ],
    exercises=[
        _je("j11-mth-instance", "A method that uses its fields",
            "`area()` should return the rectangle's area. Inside an instance method "
            "the fields are simply in scope. Replace `____` with the body.",
            _joop("class Rect {\n"
                  "    int w;\n"
                  "    int h;\n"
                  "\n"
                  "    int area() {\n"
                  "        return w * h;\n"
                  "    }\n"
                  "}",
                  "        Rect r = new Rect();\n"
                  "        r.w = sc.nextInt();\n"
                  "        r.h = sc.nextInt();\n"
                  "        System.out.println(r.area());"),
            "        return w * h;",
            [_case(f"{w}\n{h}", w * h) for (w, h) in ((3, 4), (1, 1), (7, 0), (5, 9))],
            hints=["No parameters needed — the data is already in the object.",
                   "`w` and `h` refer to this object's fields.",
                   "`return w * h;`"],
            difficulty="Intro"),

        _je("j11-mth-this", "The setter that needs `this`",
            "`setW` takes a parameter named `w`, which shadows the field named `w`. "
            "Replace `____` with the assignment that actually updates the field.",
            _joop("class Rect {\n"
                  "    int w;\n"
                  "    int h;\n"
                  "\n"
                  "    void setW(int w) {\n"
                  "        this.w = w;\n"
                  "    }\n"
                  "}",
                  "        Rect r = new Rect();\n"
                  "        r.setW(sc.nextInt());\n"
                  "        r.h = sc.nextInt();\n"
                  '        System.out.println(r.w + " " + r.h);'),
            "        this.w = w;",
            [_case(f"{w}\n{h}", f"{w} {h}") for (w, h) in ((3, 4), (0, 0), (-2, 8))],
            hints=["Plain `w` means the parameter, because it shadows the field.",
                   "The field has to be named explicitly.",
                   "`this.w = w;` — field on the left, parameter on the right."]),

        _je("j11-mth-mutate", "A method that changes its object",
            "`grow` should add `dw` to the width and `dh` to the height, in place. "
            "Replace `____` with the body.",
            _joop("class Rect {\n"
                  "    int w;\n"
                  "    int h;\n"
                  "\n"
                  "    void grow(int dw, int dh) {\n"
                  "        w += dw;\n"
                  "        h += dh;\n"
                  "    }\n"
                  "}",
                  "        Rect r = new Rect();\n"
                  "        r.w = sc.nextInt();\n"
                  "        r.h = sc.nextInt();\n"
                  "        r.grow(sc.nextInt(), sc.nextInt());\n"
                  '        System.out.println(r.w + " " + r.h);'),
            "        w += dw;\n"
            "        h += dh;",
            [_case(f"{w}\n{h}\n{dw}\n{dh}", f"{w + dw} {h + dh}")
             for (w, h, dw, dh) in ((3, 4, 1, 1), (0, 0, 5, -5), (10, 10, -3, 2))],
            hints=["An instance method can assign to its own object's fields.",
                   "No `this.` needed here — nothing is shadowing.",
                   "`w += dw;` then `h += dh;`"],
            difficulty="Intro"),

        _jfix("j11-mth-static", "Static cannot see an object",
              "`area()` is marked `static`, so it has no object and cannot read `w` "
              "or `h`. The program does not compile. Make it an instance method.",
              _joop("class Rect {\n"
                    "    int w;\n"
                    "    int h;\n"
                    "\n"
                    "    static int area() {\n"
                    "        return w * h;\n"
                    "    }\n"
                    "}",
                    "        Rect r = new Rect();\n"
                    "        r.w = sc.nextInt();\n"
                    "        r.h = sc.nextInt();\n"
                    "        System.out.println(r.area());"),
              _joop("class Rect {\n"
                    "    int w;\n"
                    "    int h;\n"
                    "\n"
                    "    int area() {\n"
                    "        return w * h;\n"
                    "    }\n"
                    "}",
                    "        Rect r = new Rect();\n"
                    "        r.w = sc.nextInt();\n"
                    "        r.h = sc.nextInt();\n"
                    "        System.out.println(r.area());"),
              [_case(f"{w}\n{h}", w * h) for (w, h) in ((3, 4), (6, 7), (2, 0))],
              hints=["Which object's `w` would a static method read?",
                     "`main` already calls it on an object: `r.area()`.",
                     "Drop the `static`."],
              difficulty="Intro"),

        _jch("j11-mth-return", "Return a new object", "Medium",
             "Add `scaled(int k)`, which returns a **new** `Rect` with both sides "
             "multiplied by `k`, leaving the original untouched. `main` prints the "
             "scaled one and then the original, so a method that mutated in place "
             "would fail. Write the whole method where you see `____`.",
             _joop("class Rect {\n"
                   "    int w;\n"
                   "    int h;\n"
                   "\n"
                   "    Rect scaled(int k) {\n"
                   "        Rect out = new Rect();\n"
                   "        out.w = w * k;\n"
                   "        out.h = h * k;\n"
                   "        return out;\n"
                   "    }\n"
                   "}",
                   "        Rect r = new Rect();\n"
                   "        r.w = sc.nextInt();\n"
                   "        r.h = sc.nextInt();\n"
                   "        Rect s = r.scaled(sc.nextInt());\n"
                   '        System.out.println(s.w + " " + s.h);\n'
                   '        System.out.println(r.w + " " + r.h);'),
             "    Rect scaled(int k) {\n"
             "        Rect out = new Rect();\n"
             "        out.w = w * k;\n"
             "        out.h = h * k;\n"
             "        return out;\n"
             "    }",
             [_case(f"{w}\n{h}\n{k}", _nl(f"{w * k} {h * k}", f"{w} {h}"))
              for (w, h, k) in ((3, 4, 2), (5, 5, 1), (2, 7, 0), (1, 2, 10))],
             hints=["The return type is the class itself: `Rect scaled(int k)`.",
                    "Build a new object inside, fill it from this object's fields, return it.",
                    "Do NOT assign to `w` or `h` — the second printed line proves the "
                    "original survived."]),
    ],
    quiz=[
        _jq("When is writing `this.` required rather than optional?",
            ["When a parameter or local shadows the field you mean",
             "Always, in every method",
             "Only in static methods",
             "Only when the field is an object type"],
            0,
            "Without shadowing the compiler resolves a bare name to the field anyway. With "
            "shadowing, the bare name is the parameter — which is why every setter has it."),
        _jq("A method that changes its object versus one that returns a new one — how should you decide?",
            ["Decide deliberately and let the NAME say which — `grow` versus `scaled`",
             "Always mutate; it is faster",
             "Always return a new object",
             "It makes no difference to callers"],
            0,
            "Same principle as module 9's `sortInPlace` versus `sorted`. Silent mutation of "
            "an object a caller still holds is a hard bug to find."),
    ],
))

# --- 11.3 Constructors ------------------------------------------------------

_M11.append(_jlesson(
    "m11-ctor", "Constructors",
    "Build an object that is valid from its first instant.",
    """
Setting fields one at a time after `new` leaves a window where the object is
half-built. A **constructor** closes it:

```java
class Point {
    int x;
    int y;

    Point(int x, int y) {        // no return type, name matches the class
        this.x = x;
        this.y = y;
    }
}

Point p = new Point(3, 4);       // valid the instant it exists
```

Two things mark a constructor out: **its name is exactly the class name**, and
it has **no return type** — not even `void`. Write `void Point(...)` and you
have quietly declared an ordinary method that will never be called by `new`,
which compiles and then baffles you.

**`this.x = x;` again.** The parameters are conventionally named after the
fields, so they shadow them, so `this.` is mandatory. This is the single most
common line of Java in existence.

**The default constructor is a gift you can lose.** If you write no constructor
at all, Java supplies a no-argument one that leaves every field at its default —
that is what `new Point()` used in lesson 11.1. **The moment you declare any
constructor, that gift disappears.** So after adding `Point(int, int)`, the call
`new Point()` no longer compiles. If you want both, declare both.

**Constructors overload** by their parameter lists, exactly like methods
(module 9):

```java
Point() { this(0, 0); }              // delegates to the other one
Point(int x, int y) { this.x = x; this.y = y; }
```

`this(...)` calls another constructor **of the same class** and, if used, must
be the very first statement. It is how you avoid copy-pasting initialisation
logic between overloads — write the real work once, in the fullest constructor,
and have the others delegate to it.

Do not confuse the two uses of the word: `this.x` is *the current object's
field*; `this(0, 0)` is *another constructor*. Same keyword, unrelated jobs.

**A constructor's job is to establish what must always be true.** Once it
returns, the object should be usable — no "remember to call `init()` afterwards".
That idea gets a name in module 12: the class invariant.
""",
    warmup=[
        _jq("```java\nclass P { int x;\n    void P(int x) { this.x = x; }\n}\nP p = new P(5);\n```",
            ["Compile error — `void P` is a method, so there is no P(int) constructor",
             "It works; p.x is 5",
             "It works but p.x is 0",
             "It throws at runtime"],
            0,
            "A return type turns it into an ordinary method that merely happens to be named "
            "`P`. Constructors have no return type at all."),
        _jq("You add `Point(int x, int y)` to a class that had no constructors. What breaks?",
            ["`new Point()` — the free no-arg constructor is gone",
             "Nothing", "All existing field access", "`this.x = x` stops working"],
            0,
            "Java only supplies the default constructor when you declare none. Declare one "
            "and you own the full set."),
    ],
    exercises=[
        _je("j11-ct-basic", "Write the constructor",
            "`Point` should be constructible as `new Point(x, y)`. Replace `____` "
            "with the constructor — mind the shadowing.",
            _joop("class Point {\n"
                  "    int x;\n"
                  "    int y;\n"
                  "\n"
                  "    Point(int x, int y) {\n"
                  "        this.x = x;\n"
                  "        this.y = y;\n"
                  "    }\n"
                  "}",
                  "        Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  '        System.out.println(p.x + "," + p.y);'),
            "    Point(int x, int y) {\n"
            "        this.x = x;\n"
            "        this.y = y;\n"
            "    }",
            [_case(f"{x}\n{y}", f"{x},{y}") for (x, y) in ((3, 4), (0, 0), (-1, 8))],
            hints=["The name is exactly the class name, and there is no return type.",
                   "The parameters shadow the fields, so both assignments need `this.`.",
                   "`Point(int x, int y) { this.x = x; this.y = y; }`"]),

        _je("j11-ct-delegate", "One constructor calling another",
            "`Point()` should produce the origin by delegating to the two-argument "
            "constructor rather than repeating its work. Replace `____` with that "
            "delegation.",
            _joop("class Point {\n"
                  "    int x;\n"
                  "    int y;\n"
                  "\n"
                  "    Point() {\n"
                  "        this(0, 0);\n"
                  "    }\n"
                  "\n"
                  "    Point(int x, int y) {\n"
                  "        this.x = x;\n"
                  "        this.y = y;\n"
                  "    }\n"
                  "}",
                  "        Point o = new Point();\n"
                  "        Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  '        System.out.println(o.x + "," + o.y);\n'
                  '        System.out.println(p.x + "," + p.y);'),
            "        this(0, 0);",
            [_case(f"{x}\n{y}", _nl("0,0", f"{x},{y}"))
             for (x, y) in ((3, 4), (-5, 5), (0, 1))],
            hints=["`this(...)` calls another constructor of the same class.",
                   "The origin is (0, 0).",
                   "`this(0, 0);` — and it must be the first statement in the constructor."],
            difficulty="Medium"),

        _jfix("j11-ct-void", "It looks like a constructor",
              "This is meant to build a `Rect` from a width and a height, but it does "
              "not compile: `new Rect(w, h)` finds no matching constructor. Look "
              "closely at the declaration.",
              _joop("class Rect {\n"
                    "    int w;\n"
                    "    int h;\n"
                    "\n"
                    "    void Rect(int w, int h) {\n"
                    "        this.w = w;\n"
                    "        this.h = h;\n"
                    "    }\n"
                    "}",
                    "        Rect r = new Rect(sc.nextInt(), sc.nextInt());\n"
                    '        System.out.println(r.w * r.h);'),
              _joop("class Rect {\n"
                    "    int w;\n"
                    "    int h;\n"
                    "\n"
                    "    Rect(int w, int h) {\n"
                    "        this.w = w;\n"
                    "        this.h = h;\n"
                    "    }\n"
                    "}",
                    "        Rect r = new Rect(sc.nextInt(), sc.nextInt());\n"
                    '        System.out.println(r.w * r.h);'),
              [_case(f"{w}\n{h}", w * h) for (w, h) in ((3, 4), (5, 5), (2, 9))],
              hints=["A constructor has no return type — not even `void`.",
                     "As written, this is an ordinary method that happens to be called `Rect`.",
                     "Delete the `void`."]),

        _jch("j11-ct-both", "Two ways to build one", "Medium",
             "Give `Rect` two constructors: `Rect(int side)` for a square, and "
             "`Rect(int w, int h)` for the general case. The one-argument version "
             "must **delegate** to the two-argument one rather than repeating it. "
             "Write both where you see `____`.",
             _joop("class Rect {\n"
                   "    int w;\n"
                   "    int h;\n"
                   "\n"
                   "    Rect(int side) {\n"
                   "        this(side, side);\n"
                   "    }\n"
                   "\n"
                   "    Rect(int w, int h) {\n"
                   "        this.w = w;\n"
                   "        this.h = h;\n"
                   "    }\n"
                   "\n"
                   "    int area() {\n"
                   "        return w * h;\n"
                   "    }\n"
                   "}",
                   "        Rect sq = new Rect(sc.nextInt());\n"
                   "        Rect re = new Rect(sc.nextInt(), sc.nextInt());\n"
                   "        System.out.println(sq.area());\n"
                   "        System.out.println(re.area());"),
             "    Rect(int side) {\n"
             "        this(side, side);\n"
             "    }\n"
             "\n"
             "    Rect(int w, int h) {\n"
             "        this.w = w;\n"
             "        this.h = h;\n"
             "    }",
             [_case(f"{s}\n{w}\n{h}", _nl(s * s, w * h))
              for (s, w, h) in ((3, 4, 5), (1, 1, 1), (7, 2, 0), (10, 3, 3))],
             hints=["Two constructors, differing in parameter count — ordinary overloading.",
                    "The square one delegates: `this(side, side);`",
                    "`this(...)` has to be the FIRST statement of the constructor.",
                    "Only the two-argument version should assign the fields; write the real "
                    "work once."]),
    ],
    quiz=[
        _jq("What are the two uses of `this`, and are they related?",
            ["`this.field` is the current object; `this(...)` calls another constructor — unrelated jobs",
             "They are the same thing",
             "`this(...)` is not valid Java",
             "`this.field` only works inside constructors"],
            0,
            "Same keyword, two grammars. `this(...)` is only legal as the first statement of "
            "a constructor."),
        _jq("Why should the fullest constructor hold the real initialisation logic?",
            ["So the others delegate to it and the validation exists in exactly one place",
             "Because Java requires it",
             "Because it is faster",
             "So the class can have a default constructor"],
            0,
            "Duplicated initialisation is duplicated validation, and one copy will drift. "
            "Module 12 makes that concrete."),
    ],
))

# --- 11.4 static and final --------------------------------------------------

_M11.append(_jlesson(
    "m11-static", "`static` and `final`",
    "State that belongs to the class, and names that can only be assigned once.",
    """
**A `static` field belongs to the class — one copy, shared by every object.**

```java
class Counter {
    static int created = 0;         // ONE of these, for the whole program
    int id;                          // one per object

    Counter() {
        created++;                   // every construction bumps the shared count
        id = created;                // ...and this object remembers its number
    }
}
```

Make three `Counter`s and there are three `id` fields and exactly one `created`.
That is the whole distinction. Reach a static field through the class —
`Counter.created` — not through an instance; `c.created` compiles but reads as
though it were per-object, which is exactly the confusion to avoid.

**Static methods** you already know from module 9: no object, no `this`, no
instance fields. `Math.max`, `Arrays.sort` and `String.join` are all static
because they need no receiver.

**Static is not "the default".** Reach for it when something genuinely belongs
to the type rather than to any instance: a counter of all instances, a shared
constant, a factory method. Reaching for it to dodge "I need an object here" is
how a program ends up with global mutable state.

**`final` means "assigned exactly once".**

```java
final int limit = 10;
limit = 20;                          // compile error
```

On a **field** it means the field must be set by the time the constructor
finishes, and can never change afterwards:

```java
class Point {
    final int x;
    final int y;

    Point(int x, int y) {
        this.x = x;                  // the one and only assignment
        this.y = y;
    }
}
```

Now a `Point` can never change after construction — it is **immutable**, with
all the benefits `String` gets from the same property (safe to share, safe as a
map key, impossible to corrupt from another part of the program).

**`static final` together is a constant**, and by convention it is named in
capitals:

```java
static final int MAX_SIZE = 100;
```

One copy, never changes, reachable as `Rect.MAX_SIZE`.

**The catch worth knowing:** `final` freezes the *reference*, not the object.

```java
final int[] data = {1, 2, 3};
data[0] = 99;                        // FINE — the array's contents are not final
data = new int[5];                   // compile error — the reference is
```

Module 1's aliasing distinction, one more time: `final` protects the variable,
never what it points at. Real immutability takes more work, and module 12 does it.
""",
    warmup=[
        _jq("Three objects of a class with `static int created` and `int id`. How many of each field exist?",
            ["One `created`, three `id`s", "Three of each", "One of each",
             "Three `created`, one `id`"],
            0,
            "Static belongs to the class, instance fields belong to objects. That is the "
            "entire difference."),
        _jq("```java\nfinal int[] a = {1, 2, 3};\na[0] = 99;\n```",
            ["Compiles and works — final freezes the reference, not the contents",
             "Compile error",
             "Runtime exception",
             "Compiles but silently does nothing"],
            0,
            "`final` says the variable can never point at a different array. It says nothing "
            "about the array."),
    ],
    exercises=[
        _je("j11-st-counter", "Count every object made",
            "`Counter` should track how many instances have been created. Replace "
            "`____` with the field declaration — it has to be shared by every object, "
            "not one per object.",
            _joop("class Counter {\n"
                  "    static int created = 0;\n"
                  "\n"
                  "    Counter() {\n"
                  "        created++;\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) new Counter();\n"
                  "        System.out.println(Counter.created);"),
            "    static int created = 0;",
            [_case(n, n) for n in (3, 1, 0, 10)],
            hints=["One copy for the whole class, not one per object.",
                   "`main` reads it as `Counter.created`, through the class.",
                   "`static int created = 0;`"]),

        _je("j11-st-both", "One shared, one per object",
            "Each `Ticket` should get its own sequential number, starting at 1, "
            "from a shared counter. Replace `____` with the constructor body.",
            _joop("class Ticket {\n"
                  "    static int issued = 0;\n"
                  "    int number;\n"
                  "\n"
                  "    Ticket() {\n"
                  "        issued++;\n"
                  "        number = issued;\n"
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        Ticket last = null;\n"
                  "        for (int i = 0; i < n; i++) last = new Ticket();\n"
                  '        System.out.println(Ticket.issued + " " + last.number);'),
            "        issued++;\n"
            "        number = issued;",
            [_case(n, f"{n} {n}") for n in (3, 1, 7)],
            hints=["Bump the shared counter first, then record it in this object.",
                   "`issued` is the class's; `number` is this object's.",
                   "`issued++;` then `number = issued;`"],
            difficulty="Medium"),

        _je("j11-st-final", "A field assigned once",
            "`Point` should be immutable: its coordinates can never change after "
            "construction. Replace `____` with the two field declarations.",
            _joop("class Point {\n"
                  "    final int x;\n"
                  "    final int y;\n"
                  "\n"
                  "    Point(int x, int y) {\n"
                  "        this.x = x;\n"
                  "        this.y = y;\n"
                  "    }\n"
                  "}",
                  "        Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  '        System.out.println(p.x + "," + p.y);'),
            "    final int x;\n"
            "    final int y;",
            [_case(f"{x}\n{y}", f"{x},{y}") for (x, y) in ((3, 4), (0, 0), (-7, 2))],
            hints=["One keyword makes a field assignable exactly once.",
                   "It is still assigned — by the constructor.",
                   "`final int x;` and `final int y;`"]),

        _jfix("j11-st-instance", "The counter that always says 1",
              "`Counter.created` should report how many objects were made. It always "
              "reports 1, because the field is per-object instead of per-class.",
              _joop("class Counter {\n"
                    "    int created = 0;\n"
                    "\n"
                    "    Counter() {\n"
                    "        created++;\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        Counter last = null;\n"
                    "        for (int i = 0; i < n; i++) last = new Counter();\n"
                    "        System.out.println(last.created);"),
              _joop("class Counter {\n"
                    "    static int created = 0;\n"
                    "\n"
                    "    Counter() {\n"
                    "        created++;\n"
                    "    }\n"
                    "}",
                    "        int n = sc.nextInt();\n"
                    "        Counter last = null;\n"
                    "        for (int i = 0; i < n; i++) last = new Counter();\n"
                    "        System.out.println(last.created);"),
              [_case(n, n) for n in (3, 1, 6)],
              hints=["Each new object gets its own fresh `created`, starting at 0.",
                     "So every object increments its own copy to 1.",
                     "Make the field `static` so there is only one."]),

        _jch("j11-st-constant", "A shared constant and a clamp", "Medium",
             "Give `Box` a `static final int MAX = 100` and a constructor that "
             "**clamps** its size into `1..MAX` — anything below 1 becomes 1, "
             "anything above `MAX` becomes `MAX`. Store the result in a `final int "
             "size`. Write the field declarations and the constructor where you see "
             "`____`.",
             _joop("class Box {\n"
                   "    static final int MAX = 100;\n"
                   "    final int size;\n"
                   "\n"
                   "    Box(int size) {\n"
                   "        if (size < 1) this.size = 1;\n"
                   "        else if (size > MAX) this.size = MAX;\n"
                   "        else this.size = size;\n"
                   "    }\n"
                   "}",
                   "        Box b = new Box(sc.nextInt());\n"
                   '        System.out.println(b.size + " " + Box.MAX);'),
             "    static final int MAX = 100;\n"
             "    final int size;\n"
             "\n"
             "    Box(int size) {\n"
             "        if (size < 1) this.size = 1;\n"
             "        else if (size > MAX) this.size = MAX;\n"
             "        else this.size = size;\n"
             "    }",
             [_case(v, f"{min(100, max(1, v))} 100")
              for v in (50, 0, -5, 100, 101, 1, 1000)],
             hints=["`static final int MAX = 100;` — one copy, never changes, capitals by "
                    "convention.",
                    "`final int size;` is assigned by the constructor and never again.",
                    "A `final` field must be assigned exactly once on EVERY path, so use "
                    "if/else-if/else rather than assigning then overwriting.",
                    "The parameter shadows the field, so every assignment needs `this.size`."]),
    ],
    quiz=[
        _jq("Why is `static final int MAX = 100;` written in capitals?",
            ["Convention for a constant — one copy that never changes",
             "Java requires capitals for static fields",
             "So it can be accessed without an object",
             "To make it thread-safe"],
            0,
            "Purely convention, but a strong one: capitals tell a reader at a glance that "
            "the value is fixed at compile time."),
        _jq("A `final` field must be assigned…",
            ["exactly once, by the time every constructor finishes",
             "at its declaration only",
             "at most once, or never",
             "in a static block"],
            0,
            "Declaration or constructor, but exactly once on every path — which is why an "
            "if/else chain works and 'assign a default then overwrite' does not."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m11_rect(w, h, k):
    return _nl(
        f"area={w * h}",
        f"perimeter={2 * (w + h)}",
        f"square={_jbool(w == h)}",
        f"scaled={w * k}x{h * k}",
        f"original={w}x{h}",
        "count=2",
    )


_M11_CAP = _jcap(
    "The Rect class",
    """
One class that uses everything in module 11.

Read `w`, `h` and `k`. Build a `Rect(w, h)`, then print:

```
area=<w * h>
perimeter=<2 * (w + h)>
square=<true when w equals h, else false>
scaled=<the scaled rectangle as WxH>
original=<the ORIGINAL rectangle as WxH>
count=<how many Rect objects have been created>
```

`Rect` needs:

| Member | Kind |
|---|---|
| `w`, `h` | `final int` fields — a Rect never changes after construction |
| `count` | a `static int`, bumped by the constructor |
| `Rect(int w, int h)` | the constructor: assigns both fields and bumps `count` |
| `area()`, `perimeter()` | instance methods returning an `int` |
| `isSquare()` | an instance method returning a `boolean` |
| `scaled(int k)` | returns a **new** `Rect`, multiplying both sides by `k` |

Two things the hidden cases check:

- **`scaled` must not mutate.** The `original=` line prints the first rectangle
  after scaling, so a method that assigned to `w` or `h` would fail — and with
  `final` fields it would not even compile, which is the point of using them.
- **`count` is exactly 2.** One `Rect` from `main`, one made inside `scaled`.
  If you get 1, `scaled` is mutating instead of constructing; if you get more,
  something is building rectangles it does not need.
""",
    _jch("j11-cap-rect", "The Rect class", "Hard",
         "Write the whole `Rect` class where you see `____`. `main` is already "
         "written and uses it.",
         _joop("class Rect {\n"
               "    static int count = 0;\n"
               "    final int w;\n"
               "    final int h;\n"
               "\n"
               "    Rect(int w, int h) {\n"
               "        this.w = w;\n"
               "        this.h = h;\n"
               "        count++;\n"
               "    }\n"
               "\n"
               "    int area() {\n"
               "        return w * h;\n"
               "    }\n"
               "\n"
               "    int perimeter() {\n"
               "        return 2 * (w + h);\n"
               "    }\n"
               "\n"
               "    boolean isSquare() {\n"
               "        return w == h;\n"
               "    }\n"
               "\n"
               "    Rect scaled(int k) {\n"
               "        return new Rect(w * k, h * k);\n"
               "    }\n"
               "}",
               "        int w = sc.nextInt();\n"
               "        int h = sc.nextInt();\n"
               "        int k = sc.nextInt();\n"
               "        Rect r = new Rect(w, h);\n"
               "        Rect s = r.scaled(k);\n"
               '        System.out.println("area=" + r.area());\n'
               '        System.out.println("perimeter=" + r.perimeter());\n'
               '        System.out.println("square=" + r.isSquare());\n'
               '        System.out.println("scaled=" + s.w + "x" + s.h);\n'
               '        System.out.println("original=" + r.w + "x" + r.h);\n'
               '        System.out.println("count=" + Rect.count);'),
         "class Rect {\n"
         "    static int count = 0;\n"
         "    final int w;\n"
         "    final int h;\n"
         "\n"
         "    Rect(int w, int h) {\n"
         "        this.w = w;\n"
         "        this.h = h;\n"
         "        count++;\n"
         "    }\n"
         "\n"
         "    int area() {\n"
         "        return w * h;\n"
         "    }\n"
         "\n"
         "    int perimeter() {\n"
         "        return 2 * (w + h);\n"
         "    }\n"
         "\n"
         "    boolean isSquare() {\n"
         "        return w == h;\n"
         "    }\n"
         "\n"
         "    Rect scaled(int k) {\n"
         "        return new Rect(w * k, h * k);\n"
         "    }\n"
         "}",
         [_case(f"{w}\n{h}\n{k}", _m11_rect(w, h, k))
          for (w, h, k) in ((3, 4, 2), (5, 5, 1), (2, 7, 3), (1, 1, 10), (6, 2, 0))],
         hints=["`static int count = 0;` is shared; `final int w` and `final int h` are "
                "per-object and assigned once.",
                "The constructor assigns both fields with `this.` (the parameters shadow "
                "them) and bumps `count`.",
                "`area`, `perimeter` and `isSquare` are instance methods with no parameters "
                "— the data is already in the object.",
                "`scaled` returns `new Rect(w * k, h * k)`, which also bumps `count` to 2. "
                "That is why the expected count is 2, not 1.",
                "Do not try to assign `w` or `h` outside the constructor; `final` will stop "
                "you, which is exactly what it is for."]),
    example_io="stdin:  3\n        4\n        2\n\n"
               "stdout: area=12\n        perimeter=14\n        square=false\n"
               "        scaled=6x8\n        original=3x4\n        count=2",
    rubric=[
        "`w` and `h` are `final`, so the class cannot be mutated after construction.",
        "`count` is `static`, so it counts across all objects rather than per object.",
        "The constructor uses `this.` for both assignments and bumps the counter.",
        "`scaled` builds and returns a new `Rect` — the `original=` line is unchanged.",
        "`count` prints 2: the original plus the one `scaled` created.",
        "All six lines print, in order, with no spaces around `=`.",
    ],
)


_MODULES.append(_jmod(
    11, 4, "Object-oriented programming",
    "Classes and objects",
    "Define your own types: fields, instance methods, `this`, constructors, and the "
    "difference between what belongs to an object and what belongs to the class.",
    """
Part 4 begins. Everything so far has used types Java gave you; from here you
define your own — which is what Java is actually for, and the section interviews
probe hardest.

Three ideas carry the module. A **class** is a type, an **object** is one value
of it, and a **reference** is a variable pointing at one — and that last
distinction is module 1's aliasing lesson arriving for the third time, now
general to every type you will write. A **constructor** exists so an object is
valid from its first instant rather than after you remember to fill it in. And
**static** marks the things that belong to the type rather than to any instance.

`this.x = x` shows up in almost every exercise here. It is not ceremony — it is
module 9's shadowing bug appearing exactly where the convention of naming
parameters after fields guarantees it.
""",
    _M11,
    capstone=_M11_CAP,
    objectives=[
        "Declare a class with fields, create objects with `new`, and reach fields with a dot.",
        "Explain class vs object vs reference, and predict `==` and aliasing for your own types.",
        "Write instance methods that use their object's fields, and say why `static` ones cannot.",
        "Use `this` for shadowed fields and `this(...)` to delegate between constructors.",
        "Say what the default constructor is and when declaring one takes it away.",
        "Choose between `static` and instance members, and use `final` for once-only assignment.",
        "Build an array of objects, and remember every slot needs its own `new`.",
    ],
    why="Every Java codebase you will ever open is classes and objects. It is also the "
        "section that unlocks the rest of the roadmap: collections hold objects, "
        "generics abstract over them, and Spring is objects wired together.",
    est_minutes=300,
    glossary=[
        _jg("class", "A type you define, bundling fields and the methods that operate on them."),
        _jg("object", "One value of a class, living on the heap. Also called an instance."),
        _jg("instance variable", "A field declared without `static` — one copy per object."),
        _jg("reference", "A variable holding an object's address. Copying it aliases; it does "
                         "not copy the object."),
        _jg("new", "Allocates an object, runs a constructor, and returns a reference to it."),
        _jg("instance method", "A method called on an object, with that object's fields in "
                               "scope and available as `this`."),
        _jg("this", "The object the current instance method or constructor was invoked on. "
                    "Required when a parameter shadows a field."),
        _jg("constructor", "A member with the class's name and no return type, run by `new` "
                           "to make the object valid."),
        _jg("default constructor", "The free no-argument constructor Java supplies only when "
                                   "you declare none of your own."),
        _jg("this(...)", "A call to another constructor of the same class. Must be the first "
                         "statement."),
        _jg("static member", "A field or method belonging to the class — one copy, no `this`, "
                             "reached through the class name."),
        _jg("final", "Assignable exactly once. On a reference it freezes the variable, never "
                     "the object it points at."),
    ],
    cheatsheet="""
```java
// --- declare a type -----------------------------------------------------
class Point {
    static int created = 0;          // ONE copy, for the whole class
    final int x;                     // one per object, assigned exactly once
    final int y;

    Point() { this(0, 0); }          // delegates; must be the FIRST statement
    Point(int x, int y) {            // name = class name, NO return type
        this.x = x;                  // this. required: parameter shadows field
        this.y = y;
        created++;
    }

    int lengthSquared() {            // instance method: fields are in scope
        return x * x + y * y;
    }
    Point movedBy(int dx, int dy) {  // returns a NEW object; leaves this one alone
        return new Point(x + dx, y + dy);
    }
}

// --- use it -------------------------------------------------------------
Point p = new Point(3, 4);
p.x                                  // field access
p.lengthSquared()                    // instance method
Point.created                        // static member, through the CLASS

Point q = p;                         // ALIAS — one object, two names
p == q                               // true (same object)
p == new Point(3, 4)                 // false (different object, same values)

// --- arrays of objects --------------------------------------------------
Point[] ps = new Point[3];           // three NULL slots
for (int i = 0; i < 3; i++) ps[i] = new Point();   // each needs its own new

// --- traps --------------------------------------------------------------
void Point(int x) { }                // a METHOD named Point, not a constructor
void setX(int x) { x = x; }          // assigns the parameter to itself
final int[] a = {1,2}; a[0] = 9;     // legal: final freezes the variable only
```
""",
    self_check=[
        "Can you say precisely what `new Point(3, 4)` allocates and what the variable holds?",
        "Can you predict `==` for two objects with identical field values?",
        "Do you know why `this.x = x;` appears in nearly every constructor?",
        "Can you explain why a `static` method cannot read an instance field?",
        "Can you say what happens to the default constructor when you declare one of your own?",
        "Can you explain why `final int[] a` still allows `a[0] = 9`?",
        "Would you remember that `new Point[3]` creates zero Point objects?",
    ],
    review=[
        _jq("```java\nPoint[] ps = new Point[2];\nps[0].x = 1;\n```",
            ["NullPointerException — the slots are null until you assign objects",
             "Works; ps[0].x is 1",
             "Compile error",
             "ArrayIndexOutOfBoundsException"],
            0,
            "The array exists; the Points do not. `ps[0] = new Point();` first. This is the "
            "most common object-array mistake."),
        _jq("A class declares `Rect(int w, int h)` and nothing else. Which call compiles?",
            ["new Rect(2, 3)", "new Rect()", "both", "neither"],
            0,
            "Declaring any constructor removes the free no-argument one. Add `Rect() { this(1, 1); }` "
            "if you want both."),
        _jq("`static int created` versus `int id`, after creating four objects:",
            ["one `created` shared by all four, and four separate `id`s",
             "four of each", "one of each", "four `created`, one `id`"],
            0,
            "Static belongs to the class; instance fields belong to instances. Reach the "
            "static one through the class name to keep that visible."),
        _jq("Why does the capstone's `count` come out as 2 rather than 1?",
            ["`scaled` constructs a second Rect, and the constructor bumps the counter",
             "The counter starts at 1",
             "`main` creates two rectangles explicitly",
             "Because count is not static"],
            0,
            "Every `new` runs the constructor. If your `scaled` mutated instead of "
            "constructing, the count would be 1 — which is how the test catches it."),
    ],
    milestone="You can define your own types, give them behaviour and constructors, and "
              "reason about objects and references as confidently as you already do about "
              "arrays.",
))
