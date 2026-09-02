# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 14 - Abstraction, interfaces and composition.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# The close of Part 4, and the module where the course finally argues about
# DESIGN rather than mechanism. Modules 11-13 answered "how do I build a class
# hierarchy"; this one answers "should I", and gives the two tools that usually
# turn out to be the better answer - an interface (a contract with no state)
# and a field (composition).
#
# `abstract `, `interface ` and `implements ` are reserved for module 14 by the
# scope linter in java_course.py, so this is the first module allowed to use
# them. Collections stay banned course-wide, so an interface here is always
# implemented by a named class, never by a lambda - Part 8 owns lambdas.
# ---------------------------------------------------------------------------

_M14 = []


def _m14t(src):
    """Trim a triple-quoted Java block to exactly what `_joop` expects: no
    leading newline, no trailing newline. Spelled out rather than reusing `_jp`
    because a `blank=` argument has to match the solution text byte for byte."""
    return src.strip("\n")


# ===========================================================================
# Python mirrors - design rule 2: expected outputs are computed, never typed.
# ===========================================================================

def _m14_accounts(rows):
    """rows: (kind, owner, balance). kind 1 = Basic (flat 2), 2 = Premium (1%)."""
    out = []
    total = 0
    for (kind, owner, balance) in rows:
        fee = 2 if kind == 1 else _jdiv(balance, 100)
        out.append(f"{owner} {balance} fee={fee} net={balance - fee}")
        total += balance - fee
    out.append(f"total={total}")
    return _nl(*out)


def _m14_acct_case(rows):
    lines = [str(len(rows))] + [f"{k} {o} {b}" for (k, o, b) in rows]
    return _case("\n".join(lines), _m14_accounts(rows))


# --- 14.1 abstract classes --------------------------------------------------

_M14.append(_jlesson(
    "m14-abstract", "Abstract classes and abstract methods",
    "A class that exists only to be extended, and a method that exists only to be overridden.",
    """
Module 13 left `Shape` in an awkward spot. It had an `area()` that returned `0`,
which is not the area of anything — it was a placeholder standing in for "every
shape has an area, but a shape *in general* does not know how to compute one".

**`abstract` says that out loud.**

```java
abstract class Shape {
    abstract int area();          // no body, and a semicolon instead of braces

    String describe() {           // an ordinary method — and it may call area()
        return "area=" + area();
    }
}
```

Two new things:

**An abstract method has no body.** It is a signature and a semicolon. It is a
demand: *every concrete subclass must supply this*.

**An abstract class cannot be instantiated.**

```java
Shape s = new Shape();     // does not compile: Shape is abstract
Shape s = new Rect(3, 4);  // fine — a Rect is a Shape
```

That is the whole point. `new Shape()` was never a sensible thing to write, and
`abstract` upgrades it from "meaningless at run time" to "rejected at compile
time".

**The rules, in full:**

- A class with even one abstract method **must** be declared `abstract`.
- An abstract class may have **no** abstract methods at all. That is legal, and
  occasionally what you want: it just means "do not instantiate this directly".
- An abstract class has constructors, fields and ordinary methods like any other
  class. Its constructor still runs — via `super(...)` — when a subclass is
  built. It is never instantiated alone, but it is always *constructed* as part
  of the subclass.
- A subclass that does not implement every inherited abstract method must itself
  be `abstract`. The demand is simply passed further down the chain.

**The pattern that makes all of this worth the keyword** is already above:
`describe()` is written once, in the abstract class, in terms of a method that
does not exist yet. Every subclass gets `describe()` free and supplies only the
one piece that genuinely varies. That shape has a name — the **template
method** — and it is the main reason to reach for an abstract class rather than
an interface.

```java
abstract class Employee {
    protected final String name;

    Employee(String name) { this.name = name; }

    abstract int pay();                                   // varies

    String slip() { return name + " earns " + pay(); }    // fixed, forever
}
```

`slip()` is written once and is correct for every kind of employee that will
ever exist, including the ones somebody adds years from now.
""",
    warmup=[
        _jq("What does `new Shape()` do when `Shape` is declared `abstract`?",
            ["It does not compile",
             "It compiles and returns null",
             "It compiles and throws at run time",
             "It compiles and gives a Shape with default fields"],
            0,
            "That is exactly what `abstract` buys you: a meaningless call is rejected "
            "before the program ever runs."),
        _jq("A class inherits an abstract method and does not implement it. What must be true?",
            ["That class must itself be declared abstract",
             "Nothing — the method is skipped",
             "The method returns 0 by default",
             "The parent must drop the `abstract` keyword"],
            0,
            "The demand is passed down until some class finally satisfies it. Only that "
            "class can be instantiated."),
    ],
    exercises=[
        _je("j14-ex-abstract-decl", "Declare it abstract",
            "`Shape` has an `area()` with no body, so `Shape` cannot be an ordinary "
            "class. Replace `____` with its declaration.",
            _joop(_m14t("""
abstract class Shape {
    abstract int area();

    String describe() {
        return "area=" + area();
    }
}

class Rect extends Shape {
    private final int w;
    private final int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    @Override
    int area() {
        return w * h;
    }
}
"""),
                  _m14t("""
        int w = sc.nextInt();
        int h = sc.nextInt();
        Shape s = new Rect(w, h);
        System.out.println(s.describe());
""")),
            "abstract class Shape {",
            [_case(f"{w} {h}", f"area={w * h}")
             for (w, h) in ((3, 4), (1, 1), (12, 0), (7, 9))],
            hints=["One keyword goes in front of `class`.",
                   "It is the same keyword that is already sitting on `area()`.",
                   "`abstract class Shape {`"],
            difficulty="Intro"),

        _je("j14-ex-abstract-method", "Demand it from every subclass",
            "Every `Employee` is paid, but there is no way to compute pay for an employee "
            "in general — `Hourly` and `Salaried` each do it differently. Replace `____` "
            "with the declaration that demands the method without supplying it.",
            _joop(_m14t("""
abstract class Employee {
    protected final String name;

    Employee(String name) {
        this.name = name;
    }

    abstract int pay();

    String slip() {
        return name + " earns " + pay();
    }
}

class Hourly extends Employee {
    private final int rate;
    private final int hours;

    Hourly(String name, int rate, int hours) {
        super(name);
        this.rate = rate;
        this.hours = hours;
    }

    @Override
    int pay() {
        return rate * hours;
    }
}

class Salaried extends Employee {
    private final int annual;

    Salaried(String name, int annual) {
        super(name);
        this.annual = annual;
    }

    @Override
    int pay() {
        return annual / 12;
    }
}
"""),
                  _m14t("""
        int kind = sc.nextInt();
        String name = sc.next();
        Employee e;
        if (kind == 1) {
            int rate = sc.nextInt();
            int hours = sc.nextInt();
            e = new Hourly(name, rate, hours);
        } else {
            int annual = sc.nextInt();
            e = new Salaried(name, annual);
        }
        System.out.println(e.slip());
""")),
            "    abstract int pay();",
            [_case("1 Ann 20 38", f"Ann earns {20 * 38}"),
             _case("2 Bob 60000", f"Bob earns {_jdiv(60000, 12)}"),
             _case("1 Cy 15 0", "Cy earns 0"),
             _case("2 Di 1000", f"Di earns {_jdiv(1000, 12)}")],
            hints=["An abstract method is a signature with no body.",
                   "It ends in a semicolon where an ordinary method would open a brace.",
                   "`abstract int pay();`"],
            difficulty="Easy"),

        _jfix("j14-ex-abstract-fix", "The method that never got implemented",
              "`Square` says `@Override` and looks like it implements `cost()`, but the "
              "compiler disagrees. Read the signature it inherited, then read the one it "
              "actually wrote.",
              _joop(_m14t("""
abstract class Tile {
    abstract int cost();

    String bill() {
        return "cost=" + cost();
    }
}

class Square extends Tile {
    private final int side;

    Square(int side) {
        this.side = side;
    }

    @Override
    int cost(int side) {
        return side * side;
    }
}
"""),
                    _m14t("""
        int side = sc.nextInt();
        Tile t = new Square(side);
        System.out.println(t.bill());
""")),
              _joop(_m14t("""
abstract class Tile {
    abstract int cost();

    String bill() {
        return "cost=" + cost();
    }
}

class Square extends Tile {
    private final int side;

    Square(int side) {
        this.side = side;
    }

    @Override
    int cost() {
        return side * side;
    }
}
"""),
                    _m14t("""
        int side = sc.nextInt();
        Tile t = new Square(side);
        System.out.println(t.bill());
""")),
              [_case(str(s), f"cost={s * s}") for s in (5, 1, 0, 13)],
              hints=["`cost(int side)` and `cost()` are different methods — the first is an "
                     "overload, not an override.",
                     "So `Square` still carries an unimplemented abstract method, which is "
                     "why it cannot be a concrete class.",
                     "`@Override` is what turned a silent design bug into a clear compile "
                     "error. Without it the failure would be far more confusing.",
                     "Drop the parameter and read the field instead: `int cost() { return "
                     "side * side; }`."],
              difficulty="Medium"),

        _jch("j14-ex-abstract-template", "Write only the varying half", "Medium",
             "`Account` already knows how to print a summary — it just does not know what "
             "a fee is. Write the two subclasses where you see `____`. `Basic` charges a "
             "flat fee of `2`; `Premium` charges one percent of the balance "
             "(`balance / 100`). Neither one writes its own `summary()`.",
             _joop(_m14t("""
abstract class Account {
    protected final String owner;
    protected final int balance;

    Account(String owner, int balance) {
        this.owner = owner;
        this.balance = balance;
    }

    abstract int fee();

    String summary() {
        return owner + " " + balance + " fee=" + fee() + " net=" + (balance - fee());
    }
}

class Basic extends Account {
    Basic(String owner, int balance) {
        super(owner, balance);
    }

    @Override
    int fee() {
        return 2;
    }
}

class Premium extends Account {
    Premium(String owner, int balance) {
        super(owner, balance);
    }

    @Override
    int fee() {
        return balance / 100;
    }
}
"""),
                   _m14t("""
        int n = sc.nextInt();
        int total = 0;
        for (int i = 0; i < n; i++) {
            int kind = sc.nextInt();
            String owner = sc.next();
            int balance = sc.nextInt();
            Account a;
            if (kind == 1) {
                a = new Basic(owner, balance);
            } else {
                a = new Premium(owner, balance);
            }
            System.out.println(a.summary());
            total += balance - a.fee();
        }
        System.out.println("total=" + total);
""")),
             _m14t("""
class Basic extends Account {
    Basic(String owner, int balance) {
        super(owner, balance);
    }

    @Override
    int fee() {
        return 2;
    }
}

class Premium extends Account {
    Premium(String owner, int balance) {
        super(owner, balance);
    }

    @Override
    int fee() {
        return balance / 100;
    }
}
"""),
             [_m14_acct_case(rows) for rows in (
                 [(1, "Ann", 500), (2, "Bob", 900)],
                 [(2, "Cy", 12345)],
                 [(1, "Di", 0), (1, "Eve", 7), (2, "Fay", 99)],
                 [(2, "Gus", 100), (2, "Hal", 250), (1, "Ivy", 1000)],
             )],
             hints=["Each subclass needs a constructor that passes both values up with "
                    "`super(owner, balance)` — constructors are never inherited.",
                    "`balance` is `protected` on `Account`, so `Premium` can read it "
                    "directly.",
                    "Neither subclass declares `summary()`. That is the entire point: it "
                    "was written once, in terms of a method that did not exist yet.",
                    "`Basic.fee()` returns `2`; `Premium.fee()` returns `balance / 100`, "
                    "which is integer division and so truncates."]),
    ],
    quiz=[
        _jq("Why can an abstract class still declare a constructor?",
            ["Because a subclass calls it with `super(...)` to build the inherited part",
             "It cannot — abstract classes have no constructors",
             "Only if it declares no abstract methods",
             "So that `new` works on it after all"],
            0,
            "It is never instantiated on its own, but every subclass object contains its "
            "fields, and those have to be initialised."),
        _jq("What is the template method pattern, in one sentence?",
            ["A concrete method in the parent, written in terms of an abstract method the subclasses supply",
             "A method that returns a template string",
             "Any method marked `final`",
             "A constructor that calls another constructor"],
            0,
            "`slip()` and `describe()` in this lesson. The fixed part is written once; only "
            "the step that genuinely varies is delegated downwards."),
    ],
))


