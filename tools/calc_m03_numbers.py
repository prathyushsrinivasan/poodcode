# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 3 — Numbers, and tokens longer than one character.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 2's `_C_TOKENS`, `_C2_MAIN` and the
# `_toks` expected-output helper.
#
# THE FIRST LOOKAHEAD. Module 2's digit branch consumed one character, so `12`
# was two tokens. The fix is the shape every multi-character token uses from now
# on — remember where it started, advance while the next character still
# belongs, cut the run out — and module 2 already made it possible by having
# every branch move its own cursor.
#
# `.slice(` AND `Number(` ARRIVE HERE, and `Number` cannot fail on what it is
# given: the scanner only ever hands it a run of digits. Step 2 says so, and
# says where that stops being true (a decimal point, a sign — both stretch).
#
# THE GUARD ORDER IS THE MODULE'S TRAP. `isDigit` is `DIGITS.indexOf(ch) !== -1`,
# and `DIGITS.indexOf("")` is 0 — so `isDigit("")` is TRUE. The inner loop reads
# `i < src.length && isDigit(src.charAt(i))`, and the length check must come
# first: reversed or dropped, the loop runs forever on any input that ends in a
# digit. A hang costs a timeout per run, so it is taught in prose and pitfalls,
# never graded (see PROJECTS_ROADMAP.md, "Related: a bug whose symptom is a
# hang").
#
# STILL WRONG, AND GRADED: `1 $ 2` drops the `$`. Module 4's.
# ---------------------------------------------------------------------------

_C3_SCAN = """const DIGITS = "0123456789";

function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}

function scan(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    const ch = src.charAt(i);
    if (ch === " ") {
      i = i + 1;
    } else if (isDigit(ch)) {
      const start = i;
      while (i < src.length && isDigit(src.charAt(i))) {
        i = i + 1;
      }
      const text = src.slice(start, i);
      tokens.push(numberToken(Number(text)));
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      tokens.push(opToken(ch));
      i = i + 1;
    } else {
      i = i + 1;
    }
  }
  tokens.push(eofToken());
  return tokens;
}
"""


def _c3(scan=_C3_SCAN):
    return _stdin("\n\n".join(p.rstrip("\n") for p in (_C_TOKENS, scan, _C2_MAIN)))


_C3_FULL = _c3()

_C3_SCAN_TESTS = [
    ("12 + 345", _toks(12, "+", 345)),
    ("7", _toks(7)),
    ("10/4", _toks(10, "/", 4)),
    ("2 * 30 - 100", _toks(2, "*", 30, "-", 100)),
    ("007", _toks(7)),
    ("", _CEOF),
]

# --- Step 1's plain program: cutting runs out of a string -------------------
_C3_S1_PRINTS = """
const src = "12 + 345";
console.log(src.slice(0, 2));
console.log(src.slice(5, 8));
console.log(src.slice(3, 4));
console.log(src.slice(5));
console.log(JSON.stringify(src.slice(2, 2)));
console.log(src.slice(0, 2) + src.slice(5, 8));
"""
_C3_S1_OUT = '12\n345\n+\n345\n""\n12345'

# --- Step 2's plain program: text to number ---------------------------------
_C3_S2_BODY = """
function toNumber(digits: string): number {
  return Number(digits);
}

console.log(toNumber("12") + 1);
console.log(toNumber("345") * 2);
console.log(toNumber("007"));
console.log(toNumber("0"));
console.log(JSON.stringify(numberToken(toNumber("42"))));
"""
_C3_S2_OUT = '13\n690\n7\n0\n{"kind":"number","value":42}'


def _c3_s2(body=_C3_S2_BODY):
    return _plain(_C_TOKENS + "\n" + body.lstrip("\n"))


_C3_WHY = (
    "Module 2's scanner reads one character per token, so it reads one digit per "
    "number: `12` comes out as a 1 and a 2, and no calculator worth the name "
    "can add twelve to anything. The fix is not a special case for two-digit "
    "numbers. It is the shape every token longer than one character will use for "
    "the rest of the project — remember where it started, keep going while the "
    "next character still belongs to it, and cut the whole run out at once."
)

