# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — more type challenges (TS_MASTERY_ROADMAP X-21, X-24).
#
#   * 14 type-graded problem-set problems: weeks 16 and 18-22 each reach the
#     12-problem floor now that weeks 18-22 keep a single "applied" DSA problem.
#   * 15 type-challenge practice items across weeks 15-22.
# Together they take the type-challenge ladder (the daily puzzle, M5-02) to 120.
#
# Every puzzle stays inside what its week has taught: mapped types only from
# week 20, conditional types and `infer` only from week 21, recursion over
# strings and tuples in week 22. exec()'d after mastery_ts_more_m6.py and
# before mastery_ts_attach.py.
# ---------------------------------------------------------------------------


def _prt(week, eid, title, prompt, full, blank, checks, hints=(), difficulty="Medium"):
    ex = _tl(eid, title, prompt, full, blank, checks, hints=hints, difficulty=difficulty)
    ex["strictness"] = _week_strictness(week) or "strict"
    return ex


# Flattens an intersection so `Equal` can compare it with an object literal.
_SIMPLIFY_T = "type Simplify<T> = { [K in keyof T]: T[K] } & {};\n"


def _more_problems(week, items):
    TS_PROBLEM_SETS.setdefault(week, []).extend(items)


def _more_practice(week, items):
    TS_PRACTICE_MORE.setdefault(week, []).extend(items)


# ===========================================================================
# Problem-set problems
# ===========================================================================

_more_problems(16, [
    _tsp_types(16, "tsm-w16-t-as-const-shape", "Write out what `as const` gives", "core",
        "`LIMITS` is declared `as const`. Write its type out by hand as `Limits` — every property and every "
        "array element exactly as `as const` makes it — so that `Limits` and `typeof LIMITS` are the same type.",
        '''
const LIMITS = {
  free: { seats: 1, tags: ["basic"] },
  pro: { seats: 5, tags: ["basic", "export"] },
} as const;

type Limits = {
  readonly free: { readonly seats: 1; readonly tags: readonly ["basic"] };
  readonly pro: { readonly seats: 5; readonly tags: readonly ["basic", "export"] };
};
''', '''{
  readonly free: { readonly seats: 1; readonly tags: readonly ["basic"] };
  readonly pro: { readonly seats: 5; readonly tags: readonly ["basic", "export"] };
}''', '''
type _1 = Expect<Equal<Limits, typeof LIMITS>>;
''', hints=["`as const` does three things: literal types, `readonly` properties, and arrays become readonly tuples.",
            "Every level is `readonly` — the tags too: `readonly [\"basic\", \"export\"]`."]),
])

_more_problems(18, [
    _tsp_types(18, "tsm-w18-t-map-values", "Type `mapValues`", "core",
        "Write the signature of `mapValues`: it takes a record whose keys are `K` (string keys) and values `V`, and a "
        "function from `V` to `U`, and returns a record with the same keys and `U` values. `K` must be inferred "
        "from the object passed in.",
        '''
declare function mapValues<K extends string, V, U>(obj: Record<K, V>, fn: (value: V) => U): Record<K, U>;
''', "<K extends string, V, U>(obj: Record<K, V>, fn: (value: V) => U): Record<K, U>",
        '''
const lengths = mapValues({ a: "one", b: "three" }, (s) => s.length);
type _1 = Expect<Equal<typeof lengths, Record<"a" | "b", number>>>;
const flags = mapValues({ on: 1 }, (n) => n > 0);
type _2 = Expect<Equal<typeof flags, Record<"on", boolean>>>;
''', hints=["Three type parameters: the keys, the old value type, the new value type.",
            "`obj: Record<K, V>` lets TypeScript infer the key union from the literal's keys."]),
])

