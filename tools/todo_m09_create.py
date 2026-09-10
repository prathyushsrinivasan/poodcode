# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 9 — POST /todos, create.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# THE MODULE WHERE THE APPLICATION STOPS BEING YOURS. Everything in the store
# up to here was put there by two lines the learner typed. This is the first
# module where data comes from outside the process — and the first where the
# right answer to "what id does it get?" is "not the one they sent".
#
# THREE THINGS THIS MODULE DELIBERATELY DOES NOT DO, each owned by a later one:
#
#   * It does not VALIDATE. `{"title":""}` is accepted, and `{}` produces a todo
#     with no title at all. Module 14 rejects both with a field-level 400.
#   * It does not DISTRUST the parse. `JSON.parse` hands back `any` and the
#     module says so out loud, because module 13's whole argument is that `any`
#     is silent. Naming the hole here is what makes module 13 land.
#   * It does not CATCH. A body that is not JSON throws, and the given replayer
#     turns that into a 500. That is graded, on purpose — see below.
#
# THE 500 IS A TEST CASE, NOT AN OVERSIGHT. `POST /todos notjson` produces
# `500 {"error":"server_error"}` through the replayer's boundary, and the module
# build asserts it. It is the cheapest possible demonstration of what the next
# three modules are for: the API's answer to bad input today is "something broke
# on our end", which is a lie, and modules 14 and 16 turn it into a 400 and a
# deliberate 500 respectively. Grading the lie is what stops it being a
# surprise.
#
# WHAT GOT DELETED: the two `addTodo` seed calls that have been in every program
# since module 7, and the `/echo` route from module 8. Both were scaffolding
# with a stated expiry date, and this is it. `GET /todos` on a fresh process now
# correctly returns `[]` — which step 4 makes a point of, because an empty
# collection is a 200 and a learner who reaches for 404 there has misunderstood
# what the resource is.
#
# NO `try`/`catch`, NO `typeof`, NO SPREAD anywhere in these programs — 16, 13
# and 11 own those, and `_lint_scope` enforces it. That is why "today a bad body
# is a 500" is taught as a fact about the current build rather than fixed on the
# spot.
# ---------------------------------------------------------------------------

_M9_STORE = """type Todo = {
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
"""

_M9_SEND = """function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}
"""

_M9_READBODY = """function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    req.setEncoding("utf8");
    let body = "";
    req.on("data", (chunk: string) => {
      body = body + chunk;
    });
    req.on("end", () => {
      resolve(body);
    });
  });
}
"""

_M9_HANDLER = """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = addTodo(data.title);
    send(res, 201, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""


def _m9(handler=_M9_HANDLER, store=_M9_STORE):
    """A module-9 judged program. Everything except the handler is code the
    learner already has, so a blank is always about today's lesson."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (store, _M9_SEND, _M9_READBODY, handler)))


_M9_FULL = _m9()

_M9_WHY = (
    "Your server can read a body and does nothing with it, and your store is "
    "still filled by two lines you typed. Every todo in the application is one "
    "you put there — which means the application has no users, only an author. "
    "This is the module where that ends: text arrives, becomes an object, "
    "becomes a todo, and comes back carrying the one thing the client could not "
    "have known, which is the id you gave it."
)

_M9_BRIEF = """
### The whole module in one line

Turn the body you can now read into a todo in the store, and answer `201` with
it.

### Four lines, and each one is a decision

```ts
const body = await readBody(req);      // module 8 — text
const data = JSON.parse(body);         // text → a value. And a hole in the types
const todo = addTodo(data.title);      // the store's id, not the client's
send(res, 201, todo);                  // created, not "OK"
```

That is the whole route. The rest of this module is why each line is that line
and not the obvious alternative.

### `JSON.parse` costs you the type system, and this module says so

```ts
const data = JSON.parse(body);
data.title        // string? number? not there at all? The compiler has no idea
data.anything     // also fine, as far as the compiler is concerned
data.a.b.c        // still fine. Crashes at runtime
```

`JSON.parse` is declared to return `any`, and `any` means *stop checking*. Every
guarantee the last eight modules have been leaning on ends at that line.

Today you are going to trust it anyway — deliberately, with the hole named — and
**module 13 is the module that closes it**. That is not an accident of ordering:
learning to distrust parsed input is a whole lesson, and it is a much better one
after you have written the code that trusts it.

### What happens today when the body is junk

```
$ curl -s -i -X POST localhost:3000/todos -d 'not json'
HTTP/1.1 500 Internal Server Error
{"error":"server_error"}
```

`JSON.parse` throws on input it cannot read, nothing in your handler catches it,
and the error boundary in the replayer turns it into a 500. Look at what that
response *claims*: something went wrong on the server. It did not. The client
sent nonsense and got told the fault was ours.

That is wrong, it is graded in the module build so you cannot miss it, and it
gets fixed twice: **module 14** makes bad input a `400`, and **module 16** makes
the 500 a boundary you wrote rather than one you inherited.

### 201, not 200

`200 OK` says "here is what you asked for". `201 Created` says "something now
exists that did not exist before, and here it is". A client can tell the
difference between a create that happened and a create that was quietly ignored
without reading the body at all.

### The id is yours, not theirs

```
$ curl -s -X POST localhost:3000/todos -d '{"id":99,"title":"Sneaky"}'
{"id":1,"title":"Sneaky","done":false}
```

The client sent `99`. It got `1`. The store owns identity — that is what a store
*is* — and a server that accepts a client-supplied id lets any client overwrite
any row by guessing. You do not reject the id; you ignore it, because it was
never an input.

### Two things get deleted today

The two `addTodo` seed calls, and the `/echo` route. Both were scaffolding with
a stated expiry date and this is it. `GET /todos` on a fresh process now returns
`[]`, and that is a **200**.
"""

