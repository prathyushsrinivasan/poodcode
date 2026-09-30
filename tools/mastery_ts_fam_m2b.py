# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter practice families, Month 2, weeks 7-8
# (TS_MASTERY_ROADMAP X-19): four families of five for each of the array
# methods, tuples, modern arrays, destructuring, objects, JSON, interfaces and
# index-signature chapters. Each base problem practises one facet of its
# chapter; each twist changes one dimension of it. The week families in
# mastery_ts_families.py (`positions`, `staff`) are not repeated.
#
# Weeks 7-8 run at `strict`; the scope lint keeps week 7 free of `interface`,
# `JSON` and `try`. Helpers are in mastery_ts_chapter_kit.py; exec()'d by
# gen_seed.py with the other tools/mastery_ts_*.py content files.
# ---------------------------------------------------------------------------

# ── ts_array_methods (week 7) ───────────────────────────────────────────────

_M2B_CART = "pen 1.50 4\ncup 4.25 2\nink 12 1"
_M2B_CART_BIG = "desk 120 1\nlamp 18.50 2\npen 1.25 10"

_xfam("ts_array_methods", "cart", "A shopping cart", [
    ("", "Each line is `name price qty`. Print the cart's total cost — the sum of price × qty — with two decimals. Use `map` and `reduce`.",
     r'''
const costs = input.split("\n").map((line) => {
  const [, price, qty] = line.trim().split(/\s+/);
  return Number(price) * Number(qty);
});
console.log(costs.reduce((sum, c) => sum + c, 0).toFixed(2));
''', [_M2B_CART, "gum 0.99 3", _M2B_CART_BIG]),
    ("a receipt", "Each line is `name price qty`. Print one line per item, `<name> x<qty> <cost>`, then `total <sum>` — costs and total with two decimals.",
     r'''
const items = input.split("\n").map((line) => {
  const [name = "", price = "0", qty = "0"] = line.trim().split(/\s+/);
  return { name, qty: Number(qty), cost: Number(price) * Number(qty) };
});
for (const it of items) console.log(`${it.name} x${it.qty} ${it.cost.toFixed(2)}`);
console.log(`total ${items.reduce((sum, it) => sum + it.cost, 0).toFixed(2)}`);
''', [_M2B_CART, "gum 0.99 3"]),
    ("nothing bought", "Each line is `name price qty`, and some quantities are 0. Print `bought: <names>` — the items with a quantity above 0, comma-separated in input order, or `bought: nothing` — then `total <sum>` with two decimals.",
     r'''
const items = input.split("\n").map((line) => {
  const [name = "", price = "0", qty = "0"] = line.trim().split(/\s+/);
  return { name, cost: Number(price) * Number(qty), qty: Number(qty) };
});
const bought = items.filter((it) => it.qty > 0);
console.log(`bought: ${bought.length > 0 ? bought.map((it) => it.name).join(",") : "nothing"}`);
console.log(`total ${bought.reduce((sum, it) => sum + it.cost, 0).toFixed(2)}`);
''', ["tea 3 0\nmug 7.5 2\njam 2 0", "tea 3 0", _M2B_CART]),
    ("a bulk discount", "Each line is `name price qty`. A line whose cost is 20 or more gets 10% off that line. Print `saved <amount>` and then `total <sum after discounts>`, both with two decimals, on two lines.",
     r'''
const costs = input.split("\n").map((line) => {
  const [, price, qty] = line.trim().split(/\s+/);
  return Number(price) * Number(qty);
});
const saved = costs.filter((c) => c >= 20).reduce((sum, c) => sum + c * 0.1, 0);
const total = costs.reduce((sum, c) => sum + c, 0) - saved;
console.log(`saved ${saved.toFixed(2)}`);
console.log(`total ${total.toFixed(2)}`);
''', [_M2B_CART, _M2B_CART_BIG, "gum 0.99 3"]),
    ("the biggest line", "Each line is `name price qty`. Print the line with the highest cost as `biggest <name> <cost>` (the first one on a tie), then `total <sum>` — both amounts with two decimals. Find the biggest with `reduce`.",
     r'''
const items = input.split("\n").map((line) => {
  const [name = "", price = "0", qty = "0"] = line.trim().split(/\s+/);
  return { name, cost: Number(price) * Number(qty) };
});
const biggest = items.reduce((best, it) => (it.cost > best.cost ? it : best), items[0]);
console.log(`biggest ${biggest.name} ${biggest.cost.toFixed(2)}`);
console.log(`total ${items.reduce((sum, it) => sum + it.cost, 0).toFixed(2)}`);
''', [_M2B_CART, _M2B_CART_BIG, "a 2 5\nb 5 2"]),
])

