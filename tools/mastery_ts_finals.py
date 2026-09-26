# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — finals, round two (TS_MASTERY_ROADMAP A4):
#
#   TS_EXAM_TYPES       X-34: the type-graded half of the two-part finals for
#                       weeks 15-22. The week's final passes only when both the
#                       runtime half (stdout tests) and this half (hidden
#                       `Expect<Equal<…>>` claims) are green.
#   TS_EXAM_REPLACE     finals rewritten on the roadmap's say-so — week 17's
#                       "Merge intervals" becomes "Typed patch API".
#   TS_VISIBLE_TESTS    X-32: how many of a final's tests are shown when they
#                       fail. The rest are a hidden set: a failing hidden test
#                       says only that it failed, never its input.
#
# exec()'d by gen_seed.py after the month files and before
# mastery_ts_attach.py, which applies all of it.
# ---------------------------------------------------------------------------


def _exam_types(week, title, prompt, full, blank, checks, hints=()):
    ex = _tl(f"tsm-final-w{week}-types", title, prompt, full, blank, checks, hints=hints)
    ex["strictness"] = _week_strictness(week) or "strict"
    return ex


# Checks may compare an intersection with a flat object; Equal<> treats the two
# as different types, so they are flattened first.
_SIMPLIFY = "type Simplify<T> = { [K in keyof T]: T[K] } & {};\n"

