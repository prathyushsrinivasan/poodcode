# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The 8-month structured TypeScript course.
#
# This file is exec()'d inside gen_seed.py's namespace AFTER typescript_defs.py
# and typescript_expand.py, so it can reuse their helpers `tsx` / `tsc` / `_P`.
# It defines a single global `TS_COURSE` (dict) which gen_seed writes to
# src-tauri/seeds/ts_course.json (served by the `ts_course` command).
#
# HARD DESIGN RULE (the user's core ask): a week may only require syntax and
# concepts introduced in that week or earlier. Weeks 1-8 below are authored to
# obey this strictly — e.g. no loops before Week 4, no arrays before Week 6, no
# `interface` before Week 8. Weeks 9-32 are themed skeletons (authored=False)
# shown as "coming soon"; they are authored in later batches.
#
# EXECUTION MODEL: exercises run through the SAME stdin/stdout judge as every
# other Learn drill, via Node type-stripping (see exec.rs). So every blank
# targets RUNTIME code (never a bare type annotation), programs read stdin with
# `fs.readFileSync(0, "utf8")`, and expected output is matched exactly (after
# whitespace normalization). Each `solution` is verified end-to-end by
# tests/verify_ts_course.rs (runs it through the real judge, asserts Accepted).
# ---------------------------------------------------------------------------


def _prog(src):
    return _P(src)


def _q(question, options, answer, explanation):
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def _lesson(key, title, what, lesson_md, exercises, quiz=None):
    return {
        "key": key,
        "title": title,
        "what": what,
        "lesson": _prog(lesson_md) if lesson_md else "",
        "exercises": exercises,
        "quiz": quiz or [],
    }


def _cap_auto(title, brief, exercise):
    return {"title": title, "brief": brief, "kind": "auto", "exercise": exercise}


def _cap_brief(title, brief):
    return {"title": title, "brief": brief, "kind": "brief", "exercise": None}


def _week(number, month, month_title, theme, goal, summary, lessons,
          capstone=None, authored=True):
    return {
        "number": number,
        "month": month,
        "month_title": month_title,
        "theme": theme,
        "goal": goal,
        "summary": _prog(summary) if summary else "",
        "authored": authored,
        "lessons": lessons,
        "capstone": capstone,
    }


def _skel(number, month, month_title, theme, goal, summary=""):
    return _week(number, month, month_title, theme, goal, summary, [], None,
                 authored=False)


_WEEKS = []

# ===========================================================================
# MONTH 1 — Absolute basics: output, values, decisions, loops
# ===========================================================================
_M1 = "First Steps: Values, Logic & Loops"