_xfam("ts_array_methods", "sensors", "Sensor checks", [
    ("", "The input is sensor readings separated by spaces. A good reading is between 0 and 100 inclusive. Print `all ok`, or `first bad: <reading>` for the first reading out of range. Use `find`.",
     r'''
const readings = input.split(/\s+/).map(Number);
const bad = readings.find((r) => r < 0 || r > 100);
console.log(bad === undefined ? "all ok" : `first bad: ${bad}`);
''', ["12 50 99", "12 150 -3", "100 0"]),
    ("where it went wrong", "The input is sensor readings separated by spaces; a good reading is between 0 and 100 inclusive. Print `all ok`, or `first bad: <reading> at <index>` with the 0-based index of the first bad one. Use `findIndex`.",
     r'''
const readings = input.split(/\s+/).map(Number);
const i = readings.findIndex((r) => r < 0 || r > 100);
console.log(i < 0 ? "all ok" : `first bad: ${readings[i]} at ${i}`);
''', ["12 50 99", "12 150 -3", "-1"]),
    ("unreadable readings", "The input is sensor readings separated by spaces, but a sensor may report a word such as `err` instead of a number. A reading is bad if it is not a number or is outside 0-100. Print `all ok`, or `first bad: <reading as written> at <index>`.",
     r'''
const readings = input.split(/\s+/);
const isBad = (r: string) => {
  const n = Number(r);
  return Number.isNaN(n) || n < 0 || n > 100;
};
const i = readings.findIndex(isBad);
console.log(i < 0 ? "all ok" : `first bad: ${readings[i]} at ${i}`);
''', ["12 err 150", "5 6 7", "7 101 err"]),
    ("limits from the input", "Line 1 is `min max`; line 2 is the readings. Print `all ok` if `every` reading is within min-max inclusive; otherwise print `<k> bad` (how many) and then `first bad: <reading> at <index>`.",
     r'''
const [limits = "", line = ""] = input.split("\n");
const [min, max] = limits.split(/\s+/).map(Number);
const readings = line.split(/\s+/).map(Number);
const ok = (r: number) => r >= min && r <= max;
if (readings.every(ok)) {
  console.log("all ok");
} else {
  const i = readings.findIndex((r) => !ok(r));
  console.log(`${readings.filter((r) => !ok(r)).length} bad`);
  console.log(`first bad: ${readings[i]} at ${i}`);
}
''', ["10 20\n10 15 20", "10 20\n5 15 25 30", "-5 5\n0 -5 6"]),
    ("many sensors", "Each line is `name r1 r2 ...`; a good reading is 0-100 inclusive. For each sensor print `<name>: ok` or `<name>: <k> bad, first at <index>` (0-based among its readings). Then print `all sensors ok` if every sensor is fine, else `<n> sensors need attention`.",
     r'''
const bad = (r: number) => r < 0 || r > 100;
const sensors = input.split("\n").map((line) => {
  const [name = "", ...rest] = line.trim().split(/\s+/);
  return { name, readings: rest.map(Number) };
});
for (const s of sensors) {
  const i = s.readings.findIndex(bad);
  console.log(i < 0 ? `${s.name}: ok` : `${s.name}: ${s.readings.filter(bad).length} bad, first at ${i}`);
}
const failing = sensors.filter((s) => s.readings.some(bad)).length;
console.log(failing === 0 ? "all sensors ok" : `${failing} sensors need attention`);
''', ["t1 10 20 30\nt2 5 150 -2 7\nt3 101", "solo 50 60"]),
])

_xfam("ts_array_methods", "votes", "Counting votes", [
    ("", "The input is votes, one name per word. Tally them with `reduce` into a `Record<string, number>` and print the winner as `<name> <count>`; on a tie, the name that comes first alphabetically.",
     r'''
const tally = input.split(/\s+/).reduce<Record<string, number>>((acc, v) => {
  acc[v] = (acc[v] ?? 0) + 1;
  return acc;
}, {});
const [winner, count] = Object.entries(tally).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(`${winner} ${count}`);
''', ["ts go ts rust ts go", "go rust", "zig"]),
    ("the full table", "The input is votes, one name per word. Print every name with its count, `<name> <count>`, one per line — most votes first, ties alphabetical.",
     r'''
const tally = input.split(/\s+/).reduce<Record<string, number>>((acc, v) => {
  acc[v] = (acc[v] ?? 0) + 1;
  return acc;
}, {});
const rows = Object.entries(tally).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
for (const [name, n] of rows) console.log(`${name} ${n}`);
''', ["ts go ts rust ts go", "b a c a"]),
    ("mixed case", "The input is votes, one name per word, but people type names in any case: `Ada`, `ada` and `ADA` are the same vote. Print the winner in lower case as `<name> <count>`; ties alphabetical.",
     r'''
const tally = input.split(/\s+/).reduce<Record<string, number>>((acc, v) => {
  const key = v.toLowerCase();
  acc[key] = (acc[key] ?? 0) + 1;
  return acc;
}, {});
const [winner, count] = Object.entries(tally).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(`${winner} ${count}`);
''', ["Ada bo ADA Bo bo", "Zed zed ZED", "x Y"]),
    ("a majority rule", "The input is votes, one name per word. The leader (most votes, ties alphabetical) wins only with more than half of all votes. Print `<name> wins with <count> of <total>`, or `no majority: <name> leads with <count> of <total>`.",
     r'''
const votes = input.split(/\s+/);
const tally = votes.reduce<Record<string, number>>((acc, v) => {
  acc[v] = (acc[v] ?? 0) + 1;
  return acc;
}, {});
const [name, count] = Object.entries(tally).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
const total = votes.length;
console.log(count * 2 > total ? `${name} wins with ${count} of ${total}` : `no majority: ${name} leads with ${count} of ${total}`);
''', ["ts go ts rust ts", "ts go ts rust ts go", "a b"]),
    ("changed minds", "Each line is `voter choice`. A voter may vote again; their last choice replaces the earlier one. Print the winner as `<name> <count>` (ties alphabetical). Reduce the lines into a `Record` from voter to choice first.",
     r'''
const finalVote = input.split("\n").reduce<Record<string, string>>((acc, line) => {
  const [voter = "", choice = ""] = line.trim().split(/\s+/);
  acc[voter] = choice;
  return acc;
}, {});
const tally = Object.values(finalVote).reduce<Record<string, number>>((acc, v) => {
  acc[v] = (acc[v] ?? 0) + 1;
  return acc;
}, {});
const [winner, count] = Object.entries(tally).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0];
console.log(`${winner} ${count}`);
''', ["ana ts\nbo go\ncy go\nbo ts", "ana ts\nana go", "a x\nb y\nc y\nc x\nb x"]),
])

