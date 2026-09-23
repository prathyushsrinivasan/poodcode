# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# New TypeScript chapters for Mastery Month 1 — Language foundations.
#
#   week 1  ts_program_io      the stdin/stdout contract every judged program keeps
#   week 2  ts_equality        ===, NaN, Object.is, the truthiness table, ?? vs ||
#   week 3  ts_number_format   floating point, toFixed, cents, bigint, Intl
#   week 4  ts_regex           regular expressions, flags, groups, replaceAll
#   week 4  ts_unicode         code units vs code points vs graphemes
#
# Built with ts_chapter_kit.py's `_chapter`: every printed output and compiler
# message is computed (python tools/gen_ts_outputs.py). Raw strings keep a
# TypeScript "\n" as backslash-n.
# ---------------------------------------------------------------------------

_chapter(
    "ts_program_io", "TS: Language Basics",
    "Program I/O — stdin and stdout",
    "How a judged program reads its input and prints its answer: `readFileSync(0)`, `trim`, `split`, `Number`, and exactly what `console.log` writes.",
    "Every program in this app talks to the judge through text: the test's input arrives on standard input, and whatever the program prints on standard output is compared with the expected answer. Reading that text reliably — all of it, trimmed, split into lines and tokens, converted to numbers — and printing exactly the expected characters is the first skill, and most \"wrong answer\" verdicts in week 1 come from it rather than from the logic.",
    "Java reads with a `Scanner` and prints with `System.out.println`. Here the whole input is read at once as one string (`fs.readFileSync(0, \"utf8\")`) and cut up with string methods; `console.log` is `println`, but it joins several arguments with spaces.",
    why=r"""
A judged program is a black box with one input and one output. The judge
writes the test's input to your program's **standard input**, runs it, and
compares everything it printed to **standard output** with the expected text.
It does not call your functions and does not look at your variables.

That makes the edges of the program matter more than they look. Read only part
of the input, keep a stray newline, print a value with an extra space or one
decimal too many, and a correct algorithm scores zero. Every week of this
programme uses the same few lines to read and print; this chapter is those lines,
and what each one really does.
""",
    idea=r"""
**Reading.** Node gives a program its standard input as file descriptor `0`:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
```

- `readFileSync(0, "utf8")` reads **all** of standard input into one string.
  Without the `"utf8"` you would get raw bytes, not text.
- `.trim()` drops the whitespace at both ends — above all the final newline,
  and the `\r` that Windows line endings leave behind.

**Cutting it up.** The input is text; the structure is yours to recover.

| input looks like | read it with |
|---|---|
| one value | `input` |
| several tokens on a line | `input.split(/\s+/)` |
| several lines | `input.split("\n")` |
| a line of numbers | `input.split(/\s+/).map(Number)` |

`/\s+/` splits on any run of spaces or tabs, so `"3   4"` still gives two
tokens where `split(" ")` would give an empty string between them.

**Converting.** Everything read is a `string` — TypeScript knows it, and will
not let you do arithmetic on it. Convert on purpose:

- `Number(text)` — the whole string must be a number: `Number("12")` is `12`,
  `Number("12px")` is `NaN`, and `Number("")` is `0`.
- `parseInt(text, 10)` / `parseFloat(text)` — read a number off the *front*
  and ignore the rest: `parseInt("12px", 10)` is `12`.

**Printing.** `console.log` writes its arguments and a newline:

- several arguments are joined with **one space**: `console.log("a", 1)`
  prints `a 1`;
- a number prints in its shortest form: `2.50` is printed as `2.5`, so use
  `toFixed(2)` when the format demands two decimals;
- an array of values is best printed with `join`: `xs.join(" ")`.

**What the judge forgives.** Trailing spaces at the end of a line, `\r`
characters and trailing blank lines are ignored. Everything else — a missing
space, an extra decimal, `2.5` for `2.50` — is a wrong answer.
""",
    examples=[
        ("One number in, one number out",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n = Number(input);
console.log(n * 2);
""", ["21", "-4\n"],
         "The second input ends in a newline, as real input usually does; `trim` removes it before `Number` sees it."),
        ("Two numbers on one line",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const parts = input.split(/\s+/);
const width = Number(parts[0]);
const height = Number(parts[1]);
console.log("area", width * height);
console.log(`perimeter ${2 * (width + height)}`);
""", ["3 4", "10    2"],
         "`console.log(\"area\", 12)` prints `area 12` — the two arguments are joined with one space. The template string gives you full control instead."),
        ("Several lines",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const lines = input.split("\n");
const name = lines[0].trim();
const age = Number(lines[1]);
console.log(`Hello, ${name}. Next year you will be ${age + 1}.`);
""", ["Ada\n36", "Grace\r\n85\r\n"],
         "The second input has Windows line endings. `trim()` on the whole input and on each line removes the `\\r` characters that would otherwise end up inside `name`."),
        ("Printing exactly two decimals",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const price = Number(input);
console.log(price);
console.log(price.toFixed(2));
console.log("$" + (price * 3).toFixed(2));
""", ["2.5", "10"],
         "`console.log(2.5)` prints `2.5`. When the expected output says `2.50`, only `toFixed(2)` produces it — and `toFixed` returns a *string*, ready to print."),
    ],
    errors=[
        (2554, r"""
import * as fs from "fs";
const input = fs.readFileSync(0);
console.log(input);
""", "Without an encoding `readFileSync` returns raw bytes, not text, and the judge's declarations only offer the text form — so the compiler wants the second argument, `\"utf8\"`."),
        (2362, r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
console.log(input * 2);
""", "`input` is a `string`. TypeScript refuses arithmetic on it rather than guessing what you meant; convert with `Number(input)` first."),
        (2322, r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n: number = input;
console.log(n + 1);
""", "An annotation does not convert anything. Reading gives you a `string`; `Number(...)` is the conversion, and the annotation only checks you did it."),
    ],
    pitfalls=[
        ("Forgetting to trim",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8");
console.log("[" + input + "]");
""",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
console.log("[" + input + "]");
""",
         "The raw input still carries its final newline, so it ends up *inside* the brackets. With a number it is harmless — `Number(\"5\\n\")` is `5` — but compare or print the string and the stray newline breaks the answer.",
         ["hello\n"]),
        ("`+` on two strings concatenates",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const parts = input.split(/\s+/);
console.log(parts[0] + parts[1]);
""",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const parts = input.split(/\s+/);
console.log(Number(parts[0]) + Number(parts[1]));
""",
         "Both tokens are strings, and `+` with strings joins them: `\"2\" + \"3\"` is `\"23\"`. The compiler allows it because string concatenation is legal — only converting first makes it addition.",
         ["2 3"]),
        ("`console.log` adds a space between arguments",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const total = Number(input) * 2;
console.log("total:", total);
""",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const total = Number(input) * 2;
console.log(`total:${total}`);
""",
         "If the expected output is `total:10`, passing two arguments prints `total: 10` — one space too many. Build the exact string yourself when spacing matters.",
         ["5"]),
        ("`split(\" \")` and double spaces",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const words = input.split(" ");
console.log(words.length);
""",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const words = input.split(/\s+/);
console.log(words.length);
""",
         "Two spaces in a row give an empty string between them, so `split(\" \")` counts three words in `a  b`… plus one more for every extra space. Split on the pattern `/\\s+/` instead.",
         ["one  two   three"]),
    ],
    later=[
        "**Week 2 — Operators & control flow.** Comparing what you read: `===` on strings versus numbers.",
        "**Week 3 — Numbers.** Why `toFixed` rounds the way it does, and printing money exactly.",
        "**Week 7 — Arrays.** `split(...).map(Number)` properly, plus `reduce` for totals.",
        "**Week 11 — Narrowing.** `JSON.parse` hands you `any`; turning untrusted input into a real type.",
    ],
    exercises=[
        _drill("ts_program_io-double", "Read, convert, print",
               "The input is one number. Replace `____` so `n` holds that number — converted, not the string.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n = Number(input);
console.log(n * 2);
console.log(n + 1);
""", ["Number(input)"], ["21", "0", "-3.5", "100\n"],
               hint="Everything read from stdin is a string. `Number(...)` converts the whole thing."),
        _drill("ts_program_io-pair", "Two tokens on a line",
               "The input is two numbers separated by one or more spaces. Replace `____` with the expression that splits the line into its tokens, however many spaces sit between them.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const parts = input.split(/\s+/);
const a = Number(parts[0]);
const b = Number(parts[1]);
console.log(a + b);
console.log(a * b);
""", ["input.split(/\\s+/)"], ["2 3", "10     4", "-1 1", "7\t8"],
               hint="Split on a pattern that matches any run of whitespace: `/\\s+/`."),
        _drill("ts_program_io-money", "Exactly two decimals",
               "The input is a price and a quantity on two lines. Print the total with exactly two decimals, prefixed by `$`. Replace `____` with the expression that formats `total`.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const lines = input.split("\n");
const price = Number(lines[0]);
const quantity = Number(lines[1]);
const total = price * quantity;
console.log("$" + total.toFixed(2));
""", ["total.toFixed(2)"], ["2.5\n3", "10\n1", "0.1\n3", "19.99\r\n2\r\n"],
               hint="`console.log(7.5)` prints `7.5`; the expected output wants `7.50`. `toFixed(2)` returns the string you need."),
        _chal("ts_program_io-receipt", "A receipt line", "Easy",
              "The input is three lines: an item name, a unit price, and a quantity. Print `<name> x<quantity> = $<total>` with the total to exactly two decimals, then on a second line `avg $<price>` with the unit price to two decimals. Names may have spaces; ignore spaces around every line.",
              r"""
const lines = input.split("\n");
const name = lines[0].trim();
const price = Number(lines[1]);
const quantity = Number(lines[2]);
const total = price * quantity;
console.log(`${name} x${quantity} = $${total.toFixed(2)}`);
console.log(`avg $${price.toFixed(2)}`);
""", ["pen\n1.5\n4", "coffee beans\n12\n1", "  tea  \n 3.25 \n 10 ", "gum\n0.99\n3"],
              hint="Read the three lines, trim what you print, convert what you compute with, and format with `toFixed(2)`."),
    ],
    quiz=[
        _cq("What does `fs.readFileSync(0, \"utf8\")` read?",
            "All of standard input, as one string",
            ["The first line of standard input", "The file named `0`", "Standard output"],
            "File descriptor 0 is standard input. The whole input arrives at once; splitting it is up to you."),
        _cq("Why call `.trim()` on the input?",
            "To drop the trailing newline and any `\\r` from Windows line endings",
            ["To convert it to a string", "To remove every space inside it", "It is required by TypeScript"],
            "Input almost always ends in a newline; leaving it on makes comparisons and printed strings wrong."),
        _cq("`Number(\"12px\")`, `parseInt(\"12px\", 10)` — what do they give?",
            "`NaN` and `12`",
            ["`12` and `12`", "`NaN` and `NaN`", "`12` and `NaN`"],
            "`Number` needs the whole string to be numeric; `parseInt` reads the leading digits and stops."),
        _cq("What does `console.log(\"sum\", 5)` print?",
            "`sum 5`",
            ["`sum5`", "`sum, 5`", "`[\"sum\", 5]`"],
            "Several arguments are joined with a single space."),
        _cq("`const n = 2.5; console.log(n)` prints `2.5`. How do you print `2.50`?",
            "`console.log(n.toFixed(2))`",
            ["`console.log(n, 2)`", "`console.log(Number(n.toFixed(2)))`", "`console.log(n * 1.00)`"],
            "`toFixed` returns a string with exactly that many decimals. Converting it back to a number loses the trailing zero again."),
        _cq("Why does `input.split(\" \")` miscount words in `\"a  b\"`?",
            "Two spaces produce an empty string between them",
            ["`split` ignores the second word", "It counts characters, not words", "It doesn't; it returns two words"],
            "`\"a  b\".split(\" \")` is `[\"a\", \"\", \"b\"]`. Splitting on `/\\s+/` treats any run of whitespace as one separator."),
    ],
    interview=[
        ("How do you read input in a Node program that is fed through stdin?",
         "`fs.readFileSync(0, \"utf8\")` reads all of standard input as one string; then `trim()` and `split` it into lines or tokens. For a long-running program you'd use a stream (`process.stdin` with `readline`), but for a batch program reading it at once is simplest."),
        ("What's the difference between `Number()` and `parseInt()`?",
         "`Number` converts the whole string or gives `NaN` (and treats `\"\"` as 0); `parseInt` reads an integer off the front and ignores the rest, and should always get its radix: `parseInt(s, 10)`. For validation, `Number` plus `Number.isNaN` is stricter."),
        ("Your output looks right but the judge says wrong answer. What do you check?",
         "Formatting before logic: extra or missing spaces (`console.log` joins arguments with spaces), decimals (`2.5` vs `2.50`), a stray `\\r` or newline in a printed string, and whether I printed every line the format asks for, in order."),
    ],
)


_chapter(
    "ts_equality", "TS: Language Basics",
    "Equality & Truthiness",
    "`===` versus `==`, why `NaN !== NaN`, `Object.is`, the full truthiness table, and when `??` beats `||`.",
    "Two questions decide every branch: are these equal, and is this value truthy? JavaScript answers both with rules that are easy to half-remember — `==` coerces, `NaN` is not equal to itself, `0` and `\"\"` are falsy, objects compare by identity. TypeScript catches some of the traps (comparing a string with a number) and not others (a `0` treated as missing). This chapter makes the rules exact.",
    "Java's `==` on objects compares references and `.equals` compares values; JavaScript objects and arrays likewise compare by reference with `===`, but strings compare by value. There is no `.equals` — deep comparison is something you write (or `JSON.stringify` for plain data).",
    why=r"""
Most wrong branches are not wrong logic — they are the wrong idea of what
"equal" or "present" means. `if (count)` skips a legitimate zero. `value || 10`
overwrites an empty string the user typed on purpose. `input == 0` is `true` for
an empty line. `[1] === [1]` is `false`.

JavaScript's rules here are fixed and learnable, and TypeScript helps with some
of them — it rejects `===` between types that can never be equal. The rest you
have to know. Knowing them is the difference between a condition that is right
and one that is right for the inputs you happened to try.
""",
    idea=r"""
**Strict equality.** `a === b` is `true` when both have the same type and the
same value — no conversion. Use it everywhere. `!==` is its negation.

**Loose equality.** `a == b` first *converts* its operands by a table almost
nobody remembers: `"" == 0`, `"1" == 1`, `null == undefined`, `false == "0"`
are all `true`. The one idiomatic use is `x == null`, which matches both
`null` and `undefined`.

**The odd numbers.** `NaN` is not equal to anything, including itself:
`NaN === NaN` is `false`, so test with `Number.isNaN(x)`. `0 === -0` is `true`.
`Object.is(a, b)` is `===` with those two corners fixed:
`Object.is(NaN, NaN)` is `true` and `Object.is(0, -0)` is `false`.

**Objects compare by identity.** Two arrays or objects are `===` only if they
are the *same* object. `[1, 2] === [1, 2]` is `false`. Compare contents
yourself — element by element, or with `JSON.stringify` for plain data.

**Truthiness.** In a condition, eight values count as false:

| falsy | |
|---|---|
| `false` | the boolean |
| `0`, `-0`, `0n` | zero |
| `""` | the empty string |
| `null`, `undefined` | absence |
| `NaN` | not-a-number |

Everything else is truthy — including `"0"`, `"false"`, `[]` and `{}`.

**Defaults: `||` versus `??`.** `a || b` falls back to `b` whenever `a` is
*falsy*; `a ?? b` only when `a` is `null` or `undefined`. For "use the default
if nothing was given", `??` is almost always what you mean, because `0` and
`""` are real values.

**What TypeScript adds.** Comparing values whose types can never overlap —
a `number` with a `string` — is a compile error (TS2367), which catches many
`===` mistakes that `==` would have silently coerced.
""",
    examples=[
        ("`===` does not convert; `==` does",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const asNumber = Number(input);
console.log(asNumber === 0);
console.log(input === "0");
console.log(Object.is(asNumber, -0));
""", ["0", "", "-0"],
         "An empty line becomes `0` through `Number(\"\")`, which is why checking the *text* is sometimes the honest test. `Object.is` can even tell `-0` from `0`."),
        ("`NaN` is never equal to itself",
         r"""
const values = [Number("12"), Number("12px"), Number("")];
for (const v of values) {
  console.log(v, v === v, Number.isNaN(v));
}
""", [""],
         "`v === v` is `false` only for `NaN` — an old trick, but `Number.isNaN` says what you mean."),
        ("Identity, not contents",
         r"""
const a = [1, 2];
const b = [1, 2];
const c = a;
console.log(a === b, a === c);
console.log(JSON.stringify(a) === JSON.stringify(b));
c.push(3);
console.log(a.length);
""", [""],
         "`a` and `b` are two arrays with the same contents; `a` and `c` are one array with two names — which is why pushing through `c` changes `a`."),
        ("`??` keeps the zero `||` throws away",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const typed = input === "" ? undefined : Number(input);
console.log("with ||:", typed || 10);
console.log("with ??:", typed ?? 10);
""", ["0", "", "7"],
         "When the user typed `0`, `||` replaces it with the default; `??` keeps it. Only when nothing was typed do both fall back."),
    ],
    errors=[
        (2367, r"""
const count: number = 3;
const label: string = "3";
console.log(count === label);
""", "A `number` and a `string` can never be `===`, so the comparison is always `false` — almost certainly a bug. Convert one side on purpose first."),
        (5076, r"""
const a: number | undefined = undefined;
const b = 0;
console.log(a ?? b || 5);
""", "Mixing `??` with `||` or `&&` without parentheses is rejected outright, because the precedence is too easy to misread. Say which you mean: `(a ?? b) || 5`."),
    ],
    pitfalls=[
        ("`if (count)` skips a real zero",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const count = Number(input);
if (count) console.log(`${count} items`);
else console.log("no count given");
""",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
if (input !== "") console.log(`${Number(input)} items`);
else console.log("no count given");
""",
         "`0` is falsy, so a genuine count of zero takes the \"missing\" branch. Test for what you actually mean — here, whether anything was typed.",
         ["0"]),
        ("`||` overwrites a legitimate empty string",
         r"""
const settings: { nickname?: string } = { nickname: "" };
const shown = settings.nickname || "anonymous";
console.log(`[${shown}]`);
""",
         r"""
const settings: { nickname?: string } = { nickname: "" };
const shown = settings.nickname ?? "anonymous";
console.log(`[${shown}]`);
""",
         "The user deliberately cleared their nickname; `||` treats that as missing. `??` only falls back for `null` and `undefined`."),
        ("Comparing arrays with `===`",
         r"""
const expected = [1, 2, 3];
const actual = [3, 2, 1].sort();
console.log(actual === expected ? "match" : "different");
""",
         r"""
const expected = [1, 2, 3];
const actual = [3, 2, 1].sort();
const same = actual.length === expected.length && actual.every((v, i) => v === expected[i]);
console.log(same ? "match" : "different");
""",
         "Two separate arrays are never `===`, whatever they contain. Compare element by element (or `JSON.stringify` both for plain data)."),
        ("`=== NaN` can never be true",
         (r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n = Number(input);
console.log(n === NaN ? "not a number" : `ok: ${n}`);
""", 2845),
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n = Number(input);
console.log(Number.isNaN(n) ? "not a number" : `ok: ${n}`);
""",
         "`n === NaN` is always `false` — even when `n` is `NaN` — and TypeScript knows it, so it refuses the comparison outright. In plain JavaScript this bug runs silently. `Number.isNaN` is the reliable test.",
         ["abc"]),
    ],
    later=[
        "**Week 3 — Numbers.** Floating-point equality: why `0.1 + 0.2 !== 0.3`, and comparing with a tolerance.",
        "**Week 9 — Maps & Sets.** Keys are compared with SameValueZero — like `===` but with `NaN` equal to itself — and objects by identity.",
        "**Week 11 — Narrowing.** `===` checks, `typeof` and truthiness all *narrow* types; the falsy table decides what each branch knows.",
    ],
    exercises=[
        _drill("ts_equality-default", "Keep the zero",
               "The input is a line that may be empty. Replace `____` with a default that falls back to `1` only when nothing was typed — a typed `0` must stay `0`.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const typed = input === "" ? undefined : Number(input);
const quantity = typed ?? 1;
console.log(`quantity ${quantity}`);
""", ["typed ?? 1"], ["0", "", "5"],
               hint="`||` would replace the zero. Which operator only replaces `null` and `undefined`?"),
        _drill("ts_equality-nan", "Spot the not-a-number",
               "Each input line should be a number. Replace `____` with the test that is `true` exactly when `n` is `NaN`.",
               r"""
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
for (const line of lines) {
  const n = Number(line);
  console.log(Number.isNaN(n) ? `bad: ${line.trim()}` : `ok: ${n}`);
}
""", ["Number.isNaN(n)"], ["12\nabc\n3.5", "x", "0\n-1"],
               hint="`n === NaN` is never true. There is a function for exactly this."),
        _drill("ts_equality-same", "Same contents?",
               "The input is two lines of numbers. Replace `____` with a check that is `true` when both lines hold the same numbers in the same order.",
               r"""
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
const a = lines[0].trim().split(/\s+/).map(Number);
const b = lines[1].trim().split(/\s+/).map(Number);
const same = a.length === b.length && a.every((v, i) => v === b[i]);
console.log(same ? "same" : "different");
""", ["a.length === b.length && a.every((v, i) => v === b[i])"],
               ["1 2 3\n1 2 3", "1 2 3\n3 2 1", "1 2\n1 2 3", "5\n5"],
               hint="`a === b` compares identity. Compare the lengths, then every element."),
        _chal("ts_equality-classify", "Classify the value", "Easy",
              "Each input line is one raw value. Print `empty` for an empty or all-space line, `nan` if it is not a number, `zero` if it equals zero (including `-0` and `0.0`), and otherwise `positive` or `negative`.",
              r"""
for (const raw of input.split("\n")) {
  const text = raw.trim();
  if (text === "") {
    console.log("empty");
    continue;
  }
  const n = Number(text);
  if (Number.isNaN(n)) console.log("nan");
  else if (n === 0) console.log("zero");
  else console.log(n > 0 ? "positive" : "negative");
}
""", ["5\n-2\n0", "abc\n-0\n0.0", "  \n7", "1e3\n-0.5\nNaN"],
              hint="Check emptiness on the text before converting — `Number(\"\")` is `0`. `-0 === 0` is `true`, which is what you want here."),
    ],
    quiz=[
        _cq("Which comparison is `true`?", "`null == undefined`",
            ["`null === undefined`", "`NaN === NaN`", "`[1] === [1]`"],
            "Loose equality treats `null` and `undefined` as equal to each other and nothing else — the one widely accepted use of `==`."),
        _cq("How do you test whether `x` is `NaN`?", "`Number.isNaN(x)`",
            ["`x === NaN`", "`x == NaN`", "`typeof x === \"NaN\"`"],
            "`NaN` is not equal to anything, itself included."),
        _cq("Which value is truthy?", "`\"false\"`", ["`0`", "`\"\"`", "`NaN`"],
            "Any non-empty string is truthy, whatever it says."),
        _cq("`const n = 0; n || 10` and `n ?? 10` give…", "`10` and `0`",
            ["`0` and `10`", "`10` and `10`", "`0` and `0`"],
            "`||` falls back on any falsy value; `??` only on `null`/`undefined`."),
        _cq("What does TypeScript say about `3 === \"3\"` with those declared types?",
            "It's a compile error: the types have no overlap",
            ["`true`", "`false`, with no error", "A warning only"],
            "TS2367: comparing a `number` and a `string` is always `false`, so the compiler flags it."),
        _cq("`Object.is(0, -0)` and `Object.is(NaN, NaN)`?", "`false` and `true`",
            ["`true` and `false`", "`true` and `true`", "`false` and `false`"],
            "`Object.is` is `===` with the two corners fixed the other way."),
    ],
    interview=[
        ("`==` or `===`?",
         "`===`, always, except `x == null` to catch both `null` and `undefined`. `==` coerces by a table that makes `\"\" == 0` true, and TypeScript's overlap check (TS2367) only works when you compare like with like."),
        ("How do you compare two arrays or objects for equality?",
         "Not with `===` — that's identity. For arrays: same length and `every` element equal; for nested plain data, a recursive deep-equal or `JSON.stringify` if key order is controlled. Libraries like `node:util`'s `isDeepStrictEqual` exist too."),
        ("Why is `??` usually better than `||` for defaults?",
         "`||` replaces every falsy value, so a real `0`, `\"\"` or `false` gets overwritten. `??` only replaces `null`/`undefined`, which is what \"not provided\" means."),
    ],
)


