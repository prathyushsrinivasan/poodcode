# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 2 — The scanner loop.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`.
#
# STDIN ARRIVES HERE. From this module on, every Calc program reads its source
# text from stdin, so one exercise is checked against several inputs at once —
# `1 + 2`, `7`, the empty string — each as its own test case. That is the
# `_stdin` program shape, proven in this module.
#
# WHAT IS NOW LEGAL (`_CALC_SCOPE_RULES` at 2): arrays (`[]`, `.push(`,
# `.length`), `while (` and `for (`, `.charAt(`, `.indexOf(`, `readFileSync(`
# and `.trim(`. Still NOT legal: `.slice(` and `Number(` (module 3), `=>`
# (module 18 — so no arrow functions, and no array methods that take one), and
# the words `never` and `case ` anywhere, comments included.
#
# SINGLE-DIGIT NUMBERS, BY DESIGN. Without `Number` and `.slice`, a digit's
# value comes from its position in "0123456789" — `DIGITS.indexOf(ch)` — which
# also answers "is it a digit?" with -1. That limitation is the module: `12`
# scans as two tokens, the scanner is graded doing exactly that, and module 3
# opens by pointing at it.
#
# EVERY BRANCH ADVANCES THE CURSOR ITSELF. `i = i + 1` appears in all four
# branches rather than once at the bottom of the loop. It looks repetitive, and
# it is the shape module 3 needs: a number branch consumes as many characters as
# the number has, and a loop that always advances by one cannot express that.
# Settled here for module 3's sake, the same way module 1 settled `eof`.
#
# THE LIE, GRADED. An unrecognised character is silently skipped — `1 $ 2`
# scans as `1`, `2`. That is wrong, the module says so, and the build asserts
# it, exactly as the Todo API's module 9 grades its dishonest 500. Module 4 makes
# it an error.
# ---------------------------------------------------------------------------

_C_TOKENS = """type Op = "+" | "-" | "*" | "/";

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
"""

_C2_SCAN = """const DIGITS = "0123456789";

function scan(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    const ch = src.charAt(i);
    const digit = DIGITS.indexOf(ch);
    if (ch === " ") {
      i = i + 1;
    } else if (digit !== -1) {
      tokens.push(numberToken(digit));
      i = i + 1;
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

_C2_MAIN = """const src = readFileSync(0, "utf8").trim();
for (const t of scan(src)) {
  console.log(JSON.stringify(t));
}
"""


def _c2(scan=_C2_SCAN, main=_C2_MAIN):
    return _stdin("\n\n".join(p.rstrip("\n") for p in (_C_TOKENS, scan, main)))


_C2_FULL = _c2()

# JSON for the tokens the tests print.
_CN = lambda v: '{"kind":"number","value":%d}' % v          # noqa: E731
_CO = lambda o: '{"kind":"op","op":"%s"}' % o               # noqa: E731
_CEOF = '{"kind":"eof"}'


def _toks(*parts):
    """Expected output for a token list: ints are numbers, strings operators."""
    return "\n".join([_CN(p) if isinstance(p, int) else _CO(p) for p in parts] + [_CEOF])


# --- Step 1's plain program: a list of tokens, printed ----------------------
_C2_S1_BODY = """const tokens: Token[] = [];
tokens.push(numberToken(1));
tokens.push(opToken("+"));
tokens.push(numberToken(2));
tokens.push(eofToken());

console.log(tokens.length);
for (const t of tokens) {
  console.log(JSON.stringify(t));
}
"""
_C2_S1_OUT = "4\n" + _toks(1, "+", 2)


def _c2_s1(body=_C2_S1_BODY):
    return _plain(_C_TOKENS + "\n" + body)


# --- Step 2's program: walking the source with a cursor ---------------------
_C2_S2_WALK = """const src = readFileSync(0, "utf8").trim();
let i = 0;
while (i < src.length) {
  const ch = src.charAt(i);
  if (ch !== " ") {
    console.log(`${i} ${ch}`);
  }
  i = i + 1;
}
"""
_C2_S2_TESTS = [("1 + 2", "0 1\n2 +\n4 2"), ("7", "0 7"), ("3*4", "0 3\n1 *\n2 4"),
                ("", "")]


def _c2_s2(walk=_C2_S2_WALK):
    return _stdin(walk)


_C2_SCAN_TESTS = [
    ("1 + 2", _toks(1, "+", 2)),
    ("7", _toks(7)),
    ("3*4-5", _toks(3, "*", 4, "-", 5)),
    ("  9 / 3  ", _toks(9, "/", 3)),
    ("", _CEOF),
]

_C2_WHY = (
    "Module 1 designed the token and then built four of them by hand, because "
    "there was nothing to build them from. That was the right order — you "
    "cannot write the thing that produces tokens before you know what one is — "
    "but it leaves a language that cannot read. The source text is sitting on "
    "stdin and nothing looks at it. This module writes the loop that does: one "
    "character at a time, left to right, a token pushed onto a list for each "
    "one that means something."
)

_C2_BRIEF = """
### The whole module in one line

Read a line of source from stdin, walk it one character at a time, and push a
token onto a list for every character that means something.

### What a scanner is

```
"1 + 2"   →   [number 1, op +, number 2, eof]
```

A **scanner** (also called a *lexer* or *tokenizer*) is the first arrow in the
pipeline from module 1's brief. It turns text, which is hard to compute with,
into a list of small typed facts, which is easy. Every later phase reads the
list and never looks at the text again.

Its shape is always the same, in every language processor ever written:

