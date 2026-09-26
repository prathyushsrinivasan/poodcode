# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New quiz kinds for the TypeScript Mastery weeks (TS_MASTERY_ROADMAP.md X-31):
#
#   _qm — multi-select: every index in `answers` is right, and a sitting only
#         counts the question right when exactly those options are picked.
#   _qt — fill-the-type: the learner types a type; it becomes
#         `type Answer = …` after the question's code, and the hidden claim
#         `Expect<Equal<Answer, target>>` must compile. `target` is written
#         against the code's own values (`typeof x`, `ReturnType<typeof f>`),
#         so the grade is what the compiler really infers — the model answer
#         is checked against it by both verifiers.
#
# Code-output questions (the third kind) are derived from chapter pitfalls in
# mastery_ts_derived.py. The UI is src/components/QuizChoices.tsx; the grading
# contract is in src/lib/quizKinds.ts. exec()'d before mastery_ts_attach.py.
# ---------------------------------------------------------------------------

import re as _qk_re

TS_QUIZ_KINDS = {}  # week -> [question]


def _qm(question, options, answers, explanation):
    assert len(answers) >= 2 and len(answers) < len(options), f"{question!r}: multi-select needs 2+ right and 1+ wrong"
    assert len(set(options)) == len(options), f"{question!r}: repeated option"
    return {"question": question, "options": list(options), "answer": answers[0], "answers": sorted(answers),
            "kind": "multi", "explanation": explanation}


def _qt(question, code, type_answer, target, explanation):
    # The UI rejects these words in a typed answer (TYPE_ANSWER_FORBID in
    # src/lib/quizKinds.ts); the model answer has to live by the same rule.
    assert not _qk_re.search(r"\b(typeof|ReturnType|Parameters|keyof)\b", type_answer), \
        f"{question!r}: the model answer uses a word the answer box bans"
    return {"question": question, "options": [type_answer], "answer": 0, "kind": "type",
            "code": code.strip("\n") + "\n", "type_answer": type_answer,
            "harness": _TW_PRELUDE + f"type _Check = Expect<Equal<Answer, {target}>>;\n",
            "explanation": explanation}


TS_QUIZ_KINDS[1] = [
    _qm("Which declarations infer a literal type rather than a widened one?",
        ['const a = "x"', "const b = 42", 'let c = "x"', "let d: number = 42"], [0, 1],
        "A `const` can never be reassigned, so a primitive initializer keeps its literal type. `let` widens to `string`/`number`, and an annotation always wins."),
    _qm('Which values does `typeof` report as "object" at runtime?',
        ["null", "[1, 2]", "new Date()", "undefined", "() => 1"], [0, 1, 2],
        '`typeof null` is "object" (a historic bug), arrays and dates are objects; `undefined` is "undefined" and a function is "function".'),
    _qt("Write the type TypeScript infers for `retries`.",
        'const port = 8080;\nlet retries = 3;\nconst label = "api";', "number", "typeof retries",
        "`let` widens the literal `3` to `number`, because the variable may be reassigned later."),
    _qt("Write the type TypeScript infers for `config`.",
        'const config = { host: "localhost", port: 8080, secure: false };',
        "{ host: string; port: number; secure: boolean }", "typeof config",
        "Object properties are mutable, so each one widens — even inside a `const` object. Only `as const` keeps the literals."),
]

TS_QUIZ_KINDS[2] = [
    _qm("Which expressions evaluate to `true`?",
        ["null == undefined", '0 == ""', "NaN === NaN", "Object.is(NaN, NaN)"], [0, 1, 3],
        '`==` treats null and undefined as equal and coerces `""` to 0. `NaN` is never `===` to anything, itself included; `Object.is` is the one comparison that says two NaNs are the same.'),
    _qm("Which values are falsy?",
        ["0", '""', '"0"', "[]", "NaN"], [0, 1, 4],
        'The falsy values are `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` and `NaN`. The string `"0"` and an empty array are both truthy.'),
    _qt("Write the type TypeScript infers for `size`.",
        'const n = Math.random();\nconst size = n > 0.5 ? "big" : "small";', '"big" | "small"', "typeof size",
        "Each branch of the conditional is a literal, and a `const` keeps literals, so the result is the union of the two."),
    _qt("Write the type TypeScript infers for `name`.",
        'declare const input: string | undefined;\nconst name = input ?? "guest";', "string", "typeof name",
        '`??` removes `undefined` from the left side and adds the right side: `string | "guest"`, which is just `string`.'),
]

