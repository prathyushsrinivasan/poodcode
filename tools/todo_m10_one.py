# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 10 — GET /todos/:id, dynamic paths.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`.
#
# THE MODULE DECISION 4 WAS FOR. The whole track type-checks under
# `noUncheckedIndexedAccess`, and until now that flag has mostly been a promise.
# Here it pays: `"/todos".split("/")[2]` genuinely does not exist, `/todos`
# genuinely reaches this code, and the compiler refuses to let that `undefined`
# reach a function that wants a string. Step 3 grades that refusal on purpose —
# the one `fix` in this module whose starter fails at COMPILE time, because the
# red squiggle IS the lesson. `verify_projects.py` lists it under "fix starters
# that fail at compile time"; that is expected, not an authoring slip.
#
# THREE FUNCTIONS, ONE IDEA EACH, and the split is the design:
#
#   idText(pathname)   is this path shaped like /todos/<something>?   (structure)
#   parseId(text)      is that something a whole number from 1?       (value)
#   todoId(pathname)   both, or undefined                             (compose)
#
# Steps 1 and 2 are PLAIN programs that print what each function returns, so a
# single exercise can check eight paths at once and a wrong answer is a wrong
# line, not a wrong status code three requests later. Steps 3 and 4 put them in
# the router.
#
# TWO 404S, ONE ANSWER. `/todos/99` (no such todo) and `/todos/abc` (not an id)
# both answer `404 {"error":"not_found"}`. Step 4 argues for that rather than
# 400 for the second — "there is nothing at this address" is exactly true of
# both — and says which later module would change it if anything did.
#
# NO `...`, NO `.slice(`, NO `typeof` anywhere in these programs, including
# comments: modules 11, 18 and 13 own those, and `_lint_scope` reads program
# text, not just code. Teaching text inside a program uses the Unicode `…`.
# ---------------------------------------------------------------------------

_M10_STORE = """type Todo = {
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
"""

_M10_SEND = """function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}
"""

_M10_READBODY = """function readBody(req: IncomingMessage): Promise<string> {
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

_M10_IDTEXT = """function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}
"""

_M10_PARSEID = """function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}
"""

_M10_TODOID = """function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}
"""

_M10_HANDLER = """async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const id = todoId(url.pathname);

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

  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    send(res, 200, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}
"""


def _m10(handler=_M10_HANDLER, idtext=_M10_IDTEXT, parseid=_M10_PARSEID,
         todoid=_M10_TODOID):
    """A module-10 server program. Everything but the three path functions and
    the handler is code the learner already has."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (_M10_STORE, _M10_SEND, _M10_READBODY,
                                idtext, parseid, todoid, handler)))


_M10_FULL = _m10()

# --- Step 1's plain program: what idText makes of eight paths ---------------
_M10_S1_PRINTS = """
console.log(JSON.stringify(idText("/todos/7")));
console.log(JSON.stringify(idText("/todos/42")));
console.log(JSON.stringify(idText("/todos/abc")));
console.log(JSON.stringify(idText("/todos")));
console.log(JSON.stringify(idText("/todos/7/done")));
console.log(JSON.stringify(idText("/users/7")));
console.log(JSON.stringify(idText("/todos/")));
console.log(JSON.stringify(idText("/")));
"""
_M10_S1_OUT = ('"7"\n"42"\n"abc"\nundefined\nundefined\nundefined\n""\nundefined')


def _m10_s1(idtext=_M10_IDTEXT):
    return _plain(idtext.rstrip("\n") + "\n" + _M10_S1_PRINTS)


# --- Step 2's plain program: what parseId makes of nine strings -------------
_M10_S2_PRINTS = """
console.log(parseId("7"));
console.log(parseId("42"));
console.log(parseId("abc"));
console.log(parseId("7.5"));
console.log(parseId("0"));
console.log(parseId("-3"));
console.log(parseId(""));
console.log(parseId("007"));
console.log(parseId("1e3"));
"""
_M10_S2_OUT = "7\n42\nundefined\nundefined\nundefined\nundefined\nundefined\n7\n1000"


def _m10_s2(parseid=_M10_PARSEID):
    return _plain(parseid.rstrip("\n") + "\n" + _M10_S2_PRINTS)


_TODO_A = '{"id":1,"title":"Buy milk","done":false}'
_TODO_B = '{"id":2,"title":"Write tests","done":false}'
_POST_A = 'POST /todos {"title":"Buy milk"}'
_POST_B = 'POST /todos {"title":"Write tests"}'
_NF = '404 {"error":"not_found"}'

_M10_WHY = (
    "Every todo has an id, and a client that created one got that id back in "
    "the 201 — and there is nothing it can do with it. `GET /todos/1` is a 404. "
    "The only way to see one todo is to download all of them and search, which "
    "works with three and stops working with three thousand. A resource that "
    "cannot be addressed one at a time cannot be updated or deleted one at a "
    "time either, so modules 11 and 12 are both blocked on this one."
)

_M10_BRIEF = """
### The whole module in one line

Give every todo its own address — `/todos/1`, `/todos/2` — and answer `404`
when there is nothing there.

### Every route so far has been a fixed string

```ts
if (req.method === "GET" && url.pathname === "/todos") { … }
```

That comparison can never match `/todos/1`, `/todos/2` and `/todos/9000` at
once, and writing one `if` per todo is not a plan. The path now has a **part
that varies**, and the router has to take it apart to read it.

### Three questions, three small functions

```
"/todos/7"  →  is it shaped like /todos/<something>?   →  "7"
"7"         →  is that a whole number from 1?          →  7
            →  and is there a todo with that id?       →  the todo, or 404
```

The first two are pure functions of a string, so steps 1 and 2 build them with
no server at all and check eight inputs in a single run. The third is the store
lookup you wrote in module 3 and have been waiting seven modules to use.

### The flag this project has been type-checking under since module 1

```ts
const parts = "/todos".split("/");    // ["", "todos"]
parts[2]                              // string | undefined — and here, undefined
```

`noUncheckedIndexedAccess` makes every array read say it might miss. Until now
that has been a promise; here it is a fact, because `/todos` really does reach
this code and really does have no third part. The compiler will not let that
`undefined` reach a function that needs a string — and step 3 grades exactly
that refusal.

### `/todos/abc` is a 404 too

Not a 400. Step 4 makes the argument, but the short version is module 5's
definition: 404 means *there is nothing at this address*, and that is precisely
true of `/todos/abc`. There is no request body to be wrong, only an address
that leads nowhere.
"""

