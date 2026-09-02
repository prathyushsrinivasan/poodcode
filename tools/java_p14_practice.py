# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 14 practice - abstraction, interfaces and composition.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[14]`.
#
# Module 14 scope: abstract classes and abstract methods, interfaces and
# `implements`, multiple interfaces, `default` and `static` interface methods,
# abstract class vs interface, `final` methods and classes, composition over
# inheritance, delegation, aggregation and association.
#
# Lambdas are Part 8 and banned course-wide, so every interface here is
# implemented by a NAMED class. Exceptions are Part 5, so nothing throws.
# ---------------------------------------------------------------------------


def _p14ex(eid, title, difficulty, prompt, types, body, tests, hints):
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


# --- Family A - abstract classes ---------------------------------------------

_P14_A = _jfam(
    "p14-abstract", "Abstract classes",
    "A class that cannot be built, and a method with no body.",
    """
```java
abstract class Shape {
    abstract int area();                       // no body, a semicolon

    String describe() {                        // ordinary, and may call area()
        return "area=" + area();
    }
}

new Shape();          // does NOT compile — and that is the point
```

**An abstract method is a demand**: every concrete subclass must supply it. A
class with even one abstract method must itself be `abstract`.

**An abstract class cannot be instantiated**, which upgrades `new Shape()` from
"meaningless at run time" to "rejected at compile time". Module 13's `Shape`
returned a placeholder `0` for its area; `abstract` is how you say *there is no
sensible answer here* instead of inventing one.

**It is still a class.** It has constructors (run via `super(...)`), fields and
ordinary methods. It just cannot be the thing you build.

**The template method is why you reach for one:** a concrete method written in
terms of an abstract one, so the fixed part is written once and only the varying
step is delegated downwards.

```java
abstract class Employee {
    protected final String name;
    Employee(String name) { this.name = name; }

    abstract int pay();                                   // varies
    String slip() { return name + " earns " + pay(); }    // fixed, forever
}
```

`slip()` is correct for every kind of employee that will ever exist, including
ones written years from now.
""",
    [
        _p14ex("j14-pr-abstract-shape", "An abstract base and two subclasses", "Medium",
               "Write `abstract class Shape` with `abstract int area()` and a concrete "
               "`String describe()` returning `area=<area>`. Then `Square extends Shape` "
               "(one side) and `Rect extends Shape` (two sides), each supplying "
               "`area()`. `main` reads two integers and prints both descriptions.",
               """
abstract class Shape {
    abstract int area();

    String describe() {
        return "area=" + area();
    }
}

class Square extends Shape {
    private final int side;

    Square(int side) {
        this.side = side;
    }

    @Override
    int area() {
        return side * side;
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
""",
               """        int p = sc.nextInt();
        int q = sc.nextInt();
        System.out.println(new Square(p).describe());
        System.out.println(new Rect(p, q).describe());""",
               [_case(f"{p} {q}", _nl(f"area={p * p}", f"area={p * q}"))
                for (p, q) in ((3, 4), (1, 1), (0, 5), (12, 2), (7, 7))],
               ["`abstract` goes on both the class and the bodiless method.",
                "`abstract int area();` ends in a semicolon, not braces.",
                "`describe()` is written ONCE in the base and inherited by both — "
                "neither subclass redeclares it.",
                "Each subclass must carry `@Override` on its `area()`.",
                "Neither subclass may be abstract, since both supply the demanded "
                "method."]),

        _p14ex("j14-pr-template", "The template method", "Medium",
               "Write `abstract class Employee` with `protected final String name`, a "
               "constructor, `abstract int pay()`, and `String slip()` returning "
               "`<name> earns <pay>`. Then `Hourly` (rate and hours) and `Salaried` "
               "(annual, paid `annual / 12`). `main` reads a kind, a name and the "
               "numbers.",
               """
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
""",
               """        int kind = sc.nextInt();
        String nm = sc.next();
        Employee e;
        if (kind == 1) {
            int rate = sc.nextInt();
            int hours = sc.nextInt();
            e = new Hourly(nm, rate, hours);
        } else {
            e = new Salaried(nm, sc.nextInt());
        }
        System.out.println(e.slip());""",
               [_case("1 Ann 20 38", f"Ann earns {20 * 38}"),
                _case("2 Bob 60000", f"Bob earns {_jdiv(60000, 12)}"),
                _case("1 Cy 15 0", "Cy earns 0"),
                _case("2 Di 1000", f"Di earns {_jdiv(1000, 12)}"),
                _case("1 Eve 10 10", "Eve earns 100")],
               ["`slip()` is the template: fixed text, one delegated step.",
                "Each subclass passes the name up with `super(name)` and adds its "
                "own fields.",
                "`Salaried.pay()` uses integer division, which truncates.",
                "Neither subclass writes `slip()` — that is the whole return on the "
                "pattern."]),

        _p14ex("j14-pr-abstract-partial", "An abstract class that fills in half",
               "Hard",
               "Write `abstract class Greeter` with `abstract String name()` and a "
               "concrete `String greet()` returning `hello <name>`. Then "
               "`abstract class Titled extends Greeter` adding "
               "`abstract String title()` and overriding `name()` to return "
               "`<title> <base>` where `base` comes from a new `abstract String base()`. "
               "Finally `Doctor extends Titled` supplying `title()` as `Dr` and `base()` "
               "from a constructor argument. `main` reads a one-word name.",
               """
abstract class Greeter {
    abstract String name();

    String greet() {
        return "hello " + name();
    }
}

abstract class Titled extends Greeter {
    abstract String title();

    abstract String base();

    @Override
    String name() {
        return title() + " " + base();
    }
}

class Doctor extends Titled {
    private final String who;

    Doctor(String who) {
        this.who = who;
    }

    @Override
    String title() {
        return "Dr";
    }

    @Override
    String base() {
        return who;
    }
}
""",
               """        String nm = sc.next();
        System.out.println(new Doctor(nm).greet());""",
               [_case(w, f"hello Dr {w}") for w in ("Ada", "a", "Bo", "Smith", "x")],
               ["A subclass that does not implement every inherited abstract method "
                "must itself be `abstract` — that is `Titled`.",
                "`Titled` implements `name()` but introduces two new demands, so it "
                "is still abstract.",
                "`Doctor` satisfies both and is therefore concrete.",
                "`greet()` was written once at the top and still works three levels "
                "down.",
                "The demand is simply passed down the chain until some class finally "
                "meets it."]),

        _p14ex("j14-pr-abstract-ctor", "An abstract class with a constructor", "Medium",
               "Write `abstract class Account` with `protected final int balance`, a "
               "constructor, `abstract int fee()`, and `int net()` returning "
               "`balance - fee()`. Then `Basic` (flat fee `2`) and `Premium` (fee "
               "`balance / 100`). `main` reads a kind and a balance.",
               """
abstract class Account {
    protected final int balance;

    Account(int balance) {
        this.balance = balance;
    }

    abstract int fee();

    int net() {
        return balance - fee();
    }
}

class Basic extends Account {
    Basic(int balance) {
        super(balance);
    }

    @Override
    int fee() {
        return 2;
    }
}

class Premium extends Account {
    Premium(int balance) {
        super(balance);
    }

    @Override
    int fee() {
        return balance / 100;
    }
}
""",
               """        int kind = sc.nextInt();
        int bal = sc.nextInt();
        Account a;
        if (kind == 1) {
            a = new Basic(bal);
        } else {
            a = new Premium(bal);
        }
        System.out.println(a.net());""",
               [_case(f"{k} {b}", b - (2 if k == 1 else _jdiv(b, 100)))
                for (k, b) in ((1, 500), (2, 900), (1, 0), (2, 12345), (2, 50))],
               ["An abstract class may absolutely have a constructor — it just runs "
                "as part of building a subclass.",
                "Both subclasses call `super(balance)`.",
                "`balance` is `protected final`, so `Premium.fee()` can read it and "
                "nothing can change it.",
                "`net()` is another template method: written once, using a step "
                "each subclass supplies."]),

        _p14ex("j14-pr-abstract-array", "An abstract type in an array", "Medium",
               "Reuse `abstract class Shape` with `abstract int area()`. Write `Square` "
               "and `Rect` as before. `main` reads `n`, then `n` lines of `kind a b` "
               "(kind `1` = Square using `a`, otherwise Rect using `a` and `b`), stores "
               "them in a `Shape[]` and prints the total area.",
               """
abstract class Shape {
    abstract int area();
}

class Square extends Shape {
    private final int side;

    Square(int side) {
        this.side = side;
    }

    @Override
    int area() {
        return side * side;
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
""",
               """        int n = sc.nextInt();
        Shape[] shapes = new Shape[n];
        for (int i = 0; i < n; i++) {
            int kind = sc.nextInt();
            int a1 = sc.nextInt();
            int b1 = sc.nextInt();
            if (kind == 1) {
                shapes[i] = new Square(a1);
            } else {
                shapes[i] = new Rect(a1, b1);
            }
        }
        int total = 0;
        for (Shape s : shapes) {
            total += s.area();
        }
        System.out.println(total);""",
               [_case("\n".join([str(len(rows))]
                                + [f"{k} {a} {b}" for (k, a, b) in rows]),
                      sum(a * a if k == 1 else a * b for (k, a, b) in rows))
                for rows in ([(1, 3, 0), (2, 4, 5)],
                             [(1, 2, 9)],
                             [(2, 0, 7), (1, 1, 1)],
                             [(1, 5, 5), (1, 2, 2), (2, 3, 3)],
                             [(2, 10, 10)])],
               ["A `Shape[]` may hold any concrete subclass, even though no `Shape` "
                "itself can ever be built.",
                "The summing loop calls `s.area()` with no type test — dynamic "
                "dispatch picks the right one.",
                "That loop would not change if a `Triangle` were added tomorrow.",
                "The array is declared with the abstract type; only the elements are "
                "concrete."]),
    ])


