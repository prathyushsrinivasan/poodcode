# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — Month 5: Generics & type-level (weeks 18-22).
#
# The month's week tables, coding finals, authored bank questions and the
# extra final tests. exec()'d in order by mastery_defs.py, which defines
# `_w`, `_ts_exam` and the four collections this file extends.
# ---------------------------------------------------------------------------

TS_WEEKS.extend([
    # =======================================================================
    # MONTH 5 — Generics & type-level
    # =======================================================================
    _w(18, "Month 5 · Generics & type-level",
        "Generics & Constraints",
        "Write one implementation that keeps every caller's exact type.",
        ["ts_generics", "ts_generic_constraints"],
        [("two-sum-fn", "A function whose signature is the interesting part."),
         ("reverse-array-fn", "Generic in the element type."),
         ("kth-largest-element", "A comparator-driven selection.")],
        "Write a `collections.ts` exporting generic `unique`, `groupBy`, `partition` and `sortBy` helpers, each preserving the input's element type.",
        [("Why is `<T extends { length: number }>` better than a plain `{ length: number }` parameter?",
          ["The generic returns the caller's exact type instead of collapsing it",
           "It is faster",
           "The non-generic form does not compile",
           "Only the generic accepts arrays"], 0,
          "Both accept the same arguments. The difference is on the way out — the generic hands back `string` for strings."),
         ("In `get<T, K extends keyof T>(obj: T, key: K): T[K]`, what is `T[K]`?",
          ["An indexed access type — the type of the property named K",
           "An array of T indexed by K",
           "A mapped type",
           "The same as keyof T"], 0,
          "It looks up a property type by name, which is how one signature returns `string` for one key and `number` for another."),
         ("What does a type-parameter default like `<T = string>` do?",
          ["Supplies T only when inference has nothing to work from",
           "Makes the parameter optional",
           "Coerces the argument to string",
           "Constrains T to string"], 0,
          "It is not a value default. `makeBox(1)` still infers `number`; the default matters when no argument drives inference."),
         ("When is a generic the WRONG tool?",
          ["When the body never uses T — a plain parameter type is clearer",
           "When there is more than one type parameter",
           "When T is constrained",
           "When the function is exported"], 0,
          "A type parameter used once and never related to anything else adds noise without adding a guarantee.")]),

    _w(19, "Month 5 · Generics & type-level",
        "keyof, typeof & Indexed Access",
        "Derive types from values so one source of truth drives both.",
        ["ts_keyof_indexed"],
        [("time-based-kv", "A keyed store with a typed accessor."),
         ("prefix-counts", "Deriving structure from data.")],
        "Write a `settings.ts` where one `as const` object defines the defaults, and every getter, setter and key union is derived from it — adding a setting should require exactly one edit.",
        [("What is `(typeof levels)[number]` when `const levels = [\"a\", \"b\"] as const`?",
          ["\"a\" | \"b\"", "string", "readonly [\"a\", \"b\"]", "number"], 0,
          "`as const` keeps the elements literal, and indexing the tuple type by `number` unions them — the standard derive-a-union idiom."),
         ("Drop the `as const`. What does it become?",
          ["string", "\"a\" | \"b\"", "never", "string[]"], 0,
          "The array widens to `string[]`, so the literal information is gone before the type-level trick can use it."),
         ("How does type-position `typeof` differ from the runtime operator?",
          ["It lifts a value into a type; the runtime one returns a string when executed",
           "They are the same operator",
           "The type one works on classes only",
           "The runtime one is erased"], 0,
          "They share a keyword and nothing else. One computes a type, the other is a runtime check that happens to narrow."),
         ("What is `keyof Record<string, number>`?",
          ["string | number", "string", "number", "never"], 0,
          "`keyof` on an index signature gives the index type, and numeric keys are also valid string keys — which is why it includes `number`.")]),

    _w(20, "Month 5 · Generics & type-level",
        "Mapped Types",
        "Transform every property of a type at once — and build what the type describes.",
        ["ts_mapped_types"],
        [("design-hashset", "A container described by a derived type."),
         ("top-k-frequent", "Projection over a frequency table.")],
        "Reimplement `Partial`, `Required`, `Readonly`, `Pick` and `Omit` from scratch in a `utils.d.ts`, then check each against the built-in with a type-level test.",
        [("What does `{ [K in keyof T]-?: T[K] }` produce?",
          ["Every property made required — the built-in Required<T>",
           "Every property made optional",
           "T with all properties removed",
           "A union of T's property types"], 0,
          "The `-` prefix strips a modifier the source had. `-readonly` does the same for readonly."),
         ("In an `as` clause, what happens to a key mapped to `never`?",
          ["The property is removed — this is how Omit works",
           "Its type becomes never",
           "It is a compile error",
           "It is renamed to \"never\""], 0,
          "Key remapping to `never` drops the entry, which is the mechanism behind every filtering utility type."),
         ("You define `Getters<T>` renaming keys to getName/getAge. What exists at runtime?",
          ["Nothing — the type only describes an object you still have to build",
           "An object with those methods",
           "A proxy",
           "The original object with extra prototype methods"], 0,
          "Mapped types are erased like everything else in the type system. They describe an obligation your runtime code has to meet."),
         ("What is `keyof (A | B)`?",
          ["The keys A and B have in COMMON",
           "All keys of both",
           "never",
           "The keys of A only"], 0,
          "Only shared keys are safe to access on a value that might be either — a frequent surprise when mapping over a union.")]),

    _w(21, "Month 5 · Generics & type-level",
        "Conditional Types & infer",
        "Branch on types and pattern-match their structure.",
        ["ts_conditional_types"],
        [("nested-list-depth-sum", "Nested data is the runtime shape a recursive `Unwrap<T>` describes — peel one layer per level."),
         ("decode-string", "`k[...]` nests arbitrarily deep: unwrap the inner layer before the outer one, as `infer` does.")],
        "Write a `types.ts` implementing `ReturnType`, `Parameters`, `Awaited` and `Exclude` yourself, with a comment on each explaining where `infer` binds.",
        [("What does `infer` do?",
          ["Binds a fresh type variable to whatever matched at that position",
           "Forces re-inference of the expression",
           "Declares a default for the type parameter",
           "Converts a value into a type"], 0,
          "`T extends (infer U)[] ? U : T` matches T against 'array of something' and names that something `U`."),
         ("`type NonNil<T> = T extends null | undefined ? never : T`. What is `NonNil<string | null>`?",
          ["string", "string | null", "never", "string | never"], 0,
          "T is naked, so the conditional distributes: `string` takes the else branch, `null` becomes `never`, and `never` vanishes from a union."),
         ("How do you STOP a conditional type distributing?",
          ["Wrap both sides in a tuple: [T] extends [U] ? X : Y",
           "Add a nodistribute modifier",
           "Constrain T with extends object",
           "Use an interface"], 0,
          "Distribution needs a bare type parameter. Putting it in a tuple makes it non-naked, so the check runs once on the whole union."),
         ("What is `IsString<any>` for `type IsString<T> = T extends string ? \"yes\" : \"no\"`?",
          ["\"yes\" | \"no\" — any takes both branches",
           "\"yes\"", "\"no\"", "any"], 0,
          "`any` is assignable to everything and nothing simultaneously, so a conditional over it resolves to the union of both branches.")]),

    _w(22, "Month 5 · Generics & type-level",
        "Template Literals & Recursive Types",
        "Encode naming conventions in the type system, and describe unbounded data.",
        ["ts_template_literal_types", "ts_type_level"],
        [("replace-words-roots", "Prefix matching over a dictionary."),
         ("implement-trie-ops", "A recursive structure with a recursive type.")],
        "Write an `events.ts` where the entity and action lists are `as const` arrays, the event-name type is a template literal over them, and a typed emitter rejects any name not in the catalogue.",
        [("How many members does `` `${\"a\" | \"b\"}-${\"x\" | \"y\" | \"z\"}` `` have?",
          ["6", "5", "2", "3"], 0,
          "Interpolating unions gives the cross product — 2 × 3. This growth is also why deeply nested templates can exhaust the compiler."),
         ("Where can `Capitalize<T>` be used?",
          ["Only inside template literal types — it is a compiler intrinsic",
           "Anywhere, including at runtime",
           "Only in key remapping",
           "Only on unions"], 0,
          "`Capitalize`, `Uppercase`, `Lowercase` and `Uncapitalize` live purely in the type system. Capitalizing a real string is still your own code."),
         ("Why is `type Bad = Bad | string` an error while `type Json = string | Json[]` is fine?",
          ["A recursive alias must go through an object, array or function",
           "Unions cannot be recursive",
           "Bad has no base case",
           "type aliases cannot be recursive at all"], 0,
          "`Bad` refers to itself with nothing to defer into. Wrapping the recursion in `Json[]` gives the checker a structure to expand lazily."),
         ("What does `T extends readonly [unknown, ...infer Rest]` accomplish?",
          ["Peels the first tuple element and binds the rest, enabling recursion",
           "Checks T is a readonly array",
           "Reverses the tuple",
           "Makes the tuple mutable"], 0,
          "It is the type-level head/tail destructure — the shrinking step every recursive tuple algorithm needs.")]),
])


