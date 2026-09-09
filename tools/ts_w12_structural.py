# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 12 — structural typing, variance & satisfies.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# TWO AUTHORING CONSTRAINTS THIS WEEK, BOTH LOAD-BEARING.
#
# 1. `enum` is NOT erasable syntax. The judge runs TypeScript by stripping
#    types, and an enum emits a runtime object, so Node refuses it outright:
#
#        ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX: TypeScript enum is not supported
#        in strip-only mode
#
#    So every enum exercise in lesson 8 is `judge_mode: "types"` (graded by the
#    compiler, never run), and the one `diagnose` that starts from an enum has
#    a solution that has REPLACED it with a literal union — which is the whole
#    argument of the lesson, made mechanical. Week 11 introduced "erasable
#    syntax" as a named idea for exactly this payoff.
#
# 2. Variance has almost nothing to print. Most of this week is therefore
#    graded by `predict`, `diagnose` and `types` rather than by stdout — with
#    two deliberate exceptions where the type hole is genuinely OBSERVABLE at
#    runtime, and those two carry the lesson:
#      - w12-assignable: a wider object keeps its extra key after assignment.
#      - w12-arrays:     Dog[] -> Animal[] -> push a cat -> dogs is now wrong.
# ---------------------------------------------------------------------------

# --- Week 12 --------------------------------------------------------------
_WEEKS.append(_week(
    12, 3, _M3,
    "Structural Typing, Variance & satisfies",
    "Learn the rule that decides whether one type is assignable to another, meet `satisfies` — which checks a value against a type without widening it — and see why a literal union usually beats an enum.",
    """
Every week so far has relied on a rule nobody has stated. Here it is:

> **TypeScript compares types by their SHAPE, never by their name.**

Two types you declared separately, that know nothing about each other, are
interchangeable if their members line up:

```ts
interface Point { x: number; y: number; }
interface Vec2  { x: number; y: number; }

const v: Vec2 = { x: 1, y: 2 };
const p: Point = v;              // ✅ no cast, no complaint
```

If you have written Java or C#, that is the opposite of what you expect: there,
two classes with identical members are two unrelated types. TypeScript is
**structural**, and it has to be, because it describes JavaScript — where a
value is just a bag of properties and nobody declared anything.

That one rule explains an enormous amount:

* why a class satisfies an interface it never mentioned (week 11, lesson 7);
* why `{ x: 1, y: 2, z: 3 }` is a fine `Point` — but only sometimes;
* why a callback taking one parameter can be passed where two are expected;
* why `Dog[]` is assignable to `Animal[]`, and why that is **unsound**;
* why "a user id" and "an order id" are the same type unless you make them
  differ on purpose.

This is the hardest week of month 3. The material is not long, but it is
counter-intuitive, and almost none of it prints anything — so most of the
exercises ask you to *read*: name the type the compiler inferred, decode the
assignability error it raised, and prove a claim with the type-checker.

Two practical tools come out of it. **`satisfies`** checks a value against a
type without widening it, which is the answer to a problem you have been living
with since week 6. **Branded types** buy you back the nominal typing that
structural typing gives away, in about three lines.

And one recommendation, which the last lesson argues rather than asserts: prefer
a literal union to an `enum`.

⏱️ Budget about **ten hours**, and expect to reread the variance lesson.
""",
    objectives=[
        "State the structural typing rule and say why TypeScript has to work that way",
        "Name the one place structural typing does not apply: classes with private members",
        "Tell assignability from identity, and say why `Equal` is the honest check",
        "Explain why an extra property is accepted through a variable but rejected on a fresh literal",
        "Say what excess property checking is for, and name three ways to sidestep it",
        "Predict whether one function type is assignable to another from its parameters and return",
        "Explain why parameters are checked contravariantly and returns covariantly",
        "Demonstrate the array variance hole at runtime, and say how `readonly` closes it",
        "Say why a method declared with method syntax is checked bivariantly, and what that costs",
        "Choose between an annotation, `as`, and `satisfies`, and justify the choice",
        "Build a branded type and its constructor, and say what it costs at runtime",
        "Write an enum, and give three concrete reasons to reach for a literal union instead",
    ],
    why="Nearly every confusing TypeScript error is an assignability error, and assignability is what this week is about. Reading 'Type X is not assignable to type Y' fluently — knowing whether the problem is a missing property, a fresh literal, or a parameter checked in the direction you did not expect — is the difference between fixing the cause and reaching for `as any`.",
    est_minutes=620,
    glossary=[
        _gloss("structural typing", "Types are compatible when their shapes are compatible, regardless of their names."),
        _gloss("nominal typing", "The other rule, used by Java and C#: compatibility follows the declared name."),
        _gloss("assignable", "X is assignable to Y when a value of type X may be used where Y is expected. One direction only."),
        _gloss("identical (Equal)", "The stricter relation: the SAME type, not merely one that fits. What `Equal<X, Y>` checks."),
        _gloss("width subtyping", "A type with MORE members is assignable to one with fewer."),
        _gloss("fresh literal", "An object literal written directly at the assignment or call. Only these get excess property checking."),
        _gloss("excess property check", "The rule that a fresh literal may not carry properties the target type does not declare (TS2353)."),
        _gloss("weak type", "A type whose members are all optional; assigning something with no overlap at all is rejected."),
        _gloss("index signature", "`[key: string]: number` — declares that any string key is allowed, which also lets extras through."),
        _gloss("variance", "How the compatibility of a compound type follows from the compatibility of its parts."),
        _gloss("covariant", "Varies the same way. Return types are covariant: returning a MORE specific type is fine."),
        _gloss("contravariant", "Varies the opposite way. Parameters are contravariant: accepting a WIDER type is fine."),
        _gloss("bivariant", "Checked both ways, which is unsound. Members written with method syntax are bivariant."),
        _gloss("strictFunctionTypes", "The strict-mode flag that makes standalone function-type parameters contravariant rather than bivariant."),
        _gloss("unsound", "A rule the compiler accepts that can still fail at runtime. Array covariance is the classic example."),
        _gloss("readonly T[]", "An array type with no mutating methods, which is how the array variance hole is closed."),
        _gloss("annotation", "`const x: T = …` — checks the value AND widens it to T."),
        _gloss("as (type assertion)", "`x as T` — overrides the compiler's opinion. It checks almost nothing and can lie."),
        _gloss("satisfies", "`x satisfies T` — checks the value against T while keeping the type that was inferred."),
        _gloss("branded type", "`number & { __brand: \"Cents\" }` — a type made nominal by an intersection nothing else can produce."),
        _gloss("phantom property", "The `__brand` member: it exists only in the type, never at runtime."),
        _gloss("enum", "A named set of constants. NOT erasable syntax: it emits a runtime object."),
        _gloss("string enum", "`enum Tag { Food = \"food\" }` — its members are still not interchangeable with the plain strings."),
        _gloss("reverse mapping", "A numeric enum's runtime object maps names to numbers AND numbers back to names."),
        _gloss("literal union", "`type Tag = \"food\" | \"home\"` — the usual replacement for an enum. Erasable, and plain strings work."),
        _gloss("as const object", "A frozen-in-place object whose values keep their literal types, used when the values are needed at runtime."),
    ],
    cheatsheet="""
```ts
// ---- structural: shape, not name ---------------------------------------
interface Point { x: number; y: number; }
interface Vec2  { x: number; y: number; }
const p: Point = { x: 1, y: 2 } as Vec2;     // interchangeable

// ...except classes with private members, which ARE nominal:
class A { private id = 1; }
class B { private id = 1; }
const a: A = new B();   // TS2322: separate declarations of a private property

// ---- assignable, one direction -----------------------------------------
interface P3 { x: number; y: number; z: number; }
const wide: P3 = { x: 1, y: 2, z: 3 };
const narrow: Point = wide;      // ✅ more members -> fewer
// const back: P3 = narrow;      // ❌ fewer -> more

// ---- excess property checks fire only on FRESH literals -----------------
// const bad: Point = { x: 1, y: 2, z: 3 };   // ❌ TS2353
const tmp = { x: 1, y: 2, z: 3 };
const ok: Point = tmp;                        // ✅ not fresh — and z survives!

// ---- function variance ---------------------------------------------------
type Fmt = (value: string, index: number) => string;
const a1: Fmt = (v: string): string => v;                 // ✅ fewer params
const a2: Fmt = (v: string | number): string => String(v); // ✅ WIDER param
// const a3: (v: string | number) => string = a1;          // ❌ narrower param

// ---- array variance is unsound ------------------------------------------
interface Animal { name: string; }
interface Dog extends Animal { fetch(): string; }
const dogs: Dog[] = [];
const animals: Animal[] = dogs;    // ✅ allowed...
animals.push({ name: "tom" });     // ...and dogs now holds a non-dog
const safe: readonly Animal[] = dogs;   // no push at all — hole closed

// ---- annotation vs as vs satisfies --------------------------------------
const ann: Record<string, number> = { food: 1 };  // widened: ann.food is number|undefined
const asrt = { food: "x" } as unknown as Record<string, number>;  // a lie
const sat = { food: 1 } satisfies Record<string, number>;         // checked, NOT widened
sat.food + 1;      // ✅ number — the key is still known

// ---- branded types -------------------------------------------------------
type Cents = number & { readonly __brand: "Cents" };
const cents = (n: number): Cents => n as Cents;   // the only way in
const show  = (c: Cents): string => `$${(c / 100).toFixed(2)}`;
show(cents(325));      // ✅
// show(325);          // ❌ TS2345 — a plain number is not Cents
// At runtime a Cents IS just a number: the brand is erased.

// ---- enum vs literal union ----------------------------------------------
enum ETag { Food = "food" }        // emits code; not erasable
// const t: ETag = "food";         // ❌ even the string is not the member

type Tag = "food" | "fun" | "home";      // erasable, plain strings work
const Tags = { Food: "food", Home: "home" } as const;   // when you need VALUES
type TagV = (typeof Tags)[keyof typeof Tags];
```
""",
    self_check=[
        "Can you state the structural typing rule in one sentence, and name its one exception?",
        "Can you say why `const p: Point = vec2Value` compiles with no cast?",
        "Can you explain the difference between 'assignable' and 'the same type'?",
        "Can you say why `{ x: 1, y: 2, z: 3 }` is rejected as a Point inline but accepted through a variable?",
        "Can you name three ways to get an extra property past the excess property check?",
        "Can you say which direction parameters are checked in, and which direction returns are?",
        "Can you explain why a callback that ignores its second parameter is still acceptable?",
        "Can you write the four lines that make array covariance blow up at runtime?",
        "Can you say what `readonly T[]` fixes, and what it costs?",
        "Can you say what `satisfies` does that an annotation does not, with a concrete example?",
        "Can you say what `as` checks, and why it is the last resort?",
        "Can you write a branded type, its constructor, and say what it weighs at runtime?",
        "Can you give three reasons to prefer a literal union over an enum?",
        "Can you say when an `as const` object is the right replacement for an enum instead?",
    ],
    review=[
        _q("TypeScript decides two types are compatible by comparing…",
           ["their names", "their shapes", "their files", "their declaration order"], 1,
           "Structural typing, top to bottom."),
        _q("Two classes each declaring `private id: number` are…",
           ["interchangeable", "NOT assignable to each other", "the same type", "both any"], 1,
           "Private members are the one nominal corner of the language."),
        _q("`const narrow: Point = wideValue` where wide has an extra member is…",
           ["an error", "fine — more members satisfy fewer", "a cast", "unsound"], 1,
           "Width subtyping."),
        _q("Assignability runs…",
           ["both ways", "one way only", "only for objects", "only under strict"], 1,
           "Fewer members are not assignable to more."),
        _q("`Equal<X, Y>` differs from `X extends Y` because…",
           ["it is faster", "it checks identity rather than mere assignability",
            "it works on unions only", "it ignores any"], 1,
           "Assignability would accept anything wide enough."),
        _q("The excess property check fires on…",
           ["every assignment", "a FRESH object literal at the assignment or call",
            "variables only", "function returns only"], 1,
           "Which is why routing through a variable sidesteps it."),
        _q("Excess property checking exists to…",
           ["enforce soundness", "catch typos and dead configuration options",
            "speed up compilation", "support classes"], 1,
           "It is a usability rule, not a soundness one."),
        _q("A function type's PARAMETERS are checked…",
           ["covariantly", "contravariantly — a wider parameter is acceptable",
            "bivariantly always", "not at all"], 1,
           "Under strictFunctionTypes."),
        _q("A function type's RETURN is checked…",
           ["contravariantly", "covariantly — a more specific return is acceptable",
            "bivariantly", "by name"], 1,
           "Returning more than promised is safe."),
        _q("`const f: (v: string, i: number) => string = (v: string) => v` is…",
           ["an error", "fine — ignoring trailing parameters is allowed",
            "unsound", "a cast"], 1,
           "Which is why array callbacks can take one argument."),
        _q("`Dog[]` is assignable to `Animal[]`, and that is…",
           ["sound", "unsound — you can then push a non-dog into it",
            "impossible", "only allowed with a cast"], 1,
           "A deliberate, documented hole."),
        _q("The fix for the array variance hole is…",
           ["a cast", "`readonly Animal[]`, which has no push", "an interface", "a generic"], 1,
           "Take away the mutation and covariance is safe."),
        _q("A member written with METHOD syntax is checked…",
           ["contravariantly", "bivariantly, which is unsound",
            "covariantly", "not at all"], 1,
           "Property syntax with a function type is the strict version."),
        _q("`const r: Record<string, number> = { food: 1 }` then `r.food` is typed…",
           ["number", "number | undefined under noUncheckedIndexedAccess",
            "1", "never"], 1,
           "The annotation widened the value and lost the key."),
        _q("`const r = { food: 1 } satisfies Record<string, number>` then `r.food` is typed…",
           ["number | undefined", "number — the inferred type was kept",
            "unknown", "any"], 1,
           "Checked against the type without being widened to it."),
        _q("`x as T` checks…",
           ["everything an annotation does", "almost nothing — it overrides the compiler",
            "more than satisfies", "the runtime value"], 1,
           "Which is why it is the last resort."),
        _q("A branded type works because…",
           ["the runtime tags the value", "the intersection adds a member nothing else produces",
            "it uses a class", "it is nominal by declaration"], 1,
           "And the constructor function is the only thing that asserts it."),
        _q("At runtime, a `Cents` value is…",
           ["an object with a __brand key", "just a number — the brand is erased",
            "a string", "a class instance"], 1,
           "Branding costs nothing when the program runs."),
        _q("An `enum` cannot run in this course because…",
           ["it is deprecated", "it emits a runtime object, so it is not erasable syntax",
            "the judge forbids it", "it needs a decorator"], 1,
           "The same reason as week 11's parameter properties."),
        _q("`enum Tag { Food = \"food\" }` then `const t: Tag = \"food\"` is…",
           ["fine", "TS2322 — the member is not the plain string", "a warning", "unchecked"], 1,
           "Even a string enum is nominal about its members."),
        _q("Reach for an `as const` object instead of a literal union when…",
           ["never", "you need the VALUES at runtime — to iterate or look up",
            "the union is long", "you need speed"], 1,
           "A bare union has no runtime representation at all."),
    ],
    milestone="Budget Buddy's amounts can no longer be confused with any other number in the program: a `Cents` is its own type, built one way and checked everywhere. Its category table is checked by `satisfies`, so the compiler still knows every key by name. Month 3, and the type system proper, is done.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w12-structural", "Shapes, not names",
            "The rule every earlier week has been quietly relying on.",
            """
Two interfaces, declared separately, that have never heard of each other:

```ts
interface Point { x: number; y: number; }
interface Vec2  { x: number; y: number; }

const v: Vec2 = { x: 1, y: 2 };
const p: Point = v;             // ✅ accepted
```

No cast, no `implements`, no complaint. TypeScript asks one question — *does the
value have what `Point` requires?* — and the answer is yes.

## Why it has to be this way

TypeScript describes JavaScript that already exists. A value that arrives from
`JSON.parse`, from a library, or from an object literal three files away was
never declared as anything. If compatibility followed declared names, none of
that code could be typed at all without rewriting it.

So the rule is: **a value is a T if it has what T requires.** It does not matter
where it came from or what it was called.

## Which is why week 11's `implements` was optional

```ts
interface Priced { amount: number; label(): string; }

class Refund {                        // no implements clause
  amount: number;
  constructor(amount: number) { this.amount = -amount; }
  label(): string { return "refund"; }
}

function describe(p: Priced): string { return `${p.label()} ${p.amount}`; }

describe(new Refund(4));              // ✅ it fits, so it is accepted
```

`implements` moved the error message; it never controlled acceptance.

## Only what is REQUIRED has to match

Extra members are not a problem — a `Point3D` is a perfectly good `Point`:

```ts
interface Point3D { x: number; y: number; z: number; }
const q: Point = { x: 1, y: 2, z: 3 } as Point3D;    // ✅
```

(Write that object literal directly as a `Point` and you *will* get an error —
that is a separate rule, and it has lesson 3 to itself.)

## The one exception: private members

There is exactly one place TypeScript behaves nominally, and it is worth
knowing because the error message is baffling otherwise:

```ts
class Cents { private value: number = 0; }
class Grams { private value: number = 0; }

const c: Cents = new Grams();
// TS2322: Type 'Grams' is not assignable to type 'Cents'.
//         Types have separate declarations of a private property 'value'.
```

Identical shapes, rejected. A `private` (or `protected`) member is tied to the
declaration it came from, so only the *same* declaration is compatible. This is
deliberate: a private field means "my invariant", and two classes' invariants
are not interchangeable just because their fields happen to line up.

Note what this makes possible — a class with a private member is effectively
nominal. Lesson 7 gets the same effect without a class, and without a runtime
cost.

> ⚠️ **Common mistakes:** expecting `implements` to be what makes a class
> acceptable; assuming two identically-shaped classes are interchangeable (they
> are, unless either has a private member); and reading "structural" as
> "anything goes" — every *required* member still has to be there, with a
> compatible type.
""",
            warmup=[
                _q("TypeScript compares two types by…",
                   ["their declared names", "their shapes", "their files", "declaration order"], 1,
                   "Structural typing."),
                _q("A class satisfies an interface it never mentioned…",
                   ["never", "whenever its shape fits", "only with a cast", "only if final"], 1,
                   "Which is why `implements` is optional."),
                _q("A value with EXTRA members, held in a variable, is…",
                   ["rejected", "accepted where fewer are required", "cast", "an error"], 1,
                   "Only required members are checked."),
                _q("Two classes with identical shapes but each a `private id` are…",
                   ["interchangeable", "not assignable to each other", "the same", "unknown"], 1,
                   "Private members are matched by declaration, not by shape."),
            ],
            exercises=[
                _ex("tscourse-w12-st-1", "Two names, one shape",
                    "Assign the Vec2 value where a Point is expected — no cast needed.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'interface Vec2 {\n  x: number;\n  y: number;\n}\n'
                    'const v: Vec2 = { x: 1, y: 2 };\n'
                    'const p: Point = v;\n'
                    'console.log(p.x + p.y);\n',
                    'const p: Point = v;', [("", "3")],
                    hints=["The two interfaces require exactly the same members.",
                           "Write const p: Point = v;"]),
                _ex("tscourse-w12-st-2", "A function does not care where it came from",
                    "Write the body so it uses only the members the parameter type declares.",
                    'interface Named {\n  name: string;\n}\n'
                    'interface User {\n  name: string;\n  age: number;\n}\n'
                    'function greet(n: Named): string {\n'
                    '  return `hello ${n.name}`;\n}\n'
                    'const u: User = { name: "ada", age: 36 };\n'
                    'console.log(greet(u));\n',
                    'return `hello ${n.name}`;', [("", "hello ada")],
                    hints=["The parameter is `Named`, so only `name` is available on it.",
                           "The User has more than that, which is exactly why it is accepted."]),
                _ex("tscourse-w12-st-3", "A class with no implements clause",
                    "Pass the class instance to the function typed by the interface.",
                    'interface Priced {\n  amount: number;\n  label(): string;\n}\n'
                    'class Refund {\n  amount: number;\n\n'
                    '  constructor(amount: number) {\n    this.amount = -amount;\n  }\n\n'
                    '  label(): string {\n    return "refund";\n  }\n}\n'
                    'function describe(p: Priced): string {\n'
                    '  return `${p.label()} ${p.amount}`;\n}\n'
                    'console.log(describe(new Refund(4)));\n',
                    'describe(new Refund(4))', [("", "refund -4")],
                    hints=["The class never says `implements`, and it does not have to.",
                           "Write describe(new Refund(4))."],
                    difficulty="Medium"),
                _predict("tscourse-w12-st-p1", "What the literal was inferred as",
                         'interface Point {\n  x: number;\n  y: number;\n}\n'
                         'const v = { x: 1, y: 2, z: 3 };\n',
                         "v", "{ x: number; y: number; z: number }",
                         why="Nobody annotated it, so the compiler described exactly what is "
                             "there — not the Point above.",
                         hints=["An unannotated object literal is inferred member by member.",
                                "The values are numbers, and they widen from their literal types.",
                                "Write { x: number; y: number; z: number }."],
                         difficulty="Medium"),
                _diagnose("tscourse-w12-st-d1", "The member that is not there",
                          "TS2741: Property 'y' is missing in type '{ x: number; }' but required in type 'Point'.",
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'const p: Point = { x: 1 };\n'
                          'console.log(p.x + p.y);\n',
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'const p: Point = { x: 1, y: 2 };\n'
                          'console.log(p.x + p.y);\n',
                          [("", "3")],
                          hints=["Structural typing is not permissive about REQUIRED members.",
                                 "Give the literal a `y` of 2."],
                          difficulty="Easy"),
                _diagnose("tscourse-w12-st-d2", "The identical types that are not",
                          "TS2322: Type 'Grams' is not assignable to type 'Cents'. Types have separate declarations of a private property 'value'.",
                          'class Cents {\n  private value: number;\n\n'
                          '  constructor(value: number) {\n    this.value = value;\n  }\n\n'
                          '  show(): string {\n    return `${this.value}c`;\n  }\n}\n'
                          'class Grams {\n  private value: number;\n\n'
                          '  constructor(value: number) {\n    this.value = value;\n  }\n\n'
                          '  show(): string {\n    return `${this.value}g`;\n  }\n}\n'
                          'const c: Cents = new Grams(5);\nconsole.log(c.show());\n',
                          'class Cents {\n  private value: number;\n\n'
                          '  constructor(value: number) {\n    this.value = value;\n  }\n\n'
                          '  show(): string {\n    return `${this.value}c`;\n  }\n}\n'
                          'class Grams {\n  private value: number;\n\n'
                          '  constructor(value: number) {\n    this.value = value;\n  }\n\n'
                          '  show(): string {\n    return `${this.value}g`;\n  }\n}\n'
                          'const c: Cents = new Cents(5);\nconsole.log(c.show());\n',
                          [("", "5c")],
                          hints=["The two shapes are identical, and that is not enough here.",
                                 "A private member is matched by the declaration it came from — the one nominal corner of the language.",
                                 "Build the class the annotation actually asks for."],
                          difficulty="Medium"),
                _fix("tscourse-w12-st-fix1", "Fix the function that asked for too much",
                     "`greet` only needs a name, but it is typed to demand the whole User, so it prints the wrong greeting for the Named value it was given. It should print `hello rex`. Widen the parameter to the smallest type the body uses.",
                     'interface Named {\n  name: string;\n}\n'
                     'interface User {\n  name: string;\n  age: number;\n}\n'
                     'function greet(u: User): string {\n'
                     '  return `hello ${u.name} (${u.age})`;\n}\n'
                     'const pet: User = { name: "rex", age: 3 };\n'
                     'console.log(greet(pet));\n',
                     'interface Named {\n  name: string;\n}\n'
                     'interface User {\n  name: string;\n  age: number;\n}\n'
                     'function greet(n: Named): string {\n'
                     '  return `hello ${n.name}`;\n}\n'
                     'const pet: User = { name: "rex", age: 3 };\n'
                     'console.log(greet(pet));\n',
                     [("", "hello rex")],
                     hints=["The expected output has no age in it.",
                            "Annotate the parameter with the narrowest interface the body actually reads.",
                            "The User still goes in — structural typing accepts it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Structural typing is necessary because…",
                   ["it is faster", "TypeScript describes JavaScript values nobody declared",
                    "of generics", "the spec says so"], 1,
                   "Most values in a real program were never given a name."),
                _q("\"Structural\" does NOT mean…",
                   ["shapes are compared", "required members can be missing",
                    "names are ignored", "extras are allowed"], 1,
                   "Every required member still has to be there."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w12-assignable", "Assignable, not identical",
            "One direction, and why `Equal` is the stricter question.",
            """
"Compatible" is not a symmetric idea. **X is assignable to Y** when a value of
type X may be used where a Y is expected — and that says nothing about the other
direction.

```ts
interface Point  { x: number; y: number; }
interface Point3 { x: number; y: number; z: number; }

const wide: Point3 = { x: 1, y: 2, z: 3 };
const narrow: Point = wide;        // ✅ more members satisfy fewer

const back: Point3 = narrow;
// ❌ TS2741: Property 'z' is missing in type 'Point'
//            but required in type 'Point3'.
```

More is safe; less is not. That is **width subtyping**, and it is the everyday
case of the rule from lesson 1.

## The extra property is still there at runtime

This is worth seeing rather than being told, because it explains a whole class
of confusing behaviour:

```ts
const v = { x: 1, y: 2, z: 3 };
const p: Point = v;
console.log(Object.keys(p).join(","));      // x,y,z
```

The *type* says two members. The *value* has three, and always did. Annotating
something does not reshape it — it only changes what the compiler will let you
do with it. That is why `JSON.stringify(p)` will happily include the `z` you
thought you had typed away, and why week 15's validation lesson exists.

## Assignable is not the same as identical

Two types can be mutually assignable and still not be the same type, and a lot
of type-level work depends on telling those apart:

```ts
type A = { x: number };
type B = { x: number };
// A and B are assignable both ways AND identical.

type C = any;
// `any` is assignable to and from everything — but it is not the same as
// anything.
```

Week 10's `Equal<X, Y>` is the honest check, which is exactly why the course
uses it in every type-level assertion instead of `extends`:

```ts
type Loose<X, Y> = X extends Y ? true : false;

type L1 = Loose<any, string>;      // boolean — not true, not false
type L2 = Loose<never, string>;    // never   — not `true` either!
```

Neither answers the question you asked. `any` is assignable in both directions,
so the conditional cannot pick a branch and you get both. And `never` does not
give `true` — a bare type parameter on the left *distributes* over a union, and
`never` is the empty union, so there is nothing to distribute over and the whole
thing collapses to `never`. (Write it `[X] extends [Y]` to switch distribution
off, and then it is `true`.)

`Equal<X, Y>` says a plain `false` for both, which is the answer you wanted. You
do not need to be able to derive it — you need to know it is the honest one.

## Optional and readonly do not change assignability the way you expect

```ts
interface Loose { x?: number; }
interface Tight { x: number; }

const t: Tight = { x: 1 };
const l: Loose = t;         // ✅ required satisfies optional
// const t2: Tight = l;     // ❌ optional does not satisfy required
```

And `readonly` is ignored when checking object assignability — it stops *you*
writing, but it does not make two object types incompatible. (Arrays are
different; that is lesson 5.)

> ⚠️ **Common mistakes:** reading an assignability error backwards (the message
> always names the source type first); believing an annotation removes the extra
> properties from the value; and using `extends` where you meant `Equal`.
""",
            warmup=[
                _q("`const narrow: Point = wideValue` where wide has an extra member is…",
                   ["an error", "allowed", "a cast", "unsound"], 1,
                   "More members satisfy fewer."),
                _q("The reverse — assigning the narrow value where the wide type is expected — is…",
                   ["allowed", "TS2741, a missing property", "a warning", "the same"], 1,
                   "Assignability runs one way."),
                _q("After `const p: Point = v` where v had an extra `z`, `Object.keys(p)` shows…",
                   ["x,y", "x,y,z", "nothing", "an error"], 1,
                   "The annotation changed the type, not the value."),
                _q("`X extends Y ? true : false` differs from `Equal<X, Y>` because…",
                   ["it is slower", "it accepts anything merely assignable",
                    "it only works on unions", "it ignores optional members"], 1,
                   "Which is why the course asserts with Equal."),
            ],
            exercises=[
                _ex("tscourse-w12-as-1", "The property that is still there",
                    "Print the value's real runtime keys, comma-separated, and note that the annotation did not remove one.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const v = { x: 1, y: 2, z: 3 };\n'
                    'const p: Point = v;\n'
                    'console.log(Object.keys(p).join(","));\n',
                    'console.log(Object.keys(p).join(","));', [("", "x,y,z")],
                    hints=["Week 7's Object.keys, joined with a comma.",
                           "The type says two members. Ask the value how many it has."],
                    difficulty="Medium"),
                _ex("tscourse-w12-as-2", "More satisfies fewer",
                    "Assign the three-member value where the two-member type is expected.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'interface Point3 {\n  x: number;\n  y: number;\n  z: number;\n}\n'
                    'const wide: Point3 = { x: 1, y: 2, z: 3 };\n'
                    'const narrow: Point = wide;\n'
                    'console.log(narrow.x + narrow.y);\n',
                    'const narrow: Point = wide;', [("", "3")],
                    hints=["Everything Point requires is present on wide.",
                           "Write const narrow: Point = wide;"]),
                _ex("tscourse-w12-as-3", "Required satisfies optional",
                    "Assign the value with a required member where the optional one is expected.",
                    'interface Loose {\n  x?: number;\n}\n'
                    'interface Tight {\n  x: number;\n}\n'
                    'const t: Tight = { x: 1 };\n'
                    'const l: Loose = t;\n'
                    'console.log(l.x ?? 0);\n',
                    'const l: Loose = t;', [("", "1")],
                    hints=["A value that definitely has `x` certainly has it optionally.",
                           "Write const l: Loose = t;"]),
                _predict("tscourse-w12-as-p1", "Reading an optional member",
                         'interface Loose {\n  x?: number;\n}\n'
                         'const l: Loose = { x: 1 };\n'
                         'const got = l.x;\n',
                         "got", "number | undefined",
                         why="The value plainly has an `x`, but the TYPE is what the read goes through.",
                         hints=["An optional member might not be there, as far as the type is concerned.",
                                "Write number | undefined."]),
                _types("tscourse-w12-as-t1", "Prove the direction",
                       "Declare `Point3` with the three members that make the assertions below hold: "
                       "a Point3 must be usable as a Point, and a Point must NOT be usable as a Point3.",
                       'interface Point {\n  x: number;\n  y: number;\n}\n'
                       'interface Point3 {\n  x: number;\n  y: number;\n  z: number;\n}\n',
                       'x: number;\n  y: number;\n  z: number;',
                       """
const wide: Point3 = { x: 1, y: 2, z: 3 };
const narrow: Point = wide;
type _1 = Expect<Equal<typeof narrow, Point>>;

// The other direction must fail: a Point has no z to offer.
// @ts-expect-error
const back: Point3 = narrow;
""",
                       hints=["Point3 needs everything Point has, plus one more.",
                              "All three are numbers.",
                              "Write x: number; y: number; z: number;"],
                       difficulty="Medium"),
                _diagnose("tscourse-w12-as-d1", "The direction that does not work",
                          "TS2741: Property 'z' is missing in type 'Point' but required in type 'Point3'.",
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'interface Point3 {\n  x: number;\n  y: number;\n  z: number;\n}\n'
                          'const narrow: Point = { x: 1, y: 2 };\n'
                          'const wide: Point3 = narrow;\n'
                          'console.log(wide.x + wide.y + wide.z);\n',
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'interface Point3 {\n  x: number;\n  y: number;\n  z: number;\n}\n'
                          'const wide: Point3 = { x: 1, y: 2, z: 3 };\n'
                          'const narrow: Point = wide;\n'
                          'console.log(wide.x + wide.y + wide.z);\n',
                          [("", "6")],
                          hints=["A Point genuinely has no `z`, so no rule could make this safe.",
                                 "Build the value at the WIDER type, then narrow it — that direction is the legal one.",
                                 "The program still has to print 6."],
                          difficulty="Medium"),
                _fix("tscourse-w12-as-fix1", "Fix the annotation that hid a member",
                     "`total` is annotated with the narrower type, so the `tax` the value really carries is unreachable and this prints `30` instead of `33`.",
                     'interface Sub {\n  net: number;\n}\n'
                     'interface Full {\n  net: number;\n  tax: number;\n}\n'
                     'const row: Full = { net: 30, tax: 3 };\n'
                     'const total: Sub = row;\n'
                     'console.log(total.net);\n',
                     'interface Sub {\n  net: number;\n}\n'
                     'interface Full {\n  net: number;\n  tax: number;\n}\n'
                     'const row: Full = { net: 30, tax: 3 };\n'
                     'const total: Full = row;\n'
                     'console.log(total.net + total.tax);\n',
                     [("", "33")],
                     hints=["The tax was never lost from the VALUE — only from the type of the binding.",
                            "Annotate with the type that still has both members, then add them."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("An assignability error message names…",
                   ["the target first", "the source type first, then the target", "only the property",
                    "the file"], 1,
                   "'Type X is not assignable to type Y' — X is what you had."),
                _q("`readonly` on an object member affects assignability…",
                   ["strongly", "not at all — it only stops you writing",
                    "only under strict", "only for arrays"], 1,
                   "Arrays are the case where it does matter — lesson 5."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w12-excess", "Excess property checks & fresh literals",
            "The rule that contradicts lesson 2 — and why it is worth it.",
            """
Lesson 2 said an extra property is fine. Now try it inline:

```ts
interface Point { x: number; y: number; }

const p: Point = { x: 1, y: 2, z: 3 };
// ❌ TS2353: Object literal may only specify known properties,
//            and 'z' does not exist in type 'Point'.
```

Both are true. The difference is **freshness**.

## The rule

An object literal written *directly* at the assignment or at the call is
**fresh**. Only fresh literals get excess property checking. Put the same object
in a variable first and the check does not apply:

```ts
const tmp = { x: 1, y: 2, z: 3 };
const p: Point = tmp;                   // ✅ no complaint
```

Freshness is lost as soon as the literal is assigned to anything.

The same rule holds at a call site:

```ts
function show(p: Point): string { return `${p.x},${p.y}`; }

show({ x: 1, y: 2, z: 3 });    // ❌ TS2353 — fresh
show(tmp);                     // ✅ not fresh
```

## Why have a rule that is not sound?

Because it catches the mistake that actually happens. Excess property checking
is not about safety — an extra property can never break anything. It is about
**typos and dead options**:

```ts
interface Options { url: string; retries?: number; }

request({ url: "/x", retires: 3 });
// ❌ TS2561: Object literal may only specify known properties, but 'retires'
//            does not exist in type 'Options'. Did you mean to write 'retries'?
```

Without the rule, that call compiles, `retries` is `undefined`, and the option
is silently ignored. The check exists precisely because you *meant* the literal
to be complete.

Note the code: a plain extra property is **TS2353**, but when the name is close
to a real one TypeScript upgrades to **TS2561** and names the member you
probably meant. Two codes, one rule.

Note how narrow the protection is: route the same typo through a variable and
nothing is reported at all. That failure mode is real, and it is the fix
exercise below.

## The three escape hatches

When the extra property is deliberate:

```ts
// 1. a variable (freshness is lost)
const opts = { url: "/x", trace: true };
request(opts);

// 2. an index signature (extras are declared to be allowed)
interface Options { url: string; [key: string]: unknown; }

// 3. an assertion (last resort — it checks nothing else either)
request({ url: "/x", trace: true } as Options);
```

Prefer 2 when extras are genuinely part of the design, and 1 when they are
incidental. Reach for 3 only when neither fits.

## Weak types

One related rule. If a type's members are **all optional**, an object with no
overlapping members at all is still rejected:

```ts
interface Config { retries?: number; timeout?: number; }
const c: Config = { nope: 1 };
// ❌ Type '{ nope: number; }' has no properties in common with type 'Config'.
```

Without this, an all-optional type would accept literally anything, which makes
it useless as a check.

> ⚠️ **Common mistakes:** concluding the extra property was removed (it was not —
> lesson 2 proved it); adding an index signature just to silence the error, which
> switches the typo protection off for every key; and assuming the check protects
> you when the object came from a variable or from `JSON.parse`.
""",
            warmup=[
                _q("Excess property checking applies to…",
                   ["every assignment", "a fresh object literal at the assignment or call",
                    "variables", "function returns"], 1,
                   "Freshness is the whole rule."),
                _q("`const tmp = {x:1,y:2,z:3}; const p: Point = tmp;` is…",
                   ["TS2353", "accepted — tmp is not fresh", "a cast", "unsound"], 1,
                   "Assigning to the variable lost the freshness."),
                _q("The check exists to catch…",
                   ["unsound code", "typos and options that would be silently ignored",
                    "missing members", "slow code"], 1,
                   "An extra property is harmless; a misspelled one is not."),
                _q("A type whose members are ALL optional rejects an object with…",
                   ["any extra", "no members in common with it at all", "a number", "nothing"], 1,
                   "The weak type rule."),
            ],
            exercises=[
                _ex("tscourse-w12-xs-1", "Lose the freshness on purpose",
                    "Bind the literal to a variable first, so the extra property is allowed through.",
                    'interface Point {\n  x: number;\n  y: number;\n}\n'
                    'const tmp = { x: 1, y: 2, z: 3 };\n'
                    'const p: Point = tmp;\n'
                    'console.log(`${p.x},${p.y}`);\n',
                    'const tmp = { x: 1, y: 2, z: 3 };', [("", "1,2")],
                    hints=["A fresh literal would be rejected here; a variable is not fresh.",
                           "Write const tmp = { x: 1, y: 2, z: 3 };"],
                    difficulty="Medium"),
                _ex("tscourse-w12-xs-2", "Declare that extras are welcome",
                    "Add an index signature so any extra numeric option is allowed.",
                    'interface Options {\n  retries: number;\n  [key: string]: number;\n}\n'
                    'const o: Options = { retries: 3, timeout: 50 };\n'
                    'console.log(`${o.retries} ${Object.keys(o).sort().join(",")}`);\n',
                    '[key: string]: number;', [("", "3 retries,timeout")],
                    hints=["A key of any string name, holding a number.",
                           "Write [key: string]: number;"],
                    difficulty="Medium"),
                _ex("tscourse-w12-xs-3", "The overlap a weak type demands",
                    "Give the config one member the type actually declares.",
                    'interface Config {\n  retries?: number;\n  timeout?: number;\n}\n'
                    'const c: Config = { retries: 3 };\n'
                    'console.log(`${c.retries ?? 0}/${c.timeout ?? 0}`);\n',
                    'const c: Config = { retries: 3 };', [("", "3/0")],
                    hints=["Every member is optional, so an object with nothing in common is refused.",
                           "Set retries to 3."]),
                _diagnose("tscourse-w12-xs-d1", "The property that was not asked for",
                          "TS2353: Object literal may only specify known properties, and 'z' does not exist in type 'Point'.",
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'const p: Point = { x: 1, y: 2, z: 3 };\n'
                          'console.log(`${p.x},${p.y}`);\n',
                          'interface Point {\n  x: number;\n  y: number;\n}\n'
                          'const p: Point = { x: 1, y: 2 };\n'
                          'console.log(`${p.x},${p.y}`);\n',
                          [("", "1,2")],
                          hints=["The literal is written straight at the annotation, so it is fresh.",
                                 "Nothing reads `z` — it was never wanted. Drop it."],
                          difficulty="Easy"),
                _diagnose("tscourse-w12-xs-d2", "The misspelled option",
                          "TS2561: Object literal may only specify known properties, but 'retires' does not exist in type 'Options'. Did you mean to write 'retries'?",
                          'interface Options {\n  url: string;\n  retries?: number;\n}\n'
                          'function request(o: Options): string {\n'
                          '  return `${o.url} x${o.retries ?? 0}`;\n}\n'
                          'console.log(request({ url: "/x", retires: 3 }));\n',
                          'interface Options {\n  url: string;\n  retries?: number;\n}\n'
                          'function request(o: Options): string {\n'
                          '  return `${o.url} x${o.retries ?? 0}`;\n}\n'
                          'console.log(request({ url: "/x", retries: 3 }));\n',
                          [("", "/x x3")],
                          hints=["This is the mistake the whole rule exists to catch.",
                                 "Look very closely at the spelling of the key.",
                                 "The expected output shows the option should take effect: x3, not x0."],
                          difficulty="Medium"),
                _fix("tscourse-w12-xs-fix1", "Fix the typo the check could not see",
                     "The same misspelling as the exercise above, but the object goes through a variable — so it is not fresh, nothing is reported, and the option is silently ignored. It prints `/x x0` and should print `/x x3`.",
                     'interface Options {\n  url: string;\n  retries?: number;\n}\n'
                     'function request(o: Options): string {\n'
                     '  return `${o.url} x${o.retries ?? 0}`;\n}\n'
                     'const opts = { url: "/x", retires: 3 };\n'
                     'console.log(request(opts));\n',
                     'interface Options {\n  url: string;\n  retries?: number;\n}\n'
                     'function request(o: Options): string {\n'
                     '  return `${o.url} x${o.retries ?? 0}`;\n}\n'
                     'const opts = { url: "/x", retries: 3 };\n'
                     'console.log(request(opts));\n',
                     [("", "/x x3")],
                     hints=["Excess property checking never ran here — `opts` is a variable, not a fresh literal.",
                            "So the compiler had nothing to say, and `retries` stayed undefined.",
                            "Fix the spelling. (Annotating `opts` as `Options` would have caught it too.)"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Adding an index signature to silence one error…",
                   ["is the best fix", "switches typo protection off for EVERY key",
                    "is required", "changes runtime"], 1,
                   "Use it when extras are genuinely part of the design."),
                _q("Data from JSON.parse gets excess property checking…",
                   ["always", "never — it is not a fresh literal", "under strict", "with a cast"], 1,
                   "Which is why week 15 validates instead."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w12-fnvariance", "Parameters and returns",
            "Why the two halves of a function type are checked in opposite directions.",
            """
When is one function type assignable to another? Take a target type:

```ts
type Formatter = (value: string, index: number) => string;
```

## Fewer parameters is fine

```ts
const upper: Formatter = (v: string): string => v.toUpperCase();   // ✅
```

The caller will pass two arguments; this function ignores the second. Nothing
can go wrong, and this is why you can write `xs.map((x) => x * 2)` without
declaring the index and array parameters that `map` actually passes.

## A WIDER parameter is fine. A narrower one is not.

```ts
const wide: Formatter = (v: string | number): string => String(v);  // ✅
```

`Formatter` promises to call it with a `string`. A function that accepts
`string | number` handles every string, so it is safe.

Now the other direction:

```ts
type Handler = (v: string | number) => string;
const onlyStrings = (v: string): string => v.toUpperCase();

const h: Handler = onlyStrings;
// ❌ TS2322: Types of parameters 'v' and 'v' are incompatible.
//            Type 'string | number' is not assignable to type 'string'.
```

`Handler` may be called with a number. `onlyStrings` would then call
`.toUpperCase()` on it and crash. Rejecting it is the whole point.

**Parameters are contravariant**: the assignable function may accept *more*
than promised, never less. That flip is the thing people find strange, and it
follows from one question — *who calls it?* The caller decides the argument, so
the function must be ready for everything the caller might send.

## Returns go the normal way

```ts
type Make = () => { a: number; b: number };

const rich = (): { a: number; b: number; c: number } => ({ a: 1, b: 2, c: 3 });
const m: Make = rich;      // ✅ returning MORE than promised is fine

const thin = (): { a: number } => ({ a: 1 });
// const m2: Make = thin;
// ❌ TS2322: Property 'b' is missing in type '{ a: number; }'
```

**Returns are covariant**: give at least what you promised, and extra is fine.
Here the *function* decides the value, so it must not under-deliver.

Two rules, one idea: **be liberal in what you accept, conservative in what you
return.**

## The exception: method syntax is bivariant

Write a member with method syntax and TypeScript checks it in **both**
directions, which is unsound and it knows it:

```ts
interface Box {
  set(v: string | number): void;      // method syntax
}

const b: Box = {
  set(v: string): void {              // narrower parameter — accepted!
    console.log(v.toUpperCase());
  },
};

b.set(5);      // TypeError: v.toUpperCase is not a function
```

That compiles and crashes. `strictFunctionTypes` — which this course runs under
— makes function types contravariant, but it **deliberately exempts method
syntax**, because `Array<T>` and most of the standard library would stop
type-checking otherwise.

**The fix, when you want strictness:** declare the member as a property holding
a function type.

```ts
interface Box {
  set: (v: string | number) => void;   // property syntax — checked strictly
}
```

Same call syntax, stricter check. Worth knowing the difference exists; you will
not always get to choose.

> ⚠️ **Common mistakes:** thinking a callback must declare every parameter;
> expecting a narrower parameter to be accepted; and assuming
> `strictFunctionTypes` protects methods — it does not.
""",
            warmup=[
                _q("`const f: (a: string, b: number) => string = (a: string) => a` is…",
                   ["an error", "fine — extra parameters may be ignored", "a cast", "unsound"], 1,
                   "Which is why map callbacks can take one argument."),
                _q("A function accepting a WIDER parameter than promised is…",
                   ["rejected", "accepted — that is contravariance", "unsound", "bivariant"], 1,
                   "It handles everything the caller could send."),
                _q("A function returning MORE than promised is…",
                   ["rejected", "accepted — that is covariance", "a cast", "unsound"], 1,
                   "Extra is never a problem for the caller."),
                _q("A member written with METHOD syntax is checked…",
                   ["contravariantly", "bivariantly, which is unsound", "covariantly", "never"], 1,
                   "strictFunctionTypes exempts it on purpose."),
            ],
            exercises=[
                _ex("tscourse-w12-fv-1", "Ignore the parameters you do not need",
                    "Supply a formatter that only declares the first parameter.",
                    'type Formatter = (value: string, index: number) => string;\n'
                    'const upper: Formatter = (v: string): string => v.toUpperCase();\n'
                    'console.log(upper("hi", 0));\n',
                    'const upper: Formatter = (v: string): string => v.toUpperCase();',
                    [("", "HI")],
                    hints=["The target type passes two arguments; yours may declare one.",
                           "Write const upper: Formatter = (v: string): string => v.toUpperCase();"]),
                _ex("tscourse-w12-fv-2", "Accept more than you were promised",
                    "Supply a formatter whose parameter is wider than `string`.",
                    'type Formatter = (value: string) => string;\n'
                    'const wide: Formatter = (v: string | number): string => String(v).toUpperCase();\n'
                    'console.log(wide("hi"));\n',
                    '(v: string | number): string => String(v).toUpperCase()',
                    [("", "HI")],
                    hints=["A parameter of `string | number` copes with every string it could be sent.",
                           "Convert with String(v) before uppercasing, since v might be a number."],
                    difficulty="Medium"),
                _ex("tscourse-w12-fv-3", "Return more than you promised",
                    "Supply a maker that returns an extra member beyond the two required.",
                    'type Make = () => { a: number; b: number };\n'
                    'const rich = (): { a: number; b: number; c: number } => ({ a: 1, b: 2, c: 3 });\n'
                    'const m: Make = rich;\n'
                    'const out = m();\n'
                    'console.log(out.a + out.b);\n',
                    'const m: Make = rich;', [("", "3")],
                    hints=["Returning more than the target type asks for is safe.",
                           "Write const m: Make = rich;"],
                    difficulty="Medium"),
                _predict("tscourse-w12-fv-p1", "What the target type gives back",
                         'type Make = () => { a: number; b: number };\n'
                         'const rich = (): { a: number; b: number; c: number } => ({ a: 1, b: 2, c: 3 });\n'
                         'const m: Make = rich;\n'
                         'const out = m();\n',
                         "out", "{ a: number; b: number }",
                         why="The value has three members. The question is what the ANNOTATION on "
                             "`m` lets you see.",
                         hints=["`out` is typed by `Make`'s return type, not by what `rich` really returns.",
                                "Lesson 2 again: the extra member is there at runtime and invisible to the type.",
                                "Write { a: number; b: number }."],
                         difficulty="Medium"),
                _diagnose("tscourse-w12-fv-d1", "The parameter that is too narrow",
                          "TS2322: Type '(v: string) => string' is not assignable to type 'Handler'. Types of parameters 'v' and 'v' are incompatible. Type 'string | number' is not assignable to type 'string'.",
                          'type Handler = (v: string | number) => string;\n'
                          'const onlyStrings = (v: string): string => v.toUpperCase();\n'
                          'const h: Handler = onlyStrings;\n'
                          'console.log(h(5));\n',
                          'type Handler = (v: string | number) => string;\n'
                          'const anyValue = (v: string | number): string => String(v).toUpperCase();\n'
                          'const h: Handler = anyValue;\n'
                          'console.log(h(5));\n',
                          [("", "5")],
                          hints=["`Handler` may be called with a number, and the call below does exactly that.",
                                 "A function stored in a Handler has to accept everything a Handler accepts.",
                                 "Widen the parameter to `string | number` and convert before uppercasing."],
                          difficulty="Medium"),
                _diagnose("tscourse-w12-fv-d2", "The return that under-delivers",
                          "TS2322: Type '() => { a: number; }' is not assignable to type 'Make'. Property 'b' is missing in type '{ a: number; }' but required in type '{ a: number; b: number; }'.",
                          'type Make = () => { a: number; b: number };\n'
                          'const thin = (): { a: number } => ({ a: 1 });\n'
                          'const m: Make = thin;\n'
                          'const out = m();\n'
                          'console.log(out.a + out.b);\n',
                          'type Make = () => { a: number; b: number };\n'
                          'const thin = (): { a: number; b: number } => ({ a: 1, b: 2 });\n'
                          'const m: Make = thin;\n'
                          'const out = m();\n'
                          'console.log(out.a + out.b);\n',
                          [("", "3")],
                          hints=["Returns are covariant: more is fine, less is not.",
                                 "The caller reads `out.b`, so the function has to produce one.",
                                 "Give it a `b` of 2."],
                          difficulty="Medium"),
                _fix("tscourse-w12-fv-fix1", "Fix the method bivariance crash",
                     "`Box.set` is declared with method syntax, so its narrower implementation was accepted — and `b.set(5)` then calls `.toUpperCase()` on a number and crashes. It should print 5.",
                     'interface Box {\n  set(v: string | number): void;\n}\n'
                     'const b: Box = {\n'
                     '  set(v: string): void {\n'
                     '    console.log(v.toUpperCase());\n  },\n};\n'
                     'b.set(5);\n',
                     'interface Box {\n  set(v: string | number): void;\n}\n'
                     'const b: Box = {\n'
                     '  set(v: string | number): void {\n'
                     '    console.log(String(v).toUpperCase());\n  },\n};\n'
                     'b.set(5);\n',
                     [("", "5")],
                     hints=["Method syntax is checked bivariantly, so the too-narrow parameter slipped through.",
                            "Widen the implementation's parameter to match what the interface promises, and convert before uppercasing.",
                            "Declaring the member as `set: (v: string | number) => void` would have made the compiler catch this."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("\"Be liberal in what you accept, conservative in what you return\" describes…",
                   ["covariance only", "contravariant parameters and covariant returns",
                    "bivariance", "structural typing"], 1,
                   "One sentence for both rules."),
                _q("`strictFunctionTypes` exempts method syntax because…",
                   ["it is faster", "Array<T> and much of the standard library would stop checking",
                    "methods are private", "of generics"], 1,
                   "A pragmatic, documented hole."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w12-arrays", "Array variance, and where it is unsound",
            "A hole you can watch open at runtime.",
            """
Arrays are **covariant** in TypeScript: `Dog[]` is assignable to `Animal[]`.

```ts
interface Animal { name: string; }
interface Dog extends Animal { fetch(): string; }

const dogs: Dog[] = [{ name: "rex", fetch: (): string => "ball" }];
const animals: Animal[] = dogs;      // ✅ allowed
```

That is convenient and it reads as obviously right — a list of dogs *is* a list
of animals. It is also **unsound**, and you can watch it break:

```ts
animals.push({ name: "tom" });       // ✅ a valid Animal

console.log(dogs.length);            // 2
dogs[1]!.fetch();                    // TypeError: fetch is not a function
```

(The `!` is only there to satisfy `noUncheckedIndexedAccess` — it says "there
*is* an element here", which is true. What is false is its **type**.)

`dogs` is typed `Dog[]`. Its second element is not a dog. No cast was used and
no rule was broken — `animals` and `dogs` are the **same array**, and pushing
an `Animal` into an `Animal[]` is exactly what the type permits.

## Why the language allows it

Because forbidding it would be worse. Almost all real code reads from arrays,
where covariance is perfectly safe, and rejecting `Dog[]` where `Animal[]` is
expected would make everyday code miserable. TypeScript takes the trade
knowingly and documents it. (Java made the same choice for arrays; C# too.)

## Closing the hole

The safe type is one with no mutating methods:

```ts
const safe: readonly Animal[] = dogs;
safe.push({ name: "tom" });
// ❌ TS2339: Property 'push' does not exist on type 'readonly Animal[]'.
```

`readonly T[]` is covariant *and* sound, because the operation that made it
unsound is gone. So: **take `readonly T[]` in a parameter unless you genuinely
intend to mutate.** It costs nothing, it accepts more callers, and it closes
this hole at the boundary where it matters. Week 13 makes this a habit.

## Objects have the same hole

Nothing about this is special to arrays. A mutable property behaves the same
way:

```ts
interface Kennel { pet: Animal; }
const dogHouse: { pet: Dog } = { pet: { name: "rex", fetch: () => "ball" } };
const k: Kennel = dogHouse;          // ✅
k.pet = { name: "tom" };             // ✅ — and dogHouse.pet is no longer a Dog
```

Same cause, same fix: `readonly pet: Animal` makes the assignment impossible.

## What this means in practice

Three habits come out of this lesson, and they are worth more than the theory:

1. Annotate parameters `readonly T[]` when the function only reads.
2. Be suspicious of a function that takes `Animal[]` and pushes into it.
3. When a value seems to have the wrong type at runtime despite compiling
   cleanly, aliasing through a covariant assignment is a prime suspect.

> ⚠️ **Common mistakes:** believing a clean compile proves an array's element
> type; assigning a narrower array to a wider one and then passing it to
> something that mutates; and using `Array<T>` in a parameter out of habit when
> `readonly T[]` would say what you meant.
""",
            warmup=[
                _q("`const animals: Animal[] = dogs;` where dogs is `Dog[]` is…",
                   ["rejected", "allowed, and unsound", "a cast", "sound"], 1,
                   "Covariant arrays are a known hole."),
                _q("After pushing a plain Animal into that array, `dogs` …",
                   ["is unaffected", "holds an element that is not a Dog", "throws", "is copied"], 1,
                   "They are the same array."),
                _q("`readonly Animal[]` closes the hole because…",
                   ["it copies", "there is no push to call", "it is nominal", "it is faster"], 1,
                   "Remove the mutation and covariance is safe."),
                _q("TypeScript allows the unsound rule because…",
                   ["it is a bug", "forbidding it would reject far too much everyday code",
                    "of generics", "arrays are special"], 1,
                   "A deliberate, documented trade."),
            ],
            exercises=[
                _ex("tscourse-w12-av-1", "Watch the hole open",
                    "Push a plain Animal into the widened array, then see what the Dog array now contains.",
                    'interface Animal {\n  name: string;\n}\n'
                    'interface Dog extends Animal {\n  fetch(): string;\n}\n'
                    'const dogs: Dog[] = [{ name: "rex", fetch: (): string => "ball" }];\n'
                    'const animals: Animal[] = dogs;\n'
                    'animals.push({ name: "tom" });\n'
                    'console.log(dogs.length);\n'
                    'console.log(dogs[1]?.fetch === undefined ? "no fetch" : "has fetch");\n',
                    'animals.push({ name: "tom" });', [("", "2\nno fetch")],
                    hints=["An Animal literal is a perfectly good thing to push into an Animal[].",
                           "The array is typed Dog[] elsewhere, and nothing stopped this.",
                           'Write animals.push({ name: "tom" });'],
                    difficulty="Medium"),
                _ex("tscourse-w12-av-2", "The type that cannot be mutated",
                    "Widen the dogs into a read-only view instead, so nothing can be pushed into it.",
                    'interface Animal {\n  name: string;\n}\n'
                    'interface Dog extends Animal {\n  fetch(): string;\n}\n'
                    'const dogs: Dog[] = [{ name: "rex", fetch: (): string => "ball" }];\n'
                    'const safe: readonly Animal[] = dogs;\n'
                    'console.log(`${safe.length} ${safe[0]?.name ?? "none"}`);\n',
                    'const safe: readonly Animal[] = dogs;', [("", "1 rex")],
                    hints=["Still covariant, but with no mutating methods at all.",
                           "Write const safe: readonly Animal[] = dogs;"],
                    difficulty="Medium"),
                _ex("tscourse-w12-av-3", "Read-only at the boundary",
                    "Type the parameter so the function accepts any array but cannot mutate it.",
                    'function longest(names: readonly string[]): string {\n'
                    '  let best = "";\n'
                    '  for (const n of names) {\n'
                    '    if (n.length > best.length) {\n      best = n;\n    }\n  }\n'
                    '  return best;\n}\n'
                    'const words: string[] = ["a", "coffee", "book"];\n'
                    'console.log(longest(words));\n',
                    'names: readonly string[]', [("", "coffee")],
                    hints=["The body only reads, so say so in the signature.",
                           "A mutable string[] is still accepted by such a parameter.",
                           "Write names: readonly string[]"],
                    difficulty="Medium"),
                _predict("tscourse-w12-av-p1", "What the widened array yields",
                         'interface Animal {\n  name: string;\n}\n'
                         'interface Dog extends Animal {\n  fetch(): string;\n}\n'
                         'const dogs: Dog[] = [{ name: "rex", fetch: (): string => "ball" }];\n'
                         'const animals: Animal[] = dogs;\n'
                         'const got = animals[0];\n',
                         "got", "Animal | undefined",
                         why="Two things are happening at once: the widening, and "
                             "noUncheckedIndexedAccess.",
                         hints=["The binding was widened to Animal[], so the element type is Animal — not Dog.",
                                "And indexing an array may find nothing.",
                                "Write Animal | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w12-av-d1", "The mutation that is not offered",
                          "TS2339: Property 'push' does not exist on type 'readonly Animal[]'.",
                          'interface Animal {\n  name: string;\n}\n'
                          'const animals: readonly Animal[] = [{ name: "rex" }];\n'
                          'animals.push({ name: "tom" });\n'
                          'console.log(animals.length);\n',
                          'interface Animal {\n  name: string;\n}\n'
                          'const animals: readonly Animal[] = [{ name: "rex" }];\n'
                          'const more: readonly Animal[] = [...animals, { name: "tom" }];\n'
                          'console.log(more.length);\n',
                          [("", "2")],
                          hints=["A read-only array deliberately has no mutating methods.",
                                 "Do not widen the type back — build a new array instead.",
                                 "Spread the old one and add the new element, then report that array's length."],
                          difficulty="Medium"),
                _fix("tscourse-w12-av-fix1", "Fix the helper that mutates its argument",
                     "`addDefault` pushes into the array it was given, so the caller's own list changes underneath it and this prints `2 2` instead of `1 2`. Make it leave the argument alone.",
                     'function addDefault(names: string[]): string[] {\n'
                     '  names.push("misc");\n'
                     '  return names;\n}\n'
                     'const tags: string[] = ["food"];\n'
                     'const out = addDefault(tags);\n'
                     'console.log(`${tags.length} ${out.length}`);\n',
                     'function addDefault(names: readonly string[]): string[] {\n'
                     '  return [...names, "misc"];\n}\n'
                     'const tags: string[] = ["food"];\n'
                     'const out = addDefault(tags);\n'
                     'console.log(`${tags.length} ${out.length}`);\n',
                     [("", "1 2")],
                     hints=["`tags` and `names` are the same array, so the push was visible to the caller.",
                            "Return a new array built from the old one instead of pushing.",
                            "Then type the parameter readonly, so the compiler enforces it from now on."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A clean compile proves an array's elements really have the element type…",
                   ["yes", "no — covariant assignment can put the wrong thing in",
                    "only under strict", "only for primitives"], 1,
                   "That is what unsound means."),
                _q("Prefer `readonly T[]` in a parameter because…",
                   ["it is faster", "it says the function only reads, and accepts mutable arrays anyway",
                    "it copies", "it is required"], 1,
                   "No cost, more callers, one fewer hole."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w12-satisfies", "`satisfies` vs annotation vs `as`",
            "Three ways to relate a value to a type. Only one both checks and remembers.",
            """
You have three tools. They are not interchangeable.

## The annotation checks — and widens

```ts
const rates: Record<string, number> = { food: 1, home: 2 };
```

The value is checked against `Record<string, number>`. But the binding's type is
now *exactly* that, and everything specific about the value is gone. Under
`noUncheckedIndexedAccess` — which this course has run under since week 6 — that
bites immediately:

```ts
console.log(rates.food + rates.home);
// ❌ TS18048: 'rates.food' is possibly 'undefined'.
```

The compiler is right. As far as the type is concerned, `rates` is a map from
*any* string to a number, so `food` might not be there. You knew it was; the
annotation threw that knowledge away.

## `as` does not check

```ts
const rates = { food: 1, home: "2" } as unknown as Record<string, number>;
console.log(rates.food);      // 1
console.log(rates.home);      // "2" — typed number, actually a string
```

A type assertion **overrides** the compiler. It is not a conversion and it
checks almost nothing; `as unknown as T` checks literally nothing. Every `as` in
a codebase is a place where the types stopped being evidence.

## `satisfies` checks without widening

```ts
const rates = { food: 1, home: 2 } satisfies Record<string, number>;

console.log(rates.food + rates.home);   // ✅ 3 — both are `number`
```

`satisfies` asks: *is this value assignable to that type?* If not, it is an
error. If so, the binding keeps **the type that was inferred from the value** —
here `{ food: number; home: number }`, which has both keys and no `undefined`.

And the check is real:

```ts
const bad = { food: 1, home: "two" } satisfies Record<string, number>;
// ❌ TS2322: Type 'string' is not assignable to type 'number'.
```

## The one-line summary

| | checks the value? | keeps the inferred type? |
|---|---|---|
| `const x: T = v` | yes | no — widened to T |
| `v as T` | barely | it becomes T, checked or not |
| `v satisfies T` | yes | **yes** |

**Reach for `satisfies` whenever you want a value validated against a contract
but still want to know exactly what you wrote.** Configuration tables, route
maps, colour palettes, the category budgets in this week's capstone — all the
same shape of problem.

Use an annotation when you genuinely want the wider type (a variable that will
later hold other values). Use `as` when you know something the compiler cannot,
and leave a comment saying what.

## With `as const`

The two compose, and this is the idiomatic pairing:

```ts
const CATEGORIES = ["food", "fun", "home"] as const;
type Category = (typeof CATEGORIES)[number];   // "food" | "fun" | "home"

const BUDGETS = {
  food: 5000,
  fun: 2000,
  home: 80000,
} satisfies Record<Category, number>;
```

`satisfies` proves every category has a budget — miss one and it is an error —
while `BUDGETS.food` stays a known `number` rather than `number | undefined`.
That is the capstone in miniature.

> ⚠️ **Common mistakes:** using `satisfies` where you wanted the wide type (a
> `let` that will be reassigned); thinking `as` converts anything; and
> annotating a config object with `Record<string, T>` and then fighting
> `possibly undefined` for the rest of the file.
""",
            warmup=[
                _q("`const r: Record<string, number> = { food: 1 }` makes `r.food`…",
                   ["number", "number | undefined under noUncheckedIndexedAccess",
                    "1", "never"], 1,
                   "The annotation widened away the key."),
                _q("`x as T` checks…",
                   ["as much as an annotation", "almost nothing — it overrides the compiler",
                    "the runtime value", "more than satisfies"], 1,
                   "It is an assertion, not a conversion."),
                _q("`v satisfies T` keeps…",
                   ["T", "the type inferred from v", "any", "unknown"], 1,
                   "Checked against T, typed as itself."),
                _q("`{ food: 1, home: \"two\" } satisfies Record<string, number>` is…",
                   ["accepted", "TS2322 — string is not number", "a cast", "widened"], 1,
                   "The check is real."),
            ],
            exercises=[
                _ex("tscourse-w12-sa-1", "Check without widening",
                    "Relate the table to the contract so both keys stay known numbers.",
                    'const rates = { food: 1, home: 2 } satisfies Record<string, number>;\n'
                    'console.log(rates.food + rates.home);\n',
                    'satisfies Record<string, number>', [("", "3")],
                    hints=["An annotation here would make each key `number | undefined`.",
                           "Write satisfies Record<string, number>"],
                    difficulty="Medium"),
                _ex("tscourse-w12-sa-2", "Prove every category is covered",
                    "Check the budget table against the categories, without losing the keys.",
                    'const CATEGORIES = ["food", "fun", "home"] as const;\n'
                    'type Category = (typeof CATEGORIES)[number];\n'
                    'const BUDGETS = {\n  food: 5000,\n  fun: 2000,\n  home: 80000,\n'
                    '} satisfies Record<Category, number>;\n'
                    'for (const c of CATEGORIES) {\n'
                    '  console.log(`${c} ${BUDGETS[c]}`);\n}\n',
                    '} satisfies Record<Category, number>;',
                    [("", "food 5000\nfun 2000\nhome 80000")],
                    hints=["Miss a category out of the table and this must fail to compile.",
                           "Write } satisfies Record<Category, number>;"],
                    difficulty="Medium"),
                _predict("tscourse-w12-sa-p1", "What satisfies left behind",
                         'const rates = { food: 1, home: 2 } satisfies Record<string, number>;\n'
                         'const got = rates.food;\n',
                         "got", "number",
                         why="The value was checked against Record<string, number> — but what "
                             "type did the BINDING end up with?",
                         hints=["satisfies does not widen, so `rates` keeps the type inferred from the literal.",
                                "That type has a `food` member, so no `| undefined` is involved.",
                                "Write number."],
                         difficulty="Medium"),
                _predict("tscourse-w12-sa-p2", "What the annotation left behind",
                         'const rates: Record<string, number> = { food: 1, home: 2 };\n'
                         'const got = rates.food;\n',
                         "got", "number | undefined",
                         why="Same value, same contract — but written as an annotation. "
                             "Compare your answer with the previous exercise.",
                         hints=["The binding's type is now exactly Record<string, number>.",
                                "An arbitrary string key might not be present, and this course runs under noUncheckedIndexedAccess.",
                                "Write number | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w12-sa-d1", "The annotation that forgot the keys",
                          "TS18048: 'rates.food' is possibly 'undefined'.",
                          'const rates: Record<string, number> = { food: 1, home: 2 };\n'
                          'console.log(rates.food + rates.home);\n',
                          'const rates = { food: 1, home: 2 } satisfies Record<string, number>;\n'
                          'console.log(rates.food + rates.home);\n',
                          [("", "3")],
                          hints=["The value obviously has a `food`. The annotation is what lost that.",
                                 "Do not paper over it with `!` or `?? 0` — keep the knowledge instead.",
                                 "Check the value against the contract without widening it."],
                          difficulty="Medium"),
                _diagnose("tscourse-w12-sa-d2", "The value that does not satisfy",
                          "TS2322: Type 'string' is not assignable to type 'number'.",
                          'const rates = { food: 1, home: "two" } satisfies Record<string, number>;\n'
                          'console.log(rates.food + rates.home);\n',
                          'const rates = { food: 1, home: 2 } satisfies Record<string, number>;\n'
                          'console.log(rates.food + rates.home);\n',
                          [("", "3")],
                          hints=["satisfies really does check — that is the difference from `as`.",
                                 "The contract says every value is a number."],
                          difficulty="Easy"),
                _fix("tscourse-w12-sa-fix1", "Fix what the assertion hid",
                     "A double assertion forced a bad table past the compiler, so `home` is typed `number` and is a string at runtime — this prints `12` (a string concatenation) instead of `3`. Replace the lie with a real check.",
                     'type Rates = Record<string, number>;\n'
                     'const rates = { food: 1, home: "2" } as unknown as Rates;\n'
                     'console.log((rates.food ?? 0) + (rates.home ?? 0));\n',
                     'type Rates = Record<string, number>;\n'
                     'const rates = { food: 1, home: 2 } satisfies Rates;\n'
                     'console.log(rates.food + rates.home);\n',
                     [("", "3")],
                     hints=["`as unknown as T` checks nothing at all, which is why the string got through.",
                            "Swap the assertion for `satisfies Rates` — and then the compiler will make you fix the data.",
                            "Once the keys are known again, the `?? 0` guards are unnecessary."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Use an annotation rather than satisfies when…",
                   ["never", "you genuinely want the wider type — a binding that will hold other values",
                    "the value is a literal", "under strict"], 1,
                   "Widening is sometimes the point."),
                _q("`as const` and `satisfies` together give you…",
                   ["nothing extra", "literal types AND a checked contract",
                    "a runtime check", "an enum"], 1,
                   "The idiomatic configuration-table pairing."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w12-branded", "Branded types",
            "Buying back nominal typing in three lines.",
            """
Structural typing has a cost, and here it is:

```ts
function transfer(fromId: number, toId: number, cents: number): void { … }

transfer(cents, fromId, toId);      // ✅ compiles perfectly
```

Three numbers. The compiler has no basis to object, because they *are* all
numbers. Every id, quantity, timestamp and amount in your program is the same
type as every other one.

## The trick

Intersect the primitive with a property nothing else will ever have:

```ts
type Cents = number & { readonly __brand: "Cents" };
```

Nothing can produce that type by accident: a plain `number` has no `__brand`,
and no object literal is also a `number`. So the only way to get one is to
assert it deliberately — which you do exactly once, in a **constructor
function**:

```ts
function cents(n: number): Cents {
  return n as Cents;
}

function show(c: Cents): string {
  return `$${(c / 100).toFixed(2)}`;
}

show(cents(325));      // ✅ $3.25
show(325);
// ❌ TS2345: Argument of type 'number' is not assignable to parameter of
//            type 'Cents'. Type 'number' is not assignable to type
//            '{ readonly __brand: "Cents"; }'.
```

That single `as` is the whole design. Keep it in one small function, give that
function any validation you want, and every other line in the program is
checked.

## Two brands do not mix

```ts
type Days = number & { readonly __brand: "Days" };
const days = (n: number): Days => n as Days;

show(days(5));
// ❌ TS2345: Type '"Days"' is not assignable to type '"Cents"'.
```

This is the payoff. `Cents` and `Days` were both `number` a moment ago;
now confusing them is a compile error, and the message names both brands.

## It still behaves like a number

Because `Cents` **is** a `number` (that is what the intersection says),
arithmetic works:

```ts
const total = cents(325) + cents(175);    // total: number — note, not Cents
```

The result widens back to `number`, which is usually what you want to notice —
it forces you to re-brand deliberately:

```ts
function addCents(a: Cents, b: Cents): Cents {
  return cents(a + b);
}
```

## It costs nothing at runtime

The brand is a phantom. There is no `__brand` property anywhere:

```ts
const c = cents(325);
console.log(typeof c);              // number
console.log(Object.keys(c).length); // 0
```

The type is erased with every other type. A branded type is a compile-time
labelling scheme with zero runtime weight — which is exactly why it is worth
reaching for.

## When to use it

When two values of the same primitive type mean different things and mixing
them would be a real bug: money vs quantity, user id vs order id, a validated
email vs an arbitrary string, a normalised path vs whatever the user typed.

Do not brand everything. The cost is a constructor function per brand and a
little noise in signatures.

> ⚠️ **Common mistakes:** exporting the brand type without its constructor, so
> callers reach for `as` themselves; forgetting that arithmetic widens back to
> the primitive; and expecting the brand to exist at runtime — it never does, so
> it cannot be checked with `typeof` or `instanceof`.
""",
            warmup=[
                _q("`type Cents = number & { readonly __brand: \"Cents\" }` works because…",
                   ["numbers have a __brand", "nothing else can produce that intersection",
                    "it is a class", "of generics"], 1,
                   "The only way in is a deliberate assertion."),
                _q("The constructor `cents(n: number): Cents` contains…",
                   ["a runtime check", "the single `as` the design allows", "a class",
                    "a generic"], 1,
                   "Keep it in one place and everything else is checked."),
                _q("At runtime, a Cents value is…",
                   ["an object", "just a number — the brand is erased", "a string", "wrapped"], 1,
                   "Zero runtime cost."),
                _q("`cents(1) + cents(2)` has type…",
                   ["Cents", "number — arithmetic widens back", "never", "unknown"], 1,
                   "Which is why you re-brand in a helper."),
            ],
            exercises=[
                _ex("tscourse-w12-br-1", "Declare the brand",
                    "Write the branded type: a number intersected with a phantom brand of \"Cents\".",
                    'type Cents = number & { readonly __brand: "Cents" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'function show(c: Cents): string {\n'
                    '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                    'console.log(show(cents(325)));\n',
                    'type Cents = number & { readonly __brand: "Cents" };',
                    [("", "$3.25")],
                    hints=["An intersection of the primitive and an object type with one readonly member.",
                           'Write type Cents = number & { readonly __brand: "Cents" };'],
                    difficulty="Medium"),
                _ex("tscourse-w12-br-2", "The only way in",
                    "Write the constructor's body — the one place the assertion is allowed to live.",
                    'type Cents = number & { readonly __brand: "Cents" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'function show(c: Cents): string {\n'
                    '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                    'console.log(show(cents(1250)));\n',
                    'return n as Cents;', [("", "$12.50")],
                    hints=["A plain number is not a Cents, so it has to be asserted.",
                           "Write return n as Cents;"]),
                _ex("tscourse-w12-br-3", "Re-brand after arithmetic",
                    "Add the two amounts and hand back a Cents again.",
                    'type Cents = number & { readonly __brand: "Cents" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'function addCents(a: Cents, b: Cents): Cents {\n'
                    '  return cents(a + b);\n}\n'
                    'function show(c: Cents): string {\n'
                    '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                    'console.log(show(addCents(cents(325), cents(175))));\n',
                    'return cents(a + b);', [("", "$5.00")],
                    hints=["`a + b` is a plain number — the brand does not survive arithmetic.",
                           "Send it back through the constructor rather than asserting again."],
                    difficulty="Medium"),
                _ex("tscourse-w12-br-4", "Prove the brand weighs nothing",
                    "Report the runtime type and the number of own keys, to show the brand is not really there.",
                    'type Cents = number & { readonly __brand: "Cents" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'const c = cents(325);\n'
                    'console.log(`${typeof c} ${Object.keys(c).length}`);\n',
                    'console.log(`${typeof c} ${Object.keys(c).length}`);',
                    [("", "number 0")],
                    hints=["`typeof` on the value, and the count of its own keys.",
                           "There is no __brand property anywhere — it exists only in the type."],
                    difficulty="Medium"),
                _diagnose("tscourse-w12-br-d1", "The unbranded number",
                          "TS2345: Argument of type 'number' is not assignable to parameter of type 'Cents'.",
                          'type Cents = number & { readonly __brand: "Cents" };\n'
                          'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                          'function show(c: Cents): string {\n'
                          '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                          'console.log(show(500));\n',
                          'type Cents = number & { readonly __brand: "Cents" };\n'
                          'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                          'function show(c: Cents): string {\n'
                          '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                          'console.log(show(cents(500)));\n',
                          [("", "$5.00")],
                          hints=["This is the error the brand exists to produce.",
                                 "Do not assert at the call site — there is a constructor for that."],
                          difficulty="Medium"),
                _diagnose("tscourse-w12-br-d2", "The two brands that do not mix",
                          "TS2345: Argument of type 'Days' is not assignable to parameter of type 'Cents'.",
                          'type Cents = number & { readonly __brand: "Cents" };\n'
                          'type Days = number & { readonly __brand: "Days" };\n'
                          'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                          'function days(n: number): Days {\n  return n as Days;\n}\n'
                          'function show(c: Cents): string {\n'
                          '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                          'console.log(show(days(500)));\n',
                          'type Cents = number & { readonly __brand: "Cents" };\n'
                          'type Days = number & { readonly __brand: "Days" };\n'
                          'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                          'function days(n: number): Days {\n  return n as Days;\n}\n'
                          'function show(c: Cents): string {\n'
                          '  return `$${(c / 100).toFixed(2)}`;\n}\n'
                          'console.log(show(cents(500)));\n',
                          [("", "$5.00")],
                          hints=["Both are numbers underneath, and the brands are what tell them apart.",
                                 "`show` deals in money — build the argument with the matching constructor."],
                          difficulty="Medium"),
                _types("tscourse-w12-br-t1", "A second, incompatible brand",
                       "Declare `Days` as a branded number, distinct from `Cents`. Graded by the "
                       "type-checker: the claims below say a Days must not pass where a Cents is wanted.",
                       'type Cents = number & { readonly __brand: "Cents" };\n'
                       'type Days = number & { readonly __brand: "Days" };\n',
                       'type Days = number & { readonly __brand: "Days" };',
                       """
const c = 1 as Cents;
const d = 1 as Days;

function show(x: Cents): string {
  return String(x);
}
show(c);

// A Days is a number too, and that must not be enough.
// @ts-expect-error
show(d);

// Nor is a plain number.
// @ts-expect-error
show(1);
""",
                       hints=["The same shape as Cents, with a different brand string.",
                              "The brand's VALUE is what makes the two incompatible.",
                              'Write type Days = number & { readonly __brand: "Days" };'],
                       difficulty="Medium"),
                _fix("tscourse-w12-br-fix1", "Fix the arguments in the wrong order",
                     "`record` takes the amount first and the day second, and the call has them the other way round — so it prints `$5.00 on day 325` instead of `$3.25 on day 500`. Brand the two parameters so this mistake becomes impossible, and fix the call.",
                     'function record(amount: number, day: number): string {\n'
                     '  return `$${(amount / 100).toFixed(2)} on day ${day}`;\n}\n'
                     'const amount = 325;\nconst day = 500;\n'
                     'console.log(record(day, amount));\n',
                     'type Cents = number & { readonly __brand: "Cents" };\n'
                     'type Days = number & { readonly __brand: "Days" };\n'
                     'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                     'function days(n: number): Days {\n  return n as Days;\n}\n'
                     'function record(amount: Cents, day: Days): string {\n'
                     '  return `$${(amount / 100).toFixed(2)} on day ${day}`;\n}\n'
                     'const amount = cents(325);\nconst day = days(500);\n'
                     'console.log(record(amount, day));\n',
                     [("", "$3.25 on day 500")],
                     hints=["Two numbers in a row is exactly the signature branding is for.",
                            "Declare Cents and Days with their constructors, then annotate the parameters.",
                            "Build the two values through their constructors and pass them in the declared order — the compiler will now refuse the swap."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The brand property should be…",
                   ["set at runtime", "phantom — declared in the type and never assigned",
                    "a class field", "a string value"], 1,
                   "It never exists when the program runs."),
                _q("Brand a type when…",
                   ["always", "two values of the same primitive mean different things and mixing them is a bug",
                    "the type is a number", "you use generics"], 1,
                   "Money vs quantity, user id vs order id."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w12-enums", "`enum`, and why a literal union usually wins",
            "The comparison, made concrete.",
            """
An `enum` names a set of constants:

```ts
enum Level {
  Low,       // 0
  High,      // 1
}

enum Tag {
  Food = "food",
  Home = "home",
}
```

You will meet enums in real codebases, so you need to read them. You will
mostly not want to write them, and this lesson is the argument for that rather
than an assertion of it.

## Reason 1: an enum is not erasable syntax

Every other type in this course disappears when the annotations are stripped. An
enum does not — it **emits a real object** at runtime, because `Tag.Food` has to
evaluate to something:

```
ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX: TypeScript enum is not supported
in strip-only mode
```

That is this course's runner refusing to execute one, and it is the same reason
week 11's parameter properties could not run. It is not a quirk of this app:
Node's type stripping, `esbuild` in some configurations, and the
`--erasableSyntaxOnly` compiler flag all draw the same line. Anything you write
with an enum requires a toolchain that *transforms* TypeScript rather than
merely stripping it.

That is why every enum exercise below is graded by the type-checker alone.

## Reason 2: the members are nominal, awkwardly

A string enum's member is not the string:

```ts
enum Tag { Food = "food", Home = "home" }

const t: Tag = "food";
// ❌ TS2322: Type '"food"' is not assignable to type 'Tag'.
```

Everything that crosses a boundary — JSON from an API, a value read from stdin,
a database column — arrives as a plain string, and every one of those points
needs a conversion back into the enum. With a literal union there is nothing to
convert.

## Reason 3: numeric enums are loose

A numeric enum also builds a **reverse mapping** at runtime (`Level[0]` is
`"Low"`), which means `Object.keys` on it gives you both directions and rarely
what you expected. Historically a numeric enum would also accept any number at
all; modern TypeScript has tightened that, but the reverse mapping remains.

## The replacement: a literal union

```ts
type Tag = "food" | "fun" | "home";

function budget(t: Tag): number {
  switch (t) {
    case "food":
      return 50;
    case "fun":
      return 20;
    case "home":
      return 800;
  }
}
```

Erasable, plain strings work, and you keep the exhaustiveness checking from
week 9 — remove one `case` and the function no longer returns on every path.

## When you need the VALUES at runtime

A union is only a type; there is nothing to iterate. When you need the list at
runtime, use an `as const` object — the other half of lesson 6's pairing:

```ts
const Tag = {
  Food: "food",
  Home: "home",
} as const;

type Tag = (typeof Tag)[keyof typeof Tag];    // "food" | "home"

const t: Tag = Tag.Food;
Object.keys(Tag);        // ["Food", "Home"] — one direction, no surprises
```

That gives you everything an enum offered — a namespace, named members, the
values at runtime — while staying erasable and still accepting a plain
`"food"`. Declaring the const and the type with the same name is deliberate and
legal: TypeScript keeps values and types in separate namespaces, so `Tag` is
both.

## The honest summary

Use a literal union by default. Use an `as const` object when you need the
values at runtime. Reach for `enum` when a codebase already uses them
consistently — matching the surrounding style is worth more than being right in
one file.

> ⚠️ **Common mistakes:** assuming a string enum member is interchangeable with
> its string; using `const enum` (it has its own inlining problems and is
> disallowed under `isolatedModules`); and reaching for an enum when a
> three-member union would have done.
""",
            warmup=[
                _q("An enum cannot run under type stripping because…",
                   ["it is deprecated", "it emits a runtime object, so it is not erasable",
                    "it is slow", "of generics"], 1,
                   "Same reason as week 11's parameter properties."),
                _q("`enum Tag { Food = \"food\" }` then `const t: Tag = \"food\"` is…",
                   ["fine", "TS2322 — the member is not the plain string", "a warning", "unchecked"], 1,
                   "Which is friction at every boundary."),
                _q("A numeric enum also builds…",
                   ["a class", "a reverse mapping from number back to name", "a union", "a brand"], 1,
                   "So Object.keys gives both directions."),
                _q("When you need the list of values at RUNTIME, use…",
                   ["a literal union", "an `as const` object", "an interface", "a brand"], 1,
                   "A bare union has no runtime representation."),
            ],
            exercises=[
                _types("tscourse-w12-en-t1", "Write a string enum",
                       "Declare the two members `Food = \"food\"` and `Home = \"home\"`. Graded by "
                       "the type-checker: an enum is not erasable, so it cannot be run here.",
                       'enum Tag {\n  Food = "food",\n  Home = "home",\n}\n',
                       'Food = "food",\n  Home = "home",',
                       """
type _1 = Expect<Equal<keyof typeof Tag, "Food" | "Home">>;

const t: Tag = Tag.Food;

// Reason 2 from the lesson: even a STRING enum's member is not the string.
// @ts-expect-error
const bad: Tag = "food";
""",
                       hints=["Two members, each with an explicit string value, comma-separated.",
                              "The member names are capitalised; the values are lower case.",
                              'Write Food = "food", then Home = "home",'],
                       difficulty="Medium"),
                _types("tscourse-w12-en-t2", "Write a numeric enum",
                       "Declare the two members `Low` and `High` with no explicit values, so they "
                       "number themselves from 0.",
                       'enum Level {\n  Low,\n  High,\n}\n',
                       'Low,\n  High,',
                       """
type _1 = Expect<Equal<keyof typeof Level, "Low" | "High">>;

// A numeric enum member IS assignable to number...
const n: number = Level.Low;

// ...but an arbitrary number is not one of the declared members.
// @ts-expect-error
const bad: Level = 7;
""",
                       hints=["Just the two names, with no `=` at all.",
                              "A numeric enum numbers its members from 0 automatically.",
                              "Write Low, then High,"],
                       difficulty="Medium"),
                _ex("tscourse-w12-en-1", "The literal union instead",
                    "Declare the tag type as a union of the two string literals.",
                    'type Tag = "food" | "home";\n'
                    'function label(t: Tag): string {\n  return t.toUpperCase();\n}\n'
                    'console.log(label("food"));\n',
                    'type Tag = "food" | "home";', [("", "FOOD")],
                    hints=["Two string literal types, joined by a bar.",
                           "Note that the plain string \"food\" then just works.",
                           'Write type Tag = "food" | "home";'],
                    difficulty="Medium"),
                _ex("tscourse-w12-en-2", "Exhaustiveness survives",
                    "Handle the last case, so the switch covers the whole union and the function returns on every path.",
                    'type Tag = "food" | "fun" | "home";\n'
                    'function budget(t: Tag): number {\n'
                    '  switch (t) {\n'
                    '    case "food":\n      return 50;\n'
                    '    case "fun":\n      return 20;\n'
                    '    case "home":\n      return 800;\n'
                    '  }\n}\n'
                    'console.log(`${budget("fun")} ${budget("home")}`);\n',
                    '    case "home":\n      return 800;',
                    [("", "20 800")],
                    hints=["Without every member covered, the function can fall off the end and stops compiling.",
                           "Add the home case, returning 800."],
                    difficulty="Medium"),
                _ex("tscourse-w12-en-3", "The as const object, when you need the values",
                    "Derive the union type from the object's values.",
                    'const Tag = {\n  Food: "food",\n  Home: "home",\n} as const;\n'
                    'type Tag = (typeof Tag)[keyof typeof Tag];\n'
                    'const t: Tag = Tag.Food;\n'
                    'console.log(`${t} ${Object.keys(Tag).join(",")}`);\n',
                    'type Tag = (typeof Tag)[keyof typeof Tag];',
                    [("", "food Food,Home")],
                    hints=["`typeof Tag` is the object's type; `keyof` gives its key names.",
                           "Indexing the object type by all of its keys gives the union of its VALUES.",
                           "Write type Tag = (typeof Tag)[keyof typeof Tag];"],
                    difficulty="Medium"),
                _predict("tscourse-w12-en-p1", "What as const preserved",
                         'const Tag = {\n  Food: "food",\n  Home: "home",\n} as const;\n',
                         "Tag.Food", '"food"',
                         why="Without `as const` this would be `string`. With it, something more "
                             "specific survived.",
                         hints=["A const assertion stops literal types from widening.",
                                "The answer is the literal type, not the primitive.",
                                'Write "food" — with the quotes.'],
                         difficulty="Medium"),
                _diagnose("tscourse-w12-en-d1", "The string that is not the member",
                          "TS2345: Argument of type '\"food\"' is not assignable to parameter of type 'Tag'.",
                          'enum Tag {\n  Food = "food",\n  Home = "home",\n}\n'
                          'function label(t: Tag): string {\n  return t.toUpperCase();\n}\n'
                          'console.log(label("food"));\n',
                          'type Tag = "food" | "home";\n'
                          'function label(t: Tag): string {\n  return t.toUpperCase();\n}\n'
                          'console.log(label("food"));\n',
                          [("", "FOOD")],
                          hints=["A plain string arriving from outside will never be an enum member.",
                                 "You could convert at every boundary — or remove the need to.",
                                 "Replace the enum with the literal union it was standing in for; the rest of the program is unchanged."],
                          difficulty="Medium"),
                _fix("tscourse-w12-en-fix1", "Fix the lookup that lost its keys",
                     "The budget table is annotated rather than checked, so every lookup is `number | undefined` and the `?? 0` fallbacks silently turn a typo'd category into 0 — this prints `0` instead of `20`. Keep the categories known.",
                     'type Tag = "food" | "fun" | "home";\n'
                     'const BUDGETS: Record<string, number> = { food: 50, fun: 20, home: 800 };\n'
                     'function budget(t: Tag): number {\n'
                     '  return BUDGETS[t + "!"] ?? 0;\n}\n'
                     'console.log(budget("fun"));\n',
                     'type Tag = "food" | "fun" | "home";\n'
                     'const BUDGETS = { food: 50, fun: 20, home: 800 } satisfies Record<Tag, number>;\n'
                     'function budget(t: Tag): number {\n'
                     '  return BUDGETS[t];\n}\n'
                     'console.log(budget("fun"));\n',
                     [("", "20")],
                     hints=["`Record<string, number>` accepts any string key, so the mangled one raised no complaint.",
                            "Check the table with `satisfies Record<Tag, number>` instead of annotating it.",
                            "Then index it with the tag itself — the key is known, so no `?? 0` is needed and the mangled key no longer compiles."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("The default choice for a small fixed set of names is…",
                   ["enum", "a literal union", "const enum", "a class"], 1,
                   "Erasable, and plain strings work."),
                _q("Declaring `const Tag = {...}` and `type Tag = ...` with the same name is…",
                   ["an error", "legal — values and types live in separate namespaces",
                    "a cast", "shadowing"], 1,
                   "Which is what makes the as const pattern read so well."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #12 — a branded Money type",
        """
Budget Buddy has been adding plain numbers together since week 1. Nothing has
stopped a quantity, a day count or a raw dollar figure being passed where cents
were expected. This week closes that, and adds a budget table the compiler
checks.

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
food:     $12.75 of $50.00 ok
fun:      $12.00 of $20.00 ok
home:     $900.00 of $800.00 OVER
```

Build this scaffolding:

```ts
type Cents = number & { readonly __brand: "Cents" };
function cents(n: number): Cents            // the ONLY way to make one
function addCents(a: Cents, b: Cents): Cents
function money(c: Cents): string            // "$3.25"

const CATEGORIES = ["food", "fun", "home"] as const;
type Category = (typeof CATEGORIES)[number];
const BUDGETS = { … } satisfies Record<Category, number>;

function toCategory(s: string): Category    // throws on an unknown tag
```

Rules:

- **Every amount in the program is a `Cents`.** The only `as` in the whole file
  is the one inside `cents`. If you find yourself asserting anywhere else, the
  brand is not doing its job.
- `BUDGETS` must be checked with **`satisfies`**, not annotated. Miss a category
  and the program must fail to compile; and `BUDGETS[c]` must stay a plain
  `number`, with no `?? 0` anywhere.
- The category lines are printed in `CATEGORIES` order — not sorted, not input
  order — and a category with no rows still prints, at `$0.00`.
- Each line is `${(c + ":").padEnd(10)}` then the spend, `" of "`, the budget,
  and `ok` or `OVER`. A category is `OVER` only when it is **strictly** above
  its budget.
- `toCategory` rejects an unknown tag by throwing, so a bad input never quietly
  becomes a category.
""",
        _ch("tscourse-w12-capstone", "Budget Buddy #12", "Medium",
            "Write the branded money type, its three helpers, the checked budget table and the tag validator.",
            _FS + 'type Cents = number & { readonly __brand: "Cents" };\n'
            'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
            'function addCents(a: Cents, b: Cents): Cents {\n  return cents(a + b);\n}\n'
            'function money(c: Cents): string {\n'
            '  return `$${(c / 100).toFixed(2)}`;\n}\n'
            'const CATEGORIES = ["food", "fun", "home"] as const;\n'
            'type Category = (typeof CATEGORIES)[number];\n'
            'const BUDGETS = {\n  food: 5000,\n  fun: 2000,\n  home: 80000,\n'
            '} satisfies Record<Category, number>;\n'
            'function toCategory(s: string): Category {\n'
            '  for (const c of CATEGORIES) {\n'
            '    if (c === s) {\n      return c;\n    }\n  }\n'
            '  throw new Error(`unknown category: ${s}`);\n}\n'
            'const totals: Record<Category, Cents> = {\n'
            '  food: cents(0),\n  fun: cents(0),\n  home: cents(0),\n};\n'
            'let count = 0;\n'
            'let total: Cents = cents(0);\n'
            'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
            '  const p = line.trim().split(" ");\n'
            '  const amount = cents(Math.round(Number(p[1] ?? "0") * 100));\n'
            '  const cat = toCategory(p[2] ?? "");\n'
            '  totals[cat] = addCents(totals[cat], amount);\n'
            '  total = addCents(total, amount);\n'
            '  count = count + 1;\n}\n'
            'console.log(`Entries:  ${count}`);\n'
            'console.log(`Total:    ${money(total)}`);\n'
            'for (const c of CATEGORIES) {\n'
            '  const spent = totals[c];\n'
            '  const budget = cents(BUDGETS[c]);\n'
            '  const status = spent > budget ? "OVER" : "ok";\n'
            '  console.log(`${(c + ":").padEnd(10)}${money(spent)} of ${money(budget)} ${status}`);\n}\n',
            'type Cents = number & { readonly __brand: "Cents" };\n'
            'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
            'function addCents(a: Cents, b: Cents): Cents {\n  return cents(a + b);\n}\n'
            'function money(c: Cents): string {\n'
            '  return `$${(c / 100).toFixed(2)}`;\n}\n'
            'const CATEGORIES = ["food", "fun", "home"] as const;\n'
            'type Category = (typeof CATEGORIES)[number];\n'
            'const BUDGETS = {\n  food: 5000,\n  fun: 2000,\n  home: 80000,\n'
            '} satisfies Record<Category, number>;\n'
            'function toCategory(s: string): Category {\n'
            '  for (const c of CATEGORIES) {\n'
            '    if (c === s) {\n      return c;\n    }\n  }\n'
            '  throw new Error(`unknown category: ${s}`);\n}',
            [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
              "Entries:  4\nTotal:    $924.75\n"
              "food:     $12.75 of $50.00 ok\n"
              "fun:      $12.00 of $20.00 ok\n"
              "home:     $900.00 of $800.00 OVER"),
             ("tea 2 food",
              "Entries:  1\nTotal:    $2.00\n"
              "food:     $2.00 of $50.00 ok\n"
              "fun:      $0.00 of $20.00 ok\n"
              "home:     $0.00 of $800.00 ok"),
             ("gift 25 fun",
              "Entries:  1\nTotal:    $25.00\n"
              "food:     $0.00 of $50.00 ok\n"
              "fun:      $25.00 of $20.00 OVER\n"
              "home:     $0.00 of $800.00 ok")],
            hints=["`Cents` is `number & { readonly __brand: \"Cents\" }`, and `cents` is the only place `as` appears.",
                   "addCents adds the two and sends the result back through `cents` — arithmetic widens the brand away.",
                   "CATEGORIES is `as const`, and Category is `(typeof CATEGORIES)[number]` — the union of its elements.",
                   "BUDGETS uses `satisfies Record<Category, number>` so every key stays known: BUDGETS[c] is a plain number.",
                   "toCategory walks CATEGORIES comparing with ===, returns the matching literal, and throws if none matched.",
                   "The budgets are in cents: food 5000, fun 2000, home 80000.",
                   "Print with `${(c + \":\").padEnd(10)}` so the columns line up with the two header lines."]),
        example_io="Entries:  4\nTotal:    $924.75\nfood:     $12.75 of $50.00 ok\nfun:      $12.00 of $20.00 ok\nhome:     $900.00 of $800.00 OVER",
        rubric=["Cents is a branded number, and the only `as` in the file is inside its constructor",
                "addCents re-brands the sum rather than asserting again",
                "CATEGORIES is `as const` and Category is derived from it, not written out twice",
                "BUDGETS is checked with satisfies, so BUDGETS[c] needs no `?? 0`",
                "toCategory throws on an unknown tag instead of defaulting",
                "Categories print in CATEGORIES order, including ones with no rows",
                "OVER is strict: exactly on budget prints ok"],
        stretch=_ch("tscourse-w12-capstone-stretch", "Budget Buddy #12 (stretch)", "Medium",
                    "Add a SECOND brand — `type Percent = number & { readonly __brand: \"Percent\" }` "
                    "— with a `percent(part: Cents, whole: Cents): Percent` that returns the "
                    "rounded whole-number percentage (0 when the whole is 0). Print "
                    "`Used:     106%`: the total spend against the sum of all three budgets. "
                    "Because Percent and Cents are different brands, neither can be passed where "
                    "the other is expected.",
                    _FS + 'type Cents = number & { readonly __brand: "Cents" };\n'
                    'type Percent = number & { readonly __brand: "Percent" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'function addCents(a: Cents, b: Cents): Cents {\n  return cents(a + b);\n}\n'
                    'function percent(part: Cents, whole: Cents): Percent {\n'
                    '  return (whole === 0 ? 0 : Math.round((part / whole) * 100)) as Percent;\n}\n'
                    'const BUDGETS = {\n  food: 5000,\n  fun: 2000,\n  home: 80000,\n'
                    '} satisfies Record<string, number>;\n'
                    'let total: Cents = cents(0);\n'
                    'for (const line of fs.readFileSync(0, "utf8").trim().split("\\n")) {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  total = addCents(total, cents(Math.round(Number(p[1] ?? "0") * 100)));\n}\n'
                    'const whole = cents(BUDGETS.food + BUDGETS.fun + BUDGETS.home);\n'
                    'console.log(`Used:     ${percent(total, whole)}%`);\n',
                    'type Percent = number & { readonly __brand: "Percent" };\n'
                    'function cents(n: number): Cents {\n  return n as Cents;\n}\n'
                    'function addCents(a: Cents, b: Cents): Cents {\n  return cents(a + b);\n}\n'
                    'function percent(part: Cents, whole: Cents): Percent {\n'
                    '  return (whole === 0 ? 0 : Math.round((part / whole) * 100)) as Percent;\n}',
                    [("coffee 3.25 food\nrent 900 home\nlunch 9.50 food\nbook 12 fun",
                      "Used:     106%"),
                     ("tea 2 food", "Used:     0%")],
                    hints=["The second brand is the same shape with a different brand string.",
                           "Guard the zero whole first, then Math.round((part / whole) * 100).",
                           "The division produces a plain number, so the assertion to Percent goes around the whole expression.",
                           "The three budgets sum to 87000 cents."]),
    ),
))
