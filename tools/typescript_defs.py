# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript foundational Learn track.
#
# This file is exec()'d inside gen_seed.py's namespace (see the hook near the
# expansion_defs.py include). It extends CONCEPTS / CATEGORY / LESSONS /
# EXERCISES in place with a beginner TypeScript curriculum. Every concept is
# marked  "language": "typescript"  so the Learn tab's language toggle shows it
# only under the TypeScript view.
#
# EXECUTION MODEL (important, drives how the drills are written):
#   Drills run through the SAME stdin/stdout judge as Java, via
#   `node --experimental-strip-types --no-warnings main.ts` (see exec.rs).
#   Consequences that shaped every program below:
#     * TypeScript *types are stripped before running* — so a fill-in-the-blank
#       must target a RUNTIME piece (a value/expression/statement whose result
#       changes stdout), never a pure type annotation (which the runtime can't
#       validate).
#     * `enum` and constructor parameter-properties (`constructor(public x)`)
#       are NOT supported by type-stripping — they are taught in prose only;
#       graded code uses `as const` / string-literal unions and explicit fields.
#     * Node runs the `.ts` file as an ES module, so top-level `await`,
#       `import`, and `export` all work.
#   Every `solution` here is verified end-to-end by tests/verify_exercises.rs
#   (it runs each one through the real judge and asserts Accepted).
# ---------------------------------------------------------------------------


def _P(src):
    """Normalize a triple-quoted program: drop the leading newline, guarantee a
    single trailing newline. Top-level code has no indentation, so blanks are
    whole lines and match uniquely."""
    return src.lstrip("\n").rstrip() + "\n"


def tsx(eid, title, prompt, full, blanks, tests, hint="", source_slug=None):
    """Like gen_seed.ex(), but tags the drill as TypeScript."""
    starter = full
    for b in blanks:
        assert b in full, f"ts exercise {eid}: blank not found in solution: {b!r}"
        starter = starter.replace(b, "____", 1)
    assert starter != full, f"ts exercise {eid}: no blank was applied"
    assert tests, f"ts exercise {eid}: needs at least one test"
    return {
        "id": eid,
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "typescript",
        "starter": starter,
        "solution": full,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
        "source_slug": source_slug or "",
    }


# Standard input-reading preamble reused across drills. Reading stdin is
# boilerplate a beginner shouldn't have to re-derive, so most drills read the
# input for you and leave the teaching line as the blank.
_FS = 'import * as fs from "fs";\n'


# ===========================================================================
# CONCEPTS  (name / what / deep / java=TS-note / language)
# ===========================================================================
TS_CONCEPTS = {
    # -- Language basics ----------------------------------------------------
    "ts_variables": {
        "name": "Variables — let & const",
        "what": "Naming values with const (fixed binding) and let (reassignable), both block-scoped.",
        "deep": "A variable is a named box for a value. `const` locks the name to one value; `let` allows reassignment. Both live only inside the `{ }` block they are declared in. Reach for `const` by default and only switch to `let` when you truly need to reassign.",
        "java": "`const x = 5;` and `let y = 5;` replace Java's `final int x` / `int y`. No `var` (function-scoped, avoid it). Types are usually inferred, so `const x = 5` already has type `number`.",
        "language": "typescript",
    },
    "ts_types": {
        "name": "Primitive Types & Annotations",
        "what": "The built-in value types (number, string, boolean, null, undefined) and how to annotate them.",
        "deep": "TypeScript adds a type to every value. The primitives you meet first are `number` (one type for ints and floats), `string`, `boolean`, plus `null` and `undefined`. You write a type after a colon — `let n: number` — but usually inference figures it out for you.",
        "java": "One `number` covers Java's int/long/double. `string` is lowercase (the type), `String` capitalized is something else. `boolean` holds `true`/`false`. There is no `char` — a single character is just a length-1 `string`.",
        "language": "typescript",
    },
    "ts_inference": {
        "name": "Type Inference, any & unknown",
        "what": "Letting TypeScript work out types for you, and the escape hatches any and unknown.",
        "deep": "When you initialize a variable, TypeScript infers its type — `const x = 3` is a `number` without you saying so. `any` turns checking off for a value (avoid it); `unknown` is the safe alternative that forces you to narrow before use.",
        "java": "Inference is like Java's `var`, but pervasive. `any` opts out of all checking (a foot-gun); prefer `unknown` and narrow with `typeof` before using the value.",
        "language": "typescript",
    },
    "ts_strings": {
        "name": "Strings & Template Literals",
        "what": "Building and inspecting text, and interpolating values with backtick templates.",
        "deep": "Strings are immutable sequences of characters. Backtick templates `` `Hi ${name}` `` splice values straight into text — clearer than `+` chains. Common tools: `.length`, `.toUpperCase()`, `.slice()`, `.includes()`, `.split()`.",
        "java": "`` `${a} and ${b}` `` replaces Java's string concatenation and `String.format`. Methods are camelCase and mostly match (`length` is a property, not `length()`). Indexing uses `s[i]` or `s.charAt(i)`.",
        "language": "typescript",
    },
    "ts_operators": {
        "name": "Operators & Expressions",
        "what": "Arithmetic, comparison, logical operators, plus ?? (nullish) and ?. (optional chaining).",
        "deep": "Expressions combine values with operators. Beyond the usual `+ - * / %` and `< > === !==`, TypeScript has two everyday safety operators: `??` supplies a fallback only when the left side is null/undefined, and `?.` reads a property only if the object exists.",
        "java": "Always compare with `===`/`!==` (strict, no coercion), never `==`. `%` is remainder. `a ?? b` is like `a != null ? a : b`; `obj?.prop` short-circuits to `undefined` instead of throwing an NPE.",
        "language": "typescript",
    },
    "ts_conditionals": {
        "name": "Conditionals & Truthiness",
        "what": "Branching with if/else and switch, and which values count as true or false.",
        "deep": "`if` runs a block when a condition is truthy. Empty string, 0, null, undefined, and NaN are 'falsy'; everything else is 'truthy'. `switch` compares one value against many cases (remember `break`). Ternary `cond ? a : b` is an expression form.",
        "java": "`if`, `else if`, `switch` look like Java, but the condition need not be a boolean — any value is tested for truthiness. `switch` uses `===` and needs `break` between cases.",
        "language": "typescript",
    },
    "ts_loops": {
        "name": "Loops",
        "what": "Repeating work with for, for…of, for…in, while and do…while.",
        "deep": "`for (let i…)` counts with an index; `for…of` walks the *values* of an array; `for…in` walks the *keys* of an object. `while` repeats until a condition fails. `break` stops the loop; `continue` skips to the next turn.",
        "java": "`for…of` is Java's enhanced for (`for (x : arr)`). Do NOT use `for…in` on arrays — it yields string keys, not elements. Classic `for (let i = 0; i < n; i++)` still works for index math.",
        "language": "typescript",
    },
    # -- Functions & types --------------------------------------------------
    "ts_functions": {
        "name": "Functions & Arrow Functions",
        "what": "Declaring reusable logic with function declarations, expressions, and arrow syntax.",
        "deep": "A function packages steps behind a name. You annotate parameter types and (optionally) a return type: `function add(a: number, b: number): number`. Arrow functions `(a, b) => a + b` are a compact form used constantly for callbacks.",
        "java": "Return type goes *after* the parameters. Arrow functions `(x) => x * 2` are like Java lambdas but also usable as top-level functions. A `: void` return means 'returns nothing'.",
        "language": "typescript",
    },
    "ts_params": {
        "name": "Optional, Default & Rest Parameters",
        "what": "Flexible parameter lists: optional (?), defaults (=), and variadic rest (…).",
        "deep": "A `?` marks a parameter optional (it may be `undefined`). A default `= value` fills in when the argument is omitted. A rest parameter `...nums: number[]` collects any number of trailing arguments into an array.",
        "java": "`...nums: number[]` is Java's varargs `int... nums`. Defaults (`p = 10`) and optionals (`p?`) have no direct Java equivalent — they remove most overloads. Optional params must come after required ones.",
        "language": "typescript",
    },
    "ts_unions": {
        "name": "Union & Literal Types",
        "what": "Types that allow several shapes (A | B) and exact-value literal types.",
        "deep": "A union `string | number` says a value is one of several types. A literal type like `\"N\" | \"S\" | \"E\" | \"W\"` restricts a value to an exact set of strings — a lightweight, type-safe alternative to enums.",
        "java": "There is no Java equivalent to `\"red\" | \"green\"` — it constrains a plain string to a fixed set at compile time. Unions replace many small class hierarchies. You must narrow a union before using type-specific methods.",
        "language": "typescript",
    },
    "ts_aliases": {
        "name": "Type Aliases & Interfaces",
        "what": "Naming a type with `type`, and describing object shapes with `interface`.",
        "deep": "`type ID = string | number` gives a name to any type. `interface Point { x: number; y: number }` describes the shape an object must have. Both let you write the shape once and reuse it; interfaces are the usual choice for object shapes.",
        "java": "An `interface` here just lists fields an object must have (no implementation, no `implements` needed — shape matching is structural). `type` can name unions and primitives too, which Java interfaces cannot.",
        "language": "typescript",
    },
    "ts_narrowing": {
        "name": "Type Narrowing",
        "what": "Convincing TypeScript (and yourself) which specific type a value has right now.",
        "deep": "When a value could be several types, you narrow it with a runtime check: `typeof x === \"number\"`, `\"key\" in obj`, a truthiness test, or `Array.isArray(x)`. Inside the checked branch TypeScript knows the exact type — and so does your logic.",
        "java": "`typeof x === \"string\"` plays the role of `instanceof` for primitives. Narrowing is how you safely 'unpack' a union — the runtime check and the compile-time type refinement happen together.",
        "language": "typescript",
    },
    # -- Data structures ----------------------------------------------------
    "ts_arrays": {
        "name": "Arrays & Tuples",
        "what": "Ordered, growable lists (number[]) and fixed-shape tuples ([number, string]).",
        "deep": "An array `number[]` is an ordered, resizable list — push/pop at the end, index with `arr[i]`, length via `arr.length`. A tuple `[number, string]` is a fixed-length array where each position has its own type.",
        "java": "Arrays here are dynamic like `ArrayList` — `.push()` grows them, no fixed size. `number[]` and `Array<number>` are the same type. Tuples `[a, b]` have no Java analogue; they type a fixed-position pair.",
        "language": "typescript",
    },
    "ts_array_methods": {
        "name": "Array Methods",
        "what": "Transforming lists with map, filter, reduce, find, some/every and sort.",
        "deep": "Array methods express loops declaratively: `map` transforms every element, `filter` keeps the ones matching a test, `reduce` folds a list to one value, `find` returns the first match, `some`/`every` answer yes/no. Each takes a callback.",
        "java": "These are the Stream operations without the `.stream()`/`.collect()` ceremony — called straight on the array and returning a new array. Note `sort` mutates in place and sorts *as strings* by default; pass `(a, b) => a - b` for numbers.",
        "language": "typescript",
    },
    "ts_objects": {
        "name": "Objects",
        "what": "Key–value records with typed fields, optional properties, and index signatures.",
        "deep": "An object groups named fields: `{ name: \"Ada\", age: 36 }`. Fields can be optional (`age?: number`), read-only (`readonly id`), and an index signature `{ [k: string]: number }` types a map-like bag of arbitrary keys.",
        "java": "Object literals are like anonymous POJOs typed by shape. Access with `obj.field` or `obj[\"field\"]`. `Object.keys(o)`, `Object.values(o)`, `Object.entries(o)` iterate them — handy when using an object as a small map.",
        "language": "typescript",
    },
    "ts_maps_sets": {
        "name": "Map & Set",
        "what": "Real hash structures: Map for key→value, Set for unique membership.",
        "deep": "`Map<K, V>` stores key→value pairs with any key type and preserves insertion order (`.set`, `.get`, `.has`, `.size`). `Set<T>` stores unique values (`.add`, `.has`). Both beat plain objects when keys aren't strings or order/size matters.",
        "java": "`Map`/`Set` mirror `HashMap`/`HashSet` (well, `LinkedHashMap` — order is kept). Iterate a Map with `for (const [k, v] of map)`. Use `map.get(k) ?? 0` for the getOrDefault pattern when counting.",
        "language": "typescript",
    },
    "ts_enums": {
        "name": "Enums & Literal Unions",
        "what": "Fixed sets of named constants — via enum, or the more common literal-union pattern.",
        "deep": "An `enum Dir { N, S, E, W }` names a fixed set of options. In modern TypeScript the lighter-weight pattern is a literal union `type Dir = \"N\" | \"S\" | \"E\" | \"W\"` plus plain string values — no runtime cost and easier to serialize.",
        "java": "`enum` looks like Java's, but many codebases prefer the union-of-string-literals form instead. (Note: bare `enum` needs a compile step; the string-union pattern is what runs in a type-stripping runtime, so the drills use that.)",
        "language": "typescript",
    },
    # -- Composition & reuse ------------------------------------------------
    "ts_generics": {
        "name": "Generics (Basics)",
        "what": "Type variables that let one function or type work for many element types safely.",
        "deep": "A generic `<T>` is a placeholder type filled in per call: `function first<T>(a: T[]): T` returns the array's element type, whatever it is. A constraint `<T extends { length: number }>` limits what T can be while keeping the link.",
        "java": "`<T>` works exactly like Java generics — `function id<T>(x: T): T`. Constraints use `extends` (`<T extends number>`). At runtime the type is erased (as in Java), so generics are a compile-time guarantee only.",
        "language": "typescript",
    },
    "ts_classes": {
        "name": "Classes",
        "what": "Blueprints with fields, a constructor, methods, access modifiers, and inheritance.",
        "deep": "A `class` bundles data (fields) with behavior (methods). The `constructor` initializes fields; `public`/`private`/`readonly` control access; `extends` inherits and `super(...)` calls the parent. Create instances with `new`.",
        "java": "Very close to Java: `class`, `extends`, `super`, `new`. Declare each field and assign it in the constructor (the shorthand `constructor(public x)` needs a compile step, so spell fields out). Methods drop the `public` keyword by default.",
        "language": "typescript",
    },
    "ts_this_accessors": {
        "name": "this, Getters & Setters",
        "what": "Referring to the current instance and exposing computed properties via get/set.",
        "deep": "Inside a method `this` is the current instance. A getter `get area()` looks like a field to callers but runs code; a setter `set width(v)` intercepts assignment. Arrow-function methods capture the surrounding `this`, avoiding a classic pitfall.",
        "java": "`this` matches Java. Getters/setters use the `get`/`set` keywords and are accessed *without* parentheses — `rect.area`, not `rect.area()`. Beware: a plain method passed as a callback can lose its `this`; an arrow field keeps it.",
        "language": "typescript",
    },
    "ts_modules": {
        "name": "Modules (import / export)",
        "what": "Splitting code across files with export (publish) and import (consume).",
        "deep": "Each file is a module. `export` publishes a function/type/value; another file pulls it in with `import { thing } from \"./file\"`. There are named exports (`export function f`) and one `export default` per file. Imports are how real projects stay organized.",
        "java": "`import { X } from \"./util\"` is like Java's `import`, but you choose exactly what to expose with `export` (no `public` per file — nothing is visible unless exported). `export default` is the single 'main' export of a file.",
        "language": "typescript",
    },
    # -- Robustness ---------------------------------------------------------
    "ts_nullish": {
        "name": "null, undefined & Strict Checks",
        "what": "Handling missing values safely with strictNullChecks, ??, and ?..",
        "deep": "`undefined` means 'no value assigned'; `null` means 'intentionally empty'. Under strict checks a `string | undefined` must be handled before use. `x ?? fallback` supplies a default; `obj?.field` reads safely; a guard `if (x != null)` narrows away the empty case.",
        "java": "This is TypeScript's answer to the NullPointerException: the type system forces you to deal with maybe-missing values. `x ?? d` = default-if-nullish, `x?.y` = safe access. `x != null` rules out BOTH null and undefined at once.",
        "language": "typescript",
    },
    "ts_errors": {
        "name": "Error Handling",
        "what": "Signaling and recovering from failures with throw, try/catch/finally.",
        "deep": "`throw new Error(\"message\")` signals a failure. A `try { … } catch (e) { … }` block runs the risky code and handles the error; `finally` always runs. Because anything can be thrown, the caught value is `unknown` — narrow it before reading `.message`.",
        "java": "`throw`/`try`/`catch`/`finally` mirror Java, but there are no checked exceptions and no `throws` clause. The catch binding is untyped (`unknown`) — use `e instanceof Error` before touching `e.message`.",
        "language": "typescript",
    },
    "ts_utility_types": {
        "name": "Utility Types",
        "what": "Built-in type transformers: Partial, Readonly, Pick, Record.",
        "deep": "Utility types reshape existing types so you don't repeat yourself: `Partial<T>` makes every field optional, `Readonly<T>` makes them read-only, `Pick<T, K>` selects some fields, and `Record<K, V>` builds an object type from keys to a value type.",
        "java": "There is no Java analogue — these are compile-time functions over types. `Record<string, number>` types a string-keyed map; `Partial<User>` is a User where every field may be absent (great for update payloads).",
        "language": "typescript",
    },
    "ts_async": {
        "name": "Promises & async/await",
        "what": "Working with values that arrive later using Promise, async and await.",
        "deep": "A `Promise<T>` is a value that will exist later. An `async` function always returns a Promise; inside it `await p` pauses until the promise resolves and hands you the value. This makes asynchronous code read top-to-bottom like ordinary code.",
        "java": "A `Promise<T>` is like a `CompletableFuture<T>`. `await` unwraps it without callbacks — the function suspends, not the thread. Mark a function `async` to use `await` inside it; the function's result is itself a Promise.",
        "language": "typescript",
    },
    # -- Foundational gaps (added after review) -----------------------------
    "ts_destructuring": {
        "name": "Destructuring, Spread & Rest",
        "what": "Pulling values out of arrays/objects by shape, and copying/merging them with the ... operator.",
        "deep": "Destructuring unpacks a structure in one line: `const [a, b] = arr` or `const { name } = user`. The spread `...` copies an array/object into a new one (`[...a, ...b]`, `{ ...user, age: 40 }`), and rest `...` gathers leftovers (`const [first, ...rest] = arr`). This syntax appears in almost every real TypeScript file.",
        "java": "There is no Java analogue — one line replaces a pile of `arr[0]`/`getX()` calls. Spread is the idiomatic immutable copy/merge (like `List.copyOf` + edits), and rest gathers the remaining elements into a new array.",
        "language": "typescript",
    },
    "ts_assertions": {
        "name": "Type Assertions (as)",
        "what": "Telling the compiler a value's type when you know more than it does — value as Type.",
        "deep": "When you know a value's type better than TypeScript can infer (a `JSON.parse` result, a value from a union, a DOM lookup), `value as Type` asserts it. It is a compile-time claim only — it does NOT convert or check anything at runtime, so a wrong assertion becomes a bug. Related: `expr!` asserts non-null, and `as const` freezes a literal's type.",
        "java": "`x as Foo` looks like a Java cast but does NOT check at runtime (no ClassCastException) — it is a pure compile-time promise, so use it sparingly and only when you are certain. `expr!` is 'trust me, not null'.",
        "language": "typescript",
    },
    "ts_compose": {
        "name": "Extending & Combining Types",
        "what": "Building bigger shapes from smaller ones with interface extends and intersection (&).",
        "deep": "Reuse shapes instead of repeating fields: `interface B extends A` adds fields to `A`, and `type C = A & B` (an intersection) requires everything from both. This is how you compose small, focused types into the exact shape a function needs — the type-level equivalent of building with blocks.",
        "java": "`interface B extends A` matches Java. The intersection `A & B` has no direct Java equivalent — it means 'has all members of A AND B at once', the way implementing two interfaces does, but as a plain type you can name and pass around.",
        "language": "typescript",
    },
    "ts_json": {
        "name": "JSON: parse & stringify",
        "what": "Converting between JSON text and live objects with JSON.parse and JSON.stringify.",
        "deep": "`JSON.parse(text)` turns a JSON string into a live value; `JSON.stringify(value)` turns a value back into a JSON string. This is how programs read config, talk to APIs, and save state. Because `JSON.parse` returns `any`, you typically assert or validate the shape before trusting it.",
        "java": "This is built in — no Jackson/Gson needed. `JSON.stringify(obj)` serializes in field-insertion order with no spaces; `JSON.parse` gives you a plain object typed `any`, so pair it with a type assertion or a runtime check.",
        "language": "typescript",
    },
    "ts_immutability": {
        "name": "readonly & Immutability",
        "what": "Preventing change: readonly fields, as const, Object.freeze, and immutable updates via spread.",
        "deep": "Immutability means never mutating existing data — you build a new value instead. `readonly` fields and `readonly T[]` forbid reassignment at compile time; `Object.freeze(obj)` enforces it at runtime; and the everyday pattern is an immutable update with spread: `{ ...user, age: 40 }` leaves the original untouched. Immutable data is easier to reason about and avoids a whole class of bugs.",
        "java": "`readonly` is like `final` on a field, but also applies to arrays (`readonly number[]`). `const` fixes the binding; `readonly`/`Object.freeze` fix the contents — two different guarantees. Spreading to a new object is the idiomatic 'copy with changes'.",
        "language": "typescript",
    },
}
CONCEPTS.update(TS_CONCEPTS)

