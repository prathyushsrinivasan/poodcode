# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 7 — Routing, and 404 as the default.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# INTRODUCES NO NEW GATED SYNTAX, deliberately. Everything this module needs —
# `if`, `===`, `&&`, `return`, the store from modules 2-3, `send` from 5, the
# parse from 6 — is already taught. That is the point: the capstone of a phase
# should be composition, not vocabulary. If a module 7 rewrite finds itself
# reaching for a new token, the module before it did too little.
#
# THE PHASE PAYOFF: this is the first module where the learner's OWN data goes
# over HTTP. Modules 1-3 built a store nothing could reach; 4-6 built a server
# that could not reach the store. This is the wire between them, and it is
# roughly eight lines, which is the argument for having built them separately.
#
# WHY THE STORE IS SEEDED AT BOOT: there is no POST until module 9, so an empty
# array is all `GET /todos` could return. Two `addTodo` calls before `listen`
# give the route something to show, and they are the same two calls module 2's
# program made — the learner recognises them.
#
# NO TIMEOUT-BASED EXERCISE, on purpose. The signature bug of this module — a
# handler with no fall-through — HANGS rather than failing, so grading it would
# cost a 25s Python timeout plus a 30s Rust one for a lesson module 4 step 3
# already taught with a one-line `res.end()` fix. It is taught here in the
# warm-up, the pitfalls and the manual test (where you break it on purpose and
# watch curl sit there) instead. Both graded `fix`es fail fast and loudly.
#
# THE 405 QUESTION is raised and answered "no" in step 4. `POST /todos` before
# module 9 exists is arguably a 405, and a router that answers 404 for it is
# making a simplification. Saying so is cheaper than a learner finding the gap.
# ---------------------------------------------------------------------------

_M7_WHY = (
    "You have a store nothing can reach and a server that has never touched it. "
    "Module 6 left the handler able to say `this was a GET for /todos` and then "
    "answer 404 anyway, which is the software equivalent of reading a letter "
    "aloud and filing it in the bin. One `if` closes the gap — and where you "
    "put the 404 that is already there decides whether the next thirteen "
    "modules add routes safely or break something every time."
)

_M7_BRIEF = """
### The whole module in one line

Answer `GET /todos` from your store, and let everything else fall through to the
404 you already wrote.

### Two halves that have never met

```
modules 1-3:   a store — add, list, find          nothing can reach it
modules 4-6:   a server that knows what it was asked   it never asks the store
```

This module is the wire, and it is about eight lines. That it is only eight
lines is the argument for having built the two halves separately: neither one
had the other in the way while it was being got right.

### A route is a method AND a path

```ts
if (req.method === "GET" && url.pathname === "/todos") {
  send(res, 200, todos);
  return;
}
send(res, 404, { error: "not_found" });
```

Both halves of that condition are load-bearing. Drop the method and
`DELETE /todos` returns your list. Drop the path and `GET /anything` does.
`&&`, never `||` — a route that matches too much is worse than one that matches
nothing, because nothing is obvious and too much is not.

### The 404 goes last, and it is not a branch

This is the design decision of the module.

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (/* route 1 */) { …; return; }
  if (/* route 2 */) { …; return; }
  if (/* route 3 */) { …; return; }

  send(res, 404, { error: "not_found" });     // ← the default. Not an else.
}
```

Written this way the router **cannot forget its 404**, because the 404 is what
happens when you write nothing. Compare the shape people reach for first:

```ts
if (a) { … } else if (b) { … } else if (c) { … }
```

That one has no default at all, and a request matching none of the three does
not 404 — it *hangs*, exactly as module 4 warned, with no error anywhere.
Adding a fourth route to the first shape is one `if`. Adding one to the second
means finding the end of a chain and remembering an `else` you cannot see from
where you are typing.

You already wrote the default in module 5, when your server answered 404 to
everything. You are not adding a fall-through today. You are adding a route
*above* one you already have.

### `return` after every `send`

Module 4 told you to make this a habit while there was one path and it could not
possibly matter. Now there are two, and it does: without the `return`, a matched
route sends its response and then carries on to the 404, which tries to set
headers on a response that has already gone. That does not produce a wrong
answer — it throws, and takes your server with it.

### What `GET /todos` returns

A bare JSON array:

```
$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```

Not `{"items":[…],"total":2}`. That envelope arrives in module 18, and it is the
one deliberate breaking change in this project — worth a paragraph there, and
worth not pre-empting here.
"""