_more_problems(19, [
    _tsp_types(19, "tsm-w19-t-common-keys", "Keys two types share", "warm-up",
        "Write `CommonKeys<A, B>`: the keys present in both `A` and `B`.",
        '''
type CommonKeys<A, B> = keyof A & keyof B;
''', "keyof A & keyof B",
        '''
type _1 = Expect<Equal<CommonKeys<{ id: number; name: string }, { id: string; email: string }>, "id">>;
type _2 = Expect<Equal<CommonKeys<{ a: 1; b: 2 }, { a: 3; b: 4 }>, "a" | "b">>;
type _3 = Expect<Equal<CommonKeys<{ a: 1 }, { b: 2 }>, never>>;
''', hints=["`keyof` gives each type's keys as a union.", "The keys in both is the intersection of the two unions."]),

    _tsp_types(19, "tsm-w19-t-option-of", "One option of a function", "core",
        "`connect` takes a single options object. Write `OptionOf<F, K>`: the type of option `K` of such a function "
        "`F`. `K` must be one of the options' keys.",
        '''
type OptionOf<F extends (options: never) => unknown, K extends keyof Parameters<F>[0]> = Parameters<F>[0][K];
''', "Parameters<F>[0][K]",
        '''
declare function connect(options: { host: string; port: number; secure?: boolean }): void;
type _1 = Expect<Equal<OptionOf<typeof connect, "port">, number>>;
type _2 = Expect<Equal<OptionOf<typeof connect, "secure">, boolean | undefined>>;
// @ts-expect-error — "user" is not an option
type _3 = OptionOf<typeof connect, "user">;
''', hints=["`Parameters<F>` is a tuple of the parameter types; `[0]` is the options object.",
            "Then index the options object by `K`."]),

    _tsp_types(19, "tsm-w19-t-column-type", "A column's value type", "stretch",
        "`COLUMNS` names each column's type as a string. Write `ColumnType<K>`: the TypeScript type of column `K`, "
        "looked up through `TypeNames` — two indexed accesses in a row.",
        '''
const COLUMNS = { id: "number", name: "string", active: "boolean" } as const;
type TypeNames = { number: number; string: string; boolean: boolean };
type ColumnType<K extends keyof typeof COLUMNS> = TypeNames[(typeof COLUMNS)[K]];
''', "TypeNames[(typeof COLUMNS)[K]]",
        '''
type _1 = Expect<Equal<ColumnType<"id">, number>>;
type _2 = Expect<Equal<ColumnType<"active">, boolean>>;
type _3 = Expect<Equal<ColumnType<"id" | "name">, number | string>>;
''', hints=["`(typeof COLUMNS)[K]` gives the type NAME, like `\"number\"`.",
            "Use that name as the key into `TypeNames`."]),
])

_more_problems(20, [
    _tsp_types(20, "tsm-w20-t-prefixed", "Prefix every key", "core",
        "Write `Prefixed<T, P>`: `T` with every key renamed to `P` followed by the key; the values unchanged.",
        '''
type Prefixed<T, P extends string> = { [K in keyof T as `${P}${K & string}`]: T[K] };
''', "{ [K in keyof T as `${P}${K & string}`]: T[K] }",
        '''
type _1 = Expect<Equal<Prefixed<{ id: number; name: string }, "user_">, { user_id: number; user_name: string }>>;
type _2 = Expect<Equal<Prefixed<{ x: 1 }, "">, { x: 1 }>>;
''', hints=["Key remapping: `[K in keyof T as …]`.", "A template literal builds the new key; `K & string` keeps only string keys."]),

    _tsp_types(20, "tsm-w20-t-rename-key", "Rename one key", "stretch",
        "Write `RenameKey<T, From, To>`: `T` with the key `From` renamed to `To`, every other key unchanged.",
        '''
type RenameKey<T, From extends keyof T, To extends string> = { [K in keyof T as K extends From ? To : K]: T[K] };
''', "{ [K in keyof T as K extends From ? To : K]: T[K] }",
        '''
type _1 = Expect<Equal<RenameKey<{ id: number; name: string }, "id", "key">, { key: number; name: string }>>;
type _2 = Expect<Equal<RenameKey<{ a: 1; b: 2 }, "b", "c">, { a: 1; c: 2 }>>;
// @ts-expect-error — "zip" is not a key
type _3 = RenameKey<{ a: 1 }, "zip", "z">;
''', hints=["The `as` clause can decide the new name per key.", "`K extends From ? To : K`."]),

    _tsp_types(20, "tsm-w20-t-returns", "What every handler returns", "core",
        "`handlers` maps names to functions. Write `Returns<T>`: the same keys, each mapped to what that function "
        "returns.",
        '''
type Returns<T extends Record<string, (...args: never[]) => unknown>> = { [K in keyof T]: ReturnType<T[K]> };
''', "{ [K in keyof T]: ReturnType<T[K]> }",
        '''
const handlers = { count: () => 3, label: (n: number) => `#${n}`, ok: () => true };
type _1 = Expect<Equal<Returns<typeof handlers>, { count: number; label: string; ok: boolean }>>;
''', hints=["Map over the keys and keep them.", "`ReturnType<T[K]>` for each value."]),
])

