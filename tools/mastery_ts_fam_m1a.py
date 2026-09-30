# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# TypeScript Mastery — practice families, Month 1 part A (TS_MASTERY_ROADMAP
# X-19): four families on each of the program I/O, variables, primitive types,
# inference, operators, equality and conditionals chapters of weeks 1-2.
#
# A family is a base problem and four twists that each change ONE dimension
# (the input's shape, the output's format, an edge case, a rule, a
# generalisation); the learner writes every one from a blank, so each prompt
# spells out the exact output. The week families already in
# mastery_ts_families.py (temperature table, grade bands) are not repeated.
# Weeks 1-2 run at `strict`, and the scope lint keeps the programs inside what
# those weeks teach. Helpers are in mastery_ts_chapter_kit.py; exec()'d by
# gen_seed.py with the other tools/mastery_ts_fam_m*.py files.
# ---------------------------------------------------------------------------


# ===========================================================================
# Week 1 — ts_program_io
# ===========================================================================

_xfam("ts_program_io", "words", "Word count", [
    ("", "The input is one line of words separated by any amount of spaces or tabs. "
         "Print how many words it has, as a bare number.",
     r'''
console.log(input.split(/\s+/).length);
''', ["the quick brown fox", "hello", "a   b\tc  d"]),
    ("blank input", "The same, but the input may also be empty or only whitespace: print `0` for it "
                    "(not `1`, which is what splitting an empty string would count).",
     r'''
console.log(input === "" ? 0 : input.split(/\s+/).length);
''', ["", "   ", "one two", "solo"]),
    ("line by line", "The input is now several lines. Print each line's word count on its own line, "
                     "in order; a line with no words counts `0`.",
     r'''
for (const line of input.split("\n")) {
  const text = line.trim();
  console.log(text === "" ? 0 : text.split(/\s+/).length);
}
''', ["to be\nor not to be", "one\n\n  two   three  ", "single"]),
    ("two counts", "The input is one or more lines. Print `words <w> chars <c>` on one line, where `w` is "
                   "the number of words and `c` the number of characters that are not whitespace.",
     r'''
const words = input === "" ? [] : input.split(/\s+/);
console.log(`words ${words.length} chars ${words.join("").length}`);
''', ["hello world", "a bb\nccc  dddd", ""]),
    ("busiest line", "The input is several lines. Print `line <i>: <n> words` for the line with the most "
                     "words (`i` counts from 1; on a tie, the earliest line wins).",
     r'''
const counts = input.split("\n").map((line) => {
  const text = line.trim();
  return text === "" ? 0 : text.split(/\s+/).length;
});
let best = 0;
for (let i = 1; i < counts.length; i++) {
  if (counts[i] > counts[best]) best = i;
}
console.log(`line ${best + 1}: ${counts[best]} words`);
''', ["one\nthree more words\ntwo words", "a b\nc d\ne", "only"]),
])

_xfam("ts_program_io", "settings", "Settings lines", [
    ("", "Each input line is a setting written `key=value`, with no spaces. Print each as "
         "`key -> value`, one per line, in order.",
     r'''
for (const line of input.split("\n")) {
  const [key, value] = line.trim().split("=");
  console.log(`${key} -> ${value}`);
}
''', ["theme=dark\nfont=mono", "port=8080", "a=1\r\nb=2"]),
    ("spaces around", "Now there may be spaces around the key, the `=` and the value (`  size = 12 `). "
                      "Print `key -> value` with those spaces removed.",
     r'''
for (const line of input.split("\n")) {
  const [key, value] = line.split("=");
  console.log(`${key.trim()} -> ${value.trim()}`);
}
''', ["  size = 12 \ncolor=red", "name   =   Ada"]),
    ("an = in the value", "The value itself may contain `=` (`query = a=1`): only the FIRST `=` separates key "
                          "from value. Print `key -> value`, spaces around both trimmed.",
     r'''
for (const line of input.split("\n")) {
  const at = line.indexOf("=");
  console.log(`${line.slice(0, at).trim()} -> ${line.slice(at + 1).trim()}`);
}
''', ["query = a=1&b=2\nmode=x", "eq = 1+1=2", "plain=value"]),
    ("look one up", "The first line is a key to look up; the lines after it are settings as before (first "
                    "`=` separates, spaces trimmed). Print that key's value — the LAST one if it is set twice — "
                    "or `missing`.",
     r'''
const lines = input.split("\n");
const wanted = lines[0].trim();
let found = "missing";
for (const line of lines.slice(1)) {
  const at = line.indexOf("=");
  if (line.slice(0, at).trim() === wanted) found = line.slice(at + 1).trim();
}
console.log(found);
''', ["port\nhost = local\nport = 80\nport = 8080", "user\nname=ada", "x\nx = a=b"]),
    ("comments", "Settings as in twist 2 (first `=` separates, spaces trimmed), but blank lines and lines "
                 "starting with `#` are skipped. Print `key -> value` for each real setting, then a last "
                 "line `<n> settings`.",
     r'''
let n = 0;
for (const line of input.split("\n")) {
  const text = line.trim();
  if (text === "" || text.startsWith("#")) continue;
  const at = text.indexOf("=");
  console.log(`${text.slice(0, at).trim()} -> ${text.slice(at + 1).trim()}`);
  n++;
}
console.log(`${n} settings`);
''', ["# display\ntheme = dark\n\nfont=mono", "# nothing here", "a=1\n  # indented comment\nb = x=y"]),
])

