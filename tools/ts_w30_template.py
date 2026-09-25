# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 30 — inference & template literal types.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief, _mk, _TYPE_PRELUDE) and every
# shared program prefix (_FS, _NUMS, _WORDS, _LINE) is already defined. This
# file only appends its week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# WHAT THE WEEK BUILDS ON: week 29's conditional types, `infer` and mapped types,
# plus week 19's `${r},${c}` string keys (this week gives such strings TYPES).
#
# EVERYTHING HERE WAS PROBED AGAINST THE CHECKER (TypeScript 5.9) FIRST, including
# the ones that look too clever to be true: a cartesian union from a template
# (`${"a"|"b"}-${1|2}` is four members), `infer N extends number` turning "42" into
# the literal 42, dotted object paths (`Paths<Config>` is "name" | "db" | "db.host"
# | "db.port"), and a `const` type parameter keeping `["a", "b"]` as a readonly
# tuple of literals.
#
# THE KEY-TYPE TRAP, shipped as a diagnose: `Capitalize<K>` with `K in keyof T` is
# TS2344, because `keyof T` may include number and symbol keys. `K & string` is the
# idiom, and the reason for it is the lesson.
#
# THE LIBRARY: Library #2 is the router TS_ROADMAP's decision 2 named — "a router
# whose paths are parsed by template literal types". A handler for
# "/users/:id/posts/:postId" receives `{ id: string; postId: string }`, computed from
# the string; reading `p.name` does not compile, and the capstone's harness proves
# it with a `@ts-expect-error` inside a function that never runs (week 29's device).
# The router stores routes type-erased, with one cast at `add` — the same "precise
# outside, careful inside" rule week 29 taught.
# ---------------------------------------------------------------------------

_PARAMS = (
    'type ParamNames<P extends string> =\n'
    '  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`>\n'
    '  : P extends `${string}:${infer Name}` ? Name\n'
    '  : never;\n'
    'type Params<P extends string> = { [K in ParamNames<P>]: string };\n'
)

_CFG = (
    'interface Config {\n'
    '  name: string;\n'
    '  db: { host: string; port: number };\n}\n'
)

_PATHS = (
    'type Paths<T> = T extends object\n'
    '  ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]\n'
    '  : never;\n'
    'type PathValue<T, P extends string> =\n'
    '  P extends `${infer K}.${infer R}` ? (K extends keyof T ? PathValue<T[K], R> : never)\n'
    '  : P extends keyof T ? T[P]\n'
    '  : never;\n'
)


