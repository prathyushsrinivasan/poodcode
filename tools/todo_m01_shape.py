# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 1 — What a todo is.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# THE CONSTRAINT THAT SHAPES THIS MODULE: it is first, so it may assume
# nothing. Every token in `_SCOPE_RULES` is off-limits except the three
# introduced here (`type `, `JSON.stringify(`, and the object literal), and the
# ungated basics module 1's own primer covers — `const`, `function`, `return`,
# `if`, `console.log`, template literals.
#
# In particular there are NO arrays yet (module 2), no `.find` and no
# `undefined` (module 3), no arrow functions (module 14) and no object spread
# (module 11). If a program here looks longhand — `{ id: id, title: title }`
# rather than shorthand, a `function` rather than a `=>` — that is deliberate,
# not an oversight.
#
# PROGRAMS ARE STDIN-FREE. Reading stdin means splitting it, and `.split(` is
# not introduced until module 10. So phase 1's programs print a fixed sequence
# of lines and carry one test each. That is enough: a drill is judged on exact
# stdout, and the thing being judged here is whether the type is right.
# ---------------------------------------------------------------------------

_M1_WHY = (
    "You cannot build an API for a thing you have not defined. Every decision "
    "later in this project — what `POST /todos` accepts, what `GET /todos` "
    "returns, what validation rejects, what gets written to disk — is "
    "downstream of one question that takes ten minutes to answer and causes "
    "months of pain when it is answered badly: what *is* a todo?"
)

_M1_BRIEF = """
### The whole module in one line

Write down what a todo is, in a form the compiler will hold you to, and print
one as exactly the JSON your API will eventually send.

### Why start here rather than with the server

The instinct is to get something on `localhost` first, because that feels like
progress. Resist it for one module. A server is plumbing; you can add it in
twenty minutes once you know what is flowing through the pipes. The data model
is the thing you will be stuck with — every route, every validator and every
line of storage code is written in terms of it, so a field you get wrong now is
a field you rename in nine places in module 19.

### Designing the fields

A todo needs, at minimum, an answer to three questions.

| Question | Field | Type | Why not something else |
|---|---|---|---|
| Which one is this? | `id` | `number` | Every resource needs a stable handle, because `/todos/1` has to mean something. Counters, not names — two todos can share a title. |
| What does it say? | `title` | `string` | Free text. Not `name`: the word `name` invites you to think it is unique, and it is not. |
| Is it finished? | `done` | `boolean` | Two states, so a boolean. The moment there is a third state (`archived`) this becomes a union of string literals — but do not build that today. |

Three fields. Genuinely three. The temptation is to add `createdAt`,
`priority`, `tags` and `dueDate` now, while you are thinking about it, and the
reason not to is that you cannot yet *justify* any of them from a behaviour the
API has to support. Fields you cannot justify are fields you will half-support:
accepted by `POST`, forgotten by `PATCH`, absent from the validator, and wrong
in storage. Add a field in the module that needs it.

### Why `type` and not `interface`

TypeScript will let you write either:

```ts
type Todo = { id: number };
interface Todo { id: number }
```

For a plain data shape they are close to interchangeable. This track uses `type`
everywhere and never mentions `interface` again, for two reasons: `type` also
describes things `interface` cannot (unions, which module 15 needs badly), so
using one keyword throughout means one thing to learn; and `interface` silently
allows *declaration merging* — declare it twice and the two quietly combine
rather than erroring — which is a feature for library authors and a trap for
everyone else.
"""