_M7_SYNTAX = [
    _syn(
        'if (req.method === "GET" && url.pathname === "/todos") { … }',
        "A route: one verb and one path, both of which must match. Two "
        "comparisons joined with `&&`.",
        """
if (req.method === "GET" && url.pathname === "/todos") {
  send(res, 200, todos);
  return;
}
""",
        "`||` here is not a typo you will spot by reading — it compiles, and it "
        "makes `GET /anything` and `DELETE /todos` both match. Check the failing "
        "request, not the passing one.",
    ),
    _syn(
        "return;",
        "Stop the handler. Goes immediately after every `send`, so that a route "
        "which has answered cannot fall into the one below it.",
        """
if (req.method === "GET" && url.pathname === "/todos") {
  send(res, 200, todos);
  return;                    // ← without this, the 404 below also runs
}
send(res, 404, { error: "not_found" });
""",
        "Forgetting it does not send a wrong response. It sends the right one and "
        "then throws `ERR_HTTP_HEADERS_SENT` trying to send a second — which "
        "brings the process down rather than failing one request.",
    ),
    _syn(
        "send(res, 200, todos)",
        "Send the store's array as the response body. `todos` is a `Todo[]`, and "
        "an array is an object, so module 5's helper takes it unchanged.",
        """
send(res, 200, todos);
// [{"id":1,"title":"Buy milk","done":false}]
""",
        "A bare array, not `{ todos: todos }` and not `{ items: […] }`. The "
        "envelope is module 18, and it is a deliberate breaking change there "
        "rather than a shape you drifted into here.",
    ),
    _syn(
        "const todos: Todo[] = []; function addTodo(title: string): Todo { … }",
        "The store from modules 2 and 3, unchanged. This module is the first "
        "thing outside it that ever reads it.",
        "",
        "There is no `POST` until module 9, so the program seeds itself with two "
        "`addTodo` calls before it starts listening — otherwise the route works "
        "perfectly and returns `[]`.",
        recap=True,
    ),
    _syn(
        'const url = new URL(req.url ?? "/", "http://localhost");',
        "Module 6's parse. `url.pathname` is the path with any query string "
        "removed — which is why `/todos?done=true` still matches `/todos`.",
        "",
        "Route on `url.pathname`, never on `req.url`. The raw target carries the "
        "query string and stops matching the moment anyone adds one.",
        recap=True,
    ),
    _syn(
        "function send(res: ServerResponse, status: number, data: object): void { … }",
        "Module 5's helper. Every route answers through it, which is why adding "
        "a route is one `if` and not one `if` plus two lines of header handling.",
        "",
        "",
        recap=True,
    ),
]

_M7_S1 = _pstep(
    "match", "One route",
    "A verb and a path, joined by `&&` — and the `return` that stops it there.",
    """
Module 6 left you here:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  send(res, 404, { error: "not_found" });
}
```

Everything a route needs is in scope. Put one `if` between those two lines:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
```

That is routing. There is no more to it than that — a framework's router is this
`if` with a lookup table in front of it, and you will build that table yourself
in module 20.

### Both halves of the condition

**`req.method === "GET"`** — the verb. Module 6 established that this comparison
needs no narrowing even though `req.method` is `string | undefined`: a request
with no method is not a GET, which is the right answer.

**`url.pathname === "/todos"`** — the path, with the query string already
stripped by module 6's parse. `GET /todos?done=true` matches this and
`GET /todos` matches this, which is what you want and is exactly what a
`req.url === "/todos"` comparison would have got wrong.

**`&&`, not `||`.** With `||` the route matches when *either* half is true:
`GET /` returns your todo list, and so does `DELETE /todos`. It compiles, it
passes the test you would write first, and you find it when a client deletes
something and gets a 200 back.

### The `return` is not optional any more

Module 4 asked you to write `return` after every `res.end` while there was one
path and it genuinely could not matter. There are two now.

Without it, a matching request runs `send(res, 200, todos)` — which writes the
whole response and closes it — and then keeps going, falls out of the `if`, and
runs `send(res, 404, …)`, which tries to write a status line onto a response
that has already gone. Node throws `ERR_HTTP_HEADERS_SENT`.

Notice what that is *not*: it is not a wrong answer. The client already got its
200 and its list. It is your server crashing a moment later, on a request that
looked like it worked.
""",
    """
```bash
$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]

$ curl -s -i localhost:3000/nonsense
HTTP/1.1 404 Not Found
{"error":"not_found"}

$ curl -s -i -X DELETE localhost:3000/todos
HTTP/1.1 404 Not Found
```

Three requests, two different answers, and the third is the one worth checking:
the path matches and the verb does not, so it must not return your list.
""",
    pitfalls=[
        "`||` where you meant `&&`. The route then matches on either half alone — `GET /anything` and `DELETE /todos` both return the list. Nothing about the code looks wrong; only a request you did not think to try shows it.",
        "Forgetting the `return`. The response goes out correctly and then the fall-through throws `ERR_HTTP_HEADERS_SENT` on a response that no longer exists, which takes the process down rather than failing one request.",
        "Routing on `req.url` rather than `url.pathname`. Correct until the first query string, then a route you handle starts 404ing with nothing in the logs.",
        "Comparing `\"/todos/\"` and expecting `\"/todos\"` to match. `pathname` does not normalise the trailing slash, and neither does `===`.",
        "Putting the route below the 404. It is unreachable, and because the 404 already answered, the route's `send` throws on top of it.",
    ],
    warmup=[
        _pq("The route condition is written with `||` instead of `&&`. Which request "
            "shows the bug first?",
            ["`DELETE /todos` — the path matches, so the whole condition is true and the list comes back with a 200",
             "`GET /todos` — it stops matching",
             "`GET /nonsense` — it throws",
             "None; `||` and `&&` are equivalent for two `===` comparisons"],
            0,
            "`||` is true when either side is. So every GET matches whatever the "
            "path, and every request to `/todos` matches whatever the verb. The "
            "request you would test first — `GET /todos` — works perfectly."),
    ],
    exercises=[
        _pex("todo-m7-match-1", "The condition",
             "Route `GET /todos` to the store. Match on the verb and the path — both "
             "of them — using the parsed `url`, not the raw target.",
             _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");
addTodo("Write tests");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
             'req.method === "GET" && url.pathname === "/todos"',
             [("GET /todos\nGET /\nDELETE /todos\nGET /todos?done=true",
               '200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]'
               '\n404 {"error":"not_found"}'
               '\n404 {"error":"not_found"}'
               '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]')],
             ["Two comparisons, and both have to hold.",
              "The verb comes off `req`; the path comes off the parsed `url`, not the raw target.",
              "Joined with `&&` — with `||` the fourth request would still pass and the third would not.",
              '`req.method === "GET" && url.pathname === "/todos"`']),
        _pfix("todo-m7-match-fix1", "The route that matches too much",
              "`GET /todos` works. So does `GET /`, and so does `DELETE /todos` — all "
              "three come back with the full list and a 200.\n\n"
              "One character.",
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" || url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              [("GET /todos\nGET /\nDELETE /todos",
                '200 [{"id":1,"title":"Buy milk","done":false}]'
                '\n404 {"error":"not_found"}'
                '\n404 {"error":"not_found"}')],
              ["A route is a verb AND a path. Read the operator joining them.",
               "`||` is true when either side is, so every GET matches and every request to `/todos` matches.",
               '`req.method === "GET" && url.pathname === "/todos"`'],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What happens on a matching request if you forget the `return` after "
            "`send(res, 200, todos)`?",
            ["The client gets its 200 and the list, and then the handler throws `ERR_HTTP_HEADERS_SENT` on the fall-through",
             "The client gets a 404 instead of the list",
             "The client gets both responses, one after the other",
             "Nothing — `send` returns, so the handler stops"],
            0,
            "The response was already written and closed. Execution carries on into "
            "the 404, which tries to set a status line on something that has gone. "
            "The request looked fine from the client's side; the damage is on yours."),
    ],
)

