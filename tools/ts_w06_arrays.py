# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 6 — arrays.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 6 ---------------------------------------------------------------

_WEEKS.append(_week(
    6, 2, _M2,
    "Arrays",
    "Hold lists of values, walk them, reshape them with map/filter/find, and sort them correctly.",
    """
A variable holds one value. An **array** holds an ordered list of them, reached
by position. Nearly all real data is a list — rows in a report, items in a
basket, results from a search — so this is the week your programs start looking
like real programs.

Two halves to it:

1. **The manual half** — creating, indexing, looping, accumulating. This is last
   week's accumulator pattern applied to lists, and it never stops being useful.
2. **The method half** — `map`, `filter`, `find`, `some`, `every`, `sort`. Each
   takes a small function (exactly what you learned to pass in week 5) and
   describes an operation on the *whole* list in one line.

The methods are not just shorthand. `nums.filter((x) => x > 10)` says *what you
want*; the loop that does the same thing says *how to get it*, and you have to
read all five lines to find out. Learn both — you need the loop when the
operation doesn't fit a method, and the method every other time.

⏱️ Budget about **eight and a half hours**, spread over several sittings.
""",
    objectives=[
        "Create arrays, index them, and reach the last element safely",
        "Turn a line of input into an array with split, and back with join",
        "Walk an array with for...of and an indexed for, accumulating a result",
        "Add and remove elements, and tell mutation apart from making a new array",
        "Transform every element with map",
        "Select elements with filter, find, findIndex, some and every",
        "Sort numbers and strings correctly with a comparator, without wrecking the original",
        "Chain split, map, filter, sort, slice and join into one readable pipeline",
        "Choose the order of a chain, and copy an array before sorting it",
    ],
    why="Every list you will ever process — search results, table rows, log lines, basket items — is an array. The methods in this week are the vocabulary of day-to-day data work.",
    est_minutes=510,
    glossary=[
        _gloss("array", "An ordered list of values: [3, 5, 7]."),
        _gloss("element", "One value inside an array."),
        _gloss("index", "An element's position, from 0."),
        _gloss(".length", "How many elements the array holds."),
        _gloss(".split(sep)", "Cuts a string into an array of pieces."),
        _gloss(".join(sep)", "Glues an array into one string, with sep between."),
        _gloss(".push(x)", "Adds x to the END, changing the array in place."),
        _gloss(".pop()", "Removes and returns the LAST element."),
        _gloss(".shift() / .unshift(x)", "Remove from / add to the FRONT."),
        _gloss("mutation", "Changing an array in place, so every reference to it sees the change."),
        _gloss("spread (...)", "Copies elements out: [...a] is a fresh copy of a."),
        _gloss(".map(f)", "A NEW array with f applied to every element. Same length."),
        _gloss(".filter(f)", "A NEW array of only the elements passing f. Same or shorter."),
        _gloss(".find(f)", "The FIRST element passing f, or undefined."),
        _gloss(".findIndex(f)", "The index of the first element passing f, or -1."),
        _gloss(".some(f) / .every(f)", "Does any / does every element pass f?"),
        _gloss("callback", "The small function you hand to map, filter, sort…"),
        _gloss("predicate", "A callback returning true/false, used to test elements."),
        _gloss("comparator", "The (a, b) function sort uses to order two elements."),
        _gloss("chain", "Calling one array method on the result of the last, because each returns a new array."),
        _gloss("pipeline", "A chain read top to bottom, each stage transforming the whole list once."),
        _gloss("slice", "Takes a section of an array — and with no arguments, copies the whole thing."),
        _gloss("in-place", "A method that rearranges the array it was called on. sort and reverse are the two."),
    ],
    cheatsheet="""
```ts
// ---- create & index --------------------------------------------------
const a = [3, 5, 7];
a[0]                 // 3      first
a.length             // 3
a[a.length - 1]      // 7      last
a.at(-1)             // 7      last, more readably
a[99]                // undefined  (no error)

// ---- input & output --------------------------------------------------
"1 2 3".split(" ")            // ["1","2","3"]   (strings!)
"1 2 3".split(" ").map(Number) // [1,2,3]
"abc".split("")               // ["a","b","c"]
a.join(" ")                   // "3 5 7"
a.join(", ")                  // "3, 5, 7"

// ---- walk -------------------------------------------------------------
for (const x of a) { ... }              // values
for (let i = 0; i < a.length; i++) { }  // positions

// ---- change in place (MUTATES) ---------------------------------------
a.push(9);      // add to end        a is now [3,5,7,9]
a.pop();        // remove from end   returns 9
a.unshift(1);   // add to front
a.shift();      // remove from front
a.includes(5)   // true
a.indexOf(5)    // 1   (or -1)

// ---- make a NEW array (leaves the original alone) --------------------
[...a]                       // a copy
a.slice(1, 3)                // elements 1 and 2
a.map((x) => x * 2)          // [6,10,14]
a.filter((x) => x > 4)       // [5,7]
a.concat([8, 9])             // a with more on the end

// ---- search ------------------------------------------------------------
a.find((x) => x > 4)         // 5      the element
a.findIndex((x) => x > 4)    // 1      the position
a.some((x) => x > 6)         // true   any?
a.every((x) => x > 0)        // true   all?

// ---- sort (MUTATES — copy first if you care) --------------------------
[...a].sort((x, y) => x - y)   // ascending numbers
[...a].sort((x, y) => y - x)   // descending numbers
[...names].sort()               // strings, alphabetical
[10, 9, 1].sort()               // ⚠️ [1, 10, 9] — sorts as TEXT
```
""",
    self_check=[
        "Can you read a line of numbers into an array and print the last one?",
        "Can you sum an array with a loop, and say why the accumulator sits outside it?",
        "Can you say what map returns when the array has 5 elements?",
        "Can you pick the right one of find, filter, some and includes for a given question?",
        "Can you sort numbers descending, without changing the original array?",
        "Can you explain why [10, 9, 1].sort() gives [1, 10, 9]?",
        "Can you turn a line of raw input into a ranked report in one chain?",
        "Can you say why sort needs a slice() in front of it, and when filter should come before map?",
    ],
    review=[
        _q("The first element of an array is at index…", ["1", "0", "-1", "any"], 1,
           "Arrays are zero-indexed, so the last is at length - 1."),
        _q('`"3 5".split(" ")` gives…',
           ["35", '["3","5"]', '[3,5]', "an error"], 1,
           'split always produces STRINGS — hence the .map(Number) that usually follows.'),
        _q("`[1,2,3].map((x) => x * 2)` has how many elements?",
           ["1", "2", "3", "6"], 2, "map never changes the length — one output per input."),
        _q("`[1,2,3].filter((x) => x > 1).length` is…", ["1", "2", "3", "0"], 1,
           "It keeps 2 and 3."),
        _q("Which returns the ELEMENT rather than a list?",
           ["filter", "map", "find", "some"], 2,
           "find gives the first match itself, or undefined."),
        _q("`[1,2,3].some((x) => x > 2)` is…", ["true", "false", "3", "[3]"], 0,
           "At least one element passes."),
        _q("`a.push(4)` does what to `a`?",
           ["returns a new array", "changes a in place", "nothing", "sorts it"], 1,
           "push mutates. map/filter/slice are the ones that return new arrays."),
        _q("`[10, 9, 1].sort()` gives…",
           ["[1, 9, 10]", "[1, 10, 9]", "[10, 9, 1]", "an error"], 1,
           'With no comparator, sort compares as text: "1" < "10" < "9".'),
        _q("Sorting numbers ascending needs the comparator…",
           ["(a, b) => a > b", "(a, b) => a - b", "(a, b) => b - a", "none"], 1,
           "A negative result means a comes first."),
        _q("To sort without disturbing the original you…",
           ["cannot", "copy first: [...a].sort(...)", "use map", "use filter"], 1,
           "sort mutates the array it is called on."),
        _q("Array methods can be chained because…",
           ["they mutate in place", "each hands back a new array", "TypeScript rewrites them", "they are lazy"], 1,
           "map, filter and slice all return fresh arrays."),
        _q("`nums.filter((n) => n > 0);` on a line of its own changes `nums`…",
           ["to the positives", "not at all — the result was discarded", "to an empty array", "to a copy"], 1,
           "You must keep what a non-mutating method returns."),
        _q("Which pair of methods rearranges the original array?",
           ["map and filter", "sort and reverse", "slice and join", "split and map"], 1,
           "Copy with slice() first if anyone else is holding that array."),
    ],
    milestone="Budget Buddy can now crunch a whole month of expenses at once — totals, extremes, averages and a ranked list.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w6-basics", "Creating & indexing",
            "Making an array and reaching into it.",
            """
Write an array as a comma-separated list in square brackets:

```ts
const names = ["Ada", "Bo", "Cy"];
const nums = [3, 5, 7];
const empty: number[] = [];
```

That `number[]` annotation reads as *"an array of numbers"*. You need it on an
empty array, because there is nothing there for TypeScript to infer from.

**Indexing** works exactly like string indexing — positions start at **0**:

```
 "Ada"  "Bo"  "Cy"
   0      1     2
```

```ts
names[0]                 // "Ada"
names.length             // 3
names[names.length - 1]  // "Cy"   the last one
names.at(-1)             // "Cy"   the same, said better
names[99]                // undefined  — no error, just nothing
```

The `length - 1` for the last element is the same off-by-one you met in week 2,
and it catches people just as often here.

**Out of range is silent.** `names[99]` doesn't throw; it hands back
`undefined`, which then flows onward and breaks something far away. When an
index might be out of range, check it.

**And from this week on, the compiler says so too.** Because `a[i]` can always
come back empty, TypeScript types every index as *"the element, or nothing"*:

```ts
const nums = [3, 5, 7];
nums[0]          // number | undefined   — not just number
```

That is a real change in what you are allowed to write. This no longer compiles:

```ts
const first: number = nums[0];   // ✗ Type 'number | undefined' is not
                                 //   assignable to type 'number'
```

Which is the point: `nums` might have been empty, and the compiler is refusing
to let you pretend otherwise. You have two honest answers.

**1. Supply a fallback with `??`** — "use this if there is nothing there":

```ts
const first = nums[0] ?? 0;      // number
```

`??` yields the left side unless it is `null` or `undefined`, in which case it
yields the right. Reach for it when a default genuinely makes sense.

**2. Assert with `!`** — "I have already checked; there is definitely something
here":

```ts
if (nums.length > 0) {
  const first = nums[0]!;        // number
}
```

The `!` is a promise *you* make to the compiler, and it is only as good as the
check in front of it. Used without one it is just a lie that crashes later — so
prefer `??` unless you can point at the thing that guarantees the element exists.

Printing is the one place you need neither, because `console.log` is happy to
print `undefined`:

```ts
console.log(nums[0]);            // fine — prints 3
```

**Arrays can hold anything**, including other arrays:

```ts
const grid = [[1, 2], [3, 4]];
grid[1]![0]    // 3   — row 1 (asserted non-empty), then column 0
```

Read `grid[1]![0]` left to right: take element 1 (`[3, 4]`), then element 0 of
that (`3`). The `!` is needed because indexing *once* already gave us
`number[] | undefined`, and you cannot index into nothing.

> ⚠️ **Common mistakes:** thinking `a[1]` is the first element; using
> `a[a.length]` for the last; and calling `a.length()` — like strings, it is a
> property, with no parentheses.
""",
            warmup=[
                _q("`const a = [10,20,30]; console.log(a[1]);` prints…",
                   ["10", "20", "30", "1"], 1, "Index 1 is the second element."),
                _q("`[10,20,30].length` is…", ["2", "3", "30", "undefined"], 1,
                   "Three elements."),
                _q("`[10,20,30][3]` is…", ["30", "0", "undefined", "an error"], 2,
                   "Valid indices are 0, 1, 2."),
                _q("`[[1,2],[3,4]][0][1]` is…", ["1", "2", "3", "4"], 1,
                   "Row 0 is [1,2]; its element 1 is 2."),
            ],
            exercises=[
                _predict("tscourse-w6-b-p1", "The type of an element you took out",
                         'const words = "a,bb".split(",");\nconst first = words[0];\n',
                         "first", "string | undefined",
                         why="From this week on, the compiler stops assuming an index is in range.",
                         hints=["`words` is a string[], so an element is a string — if it is there.",
                                "Nothing about `words[0]` promises the array had a first element; "
                                "an empty array would give you undefined.",
                                "Write string | undefined."],
                         difficulty="Medium"),
                _diagnose("tscourse-w6-b-diag1", "The element that might not exist",
                          "TS2532: Object is possibly 'undefined'.",
                          'const names: string[] = ["Ada", "Bo"];\n'
                          'console.log(names[0].toUpperCase());\n',
                          'const names: string[] = ["Ada", "Bo"];\n'
                          'console.log((names[0] ?? "").toUpperCase());\n',
                          [("", "ADA")],
                          ask="You can see the array is not empty; the compiler cannot. "
                              "Give it a fallback so it prints ADA.",
                          hints=["The 'Object' the message means is `names[0]` — the thing "
                                 "you called .toUpperCase() on.",
                                 "Reading past the end of an array gives undefined, and "
                                 "undefined has no .toUpperCase().",
                                 "?? supplies a value for exactly the undefined case.",
                                 'Write (names[0] ?? "").toUpperCase().'],
                          difficulty="Medium"),
                _ex("tscourse-w6-b-1", "First element",
                    "Print the first name in the list.",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[0]);\n',
                    'names[0]', [("", "Ada")],
                    hints=["Positions start at 0."]),
                _ex("tscourse-w6-b-2", "How many",
                    "Print how many names there are.",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names.length);\n',
                    'names.length', [("", "3")],
                    hints=["length is a property — no parentheses."]),
                _ex("tscourse-w6-b-3", "Last element",
                    "Print the last name, computed from the length (not typed as 2).",
                    'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length - 1]);\n',
                    'names[names.length - 1]', [("", "Cy")],
                    hints=["The last index is one less than the length.",
                           "Write names[names.length - 1]."]),
                _ex("tscourse-w6-b-4", "An annotated empty array",
                    "Annotate the empty array as an array of numbers.",
                    'const scores: number[] = [];\nconsole.log(scores.length);\n',
                    'number[]', [("", "0")],
                    hints=["An array of numbers is written number[].",
                           "Write const scores: number[] = [];"]),
                _ex("tscourse-w6-b-5", "Into the grid",
                    "Print the value in row 1, column 0 (it should be 3). "
                    "Indexing once gives you a row *or nothing*, so you have to "
                    "promise the row is there before indexing into it.",
                    'const grid = [[1, 2], [3, 4]];\nconsole.log(grid[1]![0]);\n',
                    'grid[1]![0]', [("", "3")],
                    hints=["Index the row first, then the column.",
                           "grid[1] is number[] | undefined — assert it with ! "
                           "before the second index.",
                           "Write grid[1]![0]."]),
                _ex("tscourse-w6-b-6", "A safe default",
                    "The list is empty. Print 0 rather than `undefined`, using ??.",
                    'const scores: number[] = [];\nconsole.log(scores[0] ?? 0);\n',
                    'scores[0] ?? 0', [("", "0")],
                    hints=["?? supplies a value when the left side is undefined.",
                           "Write scores[0] ?? 0."]),
                _fix("tscourse-w6-b-fix1", "Fix the index",
                     "This should print the FIRST name but prints the second. Fix it.",
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[1]);\n',
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[0]);\n',
                     [("", "Ada")],
                     hints=["Index 1 is the second element.",
                            "The first is index 0."]),
                _fix("tscourse-w6-b-fix2", "Fix the off-by-one",
                     "This should print the last name but prints nothing. Fix it.",
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length]);\n',
                     'const names = ["Ada", "Bo", "Cy"];\nconsole.log(names[names.length - 1]);\n',
                     [("", "Cy")],
                     hints=["A 3-element array has indices 0, 1, 2 — never 3.",
                            "Subtract one from the length."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("For an array of length n, the valid indices are…",
                   ["1..n", "0..n", "0..n-1", "0..n+1"], 2, "Zero-based."),
                _q("Why annotate `const xs: number[] = []`?",
                   ["It is required", "There is nothing in it to infer a type from",
                    "It makes it faster", "To make it readonly"], 1,
                   "An empty literal gives the compiler no evidence."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w6-input", "split & join",
            "Turning a line of text into an array, and back again.",
            """
Input arrives as one string. `split` cuts it into an array:

```ts
"1 2 3".split(" ")        // ["1", "2", "3"]
"a,b,c".split(",")        // ["a", "b", "c"]
"abc".split("")           // ["a", "b", "c"]   — every character
```

**Everything split produces is a string**, even when it looks like a number.
`["1","2","3"]` is three strings. To compute with them, convert:

```ts
"1 2 3".split(" ").map(Number)     // [1, 2, 3]
```

`.map(Number)` runs `Number` on each piece. You'll meet `map` properly in
lesson 5 — for now, take this as the standard opening line for a numeric
program:

```ts
import * as fs from "fs";
const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);
```

Read it right to left: read the input, trim it, cut at spaces, convert each
piece.

**`join` is the mirror image**, gluing an array into one string:

```ts
[3, 5, 7].join(" ")      // "3 5 7"
[3, 5, 7].join(", ")     // "3, 5, 7"
[3, 5, 7].join("")       // "357"
["a"].join(", ")         // "a"        — no trailing separator
[].join(", ")            // ""
```

`join` is how you print a list on one line, and it never leaves a dangling
separator at the end — which a loop building `out += x + ", "` always does.

**Why trim first.** Without `.trim()`, `"1 2 3\\n".split(" ")` gives
`["1", "2", "3\\n"]`, and that last entry converts to a number just fine but
prints with a stray newline. Trim, then split.

> ⚠️ **Common mistakes:** forgetting `.map(Number)` and then adding strings
> (`"1" + "2"` is `"12"`); splitting on `""` when you meant `" "`; and building
> output with `+=` and a separator instead of using `join`.
""",
            warmup=[
                _q('`"a b".split(" ")` gives…',
                   ['"ab"', '["a","b"]', '["a b"]', '["a"," ","b"]'], 1,
                   "Two pieces, with the separator removed."),
                _q('`"1 2".split(" ")[0] + 1` gives…',
                   ["2", '"11"', "11", "an error"], 1,
                   'The piece is the STRING "1", so + joins.'),
                _q('`[1,2,3].join("-")` gives…',
                   ['"1-2-3"', '"123"', "[1,2,3]", '"1-2-3-"'], 0,
                   "Separators go between, never at the end."),
                _q('`"abc".split("")` gives…',
                   ['["abc"]', '["a","b","c"]', '"abc"', "[]"], 1,
                   "An empty separator splits between every character."),
            ],
            exercises=[
                _ex("tscourse-w6-in-1", "Read the numbers",
                    "Read the space-separated numbers into an array and print the first one.",
                    _NUMS + 'console.log(nums[0]);\n',
                    '.split(" ").map(Number)',
                    [("3 5 7", "3"), ("9 1", "9")],
                    hints=["Cut at spaces, then convert each piece.",
                           'Chain .split(" ").map(Number).']),
                _ex("tscourse-w6-in-2", "How many words",
                    "Print how many space-separated words the input has.",
                    _WORDS + 'console.log(words.length);\n',
                    'words.length', [("a b c d", "4"), ("hi", "1")],
                    hints=["Split first, then take the length."]),
                _ex("tscourse-w6-in-3", "Join with commas",
                    "Print the words joined by `, `.",
                    _WORDS + 'console.log(words.join(", "));\n',
                    'words.join(", ")', [("a b c", "a, b, c"), ("solo", "solo")],
                    hints=["join puts the separator between elements only.",
                           'Write words.join(", ").']),
                _ex("tscourse-w6-in-4", "Sum two numbers from input",
                    "The input is two numbers. Print their sum.",
                    _NUMS + 'console.log((nums[0] ?? 0) + (nums[1] ?? 0));\n',
                    '(nums[0] ?? 0) + (nums[1] ?? 0)',
                    [("3 4", "7"), ("10 -2", "8")],
                    hints=["They are already numbers thanks to map(Number).",
                           "Indexing gives number | undefined, and you cannot add "
                           "undefined \u2014 supply a fallback with ??.",
                           "Write (nums[0] ?? 0) + (nums[1] ?? 0)."]),
                _ex("tscourse-w6-in-5", "Letters of a word",
                    "Split the input into individual characters and print them space-separated.",
                    _FS + 'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(s.split("").join(" "));\n',
                    's.split("").join(" ")',
                    [("abc", "a b c"), ("hi", "h i")],
                    hints=["An empty separator splits every character apart.",
                           'Write s.split("").join(" ").'],
                    difficulty="Medium"),
                _fix("tscourse-w6-in-fix1", "Fix the missing conversion",
                     "This should print the sum 7 for `3 4`, but prints `34`. Fix it.",
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ");\n'
                     'console.log((nums[0] ?? "") + (nums[1] ?? ""));\n',
                     _FS + 'const nums = fs.readFileSync(0, "utf8").trim().split(" ").map(Number);\n'
                     'console.log((nums[0] ?? 0) + (nums[1] ?? 0));\n',
                     [("3 4", "7"), ("10 5", "15")],
                     hints=["split gives strings, so + is joining them.",
                            "Add .map(Number) after the split."],
                     difficulty="Medium"),
                _fix("tscourse-w6-in-fix2", "Fix the trailing separator",
                     "This builds the line by hand and leaves a trailing `, `. Rewrite it using join.",
                     _WORDS + 'let out = "";\nfor (const w of words) {\n  out += w + ", ";\n}\nconsole.log(out);\n',
                     _WORDS + 'console.log(words.join(", "));\n',
                     [("a b c", "a, b, c"), ("solo", "solo")],
                     hints=["Every pass appends a separator, including after the last word.",
                            'join solves this exactly: words.join(", ").'],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What type are the pieces from `.split(\" \")`?",
                   ["numbers", "strings", "booleans", "it depends on the input"], 1,
                   "Always strings — convert explicitly."),
                _q("Why is join better than += with a separator?",
                   ["It is faster", "It never leaves a separator dangling at the end",
                    "It sorts", "It removes duplicates"], 1,
                   "Separators go strictly between elements."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w6-loop", "Walking an array",
            "Loops and accumulators over lists.",
            """
Everything you learned about loops in week 4 applies directly. `for...of` hands
you each element:

```ts
let sum = 0;
for (const x of [1, 2, 3, 4]) {
  sum += x;
}
console.log(sum);   // 10
```

| pass | x | sum after |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 3 |
| 3 | 3 | 6 |
| 4 | 4 | 10 |

The accumulator lives **outside** the loop — same rule as always.

**When you need positions**, use the indexed form:

```ts
for (let i = 0; i < nums.length; i++) {
  console.log(`${i}: ${nums[i]}`);
}
```

Use it when you need the index in the output, when you want to compare an
element with its neighbour (`nums[i - 1]`), or when you're walking backwards.

**The four accumulator shapes**, now over arrays:

```ts
let sum = 0;                        for (const x of a) sum += x;
let count = 0;                      for (const x of a) if (x > 10) count++;
let best = a[0];                    for (const x of a) if (x > best) best = x;
let out = "";                       for (const x of a) out += x;
```

**A note on the maximum.** Over an array you can seed `best` with `a[0]` rather
than `-Infinity`, because a real element is right there. That's better: the
answer is guaranteed to be a value that actually appeared. It does assume the
array is non-empty — so if it might be, check first.

**Neighbour comparisons** need indices, and start at 1:

```ts
let rises = 0;
for (let i = 1; i < a.length; i++) {
  if (a[i] > a[i - 1]) rises++;
}
```

Starting at `i = 1` is deliberate: element 0 has no predecessor.

> ⚠️ **Common mistakes:** declaring the accumulator inside the loop; seeding a
> maximum with 0 when the data can be negative; and looking at `a[i - 1]` from
> `i = 0`, which is `a[-1]` — `undefined`.
""",
            warmup=[
                _q("Summing [2,2,2] with a for...of accumulator gives…",
                   ["2", "6", "3", "222"], 1, "2+2+2."),
                _q("Why does a neighbour-comparison loop start at i = 1?",
                   ["style", "element 0 has no previous element", "to skip the first value",
                    "arrays start at 1"], 1,
                   "a[-1] would be undefined."),
                _q("Seeding `best = a[0]` rather than 0 protects against…",
                   ["empty arrays", "all-negative data", "strings", "nothing"], 1,
                   "With 0 as the seed, all-negative data would wrongly report 0."),
            ],
            exercises=[
                _ex("tscourse-w6-lp-1", "Sum the list",
                    "Add every number and print the total.",
                    _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                    'sum += x;', [("1 2 3 4", "10"), ("5", "5")],
                    hints=["Add each element to the running total."]),
                _ex("tscourse-w6-lp-2", "Largest",
                    "Print the largest number, seeding from the first element.",
                    _NUMS + 'let best = nums[0]!;\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                    'let best = nums[0]!;',
                    [("3 9 2 7", "9"), ("4", "4"), ("-5 -2 -9", "-2")],
                    hints=["Seed from a value that is actually in the list.",
                           "The input always has at least one number, so assert it with !.",
                           "Write let best = nums[0]!;"]),
                _ex("tscourse-w6-lp-3", "Count the big ones",
                    "Count how many numbers are greater than 10.",
                    _NUMS + 'let count = 0;\nfor (const x of nums) {\n  if (x > 10) {\n    count++;\n  }\n}\nconsole.log(count);\n',
                    'x > 10', [("5 20 30 1", "2"), ("1 2", "0")],
                    hints=["Strictly greater, so 10 itself does not count."]),
                _ex("tscourse-w6-lp-4", "Numbered list",
                    "Print each element on its own line as `1. value`, numbering from 1.",
                    _WORDS + 'for (let i = 0; i < words.length; i++) {\n  console.log(`${i + 1}. ${words[i]}`);\n}\n',
                    '`${i + 1}. ${words[i]}`',
                    [("a b c", "1. a\n2. b\n3. c"), ("solo", "1. solo")],
                    hints=["The index starts at 0 but the display starts at 1.",
                           "Write `${i + 1}. ${words[i]}`."],
                    difficulty="Medium"),
                _ex("tscourse-w6-lp-5", "Count the rises",
                    "Count how many times a number is greater than the one before it.",
                    _NUMS + 'let rises = 0;\nfor (let i = 1; i < nums.length; i++) {\n  if (nums[i]! > nums[i - 1]!) {\n    rises++;\n  }\n}\nconsole.log(rises);\n',
                    'nums[i]! > nums[i - 1]!',
                    [("1 3 2 5", "2"), ("5 4 3", "0"), ("1 2 3", "2")],
                    hints=["Compare each element with its predecessor.",
                           "The loop bound guarantees both are in range, so assert both with !.",
                           "Write nums[i]! > nums[i - 1]!."],
                    difficulty="Medium"),
                _ex("tscourse-w6-lp-6", "Average",
                    "Print the average of the numbers to two decimal places.",
                    _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log((sum / nums.length).toFixed(2));\n',
                    '(sum / nums.length).toFixed(2)',
                    [("2 4 6", "4.00"), ("1 2", "1.50")],
                    hints=["Total first, then divide by the count — after the loop.",
                           "Write (sum / nums.length).toFixed(2)."]),
                _fix("tscourse-w6-lp-fix1", "Fix the sum seed",
                     "This total is always one too big. Fix it so `1 2 3` gives 6.",
                     _NUMS + 'let sum = 1;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                     _NUMS + 'let sum = 0;\nfor (const x of nums) {\n  sum += x;\n}\nconsole.log(sum);\n',
                     [("1 2 3", "6"), ("5", "5")],
                     hints=["What should the sum of an empty list be?",
                            "A running total starts at 0."]),
                _fix("tscourse-w6-lp-fix2", "Fix the maximum seed",
                     "With all-negative input this wrongly prints 0. Fix it so `-5 -2 -9` gives -2.",
                     _NUMS + 'let best = 0;\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                     _NUMS + 'let best = nums[0]!;\nfor (const x of nums) {\n  if (x > best) {\n    best = x;\n  }\n}\nconsole.log(best);\n',
                     [("-5 -2 -9", "-2"), ("3 9 2", "9")],
                     hints=["0 beats every negative number, so it is never replaced.",
                            "Seed from an element that is actually in the array: nums[0]!."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Which loop do you need to print `3: value`?",
                   ["for...of", "an indexed for", "either", "while(true)"], 1,
                   "Only the indexed form gives you the position."),
                _q("An accumulator declared inside the loop body…",
                   ["works fine", "is reset every pass", "is an error", "is faster"], 1,
                   "It never accumulates anything."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w6-mutate", "Growing, shrinking & copying",
            "Changing an array in place — and when not to.",
            """
Four methods change an array **in place**:

```ts
const a = [1, 2, 3];
a.push(4);      // [1,2,3,4]   add to the end
a.pop();        // [1,2,3]     remove from the end, returns 4
a.unshift(0);   // [0,1,2,3]   add to the front
a.shift();      // [1,2,3]     remove from the front, returns 0
```

**`push` is how you build a list in a loop** — the array equivalent of `+=`:

```ts
const doubled: number[] = [];
for (const x of nums) {
  doubled.push(x * 2);
}
```

**`const` does not mean frozen.** This surprises everyone once:

```ts
const a = [1, 2];
a.push(3);      // ✅ fine — the array's CONTENTS changed
a = [9];        // ❌ error — the NAME cannot be repointed
```

`const` fixes what the name points at, not what lives inside it.

**Mutation is shared.** Assigning an array to another name does not copy it —
both names point at the same array:

```ts
const a = [1, 2];
const b = a;
b.push(3);
console.log(a);   // [1, 2, 3]   ⚠️ a changed too
```

That's the single most surprising thing in this lesson, and the cause of bugs
that look like action at a distance. To get a genuine copy, spread it:

```ts
const b = [...a];      // a fresh array with the same elements
b.push(3);             // a is untouched
```

**Searching:**

```ts
a.includes(2)     // true / false
a.indexOf(2)      // 1, or -1 when absent
```

**`slice` takes a piece without mutating** (unlike its confusable neighbour
`splice`, which does mutate):

```ts
a.slice(1, 3)     // elements 1 and 2, as a new array
a.slice(-2)       // the last two
```

Same rules as string `slice` — the end is excluded, negatives count from the
end.

> ⚠️ **Common mistakes:** expecting `const b = a` to copy; expecting `push` to
> return the new array (it returns the new *length*); and mixing up `slice`
> (copies) with `splice` (mutates).
""",
            warmup=[
                _q("`const a = [1,2]; a.push(3);` is…",
                   ["an error, a is const", "fine — contents may change", "a no-op",
                    "a copy"], 1,
                   "const fixes the binding, not the contents."),
                _q("`const a=[1,2]; const b=a; b.push(3); a.length` is…",
                   ["2", "3", "0", "an error"], 1,
                   "b is the same array, so a sees the change too."),
                _q("`[1,2,3].pop()` returns…", ["[1,2]", "3", "1", "3 elements"], 1,
                   "The removed element."),
                _q("Which makes a genuine copy?",
                   ["const b = a", "const b = [...a]", "const b = a.length",
                    "const b = a.push()"], 1,
                   "Spreading builds a fresh array."),
            ],
            exercises=[
                _ex("tscourse-w6-mu-1", "Build with push",
                    "Collect the doubled numbers into a new array, then print them space-separated.",
                    _NUMS + 'const doubled: number[] = [];\nfor (const x of nums) {\n  doubled.push(x * 2);\n}\nconsole.log(doubled.join(" "));\n',
                    'doubled.push(x * 2);',
                    [("1 2 3", "2 4 6"), ("5", "10")],
                    hints=["push adds to the end of the array.",
                           "Write doubled.push(x * 2);"]),
                _ex("tscourse-w6-mu-2", "Add to the end",
                    "Append 99 to the list, then print it.",
                    'const a = [1, 2, 3];\na.push(99);\nconsole.log(a.join(" "));\n',
                    'a.push(99);', [("", "1 2 3 99")],
                    hints=["push puts it at the end."]),
                _ex("tscourse-w6-mu-3", "Copy before changing",
                    "Make `b` a genuine copy so pushing to it leaves `a` alone.",
                    'const a = [1, 2];\nconst b = [...a];\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                    'const b = [...a];', [("", "2\n3")],
                    hints=["Assignment shares; spreading copies.",
                           "Write const b = [...a];"],
                    difficulty="Medium"),
                _ex("tscourse-w6-mu-4", "Is it in there?",
                    "Print whether the list of words contains `cat`.",
                    _WORDS + 'console.log(words.includes("cat"));\n',
                    'words.includes("cat")',
                    [("dog cat bird", "true"), ("dog bird", "false")],
                    hints=["includes answers true or false.",
                           'Write words.includes("cat").']),
                _ex("tscourse-w6-mu-5", "Drop the first",
                    "Print every element except the first, space-separated, without mutating.",
                    _NUMS + 'console.log(nums.slice(1).join(" "));\n',
                    'nums.slice(1)',
                    [("1 2 3", "2 3"), ("9 8", "8")],
                    hints=["slice from index 1 to the end.",
                           "Write nums.slice(1)."]),
                _ex("tscourse-w6-mu-6", "The last two",
                    "Print the last two elements, space-separated.",
                    _NUMS + 'console.log(nums.slice(-2).join(" "));\n',
                    'nums.slice(-2)',
                    [("1 2 3 4", "3 4"), ("7 8", "7 8")],
                    hints=["A negative start counts from the end.",
                           "Write nums.slice(-2)."]),
                _fix("tscourse-w6-mu-fix1", "Fix the accidental sharing",
                     "This should print `2` then `3`, but prints `3` then `3` — the copy is not a copy. Fix it.",
                     'const a = [1, 2];\nconst b = a;\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                     'const a = [1, 2];\nconst b = [...a];\nb.push(3);\nconsole.log(a.length);\nconsole.log(b.length);\n',
                     [("", "2\n3")],
                     hints=["`const b = a;` gives the same array a second name.",
                            "Spread to build a fresh one: [...a]."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`const` applied to an array prevents…",
                   ["adding elements", "reassigning the name", "reading elements",
                    "sorting"], 1,
                   "Contents stay mutable."),
                _q("`slice` and `splice` differ in that…",
                   ["nothing", "slice copies, splice mutates", "splice copies, slice mutates",
                    "slice is for strings only"], 1,
                   "A one-letter difference with opposite consequences."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w6-map", "map — transform every element",
            "One output for every input.",
            """
`map` builds a **new** array by running a function on each element:

```ts
const nums = [1, 2, 3];
nums.map((x) => x * 2);          // [2, 4, 6]
nums.map((x) => `#${x}`);        // ["#1", "#2", "#3"]
```

Compare with the loop it replaces:

```ts
const doubled: number[] = [];
for (const x of nums) {
  doubled.push(x * 2);
}
```

Five lines become one, and — more importantly — the one-liner *cannot* get the
bookkeeping wrong. There is no accumulator to seed and no push to forget.

**Three facts about map, in order of how often they matter:**

1. **The length never changes.** Three in, three out, always. If you want fewer,
   you want `filter`.
2. **A new array comes back.** The original is untouched. Ignore the return
   value and you've done nothing.
3. **The callback must return something.** An arrow with braces and no `return`
   gives you an array of `undefined` — the arrow trap from week 5, in its
   natural habitat.

**The index is available** as a second parameter:

```ts
["a", "b"].map((x, i) => `${i}: ${x}`);   // ["0: a", "1: b"]
```

**Chaining** is where it gets pleasant, because each step hands an array to the
next:

```ts
"1 2 3".split(" ").map(Number).map((x) => x * 10).join(", ");   // "10, 20, 30"
```

`.map(Number)` deserves a note: you're passing the `Number` function itself
rather than calling it — exactly the "functions as values" idea from week 5.

> ⚠️ **Common mistakes:** using `map` when you meant `filter` (the length gives
> it away); forgetting `return` inside a braced callback; and discarding the
> result — `nums.map(...)` on its own line changes nothing.
""",
            warmup=[
                _q("`[1,2,3].map((x) => x * 2)` is…",
                   ["[2,4,6]", "[1,2,3]", "12", "6"], 0, "Each element doubled."),
                _q("`[1,2,3].map((x) => x > 1)` has length…",
                   ["1", "2", "3", "0"], 2, "map always preserves the length."),
                _q("`[1,2].map((x) => { x * 2; })` gives…",
                   ["[2,4]", "[undefined, undefined]", "[]", "an error"], 1,
                   "A braced callback needs an explicit return."),
                _q('`["a","b"].map((x, i) => `${i}${x}`)` is…',
                   ['["0a","1b"]', '["a0","b1"]', '["ab"]', '["1a","2b"]'], 0,
                   "The second parameter is the index, counting from 0."),
            ],
            exercises=[
                _predict("tscourse-w6-mp-p1", "What map hands back",
                         'const words = "a,bb,ccc".split(",");\n'
                         'const lengths = words.map((w) => w.length);\n',
                         "lengths", "number[]",
                         why="`map` changes the element type to whatever the callback returns.",
                         hints=["Start from what one call to the callback returns.",
                                "`w.length` is a number, and map collects one per element.",
                                "Write number[]."],
                         difficulty="Easy"),
                _ex("tscourse-w6-mp-1", "Double them",
                    "Double every number and print them space-separated.",
                    _NUMS + 'console.log(nums.map((x) => x * 2).join(" "));\n',
                    'nums.map((x) => x * 2)',
                    [("1 2 3", "2 4 6"), ("10", "20")],
                    hints=["map transforms each element.",
                           "Write nums.map((x) => x * 2)."]),
                _ex("tscourse-w6-mp-2", "Shout the words",
                    "Uppercase every word and print them space-separated.",
                    _WORDS + 'console.log(words.map((w) => w.toUpperCase()).join(" "));\n',
                    'w.toUpperCase()',
                    [("a bc", "A BC"), ("hi there", "HI THERE")],
                    hints=["The callback receives one word at a time.",
                           "Return w.toUpperCase()."]),
                _ex("tscourse-w6-mp-3", "Number the words",
                    "Print each word prefixed by its 1-based position, comma-separated: `1:a, 2:b`.",
                    _WORDS + 'console.log(words.map((w, i) => `${i + 1}:${w}`).join(", "));\n',
                    '`${i + 1}:${w}`',
                    [("a b", "1:a, 2:b"), ("solo", "1:solo")],
                    hints=["The second callback parameter is the index, from 0.",
                           "Write `${i + 1}:${w}`."],
                    difficulty="Medium"),
                _ex("tscourse-w6-mp-4", "Lengths",
                    "Print the length of each word, space-separated.",
                    _WORDS + 'console.log(words.map((w) => w.length).join(" "));\n',
                    'w.length',
                    [("a bb ccc", "1 2 3"), ("hello", "5")],
                    hints=["Return each word's length.", "Write w.length."]),
                _ex("tscourse-w6-mp-5", "Chain two steps",
                    "Multiply every number by 10, then print them comma-separated.",
                    _NUMS + 'console.log(nums.map((x) => x * 10).join(", "));\n',
                    '.map((x) => x * 10).join(", ")',
                    [("1 2 3", "10, 20, 30"), ("7", "70")],
                    hints=["map produces an array, which join then turns into text.",
                           'Chain .map((x) => x * 10).join(", ").']),
                _fix("tscourse-w6-mp-fix1", "Fix the missing return",
                     "This should double the numbers but prints a row of `undefined`. Fix it.",
                     _NUMS + 'console.log(nums.map((x) => { x * 2; }).join(" "));\n',
                     _NUMS + 'console.log(nums.map((x) => x * 2).join(" "));\n',
                     [("1 2 3", "2 4 6")],
                     hints=["A braced arrow body returns nothing unless you say so.",
                            "Drop the braces, or add return."],
                     difficulty="Medium"),
                _fix("tscourse-w6-mp-fix2", "Fix the discarded result",
                     "This should print the doubled numbers but prints the originals. Fix it.",
                     _NUMS + 'nums.map((x) => x * 2);\nconsole.log(nums.join(" "));\n',
                     _NUMS + 'const doubled = nums.map((x) => x * 2);\nconsole.log(doubled.join(" "));\n',
                     [("1 2 3", "2 4 6"), ("5", "10")],
                     hints=["map does not change nums — it returns a new array that is being thrown away.",
                            "Store the result and print that."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`a.map(f)` where a has 5 elements returns an array of length…",
                   ["0..5", "exactly 5", "1", "it depends on f"], 1,
                   "map is one-for-one; only filter can shorten."),
                _q("`nums.map(Number)` passes…",
                   ["the result of Number", "the Number function itself", "a string",
                    "nothing"], 1,
                   "No parentheses — a function as a value, as in week 5."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w6-filter", "filter, find & friends",
            "Selecting elements, and asking questions about them.",
            """
`filter` keeps the elements whose callback returns `true`:

```ts
const nums = [1, 2, 3, 4, 5, 6];
nums.filter((x) => x % 2 === 0);    // [2, 4, 6]
nums.filter((x) => x > 100);        // []          — empty, not undefined
```

A callback that returns true/false is called a **predicate**. Everything in this
lesson takes one; they differ only in what they hand back:

| method | question | answer |
|---|---|---|
| `filter` | which ones? | a new **array** (possibly empty) |
| `find` | the first one? | the **element**, or `undefined` |
| `findIndex` | where is the first one? | the **index**, or `-1` |
| `some` | any at all? | `true` / `false` |
| `every` | all of them? | `true` / `false` |

```ts
nums.find((x) => x > 3);        // 4        the element itself
nums.findIndex((x) => x > 3);   // 3        its position
nums.some((x) => x > 5);        // true
nums.every((x) => x > 0);       // true
```

**Choose by what you actually need.** Reaching for `filter(...)[0]` when you
want one element works but scans the whole array and allocates one you throw
away; `find` says what you mean. `filter(...).length > 0` is `some`.

**Two edge cases worth knowing:**

- `find` returns `undefined` when nothing matches — check for it before using
  the result.
- `every` on an **empty** array is `true`. ("Every element passes" is vacuously
  true when there are no elements.) It's a real source of surprise when a filter
  upstream emptied the list.

**Chaining filter and map** is the everyday pattern — narrow, then reshape:

```ts
words.filter((w) => w.length > 3).map((w) => w.toUpperCase()).join(", ")
```

Filter first when you can: there's less left to transform.

> ⚠️ **Common mistakes:** using `map` when you meant `filter`; forgetting `find`
> can be `undefined`; and testing `findIndex(...)` for truthiness, when index 0
> is a real match (the `indexOf` trap from week 2, again).
""",
            warmup=[
                _q("`[1,2,3,4].filter((x) => x % 2 === 0)` is…",
                   ["[1,3]", "[2,4]", "[1,2,3,4]", "2"], 1, "The even ones."),
                _q("`[1,2,3].find((x) => x > 1)` is…", ["[2,3]", "2", "1", "true"], 1,
                   "The first matching element itself."),
                _q("`[1,2,3].find((x) => x > 9)` is…", ["[]", "-1", "undefined", "0"], 2,
                   "find has nothing to return."),
                _q("`[].every((x) => x > 5)` is…", ["true", "false", "undefined", "an error"], 0,
                   "Vacuously true — there is no element that fails."),
            ],
            exercises=[
                _ex("tscourse-w6-fl-1", "Keep the evens",
                    "Print the even numbers, space-separated.",
                    _NUMS + 'console.log(nums.filter((x) => x % 2 === 0).join(" "));\n',
                    'x % 2 === 0',
                    [("1 2 3 4 5 6", "2 4 6"), ("1 3", "")],
                    hints=["Even means remainder 0 mod 2."]),
                _ex("tscourse-w6-fl-2", "Count the big ones",
                    "Print how many numbers are greater than 10.",
                    _NUMS + 'console.log(nums.filter((x) => x > 10).length);\n',
                    'nums.filter((x) => x > 10).length',
                    [("5 20 30 1", "2"), ("1 2", "0")],
                    hints=["Filter first, then take the length.",
                           "Write nums.filter((x) => x > 10).length."]),
                _ex("tscourse-w6-fl-3", "First over ten",
                    "Print the first number greater than 10, or `none` if there isn't one.",
                    _NUMS + 'const hit = nums.find((x) => x > 10);\n'
                    'console.log(hit === undefined ? "none" : hit);\n',
                    'nums.find((x) => x > 10)',
                    [("5 20 30", "20"), ("1 2", "none")],
                    hints=["find gives the element or undefined.",
                           "Write nums.find((x) => x > 10)."],
                    difficulty="Medium"),
                _ex("tscourse-w6-fl-4", "Any negatives?",
                    "Print whether any number is negative.",
                    _NUMS + 'console.log(nums.some((x) => x < 0));\n',
                    'nums.some((x) => x < 0)',
                    [("1 -2 3", "true"), ("1 2", "false")],
                    hints=["'Any at all' is exactly what some answers.",
                           "Write nums.some((x) => x < 0)."]),
                _ex("tscourse-w6-fl-5", "All positive?",
                    "Print whether every number is greater than 0.",
                    _NUMS + 'console.log(nums.every((x) => x > 0));\n',
                    'nums.every((x) => x > 0)',
                    [("1 2 3", "true"), ("1 -2", "false")],
                    hints=["every requires all of them to pass.",
                           "Write nums.every((x) => x > 0)."]),
                _ex("tscourse-w6-fl-6", "Narrow then reshape",
                    "Keep the words longer than 3 characters, uppercase them, and join with `, `.",
                    _WORDS + 'console.log(words.filter((w) => w.length > 3).map((w) => w.toUpperCase()).join(", "));\n',
                    '.filter((w) => w.length > 3).map((w) => w.toUpperCase())',
                    [("hi there you all", "THERE"), ("abcd efgh", "ABCD, EFGH")],
                    hints=["Filter first so there is less to transform.",
                           "Chain .filter(...) then .map(...)."],
                    difficulty="Medium"),
                _fix("tscourse-w6-fl-fix1", "Fix filter vs map",
                     "This should COUNT the evens (3 of them) but always prints 6. Fix it.",
                     _NUMS + 'const evens = nums.map((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     _NUMS + 'const evens = nums.filter((x) => x % 2 === 0);\nconsole.log(evens.length);\n',
                     [("1 2 3 4 5 6", "3"), ("1 3 5", "0")],
                     hints=["map keeps every element, so its length never changes.",
                            "To keep only some, use filter."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("You need the first matching element. Best choice?",
                   ["filter(...)[0]", "find(...)", "some(...)", "map(...)"], 1,
                   "find says what you mean and stops at the first match."),
                _q("`arr.filter(p).length > 0` can be written as…",
                   ["arr.every(p)", "arr.some(p)", "arr.find(p)", "arr.map(p)"], 1,
                   "some asks exactly that question."),
                _q("`findIndex` returns what when nothing matches?",
                   ["undefined", "-1", "0", "null"], 1,
                   "Same sentinel as indexOf — and the same truthiness trap."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w6-sort", "Sorting",
            "Ordering a list — and the trap that catches everyone.",
            """
Start with the trap, because you will hit it:

```ts
[10, 9, 1].sort();      // [1, 10, 9]   ⚠️ not what you wanted
```

With no argument, `sort` converts every element to a **string** and orders them
alphabetically. As text, `"10"` really does come before `"9"`, because `1` comes
before `9`. This is not a bug; it's a default that suits words and ruins
numbers.

**Numbers need a comparator** — a function of two elements that returns a
number:

```ts
[10, 9, 1].sort((a, b) => a - b);    // [1, 9, 10]    ascending
[10, 9, 1].sort((a, b) => b - a);    // [10, 9, 1]    descending
```

The contract is:

| `compare(a, b)` returns | meaning |
|---|---|
| negative | `a` comes first |
| positive | `b` comes first |
| `0` | leave their order alone |

So `a - b` is negative exactly when `a` is smaller — ascending. Swap to `b - a`
for descending. You do not need to memorise more than that.

**Strings sort sensibly by default:**

```ts
["Cy", "Ada", "Bo"].sort();     // ["Ada", "Bo", "Cy"]
```

Though capitals sort before lowercase (`"Z" < "a"`), so normalise the case first
if that matters.

**`sort` mutates.** It reorders the array you called it on and returns that same
array — it does not hand you a sorted copy:

```ts
const a = [3, 1, 2];
const b = a.sort((x, y) => x - y);
console.log(a);          // [1,2,3]  ⚠️ a was reordered
console.log(b === a);    // true     — the same array
```

If the original matters, **copy first** — the idiom is worth memorising:

```ts
const sorted = [...a].sort((x, y) => x - y);
```

**`reverse` also mutates**, so the same rule applies: `[...a].reverse()`.

**Sorting by a field** is the everyday case, and it's the same comparator with
the field named:

```ts
[...people].sort((p, q) => p.age - q.age);
```

You'll use exactly this next week, on arrays of objects.

> ⚠️ **Common mistakes:** sorting numbers without a comparator; forgetting that
> `sort` mutates and then wondering why an earlier printout changed; and writing
> `(a, b) => a > b`, which returns a boolean where a number is required.
""",
            warmup=[
                _q("`[10, 9, 1].sort()` gives…",
                   ["[1,9,10]", "[1,10,9]", "[10,9,1]", "an error"], 1,
                   "Default sort compares as text."),
                _q("`[10, 9, 1].sort((a,b) => a - b)` gives…",
                   ["[1,9,10]", "[1,10,9]", "[10,9,1]", "[]"], 0, "Ascending numeric."),
                _q("`(a, b) => b - a` sorts…", ["ascending", "descending", "randomly",
                                                "alphabetically"], 1,
                   "The sign is flipped, so bigger comes first."),
                _q("After `a.sort(...)`, the array `a` is…",
                   ["unchanged", "reordered in place", "emptied", "copied"], 1,
                   "sort mutates — copy first if you need the original."),
            ],
            exercises=[
                _ex("tscourse-w6-so-1", "Sort ascending",
                    "Print the numbers in ascending order, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => a - b).join(" "));\n',
                    '(a, b) => a - b',
                    [("10 9 1", "1 9 10"), ("3 1 2", "1 2 3")],
                    hints=["Numbers need a comparator, or they sort as text.",
                           "Write (a, b) => a - b."]),
                _ex("tscourse-w6-so-2", "Sort descending",
                    "Print the numbers largest first, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => b - a).join(" "));\n',
                    '(a, b) => b - a',
                    [("1 9 10", "10 9 1"), ("3 1 2", "3 2 1")],
                    hints=["Flip the subtraction to reverse the order.",
                           "Write (a, b) => b - a."]),
                _ex("tscourse-w6-so-3", "Alphabetical",
                    "Print the words in alphabetical order, space-separated.",
                    _WORDS + 'console.log([...words].sort().join(" "));\n',
                    '[...words].sort()',
                    [("cy ada bo", "ada bo cy"), ("b a", "a b")],
                    hints=["Strings sort sensibly with no comparator at all.",
                           "Write [...words].sort()."]),
                _ex("tscourse-w6-so-4", "Keep the original",
                    "Print the sorted list, then the ORIGINAL list unchanged.",
                    _NUMS + 'const sorted = [...nums].sort((a, b) => a - b);\n'
                    'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                    'const sorted = [...nums].sort((a, b) => a - b);',
                    [("3 1 2", "1 2 3\n3 1 2"), ("2 1", "1 2\n2 1")],
                    hints=["sort mutates, so sort a copy.",
                           "Write const sorted = [...nums].sort((a, b) => a - b);"],
                    difficulty="Medium"),
                _ex("tscourse-w6-so-5", "The three smallest",
                    "Print the three smallest numbers in ascending order, space-separated.",
                    _NUMS + 'console.log([...nums].sort((a, b) => a - b).slice(0, 3).join(" "));\n',
                    '.slice(0, 3)',
                    [("5 3 9 1 7", "1 3 5"), ("2 1 4", "1 2 4")],
                    hints=["Sort ascending, then take the front of the list.",
                           "Chain .slice(0, 3)."],
                    difficulty="Medium"),
                _ex("tscourse-w6-so-6", "Second largest",
                    "Print the second largest number.",
                    _NUMS + 'console.log([...nums].sort((a, b) => b - a)[1]);\n',
                    '[...nums].sort((a, b) => b - a)[1]',
                    [("5 3 9 1", "5"), ("2 7", "2")],
                    hints=["Sort descending, then take index 1.",
                           "Write [...nums].sort((a, b) => b - a)[1]."],
                    difficulty="Medium"),
                _fix("tscourse-w6-so-fix1", "Fix the text sort",
                     "This should sort numbers ascending but gives `1 10 9`. Fix it.",
                     _NUMS + 'console.log([...nums].sort().join(" "));\n',
                     _NUMS + 'console.log([...nums].sort((a, b) => a - b).join(" "));\n',
                     [("10 9 1", "1 9 10"), ("100 20 3", "3 20 100")],
                     hints=["With no comparator, sort compares string forms.",
                            "Supply (a, b) => a - b."],
                     difficulty="Medium"),
                _fix("tscourse-w6-so-fix2", "Fix the clobbered original",
                     "The second line should print the ORIGINAL order but prints the sorted one. Fix it.",
                     _NUMS + 'const sorted = nums.sort((a, b) => a - b);\n'
                     'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                     _NUMS + 'const sorted = [...nums].sort((a, b) => a - b);\n'
                     'console.log(sorted.join(" "));\nconsole.log(nums.join(" "));\n',
                     [("3 1 2", "1 2 3\n3 1 2")],
                     hints=["sort reordered nums itself, and returned that same array.",
                            "Sort a copy: [...nums].sort(...)."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A comparator returning a negative number means…",
                   ["a comes first", "b comes first", "they are equal", "an error"], 0,
                   "Negative keeps a ahead of b."),
                _q("`(a, b) => a > b` as a comparator is wrong because…",
                   ["it is too slow", "it returns a boolean where a number is needed",
                    "it sorts descending", "it mutates"], 1,
                   "true/false convert to 1/0, so 'a comes first' can never be expressed."),
                _q("`[...a].sort()` rather than `a.sort()` because…",
                   ["it is faster", "sort mutates, and the copy protects the original",
                    "sort needs an array", "no reason"], 1,
                   "The spread makes a fresh array for sort to reorder."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w6-pipeline", "Chaining: building a pipeline",
            "split → filter → map → sort → slice → join, as one readable flow.",
            """
You have met `split`, `map`, `filter`, `sort` and `join` one at a time. Real
programs use them **together**, in a chain, because every one of them *returns a
new array* — so the next one can start where the last finished.

```ts
const raw = "5, 12, -3, 8, 20";

const top = raw
  .split(",")                     // ["5", " 12", " -3", " 8", " 20"]
  .map((s) => Number(s.trim()))   // [5, 12, -3, 8, 20]
  .filter((n) => n > 0)           // [5, 12, 8, 20]
  .sort((a, b) => b - a)          // [20, 12, 8, 5]
  .slice(0, 3);                   // [20, 12, 8]

console.log(top.join(" "));       // 20 12 8
```

Read a chain **top to bottom**: each line is one small, total transformation of
the whole list. That is much easier to hold in your head than one loop doing
five things at once.

**Order changes the answer.** These two are not the same program:

```ts
words.filter((w) => w.length > 3).map((w) => w.toUpperCase())   // test the raw value
words.map((w) => w.toUpperCase()).filter((w) => w.length > 3)   // test the mapped value
```

The rule of thumb: **filter first when the test works on the original value** —
you then do the expensive `map` on fewer items. Map first only when the test
needs the transformed value.

**`slice` is your "take" and your "copy".** `xs.slice(0, 3)` takes the first
three; a bare `xs.slice()` copies the whole array. That copy matters because
`sort` and `reverse` are the odd ones out — they **mutate in place** and return
the *same* array:

```ts
const scores = [88, 92, 79];
const ranked = scores.slice().sort((a, b) => b - a);   // copy first, then sort
console.log(scores.join(","));   // 88,92,79 — untouched
```

**`map` hands you the index too.** The callback's second parameter is the
position, which is how you number a list:

```ts
const names = ["ada", "alan"];
console.log(names.map((n, i) => `${i + 1}. ${n}`).join("\\n"));
// 1. ada
// 2. alan
```

**Name the middle when the chain gets long.** A chain of three is a sentence; a
chain of eight is a paragraph with no full stops. Break it:

```ts
const cleaned = lines.map((l) => l.trim()).filter((l) => l.length > 0);
const parsed = cleaned.map((l) => l.split(","));
```

Named steps also give you somewhere to put a `console.log` when the answer comes
out wrong — inspect `cleaned`, then `parsed`, and the broken stage announces
itself.

> ⚠️ **Common mistakes:** calling `filter` and throwing the result away (these
> methods never change the original — you must keep what they return); writing
> `(n) => { n > 0; }` with braces but no `return`, so every test is `undefined`
> and the result is empty; and sorting a shared array without copying it first.
""",
            warmup=[
                _q("`[1,2,3,4].filter((n) => n % 2 === 0).map((n) => n * 10)` gives…",
                   ["[10,20,30,40]", "[20,40]", "[2,4]", "[]"], 1,
                   "Filter keeps 2 and 4; map then multiplies each by 10."),
                _q("`nums.filter((n) => n > 0);` on its own line, then printing `nums`, shows…",
                   ["only the positives", "the original array unchanged", "an empty array", "an error"], 1,
                   "filter returns a NEW array; ignoring it changes nothing."),
                _q("`[1,2,3].map((n, i) => n * i)` gives…",
                   ["[1,2,3]", "[0,2,6]", "[0,1,2]", "[1,4,9]"], 1,
                   "The second parameter is the index: 1*0, 2*1, 3*2."),
                _q("Which method changes the array it is called on?",
                   ["map", "filter", "slice", "sort"], 3,
                   "sort (and reverse) mutate in place — copy with slice() first."),
            ],
            exercises=[
                _ex("tscourse-w6-pipe-1", "Filter, then map",
                    "Keep the even numbers, then multiply each by 10. Fill in the filtering stage.",
                    'const nums = [1, 2, 3, 4, 5, 6];\n'
                    'const result = nums.filter((n) => n % 2 === 0).map((n) => n * 10);\n'
                    'console.log(result.join(","));\n',
                    'filter((n) => n % 2 === 0)', [("", "20,40,60")],
                    hints=["A number is even when the remainder after dividing by 2 is 0.",
                           "Write filter((n) => n % 2 === 0)."]),
                _ex("tscourse-w6-pipe-2", "Map, then filter",
                    "The test needs the mapped value — the lengths — so map runs first. Add the filter that keeps lengths above 2.",
                    'const words = ["hi", "there", "ok", "friend"];\n'
                    'const lens = words.map((w) => w.length).filter((n) => n > 2);\n'
                    'console.log(lens.join(" "));\n',
                    '.filter((n) => n > 2)', [("", "5 6")],
                    hints=["After map you have [2, 5, 2, 6].",
                           "Chain .filter((n) => n > 2) onto the map."]),
                _ex("tscourse-w6-pipe-3", "Sort inside a chain",
                    "Read a comma-separated list, keep the positives, and print the three largest, biggest first. Add the sorting stage.",
                    _FS +
                    'const raw = fs.readFileSync(0, "utf8").trim();\n'
                    'const top = raw\n'
                    '  .split(",")\n'
                    '  .map((s) => Number(s.trim()))\n'
                    '  .filter((n) => n > 0)\n'
                    '  .sort((a, b) => b - a)\n'
                    '  .slice(0, 3);\n'
                    'console.log(top.join(" "));\n',
                    '.sort((a, b) => b - a)',
                    [("5, 12, -3, 8, 20, 1", "20 12 8"), ("3,1,2", "3 2 1"), ("-4, 7", "7")],
                    hints=["Descending order means the comparator subtracts the other way round.",
                           "Write .sort((a, b) => b - a)."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-4", "Name the middle",
                    "Lines are cleaned into `names`; now build `shouted` from it by upper-casing every name.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const names = lines.map((l) => l.trim()).filter((l) => l.length > 0);\n'
                    'const shouted = names.map((n) => n.toUpperCase());\n'
                    'console.log(shouted.join(", "));\n',
                    'names.map((n) => n.toUpperCase())',
                    [("ada\n  grace \n\nalan", "ADA, GRACE, ALAN"), ("solo", "SOLO")],
                    hints=["Start from the array the previous line named, not from `lines`.",
                           "Write names.map((n) => n.toUpperCase())."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-5", "Copy before you sort",
                    "Print the scores sorted ascending, then prove the original is untouched. Fill in the copy.",
                    'const scores = [88, 92, 79, 95, 61];\n'
                    'const sorted = scores.slice().sort((a, b) => a - b);\n'
                    'console.log(sorted.join(","));\n'
                    'console.log(scores.join(","));\n',
                    'scores.slice()', [("", "61,79,88,92,95\n88,92,79,95,61")],
                    hints=["sort rearranges the array it is given, so hand it a copy.",
                           "A bare slice() with no arguments copies the whole array."],
                    difficulty="Easy"),
                _ex("tscourse-w6-pipe-6", "Number the list",
                    "Print each name on its own line, numbered from 1. Use map's index parameter.",
                    'const names = ["ada", "alan", "grace"];\n'
                    'const numbered = names.map((n, i) => `${i + 1}. ${n}`);\n'
                    'console.log(numbered.join("\\n"));\n',
                    '(n, i) => `${i + 1}. ${n}`',
                    [("", "1. ada\n2. alan\n3. grace")],
                    hints=["The callback can take a second parameter: the index, counting from 0.",
                           "Add 1 to the index so the list starts at 1."],
                    difficulty="Medium"),
                _fix("tscourse-w6-pipe-fix1", "Fix the discarded result",
                     "This should print only the positive numbers, but prints all of them. The filtered array is being thrown away.",
                     'const nums = [3, -1, 4, -5, 9];\n'
                     'nums.filter((n) => n > 0);\n'
                     'console.log(nums.join(","));\n',
                     'const nums = [3, -1, 4, -5, 9];\n'
                     'const positive = nums.filter((n) => n > 0);\n'
                     'console.log(positive.join(","));\n',
                     [("", "3,4,9")],
                     hints=["filter never edits the array it is called on — it hands back a new one.",
                            "Store the returned array in a const and print that instead."]),
                _fix("tscourse-w6-pipe-fix2", "Fix the silent predicate",
                     "This should print 3 (the count of even numbers) but prints 0. The callback has braces but never returns.",
                     'const nums = [1, 2, 3, 4, 5, 6];\n'
                     'const evens = nums.filter((n) => { n % 2 === 0; });\n'
                     'console.log(evens.length);\n',
                     'const nums = [1, 2, 3, 4, 5, 6];\n'
                     'const evens = nums.filter((n) => n % 2 === 0);\n'
                     'console.log(evens.length);\n',
                     [("", "3")],
                     hints=["A braced arrow body needs an explicit return; without one every test is undefined.",
                            "Drop the braces so the expression is returned automatically."],
                     difficulty="Medium"),
                _fix("tscourse-w6-pipe-fix3", "Fix the mutated original",
                     "This should print the top score and then the original order, but sorting rearranged the array everyone shares.",
                     'const scores = [88, 92, 79];\n'
                     'const ranked = scores.sort((a, b) => b - a);\n'
                     'console.log(`Top: ${ranked[0]}`);\n'
                     'console.log(`Original: ${scores.join(",")}`);\n',
                     'const scores = [88, 92, 79];\n'
                     'const ranked = scores.slice().sort((a, b) => b - a);\n'
                     'console.log(`Top: ${ranked[0]}`);\n'
                     'console.log(`Original: ${scores.join(",")}`);\n',
                     [("", "Top: 92\nOriginal: 88,92,79")],
                     hints=["sort is one of the two array methods that change the array in place.",
                            "Insert a .slice() before the .sort(...) so it sorts a copy."],
                     difficulty="Medium"),
                _ch("tscourse-w6-pipe-ch1", "Leaderboard", "Medium",
                    "Each input line is `name,score`, and blank lines may appear. Build the pipeline: clean the lines, split each into fields, rank by score highest first, keep the top three, and number them as `1. name (score)`.",
                    _FS +
                    'const lines = fs.readFileSync(0, "utf8").trim().split("\\n");\n'
                    'const rows = lines\n'
                    '  .map((l) => l.trim())\n'
                    '  .filter((l) => l.length > 0)\n'
                    '  .map((l) => l.split(","));\n'
                    'const ranked = rows.sort((a, b) => Number(b[1]) - Number(a[1])).slice(0, 3);\n'
                    'const out = ranked.map((r, i) => `${i + 1}. ${r[0]} (${r[1]})`);\n'
                    'console.log(out.join("\\n"));\n',
                    'const rows = lines\n'
                    '  .map((l) => l.trim())\n'
                    '  .filter((l) => l.length > 0)\n'
                    '  .map((l) => l.split(","));\n'
                    'const ranked = rows.sort((a, b) => Number(b[1]) - Number(a[1])).slice(0, 3);\n'
                    'const out = ranked.map((r, i) => `${i + 1}. ${r[0]} (${r[1]})`);',
                    [("ada,91\ngrace,88\n\nalan,95\nedsger,70",
                      "1. alan (95)\n2. ada (91)\n3. grace (88)"),
                     ("bob,10\nsue,20", "1. sue (20)\n2. bob (10)")],
                    hints=["Four stages: trim each line, drop the empty ones, split each on the comma, then rank.",
                           "After the last map, each row is a two-element array: [name, score].",
                           "The score is text, so compare Number(b[1]) - Number(a[1]) for descending order.",
                           "slice(0, 3) takes the top three, and map's index gives you the numbering."]),
            ],
            quiz=[
                _q("Why can array methods be chained?",
                   ["they mutate in place", "each returns a new array for the next one to work on",
                    "TypeScript rewrites them", "they are asynchronous"], 1,
                   "map/filter/slice each hand back a fresh array."),
                _q("`filter` before `map` is usually preferred because…",
                   ["it reads better", "the map then runs on fewer items",
                    "map cannot come first", "filter is faster than map"], 1,
                   "Unless the test needs the mapped value, shrink the list first."),
                _q("`xs.slice()` with no arguments…",
                   ["empties the array", "copies the whole array", "sorts it", "is an error"], 1,
                   "Which is exactly how you protect an array from an in-place sort."),
                _q("A long chain is worth breaking into named steps because…",
                   ["it runs faster", "you get somewhere to inspect the middle when it goes wrong",
                    "chains are limited to three calls", "TypeScript requires it"], 1,
                   "Named stages turn debugging into reading."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #6 — the month in numbers",
        """
Budget Buddy finally sees a whole month at once. The input is a line of
expense amounts:

```
12 3 45 7 3 20
```

Print a six-line summary:

```
Count:    6
Total:    $90.00
Average:  $15.00
Largest:  $45.00
Smallest: $3.00
Top 3:    45, 20, 12
```

Rules:

- Money is shown to two decimal places.
- `Top 3` is the three largest amounts, largest first, joined with `, `. If
  there are fewer than three, show all of them.
- The input array must be left **unsorted** — sort copies, not the original.
""",
        _ch("tscourse-w6-capstone", "Budget Buddy #6", "Medium",
            "Compute the six statistics and print them.",
            _NUMS +
            'let total = 0;\n'
            'for (const x of nums) {\n  total += x;\n}\n'
            'const desc = [...nums].sort((a, b) => b - a);\n'
            'console.log(`Count:    ${nums.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Average:  $${(total / nums.length).toFixed(2)}`);\n'
            'console.log(`Largest:  $${desc[0]!.toFixed(2)}`);\n'
            'console.log(`Smallest: $${desc[desc.length - 1]!.toFixed(2)}`);\n'
            'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);\n',
            'let total = 0;\n'
            'for (const x of nums) {\n  total += x;\n}\n'
            'const desc = [...nums].sort((a, b) => b - a);\n'
            'console.log(`Count:    ${nums.length}`);\n'
            'console.log(`Total:    $${total.toFixed(2)}`);\n'
            'console.log(`Average:  $${(total / nums.length).toFixed(2)}`);\n'
            'console.log(`Largest:  $${desc[0]!.toFixed(2)}`);\n'
            'console.log(`Smallest: $${desc[desc.length - 1]!.toFixed(2)}`);\n'
            'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);',
            [("12 3 45 7 3 20",
              "Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12"),
             ("10", "Count:    1\nTotal:    $10.00\nAverage:  $10.00\nLargest:  $10.00\nSmallest: $10.00\nTop 3:    10"),
             ("5 1", "Count:    2\nTotal:    $6.00\nAverage:  $3.00\nLargest:  $5.00\nSmallest: $1.00\nTop 3:    5, 1")],
            hints=["Total needs a loop and an accumulator — reduce arrives in week 8.",
                   "Sort a COPY descending once, and read largest, smallest and the top three off it.",
                   "The smallest is the last element of the descending copy: desc[desc.length - 1]!.",
                   'Top 3 is desc.slice(0, 3).join(", ") — slice happily returns fewer if there are fewer.']),
        example_io="Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12",
        rubric=["Count, total, average, largest and smallest are all computed from the array",
                "Money values carry two decimal places",
                "Top 3 is sorted descending and joined with a comma and a space",
                "The original array is never mutated — sorting happens on a copy"],
        stretch=_ch("tscourse-w6-capstone-stretch", "Budget Buddy #6 (stretch)", "Medium",
                    "Add a seventh line, `Over avg: <n>`, counting how many amounts are strictly above the average.",
                    _NUMS +
                    'let total = 0;\n'
                    'for (const x of nums) {\n  total += x;\n}\n'
                    'const avg = total / nums.length;\n'
                    'const desc = [...nums].sort((a, b) => b - a);\n'
                    'console.log(`Count:    ${nums.length}`);\n'
                    'console.log(`Total:    $${total.toFixed(2)}`);\n'
                    'console.log(`Average:  $${avg.toFixed(2)}`);\n'
                    'console.log(`Largest:  $${desc[0]!.toFixed(2)}`);\n'
                    'console.log(`Smallest: $${desc[desc.length - 1]!.toFixed(2)}`);\n'
                    'console.log(`Top 3:    ${desc.slice(0, 3).join(", ")}`);\n'
                    'console.log(`Over avg: ${nums.filter((x) => x > avg).length}`);\n',
                    'console.log(`Over avg: ${nums.filter((x) => x > avg).length}`);',
                    [("12 3 45 7 3 20",
                      "Count:    6\nTotal:    $90.00\nAverage:  $15.00\nLargest:  $45.00\nSmallest: $3.00\nTop 3:    45, 20, 12\nOver avg: 2"),
                     ("5 1", "Count:    2\nTotal:    $6.00\nAverage:  $3.00\nLargest:  $5.00\nSmallest: $1.00\nTop 3:    5, 1\nOver avg: 1")],
                    hints=["Name the average once so both the printout and the count can use it.",
                           "Counting matches is filter then .length.",
                           "Write nums.filter((x) => x > avg).length."]),
    ),
))
