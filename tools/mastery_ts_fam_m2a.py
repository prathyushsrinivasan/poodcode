# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — per-chapter practice families, Month 2 part A
# (TS_MASTERY_ROADMAP X-19): four families on each of the function, parameter,
# overload, closure, higher-order, recursion and array chapters of weeks 5-7.
#
# Each family is a small realistic task and four twists that each change one
# dimension (input shape, output format, an edge case, a rule, a
# generalisation). The four families of a chapter practise different facets of
# it and do not repeat the week families in mastery_ts_families.py (tips, ops,
# positions). Weeks 5-7 run at `strict`; the scope lint keeps every program
# inside its week (no `interface`/`JSON`/`try`, no `as const`, no `throw`, and
# `toSorted` only from week 7). Helpers are in mastery_ts_chapter_kit.py;
# exec()'d by gen_seed.py with the other tools/mastery_ts_fam_m*.py files.
# ---------------------------------------------------------------------------

# ═══ ts_functions (week 5) ═══════════════════════════════════════════════════

_xfam("ts_functions", "invoice", "Invoice lines", [
    ("", "Each input line is `name qty price`. Write `lineTotal(qty: number, price: number): number` and "
         "`formatLine(name: string, total: number): string`, and print one line per item: `<name>: <total>` "
         "with the total to two decimals.",
     r'''
function lineTotal(qty: number, price: number): number {
  return qty * price;
}
function formatLine(name: string, total: number): string {
  return `${name}: ${total.toFixed(2)}`;
}
for (const line of input.split("\n")) {
  const [name, qty, price] = line.trim().split(/\s+/);
  console.log(formatLine(name, lineTotal(Number(qty), Number(price))));
}
''', ["pen 3 1.5\nbook 1 12\nmug 2 7.25", "tea 10 0.99"]),
    ("a grand total", "Each line is `name qty price`. Print the item lines as `<name>: <total>` (two decimals), then a "
                      "last line `total: <sum of all lines>` (two decimals). Add a function "
                      "`grandTotal(totals: number[]): number`.",
     r'''
function lineTotal(qty: number, price: number): number {
  return qty * price;
}
function formatLine(name: string, total: number): string {
  return `${name}: ${total.toFixed(2)}`;
}
function grandTotal(totals: number[]): number {
  return totals.reduce((a, b) => a + b, 0);
}
const totals: number[] = [];
for (const line of input.split("\n")) {
  const [name, qty, price] = line.trim().split(/\s+/);
  const total = lineTotal(Number(qty), Number(price));
  totals.push(total);
  console.log(formatLine(name, total));
}
console.log(`total: ${grandTotal(totals).toFixed(2)}`);
''', ["pen 3 1.5\nbook 1 12\nmug 2 7.25", "tea 10 0.99"]),
    ("a bulk discount", "Each line is `name qty price`. A line with a quantity of 10 or more gets 10% off its total. "
                        "Print `<name>: <total>` per line with two decimals; keep the discount rule inside `lineTotal`.",
     r'''
function lineTotal(qty: number, price: number): number {
  const total = qty * price;
  return qty >= 10 ? total * 0.9 : total;
}
function formatLine(name: string, total: number): string {
  return `${name}: ${total.toFixed(2)}`;
}
for (const line of input.split("\n")) {
  const [name, qty, price] = line.trim().split(/\s+/);
  console.log(formatLine(name, lineTotal(Number(qty), Number(price))));
}
''', ["pen 12 1.5\nbook 1 12\nmug 9 2", "tea 10 1", "cup 100 0.5"]),
    ("comma-separated", "Each line is now `name,qty,price`, and a name may contain spaces (`blue pen,3,1.5`). Print "
                        "`<name>: <total>` per line with two decimals.",
     r'''
function lineTotal(qty: number, price: number): number {
  return qty * price;
}
function formatLine(name: string, total: number): string {
  return `${name}: ${total.toFixed(2)}`;
}
for (const line of input.split("\n")) {
  const [name, qty, price] = line.trim().split(",");
  console.log(formatLine(name, lineTotal(Number(qty), Number(price))));
}
''', ["blue pen,3,1.5\nbook,1,12\ncoffee mug,2,7.25", "green tea bags,10,0.99"]),
    ("aligned columns", "Each line is `name qty price`. Print each item as its name padded with spaces on the right to "
                        "the length of the longest name, a space, then its total with two decimals padded with spaces "
                        "on the left to 8 characters.",
     r'''
function lineTotal(qty: number, price: number): number {
  return qty * price;
}
function formatLine(name: string, total: number, width: number): string {
  return `${name.padEnd(width)} ${total.toFixed(2).padStart(8)}`;
}
const items = input.split("\n").map((line) => {
  const [name, qty, price] = line.trim().split(/\s+/);
  return { name, total: lineTotal(Number(qty), Number(price)) };
});
const width = Math.max(...items.map((item) => item.name.length));
for (const item of items) console.log(formatLine(item.name, item.total, width));
''', ["pen 3 1.5\nnotebook 1 12\nmug 20 7.25", "tea 10 0.99"]),
])

