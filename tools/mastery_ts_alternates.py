# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — alternate coding finals (TS_MASTERY_ROADMAP X-33).
#
# One per core week. After a failed attempt the week's final offers "retake
# with a different version": a different problem on the same ideas at the same
# strictness, so a retake tests the week rather than a memory of its tests.
# Passing either version passes the week.
#
# Every expected output is computed from the reference (ts_outputs_kit.py) and
# tests/verify_mastery.rs re-proves every alternate through the real judge.
# exec()'d by gen_seed.py after mastery_ts_finals.py; attached by
# mastery_ts_attach.py.
# ---------------------------------------------------------------------------


def _alt(week, slug, title, prompt, body, inputs, hint=""):
    return _ts_exam_io(f"tsm-final-w{week}-alt-{slug}", title, prompt, body, inputs, hint=hint,
                       strictness=_week_strictness(week))


TS_EXAM_ALTERNATES = {
    # ------------------------------------------------------------ Month 1
    1: _alt(1, "inches", "Length table",
        "The input is a line of lengths in inches (whole numbers). For each one print `in=cm` where cm is "
        "`in * 2.54`, one per line, then the total of all the centimetre values on the last line.",
        r'''
const lengths = input.split(/\s+/).map(Number);
let total = 0;
for (const inches of lengths) {
  const cm = inches * 2.54;
  total += cm;
  console.log(inches + "=" + cm);
}
console.log(total);
''', ["1 2", "0", "12", "-3 3", "10 20 30", "100", "7", "1 1 1 1"],
        hint="Split on whitespace, convert with `Number`, and keep a running total declared with `let`."),

    2: _alt(2, "parking", "Parking fee",
        "The input is `hours weekend` — a whole number of hours and `yes` or `no`. On a weekday the first "
        "hour is free, then each extra hour costs 4, capped at 20. At the weekend any stay costs a flat 6, "
        "and a stay of 0 hours costs nothing on any day. Print the fee, then `weekend` or `weekday`.",
        r'''
const [hoursRaw, weekendRaw] = input.split(/\s+/);
const hours = Number(hoursRaw);
const weekend = weekendRaw === "yes";
let fee = 0;
if (hours > 0) {
  if (weekend) fee = 6;
  else fee = Math.min(20, (hours - 1) * 4);
}
console.log(fee);
console.log(weekend ? "weekend" : "weekday");
''', ["0 no", "1 no", "2 no", "5 no", "6 no", "10 no", "0 yes", "3 yes", "1 yes"],
        hint="Handle the zero-hour stay first, then branch on the day; `Math.min` applies the cap."),

    3: _alt(3, "digits", "Digit report",
        "The input is one integer `n` (at least 1). Print four lines: the sum of its digits, the number "
        "with its digits reversed (leading zeros dropped), `yes` or `no` for whether n reads the same "
        "backwards, and how many of its digits are even. Use arithmetic (`%` and division), not strings.",
        r'''
const n = Number(input);
let rest = n;
let digitSum = 0;
let reversed = 0;
let evens = 0;
while (rest > 0) {
  const digit = rest % 10;
  digitSum += digit;
  reversed = reversed * 10 + digit;
  if (digit % 2 === 0) evens++;
  rest = Math.floor(rest / 10);
}
console.log(digitSum);
console.log(reversed);
console.log(reversed === n ? "yes" : "no");
console.log(evens);
''', ["7", "121", "1230", "9999", "10", "123456", "1", "1001"],
        hint="`n % 10` is the last digit and `Math.floor(n / 10)` drops it; build the reverse as you go."),

    4: _alt(4, "mirror", "Mirror words",
        "The input is a line of lowercase words separated by one or more spaces. Print the words each "
        "reversed letter by letter (in their original order), then the words in reverse order, then the "
        "number of vowels (`a e i o u`) in the line — all separated by single spaces.",
        r'''
const words = input.split(/\s+/).filter((w) => w.length > 0);
console.log(words.map((w) => w.split("").reverse().join("")).join(" "));
console.log([...words].reverse().join(" "));
let vowels = 0;
for (const ch of input) {
  if ("aeiou".includes(ch)) vowels++;
}
console.log(vowels);
''', ["hello world", "a", "type script rocks", "level   noon", "xyz", "one two three four",
      "queue", "  padded words here  "],
        hint="`split(\"\")`, `reverse()` and `join(\"\")` reverse one word; spread before reversing the list."),

    # ------------------------------------------------------------ Month 2
    5: _alt(5, "repeat", "Repeat with defaults",
        "The input is `word times sep`, where `times` may be `-` and `sep` may be `none`, meaning \"use "
        "the default\". Write `repeat(word, times?, sep?)` with `times` defaulting to 2 and `sep` to `-`, "
        "returning `word` repeated `times` times joined by `sep` (an empty string for 0). Print `repeat` "
        "applied to the input, then `repeat(word)`.",
        r'''
const [word = "", timesRaw, sepRaw] = input.split(/\s+/);
function repeat(word: string, times = 2, sep = "-"): string {
  const parts: string[] = [];
  for (let i = 0; i < times; i++) parts.push(word);
  return parts.join(sep);
}
const times = timesRaw === "-" ? undefined : Number(timesRaw);
const sep = sepRaw === "none" ? undefined : sepRaw;
console.log(repeat(word, times, sep));
console.log(repeat(word));
''', ["ab 3 +", "go - none", "x 0 ,", "hi 1 none", "na 4 none", "yo - *", "z 5 .", "echo 2 ~"],
        hint="Passing `undefined` for a parameter uses its default — so map `-` and `none` to `undefined`."),

    6: _alt(6, "numbers", "Compose a number pipeline",
        "The input is a line of integers. Build a `pipe` helper that composes `(xs: number[]) => number[]` "
        "transforms left to right, then apply: drop the negatives, double each value, keep those under 50. "
        "Print the result space-separated (or `(none)`), then how many values the pipeline removed.",
        r'''
const nums = input.split(/\s+/).map(Number);
type Step = (xs: number[]) => number[];
function pipe(...steps: Step[]): Step {
  return (start) => steps.reduce((acc, step) => step(acc), start);
}
const run = pipe(
  (xs) => xs.filter((x) => x >= 0),
  (xs) => xs.map((x) => x * 2),
  (xs) => xs.filter((x) => x < 50),
);
const out = run(nums);
console.log(out.join(" ") || "(none)");
console.log(nums.length - out.length);
''', ["1 2 3", "-1 -2", "30 10 -5 24", "0", "25 24", "5 -5 5 -5", "100 1", "12 13 -14 15"],
        hint="`reduce` over the steps, starting from the input array, applies them in order."),

    7: _alt(7, "report", "Array report",
        "The input is a line of numbers. Print, one per line: the minimum, the median (the mean of the two "
        "middle values when the count is even), the values that appear more than once in ascending order "
        "space-separated (or `(none)`), and the input reversed — without mutating the input for the "
        "earlier answers.",
        r'''
const nums = input.split(/\s+/).map(Number);
const sorted = nums.toSorted((a, b) => a - b);
const mid = Math.floor(sorted.length / 2);
const median =
  sorted.length % 2 === 1 ? sorted[mid]! : (sorted[mid - 1]! + sorted[mid]!) / 2;
const repeated = sorted.filter((x, i) => sorted.indexOf(x) !== i && sorted.indexOf(x) === i - 1);
console.log(Math.min(...nums));
console.log(median);
console.log(repeated.join(" ") || "(none)");
console.log(nums.toReversed().join(" "));
''', ["1 2 3 4", "5", "3 1 3 2 1", "7 7 7", "10 -2 4", "2 8", "9 1 5 1 9 9", "0 0 1"],
        hint="`toSorted` and `toReversed` leave the original alone. A value repeats when it equals its neighbour in the sorted copy."),

    8: _alt(8, "inventory", "Merge inventory records",
        "The input is `n` then `n` JSON objects with a `sku`, a `qty` and an optional `price`. Merge them "
        "per sku: quantities add up, and the price is the last one given (0 if none ever was). Print "
        "`sku qty price` per sku in alphabetical order, then the stock value — the sum of qty × price.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
type Entry = { sku: string; qty: number; price?: number };
const merged: { [sku: string]: { qty: number; price: number } } = {};
for (let i = 1; i <= n; i++) {
  const { sku, qty, price }: Entry = JSON.parse(lines[i] ?? "{}");
  const current = merged[sku] ?? { qty: 0, price: 0 };
  merged[sku] = { qty: current.qty + qty, price: price ?? current.price };
}
let value = 0;
for (const sku of Object.keys(merged).sort()) {
  const { qty, price } = merged[sku]!;
  value += qty * price;
  console.log(sku + " " + qty + " " + price);
}
console.log(value);
''', ['2\n{"sku":"b2","qty":3,"price":4}\n{"sku":"a1","qty":1,"price":10}',
      '3\n{"sku":"a1","qty":2}\n{"sku":"a1","qty":1,"price":5}\n{"sku":"a1","qty":4}',
      '1\n{"sku":"z9","qty":0,"price":99}',
      '2\n{"sku":"c3","qty":5}\n{"sku":"b2","qty":1}',
      '3\n{"sku":"a1","qty":1,"price":2}\n{"sku":"a1","qty":1,"price":3}\n{"sku":"b1","qty":2,"price":1}',
      '2\n{"sku":"x","qty":10,"price":1}\n{"sku":"y","qty":1,"price":10}',
      '4\n{"sku":"m","qty":1,"price":1}\n{"sku":"k","qty":2,"price":2}\n{"sku":"m","qty":3}\n{"sku":"k","qty":1,"price":5}',
      '1\n{"sku":"only","qty":7}'],
        hint="Destructure each parsed record; `price ?? current.price` keeps the previous price when one is missing."),

    # ------------------------------------------------------------ Month 3
    9: _alt(9, "friends", "Friends in common",
        "The input is `n` then `n` lines `a b`, each meaning a and b are friends (friendship goes both "
        "ways), then a final line `x y`. Print the friends x and y have in common, sorted and "
        "space-separated (or `(none)`), then the number of distinct people in the friendship list.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
const friends = new Map<string, Set<string>>();
function link(a: string, b: string): void {
  if (!friends.has(a)) friends.set(a, new Set());
  friends.get(a)!.add(b);
}
for (let i = 1; i <= n; i++) {
  const [a = "", b = ""] = (lines[i] ?? "").trim().split(/\s+/);
  link(a, b);
  link(b, a);
}
const [x = "", y = ""] = (lines[n + 1] ?? "").trim().split(/\s+/);
const ofX = friends.get(x) ?? new Set<string>();
const ofY = friends.get(y) ?? new Set<string>();
const common = [...ofX].filter((p) => ofY.has(p)).sort();
console.log(common.join(" ") || "(none)");
console.log(friends.size);
''', ["3\nann bob\nann cat\nbob cat\nann bob",
      "2\nann bob\ncat dan\nann cat",
      "4\na c\nb c\na d\nb d\na b",
      "1\na b\nx y",
      "3\nmia leo\nleo zoe\nzoe mia\nmia zoe",
      "5\np q\np r\np s\nt q\nt r\np t",
      "2\nsolo pal\npal solo\nsolo pal",
      "3\na b\nb c\nc d\na c"],
        hint="A `Map<string, Set<string>>` of friends; the common ones are one set filtered by `has` on the other."),

    10: _alt(10, "turnstile", "Turnstile machine",
        "A turnstile is `locked` or `unlocked`; events are `coin` and `push`. A coin unlocks a locked "
        "turnstile (and is kept); a coin in an unlocked one is refunded; a push through an unlocked one "
        "locks it; a push on a locked one does nothing. The input is a start state then events. Print the "
        "state after each event (`ignored <word>` for anything that is not an event, leaving the state as "
        "it was), then the number of coins kept.",
        r'''
const [start, ...events] = input.split(/\s+/);
type State = "locked" | "unlocked";
type Event = "coin" | "push";
function isEvent(word: string): word is Event {
  return word === "coin" || word === "push";
}
let state: State = start === "unlocked" ? "unlocked" : "locked";
let kept = 0;
for (const word of events) {
  if (!isEvent(word)) {
    console.log("ignored " + word);
    continue;
  }
  if (state === "locked" && word === "coin") {
    state = "unlocked";
    kept++;
  } else if (state === "unlocked" && word === "push") {
    state = "locked";
  }
  console.log(state);
}
console.log(kept);
''', ["locked coin push", "unlocked coin push push", "locked push push coin",
      "locked coin coin push coin", "unlocked kick push", "locked", "unlocked push coin push coin",
      "locked coin wave push"],
        hint="Two literal unions — the states and the events — and a guard that turns a raw word into an `Event`."),

    11: _alt(11, "sensors", "Clean sensor readings",
        "The input is `n` then `n` JSON lines. A reading is an object with a non-empty string `sensor` and "
        "a `value` that is either a finite number or `null` (a gap). Print `ok <sensor> <value>`, "
        "`gap <sensor>` for a null value, or `bad` for anything else. Then print the largest valid value, "
        "or `none`. Write a type predicate for the reading.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
type Reading = { sensor: string; value: number | null };
function isReading(x: unknown): x is Reading {
  if (typeof x !== "object" || x === null) return false;
  const r = x as { sensor?: unknown; value?: unknown };
  return (
    typeof r.sensor === "string" && r.sensor.length > 0 &&
    (r.value === null || (typeof r.value === "number" && Number.isFinite(r.value)))
  );
}
let best: number | undefined;
for (let i = 1; i <= n; i++) {
  const parsed: unknown = JSON.parse(lines[i] ?? "null");
  if (!isReading(parsed)) {
    console.log("bad");
  } else if (parsed.value === null) {
    console.log("gap " + parsed.sensor);
  } else {
    console.log("ok " + parsed.sensor + " " + parsed.value);
    best = best === undefined ? parsed.value : Math.max(best, parsed.value);
  }
}
console.log(best ?? "none");
''', ['3\n{"sensor":"t1","value":20.5}\n{"sensor":"t2","value":null}\n{"sensor":"","value":3}',
      '2\n{"sensor":"a","value":-4}\n{"sensor":"b","value":-1}',
      '1\n{"value":5}',
      '2\n[1,2]\n"t1"',
      '3\n{"sensor":"x","value":"7"}\n{"sensor":"y","value":0}\n{"sensor":"z","value":null}',
      '1\n{"sensor":"solo","value":null}',
      '4\n{"sensor":"a","value":1}\n{"sensor":"b","value":3}\n{"sensor":"c","value":2}\nnull',
      '2\n{"sensor":"q","value":true}\n{"sensor":"r","value":12}'],
        hint="Parse into `unknown`; the predicate checks `sensor` and both allowed forms of `value`."),

    12: _alt(12, "shapes", "Drawing commands",
        "Commands are `circle r`, `rect w h`, `square s` and `clear` (remove every shape drawn so far). "
        "Model the shapes as a discriminated union. The input is `n` then `n` commands. Print each shape "
        "left at the end as `<kind> <area>` with the area to 2 decimal places (π from `Math.PI`), then the "
        "total area to 2 places — or `(empty)` and `0.00` when nothing is left.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number }
  | { kind: "square"; s: number };
function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.r * shape.r;
    case "rect":
      return shape.w * shape.h;
    case "square":
      return shape.s * shape.s;
  }
}
let shapes: Shape[] = [];
for (let i = 1; i <= n; i++) {
  const [cmd, a = "0", b = "0"] = (lines[i] ?? "").trim().split(/\s+/);
  if (cmd === "circle") shapes.push({ kind: "circle", r: Number(a) });
  else if (cmd === "rect") shapes.push({ kind: "rect", w: Number(a), h: Number(b) });
  else if (cmd === "square") shapes.push({ kind: "square", s: Number(a) });
  else if (cmd === "clear") shapes = [];
}
let total = 0;
for (const shape of shapes) {
  total += area(shape);
  console.log(shape.kind + " " + area(shape).toFixed(2));
}
if (shapes.length === 0) console.log("(empty)");
console.log(total.toFixed(2));
''', ["2\ncircle 1\nsquare 2", "3\nrect 2 3\nclear\nsquare 1", "1\nclear", "2\ncircle 2\ncircle 0.5",
      "3\nsquare 3\nrect 1 1\ncircle 1", "4\nrect 10 2\nclear\nclear\nrect 1 2", "1\nrect 4 0.25",
      "2\nsquare 0\ncircle 3"],
        hint="`switch` on `kind` gives each branch the right fields; `toFixed(2)` formats."),

    13: _alt(13, "letters", "Checkpoint: letter frequency report",
        "The input is a line of text. Counting letters only, case-insensitively, print the three most "
        "frequent letters as `letter=count`, one per line, breaking ties alphabetically; then the number "
        "of distinct letters. Fewer than three distinct letters prints only what exists.",
        r'''
const counts = new Map<string, number>();
for (const ch of input.toLowerCase()) {
  if (ch >= "a" && ch <= "z") counts.set(ch, (counts.get(ch) ?? 0) + 1);
}
const ranked = [...counts.entries()].sort((a, b) =>
  b[1] !== a[1] ? b[1] - a[1] : a[0].localeCompare(b[0]),
);
for (const [letter, count] of ranked.slice(0, 3)) {
  console.log(letter + "=" + count);
}
console.log(counts.size);
''', ["banana", "Hello, World!", "aAbB", "xyz", "Mississippi", "aa bb cc dd", "q", "The quick brown fox"],
        hint="A `Map<string, number>` of counts, then sort entries by count descending and letter ascending."),

    # ------------------------------------------------------------ Month 4
    14: _alt(14, "matrix", "Safe matrix lookups",
        "The input is `r c`, then `r` rows of `c` numbers, then a line of queries `row,col`. Treat every "
        "index as possibly missing. Print the value or `(out of range)` per query, then the sum of the "
        "values that were found.",
        r'''
const lines = input.split("\n");
const [r = 0] = (lines[0] ?? "").trim().split(/\s+/).map(Number);
const grid: number[][] = [];
for (let i = 1; i <= r; i++) {
  grid.push((lines[i] ?? "").trim().split(/\s+/).map(Number));
}
let found = 0;
for (const query of (lines[r + 1] ?? "").trim().split(/\s+/)) {
  const [row = -1, col = -1] = query.split(",").map(Number);
  const value = grid[row]?.[col];
  if (value === undefined) {
    console.log("(out of range)");
  } else {
    found += value;
    console.log(value);
  }
}
console.log(found);
''', ["2 2\n1 2\n3 4\n0,0 1,1 2,0", "1 3\n5 6 7\n0,2 0,3", "3 1\n1\n2\n3\n2,0 -1,0",
      "2 3\n1 1 1\n2 2 2\n1,2 0,0 1,3", "1 1\n42\n0,0", "2 2\n-1 -2\n-3 -4\n1,0 0,1 5,5",
      "3 3\n1 2 3\n4 5 6\n7 8 9\n2,2 1,1 0,0 3,3", "2 2\n0 0\n0 0\n0,0 9,9 1,1"],
        hint="`grid[row]?.[col]` is `number | undefined` under `noUncheckedIndexedAccess` — test for `undefined`."),

    15: _alt(15, "status", "Status codes with satisfies",
        "Declare a status table (`ok` → 200, `created` → 201, `notFound` → 404, `teapot` → 418) checked "
        "with `satisfies Record<string, number>`, and derive the name union from it. The input is `n` then "
        "`n` names. Print each code or `unknown` (inherited names like `toString` are unknown), then the "
        "names whose code is 400 or above, sorted and space-separated.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
const statuses = {
  ok: 200,
  created: 201,
  notFound: 404,
  teapot: 418,
} satisfies Record<string, number>;
type StatusName = keyof typeof statuses;
function isStatusName(name: string): name is StatusName {
  return Object.hasOwn(statuses, name);
}
for (let i = 1; i <= n; i++) {
  const name = (lines[i] ?? "").trim();
  console.log(isStatusName(name) ? statuses[name] : "unknown");
}
const errors = (Object.keys(statuses) as StatusName[]).filter((k) => statuses[k] >= 400).sort();
console.log(errors.join(" "));
''', ["2\nok\nteapot", "1\nmissing", "3\ntoString\ncreated\nnotFound", "4\nok\nok\nok\nok",
      "2\nconstructor\nteapot", "1\nOK", "3\nnotFound\ncreated\nhasOwnProperty", "2\n \nok"],
        hint="`Object.hasOwn` rejects inherited keys; a type predicate turns the string into the name union."),

    16: _alt(16, "kelvin", "Branded temperatures",
        "Brand `Kelvin` and `Celsius`. The input is `n` then `n` readings in kelvin. Only a validating "
        "constructor may produce a `Kelvin` (a finite number, not below 0); print `invalid` for any other "
        "line. Convert each valid reading to `Celsius` (K − 273.15) and print it to 2 decimal places; then "
        "print the mean Celsius of the valid readings to 2 places, or `none`.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
declare const brand: unique symbol;
type Kelvin = number & { readonly [brand]: "Kelvin" };
type Celsius = number & { readonly [brand]: "Celsius" };
function toKelvin(raw: number): Kelvin | null {
  return Number.isFinite(raw) && raw >= 0 ? (raw as Kelvin) : null;
}
function toCelsius(k: Kelvin): Celsius {
  return (k - 273.15) as Celsius;
}
const readings: Celsius[] = [];
for (let i = 1; i <= n; i++) {
  const text = (lines[i] ?? "").trim();
  const k = text === "" ? null : toKelvin(Number(text));
  if (k === null) {
    console.log("invalid");
    continue;
  }
  const c = toCelsius(k);
  readings.push(c);
  console.log(c.toFixed(2));
}
const mean = readings.reduce((sum, c) => sum + c, 0) / readings.length;
console.log(readings.length === 0 ? "none" : mean.toFixed(2));
''', ["2\n273.15\n300", "1\n-1", "3\n0\nabc\n373.15", "1\nhot", "2\n310.15\n310.15",
      "4\n1000\n-5\n250\n", "1\n273.15", "3\n5\n10\n15"],
        hint="The constructor returns `Kelvin | null`; nothing else may assert a number into a brand."),

    17: _alt(17, "directory", "A user directory with Pick and Omit",
        "Users are `id|name|email|password` lines after a count `n`; then `m` queries `public <id>` "
        "(the user without `password`), `card <id>` (only `name` and `email`) or anything else. Print a "
        "public view or a card as JSON — keys in the order the type lists them — `no such user <id>`, or "
        "`bad query`. Type the views with `Omit` and `Pick`, and make sure the password really is absent "
        "at runtime. Finally print how many public views were served.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
type User = { id: number; name: string; email: string; password: string };
type PublicUser = Omit<User, "password">;
type Card = Pick<User, "name" | "email">;
const users = new Map<number, User>();
for (let i = 1; i <= n; i++) {
  const [id = "", name = "", email = "", password = ""] = (lines[i] ?? "").split("|");
  users.set(Number(id), { id: Number(id), name, email, password });
}
function publicView({ password: _secret, ...rest }: User): PublicUser {
  return rest;
}
function card(user: User): Card {
  return { name: user.name, email: user.email };
}
const m = Number(lines[n + 1] ?? "0");
let served = 0;
for (let j = 0; j < m; j++) {
  const [kind = "", idText = ""] = (lines[n + 2 + j] ?? "").trim().split(/\s+/);
  if (kind !== "public" && kind !== "card") {
    console.log("bad query");
    continue;
  }
  const user = users.get(Number(idText));
  if (user === undefined) {
    console.log("no such user " + idText);
  } else if (kind === "public") {
    served++;
    console.log(JSON.stringify(publicView(user)));
  } else {
    console.log(JSON.stringify(card(user)));
  }
}
console.log(served);
''', ["2\n1|Ada|ada@x.io|pw1\n2|Alan|alan@x.io|pw2\n3\npublic 1\ncard 2\npublic 3",
      "1\n7|Grace|g@x.io|s3cret\n2\npublic 7\npublic 7",
      "1\n1|A|a@x.io|p\n2\ndelete 1\ncard 1",
      "1\n5|Bo|bo@x.io|x\n0",
      "2\n3|Cy|cy@x.io|a\n4|Di|di@x.io|b\n3\ncard 4\ncard 3\npublic 4",
      "1\n9|Ed|ed@x.io|z\n1\ncard 10",
      "3\n1|a|a@a|1\n2|b|b@b|2\n3|c|c@c|3\n3\npublic 3\npublic 2\npublic 1",
      "1\n2|Fay|fay@x.io|q\n2\n  public 2  \nshow 2"],
        hint="`Omit` changes only the type; a rest destructure (`{ password, ...rest }`) removes the key at runtime."),

    # ------------------------------------------------------------ Month 5
    18: _alt(18, "partition", "Generic partition and top-k",
        "Write generic `partition<T>(items, keep)` returning `[kept, rest]` and `topBy<T>(items, k, score, tie)`. "
        "The input is `n` then `n` lines `name score`. Print the names scoring 50 or more in input order "
        "(or `(none)`), then the others (or `(none)`), then the top two by score as `name:score` "
        "space-separated, ties broken by name.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
type Entry = { name: string; score: number };
function partition<T>(items: readonly T[], keep: (item: T) => boolean): [T[], T[]] {
  const kept: T[] = [];
  const rest: T[] = [];
  for (const item of items) (keep(item) ? kept : rest).push(item);
  return [kept, rest];
}
function topBy<T>(items: readonly T[], k: number, score: (item: T) => number, tie: (a: T, b: T) => number): T[] {
  return [...items].sort((a, b) => score(b) - score(a) || tie(a, b)).slice(0, k);
}
const entries: Entry[] = [];
for (let i = 1; i <= n; i++) {
  const [name = "", score = "0"] = (lines[i] ?? "").trim().split(/\s+/);
  entries.push({ name, score: Number(score) });
}
const [pass, fail] = partition(entries, (e) => e.score >= 50);
console.log(pass.map((e) => e.name).join(" ") || "(none)");
console.log(fail.map((e) => e.name).join(" ") || "(none)");
const top = topBy(entries, 2, (e) => e.score, (a, b) => a.name.localeCompare(b.name));
console.log(top.map((e) => e.name + ":" + e.score).join(" "));
''', ["3\nann 70\nbob 40\ncat 90", "1\nsolo 50", "2\nx 10\ny 20", "4\na 80\nb 80\nc 80\nd 10",
      "3\nzed 99\namy 99\nbo 1", "2\nlow 0\nhigh 100", "5\nq 55\nr 45\ns 65\nt 35\nu 75", "1\nnobody 49"],
        hint="`partition` returns a tuple type `[T[], T[]]`; `topBy` sorts a copy with a score function."),

    19: _alt(19, "tokens", "Theme tokens from one source of truth",
        "Declare defaults `primary: \"#3366ff\"`, `radius: 4`, `dark: false`, and derive the token names "
        "with `keyof typeof`. The input is `n` then `n` overrides `key=value`. An override applies only if "
        "the key is a token (not an inherited name) and the value parses to the default's runtime type "
        "(a number for `radius`, `true`/`false` for `dark`, any text for `primary`). Print `set <key>`, "
        "`unknown <key>` or `bad value <key>` per line, then every token as `key=value` sorted by key.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
const defaults = { primary: "#3366ff", radius: 4, dark: false };
type Tokens = typeof defaults;
type Token = keyof Tokens;
const tokens: Tokens = { ...defaults };
function isToken(key: string): key is Token {
  return Object.hasOwn(defaults, key);
}
for (let i = 1; i <= n; i++) {
  const line = (lines[i] ?? "").trim();
  const eq = line.indexOf("=");
  const key = eq < 0 ? line : line.slice(0, eq);
  const raw = eq < 0 ? "" : line.slice(eq + 1);
  if (!isToken(key)) {
    console.log("unknown " + key);
    continue;
  }
  if (key === "radius") {
    const num = Number(raw);
    if (raw === "" || !Number.isFinite(num)) {
      console.log("bad value " + key);
      continue;
    }
    tokens.radius = num;
  } else if (key === "dark") {
    if (raw !== "true" && raw !== "false") {
      console.log("bad value " + key);
      continue;
    }
    tokens.dark = raw === "true";
  } else {
    tokens.primary = raw;
  }
  console.log("set " + key);
}
for (const key of (Object.keys(tokens) as Token[]).sort()) {
  console.log(key + "=" + String(tokens[key]));
}
''', ["2\nradius=8\ndark=true", "1\ncolor=red", "2\nradius=big\ndark=yes", "1\ntoString=x",
      "3\nprimary=#000\nprimary=#fff\nradius=0", "0", "2\ndark=false\nradius=-2", "1\nradius="],
        hint="`Object.hasOwn` plus a type predicate narrows a string to a token name; each branch knows its value type."),

    20: _alt(20, "changes", "Which fields changed",
        "`Changes<T>` maps every key of `T` to `boolean`. The input is two JSON objects on two lines with "
        "the same keys (values are strings, numbers or booleans). Build the `Changes` record at runtime and "
        "print `key: changed` or `key: same` for every key in sorted order, then how many changed.",
        r'''
const [beforeText = "{}", afterText = "{}"] = input.split("\n");
type Changes<T> = { [K in keyof T]: boolean };
type Flat = Record<string, string | number | boolean>;
function diff<T extends Flat>(before: T, after: T): Changes<T> {
  const out = {} as Changes<T>;
  for (const key of Object.keys(before) as (keyof T)[]) {
    out[key] = before[key] !== after[key];
  }
  return out;
}
const changes = diff(JSON.parse(beforeText) as Flat, JSON.parse(afterText) as Flat);
let changed = 0;
for (const key of Object.keys(changes).sort()) {
  const flag = changes[key];
  if (flag) changed++;
  console.log(key + ": " + (flag ? "changed" : "same"));
}
console.log(changed);
''', ['{"a":1,"b":2}\n{"a":1,"b":3}', '{"name":"x"}\n{"name":"x"}', '{"on":true,"n":0}\n{"on":false,"n":0}',
      '{"z":"1","y":1}\n{"z":1,"y":"1"}', '{"k":"v","m":"w","l":"u"}\n{"k":"V","m":"w","l":"U"}',
      '{"only":0}\n{"only":1}', '{"a":true,"b":true}\n{"a":true,"b":true}', '{"q":1.5,"r":2}\n{"q":1.5,"r":2.5}'],
        hint="A mapped type over `keyof T` gives the shape; build it key by key, comparing with `!==`."),

    21: _alt(21, "flatten", "Flatten and drop the gaps",
        "Write `Flat<T>` (the element type of an array, else `T`) and use `Exclude` to drop `null`. The "
        "input is a JSON array whose items are numbers, `null`, or arrays of numbers and `null` (one level "
        "deep). Flatten it one level, drop the nulls, and print the first value (or `(none)`), the values "
        "space-separated (or `(none)`), and their sum.",
        r'''
type Flat<T> = T extends readonly (infer U)[] ? U : T;
type Item = number | null | (number | null)[];
function flatten<T>(items: readonly T[]): Flat<T>[] {
  const out: Flat<T>[] = [];
  for (const item of items) {
    if (Array.isArray(item)) out.push(...(item as Flat<T>[]));
    else out.push(item as Flat<T>);
  }
  return out;
}
function dropNull<T>(items: readonly T[]): Exclude<T, null>[] {
  return items.filter((x): x is Exclude<T, null> => x !== null);
}
const items = JSON.parse(input) as Item[];
const values = dropNull(flatten(items));
console.log(values[0] ?? "(none)");
console.log(values.join(" ") || "(none)");
console.log(values.reduce((a, b) => a + b, 0));
''', ["[1,[2,3],null,4]", "[]", "[null,[null]]", "[[5],[6,null],7]", "[0,[0]]", "[[-1,2],null,[3]]",
      "[9]", "[null,8,[null,1]]"],
        hint="`T extends readonly (infer U)[] ? U : T`; a type predicate on `filter` narrows away `null`."),

    22: _alt(22, "classes", "Utility class names",
        "Colours are `red`, `blue`; sizes are `sm`, `md`, `lg`. Derive `ClassName` as the template literal "
        "`${Color}-${Size}` over `as const` arrays and build the list at runtime. The input is `n` then `n` "
        "candidates. Print `color=<c> size=<s>` for a valid name or `bad` otherwise, then the number of "
        "class names, then the `blue` ones sorted.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
const colors = ["red", "blue"] as const;
const sizes = ["sm", "md", "lg"] as const;
type Color = (typeof colors)[number];
type Size = (typeof sizes)[number];
type ClassName = `${Color}-${Size}`;
const all: ClassName[] = [];
for (const c of colors) {
  for (const s of sizes) all.push(`${c}-${s}`);
}
const known = new Set<string>(all);
function isClassName(text: string): text is ClassName {
  return known.has(text);
}
for (let i = 1; i <= n; i++) {
  const text = (lines[i] ?? "").trim();
  if (isClassName(text)) {
    const [c, s] = text.split("-");
    console.log("color=" + c + " size=" + s);
  } else {
    console.log("bad");
  }
}
console.log(all.length);
console.log(all.filter((x) => x.startsWith("blue-")).sort().join(" "));
''', ["2\nred-sm\nblue-xl", "1\ngreen-md", "3\nblue-lg\nblue-md\nred-lg", "1\nred", "2\nRED-sm\nred-sm",
      "0", "2\nblue-sm-sm\nblue-sm", "1\n-md"],
        hint="`(typeof colors)[number]` is the union; a template literal type crosses the two unions."),

    # ------------------------------------------------------------ Month 6
    23: _alt(23, "stock", "Stock room with invariants",
        "Write a `Stock` class holding a `#counts` map from sku to units, with `add(sku, n)`, `remove(sku, "
        "n)` that refuses to go below zero, and a `total` getter. The input is `n` then `n` commands "
        "(`add sku n`, `remove sku n`). Print `<sku>=<units>` after each successful command or `refused`, "
        "then the total units. Quantities must be positive whole numbers; anything else is refused.",
        r'''
const lines = input.split("\n");
const n = Number(lines[0]);
class Stock {
  #counts = new Map<string, number>();
  add(sku: string, units: number): boolean {
    if (!Number.isInteger(units) || units <= 0) return false;
    this.#counts.set(sku, this.count(sku) + units);
    return true;
  }
  remove(sku: string, units: number): boolean {
    if (!Number.isInteger(units) || units <= 0 || units > this.count(sku)) return false;
    this.#counts.set(sku, this.count(sku) - units);
    return true;
  }
  count(sku: string): number {
    return this.#counts.get(sku) ?? 0;
  }
  get total(): number {
    let sum = 0;
    for (const units of this.#counts.values()) sum += units;
    return sum;
  }
}
const stock = new Stock();
for (let i = 1; i <= n; i++) {
  const [op = "", sku = "", unitsRaw = ""] = (lines[i] ?? "").trim().split(/\s+/);
  const units = Number(unitsRaw);
  const ok = op === "add" ? stock.add(sku, units) : op === "remove" ? stock.remove(sku, units) : false;
  console.log(ok ? sku + "=" + stock.count(sku) : "refused");
}
console.log(stock.total);
''', ["3\nadd a 5\nremove a 2\nremove a 9", "1\nremove x 1", "2\nadd b 0\nadd b -3",
      "4\nadd a 1\nadd b 2\nremove a 1\nremove b 2", "2\nadd c 2.5\nadd c 2", "3\nsell a 1\nadd a 3\nremove a 3",
      "1\nadd big 1000", "3\nadd q 4\nremove q 4\nremove q 1"],
        hint="Keep the map private with `#`; every mutation goes through a method that checks the invariant first."),

    24: _alt(24, "fibonacci", "Lazy Fibonacci filter",
        "Write generators `fibonacci` (1, 1, 2, 3, 5, …, infinite), `filter` and `takeWhile`. The input is "
        "`limit divisor`. Take the Fibonacci numbers below `limit` that are divisible by `divisor` and "
        "print them space-separated (or `(none)`), then how many there were. Nothing infinite may be "
        "materialised.",
        r'''
const [limit = 0, divisor = 1] = input.split(/\s+/).map(Number);
function* fibonacci(): Generator<number> {
  let a = 1;
  let b = 1;
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}
function* filter<T>(source: Iterable<T>, keep: (value: T) => boolean): Generator<T> {
  for (const value of source) if (keep(value)) yield value;
}
function* takeWhile<T>(source: Iterable<T>, ok: (value: T) => boolean): Generator<T> {
  for (const value of source) {
    if (!ok(value)) return;
    yield value;
  }
}
const picked = [...filter(takeWhile(fibonacci(), (x) => x < limit), (x) => x % divisor === 0)];
console.log(picked.join(" ") || "(none)");
console.log(picked.length);
''', ["100 2", "10 1", "1 1", "1000 5", "50 7", "2 1", "10000 3", "144 144"],
        hint="`takeWhile` must stop the infinite source before `filter` sees it — the order of the wrappers matters."),

    25: _alt(25, "durations", "Parse a list of durations",
        "Each input line is a duration made of number-unit pairs: `90s`, `5m`, `2h`, `1h30m`, `1h5m10s` "
        "(units `h`, `m`, `s`, each at most once, in that order). Parse every line into seconds with a "
        "`Result`; blank lines are skipped. Print `line <k>: <seconds>` for a good line or "
        "`line <k>: error <message>` for a bad one (`empty`, `bad token <t>`, `unit order`), numbering "
        "lines from 1 — collect every error rather than stopping at the first — then `total <seconds>` "
        "over the good lines and `errors <count>`.",
        r'''
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
const UNIT_SECONDS = { h: 3600, m: 60, s: 1 } as const;
type Unit = keyof typeof UNIT_SECONDS;
const ORDER: readonly Unit[] = ["h", "m", "s"];
function parseDuration(text: string): Result<number> {
  if (text === "") return { ok: false, error: "empty" };
  let rest = text;
  let seconds = 0;
  let lastIndex = -1;
  while (rest.length > 0) {
    const match = /^(\d+)([a-z]?)/.exec(rest);
    const digits = match?.[1];
    const unit = match?.[2] ?? "";
    if (match === null || digits === undefined || !Object.hasOwn(UNIT_SECONDS, unit)) {
      return { ok: false, error: `bad token ${rest}` };
    }
    const index = ORDER.indexOf(unit as Unit);
    if (index <= lastIndex) return { ok: false, error: "unit order" };
    lastIndex = index;
    seconds += Number(digits) * UNIT_SECONDS[unit as Unit];
    rest = rest.slice(match[0].length);
  }
  return { ok: true, value: seconds };
}
let total = 0;
let errors = 0;
input.split("\n").forEach((raw, i) => {
  const text = raw.trim();
  if (text === "") return;
  const result = parseDuration(text);
  if (result.ok) {
    total += result.value;
    console.log(`line ${i + 1}: ${result.value}`);
  } else {
    errors++;
    console.log(`line ${i + 1}: error ${result.error}`);
  }
});
console.log(`total ${total}`);
console.log(`errors ${errors}`);
''', ["90s\n5m\n2h", "1h30m\n1h5m10s", "5x\n10", "30m1h", "2h\n\n45s", "1h1h", "0s\n3m", "12m30s\nabc\n1h"],
        hint="Match one `digits+unit` pair at a time from the front; remember the last unit's position to enforce the order."),

    26: _alt(26, "timeouts", "Race each load against a timeout",
        "`task(id)` resolves to `id * id` after `id * 10` ms. The input is a timeout `t` in ms, then ids. "
        "Race every task against its own `t`-ms timeout, all at once, and turn each outcome into a "
        "`Result`. Print `id=value` or `id=timeout` in input order, then how many finished in time. "
        "(No test has a task that takes exactly `t` ms.)",
        r'''
const [t = 0, ...ids] = input.split(/\s+/).map(Number);
type Result<T> = { ok: true; value: T } | { ok: false; error: string };
function task(id: number): Promise<number> {
  return new Promise<number>((resolve) => setTimeout(() => resolve(id * id), id * 10));
}
function timeout(ms: number): Promise<never> {
  return new Promise<never>((_, reject) => setTimeout(() => reject(new Error("timeout")), ms));
}
async function attempt(id: number): Promise<Result<number>> {
  try {
    return { ok: true, value: await Promise.race([task(id), timeout(t)]) };
  } catch (e) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}
async function main(): Promise<void> {
  const results = await Promise.all(ids.map(attempt));
  let inTime = 0;
  results.forEach((r, i) => {
    if (r.ok) inTime++;
    console.log(`${ids[i]}=${r.ok ? r.value : "timeout"}`);
  });
  console.log(inTime);
}
main().catch((e: unknown) => console.log(String(e)));
''', ["25 1 2 3", "5 1", "45 4 1 2", "100 3 6 9", "15 2 1", "35 5 4 3 2 1", "65 7 1 6", "3 0 2"],
        hint="`Promise.race([task, timeout])` per id, inside a `try`, turns into a `Result`; `Promise.all` keeps input order."),
}