_C3_BRIEF = """
### The whole module in one line

Scan `123` as one number token carrying the value 123, not three tokens carrying
1, 2 and 3.

### The shape: start, advance, cut

```ts
const start = i;                                     // 1. remember where it began
while (i < src.length && isDigit(src.charAt(i))) {   // 2. advance while it continues
  i = i + 1;
}
const text = src.slice(start, i);                    // 3. cut the run out
tokens.push(numberToken(Number(text)));              //    and make it a number
```

This is the project's first **lookahead**: the scanner has to look past the
current character to know where the token ends. Every multi-character token a
language has — numbers, names, `==`, `let`, string literals — is these three
lines with a different condition in the middle. Module 12 will use it for
variable names without changing its shape at all.

### Why module 2 already made room for it

Module 2 put `i = i + 1` in every branch rather than once at the bottom of the
loop, and said it was for this module. Here is why: the number branch no longer
moves the cursor by one. It moves it by however many digits there are — and the
inner `while` has already done that by the time the branch ends. A loop that
always added one at the bottom would skip the character after every number.

### Two new tools

`src.slice(start, end)` cuts a piece out of a string. `Number(text)` turns
`"123"` into `123`. Steps 1 and 2 take one each.

### What is still wrong

`1 $ 2` still loses its `$` without a word. That is module 4's, and after this
module it is the scanner's only wrong answer.
"""