_M1_SYNTAX = [
    _syn(
        "type Todo = { id: number; title: string; done: boolean };",
        "Give a name to a shape. `Todo` now means \"an object with exactly these "
        "three fields, of these three types\" everywhere you write it.",
        """
type Todo = {
  id: number;
  title: string;
  done: boolean;
};
""",
        "The separator inside the braces can be `;` or `,` or a newline. Pick one "
        "and stay with it — this track uses `;`, matching how the fields would be "
        "written in an object type on one line.",
    ),
    _syn(
        "const first: Todo = { id: 1, title: \"Buy milk\", done: false };",
        "Declare a value and tell the compiler which shape it must have. If the "
        "object is missing a field, has a spare one, or has one of the wrong "
        "type, this line fails to compile.",
        """
const first: Todo = { id: 1, title: "Buy milk", done: false };
console.log(first.title);
""",
        "The annotation goes on the variable, not the value. `const first = { … } "
        "as Todo` looks similar and is much weaker — `as` tells the compiler to "
        "stop arguing, which is the opposite of what you want here.",
    ),
    _syn(
        "first.title",
        "Read one field out of an object.",
        """
const first: Todo = { id: 1, title: "Buy milk", done: false };
console.log(first.done);
""",
        "Misspell the field and you get a compile error naming it — which is most "
        "of the value of having written the type down at all.",
    ),
    _syn(
        "JSON.stringify(first)",
        "Turn a value into the JSON text an HTTP response is made of.",
        """
const first: Todo = { id: 1, title: "Buy milk", done: false };
console.log(JSON.stringify(first));
// {"id":1,"title":"Buy milk","done":false}
""",
        "Keys come out in the order you inserted them, NOT alphabetically. That is "
        "why the field order in your object literal is part of your API's output "
        "and not a style choice.",
    ),
    _syn(
        "function makeTodo(id: number, title: string): Todo { return { … }; }",
        "A function with typed parameters and a declared return type. The return "
        "type is checked against what you actually return.",
        """
function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}
console.log(JSON.stringify(makeTodo(1, "Buy milk")));
""",
        "Writing `: Todo` on the end is optional — TypeScript would infer it — and "
        "you should write it anyway. Inferred return types report a mistake at "
        "every call site; a declared one reports it once, on the line that is "
        "actually wrong.",
    ),
    _syn(
        "console.log(value)",
        "Print one line to stdout. This is the whole output mechanism until the "
        "server arrives in module 4.",
        """
console.log("Buy milk");
console.log(false);
console.log(JSON.stringify({ id: 1 }));
""",
        "`console.log` on an object prints a debugging view, not JSON — "
        "`{ id: 1 }` rather than `{\"id\":1}`. Always stringify when the output is "
        "meant to be JSON.",
    ),
]

_M1_S1 = _pstep(
    "fields", "Decide the fields",
    "Three questions a todo has to answer, and nothing else.",
    """
Open a new file, `server.ts`. It will not serve anything for another three
modules; name it that anyway so you are not renaming imports later.

Before you type, answer this on paper — it takes a minute and it is the actual
work of the module:

> **What is the smallest set of fields such that the API in the project brief
> can be built?**

Look back at the contract on the project page. It has five endpoints. Walk them:

- `GET /todos` returns a list — needs nothing extra.
- `POST /todos` takes `{"title": "…"}` and returns a todo **with an id it did
  not send** — so the server invents `id`, and `done` starts somewhere.
- `GET /todos/:id` looks one up by id — confirms `id` must be unique and stable.
- `PATCH /todos/:id` takes `{"done": true}` — confirms `done` is a field, not a
  computed thing.
- `DELETE /todos/:id` — needs nothing extra.

That is `id`, `title`, `done`. Nothing in the contract needs a fourth field, so
there is no fourth field.

Write the answer down as a comment at the top of your file. You are going to
disagree with yourself about it in module 17 and it is useful to see what you
originally thought.
""",
    """
Your `server.ts` contains a comment naming exactly three fields and the reason
each one exists. No code yet.

If you wrote down a fourth field, delete it and write next to it which endpoint
in the contract requires it. If you cannot name one, you have just proved the
point of this step.
""",
    pitfalls=[
        "Adding `createdAt` because every table you have seen has one. It is a fine field; it is not needed by any endpoint in the contract, and phase 5 is where sorting gives it a reason to exist.",
        "Calling the text field `name`. `name` reads as an identifier and invites a uniqueness rule nobody wants; `title` reads as free text, which is what it is.",
        "Making `done` a string (`\"pending\"` / `\"complete\"`) before there is a third state. Two states is a boolean. Widen it when reality does.",
    ],
    warmup=[
        _pq("The contract says `POST /todos` takes `{\"title\":\"Buy milk\"}` and "
            "returns `{\"id\":1,\"title\":\"Buy milk\",\"done\":false}`. What does that "
            "tell you about `id` and `done`?",
            ["Both are supplied by the server, not the client",
             "Both are optional fields on a todo",
             "`id` is sent by the client and `done` by the server",
             "Nothing — the response shape is unrelated to the fields"],
            0,
            "The client sent neither, and both came back. Anything present in the "
            "response but absent from the request is the server's job to produce — "
            "which is exactly why `POST` cannot simply store what it was given."),
    ],
)