_xfam("ts_functions", "calendar", "Calendar helpers", [
    ("", "The input is a year. Write `isLeap(year: number): boolean` — divisible by 4, except century years, which "
         "must be divisible by 400 — and print `leap` or `common`.",
     r'''
function isLeap(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}
console.log(isLeap(Number(input)) ? "leap" : "common");
''', ["2024", "1900", "2000", "2023"]),
    ("days in a month", "The input is `year month` (month 1-12). Write `daysIn(year: number, month: number): number`, "
                        "using `isLeap` for February, and print the number of days.",
     r'''
function isLeap(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}
function daysIn(year: number, month: number): number {
  const lengths = [31, isLeap(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return lengths[month - 1];
}
const [year, month] = input.split(/\s+/).map(Number);
console.log(daysIn(year, month));
''', ["2024 2", "2023 2", "2023 4", "1900 12"]),
    ("a range of years", "The input is `from to`. Print how many leap years lie between them, both ends included.",
     r'''
function isLeap(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}
function countLeaps(from: number, to: number): number {
  let count = 0;
  for (let y = from; y <= to; y++) if (isLeap(y)) count++;
  return count;
}
const [from, to] = input.split(/\s+/).map(Number);
console.log(countLeaps(from, to));
''', ["1990 2030", "1900 1900", "2000 2000", "1896 1912"]),
    ("day of the year", "The input is a date `YYYY-MM-DD`. Print its day number within the year (1 January is 1). "
                        "Build it from `isLeap` and `daysIn(year, month)`.",
     r'''
function isLeap(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}
function daysIn(year: number, month: number): number {
  const lengths = [31, isLeap(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return lengths[month - 1];
}
function dayOfYear(year: number, month: number, day: number): number {
  let total = day;
  for (let m = 1; m < month; m++) total += daysIn(year, m);
  return total;
}
const [y, m, d] = input.split("-").map(Number);
console.log(dayOfYear(y, m, d));
''', ["2024-03-01", "2023-03-01", "2023-12-31", "2000-01-01"]),
    ("checking a date", "The input is a date `YYYY-MM-DD`. Write `isValidDate(year, month, day): boolean` (month 1-12, "
                        "day from 1 to that month's length) and print `valid` or `invalid`.",
     r'''
function isLeap(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
}
function daysIn(year: number, month: number): number {
  const lengths = [31, isLeap(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return lengths[month - 1];
}
function isValidDate(year: number, month: number, day: number): boolean {
  if (month < 1 || month > 12) return false;
  return day >= 1 && day <= daysIn(year, month);
}
const [y, m, d] = input.split("-").map(Number);
console.log(isValidDate(y, m, d) ? "valid" : "invalid");
''', ["2023-02-29", "2024-02-29", "2023-13-01", "2023-04-31", "2023-04-30", "2023-00-10"]),
])

