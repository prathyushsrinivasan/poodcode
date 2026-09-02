# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 13 — Inheritance and polymorphism.
#
# exec()'d by tools/java_course.py; appends one module to `_MODULES`.
#
# The pivot of Part 4: overriding is the first thing in this course that is
# resolved at RUN time rather than compile time, and the whole point of the
# module is to make that distinction concrete rather than slogan-shaped.
#
# `toString`, `equals` and `hashCode` live here rather than in module 12,
# because they are overrides — and teaching them before overriding would break
# the course's own "nothing before its module" rule.
# ---------------------------------------------------------------------------

_M13 = []


# --- 13.1 extends -----------------------------------------------------------

_M13.append(_jlesson(
    "m13-extends", "`extends` and the is-a relation",
    "One class built on another — and the question you must be able to answer yes to.",
    """
**Inheritance lets a class take everything another class has and add to it.**

```java
class Animal {
    String name;

    Animal(String name) { this.name = name; }

    String describe() { return name + " is an animal"; }
}

class Dog extends Animal {
    Dog(String name) { super(name); }         // more on super in 13.2

    String fetch() { return name + " fetches"; }   // `name` is inherited
}
```

A `Dog` now has **everything** an `Animal` has — the `name` field and the
`describe()` method — plus whatever it adds. `Animal` is the **superclass** (or
parent, or base); `Dog` is the **subclass** (or child, or derived).

**The test is "is-a".** Before writing `extends`, finish this sentence out loud:
*a Dog **is an** Animal.* If it sounds wrong, inheritance is the wrong tool.

```java
class Car extends Engine { }        // a Car is NOT an Engine — wrong
class Car { private Engine engine; } // a Car HAS an Engine — right
```

That second form is **composition**, and it is right far more often than
inheritance is. Module 14 makes the argument properly; for now, just notice that
"is-a" is a real test that fails frequently.

**What is inherited:** every `public` and `protected` member, and every
package-private one in the same package. **Constructors are not inherited** — a
subclass declares its own.

**`private` members are not accessible to a subclass.** They are still *there* —
a `Dog` object physically contains `Animal`'s private fields — but `Dog`'s code
cannot name them. That is what `protected` is for: visible to subclasses and to
the package, hidden from everyone else. Use it sparingly; a protected field is a
promise to every future subclass.

**Java has single inheritance.** A class may extend exactly one class. If you
want a type to fit into several categories, that is what interfaces are for
(module 14). The reason is the "diamond problem": with two parents defining the
same method, there is no principled answer to which one wins.

**Every class extends something.** Write no `extends` and you extend
`java.lang.Object`, which is where `toString()`, `equals()` and `hashCode()`
come from — lesson 13.5.
""",
    warmup=[
        _jq("`class Car extends Engine` — what is wrong with it?",
            ["A Car is not an Engine; it HAS one, so this should be composition",
             "Nothing — it is correct",
             "Engine must be abstract first",
             "Car cannot extend anything else afterwards, which is the only problem"],
            0,
            "The is-a test fails, so inheritance is modelling the wrong relationship. A field "
            "of type Engine says what is actually true."),
        _jq("A subclass can access which members of its superclass?",
            ["public and protected ones — not private ones",
             "All of them, including private",
             "Only public ones",
             "Only the ones it redeclares"],
            0,
            "Private members still exist inside the object; the subclass simply cannot name "
            "them. `protected` is the level that opens them to subclasses."),
    ],
    exercises=[
        _je("j13-ex-extends", "Build on another class",
            "`Dog` should inherit everything `Animal` has. Replace `____` with the "
            "class declaration.",
            _joop("class Animal {\n"
                  "    String name;\n"
                  "\n"
                  "    Animal(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "\n"
                  "    String describe() {\n"
                  '        return name + " is an animal";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    Dog(String name) {\n"
                  "        super(name);\n"
                  "    }\n"
                  "\n"
                  "    String fetch() {\n"
                  '        return name + " fetches";\n'
                  "    }\n"
                  "}",
                  "        Dog d = new Dog(sc.nextLine());\n"
                  "        System.out.println(d.describe());\n"
                  "        System.out.println(d.fetch());"),
            "class Dog extends Animal {",
            [_scase(s, _nl(f"{s} is an animal", f"{s} fetches"))
             for s in ("Rex", "Lady Bird", "x")],
            hints=["One keyword links a subclass to its superclass.",
                   "The subclass name comes first, then the keyword, then the parent.",
                   "`class Dog extends Animal {`"],
            difficulty="Intro"),

        _je("j13-ex-inherited", "Use what you inherited",
            "`Dog` has no `name` field of its own — it inherited one. Replace `____` "
            "with the body of `fetch`, which uses it.",
            _joop("class Animal {\n"
                  "    String name;\n"
                  "\n"
                  "    Animal(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    Dog(String name) {\n"
                  "        super(name);\n"
                  "    }\n"
                  "\n"
                  "    String fetch() {\n"
                  '        return name + " fetches the ball";\n'
                  "    }\n"
                  "}",
                  "        Dog d = new Dog(sc.nextLine());\n"
                  "        System.out.println(d.fetch());"),
            '        return name + " fetches the ball";',
            [_scase(s, f"{s} fetches the ball") for s in ("Rex", "Bo", "Good Dog")],
            hints=["`name` is in scope here even though `Dog` never declared it.",
                   "Glue it to the rest of the sentence with `+`.",
                   '`return name + " fetches the ball";`'],
            difficulty="Intro"),

        _jfix("j13-ex-private", "The field the subclass cannot see",
              "`Animal.name` is `private`, so `Dog` cannot name it and the program "
              "does not compile. Open it to subclasses — without making it public.",
              _joop("class Animal {\n"
                    "    private String name;\n"
                    "\n"
                    "    Animal(String name) {\n"
                    "        this.name = name;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    Dog(String name) {\n"
                    "        super(name);\n"
                    "    }\n"
                    "\n"
                    "    String bark() {\n"
                    '        return name + " barks";\n'
                    "    }\n"
                    "}",
                    "        Dog d = new Dog(sc.nextLine());\n"
                    "        System.out.println(d.bark());"),
              _joop("class Animal {\n"
                    "    protected String name;\n"
                    "\n"
                    "    Animal(String name) {\n"
                    "        this.name = name;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    Dog(String name) {\n"
                    "        super(name);\n"
                    "    }\n"
                    "\n"
                    "    String bark() {\n"
                    '        return name + " barks";\n'
                    "    }\n"
                    "}",
                    "        Dog d = new Dog(sc.nextLine());\n"
                    "        System.out.println(d.bark());"),
              [_scase(s, f"{s} barks") for s in ("Rex", "Bo", "Old Yeller")],
              hints=["The field exists inside every Dog — the subclass just cannot NAME it.",
                     "There is an access level between private and public for exactly this.",
                     "`protected String name;` — and note this is a promise to every future "
                     "subclass, so use it sparingly."]),

        _jch("j13-ex-chain", "Three levels deep", "Medium",
             "`Puppy` should extend `Dog`, which extends `Animal`. Give `Puppy` a "
             "constructor taking the name, and a `play()` method returning "
             "`<name> plays`. It should inherit `describe()` from `Animal` and "
             "`fetch()` from `Dog` without redeclaring either. Write the whole "
             "`Puppy` class where you see `____`.",
             _joop("class Animal {\n"
                   "    protected String name;\n"
                   "\n"
                   "    Animal(String name) {\n"
                   "        this.name = name;\n"
                   "    }\n"
                   "\n"
                   "    String describe() {\n"
                   '        return name + " is an animal";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Dog extends Animal {\n"
                   "    Dog(String name) {\n"
                   "        super(name);\n"
                   "    }\n"
                   "\n"
                   "    String fetch() {\n"
                   '        return name + " fetches";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Puppy extends Dog {\n"
                   "    Puppy(String name) {\n"
                   "        super(name);\n"
                   "    }\n"
                   "\n"
                   "    String play() {\n"
                   '        return name + " plays";\n'
                   "    }\n"
                   "}",
                   "        Puppy p = new Puppy(sc.nextLine());\n"
                   "        System.out.println(p.describe());\n"
                   "        System.out.println(p.fetch());\n"
                   "        System.out.println(p.play());"),
             "class Puppy extends Dog {\n"
             "    Puppy(String name) {\n"
             "        super(name);\n"
             "    }\n"
             "\n"
             "    String play() {\n"
             '        return name + " plays";\n'
             "    }\n"
             "}",
             [_scase(s, _nl(f"{s} is an animal", f"{s} fetches", f"{s} plays"))
              for s in ("Rex", "Bo", "Small Dog")],
             hints=["`class Puppy extends Dog` — inheritance chains as deep as you like.",
                    "Its constructor passes the name up with `super(name);`, which Dog's "
                    "constructor then passes up again.",
                    "`describe()` and `fetch()` are inherited through the chain — do not "
                    "redeclare them.",
                    "`name` is `protected` on `Animal`, so `Puppy` can use it directly."]),
    ],
    quiz=[
        _jq("Why does Java allow only one superclass?",
            ["The diamond problem — with two parents defining the same method there is no principled winner",
             "For performance",
             "It doesn't; Java allows several",
             "Because of the string pool"],
            0,
            "Multiple inheritance of *state* has no good answer. Interfaces (module 14) give "
            "you multiple inheritance of *type* without it."),
        _jq("A class with no `extends` clause extends…",
            ["java.lang.Object", "nothing", "itself", "Comparable"],
            0,
            "Which is where `toString()`, `equals()` and `hashCode()` come from — every "
            "object has them because every class inherits them."),
    ],
))