_more_problems(21, [
    _tsp_types(21, "tsm-w21-t-map-value", "The value type of a Map", "warm-up",
        "Write `MapValue<M>`: for a `Map`, the type of its values; `never` for anything else.",
        '''
type MapValue<M> = M extends Map<unknown, infer V> ? V : never;
''', "M extends Map<unknown, infer V> ? V : never",
        '''
type _1 = Expect<Equal<MapValue<Map<string, number[]>>, number[]>>;
type _2 = Expect<Equal<MapValue<Map<"a", "b">>, "b">>;
type _3 = Expect<Equal<MapValue<Set<number>>, never>>;
''', hints=["`infer` the second type argument of `Map`.", "`M extends Map<unknown, infer V> ? V : never`."]),

    _tsp_types(21, "tsm-w21-t-to-array", "Wrap in an array unless it is one", "core",
        "Write `ToArray<T>`: `T` itself when it is an array, otherwise `T[]`. It must distribute over unions.",
        '''
type ToArray<T> = T extends unknown[] ? T : T[];
''', "T extends unknown[] ? T : T[]",
        '''
type _1 = Expect<Equal<ToArray<string>, string[]>>;
type _2 = Expect<Equal<ToArray<number[]>, number[]>>;
type _3 = Expect<Equal<ToArray<string | number[]>, string[] | number[]>>;
''', hints=["A conditional on a naked type parameter distributes.", "`T extends unknown[] ? T : T[]`."]),

    _tsp_types(21, "tsm-w21-t-arity", "How many parameters?", "core",
        "Write `Arity<F>`: the number of parameters of the function type `F`, as a number literal.",
        '''
type Arity<F> = F extends (...args: infer A) => unknown ? A["length"] : never;
''', 'F extends (...args: infer A) => unknown ? A["length"] : never',
        '''
type _1 = Expect<Equal<Arity<(a: string, b: number) => void>, 2>>;
type _2 = Expect<Equal<Arity<() => void>, 0>>;
type _3 = Expect<Equal<Arity<string>, never>>;
''', hints=["`infer` the parameter list as a tuple.", "A tuple's `length` is a number literal."]),
])

_more_problems(22, [
    _tsp_types(22, "tsm-w22-t-title-case", "Title Case, as a type", "core",
        "Write `TitleCase<S>`: every space-separated word of `S` capitalised.",
        '''
type TitleCase<S extends string> = S extends `${infer W} ${infer Rest}` ? `${Capitalize<W>} ${TitleCase<Rest>}` : Capitalize<S>;
''', "S extends `${infer W} ${infer Rest}` ? `${Capitalize<W>} ${TitleCase<Rest>}` : Capitalize<S>",
        '''
type _1 = Expect<Equal<TitleCase<"hello typed world">, "Hello Typed World">>;
type _2 = Expect<Equal<TitleCase<"one">, "One">>;
type _3 = Expect<Equal<TitleCase<"">, "">>;
''', hints=["Split off the first word at the first space.", "Capitalise it and recurse on the rest."]),

    _tsp_types(22, "tsm-w22-t-repeat", "Repeat a string", "stretch",
        "Write `Repeat<S, N>`: the string `S` repeated `N` times. Count with an accumulator tuple.",
        '''
type Repeat<S extends string, N extends number, Acc extends unknown[] = []> =
  Acc["length"] extends N ? "" : `${S}${Repeat<S, N, [...Acc, unknown]>}`;
''', '''Acc["length"] extends N ? "" : `${S}${Repeat<S, N, [...Acc, unknown]>}`''',
        '''
type _1 = Expect<Equal<Repeat<"ab", 3>, "ababab">>;
type _2 = Expect<Equal<Repeat<"x", 0>, "">>;
type _3 = Expect<Equal<Repeat<"-", 1>, "-">>;
''', hints=["Stop when the accumulator's length reaches `N`.", "Otherwise put one `S` in front and recurse with one more element."]),

    _tsp_types(22, "tsm-w22-t-ends-with", "Ends with", "warm-up",
        "Write `EndsWith<S, Suffix>`: `true` when the string `S` ends with `Suffix`, otherwise `false`.",
        '''
type EndsWith<S extends string, Suffix extends string> = S extends `${string}${Suffix}` ? true : false;
''', "S extends `${string}${Suffix}` ? true : false",
        '''
type _1 = Expect<Equal<EndsWith<"report.ts", ".ts">, true>>;
type _2 = Expect<Equal<EndsWith<"report.js", ".ts">, false>>;
type _3 = Expect<Equal<EndsWith<"a", "">, true>>;
''', hints=["A template literal pattern can start with `${string}`.", "`S extends `${string}${Suffix}``."]),
])


