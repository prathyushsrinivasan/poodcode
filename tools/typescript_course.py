# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# The 8-month structured TypeScript course (POLISHED build).
#
# exec()'d inside gen_seed.py's namespace AFTER the other TypeScript files, so it
# can reuse `_P` (program normalizer). Defines a single global `TS_COURSE` (dict)
# which gen_seed writes to src-tauri/seeds/ts_course.json (served by `ts_course`).
#
# HARD DESIGN RULE (the user's core ask): a week may only require syntax/concepts
# introduced in that week or earlier. A gen-time `_lint_scope` check at the end
# enforces this by scanning every program for constructs that appear before the
# week that teaches them (loops<W4, functions<W5, array methods<W6, reduce<W8,
# object literals<W7). If you add content that violates the ladder, generation
# FAILS loudly.
#
# EXECUTION MODEL: exercises run through the same stdin/stdout judge as every
# Learn drill (Node type-stripping). Every blank targets RUNTIME code; programs
# read stdin with `fs.readFileSync(0,"utf8")`; output is matched exactly (after
# whitespace normalization). Each `solution` is verified end-to-end by
# tests/verify_ts_course.rs and a Node verifier.
#
# EXERCISE KINDS: "drill" (fill one ____ blank), "challenge"/"capstone" (write a
# whole solution where you see ____), "fix" (a complete but buggy program the
# learner corrects — no blank; starter=buggy, solution=fixed).
# ---------------------------------------------------------------------------


def _prog(src):
    return _P(src)


def _q(question, options, answer, explanation):
    return {"question": question, "options": options, "answer": answer,
            "explanation": explanation}


def _gloss(term, definition):
    return {"term": term, "def": definition}


def _tests(pairs):
    return [{"input": i, "output": o} for (i, o) in pairs]


def _mk(eid, title, prompt, full, tests, hints, difficulty, kind, starter=None,
        blank=None):
    """Build a course Exercise dict. Either `blank` (a unique substring of `full`
    replaced by ____ to form the starter) OR an explicit `starter` (for "fix")."""
    full = _prog(full)
    if starter is None:
        assert blank is not None, f"{eid}: need blank or starter"
        assert blank in full, f"{eid}: blank not found in solution: {blank!r}"
        starter = full.replace(blank, "____", 1)
        assert starter != full, f"{eid}: no blank applied"
    else:
        starter = _prog(starter)
        assert starter != full, f"{eid}: starter equals solution"
    assert tests, f"{eid}: needs at least one test"
    hints = list(hints or [])
    return {
        "id": eid, "title": title, "prompt": prompt,
        "hint": hints[0] if hints else "",
        "hints": hints, "language": "typescript",
        "kind": kind, "difficulty": difficulty,
        "starter": starter, "solution": full, "tests": _tests(tests),
        "source_slug": "", "dataset": "",
    }


def _ex(eid, title, prompt, full, blank, tests, hints=(), difficulty="Intro"):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "drill", blank=blank)


def _ch(eid, title, difficulty, prompt, full, blank, tests, hints=()):
    return _mk(eid, title, prompt, full, tests, hints, difficulty, "challenge", blank=blank)


def _fix(eid, title, prompt, buggy, fixed, tests, hints=(), difficulty="Easy"):
    return _mk(eid, title, prompt, fixed, tests, hints, difficulty, "fix", starter=buggy)


def _lesson(key, title, what, lesson_md, exercises, warmup=None, quiz=None):
    return {"key": key, "title": title, "what": what,
            "lesson": _prog(lesson_md) if lesson_md else "",
            "warmup": warmup or [], "exercises": exercises, "quiz": quiz or []}


def _cap_auto(title, brief, exercise, example_io="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "auto",
            "exercise": exercise, "example_io": example_io,
            "rubric": rubric or [], "reference": "", "stretch": stretch}


def _cap_brief(title, brief, reference="", rubric=None, stretch=None):
    return {"title": title, "brief": _prog(brief), "kind": "brief",
            "exercise": None, "example_io": "",
            "rubric": rubric or [], "reference": _prog(reference) if reference else "",
            "stretch": stretch}


def _week(number, month, month_title, theme, goal, summary, lessons, capstone=None,
          objectives=None, why="", est_minutes=40, glossary=None, cheatsheet="",
          self_check=None, review=None, milestone="", authored=True):
    return {
        "number": number, "month": month, "month_title": month_title,
        "theme": theme, "goal": goal, "summary": _prog(summary) if summary else "",
        "authored": authored, "lessons": lessons, "capstone": capstone,
        "objectives": objectives or [], "why": why, "est_minutes": est_minutes,
        "glossary": glossary or [], "cheatsheet": _prog(cheatsheet) if cheatsheet else "",
        "self_check": self_check or [], "review": review or [], "milestone": milestone,
    }


def _skel(number, month, month_title, theme, goal, summary=""):
    return _week(number, month, month_title, theme, goal, summary, [], None,
                 authored=False)


_FS = 'import * as fs from "fs";\n'
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
named variables, and do arithmetic. That's genuinely what most programs do: take
some values, combine them, and print a result.

Everything you write is **checked instantly**. Replace the `____` in each drill,
then press **Check**.
""",
    objectives=[
        "Print text and numbers with console.log",
        "Store values in const and let variables",
        "Do arithmetic with + - * / and %",
        "Build a line of output by joining strings",
    ],
    why="Every program you'll ever write starts by holding values and showing results — this is the bedrock.",
    est_minutes=35,
    glossary=[
        _gloss("statement", "One instruction, usually ending in a semicolon."),
        _gloss("string", "Text, written inside quotes: \"hello\"."),
        _gloss("variable", "A named box that holds a value."),
        _gloss("const", "A variable whose value never changes."),
        _gloss("let", "A variable you can reassign later."),
        _gloss("operator", "A symbol that combines values: + - * / %."),
    ],
    cheatsheet="""
```ts
console.log("hi");        // print text + newline
const name = "Ada";       // fixed value
let count = 0;            // reassignable
count = count + 1;        // reassign
6 * 7                     // 42   (* / + - )
17 % 5                    // 2    (remainder)
"a" + "b"                // "ab"  (join strings)
```
""",
    self_check=[
        "Can you print an exact line of text?",
        "Can you explain when to use const vs let?",
        "Can you compute a total from a price and a quantity?",
    ],
    review=[
        _q("Which declares a value that never changes?",
           ["let x = 1", "const x = 1", "var x = 1", "x = 1"], 1,
           "const fixes the binding; let allows reassignment."),
        _q("What does 17 % 5 evaluate to?", ["3", "2", "3.4", "12"], 1,
           "% is the remainder: 17 = 3*5 + 2."),
        _q('What does "5" + 3 look like if both were strings joined?',
           ['8', '"53"', 'error', '15'], 1,
           "Joining strings with + concatenates them; \"5\"+\"3\" is \"53\"."),
    ],
    milestone="You can already write a program that prints a formatted receipt line. That's real code!",
    lessons=[
        _lesson(
            "w1-hello", "Your first program",
            "Printing text with console.log.",
            """
A **program** is a list of instructions run top to bottom. The one you'll use
most is `console.log(...)`, which prints its argument followed by a newline.

```ts
console.log("Hello, world!");
```

Text in quotes is a **string**. Every statement ends with `;`.

> ⚠️ **Common mistakes:** forgetting the quotes around text, or forgetting the
> parentheses — it's `console.log("hi")`, not `console.log "hi"`.
""",
            warmup=[
                _q('What does `console.log("Hi")` print?',
                   ['"Hi"', "Hi", "Hi (with quotes)", "nothing"], 1,
                   "The quotes mark the string; they aren't printed."),
                _q("What does `console.log(2 + 3)` print?",
                   ["2 + 3", "23", "5", "\"5\""], 2,
                   "2 + 3 is arithmetic, so it prints 5."),
            ],
            exercises=[
                _ex("tscourse-w1-hello-1", "Print a greeting",
                    "Make the program print exactly: Hello, world!",
                    'console.log("Hello, world!");\n',
                    '"Hello, world!"', [("", "Hello, world!")],
                    hints=["A string is text in double quotes.",
                           'Put "Hello, world!" inside console.log(...).']),
                _ex("tscourse-w1-hello-2", "Print two lines",
                    "Print `Line one` then `Line two`, each on its own line.",
                    'console.log("Line one");\nconsole.log("Line two");\n',
                    '"Line two"', [("", "Line one\nLine two")],
                    hints=["Each console.log prints its own line.",
                           'The second line should print "Line two".']),
                _fix("tscourse-w1-hello-fix", "Fix the greeting",
                     "This should print `Hello!` but it prints the wrong thing. Fix it.",
                     'console.log("Goodbye!");\n',
                     'console.log("Hello!");\n',
                     [("", "Hello!")],
                     hints=["Look at the text inside the quotes.",
                            'Change "Goodbye!" to "Hello!".']),
            ],
        ),
        _lesson(
            "w1-variables", "Variables: let and const",
            "Naming values so you can reuse them.",
            """
A **variable** is a named box for a value. Use `const` when the value never
changes, `let` when you'll reassign it. Prefer `const`.

```ts
const name = "Ada";
let count = 0;
count = count + 1;   // reassigned to 1
```

