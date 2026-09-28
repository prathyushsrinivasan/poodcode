# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 6 — A parser with a cursor.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 4's scanner and module 5's tree.
#
# THE PARSER'S MACHINERY, ON THE SMALLEST GRAMMAR THERE IS: an expression is a
# single number. That is deliberate — peek, advance, the eof guarantee, the parse
# result and the end-of-input check are all new, and none of them should have to
# compete with precedence (module 7) for attention. `1 + 2` is REFUSED here,
# graded, and module 7 opens on it.
#
# THE eof PAYOFF, SAID OUT LOUD (the roadmap asks for it). Under
# noUncheckedIndexedAccess `p.tokens[p.pos]` is `Token | undefined`. `peek`
# handles that once, and because the scanner always ends the list with exactly
# one eof and `advance` refuses to move past it, nothing else in the parser ever
# holds a `Token | undefined`. Module 1 made that decision four modules ago.
#
# THE POSITION DECISION CALC_ROADMAP.md FLAGGED. Tokens carry no positions, so a
# parse error cannot name a column. Decided: parse errors say WHAT was found —
# `error: unexpected '+'`, `error: unexpected end of input` — and not where,
# until module 16 retrofits positions onto every token. Scan errors keep their
# `at 1:C`, because the scanner has its cursor in hand. The inconsistency is
# stated in step 2 as a cost, deliberately left for module 16 to pay.
#
# `Failure` IS NAMED HERE. `ScanResult` and the new `ParseResult` share their
# failure member, so it gets a name once; module 16 changes it in one place.
# A generic `Result<T>` stays a stretch item.
#
# `describe` IS AN if-CHAIN WITH A FALL-THROUGH TO "end of input". It is correct
# today and becomes wrong in module 8 when parentheses arrive — which module 8
# grades as a fix, and which module 10 then makes impossible.
# ---------------------------------------------------------------------------

_C6_RESULTS = """type Failure = { ok: false; error: string };
type ScanResult = { ok: true; tokens: Token[] } | Failure;
"""

_C6_TREE = _C5_TYPES + "\n" + _C5_FACTORIES + "\n" + _C5_SHOW

_C6_STATE = """type Parser = { tokens: Token[]; pos: number };

function peek(p: Parser): Token {
  const t = p.tokens[p.pos];
  if (t === undefined) {
    return eofToken();
  }
  return t;
}

function advance(p: Parser): Token {
  const t = peek(p);
  if (t.kind !== "eof") {
    p.pos = p.pos + 1;
  }
  return t;
}
"""

_C6_DESCRIBE = """function describe(t: Token): string {
  if (t.kind === "number") {
    return `'${t.value}'`;
  }
  if (t.kind === "op") {
    return `'${t.op}'`;
  }
  return "end of input";
}

function unexpectedToken(t: Token): Failure {
  return { ok: false, error: `error: unexpected ${describe(t)}` };
}
"""

_C6_PRIMARY = """type ParseResult = { ok: true; expr: Expr } | Failure;

function parsePrimary(p: Parser): ParseResult {
  const t = advance(p);
  if (t.kind === "number") {
    return { ok: true, expr: num(t.value) };
  }
  return unexpectedToken(t);
}
"""

_C6_PARSE = """function parse(tokens: Token[]): ParseResult {
  const p: Parser = { tokens: tokens, pos: 0 };
  const result = parsePrimary(p);
  if (!result.ok) {
    return result;
  }
  const next = peek(p);
  if (next.kind !== "eof") {
    return unexpectedToken(next);
  }
  return result;
}
"""

_C6_PARSE_EARLY = """function parse(tokens: Token[]): ParseResult {
  const p: Parser = { tokens: tokens, pos: 0 };
  return parsePrimary(p);
}
"""

_C6_RUN = """function run(src: string): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return scanned.error;
  }
  const parsed = parse(scanned.tokens);
  if (!parsed.ok) {
    return parsed.error;
  }
  return show(parsed.expr);
}

console.log(run(readFileSync(0, "utf8").trimEnd()));
"""


def _cjoin(*parts):
    return "\n".join(p.rstrip("\n") + "\n" for p in parts if p)


def _c6(parse=_C6_PARSE, state=_C6_STATE, describe=_C6_DESCRIBE,
        primary=_C6_PRIMARY, run=_C6_RUN):
    return _stdin(_cjoin(_C_TOKENS, _C6_RESULTS, _C4_UNEXPECTED, _C4_SCAN, _C6_TREE,
                         state, describe, primary, parse, run))


_C6_FULL = _c6()

_C6_INPUTS = ["42", "7", "  12", "007", "", "+", "1 + 2", "3 4", "1 $ 2"]
_C6_TESTS = _ctests(6, _C6_INPUTS)
# Step 3's program has no end check yet, so only inputs with nothing after the
# number are fair to it.
_C6_S3_TESTS = _ctests(6, ["42", "7", "  12", "", "+", "1 $ 2"])