_xfam("ts_functions", "banner", "Text boxes", [
    ("", "The input is one line of text. Print it in a box: a border of `*` as long as the text plus 4, then "
         "`* <text> *`, then the border again. Write `border(width: number): string` and "
         "`framed(text: string): string[]` (the three lines).",
     r'''
function border(width: number): string {
  return "*".repeat(width);
}
function framed(text: string): string[] {
  const edge = border(text.length + 4);
  return [edge, `* ${text} *`, edge];
}
for (const line of framed(input)) console.log(line);
''', ["hello", "TypeScript rocks", "a"]),
    ("several lines", "The input has several lines. Put them all in one box of `*`: the border is as long as the "
                      "longest line plus 4, and each line is printed as `* <line> *` with the line padded with spaces "
                      "on the right to the longest line's length.",
     r'''
function border(width: number): string {
  return "*".repeat(width);
}
function framed(lines: string[]): string[] {
  const width = Math.max(...lines.map((l) => l.length));
  const edge = border(width + 4);
  return [edge, ...lines.map((l) => `* ${l.padEnd(width)} *`), edge];
}
for (const line of framed(input.split("\n"))) console.log(line);
''', ["hello\nwide world\nhi", "one line"]),
    ("any border character", "Line 1 is a single border character, line 2 the text. Print the box as in the base "
                             "problem, drawn with that character: a border line of it (text length plus 4), "
                             "`<c> <text> <c>`, and the border again.",
     r'''
function border(width: number, ch: string): string {
  return ch.repeat(width);
}
function framed(text: string, ch: string): string[] {
  const edge = border(text.length + 4, ch);
  return [edge, `${ch} ${text} ${ch}`, edge];
}
const [ch, text] = input.split("\n");
for (const line of framed(text, ch)) console.log(line);
''', ["#\nhello", "=\nTypeScript rocks", "+\nx"]),
    ("centred", "The input has several lines. Print one `*` box as wide as the longest line plus 4, with each line "
                "centred as `* <line> *`: of the spaces needed to reach the longest length, the left side gets half "
                "(rounded down) and the right side the rest.",
     r'''
function border(width: number): string {
  return "*".repeat(width);
}
function centre(text: string, width: number): string {
  const extra = width - text.length;
  const left = Math.floor(extra / 2);
  return " ".repeat(left) + text + " ".repeat(extra - left);
}
function framed(lines: string[]): string[] {
  const width = Math.max(...lines.map((l) => l.length));
  const edge = border(width + 4);
  return [edge, ...lines.map((l) => `* ${centre(l, width)} *`), edge];
}
for (const line of framed(input.split("\n"))) console.log(line);
''', ["hi\nhello\nwide world", "abc\nabcd"]),
    ("a box per word", "The input is several words on one line. Print a separate `*` box (as in the base problem) for "
                       "each word, with one empty line between boxes. Write `printBox(text: string): void`, which "
                       "prints one box and returns nothing.",
     r'''
function border(width: number): string {
  return "*".repeat(width);
}
function printBox(text: string): void {
  const edge = border(text.length + 4);
  console.log(edge);
  console.log(`* ${text} *`);
  console.log(edge);
}
input.split(/\s+/).forEach((word, i) => {
  if (i > 0) console.log("");
  printBox(word);
});
''', ["hello big world", "solo"]),
])

