# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter reading kinds, Month 3 (TS_MASTERY_ROADMAP
# X-10, X-11): predict / diagnose / retype / design / fix for the maps & sets,
# unions, aliases, literal inference, enums, narrowing, predicates, nullish,
# control flow, discriminated unions, top/bottom, function types and type
# testing chapters of weeks 9-13, topping each chapter up to its target.
#
# Weeks 9-13 run at `strict` (no noUncheckedIndexedAccess), and the scope lint
# keeps each program inside what its week has taught. `enum` is not erasable
# syntax, so an exercise that declares one is type-only (no inputs). Helpers
# are in mastery_ts_chapter_kit.py; exec()'d by gen_seed.py with the other
# tools/mastery_ts_x_m*.py files.
# ---------------------------------------------------------------------------


# === ts_maps_sets (week 9) ==================================================

_xpr("ts_maps_sets", 1, "A lookup that might miss",
     "const byLength = new Map<number, string[]>();\nbyLength.set(3, [\"cat\", \"dog\"]);\nconst three = byLength.get(3);\n",
     "three", "string[] | undefined",
     hints=["`get` cannot know the key is there, even right after a `set`.", "The value type, or `undefined`."])

_xpr("ts_maps_sets", 2, "Spreading a map",
     "const stock = new Map([[\"pen\", 3], [\"ink\", 0]]);\nconst rows = [...stock];\n",
     "rows", "[string, number][]",
     hints=["Iterating a `Map` yields entries.", "Each entry is a `[key, value]` tuple."])

_xdx("ts_maps_sets", 1, "A Set has no push",
     "TS2339: Property 'push' does not exist on type 'Set<string>'.",
     r'''
const seen = new Set<string>();
for (const w of input.split(/\s+/)) seen.push(w);
console.log(seen.size);
''', r'''
const seen = new Set<string>();
for (const w of input.split(/\s+/)) seen.add(w);
console.log(seen.size);
''', ["a b a c", "x x x", "one"],
     ask="Count the distinct words.",
     hints=["A `Set` is not an array: it has no position to push onto.", "Members go in with `add`."])

_xrt("ts_maps_sets", 1, "A map of word lengths",
     "Each word is stored with its length, then every word of length 3 is printed. Replace the `any`.",
     r'''
const lengths: any = new Map();
for (const w of input.split(/\s+/)) lengths.set(w, w.length);
const short = [...lengths].filter(([, n]) => n === 3).map(([w]) => w);
console.log(short.join(" ") || "none");
''', r'''
const lengths = new Map<string, number>();
for (const w of input.split(/\s+/)) lengths.set(w, w.length);
const short = [...lengths].filter(([, n]) => n === 3).map(([w]) => w);
console.log(short.join(" ") || "none");
''', "type _1 = Expect<Equal<typeof lengths, Map<string, number>>>;\ntype _2 = Expect<Equal<typeof short, string[]>>;",
     ["cat horse dog cat", "elephant", "the end"],
     hints=["`new Map()` with no type arguments is a map of `any` to `any`.",
            "Say the key and value types: `new Map<string, number>()`."])

_xrt("ts_maps_sets", 2, "The first repeat",
     "`firstRepeat` returns the first word seen twice, or nothing. Type its parameter and result honestly.",
     r'''
function firstRepeat(words: any): any {
  const seen = new Set<string>();
  for (const w of words) {
    if (seen.has(w)) return w;
    seen.add(w);
  }
  return undefined;
}
console.log(firstRepeat(input.split(/\s+/)) ?? "none");
''', r'''
function firstRepeat(words: string[]): string | undefined {
  const seen = new Set<string>();
  for (const w of words) {
    if (seen.has(w)) return w;
    seen.add(w);
  }
  return undefined;
}
console.log(firstRepeat(input.split(/\s+/)) ?? "none");
''', "type _1 = Expect<Equal<ReturnType<typeof firstRepeat>, string | undefined>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof firstRepeat>, [words: string[]]>>;",
     ["a b c b a", "x y z", "q q"],
     hints=["What does the loop iterate, and what can the function hand back?",
            "`string[]` in; a word or `undefined` out."])

_xrt("ts_maps_sets", 3, "Grouping by first letter",
     "Words are grouped under their first letter, and the groups printed in first-seen order. Replace the `any`s.",
     r'''
const groups = new Map<any, any>();
for (const w of input.split(/\s+/)) {
  const key = w[0];
  const group = groups.get(key) ?? [];
  group.push(w);
  groups.set(key, group);
}
for (const [letter, words] of groups) console.log(`${letter}: ${words.join(" ")}`);
''', r'''
const groups = new Map<string, string[]>();
for (const w of input.split(/\s+/)) {
  const key = w[0];
  const group = groups.get(key) ?? [];
  group.push(w);
  groups.set(key, group);
}
for (const [letter, words] of groups) console.log(`${letter}: ${words.join(" ")}`);
''', "type _1 = Expect<Equal<typeof groups, Map<string, string[]>>>;",
     ["apple bat avocado cherry banana", "kiwi", "ox owl ox"],
     hints=["The key is a letter; the value is the list of words under it.",
            "`Map<string, string[]>`."])

