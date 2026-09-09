# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Week 5 — functions.
#
# exec()'d by tools/typescript_course.py INTO ITS NAMESPACE, so every helper
# (_week, _lesson, _ex, _fix, _ch, _fn, _types, _predict, _diagnose, _retype,
# _design, _q, _gloss, _cap_auto, _cap_brief) and every shared program prefix
# (_FS, _NUMS, _WORDS, _LINE) is already defined. This file only appends its
# week to `_WEEKS`; it is not importable on its own.
# ---------------------------------------------------------------------------

# --- Week 5 ---------------------------------------------------------------
_WEEKS.append(_week(
    5, 2, _M2,
    "Functions",
    "Package logic into named, reusable functions with parameters, return values, guards, defaults and predictable behaviour.",
    """
Everything you've written so far has been one long script. This week you learn
to **name a piece of logic** so you can use it again, test it on its own, and
read it without re-deriving it.

A **function** takes inputs (**parameters**), does something, and hands back a
**return value**. That's it. But the consequences are large:

- You write the tricky bit **once** and fix bugs in one place.
- The name becomes documentation: `withTax(amount)` explains itself.
- Each piece can be reasoned about alone, which is the only way anything big
  stays understandable.

You'll also meet **annotations on the boundary** — `(x: number): number` — which
is where TypeScript really starts to earn its name. The compiler checks every
call site against that signature, so a wrong argument is caught while you type
rather than at 3am.

⏱️ Budget about **nine hours**, spread over several sittings.
""",
    objectives=[
        "Declare a function with parameters, a return type, and a return value",
        "Call a function and use what it hands back",
        "Write compact functions as arrow functions",
        "Return early with guard clauses instead of deep nesting",
        "Give parameters defaults and mark them optional",
        "Explain scope, shadowing, and why a pure function is easier to trust",
        "Pass a function to another function as a value",
        "Return a function from a function, and explain what a closure captures",
        "Write a function's contract — name, inputs, output, preconditions — before its body",
        "Trace a nested call by substituting each return value, and extract a helper on the third repetition",
    ],
    why="Functions are how you stop a program growing into an unreadable sheet of statements. Every abstraction you will ever build — modules, classes, components, APIs — is this idea repeated at a larger scale.",
    est_minutes=540,
    glossary=[
        _gloss("function", "Named, reusable logic that takes inputs and returns a value."),
        _gloss("parameter", "A named input, written in the declaration."),
        _gloss("argument", "The actual value you pass at the call site."),
        _gloss("signature", "The parameter types and return type together: (x: number) => number."),
        _gloss("return", "Hands a value back to the caller AND ends the function immediately."),
        _gloss("call site", "The place where a function is invoked."),
        _gloss("arrow function", "A compact form: const f = (x: number): number => x * 2."),
        _gloss("guard clause", "An early return that rejects a case up front, keeping the body flat."),
        _gloss("default parameter", "A value used when the argument is omitted: (rate = 0.08)."),
        _gloss("optional parameter", "A parameter marked with ? that may be undefined."),
        _gloss("void", "The return type of a function that returns nothing useful."),
        _gloss("scope", "The region where a name is visible."),
        _gloss("shadowing", "An inner name hiding an outer one of the same name."),
        _gloss("pure function", "Same inputs, same output, no side effects."),
        _gloss("side effect", "Anything a function does beyond returning — printing, changing an outer variable."),
        _gloss("composition", "Feeding one function's result into another: whole(withTax(x))."),
        _gloss("higher-order function", "A function that takes or returns another function."),
        _gloss("hoisting", "Function declarations are usable before the line that defines them; const arrow functions are not."),
        _gloss("closure", "A function together with the variables it captured from the scope around it."),
        _gloss("factory", "A function whose job is to build and return another function."),
        _gloss("contract", "The name, inputs, output and preconditions a function promises to honour."),
        _gloss("stub", "A function body that returns a placeholder so the rest of the program can already call it."),
        _gloss("tracing", "Working out a result by hand: replace each call with the value it returned."),
        _gloss("extraction", "Turning a repeated line into a function whose parameter is the part that varied."),
    ],
    cheatsheet="""
```ts
// ---- declaration -----------------------------------------------------
function square(x: number): number {
  return x * x;
}
console.log(square(5));            // 25

// ---- several parameters ----------------------------------------------
function lineTotal(price: number, qty: number): number {
  return price * qty;
}
lineTotal(3.25, 4)                 // 13   — order matters

// ---- arrow function ---------------------------------------------------
const cube = (x: number): number => x * x * x;       // auto-returns
const cube2 = (x: number): number => { return x * x * x; };   // needs return

// ---- guard clause ------------------------------------------------------
function describe(n: number): string {
  if (Number.isNaN(n)) return "not a number";        // reject early
  if (n < 0) return "negative";
  return "ok";                                        // the happy path, flat
}

// ---- defaults & optionals ----------------------------------------------
function withTax(amount: number, rate: number = 0.08): number {
  return amount * (1 + rate);
}
withTax(100)         // 108   — rate defaulted
withTax(100, 0.2)    // 120

function greet(name: string, title?: string): string {
  return title === undefined ? `Hi ${name}` : `Hi ${title} ${name}`;
}

// ---- returns nothing ---------------------------------------------------
function banner(text: string): void {
  console.log("-".repeat(text.length));
}

// ---- a function as a value ---------------------------------------------
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}
applyTwice(cube, 2)   // 512
```
""",
    self_check=[
        "Can you write a function that takes two numbers and returns a result?",
        "Can you explain the difference between console.log and return?",
        "Can you rewrite a two-line function as an arrow function?",
        "Can you replace a nested if/else with guard clauses?",
        "Can you give a parameter a default and say when the default is used?",
        "Can you say why a pure function is easier to test than one that prints?",
        "Can you pass one function into another as an argument?",
        "Can you write a function that returns a configured function, and say what it remembers?",
        "Can you state a function's contract before writing a line of its body?",
        "Can you trace inc(twice(5)) on paper, and say which guard order a grade() needs?",
    ],
    review=[
        _q("What does `return` do?",
           ["Prints a value", "Hands a value back to the caller and ends the function",
            "Declares a variable", "Starts a loop"], 1,
           "It produces the function's result and stops it there and then."),
        _q("In `function f(x: number)`, `x` is a…",
           ["return value", "parameter", "global", "argument"], 1,
           "A parameter. The value you pass at the call site is the argument."),
        _q("`const d = (x: number): number => x * 2; d(4)` is…",
           ["4", "8", "24", "an error"], 1, "It doubles: 8."),
        _q("A function with no `return` statement returns…",
           ["0", "null", "undefined", "an error"], 2,
           "undefined — which is why a forgotten return prints as `undefined`."),
        _q("`const f = (x: number): number => { x * 2; };` returns…",
           ["2x", "undefined", "an error", "x"], 1,
           "With braces you must write return yourself."),
        _q("A guard clause is…",
           ["a try/catch", "an early return that handles a case and leaves",
            "a loop condition", "a type annotation"], 1,
           "It keeps the main path flat and unindented."),
        _q("`function f(a: number, b: number = 2)` — what is `f(5)`'s b?",
           ["undefined", "0", "2", "an error"], 2,
           "The default fills in for the omitted argument."),
        _q("A pure function…",
           ["prints its result", "returns the same output for the same input and changes nothing else",
            "has no parameters", "is always short"], 1,
           "Which is exactly what makes it trivially testable."),
        _q("Which can you call on the line ABOVE where it is written?",
           ["const f = () => ...", "function f() { ... }", "both", "neither"], 1,
           "Function declarations are hoisted; const arrow functions are not."),
        _q("`applyTwice(cube, 2)` passes `cube`…",
           ["as a string", "as a value — the function itself, not its result",
            "by calling it first", "as a number"], 1,
           "Note there are no parentheses after cube — that is the whole point."),
        _q("What is a function's contract?",
           ["its length", "its name, inputs, output and preconditions", "its call sites", "its return statement"], 1,
           "Decide it first and the body usually writes itself."),
        _q("Tracing `inc(twice(5))`, you first replace…",
           ["inc with its body", "twice(5) with 10", "5 with 10", "nothing"], 1,
           "Innermost call first — substitute the value it returned."),
        _q("Copying a line and changing one number in it is a sign that…",
           ["the code is fine", "that number wants to be a parameter",
            "you need a loop", "the function is pure"], 1,
           "The part that varies between copies is exactly the input."),
    ],
    milestone="Budget Buddy is now built from named helpers instead of one long script — the first version you could hand to somebody else and have them understand.",
    lessons=[
        # ---- Lesson 1 --------------------------------------------------
        _lesson(
            "w5-declare", "Declaring a function",
            "function name(params): type { return ... }",
            """
```ts
function square(x: number): number {
  return x * x;
}

console.log(square(5));    // 25
console.log(square(3));    // 9
```

Every part earns its place:

| piece | name | meaning |
|---|---|---|
| `function` | keyword | "here comes a named piece of logic" |
| `square` | name | how you'll call it |
| `(x: number)` | parameter list | one input, annotated as a number |
| `: number` | return type | what it hands back |
| `{ ... }` | body | what it does |
| `return x * x` | return statement | the result |

**`return` is not `console.log`.** This is the single most common confusion at
this stage:

- `console.log(v)` **shows** `v` on screen. The value is gone afterwards.
- `return v` **hands `v` back** to whoever called the function, so they can use
  it, store it, or combine it.

```ts
function bad(x: number): void { console.log(x * 2); }   // shows it
function good(x: number): number { return x * 2; }      // gives it back

const t = good(5) + good(5);   // 20   — you can do this
```

You can't add up things that were only printed.

**`return` ends the function immediately.** Anything after it never runs:

```ts
function f(): number {
  return 1;
  console.log("never");   // unreachable
}
```

**A function with no return** hands back `undefined`. That's the cause of the
classic "why does it print undefined?" — a body that computes the answer and
then forgets to give it back.

**Hoisting.** A `function` declaration can be called from a line above where
it's written. That's why helper functions are often placed at the bottom of a
file, with the main flow readable at the top.

> ⚠️ **Common mistakes:** forgetting `return`; printing instead of returning;
> and putting statements after `return` and wondering why they never run.
""",
            warmup=[
                _q("`function f(x){ return x + 1; } console.log(f(4));` prints…",
                   ["4", "5", "x + 1", "undefined"], 1, "f(4) returns 5."),
                _q("`function f(x){ x + 1; } console.log(f(4));` prints…",
                   ["4", "5", "undefined", "an error"], 2,
                   "It computes and discards; with no return the result is undefined."),
                _q("`function f(){ return 1; console.log(2); } f();` prints…",
                   ["1", "2", "nothing", "1 then 2"], 2,
                   "return ends the function, so the log is unreachable."),
            ],
            exercises=[
                _ex("tscourse-w5-dec-1", "Square", "Return x multiplied by itself.",
                    'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                    'return x * x;', [("", "25")],
                    hints=["Hand the result back rather than printing it.",
                           "Write return x * x;"]),
                _ex("tscourse-w5-dec-2", "Greet", "Return a greeting string for the given name.",
                    'function greet(name: string): string {\n  return `Hello, ${name}!`;\n}\nconsole.log(greet("Ada"));\n',
                    '`Hello, ${name}!`', [("", "Hello, Ada!")],
                    hints=["Return a template literal that uses the parameter."]),
                _ex("tscourse-w5-dec-3", "Name the return type",
                    "Fill in the return type annotation. This function hands back text.",
                    'function describe(n: number): string {\n  return `n is ${n}`;\n}\nconsole.log(describe(7));\n',
                    'string', [("", "n is 7")],
                    hints=["The return type goes after the parameter list, before the body.",
                           "It hands back text, so the annotation is string."]),
                _ex("tscourse-w5-dec-4", "Use the result twice",
                    "Print double(5) added to double(10) — the function must return, not print.",
                    'function double(x: number): number {\n  return x * 2;\n}\nconsole.log(double(5) + double(10));\n',
                    'double(5) + double(10)', [("", "30")],
                    hints=["Because it returns, you can combine the two calls in one expression.",
                           "Write double(5) + double(10)."]),
                _ex("tscourse-w5-dec-5", "Call it on input",
                    "Read a number and print its square, using the function.",
                    _FS + 'function square(x: number): number {\n  return x * x;\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(square(n));\n',
                    'square(n)', [("5", "25"), ("9", "81")],
                    hints=["Pass the input as the argument.", "Write square(n)."]),
                _fix("tscourse-w5-dec-fix1", "Fix the missing return",
                     "This should print 25 but prints undefined. Fix it.",
                     'function square(x: number): number {\n  x * x;\n}\nconsole.log(square(5));\n',
                     'function square(x: number): number {\n  return x * x;\n}\nconsole.log(square(5));\n',
                     [("", "25")],
                     hints=["The function computes x*x but never hands it back.",
                            "Add return before x * x."]),
                _fix("tscourse-w5-dec-fix2", "Fix print-versus-return",
                     "This prints 10 then `undefined` — the function logs instead of returning. Make it print just 10.",
                     'function double(x: number) {\n  console.log(x * 2);\n}\nconsole.log(double(5));\n',
                     'function double(x: number): number {\n  return x * 2;\n}\nconsole.log(double(5));\n',
                     [("", "10")],
                     hints=["The inner log shows the value; the outer log then shows what was returned — nothing.",
                            "Return the value instead of logging it inside."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What is the difference between return and console.log?",
                   ["None", "return hands the value back to the caller; console.log only displays it",
                    "console.log is faster", "return prints too"], 1,
                   "Only a returned value can be used in further computation."),
                _q("A function whose body never reaches a return gives back…",
                   ["0", "undefined", '""', "an error"], 1,
                   "undefined — the source of countless 'why undefined?' moments."),
            ],
        ),
        # ---- Lesson 2 --------------------------------------------------
        _lesson(
            "w5-params", "Parameters & arguments",
            "Several inputs, in a fixed order.",
            """
Functions can take any number of inputs, separated by commas:

```ts
function lineTotal(price: number, qty: number): number {
  return price * qty;
}
console.log(lineTotal(3.25, 4));   // 13
```

**Parameter vs argument** — worth keeping straight:

- **Parameter**: the name in the declaration (`price`, `qty`).
- **Argument**: the value at the call site (`3.25`, `4`).

**Order is everything.** Arguments are matched by position, not by name:

```ts
function divide(a: number, b: number): number { return a / b; }
divide(10, 2)   // 5
divide(2, 10)   // 0.2   — no error, just wrong
```

TypeScript catches a wrong *type* here but cannot catch a wrong *order* when
both are numbers. Two defences: name parameters so the call reads sensibly, and
keep the count small. More than three or four arguments is a signal that the
inputs want grouping into an object (week 7).

**Composition.** Because a function returns a value, one call can be the
argument to another:

```ts
function withTax(amount: number): number { return amount * 1.08; }
function whole(amount: number): number { return Math.floor(amount); }

console.log(whole(withTax(50)));   // 54
```

Read those inside-out: `withTax(50)` produces 54, which `whole` then floors.
Chaining small, well-named functions like this is most of what "good structure"
means in practice.

**Parameters are local copies.** Reassigning one inside the function has no
effect on the caller's variable:

```ts
function f(x: number): number { x = 99; return x; }
const a = 1;
f(a);            // 99
console.log(a);  // still 1
```

> ⚠️ **Common mistakes:** swapping arguments; forgetting to *call* the function
> (writing `double` instead of `double(21)`); and passing the wrong count —
> TypeScript will tell you, so read the error.
""",
            warmup=[
                _q("`function add(a, b){ return a - b; } add(5, 3)` returns…",
                   ["8", "2", "15", "an error"], 1, "This (deliberately misnamed) function subtracts."),
                _q("`function sub(a, b){ return a - b; } sub(3, 5)` returns…",
                   ["2", "-2", "8", "an error"], 1, "Order matters: 3 - 5."),
                _q("In `greet(\"Ada\")`, `\"Ada\"` is the…",
                   ["parameter", "argument", "return value", "signature"], 1,
                   "The value at the call site is the argument."),
                _q("`whole(withTax(50))` evaluates which first?",
                   ["whole", "withTax", "neither", "both at once"], 1,
                   "Inner calls are evaluated before the outer one can use their result."),
            ],
            exercises=[
                _ex("tscourse-w5-par-1", "Two parameters",
                    "Return the line total for a price and a quantity.",
                    'function lineTotal(price: number, qty: number): number {\n  return price * qty;\n}\n'
                    'console.log(lineTotal(3.25, 4));\n',
                    'price * qty', [("", "13")],
                    hints=["Multiply the two parameters.", "Write price * qty."]),
                _ex("tscourse-w5-par-2", "Double the input",
                    "Return x doubled; the program prints double(n) for the input n.",
                    _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                    'x * 2', [("21", "42"), ("0", "0")],
                    hints=["Multiply the parameter by 2."]),
                _ex("tscourse-w5-par-3", "Three inputs",
                    "Return the total for a price, a quantity and a flat delivery fee.",
                    'function orderTotal(price: number, qty: number, delivery: number): number {\n'
                    '  return price * qty + delivery;\n}\n'
                    'console.log(orderTotal(3, 4, 5));\n',
                    'price * qty + delivery', [("", "17")],
                    hints=["Multiply, then add the fee.",
                           "Write price * qty + delivery."]),
                _ex("tscourse-w5-par-4", "Compose two functions",
                    "Print the taxed amount floored to a whole number, by calling one function inside the other.",
                    'function withTax(amount: number): number {\n  return amount * 1.08;\n}\n'
                    'function whole(amount: number): number {\n  return Math.floor(amount);\n}\n'
                    'console.log(whole(withTax(50)));\n',
                    'whole(withTax(50))', [("", "54")],
                    hints=["The inner call runs first and its result becomes the outer argument.",
                           "Write whole(withTax(50))."],
                    difficulty="Medium"),
                _ex("tscourse-w5-par-5", "Percentage of",
                    "Return what percent `part` is of `total`, to one decimal place, as a string like `25.0`.",
                    _FS + 'function percentOf(part: number, total: number): string {\n'
                    '  return ((part / total) * 100).toFixed(1);\n}\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(percentOf(n, 200));\n',
                    '((part / total) * 100).toFixed(1)',
                    [("50", "25.0"), ("200", "100.0"), ("0", "0.0")],
                    hints=["Divide, scale by 100, then fix the decimals.",
                           "Write ((part / total) * 100).toFixed(1)."],
                    difficulty="Medium"),
                _fix("tscourse-w5-par-fix1", "Fix the missing call",
                     "This should print 42 but prints the function itself. Fix the call.",
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                     'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double);\n',
                     _FS + 'function double(x: number): number {\n  return x * 2;\n}\n'
                     'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(double(n));\n',
                     [("21", "42")],
                     hints=["`double` names the function; it does not run it.",
                            "Add the parentheses and the argument: double(n)."]),
                _fix("tscourse-w5-par-fix2", "Fix the argument order",
                     "This should print 5 for `divide(10, 2)` but prints 0.2. Fix it.",
                     'function divide(a: number, b: number): number {\n  return b / a;\n}\n'
                     'console.log(divide(10, 2));\n',
                     'function divide(a: number, b: number): number {\n  return a / b;\n}\n'
                     'console.log(divide(10, 2));\n',
                     [("", "5")],
                     hints=["The body divides the second parameter by the first.",
                            "Swap them: return a / b;"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Arguments are matched to parameters by…",
                   ["name", "position", "type", "alphabetical order"], 1,
                   "Which is why swapping two same-typed arguments is invisible to the compiler."),
                _q("Reassigning a parameter inside a function…",
                   ["changes the caller's variable", "affects only the local copy",
                    "is an error", "returns it"], 1,
                   "For numbers and strings the caller is untouched."),
            ],
        ),
        # ---- Lesson 3 --------------------------------------------------
        _lesson(
            "w5-arrow", "Arrow functions",
            "A compact form for small functions.",
            """
For short functions there's a lighter syntax:

```ts
const cube = (x: number): number => x * x * x;
console.log(cube(3));    // 27
```

Compare the two forms side by side:

```ts
function cube(x: number): number {
  return x * x * x;
}

const cube = (x: number): number => x * x * x;
```

**The implicit return.** When the body is a single expression with no braces,
its value is returned automatically — no `return` keyword. Add braces and you're
back to writing it yourself:

```ts
const a = (x: number): number => x * 2;              // returns 2x
const b = (x: number): number => { return x * 2; };  // returns 2x
const c = (x: number): number => { x * 2; };         // ⚠️ returns undefined
```

That third one is the classic arrow mistake. Braces mean "here is a block of
statements", and a block returns nothing unless told to.

**Several parameters** need the parentheses; a body over one expression needs
the braces:

```ts
const add = (a: number, b: number): number => a + b;
```

**Declaration vs arrow — which to use?**

| | `function` | arrow |
|---|---|---|
| hoisted (callable above) | yes | no |
| best for | named, standalone logic | short helpers, and functions passed as values |

They behave differently in one deeper way too (around a keyword called `this`),
which you'll meet with objects. For everything this week, pick whichever reads
better — and reach for arrows when the function is small or is being handed to
another function (lesson 7).

> ⚠️ **Common mistakes:** braces without `return`; calling a `const` arrow above
> the line that defines it (it isn't hoisted); and forgetting that
> `const f = ...` is a variable declaration, so it ends with a semicolon.
""",
            warmup=[
                _q("`const f = (x: number) => x + 10; f(5)` is…",
                   ["5", "10", "15", "an error"], 2, "5 + 10."),
                _q("`const f = (x: number) => { x + 10; }; f(5)` is…",
                   ["15", "undefined", "5", "an error"], 1,
                   "With braces you must write return."),
                _q("Which can be called on the line above its definition?",
                   ["const f = () => 1;", "function f() { return 1; }", "both", "neither"], 1,
                   "Only function declarations are hoisted."),
            ],
            exercises=[
                _ex("tscourse-w5-arr-1", "Cube (arrow)", "Return x cubed, using the implicit return.",
                    'const cube = (x: number): number => x * x * x;\nconsole.log(cube(3));\n',
                    'x * x * x', [("", "27")],
                    hints=["No braces, no return — just the expression.",
                           "Write x * x * x."]),
                _ex("tscourse-w5-arr-2", "Triple (arrow)",
                    "Return x * 3; the program prints triple(n) for the input.",
                    _FS + 'const triple = (x: number): number => x * 3;\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'x * 3', [("5", "15"), ("10", "30")],
                    hints=["Multiply x by 3."]),
                _ex("tscourse-w5-arr-3", "Two parameters, arrow style",
                    "Write the arrow that adds its two parameters.",
                    'const add = (a: number, b: number): number => a + b;\nconsole.log(add(2, 40));\n',
                    'a + b', [("", "42")],
                    hints=["The body is a single expression.", "Write a + b."]),
                _ex("tscourse-w5-arr-4", "Arrow returning text",
                    "Return an initial-plus-dot for a name: `Ada` → `A.`",
                    _FS + 'const initial = (name: string): string => `${name[0].toUpperCase()}.`;\n'
                    'const s = fs.readFileSync(0, "utf8").trim();\nconsole.log(initial(s));\n',
                    '`${name[0].toUpperCase()}.`',
                    [("Ada", "A."), ("bo", "B.")],
                    hints=["Take the first character, uppercase it, and append a dot.",
                           "Write `${name[0].toUpperCase()}.`"],
                    difficulty="Medium"),
                _ex("tscourse-w5-arr-5", "Explicit return in a block",
                    "This arrow needs a block because it has two statements. Add the return.",
                    'const doubleThenAddOne = (x: number): number => {\n'
                    '  const d = x * 2;\n  return d + 1;\n};\n'
                    'console.log(doubleThenAddOne(5));\n',
                    'return d + 1;', [("", "11")],
                    hints=["Inside braces nothing is returned automatically.",
                           "Write return d + 1;"]),
                _fix("tscourse-w5-arr-fix1", "Fix the arrow body",
                     "This prints undefined instead of 8. Fix it so cube(2) is 8.",
                     'const cube = (x: number): number => { x * x * x; };\nconsole.log(cube(2));\n',
                     'const cube = (x: number): number => x * x * x;\nconsole.log(cube(2));\n',
                     [("", "8")],
                     hints=["With braces you must return explicitly.",
                            "Either add return, or drop the braces for the implicit return."]),
                _fix("tscourse-w5-arr-fix2", "Fix the too-early call",
                     "This crashes because the arrow is used before it exists. Fix it by moving the call.",
                     'console.log(half(10));\nconst half = (x: number): number => x / 2;\n',
                     'const half = (x: number): number => x / 2;\nconsole.log(half(10));\n',
                     [("", "5")],
                     hints=["Arrow functions stored in a const are not hoisted.",
                            "Define it first, then call it."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`(x) => x * 2` returns…",
                   ["undefined", "2x", "a block", "an error"], 1,
                   "A braceless body returns its expression."),
                _q("`(x) => { x * 2 }` returns…",
                   ["2x", "undefined", "a block", "an error"], 1,
                   "A block returns nothing unless you write return."),
            ],
        ),
        # ---- Lesson 4 --------------------------------------------------
        _lesson(
            "w5-guards", "Guard clauses & early return",
            "Handling the awkward cases first, and keeping the main path flat.",
            """
`return` ends the function *immediately*. That's not just a way to produce a
value — it's a structural tool.

Compare. Nested:

```ts
function describe(n: number): string {
  if (!Number.isNaN(n)) {
    if (n >= 0) {
      if (n <= 100) {
        return "in range";
      } else {
        return "too big";
      }
    } else {
      return "negative";
    }
  } else {
    return "not a number";
  }
}
```

Guarded:

```ts
function describe(n: number): string {
  if (Number.isNaN(n)) return "not a number";
  if (n < 0) return "negative";
  if (n > 100) return "too big";
  return "in range";
}
```

Same behaviour. The second version reads top to bottom as a list of rejections
followed by the answer, never indents past one level, and lets you add a rule by
adding a line.

**The pattern:** deal with every exceptional case first, each with its own early
`return`. By the time you reach the last line, everything awkward has already
left the building — so the **happy path** sits at the end, unindented, with no
conditions attached.

**Order still matters**, exactly as in an `else if` chain. Each guard may assume
all the earlier ones passed, which is precisely what makes them short.

**Multiple returns are fine.** Some people are taught "one return per function".
For guard clauses, that advice makes code worse: it forces a mutable result
variable and deeper nesting. Prefer several early returns.

> ⚠️ **Common mistakes:** guards in the wrong order (a broad one first makes the
> rest unreachable); forgetting a final return, so some path yields `undefined`;
> and writing `if (cond) return;` in a function that's supposed to return a
> value.
""",
            warmup=[
                _q("What does an early `return` do to the rest of the body?",
                   ["Runs it anyway", "Skips it entirely", "Runs it later", "Errors"], 1,
                   "The function ends there and then."),
                _q("A guard clause's main benefit is…",
                   ["speed", "keeping the main path flat and unindented",
                    "fewer characters", "type safety"], 1,
                   "Readability: exceptions first, answer last."),
                _q("If a function's last guard is missing and no path returns, the result is…",
                   ["0", "undefined", "an error", "the last value computed"], 1,
                   "undefined — and TypeScript will usually warn you."),
            ],
            exercises=[
                _ex("tscourse-w5-grd-1", "Reject the bad case first",
                    "Return `not a number` for NaN input, otherwise the doubled value as a string.",
                    _FS + 'function describe(n: number): string {\n'
                    '  if (Number.isNaN(n)) return "not a number";\n'
                    '  return String(n * 2);\n}\n'
                    'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'if (Number.isNaN(n)) return "not a number";',
                    [("abc", "not a number"), ("21", "42")],
                    hints=["One line: test the bad case and return immediately.",
                           'Write if (Number.isNaN(n)) return "not a number";']),
                _ex("tscourse-w5-grd-2", "A ladder of guards",
                    "Return `negative`, `too big` (over 100) or `in range`.",
                    _FS + 'function describe(n: number): string {\n'
                    '  if (n < 0) return "negative";\n'
                    '  if (n > 100) return "too big";\n'
                    '  return "in range";\n}\n'
                    'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'if (n > 100) return "too big";',
                    [("-1", "negative"), ("150", "too big"), ("50", "in range"), ("100", "in range")],
                    hints=["The second guard only sees non-negative numbers.",
                           'Write if (n > 100) return "too big";']),
                _ex("tscourse-w5-grd-3", "Empty first",
                    "Return `(empty)` for an empty string, otherwise the string uppercased.",
                    _FS + 'function label(s: string): string {\n'
                    '  if (!s) return "(empty)";\n'
                    '  return s.toUpperCase();\n}\n'
                    'console.log(label(fs.readFileSync(0, "utf8").trim()));\n',
                    '!s',
                    [("", "(empty)"), ("hi", "HI")],
                    hints=["An empty string is falsy.", "The guard condition is !s."]),
                _ex("tscourse-w5-grd-4", "The happy path last",
                    "Complete the function so a valid, non-negative amount returns its formatted value.",
                    _FS + 'function money(n: number): string {\n'
                    '  if (Number.isNaN(n)) return "invalid";\n'
                    '  if (n < 0) return "negative";\n'
                    '  return `$${n.toFixed(2)}`;\n}\n'
                    'console.log(money(Number(fs.readFileSync(0, "utf8").trim())));\n',
                    'return `$${n.toFixed(2)}`;',
                    [("abc", "invalid"), ("-2", "negative"), ("7.5", "$7.50")],
                    hints=["By this line the value is known to be a valid non-negative number.",
                           "Return `$${n.toFixed(2)}`."],
                    difficulty="Medium"),
                _ex("tscourse-w5-grd-5", "Guard inside a loop-free check",
                    "Return `too short` when the input is under 3 characters, `too long` over 10, else `ok`.",
                    _FS + 'function check(s: string): string {\n'
                    '  if (s.length < 3) return "too short";\n'
                    '  if (s.length > 10) return "too long";\n'
                    '  return "ok";\n}\n'
                    'console.log(check(fs.readFileSync(0, "utf8").trim()));\n',
                    's.length < 3',
                    [("ab", "too short"), ("abcdefghijk", "too long"), ("hello", "ok"), ("abc", "ok")],
                    hints=["3 itself is acceptable, so the rejection is strictly under 3.",
                           "Write s.length < 3."]),
                _fix("tscourse-w5-grd-fix1", "Fix the guard order",
                     "Every input returns `in range`, even -5. Fix the order.",
                     _FS + 'function describe(n: number): string {\n'
                     '  if (n <= 100) return "in range";\n'
                     '  if (n < 0) return "negative";\n'
                     '  return "too big";\n}\n'
                     'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                     _FS + 'function describe(n: number): string {\n'
                     '  if (n < 0) return "negative";\n'
                     '  if (n > 100) return "too big";\n'
                     '  return "in range";\n}\n'
                     'console.log(describe(Number(fs.readFileSync(0, "utf8").trim())));\n',
                     [("-5", "negative"), ("150", "too big"), ("50", "in range")],
                     hints=["`n <= 100` is true for every negative number too, so it fires first.",
                            "Reject the negative case before testing the range."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Guard clauses replace…",
                   ["loops", "deep if/else nesting", "type annotations", "return values"], 1,
                   "They flatten the structure by leaving early."),
                _q("'One return per function' applied to guard clauses tends to…",
                   ["improve them", "force a mutable result variable and more nesting",
                    "make them faster", "have no effect"], 1,
                   "Which is why the rule is not followed in modern code."),
            ],
        ),
        # ---- Lesson 5 --------------------------------------------------
        _lesson(
            "w5-defaults", "Defaults, optionals & void",
            "Parameters that don't always have to be supplied.",
            """
**Default parameters** supply a value when the argument is omitted:

```ts
function withTax(amount: number, rate: number = 0.08): number {
  return amount * (1 + rate);
}

withTax(100)        // 108   — rate defaulted to 0.08
withTax(100, 0.2)   // 120
```

The default is evaluated **only when the argument is missing** (or explicitly
`undefined`). Passing `0` is a real value and overrides it — passing `0` and
getting the default anyway is the bug people expect here and don't get. Good.

**Defaults must come last.** Otherwise you'd have no way to skip them:

```ts
function bad(rate: number = 0.08, amount: number): number { ... }  // ⚠️ awkward
```

**Optional parameters** use `?` and may simply be absent, arriving as
`undefined`:

```ts
function greet(name: string, title?: string): string {
  if (title === undefined) return `Hi ${name}`;
  return `Hi ${title} ${name}`;
}

greet("Ada")            // Hi Ada
greet("Ada", "Dr")      // Hi Dr Ada
```

Use a **default** when there's a sensible fallback value; use **optional** when
absence itself means something different.

**`void`** is the return type of a function that returns nothing useful —
typically because its whole job is a side effect like printing:

```ts
function banner(text: string): void {
  console.log(text);
  console.log("-".repeat(text.length));
}
```

Annotating `void` is a promise to the reader: *don't expect a value back from
this*.

> ⚠️ **Common mistakes:** putting a defaulted parameter before a required one;
> assuming a default fires for `0` or `""` (it doesn't — only for `undefined`);
> and forgetting to handle the `undefined` case of an optional parameter.
""",
            warmup=[
                _q("`function f(a: number, b: number = 2){ return a + b; } f(5)` is…",
                   ["5", "7", "undefined", "an error"], 1, "b defaults to 2."),
                _q("`function f(a: number, b: number = 2){ return a + b; } f(5, 0)` is…",
                   ["7", "5", "2", "undefined"], 1,
                   "0 is a real argument, so the default is not used."),
                _q("An optional parameter that is not passed arrives as…",
                   ["0", "null", "undefined", '""'], 2, "undefined."),
                _q("A function annotated `: void`…",
                   ["returns 0", "returns nothing useful", "cannot be called",
                    "returns a string"], 1,
                   "It exists for its side effect."),
            ],
            exercises=[
                _ex("tscourse-w5-def-1", "Give the rate a default",
                    "Default the tax rate to 0.08 so withTax(100) prints 108.00.",
                    'function withTax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * (1 + rate);\n}\n'
                    'console.log(withTax(100).toFixed(2));\n',
                    'rate: number = 0.08', [("", "108.00")],
                    hints=["A default is written with = in the parameter list.",
                           "Write rate: number = 0.08."]),
                _ex("tscourse-w5-def-2", "Override the default",
                    "Call withTax with an explicit 20% rate so it prints 120.",
                    'function withTax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * (1 + rate);\n}\n'
                    'console.log(withTax(100, 0.2));\n',
                    'withTax(100, 0.2)', [("", "120")],
                    hints=["Pass the rate as a second argument.",
                           "Write withTax(100, 0.2)."]),
                _ex("tscourse-w5-def-3", "A default separator",
                    "Default the separator to `, ` so join2(\"a\", \"b\") is `a, b`.",
                    'function join2(a: string, b: string, sep: string = ", "): string {\n'
                    '  return a + sep + b;\n}\n'
                    'console.log(join2("a", "b"));\n',
                    'sep: string = ", "', [("", "a, b")],
                    hints=["The default goes in the parameter list.",
                           'Write sep: string = ", ".']),
                _ex("tscourse-w5-def-4", "Handle the optional",
                    "Return `Hi Ada` when no title is given, `Hi Dr Ada` when one is.",
                    'function greet(name: string, title?: string): string {\n'
                    '  if (title === undefined) return `Hi ${name}`;\n'
                    '  return `Hi ${title} ${name}`;\n}\n'
                    'console.log(greet("Ada"));\nconsole.log(greet("Ada", "Dr"));\n',
                    'title === undefined',
                    [("", "Hi Ada\nHi Dr Ada")],
                    hints=["An omitted optional parameter is undefined.",
                           "Test title === undefined."],
                    difficulty="Medium"),
                _ex("tscourse-w5-def-5", "A void helper",
                    "Complete the banner function's return type — it only prints, so it hands nothing back.",
                    'function banner(text: string): void {\n'
                    '  console.log(text);\n  console.log("-".repeat(text.length));\n}\n'
                    'banner("Report");\n',
                    'void', [("", "Report\n------")],
                    hints=["There is a return type reserved for functions that return nothing useful.",
                           "The annotation is void."]),
                _fix("tscourse-w5-def-fix1", "Fix the parameter order",
                     "A defaulted parameter sits before a required one, which forces every caller to pass both. Reorder them so `charge(100)` works and prints 108.00.",
                     # The call site must stay `charge(100)`. Writing it as
                     # `charge(0.08, 100)` worked around the very bug the
                     # exercise is about, so the starter already passed.
                     'function charge(rate: number = 0.08, amount: number): number {\n'
                     '  return amount * (1 + rate);\n}\n'
                     'console.log(charge(100).toFixed(2));\n',
                     'function charge(amount: number, rate: number = 0.08): number {\n'
                     '  return amount * (1 + rate);\n}\n'
                     'console.log(charge(100).toFixed(2));\n',
                     [("", "108.00")],
                     hints=["Optional and defaulted parameters belong at the end.",
                            "Put amount first, then rate with its default, and simplify the call."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("A default parameter fires when the argument is…",
                   ["0", '""', "undefined or omitted", "null"], 2,
                   "Only undefined (or absent) triggers it."),
                _q("Defaulted and optional parameters must be…",
                   ["first", "last", "alphabetical", "annotated as any"], 1,
                   "Otherwise callers could not skip them."),
            ],
        ),
        # ---- Lesson 6 --------------------------------------------------
        _lesson(
            "w5-scope", "Scope, shadowing & purity",
            "Where names live, and why some functions are easier to trust.",
            """
**Scope** is the region of code where a name is visible. `let` and `const` are
**block-scoped**: they exist inside the nearest `{ }` and nowhere else.

```ts
function f(): void {
  const inner = 1;
  console.log(inner);      // fine
}
console.log(inner);        // ❌ not defined out here
```

A function can *read* names from the scope around it, but the outside can't see
in. That asymmetry is the point: a function's internals are its own business.

**Shadowing** happens when an inner name reuses an outer one:

```ts
const n = 1;
function f(): number {
  const n = 2;      // shadows the outer n inside this function
  return n;         // 2
}
console.log(f(), n);   // 2 1
```

Legal, occasionally useful, and a frequent source of confusion — if you find
yourself shadowing by accident, rename.

**Side effects and purity.** A function has a **side effect** if it does
anything beyond computing its return value: printing, modifying an outer
variable, writing a file.

```ts
let total = 0;

function addImpure(x: number): void {
  total += x;                       // side effect: changes the outside
}

function addPure(a: number, b: number): number {
  return a + b;                     // pure: same inputs, same output, no effects
}
```

A **pure** function is easier to trust because:

- You can test it by calling it — nothing needs to be set up first.
- Reading the call site tells you everything that happens.
- Calling it twice with the same input can never differ.

You can't make everything pure — programs have to print things and save
things eventually. The useful discipline is to **keep the calculation pure and
push the side effects to the edges**: compute the report with pure helpers, then
print it once at the end.

> ⚠️ **Common mistakes:** relying on an outer `let` that another part of the
> program also changes; shadowing a name by accident; and mixing computing with
> printing inside one function, which makes it impossible to reuse.
""",
            warmup=[
                _q("A `const` declared inside a function is visible…",
                   ["everywhere", "only inside that function", "only after it",
                    "only in the parameter list"], 1,
                   "Block scope: it exists inside those braces only."),
                _q("`const n = 1; function f(){ const n = 2; return n; } f()` returns…",
                   ["1", "2", "3", "an error"], 1, "The inner n shadows the outer one."),
                _q("Which is pure?",
                   ["one that prints its result", "one that returns a value and changes nothing else",
                    "one with no parameters", "one that reads input"], 1,
                   "No side effects, and the same output for the same input."),
            ],
            exercises=[
                _ex("tscourse-w5-scope-1", "Keep it local",
                    "Complete the function so the calculation happens with a local name.",
                    'function area(w: number, h: number): number {\n'
                    '  const result = w * h;\n  return result;\n}\n'
                    'console.log(area(3, 4));\n',
                    'const result = w * h;', [("", "12")],
                    hints=["Name the intermediate value inside the function.",
                           "Write const result = w * h;"]),
                _ex("tscourse-w5-scope-2", "Return, don't print",
                    "Make the function pure — it must return the label so the caller can print it.",
                    'function label(n: number): string {\n'
                    '  return `Total: ${n}`;\n}\n'
                    'console.log(label(42));\n',
                    'return `Total: ${n}`;', [("", "Total: 42")],
                    hints=["A pure function hands the text back rather than logging it.",
                           "Write return `Total: ${n}`;"]),
                _ex("tscourse-w5-scope-3", "Shadowing on purpose",
                    "Inside the function, declare a local `n` of 2 so it returns 2 while the outer n stays 1.",
                    'const n = 1;\nfunction f(): number {\n  const n = 2;\n  return n;\n}\n'
                    'console.log(f());\nconsole.log(n);\n',
                    'const n = 2;', [("", "2\n1")],
                    hints=["A same-named const inside the function shadows the outer one.",
                           "Write const n = 2; inside f."],
                    difficulty="Medium"),
                _ex("tscourse-w5-scope-4", "Pure calculation, printed once",
                    "Compute the whole report string in a pure helper, then print it in one place.",
                    _FS + 'function report(name: string, amount: number): string {\n'
                    '  return `${name}: $${amount.toFixed(2)}`;\n}\n'
                    'const s = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(report(s, 12.5));\n',
                    'console.log(report(s, 12.5));',
                    [("Coffee", "Coffee: $12.50"), ("Rent", "Rent: $12.50")],
                    hints=["The helper builds the text; the caller does the printing.",
                           "Write console.log(report(s, 12.5));"]),
                _ex("tscourse-w5-scope-5", "Read from the enclosing scope",
                    "The tax rate lives outside the function. Use it inside.",
                    'const RATE = 0.1;\nfunction withTax(amount: number): number {\n'
                    '  return amount * (1 + RATE);\n}\n'
                    'console.log(withTax(100).toFixed(2));\n',
                    'amount * (1 + RATE)', [("", "110.00")],
                    hints=["A function can read names from the scope around it.",
                           "Write amount * (1 + RATE)."]),
                _fix("tscourse-w5-scope-fix1", "Fix the leaky helper",
                     "This should total 5 but prints 3 — the side effect overwrites instead of accumulating. Fix it.",
                     'let total = 0;\nfunction add(x: number): void {\n  total = x;\n}\n'
                     'add(2);\nadd(3);\nconsole.log(total);\n',
                     'let total = 0;\nfunction add(x: number): void {\n  total += x;\n}\n'
                     'add(2);\nadd(3);\nconsole.log(total);\n',
                     [("", "5")],
                     hints=["Each call replaces the shared variable, so only the last one survives.",
                            "It should add to what is already there: total += x;",
                            "Worth noticing: this bug is only possible because the function reaches outside itself. A pure `add(a, b)` returning a + b could not go wrong this way."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("Why is a pure function easier to test?",
                   ["It is shorter", "Calling it with inputs is the entire test — no setup, no cleanup",
                    "It cannot fail", "It has no parameters"], 1,
                   "Nothing outside it has to be arranged or inspected."),
                _q("The practical discipline with side effects is…",
                   ["never use them", "keep calculation pure and push effects to the edges",
                    "put them everywhere", "use only global variables"], 1,
                   "Compute with pure helpers, print or save once at the boundary."),
            ],
        ),
        # ---- Lesson 7 --------------------------------------------------
        _lesson(
            "w5-values", "Functions as values",
            "Passing behaviour around, not just data.",
            """
A function is a **value**. You can store it in a variable, and you can pass it
to another function — which is exactly what `const cube = ...` has been doing
all along.

```ts
const cube = (x: number): number => x * x * x;
const f = cube;         // no parentheses — the function itself
console.log(f(2));      // 8
```

**The parentheses are the difference.** `cube` is the function; `cube(2)` is the
result of running it. Passing `cube(2)` where a function was expected is the
mistake to watch for.

**A function that takes a function:**

```ts
function applyTwice(f: (x: number) => number, x: number): number {
  return f(f(x));
}

console.log(applyTwice(cube, 2));   // cube(cube(2)) = cube(8) = 512
```

Read the parameter's annotation `(x: number) => number` as *"a function taking a
number and returning a number"*. That's the **signature**, and TypeScript checks
that whatever you pass matches it.

A function that takes or returns another function is called a **higher-order
function**. They let you write the *shape* of an operation once and supply the
varying part at the call site:

```ts
function twice(f: (s: string) => string, s: string): string {
  return f(f(s));
}
const excite = (s: string): string => s + "!";
console.log(twice(excite, "wow"));   // wow!!
```

**Why this matters next week.** Arrays come with built-in higher-order methods —
`map`, `filter`, `reduce` — each of which takes exactly this: a small function
describing what to do with one item. Everything in week 6 rests on being
comfortable with the idea that a function can be an argument.

**Inline arrows.** You'll usually define the little function right at the call
site rather than naming it:

```ts
console.log(applyTwice((x: number): number => x + 3, 10));   // 16
```

> ⚠️ **Common mistakes:** passing `f(x)` (the result) where `f` (the function)
> was wanted; annotating a function parameter as `number` instead of a signature;
> and forgetting that the inner function's parameter name is entirely its own.
""",
            warmup=[
                _q("`const g = cube;` stores…",
                   ["the result of cube", "the function itself", "a string", "undefined"], 1,
                   "No parentheses means no call."),
                _q("`applyTwice(cube, 2)` computes…",
                   ["cube(2)", "cube(cube(2))", "2 * cube", "an error"], 1,
                   "The function is applied to its own result."),
                _q("`(x: number) => number` as a parameter type means…",
                   ["a number", "a function from number to number", "an arrow", "a string"], 1,
                   "It is the signature of the function you must pass."),
            ],
            exercises=[
                _ex("tscourse-w5-val-1", "Store a function",
                    "Point `f` at the `cube` function (do not call it), then use it.",
                    'const cube = (x: number): number => x * x * x;\n'
                    'const f = cube;\nconsole.log(f(2));\n',
                    'const f = cube;', [("", "8")],
                    hints=["No parentheses — you want the function, not its result.",
                           "Write const f = cube;"]),
                _ex("tscourse-w5-val-2", "Apply it twice",
                    "Complete applyTwice so it feeds its own result back in.",
                    'const cube = (x: number): number => x * x * x;\n'
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice(cube, 2));\n',
                    'return f(f(x));', [("", "512")],
                    hints=["Call f on x, then call f on that.",
                           "Write return f(f(x));"],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-3", "Annotate the parameter",
                    "Fill in the signature for a parameter that takes a number and returns a number.",
                    'function applyOnce(f: (x: number) => number, x: number): number {\n'
                    '  return f(x);\n}\n'
                    'console.log(applyOnce((n: number): number => n + 1, 41));\n',
                    '(x: number) => number', [("", "42")],
                    hints=["The type of a function is written like an arrow function without a body.",
                           "Write (x: number) => number."],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-4", "Pass an inline arrow",
                    "Pass a function that adds 3, so the result is 16.",
                    'function applyTwice(f: (x: number) => number, x: number): number {\n'
                    '  return f(f(x));\n}\n'
                    'console.log(applyTwice((x: number): number => x + 3, 10));\n',
                    '(x: number): number => x + 3',
                    [("", "16")],
                    hints=["Define the little function right at the call site.",
                           "Write (x: number): number => x + 3."],
                    difficulty="Medium"),
                _ex("tscourse-w5-val-5", "A string transformer",
                    "Pass a function that appends an exclamation mark, so `wow` becomes `wow!!`.",
                    _FS + 'function twice(f: (s: string) => string, s: string): string {\n'
                    '  return f(f(s));\n}\n'
                    'const input = fs.readFileSync(0, "utf8").trim();\n'
                    'console.log(twice((s: string): string => s + "!", input));\n',
                    '(s: string): string => s + "!"',
                    [("wow", "wow!!"), ("hi", "hi!!")],
                    hints=["Each application adds one character.",
                           'Write (s: string): string => s + "!".'],
                    difficulty="Medium"),
                _fix("tscourse-w5-val-fix1", "Fix the accidental call",
                     "This passes the RESULT of cube instead of the function, and crashes. Fix it.",
                     'const cube = (x: number): number => x * x * x;\n'
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'console.log(applyTwice(cube(2), 2));\n',
                     'const cube = (x: number): number => x * x * x;\n'
                     'function applyTwice(f: (x: number) => number, x: number): number {\n'
                     '  return f(f(x));\n}\n'
                     'console.log(applyTwice(cube, 2));\n',
                     [("", "512")],
                     hints=["cube(2) is the number 8; applyTwice wants something it can call.",
                            "Drop the parentheses: pass cube."],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("`f` versus `f(x)` — the difference is…",
                   ["none", "f is the function; f(x) is the result of running it",
                    "f is faster", "f(x) is the function"], 1,
                   "Parentheses mean 'run it now'."),
                _q("A higher-order function is one that…",
                   ["is very long", "takes or returns another function",
                    "has many parameters", "returns void"], 1,
                   "map, filter and reduce — next week — are all higher-order."),
            ],
        ),
        # ---- Lesson 8 --------------------------------------------------
        _lesson(
            "w5-closures", "Functions that build functions",
            "Returning a function, and the variables it remembers.",
            """
A function can **return** a function, just as it can return a number. That
sounds like a curiosity; it's actually one of the most useful tools you have.

```ts
function multiplier(factor: number): (x: number) => number {
  return (x: number): number => x * factor;
}

const double = multiplier(2);
const triple = multiplier(3);
console.log(double(10));   // 20
console.log(triple(10));   // 30
```

Read the return type `(x: number) => number` as *"…and it hands back a function
from number to number."*

**The remembering part.** `multiplier(2)` finishes and returns. Yet the little
function it produced still knows that `factor` was 2 — forever. A function
bundled together with the variables it captured from the scope around it is
called a **closure**.

```ts
function counter(): () => number {
  let n = 0;                       // lives on, privately
  return (): number => {
    n = n + 1;
    return n;
  };
}

const next = counter();
console.log(next());   // 1
console.log(next());   // 2
console.log(next());   // 3
```

`n` is not a global and nothing outside can touch it, but it survives between
calls because the returned function still holds a reference to it. That's a
**private variable** — genuinely private, enforced by scope rather than
convention.

**Each call makes a fresh one.** `counter()` twice gives two independent
counters with two separate `n`s. This is why closures are how you make
*configured* behaviour:

```ts
const withRate = multiplier(1.08);    // a tax function, configured once
```

**Where you'll meet this next.** A closure is what makes `filter` calls like
this work:

```ts
const limit = 10;
items.filter((x) => x > limit);       // the arrow captured `limit`
```

The little function you hand to `filter` reaches out and remembers `limit` from
the surrounding scope. You've been relying on closures without naming them.

> ⚠️ **Common mistakes:** calling the outer function every time
> (`multiplier(2)(10)` works but throws away the configured function); expecting
> two calls to the factory to share state (they don't); and returning the
> *result* rather than the function — `return x * factor;` in the outer body is
> a different program entirely.
""",
            warmup=[
                _q("`const double = multiplier(2); double(10)` gives…",
                   ["2", "10", "20", "a function"], 2, "factor is 2, so 10 * 2."),
                _q("After `const a = counter(); const b = counter(); a(); a(); b();` what did the last call print?",
                   ["3", "2", "1", "0"], 2,
                   "b has its own independent n, so its first call is 1."),
                _q("A closure is…",
                   ["a loop that closes", "a function plus the variables it captured",
                    "a type annotation", "a return statement"], 1,
                   "The function keeps its surrounding variables alive."),
            ],
            exercises=[
                _ex("tscourse-w5-clo-1", "Return a function",
                    "Complete multiplier so it hands back a function that multiplies by factor.",
                    'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x: number): number => x * factor;\n}\n'
                    'const double = multiplier(2);\nconsole.log(double(10));\n',
                    'return (x: number): number => x * factor;', [("", "20")],
                    hints=["The outer function returns a function, not a number.",
                           "Write return (x: number): number => x * factor;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-2", "Configure it once",
                    "Build a tripling function from the factory, then use it.",
                    _FS + 'function multiplier(factor: number): (x: number) => number {\n'
                    '  return (x: number): number => x * factor;\n}\n'
                    'const triple = multiplier(3);\n'
                    'const n = Number(fs.readFileSync(0, "utf8").trim());\nconsole.log(triple(n));\n',
                    'multiplier(3)', [("5", "15"), ("10", "30")],
                    hints=["Call the factory once with the factor you want.",
                           "Write multiplier(3)."]),
                _ex("tscourse-w5-clo-3", "A private counter",
                    "Complete the returned function so each call gives the next number.",
                    'function counter(): () => number {\n  let n = 0;\n'
                    '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                    'const next = counter();\nconsole.log(next());\nconsole.log(next());\nconsole.log(next());\n',
                    'n = n + 1;\n    return n;', [("", "1\n2\n3")],
                    hints=["Advance the captured variable, then hand it back.",
                           "Write n = n + 1; then return n;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-4", "A configured greeter",
                    "Return a function that greets a name with the captured greeting word.",
                    _FS + 'function greeterFor(word: string): (name: string) => string {\n'
                    '  return (name: string): string => `${word}, ${name}!`;\n}\n'
                    'const hello = greeterFor("Hello");\n'
                    'const who = fs.readFileSync(0, "utf8").trim();\nconsole.log(hello(who));\n',
                    '`${word}, ${name}!`', [("Ada", "Hello, Ada!"), ("Bo", "Hello, Bo!")],
                    hints=["The inner function sees both its own parameter and the captured word.",
                           "Write `${word}, ${name}!`."],
                    difficulty="Medium"),
                _ex("tscourse-w5-clo-5", "Two independent counters",
                    "Show that each factory call gets its own state: print a's first two, then b's first.",
                    'function counter(): () => number {\n  let n = 0;\n'
                    '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                    'const a = counter();\nconst b = counter();\n'
                    'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                    'const b = counter();', [("", "1\n2\n1")],
                    hints=["b must come from its own call to the factory.",
                           "Write const b = counter();"],
                    difficulty="Medium"),
                _fix("tscourse-w5-clo-fix1", "Fix the factory that forgot to be one",
                     "This should print 20, but the factory returns a number instead of a function. Fix it.",
                     'function multiplier(factor: number): (x: number) => number {\n'
                     '  return factor;\n}\n'
                     'const double = multiplier(2);\nconsole.log(double(10));\n',
                     'function multiplier(factor: number): (x: number) => number {\n'
                     '  return (x: number): number => x * factor;\n}\n'
                     'const double = multiplier(2);\nconsole.log(double(10));\n',
                     [("", "20")],
                     hints=["`double` is supposed to be callable, but it was handed the number 2.",
                            "Return a function: (x: number): number => x * factor."],
                     difficulty="Medium"),
                _fix("tscourse-w5-clo-fix2", "Fix the shared state",
                     "These two counters should be independent — expected 1, 2, 1 — but the second one continues the first. Fix it.",
                     'function counter(): () => number {\n  let n = 0;\n'
                     '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                     'const a = counter();\nconst b = a;\n'
                     'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                     'function counter(): () => number {\n  let n = 0;\n'
                     '  return (): number => {\n    n = n + 1;\n    return n;\n  };\n}\n'
                     'const a = counter();\nconst b = counter();\n'
                     'console.log(a());\nconsole.log(a());\nconsole.log(b());\n',
                     [("", "1\n2\n1")],
                     hints=["`const b = a;` points b at the SAME function, so it shares a's captured n.",
                            "Call the factory again to get a fresh one: const b = counter();"],
                     difficulty="Medium"),
            ],
            quiz=[
                _q("What keeps `factor` alive after `multiplier` has returned?",
                   ["a global variable", "the closure — the returned function captured it",
                    "nothing, it is copied", "the type annotation"], 1,
                   "The returned function holds a reference to the scope it was created in."),
                _q("`(x: number) => number` written as a RETURN type means…",
                   ["the function returns a number", "the function returns another function",
                    "the parameter is a function", "it is a syntax error"], 1,
                   "The whole arrow notation is the type of the returned value."),
                _q("Why is the `n` inside `counter` effectively private?",
                   ["it is const", "nothing outside the closure has a reference to it",
                    "it is annotated private", "it is a global"], 1,
                   "Scope, not convention, enforces it."),
            ],
        ),
        # ---- Lesson 9 --------------------------------------------------
        _lesson(
            "w5-design", "Designing a function",
            "Contract first, trace by hand, extract the duplication.",
            """
You can now *write* functions. This lesson is about *deciding* which functions
to write — the judgement that separates code you can live with from code you
can't.

**1. Write the contract before the body.** A contract is four short answers:

| question | for `shipping` |
|---|---|
| What is it called? | `shipping` |
| What goes in? | `weight: number` — kilograms, never negative |
| What comes out? | `number` — the cost in dollars |
| What must be true? | the caller passes kilograms, not grams |

Write the signature first and the body almost writes itself:

```ts
function shipping(weight: number): number {
  return 0;   // stub — fill this in once the shape is agreed
}
```

A stub that compiles is a real milestone: the rest of the program can already
call it while you work out the arithmetic.

**2. Trace a call by hand.** When something is wrong, don't guess — substitute.

```ts
function twice(x: number): number { return x * 2; }
function inc(x: number): number { return x + 1; }
console.log(inc(twice(5)));
```

```
inc(twice(5))
inc(10)          // twice(5) returned 10 — the call is REPLACED by its value
11
```

Innermost call first, replace it with what it returned, repeat. Nearly every
debugging session you will ever have is this, done patiently.

**3. Extract on the third repetition.** Two similar lines are a coincidence;
three are a pattern. When you copy a line and edit one number, that number is a
parameter and the line is a function:

```ts
console.log((10 * 1.2).toFixed(2));    // copy…
console.log((25 * 1.2).toFixed(2));    // …paste…
console.log((99 * 1.2).toFixed(2));    // …paste again  ← stop.

function withVat(amount: number): string {
  return (amount * 1.2).toFixed(2);    // the rate now lives in ONE place
}
```

**4. One function, one job.** If the name needs an "and" — `validateAndSave` —
it is two functions wearing one coat. Small named pieces compose; big ones
don't.

**5. Order guards from most specific to least.** Guards are checked top to
bottom and the first match wins, so a broad condition placed first swallows the
narrow ones underneath it. This is the most common logic bug in guarded code.

**6. Choose test cases deliberately.** Before running anything, pick a typical
value, a boundary value (exactly the limit), and a hostile value (zero,
negative, empty). A function that survives those three usually survives the
rest.

> ⚠️ **Common mistakes:** writing the body before deciding what it returns;
> ordering guards widest-first; and a helper that both computes *and* prints,
> which makes it unusable anywhere that has to stay quiet.
""",
            warmup=[
                _q("Trace `inc(twice(5))` where `twice` doubles and `inc` adds 1:",
                   ["11", "12", "10", "6"], 0,
                   "twice(5) is 10; that call is replaced by 10; inc(10) is 11."),
                _q("You copy a line and change one number in it. That number should become…",
                   ["a global", "a parameter", "a comment", "a string"], 1,
                   "The thing that varies between the copies is exactly the input."),
                _q("With `if (s >= 50) return 'pass';` placed ABOVE `if (s >= 80) return 'distinction';`, `grade(90)` is…",
                   ["distinction", "pass", "fail", "undefined"], 1,
                   "The broad guard matched first and returned, so the narrow one never ran."),
                _q("A helper that both computes a total and prints it is hard to…",
                   ["name", "reuse anywhere that must not print", "annotate", "call twice"], 1,
                   "Printing is a side effect, and it decides for every caller."),
            ],
            exercises=[
                _ex("tscourse-w5-des-1", "Fill in the contract",
                    "The body is written. Declare the two parameters it needs: an amount and a rate, both numbers.",
                    'function feeFor(amount: number, rate: number): number {\n'
                    '  return amount * rate;\n}\n'
                    'console.log(feeFor(200, 0.015).toFixed(2));\n',
                    'amount: number, rate: number', [("", "3.00")],
                    hints=["Read the body: which names does it use?",
                           "Two parameters, comma-separated, each annotated : number."]),
                _ex("tscourse-w5-des-2", "Extract the repeated line",
                    "Three lines each multiplied by 1.2 and formatted became one helper. Fill in its body.",
                    'function withVat(amount: number): string {\n'
                    '  return (amount * 1.2).toFixed(2);\n}\n'
                    'console.log(withVat(10));\n'
                    'console.log(withVat(25));\n'
                    'console.log(withVat(99));\n',
                    'return (amount * 1.2).toFixed(2);',
                    [("", "12.00\n30.00\n118.80")],
                    hints=["The part that never changed was `* 1.2` followed by `.toFixed(2)`.",
                           "The part that did change is now the parameter `amount`."]),
                _ex("tscourse-w5-des-3", "Guard the upper bound",
                    "`clamp` pulls any value back inside low..high. The low guard is written; add the high one.",
                    'function clamp(value: number, low: number, high: number): number {\n'
                    '  if (value < low) return low;\n'
                    '  if (value > high) return high;\n'
                    '  return value;\n}\n'
                    'console.log(clamp(15, 0, 10));\n'
                    'console.log(clamp(-4, 0, 10));\n'
                    'console.log(clamp(7, 0, 10));\n',
                    'if (value > high) return high;', [("", "10\n0\n7")],
                    hints=["Mirror the line above it, flipping the comparison.",
                           "Write if (value > high) return high;"],
                    difficulty="Easy"),
                _ex("tscourse-w5-des-4", "Guards in the right order",
                    "Shipping is free at zero weight, a flat $3 below 1 kg, and $3 plus $2 for every whole extra kilogram beyond that. Fill in the last case.",
                    _FS +
                    'function shipping(weight: number): number {\n'
                    '  if (weight <= 0) return 0;\n'
                    '  if (weight < 1) return 3;\n'
                    '  return 3 + Math.ceil(weight - 1) * 2;\n}\n'
                    'const w = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'console.log(shipping(w));\n',
                    'return 3 + Math.ceil(weight - 1) * 2;',
                    [("0", "0"), ("0.5", "3"), ("1", "3"), ("2.5", "7"), ("4", "9")],
                    hints=["Anything from 1 kg up pays the base 3 plus 2 per rounded-up extra kilo.",
                           "Math.ceil(weight - 1) counts those extra kilos.",
                           "Write return 3 + Math.ceil(weight - 1) * 2;"],
                    difficulty="Medium"),
                _ex("tscourse-w5-des-5", "One job each",
                    "`badge` should not know how initials are built — it should call the helper. Fill in that call.",
                    'function initials(first: string, last: string): string {\n'
                    '  return `${first[0]}.${last[0]}.`;\n}\n'
                    'function badge(first: string, last: string, role: string): string {\n'
                    '  return `${initials(first, last)} ${role}`;\n}\n'
                    'console.log(badge("Ada", "Lovelace", "engineer"));\n'
                    'console.log(badge("Grace", "Hopper", "admiral"));\n',
                    'initials(first, last)',
                    [("", "A.L. engineer\nG.H. admiral")],
                    hints=["Pass badge's own two name parameters straight through.",
                           "Write initials(first, last) inside the template literal."]),
                _fix("tscourse-w5-des-fix1", "Fix the guard order",
                     "This should print distinction, pass, fail — but the broad guard is swallowing the narrow one. Reorder it.",
                     'function grade(score: number): string {\n'
                     '  if (score >= 50) return "pass";\n'
                     '  if (score >= 80) return "distinction";\n'
                     '  return "fail";\n}\n'
                     'console.log(grade(90));\n'
                     'console.log(grade(60));\n'
                     'console.log(grade(20));\n',
                     'function grade(score: number): string {\n'
                     '  if (score >= 80) return "distinction";\n'
                     '  if (score >= 50) return "pass";\n'
                     '  return "fail";\n}\n'
                     'console.log(grade(90));\n'
                     'console.log(grade(60));\n'
                     'console.log(grade(20));\n',
                     [("", "distinction\npass\nfail")],
                     hints=["90 is also >= 50, so the first guard returns before the second is ever read.",
                            "Put the most specific test first."],
                     difficulty="Medium"),
                _fix("tscourse-w5-des-fix2", "Fix the leaky helper",
                     "`withFee` adds a flat $2 fee, so both lines should print 12. The second is wrong because the helper accumulates into an outer variable. Make it pure.",
                     'let running = 0;\n'
                     'function withFee(amount: number): number {\n'
                     '  running = running + amount;\n'
                     '  return running + 2;\n}\n'
                     'console.log(withFee(10));\n'
                     'console.log(withFee(10));\n',
                     'function withFee(amount: number): number {\n'
                     '  return amount + 2;\n}\n'
                     'console.log(withFee(10));\n'
                     'console.log(withFee(10));\n',
                     [("", "12\n12")],
                     hints=["The second call remembers the first one — that is a side effect.",
                            "A pure version needs no outer variable at all: return amount + 2."],
                     difficulty="Medium"),
                _fix("tscourse-w5-des-fix3", "Fix the helper that prints",
                     "`describe` logs instead of returning, so the caller cannot build a sentence from it. It should print `Rating: warm`.",
                     'function describe(temp: number): void {\n'
                     '  if (temp > 25) console.log("hot");\n'
                     '  else if (temp > 15) console.log("warm");\n'
                     '  else console.log("cold");\n}\n'
                     'console.log(`Rating: ${describe(20)}`);\n',
                     'function describe(temp: number): string {\n'
                     '  if (temp > 25) return "hot";\n'
                     '  if (temp > 15) return "warm";\n'
                     '  return "cold";\n}\n'
                     'console.log(`Rating: ${describe(20)}`);\n',
                     [("", "Rating: warm")],
                     hints=["A void helper hands back undefined, which is what the template ends up showing.",
                            "Return each word instead of logging it, and change the return type to string.",
                            "With returns you no longer need else — each return already leaves the function."],
                     difficulty="Medium"),
                _ch("tscourse-w5-des-ch1", "Build a three-piece toolkit", "Medium",
                    "Write three helpers. `pct(part, whole)` returns the percentage and 0 when whole is 0; `round1(x)` returns it as a string with one decimal; `bar(value)` returns one `#` per full 10 percent, rounded.",
                    _FS +
                    'function pct(part: number, whole: number): number {\n'
                    '  if (whole === 0) return 0;\n'
                    '  return (part / whole) * 100;\n}\n'
                    'function round1(x: number): string {\n'
                    '  return x.toFixed(1);\n}\n'
                    'function bar(value: number): string {\n'
                    '  return "#".repeat(Math.round(value / 10));\n}\n'
                    'const done = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'const total = 40;\n'
                    'const p = pct(done, total);\n'
                    'console.log(`${round1(p)}%`);\n'
                    'console.log(bar(p));\n',
                    'function pct(part: number, whole: number): number {\n'
                    '  if (whole === 0) return 0;\n'
                    '  return (part / whole) * 100;\n}\n'
                    'function round1(x: number): string {\n'
                    '  return x.toFixed(1);\n}\n'
                    'function bar(value: number): string {\n'
                    '  return "#".repeat(Math.round(value / 10));\n}',
                    [("10", "25.0%\n###"), ("20", "50.0%\n#####"), ("40", "100.0%\n##########")],
                    hints=["Write the three signatures first, each returning a stub, then fill the bodies one at a time.",
                           "pct needs a guard: reject whole === 0 before dividing.",
                           "round1 is a one-liner over toFixed(1).",
                           'bar uses "#".repeat(n) where n is Math.round(value / 10).']),
            ],
            quiz=[
                _q("What should you decide before writing a function's body?",
                   ["its length", "its name, inputs, output and preconditions",
                    "which file it lives in", "whether it is an arrow function"], 1,
                   "That is the contract — everything else follows from it."),
                _q("Tracing `inc(twice(5))`, the first step is to…",
                   ["run inc", "replace twice(5) with 10", "print both", "read right to left"], 1,
                   "Innermost call first: substitute its return value, then continue."),
                _q("Guards should be ordered…",
                   ["alphabetically", "most specific first", "widest first", "any order works"], 1,
                   "The first matching guard returns, so a wide one placed first hides the rest."),
                _q("A name like `validateAndSave` hints that…",
                   ["it is too short", "it is doing two jobs and wants splitting",
                    "it needs a return type", "it should be an arrow function"], 1,
                   "The 'and' is the seam where the function wants to be cut in two."),
            ],
        ),
    ],
    capstone=_cap_auto(
        "Budget Buddy #5 — refactored into helpers",
        """
Budget Buddy has grown into a script. This week you **rebuild it out of named
functions** — which is what a working codebase actually looks like.

Read a **quantity** and print a receipt for coffees at **$3.25** each, with 8%
tax, and a budget of $20:

```
Coffee x4
Subtotal:  $13.00
Tax (8%):  $1.04
Total:     $14.04
Remaining: $5.96
Verdict:   within budget
```

Build it from four helpers — no free-floating arithmetic in the printing code:

- `subtotal(price, qty)` → the pre-tax amount
- `tax(amount, rate = 0.08)` → just the tax portion, with a default rate
- `money(amount)` → a string like `$13.00`
- `verdict(remaining)` → `within budget` when remaining is 0 or more,
  `OVER BUDGET` otherwise

Each helper is **pure** — it returns a value and prints nothing. All the
`console.log` calls live at the bottom.
""",
        _ch("tscourse-w5-capstone", "Budget Buddy #5", "Medium",
            "Write the four helpers, then print the six lines using them.",
            _FS + 'function subtotal(price: number, qty: number): number {\n'
            '  return price * qty;\n}\n'
            'function tax(amount: number, rate: number = 0.08): number {\n'
            '  return amount * rate;\n}\n'
            'function money(amount: number): string {\n'
            '  return `$${amount.toFixed(2)}`;\n}\n'
            'function verdict(remaining: number): string {\n'
            '  if (remaining < 0) return "OVER BUDGET";\n'
            '  return "within budget";\n}\n'
            'const qty = Number(fs.readFileSync(0, "utf8").trim());\n'
            'const price = 3.25;\n'
            'const budget = 20;\n'
            'const sub = subtotal(price, qty);\n'
            'const t = tax(sub);\n'
            'const total = sub + t;\n'
            'console.log(`Coffee x${qty}`);\n'
            'console.log(`Subtotal:  ${money(sub)}`);\n'
            'console.log(`Tax (8%):  ${money(t)}`);\n'
            'console.log(`Total:     ${money(total)}`);\n'
            'console.log(`Remaining: ${money(budget - total)}`);\n'
            'console.log(`Verdict:   ${verdict(budget - total)}`);\n',
            'function subtotal(price: number, qty: number): number {\n'
            '  return price * qty;\n}\n'
            'function tax(amount: number, rate: number = 0.08): number {\n'
            '  return amount * rate;\n}\n'
            'function money(amount: number): string {\n'
            '  return `$${amount.toFixed(2)}`;\n}\n'
            'function verdict(remaining: number): string {\n'
            '  if (remaining < 0) return "OVER BUDGET";\n'
            '  return "within budget";\n}',
            [("4", "Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget"),
             ("10", "Coffee x10\nSubtotal:  $32.50\nTax (8%):  $2.60\nTotal:     $35.10\nRemaining: $-15.10\nVerdict:   OVER BUDGET"),
             ("1", "Coffee x1\nSubtotal:  $3.25\nTax (8%):  $0.26\nTotal:     $3.51\nRemaining: $16.49\nVerdict:   within budget")],
            hints=["Write the four helpers first; the printing code at the bottom already calls them.",
                   "tax returns only the tax portion — amount * rate — not the taxed total.",
                   "money returns a string: `$${amount.toFixed(2)}`.",
                   "verdict is a guard clause: reject the negative case, then return the happy answer.",
                   "Give tax's rate parameter a default of 0.08 so the call site can omit it."]),
        example_io="Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget",
        rubric=["Four named helpers, each doing one thing",
                "Every helper returns a value; none of them prints",
                "tax has a defaulted rate parameter",
                "verdict uses a guard clause rather than nested if/else",
                "All printing happens in one place at the bottom"],
        stretch=_ch("tscourse-w5-capstone-stretch", "Budget Buddy #5 (stretch)", "Medium",
                    "Add a `line(label, value)` helper that formats any row as a label padded to 11 characters followed by the value, and use it for all four money rows — so changing the column width means editing one function.",
                    _FS + 'function subtotal(price: number, qty: number): number {\n'
                    '  return price * qty;\n}\n'
                    'function tax(amount: number, rate: number = 0.08): number {\n'
                    '  return amount * rate;\n}\n'
                    'function money(amount: number): string {\n'
                    '  return `$${amount.toFixed(2)}`;\n}\n'
                    'function verdict(remaining: number): string {\n'
                    '  if (remaining < 0) return "OVER BUDGET";\n'
                    '  return "within budget";\n}\n'
                    'function line(label: string, value: string): string {\n'
                    '  return label.padEnd(11) + value;\n}\n'
                    'const qty = Number(fs.readFileSync(0, "utf8").trim());\n'
                    'const price = 3.25;\n'
                    'const budget = 20;\n'
                    'const sub = subtotal(price, qty);\n'
                    'const t = tax(sub);\n'
                    'const total = sub + t;\n'
                    'console.log(`Coffee x${qty}`);\n'
                    'console.log(line("Subtotal:", money(sub)));\n'
                    'console.log(line("Tax (8%):", money(t)));\n'
                    'console.log(line("Total:", money(total)));\n'
                    'console.log(line("Remaining:", money(budget - total)));\n'
                    'console.log(line("Verdict:", verdict(budget - total)));\n',
                    'function line(label: string, value: string): string {\n'
                    '  return label.padEnd(11) + value;\n}',
                    [("4", "Coffee x4\nSubtotal:  $13.00\nTax (8%):  $1.04\nTotal:     $14.04\nRemaining: $5.96\nVerdict:   within budget")],
                    hints=["padEnd(11) makes every label occupy the same width.",
                           "Write return label.padEnd(11) + value;"]),
    ),
))