CATEGORY.update({
    "ts_variables": "TS: Language Basics", "ts_types": "TS: Language Basics",
    "ts_inference": "TS: Language Basics", "ts_strings": "TS: Language Basics",
    "ts_operators": "TS: Language Basics", "ts_conditionals": "TS: Language Basics",
    "ts_loops": "TS: Language Basics",
    "ts_functions": "TS: Functions & Types", "ts_params": "TS: Functions & Types",
    "ts_unions": "TS: Functions & Types", "ts_aliases": "TS: Functions & Types",
    "ts_narrowing": "TS: Functions & Types",
    "ts_arrays": "TS: Data Structures", "ts_array_methods": "TS: Data Structures",
    "ts_objects": "TS: Data Structures", "ts_maps_sets": "TS: Data Structures",
    "ts_enums": "TS: Data Structures",
    "ts_generics": "TS: Composition & Reuse", "ts_classes": "TS: Composition & Reuse",
    "ts_this_accessors": "TS: Composition & Reuse", "ts_modules": "TS: Composition & Reuse",
    "ts_nullish": "TS: Robustness", "ts_errors": "TS: Robustness",
    "ts_utility_types": "TS: Robustness", "ts_async": "TS: Robustness",
    # foundational gaps added after review
    "ts_destructuring": "TS: Language Basics",
    "ts_assertions": "TS: Functions & Types",
    "ts_compose": "TS: Functions & Types",
    "ts_json": "TS: Data Structures",
    "ts_immutability": "TS: Robustness",
})


