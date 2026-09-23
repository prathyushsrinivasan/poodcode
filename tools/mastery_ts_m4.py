# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 4: Rigor (weeks 14-17).
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
    # =======================================================================
    # MONTH 4 — Rigor
    # =======================================================================
    # D-2: the toolchain week. `ts_nullish` moved to week 11; modules and
    # declaration files came forward from the old capstone week, which was too
    # late to meet the tools every real project starts with.
    _w(14, "Month 4 · Rigor",
        "The Toolchain: tsconfig, Modules & Declarations",
        "Configure the compiler on purpose, split code into modules, and describe the code you do not own.",
        ["ts_tsconfig", "ts_modules", "ts_declaration_files"],
        [("missing-number", "Absence as a first-class case — under `noUncheckedIndexedAccess`."),
         ("count-negatives", "Boundary conditions on an index scan, with every read honest."),
         ("is-sorted", "An empty input is a real case — decide what it means.")],
        "Take your Week 8 config reader and make it clean under `noUncheckedIndexedAccess`: rewrite every index access to handle `undefined` honestly, split the parsing and the printing into their own modules, and write a `.d.ts` for one helper you pretend is an untyped library.",
        [("With `strictNullChecks` on, what does `string` mean?",
          ["A string — absence must be written as string | null or string | undefined",
           "A string, null or undefined",
           "A non-empty string",
           "The same as before; the flag only affects parameters"], 0,
          "The flag is what makes annotations mean what they say. Off, every type quietly includes the nullish values."),
         ("What does `noUncheckedIndexedAccess` change?",
          ["arr[i] becomes T | undefined, reflecting that the index may be out of range",
           "It throws at runtime on a bad index",
           "It forbids index signatures",
           "It requires .at() instead of brackets"], 0,
          "It tells the truth about indexing. Not part of `strict`, usually the most disruptive flag to adopt — and the most valuable."),
         ("What does a `.d.ts` file emit at build time?",
          ["Nothing — it only describes types the runtime is assumed to provide",
           "A JavaScript stub per declaration",
           "A module that must be imported",
           "A runtime validation shim"], 0,
          "Declaration files are pure description. Declaring something the runtime lacks gives a ReferenceError with no compile-time warning."),
         ("Why must module augmentation use `interface` rather than `type`?",
          ["Interfaces merge across declarations; type aliases cannot be reopened",
           "type is illegal inside declare module",
           "Interfaces are erased and types are not",
           "type cannot describe objects"], 0,
          "Declaration merging is interface-only, and it is what lets you ADD a field to a library type instead of shadowing it."),
         ("What is the difference between a default export and a named export?",
          ["A default can be imported under any name, which makes it easy to rename inconsistently",
           "A default is faster to load",
           "Named exports cannot be re-exported",
           "A module may have several defaults"], 0,
          "Named exports keep one canonical spelling across the codebase, which is why many style guides prefer them for anything but a single obvious entry point."),
         ("What does `import type { X } from \"./x\"` guarantee?",
          ["The import is erased entirely, so no runtime module dependency is created",
           "X is imported lazily",
           "X must be a type alias, not an interface",
           "The module is loaded but unused"], 0,
          "It makes the type-only intent explicit, avoiding a runtime import that a bundler would otherwise have to keep — the point of `verbatimModuleSyntax`.")]),

    _w(15, "Month 4 · Rigor",
        "Assertions, satisfies & Structural Typing",
        "Understand what the compiler compares, and the two very different ways to override it.",
        ["ts_assertions", "ts_satisfies", "ts_structural_typing"],
        [("longest-common-prefix-strs", "Shape-driven helpers over string arrays."),
         ("design-hashmap", "Build to an interface without inheriting from one.")],
        "Write a `routes.ts` that declares a route table with `satisfies`, derives the route-name union from it, and exposes a lookup that rejects unknown names.",
        [("What does `satisfies` do that an annotation does not?",
          ["Checks the value against the type while keeping its narrower inferred type",
           "Checks the value at runtime",
           "Widens the value to the given type",
           "Makes the value readonly"], 0,
          "An annotation replaces the inferred type; `satisfies` only validates against it, so literal keys and tuple shapes survive."),
         ("Why is `const p: Point = { x: 1, y: 2, label: \"h\" }` an error when assigning the same object via a variable is not?",
          ["The excess property check applies only to fresh object literals assigned directly",
           "Variables are typed any",
           "Both are errors, reported at different times",
           "label is a reserved name"], 0,
          "The literal form is where typos live, so TypeScript checks it. Widening through a variable falls back to ordinary structural assignability."),
         ("Two unrelated aliases with identical members — is one assignable to the other?",
          ["Yes; structural typing compares shapes, not names",
           "No; they are distinct named types",
           "Only if one extends the other",
           "Only for interfaces"], 0,
          "Nothing links them by name, but their members match. This is the core difference from Java's nominal `implements`."),
         ("What makes a class partly nominal?",
          ["private or protected members, which only match the declaring class",
           "A constructor",
           "Implementing an interface",
           "Being abstract"], 0,
          "Private members are tied to their declaration, so two identical-looking classes are not interchangeable — the one nominal corner of the system.")]),

    _w(16, "Month 4 · Rigor",
        "Branded Types & Immutability",
        "Make validated values a type, and stop accidental mutation at the boundary.",
        ["ts_branded_types", "ts_immutability"],
        [("product-except-self", "Build a new array rather than editing in place."),
         ("rotate-array", "Compare the in-place and copying solutions honestly.")],
        "Write an `ids.ts` with branded `UserId` and `OrderId`, validating parsers for both, and a `readonly` lookup table that cannot be mutated by callers.",
        [("What does a brand cost at runtime?",
          ["Nothing — the intersection is erased and the value stays a plain string",
           "One object allocation per value",
           "A hidden property on each value",
           "A prototype lookup per access"], 0,
          "That is the appeal over a wrapper class: nominal safety with zero runtime representation."),
         ("Why should exactly one function apply the `as UserId` cast?",
          ["It concentrates the unchecked assertion in one validated place",
           "TypeScript allows one cast per type",
           "Casting elsewhere fails at runtime",
           "The compiler counts casts"], 0,
          "A brand is only as trustworthy as the assertions that create it. Scattered casts mean the type proves nothing."),
         ("What does `readonly string[]` prevent?",
          ["Calling mutating methods and assigning to indices",
           "Reassigning the variable",
           "Reading elements",
           "Passing the array to functions"], 0,
          "It is a compile-time restriction on the array's own operations. `const` only stops rebinding the variable."),
         ("Does `Object.freeze` give you a deeply immutable object?",
          ["No — it is shallow; nested objects remain mutable",
           "Yes, it recurses",
           "Only under strict mode",
           "Only for arrays"], 0,
          "Freezing one level is the runtime counterpart to `Readonly<T>`, which is also shallow. Deep immutability needs a recursive helper.")]),

    _w(17, "Month 4 · Rigor",
        "Composition & Utility Types",
        "Build types out of other types instead of restating them.",
        ["ts_compose", "ts_utility_types"],
        [("merge-intervals", "Sort, then fold — with a well-typed interval."),
         ("insert-interval", "A variant of the same model."),
         ("can-attend-meetings", "The simplest form of the pattern.")],
        "Model a `Task` type, then derive `TaskDraft` (no id), `TaskPatch` (all optional) and `TaskSummary` (a few fields) with `Omit`, `Partial` and `Pick` rather than three hand-written types.",
        [("What does `Omit<T, K>` do?",
          ["Produces T without the properties named in K",
           "Makes the properties in K optional",
           "Keeps only the properties in K",
           "Makes T readonly except K"], 0,
          "`Pick` keeps, `Omit` removes. `Omit` is defined in terms of `Pick` and `Exclude`."),
         ("How do you combine two object types?",
          ["An intersection: A & B, or interface B extends A",
           "A union: A | B",
           "Object.assign at the type level",
           "Merge<A, B>"], 0,
          "An intersection requires BOTH sets of members. A union means 'one or the other', which is the opposite of combining."),
         ("What is `Record<string, number>`?",
          ["An object type with string keys and number values",
           "A tuple of a string and a number",
           "A Map with those types",
           "A union of string and number"], 0,
          "`Record` is a mapped type: `{ [P in K]: V }`. Note that a string-keyed Record loses literal key checking."),
         ("`Partial<T>` makes every property optional. What is its inverse?",
          ["Required<T>", "Complete<T>", "NonNullable<T>", "Readonly<T>"], 0,
          "`Required<T>` is `{ [K in keyof T]-?: T[K] }` — the `-?` strips the optional modifier the source type had.")]),
])


