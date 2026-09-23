# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Type workshops for the TypeScript Mastery track — graded by the compiler.
#
# Weeks 17-22 are about types: utility types, generics, keyof/indexed access,
# mapped, conditional and template-literal types. Their curated Library
# problems are ordinary stdin/stdout programs, which cannot test a type at all
# (week 21, "Conditional Types & infer", was practising a prefix sum). A type
# has no runtime value to print, so the only honest grader is the compiler.
#
# Each exercise here is a program with the type blanked out, plus a hidden
# harness of `Expect<Equal<…>>` claims appended before type-checking — the same
# `judge_mode: "types"` machinery the TypeScript course's week-10 `proof` lesson
# proved. `Equal` is the identity check from type-challenges: `any`, `unknown`
# and near-miss unions all fail it. A few claims are `// @ts-expect-error`
# lines, which assert that a misuse is REJECTED — a type that accepts too much
# fails those.
#
# Practice is outside the week's gate (chapters + quiz + final), like the
# course's practice families. tests/verify_mastery.rs proves every solution
# type-checks against its claims and every starter does not.
#
# exec()'d inside gen_seed.py's namespace after mastery_defs.py.
# ---------------------------------------------------------------------------

_TW_PRELUDE = """\
// Supplied by the checker. Equal<X, Y> is true only when X and Y are the SAME
// type, not merely assignable to each other.
type Equal<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends (<T>() => T extends Y ? 1 : 2) ? true : false;
type Expect<T extends true> = T;
"""


def _tl(eid, title, prompt, full, blank, checks, hints=(), difficulty="Medium"):
    """A type-level exercise: `blank` (a unique substring of `full`) becomes the
    ____ in the starter; `checks` is the hidden harness of claims."""
    full = full.strip("\n") + "\n"
    assert full.count(blank) == 1, f"{eid}: blank must appear exactly once in the solution"
    starter = full.replace(blank, "____", 1)
    hints = list(hints)
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": "typelevel", "difficulty": difficulty,
        "strictness": "strict",
        "harness": _TW_PRELUDE + "\n" + checks.strip("\n") + "\n",
        "judge_mode": "types", "forbid": [],
        "starter": starter, "solution": full, "tests": [],
        "source_slug": "", "dataset": "",
    }


