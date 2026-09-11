# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 4 — When the input is not a program.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses modules 2-3's `_C_TOKENS` and `_toks`.
#
# THE MODULE THAT DECIDES THE PROJECT'S ERROR STRATEGY, and decides it against
# exceptions: a scan failure is a VALUE, `{ ok: false; error: string }`, until
# module 17. Two reasons, both stated in step 1: an uncaught `throw` in a judged
# program is a crash rather than an answer, and returning failures makes every
# caller say what it does about them — which the compiler then enforces, since
# `result.tokens` does not exist until `result.ok` has been checked. Step 4
# grades that refusal as the module's one compile-time `fix`, on purpose.
#
# THE ERROR TEXT IS CONTRACT FROM HERE: `error: unexpected '$' at 1:3`. Line is
# always 1 until statements exist; the column is 1-based, `i + 1`.
#
# THE COLUMN DECISION CALC_ROADMAP.md FLAGGED. Modules 2-3 read the source with
# `.trim()`, which also removes LEADING whitespace — so for `  1 $ 2` the `$`
# would be reported at column 3 of text the user never typed. This module
# switches to `.trimEnd()`: the trailing newline still goes, and columns are
# columns of what was typed, which module 17's caret needs. Graded: the build's
# `  1 $ 2` must say column 5. `.trimEnd(` is gated here.
#
# FIRST ERROR ONLY. The scanner stops at the first character it cannot read.
# Reporting all of them is a real design (and a stretch item); one clear error
# is the right place to start.
#
# The error is printed on STDOUT so it can be judged. Where it belongs — stderr,
# with a non-zero exit code — is module 17's decision, and the module says so.
# ---------------------------------------------------------------------------

_C4_RESULT = """type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };
"""

_C4_UNEXPECTED = """function unexpected(ch: string, i: number): string {
  return `error: unexpected '${ch}' at 1:${i + 1}`;
}
"""

_C4_SCAN = """const DIGITS = "0123456789";

function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}

function scan(src: string): ScanResult {
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
      return { ok: false, error: unexpected(ch, i) };
    }
  }
  tokens.push(eofToken());
  return { ok: true, tokens: tokens };
}
"""

_C4_MAIN = """const src = readFileSync(0, "utf8").trimEnd();
const result = scan(src);
if (result.ok) {
  for (const t of result.tokens) {
    console.log(JSON.stringify(t));
  }
} else {
  console.log(result.error);
}
"""


def _c4(scan=_C4_SCAN, main=_C4_MAIN, unexpected=_C4_UNEXPECTED):
    return _stdin("\n\n".join(p.rstrip("\n") for p in
                              (_C_TOKENS, _C4_RESULT, unexpected, scan, main)))


_C4_FULL = _c4()


def _cerr(ch, col):
    return f"error: unexpected '{ch}' at 1:{col}"


_C4_TESTS = [
    ("1 + 2", _toks(1, "+", 2)),
    ("12 * 3", _toks(12, "*", 3)),
    ("", _CEOF),
    ("1 $ 2", _cerr("$", 3)),
    ("12 + x", _cerr("x", 6)),
    ("@", _cerr("@", 1)),
    ("1 $ 2 # 3", _cerr("$", 3)),
]

# --- Step 1's plain program: results built by hand --------------------------
_C4_SHOW = """function show(result: ScanResult): string {
  if (result.ok) {
    return `tokens: ${result.tokens.length}`;
  }
  return result.error;
}
"""

_C4_S1_PRINTS = """
console.log(show({ ok: true, tokens: [numberToken(1), opToken("+"), numberToken(2), eofToken()] }));
console.log(show({ ok: true, tokens: [eofToken()] }));
console.log(show({ ok: false, error: "error: unexpected '$' at 1:3" }));
"""
_C4_S1_OUT = "tokens: 4\ntokens: 1\nerror: unexpected '$' at 1:3"


def _c4_s1(result=_C4_RESULT, show=_C4_SHOW):
    return _plain(_C_TOKENS + "\n" + result + "\n" + show.rstrip("\n") + "\n" + _C4_S1_PRINTS)


# --- Step 2's plain program: the message ------------------------------------
_C4_S2_PRINTS = """
console.log(unexpected("$", 2));
console.log(unexpected("x", 5));
console.log(unexpected("@", 0));
console.log(unexpected("#", 10));
"""
_C4_S2_OUT = "\n".join([_cerr("$", 3), _cerr("x", 6), _cerr("@", 1), _cerr("#", 11)])


def _c4_s2(unexpected=_C4_UNEXPECTED):
    return _plain(unexpected.rstrip("\n") + "\n" + _C4_S2_PRINTS)


_C4_WHY = (
    "The scanner has one wrong answer left, and it is the worst kind: `1 $ 2` "
    "scans as `1` and `2`, and the `$` disappears without a word. A language that "
    "hides a typo is a language whose users spend an afternoon working out why "
    "`10 $ 3` equals 13. Every later phase will have its own ways to fail — a "
    "parser meeting `1 +`, an evaluator meeting `1 / 0` — and they will all "
    "report failure the way this module decides to. So this is where the project "
    "chooses how a failure travels, and what it says when it arrives."
)