# --- 14.2 interfaces --------------------------------------------------------

_M14.append(_jlesson(
    "m14-interface", "Interfaces and `implements`",
    "A contract with no state, no constructor and no implementation — and why that is a feature.",
    """
An abstract class still *is* a class: it has fields, a constructor, and it uses
up your one `extends` slot. An **interface** gives up all of that in exchange
for one thing — a class may implement as many as it likes.

```java
interface Greeter {
    String greet(String name);      // no body, and no `abstract` needed
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Good morning, " + name;
    }
}
```

**Everything in an interface is implicitly public.** `String greet(String name);`
is short for `public abstract String greet(String name);` — the keywords are
allowed but nobody writes them. This has a consequence that bites everyone once:

```java
class Polite implements Greeter {
    @Override
    String greet(String name) { ... }     // does NOT compile
}
```

> error: attempting to assign weaker access privileges; was public

The interface method is public, and module 13's rule still holds — an override
may widen access but never narrow it. **Implementing methods must be declared
`public`.**

**An interface is a type.** That is what you actually buy:

```java
Greeter g = new Polite();                          // the interface is the type
Greeter[] all = { new Polite(), new Loud() };      // unrelated classes, one array
for (Greeter x : all) System.out.println(x.greet("Ada"));
```

`Polite` and `Loud` need no common superclass, no shared fields, nothing —
only the promise that they can greet. Code written against `Greeter` works with
implementations that did not exist when it was written. That is the phrase
"program to an interface, not an implementation", and it is the single most
useful sentence in object-oriented design.

**What an interface cannot have:** instance fields, a constructor, or any
per-object state. A field declared in an interface is implicitly
`public static final` — a constant, shared by everyone, not an instance field:

```java
interface Limits {
    int MAX = 100;      // really: public static final int MAX = 100;
}
```

**`implements` versus `extends`:** a class `extends` exactly one class and
`implements` any number of interfaces. Both may appear, in that order:

```java
class Loud extends Speaker implements Greeter, Comparable { ... }
```

**The is-a test still applies,** in its "can-do" form. `implements Greeter`
claims *this thing can greet*. If the sentence sounds wrong, the interface is
wrong.
""",
    warmup=[
        _jq("Why does `String greet(String n)` fail to compile inside a class that implements `Greeter`?",
            ["The interface method is implicitly public, and an override may not narrow access",
             "Interfaces cannot declare methods that return String",
             "It needs the `abstract` keyword",
             "`greet` is a reserved name"],
            0,
            "Everything in an interface is public. The implementing method must say "
            "`public` out loud."),
        _jq("What does `int MAX = 100;` inside an interface actually declare?",
            ["A public static final constant",
             "A private instance field",
             "A field every implementing class gets its own copy of",
             "Nothing — interfaces cannot contain fields"],
            0,
            "Interfaces hold no per-object state. A field there is a shared constant, which "
            "is why the convention is to name it in capitals."),
    ],
    exercises=[
        _je("j14-ex-iface-decl", "Declare the contract",
            "`Polite` promises to greet. Replace `____` with the declaration of the "
            "contract it is promising to fulfil.",
            _joop(_m14t("""
interface Greeter {
    String greet(String name);
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Good morning, " + name;
    }
}
"""),
                  _m14t("""
        String name = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(name));
""")),
            "interface Greeter {",
            [_case(n, f"Good morning, {n}") for n in ("Ada", "Bo", "Zed", "x")],
            hints=["It is not a class — it is the other kind of type.",
                   "One keyword, then the name, then the brace.",
                   "`interface Greeter {`"],
            difficulty="Intro"),

        _je("j14-ex-implements", "Sign the contract",
            "`Loud` greets differently, but it makes the same promise. Replace `____` "
            "with its declaration so it can sit in a `Greeter[]` beside `Polite`.",
            _joop(_m14t("""
interface Greeter {
    String greet(String name);
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Good morning, " + name;
    }
}

class Loud implements Greeter {
    @Override
    public String greet(String name) {
        return "HEY " + name.toUpperCase();
    }
}
"""),
                  _m14t("""
        String name = sc.next();
        Greeter[] all = { new Polite(), new Loud() };
        for (Greeter g : all) {
            System.out.println(g.greet(name));
        }
""")),
            "class Loud implements Greeter {",
            [_case(n, _nl(f"Good morning, {n}", f"HEY {n.upper()}"))
             for n in ("Ada", "bo", "Zed")],
            hints=["A class does not `extend` an interface.",
                   "The keyword claims the class can do what the interface describes.",
                   "`class Loud implements Greeter {`"],
            difficulty="Intro"),

        _jfix("j14-ex-iface-fix", "Weaker access privileges",
              "This will not compile, and the compiler's wording is worth learning by "
              "heart: *attempting to assign weaker access privileges; was public*. Find "
              "the one missing keyword.",
              _joop(_m14t("""
interface Greeter {
    String greet(String name);
}

class Polite implements Greeter {
    @Override
    String greet(String name) {
        return "Good morning, " + name;
    }
}
"""),
                    _m14t("""
        String name = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(name));
""")),
              _joop(_m14t("""
interface Greeter {
    String greet(String name);
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Good morning, " + name;
    }
}
"""),
                    _m14t("""
        String name = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(name));
""")),
              [_case(n, f"Good morning, {n}") for n in ("Ada", "Bo", "Zed")],
              hints=["The interface does not say `public`, but it means it — every "
                     "interface method is implicitly public.",
                     "Module 13's rule: an override may widen access, never narrow it.",
                     "Writing no modifier at all is package-private, which is narrower "
                     "than public.",
                     "`public String greet(String name) {`"],
              difficulty="Easy"),

        _jch("j14-ex-iface-param", "Program to the interface", "Medium",
             "`Form` runs a set of rules over a string and counts how many it passes. "
             "Write it where you see `____`. It must be written against `Validator` and "
             "must never mention `NotEmpty`, `MaxLen` or `Digits` — that is what lets a "
             "fourth rule be added tomorrow without touching it.\n\n"
             "`Form` takes a `Validator[]` in its constructor and exposes "
             "`int passes(String s)` returning how many of the rules accept `s`.",
             _joop(_m14t("""
interface Validator {
    boolean ok(String s);
}

class NotEmpty implements Validator {
    @Override
    public boolean ok(String s) {
        return s.length() > 0;
    }
}

class MaxLen implements Validator {
    private final int max;

    MaxLen(int max) {
        this.max = max;
    }

    @Override
    public boolean ok(String s) {
        return s.length() <= max;
    }
}

class Digits implements Validator {
    @Override
    public boolean ok(String s) {
        for (int i = 0; i < s.length(); i++) {
            if (!Character.isDigit(s.charAt(i))) {
                return false;
            }
        }
        return true;
    }
}

class Form {
    private final Validator[] rules;

    Form(Validator[] rules) {
        this.rules = rules;
    }

    int passes(String s) {
        int k = 0;
        for (Validator v : rules) {
            if (v.ok(s)) {
                k++;
            }
        }
        return k;
    }
}
"""),
                   _m14t("""
        int max = sc.nextInt();
        String s = sc.next();
        Validator[] rules = { new NotEmpty(), new MaxLen(max), new Digits() };
        Form f = new Form(rules);
        System.out.println("passes=" + f.passes(s));
""")),
             _m14t("""
class Form {
    private final Validator[] rules;

    Form(Validator[] rules) {
        this.rules = rules;
    }

    int passes(String s) {
        int k = 0;
        for (Validator v : rules) {
            if (v.ok(s)) {
                k++;
            }
        }
        return k;
    }
}
"""),
             [_case(f"{mx} {s}",
                    "passes=" + str((1 if len(s) > 0 else 0)
                                    + (1 if len(s) <= mx else 0)
                                    + (1 if s.isdigit() else 0)))
              for (mx, s) in ((4, "12345"), (6, "12345"), (3, "abc"), (2, "9"), (1, "ab7"))],
             hints=["The field is `private final Validator[] rules;` — store what you are "
                    "handed.",
                    "`passes` is an enhanced `for` over `rules`, counting the ones whose "
                    "`ok(s)` is true.",
                    "The loop variable's type is `Validator`. If you ever write "
                    "`if (v instanceof MaxLen)` in here, the design has failed.",
                    "`int k = 0; for (Validator v : rules) if (v.ok(s)) k++; return k;`"]),
    ],
    quiz=[
        _jq("A class may extend ___ class(es) and implement ___ interface(s).",
            ["one; any number", "any number; one", "one; one", "any number; any number"],
            0,
            "Single inheritance of state, multiple inheritance of type. That asymmetry is "
            "the whole reason interfaces exist."),
        _jq("What is the practical payoff of `Greeter g = new Polite();`?",
            ["Code written against Greeter also works with implementations that did not exist yet",
             "It is faster than using the concrete type",
             "It lets Polite have more fields",
             "It avoids writing @Override"],
            0,
            "Program to the interface, not the implementation. The array loop in this "
            "lesson never changes when a fifth Greeter is added."),
    ],
))