# --- Family B - interfaces ---------------------------------------------------

_P14_B = _jfam(
    "p14-interface", "Interfaces",
    "A contract with no state and no constructor.",
    """
```java
interface Greeter {
    String greet(String name);        // implicitly public abstract
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {     // `public` is REQUIRED
        return "Good morning, " + name;
    }
}
```

**Everything in an interface is implicitly public.** So an implementing method
declared without `public` produces *attempting to assign weaker access
privileges; was public* — module 13's widening rule, met for real. This is the
single most common first error with interfaces.

**An interface is a type**, and that is what you are buying:

```java
Greeter[] all = { new Polite(), new Loud() };
for (Greeter g : all) System.out.println(g.greet("Ada"));
```

`Polite` and `Loud` need no common superclass and no shared fields — only the
promise that they can greet. Code written against `Greeter` works with
implementations that did not exist when it was written. That is "program to an
interface, not an implementation", and it is the most useful sentence in
object-oriented design.

**What an interface cannot have:** instance fields, a constructor, or any
per-object state. A field declared in one is implicitly `public static final` —
a shared constant, not an instance field.

**`implements` versus `extends`:** a class extends exactly **one** class and
implements **any number** of interfaces. Both may appear, in that order.

The is-a test still applies in its *can-do* form: `implements Greeter` claims
*this thing can greet*.
""",
    [
        _p14ex("j14-pr-iface-basic", "Declare it and implement it", "Intro",
               "Write `interface Greeter` with `String greet(String name);`, and "
               "`class Polite implements Greeter` returning `Good morning, <name>`. "
               "`main` reads a one-word name and prints the greeting.",
               """
interface Greeter {
    String greet(String name);
}

class Polite implements Greeter {
    @Override
    public String greet(String name) {
        return "Good morning, " + name;
    }
}
""",
               """        String nm = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(nm));""",
               [_case(w, f"Good morning, {w}") for w in ("Ada", "a", "Bo", "Zed", "x")],
               ["`interface Greeter { ... }` — not a class.",
                "The method in the interface has no body and no `public` keyword "
                "(it is implied).",
                "The implementing method MUST be declared `public`, or you get "
                "*weaker access privileges*.",
                "The variable is declared as the interface type, which is the whole "
                "point."]),

        _p14ex("j14-pr-iface-many", "Many implementations, one loop", "Easy",
               "Write `interface Greeter` and three implementations: `Polite` "
               "(`Good morning, <name>`), `Loud` (`HEY <NAME>` in upper case) and "
               "`Terse` (just the name). `main` reads a name and prints all three.",
               """
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

class Terse implements Greeter {
    @Override
    public String greet(String name) {
        return name;
    }
}
""",
               """        String nm = sc.next();
        Greeter[] all = { new Polite(), new Loud(), new Terse() };
        for (Greeter g : all) {
            System.out.println(g.greet(nm));
        }""",
               [_case(w, _nl(f"Good morning, {w}", f"HEY {w.upper()}", w))
                for w in ("Ada", "a", "bo", "Zed", "x")],
               ["Three unrelated classes, none extending anything.",
                "All three go in a `Greeter[]` because each IS a Greeter.",
                "The loop names no concrete class at all — adding a fourth would not "
                "touch it.",
                "`toUpperCase()` is module 7."]),

        _p14ex("j14-pr-iface-param", "Program to the interface", "Medium",
               "Write `interface Validator` with `boolean ok(String s);`, plus "
               "`NotEmpty`, `MaxLen` (constructed with a limit) and `Digits`. Then a "
               "`Form` class holding a `Validator[]` with `int passes(String s)` "
               "counting how many accept. `Form` must never mention a concrete "
               "validator.",
               """
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
""",
               """        int max = sc.nextInt();
        String s = sc.next();
        Validator[] rules = { new NotEmpty(), new MaxLen(max), new Digits() };
        System.out.println(new Form(rules).passes(s));""",
               [_case(f"{mx} {s}",
                      (1 if len(s) > 0 else 0) + (1 if len(s) <= mx else 0)
                      + (1 if s.isdigit() else 0))
                for (mx, s) in ((4, "12345"), (6, "12345"), (3, "abc"), (2, "9"),
                                (1, "ab7"))],
               ["`Form` stores and loops over `Validator`, never a concrete class.",
                "`MaxLen` is the only one with state, and it takes it in a "
                "constructor — interfaces cannot hold state, implementations can.",
                "If `Form` ever needs `if (v instanceof MaxLen)`, the design has "
                "failed.",
                "A fourth rule can be added without touching `Form` at all."]),

        _p14ex("j14-pr-iface-unrelated", "One capability, no shared parent", "Medium",
               "Write `interface Printable` with `String line();`, and two entirely "
               "unrelated classes implementing it: `Invoice(String customer, int amount)` "
               "rendering `INVOICE <customer> <amount>`, and `Ticket(String event, "
               "int seat)` rendering `TICKET <event> seat <seat>`. `main` reads `n` items "
               "and prints each line.",
               """
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
""",
               """        int n = sc.nextInt();
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
        }""",
               [_case("\n".join([str(len(rows))]
                                + [f"{k} {lab} {num}" for (k, lab, num) in rows]),
                      _nl(*[(f"INVOICE {lab} {num}" if k == 1
                             else f"TICKET {lab} seat {num}")
                            for (k, lab, num) in rows]))
                for rows in ([(1, "Ada", 250), (2, "Opera", 14)],
                             [(2, "Cup", 1)],
                             [(1, "Bo", 0), (1, "Cy", 99), (2, "Gig", 300)],
                             [(2, "a", 7), (2, "b", 8), (1, "c", 9)],
                             [(1, "solo", 5)])],
               ["Neither class extends anything — `implements Printable` is the "
                "entire relationship.",
                "Inventing a `Document` superclass to hold them would be a lie: they "
                "share no data at all.",
                "Both `line()` methods must be `public`.",
                "Watch the exact wording, including the word `seat` in the ticket."]),

        _p14ex("j14-pr-iface-constant", "A constant on an interface", "Easy",
               "Write `interface Limits` with `int MAX = 100;` and "
               "`boolean within(int v);`, plus `class Strict implements Limits` whose "
               "`within` returns whether `v` is between `0` and `MAX` inclusive. `main` "
               "reads one integer and prints the check and then `Limits.MAX`.",
               """
interface Limits {
    int MAX = 100;

    boolean within(int v);
}

class Strict implements Limits {
    @Override
    public boolean within(int v) {
        return v >= 0 && v <= MAX;
    }
}
""",
               """        int v = sc.nextInt();
        Limits l = new Strict();
        System.out.println(l.within(v));
        System.out.println(Limits.MAX);""",
               [_case(str(v), _nl(_jbool(0 <= v <= 100), 100))
                for v in (50, -1, 100, 101, 0)],
               ["A field in an interface is implicitly `public static final` — a "
                "shared constant, not per-object state.",
                "So no `static` or `final` keyword needs writing, and it must be "
                "given a value immediately.",
                "The implementing class can use `MAX` unqualified, because it "
                "inherits it.",
                "From outside, reach it through the interface name: `Limits.MAX`.",
                "Inclusive bounds, so `100` is within and `101` is not."]),
    ])


