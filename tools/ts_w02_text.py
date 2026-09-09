# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 2 — text & input.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 2 ---------------------------------------------------------------
_WEEKS.append(_week(
    2, 1, _M1,
    "Text & Input",
    "Read what the user types and reshape it: measure it, search it, slice it, pad it, and turn it into a number.",
    """
Last week your programs always printed the same thing. This week they **react**.
Almost every program from here on starts the same way:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
```

That reads everything the user typed as one string, and `.trim()` shaves off the
newline they pressed at the end.

The rest of the week is the **string toolbox** — the handful of operations you'll
use for the rest of your life: measuring, indexing, changing case, searching,
slicing, padding, replacing, and converting text to numbers. None of them is
hard on its own. The skill is knowing which one to reach for, which comes from
using each of them a dozen times. That's what this week is.

⏱️ Budget about **six hours**, spread over several sittings.
""",
    objectives=[
        "Read a line of input and trim it",
        "Measure a string with .length and reach individual characters with s[i]",
        "Normalise case with toUpperCase / toLowerCase and compare case-insensitively",
        "Search text with includes, startsWith, endsWith and indexOf",
        "Extract parts with slice, including from the end with negative indices",
        "Pad, repeat and replace text to produce neatly aligned output",
        "Convert text to numbers with Number and parseInt, and spot NaN",
    ],
    why="Every real program has an edge where text comes in — a form field, a filename, a command, a CSV cell. Cleaning and interrogating that text is a daily job, not a beginner exercise.",
    est_minutes=350,
    glossary=[
        _gloss("standard input", "The stream of text a program reads — here, whatever the user types."),
        _gloss("fs.readFileSync(0, \"utf8\")", "Reads all of standard input as one string. The 0 means 'the input stream'."),
        _gloss(".trim()", "Returns a copy with whitespace removed from both ends."),
        _gloss("property", "A value attached to a value, read without parentheses: s.length."),
        _gloss("method", "A function attached to a value, called with parentheses: s.toUpperCase()."),
        _gloss("index", "A character's position, counting from 0. In \"cat\", 'c' is index 0."),
        _gloss("zero-based", "Counting starts at 0, so the last index is length - 1."),
        _gloss("immutable", "Strings never change in place. Every string method returns a NEW string."),
        _gloss(".includes(x)", "true when x appears anywhere inside."),
        _gloss(".indexOf(x)", "The index where x starts, or -1 when it is absent."),
        _gloss(".slice(a, b)", "The characters from index a up to but NOT including b."),
        _gloss(".padStart(n, c)", "Pads the front with c until the string is n characters long."),
        _gloss(".replaceAll(a, b)", "Every occurrence of a swapped for b."),
        _gloss("Number(x)", "Converts a whole string to a number, or NaN if it isn't one."),
        _gloss("parseInt(x)", "Reads a leading whole number, ignoring trailing text: parseInt(\"12kg\") is 12."),
        _gloss("NaN", "'Not a Number' — the result of a failed numeric conversion. It equals nothing, not even itself."),
    ],
    cheatsheet="""
```ts
import * as fs from "fs";
const s = fs.readFileSync(0, "utf8").trim();   // read + clean input

// ---- measure & index ------------------------------------------------
s.length              // 5 for "hello"   (a property: no parentheses)
s[0]                  // "h"   first character
s[s.length - 1]       // "o"   last character
s.at(-1)              // "o"   same thing, counting from the end

// ---- case -----------------------------------------------------------
s.toUpperCase()       // "HELLO"
s.toLowerCase()       // "hello"
a.toLowerCase() === b.toLowerCase()    // case-insensitive comparison

// ---- search ---------------------------------------------------------
s.includes("ell")     // true
s.startsWith("he")    // true
s.endsWith("lo")      // true
s.indexOf("l")        // 2    first position, or -1 if absent
s.lastIndexOf("l")    // 3

// ---- extract --------------------------------------------------------
s.slice(0, 3)         // "hel"   from 0 up to (not including) 3
s.slice(2)            // "llo"   from 2 to the end
s.slice(-2)           // "lo"    last two characters

// ---- reshape --------------------------------------------------------
s.trim()              // both ends
"7".padStart(3, "0")  // "007"
"ab".padEnd(5, ".")   // "ab..."
"-".repeat(10)        // "----------"
"a-b-c".replaceAll("-", " ")   // "a b c"

// ---- text -> number -------------------------------------------------
Number("42")          // 42
Number("4.5")         // 4.5
Number("abc")         // NaN
parseInt("12kg", 10)  // 12
Number.isNaN(v)       // the safe way to test for NaN
```
""",
    self_check=[
        "Can you read a line of input and print it back unchanged?",
        "Can you print the first and last character of whatever is typed?",
        "Can you compare two words ignoring their case?",
        "Can you explain why s.slice(0, 3) gives three characters, not four?",
        "Can you right-align a number in a 6-character column?",
        "Can you turn \"42\" into 42, and say what happens with \"forty-two\"?",
    ],
    review=[
        _q("Why call `.trim()` on the input?",
           ["To uppercase it", "To remove the trailing newline and stray spaces",
            "To convert it to a number", "It is optional and pointless"], 1,
           "The user pressed Enter, so the raw input ends in a newline."),
        _q("`\"hello\".length` is…", ["a method call", "5", '"5"', "an error"], 1,
           "length is a property whose value is the number 5."),
        _q('What is `"cat"[1]`?', ['"c"', '"a"', '"t"', "1"], 1,
           "Indexing is zero-based, so index 1 is the second character."),
        _q('What is `"hello".slice(1, 3)`?', ['"ell"', '"el"', '"he"', '"hel"'], 1,
           "From index 1 up to but not including 3: characters 1 and 2."),
        _q('What does `"Hello".indexOf("z")` return?', ["0", "-1", "undefined", "an error"], 1,
           "-1 is the 'not found' answer — remember it, it catches everyone once."),
        _q('`"7".padStart(3, "0")` gives…', ['"700"', '"007"', '"7  "', '"7"'], 1,
           "padStart adds to the FRONT until the target length is reached."),
        _q('`Number("12kg")` gives…', ["12", "NaN", '"12"', "0"], 1,
           'Number needs the WHOLE string to be numeric. parseInt("12kg", 10) gives 12.'),
        _q("Which correctly tests that `v` failed to convert?",
           ["v === NaN", "v == NaN", "Number.isNaN(v)", "v === \"NaN\""], 2,
           "NaN is not equal to anything, including itself — always use Number.isNaN."),
        _q('After `const t = s.toUpperCase();`, what has happened to `s`?',
           ["It is now uppercase", "It is unchanged", "It is empty", "It is a number"], 1,
           "Strings are immutable; methods return a new string and leave the original alone."),
        _q("How do you compare two names ignoring case?",
           ["a === b", "a.toLowerCase() === b.toLowerCase()", "a.includes(b)",
            "a.length === b.length"], 1,
           "Normalise both sides to the same case first."),
    ],
    milestone="Budget Buddy can now take a messy, hand-typed expense line and print a clean, aligned entry from it.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w2-input", "Reading input",
            "Getting whatever the user types into a variable.",
            """
Your programs get their input from **standard input** — the text piped into them
when they run. Two lines do the job:

```ts
import * as fs from "fs";
const input = fs.readFileSync(0, "utf8").trim();
console.log(input);
```

Reading it piece by piece:

| piece | meaning |
|---|---|
| `import * as fs from "fs"` | bring in the file-system toolbox |
| `readFileSync(0, "utf8")` | read stream number 0 — standard input — as text |
| `.trim()` | drop whitespace from both ends |

**Why `.trim()` matters.** The user pressed Enter, so the raw input is
`"hello\\n"`. Without trimming, `input.length` would be 6, not 5, and comparing
it to `"hello"` would fail — for a reason you cannot see on screen. Trimming
first removes a whole class of baffling bugs.

**`.trim()` returns a new string.** Strings are **immutable** — nothing you call
on a string ever modifies it. `s.trim()` hands you a cleaned copy; `s` is
untouched unless you assign the result somewhere.

The `import` line goes at the very top, once. From here on, exercises that need
input already have it.

> ⚠️ **Common mistakes:** forgetting `.trim()`, so your output has a stray blank
> line or your comparison mysteriously fails; forgetting the `import` line; and
> writing `readFileSync("0")` — the 0 is a number, not text.
""",
            warmup=[
                _q("If the user types `cat` and the program does `console.log(input)`, the output is…",
                   ["cat", '"cat"', "input", "3"], 0, "It echoes the text."),
                _q('Without .trim(), what is the length of the input when the user types `hi` and presses Enter?',
                   ["1", "2", "3", "0"], 2, 'It is "hi\\n" — two letters plus the newline.'),
                _q("After `const t = s.trim();`, what is `s`?",
                   ["Trimmed", "Unchanged", "Empty", "undefined"], 1,
                   "trim returns a copy; the original is untouched."),
            ],
            exercises=[
                _ex("tscourse-w2-input-1", "Echo the input",
                    "Read the whole input, trimmed, and print it back.",
                    _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(input);\n',
                    'fs.readFileSync(0, "utf8").trim()',
                    [("hello\n", "hello"), ("  spaced  ", "spaced")],
                    hints=['readFileSync(0, "utf8") reads standard input.',
                           "Chain .trim() onto it to drop surrounding whitespace."]),
                _ex("tscourse-w2-input-2", "Greet the input",
                    "Read a name and print `Hello, <name>!` using a template literal.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`Hello, ${name}!`);\n',
                    '`Hello, ${name}!`',
                    [("Ada", "Hello, Ada!"), ("Bo", "Hello, Bo!")],
                    hints=["Backticks and one hole.",
                           "Write `Hello, ${name}!`."]),
                _ex("tscourse-w2-input-3", "Say it twice",
                    "Print the input twice on one line, separated by a single space.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`${s} ${s}`);\n',
                    '`${s} ${s}`',
                    [("hi", "hi hi"), ("ok", "ok ok")],
                    hints=["One template literal with two holes.",
                           "Write `${s} ${s}` — the space between them is literal."]),
                _ex("tscourse-w2-input-4", "Quote the input",
                    'Print the input wrapped in square brackets, e.g. `[hi]`.',
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`[${s}]`);\n',
                    '`[${s}]`',
                    [("hi", "[hi]"), ("  pad  ", "[pad]")],
                    hints=["Brackets are ordinary characters in a template.",
                           "Write `[${s}]` — the trim already removed the padding."]),
                _fix("tscourse-w2-input-fix1", "Fix the echo",
                     "This should echo what the user typed, but it prints a fixed word. Fix it.",
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log("input");\n',
                     _FS + 'const input = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(input);\n',
                     [("hello", "hello"), ("bo", "bo")],
                     hints=['It prints the literal word "input" rather than the value.',
                            "Log the variable — no quotes."]),
                _fix("tscourse-w2-input-fix2", "Fix the untrimmed length",
                     "This should print the number of characters typed, but the newline is being counted. Fix it so `hi` prints 2.",
                     _FS + 'const s = fs.readFileSync(0, "utf8");\n'
                     'console.log(s.length);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length);\n',
                     [("hi\n", "2"), ("hello\n", "5")],
                     hints=["The trailing newline is a character too.",
                            "Add .trim() when reading."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What does the 0 in readFileSync(0, \"utf8\") mean?",
                   ["Read zero bytes", "Standard input", "The first file", "An error code"], 1,
                   "0 is the standard-input stream."),
                _q("Strings in TypeScript are…",
                   ["mutable — methods change them in place",
                    "immutable — methods return new strings", "numbers", "always uppercase"], 1,
                   "Immutable. This is why you must assign the result of s.trim()."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w2-inspect", "Measuring & indexing",
            "How long is it, and what is the character at position i?",
            """
**Length** is a *property* — no parentheses:

```ts
"hello".length     // 5
"".length          // 0
```

**Indexing** reaches one character. Positions start at **0**:

```
 "h"  "e"  "l"  "l"  "o"
  0    1    2    3    4
```

```ts
const s = "hello";
s[0]                // "h"   first
s[4]                // "o"   fifth
s[s.length - 1]     // "o"   LAST — length is 5, last index is 4
s[99]               // undefined  (no error, just nothing)
```

That `length - 1` is worth burning in: a 5-character string has indices 0 to 4.
Reaching for `s[s.length]` gets you `undefined`, which then quietly poisons
everything downstream. This is the famous **off-by-one**, and you will meet it
again in loops next week.

`.at()` is a friendlier way to count from the end:

```ts
s.at(-1)    // "o"   last
s.at(-2)    // "l"   second from last
```

A single character is itself a string of length 1 — there's no separate
character type, so everything you know about strings applies to it.

> ⚠️ **Common mistakes:** writing `s.length()` (it's a property, so no
> parentheses); using `s[s.length]` instead of `s[s.length - 1]`; and forgetting
> that an empty input makes every index `undefined`.
""",
            warmup=[
                _q('What is `"cat".length`?', ["cat", "2", "3", '"3"'], 2, "Three characters."),
                _q('What is `"cat"[0]`?', ['"c"', '"a"', "0", "undefined"], 0, "Index 0 is the first."),
                _q('What is `"cat"[3]`?', ['"t"', '""', "undefined", "an error"], 2,
                   "The valid indices are 0, 1, 2. Index 3 is past the end."),
                _q('Which reliably gives the LAST character of `s`?',
                   ["s[s.length]", "s[s.length - 1]", "s[-1]", "s.last()"], 1,
                   "s[-1] is undefined in TypeScript — use s[s.length - 1] or s.at(-1)."),
            ],
            exercises=[
                _ex("tscourse-w2-idx-1", "Count the characters",
                    "Print how many characters the input has.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.length);\n',
                    's.length',
                    [("hello", "5"), ("hi", "2")],
                    hints=["length is a property — no parentheses."]),
                _ex("tscourse-w2-idx-2", "First character",
                    "Print the first character of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[0]);\n',
                    's[0]',
                    [("hello", "h"), ("Ada", "A")],
                    hints=["Positions start at 0.", "Write s[0]."]),
                _ex("tscourse-w2-idx-3", "Last character",
                    "Print the last character of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[s.length - 1]);\n',
                    's[s.length - 1]',
                    [("hello", "o"), ("Ada", "a"), ("x", "x")],
                    hints=["The last index is one less than the length.",
                           "Write s[s.length - 1]."]),
                _ex("tscourse-w2-idx-4", "First and last, together",
                    "Print the first and last character joined, e.g. `hello` → `ho`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(`${s[0]}${s.at(-1)}`);\n',
                    '`${s[0]}${s.at(-1)}`',
                    [("hello", "ho"), ("ab", "ab")],
                    hints=["Two holes, no separator between them.",
                           "Write `${s[0]}${s.at(-1)}` — or use s[s.length - 1] for the last."]),
                _ex("tscourse-w2-idx-5", "Middle character",
                    "The input always has an odd length. Print its middle character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s[Math.floor(s.length / 2)]);\n',
                    'Math.floor(s.length / 2)',
                    [("abc", "b"), ("hello", "l"), ("x", "x")],
                    hints=['For "abc" the middle index is 1, and 3 / 2 is 1.5.',
                           "Round the halved length down: Math.floor(s.length / 2)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-idx-fix1", "Fix the length call",
                     "This should print the length but crashes. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length());\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.length);\n',
                     [("hello", "5")],
                     hints=["length is a property, not a method.",
                            "Remove the parentheses after length."]),
                _fix("tscourse-w2-idx-fix2", "Fix the off-by-one",
                     "This should print the last character but prints nothing (undefined). Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[s.length]);\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s[s.length - 1]);\n',
                     [("hello", "o"), ("ab", "b")],
                     hints=["A 5-character string has indices 0 to 4, not 0 to 5.",
                            "Subtract one: s[s.length - 1]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("For a string of length n, the valid indices are…",
                   ["1 to n", "0 to n", "0 to n - 1", "0 to n + 1"], 2,
                   "Zero-based: 0 up to n - 1."),
                _q("`\"abc\"[5]` evaluates to…",
                   ["an error that stops the program", "undefined", '""', "c"], 1,
                   "Out-of-range indexing is silent — which is exactly what makes it dangerous."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w2-case", "Changing case",
            "Normalising text so comparisons behave.",
            """
Two methods, both returning a **new** string:

```ts
"Hello".toUpperCase()    // "HELLO"
"Hello".toLowerCase()    // "hello"
```

The real use isn't shouting — it's **normalising before you compare**. To a
computer `"YES"`, `"Yes"` and `"yes"` are three different strings. Users type
all three. So you flatten both sides first:

```ts
const answer = "YeS";
console.log(answer.toLowerCase() === "yes");   // true
```

That pattern — *normalise, then compare* — turns up constantly: matching
commands, checking a filename's extension, deduplicating names.

**Capitalising a word** combines case with indexing and slicing (slicing gets
its own lesson shortly, but here's the shape):

```ts
const w = "ada";
console.log(w[0].toUpperCase() + w.slice(1));   // "Ada"
```

Take the first character, uppercase it, and glue on everything from index 1
onward.

> ⚠️ **Common mistakes:** calling `s.toUpperCase()` and expecting `s` itself to
> change; normalising only one side of a comparison; and forgetting the
> parentheses — `s.toUpperCase` without them is the method itself, not its
> result.
""",
            warmup=[
                _q('What is `"hi".toUpperCase()`?', ["hi", "HI", "Hi", '"HI"'], 1, "Both letters uppercased."),
                _q('After `const t = s.toUpperCase();` with `s = "hi"`, what is `s`?',
                   ['"HI"', '"hi"', '""', "undefined"], 1, "Unchanged — strings are immutable."),
                _q('Is `"YES" === "yes"`?', ["true", "false"], 1,
                   "String comparison is case-sensitive; normalise first."),
            ],
            exercises=[
                _ex("tscourse-w2-case-1", "Shout it",
                    "Print the input in UPPERCASE.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toUpperCase());\n',
                    's.toUpperCase()',
                    [("hello", "HELLO"), ("Bo", "BO")],
                    hints=["Call .toUpperCase() on the string."]),
                _ex("tscourse-w2-case-2", "Whisper it",
                    "Print the input in lowercase.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toLowerCase());\n',
                    's.toLowerCase()',
                    [("HELLO", "hello"), ("MiXeD", "mixed")],
                    hints=["The mirror image of toUpperCase."]),
                _ex("tscourse-w2-case-3", "Case-insensitive yes",
                    "Print `true` when the input is any capitalisation of `yes`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.toLowerCase() === "yes");\n',
                    's.toLowerCase() === "yes"',
                    [("YES", "true"), ("Yes", "true"), ("yes", "true"), ("no", "false")],
                    hints=["Flatten the input, then compare to the lowercase word.",
                           'Write s.toLowerCase() === "yes".']),
                _ex("tscourse-w2-case-4", "Capitalise a word",
                    "Print the input with only its first letter capitalised: `ada` → `Ada`.",
                    _FS + 'const w = fs.readFileSync(0, "utf8").trim().toLowerCase();\n'
                    'console.log(w[0].toUpperCase() + w.slice(1));\n',
                    'w[0].toUpperCase() + w.slice(1)',
                    [("ada", "Ada"), ("BOB", "Bob"), ("x", "X")],
                    hints=["Uppercase the first character, then append the rest.",
                           "The rest of the word is w.slice(1)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-case-fix1", "Fix the one-sided compare",
                     "This should accept `YES` in any case, but only `yes` works. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s === "yes");\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.toLowerCase() === "yes");\n',
                     [("YES", "true"), ("Yes", "true"), ("no", "false")],
                     hints=["Only one side has been normalised — actually, neither has.",
                            "Lowercase the input before comparing."]),
                _fix("tscourse-w2-case-fix2", "Fix the ignored result",
                     "This should print the input uppercased, but prints it unchanged. Fix it.",
                     _FS + 'let s = fs.readFileSync(0, "utf8").trim();\n'
                     's.toUpperCase();\nconsole.log(s);\n',
                     _FS + 'let s = fs.readFileSync(0, "utf8").trim();\n'
                     's = s.toUpperCase();\nconsole.log(s);\n',
                     [("hi", "HI"), ("ada", "ADA")],
                     hints=["The call happens, but its result is thrown away.",
                            "Assign it back: s = s.toUpperCase();"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why normalise case before comparing?",
                   ["It is faster", "Because users type the same word many ways",
                    "It saves memory", "It is required by TypeScript"], 1,
                   "Yes / YES / yes are three different strings to a computer."),
                _q('`"ada"[0].toUpperCase()` gives…', ['"ADA"', '"A"', '"a"', "an error"], 1,
                   'Indexing first gives the one-character string "a", which uppercases to "A".'),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w2-search", "Searching inside text",
            "Does it contain, start with, end with — and where?",
            """
Four everyday questions, four methods:

```ts
const s = "budget-report.csv";

s.includes("report")     // true   — anywhere?
s.startsWith("budget")   // true   — at the front?
s.endsWith(".csv")       // true   — at the back?
s.indexOf("report")      // 7      — WHERE? (or -1)
```

The first three answer `true`/`false`. `indexOf` answers **where**, and when the
text isn't there it returns **`-1`** — not `0`, not `undefined`. `-1` is the
sentinel you have to remember, because `0` is a perfectly good answer meaning
"right at the start".

```ts
"hello".indexOf("h")    // 0   found, at the front
"hello".indexOf("z")    // -1  not found
```

`lastIndexOf` searches from the right, which is how you find a file extension:

```ts
const name = "my.report.csv";
name.lastIndexOf(".")   // 9   the final dot
```

**`indexOf` vs `includes`.** `includes` is just a friendlier way of asking
`indexOf(x) !== -1`. Prefer `includes` when you only care *whether*; use
`indexOf` when you need the position for slicing.

`startsWith` and `endsWith` also take a second argument in some forms, but the
plain version covers nearly everything: prefixes (`"http"`), suffixes
(`".csv"`), and command matching.

> ⚠️ **Common mistakes:** treating `indexOf` as truthy — `if (s.indexOf("a"))`
> is wrong, because a match at position 0 is falsy; and forgetting that all four
> are case-sensitive, so normalise first when that matters.
""",
            warmup=[
                _q('What is `"hello".includes("ell")`?', ["true", "false"], 0,
                   "It appears starting at index 1."),
                _q('What is `"hello".indexOf("l")`?', ["1", "2", "3", "-1"], 1,
                   "The FIRST l is at index 2."),
                _q('What is `"hello".indexOf("z")`?', ["0", "-1", "undefined", "5"], 1,
                   "-1 means not found."),
                _q('What is `"report.csv".endsWith(".csv")`?', ["true", "false"], 0,
                   "The string does end with that suffix."),
            ],
            exercises=[
                _ex("tscourse-w2-find-1", "Contains a word",
                    "Print whether the input contains `cat`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.includes("cat"));\n',
                    's.includes("cat")',
                    [("concatenate", "true"), ("dog", "false"), ("cat", "true")],
                    hints=["includes answers true or false.",
                           'Write s.includes("cat").']),
                _ex("tscourse-w2-find-2", "Is it a CSV?",
                    "Print whether the input filename ends with `.csv`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(name.endsWith(".csv"));\n',
                    'name.endsWith(".csv")',
                    [("report.csv", "true"), ("report.txt", "false"), ("csv", "false")],
                    hints=["endsWith checks a suffix.",
                           'Write name.endsWith(".csv").']),
                _ex("tscourse-w2-find-3", "Where is it?",
                    "Print the index where `-` first appears (or -1 if it doesn't).",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.indexOf("-"));\n',
                    's.indexOf("-")',
                    [("a-b", "1"), ("-x", "0"), ("abc", "-1")],
                    hints=["indexOf gives the position, or -1.",
                           'Write s.indexOf("-").']),
                _ex("tscourse-w2-find-4", "Explicit not-found test",
                    "Print `true` when the input does NOT contain `x`, using indexOf.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.indexOf("x") === -1);\n',
                    's.indexOf("x") === -1',
                    [("abc", "true"), ("axc", "false"), ("x", "false")],
                    hints=["Not found is exactly -1.",
                           'Compare s.indexOf("x") to -1.']),
                _ex("tscourse-w2-find-5", "The final dot",
                    "Print the index of the LAST `.` in the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.lastIndexOf("."));\n',
                    's.lastIndexOf(".")',
                    [("my.report.csv", "9"), ("a.b", "1"), ("plain", "-1")],
                    hints=["Search from the right-hand end.",
                           'Write s.lastIndexOf(".").']),
                _fix("tscourse-w2-find-fix1", "Fix the case-sensitive search",
                     "This should find `cat` however it is capitalised, but misses `CAT`. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.includes("cat"));\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.toLowerCase().includes("cat"));\n',
                     [("CAT", "true"), ("A Cat here", "true"), ("dog", "false")],
                     hints=["Searching is case-sensitive.",
                            "Lowercase the haystack before searching."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`s.includes(x)` is equivalent to…",
                   ["s.indexOf(x) === 0", "s.indexOf(x) !== -1", "s.indexOf(x) > 0",
                    "s.length > 0"], 1,
                   "Found means the index is anything other than -1."),
                _q("Why is `if (s.indexOf(\"a\"))` a bug?",
                   ["indexOf doesn't exist", "A match at index 0 is falsy, so it reads as 'not found'",
                    "It is too slow", "indexOf returns a string"], 1,
                   "Position 0 is a real match but behaves as false. Compare to -1 explicitly."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w2-slice", "Slicing out a piece",
            "Taking a substring by position.",
            """
`slice(start, end)` returns the characters from `start` **up to but not
including** `end`:

```
 "h"  "e"  "l"  "l"  "o"
  0    1    2    3    4    5   <- boundaries
```

```ts
const s = "hello";
s.slice(0, 3)    // "hel"   indices 0,1,2
s.slice(1, 3)    // "el"
s.slice(2)       // "llo"   from 2 to the end
s.slice(0, 0)    // ""      empty
```

**Why exclude the end?** Because then the length of the result is simply
`end - start`. `slice(0, 3)` gives exactly 3 characters. Once you internalise
that, the arithmetic stops being fiddly.

**Negative indices count from the end**, which is enormously convenient:

```ts
s.slice(-1)      // "o"    last character
s.slice(-3)      // "llo"  last three
s.slice(0, -1)   // "hell" everything except the last
```

**Slicing at a found position** is the classic combination — find, then cut:

```ts
const file = "report.csv";
const dot = file.lastIndexOf(".");
console.log(file.slice(0, dot));   // "report"
console.log(file.slice(dot + 1));  // "csv"
```

`substring` does something very similar but treats negatives as 0. Prefer
`slice`; there is no reason to carry two.

> ⚠️ **Common mistakes:** expecting `slice(0, 3)` to include index 3; forgetting
> the `+ 1` when slicing after a found separator (you'd keep the separator); and
> using `substring` with a negative number and wondering why nothing happened.
""",
            warmup=[
                _q('What is `"hello".slice(0, 2)`?', ['"he"', '"hel"', '"h"', '"llo"'], 0,
                   "Indices 0 and 1 — the end is excluded."),
                _q('What is `"hello".slice(2)`?', ['"he"', '"llo"', '"l"', '"hello"'], 1,
                   "With no end, it runs to the end of the string."),
                _q('How many characters does `s.slice(2, 6)` return (for a long enough s)?',
                   ["3", "4", "5", "6"], 1, "end - start = 6 - 2 = 4."),
                _q('What is `"hello".slice(-2)`?', ['"he"', '"lo"', '"llo"', '""'], 1,
                   "Negative counts back from the end: the last two characters."),
            ],
            exercises=[
                _ex("tscourse-w2-slice-1", "First three",
                    "Print the first three characters of the input.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(0, 3));\n',
                    's.slice(0, 3)',
                    [("hello", "hel"), ("abcdef", "abc")],
                    hints=["The end index is excluded, so 0 to 3 gives three characters.",
                           "Write s.slice(0, 3)."]),
                _ex("tscourse-w2-slice-2", "Drop the first character",
                    "Print everything except the first character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(1));\n',
                    's.slice(1)',
                    [("hello", "ello"), ("ab", "b")],
                    hints=["Start at index 1 and run to the end.",
                           "Write s.slice(1)."]),
                _ex("tscourse-w2-slice-3", "Last two characters",
                    "Print the last two characters, using a negative index.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(-2));\n',
                    's.slice(-2)',
                    [("hello", "lo"), ("ab", "ab")],
                    hints=["Negative means 'this many from the end'.",
                           "Write s.slice(-2)."]),
                _ex("tscourse-w2-slice-4", "Drop the last character",
                    "Print everything except the final character.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.slice(0, -1));\n',
                    's.slice(0, -1)',
                    [("hello!", "hello"), ("ab", "a")],
                    hints=["A negative END means 'stop that far from the end'.",
                           "Write s.slice(0, -1)."]),
                _ex("tscourse-w2-slice-5", "The file extension",
                    "Print the extension of a filename, without the dot: `report.csv` → `csv`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'const dot = name.lastIndexOf(".");\n'
                    'console.log(name.slice(dot + 1));\n',
                    'name.slice(dot + 1)',
                    [("report.csv", "csv"), ("my.data.json", "json"), ("a.b", "b")],
                    hints=["Start one past the dot, or you keep the dot.",
                           "Write name.slice(dot + 1)."],
                    difficulty="Medium"),
                _ex("tscourse-w2-slice-6", "The base name",
                    "Print the filename WITHOUT its extension: `report.csv` → `report`.",
                    _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                    'const dot = name.lastIndexOf(".");\n'
                    'console.log(name.slice(0, dot));\n',
                    'name.slice(0, dot)',
                    [("report.csv", "report"), ("my.data.json", "my.data")],
                    hints=["Cut from the start up to (not including) the dot.",
                           "Write name.slice(0, dot)."],
                    difficulty="Medium"),
                _fix("tscourse-w2-slice-fix1", "Fix the retained dot",
                     "This should print the extension `csv` but prints `.csv`. Fix it.",
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     'const dot = name.lastIndexOf(".");\n'
                     'console.log(name.slice(dot));\n',
                     _FS + 'const name = fs.readFileSync(0, "utf8").trim();\n'
                     'const dot = name.lastIndexOf(".");\n'
                     'console.log(name.slice(dot + 1));\n',
                     [("report.csv", "csv"), ("a.b", "b")],
                     hints=["Slicing FROM the dot includes the dot itself.",
                            "Start one character later: dot + 1."]),
            ],
            quiz=[
                _q("`s.slice(a, b)` returns how many characters?",
                   ["b", "b - a", "b - a + 1", "a + b"], 1,
                   "Excluding the end makes the length exactly b - a."),
                _q("Which gives everything but the last character?",
                   ["s.slice(1)", "s.slice(0, -1)", "s.slice(-1)", "s.slice(0, s.length)"], 1,
                   "A negative end stops that many characters from the end."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w2-shape", "Padding, repeating & replacing",
            "Making output line up, and swapping text out.",
            """
**Padding** grows a string to a target width, which is how columns line up:

```ts
"7".padStart(3, "0")      // "007"    pad the FRONT
"7".padStart(4)           // "   7"   spaces by default
"Name".padEnd(10, ".")    // "Name......"
```

Right-align numbers with `padStart`, left-align labels with `padEnd`. Two
`padEnd`s and everything in a report suddenly reads as a table:

```ts
console.log("Coffee".padEnd(12) + "$13.00".padStart(8));
console.log("Rent".padEnd(12) + "$900.00".padStart(8));
```

```
Coffee        $13.00
Rent         $900.00
```

**Repeating** builds rules and bars:

```ts
"-".repeat(20)     // a 20-character rule
"█".repeat(3)      // a tiny bar chart
```

**Replacing** swaps text out. `replace` changes only the first match;
`replaceAll` changes every one:

```ts
"a-b-c".replace("-", " ")      // "a b-c"    first only
"a-b-c".replaceAll("-", " ")   // "a b c"    all of them
"  x  ".trim()                 // "x"
```

Remember: every one of these returns a **new** string. `s.replaceAll(...)` on
its own does nothing useful — you must use or store the result.

> ⚠️ **Common mistakes:** using `replace` when you meant `replaceAll` and only
> fixing the first occurrence; padding to a width shorter than the string (it's
> left alone, never truncated); and forgetting that padding a *number* requires
> `String(n)` or a template hole first.
""",
            warmup=[
                _q('`"5".padStart(3, "0")` is…', ['"500"', '"005"', '"5  "', '"5"'], 1,
                   "The front is padded until the length is 3."),
                _q('`"hello".padStart(3, "0")` is…', ['"hel"', '"hello"', '"000hello"', '""'], 1,
                   "Already longer than 3, so it is returned unchanged — padding never truncates."),
                _q('`"a-b-c".replace("-", "+")` is…', ['"a+b+c"', '"a+b-c"', '"a-b-c"', '"abc"'], 1,
                   "replace changes only the first occurrence."),
                _q('`"ab".repeat(3)` is…', ['"ababab"', '"aaabbb"', '"ab3"', '"ab"'], 0,
                   "Three copies, joined."),
            ],
            exercises=[
                _ex("tscourse-w2-shape-1", "Zero-pad an ID",
                    "Print the input padded with leading zeros to 5 characters: `42` → `00042`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.padStart(5, "0"));\n',
                    's.padStart(5, "0")',
                    [("42", "00042"), ("7", "00007"), ("12345", "12345")],
                    hints=["padStart adds to the front until the length is reached.",
                           'Write s.padStart(5, "0").']),
                _ex("tscourse-w2-shape-2", "Left-align a label",
                    "Print the input padded with dots to 10 characters: `Rent` → `Rent......`.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.padEnd(10, "."));\n',
                    's.padEnd(10, ".")',
                    [("Rent", "Rent......"), ("Groceries", "Groceries.")],
                    hints=["padEnd adds to the back.",
                           'Write s.padEnd(10, ".").']),
                _ex("tscourse-w2-shape-3", "A rule as wide as the text",
                    "Print the input, then a line of `=` exactly as long as it.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s);\nconsole.log("=".repeat(s.length));\n',
                    '"=".repeat(s.length)',
                    [("Report", "Report\n======"), ("Hi", "Hi\n==")],
                    hints=["repeat takes the number of copies.",
                           'The count is s.length: "=".repeat(s.length).']),
                _ex("tscourse-w2-shape-4", "Swap every separator",
                    "Print the input with EVERY `-` replaced by a space.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.replaceAll("-", " "));\n',
                    's.replaceAll("-", " ")',
                    [("a-b-c", "a b c"), ("one-two", "one two"), ("plain", "plain")],
                    hints=["replace stops after the first match.",
                           'Use replaceAll("-", " ").']),
                _ex("tscourse-w2-shape-5", "A tiny bar",
                    "The input is a small number. Print that many `#` characters.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log("#".repeat(n));\n',
                    '"#".repeat(n)',
                    [("3", "###"), ("1", "#"), ("6", "######")],
                    hints=["repeat takes a number, and n already is one.",
                           'Write "#".repeat(n).']),
                _ex("tscourse-w2-shape-6", "An aligned row",
                    "Print `Coffee` padded to 12 characters, then `$13.00` right-aligned in 8.",
                    _FS + 'const label = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(label.padEnd(12) + "$13.00".padStart(8));\n',
                    'label.padEnd(12) + "$13.00".padStart(8)',
                    [("Coffee", "Coffee        $13.00"), ("Rent", "Rent          $13.00")],
                    hints=["padEnd for the label on the left, padStart for the amount on the right.",
                           'Join them with +: label.padEnd(12) + "$13.00".padStart(8).'],
                    difficulty="Medium"),
                _fix("tscourse-w2-shape-fix1", "Fix the partial replace",
                     "This should replace every `-` but only replaces the first. Fix it.",
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.replace("-", " "));\n',
                     _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(s.replaceAll("-", " "));\n',
                     [("a-b-c", "a b c"), ("x-y", "x y")],
                     hints=["replace handles one occurrence only.",
                            "Use replaceAll."]),
            ],
            quiz=[
                _q("`\"abc\".padStart(2, \"0\")` gives…", ['"ab"', '"abc"', '"0abc"', '""'], 1,
                   "Padding never shortens a string."),
                _q("To right-align an amount in a report column you use…",
                   ["padEnd", "padStart", "repeat", "trim"], 1,
                   "padStart pushes the text to the right by filling the front."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w2-tonumber", "Text to numbers",
            "Converting input into something you can compute with.",
            """
Input always arrives as **text**, even when it looks like a number. `"12"` is
not `12`, and `"12" + 1` is `"121"`. Convert deliberately:

```ts
Number("42")       // 42
Number("4.5")      // 4.5
Number("  7  ")    // 7      surrounding whitespace is fine
Number("")         // 0      ⚠️ an empty string becomes zero
Number("abc")      // NaN
Number("12kg")     // NaN    the WHOLE string must be numeric
```

`parseInt` is more forgiving — it reads a leading number and stops:

```ts
parseInt("12kg", 10)    // 12
parseInt("abc", 10)     // NaN
parseFloat("3.5cm")     // 3.5
```

The `10` is the number base; always pass it, so `"08"` can never be misread.

**NaN** — "Not a Number" — is what a failed conversion produces. It is
contagious (`NaN + 1` is `NaN`) and, famously, **not equal to itself**:

```ts
const v = Number("abc");
console.log(v === NaN);          // false  ⚠️ always false, for everything
console.log(Number.isNaN(v));    // true   ✅ the correct test
```

So the rule is: **test with `Number.isNaN(x)`**, never with `===`.

**Round-tripping.** Going back the other way, `toFixed` gives you a string with
a set number of decimals, and `String(n)` gives the plain text:

```ts
const total = 13;
console.log(total.toFixed(2));   // "13.00"
console.log(String(total));      // "13"
```

> ⚠️ **Common mistakes:** forgetting to convert, so `+` silently concatenates;
> comparing to `NaN` with `===`; and being surprised that `Number("")` is `0`,
> which makes empty input look like a legitimate zero.
""",
            warmup=[
                _q('What is `Number("12") + 1`?', ['"121"', "13", "12", "NaN"], 1,
                   "Converted first, so it's real addition."),
                _q('What is `"12" + 1`?', ['"121"', "13", "12", "NaN"], 0,
                   "A string on the left means concatenation."),
                _q('What is `Number("12kg")`?', ["12", "NaN", '"12"', "0"], 1,
                   "Number requires the entire string to be numeric."),
                _q('What is `parseInt("12kg", 10)`?', ["12", "NaN", '"12"', "0"], 0,
                   "parseInt reads the leading digits and stops."),
                _q("What does `Number.isNaN(Number(\"abc\"))` give?", ["true", "false"], 0,
                   "The conversion failed, so the result is NaN."),
            ],
            exercises=[
                _predict("tscourse-w2-num-p1", "The type of a failed conversion",
                         'const raw = "banana";\nconst n = Number(raw);\n',
                         "n", "number",
                         why="`Number(\"banana\")` is NaN when it runs — but that is a *value*, "
                             "not a type, and this is the gap the lesson is about.",
                         hints=["NaN is a number: `typeof NaN` reports \"number\".",
                                "Number() always hands back a number, successful or not.",
                                "Write number."],
                         difficulty="Easy"),
                _diagnose("tscourse-w2-num-diag1", "The text that was never converted",
                          "TS2362: The left-hand side of an arithmetic operation must be of "
                          "type 'any', 'number', 'bigint' or an enum type.",
                          _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(raw * 2);\n',
                          _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                          'console.log(Number(raw) * 2);\n',
                          [("21", "42"), ("0", "0")],
                          ask="The compiler is naming the exact operand it objects to. "
                              "Convert it so the program doubles its input.",
                          hints=["Input arrives as text — always, however numeric it looks.",
                                 "'Left-hand side' points at `raw`, not at `2`.",
                                 "Wrap it: Number(raw) * 2."],
                          difficulty="Easy"),
                _ex("tscourse-w2-num-1", "Double the input",
                    "Read a number and print it doubled.",
                    _FS + 'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(n * 2);\n',
                    'Number(fs.readFileSync(0, "utf8").trim())',
                    [("21", "42"), ("0", "0"), ("2.5", "5")],
                    hints=["Convert the text before doing arithmetic.",
                           "Wrap the read in Number(...)."]),
                _ex("tscourse-w2-num-2", "Money, formatted",
                    "Read an amount and print it with exactly two decimals: `7.5` → `7.50`.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(amt.toFixed(2));\n',
                    'amt.toFixed(2)',
                    [("7.5", "7.50"), ("13", "13.00"), ("0.1", "0.10")],
                    hints=["toFixed sets the number of decimal places.",
                           "Write amt.toFixed(2)."]),
                _ex("tscourse-w2-num-3", "A number with a unit",
                    "The input looks like `12kg`. Print just the number, 12.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(parseInt(raw, 10));\n',
                    'parseInt(raw, 10)',
                    [("12kg", "12"), ("7lbs", "7"), ("100m", "100")],
                    hints=["Number() would give NaN here — you need the forgiving one.",
                           "Write parseInt(raw, 10)."]),
                _ex("tscourse-w2-num-4", "Is it a number at all?",
                    "Print `true` when the input is NOT a valid number.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(Number.isNaN(Number(raw)));\n',
                    'Number.isNaN(Number(raw))',
                    [("abc", "true"), ("42", "false"), ("4.5", "false")],
                    hints=["Convert, then test the result properly.",
                           "Write Number.isNaN(Number(raw))."],
                    difficulty="Medium"),
                _ex("tscourse-w2-num-5", "Percent of a total",
                    "Read an amount and print 8% of it, to two decimals: `50` → `4.00`.",
                    _FS + 'const amt = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log((amt * 0.08).toFixed(2));\n',
                    '(amt * 0.08).toFixed(2)',
                    [("50", "4.00"), ("100", "8.00"), ("12.5", "1.00")],
                    hints=["8% is a multiplication by 0.08.",
                           "Compute first, then format: (amt * 0.08).toFixed(2)."]),
                _fix("tscourse-w2-num-fix1", "Fix the accidental concatenation",
                     "This should add 10 to the input, but `5` gives `510`. Fix it.",
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(raw + 10);\n',
                     _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                     'console.log(Number(raw) + 10);\n',
                     [("5", "15"), ("0", "10")],
                     hints=["raw is text, so + joins instead of adding.",
                            "Convert it: Number(raw) + 10."],
                     difficulty="Medium"),
                _fix("tscourse-w2-num-fix2", "Fix the NaN test",
                     "This should print `true` for `abc`, but always prints `false`. Fix it.",
                     _FS + 'const v = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(v === NaN);\n',
                     _FS + 'const v = Number(fs.readFileSync(0, "utf8").trim());\n'
                     'console.log(Number.isNaN(v));\n',
                     [("abc", "true"), ("42", "false")],
                     hints=["NaN is not equal to anything, not even another NaN.",
                            "Use Number.isNaN(v)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q('Why pass 10 to parseInt?',
                   ["It's the maximum value", "It fixes the number base to decimal",
                    "It's the number of digits", "It is optional and pointless"], 1,
                   "Being explicit about base 10 removes any ambiguity."),
                _q('`Number("")` is…', ["NaN", "0", '""', "undefined"], 1,
                   "Empty text converts to zero — a real source of quiet bugs with blank input."),
                _q("`total.toFixed(2)` returns…",
                   ["a number", "a string", "a boolean", "nothing"], 1,
                   "A string, ready to print — don't do further maths on it."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #2 — the entry cleaner",
        """
Real expense lines are typed by hand and arrive messy: stray spaces, random
capitalisation, a unit stuck to the amount. This week Budget Buddy **cleans one
up and files it**.

The input is a single line like:

```
  coffee-and-cake:12kg
```

Print a four-line record:

```
Label:  Coffee and cake
Code:   COF
Amount: 12
Row:    Coffee and cake....... 12
```

Rules:

- **Label** — trimmed, `-` swapped for spaces, first letter capitalised, rest lowercase.
- **Code** — the first three letters of the label, uppercased.
- **Amount** — the digits after the `:`, read with `parseInt`.
- **Row** — the label padded with `.` to 22 characters, a space, then the amount.
""",
        _ch("tscourse-w2-capstone", "Budget Buddy #2", "Medium",
            "Clean the raw entry and print the four lines exactly.",
            _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
            'const colon = raw.indexOf(":");\n'
            'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
            'const label = words[0].toUpperCase() + words.slice(1);\n'
            'const code = label.slice(0, 3).toUpperCase();\n'
            'const amount = parseInt(raw.slice(colon + 1), 10);\n'
            'console.log(`Label:  ${label}`);\n'
            'console.log(`Code:   ${code}`);\n'
            'console.log(`Amount: ${amount}`);\n'
            'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);\n',
            'const colon = raw.indexOf(":");\n'
            'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
            'const label = words[0].toUpperCase() + words.slice(1);\n'
            'const code = label.slice(0, 3).toUpperCase();\n'
            'const amount = parseInt(raw.slice(colon + 1), 10);\n'
            'console.log(`Label:  ${label}`);\n'
            'console.log(`Code:   ${code}`);\n'
            'console.log(`Amount: ${amount}`);\n'
            'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);',
            [("  coffee-and-cake:12kg",
              "Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12"),
             ("RENT:900",
              "Label:  Rent\nCode:   REN\nAmount: 900\nRow:    Rent.................. 900")],
            hints=["Find the colon first — everything before it is the label, everything after is the amount.",
                   'Build the label in steps: slice off the front, replaceAll("-", " "), then toLowerCase().',
                   "Capitalise with words[0].toUpperCase() + words.slice(1).",
                   'The amount needs parseInt(raw.slice(colon + 1), 10) because of the trailing unit.',
                   'The row is label.padEnd(22, ".") then a space then the amount.']),
        example_io="Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12",
        rubric=["The label is trimmed, de-hyphenated, and capitalised like a sentence",
                "The code is three uppercase letters taken from the label",
                "The amount survives a trailing unit like `kg`",
                "The row is padded to a fixed width so many rows would line up"],
        stretch=_ch("tscourse-w2-capstone-stretch", "Budget Buddy #2 (stretch)", "Medium",
                    "Add a fifth line flagging big expenses: `Over:   true` when the amount is 100 or more, `Over:   false` otherwise. You have not met if/else yet — you don't need it, because a comparison is itself a value you can print.",
                    _FS + 'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const colon = raw.indexOf(":");\n'
                    'const words = raw.slice(0, colon).replaceAll("-", " ").toLowerCase();\n'
                    'const label = words[0].toUpperCase() + words.slice(1);\n'
                    'const code = label.slice(0, 3).toUpperCase();\n'
                    'const amount = parseInt(raw.slice(colon + 1), 10);\n'
                    'console.log(`Label:  ${label}`);\n'
                    'console.log(`Code:   ${code}`);\n'
                    'console.log(`Amount: ${amount}`);\n'
                    'console.log(`Row:    ${label.padEnd(22, ".")} ${amount}`);\n'
                    'console.log(`Over:   ${amount >= 100}`);\n',
                    'console.log(`Over:   ${amount >= 100}`);',
                    [("  coffee-and-cake:12kg",
                      "Label:  Coffee and cake\nCode:   COF\nAmount: 12\nRow:    Coffee and cake....... 12\nOver:   false"),
                     ("RENT:900",
                      "Label:  Rent\nCode:   REN\nAmount: 900\nRow:    Rent.................. 900\nOver:   true")],
                    hints=["A comparison like amount >= 100 is itself a value — true or false.",
                           "Drop it straight into a template hole: `Over:   ${amount >= 100}`."]),
    ),
))