# ===========================================================================
# LESSONS  (deep, TypeScript-only Markdown teaching pages)
# ===========================================================================
TS_LESSONS = {
    "ts_variables": """### Worked example
Think of a variable as a labelled box. `const pi = 3.14` puts `3.14` in a box named `pi` and *locks the label* — you can never point `pi` at a different value. `let score = 0` makes a box you *can* refill: `score = score + 10`.

```ts
const name = "Ada";      // fixed binding — reassigning is a compile error
let score = 0;           // reassignable
score = score + 10;      // fine
console.log(name, score); // Ada 10
```

### Reach for const first
Default to `const`. It signals "this never changes", which makes code easier to read and catches accidental reassignment. Switch to `let` only when you genuinely need to update the variable (a running total, a loop counter).

### Block scope
A `const`/`let` exists only inside the nearest `{ }`:
```ts
if (true) {
  const secret = 42;
}
// console.log(secret);  // error: secret is not defined out here
```

### Watch out for
- `const` fixes the *binding*, not the contents: `const a = [1]; a.push(2);` is allowed — you changed the array, not which array `a` points to.
- Never use `var` — it ignores block scope and causes subtle bugs.
""",
    "ts_types": """### Worked example
Every value has a type. You can let TypeScript infer it, or write it after a colon:
```ts
let count: number = 5;      // whole numbers AND decimals are both `number`
let price: number = 9.99;
let title: string = "Poodcode";
let done: boolean = false;  // true / false
let nothing: null = null;
let missing: undefined = undefined;
```

### The primitives you meet first
| Type | Example | Notes |
|------|---------|-------|
| `number` | `42`, `3.5`, `-7` | one type for ints and floats |
| `string` | `"hi"`, `` `hi ${x}` `` | text; no separate `char` type |
| `boolean` | `true`, `false` | |
| `null` | `null` | intentionally empty |
| `undefined` | `undefined` | no value assigned yet |

### From input to number
Input arrives as text. Convert it explicitly:
```ts
const n: number = Number("42");   // 42, a real number
const s: string = String(42);     // "42"
```

### Watch out for
- `number` can't hold arbitrarily huge integers exactly (beyond ~9 quadrillion); that's what `bigint` is for later.
- `"5" + 1` is `"51"` (string concat) but `Number("5") + 1` is `6`. Convert before doing math.
""",
    "ts_inference": """### Worked example
You rarely need to write types — TypeScript infers them from the initializer:
```ts
const x = 3;          // inferred: number
const label = "hi";   // inferred: string
const flags = [true]; // inferred: boolean[]
```
Annotate only when there's no initializer, or to be intentionally stricter.

### any vs unknown
Both mean "type not known", but they behave oppositely:
```ts
let a: any = "hello";
a.foo.bar();          // compiles — checking is OFF. Dangerous.

let u: unknown = "hello";
// u.toUpperCase();   // error: must narrow first
if (typeof u === "string") {
  console.log(u.toUpperCase()); // OK here — narrowed to string
}
```

### Rule of thumb
- Prefer inference; write a type when it clarifies intent.
- Avoid `any` — it silently disables the safety you came for.
- When you truly don't know a type (parsing, catch blocks), use `unknown` and narrow with a runtime check.

### Watch out for
- An empty `const arr = []` infers `any[]`; give it a type — `const arr: number[] = []`.
""",
    "ts_strings": """### Worked example
Template literals (backticks) splice values into text — clearer than gluing with `+`:
```ts
const name = "Ada";
const age = 36;
console.log(`${name} is ${age}`);   // Ada is 36
console.log(name + " is " + age);   // same, but noisier
```

### Everyday string tools
```ts
const s = "Poodcode";
s.length;            // 8   (a property, not a call)
s.toUpperCase();     // "POODCODE"
s[0];                // "P"
s.slice(0, 4);       // "Pood"   (start, end-exclusive)
s.includes("code");  // true
s.indexOf("d");      // 3
"a,b,c".split(",");  // ["a","b","c"]
"  hi  ".trim();     // "hi"
```

### Strings are immutable
Methods return NEW strings; the original never changes:
```ts
let t = "hi";
t.toUpperCase();      // returns "HI" but discards it
console.log(t);       // still "hi"
t = t.toUpperCase();  // keep the result
```

### Watch out for
- `length` and `[i]` count UTF-16 units — fine for plain ASCII text.
- To reverse a string: `[...s].reverse().join("")`.
""",
    "ts_operators": """### Worked example
```ts
7 + 2;      // 9
7 % 2;      // 1   (remainder — 7 is odd)
7 / 2;      // 3.5 (real division, no truncation)
Math.floor(7 / 2); // 3

3 === 3;    // true   (strict equality — ALWAYS use ===)
3 !== 4;    // true
2 < 5 && 5 < 9; // true (logical and)
```

### The two safety operators
```ts
// ?? — fallback only when the left side is null OR undefined
const port = input ?? 8080;     // 0 and "" are kept; only null/undefined trigger the default

// ?. — read a property only if the object exists
const city = user?.address?.city;  // undefined instead of a crash
```

### === vs ==
Always use `===` / `!==`. The loose `==` coerces types with surprising results (`0 == ""` is `true`). Strict equality has no surprises.

### Watch out for
- `??` differs from `||`: `0 || 5` is `5`, but `0 ?? 5` is `0`. Use `??` when 0 / "" / false are valid values.
- `%` can be negative for negative inputs: `-7 % 3` is `-1`.
""",
    "ts_conditionals": """### Worked example
```ts
const n = 7;
if (n % 2 === 0) {
  console.log("Even");
} else {
  console.log("Odd");        // prints Odd
}
```

### Truthiness
`if` accepts any value, not just booleans. These are **falsy**: `false`, `0`, `""` (empty string), `null`, `undefined`, `NaN`. Everything else is **truthy**.
```ts
if (name) { /* runs when name is a non-empty string */ }
if (list.length) { /* runs when the array is non-empty */ }
```

### switch
Compare one value against many, with `===`. Don't forget `break`:
```ts
switch (grade) {
  case "A": console.log("Excellent"); break;
  case "B": console.log("Good"); break;
  default:  console.log("Keep going");
}
```

### Ternary — a conditional expression
```ts
const label = n % 2 === 0 ? "Even" : "Odd";
```

### Watch out for
- A missing `break` "falls through" to the next case — occasionally useful, usually a bug.
- `if (x = 5)` (assignment) vs `if (x === 5)` (comparison) — use `===`.
""",
    "ts_loops": """### Worked example
Sum an array three equivalent ways:
```ts
const nums = [10, 20, 30];

let a = 0;
for (let i = 0; i < nums.length; i++) a += nums[i];  // index loop

let b = 0;
for (const x of nums) b += x;                         // for…of: values

console.log(a, b);  // 60 60
```

### Which loop when
| Loop | Gives you | Use for |
|------|-----------|---------|
| `for (let i…)` | an index `i` | index math, counting |
| `for…of` | each **value** | arrays, strings, Sets |
| `for…in` | each **key** | object properties |
| `while` | — | repeat until a condition fails |

### break & continue
```ts
for (const x of nums) {
  if (x < 0) continue;   // skip negatives
  if (x > 100) break;    // stop entirely
  console.log(x);
}
```

### Watch out for
- **Never** use `for…in` on an array — it iterates string keys ("0","1",…), not elements. Use `for…of`.
- Off-by-one: `i < n` visits indexes 0..n-1; `i <= n` overruns.
""",
    "ts_functions": """### Worked example
```ts
// declaration — hoisted, named
function add(a: number, b: number): number {
  return a + b;
}

// arrow function — compact, great for callbacks
const double = (x: number): number => x * 2;

console.log(add(2, 3), double(10));  // 5 20
```

### Anatomy
- Parameters get types: `(a: number, b: number)`.
- The return type goes after the `)`: `: number`. It's usually inferred, so you can omit it.
- A function that returns nothing has return type `void`.

### Arrow function shorthands
```ts
const square = (x: number) => x * x;   // single expression: implicit return
const greet = (name: string): void => { console.log(`Hi ${name}`); };
```

### Functions are values
You can pass them around and store them — the foundation of array methods and callbacks:
```ts
const ops = [add, (a: number, b: number) => a - b];
console.log(ops[1](9, 4));  // 5
```

### Watch out for
- No implicit return with braces: `(x) => { x * 2 }` returns `undefined`; drop the braces or add `return`.
""",
    "ts_params": """### Worked example
```ts
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`;
}
greet("Ada");            // "Hello, Ada!"   (default used)
greet("Ada", "Hi");      // "Hi, Ada!"
```

### Three flavours
```ts
function f(required: number, optional?: number, withDefault = 10) { … }

function sum(...nums: number[]): number {     // rest: collects the rest into an array
  return nums.reduce((a, b) => a + b, 0);
}
sum(1, 2, 3, 4);  // 10
```

### Rules of order
Required parameters come first, then optional/defaulted ones, then a single rest parameter last:
```ts
function log(level: string, ...messages: string[]) { … }
```

### Optional means "maybe undefined"
```ts
function area(w: number, h?: number): number {
  return w * (h ?? w);   // square when h is omitted
}
```

### Watch out for
- You can't put a required parameter after an optional one.
- A default value makes the parameter optional automatically — don't add `?` too.
""",
    "ts_unions": """### Worked example
A union lets a value be one of several types:
```ts
function describe(x: string | number): string {
  if (typeof x === "number") return `number ${x}`;
  return `string of length ${x.length}`;
}
describe(42);      // "number 42"
describe("hi");    // "string of length 2"
```

### Literal types — an exact set of values
```ts
type Direction = "N" | "S" | "E" | "W";
function step(d: Direction): string {
  return d === "N" ? "up" : d === "S" ? "down" : "sideways";
}
```
Now `step("X")` is a compile error — only the four strings are allowed. This is the type-safe replacement for magic strings and (often) enums.

### Combining them
```ts
type Status = "loading" | "done" | number;  // strings OR a numeric code
```

### Watch out for
- Before calling a method that only one member has, you must **narrow** (see Type Narrowing) — TypeScript won't let you call `.length` on a `string | number` directly.
- Literal unions are compile-time only; at runtime they're just plain strings/numbers.
""",
    "ts_aliases": """### Worked example
```ts
type ID = string | number;          // name any type
interface Point { x: number; y: number; }   // describe an object shape

const p: Point = { x: 3, y: 4 };
function dist(a: Point): number {
  return Math.sqrt(a.x * a.x + a.y * a.y);
}
console.log(dist(p));  // 5
```

### interface vs type
- Use `interface` for object shapes — it's the convention and can be extended.
- Use `type` for unions, primitives, tuples, and aliases — things an interface can't name.
```ts
interface User { name: string; age: number; }
type Pair = [number, number];
type Nullable = string | null;
```

### Optional & readonly fields
```ts
interface Config {
  host: string;
  port?: number;       // may be omitted
  readonly id: string; // can't be reassigned after creation
}
```

### Structural typing
An object fits an interface if it *has the right shape* — no `implements` needed:
```ts
function print(pt: Point) { console.log(`${pt.x},${pt.y}`); }
print({ x: 1, y: 2 });   // fine — shape matches
```

### Watch out for
- Interfaces describe shape at compile time only; they vanish at runtime.
""",
    "ts_narrowing": """### Worked example
A union isn't usable until you prove which type it is *right now*:
```ts
function len(x: string | string[]): number {
  if (typeof x === "string") {
    return x.length;        // here x is a string
  }
  return x.length;          // here x is string[]
}
```

### The narrowing toolkit
| Check | Narrows to |
|-------|-----------|
| `typeof x === "number"` | primitive types |
| `Array.isArray(x)` | arrays |
| `"key" in obj` | objects that have that key |
| `if (x)` / `if (x != null)` | rules out falsy / null+undefined |
| `x === "N"` | a specific literal |

### Discriminated unions (a taste)
Give each shape a common tag, then switch on it:
```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  if (s.kind === "circle") return Math.PI * s.r * s.r;
  return s.side * s.side;
}
```

### Watch out for
- After narrowing inside an `if`, the refinement only holds *inside* that branch.
- `typeof null` is `"object"` — guard null with `x != null`, not `typeof`.
""",
    "ts_arrays": """### Worked example
```ts
const nums: number[] = [10, 20, 30];
nums.push(40);           // add to end -> [10,20,30,40]
nums[0];                 // 10
nums.length;             // 4
const last = nums.pop(); // remove & return end -> 40
```

### Making & reshaping
```ts
const zeros: number[] = new Array(3).fill(0);   // [0,0,0]
const copy = [...nums];                          // shallow copy (spread)
const joined = nums.join("-");                   // "10-20-30"
const part = nums.slice(1, 3);                   // [20,30] (end-exclusive)
```

### Tuples — fixed shape, per-position types
```ts
const point: [number, number] = [3, 4];
const entry: [string, number] = ["age", 36];
const [x, y] = point;   // destructuring -> x=3, y=4
```

### Watch out for
- Reading past the end gives `undefined`, not an error: `nums[99]` is `undefined`.
- `number[]` and `Array<number>` are the same type — pick one style.
- Arrays are reference values: `const b = a` shares the same array; copy with `[...a]`.
""",
    "ts_array_methods": """### Worked example
```ts
const nums = [1, 2, 3, 4, 5];

nums.map(x => x * x);            // [1,4,9,16,25]   transform each
nums.filter(x => x % 2 === 0);  // [2,4]            keep matches
nums.reduce((a, x) => a + x, 0);// 15               fold to one value
nums.find(x => x > 3);          // 4                first match (or undefined)
nums.some(x => x > 4);          // true
nums.every(x => x > 0);         // true
```

### Chaining
Each method returns a new value, so they compose:
```ts
const total = nums
  .filter(x => x % 2 === 1)   // [1,3,5]
  .map(x => x * 10)           // [10,30,50]
  .reduce((a, x) => a + x, 0);// 90
```

### reduce, demystified
`reduce(fn, start)` carries an accumulator: start with `start`, then for each element compute `fn(acc, element)`.
```ts
const max = nums.reduce((m, x) => (x > m ? x : m), nums[0]);  // 5
```

### Watch out for
- `sort()` sorts **as strings** by default: `[10,2,1].sort()` -> `[1,10,2]`. For numbers pass `(a, b) => a - b`.
- `sort` and `reverse` **mutate** the array in place; copy first (`[...a].sort(...)`) if you need the original.
- `map`/`filter` return new arrays; `forEach` returns nothing (use it only for side effects).
""",
    "ts_objects": """### Worked example
```ts
interface User { name: string; age: number; admin?: boolean; }

const u: User = { name: "Ada", age: 36 };
console.log(u.name);      // Ada
u.age = 37;               // update a field
console.log(u.admin);     // undefined (optional, absent)
```

### Access & iterate
```ts
u["name"];                    // bracket access
Object.keys(u);               // ["name","age"]
Object.values(u);             // ["Ada", 37]
for (const [k, v] of Object.entries(u)) {
  console.log(`${k}=${v}`);
}
```

### Index signatures — object as a bag of keys
```ts
const counts: { [word: string]: number } = {};
counts["hi"] = (counts["hi"] ?? 0) + 1;
```

### Copy & merge with spread
```ts
const patched = { ...u, age: 40 };   // new object, age overridden
```

### Watch out for
- Objects are references: `const b = a` shares the same object; spread `{...a}` for a shallow copy.
- Reading a missing key gives `undefined` — combine with `??` to supply a default.
""",
    "ts_maps_sets": """### Worked example
```ts
const ages = new Map<string, number>();
ages.set("Ada", 36);
ages.set("Bob", 40);
ages.get("Ada");     // 36
ages.has("Cid");     // false
ages.size;           // 2

for (const [name, age] of ages) {
  console.log(`${name}:${age}`);
}
```

### Set — unique values
```ts
const seen = new Set<number>();
seen.add(1); seen.add(1); seen.add(2);
seen.has(1);         // true
seen.size;           // 2
const unique = [...new Set([3, 3, 1, 3])];  // [3,1]
```

### Counting pattern (very common)
```ts
const freq = new Map<string, number>();
for (const w of words) {
  freq.set(w, (freq.get(w) ?? 0) + 1);
}
```

### Map vs plain object
Prefer `Map` when: keys aren't strings, you add/remove a lot, or you need `.size` and reliable iteration order. Prefer a plain object for fixed, string-keyed records.

### Watch out for
- `map.get(k)` returns `V | undefined` — handle the miss (often with `?? 0`).
- A `Set` uses `===` for equality, so two different objects with the same fields count as distinct.
""",
    "ts_enums": """### Worked example — the pattern that runs everywhere
The modern, lightweight way to model a fixed set is a **literal union** plus plain values:
```ts
type Direction = "N" | "E" | "S" | "W";

function turnRight(d: Direction): Direction {
  const order: Direction[] = ["N", "E", "S", "W"];
  return order[(order.indexOf(d) + 1) % 4];
}
console.log(turnRight("N"));  // E
```
No runtime object is created, the values serialize as themselves, and invalid strings are compile errors.

### The classic enum
TypeScript also has a dedicated `enum`:
```ts
enum Direction { N, E, S, W }   // N=0, E=1, S=2, W=3
enum Color { Red = "RED", Green = "GREEN" }
```
It creates a real runtime object mapping names to values. It's fine, but many teams prefer the union pattern because it's simpler and lighter.

> Note: a bare `enum` needs a compile/transform step, so it won't run in a pure type-stripping runtime. The drills below use the string-union pattern, which runs everywhere.

### const objects as enums
```ts
const Status = { Loading: "loading", Done: "done" } as const;
type Status = typeof Status[keyof typeof Status];   // "loading" | "done"
```

### Watch out for
- Prefer the union pattern unless you specifically need reverse mappings.
""",
    "ts_generics": """### Worked example
A generic keeps the *link* between input and output types:
```ts
function first<T>(arr: T[]): T {
  return arr[0];
}
first([1, 2, 3]);        // T = number  -> 1
first(["a", "b"]);       // T = string  -> "a"
```
The `<T>` is a type variable filled in per call — so `first` works for any element type without losing type safety.

### Constraints — limit T while keeping the link
```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
longest([1, 2, 3], [1]);      // arrays have .length -> ok
longest("hello", "hi");       // strings too
```

### Generic pairs and containers
```ts
function pair<A, B>(a: A, b: B): [A, B] {
  return [a, b];
}
const p = pair("age", 36);   // [string, number]
```

### Watch out for
- Types are erased at runtime — a generic can't inspect `T` (no `new T()`, no `T === number`).
- Don't over-constrain: only add `extends` when you actually use the capability.
""",
    "ts_classes": """### Worked example
```ts
class Counter {
  private count: number;         // declare the field
  constructor(start: number) {
    this.count = start;          // assign it
  }
  increment(): void { this.count++; }
  get value(): number { return this.count; }
}

const c = new Counter(10);
c.increment();
console.log(c.value);   // 11
```

### Access modifiers
- `public` (default): visible everywhere.
- `private`: only inside the class.
- `readonly`: assignable once (in the constructor), then fixed.

### Inheritance
```ts
class Animal {
  name: string;
  constructor(name: string) { this.name = name; }
  speak(): string { return `${this.name} makes a sound`; }
}
class Dog extends Animal {
  speak(): string { return `${this.name} barks`; }   // override
}
console.log(new Dog("Rex").speak());  // Rex barks
```
Call the parent constructor with `super(...)`, and a parent method with `super.method()`.

> Note: the shorthand `constructor(public count: number)` needs a compile step, so these drills declare fields explicitly and assign them in the constructor — the form that runs in a type-stripping runtime.

### Watch out for
- You must call `super(...)` before using `this` in a subclass constructor.
""",
    "ts_this_accessors": """### Worked example
```ts
class Rect {
  width: number;
  height: number;
  constructor(w: number, h: number) {
    this.width = w;
    this.height = h;
  }
  get area(): number {          // getter — accessed WITHOUT ()
    return this.width * this.height;
  }
  set square(side: number) {    // setter — runs on assignment
    this.width = side;
    this.height = side;
  }
}

const r = new Rect(3, 4);
console.log(r.area);   // 12   (no parentheses!)
r.square = 5;
console.log(r.area);   // 25
```

### this
Inside a method, `this` is the instance the method was called on. It's how methods read and update their own fields.

### The lost-this pitfall
Passing a method as a callback can detach it from its object:
```ts
class Greeter {
  name = "Ada";
  hi = () => `Hi ${this.name}`;   // arrow field captures `this` — safe
}
```
An **arrow-function field** captures the surrounding `this`, so it keeps working as a callback.

### Watch out for
- Getters/setters are used like properties (`r.area`), not called like methods (`r.area()`).
""",
    "ts_modules": """### Worked example
Real projects split code across files. One file **exports**; another **imports**.
```ts
// math.ts
export function add(a: number, b: number): number { return a + b; }
export const PI = 3.14159;

// main.ts
import { add, PI } from "./math";
console.log(add(2, 3), PI);   // 5 3.14159
```

### Named vs default exports
```ts
// util.ts
export function helper() { … }        // named — import { helper }
export default function main() { … }  // one default per file

// consumer.ts
import main, { helper } from "./util";   // default first, then named in braces
```

### Rename & namespace imports
```ts
import { add as plus } from "./math";
import * as math from "./math";
math.add(1, 2);
```

### Why it matters
Nothing in a file is visible to other files unless you `export` it — modules give you explicit, per-symbol encapsulation. This is how large codebases stay organized and avoid name clashes.

### Watch out for
- Import paths to your own files start with `./` or `../`; bare names (`"fs"`) mean packages.
- A file with no `import`/`export` is treated as a plain script, not a module.
""",
    "ts_nullish": """### Worked example
```ts
function greet(name: string | undefined): string {
  return `Hi ${name ?? "friend"}`;   // fallback when missing
}
greet("Ada");        // "Hi Ada"
greet(undefined);    // "Hi friend"
```

### undefined vs null
- `undefined`: no value has been assigned yet (missing property, unset variable).
- `null`: an intentional "empty" you set on purpose.
Both are ruled out at once by `x != null` (note: loose `!=` here is the idiomatic exception).

### The three safety tools
```ts
const port = config.port ?? 8080;   // ?? default when null/undefined
const city = user?.address?.city;   // ?. safe read, short-circuits to undefined
if (value != null) {                // guard narrows to the non-empty type
  value.toFixed(2);
}
```

### Strict null checks
With strict checks on (the default here), a `string | undefined` *cannot* be used as a `string` until you handle the `undefined` case — the compiler forces the safety that prevents "cannot read property of undefined" crashes.

### Watch out for
- `??` vs `||`: use `??` when `0`, `""`, or `false` are valid values you want to keep.
- `obj?.method()` skips the call entirely when `obj` is nullish (returns `undefined`).
""",
    "ts_errors": """### Worked example
```ts
function parsePositive(s: string): number {
  const n = Number(s);
  if (Number.isNaN(n)) throw new Error("not a number");
  if (n <= 0) throw new Error("must be positive");
  return n;
}

try {
  console.log(parsePositive("abc"));
} catch (e) {
  console.log("failed:", e instanceof Error ? e.message : "unknown");
}
// failed: not a number
```

### try / catch / finally
```ts
try {
  risky();
} catch (e) {
  // handle the failure
} finally {
  // ALWAYS runs — cleanup goes here
}
```

### The catch value is unknown
You can throw anything, so `e` is typed `unknown`. Narrow before reading it:
```ts
catch (e) {
  if (e instanceof Error) console.log(e.message);
  else console.log(String(e));
}
```

### Throwing well
`throw new Error("clear message")` — prefer `Error` (or a subclass) over throwing bare strings, so callers get a `.message` and a stack trace.

### Watch out for
- `finally` runs even if you `return` or `throw` inside `try`.
- Don't swallow errors silently — at least log them.
""",
    "ts_utility_types": """### Worked example
Utility types transform an existing type so you don't repeat its fields:
```ts
interface User {
  id: string;
  name: string;
  age: number;
}

type UserUpdate = Partial<User>;          // every field optional
type FrozenUser = Readonly<User>;         // every field read-only
type NameCard  = Pick<User, "name">;      // { name: string }
type ById      = Record<string, User>;    // { [id: string]: User }
```

### What each one does
| Utility | Effect |
|---------|--------|
| `Partial<T>` | all fields optional — great for update/patch payloads |
| `Required<T>` | all fields required (the inverse) |
| `Readonly<T>` | all fields read-only |
| `Pick<T, K>` | keep only fields `K` |
| `Omit<T, K>` | drop fields `K` |
| `Record<K, V>` | build an object type from keys `K` to values `V` |

### In practice
```ts
function update(user: User, patch: Partial<User>): User {
  return { ...user, ...patch };
}
update(u, { age: 41 });   // only the fields you pass are changed
```

### Watch out for
- These are **compile-time only** — at runtime the objects are ordinary objects; nothing enforces `Readonly` except the type checker.
- `Record<string, number>` is the idiomatic type for a string-keyed count map.
""",
    "ts_async": """### Worked example
```ts
function later(value: number): Promise<number> {
  return new Promise(resolve => setTimeout(() => resolve(value), 10));
}

async function main(): Promise<void> {
  const x = await later(21);   // pause until it resolves
  console.log(x * 2);          // 42
}
main();
```

### The shape of async code
- A `Promise<T>` is a value that will exist *later* (or fail).
- An `async` function always returns a `Promise`.
- `await p` inside an `async` function suspends until `p` resolves, then yields the value — so asynchronous code reads top-to-bottom.

### Sequential vs parallel
```ts
const a = await slow();   // wait...
const b = await slow();   // ...then wait again (sequential)

const [c, d] = await Promise.all([slow(), slow()]);  // both at once (parallel)
```

### Errors in async code
`await` throws on rejection, so use ordinary `try/catch`:
```ts
try {
  const data = await fetchThing();
} catch (e) {
  console.log("failed");
}
```

### Watch out for
- `await` only works inside an `async` function (or at the top level of a module).
- Forgetting `await` gives you the *Promise*, not the value — a very common bug.
""",
    "ts_destructuring": """### Worked example
Destructuring unpacks a structure in one line:
```ts
const [a, b] = [3, 4];          // a = 3, b = 4
const { name, age } = { name: "Ada", age: 36 };
console.log(a, b, name, age);   // 3 4 Ada 36
```

### Array vs object
```ts
const [first, second] = [10, 20];         // by position
const { x, y } = { x: 1, y: 2 };           // by key name
const { y: height } = { y: 99 };           // rename while unpacking -> height = 99
const [head, ...tail] = [1, 2, 3, 4];      // head = 1, tail = [2, 3, 4]
```

### Spread — copy and merge
The `...` operator expands a structure into a new one:
```ts
const a = [1, 2];
const b = [3, 4];
const both = [...a, ...b];                 // [1, 2, 3, 4]

const user = { name: "Ada", age: 36 };
const older = { ...user, age: 37 };        // new object; user is untouched
```

### Defaults while destructuring
```ts
const { port = 8080 } = config;            // 8080 when port is missing
const [p = 0, q = 0] = [5];                // p = 5, q = 0
```

### Watch out for
- Spread makes a **shallow** copy — nested objects are still shared.
- `{ ...a, ...b }` lets later keys win, which is exactly how you 'patch' an object.
""",
    "ts_assertions": """### Worked example
Sometimes you know a value's type better than TypeScript can. `as` tells it so:
```ts
const raw: unknown = JSON.parse('{"count":5}');
const data = raw as { count: number };
console.log(data.count);   // 5
```

### It is a compile-time claim only
An assertion does **not** convert or check anything at runtime — it just silences the type checker. If you assert wrongly, you get a runtime bug with no cast error:
```ts
const n = "hello" as unknown as number;   // compiles, but n is really a string
```
So reach for `as` only when you are genuinely certain, and prefer narrowing (`typeof`, `in`) when you can check instead.

### The non-null assertion `!`
```ts
const el = list.find(x => x > 10)!;   // 'I promise this isn't undefined'
```
Use it only when you truly know the value exists — otherwise a real `undefined` slips through.

### `as const`
```ts
const dir = "N" as const;   // type is the literal "N", not string
```

### Watch out for
- `x as Foo` is not a Java cast — there is no runtime check, so a wrong assertion fails silently later.
- Prefer a real runtime check (narrowing) over an assertion whenever one is possible.
""",
    "ts_compose": """### Worked example
Build bigger shapes out of smaller ones instead of repeating fields.
```ts
interface Named { name: string; }
interface Person extends Named {   // adds to Named
  age: number;
}
const p: Person = { name: "Ada", age: 36 };   // needs BOTH fields
```

### Intersection types (&)
`A & B` means 'has everything from A **and** B':
```ts
type Point = { x: number; y: number };
type Labeled = { label: string };
type LabeledPoint = Point & Labeled;

const lp: LabeledPoint = { x: 1, y: 2, label: "origin" };
```

### extends vs &
- `interface B extends A` — the interface way to add fields to a shape.
- `type C = A & B` — the `type` way; also works on unions and primitives.
Both produce a shape requiring all the combined members.

### Composing many small types
```ts
type Timestamps = { createdAt: number; updatedAt: number };
type User = { id: string; name: string } & Timestamps;
```
Small, focused pieces snap together into exactly the shape a function needs.

### Watch out for
- Intersection requires **all** members at once — `Point & Labeled` needs `x`, `y`, *and* `label`.
- Don't confuse `&` (must satisfy both) with `|` (a union — may be either).
""",
    "ts_json": """### Worked example
```ts
const text = '{"name":"Ada","age":36}';
const user = JSON.parse(text);        // live object
console.log(user.name);               // Ada

const back = JSON.stringify(user);    // '{"name":"Ada","age":36}'
console.log(back);
```

### The two directions
| Call | In | Out |
|------|----|-----|
| `JSON.parse(text)` | JSON string | a live value (`any`) |
| `JSON.stringify(value)` | any value | a JSON string |

### Typing the parsed result
`JSON.parse` returns `any`, so it is a prime spot for an assertion (or a runtime check):
```ts
const data = JSON.parse(text) as { name: string; age: number };
```

### Round-trip: read, change, write
```ts
const user = JSON.parse(text) as { name: string; age: number };
user.age = user.age + 1;
console.log(JSON.stringify(user));    // '{"name":"Ada","age":37}'
```

### Watch out for
- `JSON.stringify` outputs fields in insertion order with no spaces: `{"a":1,"b":2}`.
- Only JSON-safe data survives: functions, `undefined`, and `Map`/`Set` are dropped or need custom handling.
- `JSON.parse` throws on malformed text — wrap it in `try/catch` for untrusted input.
""",
    "ts_immutability": """### Worked example
Immutability means you never change existing data — you build a new value instead.
```ts
const user = { name: "Ada", age: 36 };
const older = { ...user, age: 37 };   // new object
console.log(user.age, older.age);     // 36 37  (original untouched)
```

### readonly — compile-time protection
```ts
interface Config {
  readonly id: string;        // cannot be reassigned after creation
}
const nums: readonly number[] = [1, 2, 3];
// nums.push(4);              // error: push doesn't exist on a readonly array
```

### const vs readonly
- `const` fixes the **binding** — you can't point the name at a new value, but you can still mutate the contents.
- `readonly` / `Object.freeze` fix the **contents**.
```ts
const arr = [1, 2];
arr.push(3);        // allowed! const only locks the binding
```

### Object.freeze — runtime protection
```ts
const config = Object.freeze({ limit: 10 });
// config.limit = 20;   // throws in strict mode; silently ignored otherwise
```

### Immutable update patterns
```ts
const next = [...arr, 99];               // append without mutating
const patched = { ...obj, done: true };  // change one field, keep the rest
```

### Watch out for
- `const` alone does **not** make an object immutable — its fields can still change.
- `Object.freeze` is shallow: nested objects remain mutable.
""",
}
LESSONS.update(TS_LESSONS)


