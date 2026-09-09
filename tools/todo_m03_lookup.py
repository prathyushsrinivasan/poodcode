# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 3 — Finding one.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES: arrow functions, `.find(`, `undefined` and the union type
# `Todo | undefined`, narrowing by comparison, and — because the whole track
# runs under `noUncheckedIndexedAccess` — the fact that `todos[0]` has the same
# type as a `find` that missed.
#
# WHY THIS IS ITS OWN MODULE rather than three lines inside module 2: `Todo |
# undefined` is the first union in the project and the direct ancestor of the
# 404. Every "not found" response in the next seventeen modules is this type
# being narrowed. Teaching it as an aside would make module 10 much harder than
# it needs to be.
#
# Still no `.filter`/`.map` (17/14), no `Number(`/`.split(` (10), no object
# spread (11), no `try` (16), no `unknown`/`typeof` (13).
#
# Programs are stdin-free for the reason given in module 1's header.
# ---------------------------------------------------------------------------

_M3_WHY = (
    "`GET /todos/:id` and `PATCH /todos/:id` and `DELETE /todos/:id` all begin "
    "with the same sentence: find the todo with this id. And all three have to "
    "answer the same awkward question first — what if there isn't one? That "
    "question has a type, the type is `Todo | undefined`, and every 404 in the "
    "rest of this project is that type being narrowed. Get it right once, here, "
    "with no HTTP in the way."
)

_M3_BRIEF = """
### The whole module in one line

Look a todo up by id, and be honest in the type system about the case where it
is not there.

### The function you want

```ts
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}
```

Two new things, and the second is the important one.

### `Todo | undefined` — a union

The `|` means *or*. `Todo | undefined` is the type of a value that is either a
todo or nothing at all, and the compiler will not let you treat it as a todo
until you have ruled out the second case:

```ts
const t = findTodo(1);
console.log(t.title);
//          ^ 't' is possibly 'undefined'.
```

That error is the point of the module. It is not the compiler being difficult;
it is the compiler noticing that you have not yet decided what happens when the
todo is missing — and "what happens when it is missing" is precisely the
difference between a 200 and a 404.

`find` **cannot** promise you a todo. It searched a list; the list might not
have contained one. A signature that claimed otherwise would be a lie, and the
program would crash at the first `GET /todos/999` instead of answering it.

### Narrowing: how you get from the union to the todo

Rule the missing case out, and inside the `else` the type is just `Todo`:

```ts
const t = findTodo(1);
if (t === undefined) {
  console.log("not_found");     // module 10 makes this a real 404
} else {
  console.log(JSON.stringify(t));   // here `t` is a Todo. No error.
}
```

This is called **narrowing**, and it is the single most useful thing TypeScript
does. You did not cast, assert, or convince the compiler of anything — you wrote
an ordinary `if`, and the type inside each branch followed from it.

The shape above is worth memorising, because modules 10, 11 and 12 all open with
it:

```
find it  →  if it is missing, say so and stop  →  otherwise carry on with a Todo
```

### The escape hatch, and why not to take it

TypeScript offers `!` — the non-null assertion — which switches the error off:

```ts
const t = findTodo(1)!;         // "trust me, it's there"
console.log(t.title);
```

It compiles. It also crashes with `Cannot read properties of undefined` the
first time someone requests an id that does not exist, which on a server means a
500 for what should have been a 404. `!` does not check anything; it tells the
compiler to stop checking. Every time you write one you are betting that you
know the data better than the type says — and here, you demonstrably do not,
because the whole point is that the client chose the id.

### The same type, from somewhere you did not expect

This project is type-checked with `noUncheckedIndexedAccess` switched on, which
means indexing an array gives you the same union:

```ts
const first = todos[0];         // Todo | undefined, not Todo
```

Which is simply true: `todos` might be empty. Most TypeScript projects have this
flag off and let `todos[0]` claim to be a `Todo`, which is how "cannot read
properties of undefined" becomes the most common error in JavaScript. Here it is
on, so the first module that indexes an array is honest about it — and you
already know how to handle it, because it is the same `if` as above.
"""