# --- Family C - default, static and multiple interfaces ----------------------

_P14_C = _jfam(
    "p14-default", "`default`, `static`, and several at once",
    "Interfaces that ship real code.",
    """
**A class may implement several interfaces:**

```java
class Robot implements Walker, Talker { ... }
```

No diamond problem arises, because interfaces carry **no state** — there are no
competing fields to inherit, and two identical signatures merge harmlessly.

## `default` methods

Originally an interface held nothing but signatures, which made interfaces
impossible to evolve: adding one method broke every implementor everywhere. Java
8 fixed that.

```java
interface Greeter {
    String greet(String name);                  // still abstract

    default String greetTwice(String name) {    // has a body
        return greet(name) + " " + greet(name);
    }
}
```

Implementors get it free and may override it. A default method **can** call the
interface's own abstract methods, and **cannot** touch instance state — because
an interface has none. The moment your "interface" wants a field, it wanted to
be an abstract class.

## `static` interface methods

```java
interface Money {
    int cents();
    static String format(int c) { return c / 100 + "." + (c % 100 < 10 ? "0" : "") + c % 100; }
}

Money.format(425);          // called on the INTERFACE
```

**Static interface methods are not inherited.** Neither `impl.format(...)` nor
`Price.format(...)` compiles — only `Money.format(...)`. They exist so a utility
that obviously belongs to a contract can live with it.

| | abstract | `default` | `static` |
|---|---|---|---|
| Has a body | no | yes | yes |
| Implementor must supply | yes | no | no |
| Can be overridden | must be | may be | never |
| Called through | the object | the object | the interface name |
""",
    [
        _p14ex("j14-pr-multi", "Two contracts at once", "Easy",
               "Write `interface Walker` with `String walk();`, `interface Talker` with "
               "`String talk();`, and `class Robot implements Walker, Talker` built with "
               "an id, returning `<id> walks` and `<id> says hello`. `main` reads an id "
               "and prints both through interface-typed variables.",
               """
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
""",
               """        String id = sc.next();
        Robot r = new Robot(id);
        Walker w = r;
        Talker t = r;
        System.out.println(w.walk());
        System.out.println(t.talk());""",
               [_case(i, _nl(f"{i} walks", f"{i} says hello"))
                for i in ("R2", "unit", "z", "Bot", "x")],
               ["One `implements` keyword covers both, separated by a comma.",
                "The same object can be held as a `Walker` or a `Talker` — one "
                "object, two types.",
                "Both methods must be `public`.",
                "No diamond problem, because neither interface carries state."]),

        _p14ex("j14-pr-default", "An interface method with a body", "Easy",
               "Write `interface Greeter` with `String greet(String name);` and a "
               "`default String greetTwice(String name)` returning the greeting twice "
               "separated by a space. Add `class Polite implements Greeter` returning "
               "`Hi <name>`. `main` prints both.",
               """
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
""",
               """        String nm = sc.next();
        Greeter g = new Polite();
        System.out.println(g.greet(nm));
        System.out.println(g.greetTwice(nm));""",
               [_case(w, _nl(f"Hi {w}", f"Hi {w} Hi {w}"))
                for w in ("Ada", "a", "Bo", "Zed", "x")],
               ["`default` is the keyword that lets an interface method have a "
                "body.",
                "It calls `greet(name)`, which the implementor supplies — a default "
                "method may call the interface's own abstract methods.",
                "`Polite` implements only `greet` and gets `greetTwice` free.",
                "It is not `static`: implementors should be able to override it."]),

        _p14ex("j14-pr-override-default", "Take the default, or replace it", "Medium",
               "Same `Greeter` interface with the `greetTwice` default. Add `Polite` "
               "(`Hi <name>`, keeping the default) and `Terse` (returns the name, and "
               "OVERRIDES `greetTwice` to join the two copies with no space). `main` "
               "prints `greetTwice` for both.",
               """
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
""",
               """        String nm = sc.next();
        Greeter[] all = { new Polite(), new Terse() };
        for (Greeter g : all) {
            System.out.println(g.greetTwice(nm));
        }""",
               [_case(w, _nl(f"Hi {w} Hi {w}", w + w))
                for w in ("Ada", "a", "Bo", "Zed", "x")],
               ["Overriding a default method looks exactly like overriding an "
                "inherited one, `@Override` included.",
                "`Polite` says nothing about `greetTwice` and inherits the default.",
                "`Terse` replaces it entirely.",
                "Both classes are unrelated to each other; they share only the "
                "interface."]),

        _p14ex("j14-pr-static-iface", "A utility on the interface itself", "Medium",
               "Write `interface Money` with `int cents();` and "
               "`static String format(int c)` rendering cents as pounds and pence with "
               "two decimal places (`425` becomes `4.25`, `105` becomes `1.05`). Add "
               "`class Price implements Money`. `main` reads two amounts and prints the "
               "formatted total.",
               """
interface Money {
    int cents();

    static String format(int c) {
        int whole = c / 100;
        int rest = c % 100;
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
""",
               """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Money x = new Price(a1);
        Money y = new Price(b1);
        System.out.println(Money.format(x.cents() + y.cents()));""",
               [_case(f"{a} {b}", f"{(a + b) // 100}.{(a + b) % 100:02d}")
                for (a, b) in ((150, 275), (100, 5), (0, 0), (999, 1), (7, 8))],
               ["`static` on an interface method makes it belong to the interface "
                "itself.",
                "It is called as `Money.format(...)` — not on an object, and not "
                "through `Price`.",
                "Static interface methods are NOT inherited, which is exactly why "
                "`Price.format(...)` would not compile.",
                "Pad a remainder below ten with a leading zero, or `105` prints as "
                "`1.5`."]),

        _p14ex("j14-pr-iface-extends", "An interface built on interfaces", "Medium",
               "Write `interface Walker` (`String walk();`), `interface Talker` "
               "(`String talk();`), and `interface Robotic extends Walker, Talker` "
               "adding a `default String both()` returning `walk() + \" and \" + "
               "talk()`. Add `class Bot implements Robotic` built with an id. `main` "
               "prints `both()`.",
               """
interface Walker {
    String walk();
}

interface Talker {
    String talk();
}

interface Robotic extends Walker, Talker {
    default String both() {
        return walk() + " and " + talk();
    }
}

class Bot implements Robotic {
    private final String id;

    Bot(String id) {
        this.id = id;
    }

    @Override
    public String walk() {
        return id + " walks";
    }

    @Override
    public String talk() {
        return id + " talks";
    }
}
""",
               """        String id = sc.next();
        Robotic r = new Bot(id);
        System.out.println(r.both());""",
               [_case(i, f"{i} walks and {i} talks")
                for i in ("R2", "unit", "z", "Bot", "x")],
               ["An interface uses `extends` to build on other interfaces — not "
                "`implements`.",
                "It may extend SEVERAL, which a class cannot do.",
                "`Robotic` adds no abstract methods of its own; it just bundles two "
                "contracts and adds a default.",
                "`Bot` implements one interface and must supply both inherited "
                "methods.",
                "The default method calls methods it does not implement, which is "
                "perfectly normal."]),
    ])