TS_QUIZ_KINDS[3] = [
    _qm('Which of these produce the string "3.14"?',
        ["(3.14159).toFixed(2)", "String(Math.round(3.14159 * 100) / 100)",
         "Math.floor(3.14159 * 100) / 100", "(3.14159).toPrecision(3)"], [0, 1, 3],
        "`toFixed` and `toPrecision` return strings, and so does `String(…)`. `Math.floor(…) / 100` is the number 3.14, not a string."),
    _qm("Which of these give you each element of `xs` (not its index) as `x`?",
        ["for (const x of xs)", "for (const x in xs)", "xs.forEach((x) => { … })", "for (const [x] of xs.entries())"],
        [0, 2],
        "`for…of` and `forEach` hand over values. `for…in` walks the keys (as strings), and `entries()` yields `[index, value]` pairs, so `[x]` is the index."),
    _qt("Write the type TypeScript infers for `report`.",
        "const scores = [90, 72, 85];\nconst best = Math.max(...scores);\nconst report = best.toFixed(1);",
        "string", "typeof report",
        "`toFixed` formats a number as text; the result is a `string`, not a number."),
    _qt("Write the type TypeScript infers for `firstBig`.",
        "const nums = [4, 8, 15];\nconst firstBig = nums.find((n) => n > 10);", "number | undefined", "typeof firstBig",
        "`find` returns `undefined` when nothing matches, and the type says so — you have to handle the miss."),
]

TS_QUIZ_KINDS[4] = [
    _qm("Which of these calls on a `string` `s` return a `string`?",
        ['s.split(",")', "s.at(0)", "s.slice(1)", "s.charAt(0)", "s.match(/a/)"], [2, 3],
        "`split` returns `string[]`, `at` returns `string | undefined` (the index may be out of range) and `match` returns a match array or `null`. `slice` and `charAt` always return a string."),
    _qm('`const s = "héllo"`, written with a single precomposed é. Which expressions equal 5?',
        ["s.length", "[...s].length", 's.normalize("NFD").length', "Array.from(s).length"], [0, 1, 3],
        "A precomposed é is one code unit, so all the plain counts are 5. NFD splits it into `e` plus a combining accent, which makes 6."),
    _qt("Write the type TypeScript infers for `m`.",
        'const m = "2026-09-27".match(/^(\\d{4})-(\\d{2})/);', "RegExpMatchArray | null", "typeof m",
        "A regex may not match, so `match` returns `RegExpMatchArray | null` — narrow it before reading the groups."),
    _qt("Write the type TypeScript infers for `lens`.",
        'const words = "a b c".split(" ");\nconst lens = words.map((w) => w.length);', "number[]", "typeof lens",
        "`split` gives `string[]`, and mapping each string to its `length` gives `number[]`."),
]

TS_QUIZ_KINDS[5] = [
    _qm("Which declarations let `greet()` be called with no arguments?",
        ["function greet(name?: string) {}", 'function greet(name = "you") {}',
         "function greet(name: string | undefined) {}", "function greet(...names: string[]) {}"], [0, 1, 3],
        "An optional parameter, a default and a rest parameter can all be left out. A parameter typed `string | undefined` still has to be passed — even if you pass `undefined`."),
    _qm("Which statements about closures are true?",
        ["A closure keeps the variables it captures alive after the outer function returns",
         "Each call of the outer function makes a fresh set of captured variables",
         "A closure captures a copy of each variable's value when it is created",
         "`let` in a `for` header gives each iteration its own binding"], [0, 1, 3],
        "Closures capture variables, not values — a later change is visible. Each call makes new variables, and `let` in a loop header makes one per iteration, which is why loop closures work with `let` and not `var`."),
    _qt("Write the type TypeScript infers for `next`.",
        "function makeCounter(start = 0) {\n  let n = start;\n  return () => ++n;\n}\nconst next = makeCounter();",
        "() => number", "typeof next",
        "`makeCounter` returns an arrow with no parameters that returns `++n`, a number."),
    _qt("Write the return type TypeScript infers for `pick`.",
        "function pick(xs: string[], i?: number) {\n  return i === undefined ? xs : xs[i];\n}",
        "string | string[]", "ReturnType<typeof pick>",
        "The two branches return the whole array or one element, so the inferred return type is the union of both."),
]

TS_QUIZ_KINDS[6] = [
    _qm("Which of these are higher-order functions?",
        ["Array.prototype.map", "(f: () => void) => f()", "(n: number) => n * 2", "setTimeout"], [0, 1, 3],
        "A higher-order function takes or returns a function. `map`, the wrapper and `setTimeout` all take one; doubling a number takes and returns plain numbers."),
    _qm("Which calls return `[2, 4]`?",
        ["[1, 2].map((x) => x * 2)", "[1, 2].flatMap((x) => [x * 2])", "[1, 2].forEach((x) => x * 2)",
         "[1, 2, 3, 4].filter((x) => x % 2 === 0)"], [0, 1, 3],
        "`forEach` returns `undefined` whatever its callback returns — it is for side effects, never for building a result."),
    _qt("Write the type TypeScript infers for `results`.",
        "const apply = (f: (n: number) => number, n: number) => f(n);\n"
        "const results = [1, 2, 3].map((n) => apply((x) => x * 10, n) > 15);",
        "boolean[]", "typeof results",
        "The callback returns a comparison, a `boolean`, so `map` builds `boolean[]`."),
    _qt("Write the type TypeScript infers for `run`.",
        "function sum(xs: number[]): number {\n  return xs.length === 0 ? 0 : xs[0] + sum(xs.slice(1));\n}\n"
        "const run = (xs: number[]) => [sum(xs), xs.length];",
        "(xs: number[]) => number[]", "typeof run",
        "An array literal is inferred as an array, not a tuple: `[sum(xs), xs.length]` is `number[]`. Say `as const` or annotate a tuple if you mean a pair."),
]

