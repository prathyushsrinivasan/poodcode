# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Calc · Module 12 — Variables and an environment.
#
# exec()'d by tools/calc_project.py inside the shared namespace; appends one
# module to `_CALC_MODULES`. Reuses module 11's program.
#
# NAMES, AND WHAT THEY MEAN. A new token kind (`ident`), a new node kind (`var`),
# and an environment — `Map<string, number>` — that `evaluate` now carries down
# the tree. `Map.get` returns `number | undefined`, and here that `undefined` is
# not an annoyance to be silenced: it IS the undefined-variable error, the first
# error in the project raised by something other than syntax or arithmetic.
#
# WHAT IS NOW LEGAL (`_CALC_SCOPE_RULES` at 12): `new Map`, `.set(`, `.get(`.
#
# WHERE BINDINGS COME FROM. `let` needs statements and `;`, which are module
# 13's. So this module's judged programs start with an environment the program
# itself fills in — `day = 24`, `week = 7`, `dozen = 12` — and the brief says so:
# the environment is a Map, and who writes into it is the next module's question.
# The skeleton's "`let x = 4`" moved to module 13 for exactly that reason.
#
# MODULE 10 PAYS ITS FIRST DIVIDEND. Adding `IdentToken` and `Var` produces
# two `never` errors — one in `describe`, one in `evaluate` — and step 2 is built
# around reading that list. The compile-time fix there is deliberate.
#
# THE TRAP FROM MODULE 2, AGAIN: `LETTERS.indexOf("")` is 0, so `isLetter("")`
# is true. The identifier loop's `i < src.length` guard is what keeps it from
# spinning at the end of the input; module 3 taught the same hang for digits.
# Taught, not graded — a hang is a timeout, not an answer.
# ---------------------------------------------------------------------------

_C12_TOKENS = """type Op = "+" | "-" | "*" | "/";

type NumberToken = { kind: "number"; value: number };
type OpToken = { kind: "op"; op: Op };
type IdentToken = { kind: "ident"; name: string };
type LParenToken = { kind: "lparen" };
type RParenToken = { kind: "rparen" };
type EofToken = { kind: "eof" };

type Token = NumberToken | OpToken | IdentToken | LParenToken | RParenToken | EofToken;

function numberToken(value: number): NumberToken {
  return { kind: "number", value: value };
}

function opToken(op: Op): OpToken {
  return { kind: "op", op: op };
}

function identToken(name: string): IdentToken {
  return { kind: "ident", name: name };
}

function lparenToken(): LParenToken {
  return { kind: "lparen" };
}

function rparenToken(): RParenToken {
  return { kind: "rparen" };
}

function eofToken(): EofToken {
  return { kind: "eof" };
}
"""

_C12_LETTERS = """const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";

function isLetter(ch: string): boolean {
  return LETTERS.indexOf(ch) !== -1;
}
"""

_C12_IDENT_BRANCH = """    } else if (isLetter(ch)) {
      const start = i;
      while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) {
        i = i + 1;
      }
      tokens.push(identToken(src.slice(start, i)));
"""

_C12_SCAN = _C8_SCAN.replace("\nfunction scan(", "\n" + _C12_LETTERS + "\nfunction scan(", 1) \
    .replace("    } else {\n", _C12_IDENT_BRANCH + "    } else {\n", 1)

_C12_TREE = """type NumLit = { kind: "num"; value: number };
type Var = { kind: "var"; name: string };
type Neg = { kind: "neg"; operand: Expr };
type Binary = { kind: "binary"; op: Op; left: Expr; right: Expr };

type Expr = NumLit | Var | Neg | Binary;

function num(value: number): NumLit {
  return { kind: "num", value: value };
}

function variable(name: string): Var {
  return { kind: "var", name: name };
}

function neg(operand: Expr): Neg {
  return { kind: "neg", operand: operand };
}

function binary(op: Op, left: Expr, right: Expr): Binary {
  return { kind: "binary", op: op, left: left, right: right };
}
"""

_C12_DESCRIBE = _C10_DESCRIBE.replace(
    '    case "lparen":', '    case "ident":\n      return `\'${t.name}\'`;\n    case "lparen":', 1)

_C12_PRIMARY = _C8_PRIMARY.replace(
    '  if (t.kind === "lparen") {',
    '  if (t.kind === "ident") {\n    return { ok: true, expr: variable(t.name) };\n  }\n  if (t.kind === "lparen") {', 1)