_M1_S2 = _pstep(
    "type", "Write the type down",
    "Turn the three fields into something the compiler enforces.",
    """
Under your comment, write the type:

```ts
type Todo = {
  id: number;
  title: string;
  done: boolean;
};
```

That is the single most valuable line in the project. From here on, `Todo` is a
word you can use anywhere and the compiler knows what it means.

Now make one, and annotate it:

```ts
const first: Todo = { id: 1, title: "Buy milk", done: false };
console.log(first.title);
```

The annotation `: Todo` is what makes this worth doing. Prove it to yourself —
try each of these in turn and read the error before deleting it:

```ts
const bad1: Todo = { id: 1, title: "Buy milk" };                  // missing done
const bad2: Todo = { id: 1, title: "Buy milk", done: "no" };      // wrong type
const bad3: Todo = { id: 1, title: "Buy milk", done: false, x: 1 }; // spare field
```

The third one is the interesting one. TypeScript normally lets an object have
extra fields — but not when you assign a *literal* straight to an annotated
variable, where a spare key is almost always a typo. That check has a name
(*excess property checking*) and it is the reason `dnoe: false` gets caught here
and would not if you went through a variable first.
""",
    """
`node server.ts` runs and prints:

```
Buy milk
```

And all three `bad` lines, when you try them, are refused **before** the program
runs — with an error naming the field. If a wrong one ran anyway, you saved the
file with the line commented out, or you are on a `.js` file.
""",
    pitfalls=[
        "Writing `const first = { … } as Todo`. `as` is an assertion, not a check — it tells the compiler you know better and switches off exactly the protection you added the type for. Annotate the variable instead.",
        "Expecting Node to catch a type error on its own. Node *strips* types to run `.ts`; it never checks them. The exercises here are type-checked before they run, but on your own machine you need `npx tsc --noEmit --strict server.ts`.",
    ],
    exercises=[
        _pex("todo-m1-type-1", "Complete the type",
             "The program reads `t.done`, but `Todo` does not declare it yet. Add the "
             "missing field with the right type.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const t: Todo = { id: 1, title: "Buy milk", done: false };
console.log(t.title);
console.log(t.done);
"""),
             "  done: boolean;",
             [("", "Buy milk\nfalse")],
             ["A todo is either finished or it is not — two states.",
              "The field is named `done`, and the type for two states is `boolean`.",
              "`  done: boolean;`"]),
        _pex("todo-m1-type-2", "Annotate the value",
             "The object below is a perfectly good todo, but nothing is checking that. "
             "Annotate `second` so the compiler holds it to the `Todo` shape.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const second: Todo = { id: 2, title: "Write tests", done: false };
console.log(second.id);
console.log(second.title);
"""),
             ": Todo",
             [("", "2\nWrite tests")],
             ["The annotation goes after the variable name, before the `=`.",
              "It is a colon followed by the type's name.",
              "`const second: Todo = { … }`"]),
    ],
    quiz=[
        _pq("Why does `const t: Todo = { id: 1, title: \"x\", done: false, extra: 9 }` "
            "fail to compile, when TypeScript usually allows an object to have more "
            "fields than a type requires?",
            ["Excess property checking applies to object literals assigned directly to an annotated target",
             "`Todo` is a sealed type because it was declared with `type`",
             "Objects may never have fields their type does not declare",
             "It does not fail — `extra` is silently allowed"],
            0,
            "A spare key on a literal you are assigning right now is nearly always a "
            "typo, so TypeScript makes a special case and rejects it. Assign the "
            "literal to an unannotated variable first and the check does not apply — "
            "which is worth knowing, because it is how the error occasionally hides."),
    ],
)