# --- 14.3 multiple interfaces, default and static ---------------------------

_M14.append(_jlesson(
    "m14-default", "Multiple interfaces, `default` and `static` methods",
    "Several contracts at once — and the two ways an interface may ship real code.",
    """
**A class may implement several interfaces**, separated by commas:

```java
interface Walker { String walk(); }
interface Talker { String talk(); }

class Robot implements Walker, Talker {
    @Override public String walk() { return "clank"; }
    @Override public String talk() { return "beep"; }
}
```

A `Robot` is now usable anywhere a `Walker` is wanted *and* anywhere a `Talker`
is wanted. No diamond problem arises, because interfaces carry no state — there
are no competing fields to inherit, only signatures, and two identical
signatures merge harmlessly into one.

Interfaces may also extend each other, and an interface may extend several:

```java
interface Robotic extends Walker, Talker { }
```

## `default` methods

Originally an interface could contain nothing but signatures. That made
interfaces impossible to evolve: adding one method to a published interface
broke every class that implemented it, everywhere in the world. Java 8 fixed
that with **default methods** — an interface method that ships a body.

```java
interface Greeter {
    String greet(String name);                 // still abstract

    default String greetTwice(String name) {   // has a body
        return greet(name) + " " + greet(name);
    }
}
```

Implementors get `greetTwice` free and need change nothing. Any implementor may
still override it:

```java
class Terse implements Greeter {
    @Override public String greet(String name) { return name; }
    @Override public String greetTwice(String name) { return name + name; }
}
```

Notice what a default method may and may not do. It **can** call the
interface's own abstract methods — `greetTwice` calls `greet` without knowing
who implements it. It **cannot** touch instance state, because an interface has
none.

> **Interfaces still cannot hold state.** A default method is behaviour, not a
> field. The moment your "interface" wants a field, it wanted to be an abstract
> class.

## `static` interface methods

An interface may also carry `static` helpers. They belong to the interface, not
to any implementor, and are called through the interface name:

```java
interface Money {
    int cents();

    static String format(int cents) {
        return cents / 100 + "." + (cents % 100 < 10 ? "0" : "") + cents % 100;
    }
}

Money.format(425);      // "4.25" — called on the interface itself
```

Static interface methods are **not inherited**. `new Price(1).format(...)` does
not compile, and neither does `Price.format(...)`. They exist so a utility that
obviously belongs to a contract can live with it, instead of in a separate
`MoneyUtils` class off to one side.

| | abstract method | `default` method | `static` method |
|---|---|---|---|
| Has a body | no | yes | yes |
| Implementor must supply it | yes | no | no |
| Can be overridden | must be | may be | never |
| Called through | the object | the object | the interface name |
""",
    warmup=[
        _jq("Why does implementing two interfaces not cause the diamond problem?",
            ["Interfaces carry no state, so there are no competing fields — identical signatures merge",
             "Java picks the first one listed",
             "It does cause it, and the class will not compile",
             "The compiler renames one of the methods"],
            0,
            "The diamond problem is about inheriting the same *field* twice. Interfaces "
            "have none, so the question never arises."),
        _jq("Why were `default` methods added to Java?",
            ["So an interface can gain a method without breaking every existing implementor",
             "To let interfaces hold fields",
             "To make interfaces faster",
             "To replace abstract classes entirely"],
            0,
            "Before Java 8, adding one method to a published interface broke every class "
            "implementing it. A default body makes the addition backwards compatible."),
    ],
    exercises=[
        _je("j14-ex-multi", "Two contracts at once",
            "A `Robot` both walks and talks. Replace `____` with its declaration.",
            _joop(_m14t("""
interface Walker {
    String walk();
}

interface Talker {
    String talk();
}

class Robot implements Walker, Talker {
    private final String id;

    Robot(String id) {
        this.id = id;
    }

    @Override
    public String walk() {
        return id + " walks";
    }

    @Override
    public String talk() {
        return id + " says hello";
    }
}
"""),
                  _m14t("""
        String id = sc.next();
        Robot r = new Robot(id);
        Walker w = r;
        Talker t = r;
        System.out.println(w.walk());
        System.out.println(t.talk());
""")),
            "class Robot implements Walker, Talker {",
            [_case(i, _nl(f"{i} walks", f"{i} says hello")) for i in ("R2", "unit-7", "z")],
            hints=["One `implements` keyword covers both.",
                   "Separate the interface names with a comma.",
                   "`class Robot implements Walker, Talker {`"],
            difficulty="Easy"),

        _je("j14-ex-default", "An interface method with a body",
            "`greetTwice` should be shipped by the interface itself, so every implementor "
            "gets it free. Replace `____` with its declaration line.",
            _joop(_m14t("""
interface Greeter {
    String greet(String name);

    default String greetTwice(String name) {
        return greet(name) + " " + greet(name);
    }
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Hi " + name;
    }
}
"""),
                  _m14t("""
        String name = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(name));
        System.out.println(g.greetTwice(name));
""")),
            "    default String greetTwice(String name) {",
            [_case(n, _nl(f"Hi {n}", f"Hi {n} Hi {n}")) for n in ("Ada", "Bo", "Zed")],
            hints=["An interface method with a body needs one extra keyword.",
                   "It is not `static` — implementors should be able to override it.",
                   "`default String greetTwice(String name) {`"],
            difficulty="Easy"),

        _jch("j14-ex-default-override", "Take the default, or replace it", "Medium",
             "`Polite` is happy with the inherited `greetTwice`. `Terse` is not — it wants "
             "`greetTwice(\"Ada\")` to be `AdaAda`, with no separating space. Write "
             "`Terse` where you see `____`: its `greet` returns the name unchanged, and it "
             "overrides `greetTwice` to join the two copies directly.",
             _joop(_m14t("""
interface Greeter {
    String greet(String name);

    default String greetTwice(String name) {
        return greet(name) + " " + greet(name);
    }
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Hi " + name;
    }
}

class Terse implements Greeter {
    @Override
    public String greet(String name) {
        return name;
    }

    @Override
    public String greetTwice(String name) {
        return name + name;
    }
}
"""),
                   _m14t("""
        String name = sc.next();
        Greeter[] all = { new Polite(), new Terse() };
        for (Greeter g : all) {
            System.out.println(g.greetTwice(name));
        }
""")),
             _m14t("""
class Terse implements Greeter {
    @Override
    public String greet(String name) {
        return name;
    }

    @Override
    public String greetTwice(String name) {
        return name + name;
    }
}
"""),
             [_case(n, _nl(f"Hi {n} Hi {n}", n + n)) for n in ("Ada", "Bo", "Zed")],
             hints=["`Terse implements Greeter` — it is not related to `Polite` at all.",
                    "Both methods must be `public`, since both come from the interface.",
                    "Overriding a default method looks exactly like overriding an inherited "
                    "one, `@Override` included.",
                    "`public String greetTwice(String name) { return name + name; }`"]),

        _je("j14-ex-static-iface", "A utility that belongs to the contract",
             "Formatting cents as pounds-and-pence has nothing to do with any one `Money` "
             "object, but it belongs beside the contract rather than in a separate utility "
             "class. Replace `____` with the declaration that puts it on the interface "
             "itself, callable as `Money.format(...)`.",
             _joop(_m14t("""
interface Money {
    int cents();

    static String format(int cents) {
        int whole = cents / 100;
        int rest = cents % 100;
        if (rest < 10) {
            return whole + ".0" + rest;
        }
        return whole + "." + rest;
    }
}

class Price implements Money {
    private final int cents;

    Price(int cents) {
        this.cents = cents;
    }

    @Override
    public int cents() {
        return cents;
    }
}
"""),
                   _m14t("""
        int a = sc.nextInt();
        int b = sc.nextInt();
        Money x = new Price(a);
        Money y = new Price(b);
        System.out.println(Money.format(x.cents() + y.cents()));
""")),
             "    static String format(int cents) {",
             [_case(f"{a} {b}", f"{(a + b) // 100}.{(a + b) % 100:02d}")
              for (a, b) in ((150, 275), (100, 5), (0, 0), (999, 1), (7, 8))],
             hints=["It is called on the interface name, not on an object.",
                    "That is the same keyword you would use for a helper beside `main`.",
                    "`static String format(int cents) {`"],
             difficulty="Medium"),
    ],
    quiz=[
        _jq("Which is true of a `static` interface method?",
            ["It is not inherited — only `Money.format(...)` works, not `Price.format(...)`",
             "Implementors must override it",
             "It can read instance fields",
             "It is the same thing as a default method"],
            0,
            "Static members belong to the type that declares them. Interfaces deliberately "
            "do not pass theirs down."),
        _jq("A default method needs to remember a value between calls. What does that tell you?",
            ["You wanted an abstract class — interfaces hold no state",
             "Add a private field to the interface",
             "Make the method static instead",
             "Use a second interface"],
            0,
            "The moment a contract needs per-object memory it is no longer a contract. "
            "That is the sharpest line between an interface and an abstract class."),
    ],
))