_M2B_POSTS = "intro|ts,basics\ngenerics|ts,types\nmaps|basics,collections\nsets|collections,ts"

_xfam("ts_array_methods", "tags", "Post tags", [
    ("", "Each line is `title|tag,tag,...`. Print every distinct tag in the order it first appears, comma-separated. `flatMap` the lines into one list of tags.",
     r'''
const tags = input.split("\n").flatMap((line) => (line.split("|")[1] ?? "").split(","));
console.log(tags.filter((t, i) => tags.indexOf(t) === i).join(","));
''', [_M2B_POSTS, "solo|one", "a|x,y\nb|y,x"]),
    ("counted", "Each line is `title|tag,tag,...` (no tag repeats within a post). Print each distinct tag with the number of posts using it as `tag(n)`, alphabetically, separated by spaces.",
     r'''
const tags = input.split("\n").flatMap((line) => (line.split("|")[1] ?? "").split(","));
const distinct = tags.filter((t, i) => tags.indexOf(t) === i).sort();
console.log(distinct.map((t) => `${t}(${tags.filter((x) => x === t).length})`).join(" "));
''', [_M2B_POSTS, "solo|one"]),
    ("untidy tags", "Each line is `title|tag,tag,...`, but tags may have spaces around them or capitals, and a post may have no tags at all (`title|`). Trim and lower-case every tag, ignore empty ones, and print the distinct tags alphabetically, comma-separated — or `no tags`.",
     r'''
const tags = input
  .split("\n")
  .flatMap((line) => (line.split("|")[1] ?? "").split(","))
  .map((t) => t.trim().toLowerCase())
  .filter((t) => t !== "");
const distinct = tags.filter((t, i) => tags.indexOf(t) === i).sort();
console.log(distinct.length > 0 ? distinct.join(",") : "no tags");
''', ["intro| TS , Basics\nmaps|\nsets|ts,collections ", "a|\nb|", "x|B,a,b"]),
    ("popular only", "Each line is `title|tag,tag,...` (no tag repeats within a post). Print only the tags used by two or more posts, alphabetically, comma-separated — or `none`.",
     r'''
const tags = input.split("\n").flatMap((line) => (line.split("|")[1] ?? "").split(","));
const popular = tags.filter((t, i) => tags.indexOf(t) === i && tags.lastIndexOf(t) !== i).sort();
console.log(popular.length > 0 ? popular.join(",") : "none");
''', [_M2B_POSTS, "a|x\nb|y", "a|x,y\nb|y,x\nc|z"]),
    ("a tag index", "Each line is `title|tag,tag,...`. Print one line per tag, alphabetically: `<tag>: <titles>` with the titles that use it comma-separated in input order. Build `[tag, title]` pairs with `flatMap`.",
     r'''
const pairs = input.split("\n").flatMap((line) => {
  const [title = "", list = ""] = line.split("|");
  return list.split(",").map((tag) => [tag, title]);
});
const tags = pairs.map(([tag]) => tag).filter((t, i, all) => all.indexOf(t) === i).sort();
for (const tag of tags) {
  console.log(`${tag}: ${pairs.filter(([t]) => t === tag).map(([, title]) => title).join(",")}`);
}
''', [_M2B_POSTS, "solo|one,two"]),
])

# ── ts_tuples (week 7) ──────────────────────────────────────────────────────

_xfam("ts_tuples", "clock", "Clock times", [
    ("", "Each line is a time `HH:MM`. Write `parseTime(text: string): [hours: number, minutes: number]` and, for each line, print `<h>h <m>m = <total> min` where total is the minutes since midnight.",
     r'''
function parseTime(text: string): [hours: number, minutes: number] {
  const [h, m] = text.split(":").map(Number);
  return [h, m];
}
for (const line of input.split("\n")) {
  const [h, m] = parseTime(line.trim());
  console.log(`${h}h ${m}m = ${h * 60 + m} min`);
}
''', ["09:05\n23:59", "00:00", "12:30"]),
    ("optional seconds", "Each line is a time `HH:MM` or `HH:MM:SS`. Write `parseTime(text: string): [hours: number, minutes: number, seconds?: number]` and print the seconds since midnight for each line (missing seconds count as 0).",
     r'''
function parseTime(text: string): [hours: number, minutes: number, seconds?: number] {
  const parts = text.split(":").map(Number);
  const [h, m, s] = parts;
  return parts.length > 2 ? [h, m, s] : [h, m];
}
for (const line of input.split("\n")) {
  const [h, m, s] = parseTime(line.trim());
  console.log((h * 60 + m) * 60 + (s ?? 0));
}
''', ["00:01:05\n01:00", "23:59:59", "00:00"]),
    ("a 12-hour clock", "Each line is a time `HH:MM`. Parse it into `[hours: number, minutes: number]` and print it on a 12-hour clock: `h:MM am` or `h:MM pm`, where `00:30` is `12:30 am` and `12:00` is `12:00 pm`.",
     r'''
function parseTime(text: string): [hours: number, minutes: number] {
  const [h, m] = text.split(":").map(Number);
  return [h, m];
}
for (const line of input.split("\n")) {
  const [h, m] = parseTime(line.trim());
  const hour = h % 12 === 0 ? 12 : h % 12;
  console.log(`${hour}:${String(m).padStart(2, "0")} ${h < 12 ? "am" : "pm"}`);
}
''', ["00:30\n09:05\n12:00\n23:59", "13:07"]),
    ("durations", "Each line is `start end`, two `HH:MM` times. Print the minutes from start to end; an end earlier than the start is on the next day. Parse each time with a function returning `[hours: number, minutes: number]`.",
     r'''
function parseTime(text: string): [hours: number, minutes: number] {
  const [h, m] = text.split(":").map(Number);
  return [h, m];
}
for (const line of input.split("\n")) {
  const [a = "", b = ""] = line.trim().split(/\s+/);
  const [h1, m1] = parseTime(a);
  const [h2, m2] = parseTime(b);
  const diff = h2 * 60 + m2 - (h1 * 60 + m1);
  console.log(diff < 0 ? diff + 24 * 60 : diff);
}
''', ["09:00 17:30\n22:15 01:45", "08:00 08:00", "23:59 00:00"]),
    ("adding minutes", "Each line is `HH:MM +N` or `HH:MM -N`. Write `parseTime` returning `[hours, minutes]` and its inverse `toTime(total: number): [hours: number, minutes: number]`, which wraps around the day. Print the new time as `HH:MM`.",
     r'''
function parseTime(text: string): [hours: number, minutes: number] {
  const [h, m] = text.split(":").map(Number);
  return [h, m];
}
function toTime(total: number): [hours: number, minutes: number] {
  const t = ((total % 1440) + 1440) % 1440;
  return [Math.floor(t / 60), t % 60];
}
const pad = (n: number) => String(n).padStart(2, "0");
for (const line of input.split("\n")) {
  const [time = "", delta = "0"] = line.trim().split(/\s+/);
  const [h, m] = parseTime(time);
  const [nh, nm] = toTime(h * 60 + m + Number(delta));
  console.log(`${pad(nh)}:${pad(nm)}`);
}
''', ["09:05 +70\n23:30 +45", "00:10 -20", "12:00 -1440"]),
])