_M3_SYNTAX = [
    _syn(
        "(t) => t.id === id",
        "An arrow function: a short function you pass to something else. The "
        "parameter is on the left, the value it produces on the right.",
        """
const isDone = (t: Todo) => t.done;
console.log(isDone({ id: 1, title: "x", done: true }));   // true
""",
        "With no braces, the body IS the return value. Add braces and you must "
        "write `return` yourself — `(t) => { t.id === id }` returns nothing at all, "
        "which is a silent and very common bug.",
    ),
    _syn(
        "todos.find((t) => t.id === id)",
        "Return the first element the test says yes to — or `undefined` if none "
        "of them do.",
        """
const match = todos.find((t) => t.id === 2);
""",
        "`find` gives you the element; `findIndex` gives you its position (module "
        "12); `filter` gives you all the matches as an array (module 17). Reaching "
        "for the wrong one is the usual cause of \"my todo is wrapped in an array\".",
    ),
    _syn(
        "Todo | undefined",
        "A union: this value is either a `Todo` or it is `undefined`. You cannot "
        "use it as a `Todo` until you have ruled the second case out.",
        """
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}
""",
        "Write the union in the return type even though TypeScript would infer it. "
        "It documents the one thing every caller has to deal with, right where "
        "they will look.",
    ),
    _syn(
        "if (t === undefined) { … } else { … }",
        "Narrowing. Rule out the missing case and, inside the `else`, the value's "
        "type is just `Todo`.",
        """
const t = findTodo(1);
if (t === undefined) {
  console.log("not_found");
} else {
  console.log(JSON.stringify(t));   // t is a Todo here
}
""",
        "Use `===`, not `==`. `t == undefined` is also true for `null`, which is a "
        "different absence with a different cause — and blurring the two is how you "
        "end up unable to tell \"missing\" from \"explicitly empty\".",
    ),
    _syn(
        "todos[0]",
        "Index into an array. Under this project's settings the result is "
        "`Todo | undefined`, because the array might be empty.",
        """
const first = todos[0];
if (first === undefined) {
  console.log("empty");
} else {
  console.log(first.title);
}
""",
        "Most TypeScript projects leave `noUncheckedIndexedAccess` off, so `todos[0]` "
        "claims to be a `Todo` even when the array is empty. That claim is where "
        "\"cannot read properties of undefined\" comes from.",
    ),
    _syn(
        "const todos: Todo[] = []; todos.push(todo);",
        "The store from module 2 — still the only thing holding data.",
        "",
        "",
        recap=True,
    ),
]

