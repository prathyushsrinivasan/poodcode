# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 2 — The store.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES: `Todo[]`, `.push(`, `.length`, `for (const … of …)`, and a mutable
# module-level `let`. Still no `.find` and no `undefined` (module 3), no arrow
# functions (module 3), no object spread (module 11).
#
# THE ARGUMENT THIS MODULE EXISTS TO MAKE: ids come from a counter, not from
# `todos.length + 1`. Every beginner writes the second one, it works perfectly
# until module 12 adds DELETE, and then two todos share an id. Teaching it here
# — with the collision demonstrated as a runnable program, not asserted in prose
# — is much cheaper than debugging it ten modules later.
#
# Programs are stdin-free for the reason given in module 1's header.
# ---------------------------------------------------------------------------

_M2_WHY = (
    "Module 1 can make a todo but cannot remember one. A `makeTodo` call that "
    "nobody keeps is a value that exists for a microsecond and is collected — "
    "and an API whose todos vanish between requests is not an API. Before "
    "anything can be served, something has to hold the list and hand out ids "
    "that stay unique for the life of the process."
)

_M2_BRIEF = """
### The whole module in one line

Give the todos somewhere to live, and give each one an id nobody else will ever
get.

### What a "store" is, and what it is not

A store is the one place that owns the data. Everything else asks it. Right now
that is an array and a counter sitting at the top of your file:

```ts
const todos: Todo[] = [];
let nextId = 1;
```

Two lines, and they are already making a design decision worth naming: **the
data lives in the process**. Stop the server and the todos are gone. That is
fine for now and it is fixed in module 19, when persistence arrives — and
because everything goes through one small set of functions, module 19 will
change those functions and nothing else. That is the whole reason to have a
store rather than reaching into the array from every route.

### `const todos` but `let nextId` — why the difference?

This trips people up, and the answer is precise:

- `const` means the *binding* never changes — `todos` will always point at that
  same array. It says nothing about the array's contents, so `todos.push(…)` is
  perfectly legal. You are changing what is in the box, not which box.
- `nextId` genuinely has to be rebound: `1` becomes `2`. There is no way to do
  that to a `const`, so it is a `let`.

The rule that falls out: use `const` unless you have to reassign, and adding to
an array is not reassigning.

### The counter, and the bug it exists to prevent

The obvious way to allocate an id is `todos.length + 1`. It is shorter, it needs
no extra variable, and it produces 1, 2, 3 exactly like the counter does. It is
also wrong, and the failure is not subtle:

```
add "a"        → id 1,  list = [1]
add "b"        → id 2,  list = [1, 2]
delete id 1    →        list = [2]        length is now 1
add "c"        → id 2   ← collision. Two todos with id 2.
```

`GET /todos/2` now has two possible answers, `DELETE /todos/2` removes an
arbitrary one, and the bug reaches you as "sometimes the wrong todo disappears",
which is a miserable thing to debug.

A counter that only ever goes up cannot do this. Ids are **not** positions in a
list, and the moment you allow deletion, treating them as positions breaks. The
counter costs one `let`.

> **In production this is a UUID.** Real services use `crypto.randomUUID()`, or
> a database sequence, because a counter resets when the process restarts and
> collides across two machines. This track uses `1, 2, 3` for one reason: a test
> can only assert an exact response if the ids are predictable. Wherever that
> choice matters, the module says so.
"""