_xfam("ts_tuples", "calc", "A command row", [
    ("", "Each line is an operation and its numbers: `add 1 2 3`, `mul 2 5` or `max 4 9 2`. Parse each line into `[op: string, ...args: number[]]` and print the result.",
     r'''
type Command = [op: string, ...args: number[]];
function parse(line: string): Command {
  const [op = "", ...rest] = line.trim().split(/\s+/);
  return [op, ...rest.map(Number)];
}
for (const line of input.split("\n")) {
  const [op, ...args] = parse(line);
  if (op === "add") console.log(args.reduce((a, b) => a + b, 0));
  else if (op === "mul") console.log(args.reduce((a, b) => a * b, 1));
  else console.log(Math.max(...args));
}
''', ["add 1 2 3\nmul 2 5\nmax 4 9 2", "max -3 -1", "mul 7"]),
    ("no numbers", "Each line is `add`, `mul` or `max` followed by numbers, parsed into `[op: string, ...args: number[]]` — but a line may have no numbers at all. Print the result, or `<op>: no numbers` for such a line.",
     r'''
type Command = [op: string, ...args: number[]];
function parse(line: string): Command {
  const [op = "", ...rest] = line.trim().split(/\s+/);
  return [op, ...rest.map(Number)];
}
for (const line of input.split("\n")) {
  const [op, ...args] = parse(line);
  if (args.length === 0) console.log(`${op}: no numbers`);
  else if (op === "add") console.log(args.reduce((a, b) => a + b, 0));
  else if (op === "mul") console.log(args.reduce((a, b) => a * b, 1));
  else console.log(Math.max(...args));
}
''', ["add 1 2\nmax\nmul 3 3", "add"]),
    ("show the working", "Each line is `add`, `mul` or `max` followed by numbers, parsed into `[op: string, ...args: number[]]`. Print `<op>(<a>, <b>, ...) = <result>`, the numbers separated by a comma and a space.",
     r'''
type Command = [op: string, ...args: number[]];
function parse(line: string): Command {
  const [op = "", ...rest] = line.trim().split(/\s+/);
  return [op, ...rest.map(Number)];
}
for (const line of input.split("\n")) {
  const [op, ...args] = parse(line);
  const result = op === "add" ? args.reduce((a, b) => a + b, 0) : op === "mul" ? args.reduce((a, b) => a * b, 1) : Math.max(...args);
  console.log(`${op}(${args.join(", ")}) = ${result}`);
}
''', ["add 1 2 3\nmul 2 5\nmax 4 9 2", "max 8"]),
    ("a precision field", "Each line is an operation, a number of decimal places, then numbers: `avg 2 1 2 2`. Parse into `[op: string, places: number, ...args: number[]]`; the operations are `add`, `avg` and `max`. Print the result with that many decimals.",
     r'''
type Command = [op: string, places: number, ...args: number[]];
function parse(line: string): Command {
  const [op = "", places = "0", ...rest] = line.trim().split(/\s+/);
  return [op, Number(places), ...rest.map(Number)];
}
for (const line of input.split("\n")) {
  const [op, places, ...args] = parse(line);
  const sum = args.reduce((a, b) => a + b, 0);
  const result = op === "add" ? sum : op === "avg" ? sum / args.length : Math.max(...args);
  console.log(result.toFixed(places));
}
''', ["avg 2 1 2 2\nadd 1 0.25 0.5\nmax 0 3.7 2", "avg 3 10 20 25"]),
    ("a result tuple", "Each line is an operation (`add`, `mul`, `max`) and numbers, parsed into `[op: string, ...args: number[]]`. Write `run(cmd): [ok: boolean, value: number]`, returning `[false, 0]` for an unknown operation. Print each value, or `error` for an unknown one; then `sum <total of the ok values>`.",
     r'''
type Command = [op: string, ...args: number[]];
function parse(line: string): Command {
  const [op = "", ...rest] = line.trim().split(/\s+/);
  return [op, ...rest.map(Number)];
}
function run([op, ...args]: Command): [ok: boolean, value: number] {
  if (op === "add") return [true, args.reduce((a, b) => a + b, 0)];
  if (op === "mul") return [true, args.reduce((a, b) => a * b, 1)];
  if (op === "max") return [true, Math.max(...args)];
  return [false, 0];
}
let sum = 0;
for (const line of input.split("\n")) {
  const [ok, value] = run(parse(line));
  console.log(ok ? value : "error");
  if (ok) sum += value;
}
console.log(`sum ${sum}`);
''', ["add 1 2 3\ndiv 8 2\nmax 4 9 2", "pow 2 3", "mul 2 5"]),
])

