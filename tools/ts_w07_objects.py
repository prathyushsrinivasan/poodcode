# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 7 — objects.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 7 ---------------------------------------------------------------
_WEEKS.append(_week(
    7, 2, _M2,
    "Objects",
    "Model a 'thing' as a bundle of named fields, reach into it safely, and process arrays of records.",
    """
An array holds many values in a row. An **object** holds a few values *by name*:

```ts
const expense = { desc: "coffee", amount: 3.25, paid: true };
```

Arrays answer "which one?" with a number. Objects answer "which one?" with a
word — and words are what real data is made of. An expense has a description,
an amount and a paid flag; calling them `e[0]`, `e[1]`, `e[2]` would be
technically possible and humanly hopeless.

Put the two together and you get **an array of objects** — the shape of very
nearly every dataset you will ever touch:

```ts
const expenses = [
  { desc: "coffee", amount: 3.25, paid: true },
  { desc: "book",   amount: 12,   paid: false },
];
```

This week: building objects, reaching into them (including when a field might
not be there), passing them around, processing lists of them, the sharing
behaviour that catches everyone out, and using an object as a **lookup table** —
which is the single most useful trick in the whole course.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Create objects, read fields with dot access, and update or add fields",
        "Reach a field whose name is decided at runtime, with bracket access",
        "Handle missing fields with in, optional chaining and ??",
        "Navigate nested objects and arrays inside objects",
        "Take objects as parameters and return them, with destructuring",
        "Filter, map and sort an array of records by a field",
        "Tell sharing from copying, and make a copy with spread",
        "Count and group with an object used as a lookup table",
        "Group records into buckets keyed by any field, in a single pass",
        "Summarise each bucket and print the report in a stable, sorted order",
    ],
    why="Objects are how a program talks about the real world — a user, an order, a row, a config. Once you can model data as records and process a list of them, you can write actual applications.",
    est_minutes=550,
    glossary=[
        _gloss("object", "A bundle of named values: { name: \"Ada\" }."),
        _gloss("property / field / key", "One named slot on an object."),
        _gloss("value", "What is stored in a slot."),
        _gloss("dot access", "Reaching a known field: obj.name."),
        _gloss("bracket access", "Reaching a field by a name computed at runtime: obj[k]."),
        _gloss("shorthand", "{ name } is short for { name: name }."),
        _gloss("in", "Tests whether a key exists: \"paid\" in obj."),
        _gloss("optional chaining (?.)", "Reads a field only if the thing exists, else undefined."),
        _gloss("?? (nullish coalescing)", "A fallback used only for null/undefined, not for 0 or \"\"."),
        _gloss("destructuring", "Pulling fields into names: const { desc, amount } = e;"),
        _gloss("record", "An object used as one row of data."),
        _gloss("reference", "A name pointing at an object. Two names can point at the same one."),
        _gloss("aliasing", "Two names sharing one object, so a change through either is seen by both."),
        _gloss("shallow copy", "{ ...o } — a new top-level object, but nested objects are still shared."),
        _gloss("lookup table", "An object used as a name-to-value map."),
        _gloss("Object.keys / values / entries", "Turn an object into an array of its keys, values, or [key, value] pairs."),
        _gloss("grouping", "Bucketing records under a key so each bucket holds every matching item."),
        _gloss("bucket", "The array (or running total) stored under one key of a lookup table."),
        _gloss("accumulator table", "A lookup whose values are running totals rather than arrays."),
        _gloss("deterministic output", "Output that is identical for identical input — here, by sorting the keys."),
    ],
    cheatsheet="""
```ts
// ---- create & read ---------------------------------------------------
const e = { desc: "coffee", amount: 3.25, paid: true };
e.desc                    // "coffee"
e.missing                 // undefined  (no error)
e.amount = 4;             // update
e.tag = "food";           // add (needs a `let`-style shape or an annotation)

const desc = "tea";
const f = { desc };       // shorthand for { desc: desc }

// ---- dynamic keys -----------------------------------------------------
const k = "amount";
e[k]                      // 3.25   bracket access
"paid" in e               // true
Object.keys(e)            // ["desc","amount","paid"]
Object.values(e)          // ["coffee",3.25,true]
Object.entries(e)         // [["desc","coffee"], ...]

// ---- possibly missing --------------------------------------------------
user?.address?.city       // undefined instead of a crash
e.note ?? "(none)"        // fallback ONLY for null/undefined
e.count ?? 0              // 0 stays 0; ||  would replace it

// ---- nested ------------------------------------------------------------
const u = { name: "Ada", address: { city: "London" }, tags: ["a","b"] };
u.address.city            // "London"
u.tags[0]                 // "a"

// ---- functions ---------------------------------------------------------
function total(e: { amount: number; qty: number }): number {
  return e.amount * e.qty;
}
function label({ desc, amount }: { desc: string; amount: number }): string {
  return `${desc}: ${amount}`;      // destructured parameter
}

// ---- arrays of records --------------------------------------------------
const rows = [{ n: "a", v: 2 }, { n: "b", v: 9 }];
rows.filter((r) => r.v > 5)
rows.map((r) => r.n)
[...rows].sort((p, q) => p.v - q.v)

// ---- sharing vs copying --------------------------------------------------
const b = a;              // ⚠️ same object
const c = { ...a };       // a fresh shallow copy
const d = { ...a, v: 9 }; // copy with one field replaced

// ---- lookup table / tally -------------------------------------------------
const counts: { [key: string]: number } = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
```
""",
    self_check=[
        "Can you read and update a field on an object?",
        "Can you say what `obj.nope` gives you, and why that is dangerous?",
        "Can you reach a field whose name is in a variable?",
        "Can you total one field across an array of records?",
        "Can you sort records by a field without mutating the original array?",
        "Can you explain why `const b = a` then `b.x = 1` changes `a` too?",
        "Can you count word frequencies with an object?",
        "Can you group an array of records by one of their fields without knowing the categories in advance?",
        "Can you say when to bucket into arrays and when to accumulate straight into numbers?",
    ],
    review=[
        _q("How do you read the `name` of `user`?",
           ["user[name]", "user->name", "user.name", "name(user)"], 2,
           "Dot access for a key you know at write time."),
        _q("`({a: 1}).b` evaluates to…", ["null", "0", "undefined", "an error"], 2,
           "Missing fields are undefined, silently."),
        _q("`const k = \"a\"; ({a: 1})[k]` is…", ["undefined", "1", '"a"', "an error"], 1,
           "Bracket access uses the VALUE of k as the key."),
        _q("`obj?.x` when obj is undefined gives…",
           ["a crash", "undefined", "null", "0"], 1,
           "Optional chaining short-circuits instead of throwing."),
        _q("`0 ?? 5` is…", ["5", "0", "undefined", "an error"], 1,
           "?? only falls back for null/undefined — 0 is a real value. `0 || 5` would give 5."),
        _q("`const b = a; b.x = 9;` — what is `a.x`?",
           ["unchanged", "9", "undefined", "an error"], 1,
           "Both names point at the same object."),
        _q("`{ ...a }` gives you…",
           ["the same object", "a shallow copy", "a deep copy", "an array"], 1,
           "Top level is fresh; nested objects are still shared."),
        _q("`Object.keys({a:1, b:2})` is…",
           ["[1,2]", '["a","b"]', "2", '[["a",1],["b",2]]'], 1,
           "The key names, as an array of strings."),
        _q("Sorting records by a numeric field uses the comparator…",
           ["(p, q) => p.v > q.v", "(p, q) => p.v - q.v", "(p, q) => p - q", "none"], 1,
           "Same rule as week 6 — subtract, don't compare."),
        _q("`counts[w] = (counts[w] ?? 0) + 1;` — why the `?? 0`?",
           ["style", "the first time a word appears, counts[w] is undefined",
            "to reset the count", "it is optional"], 1,
           "undefined + 1 is NaN, so the first occurrence needs a starting value."),
        _q("The two lines at the heart of grouping are…",
           ["sort then join", "create the bucket if missing, then push",
            "keys then values", "filter then map"], 1,
           "Everything else is choosing what the key should be."),
        _q("`tally[k] = tally[k] + 1` for a brand-new key gives…",
           ["1", "0", "NaN", "an error"], 2,
           "undefined + 1 is NaN — start from (tally[k] ?? 0)."),
        _q("Sorting `Object.keys(groups)` before printing gives you…",
           ["faster lookup", "a report that is identical for identical input",
            "sorted buckets", "fewer keys"], 1,
           "Stable output is what makes a report testable."),
    ],
    milestone="Budget Buddy now models each expense as a proper record and reports over the whole list — the data shape real applications use.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w7-basics", "Object basics",
            "Keys, values and dot access.",
            """
An **object literal** is a comma-separated list of `key: value` pairs in braces:

```ts
const point = { x: 3, y: 4 };
const user = { name: "Ada", age: 36, admin: true };
```

Keys are names; values can be anything — numbers, strings, booleans, arrays,
even other objects.

**Reading** uses a dot:

```ts
point.x        // 3
user.name      // "Ada"
```

**Updating** assigns through the same dot:

```ts
point.y = point.y + 1;    // 5
user.age += 1;            // 37
```

**`const` doesn't freeze it** — same as arrays last week. `const` fixes the
name, not the contents:

```ts
const p = { x: 1 };
p.x = 2;        // ✅ fine
p = { x: 3 };   // ❌ error — cannot repoint the name
```

**A missing key gives `undefined`**, quietly:

```ts
user.email     // undefined — no error, no warning at runtime
```

This is the object equivalent of reading past the end of an array, and it's why
a typo like `user.nmae` produces a mystery `undefined` three functions later
rather than an error at the scene. TypeScript catches this one for you when the
object's shape is known — one of the clearest wins the language offers.

**Shorthand.** When a variable already has the name you want for the key, say
it once:

```ts
const desc = "coffee";
const e = { desc };          // same as { desc: desc }
```

> ⚠️ **Common mistakes:** separating pairs with `;` instead of `,` inside the
> braces; misspelling a key on read (silent `undefined`) or on write (you
> quietly create a *new* field); and expecting `const` to prevent field updates.
""",
            warmup=[
                _q("`const u = { age: 5 }; console.log(u.age);` prints…",
                   ["age", "5", "u.age", "undefined"], 1, "It reads the value."),
                _q("`const u = { age: 5 }; console.log(u.name);` prints…",
                   ["null", "undefined", "an error", '""'], 1,
                   "Missing keys read as undefined."),
                _q("`const p = { x: 1 }; p.x = 2;` is…",
                   ["an error, p is const", "fine", "a no-op", "a copy"], 1,
                   "const fixes the binding, not the contents."),
                _q("`const n = 'a'; const o = { n };` gives o the key…",
                   ['"n"', '"a"', "both", "none"], 0,
                   'Shorthand uses the VARIABLE NAME as the key: { n: "a" }.'),
            ],
            exercises=[
                _ex("tscourse-w7-b-1", "Read a field", "Print the user's name.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                    'user.name', [("", "Ada")],
                    hints=["Reach it with a dot."]),
                _ex("tscourse-w7-b-2", "Update a field",
                    "Add 5 to counter.value, then print it.",
                    'const counter = { value: 0 };\ncounter.value = counter.value + 5;\nconsole.log(counter.value);\n',
                    'counter.value + 5', [("", "5")],
                    hints=["Read the current value and add to it."]),
                _ex("tscourse-w7-b-3", "Build an object",
                    "Build an expense with desc `coffee` and amount 3, then print the amount.",
                    'const e = { desc: "coffee", amount: 3 };\nconsole.log(e.amount);\n',
                    '{ desc: "coffee", amount: 3 }', [("", "3")],
                    hints=["Pairs are key: value, separated by commas.",
                           'Write { desc: "coffee", amount: 3 }.']),
                _ex("tscourse-w7-b-4", "Two fields in a sentence",
                    "Print `Ada is 36`.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(`${user.name} is ${user.age}`);\n',
                    '`${user.name} is ${user.age}`', [("", "Ada is 36")],
                    hints=["Two holes, each a dot access.",
                           "Write `${user.name} is ${user.age}`."]),
                _ex("tscourse-w7-b-5", "Shorthand",
                    "Build the object using shorthand so its key is `desc`.",
                    _FS + 'const desc = fs.readFileSync(0, "utf8").trim();\n'
                    'const e = { desc };\nconsole.log(e.desc);\n',
                    '{ desc }', [("coffee", "coffee"), ("rent", "rent")],
                    hints=["When the variable is already named right, say it once.",
                           "Write { desc }."]),
                _fix("tscourse-w7-b-fix1", "Fix the field name",
                     "This should print the name but prints undefined. Fix it.",
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.username);\n',
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                     [("", "Ada")],
                     hints=["There is no `username` key on this object.",
                            "The key is `name`."]),
                _fix("tscourse-w7-b-fix2", "Fix the typo'd write",
                     "This should print 5, but the update lands on the wrong field and it prints 0. Fix it.",
                     'const counter = { value: 0 };\ncounter.valeu = 5;\nconsole.log(counter.value);\n',
                     'const counter = { value: 0 };\ncounter.value = 5;\nconsole.log(counter.value);\n',
                     [("", "5")],
                     hints=["Writing a misspelled key silently creates a brand-new field.",
                            "The key is `value`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Reading a key that does not exist gives…",
                   ["an error", "null", "undefined", "0"], 2,
                   "Silently — which is exactly why annotating shapes is worth it."),
                _q("Objects answer 'which one?' with…",
                   ["a number", "a name", "an index", "a type"], 1,
                   "Arrays use positions; objects use names."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w7-access", "Dynamic keys & missing fields",
            "Bracket access, in, ?. and ??.",
            """
Dot access needs the key spelled out when you write the code. When the key is
only known at **runtime**, use brackets:

```ts
const e = { desc: "coffee", amount: 3 };
const k = "amount";

e.k        // ⚠️ undefined — looks for a key literally called "k"
e[k]       // 3            — uses the VALUE of k
```

That distinction is the whole lesson: `e.k` is the key `"k"`; `e[k]` is the key
whose name `k` holds.

**Does the key exist?** `in` asks directly:

```ts
"amount" in e     // true
"paid" in e       // false
```

Why not just check `e.paid === undefined`? Because a key *can* exist and hold
`undefined`. `in` distinguishes "absent" from "present but empty".

**Optional chaining `?.`** reads through something that might not be there:

```ts
const u = { name: "Ada" };
u.address.city      // 💥 crashes — cannot read city of undefined
u.address?.city     // undefined — stops safely
```

Read `a?.b` as *"if `a` is null or undefined, the whole thing is `undefined`;
otherwise carry on"*. It short-circuits the rest of the chain, so
`u?.address?.city` is safe at every step.

**Nullish coalescing `??`** supplies a fallback:

```ts
e.note ?? "(none)"      // "(none)" when note is missing
```

`??` falls back **only** for `null` and `undefined`. Its older cousin `||` falls
back for every falsy value, which quietly destroys legitimate data:

```ts
const count = 0;
count || 10     // 10  ⚠️ a real zero was thrown away
count ?? 10     // 0   ✅
```

When the fallback is for *missing*, use `??`. Reserve `||` for genuine
true/false logic.

> ⚠️ **Common mistakes:** writing `e.k` when you meant `e[k]`; using `||` where
> `??` was needed and losing zeros and empty strings; and reaching for `?.`
> everywhere, which hides bugs — use it where a value is *genuinely* optional.
""",
            warmup=[
                _q('`const k = "a"; const o = { a: 1 }; o[k]` is…',
                   ["undefined", "1", '"a"', "an error"], 1, "Bracket access uses k's value."),
                _q('`const k = "a"; const o = { a: 1 }; o.k` is…',
                   ["1", "undefined", '"a"', "an error"], 1,
                   'Dot access looks for a key literally named "k".'),
                _q("`undefined?.x` is…", ["a crash", "undefined", "null", "0"], 1,
                   "Optional chaining stops safely."),
                _q("`0 || 5` and `0 ?? 5` are…", ["5 and 5", "0 and 0", "5 and 0", "0 and 5"], 2,
                   "|| treats 0 as falsy; ?? only replaces null/undefined."),
            ],
            exercises=[
                _ex("tscourse-w7-ac-1", "Key from a variable",
                    "Print the value of the field named by `k`.",
                    'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e[k]);\n',
                    'e[k]', [("", "3")],
                    hints=["Brackets use the value held in k.", "Write e[k]."]),
                # The index-signature annotation is load-bearing, not decoration:
                # `e[k]` where k is only known at run time is a type error on a
                # plain object literal (TS7053), because the compiler cannot
                # prove k is one of the declared keys. Saying "this object is
                # indexed by string" is the honest way to ask for that.
                _ex("tscourse-w7-ac-2", "Key from input",
                    "Read a field name from input and print that field's value.",
                    _FS + 'const e: { [key: string]: string | number } = '
                    '{ desc: "coffee", amount: 3 };\n'
                    'const k = fs.readFileSync(0, "utf8").trim();\nconsole.log(e[k]);\n',
                    'e[k]', [("desc", "coffee"), ("amount", "3")],
                    hints=["The key is only known when the program runs.",
                           "Write e[k]."]),
                _ex("tscourse-w7-ac-3", "Does it have one?",
                    "Print whether the object has a `paid` key.",
                    'const e = { desc: "coffee", amount: 3 };\nconsole.log("paid" in e);\n',
                    '"paid" in e', [("", "false")],
                    hints=["`in` tests for the key's presence.",
                           'Write "paid" in e.']),
                _ex("tscourse-w7-ac-4", "Safe deep read",
                    "Print the city, or `undefined` if there is no address — without crashing.",
                    'const u: { name: string; address?: { city: string } } = { name: "Ada" };\n'
                    'console.log(u.address?.city);\n',
                    'u.address?.city', [("", "undefined")],
                    hints=["Reading .city off a missing address would crash.",
                           "Write u.address?.city."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ac-5", "A sensible fallback",
                    "Print the note, or `(none)` when there isn't one.",
                    'const e: { desc: string; note?: string } = { desc: "coffee" };\n'
                    'console.log(e.note ?? "(none)");\n',
                    'e.note ?? "(none)"', [("", "(none)")],
                    hints=["?? supplies a value only when the left side is null/undefined.",
                           'Write e.note ?? "(none)".']),
                _ex("tscourse-w7-ac-6", "Keep a real zero",
                    "Print the count, defaulting to 10 only when it is genuinely missing. Here it is 0, so 0 must print.",
                    'const e: { count?: number } = { count: 0 };\nconsole.log(e.count ?? 10);\n',
                    'e.count ?? 10', [("", "0")],
                    hints=["|| would throw the zero away.",
                           "Write e.count ?? 10."],
                    difficulty="Medium"),
                _fix("tscourse-w7-ac-fix1", "Fix the dot-versus-bracket",
                     "This should print 3 but prints undefined. Fix it.",
                     'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e.k);\n',
                     'const e = { desc: "coffee", amount: 3 };\nconst k = "amount";\nconsole.log(e[k]);\n',
                     [("", "3")],
                     hints=['e.k looks for a key spelled "k", which does not exist.',
                            "Use brackets so the VALUE of k is the key."],
                     difficulty="Medium"),
                _fix("tscourse-w7-ac-fix2", "Fix the swallowed zero",
                     "A count of 0 is real data, but this prints 10. Fix it.",
                     'const e: { count?: number } = { count: 0 };\nconsole.log(e.count || 10);\n',
                     'const e: { count?: number } = { count: 0 };\nconsole.log(e.count ?? 10);\n',
                     [("", "0")],
                     hints=["0 is falsy, so || replaces it.",
                            "?? only falls back for null and undefined."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`obj[k]` uses as the key…",
                   ['the letter "k"', "the value stored in k", "index k", "nothing"], 1,
                   "That is the whole point of bracket access."),
                _q("Prefer `??` over `||` when…",
                   ["always", "the fallback is for a MISSING value and 0 or \"\" are legitimate",
                    "never", "comparing booleans"], 1,
                   "Otherwise real zeros and empty strings get replaced."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w7-nested", "Nested data",
            "Objects inside objects, arrays inside objects.",
            """
A field's value can be another object, or an array. Real data nests:

```ts
const user = {
  name: "Ada",
  address: { city: "London", postcode: "E1" },
  tags: ["engineer", "founder"],
};
```

Read it by chaining, left to right:

```ts
user.address.city     // "London"
user.tags[0]          // "engineer"
user.tags.length      // 2
```

`user.address.city` means: take `user`, take its `address` (an object), take
that object's `city`. Each step must actually exist — if `address` were missing,
the second step crashes, which is exactly what `?.` is for.

**Arrays of objects, with objects inside them**, are entirely normal:

```ts
const orders = [
  { id: 1, customer: { name: "Ada" }, items: ["pen", "ink"] },
  { id: 2, customer: { name: "Bo" },  items: ["pad"] },
];

orders[0].customer.name     // "Ada"
orders[1].items.length      // 1
```

**Building nested data from input** is the everyday task. Given a line per
record:

```
coffee 3
book 12
```

split into lines, then split each line:

```ts
const rows = fs.readFileSync(0, "utf8").trim().split("\\n");
const items = rows.map((line) => {
  const parts = line.trim().split(" ");
  return { desc: parts[0], amount: Number(parts[1]) };
});
```

That callback has braces, so it needs an explicit `return` — the arrow trap
again. (An alternative is to wrap the object in parentheses:
`(line) => ({ desc: ... })`, which tells TypeScript the braces are an *object*
and not a function body. Both work; the explicit `return` is easier to read.)

**Depth is a cost.** `a.b.c.d.e` is fragile: five things must exist, and one
rename anywhere breaks it. Pull intermediate values into named variables when a
chain gets long.

> ⚠️ **Common mistakes:** reading through a missing level and crashing;
> forgetting `return` in a braced `map` callback that builds an object; and
> forgetting that a nested array still needs `[i]`, not `.i`.
""",
            warmup=[
                _q('`{a: {b: 2}}.a.b` is…', ["undefined", "2", "{b: 2}", "an error"], 1,
                   "Chain left to right."),
                _q('`{tags: ["x","y"]}.tags[1]` is…', ['"x"', '"y"', "1", "undefined"], 1,
                   "Index the array after reaching it."),
                _q('`{a: 1}.b.c` does what?',
                   ["gives undefined", "crashes", "gives null", "gives 1"], 1,
                   "`.b` is undefined, and reading `.c` off undefined throws."),
                _q("`(line) => { desc: line }` returns…",
                   ["an object", "undefined", "a string", "an error"], 1,
                   "The braces read as a function body, not an object literal."),
            ],
            exercises=[
                _ex("tscourse-w7-ne-1", "Reach into a nested object",
                    "Print the user's city.",
                    'const user = { name: "Ada", address: { city: "London" } };\n'
                    'console.log(user.address.city);\n',
                    'user.address.city', [("", "London")],
                    hints=["Chain the dots left to right."]),
                _ex("tscourse-w7-ne-2", "An array inside an object",
                    "Print how many tags the user has.",
                    'const user = { name: "Ada", tags: ["engineer", "founder"] };\n'
                    'console.log(user.tags.length);\n',
                    'user.tags.length', [("", "2")],
                    hints=["Reach the array, then take its length."]),
                _ex("tscourse-w7-ne-3", "Into a list of records",
                    "Print the name of the customer on the SECOND order.",
                    'const orders = [\n'
                    '  { id: 1, customer: { name: "Ada" } },\n'
                    '  { id: 2, customer: { name: "Bo" } },\n'
                    '];\n'
                    'console.log(orders[1]!.customer.name);\n',
                    'orders[1]!.customer.name', [("", "Bo")],
                    hints=["Index the array first, then chain the dots.",
                           "You can see index 1 is there, so ! is honest here.",
                           "Write orders[1]!.customer.name."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ne-4", "Records from input",
                    "Each input line is `desc amount`. Build the records and print the first description.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const parts = line.trim().split(" ");\n'
                    '  return { desc: parts[0] ?? "", amount: Number(parts[1]) };\n'
                    '});\n'
                    'console.log(items[0]!.desc);\n',
                    'return { desc: parts[0] ?? "", amount: Number(parts[1]) };',
                    [("coffee 3\nbook 12", "coffee"), ("rent 900", "rent")],
                    hints=["The callback has braces, so it needs an explicit return.",
                           "desc must be a string, and parts[0] might be missing — give it a fallback.",
                           'Return { desc: parts[0] ?? "", amount: Number(parts[1]) };'],
                    difficulty="Medium"),
                _ex("tscourse-w7-ne-5", "Total from built records",
                    "Each line is `desc amount`. Print the total of the amounts.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const parts = line.trim().split(" ");\n'
                    '  return { desc: parts[0], amount: Number(parts[1]) };\n'
                    '});\n'
                    'let total = 0;\nfor (const it of items) {\n  total += it.amount;\n}\n'
                    'console.log(total);\n',
                    'total += it.amount;',
                    [("coffee 3\nbook 12", "15"), ("rent 900", "900")],
                    hints=["Accumulate the amount field across the records.",
                           "Write total += it.amount;"],
                    difficulty="Medium"),
                _fix("tscourse-w7-ne-fix1", "Fix the object-literal callback",
                     "This should print `coffee` but prints `undefined` — the callback returns nothing. Fix it.",
                     _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const items = rows.map((line) => {\n'
                     '  const parts = line.trim().split(" ");\n'
                     '  ({ desc: parts[0], amount: Number(parts[1]) });\n'
                     '});\n'
                     'console.log(items[0]?.desc);\n',
                     _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                     'const items = rows.map((line) => {\n'
                     '  const parts = line.trim().split(" ");\n'
                     '  return { desc: parts[0], amount: Number(parts[1]) };\n'
                     '});\n'
                     'console.log(items[0]?.desc);\n',
                     [("coffee 3", "coffee"), ("book 12\nrent 900", "book")],
                     hints=["The object is built and then thrown away.",
                            "Add return in front of it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`a.b.c` crashes when…",
                   ["c is missing", "b is missing", "a is missing", "b is missing or a is missing"], 3,
                   "You can read a missing FINAL field safely; reading THROUGH a missing one throws."),
                _q("To return an object from a braceless arrow you write…",
                   ["(x) => { a: x }", "(x) => ({ a: x })", "(x) => a: x", "impossible"], 1,
                   "The parentheses tell TypeScript the braces are an object literal."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w7-funcs", "Objects & functions",
            "Passing records in, handing records back, destructuring.",
            """
Functions take and return objects like any other value. The parameter's type is
written as the shape itself:

```ts
function lineTotal(e: { amount: number; qty: number }): number {
  return e.amount * e.qty;
}
lineTotal({ amount: 3, qty: 4 });   // 12
```

Note the shape uses `;` between fields (a semicolon inside a *type*, a comma
inside a *value* — an inconsistency worth simply memorising).

**Returning an object** lets a function hand back several values at once:

```ts
function stats(a: number[]): { count: number; total: number } {
  let total = 0;
  for (const x of a) total += x;
  return { count: a.length, total };
}
const s = stats([1, 2, 3]);
console.log(s.total);    // 6
```

That's the answer to "how do I return two things?" — return one object with two
fields.

**Destructuring** pulls fields out into local names:

```ts
const e = { desc: "coffee", amount: 3 };
const { desc, amount } = e;
console.log(desc, amount);      // coffee 3
```

It works on **parameters** too, which is where it earns its keep — the function
signature then lists exactly what it uses:

```ts
function label({ desc, amount }: { desc: string; amount: number }): string {
  return `${desc}: $${amount}`;
}
```

Compare with `e.desc` and `e.amount` repeated through a long body. Destructuring
names them once.

You can rename and default while destructuring:

```ts
const { desc: name, note = "(none)" } = e;
```

**Objects are passed by reference.** A function receives the *same* object, so
changing a field inside is visible to the caller:

```ts
function bump(o: { n: number }): void { o.n += 1; }
const p = { n: 1 };
bump(p);
console.log(p.n);    // 2  ⚠️
```

That's a side effect of exactly the kind week 5 warned about. Prefer returning a
**new** object:

```ts
function bumped(o: { n: number }): { n: number } { return { ...o, n: o.n + 1 }; }
```

> ⚠️ **Common mistakes:** using `,` instead of `;` in an inline shape type;
> mutating a parameter object and surprising the caller; and forgetting that
> destructuring copies the *value* — for a nested object, that value is still a
> shared reference.
""",
            warmup=[
                _q("`function f(e: { a: number }): number { return e.a; } f({a: 7})` is…",
                   ["7", "undefined", "{a:7}", "an error"], 0, "It reads the field."),
                _q("`const { a } = { a: 1, b: 2 };` leaves `a` as…",
                   ["1", "2", "{a:1}", "undefined"], 0, "Destructuring pulls out the field."),
                _q("A function that mutates its object parameter…",
                   ["cannot", "changes the caller's object too", "makes a copy",
                    "returns it"], 1,
                   "Objects are handed over by reference."),
                _q("How do you return two values from a function?",
                   ["you cannot", "return an object with two fields", "return twice",
                    "use a global"], 1,
                   "One object, several fields."),
            ],
            exercises=[
                _ex("tscourse-w7-fu-1", "Take an object",
                    "Return the line total from the record's amount and qty.",
                    'function lineTotal(e: { amount: number; qty: number }): number {\n'
                    '  return e.amount * e.qty;\n}\n'
                    'console.log(lineTotal({ amount: 3, qty: 4 }));\n',
                    'e.amount * e.qty', [("", "12")],
                    hints=["Multiply the two fields."]),
                _ex("tscourse-w7-fu-2", "Return an object",
                    "Return a record holding the count and the total.",
                    'function stats(a: number[]): { count: number; total: number } {\n'
                    '  let total = 0;\n  for (const x of a) {\n    total += x;\n  }\n'
                    '  return { count: a.length, total };\n}\n'
                    'const s = stats([1, 2, 3]);\nconsole.log(`${s.count} ${s.total}`);\n',
                    'return { count: a.length, total };', [("", "3 6")],
                    hints=["Bundle both answers into one object; `total` can use shorthand.",
                           "Write return { count: a.length, total };"],
                    difficulty="Medium"),
                _ex("tscourse-w7-fu-3", "Destructure a record",
                    "Pull `desc` and `amount` out of the record in one line, then print them.",
                    'const e = { desc: "coffee", amount: 3 };\n'
                    'const { desc, amount } = e;\n'
                    'console.log(`${desc} ${amount}`);\n',
                    'const { desc, amount } = e;', [("", "coffee 3")],
                    hints=["Braces on the LEFT of = destructure.",
                           "Write const { desc, amount } = e;"]),
                _ex("tscourse-w7-fu-4", "Destructure a parameter",
                    "Destructure the parameter so the body can use `desc` and `amount` directly.",
                    'function label({ desc, amount }: { desc: string; amount: number }): string {\n'
                    '  return `${desc}: $${amount}`;\n}\n'
                    'console.log(label({ desc: "coffee", amount: 3 }));\n',
                    '{ desc, amount }', [("", "coffee: $3")],
                    hints=["The destructuring pattern goes where the parameter name would.",
                           "Write { desc, amount } before the type annotation."],
                    difficulty="Medium"),
                _ex("tscourse-w7-fu-5", "Return a changed copy",
                    "Return a NEW record with n increased by one, leaving the original alone.",
                    'function bumped(o: { n: number }): { n: number } {\n'
                    '  return { ...o, n: o.n + 1 };\n}\n'
                    'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                    'return { ...o, n: o.n + 1 };', [("", "1 2")],
                    hints=["Spread the old fields, then override the one that changes.",
                           "Write return { ...o, n: o.n + 1 };"],
                    difficulty="Medium"),
                _fix("tscourse-w7-fu-fix1", "Fix the field access",
                     "This should print the first name but reads the wrong field. Fix it.",
                     'function first(p: { first: string; last: string }): string {\n  return p.last;\n}\n'
                     'console.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     'function first(p: { first: string; last: string }): string {\n  return p.first;\n}\n'
                     'console.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     [("", "Ada")],
                     hints=["It returns p.last.", "Return p.first."]),
                _fix("tscourse-w7-fu-fix2", "Fix the surprise mutation",
                     "The caller's object should be untouched — expected `1 2` — but this prints `2 2`. Fix it.",
                     'function bumped(o: { n: number }): { n: number } {\n  o.n = o.n + 1;\n  return o;\n}\n'
                     'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                     'function bumped(o: { n: number }): { n: number } {\n  return { ...o, n: o.n + 1 };\n}\n'
                     'const p = { n: 1 };\nconst q = bumped(p);\nconsole.log(`${p.n} ${q.n}`);\n',
                     [("", "1 2")],
                     hints=["The function is handed the caller's own object and edits it.",
                            "Build and return a new one instead: { ...o, n: o.n + 1 }."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Inside an inline shape type, fields are separated by…",
                   [",", ";", ":", "nothing"], 1,
                   "Semicolons in a type, commas in a value."),
                _q("Destructuring a parameter mainly buys you…",
                   ["speed", "a signature that names exactly what the function uses",
                    "type safety", "immutability"], 1,
                   "It documents the function's real dependencies."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w7-records", "Arrays of records",
            "The shape of real datasets.",
            """
Put last week's array methods together with this week's objects and you can
answer real questions about real data:

```ts
const people = [
  { name: "Ada", age: 36 },
  { name: "Bo",  age: 20 },
  { name: "Cy",  age: 47 },
];
```

**Total a field** — a loop and an accumulator:

```ts
let total = 0;
for (const p of people) total += p.age;
```

**Select rows** — `filter` with a predicate on a field:

```ts
people.filter((p) => p.age >= 21);      // Ada and Cy
```

**Pull out one column** — `map` to a field:

```ts
people.map((p) => p.name);              // ["Ada","Bo","Cy"]
people.map((p) => p.name).join(", ");   // "Ada, Bo, Cy"
```

**Find one row:**

```ts
people.find((p) => p.name === "Bo");        // the record, or undefined
people.some((p) => p.age > 40);             // true
```

**Sort by a field** — the week 6 comparator, reading a field from each side:

```ts
[...people].sort((p, q) => p.age - q.age);            // youngest first
[...people].sort((p, q) => q.age - p.age);            // oldest first
[...people].sort((p, q) => p.name.localeCompare(q.name));  // by name
```

`localeCompare` returns a negative/zero/positive number comparing two strings —
exactly the comparator contract. And the copy (`[...people]`) matters just as
much here: sorting in place reorders the array everyone else is holding.

**Chaining reads like a sentence** once you're used to it:

```ts
people
  .filter((p) => p.age >= 21)
  .map((p) => p.name)
  .join(", ");                    // "Ada, Cy"
```

Filter, then map, then join: narrow the rows, pick the column, print it.

> ⚠️ **Common mistakes:** reading a field that doesn't exist and totalling
> `NaN`; sorting in place and corrupting the source array; and mapping before
> filtering, which does more work than necessary.
""",
            warmup=[
                _q("Totalling `age` over [{age:1},{age:2},{age:3}] gives…",
                   ["3", "6", "123", "an error"], 1, "1+2+3."),
                _q("`[{a:1},{a:2}].filter((o) => o.a > 1).length` is…",
                   ["0", "1", "2", "an error"], 1, "Only {a:2} passes."),
                _q("`[{n:\"x\"},{n:\"y\"}].map((o) => o.n).join(\"-\")` is…",
                   ['"x-y"', '"xy"', '["x","y"]', '"x, y"'], 0,
                   "Pull the column, then glue it."),
                _q("Totalling a MISSPELLED field over records gives…",
                   ["0", "NaN", "undefined", "an error"], 1,
                   "undefined + a number is NaN, and NaN spreads."),
            ],
            exercises=[
                _ex("tscourse-w7-re-1", "Total a column",
                    "Sum everyone's age and print it.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'let total = 0;\nfor (const p of people) {\n  total += p.age;\n}\nconsole.log(total);\n',
                    'total += p.age;', [("", "56")],
                    hints=["Accumulate the age field."]),
                _ex("tscourse-w7-re-2", "Count matching rows",
                    "Count people aged 21 or older.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log(people.filter((p) => p.age >= 21).length);\n',
                    'p.age >= 21', [("", "2")],
                    hints=["21 itself counts, so the test is >=."]),
                _ex("tscourse-w7-re-3", "Pull a column",
                    "Print everyone's name, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'console.log(people.map((p) => p.name).join(", "));\n',
                    'people.map((p) => p.name)', [("", "Ada, Bo")],
                    hints=["map to the field, then join.",
                           "Write people.map((p) => p.name)."]),
                _ex("tscourse-w7-re-4", "Find a row",
                    "Print Bo's age, found by name.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                    'const bo = people.find((p) => p.name === "Bo");\nconsole.log(bo?.age);\n',
                    'people.find((p) => p.name === "Bo")', [("", "20")],
                    hints=["find returns the record itself, or undefined.",
                           'Write people.find((p) => p.name === "Bo").'],
                    difficulty="Medium"),
                _ex("tscourse-w7-re-5", "Sort by a field",
                    "Print the names youngest first, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log([...people].sort((p, q) => p.age - q.age).map((p) => p.name).join(", "));\n',
                    '(p, q) => p.age - q.age', [("", "Bo, Ada, Cy")],
                    hints=["Same comparator rule as week 6, reading a field from each side.",
                           "Write (p, q) => p.age - q.age."],
                    difficulty="Medium"),
                _ex("tscourse-w7-re-6", "Filter then map",
                    "Print the names of everyone 21 or older, comma-separated.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n  { name: "Cy", age: 47 },\n];\n'
                    'console.log(people.filter((p) => p.age >= 21).map((p) => p.name).join(", "));\n',
                    '.filter((p) => p.age >= 21).map((p) => p.name)',
                    [("", "Ada, Cy")],
                    hints=["Narrow the rows first, then pick the column.",
                           "Chain .filter(...) then .map(...)."],
                    difficulty="Medium"),
                _fix("tscourse-w7-re-fix1", "Fix the wrong field",
                     "This should total ages (56) but prints NaN. Fix it.",
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                     'let total = 0;\nfor (const p of people) {\n  total += p.years;\n}\nconsole.log(total);\n',
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\n'
                     'let total = 0;\nfor (const p of people) {\n  total += p.age;\n}\nconsole.log(total);\n',
                     [("", "56")],
                     hints=["There is no `years` field, so each read is undefined — and 0 + undefined is NaN.",
                            "The field is `age`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which order does less work?",
                   ["map then filter", "filter then map", "identical", "neither works"], 1,
                   "Filtering first leaves fewer elements to transform."),
                _q("`[...rows].sort(...)` rather than `rows.sort(...)` because…",
                   ["it is faster", "sort mutates, and other code may be holding rows",
                    "sort needs a copy", "no reason"], 1,
                   "The same rule as week 6."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w7-copy", "Sharing, copying & spread",
            "Why changing one object changed another.",
            """
An object variable does not hold the object. It holds a **reference** — the
address of one. Assigning copies the address, not the object:

```ts
const a = { n: 1 };
const b = a;        // b points at THE SAME object
b.n = 9;
console.log(a.n);   // 9   ⚠️
```

Both names sit in front of one object. This is called **aliasing**, and it is
behind a whole family of bugs that feel like magic: a value changes and nothing
nearby touched it.

**Comparison follows the same rule.** `===` on objects asks "the same object?",
not "the same contents?":

```ts
{ n: 1 } === { n: 1 }     // false — two different objects
const a = { n: 1 }; a === a   // true
```

**Copying** uses spread:

```ts
const c = { ...a };            // a fresh object with the same fields
const d = { ...a, n: 9 };      // copy, with n replaced
```

`{ ...a, n: 9 }` is the everyday "change one field without mutating" move —
later fields win, so the override goes last. It's how you'll update state in
almost any modern framework.

**The copy is shallow.** Spread copies each field's *value* — and for a nested
object, that value is another reference:

```ts
const u = { name: "Ada", address: { city: "London" } };
const v = { ...u };
v.address.city = "Paris";
console.log(u.address.city);    // "Paris"  ⚠️ still shared
```

The top level is fresh; anything nested is not. To copy a level down, spread
that level too:

```ts
const v = { ...u, address: { ...u.address } };
```

For deeply nested data, `structuredClone(u)` copies the whole tree.

**The same is true of arrays of objects.** `[...rows]` gives you a new array
holding the *same* record objects — reordering it is safe, editing a record
through it is not.

> ⚠️ **Common mistakes:** expecting `=` to copy; comparing objects with `===`
> and expecting contents to be compared; and trusting a shallow copy to protect
> nested data.
""",
            warmup=[
                _q("`const a={n:1}; const b=a; b.n=9; a.n` is…", ["1", "9", "undefined", "an error"], 1,
                   "One object, two names."),
                _q("`({n:1}) === ({n:1})` is…", ["true", "false"], 1,
                   "Different objects, so not identical — contents are not compared."),
                _q("`{ ...a, n: 9 }` produces…",
                   ["a mutated a", "a copy with n replaced", "an error", "just {n:9}"], 1,
                   "Later fields override earlier ones."),
                _q("After `const v = { ...u }`, changing `v.address.city` affects `u` because…",
                   ["spread is broken", "the copy is shallow — nested objects are still shared",
                    "address is const", "it does not"], 1,
                   "Only the top level was duplicated."),
            ],
            exercises=[
                _ex("tscourse-w7-cp-1", "Make a real copy",
                    "Copy the object so changing the copy leaves the original at 1.",
                    'const a = { n: 1 };\nconst b = { ...a };\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                    'const b = { ...a };', [("", "1 9")],
                    hints=["Assignment shares; spread copies.",
                           "Write const b = { ...a };"]),
                _ex("tscourse-w7-cp-2", "Copy with an override",
                    "Build a new record with the same fields but amount 9.",
                    'const e = { desc: "coffee", amount: 3 };\n'
                    'const f = { ...e, amount: 9 };\n'
                    'console.log(`${f.desc} ${f.amount} ${e.amount}`);\n',
                    '{ ...e, amount: 9 }', [("", "coffee 9 3")],
                    hints=["Spread first, then name the field you want different.",
                           "Write { ...e, amount: 9 }."],
                    difficulty="Medium"),
                _ex("tscourse-w7-cp-3", "Compare identity",
                    "Print whether the two separately-built objects are the same object.",
                    'const a = { n: 1 };\nconst b = { n: 1 };\nconsole.log(a === b);\n',
                    'a === b', [("", "false")],
                    hints=["=== on objects asks about identity, not contents."]),
                _ex("tscourse-w7-cp-4", "Copy one level down",
                    "Copy the user so changing the copy's city leaves the original as London.",
                    'const u = { name: "Ada", address: { city: "London" } };\n'
                    'const v = { ...u, address: { ...u.address } };\n'
                    'v.address.city = "Paris";\n'
                    'console.log(`${u.address.city} ${v.address.city}`);\n',
                    '{ ...u, address: { ...u.address } }',
                    [("", "London Paris")],
                    hints=["A plain spread leaves address shared.",
                           "Spread the nested object too: { ...u, address: { ...u.address } }."],
                    difficulty="Medium"),
                _ex("tscourse-w7-cp-5", "Copy an array of records",
                    "Sort a copy by amount so the original order survives.",
                    'const rows = [{ n: "a", v: 2 }, { n: "b", v: 1 }];\n'
                    'const sorted = [...rows].sort((p, q) => p.v - q.v);\n'
                    'console.log(sorted.map((r) => r.n).join(""));\n'
                    'console.log(rows.map((r) => r.n).join(""));\n',
                    '[...rows].sort((p, q) => p.v - q.v)', [("", "ba\nab")],
                    hints=["Spread the array before sorting it.",
                           "Write [...rows].sort((p, q) => p.v - q.v)."],
                    difficulty="Medium"),
                _fix("tscourse-w7-cp-fix1", "Fix the shared object",
                     "This should print `1 9` but prints `9 9`. Fix it.",
                     'const a = { n: 1 };\nconst b = a;\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                     'const a = { n: 1 };\nconst b = { ...a };\nb.n = 9;\nconsole.log(`${a.n} ${b.n}`);\n',
                     [("", "1 9")],
                     hints=["`const b = a;` gives the same object a second name.",
                            "Spread to build a fresh one."],
                     difficulty="Medium"),
                _fix("tscourse-w7-cp-fix2", "Fix the shallow copy",
                     "This should print `London Paris` but prints `Paris Paris`. Fix it.",
                     'const u = { name: "Ada", address: { city: "London" } };\n'
                     'const v = { ...u };\nv.address.city = "Paris";\n'
                     'console.log(`${u.address.city} ${v.address.city}`);\n',
                     'const u = { name: "Ada", address: { city: "London" } };\n'
                     'const v = { ...u, address: { ...u.address } };\nv.address.city = "Paris";\n'
                     'console.log(`${u.address.city} ${v.address.city}`);\n',
                     [("", "London Paris")],
                     hints=["Spread copies only the top level; address is still the same object.",
                            "Spread the nested object as well."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("An object variable holds…",
                   ["the object", "a reference to the object", "a copy", "a name"], 1,
                   "Which is why assignment shares rather than copies."),
                _q("`{ ...a, x: 1 }` versus `{ x: 1, ...a }` — the difference is…",
                   ["none", "which one wins: the LAST mention of a field",
                    "the first is invalid", "the second is faster"], 1,
                   "In the second, a's own x would override the 1."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w7-tally", "Objects as lookup tables",
            "Counting, grouping, and looking things up by name.",
            """
So far objects have modelled *one thing* with a fixed set of fields. They have a
second life: as a **lookup table** from arbitrary names to values.

```ts
const prices: { [key: string]: number } = {
  coffee: 3.25,
  book: 12,
};
prices["coffee"];    // 3.25
```

That annotation — `{ [key: string]: number }` — is an **index signature**. It
says *"any string key, and every value is a number"*. Use it when the keys are
data rather than a fixed schema.

**Counting** is the classic use, and worth knowing cold:

```ts
const counts: { [key: string]: number } = {};
for (const w of words) {
  counts[w] = (counts[w] ?? 0) + 1;
}
```

The `?? 0` carries the whole idea. The first time a word appears, `counts[w]` is
`undefined`, and `undefined + 1` is `NaN`. The fallback supplies the starting
value. (`|| 0` happens to work here too, since a count of 0 never survives, but
`??` states the intent: *only* when missing.)

**Why an object rather than searching an array?** Looking a key up in an object
is effectively instant no matter how many keys there are, where scanning an
array to find a match takes longer as it grows. Counting a million words with an
array of pairs would be unusably slow; with an object it's immediate. You'll
give this a name — O(1) versus O(n) — in Month 6.

**Reading a table back out:**

```ts
Object.keys(counts)      // ["a", "b"]
Object.values(counts)    // [2, 1]
Object.entries(counts)   // [["a", 2], ["b", 1]]
```

`entries` gives an array of `[key, value]` pairs, which you can then sort or map
like any array:

```ts
Object.entries(counts)
  .sort((p, q) => q[1] - p[1])          // by count, descending
  .map((p) => `${p[0]}:${p[1]}`)
  .join(", ");
```

`p[0]` is the key and `p[1]` the value. You can destructure the pair instead,
which reads better: `.map(([k, v]) => `${k}:${v}`)`.

**Grouping** is the same move with arrays as the values:

```ts
const byTag: { [key: string]: string[] } = {};
for (const e of expenses) {
  if (byTag[e.tag] === undefined) byTag[e.tag] = [];
  byTag[e.tag].push(e.desc);
}
```

Make sure the bucket exists, then push into it. (`Map` — a purpose-built
alternative — arrives in week 18.)

> ⚠️ **Common mistakes:** forgetting `?? 0` and getting `NaN`; forgetting to
> create the empty array before pushing; and assuming key order is meaningful
> (it mostly follows insertion order for string keys, but don't rely on it —
> sort explicitly).
""",
            warmup=[
                _q("`counts[w] = counts[w] + 1;` on a brand-new word gives…",
                   ["1", "0", "NaN", "an error"], 2,
                   "undefined + 1 is NaN — hence the ?? 0."),
                _q("`Object.keys({a:1,b:2})` is…",
                   ['["a","b"]', "[1,2]", "2", '[["a",1],["b",2]]'], 0, "The key names."),
                _q("`Object.entries({a:1})` is…",
                   ['["a",1]', '[["a",1]]', '{a:1}', '["a"]'], 1,
                   "An array of [key, value] pairs — one pair here."),
                _q("Looking a key up in an object versus scanning an array…",
                   ["the array is faster", "the object stays fast as it grows",
                    "identical", "objects cannot be searched"], 1,
                   "Key lookup does not get slower with size."),
            ],
            exercises=[
                _ex("tscourse-w7-ta-1", "A price table",
                    "Look up the price of the word given on input.",
                    _FS + 'const prices: { [key: string]: number } = { coffee: 3.25, book: 12 };\n'
                    'const k = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(prices[k]);\n',
                    'prices[k]', [("coffee", "3.25"), ("book", "12")],
                    hints=["Bracket access with the runtime key."]),
                _ex("tscourse-w7-ta-2", "Count the words",
                    "Count how many times each word appears, then print the count for `a`.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'console.log(counts["a"] ?? 0);\n',
                    'counts[w] = (counts[w] ?? 0) + 1;',
                    [("a b a c a", "3"), ("b c", "0")],
                    hints=["The first sighting of a word has no existing count.",
                           "Write counts[w] = (counts[w] ?? 0) + 1;"],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-3", "How many distinct",
                    "Print how many DISTINCT words the input contains.",
                    _WORDS + 'const seen: { [key: string]: boolean } = {};\n'
                    'for (const w of words) {\n  seen[w] = true;\n}\n'
                    'console.log(Object.keys(seen).length);\n',
                    'Object.keys(seen).length',
                    [("a b a c a", "3"), ("x", "1")],
                    hints=["Each distinct word becomes one key.",
                           "Count the keys: Object.keys(seen).length."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-4", "Read the table out",
                    "Print each word and its count as `a:3` lines, sorted alphabetically by word.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'for (const k of Object.keys(counts).sort()) {\n  console.log(`${k}:${counts[k]}`);\n}\n',
                    'Object.keys(counts).sort()',
                    [("b a a", "a:2\nb:1"), ("x", "x:1")],
                    hints=["Key order is not guaranteed, so sort the keys explicitly.",
                           "Write Object.keys(counts).sort()."],
                    difficulty="Medium"),
                _ex("tscourse-w7-ta-5", "The most common word",
                    "Print the most frequent word. On a tie, the alphabetically first wins.",
                    _WORDS + 'const counts: { [key: string]: number } = {};\n'
                    'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                    'const best = Object.keys(counts).sort().sort((p, q) => (counts[q] ?? 0) - (counts[p] ?? 0))[0];\n'
                    'console.log(best);\n',
                    '(p, q) => (counts[q] ?? 0) - (counts[p] ?? 0)',
                    [("a b a c a", "a"), ("b b c c", "b"), ("z", "z")],
                    hints=["Sort alphabetically first, then re-sort by count descending — sort is stable, so ties keep the alphabetical order.",
                           "A table lookup can always miss, so each count needs a ?? 0 fallback.",
                           "The count comparator is (p, q) => (counts[q] ?? 0) - (counts[p] ?? 0)."],
                    difficulty="Medium"),
                _fix("tscourse-w7-ta-fix1", "Fix the NaN count",
                     "This should print 3 for `a b a c a` but prints NaN. Fix it.",
                     _WORDS + 'const counts: { [key: string]: number } = {};\n'
                     'for (const w of words) {\n  counts[w] = counts[w] + 1;\n}\n'
                     'console.log(counts["a"]);\n',
                     _WORDS + 'const counts: { [key: string]: number } = {};\n'
                     'for (const w of words) {\n  counts[w] = (counts[w] ?? 0) + 1;\n}\n'
                     'console.log(counts["a"]);\n',
                     [("a b a c a", "3"), ("a", "1")],
                     hints=["The first time a word is seen, its count is undefined.",
                            "Supply a starting value: (counts[w] ?? 0) + 1."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`{ [key: string]: number }` describes…",
                   ["one field called key", "any string key, with number values",
                    "an array", "a function"], 1,
                   "An index signature, for tables whose keys are data."),
                _q("Why `?? 0` in a tally?",
                   ["style", "the first occurrence has no existing count",
                    "to reset", "for speed"], 1,
                   "Otherwise undefined + 1 is NaN."),
                _q("To group values under a key you must first…",
                   ["sort", "make sure the bucket array exists", "count them",
                    "use an array"], 1,
                   "Pushing onto undefined throws."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w7-group", "Grouping & summarising",
            "Bucket records by a key, then report each bucket.",
            """
A tally answers *how many of each*. **Grouping** answers the bigger question:
*which ones, in each bucket* — and once you have the buckets you can summarise
them any way you like. It is the single most common shape of real reporting
code, and it is three lines of pattern.

**The bucket pattern.** The table's values are arrays instead of numbers:

```ts
const byLetter: { [key: string]: string[] } = {};

for (const w of ["ant", "bee", "ape", "bat"]) {
  const key = w[0];
  if (!(key in byLetter)) byLetter[key] = [];   // create the bucket once
  byLetter[key].push(w);                        // then always push
}
// { a: ["ant", "ape"], b: ["bee", "bat"] }
```

Those two lines never change. The only decision you make is **what the key is** —
`w[0]` here, `expense.category` in Budget Buddy, `user.country` at work.

The same idea with the `??` fallback from the previous lesson:

```ts
byLetter[key] = byLetter[key] ?? [];
byLetter[key].push(w);
```

Both are fine. Pick one and use it everywhere.

**Then walk the buckets.** `Object.keys` gives you the keys, and `.sort()` makes
the report **deterministic** — the same input always prints in the same order,
which is what makes output testable:

```ts
for (const key of Object.keys(byLetter).sort()) {
  const bucket = byLetter[key];
  console.log(`${key}: ${bucket.length} — ${bucket.join(", ")}`);
}
```

**Summarising a bucket** is ordinary array work on `byLetter[key]`: count with
`.length`, total with a running sum, best with a running maximum.

```ts
const totals: { [key: string]: number } = {};
for (const s of sales) {
  totals[s.region] = (totals[s.region] ?? 0) + s.amount;   // sum straight in
}
```

Notice the choice: bucket into **arrays** when you still need the individual
items later, and accumulate into **numbers** when you only ever want the total.
Grouping keeps your options open; accumulating is cheaper.

**Grouping is one pass.** Resist the urge to loop once per category — you'd have
to know the categories in advance, and you'd read the data as many times as
there are keys. One pass over the records builds every bucket at once, whatever
the categories turn out to be.

> ⚠️ **Common mistakes:** pushing into a bucket that was never created (a crash
> on `undefined.push`); *assigning* `groups[key] = [item]` instead of pushing, so
> each bucket only ever holds the last item; and adding to a missing numeric
> bucket, where `undefined + 1` quietly gives you `NaN`.
""",
            warmup=[
                _q("After bucketing `[\"ant\",\"ape\"]` by first letter, `groups[\"a\"]` is…",
                   ['"ape"', '["ant", "ape"]', '2', 'undefined'], 1,
                   "The value is an array holding every item that matched the key."),
                _q("`groups[key].push(w)` without creating the bucket first…",
                   ["works fine", "crashes, because groups[key] is undefined",
                    "creates the bucket automatically", "returns NaN"], 1,
                   "You cannot call .push on undefined."),
                _q("`totals[k] = totals[k] + 1` on a key seen for the first time gives…",
                   ["1", "0", "NaN", "undefined"], 2,
                   "undefined + 1 is NaN — supply a starting value with ?? 0."),
                _q("Why `.sort()` the keys before printing?",
                   ["it is faster", "so the report comes out in the same order every time",
                    "objects cannot be read otherwise", "it removes duplicates"], 1,
                   "Deterministic output is what makes a report testable."),
            ],
            exercises=[
                _ex("tscourse-w7-grp-1", "Create the bucket",
                    "Group the words by their first letter. Add the line that creates a bucket the first time a letter is seen.",
                    'const words = ["ant", "bee", "ape", "bat"];\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const w of words) {\n'
                    '  const key = w[0] ?? "";\n'
                    '  if (!(key in groups)) groups[key] = [];\n'
                    '  groups[key]!.push(w);\n'
                    '}\n'
                    'console.log(Object.keys(groups).sort().join(","));\n'
                    'console.log(groups["a"]!.join(" "));\n',
                    'if (!(key in groups)) groups[key] = [];',
                    [("", "a,b\nant ape")],
                    hints=["Use the `in` operator to ask whether the key exists yet.",
                           "Write if (!(key in groups)) groups[key] = [];",
                           "The ! on the next line is earned by exactly this check: after it, the bucket is definitely there."]),
                _ex("tscourse-w7-grp-2", "Push into the bucket",
                    "The buckets are created; now add each expense's name to the bucket for its category.",
                    'const expenses = [\n'
                    '  { name: "coffee", category: "food" },\n'
                    '  { name: "novel", category: "books" },\n'
                    '  { name: "bread", category: "food" },\n'
                    '];\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const e of expenses) {\n'
                    '  groups[e.category] = groups[e.category] ?? [];\n'
                    '  groups[e.category]!.push(e.name);\n'
                    '}\n'
                    'console.log(groups["food"]!.join(" + "));\n',
                    'groups[e.category]!.push(e.name);',
                    [("", "coffee + bread")],
                    hints=["The bucket for this record is groups[e.category].",
                           "The line above just guaranteed it exists, so ! is earned.",
                           "Push the name onto it: groups[e.category]!.push(e.name);"]),
                _ex("tscourse-w7-grp-3", "Walk the buckets in order",
                    "Print one line per category, alphabetically. Fill in how the keys are obtained and ordered.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const groups: { [key: string]: string[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0] ?? "";\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat]!.push(parts[1] ?? "");\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  console.log(`${cat}: ${groups[cat]!.join(", ")}`);\n'
                    '}\n',
                    'Object.keys(groups).sort()',
                    [("fruit,apple\nveg,leek\nfruit,fig", "fruit: apple, fig\nveg: leek"),
                     ("b,two\na,one", "a: one\nb: two")],
                    hints=["Object.keys gives you the bucket names as an array.",
                           "Sorting that array makes the report order stable."],
                    difficulty="Easy"),
                _ex("tscourse-w7-grp-4", "Accumulate instead of bucketing",
                    "You only need the totals here, so add straight into a numeric table. Fill in the accumulating line.",
                    'const sales = [\n'
                    '  { region: "north", amount: 30 },\n'
                    '  { region: "south", amount: 20 },\n'
                    '  { region: "north", amount: 12 },\n'
                    '];\n'
                    'const totals: { [key: string]: number } = {};\n'
                    'for (const s of sales) {\n'
                    '  totals[s.region] = (totals[s.region] ?? 0) + s.amount;\n'
                    '}\n'
                    'for (const r of Object.keys(totals).sort()) {\n'
                    '  console.log(`${r} ${totals[r]}`);\n'
                    '}\n',
                    'totals[s.region] = (totals[s.region] ?? 0) + s.amount;',
                    [("", "north 42\nsouth 20")],
                    hints=["The first time a region appears there is no running total yet.",
                           "Fall back to 0 with ?? before adding the amount."],
                    difficulty="Easy"),
                _ex("tscourse-w7-grp-5", "Find the biggest bucket",
                    "Report which category holds the most items. Fill in the comparison.",
                    'const groups: { [key: string]: string[] } = {\n'
                    '  fruit: ["apple", "fig"],\n'
                    '  veg: ["leek"],\n'
                    '  drink: ["tea", "coffee", "cocoa"],\n'
                    '};\n'
                    'let best = "";\n'
                    'for (const k of Object.keys(groups).sort()) {\n'
                    '  if (best === "" || groups[k]!.length > groups[best]!.length) best = k;\n'
                    '}\n'
                    'console.log(`${best} (${groups[best]!.length})`);\n',
                    'groups[k]!.length > groups[best]!.length',
                    [("", "drink (3)")],
                    hints=["Compare this bucket's length against the best one found so far.",
                           "Both keys came out of Object.keys(groups), so both buckets exist — ! says so.",
                           "Write groups[k]!.length > groups[best]!.length."],
                    difficulty="Medium"),
                _fix("tscourse-w7-grp-fix1", "Fix the missing bucket",
                     "This should print `ant ape` but crashes on the first word, because nothing ever creates the bucket.",
                     'const words = ["ant", "bee", "ape"];\n'
                     'const groups: { [key: string]: string[] } = {};\n'
                     'for (const w of words) {\n'
                     '  const k = w[0] ?? "";\n'
                     '  groups[k]!.push(w);\n'
                     '}\n'
                     'console.log(groups["a"]!.join(" "));\n',
                     'const words = ["ant", "bee", "ape"];\n'
                     'const groups: { [key: string]: string[] } = {};\n'
                     'for (const w of words) {\n'
                     '  const k = w[0] ?? "";\n'
                     '  groups[k] = groups[k] ?? [];\n'
                     '  groups[k]!.push(w);\n'
                     '}\n'
                     'console.log(groups["a"]!.join(" "));\n',
                     [("", "ant ape")],
                     hints=["The very first time a letter appears, groups[letter] is undefined.",
                            "The ! promised the bucket was there. Nothing had made that true yet.",
                            "Create an empty array for it before pushing."]),
                _fix("tscourse-w7-grp-fix2", "Fix the overwritten bucket",
                     "This should print `ant ape` but prints only `ape`. Each record is replacing the bucket instead of joining it.",
                     'const groups: { [key: string]: string[] } = {};\n'
                     'const words = ["ant", "ape", "bee"];\n'
                     'for (const w of words) {\n'
                     '  const k = w[0] ?? "";\n'
                     '  if (!(k in groups)) groups[k] = [];\n'
                     '  groups[k] = [w];\n'
                     '}\n'
                     'console.log(groups["a"]!.join(" "));\n',
                     'const groups: { [key: string]: string[] } = {};\n'
                     'const words = ["ant", "ape", "bee"];\n'
                     'for (const w of words) {\n'
                     '  const k = w[0] ?? "";\n'
                     '  if (!(k in groups)) groups[k] = [];\n'
                     '  groups[k]!.push(w);\n'
                     '}\n'
                     'console.log(groups["a"]!.join(" "));\n',
                     [("", "ant ape")],
                     hints=["Assigning a fresh one-element array throws away everything already in the bucket.",
                            "Add to the existing bucket with .push(w) instead."],
                     difficulty="Medium"),
                _fix("tscourse-w7-grp-fix3", "Fix the NaN tally",
                     "This should print `2 1` but prints `NaN NaN`. The first addition has nothing to add to.",
                     'const tally: { [key: string]: number } = {};\n'
                     'for (const c of ["a", "b", "a"]) {\n'
                     '  tally[c] = tally[c] + 1;\n'
                     '}\n'
                     'console.log(`${tally["a"]} ${tally["b"]}`);\n',
                     'const tally: { [key: string]: number } = {};\n'
                     'for (const c of ["a", "b", "a"]) {\n'
                     '  tally[c] = (tally[c] ?? 0) + 1;\n'
                     '}\n'
                     'console.log(`${tally["a"]} ${tally["b"]}`);\n',
                     [("", "2 1")],
                     hints=["A key that has never been seen reads back as undefined.",
                            "undefined + 1 is NaN — supply 0 with ?? before adding."]),
                _ch("tscourse-w7-grp-ch1", "Grouped spending report", "Medium",
                    "Each input line is `category,item,price`. Group the prices by category, then print one line per category in alphabetical order: `category: N item(s), total $X.XX`, singular when the category holds exactly one item.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const groups: { [key: string]: number[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0] ?? "";\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat]!.push(Number(parts[2]));\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  const prices = groups[cat]!;\n'
                    '  let total = 0;\n'
                    '  for (const p of prices) total = total + p;\n'
                    '  const label = prices.length === 1 ? "item" : "items";\n'
                    '  console.log(`${cat}: ${prices.length} ${label}, total $${total.toFixed(2)}`);\n'
                    '}\n',
                    'const groups: { [key: string]: number[] } = {};\n'
                    'for (const line of lines) {\n'
                    '  const parts = line.trim().split(",");\n'
                    '  const cat = parts[0] ?? "";\n'
                    '  groups[cat] = groups[cat] ?? [];\n'
                    '  groups[cat]!.push(Number(parts[2]));\n'
                    '}\n'
                    'for (const cat of Object.keys(groups).sort()) {\n'
                    '  const prices = groups[cat]!;\n'
                    '  let total = 0;\n'
                    '  for (const p of prices) total = total + p;\n'
                    '  const label = prices.length === 1 ? "item" : "items";\n'
                    '  console.log(`${cat}: ${prices.length} ${label}, total $${total.toFixed(2)}`);\n'
                    '}',
                    [("food,apple,1.50\nbooks,novel,29.99\nfood,bread,2.25",
                      "books: 1 item, total $29.99\nfood: 2 items, total $3.75"),
                     ("a,x,1\na,y,2\na,z,3", "a: 3 items, total $6.00")],
                    hints=["One pass builds the buckets; a second pass over the sorted keys prints the report.",
                           "The bucket here holds numbers, so its annotation is { [key: string]: number[] }.",
                           "Sum a bucket with a running total in a for..of loop.",
                           'Pick the word with a ternary: prices.length === 1 ? "item" : "items".']),
            ],
            quiz=[
                _q("The two lines at the heart of grouping are…",
                   ["sort then join", "create the bucket if missing, then push",
                    "filter then map", "keys then values"], 1,
                   "Everything else is deciding what the key should be."),
                _q("Bucket into arrays rather than accumulating numbers when…",
                   ["there are many keys", "you still need the individual items later",
                    "the values are strings", "the input is sorted"], 1,
                   "Grouping keeps the members; accumulating keeps only the answer."),
                _q("`Object.keys(groups).sort()` is used so that…",
                   ["the buckets are sorted", "the report prints in a stable, testable order",
                    "duplicate keys are removed", "lookup gets faster"], 1,
                   "The keys are ordered; the buckets themselves are untouched."),
                _q("How many passes over the records does grouping take?",
                   ["one per category", "one, whatever the categories turn out to be",
                    "two per category", "one per record squared"], 1,
                   "That is exactly why you group rather than loop per category."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #7 — the expense ledger",
        """
Budget Buddy grows up: expenses become **records**, and the report is built
from them.

Input is one expense per line — `desc amount paid` — where `paid` is `y` or
`n`:

```
coffee 3.25 y
book 12 n
lunch 9.50 n
rent 900 y
```

Print:

```
Entries:  4
Total:    $924.75
Unpaid:   $21.50 (book, lunch)
Biggest:  rent ($900.00)
```

Rules:

- Build an array of records with `desc` (string), `amount` (number) and `paid`
  (boolean — `true` when the third field is `y`).
- `Unpaid` shows the unpaid total, then the unpaid descriptions in **input
  order**, joined with `, `.
- `Biggest` is the single largest expense, paid or not.
- Money always carries two decimal places.
""",
        _ch("tscourse-w7-capstone", "Budget Buddy #7", "Medium",
            "Parse the lines into records, then report on them.",
            _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
            'const items = rows.map((line) => {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0] ?? "", amount: Number(p[1]), paid: p[2] === "y" };\n'
            '});\n'
            'let total = 0;\n'
            'for (const it of items) {\n  total += it.amount;\n}\n'
            'const unpaid = items.filter((it) => !it.paid);\n'
            'let unpaidTotal = 0;\n'
            'for (const it of unpaid) {\n  unpaidTotal += it.amount;\n}\n'
            'const biggest = [...items].sort((p, q) => q.amount - p.amount)[0]!;\n'
            'console.log(`Entries:  ${items.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Unpaid:   $${unpaidTotal.toFixed(2)} (${unpaid.map((it) => it.desc).join(", ")})`);\n'
            'console.log(`Biggest:  ${biggest.desc} ($${biggest.amount.toFixed(2)})`);\n',
            'const items = rows.map((line) => {\n'
            '  const p = line.trim().split(" ");\n'
            '  return { desc: p[0] ?? "", amount: Number(p[1]), paid: p[2] === "y" };\n'
            '});\n'
            'let total = 0;\n'
            'for (const it of items) {\n  total += it.amount;\n}\n'
            'const unpaid = items.filter((it) => !it.paid);\n'
            'let unpaidTotal = 0;\n'
            'for (const it of unpaid) {\n  unpaidTotal += it.amount;\n}\n'
            'const biggest = [...items].sort((p, q) => q.amount - p.amount)[0]!;\n'
            'console.log(`Entries:  ${items.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Unpaid:   $${unpaidTotal.toFixed(2)} (${unpaid.map((it) => it.desc).join(", ")})`);\n'
            'console.log(`Biggest:  ${biggest.desc} ($${biggest.amount.toFixed(2)})`);',
            [("coffee 3.25 y\nbook 12 n\nlunch 9.50 n\nrent 900 y",
              "Entries:  4\nTotal:    $924.75\nUnpaid:   $21.50 (book, lunch)\nBiggest:  rent ($900.00)"),
             ("tea 2 n",
              "Entries:  1\nTotal:    $2.00\nUnpaid:   $2.00 (tea)\nBiggest:  tea ($2.00)"),
             ("a 5 y\nb 5 y",
              "Entries:  2\nTotal:    $10.00\nUnpaid:   $0.00 ()\nBiggest:  a ($5.00)")],
            hints=["Parse first: split into lines, then split each line into three parts.",
                   'paid is a boolean, so convert it: p[2] === "y".',
                   "Filter to the unpaid records ONCE and reuse that array for both the total and the names — it keeps input order automatically.",
                   "Biggest comes from sorting a copy descending by amount and taking element 0.",
                   "Every money figure ends in .toFixed(2)."]),
        example_io="Entries:  4\nTotal:    $924.75\nUnpaid:   $21.50 (book, lunch)\nBiggest:  rent ($900.00)",
        rubric=["Each line becomes a record with desc, amount and a boolean paid",
                "The unpaid list preserves input order",
                "Biggest is found without mutating the items array",
                "All money is formatted to two decimal places"],
        stretch=_ch("tscourse-w7-capstone-stretch", "Budget Buddy #7 (stretch)", "Medium",
                    "Add a `By tag:` line. Each line now ends with a tag (`coffee 3.25 y food`); total the amounts per tag and print them sorted alphabetically as `food=$12.75; rent=$900.00`.",
                    _FS + 'const rows = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const items = rows.map((line) => {\n'
                    '  const p = line.trim().split(" ");\n'
                    '  return { desc: p[0] ?? "", amount: Number(p[1]), paid: p[2] === "y", tag: p[3] ?? "" };\n'
                    '});\n'
                    'const byTag: { [key: string]: number } = {};\n'
                    'for (const it of items) {\n  byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;\n}\n'
                    'const parts = Object.keys(byTag).sort().map((t) => `${t}=$${(byTag[t] ?? 0).toFixed(2)}`);\n'
                    'console.log(`By tag: ${parts.join("; ")}`);\n',
                    'const byTag: { [key: string]: number } = {};\n'
                    'for (const it of items) {\n  byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;\n}\n'
                    'const parts = Object.keys(byTag).sort().map((t) => `${t}=$${(byTag[t] ?? 0).toFixed(2)}`);\n'
                    'console.log(`By tag: ${parts.join("; ")}`);',
                    [("coffee 3.25 y food\nlunch 9.50 n food\nrent 900 y home",
                      "By tag: food=$12.75; home=$900.00"),
                     ("tea 2 n drink", "By tag: drink=$2.00")],
                    hints=["This is the tally pattern, accumulating an amount rather than a count.",
                           "byTag[it.tag] = (byTag[it.tag] ?? 0) + it.amount;",
                           "Sort the keys before mapping so the output is deterministic."]),
    ),
))
