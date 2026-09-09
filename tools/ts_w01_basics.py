# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 1 — values, variables & output.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 1 ---------------------------------------------------------------
_WEEKS.append(_week(
    1, 1, _M1,
    "Values, Variables & Output",
    "Write programs that hold values in named variables, compute with them, and print exactly the text you intend.",
    """
Welcome — this is the very beginning, and it assumes **nothing**. By the end of
this week you'll have written a few dozen small programs that print things,
remember things, and do arithmetic. That sounds modest, but it genuinely is
what most code does: take some values, combine them, show a result.

**How to work through a week.** Each lesson has four parts:

1. **Read** the explanation — short, with a worked example.
2. **Predict the output** — guess before you run. Guessing wrong is the single
   fastest way to fix a wrong mental model, so answer honestly.
3. **Practice** — fill in the `____` and press **Check**. Your code really runs.
4. **Fix the bug** — a complete program that looks right but isn't.

Plan on roughly **five hours** for the week. Nobody does that in one sitting —
one lesson per session is a perfectly good pace, and the page remembers what
you've solved.
""",
    objectives=[
        "Print exact text, numbers, and several values at once with console.log",
        "Store values in const and let, and know which to reach for",
        "Compute with + - * / % and control the order with parentheses",
        "Round and truncate numbers with Math.round, Math.floor and toFixed",
        "Join text with + and with template literals",
        "Name the type of a value, annotate a variable, and convert between text and numbers",
    ],
    why="Every program you will ever write holds values and shows results. Everything later — decisions, loops, functions, whole applications — is built on this floor.",
    est_minutes=280,
    glossary=[
        _gloss("statement", "One instruction. Statements run top to bottom, usually one per line, ending in a semicolon."),
        _gloss("expression", "Anything that produces a value: 2 + 3, \"hi\", price * qty."),
        _gloss("string", "Text. Written inside quotes: \"hello\"."),
        _gloss("number", "TypeScript's one numeric type — it covers 7 and 7.5 alike."),
        _gloss("boolean", "A value that is either true or false."),
        _gloss("variable", "A named box holding a value."),
        _gloss("const", "Declares a name whose value is never reassigned. Your default."),
        _gloss("let", "Declares a name you intend to reassign later."),
        _gloss("declaration", "The first mention, with let/const. You declare a name once."),
        _gloss("assignment", "Putting a value into an already-declared name: count = 5."),
        _gloss("operator", "A symbol combining values: + - * / %."),
        _gloss("operand", "A value an operator works on. In a * b, a and b are the operands."),
        _gloss("precedence", "Which operator binds tighter. * and / happen before + and -."),
        _gloss("concatenation", "Joining strings with +."),
        _gloss("escape sequence", "A backslash code inside a string: \\n newline, \\\" a quote, \\\\ a backslash."),
        _gloss("template literal", "A backtick string with ${...} holes: `Hi ${name}`."),
        _gloss("annotation", "The `: number` in `const n: number = 5` — a note to the compiler about the type."),
        _gloss("typeof", "An operator reporting a value's type as a string: typeof 5 is \"number\"."),
        _gloss("comment", "Text the computer ignores: // to end of line, or /* ... */."),
    ],
    cheatsheet="""
```ts
// ---- printing -------------------------------------------------------
console.log("hi");            // prints: hi
console.log("Total:", 42);    // prints: Total: 42   (a space between args)
console.log(6 * 7);           // prints: 42
// this line is a comment — ignored

// ---- variables ------------------------------------------------------
const name = "Ada";           // never reassigned  <- your default
let count = 0;                // will be reassigned
count = count + 1;            // assignment (no second `let`)

// ---- annotations ----------------------------------------------------
const price: number = 3;
const label: string = "Coffee";
const paid: boolean = true;

// ---- arithmetic -----------------------------------------------------
6 * 7                         // 42
17 % 5                        // 2      remainder
10 / 4                        // 2.5    always a decimal
2 + 3 * 4                     // 14     * before +
(2 + 3) * 4                   // 20     parentheses win

Math.floor(7 / 2)             // 3      chop toward zero-ish (down)
Math.round(2.6)               // 3
Math.max(3, 9)                // 9
(0.1 + 0.2).toFixed(2)        // "0.30" fixed decimal places (a string!)

// ---- text -----------------------------------------------------------
"a" + "b"                     // "ab"
"Line 1\\nLine 2"              // \\n is a newline inside one string
`Hi ${name}, you owe $${total}`   // template literal

// ---- types & conversion ---------------------------------------------
typeof 5                      // "number"
typeof "5"                    // "string"
"5" + 3                       // "53"   <- + joined them!
Number("5") + 3               // 8      convert first
String(42) + "!"              // "42!"
```
""",
    self_check=[
        "Can you print an exact line of text, including punctuation and spacing?",
        "Can you explain, in your own words, when to use const and when to use let?",
        "Can you predict what 2 + 3 * 4 gives, and how to make it 20 instead?",
        "Can you say why \"5\" + 3 is \"53\" and how to get 8?",
        "Can you write the same output line twice — once with + and once with a template literal?",
        "Can you compute a total from a price and a quantity and print it with two decimal places?",
    ],
    review=[
        _q("Which declares a value that is never reassigned?",
           ["let x = 1", "const x = 1", "x = 1", "number x = 1"], 1,
           "const fixes the binding. Reach for it first; switch to let only when you actually reassign."),
        _q("What does `17 % 5` evaluate to?", ["3", "2", "3.4", "12"], 1,
           "% is the remainder: 17 = 3*5 + 2, so 2."),
        _q('What does `console.log("5" + 3)` print?', ["8", "53", "\"53\"", "an error"], 1,
           'The left side is a string, so + joins rather than adds: "53".'),
        _q("What does `2 + 3 * 4` evaluate to?", ["20", "14", "24", "9"], 1,
           "* binds tighter than +, so it's 2 + 12 = 14."),
        _q("What does `console.log(\"Total:\", 7)` print?",
           ["Total:7", "Total: 7", "Total: , 7", "Total:"], 1,
           "console.log separates its arguments with a single space."),
        _q("Which is TRUE of `const total = 10 / 4;`?",
           ["total is 2", "total is 2.5", "total is 3", "it is an error"], 1,
           "There is no integer division in TypeScript — / keeps the decimal."),
        _q("What is `typeof true`?", ['"true"', '"boolean"', '"number"', "true"], 1,
           "typeof reports the type name as a string: \"boolean\"."),
        _q("`(2.345).toFixed(1)` produces…", ["2.3", '"2.3"', "2", '"2.35"'], 1,
           "toFixed returns a STRING with that many decimal places."),
        _q("You wrote `let n = 1;` then want n to be 5. Which line is right?",
           ["let n = 5;", "n = 5;", "const n = 5;", "n == 5;"], 1,
           "The name is already declared — reassignment is just `n = 5;`."),
        _q("What does `console.log(`${2 + 3} apples`)` print?",
           ["${2 + 3} apples", "5 apples", "2 + 3 apples", "23 apples"], 1,
           "Any expression inside ${ } is evaluated first."),
    ],
    milestone="You can write a program that prints a formatted, computed receipt. That is real, working code — the same shape as the billing line in a real checkout.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w1-hello", "Your first program",
            "Statements, console.log, and comments.",
            """
A **program** is a list of **statements** run strictly top to bottom. The
statement you'll use most is `console.log(...)`, which prints its argument and
then moves to a new line.

```ts
console.log("Hello, world!");
```

Three things are happening there:

| piece | name | meaning |
|---|---|---|
| `console.log` | the thing being called | "print this" |
| `( ... )` | parentheses | what to print goes inside |
| `"Hello, world!"` | a **string** | text; the quotes mark where it starts and ends |

The quotes are *not* printed — they only tell TypeScript "the text starts
here and ends here".

**Several values at once.** Separate them with commas and `console.log` joins
them with a single space:

```ts
console.log("Total:", 42);   // Total: 42
console.log("a", "b", "c");  // a b c
```

**Arithmetic prints its result, not the sum you typed:**

```ts
console.log(2 + 3);     // 5     — no quotes, so it's a calculation
console.log("2 + 3");   // 2 + 3 — quotes, so it's just text
```

That difference — *value* versus *text that looks like a value* — is the single
most important idea this week.

**Comments** are notes for humans; the computer skips them entirely:

```ts
// everything after two slashes on this line is ignored
console.log("run"); // ...including a note after a statement
```

> ⚠️ **Common mistakes:** forgetting the quotes around text (TypeScript then
> thinks you're naming a variable that doesn't exist); forgetting the
> parentheses — it is `console.log("hi")`, never `console.log "hi"`; and
> expecting `console.log` to print quotes it never prints.
""",
            warmup=[
                _q('What does `console.log("Hi")` print?',
                   ['"Hi"', "Hi", "Hi (with quotes)", "nothing"], 1,
                   "The quotes delimit the string; they are not part of it."),
                _q("What does `console.log(2 + 3)` print?",
                   ["2 + 3", "23", "5", '"5"'], 2,
                   "No quotes, so it is arithmetic: 5."),
                _q('What does `console.log("2 + 3")` print?',
                   ["5", "2 + 3", "23", "error"], 1,
                   "Inside quotes it is plain text, printed as written."),
                _q('What does `console.log("Score:", 10)` print?',
                   ["Score:10", "Score: 10", "Score:, 10", "Score: \"10\""], 1,
                   "Arguments are separated by exactly one space."),
            ],
            exercises=[
                _ex("tscourse-w1-hello-1", "Print a greeting",
                    "Make the program print exactly: Hello, world!",
                    'console.log("Hello, world!");\n',
                    '"Hello, world!"', [("", "Hello, world!")],
                    hints=["A string is text between double quotes.",
                           'Put "Hello, world!" inside the parentheses.']),
                _ex("tscourse-w1-hello-2", "Print two lines",
                    "Print `Line one` then `Line two`, each on its own line.",
                    'console.log("Line one");\nconsole.log("Line two");\n',
                    'console.log("Line two");', [("", "Line one\nLine two")],
                    hints=["Each console.log ends with a newline of its own.",
                           'The second statement is console.log("Line two");']),
                _ex("tscourse-w1-hello-3", "A label and a value",
                    "Print `Total: 42` using ONE console.log with two arguments.",
                    'console.log("Total:", 42);\n',
                    '"Total:", 42', [("", "Total: 42")],
                    hints=["Two arguments separated by a comma get one space between them.",
                           'Write "Total:", 42 inside the parentheses.']),
                _ex("tscourse-w1-hello-4", "Print a calculation",
                    "Print the result of 12 times 12 (not the text `12 * 12`).",
                    'console.log(12 * 12);\n',
                    '12 * 12', [("", "144")],
                    hints=["No quotes — you want the value, not the text.",
                           "Write 12 * 12 with no quotes around it."]),
                _ex("tscourse-w1-hello-5", "A blank line between",
                    "Print `top`, then an empty line, then `bottom`.",
                    'console.log("top");\nconsole.log("");\nconsole.log("bottom");\n',
                    'console.log("");', [("", "top\n\nbottom")],
                    hints=["An empty string is just two quotes with nothing between.",
                           'The middle statement is console.log("");']),
                _fix("tscourse-w1-hello-fix1", "Fix the greeting",
                     "This is supposed to print `Hello!` but prints something else. Fix it.",
                     'console.log("Goodbye!");\n',
                     'console.log("Hello!");\n',
                     [("", "Hello!")],
                     hints=["Only the text inside the quotes is wrong.",
                            'Change "Goodbye!" to "Hello!".']),
                _fix("tscourse-w1-hello-fix2", "Fix the quoted sum",
                     "This should print the number 9, but prints the text `4 + 5` instead. Fix it.",
                     'console.log("4 + 5");\n',
                     'console.log(4 + 5);\n',
                     [("", "9")],
                     hints=["Quotes turn a calculation into plain text.",
                            "Remove the quotes so 4 + 5 is actually computed."]),
            ],
            quiz=[
                _q("Statements in a program run…",
                   ["in a random order", "top to bottom", "bottom to top",
                    "only if you ask"], 1,
                   "Top to bottom, one after another."),
                _q("What is printed by `console.log(\"3\", 3);`?",
                   ["3 3", "33", "6", '"3" 3'], 0,
                   'Both print as 3, separated by a space — the string "3" and the number 3 look identical when printed.'),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w1-variables", "Naming values: const and let",
            "Storing a value so you can use it more than once.",
            """
A **variable** is a name attached to a value. You **declare** it once — with
`const` or `let` — and use the name everywhere after.

```ts
const name = "Ada";
console.log(name);          // Ada
console.log("Hi, " + name); // Hi, Ada
```

**Declaration vs assignment.** The first mention creates the name; later
mentions just put a new value in it. You never repeat `let`:

```ts
let count = 1;     // declaration  (creates `count`)
count = 2;         // assignment   (no `let`!)
count = count + 1; // reads 2, adds 1, stores 3
```

That last line reads strangely if you think `=` means "equals". It doesn't —
`=` means **"put the value on the right into the name on the left."** The right
side is worked out first.

**const vs let.** `const` means *this name will never be reassigned*:

```ts
const rate = 0.08;
rate = 0.09;   // ❌ error: cannot assign to a constant
```

**Reach for `const` by default.** Use `let` only when you genuinely need the
value to change. A `const` is a promise to your future self that this name
means one thing throughout — which makes code far easier to read.

**Naming.** Names use letters, digits, `_` and `$`, and can't start with a
digit. The convention is `camelCase`: `lineTotal`, `taxRate`, `userName`.
Choose names that say what the value *means*: `qty` beats `q`, `n2` means
nothing to anyone.

> ⚠️ **Common mistakes:** writing `let` a second time when reassigning (that's
> a redeclaration error); trying to reassign a `const`; and using a name before
> the line that declares it.
""",
            warmup=[
                _q("After `let n = 1; n = n + 4;`, what is `n`?",
                   ["1", "5", "14", "4"], 1, "n + 4 is 5, and that is stored back into n."),
                _q("After `let a = 2; let b = a; a = 9;`, what is `b`?",
                   ["9", "2", "11", "error"], 1,
                   "b copied the VALUE 2 at that moment; changing a afterwards doesn't touch b."),
                _q("Which line is an error?",
                   ["let x = 1;", "const y = 2;", "let x = 1; let x = 3;", "let z = 1; z = 3;"], 2,
                   "You may only declare a given name once in the same scope."),
            ],
            exercises=[
                _ex("tscourse-w1-var-1", "Name a value",
                    "Store `Ada` in `name` so the program prints `Hello, Ada`.",
                    'const name = "Ada";\nconsole.log("Hello, " + name);\n',
                    '"Ada"', [("", "Hello, Ada")],
                    hints=["The value is a string, so it needs quotes.",
                           'Set name to "Ada".']),
                _ex("tscourse-w1-var-2", "Reassign with let",
                    "Reassign `count` to 2 so the program prints 2.",
                    'let count = 1;\ncount = 2;\nconsole.log(count);\n',
                    'count = 2;', [("", "2")],
                    hints=["Reassignment does not repeat `let`.",
                           "The line is exactly `count = 2;`."]),
                _ex("tscourse-w1-var-3", "Use a name twice",
                    "Print the item name on both lines, using the variable each time.",
                    'const item = "Coffee";\nconsole.log("Item: " + item);\nconsole.log("Thanks for buying " + item);\n',
                    '"Thanks for buying " + item',
                    [("", "Item: Coffee\nThanks for buying Coffee")],
                    hints=["Join the fixed text and the variable with +.",
                           'Write "Thanks for buying " + item — mind the trailing space inside the quotes.']),
                _ex("tscourse-w1-var-4", "Grow a running count",
                    "Add 3 to `score`, then add 4, so the program prints 7.",
                    'let score = 0;\nscore = score + 3;\nscore = score + 4;\nconsole.log(score);\n',
                    'score = score + 4;', [("", "7")],
                    hints=["Read the current value, add to it, store it back.",
                           "The second line is `score = score + 4;`."]),
                _ex("tscourse-w1-var-5", "Swap in a helper name",
                    "Introduce `total` so the printed line stays `Total: 30`.",
                    'const price = 10;\nconst qty = 3;\nconst total = price * qty;\nconsole.log("Total: " + total);\n',
                    'const total = price * qty;', [("", "Total: 30")],
                    hints=["Naming the intermediate result makes the last line readable.",
                           "Declare `const total = price * qty;`."]),
                _fix("tscourse-w1-var-fix1", "Fix the redeclaration",
                     "This should print 10 but crashes. Fix it so it prints 10.",
                     'let total = 4;\nlet total = 10;\nconsole.log(total);\n',
                     'let total = 4;\ntotal = 10;\nconsole.log(total);\n',
                     [("", "10")],
                     hints=["A name may only be declared once.",
                            "The second line should reassign, not redeclare — drop the `let`."]),
                _fix("tscourse-w1-var-fix2", "Fix the const",
                     "This should print 20, but assigning to a const is an error. Change the declaration so the program works.",
                     'const budget = 10;\nbudget = 20;\nconsole.log(budget);\n',
                     'let budget = 10;\nbudget = 20;\nconsole.log(budget);\n',
                     [("", "20")],
                     hints=["The value here really does need to change.",
                            "Declare it with `let` instead of `const`."]),
            ],
            quiz=[
                _q("What does `=` mean in `total = price * qty;`?",
                   ["is equal to", "put the right-hand value into the left-hand name",
                    "compare the two sides", "declare a constant"], 1,
                   "`=` is assignment. Comparison comes later, and uses `===`."),
                _q("Which should you reach for by default?",
                   ["let", "const", "whichever", "neither — skip the declaration"], 1,
                   "const first; switch to let only when you actually reassign."),
                _q("Which is the best name for a coffee's price?",
                   ["p", "x2", "coffeePrice", "COFFEE_price_value_number"], 2,
                   "Say what it means, in camelCase, without padding."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w1-numbers", "Numbers & arithmetic",
            "One number type, five operators, and the order they happen in.",
            """
TypeScript has **one** numeric type, `number`, covering `7` and `7.5` alike.
There is no separate integer type — and, importantly, **no integer division**:

```ts
10 / 4      // 2.5   (not 2)
```

The five operators:

| operator | name | example | result |
|---|---|---|---|
| `+` | add | `4 + 5` | `9` |
| `-` | subtract | `9 - 4` | `5` |
| `*` | multiply | `6 * 7` | `42` |
| `/` | divide | `10 / 4` | `2.5` |
| `%` | remainder | `17 % 5` | `2` |

**Remainder (`%`)** is what's left after dividing as many whole times as
possible: 17 ÷ 5 is 3 with 2 left over, so `17 % 5` is `2`. It's how you test
"is this even?" (`n % 2` is 0) or "what's the last digit?" (`n % 10`).

**Precedence.** `*`, `/` and `%` happen before `+` and `-`, exactly as in school
maths. Parentheses override that:

```ts
2 + 3 * 4      // 14   (3*4 first)
(2 + 3) * 4    // 20   (parentheses first)
```

When in doubt, add parentheses. They cost nothing and they document intent.

**Rounding.** `Math` holds a toolbox of number helpers:

```ts
Math.floor(2.9)   // 2    always down
Math.ceil(2.1)    // 3    always up
Math.round(2.5)   // 3    to nearest, .5 goes up
Math.abs(-4)      // 4    distance from zero
Math.max(3, 9)    // 9
Math.min(3, 9)    // 3
```

`Math.floor(a / b)` is how you get "whole divisions only": `Math.floor(17 / 5)`
is `3`.

**Decimals lie a little.** Computers store decimals in binary, and some
fractions don't fit exactly:

```ts
console.log(0.1 + 0.2);   // 0.30000000000000004
```

That is not a bug in your code — it's how binary fractions work everywhere.
When you're *displaying* money, fix the decimal places:

```ts
console.log((0.1 + 0.2).toFixed(2));   // 0.30
```

Note `toFixed` hands back a **string**, ready for printing.

> ⚠️ **Common mistakes:** expecting `10 / 3` to be a whole number; mixing up `/`
> with `%`; and forgetting parentheses in a formula like `(a + b) / 2`, which
> without them means `a + (b / 2)`.
""",
            warmup=[
                _q("What does `console.log(10 / 4)` print?",
                   ["2", "2.5", "3", "2.4"], 1, "Division keeps the decimal part."),
                _q("What does `console.log(9 % 2)` print?",
                   ["4.5", "0", "1", "4"], 2, "9 = 4*2 + 1, so the remainder is 1."),
                _q("What does `console.log(2 + 3 * 4)` print?",
                   ["20", "14", "24", "9"], 1, "* binds tighter: 2 + 12."),
                _q("What does `console.log(Math.floor(7 / 2))` print?",
                   ["3.5", "4", "3", "3.0"], 2, "7/2 is 3.5; floor rounds down to 3."),
            ],
            exercises=[
                _ex("tscourse-w1-num-1", "Multiply",
                    "Print the product of `a` and `b` (it should be 42).",
                    'const a = 6;\nconst b = 7;\nconsole.log(a * b);\n',
                    'a * b', [("", "42")],
                    hints=["Use the * operator.", "Write `a * b`."]),
                _ex("tscourse-w1-num-2", "Remainder",
                    "Print the remainder when `total` is divided by 5.",
                    'const total = 17;\nconsole.log(total % 5);\n',
                    'total % 5', [("", "2")],
                    hints=["`%` gives what is left over.", "Write `total % 5`."]),
                _ex("tscourse-w1-num-3", "Average of two",
                    "Print the average of `a` and `b`. Mind the parentheses!",
                    'const a = 4;\nconst b = 9;\nconsole.log((a + b) / 2);\n',
                    '(a + b) / 2', [("", "6.5")],
                    hints=["Add first, then halve.",
                           "Without parentheses you would get a + (b / 2). Write (a + b) / 2."]),
                _ex("tscourse-w1-num-4", "Whole divisions only",
                    "How many whole 5s fit in 17? Print 3, using Math.floor.",
                    'const total = 17;\nconsole.log(Math.floor(total / 5));\n',
                    'Math.floor(total / 5)', [("", "3")],
                    hints=["17 / 5 is 3.4; you want it rounded down.",
                           "Wrap the division: Math.floor(total / 5)."]),
                _ex("tscourse-w1-num-5", "Money to two decimals",
                    "Print the total to exactly two decimal places: 21.75",
                    'const price = 7.25;\nconst qty = 3;\nconsole.log((price * qty).toFixed(2));\n',
                    '(price * qty).toFixed(2)', [("", "21.75")],
                    hints=["Compute first, then fix the decimals.",
                           "Write (price * qty).toFixed(2)."]),
                _ex("tscourse-w1-num-6", "Last digit",
                    "Print the last digit of `code` (should be 7).",
                    'const code = 40127;\nconsole.log(code % 10);\n',
                    'code % 10', [("", "7")],
                    hints=["The remainder after dividing by 10 is the last digit.",
                           "Write code % 10."]),
                _fix("tscourse-w1-num-fix1", "Fix the total",
                     "This should print the SUM of a and b (8) but prints something else.",
                     'const a = 5;\nconst b = 3;\nconsole.log(a - b);\n',
                     'const a = 5;\nconst b = 3;\nconsole.log(a + b);\n',
                     [("", "8")],
                     hints=["Look closely at the operator between a and b.",
                            "A sum uses + , not - ."]),
                _fix("tscourse-w1-num-fix2", "Fix the precedence bug",
                     "This should print the average of 4 and 10 (7) but prints 9. Fix it.",
                     'const a = 4;\nconst b = 10;\nconsole.log(a + b / 2);\n',
                     'const a = 4;\nconst b = 10;\nconsole.log((a + b) / 2);\n',
                     [("", "7")],
                     hints=["/ happens before +, so right now it computes 4 + 5.",
                            "Parenthesise the addition: (a + b) / 2."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("How do you test whether `n` is even?",
                   ["n / 2 === 0", "n % 2 === 0", "Math.floor(n) === n", "n * 2 === n"], 1,
                   "An even number leaves remainder 0 when divided by 2."),
                _q("`(2.5).toFixed(0)` gives you…",
                   ["the number 3", 'the string "3"', "the number 2", "an error"], 1,
                   "toFixed always returns a string — handy for printing, not for further maths."),
                _q("Why does `0.1 + 0.2` print 0.30000000000000004?",
                   ["A TypeScript bug", "Binary can't represent some decimal fractions exactly",
                    "console.log is broken", "0.1 isn't a number"], 1,
                   "It's how binary floating point works — true in nearly every language."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w1-strings", "Strings: quotes, joining & escapes",
            "Building exact text out of pieces.",
            """
A **string** is text. Double quotes and single quotes both work — pick one and
stay consistent (this course uses double):

```ts
const a = "hello";
const b = 'hello';   // identical
```

**Joining (concatenation)** uses `+`:

```ts
const name = "Ada";
console.log("Hello, " + name + "!");   // Hello, Ada!
```

Spacing is *literal*. `"Hello," + name` produces `Hello,Ada` — the space has to
be inside the quotes: `"Hello, "`. Nearly every wrong-output moment this week
will be a missing or extra space.

**Mixing text and numbers.** When either side of `+` is a string, `+` joins
instead of adding:

```ts
console.log("Total: " + 42);   // Total: 42
```

That's convenient here, and a trap later (lesson 6).

**Escape sequences** put otherwise-impossible characters inside a string. A
backslash starts one:

| escape | meaning |
|---|---|
| `\\n` | newline |
| `\\t` | tab |
| `\\"` | a literal double quote |
| `\\\\` | a literal backslash |

```ts
console.log("Line 1\\nLine 2");     // prints TWO lines from ONE call
console.log("She said \\"hi\\"");     // She said "hi"
```

**Handy for output:** `"-".repeat(20)` builds a 20-character rule, which is how
you draw a separator line without typing twenty dashes.

> ⚠️ **Common mistakes:** forgetting the space inside the quotes; putting a
> `"` inside a `"`-quoted string without escaping it; and writing `\\n` outside
> a string, where it means nothing.
""",
            warmup=[
                _q('What does `console.log("a" + "b")` print?',
                   ["a b", "ab", "a+b", '"ab"'], 1, "Concatenation glues them with nothing between."),
                _q('What does `console.log("Hi," + "Bo")` print?',
                   ["Hi, Bo", "Hi,Bo", "HiBo", "Hi, + Bo"], 1,
                   "There is no space in either string, so none appears."),
                _q('How many lines does `console.log("a\\nb")` print?',
                   ["1", "2", "3", "0"], 1, "\\n is a newline inside the one string."),
            ],
            exercises=[
                _ex("tscourse-w1-str-1", "Join with a space",
                    "Print `Hello, Ada!` — mind the space after the comma.",
                    'const name = "Ada";\nconsole.log("Hello, " + name + "!");\n',
                    '"Hello, " + name + "!"', [("", "Hello, Ada!")],
                    hints=["The space has to live inside the quotes.",
                           'Write "Hello, " + name + "!".']),
                _ex("tscourse-w1-str-2", "Two lines from one call",
                    "Using ONE console.log, print `top` then `bottom` on separate lines.",
                    'console.log("top\\nbottom");\n',
                    '"top\\nbottom"', [("", "top\nbottom")],
                    hints=["\\n inside a string is a newline.",
                           'Write "top\\nbottom".']),
                _ex("tscourse-w1-str-3", "Quote inside a quote",
                    'Print exactly: She said "hi"',
                    'console.log("She said \\"hi\\"");\n',
                    '"She said \\"hi\\""', [("", 'She said "hi"')],
                    hints=['A " inside a "-string must be escaped as \\".',
                           'Write "She said \\"hi\\"".']),
                _ex("tscourse-w1-str-4", "Draw a rule",
                    "Print a line of exactly 10 dashes, using repeat.",
                    'console.log("-".repeat(10));\n',
                    '"-".repeat(10)', [("", "----------")],
                    hints=["repeat makes n copies of a string.",
                           'Write "-".repeat(10).']),
                _ex("tscourse-w1-str-5", "Label a number",
                    "Print `Items: 3` by joining text and a number with +.",
                    'const count = 3;\nconsole.log("Items: " + count);\n',
                    '"Items: " + count', [("", "Items: 3")],
                    hints=["When one side of + is text, the other is converted for you.",
                           'Write "Items: " + count.']),
                _fix("tscourse-w1-str-fix1", "Fix the missing space",
                     "This prints `Hello,Ada` but should print `Hello, Ada`. Fix it.",
                     'const name = "Ada";\nconsole.log("Hello," + name);\n',
                     'const name = "Ada";\nconsole.log("Hello, " + name);\n',
                     [("", "Hello, Ada")],
                     hints=["Nothing adds a space for you.",
                            'Put the space inside the quotes: "Hello, ".']),
                _fix("tscourse-w1-str-fix2", "Fix the escape",
                     "This was meant to print a real newline between the words, but prints the backslash-n. Fix it.",
                     'console.log("top" + "\\\\n" + "bottom");\n',
                     'console.log("top" + "\\n" + "bottom");\n',
                     [("", "top\nbottom")],
                     hints=["\\\\ is an escaped backslash — it prints a literal \\.",
                            'A newline is a single backslash then n: "\\n".']),
            ],
            quiz=[
                _q('What is the length of the printed output of `console.log("a\\tb")`?',
                   ["it prints a, a tab, then b", "it prints a\\tb literally",
                    "it prints ab", "it errors"], 0,
                   "\\t is a tab character."),
                _q('`"ab".repeat(3)` is…', ['"ababab"', '"ab3"', '"aaabbb"', "an error"], 0,
                   "repeat concatenates that many copies."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w1-templates", "Template literals",
            "The readable way to build a line of text.",
            """
Building a line with `+` gets noisy fast:

```ts
console.log("Item: " + item + " x" + qty + " = $" + total);
```

A **template literal** uses **backticks** (`` ` ``, the key left of `1` on most
keyboards) and drops values straight into the text with `${ }`:

```ts
console.log(`Item: ${item} x${qty} = $${total}`);
```

Same output, and you can *see* the shape of the line. Notice `$${total}`: the
first `$` is a literal dollar sign you want printed, the `${total}` is the hole.

**Anything that produces a value can go in a hole:**

```ts
const a = 3, b = 4;
console.log(`${a} + ${b} = ${a + b}`);        // 3 + 4 = 7
console.log(`Half: ${(a + b) / 2}`);           // Half: 3.5
console.log(`Price: $${(9.5).toFixed(2)}`);    // Price: $9.50
```

**Templates can span multiple lines** — the line breaks are part of the string:

```ts
console.log(`Name: Ada
Role: Engineer`);
```

prints two lines.

> ⚠️ **Common mistakes:** using `"` or `'` instead of a backtick — then
> `${name}` prints literally, character for character; and forgetting the `$`
> before the `{ }`.
""",
            warmup=[
                _q("With `const n = 3;`, what does `` `n = ${n}` `` produce?",
                   ["n = ${n}", "n = 3", "n = n", "3"], 1, "${n} is replaced by the value."),
                _q("With `const n = 3;`, what does `'n = ${n}'` (single quotes) produce?",
                   ["n = 3", "n = ${n}", "an error", "n = n"], 1,
                   "Only backticks interpolate. In ordinary quotes it is literal text."),
                _q("What does `` `${2 * 5} apples` `` produce?",
                   ["${2 * 5} apples", "10 apples", "2 * 5 apples", "25 apples"], 1,
                   "The expression inside the hole is evaluated first."),
            ],
            exercises=[
                _ex("tscourse-w1-tmpl-1", "Welcome message",
                    "Use a template literal to print `Hi Ada, welcome!`.",
                    'const name = "Ada";\nconsole.log(`Hi ${name}, welcome!`);\n',
                    '`Hi ${name}, welcome!`', [("", "Hi Ada, welcome!")],
                    hints=["Backticks, not quotes.",
                           "Put ${name} where the name belongs."]),
                _ex("tscourse-w1-tmpl-2", "Inline arithmetic",
                    "Print `3 + 4 = 7` using a single template literal.",
                    'const a = 3;\nconst b = 4;\nconsole.log(`${a} + ${b} = ${a + b}`);\n',
                    '`${a} + ${b} = ${a + b}`', [("", "3 + 4 = 7")],
                    hints=["A hole can contain an expression like a + b.",
                           "The template is `${a} + ${b} = ${a + b}`."]),
                _ex("tscourse-w1-tmpl-3", "A dollar sign and a hole",
                    "Print `Total: $36` — a literal $ followed by the computed total.",
                    'const price = 12;\nconst qty = 3;\nconsole.log(`Total: $${price * qty}`);\n',
                    '`Total: $${price * qty}`', [("", "Total: $36")],
                    hints=["You need two dollar signs: one printed, one starting the hole.",
                           "Write `Total: $${price * qty}`."]),
                _ex("tscourse-w1-tmpl-4", "Money, fixed",
                    "Print `Price: $9.50` from the number 9.5.",
                    'const price = 9.5;\nconsole.log(`Price: $${price.toFixed(2)}`);\n',
                    'price.toFixed(2)', [("", "Price: $9.50")],
                    hints=["toFixed(2) gives exactly two decimal places.",
                           "Put price.toFixed(2) inside the hole."]),
                _ex("tscourse-w1-tmpl-5", "Two lines, one template",
                    "Using ONE console.log and a multi-line template, print `Name: Ada` then `Role: Engineer`.",
                    'const name = "Ada";\nconsole.log(`Name: ${name}\nRole: Engineer`);\n',
                    'Role: Engineer', [("", "Name: Ada\nRole: Engineer")],
                    hints=["A real line break inside backticks becomes a newline.",
                           "The second line of the template is `Role: Engineer`."]),
                _fix("tscourse-w1-tmpl-fix1", "Fix the quotes",
                     "This was meant to greet by name but prints the hole literally. Fix it.",
                     'const name = "Ada";\nconsole.log(\'Hi ${name}!\');\n',
                     'const name = "Ada";\nconsole.log(`Hi ${name}!`);\n',
                     [("", "Hi Ada!")],
                     hints=["${...} only means anything inside backticks.",
                            "Swap the single quotes for backticks."]),
                _fix("tscourse-w1-tmpl-fix2", "Fix the missing dollar",
                     "This prints `{name} is here` instead of `Ada is here`. Fix it.",
                     'const name = "Ada";\nconsole.log(`{name} is here`);\n',
                     'const name = "Ada";\nconsole.log(`${name} is here`);\n',
                     [("", "Ada is here")],
                     hints=["A hole is $ followed by braces.",
                            "Add the missing $ before {name}."]),
            ],
            quiz=[
                _q("Which character opens a template literal?",
                   ['"', "'", "`", "$"], 2, "The backtick, usually left of the 1 key."),
                _q("`` `a${1 + 1}c` `` produces…", ["a1 + 1c", "a2c", "a${2}c", "ac"], 1,
                   "The hole evaluates to 2."),
                _q("Which is easier to get wrong by one space?",
                   ['"Hi, " + name + "!"', "`Hi, ${name}!`", "they are equally risky",
                    "neither can go wrong"], 0,
                   "With + the spaces are scattered across several quoted pieces; a template shows the whole line at once."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w1-types", "Types, annotations & conversion",
            "What the 'Type' in TypeScript buys you.",
            """
Every value has a **type**. This week you've met three:

| type | example values |
|---|---|
| `number` | `42`, `-1`, `3.5` |
| `string` | `"hi"`, `""`, `"42"` |
| `boolean` | `true`, `false` |

`typeof` reports the type as a string:

```ts
console.log(typeof 42);      // number
console.log(typeof "42");    // string
console.log(typeof true);    // boolean
```

Notice `42` and `"42"` are *different values*. They print identically, which is
exactly why the difference bites.

**The classic trap.** `+` means "add" for two numbers and "join" for anything
involving a string:

```ts
console.log(3 + 4);       // 7    two numbers  -> addition
console.log("3" + 4);     // 34   a string     -> concatenation
console.log("3" - 1);     // 2    - has no string meaning, so it converts
```

That inconsistency is inherited from JavaScript. The cure is to **convert on
purpose**:

```ts
Number("3") + 4     // 7
String(3) + "4"     // "34"
```

**Annotations** are how you tell TypeScript what you mean, so it can catch the
mistake before the program ever runs:

```ts
const price: number = 3;
const label: string = "Coffee";
const paid: boolean = true;
```

Read `: number` as "…and this is a number". You don't need it everywhere —
TypeScript can usually work it out from the value — but writing one costs a
second and turns a silent wrong answer into a red squiggle.

The annotations are **erased before the program runs**. They are a checking
tool, not part of the running code; at runtime it is all just values.

> ⚠️ **Common mistakes:** assuming `"5" + 3` adds; annotating something as
> `number` and then assigning text to it; and reaching for `Number(...)` after
> the concatenation has already happened, e.g. `Number("5" + 3)` is 53, not 8.
""",
            warmup=[
                _q('What does `console.log(typeof "42")` print?',
                   ["42", "number", "string", "text"], 2, 'The quotes make it a string.'),
                _q('What does `console.log("5" + 3)` print?', ["8", "53", "15", "error"], 1,
                   "A string on the left makes + concatenate."),
                _q('What does `console.log("5" - 3)` print?', ["53", "2", "8", "error"], 1,
                   'The - operator has no string meaning, so "5" is converted to 5 first.'),
                _q('What does `console.log(Number("5") + 3)` print?',
                   ["53", "8", '"8"', "error"], 1, "Convert first, then add."),
            ],
            exercises=[
                _predict("tscourse-w1-typ-p1", "The type of a product",
                         'const price = 3;\nconst qty = 4;\nconst total = price * qty;\n',
                         "total", "number",
                         why="Arithmetic always lands on a number, however the operands were written.",
                         hints=["`*` is arithmetic — there is only one type it can produce.",
                                "Write number."],
                         difficulty="Intro"),
                _predict("tscourse-w1-typ-p2", "The type of a join",
                         'const qty = 4;\nconst label = "Qty: " + qty;\n',
                         "label", "string",
                         why="A number went in, so it is worth being sure what came out.",
                         hints=["When either side of + is text, + joins rather than adds.",
                                "Joining produces text: write string."],
                         difficulty="Intro"),
                _diagnose("tscourse-w1-typ-diag1", "The annotation that disagrees",
                          "TS2322: Type 'string' is not assignable to type 'number'.",
                          'const price: number = "3";\nconsole.log(price + 1);\n',
                          'const price: number = 3;\nconsole.log(price + 1);\n',
                          [("", "4")],
                          ask="The annotation says one thing and the value says another. "
                              "Keep the annotation and make the value honest, so it prints 4.",
                          hints=['"3" with quotes is text; 3 without them is a number.',
                                 "The quotes are the whole bug — drop them.",
                                 "Write const price: number = 3;"],
                          difficulty="Easy"),
                _ex("tscourse-w1-typ-1", "Report a type",
                    "Print the type of the value in `v` (it should print `string`).",
                    'const v = "42";\nconsole.log(typeof v);\n',
                    'typeof v', [("", "string")],
                    hints=["typeof reports the type name.", "Write typeof v."]),
                _ex("tscourse-w1-typ-2", "Add, don't join",
                    "`raw` holds text. Print 8 — the sum, not `53`.",
                    'const raw = "5";\nconsole.log(Number(raw) + 3);\n',
                    'Number(raw) + 3', [("", "8")],
                    hints=["Convert the text to a number before adding.",
                           "Write Number(raw) + 3."]),
                _ex("tscourse-w1-typ-3", "Join, don't add",
                    "`n` holds the number 42. Print `42!`.",
                    'const n = 42;\nconsole.log(String(n) + "!");\n',
                    'String(n) + "!"', [("", "42!")],
                    hints=["String(...) turns a number into text.",
                           'Write String(n) + "!".']),
                _ex("tscourse-w1-typ-4", "Annotate it",
                    "Fill in the annotation so `rate` is declared as a number.",
                    'const rate: number = 0.08;\nconsole.log(rate);\n',
                    'number', [("", "0.08")],
                    hints=["The annotation names the kind of value: number, string or boolean.",
                           "0.08 is a number, so write `const rate: number = 0.08;`."]),
                _ex("tscourse-w1-typ-5", "A boolean value",
                    "Store `true` in `paid` and print it.",
                    'const paid: boolean = true;\nconsole.log(paid);\n',
                    'true', [("", "true")],
                    hints=["true is a value, written without quotes.",
                           "Assign the bare word true."]),
                _fix("tscourse-w1-typ-fix1", "Fix the accidental join",
                     "This should print the total 15 but prints 105. Fix it.",
                     'const a = "10";\nconst b = 5;\nconsole.log(a + b);\n',
                     'const a = "10";\nconst b = 5;\nconsole.log(Number(a) + b);\n',
                     [("", "15")],
                     hints=['a is the string "10", so + joins: "10" + 5 is "105".',
                            "Convert a first: Number(a) + b."],
                     difficulty="Medium"),
                _fix("tscourse-w1-typ-fix2", "Fix the late conversion",
                     "Someone tried to convert, but in the wrong place: this prints 53 instead of 8. Fix it.",
                     'const raw = "5";\nconsole.log(Number(raw + 3));\n',
                     'const raw = "5";\nconsole.log(Number(raw) + 3);\n',
                     [("", "8")],
                     hints=['The join happens inside the parentheses first, giving "53".',
                            "Convert raw alone, then add: Number(raw) + 3."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What are annotations like `: number` for?",
                   ["Speed", "Catching mistakes before the program runs",
                    "They change the value", "They are required"], 1,
                   "They're checked while you write, then erased before running."),
                _q('`Number("abc")` gives…', ["0", "NaN", '"abc"', "an error that stops the program"], 1,
                   "NaN — 'not a number'. You'll learn to check for it in week 2."),
                _q("Which pair holds DIFFERENT values?",
                   ["42 and 42", '"42" and 42', "true and true", '"a" and "a"'], 1,
                   "One is text, one is a number — they only look alike when printed."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #1 — the receipt line",
        """
Meet **Budget Buddy**, the little expense tool you'll grow all the way through
this course. Each week it gains exactly the powers you just learned.

**This week.** Using only variables, arithmetic and text-building, print a
four-line receipt for **4 coffees at $3.25 each** against a **$20** budget:

```
Coffee x4
Each:      $3.25
Subtotal:  $13.00
Remaining: $7.00
```

Every number must be **computed**, not typed in — change `qty` to 5 and the
receipt should still be right. Money is shown to two decimal places.
""",
        _ch("tscourse-w1-capstone", "Budget Buddy #1", "Easy",
            "Compute the subtotal and the remaining budget, then print the four lines exactly.",
            'const item = "Coffee";\n'
            'const price = 3.25;\n'
            'const qty = 4;\n'
            'const budget = 20;\n'
            'const subtotal = price * qty;\n'
            'const remaining = budget - subtotal;\n'
            'console.log(`${item} x${qty}`);\n'
            'console.log(`Each:      $${price.toFixed(2)}`);\n'
            'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
            'console.log(`Remaining: $${remaining.toFixed(2)}`);\n',
            'const subtotal = price * qty;\n'
            'const remaining = budget - subtotal;\n'
            'console.log(`${item} x${qty}`);\n'
            'console.log(`Each:      $${price.toFixed(2)}`);\n'
            'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
            'console.log(`Remaining: $${remaining.toFixed(2)}`);',
            [("", "Coffee x4\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00")],
            hints=["Start by naming the two computed values: subtotal and remaining.",
                   "subtotal is price * qty; remaining is budget - subtotal.",
                   "Each money line is a template literal ending in .toFixed(2), e.g. `Subtotal:  $${subtotal.toFixed(2)}`.",
                   "Match the label padding exactly: `Each:` has six spaces after it, `Subtotal:` two, `Remaining:` one."]),
        example_io="Coffee x4\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00",
        rubric=["Line 1 shows the item and quantity",
                "The unit price, subtotal and remaining budget each appear on their own line",
                "Every money figure has exactly two decimal places",
                "Nothing is hard-coded — the numbers come from price, qty and budget"],
        stretch=_ch("tscourse-w1-capstone-stretch", "Budget Buddy #1 (stretch)", "Medium",
                    "Add a dashed rule under the header and a final line showing how many MORE coffees the remaining budget affords (whole coffees only).",
                    'const item = "Coffee";\n'
                    'const price = 3.25;\n'
                    'const qty = 4;\n'
                    'const budget = 20;\n'
                    'const subtotal = price * qty;\n'
                    'const remaining = budget - subtotal;\n'
                    'console.log(`${item} x${qty}`);\n'
                    'console.log("-".repeat(20));\n'
                    'console.log(`Each:      $${price.toFixed(2)}`);\n'
                    'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
                    'console.log(`Remaining: $${remaining.toFixed(2)}`);\n'
                    'console.log(`Affords:   ${Math.floor(remaining / price)} more`);\n',
                    'const subtotal = price * qty;\n'
                    'const remaining = budget - subtotal;\n'
                    'console.log(`${item} x${qty}`);\n'
                    'console.log("-".repeat(20));\n'
                    'console.log(`Each:      $${price.toFixed(2)}`);\n'
                    'console.log(`Subtotal:  $${subtotal.toFixed(2)}`);\n'
                    'console.log(`Remaining: $${remaining.toFixed(2)}`);\n'
                    'console.log(`Affords:   ${Math.floor(remaining / price)} more`);',
                    [("", "Coffee x4\n--------------------\nEach:      $3.25\nSubtotal:  $13.00\nRemaining: $7.00\nAffords:   2 more")],
                    hints=['A 20-dash rule is "-".repeat(20).',
                           "Whole coffees only means Math.floor(remaining / price).",
                           "$7.00 buys 2 more coffees at $3.25 (2.15 rounded down)."]),
    ),
))