_M7_S2 = _pstep(
    "store", "Your data, over HTTP",
    "The wire between phase 1 and phase 2 — and the response shape you are promising.",
    """
```ts
send(res, 200, todos);
```

One line, and it is the point of the last six modules. `todos` is the array from
module 2. `send` is the helper from module 5. Neither needed changing.

### Why `todos` can be passed straight in

Module 5 typed `send`'s third parameter `object`, and an array is an object in
JavaScript. So a `Todo[]` goes in unchanged, `JSON.stringify` turns it into a
JSON array, and the client gets:

```
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```

Had `send` been typed `data: Todo`, this line would need the signature changing.
That is the module-5 decision paying for itself for the first time.

### Seeding the store, and why

There is no `POST` until module 9, so a fresh process has an empty array and
`GET /todos` correctly returns `[]`. Correct is not the same as useful while you
are looking at it, so seed it before you start listening:

```ts
addTodo("Buy milk");
addTodo("Write tests");

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
```

Those are the same two calls module 2's program made. They go **before**
`listen`, not inside the handler — seeding per request would add two todos every
time anyone asked for the list.

Delete them in module 9, when the client can create its own.

### A bare array is a promise

You are returning `[…]`, not `{"todos":[…]}` and not `{"items":[…],"total":2}`.

All three are defensible. What is not defensible is drifting between them, so
pick the simple one now and change it deliberately later: **module 18 replaces
this with `{"items":[…],"total":n}`**, and does it as a stated breaking change
with an argument for why envelopes exist. A response shape is a contract, and
the useful skill is noticing when you are changing one.

### Reading the store, not copying it

`send(res, 200, todos)` passes the array itself. Nothing here mutates it, so
that is fine — and it stays fine right up to module 17, where filtering must
produce a *new* array rather than reordering or emptying the one the store owns.
`.filter` and `.sort` differ on exactly that point, which is why they are eleven
modules apart.
""",
    """
```bash
$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]
```

Two todos you added in code, over HTTP, from a store you wrote in module 2 and
a server you wrote in module 4. Then comment out the two `addTodo` calls,
restart, and confirm you get `[]` — an empty list is a successful 200, not a
404. There is nothing wrong with having no todos.
""",
    pitfalls=[
        "Seeding inside the handler. Two more todos per request, and the list grows every time anyone looks at it.",
        "Answering 404 when the list is empty. An empty collection is a 200 with `[]` — the resource exists, it just has nothing in it. 404 is for an address, and `/todos` is a real address.",
        "Wrapping the array: `send(res, 200, { todos: todos })`. It is a different contract, and module 18 is where the envelope arrives on purpose.",
        "`send(res, 200, todos.length)` or any other non-object. `data: object` rejects a number, which is module 5's typing doing its job.",
    ],
    exercises=[
        _pex("todo-m7-store-1", "Serve the list",
             "The route matches. Answer it with the store's array and a 200.",
             _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");
addTodo("Write tests");
addTodo("Ship it");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
             "    send(res, 200, todos);",
             [("GET /todos",
               '200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false},'
               '{"id":3,"title":"Ship it","done":false}]')],
             ["Module 5's helper: the response, the status, the data.",
              "The array itself — `send` takes an `object`, and an array is one.",
              "`    send(res, 200, todos);`"]),
        _pfix("todo-m7-store-fix1", "The envelope nobody asked for",
              "This wraps the list in an object. It is valid JSON and it is a "
              "perfectly reasonable API design — it is just not the one this project "
              "promised for the next eleven modules, and a client written against the "
              "contract will read `[0]` and find nothing.\n\n"
              "Send the array itself. Module 18 is where the envelope arrives, "
              "deliberately.",
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");
addTodo("Write tests");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, { todos: todos });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");
addTodo("Write tests");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              [("GET /todos\nGET /nope",
                '200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]'
                '\n404 {"error":"not_found"}')],
              ["The status is right and the data is right; the shape around it is not.",
               "`GET /todos` returns a bare JSON array until module 18.",
               "`send(res, 200, todos);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("`GET /todos` on a server with no todos in it. What should it answer?",
            ["200 with `[]` — the collection exists and is empty",
             "404, because there is nothing to return",
             "204, because there is no content",
             "400, because the client should not ask for an empty list"],
            0,
            "404 is about the address, and `/todos` is a real address. An empty "
            "collection is a successful answer to a well-formed question, and a "
            "client that has to treat \"empty\" and \"missing\" the same way ends "
            "up with a bug in it."),
        _pq("Why can `send(res, 200, todos)` pass a `Todo[]` to a parameter typed "
            "`object`?",
            ["An array is an object in JavaScript, which is exactly why module 5 chose that type",
             "TypeScript widens arrays to `object` implicitly at call sites",
             "`send` has an overload for arrays",
             "It cannot — this line needs a cast"],
            0,
            "That decision is paying off here for the first time. Had `data` been "
            "typed `Todo`, serving the list would mean changing the signature — and "
            "again in module 14 for error records."),
    ],
)

