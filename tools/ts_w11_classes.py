# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 11 — classes & objects.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# ERASABLE SYNTAX — the one rule this week has to design around.
#
# The judge runs TypeScript by STRIPPING types (Node's type-stripping mode),
# not by compiling them. Almost all of TypeScript is erasable: delete the
# annotations and valid JavaScript is left behind. Three constructs are not,
# because they EMIT code, and Node refuses them outright:
#
#     ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX: TypeScript parameter property is not
#     supported in strip-only mode
#
#   - parameter properties   `constructor(public readonly x: number) {}`
#   - enums                  (week 12's problem, not this week's)
#   - namespaces
#
# Everything else this week uses was checked against the real runner and runs:
# `private`/`protected`/`static`/`readonly` modifiers, `#private` names,
# getters and setters, `implements`, `extends`/`super`, `abstract`, `override`.
#
# So lesson 5 teaches parameter properties with `judge_mode: "types"` — graded
# by the compiler alone, which is the only honest way to ship them here — and
# says so in the lesson text rather than pretending the restriction away. The
# same distinction is the closing argument of week 12's enum lesson, so it is
# introduced here as a named idea ("erasable syntax") on purpose.
# ---------------------------------------------------------------------------

# --- Week 11 --------------------------------------------------------------
_WEEKS.append(_week(
    11, 3, _M3,
    "Classes & Objects",
    "Bundle data with the operations on it: fields, constructors, methods, access modifiers, static members, and accessors.",
    """
Week 7 gave you objects. You could describe a receipt line:

```ts
const e = { desc: "coffee", cents: 325 };
```

and week 5 gave you functions that work on one:

```ts
function line(e: { desc: string; cents: number }): string {
  return `${e.desc} $${(e.cents / 100).toFixed(2)}`;
}
```

Those two halves belong together, and nothing in the language has been holding
them together. Anyone can build an `{ desc, cents }` with a negative amount, or
forget that `cents` is an integer, or write a second slightly different `line`.
The data and the rules about the data live in different places, and they drift.

A **class** is one declaration that holds both:

```ts
class Expense {
  readonly desc: string;
  readonly cents: number;

  constructor(desc: string, cents: number) {
    if (cents < 0) throw new Error("cents must not be negative");
    this.desc = desc;
    this.cents = cents;
  }

  line(): string {
    return `${this.desc} $${(this.cents / 100).toFixed(2)}`;
  }
}

const e = new Expense("coffee", 325);
console.log(e.line());        // coffee $3.25
```

Three things arrived at once. `new Expense(...)` is now the **only** way to get
one, so the constructor's check cannot be skipped. `line()` travels *with* the
value instead of having to be imported next to it. And `readonly` says the
fields are settled once built.

This week is mostly ordinary code — the difficulty is not in the type system,
it is in deciding what belongs inside a class and what does not. Two lessons
push back on inheritance for exactly that reason.

**Why this week is here, and not in month 5.** Weeks 18, 20 and 28 build a
`Stack<T>`, a linked list and a priority queue. None of them can be written
without this week, so it comes first.

⏱️ Budget about **ten hours**, spread over several sittings.
""",
    objectives=[
        "Say what a class gives you that an object literal plus a loose function does not",
        "Declare typed fields and a constructor, and satisfy strictPropertyInitialization",
        "Write methods that read and update the instance through `this`",
        "Explain why a detached method loses `this`, and fix it with an arrow-function field",
        "Hide state with `private`, and say how `#private` differs from it at runtime",
        "Use `readonly` fields to build value objects whose methods return new instances",
        "Recognise parameter properties, and say why they are not erasable syntax",
        "Expose a computed value with a getter and validate an assignment with a setter",
        "Put shared state and factory functions on the class with `static`",
        "Check a class against an interface with `implements`, and see that a plain object can satisfy the same interface",
        "Extend a class, call `super`, override a method, and reach the parent's version with `super.method()`",
        "Use `abstract` to demand a hook from every subclass — and choose composition when inheritance is the wrong tool",
    ],
    why="Classes are how the ecosystem ships stateful things: `Error` subclasses, every collection you will build in month 5, React class components in older code, NestJS controllers, and the priority queue an interviewer asks for. They are also where TypeScript's access modifiers live, which is the only place the language lets you say 'this field is nobody else's business'.",
    est_minutes=600,
    glossary=[
        _gloss("class", "A declaration that defines the shape, the construction rules and the behaviour of a kind of value."),
        _gloss("instance", "One value produced by `new`. Two instances of the same class have separate field values."),
        _gloss("new", "The operator that allocates an instance and runs the constructor."),
        _gloss("field (property)", "A named, typed slot on every instance."),
        _gloss("constructor", "The method that runs once, at `new`, to put the instance into a valid state."),
        _gloss("strictPropertyInitialization", "The strict-mode rule that a field must be initialised, or definitely assigned in the constructor (TS2564)."),
        _gloss("method", "A function declared in the class body and called on an instance."),
        _gloss("this", "Inside a method, the instance the method was called ON — decided by the call, not by the declaration."),
        _gloss("public", "The default. Readable and writable from anywhere."),
        _gloss("private", "Visible only inside the class body. A compile-time rule: the field is still an ordinary property at runtime."),
        _gloss("#private name", "A field whose name starts with `#`. Genuinely inaccessible outside the class, at runtime as well as compile time."),
        _gloss("protected", "Visible inside the class and its subclasses, but not from outside."),
        _gloss("readonly field", "Assignable in the constructor and nowhere else (TS2540)."),
        _gloss("value object", "A class whose instances are never mutated; operations return a new instance."),
        _gloss("parameter property", "`constructor(public readonly x: number)` — declares the field and assigns it in one stroke."),
        _gloss("erasable syntax", "TypeScript that disappears when annotations are deleted. Parameter properties and enums are NOT erasable: they emit code."),
        _gloss("getter", "`get name(): T` — read like a field, runs like a method."),
        _gloss("setter", "`set name(v: T)` — assigned like a field, so it is where an assignment can be validated."),
        _gloss("static member", "A field or method on the CLASS rather than on each instance (TS2576 if you reach it through an instance)."),
        _gloss("static factory", "A static method that returns an instance, usually parsing or validating on the way in."),
        _gloss("implements", "Asks the compiler to check that a class satisfies an interface (TS2420 when it does not)."),
        _gloss("extends", "Declares a subclass, which inherits the parent's fields and methods."),
        _gloss("super(...)", "Calls the parent constructor. Required in a derived constructor, and required BEFORE `this` (TS2377, TS17009)."),
        _gloss("super.method()", "Calls the parent's version of a method you have overridden."),
        _gloss("override", "Optional modifier saying a method is meant to replace an inherited one."),
        _gloss("abstract class", "A base class that cannot be instantiated (TS2511) and may declare members with no body."),
        _gloss("abstract member", "A signature with no implementation that every concrete subclass must provide (TS2515)."),
        _gloss("template method", "A concrete method on the base that calls an abstract hook the subclass fills in."),
        _gloss("composition", "Holding a collaborator in a field instead of inheriting from it."),
        _gloss("instanceof", "Runtime check that narrows a base-class type to a subclass."),
    ],
    cheatsheet="""
```ts
// ---- fields, constructor, methods ---------------------------------------
class Expense {
  desc: string;                  // declared, assigned in the constructor
  cents: number;
  tag: string = "misc";          // declared with a default

  constructor(desc: string, cents: number) {
    this.desc = desc;
    this.cents = cents;
  }

  line(): string {                       // a method
    return `${this.desc} ${this.dollars()}`;
  }
  dollars(): string {                    // methods may call each other
    return `$${(this.cents / 100).toFixed(2)}`;
  }
}
const e = new Expense("coffee", 325);    // `new` is not optional (TS2348)

// ---- visibility ----------------------------------------------------------
class Account {
  private balance: number = 0;   // compile-time only; still a property at runtime
  #pin: number = 1234;           // really private, at runtime too
  protected owner: string = "";  // this class and its subclasses
  deposit(n: number): void { this.balance += n; }
}

// ---- readonly & value objects -------------------------------------------
class Money {
  readonly cents: number;
  constructor(cents: number) { this.cents = cents; }
  plus(other: Money): Money {           // returns a NEW instance
    return new Money(this.cents + other.cents);
  }
}

// ---- parameter properties (NOT erasable — type-checked here, not run) ----
class Point {
  constructor(public readonly x: number, private y: number = 0) {}
}
// longhand equivalent, which does run:
class Point2 {
  readonly x: number;
  private y: number;
  constructor(x: number, y: number = 0) { this.x = x; this.y = y; }
}

// ---- accessors & statics -------------------------------------------------
class Thermostat {
  private c: number = 20;
  static readonly MIN: number = 5;
  get temp(): number { return this.c; }               // read as t.temp
  set temp(v: number) {                               // written as t.temp = 9
    this.c = v < Thermostat.MIN ? Thermostat.MIN : v;
  }
  static fromF(f: number): Thermostat {               // static factory
    const t = new Thermostat();
    t.temp = (f - 32) / 1.8;
    return t;
  }
}

// ---- interfaces, inheritance, abstract ----------------------------------
interface Priced { amount: number; label(): string; }

abstract class Entry {
  constructor(protected desc: string) {}    // (shown longhand in lessons)
  abstract cents(): number;                 // every subclass must supply it
  line(): string {                          // template method
    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;
  }
}
class Fixed extends Entry {
  private amount: number;
  constructor(desc: string, amount: number) {
    super(desc);                            // FIRST, before any `this`
    this.amount = amount;
  }
  cents(): number { return this.amount; }
  override line(): string { return `* ${super.line()}`; }
}
// new Entry("x")   // TS2511: cannot instantiate an abstract class
```
""",
    self_check=[
        "Can you say two things a class gives you that an object literal plus a function does not?",
        "Can you write a class with two fields and a constructor that assigns both?",
        "Can you explain the error 'Property x has no initializer and is not definitely assigned in the constructor'?",
        "Can you say what `this` refers to inside a method, and what decides it?",
        "Can you explain why `const f = obj.method; f()` throws, and fix it two different ways?",
        "Can you say what `private` does NOT protect you from at runtime, and which syntax does?",
        "Can you write a value object whose `plus` returns a new instance instead of mutating?",
        "Can you say why a parameter property cannot run in this course, and write its longhand form?",
        "Can you write a getter and a setter, and say what makes a setter the right place for validation?",
        "Can you say when a member belongs on the class (`static`) rather than on each instance?",
        "Can you make a class satisfy an interface, and explain why a plain object can satisfy it too?",
        "Can you write a subclass that calls `super(...)` and overrides one method with `super.method()` inside it?",
        "Can you say what an abstract class buys over an interface, and name a case where composition is the better answer?",
    ],
    review=[
        _q("`new Expense(\"coffee\", 325)` does what, in order?",
           ["runs the constructor, then allocates", "allocates an instance, then runs the constructor",
            "calls line()", "copies an existing instance"], 1,
           "Allocation first, then the constructor puts it into a valid state."),
        _q("Leaving out `new` — `const c = Counter();` — gives…",
           ["a fresh instance", "TS2348: value of type 'typeof Counter' is not callable",
            "undefined", "a runtime crash only"], 1,
           "The class itself is not a callable function."),
        _q("A field declared `desc: string;` with no default and no assignment in the constructor…",
           ["defaults to \"\"", "is TS2564", "defaults to undefined silently", "is allowed under strict"], 1,
           "strictPropertyInitialization demands it be definitely assigned."),
        _q("Inside a method, `this` is…",
           ["the class", "the instance the method was called on", "the module", "always undefined"], 1,
           "It is decided by the call site, which is why a detached method loses it."),
        _q("`const f = counter.bump; f();` throws because…",
           ["bump is private", "the call has no receiver, so `this` is undefined",
            "bump is static", "f is not a function"], 1,
           "Reading the method detaches it from the instance."),
        _q("The reliable fix for a method that will be detached is…",
           ["make it static", "declare it as an arrow-function field", "make it private",
            "add a return type"], 1,
           "An arrow field captures `this` where it is created."),
        _q("`private balance` at RUNTIME is…",
           ["absent from the object", "an ordinary property, visible to Object.keys",
            "frozen", "renamed"], 1,
           "`private` is erased; only `#balance` is enforced when the program runs."),
        _q("`readonly cents` may be assigned…",
           ["nowhere", "in the constructor only", "in any method", "only via a setter"], 1,
           "Anywhere else is TS2540."),
        _q("`constructor(public readonly x: number) {}` is…",
           ["erasable syntax", "a parameter property, which EMITS an assignment and so is not erasable",
            "the same as a getter", "invalid TypeScript"], 1,
           "It declares and assigns the field, so deleting the types would change behaviour."),
        _q("A getter is called…",
           ["with parentheses, like a method", "without parentheses, like a field",
            "only from the constructor", "only once"], 1,
           "`t.temp`, not `t.temp()`."),
        _q("`Counter.made` where `made` is static, reached as `c.made` on an instance, gives…",
           ["the same value", "TS2576 — did you mean the static member?", "undefined", "0"], 1,
           "A static member is not on the instance."),
        _q("`class Expense implements Priced` does what?",
           ["copies Priced's code", "asks the compiler to check the class against the interface",
            "creates a subclass", "nothing at runtime or compile time"], 1,
           "It is a check, not inheritance — TS2420 when it fails."),
        _q("A plain object literal can satisfy `Priced` because TypeScript is…",
           ["nominal", "structural — the shape is what counts", "dynamic", "erased"], 1,
           "Week 12 is entirely about this rule."),
        _q("In a derived constructor, `super(...)` must come…",
           ["last", "before any use of `this`", "anywhere", "only if there are fields"], 1,
           "TS2377 when it is missing, TS17009 when `this` comes first."),
        _q("`super.line()` inside an override calls…",
           ["itself, recursively", "the parent's version of line", "a static method",
            "the constructor"], 1,
           "Which is how you extend a parent's behaviour instead of replacing it."),
        _q("`new Entry(\"x\")` where `Entry` is abstract gives…",
           ["an instance", "TS2511: cannot create an instance of an abstract class",
            "undefined", "TS2515"], 1,
           "Abstract classes exist only to be extended."),
        _q("A subclass of an abstract class that does not implement an abstract member gives…",
           ["TS2511", "TS2515", "no error", "TS2420"], 1,
           "Non-abstract class does not implement inherited abstract member."),
        _q("An abstract class is the better choice over an interface when…",
           ["you need multiple inheritance", "the base has real shared CODE to give the subclasses",
            "you want structural typing", "never"], 1,
           "An interface carries no implementation; that is the whole difference."),
    ],
    milestone="Budget Buddy stops being a pile of functions that pass records around. A `Ledger` now owns its entries — nothing outside it can touch the array — and an `Expense` knows how to parse and format itself. Every data structure in month 5 is built on the syntax you just learned.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w11-why", "Why a class",
            "What an object literal and a loose function cannot do.",
            """
You already have two ways to keep data together, and one way to act on it.

```ts
interface Expense { desc: string; cents: number; }

function line(e: Expense): string {
  return `${e.desc} $${(e.cents / 100).toFixed(2)}`;
}
```

That works. Here is what it does not do.

**Nothing makes an invalid value impossible.** `{ desc: "", cents: -500 }` is a
perfectly good `Expense` as far as the compiler is concerned. The interface
describes a shape; it cannot describe a *rule*.

**The behaviour is somewhere else.** `line` sits next to the type today. In six
months it is in another file, and somebody has written a second one that
formats to three decimal places.

**There is no single answer to "what can I do with this?"** With an interface,
the operations are wherever anyone happened to put them.

A class fixes all three:

```ts
class Expense {
  desc: string;
  cents: number;

  constructor(desc: string, cents: number) {
    this.desc = desc;
    this.cents = cents;
  }

  line(): string {
    return `${this.desc} $${(this.cents / 100).toFixed(2)}`;
  }
}
```

## Reading the declaration

```ts
const e = new Expense("coffee", 325);
console.log(e.line());        // coffee $3.25
```

`new Expense(...)` does two things: it allocates a fresh **instance**, then runs
the **constructor** on it. The `desc` and `cents` lines are **fields** — every
instance gets its own. `line()` is a **method**, and inside it `this` is the
instance it was called on.

**Instances are independent.** This is the whole point of `new`:

```ts
const a = new Expense("coffee", 325);
const b = new Expense("book", 1200);
console.log(a.cents);   // 325
console.log(b.cents);   // 1200
```

## `new` is not optional

```ts
const bad = Expense("coffee", 325);
// TS2348: Value of type 'typeof Expense' is not callable.
//         Did you mean to include 'new'?
```

A class is not a function that returns an object. `new` is what allocates.

## When NOT to reach for a class

Plenty of data has no rules and no behaviour. A parsed CSV row you read once
and throw away wants an interface, not a class. Reach for a class when there is
an **invariant to protect** (`cents` is a non-negative integer), **state that
changes over time** (a ledger you add to), or **behaviour that belongs to the
data** rather than to the caller.

> ⚠️ **Common mistakes:** forgetting `new`; expecting two instances to share a
> field (they do not — that is what `static` is for, in lesson 6); and writing
> classes with no methods at all, which is an interface with extra steps.
""",
            warmup=[
                _q("`new Expense(\"coffee\", 325)` returns…",
                   ["the class", "a new instance", "a function", "an interface"], 1,
                   "One fresh value, with its own fields."),
                _q("Inside `line()`, `this` refers to…",
                   ["the class Expense", "the instance the method was called on",
                    "the module", "the constructor"], 1,
                   "The receiver of the call."),
                _q("Two instances of the same class…",
                   ["share their field values", "each have their own field values",
                    "are the same object", "cannot both exist"], 1,
                   "That is what `new` allocates."),
                _q("What an interface CANNOT do that a class can:",
                   ["describe a shape", "make an invalid value impossible to construct",
                    "be used as a type", "have optional members"], 1,
                   "An interface has no constructor to enforce anything."),
            ],
            exercises=[
                _ex("tscourse-w11-wh-1", "Your first class",
                    "Give the class a `count` field that starts at 0.",
                    'class Counter {\n  count: number = 0;\n}\n'
                    'const c = new Counter();\nconsole.log(c.count);\n',
                    'count: number = 0;', [("", "0")],
                    hints=["A field is a name, a type, and here an initial value.",
                           "Write count: number = 0;"]),
                _ex("tscourse-w11-wh-2", "Add a method",
                    "`bump` should add one to the instance's own count.",
                    'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                    '    this.count = this.count + 1;\n  }\n}\n'
                    'const c = new Counter();\nc.bump();\nc.bump();\nconsole.log(c.count);\n',
                    'this.count = this.count + 1;', [("", "2")],
                    hints=["The field belongs to the instance, so reach it through `this`.",
                           "Write this.count = this.count + 1;"]),
                _ex("tscourse-w11-wh-3", "Two instances, two states",
                    "Make a second, independent counter so the two totals differ.",
                    'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                    '    this.count = this.count + 1;\n  }\n}\n'
                    'const a = new Counter();\nconst b = new Counter();\n'
                    'a.bump();\na.bump();\nb.bump();\n'
                    'console.log(`${a.count} ${b.count}`);\n',
                    'const b = new Counter();', [("", "2 1")],
                    hints=["Each `new` allocates its own fields.",
                           "Write const b = new Counter();"]),
                _ex("tscourse-w11-wh-4", "Build the instance",
                    "Create the greeter so its method can be called.",
                    'class Greeter {\n  name: string = "world";\n\n  greet(): string {\n'
                    '    return `hello ${this.name}`;\n  }\n}\n'
                    'const g = new Greeter();\nconsole.log(g.greet());\n',
                    'new Greeter()', [("", "hello world")],
                    hints=["A class is not callable on its own.",
                           "Write new Greeter()."]),
                _ex("tscourse-w11-wh-5", "A class over a list",
                    "Write `summary` so it reports the count and the items, comma-separated.",
                    'class Basket {\n  items: string[] = [];\n\n  add(item: string): void {\n'
                    '    this.items.push(item);\n  }\n\n  summary(): string {\n'
                    '    return `${this.items.length}: ${this.items.join(", ")}`;\n  }\n}\n'
                    'const b = new Basket();\nb.add("coffee");\nb.add("book");\n'
                    'console.log(b.summary());\n',
                    'return `${this.items.length}: ${this.items.join(", ")}`;',
                    [("", "2: coffee, book")],
                    hints=["Both halves come off `this.items`.",
                           "Length, then a colon and a space, then join with a comma and a space."],
                    difficulty="Medium"),
                _predict("tscourse-w11-wh-p1", "The type of an instance",
                         'class Counter {\n  count: number = 0;\n}\n'
                         'const c = new Counter();\n',
                         "c", "Counter",
                         why="A class declaration introduces a type as well as a value.",
                         hints=["The class name is usable as a type, and that type describes its instances.",
                                "Write Counter."]),
                _diagnose("tscourse-w11-wh-d1", "The missing operator",
                          "TS2348: Value of type 'typeof Counter' is not callable. Did you mean to include 'new'?",
                          'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                          '    this.count = this.count + 1;\n  }\n}\n'
                          'const c = Counter();\nc.bump();\nconsole.log(c.count);\n',
                          'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                          '    this.count = this.count + 1;\n  }\n}\n'
                          'const c = new Counter();\nc.bump();\nconsole.log(c.count);\n',
                          [("", "1")],
                          hints=["`typeof Counter` is the type of the class itself, not of an instance.",
                                 "A class has to be allocated before it can be used."],
                          difficulty="Easy"),
                _fix("tscourse-w11-wh-fix1", "Fix the counter that never counts",
                     "`bump` computes the new value and drops it on the floor, so this prints 0 instead of 2.",
                     'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                     '    const count = this.count + 1;\n  }\n}\n'
                     'const c = new Counter();\nc.bump();\nc.bump();\nconsole.log(c.count);\n',
                     'class Counter {\n  count: number = 0;\n\n  bump(): void {\n'
                     '    this.count = this.count + 1;\n  }\n}\n'
                     'const c = new Counter();\nc.bump();\nc.bump();\nconsole.log(c.count);\n',
                     [("", "2")],
                     hints=["A `const` inside the method is a local that vanishes when the method returns.",
                            "Assign to the field on `this`, not to a new local."]),
            ],
            quiz=[
                _q("A class is the right tool when…",
                   ["you have any data at all", "there is an invariant, changing state, or behaviour that belongs to the data",
                    "you dislike interfaces", "the data is read once"], 1,
                   "Otherwise an interface is lighter and says the same thing."),
                _q("`class Expense { desc: string = \"\"; }` with no methods is…",
                   ["good practice", "essentially an interface with extra steps",
                    "invalid", "faster than an interface"], 1,
                   "The point of a class is bundling behaviour with the data."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w11-fields", "Fields & constructors",
            "Declaring the slots, and guaranteeing they are filled.",
            """
A field is declared like a variable with no `const` or `let`:

```ts
class Expense {
  desc: string;
  cents: number;
  tag: string = "misc";      // with a default
}
```

Fields with no default have to be assigned by the time the constructor
finishes. That is `strictPropertyInitialization`, part of `strict`:

```ts
class Expense {
  desc: string;
  // TS2564: Property 'desc' has no initializer and is not
  //         definitely assigned in the constructor.
}
```

It is one of the most useful rules in the language: without it, `e.desc` would
be typed `string` and be `undefined` at runtime — a lie the compiler told you.

## The constructor

```ts
class Expense {
  desc: string;
  cents: number;

  constructor(desc: string, cents: number) {
    this.desc = desc;
    this.cents = cents;
  }
}
```

The parameters and the fields are **different things** that happen to share
names. `desc` inside the constructor is the parameter; `this.desc` is the field.
Forget the `this.` and you get TS2663, which helpfully names the fix.

Constructor parameters can have defaults, exactly like a function's:

```ts
constructor(desc: string, cents: number = 0) { … }
```

## Deriving one field from another

Assignments run in order, so a later field can read an earlier one:

```ts
class Receipt {
  subtotal: number;
  tax: number;
  total: number;

  constructor(subtotal: number) {
    this.subtotal = subtotal;
    this.tax = subtotal * 0.1;
    this.total = this.subtotal + this.tax;   // reads the two above
  }
}
```

(Once you meet getters in lesson 6 you will often prefer to *compute* `total`
rather than store it — a stored derived value is one more thing to keep in
step.)

## The constructor is the gate

This is the payoff from lesson 1. Because `new` is the only way in, the
constructor is the one place a rule can be enforced:

```ts
class Expense {
  desc: string;
  cents: number;

  constructor(desc: string, cents: number) {
    if (cents < 0) {
      throw new Error("cents must not be negative");
    }
    this.desc = desc;
    this.cents = cents;
  }
}
```

Now no `Expense` anywhere in the program has a negative amount, and you did not
have to check at every use site.

**Argument counts are checked**, so a missed argument is TS2554 —
`Expected 2 arguments, but got 1` — rather than a silent `undefined`.

> ⚠️ **Common mistakes:** assigning to the parameter instead of the field
> (`desc = desc`); expecting a field's declared type to protect you when you
> never assigned it (that is what TS2564 is for); and storing a derived value
> that then goes stale.
""",
            warmup=[
                _q("A field with no default and no constructor assignment is…",
                   ["undefined at runtime, silently", "TS2564", "automatically zero",
                    "optional"], 1,
                   "strictPropertyInitialization refuses to let it through."),
                _q("Inside `constructor(desc: string)`, `desc` refers to…",
                   ["the field", "the parameter", "both", "neither"], 1,
                   "The field is `this.desc`."),
                _q("`new Expense(\"coffee\")` on a two-parameter constructor gives…",
                   ["undefined for the second", "TS2554: Expected 2 arguments, but got 1",
                    "0 for the second", "a runtime error only"], 1,
                   "Constructors are checked like any other call."),
                _q("Why is the constructor a good place for a validity check?",
                   ["it is faster", "it is the only way to build an instance, so the check cannot be skipped",
                    "it runs on every method call", "it is required"], 1,
                   "That is the invariant argument from lesson 1."),
            ],
            exercises=[
                _ex("tscourse-w11-fl-1", "Assign both fields",
                    "Fill in the constructor body so both fields come from the parameters.",
                    'class Expense {\n  desc: string;\n  amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                    'const e = new Expense("coffee", 3.25);\n'
                    'console.log(`${e.desc} ${e.amount.toFixed(2)}`);\n',
                    'this.desc = desc;\n    this.amount = amount;',
                    [("", "coffee 3.25")],
                    hints=["Two assignments, both onto `this`.",
                           "this.desc = desc; then this.amount = amount;"]),
                _ex("tscourse-w11-fl-2", "Declare the fields",
                    "Declare the two fields the constructor assigns.",
                    'class Expense {\n  desc: string;\n  amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                    'console.log(new Expense("book", 12).desc);\n',
                    'desc: string;\n  amount: number;',
                    [("", "book")],
                    hints=["A field declaration is a name, a colon and a type, ending in a semicolon.",
                           "desc: string; then amount: number;"]),
                _ex("tscourse-w11-fl-3", "A field with a default",
                    "Give `tag` a default of \"misc\" so the constructor does not have to set it.",
                    'class Expense {\n  desc: string;\n  amount: number;\n  tag: string = "misc";\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                    'const e = new Expense("coffee", 3.25);\n'
                    'console.log(`${e.desc} ${e.tag}`);\n',
                    'tag: string = "misc";', [("", "coffee misc")],
                    hints=["A default makes the field definitely assigned without touching the constructor.",
                           'Write tag: string = "misc";']),
                _ex("tscourse-w11-fl-4", "Derive a field from the others",
                    "Set `total` from the two fields already assigned above it.",
                    'class Receipt {\n  subtotal: number;\n  tax: number;\n  total: number;\n\n'
                    '  constructor(subtotal: number) {\n'
                    '    this.subtotal = subtotal;\n    this.tax = subtotal * 0.1;\n'
                    '    this.total = this.subtotal + this.tax;\n  }\n}\n'
                    'const r = new Receipt(20);\n'
                    'console.log(`${r.subtotal} ${r.tax.toFixed(2)} ${r.total.toFixed(2)}`);\n',
                    'this.total = this.subtotal + this.tax;',
                    [("", "20 2.00 22.00")],
                    hints=["The two fields above have already been assigned by the time this line runs.",
                           "Add this.subtotal and this.tax."],
                    difficulty="Medium"),
                _ex("tscourse-w11-fl-5", "The constructor as a gate",
                    "Reject a negative amount before either field is assigned.",
                    'class Expense {\n  desc: string;\n  amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    if (amount < 0) {\n'
                    '      throw new Error("amount must not be negative");\n'
                    '    }\n'
                    '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                    'try {\n  const bad = new Expense("refund", -5);\n  console.log(bad.desc);\n'
                    '} catch (err) {\n'
                    '  console.log(err instanceof Error ? err.message : "unknown");\n}\n'
                    'console.log(new Expense("coffee", 3.25).desc);\n',
                    'throw new Error("amount must not be negative");',
                    [("", "amount must not be negative\ncoffee")],
                    hints=["Throwing stops the constructor, so no half-built instance escapes.",
                           'Write throw new Error("amount must not be negative");'],
                    difficulty="Medium"),
                _diagnose("tscourse-w11-fl-d1", "The field that was never filled",
                          "TS2564: Property 'desc' has no initializer and is not definitely assigned in the constructor.",
                          'class Expense {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(amount: number) {\n'
                          '    this.amount = amount;\n  }\n\n'
                          '  label(): string {\n    return `${this.desc}:${this.amount}`;\n  }\n}\n'
                          'console.log(new Expense(3).label());\n',
                          'class Expense {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                          '  label(): string {\n    return `${this.desc}:${this.amount}`;\n  }\n}\n'
                          'console.log(new Expense("coffee", 3).label());\n',
                          [("", "coffee:3")],
                          hints=["`desc` is typed `string`, but nothing ever puts a string in it.",
                                 "Take it as a constructor parameter and assign it — then pass it at the call site.",
                                 "A default value would also satisfy the compiler, but here the caller clearly has the description."],
                          difficulty="Medium"),
                _diagnose("tscourse-w11-fl-d2", "The missing argument",
                          "TS2554: Expected 2 arguments, but got 1.",
                          'class Expense {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                          'const e = new Expense("coffee");\n'
                          'console.log(e.amount.toFixed(2));\n',
                          'class Expense {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    this.desc = desc;\n    this.amount = amount;\n  }\n}\n'
                          'const e = new Expense("coffee", 3.25);\n'
                          'console.log(e.amount.toFixed(2));\n',
                          [("", "3.25")],
                          hints=["The constructor takes two parameters and the call supplies one.",
                                 "Pass an amount of 3.25 as well."],
                          difficulty="Easy"),
                _fix("tscourse-w11-fl-fix1", "Fix the constructor that loses a parameter",
                     "Both fields are assigned from the same parameter, so this prints `Lovelace Lovelace` instead of `Ada Lovelace`.",
                     'class Person {\n  first: string;\n  last: string;\n\n'
                     '  constructor(first: string, last: string) {\n'
                     '    this.first = last;\n    this.last = last;\n  }\n\n'
                     '  full(): string {\n    return `${this.first} ${this.last}`;\n  }\n}\n'
                     'console.log(new Person("Ada", "Lovelace").full());\n',
                     'class Person {\n  first: string;\n  last: string;\n\n'
                     '  constructor(first: string, last: string) {\n'
                     '    this.first = first;\n    this.last = last;\n  }\n\n'
                     '  full(): string {\n    return `${this.first} ${this.last}`;\n  }\n}\n'
                     'console.log(new Person("Ada", "Lovelace").full());\n',
                     [("", "Ada Lovelace")],
                     hints=["Both parameters are strings, so the compiler had nothing to object to.",
                            "Each field should come from the parameter of the same name."]),
            ],
            quiz=[
                _q("`this.tax = subtotal * 0.1;` inside a constructor reads…",
                   ["the field tax", "the parameter subtotal", "a global", "nothing"], 1,
                   "Parameters are plain locals; fields need `this.`."),
                _q("Storing a derived value like `total` in a field risks…",
                   ["a type error", "the stored value going stale when the inputs change",
                    "slower construction", "nothing"], 1,
                   "Lesson 6's getter computes it fresh instead."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w11-methods", "Methods & `this`",
            "Behaviour that travels with the value — and the one way it comes loose.",
            """
A method is a function declared in the class body, with no `function` keyword:

```ts
class Ledger {
  entries: number[] = [];

  add(n: number): void {
    this.entries.push(n);
  }

  total(): number {
    return this.entries.reduce((s, n) => s + n, 0);
  }
}
```

Everything you know about functions applies: parameters, return types,
defaults, generics. The only new thing is `this`.

## Methods can call each other

```ts
average(): number {
  return this.entries.length === 0 ? 0 : this.total() / this.entries.length;
}
```

`this.total()` — the same `this.` you use for a field. A method that calls
another method is how a class grows a small vocabulary instead of one enormous
function.

## `this` is decided by the CALL, not the declaration

This is the one genuinely surprising thing about methods, and it comes from
JavaScript rather than from TypeScript.

```ts
const led = new Ledger();
led.add(3);              // `this` is led — it is left of the dot
```

Read the method **off** the instance and the dot is gone:

```ts
const detached = led.add;
detached(3);
// TypeError: Cannot read properties of undefined (reading 'entries')
```

`detached` is the same function, called with no receiver, so `this` is
`undefined`. This is not exotic — it is what happens every time a method is
passed as a callback:

```ts
[1, 2, 3].forEach(led.add);      // same crash
```

**Two fixes.** Pass a call instead of a function:

```ts
[1, 2, 3].forEach((n) => led.add(n));    // the dot is still there
```

Or declare the method as an **arrow-function field**, which captures `this`
where the instance is built:

```ts
class Counter {
  count: number = 0;
  bump = (): void => {
    this.count = this.count + 1;
  };
}
const c = new Counter();
const detached = c.bump;
detached();                 // fine — count is 1
```

The trade-off: an arrow field is a separate function object per instance and
cannot be overridden by a subclass in the normal way. Use a normal method by
default, and an arrow field when you know the method will travel alone.

## `this.` is not optional

```ts
bump(): void {
  count = count + 1;
  // TS2663: Cannot find name 'count'. Did you mean the instance member 'this.count'?
}
```

TypeScript recognises the mistake and names the fix. In plain JavaScript this
would have been a silent global.

> ⚠️ **Common mistakes:** passing `obj.method` as a callback; leaving off
> `this.`; and reaching for an arrow field everywhere "to be safe", which
> quietly breaks overriding in lesson 8.
""",
            warmup=[
                _q("`this` inside a method is…",
                   ["the class", "whatever was left of the dot at the call site",
                    "always the instance that declared it", "the module"], 1,
                   "The call decides it."),
                _q("`const f = led.add; f(3);` throws because…",
                   ["add is private", "there is no receiver, so `this` is undefined",
                    "add takes no arguments", "f is not a function"], 1,
                   "Reading the method detached it."),
                _q("`count = count + 1;` inside a method gives…",
                   ["TS2663, naming this.count as the fix", "a new global",
                    "the right answer", "TS2564"], 0,
                   "The compiler spots exactly this mistake."),
                _q("An arrow-function field fixes detachment because…",
                   ["arrows are faster", "it captures `this` where the instance is created",
                    "arrows cannot be detached", "it is static"], 1,
                   "The binding is fixed at construction time."),
            ],
            exercises=[
                _ex("tscourse-w11-me-1", "Total the entries",
                    "Fold the entries into a sum.",
                    'class Ledger {\n  entries: number[] = [];\n\n'
                    '  add(n: number): void {\n    this.entries.push(n);\n  }\n\n'
                    '  total(): number {\n    return this.entries.reduce((s, n) => s + n, 0);\n  }\n}\n'
                    'const l = new Ledger();\nl.add(3);\nl.add(4.5);\n'
                    'console.log(l.total().toFixed(2));\n',
                    'return this.entries.reduce((s, n) => s + n, 0);',
                    [("", "7.50")],
                    hints=["Week 8's fold, over the field rather than a parameter.",
                           "Seed the reduce with 0."]),
                _ex("tscourse-w11-me-2", "One method calling another",
                    "Return the mean, guarding the empty case with 0.",
                    'class Ledger {\n  entries: number[] = [];\n\n'
                    '  add(n: number): void {\n    this.entries.push(n);\n  }\n\n'
                    '  total(): number {\n    return this.entries.reduce((s, n) => s + n, 0);\n  }\n\n'
                    '  average(): number {\n'
                    '    return this.entries.length === 0 ? 0 : this.total() / this.entries.length;\n  }\n}\n'
                    'const l = new Ledger();\nl.add(2);\nl.add(4);\n'
                    'console.log(l.average());\n'
                    'console.log(new Ledger().average());\n',
                    'this.entries.length === 0 ? 0 : this.total() / this.entries.length',
                    [("", "3\n0")],
                    hints=["Reuse `total()` rather than folding a second time.",
                           "Guard the empty array first, or you divide by zero."],
                    difficulty="Medium"),
                _ex("tscourse-w11-me-3", "A method that filters",
                    "Return only the items starting with the given prefix.",
                    'class Basket {\n  items: string[] = [];\n\n'
                    '  add(item: string): void {\n    this.items.push(item);\n  }\n\n'
                    '  startingWith(prefix: string): string[] {\n'
                    '    return this.items.filter((i) => i.startsWith(prefix));\n  }\n}\n'
                    'const b = new Basket();\nb.add("coffee");\nb.add("cocoa");\nb.add("book");\n'
                    'console.log(b.startingWith("co").join(","));\n',
                    'return this.items.filter((i) => i.startsWith(prefix));',
                    [("", "coffee,cocoa")],
                    hints=["A method may use its parameter and its fields together.",
                           "Filter this.items on startsWith(prefix)."]),
                _ex("tscourse-w11-me-4", "A report built from two methods",
                    "Write `report` so it reads the count and calls `total`.",
                    'class Ledger {\n  entries: number[] = [];\n\n'
                    '  add(n: number): void {\n    this.entries.push(n);\n  }\n\n'
                    '  total(): number {\n    return this.entries.reduce((s, n) => s + n, 0);\n  }\n\n'
                    '  report(): string {\n'
                    '    return `${this.entries.length} entries, total ${this.total().toFixed(2)}`;\n  }\n}\n'
                    'const l = new Ledger();\nl.add(3);\nl.add(4.5);\n'
                    'console.log(l.report());\n',
                    'return `${this.entries.length} entries, total ${this.total().toFixed(2)}`;',
                    [("", "2 entries, total 7.50")],
                    hints=["Both halves come off `this` — one a field, one a method call.",
                           "Two decimal places on the total."],
                    difficulty="Medium"),
                _ex("tscourse-w11-me-5", "A method that survives detachment",
                    "Declare `bump` as an arrow-function field so `this` is captured at construction.",
                    'class Counter {\n  count: number = 0;\n\n'
                    '  bump = (): void => {\n    this.count = this.count + 1;\n  };\n}\n'
                    'const c = new Counter();\nconst detached = c.bump;\n'
                    'detached();\ndetached();\nconsole.log(c.count);\n',
                    'bump = (): void =>', [("", "2")],
                    hints=["It is a field whose value is a function, so it needs `=` rather than a parameter list alone.",
                           "Write bump = (): void =>"],
                    difficulty="Medium"),
                _predict("tscourse-w11-me-p1", "What a method hands back",
                         'class Ledger {\n  entries: number[] = [];\n\n'
                         '  first(): number | undefined {\n'
                         '    return this.entries[0];\n  }\n}\n'
                         'const l = new Ledger();\nconst got = l.first();\n',
                         "got", "number | undefined",
                         why="Read the declared return type, and note why it has to say that "
                             "under noUncheckedIndexedAccess.",
                         hints=["`this.entries[0]` is not a `number` — indexing may find nothing.",
                                "The declared return type is what the call site sees.",
                                "Write number | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w11-me-d1", "The forgotten receiver",
                          "TS2663: Cannot find name 'count'. Did you mean the instance member 'this.count'?",
                          'class Counter {\n  count: number = 0;\n\n'
                          '  bump(): void {\n    count = count + 1;\n  }\n\n'
                          '  value(): number {\n    return this.count;\n  }\n}\n'
                          'const c = new Counter();\nc.bump();\nc.bump();\nconsole.log(c.value());\n',
                          'class Counter {\n  count: number = 0;\n\n'
                          '  bump(): void {\n    this.count = this.count + 1;\n  }\n\n'
                          '  value(): number {\n    return this.count;\n  }\n}\n'
                          'const c = new Counter();\nc.bump();\nc.bump();\nconsole.log(c.value());\n',
                          [("", "2")],
                          hints=["A field is not in scope as a bare name.",
                                 "The error message names the fix exactly."],
                          difficulty="Easy"),
                _fix("tscourse-w11-me-fix1", "Fix the method that lost its instance",
                     "`c.bump` is read off the instance and called without it, so `this` is undefined and the program crashes. It should print 1. Keep the detached call — change the class so it works.",
                     'class Counter {\n  count: number = 0;\n\n'
                     '  bump(): void {\n    this.count = this.count + 1;\n  }\n}\n'
                     'const c = new Counter();\nconst detached = c.bump;\n'
                     'detached();\nconsole.log(c.count);\n',
                     'class Counter {\n  count: number = 0;\n\n'
                     '  bump = (): void => {\n    this.count = this.count + 1;\n  };\n}\n'
                     'const c = new Counter();\nconst detached = c.bump;\n'
                     'detached();\nconsole.log(c.count);\n',
                     [("", "1")],
                     hints=["Nothing is left of the dot when `detached()` runs.",
                            "An arrow-function field binds `this` when the instance is built.",
                            "Remember the trailing semicolon: a field's value is an expression."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`[1, 2, 3].forEach(led.add)` fails for the same reason as…",
                   ["a missing return type", "`const f = led.add; f(1)`",
                    "a private field", "TS2564"], 1,
                   "Passing a method as a callback detaches it."),
                _q("A normal method is preferable to an arrow field because…",
                   ["it is shorter", "it lives on the prototype and can be overridden by a subclass",
                    "it binds `this`", "it is private"], 1,
                   "Arrow fields are per-instance and break the override in lesson 8."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w11-access", "`public`, `private` and `#private`",
            "Deciding what is nobody else's business.",
            """
Every member is **public** by default: readable and writable from anywhere. You
can write the keyword, and most codebases do not.

```ts
class Account {
  public balance: number = 0;   // same as: balance: number = 0;
}
```

`private` restricts a member to the class body:

```ts
class Account {
  private balance: number = 0;

  deposit(n: number): void {
    if (n <= 0) {
      return;
    }
    this.balance = this.balance + n;
  }

  formatted(): string {
    return `$${this.balance.toFixed(2)}`;
  }
}

const a = new Account();
a.deposit(10);
console.log(a.balance);
// TS2341: Property 'balance' is private and only accessible within class 'Account'.
```

## Why bother

Not secrecy — **invariants**. `deposit` refuses a non-positive amount. If
`balance` were public, `a.balance = -100` would walk straight past that rule,
and the class's promise would be worthless. `private` is what makes the
constructor-as-a-gate argument from lesson 2 hold for the whole lifetime of the
object, not just at construction.

The useful question is not "should this be private?" but **"if someone set this
from outside, would the object still make sense?"** If no, make it private and
offer a method.

## `private` is a compile-time rule. `#private` is real.

This surprises people, so it is worth proving:

```ts
class Row {
  desc: string = "coffee";
  private amount: number = 3;
  #tag: string = "food";

  visible(): string {
    return Object.keys(this).join(",");
  }
}
console.log(new Row().visible());     // desc,amount
```

`amount` is right there at runtime. `private` is erased with every other type —
it stops *your* code at compile time and nothing else. `#tag` is different: it
is a **private name**, part of JavaScript itself, and it is not a property at
all. `Object.keys` cannot see it, `JSON.stringify` will not serialise it, and
reaching for it from outside is a hard error:

```ts
console.log(new Row().#tag);
// TS18013: Property '#tag' is not accessible outside class 'Row'
//          because it has a private identifier.
```

**Which to use.** `private` is conventional, reads better in signatures, and
works with the rest of the type system (a subclass can widen it to
`protected`, an interface can be satisfied). Reach for `#` when the privacy has
to survive at runtime — a library boundary, or a field that must never be
serialised.

## `protected`

The third modifier: visible inside the class **and its subclasses**, but not
from outside. It only means something once a subclass exists, so it gets its
demonstration in lesson 8.

## Private methods

Modifiers work on methods too, and a private method is often the tidier win: it
says "this is a step in my own implementation, not part of my interface".

```ts
class Report {
  private rows: string[] = [];

  add(row: string): void { this.rows.push(row); }

  private bullet(row: string): string {
    return `- ${row}`;
  }

  render(): string {
    return this.rows.map((r) => this.bullet(r)).join("\\n");
  }
}
```

> ⚠️ **Common mistakes:** believing `private` hides anything at runtime;
> marking everything private and then adding a getter for each field, which is
> a public field with extra typing; and returning a private array directly,
> which hands the caller a reference to the very state you protected.
""",
            warmup=[
                _q("The default visibility of a class member is…",
                   ["private", "public", "protected", "readonly"], 1,
                   "You may write `public`, but it changes nothing."),
                _q("`private` at runtime is…",
                   ["enforced by the engine", "erased — an ordinary property remains",
                    "renamed", "frozen"], 1,
                   "Only `#name` is enforced when the program runs."),
                _q("`Object.keys(this)` on an instance with a `#tag` field includes…",
                   ["#tag", "tag", "neither — a private name is not a property", "all fields"], 2,
                   "That is exactly what makes it private at runtime."),
                _q("The good reason to make a field private is…",
                   ["secrecy", "to protect an invariant the methods maintain",
                    "performance", "to shorten the type"], 1,
                   "Otherwise anyone can set it past your rules."),
            ],
            exercises=[
                _ex("tscourse-w11-ac-1", "Hide the balance",
                    "Make `balance` reachable only from inside the class.",
                    'class Account {\n  private balance: number = 0;\n\n'
                    '  deposit(n: number): void {\n    this.balance = this.balance + n;\n  }\n\n'
                    '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                    'const a = new Account();\na.deposit(10);\na.deposit(5.5);\n'
                    'console.log(a.formatted());\n',
                    'private balance: number = 0;', [("", "$15.50")],
                    hints=["One modifier in front of the field declaration.",
                           "Write private balance: number = 0;"]),
                _ex("tscourse-w11-ac-2", "The invariant privacy buys",
                    "Refuse a deposit that is not positive, so the negative one is ignored.",
                    'class Account {\n  private balance: number = 0;\n\n'
                    '  deposit(n: number): void {\n'
                    '    if (n <= 0) {\n      return;\n    }\n'
                    '    this.balance = this.balance + n;\n  }\n\n'
                    '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                    'const a = new Account();\na.deposit(10);\na.deposit(-100);\n'
                    'console.log(a.formatted());\n',
                    'if (n <= 0) {\n      return;\n    }',
                    [("", "$10.00")],
                    hints=["Leave the method early when the argument is no good.",
                           "Because the field is private, this check cannot be bypassed."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ac-3", "A private name",
                    "Assign the constructor's argument to the `#code` field.",
                    'class Secret {\n  #code: number;\n\n'
                    '  constructor(code: number) {\n    this.#code = code;\n  }\n\n'
                    '  hint(): string {\n    return `${String(this.#code).length} digits`;\n  }\n}\n'
                    'console.log(new Secret(1234).hint());\n',
                    'this.#code = code;', [("", "4 digits")],
                    hints=["The `#` is part of the name, so it stays in every reference.",
                           "Write this.#code = code;"],
                    difficulty="Medium"),
                _ex("tscourse-w11-ac-4", "Which fields really exist",
                    "List the instance's own runtime property names, comma-separated. Watch which of the three appear.",
                    'class Row {\n  desc: string = "coffee";\n  private amount: number = 3;\n'
                    '  #tag: string = "food";\n\n'
                    '  visible(): string {\n    return Object.keys(this).join(",");\n  }\n}\n'
                    'console.log(new Row().visible());\n',
                    'return Object.keys(this).join(",");',
                    [("", "desc,amount")],
                    hints=["Week 7's Object.keys, applied to `this`.",
                           "`private` is erased, so it is still a property. A `#` name is not a property at all."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ac-5", "A private helper method",
                    "Write the private `bullet` helper that `render` calls once per row.",
                    'class Report {\n  private rows: string[] = [];\n\n'
                    '  add(row: string): void {\n    this.rows.push(row);\n  }\n\n'
                    '  private bullet(row: string): string {\n    return `- ${row}`;\n  }\n\n'
                    '  render(): string {\n'
                    '    return this.rows.map((r) => this.bullet(r)).join("\\n");\n  }\n}\n'
                    'const r = new Report();\nr.add("coffee");\nr.add("book");\n'
                    'console.log(r.render());\n',
                    'return `- ${row}`;', [("", "- coffee\n- book")],
                    hints=["A hyphen, a space, then the row.",
                           "It is private because it is a step in `render`, not part of the class's interface."]),
                _diagnose("tscourse-w11-ac-d1", "Reaching past the interface",
                          "TS2341: Property 'balance' is private and only accessible within class 'Account'.",
                          'class Account {\n  private balance: number = 0;\n\n'
                          '  deposit(n: number): void {\n'
                          '    if (n <= 0) {\n      return;\n    }\n'
                          '    this.balance = this.balance + n;\n  }\n\n'
                          '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                          'const a = new Account();\na.deposit(10);\n'
                          'console.log(`$${a.balance.toFixed(2)}`);\n',
                          'class Account {\n  private balance: number = 0;\n\n'
                          '  deposit(n: number): void {\n'
                          '    if (n <= 0) {\n      return;\n    }\n'
                          '    this.balance = this.balance + n;\n  }\n\n'
                          '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                          'const a = new Account();\na.deposit(10);\n'
                          'console.log(a.formatted());\n',
                          [("", "$10.00")],
                          hints=["The class already offers a way to read the balance as text.",
                                 "Do not widen the field — use the method that exists.",
                                 "Call a.formatted()."],
                          difficulty="Medium"),
                _diagnose("tscourse-w11-ac-d2", "The name that is not a property",
                          "TS18013: Property '#code' is not accessible outside class 'Secret' because it has a private identifier.",
                          'class Secret {\n  #code: number;\n\n'
                          '  constructor(code: number) {\n    this.#code = code;\n  }\n\n'
                          '  hint(): string {\n    return `${String(this.#code).length} digits`;\n  }\n}\n'
                          'const s = new Secret(1234);\nconsole.log(`${String(s.#code).length} digits`);\n',
                          'class Secret {\n  #code: number;\n\n'
                          '  constructor(code: number) {\n    this.#code = code;\n  }\n\n'
                          '  hint(): string {\n    return `${String(this.#code).length} digits`;\n  }\n}\n'
                          'const s = new Secret(1234);\nconsole.log(s.hint());\n',
                          [("", "4 digits")],
                          hints=["Unlike `private`, this one is enforced by the language itself — no cast can get round it.",
                                 "The class already exposes exactly this calculation."],
                          difficulty="Medium"),
                _fix("tscourse-w11-ac-fix1", "Fix the deposit that overwrites",
                     "`deposit` replaces the balance instead of adding to it, so two deposits print `$5.50` instead of `$15.50`.",
                     'class Account {\n  private balance: number = 0;\n\n'
                     '  deposit(n: number): void {\n    this.balance = n;\n  }\n\n'
                     '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                     'const a = new Account();\na.deposit(10);\na.deposit(5.5);\n'
                     'console.log(a.formatted());\n',
                     'class Account {\n  private balance: number = 0;\n\n'
                     '  deposit(n: number): void {\n    this.balance = this.balance + n;\n  }\n\n'
                     '  formatted(): string {\n    return `$${this.balance.toFixed(2)}`;\n  }\n}\n'
                     'const a = new Account();\na.deposit(10);\na.deposit(5.5);\n'
                     'console.log(a.formatted());\n',
                     [("", "$15.50")],
                     hints=["Both types are `number`, so nothing was flagged.",
                            "A deposit accumulates onto what is already there."]),
            ],
            quiz=[
                _q("A method returning its private array directly…",
                   ["is safe", "hands the caller a reference to the state you protected",
                    "copies it", "is a compile error"], 1,
                   "Return a copy, or a derived value, if the invariant matters."),
                _q("Prefer `#name` over `private` when…",
                   ["always", "the privacy must hold at runtime too — serialisation, a library boundary",
                    "never", "the field is a number"], 1,
                   "`private` is a compile-time courtesy."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w11-params", "Parameter properties & `readonly` fields",
            "Fields that are settled once built — and the shorthand for declaring them.",
            """
Week 8 already used `readonly` on an interface member. On a class field it means
the same thing, with one addition: the constructor may still assign it.

```ts
class Money {
  readonly cents: number;

  constructor(cents: number) {
    this.cents = cents;        // ✅ allowed — this is the constructor
  }
}

const m = new Money(325);
m.cents = 400;
// TS2540: Cannot assign to 'cents' because it is a read-only property.
```

## Value objects

Once the fields cannot change, an "operation" has to hand back a **new
instance** rather than editing this one:

```ts
class Money {
  readonly cents: number;
  constructor(cents: number) { this.cents = cents; }

  plus(other: Money): Money {
    return new Money(this.cents + other.cents);
  }
  formatted(): string {
    return `$${(this.cents / 100).toFixed(2)}`;
  }
}

const a = new Money(325);
const b = a.plus(new Money(175));
console.log(a.formatted());     // $3.25 — unchanged
console.log(b.formatted());     // $5.00
```

That shape is a **value object**, and it is how `Date`-done-right, every money
library and most of week 13 behave. The advantage is that a value you were
handed cannot be changed underneath you by whoever you handed it to.

`readonly` is shallow, exactly as in week 8 — a `readonly` field holding an
array still has a mutable array in it, unless the array type is `readonly` too:

```ts
readonly names: readonly string[];
```

Week 13 spends a whole lesson on that gap.

## Parameter properties

Declaring a field and assigning it from a same-named parameter is such a common
pattern that TypeScript has a shorthand. Put a modifier on the constructor
parameter and the field is declared and assigned for you:

```ts
class Money {
  constructor(public readonly cents: number) {}
}
```

That is the whole class. It is exactly equivalent to:

```ts
class Money {
  readonly cents: number;
  constructor(cents: number) {
    this.cents = cents;
  }
}
```

Any modifier works — `public`, `private`, `protected`, `readonly`, or a
combination — and it is very common in Angular and NestJS code, so you need to
be able to read it.

## Why these two exercises are checked, not run

Almost all of TypeScript is **erasable**: delete the annotations and valid
JavaScript remains. That is how this course runs your programs — the types are
stripped, and Node executes what is left.

A parameter property is one of the few pieces of TypeScript that is *not*
erasable. `public readonly cents: number` does not merely annotate; it **emits**
a `this.cents = cents` that exists nowhere in the source. Strip the types and
the assignment disappears with them, so the runner refuses it outright:

```
ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX: TypeScript parameter property is not
supported in strip-only mode
```

So the two parameter-property exercises below are graded by the **type-checker
alone** — press *Type-check*, and the claims in the harness either hold or they
do not. Everything else this week runs normally.

This is worth remembering rather than filing away: it is the same reason week 12
argues against `enum`. "Is this syntax erasable?" is a real question about real
build setups, not a quirk of this course.

> ⚠️ **Common mistakes:** expecting `readonly` to freeze a nested array;
> writing a value object's operation so it mutates and *also* returns `this`
> (then two variables are the same object); and assuming a parameter property
> works in every toolchain.
""",
            warmup=[
                _q("A `readonly` field may be assigned…",
                   ["never", "in the constructor only", "in any method", "from outside"], 1,
                   "Anywhere else is TS2540."),
                _q("A value object's `plus` should…",
                   ["mutate and return this", "return a new instance",
                    "return void", "throw"], 1,
                   "Otherwise the value the caller holds changes underneath them."),
                _q("`constructor(public readonly cents: number) {}` …",
                   ["only annotates", "declares the field AND emits the assignment",
                    "creates a getter", "is invalid"], 1,
                   "Which is exactly why it is not erasable."),
                _q("\"Erasable syntax\" means…",
                   ["it compiles fast", "deleting the types leaves valid, equivalent JavaScript",
                    "it has no runtime cost", "it is deprecated"], 1,
                   "Parameter properties and enums are the notable exceptions."),
            ],
            exercises=[
                _ex("tscourse-w11-pp-1", "A field that cannot change",
                    "Declare `cents` so it may only be assigned in the constructor.",
                    'class Money {\n  readonly cents: number;\n\n'
                    '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                    '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                    'console.log(new Money(325).formatted());\n',
                    'readonly cents: number;', [("", "$3.25")],
                    hints=["One modifier, and the constructor assignment is still allowed.",
                           "Write readonly cents: number;"]),
                _ex("tscourse-w11-pp-2", "An operation that returns a new value",
                    "`plus` must leave both operands untouched and hand back a new Money.",
                    'class Money {\n  readonly cents: number;\n\n'
                    '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                    '  plus(other: Money): Money {\n'
                    '    return new Money(this.cents + other.cents);\n  }\n\n'
                    '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                    'const a = new Money(325);\nconst b = a.plus(new Money(175));\n'
                    'console.log(`${a.formatted()} ${b.formatted()}`);\n',
                    'return new Money(this.cents + other.cents);',
                    [("", "$3.25 $5.00")],
                    hints=["The fields are readonly, so there is nothing to assign — construct instead.",
                           "Write return new Money(this.cents + other.cents);"],
                    difficulty="Medium"),
                _ex("tscourse-w11-pp-3", "A readonly array field",
                    "`with` should return a new Tags holding the old names plus one more.",
                    'class Tags {\n  readonly names: readonly string[];\n\n'
                    '  constructor(names: readonly string[]) {\n    this.names = names;\n  }\n\n'
                    '  with(name: string): Tags {\n'
                    '    return new Tags([...this.names, name]);\n  }\n\n'
                    '  render(): string {\n    return this.names.join(",");\n  }\n}\n'
                    'const t = new Tags(["food"]);\nconst t2 = t.with("home");\n'
                    'console.log(`${t.render()} | ${t2.render()}`);\n',
                    'return new Tags([...this.names, name]);',
                    [("", "food | food,home")],
                    hints=["`readonly string[]` has no push, which is the point — copy instead.",
                           "Spread the existing names into a fresh array with the new one on the end."],
                    difficulty="Medium"),
                _diagnose("tscourse-w11-pp-d1", "The assignment that came too late",
                          "TS2540: Cannot assign to 'cents' because it is a read-only property.",
                          'class Money {\n  readonly cents: number;\n\n'
                          '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                          '  plus(other: Money): Money {\n'
                          '    this.cents = this.cents + other.cents;\n    return this;\n  }\n\n'
                          '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                          'const a = new Money(325);\nconst b = a.plus(new Money(175));\n'
                          'console.log(`${a.formatted()} ${b.formatted()}`);\n',
                          'class Money {\n  readonly cents: number;\n\n'
                          '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                          '  plus(other: Money): Money {\n'
                          '    return new Money(this.cents + other.cents);\n  }\n\n'
                          '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                          'const a = new Money(325);\nconst b = a.plus(new Money(175));\n'
                          'console.log(`${a.formatted()} ${b.formatted()}`);\n',
                          [("", "$3.25 $5.00")],
                          hints=["Do not remove `readonly` — the field is meant to be settled.",
                                 "A value object builds a new instance rather than editing itself.",
                                 "Note what the expected output says about `a`: it must still be $3.25."],
                          difficulty="Medium"),
                _types("tscourse-w11-pp-t1", "The parameter-property shorthand",
                       "Write the constructor parameter so it declares a public, readonly "
                       "`cents` field of type number in one stroke. Graded by the type-checker: "
                       "a parameter property cannot be run here.",
                       'class Money {\n  constructor(public readonly cents: number) {}\n}\n',
                       'public readonly cents: number',
                       """
type _1 = Expect<Equal<Money["cents"], number>>;

const m = new Money(325);
// The field must be READONLY, so this assignment has to fail. If you leave off
// `readonly` the directive below goes unused, which is itself an error.
// @ts-expect-error
m.cents = 1;
""",
                       hints=["Two modifiers and a normal annotated parameter, in that order.",
                              "`public` says the field is visible; `readonly` says it is settled.",
                              "Write public readonly cents: number."],
                       difficulty="Medium"),
                _types("tscourse-w11-pp-t2", "A private parameter property",
                       "Declare `entries` as a private, readonly field of type `readonly number[]` "
                       "using the shorthand, so `count()` can read it and nothing outside can.",
                       'class Ledger {\n'
                       '  constructor(private readonly entries: readonly number[]) {}\n\n'
                       '  count(): number {\n    return this.entries.length;\n  }\n}\n',
                       'private readonly entries: readonly number[]',
                       """
const led = new Ledger([1, 2, 3]);
type _1 = Expect<Equal<typeof led, Ledger>>;

// The field must be PRIVATE, so reaching it from out here has to fail.
// @ts-expect-error
led.entries;
""",
                       hints=["Same shorthand as before, with a different visibility modifier.",
                              "The element type is already immutable: `readonly number[]`.",
                              "Write private readonly entries: readonly number[]."],
                       difficulty="Medium"),
                _fix("tscourse-w11-pp-fix1", "Fix the value object that mutates",
                     "`plus` edits the receiver and returns it, so `a` and `b` end up being the same object and this prints `$5.00 $5.00`. It should print `$3.25 $5.00`.",
                     'class Money {\n  cents: number;\n\n'
                     '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                     '  plus(other: Money): Money {\n'
                     '    this.cents = this.cents + other.cents;\n    return this;\n  }\n\n'
                     '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                     'const a = new Money(325);\nconst b = a.plus(new Money(175));\n'
                     'console.log(`${a.formatted()} ${b.formatted()}`);\n',
                     'class Money {\n  readonly cents: number;\n\n'
                     '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                     '  plus(other: Money): Money {\n'
                     '    return new Money(this.cents + other.cents);\n  }\n\n'
                     '  formatted(): string {\n    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                     'const a = new Money(325);\nconst b = a.plus(new Money(175));\n'
                     'console.log(`${a.formatted()} ${b.formatted()}`);\n',
                     [("", "$3.25 $5.00")],
                     hints=["`b` is not a second value here — it is the same object as `a`.",
                            "Return a new instance instead of editing this one.",
                            "Marking the field readonly would have made the compiler catch this for you."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`readonly names: readonly string[]` differs from `readonly names: string[]` because…",
                   ["nothing", "the second still allows names.push(...)",
                    "the first is slower", "the second is invalid"], 1,
                   "`readonly` on the field only stops reassigning the field itself."),
                _q("A parameter property fails to RUN in this course because…",
                   ["it is deprecated", "it emits an assignment, so it is not erasable syntax",
                    "it needs a decorator", "the judge forbids it"], 1,
                   "Stripping the types would delete the assignment along with them."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w11-accessors", "Getters, setters & `static`",
            "Computed members that read like fields, and members that belong to the class.",
            """
## Getters

A getter is a method you call without parentheses:

```ts
class Expense {
  desc: string;
  cents: number;
  constructor(desc: string, cents: number) {
    this.desc = desc;
    this.cents = cents;
  }

  get dollars(): number {
    return this.cents / 100;
  }
}

const e = new Expense("coffee", 325);
console.log(e.dollars);       // 3.25 — no ()
```

This is the fix for lesson 2's stale-derived-field problem. `dollars` is
computed on every read, so it cannot disagree with `cents`. The cost is that a
getter *looks* free: `e.dollars` might be a division or might walk a thousand
rows, and the call site cannot tell. Keep getters cheap, and use a normal method
when the work is real.

## Setters

A setter runs on assignment, which makes it the one place an assignment can be
checked:

```ts
class Thermostat {
  private celsius: number = 20;

  get temp(): number {
    return this.celsius;
  }
  set temp(value: number) {
    this.celsius = value < 5 ? 5 : value;
  }
}

const t = new Thermostat();
t.temp = 22;
console.log(t.temp);     // 22
t.temp = -40;
console.log(t.temp);     // 5 — clamped
```

Note the shape: a `private` field holding the state, and a getter/setter pair
as the public face of it. That is the standard way to keep an invariant while
still offering field-like syntax.

**The classic bug** is to assign to the accessor from inside itself:

```ts
set temp(value: number) {
  this.temp = value;      // calls the setter again... and again
}
```

It compiles, then dies with a stack overflow. The setter must write to the
*field*, never to itself.

A getter with no setter is read-only from outside, which is often exactly what
you want.

## `static`

A static member belongs to the **class**, not to any instance:

```ts
class Expense {
  static made: number = 0;
  desc: string;

  constructor(desc: string) {
    this.desc = desc;
    Expense.made = Expense.made + 1;      // note: the CLASS name, not `this`
  }
}

new Expense("a");
new Expense("b");
console.log(Expense.made);      // 2
```

Reach for it through an instance and TypeScript catches you:

```ts
const e = new Expense("c");
console.log(e.made);
// TS2576: Property 'made' does not exist on type 'Expense'.
//         Did you mean to access the static member 'Expense.made' instead?
```

**Static factories** are the most useful case by far — a named constructor that
does the parsing or validating:

```ts
class Expense {
  desc: string;
  cents: number;
  constructor(desc: string, cents: number) {
    this.desc = desc;
    this.cents = cents;
  }

  static fromLine(line: string): Expense {
    const parts = line.split(" ");
    return new Expense(parts[0] ?? "", Math.round(Number(parts[1] ?? "0") * 100));
  }
}

Expense.fromLine("coffee 3.25");
```

A class can have only one constructor, so a static factory is how you offer a
second way in — and it gets a *name*, which `new Expense(…)` never does.

**Static constants** round it out: `static readonly TAX: number = 0.1`, reached
as `Rate.TAX`, with the class as the namespace.

> ⚠️ **Common mistakes:** a setter that assigns to itself; expecting `this` to
> mean the class inside a static method (it does not mean the instance either —
> just name the class); and a getter that hides expensive work.
""",
            warmup=[
                _q("A getter is read as…",
                   ["e.dollars()", "e.dollars", "e.get(\"dollars\")", "Expense.dollars"], 1,
                   "It looks exactly like a field."),
                _q("`set temp(v) { this.temp = v; }` does what?",
                   ["works fine", "calls itself until the stack overflows",
                    "is a compile error", "sets a private field"], 1,
                   "The setter must write to the backing field."),
                _q("`static made` is reached as…",
                   ["instance.made", "Expense.made", "this.made anywhere", "both"], 1,
                   "Through an instance is TS2576."),
                _q("The main reason to write a static factory is…",
                   ["speed", "a second, NAMED way to construct — and a place to parse or validate",
                    "to avoid `new`", "privacy"], 1,
                   "A class only gets one constructor."),
            ],
            exercises=[
                _ex("tscourse-w11-gs-1", "A computed member",
                    "Return the amount in dollars, computed from the cents field.",
                    'class Expense {\n  desc: string;\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    this.desc = desc;\n    this.cents = cents;\n  }\n\n'
                    '  get dollars(): number {\n    return this.cents / 100;\n  }\n}\n'
                    'const e = new Expense("coffee", 325);\n'
                    'console.log(e.dollars.toFixed(2));\n',
                    'return this.cents / 100;', [("", "3.25")],
                    hints=["A hundred cents to the dollar.",
                           "Write return this.cents / 100;"]),
                _ex("tscourse-w11-gs-2", "Read it like a field",
                    "Use the getter — no parentheses.",
                    'class Expense {\n  desc: string;\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    this.desc = desc;\n    this.cents = cents;\n  }\n\n'
                    '  get dollars(): number {\n    return this.cents / 100;\n  }\n}\n'
                    'const e = new Expense("coffee", 325);\n'
                    'console.log(`${e.desc} costs ${e.dollars.toFixed(2)}`);\n',
                    'e.dollars', [("", "coffee costs 3.25")],
                    hints=["A getter is accessed exactly like a field.",
                           "Write e.dollars, with no ()."]),
                _ex("tscourse-w11-gs-3", "A setter that clamps",
                    "Store the value, but never let it fall below 5.",
                    'class Thermostat {\n  private celsius: number = 20;\n\n'
                    '  get temp(): number {\n    return this.celsius;\n  }\n\n'
                    '  set temp(value: number) {\n'
                    '    this.celsius = value < 5 ? 5 : value;\n  }\n}\n'
                    'const t = new Thermostat();\nt.temp = 22;\nconsole.log(t.temp);\n'
                    't.temp = -40;\nconsole.log(t.temp);\n',
                    'this.celsius = value < 5 ? 5 : value;',
                    [("", "22\n5")],
                    hints=["Write to the private field, never to `this.temp`.",
                           "A conditional picks 5 when the value is too low."],
                    difficulty="Medium"),
                _ex("tscourse-w11-gs-4", "Count every instance",
                    "Increment the class-level counter each time one is built.",
                    'class Expense {\n  static made: number = 0;\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n'
                    '    this.desc = desc;\n    Expense.made = Expense.made + 1;\n  }\n}\n'
                    'new Expense("a");\nnew Expense("b");\nconsole.log(Expense.made);\n',
                    'Expense.made = Expense.made + 1;', [("", "2")],
                    hints=["The counter is on the class, so name the class.",
                           "Write Expense.made = Expense.made + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w11-gs-5", "A static factory",
                    "Parse `desc amount` into an instance, storing the amount as integer cents.",
                    'class Expense {\n  desc: string;\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    this.desc = desc;\n    this.cents = cents;\n  }\n\n'
                    '  static fromLine(line: string): Expense {\n'
                    '    const parts = line.split(" ");\n'
                    '    return new Expense(parts[0] ?? "", Math.round(Number(parts[1] ?? "0") * 100));\n'
                    '  }\n\n'
                    '  formatted(): string {\n'
                    '    return `${this.desc} $${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                    'console.log(Expense.fromLine("coffee 3.25").formatted());\n',
                    'return new Expense(parts[0] ?? "", Math.round(Number(parts[1] ?? "0") * 100));',
                    [("", "coffee $3.25")],
                    hints=["Under noUncheckedIndexedAccess each part is `string | undefined`, so default both.",
                           "Multiply by 100 and round, so 3.25 becomes the integer 325.",
                           'Write return new Expense(parts[0] ?? "", Math.round(Number(parts[1] ?? "0") * 100));'],
                    difficulty="Medium"),
                _ex("tscourse-w11-gs-6", "A static constant and a static method",
                    "Apply the class's own tax rate to the amount.",
                    'class Rate {\n  static readonly TAX: number = 0.1;\n\n'
                    '  static withTax(amount: number): number {\n'
                    '    return amount * (1 + Rate.TAX);\n  }\n}\n'
                    'console.log(Rate.withTax(20).toFixed(2));\n',
                    'return amount * (1 + Rate.TAX);', [("", "22.00")],
                    hints=["The constant is on the class, so reach it as Rate.TAX.",
                           "Multiply by one plus the rate."]),
                _diagnose("tscourse-w11-gs-d1", "The static reached the wrong way",
                          "TS2576: Property 'made' does not exist on type 'Expense'. Did you mean to access the static member 'Expense.made' instead?",
                          'class Expense {\n  static made: number = 0;\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n'
                          '    this.desc = desc;\n    Expense.made = Expense.made + 1;\n  }\n}\n'
                          'const a = new Expense("a");\nnew Expense("b");\nconsole.log(a.made);\n',
                          'class Expense {\n  static made: number = 0;\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n'
                          '    this.desc = desc;\n    Expense.made = Expense.made + 1;\n  }\n}\n'
                          'const a = new Expense("a");\nnew Expense("b");\nconsole.log(Expense.made);\n',
                          [("", "2")],
                          hints=["A static member is not on the instance at all.",
                                 "The error message names the fix."],
                          difficulty="Easy"),
                _fix("tscourse-w11-gs-fix1", "Fix the setter that never stops",
                     "The setter assigns to itself, so `t.temp = 22` recurses until the stack runs out. It should print 22.",
                     'class Thermostat {\n  private celsius: number = 20;\n\n'
                     '  get temp(): number {\n    return this.celsius;\n  }\n\n'
                     '  set temp(value: number) {\n    this.temp = value;\n  }\n}\n'
                     'const t = new Thermostat();\nt.temp = 22;\nconsole.log(t.temp);\n',
                     'class Thermostat {\n  private celsius: number = 20;\n\n'
                     '  get temp(): number {\n    return this.celsius;\n  }\n\n'
                     '  set temp(value: number) {\n    this.celsius = value;\n  }\n}\n'
                     'const t = new Thermostat();\nt.temp = 22;\nconsole.log(t.temp);\n',
                     [("", "22")],
                     hints=["`this.temp = …` is not a field assignment — it is a call to this very setter.",
                            "Write to the private field that backs the accessor."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A getter with no setter is…",
                   ["an error", "read-only from outside", "the same as a field", "static"], 1,
                   "Which is often exactly the intent."),
                _q("The risk of a getter is that…",
                   ["it cannot be typed", "the call site cannot tell how much work it does",
                    "it runs once", "it is public"], 1,
                   "Field syntax implies it is cheap, so keep it cheap."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w11-implements", "A class meeting an interface",
            "`implements` is a check, not inheritance.",
            """
Week 8's interfaces described object shapes. A class can be asked to satisfy
one:

```ts
interface Priced {
  amount: number;
  label(): string;
}

class Expense implements Priced {
  desc: string;
  amount: number;

  constructor(desc: string, amount: number) {
    this.desc = desc;
    this.amount = amount;
  }

  label(): string {
    return `${this.desc} (${this.amount})`;
  }
}
```

`implements` **copies nothing**. It adds one check: does this class have every
member the interface requires, with compatible types? Leave `label` out and:

```
TS2420: Class 'Expense' incorrectly implements interface 'Priced'.
        Property 'label' is missing in type 'Expense' but required in type 'Priced'.
```

Note also that `Expense` has an *extra* field, `desc`, and that is fine. An
interface is a floor, not a ceiling.

## The part that surprises people

`implements` is not what makes the class usable as a `Priced`. This works with
no `implements` clause at all:

```ts
class Refund {              // no implements
  amount: number;
  constructor(amount: number) { this.amount = -amount; }
  label(): string { return "refund"; }
}

function describe(p: Priced): string {
  return `${p.label()} = ${p.amount}`;
}

describe(new Refund(4));    // ✅ accepted
```

TypeScript checks **shapes, not names**. `Refund` has the right members, so it
is a `Priced` whether or not it says so. And a plain object is too:

```ts
const plain: Priced = { amount: 9, label: (): string => "plain 9" };
describe(plain);            // ✅ also accepted
```

So what is `implements` *for*? It moves the error. Without it, a class that
drifts out of shape compiles fine and fails at every call site that expected
the interface. With it, the error lands on the class itself, which is where the
mistake is. Declare it for the documentation and the early failure — never
because the code would not otherwise work.

That rule — shapes, not names — is the entire subject of week 12.

## Several interfaces

```ts
interface Priced { amount: number; }
interface Labelled { label(): string; }

class Expense implements Priced, Labelled { … }
```

A class may implement any number of them. This is where interfaces beat the
abstract classes of lesson 9, which you only get one of.

## The usual pattern

Type the *variable*, not just the class: `const rows: Priced[] = [...]` lets a
loop treat expenses and refunds identically, and is how you get polymorphism
without inheritance.

> ⚠️ **Common mistakes:** thinking `implements` inherits something; thinking it
> is required for a class to be accepted where the interface is expected; and
> annotating a method's parameter as the class when the interface would do,
> which needlessly refuses everything else that fits.
""",
            warmup=[
                _q("`implements` copies…",
                   ["fields", "methods", "nothing — it only checks", "the constructor"], 2,
                   "It is an assertion about the class, checked at compile time."),
                _q("A class with the right members but no `implements` clause…",
                   ["is rejected where the interface is expected", "is accepted — shapes, not names",
                    "needs a cast", "is an error"], 1,
                   "Structural typing, which week 12 is about."),
                _q("A class implementing an interface may have extra members?",
                   ["no", "yes — the interface is a floor, not a ceiling", "only private ones",
                    "only methods"], 1,
                   "Only the required members are checked."),
                _q("A class missing a required method gives…",
                   ["TS2564", "TS2420", "TS2341", "no error"], 1,
                   "'incorrectly implements interface'."),
            ],
            exercises=[
                _ex("tscourse-w11-im-1", "Satisfy the contract",
                    "Write the `label` method the interface requires.",
                    'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                    'class Expense implements Priced {\n  desc: string;\n  amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                    '  label(): string {\n    return `${this.desc} (${this.amount})`;\n  }\n}\n'
                    'console.log(new Expense("coffee", 3).label());\n',
                    'return `${this.desc} (${this.amount})`;',
                    [("", "coffee (3)")],
                    hints=["The description, a space, then the amount in parentheses."]),
                _ex("tscourse-w11-im-2", "One function, two kinds of value",
                    "Write `describe` against the interface, so both a class instance and a plain object work.",
                    'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                    'class Expense implements Priced {\n  amount: number;\n\n'
                    '  constructor(amount: number) {\n    this.amount = amount;\n  }\n\n'
                    '  label(): string {\n    return `expense ${this.amount}`;\n  }\n}\n'
                    'function describe(p: Priced): string {\n'
                    '  return `${p.label()} = ${p.amount}`;\n}\n'
                    'const plain: Priced = { amount: 9, label: (): string => "plain 9" };\n'
                    'console.log(describe(new Expense(3)));\nconsole.log(describe(plain));\n',
                    'return `${p.label()} = ${p.amount}`;',
                    [("", "expense 3 = 3\nplain 9 = 9")],
                    hints=["The parameter is the interface, so only its members are available.",
                           "Call the method, then an equals sign, then the field."],
                    difficulty="Medium"),
                _ex("tscourse-w11-im-3", "A list typed by the interface",
                    "Declare the array as the interface type so both classes can sit in it.",
                    'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                    'class Expense implements Priced {\n  amount: number;\n'
                    '  constructor(amount: number) {\n    this.amount = amount;\n  }\n'
                    '  label(): string {\n    return "expense";\n  }\n}\n'
                    'class Refund implements Priced {\n  amount: number;\n'
                    '  constructor(amount: number) {\n    this.amount = -amount;\n  }\n'
                    '  label(): string {\n    return "refund";\n  }\n}\n'
                    'const rows: Priced[] = [new Expense(10), new Refund(4)];\n'
                    'let total = 0;\nfor (const r of rows) {\n  total = total + r.amount;\n}\n'
                    'console.log(`${rows.map((r) => r.label()).join(",")} ${total}`);\n',
                    'const rows: Priced[] = [new Expense(10), new Refund(4)];',
                    [("", "expense,refund 6")],
                    hints=["Annotate the array with the interface, not with either class.",
                           "Then a loop can treat every element the same way."],
                    difficulty="Medium"),
                _ex("tscourse-w11-im-4", "Two interfaces at once",
                    "Declare that the class satisfies both contracts.",
                    'interface Priced {\n  amount: number;\n}\n'
                    'interface Labelled {\n  label(): string;\n}\n'
                    'class Expense implements Priced, Labelled {\n'
                    '  amount: number;\n\n'
                    '  constructor(amount: number) {\n    this.amount = amount;\n  }\n\n'
                    '  label(): string {\n    return `expense ${this.amount}`;\n  }\n}\n'
                    'const e = new Expense(7);\nconsole.log(`${e.label()} / ${e.amount}`);\n',
                    'implements Priced, Labelled',
                    [("", "expense 7 / 7")],
                    hints=["One clause, both names, separated by a comma.",
                           "Write implements Priced, Labelled."]),
                _design("tscourse-w11-im-des1", "Recover the contract",
                        "The interface declaration has been removed. Work out what `Row` must be "
                        "from how the class and `render` use it, and write it back.",
                        'interface Row {\n  desc: string;\n  cents: number;\n}\n'
                        'class Expense implements Row {\n  desc: string;\n  cents: number;\n\n'
                        '  constructor(desc: string, cents: number) {\n'
                        '    this.desc = desc;\n    this.cents = cents;\n  }\n}\n'
                        'function render(r: Row): string {\n'
                        '  return `${r.desc}: ${(r.cents / 100).toFixed(2)}`;\n}\n'
                        'console.log(render(new Expense("coffee", 325)));\n',
                        'interface Row {\n  desc: string;\n  cents: number;\n}',
                        """
type _1 = Expect<Equal<Row, { desc: string; cents: number }>>;
""",
                        [("", "coffee: 3.25")],
                        hints=["`render` reads two members off it; the class declares exactly those.",
                               "`desc` is used as a string and `cents` is divided, so it is a number.",
                               "Two required members, no extras — the assertion checks it exactly."],
                        difficulty="Medium"),
                _diagnose("tscourse-w11-im-d1", "The contract that is not met",
                          "TS2420: Class 'Expense' incorrectly implements interface 'Priced'. Property 'label' is missing in type 'Expense' but required in type 'Priced'.",
                          'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                          'class Expense implements Priced {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                          '  describe(): string {\n    return `${this.desc} (${this.amount})`;\n  }\n}\n'
                          'console.log(new Expense("coffee", 3).describe());\n',
                          'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                          'class Expense implements Priced {\n  desc: string;\n  amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                          '  label(): string {\n    return `${this.desc} (${this.amount})`;\n  }\n}\n'
                          'console.log(new Expense("coffee", 3).label());\n',
                          [("", "coffee (3)")],
                          hints=["The method is there — under the wrong name.",
                                 "The interface asks for `label`, so rename the method and its call."],
                          difficulty="Medium"),
                _fix("tscourse-w11-im-fix1", "Fix the label that reads the wrong field",
                     "`label` reports the amount where the description belongs, so this prints `3 (3)` instead of `coffee (3)`.",
                     'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                     'class Expense implements Priced {\n  desc: string;\n  amount: number;\n\n'
                     '  constructor(desc: string, amount: number) {\n'
                     '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                     '  label(): string {\n    return `${this.amount} (${this.amount})`;\n  }\n}\n'
                     'console.log(new Expense("coffee", 3).label());\n',
                     'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                     'class Expense implements Priced {\n  desc: string;\n  amount: number;\n\n'
                     '  constructor(desc: string, amount: number) {\n'
                     '    this.desc = desc;\n    this.amount = amount;\n  }\n\n'
                     '  label(): string {\n    return `${this.desc} (${this.amount})`;\n  }\n}\n'
                     'console.log(new Expense("coffee", 3).label());\n',
                     [("", "coffee (3)")],
                     hints=["Interpolation turns anything into a string, so the compiler saw no problem.",
                            "The first slot should be the description."]),
            ],
            quiz=[
                _q("`implements` is worth writing because…",
                   ["the code needs it", "it moves the error onto the class instead of every call site",
                    "it inherits code", "it is faster"], 1,
                   "Structural typing would have accepted the class anyway."),
                _q("A method parameter should usually be annotated with…",
                   ["the concrete class", "the narrowest interface that has what the function uses",
                    "any", "unknown"], 1,
                   "Annotating the class refuses everything else that fits."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w11-extends", "`extends` & `super`",
            "Specialising a class, and reaching the version you replaced.",
            """
`extends` makes a class a **subclass**: it inherits every field and method of
the parent and may add or replace members.

```ts
class Entry {
  desc: string;

  constructor(desc: string) {
    this.desc = desc;
  }

  line(): string {
    return this.desc;
  }
}

class Expense extends Entry {
  cents: number;

  constructor(desc: string, cents: number) {
    super(desc);              // run the parent constructor FIRST
    this.cents = cents;
  }
}

const e = new Expense("coffee", 325);
console.log(e.line());        // coffee — inherited, not rewritten
console.log(e.cents);         // 325
```

## `super(...)` and the two rules about it

A derived constructor **must** call `super`, and must do it **before** touching
`this`:

```
TS2377:  Constructors for derived classes must contain a 'super' call.
TS17009: 'super' must be called before accessing 'this' in the constructor
         of a derived class.
```

Both exist for the same reason: until the parent constructor has run, the
parent's fields do not exist yet, so `this` is not a complete object.

## Overriding

Declare a method the parent already has and yours wins:

```ts
class Expense extends Entry {
  …
  line(): string {
    return `${this.desc} $${(this.cents / 100).toFixed(2)}`;
  }
}
```

The optional `override` modifier says you meant to — and turns a typo into an
error rather than a silent extra method.

**`super.line()`** calls the parent's version, which is how you *extend* rather
than replace:

```ts
line(): string {
  return `${super.line()} $${(this.cents / 100).toFixed(2)}`;
}
```

Note the difference from `this.line()`: that would call *your* method again, and
recurse until the stack ran out.

## `protected`, at last

Lesson 4 left this one hanging. A `protected` member is visible inside the class
**and its subclasses**, but not from outside:

```ts
class Entry {
  protected desc: string;
  constructor(desc: string) { this.desc = desc; }
}

class Expense extends Entry {
  line(): string { return this.desc; }     // ✅ a subclass may read it
}

new Expense("coffee", 325).desc;
// TS2445: Property 'desc' is protected and only accessible within class
//         'Entry' and its subclasses.
```

Use it for state the hierarchy shares. Use `private` when even the subclasses
have no business with it — which is more often than people expect.

## Polymorphism

The payoff: one array, one loop, different behaviour.

```ts
const rows: Entry[] = [new Entry("note"), new Expense("coffee", 325)];
for (const r of rows) {
  console.log(r.line());     // whichever line() the object actually has
}
```

And `instanceof` narrows back down when you need the subclass specifically —
the same narrowing you used on `Error` in week 9:

```ts
for (const r of rows) {
  if (r instanceof Expense) {
    console.log(r.cents);    // narrowed to Expense
  }
}
```

## A word of restraint

Inheritance is the most over-used tool in this week. It couples the subclass to
the parent's internals permanently, and you get exactly one parent. Reach for it
when the subclass genuinely **is** a kind of the parent *and* there is shared
code to inherit. Otherwise use an interface (lesson 7) or composition
(lesson 9).

> ⚠️ **Common mistakes:** forgetting `super(...)`; calling `this.method()` where
> you meant `super.method()`; putting fields in the parent that only one
> subclass uses; and building three levels of hierarchy where an interface would
> have done.
""",
            warmup=[
                _q("A derived constructor must call `super(...)`…",
                   ["last", "before any use of `this`", "only when it has fields", "never"], 1,
                   "TS17009 otherwise."),
                _q("Omitting the `super` call entirely gives…",
                   ["TS17009", "TS2377", "TS2420", "no error"], 1,
                   "'Constructors for derived classes must contain a super call.'"),
                _q("`super.line()` inside your `line()` calls…",
                   ["itself", "the parent's line", "a static method", "the constructor"], 1,
                   "`this.line()` would recurse."),
                _q("A `protected` field is readable…",
                   ["anywhere", "in the class and its subclasses", "in the class only",
                    "only in the constructor"], 1,
                   "From outside is TS2445."),
            ],
            exercises=[
                _ex("tscourse-w11-ex-1", "Call the parent constructor",
                    "Run the parent's constructor before assigning the subclass's own field.",
                    'class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  line(): string {\n    return this.desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n}\n'
                    'const e = new Expense("coffee", 325);\n'
                    'console.log(`${e.line()} ${e.cents}`);\n',
                    'super(desc);', [("", "coffee 325")],
                    hints=["The parent takes the description.",
                           "Write super(desc);"]),
                _ex("tscourse-w11-ex-2", "Override a method",
                    "Replace the inherited `line` so an expense shows its amount too.",
                    'class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  line(): string {\n    return this.desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n\n'
                    '  override line(): string {\n'
                    '    return `${this.desc} $${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                    'console.log(new Entry("note").line());\n'
                    'console.log(new Expense("coffee", 325).line());\n',
                    'return `${this.desc} $${(this.cents / 100).toFixed(2)}`;',
                    [("", "note\ncoffee $3.25")],
                    hints=["The description, then the amount as dollars with two decimals.",
                           "The parent's own instances are unaffected."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ex-3", "Extend instead of replace",
                    "Build on the parent's version rather than repeating it.",
                    'class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  line(): string {\n    return this.desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n\n'
                    '  override line(): string {\n'
                    '    return `${super.line()} $${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
                    'console.log(new Expense("coffee", 325).line());\n',
                    'super.line()', [("", "coffee $3.25")],
                    hints=["`this.line()` would call this very method again.",
                           "Write super.line()."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ex-4", "State the hierarchy shares",
                    "Declare `desc` so the subclass may read it but nothing outside can.",
                    'class Entry {\n  protected desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n\n'
                    '  line(): string {\n    return `${this.desc}=${this.cents}`;\n  }\n}\n'
                    'console.log(new Expense("coffee", 325).line());\n',
                    'protected desc: string;', [("", "coffee=325")],
                    hints=["`private` would be too tight — the subclass has to read it.",
                           "Write protected desc: string;"],
                    difficulty="Medium"),
                _ex("tscourse-w11-ex-5", "One loop, two behaviours",
                    "Type the array as the parent so both kinds can sit in it.",
                    'class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  line(): string {\n    return this.desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n\n'
                    '  override line(): string {\n    return `${this.desc} ${this.cents}`;\n  }\n}\n'
                    'const rows: Entry[] = [new Entry("note"), new Expense("coffee", 325)];\n'
                    'for (const r of rows) {\n  console.log(r.line());\n}\n',
                    'const rows: Entry[] = [new Entry("note"), new Expense("coffee", 325)];',
                    [("", "note\ncoffee 325")],
                    hints=["A subclass instance is acceptable wherever the parent type is expected.",
                           "Annotate the array with the parent type."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ex-6", "Narrow back to the subclass",
                    "Test whether the entry is really an Expense so its own field is reachable.",
                    'class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                    'class Expense extends Entry {\n  cents: number;\n\n'
                    '  constructor(desc: string, cents: number) {\n'
                    '    super(desc);\n    this.cents = cents;\n  }\n}\n'
                    'const rows: Entry[] = [new Entry("note"), new Expense("coffee", 325)];\n'
                    'for (const r of rows) {\n'
                    '  if (r instanceof Expense) {\n'
                    '    console.log(`expense ${r.cents}`);\n'
                    '  } else {\n'
                    '    console.log(`entry ${r.desc}`);\n  }\n}\n',
                    'r instanceof Expense', [("", "entry note\nexpense 325")],
                    hints=["The same narrowing you used on Error in week 9.",
                           "Write r instanceof Expense."],
                    difficulty="Medium"),
                _diagnose("tscourse-w11-ex-d1", "The constructor that skipped its parent",
                          "TS2377: Constructors for derived classes must contain a 'super' call.",
                          'class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                          'class Expense extends Entry {\n  cents: number;\n\n'
                          '  constructor(desc: string, cents: number) {\n'
                          '    this.cents = cents;\n  }\n\n'
                          '  line(): string {\n    return `${this.desc} ${this.cents}`;\n  }\n}\n'
                          'console.log(new Expense("coffee", 325).line());\n',
                          'class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                          'class Expense extends Entry {\n  cents: number;\n\n'
                          '  constructor(desc: string, cents: number) {\n'
                          '    super(desc);\n    this.cents = cents;\n  }\n\n'
                          '  line(): string {\n    return `${this.desc} ${this.cents}`;\n  }\n}\n'
                          'console.log(new Expense("coffee", 325).line());\n',
                          [("", "coffee 325")],
                          hints=["Nothing has set the parent's `desc` field.",
                                 "Add the parent call as the first statement, passing the description."],
                          difficulty="Medium"),
                _diagnose("tscourse-w11-ex-d2", "Protected from out here",
                          "TS2445: Property 'desc' is protected and only accessible within class 'Entry' and its subclasses.",
                          'class Entry {\n  protected desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                          'class Expense extends Entry {\n  cents: number;\n\n'
                          '  constructor(desc: string, cents: number) {\n'
                          '    super(desc);\n    this.cents = cents;\n  }\n\n'
                          '  line(): string {\n    return `${this.desc}=${this.cents}`;\n  }\n}\n'
                          'const e = new Expense("coffee", 325);\n'
                          'console.log(`${e.desc}=${e.cents}`);\n',
                          'class Entry {\n  protected desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n}\n'
                          'class Expense extends Entry {\n  cents: number;\n\n'
                          '  constructor(desc: string, cents: number) {\n'
                          '    super(desc);\n    this.cents = cents;\n  }\n\n'
                          '  line(): string {\n    return `${this.desc}=${this.cents}`;\n  }\n}\n'
                          'const e = new Expense("coffee", 325);\nconsole.log(e.line());\n',
                          [("", "coffee=325")],
                          hints=["`protected` deliberately stops the outside world, subclass or not.",
                                 "The subclass already publishes exactly this string.",
                                 "Do not widen the field to public — call the method."],
                          difficulty="Medium"),
                _fix("tscourse-w11-ex-fix1", "Fix the argument passed to `super`",
                     "The subclass hands the parent the amount where the description belongs, so this prints `325 325` instead of `coffee 325`.",
                     'class Entry {\n  desc: string;\n\n'
                     '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                     '  line(): string {\n    return this.desc;\n  }\n}\n'
                     'class Expense extends Entry {\n  cents: number;\n\n'
                     '  constructor(desc: string, cents: number) {\n'
                     '    super(String(cents));\n    this.cents = cents;\n  }\n\n'
                     '  override line(): string {\n    return `${super.line()} ${this.cents}`;\n  }\n}\n'
                     'console.log(new Expense("coffee", 325).line());\n',
                     'class Entry {\n  desc: string;\n\n'
                     '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                     '  line(): string {\n    return this.desc;\n  }\n}\n'
                     'class Expense extends Entry {\n  cents: number;\n\n'
                     '  constructor(desc: string, cents: number) {\n'
                     '    super(desc);\n    this.cents = cents;\n  }\n\n'
                     '  override line(): string {\n    return `${super.line()} ${this.cents}`;\n  }\n}\n'
                     'console.log(new Expense("coffee", 325).line());\n',
                     [("", "coffee 325")],
                     hints=["`String(cents)` is a string, so the parent's parameter type was satisfied.",
                            "The parent wants the description, and the subclass has one."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`override` on a method…",
                   ["is required", "documents the intent and turns a typo into an error",
                    "changes dispatch", "makes it static"], 1,
                   "Without it, a misspelled override is just a new method."),
                _q("Inheritance is the wrong tool when…",
                   ["there is shared code", "the subclass is not really a kind of the parent",
                    "there are two subclasses", "the parent is abstract"], 1,
                   "An interface or composition says it better."),
            ],
        ),
        # ---- Lesson 9 --------------------------------------------------
        _lesson(
            "w11-abstract", "`abstract` classes, and when not to inherit",
            "Demanding a hook from every subclass — and the alternative.",
            """
Sometimes a base class has real code to share but is not a complete thing on its
own. `abstract` says so:

```ts
abstract class Entry {
  desc: string;

  constructor(desc: string) {
    this.desc = desc;
  }

  abstract cents(): number;          // no body — every subclass must supply one

  line(): string {                   // concrete, and shared
    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;
  }
}
```

Two new things. The class cannot be instantiated:

```ts
new Entry("x");
// TS2511: Cannot create an instance of an abstract class.
```

And an `abstract` member is a signature with no implementation. A concrete
subclass that fails to provide one is an error:

```
TS2515: Non-abstract class 'Fixed' does not implement inherited abstract
        member cents from class 'Entry'.
```

## The template method

Look again at `line()`. It is finished code, written once, that calls a method
which does not exist yet. Each subclass fills in the hole:

```ts
class Fixed extends Entry {
  private amount: number;
  constructor(desc: string, amount: number) {
    super(desc);
    this.amount = amount;
  }
  cents(): number {
    return this.amount;
  }
}

class Hourly extends Entry {
  private hours: number;
  private rate: number;
  constructor(desc: string, hours: number, rate: number) {
    super(desc);
    this.hours = hours;
    this.rate = rate;
  }
  cents(): number {
    return this.hours * this.rate;
  }
}

const rows: Entry[] = [new Fixed("coffee", 325), new Hourly("tutor", 2, 2500)];
for (const r of rows) {
  console.log(r.line());
}
// coffee $3.25
// tutor $50.00
```

That shape — a concrete method calling an abstract hook — is the **template
method** pattern, and it is the single best reason to reach for an abstract
class.

## `abstract class` or `interface`?

| | interface | abstract class |
|---|---|---|
| carries implementation | no | yes |
| how many per class | any number | exactly one |
| exists at runtime | no | yes (so `instanceof` works) |
| can have constructors, private state | no | yes |

**Rule of thumb:** if the base has no code to give, use an interface. The moment
you find yourself writing an abstract class whose every member is abstract, you
have written an interface the hard way.

## When not to inherit at all

Inheritance ties a subclass to its parent forever, and you only get one parent.
Very often what you actually wanted was to **hold** the other thing rather than
to *be* it:

```ts
interface Fee {
  cents(): number;
}

class Flat implements Fee {
  private amount: number;
  constructor(amount: number) { this.amount = amount; }
  cents(): number { return this.amount; }
}

class Entry {
  private desc: string;
  private fee: Fee;

  constructor(desc: string, fee: Fee) {
    this.desc = desc;
    this.fee = fee;
  }

  line(): string {
    return `${this.desc} $${(this.fee.cents() / 100).toFixed(2)}`;
  }
}

new Entry("coffee", new Flat(325)).line();     // coffee $3.25
```

Same output, no hierarchy. `Entry` is now one concrete class, the fee rule is
swappable at runtime, and a new kind of fee does not require a new subclass of
anything. This is **composition**, and it is the default worth reaching for
first; inheritance is the special case.

> ⚠️ **Common mistakes:** an abstract class with no concrete members (write an
> interface); calling an abstract method from the base *constructor*, before the
> subclass's fields are assigned; and modelling with inheritance what varies at
> runtime, where composition swaps a collaborator instead.
""",
            warmup=[
                _q("`new Entry(\"x\")` where Entry is abstract gives…",
                   ["an instance", "TS2511", "TS2515", "undefined"], 1,
                   "Abstract classes exist only to be extended."),
                _q("An `abstract` member is…",
                   ["a private method", "a signature with no body that subclasses must implement",
                    "a static field", "optional"], 1,
                   "TS2515 when a concrete subclass omits it."),
                _q("A concrete base method that calls an abstract one is called…",
                   ["a factory", "the template method pattern", "composition", "an override"], 1,
                   "Shared code with a hole in it."),
                _q("An abstract class whose every member is abstract is…",
                   ["ideal", "an interface written the hard way", "faster", "required"], 1,
                   "With no implementation to share, there is nothing to inherit."),
            ],
            exercises=[
                _ex("tscourse-w11-ab-1", "Fill in the hook",
                    "Implement the abstract method so the inherited `line` can work.",
                    'abstract class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  abstract cents(): number;\n\n'
                    '  line(): string {\n'
                    '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                    'class Fixed extends Entry {\n  private amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    super(desc);\n    this.amount = amount;\n  }\n\n'
                    '  cents(): number {\n    return this.amount;\n  }\n}\n'
                    'console.log(new Fixed("coffee", 325).line());\n',
                    'return this.amount;', [("", "coffee $3.25")],
                    hints=["The subclass already stores the value the base needs.",
                           "Write return this.amount;"]),
                _ex("tscourse-w11-ab-2", "Declare the hook",
                    "Declare the member every subclass must supply — a method taking nothing and returning a number, with no body.",
                    'abstract class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  abstract cents(): number;\n\n'
                    '  line(): string {\n'
                    '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                    'class Fixed extends Entry {\n  private amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    super(desc);\n    this.amount = amount;\n  }\n\n'
                    '  cents(): number {\n    return this.amount;\n  }\n}\n'
                    'console.log(new Fixed("coffee", 325).line());\n',
                    'abstract cents(): number;', [("", "coffee $3.25")],
                    hints=["A modifier, the signature, and a semicolon instead of a body.",
                           "Write abstract cents(): number;"],
                    difficulty="Medium"),
                _ex("tscourse-w11-ab-3", "Two subclasses, one shared method",
                    "Compute the hourly total in cents, so both kinds print through the same `line`.",
                    'abstract class Entry {\n  desc: string;\n\n'
                    '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                    '  abstract cents(): number;\n\n'
                    '  line(): string {\n'
                    '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                    'class Fixed extends Entry {\n  private amount: number;\n\n'
                    '  constructor(desc: string, amount: number) {\n'
                    '    super(desc);\n    this.amount = amount;\n  }\n\n'
                    '  cents(): number {\n    return this.amount;\n  }\n}\n'
                    'class Hourly extends Entry {\n  private hours: number;\n  private rate: number;\n\n'
                    '  constructor(desc: string, hours: number, rate: number) {\n'
                    '    super(desc);\n    this.hours = hours;\n    this.rate = rate;\n  }\n\n'
                    '  cents(): number {\n    return this.hours * this.rate;\n  }\n}\n'
                    'const rows: Entry[] = [new Fixed("coffee", 325), new Hourly("tutor", 2, 2500)];\n'
                    'for (const r of rows) {\n  console.log(r.line());\n}\n',
                    'return this.hours * this.rate;',
                    [("", "coffee $3.25\ntutor $50.00")],
                    hints=["The rate is already in cents per hour.",
                           "Neither subclass writes its own `line` — that is the point."],
                    difficulty="Medium"),
                _ex("tscourse-w11-ab-4", "Hold it instead of being it",
                    "Store the collaborator so `line` can ask it for the amount.",
                    'interface Fee {\n  cents(): number;\n}\n'
                    'class Flat implements Fee {\n  private amount: number;\n\n'
                    '  constructor(amount: number) {\n    this.amount = amount;\n  }\n\n'
                    '  cents(): number {\n    return this.amount;\n  }\n}\n'
                    'class Entry {\n  private desc: string;\n  private fee: Fee;\n\n'
                    '  constructor(desc: string, fee: Fee) {\n'
                    '    this.desc = desc;\n    this.fee = fee;\n  }\n\n'
                    '  line(): string {\n'
                    '    return `${this.desc} $${(this.fee.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                    'console.log(new Entry("coffee", new Flat(325)).line());\n',
                    'this.desc = desc;\n    this.fee = fee;',
                    [("", "coffee $3.25")],
                    hints=["Two ordinary field assignments — the second holds another object.",
                           "No inheritance anywhere: `Entry` is concrete and the fee is swappable."],
                    difficulty="Medium"),
                _diagnose("tscourse-w11-ab-d1", "Instantiating the incomplete",
                          "TS2511: Cannot create an instance of an abstract class.",
                          'abstract class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                          '  abstract cents(): number;\n\n'
                          '  line(): string {\n'
                          '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                          'class Fixed extends Entry {\n  private amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    super(desc);\n    this.amount = amount;\n  }\n\n'
                          '  cents(): number {\n    return this.amount;\n  }\n}\n'
                          'const e = new Entry("coffee");\nconsole.log(e.line());\n',
                          'abstract class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                          '  abstract cents(): number;\n\n'
                          '  line(): string {\n'
                          '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                          'class Fixed extends Entry {\n  private amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    super(desc);\n    this.amount = amount;\n  }\n\n'
                          '  cents(): number {\n    return this.amount;\n  }\n}\n'
                          'const e = new Fixed("coffee", 325);\nconsole.log(e.line());\n',
                          [("", "coffee $3.25")],
                          hints=["`Entry` has no `cents` to run, which is exactly why it is abstract.",
                                 "There is already a concrete subclass — build that instead, with an amount of 325."],
                          difficulty="Medium"),
                _diagnose("tscourse-w11-ab-d2", "The hook nobody filled",
                          "TS2515: Non-abstract class 'Fixed' does not implement inherited abstract member cents from class 'Entry'.",
                          'abstract class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                          '  abstract cents(): number;\n\n'
                          '  line(): string {\n'
                          '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                          'class Fixed extends Entry {\n  private amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    super(desc);\n    this.amount = amount;\n  }\n\n'
                          '  total(): number {\n    return this.amount;\n  }\n}\n'
                          'console.log(new Fixed("coffee", 325).line());\n',
                          'abstract class Entry {\n  desc: string;\n\n'
                          '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                          '  abstract cents(): number;\n\n'
                          '  line(): string {\n'
                          '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                          'class Fixed extends Entry {\n  private amount: number;\n\n'
                          '  constructor(desc: string, amount: number) {\n'
                          '    super(desc);\n    this.amount = amount;\n  }\n\n'
                          '  cents(): number {\n    return this.amount;\n  }\n}\n'
                          'console.log(new Fixed("coffee", 325).line());\n',
                          [("", "coffee $3.25")],
                          hints=["The method is there under another name, so the contract is unmet.",
                                 "The base calls `this.cents()` — give it exactly that."],
                          difficulty="Medium"),
                _fix("tscourse-w11-ab-fix1", "Fix the base that ignores its own hook",
                     "`line` hard-codes a zero instead of calling the abstract method, so it prints `coffee $0.00` instead of `coffee $3.25`.",
                     'abstract class Entry {\n  desc: string;\n\n'
                     '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                     '  abstract cents(): number;\n\n'
                     '  line(): string {\n'
                     '    return `${this.desc} $${(0 / 100).toFixed(2)}`;\n  }\n}\n'
                     'class Fixed extends Entry {\n  private amount: number;\n\n'
                     '  constructor(desc: string, amount: number) {\n'
                     '    super(desc);\n    this.amount = amount;\n  }\n\n'
                     '  cents(): number {\n    return this.amount;\n  }\n}\n'
                     'console.log(new Fixed("coffee", 325).line());\n',
                     'abstract class Entry {\n  desc: string;\n\n'
                     '  constructor(desc: string) {\n    this.desc = desc;\n  }\n\n'
                     '  abstract cents(): number;\n\n'
                     '  line(): string {\n'
                     '    return `${this.desc} $${(this.cents() / 100).toFixed(2)}`;\n  }\n}\n'
                     'class Fixed extends Entry {\n  private amount: number;\n\n'
                     '  constructor(desc: string, amount: number) {\n'
                     '    super(desc);\n    this.amount = amount;\n  }\n\n'
                     '  cents(): number {\n    return this.amount;\n  }\n}\n'
                     'console.log(new Fixed("coffee", 325).line());\n',
                     [("", "coffee $3.25")],
                     hints=["The whole point of the abstract member is that the base calls it.",
                            "Replace the literal with this.cents()."]),
            ],
            quiz=[
                _q("Choose an interface over an abstract class when…",
                   ["you need instanceof", "the base has no implementation to share",
                    "you need private state", "there is one subclass"], 1,
                   "No code to inherit means nothing to inherit."),
                _q("Composition means…",
                   ["extending two classes", "holding a collaborator in a field instead of inheriting",
                    "using an abstract class", "copying methods"], 1,
                   "Swappable at runtime, and no hierarchy to maintain."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #11 — the ledger becomes a class",
        """
Budget Buddy has been a set of functions passing plain records around since week
1. This week it gets two classes, and the entries array stops being anybody
else's business.

Input is one row per line, `desc amount tag`:

```
coffee 3.25 food
rent 900 home
lunch 9.50 food
book 12 fun
```

Print exactly:

```
Entries:  4
Total:    $924.75
By tag:   food=$12.75, fun=$12.00, home=$900.00
Largest:  rent $900.00
```

Build these two classes:

```ts
class Expense {
  readonly desc: string;
  readonly cents: number;
  readonly tag: string;
  constructor(desc: string, cents: number, tag: string)
  static fromLine(line: string): Expense    // parses "coffee 3.25 food"
  get dollars(): string                     // "$3.25"
}

class Ledger {
  private entries: Expense[] = [];
  add(e: Expense): void
  get count(): number
  total(): number                           // in CENTS
  byTag(): Record<string, number>           // tag -> cents
  largest(): Expense                        // first row wins a tie
}
```

Rules:

- **Money is integer cents.** `fromLine` converts with
  `Math.round(Number(...) * 100)`, so 3.25 becomes 325 and no float error can
  creep into the total.
- `Ledger.entries` is `private`. Nothing outside the class may touch the array —
  every number in the output comes from a method or a getter.
- `By tag` lists each tag and its total, keys sorted alphabetically, joined with
  `, `.
- `Largest` is the description and dollars of the biggest row; on a tie the
  **first** such row wins.
- `largest()` must not lie about an empty ledger — guard the empty case and throw
  rather than asserting with `!`.
""",
        _ch("tscourse-w11-capstone", "Budget Buddy #11", "Medium",
            "Write the two classes, then feed the parsed rows through the ledger.",
            _FS + 'class Expense {\n'
            '  readonly desc: string;\n  readonly cents: number;\n  readonly tag: string;\n\n'
            '  constructor(desc: string, cents: number, tag: string) {\n'
            '    this.desc = desc;\n    this.cents = cents;\n    this.tag = tag;\n  }\n\n'
            '  static fromLine(line: string): Expense {\n'
            '    const p = line.trim().split(" ");\n'
            '    return new Expense(p[0] ?? "", Math.round(Number(p[1] ?? "0") * 100), p[2] ?? "");\n'
            '  }\n\n'
            '  get dollars(): string {\n'
            '    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
            'class Ledger {\n'
            '  private entries: Expense[] = [];\n\n'
            '  add(e: Expense): void {\n    this.entries.push(e);\n  }\n\n'
            '  get count(): number {\n    return this.entries.length;\n  }\n\n'
            '  total(): number {\n'
            '    return this.entries.reduce((s, e) => s + e.cents, 0);\n  }\n\n'
            '  byTag(): Record<string, number> {\n'
            '    const out: Record<string, number> = {};\n'
            '    for (const e of this.entries) {\n'
            '      out[e.tag] = (out[e.tag] ?? 0) + e.cents;\n    }\n'
            '    return out;\n  }\n\n'
            '  largest(): Expense {\n'
            '    const first = this.entries[0];\n'
            '    if (first === undefined) {\n'
            '      throw new Error("empty ledger");\n    }\n'
            '    let best: Expense = first;\n'
            '    for (const e of this.entries) {\n'
            '      if (e.cents > best.cents) {\n        best = e;\n      }\n    }\n'
            '    return best;\n  }\n}\n'
            'const ledger = new Ledger();\n'
            'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
            '  ledger.add(Expense.fromLine(line));\n}\n'
            'const tags = ledger.byTag();\n'
            'const parts = Object.keys(tags).sort().map((t) => `${t}=$${((tags[t] ?? 0) / 100).toFixed(2)}`);\n'
            'const big = ledger.largest();\n'
            'console.log(`Entries:  ${ledger.count}`);\n'
            'console.log(`Total:    $${(ledger.total() / 100).toFixed(2)}`);\n'
            'console.log(`By tag:   ${parts.join(", ")}`);\n'
            'console.log(`Largest:  ${big.desc} ${big.dollars}`);\n',
            'class Expense {\n'
            '  readonly desc: string;\n  readonly cents: number;\n  readonly tag: string;\n\n'
            '  constructor(desc: string, cents: number, tag: string) {\n'
            '    this.desc = desc;\n    this.cents = cents;\n    this.tag = tag;\n  }\n\n'
            '  static fromLine(line: string): Expense {\n'
            '    const p = line.trim().split(" ");\n'
            '    return new Expense(p[0] ?? "", Math.round(Number(p[1] ?? "0") * 100), p[2] ?? "");\n'
            '  }\n\n'
            '  get dollars(): string {\n'
            '    return `$${(this.cents / 100).toFixed(2)}`;\n  }\n}\n'
            'class Ledger {\n'
            '  private entries: Expense[] = [];\n\n'
            '  add(e: Expense): void {\n    this.entries.push(e);\n  }\n\n'
            '  get count(): number {\n    return this.entries.length;\n  }\n\n'
            '  total(): number {\n'
            '    return this.entries.reduce((s, e) => s + e.cents, 0);\n  }\n\n'
            '  byTag(): Record<string, number> {\n'
            '    const out: Record<string, number> = {};\n'
            '    for (const e of this.entries) {\n'
            '      out[e.tag] = (out[e.tag] ?? 0) + e.cents;\n    }\n'
            '    return out;\n  }\n\n'
            '  largest(): Expense {\n'
            '    const first = this.entries[0];\n'
            '    if (first === undefined) {\n'
            '      throw new Error("empty ledger");\n    }\n'
            '    let best: Expense = first;\n'
            '    for (const e of this.entries) {\n'
            '      if (e.cents > best.cents) {\n        best = e;\n      }\n    }\n'
            '    return best;\n  }\n}',
            [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
              "Entries:  4\nTotal:    $924.75\nBy tag:   food=$12.75, fun=$12.00, home=$900.00\nLargest:  rent $900.00"),
             ("tea 2 drink",
              "Entries:  1\nTotal:    $2.00\nBy tag:   drink=$2.00\nLargest:  tea $2.00"),
             ("a 5 x\nb 5 x",
              "Entries:  2\nTotal:    $10.00\nBy tag:   x=$10.00\nLargest:  a $5.00")],
            hints=["`Expense` holds three readonly fields; the constructor is the only place they are assigned.",
                   "`fromLine` is a static factory: split on a space, and default each part with ?? because indexing may find nothing.",
                   "Math.round(Number(p[1] ?? \"0\") * 100) turns \"3.25\" into the integer 325.",
                   "`dollars` is a getter, so it is read as `e.dollars` with no parentheses.",
                   "`count` is a getter over this.entries.length; `total` is week 8's reduce over e.cents.",
                   "byTag is week 7's grouping: out[e.tag] = (out[e.tag] ?? 0) + e.cents.",
                   "largest reads entries[0] into a const first, throws when it is undefined, then runs the best-so-far loop with a strict > so a tie keeps the first row."]),
        example_io="Entries:  4\nTotal:    $924.75\nBy tag:   food=$12.75, fun=$12.00, home=$900.00\nLargest:  rent $900.00",
        rubric=["Expense's three fields are readonly and assigned only in the constructor",
                "fromLine is a static method returning an Expense, and stores integer cents",
                "dollars is a getter, not a method",
                "Ledger.entries is private, and no code outside the class touches the array",
                "count is a getter; total, byTag and largest are methods",
                "largest guards the empty case by throwing rather than asserting with !",
                "A tie in largest keeps the first row"],
        stretch=_ch("tscourse-w11-capstone-stretch", "Budget Buddy #11 (stretch)", "Medium",
                    "Add an `average()` method to `Ledger` returning the mean in cents (0 for an "
                    "empty ledger), and print `Average:  $231.19` from it. Reuse `total()` and "
                    "`count` rather than folding again.",
                    _FS + 'class Expense {\n'
                    '  readonly cents: number;\n\n'
                    '  constructor(cents: number) {\n    this.cents = cents;\n  }\n\n'
                    '  static fromLine(line: string): Expense {\n'
                    '    const p = line.trim().split(" ");\n'
                    '    return new Expense(Math.round(Number(p[1] ?? "0") * 100));\n  }\n}\n'
                    'class Ledger {\n'
                    '  private entries: Expense[] = [];\n\n'
                    '  add(e: Expense): void {\n    this.entries.push(e);\n  }\n\n'
                    '  get count(): number {\n    return this.entries.length;\n  }\n\n'
                    '  total(): number {\n'
                    '    return this.entries.reduce((s, e) => s + e.cents, 0);\n  }\n\n'
                    '  average(): number {\n'
                    '    return this.count === 0 ? 0 : this.total() / this.count;\n  }\n}\n'
                    'const ledger = new Ledger();\n'
                    'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
                    '  ledger.add(Expense.fromLine(line));\n}\n'
                    'console.log(`Average:  $${(ledger.average() / 100).toFixed(2)}`);\n',
                    '  average(): number {\n'
                    '    return this.count === 0 ? 0 : this.total() / this.count;\n  }',
                    [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
                      "Average:  $231.19"),
                     ("tea 2 drink", "Average:  $2.00")],
                    hints=["Guard the empty ledger first, or you divide by zero.",
                           "`this.count` is a getter, so no parentheses; `this.total()` is a method, so it needs them.",
                           "Leave the division unrounded — the caller's toFixed(2) does the rounding."]),
    ),
))