_xfam("ts_functions", "median", "Statistics that leave the data alone", [
    ("", "The input is an odd-length list of numbers. Write `median(xs: readonly number[]): number` (the middle value "
         "once sorted) without changing its argument. Print `median <m>`, then on a second line the numbers exactly "
         "as given, separated by spaces.",
     r'''
function median(xs: readonly number[]): number {
  const sorted = [...xs].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}
const xs = input.split(/\s+/).map(Number);
console.log(`median ${median(xs)}`);
console.log(xs.join(" "));
''', ["9 1 5", "3", "7 -2 7 10 0"]),
    ("even counts", "The list may now have an even length: then the median is the mean of the two middle values. "
                    "Print `median <m>` with one decimal, then the numbers exactly as given, separated by spaces.",
     r'''
function median(xs: readonly number[]): number {
  const sorted = [...xs].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 1 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}
const xs = input.split(/\s+/).map(Number);
console.log(`median ${median(xs).toFixed(1)}`);
console.log(xs.join(" "));
''', ["9 1 5 3", "4 8", "5", "2 2 1"]),
    ("the spread", "Write `spread(xs: readonly number[]): string` returning `min <a> max <b> range <b - a>` from a sorted "
                   "copy. Print it, then the numbers exactly as given, separated by spaces.",
     r'''
function spread(xs: readonly number[]): string {
  const sorted = [...xs].sort((a, b) => a - b);
  const lo = sorted[0];
  const hi = sorted[sorted.length - 1];
  return `min ${lo} max ${hi} range ${hi - lo}`;
}
const xs = input.split(/\s+/).map(Number);
console.log(spread(xs));
console.log(xs.join(" "));
''', ["9 1 5", "4", "-3 10 2 10"]),
    ("without outliers", "The list has at least three numbers. Write `trimmedMean(xs: readonly number[]): number`: drop "
                         "one lowest and one highest value and average the rest. Print `trimmed <mean>` with two "
                         "decimals, then the numbers exactly as given.",
     r'''
function trimmedMean(xs: readonly number[]): number {
  const kept = [...xs].sort((a, b) => a - b).slice(1, -1);
  return kept.reduce((a, b) => a + b, 0) / kept.length;
}
const xs = input.split(/\s+/).map(Number);
console.log(`trimmed ${trimmedMean(xs).toFixed(2)}`);
console.log(xs.join(" "));
''', ["100 3 4 5 -50", "1 2 3", "7 7 7 8"]),
    ("the mode", "Write `mode(xs: readonly number[]): number`: the most frequent value, the smallest one on a tie. "
                 "Print `mode <m>`, then the numbers exactly as given, separated by spaces.",
     r'''
function mode(xs: readonly number[]): number {
  const counts = new Map<number, number>();
  for (const x of xs) counts.set(x, (counts.get(x) ?? 0) + 1);
  let best = xs[0];
  let bestCount = 0;
  for (const [value, count] of counts) {
    if (count > bestCount || (count === bestCount && value < best)) {
      best = value;
      bestCount = count;
    }
  }
  return best;
}
const xs = input.split(/\s+/).map(Number);
console.log(`mode ${mode(xs)}`);
console.log(xs.join(" "));
''', ["3 1 3 2 1", "5", "4 9 9 4 4"]),
])

# ═══ ts_params (week 5) ══════════════════════════════════════════════════════