TS_QUIZ_KINDS[7] = [
    _qm("Which methods leave the original array unchanged?",
        ["toSorted", "sort", "toReversed", "splice", "with"], [0, 2, 4],
        "The ES2023 copying methods — `toSorted`, `toReversed`, `toSpliced`, `with` — return a new array. `sort` and `splice` change the array in place."),
    _qm('With `const t: [string, number] = ["a", 1]`, which lines are compile errors?',
        ["t[2]", "t.push(2)", "const [a, b, c] = t", "t[0].toUpperCase()"], [0, 2],
        "Reading past a tuple's length is TS2493, in an index or a destructuring. `push` is allowed — a known hole in mutable tuples, and a reason to make them `readonly`."),
    _qt("Write the type TypeScript infers for `swapped`.",
        'const entry: [string, number] = ["x", 1];\nconst [key, value] = entry;\nconst swapped = [value, key];',
        "(string | number)[]", "typeof swapped",
        "Destructuring keeps the element types, but a new array literal widens to an array of the union — not the tuple `[number, string]`."),
    _qt("Write the type TypeScript infers for `flat`.",
        "const grid = [[1, 2], [3, 4]];\nconst flat = grid.flat();", "number[]", "typeof flat",
        "`flat()` removes one level of nesting: `number[][]` becomes `number[]`."),
]

TS_QUIZ_KINDS[8] = [
    _qm('Which declarations allow `scores["anyName"] = 3`?',
        ["const scores: Record<string, number> = {};", "const scores: { [name: string]: number } = {};",
         "const scores = {};", "const scores: Map<string, number> = new Map();"], [0, 1],
        "Only an index signature (or `Record<string, …>`, which is one) accepts any string key. `{}` has no keys at all, and a `Map` is read and written with `get`/`set`, not brackets."),
    _qm("What does `JSON.stringify` drop or change?",
        ["undefined properties are left out", "a Date becomes a string", "a Map becomes {}", "NaN becomes null",
         "nested objects are left out"], [0, 1, 2, 3],
        "JSON has no undefined, Date, Map or NaN. Dates go through `toJSON`, a Map has no enumerable own properties, and NaN is written as `null`. Nested plain objects serialise fine."),
    _qt("Write the type TypeScript infers for `rest`.",
        'const user = { id: 7, name: "Ada", tags: ["admin"] };\nconst { tags, ...rest } = user;',
        "{ id: number; name: string }", "typeof rest",
        "A rest element in object destructuring collects every property not named before it — here `id` and `name`."),
    _qt("Write the type TypeScript infers for `raw`.",
        "const raw = JSON.parse('{\"n\": 1}');", "any", "typeof raw",
        "`JSON.parse` returns `any`, which silently switches checking off. Annotate the result as `unknown` and validate it."),
]

TS_QUIZ_KINDS[9] = [
    _qm("Which are true of a Map, compared with a plain object used as a dictionary?",
        ["Any value can be a key, including objects", "It has a size property",
         "JSON.stringify serialises its entries", "It iterates in insertion order"], [0, 1, 3],
        "Maps take any key, know their size and iterate in insertion order. `JSON.stringify(map)` is `{}` — convert with `Object.fromEntries` first."),
    _qm("Which are true for `const s = new Set([1, 2, 2, 3])`?",
        ["s.size === 3", "s.has(2)", "s.size === 4", "[...s].length === 3"], [0, 1, 3],
        "A Set keeps one copy of each value, so the duplicate 2 is dropped: three values."),
    _qt("Write the type TypeScript infers for `got`.",
        "const byLen = new Map<number, string[]>();\nconst got = byLen.get(3);", "string[] | undefined", "typeof got",
        "`get` returns `undefined` for a missing key, so the value type always comes back with `| undefined`."),
    _qt("Write the type TypeScript infers for `list`.",
        'const seen = new Set(["a", "b"]);\nconst list = [...seen].map((s) => s.length);', "number[]", "typeof list",
        "The Set is `Set<string>`; spreading it gives `string[]`, and mapping to lengths gives `number[]`."),
]