_xfam("ts_tuples", "codes", "Code tables", [
    ("", "Line 1 is `code:city` pairs separated by spaces; line 2 is codes. Turn line 1 into `[string, string][]` pairs, build a `Map` from them, and print the city for each code on its own line — or `? <code>` if it is unknown.",
     r'''
const [table = "", queries = ""] = input.split("\n");
const pairs: [string, string][] = table.split(/\s+/).map((p) => {
  const [code = "", city = ""] = p.split(":");
  return [code, city];
});
const cities = new Map(pairs);
for (const code of queries.split(/\s+/)) console.log(cities.get(code) ?? `? ${code}`);
''', ["uk:London fr:Paris jp:Tokyo\nfr jp de", "no:Oslo\nno"]),
    ("the other way round", "The input is `code:city` pairs separated by spaces. Swap each `[code, city]` pair and print `city=code`, one per line, sorted by city.",
     r'''
const pairs: [string, string][] = input.split(/\s+/).map((p) => {
  const [code = "", city = ""] = p.split(":");
  return [code, city];
});
const swapped = pairs.map(([code, city]): [string, string] => [city, code]).sort((a, b) => a[0].localeCompare(b[0]));
for (const [city, code] of swapped) console.log(`${city}=${code}`);
''', ["uk:London fr:Paris jp:Tokyo", "no:Oslo"]),
    ("repeated codes", "The input is `code:city` pairs separated by spaces, and a code may appear more than once — the later pair wins. Build a `Map` from the pairs and print the final table as `code=city`, one per line, sorted by code.",
     r'''
const pairs: [string, string][] = input.split(/\s+/).map((p) => {
  const [code = "", city = ""] = p.split(":");
  return [code, city];
});
const table = [...new Map(pairs)].sort((a, b) => a[0].localeCompare(b[0]));
for (const [code, city] of table) console.log(`${code}=${city}`);
''', ["uk:London fr:Paris uk:Leeds", "de:Bonn de:Berlin", "a:x"]),
    ("broken pairs", "Line 1 is `code:city` pairs separated by spaces, but some are broken: no `:`, or an empty side. Skip those. Print `skipped <n>`, then for each code on line 2 its city or `? <code>`, one per line.",
     r'''
const [table = "", queries = ""] = input.split("\n");
const all = table.split(/\s+/).map((p) => p.split(":"));
const pairs = all
  .filter((parts) => parts.length === 2 && parts[0] !== "" && parts[1] !== "")
  .map(([code = "", city = ""]): [string, string] => [code, city]);
const cities = new Map(pairs);
console.log(`skipped ${all.length - pairs.length}`);
for (const code of queries.split(/\s+/)) console.log(cities.get(code) ?? `? ${code}`);
''', ["uk:London fr jp: :Rome no:Oslo\nuk no jp", "a:b\na"]),
    ("two lists zipped", "Line 1 is names, line 2 scores, both separated by spaces. Pair them up position by position into `[name: string, score: number]` tuples (ignore extras if one list is longer) and print `name score`, one per line, highest score first, ties by name.",
     r'''
const [a = "", b = ""] = input.split("\n");
const names = a.split(/\s+/);
const scores = b.split(/\s+/).map(Number);
const n = Math.min(names.length, scores.length);
const rows: [name: string, score: number][] = names.slice(0, n).map((name, i) => [name, scores[i]]);
rows.sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0]));
for (const [name, score] of rows) console.log(`${name} ${score}`);
''', ["ana bo cy\n7 9 7", "ana bo cy di\n3 5", "solo\n1 2 3"]),
])

