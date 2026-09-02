# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 13 practice - inheritance and polymorphism.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[13]`.
#
# Module 13 scope: `extends` and the is-a test, `protected`, `super(...)` and
# `super.method()`, overriding vs overloading, `@Override`, polymorphism and
# dynamic dispatch, upcasting and downcasting, `instanceof`, `Object` as the
# root, and the toString / equals / hashCode contracts.
#
# `abstract`, `interface` and `implements` are module 14, so every base class
# here is concrete. Exceptions are Part 5, so nothing throws.
# ---------------------------------------------------------------------------


def _p13ex(eid, title, difficulty, prompt, types, body, tests, hints):
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


# --- Family A - extends ------------------------------------------------------

_P13_A = _jfam(
    "p13-extends", "`extends`",
    "One class built on another, and the question to ask first.",
    """
```java
class Animal {
    protected String name;

    Animal(String name) { this.name = name; }

    String describe() { return name + " is an animal"; }
}

class Dog extends Animal {
    Dog(String name) { super(name); }

    String fetch() { return name + " fetches"; }    // `name` is inherited
}
```

A `Dog` now has everything an `Animal` has, plus whatever it adds.

**Ask the is-a question out loud before writing `extends`.** *A Dog is an
Animal* — fine. *A Car is an Engine* — obviously wrong, and the fix is a field,
not a keyword. The test fails far more often than people expect, which is why
module 14 spends a whole family arguing for composition.

**What is inherited:** every `public` and `protected` member, and every
package-private one in the same package. **Constructors are not inherited** — a
subclass declares its own.

**`private` members are not accessible to a subclass.** They still exist inside
the object, but the subclass's code cannot name them. `protected` is the level
that opens a member to subclasses while keeping it away from everyone else. Use
it sparingly: a protected field is a promise to every future subclass, and you
can never take it back.

**Java has single inheritance.** A class extends exactly one class. Interfaces
(module 14) are how a type fits into several categories at once.

**Every class extends something.** Write no `extends` and you extend
`java.lang.Object`, which is where `toString()`, `equals()` and `hashCode()`
come from.
""",
    [
        _p13ex("j13-pr-extends", "Build on another class", "Intro",
               "Write an `Animal` class with `protected String name`, a constructor, and "
               "`String describe()` returning `<name> is an animal`. Then write "
               "`Dog extends Animal` with a constructor passing the name up, and "
               "`String fetch()` returning `<name> fetches`. `main` reads a one-word "
               "name and prints both.",
               """
class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    String describe() {
        return name + " is an animal";
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }

    String fetch() {
        return name + " fetches";
    }
}
""",
               """        String nm = sc.next();
        Dog d = new Dog(nm);
        System.out.println(d.describe());
        System.out.println(d.fetch());""",
               [_case(w, _nl(f"{w} is an animal", f"{w} fetches"))
                for w in ("Rex", "a", "Lassie", "Bo", "Spot")],
               ["`class Dog extends Animal` is the whole link.",
                "`Dog` declares its own constructor, because constructors are never "
                "inherited.",
                "That constructor must call `super(name)` to build the `Animal` part.",
                "`name` is `protected`, so `Dog` can read it directly. If it were "
                "`private`, `fetch()` would not compile.",
                "`describe()` is inherited and must NOT be redeclared."]),

        _p13ex("j13-pr-chain", "Three deep", "Easy",
               "Write `Animal` (with `protected String name`, a constructor and "
               "`String describe()` returning `<name> is an animal`), then "
               "`Dog extends Animal`, then `Puppy extends Dog`. Each passes the name up. "
               "`Puppy` adds `String yap()` returning `<name> yaps`. `main` prints "
               "`describe()` and `yap()`.",
               """
class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    String describe() {
        return name + " is an animal";
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }
}

class Puppy extends Dog {
    Puppy(String name) {
        super(name);
    }

    String yap() {
        return name + " yaps";
    }
}
""",
               """        String nm = sc.next();
        Puppy p = new Puppy(nm);
        System.out.println(p.describe());
        System.out.println(p.yap());""",
               [_case(w, _nl(f"{w} is an animal", f"{w} yaps"))
                for w in ("Rex", "a", "Lassie", "Bo", "Spot")],
               ["Inheritance chains as deep as you like.",
                "Each constructor passes the name one level up with `super(name)`.",
                "`Dog` adds nothing at all, which is legal — its body is just the "
                "constructor.",
                "`describe()` is inherited through two levels and still works.",
                "`name` is `protected` on `Animal`, so `Puppy` can reach it even "
                "though it is two levels down."]),

        _p13ex("j13-pr-protected", "What a subclass can and cannot see", "Medium",
               "Write a `Base` class with `private int hidden = 1;`, "
               "`protected int shared = 2;` and `int getHidden()` returning `hidden`. "
               "Then `Derived extends Base` with `int sum()` returning "
               "`getHidden() + shared` — it must reach `hidden` through the getter, "
               "because it cannot name it directly.",
               """
class Base {
    private int hidden = 1;
    protected int shared = 2;

    int getHidden() {
        return hidden;
    }
}

class Derived extends Base {
    int sum() {
        return getHidden() + shared;
    }
}
""",
               """        int ignored = sc.nextInt();
        Derived d = new Derived();
        System.out.println(d.sum());""",
               [_case(str(v), 3) for v in (1, 0, -3, 100, 5)],
               ["`shared` is `protected`, so `Derived` names it directly.",
                "`hidden` is `private`, so `Derived` cannot name it — writing "
                "`hidden` there would not compile.",
                "It is still THERE inside the object; the subclass just has no "
                "access to the name.",
                "The public route in is the inherited `getHidden()` method.",
                "Neither class declares a constructor, so Java's free no-argument "
                "one is used, and both fields keep their declared initial values."]),

        _p13ex("j13-pr-add-field", "A subclass with its own state", "Easy",
               "Write `Shape` with `protected String label`, a constructor and "
               "`String describe()` returning `shape <label>`. Then "
               "`Square extends Shape` with an extra `private int side`, a constructor "
               "taking both, and `int area()`. `main` reads a label and a side.",
               """
class Shape {
    protected String label;

    Shape(String label) {
        this.label = label;
    }

    String describe() {
        return "shape " + label;
    }
}

class Square extends Shape {
    private int side;

    Square(String label, int side) {
        super(label);
        this.side = side;
    }

    int area() {
        return side * side;
    }
}
""",
               """        String lb = sc.next();
        int sd = sc.nextInt();
        Square s = new Square(lb, sd);
        System.out.println(s.describe());
        System.out.println(s.area());""",
               [_case(f"{lb} {sd}", _nl(f"shape {lb}", sd * sd))
                for (lb, sd) in (("box", 4), ("x", 0), ("tile", 1), ("big", 12),
                                 ("s", 7))],
               ["A subclass may add fields of its own.",
                "`super(label)` must come FIRST in the constructor, before "
                "`this.side = side;`.",
                "That ordering is enforced: the parent part has to be built before "
                "the child part.",
                "`side` is `private` to `Square`, which is fine — nothing below it "
                "needs it."]),

        _p13ex("j13-pr-object-root", "Everything extends Object", "Medium",
               "Write a `Thing` class with no `extends` clause, `private int id`, a "
               "constructor and `int getId()`. `main` prints the id, then whether the "
               "object `instanceof Object` — which is always `true`.",
               """
class Thing {
    private int id;

    Thing(int id) {
        this.id = id;
    }

    int getId() {
        return id;
    }
}
""",
               """        int v = sc.nextInt();
        Thing t = new Thing(v);
        System.out.println(t.getId());
        System.out.println(t instanceof Object);""",
               [_case(str(v), _nl(v, "true")) for v in (5, 0, -3, 100, 1)],
               ["A class with no `extends` clause implicitly extends "
                "`java.lang.Object`.",
                "So every object in Java is an `Object`, and the second line is "
                "always `true`.",
                "That is where `toString()`, `equals()` and `hashCode()` come from — "
                "the last family in this module overrides all three.",
                "You never write `extends Object` yourself; it is implied."]),
    ])