_M2_SYNTAX = [
    _syn(
        "const todos: Todo[] = [];",
        "An array whose every element must be a `Todo`. Starts empty.",
        """
const todos: Todo[] = [];
""",
        "The annotation matters on an empty array. Without it TypeScript infers "
        "`never[]` — an array nothing can ever be put into — and the first `push` "
        "fails with an error that reads like nonsense.",
    ),
    _syn(
        "todos.push(todo)",
        "Add one element to the end of an array.",
        """
const todos: Todo[] = [];
todos.push({ id: 1, title: "Buy milk", done: false });
console.log(todos.length);
""",
        "`push` returns the array's **new length**, not the array and not the item. "
        "`return todos.push(t)` gives you a number, which is a surprising thing to "
        "find in a response body.",
    ),
    _syn(
        "todos.length",
        "How many elements the array holds.",
        """
const todos: Todo[] = [];
todos.push({ id: 1, title: "Buy milk", done: false });
console.log(todos.length);   // 1
""",
        "It is a property, not a method — `todos.length`, never `todos.length()`.",
    ),
    _syn(
        "let nextId = 1;",
        "A variable you intend to reassign. `let` rebinds; `const` does not.",
        """
let nextId = 1;
nextId = nextId + 1;
console.log(nextId);   // 2
""",
        "`const` on an array still lets you `push` — it freezes the binding, not "
        "the contents. So `const todos` next to `let nextId` is not an "
        "inconsistency, it is the rule applied twice.",
    ),
    _syn(
        "for (const t of todos) { … }",
        "Visit every element of an array in order.",
        """
for (const t of todos) {
  console.log(JSON.stringify(t));
}
""",
        "`of` walks the *values*; `in` walks the *keys* and hands you `\"0\"`, "
        "`\"1\"` as strings. `for (const t in todos)` compiles and gives you "
        "nonsense — one of the few places TypeScript will not save you.",
    ),
    _syn(
        "todos.shift()",
        "Remove the first element and return it. Used here only to demonstrate "
        "the id collision in step 3 — deleting a todo *by id* is module 12's job.",
        """
const todos: Todo[] = [];
todos.push({ id: 1, title: "Buy milk", done: false });
todos.shift();
console.log(todos.length);   // 0
""",
        "It shifts every remaining element down one position, so every index after "
        "the first changes. That is the whole reason an id must not be a position "
        "— which is what step 3 is about.",
    ),
    _syn(
        "JSON.stringify(todos)",
        "An array stringifies to a JSON array — the whole list as one response body.",
        """
console.log(JSON.stringify(todos));
// [{"id":1,"title":"Buy milk","done":false}]
""",
        "No spaces, no trailing comma. An empty array is `[]`, which is a "
        "perfectly good 200 response and not a 404.",
        recap=True,
    ),
    _syn(
        "type Todo = { id: number; title: string; done: boolean };",
        "The shape from module 1, still the centre of everything.",
        "",
        "",
        recap=True,
    ),
]