TS_EXAMS.update({
    14: _ts_exam(
        "Safe lookup table",
        "The input is `n` then `n` lines of `key value`, then a final line of keys to look up. Treat every index and map access as possibly missing. Print `key=value` or `key=(missing)` per query, then how many queries missed.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const table = new Map<string, string>();
for (let i = 1; i <= n; i++) {
  const parts = (lines[i] ?? "").trim().split(/\\s+/);
  const key: string | undefined = parts[0];
  const value: string | undefined = parts[1];
  if (key !== undefined && value !== undefined) table.set(key, value);
}
let missed = 0;
for (const query of (lines[n + 1] ?? "").trim().split(/\\s+/)) {
  const found = table.get(query);
  if (found === undefined) missed++;
  console.log(query + "=" + (found ?? "(missing)"));
}
console.log(missed);
''',
        [("2\na 1\nb 2\na b c", "a=1\nb=2\nc=(missing)\n1"),
         ("1\nk v\nk", "k=v\n0"),
         ("1\nk v\nx y", "x=(missing)\ny=(missing)\n2")],
        hint="Map.get returns T | undefined — compare against undefined explicitly rather than relying on truthiness, or an empty-string value looks missing."),

    15: _ts_exam(
        "Route table with satisfies",
        "Declare a route table (`home` → `/`, `about` → `/about`, `docs` → `/docs`) checked with `satisfies Record<string, string>`, derive the name union from it, and look up each of the `n` requested names. Print the path or `404`, then the number of routes.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const routes = {
  home: "/",
  about: "/about",
  docs: "/docs",
} satisfies Record<string, string>;
type RouteName = keyof typeof routes;
for (let i = 1; i <= n; i++) {
  const name = (lines[i] ?? "").trim();
  console.log(Object.hasOwn(routes, name) ? routes[name as RouteName] : "404");
}
console.log(Object.keys(routes).length);
''',
        [("3\nhome\ndocs\nnope", "/\n/docs\n404\n3"),
         ("1\nabout", "/about\n3"),
         ("2\nx\ny", "404\n404\n3")],
        hint="`satisfies` keeps the keys literal, so `keyof typeof routes` is the three names rather than plain string. Test membership with `Object.hasOwn` — `name in routes` is also true for `toString`, which every object inherits."),

    16: _ts_exam(
        "Branded money",
        "Brand `Cents` and `Dollars`. The input is `n` then `n` amounts in cents. Print the running total in cents after each, then the final total in dollars (cents / 100). Only a validating constructor may produce a branded value; reject negatives by printing `invalid` for that line and skipping it.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
declare const brand: unique symbol;
type Cents = number & { readonly [brand]: "Cents" };
type Dollars = number & { readonly [brand]: "Dollars" };
function toCents(raw: number): Cents | null {
  return Number.isInteger(raw) && raw >= 0 ? (raw as Cents) : null;
}
function toDollars(c: Cents): Dollars {
  return (c / 100) as Dollars;
}
let total = 0;
for (let i = 1; i <= n; i++) {
  const cents = toCents(Number((lines[i] ?? "").trim()));
  if (cents === null) {
    console.log("invalid");
    continue;
  }
  total += cents;
  console.log(total);
}
console.log(toDollars(total as Cents));
''',
        [("3\n120\n30\n-5", "120\n150\ninvalid\n1.5"),
         ("1\n100", "100\n1"),
         ("2\n0\n0", "0\n0\n0"),
         ("2\n250\n250", "250\n500\n5")],
        hint="Return `Cents | null` from the constructor so the caller must handle bad input; the cast inside it is the single place the brand is applied."),

    17: _ts_exam(
        "Merge intervals",
        "The input is `n` then `n` lines of `start end`. Merge every overlapping or touching interval and print the merged ones as `start end`, one per line sorted by start, then how many intervals were absorbed (input count minus output count).",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Interval = { start: number; end: number };
const intervals: Interval[] = [];
for (let i = 1; i <= n; i++) {
  const [start = 0, end = 0] = (lines[i] ?? "").trim().split(/\\s+/).map(Number);
  intervals.push({ start, end });
}
intervals.sort((a, b) => a.start - b.start);
const merged: Interval[] = [];
for (const current of intervals) {
  const last = merged[merged.length - 1];
  if (last !== undefined && current.start <= last.end) {
    last.end = Math.max(last.end, current.end);
  } else {
    merged.push({ ...current });
  }
}
for (const iv of merged) console.log(iv.start + " " + iv.end);
console.log(n - merged.length);
''',
        [("4\n1 3\n2 6\n8 10\n15 18", "1 6\n8 10\n15 18\n1"),
         ("2\n1 4\n4 5", "1 5\n1"),
         ("1\n5 7", "5 7\n0"),
         ("3\n1 10\n2 3\n4 5", "1 10\n2")],
        hint="Sort by start, then either extend the last merged interval or push a copy of the current one."),
})