# --- Family B - super --------------------------------------------------------

_P13_B = _jfam(
    "p13-super", "`super`",
    "Two unrelated jobs sharing one keyword.",
    """
## 1. `super(...)` calls the superclass constructor

```java
class Dog extends Animal {
    private String breed;

    Dog(String name, String breed) {
        super(name);              // build the Animal part FIRST
        this.breed = breed;       // then the Dog part
    }
}
```

**It must be the first statement.** The parent's fields have to exist before the
child's constructor can rely on them.

**If you omit it, Java inserts `super();`** — a call to the parent's *no-argument*
constructor. So if the parent only declares `Animal(String)`, a subclass
constructor without an explicit `super(...)` fails to compile with a message
about a missing `Animal()`. That error is confusing exactly once.

## 2. `super.method()` calls the parent's version

```java
@Override
String describe() {
    return super.describe() + ", a dog";     // EXTEND rather than replace
}
```

This is how you add to inherited behaviour instead of throwing it away.

**A bare `describe()` there would be infinite recursion**, because dynamic
dispatch would send it straight back to the overriding method. `super.` is what
says "the version one level up, specifically". It is the one place where the
call is resolved statically rather than dynamically.

`super` and `this` mirror each other: `this(...)` and `super(...)` both delegate
constructors (and you may use only one of them, as the first statement);
`this.x` and `super.x` both name a member, one on this object, one on its parent
half.
""",
    [
        _p13ex("j13-pr-super-ctor", "Pass the parent its part", "Easy",
               "Write `Animal` with `protected String name`, a constructor and "
               "`String describe()` returning `<name> is an animal`. Then "
               "`Dog extends Animal` with `private String breed`, a two-argument "
               "constructor, and `String full()` returning `<name> the <breed>`.",
               """
class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    String describe() {
        return name + " is an animal";
    }
}

class Dog extends Animal {
    private String breed;

    Dog(String name, String breed) {
        super(name);
        this.breed = breed;
    }

    String full() {
        return name + " the " + breed;
    }
}
""",
               """        String nm = sc.next();
        String br = sc.next();
        Dog d = new Dog(nm, br);
        System.out.println(d.describe());
        System.out.println(d.full());""",
               [_case(f"{n} {b}", _nl(f"{n} is an animal", f"{n} the {b}"))
                for (n, b) in (("Rex", "collie"), ("a", "b"), ("Bo", "pug"),
                               ("Spot", "beagle"), ("x", "y"))],
               ["`super(name)` is the first statement in `Dog`'s constructor.",
                "Then assign the subclass's own field.",
                "Reversing the order does not compile — the parent must be built "
                "first.",
                "Omitting `super(name)` also fails, because Java would insert "
                "`super()` and `Animal` has no no-argument constructor."]),

        _p13ex("j13-pr-super-method", "Extend, do not replace", "Medium",
               "Write `Animal` with `protected String name`, a constructor and "
               "`String describe()` returning `<name> is an animal`. Then "
               "`Dog extends Animal` overriding `describe()` to return the parent's "
               "answer followed by `, a dog` — using `super.describe()`.",
               """
class Animal {
    protected String name;

    Animal(String name) {
        this.name = name;
    }

    String describe() {
        return name + " is an animal";
    }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);
    }

    @Override
    String describe() {
        return super.describe() + ", a dog";
    }
}
""",
               """        String nm = sc.next();
        Dog d = new Dog(nm);
        System.out.println(d.describe());""",
               [_case(w, f"{w} is an animal, a dog")
                for w in ("Rex", "a", "Lassie", "Bo", "Spot")],
               ["The override calls `super.describe()` to get the inherited text.",
                "Writing a bare `describe()` there would call ITSELF forever — "
                "dynamic dispatch would send it right back.",
                "`super.` is the one call that is resolved statically, to the parent "
                "version specifically.",
                "Then append `, a dog` — note the comma and the space.",
                "`@Override` is optional but should always be written."]),

        _p13ex("j13-pr-super-chain", "Through three levels", "Medium",
               "Write `A` with `String who()` returning `A`; `B extends A` overriding it "
               "to return `super.who() + \"B\"`; and `C extends B` overriding it to "
               "return `super.who() + \"C\"`. `main` prints `new C().who()`, which is "
               "`ABC`.",
               """
class A {
    String who() {
        return "A";
    }
}

class B extends A {
    @Override
    String who() {
        return super.who() + "B";
    }
}

class C extends B {
    @Override
    String who() {
        return super.who() + "C";
    }
}
""",
               """        int ignored = sc.nextInt();
        System.out.println(new C().who());""",
               [_case(str(v), "ABC") for v in (1, 0, -3, 100, 5)],
               ["Each level appends its own letter to whatever the level above "
                "returned.",
                "`super.who()` in `C` reaches `B`'s version, which itself calls "
                "`A`'s.",
                "So the string is built from the top down: `A`, then `AB`, then "
                "`ABC`.",
                "None of these classes declares a constructor, so the free "
                "no-argument ones chain automatically.",
                "The answer is the same for every input."]),

        _p13ex("j13-pr-super-field", "The parent's field, adjusted", "Medium",
               "Write `Employee` with `protected int base`, a constructor, and "
               "`int pay()` returning `base`. Then `Manager extends Employee` with "
               "`private int bonus`, a two-argument constructor, and an override of "
               "`pay()` returning `super.pay() + bonus`.",
               """
class Employee {
    protected int base;

    Employee(int base) {
        this.base = base;
    }

    int pay() {
        return base;
    }
}

class Manager extends Employee {
    private int bonus;

    Manager(int base, int bonus) {
        super(base);
        this.bonus = bonus;
    }

    @Override
    int pay() {
        return super.pay() + bonus;
    }
}
""",
               """        int b1 = sc.nextInt();
        int b2 = sc.nextInt();
        Manager m = new Manager(b1, b2);
        System.out.println(m.pay());""",
               [_case(f"{a} {b}", a + b)
                for (a, b) in ((1000, 500), (0, 0), (-100, 100), (50, 5),
                               (9999, 1))],
               ["The override extends the parent's calculation rather than "
                "repeating it.",
                "`super.pay() + bonus` means that if the base pay rule ever changes, "
                "`Manager` follows automatically.",
                "Writing `base + bonus` instead would work today and silently "
                "diverge the moment `Employee.pay()` gains a rule.",
                "`super(base)` first in the constructor, then the bonus."]),

        _p13ex("j13-pr-implicit-super", "The constructor call you did not write",
               "Medium",
               "Write `Parent` with a **no-argument** constructor that sets "
               "`protected String tag = \"parent\";` to `\"built\"`, and "
               "`String getTag()`. Then `Child extends Parent` with a constructor that "
               "writes **no** `super(...)` call at all. `main` prints the tag, which is "
               "`built` because Java inserted `super()` for you.",
               """
class Parent {
    protected String tag = "parent";

    Parent() {
        tag = "built";
    }

    String getTag() {
        return tag;
    }
}

class Child extends Parent {
    Child() {
    }
}
""",
               """        int ignored = sc.nextInt();
        System.out.println(new Child().getTag());""",
               [_case(str(v), "built") for v in (1, 0, -3, 100, 5)],
               ["`Child`'s constructor body is empty, and it writes no "
                "`super(...)`.",
                "Java silently inserts `super();` as the first statement anyway.",
                "So `Parent()` runs and overwrites the field, and the tag is "
                "`built`.",
                "The field initialiser `= \"parent\"` runs first, then the "
                "constructor body — which is why the later value wins.",
                "If `Parent` had ONLY a `Parent(String)` constructor, this would "
                "fail to compile, because the inserted `super()` would match "
                "nothing."]),
    ])