_xfam("ts_program_io", "prices", "Price list", [
    ("", "Each input line is `<item> <price>`. Print each as `<item>: $<price>` with the price "
         "to exactly two decimals.",
     r'''
for (const line of input.split("\n")) {
  const [item, price] = line.trim().split(/\s+/);
  console.log(`${item}: $${Number(price).toFixed(2)}`);
}
''', ["apple 1.5\nbread 3", "tea 12.345", "pen 0.1"]),
    ("aligned columns", "Same input. Print each line as the item padded on the right with dots to 12 "
                        "characters, then the price (two decimals) padded on the left with spaces to 8 "
                        "characters — `apple.......    1.50`.",
     r'''
for (const line of input.split("\n")) {
  const [item, price] = line.trim().split(/\s+/);
  console.log(item.padEnd(12, ".") + Number(price).toFixed(2).padStart(8));
}
''', ["apple 1.5\nbread 3\ncheese 125.4", "x 0"]),
    ("dollar signs", "Prices may now be written with a leading `$` (`$3.5`) or without (`3.5`). Print "
                     "`<item>: $<price>` with two decimals, as in the base problem.",
     r'''
for (const line of input.split("\n")) {
  const [item, price] = line.trim().split(/\s+/);
  const text = price.startsWith("$") ? price.slice(1) : price;
  console.log(`${item}: $${Number(text).toFixed(2)}`);
}
''', ["apple $1.5\nbread 3", "tea $12", "gum 0.25"]),
    ("a quantity", "Each line is now `<item> <qty> <unit price>`. Print `<item> x<qty>: $<qty × price>`, "
                   "the amount to two decimals.",
     r'''
for (const line of input.split("\n")) {
  const [item, qty, price] = line.trim().split(/\s+/);
  console.log(`${item} x${qty}: $${(Number(qty) * Number(price)).toFixed(2)}`);
}
''', ["apple 3 0.5\nbread 1 2.25", "egg 12 0.2"]),
    ("a total line", "Lines of `<item> <qty> <unit price>` as in twist 3; print the same lines, then a last "
                     "line `total: $<sum of the amounts>` to two decimals.",
     r'''
let total = 0;
for (const line of input.split("\n")) {
  const [item, qty, price] = line.trim().split(/\s+/);
  const amount = Number(qty) * Number(price);
  total += amount;
  console.log(`${item} x${qty}: $${amount.toFixed(2)}`);
}
console.log(`total: $${total.toFixed(2)}`);
''', ["apple 3 0.5\nbread 1 2.25", "egg 12 0.2\nmilk 2 1.1\nsalt 1 0.75"]),
])