_chapter(
    "ts_number_format", "TS: Language Basics",
    "Numbers in Practice — Precision, Money & Formatting",
    "Floating-point surprises, `toFixed` and rounding, money as integer cents, `Number.isInteger`, the safe-integer limit, `bigint`, and `Intl.NumberFormat`.",
    "`number` is a 64-bit binary float. That is why `0.1 + 0.2` is `0.30000000000000004`, why `(1.005).toFixed(2)` is `\"1.00\"`, and why integers stop being exact past 2^53. None of this is a TypeScript quirk — it is IEEE-754 arithmetic, shared by almost every language. Knowing where it bites tells you when to compare with a tolerance, when to count money in whole cents, when to reach for `bigint`, and how to print a number the way a human expects.",
    "Java has `int`, `long`, `double` and `BigDecimal`. TypeScript has only `number` (a Java `double`) and `bigint` (a `BigInteger`). There is no fixed-point decimal type, so money is conventionally stored as an integer number of cents.",
    why=r"""
Week 3's problems print averages, totals and prices, and the first time a
program prints `0.30000000000000004` or rounds a price the wrong way it looks
like a bug in your logic. It isn't — it is the number type doing exactly what
it was designed to do, with a finite number of binary digits.

The fixes are all simple once you know which problem you have: compare with a
tolerance, keep money in integer cents, format only at the moment of printing,
and switch to `bigint` when a count outgrows 2^53. This chapter is that map.
""",
    idea=r"""
**One number type.** `number` covers integers and fractions alike, stored as
a binary floating-point value with about 15-17 significant decimal digits.
Most decimal fractions — `0.1`, `0.2`, `1.005` — have no exact binary form, so
what is stored is the nearest representable value.

- `0.1 + 0.2 === 0.3` is `false`. Compare with a tolerance when fractions are
  involved: `Math.abs(a - b) < 1e-9`.
- `toFixed(n)` rounds the *stored* value, which can sit just below the decimal
  you wrote: `(1.005).toFixed(2)` is `"1.00"`.
- `Math.round` rounds halves **up**, towards +∞: `Math.round(2.5)` is `3` but
  `Math.round(-2.5)` is `-2`.

**Money in cents.** Store prices as integers — `1999`, not `19.99` — and
integer arithmetic stays exact. Convert to a decimal string only when printing:
`(cents / 100).toFixed(2)`.

**Integers, and their limit.** Integer values are exact up to
`Number.MAX_SAFE_INTEGER` (2^53 − 1, about 9·10^15). `Number.isInteger(x)` asks
whether a value has no fractional part; `Number.isSafeInteger(x)` also checks it
is within that range. Beyond it, consecutive integers collapse together.

**`bigint`.** For exact integers of any size: a literal ends in `n` (`123n`),
or convert with `BigInt("123")`. `bigint` and `number` do not mix in
arithmetic — the compiler rejects `1n + 1` — and `bigint` division truncates.

**Formatting for people.** `toFixed` for a fixed number of decimals.
`Intl.NumberFormat` for grouping and currency, in a fixed locale so the output
is deterministic:

```ts
new Intl.NumberFormat("en-US").format(1234567.891);                       // "1,234,567.891"
new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(19.5); // "$19.50"
```
""",
    examples=[
        ("Where the float shows",
         r"""
const sum = 0.1 + 0.2;
console.log(sum);
console.log(sum === 0.3);
console.log(Math.abs(sum - 0.3) < 1e-9);
console.log((1.005).toFixed(2), (1.015).toFixed(2));
console.log(Math.round(2.5), Math.round(-2.5));
""", [""],
         "Every line is the same story: the stored value is a hair away from the decimal on the page, and each operation sees the stored value."),
        ("Money as integer cents",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const prices = input.split(/\s+/).map((p) => Math.round(Number(p) * 100));
let totalCents = 0;
for (const cents of prices) totalCents += cents;
console.log("items:", prices.join(" "));
console.log("total: $" + (totalCents / 100).toFixed(2));
""", ["0.10 0.20", "19.99 5.01 0.10", "0.1 0.2 0.3"],
         "Converting each price to cents once — rounding at that moment — keeps every later sum exact. Only the final print turns cents back into dollars."),
        ("Past 2^53, and `bigint`",
         r"""
const big = Number.MAX_SAFE_INTEGER;
console.log(big, Number.isSafeInteger(big + 1));
console.log(big + 1 === big + 2);
let factorial = 1n;
for (let i = 1n; i <= 25n; i++) factorial *= i;
console.log(factorial.toString());
console.log(7n / 2n);
""", [""],
         "`big + 1` and `big + 2` are the same double — the integers have run out of bits. The `bigint` factorial is exact, and `bigint` division truncates towards zero."),
        ("Formatting for people",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const n = Number(input);
const grouped = new Intl.NumberFormat("en-US");
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const percent = new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 });
console.log(grouped.format(n));
console.log(money.format(n));
console.log(percent.format(n / 100));
""", ["1234567.891", "19.5", "-0.25"],
         "Passing an explicit locale (`\"en-US\"`) makes the output the same on every machine — the default locale varies."),
    ],
    errors=[
        (2365, r"""
const count = 10n;
const total = count + 1;
console.log(total);
""", "`bigint` and `number` never mix in arithmetic — not even `+ 1`. Write `count + 1n`, or convert one side on purpose with `Number(...)` / `BigInt(...)`."),
        (2362, r"""
const price = "19.99";
const doubled = price * 2;
console.log(doubled);
""", "A string that *looks* like a number is still a string. Convert it first; TypeScript will not do it implicitly the way JavaScript's `*` would."),
    ],
    pitfalls=[
        ("Summing decimal prices directly",
         r"""
import * as fs from "fs";
const prices = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let total = 0;
for (const p of prices) total += p;
console.log(total);
""",
         r"""
import * as fs from "fs";
const prices = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let cents = 0;
for (const p of prices) cents += Math.round(p * 100);
console.log((cents / 100).toFixed(2));
""",
         "Float errors accumulate with every addition and then get printed. Add integer cents instead, and format once.",
         ["0.1 0.2 0.3"]),
        ("`toFixed` rounds the stored value",
         r"""
import * as fs from "fs";
const price = Number(fs.readFileSync(0, "utf8").trim());
console.log(price.toFixed(2));
""",
         r"""
import * as fs from "fs";
const text = fs.readFileSync(0, "utf8").trim();
const cents = Math.round(Number(text + "e2"));
console.log((cents / 100).toFixed(2));
""",
         "`1.005` is stored as `1.00499999…`, so `toFixed(2)` rounds it down — and so does `Math.round(1.005 * 100)`, because the multiplication inherits the same error. Shifting the decimal point *in the text* (`\"1.005e2\"` is exactly `100.5`) rounds the number the person actually typed.",
         ["1.005"]),
        ("`Math.round` and negative halves",
         r"""
const values = [2.5, -2.5, -0.5];
console.log(values.map((v) => Math.round(v)).join(" "));
""",
         r"""
const roundHalfAway = (v: number) => Math.sign(v) * Math.round(Math.abs(v));
const values = [2.5, -2.5, -0.5];
console.log(values.map(roundHalfAway).join(" "));
""",
         "`Math.round` rounds halves towards +∞, so `-2.5` becomes `-2` and `-0.5` becomes `-0` (printed `0`). If the task says \"round half away from zero\", apply it to the magnitude and restore the sign."),
        ("A count that outgrows `number`",
         r"""
let ways = 1;
for (let i = 1; i <= 25; i++) ways *= i;
console.log(ways);
""",
         r"""
let ways = 1n;
for (let i = 1n; i <= 25n; i++) ways *= i;
console.log(ways.toString());
""",
         "25! is about 1.55·10^25 — far past 2^53 — so the `number` result is only an approximation printed in exponent form. `bigint` keeps every digit."),
    ],
    later=[
        "**Week 7 — Arrays.** `reduce` for totals — with the same cents discipline.",
        "**Week 16 — Branded types.** A `Cents` brand so a dollar amount can never be passed where cents are expected.",
        "**Week 25 — Errors.** Parsing numbers from untrusted text into a `Result` instead of a silent `NaN`.",
    ],
    exercises=[
        _drill("ts_number_format-cents", "Add money in cents",
               "The input is a line of prices like `19.99`. Replace `____` so each price becomes a whole number of cents, rounding once, before it is added.",
               r"""
import * as fs from "fs";
const prices = fs.readFileSync(0, "utf8").trim().split(/\s+/).map(Number);
let cents = 0;
for (const p of prices) cents += Math.round(p * 100);
console.log(cents);
console.log((cents / 100).toFixed(2));
""", ["Math.round(p * 100)"], ["0.1 0.2 0.3", "19.99 0.01", "1.10 2.20 3.30", "5"],
               hint="`p * 100` is nearly an integer; `Math.round` makes it one."),
        _drill("ts_number_format-big", "Exact big factorials",
               "The input is `n` (up to 40). Replace `____` so the loop multiplies `bigint` values and the factorial stays exact.",
               r"""
import * as fs from "fs";
const n = BigInt(fs.readFileSync(0, "utf8").trim());
let result = 1n;
for (let i = 2n; i <= n; i++) result *= i;
console.log(result.toString());
console.log(result.toString().length);
""", ["for (let i = 2n; i <= n; i++) result *= i;"], ["5", "25", "40", "0"],
               hint="Every operand must be a `bigint`: start the counter at `2n`."),
        _drill("ts_number_format-grouped", "Print it for people",
               "The input is a number. Replace `____` with a formatter that groups thousands in the `en-US` locale.",
               r"""
import * as fs from "fs";
const n = Number(fs.readFileSync(0, "utf8").trim());
const grouped = new Intl.NumberFormat("en-US");
console.log(grouped.format(n));
""", ['new Intl.NumberFormat("en-US")'], ["1234567", "999", "-1000000.5", "0.125"],
               hint="`Intl.NumberFormat` with an explicit locale."),
        _chal("ts_number_format-bill", "Split the bill", "Medium",
              "The input is `total people tipPercent` on one line, e.g. `100.00 3 15`. Work in whole cents: the tip is `total × tipPercent / 100` rounded to the nearest cent, the grand total is the sum, and each person pays the grand total divided by the number of people **rounded up** to the next cent. Print `tip $x.xx`, `total $x.xx` and `each $x.xx`, then `extra $x.xx` — how much rounding up collects beyond the grand total.",
              r"""
const [totalText = "0", peopleText = "1", tipText = "0"] = input.split(/\s+/);
const baseCents = Math.round(Number(totalText) * 100);
const people = Number(peopleText);
const tipCents = Math.round((baseCents * Number(tipText)) / 100);
const grandCents = baseCents + tipCents;
const eachCents = Math.ceil(grandCents / people);
const money = (cents: number) => "$" + (cents / 100).toFixed(2);
console.log("tip " + money(tipCents));
console.log("total " + money(grandCents));
console.log("each " + money(eachCents));
console.log("extra " + money(eachCents * people - grandCents));
""", ["100.00 3 15", "10 1 0", "59.99 4 20", "0.10 3 10", "250 7 12.5"],
              hint="Convert the total to cents once, do integer arithmetic, and use `Math.ceil` for the per-person share."),
    ],
    quiz=[
        _cq("Why is `0.1 + 0.2 === 0.3` false?", "Neither 0.1 nor 0.2 has an exact binary representation",
            ["TypeScript rounds decimals", "`===` compares references for numbers", "It is true under `strict`"],
            "The stored values are the nearest doubles; their sum is a hair above 0.3."),
        _cq("How should an app store a price of $19.99?", "As the integer `1999` (cents)",
            ["As the number `19.99`", "As the string `\"19.99\"` and parse it every time", "As a `bigint`"],
            "Integer arithmetic is exact; format to dollars only when printing."),
        _cq("`Math.round(-2.5)`?", "`-2`", ["`-3`", "`-2.5`", "`NaN`"],
            "`Math.round` rounds halves towards +∞."),
        _cq("`1n + 1`?", "A compile error: `bigint` and `number` can't be mixed",
            ["`2n`", "`2`", "`\"11\"`"],
            "Mixing needs an explicit conversion (TS2365 at compile time, a TypeError at runtime)."),
        _cq("What is `Number.MAX_SAFE_INTEGER`?", "2^53 − 1, the largest integer every smaller integer is exact below",
            ["The largest `number` at all", "2^31 − 1", "2^64 − 1"],
            "Past it, adjacent integers share one double. `Number.MAX_VALUE` is the largest finite number, a different thing."),
        _cq("Why pass `\"en-US\"` to `Intl.NumberFormat` in a judged program?", "So the output doesn't depend on the machine's locale",
            ["It's required", "It's faster", "Other locales can't format currency"],
            "The default locale varies between machines; tests need one fixed format."),
    ],
    interview=[
        ("Why shouldn't you use floating point for money?",
         "Most decimal amounts aren't exactly representable in binary, so sums drift (`0.1 + 0.2`) and rounding surprises you (`1.005.toFixed(2)`). Store integer minor units — cents — and format at the edge, or use a decimal library when you need arbitrary precision."),
        ("When do you reach for `bigint`?",
         "When integers can exceed 2^53 − 1: IDs from other systems, factorials and combinatorics, cryptography. It's exact but slower, can't mix with `number` without explicit conversion, and `JSON.stringify` refuses it by default."),
        ("How do you compare two floating-point results?",
         "With a tolerance scaled to the problem — `Math.abs(a - b) < 1e-9`, or relative to the magnitude for large values — never with `===` after arithmetic."),
    ],
)