# --- Week 30 --------------------------------------------------------------
_WEEKS.append(_week(
    30, 8, _M8,
    "Inference & Template Literal Types",
    "Strings get types too. Build them with template literals, take them apart with `infer`, and parse a route like \"/users/:id\" into the object its handler receives — at compile time.",
    """
Week 19 keyed a `Map` with strings like `"3,4"`. To the compiler those were just
`string`. This week they get **types with structure**.

## Template literal types

The template-literal syntax you have used for values since week 2 works on types:

```ts
type Px = `${number}px`;                       // "12px" ✓   "12em" ✗
type Cell = `${"a" | "b"}${1 | 2}`;            // "a1" | "a2" | "b1" | "b2"
type Handler = `on${Capitalize<"click">}`;     // "onClick"
```

Unions **multiply**, and four built-in helpers change case: `Uppercase`,
`Lowercase`, `Capitalize`, `Uncapitalize`.

## …and `infer` takes them apart

Week 29's `infer` works inside a template literal too — which makes it a **parser**:

```ts
type Head<S> = S extends `${infer H} ${string}` ? H : S;
type A = Head<"hello world">;                  // "hello"
```

Recursion (week 25, at the type level) lets it keep going: split on commas, trim
spaces, pull `:id` and `:postId` out of `"/users/:id/posts/:postId"`.

## Why anyone does this

Because then a **string argument can decide a type**:

```ts
router.add("/users/:id/posts/:postId", (p) => p.postId);   // p: { id: string; postId: string }
router.add("/users/:id", (p) => p.name);                   // ✗ does not compile
```

That is the library module this week builds, and it is exactly how real routers,
ORMs and i18n libraries type their string APIs.

⏱️ Budget about **seven hours**.
""",
    objectives=[
        "Write template literal types, and predict how unions multiply inside them",
        "Change case with Uppercase, Lowercase, Capitalize and Uncapitalize",
        "Remap keys through a template, and say why `K & string` is needed",
        "Match and take apart strings with `infer` inside a template",
        "Write recursive string types: trim, split, replace",
        "Use `infer` in tuple positions, object properties, and with an `extends` constraint",
        "Parse route parameters out of a path string at the type level",
        "Type dotted object paths, and the value at a path",
        "Keep literal types alive with `as const` and `const` type parameters",
        "Give a runtime string API a type computed from its argument",
    ],
    why="String-typed APIs are everywhere — routes, event names, CSS values, translation keys, SQL-ish query builders — and template literal types are how modern libraries make them safe. Being able to read (and occasionally write) the types behind `router.get(\"/users/:id\", …)` is what separates using a typed library from being surprised by it.",
    est_minutes=420,
    glossary=[
        _gloss("template literal type", "`prefix${T}suffix` at the type level. Unions inside it multiply."),
        _gloss("intrinsic string types", "Uppercase, Lowercase, Capitalize, Uncapitalize — case changes built into the compiler."),
        _gloss("K & string", "Narrows a key type to its string members, so it can go inside a template."),
        _gloss("pattern match", "S extends `${infer A}-${infer B}` — split S at the first '-'."),
        _gloss("recursive string type", "A string type that calls itself on the rest — trim, split, replace."),
        _gloss("variadic tuple", "[...unknown[], infer L] — match the LAST element of any tuple."),
        _gloss("infer … extends", "infer N extends number — infer, and only accept it if it matches the constraint."),
        _gloss("path type", "\"db\" | \"db.host\" — every dotted path into an object, as a union."),
        _gloss("widening", "`let m = \"GET\"` is typed string, not \"GET\" — the literal is lost."),
        _gloss("const type parameter", "function f<const T>(x: T) — infer T as narrowly as `as const` would."),
    ],
    cheatsheet="""
```ts
// ---- building strings ----------------------------------------------------
type Px = `${number}px`;
type Cell = `${"a" | "b"}${1 | 2}`;                   // a1 | a2 | b1 | b2
type OnEvent<E extends string> = `on${Capitalize<E>}`;
type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };
//                                                  ^^^^^^^^^^ keyof may hold number | symbol

// ---- taking them apart -----------------------------------------------------
type StartsWith<S extends string, P extends string> = S extends `${P}${string}` ? true : false;
type TrimLeft<S extends string> = S extends ` ${infer R}` ? TrimLeft<R> : S;
type Split<S extends string, D extends string> =
  S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S];

// ---- infer, in depth ---------------------------------------------------------
type Last<T extends readonly unknown[]> = T extends readonly [...unknown[], infer L] ? L : never;
type ToNum<S extends string> = S extends `${infer N extends number}` ? N : never;   // "42" → 42
type DataOf<T> = T extends { data: infer D } ? D : never;

// ---- a route's parameters ------------------------------------------------------
type ParamNames<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? Name
  : never;
type Params<P extends string> = { [K in ParamNames<P>]: string };

// ---- dotted paths -----------------------------------------------------------------
type Paths<T> = T extends object
  ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]
  : never;

// ---- keeping literals ----------------------------------------------------------------
const m = "GET";                       // "GET"      (let m = "GET" would be string)
const xs = ["a", "b"] as const;        // readonly ["a", "b"]
function tags<const T extends readonly string[]>(xs: T): T { return xs; }
```
""",
    self_check=[
        "Can you say how many members `${\"a\"|\"b\"}-${1|2|3}` has?",
        "Can you write an event-handler name type with Capitalize?",
        "Can you explain why `Capitalize<K>` needs `K & string` in a mapped type?",
        "Can you test whether a string type starts with a prefix?",
        "Can you write a recursive TrimLeft and Split?",
        "Can you get the last element of any tuple type?",
        "Can you turn \"42\" into the literal type 42?",
        "Can you extract the parameter names from \"/users/:id/posts/:postId\"?",
        "Can you list every dotted path of a nested object type?",
        "Can you say why `let method = \"GET\"` fails where `const` passes?",
        "Can you give a router handler a params type computed from its path?",
    ],
    review=[
        _q("`${\"a\" | \"b\"}-${1 | 2}` has how many members?",
           ["2", "4", "3", "1"], 1,
           "Unions multiply."),
        _q("`Capitalize<\"click\">` is…",
           ["\"CLICK\"", "\"Click\"", "\"click\"", "string"], 1,
           "First letter only."),
        _q("In `{ [K in keyof T as `get${Capitalize<K>}`]: … }`, the error is because…",
           ["Capitalize is wrong", "keyof T may include number and symbol keys", "T is unknown", "of the as"], 1,
           "Write K & string."),
        _q("`S extends `${infer H} ${string}` ? H : S` on \"hello big world\" gives…",
           ["\"hello big\"", "\"hello\"", "\"world\"", "never"], 1,
           "infer H takes the shortest match before the first space."),
        _q("A recursive string type needs…",
           ["a loop", "a case where it stops calling itself", "a Map", "infer twice"], 1,
           "Week 25, at the type level."),
        _q("`[...unknown[], infer L]` matches…",
           ["the first element", "the last element of any tuple", "an empty tuple", "arrays only"], 1,
           "A variadic tuple pattern."),
        _q("`infer N extends number` in `${infer N extends number}` turns \"42\" into…",
           ["number", "42", "\"42\"", "never"], 1,
           "The literal number."),
        _q("`ParamNames<\"/users/:id/posts/:postId\">` is…",
           ["string", "\"id\" | \"postId\"", "[\"id\", \"postId\"]", "never"], 1,
           "Parsed from the string."),
        _q("`let method = \"GET\"` has the type…",
           ["\"GET\"", "string", "any", "const"], 1,
           "let widens; const does not."),
        _q("A `const` type parameter makes `f([\"a\", \"b\"])` infer…",
           ["string[]", "readonly [\"a\", \"b\"]", "[string, string]", "any"], 1,
           "As if the caller had written as const."),
    ],
    milestone="Library #2 — the router. Register handlers against patterns like \"/users/:id/posts/:postId\"; each handler's parameter object is typed FROM the pattern string, so a handler that reads a parameter the path does not declare does not compile. At run time the router matches incoming paths segment by segment and calls the right handler, or reports a 404.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w30-template", "Strings with structure",
            "Template literal types, multiplying unions, and changing case.",
            """
```ts
type Px = `${number}px`;
const a: Px = "12px";      // ✓
const b: Px = "12em";      // ✗
```

A template literal **type** describes a set of strings. `${number}` matches any
numeric text; `${string}` matches anything.

## Unions multiply

```ts
type Row = "a" | "b";
type Col = 1 | 2 | 3;
type Cell = `${Row}${Col}`;     // six members: a1 a2 a3 b1 b2 b3
```

Every combination, like a nested loop. Useful — and a thing to watch: three unions of
ten members is a thousand-member type.

## Changing case

Four helpers are built into the compiler:

```ts
Uppercase<"get">       // "GET"
Lowercase<"GET">       // "get"
Capitalize<"click">    // "Click"
Uncapitalize<"Click">  // "click"
```

Together with templates, the classic:

```ts
type OnEvent<E extends string> = `on${Capitalize<E>}`;
type H = OnEvent<"click" | "focus">;     // "onClick" | "onFocus" — distributes, too
```

## Renaming keys — and the `& string`

Week 29's `as` clause can rename keys through a template:

```ts
type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };
```

Leave out `& string` and:

```
TS2344: Type 'K' does not satisfy the constraint 'string'.
```

`keyof T` can contain **number** and **symbol** keys, and you cannot capitalise a
symbol. `K & string` keeps only the string keys — the idiom you will see in every
library that does this.

> ⚠️ **Common mistakes:** `Capitalize<K>` without `& string`; expecting
> `Capitalize` to change more than the first letter; and building accidental
> thousand-member unions.
""",
            warmup=[
                _q("`${number}px` accepts…",
                   ["\"px\"", "\"12px\"", "\"12 px\"", "12"], 1,
                   "Numeric text, then px."),
                _q("`${\"x\"|\"y\"}${1|2|3}` has how many members?",
                   ["5", "6", "3", "2"], 1,
                   "2 × 3."),
                _q("`Uppercase<\"get\">` is…",
                   ["\"Get\"", "\"GET\"", "\"get\"", "string"], 1,
                   "Every letter."),
                _q("`K & string` in a key remap exists because…",
                   ["style", "keyof may include number and symbol keys", "Capitalize needs two", "of never"], 1,
                   "TS2344 otherwise."),
            ],
            exercises=[
                _types("tscourse-w30-tl-t1", "Every cell",
                       "Write `Cell` as every combination of a row letter and a column number.",
                       'type Row = "a" | "b";\n'
                       'type Col = 1 | 2;\n'
                       'type Cell = `${Row}${Col}`;\n',
                       '`${Row}${Col}`',
                       """
type _1 = Expect<Equal<Cell, "a1" | "a2" | "b1" | "b2">>;
""",
                       hints=["A template literal type with two placeholders.",
                              "Unions inside it multiply out.",
                              "`${Row}${Col}`"],
                       difficulty="Easy"),
                _types("tscourse-w30-tl-t2", "Handler names",
                       "Write `OnEvent<E>`: \"on\" followed by the event name with its first letter capitalised.",
                       'type OnEvent<E extends string> = `on${Capitalize<E>}`;\n',
                       '`on${Capitalize<E>}`',
                       """
type _1 = Expect<Equal<OnEvent<"click">, "onClick">>;
type _2 = Expect<Equal<OnEvent<"click" | "focus">, "onClick" | "onFocus">>;
""",
                       hints=["A template with the prefix \"on\".",
                              "Capitalize changes only the first letter.",
                              "`on${Capitalize<E>}`"],
                       difficulty="Easy"),
                _types("tscourse-w30-tl-t3", "Only pixel values",
                       "Write `Px` so that \"12px\" and \"0.5px\" are accepted and \"12em\" is not.",
                       'type Px = `${number}px`;\n',
                       '`${number}px`',
                       """
const _a: Px = "12px";
const _b: Px = "0.5px";
// @ts-expect-error — not pixels
const _c: Px = "12em";
""",
                       hints=["`${number}` matches numeric text.",
                              "`${number}px`"],
                       difficulty="Easy"),
                _types("tscourse-w30-tl-t4", "Getters for every key",
                       "Write `Getters<T>`: for each key `name`, a method `getName` returning that key's type.",
                       'type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };\n',
                       '{ [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] }',
                       """
type _1 = Expect<Equal<Getters<{ name: string; age: number }>, { getName: () => string; getAge: () => number }>>;
""",
                       hints=["Week 29's key remapping, with a template as the new key.",
                              "Only string keys can be capitalised: K & string.",
                              "{ [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] }"],
                       difficulty="Hard"),
                _diagnose("tscourse-w30-tl-d1", "The key that might be a symbol",
                          "TS2344: Type 'K' does not satisfy the constraint 'string'.",
                          'interface Person {\n'
                          '  name: string;\n'
                          '  age: number;\n}\n'
                          'type Getters<T> = { [K in keyof T as `get${Capitalize<K>}`]: () => T[K] };\n'
                          'const g: Getters<Person> = { getName: () => "Ada", getAge: () => 36 };\n'
                          'console.log(`${g.getName()} ${g.getAge()}`);\n',
                          'interface Person {\n'
                          '  name: string;\n'
                          '  age: number;\n}\n'
                          'type Getters<T> = { [K in keyof T as `get${Capitalize<K & string>}`]: () => T[K] };\n'
                          'const g: Getters<Person> = { getName: () => "Ada", getAge: () => 36 };\n'
                          'console.log(`${g.getName()} ${g.getAge()}`);\n',
                          [("", "Ada 36")],
                          hints=["What kinds of key can `keyof T` produce?",
                                 "Capitalize only accepts strings.",
                                 "Capitalize<K & string>."],
                          difficulty="Medium"),
                _typed("tscourse-w30-tl-1", "The runtime twin",
                       "Build the getter name at run time, typed with the same template the type uses.",
                       'function getterName<K extends string>(key: K): `get${Capitalize<K>}` {\n'
                       '  return `get${key.charAt(0).toUpperCase()}${key.slice(1)}` as `get${Capitalize<K>}`;\n}\n'
                       'const n = getterName("total");\n'
                       'console.log(n);\n',
                       '  return `get${key.charAt(0).toUpperCase()}${key.slice(1)}` as `get${Capitalize<K>}`;',
                       'type _1 = Expect<Equal<typeof n, "getTotal">>;\n',
                       [("", "getTotal")],
                       hints=["Upper-case the first character, keep the rest.",
                              "String methods return string, so the precise type needs one cast.",
                              "return `get${key.charAt(0).toUpperCase()}${key.slice(1)}` as `get${Capitalize<K>}`;"],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("`Capitalize<\"hELLO\">` is…",
                   ["\"Hello\"", "\"HELLO\"", "\"hELLO\"", "\"hello\""], 1,
                   "Only the first letter is changed; the rest is left exactly as it was."),
                _q("Why does the runtime getterName need a cast?",
                   ["it does not", "string methods return string; the checker cannot follow them into the template",
                    "Capitalize is runtime", "K is unknown"], 1,
                   "Precise outside, careful inside."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w30-match", "Taking strings apart",
            "`infer` inside a template: prefixes, trimming, splitting, replacing.",
            """
A template literal can sit on the right of `extends`, with `infer` in its holes:

```ts
type Head<S> = S extends `${infer H} ${string}` ? H : S;
type A = Head<"hello big world">;      // "hello"
```

The compiler matches left to right, and an `infer` followed by a literal takes the
**shortest** match up to that literal — so `H` stops at the first space.

## Prefixes and suffixes

```ts
type StartsWith<S extends string, P extends string> = S extends `${P}${string}` ? true : false;
```

No `infer` needed when you only ask *whether* it matches.

## Recursion makes it a parser

```ts
type TrimLeft<S extends string> = S extends ` ${infer R}` ? TrimLeft<R> : S;
```

Peel one space, call again on the rest, stop when there is no leading space — the
base case. `TrimLeft<"   hi">` is `"hi"`.

Splitting collects pieces into a **tuple**:

```ts
type Split<S extends string, D extends string> =
  S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S];
type P = Split<"a,b,c", ",">;          // ["a", "b", "c"]
```

## The limits

Recursive types have a depth limit (about 1,000 levels for these tail-recursive
conditionals); past it the compiler reports that the type is excessively deep. It
is week 25's stack, at the type level — and one reason type-level parsing is for
short strings like routes, not documents.

> ⚠️ **Common mistakes:** expecting `infer` to take the longest match; a recursive
> string type with no base case; and parsing long strings at the type level.
""",
            warmup=[
                _q("`infer H` followed by a literal matches…",
                   ["the longest prefix", "the shortest prefix up to that literal", "one character", "nothing"], 1,
                   "Left to right, first occurrence."),
                _q("`StartsWith<\"hello\", \"he\">` is…",
                   ["false", "true", "never", "\"llo\""], 1,
                   "`${P}${string}` matches."),
                _q("`Split<\"a,b\", \",\">` is…",
                   ["\"a\" | \"b\"", "[\"a\", \"b\"]", "string[]", "[\"a,b\"]"], 1,
                   "A tuple."),
                _q("Type-level recursion has…",
                   ["no limit", "a depth limit", "a runtime cost", "no base case"], 1,
                   "The compiler's own stack."),
            ],
            exercises=[
                _types("tscourse-w30-mt-t1", "Does it start with…",
                       "Write `StartsWith<S, P>`: true when S begins with P.",
                       'type StartsWith<S extends string, P extends string> = S extends `${P}${string}` ? true : false;\n',
                       'S extends `${P}${string}` ? true : false',
                       """
type _1 = Expect<Equal<StartsWith<"hello", "he">, true>>;
type _2 = Expect<Equal<StartsWith<"hello", "lo">, false>>;
type _3 = Expect<Equal<StartsWith<"abc", "">, true>>;
""",
                       hints=["Match P followed by anything.",
                              "S extends `${P}${string}` ? true : false"],
                       difficulty="Easy"),
                _types("tscourse-w30-mt-t2", "The first word",
                       "Write `FirstWord<S>`: everything before the first space, or S if there is none.",
                       'type FirstWord<S extends string> = S extends `${infer W} ${string}` ? W : S;\n',
                       'S extends `${infer W} ${string}` ? W : S',
                       """
type _1 = Expect<Equal<FirstWord<"hello big world">, "hello">>;
type _2 = Expect<Equal<FirstWord<"solo">, "solo">>;
""",
                       hints=["Infer the part before a space.",
                              "S extends `${infer W} ${string}` ? W : S"],
                       difficulty="Medium"),
                _types("tscourse-w30-mt-t3", "Trim the left",
                       "Write `TrimLeft<S>`, removing every leading space — recursively.",
                       'type TrimLeft<S extends string> = S extends ` ${infer R}` ? TrimLeft<R> : S;\n',
                       'S extends ` ${infer R}` ? TrimLeft<R> : S',
                       """
type _1 = Expect<Equal<TrimLeft<"   hi">, "hi">>;
type _2 = Expect<Equal<TrimLeft<"hi ">, "hi ">>;
type _3 = Expect<Equal<TrimLeft<"">, "">>;
""",
                       hints=["Peel one leading space and call again on the rest.",
                              "S extends ` ${infer R}` ? TrimLeft<R> : S"],
                       difficulty="Medium"),
                _types("tscourse-w30-mt-t4", "Split on a delimiter",
                       "Write `Split<S, D>` returning a tuple of the pieces.",
                       'type Split<S extends string, D extends string> = S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S];\n',
                       'S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S]',
                       """
type _1 = Expect<Equal<Split<"a,b,c", ",">, ["a", "b", "c"]>>;
type _2 = Expect<Equal<Split<"one", ",">, ["one"]>>;
type _3 = Expect<Equal<Split<"x-y", "-">, ["x", "y"]>>;
""",
                       hints=["Take the head before the first delimiter; recurse on the tail.",
                              "Spread the recursive result into a tuple after the head.",
                              "S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S]"],
                       difficulty="Hard"),
                _types("tscourse-w30-mt-t5", "Replace every occurrence",
                       "Write `ReplaceAll<S, From, To>`.",
                       'type ReplaceAll<S extends string, From extends string, To extends string> =\n'
                       '  From extends "" ? S : S extends `${infer A}${From}${infer B}` ? `${A}${To}${ReplaceAll<B, From, To>}` : S;\n',
                       'From extends "" ? S : S extends `${infer A}${From}${infer B}` ? `${A}${To}${ReplaceAll<B, From, To>}` : S',
                       """
type _1 = Expect<Equal<ReplaceAll<"a-b-c", "-", "+">, "a+b+c">>;
type _2 = Expect<Equal<ReplaceAll<"none", "-", "+">, "none">>;
type _3 = Expect<Equal<ReplaceAll<"abc", "", "x">, "abc">>;
""",
                       hints=["Split around the first From, put To in its place, and recurse on what follows.",
                              "An empty From would match everywhere forever — treat it as a no-op first."],
                       difficulty="Hard"),
            ],
            quiz=[
                _q("Why must ReplaceAll guard `From extends \"\"`?",
                   ["style", "an empty pattern matches at every position and the recursion never shrinks", "speed", "it is required"], 1,
                   "A base case, again."),
                _q("Split recurses on…",
                   ["the head", "the tail after the first delimiter", "the whole string", "the delimiter"], 1,
                   "The part still to process."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w30-infer", "`infer`, in depth",
            "Tuples, object properties, and inference with a constraint.",
            """
Week 29 used `infer` in function and promise positions. It works anywhere a type
can be written inside the `extends` clause.

## In tuples

```ts
type Last<T extends readonly unknown[]> = T extends readonly [...unknown[], infer L] ? L : never;
type Tail<T extends readonly unknown[]> = T extends readonly [unknown, ...infer R] ? R : [];
```

Variadic tuple patterns: "anything, then one last element" and "one element, then
the rest". `Last<[1, 2, 3]>` is `3`; `Tail<[1, 2, 3]>` is `[2, 3]`.

## In object properties

```ts
type DataOf<T> = T extends { data: infer D } ? D : never;
type R = DataOf<{ status: 200; data: string[] }>;     // string[]
```

Pull the payload type out of an API response shape without naming it anywhere.

## Several at once

```ts
type Swap<T> = T extends [infer A, infer B] ? [B, A] : never;
```

## With a constraint

TypeScript 4.7 added `infer X extends C`: infer, **and** only match if it fits C.
Its best trick converts numeric text to a number literal:

```ts
type ToNum<S extends string> = S extends `${infer N extends number}` ? N : never;
type N = ToNum<"42">;          // 42 — the number, not the string
```

That is what lets a type-level parser do arithmetic on route segments or version
strings.

## Literal templates on values

A template **expression** is typed `string`, unless you say otherwise:

```ts
const n = 7;
const loose = `id-${n}`;              // string
const exact = `id-${n}` as const;     // "id-7"
```

`as const` asks for the narrowest type, and for a template that is the literal it
will produce.

> ⚠️ **Common mistakes:** `infer` outside an extends clause; forgetting `readonly`
> in tuple patterns (a readonly tuple will not match a mutable pattern); and
> expecting template expressions to keep literal types without `as const`.
""",
            warmup=[
                _q("`[...unknown[], infer L]` gives…",
                   ["the first element", "the last element", "the length", "the rest"], 1,
                   "Anything, then one."),
                _q("`T extends { data: infer D }` extracts…",
                   ["T", "the type of the data property", "the keys", "never"], 1,
                   "Infer in a property."),
                _q("`infer N extends number` on \"42\" gives…",
                   ["number", "42", "\"42\"", "never"], 1,
                   "The numeric literal."),
                _q("`const x = `id-${7}`` is typed…",
                   ["\"id-7\"", "string", "`id-${number}`", "never"], 1,
                   "Add as const for the literal."),
            ],
            exercises=[
                _types("tscourse-w30-id-t1", "The last element",
                       "Write `Last<T>` for any tuple.",
                       'type Last<T extends readonly unknown[]> = T extends readonly [...unknown[], infer L] ? L : never;\n',
                       'T extends readonly [...unknown[], infer L] ? L : never',
                       """
type _1 = Expect<Equal<Last<[1, 2, 3]>, 3>>;
type _2 = Expect<Equal<Last<readonly ["a"]>, "a">>;
type _3 = Expect<Equal<Last<[]>, never>>;
""",
                       hints=["A variadic pattern: anything, then one inferred element.",
                              "readonly in the pattern lets readonly tuples match too."],
                       difficulty="Medium"),
                _types("tscourse-w30-id-t2", "Everything but the first",
                       "Write `Tail<T>`: the tuple without its first element, or [] if it is empty.",
                       'type Tail<T extends readonly unknown[]> = T extends readonly [unknown, ...infer R] ? R : [];\n',
                       'T extends readonly [unknown, ...infer R] ? R : []',
                       """
type _1 = Expect<Equal<Tail<[1, 2, 3]>, [2, 3]>>;
type _2 = Expect<Equal<Tail<[1]>, []>>;
type _3 = Expect<Equal<Tail<[]>, []>>;
""",
                       hints=["One element, then infer the rest.",
                              "T extends readonly [unknown, ...infer R] ? R : []"],
                       difficulty="Medium"),
                _types("tscourse-w30-id-t3", "The payload",
                       "Write `DataOf<T>`: the type of an object's `data` property, or never.",
                       'type DataOf<T> = T extends { data: infer D } ? D : never;\n',
                       'T extends { data: infer D } ? D : never',
                       """
type _1 = Expect<Equal<DataOf<{ status: 200; data: string[] }>, string[]>>;
type _2 = Expect<Equal<DataOf<{ status: 404 }>, never>>;
""",
                       hints=["Infer the type in the data position.",
                              "T extends { data: infer D } ? D : never"],
                       difficulty="Easy"),
                _types("tscourse-w30-id-t4", "Text to number",
                       "Write `ToNum<S>`: the number literal a numeric string spells, or never.",
                       'type ToNum<S extends string> = S extends `${infer N extends number}` ? N : never;\n',
                       'S extends `${infer N extends number}` ? N : never',
                       """
type _1 = Expect<Equal<ToNum<"42">, 42>>;
type _2 = Expect<Equal<ToNum<"3.5">, 3.5>>;
type _3 = Expect<Equal<ToNum<"abc">, never>>;
""",
                       hints=["infer with a constraint: infer N extends number.",
                              "S extends `${infer N extends number}` ? N : never"],
                       difficulty="Hard"),
                _types("tscourse-w30-id-t5", "Swap a pair",
                       "Write `Swap<T>` for two-element tuples.",
                       'type Swap<T> = T extends [infer A, infer B] ? [B, A] : never;\n',
                       'T extends [infer A, infer B] ? [B, A] : never',
                       """
type _1 = Expect<Equal<Swap<[1, "a"]>, ["a", 1]>>;
type _2 = Expect<Equal<Swap<[1, 2, 3]>, never>>;
""",
                       hints=["Infer both elements, then rebuild in the other order.",
                              "T extends [infer A, infer B] ? [B, A] : never"],
                       difficulty="Easy"),
                _predict("tscourse-w30-id-p1", "A template that keeps its value",
                         'const n = 7;\n'
                         'const label = `id-${n}` as const;\n',
                         "label", '"id-7"',
                         why="Without `as const` it would be plain string.",
                         hints=["`as const` asks for the narrowest type.",
                                "n is the literal 7, so the template is fully known.",
                                'Write "id-7".']),
            ],
            quiz=[
                _q("Why does `Last` use `readonly` in its pattern?",
                   ["style", "a readonly tuple does not match a mutable tuple pattern", "speed", "it is required by infer"], 1,
                   "readonly accepts both."),
                _q("Where can `infer` appear?",
                   ["anywhere", "anywhere a type can be written, inside a conditional's extends clause", "only in functions",
                    "only in tuples"], 1,
                   "Pattern positions."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w30-parse", "Parsing a route",
            "From \"/users/:id/posts/:postId\" to { id: string; postId: string }.",
            """
Everything so far comes together in one type:

```ts
type ParamNames<P extends string> =
  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`>
  : P extends `${string}:${infer Name}` ? Name
  : never;
```

Read the three branches:

1. A `:name` followed by more path → that name, **plus** the names in the rest.
2. A `:name` at the end → just that name.
3. No `:` at all → `never` — no parameters.

`ParamNames<"/users/:id/posts/:postId">` is `"id" | "postId"`. A mapped type (week
29) turns that into the object a handler receives:

```ts
type Params<P extends string> = { [K in ParamNames<P>]: string };
```

`Params<"/health">` is `{}` — a mapped type over `never` has no keys.

## Why the rest is re-prefixed

`ParamNames<`/${Rest}`>` puts the slash back. Without it, `Rest` is
`"posts/:postId"`, which still works here — but it keeps every recursive call
looking like a path, which makes the type easier to reason about and to extend.

## The same shape, elsewhere

A query string `"page=2&sort=name"` has keys before each `=`; a template
`"Hello {name}"` has keys inside braces. Each is one conditional and one recursion
away. This week's exercises and stretch do both.

> ⚠️ **Common mistakes:** forgetting the recursive call, so only the first
> parameter is found; matching `:name` without stopping at the next `/`; and
> expecting route parsing on a `string` — a plain `string` has no structure to
> parse, so it yields `never`.
""",
            warmup=[
                _q("`ParamNames<\"/users/:id\">` is…",
                   ["string", "\"id\"", "\"users\"", "never"], 1,
                   "The name after the colon."),
                _q("`Params<\"/health\">` is…",
                   ["never", "{}", "{ health: string }", "string"], 1,
                   "A mapped type over never."),
                _q("Without the recursive call, `ParamNames` of a two-parameter path gives…",
                   ["both", "only the first", "never", "string"], 1,
                   "It stops after one."),
                _q("`ParamNames<string>` is…",
                   ["string", "never — a plain string has no structure to match", "any", "\"\""], 1,
                   "Needs a literal."),
            ],
            exercises=[
                _types("tscourse-w30-pr-t1", "The parameter names",
                       "Write `ParamNames<P>` for route patterns.",
                       'type ParamNames<P extends string> =\n'
                       '  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`>\n'
                       '  : P extends `${string}:${infer Name}` ? Name\n'
                       '  : never;\n',
                       '  P extends `${string}:${infer Name}/${infer Rest}` ? Name | ParamNames<`/${Rest}`>\n'
                       '  : P extends `${string}:${infer Name}` ? Name\n'
                       '  : never;',
                       """
type _1 = Expect<Equal<ParamNames<"/users/:id/posts/:postId">, "id" | "postId">>;
type _2 = Expect<Equal<ParamNames<"/users/:id">, "id">>;
type _3 = Expect<Equal<ParamNames<"/health">, never>>;
""",
                       hints=["Three cases: a parameter with more path after it, a final parameter, none.",
                              "In the first case, union the name with the names in the rest.",
                              "Stop the name at the next / by matching `:${infer Name}/${infer Rest}`."],
                       difficulty="Hard"),
                _types("tscourse-w30-pr-t2", "The handler's argument",
                       "Write `Params<P>`: an object with a string property per parameter name.",
                       _PARAMS,
                       '{ [K in ParamNames<P>]: string }',
                       """
type _1 = Expect<Equal<Params<"/users/:id/posts/:postId">, { id: string; postId: string }>>;
type _2 = Expect<Equal<Params<"/health">, {}>>;
""",
                       hints=["A mapped type over the union of names.",
                              "{ [K in ParamNames<P>]: string }"],
                       difficulty="Medium"),
                _types("tscourse-w30-pr-t3", "Query-string keys",
                       "Write `QueryKeys<Q>` for strings like \"page=2&sort=name\": the keys before each `=`.",
                       'type QueryKeys<Q extends string> =\n'
                       '  Q extends `${infer Pair}&${infer Rest}` ? QueryKeys<Pair> | QueryKeys<Rest>\n'
                       '  : Q extends `${infer K}=${string}` ? K\n'
                       '  : never;\n',
                       '  Q extends `${infer Pair}&${infer Rest}` ? QueryKeys<Pair> | QueryKeys<Rest>\n'
                       '  : Q extends `${infer K}=${string}` ? K\n'
                       '  : never;',
                       """
type _1 = Expect<Equal<QueryKeys<"page=2&sort=name">, "page" | "sort">>;
type _2 = Expect<Equal<QueryKeys<"q=ts">, "q">>;
type _3 = Expect<Equal<QueryKeys<"">, never>>;
""",
                       hints=["Split on & first; each pair then has a key before =.",
                              "Recurse on both halves of the split."],
                       difficulty="Hard"),
                _types("tscourse-w30-pr-t4", "Join a tuple",
                       "Write `Join<T, D>`: a tuple of strings joined by a delimiter.",
                       'type Join<T extends readonly string[], D extends string> =\n'
                       '  T extends readonly [infer H extends string] ? H\n'
                       '  : T extends readonly [infer H extends string, ...infer R extends readonly string[]] ? `${H}${D}${Join<R, D>}`\n'
                       '  : "";\n',
                       '  T extends readonly [infer H extends string] ? H\n'
                       '  : T extends readonly [infer H extends string, ...infer R extends readonly string[]] ? `${H}${D}${Join<R, D>}`\n'
                       '  : "";',
                       """
type _1 = Expect<Equal<Join<["a", "b", "c"], "/">, "a/b/c">>;
type _2 = Expect<Equal<Join<["solo"], "/">, "solo">>;
type _3 = Expect<Equal<Join<[], "/">, "">>;
""",
                       hints=["One element: just it. More: the head, the delimiter, and the joined rest.",
                              "`infer … extends string` keeps each piece usable in a template."],
                       difficulty="Hard"),
                _typed("tscourse-w30-pr-1", "Parse at run time, typed at compile time",
                       "Extract a path's parameters at run time into the object the type describes.",
                       _PARAMS +
                       'function extract<P extends string>(pattern: P, path: string): Params<P> {\n'
                       '  const want = pattern.split("/");\n'
                       '  const got = path.split("/");\n'
                       '  const out: Record<string, string> = {};\n'
                       '  want.forEach((w, i) => {\n'
                       '    if (w.startsWith(":")) {\n'
                       '      out[w.slice(1)] = got[i] ?? "";\n    }\n  });\n'
                       '  return out as Params<P>;\n}\n'
                       'const p = extract("/users/:id/posts/:postId", "/users/42/posts/7");\n'
                       'console.log(`${p.id} ${p.postId}`);\n',
                       '    if (w.startsWith(":")) {\n'
                       '      out[w.slice(1)] = got[i] ?? "";\n    }',
                       'type _1 = Expect<Equal<typeof p, { id: string; postId: string }>>;\n',
                       [("", "42 7")],
                       hints=["A segment starting with : is a parameter; its name is the rest of the segment.",
                              "Store the matching segment of the actual path under that name."],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Why does `Join` use `infer H extends string`?",
                   ["style", "so H is known to be a string and can go inside a template", "speed", "for readonly"], 1,
                   "Week 30's constrained infer."),
                _q("`extract` casts its result because…",
                   ["it is wrong", "the object is built from runtime strings the checker cannot follow", "Params is optional",
                    "of Record"], 1,
                   "One cast, inside, where the code establishes the claim."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w30-paths", "Typed object paths",
            "\"db.port\" as a type — and a `get` that knows it returns a number.",
            """
Week 29's config has nested keys. A settings screen, a form library or a logger
often refers to them as **dotted paths**: `"db.port"`. With template literals, the
set of valid paths is a type:

```ts
type Paths<T> = T extends object
  ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]
  : never;

type P = Paths<Config>;     // "name" | "db" | "db.host" | "db.port"
```

A mapped type builds, for each key, "the key itself, or the key, a dot, and any
path inside it"; indexing the result with `[keyof T & string]` collects all of them
into one union.

## The value at a path

```ts
type PathValue<T, P extends string> =
  P extends `${infer K}.${infer R}` ? (K extends keyof T ? PathValue<T[K], R> : never)
  : P extends keyof T ? T[P]
  : never;

type V = PathValue<Config, "db.port">;    // number
```

Split at the first dot, step into that key, recurse on the rest.

## A typed `get`

```ts
function get<T, P extends Paths<T>>(obj: T, path: P): PathValue<T, P> { … }
get(config, "db.port");       // number
get(config, "db.prot");       // ✗ — not a path of Config
```

The implementation walks the object at run time with `split(".")` and one cast;
the signature makes every call site checked and precisely typed.

> ⚠️ **Common mistakes:** forgetting `& string` (symbol keys cannot be in a template);
> walking the runtime path with a different separator from the type's; and using
> paths on deeply recursive types, which can hit the depth limit.
""",
            warmup=[
                _q("`Paths<{ a: { b: number } }>` is…",
                   ["\"a.b\"", "\"a\" | \"a.b\"", "\"b\"", "string"], 1,
                   "Every prefix, too."),
                _q("`PathValue<Config, \"db.host\">` is…",
                   ["Config", "string", "never", "number"], 1,
                   "Step into db, then host."),
                _q("`{ … }[keyof T & string]` at the end of Paths…",
                   ["is a typo", "collects every key's paths into one union", "filters keys", "makes it optional"], 1,
                   "An indexed access with a union."),
                _q("A typed `get(config, \"db.prot\")`…",
                   ["returns undefined", "does not compile", "returns never", "throws"], 1,
                   "Not a member of Paths<Config>."),
            ],
            exercises=[
                _types("tscourse-w30-pa-t1", "Every path",
                       "Write `Paths<T>`: every dotted path into T, as a union.",
                       _CFG +
                       'type Paths<T> = T extends object\n'
                       '  ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]\n'
                       '  : never;\n',
                       '  ? { [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]',
                       """
type _1 = Expect<Equal<Paths<Config>, "name" | "db" | "db.host" | "db.port">>;
type _2 = Expect<Equal<Paths<{ a: { b: { c: 1 } } }>, "a" | "a.b" | "a.b.c">>;
""",
                       hints=["For each key: the key alone, or the key + \".\" + a path inside it.",
                              "Index the mapped type by its own keys to collect them.",
                              "{ [K in keyof T & string]: K | `${K}.${Paths<T[K]>}` }[keyof T & string]"],
                       difficulty="Hard"),
                _types("tscourse-w30-pa-t2", "The value at a path",
                       "Write `PathValue<T, P>`.",
                       _CFG +
                       'type PathValue<T, P extends string> =\n'
                       '  P extends `${infer K}.${infer R}` ? (K extends keyof T ? PathValue<T[K], R> : never)\n'
                       '  : P extends keyof T ? T[P]\n'
                       '  : never;\n',
                       '  P extends `${infer K}.${infer R}` ? (K extends keyof T ? PathValue<T[K], R> : never)\n'
                       '  : P extends keyof T ? T[P]\n'
                       '  : never;',
                       """
type _1 = Expect<Equal<PathValue<Config, "db.port">, number>>;
type _2 = Expect<Equal<PathValue<Config, "name">, string>>;
type _3 = Expect<Equal<PathValue<Config, "db">, { host: string; port: number }>>;
type _4 = Expect<Equal<PathValue<Config, "db.nope">, never>>;
""",
                       hints=["A dotted path: step into the first key and recurse on the rest.",
                              "An undotted path: it is a key, or it is nothing."],
                       difficulty="Hard"),
                _typed("tscourse-w30-pa-1", "A typed get",
                       "Walk the object one dotted segment at a time.",
                       _CFG + _PATHS +
                       'function get<T, P extends Paths<T>>(obj: T, path: P): PathValue<T, P> {\n'
                       '  let cur: unknown = obj;\n'
                       '  for (const key of path.split(".")) {\n'
                       '    cur = (cur as Record<string, unknown>)[key];\n  }\n'
                       '  return cur as PathValue<T, P>;\n}\n'
                       'const config: Config = { name: "app", db: { host: "localhost", port: 5432 } };\n'
                       'const port = get(config, "db.port");\n'
                       'console.log(`${get(config, "name")} ${port + 1}`);\n',
                       '  for (const key of path.split(".")) {\n'
                       '    cur = (cur as Record<string, unknown>)[key];\n  }',
                       'type _1 = Expect<Equal<typeof port, number>>;\n'
                       'function _neverCalled(): void {\n'
                       '  // @ts-expect-error — not a path of Config\n'
                       '  get(config, "db.prot");\n}\n',
                       [("", "app 5433")],
                       hints=["Split the path on dots and step down one key at a time.",
                              "At run time the object is just a record of unknowns — one cast per step."],
                       difficulty="Hard"),
                _fix("tscourse-w30-pa-fix1", "Fix the separator that did not match the type",
                     "The type says paths are dotted, and the runtime walk splits on `/` — so `get(config, \"db.port\")` looks up a key literally named `db.port`, finds nothing, and prints `undefined`. The type and the implementation must agree on the separator.",
                     _CFG + _PATHS +
                     'function get<T, P extends Paths<T>>(obj: T, path: P): PathValue<T, P> {\n'
                     '  let cur: unknown = obj;\n'
                     '  for (const key of path.split("/")) {\n'
                     '    cur = (cur as Record<string, unknown>)[key];\n  }\n'
                     '  return cur as PathValue<T, P>;\n}\n'
                     'const config: Config = { name: "app", db: { host: "localhost", port: 5432 } };\n'
                     'console.log(get(config, "db.port"));\n',
                     _CFG + _PATHS +
                     'function get<T, P extends Paths<T>>(obj: T, path: P): PathValue<T, P> {\n'
                     '  let cur: unknown = obj;\n'
                     '  for (const key of path.split(".")) {\n'
                     '    cur = (cur as Record<string, unknown>)[key];\n  }\n'
                     '  return cur as PathValue<T, P>;\n}\n'
                     'const config: Config = { name: "app", db: { host: "localhost", port: 5432 } };\n'
                     'console.log(get(config, "db.port"));\n',
                     [("", "5432")],
                     hints=["The cast at the end is a promise the walk must keep.",
                            "What character separates the segments in Paths<T>?",
                            "Split on \".\"."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why can the typed `get` still print undefined?",
                   ["it cannot", "the cast trusts the implementation; if the walk is wrong, the type is a lie", "of never",
                    "Paths is loose"], 1,
                   "Types describe; code does."),
                _q("Paths on a type that contains itself (a tree) would…",
                   ["be fine", "recurse without end and hit the depth limit", "be never", "be string"], 1,
                   "Infinite paths."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w30-literal", "Keeping literals alive",
            "Why `let` loses \"GET\", and how `const` type parameters keep it.",
            """
Everything this week depends on the compiler seeing a **literal** — `"/users/:id"`,
not `string`. Literals are easy to lose.

## Widening

```ts
let method = "GET";          // string   — a let may be reassigned, so it is widened
const verb = "GET";          // "GET"    — a const cannot change
request(method);             // ✗ TS2345: 'string' is not assignable to '"GET" | "POST"'
```

## `as const`

For objects and arrays, `as const` keeps every literal and makes it readonly:

```ts
const EVENTS = ["open", "close"] as const;       // readonly ["open", "close"]
type Ev = (typeof EVENTS)[number];               // "open" | "close"
```

A runtime list and a type, from one declaration — the list is the source of truth.

## `const` type parameters

A generic function infers loose types by default: `tags(["a", "b"])` is `string[]`.
Since TypeScript 5.0, a **`const` type parameter** asks for the narrow inference the
caller would have got with `as const`:

```ts
function tags<const T extends readonly string[]>(xs: T): T { return xs; }
const t = tags(["a", "b"]);                      // readonly ["a", "b"]
```

Library authors use this so callers do not have to remember `as const`. A route
function receiving `"/users/:id"` does not need it — a string argument already infers
as its literal — but arrays and objects of routes do.

> ⚠️ **Common mistakes:** `let` for a value whose literal type matters; forgetting
> `as const` on a list meant to define a union; and writing `as const` at every call
> site when a `const` type parameter would do it once.
""",
            warmup=[
                _q("`let m = \"GET\"` is typed…",
                   ["\"GET\"", "string", "const", "any"], 1,
                   "Widened, because it may change."),
                _q("`[\"a\", \"b\"] as const` is…",
                   ["string[]", "readonly [\"a\", \"b\"]", "[\"a\", \"b\"]", "readonly string[]"], 1,
                   "Literal and readonly."),
                _q("`(typeof EVENTS)[number]` gives…",
                   ["the length", "the union of the list's elements", "number", "the first element"], 1,
                   "Indexed access by number."),
                _q("A `const` type parameter…",
                   ["makes the argument readonly at run time", "infers as narrowly as `as const` would", "is a const variable",
                    "disables inference"], 1,
                   "TypeScript 5.0."),
            ],
            exercises=[
                _diagnose("tscourse-w30-lt-d1", "The method that became a string",
                          "TS2345: Argument of type 'string' is not assignable to parameter of type '\"GET\" | \"POST\"'.",
                          'function request(method: "GET" | "POST", path: string): string {\n'
                          '  return `${method} ${path}`;\n}\n'
                          'let method = "GET";\n'
                          'console.log(request(method, "/health"));\n',
                          'function request(method: "GET" | "POST", path: string): string {\n'
                          '  return `${method} ${path}`;\n}\n'
                          'const method = "GET";\n'
                          'console.log(request(method, "/health"));\n',
                          [("", "GET /health")],
                          hints=["What type does a `let` initialised with \"GET\" get?",
                                 "A binding that never changes can keep its literal type.",
                                 "Use const."],
                          difficulty="Easy"),
                _types("tscourse-w30-lt-t1", "A union from a list",
                       "Derive `Ev` from the runtime list, so adding an event to the list adds it to the type.",
                       'const EVENTS = ["open", "close", "error"] as const;\n'
                       'type Ev = (typeof EVENTS)[number];\n',
                       '(typeof EVENTS)[number]',
                       """
type _1 = Expect<Equal<Ev, "open" | "close" | "error">>;
""",
                       hints=["Index the list's type with number.",
                              "(typeof EVENTS)[number]"],
                       difficulty="Easy"),
                _typed("tscourse-w30-lt-1", "A const type parameter",
                       "Declare `tags` so its callers get their exact literals back without writing `as const`.",
                       'function tags<const T extends readonly string[]>(xs: T): T {\n'
                       '  return xs;\n}\n'
                       'const t = tags(["urgent", "later"]);\n'
                       'console.log(t.join(" "));\n',
                       'function tags<const T extends readonly string[]>(xs: T): T {',
                       'type _1 = Expect<Equal<typeof t, readonly ["urgent", "later"]>>;\n',
                       [("", "urgent later")],
                       hints=["Add the const modifier to the type parameter.",
                              "function tags<const T extends readonly string[]>(xs: T): T {"],
                       difficulty="Medium"),
                _typed("tscourse-w30-lt-2", "Handlers named from events",
                       "Type a handler table whose keys are `on` + each event name, derived from the runtime list.",
                       'const EVENTS = ["open", "close"] as const;\n'
                       'type Ev = (typeof EVENTS)[number];\n'
                       'type Handlers = { [E in Ev as `on${Capitalize<E>}`]: () => string };\n'
                       'const handlers: Handlers = {\n'
                       '  onOpen: () => "opened",\n'
                       '  onClose: () => "closed",\n};\n'
                       'for (const e of EVENTS) {\n'
                       '  const key = `on${e.charAt(0).toUpperCase()}${e.slice(1)}` as keyof Handlers;\n'
                       '  console.log(handlers[key]());\n}\n',
                       'type Handlers = { [E in Ev as `on${Capitalize<E>}`]: () => string };',
                       'type _1 = Expect<Equal<keyof Handlers, "onOpen" | "onClose">>;\n',
                       [("", "opened\nclosed")],
                       hints=["Map over the event union, renaming each through a template.",
                              "type Handlers = { [E in Ev as `on${Capitalize<E>}`]: () => string };"],
                       difficulty="Medium"),
            ],
            quiz=[
                _q("Why does `router.add(\"/users/:id\", …)` not need `as const`?",
                   ["it does", "a string argument to a generic `P extends string` already infers as its literal", "routes are const",
                    "of Params"], 1,
                   "Arrays and objects are where widening bites."),
                _q("Deriving a type from `as const` data makes…",
                   ["two sources of truth", "the runtime list the single source of truth", "the list mutable", "no difference"], 1,
                   "Add to the list, the type follows."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w30-library", "Library #2: the router",
            "Handlers typed from their patterns, matched at run time.",
            """
The library's second module is a **router**:

```ts
const router = new Router()
  .add("/health", () => "ok")
  .add("/users/:id", (p) => `user ${p.id}`)
  .add("/users/:id/posts/:postId", (p) => `post ${p.postId} by ${p.id}`);

router.resolve("/users/42/posts/7");      // "post 7 by 42"
router.resolve("/nope");                  // "404 /nope"
```

Two halves, deliberately separated.

## The type half

```ts
add<P extends string>(pattern: P, handler: (params: Params<P>) => string): this
```

`P` infers as the literal pattern, `Params<P>` parses it (lesson 4), and the handler's
`p` is exactly `{ id: string; postId: string }`. Returning `this` makes `.add` chain.

## The runtime half

Routes of *different* parameter types must live in one array, so they are stored
**type-erased**:

```ts
interface Route {
  readonly pattern: string;
  readonly handle: (params: Record<string, string>) => string;
}
```

`add` casts its precise handler to that erased shape — once, at the boundary — and
`resolve` matches segment by segment: equal lengths, literal segments equal, `:name`
segments captured into the params object.

## The test that proves it

The capstone's harness contains, in a function that never runs:

```ts
// @ts-expect-error — /users/:id has no `name` parameter
router.add("/users/:id", (p) => p.name);
```

If `Params` were too loose (say `Record<string, string>`), that line would compile and
the unused directive would fail the check.
""",
            warmup=[
                _q("`add` returns `this` so that…",
                   ["it is typed", "calls can chain", "it is private", "it is async"], 1,
                   "A fluent API."),
                _q("Routes are stored type-erased because…",
                   ["types are slow", "routes with different parameter types must share one array", "Params is unknown",
                    "of classes"], 1,
                   "One cast, at the boundary."),
                _q("A path matches a pattern when…",
                   ["it starts with it", "segment counts match and every literal segment is equal", "it contains a :",
                    "always"], 1,
                   "Segment by segment."),
                _q("The `@ts-expect-error` test fails if…",
                   ["the router is wrong at run time", "the handler type is loose enough that p.name compiles", "it runs",
                    "never"], 1,
                   "An unused directive is an error."),
            ],
            exercises=[
                _ex("tscourse-w30-lb-1", "Match one segment",
                    "A parameter segment captures; a literal segment must be equal.",
                    'function match(pattern: string, path: string): Record<string, string> | null {\n'
                    '  const want = pattern.split("/").filter((s) => s !== "");\n'
                    '  const got = path.split("/").filter((s) => s !== "");\n'
                    '  if (want.length !== got.length) {\n'
                    '    return null;\n  }\n'
                    '  const params: Record<string, string> = {};\n'
                    '  for (let i = 0; i < want.length; i = i + 1) {\n'
                    '    const w = want[i] ?? "";\n'
                    '    const g = got[i] ?? "";\n'
                    '    if (w.startsWith(":")) {\n'
                    '      params[w.slice(1)] = g;\n'
                    '    } else if (w !== g) {\n'
                    '      return null;\n    }\n  }\n'
                    '  return params;\n}\n'
                    'console.log(JSON.stringify(match("/users/:id", "/users/42")));\n'
                    'console.log(JSON.stringify(match("/users/:id", "/teams/42")));\n'
                    'console.log(JSON.stringify(match("/users/:id", "/users/42/x")));\n',
                    '    if (w.startsWith(":")) {\n'
                    '      params[w.slice(1)] = g;\n'
                    '    } else if (w !== g) {\n'
                    '      return null;\n    }',
                    [("", '{"id":"42"}\nnull\nnull')],
                    hints=["Two cases per segment: a parameter, or a literal.",
                           "A mismatched literal means this pattern does not match at all."],
                    difficulty="Medium"),
                _fix("tscourse-w30-lb-fix1", "Fix the match that ignored the length",
                     "`/users/42/posts/7` should not match the pattern `/users/:id`, and this prints `{\"id\":\"42\"}` — it compares the pattern's segments and never checks that the path has no more of its own.",
                     'function match(pattern: string, path: string): Record<string, string> | null {\n'
                     '  const want = pattern.split("/").filter((s) => s !== "");\n'
                     '  const got = path.split("/").filter((s) => s !== "");\n'
                     '  const params: Record<string, string> = {};\n'
                     '  for (let i = 0; i < want.length; i = i + 1) {\n'
                     '    const w = want[i] ?? "";\n'
                     '    const g = got[i] ?? "";\n'
                     '    if (w.startsWith(":")) {\n'
                     '      params[w.slice(1)] = g;\n'
                     '    } else if (w !== g) {\n'
                     '      return null;\n    }\n  }\n'
                     '  return params;\n}\n'
                     'console.log(JSON.stringify(match("/users/:id", "/users/42/posts/7")));\n',
                     'function match(pattern: string, path: string): Record<string, string> | null {\n'
                     '  const want = pattern.split("/").filter((s) => s !== "");\n'
                     '  const got = path.split("/").filter((s) => s !== "");\n'
                     '  if (want.length !== got.length) {\n'
                     '    return null;\n  }\n'
                     '  const params: Record<string, string> = {};\n'
                     '  for (let i = 0; i < want.length; i = i + 1) {\n'
                     '    const w = want[i] ?? "";\n'
                     '    const g = got[i] ?? "";\n'
                     '    if (w.startsWith(":")) {\n'
                     '      params[w.slice(1)] = g;\n'
                     '    } else if (w !== g) {\n'
                     '      return null;\n    }\n  }\n'
                     '  return params;\n}\n'
                     'console.log(JSON.stringify(match("/users/:id", "/users/42/posts/7")));\n',
                     [("", "null")],
                     hints=["The loop only looks at as many segments as the pattern has.",
                            "A path with extra segments is a different route.",
                            "Return null when the segment counts differ."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("Why does the router's first route not match `/users/42/posts/7` in the capstone?",
                   ["order", "the segment counts differ", "it is shadowed", "of types"], 1,
                   "The length check."),
                _q("Where would a real router validate `:id` as a number?",
                   ["in the type", "at run time, in the handler or a parser — types never see the real path",
                    "in Params", "nowhere"], 1,
                   "Runtime values need runtime checks (week 15)."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Library #2 — the router",
        """
Build the router class. The parameter types are supplied:

```ts
type ParamNames<P extends string> = …;          // lesson 4
type Params<P extends string> = { [K in ParamNames<P>]: string };
interface Route {
  readonly pattern: string;
  readonly handle: (params: Record<string, string>) => string;
}
```

**`class Router`:**

* `add<P extends string>(pattern: P, handler: (params: Params<P>) => string): this` —
  store the route, casting the handler to the erased shape once, and return `this`.
* `resolve(path: string): string` — try the routes **in the order they were added**;
  the first whose pattern matches (same number of segments, every literal segment
  equal, every `:name` segment captured) is called with the captured params. If none
  matches, return `404 <path>`.

The program registers three routes and resolves each input line:

```
/health
/users/42
/users/42/posts/7
/users
```

```
ok
user 42
post 7 by 42
404 /users
```

**How it is checked:** stdout, plus type assertions — that `Params` of the three
patterns are exactly right, and a `@ts-expect-error` on a handler that reads a
parameter its pattern does not declare. The class must use **no parameter
properties** (week 11) — declare `routes` as a field.
""",
        _mk("tscourse-w30-capstone", "Library #2 — the router",
            "Write the Router class: typed registration with chaining, and segment-by-segment "
            "resolution with a 404 — checked on stdout and by type assertions.",
            _FS + _PARAMS +
            'interface Route {\n'
            '  readonly pattern: string;\n'
            '  readonly handle: (params: Record<string, string>) => string;\n}\n'
            'class Router {\n'
            '  private readonly routes: Route[] = [];\n'
            '  add<P extends string>(pattern: P, handler: (params: Params<P>) => string): this {\n'
            '    this.routes.push({ pattern, handle: handler as (params: Record<string, string>) => string });\n'
            '    return this;\n  }\n'
            '  resolve(path: string): string {\n'
            '    const parts = path.split("/").filter((s) => s !== "");\n'
            '    for (const r of this.routes) {\n'
            '      const want = r.pattern.split("/").filter((s) => s !== "");\n'
            '      if (want.length !== parts.length) {\n'
            '        continue;\n      }\n'
            '      const params: Record<string, string> = {};\n'
            '      let ok = true;\n'
            '      want.forEach((w, i) => {\n'
            '        const got = parts[i] ?? "";\n'
            '        if (w.startsWith(":")) {\n'
            '          params[w.slice(1)] = got;\n'
            '        } else if (w !== got) {\n'
            '          ok = false;\n        }\n      });\n'
            '      if (ok) {\n'
            '        return r.handle(params);\n      }\n    }\n'
            '    return `404 ${path}`;\n  }\n}\n'
            'const router = new Router()\n'
            '  .add("/health", () => "ok")\n'
            '  .add("/users/:id", (p) => `user ${p.id}`)\n'
            '  .add("/users/:id/posts/:postId", (p) => `post ${p.postId} by ${p.id}`);\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").map((l) => l.trim()).filter((l) => l !== "");\n'
            'for (const line of lines) {\n'
            '  console.log(router.resolve(line));\n}\n',
            [("/health\n/users/42\n/users/42/posts/7\n/users", "ok\nuser 42\npost 7 by 42\n404 /users"),
             ("/users/abc/posts/xyz\n/health/extra", "post xyz by abc\n404 /health/extra"),
             ("/", "404 /")],
            ["Store routes type-erased: one cast in add, where the precise handler becomes the erased shape.",
             "add returns this, so registrations chain.",
             "resolve: split into non-empty segments, compare counts first, then each segment.",
             "A `:name` segment captures; a literal segment must be equal.",
             "No parameter properties — declare `routes` as a field (week 11)."],
            "Hard", "challenge",
            blank='class Router {\n'
                  '  private readonly routes: Route[] = [];\n'
                  '  add<P extends string>(pattern: P, handler: (params: Params<P>) => string): this {\n'
                  '    this.routes.push({ pattern, handle: handler as (params: Record<string, string>) => string });\n'
                  '    return this;\n  }\n'
                  '  resolve(path: string): string {\n'
                  '    const parts = path.split("/").filter((s) => s !== "");\n'
                  '    for (const r of this.routes) {\n'
                  '      const want = r.pattern.split("/").filter((s) => s !== "");\n'
                  '      if (want.length !== parts.length) {\n'
                  '        continue;\n      }\n'
                  '      const params: Record<string, string> = {};\n'
                  '      let ok = true;\n'
                  '      want.forEach((w, i) => {\n'
                  '        const got = parts[i] ?? "";\n'
                  '        if (w.startsWith(":")) {\n'
                  '          params[w.slice(1)] = got;\n'
                  '        } else if (w !== got) {\n'
                  '          ok = false;\n        }\n      });\n'
                  '      if (ok) {\n'
                  '        return r.handle(params);\n      }\n    }\n'
                  '    return `404 ${path}`;\n  }\n}',
            harness=_TYPE_PRELUDE +
                    'type _1 = Expect<Equal<Params<"/users/:id/posts/:postId">, { id: string; postId: string }>>;\n'
                    'type _2 = Expect<Equal<Params<"/health">, {}>>;\n'
                    'function _neverCalled(): void {\n'
                    '  // @ts-expect-error — /users/:id has no `name` parameter\n'
                    '  router.add("/users/:id", (p) => p.name);\n}\n'),
        example_io="ok\nuser 42\npost 7 by 42\n404 /users",
        rubric=["handlers are typed from their pattern strings, not from a loose record",
                "routes are stored type-erased with exactly one cast, in add",
                "add returns this, so registrations chain",
                "resolution compares segment counts before segments",
                "routes are tried in the order added, and an unmatched path is a 404",
                "no parameter properties"],
        stretch=_mk("tscourse-w30-capstone-stretch", "Library #2 (stretch)",
                    "A typed message formatter. `format(\"Hello {name}, you have {count} new\", values)` must "
                    "require exactly the placeholders the template names — computed with a template literal "
                    "type — and fill them at run time. Input: two lines, a name and a count.",
                    _FS +
                    'type Placeholders<S extends string> =\n'
                    '  S extends `${string}{${infer K}}${infer Rest}` ? K | Placeholders<Rest> : never;\n'
                    'function format<S extends string>(template: S, values: { [K in Placeholders<S>]: string | number }): string {\n'
                    '  const table = values as Record<string, string | number>;\n'
                    '  return template.replace(/\\{(\\w+)\\}/g, (_: string, key: string) => String(table[key] ?? ""));\n}\n'
                    'const [who, count] = fs.readFileSync(0, "utf8").split("\\n").map((l) => l.trim());\n'
                    'console.log(format("Hello {name}, you have {count} new", { name: who ?? "", count: Number(count ?? "0") }));\n',
                    [("Ada\n3", "Hello Ada, you have 3 new"), ("Lin\n0", "Hello Lin, you have 0 new")],
                    ["Placeholders is ParamNames with braces instead of a colon and a slash.",
                     "The values parameter is a mapped type over those names.",
                     "At run time, one regex replace with a callback fills them in."],
                    "Hard", "challenge",
                    blank='type Placeholders<S extends string> =\n'
                          '  S extends `${string}{${infer K}}${infer Rest}` ? K | Placeholders<Rest> : never;\n'
                          'function format<S extends string>(template: S, values: { [K in Placeholders<S>]: string | number }): string {\n'
                          '  const table = values as Record<string, string | number>;\n'
                          '  return template.replace(/\\{(\\w+)\\}/g, (_: string, key: string) => String(table[key] ?? ""));\n}',
                    harness=_TYPE_PRELUDE +
                            'type _1 = Expect<Equal<Placeholders<"a {x} b {y}">, "x" | "y">>;\n'
                            'type _2 = Expect<Equal<Placeholders<"none">, never>>;\n'
                            'function _neverCalled(): void {\n'
                            '  // @ts-expect-error — {count} is missing\n'
                            '  format("Hi {name}, {count}", { name: "x" });\n}\n'),
    ),
))