```ts
let i = 0;                          // a cursor: where you are in the text
while (i < src.length) {            // until you run out of text
  const ch = src.charAt(i);         // look at one character
  // decide what it is, push a token, move the cursor on
}
tokens.push(eofToken());            // then say the text ended
```

Four new pieces of language make that possible, and each gets a step: an array
to hold the tokens, stdin to read the source from, a loop with a cursor, and a
way to tell which character you are looking at.

### What it cannot do yet — on purpose

**Numbers are one digit long.** `12` scans as a `1` and a `2`. Reading a run of
digits as one number needs two tools this module does not have yet, and it is
the whole of module 3.

**A character it does not recognise is skipped.** `1 $ 2` scans as `1`, `2` and
nothing about the `$`. That is wrong — a scanner that quietly ignores what it
cannot read is a scanner that hides typos — and the module build grades it
anyway, so you know exactly what today's scanner does. Module 4 turns it into an
error that names the character and where it was.

### Why `charAt(i)` and not `src[i]`

The project is type-checked under `noUncheckedIndexedAccess`, which makes
`src[i]` a `string | undefined` — an index can always miss. `src.charAt(i)` is a
plain `string`: past the end it answers `""` rather than `undefined`. Step 2 is
about which to use and what each one costs.
"""

_C2_SYNTAX = [
    _syn(
        "const tokens: Token[] = [];",
        "An **array** — an ordered list — of tokens, starting empty. `Token[]` is "
        "read \"array of `Token`\".",
        """
const tokens: Token[] = [];
console.log(tokens.length);    // 0
""",
        "The annotation matters. `const tokens = [];` gives the compiler nothing "
        "to go on, and it cannot then check that what you push is a `Token`.",
    ),
    _syn(
        "tokens.push(numberToken(1));",
        "Add one element to the end of the array. The array is `const`, and you "
        "can still push: `const` fixes which array the name refers to, not what "
        "is in it.",
        """
const tokens: Token[] = [];
tokens.push(opToken("+"));
console.log(tokens.length);    // 1
""",
        "`push` checks what you give it against the element type — "
        "`tokens.push(\"+\")` is refused, because a string is not a `Token`.",
    ),
    _syn(
        "tokens.length",
        "How many elements the array holds — and, on a string, how many "
        "characters: `\"1 + 2\".length` is 5.",
        "",
        "Positions run from `0` to `length - 1`. `length` itself is one past the "
        "end, which is why loops test `i < src.length` and not `<=`.",
    ),
    _syn(
        "for (const t of tokens) { … }",
        "Run the block once per element, in order, with `t` holding each one in "
        "turn.",
        """
for (const t of tokens) {
  console.log(JSON.stringify(t));
}
""",
        "**`of`**, not `in`. `for (const t in tokens)` walks the *positions* — "
        "`\"0\"`, `\"1\"`, `\"2\"` as strings — and prints those instead of the "
        "tokens.",
    ),
    _syn(
        'const src = readFileSync(0, "utf8").trim();',
        "Read everything on stdin as text, and cut off the whitespace at both "
        "ends. `0` means stdin; `\"utf8\"` means give me a string, not bytes.",
        """
import { readFileSync } from "node:fs";

const src = readFileSync(0, "utf8").trim();
console.log(src.length);
""",
        "`echo '1 + 2'` sends a newline after the 2. Without `.trim()` your "
        "scanner meets a `\\n` at the end of every input and has to decide what it "
        "is.",
    ),
    _syn(
        "while (i < src.length) { … }",
        "Run the block again and again, for as long as the condition is true. "
        "Here: while the cursor is still inside the text.",
        """
let i = 0;
while (i < 3) {
  console.log(i);
  i = i + 1;
}
""",
        "Something in the block must eventually make the condition false. Forget "
        "`i = i + 1` in any branch and the loop runs forever — the program does "
        "not crash, it simply never finishes.",
    ),
    _syn(
        "const ch = src.charAt(i);",
        "The character at position `i`, as a one-character string. Past the end "
        "it answers `\"\"`.",
        """
"1 + 2".charAt(0);   // "1"
"1 + 2".charAt(2);   // "+"
"1 + 2".charAt(9);   // ""
""",
        "`src[i]` looks the same and is typed `string | undefined` here, because "
        "of `noUncheckedIndexedAccess`. `charAt` is always a `string` — at the "
        "cost that \"past the end\" becomes `\"\"`, a value that looks real.",
    ),
    _syn(
        "const digit = DIGITS.indexOf(ch);",
        "Where `ch` first appears in `\"0123456789\"` — which, for a digit, is its "
        "value. `-1` means it is not there at all.",
        """
const DIGITS = "0123456789";
DIGITS.indexOf("7");    // 7
DIGITS.indexOf("+");    // -1
""",
        "`DIGITS.indexOf(\"\")` is **0**: the empty string is found at the start "
        "of every string. So a cursor that runs one past the end reads `\"\"`, "
        "and `\"\"` reads as the digit zero.",
    ),
    _syn(
        "if (ch === \"+\" || ch === \"-\" || ch === \"*\" || ch === \"/\") { … }",
        "Narrowing on a string. Inside the `if`, the compiler knows `ch` is one "
        "of those four — so it is an `Op`, and `opToken(ch)` compiles.",
        "",
        "It is module 1's narrowing, applied to a plain `string` instead of a "
        "`kind` field. Leave out one of the four comparisons and that operator "
        "is silently skipped.",
    ),
    _syn(
        "type Token = NumberToken | OpToken | EofToken;",
        "Module 1's union. The scanner produces a `Token[]` and nothing else.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a list of tokens.
# ---------------------------------------------------------------------------

_C2_S1 = _pstep(
    "list", "A list of tokens",
    "Arrays: `Token[]`, `push`, `length`, and a `for … of` to print them.",
    """