# ===========================================================================
# Practice (type challenges)
# ===========================================================================

_more_practice(15, [
    _prt(15, "tsm-w15-t-handler-variance", "A handler that cannot be faked",
        "A handler for `Dog`s only must not pose as a handler for any `Animal`. Write `AnimalHandler` so that "
        "`strictFunctionTypes` checks its `handle` — and a handler for all animals still works where a dog handler is "
        "expected.",
        '''
type Animal = { name: string };
type Dog = Animal & { bark(): string };
type AnimalHandler = { handle: (animal: Animal) => void };
type DogHandler = { handle: (dog: Dog) => void };
''', "{ handle: (animal: Animal) => void }",
        '''
declare const forAnimals: AnimalHandler;
declare const forDogs: DogHandler;
const ok: DogHandler = forAnimals;
// @ts-expect-error — a dog-only handler is not an animal handler
const fake: AnimalHandler = forDogs;
''', hints=["Method syntax (`handle(a: Animal): void`) is checked bivariantly — that is the loophole.",
            "Declare `handle` as a property with a function type: `handle: (animal: Animal) => void`."]),
])

_more_practice(16, [
    _prt(16, "tsm-w16-t-readonly-input", "Input that cannot be pushed to",
        "Write `Input` — a list of numbers the function receiving it can read but not change. It must accept an "
        "ordinary array and an `as const` tuple.",
        '''
type Input = readonly number[];
''', "readonly number[]",
        '''
const plain: Input = [1, 2, 3];
const fixed: Input = [4, 5] as const;
declare const inp: Input;
// @ts-expect-error — push does not exist on a readonly array
inp.push(6);
type _1 = Expect<Equal<Input[number], number>>;
''', hints=["An array type can be marked read-only.", "`readonly number[]` (or `ReadonlyArray<number>`)."], difficulty="Easy"),
])

_more_practice(17, [
    _prt(17, "tsm-w17-t-arg-not-null", "The argument, without the null",
        "`greet` accepts a name or `null`. Write `Name`: the type of its first parameter with `null` and `undefined` "
        "removed — using utility types, not by writing `string` yourself.",
        '''
declare function greet(name: string | null, loud?: boolean): string;
type Name = NonNullable<Parameters<typeof greet>[0]>;
''', "NonNullable<Parameters<typeof greet>[0]>",
        '''
type _1 = Expect<Equal<Name, string>>;
''', hints=["`Parameters<typeof greet>[0]` is the first parameter's type.", "`NonNullable` removes `null` and `undefined`."], difficulty="Easy"),

    _prt(17, "tsm-w17-t-with-payload", "Only the events that carry data",
        "Write `WithPayload`: the members of `AppEvent` that have a `payload` property.",
        '''
type AppEvent =
  | { type: "ready" }
  | { type: "message"; payload: string }
  | { type: "error"; payload: Error }
  | { type: "closed" };
type WithPayload = Extract<AppEvent, { payload: unknown }>;
''', "Extract<AppEvent, { payload: unknown }>",
        '''
type _1 = Expect<Equal<WithPayload, { type: "message"; payload: string } | { type: "error"; payload: Error }>>;
''', hints=["One utility type keeps the union members assignable to a shape.", "`Extract<AppEvent, { payload: unknown }>`."]),
])