_chapter(
    "ts_regex", "TS: Language Basics",
    "Regular Expressions",
    "Pattern matching on text: literals and `new RegExp`, flags, `test`, `match`, `matchAll`, `replace` and `replaceAll`, capture groups and named groups.",
    "A regular expression describes a *shape* of text — \"one or more digits\", \"a word followed by an equals sign\" — and lets you test for it, find every occurrence, pull out the parts, or replace them. Most text-processing problems that take twenty lines of index arithmetic take one pattern. TypeScript types the results precisely: a failed `match` is `null`, a capture group may be `undefined`, and the compiler makes you handle both.",
    "`java.util.regex` puts patterns in strings (`\"\\\\d+\"`), compiles them with `Pattern.compile` and walks them with a `Matcher`. JavaScript has regex *literals* — `/\\d+/g` — with the same syntax, and the string methods (`match`, `replace`, `split`) take them directly.",
    why=r"""
Text in the wild has structure that fixed indexes can't see: a date that may be
`2026-9-4` or `2026-09-04`, words separated by any mix of spaces and
punctuation, `key=value` pairs with optional spaces around the `=`. Code that
walks such text character by character is long and fragile.

A regular expression states the structure once, and the engine does the
walking. The cost is a small, dense language — and a few traps that this
chapter points out before they cost you a wrong answer.
""",
    idea=r"""
**Writing one.** A literal between slashes, optionally followed by flags:
`/\d+/g`. Or build one from a string at runtime: `new RegExp("\\d+", "g")` —
note the doubled backslash, because the string needs escaping first.

**The pieces you'll use most.**

| pattern | matches |
|---|---|
| `\d` `\w` `\s` | a digit, a word character (`[A-Za-z0-9_]`), whitespace |
| `.` | any character except a newline |
| `[aeiou]` `[^,]` | one of these / anything but these |
| `x*` `x+` `x?` `x{2,4}` | 0+, 1+, 0-1, 2-4 repetitions |
| `^` `$` | start and end of the string (of each line with `m`) |
| `(…)` `(?<name>…)` | a capture group / a named capture group |
| `a\|b` | either alternative |

**Flags.** `g` finds *every* match rather than the first; `i` ignores case;
`m` makes `^`/`$` match at line boundaries; `u` treats the pattern as
Unicode code points.

**Using one.**

- `re.test(s)` — does it match anywhere? A `boolean`.
- `s.match(re)` — without `g`: the first match with its groups, or `null`.
  With `g`: every matched string, or `null`.
- `s.matchAll(re)` — with `g`: an iterator of full match objects, groups and
  all. The tool for "extract every key=value pair".
- `s.replace(re, replacement)` / `s.replaceAll(...)` — the replacement can use
  `$1` or `$<name>`, or be a function of the match.
- `s.split(re)` — split on a pattern, e.g. `/\s+/` or `/[,;]\s*/`.

**What the types say.** `match` returns `RegExpMatchArray | null`, so you must
handle "no match" before reading it. A group is `string | undefined` under
`noUncheckedIndexedAccess`, and named groups live in `m.groups`, which may be
`undefined` too.

**Anchor when you validate.** `/\d+/.test("abc123")` is `true` — it found
digits somewhere. To require the *whole* string to be digits, anchor it:
`/^\d+$/`.
""",
    examples=[
        ("Test, and the anchoring trap",
         r"""
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
for (const line of lines) {
  const hasDigits = /\d+/.test(line);
  const allDigits = /^\d+$/.test(line);
  console.log(`${line}: contains ${hasDigits}, is ${allDigits}`);
}
""", ["123\nabc123\nabc"],
         "Without `^` and `$`, a pattern matches anywhere — fine for searching, wrong for validating."),
        ("Every key=value pair, with named groups",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const pair = /(?<key>\w+)\s*=\s*(?<value>[^;]*)/g;
for (const m of input.matchAll(pair)) {
  const key = m.groups?.key ?? "?";
  const value = (m.groups?.value ?? "").trim();
  console.log(`${key} -> [${value}]`);
}
""", ["host=example.com; port = 8080;debug=true", "name = Ada Lovelace"],
         "`matchAll` needs the `g` flag and yields one full match per pair. `m.groups` is typed as possibly `undefined`, so the lookups carry a fallback."),
        ("Replacing with groups and functions",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
console.log(input.replace(/(\d{4})-(\d{2})-(\d{2})/g, "$3/$2/$1"));
console.log(input.replaceAll(/\d+/g, (digits) => String(Number(digits) * 2)));
console.log(input.split(/[\s,;]+/).length);
""", ["due 2026-09-24, paid 2026-10-01"],
         "`$1`… refer to capture groups in a replacement string; a function receives each match and returns its replacement."),
    ],
    errors=[
        (18047, r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const m = input.match(/(\d+)-(\d+)/);
console.log(m.length);
""", "A match can fail, and then `match` returns `null`. Check it — `if (m === null) …` — or use `?.` before reading anything from it."),
        (2532, r"""
const m = "a=1".match(/(\w+)=(\w+)/);
if (m !== null) {
  const value: string = m[2].toUpperCase();
  console.log(value);
}
""", "With `noUncheckedIndexedAccess`, `m[2]` is `string | undefined`: the compiler can't know the group took part in the match. Handle the `undefined` (`m[2] ?? \"\"`) or check it.", "strict+indexed"),
    ],
    pitfalls=[
        ("`replace` with a string replaces only the first",
         r"""
const text = "a-b-c-d";
console.log(text.replace("-", "+"));
""",
         r"""
const text = "a-b-c-d";
console.log(text.replaceAll("-", "+"));
""",
         "A string pattern (or a regex without `g`) replaces one occurrence. `replaceAll`, or a regex with the `g` flag, replaces every one."),
        ("A `g` regex remembers where it stopped",
         r"""
const digits = /\d/g;
const inputs = ["7", "8", "9"];
console.log(inputs.map((s) => digits.test(s)).join(" "));
""",
         r"""
const digits = /\d/;
const inputs = ["7", "8", "9"];
console.log(inputs.map((s) => digits.test(s)).join(" "));
""",
         "With `g`, `test` starts from `lastIndex` and updates it, so reusing one regex across strings gives alternating answers. Don't use `g` for plain testing."),
        ("Special characters in a pattern built from text",
         r"""
const price = "1.5";
const re = new RegExp(price);
console.log(re.test("125"));
""",
         r"""
const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const price = "1.5";
const re = new RegExp(escape(price));
console.log(re.test("125"));
""",
         "`.` means \"any character\", so a pattern built from `\"1.5\"` matches `125`. Escape user text before turning it into a pattern."),
    ],
    later=[
        "**Week 4 — Unicode.** The `u` flag, and why `.` can split an emoji in half without it.",
        "**Week 22 — Template literal types.** Parsing strings at the *type* level — a cousin of the patterns here.",
        "**Week 25 — Errors.** Validating input with anchored patterns and reporting *which* line failed.",
    ],
    exercises=[
        _drill("ts_regex-valid", "Validate the whole string",
               "Each input line should be a US-style ZIP code: exactly five digits. Replace `____` with a pattern that accepts only that — not five digits *somewhere* in the line.",
               r"""
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
const zip = /^\d{5}$/;
for (const line of lines) console.log(zip.test(line.trim()) ? "valid" : "invalid");
""", ["/^\\d{5}$/"], ["12345\n1234\n123456\nabcde", "90210", "x12345"],
               hint="Anchor both ends with `^` and `$`, and count with `{5}`."),
        _drill("ts_regex-count", "Count every number",
               "Replace `____` with a pattern that, with `match`, finds every run of digits in the line (so `a12b3` has two numbers).",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const found = input.match(/\d+/g) ?? [];
console.log(found.length);
console.log(found.join(" ") || "(none)");
""", ["/\\d+/g"], ["a12b3", "no digits", "10 20 30", "007x"],
               hint="One or more digits, and the flag that finds every match."),
        _drill("ts_regex-swap", "Reorder with groups",
               "Each line is `Last, First`. Replace `____` with the replacement string that turns it into `First Last`, using the two capture groups.",
               r"""
import * as fs from "fs";
const lines = fs.readFileSync(0, "utf8").trim().split("\n");
for (const line of lines) console.log(line.trim().replace(/^(\w+),\s*(\w+)$/, "$2 $1"));
""", ['"$2 $1"'], ["Lovelace, Ada\nHopper,Grace", "Turing, Alan"],
               hint="`$1` is the first group, `$2` the second."),
        _chal("ts_regex-log", "Parse a log", "Medium",
              "Each input line is a log entry like `2026-09-24 12:05:33 ERROR [db] connection lost`. Lines that don't have that shape are ignored. Print one line per level that occurs, in the order ERROR, WARN, INFO, as `<LEVEL> <count>`, skipping levels that never occur; then print the distinct components in square brackets, sorted, space-separated (or `(none)`).",
              r"""
const entry = /^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (ERROR|WARN|INFO) \[(\w+)\] (.*)$/;
const counts = new Map<string, number>();
const components = new Set<string>();
for (const line of input.split("\n")) {
  const m = line.trim().match(entry);
  if (m === null) continue;
  const level = m[3] ?? "";
  counts.set(level, (counts.get(level) ?? 0) + 1);
  components.add(m[4] ?? "");
}
for (const level of ["ERROR", "WARN", "INFO"]) {
  const n = counts.get(level);
  if (n !== undefined) console.log(level + " " + n);
}
console.log([...components].sort().join(" ") || "(none)");
""", ["2026-09-24 12:05:33 ERROR [db] connection lost\n2026-09-24 12:05:34 INFO [api] retrying\n2026-09-24 12:05:35 ERROR [db] still down",
      "garbage\n2026-01-01 00:00:00 WARN [cache] cold start",
      "nothing to see",
      "2026-09-24 1:05:33 ERROR [db] bad time\n2026-09-24 01:05:33 DEBUG [db] unknown level\n2026-09-24 01:05:33 INFO [auth] ok"],
              hint="Anchor the pattern, capture the level and the component, and skip lines where `match` returns `null`."),
    ],
    quiz=[
        _cq("What does `/\\d+/.test(\"abc123\")` return?", "`true` — it matches digits anywhere",
            ["`false` — the string isn't all digits", "`\"123\"`", "`null`"],
            "Unanchored patterns match anywhere. `^…$` makes it about the whole string."),
        _cq("What does `\"a1b22\".match(/\\d+/g)` return?", "`[\"1\", \"22\"]`",
            ["`[\"1\"]`", "`true`", "An iterator of match objects"],
            "With `g`, `match` returns every matched string (or `null` when there are none)."),
        _cq("Why is `m[1]` typed `string | undefined` under `noUncheckedIndexedAccess`?",
            "The compiler can't know a group took part in the match",
            ["Because regexes are untyped", "Because `match` returns `any`", "It isn't; it's `string`"],
            "Optional groups really can be `undefined`, and index reads are honest under that flag."),
        _cq("In a replacement string, what is `$<year>`?", "The text of the named group `year`",
            ["A template literal", "The whole match", "A literal dollar sign"],
            "Named groups can be referenced by name in replacements and read from `m.groups`."),
        _cq("Which flag makes `^` and `$` match at each line?", "`m`", ["`g`", "`i`", "`s`"],
            "`m` is multiline; `s` makes `.` match newlines."),
        _cq("Why build patterns from user text carefully?", "Characters like `.` and `*` have special meaning and must be escaped",
            ["`new RegExp` can't take variables", "It's slower", "User text can't contain letters"],
            "Unescaped, `\"1.5\"` becomes a pattern where `.` matches any character."),
    ],
    interview=[
        ("When would you use a regex, and when not?",
         "For recognising or extracting simple shapes in text — tokens, dates, key/value pairs, validation of a format. Not for nested structure (HTML, JSON, balanced parentheses): that needs a real parser. And a clear string method beats a clever pattern."),
        ("`match` versus `matchAll`?",
         "`match` with `g` gives just the matched strings; without `g`, the first match with its groups. `matchAll` (which requires `g`) gives every match *with* its groups and index — what you want for extraction."),
        ("What is the `lastIndex` gotcha?",
         "A regex with `g` or `y` is stateful: `test` and `exec` continue from `lastIndex`. Reusing one across calls gives alternating results. Use a non-global regex for testing, or reset `lastIndex`."),
    ],
)