_M7_S3 = _pstep(
    "fallthrough", "404 as the default",
    "The last line of the handler, not an `else` — so the router cannot forget it.",
    """
Your handler now has this shape, and it is the shape it keeps until module 20:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (/* route */) { …; return; }

  send(res, 404, { error: "not_found" });
}
```

**Routes first, each returning. The 404 last, unconditional.**

### Why not `else`

The obvious alternative:

```ts
if (req.method === "GET" && url.pathname === "/todos") {
  send(res, 200, todos);
} else {
  send(res, 404, { error: "not_found" });
}
```

which is correct today, with one route. Now add a second:

```ts
if (a) { … } else if (b) { … } else { 404 }
```

and a third, and a fourth. Every addition means finding the end of a chain you
can no longer see from where you are typing, and the day someone appends
`else if (e) { … }` after the `else` — or writes a new `if` below the whole
thing — the default silently stops being last.

The flat form has none of that. A route is an `if` with a `return`; you add one
by typing one, anywhere above the last line, and the default is still the last
line because it always was.

### What "forgetting the 404" actually looks like

Not a 404 with the wrong body. Not a 500. Module 4 told you: a path through the
handler that never calls `res.end` means the client waits, and nothing anywhere
logs a reason.

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");
  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }
  // ← nothing here
}
```

`curl localhost:3000/nonsense` sits there. Your server is fine. The request is
never coming back. Try it — it is in this module's manual test, and it is worth
seeing once from the outside.

That is the argument for writing the default before the routes, which is what
module 5 did without telling you why: you cannot forget a line you wrote two
modules ago and never removed.

### The order of the routes

With the routes you have, order does not matter — the conditions are mutually
exclusive, so at most one can be true.

That stops being free in module 10, when `/todos/:id` arrives and there is a
route that matches a *family* of paths. Two routes that can both match must be
ordered most-specific-first, and the module says so at the point it becomes
true. For now: routes above, default below, and do not think about it further.
""",
    """
```bash
$ curl -s -i localhost:3000/nonsense
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error":"not_found"}

$ curl -s -i -X POST localhost:3000/todos
HTTP/1.1 404 Not Found
```

Both fall through, and the second is the interesting one: the path is real and
the verb is not handled yet. Module 9 adds it, and the only change is one more
`if` above the last line.

Then delete the last line, restart, and run `curl localhost:3000/nonsense`. It
hangs. Put it back.
""",
    pitfalls=[
        "Using `else` for the 404. Correct with one route and a trap with four — the default is only last until somebody appends to the chain, and nothing warns you when it stops being.",
        "Leaving a path with no response at all. That is a hang, not a 404: no status, no error, no log line, and a client that waits until it gives up.",
        "Putting the fall-through above the routes. It answers first, and then the route's `send` throws on a response that has already gone.",
        "Answering 404 from inside a route's `else` as well as at the bottom. Two 404s that can drift apart — one place, at the end.",
    ],
    warmup=[
        _pq("A handler routes `GET /todos` and has no line after the `if`. What does "
            "`curl localhost:3000/nonsense` do?",
            ["Hangs — no response is ever written, so nothing closes the request",
             "Returns 404, because that is Node's default for an unhandled path",
             "Returns an empty 200",
             "Returns 500, because the handler fell off the end"],
            0,
            "Node has no idea what your routes are. A handler that returns without "
            "writing to `res` leaves the response open forever. This is module 4's "
            "missing `res.end`, wearing a router."),
    ],
    exercises=[
        _pch("todo-m7-fallthrough-1", "Route, then default", "Easy",
             "Write the body of the handler below the URL parse.\n\n"
             "Route `GET /todos` to the store with a 200, and let everything else — "
             "any other path, any other verb — fall through to a 404 with the body "
             "`{\"error\":\"not_found\"}`.\n\n"
             "Routes first, each stopping. The default last, and unconditional.",
             _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
             """  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  send(res, 404, { error: "not_found" });""",
             [("GET /todos\nGET /\nGET /todos/1\nPOST /todos {\"title\":\"Ship it\"}\nDELETE /todos/1",
               '200 [{"id":1,"title":"Buy milk","done":false}]'
               '\n404 {"error":"not_found"}\n404 {"error":"not_found"}'
               '\n404 {"error":"not_found"}\n404 {"error":"not_found"}')],
             ["One `if` for the route, then one unconditional `send` below it.",
              "The condition needs both the verb and the path, joined with `&&`.",
              "`return` immediately after the route's `send`, or the 404 runs too.",
              "The 404 is not in an `else` — it is the last statement of the handler, "
              "reached by anything that did not return above it."]),
    ],
    quiz=[
        _pq("Why does this project write the 404 as the handler's last statement "
            "rather than as an `else`?",
            ["Adding a route is then a single `if` anywhere above it, and the default cannot stop being last",
             "`else` blocks cannot contain a `send` call",
             "It runs faster, because there is no branch to evaluate",
             "TypeScript narrows `req.method` better without an `else`"],
            0,
            "With four or five routes an `else if` chain has its default somewhere "
            "you cannot see from where you are typing, and appending to the chain "
            "moves it. The flat form has one rule — routes return, the last line is "
            "the default — that does not decay as the file grows."),
        _pq("Does the ORDER of the routes matter in this module?",
            ["No — the conditions are mutually exclusive, so at most one can match. It starts mattering in module 10",
             "Yes — the first route must always be the GET",
             "Yes — routes must be in alphabetical order by path",
             "No, and it never will, because each route names an exact path"],
            0,
            "Exact-path routes cannot both match. Module 10 adds `/todos/:id`, "
            "which matches a family of paths, and two routes that can both match "
            "have to be ordered most-specific-first."),
    ],
)