_more_practice(18, [
    _prt(18, "tsm-w18-t-has-length", "Anything with a length",
        "Write the type parameter of `longest` so it accepts any two values of one type that has a numeric `length` — "
        "arrays, strings — and rejects numbers.",
        '''
declare function longest<T extends { length: number }>(a: T, b: T): T;
''', "<T extends { length: number }>",
        '''
const arr = longest([1, 2], [3]);
type _1 = Expect<Equal<typeof arr, number[]>>;
// @ts-expect-error — a number has no length
longest(1, 2);
''', hints=["Constrain `T` with `extends`.", "The constraint is a shape: `{ length: number }`."]),

    _prt(18, "tsm-w18-t-key-of-arg", "Only keys of the object",
        "Write the signature of `getAll`: it takes an object and a list of its keys, and returns the values at those "
        "keys as an array of the matching value types.",
        '''
declare function getAll<T, K extends keyof T>(obj: T, keys: K[]): T[K][];
''', "<T, K extends keyof T>(obj: T, keys: K[]): T[K][]",
        '''
const user = { id: 1, name: "Ada", admin: true };
const picked = getAll(user, ["id", "name"]);
type _1 = Expect<Equal<typeof picked, (string | number)[]>>;
// @ts-expect-error — "email" is not a key of user
getAll(user, ["email"]);
''', hints=["`K extends keyof T` ties the keys to the object.", "The result is `T[K][]` — an array of the looked-up types."]),
])

_more_practice(19, [
    _prt(19, "tsm-w19-t-tag-of-post", "The type of one tag",
        "`Post` has a list of tags. Write `Tag`: the type of a single element of that list, by indexed access.",
        '''
type Post = { id: number; tags: { label: string; colour: "red" | "blue" }[] };
type Tag = Post["tags"][number];
''', 'Post["tags"][number]',
        '''
type _1 = Expect<Equal<Tag, { label: string; colour: "red" | "blue" }>>;
''', hints=["First look up the `tags` property.", "Then `[number]` gives the element type of an array type."], difficulty="Easy"),

    _prt(19, "tsm-w19-t-colour-of-tag", "Two lookups deep",
        "Write `Colour`: the type of a tag's `colour`, reached from `Post` in one chain of indexed accesses.",
        '''
type Post = { id: number; tags: { label: string; colour: "red" | "blue" }[] };
type Colour = Post["tags"][number]["colour"];
''', 'Post["tags"][number]["colour"]',
        '''
type _1 = Expect<Equal<Colour, "red" | "blue">>;
''', hints=["Indexed accesses chain.", "`Post[\"tags\"][number][\"colour\"]`."], difficulty="Easy"),
])

_more_practice(20, [
    _prt(20, "tsm-w20-t-form-text", "Every field as form text",
        "A form holds every field of a model as the text typed into it. Write `FormText<T>`: the same keys, every "
        "value a `string`, every key required.",
        '''
type FormText<T> = { [K in keyof T]-?: string };
''', "{ [K in keyof T]-?: string }",
        '''
type _1 = Expect<Equal<FormText<{ age: number; name?: string }>, { age: string; name: string }>>;
''', hints=["Map over `keyof T` and ignore the old value type.", "`-?` makes an optional field required."], difficulty="Easy"),

    _prt(20, "tsm-w20-t-readonly-except", "Readonly except one field",
        "Write `ReadonlyExcept<T, K>`: every field read-only except the ones in `K`, which stay writable. "
        "(The checks flatten the result before comparing.)",
        '''
type ReadonlyExcept<T, K extends keyof T> = Readonly<Omit<T, K>> & Pick<T, K>;
''', "Readonly<Omit<T, K>> & Pick<T, K>",
        _SIMPLIFY_T + '''
type Doc = { id: number; title: string; body: string };
type _1 = Expect<Equal<Simplify<ReadonlyExcept<Doc, "body">>, { readonly id: number; readonly title: string; body: string }>>;
''', hints=["Split the type: the part that becomes read-only, and the part that does not.", "`Readonly<Omit<T, K>> & Pick<T, K>`."]),
])