_xfam("ts_program_io", "sizes", "CSS sizes", [
    ("", "The input is sizes in pixels such as `12px 3px 40px`. Add them up and print the total "
         "with its unit, like `55px`.",
     r'''
let total = 0;
for (const token of input.split(/\s+/)) total += parseInt(token, 10);
console.log(`${total}px`);
''', ["12px 3px 40px", "7px", "100px 0px"]),
    ("decimals", "The sizes are now in `em` and may have decimals (`1.5em 2em`). Print the total "
                 "followed by `em`, as JavaScript prints the number (`3.5em`, `4em`).",
     r'''
let total = 0;
for (const token of input.split(/\s+/)) total += parseFloat(token);
console.log(`${total}em`);
''', ["1.5em 2em", "0.25em 0.75em 1em", "3em"]),
    ("in rem", "Pixel sizes as in the base problem, but print the total in rem (1rem is 16px) to "
               "three decimals, like `3.438rem`.",
     r'''
let total = 0;
for (const token of input.split(/\s+/)) total += parseInt(token, 10);
console.log(`${(total / 16).toFixed(3)}rem`);
''', ["12px 3px 40px", "16px", "1px"]),
    ("not a size", "Pixel sizes, but some tokens are keywords like `auto` that do not start with a number. "
                   "Skip them. Print `<total>px` on the first line and `skipped <k>` on the second.",
     r'''
let total = 0;
let skipped = 0;
for (const token of input.split(/\s+/)) {
  const n = parseInt(token, 10);
  if (Number.isNaN(n)) skipped++;
  else total += n;
}
console.log(`${total}px`);
console.log(`skipped ${skipped}`);
''', ["12px auto 40px", "auto inherit", "8px"]),
    ("mixed units", "Tokens are now either pixels (`24px`) or rem (`1.5rem`, where 1rem is 16px). Print "
                    "the total in pixels, like `48px`, as JavaScript prints the number.",
     r'''
let total = 0;
for (const token of input.split(/\s+/)) {
  const n = parseFloat(token);
  total += token.endsWith("rem") ? n * 16 : n;
}
console.log(`${total}px`);
''', ["24px 1.5rem", "2rem 2rem", "10px 0.5rem 3px"]),
])


# ===========================================================================
# Week 1 — ts_variables
# ===========================================================================

_xfam("ts_variables", "balance", "Running balance", [
    ("", "The input is a line of amounts: positive ones are deposits, negative ones withdrawals. "
         "Starting from 0, print the balance after each amount, all on one line separated by spaces.",
     r'''
let balance = 0;
const after: number[] = [];
for (const token of input.split(/\s+/)) {
  balance += Number(token);
  after.push(balance);
}
console.log(after.join(" "));
''', ["50 -20 30", "-5 5", "100"]),
    ("an opening balance", "The first line is now the opening balance and the second line the amounts. "
                           "Print the balance after each amount, on one line separated by spaces.",
     r'''
const [first, second] = input.split("\n");
let balance = Number(first);
const after: number[] = [];
for (const token of second.trim().split(/\s+/)) {
  balance += Number(token);
  after.push(balance);
}
console.log(after.join(" "));
''', ["100\n-30 -30 10", "0\n5", "-10\n20 -5"]),
    ("final and lowest", "One line of amounts, starting from 0 again. Print only `final <f> lowest <l>`: the "
                         "last balance and the lowest balance it ever had (the starting 0 counts).",
     r'''
let balance = 0;
let lowest = 0;
for (const token of input.split(/\s+/)) {
  balance += Number(token);
  if (balance < lowest) lowest = balance;
}
console.log(`final ${balance} lowest ${lowest}`);
''', ["50 -80 60", "10 20", "-5 -5 20"]),
    ("refused withdrawals", "One line of amounts from 0, but a withdrawal that would take the balance below 0 "
                            "is refused and leaves it unchanged. Print `final <f> refused <k>`.",
     r'''
let balance = 0;
let refused = 0;
for (const token of input.split(/\s+/)) {
  const amount = Number(token);
  if (balance + amount < 0) refused++;
  else balance += amount;
}
console.log(`final ${balance} refused ${refused}`);
''', ["50 -80 -50 10", "-1 -2", "20 -20"]),
    ("an overdraft limit", "The first line is an overdraft limit L; the second line the amounts, from 0. "
                           "The balance may go down to -L but no further: a withdrawal that would pass it is "
                           "refused. Print `final <f> refused <k>`.",
     r'''
const [first, second] = input.split("\n");
const limit = Number(first);
let balance = 0;
let refused = 0;
for (const token of second.trim().split(/\s+/)) {
  const amount = Number(token);
  if (balance + amount < -limit) refused++;
  else balance += amount;
}
console.log(`final ${balance} refused ${refused}`);
''', ["50\n-30 -30 -30", "0\n-1 5 -5", "100\n-100 -1 50"]),
])