TS_QUIZ_EXTRA.update({
    17: [
        ("What does `A & B` mean for two object types?",
         ["A value must satisfy BOTH — it has all members of A and of B",
          "A value must satisfy either one",
          "Only the shared members",
          "A is replaced by B"], 0,
         "Intersection combines requirements. It is unions that mean 'one or the other', which is the opposite of what people first expect from the & symbol."),
        ("What is `Exclude<\"a\" | \"b\" | \"c\", \"b\">`?",
         ["\"a\" | \"c\"", "\"b\"", "never", "\"a\" | \"b\" | \"c\""], 0,
         "`Exclude` filters a union with a distributive conditional type. `Omit` is the object-level cousin, built from Exclude and Pick."),
    ],
})


TS_EXAM_MORE_TESTS.update({
    14: [
        ('0\na', 'a=(missing)\n1'),
        ('3\nx 1\ny 2\nx 3\nx y', 'x=3\ny=2\n0'),
        ('2\na 1\nb\na b', 'a=1\nb=(missing)\n1'),
        ('1\nkey value\nkey key', 'key=value\nkey=value\n0'),
        ('2\np q\nr s\nr p z', 'r=s\np=q\nz=(missing)\n1'),
    ],
    15: [
        ('3\nhome\nabout\ndocs', '/\n/about\n/docs\n3'),
        ('1\nHOME', '404\n3'),
        ('2\ndocs\ndocs', '/docs\n/docs\n3'),
        ('1\ntoString', '404\n3'),
        ('0', '3'),
    ],
    16: [
        ('1\n-1', 'invalid\n0'),
        ('2\n12.5\n10', 'invalid\n10\n0.1'),
        ('3\n1\n2\n3', '1\n3\n6\n0.06'),
        ('1\n99999', '99999\n999.99'),
    ],
    17: [
        ('3\n8 10\n1 3\n2 6', '1 6\n8 10\n1'),
        ('2\n1 2\n3 4', '1 2\n3 4\n0'),
        ('3\n1 5\n1 5\n1 5', '1 5\n2'),
        ('4\n5 6\n1 2\n2 3\n6 7', '1 3\n5 7\n2'),
    ],
})