# --- Family C - overriding versus overloading --------------------------------

_P13_C = _jfam(
    "p13-override", "Overriding versus overloading",
    "Identical signature, or merely the same name.",
    """
| | Parameters | Resolved | Where |
|---|---|---|---|
| **Overload** | **different** | compile time | usually one class |
| **Override** | **identical** | **run time** | subclass replaces superclass |

That table is the answer to the most-asked question in this module, and every
other fact follows from it.

```java
class Animal {
    String speak() { return "..."; }
}

class Dog extends Animal {
    @Override
    String speak() { return "woof"; }         // OVERRIDE: same signature

    String speak(int times) { return "woof x" + times; }   // OVERLOAD
}
```

**`@Override` is optional and you should always write it.** It asks the compiler
to check that the method really does override something. Without it, a typo in
the name or a wrong parameter type silently creates a *new* method, and the
parent's version keeps running — a bug that is very hard to see by reading.

**What cannot be overridden:** `static`, `private` and `final` methods. A static
method redeclared in a subclass is *hidden*, not overridden, and which one runs
depends on the declared type rather than the object — a genuinely confusing
corner best avoided entirely.

**An override may widen access, never narrow it.** A `public` method cannot be
overridden as package-private; the compiler says *attempting to assign weaker
access privileges*. It may also return a **subtype** of the original return type
(covariant returns), which is occasionally useful.

**Overriding is what makes the next family work.** Overloading is a convenience;
overriding is the mechanism behind polymorphism.
""",
    [
        _p13ex("j13-pr-override-basic", "Replace the behaviour", "Intro",
               "Write `Animal` with `String speak()` returning `...`, and "
               "`Dog extends Animal` overriding it to return `woof`. `main` prints an "
               "`Animal`'s and a `Dog`'s.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }
}
""",
               """        int ignored = sc.nextInt();
        System.out.println(new Animal().speak());
        System.out.println(new Dog().speak());""",
               [_case(str(v), _nl("...", "woof")) for v in (1, 0, -3, 100, 5)],
               ["The override must have the SAME signature: same name, same "
                "parameters, compatible return type.",
                "`@Override` above it asks the compiler to verify that.",
                "The parent's version still exists and still runs for an `Animal`.",
                "Neither class needs a constructor."]),

        _p13ex("j13-pr-both", "One overrides, one overloads", "Medium",
               "Write `Animal` with `String speak()` returning `...`. Then "
               "`Dog extends Animal` which BOTH overrides `speak()` to return `woof` AND "
               "overloads it with `String speak(int times)` returning "
               "`woof x<times>`. `main` calls both.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }

    String speak(int times) {
        return "woof x" + times;
    }
}
""",
               """        int k = sc.nextInt();
        Dog d = new Dog();
        System.out.println(d.speak());
        System.out.println(d.speak(k));""",
               [_case(str(k), _nl("woof", f"woof x{k}")) for k in (3, 0, 1, 10, 7)],
               ["`speak()` has the same signature as the parent's, so it OVERRIDES.",
                "`speak(int)` has a different parameter list, so it OVERLOADS — it "
                "replaces nothing.",
                "`@Override` belongs on the first one only. Putting it on the second "
                "would be a compile error, which is exactly the check you want.",
                "The compiler picks between them by the argument at the call site."]),

        _p13ex("j13-pr-override-typo", "The method that overrides nothing", "Medium",
               "Write `Animal` with `String speak()` returning `...`, and "
               "`Dog extends Animal` that declares `String Speak()` — capital S, no "
               "`@Override` — returning `woof`. `main` calls `speak()` on a `Dog`, and "
               "gets the INHERITED `...` because nothing was actually overridden.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    String Speak() {
        return "woof";
    }
}
""",
               """        int ignored = sc.nextInt();
        Dog d = new Dog();
        System.out.println(d.speak());
        System.out.println(d.Speak());""",
               [_case(str(v), _nl("...", "woof")) for v in (1, 0, -3, 100, 5)],
               ["`Speak` and `speak` are different names, so `Dog` now has BOTH "
                "methods.",
                "`d.speak()` finds the inherited one and prints `...`.",
                "This compiles perfectly and is almost always a bug.",
                "Adding `@Override` to `Speak()` would have turned it into a compile "
                "error — which is the entire argument for always writing it.",
                "Write the class exactly as described, typo and all: the point is to "
                "see the failure."]),

        _p13ex("j13-pr-final-method", "A method that cannot be replaced", "Medium",
               "Write `Base` with `final String id()` returning `base` and "
               "`String label()` returning `plain`. Then `Sub extends Base` overriding "
               "only `label()` to return `fancy` — `id()` cannot be overridden. `main` "
               "prints both from a `Sub`.",
               """