_C12_ENV = "type Env = Map<string, number>;\n"

_C12_VAR_CASE = """    case "var": {
      const value = env.get(e.name);
      if (value === undefined) {
        return { ok: false, error: `error: undefined variable '${e.name}'` };
      }
      return { ok: true, value: value };
    }
"""

_C12_EVAL = _C11_EVAL.replace("function evaluate(e: Expr): EvalResult {",
                              "function evaluate(e: Expr, env: Env): EvalResult {") \
    .replace("evaluate(e.operand)", "evaluate(e.operand, env)") \
    .replace("evaluate(e.left)", "evaluate(e.left, env)") \
    .replace("evaluate(e.right)", "evaluate(e.right, env)") \
    .replace('    case "neg": {', _C12_VAR_CASE + '    case "neg": {', 1)

_C12_RUN_FN = _C11_RUN.split("\n\nconsole.log")[0] \
    .replace("function run(src: string): string {", "function run(src: string, env: Env): string {") \
    .replace("evaluate(parsed.expr)", "evaluate(parsed.expr, env)") + "\n"

_C12_MAIN = """const env: Env = new Map();
env.set("day", 24);
env.set("week", 7);
env.set("dozen", 12);

console.log(run(readFileSync(0, "utf8").trimEnd(), env));
"""


def _c12(tokens=_C12_TOKENS, scan=_C12_SCAN, describe=_C12_DESCRIBE, primary=_C12_PRIMARY,
         evaluate=_C12_EVAL, run=_C12_RUN_FN, main=_C12_MAIN):
    return _stdin(_cjoin(tokens, _C6_RESULTS, _C4_UNEXPECTED, scan, _C12_TREE, _C6_STATE,
                         describe, primary, _C8_UNARY, _C8_PRODUCT, _C7_SUM, _C8_PARSE,
                         _C11_RESULT, _C12_ENV, evaluate, _C11_ARITH, run, main))


_C12_FULL = _c12()

_C12_INPUTS = ["week * day", "dozen / 4", "day - dozen * 2", "-week",
               "(day + week) * 0 + dozen", "year + 1", "x1 + 1", "Day", "_",
               "2week", "week week", "1 / (week - 7)", "1 + 2 * 3", "day $", ""]
_C12_TESTS = _ctests(12, _C12_INPUTS)

# --- Step 3's plain program: a Map on its own -------------------------------
_C12_S3_MAIN = """const env: Env = new Map();
env.set("week", 7);
env.set("day", 24);

console.log(env.get("week"));
console.log(env.get("day"));
console.log(env.get("year"));

env.set("week", 5);
console.log(env.get("week"));
console.log(env.size);
"""
_C12_S3_OUT = "7\n24\nundefined\n5\n2"


def _c12_s3(main=_C12_S3_MAIN):
    return _plain(_cjoin(_C12_ENV, main))


_C12_WHY = (
    "A calculator forgets everything the moment it answers. A language remembers: "
    "you give a value a name, and use the name instead of the value. That needs "
    "three things this project does not have — a way to scan a name, a node that "
    "stands for one, and somewhere to look up what it means. The last one is the "
    "interesting one. It is a `Map` from names to values, and it hands back "
    "`undefined` for a name that was never given a value — which, in a language, "
    "is not a missing piece of data but a mistake in the program, with its own "
    "message."
)

_C12_BRIEF = """
### The whole module in one line

`week * day` evaluates to `168`, because `evaluate` carries a `Map` from names
to numbers down the tree — and `year + 1` says `error: undefined variable 'year'`.

### Three new pieces, one per stage

| Stage | New | Example |
|---|---|---|
| scanner | an `ident` token — a name | `week` → `{ kind: "ident", name: "week" }` |
| parser | a `var` node — a name in a tree | `variable("week")` |
| evaluator | an **environment**: `Map<string, number>` | `week` → 7 |

A name is a letter or `_`, followed by letters, digits and `_`s. `week`, `x1` and
`_tmp` are names; `2week` is the number 2 followed by the name `week`.

### The environment

An environment is what a name *means* at the moment it is evaluated. Here, it is
a `Map` — the built-in key-value store:

```ts
type Env = Map<string, number>;

const env: Env = new Map();
env.set("week", 7);
env.get("week");      // 7
env.get("year");      // undefined
```

`evaluate` gets the environment as a second argument and passes it to every
recursive call, so a name anywhere in the tree is looked up in the same place.

### `undefined` is the error

`env.get` returns `number | undefined`, and the compiler will not let you use it
as a number until you have said what `undefined` means. Here it means one thing
exactly:

```
$ echo 'year + 1' | node calc.ts
error: undefined variable 'year'
```

Treating it as zero would be module 10's `default: return 0` all over again — a
wrong answer that looks right.

### Where the names come from — for now

`let` needs statements, and statements are module 13. So this module's
`calc.ts` starts with three names already in its environment — `day`, `week`
and `dozen` — put there by the program itself. The environment is a Map; who
writes into it is the next module's question.

### Module 10 pays out

Add `IdentToken` to `Token` and `Var` to `Expr`, compile, and the compiler hands
you a list: `describe` has no case for identifiers, `evaluate` has none for
variables. That list is step 2.
"""