_M2_S1 = _pstep(
    "state", "Give the todos somewhere to live",
    "Two lines of module-level state, and the `const`/`let` decision behind them.",
    """
At the top of `server.ts`, under the `Todo` type, add the store:

```ts
const todos: Todo[] = [];
let nextId = 1;
```

Do not skip the annotation on the empty array. Try it without and read what
happens:

```ts
const todos = [];        // inferred as never[]
todos.push(makeTodo(1, "Buy milk"));
//    ^ Argument of type 'Todo' is not assignable to parameter of type 'never'
```

TypeScript had nothing to infer from — an empty array literal gives it no
element to look at — so it picked `never[]`, the array that can hold nothing.
The error is confusing the first time and obvious the second: you never told it
what the array is for.

### Where these two lines go

Top level of the file, outside every function. That makes them *module state* —
one array and one counter for the whole process, shared by every request that
will eventually arrive. That is exactly what you want, and it is also exactly
why module 19 is going to be able to swap it for a file without touching a
single route.
""",
    """
`node server.ts` still runs and prints module 1's three todos. You have added
two lines and changed no behaviour yet.

Then check the annotation is doing something: temporarily change `Todo[]` to
`string[]` and confirm the file refuses to compile once you start pushing todos
into it. Change it back.
""",
    pitfalls=[
        "`const todos = []` with no annotation. TypeScript infers `never[]` and the first push fails with a message about `never` that reads like a compiler bug. It is not — you never said what the array holds.",
        "Declaring the array inside a function. It is then rebuilt empty on every call, which is the single most common version of \"my data keeps disappearing\".",
        "Reaching for `let todos` out of habit. You never reassign the array, only add to it — `const` is correct and says so.",
    ],
    warmup=[
        _pq("`const todos: Todo[] = []; todos.push(t);` — why does this compile, when "
            "`todos` is `const`?",
            ["`const` freezes the binding, not the array's contents",
             "`push` is specially exempted from `const`",
             "It does not compile — you need `let`",
             "Arrays are copied on push, so the original is untouched"],
            0,
            "`const` promises that `todos` will always name that same array. It "
            "promises nothing about what is inside it. Reassigning — `todos = []` — "
            "is the thing that fails."),
    ],
    exercises=[
        _pex("todo-m2-state-1", "Type the empty array",
             "The array is declared but TypeScript does not know what goes in it, so the "
             "push below is refused. Annotate it.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
todos.push({ id: 1, title: "Buy milk", done: false });

console.log(todos.length);
console.log(JSON.stringify(todos));
"""),
             ": Todo[]",
             [("", '1\n[{"id":1,"title":"Buy milk","done":false}]')],
             ["An empty literal gives the compiler nothing to infer from — tell it.",
              "The annotation is the element type followed by square brackets.",
              "`const todos: Todo[] = [];`"]),
    ],
    quiz=[
        _pq("You write `const todos = [];` and the first `todos.push(myTodo)` fails with "
            "\"not assignable to parameter of type 'never'\". What is wrong?",
            ["The empty literal was inferred as `never[]` because nothing said what it holds",
             "`myTodo` is missing a required field",
             "`push` cannot be used on a `const` array",
             "`never` means the array is full"],
            0,
            "With no annotation and no elements, there is nothing for inference to "
            "work from, so the array's element type is `never` — the type with no "
            "values. Annotate it `Todo[]` and the message disappears."),
    ],
)

_M2_S2 = _pstep(
    "add", "One function that adds a todo",
    "Allocate an id, build the todo, keep it — in that order, in one place.",
    """
Replace module 1's `makeTodo` with a function that also *keeps* what it makes:

```ts
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}
```

Read the body in order, because each line is a decision.

**`id: nextId`** — the current value of the counter becomes this todo's id.

**`nextId = nextId + 1`** — and then the counter moves on, so nobody else can
get that id. (`nextId++` does the same thing and is what you would normally
write; it is spelled out here so the two steps stay visible.)

**`todos.push(todo)`** — the store keeps it. Miss this line and the function
still compiles, still returns a perfectly good todo, and the list stays empty
forever. It is a genuinely easy line to forget.

**`return todo`** — hand back what was created. `POST /todos` will send this
straight to the client in module 9, which is why the function returns the todo
rather than nothing.

### Why not `return todos.push(todo)`

Because `push` returns the array's new *length* — a number. The function's
declared return type is `Todo`, so this one is caught at compile time. That is
the return type from module 1 earning its keep.

Now use it:

```ts
addTodo("Buy milk");
addTodo("Write tests");
console.log(JSON.stringify(todos));
```
""",
    """
`node server.ts` prints:

```
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```

One array, two todos, ids 1 and 2, and no spaces anywhere. If your list is empty
you forgot the `push`; if both ids are 1 you forgot to advance the counter.
""",
    pitfalls=[
        "Forgetting `todos.push(todo)`. The function compiles, returns the right value, and the list never fills up. Nothing warns you — the type system cannot see that you meant to keep it.",
        "Advancing the counter *before* using it, so the first todo gets id 2. Read the two lines in order: use it, then advance it.",
        "`return todos.push(todo)`. That is a number. The declared return type catches it — which is the argument for declaring return types, made concrete.",
    ],
    exercises=[
        _pex("todo-m2-add-1", "Keep what you made",
             "`addTodo` builds the todo and returns it, but the list stays empty. Add the "
             "line that keeps it.",
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

addTodo("Buy milk");
addTodo("Write tests");
console.log(todos.length);
console.log(JSON.stringify(todos));
"""),
             "  todos.push(todo);",
             [("", '2\n[{"id":1,"title":"Buy milk","done":false},'
                   '{"id":2,"title":"Write tests","done":false}]')],
             ["The todo is built and returned, but nothing ever adds it to the array.",
              "The array method that appends one element is `push`.",
              "`  todos.push(todo);`"]),
        _pex("todo-m2-add-2", "Move the counter on",
             "Both todos are coming out with id 1. Advance the counter after using it.",
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

addTodo("Buy milk");
addTodo("Write tests");
addTodo("Ship it");
console.log(JSON.stringify(todos));
"""),
             "  nextId = nextId + 1;",
             [("", '[{"id":1,"title":"Buy milk","done":false},'
                   '{"id":2,"title":"Write tests","done":false},'
                   '{"id":3,"title":"Ship it","done":false}]')],
             ["The id is read from `nextId`, but nothing ever changes `nextId`.",
              "Add one to it, after the todo has taken its value.",
              "`  nextId = nextId + 1;`"]),
        _pfix("todo-m2-add-fix1", "The first todo gets id 2",
              "The counter is advanced in the wrong place, so ids start at 2. Fix it so "
              "the first todo gets id 1.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  nextId = nextId + 1;
  const todo: Todo = { id: nextId, title: title, done: false };
  todos.push(todo);
  return todo;
}

addTodo("Buy milk");
addTodo("Write tests");
console.log(JSON.stringify(todos));
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

addTodo("Buy milk");
addTodo("Write tests");
console.log(JSON.stringify(todos));
"""),
              [("", '[{"id":1,"title":"Buy milk","done":false},'
                    '{"id":2,"title":"Write tests","done":false}]')],
              ["The counter starts at 1, so the first todo should get 1.",
               "Look at the order of the first two lines in the function body.",
               "Build the todo first, then advance the counter."]),
    ],
    quiz=[
        _pq("Why does `addTodo` return the todo rather than returning nothing?",
            ["`POST /todos` has to send the created todo — including the id the client did not supply — straight back",
             "TypeScript requires every function to return a value",
             "So the caller can push it into the array itself",
             "It does not matter; returning `void` would be equally good"],
            0,
            "Look at the contract: `POST /todos` responds `201` with the full todo. "
            "The id was invented by the server, so the client has no other way to "
            "learn it. Module 9 sends exactly this return value."),
    ],
)