_M3_S1 = _pstep(
    "arrow", "Arrow functions, in one step",
    "You need a way to hand a test to `find`. This is it.",
    """
`find` has to be told what you are looking for, and the way you tell it is by
passing it a function. Writing that out longhand is noisy:

```ts
todos.find(function (t) { return t.id === id; });
```

so there is a shorter form for exactly this job:

```ts
todos.find((t) => t.id === id);
```

`(t) => t.id === id` reads as "given a `t`, produce `t.id === id`". The
parameter list is on the left of the `=>`, and the value it produces is on the
right. You do not write `return`, because there is nothing else it could mean.

You also do not annotate `t`. TypeScript already knows `todos` is a `Todo[]`, so
it knows what `find` will hand the callback — this is *contextual typing*, and
it is why callbacks in TypeScript are usually shorter than the code around them.
Hover over `t` in your editor and you will see `Todo`. Misspell `t.titel` and
you still get a compile error, which is the part that matters.

### The one trap

Braces change what the arrow means:

```ts
(t) => t.id === id        // returns the comparison
(t) => { t.id === id }    // returns NOTHING — the comparison is just computed and dropped
```

The second one compiles. `find` then gets `undefined` back for every element,
treats them all as non-matches, and returns `undefined` no matter what is in the
list. There is no error message; the search just never finds anything.

If you use braces, write the `return`:

```ts
(t) => { return t.id === id; }
```
""",
    """
In your `server.ts`, this prints `true` then `false`:

```ts
const isDone = (t: Todo) => t.done;
console.log(isDone({ id: 1, title: "a", done: true }));
console.log(isDone({ id: 2, title: "b", done: false }));
```

Then break it deliberately — change it to `(t: Todo) => { t.done }` — and watch
the compiler complain that a function returning `void` is not what was expected.
That error is the trap being caught for you; inside `find` it would not be.
""",
    pitfalls=[
        "`(t) => { t.id === id }` — braces without a `return`. The function returns nothing, `find` never matches, and there is no error to read.",
        "Annotating the parameter out of habit: `(t: Todo) => …` inside `todos.find(…)` is not wrong, just noise. TypeScript already knows what `find` hands you.",
        "Assuming the parameter is untyped because you did not type it. It is a `Todo`, and `t.titel` will still be caught.",
    ],
    warmup=[
        _pq("`const f = (t: Todo) => { t.done };` — what does `f(someTodo)` return?",
            ["`undefined`, because the braces make it a body with no `return`",
             "`true` or `false`, the value of `t.done`",
             "The todo itself",
             "It is a syntax error"],
            0,
            "With braces, the arrow takes a statement body — and a body with no "
            "`return` produces `undefined`. Without braces the expression IS the "
            "return value. This is the difference that makes a `find` silently never "
            "match."),
    ],
    exercises=[
        _pex("todo-m3-arrow-1", "Write the test",
             "Fill in the arrow function so it reports whether a todo is finished.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const isDone = (t: Todo) => t.done;

console.log(isDone({ id: 1, title: "Buy milk", done: true }));
console.log(isDone({ id: 2, title: "Write tests", done: false }));
"""),
             "(t: Todo) => t.done",
             [("", "true\nfalse")],
             ["The parameter goes on the left of the arrow, the answer on the right.",
              "No braces and no `return` — the expression is the return value.",
              "`(t: Todo) => t.done`"]),
        _pfix("todo-m3-arrow-fix1", "The braces that swallow the answer",
              "This program does not compile: the arrow has a brace body but never "
              "returns anything. Fix it, keeping it on one line.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const titleOf = (t: Todo) => { t.title };

console.log(titleOf({ id: 1, title: "Buy milk", done: false }));
"""),
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const titleOf = (t: Todo) => t.title;

console.log(titleOf({ id: 1, title: "Buy milk", done: false }));
"""),
              [("", "Buy milk")],
              ["A brace body needs an explicit `return` — or no braces at all.",
               "The shortest fix removes two characters.",
               "`const titleOf = (t: Todo) => t.title;`"],
              difficulty="Intro"),
    ],
)

_M3_S2 = _pstep(
    "find", "Look one up",
    "`find`, and the type it is honest enough to return.",
    """
Add the lookup to your store, next to `addTodo`:

```ts
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}
```

Write the return type out, even though TypeScript would infer it. `Todo |
undefined` is the one thing every caller of this function has to think about,
and the signature is where they will look.

### Why it cannot just return `Todo`

Because the list might not contain one. `findTodo(999)` has to produce
*something*, and there is no todo to produce. A function typed `(id: number) =>
Todo` would be claiming that every number identifies a todo, which is false the
first time a client makes up an id.

You could throw instead — and module 16 will discuss exactly that — but "the
client asked for a todo that does not exist" is not an exceptional condition. It
is an ordinary, expected outcome with its own status code. Returning `undefined`
models it as what it is.

### Using it

```ts
const found = findTodo(1);
if (found === undefined) {
  console.log("not_found");
} else {
  console.log(JSON.stringify(found));
}
```

Inside the `else`, `found` is a `Todo`. Not "a `Todo` you asserted", not "a
`Todo` if you are lucky" — the compiler has followed the `if` and narrowed the
type for you. Hover it and check.

Try, once, to skip the check:

```ts
const found = findTodo(1);
console.log(found.title);
//          ^ 'found' is possibly 'undefined'.
```

Read that error properly. It is not asking you to add a `!`. It is pointing out
that you have not decided what a missing todo means yet — and in module 10, the
answer to that question is a 404.
""",
    """
`node server.ts` prints one todo and one miss:

```
{"id":1,"title":"Buy milk","done":false}
not_found
```

And `console.log(findTodo(1).title)` — without the check — is refused before the
program runs, with "possibly 'undefined'". If it compiled, your return type says
`Todo` rather than `Todo | undefined`.
""",
    pitfalls=[
        "Declaring the return type as `Todo` because \"it will always be there\". It will not: the id comes from the client, and clients make ids up.",
        "Using `==` instead of `===`. `t == undefined` is also true for `null`, so you lose the ability to tell \"never existed\" from \"explicitly nothing\".",
        "Reaching for `find` when you want the position. `find` gives you the element — module 12 needs `findIndex` and the two are easy to swap by accident.",
    ],
    warmup=[
        _pq("`todos` holds ids 1 and 2. What does `todos.find((t) => t.id === 99)` "
            "return, and what is its type?",
            ["`undefined`, typed `Todo | undefined`",
             "`null`, typed `Todo | null`",
             "`undefined`, typed `undefined`",
             "It throws, because nothing matched"],
            0,
            "`find` returns `undefined` when nothing matches, and its declared return "
            "type is the union — the *type* does not change based on what happens to "
            "be in the array at runtime."),
    ],
    exercises=[
        _pex("todo-m3-find-1", "Search by id",
             "Fill in the call that finds the todo with the given id.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

addTodo("Buy milk");
addTodo("Write tests");

const found = findTodo(2);
if (found === undefined) {
  console.log("not_found");
} else {
  console.log(JSON.stringify(found));
}
"""),
             "todos.find((t) => t.id === id)",
             [("", '{"id":2,"title":"Write tests","done":false}')],
             ["The array method that returns the first match is `find`.",
              "It takes an arrow function comparing each todo's id to the one asked for.",
              "`return todos.find((t) => t.id === id);`"]),
        _pex("todo-m3-find-2", "Be honest about the return type",
             "`findTodo` can fail to find anything, but its signature does not say so. "
             "Fix the return type.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

addTodo("Buy milk");

const missing = findTodo(99);
if (missing === undefined) {
  console.log("not_found");
} else {
  console.log(JSON.stringify(missing));
}
"""),
             ": Todo | undefined",
             [("", "not_found")],
             ["`find` returns the element or nothing at all.",
              "The type is a union of the two possibilities, written with `|`.",
              "`function findTodo(id: number): Todo | undefined {`"]),
    ],
    quiz=[
        _pq("Why model \"no todo with that id\" as a returned `undefined` rather than a "
            "thrown error?",
            ["It is an ordinary, expected outcome with its own status code — not an exceptional one",
             "Throwing is slower in Node",
             "TypeScript cannot type thrown values",
             "`find` is unable to throw"],
            0,
            "A client asking for id 999 is normal traffic, and the correct answer is "
            "a 404. Exceptions are for the cases you did not plan for — module 16 "
            "builds the boundary that catches those."),
    ],
)

_M3_S3 = _pstep(
    "narrow", "Narrowing, and the `!` you must not write",
    "How an ordinary `if` changes a type, and what the shortcut costs.",
    """
The `if` you wrote in the last step did something worth naming:

```ts
const t = findTodo(1);        // t: Todo | undefined
if (t === undefined) {
  return;                     // t: undefined  (in here)
}
// t: Todo   (out here — the compiler followed the if)
console.log(t.title);
```

This is **narrowing**. You wrote no types and no casts; you wrote a normal
comparison, and TypeScript worked out that below the `if` the only remaining
possibility is `Todo`. Everything the rest of this project does with unions —
the error type in module 15, the validation result in module 14 — is this same
mechanism.

Both shapes are fine. Use whichever reads better:

```ts
// early return: the failure case leaves, the happy path is un-indented
if (t === undefined) { console.log("not_found"); return; }
console.log(JSON.stringify(t));

// if/else: both cases visible side by side
if (t === undefined) { console.log("not_found"); }
else { console.log(JSON.stringify(t)); }
```

The early return is the one you will want inside a request handler, because by
module 14 there are four failure cases before the happy path and nesting them
would be unreadable.

### `!` — the non-null assertion

TypeScript will let you silence the error instead:

```ts
const t = findTodo(999)!;     // "trust me"
console.log(t.title);         // TypeError: Cannot read properties of undefined
```

The `!` removes `undefined` from the type. It does not check anything, it does
not generate any code, and it is *wrong here* in a specific and expensive way:
the id came from the client. You do not know it is valid, so you cannot promise
it is.

What it costs at runtime: an uncaught `TypeError`, which module 16's boundary
will turn into a **500 Internal Server Error** — the status code that means "my
server is broken". The correct answer was a **404**, which means "you asked for
something that isn't here". A `!` in this position converts the client's mistake
into your outage.

There are legitimate uses for `!` — when you have just checked something the
compiler cannot see. This is not one, and neither is anything else in this
project.
""",
    """
Both branches work in your own file: `findTodo(1)` prints the todo,
`findTodo(99)` prints `not_found`, and neither crashes.

Then run the experiment: write `const t = findTodo(99)!;` followed by
`console.log(t.title);`. It compiles — and the program dies with `TypeError:
Cannot read properties of undefined (reading 'title')`. Seeing that crash come
out of code the compiler accepted is the point of the step. Delete it.
""",
    pitfalls=[
        "Reaching for `!` to make an error go away. It is the compiler asking a real question — \"what happens when this is missing?\" — and `!` answers \"crash\".",
        "Narrowing with `if (t)` instead of `if (t === undefined)`. It works for todos, but it also treats `0` and `\"\"` as absent — which becomes a genuine bug the moment you narrow a number or a string.",
        "Checking, and then using the value in a callback defined earlier. Narrowing follows the flow of the code; it does not travel backwards.",
    ],
    exercises=[
        _pex("todo-m3-narrow-1", "Rule out the missing case",
             "The program will not compile — `found` might be `undefined`. Add the check "
             "that narrows it.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

addTodo("Buy milk");

const found = findTodo(1);
if (found === undefined) {
  console.log("not_found");
} else {
  console.log(found.title);
}
"""),
             "if (found === undefined) {",
             [("", "Buy milk")],
             ["Compare against the value `find` returns when it matches nothing.",
              "Use `===`, not `==`.",
              "`if (found === undefined) {`"]),
        _pfix("todo-m3-narrow-fix1", "The assertion that becomes a 500",
              "This program compiles and then crashes. It asserts a todo is there with "
              "`!` instead of checking. Replace the assertion with a real check that "
              "prints `not_found` when the todo is missing.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

addTodo("Buy milk");

const found = findTodo(99)!;
console.log(JSON.stringify(found));
"""),
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

addTodo("Buy milk");

const found = findTodo(99);
if (found === undefined) {
  console.log("not_found");
} else {
  console.log(JSON.stringify(found));
}
"""),
              [("", "not_found")],
              ["The `!` is doing the damage — it removes `undefined` from the type "
               "without checking anything.",
               "Drop the `!`, then handle both cases with an `if`/`else`.",
               "`const found = findTodo(99);` then `if (found === undefined) { "
               "console.log(\"not_found\"); } else { … }`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("A handler does `const t = findTodo(id)!` and the client requests an id "
            "that does not exist. What does the client get, once module 16's error "
            "boundary is in place?",
            ["500 — the assertion crashed, and a crash is a server error",
             "404 — the boundary works out that the todo was missing",
             "200 with an empty body",
             "400 — the id was invalid"],
            0,
            "`!` produces a `TypeError` at runtime, the boundary catches it and "
            "answers 500. The client's perfectly reasonable request for a missing "
            "todo has been reported as your server being broken."),
    ],
)

