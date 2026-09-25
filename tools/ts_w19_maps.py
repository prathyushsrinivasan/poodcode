# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 19 — maps & sets.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
#
# ---------------------------------------------------------------------------
# THIS IS THE WEEK `Map` AND `Set` UNLOCK. `_SCOPE_RULES` gates `new Map(`,
# `new Map<`, `new Set(` and `new Set<` at 19, so every lookup in weeks 1-18 is
# an object, a `Record` or an array scan. Week 18 in particular had to build its
# bracket table as a `Record<string, string>` and its queue as an array — so this
# week arrives as the *answer* to a cost the learner has already paid, rather
# than as a new API to memorise. The lesson text leans on that: lesson 1 is
# explicitly "here is what the Record you have been using cannot do".
#
# ---------------------------------------------------------------------------
# THE FOUR FACTS THIS WEEK IS BUILT ON — all verified against the real runner,
# because each one is the kind of claim that is easy to get subtly wrong.
#
#  1. AN OBJECT REORDERS INTEGER-LIKE KEYS, AND A MAP DOES NOT.
#         o["10"]=…; o["2"]=…; o["b"]=…; o["a"]=…
#         Object.keys(o)  ->  2,10,b,a      ← integer-like first, ASCENDING
#         [...m.keys()]   ->  10,2,b,a      ← insertion order, always
#     This is the single most convincing argument for `Map`, and it is invisible
#     until somebody shows you the output. Lesson 5 is built on it.
#
#  2. AN EMPTY OBJECT ALREADY "HAS" A `toString` KEY.
#         const o: Record<string, number> = {};
#         "toString" in o        ->  true    ← from the prototype
#         Object.keys(o).length  ->  0
#         new Map().has("toString") -> false
#     Which makes `in` on a Record a genuinely unsafe membership test, and is why
#     `Object.hasOwn` exists. Lesson 1.
#
#  3. `map.get(k)` IS `V | undefined`, ALWAYS — not because of a flag, but
#     because the key might not be there. Every read in this week takes a `??`
#     or a guard, exactly like an index access (week 16, lesson 7); `TS2532` is
#     what you get for forgetting.
#
#  4. TWO STRUCTURALLY IDENTICAL OBJECTS ARE TWO DIFFERENT MAP KEYS.
#         m.set({name:"food"}, 1); m.set({name:"food"}, 2);  ->  size 2
#     Map compares keys by IDENTITY (SameValueZero), never structurally. Lesson 6
#     is that fact plus the canonical-key-function workaround.
#
# ---------------------------------------------------------------------------
# WHAT THE ENVIRONMENT PROVIDES, checked rather than assumed:
#
#   Map / Set, with constructor entries              lib.es2024      ✅ runs
#   Set algebra — union, intersection, difference,
#     symmetricDifference, isSubsetOf, isSupersetOf,
#     isDisjointFrom                                 lib.esnext.collection ✅ runs
#   Object.groupBy / Map.groupBy                     lib.es2024      ✅ runs
#   WeakMap / WeakSet                                lib.es2024      ✅ runs
#
# Two WeakMap facts are shipped as `diagnose` exercises because the compiler's
# message for each is genuinely instructive: a WeakMap has no `.size`
# (**TS2339**), and a primitive key does not satisfy its constraint
# (**TS2344: Type 'string' does not satisfy the constraint 'WeakKey'**).
#
# ---------------------------------------------------------------------------
# DETERMINISM. A `Map`'s iteration order IS specified — insertion order — so
# printing one directly is deterministic here, unlike a Java `HashMap` (which is
# why the Java course forbids it). That makes it tempting to print a Map straight
# out. The week teaches the distinction instead: insertion order is *guaranteed*,
# but it is rarely the order a REPORT wants, so every summary in this week sorts
# its keys and says why. Lesson 3's frequency table sorts by count and then
# alphabetically, which is both deterministic and semantic.
# ---------------------------------------------------------------------------