> ⚠️ **Common mistakes:** trying to reassign a `const` (that's an error), or
> writing `let` again when you reassign — the second time it's just `count = 2`.
""",
            warmup=[
                _q("After `let n = 1; n = n + 4;`, what is n?",
                   ["1", "5", "14", "4"], 1, "n becomes 1 + 4 = 5."),
            ],
            exercises=[
                _ex("tscourse-w1-var-1", "Name a value",
                    "Store `Ada` in `name` so it prints `Hello, Ada`.",
                    'const name = "Ada";\nconsole.log("Hello, " + name);\n',
                    '"Ada"', [("", "Hello, Ada")],
                    hints=["Joining strings with + is concatenation.",
                           'Set name to the string "Ada".']),
                _ex("tscourse-w1-var-2", "Reassign with let",
                    "Reassign `count` to 2 so the program prints 2.",
                    'let count = 1;\ncount = 2;\nconsole.log(count);\n',
                    'count = 2;', [("", "2")],
                    hints=["Reassignment doesn't repeat `let`.",
                           "Write `count = 2;`."]),
                _fix("tscourse-w1-var-fix", "Fix the reassignment",
                     "This should print 10 but has a bug. Fix it so it prints 10.",
                     'let total = 4;\nlet total = 10;\nconsole.log(total);\n',
                     'let total = 4;\ntotal = 10;\nconsole.log(total);\n',
                     [("", "10")],
                     hints=["You can only declare a variable with `let` once.",
                            "The second line should reassign, not redeclare — drop the `let`."]),
            ],
        ),
        _lesson(
            "w1-numbers", "Numbers & arithmetic",
            "Doing math with + - * / and %.",
            """
One `number` type covers whole numbers and decimals. Operators: `+ - * /` and
`%` (remainder — what's left after division).

```ts
6 * 7      // 42
17 % 5     // 2
10 / 4     // 2.5
```

> ⚠️ **Common mistakes:** expecting `10 / 3` to be a whole number (it's
> 3.333…), and mixing up `/` (divide) with `%` (remainder).
""",
            warmup=[
                _q("What does `console.log(10 / 4)` print?",
                   ["2", "2.5", "3", "2.4"], 1, "Division keeps the decimal: 2.5."),
                _q("What does `console.log(9 % 2)` print?",
                   ["4.5", "0", "1", "4"], 2, "9 = 4*2 + 1, remainder 1."),
            ],
            exercises=[
                _ex("tscourse-w1-num-1", "Multiply",
                    "Print the product of `a` and `b` (should be 42).",
                    'const a = 6;\nconst b = 7;\nconsole.log(a * b);\n',
                    'a * b', [("", "42")],
                    hints=["Use the * operator.", "Write `a * b`."]),
                _ex("tscourse-w1-num-2", "Remainder",
                    "Print the remainder of `total` divided by 5.",
                    'const total = 17;\nconsole.log(total % 5);\n',
                    'total % 5', [("", "2")],
                    hints=["`%` gives the remainder.", "Write `total % 5`."]),
                _fix("tscourse-w1-num-fix", "Fix the total",
                     "This should print the SUM of a and b (8) but prints something else.",
                     'const a = 5;\nconst b = 3;\nconsole.log(a - b);\n',
                     'const a = 5;\nconst b = 3;\nconsole.log(a + b);\n',
                     [("", "8")],
                     hints=["Check the operator between a and b.",
                            "A sum uses + , not - ."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #1 — a receipt line",
        """
Meet **Budget Buddy**, the little expense tool you'll grow all through the
course. This week: using only `const`, arithmetic, and string joining, print a
two-line receipt for **4 coffees at $3 each**, against a **$20** budget:

```
Coffee x4 = $12
Remaining: $8
```
""",
        _ch("tscourse-w1-capstone", "Budget Buddy #1", "Intro",
            "Compute the line total and remaining budget, and print both lines.",
            'const item = "Coffee";\n'
            'const price = 3;\n'
            'const qty = 4;\n'
            'const budget = 20;\n'
            'const lineTotal = price * qty;\n'
            'console.log(item + " x" + qty + " = $" + lineTotal);\n'
            'console.log("Remaining: $" + (budget - lineTotal));\n',
            'const lineTotal = price * qty;\n'
            'console.log(item + " x" + qty + " = $" + lineTotal);\n'
            'console.log("Remaining: $" + (budget - lineTotal));',
            [("", "Coffee x4 = $12\nRemaining: $8")],
            hints=["lineTotal is price * qty.",
                   "Remaining is budget - lineTotal.",
                   'Build each line by joining strings with + , e.g. "Remaining: $" + (budget - lineTotal).']),
        example_io="Coffee x4 = $12\nRemaining: $8",
        rubric=["Prints the item, quantity and line total on line 1",
                "Prints the remaining budget on line 2",
                "Uses variables (not hard-coded 12 and 8)"],
        stretch=_ch("tscourse-w1-capstone-stretch", "Budget Buddy #1 (stretch)", "Easy",
                    "Also print a third line: the price of a single item as `Each: $3`.",
                    'const item = "Coffee";\n'
                    'const price = 3;\n'
                    'const qty = 4;\n'
                    'const budget = 20;\n'
                    'const lineTotal = price * qty;\n'
                    'console.log(item + " x" + qty + " = $" + lineTotal);\n'
                    'console.log("Remaining: $" + (budget - lineTotal));\n'
                    'console.log("Each: $" + price);\n',
                    'const lineTotal = price * qty;\n'
                    'console.log(item + " x" + qty + " = $" + lineTotal);\n'
                    'console.log("Remaining: $" + (budget - lineTotal));\n'
                    'console.log("Each: $" + price);',
                    [("", "Coffee x4 = $12\nRemaining: $8\nEach: $3")],
                    hints=["Add one more console.log at the end.",
                           'Print "Each: $" + price.']),
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

Most programs from now on start by reading standard input:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
```

`fs.readFileSync(0, "utf8")` reads everything typed as one string; `.trim()`
removes the trailing newline.
""",
    objectives=[
        "Read a line of input from the user",
        "Insert values into text with template literals",
        "Use .length, .toUpperCase() and .trim()",
        "Build multi-line output from input",
    ],
    why="Real programs respond to input — a search box, a form, a command. Reading input is step one.",
    est_minutes=40,
    glossary=[
        _gloss("standard input", "The stream of text a program reads from (what the user types)."),
        _gloss("template literal", "A backtick string with ${...} holes: `Hi ${name}`."),
        _gloss("method", "A function attached to a value: s.toUpperCase()."),
        _gloss(".trim()", "Removes whitespace from both ends of a string."),
        _gloss(".length", "A property giving the number of characters."),
    ],
    cheatsheet="""
```ts
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();  // read input
`Hi ${name}, you are ${age}`   // template literal
s.length            // number of characters
s.toUpperCase()     // "HELLO"
s.includes("ell")   // true / false
s.slice(0, 3)       // first 3 characters
```
""",
    self_check=[
        "Can you read a line of input and print it back?",
        "Can you build a sentence that includes a value with a template literal?",
        "Do you know the difference between .length (a property) and .toUpperCase() (a method call)?",
    ],
    review=[
        _q("Why call .trim() on input?",
           ["To uppercase it", "To remove the trailing newline / stray spaces",
            "To make it a number", "To split it"], 1,
           "Input usually ends in a newline; trim removes surrounding whitespace."),
        _q("Which builds `Hi Sam` from `const name = \"Sam\"`?",
           ['"Hi " + name', "`Hi ${name}`", "Both of these", "Neither"], 2,
           "Concatenation and template literals both work; templates are clearer."),
        _q("`\"hello\".length` is…", ["a method call", "5", "\"5\"", "an error"], 1,
           "length is a property whose value is 5."),
    ],
    milestone="Budget Buddy can now label an expense entry from whatever the user types.",
    lessons=[
        _lesson(
            "w2-input", "Reading input",
            "Getting text from standard input.",
            """
Read it all, trim it, and you have a string to work with.

```ts
import * as fs from "fs";
const line = fs.readFileSync(0, "utf8").trim();
console.log(line);
```

> ⚠️ **Common mistakes:** forgetting `.trim()` (your output ends up with an
> extra blank line), or forgetting the `import` line at the top.
""",
            warmup=[
                _q("If the user types `cat` and the program does `console.log(input)`, output is…",
                   ["cat", "\"cat\"", "input", "3"], 0, "It echoes the text: cat."),
            ],
            exercises=[
                _ex("tscourse-w2-input-1", "Echo the input",
                    "Read the whole input (trimmed) and print it back.",
                    _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(input);\n',
                    'fs.readFileSync(0, "utf8").trim()',
                    [("hello\n", "hello"), ("  spaced  ", "spaced")],
                    hints=["readFileSync(0, \"utf8\") reads stdin.",
                           "Add .trim() to drop surrounding whitespace."]),
                _ex("tscourse-w2-input-2", "Greet the input",
                    "Read a name and print `Hello, <name>!`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log("Hello, " + name + "!");\n',
                    '"Hello, " + name + "!"',
                    [("Ada", "Hello, Ada!"), ("Bo", "Hello, Bo!")],
                    hints=["Join the three pieces with +.",
                           'It is "Hello, " + name + "!".']),
                _fix("tscourse-w2-input-fix", "Fix the echo",
                     "This should echo what the user typed, but it prints a fixed word. Fix it.",
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log("input");\n',
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(input);\n',
                     [("hello", "hello"), ("bo", "bo")],
                     hints=['It prints the literal word "input" instead of the value.',
                            "Log the variable input (no quotes)."]),
            ],
        ),
        _lesson(
            "w2-templates", "Template literals",
            "Splicing values into text with backticks.",
            """
Backtick strings drop values straight into text with `${ }`.

```ts
const name = "Sam";
`Hi ${name}`        // Hi Sam
`2 + 2 = ${2 + 2}`  // 2 + 2 = 4
```

> ⚠️ **Common mistakes:** using normal quotes instead of backticks (then
> `${name}` prints literally), or forgetting the `$` before `{ }`.
""",
            warmup=[
                _q("With `const n = 3;`, what does `` `n = ${n}` `` produce?",
                   ["n = ${n}", "n = 3", "n = n", "3"], 1,
                   "${n} is replaced by the value 3."),
            ],
            exercises=[
                _ex("tscourse-w2-tmpl-1", "Welcome message",
                    "Use a template literal to print `Hi <name>, welcome!`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`Hi ${name}, welcome!`);\n',
                    '`Hi ${name}, welcome!`',
                    [("Sam", "Hi Sam, welcome!"), ("Ada", "Hi Ada, welcome!")],
                    hints=["Use backticks, not quotes.",
                           "Put ${name} inside the text."]),
                _ex("tscourse-w2-tmpl-2", "Inline arithmetic",
                    "Print `<a> + <b> = <sum>` using a template literal.",
                    'const a = 3;\nconst b = 4;\nconsole.log(`${a} + ${b} = ${a + b}`);\n',
                    '`${a} + ${b} = ${a + b}`',
                    [("", "3 + 4 = 7")],
                    hints=["You can put an expression like a + b inside ${ }.",
                           "The template is `${a} + ${b} = ${a + b}`."]),
                _fix("tscourse-w2-tmpl-fix", "Fix the template",
                     "This was meant to greet the name but prints it literally. Fix it.",
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     "console.log('Hi ${name}!');\n",
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(`Hi ${name}!`);\n',
                     [("Sam", "Hi Sam!")],
                     hints=["${...} only works inside backticks.",
                            "Swap the single quotes for backticks (`)."]),
            ],
        ),
        _lesson(
            "w2-methods", "String methods",
            "Inspecting and transforming text.",
            """
```ts
const s = "hello";
s.length         // 5   (property, no parentheses)
s.toUpperCase()  // HELLO
s.includes("ell")// true
s.slice(0, 3)    // hel
```

> ⚠️ **Common mistakes:** writing `s.length()` — `length` is a property, so no
> parentheses. Methods like `toUpperCase()` DO need them.
""",
            warmup=[
                _q('What is `"hi".toUpperCase()`?', ["hi", "HI", "Hi", '"HI"'], 1,
                   "toUpperCase returns HI."),
                _q('What is `"cat".length`?', ["cat", "2", "3", "\"3\""], 2,
                   "cat has 3 characters."),
            ],
            exercises=[
                _ex("tscourse-w2-meth-1", "Shout it",
                    "Print the input in UPPERCASE.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toUpperCase());\n',
                    's.toUpperCase()',
                    [("hello", "HELLO"), ("Bo", "BO")],
                    hints=["Call .toUpperCase() on the string."]),
                _ex("tscourse-w2-meth-2", "Count the letters",
                    "Print how many characters the input has.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.length);\n',
                    's.length',
                    [("hello", "5"), ("hi", "2")],
                    hints=["length is a property — no parentheses."]),
                _fix("tscourse-w2-meth-fix", "Fix the length call",
                     "This should print the length but crashes. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length());\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length);\n',
                     [("hello", "5")],
                     hints=["length is a property, not a method.",
                            "Remove the () after length."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #2 — entry label",
        """
Read a single expense **description** and print a tidy three-line label:

```
Entry: coffee
Tag: COFFEE
Length: 6
```
""",
        _ch("tscourse-w2-capstone", "Budget Buddy #2", "Intro",
            "Print the three lines exactly, based on the input description.",
            _FS + 'const desc = fs.readFileSync(0, "utf8").trim();\n'
            'console.log(`Entry: ${desc}`);\n'
            'console.log(`Tag: ${desc.toUpperCase()}`);\n'
            'console.log(`Length: ${desc.length}`);\n',
            'console.log(`Entry: ${desc}`);\n'
            'console.log(`Tag: ${desc.toUpperCase()}`);\n'
            'console.log(`Length: ${desc.length}`);',
            [("coffee", "Entry: coffee\nTag: COFFEE\nLength: 6"),
             ("rent", "Entry: rent\nTag: RENT\nLength: 4")],
            hints=["One template-literal console.log per line.",
                   "Use ${desc.toUpperCase()} and ${desc.length}."]),
        example_io="Entry: coffee\nTag: COFFEE\nLength: 6",
        rubric=["Line 1 echoes the description",
                "Line 2 is the description uppercased",
                "Line 3 is the character count"],
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

One helper you'll need: input arrives as **text**, so wrap it in `Number(...)`
for math or numeric comparisons:

```ts
const n = Number(fs.readFileSync(0, "utf8").trim());  // "42" -> 42
```
""",
    objectives=[
        "Compare values with === , !== , < , > and produce booleans",
        "Convert input text to a number with Number(...)",
        "Branch with if / else if / else",
        "Combine conditions with && , || and !",
    ],
    why="Decisions are how software adapts — access control, pricing tiers, validation. It's all if/else.",
    est_minutes=45,
    glossary=[
        _gloss("boolean", "A value that is either true or false."),
        _gloss("===", "Strict equality — compares without surprise conversions."),
        _gloss("Number(x)", "Converts a numeric string to a number."),
        _gloss("if / else", "Runs one block or another depending on a condition."),
        _gloss("&& , || , !", "Logical AND, OR, and NOT."),
    ],
    cheatsheet="""
```ts
const n = Number(input);        // text -> number
5 > 3            // true
a === b          // strict equality (use this, not ==)
if (n >= 0) { ... } else { ... }
if (s >= 90) {...} else if (s >= 80) {...} else {...}
a && b   // both true
a || b   // either true
!a       // not
```
""",
    self_check=[
        "Can you convert input text to a number and compare it?",
        "Can you write an if / else if / else chain that picks the right branch?",
        "Do you know why === is preferred over == ?",
    ],
    review=[
        _q("Which operator is strict equality?", ["=", "==", "===", "=>"], 2,
           "=== compares without type coercion; = is assignment."),
        _q("`Number(\"7\")` produces…", ['"7"', "7", "true", "an error"], 1,
           "It converts the string to the number 7."),
        _q("`(n >= 1 && n <= 5)` is true when…",
           ["n is 1..5 inclusive", "n is any number", "n is 0", "never"], 0,
           "Both parts must hold: n between 1 and 5."),
    ],
    milestone="Budget Buddy can now judge an expense — small, medium, or large.",
    lessons=[
        _lesson(
            "w3-compare", "Booleans & comparison",
            "Values that are true or false.",
            """
Comparisons produce a **boolean**. Always compare with `===` / `!==` (strict),
plus `<`, `>`, `<=`, `>=`.

```ts
5 > 3        // true
"a" === "b"  // false
10 >= 10     // true
```

`console.log(someBoolean)` prints `true` or `false`.

> ⚠️ **Common mistakes:** using `=` (assignment) where you meant `===`
> (comparison), and comparing input text to a number without `Number(...)`.
""",
            warmup=[
                _q("What does `console.log(4 > 9)` print?",
                   ["true", "false", "4", "9"], 1, "4 is not greater than 9."),
                _q('What does `console.log("a" === "a")` print?',
                   ["a", "true", "false", "1"], 1, "The strings are equal."),
            ],
            exercises=[
                _ex("tscourse-w3-cmp-1", "Greater than ten",
                    "Print whether the number is greater than 10.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n > 10);\n',
                    'n > 10',
                    [("15", "true"), ("3", "false"), ("10", "false")],
                    hints=["Use the > operator.",
                           "console.log prints the boolean directly."]),
                _ex("tscourse-w3-cmp-2", "Exact match",
                    "Print whether the input equals the string `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s === "yes");\n',
                    's === "yes"',
                    [("yes", "true"), ("no", "false")],
                    hints=["Use === for a strict comparison.",
                           'Compare s to "yes".']),
                _fix("tscourse-w3-cmp-fix", "Fix the threshold",
                     "This should be true only when STRICTLY greater than 10, but 10 itself prints true. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 10);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n > 10);\n',
                     [("15", "true"), ("10", "false"), ("3", "false")],
                     hints=[">= includes 10 itself.",
                            "Use > for strictly greater than."]),
            ],
        ),
        _lesson(
            "w3-ifelse", "if / else",
            "Choosing between branches.",
            """
`if` runs a block when its condition is true; `else` covers the rest; `else if`
chains more tests. Only the **first** matching branch runs.

```ts
if (score >= 90) {
  console.log("A");
} else if (score >= 80) {
  console.log("B");
} else {
  console.log("C");
}
```

> ⚠️ **Common mistakes:** ordering branches wrong (a broad test first swallows
> the narrow ones), and forgetting that only one branch runs.
""",
            warmup=[
                _q("With score = 85, which line prints from the chain above?",
                   ["A", "B", "C", "all three"], 1,
                   "85 fails >=90 but passes >=80, so B."),
            ],
            exercises=[
                _ex("tscourse-w3-if-1", "Sign of a number",
                    "Print `non-negative` when n >= 0, else `negative`.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (n >= 0) {\n  console.log("non-negative");\n} else {\n  console.log("negative");\n}\n',
                    'n >= 0',
                    [("5", "non-negative"), ("-2", "negative"), ("0", "non-negative")],
                    hints=["Zero counts as non-negative.", "Use >= 0."]),
                _ex("tscourse-w3-if-2", "Letter grade",
                    "Fill the middle test so 85→B, 95→A, 70→C.",
                    _FS + 'const score = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (score >= 90) {\n  console.log("A");\n} else if (score >= 80) {\n  console.log("B");\n} else {\n  console.log("C");\n}\n',
                    'score >= 80',
                    [("95", "A"), ("85", "B"), ("70", "C")],
                    hints=["The B band is 80 or more.", "Write score >= 80."]),
                _fix("tscourse-w3-if-fix", "Fix the branch order",
                     "Every input prints `adult`. Fix the logic so age 10 prints `minor`, age 40 prints `adult`.",
                     _FS + 'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (age >= 0) {\n  console.log("adult");\n} else if (age < 18) {\n  console.log("minor");\n} else {\n  console.log("adult");\n}\n',
                     _FS + 'const age = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'if (age < 18) {\n  console.log("minor");\n} else {\n  console.log("adult");\n}\n',
                     [("10", "minor"), ("40", "adult"), ("18", "adult")],
                     hints=["`age >= 0` is true for everyone, so it always wins.",
                            "Test the minor case (age < 18) first."],
                     difficulty="Medium"),
            ],
        ),
        _lesson(
            "w3-logic", "Logical operators",
            "Combining conditions with && , || and !.",
            """
- `a && b` — true only when **both** are true.
- `a || b` — true when **either** is true.
- `!a` — flips a boolean.

```ts
n >= 1 && n <= 5       // in range 1..5 ?
s === "y" || s === "yes"
```

> ⚠️ **Common mistakes:** writing `1 <= n <= 5` (doesn't work as you'd expect) —
> use `n >= 1 && n <= 5`.
""",
            warmup=[
                _q("`true && false` is…", ["true", "false"], 1,
                   "AND needs both true."),
                _q("`false || true` is…", ["true", "false"], 0,
                   "OR needs just one true."),
            ],
            exercises=[
                _ex("tscourse-w3-log-1", "In range",
                    "Print whether n is between 1 and 5 (inclusive).",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n >= 1 && n <= 5);\n',
                    'n >= 1 && n <= 5',
                    [("3", "true"), ("9", "false"), ("1", "true")],
                    hints=["Both conditions must hold.", "Use && between them."]),
                _ex("tscourse-w3-log-2", "Yes in either form",
                    "Print true when the input is `y` or `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s === "y" || s === "yes");\n',
                    's === "y" || s === "yes"',
                    [("yes", "true"), ("y", "true"), ("n", "false")],
                    hints=["Either spelling is acceptable.", "Use || between the two checks."]),
                _fix("tscourse-w3-log-fix", "Fix the range test",
                     "This should be true only for 1..5, but 9 also prints true. Fix it.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 1 || n <= 5);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(n >= 1 && n <= 5);\n',
                     [("3", "true"), ("9", "false")],
                     hints=["|| is true when EITHER side holds — too loose here.",
                            "Both must hold, so use &&."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #3 — size an expense",
        """
Read an expense **amount** and print its size band:

- under 10 → `small`
- 10 to 49 → `medium`
- 50 and up → `large`
""",
        _ch("tscourse-w3-capstone", "Budget Buddy #3", "Easy",
            "Print small / medium / large for the given amount.",
            _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
            'if (amt < 10) {\n  console.log("small");\n} else if (amt < 50) {\n  console.log("medium");\n} else {\n  console.log("large");\n}\n',
            'if (amt < 10) {\n  console.log("small");\n} else if (amt < 50) {\n  console.log("medium");\n} else {\n  console.log("large");\n}',
            [("4", "small"), ("25", "medium"), ("50", "large"), ("9", "small"), ("49", "medium")],
            hints=["Test the smallest band first.",
                   "small is < 10, medium is < 50, else large."]),
        example_io="(amount 25) → medium",
        rubric=["Handles amounts below 10, 10–49, and 50+",
                "Uses an if / else if / else chain",
                "Reads the amount as a number"],
        stretch=_ch("tscourse-w3-capstone-stretch", "Budget Buddy #3 (stretch)", "Medium",
                    "Also flag over-budget: if the amount is 50+, print `large (over budget!)`.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'if (amt < 10) {\n  console.log("small");\n} else if (amt < 50) {\n  console.log("medium");\n} else {\n  console.log("large (over budget!)");\n}\n',
                    'if (amt < 10) {\n  console.log("small");\n} else if (amt < 50) {\n  console.log("medium");\n} else {\n  console.log("large (over budget!)");\n}',
                    [("4", "small"), ("25", "medium"), ("80", "large (over budget!)")],
                    hints=["Only the last branch changes.",
                           'Print "large (over budget!)" for 50+.']),
    ),
))

# --- Week 4 ---------------------------------------------------------------
_WEEKS.append(_week(
    4, 1, _M1,
    "Loops",
    "Repeat work with while and for loops, and accumulate results.",
    """
Computers shine at doing the same thing many times. This week: `while` and `for`
loops, the idea of an **accumulator** (a running total/counter), and `for...of`
for walking through text a character at a time.
""",
    objectives=[
        "Repeat work with while and for loops",
        "Build a running total or counter (an accumulator)",
        "Walk a string with for...of",
        "Know how to avoid an infinite loop",
    ],
    why="Loops power everything repetitive — from summing a column of numbers to a game's frame loop.",
    est_minutes=50,
    glossary=[
        _gloss("loop", "Code that repeats while a condition holds."),
        _gloss("accumulator", "A variable that builds a result across iterations."),
        _gloss("for", "A compact loop with setup, condition, and step on one line."),
        _gloss("for...of", "A loop that hands you each item of a sequence."),
        _gloss("infinite loop", "A loop whose condition never becomes false — it never ends."),
    ],
    cheatsheet="""
```ts
let i = 1;
while (i <= n) { sum = sum + i; i = i + 1; }   // while
for (let i = 1; i <= n; i = i + 1) { ... }      // for
for (const ch of "hello") { ... }                // each character
```
""",
    self_check=[
        "Can you sum the numbers 1..n with a loop?",
        "Can you count how often a character appears in a string?",
        "Can you explain what makes a loop infinite?",
    ],
    review=[
        _q("What is an accumulator?",
           ["A loop keyword", "A variable that builds a result across iterations",
            "A comparison", "An input reader"], 1,
           "Like a running sum or counter."),
        _q("A while loop whose condition never becomes false…",
           ["runs once", "never runs", "loops forever", "errors"], 2,
           "It's an infinite loop."),
        _q("`for (const ch of \"hi\")` runs the body…",
           ["once", "twice (h, then i)", "three times", "never"], 1,
           "Once per character: h, i."),
    ],
    milestone="Budget Buddy can now project a savings schedule day by day.",
    lessons=[
        _lesson(
            "w4-while", "while loops",
            "Repeat while a condition holds.",
            """
A `while` loop runs its body while its condition is true. Something inside must
move toward making it false.

Watch the state evolve summing 1..3:

| step | i | i <= 3 | sum after |
|------|---|--------|-----------|
| start| 1 | —      | 0         |
| 1    | 1 | true   | 1         |
| 2    | 2 | true   | 3         |
| 3    | 3 | true   | 6         |
| end  | 4 | false  | 6         |

```ts
let i = 1, sum = 0;
while (i <= 3) { sum = sum + i; i = i + 1; }
console.log(sum);   // 6
```

> ⚠️ **Common mistakes:** forgetting to advance `i`, which loops forever.
""",
            warmup=[
                _q("`let i=0; while(i<2){ i = i+1; } console.log(i);` prints…",
                   ["0", "1", "2", "forever"], 2, "i climbs to 2, then i<2 is false."),
            ],
            exercises=[
                _ex("tscourse-w4-while-1", "Sum 1..n",
                    "Loop while i <= n, adding each i to sum. Print the total.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let sum = 0;\nlet i = 1;\nwhile (i <= n) {\n  sum = sum + i;\n  i = i + 1;\n}\nconsole.log(sum);\n',
                    'i <= n',
                    [("5", "15"), ("1", "1"), ("10", "55")],
                    hints=["Keep going while i has not passed n.", "Condition: i <= n."]),
                _ex("tscourse-w4-while-2", "Countdown",
                    "Print n, n-1, … down to 1, each on its own line.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let i = n;\nwhile (i >= 1) {\n  console.log(i);\n  i = i - 1;\n}\n',
                    'i = i - 1;',
                    [("3", "3\n2\n1"), ("1", "1")],
                    hints=["Move i toward 0 each pass.", "Write i = i - 1;"]),
                _fix("tscourse-w4-while-fix", "Fix the infinite loop",
                     "This loop never ends because i never changes. Fix it so it prints 1 2 3.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nwhile (i <= n) {\n  console.log(i);\n}\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let i = 1;\nwhile (i <= n) {\n  console.log(i);\n  i = i + 1;\n}\n',
                     [("3", "1\n2\n3")],
                     hints=["Nothing advances i, so i <= n stays true forever.",
                            "Add i = i + 1; inside the loop."],
                     difficulty="Medium"),
            ],
        ),
        _lesson(
            "w4-for", "for loops",
            "A compact counting loop.",
            """
A `for` loop packs setup, condition, and step into one line:

```ts
for (let i = 1; i <= n; i = i + 1) {
  // body runs for i = 1, 2, ... n
}
```

Same idea as `while`, tidier when counting.

> ⚠️ **Common mistakes:** an off-by-one — `i < n` stops at n-1, `i <= n` includes n.
""",
            warmup=[
                _q("`for (let i=0; i<3; i=i+1) console.log(i);` prints…",
                   ["0 1 2 3", "0 1 2", "1 2 3", "3"], 1, "i < 3 runs for 0,1,2."),
            ],
            exercises=[
                _ex("tscourse-w4-for-1", "Factorial",
                    "Multiply 1*2*...*n into product. Print it.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let product = 1;\nfor (let i = 1; i <= n; i = i + 1) {\n  product = product * i;\n}\nconsole.log(product);\n',
                    'product = product * i;',
                    [("5", "120"), ("1", "1"), ("4", "24")],
                    hints=["Each pass multiplies the running product by i.",
                           "Write product = product * i;"]),
                _ex("tscourse-w4-for-2", "Count evens",
                    "Count how many numbers from 1..n are even. Print the count.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let count = 0;\nfor (let i = 1; i <= n; i = i + 1) {\n  if (i % 2 === 0) {\n    count = count + 1;\n  }\n}\nconsole.log(count);\n',
                    'i % 2 === 0',
                    [("10", "5"), ("1", "0"), ("2", "1")],
                    hints=["Even means remainder 0 mod 2.", "Test i % 2 === 0."]),
                _fix("tscourse-w4-for-fix", "Fix the off-by-one",
                     "This should sum 1..n but leaves out n. Fix the loop so sum(1..3)=6.",
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nfor (let i = 1; i < n; i = i + 1) {\n  sum = sum + i;\n}\nconsole.log(sum);\n',
                     _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'let sum = 0;\nfor (let i = 1; i <= n; i = i + 1) {\n  sum = sum + i;\n}\nconsole.log(sum);\n',
                     [("3", "6"), ("5", "15")],
                     hints=["`i < n` stops one short — it never adds n itself.",
                            "Use i <= n."]),
            ],
        ),
        _lesson(
            "w4-forof", "Looping over text",
            "for...of walks a string character by character.",
            """
`for...of` hands you each character in turn.

```ts
let vowels = 0;
for (const ch of "hello") {
  if (ch === "e" || ch === "o") vowels = vowels + 1;
}
console.log(vowels);   // 2
```

> ⚠️ **Common mistakes:** confusing `for...of` (values) with `for...in` (keys) —
> for strings and arrays you almost always want `for...of`.
""",
            warmup=[
                _q('How many times does `for (const c of "aba")` run its body?',
                   ["1", "2", "3", "0"], 2, "Once per character: a, b, a."),
            ],
            exercises=[
                _ex("tscourse-w4-of-1", "Count a letter",
                    "Count how many times the letter `a` appears in the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let count = 0;\nfor (const ch of s) {\n  if (ch === "a") {\n    count = count + 1;\n  }\n}\nconsole.log(count);\n',
                    'ch === "a"',
                    [("banana", "3"), ("xyz", "0"), ("aaa", "3")],
                    hints=['Compare each character to "a".']),
                _ex("tscourse-w4-of-2", "Reverse a string",
                    "Build the input backwards by putting each new char in front.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'let out = "";\nfor (const ch of s) {\n  out = ch + out;\n}\nconsole.log(out);\n',
                    'ch + out',
                    [("abc", "cba"), ("hello", "olleh")],
                    hints=["Prepend each character.", "Write ch + out."]),
                _fix("tscourse-w4-of-fix", "Fix the reversal",
                     "This should reverse the string but returns it unchanged. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  out = out + ch;\n}\nconsole.log(out);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'let out = "";\nfor (const ch of s) {\n  out = ch + out;\n}\nconsole.log(out);\n',
                     [("abc", "cba")],
                     hints=["out + ch appends — that keeps the original order.",
                            "Prepend instead: ch + out."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #4 — savings schedule",
        """
Read a number of **days** and print a running savings total, adding **$5** each
day:

```
Day 1: $5
Day 2: $10
Day 3: $15
```
""",
        _ch("tscourse-w4-capstone", "Budget Buddy #4", "Easy",
            "Loop over the days, keep a running total, and print each day's line.",
            _FS + 'const days = Number(fs.readFileSync(0, "utf8").trim());\n'
            'let total = 0;\nfor (let d = 1; d <= days; d = d + 1) {\n  total = total + 5;\n  console.log(`Day ${d}: $${total}`);\n}\n',
            'let total = 0;\nfor (let d = 1; d <= days; d = d + 1) {\n  total = total + 5;\n  console.log(`Day ${d}: $${total}`);\n}',
            [("3", "Day 1: $5\nDay 2: $10\nDay 3: $15"), ("1", "Day 1: $5")],
            hints=["Keep a running total that grows by 5 each pass.",
                   "Print `Day ${d}: $${total}` inside the loop."]),
        example_io="Day 1: $5\nDay 2: $10\nDay 3: $15",
        rubric=["Loops once per day",
                "Keeps a running total (+$5 each day)",
                "Prints the day number and total on each line"],
        stretch=_ch("tscourse-w4-capstone-stretch", "Budget Buddy #4 (stretch)", "Medium",
                    "After the schedule, print `Total saved: $<total>`.",
                    _FS + 'const days = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'let total = 0;\nfor (let d = 1; d <= days; d = d + 1) {\n  total = total + 5;\n  console.log(`Day ${d}: $${total}`);\n}\nconsole.log(`Total saved: $${total}`);\n',
                    'let total = 0;\nfor (let d = 1; d <= days; d = d + 1) {\n  total = total + 5;\n  console.log(`Day ${d}: $${total}`);\n}\nconsole.log(`Total saved: $${total}`);',
                    [("3", "Day 1: $5\nDay 2: $10\nDay 3: $15\nTotal saved: $15")],
                    hints=["Print the summary line after the loop ends.",
                           "The total variable already holds the final amount."]),
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
A **function** is named, reusable logic: give it inputs (**parameters**), it
hands back a **return value**. Functions let you name an idea once and use it
everywhere. This week: declaring functions, arrow functions, and returning values.

You'll see annotations like `(x: number): number` — they document what goes in
and out. (They're checked as you write, then stripped before the program runs.)
""",
    objectives=[
        "Declare a function with parameters and a return value",
        "Call a function and use what it returns",
        "Write short functions as arrow functions",
        "Compose functions — feed one result into another",
    ],
    why="Functions are how you tame complexity: name a step once, reuse and test it everywhere.",
    est_minutes=45,
    glossary=[
        _gloss("function", "Named, reusable logic that takes inputs and returns a value."),
        _gloss("parameter", "A named input to a function."),
        _gloss("argument", "The actual value you pass in when calling."),
        _gloss("return", "Sends a value back to the caller and ends the function."),
        _gloss("arrow function", "A compact function: (x) => x * 2."),
    ],
    cheatsheet="""
```ts
function square(x: number): number { return x * x; }
const cube = (x: number): number => x * x * x;   // arrow (auto-return)
square(5)   // 25
cube(3)     // 27
```
""",
    self_check=[
        "Can you write a function that takes a number and returns a result?",
        "Can you call a function and print what it returns?",
        "Can you write the same tiny function as an arrow function?",
    ],
    review=[
        _q("What does `return` do?",
           ["Prints a value", "Sends a value back to the caller and ends the function",
            "Declares a variable", "Starts a loop"], 1,
           "return produces the function's result."),
        _q("In `function f(x: number)`, `x` is a…",
           ["return value", "parameter", "global", "type alias"], 1,
           "x is a parameter — an input."),
        _q("`const d = (x: number): number => x * 2; d(4)` is…",
           ["4", "8", "24", "error"], 1, "It doubles: 8."),
    ],
    milestone="Budget Buddy now has reusable money helpers — like applying tax.",
    lessons=[
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

`return` sends a value back and ends the function.

> ⚠️ **Common mistakes:** forgetting `return` (the function then returns
> `undefined`), and confusing `console.log` (prints) with `return` (hands back).
""",
            warmup=[
                _q("`function f(x){ return x + 1; } console.log(f(4));` prints…",
                   ["4", "5", "x + 1", "undefined"], 1, "f(4) returns 5."),
            ],
            exercises=[
                _ex("tscourse-w5-dec-1", "Square", "Return x times itself.",
                    'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                    'x * x', [("", "25")],
                    hints=["Multiply x by x.", "return x * x;"]),
                _ex("tscourse-w5-dec-2", "Greet", "Return a greeting string for the given name.",
                    'function greet(name: string): string {\n  return `Hello, ${name}!`;\n}\nconsole.log(greet("Ada"));\n',
                    '`Hello, ${name}!`', [("", "Hello, Ada!")],
                    hints=["Return a template literal using name."]),
                _fix("tscourse-w5-dec-fix", "Fix the missing return",
                     "This should print 25 but prints undefined. Fix it.",
                     'function square(x: number): number {\n  x * x;\n}\nconsole.log(square(5));\n',
                     'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                     [("", "25")],
                     hints=["The function computes x*x but never hands it back.",
                            "Add `return` before x * x."]),
            ],
        ),
        _lesson(
            "w5-params", "Parameters & return values",
            "Passing inputs and using the result.",
            """
Functions compose — one's result feeds the next.

```ts
function double(x: number): number { return x * 2; }
console.log(double(21));   // 42
```

> ⚠️ **Common mistakes:** mixing up the order of arguments, or forgetting to
> actually *call* the function (writing `double` instead of `double(21)`).
""",
            warmup=[
                _q("`function add(a,b){return a-b;} add(5,3)` returns…",
                   ["8", "2", "15", "error"], 1, "This (buggy) add subtracts: 5-3=2."),
            ],
            exercises=[
                _ex("tscourse-w5-par-1", "Double the input",
                    "Return x doubled; the program prints double(n) for the input n.",
                    _FS + 'function double(x: number): number {\n  return x * 2;\n}\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                    'x * 2', [("21", "42"), ("0", "0")],
                    hints=["Multiply the parameter by 2."]),
                _ex("tscourse-w5-par-2", "Absolute value",
                    "Return the negation of x when x is negative.",
                    _FS + 'function abs(x: number): number {\n  if (x < 0) {\n    return -x;\n  }\n  return x;\n}\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(abs(n));\n',
                    '-x', [("-5", "5"), ("7", "7")],
                    hints=["The opposite of x is -x."]),
                _fix("tscourse-w5-par-fix", "Fix the call",
                     "This should print 42 but prints a function, not a number. Fix the call.",
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double);\n',
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                     [("21", "42")],
                     hints=["`double` names the function; it doesn't run it.",
                            "Call it with the value: double(n)."]),
            ],
        ),
        _lesson(
            "w5-arrow", "Arrow functions",
            "A shorter way to write small functions.",
            """
When the body is a single expression, its value is returned automatically.

```ts
const cube = (x: number): number => x * x * x;
console.log(cube(3));   // 27
```

> ⚠️ **Common mistakes:** adding `{ }` around a single-expression arrow body but
> forgetting `return` — with braces you must write `return` yourself.
""",
            warmup=[
                _q("`const f = (x:number) => x + 10; f(5)` is…",
                   ["5", "10", "15", "error"], 2, "5 + 10 = 15."),
            ],
            exercises=[
                _ex("tscourse-w5-arr-1", "Cube (arrow)", "Return x cubed.",
                    'const cube = (x: number): number => x * x * x;\nconsole.log(cube(3));\n',
                    'x * x * x', [("", "27")],
                    hints=["x times x times x."]),
                _ex("tscourse-w5-arr-2", "Triple (arrow)",
                    "Return x * 3; print triple(n) for the input.",
                    _FS + 'const triple = (x: number): number => x * 3;\nconst n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'x * 3', [("5", "15"), ("10", "30")],
                    hints=["Multiply x by 3."]),
                _fix("tscourse-w5-arr-fix", "Fix the arrow body",
                     "This arrow has braces but forgot to return. Fix it so cube(2)=8.",
                     'const cube = (x: number): number => { x * x * x; };\nconsole.log(cube(2));\n',
                     'const cube = (x: number): number => x * x * x;\nconsole.log(cube(2));\n',
                     [("", "8")],
                     hints=["With { } you must write return yourself.",
                            "Either add return, or drop the braces for an auto-return arrow."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #5 — money helpers",
        """
Write two functions and use them. Read a **pre-tax amount** and print:

1. the amount with **8% tax** added (`withTax`)
2. that taxed amount rounded down to a whole dollar (`Math.floor`)

For input `50`:

```
54
54
```
(50 + 8% = 54 exactly.)
""",
        _ch("tscourse-w5-capstone", "Budget Buddy #5", "Easy",
            "Fill in the two function bodies.",
            _FS + 'function withTax(amount: number): number {\n  return amount * 1.08;\n}\n'
            'function whole(amount: number): number {\n  return Math.floor(amount);\n}\n'
            'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
            'console.log(withTax(amt));\nconsole.log(whole(withTax(amt)));\n',
            'function withTax(amount: number): number {\n  return amount * 1.08;\n}\n'
            'function whole(amount: number): number {\n  return Math.floor(amount);\n}',
            [("50", "54\n54"), ("100", "108\n108")],
            hints=["withTax multiplies by 1.08.",
                   "whole uses Math.floor(amount).",
                   "The second line prints whole(withTax(amt))."]),
        example_io="(amount 50) → 54  then  54",
        rubric=["withTax adds 8%", "whole floors to an integer dollar",
                "The two functions are composed on the last line"],
    ),
))

# --- Week 6 ---------------------------------------------------------------
_WEEKS.append(_week(
    6, 2, _M2,
    "Arrays",
    "Store lists of values and process them with loops and array methods.",
    """
An **array** is an ordered list, reached by index (`nums[0]` is the first). This
week: creating and indexing arrays, iterating them, and `map` / `filter` that
make list-processing concise.

To read a line of numbers into an array:

```ts
const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);
```

`.split(" ")` cuts the text at spaces; `.map(Number)` turns each piece into a number.
""",
    objectives=[
        "Create arrays and read elements by index",
        "Read a line of numbers into an array",
        "Loop over an array to sum or find a max",
        "Transform and filter with map and filter",
    ],
    why="Almost all real data is a list — rows, items, results. Arrays are how you hold and process them.",
    est_minutes=50,
    glossary=[
        _gloss("array", "An ordered list of values."),
        _gloss("index", "A position in an array, starting at 0."),
        _gloss(".split(sep)", "Cuts a string into an array of pieces."),
        _gloss(".map(f)", "Makes a new array by transforming each element."),
        _gloss(".filter(f)", "Keeps only the elements that pass a test."),
        _gloss(".join(sep)", "Glues an array back into a string."),
    ],
    cheatsheet="""
```ts
const a = [3, 5, 7];
a[0]         // 3   (index starts at 0)
a.length     // 3
"1 2 3".split(" ").map(Number)   // [1,2,3]
a.map((x) => x * 2)              // [6,10,14]
a.filter((x) => x > 4)           // [5,7]
a.join(" ")                       // "3 5 7"
```
""",
    self_check=[
        "Can you read numbers into an array and print the first one?",
        "Can you sum an array with a loop?",
        "Can you keep only the even numbers with filter?",
    ],
    review=[
        _q("The first element of an array is at index…", ["1", "0", "-1", "any"], 1,
           "Arrays are zero-indexed."),
        _q('`"3 5".split(" ")` gives…',
           ["35", '["3","5"]', '"3 5"', "error"], 1, "split cuts into pieces."),
        _q("`[1,2,3].filter((x)=>x>1).length` is…", ["1", "2", "3", "0"], 1,
           "Keeps 2 and 3 → length 2."),
    ],
    milestone="Budget Buddy can now crunch a whole month of expenses at once.",
    lessons=[
        _lesson(
            "w6-basics", "Creating & indexing",
            "Arrays and their indexes.",
            """
```ts
const names = ["Ada", "Bo", "Cy"];
names[0]      // Ada  (indexes start at 0)
names.length  // 3
```

> ⚠️ **Common mistakes:** expecting `a[1]` to be the first element (it's the
> *second*), and reading past the end (`a[a.length]` is `undefined`).
""",
            warmup=[
                _q('`const a = [10,20,30]; console.log(a[1]);` prints…',
                   ["10", "20", "30", "1"], 1, "Index 1 is the second element, 20."),
            ],
            exercises=[
                _ex("tscourse-w6-b-1", "First number",
                    "Read the numbers and print the first one.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[0]);\n',
                    'nums[0]', [("3 5 7", "3"), ("9", "9")],
                    hints=["The first element is at index 0."]),
                _ex("tscourse-w6-b-2", "How many",
                    "Print how many space-separated words the input has.",
                    _FS + 'const words = fs.readFileSync(0, "utf8").trim().split(" ");\nconsole.log(words.length);\n',
                    'words.length', [("a b c d", "4"), ("hi", "1")],
                    hints=["length gives the number of elements."]),
                _fix("tscourse-w6-b-fix", "Fix the index",
                     "This should print the FIRST number but prints the second. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[1]);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconsole.log(nums[0]);\n',
                     [("3 5 7", "3")],
                     hints=["Index 1 is the second element.",
                            "The first element is index 0."]),
            ],
        ),
        _lesson(
            "w6-iterate", "Iterating & accumulating",
            "Walk an array with for...of.",
            """
Sum the array [1,2,3,4]:

| step | x | sum after |
|------|---|-----------|
| 1    | 1 | 1         |
| 2    | 2 | 3         |
| 3    | 3 | 6         |
| 4    | 4 | 10        |

```ts
let sum = 0;
for (const x of [1, 2, 3, 4]) sum = sum + x;
console.log(sum);   // 10
```
""",
            warmup=[
                _q("Summing [2,2,2] with a for...of accumulator gives…",
                   ["2", "6", "3", "222"], 1, "2+2+2 = 6."),
            ],
            exercises=[
                _ex("tscourse-w6-it-1", "Sum the list",
                    "Add every number and print the total.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 0;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                    'sum = sum + x;', [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Add each x to the running sum."]),
                _ex("tscourse-w6-it-2", "Largest",
                    "Track and print the largest number in the list.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet best = nums[0];\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                    'x > best', [("3 9 2 7", "9"), ("4", "4")],
                    hints=["Replace best whenever x is bigger."]),
                _fix("tscourse-w6-it-fix", "Fix the sum start",
                     "This sum is always one too big. Fix it so sum(1 2 3)=6.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 1;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nlet sum = 0;\nfor (const x of nums) {\n  sum = sum + x;\n}\nconsole.log(sum);\n',
                     [("1 2 3", "6")],
                     hints=["A running sum must start at 0, not 1."]),
            ],
        ),
        _lesson(
            "w6-methods", "map & filter",
            "Transform and select.",
            """
- `map` makes a new array by transforming each element.
- `filter` keeps only elements that pass a test.
- `join` glues an array into a string.

```ts
const nums = [1, 2, 3];
nums.map((x) => x * 2).join(" ")     // "2 4 6"
nums.filter((x) => x % 2 === 1).length // 2
```

> ⚠️ **Common mistakes:** forgetting `map`/`filter` return a NEW array (they
> don't change the original), and forgetting to `return`/produce a value in the callback.
""",
            warmup=[
                _q("`[1,2,3,4].filter((x)=>x%2===0)` is…",
                   ["[1,3]", "[2,4]", "[1,2,3,4]", "2"], 1, "Keeps the even numbers."),
            ],
            exercises=[
                _ex("tscourse-w6-m-1", "Count evens",
                    "Keep the even numbers and print how many there are.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                    'x % 2 === 0', [("1 2 3 4 5 6", "3"), ("1 3 5", "0")],
                    hints=["Even means remainder 0 mod 2."]),
                _ex("tscourse-w6-m-2", "Double them",
                    "Double every number and print them space-separated.",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst doubled = nums.map((x) => x * 2);\nconsole.log(doubled.join(" "));\n',
                    'x * 2', [("1 2 3", "2 4 6"), ("10", "20")],
                    hints=["map transforms each x to x * 2."]),
                _fix("tscourse-w6-m-fix", "Fix filter vs map",
                     "This should COUNT the evens, but it doubles instead. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.map((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\nconst evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     [("1 2 3 4 5 6", "3")],
                     hints=["map keeps every element (so length never changes).",
                            "To keep only some elements, use filter."],
                     difficulty="Medium"),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #6 — month stats",
        """
Read a line of expense **amounts** and print three stats:

```
total 14
biggest 5
count 5
```

for input `3 1 4 1 5`.
""",
        _ch("tscourse-w6-capstone", "Budget Buddy #6", "Easy",
            "Compute total and the biggest in one pass, then print the report.",
            _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
            'let total = 0;\nlet biggest = nums[0];\nfor (const x of nums) {\n  total = total + x;\n  if (x > biggest) {\n    biggest = x;\n  }\n}\n'
            'console.log(`total ${total}`);\nconsole.log(`biggest ${biggest}`);\nconsole.log(`count ${nums.length}`);\n',
            'let total = 0;\nlet biggest = nums[0];\nfor (const x of nums) {\n  total = total + x;\n  if (x > biggest) {\n    biggest = x;\n  }\n}\n'
            'console.log(`total ${total}`);\nconsole.log(`biggest ${biggest}`);\nconsole.log(`count ${nums.length}`);',
            [("3 1 4 1 5", "total 14\nbiggest 5\ncount 5"), ("10", "total 10\nbiggest 10\ncount 1")],
            hints=["Start biggest at nums[0].",
                   "Update total and biggest together in one loop.",
                   "count is nums.length."]),
        example_io="total 14\nbiggest 5\ncount 5",
        rubric=["Prints total, biggest and count",
                "Computes total and biggest in a single loop",
                "biggest starts from the first element"],
        stretch=_ch("tscourse-w6-capstone-stretch", "Budget Buddy #6 (stretch)", "Medium",
                    "Also print `average <avg>` where avg = total / count (a decimal is fine).",
                    _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                    'let total = 0;\nfor (const x of nums) {\n  total = total + x;\n}\n'
                    'console.log(`total ${total}`);\nconsole.log(`count ${nums.length}`);\nconsole.log(`average ${total / nums.length}`);\n',
                    'let total = 0;\nfor (const x of nums) {\n  total = total + x;\n}\n'
                    'console.log(`total ${total}`);\nconsole.log(`count ${nums.length}`);\nconsole.log(`average ${total / nums.length}`);',
                    [("2 4 6", "total 12\ncount 3\naverage 4"), ("10", "total 10\ncount 1\naverage 10")],
                    hints=["average is total divided by the count.",
                           "Use total / nums.length."]),
    ),
))

# --- Week 7 ---------------------------------------------------------------
_WEEKS.append(_week(
    7, 2, _M2,
    "Objects",
    "Model structured data with objects, and combine them with arrays.",
    """
An **object** groups related values under named keys — perfect for a 'thing'
like an expense or a user. This week: object literals, reading and updating
properties, and arrays of objects (the shape of most real data).

```ts
const user = { name: "Ada", age: 36 };
user.name          // Ada
user.age = user.age + 1;
```
""",
    objectives=[
        "Create objects and read properties with dot access",
        "Update a property on an object",
        "Pass objects into functions",
        "Loop over an array of objects and reach into each one",
    ],
    why="Objects model the real world — a product, a user, an expense — as one tidy bundle of fields.",
    est_minutes=45,
    glossary=[
        _gloss("object", "A bundle of named values (keys) — { name: \"Ada\" }."),
        _gloss("property / key", "A named slot on an object."),
        _gloss("dot access", "Reaching a property: obj.name."),
        _gloss("array of objects", "A list where each item is an object — the shape of most data."),
    ],
    cheatsheet="""
```ts
const p = { name: "Ada", age: 36 };
p.name           // "Ada"
p.age = p.age + 1;  // update
const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];
for (const q of people) total = total + q.age;
people.filter((q) => q.age >= 21)
```
""",
    self_check=[
        "Can you read and update a property on an object?",
        "Can you write a function that takes an object and returns a field?",
        "Can you total a field across an array of objects?",
    ],
    review=[
        _q("How do you read the `name` of `user`?",
           ["user[name]", "user->name", "user.name", "name(user)"], 2,
           "Dot notation: user.name."),
        _q("An object is best for…",
           ["an ordered list", "grouping related values under keys",
            "repeating an action", "comparing numbers"], 1,
           "Objects bundle related fields."),
        _q("`[{a:1},{a:2}].filter((o)=>o.a>1).length` is…",
           ["0", "1", "2", "error"], 1, "Only {a:2} passes."),
    ],
    milestone="Budget Buddy now models each expense as a proper record.",
    lessons=[
        _lesson(
            "w7-basics", "Object basics",
            "Keys, values, and dot access.",
            """
```ts
const point = { x: 3, y: 4 };
point.x            // 3
point.y = point.y + 1;   // 5
```

> ⚠️ **Common mistakes:** using `[]` with a bare word (`obj[name]` looks up a
> *variable* name); for a known key, use dot access `obj.name`.
""",
            warmup=[
                _q("`const u = { age: 5 }; console.log(u.age);` prints…",
                   ["age", "5", "u.age", "undefined"], 1, "It reads the property value 5."),
            ],
            exercises=[
                _ex("tscourse-w7-b-1", "Read a property", "Print the user's name.",
                    'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                    'user.name', [("", "Ada")],
                    hints=["Access it with user.name."]),
                _ex("tscourse-w7-b-2", "Update a property",
                    "Add 5 to counter.value, then print it.",
                    'const counter = { value: 0 };\ncounter.value = counter.value + 5;\nconsole.log(counter.value);\n',
                    'counter.value + 5', [("", "5")],
                    hints=["Read the current value and add 5."]),
                _fix("tscourse-w7-b-fix", "Fix the property name",
                     "This should print the name but prints undefined. Fix the property.",
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.username);\n',
                     'const user = { name: "Ada", age: 36 };\nconsole.log(user.name);\n',
                     [("", "Ada")],
                     hints=["There is no `username` key on this object.",
                            "The key is `name`."]),
            ],
        ),
        _lesson(
            "w7-funcs", "Objects & functions",
            "Passing objects around.",
            """
Functions can take and return objects.

```ts
function fullName(p: { first: string; last: string }): string {
  return `${p.first} ${p.last}`;
}
fullName({ first: "Ada", last: "Lovelace" });   // Ada Lovelace
```
""",
            warmup=[
                _q("`fullName({first:\"A\", last:\"B\"})` above returns…",
                   ["A", "B", "A B", "AB"], 2, "Template joins them with a space."),
            ],
            exercises=[
                _ex("tscourse-w7-f-1", "Full name",
                    "Return the first and last name joined by a space.",
                    'function fullName(p: { first: string; last: string }): string {\n  return `${p.first} ${p.last}`;\n}\nconsole.log(fullName({ first: "Ada", last: "Lovelace" }));\n',
                    '`${p.first} ${p.last}`', [("", "Ada Lovelace")],
                    hints=["Template literal with p.first and p.last."]),
                _ex("tscourse-w7-f-2", "Build from input",
                    "Store a greeting on the object, then print it.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\nconst user = { name: name, greeting: `Hi ${name}` };\nconsole.log(user.greeting);\n',
                    '`Hi ${name}`', [("Sam", "Hi Sam"), ("Ada", "Hi Ada")],
                    hints=["The greeting is a template literal using name."]),
                _fix("tscourse-w7-f-fix", "Fix the field access",
                     "This should print the first name but reads the wrong field. Fix it.",
                     'function first(p: { first: string; last: string }): string {\n  return p.last;\n}\nconsole.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     'function first(p: { first: string; last: string }): string {\n  return p.first;\n}\nconsole.log(first({ first: "Ada", last: "Lovelace" }));\n',
                     [("", "Ada")],
                     hints=["It returns p.last but should return the first name.",
                            "Return p.first."]),
            ],
        ),
        _lesson(
            "w7-arrays", "Arrays of objects",
            "The shape of real datasets.",
            """
Most data is a list of records. Loop over it and reach into each one.

```ts
const people = [{ name: "Ada", age: 36 }, { name: "Bo", age: 20 }];
let total = 0;
for (const p of people) total = total + p.age;
console.log(total);   // 56
```
""",
            warmup=[
                _q("Totalling `age` over [{age:1},{age:2},{age:3}] gives…",
                   ["3", "6", "123", "error"], 1, "1+2+3 = 6."),
            ],
            exercises=[
                _ex("tscourse-w7-a-1", "Total ages",
                    "Sum everyone's age and print it.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.age;\n}\nconsole.log(total);\n',
                    'total + p.age', [("", "56")],
                    hints=["Add each person's age to total."]),
                _ex("tscourse-w7-a-2", "Count adults",
                    "Count people aged 21 or older and print the count.",
                    'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nconst adults = people.filter((p) => p.age >= 21);\nconsole.log(adults.length);\n',
                    'p.age >= 21', [("", "1")],
                    hints=["Keep people whose age is at least 21."]),
                _fix("tscourse-w7-a-fix", "Fix the field in the loop",
                     "This should total ages but totals nothing sensible. Fix the field it reads.",
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.years;\n}\nconsole.log(total);\n',
                     'const people = [\n  { name: "Ada", age: 36 },\n  { name: "Bo", age: 20 },\n];\nlet total = 0;\nfor (const p of people) {\n  total = total + p.age;\n}\nconsole.log(total);\n',
                     [("", "56")],
                     hints=["There is no `years` field — it's `age`.",
                            "Read p.age."]),
            ],
        ),
    ],
    capstone=_cap_brief(
        "Budget Buddy #7 — model your expenses (free build)",
        """
A **free-build** project — no auto-grader. In the editor, model Budget Buddy's data:

1. Represent each expense as an object with `desc`, `amount`, and `paid` (a boolean).
2. Put several expenses in an array.
3. Write a function that takes the array and prints a report: the number of
   expenses, the total amount, and the descriptions of the unpaid ones.

Use everything from Weeks 1–7: variables, loops, functions, arrays, objects.
When you're happy with the output, click **Mark done**. A reference solution is
below if you want to compare.
""",
        reference="""
const expenses = [
  { desc: "coffee", amount: 3, paid: true },
  { desc: "book", amount: 12, paid: false },
  { desc: "lunch", amount: 9, paid: false },
];
function report(items) {
  let total = 0;
  for (const e of items) total = total + e.amount;
  console.log(`Expenses: ${items.length}`);
  console.log(`Total: $${total}`);
  const unpaid = items.filter((e) => !e.paid).map((e) => e.desc);
  console.log(`Unpaid: ${unpaid.join(", ")}`);
}
report(expenses);
""",
        rubric=["Each expense is an object with desc, amount, paid",
                "A function takes the array and prints a report",
                "The report includes the count, the total, and the unpaid descriptions"],
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

Types are erased before the program runs, so the drills still exercise runtime
logic — the annotations describe it.
""",
    objectives=[
        "Write type annotations on values and functions",
        "Name a shape with interface or type",
        "Annotate an array of records (Item[])",
        "Fold a list to one value with reduce",
    ],
    why="Types catch whole classes of bugs before the program ever runs — the reason TypeScript exists.",
    est_minutes=50,
    glossary=[
        _gloss("annotation", "A written type after a colon: let n: number."),
        _gloss("inference", "TypeScript working out a type for you."),
        _gloss("interface", "A name for the shape of an object type."),
        _gloss("type alias", "Another way to name a type: type User = {...}."),
        _gloss(".reduce(f, start)", "Folds a list into a single accumulated value."),
    ],
    cheatsheet="""
```ts
const price: number = 10;
function repeat(s: string, n: number): string { return s.repeat(n); }
interface Point { x: number; y: number; }
type User = { name: string; admin: boolean };
const items: Item[] = [...];
items.reduce((sum, it) => sum + it.price, 0)   // fold to one number
```
""",
    self_check=[
        "Can you annotate a function's parameters and return type?",
        "Can you name an object shape with interface and use it?",
        "Can you total a field over a typed array with reduce?",
    ],
    review=[
        _q("What happens to type annotations at runtime?",
           ["they slow it down", "they're erased (compile-time only)",
            "they become comments", "they print"], 1,
           "Types guide you and the compiler, then vanish before running."),
        _q("`interface` names…",
           ["a running object", "the shape of an object type", "a loop", "an input"], 1,
           "It names a reusable object shape."),
        _q("`[1,2,3].reduce((s,x)=>s+x, 0)` is…", ["0", "6", "123", "3"], 1,
           "It folds to the sum, 6."),
    ],
    milestone="Budget Buddy is now fully typed — the compiler guards its data. You've finished Month 2!",
    lessons=[
        _lesson(
            "w8-annotations", "Annotations & inference",
            "Writing types on values and functions.",
            """
```ts
const price: number = 10;
function repeat(s: string, n: number): string {
  return s.repeat(n);
}
```

Often you can omit annotations and let TypeScript **infer** them — but writing
them on function parameters and returns is good practice.

> ⚠️ **Common mistakes:** thinking annotations change runtime behaviour — they
> don't; they're checked, then stripped.
""",
            warmup=[
                _q('`"ab".repeat(3)` is…', ["ababab", "ab3", "6", "aaabbb"], 0,
                   "repeat concatenates 3 copies."),
            ],
            exercises=[
                _ex("tscourse-w8-an-1", "Typed total",
                    "Compute price * qty into the annotated total.",
                    'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price * qty;\nconsole.log(total);\n',
                    'price * qty', [("", "30")],
                    hints=["Multiply the two annotated numbers."]),
                _ex("tscourse-w8-an-2", "Typed repeat",
                    "Return the string repeated n times.",
                    'function repeat(s: string, n: number): string {\n  return s.repeat(n);\n}\nconsole.log(repeat("ab", 3));\n',
                    's.repeat(n)', [("", "ababab")],
                    hints=["Strings have a .repeat(n) method."]),
                _fix("tscourse-w8-an-fix", "Fix the annotation mismatch",
                     "This should print 30, but a wrong operator sneaks in. Fix it.",
                     'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price + qty;\nconsole.log(total);\n',
                     'const price: number = 10;\nconst qty: number = 3;\nconst total: number = price * qty;\nconsole.log(total);\n',
                     [("", "30")],
                     hints=["price + qty is 13, not 30.",
                            "A total of items uses multiplication."]),
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

`Math.abs(n)` is the distance of n from zero.
""",
            warmup=[
                _q("`Math.abs(-4)` is…", ["-4", "4", "0", "error"], 1,
                   "abs gives the magnitude, 4."),
            ],
            exercises=[
                _ex("tscourse-w8-if-1", "Manhattan distance",
                    "Return |p.x| + |p.y| using Math.abs.",
                    'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                    'Math.abs(p.x) + Math.abs(p.y)', [("", "7")],
                    hints=["Add the absolute values of x and y."]),
                _ex("tscourse-w8-if-2", "Labelled user",
                    "Return `<name> (admin)` when admin is true, else just the name.",
                    'type User = { name: string; admin: boolean };\nfunction label(u: User): string {\n  return u.admin ? `${u.name} (admin)` : u.name;\n}\nconsole.log(label({ name: "Ada", admin: true }));\n',
                    'u.admin ? `${u.name} (admin)` : u.name', [("", "Ada (admin)")],
                    hints=["A ternary cond ? a : b picks a when cond is true."]),
                _fix("tscourse-w8-if-fix", "Fix the distance",
                     "Negative coordinates break this. Fix it so dist({x:3,y:-4}) is 7.",
                     'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return p.x + p.y;\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                     'interface Point {\n  x: number;\n  y: number;\n}\nfunction dist(p: Point): number {\n  return Math.abs(p.x) + Math.abs(p.y);\n}\nconsole.log(dist({ x: 3, y: -4 }));\n',
                     [("", "7")],
                     hints=["3 + (-4) is -1, not a distance.",
                            "Wrap each coordinate in Math.abs."]),
            ],
        ),
        _lesson(
            "w8-typed-arrays", "Typed arrays & reduce",
            "Interfaces over lists, folded with reduce.",
            """
Annotate an array of records with `Item[]`, and fold it with `reduce`:

```ts
interface Item { name: string; price: number; }
const items: Item[] = [{ name: "A", price: 4 }, { name: "B", price: 6 }];
const total = items.reduce((sum, it) => sum + it.price, 0);   // 10
```

`reduce` carries an accumulator (`sum`, starting at 0) across the list.
""",
            warmup=[
                _q("`[2,3,5].reduce((s,x)=>s+x, 0)` is…", ["0", "10", "235", "3"], 1,
                   "Folds to the sum, 10."),
            ],
            exercises=[
                _ex("tscourse-w8-ta-1", "Total price",
                    "Reduce the items to the sum of their prices.",
                    'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 0);\nconsole.log(total);\n',
                    'sum + it.price', [("", "10")],
                    hints=["Each step adds it.price to the running sum."]),
                _fix("tscourse-w8-ta-fix", "Fix the reduce start",
                     "The total is one too high — the seed is wrong. Fix it to 10.",
                     'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 1);\nconsole.log(total);\n',
                     'interface Item {\n  name: string;\n  price: number;\n}\nconst items: Item[] = [\n  { name: "A", price: 4 },\n  { name: "B", price: 6 },\n];\nconst total = items.reduce((sum, it) => sum + it.price, 0);\nconsole.log(total);\n',
                     [("", "10")],
                     hints=["The reduce seed (last argument) starts the sum.",
                            "A sum should seed at 0, not 1."]),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #8 — typed report",
        """
Bring it home: model expenses with an `interface`, then report on them. Given
three expenses, print:

```
Count: 3
Total: $24
Unpaid: book, lunch
```
""",
        _ch("tscourse-w8-capstone", "Budget Buddy #8", "Medium",
            "Use filter, map, join, reduce and .length over a typed array of records.",
            'interface Expense {\n  desc: string;\n  amount: number;\n  paid: boolean;\n}\n'
            'const expenses: Expense[] = [\n  { desc: "coffee", amount: 3, paid: true },\n  { desc: "book", amount: 12, paid: false },\n  { desc: "lunch", amount: 9, paid: false },\n];\n'
            'const total = expenses.reduce((sum, e) => sum + e.amount, 0);\n'
            'const unpaid = expenses.filter((e) => !e.paid).map((e) => e.desc);\n'
            'console.log(`Count: ${expenses.length}`);\nconsole.log(`Total: $${total}`);\nconsole.log(`Unpaid: ${unpaid.join(", ")}`);\n',
            'const total = expenses.reduce((sum, e) => sum + e.amount, 0);\n'
            'const unpaid = expenses.filter((e) => !e.paid).map((e) => e.desc);\n'
            'console.log(`Count: ${expenses.length}`);\nconsole.log(`Total: $${total}`);\nconsole.log(`Unpaid: ${unpaid.join(", ")}`);',
            [("", "Count: 3\nTotal: $24\nUnpaid: book, lunch")],
            hints=["reduce sums the amounts (seed 0).",
                   "Filter to unpaid, then map to descriptions.",
                   'Join the unpaid descriptions with ", ".']),
        example_io="Count: 3\nTotal: $24\nUnpaid: book, lunch",
        rubric=["expenses is typed as Expense[]",
                "Total uses reduce; count uses .length",
                "Unpaid list uses filter + map + join"],
    ),
))

# ===========================================================================
# MONTHS 3-8 — themed skeletons (authored in later batches).
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


# ===========================================================================
# CONCEPT-SCOPE LINT — enforce "never require concepts beyond this week".
# For each authored week, scan every program (drills/fixes/challenges/capstone/
# stretch) for tokens that belong to a LATER week. Fails generation if violated.
# ===========================================================================
def _all_programs(week):
    out = []
    for l in week["lessons"]:
        for ex in l["exercises"]:
            out.append((ex["id"], ex["solution"]))
            out.append((ex["id"] + ":starter", ex["starter"]))
    cap = week.get("capstone")
    if cap:
        for ex in (cap.get("exercise"), cap.get("stretch")):
            if ex:
                out.append((ex["id"], ex["solution"]))
        if cap.get("reference"):
            out.append((cap["title"] + ":ref", cap["reference"]))
    return out


# (token substring, first week it's allowed). A program in a week EARLIER than
# the listed week must not contain the token.
_SCOPE_RULES = [
    ("while (", 4), ("for (", 4),          # loops
    ("=> ", 5), ("function ", 5),          # functions
    (".map(", 6), (".filter(", 6),
    (".split(", 6), (".join(", 6),         # array methods
    (".reduce(", 8),                        # reduce
    ("interface ", 8), ("type ", 8),        # named types (annotations OK earlier)
]


def _lint_scope(weeks):
    problems = []
    for w in weeks:
        if not w.get("authored"):
            continue
        wn = w["number"]
        for pid, prog in _all_programs(w):
            for token, allowed_from in _SCOPE_RULES:
                if wn < allowed_from and token in prog:
                    problems.append(
                        f"Week {wn} program {pid} uses {token!r} (not introduced until week {allowed_from})"
                    )
    if problems:
        raise AssertionError("TS course scope violations:\n  " + "\n  ".join(problems))


_lint_scope(_WEEKS)


TS_COURSE = {
    "key": "typescript",
    "title": "TypeScript: Zero to Interview",
    "subtitle": (
        "An 8-month, week-by-week course from your very first line of code to "
        "interview-ready — DSA solved in TypeScript and deep type-system mastery. "
        "Every week has a goal, lessons that never outrun what you've learned, "
        "warm-ups, hint ladders, a glossary, a cheat sheet, and a growing "
        "capstone project (Budget Buddy)."
    ),
    "weeks": _WEEKS,
}