class Base {
    final String id() {
        return "base";
    }

    String label() {
        return "plain";
    }
}

class Sub extends Base {
    @Override
    String label() {
        return "fancy";
    }
}
""",
               """        int ignored = sc.nextInt();
        Sub s = new Sub();
        System.out.println(s.id());
        System.out.println(s.label());""",
               [_case(str(v), _nl("base", "fancy")) for v in (1, 0, -3, 100, 5)],
               ["`final` on a method forbids any subclass from overriding it.",
                "So `Sub` inherits `id()` unchanged and cannot replace it.",
                "Trying to override it would not compile — try it once to see the "
                "message.",
                "`label()` is not final and is overridden normally.",
                "`final` is a design statement: this behaviour is part of the "
                "contract, not a suggestion. Module 14 argues about when to use it."]),

        _p13ex("j13-pr-widen-access", "Widening access on an override", "Medium",
               "Write `Base` with a package-private `String tag()` returning `base`. "
               "Then `Sub extends Base` overriding it as **`public`** — widening access "
               "is allowed. `main` prints a `Sub`'s tag.",
               """
class Base {
    String tag() {
        return "base";
    }
}

class Sub extends Base {
    @Override
    public String tag() {
        return "sub";
    }
}
""",
               """        int ignored = sc.nextInt();
        System.out.println(new Sub().tag());""",
               [_case(str(v), "sub") for v in (1, 0, -3, 100, 5)],
               ["An override may make a method MORE visible, never less.",
                "Package-private to `public` is widening, so it is fine.",
                "Going the other way — `public` in the parent, package-private in "
                "the child — gives *attempting to assign weaker access "
                "privileges*.",
                "The reason is substitutability: anyone holding a `Base` may call "
                "`tag()`, so every subclass must still allow it.",
                "This exact rule is why module 14's interface implementations must "
                "all be `public`."]),
    ])


# --- Family D - polymorphism -------------------------------------------------

_P13_D = _jfam(
    "p13-poly", "Polymorphism",
    "The variable decides what you may call; the object decides what runs.",
    """