TS_QUIZ_KINDS[10] = [
    _qm('Which declarations give `mode` the literal type `"dark"` rather than `string`?',
        ['const mode = "dark";', 'let mode = "dark" as const;', 'let mode = "dark";',
         'const mode: string = "dark";'], [0, 1],
        "`const` keeps the literal, and `as const` does so even on a `let`. A plain `let` widens, and an annotation says exactly what you wrote."),
    _qm('Given `type Level = "low" | "high" | number`, which assignments compile?',
        ['const a: Level = "low";', "const b: Level = 3;", 'const c: Level = "medium";', 'const d: Level = "high";'],
        [0, 1, 3],
        "Any number fits, and only the two listed strings do. `\"medium\"` is TS2322."),
    _qt("Write the type TypeScript infers for `pick`.",
        'const SIZES = ["S", "M", "L"] as const;\nconst pick = SIZES[1];', '"M"', "typeof pick",
        "`as const` makes a readonly tuple of literals, so a constant index reads the exact literal at that position."),
    _qt("Write the type TypeScript infers for `copy`.",
        'const status = Math.random() > 0.5 ? "ok" : 404;\nlet copy = status;', "string | number", "typeof copy",
        "`status` keeps the literals `\"ok\" | 404`, but copying them into a `let` widens each one: `string | number`."),
]

TS_QUIZ_KINDS[11] = [
    _qm("Inside `if (x) { … }`, where `x: string | number | null | undefined`, which types can `x` still have?",
        ["string", "number", "null", "undefined"], [0, 1],
        "Truthiness removes `null` and `undefined`. It does not remove `string` or `number` — the narrowed `x` may still be a non-empty string or a non-zero number."),
    _qm("Which of these treat `0` as a present value?",
        ["??", "||", "?.", "??="], [0, 2, 3],
        "`??`, `?.` and `??=` only react to `null` and `undefined`. `||` reacts to every falsy value, so it replaces a real 0."),
    _qt("Write the return type TypeScript infers for `f`.",
        "declare const v: string | number | undefined;\nfunction f() {\n"
        '  if (typeof v === "string") return v.length;\n  return v ?? -1;\n}',
        "number", "ReturnType<typeof f>",
        "Both returns are numbers: `v.length`, and `v ?? -1` once the string case is gone."),
    _qt("Write the type TypeScript infers for `texts`.",
        "function isText(x: unknown): x is string {\n  return typeof x === \"string\";\n}\n"
        'const mixed: unknown[] = ["a", 1, "b"];\nconst texts = mixed.filter(isText);',
        "string[]", "typeof texts",
        "`filter` has an overload for type predicates: passing `isText` narrows the result to `string[]`."),
]

TS_QUIZ_KINDS[12] = [
    _qm("Which of these types can hold any value at all?",
        ["unknown", "any", "{}", "object"], [0, 1],
        "`unknown` and `any` are the two top types. `{}` excludes `null` and `undefined`, and `object` excludes every primitive."),
    _qm("Which make a `switch` over a discriminated union fail to compile when a case is missing?",
        ["a default branch doing `const _x: never = s`",
         "a declared return type, with every case returning and no default",
         "a default branch that throws `new Error(\"?\")`",
         "an `assertNever(s)` call in the default branch"], [0, 1, 3],
        "A missing case leaves a member for `never` to reject, or a path that returns nothing (TS2366). A default that just throws satisfies the compiler and hides the gap until runtime."),
    _qt("Write the return type TypeScript infers for `other`.",
        'type Shape = { kind: "circle"; r: number } | { kind: "square"; side: number };\n'
        'declare const s: Shape;\nfunction other() {\n  if (s.kind === "circle") return "round";\n  return s;\n}',
        '"round" | { kind: "square"; side: number }', "ReturnType<typeof other>",
        "After the `circle` branch returns, `s` is narrowed to the square member — and the function returns either that or the literal."),
    _qt("Write the type of `kinds`.",
        'type Ev = { type: "click"; x: number } | { type: "key"; key: string } | { type: "quit" };\n'
        "declare const e: Ev;\nconst kinds = e.type;",
        '"click" | "key" | "quit"', "typeof kinds",
        "Reading a property every member has gives the union of its types — for the tag, the union of the literals."),
]

TS_QUIZ_KINDS[13] = [
    _qm("A function `f` has type `(n: number) => string`. To which of these types can `f` be assigned?",
        ["(n: number) => string", "(n: number, extra: boolean) => string", "() => string",
         "(n: number) => unknown"], [0, 1, 3],
        "A function may ignore extra arguments, and a `string` result is fine where `unknown` is expected. It cannot go where callers pass no argument at all — it needs its `n`."),
    _qm("Which pairs does `Equal<A, B>` consider the same type?",
        ["string | number  and  number | string", "any  and  unknown", "readonly string[]  and  string[]",
         "1 | never  and  1"], [0, 3],
        "Union order does not matter and `never` vanishes from a union. `any` is not `unknown`, and `readonly` is part of the type."),
    _qt("Write the type TypeScript infers for `handler`.",
        "const handler = (e: { key: string }, repeat = false) => e.key.length + (repeat ? 1 : 0);",
        "(e: { key: string }, repeat?: boolean) => number", "typeof handler",
        "A parameter with a default is optional to callers, so it shows up as `repeat?: boolean`."),
    _qt("Write the type TypeScript infers for `out`.",
        "function parse(x: string): number;\nfunction parse(x: number): string;\n"
        "function parse(x: string | number): string | number {\n"
        '  return typeof x === "string" ? Number(x) : String(x);\n}\nconst out = [parse("1"), parse(2)];',
        "(string | number)[]", "typeof out",
        "Each call picks its overload — `number`, then `string` — and the array literal is an array of the union."),
]