# --- 14.4 choosing, and final -----------------------------------------------

_M14.append(_jlesson(
    "m14-choose", "Abstract class or interface — and `final`",
    "Picking between the two, combining them, and the keyword that says *stop here*.",
    """
## The comparison, in full

| | abstract class | interface |
|---|---|---|
| Instance fields | yes | **no** (only `public static final` constants) |
| Constructor | yes | no |
| How many per class | **one** (`extends`) | any number (`implements`) |
| Method bodies | any method | only `default` and `static` |
| Access modifiers on members | any | everything is public |
| Models | *is-a-kind-of* | *can-do* |

**The deciding question is state.** If the types share *data* — a `name`, a
`balance`, a half-built object that every subclass needs — you want an abstract
class, because only a class can hold a field and only a constructor can
initialise it. If they share only *capability*, you want an interface.

**The second question is how many.** A class gets one `extends` and spends it
forever. `Comparable`, `Runnable`, `AutoCloseable` are all interfaces precisely
because any class at all might need to be one, whatever it already extends.

## Using both together

The two are not rivals — the standard library pairs them constantly:
`Collection` is the interface, `AbstractCollection` the skeleton that implements
the boring half.

```java
interface Codec {
    String encode(String s);
    String decode(String s);
}

abstract class SymmetricCodec implements Codec {
    @Override
    public String decode(String s) {
        return encode(s);          // true for every symmetric codec
    }
}

class Rot13 extends SymmetricCodec {
    @Override public String encode(String s) { ... }    // decode() free
}
```

The interface is the type everyone else programs against. The abstract class is
a convenience for implementors: it fills in whatever can be written once, and
leaves the rest abstract. An implementor with its own ideas can skip the
skeleton and implement `Codec` directly — nothing is forced.

## `final`

You have used `final` on fields since module 11: assign once, never again.
It has two more jobs.

**A `final` method cannot be overridden.**

```java
class Rounder {
    final int round(int cents) { return (cents + 50) / 100 * 100; }
}
```

That is a guarantee, not an optimisation. Every subclass, present and future,
rounds the same way — so any other method that relies on that rule stays
correct. Note the asymmetry with `abstract`: `abstract` means *you must
override this*, `final` means *you may not*.

**A `final` class cannot be extended.**

```java
final class Config { ... }
```

`String` is final. So are `Integer` and every other wrapper. A class that
promises immutability essentially has to be final, because a subclass could add
a mutable field and break the promise for everyone holding a `String`-typed
reference.

**When to use it.** `final` is a design statement: *this behaviour is part of
the contract, not a suggestion.* The counter-argument is that it forecloses
extensions you did not think of. The usual working rule is to make a class final
when it is immutable or when subclassing it would break an invariant, and to
leave the rest open.

> `final` also cannot be combined with `abstract`. One says "you must override
> this", the other "you may not" — the compiler rejects the pair outright.
""",
    warmup=[
        _jq("Two unrelated classes need to share a `name` field and its constructor logic. Which tool?",
            ["An abstract class — only a class can hold an instance field",
             "An interface with a `name` field",
             "An interface with a default method",
             "A static interface method"],
            0,
            "Shared *state* means abstract class. Shared *capability* means interface. "
            "Interfaces cannot hold per-object data at all."),
        _jq("Why is `String` declared `final`?",
            ["A subclass could add mutable state and break immutability for every String reference",
             "For faster compilation",
             "Because it implements an interface",
             "So it can be used as a HashMap key"],
            0,
            "An immutable class that can be subclassed is not really immutable — anyone "
            "holding a `String` reference could be handed a mutable impostor."),
    ],
    exercises=[
        _jch("j14-ex-skeleton", "The interface and its skeleton", "Medium",
             "`Rot13` and `Flip` are both symmetric — encoding twice gives back the "
             "original — so `decode` is the same line of code for both. Write the abstract "
             "skeleton class where you see `____`: it implements `Codec`, supplies "
             "`decode` once, and leaves `encode` abstract for its subclasses.",
             _joop(_m14t("""
interface Codec {
    String encode(String s);

    String decode(String s);
}

abstract class SymmetricCodec implements Codec {
    @Override
    public String decode(String s) {
        return encode(s);
    }
}

class Rot13 extends SymmetricCodec {
    @Override
    public String encode(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c >= 'a' && c <= 'z') {
                sb.append((char) ('a' + (c - 'a' + 13) % 26));
            } else if (c >= 'A' && c <= 'Z') {
                sb.append((char) ('A' + (c - 'A' + 13) % 26));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
}

class Flip extends SymmetricCodec {
    @Override
    public String encode(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}
"""),
                   _m14t("""
        String which = sc.next();
        String word = sc.next();
        Codec c;
        if (which.equals("rot13")) {
            c = new Rot13();
        } else {
            c = new Flip();
        }
        String enc = c.encode(word);
        System.out.println(enc);
        System.out.println(c.decode(enc));
""")),
             _m14t("""
abstract class SymmetricCodec implements Codec {
    @Override
    public String decode(String s) {
        return encode(s);
    }
}
"""),
             [_case(f"{which} {word}", _nl(enc, word))
              for (which, word, enc) in (
                  ("rot13", "Hello", "Uryyb"),
                  ("rot13", "abc-123", "nop-123"),
                  ("flip", "abcd", "dcba"),
                  ("flip", "racecar", "racecar"),
                  ("rot13", "Zz", "Mm"))],
             hints=["It must be `abstract`, because it never implements `encode`.",
                    "It `implements Codec` — the subclasses then `extend` it.",
                    "`decode` must be `public`, since it comes from the interface.",
                    "A symmetric codec undoes itself: `public String decode(String s) "
                    "{ return encode(s); }`."]),

        _je("j14-ex-final-class", "Close the class",
            "`Config` promises that a retry count, once validated, never changes. A "
            "subclass could break that promise for everyone holding a `Config`. Replace "
            "`____` with a declaration that makes subclassing impossible.",
            _joop(_m14t("""
final class Config {
    private final int retries;

    Config(int retries) {
        if (retries < 0) {
            this.retries = 0;
        } else {
            this.retries = retries;
        }
    }

    int retries() {
        return retries;
    }
}
"""),
                  _m14t("""
        int n = sc.nextInt();
        Config c = new Config(n);
        System.out.println("retries=" + c.retries());
""")),
            "final class Config {",
            [_case(str(n), f"retries={max(n, 0)}") for n in (3, 0, -7, 100)],
            hints=["The same keyword you already put on fields, used on the class instead.",
                   "It goes in front of `class`.",
                   "`final class Config {`"],
            difficulty="Intro"),

        _jfix("j14-ex-final-fix", "Overriding what was sealed",
              "`Rounder.round` is `final` on purpose: every price in the system rounds to "
              "the nearest 100 the same way. `LoggingRounder` tried to override it anyway "
              "and the file no longer compiles. Remove the override — `describe` should "
              "use the guaranteed rounding.",
              _joop(_m14t("""
class Rounder {
    final int round(int cents) {
        return (cents + 50) / 100 * 100;
    }
}

class LoggingRounder extends Rounder {
    @Override
    int round(int cents) {
        return cents;
    }

    String describe(int cents) {
        return cents + " becomes " + round(cents);
    }
}
"""),
                    _m14t("""
        int cents = sc.nextInt();
        LoggingRounder r = new LoggingRounder();
        System.out.println(r.describe(cents));
""")),
              _joop(_m14t("""
class Rounder {
    final int round(int cents) {
        return (cents + 50) / 100 * 100;
    }
}

class LoggingRounder extends Rounder {
    String describe(int cents) {
        return cents + " becomes " + round(cents);
    }
}
"""),
                    _m14t("""
        int cents = sc.nextInt();
        LoggingRounder r = new LoggingRounder();
        System.out.println(r.describe(cents));
""")),
              [_case(str(c), f"{c} becomes {(c + 50) // 100 * 100}")
               for c in (149, 150, 0, 99, 1249)],
              hints=["`final` on a method means no subclass may replace it, ever.",
                     "`LoggingRounder` does not need its own rounding — it needs the "
                     "parent's.",
                     "Delete the whole `round` override, `@Override` line included.",
                     "`describe` still calls `round(cents)`; it now reaches the inherited, "
                     "final version."],
              difficulty="Easy"),

        _jch("j14-ex-unrelated", "One capability, no common parent", "Medium",
             "An invoice and a ticket have nothing in common — no shared fields, no "
             "sensible superclass, and inventing a `Document` base class to hold them "
             "would be a lie. What they share is that each can render itself as one line. "
             "Write both classes where you see `____`.\n\n"
             "`Invoice(String customer, int amount)` renders "
             "`INVOICE <customer> <amount>`; `Ticket(String event, int seat)` renders "
             "`TICKET <event> seat <seat>`.",
             _joop(_m14t("""
interface Printable {
    String line();
}

class Invoice implements Printable {
    private final String customer;
    private final int amount;

    Invoice(String customer, int amount) {
        this.customer = customer;
        this.amount = amount;
    }

    @Override
    public String line() {
        return "INVOICE " + customer + " " + amount;
    }
}

class Ticket implements Printable {
    private final String event;
    private final int seat;

    Ticket(String event, int seat) {
        this.event = event;
        this.seat = seat;
    }

    @Override
    public String line() {
        return "TICKET " + event + " seat " + seat;
    }
}
"""),
                   _m14t("""
        int n = sc.nextInt();
        Printable[] items = new Printable[n];
        for (int i = 0; i < n; i++) {
            int kind = sc.nextInt();
            String label = sc.next();
            int num = sc.nextInt();
            if (kind == 1) {
                items[i] = new Invoice(label, num);
            } else {
                items[i] = new Ticket(label, num);
            }
        }
        for (Printable p : items) {
            System.out.println(p.line());
        }
""")),
             _m14t("""
class Invoice implements Printable {
    private final String customer;
    private final int amount;

    Invoice(String customer, int amount) {
        this.customer = customer;
        this.amount = amount;
    }

    @Override
    public String line() {
        return "INVOICE " + customer + " " + amount;
    }
}

class Ticket implements Printable {
    private final String event;
    private final int seat;

    Ticket(String event, int seat) {
        this.event = event;
        this.seat = seat;
    }

    @Override
    public String line() {
        return "TICKET " + event + " seat " + seat;
    }
}
"""),
             [_case("\n".join([str(len(rows))]
                              + [f"{k} {lab} {num}" for (k, lab, num) in rows]),
                    _nl(*[(f"INVOICE {lab} {num}" if k == 1 else f"TICKET {lab} seat {num}")
                          for (k, lab, num) in rows]))
              for rows in ([(1, "Ada", 250), (2, "Opera", 14)],
                           [(2, "Cup-Final", 1)],
                           [(1, "Bo", 0), (1, "Cy", 99), (2, "Gig", 300)],
                           [(2, "a", 7), (2, "b", 8), (1, "c", 9)])],
             hints=["Neither class extends anything — `implements Printable` is the whole "
                    "relationship.",
                    "Each stores its own two fields as `private final` and takes them in "
                    "its constructor.",
                    "`line()` must be `public` in both, because interface methods are.",
                    "Watch the exact wording: `INVOICE <customer> <amount>` and "
                    "`TICKET <event> seat <seat>`."]),
    ],
    quiz=[
        _jq("Why can a method not be both `abstract` and `final`?",
            ["`abstract` means you must override it; `final` means you may not",
             "It can be, but only in an interface",
             "Because abstract methods have no body",
             "Because final methods are static"],
            0,
            "The two are direct contradictions, so the compiler rejects the combination "
            "rather than picking a winner."),
        _jq("`AbstractCollection` implements `Collection`. Why ship both?",
            ["The interface is the type everyone programs against; the skeleton is an optional convenience for implementors",
             "The interface is deprecated",
             "Java requires an abstract class for every interface",
             "The abstract class is faster"],
            0,
            "Callers depend on the interface; implementors may take the skeleton's free "
            "methods or ignore it and implement the interface directly."),
    ],
))