_M2_S3 = _pstep(
    "counter", "Why the counter is not `todos.length`",
    "The shortcut everybody takes, and the collision it produces.",
    """
`nextId` looks like a variable you could delete. The list knows how long it is,
so why not:

```ts
const todo: Todo = { id: todos.length + 1, title: title, done: false };
```

It produces 1, 2, 3 exactly like the counter. Every test you have written so far
would still pass. And it is a bug — it is just a bug you cannot see yet, because
nothing deletes.

Work it through on paper before you read on:

```
add "a"       → length 0 → id 1 → list [1]
add "b"       → length 1 → id 2 → list [1, 2]
delete id 1   →                   list [2]
add "c"       → length 1 → id 2 → list [2, 2]    ← two todos with id 2
```

Now `GET /todos/2` has two valid answers, `PATCH /todos/2` updates whichever one
`find` reaches first, and `DELETE /todos/2` removes one and leaves the other.
The symptom that reaches you is "sometimes it edits the wrong todo", which is
about as unpleasant as bugs get, because it is invisible until there has been a
deletion *and* a subsequent creation.

### The rule underneath

**An id is not a position.** A position is a fact about the list right now; an
id is a promise that survives everything the list does afterwards. The moment
anything can be removed, a position stops being able to keep that promise.

A counter that only ever goes up keeps it, and costs one `let`.

### Try it

Before moving on, prove the collision to yourself. Add this temporarily, using
the length-based id:

```ts
addTodo("a");
addTodo("b");
todos.shift();      // module 12 does this properly — this is just a demo
addTodo("c");
console.log(JSON.stringify(todos));
```

Watch two todos come out with the same id. Then put the counter back.
""",
    """
You can state, without looking, the exact sequence of operations that makes
`todos.length + 1` produce a duplicate id — and your `server.ts` uses the
counter.

If you ran the demo, you saw `[{"id":2,…},{"id":2,…}]` with your own eyes. That
is worth thirty seconds; it is the difference between knowing the rule and
believing it.
""",
    pitfalls=[
        "\"I'll switch to a counter when I add DELETE.\" You will not — by module 12 this line is eight modules old and looks correct. Fix it while you are looking at it.",
        "Reusing an id after a delete \"to keep them tidy\". Ids are not meant to be tidy; they are meant to be unique forever. A client that cached id 2 must never get a different todo back.",
        "Assuming the counter is safe in production. It resets on restart and collides across two processes — which is what `crypto.randomUUID()` and database sequences exist for. It is deterministic, which is why this track uses it.",
    ],
    warmup=[
        _pq("Using `id: todos.length + 1`, you add two todos, delete the first, then "
            "add a third. What ids exist?",
            ["2 and 2", "1 and 3", "2 and 3", "1 and 2"],
            0,
            "After the delete the list holds one todo (id 2), so `length + 1` is 2 "
            "again and the new todo also gets id 2. Two todos, one id — and every "
            "lookup from then on is ambiguous."),
    ],
    exercises=[
        _pfix("todo-m2-counter-fix1", "Ids are positions, and they collide",
              "This program allocates ids from the list's length. It deletes a todo part "
              "way through — and the output has a duplicate id. Switch it to a counter "
              "that only goes up.\n\n"
              "Leave the `shift` line alone; it stands in for the DELETE you build in "
              "module 12.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: todos.length + 1, title: title, done: false };
  todos.push(todo);
  return todo;
}

addTodo("Buy milk");
addTodo("Write tests");
todos.shift();
addTodo("Ship it");

console.log(JSON.stringify(todos));
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

addTodo("Buy milk");
addTodo("Write tests");
todos.shift();
addTodo("Ship it");

console.log(JSON.stringify(todos));
"""),
              [("", '[{"id":2,"title":"Write tests","done":false},'
                    '{"id":3,"title":"Ship it","done":false}]')],
              ["`nextId` is already declared and never used. That is the clue.",
               "Take the id from `nextId`, then advance it — the length of the list "
               "has nothing to do with it.",
               "`const todo: Todo = { id: nextId, title: title, done: false };` "
               "followed by `nextId = nextId + 1;`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("What is the general rule that `todos.length + 1` violates?",
            ["An id must stay unique for the life of the data; a position is only a fact about the list right now",
             "Array lengths are expensive to compute",
             "Ids must always start from zero",
             "`length` can be fractional, so the id might not be an integer"],
            0,
            "Positions shift whenever the list changes. An id is a promise to a "
            "client that outlives every one of those changes, so it cannot be "
            "derived from something that shifts."),
    ],
)

_M2_S4 = _pstep(
    "list", "Read the list back",
    "`for … of`, and the whole array as one response body.",
    """
Two ways to look at the store, and you want both.

**One at a time**, for anything that has to look at each todo:

```ts
for (const t of todos) {
  console.log(JSON.stringify(t));
}
```

`for … of` walks the *values*. Its evil twin, `for … in`, walks the *keys* and
hands you the strings `"0"`, `"1"`, `"2"` — it compiles, it runs, and every
`t.title` is then a type error or worse. If a loop over an array is behaving
strangely, check which one you wrote.

**All at once**, which is what `GET /todos` actually sends:

```ts
console.log(JSON.stringify(todos));
```

```
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```

An array stringifies to a JSON array. That is the entire body of `GET /todos`
until module 18 wraps it in an envelope.

### An empty list is a success

Worth saying now because it comes up in module 7: if there are no todos,
`JSON.stringify(todos)` is `[]`, and the right response is **200 with `[]`** —
not 404. A 404 means *this path does not identify anything*; `/todos` identifies
the collection perfectly well, and the collection happens to be empty. Getting
this backwards is one of the most common API design mistakes there is.
""",
    """
`node server.ts` prints the count, then each todo on its own line, then the
whole list as one JSON array:

```
2
{"id":1,"title":"Buy milk","done":false}
{"id":2,"title":"Write tests","done":false}
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```
""",
    pitfalls=[
        "`for (const t in todos)`. One letter, completely different loop: you get the indexes as strings, not the todos. It is legal TypeScript, so nothing stops you.",
        "`todos.length()`. It is a property, not a method.",
        "Returning 404 for an empty list. `[]` under a 200 is the correct answer — the collection exists and is empty.",
    ],
    exercises=[
        _pex("todo-m2-list-1", "Walk the list",
             "Print each todo on its own line, in order. Fill in the loop header.",
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

addTodo("Buy milk");
addTodo("Write tests");

for (const t of todos) {
  console.log(JSON.stringify(t));
}
"""),
             "for (const t of todos) {",
             [("", '{"id":1,"title":"Buy milk","done":false}\n'
                   '{"id":2,"title":"Write tests","done":false}')],
             ["You want the todos themselves, not their positions.",
              "The keyword that walks values is `of`.",
              "`for (const t of todos) {`"]),
        _pfix("todo-m2-list-fix1", "The wrong three-letter word",
              "This loop prints indexes instead of todos, and the program does not "
              "compile because of it. Change one word.",
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

addTodo("Buy milk");
addTodo("Write tests");

for (const t in todos) {
  console.log(t.title);
}
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

addTodo("Buy milk");
addTodo("Write tests");

for (const t of todos) {
  console.log(t.title);
}
"""),
              [("", "Buy milk\nWrite tests")],
              ["The error says `title` does not exist on type `string`.",
               "`in` gives you the keys — `\"0\"`, `\"1\"` — as strings.",
               "`for (const t of todos) {`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("`GET /todos` is called and the store is empty. What should it answer?",
            ["200 with `[]`", "404 with an error body", "204 with no body",
             "200 with `null`"],
            0,
            "The collection exists; it is empty. 404 means the path identifies "
            "nothing, which is a different claim entirely — and one that forces every "
            "client to special-case \"no todos yet\" as an error."),
    ],
)

_M2_FINAL = _pch(
    "todo-m2-build", "Module 2 build — the store", "Easy",
    "Put the module together. Declare the store (`todos` and `nextId`), write "
    "`addTodo(title)` that allocates an id from the counter, keeps the todo and "
    "returns it, then let the code below drive it.\n\n"
    "Ids must come from the counter, not from the list's length — the script "
    "below deletes a todo part way through, so a length-based id would produce a "
    "duplicate and fail.",
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

const created: Todo = addTodo("Buy milk");
console.log(JSON.stringify(created));

addTodo("Write tests");
todos.shift();
addTodo("Ship it");

console.log(todos.length);
for (const t of todos) {
  console.log(JSON.stringify(t));
}
console.log(JSON.stringify(todos));
"""),
    """const todos: Todo[] = [];
let nextId = 1;

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}""",
    [("", '{"id":1,"title":"Buy milk","done":false}\n'
          "2\n"
          '{"id":2,"title":"Write tests","done":false}\n'
          '{"id":3,"title":"Ship it","done":false}\n'
          '[{"id":2,"title":"Write tests","done":false},'
          '{"id":3,"title":"Ship it","done":false}]')],
    ["Three things go in the blank: the array, the counter, and `addTodo`.",
     "The array needs its `: Todo[]` annotation or the push will not compile.",
     "Inside `addTodo`: take the id from `nextId`, advance `nextId`, push, return.",
     "The third todo must get id 3. If it gets 2, you took the id from "
     "`todos.length` rather than the counter."],
)