TS_QUIZ_KINDS[14] = [
    _qm("Which of these are erasable — removed by type stripping with no JavaScript generated?",
        ["interface User { id: number }", "x as string", "enum Color { Red }",
         "constructor(private id: number) {}", 'import type { T } from "./t";'], [0, 1, 4],
        "Interfaces, assertions and type-only imports simply disappear. `enum` and parameter properties generate code, so Node's type stripping rejects them."),
    _qm("Which options does `strict: true` switch on?",
        ["strictNullChecks", "noImplicitAny", "noUncheckedIndexedAccess", "strictFunctionTypes",
         "exactOptionalPropertyTypes"], [0, 1, 3],
        "`strict` is a family: null checks, implicit any, function types, bind/call/apply, class field init and more. `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes` must be turned on separately."),
    _qt("Write the type TypeScript infers for `label`.",
        "declare function formatBytes(n: number, opts?: { binary?: boolean }): string;\n"
        "declare const VERSION: string;\nconst label = [VERSION, formatBytes(1024)] as const;",
        "readonly [string, string]", "typeof label",
        "Declarations give the types without bodies; `as const` turns the array into a readonly tuple."),
    _qt("With `noUncheckedIndexedAccess` on (as it is from week 14), write the type of `port`.",
        'const argv = ["--port", "8080"];\nconst port = argv[1];', "string | undefined", "typeof port",
        "The flag makes every index read into an array say it may be missing: `string | undefined`."),
]

TS_QUIZ_KINDS[15] = [
    _qm('Which keep the literal type of `mode` in `{ mode: "dark" }` while still checking the object against `Theme`?',
        ["{ … } satisfies Theme", "{ … } as Theme", "an annotation `: Theme`", "{ … } as const satisfies Theme"],
        [0, 3],
        "`satisfies` checks without changing the inferred type. `as` and an annotation replace it with `Theme`, where `mode` is the whole union."),
    _qm("With `type Point = { x: number; y: number }`, which lines compile?",
        ["const p: Point = { x: 1, y: 2 };", "const q = { x: 1, y: 2, z: 3 }; const p: Point = q;",
         "const p: Point = { x: 1, y: 2, z: 3 };", "const p: Point = { x: 1 };"], [0, 1],
        "Structural typing lets extra properties through — except on a fresh object literal, where the excess property check (TS2353) catches a likely typo. A missing `y` is always an error."),
    _qt("Write the type TypeScript infers for `m`.",
        'const theme = { mode: "dark", accent: "#08f" } satisfies { mode: "dark" | "light"; accent: string };\n'
        "const m = theme.mode;",
        '"dark"', "typeof m",
        "Checked against a union of literals, the property keeps its literal type — `satisfies` does not widen it to the annotation."),
    _qt("Write the type TypeScript infers for `found`.",
        "const found = [1, 2, 3].find((n) => n > 1)!;", "number", "typeof found",
        "The non-null assertion `!` removes `undefined` from the type — a promise you make, not a check the compiler does."),
]

TS_QUIZ_KINDS[16] = [
    _qm("Which declarations make `xs.push(4)` a compile error?",
        ["const xs: readonly number[] = [1];", "const xs: ReadonlyArray<number> = [1];", "const xs = [1] as const;",
         "const xs = Object.freeze([1]);", "const xs = [1];"], [0, 1, 2, 3],
        "Readonly arrays have no `push`. `Object.freeze` is typed to return a readonly array too. A `const` binding still allows mutating the array itself."),
    _qm('Which are true of `type UserId = string & { readonly __brand: "UserId" }`?',
        ["A plain string is not assignable to it", "It costs nothing at runtime",
         "A UserId is still usable where a string is expected", "The brand property exists on the value at runtime"],
        [0, 1, 2],
        "The brand exists only in the type system: values are plain strings, so they work anywhere a string does, while an unbranded string needs a checked constructor to become one."),
    _qt("Write the type TypeScript infers for `inner`.",
        "const base = { a: 1, b: [2, 3] } as const;\nconst inner = base.b;", "readonly [2, 3]", "typeof inner",
        "`as const` applies all the way down: nested arrays become readonly tuples of literals."),
    _qt("Write the type TypeScript infers for `prices`.",
        'type Cents = number & { readonly __brand: "Cents" };\n'
        "const toCents = (n: number) => Math.round(n * 100) as Cents;\nconst prices = [1.5, 2].map(toCents);",
        "Cents[]", "typeof prices",
        "`map` keeps whatever the callback returns, brand included."),
]