Module 1 ended by printing four tokens, one `console.log` each. A scanner cannot
work that way — it does not know in advance how many tokens the text holds — so
it needs somewhere to put them as it finds them.

That somewhere is an **array**:

```ts
const tokens: Token[] = [];

tokens.push(numberToken(1));
tokens.push(opToken("+"));
tokens.push(numberToken(2));
tokens.push(eofToken());

console.log(tokens.length);    // 4
```

`Token[]` is the type: an array whose every element is a `Token`. `[]` is the
value: an empty one. `push` adds to the end, and `length` says how many there
are.

`tokens` is `const`, and you are pushing to it four times. That is fine: `const`
means *this name always refers to this array*. It says nothing about what the
array holds, which is allowed to grow.

### Printing every element

```ts
for (const t of tokens) {
  console.log(JSON.stringify(t));
}
```

`for … of` runs the block once for each element, in order, with `t` holding the
current one. Each `t` is a `Token`, so everything module 1 taught about a token
works on it — including narrowing on `t.kind`.

### `of`, not `in`

`for (const t in tokens)` is also valid, compiles, and does something different:
it walks the array's **positions**, as strings — `"0"`, `"1"`, `"2"`, `"3"`. The
`in` form exists for objects and is almost never what you want on an array.
""",
    """
Your program prints the count, then the four tokens:

```
4
{"kind":"number","value":1}
{"kind":"op","op":"+"}
{"kind":"number","value":2}
{"kind":"eof"}
```

That is exactly the list module 1 built by hand — now held in one value that a
function can return.
""",
    pitfalls=[
        "`for (const t in tokens)`. Walks positions, not elements — it prints `\"0\"`, `\"1\"`, `\"2\"`, `\"3\"`, and compiles without a murmur.",
        "`const tokens = [];` with no type. The compiler has nothing to check your `push`es against, and the mistake you wanted it to catch goes through.",
        "Thinking `const` stops you pushing. It stops you *reassigning* `tokens` to a different array; the contents are yours to change.",
        "Pushing the factory instead of calling it: `tokens.push(eofToken)`. That is the function itself, not a token — and the compiler says so, because a function is not a `Token`.",
    ],
    warmup=[
        _pq("`const tokens: Token[] = []; tokens.push(eofToken());` — is the `push` allowed on a `const`?",
            ["Yes — `const` fixes which array `tokens` names, not what the array holds",
             "No — a `const` array cannot change",
             "Only if the array was declared with `let`",
             "Only for the first element"],
            0,
            "The binding is constant; the contents are not. Module 1 made the same "
            "distinction for objects without needing it."),
    ],
    exercises=[
        _pex("calc-m2-list-1", "An empty list of tokens",
             "Declare the array the tokens are pushed onto. It starts empty, and "
             "only tokens may go in it.",
             _c2_s1(),
             "const tokens: Token[] = [];",
             [("", _C2_S1_OUT)],
             ["The type is \"array of `Token`\".",
              "The value is an empty array.",
              "`const` — the name never changes, only what is in it.",
              "`const tokens: Token[] = [];`"]),
        _pfix("calc-m2-list-fix1", "Four numbers that are not tokens",
              "The count is right — `4` — but then it prints `\"0\"`, `\"1\"`, "
              "`\"2\"` and `\"3\"` instead of the tokens.",
              _c2_s1(_C2_S1_BODY.replace("for (const t of tokens)", "for (const t in tokens)")),
              _c2_s1(),
              [("", _C2_S1_OUT)],
              ["Those are positions, printed as strings. Which loop walks positions?",
               "One word in the `for` line is wrong.",
               "`for (const t of tokens)`"],
              difficulty="Intro"),
        _pex("calc-m2-list-2", "Print every token",
             "Print each token in the list as JSON, one per line, in order.",
             _c2_s1(),
             """for (const t of tokens) {
  console.log(JSON.stringify(t));
}""",
             [("", _C2_S1_OUT)],
             ["One loop, one `console.log` inside it.",
              "`for … of` gives you each element in turn.",
              "Module 1 printed tokens with `JSON.stringify`.",
              "`for (const t of tokens) { console.log(JSON.stringify(t)); }`"]),
    ],
    quiz=[
        _pq("What does `for (const t in tokens)` walk over on an array of four tokens?",
            ["The positions `\"0\"` to `\"3\"`, as strings",
             "The four tokens",
             "The tokens' `kind` fields",
             "Nothing — it does not compile on arrays"],
            0,
            "`in` is for an object's keys, and an array's keys are its positions. "
            "`of` is the one you want on an array."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — reading and walking the source.
# ---------------------------------------------------------------------------

_C2_S2 = _pstep(
    "cursor", "Reading the source, one character at a time",
    "stdin, a cursor, `while`, and `charAt` — and why not `src[i]`.",
    """
### The source arrives on stdin

```ts
import { readFileSync } from "node:fs";

const src = readFileSync(0, "utf8").trim();
```

`readFileSync` reads a whole file at once. `0` is the file that is *standard
input* — whatever was piped to the program — and `"utf8"` asks for text rather
than raw bytes. `.trim()` then cuts whitespace off both ends, which matters more
than it looks: `echo '1 + 2' | node calc.ts` sends a newline after the 2, and
without the trim your scanner has to decide what a `\\n` is.

From this module on, every exercise reads its input this way. That is why each
one can be checked against several inputs: every input is its own test case.

### A cursor, and a loop that moves it