TS_PRACTICE = {
    # ---- Week 17: utility types ------------------------------------------
    17: [
        _tl("tsm-w17-draft", "A draft has no id yet",
            "Derive `TaskDraft` from `Task` — everything except `id` — with a utility type rather than by writing the fields out.",
            '''
type Task = { id: number; title: string; done: boolean; tags: string[] };
type TaskDraft = Omit<Task, "id">;
''', 'Omit<Task, "id">',
            '''
type _1 = Expect<Equal<TaskDraft, { title: string; done: boolean; tags: string[] }>>;
''', hints=["Which utility type removes keys?", "`Omit<T, K>` keeps every property of `T` except those in `K`."], difficulty="Easy"),
        _tl("tsm-w17-patch", "A patch may change any field but the id",
            "`TaskPatch` is what an update accepts: any subset of the fields, except `id`, which never changes. Build it by composing two utility types.",
            '''
type Task = { id: number; title: string; done: boolean; tags: string[] };
type TaskPatch = Partial<Omit<Task, "id">>;
''', 'Partial<Omit<Task, "id">>',
            '''
type _1 = Expect<Equal<TaskPatch, { title?: string; done?: boolean; tags?: string[] }>>;
''', hints=["Two steps: drop `id`, then make what is left optional.", "`Partial<Omit<Task, \"id\">>`."]),
        _tl("tsm-w17-summary", "Only what the list view needs",
            "The task list shows just `id` and `title`. Derive `TaskSummary` from `Task`.",
            '''
type Task = { id: number; title: string; done: boolean; tags: string[] };
type TaskSummary = Pick<Task, "id" | "title">;
''', 'Pick<Task, "id" | "title">',
            '''
type _1 = Expect<Equal<TaskSummary, { id: number; title: string }>>;
''', hints=["Which utility keeps only the keys you name?", "`Pick<T, K>` — and `K` can be a union of keys."], difficulty="Easy"),
        _tl("tsm-w17-totals", "A total for every status",
            "`Totals` must have exactly one number per status — no more, no fewer. Build it from `Status`.",
            '''
type Status = "open" | "blocked" | "done";
type Totals = Record<Status, number>;
''', 'Record<Status, number>',
            '''
type _1 = Expect<Equal<Totals, { open: number; blocked: number; done: number }>>;
''', hints=["You want an object type whose keys are the members of a union.", "`Record<K, V>`."], difficulty="Easy"),
        _tl("tsm-w17-finished", "Which statuses are final",
            "From `Status`, derive `Finished`: every status except `\"idle\"` and `\"loading\"`.",
            '''
type Status = "idle" | "loading" | "done" | "error";
type Finished = Exclude<Status, "idle" | "loading">;
''', 'Exclude<Status, "idle" | "loading">',
            '''
type _1 = Expect<Equal<Finished, "done" | "error">>;
''', hints=["`Omit` works on object keys; you are filtering a union.", "`Exclude<Union, Removed>`."], difficulty="Easy"),
        _tl("tsm-w17-returntype", "Name what a factory makes",
            "`makeUser` is the single source of truth for a user's shape. Derive `User` from it, so the two can never drift apart.",
            '''
function makeUser(name: string) {
  return { name, createdAt: 0, admin: false };
}
type User = ReturnType<typeof makeUser>;
''', 'ReturnType<typeof makeUser>',
            '''
type _1 = Expect<Equal<User, { name: string; createdAt: number; admin: boolean }>>;
''', hints=["A utility type can read a function's return type.", "It takes a *type*, and `makeUser` is a value — lift it with `typeof`."]),
        _tl("tsm-w17-awaited", "What does an async function give you?",
            "`loadScores` is async. Derive `Scores` — the value you get *after* awaiting it — from the function itself.",
            '''
async function loadScores() {
  return [3, 1, 2];
}
type Scores = Awaited<ReturnType<typeof loadScores>>;
''', 'Awaited<ReturnType<typeof loadScores>>',
            '''
type _1 = Expect<Equal<Scores, number[]>>;
''', hints=["`ReturnType` gives you `Promise<number[]>` — one step short.", "Unwrap the promise with `Awaited<…>`."]),
    ],

    # ---- Week 18: generics & constraints ---------------------------------
    18: [
        _tl("tsm-w18-first", "First, for any element type",
            "Write the signature of `first` so it works for an array of anything and returns that element type — or `undefined` for an empty array.",
            '''
function first<T>(xs: T[]): T | undefined {
  return xs[0];
}
''', '<T>(xs: T[]): T | undefined',
            '''
const n = first([1, 2, 3]);
const s = first(["a"]);
type _1 = Expect<Equal<typeof n, number | undefined>>;
type _2 = Expect<Equal<typeof s, string | undefined>>;
''', hints=["A type parameter links the input's element type to the output.", "`<T>(xs: T[]): T | undefined`."], difficulty="Easy"),
        _tl("tsm-w18-pluck", "Pluck a real key",
            "`pluck(rows, key)` returns the `key` column. Type it so the key must exist on the rows and the result is an array of that column's type.",
            '''
function pluck<T, K extends keyof T>(rows: T[], key: K): T[K][] {
  return rows.map((r) => r[key]);
}
''', '<T, K extends keyof T>(rows: T[], key: K): T[K][]',
            '''
const rows = [{ name: "ada", age: 36 }];
const names = pluck(rows, "name");
const ages = pluck(rows, "age");
type _1 = Expect<Equal<typeof names, string[]>>;
type _2 = Expect<Equal<typeof ages, number[]>>;
// @ts-expect-error — "email" is not a key of the rows
pluck(rows, "email");
''', hints=["The key's type should be constrained to the row's keys.", "`K extends keyof T`, and the column type is `T[K]`."]),
        _tl("tsm-w18-longest", "Keep the caller's type",
            "`longest` returns whichever argument is longer. Type it so it accepts anything with a numeric `length` and returns the caller's own type — not `{ length: number }`.",
            '''
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
''', '<T extends { length: number }>(a: T, b: T): T',
            '''
const arr = longest([1, 2], [3]);
type _1 = Expect<Equal<typeof arr, number[]>>;
// @ts-expect-error — numbers have no length
longest(1, 2);
''', hints=["A plain `{ length: number }` parameter would throw the caller's type away.", "Constrain a type parameter instead: `<T extends { length: number }>`."]),
        _tl("tsm-w18-groupby", "Group by a computed key",
            "Type `groupBy` so the map's keys have the type the key function returns, and its values keep the element type.",
            '''
function groupBy<T, K>(items: T[], keyOf: (item: T) => K): Map<K, T[]> {
  const out = new Map<K, T[]>();
  for (const item of items) {
    const k = keyOf(item);
    const bucket = out.get(k);
    if (bucket) bucket.push(item);
    else out.set(k, [item]);
  }
  return out;
}
''', '<T, K>(items: T[], keyOf: (item: T) => K): Map<K, T[]>',
            '''
const byLength = groupBy(["a", "bb", "cc"], (w) => w.length);
type _1 = Expect<Equal<typeof byLength, Map<number, string[]>>>;
''', hints=["Two type parameters: the element and the key.", "`<T, K>(items: T[], keyOf: (item: T) => K): Map<K, T[]>`."]),
        _tl("tsm-w18-stack", "A stack that keeps its type",
            "Complete `pop`'s signature: it returns the element type, or `undefined` when the stack is empty.",
            '''
class Stack<T> {
  private items: T[] = [];
  push(item: T): void {
    this.items.push(item);
  }
  pop(): T | undefined {
    return this.items.pop();
  }
}
''', 'pop(): T | undefined',
            '''
const s = new Stack<string>();
s.push("a");
const top = s.pop();
type _1 = Expect<Equal<typeof top, string | undefined>>;
// @ts-expect-error — a Stack<string> only takes strings
s.push(1);
''', hints=["The class's type parameter is in scope inside its methods.", "`pop(): T | undefined` — an empty stack has nothing to give."], difficulty="Easy"),
        _tl("tsm-w18-merge", "Merge two objects",
            "Type `merge` so its result has every property of both arguments. Both must be objects.",
            '''
function merge<A extends object, B extends object>(a: A, b: B): A & B {
  return { ...a, ...b };
}
''', '<A extends object, B extends object>(a: A, b: B): A & B',
            '''
const m = merge({ id: 1 }, { name: "ada" });
type _1 = Expect<Equal<typeof m, { id: number } & { name: string }>>;
// @ts-expect-error — 5 is not an object
merge(5, { name: "ada" });
''', hints=["Two type parameters, each constrained to `object`.", "\"Every property of both\" is an intersection: `A & B`."]),
        _tl("tsm-w18-noinfer", "The fallback must be one of the options",
            "`pick(options, fallback)` returns one of `options`. Stop the fallback from widening `T` — a fallback that isn't one of the options must be an error.",
            '''
function pick<T extends string>(options: T[], fallback: NoInfer<T>): T {
  return options[0] ?? fallback;
}
''', 'NoInfer<T>',
            '''
const p = pick(["small", "large"], "small");
type _1 = Expect<Equal<typeof p, "small" | "large">>;
// @ts-expect-error — "huge" is not one of the options
pick(["small", "large"], "huge");
''', hints=["Without help, `T` is inferred from both arguments, so `\"huge\"` joins the union.", "TypeScript 5.4's `NoInfer<T>` blocks inference from the parameter it wraps."], difficulty="Hard"),
    ],

    # ---- Week 19: keyof, typeof & indexed access --------------------------
    19: [
        _tl("tsm-w19-keys", "Every setting name",
            "Derive `Setting` — the union of setting names — from the `SETTINGS` object, so adding a setting is one edit.",
            '''
const SETTINGS = { theme: "dark", size: 14, wrap: true } as const;
type Setting = keyof typeof SETTINGS;
''', 'keyof typeof SETTINGS',
            '''
type _1 = Expect<Equal<Setting, "theme" | "size" | "wrap">>;
''', hints=["`SETTINGS` is a value; get its type first.", "`keyof typeof SETTINGS`."], difficulty="Easy"),
        _tl("tsm-w19-values", "Every default value",
            "Derive `SettingValue` — the union of the *values* in `SETTINGS`.",
            '''
const SETTINGS = { theme: "dark", size: 14, wrap: true } as const;
type SettingValue = (typeof SETTINGS)[keyof typeof SETTINGS];
''', '(typeof SETTINGS)[keyof typeof SETTINGS]',
            '''
type _1 = Expect<Equal<SettingValue, "dark" | 14 | true>>;
''', hints=["Index a type with a union of its keys to get a union of its values.", "`T[keyof T]`, where `T` is `typeof SETTINGS`."]),
        _tl("tsm-w19-level", "A union from a list",
            "Derive `Level` from the `LEVELS` array, so the list is the single source of truth.",
            '''
const LEVELS = ["debug", "info", "warn", "error"] as const;
type Level = (typeof LEVELS)[number];
''', '(typeof LEVELS)[number]',
            '''
type _1 = Expect<Equal<Level, "debug" | "info" | "warn" | "error">>;
''', hints=["Indexing an array type by `number` gives its element type.", "`(typeof LEVELS)[number]` — and it only works because of `as const`."], difficulty="Easy"),
        _tl("tsm-w19-nested", "Reach inside a type",
            "Without repeating `string`, name the type of one tag inside a user's profile.",
            '''
type User = { id: number; profile: { email: string; tags: string[] } };
type Tag = User["profile"]["tags"][number];
''', 'User["profile"]["tags"][number]',
            '''
type _1 = Expect<Equal<Tag, string>>;
''', hints=["Indexed access chains: `A[\"x\"][\"y\"]`.", "Then `[number]` for an element of the array."]),
        _tl("tsm-w19-get", "A lookup that knows the value type",
            "Type `get(obj, key)` so the key must exist and the result is that key's value type.",
            '''
function get<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
''', '<T, K extends keyof T>(obj: T, key: K): T[K]',
            '''
const user = { name: "ada", age: 36 };
const age = get(user, "age");
type _1 = Expect<Equal<typeof age, number>>;
// @ts-expect-error — no such key
get(user, "email");
''', hints=["The key's type must come from the object's keys.", "`K extends keyof T`, returning `T[K]`."]),
        _tl("tsm-w19-valuesof", "ValuesOf, generically",
            "Write `ValuesOf<T>`: the union of an object type's value types.",
            '''
type ValuesOf<T> = T[keyof T];
''', 'T[keyof T]',
            '''
type _1 = Expect<Equal<ValuesOf<{ a: 1; b: "x" }>, 1 | "x">>;
type _2 = Expect<Equal<ValuesOf<{ only: boolean }>, boolean>>;
''', hints=["The same trick as `SettingValue`, but for any `T`.", "`T[keyof T]`."], difficulty="Easy"),
    ],

    # ---- Week 20: mapped types --------------------------------------------
    20: [
        _tl("tsm-w20-partial", "Partial, by hand",
            "Implement `MyPartial<T>` without using `Partial`.",
            '''
type MyPartial<T> = { [K in keyof T]?: T[K] };
''', '{ [K in keyof T]?: T[K] }',
            '''
type _1 = Expect<Equal<MyPartial<{ a: number; b: string }>, { a?: number; b?: string }>>;
''', hints=["Loop over the keys with `[K in keyof T]`.", "Add `?` after the key: `[K in keyof T]?: T[K]`."], difficulty="Easy"),
        _tl("tsm-w20-readonly", "Readonly, by hand",
            "Implement `MyReadonly<T>` without using `Readonly`.",
            '''
type MyReadonly<T> = { readonly [K in keyof T]: T[K] };
''', '{ readonly [K in keyof T]: T[K] }',
            '''
type _1 = Expect<Equal<MyReadonly<{ a: number }>, { readonly a: number }>>;
''', hints=["The modifier goes before the key.", "`{ readonly [K in keyof T]: T[K] }`."], difficulty="Easy"),
        _tl("tsm-w20-pick", "Pick, by hand",
            "Implement `MyPick<T, K>`: only the keys in `K`, which must be keys of `T`.",
            '''
type MyPick<T, K extends keyof T> = { [P in K]: T[P] };
''', '{ [P in K]: T[P] }',
            '''
type Todo = { title: string; done: boolean; notes: string };
type _1 = Expect<Equal<MyPick<Todo, "title" | "done">, { title: string; done: boolean }>>;
// @ts-expect-error — "missing" is not a key of Todo
type _2 = MyPick<Todo, "missing">;
''', hints=["Map over `K` rather than over `keyof T`.", "`{ [P in K]: T[P] }`."]),
        _tl("tsm-w20-mutable", "Take readonly away",
            "Implement `Mutable<T>`, which removes `readonly` from every property.",
            '''
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
''', '{ -readonly [K in keyof T]: T[K] }',
            '''
type _1 = Expect<Equal<Mutable<{ readonly a: number; readonly b: string }>, { a: number; b: string }>>;
''', hints=["Modifiers can be removed as well as added.", "`-readonly` before the key."]),
        _tl("tsm-w20-nullable", "Every field may be null",
            "Implement `Nullable<T>`: the same keys, each value also allowed to be `null`.",
            '''
type Nullable<T> = { [K in keyof T]: T[K] | null };
''', '{ [K in keyof T]: T[K] | null }',
            '''
type _1 = Expect<Equal<Nullable<{ a: number; b: string }>, { a: number | null; b: string | null }>>;
''', hints=["Transform the value type, keep the key.", "`T[K] | null`."], difficulty="Easy"),
        _tl("tsm-w20-getters", "Getters from fields",
            "Implement `Getters<T>`: for each key `name`, a method `getName` returning that field's type. Use key remapping.",
            '''
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
''', '{ [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] }',
            '''
type _1 = Expect<Equal<Getters<{ name: string; age: number }>, { getName: () => string; getAge: () => number }>>;
''', hints=["Key remapping uses `as` after the key: `[K in keyof T as …]`.", "Build the name with a template literal and `Capitalize`; intersect with `string` because keys can also be numbers or symbols."], difficulty="Hard"),
        _tl("tsm-w20-pickbyvalue", "Keep only the string fields",
            "Implement `PickByValue<T, V>`: only the properties whose value type is assignable to `V`.",
            '''
type PickByValue<T, V> = { [K in keyof T as T[K] extends V ? K : never]: T[K] };
''', '{ [K in keyof T as T[K] extends V ? K : never]: T[K] }',
            '''
type Row = { id: number; name: string; email: string; admin: boolean };
type _1 = Expect<Equal<PickByValue<Row, string>, { name: string; email: string }>>;
''', hints=["Remapping a key to `never` removes it.", "`as T[K] extends V ? K : never`."], difficulty="Hard"),
    ],

    # ---- Week 21: conditional types & infer --------------------------------
    21: [
        _tl("tsm-w21-exclude", "Exclude, by hand",
            "Implement `MyExclude<T, U>`: the members of union `T` not assignable to `U`.",
            '''
type MyExclude<T, U> = T extends U ? never : T;
''', 'T extends U ? never : T',
            '''
type _1 = Expect<Equal<MyExclude<"a" | "b" | "c", "a">, "b" | "c">>;
type _2 = Expect<Equal<MyExclude<string | number | boolean, number>, string | boolean>>;
''', hints=["A conditional type over a naked type parameter distributes over the union.", "Return `never` for the members you want gone."], difficulty="Easy"),
        _tl("tsm-w21-returntype", "ReturnType, by hand",
            "Implement `MyReturnType<F>` with `infer`.",
            '''
type MyReturnType<F> = F extends (...args: any[]) => infer R ? R : never;
''', 'F extends (...args: any[]) => infer R ? R : never',
            '''
type _1 = Expect<Equal<MyReturnType<() => string>, string>>;
type _2 = Expect<Equal<MyReturnType<(a: number, b: number) => boolean>, boolean>>;
''', hints=["Match `F` against a function type and capture the return position.", "`F extends (...args: any[]) => infer R ? R : never`."]),
        _tl("tsm-w21-parameters", "Parameters, by hand",
            "Implement `MyParameters<F>`: the parameter list of a function type, as a tuple.",
            '''
type MyParameters<F> = F extends (...args: infer P) => any ? P : never;
''', 'F extends (...args: infer P) => any ? P : never',
            '''
type _1 = Expect<Equal<MyParameters<(a: number, b: string) => void>, [a: number, b: string]>>;
type _2 = Expect<Equal<MyParameters<() => void>, []>>;
''', hints=["Capture the rest-parameter position.", "`(...args: infer P) => any`."]),
        _tl("tsm-w21-awaited", "Unwrap every promise",
            "Implement `Unpromise<T>`: the value inside any number of nested promises (and `T` itself when it's not a promise).",
            '''
type Unpromise<T> = T extends Promise<infer V> ? Unpromise<V> : T;
''', 'T extends Promise<infer V> ? Unpromise<V> : T',
            '''
type _1 = Expect<Equal<Unpromise<Promise<number>>, number>>;
type _2 = Expect<Equal<Unpromise<Promise<Promise<string>>>, string>>;
type _3 = Expect<Equal<Unpromise<boolean>, boolean>>;
''', hints=["Capture the promise's value with `infer`.", "Then recurse on what you captured."]),
        _tl("tsm-w21-elementof", "Element type, or the type itself",
            "Implement `Unwrap<T>`: the element type when `T` is an array, otherwise `T`.",
            '''
type Unwrap<T> = T extends (infer E)[] ? E : T;
''', 'T extends (infer E)[] ? E : T',
            '''
type _1 = Expect<Equal<Unwrap<number[]>, number>>;
type _2 = Expect<Equal<Unwrap<string>, string>>;
''', hints=["Match against an array type and capture its element.", "`(infer E)[]` — note the parentheses."], difficulty="Easy"),
        _tl("tsm-w21-first-last", "The last element of a tuple",
            "Implement `Last<T>`: the type of a tuple's last element, `never` for an empty tuple.",
            '''
type Last<T extends unknown[]> = T extends [...unknown[], infer L] ? L : never;
''', 'T extends [...unknown[], infer L] ? L : never',
            '''
type _1 = Expect<Equal<Last<[1, 2, 3]>, 3>>;
type _2 = Expect<Equal<Last<["only"]>, "only">>;
type _3 = Expect<Equal<Last<[]>, never>>;
''', hints=["A variadic tuple pattern can put the rest *first*.", "`[...unknown[], infer L]`."]),
        _tl("tsm-w21-isnever", "Is it never?",
            "Implement `IsNever<T>`: `true` exactly when `T` is `never`.",
            '''
type IsNever<T> = [T] extends [never] ? true : false;
''', '[T] extends [never] ? true : false',
            '''
type _1 = Expect<Equal<IsNever<never>, true>>;
type _2 = Expect<Equal<IsNever<string>, false>>;
type _3 = Expect<Equal<IsNever<undefined>, false>>;
''', hints=["`T extends never ? … : …` distributes over zero members and returns `never` itself.", "Wrap both sides in a one-element tuple to stop distribution."], difficulty="Hard"),
        _tl("tsm-w21-unwrap-result", "The success type of a Result",
            "`Result` is a discriminated union. Implement `OkValue<R>`: the `value` type of its success member.",
            '''
type Result<T, E = string> = { ok: true; value: T } | { ok: false; error: E };
type OkValue<R> = R extends { ok: true; value: infer V } ? V : never;
''', 'R extends { ok: true; value: infer V } ? V : never',
            '''
type _1 = Expect<Equal<OkValue<Result<number>>, number>>;
type _2 = Expect<Equal<OkValue<Result<string[], Error>>, string[]>>;
''', hints=["Distribution runs the condition once per member.", "Match the success member's shape and `infer` its `value`."]),
    ],

    # ---- Week 22: template literals & recursive types ----------------------
    22: [
        _tl("tsm-w22-events", "Every event name",
            "Derive `EventName` from the two lists: every `entity:action` combination.",
            '''
const ENTITIES = ["user", "order"] as const;
const ACTIONS = ["created", "deleted"] as const;
type EventName = `${(typeof ENTITIES)[number]}:${(typeof ACTIONS)[number]}`;
''', '`${(typeof ENTITIES)[number]}:${(typeof ACTIONS)[number]}`',
            '''
type _1 = Expect<Equal<EventName, "user:created" | "user:deleted" | "order:created" | "order:deleted">>;
''', hints=["Each list becomes a union with `(typeof X)[number]`.", "A template literal over two unions produces every combination."]),
        _tl("tsm-w22-trimleft", "Trim the left",
            "Implement `TrimLeft<S>`: `S` without its leading spaces.",
            '''
type TrimLeft<S extends string> = S extends ` ${infer Rest}` ? TrimLeft<Rest> : S;
''', 'S extends ` ${infer Rest}` ? TrimLeft<Rest> : S',
            '''
type _1 = Expect<Equal<TrimLeft<"   hello">, "hello">>;
type _2 = Expect<Equal<TrimLeft<"x ">, "x ">>;
''', hints=["Match one leading space and capture the rest.", "Recurse until there's no leading space."]),
        _tl("tsm-w22-params", "Route parameters",
            "Implement `Params<Path>`: the union of `:name` segments in a route like `\"/users/:id/posts/:postId\"`.",
            '''
type Params<Path extends string> =
  Path extends `${string}:${infer P}/${infer Rest}` ? P | Params<Rest>
  : Path extends `${string}:${infer P}` ? P
  : never;
''', '''Path extends `${string}:${infer P}/${infer Rest}` ? P | Params<Rest>
  : Path extends `${string}:${infer P}` ? P
  : never''',
            '''
type _1 = Expect<Equal<Params<"/users/:id/posts/:postId">, "id" | "postId">>;
type _2 = Expect<Equal<Params<"/about">, never>>;
''', hints=["Two cases: a parameter followed by more path, and a parameter at the very end.", "Collect each captured name into a union, recursing on the rest."], difficulty="Hard"),
        _tl("tsm-w22-reverse", "Reverse a tuple",
            "Implement `Reverse<T>`.",
            '''
type Reverse<T extends unknown[]> = T extends [infer H, ...infer R] ? [...Reverse<R>, H] : [];
''', 'T extends [infer H, ...infer R] ? [...Reverse<R>, H] : []',
            '''
type _1 = Expect<Equal<Reverse<[1, 2, 3]>, [3, 2, 1]>>;
type _2 = Expect<Equal<Reverse<[]>, []>>;
''', hints=["Peel off the head, reverse the rest, put the head at the end.", "`[...Reverse<R>, H]`."]),
        _tl("tsm-w22-length", "The length of a tuple",
            "Implement `Length<T>` for a tuple: its length as a number literal.",
            '''
type Length<T extends readonly unknown[]> = T["length"];
''', 'T["length"]',
            '''
type _1 = Expect<Equal<Length<[1, 2, 3]>, 3>>;
type _2 = Expect<Equal<Length<readonly ["a"]>, 1>>;
''', hints=["A tuple's `length` property has a literal type.", "`T[\"length\"]`."], difficulty="Easy"),
        _tl("tsm-w22-camel", "snake_case to camelCase",
            "Implement `Camel<S>`: `\"foo_bar_baz\"` becomes `\"fooBarBaz\"`.",
            '''
type Camel<S extends string> = S extends `${infer Head}_${infer Tail}` ? `${Head}${Capitalize<Camel<Tail>>}` : S;
''', 'S extends `${infer Head}_${infer Tail}` ? `${Head}${Capitalize<Camel<Tail>>}` : S',
            '''
type _1 = Expect<Equal<Camel<"foo_bar_baz">, "fooBarBaz">>;
type _2 = Expect<Equal<Camel<"plain">, "plain">>;
''', hints=["Split at the first underscore.", "Capitalize the camel-cased tail and glue it to the head."], difficulty="Hard"),
        _tl("tsm-w22-json", "A type for any JSON value",
            "Define `Json` so that any value `JSON.parse` could return is assignable to it — and a function is not.",
            '''
type Json = string | number | boolean | null | Json[] | { [key: string]: Json };
''', 'string | number | boolean | null | Json[] | { [key: string]: Json }',
            '''
const ok1: Json = { a: [1, "two", { b: null }], c: true };
const ok2: Json = [[], {}];
// @ts-expect-error — functions are not JSON
const bad: Json = { f: () => 1 };
void ok1; void ok2; void bad;
''', hints=["Four primitive cases, then arrays and objects of JSON.", "The type refers to itself inside `Json[]` and the object type."]),
    ],
}