TS_QUIZ_KINDS[17] = [
    _qm("With `type U = { id: number; name: string }`, which produce `{ id?: number; name?: string }`?",
        ["Partial<U>", 'Pick<Partial<U>, "id" | "name">', "Required<U>", "Readonly<U>"], [0, 1],
        "`Pick` over a `Partial` keeps the `?` modifiers — mapped types over `keyof` preserve them. `Required` removes them and `Readonly` adds `readonly` instead."),
    _qm("Which utilities work on the members of a union, rather than the keys of an object?",
        ["Exclude", "Extract", "Omit", "NonNullable", "Pick"], [0, 1, 3],
        "`Exclude`, `Extract` and `NonNullable` filter union members. `Omit` and `Pick` select object keys."),
    _qt("Write the type TypeScript infers for `d`.",
        "type Task = { id: number; title: string; done: boolean };\n"
        'declare const patch: Partial<Omit<Task, "id">>;\nconst d = patch.done;',
        "boolean | undefined", "typeof d",
        "`Partial` makes every remaining property optional, so reading one may give `undefined`."),
    _qt("Write the type of `k`.",
        'const handlers = { save: (id: number) => true, load: (path: string) => "data" };\n'
        "declare const k: keyof typeof handlers;",
        '"save" | "load"', "typeof k",
        "`keyof typeof` turns a value's keys into a union of string literals."),
]

TS_QUIZ_KINDS[18] = [
    _qm("Given `function first<T extends { length: number }>(x: T): T`, which calls compile?",
        ['first("abc")', "first([1, 2])", "first(42)", "first({ length: 3 })"], [0, 1, 3],
        "The constraint only asks for a numeric `length`: strings, arrays and that object have one; a number does not (TS2345)."),
    _qm("Which are good reasons to add a type parameter to a function?",
        ["The return type depends on an argument's type", "Two parameters must have the same type",
         "It makes the function run faster", "It is used exactly once, only in a parameter"], [0, 1],
        "A type parameter earns its place by relating types — input to output, or parameter to parameter. One used once relates nothing; plain `unknown` says the same thing."),
    _qt("Write the type TypeScript infers for `p`.",
        "function pair<A, B>(a: A, b: B) {\n  return [a, b] as const;\n}\nconst p = pair(\"x\", 1);",
        "readonly [string, number]", "typeof p",
        "An unconstrained type parameter infers the widened type of a literal argument: `A` is `string`, `B` is `number`."),
    _qt("Write the type TypeScript infers for `g`.",
        "function groupBy<T, K extends string>(xs: T[], key: (x: T) => K) {\n"
        "  const out = {} as Record<K, T[]>;\n  for (const x of xs) (out[key(x)] ??= []).push(x);\n  return out;\n}\n"
        'const g = groupBy([1, 2, 3], (n) => (n % 2 ? "odd" : "even"));',
        'Record<"odd" | "even", number[]>', "typeof g",
        "Because `K` is constrained to `string`, the literal keys are kept: the result is keyed by exactly `\"odd\" | \"even\"`."),
]

TS_QUIZ_KINDS[19] = [
    _qm('For `const colors = { red: "#f00", blue: "#00f" }`, which types are `"red" | "blue"`?',
        ["keyof typeof colors", "keyof colors", "Extract<keyof typeof colors, string>",
         "(typeof colors)[keyof typeof colors]"], [0, 2],
        "`keyof` works on a type, so it needs `typeof colors`; `keyof colors` is an error. Indexing by the keys gives the values' type, `string`."),
    _qm('Which give the element type of `const xs = [1, "a"]`?',
        ["(typeof xs)[number]", "(typeof xs)[0]", "(typeof xs) extends (infer E)[] ? E : never",
         "keyof typeof xs"], [0, 1, 2],
        "`xs` is an array, not a tuple, so any numeric index gives `string | number`, as does `infer`. `keyof` an array gives its method names and `number`."),
    _qt("Write the type TypeScript infers for `path`.",
        'const routes = { home: "/", user: "/users/:id" };\ntype R = typeof routes;\n'
        "declare const key: keyof R;\nconst path = routes[key];",
        "string", "typeof path",
        "Indexing with a union of keys gives the union of the value types — here both are `string`."),
    _qt("Write the type of `u`.",
        'const users = [{ id: 1, roles: ["admin"] }];\ndeclare const u: (typeof users)[number]["roles"][number];',
        "string", "typeof u",
        "Read it left to right: an element of `users`, its `roles`, an element of that — `string`."),
]