_C12_SYNTAX = [
    _syn(
        "type Env = Map<string, number>;",
        "A `Map` from names to numbers. The angle brackets say what the keys and "
        "values are.",
        "",
        "`Map<K, V>` is a *generic* type: `Map` on its own is not a complete type, "
        "and filling in `K` and `V` makes it one. The compiler then checks every "
        "`set` and `get` against them.",
    ),
    _syn(
        "const env: Env = new Map();",
        "Create an empty Map. The annotation tells `new Map()` what it is a map "
        "of.",
        "",
        "Without the annotation, `new Map()` is a `Map<any, any>`, and nothing you "
        "put in or take out would be checked.",
    ),
    _syn(
        "env.set(\"week\", 7);",
        "Store a value under a key, replacing any value already there.",
        """
env.set("week", 7);
env.set("week", 5);     // week is now 5
""",
        "",
    ),
    _syn(
        "const value = env.get(e.name);",
        "Look a key up. Returns the value, or `undefined` if the key was never "
        "set — so its type is `number | undefined`.",
        """
const value = env.get(e.name);
if (value === undefined) {
  return { ok: false, error: `error: undefined variable '${e.name}'` };
}
return { ok: true, value: value };      // value: number here
""",
        "The compiler will not let a `number | undefined` be used as a number. "
        "Deciding what `undefined` means is the point.",
    ),
    _syn(
        "function evaluate(e: Expr, env: Env): EvalResult { … }",
        "A recursive function with a second parameter that every call passes "
        "straight on — so the whole tree is evaluated against one environment.",
        "",
        "",
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — names in the source.
# ---------------------------------------------------------------------------

_C12_S1 = _pstep(
    "names", "Names in the source",
    "An `ident` token: a letter or `_`, then letters, digits and `_`s.",
    """
A name starts with a letter or an underscore, and carries on with letters, digits
and underscores. Two character classes, the second a superset of the first:

```ts
const LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";

function isLetter(ch: string): boolean {
  return LETTERS.indexOf(ch) !== -1;
}
```

`isDigit`'s trick from module 2, for letters. The scanner gets a branch with the
shape of module 3's number branch — start, advance while it matches, cut:

```ts
} else if (isLetter(ch)) {
  const start = i;
  while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) {
    i = i + 1;
  }
  tokens.push(identToken(src.slice(start, i)));
}
```

and the token carries the name it read:

```ts
type IdentToken = { kind: "ident"; name: string };
```

### Why a name cannot start with a digit

If it could, `2week` would be ambiguous: the name `2week`, or `2` then `week`?
Starting with a letter means a digit always begins a number, and a letter always
begins a name — the scanner can tell which from one character. `2week` is two
tokens, and the parser will say so.

### Module 2's trap, one more time

`LETTERS.indexOf("")` is `0` — the empty string is found at the start of every
string — so `isLetter("")` is **true**. Past the end of the source, `charAt`
returns `""`. The `i < src.length` guard, written *first*, is the only thing
stopping the loop from running forever on any input that ends in a name. Module
3 taught this hang for digits; it is the same hang.
""",
    """
```bash
$ echo 'week * day' | node calc.ts
168
$ echo 'x1 + 1' | node calc.ts
error: undefined variable 'x1'
$ echo '2week' | node calc.ts
error: unexpected 'week'
```

`x1` is one name — digits are allowed after the first character. `2week` is two
tokens.
""",
    pitfalls=[
        "Only letters in the loop: `x1` scans as `x` then `1`, and the parser reports `unexpected '1'`.",
        "Letters and digits in the FIRST-character test. `2week` becomes one name, and `2` on its own becomes a name too — the number branch never runs.",
        "The length guard second, or missing. `isLetter(\"\")` is true, so the loop never ends on an input ending in a name.",
        "Scanning names as lowercase. `Day` and `day` are different names in almost every language, this one included.",
    ],
    warmup=[
        _pq("How does `week2 * 2week` scan?",
            ["`week2`, `*`, `2`, `week` — a digit can continue a name but never start one",
             "`week`, `2`, `*`, `2week`",
             "`week2`, `*`, `2week`",
             "An error at the first `2`"],
            0,
            "One character decides: a letter starts a name, a digit starts a number."),
    ],
    exercises=[
        _pex("calc-m12-names-1", "Letters, then letters and digits",
             "Write the identifier loop's condition: keep going while there is a "
             "character left and it is a letter or a digit.",
             _C12_FULL,
             "      while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) {",
             _C12_TESTS,
             ["Module 3's number loop is the model — the length check first.",
              "After the first character, digits are allowed too.",
              "`while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) {`"]),
        _pfix("calc-m12-names-fix1", "`x1` is not a name",
              "`x1 + 1` says `error: unexpected '1'`. The name `x1` is being cut "
              "short after the `x`.",
              _c12(scan=_C12_SCAN.replace(
                  "(isLetter(src.charAt(i)) || isDigit(src.charAt(i)))", "isLetter(src.charAt(i))")),
              _C12_FULL,
              _C12_TESTS,
              ["Which characters can continue a name?",
               "The loop stops at the first digit.",
               "Letters OR digits after the first character."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why can't a name start with a digit?",
            ["So one character tells the scanner whether a number or a name is starting — `2week` is then unambiguous",
             "Because digits are not characters",
             "It is a TypeScript rule",
             "Because names are case-sensitive"],
            0,
            "A one-character decision keeps the scanner simple and its answers "
            "predictable."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — a variable is a node.
# ---------------------------------------------------------------------------

_C12_S2 = _pstep(
    "node", "A variable is a node",
    "The `var` node, a primary that is a name — and the list module 10's check hands you.",
    """
A name can go anywhere a number can: `week * day`, `-week`, `(week + 1)`. So it
is a **primary**, and it gets a node:

```ts
type Var = { kind: "var"; name: string };
type Expr = NumLit | Var | Neg | Binary;

function variable(name: string): Var {
  return { kind: "var", name: name };
}
```

(`variable`, not `var` — `var` is a reserved word in JavaScript.)

In `parsePrimary`, an `ident` token becomes a `var` node, the way a number token
became a number node in module 6:

```ts
if (t.kind === "ident") {
  return { ok: true, expr: variable(t.name) };
}
```

### Now compile

With `IdentToken` added to `Token` and `Var` added to `Expr`, before touching
anything else:

```
error TS2322: Type 'IdentToken' is not assignable to type 'never'.      (in describe)
error TS2322: Type 'Var' is not assignable to type 'never'.             (in evaluate)
```

That is module 10 paying out, exactly as promised. In module 8, the equivalent
change left `describe` quietly calling a bracket the end of the input. Here the
compiler lists every switch that needs a case — by name — before the program can
even run. `describe` gets:

```ts
case "ident":
  return `'${t.name}'`;
```

and `evaluate`'s case is the next two steps.
""",
    """
```bash
$ echo 'week week' | node calc.ts
error: unexpected 'week'
```

The second `week` is left over after a complete expression, and `describe` names
it — because the compiler made sure it could.
""",
    pitfalls=[
        "Calling the factory `var`. It is a reserved word; the file will not parse.",
        "Silencing the `never` errors with a `default` that returns something. They are a to-do list, not noise.",
        "Storing the whole token in the node: `{ kind: \"var\", token: t }`. The node needs the name, and nothing else about the token.",
    ],
    warmup=[
        _pq("After adding `Var` to `Expr` and nothing else, what does the compiler report?",
            ["`Type 'Var' is not assignable to type 'never'` in `evaluate`'s default",
             "Nothing",
             "`Function lacks ending return statement`",
             "An error in `parsePrimary`"],
            0,
            "Every switch over `Expr` without a `var` case — here, one."),
    ],
    exercises=[
        _pfix("calc-m12-node-fix1", "The list from the compiler",
              "This does not compile:\n\n"
              "    Type 'IdentToken' is not assignable to type 'never'.\n\n"
              "A token kind was added and one switch over tokens has not heard "
              "about it.",
              _c12(describe=_C10_DESCRIBE),
              _C12_FULL,
              _C12_TESTS,
              ["Which function switches over every kind of token?",
               "It needs a case for the new kind — a name, shown in quotes like every token the user typed.",
               "`case \"ident\": return `'${t.name}'`;`"],
              difficulty="Intro"),
        _pex("calc-m12-node-1", "A name is a primary",
             "In `parsePrimary`, turn an identifier token into a variable node.",
             _C12_FULL,
             '  if (t.kind === "ident") {\n    return { ok: true, expr: variable(t.name) };\n  }',
             _C12_TESTS,
             ["Same shape as the number case above it.",
              "The factory is `variable`, and the token carries `name`.",
              "`if (t.kind === \"ident\") { return { ok: true, expr: variable(t.name) }; }`"]),
    ],
    quiz=[
        _pq("Module 8 added brackets and `describe` broke silently. Why does adding `IdentToken` not break it silently?",
            ["Module 10's `never` check in `describe`'s default turns the missing case into a compile error",
             "Because identifiers are simpler than brackets",
             "Because `describe` is now an `if` chain",
             "It does break silently"],
            0,
            "The smoke alarm, going off exactly where it should."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — an environment is a Map.
# ---------------------------------------------------------------------------

_C12_S3 = _pstep(
    "map", "An environment is a Map",
    "`new Map`, `.set`, `.get`, and a lookup that can come back empty.",
    """
The environment is where a name's value lives. JavaScript has a built-in for
exactly this — a **`Map`**, from keys to values:

```ts
type Env = Map<string, number>;

const env: Env = new Map();
env.set("week", 7);
env.set("day", 24);

env.get("week");     // 7
env.get("year");     // undefined
```

`Map<string, number>` says what goes in: string keys, number values. The
compiler checks both — `env.set("week", "seven")` is refused.

### `set` replaces

```ts
env.set("week", 5);
env.get("week");     // 5
```

A key has one value. Setting it again replaces the old one; the Map does not
keep a history.

### `get` can miss

The type of `env.get("week")` is **`number | undefined`**. Not `number` —
because the key might never have been set, and the Map cannot know from the
types which keys you have set. This is the same honesty as `tokens[pos]` in
module 6: a lookup that can miss says so in its type, and the compiler makes you
decide what a miss means before you can use the result.

### Why not a plain object

`{ week: 7, day: 24 }` would work for these names. It stops working for a name
like `toString` or `constructor`, which every object already has — `obj["toString"]`
is a function, not `undefined`. A `Map` starts genuinely empty. For keys that
come from user input, which a program's variable names are, that matters.
""",
    """
```
7
24
undefined
5
2
```

`size` counts keys: `week` was set twice, but it is still one key.
""",
    pitfalls=[
        "`new Map()` with no type: it becomes `Map<any, any>`, and nothing put in or taken out is checked.",
        "`env[\"week\"]` — bracket access on a Map does not read its entries. It is `.get`.",
        "Expecting `set` to add a second entry for an existing key. A key has exactly one value.",
        "A plain object for the environment. A variable named `toString` then already has a value — a function.",
    ],
    warmup=[
        _pq("What is the type of `env.get(\"week\")` for `const env: Map<string, number>`?",
            ["`number | undefined` — the key may never have been set",
             "`number`",
             "`string`",
             "`any`"],
            0,
            "A lookup that can miss says so in its type."),
    ],
    exercises=[
        _pex("calc-m12-map-1", "An empty environment",
             "Create the environment: an empty Map of names to numbers.",
             _c12_s3(),
             "const env: Env = new Map();",
             [("", _C12_S3_OUT)],
             ["`new Map()` makes an empty one.",
              "Annotate it, so the compiler knows what it holds.",
              "`const env: Env = new Map();`"]),
        _pex("calc-m12-map-2", "Give a name a value",
             "Store `24` under the name `day`.",
             _c12_s3(),
             'env.set("day", 24);',
             [("", _C12_S3_OUT)],
             ["A Map method with a key and a value.",
              "`env.set(key, value);`",
              "`env.set(\"day\", 24);`"]),
    ],
    quiz=[
        _pq("Why is `Map` better than a plain object for variables?",
            ["A Map starts empty; an object already has keys like `toString`, so a variable of that name would seem defined",
             "Maps are faster for three keys",
             "Objects cannot hold numbers",
             "No difference"],
            0,
            "Keys that come from the user deserve a container with nothing in it "
            "already."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the name that is not there.
# ---------------------------------------------------------------------------

_C12_S4 = _pstep(
    "undefined", "The name that is not there",
    "Evaluating a `var`: look it up, and make `undefined` an error with a name in it.",
    """
`evaluate` gains a parameter — the environment — and passes it on at every
recursive call, so every name in the tree is looked up in the same place:

```ts
function evaluate(e: Expr, env: Env): EvalResult {
  switch (e.kind) {
    …
    case "var": {
      const value = env.get(e.name);
      if (value === undefined) {
        return { ok: false, error: `error: undefined variable '${e.name}'` };
      }
      return { ok: true, value: value };
    }
    …
    case "binary": {
      const left = evaluate(e.left, env);
      …
```

After the `if`, `value` has been narrowed from `number | undefined` to `number`,
and the success member accepts it.

### `undefined` is the error

This is the first error in the project that is not about syntax or arithmetic —
it is about *meaning*. `year + 1` scans and parses perfectly; it is a sum of a
name and a number. It just refers to something that does not exist. The
evaluator is the first stage that can know that, so it is the stage that says
it.

The tempting alternative is to treat a missing name as zero. `year + 1` would
print `1`. It is module 10's `default: return 0;` in a new costume — an answer to
a question nobody asked — and a typo in a variable name would become a wrong
number instead of a message.

### The environment is passed, not global

`env` is a parameter, not a module-level `const` that `evaluate` reads. Module
13 creates a fresh environment per program; module 18's REPL keeps one alive
across many. A function that takes its environment as an argument works for both
without changing.

### `run` passes it in

```ts
function run(src: string, env: Env): string {
  …
  const result = evaluate(parsed.expr, env);
```

and the program sets up `day`, `week` and `dozen` before calling it.
""",
    """
```bash
$ echo 'week * day' | node calc.ts
168
$ echo '(day + week) * 0 + dozen' | node calc.ts
12
$ echo 'year + 1' | node calc.ts
error: undefined variable 'year'
$ echo 'Day' | node calc.ts
error: undefined variable 'Day'
```

Names are case-sensitive: `Day` is not `day`.
""",
    pitfalls=[
        "Treating `undefined` as zero. `year + 1` prints `1`, and a typo becomes a wrong answer.",
        "Forgetting to pass `env` in one recursive call. It does not compile — `evaluate` needs two arguments — which is the reason it is a parameter.",
        "A global environment `evaluate` reads directly. Works today; module 18 needs one environment that outlives many `run`s, and tests want a fresh one each time.",
        "`env.get(e.name) as number`. A cast is a promise with nothing behind it; the `if` is the promise kept.",
    ],
    warmup=[
        _pq("`year + 1` — which stage reports the error, and why that one?",
            ["The evaluator — the source scans and parses fine; only evaluation can discover `year` has no value",
             "The scanner",
             "The parser",
             "`run`"],
            0,
            "Each stage reports what only it can know."),
    ],
    exercises=[
        _pex("calc-m12-undefined-1", "Look it up",
             "Write the `var` case of `evaluate`: look the name up; if it is not "
             "there, fail with `error: undefined variable '<name>'`.",
             _C12_FULL,
             _C12_VAR_CASE.rstrip("\n"),
             _C12_TESTS,
             ["A case with braces, since it declares a `const`.",
              "`env.get(e.name)` is `number | undefined`.",
              "`undefined` → a failure naming the variable in quotes.",
              "Otherwise `{ ok: true, value: value }`."]),
        _pfix("calc-m12-undefined-fix1", "A typo that equals one",
              "`year + 1` prints `1`. `x1 + 1` prints `1`. Every name nobody "
              "defined is quietly worth zero.",
              _c12(evaluate=_C12_EVAL.replace(
                  "        return { ok: false, error: `error: undefined variable '${e.name}'` };",
                  "        return { ok: true, value: 0 };")),
              _C12_FULL,
              _C12_TESTS,
              ["What happens when `env.get` finds nothing?",
               "A missing name is not zero; it is a mistake in the program.",
               "`return { ok: false, error: `error: undefined variable '${e.name}'` };`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why is `env` a parameter of `evaluate` rather than a global it reads?",
            ["So the same function works with a fresh environment per program and one long-lived environment in a REPL",
             "Globals are not allowed in TypeScript",
             "For speed",
             "No reason"],
            0,
            "Modules 13 and 18 each need a different lifetime for it."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_C12_FINAL = _pch(
    "calc-m12-build", "Module 12 build — a language with memory", "Hard",
    "Write the evaluator and the program around it, from `Env` to the end:\n\n"
    "* `Env` — a Map from names to numbers\n"
    "* `evaluate` — module 11's, plus a `var` case, with the environment passed "
    "to every recursive call\n"
    "* `arithmetic` — unchanged from module 11\n"
    "* `run` — scan, parse, evaluate against the environment\n"
    "* the main program — an environment with `day` = 24, `week` = 7 and "
    "`dozen` = 12, then `run`\n\n"
    "The scanner, the names and the parser are given.",
    _C12_FULL,
    _cjoin(_C12_ENV, _C12_EVAL, _C11_ARITH, _C12_RUN_FN, _C12_MAIN).rstrip("\n"),
    _C12_TESTS,
    ["`type Env = Map<string, number>;`",
     "Every `evaluate(…)` call inside `evaluate` passes `env` along.",
     "The `var` case: `env.get`, then `undefined` → `error: undefined variable '<name>'`.",
     "Main: `new Map()`, three `set`s, then `console.log(run(…, env))`."],
)


_CALC_MODULES.append(_pmod(
    key="calc-vars", number=12, phase="lang",
    title="Variables and an environment",
    what="a Map from names to values, and the name that is not in it",
    goal="Read a name's value from an environment — and say so when it has none.",
    why=_C12_WHY,
    est_minutes=45,
    builds_on=["calc-parens", "calc-never", "calc-arithmetic"],
    concepts=["identifiers", "environment", "Map", "generic types",
              "undefined as an error", "threading state through recursion",
              "exhaustiveness paying off"],
    deliverable="`echo 'week * day' | node calc.ts` prints `168`, and "
                "`echo 'year + 1'` prints `error: undefined variable 'year'` "
                "rather than quietly treating it as zero.",
    objectives=[
        "Scan a name, and say why a name cannot start with a digit",
        "Add a token kind and a node kind, and read the list of switches the compiler produces",
        "Create a typed `Map`, set and get values, and say why `get` returns `V | undefined`",
        "Thread an environment through a recursive evaluator",
        "Turn a failed lookup into an error with the name in it, and say why zero is the wrong answer",
    ],
    brief=_C12_BRIEF,
    syntax=_C12_SYNTAX,
    steps=[_C12_S1, _C12_S2, _C12_S3, _C12_S4],
    final_build=_C12_FINAL,
    acceptance=[
        "`echo 'week * day' | node calc.ts` prints `168`.",
        "`echo 'year + 1' | node calc.ts` prints `error: undefined variable 'year'`.",
        "`echo 'x1 + 1' | node calc.ts` reports `x1` — a single name.",
        "`echo '2week' | node calc.ts` prints `error: unexpected 'week'`.",
        "Names are case-sensitive: `Day` is undefined.",
        "Every earlier input still gives the same output.",
    ],
    manual_test="""
```bash
echo 'week * day'             | node calc.ts     # 168
echo 'dozen / 4'              | node calc.ts     # 3
echo '-week'                  | node calc.ts     # -7
echo 'year + 1'               | node calc.ts     # error: undefined variable 'year'
echo 'x1 + 1'                 | node calc.ts     # error: undefined variable 'x1'
echo '2week'                  | node calc.ts     # error: unexpected 'week'
echo '1 / (week - 7)'         | node calc.ts     # error: division by zero
```

Now the experiment worth doing. Before writing any of this module, add only the
two new types — `IdentToken` to `Token` and `Var` to `Expr` — and compile. Read
the list. Then try the same thing on a copy of your module 9 file, from before
the `never` checks: `Var` gives one vague error and `IdentToken` gives none.
""",
    reference="""// calc.ts — module 12
//
// Names. The scanner reads identifiers, the parser makes `var` nodes, and
// evaluate() carries an environment — a Map from names to numbers — down the
// tree. Map.get returns `number | undefined`, and that undefined is the
// undefined-variable error: never a quiet zero.
//
// The environment is filled in by the program for now; `let` is module 13's.
""" + _C12_FULL,
    stretch=[
        "Add built-in constants: start every environment with `pi`. Then decide what `let pi = 3` should do in module 13 — overwrite it, refuse, or shadow it?",
        "Suggest a fix in the error: when `yaer` is undefined and `year` is not, say `did you mean 'year'?`. You will need to compare the name against every key in the Map — look up `for (const key of env.keys())`.",
        "Make names case-insensitive, and find everything that has to change. Then argue for why almost no language does it.",
        "Replace the Map with a plain object and write a program that breaks because of it — a variable called `constructor` is a good place to start.",
    ],
    glossary=[
        _pgloss("identifier", "A name in the source: a letter or `_`, then letters, digits and `_`s."),
        _pgloss("environment", "The mapping from names to values in force when an expression is evaluated."),
        _pgloss("Map", "JavaScript's built-in key-value store. `new Map()`, `.set(k, v)`, `.get(k)`."),
        _pgloss("generic type", "A type with parameters, like `Map<K, V>`, that is completed by filling them in."),
        _pgloss("undefined variable", "A name used without a value. An error of meaning, reported by the evaluator."),
    ],
    cheatsheet="""
```ts
type IdentToken = { kind: "ident"; name: string };     // scanner
type Var = { kind: "var"; name: string };              // tree
type Env = Map<string, number>;                        // evaluator

// scan: a letter or _, then letters/digits/_ — length check FIRST
while (i < src.length && (isLetter(src.charAt(i)) || isDigit(src.charAt(i)))) { i = i + 1; }

case "var": {
  const value = env.get(e.name);                       // number | undefined
  if (value === undefined) {
    return { ok: false, error: `error: undefined variable '${e.name}'` };
  }
  return { ok: true, value: value };
}

const env: Env = new Map();
env.set("week", 7);
```

| Input | Output |
|---|---|
| `week * day` | `168` |
| `year + 1` | `error: undefined variable 'year'` |
| `x1 + 1` | `error: undefined variable 'x1'` |
| `2week` | `error: unexpected 'week'` |

| Symptom | Cause |
|---|---|
| `x1` → `unexpected '1'` | identifier loop accepts letters only |
| `year + 1` prints `1` | `undefined` treated as zero |
| `Type 'IdentToken' is not assignable to type 'never'` | `describe` has no `ident` case |
""",
    self_check=[
        "Can you write the identifier branch of the scanner, with the guard in the right place?",
        "Can you say which switches the compiler lists after adding `IdentToken` and `Var`?",
        "Can you explain why `Map.get` returns `number | undefined`?",
        "Can you write the `var` case of `evaluate` from memory?",
        "Can you say why a missing name is an error rather than zero?",
    ],
    review=[
        _pq("What does `2week` scan to?",
            ["The number 2, then the name `week` — a digit always starts a number",
             "One name, `2week`",
             "An error",
             "The number 2 only"],
            0,
            "The parser then reports `unexpected 'week'`."),
        _pq("Why does `evaluate` take `env` as a parameter?",
            ["So every recursive call looks names up in the same environment, and callers choose which environment that is",
             "Because Maps cannot be global",
             "To make the function longer",
             "It does not"],
            0,
            "Module 13 makes one per program; module 18 keeps one for a whole session."),
        _pq("`env.get(\"year\")` for a name never set returns…",
            ["`undefined`",
             "`0`",
             "`null`",
             "It throws"],
            0,
            "And the type says so: `number | undefined`."),
        _pq("Why is `year + 1` → `1` a bad design?",
            ["A typo in a name silently becomes a wrong number instead of a message",
             "Because `1` is not a valid answer",
             "Because `+` needs two variables",
             "It is a good design"],
            0,
            "The module 10 lesson, in a new place."),
        _pq("What did module 10's `never` check do for this module?",
            ["Listed, as compile errors, every switch that needed a case for `IdentToken` or `Var`",
             "Nothing",
             "Added the cases automatically",
             "Made the program faster"],
            0,
            "The first time the smoke alarm went off for real."),
    ],
    milestone="The language has memory. Names scan, parse and evaluate against an "
              "environment, and a name with no value is an error that names it. "
              "Module 13 lets a program write into the environment itself.",
))