# --- 13.2 super -------------------------------------------------------------

_M13.append(_jlesson(
    "m13-super", "`super`",
    "Running the parent's constructor, and calling the parent's version of a method.",
    """
`super` has two jobs, and like `this` in module 11 they are unrelated.

**1. `super(...)` calls the superclass constructor.**

```java
class Dog extends Animal {
    private String breed;

    Dog(String name, String breed) {
        super(name);              // build the Animal part FIRST
        this.breed = breed;       // then the Dog part
    }
}
```

The superclass part of the object has to be initialised before the subclass part
can rely on it, so **`super(...)` must be the first statement** in the
constructor. (`this(...)` from module 11 has the same rule, and for the same
reason — which is why a constructor can use one or the other, never both.)

**Java inserts `super();` for you when you do not write it.** That is invisible
and fine — until the superclass has no no-argument constructor:

```java
class Animal {
    Animal(String name) { ... }        // no Animal() at all
}

class Cat extends Animal {
    Cat() { }                           // ERROR: implicit super() has no match
}
```

The error message — *"constructor Animal in class Animal cannot be applied to
given types"* pointing at a line that does not mention `Animal` — is baffling
until you know the rule. Write the `super(...)` call explicitly.

**The chain runs all the way up.** `new Puppy("Rex")` runs `Object`'s
constructor, then `Animal`'s, then `Dog`'s, then `Puppy`'s — outermost last. An
object is built from the inside out.

**2. `super.method()` calls the parent's version of a method** — the one you
have overridden:

```java
class Dog extends Animal {
    @Override
    String describe() {
        return super.describe() + ", specifically a dog";
    }
}
```

Without `super.`, writing `describe()` inside `describe()` would call itself
forever — infinite recursion and a `StackOverflowError`, which module 10 taught
you to recognise. `super.` is how you *extend* behaviour rather than replace it:
do what the parent did, then add.

Note the difference from `super(...)`: `super.describe()` is an ordinary method
call that can appear anywhere, as often as you like.
""",
    warmup=[
        _jq("Why must `super(...)` be the first statement of a constructor?",
            ["The superclass part of the object must be initialised before the subclass part uses it",
             "It is an arbitrary rule",
             "So the compiler can inline it",
             "It doesn't have to be"],
            0,
            "Objects are built from the inside out. The same reasoning forbids using both "
            "`super(...)` and `this(...)` in one constructor."),
        _jq("```java\n@Override String describe() { return describe() + \"!\"; }\n```",
            ["Infinite recursion — StackOverflowError",
             "Calls the parent version",
             "Compile error",
             "Returns the parent's string plus \"!\""],
            0,
            "A bare `describe()` is this object's own — the overriding one. You need "
            "`super.describe()` to reach the parent's."),
    ],
    exercises=[
        _je("j13-su-ctor", "Build the parent part first",
            "`Dog`'s constructor must hand the name up to `Animal` before setting "
            "its own field. Replace `____` with that call.",
            _joop("class Animal {\n"
                  "    protected String name;\n"
                  "\n"
                  "    Animal(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    private String breed;\n"
                  "\n"
                  "    Dog(String name, String breed) {\n"
                  "        super(name);\n"
                  "        this.breed = breed;\n"
                  "    }\n"
                  "\n"
                  "    String describe() {\n"
                  '        return name + " is a " + breed;\n'
                  "    }\n"
                  "}",
                  "        String n = sc.nextLine();\n"
                  "        String b = sc.nextLine();\n"
                  "        System.out.println(new Dog(n, b).describe());"),
            "        super(name);",
            [_s2case(n, b, f"{n} is a {b}")
             for (n, b) in (("Rex", "collie"), ("Bo", "portuguese water dog"),
                            ("x", "y"))],
            hints=["The superclass constructor takes the name.",
                   "It has to be the very first statement.",
                   "`super(name);`"]),

        _je("j13-su-method", "Extend, do not replace",
            "`Dog.describe()` should return whatever `Animal.describe()` returns, "
            "with `, specifically a dog` appended. Replace `____` with the "
            "expression — a bare `describe()` would call itself forever.",
            _joop("class Animal {\n"
                  "    protected String name;\n"
                  "\n"
                  "    Animal(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "\n"
                  "    String describe() {\n"
                  '        return name + " is an animal";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    Dog(String name) {\n"
                  "        super(name);\n"
                  "    }\n"
                  "\n"
                  "    String describe() {\n"
                  '        return super.describe() + ", specifically a dog";\n'
                  "    }\n"
                  "}",
                  "        System.out.println(new Dog(sc.nextLine()).describe());"),
            "super.describe()",
            [_scase(s, f"{s} is an animal, specifically a dog")
             for s in ("Rex", "Bo", "Good Dog")],
            hints=["You need the PARENT's version, not this object's.",
                   "One keyword, then a dot, then the method.",
                   "`super.describe()`"],
            difficulty="Medium"),

        _jfix("j13-su-implicit", "The constructor the compiler cannot find",
              "`Cat` does not compile: Java inserts an implicit `super();` and "
              "`Animal` has no no-argument constructor. Pass the name up explicitly.",
              _joop("class Animal {\n"
                    "    protected String name;\n"
                    "\n"
                    "    Animal(String name) {\n"
                    "        this.name = name;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Cat extends Animal {\n"
                    "    Cat(String name) {\n"
                    "        this.name = name;\n"
                    "    }\n"
                    "\n"
                    "    String speak() {\n"
                    '        return name + " meows";\n'
                    "    }\n"
                    "}",
                    "        System.out.println(new Cat(sc.nextLine()).speak());"),
              _joop("class Animal {\n"
                    "    protected String name;\n"
                    "\n"
                    "    Animal(String name) {\n"
                    "        this.name = name;\n"
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Cat extends Animal {\n"
                    "    Cat(String name) {\n"
                    "        super(name);\n"
                    "    }\n"
                    "\n"
                    "    String speak() {\n"
                    '        return name + " meows";\n'
                    "    }\n"
                    "}",
                    "        System.out.println(new Cat(sc.nextLine()).speak());"),
              [_scase(s, f"{s} meows") for s in ("Tom", "Cat Person", "z")],
              hints=["Assigning the inherited field works, but only AFTER the superclass "
                     "constructor has run — and there is no no-arg one to run.",
                     "Java is silently trying to call `super();`, which does not exist.",
                     "Replace `this.name = name;` with `super(name);`."],
              difficulty="Medium"),

        _jch("j13-su-both", "Both jobs at once", "Medium",
             "Write `Puppy extends Dog`. Its constructor takes a name and an age, "
             "passes the name up with `super(...)`, and stores the age. Its "
             "`describe()` should return `Dog`'s description with ` aged <n>` "
             "appended, using `super.describe()`. Write the whole `Puppy` class "
             "where you see `____`.",
             _joop("class Animal {\n"
                   "    protected String name;\n"
                   "\n"
                   "    Animal(String name) {\n"
                   "        this.name = name;\n"
                   "    }\n"
                   "\n"
                   "    String describe() {\n"
                   '        return name + " is an animal";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Dog extends Animal {\n"
                   "    Dog(String name) {\n"
                   "        super(name);\n"
                   "    }\n"
                   "\n"
                   "    String describe() {\n"
                   '        return super.describe() + ", a dog";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Puppy extends Dog {\n"
                   "    private int age;\n"
                   "\n"
                   "    Puppy(String name, int age) {\n"
                   "        super(name);\n"
                   "        this.age = age;\n"
                   "    }\n"
                   "\n"
                   "    String describe() {\n"
                   '        return super.describe() + " aged " + age;\n'
                   "    }\n"
                   "}",
                   "        String n = sc.nextLine();\n"
                   "        int a = sc.nextInt();\n"
                   "        System.out.println(new Puppy(n, a).describe());"),
             "class Puppy extends Dog {\n"
             "    private int age;\n"
             "\n"
             "    Puppy(String name, int age) {\n"
             "        super(name);\n"
             "        this.age = age;\n"
             "    }\n"
             "\n"
             "    String describe() {\n"
             '        return super.describe() + " aged " + age;\n'
             "    }\n"
             "}",
             [_lkcase(n, a, f"{n} is an animal, a dog aged {a}")
              for (n, a) in (("Rex", 2), ("Bo", 0), ("Small Dog", 11))],
             hints=["`super(name);` first, then `this.age = age;`.",
                    "`super.describe()` reaches Dog's version, which itself calls Animal's — "
                    "the whole chain composes.",
                    "The age is an `int`, so `+ age` converts it to text (module 6).",
                    "Note both jobs of `super` appear in one class, doing unrelated things."]),
    ],
    quiz=[
        _jq("Can a constructor contain both `this(...)` and `super(...)`?",
            ["No — each must be the first statement, so only one can be",
             "Yes, in that order",
             "Yes, in either order",
             "Only if the class is final"],
            0,
            "`this(...)` delegates to another constructor of the same class, which will itself "
            "call `super(...)`. The chain still reaches the parent exactly once."),
        _jq("In what order do constructors run for `new Puppy(...)`?",
            ["Object, then Animal, then Dog, then Puppy",
             "Puppy, then Dog, then Animal, then Object",
             "Only Puppy's",
             "Unspecified"],
            0,
            "Inside out. Each level's constructor is guaranteed a fully built parent before "
            "its own body runs."),
    ],
))

# --- 13.3 Overriding --------------------------------------------------------

_M13.append(_jlesson(
    "m13-override", "Overriding",
    "Replacing an inherited method — and the annotation that stops you missing.",
    """
**Overriding** is redeclaring an inherited method with the **same signature** so
that your version runs instead:

```java
class Animal {
    String speak() { return "..."; }
}

class Dog extends Animal {
    @Override
    String speak() { return "woof"; }        // same name, same parameters
}
```

**Overriding versus overloading** — the two words are nearly identical and mean
unrelated things. Module 9 introduced overloading; here is the contrast in full:

| | Overloading | Overriding |
|---|---|---|
| Signature | **different** parameters | **identical** parameters |
| Where | usually one class | subclass replaces superclass |
| Chosen | at **compile** time, from argument types | at **run** time, from the object's class |
| Return type | irrelevant to selection | must match (or be a subtype) |

That "run time" row is the important one, and lesson 13.4 is about what it
enables.

**`@Override` is optional and you should always write it.** It is an annotation
that asks the compiler to check you really are overriding something. Without it,
a typo silently creates a brand new method:

```java
class Dog extends Animal {
    String Speak() { return "woof"; }        // capital S — a NEW method
}

Animal a = new Dog();
a.speak();                                    // "..." — Animal's version. Silent bug.
```

With `@Override` on that line the compiler rejects it immediately. The same
protection catches a changed parameter list, which is the more common slip: you
meant to override `equals(Object)` and wrote `equals(Dog)`, which is an
*overload* and never gets called by anything.

**The rules an override must obey:**

- Same name and same parameter types. Different parameters is an overload.
- The return type must match, or be a subclass of the original's.
- It cannot be *less* accessible: a `public` method cannot be overridden as
  `private`. Widening is allowed.
- `static`, `private` and `final` methods cannot be overridden. `final` on a
  method exists precisely to forbid it.

**Fields are not overridden.** Redeclaring a field in a subclass *hides* the
parent's rather than replacing it, and which one you get depends on the
reference type instead of the object. It is confusing with no upside — do not
do it.
""",
    warmup=[
        _jq("A subclass writes `String Speak()` where the parent has `String speak()`. What happens?",
            ["A brand new method is created; calls through the parent type still run the parent's",
             "A compile error",
             "It overrides correctly — Java ignores case",
             "The parent method is deleted"],
            0,
            "Silent and easy to miss, which is exactly what `@Override` prevents: it makes "
            "the compiler check that something is really being overridden."),
        _jq("`equals(Dog other)` in a class meant to override `equals(Object o)` is…",
            ["an overload — it will never be called where equals is expected",
             "a correct override",
             "a compile error",
             "the same thing"],
            0,
            "Different parameter type means different signature means overload. This is the "
            "single most common `@Override` catch in real code."),
    ],
    exercises=[
        _je("j13-ov-basic", "Replace the parent's version",
            "`Dog.speak()` should return `woof` instead of the inherited `...`. "
            "Replace `____` with the whole overriding method, annotation included.",
            _joop("class Animal {\n"
                  "    String speak() {\n"
                  '        return "...";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    @Override\n"
                  "    String speak() {\n"
                  '        return "woof";\n'
                  "    }\n"
                  "}",
                  "        int k = sc.nextInt();\n"
                  "        Animal a = new Animal();\n"
                  "        Dog d = new Dog();\n"
                  "        for (int i = 0; i < k; i++) System.out.println(a.speak());\n"
                  "        for (int i = 0; i < k; i++) System.out.println(d.speak());"),
            "    @Override\n"
            "    String speak() {\n"
            '        return "woof";\n'
            "    }",
            [_case(k, _nl(*(["..."] * k + ["woof"] * k))) for k in (1, 2, 3)],
            hints=["Same name, same (empty) parameter list, same return type.",
                   "Put `@Override` on the line above so the compiler checks you.",
                   '`@Override String speak() { return "woof"; }`'],
            difficulty="Intro"),

        _je("j13-ov-annotation", "Ask the compiler to check",
            "This override is correct but unguarded. Replace `____` with the "
            "annotation that makes the compiler verify a method really does override "
            "something.",
            _joop("class Animal {\n"
                  "    String speak() {\n"
                  '        return "...";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Cat extends Animal {\n"
                  "    @Override\n"
                  "    String speak() {\n"
                  '        return "meow";\n'
                  "    }\n"
                  "}",
                  "        int k = sc.nextInt();\n"
                  "        Cat c = new Cat();\n"
                  "        for (int i = 0; i < k; i++) System.out.println(c.speak());"),
            "    @Override",
            [_case(k, _nl(*(["meow"] * k))) for k in (1, 3, 2)],
            hints=["It is an annotation, so it starts with `@`.",
                   "It goes on its own line, directly above the method.",
                   "`@Override`"],
            difficulty="Intro"),

        _jfix("j13-ov-typo", "The override that wasn't",
              "`Dog` was meant to override `speak()`, and `main` prints `...` instead "
              "of `woof`. The method name does not match, so a brand new method was "
              "created rather than an override. Fix it, and add the annotation that "
              "would have caught it.",
              _joop("class Animal {\n"
                    "    String speak() {\n"
                    '        return "...";\n'
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    String Speak() {\n"
                    '        return "woof";\n'
                    "    }\n"
                    "}",
                    "        int k = sc.nextInt();\n"
                    "        Animal a = new Dog();\n"
                    "        for (int i = 0; i < k; i++) System.out.println(a.speak());"),
              _joop("class Animal {\n"
                    "    String speak() {\n"
                    '        return "...";\n'
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    @Override\n"
                    "    String speak() {\n"
                    '        return "woof";\n'
                    "    }\n"
                    "}",
                    "        int k = sc.nextInt();\n"
                    "        Animal a = new Dog();\n"
                    "        for (int i = 0; i < k; i++) System.out.println(a.speak());"),
              [_case(k, _nl(*(["woof"] * k))) for k in (1, 2, 4)],
              hints=["Compare the two method names character by character.",
                     "`Speak` and `speak` are different methods entirely.",
                     "Rename it to `speak` and put `@Override` above it — with the annotation, "
                     "the original would not have compiled."],
              difficulty="Medium"),

        _jch("j13-ov-extend", "Override by extending", "Medium",
             "`LoudDog` should override `speak()` to return `Dog`'s answer followed "
             "by `!!!` — reusing the parent's implementation rather than repeating "
             "the word. Write the whole `LoudDog` class where you see `____`.",
             _joop("class Animal {\n"
                   "    String speak() {\n"
                   '        return "...";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Dog extends Animal {\n"
                   "    @Override\n"
                   "    String speak() {\n"
                   '        return "woof";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class LoudDog extends Dog {\n"
                   "    @Override\n"
                   "    String speak() {\n"
                   '        return super.speak() + "!!!";\n'
                   "    }\n"
                   "}",
                   "        int k = sc.nextInt();\n"
                   "        LoudDog l = new LoudDog();\n"
                   "        for (int i = 0; i < k; i++) System.out.println(l.speak());"),
             "class LoudDog extends Dog {\n"
             "    @Override\n"
             "    String speak() {\n"
             '        return super.speak() + "!!!";\n'
             "    }\n"
             "}",
             [_case(k, _nl(*(["woof!!!"] * k))) for k in (1, 2, 3)],
             hints=["`class LoudDog extends Dog`, with an overriding `speak()`.",
                    "`super.speak()` reaches Dog's version — a bare `speak()` would call "
                    "itself forever.",
                    'Append `"!!!"` to whatever the parent returned.',
                    "Do not hard-code `woof`: if Dog's answer changes, LoudDog should follow."]),
    ],
    quiz=[
        _jq("Overloading is resolved when, and overriding when?",
            ["Overloading at compile time from argument types; overriding at run time from the object's class",
             "Both at compile time",
             "Both at run time",
             "Overloading at run time; overriding at compile time"],
            0,
            "That single difference is what makes polymorphism possible, and it is the next "
            "lesson."),
        _jq("Which cannot be overridden?",
            ["static, private and final methods",
             "Only private methods",
             "Only final methods",
             "Any method can be overridden"],
            0,
            "`static` belongs to the class, `private` is invisible to subclasses, and `final` "
            "exists specifically to forbid it."),
    ],
))

# --- 13.4 Polymorphism ------------------------------------------------------

_M13.append(_jlesson(
    "m13-poly", "Polymorphism",
    "One reference type, many behaviours — decided by the object, not the variable.",
    """
Because overriding is resolved at **run time**, a variable of the parent type
can hold any subclass, and calling a method on it runs **the object's** version:

```java
Animal a = new Dog();       // legal: a Dog IS an Animal (upcasting)
System.out.println(a.speak());     // "woof" — Dog's version, not Animal's
```

The variable's type is `Animal`. The object is a `Dog`. **The object wins.**
That is **dynamic dispatch** (or late binding), and it is the whole payoff of
inheritance.

**Two different types are in play at once**, and keeping them separate is most
of understanding this:

- The **reference type** (`Animal`) decides *what you may call* — checked by the
  compiler.
- The **object type** (`Dog`) decides *which implementation runs* — decided at
  run time.

So `a.fetch()` does not compile even though the object is a `Dog`, because
`Animal` has no `fetch()`. The compiler only knows what the variable claims.

**Where it earns its keep: an array of the parent type.**

```java
Animal[] zoo = { new Dog(), new Cat(), new Dog() };
for (Animal x : zoo) System.out.println(x.speak());   // woof, meow, woof
```

One loop, three behaviours, and **no `if` on the type anywhere**. Add a `Sheep`
class tomorrow and this loop does not change — that is the property being bought,
and it is why polymorphism is worth the machinery. Code that switches on a type
tag is code you rewrite every time a case is added.

**Upcasting is free and always safe** — a `Dog` is an `Animal`, so no cast is
needed. **Downcasting is a claim you are making** and needs a check:

```java
Animal a = new Cat();
Dog d = (Dog) a;                  // compiles, then throws ClassCastException

if (a instanceof Dog) {           // ask first
    Dog d2 = (Dog) a;
}

if (a instanceof Dog d3) {        // Java 16+: test and bind in one step
    System.out.println(d3.fetch());
}
```

**Needing to downcast is usually a design smell.** If you find yourself writing
`if (x instanceof Dog) ... else if (x instanceof Cat) ...`, the behaviour you
are switching on probably belongs as an overridden method on the classes
themselves. Polymorphism exists to delete that chain.
""",
    warmup=[
        _jq("```java\nAnimal a = new Dog();   // Dog overrides speak() as \"woof\"\nSystem.out.println(a.speak());\n```",
            ["woof — the object's type decides which version runs",
             "... — the variable's type decides",
             "It does not compile",
             "ClassCastException"],
            0,
            "Dynamic dispatch: the reference type gates what you may CALL, the object type "
            "decides what actually RUNS."),
        _jq("With `Animal a = new Dog();`, why does `a.fetch()` not compile?",
            ["The compiler only knows `a` is an Animal, and Animal has no fetch()",
             "Because fetch() is private",
             "It does compile",
             "Because Dog is not an Animal"],
            0,
            "The reference type is the contract the compiler checks. Reaching Dog-only "
            "behaviour needs a downcast — and usually means the design should be reconsidered."),
    ],
    exercises=[
        _je("j13-po-upcast", "A parent-typed variable",
            "Hold a `Dog` in an `Animal` variable and call `speak()` on it — the "
            "Dog's version must run. Replace `____` with the declaration.",
            _joop("class Animal {\n"
                  "    String speak() {\n"
                  '        return "...";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    @Override\n"
                  "    String speak() {\n"
                  '        return "woof";\n'
                  "    }\n"
                  "}",
                  "        int k = sc.nextInt();\n"
                  "        Animal a = new Dog();\n"
                  "        for (int i = 0; i < k; i++) System.out.println(a.speak());"),
            "        Animal a = new Dog();",
            [_case(k, _nl(*(["woof"] * k))) for k in (1, 2, 3)],
            hints=["The variable's type is the parent; the object is the child.",
                   "No cast is needed — upcasting is always safe.",
                   "`Animal a = new Dog();`"],
            difficulty="Intro"),

        _je("j13-po-array", "One loop, many behaviours",
            "`zoo` holds a mix of animals. Replace `____` with the loop that prints "
            "what each one says — with no `if` on the type.",
            _joop("class Animal {\n"
                  "    String speak() {\n"
                  '        return "...";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Dog extends Animal {\n"
                  "    @Override\n"
                  "    String speak() {\n"
                  '        return "woof";\n'
                  "    }\n"
                  "}\n"
                  "\n"
                  "class Cat extends Animal {\n"
                  "    @Override\n"
                  "    String speak() {\n"
                  '        return "meow";\n'
                  "    }\n"
                  "}",
                  "        int n = sc.nextInt();\n"
                  "        Animal[] zoo = new Animal[n];\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            int t = sc.nextInt();\n"
                  "            if (t == 1) zoo[i] = new Dog();\n"
                  "            else if (t == 2) zoo[i] = new Cat();\n"
                  "            else zoo[i] = new Animal();\n"
                  "        }\n"
                  "        for (Animal x : zoo) System.out.println(x.speak());"),
            "        for (Animal x : zoo) System.out.println(x.speak());",
            [_case(f"{len(ts)}\n" + "\n".join(str(t) for t in ts),
                   _nl(*[{1: "woof", 2: "meow"}.get(t, "...") for t in ts]))
             for ts in ([1, 2, 1], [3], [2, 2], [1, 3, 2, 1])],
            hints=["An enhanced `for` over `Animal[]` gives you each element as an `Animal`.",
                   "Calling `speak()` runs each object's own version automatically.",
                   "`for (Animal x : zoo) System.out.println(x.speak());`"],
            difficulty="Medium"),

        _jfix("j13-po-refType", "The compiler only knows the variable",
              "This holds a `Dog` in an `Animal` variable and then calls `fetch()`, "
              "which `Animal` does not have — so it does not compile. Fix it by "
              "giving the variable the type that actually offers `fetch()`.",
              _joop("class Animal {\n"
                    "    String speak() {\n"
                    '        return "...";\n'
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    @Override\n"
                    "    String speak() {\n"
                    '        return "woof";\n'
                    "    }\n"
                    "\n"
                    "    String fetch() {\n"
                    '        return "fetching";\n'
                    "    }\n"
                    "}",
                    "        int k = sc.nextInt();\n"
                    "        Animal a = new Dog();\n"
                    "        for (int i = 0; i < k; i++) System.out.println(a.fetch());"),
              _joop("class Animal {\n"
                    "    String speak() {\n"
                    '        return "...";\n'
                    "    }\n"
                    "}\n"
                    "\n"
                    "class Dog extends Animal {\n"
                    "    @Override\n"
                    "    String speak() {\n"
                    '        return "woof";\n'
                    "    }\n"
                    "\n"
                    "    String fetch() {\n"
                    '        return "fetching";\n'
                    "    }\n"
                    "}",
                    "        int k = sc.nextInt();\n"
                    "        Dog a = new Dog();\n"
                    "        for (int i = 0; i < k; i++) System.out.println(a.fetch());"),
              [_case(k, _nl(*(["fetching"] * k))) for k in (1, 2, 3)],
              hints=["The object is a Dog, but the compiler only sees what the variable claims.",
                     "`fetch()` is Dog-only, so the variable has to be a Dog.",
                     "`Dog a = new Dog();` — a downcast `((Dog) a).fetch()` would also work, "
                     "but needing one here just means the variable was declared too widely."],
              difficulty="Medium"),

        _jch("j13-po-count", "Ask what it really is", "Hard",
             "Build the `zoo` exactly as before, then print two lines: every "
             "animal's `speak()` (one per line), and then how many of them are "
             "`Dog`s — using `instanceof`. Write the whole block where you see "
             "`____`.",
             _joop("class Animal {\n"
                   "    String speak() {\n"
                   '        return "...";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Dog extends Animal {\n"
                   "    @Override\n"
                   "    String speak() {\n"
                   '        return "woof";\n'
                   "    }\n"
                   "}\n"
                   "\n"
                   "class Cat extends Animal {\n"
                   "    @Override\n"
                   "    String speak() {\n"
                   '        return "meow";\n'
                   "    }\n"
                   "}",
                   "        int n = sc.nextInt();\n"
                   "        Animal[] zoo = new Animal[n];\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            int t = sc.nextInt();\n"
                   "            if (t == 1) zoo[i] = new Dog();\n"
                   "            else if (t == 2) zoo[i] = new Cat();\n"
                   "            else zoo[i] = new Animal();\n"
                   "        }\n"
                   "        for (Animal x : zoo) System.out.println(x.speak());\n"
                   "        int dogs = 0;\n"
                   "        for (Animal x : zoo) {\n"
                   "            if (x instanceof Dog) dogs++;\n"
                   "        }\n"
                   '        System.out.println("dogs=" + dogs);'),
             "        for (Animal x : zoo) System.out.println(x.speak());\n"
             "        int dogs = 0;\n"
             "        for (Animal x : zoo) {\n"
             "            if (x instanceof Dog) dogs++;\n"
             "        }\n"
             '        System.out.println("dogs=" + dogs);',
             [_case(f"{len(ts)}\n" + "\n".join(str(t) for t in ts),
                    _nl(*([{1: "woof", 2: "meow"}.get(t, "...") for t in ts]
                          + [f"dogs={sum(1 for t in ts if t == 1)}"])))
              for ts in ([1, 2, 1], [3], [2, 2], [1, 1, 1, 3])],
             hints=["First loop: `speak()` needs no type test at all — that is the point of "
                    "polymorphism.",
                    "Second loop: `x instanceof Dog` is true when the OBJECT is a Dog.",
                    "A plain `Animal` is not a `Dog`, so it does not count.",
                    "Notice the asymmetry: printing needed no type check, counting did. If you "
                    "ever find yourself `instanceof`-ing to decide BEHAVIOUR, that behaviour "
                    "wants to be an overridden method instead."]),
    ],
    quiz=[
        _jq("What does polymorphism let you delete from your code?",
            ["Chains of `if (x instanceof T)` that pick behaviour by type",
             "Constructors",
             "All type declarations",
             "The need for arrays"],
            0,
            "Each subclass carries its own version, so adding a type does not mean editing "
            "every caller. That is the property being bought."),
        _jq("`Animal a = new Cat(); Dog d = (Dog) a;` does what?",
            ["Compiles, then throws ClassCastException at run time",
             "Compile error",
             "Works fine",
             "Returns null"],
            0,
            "The compiler allows the claim because a Dog *could* have been there; the JVM "
            "checks it and finds a Cat. Guard with `instanceof` first."),
    ],
))

# --- 13.5 Object and its methods -------------------------------------------

_M13.append(_jlesson(
    "m13-object", "`Object`, `toString` and `equals`",
    "The three inherited methods you are expected to override, and the contract binding two of them.",
    """
Every class extends `Object`, so every object already has these — and the
defaults are rarely what you want.

**`toString()`** is called automatically whenever an object is printed or
concatenated. The default is the `ClassName@hashcode` form you met with arrays
in module 1:

```java
class Point {
    private final int x, y;

    @Override
    public String toString() {
        return "(" + x + ", " + y + ")";
    }
}

System.out.println(p);              // (3, 4) — println calls toString for you
```

Overriding it costs three lines and pays for itself the first time you debug.
Note `public` — `Object.toString()` is public, and an override can never be less
accessible (module 13.3).

**`equals(Object o)`** is `==` by default: two objects are equal only if they
are the *same object*. For a value type that is almost never right — module 6's
`String` lesson, now for your own classes.

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;                   // same object: done
    if (!(o instanceof Point)) return false;      // wrong type (also covers null)
    Point other = (Point) o;
    return x == other.x && y == other.y;          // compare the fields
}
```

Four steps, always the same. The parameter type must be **`Object`** — writing
`equals(Point o)` is an overload that nothing will ever call, which is precisely
the `@Override` catch from lesson 13.3.

**`hashCode()` must agree with `equals`.** The contract is one sentence:

> **If two objects are equal, they must have the same hash code.**

(The converse is not required — unequal objects may collide.) Break it and your
objects fail silently in a `HashMap` or `HashSet`: you put one in, ask for it
back, and it is not there, because the map looked in the wrong bucket. That is
why `equals` and `hashCode` are always overridden **together** — a class with
one and not the other is a bug waiting for its first hash-based collection.

```java
@Override
public int hashCode() {
    return Objects.hash(x, y);       // uses exactly the fields equals uses
}
```

**`getClass()`** returns the runtime class, and `getClass().getSimpleName()` is a
handy way to see what an object really is — useful for exactly the "is the
object type or the reference type deciding?" question from lesson 13.4.

Collections arrive in Part 6 of the roadmap, and they lean on `equals` and
`hashCode` constantly. Learning the contract now is what makes them behave then.
""",
    warmup=[
        _jq("`System.out.println(myObject)` on a class with no `toString` override prints…",
            ["something like `Point@1b6d3586`",
             "the field values",
             "an empty line",
             "a compile error"],
            0,
            "`Object.toString()` gives the class name and a hash. Exactly the `[I@1b6d3586` "
            "problem arrays had in module 1."),
        _jq("Why must `equals` take an `Object` parameter rather than the class's own type?",
            ["`equals(MyType)` is an overload, not an override, so nothing calls it",
             "For performance",
             "It doesn't matter",
             "Because Object is abstract"],
            0,
            "Signatures must match exactly to override. `@Override` catches this instantly, "
            "which is the strongest argument for always writing it."),
    ],
    exercises=[
        _je("j13-ob-tostring", "Make it printable",
            "`Point` should print as `(x, y)`. Replace `____` with the override — "
            "note it has to be `public`.",
            _joop("class Point {\n"
                  "    private final int x;\n"
                  "    private final int y;\n"
                  "\n"
                  "    Point(int x, int y) {\n"
                  "        this.x = x;\n"
                  "        this.y = y;\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public String toString() {\n"
                  '        return "(" + x + ", " + y + ")";\n'
                  "    }\n"
                  "}",
                  "        Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  "        System.out.println(p);"),
            "    @Override\n"
            "    public String toString() {\n"
            '        return "(" + x + ", " + y + ")";\n'
            "    }",
            [_case(f"{x}\n{y}", f"({x}, {y})") for (x, y) in ((3, 4), (0, 0), (-1, 7))],
            hints=["The signature is `public String toString()` — no parameters.",
                   "It must be `public`, because `Object.toString()` is, and an override "
                   "cannot narrow access.",
                   'Build the text with `+`: `"(" + x + ", " + y + ")"`.'],
            difficulty="Medium"),

        _je("j13-ob-equals", "Compare by value",
            "`Point.equals` should say two points are equal when their coordinates "
            "match. The first three lines are written; replace `____` with the field "
            "comparison.",
            _joop("class Point {\n"
                  "    private final int x;\n"
                  "    private final int y;\n"
                  "\n"
                  "    Point(int x, int y) {\n"
                  "        this.x = x;\n"
                  "        this.y = y;\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public boolean equals(Object o) {\n"
                  "        if (this == o) return true;\n"
                  "        if (!(o instanceof Point)) return false;\n"
                  "        Point other = (Point) o;\n"
                  "        return x == other.x && y == other.y;\n"
                  "    }\n"
                  "}",
                  "        Point a = new Point(sc.nextInt(), sc.nextInt());\n"
                  "        Point b = new Point(sc.nextInt(), sc.nextInt());\n"
                  "        System.out.println(a == b);\n"
                  "        System.out.println(a.equals(b));"),
            "        return x == other.x && y == other.y;",
            [_case(f"{ax}\n{ay}\n{bx}\n{by}",
                   _nl("false", _jbool(ax == bx and ay == by)))
             for (ax, ay, bx, by) in ((3, 4, 3, 4), (3, 4, 3, 5), (0, 0, 0, 0),
                                      (-1, 2, -1, 2))],
            hints=["`other` is already the cast Point — compare both fields.",
                   "`private` is per-class, so reading `other.x` is legal here (module 12).",
                   "`return x == other.x && y == other.y;` — and note `a == b` stays false "
                   "even for equal points, because they are different objects."],
            difficulty="Hard"),

        _jfix("j13-ob-overload", "equals that is never called",
              "`Point.equals` takes a `Point`, which makes it an **overload** rather "
              "than an override — so the `Object`-typed call in `main` still uses "
              "`Object`'s identity version and prints `false` for equal points. Fix "
              "the signature.",
              _joop("class Point {\n"
                    "    private final int x;\n"
                    "    private final int y;\n"
                    "\n"
                    "    Point(int x, int y) {\n"
                    "        this.x = x;\n"
                    "        this.y = y;\n"
                    "    }\n"
                    "\n"
                    "    public boolean equals(Point o) {\n"
                    "        return x == o.x && y == o.y;\n"
                    "    }\n"
                    "}",
                    "        Point a = new Point(sc.nextInt(), sc.nextInt());\n"
                    "        Object b = new Point(sc.nextInt(), sc.nextInt());\n"
                    "        System.out.println(a.equals(b));"),
              _joop("class Point {\n"
                    "    private final int x;\n"
                    "    private final int y;\n"
                    "\n"
                    "    Point(int x, int y) {\n"
                    "        this.x = x;\n"
                    "        this.y = y;\n"
                    "    }\n"
                    "\n"
                    "    @Override\n"
                    "    public boolean equals(Object o) {\n"
                    "        if (this == o) return true;\n"
                    "        if (!(o instanceof Point)) return false;\n"
                    "        Point other = (Point) o;\n"
                    "        return x == other.x && y == other.y;\n"
                    "    }\n"
                    "}",
                    "        Point a = new Point(sc.nextInt(), sc.nextInt());\n"
                    "        Object b = new Point(sc.nextInt(), sc.nextInt());\n"
                    "        System.out.println(a.equals(b));"),
              [_case(f"{ax}\n{ay}\n{bx}\n{by}", _jbool(ax == bx and ay == by))
               for (ax, ay, bx, by) in ((3, 4, 3, 4), (3, 4, 9, 9), (0, 0, 0, 0))],
              hints=["`b` is declared as `Object`, so the compiler picks `equals(Object)` — "
                     "which is Object's own.",
                     "The parameter type must be exactly `Object` to override.",
                     "Write the four-step form: identity check, `instanceof`, cast, compare — "
                     "and add `@Override`, which would have rejected the original."],
              difficulty="Hard"),

        _jch("j13-ob-full", "toString, equals and hashCode together", "Hard",
             "Give `Point` all three overrides: `toString()` returning `(x, y)`, "
             "`equals(Object)` comparing both coordinates, and `hashCode()` built "
             "with `Objects.hash(x, y)` so it agrees with `equals`. Write all three "
             "where you see `____`.",
             _joop("class Point {\n"
                   "    private final int x;\n"
                   "    private final int y;\n"
                   "\n"
                   "    Point(int x, int y) {\n"
                   "        this.x = x;\n"
                   "        this.y = y;\n"
                   "    }\n"
                   "\n"
                   "    @Override\n"
                   "    public String toString() {\n"
                   '        return "(" + x + ", " + y + ")";\n'
                   "    }\n"
                   "\n"
                   "    @Override\n"
                   "    public boolean equals(Object o) {\n"
                   "        if (this == o) return true;\n"
                   "        if (!(o instanceof Point)) return false;\n"
                   "        Point other = (Point) o;\n"
                   "        return x == other.x && y == other.y;\n"
                   "    }\n"
                   "\n"
                   "    @Override\n"
                   "    public int hashCode() {\n"
                   "        return Objects.hash(x, y);\n"
                   "    }\n"
                   "}",
                   "        Point a = new Point(sc.nextInt(), sc.nextInt());\n"
                   "        Point b = new Point(sc.nextInt(), sc.nextInt());\n"
                   "        System.out.println(a);\n"
                   "        System.out.println(b);\n"
                   "        System.out.println(a.equals(b));\n"
                   "        System.out.println(a.hashCode() == b.hashCode());"),
             "    @Override\n"
             "    public String toString() {\n"
             '        return "(" + x + ", " + y + ")";\n'
             "    }\n"
             "\n"
             "    @Override\n"
             "    public boolean equals(Object o) {\n"
             "        if (this == o) return true;\n"
             "        if (!(o instanceof Point)) return false;\n"
             "        Point other = (Point) o;\n"
             "        return x == other.x && y == other.y;\n"
             "    }\n"
             "\n"
             "    @Override\n"
             "    public int hashCode() {\n"
             "        return Objects.hash(x, y);\n"
             "    }",
             [_case(f"{ax}\n{ay}\n{bx}\n{by}",
                    _nl(f"({ax}, {ay})", f"({bx}, {by})",
                        _jbool(ax == bx and ay == by),
                        _jbool(ax == bx and ay == by)))
              for (ax, ay, bx, by) in ((3, 4, 3, 4), (3, 4, 5, 6), (0, 0, 0, 0),
                                       (-2, 7, -2, 7))],
             hints=["Three overrides, each with `@Override` and each `public`.",
                    "`equals` must take `Object` — the four steps are identity, `instanceof`, "
                    "cast, compare.",
                    "`hashCode` must use exactly the fields `equals` uses, or the contract "
                    "breaks: `Objects.hash(x, y)`.",
                    "The last printed line checks the contract directly — equal points must "
                    "produce equal hash codes.",
                    "`Objects` (plural) comes from `java.util`, already imported."]),
    ],
    quiz=[
        _jq("State the equals/hashCode contract.",
            ["Equal objects must have equal hash codes (the converse is not required)",
             "Equal hash codes mean equal objects",
             "hashCode must be unique per object",
             "They are unrelated"],
            0,
            "Collisions are allowed and expected; what is forbidden is two equal objects "
            "landing in different buckets, which is what breaks HashMap lookups."),
        _jq("What goes wrong if you override `equals` but not `hashCode`?",
            ["Objects vanish in a HashMap or HashSet — you insert one and cannot find it",
             "It fails to compile",
             "equals stops working",
             "Nothing"],
            0,
            "The map hashes to one bucket on insert and a different one on lookup. Silent, "
            "and a classic interview question."),
    ],
))


# --- Capstone ---------------------------------------------------------------

def _m13_shapes(items):
    """items: list of (kind, a, b). kind 1 = Rect(a,b), 2 = Square(a), 3 = Shape."""
    out = []
    total = 0
    squares = 0
    for (kind, a, b) in items:
        if kind == 1:
            area = a * b
            out.append(f"Rect {a}x{b} area={area}")
        elif kind == 2:
            area = a * a
            out.append(f"Square {a}x{a} area={area}")
            squares += 1
        else:
            area = 0
            out.append("Shape area=0")
        total += area
    out.append(f"total={total}")
    out.append(f"squares={squares}")
    return _nl(*out)


def _m13_case(items):
    lines = [str(len(items))]
    for (kind, a, b) in items:
        lines.append(f"{kind} {a} {b}")
    return _case("\n".join(lines), _m13_shapes(items))


_M13_CAP = _jcap(
    "Shape hierarchy",
    """
The canonical polymorphism exercise, with every part of module 13 in it.

Read `n`, then `n` lines of `kind a b`:

| kind | Build |
|---|---|
| `1` | `Rect(a, b)` |
| `2` | `Square(a)` — ignore `b` |
| `3` | a plain `Shape` — ignore both |

Store them all in a `Shape[]`, print each one's `toString()` on its own line,
then two summary lines:

```
total=<the sum of every shape's area>
squares=<how many of them are Squares>
```

The classes:

| Class | Members |
|---|---|
| `Shape` | `area()` returning `0`; `toString()` returning `Shape area=0` |
| `Rect extends Shape` | `private final int w, h`; overrides `area()` as `w * h` and `toString()` as `Rect <w>x<h> area=<area>` |
| `Square extends Rect` | constructor takes one side and calls `super(side, side)`; overrides `toString()` as `Square <s>x<s> area=<area>` — but **does not** override `area()` |

Three things the hidden cases are checking:

- **`Square` inherits `area()`.** It is a `Rect` with equal sides, so
  `super(side, side)` is all it needs. Re-implementing `area()` would work and
  would also be the wrong instinct.
- **The print loop has no type test.** One `for (Shape s : shapes)` calling
  `s.toString()` — dynamic dispatch picks the right one. `println(s)` calls it
  for you.
- **`squares` needs `instanceof`,** because counting by type genuinely is a
  question about types. Note the asymmetry with the line above it: printing is
  behaviour and belongs to the object; counting a kind is not.

Because `Square extends Rect`, a `Square` **is** a `Rect` — so a naive
`instanceof Rect` count would include the squares. Count `instanceof Square`.
""",
    _jch("j13-cap-shapes", "Shape hierarchy", "Hard",
         "Write the three classes where you see `____`. `main` is already written "
         "and builds the array, prints each shape, and prints the two summaries.",
         _joop("class Shape {\n"
               "    int area() {\n"
               "        return 0;\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    public String toString() {\n"
               '        return "Shape area=0";\n'
               "    }\n"
               "}\n"
               "\n"
               "class Rect extends Shape {\n"
               "    protected final int w;\n"
               "    protected final int h;\n"
               "\n"
               "    Rect(int w, int h) {\n"
               "        this.w = w;\n"
               "        this.h = h;\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    int area() {\n"
               "        return w * h;\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    public String toString() {\n"
               '        return "Rect " + w + "x" + h + " area=" + area();\n'
               "    }\n"
               "}\n"
               "\n"
               "class Square extends Rect {\n"
               "    Square(int side) {\n"
               "        super(side, side);\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    public String toString() {\n"
               '        return "Square " + w + "x" + h + " area=" + area();\n'
               "    }\n"
               "}",
               "        int n = sc.nextInt();\n"
               "        Shape[] shapes = new Shape[n];\n"
               "        for (int i = 0; i < n; i++) {\n"
               "            int kind = sc.nextInt();\n"
               "            int a = sc.nextInt();\n"
               "            int b = sc.nextInt();\n"
               "            if (kind == 1) shapes[i] = new Rect(a, b);\n"
               "            else if (kind == 2) shapes[i] = new Square(a);\n"
               "            else shapes[i] = new Shape();\n"
               "        }\n"
               "        int total = 0;\n"
               "        int squares = 0;\n"
               "        for (Shape s : shapes) {\n"
               "            System.out.println(s);\n"
               "            total += s.area();\n"
               "            if (s instanceof Square) squares++;\n"
               "        }\n"
               '        System.out.println("total=" + total);\n'
               '        System.out.println("squares=" + squares);'),
         "class Shape {\n"
         "    int area() {\n"
         "        return 0;\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    public String toString() {\n"
         '        return "Shape area=0";\n'
         "    }\n"
         "}\n"
         "\n"
         "class Rect extends Shape {\n"
         "    protected final int w;\n"
         "    protected final int h;\n"
         "\n"
         "    Rect(int w, int h) {\n"
         "        this.w = w;\n"
         "        this.h = h;\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    int area() {\n"
         "        return w * h;\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    public String toString() {\n"
         '        return "Rect " + w + "x" + h + " area=" + area();\n'
         "    }\n"
         "}\n"
         "\n"
         "class Square extends Rect {\n"
         "    Square(int side) {\n"
         "        super(side, side);\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    public String toString() {\n"
         '        return "Square " + w + "x" + h + " area=" + area();\n'
         "    }\n"
         "}",
         [_m13_case(items)
          for items in ([(1, 3, 4), (2, 5, 0), (3, 0, 0)],
                        [(2, 2, 9)],
                        [(1, 1, 1), (1, 2, 3), (2, 4, 4)],
                        [(3, 7, 7), (3, 1, 1)],
                        [(2, 1, 0), (2, 2, 0), (1, 10, 10)])],
         hints=["`Shape` is the base: `area()` returns 0 and `toString()` is the fixed "
                "string.",
                "`Rect` stores `w` and `h` as `protected final` so `Square` can read them in "
                "its own `toString()`.",
                "`Square`'s constructor is just `super(side, side);` — and it must NOT "
                "override `area()`, because Rect's version is already right.",
                "Every `toString()` is `public` (Object's is), while `area()` is "
                "package-private — an override may widen access but never narrow it.",
                "`System.out.println(s)` calls `toString()` for you, and dynamic dispatch "
                "picks the right one with no type test.",
                "Count `instanceof Square`, not `instanceof Rect` — a Square IS a Rect, so "
                "the wrong test would over-count."]),
    example_io="stdin:  3\n        1 3 4\n        2 5 0\n        3 0 0\n\n"
               "stdout: Rect 3x4 area=12\n        Square 5x5 area=25\n        Shape area=0\n"
               "        total=37\n        squares=1",
    rubric=[
        "`Square extends Rect` and inherits `area()` rather than reimplementing it.",
        "`Square`'s constructor delegates with `super(side, side)`.",
        "Every override carries `@Override`, and each `toString()` is `public`.",
        "The print loop contains no type test — dispatch picks the right `toString()`.",
        "`squares` counts `instanceof Square`, so a plain Rect is not miscounted.",
        "A plain `Shape` contributes 0 to the total and prints `Shape area=0`.",
    ],
)


_MODULES.append(_jmod(
    13, 4, "Object-oriented programming",
    "Inheritance and polymorphism",
    "Build one class on another, replace inherited behaviour, and let the object — "
    "not the variable — decide which version runs. Plus the three `Object` methods "
    "you are expected to override.",
    """
This is the pivot of Part 4, because it introduces the first thing in the whole
course that is decided at **run time** rather than compile time.

Overloading (module 9) picks a method from the argument types the compiler can
see. **Overriding picks one from the class of the object that actually exists**,
which is what lets a single loop over `Shape[]` do the right thing for a
rectangle, a square and a plain shape without a single `if` on the type. Adding
a new subclass tomorrow does not touch that loop — that property is the entire
return on inheritance's complexity.

The module is also honest about the costs. `extends` is the wrong tool more
often than it is the right one — the "is-a" test fails constantly, and module 14
argues for composition. And a chain of `instanceof` checks choosing behaviour is
a sign the behaviour belongs on the classes instead.

`toString`, `equals` and `hashCode` land here rather than in module 12 because
they are overrides, and the equals/hashCode contract is the thing that makes
your classes work in the collections coming in Part 6.
""",
    _M13,
    capstone=_M13_CAP,
    objectives=[
        "Use `extends`, and apply the is-a test before reaching for it.",
        "Choose between `private`, `protected` and `public` for a member a subclass may need.",
        "Use `super(...)` to build the parent part and `super.m()` to extend its behaviour.",
        "Override a method correctly, and say why `@Override` should always be written.",
        "State the difference between overloading and overriding, including when each is resolved.",
        "Explain dynamic dispatch, and predict which implementation runs for a parent-typed variable.",
        "Override `toString`, `equals` and `hashCode`, and state the contract binding the last two.",
    ],
    why="Polymorphism is why object-oriented code can be extended without being edited, "
        "and the equals/hashCode contract is what makes your own types work inside "
        "HashMap and HashSet. Both are asked about in almost every Java interview.",
    est_minutes=330,
    glossary=[
        _jg("superclass", "The class being extended — also parent or base."),
        _jg("subclass", "The class doing the extending — also child or derived. It gets "
                        "everything non-private, plus its own additions."),
        _jg("is-a test", "Say 'a Dog is an Animal' out loud before writing `extends`. If it "
                         "sounds wrong, use composition."),
        _jg("protected", "Visible to subclasses and to the package. A promise to every future "
                         "subclass, so use it sparingly."),
        _jg("super(...)", "A call to the superclass constructor. Must be the first statement; "
                          "inserted implicitly as `super()` when omitted."),
        _jg("super.method()", "The superclass's version of an overridden method — how you "
                              "extend behaviour instead of replacing it."),
        _jg("overriding", "Redeclaring an inherited method with the SAME signature. Resolved "
                          "at run time from the object's class."),
        _jg("@Override", "An annotation asking the compiler to verify a method really "
                         "overrides something. Optional; always write it."),
        _jg("polymorphism", "One reference type standing for many object types, each running "
                            "its own overridden implementation."),
        _jg("dynamic dispatch", "Choosing the implementation at run time from the object's "
                                "actual class rather than the variable's declared type."),
        _jg("upcasting", "Treating a subclass object as its supertype. Always safe, never "
                         "needs a cast."),
        _jg("downcasting", "Claiming a supertype reference is really a subtype. Checked at "
                           "run time; guard it with `instanceof`."),
        _jg("equals/hashCode contract", "Equal objects must have equal hash codes. Break it "
                                        "and hash-based collections silently lose your objects."),
    ],
    cheatsheet="""
```java
// --- extends ------------------------------------------------------------
class Dog extends Animal { ... }     // ask first: "a Dog IS an Animal"?
// inherited: public + protected (+ package-private in the same package)
// NOT inherited: constructors; private members exist but cannot be named

// --- super, two unrelated jobs -----------------------------------------
class Dog extends Animal {
    private String breed;
    Dog(String name, String breed) {
        super(name);                 // 1. parent constructor — FIRST statement
        this.breed = breed;
    }
    @Override
    String describe() {
        return super.describe() + ", a dog";     // 2. the parent's version
    }                                            //    (a bare describe() = infinite recursion)
}

// --- overriding vs overloading -----------------------------------------
//              params      resolved       where
// overload     DIFFERENT   compile time   usually one class
// override     IDENTICAL   RUN time       subclass replaces superclass
// Cannot override: static, private, final methods.
// An override may WIDEN access, never narrow it.

// --- polymorphism -------------------------------------------------------
Animal a = new Dog();                // upcast: free, always safe
a.speak();                           // Dog's version — the OBJECT decides
a.fetch();                           // does NOT compile — the VARIABLE decides
                                     //   what you may call

Animal[] zoo = { new Dog(), new Cat() };
for (Animal x : zoo) x.speak();      // one loop, many behaviours, no `if`

if (a instanceof Dog) { Dog d = (Dog) a; }   // guard every downcast
if (a instanceof Dog d) { d.fetch(); }        // Java 16+: test and bind

// --- the Object methods -------------------------------------------------
@Override public String toString() { return "(" + x + ", " + y + ")"; }

@Override public boolean equals(Object o) {   // MUST take Object
    if (this == o) return true;
    if (!(o instanceof Point)) return false;   // also handles null
    Point other = (Point) o;
    return x == other.x && y == other.y;
}
@Override public int hashCode() { return Objects.hash(x, y); }
// CONTRACT: equal objects => equal hash codes. Always override both.
```
""",
    self_check=[
        "Do you apply the is-a test out loud before writing `extends`?",
        "Can you explain why `super(...)` must be the first statement?",
        "Can you say what happens when a subclass constructor omits `super(...)` and the parent has no no-arg constructor?",
        "Can you give the four differences between overloading and overriding?",
        "Can you name two bugs `@Override` catches that would otherwise be silent?",
        "Can you predict which method runs for `Animal a = new Dog(); a.speak();` and say why?",
        "Can you write `equals` in its four steps, and say what breaks if you skip `hashCode`?",
    ],
    review=[
        _jq("```java\nclass A { String f() { return \"A\"; } }\nclass B extends A { String f() { return \"B\"; } }\nA x = new B();\nSystem.out.println(x.f());\n```",
            ["B", "A", "It does not compile", "AB"],
            0,
            "Dynamic dispatch. The variable's type gates what you may call; the object's "
            "class decides what runs."),
        _jq("A subclass constructor has no `super(...)` and the parent only declares `Parent(String)`. What happens?",
            ["Compile error — the implicit `super()` matches nothing",
             "It works; fields default",
             "A runtime exception",
             "The parent constructor is skipped"],
            0,
            "Java inserts `super();` silently, and there is no such constructor. The fix is "
            "to call `super(...)` explicitly."),
        _jq("You override `equals` and forget `hashCode`. When does it bite?",
            ["The first time the object goes into a HashMap or HashSet",
             "Immediately, at compile time",
             "Never",
             "Only with inheritance"],
            0,
            "Insert hashes to one bucket, lookup to another, and the object appears to have "
            "vanished. Silent until it matters."),
        _jq("In the capstone, why count `instanceof Square` rather than `instanceof Rect`?",
            ["Square extends Rect, so every Square is also a Rect and would be counted",
             "instanceof does not work on Rect",
             "Rect is abstract",
             "They give the same answer"],
            0,
            "`instanceof` is true for the whole subtree beneath a type. Asking about the "
            "wrong level of the hierarchy is a classic off-by-one-in-the-type-tree bug."),
    ],
    milestone="You can build class hierarchies, override behaviour deliberately, and write "
              "code that stays unchanged when a new subclass arrives — plus the three "
              "`Object` methods every serious Java class is expected to provide.",
))