TS_QUIZ_KINDS[20] = [
    _qm("Which of these keep a property's `?` modifier from `T`?",
        ["{ [K in keyof T]: T[K] }", "{ [K in keyof T]-?: T[K] }", "{ [K in keyof T as K]: T[K] }",
         "Record<keyof T, number>"], [0, 2],
        "A mapped type over `keyof T` is homomorphic and copies modifiers, `as` clause or not. `-?` strips them, and `Record` builds fresh required keys."),
    _qm("Which remove the `readonly` modifier from `T`'s properties?",
        ["{ -readonly [K in keyof T]: T[K] }", "{ [K in keyof T]: T[K] }", "{ readonly [K in keyof T]: T[K] }",
         "{ -readonly [K in keyof T]-?: T[K] }"], [0, 3],
        "Only `-readonly` removes the modifier; a plain homomorphic mapping copies it, and `readonly` adds it."),
    _qt("Write the type of `f`, spelled out as an object type.",
        "type Flags<T> = { [K in keyof T]: boolean };\ndeclare const f: Flags<{ a: string; b?: number }>;",
        "{ a: boolean; b?: boolean }", "typeof f",
        "Every value type becomes `boolean`, and the homomorphic mapping keeps `b` optional."),
    _qt("Write the type of `g`, spelled out as an object type.",
        "type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };\n"
        "declare const g: Getters<{ name: string; age: number }>;",
        "{ getName: () => string; getAge: () => number }", "typeof g",
        "The `as` clause renames each key through a template literal; the value becomes a getter for the old one."),
]

TS_QUIZ_KINDS[21] = [
    _qm("Which of these distribute over a union type argument?",
        ["type A<T> = T extends string ? 1 : 2", "type B<T> = [T] extends [string] ? 1 : 2",
         "type C<T> = T extends unknown ? T[] : never", "type D<T> = T[]"], [0, 2],
        "Only a conditional type whose checked type is a naked type parameter distributes. Wrapping it in a tuple switches that off, and `T[]` is not conditional at all."),
    _qm("Which evaluate to `never`?",
        ['Exclude<"a" | "b", "a">', 'Extract<"a" | "b", "c">', "NonNullable<string | null>",
         "string & number", "keyof {}"], [1, 3, 4],
        "Nothing is extracted, no value is both a string and a number, and `{}` declares no keys. The others leave `\"b\"` and `string`."),
    _qt("Write the type of `x`.",
        "type ElementOf<T> = T extends readonly (infer E)[] ? E : T;\ndeclare const x: ElementOf<string[] | number>;",
        "string | number", "typeof x",
        "The conditional distributes: `string[]` gives `string`, `number` falls through unchanged."),
    _qt("Write the type of `v`.",
        "type Unwrap<T> = T extends Promise<infer V> ? Unwrap<V> : T;\n"
        "declare const v: Unwrap<Promise<Promise<boolean>>>;",
        "boolean", "typeof v",
        "The recursion peels one `Promise` per step until it reaches a type that is not one."),
]

TS_QUIZ_KINDS[22] = [
    _qm("Which strings are assignable to `` `v${number}.${number}` ``?",
        ['"v1.2"', '"v10.0"', '"v.1"', '"v1.x"'], [0, 1],
        "Each `${number}` must match text that parses as a number. An empty major version and `x` do not."),
    _qm("Which intrinsic string-manipulation types does TypeScript provide?",
        ["Uppercase", "Capitalize", "Uncapitalize", "Titlecase", "Lowercase"], [0, 1, 2, 4],
        "There are four: `Uppercase`, `Lowercase`, `Capitalize` and `Uncapitalize`."),
    _qt("Write the type of `h`.",
        'type Evt = "click" | "focus";\ndeclare const h: `on${Capitalize<Evt>}`;',
        '"onClick" | "onFocus"', "typeof h",
        "A template literal type distributes over a union in a placeholder, one result per member."),
    _qt("Write the type of `p`.",
        "type Join<T extends string[]> = T extends [infer H extends string, ...infer R extends string[]]\n"
        "  ? R extends [] ? H : `${H}.${Join<R>}`\n  : \"\";\n"
        'declare const p: Join<["a", "b", "c"]>;',
        '"a.b.c"', "typeof p",
        "Each step takes the head and joins it to the joined rest, until the rest is empty."),
]

TS_QUIZ_KINDS[23] = [
    _qm('Given `class Acct { #bal = 0; private owner = "x"; static count = 0; readonly id = 1 }` and `const a = new Acct()`, which lines compile outside the class?',
        ["a.id", "a.owner", "Acct.count", "a.#bal", "(a as any).owner"], [0, 2, 4],
        "`private` is a compile-time rule that `any` walks straight past; `#bal` is private at runtime too and cannot even be named outside. `readonly` fields can be read and statics live on the class."),
    _qm("Which are true of `implements`?",
        ["It checks the class has the interface's members", "It adds the interface's methods to the class",
         "A class can implement several interfaces", "It changes the class's runtime prototype"], [0, 2],
        "`implements` is a check only: it adds nothing, generates nothing, and a class may list many interfaces."),
    _qt("Write the type TypeScript infers for `s`.",
        "class Stack {\n  private items: number[] = [];\n  push(n: number) {\n    this.items.push(n);\n    return this;\n  }\n}\n"
        "const s = new Stack().push(1).push(2);",
        "Stack", "typeof s",
        "Returning `this` gives the polymorphic `this` type, which on a `Stack` instance is `Stack` — so calls chain."),
    _qt("Write the type TypeScript infers for `reading`.",
        "class Temp {\n  #c = 0;\n  get f() {\n    return (this.#c * 9) / 5 + 32;\n  }\n"
        "  set f(v: number) {\n    this.#c = ((v - 32) * 5) / 9;\n  }\n}\nconst reading = new Temp().f;",
        "number", "typeof reading",
        "An accessor reads like a property: `f` is a `number`, not a function."),
]