_xfam("ts_variables", "changes", "Day to day", [
    ("", "The input is a line of daily readings (at least two). Print the change from each reading to "
         "the next, on one line separated by spaces (`10 12 9` gives `2 -3`).",
     r'''
const readings = input.split(/\s+/).map(Number);
let prev = readings[0];
const changes: number[] = [];
for (const r of readings.slice(1)) {
  changes.push(r - prev);
  prev = r;
}
console.log(changes.join(" "));
''', ["10 12 9", "5 5", "1 2 4 8"]),
    ("in words", "Same input. Instead of numbers, print `up`, `down` or `same` for each change, on one line "
                 "separated by spaces.",
     r'''
const readings = input.split(/\s+/).map(Number);
let prev = readings[0];
const words: string[] = [];
for (const r of readings.slice(1)) {
  words.push(r > prev ? "up" : r < prev ? "down" : "same");
  prev = r;
}
console.log(words.join(" "));
''', ["10 12 9 9", "5 5", "3 2 1"]),
    ("one reading", "As twist 1, but the input may hold a single reading, which has no changes: print "
                    "`no changes` for it.",
     r'''
const readings = input.split(/\s+/).map(Number);
let prev = readings[0];
const words: string[] = [];
for (const r of readings.slice(1)) {
  words.push(r > prev ? "up" : r < prev ? "down" : "same");
  prev = r;
}
console.log(words.length === 0 ? "no changes" : words.join(" "));
''', ["7", "10 12 9", "4 4"]),
    ("longest rise", "Readings as in the base problem. Print the length of the longest run of consecutive "
                     "rises — how many `up` changes in a row — as a bare number (`0` if it never rises).",
     r'''
const readings = input.split(/\s+/).map(Number);
let prev = readings[0];
let run = 0;
let best = 0;
for (const r of readings.slice(1)) {
  run = r > prev ? run + 1 : 0;
  if (run > best) best = run;
  prev = r;
}
console.log(best);
''', ["1 2 3 2 3 4 5", "5 4 3", "1 1 2"]),
    ("only big moves", "The first token is a threshold T; the rest are readings. Print `<from> -> <to>` "
                       "for each change whose size (up or down) is at least T, one per line, or `steady` "
                       "if there is none.",
     r'''
const [threshold, ...readings] = input.split(/\s+/).map(Number);
let prev = readings[0];
let printed = 0;
for (const r of readings.slice(1)) {
  if (Math.abs(r - prev) >= threshold) {
    console.log(`${prev} -> ${r}`);
    printed++;
  }
  prev = r;
}
if (printed === 0) console.log("steady");
''', ["3 10 12 20 16", "5 1 2 3", "0 4 4"]),
])

_xfam("ts_variables", "numbering", "Line numbers", [
    ("", "Print every input line prefixed with its line number and a colon: `1: first line`, "
         "`2: second line`, …",
     r'''
let n = 0;
for (const line of input.split("\n")) {
  n++;
  console.log(`${n}: ${line.trim()}`);
}
''', ["alpha\nbeta\ngamma", "only one"]),
    ("skip blanks", "Blank lines (empty or only spaces) are now skipped: they are not printed and do not "
                    "use up a number. Print `<n>: <line>` for the others.",
     r'''
let n = 0;
for (const line of input.split("\n")) {
  const text = line.trim();
  if (text === "") continue;
  n++;
  console.log(`${n}: ${text}`);
}
''', ["alpha\n\nbeta\n   \ngamma", "one\n\n\ntwo"]),
    ("padded numbers", "Blank lines skipped as in twist 1, and every number is now padded on the left with "
                       "spaces to the width of the largest number used (` 9: …`, `10: …`).",
     r'''
const lines = input.split("\n").map((line) => line.trim()).filter((line) => line !== "");
const width = String(lines.length).length;
let n = 0;
for (const line of lines) {
  n++;
  console.log(`${String(n).padStart(width)}: ${line}`);
}
''', ["\n".join(f"line {c}" for c in "abcdefghijk"), "a\n\nb", "x"]),
    ("sections", "No blank lines now, but a line that is exactly `---` starts a new section: print it as "
                 "`---` and restart the numbering at 1 for the lines after it.",
     r'''
let n = 0;
for (const line of input.split("\n")) {
  const text = line.trim();
  if (text === "---") {
    console.log("---");
    n = 0;
    continue;
  }
  n++;
  console.log(`${n}: ${text}`);
}
''', ["a\nb\n---\nc\nd\ne", "---\nx", "p\nq"]),
    ("start and step", "The first line is `<start> <step>`; number the lines after it starting at `start` "
                       "and going up by `step` (`10: …`, `20: …`). Blank lines are skipped and use no number.",
     r'''
const [head, ...rest] = input.split("\n");
const [start, step] = head.trim().split(/\s+/).map(Number);
let n = start;
for (const line of rest) {
  const text = line.trim();
  if (text === "") continue;
  console.log(`${n}: ${text}`);
  n += step;
}
''', ["10 10\nload\n\nsave\nquit", "0 5\na\nb", "7 -1\nx\ny\nz"]),
])