_M1_S3 = _pstep(
    "json", "Print it the way the API will",
    "`JSON.stringify`, and the field order you did not know was part of your API.",
    """
Your server will never send a `Todo` object. It sends *text* — the JSON encoding
of one. Start looking at that text now, because it is what a client sees:

```ts
console.log(JSON.stringify(first));
```

```
{"id":1,"title":"Buy milk","done":false}
```

Compare that with what you get without the stringify:

```ts
console.log(first);      // { id: 1, title: 'Buy milk', done: false }
```

Single quotes, spaces, no quotes on the keys — that is Node's *debugging* view
of an object, and it is not JSON. Confusing the two costs people an hour when
their handler "obviously returns the right thing" and the client cannot parse it.

### The thing that will bite you

`JSON.stringify` emits keys **in the order they were inserted**, not
alphabetically. So these two todos are identical as values and different as
responses:

```ts
const a: Todo = { id: 1, title: "Buy milk", done: false };
const b: Todo = { title: "Buy milk", id: 1, done: false };

JSON.stringify(a);   // {"id":1,"title":"Buy milk","done":false}
JSON.stringify(b);   // {"title":"Buy milk","id":1,"done":false}
```

Both type-check. Both are `Todo`. One matches the contract and one does not.

A real client parsing JSON does not care about key order — but every test in
this track compares output as text, and so does every snapshot test you will
ever write at work. Build your objects in contract order and the problem never
arises.
""",
    """
`node server.ts` prints, exactly:

```
{"id":1,"title":"Buy milk","done":false}
```

Character for character — no spaces after the colons, `id` first. If yours
differs, you are either printing the object rather than the JSON, or your fields
are in a different order.
""",
    pitfalls=[
        "`console.log(obj)` instead of `console.log(JSON.stringify(obj))`. The first prints something that *looks* close enough to JSON to be mistaken for it, quotes and all — until a client tries to parse it.",
        "Assuming key order is cosmetic. It is, to a parser; it is not, to a text comparison — and every judged exercise here, plus most snapshot tests in the wild, compare text.",
    ],
    warmup=[
        _pq("`const t: Todo = { done: false, id: 1, title: \"Buy milk\" };` — what does "
            "`JSON.stringify(t)` print?",
            ['{"done":false,"id":1,"title":"Buy milk"}',
             '{"id":1,"title":"Buy milk","done":false}',
             '{ done: false, id: 1, title: "Buy milk" }',
             "The order is unspecified and may vary between runs"],
            0,
            "Insertion order, exactly as written. The annotation `: Todo` says which "
            "fields must be present — it says nothing about the order you wrote them "
            "in, and `stringify` follows the object, not the type."),
    ],
    exercises=[
        _pex("todo-m1-json-1", "Send it as JSON",
             "The program prints a debugging view of the todo. Print the JSON your API "
             "would actually send instead.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const t: Todo = { id: 1, title: "Buy milk", done: false };
console.log(JSON.stringify(t));
"""),
             "JSON.stringify(t)",
             [("", '{"id":1,"title":"Buy milk","done":false}')],
             ["`console.log(t)` prints Node's view of the object, not JSON.",
              "There is a built-in that turns a value into JSON text.",
              "`console.log(JSON.stringify(t));`"]),
        _pfix("todo-m1-json-fix1", "The response is in the wrong order",
              "This program compiles and the value is a perfectly good todo — but the "
              "response text does not match the contract, which puts `id` first, then "
              "`title`, then `done`. Fix it.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const t: Todo = { title: "Buy milk", done: false, id: 1 };
console.log(JSON.stringify(t));
"""),
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const t: Todo = { id: 1, title: "Buy milk", done: false };
console.log(JSON.stringify(t));
"""),
              [("", '{"id":1,"title":"Buy milk","done":false}')],
              ["The type is fine and the values are fine. Look at the output text.",
               "`JSON.stringify` follows insertion order, not the order the fields "
               "were declared in the type.",
               "Reorder the object literal to `{ id: 1, title: \"Buy milk\", done: false }`."]),
    ],
)

_M1_S4 = _pstep(
    "factory", "A function that makes one",
    "Stop writing todos by hand — you are about to need a lot of them.",
    """
Typing a full object literal every time gets old fast, and it is also where
inconsistency creeps in: one todo starts `done: false`, another accidentally
starts `done: true`. Put the rule in one place.

```ts
function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}
```

Three things to notice.

**The parameters are typed.** `makeTodo("1", "Buy milk")` is now a compile
error rather than a todo with a string id that breaks `GET /todos/1` at three
in the morning.

**The return type is declared.** `: Todo` is optional — TypeScript would work it
out — and writing it is still the right call. Without it, a mistake inside the
function is reported at every *call site*, because the inferred type quietly
became something else. With it, the mistake is reported on the line that is
actually wrong. Declare return types on anything you would call from more than
one place.

**`done: false` is not a parameter.** A new todo is not done. That is a rule
about todos, and rules about todos belong in one function rather than at every
place that makes one.

Now use it:

```ts
console.log(JSON.stringify(makeTodo(1, "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
```

> **On `{ id: id, title: title }`.** TypeScript has a shorthand for this —
> `{ id, title }` — and it is what you would normally write. This track spells
> it out for now, because the longhand makes it obvious that the *field* `id`
> and the *parameter* `id` are two different things that happen to share a name.
> Once that is second nature, use the shorthand.
""",
    """
`node server.ts` prints two lines:

```
{"id":1,"title":"Buy milk","done":false}
{"id":2,"title":"Write tests","done":false}
```

Then try `makeTodo("3", "Break it")` and confirm it is refused before the
program runs, with an error about `string` not being assignable to `number`.
That refusal is the whole return on writing the types.
""",
    pitfalls=[
        "Taking `done` as a parameter \"for flexibility\". Nothing in the contract creates a todo that is already done, and every caller then has to remember to pass `false`. Add the parameter when a caller needs it.",
        "Leaving the return type off. It compiles, and it moves every future error away from the line that caused it.",
    ],
    exercises=[
        _pex("todo-m1-fn-1", "Declare what it returns",
             "`makeTodo` builds the right object but does not say what it returns. Add "
             "the return type annotation.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

console.log(JSON.stringify(makeTodo(1, "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
"""),
             ": Todo",
             [("", '{"id":1,"title":"Buy milk","done":false}\n'
                   '{"id":2,"title":"Write tests","done":false}')],
             ["The return type goes after the parameter list's closing bracket.",
              "A colon, then the name of the type the function hands back.",
              "`function makeTodo(id: number, title: string): Todo {`"]),
        _pex("todo-m1-fn-2", "A new todo is not done",
             "Fill in the `done` field so a freshly made todo starts unfinished.",
             _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

const t: Todo = makeTodo(7, "Ship it");
console.log(JSON.stringify(t));
console.log(t.done);
"""),
             "done: false",
             [("", '{"id":7,"title":"Ship it","done":false}\nfalse')],
             ["Nobody creates a task they have already finished.",
              "The field is `done` and the value is a boolean literal.",
              "`return { id: id, title: title, done: false };`"]),
        _pfix("todo-m1-fn-fix1", "The id is a string",
              "This program refuses to compile. Read the error, find the call that is "
              "wrong, and fix the call — not the function.",
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

console.log(JSON.stringify(makeTodo("1", "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
"""),
              _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