TS_EXAM_TYPES = {
    15: _exam_types(15, "Part 1 — a route table that keeps its literals",
        "Check `routes` against `Record<string, Route>` without losing what the object literal says: "
        "the route names must stay a union of the three keys, and each route's `method` its literal. "
        "Replace the `____` — do not annotate the variable, and do not use `as const` "
        "(the checks look at `path`, which must stay `string`).",
        '''
type Method = "GET" | "POST" | "DELETE";
type Route = { path: string; method: Method };

const routes = {
  home: { path: "/", method: "GET" },
  login: { path: "/login", method: "POST" },
  logout: { path: "/logout", method: "DELETE" },
} satisfies Record<string, Route>;

type RouteName = keyof typeof routes;
''', "satisfies Record<string, Route>",
        '''
type _1 = Expect<Equal<RouteName, "home" | "login" | "logout">>;
type _2 = Expect<Equal<(typeof routes)["login"], { path: string; method: "POST" }>>;
type _3 = Expect<Equal<(typeof routes)["home"]["method"], "GET">>;
''', hints=["An annotation (`: Record<string, Route>`) checks the value but forgets its keys.",
            "The operator that checks without widening goes after the literal: `} satisfies …;`."]),

    16: _exam_types(16, "Part 1 — a reusable brand",
        "Write `Brand<T, B>`: a `T` that carries the tag `B` in a property keyed by the `unique symbol` "
        "`brand`, so that a plain `number` is not a `UserId`, a `UserId` is not an `OrderId`, and both are "
        "still usable as numbers.",
        '''
declare const brand: unique symbol;
type Brand<T, B extends string> = T & { readonly [brand]: B };

type UserId = Brand<number, "UserId">;
type OrderId = Brand<number, "OrderId">;
''', "T & { readonly [brand]: B }",
        '''
declare const u: UserId;
declare const o: OrderId;
const asNumber: number = u;
type _1 = Expect<Equal<[UserId] extends [never] ? true : false, false>>;
type _2 = Expect<Equal<UserId extends number ? true : false, true>>;
// @ts-expect-error — a plain number is not a UserId
const fromNumber: UserId = 42;
// @ts-expect-error — an OrderId is not a UserId
const mixedUp: UserId = o;
''', hints=["A brand is an intersection: the base type `&` an object type nobody else can produce.",
            "`T & { readonly [brand]: B }` — the computed key uses the `unique symbol` declared above."]),

    17: _exam_types(17, "Part 1 — make some keys required",
        "Write `WithRequired<T, K>`: `T` with the keys in `K` made required (and no longer `undefined`), "
        "every other property exactly as it was. `K` must be a key of `T`. Compose it from utility types.",
        '''
type WithRequired<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;
''', "Omit<T, K> & Required<Pick<T, K>>",
        _SIMPLIFY + '''
type Task = { id: number; title?: string; done?: boolean; tags?: string[] };
type _1 = Expect<Equal<Simplify<WithRequired<Task, "title">>, { id: number; title: string; done?: boolean; tags?: string[] }>>;
type _2 = Expect<Equal<Simplify<WithRequired<Task, "done" | "tags">>, { id: number; title?: string; done: boolean; tags: string[] }>>;
type _3 = Expect<Equal<Simplify<WithRequired<Task, "id">>, Task>>;
// @ts-expect-error — K must be a key of T
type _4 = WithRequired<Task, "owner">;
''', hints=["Split `T` in two: the keys you are changing, and the rest.",
            "`Omit<T, K>` keeps the rest untouched; `Required<Pick<T, K>>` makes the chosen ones required. Intersect them."]),

    18: _exam_types(18, "Part 1 — type the signature of groupBy",
        "Write the type parameters and signature of `groupBy`: it takes a readonly array of `T` and a "
        "function from `T` to a key `K` (any property key), and returns `Partial<Record<K, T[]>>` — partial "
        "because a key may have no items. The key type must be inferred from the key function.",
        '''
declare function groupBy<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>>;
''', "<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>>",
        '''
type User = { name: string; role: "admin" | "member" };
declare const users: User[];
const byRole = groupBy(users, (u) => u.role);
type _1 = Expect<Equal<typeof byRole, Partial<Record<"admin" | "member", User[]>>>>;
const byLength = groupBy(["a", "bb", "cc"], (s) => s.length);
type _2 = Expect<Equal<typeof byLength, Partial<Record<number, string[]>>>>;
// @ts-expect-error — a key must be a string, number or symbol
groupBy(users, (u) => ({ name: u.name }));
''', hints=["Two type parameters: the item type, and the key type — constrained so it can index a record.",
            "`K extends PropertyKey`, and the key function has type `(item: T) => K` so `K` is inferred from what it returns."]),

    19: _exam_types(19, "Part 1 — a two-level lookup type",
        "Write `Get<T, A, B>`: the type of `obj[a][b]` for `obj: T`. `A` must be a key of `T`, and `B` a key "
        "of `T[A]` — so a key from the wrong section is rejected.",
        '''
type Get<T, A extends keyof T, B extends keyof T[A]> = T[A][B];
''', "<T, A extends keyof T, B extends keyof T[A]> = T[A][B]",
        '''
const config = { server: { port: 8080, host: "localhost" }, flags: { beta: true } };
type Config = typeof config;
type _1 = Expect<Equal<Get<Config, "server", "port">, number>>;
type _2 = Expect<Equal<Get<Config, "flags", "beta">, boolean>>;
type _3 = Expect<Equal<Get<Config, "server", "port" | "host">, number | string>>;
// @ts-expect-error — "beta" is not a key of the server section
type _4 = Get<Config, "server", "beta">;
''', hints=["Each type parameter is constrained by the one before it.",
            "`A extends keyof T`, `B extends keyof T[A]`, and the result is the indexed access `T[A][B]`."]),

    20: _exam_types(20, "Part 1 — a validator for every field",
        "Write `Validators<T>`: for every property of `T` — optional ones included — a type guard "
        "`(value: unknown) => value is …` for that property's type. An optional property's guard accepts "
        "`undefined` too, and every validator is required.",
        '''
type Validators<T> = { [K in keyof T]-?: (value: unknown) => value is T[K] };
''', "{ [K in keyof T]-?: (value: unknown) => value is T[K] }",
        '''
type _1 = Expect<Equal<Validators<{ name: string; age: number }>, {
  name: (value: unknown) => value is string;
  age: (value: unknown) => value is number;
}>>;
type _2 = Expect<Equal<Validators<{ nick?: string }>, { nick: (value: unknown) => value is string | undefined }>>;
type _3 = Expect<Equal<Validators<{ readonly id: number }>, { readonly id: (value: unknown) => value is number }>>;
''', hints=["A homomorphic mapped type over `keyof T` keeps `readonly` — and `?`, unless you remove it.",
            "`-?` removes the optionality; `T[K]` of an optional property already includes `undefined`."]),

    21: _exam_types(21, "Part 1 — resolve a function or a promise",
        "Write `Resolved<T>`: if `T` is a function, its return type; otherwise if it is a `Promise`, the "
        "value it resolves to (one level); otherwise `T` itself. It must distribute over unions.",
        '''
type Resolved<T> = T extends (...args: never[]) => infer R ? R : T extends Promise<infer V> ? V : T;
''', "T extends (...args: never[]) => infer R ? R : T extends Promise<infer V> ? V : T",
        '''
type _1 = Expect<Equal<Resolved<() => number>, number>>;
type _2 = Expect<Equal<Resolved<(a: string, b: boolean) => string[]>, string[]>>;
type _3 = Expect<Equal<Resolved<Promise<string>>, string>>;
type _4 = Expect<Equal<Resolved<boolean>, boolean>>;
type _5 = Expect<Equal<Resolved<Date | (() => 1)>, Date | 1>>;
''', hints=["Two conditional types, the second in the false branch of the first.",
            "`T extends (...args: never[]) => infer R ? R : T extends Promise<infer V> ? V : T` — a naked `T` distributes."]),

    22: _exam_types(22, "Part 1 — join a tuple of strings",
        "Write `Join<T, S>`: the string literal made by joining the tuple of string literals `T` with the "
        "separator `S`. An empty tuple joins to `\"\"`.",
        '''
type Join<T extends string[], S extends string> =
  T extends [infer H extends string, ...infer R extends string[]]
    ? R extends [] ? H : `${H}${S}${Join<R, S>}`
    : "";
''', '''T extends [infer H extends string, ...infer R extends string[]]
    ? R extends [] ? H : `${H}${S}${Join<R, S>}`
    : ""''',
        '''
type _1 = Expect<Equal<Join<["a", "b", "c"], "-">, "a-b-c">>;
type _2 = Expect<Equal<Join<["user", "created"], ":">, "user:created">>;
type _3 = Expect<Equal<Join<["solo"], ", ">, "solo">>;
type _4 = Expect<Equal<Join<[], "/">, "">>;
''', hints=["Take the tuple apart with `[infer H, ...infer R]` and recurse on the rest.",
            "One element left means no separator after it; an empty tuple gives `\"\"`."]),
}