```ts
let i = 0;
while (i < src.length) {
  const ch = src.charAt(i);
  // … look at ch …
  i = i + 1;
}
```

`i` is the **cursor** — the position you are looking at. `while` runs the block
for as long as the cursor is inside the text: positions `0` to `src.length - 1`.
The last line moves it on. Forget that line and the loop never ends; the program
does not crash, it just never finishes, which is a much worse way to find out.

### `charAt(i)`, not `src[i]`

Both read the character at position `i`. They differ in what they say about
reading past the end:

| | Type | Past the end |
|---|---|---|
| `src[i]` | `string \\| undefined` | `undefined` |
| `src.charAt(i)` | `string` | `""` |

This project type-checks under `noUncheckedIndexedAccess`, so `src[i]` admits it
might miss, and every use of it has to handle `undefined`. `charAt` never does —
it hands back `""` instead. That is convenient, and it has a cost: `""` is a real
string, so reading past the end no longer *looks* like a mistake. The loop
condition `i < src.length` is what keeps you from ever doing it.
""",
    """
For `1 + 2` your program prints each non-space character with its position:

```
0 1
2 +
4 2
```

Five characters, three printed. Positions 1 and 3 are the spaces. Empty input
prints nothing at all.
""",
    pitfalls=[
        "`while (i <= src.length)`. One step too far: `charAt` answers `\"\"` at position `length`, and the loop body runs on a character that is not there.",
        "Forgetting `i = i + 1`. The loop never ends. There is no error — the program simply sits there — which is why it is worth checking first when a run hangs.",
        "`const ch = src[i];` and then using `ch` as a string. Under `noUncheckedIndexedAccess` it is `string | undefined`, and the compiler stops you at the first place that needs a string.",
        "Leaving off `.trim()`. `echo` sends a trailing newline, and a scanner that has not been told about `\\n` treats it as an unknown character.",
        "`readFileSync(0)` without `\"utf8\"`. You get raw bytes (a `Buffer`), not a string — and `.charAt` does not exist on it.",
    ],
    warmup=[
        _pq("`\"1 + 2\".charAt(5)` — what is it?",
            ["`\"\"` — past the end, `charAt` answers the empty string",
             "`undefined`",
             "`\"2\"`",
             "It throws"],
            0,
            "Which is why the loop condition is `<`, not `<=`. Position 5 is one "
            "past the last character."),
        _pq("Under `noUncheckedIndexedAccess`, what is the type of `src[i]`?",
            ["`string | undefined`",
             "`string`",
             "`string[]`",
             "`any`"],
            0,
            "An index can always miss. `charAt` avoids the `undefined` by "
            "answering `\"\"` instead."),
    ],
    exercises=[
        _pex("calc-m2-cursor-1", "Look at one character",
             "Read the character the cursor is on — as a plain `string`, not a "
             "`string | undefined`.",
             _c2_s2(),
             "src.charAt(i)",
             _C2_S2_TESTS,
             ["`src[i]` would be `string | undefined` here.",
              "The string method that takes a position and always answers a string.",
              "`src.charAt(i)`"]),
        _pex("calc-m2-cursor-2", "Read the source",
             "The source text is on stdin. Read all of it, as text, with the "
             "whitespace trimmed off both ends.",
             _c2_s2(),
             'readFileSync(0, "utf8").trim()',
             _C2_S2_TESTS,
             ["`readFileSync` is already imported. Standard input is file `0`.",
              "Ask for `\"utf8\"` to get a string rather than bytes.",
              "Then trim it.",
              '`readFileSync(0, "utf8").trim()`']),
        _pfix("calc-m2-cursor-fix1", "One position too many",
              "Every input prints one line too many — `1 + 2` ends with a line "
              "that is just `5`, and `7` ends with a line that is just `1`.",
              _c2_s2(_C2_S2_WALK.replace("while (i < src.length)", "while (i <= src.length)")),
              _c2_s2(),
              _C2_S2_TESTS,
              ["What is at position `src.length`? What does `charAt` answer there?",
               "Positions run from 0 to `length - 1`.",
               "`while (i < src.length)`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does this project read characters with `charAt(i)` rather than `src[i]`?",
            ["`charAt` is always a `string`; `src[i]` is `string | undefined` under `noUncheckedIndexedAccess`",
             "`src[i]` does not work on strings",
             "`charAt` is faster",
             "`src[i]` counts from 1"],
            0,
            "And the price of that convenience is that past-the-end reads look "
            "like `\"\"`, not like an error — so the loop condition has to be "
            "right."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — characters become tokens.
# ---------------------------------------------------------------------------

_C2_S3 = _pstep(
    "tokens", "Characters become tokens",
    "A digit's value from `indexOf`, an operator by narrowing, and a cursor each branch moves itself.",
    """
The loop from step 2 looks at every character. Now each one has to be sorted
into what it means:

```ts
const ch = src.charAt(i);
const digit = DIGITS.indexOf(ch);
if (ch === " ") {
  i = i + 1;                                  // whitespace: means nothing
} else if (digit !== -1) {
  tokens.push(numberToken(digit));            // a digit
  i = i + 1;
} else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
  tokens.push(opToken(ch));                   // an operator
  i = i + 1;
} else {
  i = i + 1;                                  // anything else: skipped. For now.
}
```

### A digit, and its value, in one call

```ts
const DIGITS = "0123456789";
DIGITS.indexOf("7")     // 7   — found at position 7, which is its value
DIGITS.indexOf("+")     // -1  — not there at all
```

`indexOf` answers where a character first appears in a string, or `-1` if it
does not. Because `"0123456789"` lists the digits in order, a digit's position
*is* its value — so one call answers both "is this a digit?" and "which one?".