_xfam("ts_variables", "sequence", "Growing sequences", [
    ("", "The input is n (at least 1). Print the first n Fibonacci numbers — starting `0 1`, each next "
         "one the sum of the two before — on one line separated by spaces.",
     r'''
const n = Number(input);
let a = 0;
let b = 1;
const out: number[] = [];
for (let i = 0; i < n; i++) {
  out.push(a);
  [a, b] = [b, a + b];
}
console.log(out.join(" "));
''', ["7", "1", "2", "12"]),
    ("own seeds", "The input is now `a b n`: the sequence starts with `a` and `b` instead of 0 and 1. "
                  "Print its first n numbers on one line separated by spaces.",
     r'''
const [first, second, n] = input.split(/\s+/).map(Number);
let a = first;
let b = second;
const out: number[] = [];
for (let i = 0; i < n; i++) {
  out.push(a);
  [a, b] = [b, a + b];
}
console.log(out.join(" "));
''', ["2 1 6", "5 5 4", "3 -1 5"]),
    ("just the nth", "The input is n again. Print only the nth Fibonacci number (the 1st is 0, the 2nd "
                     "is 1, the 3rd is 1, …).",
     r'''
const n = Number(input);
let a = 0;
let b = 1;
for (let i = 1; i < n; i++) {
  [a, b] = [b, a + b];
}
console.log(a);
''', ["1", "2", "10", "40"]),
    ("evens only", "The input is n. Of the first n Fibonacci numbers, print the sum of the even ones "
                   "(0 counts, and adds nothing).",
     r'''
const n = Number(input);
let a = 0;
let b = 1;
let sum = 0;
for (let i = 0; i < n; i++) {
  if (a % 2 === 0) sum += a;
  [a, b] = [b, a + b];
}
console.log(sum);
''', ["10", "1", "3", "30"]),
    ("three at a time", "The input is n. Print the first n Tribonacci numbers — starting `0 0 1`, each "
                        "next one the sum of the THREE before — on one line separated by spaces.",
     r'''
const n = Number(input);
let a = 0;
let b = 0;
let c = 1;
const out: number[] = [];
for (let i = 0; i < n; i++) {
  out.push(a);
  [a, b, c] = [b, c, a + b + c];
}
console.log(out.join(" "));
''', ["8", "1", "3", "12"]),
])


# ===========================================================================
# Week 1 — ts_types
# ===========================================================================