_M10_SYNTAX = [
    _syn(
        'const parts = pathname.split("/");',
        "Cut a string into an array of the pieces between each `/`. The "
        "separator itself is thrown away.",
        """
"/todos/7".split("/");        // ["", "todos", "7"]
"/todos".split("/");          // ["", "todos"]
"/todos/7/done".split("/");   // ["", "todos", "7", "done"]
"/todos/".split("/");         // ["", "todos", ""]
""",
        "The first piece is always `\"\"` — the path starts with a `/`, and "
        "there is nothing before it. So the id is at index **2**, not 1, and "
        "a trailing slash adds an empty piece on the end rather than nothing.",
    ),
    _syn(
        "parts[2]",
        "Read one piece by position. Under `noUncheckedIndexedAccess` its type "
        "is `string | undefined`, because an array read can always miss.",
        """
const parts = "/todos".split("/");
const third = parts[2];       // string | undefined
console.log(third);           // undefined
""",
        "Checking `parts.length === 3` first does **not** narrow it. That "
        "check is proof to you, not to the compiler, which does not count. "
        "Return it with a `| undefined` in the type, or compare it with "
        "`undefined` before you use it as a string.",
    ),
    _syn(
        "const id = Number(text);",
        "Turn text into a number. The mirror of a template literal, which turns "
        "a number into text.",
        """
Number("7");      // 7
Number("abc");    // NaN — "not a number", and still of type number
Number("7.5");    // 7.5
Number("");       // 0   (!)
""",
        "It never fails — it answers `NaN` instead, and `NaN` is a `number`, so "
        "the compiler is perfectly happy. Worse, `Number(\"\")` is `0`, which "
        "looks like a real answer. Always check what came back.",
    ),
    _syn(
        "Number.isInteger(id)",
        "`true` for a whole number and `false` for everything else — `NaN`, "
        "`7.5`, `Infinity`. One call rejects both kinds of junk `Number` can hand "
        "back.",
        """
Number.isInteger(7);            // true
Number.isInteger(Number("abc"));// false — NaN is not an integer
Number.isInteger(7.5);          // false
""",
        "`id === NaN` looks like the obvious check and is always `false`: `NaN` "
        "is the one value not equal to itself. TypeScript refuses to compile it "
        "for that reason. Use `Number.isInteger`.",
    ),
    _syn(
        "function todoId(pathname: string): number | undefined { … }",
        "A function whose return type admits it might have no answer. Module 3's "
        "`findTodo` returns `Todo | undefined` for the same reason.",
        """
const id = todoId(url.pathname);
if (req.method === "GET" && id !== undefined) {
  // here, id is a number
}
""",
        "The `| undefined` is not pessimism — it is the 404. Every path that is "
        "not a todo's address comes back as `undefined`, and the router's "
        "`id !== undefined` is where that becomes a route that does not match.",
    ),
    _syn(
        "function findTodo(id: number): Todo | undefined { … }",
        "Module 3's lookup. Written seven modules ago for exactly this route.",
        "",
        "Narrow the result before you send it. `findTodo(id)!` compiles and "
        "answers `200` with an empty body when the todo is missing — module 3 "
        "named that cost; this is where you would pay it.",
        recap=True,
    ),
    _syn(
        'const url = new URL(req.url ?? "/", "http://localhost");',
        "Module 6's parse, done once at the top of the handler. `todoId` reads "
        "`url.pathname`, so a query string never gets in the way of an id.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — cutting the path.
# ---------------------------------------------------------------------------

_M10_S1 = _pstep(
    "split", "Cutting the path into pieces",
    "`.split(\"/\")`, index 2, and the `undefined` the compiler will not let you forget.",
    """
A fixed route compares the whole path at once:

```ts
url.pathname === "/todos"
```

A route with a variable part cannot. It has to take the path apart and look at
the pieces:

```ts
"/todos/7".split("/")        // ["", "todos", "7"]
```

`.split("/")` cuts the string at every `/` and hands back what was between them.
Three things about that result are worth staring at before writing any code.

**The first piece is empty.** The path starts with `/`, so there is nothing
before the first cut. That is why the id is at index **2**, and why `parts[1]`
is the word `todos`.

**The number of pieces is the shape of the path.**

| Path | `.split("/")` | Pieces |
|---|---|---|
| `/todos` | `["", "todos"]` | 2 |
| `/todos/7` | `["", "todos", "7"]` | **3** |
| `/todos/7/done` | `["", "todos", "7", "done"]` | 4 |
| `/todos/` | `["", "todos", ""]` | 3 — with an empty id |

A todo's address has exactly three. Two is the collection; four is something
this API does not have.

**The id is still text.** `"7"`, not `7`. Turning it into a number is step 2,
and it is a separate step on purpose: "is this path shaped like a todo's
address?" and "is this piece a valid id?" are different questions with
different wrong answers.

### The first function: is it shaped like `/todos/<something>`?

```ts
function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}
```

Two checks, and each one rejects something real. `parts.length !== 3` rejects
`/todos` and `/todos/7/done`. `parts[1] !== "todos"` rejects `/users/7`, which
has exactly the right number of pieces and is not a todo at all.

### Why the return type says `| undefined` twice over

Look at the last line. By the time it runs, `parts.length` is 3, so `parts[2]`
certainly exists. But hover over it and the compiler says:

```ts
parts[2]      // string | undefined
```

The compiler **does not count.** `parts.length !== 3` is proof to you; to the
compiler it is a comparison between two numbers that says nothing about what is
at index 2. That is `noUncheckedIndexedAccess` doing precisely what it was
turned on for, and the honest response is not to argue with it — the function
returns `string | undefined` anyway, because most paths are not a todo's
address. Step 3 is where that `undefined` meets something that needs a string,
and the compiler stops it there.
""",
    """
Your `idText` answers all eight of these correctly:

```
idText("/todos/7")        "7"
idText("/todos/abc")      "abc"        ← shaped right; step 2 rejects it
idText("/todos")          undefined    ← two pieces
idText("/todos/7/done")   undefined    ← four pieces
idText("/users/7")        undefined    ← wrong collection
idText("/todos/")         ""           ← three pieces, the last one empty
```

The `"abc"` and the `""` are correct answers for *this* function. It is only
asked about the shape.
""",
    pitfalls=[
        "Reading the id from `parts[1]`. That is the word `todos` — the first piece is the empty string before the leading `/`, so everything is one further along than it looks.",
        "Checking only `parts[1] === \"todos\"`. `/todos/7/done` passes, and a URL your API never defined starts returning todo 7.",
        "Checking only the length. `/users/7` has three pieces, and an API that answers it with a todo is an API with an address bug nobody asked for.",
        "Expecting `parts.length === 3` to make `parts[2]` a `string`. The compiler does not connect the two — `parts[2]` stays `string | undefined`, which is why the return type says so.",
        "Splitting `req.url` instead of `url.pathname`. `/todos/7?x=1` splits into `[\"\", \"todos\", \"7?x=1\"]`, and `Number(\"7?x=1\")` is `NaN`. Module 6 parsed the URL so that you would never have to think about this.",
        "Treating `/todos/` as `/todos`. Its last piece is `\"\"`, not missing — so it reaches step 2, and step 2 had better not think `\"\"` is an id.",
    ],
    warmup=[
        _pq("What does `\"/todos/7\".split(\"/\")` return?",
            ["`[\"\", \"todos\", \"7\"]` — the path starts with `/`, so the first piece is empty",
             "`[\"todos\", \"7\"]`",
             "`[\"/todos\", \"/7\"]`",
             "`[\"\", \"todos\", 7]`, with the id already a number"],
            0,
            "Nothing comes before the first `/`, and `split` still reports that "
            "nothing as a piece. That is why the id lives at index 2."),
        _pq("`const parts = pathname.split(\"/\"); if (parts.length === 3) { … }` "
            "— inside the `if`, what type is `parts[2]`?",
            ["`string | undefined` — the length check is proof to you, not to the compiler",
             "`string`, because the length check proved it exists",
             "`string[]`",
             "`never`"],
            0,
            "`noUncheckedIndexedAccess` makes every indexed read admit it might "
            "miss, and TypeScript does not relate `length` to which indexes exist."),
    ],
    exercises=[
        _pex("todo-m10-split-1", "Cut the path",
             "`idText` needs the pieces of the path. Cut it at every `/`.",
             _m10_s1(),
             '  const parts = pathname.split("/");',
             [("", _M10_S1_OUT)],
             ["`.split` takes the separator and returns an array of what was between.",
              "The separator is a slash, as a string.",
              "Store the array in `parts` — the next line reads `parts.length` and `parts[1]`.",
              '`const parts = pathname.split("/");`']),
        _pfix("todo-m10-split-fix1", "A todo at the users' address",
              "`idText(\"/users/7\")` answers `\"7\"`. So would `/orders/7`, "
              "`/admin/7` and every other three-piece path — the function only "
              "checks how many pieces there are, not what they say.",
              _m10_s1("""function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3) {
    return undefined;
  }
  return parts[2];
}
"""),
              _m10_s1(),
              [("", _M10_S1_OUT)],
              ["Three pieces is the right shape. It is not enough to be the right path.",
               "Which piece names the collection?",
               "Index 1 — index 0 is the empty string before the leading slash.",
               '`if (parts.length !== 3 || parts[1] !== "todos")`'],
              difficulty="Easy"),
        _pex("todo-m10-split-2", "The piece that is the id",
             "The path has the right shape. Hand back the piece that holds the "
             "id — as text, for now.",
             _m10_s1(),
             "  return parts[2];",
             [("", _M10_S1_OUT)],
             ["Count from zero, and remember what is at index 0.",
              "`parts[0]` is `\"\"`, `parts[1]` is `\"todos\"`.",
              "The return type is `string | undefined`, which is exactly the type of an array read.",
              "`return parts[2];`"]),
    ],
    quiz=[
        _pq("Why does `idText` check both `parts.length !== 3` and `parts[1] !== \"todos\"`?",
            ["Each rejects paths the other lets through: the length rejects `/todos/7/done`, the name rejects `/users/7`",
             "The second check is only there for readability",
             "`split` sometimes returns fewer pieces than there are slashes",
             "The length check is needed to make `parts[2]` a `string`"],
            0,
            "Right shape and right collection are separate facts. Missing either "
            "one gives an API that answers addresses it never defined."),
        _pq("`idText(\"/todos/\")` returns `\"\"`. Is that a bug in `idText`?",
            ["No — the path has three pieces and the last is empty; rejecting `\"\"` as an id is step 2's job",
             "Yes — it should return `undefined` for a trailing slash",
             "Yes — `split` should not produce empty pieces",
             "No — `\"\"` is a valid id"],
            0,
            "`idText` answers a question about shape, and it answers it right. "
            "Keeping \"is it an id?\" out of it is what makes both functions "
            "small enough to trust."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — text becomes an id.
# ---------------------------------------------------------------------------

_M10_S2 = _pstep(
    "number", "Text becomes an id",
    "`Number`, the `NaN` it hands you instead of failing, and `Number.isInteger`.",
    """
`idText` gives you `"7"`. The store's ids are numbers, and `findTodo("7")` does
not compile. One call converts it:

```ts
Number("7")        // 7
```

And that is where the easy part ends, because `Number` **never fails**:

```ts
Number("abc")      // NaN
Number("7.5")      // 7.5
Number("-3")       // -3
Number("")         // 0      ← really
Number("007")      // 7
Number("1e3")      // 1000
```

Every one of those has type `number`. `NaN` — *not a number* — is, confusingly,
a number, so the compiler has nothing to complain about. `Number("")` is `0`,
which looks like a real answer and is not one; and remember from step 1 that
`/todos/` hands you exactly `""`.

### What an id actually is

The store hands out `1, 2, 3, …`. So an id is a **whole number from 1 up**, and
everything else is not one:

```ts
function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}
```

`Number.isInteger(id)` is `false` for `NaN`, for `7.5` and for `Infinity`, so
one check throws out every kind of junk `Number` can produce. `id < 1` throws
out `0` — including the `0` that `""` becomes — and the negatives.

### The check that looks right and never works

```ts
if (id === NaN) { … }        // never true
```

`NaN` is the one value in JavaScript that is **not equal to itself**, so this is
`false` for every possible `id`, `NaN` included. TypeScript knows that and
refuses to compile it. `Number.isInteger` asks the question you meant.

### What `Number` still lets through

`"007"` is 7 and `"1e3"` is 1000, so `/todos/007` finds todo 7. That is
*lenient*, not *wrong* — both really are those numbers — and this project
accepts it. A stricter API would insist the text is exactly the digits of the
number; it is in the stretch list, and it is one extra comparison.
""",
    """
Your `parseId` answers all nine:

```
"7"   → 7          "abc" → undefined     "0"  → undefined
"42"  → 42         "7.5" → undefined     "-3" → undefined
"007" → 7          ""    → undefined     "1e3"→ 1000
```

Look hardest at `""`. If that one says `0`, `/todos/` is going to go looking
for a todo with id 0.
""",
    pitfalls=[
        "Trusting `Number` to fail. It never does — bad text comes back as `NaN`, which is a `number`, so nothing downstream complains until a lookup quietly finds nothing.",
        "`Number(\"\")` is `0`. `/todos/` has an empty last piece, and without `id < 1` it is a perfectly ordinary lookup for a todo with id 0.",
        "`if (id === NaN)`. `NaN` is not equal to anything, itself included. TypeScript refuses to compile it; `Number.isInteger` asks what you meant.",
        "Using `parseInt`. `parseInt(\"7abc\")` is `7` — it stops at the first character it cannot read and keeps what it has, so `/todos/7abc` would find todo 7.",
        "Rejecting the id with a `400`. Step 4 makes the case: `/todos/abc` is an address with nothing at it, which is what 404 means.",
        "Returning `NaN` or `0` for \"no id\" instead of `undefined`. A caller then has to know which magic number means nothing, and the compiler cannot remind them.",
    ],
    warmup=[
        _pq("What is `Number(\"abc\")`?",
            ["`NaN` — a value of type `number` meaning *not a number*",
             "`undefined`",
             "`0`",
             "It throws an error"],
            0,
            "`Number` never throws and never returns anything but a number. That "
            "is exactly why you have to check what it gave you."),
        _pq("What is `Number(\"\")`?",
            ["`0` — which is why `id < 1` is part of the check",
             "`NaN`",
             "`undefined`",
             "It throws"],
            0,
            "An empty string converts to zero. `/todos/` hands `parseId` exactly "
            "that string."),
    ],
    exercises=[
        _pex("todo-m10-number-1", "Is it a whole number?",
             "`Number` has turned the text into a number, or into `NaN`. Reject "
             "anything that is not a whole number.",
             _m10_s2(),
             "!Number.isInteger(id)",
             [("", _M10_S2_OUT)],
             ["There is one call that is `false` for `NaN`, `7.5` and `Infinity` alike.",
              "It lives on `Number` itself.",
              "The condition is \"not an integer\", so it starts with `!`.",
              "`!Number.isInteger(id)`"]),
        _pfix("todo-m10-number-fix1", "The id with a decimal point",
              "`parseId(\"7.5\")` answers `7.5`, and `parseId(\"abc\")` answers "
              "`NaN`. Both would go to the store as if they were ids.\n\n"
              "The one check this function makes is not enough.",
              _m10_s2("""function parseId(text: string): number | undefined {
  const id = Number(text);
  if (id < 1) {
    return undefined;
  }
  return id;
}
"""),
              _m10_s2(),
              [("", _M10_S2_OUT)],
              ["`NaN < 1` is `false` — every comparison with `NaN` is. So `NaN` sails through.",
               "And `7.5` is not less than 1.",
               "You need a check that rejects both non-numbers and fractions.",
               "`if (!Number.isInteger(id) || id < 1)`"],
              difficulty="Easy"),
        _pfix("todo-m10-number-fix2", "Todo number zero",
              "`parseId(\"0\")` answers `0`, `parseId(\"-3\")` answers `-3`, and "
              "— the one that matters most — `parseId(\"\")` answers `0`. "
              "`/todos/` is about to go looking for a todo with id 0.",
              _m10_s2("""function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id)) {
    return undefined;
  }
  return id;
}
"""),
              _m10_s2(),
              [("", _M10_S2_OUT)],
              ["0 and -3 are both whole numbers. That is not the same as being ids.",
               "What is the smallest id the store ever hands out?",
               "`Number(\"\")` is `0`, so this one check covers the empty piece as well.",
               "`if (!Number.isInteger(id) || id < 1)`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `id === NaN` never catch a bad id?",
            ["`NaN` is not equal to anything, itself included, so the comparison is always `false`",
             "`NaN` is a string, not a number",
             "`===` does not work on numbers",
             "It does catch it, but only in strict mode"],
            0,
            "It is the one value that fails `x === x`. TypeScript refuses to "
            "compile the comparison for that reason."),
        _pq("Why does `parseId` return `undefined` for a bad id rather than `0`?",
            ["`0` looks like an answer; `undefined` in the return type makes every caller handle \"no id\"",
             "`0` is a valid id",
             "Returning `0` is a type error",
             "`undefined` is faster to compare"],
            0,
            "A sentinel number hides the failure in a value of the right type. "
            "`number | undefined` puts it in the type, where the compiler can see it."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the route.
# ---------------------------------------------------------------------------

_M10_S3_FIX_TODOID = """function todoId(pathname: string): number | undefined {
  return parseId(idText(pathname));
}
"""

_M10_S3 = _pstep(
    "route", "The route, and the `undefined` that travels",
    "Put the two functions together, and meet the compile error decision 4 was for.",
    """
The two functions compose into the one the router wants:

```ts
function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}
```

### Try it without the check

```ts
function todoId(pathname: string): number | undefined {
  return parseId(idText(pathname));
}
```

It reads better, and it does not compile:

```
Argument of type 'string | undefined' is not assignable to parameter of type 'string'.
```

Follow the `undefined` back to where it came from. `parts[2]` was
`string | undefined` in step 1. `idText` said so honestly in its return type.
And now it has arrived at `parseId`, which needs a real string — so the compiler
stops it, here, at the one place it would actually do damage.

This is what `noUncheckedIndexedAccess` has been for since module 1. Without it
`parts[2]` would have been typed `string`, `idText` would have promised a string
it cannot always deliver, and `todoId("/todos")` would have handed `undefined`
to `Number` — which would have said `NaN` and carried on. No error anywhere.
**The flag turned a silent wrong answer into a compile error**, and that is the
whole trade it offers.

### The route itself

`todoId` runs once, at the top of the handler, next to module 6's parse:

```ts
const url = new URL(req.url ?? "/", "http://localhost");
const id = todoId(url.pathname);
```

and the route is module 3's lookup with a status code on each branch:

```ts
if (req.method === "GET" && id !== undefined) {
  const todo = findTodo(id);
  if (todo === undefined) {
    send(res, 404, { error: "not_found" });
    return;
  }
  send(res, 200, todo);
  return;
}
```

`id !== undefined` is the path half of the condition — it is true exactly when
the path is a todo's address. Inside, `id` is a `number`, so `findTodo(id)`
compiles, and `todo` is `Todo | undefined`, so the 404 is not optional.

Module 3 taught this `if` with no HTTP anywhere near it, and said every 404 in
modules 10 to 12 would be that `if` with a response in it. This is the first.
""",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}

$ curl -s localhost:3000/todos/1
{"id":1,"title":"Buy milk","done":false}

$ curl -s -i localhost:3000/todos/2
HTTP/1.1 404 Not Found
{"error":"not_found"}
```

A todo you made, fetched by the id you were given. And one you did not make,
correctly absent.
""",
    pitfalls=[
        "`return parseId(idText(pathname));`. Reads well, does not compile — and should not. The `undefined` from `parts[2]` has arrived somewhere that needs a string.",
        "`findTodo(id)!`. Compiles, and answers `200` with an **empty body** when the todo is missing, because `JSON.stringify(undefined)` is not a string at all. Module 3 warned about exactly this.",
        "Parsing the id inside each route. `todoId` runs once, at the top, like module 6's `new URL` — PATCH and DELETE are about to need the same number.",
        "Writing `url.pathname === \"/todos/\" + id`. It works for the id you built, and it compares after the fact rather than reading the path — so it cannot tell you what the id *was*.",
        "Forgetting the `return` after the 404 inside the route. The 200 below then runs too, on a response that has already been sent.",
    ],
    warmup=[
        _pq("`idText` returns `string | undefined` and `parseId` takes a `string`. "
            "What happens with `parseId(idText(pathname))`?",
            ["It does not compile — the `undefined` must be handled before it reaches `parseId`",
             "It compiles, and `parseId` receives `\"\"` when the path does not match",
             "It compiles, and throws at runtime for `/todos`",
             "It compiles because `Number` accepts `undefined`"],
            0,
            "The possible `undefined` travels from `parts[2]` through `idText`'s "
            "return type and is caught at the first place that needs a string."),
    ],
    exercises=[
        _pfix("todo-m10-route-fix1", "The one-line todoId",
              "This does not compile, and the error is the lesson:\n\n"
              "    Argument of type 'string | undefined' is not assignable to "
              "parameter of type 'string'.\n\n"
              "Do not change `idText` or `parseId`. The `undefined` is real — "
              "`/todos` really does reach this function — so handle it where it "
              "arrives.",
              _m10(todoid=_M10_S3_FIX_TODOID),
              _M10_FULL,
              [("\n".join([_POST_A, "GET /todos/1", "GET /todos/2", "GET /todos"]),
                "\n".join(["201 " + _TODO_A, "200 " + _TODO_A, _NF, "200 [" + _TODO_A + "]"]))],
              ["`idText(pathname)` might be `undefined`. Give it a name so you can check it.",
               "If it is `undefined`, the path is not a todo's address, and `todoId` has no id to return.",
               "Otherwise it is a `string`, and `parseId` will take it.",
               "`const text = idText(pathname); if (text === undefined) { return undefined; } return parseId(text);`"],
              difficulty="Easy"),
        _pex("todo-m10-route-1", "Fetch one",
             "The id is parsed at the top of the handler. Add the route that "
             "answers with that one todo — or a 404 when there is no such todo.",
             _M10_FULL,
             """  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    send(res, 200, todo);
    return;
  }""",
             [("\n".join([_POST_A, _POST_B, "GET /todos/2", "GET /todos/1", "GET /todos/3"]),
               "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "200 " + _TODO_B,
                          "200 " + _TODO_A, _NF]))],
             ["The condition is the verb and `id !== undefined` — true exactly when the path is `/todos/<id>`.",
              "Inside, `findTodo(id)` gives `Todo | undefined`.",
              "Missing todo: 404, and `return`. Found: 200 with the todo, and `return`.",
              "The third request asks for a todo nobody created."]),
        _pfix("todo-m10-route-fix2", "An empty 200",
              "`GET /todos/1` works. `GET /todos/2`, for a todo that was never "
              "created, answers `200` — with nothing after the status code at "
              "all. No error, no 404, no body.",
              _m10(_M10_HANDLER.replace(
                  """    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    send(res, 200, todo);""",
                  """    const todo = findTodo(id)!;
    send(res, 200, todo);""")),
              _M10_FULL,
              [("\n".join([_POST_A, "GET /todos/1", "GET /todos/2"]),
                "\n".join(["201 " + _TODO_A, "200 " + _TODO_A, _NF]))],
              ["What does `!` claim about `findTodo(id)`, and is the claim true?",
               "When there is no such todo, `todo` is `undefined` and `JSON.stringify(undefined)` produces no text at all.",
               "Take the `!` away and the compiler shows you the case you skipped.",
               "`if (todo === undefined) { send(res, 404, { error: \"not_found\" }); return; }`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("What did `noUncheckedIndexedAccess` turn into a compile error in this module?",
            ["`todoId(\"/todos\")` passing `undefined` to `Number`, which would have answered `NaN` with no error at all",
             "Splitting a path that has no slashes",
             "Comparing `id` with `undefined`",
             "Calling `findTodo` with a string"],
            0,
            "Without the flag `parts[2]` is typed `string`, and the missing id "
            "becomes a `NaN` lookup that quietly finds nothing. With it, the "
            "compiler points at the exact line."),
        _pq("Why is `todoId` called once at the top of the handler rather than inside the route?",
            ["It depends only on the path, like module 6's `new URL` — and modules 11 and 12 need the same id",
             "Routes may not call functions",
             "It is faster to call it before `req.method` is known",
             "It must run before `readBody`"],
            0,
            "Parse once, use everywhere. PATCH and DELETE are each going to add "
            "one `if` that reads `id`, and none of them will parse it again."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — two 404s, one answer.
# ---------------------------------------------------------------------------

_M10_S4 = _pstep(
    "notfound", "Two kinds of missing, one answer",
    "`/todos/99` and `/todos/abc` — why both are 404, and what the router looks like now.",
    """
There are now two different ways a `GET` can fail to find a todo, and they reach
the 404 by different roads:

| Request | What happened | Who answers |
|---|---|---|
| `GET /todos/99` | a valid id, and no todo has it | the route's own 404 |
| `GET /todos/abc` | not an id at all — `todoId` said `undefined` | the fall-through 404 |
| `GET /todos/7/done` | not a todo's address | the fall-through 404 |
| `GET /users/7` | not a todo's address | the fall-through 404 |

All four say the same thing: `404 {"error":"not_found"}`. That is deliberate.

### Why `/todos/abc` is not a 400

The tempting argument is that `abc` is *malformed*, and malformed input is a
400. But look at what 400 means in this project: **your request was wrong** —
something you *sent* failed a rule. A `GET` sends nothing. There is no body to
be wrong, only an address, and the true statement about `/todos/abc` is module
5's definition of 404: *there is nothing at this address.*

It is also the answer that leaks least. A client probing `/todos/1`,
`/todos/abc` and `/todos/99999` learns the same thing from all three, which is
the most a client that does not already know an id should learn.

(Real APIs disagree about this, and the ones that choose 400 are not wrong. The
point is to choose, say why, and be consistent — and this project's reason is
that the definition it has used since module 5 already covers the case.)

### The router, whole

```ts
const url = new URL(req.url ?? "/", "http://localhost");
const id = todoId(url.pathname);

if (req.method === "GET" && url.pathname === "/todos") { … }    // the list
if (req.method === "POST" && url.pathname === "/todos") { … }   // create
if (req.method === "GET" && id !== undefined) { … }             // one todo

send(res, 404, { error: "not_found" });
```

Three routes, still flat, still one `if` each, still the 404 last. `/todos` and
`/todos/7` share a prefix and never collide, because one route compares the
whole path and the other only matches when `todoId` found three pieces.

Modules 11 and 12 add one `if` each below the third — `PATCH` and `DELETE`, on
the same `id`. Neither will parse anything.
""",
    """
```bash
$ curl -s -o /dev/null -w '%{http_code}\\n' localhost:3000/todos/99
404
$ curl -s -o /dev/null -w '%{http_code}\\n' localhost:3000/todos/abc
404
$ curl -s -o /dev/null -w '%{http_code}\\n' localhost:3000/todos/1/done
404
$ curl -s -o /dev/null -w '%{http_code}\\n' localhost:3000/todos
200
```

Four addresses, and only the collection answers. `-w '%{http_code}'` prints
just the status, which is the fastest way to check a lot of routes at once.
""",
    pitfalls=[
        "Answering `/todos/abc` with a 400. There is no request body to be wrong — the address leads nowhere, which is what 404 says.",
        "Dropping the `parts.length !== 3` check. `/todos/1/done` reaches the route with id 1, and a URL nobody defined starts answering with a todo.",
        "Two different 404 bodies — `not_found` from the route and something else from the fall-through. A client should not be able to tell *why* nothing is there; module 15 makes one error shape the rule.",
        "Putting the `GET /todos/:id` route above `GET /todos` and worrying about order. They cannot collide: one compares the whole path, the other needs three pieces. Order only matters for routes that overlap.",
        "Treating a trailing slash as the same address. `/todos/1/` has four pieces and is a 404 here. That is a choice, and a common one — the stretch list has the other.",
    ],
    warmup=[
        _pq("A client sends `GET /todos/abc`. What should it get, and why?",
            ["404 — there is nothing at that address, which is exactly what 404 means",
             "400 — `abc` is not a valid id, so the request was malformed",
             "500 — the id could not be parsed",
             "200 with `null`"],
            0,
            "A `GET` sends no body, so nothing the client sent was wrong. The "
            "address simply leads nowhere."),
    ],
    exercises=[
        _pfix("todo-m10-notfound-fix1", "An address nobody defined",
              "`GET /todos/1/done` answers `200` with todo 1. So does "
              "`/todos/1/anything` and `/todos/1/x/y/z`. The API has sprouted "
              "addresses nobody designed.",
              _m10(idtext="""function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}
"""),
              _M10_FULL,
              [("\n".join([_POST_A, "GET /todos/1", "GET /todos/1/done", "GET /todos"]),
                "\n".join(["201 " + _TODO_A, "200 " + _TODO_A, _NF, "200 [" + _TODO_A + "]"]))],
              ["How many pieces does `/todos/1/done` split into? How many does a todo's address have?",
               "The collection name is checked. The shape is not.",
               "Check the number of pieces as well as what the second one says.",
               '`if (parts.length !== 3 || parts[1] !== "todos")`'],
              difficulty="Easy"),
        _pch("todo-m10-notfound-build", "The three-route router", "Medium",
             "Write the handler.\n\n"
             "* `GET /todos` → `200` with the store's array\n"
             "* `POST /todos` → `201` with the todo created from the body's `title`\n"
             "* `GET /todos/:id` → `200` with that todo, or `404` if there is no such todo\n"
             "* anything else → `404` with `{\"error\":\"not_found\"}`\n\n"
             "`idText`, `parseId` and `todoId` are written above. Parse the id "
             "once, at the top.",
             _M10_FULL,
             _M10_HANDLER.rstrip("\n"),
             [("\n".join([_POST_A, _POST_B, "GET /todos/2", "GET /todos/abc",
                          "GET /todos/9", "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "200 " + _TODO_B, _NF, _NF,
                          "200 [" + _TODO_A + "," + _TODO_B + "]"]))],
             ["The signature is module 9's — `async`, returning `Promise<void>`.",
              "Two lines before any route: the `new URL` parse, and `const id = todoId(url.pathname);`.",
              "The one-todo route matches on `req.method === \"GET\" && id !== undefined`.",
              "Inside it, `findTodo(id)` and two branches — 404 or 200 — each ending in `return`.",
              "`/todos/abc` needs no code of its own: `todoId` says `undefined`, and it falls through."]),
    ],
    quiz=[
        _pq("`GET /todos/99` and `GET /todos/abc` both answer 404. Which code produces each?",
            ["`/todos/99` gets the route's own 404; `/todos/abc` never matches the route and reaches the fall-through",
             "Both come from the route's own 404",
             "Both come from the fall-through",
             "`/todos/abc` comes from `parseId`"],
            0,
            "Different roads, same answer — and the client cannot tell them "
            "apart, which is the point."),
        _pq("Why can `GET /todos` and `GET /todos/:id` never match the same request?",
            ["One compares the whole path to `/todos`; the other needs `todoId` to find three pieces, and `/todos` has two",
             "Because the list route comes first",
             "Because `id` is `0` for `/todos`",
             "They can, and order decides which wins"],
            0,
            "Routes that cannot overlap do not care about order. That is worth "
            "knowing before module 20 turns the flat `if`s into a table."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M10_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in
                                (_M10_IDTEXT, _M10_PARSEID, _M10_TODOID, _M10_HANDLER))

_M10_FINAL = _pch(
    "todo-m10-build", "Module 10 build — every todo has an address", "Medium",
    "Write the three path functions and the handler.\n\n"
    "* `idText(pathname)` — the id's text for a path shaped `/todos/<something>`, "
    "otherwise `undefined`\n"
    "* `parseId(text)` — a whole number from 1, otherwise `undefined`\n"
    "* `todoId(pathname)` — both together\n"
    "* the handler — `GET /todos`, `POST /todos`, `GET /todos/:id`, and a 404 for "
    "everything else\n\n"
    "Eight requests. Look at the last four: an id nobody has, an id that is not a "
    "number, a path one piece too long, and a trailing slash. All four are 404, "
    "and none of them needs code of its own.",
    _M10_FULL,
    _M10_BUILD_BLANK,
    [("\n".join([_POST_A, _POST_B, "GET /todos/1", "GET /todos/2", "GET /todos/3",
                 "GET /todos/abc", "GET /todos/1/done", "GET /todos/"]),
      "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "200 " + _TODO_A, "200 " + _TODO_B,
                 _NF, _NF, _NF, _NF]))],
    ["`idText`: split on `/`, reject unless there are three pieces and the second is `todos`, return the third.",
     "`parseId`: `Number(text)`, then reject unless `Number.isInteger(id)` and `id >= 1`.",
     "`todoId`: call `idText`, return `undefined` if it did, otherwise `parseId` what it gave you. The compiler insists.",
     "The handler parses the URL and the id once, then three routes and the 404.",
     "`/todos/` gives `idText` an empty piece, `Number(\"\")` is 0, and `id < 1` sends it to the fall-through."],
)


_TODO_MODULES.append(_pmod(
    key="todo-one", number=10, phase="crud",
    title="GET /todos/:id — dynamic paths",
    what="split the pathname, parse the id, 404 when it isn't there",
    goal="Give every todo its own address, and answer 404 for an address with nothing at it.",
    why=_M10_WHY,
    est_minutes=50,
    builds_on=["todo-lookup", "todo-url", "todo-routing", "todo-create"],
    concepts=["path segments", "noUncheckedIndexedAccess", "Number and NaN",
              "Number.isInteger", "undefined in a return type", "404 vs 400"],
    deliverable="A todo you can fetch by its id — and the first 404 in the project "
                "that means a specific thing is missing.",
    objectives=[
        "Split a path into pieces and say which index holds the id, and why it is not 1",
        "Check both the shape and the collection of a path, and name a URL each check rejects",
        "Explain why `parts[2]` stays `string | undefined` after a length check",
        "Turn text into an id with `Number`, and name three inputs it converts without failing",
        "Reject `NaN`, fractions, zero and negatives with one condition",
        "Read the compile error `todoId` produces without its check, and trace the `undefined` to its source",
        "Argue that `/todos/abc` is a 404 rather than a 400, from what each status code means",
    ],
    endpoints=[
        _pep("GET", "/todos/:id", "Fetch one todo", "", "Todo", "200 · 404"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M10_BRIEF,
    syntax=_M10_SYNTAX,
    steps=[_M10_S1, _M10_S2, _M10_S3, _M10_S4],
    final_build=_M10_FINAL,
    acceptance=[
        "`curl -s localhost:3000/todos/1` returns the todo with id 1, after a create has made one.",
        "`curl -s -i localhost:3000/todos/99` returns 404 and `{\"error\":\"not_found\"}` when no todo has id 99.",
        "`curl -s -i localhost:3000/todos/abc` returns 404 — not 400, not 500.",
        "`curl -s -i localhost:3000/todos/1/done` returns 404 — the path has one piece too many.",
        "`curl -s -i localhost:3000/todos/` returns 404 — the empty piece is not id 0.",
        "`curl -s localhost:3000/todos` still returns the whole list: the two routes on `/todos` never collide.",
        "The handler calls `todoId(url.pathname)` exactly once, at the top.",
        "Deleting the `text === undefined` check from `todoId` stops the file compiling under `--strict --noUncheckedIndexedAccess`.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
curl -s -X POST localhost:3000/todos -d '{"title":"Write tests"}'

curl -s localhost:3000/todos/1          # Buy milk
curl -s localhost:3000/todos/2          # Write tests
curl -s -i localhost:3000/todos/3       # 404 — nobody made it
```

Then every way of not being an id. Each one is a 404, and it is worth predicting
*which* 404 — the route's or the fall-through's — before you run it:

```bash
for p in /todos/abc /todos/7.5 /todos/0 /todos/-1 /todos/ /todos/1/done /users/1; do
  printf '%-16s ' "$p"; curl -s -o /dev/null -w '%{http_code}\\n' "localhost:3000$p"
done
```

And the two that are lenient rather than wrong:

```bash
curl -s localhost:3000/todos/01         # todo 1 — Number("01") is 1
curl -s localhost:3000/todos/1e0        # todo 1 — so is Number("1e0")
```

Last, the one the compiler catches. Delete the `if (text === undefined)` check
from `todoId`, save, and run `npx tsc --noEmit --strict --noUncheckedIndexedAccess
server.ts`. Read the error, then put the check back. That error is this module.
""",
    reference="""// server.ts — module 10
//
// Every todo has its own address. The path has a part that varies, so the
// router takes the path apart — three small functions below — instead of
// comparing it whole.
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

// Module 3's lookup, written for this route seven modules early.
function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

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

// STRUCTURE. "/todos/7" → "7". Anything not shaped /todos/<something> →
// undefined: "/todos" (two pieces), "/todos/7/done" (four), "/users/7" (wrong
// collection). The first piece is always "" — nothing comes before the leading
// slash — which is why the id is at index 2.
//
// parts[2] is `string | undefined` even though the length is checked: the
// compiler does not count. The return type says so, honestly.
function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}

// VALUE. An id is a whole number from 1. Number() never fails — it answers
// NaN for "abc", 7.5 for "7.5", and 0 for "" — so every answer is checked.
// Number.isInteger rejects NaN and fractions in one call; `id < 1` rejects zero
// (including the zero that "/todos/" becomes) and negatives.
function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}

// COMPOSE. `return parseId(idText(pathname))` does not compile, and that is
// noUncheckedIndexedAccess doing its job: the undefined from parts[2] has
// reached a function that needs a string. Handle it where it arrives.
function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  // Parsed once, like the URL. PATCH (module 11) and DELETE (12) read the same
  // number and parse nothing.
  const id = todoId(url.pathname);

  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const data = JSON.parse(body);      // `any` — module 13 closes this
    const todo = addTodo(data.title);
    send(res, 201, todo);
    return;
  }

  // `id !== undefined` is the path half of the condition: true exactly when
  // the path is a todo's address. Inside, id is a number.
  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });   // a valid id nobody has
      return;
    }
    send(res, 200, todo);
    return;
  }

  // /todos/abc, /todos/1/done and /users/7 all arrive here. Not a 400: a GET
  // sends nothing that could be wrong — the address simply leads nowhere.
  send(res, 404, { error: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Module 9 left a promise: add `res.setHeader(\"Location\", \"/todos/\" + todo.id)` to the create route, just before the `send`. Then `curl -i` a create and follow the header. It answers now — which is exactly why it waited for this module.",
        "Make ids strict: after `Number(text)`, also require `String(id) === text`. Now `/todos/01` and `/todos/1e0` are 404s. Decide whether that is better, and write down who it is better for.",
        "Accept a trailing slash: make `/todos/1/` fetch todo 1. The change belongs in exactly one function — find it before you start typing.",
        "Answer `/todos/abc` with a 400 instead, and write the one-paragraph argument for it. Then compare it with step 4's. Both are defensible; the exercise is noticing that you had to choose.",
        "Add `GET /todos/:id/title` returning just the title as `{\"title\":\"…\"}`. Count which of the three path functions had to change, and whether the answer surprises you.",
    ],
    glossary=[
        _pgloss("path segment", "One piece of a URL path between slashes. `/todos/7` has three — `\"\"`, `todos` and `7` — because nothing comes before the leading slash."),
        _pgloss("path parameter", "A segment that varies, written `:id` in a contract. The part of the address that names *which* one."),
        _pgloss("split", "`s.split(sep)` — cut a string at every `sep` and return the pieces between, as an array."),
        _pgloss("NaN", "\"Not a number\" — what `Number` answers for text it cannot read. It is of type `number`, and it is not equal to itself."),
        _pgloss("Number.isInteger", "`true` only for whole numbers. `false` for `NaN`, fractions and `Infinity` — every kind of junk `Number` can produce."),
        _pgloss("noUncheckedIndexedAccess", "The compiler flag that types every array read as possibly `undefined`. Here it is what stops `/todos` from becoming a silent `NaN` lookup."),
        _pgloss("404 Not Found", "There is nothing at this address — whether the id is unknown or is not an id at all."),
    ],
    cheatsheet="""
```ts
// structure: "/todos/7" → "7", anything else → undefined
function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");               // ["", "todos", "7"]
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];                                  // string | undefined
}

// value: a whole number from 1, anything else → undefined
function parseId(text: string): number | undefined {
  const id = Number(text);                          // never fails — NaN instead
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}

// compose — the compiler insists on the check
function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}

// in the handler, once, at the top
const id = todoId(url.pathname);
if (req.method === "GET" && id !== undefined) {
  const todo = findTodo(id);
  if (todo === undefined) { send(res, 404, { error: "not_found" }); return; }
  send(res, 200, todo);
  return;
}
```

| Path | `todoId` | Answer |
|---|---|---|
| `/todos/1` | `1` | 200, or 404 if nobody has it |
| `/todos/abc` · `/todos/7.5` · `/todos/0` · `/todos/` | `undefined` | 404 (fall-through) |
| `/todos/1/done` · `/users/1` | `undefined` | 404 (fall-through) |
| `/todos/01` · `/todos/1e0` | `1` | lenient — `Number` reads both as 1 |

| `Number(…)` | Result | Caught by |
|---|---|---|
| `"abc"` | `NaN` | `Number.isInteger` |
| `"7.5"` | `7.5` | `Number.isInteger` |
| `""` | `0` | `id < 1` |
| `"-3"` | `-3` | `id < 1` |
""",
    self_check=[
        "Can you say what `\"/todos/7\".split(\"/\")` returns, element by element, and why the id is at index 2?",
        "Can you name a path each of `idText`'s two checks rejects that the other would let through?",
        "Can you explain why `parts[2]` is still `string | undefined` after `parts.length !== 3` has been ruled out?",
        "Can you give three strings `Number` converts without failing, and the check that catches each?",
        "Can you say why `id === NaN` never works?",
        "Can you read the compile error from `parseId(idText(pathname))` and say where the `undefined` came from?",
        "Can you argue for 404 over 400 on `/todos/abc` from what the two codes mean?",
    ],
    review=[
        _pq("Where does the `undefined` in `parseId(idText(pathname))`'s compile error come from?",
            ["`parts[2]` — an array read under `noUncheckedIndexedAccess`, passed on through `idText`'s return type",
             "`pathname.split` returning `undefined` for an empty path",
             "`Number` returning `undefined` for bad text",
             "`url.pathname` being optional"],
            0,
            "It is created at the index, declared honestly in a return type, and "
            "stopped at the first function that needs a string."),
        _pq("Which of these reaches the route's own 404 rather than the fall-through?",
            ["`GET /todos/99` when no todo has id 99",
             "`GET /todos/abc`",
             "`GET /todos/1/done`",
             "`GET /users/1`"],
            0,
            "Only a valid id gets inside the route. Everything `todoId` rejects "
            "never matches it and falls through."),
        _pq("`parseId(\"\")` without the `id < 1` check returns what, and which request produces that text?",
            ["`0` — and `/todos/` splits into three pieces with an empty last one",
             "`NaN`, from `/todos`",
             "`undefined`, from `/todos/`",
             "It throws"],
            0,
            "`Number(\"\")` is zero. A trailing slash is the everyday way to hand "
            "your parser an empty string."),
        _pq("What does `findTodo(id)!` cost when the todo does not exist?",
            ["A `200` with an empty body — `JSON.stringify(undefined)` produces no text, and nothing errors",
             "A compile error",
             "A 404, because `!` checks for `undefined`",
             "A 500 from the replayer's boundary"],
            0,
            "`!` removes the check without removing the case. Module 3 named this "
            "cost; module 10 is the first route that would pay it."),
        _pq("Why is `/todos/abc` a 404 in this project rather than a 400?",
            ["A `GET` sends nothing that could be wrong; the true statement is that nothing is at that address",
             "Because 400 is reserved for POST",
             "Because the replayer cannot send a 400",
             "Because `parseId` returns `undefined`"],
            0,
            "400 is *your request was wrong*. 404 is *nothing is here*. Only one of "
            "those is true of a GET for an address with no todo behind it."),
        _pq("Module 2 argued ids should come from a counter, not `todos.length + 1`. Why does that matter to this module?",
            ["`GET /todos/2` must mean the same todo for as long as it exists — an id that could be reused would fetch a different one",
             "It does not; any unique number works",
             "Because `Number` cannot parse large ids",
             "Because the counter makes `parseId` faster"],
            0,
            "An address is a promise. Module 12 is the first module that could "
            "break it, and the counter is why it will not."),
    ],
    milestone="Every todo has an address. A client that created one can fetch it by "
              "the id it was given, anything that is not a todo's address is a "
              "404, and the compiler caught the one case — `/todos`, with no third "
              "piece — that would otherwise have been a silent wrong answer.",
))