It is a trick, and it has a limit: it reads one character, so it reads one
digit. Module 3 replaces it with something that can read `123`.

### An operator, by narrowing

`opToken` takes an `Op`, and `ch` is a `string`. But inside this `if`:

```ts
if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
  tokens.push(opToken(ch));      // ch is "+" | "-" | "*" | "/" here
}
```

the compiler has narrowed `ch` to exactly those four strings — which is `Op`. It
is module 1's narrowing again, on a plain string instead of a `kind` field.
Leave one comparison out, and `opToken(ch)` still compiles for the other three,
and that operator is silently skipped.

### Why every branch moves the cursor itself

`i = i + 1` appears four times, once per branch, rather than once at the bottom
of the loop. That looks like repetition, and it is a decision: **each branch
consumes the characters of its own token.** Today every token is one character
long, so every branch moves by one. Module 3's number branch will consume as
many characters as the number has — and a loop that always moves by exactly one
could not say that.
""",
    """
```
$ echo '3*4-5' | node calc.ts
{"kind":"number","value":3}
{"kind":"op","op":"*"}
{"kind":"number","value":4}
{"kind":"op","op":"-"}
{"kind":"number","value":5}
{"kind":"eof"}
```

Spaces or none, the same tokens come out. That is the scanner's first job:
whitespace is for people, and the parser never sees it.
""",
    pitfalls=[
        "`while (i <= src.length)`. The last pass reads `\"\"`, and `DIGITS.indexOf(\"\")` is **0** — so every input grows a phantom `number 0` just before the `eof`.",
        "Checking `digit > 0` instead of `digit !== -1`. The digit `0` is at position 0, so it would never be recognised.",
        "Leaving an operator out of the narrowing `if`. The code still compiles for the rest, and that operator quietly vanishes from every input.",
        "Moving the cursor once at the bottom of the loop *as well as* in a branch. Every token then skips the character after it — `1+2` scans as `1` and `2` with the `+` never examined.",
        "A branch with no `i = i + 1`. The cursor never moves past that character and the loop runs forever.",
    ],
    warmup=[
        _pq("`\"0123456789\".indexOf(\"\")` — what is it?",
            ["`0` — the empty string is found at the start of every string",
             "`-1`",
             "`undefined`",
             "It throws"],
            0,
            "Which is why reading one past the end is not harmless here: `\"\"` "
            "reads as the digit zero."),
    ],
    exercises=[
        _pex("calc-m2-tokens-1", "Which digit is it?",
             "Work out whether `ch` is a digit and, if it is, its value — both from "
             "one call.",
             _c2(),
             "const digit = DIGITS.indexOf(ch);",
             _C2_SCAN_TESTS,
             ["`DIGITS` lists the ten digits in order, so a digit's position is its value.",
              "The string method that answers where a character appears — or `-1`.",
              "`const digit = DIGITS.indexOf(ch);`"]),
        _pex("calc-m2-tokens-2", "Is it an operator?",
             "Write the condition that is true for exactly the four operators — "
             "and that lets the compiler treat `ch` as an `Op` inside the branch.",
             _c2(),
             'ch === "+" || ch === "-" || ch === "*" || ch === "/"',
             _C2_SCAN_TESTS,
             ["Four comparisons, joined by \"or\".",
              "Each compares `ch` to one operator's string.",
              "Inside the `if`, `ch` must be narrowed to `Op`, or `opToken(ch)` will not compile.",
              '`ch === "+" || ch === "-" || ch === "*" || ch === "/"`']),
        _pfix("calc-m2-tokens-fix1", "A zero at the end of everything",
              "Every input scans correctly — and then grows one extra token, "
              "`{\"kind\":\"number\",\"value\":0}`, just before the `eof`. Even the "
              "empty input.",
              _c2(_C2_SCAN.replace("while (i < src.length)", "while (i <= src.length)")),
              _C2_FULL,
              _C2_SCAN_TESTS,
              ["The extra token appears after the last real character. What is the loop reading there?",
               "`charAt` past the end is `\"\"`, and `DIGITS.indexOf(\"\")` is 0.",
               "Stop the loop before it leaves the text.",
               "`while (i < src.length)`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does each branch of the scanner move the cursor itself, instead of once at the bottom of the loop?",
            ["Each branch consumes its own token's characters — and module 3's number branch will consume more than one",
             "Because `while` loops require it",
             "It is faster",
             "So that whitespace can be skipped twice"],
            0,
            "A decision made for the next module's sake. Today it looks like "
            "repetition; tomorrow it is the only shape that works."),
        _pq("Inside `if (ch === \"+\" || ch === \"-\" || ch === \"*\" || ch === \"/\")`, what is `ch`'s type?",
            ["`\"+\" | \"-\" | \"*\" | \"/\"` — which is `Op`, so `opToken(ch)` compiles",
             "`string`",
             "`Op | undefined`",
             "`OpToken`"],
            0,
            "Narrowing works on any comparison with a literal, not just on "
            "`kind` fields."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the end, and what today's scanner gets wrong.
# ---------------------------------------------------------------------------

_C2_S4 = _pstep(
    "eof", "The end — and what the scanner still gets wrong",
    "The `eof` token after the loop, and two answers that are wrong on purpose.",
    """
### Say the text ended

```ts
tokens.push(eofToken());
return tokens;
```

After the loop, before returning, push module 1's end-of-input token. Every list
the scanner produces ends with exactly one — even the list for an empty input,
which is `[eof]` and nothing else.