# ===========================================================================
# Weeks 1-16: reading practice — predict, read the error, fix the bug.
#
# Most of using TypeScript is reading: an inference you didn't write, an error
# the compiler raised, a program that compiles and is still wrong. These are
# the TypeScript course's reading kinds, rebuilt for the Mastery weeks:
#
#   predict  — annotate `check` with the type the compiler already infers for
#              an expression. Graded by `Equal<typeof check, typeof expr>` —
#              the learner's answer against the compiler's real opinion — with
#              `typeof` banned so the answer can't be copied from the question.
#   diagnose — a program that genuinely fails to compile, with the compiler's
#              message quoted. The verifier re-derives the quoted TSnnnn code
#              from the starter, so the prompt cannot drift from the compiler.
#   fix      — a program that compiles and is wrong at runtime. Judged on
#              stdout; the starter fails the tests.
# ===========================================================================

_STDIN = 'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8").trim();\n'


def _pr(eid, title, code, expr, answer, hints=(), strictness="strict", why=""):
    """Predict the inferred type of `expr` (an identifier or dotted path)."""
    code = code.strip("\n") + "\n"
    assert "typeof" not in code, f"{eid}: the scene may not use typeof (it is banned for the learner)"
    line = "const check: {} = " + expr + ";\n"
    prompt = (f"What type does TypeScript already infer for `{expr}`? Annotate `check` with exactly "
              f"that type — not merely one that fits." + (f" {why}" if why else ""))
    hints = list(hints)
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": "predict", "difficulty": "Easy",
        "strictness": strictness,
        "harness": _TW_PRELUDE + f"\ntype _1 = Expect<Equal<typeof check, typeof {expr}>>;\n",
        "judge_mode": "types", "forbid": ["typeof"],
        "starter": code + line.format("____"), "solution": code + line.format(answer),
        "tests": [], "source_slug": "", "dataset": "",
    }