_xfam("ts_tuples", "ranges", "Number ranges", [
    ("", "Each line is two numbers `a b`, in either order. Normalise each into a `readonly [start: number, end: number]` with start <= end, and print `<start>..<end> len <end - start>`.",
     r'''
type Range = readonly [start: number, end: number];
function toRange(a: number, b: number): Range {
  return a <= b ? [a, b] : [b, a];
}
for (const line of input.split("\n")) {
  const [a, b] = line.trim().split(/\s+/).map(Number);
  const [start, end] = toRange(a, b);
  console.log(`${start}..${end} len ${end - start}`);
}
''', ["3 9\n10 2", "5 5", "-4 -8"]),
    ("sorted", "Each line is two numbers `a b`, in either order. Normalise each into `readonly [start, end]` and print all of them on one line, sorted by start then end, each as `[start, end]`, separated by spaces.",
     r'''
type Range = readonly [start: number, end: number];
const ranges: Range[] = input.split("\n").map((line) => {
  const [a, b] = line.trim().split(/\s+/).map(Number);
  return a <= b ? [a, b] : [b, a];
});
const sorted = ranges.toSorted((x, y) => x[0] - y[0] || x[1] - y[1]);
console.log(sorted.map(([s, e]) => `[${s}, ${e}]`).join(" "));
''', ["3 9\n10 2\n3 1", "5 5"]),
    ("overlap", "Each line is `a b c d`: two ranges, each in either order. Print their overlap as `<start>..<end>`, or `none` if they do not meet. Ranges that touch, like `1 3` and `3 5`, overlap at `3..3`.",
     r'''
type Range = readonly [start: number, end: number];
const toRange = (a: number, b: number): Range => (a <= b ? [a, b] : [b, a]);
for (const line of input.split("\n")) {
  const [a, b, c, d] = line.trim().split(/\s+/).map(Number);
  const [s1, e1] = toRange(a, b);
  const [s2, e2] = toRange(c, d);
  const start = Math.max(s1, s2);
  const end = Math.min(e1, e2);
  console.log(start <= end ? `${start}..${end}` : "none");
}
''', ["1 5 3 9\n9 1 2 3", "1 3 3 5", "0 2 5 4"]),
    ("which range", "Line 1 lists ranges as `a-b` (a <= b, non-negative), separated by spaces; line 2 is numbers. Parse the ranges into `readonly [start, end]` tuples. For each number print the 0-based index of the first range containing it (ends included), or `-`; space-separated.",
     r'''
type Range = readonly [start: number, end: number];
const [first = "", second = ""] = input.split("\n");
const ranges: Range[] = first.split(/\s+/).map((r) => {
  const [a, b] = r.split("-").map(Number);
  return [a, b];
});
const answers = second.split(/\s+/).map(Number).map((x) => {
  const i = ranges.findIndex(([s, e]) => x >= s && x <= e);
  return i < 0 ? "-" : String(i);
});
console.log(answers.join(" "));
''', ["1-5 10-12 4-20\n3 11 15 30", "0-0\n0 1"]),
    ("merged", "Each line is two numbers `a b`, in either order. Merge all the ranges that overlap or touch and print the merged ranges sorted by start, each as `<start>..<end>`, separated by spaces.",
     r'''
type Range = readonly [start: number, end: number];
const ranges: Range[] = input.split("\n").map((line) => {
  const [a, b] = line.trim().split(/\s+/).map(Number);
  return a <= b ? [a, b] : [b, a];
});
const merged: Range[] = [];
for (const [s, e] of ranges.toSorted((x, y) => x[0] - y[0])) {
  const last = merged.at(-1);
  if (last !== undefined && s <= last[1]) merged[merged.length - 1] = [last[0], Math.max(last[1], e)];
  else merged.push([s, e]);
}
console.log(merged.map(([s, e]) => `${s}..${e}`).join(" "));
''', ["1 3\n8 6\n2 5\n5 6\n10 12", "4 4", "9 7\n1 2"]),
])

# ── ts_array_modern (week 7) ────────────────────────────────────────────────

_xfam("ts_array_modern", "playlist", "Playlist edits", [
    ("", "Line 1 is a playlist, song names separated by spaces. Each further line is `set <i> <song>`. Apply the edits without mutating any array — use `with` — then print the final playlist and, on a second line, `was: <the original playlist>`.",
     r'''
const [first = "", ...edits] = input.split("\n");
const original = first.split(" ");
let list = original;
for (const edit of edits) {
  const [, i = "0", song = ""] = edit.split(" ");
  list = list.with(Number(i), song);
}
console.log(list.join(" "));
console.log(`was: ${original.join(" ")}`);
''', ["intro verse chorus\nset 1 bridge\nset 0 opener", "solo\nset 0 duet"]),
    ("inserts and deletes", "Line 1 is a playlist; each further line is `set <i> <song>`, `del <i>` or `ins <i> <song>` (insert before position i). Use `with` and `toSpliced` so nothing is mutated; print the final playlist, then `was: <original>`.",
     r'''
const [first = "", ...edits] = input.split("\n");
const original = first.split(" ");
let list = original;
for (const edit of edits) {
  const [cmd, i = "0", song = ""] = edit.split(" ");
  const at = Number(i);
  if (cmd === "set") list = list.with(at, song);
  else if (cmd === "del") list = list.toSpliced(at, 1);
  else list = list.toSpliced(at, 0, song);
}
console.log(list.join(" "));
console.log(`was: ${original.join(" ")}`);
''', ["a b c d\ndel 1\nins 0 z\nset 3 y", "a\nins 1 b\nins 0 c"]),
    ("counting from the end", "Line 1 is a playlist; each further line is `set <i> <song>` or `del <i>`. An index may be negative (`-1` is the last song). An edit whose index is out of range prints `skip <edit>` and changes nothing. Afterwards print the final playlist.",
     r'''
const [first = "", ...edits] = input.split("\n");
let list = first.split(" ");
for (const edit of edits) {
  const [cmd, i = "0", song = ""] = edit.split(" ");
  const at = Number(i);
  if (at < -list.length || at >= list.length) {
    console.log(`skip ${edit}`);
    continue;
  }
  list = cmd === "set" ? list.with(at, song) : list.toSpliced(at, 1);
}
console.log(list.join(" "));
''', ["a b c\nset -1 z\ndel 5\ndel -3", "x y\nset 2 q\nset -2 w"]),
    ("every version", "Line 1 is a playlist; each further line is `set <i> <song>`, `del <i>` or `ins <i> <song>`. Print every version, numbered: `0: <original>`, then `1: <after the first edit>`, and so on.",
     r'''
const [first = "", ...edits] = input.split("\n");
const versions = [first.split(" ")];
for (const edit of edits) {
  const list = versions.at(-1) ?? [];
  const [cmd, i = "0", song = ""] = edit.split(" ");
  const at = Number(i);
  versions.push(cmd === "set" ? list.with(at, song) : cmd === "del" ? list.toSpliced(at, 1) : list.toSpliced(at, 0, song));
}
versions.forEach((v, n) => console.log(`${n}: ${v.join(" ")}`));
''', ["a b c\nset 0 x\ndel 2\nins 1 y", "one\nins 0 zero"]),
    ("undo", "Line 1 is a playlist; each further line is `set <i> <song>`, `del <i>`, `ins <i> <song>` or `undo`. `undo` goes back to the version before the most recent edit still in effect (with nothing to undo, it does nothing). Keep the versions — nothing is mutated — and print the final playlist.",
     r'''
const [first = "", ...edits] = input.split("\n");
let history = [first.split(" ")];
for (const edit of edits) {
  const list = history.at(-1) ?? [];
  if (edit === "undo") {
    if (history.length > 1) history = history.slice(0, -1);
    continue;
  }
  const [cmd, i = "0", song = ""] = edit.split(" ");
  const at = Number(i);
  const next = cmd === "set" ? list.with(at, song) : cmd === "del" ? list.toSpliced(at, 1) : list.toSpliced(at, 0, song);
  history = [...history, next];
}
console.log((history.at(-1) ?? []).join(" "));
''', ["a b c\ndel 0\nset 0 x\nundo\nins 0 z", "a b\nundo\nundo\nset 1 q", "a\nins 0 b\nundo\nundo"]),
])