_xdz("ts_maps_sets", 1, "An inventory",
     "Write the `Inventory` type from how `restock` and `take` use it. Each line is `+item n` or `-item n`.",
     r'''
type Inventory = Map<string, number>;
function restock(inv: Inventory, item: string, n: number): void {
  inv.set(item, (inv.get(item) ?? 0) + n);
}
function take(inv: Inventory, item: string, n: number): void {
  inv.set(item, Math.max(0, (inv.get(item) ?? 0) - n));
}
const inv: Inventory = new Map();
for (const line of input.split("\n")) {
  const [op, n] = line.trim().split(" ");
  const item = op.slice(1);
  if (op[0] === "+") restock(inv, item, Number(n));
  else take(inv, item, Number(n));
}
console.log([...inv].map(([k, v]) => `${k}=${v}`).join(" "));
''', "type Inventory = Map<string, number>;",
     "type _1 = Expect<Equal<Inventory, Map<string, number>>>;",
     ["+pen 3\n+ink 2\n-pen 1", "+cup 1\n-cup 5", "+a 1\n+b 2\n+a 4"],
     hints=["Items are looked up by name, and the count comes back.", "A `Map` from name to count."])

_xdz("ts_maps_sets", 2, "Likes, without doubles",
     "Each line is `user item`. Write the `Likes` type: every user's distinct items, in the order first liked.",
     r'''
type Likes = Map<string, Set<string>>;
const likes: Likes = new Map();
for (const line of input.split("\n")) {
  const [user, item] = line.trim().split(" ");
  const mine = likes.get(user) ?? new Set();
  mine.add(item);
  likes.set(user, mine);
}
for (const [user, items] of likes) console.log(`${user}: ${[...items].join(",")} (${items.size})`);
''', "type Likes = Map<string, Set<string>>;",
     "type _1 = Expect<Equal<Likes, Map<string, Set<string>>>>;",
     ["ana tea\nbo jam\nana tea\nana cake", "zed x", "a 1\nb 1\na 2\nb 1"],
     hints=["A user can like the same item twice but should see it once.", "A map whose values are sets."])

_xfx("ts_maps_sets", 1, "for...in over a Map",
     "It should print each distinct word with its count, in first-seen order, and prints nothing at all.",
     r'''
const counts = new Map<string, number>();
for (const w of input.split(/\s+/)) counts.set(w, (counts.get(w) ?? 0) + 1);
for (const w in counts) console.log(`${w} ${counts.get(w)}`);
''', r'''
const counts = new Map<string, number>();
for (const w of input.split(/\s+/)) counts.set(w, (counts.get(w) ?? 0) + 1);
for (const [w, n] of counts) console.log(`${w} ${n}`);
''', ["to be or not to be", "hi", "a a a"],
     hints=["`for...in` walks an object's enumerable properties. How many does a `Map` have?",
            "Iterate the entries with `for...of`."])


# === ts_set_algebra (week 9) ================================================

_xdx("ts_set_algebra", 1, "Object.groupBy is not a Map",
     "TS2339: Property 'get' does not exist on type 'Partial<Record<number, number[]>>'.",
     r'''
const nums = input.split(/\s+/).map(Number);
const byTens = Object.groupBy(nums, (n) => Math.floor(n / 10) * 10);
console.log(byTens.get(10)?.join(" ") ?? "none");
''', r'''
const nums = input.split(/\s+/).map(Number);
const byTens = Map.groupBy(nums, (n) => Math.floor(n / 10) * 10);
console.log(byTens.get(10)?.join(" ") ?? "none");
''', ["12 5 19 30", "1 2", "10"],
     ask="Keep the numeric keys and the `get` call.",
     hints=["`Object.groupBy` builds a plain object, and a plain object has no `get`.",
            "The grouping that returns a `Map` is `Map.groupBy`."])