TS_QUIZ_KINDS[24] = [
    _qm("Which of these are iterable (usable with `for…of`)?",
        ['"abc"', "new Map()", "{ a: 1 }", "new Set([1])", "[1, 2].entries()"], [0, 1, 3, 4],
        "Strings, Maps, Sets and array iterators all implement `Symbol.iterator`. A plain object does not — use `Object.entries` to walk it."),
    _qm("Which are true of a generator function?",
        ["Calling it runs none of its body until next() is called", "Calling it returns an iterator",
         "A return inside it ends the iteration", "It can only yield numbers"], [0, 1, 2],
        "A generator is lazy: the call builds a paused iterator. Each `next()` runs to the next `yield`; `return` finishes it. It can yield anything."),
    _qt("Write the type TypeScript infers for `it`.",
        'function* count(n: number) {\n  for (let i = 0; i < n; i++) yield i;\n  return "done";\n}\nconst it = count(3);',
        "Generator<number, string, unknown>", "typeof it",
        "A generator's type records what it yields, what it returns, and what `next()` accepts — here `number`, `string`, and nothing in particular."),
    _qt("Write the type of `total`.",
        "const total = [3, 1, 2].values().reduce((a, b) => a + b, 0);",
        "number", "typeof total",
        "Iterator helpers mirror the array methods: `reduce` with a numeric seed folds the values into a `number`."),
]

TS_QUIZ_KINDS[25] = [
    _qm("Under `strict`, which make `e.message` safe to read inside `catch (e)`?",
        ["if (e instanceof Error)", "catch (e: Error)",
         'if (typeof e === "object" && e !== null && "message" in e)', "(e as Error)"], [0, 2],
        "A caught value is `unknown`: narrow it. Annotating it as `Error` is not allowed (TS1196), and `as Error` compiles but proves nothing — a thrown string has no message."),
    _qm("Which are true of `using`?",
        ["disposal runs when the block exits, even on a throw",
         "resources are disposed in reverse order of declaration",
         "it works with any object that has a close() method", "the resource needs a [Symbol.dispose] method"],
        [0, 1, 3],
        "`using` calls `[Symbol.dispose]()` at scope exit, last declared first. A `close()` method alone is not enough."),
    _qt("Write the type TypeScript infers for `out`.",
        "type Result<T> = { ok: true; value: T } | { ok: false; error: string };\n"
        "function parseAge(s: string): Result<number> {\n  const n = Number(s);\n"
        '  return Number.isInteger(n) ? { ok: true, value: n } : { ok: false, error: "not a number" };\n}\n'
        'const r = parseAge("7");\nconst out = r.ok ? r.value : r.error;',
        "string | number", "typeof out",
        "Checking `ok` narrows each branch to its member: a `number` value or a `string` error."),
    _qt("Write the type TypeScript infers for `c`.",
        'const err = new Error("load failed", { cause: 404 });\nconst c = err.cause;', "unknown", "typeof c",
        "`cause` can be anything at all, so it is typed `unknown` — narrow it before use."),
]

TS_QUIZ_KINDS[26] = [
    _qm("Which of these run from the microtask queue?",
        ["a .then callback", "the code after an await", "a setTimeout(fn, 0) callback", "queueMicrotask(fn)"],
        [0, 1, 3],
        "Promise reactions (including resuming after `await`) and `queueMicrotask` are microtasks. Timers are macrotasks and wait until the microtask queue is empty."),
    _qm("Which are true of an `async` function?",
        ["It always returns a Promise", "A throw inside it becomes a rejected promise",
         "Its body runs synchronously up to the first await", "It runs on another thread"], [0, 1, 2],
        "An async function is ordinary code on the same thread, wrapped so that its result — or its exception — arrives as a promise."),
    _qt("Write the type TypeScript infers for `p`.",
        'async function load(id: number) {\n  if (id < 0) return null;\n  return { id, name: "n" + id };\n}\nconst p = load(1);',
        "Promise<{ id: number; name: string } | null>", "typeof p",
        "An async function wraps the union of everything it returns in a single `Promise`."),
    _qt("Write the type TypeScript infers for `both`.",
        "declare const a: Promise<number>;\ndeclare const b: Promise<string>;\nconst both = Promise.all([a, b]);",
        "Promise<[number, string]>", "typeof both",
        "`Promise.all` over a tuple of promises resolves to a tuple of their values, position by position."),
]

for _qk_week, _qk_list in TS_QUIZ_KINDS.items():
    _qk_strict = _week_strictness(_qk_week)
    for _qk in _qk_list:
        if _qk["kind"] == "type" and _qk_strict:
            _qk["strictness"] = _qk_strict