# ===========================================================================
# EXERCISES  (fill-in-the-blank drills + full-length problems)
# Programs use raw strings so /\s+/ regexes and real newlines both survive.
# ===========================================================================
TS_EXERCISES = {
    # -- ts_variables -------------------------------------------------------
    "ts_variables": [
        tsx(
            "ts_variables-const", "Declare a constant",
            "The input holds one number. Replace `____` to declare a `const` named `n` holding that number so the program can print it.",
            _P(r'''
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n: number = Number(input);
console.log(n);
'''),
            [r'const n: number = Number(input);'],
            [("42", "42"), ("7", "7"), ("-3", "-3")],
            hint="Number(input) turns the text into a real number; store it with const n = ... .",
        ),
        tsx(
            "ts_variables-let", "Reassign a running total",
            "`total` starts at `n` and must be bumped by 10. Replace `____` to declare `total` with `let` (a `const` could not be reassigned on the next line).",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
let total = n;
total = total + 10;
console.log(total);
'''),
            [r'let total = n;'],
            [("5", "15"), ("0", "10"), ("-4", "6")],
            hint="Only let allows the reassignment `total = total + 10` on the next line.",
        ),
        tsx(
            "ts_variables-swap", "Swap two numbers",
            "Two numbers `a` and `b` are read for you. Write the whole solution: swap them using a temporary variable and print them in swapped order, space-separated (`3 4` -> `4 3`).",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let first = a;
let second = b;
const tmp = first;
first = second;
second = tmp;
console.log(first + " " + second);
'''),
            [r'''let first = a;
let second = b;
const tmp = first;
first = second;
second = tmp;
console.log(first + " " + second);'''],
            [("3 4", "4 3"), ("1 2", "2 1"), ("9 9", "9 9")],
            hint="Save one value in a tmp box before overwriting it, or you lose it.",
        ),
    ],
    # -- ts_types -----------------------------------------------------------
    "ts_types": [
        tsx(
            "ts_types-bool", "Store a yes/no",
            "Replace `____` so `isPositive` is a `boolean` that is `true` exactly when `n` is greater than 0.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const isPositive: boolean = n > 0;
console.log(isPositive);
'''),
            [r'const isPositive: boolean = n > 0;'],
            [("5", "true"), ("-2", "false"), ("0", "false")],
            hint="A comparison like n > 0 already produces a boolean.",
        ),
        tsx(
            "ts_types-convert", "Text to number",
            "The input arrives as text in `raw`. Replace `____` to convert it to a `number` named `value`, so `value + 1` does math (not string concatenation).",
            _P(r'''
import * as fs from "fs";
const raw: string = fs.readFileSync(0, "utf8").trim();
const value: number = Number(raw);
console.log(value + 1);
'''),
            [r'const value: number = Number(raw);'],
            [("41", "42"), ("0", "1"), ("-1", "0")],
            hint='Without Number(), "41" + 1 would be "411". Convert first.',
        ),
        tsx(
            "ts_types-rect", "Rectangle area",
            "Width and height are read into `w` and `h`. Write the solution: compute the area (a `number`) and print it.",
            _P(r'''
import * as fs from "fs";
const [w, h] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const area: number = w * h;
console.log(area);
'''),
            [r'''const area: number = w * h;
console.log(area);'''],
            [("3 4", "12"), ("5 5", "25"), ("7 2", "14")],
            hint="Area is width times height.",
        ),
    ],
    # -- ts_inference -------------------------------------------------------
    "ts_inference": [
        tsx(
            "ts_inference-sum", "Let TypeScript infer",
            "No type annotations needed here — TypeScript infers `number` from the values. Replace `____` to declare `total` as the sum of `a` and `b`.",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const total = a + b;
console.log(total);
'''),
            [r'const total = a + b;'],
            [("3 4", "7"), ("10 -2", "8"), ("0 0", "0")],
            hint="const total = a + b;  — its type is inferred as number.",
        ),
        tsx(
            "ts_inference-unknown", "Narrow an unknown",
            "`raw` is typed `unknown`, so you must prove it is a string before calling `.toUpperCase()`. Replace `____` with the check that narrows it to a string.",
            _P(r'''
import * as fs from "fs";
const raw: unknown = fs.readFileSync(0, "utf8").trim();
let out = "";
if (typeof raw === "string") {
  out = raw.toUpperCase();
}
console.log(out);
'''),
            [r'typeof raw === "string"'],
            [("hello", "HELLO"), ("Poodcode", "POODCODE"), ("abc", "ABC")],
            hint='typeof raw === "string" tells TypeScript (and you) it is safe to call string methods.',
        ),
        tsx(
            "ts_inference-larger", "Return the larger",
            "Two numbers are read. Write the solution: store the larger of `a` and `b` in a variable (let inference give it a type) and print it.",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const larger = a > b ? a : b;
console.log(larger);
'''),
            [r'''const larger = a > b ? a : b;
console.log(larger);'''],
            [("3 4", "4"), ("9 2", "9"), ("5 5", "5")],
            hint="A ternary a > b ? a : b picks the larger value.",
        ),
    ],
    # -- ts_strings ---------------------------------------------------------
    "ts_strings": [
        tsx(
            "ts_strings-template", "Greet with a template",
            "Replace `____` with a template literal that produces `Hi, <name>!` — for input `Ada`, print `Hi, Ada!`.",
            _P(r'''
import * as fs from "fs";
const name = fs.readFileSync(0, "utf8").trim();
console.log(`Hi, ${name}!`);
'''),
            [r'`Hi, ${name}!`'],
            [("Ada", "Hi, Ada!"), ("Bob", "Hi, Bob!"), ("Grace Hopper", "Hi, Grace Hopper!")],
            hint="Backticks let you embed ${name} straight into the text.",
        ),
        tsx(
            "ts_strings-upper", "Shout it",
            "Replace `____` to print the input line in upper case.",
            _P(r'''
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();
console.log(s.toUpperCase());
'''),
            [r's.toUpperCase()'],
            [("hello", "HELLO"), ("MixEd", "MIXED"), ("abc def", "ABC DEF")],
            hint="String methods are camelCase: s.toUpperCase().",
        ),
        tsx(
            "ts_strings-length", "How long?",
            "Replace `____` to print the number of characters in `s`. Remember: `length` is a property, not a method call.",
            _P(r'''
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();
console.log(s.length);
'''),
            [r's.length'],
            [("hello", "5"), ("a", "1"), ("Poodcode", "8")],
            hint="s.length (no parentheses) gives the character count.",
        ),
        tsx(
            "ts_strings-reverse", "Reverse a word",
            "Write the solution: reverse the input word and print it (`hello` -> `olleh`). Strings are immutable, so build a new one.",
            _P(r'''
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();
const reversed = [...s].reverse().join("");
console.log(reversed);
'''),
            [r'''const reversed = [...s].reverse().join("");
console.log(reversed);'''],
            [("hello", "olleh"), ("abc", "cba"), ("racecar", "racecar")],
            hint='Spread into an array of characters, reverse it, then .join("").',
        ),
    ],
    # -- ts_operators -------------------------------------------------------
    "ts_operators": [
        tsx(
            "ts_operators-mod", "Remainder",
            "Replace `____` to print the remainder of `n` divided by 2 (0 for even, 1 for odd).",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
console.log(n % 2);
'''),
            [r'n % 2'],
            [("7", "1"), ("10", "0"), ("3", "1")],
            hint="% is the remainder operator.",
        ),
        tsx(
            "ts_operators-nullish", "Default with ??",
            "`value` is `undefined` when the input is empty. Replace `____` so `port` falls back to `\"8080\"` only when `value` is null/undefined.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const value: string | undefined = raw === "" ? undefined : raw;
const port = value ?? "8080";
console.log(port);
'''),
            [r'value ?? "8080"'],
            [("3000", "3000"), ("", "8080"), ("80", "80")],
            hint="a ?? b gives b only when a is null or undefined.",
        ),
        tsx(
            "ts_operators-ternary", "Label the sign",
            "Replace `____` with a chained ternary that yields `pos` when `n > 0`, `neg` when `n < 0`, and `zero` otherwise.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const label = n > 0 ? "pos" : n < 0 ? "neg" : "zero";
console.log(label);
'''),
            [r'n > 0 ? "pos" : n < 0 ? "neg" : "zero"'],
            [("5", "pos"), ("-3", "neg"), ("0", "zero")],
            hint="cond1 ? a : cond2 ? b : c chains two decisions.",
        ),
    ],
    # -- ts_conditionals ----------------------------------------------------
    "ts_conditionals": [
        tsx(
            "ts_conditionals-evenodd", "Even or odd",
            "Replace `____` with the condition that is true when `n` is even.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
if (n % 2 === 0) {
  console.log("Even");
} else {
  console.log("Odd");
}
'''),
            [r'n % 2 === 0'],
            [("4", "Even"), ("7", "Odd"), ("0", "Even")],
            hint="A number is even when n % 2 === 0.",
        ),
        tsx(
            "ts_conditionals-truthy", "Non-empty?",
            "Replace `____` with a truthy test on `trimmed.length` so the program prints `yes` for non-empty input and `no` for blank input.",
            _P(r'''
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8");
const trimmed = s.trim();
if (trimmed.length) {
  console.log("yes");
} else {
  console.log("no");
}
'''),
            [r'trimmed.length'],
            [("hello", "yes"), ("", "no"), ("   ", "no")],
            hint="0 is falsy, so an empty string's length of 0 takes the else branch.",
        ),
        tsx(
            "ts_conditionals-switch", "Grade to word",
            "Replace `____` with the `switch` header that branches on `grade`.",
            _P(r'''
import * as fs from "fs";
const grade = fs.readFileSync(0, "utf8").trim();
switch (grade) {
  case "A":
    console.log("Excellent");
    break;
  case "B":
    console.log("Good");
    break;
  default:
    console.log("Keep going");
}
'''),
            [r'switch (grade) {'],
            [("A", "Excellent"), ("B", "Good"), ("C", "Keep going")],
            hint="switch (grade) { ... } compares grade against each case with ===.",
        ),
    ],
    # -- ts_loops -----------------------------------------------------------
    "ts_loops": [
        tsx(
            "ts_loops-sum", "Sum with for…of",
            "Replace `____` with a `for…of` loop header that walks each value of `nums` as `x`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let total = 0;
for (const x of nums) {
  total += x;
}
console.log(total);
'''),
            [r'for (const x of nums) {'],
            [("1 2 3", "6"), ("10 20", "30"), ("5", "5")],
            hint="for (const x of nums) gives you each element, not its index.",
        ),
        tsx(
            "ts_loops-count", "Count evens",
            "Replace `____` with the loop condition that keeps `i` a valid index of `nums`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let count = 0;
for (let i = 0; i < nums.length; i++) {
  if (nums[i] % 2 === 0) count++;
}
console.log(count);
'''),
            [r'i < nums.length'],
            [("1 2 3 4", "2"), ("2 4 6", "3"), ("1 3 5", "0")],
            hint="Valid indexes run 0 .. nums.length - 1, so the guard is i < nums.length.",
        ),
        tsx(
            "ts_loops-firstover", "First over threshold",
            "Line 1 is a threshold `t`; line 2 is a list of numbers. Write the solution: print the first number strictly greater than `t`, or `-1` if none. Use `break` to stop early.",
            _P(r'''
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split(/\r?\n/);
const t = Number(lines[0]);
const nums = lines[1].split(/\s+/).map(Number);
let answer = -1;
for (const x of nums) {
  if (x > t) {
    answer = x;
    break;
  }
}
console.log(answer);
'''),
            [r'''let answer = -1;
for (const x of nums) {
  if (x > t) {
    answer = x;
    break;
  }
}
console.log(answer);'''],
            [("5\n1 3 7 2", "7"), ("10\n1 2 3", "-1"), ("0\n-1 -2 5", "5")],
            hint="Default the answer to -1, then break as soon as you find one bigger than t.",
        ),
    ],
    # -- ts_functions -------------------------------------------------------
    "ts_functions": [
        tsx(
            "ts_functions-add", "Write add()",
            "Replace `____` with the body of `add` so it returns the sum of its two parameters.",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function add(x: number, y: number): number {
  return x + y;
}
console.log(add(a, b));
'''),
            [r'return x + y;'],
            [("2 3", "5"), ("10 -4", "6"), ("0 0", "0")],
            hint="return x + y;",
        ),
        tsx(
            "ts_functions-arrow", "Double it (arrow)",
            "Replace `____` with an arrow function that takes a `number` and returns it doubled.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const double = (x: number): number => x * 2;
console.log(double(n));
'''),
            [r'(x: number): number => x * 2'],
            [("5", "10"), ("0", "0"), ("-3", "-6")],
            hint="(x: number): number => x * 2 — a single expression, so no braces or return.",
        ),
        tsx(
            "ts_functions-callback", "Apply the chosen op",
            "The input is an operator (`+` or `*`) and two numbers. Write the solution: pick the matching function and apply it, printing the result.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const op = parts[0];
const a = Number(parts[1]);
const b = Number(parts[2]);
const add = (x: number, y: number): number => x + y;
const mul = (x: number, y: number): number => x * y;
const fn = op === "+" ? add : mul;
console.log(fn(a, b));
'''),
            [r'''const fn = op === "+" ? add : mul;
console.log(fn(a, b));'''],
            [("+ 3 4", "7"), ("* 3 4", "12"), ("+ 10 -2", "8")],
            hint="Functions are values — store the chosen one in fn, then call fn(a, b).",
        ),
    ],
    # -- ts_params ----------------------------------------------------------
    "ts_params": [
        tsx(
            "ts_params-default", "A default parameter",
            "Replace `____` to declare `greeting` with a default value of `\"Hello\"`, so calling `greet(name)` still works.",
            _P(r'''
import * as fs from "fs";
const name = fs.readFileSync(0, "utf8").trim();
function greet(name: string, greeting: string = "Hello"): string {
  return `${greeting}, ${name}!`;
}
console.log(greet(name));
'''),
            [r'greeting: string = "Hello"'],
            [("Ada", "Hello, Ada!"), ("Bob", "Hello, Bob!"), ("Cid", "Hello, Cid!")],
            hint='A default is written param: type = value, e.g. greeting: string = "Hello".',
        ),
        tsx(
            "ts_params-rest", "Sum any count",
            "Replace `____` to declare a rest parameter `xs` that collects all the numbers passed in.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function sum(...xs: number[]): number {
  return xs.reduce((a, b) => a + b, 0);
}
console.log(sum(...nums));
'''),
            [r'...xs: number[]'],
            [("1 2 3 4", "10"), ("5", "5"), ("10 20 30", "60")],
            hint="A rest parameter uses ... and collects arguments into an array: ...xs: number[].",
        ),
        tsx(
            "ts_params-optional", "Rectangle or square",
            "One or two numbers are given. Write the solution: an `area(w, h?)` function that squares `w` when `h` is omitted, then print the area for the given input.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function area(w: number, h?: number): number {
  return w * (h ?? w);
}
const result = parts.length === 2 ? area(parts[0], parts[1]) : area(parts[0]);
console.log(result);
'''),
            [r'''function area(w: number, h?: number): number {
  return w * (h ?? w);
}
const result = parts.length === 2 ? area(parts[0], parts[1]) : area(parts[0]);
console.log(result);'''],
            [("3 4", "12"), ("5", "25"), ("2 6", "12")],
            hint="Mark h optional with h?, then use h ?? w so a missing h becomes w (a square).",
        ),
    ],
    # -- ts_unions ----------------------------------------------------------
    "ts_unions": [
        tsx(
            "ts_unions-direction", "Direction to word",
            "`Direction` is a literal union of the four compass letters. Replace `____` with a chained ternary mapping `N/S/E/W` to `north/south/east/west`.",
            _P(r'''
import * as fs from "fs";
const d = fs.readFileSync(0, "utf8").trim();
type Direction = "N" | "S" | "E" | "W";
function toWord(dir: Direction): string {
  return dir === "N" ? "north" : dir === "S" ? "south" : dir === "E" ? "east" : "west";
}
console.log(toWord(d as Direction));
'''),
            [r'dir === "N" ? "north" : dir === "S" ? "south" : dir === "E" ? "east" : "west"'],
            [("N", "north"), ("W", "west"), ("S", "south")],
            hint="Chain ternaries: dir === \"N\" ? \"north\" : dir === \"S\" ? ... .",
        ),
        tsx(
            "ts_unions-strnum", "string | number",
            "`value` is built as a `string | number` (a number when the input starts with `n`). Replace `____` with the expression that builds it: `Number(parts[1])` for the `n` case, else the raw string.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const value: string | number = parts[0] === "n" ? Number(parts[1]) : parts[1];
let out: number;
if (typeof value === "number") {
  out = value;
} else {
  out = value.length;
}
console.log(out);
'''),
            [r'parts[0] === "n" ? Number(parts[1]) : parts[1]'],
            [("n 42", "42"), ("s hello", "5"), ("n -3", "-3")],
            hint="Pick the number for the n case, otherwise keep the string.",
        ),
        tsx(
            "ts_unions-status", "Status to message",
            "`Status` is `\"ok\" | \"notfound\" | number`. Write the solution: if it is a number print `code <n>`, if `ok` print `all good`, otherwise print `missing`.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
type Status = "ok" | "notfound" | number;
const status: Status = /^-?\d+$/.test(raw) ? Number(raw) : (raw as "ok" | "notfound");
let message: string;
if (typeof status === "number") {
  message = `code ${status}`;
} else if (status === "ok") {
  message = "all good";
} else {
  message = "missing";
}
console.log(message);
'''),
            [r'''if (typeof status === "number") {
  message = `code ${status}`;
} else if (status === "ok") {
  message = "all good";
} else {
  message = "missing";
}'''],
            [("ok", "all good"), ("notfound", "missing"), ("404", "code 404")],
            hint="Handle the number member first with typeof, then the two string literals.",
        ),
    ],
    # -- ts_aliases ---------------------------------------------------------
    "ts_aliases": [
        tsx(
            "ts_aliases-point", "Distance from origin",
            "`Point` is an interface with `x` and `y`. Replace `____` with the body of `dist` (Pythagoras from the origin).",
            _P(r'''
import * as fs from "fs";
const [x, y] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
interface Point { x: number; y: number; }
function dist(p: Point): number {
  return Math.sqrt(p.x * p.x + p.y * p.y);
}
console.log(dist({ x, y }));
'''),
            [r'return Math.sqrt(p.x * p.x + p.y * p.y);'],
            [("3 4", "5"), ("0 0", "0"), ("6 8", "10")],
            hint="Distance from the origin is sqrt(x*x + y*y).",
        ),
        tsx(
            "ts_aliases-build", "Build to the shape",
            "`User` requires `name` and `age`. Replace `____` with the object literal that satisfies the interface using the two input tokens.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
interface User { name: string; age: number; }
const u: User = { name: parts[0], age: Number(parts[1]) };
console.log(`${u.name} is ${u.age}`);
'''),
            [r'{ name: parts[0], age: Number(parts[1]) }'],
            [("Ada 36", "Ada is 36"), ("Bob 40", "Bob is 40"), ("Cid 7", "Cid is 7")],
            hint="age must be a number, so wrap parts[1] in Number(...).",
        ),
        tsx(
            "ts_aliases-points", "Sum of point coordinates",
            "The input is pairs of numbers. Write the solution: build a `Point[]` (each `{x, y}`) and print the sum of every coordinate.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
type Point = { x: number; y: number };
const points: Point[] = [];
for (let i = 0; i < nums.length; i += 2) {
  points.push({ x: nums[i], y: nums[i + 1] });
}
let total = 0;
for (const p of points) {
  total += p.x + p.y;
}
console.log(total);
'''),
            [r'''const points: Point[] = [];
for (let i = 0; i < nums.length; i += 2) {
  points.push({ x: nums[i], y: nums[i + 1] });
}
let total = 0;
for (const p of points) {
  total += p.x + p.y;
}
console.log(total);'''],
            [("1 2 3 4", "10"), ("0 0 5 5", "10"), ("2 3", "5")],
            hint="Step by 2 to read each x,y pair; then add up x + y for every point.",
        ),
    ],
    # -- ts_narrowing -------------------------------------------------------
    "ts_narrowing": [
        tsx(
            "ts_narrowing-typeof", "Narrow with typeof",
            "`value` is `string | number`. Replace `____` with the `typeof` check that is true when it is a number.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const value: string | number = parts[0] === "num" ? Number(parts[1]) : parts[1];
let result: string;
if (typeof value === "number") {
  result = `double ${value * 2}`;
} else {
  result = `chars ${value.length}`;
}
console.log(result);
'''),
            [r'typeof value === "number"'],
            [("num 5", "double 10"), ("str hello", "chars 5"), ("num -3", "double -6")],
            hint='typeof value === "number" lets you safely do value * 2 inside the branch.',
        ),
        tsx(
            "ts_narrowing-in", "Narrow with in",
            "`shape` has either a `radius` or a `side`. Replace `____` with the `in` check that is true when the object has a `radius`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
type Shape = { radius: number } | { side: number };
const shape: Shape = parts[0] === "circle" ? { radius: Number(parts[1]) } : { side: Number(parts[1]) };
let out: number;
if ("radius" in shape) {
  out = shape.radius * 2;
} else {
  out = shape.side * 4;
}
console.log(out);
'''),
            [r'"radius" in shape'],
            [("circle 3", "6"), ("square 5", "20"), ("circle 10", "20")],
            hint='"radius" in shape is true only for the circle variant.',
        ),
        tsx(
            "ts_narrowing-discriminated", "Area by kind",
            "`Shape` is a discriminated union tagged by `kind`. Write the solution: compute a circle's area as `3*r*r` and a square's as `side*side`, then print it.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number };
const s: Shape = parts[0] === "circle"
  ? { kind: "circle", r: Number(parts[1]) }
  : { kind: "square", side: Number(parts[1]) };
let area: number;
if (s.kind === "circle") {
  area = 3 * s.r * s.r;
} else {
  area = s.side * s.side;
}
console.log(area);
'''),
            [r'''if (s.kind === "circle") {
  area = 3 * s.r * s.r;
} else {
  area = s.side * s.side;
}'''],
            [("circle 2", "12"), ("square 5", "25"), ("circle 10", "300")],
            hint="Switch on s.kind; inside each branch TypeScript knows which fields exist.",
        ),
    ],
    # -- ts_arrays ----------------------------------------------------------
    "ts_arrays": [
        tsx(
            "ts_arrays-push", "Collect and count",
            "Replace `____` to push each parsed number onto `nums`, so its length is printed.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const nums: number[] = [];
for (const r of raw) {
  nums.push(Number(r));
}
console.log(nums.length);
'''),
            [r'nums.push(Number(r));'],
            [("1 2 3", "3"), ("5", "1"), ("9 8 7 6", "4")],
            hint="arr.push(x) appends x to the end.",
        ),
        tsx(
            "ts_arrays-last", "Last element",
            "Replace `____` with the expression for the last element of `nums`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const last = nums[nums.length - 1];
console.log(last);
'''),
            [r'nums[nums.length - 1]'],
            [("1 2 3", "3"), ("42", "42"), ("5 9", "9")],
            hint="The last index is length - 1.",
        ),
        tsx(
            "ts_arrays-tuple", "Swap a tuple",
            "`pair` is a `[number, number]` tuple. Replace `____` with the swapped tuple `[pair[1], pair[0]]`.",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const pair: [number, number] = [a, b];
const swapped: [number, number] = [pair[1], pair[0]];
console.log(swapped.join(" "));
'''),
            [r'[pair[1], pair[0]]'],
            [("3 4", "4 3"), ("1 2", "2 1"), ("7 7", "7 7")],
            hint="A tuple is just a fixed-length array; put the second element first.",
        ),
        tsx(
            "ts_arrays-middle", "Drop the ends",
            "Write the solution: print all elements except the first and last, space-separated. (Input always has at least three numbers.)",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const middle = nums.slice(1, nums.length - 1);
console.log(middle.join(" "));
'''),
            [r'''const middle = nums.slice(1, nums.length - 1);
console.log(middle.join(" "));'''],
            [("1 2 3 4 5", "2 3 4"), ("10 20 30", "20"), ("5 6 7 8", "6 7")],
            hint="slice(1, length - 1) keeps everything between the ends (end index is exclusive).",
        ),
    ],
    # -- ts_array_methods ---------------------------------------------------
    "ts_array_methods": [
        tsx(
            "ts_array_methods-map", "Square each",
            "Replace `____` with a `map` call that squares every element.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const squares = nums.map(x => x * x);
console.log(squares.join(" "));
'''),
            [r'nums.map(x => x * x)'],
            [("1 2 3", "1 4 9"), ("5", "25"), ("2 4", "4 16")],
            hint="map transforms each element: nums.map(x => x * x).",
        ),
        tsx(
            "ts_array_methods-filter", "Keep evens",
            "Replace `____` with a `filter` call that keeps only even numbers.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const evens = nums.filter(x => x % 2 === 0);
console.log(evens.join(" "));
'''),
            [r'nums.filter(x => x % 2 === 0)'],
            [("2 4 6", "2 4 6"), ("1 2 3 4", "2 4"), ("10 15 20", "10 20")],
            hint="filter keeps elements whose callback returns true.",
        ),
        tsx(
            "ts_array_methods-reduce", "Sum with reduce",
            "Replace `____` with a `reduce` call that sums the array, starting from 0.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const total = nums.reduce((a, x) => a + x, 0);
console.log(total);
'''),
            [r'nums.reduce((a, x) => a + x, 0)'],
            [("1 2 3", "6"), ("10 20", "30"), ("5", "5")],
            hint="reduce((acc, x) => acc + x, 0) folds the list to a single sum.",
        ),
        tsx(
            "ts_array_methods-pipeline", "Sum of squared odds",
            "Write the solution: keep the odd numbers, square them, and sum the result — using a `filter`/`map`/`reduce` chain.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const answer = nums
  .filter(x => x % 2 === 1)
  .map(x => x * x)
  .reduce((a, x) => a + x, 0);
console.log(answer);
'''),
            [r'''const answer = nums
  .filter(x => x % 2 === 1)
  .map(x => x * x)
  .reduce((a, x) => a + x, 0);
console.log(answer);'''],
            [("1 2 3 4", "10"), ("2 4 6", "0"), ("1 3 5", "35")],
            hint="Chain the three methods; each returns a new array for the next.",
        ),
    ],
    # -- ts_objects ---------------------------------------------------------
    "ts_objects": [
        tsx(
            "ts_objects-access", "Read a field",
            "Replace `____` to print the `name` field of `user`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const user = { name: parts[0], age: Number(parts[1]) };
console.log(user.name);
'''),
            [r'user.name'],
            [("Ada 36", "Ada"), ("Bob 40", "Bob"), ("Cid 7", "Cid")],
            hint="Access object fields with a dot: user.name.",
        ),
        tsx(
            "ts_objects-count", "Count with an index signature",
            "`counts` maps each word to how many times it appears. Replace `____` with the line that increments the count for `w` (defaulting a missing count to 0).",
            _P(r'''
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const counts: { [w: string]: number } = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
console.log(counts[words[0]]);
'''),
            [r'counts[w] = (counts[w] ?? 0) + 1;'],
            [("a b a c a", "3"), ("hi hi", "2"), ("x y z", "1")],
            hint="counts[w] = (counts[w] ?? 0) + 1 — the ?? handles the first time you see w.",
        ),
        tsx(
            "ts_objects-entries", "Sum object values",
            "The input is `key value` pairs. Write the solution: build an object from them, then sum all its values with `Object.entries`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const obj: { [k: string]: number } = {};
for (let i = 0; i < parts.length; i += 2) {
  obj[parts[i]] = Number(parts[i + 1]);
}
let total = 0;
for (const [k, v] of Object.entries(obj)) {
  total += v;
}
console.log(total);
'''),
            [r'''let total = 0;
for (const [k, v] of Object.entries(obj)) {
  total += v;
}
console.log(total);'''],
            [("a 1 b 2 c 3", "6"), ("x 10 y 20", "30"), ("solo 5", "5")],
            hint="Object.entries(obj) yields [key, value] pairs you can destructure.",
        ),
    ],
    # -- ts_maps_sets -------------------------------------------------------
    "ts_maps_sets": [
        tsx(
            "ts_maps_sets-set", "Count distinct",
            "Replace `____` to add each value to the `Set`, so its `size` (the distinct count) is printed.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const seen = new Set<number>();
for (const x of nums) {
  seen.add(x);
}
console.log(seen.size);
'''),
            [r'seen.add(x);'],
            [("1 2 2 3", "3"), ("5 5 5", "1"), ("1 2 3 4", "4")],
            hint="A Set ignores duplicates, so seen.add(x) then seen.size gives the distinct count.",
        ),
        tsx(
            "ts_maps_sets-map", "Highest frequency",
            "`freq` counts each word. Replace `____` with the line that increments `w`'s count in the `Map` (defaulting a miss to 0).",
            _P(r'''
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const freq = new Map<string, number>();
for (const w of words) {
  freq.set(w, (freq.get(w) ?? 0) + 1);
}
let best = 0;
for (const c of freq.values()) {
  if (c > best) best = c;
}
console.log(best);
'''),
            [r'freq.set(w, (freq.get(w) ?? 0) + 1);'],
            [("a b a a", "3"), ("x y z", "1"), ("hi hi bye", "2")],
            hint="freq.set(w, (freq.get(w) ?? 0) + 1) is the Map counting pattern.",
        ),
        tsx(
            "ts_maps_sets-firstdup", "First repeated value",
            "Write the solution: print the first value that appears a second time, or `-1` if every value is unique. Use a `Set` to remember what you've seen.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const seen = new Set<number>();
let answer = -1;
for (const x of nums) {
  if (seen.has(x)) {
    answer = x;
    break;
  }
  seen.add(x);
}
console.log(answer);
'''),
            [r'''const seen = new Set<number>();
let answer = -1;
for (const x of nums) {
  if (seen.has(x)) {
    answer = x;
    break;
  }
  seen.add(x);
}
console.log(answer);'''],
            [("1 2 3 2 1", "2"), ("1 2 3", "-1"), ("5 5", "5")],
            hint="Check seen.has(x) BEFORE adding x; the first hit is your answer.",
        ),
    ],
    # -- ts_enums -----------------------------------------------------------
    "ts_enums": [
        tsx(
            "ts_enums-next", "Next direction",
            "`order` lists the compass directions clockwise. Replace `____` with the expression for the next direction after `idx` (wrapping around with `% 4`).",
            _P(r'''
import * as fs from "fs";
const d = fs.readFileSync(0, "utf8").trim();
type Direction = "N" | "E" | "S" | "W";
const order: Direction[] = ["N", "E", "S", "W"];
const idx = order.indexOf(d as Direction);
const next = order[(idx + 1) % 4];
console.log(next);
'''),
            [r'order[(idx + 1) % 4]'],
            [("N", "E"), ("W", "N"), ("S", "W")],
            hint="(idx + 1) % 4 wraps from the last direction back to the first.",
        ),
        tsx(
            "ts_enums-const", "Label from a const map",
            "`Status` is a frozen object mapping codes to labels. Replace `____` with the lookup that returns the label for `code`.",
            _P(r'''
import * as fs from "fs";
const code = fs.readFileSync(0, "utf8").trim();
const Status = { L: "loading", D: "done", E: "error" } as const;
type Key = keyof typeof Status;
const label = Status[code as Key];
console.log(label);
'''),
            [r'Status[code as Key]'],
            [("L", "loading"), ("D", "done"), ("E", "error")],
            hint="Index the object with the key: Status[code as Key].",
        ),
        tsx(
            "ts_enums-traffic", "Traffic light action",
            "`Light` is the literal union `red | yellow | green`. Write the solution: a function returning `stop` / `slow` / `go` respectively, then print the action.",
            _P(r'''
import * as fs from "fs";
const color = fs.readFileSync(0, "utf8").trim();
type Light = "red" | "yellow" | "green";
function action(c: Light): string {
  if (c === "red") return "stop";
  if (c === "yellow") return "slow";
  return "go";
}
console.log(action(color as Light));
'''),
            [r'''function action(c: Light): string {
  if (c === "red") return "stop";
  if (c === "yellow") return "slow";
  return "go";
}'''],
            [("red", "stop"), ("green", "go"), ("yellow", "slow")],
            hint="Handle red and yellow explicitly; green is the remaining case.",
        ),
    ],
    # -- ts_generics --------------------------------------------------------
    "ts_generics": [
        tsx(
            "ts_generics-first", "Generic first element",
            "Replace `____` with the header of a generic function `first` taking a `T[]` and returning a `T`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function first<T>(arr: T[]): T {
  return arr[0];
}
console.log(first(nums));
'''),
            [r'function first<T>(arr: T[]): T {'],
            [("3 1 2", "3"), ("9", "9"), ("5 6 7", "5")],
            hint="The type variable goes in angle brackets: function first<T>(arr: T[]): T.",
        ),
        tsx(
            "ts_generics-last", "Generic last element",
            "Replace `____` with the body that returns the last element of the generic array.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function last<T>(arr: T[]): T {
  return arr[arr.length - 1];
}
console.log(last(nums));
'''),
            [r'return arr[arr.length - 1];'],
            [("3 1 2", "2"), ("9", "9"), ("5 6 7", "7")],
            hint="The last index is arr.length - 1.",
        ),
        tsx(
            "ts_generics-longest", "Longer of two lists",
            "Two space-separated lists are given (one per line). Write the solution: a constrained generic `longest<T extends { length: number }>` that returns the longer one, then print its length. On a tie, return the first.",
            _P(r'''
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").split(/\r?\n/);
const a = lines[0].trim().split(/\s+/);
const b = lines[1].trim().split(/\s+/);
function longest<T extends { length: number }>(x: T, y: T): T {
  return x.length >= y.length ? x : y;
}
console.log(longest(a, b).length);
'''),
            [r'''function longest<T extends { length: number }>(x: T, y: T): T {
  return x.length >= y.length ? x : y;
}
console.log(longest(a, b).length);'''],
            [("1 2 3\n4 5", "3"), ("1\n2 3 4 5", "4"), ("1 2\n3 4", "2")],
            hint="The constraint { length: number } lets you compare .length; use >= so ties keep x.",
        ),
    ],
    # -- ts_classes ---------------------------------------------------------
    "ts_classes": [
        tsx(
            "ts_classes-field", "Initialize a field",
            "Replace `____` with the constructor line that stores `start` into the instance's `count` field.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
class Counter {
  count: number;
  constructor(start: number) {
    this.count = start;
  }
  increment(): void {
    this.count++;
  }
}
const c = new Counter(0);
for (let i = 0; i < n; i++) {
  c.increment();
}
console.log(c.count);
'''),
            [r'this.count = start;'],
            [("3", "3"), ("0", "0"), ("5", "5")],
            hint="Assign the parameter to the field with this.count = start;.",
        ),
        tsx(
            "ts_classes-method", "A method that computes",
            "Replace `____` with the body of the `area()` method.",
            _P(r'''
import * as fs from "fs";
const [w, h] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
class Rect {
  width: number;
  height: number;
  constructor(w: number, h: number) {
    this.width = w;
    this.height = h;
  }
  area(): number {
    return this.width * this.height;
  }
}
console.log(new Rect(w, h).area());
'''),
            [r'return this.width * this.height;'],
            [("3 4", "12"), ("5 5", "25"), ("2 7", "14")],
            hint="Inside a method, read fields via this: this.width * this.height.",
        ),
        tsx(
            "ts_classes-inherit", "Override a method",
            "`Dog` should extend `Animal` and override `speak()` to say `<name> barks`. Write the `Dog` subclass.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
class Animal {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
  speak(): string {
    return `${this.name} makes a sound`;
  }
}
class Dog extends Animal {
  speak(): string {
    return `${this.name} barks`;
  }
}
const animal = parts[0] === "dog" ? new Dog(parts[1]) : new Animal(parts[1]);
console.log(animal.speak());
'''),
            [r'''class Dog extends Animal {
  speak(): string {
    return `${this.name} barks`;
  }
}'''],
            [("dog Rex", "Rex barks"), ("cat Tom", "Tom makes a sound"), ("dog Max", "Max barks")],
            hint="extends Animal, then redefine speak() to return the barking message.",
        ),
    ],
    # -- ts_this_accessors --------------------------------------------------
    "ts_this_accessors": [
        tsx(
            "ts_this_accessors-getter", "Use a getter",
            "`area` is a getter, so it is read like a property. Replace `____` to print `r.area` (no parentheses!).",
            _P(r'''
import * as fs from "fs";
const [w, h] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
class Rect {
  width: number;
  height: number;
  constructor(w: number, h: number) {
    this.width = w;
    this.height = h;
  }
  get area(): number {
    return this.width * this.height;
  }
}
const r = new Rect(w, h);
console.log(r.area);
'''),
            [r'r.area'],
            [("3 4", "12"), ("5 5", "25"), ("2 7", "14")],
            hint="A getter is accessed like a field: r.area, not r.area().",
        ),
        tsx(
            "ts_this_accessors-setter", "A setter makes a square",
            "Assigning to `square` should set both sides. Replace `____` with the assignment `b.square = side;` that triggers the setter.",
            _P(r'''
import * as fs from "fs";
const side = Number(fs.readFileSync(0, "utf8").trim());
class Box {
  width: number;
  height: number;
  constructor() {
    this.width = 0;
    this.height = 0;
  }
  set square(s: number) {
    this.width = s;
    this.height = s;
  }
  get area(): number {
    return this.width * this.height;
  }
}
const b = new Box();
b.square = side;
console.log(b.area);
'''),
            [r'b.square = side;'],
            [("5", "25"), ("3", "9"), ("10", "100")],
            hint="A setter runs on assignment: b.square = side; sets both width and height.",
        ),
        tsx(
            "ts_this_accessors-account", "Deposit into an account",
            "Write the solution: a `deposit(amount)` method that adds to `this.balance`, so after depositing every input amount the final balance prints.",
            _P(r'''
import * as fs from "fs";
const amounts = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
class Account {
  balance: number;
  constructor() {
    this.balance = 0;
  }
  deposit(amount: number): void {
    this.balance += amount;
  }
}
const acc = new Account();
for (const a of amounts) {
  acc.deposit(a);
}
console.log(acc.balance);
'''),
            [r'''deposit(amount: number): void {
    this.balance += amount;
  }'''],
            [("10 20 30", "60"), ("5", "5"), ("100 -40 10", "70")],
            hint="Inside deposit, update the field: this.balance += amount;.",
        ),
    ],
    # -- ts_modules ---------------------------------------------------------
    "ts_modules": [
        tsx(
            "ts_modules-export", "Export a function",
            "In a real project `add` would live in its own module. Replace `____` with the `export` keyword so `add` is published (it still runs here in one file).",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
export function add(x: number, y: number): number {
  return x + y;
}
console.log(add(a, b));
'''),
            [r'export function add(x: number, y: number): number {'],
            [("2 3", "5"), ("10 -4", "6"), ("0 0", "0")],
            hint="Prefix the declaration with export: export function add(...) { ... }.",
        ),
        tsx(
            "ts_modules-use", "Use an exported constant",
            "`TAX` is exported above. Replace `____` with the expression that applies the tax: `price * TAX`, rounded down.",
            _P(r'''
import * as fs from "fs";
const price = Number(fs.readFileSync(0, "utf8").trim());
export const TAX = 2;
const total = Math.floor(price * TAX);
console.log(total);
'''),
            [r'price * TAX'],
            [("10", "20"), ("7", "14"), ("0", "0")],
            hint="Multiply price by the exported constant TAX.",
        ),
        tsx(
            "ts_modules-default", "A default export",
            "Each file may have one `export default`. Write the solution: export `main` as the default and call it, printing the doubled input.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
export default function main(x: number): number {
  return x * 2;
}
console.log(main(n));
'''),
            [r'''export default function main(x: number): number {
  return x * 2;
}
console.log(main(n));'''],
            [("5", "10"), ("0", "0"), ("-3", "-6")],
            hint="export default function main(...) marks the file's single main export.",
        ),
    ],
    # -- ts_nullish ---------------------------------------------------------
    "ts_nullish": [
        tsx(
            "ts_nullish-default", "Fallback with ??",
            "`name` may be `undefined` (empty input). Replace `____` so the greeting falls back to `friend` when it is missing.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const name: string | undefined = raw === "" ? undefined : raw;
console.log(`Hi ${name ?? "friend"}`);
'''),
            [r'name ?? "friend"'],
            [("Ada", "Hi Ada"), ("", "Hi friend"), ("Bob", "Hi Bob")],
            hint='name ?? "friend" uses the fallback only when name is null/undefined.',
        ),
        tsx(
            "ts_nullish-guard", "Guard the missing case",
            "`maybe` is `number | undefined`. Replace `____` with the guard that rules out the missing case so `.toFixed(1)` is safe.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const maybe: number | undefined = raw === "" ? undefined : Number(raw);
let out: string;
if (maybe != null) {
  out = maybe.toFixed(1);
} else {
  out = "none";
}
console.log(out);
'''),
            [r'maybe != null'],
            [("3", "3.0"), ("", "none"), ("10", "10.0")],
            hint="x != null rules out BOTH null and undefined in one check.",
        ),
        tsx(
            "ts_nullish-chain", "Safe access with ?.",
            "The city may be absent. Write the solution: use optional chaining to read `user.address?.city`, falling back to `unknown`, and print it.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const user: { address?: { city: string } } = raw === "" ? {} : { address: { city: raw } };
const city = user.address?.city ?? "unknown";
console.log(city);
'''),
            [r'''const city = user.address?.city ?? "unknown";
console.log(city);'''],
            [("Paris", "Paris"), ("", "unknown"), ("Tokyo", "Tokyo")],
            hint="user.address?.city is undefined when address is missing; ?? supplies the fallback.",
        ),
    ],
    # -- ts_errors ----------------------------------------------------------
    "ts_errors": [
        tsx(
            "ts_errors-throw", "Throw on bad input",
            "Replace `____` with a `throw` that raises an `Error` when the number is not positive.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
function check(x: number): number {
  if (x <= 0) throw new Error("must be positive");
  return x;
}
try {
  console.log(check(n));
} catch (e) {
  console.log(e instanceof Error ? e.message : "unknown");
}
'''),
            [r'throw new Error("must be positive");'],
            [("5", "5"), ("-1", "must be positive"), ("0", "must be positive")],
            hint='throw new Error("...") signals the failure the catch block handles.',
        ),
        tsx(
            "ts_errors-catch", "Narrow the caught value",
            "The caught value `e` is `unknown`. Replace `____` with the check that lets you safely read `e.message`.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
try {
  const n = Number(raw);
  if (Number.isNaN(n)) throw new Error("not a number");
  console.log(n * 2);
} catch (e) {
  console.log(e instanceof Error ? e.message : "unknown");
}
'''),
            [r'e instanceof Error'],
            [("21", "42"), ("abc", "not a number"), ("0", "0")],
            hint="e instanceof Error narrows unknown so e.message is available.",
        ),
        tsx(
            "ts_errors-finally", "Parse with try/catch/finally",
            "Write the solution: parse the input; print the number if valid or `invalid` if not; and ALWAYS print `done` afterward using `finally`.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
try {
  const n = Number(raw);
  if (Number.isNaN(n)) throw new Error("bad");
  console.log(n);
} catch (e) {
  console.log("invalid");
} finally {
  console.log("done");
}
'''),
            [r'''try {
  const n = Number(raw);
  if (Number.isNaN(n)) throw new Error("bad");
  console.log(n);
} catch (e) {
  console.log("invalid");
} finally {
  console.log("done");
}'''],
            [("7", "7\ndone"), ("oops", "invalid\ndone"), ("0", "0\ndone")],
            hint="finally runs no matter what, so put the 'done' print there.",
        ),
    ],
    # -- ts_utility_types ---------------------------------------------------
    "ts_utility_types": [
        tsx(
            "ts_utility_types-partial", "Apply a Partial patch",
            "`patch` is typed `Partial<User>` (every field optional). Replace `____` with the spread merge that applies the patch over `user`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
interface User { name: string; age: number; }
const user: User = { name: "Ada", age: 36 };
const patch: Partial<User> = { age: Number(parts[0]) };
const updated: User = { ...user, ...patch };
console.log(`${updated.name} ${updated.age}`);
'''),
            [r'{ ...user, ...patch }'],
            [("40", "Ada 40"), ("18", "Ada 18"), ("99", "Ada 99")],
            hint="Spread the base then the patch: { ...user, ...patch } — later fields win.",
        ),
        tsx(
            "ts_utility_types-record", "A Record count map",
            "`counts` is typed `Record<string, number>`. Replace `____` with the increment line for word `w`.",
            _P(r'''
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const counts: Record<string, number> = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
console.log(counts[words[0]]);
'''),
            [r'counts[w] = (counts[w] ?? 0) + 1;'],
            [("a b a a", "3"), ("hi", "1"), ("x x y", "2")],
            hint="Record<string, number> is just a string-keyed number map; increment as usual.",
        ),
        tsx(
            "ts_utility_types-pick", "Pick a subset",
            "`NameOnly` uses `Pick<User, \"name\">`. Write the solution: build a `NameOnly` from the full user and print its name.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
interface User { name: string; age: number; }
const user: User = { name: parts[0], age: Number(parts[1]) };
type NameOnly = Pick<User, "name">;
const card: NameOnly = { name: user.name };
console.log(card.name);
'''),
            [r'''const card: NameOnly = { name: user.name };
console.log(card.name);'''],
            [("Ada 36", "Ada"), ("Bob 40", "Bob"), ("Cid 7", "Cid")],
            hint='Pick<User, "name"> keeps only the name field, so build { name: user.name }.',
        ),
    ],
    # -- ts_async -----------------------------------------------------------
    "ts_async": [
        tsx(
            "ts_async-await", "Await a promise",
            "`later(n)` resolves to `n` after a tick. Replace `____` to `await` it inside the async function.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
function later(value: number): Promise<number> {
  return new Promise(resolve => setTimeout(() => resolve(value), 5));
}
async function main(): Promise<void> {
  const x = await later(n);
  console.log(x * 2);
}
main();
'''),
            [r'const x = await later(n);'],
            [("21", "42"), ("0", "0"), ("-3", "-6")],
            hint="await pauses until the promise resolves: const x = await later(n);.",
        ),
        tsx(
            "ts_async-all", "Await in parallel",
            "Replace `____` with `Promise.all` over the two promises so both resolve before you sum them.",
            _P(r'''
import * as fs from "fs";
const [a, b] = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
function later(value: number): Promise<number> {
  return new Promise(resolve => setTimeout(() => resolve(value), 5));
}
async function main(): Promise<void> {
  const [x, y] = await Promise.all([later(a), later(b)]);
  console.log(x + y);
}
main();
'''),
            [r'await Promise.all([later(a), later(b)])'],
            [("2 3", "5"), ("10 20", "30"), ("0 0", "0")],
            hint="Promise.all([p1, p2]) resolves to an array once both are done.",
        ),
        tsx(
            "ts_async-trycatch", "Handle a rejection",
            "`fetchValue` rejects when the input is negative. Write the async solution: await it, print the value on success, or `failed` on rejection using try/catch.",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
function fetchValue(x: number): Promise<number> {
  return new Promise((resolve, reject) => {
    if (x < 0) reject(new Error("negative"));
    else resolve(x);
  });
}
async function main(): Promise<void> {
  try {
    const v = await fetchValue(n);
    console.log(v);
  } catch (e) {
    console.log("failed");
  }
}
main();
'''),
            [r'''try {
    const v = await fetchValue(n);
    console.log(v);
  } catch (e) {
    console.log("failed");
  }'''],
            [("7", "7"), ("-1", "failed"), ("0", "0")],
            hint="await throws on rejection, so wrap it in try/catch just like synchronous errors.",
        ),
    ],
    # -- ts_destructuring ---------------------------------------------------
    "ts_destructuring": [
        tsx(
            "ts_destructuring-array", "Unpack an array",
            "Replace `____` to destructure the first two elements of `nums` into `a` and `b`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const [a, b] = nums;
console.log(a + b);
'''),
            [r'const [a, b] = nums;'],
            [("3 4", "7"), ("10 20", "30"), ("5 6", "11")],
            hint="const [a, b] = nums pulls out the first two elements by position.",
        ),
        tsx(
            "ts_destructuring-object", "Unpack an object",
            "Replace `____` to destructure `name` and `age` out of `user` by key.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const user = { name: parts[0], age: Number(parts[1]) };
const { name, age } = user;
console.log(`${name} ${age}`);
'''),
            [r'const { name, age } = user;'],
            [("Ada 36", "Ada 36"), ("Bob 40", "Bob 40"), ("Cid 7", "Cid 7")],
            hint="Object destructuring matches by key: const { name, age } = user.",
        ),
        tsx(
            "ts_destructuring-spread", "Merge with spread",
            "Two lists are read (one per line). Replace `____` with the spread expression that concatenates them into one array.",
            _P(r'''
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").split(/\r?\n/);
const a = lines[0].trim().split(/\s+/).map(Number);
const b = lines[1].trim().split(/\s+/).map(Number);
const merged = [...a, ...b];
console.log(merged.join(" "));
'''),
            [r'[...a, ...b]'],
            [("1 2\n3 4", "1 2 3 4"), ("5\n6 7", "5 6 7"), ("1\n2", "1 2")],
            hint="[...a, ...b] expands both arrays into a new combined array.",
        ),
        tsx(
            "ts_destructuring-rest", "Sum all but the first",
            "Write the solution: use a rest pattern to split off the first element, then print the sum of the remaining ones.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const [first, ...rest] = nums;
const total = rest.reduce((a, x) => a + x, 0);
console.log(total);
'''),
            [r'''const [first, ...rest] = nums;
const total = rest.reduce((a, x) => a + x, 0);
console.log(total);'''],
            [("1 2 3 4", "9"), ("10", "0"), ("5 5 5", "10")],
            hint="const [first, ...rest] = nums gathers everything after the first into rest.",
        ),
    ],
    # -- ts_assertions ------------------------------------------------------
    "ts_assertions": [
        tsx(
            "ts_assertions-parse", "Use an asserted shape",
            "`data` was parsed and asserted as `{ count: number }`. Replace `____` with the expression that doubles its `count`.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const data = JSON.parse(raw) as { count: number };
console.log(data.count * 2);
'''),
            [r'data.count * 2'],
            [('{"count":5}', "10"), ('{"count":0}', "0"), ('{"count":21}', "42")],
            hint="The assertion lets you read data.count as a number; multiply it by 2.",
        ),
        tsx(
            "ts_assertions-nonnull", "Trust a found value",
            "`find` may return `undefined`, but here a match always exists, so a non-null assertion `!` is used. Replace `____` with the `find` call that locates the first value over 10.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const firstBig = nums.find(x => x > 10)!;
console.log(firstBig * 2);
'''),
            [r'nums.find(x => x > 10)'],
            [("5 15 3", "30"), ("20 1", "40"), ("11 12", "22")],
            hint="nums.find(x => x > 10) returns the first match; the ! after it asserts it isn't undefined.",
        ),
        tsx(
            "ts_assertions-array", "Parse and sum a JSON array",
            "The input is a JSON array of numbers. Write the solution: parse it (asserting `number[]`) and print the sum.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const nums = JSON.parse(raw) as number[];
const total = nums.reduce((a, x) => a + x, 0);
console.log(total);
'''),
            [r'''const nums = JSON.parse(raw) as number[];
const total = nums.reduce((a, x) => a + x, 0);
console.log(total);'''],
            [("[1,2,3]", "6"), ("[10,20]", "30"), ("[5]", "5")],
            hint="JSON.parse(raw) as number[] gives a typed array you can reduce.",
        ),
    ],
    # -- ts_compose ---------------------------------------------------------
    "ts_compose": [
        tsx(
            "ts_compose-extends", "Satisfy an extended interface",
            "`Person extends Named`, so it needs BOTH `name` and `age`. Replace `____` with the object literal that satisfies `Person`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
interface Named { name: string; }
interface Person extends Named { age: number; }
const p: Person = { name: parts[0], age: Number(parts[1]) };
console.log(`${p.name} ${p.age}`);
'''),
            [r'{ name: parts[0], age: Number(parts[1]) }'],
            [("Ada 36", "Ada 36"), ("Bob 40", "Bob 40"), ("Cid 7", "Cid 7")],
            hint="An extended interface needs the inherited field (name) AND the new one (age).",
        ),
        tsx(
            "ts_compose-intersection", "Build an intersection type",
            "`Employee` is `Person & { salary: number }`. Replace `____` with the object literal that has every required field.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
type Person = { name: string };
type Employee = Person & { salary: number };
const e: Employee = { name: parts[0], salary: Number(parts[1]) };
console.log(`${e.name} earns ${e.salary}`);
'''),
            [r'{ name: parts[0], salary: Number(parts[1]) }'],
            [("Ada 100", "Ada earns 100"), ("Bob 50", "Bob earns 50"), ("Cid 7", "Cid earns 7")],
            hint="An intersection needs all members of both parts: name AND salary.",
        ),
        tsx(
            "ts_compose-circle", "Compose then compute",
            "`Circle extends Point` (adds a radius). Write the solution: build the circle from the three inputs and print its area as `3 * r * r`.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
interface Point { x: number; y: number; }
interface Circle extends Point { r: number; }
const c: Circle = { x: parts[0], y: parts[1], r: parts[2] };
const area = 3 * c.r * c.r;
console.log(area);
'''),
            [r'''const c: Circle = { x: parts[0], y: parts[1], r: parts[2] };
const area = 3 * c.r * c.r;
console.log(area);'''],
            [("0 0 2", "12"), ("1 1 10", "300"), ("5 5 1", "3")],
            hint="Circle needs x, y (from Point) and r; area uses the radius: 3 * r * r.",
        ),
    ],
    # -- ts_json ------------------------------------------------------------
    "ts_json": [
        tsx(
            "ts_json-parse", "Parse and read",
            "Replace `____` with the call that turns the JSON text `raw` into a live object.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const obj = JSON.parse(raw);
console.log(obj.name);
'''),
            [r'JSON.parse(raw)'],
            [('{"name":"Ada"}', "Ada"), ('{"name":"Bob","age":3}', "Bob"), ('{"name":"Cid"}', "Cid")],
            hint="JSON.parse(raw) converts the JSON string into an object you can read fields from.",
        ),
        tsx(
            "ts_json-stringify", "Serialize to JSON",
            "Replace `____` with the call that turns the `user` object into a JSON string.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const user = { name: parts[0], age: Number(parts[1]) };
console.log(JSON.stringify(user));
'''),
            [r'JSON.stringify(user)'],
            [("Ada 36", '{"name":"Ada","age":36}'), ("Bob 40", '{"name":"Bob","age":40}')],
            hint="JSON.stringify(user) emits the fields in insertion order with no spaces.",
        ),
        tsx(
            "ts_json-roundtrip", "Read, change, write",
            "The input is a JSON user. Write the solution: parse it, add 1 to its `age`, and print the object back as JSON.",
            _P(r'''
import * as fs from "fs";
const raw = fs.readFileSync(0, "utf8").trim();
const user = JSON.parse(raw) as { name: string; age: number };
user.age = user.age + 1;
console.log(JSON.stringify(user));
'''),
            [r'''const user = JSON.parse(raw) as { name: string; age: number };
user.age = user.age + 1;
console.log(JSON.stringify(user));'''],
            [('{"name":"Ada","age":36}', '{"name":"Ada","age":37}'),
             ('{"name":"Bob","age":9}', '{"name":"Bob","age":10}')],
            hint="Parse to an object, mutate the field, then stringify the whole object back.",
        ),
    ],
    # -- ts_immutability ----------------------------------------------------
    "ts_immutability": [
        tsx(
            "ts_immutability-update", "Immutable update",
            "Replace `____` with a spread that makes a NEW object like `user` but with `age` one higher — leaving `user` unchanged.",
            _P(r'''
import * as fs from "fs";
const parts = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const user = { name: parts[0], age: Number(parts[1]) };
const older = { ...user, age: user.age + 1 };
console.log(`${user.age} ${older.age}`);
'''),
            [r'{ ...user, age: user.age + 1 }'],
            [("Ada 36", "36 37"), ("Bob 9", "9 10"), ("Cid 0", "0 1")],
            hint="{ ...user, age: user.age + 1 } copies user then overrides age; the original stays put.",
        ),
        tsx(
            "ts_immutability-append", "Immutable append",
            "Replace `____` with a spread that builds a NEW array: every element of `nums` followed by `99`.",
            _P(r'''
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
const extended = [...nums, 99];
console.log(`${nums.length} ${extended.length}`);
'''),
            [r'[...nums, 99]'],
            [("1 2 3", "3 4"), ("5", "1 2"), ("7 8 9 10", "4 5")],
            hint="[...nums, 99] spreads the originals into a new array and adds 99 — nums itself is unchanged.",
        ),
        tsx(
            "ts_immutability-freeze", "Freeze at runtime",
            "Write the solution: freeze a config object so an attempted change can't take effect, then print its `limit` (which stays the input value).",
            _P(r'''
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const config = Object.freeze({ limit: n });
try {
  (config as { limit: number }).limit = 999;
} catch (e) {
  // frozen objects reject writes in strict mode
}
console.log(config.limit);
'''),
            [r'''const config = Object.freeze({ limit: n });
try {
  (config as { limit: number }).limit = 999;
} catch (e) {
  // frozen objects reject writes in strict mode
}
console.log(config.limit);'''],
            [("5", "5"), ("42", "42"), ("0", "0")],
            hint="Object.freeze locks the object; the write is rejected, so limit keeps its original value.",
        ),
    ],
}
EXERCISES.update(TS_EXERCISES)