# --- Family D - choosing, and final ------------------------------------------

_P14_D = _jfam(
    "p14-choose", "Choosing, and `final`",
    "Abstract class or interface, and where the design stops.",
    """
| | abstract class | interface |
|---|---|---|
| Instance fields | yes | **no** (only constants) |
| Constructor | yes | no |
| How many per class | **one** | any number |
| Method bodies | anywhere | `default` / `static` only |
| Models | *is-a-kind-of* | *can-do* |

**The deciding question is state.** Shared *data* means abstract class, because
only a class can hold a field and only a constructor can initialise it. Shared
*capability* means interface.

**The second question is how many.** A class spends its one `extends` forever.
`Comparable`, `Runnable` and `AutoCloseable` are interfaces precisely because any
class at all might need to be one.

**They pair well**, and the standard library does it constantly — `Collection`
is the interface, `AbstractCollection` the skeleton that implements the boring
half. The interface is the type callers depend on; the abstract class is an
optional convenience for implementors.

## `final`

- **A `final` method** cannot be overridden. A guarantee, not an optimisation:
  every subclass rounds the same way, so code relying on that stays correct.
- **A `final` class** cannot be extended. `String` is final, and so is every
  wrapper — a class promising immutability essentially has to be, or a subclass
  could add mutable state and break the promise for everyone.

`final` is a design statement: *this is part of the contract, not a suggestion.*
The counter-argument is that it forecloses extensions you did not foresee, so
the usual rule is to make a class final when it is immutable or when subclassing
would break an invariant, and leave the rest open.

> `final` and `abstract` cannot be combined: one says *you must override this*,
> the other *you may not*.
""",
    [
        _p14ex("j14-pr-skeleton", "The interface and its skeleton", "Hard",
               "Write `interface Codec` with `String encode(String s);` and "
               "`String decode(String s);`. Then "
               "`abstract class SymmetricCodec implements Codec` supplying `decode` as "
               "`encode(s)` and leaving `encode` abstract. Then `Flip extends "
               "SymmetricCodec` reversing the string. `main` reads a word, prints the "
               "encoding, then the decoding of that encoding.",
               """
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

class Flip extends SymmetricCodec {
    @Override
    public String encode(String s) {
        return new StringBuilder(s).reverse().toString();
    }
}
""",
               """        String w = sc.next();
        Codec c = new Flip();
        String enc = c.encode(w);
        System.out.println(enc);
        System.out.println(c.decode(enc));""",
               [_case(w, _nl(w[::-1], w))
                for w in ("hello", "a", "racecar", "abcd", "xy")],
               ["The skeleton is `abstract` because it never implements `encode`.",
                "It `implements Codec`, and the concrete class then `extends` the "
                "skeleton.",
                "`decode` must be `public`, since it comes from an interface.",
                "A symmetric codec undoes itself, so `decode` is simply `encode` — "
                "written once for every future symmetric codec.",
                "The second printed line is always the original word."]),

        _p14ex("j14-pr-final-class", "Close the class", "Intro",
               "Write `final class Config` with `private final int retries` clamped to "
               "`0` if negative, a constructor, and `int retries()`. `main` reads one "
               "integer.",
               """
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
""",
               """        int n = sc.nextInt();
        Config c = new Config(n);
        System.out.println(c.retries());""",
               [_case(str(n), max(n, 0)) for n in (3, 0, -7, 100, 1)],
               ["`final` goes in front of `class`.",
                "It means no subclass may ever exist.",
                "That matters because a subclass could otherwise add mutable state "
                "and break the clamping guarantee for anyone holding a `Config`.",
                "The field is `private final` too — assigned exactly once, in the "
                "constructor."]),

        _p14ex("j14-pr-final-method", "A method nobody may replace", "Medium",
               "Write `class Rounder` with a `final int round(int cents)` returning "
               "`(cents + 50) / 100 * 100`, and `class Logger extends Rounder` adding "
               "`String describe(int cents)` returning `<cents> becomes <rounded>` — "
               "using the inherited final method. `main` reads one integer.",
               """
class Rounder {
    final int round(int cents) {
        return (cents + 50) / 100 * 100;
    }
}

class Logger extends Rounder {
    String describe(int cents) {
        return cents + " becomes " + round(cents);
    }
}
""",
               """        int n = sc.nextInt();
        System.out.println(new Logger().describe(n));""",
               [_case(str(c), f"{c} becomes {(c + 50) // 100 * 100}")
                for c in (149, 150, 0, 99, 1249)],
               ["`final` on the method means `Logger` cannot override it — trying to "
                "would not compile.",
                "`Logger` adds a new method instead, and calls the inherited one.",
                "That is the guarantee: every price in the system rounds identically, "
                "for ever.",
                "Note `final` on a method and `final` on a class are different "
                "scopes of the same idea."]),

        _p14ex("j14-pr-state-or-capability", "Which tool for which job", "Hard",
               "Model two things correctly. Shared STATE: "
               "`abstract class Vehicle` with `protected final String plate`, a "
               "constructor, and `abstract int wheels()`. Shared CAPABILITY: "
               "`interface Insurable` with `int premium();`. Then "
               "`class Car extends Vehicle implements Insurable` with four wheels and a "
               "premium read from the constructor, and `String summary()` returning "
               "`<plate> <wheels> <premium>`. `main` reads a plate and a premium.",
               """
abstract class Vehicle {
    protected final String plate;

    Vehicle(String plate) {
        this.plate = plate;
    }

    abstract int wheels();
}

interface Insurable {
    int premium();
}

class Car extends Vehicle implements Insurable {
    private final int premium;

    Car(String plate, int premium) {
        super(plate);
        this.premium = premium;
    }

    @Override
    int wheels() {
        return 4;
    }

    @Override
    public int premium() {
        return premium;
    }

    String summary() {
        return plate + " " + wheels() + " " + premium();
    }
}
""",
               """        String pl = sc.next();
        int pr = sc.nextInt();
        Car c = new Car(pl, pr);
        System.out.println(c.summary());""",
               [_case(f"{p} {v}", f"{p} 4 {v}")
                for (p, v) in (("AB12", 500), ("x", 0), ("ZZ99", 1200),
                               ("Q1", 1), ("PLATE", 99))],
               ["`plate` is shared DATA, so it belongs on an abstract class — an "
                "interface could not hold it.",
                "Being insurable is a CAPABILITY unrelated to being a vehicle, so it "
                "is an interface.",
                "`extends` comes before `implements` in the class declaration.",
                "`wheels()` overrides a package-private abstract method, so it may "
                "stay package-private; `premium()` comes from an interface and MUST "
                "be `public`.",
                "That asymmetry in one class is the clearest possible reminder of "
                "the access rule."]),

        _p14ex("j14-pr-abstract-vs-iface", "The same job, modelled twice", "Medium",
               "Write `interface Speaker` with `String say();` and a "
               "`default String twice()` returning the phrase twice with a space. Also "
               "write `abstract class Named` with `protected final String name`, a "
               "constructor, and `String label()` returning `[<name>]`. Then "
               "`class Parrot extends Named implements Speaker` saying "
               "`<label> squawk`. `main` reads a name and prints `twice()`.",
               """
interface Speaker {
    String say();

    default String twice() {
        return say() + " " + say();
    }
}

abstract class Named {
    protected final String name;

    Named(String name) {
        this.name = name;
    }

    String label() {
        return "[" + name + "]";
    }
}

class Parrot extends Named implements Speaker {
    Parrot(String name) {
        super(name);
    }

    @Override
    public String say() {
        return label() + " squawk";
    }
}
""",
               """        String nm = sc.next();
        Parrot p = new Parrot(nm);
        System.out.println(p.twice());""",
               [_case(w, f"[{w}] squawk [{w}] squawk")
                for w in ("Polly", "a", "Bo", "Zed", "x")],
               ["The abstract class carries the state (`name`) and a concrete helper "
                "(`label()`).",
                "The interface carries the capability and a default built on it.",
                "`Parrot` takes one of each — exactly one `extends`, any number of "
                "`implements`.",
                "`say()` must be `public` because it comes from the interface, while "
                "`label()` need not be.",
                "`twice()` is inherited from the interface and calls `say()`, which "
                "calls `label()`, which reads the abstract class's field. All three "
                "layers cooperate."]),
    ])