console.log(JSON.stringify(makeTodo(1, "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
"""),
              [("", '{"id":1,"title":"Buy milk","done":false}\n'
                    '{"id":2,"title":"Write tests","done":false}')],
              ["The error names a `string` where a `number` was expected.",
               "One of the two calls passes its id in quotes.",
               "`makeTodo(1, \"Buy milk\")` — no quotes around the 1."],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why declare `: Todo` as `makeTodo`'s return type when TypeScript can "
            "infer it?",
            ["A mistake inside the function is then reported there, instead of at every place that calls it",
             "Without it the function returns `any`",
             "Inference does not work on object literals",
             "It makes the function run faster"],
            0,
            "Inference is accurate but it propagates: get the body wrong and the "
            "inferred type quietly changes, so the errors appear wherever the result "
            "is *used*. A declared return type pins the contract at the definition, "
            "and the error lands on the line that is actually wrong."),
    ],
)

_M1_FINAL = _pch(
    "todo-m1-build", "Module 1 build — the shape of a todo", "Easy",
    "Put the module together. Declare the `Todo` type, write `makeTodo(id, title)` "
    "returning a new unfinished todo, and print three todos as JSON — ids 1, 2 and "
    "3, titles `Buy milk`, `Write tests` and `Ship it`, in that order.\n\n"
    "Everything below the blank is already written for you.",
    _plain("""
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

console.log(JSON.stringify(makeTodo(1, "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
console.log(JSON.stringify(makeTodo(3, "Ship it")));
"""),
    """type Todo = {
  id: number;
  title: string;
  done: boolean;
};

function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}""",
    [("", '{"id":1,"title":"Buy milk","done":false}\n'
          '{"id":2,"title":"Write tests","done":false}\n'
          '{"id":3,"title":"Ship it","done":false}')],
    ["Two things go in the blank: the `type` declaration and the `makeTodo` function.",
     "The type has three fields — `id: number`, `title: string`, `done: boolean`.",
     "`makeTodo` takes `(id: number, title: string)`, returns `: Todo`, and always "
     "sets `done: false`.",
     "Field order in the returned object decides the output order: `id`, `title`, "
     "`done`."],
)

_TODO_MODULES.append(_pmod(
    key="todo-shape", number=1, phase="model",
    title="What a todo is",
    what="the three fields, and why not a fourth",
    goal="Define the `Todo` type and produce one as exactly the JSON your API will send.",
    why=_M1_WHY,
    est_minutes=35,
    builds_on=[],
    concepts=["type alias", "object types", "JSON.stringify", "insertion order"],
    objectives=[
        "Justify each field of a data model from the endpoints that need it",
        "Declare an object type with `type` and hold a value to it",
        "Explain why this track uses `type` rather than `interface`",
        "Turn a value into the JSON text an HTTP response carries",
        "Predict the key order `JSON.stringify` produces, and control it",
        "Write a factory function with typed parameters and a declared return type",
    ],
    deliverable="A `Todo` type the compiler enforces, and a function that produces "
                "one as exactly the JSON your API will return.",
    brief=_M1_BRIEF,
    syntax=_M1_SYNTAX,
    steps=[_M1_S1, _M1_S2, _M1_S3, _M1_S4],
    final_build=_M1_FINAL,
    acceptance=[
        "`server.ts` declares `type Todo` with exactly `id`, `title` and `done`.",
        "`makeTodo(1, \"Buy milk\")` returns a todo whose `done` is `false`.",
        "`makeTodo(\"1\", \"Buy milk\")` is refused before the program runs.",
        "Printing a todo gives `{\"id\":1,\"title\":\"Buy milk\",\"done\":false}` — that "
        "exact text, `id` first.",
    ],
    reference="""// server.ts — module 1
//
// A todo answers three questions: which one is this (id), what does it say
// (title), is it finished (done). Nothing in the API contract needs a fourth
// field, so there isn't one yet.

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

// One place that knows how a new todo starts. `done` is not a parameter
// because nothing in the contract creates an already-finished todo.
function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}

// Field order here is the field order in the response text — see step 3.
console.log(JSON.stringify(makeTodo(1, "Buy milk")));
console.log(JSON.stringify(makeTodo(2, "Write tests")));
console.log(JSON.stringify(makeTodo(3, "Ship it")));
""",
    stretch=[
        "Add a `priority` field, then try to justify it from the contract. Delete it again.",
        "Write `type TodoInput = { title: string }` — the shape a client sends — and give `makeTodo` that instead of a bare title. Module 9 arrives at this independently.",
        "Try `interface Todo` twice in one file with different fields and watch them merge silently rather than error. That is the trap step 2 mentioned.",
    ],
    glossary=[
        _pgloss("type alias", "A name for a shape, declared with `type`. `Todo` is an alias; the shape is the object type on the right of the `=`."),
        _pgloss("object type", "The `{ id: number; title: string }` part — a list of field names and the type of each."),
        _pgloss("annotation", "The `: Todo` after a variable or parameter name. It tells the compiler what is allowed there, and is checked."),
        _pgloss("assertion", "`value as Todo`. Tells the compiler to stop checking. Looks like an annotation, does the opposite."),
        _pgloss("excess property check", "The rule that rejects a spare field on an object literal assigned straight to an annotated target — the thing that catches `dnoe: false`."),
        _pgloss("insertion order", "The order keys were added to an object, which is the order `JSON.stringify` writes them out in."),
        _pgloss("declaration merging", "The `interface` feature where two declarations of the same name combine instead of erroring. The reason this track uses `type`."),
    ],
    cheatsheet="""
```ts
// Declare a shape
type Todo = {
  id: number;
  title: string;
  done: boolean;
};

// Hold a value to it (checked — missing, spare and wrong-typed fields all fail)
const t: Todo = { id: 1, title: "Buy milk", done: false };

// Read a field
t.title;          // "Buy milk"
t.done;           // false

// Turn it into the text an HTTP response carries
JSON.stringify(t);   // {"id":1,"title":"Buy milk","done":false}
console.log(t);      // { id: 1, title: 'Buy milk', done: false }   ← NOT JSON

// A factory: typed parameters, declared return type, the default in one place
function makeTodo(id: number, title: string): Todo {
  return { id: id, title: title, done: false };
}
```

| Want | Write | Not |
|---|---|---|
| Check a value's shape | `const t: Todo = { … }` | `const t = { … } as Todo` |
| A shape you may later union | `type X = { … }` | `interface X { … }` |
| JSON text | `JSON.stringify(t)` | `console.log(t)` |
| `id` first in the response | build the literal `id` first | rely on the type's field order |
""",
    self_check=[
        "Can you name each field of `Todo` and the endpoint in the contract that requires it?",
        "Can you say what `as Todo` does differently from `: Todo`, and why you want the second one?",
        "Can you predict the exact text `JSON.stringify` produces for an object, including key order?",
        "Can you explain why `done: false` lives inside `makeTodo` rather than in its parameter list?",
        "Can you give one reason to declare a return type that inference does not give you?",
    ],
    review=[
        _pq("Which of these is the strongest reason NOT to add a `createdAt` field now?",
            ["No endpoint in the contract needs it, so it would be half-supported",
             "Dates are hard to represent in TypeScript",
             "It would make `JSON.stringify` output non-deterministic",
             "Adding fields later is impossible without a migration"],
            0,
            "A field with no endpoint behind it gets accepted by one route, forgotten "
            "by another, missed by the validator and wrong in storage. The date is "
            "also non-deterministic, which is a real problem for these tests — but "
            "the design reason is the one that generalises."),
        _pq("`const t = { id: 1, title: \"x\", done: false, extra: 9 }; const u: Todo = t;` "
            "— does the second line compile?",
            ["Yes — excess property checking only applies to object literals",
             "No — `extra` is a spare field and always rejected",
             "No — `t` was declared without an annotation",
             "Only if `extra` is optional on `Todo`"],
            0,
            "Going through a variable first sidesteps the excess property check, "
            "because the rule is a special case for literals. `t` has all three "
            "required fields with the right types, so it is assignable. Worth knowing: "
            "it is how a stray field occasionally survives into a response."),
        _pq("Your handler returns `{ title: \"Buy milk\", id: 1, done: false }` and the "
            "test expects `{\"id\":1,\"title\":\"Buy milk\",\"done\":false}`. What failed?",
            ["Nothing about the types — the key order in the output text differs",
             "The object is missing a required field",
             "`title` and `id` have been given the wrong types",
             "`JSON.stringify` sorts keys alphabetically and `done` sorts first"],
            0,
            "Both objects are valid `Todo`s and a JSON parser would treat the two "
            "responses as identical. The comparison here is textual, and `stringify` "
            "follows insertion order — so build the literal in contract order."),
    ],
    milestone="You have a data model. Every route, validator and storage line in "
              "the next nineteen modules is written in terms of the three fields "
              "you just chose.",
))