_xfam("ts_params", "price", "Price formatting options", [
    ("", "Line 1 is an amount. Any further lines are options `key=value`: `currency` (default `$`) and `decimals` "
         "(default 2). Write `formatPrice(amount, { currency = \"$\", decimals = 2 } = {})` with an options object "
         "and print `<currency><amount with that many decimals>`.",
     r'''
type PriceOptions = { currency?: string; decimals?: number };
function formatPrice(amount: number, { currency = "$", decimals = 2 }: PriceOptions = {}): string {
  return currency + amount.toFixed(decimals);
}
const [first, ...rest] = input.split("\n");
const opts: PriceOptions = {};
for (const line of rest) {
  const [key, value] = line.trim().split("=");
  if (key === "currency") opts.currency = value;
  if (key === "decimals") opts.decimals = Number(value);
}
console.log(formatPrice(Number(first), opts));
''', ["12.5", "12.5\ncurrency=CHF", "3.14159\ndecimals=3\ncurrency=R", "7\ndecimals=0"]),
    ("thousands separators", "As in the base problem, plus an option `grouping=yes` (default off) that puts a comma "
                             "between every three digits of the whole part: `$12,345.50`. Print "
                             "`<currency><amount>`.",
     r'''
type PriceOptions = { currency?: string; decimals?: number; grouping?: boolean };
function formatPrice(amount: number, { currency = "$", decimals = 2, grouping = false }: PriceOptions = {}): string {
  const [whole, frac] = amount.toFixed(decimals).split(".");
  const shown = grouping ? whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : whole;
  return currency + (frac === undefined ? shown : `${shown}.${frac}`);
}
const [first, ...rest] = input.split("\n");
const opts: PriceOptions = {};
for (const line of rest) {
  const [key, value] = line.trim().split("=");
  if (key === "currency") opts.currency = value;
  if (key === "decimals") opts.decimals = Number(value);
  if (key === "grouping") opts.grouping = value === "yes";
}
console.log(formatPrice(Number(first), opts));
''', ["12345.5\ngrouping=yes", "12345.5", "1234567\ndecimals=0\ngrouping=yes\ncurrency=R", "999\ngrouping=yes"]),
    ("currency after", "As in the base problem (`currency`, `decimals`), plus an option `position` of `before` (the "
                       "default) or `after`. After prints `<amount> <currency>` with a space; before prints "
                       "`<currency><amount>`.",
     r'''
type PriceOptions = { currency?: string; decimals?: number; position?: string };
function formatPrice(amount: number, { currency = "$", decimals = 2, position = "before" }: PriceOptions = {}): string {
  const digits = amount.toFixed(decimals);
  return position === "after" ? `${digits} ${currency}` : currency + digits;
}
const [first, ...rest] = input.split("\n");
const opts: PriceOptions = {};
for (const line of rest) {
  const [key, value] = line.trim().split("=");
  if (key === "currency") opts.currency = value;
  if (key === "decimals") opts.decimals = Number(value);
  if (key === "position") opts.position = value;
}
console.log(formatPrice(Number(first), opts));
''', ["12.5\nposition=after\ncurrency=EUR", "12.5\nposition=after", "8\nposition=before\ncurrency=R", "0.5"]),
    ("negative amounts", "As in the base problem, but the amount may be negative: the minus sign goes before the "
                         "currency (`-$5.00`, not `$-5.00`).",
     r'''
type PriceOptions = { currency?: string; decimals?: number };
function formatPrice(amount: number, { currency = "$", decimals = 2 }: PriceOptions = {}): string {
  return (amount < 0 ? "-" : "") + currency + Math.abs(amount).toFixed(decimals);
}
const [first, ...rest] = input.split("\n");
const opts: PriceOptions = {};
for (const line of rest) {
  const [key, value] = line.trim().split("=");
  if (key === "currency") opts.currency = value;
  if (key === "decimals") opts.decimals = Number(value);
}
console.log(formatPrice(Number(first), opts));
''', ["-5", "-12.345\ncurrency=CHF\ndecimals=1", "3", "-0.5\ndecimals=0"]),
    ("many amounts", "Line 1 now holds several amounts separated by spaces; the option lines are as in the base "
                     "problem. Print every amount formatted with the same options, joined by `, `.",
     r'''
type PriceOptions = { currency?: string; decimals?: number };
function formatPrice(amount: number, { currency = "$", decimals = 2 }: PriceOptions = {}): string {
  return currency + amount.toFixed(decimals);
}
const [first, ...rest] = input.split("\n");
const opts: PriceOptions = {};
for (const line of rest) {
  const [key, value] = line.trim().split("=");
  if (key === "currency") opts.currency = value;
  if (key === "decimals") opts.decimals = Number(value);
}
console.log(first.split(/\s+/).map((a) => formatPrice(Number(a), opts)).join(", "));
''', ["1 2.5 10", "3.14159 2.71828\ndecimals=3\ncurrency=R", "7"]),
])