_xfam("ts_types", "kinds", "Token kinds", [
    ("", "The input is a line of tokens. For each, print `<token>: <kind>` on its own line, where the "
         "kind is `boolean` for `true` or `false`, `number` if `Number(token)` is not NaN, and "
         "`string` otherwise. Write a function whose return type is `\"number\" | \"boolean\" | \"string\"`.",
     r'''
function kind(token: string): "number" | "boolean" | "string" {
  if (token === "true" || token === "false") return "boolean";
  if (!Number.isNaN(Number(token))) return "number";
  return "string";
}
for (const token of input.split(/\s+/)) console.log(`${token}: ${kind(token)}`);
''', ["42 hi true 3.5", "false -7 x1", "0x10"]),
    ("finite only", "As the base problem, but `Infinity`, `-Infinity` and anything too big like `1e999` are "
                    "not numbers here: a token is a `number` only when `Number(token)` is finite.",
     r'''
function kind(token: string): "number" | "boolean" | "string" {
  if (token === "true" || token === "false") return "boolean";
  if (Number.isFinite(Number(token))) return "number";
  return "string";
}
for (const token of input.split(/\s+/)) console.log(`${token}: ${kind(token)}`);
''', ["Infinity 12 NaN", "1e999 -Infinity 1e3", "true"]),
    ("a null kind", "Finite numbers as in twist 1, and one more kind: the token `null` is of kind `null`. "
                    "The function now returns `\"number\" | \"boolean\" | \"string\" | \"null\"`. Print "
                    "`<token>: <kind>` per line.",
     r'''
function kind(token: string): "number" | "boolean" | "string" | "null" {
  if (token === "null") return "null";
  if (token === "true" || token === "false") return "boolean";
  if (Number.isFinite(Number(token))) return "number";
  return "string";
}
for (const token of input.split(/\s+/)) console.log(`${token}: ${kind(token)}`);
''', ["null 1 nil", "false null Infinity", "undefined"]),
    ("a tally", "Kinds as in twist 2. Print only one line: `number <a> boolean <b> string <c> null <d>`, "
                "counting the tokens of each kind.",
     r'''
function kind(token: string): "number" | "boolean" | "string" | "null" {
  if (token === "null") return "null";
  if (token === "true" || token === "false") return "boolean";
  if (Number.isFinite(Number(token))) return "number";
  return "string";
}
let numbers = 0;
let booleans = 0;
let strings = 0;
let nulls = 0;
for (const token of input.split(/\s+/)) {
  const k = kind(token);
  if (k === "number") numbers++;
  else if (k === "boolean") booleans++;
  else if (k === "string") strings++;
  else nulls++;
}
console.log(`number ${numbers} boolean ${booleans} string ${strings} null ${nulls}`);
''', ["1 2 true x null", "hello", "null null 0 false"]),
    ("convert each", "Kinds as in twist 2, but now convert each token to its real value and print the "
                     "results on one line separated by spaces: a number doubled, a boolean negated, a "
                     "string upper-cased, and `null` as `null`.",
     r'''
function convert(token: string): string {
  if (token === "null") return "null";
  if (token === "true" || token === "false") return String(!(token === "true"));
  const n = Number(token);
  if (Number.isFinite(n)) return String(n * 2);
  return token.toUpperCase();
}
console.log(input.split(/\s+/).map(convert).join(" "));
''', ["21 true hi null", "-1.5 false Infinity", "abc"]),
])