# --- Step 1's plain program: walking a hand-made token list -----------------
_C6_S1_MAIN = """const p: Parser = {
  tokens: [numberToken(1), opToken("+"), numberToken(2), eofToken()],
  pos: 0,
};

console.log(peek(p).kind);
console.log(advance(p).kind);
console.log(peek(p).kind);
advance(p);
advance(p);
console.log(advance(p).kind);
console.log(advance(p).kind);
console.log(p.pos);
"""
_C6_S1_OUT = "number\nnumber\nop\neof\neof\n3"


def _c6_s1(state=_C6_STATE):
    return _plain(_cjoin(_C_TOKENS, state, _C6_S1_MAIN))


# --- Step 2's plain program: what the parser says ---------------------------
_C6_S2_MAIN = """console.log(describe(numberToken(12)));
console.log(describe(opToken("*")));
console.log(describe(eofToken()));
console.log(unexpectedToken(opToken("+")).error);
console.log(unexpectedToken(eofToken()).error);
"""
_C6_S2_OUT = "'12'\n'*'\nend of input\nerror: unexpected '+'\nerror: unexpected end of input"


def _c6_s2(describe=_C6_DESCRIBE):
    return _plain(_cjoin(_C_TOKENS, "type Failure = { ok: false; error: string };\n",
                         describe, _C6_S2_MAIN))


_C6_WHY = (
    "Module 5 designed the tree and built every one of them by hand. Something "
    "has to build them from tokens, and that something needs machinery of its "
    "own before it can do anything clever: a cursor into the token list, a way to "
    "look at the next token without taking it, a way to take it, a result that "
    "can fail, and a rule for what happens when the input keeps going after the "
    "expression is finished. This module builds all of it — on a grammar so small "
    "that an expression is a single number — so that module 7 can spend itself "
    "entirely on precedence."
)

_C6_BRIEF = """
### The whole module in one line

Read a list of tokens with a cursor, turn a single number into an `Expr`, and
refuse — with a message — anything that is not exactly that.

### A scanner for tokens

The scanner walked characters with a cursor `i`. The parser walks **tokens** the
same way, with two operations:

| Operation | Does | Scanner equivalent |
|---|---|---|
| `peek(p)` | returns the next token, and leaves it there | `src.charAt(i)` |
| `advance(p)` | returns the next token, and moves past it | `src.charAt(i)` then `i = i + 1` |

Every parser ever written is built on these two. Peek to decide; advance to
commit.

### Module 1's `eof`, paid off

```ts
const t = p.tokens[p.pos];      // Token | undefined — the flag you turned on in setup
```

Indexing an array can miss, and the compiler says so. A parser that checks for
`undefined` at every step is a parser with thirty `if`s that are not about the
language. So `peek` checks **once**, and because the scanner always ends the list
with exactly one `eof` — and `advance` refuses to move past it — the answer to
"what comes next?" is always a real `Token`. Past the end of the input, it is
`eof`, forever.

That is a decision module 1 made four modules ago, for exactly this moment.

### A result that can fail

```ts
type Failure = { ok: false; error: string };
type ScanResult  = { ok: true; tokens: Token[] } | Failure;
type ParseResult = { ok: true; expr: Expr }      | Failure;
```

Module 4's pattern again — errors as values — with the failure half given a name
now that two results share it.

### What the parser says, and what it cannot yet say

```
$ echo '1 + 2' | node calc.ts
error: unexpected '+'
```

A parse error says **what** it found. It cannot say **where**: tokens do not
remember their positions — module 1 threw them away. That is a real cost, stated
in step 2 and paid in module 16.

### The grammar, for now

An expression is a number. `42` parses; `1 + 2` does not, and the parser says so
rather than quietly returning the `1`. Module 7 is where `+` stops being
unexpected.
"""