# --- Week 19 --------------------------------------------------------------
_WEEKS.append(_week(
    19, 5, _M5,
    "Maps & Sets",
    "The two structures you have been living without: a keyed lookup that does not lie to you, and a collection that cannot hold a duplicate.",
    """
Every lookup you have written so far has been an object, a `Record` or a scan
through an array. This week replaces all three, and the argument is not "Map is
newer" — it is that an object used as a dictionary is subtly wrong in four ways.

## What an object cannot do

```ts
const o: Record<string, number> = {};
o["10"] = 1; o["2"] = 2; o["b"] = 3; o["a"] = 4;
Object.keys(o);                  // ["2", "10", "b", "a"]   ← reordered!
```

An object sorts integer-like keys numerically and puts them first. A `Map` keeps
**insertion order**, always.

```ts
const o: Record<string, number> = {};
"toString" in o;                  // true. On an empty object.
```

Keys you never set are already there, inherited from the prototype. A `Map` starts
genuinely empty.

And two more: an object's keys can only be **strings** (a number key becomes a
string, and an object key becomes `"[object Object]"`), and there is no `.size` —
you have to build an array of keys just to count them.

`Map` fixes all four. Use an object when the shape is **known and fixed** — a
config, a record with named fields. Use a `Map` when the keys are **data**.

## And `Set`

A collection with no duplicates and O(1) membership. It replaces the
`array.includes()` in a loop that you have written a dozen times — which is O(n)
per check and therefore O(n²) overall.

```ts
const seen = new Set<string>();
if (!seen.has(word)) { seen.add(word); }
[...new Set(words)];              // de-duplicated, in first-seen order
```

## The rule that does not change

`map.get(k)` is **`V | undefined`**, because the key might not be there. Every read
takes a `??` or a guard — the same discipline as an index access, for the same
reason.

⏱️ Budget about **eight hours**.
""",
    objectives=[
        "Name four things an object used as a dictionary gets wrong",
        "Say why `\"toString\" in {}` is true, and what to use instead",
        "Use `Map` — set, get, has, delete, size, clear — and handle what `get` returns",
        "Iterate a Map's entries, keys and values, and say what order they come in",
        "Count frequencies with a Map, and produce a report whose order is semantic",
        "Use `Set` for membership and de-duplication, and say what it replaces",
        "Combine sets with union, intersection, difference and the subset predicates",
        "Say what an object reorders and a Map does not, and demonstrate it",
        "Explain why two identical-looking objects are two different Map keys",
        "Write a canonical key function when you want structural keying",
        "Say what a WeakMap is for, and two things it deliberately does not have",
        "Group a collection with `Map.groupBy`, and handle the group that might not exist",
    ],
    why="A hash map is the single most useful data structure there is, and 'use a map' is the answer to a startling share of interview problems — it is what turns an O(n²) scan into an O(n) pass. The other half of this week is knowing when an object is still the right answer, which is a judgement most codebases get wrong in one direction or the other.",
    est_minutes=480,
    glossary=[
        _gloss("Map", "A keyed collection. Any key type, insertion-ordered, with a real size."),
        _gloss("Set", "A collection with no duplicates and O(1) membership."),
        _gloss("set(k, v)", "Adds or replaces, and returns the Map — so calls chain."),
        _gloss("get(k)", "The value, or `undefined`. ALWAYS a union, because the key may be absent."),
        _gloss("has(k)", "Membership, without producing a value. The way to tell 'absent' from 'present and undefined'."),
        _gloss("delete(k)", "Removes it; returns whether it was there."),
        _gloss("size", "A property on Map and Set. An object has no equivalent."),
        _gloss("entries / keys / values", "Iterators, all in insertion order."),
        _gloss("insertion order", "Map and Set iterate in the order things were added. Specified, not incidental."),
        _gloss("integer-like key", "\"2\", \"10\" — an object hoists these to the front, in numeric order."),
        _gloss("prototype key", "`toString`, `constructor`, `__proto__` — present on every object literal."),
        _gloss("Object.hasOwn", "The safe membership test for an object: own keys only, no prototype."),
        _gloss("SameValueZero", "How Map and Set compare keys: like `===`, except `NaN` equals itself."),
        _gloss("identity keying", "Two structurally identical objects are two different keys."),
        _gloss("canonical key", "A string built from an object's fields, so structural keying works."),
        _gloss("frequency table", "Key → count. The canonical Map use, and half of the easy interview problems."),
        _gloss("de-duplication", "`[...new Set(xs)]` — unique, in first-seen order."),
        _gloss("union / intersection / difference", "Set algebra, as methods, returning new Sets."),
        _gloss("isSubsetOf / isSupersetOf / isDisjointFrom", "Set predicates, returning booleans."),
        _gloss("WeakMap", "Object keys only, no iteration, no size — for metadata that must not keep a key alive."),
        _gloss("WeakKey", "The constraint a WeakMap key must satisfy. A string does not (TS2344)."),
        _gloss("Map.groupBy", "Groups an iterable by a key function, into a Map of arrays."),
    ],
    cheatsheet="""
```ts
// ---- why not an object -------------------------------------------------
const o: Record<string, number> = {};
o["10"] = 1; o["2"] = 2; o["b"] = 3;
Object.keys(o);              // ["2","10","b"]   ← integer-like first, sorted
"toString" in o;             // true, on an EMPTY object (prototype)
Object.hasOwn(o, "toString") // false            ← the safe test
// no .size, and every key is a string

// ---- Map ----------------------------------------------------------------
const m = new Map<string, number>([["food", 325], ["home", 90000]]);
m.set("travel", 150);              // returns the Map, so .set().set() chains
m.get("food");                      // 325
m.get("nope");                      // undefined  ← the type is number | undefined
(m.get("nope") ?? 0) + 1;           // the read you will write a thousand times
m.has("food");                      // true — and the only way to tell absent
                                    //        from present-and-undefined
m.delete("food");                   // true if it was there
m.size;                             // 2
for (const [k, v] of m) { … }       // insertion order, guaranteed
[...m.keys()]; [...m.values()]; [...m.entries()];

// ---- the frequency table ------------------------------------------------
const counts = new Map<string, number>();
for (const w of words) {
  counts.set(w, (counts.get(w) ?? 0) + 1);
}
// insertion order is guaranteed but rarely what a REPORT wants:
const rows = [...counts.entries()]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));   // count desc, then A-Z

// ---- Set ----------------------------------------------------------------
const s = new Set<string>(["a", "b", "a"]);    // size 2
s.add("c"); s.has("a"); s.delete("b"); s.size;
[...new Set(words)];                            // unique, first-seen order
// replaces `if (!out.includes(w))` — which is O(n) per check, O(n²) overall

// ---- set algebra (ES2025) ----------------------------------------------
a.union(b); a.intersection(b); a.difference(b); a.symmetricDifference(b);
a.isSubsetOf(b); a.isSupersetOf(b); a.isDisjointFrom(b);

// ---- keys are compared by IDENTITY -------------------------------------
m.set({ name: "food" }, 1);
m.set({ name: "food" }, 2);        // size 2 — two different objects
const keyOf = (p: Point): string => `${p.x},${p.y}`;    // canonical key
seen.add(keyOf(p));                                      // …now it is structural

// ---- WeakMap: metadata that does not keep its key alive ---------------
const meta = new WeakMap<Row, string>();   // object keys ONLY
meta.set(row, "seen");
meta.size;                                  // ❌ TS2339 — there is no size
new WeakMap<string, number>();              // ❌ TS2344 — string is not a WeakKey

// ---- grouping (ES2024) -------------------------------------------------
const byFirst = Map.groupBy(words, (w) => w.charAt(0));   // Map<string, string[]>
(byFirst.get("a") ?? []).join(" ");
```
""",
    self_check=[
        "Can you name four things an object used as a dictionary gets wrong?",
        "Can you say what `Object.keys` does to the keys \"10\" and \"2\"?",
        "Can you say why `\"toString\" in {}` is true, and what to write instead?",
        "Can you say what `map.get(k)` returns and why it is a union?",
        "Can you say when `has` tells you something `get` cannot?",
        "Can you write a frequency table from memory?",
        "Can you say what order a Map iterates in, and why a report usually sorts anyway?",
        "Can you de-duplicate an array in one expression?",
        "Can you say what a Set replaces, and what that replacement costs in the old version?",
        "Can you say what `a.difference(b)` contains?",
        "Can you say how many entries `m.set({x:1}, 1).set({x:1}, 2)` leaves in the Map?",
        "Can you write a canonical key function, and say what it buys?",
        "Can you say two things a WeakMap does not have, and why?",
    ],
    review=[
        _q("`Object.keys` on an object with keys \"10\", \"2\", \"b\" gives…",
           ["[\"10\",\"2\",\"b\"]", "[\"2\",\"10\",\"b\"] — integer-like keys first, sorted",
            "[\"b\",\"2\",\"10\"]", "an error"], 1,
           "The most convincing single argument for Map."),
        _q("A Map iterates in…",
           ["sorted order", "insertion order, guaranteed", "random order", "reverse order"], 1,
           "Specified, not incidental."),
        _q("`\"toString\" in {}` is…",
           ["false", "true — it comes from the prototype", "an error", "undefined"], 1,
           "Which makes `in` an unsafe membership test on an object."),
        _q("The safe membership test for an object is…",
           ["in", "Object.hasOwn", "keys().includes", "getOwnPropertyNames"], 1,
           "Own keys only."),
        _q("`map.get(k)` has type…",
           ["V", "V | undefined", "unknown", "never"], 1,
           "The key might not be there."),
        _q("`has` tells you something `get` cannot, namely…",
           ["the size", "absent versus present-and-undefined", "the order", "the type"], 1,
           "Which matters whenever undefined is a legal value."),
        _q("An object's keys can be…",
           ["anything", "strings (and symbols) only", "numbers only", "objects"], 1,
           "A Map's can be any value at all."),
        _q("`counts.set(w, (counts.get(w) ?? 0) + 1)` is…",
           ["a bug", "the frequency-table idiom", "O(n)", "a type error"], 1,
           "The fallback handles the first sighting."),
        _q("`[...new Set(words)]` gives…",
           ["a sorted array", "the unique words in first-seen order", "a Map", "a Set"], 1,
           "De-duplication in one expression."),
        _q("`if (!out.includes(w))` inside a loop is…",
           ["O(1)", "O(n) per check, so O(n²) overall — what a Set replaces", "sorted",
            "a Set"], 1,
           "The commonest accidental quadratic after `shift`."),
        _q("`a.difference(b)` contains…",
           ["everything in both", "the members of a that are not in b", "the members of b",
            "nothing"], 1,
           "And `symmetricDifference` is the members of exactly one."),
        _q("`m.set({x:1}, 1).set({x:1}, 2).size` is…",
           ["1", "2 — the keys are different objects", "0", "an error"], 1,
           "Keys are compared by identity, never structurally."),
        _q("To key by an object's CONTENTS you…",
           ["use ===", "build a canonical string key from its fields", "use a WeakMap",
            "cannot"], 1,
           "Which is what makes grid coordinates work as Set members."),
        _q("A WeakMap's keys must be…",
           ["strings", "objects — a string gives TS2344", "numbers", "anything"], 1,
           "They have to be things that can be garbage collected."),
        _q("`weakMap.size` is…",
           ["0", "TS2339 — there is no size", "the count", "undefined"], 1,
           "It cannot report a count it does not track."),
        _q("`Map.groupBy(xs, f)` returns…",
           ["an object", "a Map from key to an array of members", "an array", "a Set"], 1,
           "And `Object.groupBy` returns the object version."),
    ],
    milestone="Budget Buddy gets an index. Entries go into a `Map` keyed by tag and a `Set` of descriptions already seen, so a duplicate is rejected in O(1) rather than by scanning, and the per-tag report is built from the Map rather than by filtering the whole ledger once per tag. It is the first week where the *shape* of the data, rather than the code around it, is what makes the program fast.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w19-why", "Why not an object",
            "Four things a `Record` used as a dictionary gets wrong.",
            """
You have been using objects as lookups since week 7, and `Record<string, T>` since
week 10. For a **known, fixed** set of fields that is exactly right. For keys that
are **data** it is wrong in four ways, and none of them is obvious.

## 1. Integer-like keys are reordered

```ts
const o: Record<string, number> = {};
o["10"] = 1;
o["2"] = 2;
o["b"] = 3;
o["a"] = 4;
console.log(Object.keys(o).join(","));       // 2,10,b,a
```

Not the order you inserted them. An object's own keys come out as: **integer-like
keys first, in ascending numeric order**, then string keys in insertion order. So
`"10"` moves behind `"2"`, and no amount of care at the insertion site changes it.

A `Map` gives you `10,2,b,a` — what you put in, in the order you put it in.

## 2. Keys you never set are already there

```ts
const o: Record<string, number> = {};
console.log("toString" in o);                 // true
console.log(Object.keys(o).length);           // 0
```

Both lines are correct. `in` searches the **prototype chain**, and every object
literal inherits `toString`, `constructor`, `valueOf` and friends. So `in` is not a
membership test for a dictionary, and a user-supplied key called `constructor` will
sail through a validation check that uses it.

The safe test is `Object.hasOwn(o, key)` — own properties only. A `Map` needs
neither caveat: `new Map().has("toString")` is `false`.

## 3. The keys can only be strings

```ts
const o: Record<string, number> = {};
const tag = { name: "food" };
// o[tag] = 1;      // the key becomes the string "[object Object]"
```

Numbers are silently converted (`o[1]` and `o["1"]` are the same key), and objects
all collapse to one key. A `Map` accepts **any** value as a key, which lesson 6 is
about.

## 4. There is no size

```ts
Object.keys(o).length;      // build a whole array, to count
m.size;                     // a property
```

## So when is an object right?

When the keys are **part of your program**, not part of your data:

```ts
interface Config { readonly strict: boolean; readonly retries: number; }   // ✅ object
const byTag = new Map<string, Entry[]>();                                   // ✅ Map
```

The test: *could a user invent a new key?* If yes, it is data, and it belongs in a
Map. A `Record<string, T>` in that position is a dictionary wearing a type
annotation.

Two honest caveats for the other direction: an object serialises to JSON directly
and a Map does not (`JSON.stringify(new Map())` is `{}`), and object literals are
more compact to write. Neither is a reason to key user data by string
concatenation.

> ⚠️ **Common mistakes:** using `in` as a membership test on a dictionary;
> assuming `Object.keys` preserves insertion order; and reaching for a Map for a
> fixed set of named fields, where an interface says more.
""",
            warmup=[
                _q("`Object.keys` puts integer-like keys…",
                   ["last", "first, in ascending numeric order", "in insertion order",
                    "in reverse"], 1,
                   "Which silently reorders your dictionary."),
                _q("`\"toString\" in {}` is…",
                   ["false", "true", "an error", "undefined"], 1,
                   "The prototype chain."),
                _q("An object's keys may be…",
                   ["any value", "strings and symbols only", "numbers", "objects"], 1,
                   "Everything else is converted."),
                _q("An object is still the right choice when…",
                   ["always", "the keys are a fixed part of your program, not data",
                    "never", "the keys are numbers"], 1,
                   "Could a user invent a new key? Then it is data."),
            ],
            exercises=[
                _ex("tscourse-w19-why-1", "Watch the keys get reordered",
                    "Insert an integer-like key after a string one, then print the object's key order.",
                    'const o: Record<string, number> = {};\n'
                    'o["b"] = 1;\n'
                    'o["10"] = 2;\n'
                    'o["2"] = 3;\n'
                    'console.log(Object.keys(o).join(","));\n',
                    'o["2"] = 3;', [("", "2,10,b")],
                    hints=["Both numeric keys will jump in front of `b`, in numeric order.",
                           'Write o["2"] = 3;'],
                    difficulty="Easy"),
                _ex("tscourse-w19-why-2", "…and a Map that does not",
                    "Insert the same three keys into a Map and print its order.",
                    'const m = new Map<string, number>();\n'
                    'm.set("b", 1);\n'
                    'm.set("10", 2);\n'
                    'm.set("2", 3);\n'
                    'console.log([...m.keys()].join(","));\n',
                    'const m = new Map<string, number>();', [("", "b,10,2")],
                    hints=["Insertion order, guaranteed.",
                           "Write const m = new Map<string, number>();"],
                    difficulty="Easy"),
                _ex("tscourse-w19-why-3", "The key that was always there",
                    "Compare `in` against a Map's `has` for a key nobody set.",
                    'const o: Record<string, number> = {};\n'
                    'const m = new Map<string, number>();\n'
                    'console.log(`${"toString" in o} ${m.has("toString")}`);\n',
                    'console.log(`${"toString" in o} ${m.has("toString")}`);',
                    [("", "true false")],
                    hints=["`in` walks the prototype chain; a Map has no prototype keys.",
                           'Write console.log(`${"toString" in o} ${m.has("toString")}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-why-4", "The safe membership test",
                    "Use the test that only considers keys the object actually owns.",
                    'const o: Record<string, number> = { food: 325 };\n'
                    'console.log(`${Object.hasOwn(o, "toString")} ${Object.hasOwn(o, "food")}`);\n',
                    'console.log(`${Object.hasOwn(o, "toString")} ${Object.hasOwn(o, "food")}`);',
                    [("", "false true")],
                    hints=["One static method, taking the object and the key.",
                           'Write console.log(`${Object.hasOwn(o, "toString")} ${Object.hasOwn(o, "food")}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-why-5", "Size, without building an array",
                    "Report both counts — the object's the long way, the Map's the short way.",
                    'const o: Record<string, number> = { a: 1, b: 2 };\n'
                    'const m = new Map<string, number>([["a", 1], ["b", 2]]);\n'
                    'console.log(`${Object.keys(o).length} ${m.size}`);\n',
                    'console.log(`${Object.keys(o).length} ${m.size}`);', [("", "2 2")],
                    hints=["One builds an array to count; the other is a property.",
                           'Write console.log(`${Object.keys(o).length} ${m.size}`);'],
                    difficulty="Easy"),
                _fix("tscourse-w19-why-fix1", "Fix the validator `in` let through",
                     "This is meant to reject a tag that is not in the allowed table, and `constructor` gets through — because `in` finds it on the prototype. Test only the keys the table actually owns.",
                     _LINE +
                     'const ALLOWED: Record<string, boolean> = { food: true, home: true };\n'
                     'function allowed(tag: string): boolean {\n'
                     '  return tag in ALLOWED;\n}\n'
                     'console.log(allowed(line));\n',
                     _LINE +
                     'const ALLOWED: Record<string, boolean> = { food: true, home: true };\n'
                     'function allowed(tag: string): boolean {\n'
                     '  return Object.hasOwn(ALLOWED, tag);\n}\n'
                     'console.log(allowed(line));\n',
                     [("constructor", "false"), ("food", "true"), ("toString", "false"),
                      ("travel", "false")],
                     hints=["`in` searches the prototype chain, and every object literal has a `constructor`.",
                            "You want the keys this object owns, not the ones it inherits.",
                            "Write return Object.hasOwn(ALLOWED, tag);"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`JSON.stringify(new Map([[\"a\",1]]))` gives…",
                   ["{\"a\":1}", "{} — a Map does not serialise directly", "an array", "an error"], 1,
                   "One of the two honest arguments for an object."),
                _q("A `Record<string, T>` holding user-supplied keys is…",
                   ["ideal", "a dictionary wearing a type annotation", "faster", "safer"], 1,
                   "The annotation does not fix any of the four problems."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w19-map", "`Map`, properly",
            "Six methods, and the union `get` always returns.",
            """
```ts
const m = new Map<string, number>([
  ["food", 325],
  ["home", 90000],
]);
```

The constructor takes an iterable of `[key, value]` pairs — which is also what
`entries()` produces, so `new Map(other.entries())` clones one.

## The API

```ts
m.set("travel", 150);        // adds or replaces; RETURNS THE MAP, so it chains
m.get("food");                // 325
m.get("nope");                // undefined
m.has("food");                // true
m.delete("food");             // true — and false if it was not there
m.size;                       // 2
m.clear();                    // empties it
```

`set` returning the map is why you see this:

```ts
const m = new Map<string, number>().set("a", 1).set("b", 2);
```

## `get` is `V | undefined`, always

```ts
const n = m.get("nope");      // number | undefined
m.get("nope").toFixed(1);
// ❌ TS2532: Object is possibly 'undefined'.
```

Not a flag — a fact. The key might not be there, so every read is handled the same
way an index access is (week 16, lesson 7):

```ts
const cents = m.get(tag) ?? 0;                     // a default
const found = m.get(tag);
if (found !== undefined) { … }                     // a guard
```

## When `has` says something `get` cannot

If `undefined` is a legal *value* in your map, `get` cannot distinguish "absent"
from "present, holding undefined":

```ts
const flags = new Map<string, boolean | undefined>();
flags.set("beta", undefined);
flags.get("beta");            // undefined
flags.has("beta");            // true      ← the difference
```

Most maps never need this. The ones that do are exactly the ones where getting it
wrong is subtle, so it is worth knowing which tool answers which question.

## Iterating

```ts
for (const [key, value] of m) { … }        // entries, destructured
for (const key of m.keys()) { … }
for (const value of m.values()) { … }
[...m.entries()];                           // an array of pairs, for sorting
```

Iterating a Map directly gives entries, so the `[key, value]` destructure is the
usual form. All three iterate in **insertion order**, and a `set` on an existing
key updates the value **without moving it**.

## Typing

`Map<K, V>` is generic, and both arguments matter:

```ts
const byTag = new Map<string, readonly Entry[]>();
const seenAt = new Map<number, string>();               // numeric keys, for real
const scores = new Map<string, Map<string, number>>();  // nested is fine
```

> ⚠️ **Common mistakes:** forgetting `get` may be undefined; using `get` where
> `has` was the question; and expecting `set` to return the value.
""",
            warmup=[
                _q("`m.set(k, v)` returns…",
                   ["the value", "the Map, so calls chain", "void", "a boolean"], 1,
                   "Which is why `.set().set()` works."),
                _q("`m.get(k)` where k is absent gives…",
                   ["an error", "undefined", "null", "0"], 1,
                   "Hence the union."),
                _q("`m.delete(k)` returns…",
                   ["the value", "whether the key was there", "the Map", "void"], 1,
                   "Useful more often than you would think."),
                _q("Updating an existing key's value…",
                   ["moves it to the end", "leaves its position alone", "deletes it",
                    "reorders the Map"], 1,
                   "Insertion order means FIRST insertion."),
            ],
            exercises=[
                _ex("tscourse-w19-m-1", "Build one from pairs",
                    "Seed the Map from an array of key/value pairs.",
                    'const m = new Map<string, number>([["food", 325], ["home", 90000]]);\n'
                    'console.log(`${m.size} ${m.get("home") ?? 0}`);\n',
                    'const m = new Map<string, number>([["food", 325], ["home", 90000]]);',
                    [("", "2 90000")],
                    hints=["The constructor takes an iterable of two-element arrays.",
                           'Write const m = new Map<string, number>([["food", 325], ["home", 90000]]);'],
                    difficulty="Easy"),
                _ex("tscourse-w19-m-2", "Read with a default",
                    "Handle the key that is not there, so the arithmetic below is on a number.",
                    'const m = new Map<string, number>([["food", 325]]);\n'
                    'const home = m.get("home") ?? 0;\n'
                    'console.log((home / 100).toFixed(2));\n',
                    'const home = m.get("home") ?? 0;', [("", "0.00")],
                    hints=["`get` may hand back nothing; supply the fallback at the point of reading.",
                           'Write const home = m.get("home") ?? 0;'],
                    difficulty="Easy"),
                _ex("tscourse-w19-m-3", "Chain the sets",
                    "Build the whole map in one expression, using what `set` returns.",
                    'const m = new Map<string, number>().set("a", 1).set("b", 2).set("c", 3);\n'
                    'console.log(`${m.size} ${[...m.keys()].join("")}`);\n',
                    'const m = new Map<string, number>().set("a", 1).set("b", 2).set("c", 3);',
                    [("", "3 abc")],
                    hints=["Each `set` hands the Map back, so the next one can be called on it.",
                           'Write const m = new Map<string, number>().set("a", 1).set("b", 2).set("c", 3);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-m-4", "Iterate the entries",
                    "Destructure each entry as you loop over the Map.",
                    'const m = new Map<string, number>([["food", 325], ["home", 90000]]);\n'
                    'for (const [tag, cents] of m) {\n'
                    '  console.log(`${tag} $${(cents / 100).toFixed(2)}`);\n}\n',
                    'for (const [tag, cents] of m) {',
                    [("", "food $3.25\nhome $900.00")],
                    hints=["Iterating a Map yields entries, so destructure the pair in the loop head.",
                           "Write for (const [tag, cents] of m) {"],
                    difficulty="Medium"),
                _ex("tscourse-w19-m-5", "Absent, or present and undefined",
                    "Use the method that can tell those two apart.",
                    'const flags = new Map<string, boolean | undefined>();\n'
                    'flags.set("beta", undefined);\n'
                    'console.log(`${flags.get("beta")} ${flags.has("beta")} ${flags.has("alpha")}`);\n',
                    'console.log(`${flags.get("beta")} ${flags.has("beta")} ${flags.has("alpha")}`);',
                    [("", "undefined true false")],
                    hints=["`get` gives undefined either way; only one method answers the membership question.",
                           'Write console.log(`${flags.get("beta")} ${flags.has("beta")} ${flags.has("alpha")}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-m-6", "Delete, and say whether it was there",
                    "Report the result of each delete.",
                    'const m = new Map<string, number>([["a", 1], ["b", 2]]);\n'
                    'console.log(`${m.delete("a")} ${m.delete("zz")} ${m.size}`);\n',
                    'console.log(`${m.delete("a")} ${m.delete("zz")} ${m.size}`);',
                    [("", "true false 1")],
                    hints=["Delete returns a boolean, not the value.",
                           'Write console.log(`${m.delete("a")} ${m.delete("zz")} ${m.size}`);'],
                    difficulty="Easy"),
                _ex("tscourse-w19-m-7", "A Map of arrays",
                    "Type the values as arrays of entries, appending to the group that is already there.",
                    _WORDS +
                    'const byFirst = new Map<string, string[]>();\n'
                    'for (const w of words) {\n'
                    '  const key = w.charAt(0);\n'
                    '  const group = byFirst.get(key) ?? [];\n'
                    '  group.push(w);\n'
                    '  byFirst.set(key, group);\n}\n'
                    'for (const key of [...byFirst.keys()].sort()) {\n'
                    '  console.log(`${key}: ${(byFirst.get(key) ?? []).join(" ")}`);\n}\n',
                    '  const group = byFirst.get(key) ?? [];',
                    [("ant bee auk", "a: ant auk\nb: bee"), ("solo", "s: solo")],
                    hints=["Either the group exists, or this is the first member of it.",
                           "Write const group = byFirst.get(key) ?? [];"],
                    difficulty="Medium"),
                _predict("tscourse-w19-m-p1", "What `get` gives you",
                         'const m = new Map<string, number>([["food", 325]]);\n'
                         'const got = m.get("food");\n',
                         "got", "number | undefined",
                         why="The key is present *today*; the method's signature cannot know that.",
                         hints=["The value type, plus the case where the key is missing.",
                                "Write number | undefined."]),
                _diagnose("tscourse-w19-m-d1", "The lookup that might miss",
                          "TS2532: Object is possibly 'undefined'.",
                          'const m = new Map<string, number>([["a", 1]]);\n'
                          'console.log(m.get("a").toFixed(1));\n',
                          'const m = new Map<string, number>([["a", 1]]);\n'
                          'console.log((m.get("a") ?? 0).toFixed(1));\n',
                          [("", "1.0")],
                          hints=["A Map lookup is an absence like any other — the same rule as an index access.",
                                 "Supply a fallback before calling a method on the result.",
                                 'Write (m.get("a") ?? 0).toFixed(1).'],
                          difficulty="Easy"),
            ],
            quiz=[
                _q("`new Map(other.entries())`…",
                   ["is an error", "clones the map", "empties it", "reverses it"], 1,
                   "Entries are exactly what the constructor wants."),
                _q("All three of keys(), values() and entries() iterate in…",
                   ["sorted order", "insertion order", "random order", "reverse insertion order"], 1,
                   "Consistently."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w19-freq", "Counting things",
            "The one Map idiom you will write most.",
            """
```ts
const counts = new Map<string, number>();
for (const word of words) {
  counts.set(word, (counts.get(word) ?? 0) + 1);
}
```

That is the whole pattern, and the `?? 0` is the entire subtlety: the first time a
word is seen, `get` returns `undefined`, and the fallback makes it a `0` to add
to.

It replaces the O(n²) version you would otherwise write — a scan of an array of
`{word, count}` objects for every single word — with one O(n) pass.

## Turning a count into an answer

Counting is usually step one. The questions that follow are all the same shape:

```ts
// the most common word
let best = "";
let bestCount = 0;
for (const [word, n] of counts) {
  if (n > bestCount) { best = word; bestCount = n; }
}

// how many appear exactly once
let once = 0;
for (const n of counts.values()) { if (n === 1) { once = once + 1; } }

// are these two strings anagrams? — count one up, count the other down
```

## Insertion order is guaranteed; sort anyway

A Map iterates in insertion order, so printing one directly *is* deterministic.
But insertion order is "whatever the input happened to be", which is almost never
what a **report** should be in:

```ts
const rows = [...counts.entries()]
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
for (const [word, n] of rows) { console.log(`${word} ${n}`); }
```

Two things in that comparator worth copying:

* **`b[1] - a[1]`** sorts by count, descending.
* **`|| a[0].localeCompare(b[0])`** breaks ties alphabetically. Without it, two
  words with the same count come out in input order — which is stable, but is not a
  *decision*, and it makes a diff between two runs of a report meaningless.

A tie-break is what turns "deterministic" into "explainable", and the two are not
the same thing.

## Counting into groups

The same shape, with an array as the value:

```ts
const group = byTag.get(tag) ?? [];
group.push(entry);
byTag.set(tag, group);
```

Read-or-default, mutate, put back. Lesson 8 shows the standard-library shortcut for
exactly this.

> ⚠️ **Common mistakes:** `counts.get(w) + 1` without the fallback (which is
> `NaN`); reporting in insertion order and calling it sorted; and forgetting the
> tie-break, so a report's order depends on its input's order.
""",
            warmup=[
                _q("`counts.get(w) + 1` on a first sighting gives…",
                   ["1", "NaN", "0", "an error"], 1,
                   "undefined + 1. Hence the `?? 0`."),
                _q("The frequency table is O(n) where the array-scan version is…",
                   ["O(n)", "O(n²)", "O(log n)", "O(1)"], 1,
                   "One scan per element."),
                _q("`b[1] - a[1]` sorts by…",
                   ["key ascending", "count descending", "count ascending", "insertion"], 1,
                   "Bigger first."),
                _q("A tie-break makes a report…",
                   ["faster", "explainable rather than merely deterministic", "sorted",
                    "shorter"], 1,
                   "Input order is stable but is not a decision."),
            ],
            exercises=[
                _ex("tscourse-w19-f-1", "Count the words",
                    "Increment the count, handling the first sighting.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'for (const w of words) {\n'
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                    'for (const key of [...counts.keys()].sort()) {\n'
                    '  console.log(`${key} ${counts.get(key) ?? 0}`);\n}\n',
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);',
                    [("b a b c a b", "a 2\nb 3\nc 1"), ("solo", "solo 1")],
                    hints=["Read with a default, add one, put it back.",
                           "Write counts.set(w, (counts.get(w) ?? 0) + 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-f-2", "Sort by count, then alphabetically",
                    "Write the comparator so the report is ordered by count descending, with ties broken A-Z.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'for (const w of words) {\n'
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                    'const rows = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));\n'
                    'for (const [w, n] of rows) {\n'
                    '  console.log(`${w} ${n}`);\n}\n',
                    'const rows = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));',
                    [("b a b c a b", "b 3\na 2\nc 1"), ("x y", "x 1\ny 1")],
                    hints=["Count descending first, then the key as a tie-break.",
                           "Write const rows = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));"],
                    difficulty="Medium"),
                _ex("tscourse-w19-f-3", "The most common one",
                    "Track the best as you walk the entries.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'for (const w of words) {\n'
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                    'let best = "";\n'
                    'let bestCount = 0;\n'
                    'for (const key of [...counts.keys()].sort()) {\n'
                    '  const n = counts.get(key) ?? 0;\n'
                    '  if (n > bestCount) {\n'
                    '    best = key;\n    bestCount = n;\n  }\n}\n'
                    'console.log(`${best} ${bestCount}`);\n',
                    '  if (n > bestCount) {',
                    [("b a b c a b", "b 3"), ("x y", "x 1")],
                    hints=["A strict `>` walking sorted keys means the alphabetically first winner keeps a tie.",
                           "Write if (n > bestCount) {"],
                    difficulty="Medium"),
                _ex("tscourse-w19-f-4", "How many appeared exactly once",
                    "Count the values that are 1.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'for (const w of words) {\n'
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                    'let once = 0;\n'
                    'for (const n of counts.values()) {\n'
                    '  if (n === 1) {\n'
                    '    once = once + 1;\n  }\n}\n'
                    'console.log(once);\n',
                    'for (const n of counts.values()) {',
                    [("b a b c a b", "1"), ("x y z", "3"), ("a a", "0")],
                    hints=["Only the counts matter here, not the keys.",
                           "Write for (const n of counts.values()) {"],
                    difficulty="Easy"),
                _ex("tscourse-w19-f-5", "Anagrams, by counting down",
                    "Count the first word up and the second down; anything left over means they differ.",
                    _WORDS +
                    'function anagrams(a: string, b: string): boolean {\n'
                    '  if (a.length !== b.length) {\n'
                    '    return false;\n  }\n'
                    '  const counts = new Map<string, number>();\n'
                    '  for (const ch of a) {\n'
                    '    counts.set(ch, (counts.get(ch) ?? 0) + 1);\n  }\n'
                    '  for (const ch of b) {\n'
                    '    const n = counts.get(ch) ?? 0;\n'
                    '    if (n === 0) {\n'
                    '      return false;\n    }\n'
                    '    counts.set(ch, n - 1);\n  }\n'
                    '  return true;\n}\n'
                    'console.log(anagrams(words[0] ?? "", words[1] ?? ""));\n',
                    '    counts.set(ch, n - 1);',
                    [("listen silent", "true"), ("hello world", "false"), ("ab ba", "true")],
                    hints=["Having checked the count is not already zero, put back one fewer.",
                           "Write counts.set(ch, n - 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-f-6", "First duplicate",
                    "Report the first word that has been seen before, using a count map.",
                    _WORDS +
                    'const seen = new Map<string, number>();\n'
                    'let firstDup = "none";\n'
                    'for (const w of words) {\n'
                    '  const n = seen.get(w) ?? 0;\n'
                    '  if (n > 0 && firstDup === "none") {\n'
                    '    firstDup = w;\n  }\n'
                    '  seen.set(w, n + 1);\n}\n'
                    'console.log(firstDup);\n',
                    '  if (n > 0 && firstDup === "none") {',
                    [("a b a c b", "a"), ("a b c", "none")],
                    hints=["It is a duplicate if the count is already above zero, and only the first one counts.",
                           'Write if (n > 0 && firstDup === "none") {'],
                    difficulty="Medium"),
                _fix("tscourse-w19-f-fix1", "Fix the count that came out NaN",
                     "Every count prints as `NaN`: on a word's first sighting `get` returns `undefined`, and `undefined + 1` is not a number. Nothing here is a type error — `number | undefined` plus a number is rejected, so this was written as a `!`, which is worse.",
                     _WORDS +
                     'const counts = new Map<string, number>();\n'
                     'for (const w of words) {\n'
                     '  counts.set(w, counts.get(w)! + 1);\n}\n'
                     'for (const key of [...counts.keys()].sort()) {\n'
                     '  console.log(`${key} ${counts.get(key) ?? 0}`);\n}\n',
                     _WORDS +
                     'const counts = new Map<string, number>();\n'
                     'for (const w of words) {\n'
                     '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                     'for (const key of [...counts.keys()].sort()) {\n'
                     '  console.log(`${key} ${counts.get(key) ?? 0}`);\n}\n',
                     [("b a b", "a 1\nb 2"), ("x", "x 1")],
                     hints=["The `!` claims the key is already there, and on the first sighting that is false.",
                            "A first sighting needs a zero to add to, not an assertion.",
                            "Write (counts.get(w) ?? 0) + 1."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Counting one string up and the other down tests…",
                   ["equality", "whether they are anagrams", "length", "sortedness"], 1,
                   "With a length check first."),
                _q("Reporting a frequency table in insertion order is…",
                   ["sorted", "deterministic but arbitrary — it is the input's order",
                    "random", "wrong"], 1,
                   "Sort, with a tie-break."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w19-set", "`Set`, and what it replaces",
            "Membership in O(1), and de-duplication in one expression.",
            """
A `Set` holds each value at most once, and answers "is this in here?" in constant
time.

```ts
const s = new Set<string>(["a", "b", "a"]);
s.size;              // 2 — the duplicate was never added
s.add("c");          // returns the Set, so it chains
s.has("a");          // true
s.delete("b");       // true if it was there
[...s];              // ["a", "c"] — insertion order
```

## What it replaces

```ts
// before
const seen: string[] = [];
for (const w of words) {
  if (!seen.includes(w)) { seen.push(w); }    // includes is O(n)…
}
// after
const seen = new Set<string>(words);          // …and this is O(1) per element
```

`includes` scans. In a loop, that is O(n²) — the same class of accidental
quadratic as week 18's `shift`, and just as invisible. If you find yourself
calling `includes` or `indexOf` inside a loop, a `Set` is almost always the answer.

## De-duplication

```ts
[...new Set(words)];             // unique, in first-seen order
```

One expression, and the order is the order things first appeared — which is usually
what you want, and is worth knowing rather than assuming.

## Set algebra

Modern JavaScript gives the operations names:

```ts
const a = new Set<number>([1, 2, 3]);
const b = new Set<number>([2, 3, 4]);

a.union(b);                  // {1, 2, 3, 4}
a.intersection(b);           // {2, 3}
a.difference(b);             // {1}        — in a, not in b
a.symmetricDifference(b);    // {1, 4}     — in exactly one
a.isSubsetOf(b);             // false
a.isSupersetOf(b);           // false
a.isDisjointFrom(b);         // false
```

The first four return **new Sets** and leave both operands alone; the last three
return booleans. Written by hand, each is a loop and a filter — and "the tags in
this month's ledger that were not in last month's" reads infinitely better as
`thisMonth.difference(lastMonth)`.

## What a Set is not

It is **not sorted** — insertion order, like a Map. It has no indexing, `s[0]` is
meaningless, and there is no `get`: a Set answers membership, not retrieval. If you
need "find me the entry whose id is 7", that is a Map keyed by id.

And like a Map, it compares by **identity** for objects — `new Set([{x:1},{x:1}])`
has two members. Lesson 6.

> ⚠️ **Common mistakes:** expecting a Set to be sorted; `includes` inside a loop
> when a Set was available; and using a Set where you actually needed to get the
> thing back out.
""",
            warmup=[
                _q("`new Set([\"a\",\"b\",\"a\"]).size` is…",
                   ["3", "2", "1", "0"], 1,
                   "The duplicate was never added."),
                _q("`[...new Set(words)]` gives the unique words in…",
                   ["sorted order", "first-seen order", "reverse order", "random order"], 1,
                   "Insertion order, like a Map."),
                _q("`includes` inside a loop is…",
                   ["O(n)", "O(n²) overall — what a Set replaces", "O(1)", "sorted"], 1,
                   "The same class of trap as `shift`."),
                _q("`a.difference(b)` returns…",
                   ["a boolean", "a new Set of a's members that are not in b", "a mutated a",
                    "an array"], 1,
                   "Both operands are left alone."),
            ],
            exercises=[
                _ex("tscourse-w19-s-1", "De-duplicate in one expression",
                    "Turn the words into a Set and spread it back out.",
                    _WORDS +
                    'const unique = [...new Set(words)];\n'
                    'console.log(`${unique.length} ${unique.join(" ")}`);\n',
                    'const unique = [...new Set(words)];',
                    [("b a b c a", "3 b a c"), ("solo", "1 solo")],
                    hints=["Build the Set from the array, then spread it into a new array.",
                           "Write const unique = [...new Set(words)];"],
                    difficulty="Easy"),
                _ex("tscourse-w19-s-2", "Membership in constant time",
                    "Check the Set rather than scanning the array.",
                    _WORDS +
                    'const ALLOWED = new Set<string>(["food", "home", "travel"]);\n'
                    'for (const w of words) {\n'
                    '  console.log(`${w} ${ALLOWED.has(w)}`);\n}\n',
                    'const ALLOWED = new Set<string>(["food", "home", "travel"]);',
                    [("food snacks", "food true\nsnacks false")],
                    hints=["A Set built once, queried many times.",
                           'Write const ALLOWED = new Set<string>(["food", "home", "travel"]);'],
                    difficulty="Easy"),
                _ex("tscourse-w19-s-3", "First repeat, with a Set",
                    "Add each word and report the first one that was already present.",
                    _WORDS +
                    'const seen = new Set<string>();\n'
                    'let firstRepeat = "none";\n'
                    'for (const w of words) {\n'
                    '  if (seen.has(w) && firstRepeat === "none") {\n'
                    '    firstRepeat = w;\n  }\n'
                    '  seen.add(w);\n}\n'
                    'console.log(firstRepeat);\n',
                    '  if (seen.has(w) && firstRepeat === "none") {',
                    [("a b a c", "a"), ("a b c", "none")],
                    hints=["Check before adding, and keep only the first answer.",
                           'Write if (seen.has(w) && firstRepeat === "none") {'],
                    difficulty="Medium"),
                _ex("tscourse-w19-s-4", "In both, in one",
                    "Report the intersection and the symmetric difference of two tag sets.",
                    'const thisMonth = new Set<string>(["food", "home", "travel"]);\n'
                    'const lastMonth = new Set<string>(["home", "travel", "books"]);\n'
                    'console.log([...thisMonth.intersection(lastMonth)].sort().join(","));\n'
                    'console.log([...thisMonth.symmetricDifference(lastMonth)].sort().join(","));\n',
                    'console.log([...thisMonth.intersection(lastMonth)].sort().join(","));',
                    [("", "home,travel\nbooks,food")],
                    hints=["The members of both, then the members of exactly one.",
                           'Write console.log([...thisMonth.intersection(lastMonth)].sort().join(","));'],
                    difficulty="Medium"),
                _ex("tscourse-w19-s-5", "New this month",
                    "Report the tags that appear this month and did not appear last month.",
                    'const thisMonth = new Set<string>(["food", "home", "travel"]);\n'
                    'const lastMonth = new Set<string>(["home", "books"]);\n'
                    'const isNew = thisMonth.difference(lastMonth);\n'
                    'console.log([...isNew].sort().join(","));\n',
                    'const isNew = thisMonth.difference(lastMonth);',
                    [("", "food,travel")],
                    hints=["In this month's set, not in last month's.",
                           "Write const isNew = thisMonth.difference(lastMonth);"],
                    difficulty="Easy"),
                _ex("tscourse-w19-s-6", "Is every tag allowed?",
                    "Use the predicate that answers it in one call.",
                    _WORDS +
                    'const ALLOWED = new Set<string>(["food", "home", "travel"]);\n'
                    'const used = new Set<string>(words);\n'
                    'console.log(used.isSubsetOf(ALLOWED));\n',
                    'console.log(used.isSubsetOf(ALLOWED));',
                    [("food home", "true"), ("food snacks", "false")],
                    hints=["Every member of the used set has to be in the allowed set.",
                           "Write console.log(used.isSubsetOf(ALLOWED));"],
                    difficulty="Medium"),
                # The bug here is a COST, not a wrong answer — so, exactly as week 18
                # did for `shift`, the program counts the comparisons instead of
                # timing anything. The starter's answer is right and its count is
                # not, which is what makes the starter fail deterministically.
                _fix("tscourse-w19-s-fix1", "Fix the quadratic de-duplication",
                     "The de-duplicated list is correct and the way it is built is not: `includes` scans the whole accumulated array for every single word, so this counts 4 comparisons on `b a b c a` where a Set needs none. Replace the mechanism, keep the answer — and get the count to zero.",
                     _WORDS +
                     'let comparisons = 0;\n'
                     'const unique: string[] = [];\n'
                     'for (const w of words) {\n'
                     '  comparisons = comparisons + unique.length;\n'
                     '  if (!unique.includes(w)) {\n'
                     '    unique.push(w);\n  }\n}\n'
                     'console.log(`${unique.join(" ")} comparisons ${comparisons}`);\n',
                     _WORDS +
                     'const comparisons = 0;\n'
                     'const unique = [...new Set(words)];\n'
                     'console.log(`${unique.join(" ")} comparisons ${comparisons}`);\n',
                     [("b a b c a", "b a c comparisons 0"), ("x", "x comparisons 0")],
                     hints=["`includes` is a scan, and it is inside a loop — the counter is measuring exactly that.",
                            "A Set answers membership in constant time, and de-duplicating is what it is FOR.",
                            "The whole loop collapses to `[...new Set(words)]`, which keeps first-seen order — and then nothing is compared at all."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A Set has no `get` because…",
                   ["it is a bug", "it answers membership, not retrieval — a Map is for retrieval",
                    "it is sorted", "of types"], 1,
                   "If you need the thing back, key it in a Map."),
                _q("`new Set([{x:1},{x:1}]).size` is…",
                   ["1", "2 — objects compare by identity", "0", "an error"], 1,
                   "Lesson 6."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w19-order", "Order, and what is actually guaranteed",
            "Three different answers, and only one of them is a decision.",
            """
Three collections, three orders:

| | order |
|---|---|
| **object** | integer-like keys first, ascending; then string keys in insertion order |
| **Map / Set** | insertion order, always |
| **a sorted array of entries** | whatever you asked for |

## The object's rule, demonstrated

```ts
const o: Record<string, number> = {};
o["b"] = 1; o["10"] = 2; o["2"] = 3; o["a"] = 4;
Object.keys(o);        // ["2", "10", "b", "a"]
```

`"2"` and `"10"` are *integer-like*, so they are hoisted to the front and sorted
numerically. `"b"` and `"a"` keep insertion order behind them. This is specified
behaviour, not an implementation quirk — and it is why an object indexed by id
numbers silently renumbers your report.

## Map and Set keep insertion order

```ts
const m = new Map<string, number>();
m.set("b", 1); m.set("10", 2); m.set("2", 3); m.set("a", 4);
[...m.keys()];         // ["b", "10", "2", "a"]
```

Exactly what went in. And note what re-`set`ting does **not** do:

```ts
m.set("b", 99);        // updates the value; "b" stays FIRST
```

Insertion order means *first* insertion. To move a key to the end you have to
`delete` it and set it again — which is, incidentally, how an LRU cache is built.

## Why a report should sort anyway

Insertion order is deterministic, so printing a Map is safe here — unlike a Java
`HashMap`, whose iteration order is genuinely undefined, which is why the Java
course forbids printing one. But "deterministic" is a lower bar than "correct":

```ts
for (const [tag, cents] of byTag) { … }                    // input's order
for (const tag of [...byTag.keys()].sort()) { … }          // alphabetical
[...byTag.entries()].sort((a, b) => b[1] - a[1]);          // biggest first
```

The first one produces a different report for the same ledger in a different order.
It will never *fail*, which is what makes it a bad habit: a report whose order is
an accident of its input cannot be diffed against yesterday's.

**Sort when the order carries meaning, and always break ties.** `sort()` in
JavaScript is stable, so ties keep input order — stable and arbitrary. A tie-break
makes the answer a decision.

## A tiny warning about `sort()`

Default `sort()` compares as **strings**:

```ts
[10, 9, 2].sort();                       // [10, 2, 9]  ← string order
[10, 9, 2].sort((a, b) => a - b);        // [2, 9, 10]
```

Week 6 met this. It bites hardest here, where you are sorting keys that look like
numbers.

> ⚠️ **Common mistakes:** trusting an object to preserve numeric-ish key order;
> assuming re-setting a key moves it; and printing in insertion order in a report
> somebody will compare against another run.
""",
            warmup=[
                _q("An object hoists integer-like keys…",
                   ["to the end", "to the front, in numeric order", "nowhere", "randomly"], 1,
                   "Specified behaviour."),
                _q("`m.set(existingKey, newValue)` moves the key…",
                   ["to the end", "nowhere — insertion order means FIRST insertion", "to the front",
                    "out"], 1,
                   "Delete and re-set to move it."),
                _q("Printing a Map directly is deterministic here because…",
                   ["it is sorted", "its iteration order is specified as insertion order",
                    "of the judge", "it is not"], 1,
                   "Unlike a Java HashMap."),
                _q("`[10, 9, 2].sort()` gives…",
                   ["[2,9,10]", "[10,2,9]", "[9,10,2]", "an error"], 1,
                   "Default sort compares as strings."),
            ],
            exercises=[
                _ex("tscourse-w19-o-1", "The object's reordering, in full",
                    "Insert four keys — two integer-like — and print the resulting key order.",
                    'const o: Record<string, number> = {};\n'
                    'o["b"] = 1;\n'
                    'o["10"] = 2;\n'
                    'o["2"] = 3;\n'
                    'o["a"] = 4;\n'
                    'console.log(Object.keys(o).join(","));\n',
                    'console.log(Object.keys(o).join(","));', [("", "2,10,b,a")],
                    hints=["The two numeric-looking keys come first, in numeric order.",
                           'Write console.log(Object.keys(o).join(","));'],
                    difficulty="Easy"),
                _ex("tscourse-w19-o-2", "The Map's answer to the same input",
                    "Print the Map's key order for exactly the same four keys.",
                    'const m = new Map<string, number>();\n'
                    'm.set("b", 1);\n'
                    'm.set("10", 2);\n'
                    'm.set("2", 3);\n'
                    'm.set("a", 4);\n'
                    'console.log([...m.keys()].join(","));\n',
                    'console.log([...m.keys()].join(","));', [("", "b,10,2,a")],
                    hints=["Whatever went in, in the order it went in.",
                           'Write console.log([...m.keys()].join(","));'],
                    difficulty="Easy"),
                _ex("tscourse-w19-o-3", "Re-setting does not move it",
                    "Update the first key's value and show that its position is unchanged.",
                    'const m = new Map<string, number>([["a", 1], ["b", 2]]);\n'
                    'm.set("a", 99);\n'
                    'console.log(`${[...m.keys()].join(",")} ${m.get("a") ?? 0}`);\n',
                    'm.set("a", 99);', [("", "a,b 99")],
                    hints=["Setting an existing key changes the value only.",
                           'Write m.set("a", 99);'],
                    difficulty="Easy"),
                _ex("tscourse-w19-o-4", "Move it to the end",
                    "Delete the key and set it again, which is how an LRU cache promotes an entry.",
                    'const m = new Map<string, number>([["a", 1], ["b", 2], ["c", 3]]);\n'
                    'const value = m.get("a") ?? 0;\n'
                    'm.delete("a");\n'
                    'm.set("a", value);\n'
                    'console.log([...m.keys()].join(","));\n',
                    'm.delete("a");', [("", "b,c,a")],
                    hints=["Re-setting alone is not enough; the key has to leave first.",
                           'Write m.delete("a");'],
                    difficulty="Medium"),
                _ex("tscourse-w19-o-5", "Sort the numeric keys numerically",
                    "Sort the ids as numbers rather than as strings.",
                    _NUMS +
                    'const m = new Map<number, number>();\n'
                    'for (const n of nums) {\n'
                    '  m.set(n, n * 2);\n}\n'
                    'const keys = [...m.keys()].sort((a, b) => a - b);\n'
                    'console.log(keys.join(","));\n',
                    'const keys = [...m.keys()].sort((a, b) => a - b);',
                    [("10 9 2", "2,9,10"), ("3 1", "1,3")],
                    hints=["Default sort would give 10 before 2.",
                           "Write const keys = [...m.keys()].sort((a, b) => a - b);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-o-6", "A report that is a decision",
                    "Sort by value descending with an alphabetical tie-break, so the order means something.",
                    _WORDS +
                    'const counts = new Map<string, number>();\n'
                    'for (const w of words) {\n'
                    '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                    'const rows = [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));\n'
                    'for (const [w, n] of rows) {\n'
                    '  console.log(`${n} ${w}`);\n}\n',
                    'for (const [w, n] of rows) {',
                    [("c a b a c a", "3 a\n2 c\n1 b"), ("y x", "1 x\n1 y")],
                    hints=["The rows are already sorted; the loop just prints them.",
                           "Write for (const [w, n] of rows) {"],
                    difficulty="Medium"),
                _fix("tscourse-w19-o-fix1", "Fix the report the input order decided",
                     "The ledger is summarised in whatever order the tags happened to arrive, so the same data in a different order gives a different report and yesterday's output cannot be diffed against today's. Sort the tags.",
                     _WORDS +
                     'const counts = new Map<string, number>();\n'
                     'for (const w of words) {\n'
                     '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                     'for (const [tag, n] of counts) {\n'
                     '  console.log(`${tag} ${n}`);\n}\n',
                     _WORDS +
                     'const counts = new Map<string, number>();\n'
                     'for (const w of words) {\n'
                     '  counts.set(w, (counts.get(w) ?? 0) + 1);\n}\n'
                     'for (const tag of [...counts.keys()].sort()) {\n'
                     '  console.log(`${tag} ${counts.get(tag) ?? 0}`);\n}\n',
                     [("home food home", "food 1\nhome 2"), ("b a", "a 1\nb 1")],
                     hints=["Insertion order never fails, which is what makes it easy to leave in.",
                            "Walk the keys in sorted order and look each value up.",
                            "Write for (const tag of [...counts.keys()].sort()) {"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Deleting and re-setting a key is how you build…",
                   ["a Set", "an LRU cache", "a queue", "a frequency table"], 1,
                   "Promotion to most-recently-used is a move to the end."),
                _q("`sort()` being stable means ties…",
                   ["are sorted", "keep input order — stable, and arbitrary", "throw",
                    "are removed"], 1,
                   "Which is why a tie-break matters."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w19-identity", "Keys that are objects",
            "Two identical-looking keys are two keys.",
            """
A Map accepts **any** value as a key — numbers, booleans, objects, functions,
symbols. What it does not do is compare them structurally:

```ts
const m = new Map<{ name: string }, number>();
m.set({ name: "food" }, 1);
m.set({ name: "food" }, 2);
m.size;                              // 2
m.get({ name: "food" });             // undefined
```

Three object literals, three different objects. The comparison is **identity** —
technically *SameValueZero*, which is `===` with one fix: `NaN` equals itself, so
`NaN` works as a key.

## When identity keying is exactly right

When the key **is** the thing:

```ts
const clicks = new Map<Button, number>();      // per-button counter
const cache = new Map<Node, Layout>();          // computed layout per node
```

You are annotating objects you already hold, and two different buttons *should* be
two entries even if they have the same label. This is the case that a string key
cannot express at all.

## When you wanted structure

For a grid coordinate, a date, a pair — you want `{x:1,y:2}` and `{x:1,y:2}` to be
the *same* key. They never will be, so build a **canonical key**:

```ts
function keyOf(p: Point): string {
  return `${p.x},${p.y}`;
}
const visited = new Set<string>();
visited.add(keyOf({ x: 1, y: 2 }));
visited.has(keyOf({ x: 1, y: 2 }));       // true
```

This is how every grid problem in week 27 tracks visited cells, and three rules
keep it correct:

* **Every field that matters is in the key**, in a fixed order.
* **The separator cannot appear in a field.** `"a,b" + "," + "c"` and `"a" + "," +
  "b,c"` collide; with numeric fields you are safe, with strings choose a
  separator the data cannot contain — or use `JSON.stringify` and accept its cost.
* **The key function is the only way in.** A single `visited.add(somethingElse)`
  bypassing it silently breaks the set.

## Primitives are compared by value

```ts
const m = new Map<number, string>();
m.set(1, "a");
m.get(1);            // "a" — numbers are values, not identities
```

So `Map<number, …>` and `Map<string, …>` behave exactly as you would hope. And
unlike an object, a Map keyed by `number` keeps numbers: `m.set(1, …)` and
`m.set("1", …)` are **two different keys**, where an object would collapse them.

> ⚠️ **Common mistakes:** expecting `get({...})` to find a structurally equal key;
> a canonical key that omits a field; and mixing keyed-by-object with
> keyed-by-canonical-string in the same collection.
""",
            warmup=[
                _q("`m.set({a:1},1); m.set({a:1},2); m.size` is…",
                   ["1", "2", "0", "an error"], 1,
                   "Two different objects."),
                _q("Map compares keys with…",
                   ["deep equality", "SameValueZero — like === but NaN equals itself", "==",
                    "JSON"], 1,
                   "Which is why NaN works as a key."),
                _q("To key by an object's contents you…",
                   ["cannot", "build a canonical string key", "use a WeakMap", "use =="], 1,
                   "Every grid problem does this."),
                _q("In a Map, the keys `1` and `\"1\"` are…",
                   ["the same", "two different keys", "an error", "merged"], 1,
                   "An object would collapse them."),
            ],
            exercises=[
                _ex("tscourse-w19-id-1", "Two keys that look like one",
                    "Set the same-looking object twice and report the size.",
                    'interface Tag {\n  readonly name: string;\n}\n'
                    'const m = new Map<Tag, number>();\n'
                    'm.set({ name: "food" }, 1);\n'
                    'm.set({ name: "food" }, 2);\n'
                    'console.log(`${m.size} ${m.get({ name: "food" }) ?? -1}`);\n',
                    'console.log(`${m.size} ${m.get({ name: "food" }) ?? -1}`);',
                    [("", "2 -1")],
                    hints=["A third literal is a third object, so the lookup finds nothing.",
                           'Write console.log(`${m.size} ${m.get({ name: "food" }) ?? -1}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-id-2", "Identity keying, used on purpose",
                    "Count per object, holding the objects themselves as keys.",
                    'interface Button {\n  readonly label: string;\n}\n'
                    'const ok: Button = { label: "Save" };\n'
                    'const cancel: Button = { label: "Save" };\n'
                    'const clicks = new Map<Button, number>();\n'
                    'clicks.set(ok, (clicks.get(ok) ?? 0) + 1);\n'
                    'clicks.set(ok, (clicks.get(ok) ?? 0) + 1);\n'
                    'clicks.set(cancel, (clicks.get(cancel) ?? 0) + 1);\n'
                    'console.log(`${clicks.size} ${clicks.get(ok) ?? 0} ${clicks.get(cancel) ?? 0}`);\n',
                    'clicks.set(cancel, (clicks.get(cancel) ?? 0) + 1);',
                    [("", "2 2 1")],
                    hints=["Two buttons with the same label are still two buttons — which is the point.",
                           "Write clicks.set(cancel, (clicks.get(cancel) ?? 0) + 1);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-id-3", "A canonical key",
                    "Turn the point into a string that two equal points both produce.",
                    'interface Point {\n  readonly x: number;\n  readonly y: number;\n}\n'
                    'function keyOf(p: Point): string {\n'
                    '  return `${p.x},${p.y}`;\n}\n'
                    'const visited = new Set<string>();\n'
                    'visited.add(keyOf({ x: 1, y: 2 }));\n'
                    'visited.add(keyOf({ x: 1, y: 2 }));\n'
                    'console.log(`${visited.size} ${visited.has(keyOf({ x: 1, y: 2 }))}`);\n',
                    '  return `${p.x},${p.y}`;', [("", "1 true")],
                    hints=["Both fields, in a fixed order, with a separator between them.",
                           "Write return `${p.x},${p.y}`;"],
                    difficulty="Medium"),
                _ex("tscourse-w19-id-4", "Visited cells on a grid",
                    "Track which cells have been walked, using the canonical key.",
                    _NUMS +
                    'function keyOf(x: number, y: number): string {\n'
                    '  return `${x},${y}`;\n}\n'
                    'const visited = new Set<string>();\n'
                    'let revisits = 0;\n'
                    'for (let i = 0; i + 1 < nums.length; i = i + 2) {\n'
                    '  const key = keyOf(nums[i] ?? 0, nums[i + 1] ?? 0);\n'
                    '  if (visited.has(key)) {\n'
                    '    revisits = revisits + 1;\n  }\n'
                    '  visited.add(key);\n}\n'
                    'console.log(`${visited.size} ${revisits}`);\n',
                    '  if (visited.has(key)) {',
                    [("1 2 1 2 3 4", "2 1"), ("0 0", "1 0")],
                    hints=["A cell already in the set is a revisit.",
                           "Write if (visited.has(key)) {"],
                    difficulty="Medium"),
                _ex("tscourse-w19-id-5", "Numbers stay numbers",
                    "Show that a Map keyed by number does not collapse `1` and `\"1\"` the way an object would.",
                    'const m = new Map<number | string, string>();\n'
                    'm.set(1, "number one");\n'
                    'm.set("1", "string one");\n'
                    'console.log(`${m.size} ${m.get(1) ?? "-"} ${m.get("1") ?? "-"}`);\n',
                    'm.set("1", "string one");',
                    [("", "2 number one string one")],
                    hints=["Two different key values, so two entries.",
                           'Write m.set("1", "string one");'],
                    difficulty="Medium"),
                _fix("tscourse-w19-id-fix1", "Fix the key that forgot a field",
                     "The canonical key only uses `x`, so `{x:1,y:2}` and `{x:1,y:9}` collide — the set holds one member where it should hold two. Put every field that matters into the key.",
                     'interface Point {\n  readonly x: number;\n  readonly y: number;\n}\n'
                     'function keyOf(p: Point): string {\n'
                     '  return `${p.x}`;\n}\n'
                     'const visited = new Set<string>();\n'
                     'visited.add(keyOf({ x: 1, y: 2 }));\n'
                     'visited.add(keyOf({ x: 1, y: 9 }));\n'
                     'console.log(visited.size);\n',
                     'interface Point {\n  readonly x: number;\n  readonly y: number;\n}\n'
                     'function keyOf(p: Point): string {\n'
                     '  return `${p.x},${p.y}`;\n}\n'
                     'const visited = new Set<string>();\n'
                     'visited.add(keyOf({ x: 1, y: 2 }));\n'
                     'visited.add(keyOf({ x: 1, y: 9 }));\n'
                     'console.log(visited.size);\n',
                     [("", "2")],
                     hints=["Two different points are producing the same key.",
                            "Every field that distinguishes two values has to be in the key.",
                            "Include `y`, with a separator."],
                     difficulty="Easy"),
            ],
            quiz=[
                _q("A canonical key's separator matters because…",
                   ["of speed", "two different field values can otherwise produce the same key",
                    "of types", "it does not"], 1,
                   "\"a,b\"+\",\"+\"c\" collides with \"a\"+\",\"+\"b,c\"."),
                _q("Keying a cache by the node object itself is…",
                   ["a mistake", "exactly what identity keying is for", "impossible",
                    "the same as a string key"], 1,
                   "Two different nodes should be two entries."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w19-weak", "`WeakMap`, briefly",
            "Metadata that does not keep its key alive.",
            """
A `WeakMap` is a Map with three restrictions and one superpower.

```ts
const meta = new WeakMap<Row, string>();
const row: Row = { id: 1 };
meta.set(row, "seen");
meta.get(row);                   // "seen"
meta.has(row);                   // true
meta.delete(row);
```

## The restrictions

**Keys must be objects.**

```ts
new WeakMap<string, number>();
// ❌ TS2344: Type 'string' does not satisfy the constraint 'WeakKey'.
```

**There is no `size`.**

```ts
meta.size;
// ❌ TS2339: Property 'size' does not exist on type 'WeakMap<Row, string>'.
```

**You cannot iterate it.** No `keys()`, no `values()`, no `entries()`, no
`for … of`.

## The superpower, and why the restrictions follow from it

A WeakMap holds its keys **weakly**: an entry does not stop its key from being
garbage collected. When the last other reference to `row` disappears, the entry
vanishes with it.

Every restriction follows from that one property. The number of entries can change
at any moment without your program doing anything, so `size` could not be reported
honestly; iteration would expose *when* the collector ran, which is deliberately
unobservable; and a string cannot be collected, so a primitive key would make the
whole thing meaningless.

## What it is for

**Metadata about objects you do not own.** You want to remember something about
each `Row` a library handed you, without preventing those rows from ever being
freed:

```ts
const parsed = new WeakMap<Request, ParsedBody>();     // cache per request
const listeners = new WeakMap<Element, Handler[]>();    // handlers per element
```

With a plain `Map`, every request you ever cached stays in memory for the life of
the program, because the Map is holding it. That is a textbook leak, and it is
exactly the leak a WeakMap does not have.

**Private data, historically.** Before `#private` fields, a WeakMap keyed by
`this` was how you hid state. Week 11's `#` syntax replaced that, and the pattern
is only worth recognising in older code.

## When not to reach for it

Almost always. If you can iterate what you are storing, you want a `Map`. A
WeakMap is for the specific case where the *lifetime* of the entry should be the
lifetime of the key — and in a program that reads stdin and exits, that never
matters. It matters enormously in something long-lived.

> ⚠️ **Common mistakes:** trying to count or iterate one; using a primitive key;
> and reaching for it as an optimisation rather than for the lifetime property.
""",
            warmup=[
                _q("A WeakMap's keys must be…",
                   ["strings", "objects", "numbers", "any value"], 1,
                   "Primitives cannot be collected."),
                _q("`weakMap.size` is…",
                   ["0", "TS2339 — there is no size", "the count", "undefined"], 1,
                   "The count can change without your program doing anything."),
                _q("You cannot iterate a WeakMap because…",
                   ["it is slow", "it would expose when the garbage collector ran",
                    "it has no keys", "of types"], 1,
                   "Deliberately unobservable."),
                _q("A plain Map used as a per-request cache…",
                   ["is fine", "keeps every request alive forever — a textbook leak", "is faster",
                    "is weak"], 1,
                   "Which is the case a WeakMap exists for."),
            ],
            exercises=[
                _ex("tscourse-w19-w-1", "Metadata per object",
                    "Store a note about the row, keyed by the row itself.",
                    'interface Row {\n  readonly id: number;\n}\n'
                    'const meta = new WeakMap<Row, string>();\n'
                    'const row: Row = { id: 1 };\n'
                    'meta.set(row, "seen");\n'
                    'console.log(`${meta.get(row) ?? "-"} ${meta.has(row)}`);\n',
                    'const meta = new WeakMap<Row, string>();', [("", "seen true")],
                    hints=["Same generic shape as a Map, with the object type as the key.",
                           "Write const meta = new WeakMap<Row, string>();"],
                    difficulty="Easy"),
                _ex("tscourse-w19-w-2", "Identity, again",
                    "Show that an equal-looking row is not the same key.",
                    'interface Row {\n  readonly id: number;\n}\n'
                    'const meta = new WeakMap<Row, string>();\n'
                    'const a: Row = { id: 1 };\n'
                    'meta.set(a, "seen");\n'
                    'console.log(`${meta.has(a)} ${meta.has({ id: 1 })}`);\n',
                    'console.log(`${meta.has(a)} ${meta.has({ id: 1 })}`);',
                    [("", "true false")],
                    hints=["A fresh literal is a different object, exactly as in lesson 6.",
                           'Write console.log(`${meta.has(a)} ${meta.has({ id: 1 })}`);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-w-3", "A cache, per object",
                    "Compute the parsed value once per row and reuse it on a second call.",
                    'interface Row {\n  readonly raw: string;\n}\n'
                    'const cache = new WeakMap<Row, number>();\n'
                    'let parses = 0;\n'
                    'function cents(row: Row): number {\n'
                    '  const hit = cache.get(row);\n'
                    '  if (hit !== undefined) {\n'
                    '    return hit;\n  }\n'
                    '  parses = parses + 1;\n'
                    '  const value = Number(row.raw);\n'
                    '  cache.set(row, value);\n'
                    '  return value;\n}\n'
                    'const row: Row = { raw: "325" };\n'
                    'console.log(`${cents(row)} ${cents(row)} parses ${parses}`);\n',
                    '  const hit = cache.get(row);', [("", "325 325 parses 1")],
                    hints=["Look in the cache first, and only compute on a miss.",
                           "Write const hit = cache.get(row);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-w-4", "A WeakSet of things already handled",
                    "Record that a row has been processed, without holding it alive.",
                    'interface Row {\n  readonly id: number;\n}\n'
                    'const done = new WeakSet<Row>();\n'
                    'const a: Row = { id: 1 };\n'
                    'const b: Row = { id: 2 };\n'
                    'done.add(a);\n'
                    'console.log(`${done.has(a)} ${done.has(b)}`);\n',
                    'const done = new WeakSet<Row>();', [("", "true false")],
                    hints=["The Set-shaped sibling, with the same object-key restriction.",
                           "Write const done = new WeakSet<Row>();"],
                    difficulty="Easy"),
                _diagnose("tscourse-w19-w-d1", "The count that is not there",
                          "TS2339: Property 'size' does not exist on type 'WeakMap<Row, string>'.",
                          'interface Row {\n  readonly id: number;\n}\n'
                          'const meta = new WeakMap<Row, string>();\n'
                          'const row: Row = { id: 1 };\n'
                          'meta.set(row, "seen");\n'
                          'console.log(meta.size);\n',
                          'interface Row {\n  readonly id: number;\n}\n'
                          'const meta = new Map<Row, string>();\n'
                          'const row: Row = { id: 1 };\n'
                          'meta.set(row, "seen");\n'
                          'console.log(meta.size);\n',
                          [("", "1")],
                          hints=["A WeakMap cannot report a count, because entries may vanish when their keys are collected.",
                                 "If you need to count what you are storing, you needed the strong version.",
                                 "Use a `Map` instead."],
                          difficulty="Medium"),
                _diagnose("tscourse-w19-w-d2", "A key that cannot be collected",
                          "TS2344: Type 'string' does not satisfy the constraint 'WeakKey'.",
                          'const meta = new WeakMap<string, number>();\n'
                          'meta.set("a", 1);\n'
                          'console.log(meta.get("a") ?? 0);\n',
                          'const meta = new Map<string, number>();\n'
                          'meta.set("a", 1);\n'
                          'console.log(meta.get("a") ?? 0);\n',
                          [("", "1")],
                          hints=["The whole point of a WeakMap is that the key can be garbage collected, and a string cannot.",
                                 "String keys belong in the strong version.",
                                 "Use a `Map`."],
                          difficulty="Easy"),
                # NOT a `fix`. A lifetime bug is by construction unobservable inside
                # one short program — the collector's timing is exactly what a
                # WeakMap refuses to expose — so a buggy starter here would produce
                # the right output and the verifier would (correctly) reject it.
                # It is a drill about the CHOICE instead, which is the part that
                # transfers: weak for the metadata, strong for what you must report.
                _ex("tscourse-w19-w-5", "Weak for metadata, strong for the report",
                    "Two structures, one program. The per-row parse cache must not keep its rows alive, "
                    "and the per-tag counter has to be iterated at the end — so exactly one of these two "
                    "declarations is the weak one. Write the cache's.",
                    'interface Row {\n  readonly raw: string;\n  readonly tag: string;\n}\n'
                    'const cache = new WeakMap<Row, number>();\n'
                    'const counts = new Map<string, number>();\n'
                    'function cents(row: Row): number {\n'
                    '  const hit = cache.get(row);\n'
                    '  if (hit !== undefined) {\n'
                    '    return hit;\n  }\n'
                    '  const value = Number(row.raw);\n'
                    '  cache.set(row, value);\n'
                    '  counts.set(row.tag, (counts.get(row.tag) ?? 0) + 1);\n'
                    '  return value;\n}\n'
                    'const rows: readonly Row[] = [\n'
                    '  { raw: "325", tag: "food" },\n'
                    '  { raw: "200", tag: "food" },\n'
                    '  { raw: "90000", tag: "home" },\n'
                    '];\n'
                    'let total = 0;\n'
                    'for (const row of rows) {\n'
                    '  total = total + cents(row);\n}\n'
                    'for (const row of rows) {\n'
                    '  cents(row);\n}\n'
                    'console.log(`total ${total}`);\n'
                    'for (const tag of [...counts.keys()].sort()) {\n'
                    '  console.log(`${tag} ${counts.get(tag) ?? 0}`);\n}\n',
                    'const cache = new WeakMap<Row, number>();',
                    [("", "total 90525\nfood 2\nhome 1")],
                    hints=["The cache is keyed by the rows themselves and is never iterated — it is the one that should not keep them alive.",
                           "`counts` is iterated at the end, so it cannot be the weak one.",
                           "Write const cache = new WeakMap<Row, number>();"],
                    difficulty="Medium"),
            ],
            quiz=[
                _q("Before `#private` fields, a WeakMap keyed by `this` was used for…",
                   ["caching", "private instance data", "iteration", "counting"], 1,
                   "Worth recognising in older code; week 11 replaced it."),
                _q("Reach for a WeakMap when…",
                   ["you want speed", "the entry's lifetime should be the key's lifetime",
                    "you need to iterate", "keys are strings"], 1,
                   "Otherwise you want a Map."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w19-groupby", "Grouping, with the standard library",
            "The read-or-default dance, done for you.",
            """
Lesson 3 built groups by hand:

```ts
const group = byFirst.get(key) ?? [];
group.push(word);
byFirst.set(key, group);
```

ES2024 has that built in, in two flavours:

```ts
const byFirst = Map.groupBy(words, (w) => w.charAt(0));
// Map<string, string[]>

const asObject = Object.groupBy(words, (w) => w.charAt(0));
// Partial<Record<string, string[]>>
```

Both take an iterable and a key function, and both put each member into the array
for its key, **in input order**.

## `Map.groupBy` is the one to reach for

Because of lesson 1: an object reorders integer-like keys, and grouping by a
number is extremely common ("by year", "by score", "by length"). `Map.groupBy`
keeps insertion order, so the groups come out in the order the keys were first
seen.

## Both results need a fallback

```ts
(byFirst.get("a") ?? []).join(" ");           // Map: get is V | undefined
(asObject["a"] ?? []).join(" ");               // object: Partial<…>, so the same
```

`Object.groupBy` returns a **`Partial<Record<K, T[]>>`** — the type says outright
that a key may be absent, which is unusually honest for a standard-library
signature and means the compiler makes you handle it.

## What it does not do

* **It does not aggregate.** `Map.groupBy` gives you the members; summing them is
  still your loop. The pattern is group, then reduce per group.
* **It does not sort.** Neither the groups nor their members. A report still sorts.
* **The key function must return a valid key.** Returning an object gives you
  identity keying and a group per member, which is never what was wanted.

## Group, then aggregate

The shape worth keeping:

```ts
const byTag = Map.groupBy(entries, (e) => e.tag);
const totals = new Map<string, number>();
for (const [tag, group] of byTag) {
  let sum = 0;
  for (const e of group) { sum = sum + e.cents; }
  totals.set(tag, sum);
}
for (const tag of [...totals.keys()].sort()) { … }      // and then sort the report
```

Three steps, each doing one thing: group, aggregate, order. It is worth resisting
the temptation to do all three in one pass — the version above is the one you can
still read in six months, and it is the shape the capstone uses.

> ⚠️ **Common mistakes:** expecting the groups to be sorted; forgetting the `??
> []` on a lookup; and using `Object.groupBy` with numeric keys, which reorders
> them.
""",
            warmup=[
                _q("`Map.groupBy(xs, f)` returns…",
                   ["an array", "a Map from key to an array of members", "an object", "a Set"], 1,
                   "One entry per distinct key."),
                _q("`Object.groupBy` returns…",
                   ["Record<K, T[]>", "Partial<Record<K, T[]>> — a key may be absent",
                    "a Map", "an array"], 1,
                   "Unusually honest typing."),
                _q("Members within a group are in…",
                   ["sorted order", "input order", "reverse order", "random order"], 1,
                   "Nothing is sorted for you."),
                _q("Prefer `Map.groupBy` over `Object.groupBy` because…",
                   ["it is faster", "an object reorders integer-like keys, and grouping by a number is common",
                    "it is newer", "of types"], 1,
                   "Lesson 1's first problem."),
            ],
            exercises=[
                _ex("tscourse-w19-g-1", "Group by first letter",
                    "Use the standard-library grouping, keyed by the first character.",
                    _WORDS +
                    'const byFirst = Map.groupBy(words, (w) => w.charAt(0));\n'
                    'for (const key of [...byFirst.keys()].sort()) {\n'
                    '  console.log(`${key}: ${(byFirst.get(key) ?? []).join(" ")}`);\n}\n',
                    'const byFirst = Map.groupBy(words, (w) => w.charAt(0));',
                    [("ant bee auk", "a: ant auk\nb: bee"), ("solo", "s: solo")],
                    hints=["One call, taking the iterable and a key function.",
                           "Write const byFirst = Map.groupBy(words, (w) => w.charAt(0));"],
                    difficulty="Medium"),
                _ex("tscourse-w19-g-2", "Group by length",
                    "Key by a number, and print the groups by key ascending.",
                    _WORDS +
                    'const byLength = Map.groupBy(words, (w) => w.length);\n'
                    'for (const key of [...byLength.keys()].sort((a, b) => a - b)) {\n'
                    '  console.log(`${key}: ${(byLength.get(key) ?? []).join(" ")}`);\n}\n',
                    'for (const key of [...byLength.keys()].sort((a, b) => a - b)) {',
                    [("ant bee sky at", "2: at\n3: ant bee sky")],
                    hints=["Numeric keys need a numeric comparator, not the default.",
                           "Write for (const key of [...byLength.keys()].sort((a, b) => a - b)) {"],
                    difficulty="Medium"),
                _ex("tscourse-w19-g-3", "The object flavour, and its fallback",
                    "Use `Object.groupBy` and handle the group that may be absent.",
                    _WORDS +
                    'const grouped = Object.groupBy(words, (w) => w.charAt(0));\n'
                    'console.log((grouped["a"] ?? []).length);\n',
                    'console.log((grouped["a"] ?? []).length);',
                    [("ant auk bee", "2"), ("bee", "0")],
                    hints=["The result type is `Partial<…>`, so the compiler insists on the fallback.",
                           'Write console.log((grouped["a"] ?? []).length);'],
                    difficulty="Medium"),
                _ex("tscourse-w19-g-4", "Group, then aggregate",
                    "Sum each group, then report the totals in key order.",
                    _NUMS +
                    'const byParity = Map.groupBy(nums, (n) => (n % 2 === 0 ? "even" : "odd"));\n'
                    'const totals = new Map<string, number>();\n'
                    'for (const [key, group] of byParity) {\n'
                    '  let sum = 0;\n'
                    '  for (const n of group) {\n'
                    '    sum = sum + n;\n  }\n'
                    '  totals.set(key, sum);\n}\n'
                    'for (const key of [...totals.keys()].sort()) {\n'
                    '  console.log(`${key} ${totals.get(key) ?? 0}`);\n}\n',
                    '  totals.set(key, sum);',
                    [("1 2 3 4", "even 6\nodd 4"), ("2 4", "even 6")],
                    hints=["The group's sum goes into the totals map under the same key.",
                           "Write totals.set(key, sum);"],
                    difficulty="Medium"),
                _ex("tscourse-w19-g-5", "The biggest group",
                    "Report which key has the most members, breaking ties alphabetically.",
                    _WORDS +
                    'const byFirst = Map.groupBy(words, (w) => w.charAt(0));\n'
                    'let best = "";\n'
                    'let bestCount = 0;\n'
                    'for (const key of [...byFirst.keys()].sort()) {\n'
                    '  const n = (byFirst.get(key) ?? []).length;\n'
                    '  if (n > bestCount) {\n'
                    '    best = key;\n    bestCount = n;\n  }\n}\n'
                    'console.log(`${best} ${bestCount}`);\n',
                    '  const n = (byFirst.get(key) ?? []).length;',
                    [("ant auk bee", "a 2"), ("bee cat", "b 1")],
                    hints=["The group's size is the length of its array — with the usual fallback.",
                           "Write const n = (byFirst.get(key) ?? []).length;"],
                    difficulty="Medium"),
                _predict("tscourse-w19-g-p1", "What grouping gives you",
                         'const words: readonly string[] = ["ant", "bee"];\n'
                         'const grouped = Map.groupBy(words, (w) => w.charAt(0));\n',
                         "grouped", "Map<string, string[]>",
                         why="The key comes from the key function, and each group holds the members.",
                         hints=["A Map, whose value type is an array of the member type.",
                                "Write Map<string, string[]>."],
                         difficulty="Medium"),
                _fix("tscourse-w19-g-fix1", "Fix the grouping that reordered the years",
                     "Grouping by year with `Object.groupBy` prints 1999 before 2020 and 2020 before 3 — the keys are integer-like, so the object sorted them numerically and the report no longer follows the ledger. Use the flavour that keeps insertion order.",
                     _NUMS +
                     'const grouped = Object.groupBy(nums, (n) => `${n % 100}`);\n'
                     'console.log(Object.keys(grouped).join(","));\n',
                     _NUMS +
                     'const grouped = Map.groupBy(nums, (n) => `${n % 100}`);\n'
                     'console.log([...grouped.keys()].join(","));\n',
                     [("2020 1999 103", "20,99,3"), ("5 4", "5,4")],
                     hints=["The keys here look like numbers, which is exactly the case lesson 1 warned about.",
                            "`Map.groupBy` keeps first-seen order.",
                            "Reading the keys back out changes too: `[...grouped.keys()]`."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`Map.groupBy` aggregates…",
                   ["sums", "nothing — it groups, and the aggregation is still your loop",
                    "counts", "averages"], 1,
                   "Group, aggregate, order: three steps."),
                _q("A key function returning an object gives you…",
                   ["one group", "identity keying, and a group per member", "an error",
                    "sorted groups"], 1,
                   "Lesson 6's rule, applied here."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #19 — the index",
        """
Budget Buddy has been scanning the whole ledger for every question. This week it
builds an **index** instead: entries go into a `Map` keyed by tag, and a `Set`
remembers every description already used, so a duplicate is rejected in O(1)
rather than by a scan.

Input: one entry per line, `desc cents tag`.

```
coffee 325 food
rent 90000 home
coffee 200 food
tea 200 food
```

```
rejected: coffee (duplicate)
Entries:  3
Tags:     3
food      2  $5.25
home      1  $900.00
Top tag:  home $900.00
Unique:   3 descriptions
```

**What it has to do:**

1. **Reject duplicates in O(1).** A description already in the `Set` is refused;
   print `rejected: <desc> (duplicate)` as it happens, and it does not reach the
   ledger.
2. **Index by tag** into a `Map<string, Entry[]>`, using the read-or-default
   append from lesson 2.
3. **Report per tag, sorted alphabetically** — the count and the total, the count
   padded so the columns line up (`String(count).padStart(2)`).
4. **Name the top tag** by total, breaking ties alphabetically, so the answer is a
   decision rather than an accident of input order.
5. **Count the unique descriptions** from the Set's `size`, not by building an
   array.

**Why the index is the point:** the per-tag report does not filter the ledger once
per tag — that would be O(tags × entries). Every entry is placed once as it
arrives, so the whole program is one pass plus a sort of the tag names.

A malformed line (not three fields, or a non-numeric amount) is skipped silently.
Empty input prints `Entries:  0`, `Tags:     0`, no tag rows, `Top tag:  none` and
`Unique:   0 descriptions`.
""",
        _ch("tscourse-w19-capstone", "Budget Buddy #19", "Hard",
            "Index the ledger by tag in a Map, reject duplicate descriptions with a Set, and "
            "report per tag in sorted order.",
            _FS +
            'interface Entry {\n'
            '  readonly desc: string;\n'
            '  readonly cents: number;\n'
            '  readonly tag: string;\n}\n'
            'const byTag = new Map<string, Entry[]>();\n'
            'const seen = new Set<string>();\n'
            'let count = 0;\n'
            'const lines = fs.readFileSync(0, "utf8").split("\\n").filter((l) => l.trim() !== "");\n'
            'for (const line of lines) {\n'
            '  const parts = line.trim().split(/\\s+/);\n'
            '  if (parts.length !== 3) {\n'
            '    continue;\n  }\n'
            '  const desc = parts[0] ?? "";\n'
            '  const cents = Number(parts[1] ?? "");\n'
            '  const tag = parts[2] ?? "";\n'
            '  if (!Number.isFinite(cents)) {\n'
            '    continue;\n  }\n'
            '  if (seen.has(desc)) {\n'
            '    console.log(`rejected: ${desc} (duplicate)`);\n'
            '    continue;\n  }\n'
            '  seen.add(desc);\n'
            '  const group = byTag.get(tag) ?? [];\n'
            '  group.push({ desc, cents, tag });\n'
            '  byTag.set(tag, group);\n'
            '  count = count + 1;\n}\n'
            'function money(cents: number): string {\n'
            '  return `$${(cents / 100).toFixed(2)}`;\n}\n'
            'const totals = new Map<string, number>();\n'
            'for (const [tag, group] of byTag) {\n'
            '  let sum = 0;\n'
            '  for (const e of group) {\n'
            '    sum = sum + e.cents;\n  }\n'
            '  totals.set(tag, sum);\n}\n'
            'console.log(`Entries:  ${count}`);\n'
            'console.log(`Tags:     ${byTag.size}`);\n'
            'const tags = [...byTag.keys()].sort();\n'
            'for (const tag of tags) {\n'
            '  const group = byTag.get(tag) ?? [];\n'
            '  const padded = String(group.length).padStart(2);\n'
            '  console.log(`${tag.padEnd(9)} ${padded}  ${money(totals.get(tag) ?? 0)}`);\n}\n'
            'let topTag = "none";\n'
            'let topCents = -1;\n'
            'for (const tag of tags) {\n'
            '  const sum = totals.get(tag) ?? 0;\n'
            '  if (sum > topCents) {\n'
            '    topTag = tag;\n    topCents = sum;\n  }\n}\n'
            'console.log(topTag === "none" ? "Top tag:  none" : `Top tag:  ${topTag} ${money(topCents)}`);\n'
            'console.log(`Unique:   ${seen.size} descriptions`);\n',
            'const totals = new Map<string, number>();\n'
            'for (const [tag, group] of byTag) {\n'
            '  let sum = 0;\n'
            '  for (const e of group) {\n'
            '    sum = sum + e.cents;\n  }\n'
            '  totals.set(tag, sum);\n}\n'
            'console.log(`Entries:  ${count}`);\n'
            'console.log(`Tags:     ${byTag.size}`);\n'
            'const tags = [...byTag.keys()].sort();\n'
            'for (const tag of tags) {\n'
            '  const group = byTag.get(tag) ?? [];\n'
            '  const padded = String(group.length).padStart(2);\n'
            '  console.log(`${tag.padEnd(9)} ${padded}  ${money(totals.get(tag) ?? 0)}`);\n}\n'
            'let topTag = "none";\n'
            'let topCents = -1;\n'
            'for (const tag of tags) {\n'
            '  const sum = totals.get(tag) ?? 0;\n'
            '  if (sum > topCents) {\n'
            '    topTag = tag;\n    topCents = sum;\n  }\n}\n'
            'console.log(topTag === "none" ? "Top tag:  none" : `Top tag:  ${topTag} ${money(topCents)}`);\n'
            'console.log(`Unique:   ${seen.size} descriptions`);',
            [("coffee 325 food\nrent 90000 home\ncoffee 200 food\ntea 200 food",
              "rejected: coffee (duplicate)\nEntries:  3\nTags:     2\n"
              "food       2  $5.25\nhome       1  $900.00\n"
              "Top tag:  home $900.00\nUnique:   3 descriptions"),
             ("a 100 x\nb 100 y",
              "Entries:  2\nTags:     2\nx          1  $1.00\ny          1  $1.00\n"
              "Top tag:  x $1.00\nUnique:   2 descriptions"),
             ("a 100 z\noops\nb notanumber z\nc 250 z",
              "Entries:  2\nTags:     1\nz          2  $3.50\n"
              "Top tag:  z $3.50\nUnique:   2 descriptions"),
             ("", "Entries:  0\nTags:     0\nTop tag:  none\nUnique:   0 descriptions")],
            hints=["The Set holds descriptions and answers the duplicate question in O(1) — no scan of the ledger anywhere.",
                   "`byTag.get(tag) ?? []` then push then set: the read-or-default append from lesson 2.",
                   "Totals are computed once per group after the pass, not by filtering the ledger per tag.",
                   "`byTag.size` is the tag count; `seen.size` is the unique-description count. Neither needs an array.",
                   "Sort the tag names once and reuse that array for both the rows and the top-tag scan.",
                   "`tag.padEnd(9)` and `String(n).padStart(2)` line the columns up.",
                   "`topCents` starts at -1 and the comparison is a strict `>`, so walking sorted tags gives the alphabetical winner on a tie."]),
        example_io="rejected: coffee (duplicate)\nEntries:  3\nTags:     2\nfood       2  $5.25\nhome       1  $900.00\nTop tag:  home $900.00\nUnique:   3 descriptions",
        rubric=["duplicates are rejected through a Set, in O(1) — nothing scans the ledger",
                "entries are indexed by tag as they arrive, not filtered per tag afterwards",
                "every Map read has a `??` fallback; there is no `!` in the file",
                "counts come from `.size`, not from building an array to measure",
                "the tag rows are sorted alphabetically, and the top tag breaks ties the same way",
                "a malformed line is skipped without crashing or being counted",
                "the columns line up through padEnd/padStart rather than hand-spacing",
                "empty input prints the summary, no tag rows, and `Top tag:  none`"],
        stretch=_ch("tscourse-w19-capstone-stretch", "Budget Buddy #19 (stretch)", "Hard",
                    "Compare two months. The input is two blocks separated by a line containing "
                    "only `--`; report the tags that are new this month, the ones that are gone, "
                    "and the ones in both — using set algebra rather than loops.",
                    _FS +
                    'const text = fs.readFileSync(0, "utf8");\n'
                    'const blocks = text.split("\\n--\\n");\n'
                    'function tagsOf(block: string): Set<string> {\n'
                    '  const out = new Set<string>();\n'
                    '  for (const line of block.split("\\n")) {\n'
                    '    const parts = line.trim().split(/\\s+/);\n'
                    '    if (parts.length === 3) {\n'
                    '      out.add(parts[2] ?? "");\n    }\n  }\n'
                    '  return out;\n}\n'
                    'const last = tagsOf(blocks[0] ?? "");\n'
                    'const now = tagsOf(blocks[1] ?? "");\n'
                    'function show(label: string, s: Set<string>): void {\n'
                    '  const sorted = [...s].sort();\n'
                    '  console.log(`${label.padEnd(9)} ${sorted.length === 0 ? "-" : sorted.join(",")}`);\n}\n'
                    'show("new:", now.difference(last));\n'
                    'show("gone:", last.difference(now));\n'
                    'show("both:", now.intersection(last));\n'
                    'console.log(`same set: ${now.isSubsetOf(last) && now.isSupersetOf(last)}`);\n',
                    'function show(label: string, s: Set<string>): void {\n'
                    '  const sorted = [...s].sort();\n'
                    '  console.log(`${label.padEnd(9)} ${sorted.length === 0 ? "-" : sorted.join(",")}`);\n}\n'
                    'show("new:", now.difference(last));\n'
                    'show("gone:", last.difference(now));\n'
                    'show("both:", now.intersection(last));\n'
                    'console.log(`same set: ${now.isSubsetOf(last) && now.isSupersetOf(last)}`);',
                    [("a 100 home\nb 200 books\n--\nc 300 home\nd 400 travel",
                      "new:      travel\ngone:     books\nboth:     home\nsame set: false"),
                     ("a 100 home\n--\nb 200 home",
                      "new:      -\ngone:     -\nboth:     home\nsame set: true"),
                     ("a 100 home\n--\n",
                      "new:      -\ngone:     home\nboth:     -\nsame set: false")],
                    hints=["`now.difference(last)` is what is new; `last.difference(now)` is what is gone.",
                           "An empty result prints `-` rather than an empty field.",
                           "Two sets are equal when each is a subset of the other — there is no `equals`.",
                           "Sort inside `show`, so all three lines are ordered the same way."]),
    ),
))