```java
Animal a = new Dog();      // upcast: always safe, no cast needed
a.speak();                 // "woof" — the OBJECT decides
a.fetch();                 // does NOT compile — the VARIABLE decides what you may call
```

Two different questions, and keeping them apart is the whole module:

- **What may I call?** Answered at compile time, from the variable's **declared**
  type.
- **Which implementation runs?** Answered at run time, from the object's
  **actual** class. That is **dynamic dispatch**.

**The payoff is a loop that never changes:**

```java
Animal[] zoo = { new Dog(), new Cat(), new Animal() };
for (Animal x : zoo) System.out.println(x.speak());
```

No `if`, no type test, and adding a `Horse` tomorrow does not touch this code.
That property — extend without editing — is the entire return on inheritance's
complexity.

**Downcasting** goes the other way and is checked at run time:

```java
if (a instanceof Dog) {          // ALWAYS guard it
    Dog d = (Dog) a;
    d.fetch();
}
if (a instanceof Dog d) { ... }  // Java 16+: test and bind in one step
```

An unguarded cast throws `ClassCastException`. `instanceof` is also `false` for
`null`, so it doubles as a null check.

**A chain of `instanceof` choosing behaviour is a smell.** It usually means the
behaviour belongs on the classes instead. Counting *kinds* is a legitimate
exception — that really is a question about types.