_chapter(
    "ts_unicode", "TS: Language Basics",
    "Unicode — Code Units, Code Points & Graphemes",
    "Why `\"😀\".length` is 2: UTF-16 code units, iterating by code point with `for…of`, user-perceived characters with `Intl.Segmenter`, the `u` regex flag, and comparing text with `localeCompare`.",
    "A JavaScript string is a sequence of UTF-16 code units. Most characters are one unit, but emoji and many historic scripts take two (a surrogate pair), and what a reader sees as one character — an accented letter, a flag, a family emoji — can be several code points joined together. `length`, indexing, `split(\"\")` and `reverse` all work in code units and will cut these apart. This chapter shows which operation counts what, and how to count what the user sees.",
    "Java's `String` is UTF-16 too, with the same surrogate-pair traps (`length()` versus `codePointCount`). Here `for…of` and `[...s]` walk code points, and `Intl.Segmenter` gives grapheme clusters — the closest thing to \"characters\" a user would count.",
    why=r"""
"Reverse the string", "count the letters", "truncate to 10 characters" — they
all seem to need no thought, and they all break on real text. A name with an
accent written as two code points, an emoji in a chat message, a flag made of
two regional-indicator letters: code-unit operations split them and print
garbage or a replacement character.

You don't need to know Unicode in depth. You need to know which of three
"character" counts an operation uses, and which one the task means.
""",
    idea=r"""
**Three levels.**

| level | example `"é"` written as `e` + combining accent | `"😀"` |
|---|---|---|
| UTF-16 code units — `length`, `s[i]`, `split("")` | 2 | 2 |
| code points — `for…of`, `[...s]`, `codePointAt` | 2 | 1 |
| graphemes (what a reader sees) — `Intl.Segmenter` | 1 | 1 |

**Code units.** `s.length` and `s[i]` count 16-bit units. Characters outside
the Basic Multilingual Plane — most emoji — take two, a *surrogate pair*;
splitting between them leaves two meaningless halves.

**Code points.** `for (const ch of s)` and `[...s]` iterate by code point,
so an emoji stays whole. `s.codePointAt(i)` reads one, and
`String.fromCodePoint(n)` builds one.

**Graphemes.** A user-perceived character can be several code points: a
letter plus combining marks, a flag (two regional indicators), a skin-tone or
family emoji joined with zero-width joiners. `Intl.Segmenter` splits text the
way a cursor moves:

```ts
const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
const chars = [...seg.segment(text)].map((s) => s.segment);
```

**Normalisation.** `"é"` can be one code point (U+00E9) or two (`e` + U+0301).
They *look* identical and are not `===`. `s.normalize("NFC")` puts both in
the composed form before you compare or count.

**Regex and sorting.** Add the `u` flag so `.` and character classes work on
code points. Sort human text with `a.localeCompare(b)` rather than `<`, which
compares code units.
""",
    examples=[
        ("Three answers to \"how long is it?\"",
         r"""
const words = ["cat", "café", "😀", "🇯🇵"];
const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
for (const w of words) {
  const units = w.length;
  const points = [...w].length;
  const graphemes = [...seg.segment(w)].length;
  console.log(`${w}: ${units} units, ${points} points, ${graphemes} graphemes`);
}
""", [""],
         "The flag is two code points (regional indicators J and P), each a surrogate pair — four code units that a reader sees as one character."),
        ("Reversing without breaking emoji",
         r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const byUnits = input.split("").reverse().join("");
const byPoints = [...input].reverse().join("");
console.log(byPoints);
console.log(byUnits === byPoints ? "same either way" : "units version is broken");
""", ["hello", "hi 😀!"],
         "Reversing code units swaps the two halves of the emoji's surrogate pair, producing invalid text. Spreading into code points keeps it whole."),
        ("Same look, different strings",
         r"""
const composed: string = "café";
const decomposed: string = "café";
console.log(composed.length, decomposed.length);
console.log(composed === decomposed);
console.log(composed.normalize("NFC") === decomposed.normalize("NFC"));
console.log(["b", "a", "Z", "é"].sort().join(" "));
console.log(["b", "a", "Z", "é"].sort((x, y) => x.localeCompare(y, "en")).join(" "));
""", [""],
         "Normalise before comparing text that came from different sources. (The `: string` annotations matter: as `const` literals the two would have different literal types, and the compiler would flag the comparison as impossible — which, for text arriving at runtime, it isn't.) And `sort()` orders by code unit — uppercase before lowercase, accented letters after `z` — while `localeCompare` sorts the way a dictionary does."),
    ],
    errors=[
        (2322, r"""
const first: string = "😀".codePointAt(0);
console.log(first);
""", "`codePointAt` returns a `number` — the code point — and `undefined` when the index is out of range. Convert back with `String.fromCodePoint(...)` if you want the character."),
        (2554, r"""
const s = "héllo";
console.log(s.normalize("NFC", "strict"));
""", "`normalize` takes at most one argument: the form (`\"NFC\"`, `\"NFD\"`, `\"NFKC\"` or `\"NFKD\"`)."),
    ],
    pitfalls=[
        ("Truncating by `slice` cuts an emoji",
         r"""
const message = "ok 👍👍";
const preview = message.slice(0, 4);
console.log(preview, preview.length, preview.isWellFormed());
""",
         r"""
const message = "ok 👍👍";
const preview = [...message].slice(0, 4).join("");
console.log(preview, preview.length, preview.isWellFormed());
""",
         "`slice(0, 4)` keeps four code *units*: `o`, `k`, space, and half of the first thumbs-up. `isWellFormed()` reports the broken surrogate. Slicing the code-point array keeps characters whole."),
        ("Counting letters with `length`",
         r"""
const name = "Zoë 🙂";
console.log(`${name.length} characters`);
""",
         r"""
const name = "Zoë 🙂";
const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
console.log(`${[...seg.segment(name)].length} characters`);
""",
         "`length` counts code units, so the emoji counts twice. For \"how many characters would a person count\", segment into graphemes."),
        ("Sorting names with `sort()`",
         r"""
const names = ["émile", "Zoe", "adam", "Bea"];
console.log(names.sort().join(" "));
""",
         r"""
const names = ["émile", "Zoe", "adam", "Bea"];
console.log(names.sort((a, b) => a.localeCompare(b, "en")).join(" "));
""",
         "The default sort compares UTF-16 code units: every uppercase letter comes before every lowercase one, and `é` after `z`. `localeCompare` with a fixed locale sorts like a dictionary."),
    ],
    later=[
        "**Week 7 — Arrays.** `Array.from(s)` and the spread operator as the code-point-safe way to turn text into an array.",
        "**Week 9 — Maps & Sets.** Counting characters with a `Map` — by code point, so emoji count once.",
        "**Week 22 — Template literal types.** String manipulation at the type level works on code units too.",
    ],
    exercises=[
        _drill("ts_unicode-points", "Count code points",
               "Replace `____` so `points` is the number of code points in the input — emoji count once.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const points = [...input].length;
console.log(input.length, points);
""", ["[...input].length"], ["hello", "hi 😀", "🇯🇵", "日本語"],
               hint="Spreading a string iterates it by code point."),
        _drill("ts_unicode-reverse", "Reverse safely",
               "Replace `____` with an expression that reverses the input by code point, keeping emoji intact.",
               r"""
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
const reversed = [...input].reverse().join("");
console.log(reversed);
console.log(reversed.isWellFormed());
""", ["[...input].reverse().join(\"\")"], ["stressed", "a😀b", "🙂🙃"],
               hint="Spread into code points, reverse the array, join it back."),
        _drill("ts_unicode-sort", "Sort like a dictionary",
               "The input is a line of words. Replace `____` with the comparator that sorts them the way an English dictionary would, ignoring the uppercase-first rule of the default sort.",
               r"""
import * as fs from "fs";
const words = fs.readFileSync(0, "utf8").trim().split(/\s+/);
const sorted = [...words].sort((a, b) => a.localeCompare(b, "en"));
console.log(sorted.join(" "));
""", ['(a, b) => a.localeCompare(b, "en")'], ["banana Apple cherry", "Zed apple Émile", "b a"],
               hint="`localeCompare` with a fixed locale, returning a number for `sort`."),
        _chal("ts_unicode-truncate", "Truncate for a preview", "Medium",
              "Each input line is `n text…`: a width `n` and a message. Print the message truncated to at most `n` user-perceived characters (graphemes); when it had to be cut, replace its last kept grapheme with `…` so the result is still `n` graphemes long. Messages that already fit are printed unchanged.",
              r"""
const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
for (const line of input.split("\n")) {
  const space = line.indexOf(" ");
  const width = Number(line.slice(0, space));
  const text = line.slice(space + 1);
  const graphemes = [...seg.segment(text)].map((s) => s.segment);
  if (graphemes.length <= width) {
    console.log(text);
  } else {
    console.log(graphemes.slice(0, width - 1).join("") + "…");
  }
}
""", ["5 hello world\n20 short enough", "3 👍👍👍👍", "4 🇯🇵🇫🇷🇩🇪🇮🇹🇪🇸", "6 Zoë says hi"],
              hint="Segment into graphemes first; then it's ordinary array slicing."),
    ],
    quiz=[
        _cq("What is `\"😀\".length`?", "2", ["1", "4", "It depends on the font"],
            "`length` counts UTF-16 code units, and this emoji is a surrogate pair."),
        _cq("Which walks a string by code point?", "`for (const ch of s)`",
            ["`for (let i = 0; i < s.length; i++)`", "`s.split(\"\")`", "`s.charAt(i)`"],
            "String iteration is by code point; indexing and `split(\"\")` are by code unit."),
        _cq("What splits text into user-perceived characters?", "`Intl.Segmenter` with `granularity: \"grapheme\"`",
            ["`[...s]`", "`s.split(\"\")`", "`Array.from(s)`"],
            "Code points aren't enough for flags or accented letters written with combining marks."),
        _cq("Two strings look identical but aren't `===`. What's a likely cause?",
            "Different Unicode normalisation — composed vs decomposed accents",
            ["Trailing zeros", "Different fonts", "The `u` flag"],
            "Normalise both with `s.normalize(\"NFC\")` before comparing."),
        _cq("Why sort names with `localeCompare` rather than the default `sort()`?",
            "The default compares code units, putting uppercase first and accents last",
            ["`sort()` can't sort strings", "`localeCompare` is faster", "The default sort is random"],
            "`localeCompare` orders text the way a reader expects."),
        _cq("What does the `u` flag change in a regex?", "It treats the pattern and input as code points",
            ["It makes the match case-insensitive", "It finds every match", "Nothing in modern engines"],
            "Without `u`, `.` matches a single code unit and can split an emoji."),
    ],
    interview=[
        ("Why can `\"😀\".length` be 2?",
         "JavaScript strings are UTF-16, and characters outside the Basic Multilingual Plane take two code units — a surrogate pair. `length` and indexing count code units; `for…of` and spread count code points."),
        ("How would you count the characters a user sees?",
         "With `Intl.Segmenter` at grapheme granularity. Code points still split flags, combining accents and ZWJ emoji sequences; grapheme clusters are what a cursor moves over."),
        ("Two strings render the same but compare unequal. Why?",
         "Usually normalisation: `é` as one code point versus `e` plus a combining accent. Normalise both to NFC before comparing, hashing or using them as keys."),
    ],
)