# --- 14.5 composition -------------------------------------------------------

_M14.append(_jlesson(
    "m14-compose", "Composition over inheritance",
    "The has-a relationship, delegation, and why a field usually beats `extends`.",
    """
Module 13 gave you `extends` and the is-a test. This lesson is the other half of
that sentence: **when is-a fails, use a field.**

```java
class Car extends Engine { }             // a Car IS an Engine? No.

class Car {
    private final Engine engine;         // a Car HAS an Engine. Yes.
}
```

That is **composition**: an object built out of other objects, held in fields.
It is the default. `extends` is the special case.

## Delegation

A composed object usually forwards some work to the thing it holds. That
forwarding is called **delegation**, and it is nearly always a one-line method:

```java
class Logger {
    private final Clock clock;

    Logger(Clock clock) { this.clock = clock; }

    String log(String message) {
        return "[" + clock.stamp() + "] " + message;    // delegate the timestamp
    }
}
```

`Logger` does not become a `Clock`, does not inherit a `Clock`'s other methods,
and does not break when `Clock` gains one. It uses exactly the piece it needs.

## Why composition usually wins

**1. Inheritance is not selective.** `extends` takes *everything* — every public
method, sensible or not. The textbook disaster is `class Stack extends
ArrayList`: your stack now has `add(int index, E e)`, so anyone can insert at
the bottom of a stack, and the class cannot stop them. A stack that *has* an
array can expose `push` and `pop` and nothing else.

**2. The fragile base class problem.** A superclass you did not write can change
in its next version — a method starts calling another method, and your override
is suddenly invoked twice. Composition depends only on the public methods you
actually call.

**3. You get one `extends`, and it is spent forever.** You may hold as many
fields as you like.

**4. Composition can change at run time.** A field can be reassigned to a
different implementation; a superclass is fixed the moment the object is
created.

**5. It composes with interfaces beautifully.** Hold a field typed as an
*interface*, and the held object can be swapped for any implementation — the
same "program to an interface" move as lesson 14.2, now applied to a field.

## The vocabulary

- **Composition** — the part does not make sense without the whole, and is
  usually created by it. A `Car` builds its own `Engine`.
- **Aggregation** — the whole holds parts that live independently and may be
  shared. A `Team` holds `Player`s who exist before and after the team.
- **Association** — the loosest: two objects simply know about each other. A
  `Doctor` and a `Patient`.

The distinction matters when you ask who is responsible for creating and
destroying the part. In Java the code looks the same — a field — so the honest
summary is: **prefer a field; reach for `extends` only when the is-a test passes
and you genuinely want the whole interface of the parent.**

> The rule is not "never inherit". Overriding is exactly right when the subtype
> really is a specialisation and you want polymorphism, which is why the shape
> hierarchy in module 13 was not a mistake. The rule is that inheritance should
> be a decision, not a reflex.
""",
    warmup=[
        _jq("What is actually wrong with `class Stack extends ArrayList`?",
            ["The stack inherits every list method, so callers can insert at the bottom and the class cannot stop them",
             "ArrayList is final",
             "It is slower than composition",
             "Nothing — it is the standard way to write a stack"],
            0,
            "Inheritance is all-or-nothing. A stack that *holds* an array exposes only "
            "`push` and `pop`."),
        _jq("A class needs one method from another class. Which is the safer reach?",
            ["A field holding that object, and a one-line method that forwards to it",
             "`extends`, so the method is inherited",
             "Copy the method's body",
             "Make the method static"],
            0,
            "Delegation takes exactly the piece you need and nothing else, and survives the "
            "other class gaining methods later."),
    ],
    exercises=[
        _je("j14-ex-hasa", "A Car has an Engine",
            "A `Car` is not an `Engine` — it has one. Replace `____` with the field that "
            "says so.",
            _joop(_m14t("""
class Engine {
    private final int hp;

    Engine(int hp) {
        this.hp = hp;
    }

    int hp() {
        return hp;
    }
}

class Car {
    private final String model;
    private final Engine engine;

    Car(String model, int hp) {
        this.model = model;
        this.engine = new Engine(hp);
    }

    String spec() {
        return model + " " + engine.hp() + "hp";
    }
}
"""),
                  _m14t("""
        String model = sc.next();
        int hp = sc.nextInt();
        Car c = new Car(model, hp);
        System.out.println(c.spec());
""")),
            "    private final Engine engine;",
            [_case(f"{m} {hp}", f"{m} {hp}hp")
             for (m, hp) in (("Mini", 90), ("Truck", 420), ("z", 0))],
            hints=["The constructor already assigns `this.engine`, so the field just needs "
                   "declaring.",
                   "Its type is the class it holds; keep it `private final` like `model`.",
                   "`private final Engine engine;`"],
            difficulty="Intro"),

        _je("j14-ex-delegate", "Delegate the piece you need",
            "`Logger` does not know how to format a time, and should not learn — it holds "
            "a `Clock` that already does. Replace `____` with the body of `log`, which "
            "must produce `[<stamp>] <message>`.",
            _joop(_m14t("""
class Clock {
    private final int hour;
    private final int minute;

    Clock(int hour, int minute) {
        this.hour = hour;
        this.minute = minute;
    }

    String stamp() {
        if (minute < 10) {
            return hour + ":0" + minute;
        }
        return hour + ":" + minute;
    }
}

class Logger {
    private final Clock clock;

    Logger(int hour, int minute) {
        this.clock = new Clock(hour, minute);
    }

    String log(String message) {
        return "[" + clock.stamp() + "] " + message;
    }
}
"""),
                  _m14t("""
        int hour = sc.nextInt();
        int minute = sc.nextInt();
        String message = sc.next();
        Logger l = new Logger(hour, minute);
        System.out.println(l.log(message));
""")),
            '        return "[" + clock.stamp() + "] " + message;',
            [_case(f"{h} {m} {msg}", f"[{h}:{m:02d}] {msg}")
             for (h, m, msg) in ((9, 5, "boot"), (14, 30, "ready"), (0, 0, "start"),
                                 (23, 59, "halt"))],
            hints=["`Logger` never formats the time itself — it asks the `Clock`.",
                   "The method it wants is `stamp()`, called on the field.",
                   'Square brackets, then a space, then the message: `"[" + clock.stamp() '
                   '+ "] " + message`.'],
            difficulty="Easy"),

        _jfix("j14-ex-refactor", "A Playlist is not a Song",
              "This compiles, runs, and prints `seconds=0` for every playlist. `Playlist "
              "extends Song`, so it inherited a `seconds()` that reports its own — "
              "meaningless — length of `0` rather than the total of its tracks. Refactor "
              "`Playlist` to *hold* songs instead of *being* one, and give it a `seconds()` "
              "that adds them up.",
              _joop(_m14t("""
class Song {
    private final String title;
    private final int seconds;

    Song(String title, int seconds) {
        this.title = title;
        this.seconds = seconds;
    }

    String title() {
        return title;
    }

    int seconds() {
        return seconds;
    }
}

class Playlist extends Song {
    private final Song[] songs;

    Playlist(Song[] songs) {
        super("playlist", 0);
        this.songs = songs;
    }
}
"""),
                    _m14t("""
        int n = sc.nextInt();
        Song[] songs = new Song[n];
        for (int i = 0; i < n; i++) {
            String title = sc.next();
            int secs = sc.nextInt();
            songs[i] = new Song(title, secs);
        }
        Playlist p = new Playlist(songs);
        System.out.println("tracks=" + n);
        System.out.println("seconds=" + p.seconds());
""")),
              _joop(_m14t("""
class Song {
    private final String title;
    private final int seconds;

    Song(String title, int seconds) {
        this.title = title;
        this.seconds = seconds;
    }

    String title() {
        return title;
    }

    int seconds() {
        return seconds;
    }
}

class Playlist {
    private final Song[] songs;

    Playlist(Song[] songs) {
        this.songs = songs;
    }

    int seconds() {
        int total = 0;
        for (Song s : songs) {
            total += s.seconds();
        }
        return total;
    }
}
"""),
                    _m14t("""
        int n = sc.nextInt();
        Song[] songs = new Song[n];
        for (int i = 0; i < n; i++) {
            String title = sc.next();
            int secs = sc.nextInt();
            songs[i] = new Song(title, secs);
        }
        Playlist p = new Playlist(songs);
        System.out.println("tracks=" + n);
        System.out.println("seconds=" + p.seconds());
""")),
              [_case("\n".join([str(len(rows))] + [f"{t} {s}" for (t, s) in rows]),
                     _nl(f"tracks={len(rows)}", f"seconds={sum(s for (_t, s) in rows)}"))
               for rows in ([("Alpha", 210), ("Beta", 185)],
                            [("Solo", 300)],
                            [("a", 1), ("b", 2), ("c", 3), ("d", 4)],
                            [("x", 0), ("y", 999)])],
              hints=["Say it out loud: a playlist is *not* a song. The is-a test fails, so "
                     "`extends` is the wrong tool.",
                     "Delete `extends Song` — and with it the `super(\"playlist\", 0)` call "
                     "that was only ever there to satisfy the compiler.",
                     "Keep the `Song[] songs` field. That was always the real relationship.",
                     "Add `int seconds()` to `Playlist` that loops the array adding "
                     "`s.seconds()`."],
              difficulty="Medium"),

        _jch("j14-ex-team", "A Team has Players", "Medium",
             "Write the `Team` class where you see `____`. It holds a name and a "
             "`Player[]`, and reports on them without being one:\n\n"
             "- `int total()` — the sum of every player's score\n"
             "- `String best()` — the name of the highest scorer; on a tie, the one that "
             "appears first\n"
             "- `toString()` — `<team> total=<total> best=<best>`",
             _joop(_m14t("""
class Player {
    private final String name;
    private final int score;

    Player(String name, int score) {
        this.name = name;
        this.score = score;
    }

    String name() {
        return name;
    }

    int score() {
        return score;
    }
}

class Team {
    private final String name;
    private final Player[] players;

    Team(String name, Player[] players) {
        this.name = name;
        this.players = players;
    }

    int total() {
        int t = 0;
        for (Player p : players) {
            t += p.score();
        }
        return t;
    }

    String best() {
        Player top = players[0];
        for (Player p : players) {
            if (p.score() > top.score()) {
                top = p;
            }
        }
        return top.name();
    }

    @Override
    public String toString() {
        return name + " total=" + total() + " best=" + best();
    }
}
"""),
                   _m14t("""
        String teamName = sc.next();
        int n = sc.nextInt();
        Player[] players = new Player[n];
        for (int i = 0; i < n; i++) {
            String name = sc.next();
            int score = sc.nextInt();
            players[i] = new Player(name, score);
        }
        Team team = new Team(teamName, players);
        System.out.println(team);
""")),
             _m14t("""
class Team {
    private final String name;
    private final Player[] players;

    Team(String name, Player[] players) {
        this.name = name;
        this.players = players;
    }

    int total() {
        int t = 0;
        for (Player p : players) {
            t += p.score();
        }
        return t;
    }

    String best() {
        Player top = players[0];
        for (Player p : players) {
            if (p.score() > top.score()) {
                top = p;
            }
        }
        return top.name();
    }

    @Override
    public String toString() {
        return name + " total=" + total() + " best=" + best();
    }
}
"""),
             [_case("\n".join([f"{team} {len(rows)}"] + [f"{n} {s}" for (n, s) in rows]),
                    f"{team} total={sum(s for (_n, s) in rows)} "
                    f"best={max(rows, key=lambda r: r[1])[0]}")
              for (team, rows) in (("Reds", [("Ada", 12), ("Bo", 30), ("Cy", 7)]),
                                   ("Blues", [("Solo", 5)]),
                                   ("Ties", [("First", 9), ("Second", 9)]),
                                   ("Zeros", [("a", 0), ("b", 0), ("c", 0)]))],
             hints=["`Team` extends nothing. Two `private final` fields, and a constructor "
                    "that stores what it is handed.",
                    "`total()` is an enhanced `for` over `players` accumulating "
                    "`p.score()`.",
                    "`best()` is the running-maximum pattern from module 1, over objects: "
                    "start at `players[0]`, keep a `Player top`.",
                    "Use a strict `>` in the comparison so a tie keeps the earlier player.",
                    "`toString()` must be `public` — it overrides `Object`'s — and "
                    "`System.out.println(team)` then calls it for you."]),
    ],
    quiz=[
        _jq("Composition can do one thing inheritance cannot. Which?",
            ["Swap the held object for a different implementation at run time",
             "Reuse code",
             "Call a method on another object",
             "Be used with interfaces"],
            0,
            "A field can be reassigned; a superclass is fixed when the object is created."),
        _jq("`Team` holds `Player`s who exist independently of it. What is that called?",
            ["Aggregation", "Composition proper", "Inheritance", "Association only"],
            0,
            "Composition proper implies the part is owned and created by the whole, as a "
            "Car creates its Engine. Players outlive the team."),
    ],
))