# ---------------------------------------------------------------------------
# Week 17's final: the roadmap replaces "Merge intervals" (an algorithm, not
# this week's subject) with a typed patch API. The runtime half here pairs
# with TS_EXAM_TYPES[17].
# ---------------------------------------------------------------------------
_W17_PATCH_BODY = r'''
type Task = { id: number; title: string; done: boolean; tags: readonly string[] };
type Patch = Partial<Omit<Task, "id">>;
type Result<T> = { ok: true; value: T } | { ok: false; error: string };

const lines = input.split("\n");
const n = Number(lines[0]);
const tasks = new Map<number, Task>();
for (let i = 1; i <= n; i++) {
  const [id = "", title = "", done = "", tags = ""] = (lines[i] ?? "").split("|");
  tasks.set(Number(id), { id: Number(id), title, done: done === "true", tags: tags ? tags.split(",") : [] });
}

function parsePatch(fields: readonly string[]): Result<Patch> {
  const patch: Patch = {};
  for (const field of fields) {
    const eq = field.indexOf("=");
    const key = eq < 0 ? field : field.slice(0, eq);
    const value = eq < 0 ? "" : field.slice(eq + 1);
    switch (key) {
      case "title":
        if (value.trim() === "") return { ok: false, error: "title cannot be empty" };
        patch.title = value.trim();
        break;
      case "done":
        if (value !== "true" && value !== "false") return { ok: false, error: "done must be true or false" };
        patch.done = value === "true";
        break;
      case "tags":
        patch.tags = value ? value.split(",") : [];
        break;
      case "id":
        return { ok: false, error: "id cannot change" };
      default:
        return { ok: false, error: `unknown field ${key}` };
    }
  }
  return { ok: true, value: patch };
}

function apply(task: Task, patch: Patch): Task {
  return { ...task, ...patch };
}

const m = Number(lines[n + 1] ?? "0");
for (let j = 0; j < m; j++) {
  const [idText = "", ...fields] = (lines[n + 2 + j] ?? "").split(";");
  const task = tasks.get(Number(idText));
  if (task === undefined) {
    console.log(`#${idText}: no such task`);
    continue;
  }
  const parsed = parsePatch(fields);
  if (!parsed.ok) {
    console.log(`#${task.id}: rejected, ${parsed.error}`);
    continue;
  }
  tasks.set(task.id, apply(task, parsed.value));
  console.log(`#${task.id}: updated ${Object.keys(parsed.value).join(",") || "nothing"}`);
}
for (const t of [...tasks.values()].sort((a, b) => a.id - b.id)) {
  console.log(`${t.id} | ${t.title} | ${t.done ? "done" : "open"} | ${t.tags.join(",") || "-"}`);
}
'''