_xfam("ts_params", "range", "Counting ranges", [
    ("", "The input is one or two whole numbers. Write `range(a: number, b?: number): number[]`: with one number it "
         "counts from 0 up to `a - 1`, with two from `a` up to `b - 1`. Print the numbers separated by spaces, or "
         "`empty` if there are none.",
     r'''
function range(a: number, b?: number): number[] {
  const start = b === undefined ? 0 : a;
  const end = b === undefined ? a : b;
  const out: number[] = [];
  for (let i = start; i < end; i++) out.push(i);
  return out;
}
const n = input.split(/\s+/).map(Number);
const r = n.length === 1 ? range(n[0]) : range(n[0], n[1]);
console.log(r.length === 0 ? "empty" : r.join(" "));
''', ["5", "3 7", "4 4", "0"]),
    ("a step", "An optional third number is a positive step (default 1): `range(a, b?, step = 1)`. Print the numbers "
               "separated by spaces, or `empty`.",
     r'''
function range(a: number, b?: number, step = 1): number[] {
  const start = b === undefined ? 0 : a;
  const end = b === undefined ? a : b;
  const out: number[] = [];
  for (let i = start; i < end; i += step) out.push(i);
  return out;
}
const n = input.split(/\s+/).map(Number);
const r = n.length === 1 ? range(n[0]) : n.length === 2 ? range(n[0], n[1]) : range(n[0], n[1], n[2]);
console.log(r.length === 0 ? "empty" : r.join(" "));
''', ["0 10 3", "2 5", "6", "5 3 2"]),
    ("counting down", "The input is one, two or three numbers as before, but the step may be negative: then the range "
                      "counts down from `a` while above `b`. A step of 0 gives an empty range. Print the numbers "
                      "separated by spaces, or `empty`.",
     r'''
function range(a: number, b?: number, step = 1): number[] {
  const start = b === undefined ? 0 : a;
  const end = b === undefined ? a : b;
  const out: number[] = [];
  if (step > 0) for (let i = start; i < end; i += step) out.push(i);
  if (step < 0) for (let i = start; i > end; i += step) out.push(i);
  return out;
}
const n = input.split(/\s+/).map(Number);
const r = n.length === 1 ? range(n[0]) : n.length === 2 ? range(n[0], n[1]) : range(n[0], n[1], n[2]);
console.log(r.length === 0 ? "empty" : r.join(" "));
''', ["10 0 -3", "5 1 -1", "0 10 3", "3 3 -1", "1 5 0"]),
    ("a summary", "The input is one or two whole numbers, read as in the base problem. Instead of the numbers, print "
                  "`count <c> sum <s>` for the range.",
     r'''
function range(a: number, b?: number): number[] {
  const start = b === undefined ? 0 : a;
  const end = b === undefined ? a : b;
  const out: number[] = [];
  for (let i = start; i < end; i++) out.push(i);
  return out;
}
const n = input.split(/\s+/).map(Number);
const r = n.length === 1 ? range(n[0]) : range(n[0], n[1]);
console.log(`count ${r.length} sum ${r.reduce((a, b) => a + b, 0)}`);
''', ["5", "3 7", "4 4", "-3 3"]),
    ("letters too", "The input is one or two whole numbers as in the base problem, or one or two lowercase letters: "
                    "`e` gives `a b c d`, `c f` gives `c d e`. Write `charRange(a: string, b?: string): string[]` on "
                    "top of `range`. Print the values separated by spaces, or `empty`.",
     r'''
function range(a: number, b?: number): number[] {
  const start = b === undefined ? 0 : a;
  const end = b === undefined ? a : b;
  const out: number[] = [];
  for (let i = start; i < end; i++) out.push(i);
  return out;
}
function charRange(a: string, b?: string): string[] {
  const start = b === undefined ? "a".charCodeAt(0) : a.charCodeAt(0);
  const end = b === undefined ? a.charCodeAt(0) : b.charCodeAt(0);
  return range(start, end).map((code) => String.fromCharCode(code));
}
const t = input.split(/\s+/);
let out: (string | number)[];
if (/^[a-z]$/.test(t[0])) out = t.length === 1 ? charRange(t[0]) : charRange(t[0], t[1]);
else out = t.length === 1 ? range(Number(t[0])) : range(Number(t[0]), Number(t[1]));
console.log(out.length === 0 ? "empty" : out.join(" "));
''', ["e", "c f", "3 6", "a", "x z"]),
])