_xfam("ts_array_modern", "prices", "Price history", [
    ("", "The input is daily prices, oldest first, at least two. Read from the end with `at`: print `last <p> prev <q> change <p - q>`.",
     r'''
const prices = input.split(/\s+/).map(Number);
const last = prices.at(-1) ?? 0;
const prev = prices.at(-2) ?? 0;
console.log(`last ${last} prev ${prev} change ${last - prev}`);
''', ["10 12 11 15", "7 3", "5 5 5"]),
    ("a single day", "The input is daily prices, oldest first — and there may be only one. Print `last <p> prev <q> change <p - q>`, or `last <p> prev none` when there is no previous price.",
     r'''
const prices = input.split(/\s+/).map(Number);
const last = prices.at(-1) ?? 0;
const prev = prices.at(-2);
console.log(prev === undefined ? `last ${last} prev none` : `last ${last} prev ${prev} change ${last - prev}`);
''', ["10 12 11 15", "42", "7 3"]),
    ("the last dip", "The input is daily prices, oldest first. Print the most recent price that is lower than the first price, as `last dip <p> on day <d>` (days count from 1) — or `no dip`. Use `findLast` and `findLastIndex`.",
     r'''
const prices = input.split(/\s+/).map(Number);
const start = prices[0];
const dip = prices.findLast((p) => p < start);
const day = prices.findLastIndex((p) => p < start) + 1;
console.log(dip === undefined ? "no dip" : `last dip ${dip} on day ${day}`);
''', ["10 8 12 9 15", "5 6 7", "3 1 2 4"]),
    ("days since", "Line 1 is a target; line 2 the daily prices, oldest first. Print how many days ago the price was last at or above the target — `0 days ago` if it is today — or `not reached`.",
     r'''
const [t = "0", line = ""] = input.split("\n");
const target = Number(t);
const prices = line.split(/\s+/).map(Number);
const i = prices.findLastIndex((p) => p >= target);
console.log(i < 0 ? "not reached" : `${prices.length - 1 - i} days ago`);
''', ["12\n10 13 11 9", "5\n1 2 5", "100\n1 2 3"]),
    ("a k-day change", "Line 1 is `k`; line 2 the daily prices, oldest first. Print the change over the last k days — the last price minus the price k days before it — as `change over <k> days: <d>`, or `not enough data` when there are not k + 1 prices.",
     r'''
const [kText = "1", line = ""] = input.split("\n");
const k = Number(kText);
const prices = line.split(/\s+/).map(Number);
const last = prices.at(-1);
const before = prices.at(-1 - k);
console.log(last === undefined || before === undefined || k + 1 > prices.length ? "not enough data" : `change over ${k} days: ${last - before}`);
''', ["2\n10 12 11 15", "3\n5 6 7", "3\n1 2 3 4"]),
])

_xfam("ts_array_modern", "seats", "Seat maps", [
    ("", "The input is `rows cols`. Build a seat map with `Array.from` and print it, one line per row: seats are labelled with the row letter (A, B, ...) and the seat number from 1, separated by spaces.",
     r'''
const [rows, cols] = input.split(/\s+/).map(Number);
const map = Array.from({ length: rows }, (_, r) =>
  Array.from({ length: cols }, (_, c) => `${String.fromCharCode(65 + r)}${c + 1}`));
for (const row of map) console.log(row.join(" "));
''', ["2 3", "1 1", "3 2"]),
    ("numbered", "The input is `rows cols`. Number the seats 1, 2, 3, ... across the rows (row by row) and print one line per row, each number padded on the left with spaces to the width of the largest number, separated by single spaces.",
     r'''
const [rows, cols] = input.split(/\s+/).map(Number);
const width = String(rows * cols).length;
const map = Array.from({ length: rows }, (_, r) =>
  Array.from({ length: cols }, (_, c) => String(r * cols + c + 1).padStart(width)));
for (const row of map) console.log(row.join(" "));
''', ["3 4", "1 3", "2 5"]),
    ("taken seats", "Line 1 is `rows cols`; line 2 lists the taken seats, like `A2 B1`. Print the seat map (row letter + seat number from 1, separated by spaces), with `--` in place of each taken seat.",
     r'''
const [size = "", takenLine = ""] = input.split("\n");
const [rows, cols] = size.split(/\s+/).map(Number);
const taken = takenLine.split(/\s+/);
const map = Array.from({ length: rows }, (_, r) =>
  Array.from({ length: cols }, (_, c) => `${String.fromCharCode(65 + r)}${c + 1}`));
for (const row of map) console.log(row.map((s) => (taken.includes(s) ? "--" : s)).join(" "));
''', ["2 3\nA2 B1 B3", "1 2\nC9"]),
    ("an empty hall", "The input is `rows cols`, and either may be 0. Print `no seats` for an empty hall; otherwise print the seat map (row letter + seat number from 1, separated by spaces) followed by a line `<n> seats`.",
     r'''
const [rows, cols] = input.split(/\s+/).map(Number);
const map = Array.from({ length: rows }, (_, r) =>
  Array.from({ length: cols }, (_, c) => `${String.fromCharCode(65 + r)}${c + 1}`));
const seats = map.flat();
if (seats.length === 0) console.log("no seats");
else {
  for (const row of map) console.log(row.join(" "));
  console.log(`${seats.length} seats`);
}
''', ["2 2", "0 5", "3 0"]),
    ("aisles", "The input is `rows cols k`. Print the seat map (row letter + seat number from 1, separated by spaces) with an aisle `|` after every k seats in a row — but not after the last seat.",
     r'''
const [rows, cols, k] = input.split(/\s+/).map(Number);
const map = Array.from({ length: rows }, (_, r) =>
  Array.from({ length: cols }, (_, c) => `${String.fromCharCode(65 + r)}${c + 1}`));
for (const row of map) {
  console.log(row.flatMap((seat, i) => (i > 0 && i % k === 0 ? ["|", seat] : [seat])).join(" "));
}
''', ["2 6 2", "1 5 3", "2 3 3"]),
])