> Careful: `instanceof` is true for the whole subtree. If `Square extends Rect`,
> then every `Square` is also a `Rect`, so `x instanceof Rect` counts squares
> too.
""",
    [
        _p13ex("j13-pr-dispatch", "The object decides", "Easy",
               "Write `Animal` with `String speak()` returning `...`, `Dog extends "
               "Animal` returning `woof`, and `Cat extends Animal` returning `meow`. "
               "`main` holds each in an `Animal` variable and prints all three.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }
}

class Cat extends Animal {
    @Override
    String speak() {
        return "meow";
    }
}
""",
               """        int ignored = sc.nextInt();
        Animal a = new Animal();
        Animal b = new Dog();
        Animal c = new Cat();
        System.out.println(a.speak());
        System.out.println(b.speak());
        System.out.println(c.speak());""",
               [_case(str(v), _nl("...", "woof", "meow")) for v in (1, 0, -3, 100, 5)],
               ["All three variables are declared `Animal`, yet three different "
                "methods run.",
                "That is dynamic dispatch: the object's real class wins.",
                "Assigning a `Dog` to an `Animal` variable is an upcast and needs no "
                "cast syntax.",
                "Each override needs the same signature as the parent's method."]),

        _p13ex("j13-pr-array-poly", "One loop, many behaviours", "Medium",
               "Same three classes. `main` builds an `Animal[]` of `n` animals from "
               "input codes (`1` = Dog, `2` = Cat, anything else = plain Animal) and "
               "prints each one's `speak()` on its own line, with no type test in the "
               "loop.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }
}

class Cat extends Animal {
    @Override
    String speak() {
        return "meow";
    }
}
""",
               """        int n = sc.nextInt();
        Animal[] zoo = new Animal[n];
        for (int i = 0; i < n; i++) {
            int kind = sc.nextInt();
            if (kind == 1) {
                zoo[i] = new Dog();
            } else if (kind == 2) {
                zoo[i] = new Cat();
            } else {
                zoo[i] = new Animal();
            }
        }
        for (Animal x : zoo) {
            System.out.println(x.speak());
        }""",
               [_case("\n".join([str(len(ks)), " ".join(str(k) for k in ks)]),
                      _nl(*["woof" if k == 1 else ("meow" if k == 2 else "...")
                            for k in ks]))
                for ks in ([1, 2, 3], [1], [2, 2], [3, 1, 2, 1], [9, 9])],
               ["An `Animal[]` can hold any subclass, because each one IS an "
                "Animal.",
                "The printing loop calls `x.speak()` with no `if` and no "
                "`instanceof`.",
                "Adding a fourth animal tomorrow would not change that loop at all — "
                "only the building code.",
                "The building code does need an `if`, because something must choose "
                "what to construct. That is the one place types belong."]),

        _p13ex("j13-pr-instanceof", "Counting kinds", "Medium",
               "Same three classes, same input format. `main` prints how many of the "
               "animals are `Dog`s, using `instanceof`.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }
}

class Cat extends Animal {
    @Override
    String speak() {
        return "meow";
    }
}
""",
               """        int n = sc.nextInt();
        Animal[] zoo = new Animal[n];
        for (int i = 0; i < n; i++) {
            int kind = sc.nextInt();
            if (kind == 1) {
                zoo[i] = new Dog();
            } else if (kind == 2) {
                zoo[i] = new Cat();
            } else {
                zoo[i] = new Animal();
            }
        }
        int dogs = 0;
        for (Animal x : zoo) {
            if (x instanceof Dog) {
                dogs++;
            }
        }
        System.out.println(dogs);""",
               [_case("\n".join([str(len(ks)), " ".join(str(k) for k in ks)]),
                      sum(1 for k in ks if k == 1))
                for ks in ([1, 2, 3], [1], [2, 2], [3, 1, 2, 1], [9, 9])],
               ["Counting a KIND is a genuine question about types, so `instanceof` "
                "is the right tool here.",
                "Contrast with the previous variant, where behaviour belonged on the "
                "object and no type test was needed.",
                "`x instanceof Dog` is true only for actual Dogs — a plain `Animal` "
                "is not one.",
                "It would also be true for any subclass of `Dog`, which is worth "
                "remembering when a hierarchy is deeper."]),

        _p13ex("j13-pr-downcast", "Guarded downcasting", "Hard",
               "Write `Animal` with `String speak()` returning `...`, and "
               "`Dog extends Animal` overriding it and adding `String fetch()` returning "
               "`fetches`. `main` builds one animal from a code, prints `speak()`, then "
               "prints `fetch()` only if it really is a `Dog` — otherwise `cannot "
               "fetch`.",
               """
class Animal {
    String speak() {
        return "...";
    }
}

class Dog extends Animal {
    @Override
    String speak() {
        return "woof";
    }

    String fetch() {
        return "fetches";
    }
}
""",
               """        int kind = sc.nextInt();
        Animal a;
        if (kind == 1) {
            a = new Dog();
        } else {
            a = new Animal();
        }
        System.out.println(a.speak());
        if (a instanceof Dog) {
            Dog d = (Dog) a;
            System.out.println(d.fetch());
        } else {
            System.out.println("cannot fetch");
        }""",
               [_case(str(k), _nl("woof" if k == 1 else "...",
                                  "fetches" if k == 1 else "cannot fetch"))
                for k in (1, 2, 0, 1, 9)],
               ["`a.fetch()` would not compile: the VARIABLE is an `Animal`, and "
                "`Animal` has no `fetch`.",
                "So you must downcast — and guard the cast with `instanceof` first.",
                "An unguarded `(Dog) a` on a plain `Animal` throws "
                "`ClassCastException` at run time.",
                "`instanceof` is also `false` for `null`, so it doubles as a null "
                "check.",
                "Java 16+ lets you write `if (a instanceof Dog d)` and skip the "
                "separate cast line."]),

        _p13ex("j13-pr-subtree", "instanceof covers the whole subtree", "Hard",
               "Write `Rect` with `protected int w, h`, a constructor and `int area()`; "
               "then `Square extends Rect` whose constructor calls `super(side, side)` "
               "and which adds nothing else. `main` builds one of each and prints, for "
               "both, whether it is a `Rect` and whether it is a `Square`.",
               """
class Rect {
    protected int w;
    protected int h;

    Rect(int w, int h) {
        this.w = w;
        this.h = h;
    }

    int area() {
        return w * h;
    }
}

class Square extends Rect {
    Square(int side) {
        super(side, side);
    }
}
""",
               """        int sd = sc.nextInt();
        Rect r = new Rect(sd, sd + 1);
        Rect sq = new Square(sd);
        System.out.println(r instanceof Rect);
        System.out.println(r instanceof Square);
        System.out.println(sq instanceof Rect);
        System.out.println(sq instanceof Square);
        System.out.println(sq.area());""",
               [_case(str(sd), _nl("true", "false", "true", "true", sd * sd))
                for sd in (3, 1, 0, 12, 7)],
               ["A `Square` IS a `Rect`, so `sq instanceof Rect` is `true`.",
                "A plain `Rect` is not a `Square`, so the second line is `false`.",
                "That asymmetry is why counting `instanceof Rect` would over-count "
                "when squares are present — a classic off-by-one in the type tree.",
                "`Square` inherits `area()` unchanged; `super(side, side)` is all it "
                "needs.",
                "Re-implementing `area()` in `Square` would work and would be the "
                "wrong instinct."]),
    ])