# ===========================================================================
# Capstone — every idea in Part 4 in one file.
# ===========================================================================

def _m14_draw(dev):
    """dev: [kind, name, watts, on]. A heater keeps a 5 W thermostat standby."""
    (kind, _name, watts, on) = dev
    if on:
        return watts
    return 5 if kind == "heater" else 0


def _m14_total(devs):
    return sum(_m14_draw(d) for d in devs)


def _m14_room(devices, ops):
    """Mirror of the Room the learner writes. `peak` starts at the total draw of
    the freshly built room (every device off) and is re-checked after each state
    change, exactly as the Java constructor and `record()` do."""
    devs = [[kind, name, watts, False] for (kind, name, watts) in devices]
    peak = _m14_total(devs)
    out = []
    for op in ops:
        if op[0] == "draw":
            out.append(f"draw={_m14_total(devs)}")
            continue
        target = None
        for d in devs:
            if d[1] == op[1]:
                target = d
                break
        target[3] = op[0] == "on"
        state = "on" if target[3] else "off"
        out.append(f"{target[1]} {state} {_m14_draw(target)}")
        peak = max(peak, _m14_total(devs))
    out.append(f"peak={peak}")
    return _nl(*out)


def _m14_case(devices, ops):
    lines = [str(len(devices))]
    lines += [f"{kind} {name} {watts}" for (kind, name, watts) in devices]
    lines.append(str(len(ops)))
    lines += [" ".join(op) for op in ops]
    return _case("\n".join(lines), _m14_room(devices, ops))