_W17_TASKS = "3\n1|Write report|false|work,urgent\n2|Buy milk|false|home\n3|Call bank|true|"

TS_EXAM_REPLACE = {
    17: _ts_exam_io(
        "tsm-final-w17-patch", "Typed patch API",
        "Tasks are `id|title|done|tags` lines (`done` is `true`/`false`, tags comma-separated, possibly "
        "empty) after a count `n`; then a count `m` and `m` patches `id;key=value;key=value…`. A patch may set "
        "`title` (non-empty, trimmed), `done` (`true`/`false` only) and `tags` (comma-separated; empty clears "
        "them). It may never touch `id`, and an unknown key rejects it. A patch applies completely or not at "
        "all. Print `#<id>: updated <keys>` (the keys comma-joined in the order given, `nothing` for none), "
        "`#<id>: rejected, <reason>` (`id cannot change`, `unknown field <key>`, `title cannot be empty`, "
        "`done must be true or false`), or `#<id>: no such task`. Then every task by id as "
        "`id | title | done-or-open | tags-or--`. Type the patch as a utility type of `Task`, and parse it "
        "into a `Result`.",
        _W17_PATCH_BODY,
        [
            _W17_TASKS + "\n4\n1;done=true;title=Write the report\n2;id=5\n4;done=true\n3;tags=money,phone",
            _W17_TASKS + "\n2\n1;done=yes\n2;title=  Buy oat milk  ",
            _W17_TASKS + "\n2\n1;priority=high\n1;tags=",
            _W17_TASKS + "\n1\n2;title=   ",
            _W17_TASKS + "\n0",
            _W17_TASKS + "\n2\n2\n3;done=false;done=true",
            "2\n9|Plan trip|false|travel\n4|Pay rent|false|home,money\n3\n4;done=true\n4;title=Pay March rent;tags=money\n9;title=Plan the trip;id=9",
            "1\n1|Solo|false|\n3\n1;tags=a,b,c\n1;title=Solo task;done=true\n7;title=Ghost",
            _W17_TASKS + "\n1\n1;title=Report;done=true;id=2",
        ],
        hint="`Partial<Omit<Task, \"id\">>` is the patch. Build it field by field into a `Result`, and only "
             "apply it once every field has parsed.",
    ),
}

# X-32: the tests beyond these are a hidden set. Roughly the first half of every
# TypeScript final is shown when it fails; the rest never shows its input.
TS_VISIBLE_TESTS = 4