_xfam("ts_params", "path", "Joining paths", [
    ("", "The input is path segments separated by spaces; a segment may carry stray slashes at either end (`docs/`, "
         "`/img`). Write `joinPath(...parts: string[]): string` that removes those end slashes and joins the "
         "segments with `/`, call it by spreading the segments, and print the result.",
     r'''
function joinPath(...parts: string[]): string {
  return parts.map((p) => p.replace(/^\/+|\/+$/g, "")).join("/");
}
console.log(joinPath(...input.split(/\s+/)));
''', ["home user docs", "/var/ log/ app.log", "single"]),
    ("skipping the noise", "As in the base problem, but after removing end slashes, empty segments and `.` segments "
                           "are dropped. If nothing is left, print `.`.",
     r'''
function joinPath(...parts: string[]): string {
  const kept = parts.map((p) => p.replace(/^\/+|\/+$/g, "")).filter((p) => p !== "" && p !== ".");
  return kept.length === 0 ? "." : kept.join("/");
}
console.log(joinPath(...input.split(/\s+/)));
''', ["a / . b", ". ./ /", "src/ ./ main.ts"]),
    ("going up", "As in the base problem, with two more rules: empty and `.` segments are dropped, and a `..` segment "
                 "removes the kept segment before it (it is ignored when there is none). If nothing is left, print "
                 "`.`.",
     r'''
function joinPath(...parts: string[]): string {
  const kept: string[] = [];
  for (const raw of parts) {
    const p = raw.replace(/^\/+|\/+$/g, "");
    if (p === "" || p === ".") continue;
    if (p === "..") kept.pop();
    else kept.push(p);
  }
  return kept.length === 0 ? "." : kept.join("/");
}
console.log(joinPath(...input.split(/\s+/)));
''', ["a b .. c", "x .. .. y", "docs/ ../ ..", "one . two"]),
    ("a root first", "Line 1 is a root (`/`, `C:` or a URL like `https://example.com/`), line 2 the segments. Write "
                     "`joinPath(root: string, ...parts: string[])`: remove end slashes from each segment and trailing "
                     "slashes from the root, then print the root, a `/`, and the segments joined with `/`.",
     r'''
function joinPath(root: string, ...parts: string[]): string {
  const rest = parts.map((p) => p.replace(/^\/+|\/+$/g, "")).join("/");
  return root.replace(/\/+$/, "") + "/" + rest;
}
const [root, segments] = input.split("\n");
console.log(joinPath(root.trim(), ...segments.trim().split(/\s+/)));
''', ["/\nusr bin", "C:\nUsers ana/", "https://example.com/\napi v1/ users"]),
    ("slashes inside", "The segments may now contain slashes inside them and repeated slashes (`a//b`). Split every "
                       "segment on `/` too, drop the empty pieces, and print everything joined by single `/`.",
     r'''
function joinPath(...parts: string[]): string {
  return parts.flatMap((p) => p.split("/")).filter((p) => p !== "").join("/");
}
console.log(joinPath(...input.split(/\s+/)));
''', ["a/b c", "//x//y/ z/", "docs"]),
])