_M2B_ORDERS = "o1 paid 120\no2 draft 15\no3 paid 40\no4 shipped 260\no5 draft 199"

_xfam("ts_array_modern", "orders", "Grouping orders", [
    ("", "Each line is `id status amount`. Group the orders by status with `Object.groupBy` and print `<status>: <ids>`, statuses alphabetically, ids space-separated in input order.",
     r'''
type Order = { id: string; status: string; amount: number };
const orders: Order[] = input.split("\n").map((line) => {
  const [id = "", status = "", amount = "0"] = line.trim().split(/\s+/);
  return { id, status, amount: Number(amount) };
});
const groups = Object.groupBy(orders, (o) => o.status);
for (const status of Object.keys(groups).toSorted()) {
  console.log(`${status}: ${(groups[status] ?? []).map((o) => o.id).join(" ")}`);
}
''', [_M2B_ORDERS, "x1 new 5"]),
    ("totals", "Each line is `id status amount`. Group by status with `Object.groupBy` and print `<status>: <count> orders, <total>` — statuses alphabetically, the total with two decimals.",
     r'''
type Order = { id: string; status: string; amount: number };
const orders: Order[] = input.split("\n").map((line) => {
  const [id = "", status = "", amount = "0"] = line.trim().split(/\s+/);
  return { id, status, amount: Number(amount) };
});
const groups = Object.groupBy(orders, (o) => o.status);
for (const status of Object.keys(groups).toSorted()) {
  const group = groups[status] ?? [];
  console.log(`${status}: ${group.length} orders, ${group.reduce((s, o) => s + o.amount, 0).toFixed(2)}`);
}
''', [_M2B_ORDERS, "x1 new 5.5"]),
    ("no status", "Each line is `id status amount`, but some lines are only `id amount` — group those under `unknown`. Print `<status>: <ids>` as before: statuses alphabetically, ids in input order.",
     r'''
type Order = { id: string; status: string; amount: number };
const orders: Order[] = input.split("\n").map((line) => {
  const parts = line.trim().split(/\s+/);
  const [id = "", status = "unknown", amount = "0"] = parts.length === 2 ? [parts[0], undefined, parts[1]] : parts;
  return { id, status, amount: Number(amount) };
});
const groups = Object.groupBy(orders, (o) => o.status);
for (const status of Object.keys(groups).toSorted()) {
  console.log(`${status}: ${(groups[status] ?? []).map((o) => o.id).join(" ")}`);
}
''', ["o1 paid 120\no2 15\no3 paid 40\no4 9", "o9 3"]),
    ("size bands", "Each line is `id status amount`. Group by size band instead: `small` (under 50), `medium` (under 200), `large` (the rest). Print all three bands in that order as `<band>: <ids>`, or `<band>: -` for an empty band.",
     r'''
type Order = { id: string; status: string; amount: number };
const orders: Order[] = input.split("\n").map((line) => {
  const [id = "", status = "", amount = "0"] = line.trim().split(/\s+/);
  return { id, status, amount: Number(amount) };
});
const band = (o: Order) => (o.amount < 50 ? "small" : o.amount < 200 ? "medium" : "large");
const groups = Object.groupBy(orders, band);
for (const b of ["small", "medium", "large"]) {
  const ids = (groups[b] ?? []).map((o) => o.id);
  console.log(`${b}: ${ids.length > 0 ? ids.join(" ") : "-"}`);
}
''', [_M2B_ORDERS, "x1 new 5\nx2 new 50"]),
    ("numeric keys", "Each line is `id status amount`. Group with `Map.groupBy` by the amount's hundred — `Math.floor(amount / 100) * 100`, a number key — and print `<lo>-<lo + 99>: <ids>` for each group, lowest first, ids in input order.",
     r'''
type Order = { id: string; status: string; amount: number };
const orders: Order[] = input.split("\n").map((line) => {
  const [id = "", status = "", amount = "0"] = line.trim().split(/\s+/);
  return { id, status, amount: Number(amount) };
});
const groups = Map.groupBy(orders, (o) => Math.floor(o.amount / 100) * 100);
for (const lo of [...groups.keys()].toSorted((a, b) => a - b)) {
  console.log(`${lo}-${lo + 99}: ${(groups.get(lo) ?? []).map((o) => o.id).join(" ")}`);
}
''', [_M2B_ORDERS, "a new 1000\nb new 5\nc new 1099"]),
])