_M3_S4 = _pstep(
    "indexed", "The same union, from an array index",
    "Why `todos[0]` is not a `Todo` here — and why that is correct.",
    """
One more place the union shows up, and it surprises people who have written
TypeScript before:

```ts
const first = todos[0];       // Todo | undefined
console.log(first.title);
//          ^ 'first' is possibly 'undefined'.
```

Index 0 of an array is not guaranteed to exist, because the array might be
empty. That is plainly true, and yet most TypeScript projects are configured to
let `todos[0]` claim to be a `Todo` anyway. The compiler flag that governs it is
`noUncheckedIndexedAccess`, it is **on** for everything in this track, and the
difference is worth understanding now rather than in module 10.

With it off, this compiles and crashes:

```ts
const first = todos[0];       // claims: Todo
console.log(first.title);     // reality: TypeError on an empty list
```

With it on, you handle it — with exactly the same `if` you already know:

```ts
const first = todos[0];
if (first === undefined) {
  console.log("empty");
} else {
  console.log(first.title);
}
```

### Why this track turns it on

Module 10 has to pull an id out of a URL path:

```ts
const parts = "/todos/7".split("/");    // ["", "todos", "7"]
const raw = parts[2];                   // string | undefined
```

`/todos/7` has a third segment. `/todos` does not, and a client can send either
to the same handler. Under the loose setting, `parts[2]` claims to be a `string`
and the code that follows quietly does the wrong thing with `undefined`; under
this one, you are asked the question while you are writing the line.

This is not ceremony. It is the single most common crash in JavaScript, made
visible at compile time — and it is the bug this whole track is trying to teach
you not to write.
""",
    """
In your own file, with the store empty at that point:

```ts
const first = todos[0];
if (first === undefined) { console.log("empty"); }
else { console.log(first.title); }
```

prints `empty` and does not crash. Then remove the check and confirm the
compiler refuses it with "possibly 'undefined'".
""",
    pitfalls=[
        "`todos[0]!` — the same mistake as the last step, in a new costume. If the list can be empty, say so.",
        "Assuming the flag is on everywhere. In most codebases it is off, and `arr[i]` lies to you. Knowing that it *can* lie is the transferable part.",
        "Checking `todos.length > 0` and expecting `todos[0]` to narrow. It does not — the compiler does not connect the length to the index. Bind the element and check that.",
    ],
    warmup=[
        _pq("Under `noUncheckedIndexedAccess`, what is the type of `parts[2]` where "
            "`parts` is a `string[]`?",
            ["`string | undefined`", "`string`", "`undefined`", "`any`"],
            0,
            "Indexing cannot promise the element is there, so the union includes "
            "`undefined`. This is the flag that makes module 10's URL parsing honest "
            "about `/todos` having no third segment."),
    ],
    exercises=[
        _pex("todo-m3-idx-1", "The first todo might not exist",
             "The store is empty when this runs. Add the check that makes the program "
             "compile and print `empty`.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];

const first = todos[0];
if (first === undefined) {
  console.log("empty");
} else {
  console.log(first.title);
}
"""),
             "if (first === undefined) {",
             [("", "empty")],
             ["Indexing an array cannot promise an element is there.",
              "Handle it the same way you handled a `find` that missed.",
              "`if (first === undefined) {`"]),
    ],
    quiz=[
        _pq("Why does this track enable `noUncheckedIndexedAccess`, when most projects "
            "leave it off?",
            ["Because a client can request `/todos` or `/todos/7` at the same handler, so a path segment really can be absent",
             "Because it makes the compiler faster",
             "Because arrays are immutable under it",
             "Because it is required to use `find`"],
            0,
            "Module 10 splits a path and reads segment 2. For `/todos` there is no "
            "segment 2. The flag turns that from a runtime crash into a question you "
            "answer while writing the line."),
    ],
)

_M3_FINAL = _pch(
    "todo-m3-build", "Module 3 build — lookup", "Easy",
    "Put the module together. Write `findTodo(id)` returning `Todo | undefined`, "
    "and a `report(id)` that prints the todo as JSON when it exists and the single "
    "word `not_found` when it does not.\n\n"
    "`report` must take the id and print — it returns nothing. Everything below "
    "the blank is already written for you.",
    _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function report(id: number): void {
  const found = findTodo(id);
  if (found === undefined) {
    console.log("not_found");
    return;
  }
  console.log(JSON.stringify(found));
}

addTodo("Buy milk");
addTodo("Write tests");
addTodo("Ship it");

report(1);
report(3);
report(99);
report(0);
"""),
    """function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function report(id: number): void {
  const found = findTodo(id);
  if (found === undefined) {
    console.log("not_found");
    return;
  }
  console.log(JSON.stringify(found));
}""",
    [("", '{"id":1,"title":"Buy milk","done":false}\n'
          '{"id":3,"title":"Ship it","done":false}\n'
          "not_found\n"
          "not_found")],
    ["Two functions go in the blank: `findTodo` and `report`.",
     "`findTodo` returns `Todo | undefined` — write the union out.",
     "`report` returns `void`. Find, check for `undefined`, print `not_found` and "
     "return early; otherwise print the JSON.",
     "No `!` anywhere. If you needed one, the check is missing."],
)

_TODO_MODULES.append(_pmod(
    key="todo-lookup", number=3, phase="model",
    title="Finding one, and the `undefined` you must handle",
    what="find, unions, narrowing — the ancestor of every 404 in this project",
    goal="Look a todo up by id and be honest in the type system about it not being there.",
    why=_M3_WHY,
    est_minutes=45,
    builds_on=["todo-shape", "todo-store"],
    concepts=["arrow functions", "Array.find", "union types", "narrowing",
              "noUncheckedIndexedAccess"],
    objectives=[
        "Write an arrow function, and say what braces around its body change",
        "Use `find` and explain why it cannot promise to return an element",
        "Read and write the union type `Todo | undefined`",
        "Narrow a union with an ordinary `if`, both early-return and if/else",
        "Say precisely what a `!` costs at runtime, in status codes",
        "Explain why `todos[0]` is `Todo | undefined` in this project, and why that is right",
    ],
    deliverable="A `findTodo(id)` the rest of the project builds on, and the "
                "narrowing pattern every 404 in modules 10-12 is made of.",
    brief=_M3_BRIEF,
    syntax=_M3_SYNTAX,
    steps=[_M3_S1, _M3_S2, _M3_S3, _M3_S4],
    final_build=_M3_FINAL,
    acceptance=[
        "`findTodo` is declared as returning `Todo | undefined`, not `Todo`.",
        "Looking up an id that exists prints the todo; one that does not prints `not_found`.",
        "There is no `!` anywhere in your file.",
        "`console.log(findTodo(1).title)` without a check is refused before the program runs.",
        "You can say which status code a `!` in this position would produce, and which one was correct.",
    ],
    reference="""// server.ts — module 3
//
// Every "not found" in this project starts here. findTodo returns a union
// because the id comes from the client, and clients make ids up.

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

// `Todo | undefined`, written out even though it would be inferred: it is the
// one thing every caller has to deal with, and this is where they will look.
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

// The shape modules 10, 11 and 12 all open with:
//   find it -> if missing, say so and stop -> otherwise carry on with a Todo.
// The early return is what keeps the happy path un-indented once there are
// four failure cases in front of it (module 14).
function report(id: number): void {
  const found = findTodo(id);
  if (found === undefined) {
    console.log("not_found");        // becomes a real 404 in module 10
    return;
  }
  console.log(JSON.stringify(found));  // `found` is a Todo here — narrowed
}

addTodo("Buy milk");
addTodo("Write tests");
addTodo("Ship it");

report(1);
report(3);
report(99);
report(0);
""",
    stretch=[
        "Write `findIndexTodo(id): number` returning `-1` when nothing matches, and compare how it feels against the union. Module 12 needs it and has to deal with `-1` being a perfectly valid-looking number.",
        "Try `if (found)` instead of `if (found === undefined)`. It works here — now write the same check for a value of type `number | undefined` where `0` is legitimate, and watch it break.",
        "Turn `noUncheckedIndexedAccess` off in your own tsconfig and see how much of module 3 stops being necessary. Then turn it back on and consider which version you would rather debug.",
    ],
    glossary=[
        _pgloss("arrow function", "`(x) => y` — a short function literal. Without braces the body is the return value."),
        _pgloss("contextual typing", "TypeScript inferring a callback's parameter types from where the callback is passed. Why `(t) => t.id` needs no annotation inside `todos.find`."),
        _pgloss("union type", "`A | B` — a value that is one of several types. You must rule out the others before using it as one of them."),
        _pgloss("narrowing", "Using ordinary control flow (`if`, `===`, `return`) to reduce a union to one of its members. TypeScript's most useful trick."),
        _pgloss("non-null assertion", "The `!` suffix. Removes `null`/`undefined` from a type without checking anything — a promise, not a test."),
        _pgloss("noUncheckedIndexedAccess", "The compiler flag that makes `arr[i]` return `T | undefined`. On throughout this track."),
    ],
    cheatsheet="""
```ts
// Arrow function — no braces means the expression IS the return value
const isDone = (t: Todo) => t.done;
const isDone2 = (t: Todo) => { return t.done; };   // braces need `return`

// Find one, honestly
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

// Narrow it — early return (preferred inside handlers)
const t = findTodo(id);
if (t === undefined) { console.log("not_found"); return; }
console.log(JSON.stringify(t));       // t is a Todo here

// Narrow it — if/else
if (t === undefined) { … } else { … }

// Array indexing gives the same union in this project
const first = todos[0];               // Todo | undefined
```

| Situation | Do | Never |
|---|---|---|
| `find` might miss | return `Todo \\| undefined` | return `Todo` |
| Using the result | `if (x === undefined) return;` | `findTodo(id)!` |
| Comparing | `=== undefined` | `== undefined` (also matches `null`) |
| First element | bind it, then check | `todos[0]!` |
| Want the position | `findIndex` (module 12) | `find` |

**What `!` costs:** a `TypeError`, caught by module 16's boundary, answered as
**500**. The correct answer was **404**.
""",
    self_check=[
        "Can you write `findTodo` from memory, return type included?",
        "Can you explain why `(t) => { t.id === id }` makes `find` never match, and why nothing warns you?",
        "Can you describe narrowing without using the words \"cast\" or \"assert\"?",
        "Can you name the status code a stray `!` produces, and the one that was correct?",
        "Can you say why `todos[0]` is `Todo | undefined` here, and give the module-10 example that makes it worth it?",
    ],
    review=[
        _pq("Why is `findTodo`'s return type `Todo | undefined` rather than `Todo`?",
            ["The id comes from the client, so there may be no such todo",
             "`find` is asynchronous and may not have finished",
             "TypeScript cannot infer object types from arrays",
             "So that callers can pass `undefined` in"],
            0,
            "The list might not contain a match, and the caller has to decide what "
            "that means. Returning `Todo` would be a claim that every number "
            "identifies a todo — false the first time a client invents an id."),
        _pq("Which of these compiles AND crashes at runtime?",
            ["`const t = findTodo(99)!; console.log(t.title);",
             "`const t = findTodo(99); console.log(t.title);`",
             "`const t = findTodo(99); if (t === undefined) return; console.log(t.title);`",
             "`const t = findTodo(99); console.log(JSON.stringify(t));`"],
            0,
            "The `!` removes `undefined` from the type without checking, so the "
            "compiler is satisfied and the property access fails at runtime. The "
            "second is caught at compile time; the third narrows properly; the "
            "fourth is fine because `JSON.stringify(undefined)` is legal."),
        _pq("`for (const t of todos)` walks the todos. What does `todos[0]` give you "
            "under this project's compiler settings?",
            ["`Todo | undefined`, because the array might be empty",
             "`Todo`, because the array is typed `Todo[]`",
             "`undefined`, until something is pushed",
             "`never`, because the array was declared empty"],
            0,
            "`noUncheckedIndexedAccess` makes every index access return the union. "
            "The array's declared element type says what is in it *if* something is "
            "there — not that anything is."),
    ],
    milestone="You can find a todo, and you have handled the case where there "
              "isn't one. That `if` is the 404 in modules 10, 11 and 12 — you have "
              "already written it, before there was any HTTP to write it in.",
))