_M7_S4 = _pstep(
    "grow", "Adding the second route",
    "What the ladder looks like at two — and the shape modules 9 to 12 drop straight into.",
    """
The value of the shape is what it costs to extend. Add a health check:

```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}
```

Four lines, in the middle, touching nothing. No chain to find the end of, no
default to move, no existing route to re-read. That is the whole argument for
step 3's shape, and it is now demonstrated rather than asserted.

(`/health` is not part of the todo contract — it is the endpoint an operator or
a load balancer hits to ask whether the process is alive. Nearly every real
service has one, and it makes an honest second route because it steals nothing
from the modules ahead.)

### Where the rest of the project goes

The remaining verbs slot into the same gap:

```ts
if (req.method === "GET"    && url.pathname === "/todos") { … }   // module 7 ✓
if (req.method === "POST"   && url.pathname === "/todos") { … }   // module 9
if (req.method === "GET"    && isTodoPath(url.pathname))  { … }   // module 10
if (req.method === "PATCH"  && isTodoPath(url.pathname))  { … }   // module 11
if (req.method === "DELETE" && isTodoPath(url.pathname))  { … }   // module 12
send(res, 404, { error: "not_found" });
```

Five routes and a default. Module 20 turns that into a table you can loop over —
which is all a framework's router is — and the reason it is module 20 and not
module 7 is that you cannot see what to abstract until you have written the five
by hand.

### A route that matches too much shadows everything below it

The ladder has one failure mode, and it is not order-of-mutually-exclusive-
routes. It is a condition that is broader than you meant:

```ts
if (req.method === "GET") {              // ← no path check
  send(res, 200, todos);
  return;
}
if (req.method === "GET" && url.pathname === "/health") { … }   // unreachable
```

Every GET now returns the todo list, `/health` included, and the second route
can never run. Nothing errors — the request that proves it is one you have to
think to send. **Test the route you did not just write.**

### `POST /todos` gets a 404 today, and that is a simplification

There is an argument that it should be a **405 Method Not Allowed**: the path
exists, the verb is not supported, and 405 says exactly that where 404 says "no
such address".

This project answers 404, on purpose. Doing 405 properly means knowing which
verbs a path supports and sending an `Allow` header listing them, which is a
routing table — module 20's job, not this one's. Worth knowing that the
simplification is there and what the honest version would cost, which is
generally more useful than pretending the question does not exist.
""",
    """
```bash
$ curl -s localhost:3000/health
{"status":"ok"}

$ curl -s localhost:3000/todos
[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]

$ curl -s -i localhost:3000/healthz
HTTP/1.1 404 Not Found
```

Two routes, each answering only its own request, and everything else still
reaching the default. Check the third one every time you add a route: a route
that works is half the test, and a route that does not steal other traffic is
the other half.
""",
    pitfalls=[
        "Adding a route below the fall-through. It is unreachable, and its `send` throws on a response the 404 already finished.",
        "A condition broader than you meant — `req.method === \"GET\"` with no path check. It shadows every route below it and nothing errors; only a request you thought to try shows it.",
        "Testing only the route you just added. The regression is always in the ones you did not touch: add a route, then re-curl the others and the 404.",
        "Reaching for 405 by hand, per route. Doing it properly needs the set of verbs a path allows plus an `Allow` header — that is a routing table, and it is module 20.",
        "Copy-pasting a route and forgetting to change the path, so two routes have the same condition. The second is dead code and the compiler will not tell you.",
    ],
    exercises=[
        _pex("todo-m7-grow-1", "A second route",
             "Add a health check: `GET /health` answers `200` with `{\"status\":\"ok\"}`. "
             "Write the condition — the existing route and the fall-through must keep "
             "working exactly as they do now.",
             _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
             'req.method === "GET" && url.pathname === "/health"',
             [("GET /health\nGET /todos\nGET /healthz\nPOST /health",
               '200 {"status":"ok"}'
               '\n200 [{"id":1,"title":"Buy milk","done":false}]'
               '\n404 {"error":"not_found"}\n404 {"error":"not_found"}')],
             ["The same shape as the route above it — verb and path, joined with `&&`.",
              "`/healthz` is a different path and must still 404.",
              '`req.method === "GET" && url.pathname === "/health"`']),
        _pfix("todo-m7-grow-fix1", "The route that ate the others",
              "`GET /todos` returns the list, as it should. `GET /health` also returns "
              "the list, and so does `GET /anything-at-all` — the health route never "
              "runs and the 404 is unreachable for any GET.\n\n"
              "The bug is in the first route, and it is a missing half.",
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
              [("GET /todos\nGET /health\nGET /nope",
                '200 [{"id":1,"title":"Buy milk","done":false}]'
                '\n200 {"status":"ok"}\n404 {"error":"not_found"}')],
              ["A route is a verb AND a path. The first one only checks the verb.",
               "Anything that matches too much shadows every route below it.",
               '`if (req.method === "GET" && url.pathname === "/todos") {`'],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("A route reads `if (req.method === \"GET\") { send(res, 200, todos); "
            "return; }` and sits above three other routes. What is the symptom?",
            ["Every GET returns the todo list, and the routes below it never run — with no error anywhere",
             "A 500 on every GET",
             "The routes below it run twice",
             "Only `/todos` works, which is correct"],
            0,
            "It matches too much, so it answers first and returns. The routes below "
            "are dead code the compiler is perfectly happy with. This is why you "
            "re-test the routes you did not just change."),
        _pq("Why does `POST /todos` return 404 rather than 405 in this project?",
            ["405 needs the set of verbs a path allows plus an `Allow` header — that is a routing table, which is module 20",
             "405 is not a real status code",
             "Node cannot send a 405 from `writeHead`",
             "404 and 405 mean the same thing to every client"],
            0,
            "405 is the more precise answer and this project takes the simpler one "
            "deliberately. Knowing which simplification you made, and what the "
            "honest version would cost, is the useful half."),
    ],
)

_M7_FINAL = _pch(
    "todo-m7-build", "Module 7 build — the list is live", "Medium",
    "Write the whole handler.\n\n"
    "Parse the request target as module 6 did. Then route:\n\n"
    "* `GET /todos` → `200` with the store's array, exactly as it is\n"
    "* `GET /health` → `200` with `{\"status\":\"ok\"}`\n"
    "* anything else, any verb → `404` with `{\"error\":\"not_found\"}`\n\n"
    "Routes first, each one stopping after it answers. The 404 last, and "
    "unconditional — not an `else`. The store and `send` are already written.",
    _server("""
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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

addTodo("Buy milk");
addTodo("Write tests");

function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""),
    """function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });
}""",
    [("GET /todos\nGET /health\nGET /todos?done=true\nGET /\nGET /todos/1\nPOST /todos {\"title\":\"Ship it\"}\nDELETE /todos/1",
      '200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]'
      '\n200 {"status":"ok"}'
      '\n200 [{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":false}]'
      '\n404 {"error":"not_found"}\n404 {"error":"not_found"}'
      '\n404 {"error":"not_found"}\n404 {"error":"not_found"}')],
    ["The whole handler goes in the blank: signature, parse, two routes, default.",
     'Start with `const url = new URL(req.url ?? "/", "http://localhost");` — module 6.',
     "Each route is `if (verb && path) { send(…); return; }`. `&&`, and the `return` "
     "is not optional now that there is a line below it.",
     "Route on `url.pathname`, which is why the third request — with a query string "
     "on it — must return the list rather than a 404.",
     "`GET /todos/1` is a different path from `/todos` and must 404. It gets its own "
     "route in module 10.",
     "The last statement is `send(res, 404, { error: \"not_found\" });`, outside "
     "every `if`."],
)

_TODO_MODULES.append(_pmod(
    key="todo-routing", number=7, phase="network",
    title="Routing, and 404 as the default",
    what="match method + path, fall through to not_found",
    goal="Serve GET /todos from the store, and 404 everything else.",
    why=_M7_WHY,
    est_minutes=50,
    builds_on=["todo-store", "todo-url"],
    concepts=["routing", "method + path matching", "fall-through", "404 as default",
              "route ordering", "405"],
    deliverable="The list you built in phase 1, live over HTTP — and a router "
                "shape the next thirteen modules add one `if` to.",
    objectives=[
        "Write a route that matches on both the verb and the path, and say why `||` is the bug you cannot see",
        "Serve the store's array over HTTP and explain why `send`'s `object` parameter took it unchanged",
        "Place the 404 as an unconditional last statement and argue against the `else if` chain",
        "Predict what a handler with no fall-through does to a client, and recognise the symptom",
        "Add a second route without touching the first, and name the failure mode a too-broad route causes",
        "Say why `POST /todos` gets a 404 here, what 405 would mean, and what it would cost",
    ],
    endpoints=[
        _pep("GET", "/todos", "List every todo", "", "[Todo] — a bare array until module 18", "200"),
        _pep("GET", "/health", "Is the process alive?", "", '{"status":"ok"}', "200"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M7_BRIEF,
    syntax=_M7_SYNTAX,
    steps=[_M7_S1, _M7_S2, _M7_S3, _M7_S4],
    final_build=_M7_FINAL,
    acceptance=[
        "`curl -s localhost:3000/todos` returns a JSON array of your seeded todos with a 200.",
        "`curl -s \"localhost:3000/todos?done=true\"` returns the same thing — the query string does not stop the route matching.",
        "`curl -s -i -X DELETE localhost:3000/todos` returns 404 — the path matches and the verb does not.",
        "`curl -s -i localhost:3000/nonsense` returns 404 with `{\"error\":\"not_found\"}`.",
        "`curl -s localhost:3000/health` returns `{\"status\":\"ok\"}`.",
        "Every route ends with `return`, and the 404 is the handler's last statement rather than an `else`.",
        "Deleting the 404 line makes `curl localhost:3000/nonsense` hang rather than error — and you have seen it do that.",
        "The `addTodo` seed calls are above `listen`, not inside the handler.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s localhost:3000/todos
curl -s "localhost:3000/todos?done=true"      # same list — routes on pathname
curl -s localhost:3000/health
curl -s -i localhost:3000/nonsense            # 404
curl -s -i -X DELETE localhost:3000/todos     # 404 — path matches, verb does not
curl -s -i -X POST localhost:3000/todos       # 404 — module 9 adds this
```

Then break it three ways, because each failure looks completely different from
the outside:

```bash
# 1. delete the last line (the 404), restart:
curl -s localhost:3000/nonsense
#    → hangs. No status, no error, no log. Ctrl+C. This is the one to sit with.

# 2. put it back, then delete the `return` inside the /todos route, restart:
curl -s localhost:3000/todos
#    → you get the list, and the server terminal shows ERR_HTTP_HEADERS_SENT.
#      The request looked fine. The process did not survive it.

# 3. put it back, then change the first route's `&&` to `||`, restart:
curl -s localhost:3000/health
#    → the todo list. The health route is now unreachable, and nothing said so.
```

Three bugs, three symptoms: a hang, a crash after a correct answer, and a wrong
answer with no error at all. Recognising which is which from the symptom alone
is most of what debugging a server is.
""",
    reference="""// server.ts — module 7
//
// Phase 2 complete. The store from modules 1-3 and the server from modules 4-6
// finally meet, and the wire between them is one `if`.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

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

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

// THE ROUTER. The shape matters more than any line in it:
//
//   routes first, each one `return`ing after it answers
//   the 404 last, unconditional, NOT an `else`
//
// Written this way the router cannot forget its 404, because the 404 is what
// happens when you write nothing. An `if / else if / else` chain puts the
// default somewhere you cannot see from where you are typing, and appending to
// the chain moves it.
//
// Adding a route is one `if`, anywhere above the last line. Modules 9-12 add
// four more; module 20 turns the lot into a table you loop over, which is all a
// framework's router has ever been.
function handler(req: IncomingMessage, res: ServerResponse): void {
  // pathname, not req.url — the raw target carries the query string, so
  // /todos?done=true would stop matching /todos. Module 17 depends on this.
  const url = new URL(req.url ?? "/", "http://localhost");

  // A route is a verb AND a path. `||` here compiles, passes the first test you
  // would write, and makes DELETE /todos return the list.
  //
  // `return` is load-bearing now that there is a line below: without it the
  // response goes out correctly and then the 404 throws ERR_HTTP_HEADERS_SENT
  // on a response that has already gone — a crash after an answer that looked
  // fine.
  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);     // a bare array. The {items,total} envelope is a
    return;                    // deliberate breaking change in module 18.
  }

  // Not part of the todo contract — the endpoint an operator or a load balancer
  // hits to ask whether the process is alive. It is here to prove that adding a
  // route costs four lines in the middle and touches nothing else.
  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  // The default. POST /todos lands here today; arguably that is a 405, since
  // the path exists and only the verb is unsupported — but 405 done properly
  // needs the set of allowed verbs and an `Allow` header, which is a routing
  // table, which is module 20.
  send(res, 404, { error: "not_found" });
}

// Seeded before listen, not inside the handler — seeding per request would add
// two todos every time anyone looked at the list. Deleted in module 9, when the
// client can create its own.
addTodo("Buy milk");
addTodo("Write tests");

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Add `GET /` returning `{ \"todos\": \"/todos\", \"health\": \"/health\" }` — a tiny index of what the server offers. Four lines, in the middle, touching nothing: that is the shape doing its job.",
        "Log one line per request from the top of the handler — `console.error(req.method, url.pathname)` — and watch a `curl -s \"localhost:3000/todos?done=true\"` print `GET /todos`. That is the query string being stripped, live.",
        "Give `POST /todos` a real 405: answer `405` with an `Allow: GET` header via `res.setHeader` before the `send`. Then notice you had to hard-code the verb list, and that doing it for five routes needs a table.",
        "Extract the condition into `function isRoute(req: IncomingMessage, path: string, method: string): boolean` and rewrite both routes with it. Decide for yourself whether the file got better — there is a real argument either way at two routes, and a different one at five.",
        "Delete the two `addTodo` calls and confirm `GET /todos` returns `[]` with a 200. An empty collection is a success, and a client that treats it like a 404 has a bug in it.",
    ],
    glossary=[
        _pgloss("route", "One verb plus one path, and the code that answers it. In this project: an `if` and a `send`."),
        _pgloss("fall-through", "The unconditional last statement of the handler — what answers a request no route claimed."),
        _pgloss("router", "The thing that picks a route. Here it is a list of `if`s; in module 20 it becomes a table."),
        _pgloss("shadowing", "A route whose condition is broader than intended, answering requests meant for routes below it. No error, no log."),
        _pgloss("405 Method Not Allowed", "\"That path exists; that verb does not.\" More precise than 404, and it needs an `Allow` header listing the verbs — so this project does not."),
        _pgloss("health check", "`GET /health` — the endpoint an operator or load balancer polls to ask whether the process is alive."),
        _pgloss("ERR_HTTP_HEADERS_SENT", "Two responses on one request. In a router, almost always a missing `return` after a `send`."),
    ],
    cheatsheet="""