def _run(eid, title, kind, prompt, broken, fixed, tests, hints=(), strictness="strict", difficulty="Easy"):
    """A whole-program exercise judged on stdout: `broken` is what the learner
    is handed, `fixed` the reference. `tests` are (stdin, expected stdout)."""
    broken = broken.strip("\n") + "\n"
    fixed = fixed.strip("\n") + "\n"
    assert broken != fixed, f"{eid}: starter equals solution"
    assert tests, f"{eid}: needs tests"
    hints = list(hints)
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "", "hints": hints,
        "language": "typescript", "kind": kind, "difficulty": difficulty,
        "strictness": strictness, "harness": "", "judge_mode": "", "forbid": [],
        "starter": broken, "solution": fixed,
        "tests": [{"input": i, "output": o} for (i, o) in tests],
        "source_slug": "", "dataset": "",
    }


def _dx(eid, title, error, broken, fixed, tests, ask="Fix the cause.", **kw):
    """Read a real compiler error — quoted with its TSnnnn code — and repair it."""
    assert "TS" in error, f"{eid}: quote the compiler's TSnnnn code"
    prompt = f"The compiler rejects this program:\n\n    {error}\n\n{ask}"
    return _run(eid, title, "diagnose", prompt, broken, fixed, tests, **kw)