Module 1's brief made the case: the parser in module 6 will keep asking "what is
the next token?", and with a real `eof` at the end that question always has a
token for an answer. Without it, every one of those questions becomes "a token,
or nothing?", and every place that asks has to handle both.

### Two answers that are wrong today

```
$ echo '12' | node calc.ts
{"kind":"number","value":1}
{"kind":"number","value":2}
{"kind":"eof"}

$ echo '1 $ 2' | node calc.ts
{"kind":"number","value":1}
{"kind":"number","value":2}
{"kind":"eof"}
```

**`12` is two numbers.** The digit branch reads one character, so it makes one
digit. Fixing it needs a way to cut a run of characters out of the text and a
way to turn that run into a number — module 3, exactly.

**`$` vanished.** The `else` branch skips anything it does not recognise, so a
typo disappears without a word. That is the worst thing a language can do with
a mistake: hide it. Module 4 turns the `else` into an error that says `$` at
column 3.

Both are graded in the module build, as what the scanner does *today*. Knowing
which of your program's answers are wrong — and which module makes each one
right — is worth more than a test run that only checks the easy inputs.
""",
    """
```bash
$ echo '' | node calc.ts
{"kind":"eof"}

$ echo '  9 / 3  ' | node calc.ts
{"kind":"number","value":9}
{"kind":"op","op":"/"}
{"kind":"number","value":3}
{"kind":"eof"}
```

An empty program is one `eof`. Spaces at the ends are trimmed away before the
scanner ever sees them.
""",
    pitfalls=[
        "Forgetting the `eof`. The list just stops, and module 6's parser will have to check for the end of the array everywhere instead of once.",
        "Pushing `eof` inside the loop. Every character is followed by an end-of-input marker, and the parser stops after the first token.",
        "Returning early from inside the loop when the text runs out. The loop condition already handles that — the `eof` goes after it, once.",
        "Treating the skipped `$` as a feature. It is today's behaviour and it is wrong; module 4 exists to fix it.",
    ],
    warmup=[
        _pq("What does the scanner produce for an empty input?",
            ["A list holding exactly one token: `eof`",
             "An empty list",
             "Nothing — it returns `undefined`",
             "An error"],
            0,
            "Every token list ends with `eof`, including the one with nothing "
            "before it. That is what makes \"the end\" always a token."),
    ],
    exercises=[
        _pfix("calc-m2-eof-fix1", "A list that never says it ended",
              "Every token comes out right, and the list just stops — there is no "
              "`{\"kind\":\"eof\"}` at the end. The empty input prints nothing at "
              "all.",
              _c2(_C2_SCAN.replace("  tokens.push(eofToken());\n", "")),
              _C2_FULL,
              _C2_SCAN_TESTS,
              ["Module 1 designed a token for exactly this.",
               "It goes after the loop, once, before the `return`.",
               "`tokens.push(eofToken());`"],
              difficulty="Intro"),
        _pch("calc-m2-eof-build", "Write the scanner", "Medium",
             "Write `scan(src)`. Walk the text with a cursor; skip spaces; turn "
             "each digit into a number token and each of `+ - * /` into an "
             "operator token; skip anything else; end with `eof`.\n\n"
             "`DIGITS` is declared above it. Every branch moves the cursor itself.",
             _C2_FULL,
             _C2_SCAN.replace('const DIGITS = "0123456789";\n\n', "").rstrip("\n"),
             _C2_SCAN_TESTS,
             ["`const tokens: Token[] = [];` and `let i = 0;` before the loop.",
              "`while (i < src.length)`, and inside it `const ch = src.charAt(i);`.",
              "`DIGITS.indexOf(ch)` gives a digit's value, or `-1`.",
              "Four branches — space, digit, operator, anything else — each ending in `i = i + 1;`.",
              "After the loop: `tokens.push(eofToken());` and `return tokens;`."]),
    ],
    quiz=[
        _pq("`echo '1 $ 2'` scans as `1`, `2`, `eof`. Why is that wrong, and which module fixes it?",
            ["A character the language does not know was silently dropped — module 4 makes it an error naming the character and column",
             "It is correct; `$` is whitespace",
             "It should be `1`, `$`, `2` — module 3",
             "It should crash — module 17"],
            0,
            "A language that hides typos is worse than one that refuses them. "
            "Module 4 decides the refusal's exact wording."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C2_FINAL = _pch(
    "calc-m2-build", "Module 2 build — the scanner", "Medium",
    "Write `DIGITS` and `scan(src)`.\n\n"
    "Walk the source with a cursor. Skip spaces. A digit becomes a number token "
    "carrying its value; `+ - * /` become operator tokens; anything else is "
    "skipped. Every list ends with `eof`.\n\n"
    "Seven inputs. The last two are the scanner's two wrong answers, graded as "
    "what it does today: `12` scans as two numbers (module 3 fixes it) and `1 $ 2` "
    "loses the `$` without a word (module 4 fixes that).",
    _C2_FULL,
    _C2_SCAN.rstrip("\n"),
    _C2_SCAN_TESTS + [
        ("12", _toks(1, 2)),
        ("1 $ 2", _toks(1, 2)),
    ],
    ["`const DIGITS = \"0123456789\";` — a digit's position in it is its value.",
     "The loop is `while (i < src.length)` — `<`, or `\"\"` reads as a phantom zero.",
     "Each of the four branches ends with `i = i + 1;`.",
     "The operator branch narrows `ch` to `Op` with four `===` comparisons.",
     "`tokens.push(eofToken());` after the loop, whatever the input."],
)


_CALC_MODULES.append(_pmod(
    key="calc-scan", number=2, phase="scan",
    title="The scanner loop",
    what="walk the text one character at a time and push tokens onto a list",
    goal="Turn a line of source from stdin into a list of tokens, one character at a time.",
    why=_C2_WHY,
    est_minutes=45,
    builds_on=["calc-token"],
    concepts=["arrays", "for … of", "stdin", "a cursor", "while", "charAt vs [i]",
              "indexOf", "narrowing a string"],
    deliverable="`echo '3*4-5' | node calc.ts` prints six tokens — and you can say "
                "exactly which two inputs it still gets wrong.",
    objectives=[
        "Declare a typed array, push onto it, and print every element with `for … of`",
        "Say what `for … in` walks on an array, and why it is the wrong loop here",
        "Read stdin as text with `readFileSync(0, \"utf8\")`, and say what `.trim()` saves you from",
        "Walk a string with a cursor and a `while` loop, and name the one-character mistake that runs past the end",
        "Choose `charAt(i)` over `src[i]` under `noUncheckedIndexedAccess`, and say what each costs",
        "Turn a digit into its value with `indexOf`, and explain the phantom zero `indexOf(\"\")` causes",
        "Explain why every branch of the scanner moves the cursor itself",
    ],
    brief=_C2_BRIEF,
    syntax=_C2_SYNTAX,
    steps=[_C2_S1, _C2_S2, _C2_S3, _C2_S4],
    final_build=_C2_FINAL,
    acceptance=[
        "`echo '1 + 2' | node calc.ts` prints four tokens: number 1, op +, number 2, eof.",
        "`echo '3*4-5' | node calc.ts` prints the same tokens as `echo '3 * 4 - 5'`.",
        "`echo '' | node calc.ts` prints exactly one line, `{\"kind\":\"eof\"}`.",
        "No input produces a `number 0` token that was not a `0` in the text.",
        "`echo '12' | node calc.ts` prints two number tokens today — and you can say which module makes it one.",
        "`echo '1 $ 2' | node calc.ts` drops the `$` today — and you can say which module makes it an error.",
        "`calc.ts` reads characters with `charAt`, and the file compiles under `--strict --noUncheckedIndexedAccess`.",
    ],
    manual_test="""