# --- Week 1 ---------------------------------------------------------------
_WEEKS.append(_week(
    1, 1, _M1,
    "Output & Variables",
    "Write a program that prints text and does arithmetic with named values.",
    """
Welcome! This is the very beginning — no prior coding needed. This week you'll
run your first TypeScript program, print things to the screen, store values in
named variables, and do some arithmetic. That's genuinely all a lot of programs
do: take some values, combine them, and print a result.

Everything you write here runs and is **checked instantly**. Replace the
`____` in each drill with the missing piece, then press **Check**.
""",
    [
        _lesson(
            "w1-hello", "Your first program",
            "Printing text with console.log.",
            """
A **program** is a list of instructions the computer runs top to bottom. The
instruction you'll use most is `console.log(...)`, which prints its argument
followed by a newline.

```ts
console.log("Hello, world!");
```

Text wrapped in quotes is called a **string**. `console.log` can print strings,
numbers, and more. Every statement ends with a semicolon `;`.
""",
            [
                tsx("tscourse-w1-hello-1", "Print a greeting",
                    "Make the program print exactly: Hello, world!",
                    _prog('console.log("Hello, world!");\n'),
                    ['"Hello, world!"'],
                    [("", "Hello, world!")],
                    hint='A string is text in double quotes.'),
                tsx("tscourse-w1-hello-2", "Print two lines",
                    "Print two lines: first `Line one`, then `Line two`.",
                    _prog('console.log("Line one");\nconsole.log("Line two");\n'),
                    ['"Line two"'],
                    [("", "Line one\nLine two")],
                    hint="Each console.log prints its own line."),
            ],
            quiz=[
                _q("What does console.log do?",
                   ["Reads a line of input", "Prints its argument, then a newline",
                    "Deletes a variable", "Defines a function"],
                   1, "console.log writes its argument to the output followed by a newline."),
                _q("Which of these is a string?",
                   ["42", "true", '"cat"', "x + 1"],
                   2, "A string is text wrapped in quotes, like \"cat\"."),
            ],
        ),
        _lesson(
            "w1-variables", "Variables: let and const",
            "Naming values so you can reuse them.",
            """
A **variable** is a named box for a value. Declare one with `const` (the name
keeps one value for good) or `let` (you can reassign it later). Prefer `const`
unless you truly need to change the value.

```ts
const name = "Ada";
let count = 0;
count = count + 1;
console.log(name);   // Ada
console.log(count);  // 1
```

Both are **block-scoped**: they exist only inside the `{ }` they're declared in.
""",
            [
                tsx("tscourse-w1-var-1", "Name a value",
                    "Store the string `Ada` in `name`, so the program prints `Hello, Ada`.",
                    _prog('const name = "Ada";\nconsole.log("Hello, " + name);\n'),
                    ['"Ada"'],
                    [("", "Hello, Ada")],
                    hint='Joining strings with + is called concatenation.'),
                tsx("tscourse-w1-var-2", "Reassign with let",
                    "Reassign `count` to 2 so the program prints 2.",
                    _prog('let count = 1;\ncount = 2;\nconsole.log(count);\n'),
                    ['count = 2;'],
                    [("", "2")],
                    hint="Reassignment is `count = 2;` — no `let` the second time."),
            ],
        ),
        _lesson(
            "w1-numbers", "Numbers & arithmetic",
            "Doing math with +, -, *, / and %.",
            """
TypeScript has one `number` type for whole numbers and decimals alike. The
operators are `+` `-` `*` `/` and `%` (remainder — what's left after division).

```ts
console.log(6 * 7);    // 42
console.log(17 % 5);   // 2  (17 = 3*5 + 2)
console.log(10 / 4);   // 2.5
```
""",
            [
                tsx("tscourse-w1-num-1", "Multiply",
                    "Print the product of `a` and `b` (should be 42).",
                    _prog('const a = 6;\nconst b = 7;\nconsole.log(a * b);\n'),
                    ['a * b'],
                    [("", "42")],
                    hint="Use the * operator."),
                tsx("tscourse-w1-num-2", "Remainder",
                    "Print the remainder of `total` divided by 5.",
                    _prog('const total = 17;\nconsole.log(total % 5);\n'),
                    ['total % 5'],
                    [("", "2")],
                    hint="`%` gives the remainder."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Receipt printer",
        """
Put Week 1 together. Using only `const`, arithmetic, and string joining, print a
two-line receipt for **4 coffees at $3 each**:

```
Coffee x4
Total: $12
```

The scaffold declares the item, price, and quantity. Fill in the calculation and
the two `console.log` lines.
""",
        tsc("tscourse-w1-capstone", "Receipt printer", "Intro",
            "Print the item line and the total line exactly as shown.",
            _prog(
                'const item = "Coffee";\n'
                'const price = 3;\n'
                'const qty = 4;\n'
                'const total = price * qty;\n'
                'console.log(item + " x" + qty);\n'
                'console.log("Total: $" + total);\n'),
            'const total = price * qty;\n'
            'console.log(item + " x" + qty);\n'
            'console.log("Total: $" + total);',
            [("", "Coffee x4\nTotal: $12")],
            hint='total is price * qty; build each line by joining strings with +.'),
    ),
))

# --- Week 2 ---------------------------------------------------------------
_WEEKS.append(_week(
    2, 1, _M1,
    "Strings & Input",
    "Read input from the user and build text with template literals and string tools.",
    """
Last week your programs always printed the same thing. This week they react to
**input**. You'll read what the user types, then shape text with **template
literals** and a few everyday **string methods**.

From now on most programs start by reading standard input:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
```

`fs.readFileSync(0, "utf8")` reads everything the user typed as one string;
`.trim()` removes the trailing newline.
""",
    [
        _lesson(
            "w2-input", "Reading input",
            "Getting text from standard input.",
            """
Reading input is boilerplate you'll reuse constantly. Read it all, trim it, and
you have a string to work with.

```ts
import * as fs from "fs";
const line = fs.readFileSync(0, "utf8").trim();
console.log(line);   // echoes what was typed
```
""",
            [
                tsx("tscourse-w2-input-1", "Echo the input",
                    "Read the whole input (trimmed) and print it back.",
                    _prog('import * as fs from "fs";\n'
                          'const input = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(input);\n'),
                    ['fs.readFileSync(0, "utf8").trim()'],
                    [("hello\n", "hello"), ("  spaced  ", "spaced")],
                    hint='readFileSync(0, "utf8") reads stdin; .trim() drops surrounding whitespace.'),
                tsx("tscourse-w2-input-2", "Greet the input",
                    "Read a name and print `Hello, <name>!`.",
                    _prog('import * as fs from "fs";\n'
                          'const name = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log("Hello, " + name + "!");\n'),
                    ['"Hello, " + name + "!"'],
                    [("Ada", "Hello, Ada!")],
                    hint="Join the pieces with +."),
            ],
            quiz=[
                _q("Why call .trim() on the input?",
                   ["To make it uppercase", "To remove the trailing newline and stray spaces",
                    "To convert it to a number", "To split it into words"],
                   1, "Input usually ends in a newline; .trim() removes surrounding whitespace."),
                _q("What type does fs.readFileSync(0, \"utf8\") return?",
                   ["number", "boolean", "string", "an array"],
                   2, "With the \"utf8\" encoding it returns the input as a string."),
            ],
        ),
        _lesson(
            "w2-templates", "Template literals",
            "Splicing values into text with backticks.",
            """
Backtick strings let you drop values straight into text with `${ }` — much
clearer than gluing pieces with `+`.

```ts
const name = "Sam";
const age = 3;
console.log(`Hi ${name}, you are ${age}`);   // Hi Sam, you are 3
console.log(`2 + 2 = ${2 + 2}`);              // 2 + 2 = 4
```
""",
            [
                tsx("tscourse-w2-tmpl-1", "Welcome message",
                    "Use a template literal to print `Hi <name>, welcome!`.",
                    _prog('import * as fs from "fs";\n'
                          'const name = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(`Hi ${name}, welcome!`);\n'),
                    ['`Hi ${name}, welcome!`'],
                    [("Sam", "Hi Sam, welcome!")],
                    hint="Use backticks and ${name}."),
                tsx("tscourse-w2-tmpl-2", "Inline arithmetic",
                    "Print `<a> + <b> = <sum>` using a template literal.",
                    _prog('const a = 3;\nconst b = 4;\n'
                          'console.log(`${a} + ${b} = ${a + b}`);\n'),
                    ['`${a} + ${b} = ${a + b}`'],
                    [("", "3 + 4 = 7")],
                    hint="You can put an expression like a + b inside ${ }."),
            ],
        ),
        _lesson(
            "w2-methods", "String methods",
            "Inspecting and transforming text.",
            """
Strings come with handy built-in methods:

```ts
const s = "hello";
console.log(s.length);         // 5   (a property, no parentheses)
console.log(s.toUpperCase());  // HELLO
console.log(s.includes("ell")); // true
console.log(s.slice(0, 3));    // hel
```
""",
            [
                tsx("tscourse-w2-meth-1", "Shout it",
                    "Print the input in UPPERCASE.",
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(s.toUpperCase());\n'),
                    ['s.toUpperCase()'],
                    [("hello", "HELLO")],
                    hint="Call .toUpperCase() on the string."),
                tsx("tscourse-w2-meth-2", "Count the letters",
                    "Print how many characters the input has.",
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(s.length);\n'),
                    ['s.length'],
                    [("hello", "5"), ("hi", "2")],
                    hint="length is a property — no parentheses."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Name card",
        """
Read a single name and print a three-line card:

```
Name: Ada
Letters: 3
Shout: ADA
```

Use a template literal for each line, plus `.length` and `.toUpperCase()`.
""",
        tsc("tscourse-w2-capstone", "Name card", "Intro",
            "Print the three lines exactly, based on the input name.",
            _prog('import * as fs from "fs";\n'
                  'const name = fs.readFileSync(0, "utf8").trim();\n'
                  'console.log(`Name: ${name}`);\n'
                  'console.log(`Letters: ${name.length}`);\n'
                  'console.log(`Shout: ${name.toUpperCase()}`);\n'),
            'console.log(`Name: ${name}`);\n'
            'console.log(`Letters: ${name.length}`);\n'
            'console.log(`Shout: ${name.toUpperCase()}`);',
            [("Ada", "Name: Ada\nLetters: 3\nShout: ADA"),
             ("bo", "Name: bo\nLetters: 2\nShout: BO")],
            hint="One template-literal console.log per line."),
    ),
))

# --- Week 3 ---------------------------------------------------------------
_WEEKS.append(_week(
    3, 1, _M1,
    "Making Decisions",
    "Branch on conditions with if/else and combine tests with boolean logic.",
    """
Programs get interesting when they **choose** what to do. This week: comparisons
that produce `true`/`false`, `if`/`else` branching, and the logical operators
`&&` (and), `||` (or), `!` (not).

One new helper you'll need: input arrives as **text**, so wrap it in `Number(...)`
when you want to do math or numeric comparisons:

```ts
const n = Number(fs.readFileSync(0, "utf8").trim());  // "42" -> 42
```
""",
    [
        _lesson(
            "w3-compare", "Booleans & comparison",
            "Values that are true or false.",
            """
Comparisons produce a **boolean** (`true` or `false`). Always compare with
`===` / `!==` (strict — no surprise conversions), plus `<`, `>`, `<=`, `>=`.

```ts
console.log(5 > 3);        // true
console.log("a" === "b");  // false
console.log(10 >= 10);     // true
```
""",
            [
                tsx("tscourse-w3-cmp-1", "Greater than ten",
                    "Print whether the number is greater than 10.",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'console.log(n > 10);\n'),
                    ['n > 10'],
                    [("15", "true"), ("3", "false")],
                    hint="Use the > operator; console.log prints true/false."),
                tsx("tscourse-w3-cmp-2", "Exact match",
                    'Print whether the input equals the string `yes`.',
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(s === "yes");\n'),
                    ['s === "yes"'],
                    [("yes", "true"), ("no", "false")],
                    hint="Use === for a strict comparison."),
            ],
            quiz=[
                _q("Which operator should you use to compare for equality?",
                   ["=", "==", "===", "=>"],
                   2, "=== is strict equality (no type coercion). = is assignment."),
                _q("What does Number(\"7\") produce?",
                   ['the string "7"', "the number 7", "true", "an error"],
                   1, "Number(...) converts a numeric string into a number."),
            ],
        ),
        _lesson(
            "w3-ifelse", "if / else",
            "Choosing between branches.",
            """
`if` runs a block when its condition is true; `else` covers the other case, and
`else if` chains more tests.

```ts
if (score >= 90) {
  console.log("A");
} else if (score >= 80) {
  console.log("B");
} else {
  console.log("C");
}
```

Only the first matching branch runs.
""",
            [
                tsx("tscourse-w3-if-1", "Sign of a number",
                    "Print `non-negative` when n >= 0, otherwise `negative`.",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'if (n >= 0) {\n'
                          '  console.log("non-negative");\n'
                          '} else {\n'
                          '  console.log("negative");\n'
                          '}\n'),
                    ['n >= 0'],
                    [("5", "non-negative"), ("-2", "negative"), ("0", "non-negative")],
                    hint="Zero counts as non-negative, so use >=."),
                tsx("tscourse-w3-if-2", "Letter grade",
                    "Fill the middle test so 85 prints B (>=80), 95 prints A, 70 prints C.",
                    _prog('import * as fs from "fs";\n'
                          'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'if (score >= 90) {\n'
                          '  console.log("A");\n'
                          '} else if (score >= 80) {\n'
                          '  console.log("B");\n'
                          '} else {\n'
                          '  console.log("C");\n'
                          '}\n'),
                    ['score >= 80'],
                    [("95", "A"), ("85", "B"), ("70", "C")],
                    hint="The B branch is for scores of 80 or more."),
            ],
        ),
        _lesson(
            "w3-logic", "Logical operators",
            "Combining conditions with && , || and !.",
            """
- `a && b` is true only when **both** are true.
- `a || b` is true when **either** is true.
- `!a` flips a boolean.

```ts
console.log(n >= 1 && n <= 5);   // in range 1..5 ?
console.log(s === "y" || s === "yes");
```
""",
            [
                tsx("tscourse-w3-log-1", "In range",
                    "Print whether n is between 1 and 5 (inclusive).",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'console.log(n >= 1 && n <= 5);\n'),
                    ['n >= 1 && n <= 5'],
                    [("3", "true"), ("9", "false"), ("1", "true")],
                    hint="Both conditions must hold, so use &&."),
                tsx("tscourse-w3-log-2", "Yes in either form",
                    'Print true when the input is `y` or `yes`.',
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(s === "y" || s === "yes");\n'),
                    ['s === "y" || s === "yes"'],
                    [("yes", "true"), ("y", "true"), ("n", "false")],
                    hint="Either spelling is acceptable, so use ||."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Ticket pricing",
        """
Read a person's **age** and print their ticket price:

- under 5 → `Free`
- 5 to 17 → `$10`
- 65 and over → `$12`
- everyone else → `$20`

Fill in the `if`/`else if`/`else` chain.
""",
        tsc("tscourse-w3-capstone", "Ticket pricing", "Easy",
            "Print the correct price for the given age.",
            _prog('import * as fs from "fs";\n'
                  'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                  'if (age < 5) {\n'
                  '  console.log("Free");\n'
                  '} else if (age < 18) {\n'
                  '  console.log("$10");\n'
                  '} else if (age >= 65) {\n'
                  '  console.log("$12");\n'
                  '} else {\n'
                  '  console.log("$20");\n'
                  '}\n'),
            'if (age < 5) {\n'
            '  console.log("Free");\n'
            '} else if (age < 18) {\n'
            '  console.log("$10");\n'
            '} else if (age >= 65) {\n'
            '  console.log("$12");\n'
            '} else {\n'
            '  console.log("$20");\n'
            '}',
            [("3", "Free"), ("12", "$10"), ("70", "$12"), ("30", "$20"),
             ("65", "$12"), ("5", "$10")],
            hint="Order matters — test the youngest and oldest bands with the right cutoffs."),
    ),
))

# --- Week 4 ---------------------------------------------------------------
_WEEKS.append(_week(
    4, 1, _M1,
    "Loops",
    "Repeat work with while and for loops, and accumulate results.",
    """
Computers shine at doing the same thing many times. This week you'll meet
`while` and `for` loops, the idea of an **accumulator** (a running total or
counter), and `for...of` for walking through text a character at a time.
""",
    [
        _lesson(
            "w4-while", "while loops",
            "Repeat while a condition holds.",
            """
A `while` loop runs its body over and over as long as its condition is true. Be
sure something inside moves toward making the condition false, or it runs
forever.

```ts
let i = 1;
let sum = 0;
while (i <= 5) {
  sum = sum + i;
  i = i + 1;
}
console.log(sum);   // 15
```
""",
            [
                tsx("tscourse-w4-while-1", "Sum 1..n",
                    "Loop while i <= n, adding each i to sum. Print the total.",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'let sum = 0;\n'
                          'let i = 1;\n'
                          'while (i <= n) {\n'
                          '  sum = sum + i;\n'
                          '  i = i + 1;\n'
                          '}\n'
                          'console.log(sum);\n'),
                    ['i <= n'],
                    [("5", "15"), ("1", "1"), ("10", "55")],
                    hint="Keep going while i has not passed n."),
                tsx("tscourse-w4-while-2", "Countdown",
                    "Print n, n-1, ... down to 1, each on its own line.",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'let i = n;\n'
                          'while (i >= 1) {\n'
                          '  console.log(i);\n'
                          '  i = i - 1;\n'
                          '}\n'),
                    ['i = i - 1;'],
                    [("3", "3\n2\n1"), ("1", "1")],
                    hint="Move i toward 0 each pass so the loop ends."),
            ],
            quiz=[
                _q("What is an 'accumulator'?",
                   ["A type of loop", "A variable that builds up a result across iterations",
                    "A comparison operator", "A way to read input"],
                   1, "An accumulator (like a running sum or counter) collects a result as the loop runs."),
                _q("What happens if a while loop's condition never becomes false?",
                   ["It runs once", "It never runs", "It loops forever", "It prints an error"],
                   2, "Without progress toward ending, the loop runs forever (an infinite loop)."),
            ],
        ),
        _lesson(
            "w4-for", "for loops",
            "A compact counting loop.",
            """
A `for` loop packs the setup, condition, and step into one line:

```ts
for (let i = 1; i <= n; i = i + 1) {
  // body runs for i = 1, 2, ... n
}
```

It's the same idea as `while`, just tidier when you're counting.
""",
            [
                tsx("tscourse-w4-for-1", "Factorial",
                    "Multiply 1*2*...*n into product. Print it.",
                    _prog('import * as fs from "fs";\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'let product = 1;\n'
                          'for (let i = 1; i <= n; i = i + 1) {\n'
                          '  product = product * i;\n'
                          '}\n'
                          'console.log(product);\n'),
                    ['product = product * i;'],
                    [("5", "120"), ("1", "1"), ("4", "24")],
                    hint="Each pass multiplies the running product by i."),
                tsx("tscourse-w4-for-2", "Count evens",
                    "Count how many numbers from 1..10 are even. Print the count.",
                    _prog('const n = 10;\n'
                          'let count = 0;\n'
                          'for (let i = 1; i <= n; i = i + 1) {\n'
                          '  if (i % 2 === 0) {\n'
                          '    count = count + 1;\n'
                          '  }\n'
                          '}\n'
                          'console.log(count);\n'),
                    ['i % 2 === 0'],
                    [("", "5")],
                    hint="A number is even when its remainder mod 2 is 0."),
            ],
        ),
        _lesson(
            "w4-forof", "Looping over text",
            "for...of walks a string character by character.",
            """
`for...of` hands you each item of a sequence in turn. For a string, that's each
character.

```ts
let vowels = 0;
for (const ch of "hello") {
  if (ch === "e" || ch === "o") {
    vowels = vowels + 1;
  }
}
console.log(vowels);   // 2
```
""",
            [
                tsx("tscourse-w4-of-1", "Count a letter",
                    'Count how many times the letter `a` appears in the input.',
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'let count = 0;\n'
                          'for (const ch of s) {\n'
                          '  if (ch === "a") {\n'
                          '    count = count + 1;\n'
                          '  }\n'
                          '}\n'
                          'console.log(count);\n'),
                    ['ch === "a"'],
                    [("banana", "3"), ("xyz", "0")],
                    hint="Compare each character to \"a\"."),
                tsx("tscourse-w4-of-2", "Reverse a string",
                    "Build the input backwards by putting each new char in front.",
                    _prog('import * as fs from "fs";\n'
                          'const s = fs.readFileSync(0, "utf8").trim();\n'
                          'let out = "";\n'
                          'for (const ch of s) {\n'
                          '  out = ch + out;\n'
                          '}\n'
                          'console.log(out);\n'),
                    ['ch + out'],
                    [("abc", "cba"), ("hello", "olleh")],
                    hint="Prepend each character: ch + out."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "FizzBuzz",
        """
The classic. Read a number **n** and print the numbers `1` to `n`, one per line,
with two twists:

- multiples of 3 → `Fizz`
- multiples of 5 → `Buzz`
- multiples of both → `FizzBuzz`

Fill in the loop body (test the both-case first!).
""",
        tsc("tscourse-w4-capstone", "FizzBuzz", "Easy",
            "Print 1..n applying the Fizz / Buzz / FizzBuzz rules.",
            _prog('import * as fs from "fs";\n'
                  'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                  'for (let i = 1; i <= n; i = i + 1) {\n'
                  '  if (i % 15 === 0) {\n'
                  '    console.log("FizzBuzz");\n'
                  '  } else if (i % 3 === 0) {\n'
                  '    console.log("Fizz");\n'
                  '  } else if (i % 5 === 0) {\n'
                  '    console.log("Buzz");\n'
                  '  } else {\n'
                  '    console.log(i);\n'
                  '  }\n'
                  '}\n'),
            'if (i % 15 === 0) {\n'
            '    console.log("FizzBuzz");\n'
            '  } else if (i % 3 === 0) {\n'
            '    console.log("Fizz");\n'
            '  } else if (i % 5 === 0) {\n'
            '    console.log("Buzz");\n'
            '  } else {\n'
            '    console.log(i);\n'
            '  }',
            [("5", "1\n2\nFizz\n4\nBuzz"), ("3", "1\n2\nFizz"),
             ("15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz")],
            hint="Check divisibility by 15 before 3 and 5, or the both-case never fires."),
    ),
))

# ===========================================================================
# MONTH 2 — Data & functions
# ===========================================================================
_M2 = "Data & Functions"

# --- Week 5 ---------------------------------------------------------------
_WEEKS.append(_week(
    5, 2, _M2,
    "Functions",
    "Package logic into reusable functions with parameters and return values.",
    """
A **function** is a named, reusable piece of logic: give it inputs
(**parameters**), it hands back a result (**return value**). Functions let you
name an idea once and use it everywhere. This week: declaring functions, arrow
functions, and returning values.

You'll see type annotations like `(x: number): number` — they document what goes
in and comes out. (They're checked while you write, then stripped before the
program runs.)
""",
    [
        _lesson(
            "w5-declare", "Declaring functions",
            "function name(params) { return ... }",
            """
```ts
function square(x: number): number {
  return x * x;
}
console.log(square(5));   // 25
```

`return` sends a value back to whoever called the function and ends it.
""",
            [
                tsx("tscourse-w5-dec-1", "Square",
                    "Return x times itself.",
                    _prog('function square(x: number): number {\n'
                          '  return x * x;\n'
                          '}\n'
                          'console.log(square(5));\n'),
                    ['x * x'],
                    [("", "25")],
                    hint="Multiply x by x."),
                tsx("tscourse-w5-dec-2", "Greet",
                    "Return a greeting string for the given name.",
                    _prog('function greet(name: string): string {\n'
                          '  return `Hello, ${name}!`;\n'
                          '}\n'
                          'console.log(greet("Ada"));\n'),
                    ['`Hello, ${name}!`'],
                    [("", "Hello, Ada!")],
                    hint="Return a template literal using name."),
            ],
            quiz=[
                _q("What does `return` do?",
                   ["Prints a value", "Sends a value back to the caller and ends the function",
                    "Declares a variable", "Starts a loop"],
                   1, "return produces the function's result and stops its execution."),
                _q("In `function f(x: number)`, what is `x`?",
                   ["A return value", "A parameter (an input to the function)",
                    "A global variable", "A type alias"],
                   1, "x is a parameter — a named input the caller supplies."),
            ],
        ),
        _lesson(
            "w5-params", "Parameters & return values",
            "Passing inputs and using the result.",
            """
Functions compose: the value one returns can feed into more logic.

```ts
function double(x: number): number {
  return x * 2;
}
const n = 21;
console.log(double(n));   // 42
```
""",
            [
                tsx("tscourse-w5-par-1", "Double the input",
                    "Return x doubled, then print double(n) for the input n.",
                    _prog('import * as fs from "fs";\n'
                          'function double(x: number): number {\n'
                          '  return x * 2;\n'
                          '}\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'console.log(double(n));\n'),
                    ['x * 2'],
                    [("21", "42"), ("0", "0")],
                    hint="Multiply the parameter by 2."),
                tsx("tscourse-w5-par-2", "Absolute value",
                    "Return the negation of x when x is negative.",
                    _prog('import * as fs from "fs";\n'
                          'function abs(x: number): number {\n'
                          '  if (x < 0) {\n'
                          '    return -x;\n'
                          '  }\n'
                          '  return x;\n'
                          '}\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'console.log(abs(n));\n'),
                    ['-x'],
                    [("-5", "5"), ("7", "7")],
                    hint="The opposite of x is -x."),
            ],
        ),
        _lesson(
            "w5-arrow", "Arrow functions",
            "A shorter way to write small functions.",
            """
Arrow functions are compact. When the body is a single expression, its value is
returned automatically (no `return` needed).

```ts
const cube = (x: number): number => x * x * x;
console.log(cube(3));   // 27
```
""",
            [
                tsx("tscourse-w5-arr-1", "Cube (arrow)",
                    "Return x cubed from the arrow function.",
                    _prog('const cube = (x: number): number => x * x * x;\n'
                          'console.log(cube(3));\n'),
                    ['x * x * x'],
                    [("", "27")],
                    hint="x times x times x."),
                tsx("tscourse-w5-arr-2", "Triple (arrow)",
                    "Return x * 3, then print triple(n) for the input.",
                    _prog('import * as fs from "fs";\n'
                          'const triple = (x: number): number => x * 3;\n'
                          'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                          'console.log(triple(n));\n'),
                    ['x * 3'],
                    [("5", "15"), ("10", "30")],
                    hint="Multiply x by 3."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Temperature converter",
        """
Write two functions and use them together. Read a Celsius temperature and print:

1. that temperature in Fahrenheit (`C * 9 / 5 + 32`)
2. the result converted back to Celsius (`(F - 32) * 5 / 9`) — which should equal
   what you started with

For input `100`:

```
212
100
```
""",
        tsc("tscourse-w5-capstone", "Temperature converter", "Easy",
            "Fill in the two function bodies.",
            _prog('import * as fs from "fs";\n'
                  'function cToF(c: number): number {\n'
                  '  return c * 9 / 5 + 32;\n'
                  '}\n'
                  'function fToC(f: number): number {\n'
                  '  return (f - 32) * 5 / 9;\n'
                  '}\n'
                  'const c = Number(fs.readFileSync(0, "utf8").trim());\n'
                  'console.log(cToF(c));\n'
                  'console.log(fToC(cToF(c)));\n'),
            'function cToF(c: number): number {\n'
            '  return c * 9 / 5 + 32;\n'
            '}\n'
            'function fToC(f: number): number {\n'
            '  return (f - 32) * 5 / 9;\n'
            '}',
            [("100", "212\n100"), ("0", "32\n0")],
            hint="cToF is c*9/5+32; fToC reverses it with (f-32)*5/9."),
    ),
))

# --- Week 6 ---------------------------------------------------------------
_WEEKS.append(_week(
    6, 2, _M2,
    "Arrays",
    "Store lists of values and process them with loops and array methods.",
    """
An **array** holds an ordered list of values, reached by index (`nums[0]` is the
first). This week: creating and indexing arrays, iterating them, and the trio
`map` / `filter` / `reduce` that makes list-processing concise.

To read a line of numbers into an array:

```ts
const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);
```

`.split(" ")` cuts the text into pieces at spaces; `.map(Number)` turns each
piece into a number.
""",
    [
        _lesson(
            "w6-basics", "Creating & indexing",
            "Arrays and their indexes.",
            """
```ts
const names = ["Ada", "Bo", "Cy"];
console.log(names[0]);      // Ada   (indexes start at 0)
console.log(names.length);  // 3
```
""",
            [
                tsx("tscourse-w6-b-1", "First number",
                    "Read the numbers and print the first one.",
                    _prog('import * as fs from "fs";\n'
                          'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                          'console.log(nums[0]);\n'),
                    ['nums[0]'],
                    [("3 5 7", "3"), ("9", "9")],
                    hint="The first element is at index 0."),
                tsx("tscourse-w6-b-2", "How many",
                    "Print how many space-separated words the input has.",
                    _prog('import * as fs from "fs";\n'
                          'const words = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                          'console.log(words.length);\n'),
                    ['words.length'],
                    [("a b c d", "4"), ("hi", "1")],
                    hint="length gives the number of elements."),
            ],
            quiz=[
                _q("What index is the first element of an array?",
                   ["1", "0", "-1", "It depends"],
                   1, "Arrays are zero-indexed: the first element is at index 0."),
                _q("What does \"3 5 7\".split(\" \") produce?",
                   ['the number 357', 'the array ["3", "5", "7"]', 'the string "357"', "an error"],
                   1, "split cuts the string at each space into an array of pieces."),
            ],
        ),
        _lesson(
            "w6-iterate", "Iterating & accumulating",
            "Walk an array with for...of.",
            """
```ts
let sum = 0;
for (const x of [1, 2, 3, 4]) {
  sum = sum + x;
}
console.log(sum);   // 10
```
""",
            [
                tsx("tscourse-w6-it-1", "Sum the list",
                    "Add every number and print the total.",
                    _prog('import * as fs from "fs";\n'
                          'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                          'let sum = 0;\n'
                          'for (const x of nums) {\n'
                          '  sum = sum + x;\n'
                          '}\n'
                          'console.log(sum);\n'),
                    ['sum = sum + x;'],
                    [("1 2 3 4", "10"), ("5", "5")],
                    hint="Add each x to the running sum."),
                tsx("tscourse-w6-it-2", "Largest",
                    "Track and print the largest number in the list.",
                    _prog('import * as fs from "fs";\n'
                          'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                          'let best = nums[0];\n'
                          'for (const x of nums) {\n'
                          '  if (x > best) {\n'
                          '    best = x;\n'
                          '  }\n'
                          '}\n'
                          'console.log(best);\n'),
                    ['x > best'],
                    [("3 9 2 7", "9"), ("4", "4")],
                    hint="Replace best whenever x is bigger."),
            ],
        ),
        _lesson(
            "w6-methods", "map, filter, reduce",
            "Transform, select, and combine.",
            """
- `map` makes a new array by transforming each element.
- `filter` keeps only elements that pass a test.
- `join` glues an array back into a string.

```ts
const nums = [1, 2, 3];
console.log(nums.map((x) => x * 2).join(" "));   // 2 4 6
console.log(nums.filter((x) => x % 2 === 1).length); // 2
```
""",
            [
                tsx("tscourse-w6-m-1", "Count evens",
                    "Keep the even numbers and print how many there are.",
                    _prog('import * as fs from "fs";\n'
                          'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                          'const evens = nums.filter((x) => x % 2 === 0);\n'
                          'console.log(evens.length);\n'),
                    ['x % 2 === 0'],
                    [("1 2 3 4 5 6", "3"), ("1 3 5", "0")],
                    hint="Even means remainder 0 mod 2."),
                tsx("tscourse-w6-m-2", "Double them",
                    "Double every number and print them space-separated.",
                    _prog('import * as fs from "fs";\n'
                          'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                          'const doubled = nums.map((x) => x * 2);\n'
                          'console.log(doubled.join(" "));\n'),
                    ['x * 2'],
                    [("1 2 3", "2 4 6"), ("10", "20")],
                    hint="map transforms each x to x * 2."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Number stats",
        """
Read a line of numbers and print three stats:

```
sum 14
max 5
count 5
```

for input `3 1 4 1 5`. Fill in the loop that computes the sum and max, then the
three report lines.
""",
        tsc("tscourse-w6-capstone", "Number stats", "Easy",
            "Compute sum and max in one pass, then print the report.",
            _prog('import * as fs from "fs";\n'
                  'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                  'let sum = 0;\n'
                  'let max = nums[0];\n'
                  'for (const x of nums) {\n'
                  '  sum = sum + x;\n'
                  '  if (x > max) {\n'
                  '    max = x;\n'
                  '  }\n'
                  '}\n'
                  'console.log(`sum ${sum}`);\n'
                  'console.log(`max ${max}`);\n'
                  'console.log(`count ${nums.length}`);\n'),
            'let sum = 0;\n'
            'let max = nums[0];\n'
            'for (const x of nums) {\n'
            '  sum = sum + x;\n'
            '  if (x > max) {\n'
            '    max = x;\n'
            '  }\n'
            '}\n'
            'console.log(`sum ${sum}`);\n'
            'console.log(`max ${max}`);\n'
            'console.log(`count ${nums.length}`);',
            [("3 1 4 1 5", "sum 14\nmax 5\ncount 5"), ("10", "sum 10\nmax 10\ncount 1")],
            hint="Start max at nums[0], then update sum and max together in one loop."),
    ),
))

# --- Week 7 ---------------------------------------------------------------
_WEEKS.append(_week(
    7, 2, _M2,
    "Objects",
    "Model structured data with objects, and combine them with arrays.",
    """
An **object** groups related values under named keys — perfect for modeling a
'thing' like a user or a product. This week: object literals, reading and
updating properties, and arrays of objects (the shape of most real data).

```ts
const user = { name: "Ada", age: 36 };
console.log(user.name);   // Ada
user.age = user.age + 1;  // update a property
```
""",
    [
        _lesson(
            "w7-basics", "Object basics",
            "Keys, values, and dot access.",
            """
Reach a property with dot notation: `obj.key`. You can read it or, on a `const`
object, still change its properties.

```ts
const point = { x: 3, y: 4 };
console.log(point.x);        // 3
point.y = point.y + 1;       // 5
```
""",
            [
                tsx("tscourse-w7-b-1", "Read a property",
                    "Print the user's name.",
                    _prog('const user = { name: "Ada", age: 36 };\n'
                          'console.log(user.name);\n'),
                    ['user.name'],
                    [("", "Ada")],
                    hint="Access it with user.name."),
                tsx("tscourse-w7-b-2", "Update a property",
                    "Add 5 to counter.value, then print it.",
                    _prog('const counter = { value: 0 };\n'
                          'counter.value = counter.value + 5;\n'
                          'console.log(counter.value);\n'),
                    ['counter.value + 5'],
                    [("", "5")],
                    hint="Read the current value and add 5."),
            ],
            quiz=[
                _q("How do you read the `name` property of `user`?",
                   ["user[name]", "user->name", "user.name", "name(user)"],
                   2, "Dot notation: user.name."),
                _q("An object is best for...",
                   ["An ordered list of values", "Grouping related values under named keys",
                    "Repeating an action", "Comparing two numbers"],
                   1, "Objects group related fields (name, age, ...) under keys."),
            ],
        ),
        _lesson(
            "w7-funcs", "Objects & functions",
            "Passing objects around.",
            """
Functions can take and return objects. Annotate the shape inline or with a type
(you'll formalize this next week).

```ts
function fullName(p: { first: string; last: string }): string {
  return `${p.first} ${p.last}`;
}
console.log(fullName({ first: "Ada", last: "Lovelace" }));
```
""",
            [
                tsx("tscourse-w7-f-1", "Full name",
                    "Return the first and last name joined by a space.",
                    _prog('function fullName(p: { first: string; last: string }): string {\n'
                          '  return `${p.first} ${p.last}`;\n'
                          '}\n'
                          'console.log(fullName({ first: "Ada", last: "Lovelace" }));\n'),
                    ['`${p.first} ${p.last}`'],
                    [("", "Ada Lovelace")],
                    hint="Template literal with p.first and p.last."),
                tsx("tscourse-w7-f-2", "Build from input",
                    "Store a greeting on the object, then print it.",
                    _prog('import * as fs from "fs";\n'
                          'const name = fs.readFileSync(0, "utf8").trim();\n'
                          'const user = { name: name, greeting: `Hi ${name}` };\n'
                          'console.log(user.greeting);\n'),
                    ['`Hi ${name}`'],
                    [("Sam", "Hi Sam")],
                    hint="The greeting is a template literal using name."),
            ],
        ),
        _lesson(
            "w7-arrays", "Arrays of objects",
            "The shape of real datasets.",
            """
Most data is a list of records — an array of objects. Loop over it and reach
into each one.

```ts
const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];
let total = 0;
for (const p of people) {
  total = total + p.age;
}
console.log(total);   // 56
```
""",
            [
                tsx("tscourse-w7-a-1", "Total ages",
                    "Sum everyone's age and print it.",
                    _prog('const people = [\n'
                          '  { name: "Ada", age: 36 },\n'
                          '  { name: "Bo", age: 20 },\n'
                          '];\n'
                          'let total = 0;\n'
                          'for (const p of people) {\n'
                          '  total = total + p.age;\n'
                          '}\n'
                          'console.log(total);\n'),
                    ['total + p.age'],
                    [("", "56")],
                    hint="Add each person's age to total."),
                tsx("tscourse-w7-a-2", "Count adults",
                    "Count people aged 21 or older and print the count.",
                    _prog('const people = [\n'
                          '  { name: "Ada", age: 36 },\n'
                          '  { name: "Bo", age: 20 },\n'
                          '];\n'
                          'const adults = people.filter((p) => p.age >= 21);\n'
                          'console.log(adults.length);\n'),
                    ['p.age >= 21'],
                    [("", "1")],
                    hint="Keep people whose age is at least 21."),
            ],
        ),
    ],
    capstone=_cap_brief(
        "Design: a tiny library catalog",
        """
A **free-build** project (no auto-grader — build it your way, then mark the week
done). In the editor, model a small **library**:

1. Represent each book as an object with `title`, `author`, and `available`
   (a boolean).
2. Put several books in an array.
3. Write a function that takes the array and prints a report: how many books
   there are, and the titles of the ones currently available.

Try to use everything from Weeks 1–7: variables, loops, functions, arrays, and
objects. There's no single right answer — experiment. When you're happy with the
output, click **Mark done**.
""",
    ),
))

# --- Week 8 ---------------------------------------------------------------
_WEEKS.append(_week(
    8, 2, _M2,
    "Types that Describe Your Data",
    "Annotate values and name shapes with type aliases and interfaces.",
    """
You've used TypeScript's types implicitly all along. This week you make them
explicit: **annotations** on values and functions, and naming reusable shapes
with **`interface`** and **`type`**. Well-named types are documentation the
compiler checks for you.

Remember: types are erased before the program runs, so the drills still exercise
runtime logic — the annotations are there to describe it.
""",
    [
        _lesson(
            "w8-annotations", "Annotations & inference",
            "Writing types on values and functions.",
            """
```ts
const price: number = 10;
const label: string = "Total";
function repeat(s: string, n: number): string {
  return s.repeat(n);
}
```

Often you can omit annotations and let TypeScript **infer** them — but writing
them on function parameters and returns is good practice.
""",
            [
                tsx("tscourse-w8-an-1", "Typed total",
                    "Compute price * qty into the annotated total.",
                    _prog('const price: number = 10;\n'
                          'const qty: number = 3;\n'
                          'const total: number = price * qty;\n'
                          'console.log(total);\n'),
                    ['price * qty'],
                    [("", "30")],
                    hint="Multiply the two annotated numbers."),
                tsx("tscourse-w8-an-2", "Typed repeat",
                    "Return the string repeated n times.",
                    _prog('function repeat(s: string, n: number): string {\n'
                          '  return s.repeat(n);\n'
                          '}\n'
                          'console.log(repeat("ab", 3));\n'),
                    ['s.repeat(n)'],
                    [("", "ababab")],
                    hint="Strings have a .repeat(n) method."),
            ],
            quiz=[
                _q("What happens to type annotations when the program runs?",
                   ["They slow it down", "They are stripped away — types are compile-time only",
                    "They become comments", "They turn into console.logs"],
                   1, "TypeScript types are erased before execution; they guide you and the compiler, not the runtime."),
                _q("What does `interface` do?",
                   ["Creates a running object", "Names the shape of an object type",
                    "Loops over an array", "Reads input"],
                   1, "An interface names a reusable object shape (its properties and their types)."),
            ],
        ),
        _lesson(
            "w8-interfaces", "Interfaces & type aliases",
            "Naming the shape of your data.",
            """
Name a shape once, use it everywhere:

```ts
interface Point { x: number; y: number; }
type User = { name: string; admin: boolean };

function dist(p: Point): number {
  return Math.abs(p.x) + Math.abs(p.y);
}
```

`Math.abs(n)` gives the distance of n from zero (its absolute value).
""",
            [
                tsx("tscourse-w8-if-1", "Manhattan distance",
                    "Return |p.x| + |p.y| using Math.abs.",
                    _prog('interface Point {\n'
                          '  x: number;\n'
                          '  y: number;\n'
                          '}\n'
                          'function dist(p: Point): number {\n'
                          '  return Math.abs(p.x) + Math.abs(p.y);\n'
                          '}\n'
                          'console.log(dist({ x: 3, y: -4 }));\n'),
                    ['Math.abs(p.x) + Math.abs(p.y)'],
                    [("", "7")],
                    hint="Add the absolute values of x and y."),
                tsx("tscourse-w8-if-2", "Labelled user",
                    "Return `<name> (admin)` when admin is true, else just the name.",
                    _prog('type User = { name: string; admin: boolean };\n'
                          'function label(u: User): string {\n'
                          '  return u.admin ? `${u.name} (admin)` : u.name;\n'
                          '}\n'
                          'console.log(label({ name: "Ada", admin: true }));\n'),
                    ['u.admin ? `${u.name} (admin)` : u.name'],
                    [("", "Ada (admin)")],
                    hint="A ternary `cond ? a : b` picks a when cond is true."),
            ],
        ),
        _lesson(
            "w8-typed-arrays", "Typed arrays of records",
            "Putting interfaces to work over lists.",
            """
Annotate an array of records with `Item[]` and process it with the methods you
know:

```ts
interface Item { name: string; price: number; }
const items: Item[] = [{ name: "A", price: 4 }, { name: "B", price: 6 }];
const total = items.reduce((sum, it) => sum + it.price, 0);
console.log(total);   // 10
```

`reduce` folds a list into one value, carrying an accumulator (`sum`, starting at 0).
""",
            [
                tsx("tscourse-w8-ta-1", "Total price",
                    "Reduce the items to the sum of their prices.",
                    _prog('interface Item {\n'
                          '  name: string;\n'
                          '  price: number;\n'
                          '}\n'
                          'const items: Item[] = [\n'
                          '  { name: "A", price: 4 },\n'
                          '  { name: "B", price: 6 },\n'
                          '];\n'
                          'const total = items.reduce((sum, it) => sum + it.price, 0);\n'
                          'console.log(total);\n'),
                    ['sum + it.price'],
                    [("", "10")],
                    hint="Each step adds it.price to the running sum."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Typed contacts report",
        """
Model a contact list with an `interface`, then report on it. Given three
contacts, print:

```
Total: 3
Adults: 2
Names: Ada, Bo, Cy
```

(Adults are aged 18+.) Fill in the block that computes the adults, the two
counts, and the comma-joined names.
""",
        tsc("tscourse-w8-capstone", "Typed contacts report", "Medium",
            "Use filter, map, join and .length over a typed array of records.",
            _prog('interface Contact {\n'
                  '  name: string;\n'
                  '  age: number;\n'
                  '}\n'
                  'const contacts: Contact[] = [\n'
                  '  { name: "Ada", age: 36 },\n'
                  '  { name: "Bo", age: 17 },\n'
                  '  { name: "Cy", age: 40 },\n'
                  '];\n'
                  'const adults = contacts.filter((c) => c.age >= 18);\n'
                  'console.log(`Total: ${contacts.length}`);\n'
                  'console.log(`Adults: ${adults.length}`);\n'
                  'const names = contacts.map((c) => c.name).join(", ");\n'
                  'console.log(`Names: ${names}`);\n'),
            'const adults = contacts.filter((c) => c.age >= 18);\n'
            'console.log(`Total: ${contacts.length}`);\n'
            'console.log(`Adults: ${adults.length}`);\n'
            'const names = contacts.map((c) => c.name).join(", ");\n'
            'console.log(`Names: ${names}`);',
            [("", "Total: 3\nAdults: 2\nNames: Ada, Bo, Cy")],
            hint="filter for age>=18, map to names then join with \", \"."),
    ),
))

# ===========================================================================
# MONTHS 3-8 — themed skeletons (authored in later batches). Each carries a
# real theme + goal so the whole 8-month arc is visible from day one.
# ===========================================================================
_M3 = "The Type System, Properly"
_WEEKS += [
    _skel(9, 3, _M3, "Unions & Narrowing",
          "Model a value that's 'one of several' and narrow it safely before use."),
    _skel(10, 3, _M3, "Generics",
          "Write functions and types that work over any type without losing safety."),
    _skel(11, 3, _M3, "Immutability & readonly",
          "Lock data down with readonly, as const, and pure (copy-don't-mutate) updates."),
    _skel(12, 3, _M3, "Utility Types",
          "Reshape existing types with Partial, Pick, Omit, and Record."),
]

_M4 = "Robust, Real-World Programs"
_WEEKS += [
    _skel(13, 4, _M4, "Optionals & Null-Safety",
          "Handle possibly-missing values with ?., ??, and strict null checks."),
    _skel(14, 4, _M4, "Error Handling",
          "Fail loudly and recover gracefully with try/catch and the Result pattern."),
    _skel(15, 4, _M4, "Modules & Organization",
          "Split a program across files with import/export and clear boundaries."),
    _skel(16, 4, _M4, "Async & Promises",
          "Work with promises and async/await for tasks that take time."),
]

_M5 = "Data Structures in TypeScript"
_WEEKS += [
    _skel(17, 5, _M5, "Stacks & Queues",
          "Build and use LIFO/FIFO structures and know when each fits."),
    _skel(18, 5, _M5, "Maps & Sets",
          "Reach for hash maps and sets to get O(1) lookup and de-duplication."),
    _skel(19, 5, _M5, "Recursion",
          "Solve problems whose definition refers to themselves."),
    _skel(20, 5, _M5, "Linked Lists & Trees",
          "Model data as nodes that point to other nodes."),
]

_M6 = "Algorithmic Thinking"
_WEEKS += [
    _skel(21, 6, _M6, "Big-O & Complexity",
          "Reason about the time and space cost of your code."),
    _skel(22, 6, _M6, "Searching & Two Pointers",
          "Binary search a sorted array and sweep it with two pointers."),
    _skel(23, 6, _M6, "Sliding Window & Prefix Sums",
          "Answer range and subarray questions in linear time."),
    _skel(24, 6, _M6, "Sorting",
          "Understand the common sorts and use sorting as a problem-solving tool."),
]

_M7 = "DSA Interview Core"
_WEEKS += [
    _skel(25, 7, _M7, "Recursion & Backtracking",
          "Generate and search combinatorial spaces (subsets, permutations)."),
    _skel(26, 7, _M7, "Dynamic Programming",
          "Turn overlapping recursion into fast, memoized DP."),
    _skel(27, 7, _M7, "Graphs: BFS & DFS",
          "Traverse graphs and grids to answer reachability and shortest-path questions."),
    _skel(28, 7, _M7, "Heaps & Intervals",
          "Use priority queues and interval techniques on classic problems."),
]

_M8 = "Advanced Types & Interview Polish"
_WEEKS += [
    _skel(29, 8, _M8, "Conditional & Mapped Types",
          "Compute new types from existing ones with conditional and mapped types."),
    _skel(30, 8, _M8, "Inference & Template Literal Types",
          "Bend the inference engine and build types from string patterns."),
    _skel(31, 8, _M8, "Type-Level Challenges",
          "Solve 'type gymnastics' puzzles the way interviewers pose them."),
    _skel(32, 8, _M8, "Mock Interview Week",
          "Put it together under time: DSA solved in TypeScript plus type challenges."),
]


TS_COURSE = {
    "key": "typescript",
    "title": "TypeScript: Zero to Interview",
    "subtitle": (
        "An 8-month, week-by-week course from your very first line of code to "
        "interview-ready — DSA solved in TypeScript and deep type-system mastery. "
        "Every week has a goal, lessons that never outrun what you've learned, and "
        "a capstone project."
    ),
    "weeks": _WEEKS,
}