# --- Family E - the Object methods -------------------------------------------

_P13_E = _jfam(
    "p13-object", "`toString`, `equals` and `hashCode`",
    "The three methods every serious class overrides.",
    """
## `toString`

```java
@Override
public String toString() {
    return "(" + x + ", " + y + ")";
}
```

`System.out.println(obj)` and string concatenation call it for you. Without an
override you get `Point@1b6d3586` — the class name and a hash in hex, which
tells you nothing. **It must be `public`**, because `Object`'s is.

## `equals`

```java
@Override
public boolean equals(Object o) {              // MUST take Object
    if (this == o) return true;                // 1. same object: fast path
    if (!(o instanceof Point)) return false;   // 2. wrong type (or null)
    Point other = (Point) o;                   // 3. now the cast is safe
    return x == other.x && y == other.y;       // 4. compare the fields
}
```

**The parameter must be `Object`.** Writing `equals(Point o)` is an *overload*,
not an override — and it compiles, and `Object`'s reference-comparing version
keeps getting called from anything holding your object generically. `@Override`
catches it instantly, which is the single best argument for the annotation.

Step 2 handles `null` for free: `null instanceof Point` is `false`.

## `hashCode`

**The contract: equal objects must have equal hash codes.** Break it and
`HashMap` and `HashSet` silently lose your objects — they hash to one bucket and
are looked for in another. Unequal objects *may* share a hash code; that is a
collision, and it is merely slow, not wrong.

```java
@Override
public int hashCode() {
    return Objects.hash(x, y);       // or 31 * x + y by hand
}
```

**Always override both together.** Overriding `equals` alone is the bug, and it
stays invisible until the first time your object goes into a hash-based
collection — which is Part 6.
""",
    [
        _p13ex("j13-pr-tostring", "Give it a readable form", "Easy",
               "Write a `Point` class with `private final int x, y`, a constructor, and "
               "an override of `toString()` returning `(x, y)`. `main` prints the object "
               "directly, with no `.toString()` call.",
               """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point p = new Point(px, py);
        System.out.println(p);
        System.out.println("at " + p);""",
               [_case(f"{x} {y}", _nl(f"({x}, {y})", f"at ({x}, {y})"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["The signature must be exactly `public String toString()`.",
                "It must be `public`, because `Object`'s version is — anything "
                "narrower will not compile.",
                "`println(p)` calls it automatically, and so does string "
                "concatenation.",
                "Without the override you would see something like "
                "`Point@1b6d3586`."]),

        _p13ex("j13-pr-equals", "Compare by value", "Hard",
               "Write a `Point` class with `private final int x, y`, a constructor, and "
               "a correct override of `equals(Object o)` using the four steps. `main` "
               "builds two identical points and one different, and prints "
               "`a.equals(b)`, `a.equals(c)` and `a == b`.",
               """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Point)) {
            return false;
        }
        Point other = (Point) o;
        return x == other.x && y == other.y;
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = new Point(px, py);
        Point c = new Point(px + 1, py);
        System.out.println(a.equals(b));
        System.out.println(a.equals(c));
        System.out.println(a == b);""",
               [_case(f"{x} {y}", _nl("true", "false", "false"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["The parameter type must be `Object`, not `Point` — otherwise it is "
                "an overload and overrides nothing.",
                "Step 1 is the `this == o` fast path.",
                "Step 2 is `!(o instanceof Point)`, which also rejects `null`.",
                "Step 3 casts, which is now guaranteed safe.",
                "Step 4 compares the fields with `==`, since they are `int`s.",
                "`a == b` stays `false` — overriding `equals` does not change what "
                "`==` means."]),

        _p13ex("j13-pr-hashcode", "Keep the contract", "Hard",
               "Write a `Point` with `private final int x, y`, a constructor, a correct "
               "`equals`, and `hashCode()` returning `Objects.hash(x, y)`. `main` prints "
               "whether two identical points are equal and whether their hash codes "
               "match.",
               """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Point)) {
            return false;
        }
        Point other = (Point) o;
        return x == other.x && y == other.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = new Point(px, py);
        System.out.println(a.equals(b));
        System.out.println(a.hashCode() == b.hashCode());""",
               [_case(f"{x} {y}", _nl("true", "true"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["The contract is one-directional: equal objects MUST have equal hash "
                "codes.",
                "`Objects.hash(x, y)` builds one from the same fields `equals` uses "
                "— which is what keeps them in step.",
                "`java.util.Objects` is already imported by the `import "
                "java.util.*;` at the top.",
                "Both printed lines are `true` for every input.",
                "Overriding `equals` without `hashCode` compiles and passes this "
                "test's first line — and then loses objects inside a `HashMap`, "
                "which is Part 6."]),

        _p13ex("j13-pr-equals-wrong", "The overload that is not an override", "Hard",
               "Write a `Point` with `private final int x, y`, a constructor, and a "
               "method `public boolean equals(Point o)` — taking `Point`, **not** "
               "`Object`, and with no `@Override`. `main` compares two identical points "
               "both directly and through `Object` variables, showing the two calls "
               "disagree.",
               """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public boolean equals(Point o) {
        return x == o.x && y == o.y;
    }
}
""",
               """        int px = sc.nextInt();
        int py = sc.nextInt();
        Point a = new Point(px, py);
        Point b = new Point(px, py);
        Object oa = a;
        Object ob = b;
        System.out.println(a.equals(b));
        System.out.println(oa.equals(ob));""",
               [_case(f"{x} {y}", _nl("true", "false"))
                for (x, y) in ((3, 4), (0, 0), (-1, 2), (100, -100), (7, 7))],
               ["Taking `Point` rather than `Object` makes this an OVERLOAD; "
                "`Object.equals` is untouched.",
                "So `a.equals(b)` picks the overload and prints `true`.",
                "`oa.equals(ob)` is chosen at compile time from the declared type "
                "`Object`, so it reaches the inherited reference comparison and "
                "prints `false`.",
                "The two disagree, which is exactly how this bug reaches production "
                "— collections call the `Object` version.",
                "Adding `@Override` would have refused to compile. Write it every "
                "time."]),

        _p13ex("j13-pr-tostring-inherit", "toString down a hierarchy", "Medium",
               "Write `Shape` with `protected String name`, a constructor and an "
               "override of `toString()` returning `shape:<name>`. Then "
               "`Circle extends Shape` with `private int r`, a constructor, and an "
               "override of `toString()` returning `super.toString() + \":r\" + r`. "
               "`main` prints one of each.",
               """
class Shape {
    protected String name;

    Shape(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "shape:" + name;
    }
}

class Circle extends Shape {
    private int r;

    Circle(String name, int r) {
        super(name);
        this.r = r;
    }

    @Override
    public String toString() {
        return super.toString() + ":r" + r;
    }
}
""",
               """        String nm = sc.next();
        int rr = sc.nextInt();
        System.out.println(new Shape(nm));
        System.out.println(new Circle(nm, rr));""",
               [_case(f"{nm} {r}", _nl(f"shape:{nm}", f"shape:{nm}:r{r}"))
                for (nm, r) in (("box", 4), ("x", 0), ("round", 1), ("big", 12),
                                ("c", 7))],
               ["Both overrides must be `public String toString()`.",
                "`Circle` extends the parent's text with `super.toString()` rather "
                "than rebuilding it.",
                "A bare `toString()` there would recurse forever.",
                "`println` calls the override that matches the OBJECT, so the second "
                "line uses `Circle`'s.",
                "This is the standard way to build up a description down a "
                "hierarchy."]),
    ])


_PRACTICE[13] = [_P13_A, _P13_B, _P13_C, _P13_D, _P13_E]