_C3_SYNTAX = [
    _syn(
        "const text = src.slice(start, i);",
        "The piece of `src` from position `start` up to — but **not including** — "
        "position `i`. A new string; `src` is untouched.",
        """
const src = "12 + 345";
src.slice(0, 2);    // "12"
src.slice(5, 8);    // "345"
src.slice(5);       // "345" — to the end
""",
        "The end is **exclusive**. That is what makes `slice(start, i)` exactly "
        "right after the inner loop: `i` is the first position that is *not* a "
        "digit, so it is the right place to stop.",
    ),
    _syn(
        "Number(text)",
        "Turn a string of digits into the number it spells. `Number(\"123\")` is "
        "`123`.",
        """
Number("12") + 1;    // 13 — not "121"
Number("007");       // 7
""",
        "On anything that is not a number it answers `NaN` rather than failing — "
        "`Number(\"12+\")` is `NaN`, and `JSON.stringify` writes `NaN` as `null`. "
        "The scanner only ever hands it a run of digits, so here it cannot "
        "happen. Keep it that way.",
    ),
    _syn(
        "function isDigit(ch: string): boolean { … }",
        "Module 2's `indexOf` test with a name. The scanner now asks \"is this a "
        "digit?\" in two places, and the name keeps both asking the same thing.",
        """
function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}
""",
        "`isDigit(\"\")` is **true**, because `DIGITS.indexOf(\"\")` is 0. Never "
        "call it on a position past the end — which is exactly what the "
        "`i < src.length &&` in front of it prevents.",
    ),
    _syn(
        "while (i < src.length && isDigit(src.charAt(i))) { … }",
        "Advance while the cursor is inside the text **and** the character there "
        "is a digit. The first `false` ends the loop.",
        "",
        "Order matters. `&&` stops at the first `false`, so the length check runs "
        "first and `isDigit` is never asked about `\"\"`. Reverse them — or drop "
        "the length check — and an input ending in a digit loops forever.",
    ),
    _syn(
        "const start = i;",
        "Remember where the token began, before the cursor moves. The inner loop "
        "is about to change `i`, and this is the only record of where it was.",
        "",
        "Take it *before* moving the cursor. One `i = i + 1` ahead of it and "
        "every number loses its first digit.",
    ),
    _syn(
        "const src = readFileSync(0, \"utf8\").trim();",
        "Module 2's read of stdin, unchanged.",
        "",
        "",
        recap=True,
    ),
    _syn(
        "const ch = src.charAt(i);",
        "Module 2's character read — a `string`, `\"\"` past the end.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — cutting a piece out of the text.
# ---------------------------------------------------------------------------

_C3_S1 = _pstep(
    "slice", "Cutting a piece out of the text",
    "`slice(start, end)`, and why the end is exclusive.",
    """
`12 + 345` contains two numbers, and each one is a **run** of characters. Before
any scanning, you need a way to get a run out of a string:

```ts
const src = "12 + 345";
//           01234567      ← positions

src.slice(0, 2)    // "12"
src.slice(5, 8)    // "345"
src.slice(3, 4)    // "+"
```

`slice(start, end)` hands back the characters from `start` up to, **but not
including**, `end`. It makes a new string and leaves `src` exactly as it was.

### Why the end is exclusive

It looks like an off-by-one waiting to happen, and it is the opposite: it is the
convention that makes the arithmetic come out without `+ 1`s.

* The length of the piece is `end - start`. `slice(5, 8)` is 3 characters.
* Two pieces that meet share a number: `slice(0, 2)` and `slice(2, 4)` touch
  exactly, with nothing lost or doubled.
* `slice(i, i)` is `""` — an empty piece — rather than an error.

And it fits the scanner precisely. When the inner loop in step 3 stops, `i` is
the first position that is **not** part of the number. That is exactly where the
slice should end — so `slice(start, i)` with no adjustment at all.

### Leaving off the end

`src.slice(5)` means "from 5 to the end". Handy, and not what a scanner wants: a
number is not the rest of the line.
""",
    """
Your program cuts these out of `12 + 345`:

```
slice(0, 2)    12
slice(5, 8)    345
slice(3, 4)    +
slice(5)       345
slice(2, 2)    ""
```

and joins the first two to make `12345` — two strings glued together, not a sum.
Step 2 is what makes them numbers.
""",
    pitfalls=[
        "Treating the end as inclusive: `src.slice(0, 1)` for `\"12\"`. You get `\"1\"`. The end is the first position you do *not* want.",
        "Confusing `slice` with `splice`, an array method that removes elements. `slice` only ever copies; it never changes the string.",
        "Expecting `slice` to error on a bad range. `slice(5, 2)` is `\"\"`, silently — so an off-by-one shows up as a missing token, not a crash.",
        "Adding two slices and expecting a sum. `\"12\" + \"345\"` is `\"12345\"`; strings join. Numbers need step 2.",
    ],
    warmup=[
        _pq("`\"12 + 345\".slice(5, 8)` — what is it?",
            ["`\"345\"` — positions 5, 6 and 7; the end is not included",
             "`\"345 \"`",
             "`\" 34\"`",
             "`\"+ 34\"`"],
            0,
            "Three characters, because 8 − 5 is 3. The exclusive end makes the "
            "length a subtraction."),
    ],
    exercises=[
        _pex("calc-m3-slice-1", "Cut out the first number",
             "Print the first number in `12 + 345` — the two characters at "
             "positions 0 and 1.",
             _plain(_C3_S1_PRINTS),
             "console.log(src.slice(0, 2));",
             [("", _C3_S1_OUT)],
             ["`slice` takes where to start and where to stop.",
              "Stop is the first position you do *not* want — the space at 2.",
              "`console.log(src.slice(0, 2));`"]),
        _pfix("calc-m3-slice-fix1", "A number missing its last digit",
              "The second line should be `345`. It prints `34`. The last line, "
              "which glues the two numbers together, prints `1234` instead of "
              "`12345`.",
              _plain(_C3_S1_PRINTS.replace("src.slice(5, 8)", "src.slice(5, 7)")),
              _plain(_C3_S1_PRINTS),
              [("", _C3_S1_OUT)],
              ["`345` sits at positions 5, 6 and 7. Where should the slice stop?",
               "The end position is not included.",
               "`src.slice(5, 8)` — in both places."],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("After the inner loop, `i` is the first position that is not a digit. Why is `slice(start, i)` exactly right?",
            ["The end of a slice is exclusive, so stopping at the first non-digit takes every digit and nothing else",
             "It is not — it should be `slice(start, i + 1)`",
             "Because `slice` ignores non-digits",
             "Because `i` points at the last digit"],
            0,
            "The convention and the loop agree. That is why the slice needs no "
            "`+ 1`, and why adding one is a bug."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — text becomes a number.
# ---------------------------------------------------------------------------

_C3_S2 = _pstep(
    "number", "Text becomes a number",
    "`Number`, the `NaN` it answers instead of failing, and why the scanner never sees one.",
    """
`slice` gives you `"12"`. A number token carries a `number`, and
`numberToken("12")` does not compile. One call converts it:

```ts
Number("12")         // 12
Number("12") + 1     // 13     — arithmetic
"12" + 1             // "121"  — joining, because "12" is text
```

That last pair is the whole reason the conversion matters. Text that *looks*
like a number joins rather than adds, and the bug is silent.

### `Number` never fails

Give it something that is not a number and it answers `NaN` — *not a number* —
which is, awkwardly, of type `number`, so the compiler has nothing to say:

```ts
Number("12+")    // NaN
Number("abc")    // NaN
JSON.stringify({ value: NaN })    // {"value":null}   ← and NaN prints as null
```

In most programs that means every `Number` call needs a check afterwards. **In
this scanner it does not**, and it is worth being precise about why: the text
handed to `Number` is always a run the inner loop accepted, and the inner loop
accepts only digits. A run of digits always spells a number.

That is a guarantee the *scanner* makes, not one `Number` makes. The day the
number branch accepts a `.` or a leading `-`, the guarantee is gone and a check
comes back. Both of those are in the stretch list, and the second one is
harder than it looks — module 8 has to decide whether `-3` is one token or two.

### `007`

`Number("007")` is `7`. Leading zeros are dropped, which is what a calculator
should do.
""",
    """
```
Number("12") + 1    13
Number("345") * 2   690
Number("007")       7
```

and a number token built from text:

```
{"kind":"number","value":42}
```

— with `42` as a JSON number, not `"42"` in quotes.
""",
    pitfalls=[
        "Pushing the slice itself: `numberToken(text)`. The compiler refuses — `text` is a `string` — which is the compiler doing its job.",
        "Adding before converting: `\"12\" + 1` is `\"121\"`. Strings join. Convert first, then do arithmetic.",
        "Trusting `Number` to fail loudly. It answers `NaN`, which is a `number`, and `JSON.stringify` prints it as `null`. A `null` value in a token means the slice took something that was not a digit.",
        "`parseInt(text)`. It reads `\"12+\"` as 12 — it stops at the first character it cannot read and keeps what it has — so a slice that ran one too far goes unnoticed instead of showing up as `null`.",
    ],
    warmup=[
        _pq("What is `\"12\" + 1`?",
            ["`\"121\"` — a string plus anything joins",
             "`13`",
             "`NaN`",
             "A compile error"],
            0,
            "Which is why the slice has to become a `number` before any "
            "arithmetic sees it."),
    ],
    exercises=[
        _pex("calc-m3-number-1", "Digits to a number",
             "`toNumber` receives a run of digits as text. Hand back the number "
             "it spells.",
             _c3_s2(),
             "  return Number(digits);",
             [("", _C3_S2_OUT)],
             ["One built-in call turns text into a number.",
              "The first test adds 1 to the result and expects 13 — not \"121\".",
              "`return Number(digits);`"]),
    ],
    quiz=[
        _pq("Why does the scanner never need to check `Number(text)` for `NaN`?",
            ["`text` is always a run the inner loop accepted, and it accepts only digits — so it always spells a number",
             "`Number` never returns `NaN`",
             "`numberToken` rejects `NaN`",
             "Because the compiler checks it"],
            0,
            "The guarantee belongs to the scanner's loop, not to `Number`. Change "
            "what the loop accepts and the guarantee goes with it."),
        _pq("`JSON.stringify({ value: NaN })` — what does it print?",
            ["`{\"value\":null}`",
             "`{\"value\":NaN}`",
             "`{}`",
             "It throws"],
            0,
            "JSON has no `NaN`. So a `null` where a number should be is how a bad "
            "slice shows up in this project's output."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the run.
# ---------------------------------------------------------------------------

_C3_S3 = _pstep(
    "run", "Reading the whole run",
    "The lookahead: start, advance while it is still a digit, cut — and the guard that must come first.",
    """
Now the three pieces go together, inside the scanner's digit branch:

```ts
} else if (isDigit(ch)) {
  const start = i;
  while (i < src.length && isDigit(src.charAt(i))) {
    i = i + 1;
  }
  const text = src.slice(start, i);
  tokens.push(numberToken(Number(text)));
}
```

Walk `12 + 345` through it. The outer loop is at position 0, on a `1`.

| | `i` | `src.charAt(i)` | digit? |
|---|---|---|---|
| `start = i` | 0 | `1` | |
| inner loop | 0 → 1 | `1` | yes, advance |
| inner loop | 1 → 2 | `2` | yes, advance |
| inner loop | 2 | ` ` | **no — stop** |
| `slice(0, 2)` | | | `"12"` |

The inner loop leaves `i` on the space, the first character that is not part of
the number. The branch ends **without** an `i = i + 1` of its own — the inner
loop has already moved the cursor exactly as far as it should. The outer loop
picks up at the space and carries on.

### `isDigit`, named

`DIGITS.indexOf(ch) !== -1` is asked twice now — once to enter the branch and
once per step of the inner loop — so it gets a name:

```ts
function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}
```

### The guard that has to come first

```ts
while (i < src.length && isDigit(src.charAt(i)))
```

`&&` stops at the first `false`. So when the number is at the very end of the
input, the length check fails first and `isDigit` is never called.

Now recall module 2's trap: `charAt` past the end is `""`, and
`DIGITS.indexOf("")` is `0`. So **`isDigit("")` is `true`**. Drop the length
check, or put it second, and on any input ending in a digit the inner loop reads
`""` past the end, decides it is a digit, advances, reads `""` again — and never
stops. No error. The program just never finishes.

That is not graded here, because a program that never finishes costs a timeout
on every run. It is the single most likely way to break this module, and the
place to look first when `calc.ts` hangs.
""",
    """
```
$ echo '12 + 345' | node calc.ts
{"kind":"number","value":12}
{"kind":"op","op":"+"}
{"kind":"number","value":345}
{"kind":"eof"}

$ echo '10/4' | node calc.ts
{"kind":"number","value":10}
{"kind":"op","op":"/"}
{"kind":"number","value":4}
{"kind":"eof"}
```

`10/4` has no spaces: the inner loop stops on the `/` itself, and the outer loop
reads it next as an operator.
""",
    pitfalls=[
        "Reversing the guard: `isDigit(src.charAt(i)) && i < src.length`. `isDigit(\"\")` is true, so on an input ending in a digit the loop never stops. The same if the length check is missing.",
        "Taking `start` after the first move: every number loses its first digit — `123` scans as `23`.",
        "`slice(start, i + 1)`. The slice takes one character too many — a space, which `Number` happens to ignore, or an operator, which makes it `NaN` and prints as `null`.",
        "Adding `i = i + 1` after the inner loop. The inner loop already stopped *on* the next character; one more step skips it, so `12+3` loses its `+`.",
        "Scanning a number as a digit and then \"carrying\" into the previous token. It can be made to work, and it is the hard version of three lines.",
    ],
    warmup=[
        _pq("Why must `i < src.length` come before `isDigit(src.charAt(i))`?",
            ["`&&` stops at the first false, and `isDigit(\"\")` is true — past the end the loop would never stop",
             "It is only a style choice",
             "`charAt` throws past the end",
             "Because `isDigit` is slower"],
            0,
            "`charAt` answers `\"\"` past the end, and `\"\"` is found at position "
            "0 of `DIGITS`. The length check is the only thing standing between "
            "the scanner and an endless loop."),
    ],
    exercises=[
        _pex("calc-m3-run-1", "Keep going while it is a digit",
             "Write the inner loop's condition: the cursor is still inside the "
             "text, and the character there is a digit. Guard first.",
             _C3_FULL,
             "i < src.length && isDigit(src.charAt(i))",
             _C3_SCAN_TESTS,
             ["Two conditions joined by `&&`.",
              "The first keeps the cursor inside the text.",
              "The second asks `isDigit` about the character at the cursor — and must come second.",
              "`i < src.length && isDigit(src.charAt(i))`"]),
        _pfix("calc-m3-run-fix1", "123 comes out as 23",
              "Every number is scanned as one token — the loop works — but it is "
              "missing its first digit. `12 + 345` gives `2` and `45`. And `7` "
              "gives `0` — a number that was never in the text.",
              _c3(_C3_SCAN.replace(
                  """      const start = i;
      while""",
                  """      i = i + 1;
      const start = i;
      while""")),
              _C3_FULL,
              _C3_SCAN_TESTS,
              ["Where does the cursor point when `start` is recorded?",
               "For `7` the slice is empty — and `Number(\"\")` is 0.",
               "Record `start` before anything moves the cursor.",
               "Delete the `i = i + 1;` above `const start = i;`."],
              difficulty="Easy"),
        _pfix("calc-m3-run-fix2", "A number that is null",
              "`10/4` gives `{\"kind\":\"number\",\"value\":null}` for the ten. "
              "And yet `12 + 345` and `2 * 30 - 100` scan perfectly — which is "
              "the confusing part, and the clue.",
              _c3(_C3_SCAN.replace("src.slice(start, i)", "src.slice(start, i + 1)")),
              _C3_FULL,
              _C3_SCAN_TESTS,
              ["`null` in JSON is how `NaN` prints. What text did `Number` get?",
               "For `10/4` the slice is `\"10/\"` — one character too many. Where the extra character is a space, `Number` quietly ignores it, which is why the other inputs pass.",
               "When the inner loop stops, `i` is already the first non-digit — and a slice's end is exclusive.",
               "`src.slice(start, i)`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does the number branch have no `i = i + 1` of its own?",
            ["The inner loop has already moved the cursor past every digit — one more step would skip the next character",
             "Because numbers are never followed by anything",
             "It should have one; it is a bug",
             "Because `slice` moves the cursor"],
            0,
            "This is what module 2's \"every branch moves the cursor itself\" was "
            "for: this branch moves it by the length of the number."),
        _pq("An input ends in a digit and the length check is missing from the inner loop. What happens?",
            ["The program never finishes — `isDigit(\"\")` is true, so the loop keeps advancing past the end",
             "The last digit is dropped",
             "It throws a RangeError",
             "Nothing; `charAt` stops it"],
            0,
            "Two innocent facts from module 2 — `charAt` past the end is `\"\"`, "
            "`indexOf(\"\")` is 0 — combine into a loop with no way out."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the whole scanner.
# ---------------------------------------------------------------------------

_C3_S4 = _pstep(
    "scanner", "Every token the calculator needs",
    "The scanner, whole — and the one wrong answer it has left.",
    """
```ts
function scan(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    const ch = src.charAt(i);
    if (ch === " ") {
      i = i + 1;
    } else if (isDigit(ch)) {
      const start = i;
      while (i < src.length && isDigit(src.charAt(i))) {
        i = i + 1;
      }
      const text = src.slice(start, i);
      tokens.push(numberToken(Number(text)));
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      tokens.push(opToken(ch));
      i = i + 1;
    } else {
      i = i + 1;
    }
  }
  tokens.push(eofToken());
  return tokens;
}
```

Read the four branches as four rules about how far the cursor moves:

| Branch | Consumes |
|---|---|
| space | 1 character |
| number | as many as the number has |
| operator | 1 character |
| anything else | 1 character — and says nothing |

That table is the scanner. Module 12 will add a row for names (`x`, `total`), and
it will be the number row with a different test in the middle.

### This is phase 1's promise, nearly

The phase's outcome line reads: *`1 + 2 * 3` becomes a list of tokens you can
print — and `1 $ 2` becomes an error that says which character and where.* The
first half is now true for every input the calculator will ever accept. The
second half is the last row of that table, and it is module 4's.

### Why nothing in the tests has a decimal point

`2.5` scans as `2`, then the `.` is skipped, then `5`. The calculator will still
*produce* `2.5` — module 9 evaluates `10 / 4` — but it cannot *read* one yet.
That is a deliberate scope decision, not an oversight; the stretch list has the
change, and it is where `Number` starts needing a check again.
""",
    """
```bash
$ echo '2 * 30 - 100' | node calc.ts
{"kind":"number","value":2}
{"kind":"op","op":"*"}
{"kind":"number","value":30}
{"kind":"op","op":"-"}
{"kind":"number","value":100}
{"kind":"eof"}
```

Every number, whatever its length, is one token.
""",
    pitfalls=[
        "Keeping module 2's `DIGITS.indexOf(ch)` value as the token's value. It is the first digit's value only — `12` becomes a token carrying 1.",
        "Moving the cursor at the bottom of the outer loop as well. Every token then eats the character after it.",
        "Treating `-` in `-3` as part of the number. The scanner cannot know yet whether `-` means minus or negative; module 8 decides that in the parser, where there is enough context to.",
        "Assuming the `else` branch is finished. It still hides every character it does not know. Module 4.",
    ],
    warmup=[
        _pq("How far does the cursor move when the scanner meets `345`?",
            ["Three characters — the inner loop advances once per digit, then the branch ends",
             "One character, like every other branch",
             "To the end of the input",
             "Four characters, including the space"],
            0,
            "Each branch consumes its own token's characters. The number branch "
            "is the first where that is more than one."),
    ],
    exercises=[
        _pch("calc-m3-scanner-build", "The number branch", "Medium",
             "Write the digit branch of the scanner: remember where the number "
             "starts, advance while the cursor is inside the text and on a digit, "
             "cut the run out, and push a number token carrying its value.",
             _C3_FULL,
             """      const start = i;
      while (i < src.length && isDigit(src.charAt(i))) {
        i = i + 1;
      }
      const text = src.slice(start, i);
      tokens.push(numberToken(Number(text)));""",
             _C3_SCAN_TESTS,
             ["Four things in order: `start`, the inner loop, the slice, the push.",
              "The inner loop's condition checks the length before calling `isDigit`.",
              "`src.slice(start, i)` — `i` is already on the first non-digit.",
              "No `i = i + 1` at the end of this branch: the inner loop did the moving."]),
    ],
    quiz=[
        _pq("After this module, which input does the scanner still get wrong?",
            ["`1 $ 2` — the `$` is dropped without a word; module 4 makes it an error",
             "`12`",
             "`10/4`",
             "The empty input"],
            0,
            "One wrong answer left in phase 1, and it is the one about what the "
            "language says when it cannot read you."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C3_FINAL = _pch(
    "calc-m3-build", "Module 3 build — numbers of any length", "Medium",
    "Write `DIGITS`, `isDigit` and `scan`.\n\n"
    "* `isDigit(ch)` — whether `ch` is one of the ten digits\n"
    "* `scan(src)` — module 2's scanner, except that a run of digits is one "
    "number token carrying the value the run spells\n\n"
    "Eight inputs. The last still drops its `$` — module 4's to fix — and is "
    "graded as what the scanner does today.",
    _C3_FULL,
    _C3_SCAN.rstrip("\n"),
    _C3_SCAN_TESTS + [
        ("1 2", _toks(1, 2)),
        ("40 $ 2", _toks(40, 2)),
    ],
    ["`isDigit` is `DIGITS.indexOf(ch) !== -1` — and remember `isDigit(\"\")` is true.",
     "The digit branch: `const start = i;`, an inner `while` guarded by `i < src.length` first, then `slice(start, i)`.",
     "`Number(text)` makes the value. The inner loop only accepts digits, so it cannot be `NaN`.",
     "The number branch has no `i = i + 1` of its own; every other branch still has one.",
     "`1 2` is two numbers — the space ends the first run."],
)


_CALC_MODULES.append(_pmod(
    key="calc-numbers", number=3, phase="scan",
    title="Numbers, and tokens longer than one character",
    what="a run of digits is one token, not five",
    goal="Scan `123` as a single number token carrying the value 123.",
    why=_C3_WHY,
    est_minutes=40,
    builds_on=["calc-token", "calc-scan"],
    concepts=["lookahead", "slice", "exclusive end", "Number", "NaN",
              "short-circuit &&", "guard order"],
    deliverable="A scanner that reads numbers of any length — every token the "
                "calculator needs, with one wrong answer left.",
    objectives=[
        "Cut a run out of a string with `slice(start, end)`, and explain why the end is exclusive",
        "Turn a run of digits into a number with `Number`, and say what `\"12\" + 1` is instead",
        "Say why `Number` cannot answer `NaN` inside this scanner, and what change would end that guarantee",
        "Write the start / advance / cut shape for a multi-character token",
        "Explain why the length check comes first in the inner loop, using what `isDigit(\"\")` returns",
        "Say why the number branch moves the cursor by the number's length, and why module 2 already allowed for it",
    ],
    brief=_C3_BRIEF,
    syntax=_C3_SYNTAX,
    steps=[_C3_S1, _C3_S2, _C3_S3, _C3_S4],
    final_build=_C3_FINAL,
    acceptance=[
        "`echo '12 + 345' | node calc.ts` prints number 12, op +, number 345, eof.",
        "`echo '10/4' | node calc.ts` prints number 10, op /, number 4, eof — the `/` right after a number is still read.",
        "`echo '007' | node calc.ts` prints one number token with value 7.",
        "No input prints a token with `\"value\":null`.",
        "An input ending in a digit — `echo '1 + 23'` — finishes rather than hanging.",
        "`echo '1 $ 2' | node calc.ts` still drops the `$` — and you can say it is module 4's.",
    ],
    manual_test="""
With `calc.ts` saved:

```bash
echo '12 + 345'       | node calc.ts
echo '10/4'           | node calc.ts     # no spaces — the / ends the 10
echo '2 * 30 - 100'   | node calc.ts
echo '007'            | node calc.ts     # 7
echo '1 2'            | node calc.ts     # two numbers — the space ends the run
```

Then the hang the module warned about, on purpose. In the inner loop, change
`i < src.length && isDigit(src.charAt(i))` to just `isDigit(src.charAt(i))`,
save, and run:

```bash
echo '12 +' | node calc.ts       # finishes: the run ends at the space
echo '1 + 23' | node calc.ts     # never finishes — press Ctrl+C
```

The first works because the number is followed by something. The second ends
in a digit, so the loop reads past the end, gets `""`, and `isDigit("")` is true.
Put the guard back.
""",
    reference="""// calc.ts — module 3
//
// Numbers of any length. The digit branch no longer consumes one character; it
// consumes the whole run — remember where it started, advance while it is still
// a digit, cut it out. The shape every multi-character token will use.
import { readFileSync } from "node:fs";

type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}

const DIGITS = "0123456789";

// Asked in two places now, so it has a name. Careful: isDigit("") is TRUE,
// because DIGITS.indexOf("") is 0 — see the guard in the inner loop.
function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}

function scan(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    const ch = src.charAt(i);
    if (ch === " ") {
      i = i + 1;
    } else if (isDigit(ch)) {
      // THE LOOKAHEAD. Start, advance, cut.
      const start = i;
      // Length check FIRST: && stops at the first false, so isDigit is never
      // asked about the "" that charAt returns past the end. Reverse these and
      // an input ending in a digit loops forever.
      while (i < src.length && isDigit(src.charAt(i))) {
        i = i + 1;
      }
      // `i` is now on the first non-digit, and a slice's end is exclusive — so
      // this is exactly the run, with no +1 anywhere.
      const text = src.slice(start, i);
      // Cannot be NaN: the loop above only accepted digits. That guarantee is
      // the scanner's, not Number's — accept a "." or a "-" and it is gone.
      tokens.push(numberToken(Number(text)));
      // No `i = i + 1` here. The inner loop already moved the cursor as far as
      // the number goes. This is why module 2 put one in every branch instead
      // of once at the bottom of the loop.
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      tokens.push(opToken(ch));
      i = i + 1;
    } else {
      // Still WRONG: `1 $ 2` loses its `$` without a word. Module 4.
      i = i + 1;
    }
  }
  tokens.push(eofToken());
  return tokens;
}

const src = readFileSync(0, "utf8").trim();
for (const t of scan(src)) {
  console.log(JSON.stringify(t));
}
""",
    stretch=[
        "Read decimals: let the number branch accept one `.` followed by more digits, so `2.5` is one token. Now find the input that makes `Number` answer `NaN` again — the guarantee from step 2 is gone, and you have to decide what happens instead.",
        "Allow `_` as a digit separator, so `1_000_000` is one million. The inner loop's condition changes and `Number` does not understand underscores — something has to take them out between the slice and the conversion.",
        "Make the scanner read `-3` as a single number token. Then scan `5-3` and see what goes wrong. Module 8 leaves `-` to the parser for exactly this reason.",
        "Write `isDigit` without `indexOf`: `ch >= \"0\" && ch <= \"9\"`. Check what it says about `\"\"`, and whether the guard in the inner loop is still needed.",
        "Print each token with its start position — the `start` the number branch already records. Module 16 does this for every token, and you will have written half of it.",
    ],
    glossary=[
        _pgloss("lookahead", "Reading past the current character to find where a token ends. The start / advance / cut shape."),
        _pgloss("slice", "`s.slice(start, end)` — the characters from `start` up to but not including `end`. A copy; `s` is unchanged."),
        _pgloss("exclusive end", "The convention that a range's end is the first position *not* included. Makes lengths a subtraction and adjacent ranges meet exactly."),
        _pgloss("Number", "`Number(text)` — the number a string spells, or `NaN` if it spells none. Never throws."),
        _pgloss("NaN", "\"Not a number\" — of type `number`, printed by `JSON.stringify` as `null`."),
        _pgloss("short-circuit", "`a && b` does not evaluate `b` when `a` is false. Why the length check can guard `isDigit`."),
        _pgloss("run", "A stretch of consecutive characters that all belong to one token — the digits of `345`."),
    ],
    cheatsheet="""
```ts
const DIGITS = "0123456789";

function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;      // isDigit("") is TRUE — guard it
}

// the number branch: start, advance, cut
} else if (isDigit(ch)) {
  const start = i;                                     // before moving
  while (i < src.length && isDigit(src.charAt(i))) {   // guard first
    i = i + 1;
  }
  const text = src.slice(start, i);                    // end exclusive
  tokens.push(numberToken(Number(text)));              // cannot be NaN here
  // no i = i + 1 — the inner loop did the moving
}
```

| Expression | Value |
|---|---|
| `"12 + 345".slice(0, 2)` | `"12"` |
| `"12 + 345".slice(5, 8)` | `"345"` |
| `"12 + 345".slice(5)` | `"345"` |
| `Number("12") + 1` | `13` |
| `"12" + 1` | `"121"` |
| `Number("12+")` | `NaN` — prints as `null` |

| Symptom | Cause |
|---|---|
| `123` scans as `23` | `start` taken after the cursor moved |
| `"value":null` | slice took one character too many (`i + 1`) |
| the character after a number vanishes | an extra `i = i + 1` after the inner loop |
| hangs on input ending in a digit | length check missing, or after `isDigit` |
| `12` is two tokens | still using module 2's single-digit branch |
""",
    self_check=[
        "Can you say what `\"12 + 345\".slice(5, 8)` is, and why the end is 8 and not 7?",
        "Can you say what `\"12\" + 1` is, and what converts it first?",
        "Can you explain why `Number` never answers `NaN` inside this scanner — and name a change that would end that?",
        "Can you walk `10/4` through the number branch, saying where `i` is after the inner loop?",
        "Can you explain, using `isDigit(\"\")`, why the length check must come first?",
        "Can you say why the number branch has no `i = i + 1` of its own?",
    ],
    review=[
        _pq("The inner loop's condition is `isDigit(src.charAt(i)) && i < src.length`. What happens on `1 + 23`?",
            ["The program never finishes — past the end `charAt` is `\"\"`, `isDigit(\"\")` is true, and the length check is never reached",
             "It works; the order of `&&` does not matter",
             "The `23` is dropped",
             "A compile error"],
            0,
            "Short-circuiting is what makes a guard a guard. The cheap, safe check "
            "goes first."),
        _pq("Why is `slice(start, i)` right after the inner loop, with no `+ 1`?",
            ["`i` is the first non-digit and the end of a slice is exclusive, so the slice ends just before it",
             "`slice` adds one automatically",
             "Because `i` points at the last digit",
             "It is not; it should be `i + 1`"],
            0,
            "Exclusive ends and \"stop on the first thing that doesn't belong\" "
            "fit together exactly. Adding one takes the operator with it."),
        _pq("A token prints as `{\"kind\":\"number\",\"value\":null}`. What went wrong?",
            ["`Number` got text that was not all digits and answered `NaN`, which JSON prints as `null`",
             "The number was zero",
             "The token has no value field",
             "`JSON.stringify` cannot print large numbers"],
            0,
            "A `null` value is the scanner's way of telling you the slice was the "
            "wrong length."),
        _pq("Module 2 put `i = i + 1` in every branch instead of once at the bottom. What did that buy this module?",
            ["The number branch can move the cursor by the number's length — a loop that always moved by one would skip the next character",
             "Nothing; it was style",
             "It made the scanner faster",
             "It let the scanner read negative numbers"],
            0,
            "A shape chosen one module early for the module that needed it. The "
            "project keeps doing this, and module 16 is the biggest payoff."),
    ],
    milestone="Your scanner reads every token the calculator needs — numbers of any "
              "length, the four operators, and the end — using the start / advance / "
              "cut shape every multi-character token will share. One wrong answer is "
              "left in phase 1, and it is the one about mistakes.",
))