TS_EXAMS.update({
    18: _ts_exam(
        "Generic collection helpers",
        "Write generic `unique`, `groupBy` and `sortBy`. The input is `n` then `n` lines of `category value`. Print each category in alphabetical order as `category: v1 v2` with its values sorted numerically ascending and duplicates removed, then the number of categories.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
type Row = { category: string; value: number };
function unique<T>(items: T[]): T[] {
  return [...new Set(items)];
}
function groupBy<T, K extends keyof T>(items: T[], key: K): Map<T[K], T[]> {
  const out = new Map<T[K], T[]>();
  for (const item of items) {
    const bucket = out.get(item[key]);
    if (bucket === undefined) out.set(item[key], [item]);
    else bucket.push(item);
  }
  return out;
}
function sortBy<T>(items: T[], score: (item: T) => number): T[] {
  return [...items].sort((a, b) => score(a) - score(b));
}
const rows: Row[] = [];
for (let i = 1; i <= n; i++) {
  const [category = "", value = "0"] = (lines[i] ?? "").trim().split(/\\s+/);
  rows.push({ category, value: Number(value) });
}
const groups = groupBy(rows, "category");
for (const category of [...groups.keys()].sort()) {
  const values = unique(sortBy(groups.get(category)!, (r) => r.value).map((r) => r.value));
  console.log(category + ": " + values.join(" "));
}
console.log(groups.size);
''',
        [("4\nb 2\na 3\nb 1\na 3", "a: 3\nb: 1 2\n2"),
         ("1\nx 9", "x: 9\n1"),
         ("3\nz 1\nz 2\nz 1", "z: 1 2\n1")],
        hint="`K extends keyof T` is what keeps the Map keyed by the field's real type instead of collapsing to string."),

    19: _ts_exam(
        "Settings from one source of truth",
        "Declare a defaults object, derive `Setting` with `keyof typeof`, and write a `read<K extends Setting>` returning `Profile[K]`. Defaults are `theme: \"dark\"`, `size: 14`, `wrap: true`. The input is `n` then `n` setting names. Print each value, or `unknown`, then the boolean-valued keys in alphabetical order.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const defaults = { theme: "dark", size: 14, wrap: true };
type Profile = typeof defaults;
type Setting = keyof Profile;
function read<K extends Setting>(key: K): Profile[K] {
  return defaults[key];
}
for (let i = 1; i <= n; i++) {
  const name = (lines[i] ?? "").trim();
  console.log(Object.hasOwn(defaults, name) ? String(read(name as Setting)) : "unknown");
}
const booleans = (Object.keys(defaults) as Setting[])
  .filter((k) => typeof defaults[k] === "boolean")
  .sort();
console.log(booleans.join(" "));
''',
        [("3\ntheme\nsize\nnope", "dark\n14\nunknown\nwrap"),
         ("1\nwrap", "true\nwrap"),
         ("2\nsize\ntheme", "14\ndark\nwrap")],
        hint="One object drives the values, the key union and the getter's return type — adding a setting should need exactly one edit. Check a runtime name with `Object.hasOwn`, not `in`, or inherited keys like `toString` slip through."),

    20: _ts_exam(
        "Build what the mapped type describes",
        "`Getters<T>` renames each key to `getX` returning that property's type. The input is a name. Build the getters object at runtime for `{ name, size: 5 }`, then print `getName()`, `getSize()`, and the getter keys sorted and comma-joined.",
        '''
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };
const source = { name: input, size: 5 };
function makeGetters<T extends object>(obj: T): Getters<T> {
  const out: { [k: string]: () => unknown } = {};
  for (const key of Object.keys(obj)) {
    out["get" + key.charAt(0).toUpperCase() + key.slice(1)] = () =>
      (obj as { [k: string]: unknown })[key];
  }
  return out as Getters<T>;
}
const getters = makeGetters(source);
console.log(getters.getName());
console.log(getters.getSize());
console.log(Object.keys(getters).sort().join(","));
''',
        [("ada", "ada\n5\ngetName,getSize"), ("bob", "bob\n5\ngetName,getSize")],
        hint="The mapped type is erased — the loop has to produce the renamed keys itself, and the cast at the end is where you assert it matched."),

    21: _ts_exam(
        "Unwrap and compact",
        "Write `Unwrap<T>` (element type of an array, else T) and `NonNil<T>` (drops null/undefined from a union). The input is a line of tokens where `-` means null. Print the first non-null token or `(none)`, then the compacted tokens space-separated or `(none)`, then how many were dropped.",
        '''
type Unwrap<T> = T extends (infer U)[] ? U : T;
type NonNil<T> = T extends null | undefined ? never : T;
function firstOrSelf<T>(value: T): Unwrap<T> {
  return (Array.isArray(value) ? value[0] : value) as Unwrap<T>;
}
function compact<T>(items: T[]): NonNil<T>[] {
  return items.filter((x) => x !== null && x !== undefined) as NonNil<T>[];
}
const raw = input.split(/\\s+/).map((t) => (t === "-" ? null : t));
const kept = compact(raw);
console.log(firstOrSelf(kept) ?? "(none)");
console.log(kept.join(" ") || "(none)");
console.log(raw.length - kept.length);
''',
        [("- a b", "a\na b\n1"), ("- -", "(none)\n(none)\n2"),
         ("x y", "x\nx y\n0"), ("a - b -", "a\na b\n2")],
        hint="Both types are erased, so each function ends in a cast — the type describes what the runtime branch is obliged to produce."),

    22: _ts_exam(
        "Event catalogue",
        "Entities are `user`, `order`; actions are `created`, `updated`, `deleted`. Derive `EventName` as a template literal over `as const` arrays and build the catalogue at runtime. The input is `n` then `n` candidate names. Print `ok` or `bad` per name, then the catalogue size, then the names for `user` sorted.",
        '''
const lines = input.split("\\n");
const n = Number(lines[0]);
const entities = ["user", "order"] as const;
const actions = ["created", "updated", "deleted"] as const;
type Entity = (typeof entities)[number];
type Action = (typeof actions)[number];
type EventName = `${Entity}:${Action}`;
const catalogue: EventName[] = [];
for (const entity of entities) {
  for (const action of actions) {
    catalogue.push(`${entity}:${action}`);
  }
}
const known = new Set<string>(catalogue);
for (let i = 1; i <= n; i++) {
  console.log(known.has((lines[i] ?? "").trim()) ? "ok" : "bad");
}
console.log(catalogue.length);
console.log(catalogue.filter((e) => e.startsWith("user:")).sort().join(" "));
''',
        [("2\nuser:created\nuser:archived", "ok\nbad\n6\nuser:created user:deleted user:updated"),
         ("1\norder:deleted", "ok\n6\nuser:created user:deleted user:updated"),
         ("1\nnope", "bad\n6\nuser:created user:deleted user:updated")],
        hint="The nested loops over the two as-const arrays produce exactly the six names the template literal type describes."),
})