_M14_CAP_TYPES = _m14t("""
interface Switchable {
    void turnOn();

    void turnOff();

    boolean isOn();

    default String state() {
        return isOn() ? "on" : "off";
    }
}

abstract class Device implements Switchable {
    private final String name;
    private boolean on;

    Device(String name) {
        this.name = name;
    }

    String name() {
        return name;
    }

    @Override
    public void turnOn() {
        on = true;
    }

    @Override
    public void turnOff() {
        on = false;
    }

    @Override
    public boolean isOn() {
        return on;
    }

    abstract int draw();

    @Override
    public String toString() {
        return name + " " + state() + " " + draw();
    }
}

class Lamp extends Device {
    private final int watts;

    Lamp(String name, int watts) {
        super(name);
        this.watts = watts;
    }

    @Override
    int draw() {
        return isOn() ? watts : 0;
    }
}

class Heater extends Device {
    private final int watts;

    Heater(String name, int watts) {
        super(name);
        this.watts = watts;
    }

    @Override
    int draw() {
        return isOn() ? watts : 5;
    }
}

final class Room {
    private final Device[] devices;
    private int peak;

    Room(Device[] devices) {
        this.devices = devices;
        this.peak = totalDraw();
    }

    int totalDraw() {
        int total = 0;
        for (Device d : devices) {
            total += d.draw();
        }
        return total;
    }

    String turnOn(String name) {
        Device d = find(name);
        d.turnOn();
        record();
        return d.toString();
    }

    String turnOff(String name) {
        Device d = find(name);
        d.turnOff();
        record();
        return d.toString();
    }

    int peak() {
        return peak;
    }

    private Device find(String name) {
        for (Device d : devices) {
            if (d.name().equals(name)) {
                return d;
            }
        }
        return null;
    }

    private void record() {
        int total = totalDraw();
        if (total > peak) {
            peak = total;
        }
    }
}
""")

_M14_CAP_BODY = _m14t("""
        int n = sc.nextInt();
        Device[] devices = new Device[n];
        for (int i = 0; i < n; i++) {
            String kind = sc.next();
            String name = sc.next();
            int watts = sc.nextInt();
            if (kind.equals("heater")) {
                devices[i] = new Heater(name, watts);
            } else {
                devices[i] = new Lamp(name, watts);
            }
        }
        Room room = new Room(devices);
        int q = sc.nextInt();
        for (int i = 0; i < q; i++) {
            String op = sc.next();
            if (op.equals("on")) {
                System.out.println(room.turnOn(sc.next()));
            } else if (op.equals("off")) {
                System.out.println(room.turnOff(sc.next()));
            } else {
                System.out.println("draw=" + room.totalDraw());
            }
        }
        System.out.println("peak=" + room.peak());
""")


_M14_CAP = _jcap(
    "Smart room",
    """
Five classes, one file, and every idea in Part 4 doing real work: an
**interface** with a `default` method, an **abstract class** that implements it,
two **subclasses** that differ by one method, and a **`final` class** that owns
the whole thing by composition rather than inheritance.

`main` is already written. Write the types above it.

## Input

```
n
<kind> <name> <watts>        × n        kind is `lamp` or `heater`
q
<op>                         × q        `on <name>` | `off <name>` | `draw`
```

Every device starts **off**.

## Output

- `on <name>` and `off <name>` flip that device and print it: `<name> <state> <draw>`
- `draw` prints `draw=<the room's total current draw>`
- after the last operation, one final line: `peak=<the highest total draw the room has ever been at>`

## The types

| Type | What it is |
|---|---|
| `Switchable` | **interface**: `void turnOn()`, `void turnOff()`, `boolean isOn()`, plus a **`default String state()`** returning `"on"` or `"off"` |
| `Device` | **abstract class implementing `Switchable`**: holds `name` and a private `boolean on`, implements all three interface methods, exposes `String name()`, declares **`abstract int draw()`**, and overrides `toString()` as `<name> <state()> <draw()>` |
| `Lamp extends Device` | `draw()` is its watts when on, `0` when off |
| `Heater extends Device` | `draw()` is its watts when on, **`5` when off** — the thermostat never fully sleeps |
| `Room` | **`final class`**: holds a `Device[]` and an `int peak`; `totalDraw()`, `turnOn(name)`, `turnOff(name)`, `peak()` |

## What the hidden cases are checking

- **`state()` is written once, in the interface.** Neither `Lamp` nor `Heater`
  nor `Device` should contain `"on"` or `"off"` as a literal — `toString()`
  calls `state()`, and the default method calls `isOn()` back. That round trip
  is the point of a default method.
- **`draw()` is abstract, not a field.** The only difference between a lamp and
  a heater is one overridden method. Everything else — the name, the on/off
  flag, `toString()` — is written once in `Device`.
- **`Room` is composition, not inheritance.** A room is not a device, and it
  does not extend one. It holds an array and delegates. It is `final` because
  a subclass could otherwise break the peak bookkeeping.
- **`peak` starts at the total draw of the brand-new room, not at `0`.** A room
  with two heaters begins at `10`, and a `draw` command that never turns
  anything on must still report `peak=10`. Set it in the constructor, then
  re-check after every change.
""",
    _jch("j14-cap-room", "Smart room", "Hard",
         "Write the five types where you see `____`: the `Switchable` interface, the "
         "abstract `Device`, `Lamp`, `Heater`, and the final `Room`. `main` is already "
         "written — it reads the devices, builds the `Room`, runs the operations and "
         "prints the peak.",
         _joop(_M14_CAP_TYPES, _M14_CAP_BODY),
         _M14_CAP_TYPES,
         [_m14_case(devices, ops) for (devices, ops) in (
             ([("lamp", "desk", 60), ("heater", "rad", 1500)],
              [("on", "desk"), ("draw",), ("on", "rad"), ("draw",),
               ("off", "rad"), ("draw",)]),
             ([("lamp", "a", 10)],
              [("draw",), ("on", "a"), ("off", "a"), ("draw",)]),
             ([("heater", "h1", 800), ("heater", "h2", 900)],
              [("draw",)]),
             ([("heater", "big", 2000), ("lamp", "small", 5)],
              [("on", "big"), ("off", "big"), ("on", "small")]),
             ([("lamp", "x", 40), ("lamp", "y", 40), ("heater", "z", 100)],
              [("on", "x"), ("on", "y"), ("on", "z"), ("off", "x"), ("draw",)]),
         )],
         hints=["Start with `Switchable`. Three signatures ending in semicolons, then "
                "`default String state() { return isOn() ? \"on\" : \"off\"; }`.",
                "`abstract class Device implements Switchable` holds `private final String "
                "name` and `private boolean on`. The three interface methods it implements "
                "must all be `public`.",
                "`Device` declares `abstract int draw();` and nothing else about power — "
                "then `toString()` is `name + \" \" + state() + \" \" + draw()`, written "
                "once for both subclasses.",
                "`Lamp` and `Heater` differ by exactly one method. Each stores its watts "
                "and passes the name up with `super(name)`.",
                "`Heater.draw()` returns `5` when off, not `0`. That is why a room of "
                "heaters has a non-zero draw before anything is switched on.",
                "`Room` is `final`, holds `Device[] devices` and `int peak`, and sets "
                "`peak = totalDraw()` in its constructor.",
                "Give `Room` a `private Device find(String name)` that scans the array "
                "comparing `d.name().equals(name)`, and a `private void record()` that "
                "raises `peak` if the new total is higher.",
                "`turnOn`/`turnOff` find the device, flip it, call `record()`, and return "
                "`d.toString()` — `main` prints what you return."]),
    example_io="stdin:  2\n        lamp desk 60\n        heater rad 1500\n        6\n"
               "        on desk\n        draw\n        on rad\n        draw\n"
               "        off rad\n        draw\n\n"
               "stdout: desk on 60\n        draw=65\n        rad on 1500\n"
               "        draw=1560\n        rad off 5\n        draw=65\n        peak=1560",
    rubric=[
        "`state()` is a `default` method on `Switchable` and is the only place the strings "
        "`\"on\"` and `\"off\"` appear.",
        "`Device` is abstract, implements `Switchable`, and declares `abstract int draw()`.",
        "`toString()` is written once in `Device`, not repeated in each subclass.",
        "`Lamp` and `Heater` differ by exactly one overridden method.",
        "`Heater` draws 5 W when off, so a fresh room of heaters has a non-zero total.",
        "`Room` holds a `Device[]` by composition and does not extend `Device`.",
        "`Room` is declared `final`, and `find`/`record` are `private`.",
        "`peak` is seeded from the constructor, so a run with no `on` still reports the "
        "standby total.",
    ],
    stretch=None,
)