_C6_SYNTAX = [
    _syn(
        "type Parser = { tokens: Token[]; pos: number };",
        "The parser's state: the list it is reading and how far it has got. One "
        "object, passed to every parsing function, so they all share one cursor.",
        """
const p: Parser = { tokens: [numberToken(7), eofToken()], pos: 0 };
""",
        "`p.pos = p.pos + 1` inside a function changes the object the caller "
        "passed in — every function holding `p` sees the new position. That "
        "sharing is exactly what a cursor needs.",
    ),
    _syn(
        "if (t === undefined) { return eofToken(); }",
        "Handle the `undefined` an array index can produce — once, in `peek`, so "
        "nothing else in the parser has to.",
        """
const t = p.tokens[p.pos];     // Token | undefined
if (t === undefined) {
  return eofToken();
}
return t;                      // Token
""",
        "After the `if`, `t` is narrowed to `Token`. `undefined` is a value you can "
        "compare against like any other; `===` is the way to do it.",
    ),
    _syn(
        "type Failure = { ok: false; error: string };",
        "The failure half of every result, named once. `ScanResult` and "
        "`ParseResult` both end in `| Failure`.",
        """
type ScanResult = { ok: true; tokens: Token[] } | Failure;
type ParseResult = { ok: true; expr: Expr } | Failure;
""",
        "A failure from one stage can be returned from another unchanged: once "
        "`!scanned.ok` has narrowed it, `scanned` is a `Failure`, which is a valid "
        "`ParseResult` too.",
    ),
    _syn(
        "if (!result.ok) { return result; }",
        "Pass a failure straight up to your own caller. The single most repeated "
        "line in a program that returns its errors.",
        """
const result = parsePrimary(p);
if (!result.ok) {
  return result;          // a Failure: hand it on untouched
}
result.expr;              // only exists past this point
""",
        "`!` flips a boolean. After the `if`, only the success member is left.",
    ),
    _syn(
        "`error: unexpected ${describe(t)}`",
        "A parse error: what was found, in the project's message style — with no "
        "column, because tokens do not carry one yet.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — the cursor.
# ---------------------------------------------------------------------------

_C6_S1 = _pstep(
    "cursor", "A cursor over tokens",
    "`Parser`, `peek` and `advance` — and the one `undefined` check in the whole parser.",
    """
The scanner's state was a string and an index. The parser's is a list and an
index, put in one object so every parsing function can share it:

```ts
type Parser = { tokens: Token[]; pos: number };
```

### Looking without taking

```ts
function peek(p: Parser): Token {
  const t = p.tokens[p.pos];
  if (t === undefined) {
    return eofToken();
  }
  return t;
}
```

`p.tokens[p.pos]` has type `Token | undefined` — `noUncheckedIndexedAccess`
refusing to assume an index is in range. This is the only place in the parser
that will ever deal with that. If the cursor is somehow past the end, the answer
is `eof`: past the end of the input, the input has ended.

In practice that branch cannot run, because of two guarantees:

1. The scanner always ends the list with **exactly one** `eof` (module 2).
2. `advance` **will not move past** it (below).

So the cursor always points at a real token, and the last real token is `eof`.
The compiler cannot see either guarantee — they are facts about how other
functions behave — so the check stays. But it is written once, here, and every
function built on `peek` gets a plain `Token`.

### Taking

```ts
function advance(p: Parser): Token {
  const t = peek(p);
  if (t.kind !== "eof") {
    p.pos = p.pos + 1;
  }
  return t;
}
```

Take the next token and move past it — unless it is `eof`, which stays put. Ask
for the next token at the end of the input as many times as you like; you get
`eof` every time, and the cursor does not wander off into `undefined`.

### Why `p.pos = p.pos + 1` works across functions

`p` is an object. Passing it to `advance` passes *the same object*, not a copy,
so when `advance` moves the cursor, the caller's `p` has moved too. That is what
lets `parsePrimary`, and later `parseSum` and `parseProduct`, all read one stream
of tokens in turn.
""",
    """
```
number
number
op
eof
eof
3
```

After three advances the cursor sits on `eof` at position 3, and two more
advances leave it there.
""",
    pitfalls=[
        "`return p.tokens[p.pos];` from `peek` with no check. It does not compile under this project's settings — and without the setting it compiles and hands `undefined` to code expecting a token.",
        "`advance` that always moves: the cursor walks past the `eof` into `undefined`, and `pos` stops meaning anything. `peek` still papers over it, which makes the bug hard to see — until something reads `pos`.",
        "Using a global `let pos = 0` instead of a `Parser` object. It works for one parse and quietly breaks the second, which starts wherever the first stopped.",
        "Writing `p.tokens[p.pos]!` to silence the compiler. The `!` is a promise with nothing behind it; the check in `peek` is the promise kept.",
    ],
    warmup=[
        _pq("The token list is `[num 5, eof]` and `pos` is 1. What does `advance(p)` return, and what is `pos` afterwards?",
            ["`eof`, and `pos` stays 1 — advance does not move past the end",
             "`undefined`, and `pos` becomes 2",
             "`eof`, and `pos` becomes 2",
             "It throws"],
            0,
            "`eof` is a floor. That is what makes `peek` always return a real token."),
    ],
    exercises=[
        _pex("calc-m6-cursor-1", "The one undefined check",
             "Finish `peek`: when the cursor is past the end of the list, the next "
             "token is the end of the input.",
             _c6_s1(),
             "  if (t === undefined) {\n    return eofToken();\n  }",
             [("", _C6_S1_OUT)],
             ["`t` has type `Token | undefined`. Handle the second half.",
              "Past the end, the answer is an `eof` token.",
              "`if (t === undefined) { return eofToken(); }`"]),
        _pex("calc-m6-cursor-2", "Stop at the end",
             "Finish `advance`: move the cursor on — but not past the `eof`.",
             _c6_s1(),
             '  if (t.kind !== "eof") {\n    p.pos = p.pos + 1;\n  }',
             [("", _C6_S1_OUT)],
             ["The cursor moves by one, except in one case.",
              "Which token must the cursor stay on?",
              "`if (t.kind !== \"eof\") { p.pos = p.pos + 1; }`"]),
        _pfix("calc-m6-cursor-fix1", "A cursor that walks off the end",
              "Every token prints correctly — `peek` makes sure of that. But after "
              "five advances over a four-token list, `pos` is 5: pointing at "
              "nothing.",
              _c6_s1(_C6_STATE.replace('  if (t.kind !== "eof") {\n    p.pos = p.pos + 1;\n  }',
                                       "  p.pos = p.pos + 1;")),
              _c6_s1(),
              [("", _C6_S1_OUT)],
              ["Which function moves the cursor?",
               "It moves it every time — even when the token it just returned was `eof`.",
               "`if (t.kind !== \"eof\") { p.pos = p.pos + 1; }`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why can the rest of the parser work with a plain `Token` instead of `Token | undefined`?",
            ["The scanner always ends the list with one `eof`, `advance` never moves past it, and `peek` handles the impossible case once",
             "Because arrays in TypeScript never return undefined",
             "Because `noUncheckedIndexedAccess` is off inside functions",
             "Because `Token` includes `undefined`"],
            0,
            "Two guarantees and one check. Module 1 put the `eof` there for this."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — what the parser says.
# ---------------------------------------------------------------------------

_C6_S2 = _pstep(
    "describe", "What the parser says",
    "Naming a token in a message — and the column a parse error cannot give yet.",
    """
When the parser gets a token it did not want, the message names it:

```
error: unexpected '+'
error: unexpected '4'
error: unexpected end of input
```

Same style as module 4 — `error:` prefix, the thing in quotes — built from a
function that turns any token into the words for it:

```ts
function describe(t: Token): string {
  if (t.kind === "number") {
    return `'${t.value}'`;
  }
  if (t.kind === "op") {
    return `'${t.op}'`;
  }
  return "end of input";
}
```

`eof` is not quoted. The user never typed an `eof`; they typed nothing, and
*end of input* says that in words. Quoting it — `unexpected 'eof'` — would name a
thing that is not in their program.

```ts
function unexpectedToken(t: Token): Failure {
  return { ok: false, error: `error: unexpected ${describe(t)}` };
}
```

### The column it cannot give

Module 4's messages end `at 1:3`. This one does not, and cannot: a `Token` is
`{ kind: "op", op: "+" }` and nothing else. The scanner knew where the `+` was;
it did not write it down.

There were two ways to go:

| Option | Cost |
|---|---|
| Pass a list of positions next to the tokens, starting now | every parsing function carries two lists that must stay in step |
| Report *what*, not *where*, until tokens carry positions | `1 + +` says `unexpected '+'` without saying which `+` |

This project takes the second, on purpose, and says so. Module 16 adds a
position to every token — and because tokens are only ever built by the four
factories from module 1, that change touches the factories and almost nothing
else. The cost is real for ten modules; the fix, when it comes, is small.

### A fall-through worth noticing

`describe`'s last line handles everything that is not a number or an operator —
which today means `eof`. Keep an eye on that line. It is correct right now, and
the next time the `Token` union grows, it will quietly describe the new kind as
"end of input".
""",
    """
```
'12'
'*'
end of input
error: unexpected '+'
error: unexpected end of input
```

Tokens in quotes, the end of the input in words.
""",
    pitfalls=[
        "Printing the token as JSON: `unexpected {\"kind\":\"op\",\"op\":\"+\"}`. Accurate, and written for the programmer rather than the person who typed `1 +`.",
        "Quoting the end: `unexpected 'eof'`. There is no `eof` in anything the user typed.",
        "Faking a column — `at 1:0`, or the token's index in the list. An index into the token list is not a column, and a wrong column is worse than none.",
        "Building the message inline wherever an error happens. `unexpectedToken` is the one place the format lives, exactly as `unexpected` was for the scanner.",
    ],
    warmup=[
        _pq("Why does a parse error in this module have no `at 1:N`?",
            ["Tokens do not record where they came from, so the parser has nothing to report — module 16 adds positions",
             "Parse errors do not have positions",
             "Because the column is always 1",
             "To keep the message short"],
            0,
            "The scanner knew and threw it away. Carrying it is module 16's job."),
    ],
    exercises=[
        _pex("calc-m6-describe-1", "Name the operator",
             "Finish `describe` for an operator token: the symbol, in single "
             "quotes.",
             _c6_s2(),
             "    return `'${t.op}'`;",
             [("", _C6_S2_OUT)],
             ["Inside the `if`, `t` is an `OpToken`.",
              "Same shape as the number case, with a different field.",
              "`return `'${t.op}'`;`"]),
        _pex("calc-m6-describe-2", "The failure, built once",
             "Finish `unexpectedToken`: a `Failure` whose message is `error: "
             "unexpected ` followed by the description.",
             _c6_s2(),
             "  return { ok: false, error: `error: unexpected ${describe(t)}` };",
             [("", _C6_S2_OUT)],
             ["It returns the failure member: `ok` is `false`.",
              "`describe(t)` already includes the quotes.",
              "`return { ok: false, error: `error: unexpected ${describe(t)}` };`"]),
        _pfix("calc-m6-describe-fix1", "The token nobody typed",
              "`unexpectedToken(eofToken())` says `error: unexpected 'eof'`. The "
              "user typed `1 +` and stopped — there is no `eof` anywhere in what "
              "they wrote.",
              _c6_s2(_C6_DESCRIBE.replace('  return "end of input";', "  return `'${t.kind}'`;")),
              _c6_s2(),
              [("", _C6_S2_OUT)],
              ["Which line handles the `eof` token?",
               "It quotes the kind, as if it were something typed.",
               "The end of the input is described in words: `end of input`."],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does this project accept parse errors without columns for ten modules?",
            ["Threading positions alongside tokens now costs every parsing function; adding them to tokens later touches only the factories",
             "Because nobody needs columns",
             "Because the parser cannot count",
             "It does not — module 7 adds them"],
            0,
            "A cost taken knowingly, with the payment scheduled. Module 16 is the "
            "payment."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a primary, and the parse result.
# ---------------------------------------------------------------------------

_C6_S3 = _pstep(
    "primary", "One number, parsed",
    "`ParseResult`, and `parsePrimary`: the smallest complete expression.",
    """
The parser's job is to return an `Expr` — or say why it could not:

```ts
type ParseResult = { ok: true; expr: Expr } | Failure;
```

The smallest thing that is a complete expression on its own is called a
**primary**. Today there is exactly one kind: a number. (Module 8 adds a
bracketed expression; later modules add names and `true`.)

```ts
function parsePrimary(p: Parser): ParseResult {
  const t = advance(p);
  if (t.kind === "number") {
    return { ok: true, expr: num(t.value) };
  }
  return unexpectedToken(t);
}
```

Take a token. If it is a number, it becomes a number *node* — the token's value,
in module 5's factory. Anything else cannot start an expression, and the parser
says which thing it found.

### A token becomes a node

This line is the whole of phase 2 in miniature:

```ts
num(t.value)
```

`t` is a `NumberToken`, `{ kind: "number", value: 42 }` — text that was a
number. The result is a `NumLit`, `{ kind: "num", value: 42 }` — a number in a
tree. Same value; different stage of the pipeline; different tag, so the two can
never be mixed up.

### Two stages, one pipeline

The program now has two stages that can each fail, and a function that runs
them in order:

```ts
function run(src: string): string {
  const scanned = scan(src);
  if (!scanned.ok) {
    return scanned.error;
  }
  const parsed = parse(scanned.tokens);
  if (!parsed.ok) {
    return parsed.error;
  }
  return show(parsed.expr);
}
```

Each stage's failure ends the run with its message. Only a program that survives
both gets printed. Module 9 adds a third stage to this same function.
""",
    """
```bash
$ echo '42' | node calc.ts
42
$ echo '+' | node calc.ts
error: unexpected '+'
$ echo '' | node calc.ts
error: unexpected end of input
```

A number parses to itself. Anything else is refused by name.
""",
    pitfalls=[
        "Returning the token instead of a node: `{ ok: true, expr: t }`. It does not compile — a `NumberToken` is not an `Expr`, and the different tags are why.",
        "Using `peek` instead of `advance` for the number. The number is parsed but never consumed, so whatever comes next sees it again.",
        "Printing the error from inside `parsePrimary`. The parser returns failures; the one `console.log` is at the end of the program.",
        "Forgetting the empty input. `advance` on `[eof]` returns `eof`, which is not a number — so the answer is `unexpected end of input`, not a crash.",
    ],
    warmup=[
        _pq("What does `parsePrimary` return for the tokens `[op *, num 2, eof]`?",
            ["A failure: `error: unexpected '*'` — an expression cannot start with `*`",
             "The number 2",
             "A `Binary` for `* 2`",
             "`undefined`"],
            0,
            "A primary is a number, here. A `*` cannot start one."),
    ],
    exercises=[
        _pex("calc-m6-primary-1", "A token becomes a node",
             "In `parsePrimary`, a number token becomes a successful result "
             "holding a number *node*.",
             _c6(parse=_C6_PARSE_EARLY),
             "    return { ok: true, expr: num(t.value) };",
             _C6_S3_TESTS,
             ["The success member of `ParseResult` has `ok: true` and an `expr`.",
              "Module 5's factory turns a value into a `NumLit`.",
              "`return { ok: true, expr: num(t.value) };`"]),
        _pex("calc-m6-primary-2", "What parsing returns",
             "Declare `ParseResult`: either a tree, or a `Failure`.",
             _c6(parse=_C6_PARSE_EARLY),
             "type ParseResult = { ok: true; expr: Expr } | Failure;",
             _C6_S3_TESTS,
             ["`ScanResult` is the model — a success member, `| Failure`.",
              "The success carries an `expr` of type `Expr`.",
              "`type ParseResult = { ok: true; expr: Expr } | Failure;`"]),
    ],
    quiz=[
        _pq("Why does `num(t.value)` exist instead of reusing the token as the node?",
            ["Tokens and nodes are different stages with different tags; building a node keeps them from being confused",
             "Because tokens cannot hold numbers",
             "To copy the value for safety",
             "No reason; it could return the token"],
            0,
            "A `NumberToken` is not an `Expr`, and the compiler holds you to it."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — expecting the end.
# ---------------------------------------------------------------------------

_C6_S4 = _pstep(
    "end", "Expecting the end",
    "A parser that stops early accepts `1 + 2` as `1`. Check that nothing is left.",
    """
With only `parsePrimary`, `1 + 2` parses successfully — as `1`. The parser took
one number, returned, and nobody looked at the `+ 2` still sitting in the list.
That is not a small bug. It is a parser that silently deletes most of a program.

So parsing a whole input is: parse an expression, then **expect the end**:

```ts
function parse(tokens: Token[]): ParseResult {
  const p: Parser = { tokens: tokens, pos: 0 };
  const result = parsePrimary(p);
  if (!result.ok) {
    return result;
  }
  const next = peek(p);
  if (next.kind !== "eof") {
    return unexpectedToken(next);
  }
  return result;
}
```

After the expression, the only acceptable next token is `eof`. Anything else was
left over, and the first leftover token is the one to complain about:

```
$ echo '1 + 2' | node calc.ts
error: unexpected '+'
```

That message is exactly right for *this* grammar: in a language where an
expression is a number, a `+` after one is unexpected. Module 7 changes the
grammar; the check stays.

### `peek`, not `advance`

The end check only looks. Nothing is consumed, because on success there is
nothing to consume, and on failure the parse is over. Peek to decide; advance to
commit — and here there is nothing to commit to.

### Where this leaves the program

```bash
echo '42'    | node calc.ts    # 42
echo '1 + 2' | node calc.ts    # error: unexpected '+'
echo '1 $ 2' | node calc.ts    # error: unexpected '$' at 1:3  — the scanner, first
```

Notice the last one. The scanner runs first and fails first, so a bad character
is reported even when the parser would also have objected. Stages report in
pipeline order.
""",
    """
```bash
$ echo '1 + 2' | node calc.ts
error: unexpected '+'
$ echo '3 4' | node calc.ts
error: unexpected '4'
$ echo '007' | node calc.ts
7
```

`1 + 2` is refused — correctly, for now. Module 7 is where it stops being.
""",
    pitfalls=[
        "No end check. `1 + 2` prints `1`, and the user has no idea two thirds of their input was thrown away.",
        "Checking `p.pos === p.tokens.length`. The cursor stops ON the `eof`, never past it, so that is never true. Ask the token, not the index.",
        "Reporting the leftover as `expected end of input`. True, but `unexpected '+'` names the thing the user actually typed.",
        "`advance` instead of `peek` in the check — harmless today, and the habit that consumes a token a later check needed.",
    ],
    warmup=[
        _pq("Without an end check, what does `1 + 2` parse to?",
            ["The number 1 — the rest of the input is silently ignored",
             "An error",
             "The tree `(+ 1 2)`",
             "The number 3"],
            0,
            "A parser that stops early loses input without a word. The end check "
            "is what makes it say something."),
    ],
    exercises=[
        _pex("calc-m6-end-1", "Nothing may be left over",
             "After the expression, the next token must be the end of the input. "
             "If it is not, fail with that token.",
             _C6_FULL,
             '  const next = peek(p);\n  if (next.kind !== "eof") {\n    return unexpectedToken(next);\n  }',
             _C6_TESTS,
             ["Look at the next token without consuming it.",
              "Only one kind of token is allowed here.",
              "`const next = peek(p); if (next.kind !== \"eof\") { return unexpectedToken(next); }`"]),
        _pfix("calc-m6-end-fix1", "Two thirds of the program, gone",
              "`echo '1 + 2' | node calc.ts` prints `1`. The parser read one number "
              "and returned, and the `+ 2` vanished.",
              _c6(parse=_C6_PARSE_EARLY),
              _C6_FULL,
              _C6_TESTS,
              ["After `parsePrimary` succeeds, is anything checked?",
               "A complete parse ends at `eof`.",
               "Pass on a failure, then peek: anything but `eof` is `unexpectedToken`."],
              difficulty="Easy"),
        _pch("calc-m6-end-run", "Scan, then parse, then print", "Easy",
             "Write `run`: scan the source, parse the tokens, and return the "
             "tree printed by `show` — or the first stage's error, whichever "
             "stage fails first.",
             _C6_FULL,
             _C6_RUN.split("\n\nconsole.log")[0],
             _C6_TESTS,
             ["`const scanned = scan(src);` — on failure, return `scanned.error`.",
              "After that check, `scanned.tokens` exists.",
              "Same again for `parse`, then `return show(parsed.expr);`."]),
    ],
    quiz=[
        _pq("`1 $ 2` has a bad character AND would fail to parse. Which error is printed?",
            ["The scanner's — `error: unexpected '$' at 1:3` — because scanning runs first and the run stops at the first failure",
             "The parser's",
             "Both",
             "Neither"],
            0,
            "Stages fail in pipeline order. The parser never sees a program the "
            "scanner rejected."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C6_BUILD_BLANK = _cjoin(_C6_STATE, _C6_DESCRIBE, _C6_PRIMARY, _C6_PARSE).rstrip("\n")

_C6_FINAL = _pch(
    "calc-m6-build", "Module 6 build — a parser with a cursor", "Medium",
    "Write the parser, between `show` and `run`:\n\n"
    "* `Parser`, `peek` and `advance` — the cursor, with `eof` as a floor\n"
    "* `describe` and `unexpectedToken` — `error: unexpected '+'`, `error: "
    "unexpected end of input`\n"
    "* `ParseResult` and `parsePrimary` — a number token becomes a number node\n"
    "* `parse` — a primary, then nothing but `eof`\n\n"
    "The scanner, the tree and `run` are given.",
    _C6_FULL,
    _C6_BUILD_BLANK,
    _C6_TESTS + _ctests(6, ["99 *", "*"]),
    ["`peek` is the only place that checks for `undefined`.",
     "`advance` moves the cursor unless the token is `eof`.",
     "`describe`: numbers and operators in quotes, anything else is `end of input`.",
     "`parse` makes a `Parser` at position 0, parses a primary, passes on a failure, then peeks for `eof`."],
)


_CALC_MODULES.append(_pmod(
    key="calc-cursor", number=6, phase="parse",
    title="A parser with a cursor",
    what="peek, advance and expect — reading a list of tokens in order",
    goal="Parse a single number token into an `Expr`, and refuse everything else by name.",
    why=_C6_WHY,
    est_minutes=40,
    builds_on=["calc-scan-errors", "calc-tree"],
    concepts=["parser state", "peek and advance", "sentinel token", "parse result",
              "primary expression", "end-of-input check", "pipeline of results"],
    deliverable="`calc.ts` scans AND parses: `42` prints `42`, `1 + 2` prints "
                "`error: unexpected '+'`, and an empty input says it ended early.",
    objectives=[
        "Write `peek` and `advance`, and say why `advance` stops at `eof`",
        "Explain how module 1's `eof` means only one function in the parser handles `undefined`",
        "Build parse errors that name the token found, and say why they carry no column yet",
        "Name a shared `Failure` type and pass a failure up unchanged",
        "Turn a number token into a number node, and say why they have different tags",
        "Check for leftover input, and give the input that shows why the check is needed",
    ],
    brief=_C6_BRIEF,
    syntax=_C6_SYNTAX,
    steps=[_C6_S1, _C6_S2, _C6_S3, _C6_S4],
    final_build=_C6_FINAL,
    acceptance=[
        "`echo '42' | node calc.ts` prints `42`, and `echo '007'` prints `7`.",
        "`echo '1 + 2' | node calc.ts` prints `error: unexpected '+'` — not `1`.",
        "`echo '' | node calc.ts` prints `error: unexpected end of input`.",
        "`echo '1 $ 2' | node calc.ts` still prints the scanner's error, with its column.",
        "`peek` is the only function that compares a token with `undefined`.",
        "`advance` called at the end of the input any number of times returns `eof` and leaves `pos` where it was.",
    ],
    manual_test="""
With the parser in `calc.ts`:

```bash
echo '42'      | node calc.ts     # 42
echo '  12'    | node calc.ts     # 12
echo ''        | node calc.ts     # error: unexpected end of input
echo '+'       | node calc.ts     # error: unexpected '+'
echo '1 + 2'   | node calc.ts     # error: unexpected '+'   — for now
echo '3 4'     | node calc.ts     # error: unexpected '4'
echo '1 $ 2'   | node calc.ts     # the scanner's error, first
```

Then prove the end check earns its place: comment out the three lines in `parse`
that peek for `eof`, and run `echo '1 + 2' | node calc.ts` again. It prints `1`.
Put them back.

Last, notice what you cannot find out: in `echo '1 + +'`, which `+` is the
parser complaining about? Nothing in the message says. That is the cost this
module chose, and module 16 is where it is paid.
""",
    reference="""// calc.ts — module 6
//
// Text -> tokens -> tree. The parser reads tokens with a cursor (peek to look,
// advance to take), and for now an expression is a single number. Anything else
// is refused by name; `1 + 2` is refused on purpose, until module 7.
""" + _C6_FULL,
    stretch=[
        "Write `expect(p, kind)` that advances past a token of the given kind or fails with `error: expected … but found …`. You will want it in module 8 — and you will find out what it costs to make one function work for every token kind.",
        "Make `ScanResult` and `ParseResult` one generic type: `type Result<T> = { ok: true; value: T } | Failure`. Every `.tokens` and `.expr` becomes `.value`; decide whether the loss of the descriptive name is worth it.",
        "Add a `--tokens` mode: if the source starts with `#tokens `, print the token list instead of parsing. Every real compiler has a flag like this, because it is how you find out which phase is lying to you.",
        "Report every leftover token, not just the first: `error: unexpected '+', '2'`. Then decide whether that is more useful or just longer.",
    ],
    glossary=[
        _pgloss("parser", "The stage that turns a flat list of tokens into a tree, or says why it cannot."),
        _pgloss("peek", "Look at the next token without consuming it."),
        _pgloss("advance", "Consume the next token and return it. Here, it never moves past `eof`."),
        _pgloss("sentinel", "A special value marking the end of a sequence — here, the `eof` token — so code reading the sequence never has to check the length."),
        _pgloss("primary", "The smallest complete expression. For now, a number."),
        _pgloss("leftover input", "Tokens after a complete expression. A parser must check for them, or it silently ignores part of the program."),
    ],
    cheatsheet="""
```ts
type Parser = { tokens: Token[]; pos: number };

function peek(p: Parser): Token {              // the ONLY undefined check
  const t = p.tokens[p.pos];
  if (t === undefined) { return eofToken(); }
  return t;
}
function advance(p: Parser): Token {           // eof is a floor
  const t = peek(p);
  if (t.kind !== "eof") { p.pos = p.pos + 1; }
  return t;
}

type Failure = { ok: false; error: string };
type ParseResult = { ok: true; expr: Expr } | Failure;

// parse = one expression, then nothing but eof
const result = parsePrimary(p);
if (!result.ok) { return result; }             // pass failures up untouched
const next = peek(p);
if (next.kind !== "eof") { return unexpectedToken(next); }
```

| Input | Output |
|---|---|
| `42` | `42` |
| `1 + 2` | `error: unexpected '+'` |
| (empty) | `error: unexpected end of input` |
| `1 $ 2` | `error: unexpected '$' at 1:3` — the scanner fails first |

| Symptom | Cause |
|---|---|
| `1 + 2` prints `1` | no end check in `parse` |
| `pos` larger than the list | `advance` moves past `eof` |
| `unexpected 'eof'` | `describe` quoting the kind of the end token |
""",
    self_check=[
        "Can you write `peek` and `advance`, and say which one protects the other?",
        "Can you explain why nothing else in the parser checks for `undefined`?",
        "Can you give the message for `3 4`, and say why it has no column?",
        "Can you say what `1 + 2` parses to without the end check?",
        "Can you explain why a scan error is reported before a parse error on the same input?",
    ],
    review=[
        _pq("What is the difference between `peek` and `advance`?",
            ["`peek` returns the next token and leaves the cursor; `advance` returns it and moves past it",
             "`peek` returns the previous token",
             "`advance` skips a token without returning it",
             "There is none"],
            0,
            "Peek to decide, advance to commit."),
        _pq("Why does `advance` not move past `eof`?",
            ["So the cursor always points at a real token and asking past the end keeps answering `eof`",
             "Because `eof` cannot be read",
             "To save memory",
             "It does move past it"],
            0,
            "The floor under the cursor. With it, `peek`'s `undefined` branch "
            "cannot run."),
        _pq("A parse error says `error: unexpected '+'`. Why not `at 1:3` like a scan error?",
            ["Tokens do not carry positions yet; the parser has nothing to report until module 16",
             "Parse errors are less important",
             "Because the `+` might be anywhere",
             "It should; this is a bug"],
            0,
            "A decision, not an oversight, and one with a scheduled fix."),
        _pq("What does `if (!result.ok) { return result; }` do?",
            ["Passes a failure up to the caller unchanged, so only a success continues past the `if`",
             "Retries the parse",
             "Converts the failure into a success",
             "Prints the error"],
            0,
            "The line that makes errors-as-values bearable: one `if` per call that "
            "can fail."),
        _pq("Why is `1 + 2` an error in this module?",
            ["The grammar is just a number; after it, the end check finds a `+`",
             "Because `+` is not a token",
             "Because the scanner rejects it",
             "It is not an error"],
            0,
            "Correct for this grammar. Module 7 is where `+` becomes expected."),
    ],
    milestone="`calc.ts` parses. Only single numbers, and it knows it — `1 + 2` is "
              "refused by name rather than quietly shortened to `1`. The cursor, the "
              "`eof` floor, the result type and the end check are all in place; "
              "module 7 builds precedence on top of them.",
))