With `calc.ts` saved, feed it programs:

```bash
echo '1 + 2'        | node calc.ts
echo '3*4-5'        | node calc.ts     # no spaces — same tokens
echo '  9 / 3  '    | node calc.ts     # spaces at the ends are trimmed
echo ''             | node calc.ts     # just eof
```

Then the two it gets wrong on purpose:

```bash
echo '12'           | node calc.ts     # two numbers — module 3
echo '1 $ 2'        | node calc.ts     # the $ vanishes — module 4
```

On Windows PowerShell, pipe a string instead: `'1 + 2' | node calc.ts`.

Last, see why the loop condition is `<`. Change it to `<=`, run
`echo '1 + 2' | node calc.ts`, and find the token that was never in the text.
Then change it back.
""",
    reference="""// calc.ts — module 2
//
// The scanner: text in, a list of tokens out. One character at a time, left to
// right, a cursor that each branch moves on itself.
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

// A digit's position in this string is its value, so one indexOf answers both
// "is it a digit?" (-1 if not) and "which one?". It reads ONE character, so it
// reads one digit — module 3 replaces it with something that can read "123".
//
// Careful: DIGITS.indexOf("") is 0. The loop condition below is what stops the
// scanner ever reading "" — charAt's answer past the end.
const DIGITS = "0123456789";

function scan(src: string): Token[] {
  const tokens: Token[] = [];
  let i = 0;
  while (i < src.length) {
    // charAt, not src[i]: under noUncheckedIndexedAccess src[i] is
    // `string | undefined`. charAt is always a string ("" past the end).
    const ch = src.charAt(i);
    const digit = DIGITS.indexOf(ch);

    // Every branch moves the cursor ITSELF. Today each token is one character
    // long; module 3's number branch consumes as many as the number has, and a
    // loop that always moved by one could not express that.
    if (ch === " ") {
      i = i + 1;
    } else if (digit !== -1) {
      tokens.push(numberToken(digit));
      i = i + 1;
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      // Narrowed: ch is "+" | "-" | "*" | "/" here, which is Op.
      tokens.push(opToken(ch));
      i = i + 1;
    } else {
      // WRONG, and knowingly so: an unrecognised character is dropped without a
      // word, so `1 $ 2` scans as `1 2`. Module 4 makes this an error that says
      // which character, and where.
      i = i + 1;
    }
  }
  // Every list ends with exactly one eof — even the empty one. Module 6's
  // parser can then always ask "what is the next token?" and get a token.
  tokens.push(eofToken());
  return tokens;
}