_xfam("ts_types", "flags", "Feature flags", [
    ("", "Each input line is `<name> on` or `<name> off`. Print the names that are on, in order, on one "
         "line separated by spaces — or `none`.",
     r'''
const enabled: string[] = [];
for (const line of input.split("\n")) {
  const [name, state] = line.trim().split(/\s+/);
  const on: boolean = state === "on";
  if (on) enabled.push(name);
}
console.log(enabled.length === 0 ? "none" : enabled.join(" "));
''', ["dark on\nbeta off\nsync on", "a off", "x on"]),
    ("as booleans", "Same input. Print every flag as `<name>: true` or `<name>: false`, one per line — the "
                    "boolean itself, not the text `on`/`off`.",
     r'''
for (const line of input.split("\n")) {
  const [name, state] = line.trim().split(/\s+/);
  const on: boolean = state === "on";
  console.log(`${name}: ${on}`);
}
''', ["dark on\nbeta off", "sync on"]),
    ("more spellings", "Values may now be `on`/`off`, `yes`/`no`, `true`/`false` or `1`/`0`. Print "
                       "`<name>: true` or `<name>: false` per line.",
     r'''
for (const line of input.split("\n")) {
  const [name, state] = line.trim().split(/\s+/);
  const on: boolean = state === "on" || state === "yes" || state === "true" || state === "1";
  console.log(`${name}: ${on}`);
}
''', ["dark yes\nbeta 0\nsync true\nlogs off", "a 1"]),
    ("unknown values", "Spellings as in twist 2, but any other value (`maybe`, `2`) is not a boolean at all: "
                       "print `<name>: invalid` for it. A flag's value is `true`, `false`, or missing — use "
                       "`boolean | null`.",
     r'''
function parse(state: string): boolean | null {
  if (state === "on" || state === "yes" || state === "true" || state === "1") return true;
  if (state === "off" || state === "no" || state === "false" || state === "0") return false;
  return null;
}
for (const line of input.split("\n")) {
  const [name, state] = line.trim().split(/\s+/);
  const value = parse(state);
  console.log(`${name}: ${value === null ? "invalid" : value}`);
}
''', ["dark yes\nbeta maybe\nsync 0", "x 2\ny on"]),
    ("a summary", "Values as in twist 3. Print only one line: `on <a> off <b> invalid <c>`.",
     r'''
function parse(state: string): boolean | null {
  if (state === "on" || state === "yes" || state === "true" || state === "1") return true;
  if (state === "off" || state === "no" || state === "false" || state === "0") return false;
  return null;
}
let on = 0;
let off = 0;
let invalid = 0;
for (const line of input.split("\n")) {
  const [, state] = line.trim().split(/\s+/);
  const value = parse(state);
  if (value === null) invalid++;
  else if (value) on++;
  else off++;
}
console.log(`on ${on} off ${off} invalid ${invalid}`);
''', ["dark yes\nbeta maybe\nsync 0\nlogs on", "a off", "q what"]),
])

_xfam("ts_types", "modes", "Text modes", [
    ("", "The first token of the input is a mode, `upper` or `lower`; the rest is text. Print the text "
         "(its words joined by single spaces) in that case. Write `apply(text: string, mode: \"upper\" | "
         "\"lower\"): string`.",
     r'''
function apply(text: string, mode: "upper" | "lower"): string {
  return mode === "upper" ? text.toUpperCase() : text.toLowerCase();
}
const [mode, ...words] = input.split(/\s+/);
console.log(apply(words.join(" "), mode === "upper" ? "upper" : "lower"));
''', ["upper hello world", "lower MiXeD Case", "upper x"]),
    ("an unknown mode", "Now the first token may be anything: for a mode other than `upper` or `lower`, "
                        "print `unknown mode: <mode>` instead.",
     r'''
function apply(text: string, mode: "upper" | "lower"): string {
  return mode === "upper" ? text.toUpperCase() : text.toLowerCase();
}
const [mode, ...words] = input.split(/\s+/);
if (mode === "upper" || mode === "lower") console.log(apply(words.join(" "), mode));
else console.log(`unknown mode: ${mode}`);
''', ["upper hello", "shout hello", "lower ABC def"]),
    ("a title mode", "Add a third mode, `title`: every word gets an upper-case first letter and the rest "
                     "lower-case. Unknown modes print `unknown mode: <mode>` as before.",
     r'''
type Mode = "upper" | "lower" | "title";
function apply(text: string, mode: Mode): string {
  if (mode === "upper") return text.toUpperCase();
  if (mode === "lower") return text.toLowerCase();
  return text.split(" ").map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
}
const [mode, ...words] = input.split(/\s+/);
if (mode === "upper" || mode === "lower" || mode === "title") console.log(apply(words.join(" "), mode));
else console.log(`unknown mode: ${mode}`);
''', ["title the gREAT gatsby", "upper hi", "camel x y"]),
    ("one per line", "The input is now several lines, each `<mode> <text>` with the three modes of twist 2. "
                     "Print each line's result on its own line (`unknown mode: <mode>` where needed).",
     r'''
type Mode = "upper" | "lower" | "title";
function apply(text: string, mode: Mode): string {
  if (mode === "upper") return text.toUpperCase();
  if (mode === "lower") return text.toLowerCase();
  return text.split(" ").map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
}
for (const line of input.split("\n")) {
  const [mode, ...words] = line.trim().split(/\s+/);
  if (mode === "upper" || mode === "lower" || mode === "title") console.log(apply(words.join(" "), mode));
  else console.log(`unknown mode: ${mode}`);
}
''', ["upper hi there\ntitle war and peace\nlower LOUD", "mute a\nlower B"]),
    ("chained modes", "One line again, but the first token may chain modes with `+` (`title+upper`), applied "
                      "left to right; the modes are `upper`, `lower`, `title` and a new `reverse` (reverse the "
                      "characters). If any part is unknown, print `unknown mode: <part>` for the first such part.",
     r'''
type Mode = "upper" | "lower" | "title" | "reverse";
function apply(text: string, mode: Mode): string {
  if (mode === "upper") return text.toUpperCase();
  if (mode === "lower") return text.toLowerCase();
  if (mode === "reverse") return text.split("").reverse().join("");
  return text.split(" ").map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
}
const [chain, ...words] = input.split(/\s+/);
let text = words.join(" ");
let bad = "";
for (const part of chain.split("+")) {
  if (part === "upper" || part === "lower" || part === "title" || part === "reverse") text = apply(text, part);
  else if (bad === "") bad = part;
}
console.log(bad === "" ? text : `unknown mode: ${bad}`);
''', ["title+reverse hello world", "lower+upper abc", "upper+wobble+x hi", "reverse stressed"]),
])