_TODO_MODULES.append(_pmod(
    key="todo-store", number=2, phase="model",
    title="The store",
    what="an array, a counter, and the id bug everybody writes",
    goal="Hold the todos in one place and give each one an id that stays unique.",
    why=_M2_WHY,
    est_minutes=40,
    builds_on=["todo-shape"],
    concepts=["module state", "const vs let", "arrays", "for…of", "id allocation"],
    objectives=[
        "Declare a typed array and explain why the annotation is required when it starts empty",
        "Say precisely what `const` protects on an array, and what it does not",
        "Write a function that allocates an id, stores a todo and returns it",
        "Explain the collision `todos.length + 1` causes, and when it first shows up",
        "Walk a list with `for … of` and know what `for … in` would have given you",
        "Justify 200 + `[]` rather than 404 for an empty collection",
    ],
    deliverable="An in-memory store: add a todo, get it back with an id no other "
                "todo will ever have, and read the whole list.",
    brief=_M2_BRIEF,
    syntax=_M2_SYNTAX,
    steps=[_M2_S1, _M2_S2, _M2_S3, _M2_S4],
    final_build=_M2_FINAL,
    acceptance=[
        "`addTodo(\"Buy milk\")` returns the todo *and* leaves it in `todos`.",
        "Three adds produce ids 1, 2, 3 — from the counter, not the length.",
        "Deleting a todo and adding another never produces a repeated id.",
        "`JSON.stringify(todos)` on an empty store is `[]`.",
        "`todos` is `const` and `nextId` is `let`, and you can say why each is right.",
    ],
    reference="""// server.ts — module 2
//
// The store: the one place that owns the data. Everything else asks it.
// Right now that is an array in memory — module 19 swaps it for a file, and
// because every access goes through addTodo (and, from module 3, findTodo),
// that swap will not touch a single route.

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

// `const` because the binding never changes — pushing into the array is not
// reassigning it. `let` because nextId genuinely gets rebound: 1 becomes 2.
const todos: Todo[] = [];
let nextId = 1;

// Ids come from a counter that only ever goes up. NOT from todos.length + 1:
// after a delete, the length repeats and two todos end up sharing an id.
// (In production this is crypto.randomUUID(). It is 1, 2, 3 here so the tests
// can assert an exact response.)
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);      // easy line to forget; nothing warns you
  return todo;           // POST /todos sends this straight back (module 9)
}

const created: Todo = addTodo("Buy milk");
console.log(JSON.stringify(created));

addTodo("Write tests");
todos.shift();           // stands in for DELETE — built properly in module 12
addTodo("Ship it");

console.log(todos.length);
for (const t of todos) {
  console.log(JSON.stringify(t));
}
console.log(JSON.stringify(todos));
""",
    stretch=[
        "Add `clearTodos()` that empties the list. Should it reset `nextId`? Argue both sides, then decide — and notice the argument is the same one as step 3.",
        "Make `addTodo` reject an empty title by returning early. You will discover you have no way to report *why*, which is the problem module 14 exists to solve.",
        "Swap the array for a `Map<number, Todo>` and see which functions get shorter and which get longer. Module 20 revisits this.",
    ],
    glossary=[
        _pgloss("module state", "Variables at the top level of a file, shared by everything in the process. The store lives here."),
        _pgloss("binding", "The link between a name and a value. `const` freezes the binding; the value's own contents can still change."),
        _pgloss("never[]", "The array type with no possible element, inferred for `[]` when nothing says otherwise. The cause of the confusing first-push error."),
        _pgloss("id allocation", "Deciding what identifier a new record gets. A counter, a UUID or a database sequence — never a position in a list."),
        _pgloss("collision", "Two records ending up with the same id. Every lookup after that point is ambiguous."),
        _pgloss("for…of", "Loops over an array's values. `for…in` loops over its keys as strings, which is almost never what you want."),
    ],
    cheatsheet="""
```ts
// The store — module state, one per process
const todos: Todo[] = [];    // annotation required: `[]` alone infers never[]
let nextId = 1;              // `let` because it gets reassigned

// Add
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;       // use it, THEN advance it
  todos.push(todo);          // push returns a number, not the todo
  return todo;
}

// Read
todos.length;                // property, not a method
for (const t of todos) { }   // values.  `in` would give you "0", "1"
JSON.stringify(todos);       // [{…},{…}]  — the body of GET /todos
```

| Decision | Choice | Because |
|---|---|---|
| `todos` | `const` | the binding never changes; `push` is not reassignment |
| `nextId` | `let` | 1 genuinely becomes 2 |
| id source | a counter | `todos.length + 1` repeats after a delete |
| empty list | `200 []` | the collection exists and is empty; 404 says it does not exist |
| loop | `for…of` | `for…in` gives you index strings |
""",
    self_check=[
        "Can you write the four lines of `addTodo` from memory, in the right order, and say what each one is for?",
        "Can you explain why `const todos` still allows `todos.push(…)`?",
        "Can you produce, on demand, the exact sequence of operations that makes `todos.length + 1` allocate a duplicate id?",
        "Can you say what `const todos = []` infers, and why the resulting error mentions `never`?",
        "Can you justify 200 + `[]` over 404 for an empty collection to someone who disagrees?",
    ],
    review=[
        _pq("Which line, if you forget it, leaves `addTodo` compiling and returning a "
            "correct todo while the list stays empty forever?",
            ["`todos.push(todo);`", "`nextId = nextId + 1;`", "`return todo;`",
             "`const todos: Todo[] = [];`"],
            0,
            "Nothing in the type system can tell that you meant to keep the value. "
            "The other three all fail loudly: without the counter the ids repeat, "
            "without the return the declared `: Todo` errors, and without the array "
            "nothing compiles at all."),
        _pq("`const todos = []; todos.push(myTodo);` — what does the compiler say?",
            ["`Todo` is not assignable to `never`",
             "`push` does not exist on type `never[]`",
             "Nothing — it compiles and works",
             "`todos` is `const` and cannot be modified"],
            0,
            "The empty literal was inferred as `never[]`, so the parameter of `push` "
            "is `never` — the type nothing is assignable to. The fix is the "
            "annotation, not `let`."),
        _pq("Why does this track use `1, 2, 3` for ids when real services use UUIDs?",
            ["Because a test can only assert an exact response body if the ids are predictable",
             "Because UUIDs are not available in Node",
             "Because counters are faster",
             "Because UUIDs cannot be typed as `number`"],
            0,
            "Determinism. `crypto.randomUUID()` is right in production and would make "
            "every expected output in this track unwritable. The counter's real "
            "weaknesses — it resets on restart and collides across processes — are "
            "exactly why production does not use it."),
    ],
    milestone="Your app has a memory. Todos survive from one function call to the "
              "next, each with an id that will still mean the same thing in "
              "module 20.",
))