TS_EXAM_MORE_TESTS.update({
    18: [
        ('2\nb 10\nb 9', 'b: 9 10\n1'),
        ('3\nc 1\na 1\nb 1', 'a: 1\nb: 1\nc: 1\n3'),
        ('4\nx -1\nx 5\nx -1\ny 0', 'x: -1 5\ny: 0\n2'),
        ('1\ncat 100', 'cat: 100\n1'),
        ('5\nm 3\nm 1\nm 2\nm 3\nm 1', 'm: 1 2 3\n1'),
    ],
    19: [
        ('3\nwrap\nsize\ntheme', 'true\n14\ndark\nwrap'),
        ('1\ntoString', 'unknown\nwrap'),
        ('2\nTheme\nsize', 'unknown\n14\nwrap'),
        ('1\nconstructor', 'unknown\nwrap'),
        ('0', 'wrap'),
    ],
    20: [
        ('x', 'x\n5\ngetName,getSize'),
        ('Grace', 'Grace\n5\ngetName,getSize'),
        ('longer-name', 'longer-name\n5\ngetName,getSize'),
        ('Z', 'Z\n5\ngetName,getSize'),
        ('123', '123\n5\ngetName,getSize'),
        ('two words', 'two words\n5\ngetName,getSize'),
    ],
    21: [
        ('-', '(none)\n(none)\n1'),
        ('a', 'a\na\n0'),
        ('- - x', 'x\nx\n2'),
        ('p q r -', 'p\np q r\n1'),
    ],
    22: [
        ('3\norder:created\norder:updated\nuser:deleted', 'ok\nok\nok\n6\nuser:created user:deleted user:updated'),
        ('2\nUser:created\nuser:Created', 'bad\nbad\n6\nuser:created user:deleted user:updated'),
        ('1\nuser:', 'bad\n6\nuser:created user:deleted user:updated'),
        ('2\norder:deleted\norder:deleted', 'ok\nok\n6\nuser:created user:deleted user:updated'),
        ('0', '6\nuser:created user:deleted user:updated'),
    ],
})