_M9_SYNTAX = [
    _syn(
        "const data = JSON.parse(body);",
        "Turn JSON text into a value. The mirror of `JSON.stringify`, which you "
        "have used since module 1 to go the other way.",
        """
const body = '{"title":"Buy milk"}';
const data = JSON.parse(body);
console.log(data.title);      // Buy milk
""",
        "It returns `any` — the compiler stops checking anything you do with the "
        "result — and it **throws** on text it cannot read. Both holes are real, "
        "both are deliberate today, and both are closed later: the type in "
        "module 13, the throw in modules 14 and 16.",
    ),
    _syn(
        "data.title",
        "Reach into the parsed body for the one field this route needs. Take the "
        "field, not the object: what the client sent is a request, not a row.",
        """
const data = JSON.parse(body);
const todo = addTodo(data.title);   // title only. Not data.id, not data.done.
""",
        "`data.title` is `any`, so a missing title is `undefined` and nothing "
        "complains — you get a todo with no title in it. Module 14 is where that "
        "becomes a 400.",
    ),
    _syn(
        "send(res, 201, todo);",
        "**201 Created** — the resource now exists, and the body is it. The "
        "status a POST that created something answers with.",
        """
const todo = addTodo(data.title);
send(res, 201, todo);      // 201, not 200: something new exists
""",
        "Answer with the **stored** todo, not the parsed body. They look alike "
        "and they are not: only the stored one has the id, and only the stored "
        "one is what the next `GET` will return.",
    ),
    _syn(
        "function addTodo(title: string): Todo { … }",
        "Module 2's store, and the reason the client's id is ignored rather than "
        "rejected: `addTodo` takes a title. There is no parameter to pass an id "
        "to.",
        "",
        "This is a design that defends itself. A store whose add function took an "
        "id would need a rule about when to trust it; one that takes a title "
        "cannot be misused.",
        recap=True,
    ),
    _syn(
        "const body = await readBody(req);",
        "Module 8's reader, unchanged and unchanged from here on. Every module "
        "that accepts input starts with this line.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — text becomes a value.
# ---------------------------------------------------------------------------

_M9_S1 = _pstep(
    "parse", "Text becomes a value",
    "`JSON.parse`, the `any` it hands you, and the 500 it can throw.",
    """
Module 8 left you holding this:

```ts
const body = await readBody(req);
// body === '{"title":"Buy milk"}'  — twenty characters of text
```

`body.title` does not exist and does not compile, because `body` is a `string`.
One line changes that:

```ts
const data = JSON.parse(body);
// data.title === "Buy milk"
```

`JSON.parse` is the exact mirror of the `JSON.stringify` you have been using
since module 1. One turns a value into text; the other turns text back into a
value. You have been doing half of this round trip on every response since
module 5.

### And it hands you `any`

```ts
const data = JSON.parse(body);

data.title            // any
data.nonsense         // any — no error
data.a.b.c            // any — no error, and a crash at runtime
```

`JSON.parse` is declared to return `any`, which is TypeScript's way of saying
*stop checking this*. Everything the previous eight modules taught you to lean
on — the compiler noticing a missing field, a wrong type, a typo in a property
name — stops at that line.

That is not a flaw in `JSON.parse`. It is honest: the function genuinely does
not know what is in the text, because the text came from someone else. What is
wrong is *leaving it there*, and **module 13 is the module about that**. It is
four modules away rather than in this one because "distrust your input" is a
much better lesson once you have written the code that trusts it and seen what
it costs.

For today: name the hole, use it anyway, and move on.

### It also throws

```
$ curl -s -i -X POST localhost:3000/todos -d 'not json'
HTTP/1.1 500 Internal Server Error
{"error":"server_error"}
```

Nothing in your handler catches that. The `throw` travels out of your `async`
function as a rejected promise, and the boundary in the given replayer — the one
you read in module 4 — turns it into a 500.

Read what that response *says*: something failed on the server. Nothing failed
on the server. The client sent junk, and the API blamed itself. Every part of
that is fixed later (`400` in module 14, a boundary you wrote in module 16) and
none of it is fixed today, because `try`/`catch` is module 16's and reaching for
it now would skip the argument.

The module build grades that 500. It is a fact about the application you have
right now, and knowing which of your own responses are lies is worth more than a
clean test run.
""",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}

$ curl -s -i -X POST localhost:3000/todos -d 'not json'
HTTP/1.1 500 Internal Server Error
```

The second is not a failure of the step. It is the step: you should be able to
say exactly why that is a 500 today, and exactly which module makes it a 400.
""",
    pitfalls=[
        "Storing `body` instead of `data.title`. It compiles — both are strings — and every todo's title becomes the whole JSON text, quotes and all. This is the first graded fix.",
        "Expecting the compiler to catch `data.titel`. It cannot: `data` is `any`, so every property access on it is legal and every one of them is `any`.",
        "Reaching for `try`/`catch` to handle bad JSON. That is module 16, and skipping to it here means never making the argument for why a 500 was the wrong answer in the first place.",
        "Assuming a 500 means your code is broken. Here it means the *input* was broken and your code had no opinion about it — which is a different bug, in a different place.",
        "`JSON.parse` on an empty body. `POST /todos` with no body at all throws exactly like `not json` does, because `\"\"` is not valid JSON.",
        "Parsing twice. `JSON.parse(await readBody(req))` in two places gives you two unrelated objects and a second read of a stream that has already ended.",
    ],
    warmup=[
        _pq("`const data = JSON.parse(body);`. What type does TypeScript give `data`?",
            ["`any` — the compiler stops checking anything you do with it",
             "`object`, since JSON always parses to an object",
             "`Todo`, inferred from how it is used below",
             "`string`, the same as `body`"],
            0,
            "`JSON.parse` cannot know what is in the text, so it declares `any` "
            "and hands the problem to you. Module 13 is where you take it."),
        _pq("A client posts `not json`. What does it get back today?",
            ["500 — `JSON.parse` throws, nothing catches it, and the replayer's boundary answers",
             "400, because the body was invalid",
             "201 with an empty todo",
             "The request hangs"],
            0,
            "And 500 is the wrong answer: it says the fault was the server's. "
            "Module 14 makes it a 400 and module 16 makes the boundary yours."),
    ],
    exercises=[
        _pex("todo-m9-parse-1", "Text to value",
             "The body has arrived as a string. Turn it into something you can "
             "read a field off.",
             _M9_FULL,
             "    const data = JSON.parse(body);",
             [("POST /todos {\"title\":\"Buy milk\"}\nGET /todos",
               '201 {"id":1,"title":"Buy milk","done":false}'
               '\n200 [{"id":1,"title":"Buy milk","done":false}]')],
             ["The mirror of `JSON.stringify`, which `send` has used since module 5.",
              "It takes the text and returns the value.",
              "Give it a `const` to live in — the next line reads a field off it.",
              "`const data = JSON.parse(body);`"]),
        _pfix("todo-m9-parse-fix1", "The title that is the whole request",
              "Every todo comes back with a title like "
              "`{\"title\":\"Buy milk\"}` — the entire body, quotes and braces "
              "included — instead of `Buy milk`.\n\n"
              "It compiles, because both of them are strings. One step is "
              "missing.",
              _m9("""async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const todo = addTodo(body);
    send(res, 201, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _M9_FULL,
              [("POST /todos {\"title\":\"Buy milk\"}\nPOST /todos {\"title\":\"Write tests\"}",
                '201 {"id":1,"title":"Buy milk","done":false}'
                '\n201 {"id":2,"title":"Write tests","done":false}')],
              ["`readBody` returns text. What has to happen to text before it has fields?",
               "The store wants a title — one field out of the body, not the body.",
               "Two lines where there is one: parse, then read `data.title`.",
               "`const data = JSON.parse(body);` then `addTodo(data.title)`"],
              difficulty="Easy"),
        _pex("todo-m9-parse-2", "One field, not the object",
             "The body is parsed. Create the todo from it — the store takes a "
             "title, and a title is all you should be taking.",
             _M9_FULL,
             "    const todo = addTodo(data.title);",
             [("POST /todos {\"title\":\"Ship it\"}\nPOST /todos {\"title\":\"Again\",\"done\":true}",
               '201 {"id":1,"title":"Ship it","done":false}'
               '\n201 {"id":2,"title":"Again","done":false}')],
             ["`addTodo` is module 2's, and it takes one argument.",
              "Pull the field off the parsed object rather than passing the object.",
              "The second test sends `done: true` and must still come back `false` — "
              "a new todo is not done, whatever the client says.",
              "`const todo = addTodo(data.title);`"]),
    ],
    quiz=[
        _pq("Why is `JSON.parse` declared to return `any` rather than `object`?",
            ["It genuinely cannot know what is in the text — the text came from somewhere else — so it declines to guess",
             "Because `object` would be a breaking change to the standard library",
             "Because JSON can contain functions",
             "It is a historical mistake with no reason behind it"],
            0,
            "The honest type for \"a value someone else sent\" is the one that "
            "forces you to check. `any` is the wrong tool for it — `unknown` is "
            "the right one, and that is module 13 in a sentence."),
        _pq("What is wrong with answering a malformed body with a 500?",
            ["It says the fault was the server's when the client sent something invalid — the client cannot tell it did anything wrong",
             "Nothing; 500 is the correct code for a parse failure",
             "500 responses cannot have a body",
             "It leaks a stack trace"],
            0,
            "Status codes are a contract about *whose problem this is*. 4xx is "
            "yours, 5xx is mine. Module 14 moves this one to where it belongs."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — 201.
# ---------------------------------------------------------------------------

_M9_S2 = _pstep(
    "created", "201 Created",
    "The status code that says something now exists — and why 200 is not it.",
    """
```ts
send(res, 201, todo);
```

**200 OK** means "here is what you asked for". **201 Created** means "something
now exists that did not exist before, and this is it".

A client can tell those apart without reading the body, which matters more than
it sounds: a retry that returns 200 and a create that returns 201 look identical
in a log if you use 200 for both, and "did my POST actually do anything?" is a
question people ask at three in the morning.

### The codes this project uses, and whose fault each one is

You met these in module 5. Here is where the first one lands:

| Code | Means | Arrives in |
|---|---|---|
| `200` | here is what you asked for | 5 |
| `201` | it now exists, and here it is | **9** |
| `204` | done, and there is nothing to say | 12 |
| `400` | your request was wrong | 14 |
| `404` | there is nothing at this address | 5 |
| `500` | something broke on my end | 16 |

Three of those are the client's fault and two are the server's, and getting that
split right is most of what "designing an API" means in practice.

### Answer with what you stored

```ts
const todo = addTodo(data.title);
send(res, 201, todo);       // the stored todo …
send(res, 201, data);       // … not the parsed body
```

`data` and `todo` look alike and are not the same object. `data` is what the
client sent — no id, no `done`, and whatever extra junk it felt like including.
`todo` is what now exists.

Answering with `data` produces a response that is *missing the only field the
client did not already have*, which is the id, and therefore the only field
worth sending back at all. Every subsequent request about that todo needs it.

### What a full-strength API would also send

```
HTTP/1.1 201 Created
Location: /todos/1
```

A `Location` header pointing at the thing you just made. It is one line —
`res.setHeader("Location", "/todos/" + todo.id)` — and this project skips it for
one honest reason: `/todos/1` does not exist until module 10, and a header
pointing at a 404 is worse than no header. It is in that module's stretch list.
""",
    """
```bash
$ curl -s -i -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
HTTP/1.1 201 Created
Content-Type: application/json

{"id":1,"title":"Buy milk","done":false}
```

`-i` is not optional here. The body would look exactly the same under a 200, and
the status line is the whole point of the step.
""",
    pitfalls=[
        "Answering 200. Nothing breaks and nothing tells you, which is exactly why it is worth getting right while there is one route to get right.",
        "Answering with `data` — the parsed body — instead of `todo`. The response then has no `id`, which is the only field in it the client did not already know.",
        "Sending 201 for a request that created nothing. A failed create is a 400 or a 404, never a 201 with an apology in the body.",
        "Adding a `Location` header now. It would point at `/todos/1`, which 404s until module 10 — a header that lies is worse than a header that is absent.",
        "Forgetting the `return` after the `send`. There is a 404 below it, and module 7's rule has not changed.",
    ],
    warmup=[
        _pq("What does 201 tell a client that 200 does not?",
            ["That something now exists which did not before — a create happened, rather than a request being answered",
             "That the response body is JSON",
             "That the request was idempotent",
             "Nothing; they are interchangeable for POST"],
            0,
            "It is the difference between \"here is your answer\" and \"I made "
            "something\", and it is visible without reading the body."),
    ],
    exercises=[
        _pex("todo-m9-created-1", "The right status",
             "The todo is in the store. Answer with it, under the status code "
             "that says it now exists.",
             _M9_FULL,
             "    send(res, 201, todo);",
             [("POST /todos {\"title\":\"Buy milk\"}\nGET /todos",
               '201 {"id":1,"title":"Buy milk","done":false}'
               '\n200 [{"id":1,"title":"Buy milk","done":false}]')],
             ["Module 5's helper, with today's status code.",
              "Not 200 — something was created.",
              "Send the stored todo, which is the only one of the two objects with an id.",
              "`send(res, 201, todo);`"]),
        _pfix("todo-m9-created-fix1", "A create that says OK",
              "Every field of every response is correct. Every todo is stored. "
              "The tests still fail, and the body is not the problem.\n\n"
              "Read the status line.",
              _m9("""async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = addTodo(data.title);
    send(res, 200, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _M9_FULL,
              [("POST /todos {\"title\":\"Buy milk\"}\nGET /todos",
                '201 {"id":1,"title":"Buy milk","done":false}'
                '\n200 [{"id":1,"title":"Buy milk","done":false}]')],
              ["Both routes answer 200. Only one of them created something.",
               "The listing route is right. The create route is not.",
               "`send(res, 201, todo);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why send back the stored todo rather than the parsed body?",
            ["The stored one has the id — the only field in the response the client did not already have",
             "The parsed body is not valid JSON",
             "`send` rejects the parsed body's type",
             "There is no difference; they are the same object"],
            0,
            "A response that echoes the request tells the client nothing. The id "
            "is the whole payload, and every later request about that todo needs "
            "it."),
        _pq("This project does not send a `Location: /todos/1` header on a create. "
            "Why not?",
            ["`/todos/1` does not exist until module 10, and a header pointing at a 404 is worse than no header",
             "`res.setHeader` does not exist in `node:http`",
             "A 201 may not carry headers",
             "The replayer would reject it"],
            0,
            "The header is one line and the project will add it — in module 10, "
            "where the address it names starts answering. Shipping a link to "
            "nowhere is a worse contract than shipping no link."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the id is the server's.
# ---------------------------------------------------------------------------

_M9_S3 = _pstep(
    "identity", "The id you did not send",
    "Who owns identity, and what goes wrong the moment the client does.",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"id":99,"title":"Sneaky"}'
{"id":1,"title":"Sneaky","done":false}
```

The client asked for id 99 and got id 1. Not an error — the request was
perfectly fine. The id simply was not the client's to choose.

### Why the store owns identity

An id is a promise the *server* makes: that this number refers to this row,
uniquely, for as long as it exists. The server is the only thing that can keep
that promise, because it is the only thing that can see every other row.

Let a client pick and all three of these are now your problem:

* two clients pick `1` and one silently overwrites the other
* a client picks `7`, which belongs to somebody else's todo
* a client picks `"; DROP TABLE`, and now identity is a string you did not
  validate

None of these are theoretical. "The client sends the id" is one of the most
common ways a small API grows a security hole.

### You ignore it — you do not reject it

Notice there is no check anywhere for a client-supplied id. There does not need
to be:

```ts
const todo = addTodo(data.title);
```

`addTodo` takes a title. There is no parameter an id could go into. A client can
send `id`, `done`, `createdBy`, `isAdmin` — anything it likes — and none of it
can reach the store, because the only thing this line takes out of the request
is one field.

**That is a design defending itself**, and it is worth naming as a technique:
the safest way to ignore input is to write code that has nowhere to put it.
Module 11 does exactly the same thing for `PATCH`, where the set of fields a
client may change is smaller than the set of fields a todo has.

### `done` is not the client's either

`{"title":"Buy milk","done":true}` creates an *unfinished* todo, because
`addTodo` sets `done: false` and does not look. A todo that arrives already
complete is not a create — it is a create plus an update, and those are two
requests. Module 11 is the second one.
""",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"id":99,"title":"Sneaky"}'
{"id":1,"title":"Sneaky","done":false}

$ curl -s -X POST localhost:3000/todos -d '{"title":"Real","done":true}'
{"id":2,"title":"Real","done":false}

$ curl -s localhost:3000/todos
[{"id":1,"title":"Sneaky","done":false},{"id":2,"title":"Real","done":false}]
```

Two requests that tried to set fields they do not own, and two todos that came
out exactly as the store defines them. Nothing had to say no.
""",
    pitfalls=[
        "Trusting `data.id`. Under `any` it compiles, and a client that omits the id produces a todo whose `id` is `undefined` — which `JSON.stringify` then drops from the response entirely, so the field does not appear at all.",
        "Trusting `data.done`. A create makes an unfinished todo. \"Created and already complete\" is two operations pretending to be one.",
        "Answering with `data` rather than the stored todo — the same bug wearing a different hat, since `data` has whatever id the client sent, or none.",
        "Adding an `id` parameter to `addTodo` \"just in case\". The moment it exists, something will pass a client's value to it.",
        "Validating a client-sent id instead of ignoring it. Ignoring is stronger: a check can be wrong, and a parameter that does not exist cannot be.",
    ],
    warmup=[
        _pq("A client posts `{\"id\":99,\"title\":\"Sneaky\"}`. What should the API "
            "do with the 99?",
            ["Ignore it — the id was never an input, so there is nothing to accept or reject",
             "Use it, since the client asked",
             "Return 400, because sending an id is an error",
             "Use it if no todo has that id yet"],
            0,
            "Nothing rejects it and nothing has to. `addTodo` takes a title; there "
            "is no route by which the 99 could reach the store."),
    ],
    exercises=[
        _pfix("todo-m9-identity-fix1", "The id that came from outside",
              "Post `{\"title\":\"Buy milk\"}` and the response comes back with no "
              "`id` field at all — `{\"title\":\"Buy milk\",\"done\":false}`. Post "
              "two and neither has one.\n\n"
              "The store is not being used. Something else is building the todo.",
              _m9("""async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo: Todo = { id: data.id, title: data.title, done: false };
    todos.push(todo);
    send(res, 201, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _M9_FULL,
              [("POST /todos {\"title\":\"Buy milk\"}\nPOST /todos {\"title\":\"Write tests\"}\nGET /todos",
                '201 {"id":1,"title":"Buy milk","done":false}'
                '\n201 {"id":2,"title":"Write tests","done":false}'
                '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]')],
              ["Where is the id coming from, and where should it come from?",
               "`data` is `any`, so `data.id` compiled — and the client never sent one.",
               "There is already a function that owns ids, counts them and pushes to the store.",
               "`const todo = addTodo(data.title);` — and delete the two lines that built it by hand."],
              difficulty="Easy"),
        _pfix("todo-m9-identity-fix2", "The response that is just the request",
              "`GET /todos` shows both todos stored correctly, with ids. But the "
              "`201` a client gets back has no `id` in it — it is the object they "
              "posted, handed straight back.",
              _m9("""async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = addTodo(data.title);
    send(res, 201, data);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _M9_FULL,
              [("POST /todos {\"title\":\"Buy milk\"}\nPOST /todos {\"title\":\"Write tests\"}\nGET /todos",
                '201 {"id":1,"title":"Buy milk","done":false}'
                '\n201 {"id":2,"title":"Write tests","done":false}'
                '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]')],
              ["Two objects are in scope and they are not the same one.",
               "One of them came from the client. The other came from the store.",
               "Only one of them has the id, and the id is the only reason to send a body at all.",
               "`send(res, 201, todo);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why does this route not need a check for a client-supplied id?",
            ["`addTodo` takes only a title, so there is nowhere for an id to go — the design ignores it structurally",
             "The client cannot send extra fields in JSON",
             "`JSON.parse` strips unknown fields",
             "`send` filters the response"],
            0,
            "The safest way to ignore input is to write code with nowhere to put "
            "it. A check can be wrong or forgotten; a parameter that does not "
            "exist cannot be."),
        _pq("A client posts `{\"title\":\"Buy milk\",\"done\":true}`. What is stored?",
            ["A todo with `done: false` — a create makes an unfinished todo, and `addTodo` does not look at `done`",
             "A todo with `done: true`, since the client asked",
             "A 400, because `done` is not allowed on a create",
             "A todo with `done` missing entirely"],
            0,
            "\"Created and already complete\" is a create plus an update wearing "
            "one request. The update is module 11."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the route, and the empty list.
# ---------------------------------------------------------------------------

_M9_S4 = _pstep(
    "route", "The route, and an empty list",
    "One `if` above the 404 — and the two lines that finally come out.",
    """
```ts
if (req.method === "POST" && url.pathname === "/todos") {
  const body = await readBody(req);
  const data = JSON.parse(body);
  const todo = addTodo(data.title);
  send(res, 201, todo);
  return;
}
```

Same path as the `GET`, different verb, and that is the second half of module
7's argument for matching on both: `/todos` is one address that answers two
completely different questions depending on how you knock.

Everything else in the handler is untouched. Adding a verb to an existing
resource is an insertion, exactly as adding a route was.

### Two deletions

```ts
addTodo("Buy milk");        // ← delete
addTodo("Write tests");     // ← delete
```

Those have been at the top of every program since module 7, and their entire
purpose was that `GET /todos` had nothing to show. It has something now: whatever
a client posted. Leave them in and every fresh process is born with two todos
nobody created, which will confuse you the first time you test a delete.

The `/echo` route goes too. It existed for one module and did its job.

### `[]` is a 200

```bash
$ curl -s -i localhost:3000/todos
HTTP/1.1 200 OK

[]
```

A brand-new process has no todos, and that is a **success**. The collection
exists; it is empty. 404 would mean "there is no such thing as a todo list here",
which is a completely different claim and one that would be wrong.

This trips people up often enough to be worth stating flatly: **an empty
collection is a 200 with an empty array in it.** A client that treats `[]` as an
error has the bug, not you. Module 10's 404 is for a single todo that does not
exist, which is genuinely a different situation.

### The shape of the whole route, for the last time

Read the four lines together and notice they are in the only order they could
be: you cannot parse before you have read, cannot store before you have parsed,
cannot answer before you have stored. Every remaining write route in this
project — `PATCH` in module 11, and both of them again once validation lands in
module 14 — is these four lines with something inserted between two of them.
""",
    """
```bash
$ curl -s localhost:3000/todos
[]

$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}

$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false}]

$ curl -s -i localhost:3000/todos/1
HTTP/1.1 404 Not Found
```

Four requests that tell the whole story of the module: it starts empty, a client
fills it, the list reflects it, and the todo still has no address of its own.
That last one is module 10.
""",
    pitfalls=[
        "Leaving the two `addTodo` seed calls in. Every restart is born with two todos nobody created, and the first thing that confuses is a delete test that leaves \"phantom\" rows behind.",
        "Matching only the path. `GET /todos` and `POST /todos` are the same address and different requests — this is the module where module 7's `&&` finally has two routes to keep apart.",
        "Putting the POST route below the 404. Unreachable, and the 404 has already answered by the time it runs.",
        "Answering 404 for an empty list. `[]` is a 200: the collection exists and has nothing in it.",
        "Forgetting the `return`. There is a 404 below, and a second `send` on a sent response throws.",
        "Reading the body before the route matches. A `GET` has no body, so it would work — and it would claim that reading input is part of routing. Module 8 made this argument; it does not change.",
    ],
    warmup=[
        _pq("A fresh server is asked for `GET /todos` before anything has been "
            "posted. What is the correct response?",
            ["200 with `[]` — the collection exists and is empty, which is a success",
             "404, because there are no todos",
             "204, because there is no content",
             "500, because the store was never initialised"],
            0,
            "An empty collection is not a missing one. 404 would claim there is no "
            "such thing as a todo list on this server, which is false."),
    ],
    exercises=[
        _pex("todo-m9-route-1", "The create route",
             "Add the route. Same path as the listing, different verb: read the "
             "body, parse it, store the title, and answer with what was stored.",
             _M9_FULL,
             """  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = addTodo(data.title);
    send(res, 201, todo);
    return;
  }""",
             [("GET /todos\nPOST /todos {\"title\":\"Buy milk\"}\nGET /todos\nPUT /todos {\"title\":\"No\"}",
               '200 []'
               '\n201 {"id":1,"title":"Buy milk","done":false}'
               '\n200 [{"id":1,"title":"Buy milk","done":false}]'
               '\n404 {"error":"not_found"}')],
             ["The condition is `POST` and `/todos` — module 7's shape.",
              "Four lines inside, in the only order they can be: read, parse, store, answer.",
              "The first test asks for the list before anything exists: `[]` with a 200.",
              "The fourth is a `PUT`, which no route claims — the verb half of the condition has to hold.",
              "It ends with `return;`, like every route in this handler."]),
        _pch("todo-m9-route-build", "The router with two verbs", "Medium",
             "Write the handler.\n\n"
             "* `GET /todos` → `200` with the store's array\n"
             "* `POST /todos` → `201` with the todo you created from the body's "
             "`title`\n"
             "* anything else → `404` with `{\"error\":\"not_found\"}`\n\n"
             "`readBody`, `send` and the store are already written above, and "
             "nothing seeds the store any more — the first test proves it.",
             _M9_FULL,
             _M9_HANDLER.rstrip("\n"),
             [("GET /todos\nPOST /todos {\"title\":\"Buy milk\"}\nPOST /todos {\"id\":99,\"title\":\"Sneaky\"}\nGET /todos\nDELETE /todos",
               '200 []'
               '\n201 {"id":1,"title":"Buy milk","done":false}'
               '\n201 {"id":2,"title":"Sneaky","done":false}'
               '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Sneaky","done":false}]'
               '\n404 {"error":"not_found"}')],
             ["The signature is `async` … `Promise<void>`, because the create route awaits.",
              "First line: `const url = new URL(req.url ?? \"/\", \"http://localhost\");`.",
              "Two routes, same path, different verbs — and the 404 last and unconditional.",
              "The third test sends `id: 99` and must come back `id: 2`. Pass the title to `addTodo` and the 99 has nowhere to go.",
              "Nothing seeds the store, so the first request must answer `200 []`."]),
    ],
    quiz=[
        _pq("Why are the two `addTodo` seed calls deleted in this module and not "
            "in module 7?",
            ["Until now nothing could put a todo in the store from outside, so an unseeded `GET /todos` could only ever return `[]`",
             "They were a bug that went unnoticed for two modules",
             "They break the `POST` route",
             "They were only ever there to make the tests pass"],
            0,
            "They were scaffolding with a stated expiry date — module 7 said so "
            "when it added them. This is the module where a client can create its "
            "own, so they come out."),
        _pq("`GET /todos` and `POST /todos` are the same path. What keeps them "
            "apart?",
            ["The verb half of each route's condition — this is the module where module 7's `&&` first has two routes to separate",
             "The order of the two `if`s",
             "`url.pathname` differs between them",
             "The request body"],
            0,
            "One address, two questions. That is what an HTTP verb is for, and it "
            "is why a route that matched on the path alone would have been a bug "
            "waiting for exactly this module."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M9_FINAL = _pch(
    "todo-m9-build", "Module 9 build — todos come from clients", "Medium",
    "Write the handler.\n\n"
    "* `GET /todos` → `200` with the store's array\n"
    "* `POST /todos` → `201` with the created todo\n"
    "* anything else → `404`\n\n"
    "Five test requests, and the last two are the interesting ones. "
    "`GET /todos/1` still 404s — a todo has no address of its own until module "
    "10. And `POST /todos notjson` comes back **500**, because `JSON.parse` "
    "throws and nothing in your handler catches it. That 500 is wrong — it "
    "blames the server for the client's mistake — and it is graded here so that "
    "you know it is wrong before module 14 fixes it.",
    _M9_FULL,
    _M9_HANDLER.rstrip("\n"),
    [("GET /todos\nPOST /todos {\"title\":\"Buy milk\"}\nPOST /todos {\"id\":99,\"title\":\"Sneaky\"}\nGET /todos\nGET /todos/1\nPOST /todos notjson",
      '200 []'
      '\n201 {"id":1,"title":"Buy milk","done":false}'
      '\n201 {"id":2,"title":"Sneaky","done":false}'
      '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Sneaky","done":false}]'
      '\n404 {"error":"not_found"}'
      '\n500 {"error":"server_error"}')],
    ["Two routes on the same path, separated by the verb; the 404 last.",
     "The create route is four lines: `await readBody`, `JSON.parse`, `addTodo(data.title)`, `send(res, 201, todo)`.",
     "Pass the title, not the object — that is why the `id: 99` in the third request comes back as `2`.",
     "Nothing seeds the store any more, so the first request is `200 []`.",
     "You are not meant to handle the last one. `JSON.parse` throws, the replayer's "
     "boundary answers 500, and modules 14 and 16 are where that becomes honest."],
)


_TODO_MODULES.append(_pmod(
    key="todo-create", number=9, phase="crud",
    title="POST /todos — create",
    what="parse the body, store it, answer 201",
    goal="Let a client create a todo, and give it the id it did not send.",
    why=_M9_WHY,
    est_minutes=50,
    builds_on=["todo-store", "todo-json", "todo-routing", "todo-body"],
    concepts=["JSON.parse", "any at the boundary", "201 Created",
              "server-owned identity", "empty collections"],
    deliverable="A todo list whose contents came from outside the process — and "
                "the first honest look at what `any` costs.",
    objectives=[
        "Turn a request body into a value with `JSON.parse`, and say what type it hands back and why",
        "Explain why a malformed body is a 500 today, why that is the wrong answer, and which two modules fix it",
        "Choose 201 over 200 for a create, and say what a client learns from the difference",
        "Answer with the stored todo rather than the parsed body, and say which field makes that matter",
        "Explain why the client's `id` is ignored rather than rejected, and how the store's design makes that automatic",
        "Say why `GET /todos` on a fresh server is `200 []` and not a 404",
        "Add a second verb to an existing path without touching the route already there",
    ],
    endpoints=[
        _pep("POST", "/todos", "Create a todo from the body's title",
             '{"title":"Buy milk"}', "Todo, with the id you assigned",
             "201 · 500 on bad JSON"),
        # The response wording is module 7's, unchanged — only the purpose is
        # reworded, which the Handbook's contract index correctly does not count
        # as a revision. The route itself has not moved since module 7.
        _pep("GET", "/todos", "List every todo — `[]` on a fresh server", "",
             "[Todo] — a bare array until module 18", "200"),
        # RETIREMENT, declared in the data: an em-dash status is how a module
        # says a route is gone, so the contract index stops advertising it.
        # /echo was module 8 scaffolding with a stated expiry, and this is it.
        _pep("POST", "/echo", "Retired — module 8 scaffolding, replaced by POST /todos",
             "", "—", "—"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M9_BRIEF,
    syntax=_M9_SYNTAX,
    steps=[_M9_S1, _M9_S2, _M9_S3, _M9_S4],
    final_build=_M9_FINAL,
    acceptance=[
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"Buy milk\"}'` returns 201 and `{\"id\":1,\"title\":\"Buy milk\",\"done\":false}`.",
        "A second create returns id 2 — the counter is the store's, and it survives across requests.",
        "`curl -s -X POST localhost:3000/todos -d '{\"id\":99,\"title\":\"Sneaky\"}'` returns an id you assigned, not 99.",
        "`curl -s -X POST localhost:3000/todos -d '{\"title\":\"x\",\"done\":true}'` returns `done: false` — a create makes an unfinished todo.",
        "`curl -s -i localhost:3000/todos` on a fresh server returns 200 with `[]`, not 404.",
        "`curl -s -i -X POST localhost:3000/todos -d 'not json'` returns 500 today — and you can say why, and which module makes it a 400.",
        "The two `addTodo` seed calls and the `/echo` route are gone from your file.",
        "The create route answers with the stored todo, not the parsed body.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s localhost:3000/todos                     # [] — a 200, not a 404
curl -s -i -X POST localhost:3000/todos -d '{"title":"Buy milk"}'      # 201
curl -s -X POST localhost:3000/todos -d '{"title":"Write tests"}'
curl -s localhost:3000/todos                     # both, with ids 1 and 2

# the fields that are not the client's to set
curl -s -X POST localhost:3000/todos -d '{"id":99,"title":"Sneaky"}'   # id is 3
curl -s -X POST localhost:3000/todos -d '{"title":"Nope","done":true}' # done is false
```

Then look at the three answers this API currently gets wrong. None of them are
bugs in what you wrote; all three are the shape of what is missing:

```bash
curl -s -i -X POST localhost:3000/todos -d 'not json'
#   → 500 {"error":"server_error"}
#     The client sent junk and the server took the blame. Module 14 → 400.

curl -s -i -X POST localhost:3000/todos -d '{}'
#   → 201 {"id":4,"done":false}   … a todo with no title, and no complaint.
#     `data.title` was undefined, `any` said nothing, JSON.stringify dropped it.
#     Module 13 makes the type honest; module 14 makes it a 400.

curl -s -i -X POST localhost:3000/todos -d '{"title":""}'
#   → 201 with an empty title. Same story, no error anywhere.
```

Three requests, three wrong answers, zero crashes. That is what `any` at a
boundary buys you: not failures, but *quiet* wrong answers — which is why the
next phase of this project exists at all.
""",
    reference="""// server.ts — module 9
//
// The first module where data in the application came from outside it.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

// The store owns identity. `addTodo` takes a TITLE — there is no parameter a
// client-supplied id could go into, which is why the handler below needs no
// check for one. The safest way to ignore input is to have nowhere to put it.
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

// Module 8's reader, unchanged, and unchanged for the rest of the project.
function readBody(req: IncomingMessage): Promise<string> {
  return new Promise<string>((resolve) => {
    req.setEncoding("utf8");
    let body = "";
    req.on("data", (chunk: string) => {
      body = body + chunk;
    });
    req.on("end", () => {
      resolve(body);
    });
  });
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");

  // An empty store answers 200 with []. The collection exists and has nothing
  // in it; 404 would claim there is no such thing as a todo list here.
  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  // Same path as the route above, different verb. This is the module where
  // module 7's `&&` finally has two routes to keep apart.
  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);

    // THE HOLE IN THE TYPES, named rather than hidden. JSON.parse returns
    // `any`, so from here to the end of the route the compiler is not checking
    // anything: data.title, data.nonsense and data.a.b.c are all fine by it.
    //
    // It also THROWS on text it cannot read, and nothing here catches that —
    // a malformed body becomes a rejected promise, the replayer's boundary
    // turns it into a 500, and the client is told the fault was ours. All of
    // that is deliberate and all of it is temporary:
    //
    //     module 13  the type stops being `any`
    //     module 14  bad input becomes a 400 naming the field
    //     module 16  the boundary becomes one you wrote
    const data = JSON.parse(body);

    // The title, not the object. A client may send id, done, isAdmin — none of
    // it can reach the store, because this is the only field taken out.
    const todo = addTodo(data.title);

    // 201, not 200: something now exists that did not before. And the STORED
    // todo, not `data` — only the stored one has the id, which is the only
    // field in this response the client did not already have.
    //
    // A fuller API would add `Location: /todos/1` here. This one does not yet,
    // because /todos/1 does not answer until module 10 and a header pointing at
    // a 404 is worse than no header.
    send(res, 201, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}

// The two seed addTodo calls that lived here since module 7 are GONE — a client
// can create its own now — and so is module 8's /echo route.

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Post `{}` and then `{\"title\":\"\"}`. Both give you a 201. Write down what you think each *should* return, then check yourself against module 14 when you get there.",
        "Add `res.setHeader(\"Location\", \"/todos/\" + todo.id)` before the `send`, then `curl -i` a create and follow the link. It 404s — which is exactly why the project waits until module 10 to add it for real.",
        "Post a body with a huge `title` — 100 KB of it. It works, and nothing anywhere sets a limit. Note where you would put one, and why it belongs before `JSON.parse` rather than after.",
        "Log `JSON.stringify(data)` right after the parse and post `{\"title\":\"x\",\"extra\":{\"deeply\":{\"nested\":true}}}`. Everything the client sent is sitting in your process; only one field of it reached the store.",
        "Make `addTodo` take an optional id and use it when present. Then write the two-sentence argument for why you should not, and revert. Doing it and undoing it is worth more than never doing it.",
        "Count how many of this module's six acceptance checks you could have got wrong without a single test failing. The answer is most of them, which is what module 14 is about.",
    ],
    glossary=[
        _pgloss("JSON.parse", "Text → value. The mirror of `JSON.stringify`. Returns `any` and throws on input it cannot read."),
        _pgloss("any", "TypeScript's \"stop checking\". Every property access on an `any` is legal and every result is also `any`."),
        _pgloss("boundary", "Any point where data enters your program from outside — a request body, a file, another service. Where types stop being guarantees."),
        _pgloss("201 Created", "The resource now exists and the body is it. What a POST that created something answers with."),
        _pgloss("server-owned identity", "The rule that ids are assigned by the store, never accepted from a client, because only the store can see every other row."),
        _pgloss("empty collection", "A list with nothing in it. A 200 with `[]` — not a 404, which would claim the collection itself does not exist."),
        _pgloss("idempotent", "Doing it twice is the same as doing it once. `POST /todos` is not: two calls make two todos, which is why it is not a `PUT`."),
    ],
    cheatsheet="""
```ts
if (req.method === "POST" && url.pathname === "/todos") {
  const body = await readBody(req);      // module 8 — text
  const data = JSON.parse(body);         // text → value, and `any`
  const todo = addTodo(data.title);      // the field, not the object
  send(res, 201, todo);                  // created; the STORED todo
  return;
}
```

**The order is forced:** cannot parse before reading, cannot store before
parsing, cannot answer before storing.

| Request | Answer | Why |
|---|---|---|
| `{"title":"Buy milk"}` | `201 {"id":1,…}` | the happy path |
| `{"id":99,"title":"x"}` | `201 {"id":1,…}` | the id was never an input |
| `{"title":"x","done":true}` | `201 {…,"done":false}` | a create makes an unfinished todo |
| `{}` | `201` with no title | ⚠️ wrong. `any` said nothing. → module 14 |
| `{"title":""}` | `201` with an empty title | ⚠️ wrong. → module 14 |
| `not json` | `500` | ⚠️ wrong — blames the server. → 14 and 16 |
| `GET /todos`, fresh | `200 []` | an empty collection is a success |

| Symptom | Cause |
|---|---|
| title is the whole JSON body | stored `body` instead of `data.title` |
| response has no `id` | answered with `data`, or built the todo by hand from `data.id` |
| create answers 200 | it should be 201 |
| fresh server already has todos | the module-7 seed calls are still there |
| every POST is a 500 | the body is not JSON — check what the client actually sent |
""",
    self_check=[
        "Can you say what type `JSON.parse` returns, and what that means for the next five lines?",
        "Can you explain why a malformed body is a 500 today, why that is the wrong status, and which module changes it?",
        "Can you say what a client learns from a 201 that it would not learn from a 200?",
        "Can you say which of `data` and `todo` to send back, and name the field that decides it?",
        "Can you explain why there is no check anywhere for a client-supplied id, and why that is stronger than having one?",
        "Can you say what `GET /todos` returns on a fresh server, with the status code, and why 404 would be wrong?",
        "Can you name three requests this route currently accepts that it should not?",
    ],
    review=[
        _pq("What does `JSON.parse` return, and what does that cost you?",
            ["`any` — every property access on the result is legal and unchecked, so a typo or a missing field is silent",
             "`object`, which is safe to index",
             "`unknown`, which must be narrowed before use",
             "The declared type of the variable it is assigned to"],
            0,
            "`unknown` is the answer you want and it is module 13's. Today the "
            "hole is named and used, which is the only way that module lands."),
        _pq("A client posts `{\"id\":42,\"title\":\"Read this\"}`. What is stored?",
            ["A todo with the store's next id — 42 never reaches `addTodo`, which takes only a title",
             "A todo with id 42",
             "A 400, because id is not an accepted field",
             "A todo with id 42 if no todo has it yet"],
            0,
            "And nothing rejects it: there is no parameter it could travel "
            "through. That is a design ignoring input structurally rather than by "
            "checking for it."),
        _pq("Why 201 rather than 200 for a successful create?",
            ["201 says something now exists that did not before — a client can tell a create from a plain answer without reading the body",
             "200 is reserved for GET",
             "201 is required whenever the response has a body",
             "They are equivalent; 201 is a style preference"],
            0,
            "Status codes are the part of the response a client can act on "
            "without parsing anything. Spending them properly is most of what API "
            "design is."),
        _pq("`GET /todos` on a server where nothing has been posted. Status and body?",
            ["200 and `[]` — the collection exists and is empty",
             "404 and an error, because there are no todos",
             "204 and no body",
             "200 and `null`"],
            0,
            "404 for an empty list claims the collection itself does not exist. "
            "Module 10's 404 is for one todo that is missing, which is a genuinely "
            "different statement."),
        _pq("The create route answers `send(res, 201, data)` instead of "
            "`send(res, 201, todo)`. What breaks?",
            ["The response has no id, so the client cannot refer to the thing it just made",
             "Nothing — they are the same object",
             "The todo is not stored",
             "The status code becomes wrong"],
            0,
            "The store is fine; the answer is useless. The id is the only field "
            "in that response the client did not already have."),
        _pq("Which two modules make `POST /todos` with a malformed body stop "
            "being a 500?",
            ["14, which makes bad input a 400 naming the field, and 16, which makes the boundary one you wrote",
             "10 and 11",
             "13 alone",
             "None; a 500 is correct for unparseable input"],
            0,
            "13 makes the *type* honest, 14 makes the *status* honest, and 16 "
            "makes the boundary yours. Today all three holes are open and named."),
    ],
    milestone="Your API accepts data. The list is no longer something you typed "
              "into the source — it is whatever clients have put there, with ids "
              "you assigned and fields you chose to honour. It also accepts "
              "three things it should not, and you can name all three.",
))