# --- Family E - composition --------------------------------------------------

_P14_E = _jfam(
    "p14-compose", "Composition over inheritance",
    "A field, and a one-line method that forwards.",
    """
```java
class Car extends Engine { }            // a Car IS an Engine? No.

class Car {
    private final Engine engine;        // a Car HAS an Engine. Yes.
    String spec() { return engine.hp() + "hp"; }   // delegation
}
```

That forwarding is **delegation**, and it is nearly always a one-line method.

**Why composition usually wins:**

1. **Inheritance is not selective.** `extends` takes *everything*. The textbook
   disaster is `class Stack extends ArrayList`: your stack now has
   `add(int index, E e)`, so anyone can insert at the bottom of a stack and the
   class cannot stop them. A stack that *has* an array exposes `push` and `pop`
   and nothing else.
2. **The fragile base class problem.** A superclass you did not write can change
   in its next version — a method starts calling another method and your override
   runs twice. Composition depends only on the public methods you actually call.
3. **You get one `extends`, and it is spent forever.** You may hold as many
   fields as you like.
4. **A field can be swapped at run time.** A superclass is fixed the moment the
   object is created.
5. **It composes with interfaces beautifully.** Hold a field typed as an
   *interface* and the held object can be any implementation.

**The vocabulary:** *composition* proper means the part is owned and usually
created by the whole (a `Car` builds its `Engine`); *aggregation* means the parts
live independently and may be shared (a `Team` holds `Player`s); *association*
is the loosest — two objects simply know about each other.

**The rule is not "never inherit".** Overriding is right when the subtype really
is a specialisation and you want polymorphism. The rule is that inheritance
should be a decision, not a reflex.
""",
    [
        _p14ex("j14-pr-hasa", "A Car has an Engine", "Intro",
               "Write `class Engine` with `private final int hp`, a constructor and "
               "`int hp()`. Then `class Car` holding `private final Engine engine` built "
               "in its constructor from a model and an hp, with `String spec()` "
               "returning `<model> <hp>hp`. `main` reads a model and an hp.",
               """
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
""",
               """        String md = sc.next();
        int hp = sc.nextInt();
        System.out.println(new Car(md, hp).spec());""",
               [_case(f"{m} {h}", f"{m} {h}hp")
                for (m, h) in (("Mini", 90), ("Truck", 420), ("z", 0),
                               ("Fast", 700), ("x", 1))],
               ["`Car` does not extend `Engine` — the is-a test fails badly.",
                "It holds one as a `private final` field instead.",
                "The `Car` constructor builds the `Engine`, which is composition "
                "proper: the part is created and owned by the whole.",
                "`spec()` delegates the horsepower question to the engine."]),

        _p14ex("j14-pr-delegate", "Forward the one thing you need", "Easy",
               "Write `class Clock` with `private final int hour, minute`, a "
               "constructor, and `String stamp()` returning `H:MM` with the minute "
               "zero-padded. Then `class Logger` holding a `Clock`, with "
               "`String log(String message)` returning `[<stamp>] <message>`. `main` "
               "reads an hour, a minute and a one-word message.",
               """
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
""",
               """        int h = sc.nextInt();
        int m = sc.nextInt();
        String msg = sc.next();
        System.out.println(new Logger(h, m).log(msg));""",
               [_case(f"{h} {m} {msg}", f"[{h}:{m:02d}] {msg}")
                for (h, m, msg) in ((9, 5, "boot"), (14, 30, "ready"),
                                    (0, 0, "start"), (23, 59, "halt"),
                                    (7, 7, "x"))],
               ["`Logger` never formats a time itself — it asks the `Clock`.",
                "It does not become a `Clock`, and does not inherit the `Clock`'s "
                "other methods.",
                "Pad a minute below ten with a leading zero.",
                "If `Clock` gains a method tomorrow, `Logger` is unaffected — that "
                "is the fragile-base-class problem avoided."]),

        _p14ex("j14-pr-refactor", "A Playlist is not a Song", "Hard",
               "Write `class Song` with `private final String title` and "
               "`private final int seconds`, a constructor, and `int seconds()`. Then "
               "`class Playlist` which **holds** a `Song[]` (it must not extend `Song`) "
               "with `int seconds()` returning the total. `main` reads `n` songs and "
               "prints the count and the total.",
               """
class Song {
    private final String title;
    private final int seconds;

    Song(String title, int seconds) {
        this.title = title;
        this.seconds = seconds;
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
""",
               """        int n = sc.nextInt();
        Song[] songs = new Song[n];
        for (int i = 0; i < n; i++) {
            songs[i] = new Song(sc.next(), sc.nextInt());
        }
        Playlist p = new Playlist(songs);
        System.out.println(n);
        System.out.println(p.seconds());""",
               [_case("\n".join([str(len(rows))] + [f"{t} {s}" for (t, s) in rows]),
                      _nl(len(rows), sum(s for (_t, s) in rows)))
                for rows in ([("Alpha", 210), ("Beta", 185)],
                             [("Solo", 300)],
                             [("a", 1), ("b", 2), ("c", 3)],
                             [("x", 0), ("y", 999)],
                             [("one", 60), ("two", 60), ("three", 60)])],
               ["Say it out loud: a playlist is NOT a song. The is-a test fails, so "
                "`extends` is wrong.",
                "`Playlist extends Song` would force a meaningless "
                "`super(\"playlist\", 0)` and inherit a `seconds()` that lies.",
                "Hold a `Song[]` instead — that was always the real relationship.",
                "`Playlist.seconds()` sums the parts rather than reporting its own "
                "fictional length.",
                "This is aggregation: the songs exist independently of the "
                "playlist."]),

        _p14ex("j14-pr-swap-impl", "Swap the part at run time", "Hard",
               "Write `interface Formatter` with `String format(int v);`, plus `Plain` "
               "(returns the number) and `Bracketed` (returns `[v]`). Then "
               "`class Report` holding a `private Formatter fmt` with "
               "`void setFormatter(Formatter f)` and `String render(int v)`. `main` "
               "reads a value, renders it plainly, swaps the formatter, and renders "
               "again.",
               """
interface Formatter {
    String format(int v);
}

class Plain implements Formatter {
    @Override
    public String format(int v) {
        return "" + v;
    }
}

class Bracketed implements Formatter {
    @Override
    public String format(int v) {
        return "[" + v + "]";
    }
}

class Report {
    private Formatter fmt;

    Report(Formatter fmt) {
        this.fmt = fmt;
    }

    void setFormatter(Formatter f) {
        this.fmt = f;
    }

    String render(int v) {
        return fmt.format(v);
    }
}
""",
               """        int v = sc.nextInt();
        Report r = new Report(new Plain());
        System.out.println(r.render(v));
        r.setFormatter(new Bracketed());
        System.out.println(r.render(v));""",
               [_case(str(v), _nl(str(v), f"[{v}]"))
                for v in (5, 0, -3, 100, 42)],
               ["The field is typed as the INTERFACE, so it can hold any "
                "implementation.",
                "That is the thing inheritance cannot do: a superclass is fixed when "
                "the object is created, a field can be reassigned.",
                "`Report` never names `Plain` or `Bracketed`.",
                "The field is not `final` here, precisely because it is meant to "
                "change.",
                "`\"\" + v` is the shortest way to turn an int into a String."]),

        _p14ex("j14-pr-team", "A Team has Players", "Medium",
               "Write `class Player` with `private final String name` and "
               "`private final int score`, a constructor, `String name()` and "
               "`int score()`. Then `class Team` holding a name and a `Player[]`, with "
               "`int total()`, `String best()` (highest score, first on a tie) and "
               "`String describe()` returning `<team> total=<total> best=<best>`. `main` "
               "reads a team name, `n`, and the players.",
               """
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

    String describe() {
        return name + " total=" + total() + " best=" + best();
    }
}
""",
               """        String tn = sc.next();
        int n = sc.nextInt();
        Player[] ps = new Player[n];
        for (int i = 0; i < n; i++) {
            ps[i] = new Player(sc.next(), sc.nextInt());
        }
        System.out.println(new Team(tn, ps).describe());""",
               [_case("\n".join([f"{team} {len(rows)}"]
                                + [f"{n} {s}" for (n, s) in rows]),
                      f"{team} total={sum(s for (_n, s) in rows)} "
                      f"best={max(rows, key=lambda r: r[1])[0]}")
                for (team, rows) in (("Reds", [("Ada", 12), ("Bo", 30), ("Cy", 7)]),
                                     ("Blues", [("Solo", 5)]),
                                     ("Ties", [("First", 9), ("Second", 9)]),
                                     ("Zeros", [("a", 0), ("b", 0)]),
                                     ("Mixed", [("x", -5), ("y", 3)]))],
               ["`Team` extends nothing — it holds a `Player[]`.",
                "`total()` is the accumulator from module 1; `best()` is the running "
                "maximum, keeping the whole `Player` so the name is still reachable.",
                "Seed `best()` with `players[0]`, which is what makes the negative "
                "case work.",
                "A strict `>` keeps the first of equal scores.",
                "This is aggregation: players exist before and after the team."]),
    ])


_PRACTICE[14] = [_P14_A, _P14_B, _P14_C, _P14_D, _P14_E]