_C4_BRIEF = """
### The whole module in one line

When the scanner meets a character it cannot read, stop and say which character
and where — as a value the caller has to deal with, not a crash and not a
silence.

### Four ways to fail, and why three are wrong

| When the scanner meets `$` it could… | Problem |
|---|---|
| **skip it** (today) | the typo vanishes; `10 $ 3` quietly means `10 3` |
| **crash** — `throw` | the program dies with a stack trace aimed at *you*, not the user |
| **push a special token** | now the parser has to handle a token that means "not a token" |
| **return a failure** | ✓ — and the caller must decide what to do with it |

The last one is a pattern with a name — **errors as values** — and TypeScript
makes it unusually safe:

```ts
type ScanResult =
  | { ok: true;  tokens: Token[] }
  | { ok: false; error: string };
```

A discriminated union, exactly like module 1's `Token`, with a boolean literal
as the tag. `result.tokens` does not exist until you have checked `result.ok` —
the compiler will not let you print tokens from a scan that failed.

### The message is contract

```
error: unexpected '$' at 1:3
```

Every word of that will be relied on for fourteen modules — by exercises, by
module 17's caret, and eventually by anyone who puts `calc.ts` in a script. Step
2 decides each part: the prefix, the quotes, `line:column`, and that columns
count from 1.

### A decision about spaces

Until now the source was read with `.trim()`, which removes spaces from the
**start** too — so in `  1 $ 2` the `$` would be reported at column 3 of text the
user did not type. This module switches to `.trimEnd()`. Columns become columns
of what was typed, which is what a caret has to point at.

### Why not `throw`

It is the obvious tool, and it waits until module 17 on purpose. A `throw`
nobody catches crashes the program — in a judged exercise that is a crash, not an
answer — and `catch` is a lot of machinery to meet in module 4. More importantly,
a returned failure is *visible in the type*: every caller of `scan` can see it
might fail. Module 17 puts one `try` at the very edge of the program, where it
belongs, and keeps values everywhere inside.
"""