_more_practice(21, [
    _prt(21, "tsm-w21-t-is-async", "Does it return a promise?",
        "Write `IsAsync<F>`: `true` when the function type `F` returns a `Promise`, otherwise `false`.",
        '''
type IsAsync<F> = F extends (...args: never[]) => Promise<unknown> ? true : false;
''', "F extends (...args: never[]) => Promise<unknown> ? true : false",
        '''
type _1 = Expect<Equal<IsAsync<() => Promise<void>>, true>>;
type _2 = Expect<Equal<IsAsync<(n: number) => number>, false>>;
''', hints=["Match the function against a shape whose return is `Promise<unknown>`.", "Parameters: `(...args: never[])` accepts any list."]),

    _prt(21, "tsm-w21-t-tail", "Everything but the first",
        "Write `Tail<T>`: the tuple `T` without its first element; `[]` for an empty tuple.",
        '''
type Tail<T extends unknown[]> = T extends [unknown, ...infer R] ? R : [];
''', "T extends [unknown, ...infer R] ? R : []",
        '''
type _1 = Expect<Equal<Tail<[1, 2, 3]>, [2, 3]>>;
type _2 = Expect<Equal<Tail<["only"]>, []>>;
type _3 = Expect<Equal<Tail<[]>, []>>;
''', hints=["Match `[first, ...rest]` with `infer` on the rest.", "`T extends [unknown, ...infer R] ? R : []`."]),

    _prt(21, "tsm-w21-t-props-of", "The props of a component",
        "A component here is a function taking one props object. Write `PropsOf<C>`: that props type; `never` for "
        "anything else.",
        '''
type PropsOf<C> = C extends (props: infer P) => unknown ? P : never;
''', "C extends (props: infer P) => unknown ? P : never",
        '''
declare function Button(props: { label: string; onClick: () => void }): string;
type _1 = Expect<Equal<PropsOf<typeof Button>, { label: string; onClick: () => void }>>;
type _2 = Expect<Equal<PropsOf<42>, never>>;
''', hints=["`infer` the parameter's type.", "`C extends (props: infer P) => unknown ? P : never`."]),
])

_more_practice(22, [
    _prt(22, "tsm-w22-t-dot-join", "Join two path segments",
        "Write `DotJoin<A, B>`: `A.B`, except that an empty `A` gives just `B`.",
        '''
type DotJoin<A extends string, B extends string> = A extends "" ? B : `${A}.${B}`;
''', 'A extends "" ? B : `${A}.${B}`',
        '''
type _1 = Expect<Equal<DotJoin<"user", "name">, "user.name">>;
type _2 = Expect<Equal<DotJoin<"", "id">, "id">>;
''', hints=["Check for the empty string first.", "Otherwise a template literal joins them with a dot."], difficulty="Easy"),

    _prt(22, "tsm-w22-t-str-length", "The length of a string literal",
        "Write `StrLength<S>`: the number of characters in the string literal `S`, as a number literal. Count with "
        "an accumulator tuple.",
        '''
type StrLength<S extends string, Acc extends unknown[] = []> =
  S extends `${infer _First}${infer Rest}` ? StrLength<Rest, [...Acc, unknown]> : Acc["length"];
''', '''S extends `${infer _First}${infer Rest}` ? StrLength<Rest, [...Acc, unknown]> : Acc["length"]''',
        '''
type _1 = Expect<Equal<StrLength<"hello">, 5>>;
type _2 = Expect<Equal<StrLength<"">, 0>>;
''', hints=["`${infer First}${infer Rest}` takes one character off the front.", "Grow the accumulator by one per character and read its `length` at the end."]),

    _prt(22, "tsm-w22-t-getter-name", "Getter names from keys",
        "Write `GetterName<K>`: `get` followed by the capitalised key. Given a union of keys it must give the union "
        "of getter names.",
        '''
type GetterName<K extends string> = `get${Capitalize<K>}`;
''', "`get${Capitalize<K>}`",
        '''
type _1 = Expect<Equal<GetterName<"id">, "getId">>;
type _2 = Expect<Equal<GetterName<"id" | "name">, "getId" | "getName">>;
''', hints=["A template literal type with `Capitalize`.", "Template literals distribute over unions on their own."], difficulty="Easy"),
])