_xrt("ts_set_algebra", 1, "What both share",
     "`shared` returns the tags two articles have in common. Type it honestly.",
     r'''
function shared(a: any, b: any): any {
  return a.intersection(b);
}
const [x = "", y = ""] = input.split("\n");
const common = shared(new Set(x.trim().split(/\s+/)), new Set(y.trim().split(/\s+/)));
console.log([...common].join(" ") || "(none)", common.size);
''', r'''
function shared(a: Set<string>, b: Set<string>): Set<string> {
  return a.intersection(b);
}
const [x = "", y = ""] = input.split("\n");
const common = shared(new Set(x.trim().split(/\s+/)), new Set(y.trim().split(/\s+/)));
console.log([...common].join(" ") || "(none)", common.size);
''', "type _1 = Expect<Equal<ReturnType<typeof shared>, Set<string>>>;\n"
     "type _2 = Expect<Equal<Parameters<typeof shared>, [a: Set<string>, b: Set<string>]>>;",
     ["ts js web\njs web css", "a b\nc d", "x\nx"],
     hints=["The algebra methods return a new `Set` of the same element type.", "`Set<string>` in, `Set<string>` out."])

_xrt("ts_set_algebra", 2, "Buckets by length",
     "Words are grouped by length with `Map.groupBy` and printed shortest first. Replace the `any`.",
     r'''
const words = input.split(/\s+/);
const byLength: any = Map.groupBy(words, (w) => w.length);
const lengths = [...byLength.keys()].sort((a, b) => a - b);
for (const n of lengths) console.log(`${n}: ${byLength.get(n).join(" ")}`);
''', r'''
const words = input.split(/\s+/);
const byLength = Map.groupBy(words, (w) => w.length);
const lengths = [...byLength.keys()].sort((a, b) => a - b);
for (const n of lengths) console.log(`${n}: ${(byLength.get(n) ?? []).join(" ")}`);
''', "type _1 = Expect<Equal<typeof byLength, Map<number, string[]>>>;\ntype _2 = Expect<Equal<typeof lengths, number[]>>;",
     ["go tea cake it ox", "hello", "aa b cc d"],
     hints=["Let `Map.groupBy` infer it: the key is what the callback returns.",
            "Once typed, `get` admits it may miss — handle it."])

_xdz("ts_set_algebra", 1, "What changed",
     "Two lines: the old roster and the new. Write the `Change` type that `compare` returns.",
     r'''
type Change = { joined: Set<string>; left: Set<string> };
function compare(before: Set<string>, after: Set<string>): Change {
  return { joined: after.difference(before), left: before.difference(after) };
}
const [a = "", b = ""] = input.split("\n");
const c = compare(new Set(a.trim().split(/\s+/)), new Set(b.trim().split(/\s+/)));
console.log("joined:", [...c.joined].join(" ") || "-");
console.log("left:", [...c.left].join(" ") || "-");
''', "type Change = { joined: Set<string>; left: Set<string> };",
     "type _1 = Expect<Equal<Change, { joined: Set<string>; left: Set<string> }>>;",
     ["ana bo cy\nbo cy dee", "x\nx", "a b\nc"],
     hints=["Read the object literal `compare` returns.", "Two fields, both the result of `difference`."])

_xdz("ts_set_algebra", 2, "Who may deploy",
     "The first line lists the required permissions; each later line is `user perm perm ...`. "
     "Write the `Grant` type and print the users holding every required permission.",
     r'''
type Grant = { user: string; perms: Set<string> };
const [head = "", ...rest] = input.split("\n");
const required = new Set(head.trim().split(/\s+/));
const grants: Grant[] = rest.map((line) => {
  const [user = "", ...perms] = line.trim().split(/\s+/);
  return { user, perms: new Set(perms) };
});
const ok = grants.filter((g) => required.isSubsetOf(g.perms)).map((g) => g.user);
console.log(ok.join(" ") || "nobody");
''', "type Grant = { user: string; perms: Set<string> };",
     "type _1 = Expect<Equal<Grant, { user: string; perms: Set<string> }>>;",
     ["read write\nana read write admin\nbo read\ncy write read", "x\nzed y", "a\nb a\nc a"],
     hints=["A name, and something `isSubsetOf` can take as its argument.", "`perms` is a `Set<string>`."])

_xfx("ts_set_algebra", 1, "Subset, the wrong way round",
     "The first line is the required tags, the second the tags a post has. It should print `ok` "
     "when the post has every required tag — and gets it wrong when the post has extra tags.",
     r'''
const [a = "", b = ""] = input.split("\n");
const required = new Set(a.trim().split(/\s+/));
const have = new Set(b.trim().split(/\s+/));
console.log(have.isSubsetOf(required) ? "ok" : "missing " + [...required.difference(have)].join(" "));
''', r'''
const [a = "", b = ""] = input.split("\n");
const required = new Set(a.trim().split(/\s+/));
const have = new Set(b.trim().split(/\s+/));
console.log(required.isSubsetOf(have) ? "ok" : "missing " + [...required.difference(have)].join(" "));
''', ["ts web\nts web css", "ts web\nts", "a\na"],
     hints=["Read it aloud: \"every required tag is in what the post has\".",
            "The receiver is the set that must fit inside the argument."])