def _fx(eid, title, prompt, broken, fixed, tests, **kw):
    """It compiles, and it is wrong. Find the bug."""
    return _run(eid, title, "fix", prompt, broken, fixed, tests, **kw)


TS_PRACTICE_READING = {
    1: [
        _pr("tsm-w1-p1", "A const number", "const answer = 42;\n", "answer", "42",
            hints=["A `const` can never hold anything else.", "The literal type: `42`."]),
        _pr("tsm-w1-p2", "A let number", "let total = 0;\n", "total", "number",
            hints=["A `let` can be reassigned, so its type widens.", "`number`."]),
        _pr("tsm-w1-p3", "Mixing with +", 'const label = "items: " + 3;\n', "label", "string",
            hints=["`+` with a string operand concatenates.", "The result is a `string`."]),
        _dx("tsm-w1-d1", "Counting up",
            "error TS2588: Cannot assign to 'count' because it is a constant.",
            "let start = 0;\nconst count = start;\ncount = count + 1;\nconsole.log(count);\n",
            "let start = 0;\nlet count = start;\ncount = count + 1;\nconsole.log(count);\n",
            [("", "1")], hints=["Which binding is being reassigned?", "A value that changes needs `let`."]),
        _dx("tsm-w1-d2", "A price that is text",
            "error TS2322: Type 'string' is not assignable to type 'number'.",
            'const price: number = "9.99";\nconsole.log(price * 2);\n',
            'const price: number = 9.99;\nconsole.log(price * 2);\n',
            [("", "19.98")], hints=["The annotation is right; the value is the wrong kind.", "Write the number without quotes."]),
    ],
    2: [
        _pr("tsm-w2-p1", "A comparison", "const isAdult = 20 >= 18;\n", "isAdult", "boolean",
            hints=["What do comparison operators produce?", "`boolean` — the compiler doesn't evaluate `20 >= 18` for you."]),
        _pr("tsm-w2-p2", "Two literal branches", 'const answer = Math.random() > 0.5 ? "yes" : "no";\n', "answer", '"yes" | "no"',
            hints=["A `const` keeps literal types.", "Each branch contributes its literal: a union of the two."]),
        _dx("tsm-w2-d1", "A status that can't happen",
            "error TS2367: This comparison appears to be unintentional because the types 'Status' and '\"finished\"' have no overlap.",
            'type Status = "idle" | "done";\nconst status: Status = Math.random() > 2 ? "done" : "idle";\nif (status === "finished") console.log("all done");\nelse console.log("working");\n',
            'type Status = "idle" | "done";\nconst status: Status = Math.random() > 2 ? "done" : "idle";\nif (status === "done") console.log("all done");\nelse console.log("working");\n',
            [("", "working")], hints=["Compare against a value the type allows.", "The finished state is spelled `\"done\"`."]),
        _fx("tsm-w2-f1", "Zero is a real answer",
            "Read a quantity (possibly empty). An empty line means 1; any number — including 0 — must be kept. The program turns 0 into 1.",
            _STDIN + 'const parsed: number | undefined = input === "" ? undefined : Number(input);\nconst qty = parsed || 1;\nconsole.log(qty);\n',
            _STDIN + 'const parsed: number | undefined = input === "" ? undefined : Number(input);\nconst qty = parsed ?? 1;\nconsole.log(qty);\n',
            [("0", "0"), ("", "1"), ("5", "5")], hints=["Which operator treats 0 as missing?", "`??` only replaces `null` and `undefined`."]),
    ],
    3: [
        _pr("tsm-w3-p1", "A big integer", "let big = 10n;\n", "big", "bigint",
            hints=["The `n` suffix makes a different primitive.", "A `let` widens it to `bigint`."]),
        _pr("tsm-w3-p2", "Division", "const average = (3 + 4) / 2;\n", "average", "number",
            hints=["Arithmetic is not evaluated by the type checker.", "`number` — there is no separate integer or float type."]),
        _fx("tsm-w3-f1", "Sum from 1 to n",
            "Read n and print 1 + 2 + … + n. The loop stops one short.",
            _STDIN + "const n = Number(input);\nlet sum = 0;\nfor (let i = 1; i < n; i++) sum += i;\nconsole.log(sum);\n",
            _STDIN + "const n = Number(input);\nlet sum = 0;\nfor (let i = 1; i <= n; i++) sum += i;\nconsole.log(sum);\n",
            [("3", "6"), ("1", "1"), ("5", "15")], hints=["Is `n` itself included?", "`i <= n`."]),
        _dx("tsm-w3-d1", "Adding to a bigint",
            "error TS2365: Operator '+' cannot be applied to types '10n' and '1'.",
            "const total = 10n + 1;\nconsole.log(String(total));\n",
            "const total = 10n + 1n;\nconsole.log(String(total));\n",
            [("", "11")], hints=["Both sides of the `+` must be the same kind of number.", "Write the one as `1n`."]),
    ],
    4: [
        _pr("tsm-w4-p1", "Splitting text", 'const parts = "a,b".split(",");\n', "parts", "string[]",
            hints=["What does `split` return?", "An array of strings."]),
        _pr("tsm-w4-p2", "The first character", 'const first = "hello".at(0);\n', "first", "string | undefined",
            hints=["`at` could be given an index past the end.", "`string | undefined`."]),
        _dx("tsm-w4-d1", "A misspelled property",
            "error TS2551: Property 'lenght' does not exist on type '\"hello\"'. Did you mean 'length'?",
            'const word = "hello";\nconsole.log(word.lenght);\n',
            'const word = "hello";\nconsole.log(word.length);\n',
            [("", "5")], hints=["Read the suggestion at the end of the message."]),
        _fx("tsm-w4-f1", "Replace every dash",
            "Read a line and print it with every `-` replaced by `+`. Only the first one changes.",
            _STDIN + 'console.log(input.replace("-", "+"));\n',
            _STDIN + 'console.log(input.replaceAll("-", "+"));\n',
            [("x-y-z", "x+y+z"), ("a-b", "a+b"), ("none", "none")], hints=["A string pattern in `replace` replaces only the first match.", "`replaceAll`, or a regex with the `g` flag."]),
    ],
    5: [
        _pr("tsm-w5-p1", "What a function returns",
            "function double(n: number) {\n  return n * 2;\n}\nconst result = double(4);\n", "result", "number",
            hints=["The return type is inferred from the `return` expression."]),
        _pr("tsm-w5-p2", "A return that might not happen",
            'function maybe(flag: boolean) {\n  if (flag) return "yes";\n}\nconst reply = maybe(true);\n', "reply", '"yes" | undefined',
            hints=["What does the function return when `flag` is false?", "Falling off the end returns `undefined`."]),
        _dx("tsm-w5-d1", "A missing argument",
            "error TS2554: Expected 2 arguments, but got 1.",
            'function greet(name: string, greeting: string): string {\n  return greeting + ", " + name;\n}\nconsole.log(greet("Ada"));\n',
            'function greet(name: string, greeting = "Hello"): string {\n  return greeting + ", " + name;\n}\nconsole.log(greet("Ada"));\n',
            [("", "Hello, Ada")], ask="Make the greeting optional, defaulting to \"Hello\".",
            hints=["A parameter with a default can be left out.", '`greeting = "Hello"`.']),
        _dx("tsm-w5-d2", "An untyped parameter",
            "error TS7006: Parameter 'n' implicitly has an 'any' type.",
            "function square(n) {\n  return n * n;\n}\nconsole.log(square(7));\n",
            "function square(n: number): number {\n  return n * n;\n}\nconsole.log(square(7));\n",
            [("", "49")], hints=["Parameters can't be inferred from their use.", "Annotate it: `n: number`."]),
    ],
    6: [
        _pr("tsm-w6-p1", "Mapping to lengths", 'const lengths = ["a", "bb"].map((s) => s.length);\n', "lengths", "number[]",
            hints=["`map` returns an array of whatever the callback returns."]),
        _pr("tsm-w6-p2", "A curried adder",
            "const add = (a: number) => (b: number) => a + b;\nconst addTwo = add(2);\n", "addTwo", "(b: number) => number",
            hints=["Calling `add` returns the inner function.", "A function type: `(b: number) => number`."]),
        _fx("tsm-w6-f1", "parseInt in map",
            "Read numbers on one line and print their sum. The sum comes out as NaN.",
            _STDIN + 'const nums = input.split(" ").map(parseInt);\nconsole.log(nums.reduce((a, b) => a + b, 0));\n',
            _STDIN + 'const nums = input.split(" ").map((s) => parseInt(s, 10));\nconsole.log(nums.reduce((a, b) => a + b, 0));\n',
            [("1 2 3", "6"), ("10", "10"), ("4 4", "8")], hints=["`map` passes more than the element.", "`parseInt` takes a radix as its second argument — and gets the index."]),
        _fx("tsm-w6-f2", "Recursion without a floor",
            "Read n and print 1 + … + n recursively. It never stops.",
            _STDIN + "function sumTo(n: number): number {\n  return n + sumTo(n - 1);\n}\nconsole.log(sumTo(Number(input)));\n",
            _STDIN + "function sumTo(n: number): number {\n  if (n <= 0) return 0;\n  return n + sumTo(n - 1);\n}\nconsole.log(sumTo(Number(input)));\n",
            [("4", "10"), ("1", "1"), ("0", "0")], hints=["Every recursion needs a case that doesn't recurse.", "Return 0 when n reaches 0."]),
    ],
    7: [
        _pr("tsm-w7-p1", "A mixed array", 'const mixed = [1, "a"];\n', "mixed", "(string | number)[]",
            hints=["An array literal infers an array, not a tuple.", "The element type is the union of what's in it."]),
        _pr("tsm-w7-p2", "Finding something", "const found = [1, 2, 3].find((n) => n > 1);\n", "found", "number | undefined",
            hints=["What if nothing matches?", "`find` returns `undefined` then."]),
        _fx("tsm-w7-f1", "Sorting numbers",
            "Read numbers on one line and print them in ascending order.",
            _STDIN + 'const nums = input.split(" ").map(Number);\nnums.sort();\nconsole.log(nums.join(" "));\n',
            _STDIN + 'const nums = input.split(" ").map(Number);\nnums.sort((a, b) => a - b);\nconsole.log(nums.join(" "));\n',
            [("10 9 1", "1 9 10"), ("3 20 100", "3 20 100")], hints=["What does `sort` compare by default?", "Strings. Pass `(a, b) => a - b`."]),
        _dx("tsm-w7-d1", "Past the end of a pair",
            "error TS2493: Tuple type '[string, number]' of length '2' has no element at index '2'.",
            'const pair: [string, number] = ["a", 1];\nconsole.log(pair[2]);\n',
            'const pair: [string, number] = ["a", 1];\nconsole.log(pair[1]);\n',
            [("", "1")], ask="Print the pair's number.", hints=["Tuples are zero-indexed."]),
    ],
    8: [
        _pr("tsm-w8-p1", "What rest collects",
            'const { a, ...rest } = { a: 1, b: "x", c: true };\n', "rest", "{ b: string; c: boolean }",
            hints=["`rest` gets every property that wasn't named.", "Object literal properties widen: `b` is a `string`."]),
        _pr("tsm-w8-p2", "What JSON.parse gives you", 'const parsed = JSON.parse("{}");\n', "parsed", "any",
            hints=["The compiler can't read the string.", "`JSON.parse` returns `any` — which is exactly why you should narrow it."]),
        _dx("tsm-w8-d1", "A user missing a field",
            "error TS2741: Property 'age' is missing in type '{ name: string; }' but required in type 'User'.",
            'type User = { name: string; age: number };\nconst user: User = { name: "Ada" };\nconsole.log(user.name, user.age);\n',
            'type User = { name: string; age: number };\nconst user: User = { name: "Ada", age: 36 };\nconsole.log(user.name, user.age);\n',
            [("", "Ada 36")], ask="Ada is 36.", hints=["Every required property must be present."]),
        _fx("tsm-w8-f1", "A copy that isn't",
            "Copy a record, add a tag to the copy, and print how many tags the original has. It should still be 1.",
            'const original = { tags: ["x"] };\nconst copy = { ...original };\ncopy.tags.push("y");\nconsole.log(original.tags.length);\n',
            'const original = { tags: ["x"] };\nconst copy = { ...original, tags: [...original.tags] };\ncopy.tags.push("y");\nconsole.log(original.tags.length);\n',
            [("", "1")], hints=["How deep does a spread copy?", "One level. Copy the array too."]),
    ],
    9: [
        _pr("tsm-w9-p1", "Reading a Map", 'const m = new Map<string, number>();\nconst v = m.get("a");\n', "v", "number | undefined",
            hints=["The key might not be there."]),
        _pr("tsm-w9-p2", "A set of numbers", "const s = new Set([1, 2, 2]);\n", "s", "Set<number>",
            hints=["Set is generic in its element type."]),
        _fx("tsm-w9-f1", "A counter that doesn't count",
            "Count each word. Every count comes out as 1.",
            _STDIN + 'const counts = new Map<string, number>();\nfor (const w of input.split(" ")) counts.set(w, counts.get(w) ?? 0 + 1);\nconsole.log([...counts].map(([k, v]) => k + "=" + v).join(" "));\n',
            _STDIN + 'const counts = new Map<string, number>();\nfor (const w of input.split(" ")) counts.set(w, (counts.get(w) ?? 0) + 1);\nconsole.log([...counts].map(([k, v]) => k + "=" + v).join(" "));\n',
            [("a b a", "a=2 b=1"), ("x x x", "x=3")], hints=["Operator precedence.", "`+` binds tighter than `??` — add parentheses."]),
        _dx("tsm-w9-d1", "A set of the wrong thing",
            "error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
            _STDIN + 'const seen = new Set<number>();\nfor (const t of input.split(" ")) seen.add(t);\nconsole.log(seen.size);\n',
            _STDIN + 'const seen = new Set<number>();\nfor (const t of input.split(" ")) seen.add(Number(t));\nconsole.log(seen.size);\n',
            [("1 2 2", "2"), ("5", "1")], hints=["The set holds numbers; the input is text.", "Convert with `Number(t)`."]),
    ],
    10: [
        _pr("tsm-w10-p1", "A const string", 'const dir = "up";\n', "dir", '"up"',
            hints=["`const` keeps the literal."]),
        _pr("tsm-w10-p2", "as const on an array", 'const dirs = ["up", "down"] as const;\n', "dirs", 'readonly ["up", "down"]',
            hints=["`as const` makes a read-only tuple of literals."]),
        _pr("tsm-w10-p3", "as const on a let", 'let mode = "dark" as const;\n', "mode", '"dark"',
            hints=["`as const` beats the widening a `let` would do."]),
        _dx("tsm-w10-d1", "A direction that doesn't exist",
            "error TS2345: Argument of type '\"E\"' is not assignable to parameter of type 'Dir'.",
            'type Dir = "N" | "S";\nfunction step(d: Dir): number {\n  return d === "N" ? 1 : -1;\n}\nconsole.log(step("E"));\n',
            'type Dir = "N" | "S";\nfunction step(d: Dir): number {\n  return d === "N" ? 1 : -1;\n}\nconsole.log(step("S"));\n',
            [("", "-1")], ask="The step meant here is south.", hints=["Only the members of `Dir` are allowed."]),
    ],
    11: [
        _pr("tsm-w11-p1", "A default after find",
            "const firstBig = [1, 2].find((n) => n > 5) ?? 0;\n", "firstBig", "number",
            hints=["`??` removes the `undefined` case."]),
        _dx("tsm-w11-d1", "An optional parameter",
            "error TS18048: 's' is possibly 'undefined'.",
            'function shout(s?: string): string {\n  return s.toUpperCase();\n}\nconsole.log(shout("hi"));\n',
            'function shout(s?: string): string {\n  return (s ?? "").toUpperCase();\n}\nconsole.log(shout("hi"));\n',
            [("", "HI")], hints=["An optional parameter is `string | undefined` inside.", 'Give it a default: `(s ?? "")`.']),
        _dx("tsm-w11-d2", "A property only one member has",
            "error TS2339: Property 'r' does not exist on type 'Circle | Square'.",
            'type Circle = { kind: "c"; r: number };\ntype Square = { kind: "s"; side: number };\nfunction area(s: Circle | Square): number {\n  return s.r * s.r * 3;\n}\nconsole.log(area({ kind: "s", side: 2 }), area({ kind: "c", r: 1 }));\n',
            'type Circle = { kind: "c"; r: number };\ntype Square = { kind: "s"; side: number };\nfunction area(s: Circle | Square): number {\n  return s.kind === "c" ? s.r * s.r * 3 : s.side * s.side;\n}\nconsole.log(area({ kind: "s", side: 2 }), area({ kind: "c", r: 1 }));\n',
            [("", "4 3")], ask="Handle both shapes (use 3 for pi).", hints=["Narrow on `kind` first."], difficulty="Medium"),
    ],
    12: [
        _pr("tsm-w12-p1", "Either member's payload",
            'type R = { ok: true; value: number } | { ok: false; error: string };\nfunction get(): R {\n  return { ok: true, value: 1 };\n}\nconst r = get();\nconst payload = r.ok ? r.value : r.error;\n',
            "payload", "string | number", hints=["Each branch is narrowed to one member."]),
        _dx("tsm-w12-d1", "A case that was forgotten",
            "error TS2366: Function lacks ending return statement and return type does not include 'undefined'.",
            'type Shape = { kind: "sq"; side: number } | { kind: "rect"; w: number; h: number };\nfunction area(s: Shape): number {\n  switch (s.kind) {\n    case "sq":\n      return s.side * s.side;\n  }\n}\nconsole.log(area({ kind: "rect", w: 2, h: 3 }), area({ kind: "sq", side: 2 }));\n',
            'type Shape = { kind: "sq"; side: number } | { kind: "rect"; w: number; h: number };\nfunction area(s: Shape): number {\n  switch (s.kind) {\n    case "sq":\n      return s.side * s.side;\n    case "rect":\n      return s.w * s.h;\n  }\n}\nconsole.log(area({ kind: "rect", w: 2, h: 3 }), area({ kind: "sq", side: 2 }));\n',
            [("", "6 4")], hints=["Which member has no `case`?", "Once every member is handled, the end is unreachable."], difficulty="Medium"),
        _fx("tsm-w12-f1", "A default that swallowed a command",
            "Apply commands (`inc`, `dec`, `reset`) to a counter starting at 0 and print the result. `reset` is silently ignored.",
            _STDIN + 'type Cmd = "inc" | "dec" | "reset";\nfunction apply(n: number, c: Cmd): number {\n  switch (c) {\n    case "inc":\n      return n + 1;\n    case "dec":\n      return n - 1;\n    default:\n      return n;\n  }\n}\nlet n = 0;\nfor (const c of input.split(" ")) n = apply(n, c as Cmd);\nconsole.log(n);\n',
            _STDIN + 'type Cmd = "inc" | "dec" | "reset";\nfunction apply(n: number, c: Cmd): number {\n  switch (c) {\n    case "inc":\n      return n + 1;\n    case "dec":\n      return n - 1;\n    case "reset":\n      return 0;\n  }\n}\nlet n = 0;\nfor (const c of input.split(" ")) n = apply(n, c as Cmd);\nconsole.log(n);\n',
            [("inc inc reset dec", "-1"), ("inc", "1"), ("reset", "0")],
            hints=["The `default` branch hides the missing case.", "Handle `reset` — and drop the `default`, so the compiler tells you next time."], difficulty="Medium"),
    ],
    13: [
        _fx("tsm-w13-f1", "One line too many",
            "Print how many lines the input has. It counts one extra.",
            'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8");\nconsole.log(input.split("\\n").length);\n',
            'import * as fs from "fs";\nconst input = fs.readFileSync(0, "utf8");\nconsole.log(input.trimEnd().split("\\n").length);\n',
            [("a\nb\n", "2"), ("x\n", "1"), ("1\n2\n3\n", "3")], hints=["What follows the last newline?", "An empty string. Trim the end first."]),
        _fx("tsm-w13-f2", "The largest of nothing",
            "Print the largest number on the line, or 0 for an empty line.",
            _STDIN + 'const nums = input === "" ? [] : input.split(" ").map(Number);\nconsole.log(Math.max(...nums));\n',
            _STDIN + 'const nums = input === "" ? [] : input.split(" ").map(Number);\nconsole.log(nums.length > 0 ? Math.max(...nums) : 0);\n',
            [("3 9 2", "9"), ("", "0"), ("-5", "-5")], hints=["What is `Math.max()` with no arguments?", "`-Infinity`. Handle the empty case."]),
        _pr("tsm-w13-p1", "Entries of an object", "const pairs = Object.entries({ a: 1, b: 2 });\n", "pairs", "[string, number][]",
            hints=["Keys are strings; each entry is a pair."]),
    ],
    14: [
        _pr("tsm-w14-p1", "An index read, honestly", "const xs: number[] = [1];\nconst first = xs[0];\n", "first", "number | undefined",
            strictness="strict+indexed", why="This exercise is checked with `noUncheckedIndexedAccess` on.",
            hints=["The array might be empty.", "Under this flag every index read adds `undefined`."]),
        _dx("tsm-w14-d1", "The first element",
            "error TS2532: Object is possibly 'undefined'.",
            "const xs = [3, 1, 2];\nconsole.log(xs[0].toFixed(1));\n",
            "const xs = [3, 1, 2];\nconsole.log((xs[0] ?? 0).toFixed(1));\n",
            [("", "3.0")], strictness="strict+indexed", hints=["`xs[0]` is `number | undefined` here.", "Give it a default with `??`."]),
        _dx("tsm-w14-d2", "A Map lookup",
            "error TS18048: 'v' is possibly 'undefined'.",
            'const m = new Map([["a", 1]]);\nconst v = m.get("a");\nconsole.log(v + 1);\n',
            'const m = new Map([["a", 1]]);\nconst v = m.get("a");\nconsole.log((v ?? 0) + 1);\n',
            [("", "2")], hints=["`get` returns `V | undefined`."]),
        _dx("tsm-w14-d3", "An optional address",
            "error TS18048: 'user.address' is possibly 'undefined'.",
            _STDIN + 'const user = JSON.parse(input) as { address?: { city: string } };\nconsole.log(user.address.city);\n',
            _STDIN + 'const user = JSON.parse(input) as { address?: { city: string } };\nconsole.log(user.address?.city ?? "unknown");\n',
            [('{"address":{"city":"Oslo"}}', "Oslo"), ("{}", "unknown")],
            ask='Print the city, or "unknown" when there is no address.', hints=["`?.` stops at a missing link.", "Then `??` supplies the fallback."]),
    ],
    15: [
        _pr("tsm-w15-p1", "satisfies keeps the literal",
            'const cfg = { mode: "dark" } satisfies { mode: "dark" | "light" };\n', "cfg.mode", '"dark"',
            hints=["`satisfies` checks without widening to the target type."]),
        _pr("tsm-w15-p2", "as const on an object", "const p = { x: 1, y: 2 } as const;\n", "p.x", "1",
            hints=["`as const` keeps every property's literal type."]),
        _dx("tsm-w15-d1", "A cast that isn't a conversion",
            "error TS2352: Conversion of type 'string' to type 'number' may be a mistake because neither type sufficiently overlaps with the other. If this was intentional, convert the expression to 'unknown' first.",
            'const n = "5" as number;\nconsole.log(n * 2);\n',
            'const n = Number("5");\nconsole.log(n * 2);\n',
            [("", "10")], hints=["`as` never converts a value.", "Call `Number(...)`."]),
        _fx("tsm-w15-f1", "An assertion that lied",
            "Print how many items the JSON has — 0 when there is no `items` array. It crashes instead.",
            _STDIN + "const data = JSON.parse(input) as { items: number[] };\nconsole.log(data.items.length);\n",
            _STDIN + "const data: unknown = JSON.parse(input);\nconst items = typeof data === \"object\" && data !== null && \"items\" in data && Array.isArray(data.items) ? data.items : [];\nconsole.log(items.length);\n",
            [('{"items":[1,2]}', "2"), ("{}", "0")], hints=["`as` told the compiler something the input doesn't guarantee.", "Parse into `unknown` and check before reading."], difficulty="Medium"),
    ],
    16: [
        _pr("tsm-w16-p1", "A frozen array", "const frozen = Object.freeze([1, 2]);\n", "frozen", "readonly number[]",
            hints=["`Object.freeze` changes the static type too."]),
        _dx("tsm-w16-d1", "Writing to readonly",
            "error TS2540: Cannot assign to 'x' because it is a read-only property.",
            "type P = { readonly x: number };\nconst p: P = { x: 1 };\np.x = 2;\nconsole.log(p.x);\n",
            "type P = { readonly x: number };\nconst p: P = { x: 1 };\nconst moved: P = { ...p, x: 2 };\nconsole.log(moved.x);\n",
            [("", "2")], ask="Make a new point instead of changing this one.", hints=["Build a new object with the new value."]),
        _dx("tsm-w16-d2", "A plain number isn't Cents",
            "error TS2345: Argument of type 'number' is not assignable to parameter of type 'Cents'.",
            'type Cents = number & { readonly __brand: "Cents" };\nfunction cents(n: number): Cents {\n  return n as Cents;\n}\nfunction show(c: Cents): string {\n  return (c / 100).toFixed(2);\n}\nconsole.log(show(250));\n',
            'type Cents = number & { readonly __brand: "Cents" };\nfunction cents(n: number): Cents {\n  return n as Cents;\n}\nfunction show(c: Cents): string {\n  return (c / 100).toFixed(2);\n}\nconsole.log(show(cents(250)));\n',
            [("", "2.50")], ask="Use the constructor that brands the value.", hints=["`cents(...)` is the one place the brand is applied."]),
        _fx("tsm-w16-f1", "A helper that changes its input",
            "`addTag` should return a new list, leaving the original alone. Print both lengths: the original should still have 1.",
            'function addTag(tags: string[], t: string): string[] {\n  tags.push(t);\n  return tags;\n}\nconst base = ["a"];\nconst next = addTag(base, "b");\nconsole.log(base.length, next.length);\n',
            'function addTag(tags: string[], t: string): string[] {\n  return [...tags, t];\n}\nconst base = ["a"];\nconst next = addTag(base, "b");\nconsole.log(base.length, next.length);\n',
            [("", "1 2")], hints=["`push` changes the caller's array.", "Return a new array with spread."]),
    ],
}

_seen_ids = set()
for _tsw in TS_WEEKS:
    _items = TS_PRACTICE_READING.get(_tsw["week"], []) + TS_PRACTICE.get(_tsw["week"], [])
    for _ex in _items:
        assert _ex["id"] not in _seen_ids, f"duplicate practice id {_ex['id']}"
        _seen_ids.add(_ex["id"])
    _tsw["practice"] = _items