_C4_SYNTAX = [
    _syn(
        "type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };",
        "A result union: either it worked and here are the tokens, or it did not "
        "and here is why. `ok` is the discriminant — a **boolean literal** type in "
        "each member.",
        """
const good: ScanResult = { ok: true, tokens: [eofToken()] };
const bad: ScanResult = { ok: false, error: "error: unexpected '$' at 1:3" };
""",
        "`true` and `false` are types here, not just values — `ok: true` means "
        "\"this field is always exactly `true`\". That is what lets `if "
        "(result.ok)` narrow. `{ ok: true, error: \"…\" }` is refused.",
    ),
    _syn(
        "if (result.ok) { … } else { … }",
        "Narrowing on the boolean tag. In the first branch `result.tokens` "
        "exists; in the second, `result.error` does.",
        """
if (result.ok) {
  console.log(result.tokens.length);
} else {
  console.log(result.error);
}
""",
        "Outside a check, neither field can be read: `result.tokens` is a compile "
        "error on a plain `ScanResult`. That is the point — you cannot use a "
        "failed scan by accident.",
    ),
    _syn(
        "return { ok: false, error: unexpected(ch, i) };",
        "Leave the function from the middle of the loop, handing back a failure. "
        "Nothing after it runs — the scan is over.",
        "",
        "Returning from inside a `while` is fine and common: the loop, the `eof` "
        "push and the success `return` below are all skipped.",
    ),
    _syn(
        "`error: unexpected '${ch}' at 1:${i + 1}`",
        "The error message, built with a template literal. `i + 1` because people "
        "count columns from 1 and the cursor counts from 0.",
        """
unexpected("$", 2);    // error: unexpected '$' at 1:3
""",
        "Line is always 1 for now — the source is one line. The format still says "
        "`1:` so that nothing has to change when it is not.",
    ),
    _syn(
        'const src = readFileSync(0, "utf8").trimEnd();',
        "Trim whitespace from the **end** only. The trailing newline `echo` sends "
        "still goes; leading spaces stay, so columns match what was typed.",
        """
"  1 $ 2\\n".trim();       // "1 $ 2"     — the $ is now at column 3
"  1 $ 2\\n".trimEnd();    // "  1 $ 2"   — the $ is at column 5, where it was typed
""",
        "`.trim()` silently moves every column left by however many spaces the "
        "line started with. The scanner already skips leading spaces; it never "
        "needed them removed.",
    ),
    _syn(
        "while (i < src.length && isDigit(src.charAt(i))) { … }",
        "Module 3's number run, unchanged.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a failure you can return.
# ---------------------------------------------------------------------------

_C4_S1 = _pstep(
    "result", "A failure you can return",
    "The result union, a boolean literal as a tag, and a compiler that will not let you ignore it.",
    """
`scan` returns `Token[]`. There is no way for that type to say "I could not read
this" — a list of tokens is a list of tokens. So first, a type that can say
either:

```ts
type ScanResult =
  | { ok: true; tokens: Token[] }
  | { ok: false; error: string };
```

This is module 1's discriminated union again. There, the tag was `kind`, a
string literal in each member. Here it is `ok`, and its type is a **boolean
literal**: in the first member, `ok` is always exactly `true`; in the second,
always exactly `false`. That is enough for the compiler to tell the two apart.

### Reading one

```ts
function show(result: ScanResult): string {
  if (result.ok) {
    return `tokens: ${result.tokens.length}`;   // here: { ok: true; tokens }
  }
  return result.error;                          // here: { ok: false; error }
}
```

Inside `if (result.ok)`, `result` has been narrowed to the success member, so
`result.tokens` exists. After it, only the failure member is left, so
`result.error` does.

And outside any check, **neither does**:

```ts
result.tokens      // error: Property 'tokens' does not exist on type 'ScanResult'
```

That error is the entire case for this design. A function that returns a
`ScanResult` cannot be used as if it had succeeded — every caller is made to
decide, in code, what happens when it did not.

### What the type refuses

```ts
{ ok: true, error: "x" }         // refused — the ok: true member has no error
{ ok: false, tokens: [] }        // refused — the ok: false member has no tokens
{ ok: true }                     // refused — a success must carry its tokens
```

Module 1 made the same argument for tokens: a state your program can never
produce is one your type will not let you write down.
""",
    """
```
tokens: 4
tokens: 1
error: unexpected '$' at 1:3
```

Two successes and a failure, each read through the one check that makes its
fields exist.
""",
    pitfalls=[
        "`{ ok: boolean; tokens?: Token[]; error?: string }`. Compiles, and allows a success with no tokens and a failure with no message — module 1's optional-field mistake, repeated one layer up.",
        "Reading `result.tokens` before checking `result.ok`. It does not compile, and should not; the whole design is that a failed scan cannot be used by accident.",
        "Writing `if (result.ok === true)`. It works, and it is `if (result.ok)` with more to read.",
        "Using `null` for \"failed\": `Token[] | null`. The caller can check for it, but a `null` cannot say *why* — and the why is the message.",
    ],
    warmup=[
        _pq("`const r: ScanResult = { ok: true, error: \"x\" };` — does it compile?",
            ["No — `ok: true` selects the success member, which has `tokens` and no `error`",
             "Yes — both fields are strings or booleans",
             "Yes, with `tokens` defaulting to `[]`",
             "Only in non-strict mode"],
            0,
            "The literal `true` picks the member, exactly as `kind: \"eof\"` picked "
            "one in module 1."),
    ],
    exercises=[
        _pex("calc-m4-result-1", "Success, or a reason",
             "Declare `ScanResult`: either `ok` is `true` and there are tokens, or "
             "`ok` is `false` and there is an error message.",
             _c4_s1(),
             "{ ok: true; tokens: Token[] } | { ok: false; error: string }",
             [("", _C4_S1_OUT)],
             ["Two object types joined by `|`.",
              "Each has an `ok` field whose type is a single boolean literal.",
              "The success member carries `tokens: Token[]`; the failure carries `error: string`.",
              "`{ ok: true; tokens: Token[] } | { ok: false; error: string }`"]),
        _pex("calc-m4-result-2", "Check which it is",
             "`show` has to read the tokens from a success and the message from a "
             "failure. Write the condition that makes `result.tokens` exist.",
             _c4_s1(),
             "result.ok",
             [("", _C4_S1_OUT)],
             ["The tag is a boolean — you can test it directly.",
              "Inside the `if`, only the success member is left.",
              "`if (result.ok)`"]),
    ],
    quiz=[
        _pq("Why is `{ ok: boolean; tokens?: Token[]; error?: string }` worse than the union?",
            ["It allows states no scanner produces — a success with no tokens, a failure with no message — and makes every reader check both optional fields",
             "It uses more memory",
             "Booleans cannot be discriminants",
             "It is not worse; it is shorter"],
            0,
            "Module 1's argument against optional payloads, word for word, one "
            "level up."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — what the error says.
# ---------------------------------------------------------------------------

_C4_S2 = _pstep(
    "message", "What the error says",
    "The message format, 1-based columns, and why it is fixed for fourteen modules.",
    """
```
error: unexpected '$' at 1:3
```

Each part is a decision, and each decision is now contract:

| Part | Why |
|---|---|
| `error:` | a fixed prefix a person — or a script — can search for |
| `unexpected` | says what kind of failure; module 6 adds `expected …` |
| `'$'` | the character itself, quoted so a space or a `'` is visible |
| `1:3` | line and column, the order every editor uses |

### Columns count from 1

The cursor `i` counts from 0: in `1 $ 2`, the `$` is at `i = 2`. People and
editors count from 1: it is the **third** character. So the message adds one:

```ts
function unexpected(ch: string, i: number): string {
  return `error: unexpected '${ch}' at 1:${i + 1}`;
}
```

Get this wrong and every error is one column to the left of the mistake — close
enough to look right and wrong enough to send someone to the wrong character.

### Line is always 1 — for now

The source is one line, so the line number is always `1`. It is in the format
anyway, so that nothing about it has to change when programs grow to several
lines. Module 16 carries a real line and column on every token.

### Why the format matters now

Everything downstream will match this text exactly. Exercises compare it
character for character. Module 17 prints the line again with a caret under
column 3. A user's script might `grep '^error:'`. Deciding it later means
changing all of those; deciding it now means changing none.
""",
    """
```
unexpected("$", 2)     error: unexpected '$' at 1:3
unexpected("x", 5)     error: unexpected 'x' at 1:6
unexpected("@", 0)     error: unexpected '@' at 1:1
```

A character at the very start of the line is column 1 — never column 0.
""",
    pitfalls=[
        "Reporting `i` instead of `i + 1`. Every error points one character to the left of the mistake, and a character at the start of the line is reported at column 0, which does not exist.",
        "Leaving the quotes off the character. `unexpected   at 1:2` — an unexpected space, printed without quotes — reads as a message with a word missing.",
        "Adding detail that changes per call — a timestamp, the whole source line. The message is compared exactly; module 17 is where the line gets printed, separately.",
        "Writing the message in the scanner branch itself. One function means one format; a second copy in module 6's parser is how two formats start.",
    ],
    warmup=[
        _pq("In `12 + x`, the `x` is at cursor position `i = 5`. What column is reported?",
            ["6 — columns count from 1, the cursor from 0",
             "5",
             "4",
             "1"],
            0,
            "The sixth character. `i + 1` converts between the two ways of "
            "counting."),
    ],
    exercises=[
        _pex("calc-m4-message-1", "Say where",
             "Build the message for character `ch` at cursor position `i`, in the "
             "project's format: `error: unexpected '<ch>' at 1:<column>`.",
             _c4_s2(),
             "  return `error: unexpected '${ch}' at 1:${i + 1}`;",
             [("", _C4_S2_OUT)],
             ["A template literal, with `${ … }` for the two parts that vary.",
              "The character goes inside single quotes.",
              "The column counts from 1; the cursor counts from 0.",
              "`return `error: unexpected '${ch}' at 1:${i + 1}`;`"]),
        _pfix("calc-m4-message-fix1", "Every error one to the left",
              "`unexpected(\"$\", 2)` says column 2. The `$` in `1 $ 2` is the "
              "third character. And `unexpected(\"@\", 0)` says column 0, which no "
              "editor has ever shown anyone.",
              _c4_s2(_C4_UNEXPECTED.replace("${i + 1}", "${i}")),
              _c4_s2(),
              [("", _C4_S2_OUT)],
              ["Where does the cursor start counting? Where do people?",
               "The column is one more than the position.",
               "`at 1:${i + 1}`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does the message say `1:` when the line is always 1?",
            ["So the format need not change when programs span several lines — the text is contract",
             "Because editors require it",
             "It is a placeholder that will be removed",
             "Because the first line is line 0"],
            0,
            "A format you will have to change later is a format that breaks every "
            "exercise, script and caret that trusted it."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the scanner that stops.
# ---------------------------------------------------------------------------

_C4_S3 = _pstep(
    "stop", "The scanner that stops",
    "Returning a failure from inside the loop, the first error only — and `trimEnd`.",
    """
Module 2's `else` branch skipped whatever it did not recognise. It becomes the
one place a scan can fail:

```ts
} else {
  return { ok: false, error: unexpected(ch, i) };
}
```

`return` leaves `scan` immediately, from the middle of the loop. Nothing after
it runs — no more characters, no `eof`, no success. The scan is over, and what
it hands back says why.

The end of the function changes to match:

```ts
tokens.push(eofToken());
return { ok: true, tokens: tokens };
```

and the return type becomes `ScanResult`. The compiler checks both `return`s
against it: a failure without an `error`, or a success without `tokens`, will not
compile.

### The first error only

`1 $ 2 # 3` has two characters the scanner cannot read, and the scan stops at the
first: `error: unexpected '$' at 1:3`. Reporting every error is a real design —
compilers do it — but it needs a way to keep going after a failure that leaves
the rest of the scan meaningful. One clear message is the right place to start,
and the stretch list has the other.

### Where the column comes from — and `trimEnd`

The column is `i + 1`, where `i` is a position in `src`. So `src` had better be
what the user typed. Modules 2 and 3 read it with `.trim()`, which removes
spaces from both ends:

```
typed:    "  1 $ 2"        the $ is the 5th character
.trim():  "1 $ 2"          the $ is now the 3rd
```

An error at column 3 of a line whose third character is a space is an error
message pointing at nothing. `.trimEnd()` removes only the end — the newline
`echo` adds — and leaves the leading spaces where they were. The scanner's space
branch already skips them; it never needed them taken away.

This is the kind of decision that is invisible until module 17 draws a caret
under column 3 of the original line and it lands in the wrong place.
""",
    """
```bash
$ echo '1 $ 2' | node calc.ts
error: unexpected '$' at 1:3

$ echo '  1 $ 2' | node calc.ts
error: unexpected '$' at 1:5

$ echo '1 $ 2 # 3' | node calc.ts
error: unexpected '$' at 1:3
```

The second is the one to check. If it says column 3, `src` is still being
trimmed at the front.
""",
    pitfalls=[
        "Keeping module 2's skip. `1 $ 2` scans as `1 2` and nothing is reported — the one wrong answer this module exists to remove.",
        "`.trim()` instead of `.trimEnd()`. Every column on a line that starts with spaces is off by the number of spaces, and no test without leading spaces will ever show it.",
        "Pushing the `eof` before returning the failure. The failure has no tokens; nothing after the `return` should run.",
        "Collecting the error in a variable and carrying on. The loop then keeps scanning a line it already knows is broken, and whatever it returns at the end is a success.",
        "Returning `{ ok: false, error: … }` from a function still typed `Token[]`. The compiler refuses — the return type has to become `ScanResult` first.",
    ],
    warmup=[
        _pq("`echo '  1 $ 2' | node calc.ts` with `.trim()`. What column is reported for the `$`?",
            ["3 — the two leading spaces were removed before the scanner saw the line",
             "5",
             "1",
             "No error is reported"],
            0,
            "Right character, wrong column. `.trimEnd()` keeps the line the user "
            "typed."),
    ],
    exercises=[
        _pex("calc-m4-stop-1", "Stop, and say why",
             "The `else` branch is the character nothing recognises. Instead of "
             "skipping it, end the scan with a failure naming it.",
             _C4_FULL,
             "      return { ok: false, error: unexpected(ch, i) };",
             _C4_TESTS,
             ["`return` leaves the function from inside the loop.",
              "What it returns is the failure member of `ScanResult`.",
              "`unexpected(ch, i)` builds the message.",
              "`return { ok: false, error: unexpected(ch, i) };`"]),
        _pfix("calc-m4-stop-fix1", "The `$` that vanishes",
              "`1 $ 2` scans as `1`, `2`, `eof`, and nothing is reported. `@` "
              "scans as an empty program. The scanner is still doing what module 2 "
              "did with a character it does not know.",
              _c4(_C4_SCAN.replace("      return { ok: false, error: unexpected(ch, i) };",
                                   "      i = i + 1;")),
              _C4_FULL,
              _C4_TESTS,
              ["Which branch handles a character that is not a space, a digit or an operator?",
               "It moves the cursor on and says nothing.",
               "Make it end the scan with a failure: `unexpected` is already written.",
               "`return { ok: false, error: unexpected(ch, i) };`"],
              difficulty="Easy"),
        _pfix("calc-m4-stop-fix2", "Right character, wrong column",
              "`1 $ 2` reports column 3, correctly. `  1 $ 2` — the same line typed "
              "with two spaces in front — *also* reports column 3, where the user's "
              "line has a space. The `$` they typed is the fifth character.",
              _c4(main=_C4_MAIN.replace(".trimEnd()", ".trim()")),
              _C4_FULL,
              _C4_TESTS + [("  1 $ 2", _cerr("$", 5))],
              ["The scanner counts columns correctly. What it is counting in is not what was typed.",
               "Something removed the leading spaces before the scan.",
               "Trim only the end — the newline still has to go.",
               "`readFileSync(0, \"utf8\").trimEnd()`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does the scanner stop at the first error rather than report them all?",
            ["Carrying on needs a way to recover that leaves the rest of the scan meaningful; one clear error is the right start",
             "Because `return` can only be used once per function",
             "Because only one error can exist per line",
             "It reports all of them"],
            0,
            "A real design choice, and a common one. Compilers that report many "
            "errors put real work into recovering between them."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the caller decides.
# ---------------------------------------------------------------------------

_C4_S4_FIXMAIN = """const src = readFileSync(0, "utf8").trimEnd();
const result = scan(src);
for (const t of result.tokens) {
  console.log(JSON.stringify(t));
}
"""

_C4_S4 = _pstep(
    "caller", "The caller has to decide",
    "Printing the tokens or the error — and the compile error that stops you forgetting.",
    """
`scan` now says whether it worked. The code that calls it has to say what
happens either way:

```ts
const src = readFileSync(0, "utf8").trimEnd();
const result = scan(src);
if (result.ok) {
  for (const t of result.tokens) {
    console.log(JSON.stringify(t));
  }
} else {
  console.log(result.error);
}
```

Try leaving the check out — the loop that worked for three modules:

```ts
for (const t of scan(src).tokens) { … }
```

It does not compile:

```
Property 'tokens' does not exist on type 'ScanResult'.
```

That is the design working. With a `throw`, forgetting to handle the failure
compiles fine and crashes at runtime, for whoever first types a `$`. With a
returned failure, forgetting does not compile at all. **Every caller of `scan`,
forever, has to decide in code what a failed scan means.** Module 6's parser will
be the next caller, and it will not be able to ignore this either.

### stdout, for now

The error is printed with `console.log`, on stdout, so the exercises can check
it. That is not where errors belong: a script piping `calc.ts` into something
else wants answers on stdout and errors on stderr, and a non-zero exit code so it
can tell them apart. That is module 17's decision, and the reason it waits is
that it is one decision for every kind of error at once — scan, parse and
evaluate.

### Phase 1 is done

The phase's outcome was: *`1 + 2 * 3` becomes a list of tokens you can print —
and `1 $ 2` becomes an error that says which character and where.* Both halves
are now true. Module 5 stops reading characters and starts building the tree.
""",
    """
```bash
$ echo '12 * 3' | node calc.ts
{"kind":"number","value":12}
{"kind":"op","op":"*"}
{"kind":"number","value":3}
{"kind":"eof"}

$ echo '12 + x' | node calc.ts
error: unexpected 'x' at 1:6
```

A program, or a reason it is not one. Never both, never neither.
""",
    pitfalls=[
        "Printing `result.tokens` without checking `result.ok`. It does not compile — and in a language without this type it would crash the first time a user made a typo.",
        "Printing nothing on failure. The scan failed for a reason and the reason is right there in `result.error`.",
        "Printing both — the tokens so far and the error. A failed scan has no tokens; a partial list would look like a program to anything reading it.",
        "Moving the error to stderr now. Right instinct, wrong module: the exercises judge stdout, and module 17 moves every kind of error at once, with an exit code.",
    ],
    warmup=[
        _pq("`for (const t of scan(src).tokens)` — why does this no longer compile?",
            ["`scan` returns a `ScanResult`, and `tokens` only exists on the success member — the failure must be handled first",
             "Because `tokens` was renamed",
             "Because `for … of` cannot loop over a function call",
             "It does compile"],
            0,
            "A failure you cannot forget is the whole case for errors as values."),
    ],
    exercises=[
        _pfix("calc-m4-caller-fix1", "Tokens from a scan that failed",
              "This does not compile:\n\n"
              "    Property 'tokens' does not exist on type 'ScanResult'.\n\n"
              "`scan` might have failed, and nothing here asks. Print the tokens "
              "when it worked and the message when it did not.",
              _c4(main=_C4_S4_FIXMAIN),
              _C4_FULL,
              _C4_TESTS,
              ["`result` is a union. Which member has `tokens`?",
               "Check the tag first: `if (result.ok)`.",
               "In the `else`, `result.error` exists — print it.",
               "`if (result.ok) { for (…) { … } } else { console.log(result.error); }`"],
              difficulty="Easy"),
        _pch("calc-m4-caller-build", "Print a program, or a reason", "Easy",
             "Write the end of the program: read the source (trimming only the "
             "end), scan it, and print either each token as JSON or the error "
             "message.",
             _C4_FULL,
             _C4_MAIN.rstrip("\n"),
             _C4_TESTS + [("  9 # 9", _cerr("#", 5))],
             ["`readFileSync(0, \"utf8\").trimEnd()` — leading spaces stay, so columns are right.",
              "`const result = scan(src);`",
              "`if (result.ok)` — loop over `result.tokens`; `else` — print `result.error`.",
              "The last test starts with two spaces. Its `#` is the fifth character."]),
    ],
    quiz=[
        _pq("Why is a returned failure safer than a `throw` here?",
            ["It is in the return type, so forgetting to handle it is a compile error rather than a crash for the first user who makes a typo",
             "Returning is faster than throwing",
             "`throw` cannot carry a message",
             "It is not safer; it is only more verbose"],
            0,
            "Module 17 still uses `throw` — once, at the edge, where one `try` "
            "catches everything. Inside, values keep every caller honest."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C4_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_C4_RESULT, _C4_UNEXPECTED, _C4_SCAN, _C4_MAIN))

_C4_FINAL = _pch(
    "calc-m4-build", "Module 4 build — a scanner that can say no", "Medium",
    "Write everything below the token factories.\n\n"
    "* `ScanResult` — success with tokens, or failure with a message\n"
    "* `unexpected(ch, i)` — `error: unexpected '<ch>' at 1:<column>`, columns "
    "from 1\n"
    "* `DIGITS`, `isDigit` and `scan` — module 3's scanner, returning a "
    "`ScanResult` and stopping at the first character it cannot read\n"
    "* the main program — read with `.trimEnd()`, then print the tokens or the "
    "error\n\n"
    "Nine inputs. The one to watch is the line that starts with two spaces.",
    _C4_FULL,
    _C4_BUILD_BLANK,
    _C4_TESTS + [
        ("  1 $ 2", _cerr("$", 5)),
        ("10 / 4", _toks(10, "/", 4)),
    ],
    ["`type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };`",
     "`unexpected` is one template literal; the column is `i + 1`.",
     "`scan`'s `else` branch returns the failure. Its last line returns the success, after the `eof`.",
     "The main program branches on `result.ok` — the compiler will not let it do otherwise.",
     "`.trimEnd()`, not `.trim()`, or the two-space line reports column 3."],
)


_CALC_MODULES.append(_pmod(
    key="calc-scan-errors", number=4, phase="scan",
    title="When the input is not a program",
    what="a failure you return rather than a failure you crash on",
    goal="Report an unexpected character by name and column, as a value every caller must handle.",
    why=_C4_WHY,
    est_minutes=40,
    builds_on=["calc-token", "calc-scan", "calc-numbers"],
    concepts=["errors as values", "result union", "boolean literal types",
              "narrowing on ok", "1-based columns", "trimEnd", "error text as contract"],
    deliverable="A scanner that answers every input with either its tokens or "
                "`error: unexpected '$' at 1:3` — and a program that cannot "
                "compile if it forgets which.",
    objectives=[
        "Compare skipping, throwing, a special token and returning a failure, and say what is wrong with the first three",
        "Declare a result union with a boolean literal tag, and name three objects the type refuses",
        "Narrow a result with `if (result.ok)`, and read the compile error you get without it",
        "Build the error message in the project's format, and say why columns are `i + 1`",
        "Return a failure from inside the scanner's loop, and say what does not run afterwards",
        "Choose `.trimEnd()` over `.trim()`, and give the input that shows the difference",
    ],
    brief=_C4_BRIEF,
    syntax=_C4_SYNTAX,
    steps=[_C4_S1, _C4_S2, _C4_S3, _C4_S4],
    final_build=_C4_FINAL,
    acceptance=[
        "`echo '1 $ 2' | node calc.ts` prints exactly `error: unexpected '$' at 1:3`.",
        "`echo '  1 $ 2' | node calc.ts` reports column 5 — the column of the `$` as typed.",
        "`echo '@' | node calc.ts` reports column 1, never column 0.",
        "`echo '1 $ 2 # 3' | node calc.ts` reports only the `$`.",
        "`echo '12 * 3' | node calc.ts` still prints four tokens, and no error.",
        "`scan` returns a `ScanResult`; deleting the `if (result.ok)` in the main program stops `calc.ts` compiling.",
        "No input makes `calc.ts` print a stack trace.",
    ],
    manual_test="""
With `calc.ts` saved:

```bash
echo '12 * 3'       | node calc.ts     # tokens, as before
echo '1 $ 2'        | node calc.ts     # error: unexpected '$' at 1:3
echo '12 + x'       | node calc.ts     # 'x' at 1:6
echo '@'            | node calc.ts     # 1:1 — never 1:0
echo '1 $ 2 # 3'    | node calc.ts     # only the first
echo '  1 $ 2'      | node calc.ts     # 1:5 — the column as typed
```

Then check the claim the module rests on. Replace the main program's `if`/`else`
with module 3's loop, `for (const t of scan(src).tokens) { … }`, and run
`npx tsc --noEmit --strict --noUncheckedIndexedAccess calc.ts`. Read the error:
that is the compiler refusing to let a failed scan be used as a successful one.
Put the `if` back.

Last, a preview of module 17. Run `echo '1 $ 2' | node calc.ts; echo $?`. The
exit code is `0` — the shell thinks it worked. A tool that fails and exits 0
cannot be used in a script, and fixing that is a decision for every kind of
error at once.
""",
    reference="""// calc.ts — module 4
//
// A scanner that can say no. When it meets a character it cannot read, it stops
// and returns a failure naming the character and its column — a VALUE, in the
// return type, so every caller has to decide what a failed scan means.
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

// ERRORS AS VALUES. A discriminated union like Token, tagged by a BOOLEAN
// literal: `ok` is exactly true in one member and exactly false in the other.
// `result.tokens` does not exist until `result.ok` has been checked.
//
// Why not `throw`: an uncaught throw is a crash aimed at the programmer, and it
// is invisible in the type. Module 17 throws once, at the edge; inside, values.
type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };

// THE FORMAT IS CONTRACT from here on: exercises match it exactly, and module
// 17's caret points at the column. Columns count from 1; the cursor from 0.
// Line is always 1 until programs have more than one line.
function unexpected(ch: string, i: number): string {
  return `error: unexpected '${ch}' at 1:${i + 1}`;
}

const DIGITS = "0123456789";

function isDigit(ch: string): boolean {
  return DIGITS.indexOf(ch) !== -1;
}

function scan(src: string): ScanResult {
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
      // Was a silent skip for two modules. Now the scan stops here, at the FIRST
      // character it cannot read, and says which and where.
      return { ok: false, error: unexpected(ch, i) };
    }
  }
  tokens.push(eofToken());
  return { ok: true, tokens: tokens };
}

// trimEnd, not trim: leading spaces stay, so a column is a column of what the
// user TYPED. The scanner already skips them. The trailing newline still goes.
const src = readFileSync(0, "utf8").trimEnd();
const result = scan(src);
// The compiler insists on this `if`. Delete it and `result.tokens` is an error.
if (result.ok) {
  for (const t of result.tokens) {
    console.log(JSON.stringify(t));
  }
} else {
  // stdout for now, so it can be judged. stderr and a non-zero exit code are
  // module 17's — one decision for scan, parse and evaluation errors together.
  console.log(result.error);
}
""",
    stretch=[
        "Report every error, not just the first: collect them in a `string[]` and keep scanning. Then decide what `ok` means when there are some tokens and some errors — and notice why stopping was the simpler place to start.",
        "Make a tab count as whitespace, and then decide what column a character after a tab is in. Editors disagree; pick one and write down why.",
        "Give `ScanResult` a third member for a warning — say, `007` with a leading zero — that still carries tokens. Follow the change to every caller the compiler points at.",
        "Print the error on stderr with `console.error` and exit with `process.exitCode = 1`. It works — and it is module 17's job for a reason: find the two other kinds of error that will need the same treatment.",
        "Write a generic `type Result<T> = { ok: true; value: T } | { ok: false; error: string }` and rewrite `ScanResult` as `Result<Token[]>`. Module 6's parser will want `Result<Expr>`.",
    ],
    glossary=[
        _pgloss("errors as values", "Reporting failure by returning it, in the return type, instead of throwing. Every caller can see the function might fail and must handle it."),
        _pgloss("result type", "A union of a success member carrying the answer and a failure member carrying the reason, tagged so the two can be told apart."),
        _pgloss("boolean literal type", "`true` or `false` used as a type — a field that is always exactly that value. Here it is the result union's tag."),
        _pgloss("1-based column", "Counting the first character on a line as column 1, as people and editors do. The scanner's cursor is 0-based, so the column is `i + 1`."),
        _pgloss("trimEnd", "`s.trimEnd()` — remove whitespace from the end only. Keeps leading spaces, so positions match what was typed."),
        _pgloss("contract", "Output that other things depend on exactly — tests, tools, scripts. Changing it later breaks them all, so it is decided once."),
    ],
    cheatsheet="""
```ts
// success with tokens, or failure with a reason — `ok` is the tag
type ScanResult = { ok: true; tokens: Token[] } | { ok: false; error: string };

// the format is contract. Columns count from 1.
function unexpected(ch: string, i: number): string {
  return `error: unexpected '${ch}' at 1:${i + 1}`;
}

// in scan: the branch that used to skip
} else {
  return { ok: false, error: unexpected(ch, i) };   // first error ends the scan
}
// … and at the end
tokens.push(eofToken());
return { ok: true, tokens: tokens };

// the caller MUST check — result.tokens does not exist until it has
const src = readFileSync(0, "utf8").trimEnd();      // not trim: columns as typed
const result = scan(src);
if (result.ok) {
  for (const t of result.tokens) { console.log(JSON.stringify(t)); }
} else {
  console.log(result.error);
}
```

| Input | Output |
|---|---|
| `1 $ 2` | `error: unexpected '$' at 1:3` |
| `  1 $ 2` | `error: unexpected '$' at 1:5` — as typed |
| `@` | `error: unexpected '@' at 1:1` |
| `1 $ 2 # 3` | only the `$` |
| `12 * 3` | the tokens, no error |

| Symptom | Cause |
|---|---|
| `$` vanishes, no error | the `else` still skips (`i = i + 1`) |
| every column one too small | `i` instead of `i + 1` |
| column wrong only with leading spaces | `.trim()` instead of `.trimEnd()` |
| `Property 'tokens' does not exist on type 'ScanResult'` | reading tokens without `if (result.ok)` |
""",
    self_check=[
        "Can you give the problem with skipping, with throwing, and with a special error token?",
        "Can you write `ScanResult`, and name an object each member refuses?",
        "Can you explain why `result.tokens` does not compile before `if (result.ok)`, and why that is the point?",
        "Can you produce the exact error text for a `#` at cursor position 10?",
        "Can you say what `.trim()` does to the column of the `$` in `  1 $ 2`?",
        "Can you say where the error should really be printed, and which module moves it?",
    ],
    review=[
        _pq("Why does this project return scan failures instead of throwing them — until module 17?",
            ["A returned failure is in the type, so every caller must handle it; an uncaught throw is a crash nobody was made to plan for",
             "Because TypeScript has no `throw`",
             "Returning is faster",
             "Because thrown errors cannot carry a column"],
            0,
            "Module 17 uses `throw` exactly once, at the edge. The rule is values "
            "inside, one catch outside."),
        _pq("`const r: ScanResult = { ok: false, tokens: [] };` — does it compile?",
            ["No — `ok: false` selects the failure member, which has `error` and no `tokens`",
             "Yes",
             "Yes, with `error` defaulting to `\"\"`",
             "Only if `tokens` is non-empty"],
            0,
            "The tag picks the member, and the member decides the fields — module "
            "1's rule, with a boolean for a tag."),
        _pq("The `$` in `1 $ 2` is at cursor position 2. What does the message say, and why?",
            ["`at 1:3` — columns count from 1, the cursor from 0",
             "`at 1:2`",
             "`at 0:2`",
             "`at 2`"],
            0,
            "`i + 1`. Off by one here sends every user to the character before "
            "their mistake."),
        _pq("Why `.trimEnd()` rather than `.trim()`?",
            ["`.trim()` removes leading spaces too, so every column on an indented line is wrong — `  1 $ 2` would say column 3",
             "`.trim()` does not remove newlines",
             "`.trimEnd()` is faster",
             "They are identical for single lines"],
            0,
            "Columns must be positions in what was typed, because module 17 draws "
            "a caret under the typed line."),
        _pq("`1 $ 2 # 3` has two bad characters. What is reported?",
            ["Only the `$` — the scan stops at the first character it cannot read",
             "Both, on two lines",
             "Only the `#`",
             "Neither; the tokens are printed"],
            0,
            "Stopping is the simple, honest choice. Reporting everything needs "
            "recovery, which is its own design."),
    ],
    milestone="Phase 1 is done. Every input gets an honest answer: a list of tokens, "
              "or `error: unexpected '$' at 1:3` naming the character and the column "
              "it was typed in — returned as a value the compiler will not let any "
              "caller ignore.",
))