_xfam("ts_types", "names", "Name parts", [
    ("", "Each input is a name of two or three words: `first last` or `first middle last`. Print the "
         "initials, each followed by a dot, upper-cased: `A.L.` or `A.B.L.`. Keep the middle name in a "
         "`string | null` variable.",
     r'''
const parts = input.split(/\s+/);
const first = parts[0];
const last = parts[parts.length - 1];
const middle: string | null = parts.length === 3 ? parts[1] : null;
const initial = (s: string) => s.charAt(0).toUpperCase() + ".";
console.log(initial(first) + (middle === null ? "" : initial(middle)) + initial(last));
''', ["ada lovelace", "grace brewster hopper", "Alan Turing"]),
    ("formal order", "Same input. Print the name as `Last, First` — with ` M.` (the middle initial) "
                     "added when there is a middle name: `Hopper, Grace B.`. Words are printed as given.",
     r'''
const parts = input.split(/\s+/);
const first = parts[0];
const last = parts[parts.length - 1];
const middle: string | null = parts.length === 3 ? parts[1] : null;
console.log(`${last}, ${first}` + (middle === null ? "" : ` ${middle.charAt(0).toUpperCase()}.`));
''', ["Ada Lovelace", "Grace brewster Hopper", "Alan Mathison Turing"]),
    ("a placeholder", "Every input now has exactly three words, and a middle word of `-` means there is no "
                      "middle name. Print `Last, First` or `Last, First M.` as in twist 1.",
     r'''
const [first, mid, last] = input.split(/\s+/);
const middle: string | null = mid === "-" ? null : mid;
console.log(`${last}, ${first}` + (middle === null ? "" : ` ${middle.charAt(0).toUpperCase()}.`));
''', ["Ada - Lovelace", "Grace brewster Hopper", "Kurt - Godel"]),
    ("a single name", "Back to two or three words, but the input may also be ONE word (a mononym): print it "
                      "unchanged. Otherwise print `Last, First` or `Last, First M.` as in twist 1.",
     r'''
const parts = input.split(/\s+/);
const first = parts[0];
const last: string | null = parts.length > 1 ? parts[parts.length - 1] : null;
const middle: string | null = parts.length === 3 ? parts[1] : null;
if (last === null) console.log(first);
else console.log(`${last}, ${first}` + (middle === null ? "" : ` ${middle.charAt(0).toUpperCase()}.`));
''', ["Plato", "Ada Lovelace", "Grace brewster Hopper"]),
    ("a list of names", "The input is several lines, one name per line (one, two or three words as in twist "
                        "3). Print each line's result, one per line.",
     r'''
function formal(line: string): string {
  const parts = line.trim().split(/\s+/);
  const first = parts[0];
  const last: string | null = parts.length > 1 ? parts[parts.length - 1] : null;
  const middle: string | null = parts.length === 3 ? parts[1] : null;
  if (last === null) return first;
  return `${last}, ${first}` + (middle === null ? "" : ` ${middle.charAt(0).toUpperCase()}.`);
}
for (const line of input.split("\n")) console.log(formal(line));
''', ["Plato\nAda Lovelace\nGrace brewster Hopper", "Alan Turing"]),
])