_MODULES.append(_jmod(
    14, 4, "Object-oriented programming",
    "Abstraction, interfaces and composition",
    "Say what a type must do without saying how, let one class satisfy several contracts "
    "at once, seal what must not change — and learn why a field usually beats `extends`.",
    """
Part 4 closes on design rather than mechanism.

Modules 11-13 built the machinery: classes, encapsulation, inheritance,
overriding. This module adds the two tools that turn out to be the right answer
more often than `extends` does, and then argues the case.

**`abstract`** finally lets a base class say *I do not know how to do this, and
neither does anything general enough to be me* — instead of returning a
placeholder `0` and hoping. Paired with a concrete method written in terms of
that gap, it produces the template method: the fixed part written once, the
varying step delegated down.

**Interfaces** give up state and constructors, and get something no class can
have — a type you may hold as many of as you like. That is why `Comparable`,
`Runnable` and `AutoCloseable` are interfaces: any class at all might need to
be one, whatever it already extends. `default` methods then let a published
interface grow without breaking every implementor, which is the whole reason
Java 8 introduced them.

**Composition** is the module's real argument. `extends` takes everything,
selectively takes nothing, and is spent the moment you use it. A field takes
exactly the piece you need, can be swapped at run time, and does not break when
somebody else's base class changes underneath you. Inheritance should be a
decision, not a reflex.

`final` is the counterweight to all of it — the way to say a behaviour is part
of the contract rather than a suggestion.
""",
    _M14,
    capstone=_M14_CAP,
    objectives=[
        "Declare an abstract class and an abstract method, and say what each rules out.",
        "Write a template method: a concrete method in terms of an abstract one.",
        "Declare an interface, implement it, and say why implementing methods must be `public`.",
        "Hold an object by its interface type, and write code that never names an implementation.",
        "Implement several interfaces at once, and explain why no diamond problem arises.",
        "Write `default` and `static` interface methods, and say what each is for.",
        "Choose between an abstract class and an interface from whether the types share state.",
        "Use `final` on a method and on a class, and justify each as a design statement.",
        "Refactor a wrong `extends` into a field, and delegate to it.",
    ],
    why="This is where Java stops being syntax and becomes design. Interviews ask "
        "'abstract class or interface?' constantly, and the answer they are listening for "
        "is about state and about how many you get. 'Favour composition over inheritance' "
        "is the most-quoted sentence in object-oriented design, and this module is where "
        "you can defend it with a refactor rather than a slogan.",
    est_minutes=360,
    glossary=[
        _jg("abstract method", "A signature with no body, ending in a semicolon. Every "
                               "concrete subclass must implement it."),
        _jg("abstract class", "A class that cannot be instantiated. May hold fields, a "
                              "constructor and ordinary methods, and may declare abstract ones."),
        _jg("template method", "A concrete method in a base class written in terms of an "
                               "abstract one — the fixed part written once, the varying step "
                               "delegated down."),
        _jg("interface", "A contract: signatures, constants, and `default`/`static` bodies. "
                         "No instance fields, no constructor."),
        _jg("implements", "The claim that a class fulfils an interface. A class may name any "
                          "number of them, and still `extends` one class."),
        _jg("default method", "An interface method that ships a body, so an interface can "
                              "gain a method without breaking existing implementors."),
        _jg("static interface method", "A utility living on the interface itself. Not "
                                        "inherited — call it through the interface name."),
        _jg("final method", "A method no subclass may override. The opposite of `abstract`, "
                            "and illegal in combination with it."),
        _jg("final class", "A class that cannot be extended. Effectively required of any "
                           "class promising immutability — `String` is one."),
        _jg("composition", "Building an object out of others held in fields — the has-a "
                           "relationship. The default; `extends` is the special case."),
        _jg("delegation", "Forwarding work to a held object, usually in a one-line method. "
                          "Takes exactly the piece you need and nothing more."),
        _jg("aggregation", "Composition where the parts live independently of the whole and "
                           "may be shared — a Team and its Players."),
        _jg("association", "The loosest link: two objects simply know about each other, "
                           "neither owning the other."),
        _jg("fragile base class", "The problem where a change inside a superclass silently "
                                  "breaks subclasses that override its methods."),
    ],
    cheatsheet="""
```java
// --- abstract -----------------------------------------------------------
abstract class Shape {
    abstract int area();                        // no body, semicolon
    String describe() { return "area=" + area(); }   // template method
}
new Shape();                 // does NOT compile — that is the point
// A class with any abstract method MUST be abstract.
// A subclass that does not implement them all must be abstract too.
// `abstract` + `final` on the same member: illegal, they contradict.

// --- interface ----------------------------------------------------------
interface Greeter {
    int MAX = 10;                    // really public static final
    String greet(String name);       // really public abstract

    default String twice(String n) { return greet(n) + greet(n); }
    static Greeter polite() { return new Polite(); }   // NOT inherited
}

class Polite implements Greeter {
    @Override
    public String greet(String n) { return "Hi " + n; }   // `public` REQUIRED
}                                    // else: weaker access privileges; was public

class Loud extends Speaker implements Greeter, Printable { }  // extends first

// --- choosing -----------------------------------------------------------
//                     abstract class      interface
// instance fields      yes                 NO
// constructor          yes                 no
// how many             one                 any number
// bodies               anywhere            default / static only
// ask                  "share state?"      "share capability?"

// The pairing the JDK uses everywhere:
interface Codec { String encode(String s); String decode(String s); }
abstract class SymmetricCodec implements Codec {
    @Override public String decode(String s) { return encode(s); }
}

// --- final --------------------------------------------------------------
final int x = 5;                     // assign once
final int round(int c) { ... }       // no subclass may override
final class Config { ... }           // no subclass at all (String is final)

// --- composition over inheritance ---------------------------------------
class Car extends Engine { }         // is-a FAILS
class Car { private final Engine engine; }          // has-a
String spec() { return model + " " + engine.hp(); } // delegation

// extends takes EVERYTHING (Stack extends ArrayList => add(0, e) on a stack)
// a field takes only what you call, can be reassigned at run time,
// and you only ever get one `extends`.
```
""",
    self_check=[
        "Can you say what `abstract` rules out on a method, and separately on a class?",
        "Can you write a template method and point at the part that never changes?",
        "Can you explain the exact wording of 'attempting to assign weaker access privileges'?",
        "Can you say why implementing two interfaces raises no diamond problem?",
        "Can you say what `default` methods were introduced to solve?",
        "Can you name two things a `static` interface method cannot do?",
        "Given a design, can you choose abstract class vs interface from whether state is shared?",
        "Can you argue against `class Stack extends ArrayList` in one sentence?",
        "Can you take a class that wrongly `extends` and refactor it to a field plus delegation?",
    ],
    review=[
        _jq("```java\ninterface Greeter { String greet(String n); }\nclass Polite implements Greeter {\n    @Override\n    String greet(String n) { return \"Hi \" + n; }\n}\n```\nWhat happens?",
            ["Compile error — the interface method is public and an override may not narrow access",
             "It compiles and runs",
             "It compiles but greet is never called",
             "Compile error — @Override is not allowed on interface methods"],
            0,
            "Everything in an interface is implicitly public. The implementing method has "
            "to say `public` out loud."),
        _jq("Your types share a `name` field and the constructor logic that validates it. Abstract class or interface?",
            ["Abstract class — an interface cannot hold per-object state or run a constructor",
             "Interface with a `name` constant",
             "Interface with a default getter",
             "Either; they are equivalent"],
            0,
            "Shared state is the deciding question. An interface field is a shared "
            "`public static final` constant, not an instance field."),
        _jq("Why is `class Stack extends ArrayList` the standard example of inheritance misused?",
            ["The stack inherits every list operation, so callers can insert at the bottom and it cannot prevent them",
             "ArrayList is final so it will not compile",
             "Stacks are slower than lists",
             "ArrayList has no push method"],
            0,
            "`extends` is all-or-nothing. Holding an array instead lets the class expose "
            "`push` and `pop` and nothing else."),
        _jq("In the capstone, why does `peak` start at `totalDraw()` rather than `0`?",
            ["Heaters draw 5 W while off, so a brand-new room is already above zero",
             "Because peak must never be zero",
             "To avoid a divide by zero",
             "Because the array might be empty"],
            0,
            "A room of two heaters begins at 10 W, and a run that never switches anything "
            "on must still report that. Seeding peak in the constructor is what makes the "
            "no-op case right."),
    ],
    milestone="You can design with types rather than just write them: naming a contract, "
              "sealing what must not change, and reaching for a field before reaching for "
              "`extends`. Part 4 — object-oriented programming — is complete.",
))