```ts
function handler(req: IncomingMessage, res: ServerResponse): void {
  const url = new URL(req.url ?? "/", "http://localhost");   // pathname, not req.url

  if (req.method === "GET" && url.pathname === "/todos") {   // verb AND path
    send(res, 200, todos);
    return;                                                  // not optional now
  }

  if (req.method === "GET" && url.pathname === "/health") {
    send(res, 200, { status: "ok" });
    return;
  }

  send(res, 404, { error: "not_found" });   // the default — last, unconditional
}
```

**The rule:** routes above, each returning. Default below, never an `else`.

| Symptom | Cause |
|---|---|
| unmatched path hangs, no error | no fall-through — the handler returns without writing |
| correct answer, then the process dies | missing `return`; the 404 ran too |
| a route returns another route's answer | a condition broader than you meant — it shadows what is below |
| route 404s once a `?` is added | routed on `req.url` instead of `url.pathname` |
| `DELETE /todos` returns the list | `||` where you meant `&&` |

| Request | Answer | Added in |
|---|---|---|
| `GET /todos` | 200, bare array | 7 |
| `GET /health` | 200 `{"status":"ok"}` | 7 |
| `POST /todos` | 404 today (arguably 405) | 9 |
| `GET /todos/1` | 404 today | 10 |
| anything else | 404 | 5 |
""",
    self_check=[
        "Can you say what a route is, in terms of the two things that have to match?",
        "Can you explain why the 404 is the handler's last statement rather than an `else`, in a way that mentions what happens at five routes?",
        "Can you describe the three different symptoms of: no fall-through, a missing `return`, and `||` for `&&`?",
        "Can you say why `send(res, 200, todos)` needed no change to `send`, and which module's decision that was?",
        "Can you say why `GET /todos?done=true` still matches, and which module would have broken if it did not?",
        "Can you explain what 405 would mean for `POST /todos`, and why this project does not do it yet?",
    ],
    review=[
        _pq("Which of these makes `DELETE /todos` return the todo list?",
            ["`if (req.method === \"GET\" || url.pathname === \"/todos\")`",
             "`if (req.method === \"GET\" && url.pathname === \"/todos\")`",
             "Routing on `url.pathname` instead of `req.url`",
             "A missing `return` after the `send`"],
            0,
            "`||` is true when either side is, so a request to `/todos` matches "
            "whatever the verb. The first test anyone writes — `GET /todos` — "
            "passes, which is what makes it worth checking the request that should "
            "*fail*."),
        _pq("A handler routes `GET /todos` and has nothing after the `if`. A client "
            "asks for `/nope`. What does the client see?",
            ["Nothing — the request hangs, because no response was ever written or closed",
             "404, from Node's default handling",
             "An empty 200",
             "500, from the replayer's error boundary"],
            0,
            "This is module 4's missing `res.end` with a router in front of it. "
            "Nothing errors, nothing logs, and the symptom is a client waiting "
            "forever — which is why the default is written first and never removed."),
        _pq("Why does `send(res, 200, todos)` work without changing `send`?",
            ["`data` is typed `object`, and an array is an object — module 5's decision paying off",
             "`send` was overloaded for arrays in module 5",
             "`JSON.stringify` converts the array to an object first",
             "It does not; module 7 widens the parameter"],
            0,
            "Module 5 picked `object` over `Todo` precisely so that everything "
            "leaving the application — a todo, a list of them, an error record — "
            "goes through the one helper unchanged."),
        _pq("In this module, does the order of the two routes matter?",
            ["No — both name exact paths, so at most one can match. Module 10 changes that",
             "Yes — `/health` must come first because it is shorter",
             "Yes — the most recently added route must be last",
             "No, and it never will"],
            0,
            "Exact-path conditions are mutually exclusive. `/todos/:id` in module 10 "
            "matches a family of paths, and from then on two routes can both match — "
            "which is when most-specific-first starts to matter."),
        _pq("What is the one thing every route in this handler must end with?",
            ["`return`, so a route that has answered cannot fall into the one below it",
             "`res.end()`, to close the response",
             "`break`, to leave the router",
             "A call to the fall-through, so the 404 is always considered"],
            0,
            "`send` writes the whole response and closes it, but it does not stop "
            "your function. Without the `return` the next `send` throws on a "
            "response that no longer exists."),
    ],
    milestone="Phase 2 is done. The store you built with no server in the way is "
              "now reachable over HTTP by a server you built with no store in the "
              "way — and the router they meet in has room for every route the "
              "rest of this project adds.",
))