_xfam("ts_params", "truncate", "Truncating text", [
    ("", "Line 1 is a piece of text; an optional line 2 is a maximum length (default 20). Write "
         "`truncate(text: string, max = 20): string`: text within the limit comes back unchanged, longer text is cut "
         "to its first `max - 3` characters followed by `...`. Print the result.",
     r'''
function truncate(text: string, max = 20): string {
  return text.length <= max ? text : text.slice(0, max - 3) + "...";
}
const [text, maxLine] = input.split("\n");
console.log(maxLine === undefined ? truncate(text) : truncate(text, Number(maxLine)));
''', ["The quick brown fox jumps over the lazy dog", "Short one", "Hello, world\n8", "abcdef\n6"]),
    ("your own marker", "An optional line 3 is the marker to use instead of `...`: "
                        "`truncate(text, max = 20, marker = \"...\")`. Longer text is cut to its first "
                        "`max - marker.length` characters followed by the marker. Print the result.",
     r'''
function truncate(text: string, max = 20, marker = "..."): string {
  return text.length <= max ? text : text.slice(0, max - marker.length) + marker;
}
const [text, maxLine, marker] = input.split("\n");
if (maxLine === undefined) console.log(truncate(text));
else if (marker === undefined) console.log(truncate(text, Number(maxLine)));
else console.log(truncate(text, Number(maxLine), marker));
''', ["Hello there, general\n10\n~", "Hello there, general\n10", "Shortish text",
      "A very long sentence indeed\n12\n>>", "The quick brown fox jumps over the lazy dog"]),
    ("whole words", "Line 1 text, optional line 2 max (default 20). Longer text now keeps as many whole words (split "
                    "on single spaces) as fit in `max - 3` characters, followed by `...`; if not even the first word "
                    "fits, cut it to `max - 3` characters as in the base problem.",
     r'''
function truncate(text: string, max = 20): string {
  if (text.length <= max) return text;
  const room = max - 3;
  let out = "";
  for (const word of text.split(" ")) {
    const next = out === "" ? word : out + " " + word;
    if (next.length > room) break;
    out = next;
  }
  return (out === "" ? text.slice(0, room) : out) + "...";
}
const [text, maxLine] = input.split("\n");
console.log(maxLine === undefined ? truncate(text) : truncate(text, Number(maxLine)));
''', ["The quick brown fox jumps over the lazy dog", "Supercalifragilistic word\n10", "Tiny", "one two three four\n12"]),
    ("from the middle", "Line 1 text, optional line 2 max (default 20). Longer text keeps its start and its end: the "
                        "first `ceil((max - 3) / 2)` characters, then `...`, then the last `floor((max - 3) / 2)` "
                        "characters. Print the result.",
     r'''
function truncate(text: string, max = 20): string {
  if (text.length <= max) return text;
  const room = max - 3;
  const head = Math.ceil(room / 2);
  const tail = Math.floor(room / 2);
  return text.slice(0, head) + "..." + text.slice(text.length - tail);
}
const [text, maxLine] = input.split("\n");
console.log(maxLine === undefined ? truncate(text) : truncate(text, Number(maxLine)));
''', ["a_very_long_file_name_for_testing.txt", "short.txt", "abcdefghij\n7", "report-final-v2.pdf\n10"]),
    ("many lines", "Line 1 is the maximum length, or `-` to use the default of 20; every later line is a piece of "
                   "text. Truncate each as in the base problem and print them one per line.",
     r'''
function truncate(text: string, max = 20): string {
  return text.length <= max ? text : text.slice(0, max - 3) + "...";
}
const [limit, ...texts] = input.split("\n");
for (const text of texts) console.log(limit.trim() === "-" ? truncate(text) : truncate(text, Number(limit)));
''', ["-\nThe quick brown fox jumps over the lazy dog\nshort", "8\nabcdefghij\nabc\nabcdefgh"]),
])