// trim: `echo` sends a trailing newline, and the scanner has no opinion on \\n.
const src = readFileSync(0, "utf8").trim();
for (const t of scan(src)) {
  console.log(JSON.stringify(t));
}
""",
    stretch=[
        "Treat a tab as whitespace too. Then a newline. Decide whether a newline should be whitespace in *this* language, given module 13 will separate statements with `;`.",
        "Print the tokens with module 1's `describe` instead of `JSON.stringify` — `number 1`, `operator +`, `end of input`. Which output would you rather debug a parser against?",
        "Count how many characters the `else` branch skipped, and print the count to stderr with `console.error`. You have just written the world's least helpful error message; module 4 writes a better one.",
        "Rewrite the loop so it moves the cursor once, at the bottom, instead of in every branch. It works — today. Then read module 3's first paragraph and see which of the two you would rather extend.",
        "Try `const ch = src[i];` and follow every compile error it causes. Count them: that is the cost `charAt` saved you.",
    ],
    glossary=[
        _pgloss("scanner", "The first phase of a language processor: text in, a list of tokens out. Also called a lexer or tokenizer."),
        _pgloss("array", "An ordered list of values, all of one type. `Token[]` is an array of tokens."),
        _pgloss("cursor", "A variable holding your current position in the text. The scanner's `i`."),
        _pgloss("stdin", "Standard input — whatever was piped into the program. `readFileSync(0, \"utf8\")` reads all of it."),
        _pgloss("charAt", "`s.charAt(i)` — the character at position `i`, as a string; `\"\"` past the end. Never `undefined`."),
        _pgloss("indexOf", "`s.indexOf(x)` — where `x` first appears in `s`, or `-1`. `s.indexOf(\"\")` is 0."),
        _pgloss("whitespace", "Characters that separate tokens and mean nothing themselves. The scanner consumes them and the parser never sees them."),
        _pgloss("infinite loop", "A loop whose condition never becomes false. The program never finishes and never errors — usually a missing cursor move."),
    ],
    cheatsheet="""
```ts
import { readFileSync } from "node:fs";

const DIGITS = "0123456789";           // position = value; indexOf("") is 0 (!)

function scan(src: string): Token[] {
  const tokens: Token[] = [];          // an empty, typed array
  let i = 0;                           // the cursor
  while (i < src.length) {             // <, never <=
    const ch = src.charAt(i);          // string, "" past the end — not src[i]
    const digit = DIGITS.indexOf(ch);  // 0-9, or -1
    if (ch === " ") {
      i = i + 1;
    } else if (digit !== -1) {
      tokens.push(numberToken(digit));
      i = i + 1;
    } else if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      tokens.push(opToken(ch));        // ch narrowed to Op
      i = i + 1;
    } else {
      i = i + 1;                       // skipped — wrong, and module 4's to fix
    }
  }
  tokens.push(eofToken());             // once, after the loop
  return tokens;
}

const src = readFileSync(0, "utf8").trim();
for (const t of scan(src)) {           // of, not in
  console.log(JSON.stringify(t));
}
```

| Input | Tokens | |
|---|---|---|
| `1 + 2` | `1` `+` `2` `eof` | |
| `3*4-5` | `3` `*` `4` `-` `5` `eof` | spaces are optional |
| *(empty)* | `eof` | always ends with one |
| `12` | `1` `2` `eof` | ⚠️ wrong → module 3 |
| `1 $ 2` | `1` `2` `eof` | ⚠️ wrong → module 4 |

| Symptom | Cause |
|---|---|
| a `number 0` before every `eof` | `<=` in the loop; `indexOf("")` is 0 |
| prints `"0"`, `"1"`, `"2"` | `for … in` instead of `for … of` |
| program never finishes | a branch that does not move `i` |
| an operator never appears | missing from the four `===` comparisons |
| no `eof` at the end | `tokens.push(eofToken())` missing after the loop |
""",
    self_check=[
        "Can you declare an empty array of tokens, push onto it, and say why `const` does not stop you?",
        "Can you say what `for … in` prints for an array of four tokens?",
        "Can you explain what `readFileSync(0, \"utf8\")` reads, and what `.trim()` is protecting the scanner from?",
        "Can you say what `charAt` and `src[i]` each answer past the end, and which one this project uses?",
        "Can you explain how `<=` in the loop produces a `number 0` token?",
        "Can you say why each branch moves the cursor itself?",
        "Can you name the scanner's two wrong answers today, and the module that fixes each?",
    ],
    review=[
        _pq("The scanner's loop is `while (i <= src.length)`. What appears in every output?",
            ["A `number 0` token just before `eof` — `charAt` reads `\"\"` at the end, and `DIGITS.indexOf(\"\")` is 0",
             "Nothing different; `<=` and `<` behave the same",
             "An infinite loop",
             "A compile error"],
            0,
            "Two harmless-looking facts — `charAt` past the end is `\"\"`, and "
            "`indexOf(\"\")` is 0 — combine into a token that was never in the text."),
        _pq("Why does module 1's `eof` token matter to a scanner?",
            ["It ends every list with a real token, so the parser can always ask for the next token and get one",
             "It marks where whitespace was",
             "It stores the length of the input",
             "It is only needed for empty inputs"],
            0,
            "Put the awkward case in the data, not in every piece of code that "
            "reads it."),
        _pq("Why does the scanner read with `src.charAt(i)` instead of `src[i]`?",
            ["`src[i]` is `string | undefined` under `noUncheckedIndexedAccess`; `charAt` is always a `string`",
             "`src[i]` returns a number",
             "`charAt` handles Unicode and `[i]` does not",
             "There is no difference"],
            0,
            "The flag makes every index admit it might miss. `charAt` trades "
            "`undefined` for `\"\"` — and the loop condition makes sure you never "
            "see it."),
        _pq("`echo '12' | node calc.ts` prints two number tokens. What is missing?",
            ["A way to read a run of digits as one token — cutting the run out of the text and turning it into a number, which is module 3",
             "A second `while` loop at the top level",
             "Nothing; `12` is two tokens in this language",
             "A `.trim()`"],
            0,
            "The digit branch consumes one character. Module 3 makes it consume "
            "as many as the number has — which is why every branch already moves "
            "its own cursor."),
    ],
    milestone="Your language can read. Text arrives on stdin, and a list of typed "
              "tokens comes out — one character at a time, whitespace thrown away, "
              "always ending in `eof`. It still reads `12` as two numbers and "
              "loses a `$` without a word, and you know exactly which modules fix "
              "each.",
))
