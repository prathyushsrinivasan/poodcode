# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 17 — Filtering with query strings.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-16's program pieces.
#
# OPENS PHASE 5. `GET /todos` can be asked a question: `?done=true`,
# `?q=milk`, or both. Module 7 promised this would be additive — routes match
# on `url.pathname`, so a query string never broke one — and it is: one route
# changes, and nothing else does.
#
# A DECISION THE PLAN MADE, REVERSED: the roadmap said "a default for
# `?done=banana`". This module answers it with a 400 naming `done` instead, and
# says why. Three modules have argued that input the API cannot understand is
# refused, not guessed at; ignoring `?done=flase` would answer EVERY todo to a
# client that asked for the unfinished ones — module 9's quiet wrong answer, in
# a new place. The DEFAULT the plan wanted is still here, for the case it is
# right: a parameter that is absent. Unknown parameters (`?colour=red`) are
# ignored, which the module also argues — a different question with a different
# answer.
#
# `.map(` ARRIVES HERE, not in 14. The scope table had it at 14 for "collecting
# one error per bad field", and when module 14 was written nothing in it wanted
# a map: errors are collected with `push`, because each field is checked by
# different code. Its first honest use is here, next to its sibling — `.filter`
# keeps some elements, `.map` turns each into something else — in the plain
# programs that print a list as its titles. Module 20's tests lean on it.
#
# `/boom` IS RETIRED, with an em-dash row, as module 16 promised.
#
# THE GRADABLE BUGS: the string "false" is truthy (a `?done=false` that
# returns the done ones); `""` is falsy (a `?done=` that is waved through as
# "no filter"); a `filter` whose result is thrown away; a case-sensitive search;
# `?done=banana` silently read as false; and a route that matches `req.url`
# rather than the pathname, so any query string 404s it.
#
# NO `.sort(`, NO `.slice(` in these programs, comments included — module 18's.
# ---------------------------------------------------------------------------

_M17_QUERY = """type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
};

function listQueryFrom(params: URLSearchParams): ListQuery | FieldError[] {
  const query: ListQuery = { done: undefined, q: undefined };
  const errors: FieldError[] = [];
  const done = params.get("done");
  if (done === "true") {
    query.done = true;
  } else if (done === "false") {
    query.done = false;
  } else if (done !== null) {
    errors.push({ field: "done", message: "must be true or false" });
  }
  const q = params.get("q");
  if (q !== null) {
    query.q = q;
  }
  if (errors.length > 0) {
    return errors;
  }
  return query;
}
"""

_M17_LIST = """function listTodos(query: ListQuery): Todo[] {
  let items = todos;
  if (query.done !== undefined) {
    items = items.filter((t) => t.done === query.done);
  }
  if (query.q !== undefined) {
    const q = query.q.toLowerCase();
    items = items.filter((t) => t.title.toLowerCase().includes(q));
  }
  return items;
}
"""

_M17_LIST_ROUTE = """  if (req.method === "GET" && url.pathname === "/todos") {
    const query = listQueryFrom(url.searchParams);
    if (Array.isArray(query)) {
      sendError(res, { kind: "validation", fields: query });
      return;
    }
    send(res, 200, listTodos(query));
    return;
  }"""

_M16_LIST_ROUTE = """  if (req.method === "GET" && url.pathname === "/todos") {
    send(res, 200, todos);
    return;
  }"""

assert _M16_ROUTE.count(_M16_LIST_ROUTE) == 1 and _M16_ROUTE.count(_M16_BOOM) == 1
_M17_ROUTE = _M16_ROUTE.replace(_M16_BOOM, "").replace(_M16_LIST_ROUTE, _M17_LIST_ROUTE)


def _m17(route=_M17_ROUTE, query=_M17_QUERY, listtodos=_M17_LIST):
    """A module-17 server program: module 16's, with a list that can be asked."""
    return _server_bare("\n\n".join(p.rstrip("\n") for p in
                                    (_M10_STORE, listtodos, _M10_SEND, _M10_READBODY,
                                     _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                     _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                     _M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE,
                                     _M14_CREATE, _M14_CHANGES, query,
                                     _M16_APIERROR, _M16_REPLY, _M15_SENDERROR,
                                     route, _M16_PARSE, _M16_BOUNDARY) if p))


_M17_FULL = _m17()

# --- Step 1's plain program: what a query string holds ----------------------
_M17_DONEFILTER = """function doneFilter(target: string): string {
  const url = new URL(target, "http://localhost");
  const done = url.searchParams.get("done");
  if (done === null) {
    return "every todo";
  }
  if (done === "true") {
    return "done only";
  }
  if (done === "false") {
    return "not done only";
  }
  return "400: done must be true or false";
}
"""

_M17_S1_PRINTS = """
console.log(doneFilter("/todos"));
console.log(doneFilter("/todos?done=true"));
console.log(doneFilter("/todos?done=false"));
console.log(doneFilter("/todos?done=banana"));
console.log(doneFilter("/todos?done="));
console.log(doneFilter("/todos?q=milk&done=false"));
console.log(doneFilter("/todos?done=true&done=false"));
console.log(doneFilter("/todos?DONE=true"));
"""
_M17_S1_OUT = "\n".join(["every todo", "done only", "not done only", "400: done must be true or false",
                         "400: done must be true or false", "not done only", "done only", "every todo"])


def _m17_s1(fn=_M17_DONEFILTER):
    return _plain(fn.rstrip("\n") + "\n" + _M17_S1_PRINTS)


# --- Step 2's plain program: filter and map over a fixed list ---------------
_M17_S2_STORE = """type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [
  { id: 1, title: "Buy milk", done: false },
  { id: 2, title: "Write tests", done: true },
  { id: 3, title: "Buy oat milk", done: false },
  { id: 4, title: "Ship it", done: true },
];

type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
};
"""

_M17_TITLES = """function titles(list: Todo[]): string {
  return JSON.stringify(list.map((t) => t.title));
}
"""

_M17_S2_PRINTS = """
console.log(titles(listTodos({ done: undefined, q: undefined })));
console.log(titles(listTodos({ done: true, q: undefined })));
console.log(titles(listTodos({ done: false, q: undefined })));
console.log(titles(listTodos({ done: undefined, q: "MILK" })));
console.log(titles(listTodos({ done: false, q: "oat" })));
console.log(titles(listTodos({ done: true, q: "milk" })));
console.log(todos.length);
"""
_M17_S2_OUT = "\n".join([
    '["Buy milk","Write tests","Buy oat milk","Ship it"]',
    '["Write tests","Ship it"]',
    '["Buy milk","Buy oat milk"]',
    '["Buy milk","Buy oat milk"]',
    '["Buy oat milk"]',
    "[]",
    "4",
])


def _m17_s2(listtodos=_M17_LIST, titles=_M17_TITLES):
    return _plain("\n\n".join(p.rstrip("\n") for p in (_M17_S2_STORE, listtodos, titles))
                  + "\n" + _M17_S2_PRINTS)


_POST_OAT = 'POST /todos {"title":"Buy oat milk"}'
_TODO_OAT3 = '{"id":3,"title":"Buy oat milk","done":false}'
_TODO_B_DONE = '{"id":2,"title":"Write tests","done":true}'
_M17_SETUP = [_POST_A, _POST_B, _POST_OAT, 'PATCH /todos/2 {"done":true}']
_M17_SETUP_OUT = ["201 " + _TODO_A, "201 " + _TODO_B, "201 " + _TODO_OAT3, "200 " + _TODO_B_DONE]


def _arr(*todos):
    return "200 [" + ",".join(todos) + "]"


_M17_WHY = (
    "`GET /todos` answers with every todo, every time. A client that wants the "
    "unfinished ones downloads the lot and throws most of it away — which is "
    "fine with five and absurd with five thousand, and a phone on a bad "
    "connection pays for every byte. The list is the one resource in the API "
    "you cannot ask a question. And the place to ask it has been sitting in "
    "every URL since module 6: everything after the `?`, which your router has "
    "been carefully ignoring ever since."
)

_M17_BRIEF = """
### The whole module in one line

Let a client ask the list a question — `?done=false`, `?q=milk` — and refuse a
question it cannot understand.

### The query string

```
GET /todos?done=false&q=milk
    ──────┬─────────────────
    pathname  search: ?done=false&q=milk
```

Module 6 built `url` from `req.url` and module 7 routed on `url.pathname`, which
is why a query string has never broken a route. Now the other half gets read:

```ts
url.searchParams.get("done")     // "false"   — always a string
url.searchParams.get("q")        // "milk"
url.searchParams.get("sort")     // null      — not there at all
```

### Three answers, not two

| Request | `get("done")` | Means |
|---|---|---|
| `/todos` | `null` | no filter — every todo |
| `/todos?done=true` | `"true"` | done only |
| `/todos?done=false` | `"false"` | not done only |
| `/todos?done=banana` | `"banana"` | **400** — a question we cannot answer |

Absent is not wrong: it means *don't filter*. But present-and-meaningless is a
client mistake — the same rule as a patch in module 13.

### Two array methods

```ts
todos.filter((t) => t.done)       // keep the ones where this is true
todos.map((t) => t.title)         // turn each one into something else
```

Neither changes `todos`. Both hand back a new array.
"""

_M17_SYNTAX = [
    _syn(
        'url.searchParams.get("done")',
        "The value of one query-string parameter — always a **string**, or "
        "`null` if the parameter is not there at all.",
        """
const url = new URL("/todos?done=false", "http://localhost");
url.searchParams.get("done");    // "false"  — the string, not the boolean
url.searchParams.get("q");       // null
""",
        "`null`, not `undefined` — the one API in this project that says it that "
        "way. And `\"false\"` is a non-empty string, so it is *truthy*: compare "
        "with the exact text.",
    ),
    _syn(
        "items.filter((t) => t.done === query.done)",
        "A new array of the elements for which the function returns `true`. The "
        "original is untouched.",
        """
const done = todos.filter((t) => t.done);
todos.length;   // unchanged
""",
        "`filter` returns the result; it does not change the array it was called "
        "on. `items.filter(…);` on a line of its own does nothing at all.",
    ),
    _syn(
        "list.map((t) => t.title)",
        "A new array with each element turned into whatever the function returns "
        "— here, a list of todos into a list of titles.",
        """
[{ id: 1, title: "Buy milk", done: false }].map((t) => t.title);
// ["Buy milk"]
""",
        "Same length in, same length out. `filter` chooses which; `map` changes "
        "what. This module uses `map` to print a list readably; module 20's "
        "tests use it to compare one field of many todos.",
    ),
    _syn(
        "text.toLowerCase().includes(q)",
        "`toLowerCase()` gives the string in lower case; `includes(q)` asks "
        "whether `q` appears anywhere in it.",
        """
"Buy Oat Milk".toLowerCase();              // "buy oat milk"
"buy oat milk".includes("milk");           // true
"buy oat milk".includes("Milk");           // false — case matters
""",
        "Lower-case *both* sides, or a search for `MILK` finds nothing. And "
        "`\"anything\".includes(\"\")` is `true` — an empty search matches all.",
    ),
    _syn(
        "} else if (done !== null) {",
        "A chain of `if`s where only the first match runs — the last branch "
        "catches everything the others did not.",
        """
if (done === "true") {
  query.done = true;
} else if (done === "false") {
  query.done = false;
} else if (done !== null) {
  errors.push({ field: "done", message: "must be true or false" });
}
""",
        "If none match — `done` is `null` — nothing happens, and the filter stays "
        "off. Absent is not an error.",
    ),
    _syn(
        "let items = todos;",
        "A variable that can be pointed at a different array later — here, at "
        "each filtered version in turn.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — reading the query string.
# ---------------------------------------------------------------------------

_M17_S1 = _pstep(
    "params", "What a query string holds",
    "`searchParams.get`, `null` for absent, and why the text `\"false\"` is not false.",
    """
Everything after the `?` in a URL is the **query string**: `name=value` pairs
joined by `&`. The `URL` object you have built on every request since module 6
has already split it up:

```ts
const url = new URL("/todos?done=false&q=milk", "http://localhost");
url.pathname                        // "/todos"
url.searchParams.get("done")        // "false"
url.searchParams.get("q")           // "milk"
url.searchParams.get("sort")        // null
```

### Two surprises

**It is always a string.** A URL is text, so `?done=false` gives you the
five-character string `"false"` — and a non-empty string is *truthy*:

```ts
if (url.searchParams.get("done")) {    // true for "false" too!
```

So compare with the exact text: `done === "true"`, `done === "false"`.

**Absent is `null`, not `undefined`.** And `null` is not the only way to be
empty-ish: `?done=` and a bare `?done` both give `""`, which is present but says
nothing — and is *falsy*, so `if (!done)` would wave it through as though the
parameter were not there.

### Three answers

```ts
function doneFilter(target: string): string {
  const url = new URL(target, "http://localhost");
  const done = url.searchParams.get("done");
  if (done === null) {
    return "every todo";
  }
  if (done === "true") {
    return "done only";
  }
  if (done === "false") {
    return "not done only";
  }
  return "400: done must be true or false";
}
```

Absent → no filter. `"true"` or `"false"` → a filter. Anything else — including
`""` — is a question the API cannot answer, and a client that asked it should be
told.

### The small print

* `?done=true&done=false` — `get` returns the **first**. (`getAll` returns both.)
* `?DONE=true` — names are case-sensitive; this is not `done` at all.
* `?q=oat%20milk` and `?q=oat+milk` both arrive as `"oat milk"`: `searchParams`
  decodes for you.
""",
    """
Your `doneFilter` answers:

```
/todos                          every todo
/todos?done=true                done only
/todos?done=false               not done only
/todos?done=banana              400
/todos?done=                    400
/todos?q=milk&done=false        not done only
/todos?done=true&done=false     done only
/todos?DONE=true                every todo
```

`?done=false` saying *done only* is the truthy-string bug; `?done=` saying *every
todo* is the falsy-empty-string one.
""",
    pitfalls=[
        "`?done=false` returns the finished todos — `if (done)` tested the *string* `\"false\"`, which is truthy. Compare with the exact text.",
        "`?done=` returns every todo instead of a 400 — `if (!done)` treated the empty string as absent. Absent is `=== null`; empty is present and wrong.",
        "Comparing with `undefined`. `searchParams.get` answers `null` for a missing parameter, and `null !== undefined`.",
        "Routing on `req.url === \"/todos\"`. It includes the query string, so every filtered request misses the route. Module 7 routed on `url.pathname` for exactly this day.",
        "Decoding by hand. `searchParams.get` has already turned `%20` and `+` into spaces.",
    ],
    warmup=[
        _pq("`new URL(\"/todos?done=false\", base).searchParams.get(\"done\")` — what is it?",
            ["The string `\"false\"` — which is truthy",
             "The boolean `false`",
             "`null`",
             "`undefined`"],
            0,
            "A URL is text. Turning `\"false\"` into `false` is your job, and "
            "`if (done)` does not do it."),
    ],
    exercises=[
        _pex("todo-m17-params-1", "Read the parameter",
             "Get the value of the `done` parameter from the URL's query string.",
             _m17_s1(),
             'url.searchParams.get("done")',
             [("", _M17_S1_OUT)],
             ["The URL object has already split the query string up.",
              "Its `searchParams` has a method that takes a name.",
              '`url.searchParams.get("done")`']),
        _pfix("todo-m17-params-fix1", "False is true",
              "`/todos?done=false` answers `done only`. So does `?done=banana`.",
              _m17_s1(_M17_DONEFILTER.replace('  if (done === "true") {', "  if (done) {")),
              _m17_s1(),
              [("", _M17_S1_OUT)],
              ["What type is `done` after the `null` check?",
               "Is the string `\"false\"` truthy?",
               '`if (done === "true") {`'],
              difficulty="Intro"),
        _pfix("todo-m17-params-fix2", "Empty is not absent",
              "`/todos?done=` answers `every todo`, as though the client had not "
              "mentioned `done` at all.",
              _m17_s1(_M17_DONEFILTER.replace("  if (done === null) {", "  if (!done) {")),
              _m17_s1(),
              [("", _M17_S1_OUT)],
              ["What does `get` return for `?done=` — and is it the same as for no `done` at all?",
               "`\"\"` is falsy. `null` is what absent looks like.",
               "`if (done === null) {`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("`?done=` (nothing after the `=`). What does `get(\"done\")` return, and what should the API do?",
            ["`\"\"` — present but meaningless, so a 400",
             "`null` — no filter",
             "`false` — not done only",
             "`undefined` — no filter"],
            0,
            "Present and meaningless is a client mistake. Only a parameter that is "
            "not there at all means *no filter*."),
        _pq("Why does `url.pathname === \"/todos\"` still match `/todos?done=true`?",
            ["`pathname` is only the path — the query string is in `search` and `searchParams`",
             "Because the query string is ignored by HTTP",
             "It does not match",
             "Because `URL` removes unknown parameters"],
            0,
            "Module 7 routed on the pathname so that this module would be one "
            "route changing, not a router."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — filter and map.
# ---------------------------------------------------------------------------

_M17_S2 = _pstep(
    "filter", "`filter` keeps, `map` turns",
    "Two array methods, a variable that follows the narrowing list, and a case-blind search.",
    """
```ts
todos.filter((t) => t.done)
```

`filter` calls the arrow once per element and builds a **new** array of the ones
it returned `true` for. `todos` itself is untouched — which matters, because
`todos` is the store.

Its sibling:

```ts
todos.map((t) => t.title)       // ["Buy milk", "Write tests", …]
```

`map` also calls the arrow once per element, and builds a new array of whatever
it *returned*. Same length in and out. `filter` decides **which**; `map` decides
**what**. This module uses `map` for one small job — printing a list as its
titles, so you can read it — and module 20's tests use it for the same reason.

### Filters that compose

```ts
function listTodos(query: ListQuery): Todo[] {
  let items = todos;
  if (query.done !== undefined) {
    items = items.filter((t) => t.done === query.done);
  }
  if (query.q !== undefined) {
    const q = query.q.toLowerCase();
    items = items.filter((t) => t.title.toLowerCase().includes(q));
  }
  return items;
}
```

`items` starts as the whole store and is re-pointed at each narrower list in
turn. A filter that was not asked for is simply skipped. Both asked for — both
applied.

**`items = items.filter(…)`, not `items.filter(…)`.** `filter` *returns* the
result. Called on a line of its own, it builds the new array and throws it away,
and every todo comes back.

### A search a person would expect

`?q=milk` should find *Buy Milk*, *buy oat milk* and *MILK!* — people do not
type in the case the title was saved in. So lower-case both sides:

```ts
"Buy Oat Milk".toLowerCase().includes("MILK".toLowerCase())   // true
```

`q` is lower-cased once, outside the arrow, rather than once per todo.

(`includes("")` is `true`, so `?q=` matches everything. That is a reasonable
answer to an empty search, and nothing needs to be done about it.)
""",
    """
Against a store of four — *Buy milk*, *Write tests* ✓, *Buy oat milk*,
*Ship it* ✓ — your `listTodos` answers:

```
(no filter)            ["Buy milk","Write tests","Buy oat milk","Ship it"]
done: true             ["Write tests","Ship it"]
done: false            ["Buy milk","Buy oat milk"]
q: "MILK"              ["Buy milk","Buy oat milk"]
done: false, q: "oat"  ["Buy oat milk"]
done: true, q: "milk"  []
todos.length           4
```

The last line is the store, untouched by any of it.
""",
    pitfalls=[
        "Every filter returns everything — `items.filter(…)` on a line of its own. `filter` returns the new array; assign it: `items = items.filter(…)`.",
        "`?q=MILK` finds nothing — only the title was lower-cased, or neither was. Lower-case both sides.",
        "`const items = todos;` — then it cannot be re-pointed at the filtered list. It needs `let`.",
        "Expecting `filter` to remove from the store. It never changes the array it is called on; the store keeps every todo, which is exactly right here.",
        "Using `map` to filter — `todos.map((t) => t.done ? t : undefined)`. That keeps the length and leaves holes of `undefined`. Choosing *which* is `filter`'s job.",
    ],
    warmup=[
        _pq("After `const done = todos.filter((t) => t.done);`, what is `todos.length`?",
            ["Unchanged — `filter` returns a new array and leaves the old one alone",
             "The number of done todos",
             "0",
             "It depends on the filter"],
            0,
            "Which is why it is safe to filter the store directly."),
    ],
    exercises=[
        _pex("todo-m17-filter-1", "Titles, for reading",
             "Turn the list of todos into a list of their titles.",
             _m17_s2(),
             "list.map((t) => t.title)",
             [("", _M17_S2_OUT)],
             ["One title per todo — same length in and out.",
              "That is `map`, not `filter`.",
              "`list.map((t) => t.title)`"]),
        _pfix("todo-m17-filter-fix1", "A filter that filters nothing",
              "Every query answers all four todos. `?done=true` included.",
              _m17_s2(_M17_LIST.replace("    items = items.filter((t) => t.done === query.done);",
                                        "    items.filter((t) => t.done === query.done);")
                               .replace("    items = items.filter((t) => t.title.toLowerCase().includes(q));",
                                        "    items.filter((t) => t.title.toLowerCase().includes(q));")),
              _m17_s2(),
              [("", _M17_S2_OUT)],
              ["Does `filter` change the array it is called on?",
               "Where does the filtered array go?",
               "`items = items.filter(…)` — in both places."],
              difficulty="Easy"),
        _pfix("todo-m17-filter-fix2", "MILK finds nothing",
              "`q: \"MILK\"` answers `[]`. So would *Milk*. Only exactly `milk` works.",
              _m17_s2(_M17_LIST.replace("    const q = query.q.toLowerCase();", "    const q = query.q;")),
              _m17_s2(),
              [("", _M17_S2_OUT)],
              ["The titles are lower-cased before comparing. Is the search text?",
               "Both sides have to be in the same case.",
               "`const q = query.q.toLowerCase();`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("What is the difference between `filter` and `map`?",
            ["`filter` chooses which elements to keep; `map` turns each element into something else",
             "`filter` changes the array; `map` does not",
             "`map` is faster",
             "`map` can only return strings"],
            0,
            "Which versus what. Both leave the original alone and return a new array."),
        _pq("Why is `listTodos`'s `items` declared with `let`?",
            ["It is re-pointed at each narrower list as filters are applied",
             "Because `filter` needs `let`",
             "So the store can be changed",
             "No reason; `const` works too"],
            0,
            "Each filter produces a new array, and `items` follows along."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the query, checked.
# ---------------------------------------------------------------------------

_M17_S3_SCRIPT = "\n".join(_M17_SETUP + ["GET /todos?done=true", "GET /todos?done=false", "GET /todos",
                                         "GET /todos?done=banana", "GET /todos?done=", "GET /todos?done=TRUE"])
_M17_S3_OUT = "\n".join(_M17_SETUP_OUT + [_arr(_TODO_B_DONE), _arr(_TODO_A, _TODO_OAT3),
                                          _arr(_TODO_A, _TODO_B_DONE, _TODO_OAT3),
                                          _v(_FE_DONE), _v(_FE_DONE), _v(_FE_DONE)])

_M17_QUERY_LENIENT = _M17_QUERY.replace("""  if (done === "true") {
    query.done = true;
  } else if (done === "false") {
    query.done = false;
  } else if (done !== null) {
    errors.push({ field: "done", message: "must be true or false" });
  }""", """  if (done !== null) {
    query.done = done === "true";
  }""")
assert _M17_QUERY_LENIENT != _M17_QUERY

_M17_S3 = _pstep(
    "query", "Refuse the question you cannot answer",
    "`listQueryFrom`, a validation 400 for a query string, and the plan's `?done=banana` default — declined.",
    """
Everything a client sends is input, and the query string is no exception. It
gets checked the way a body does, and answers in the same shape:

```ts
type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
};

function listQueryFrom(params: URLSearchParams): ListQuery | FieldError[] {
  const query: ListQuery = { done: undefined, q: undefined };
  const errors: FieldError[] = [];
  const done = params.get("done");
  if (done === "true") {
    query.done = true;
  } else if (done === "false") {
    query.done = false;
  } else if (done !== null) {
    errors.push({ field: "done", message: "must be true or false" });
  }
  const q = params.get("q");
  if (q !== null) {
    query.q = q;
  }
  if (errors.length > 0) {
    return errors;
  }
  return query;
}
```

It is module 14's `changesFrom` in a new place: a value, or a list of what was
wrong — and the route tells them apart the same way:

```ts
if (req.method === "GET" && url.pathname === "/todos") {
  const query = listQueryFrom(url.searchParams);
  if (Array.isArray(query)) {
    sendError(res, { kind: "validation", fields: query });
    return;
  }
  send(res, 200, listTodos(query));
  return;
}
```

### Why `?done=banana` is a 400

The plan for this module said to give `?done=banana` a *default* — treat it as
no filter, or as `false`. It is worth seeing why that was reversed.

A client that sends `?done=flase` — a typo — wants the unfinished todos. A
default answers with *every* todo, or the wrong half, with a 200. The client has
no way to know its question was not understood; the list just looks slightly
wrong. That is module 9's sin exactly — a quiet wrong answer — and three modules
have been spent removing it from the body. A query string gets the same rule:

* **absent** — `done` is not there → no filter. That is the default, and it is right.
* **understood** — `"true"` / `"false"` → the filter.
* **present and not understood** → `400`, naming `done`.

### And `?colour=red`?

Ignored. That is a *different* question: not a value the API cannot read, but a
parameter it does not know. Clients add parameters as they evolve, and older
servers are expected to let them through — refusing unknown parameters would
break every client that is one version ahead of you. Unknown *names* are
ignored; unintelligible *values* are refused.
""",
    """
```bash
$ curl -s 'localhost:3000/todos?done=false'
[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy oat milk","done":false}]

$ curl -s -i 'localhost:3000/todos?done=banana'
HTTP/1.1 400 Bad Request
{"error":"validation","fields":[{"field":"done","message":"must be true or false"}]}
```

Quote the URL in the shell: an unquoted `&` would start a background job.
""",
    pitfalls=[
        "`?done=banana` answers the unfinished todos with a 200 — `query.done = done === \"true\"` turns every value that is not `\"true\"` into `false`. A question you cannot read is a 400, not a guess.",
        "`?done=TRUE` accepted. The API documents `true` and `false`; accepting other spellings is a promise you then have to keep for ever. Refuse, and name the field.",
        "Refusing `?colour=red`. An unknown parameter is not a mistake — it may be from a newer client. Only values you cannot understand are refused.",
        "A `400` with a different shape from the body's. Query or body, a client reads one error format.",
        "Forgetting the quotes around the URL in curl: `curl localhost:3000/todos?done=false&q=milk` runs `q=milk` as a separate shell command.",
    ],
    warmup=[
        _pq("A client sends `GET /todos?done=flase`. What should it get?",
            ["400 naming `done` — the value was present and not understood",
             "Every todo, as if there were no filter",
             "The unfinished todos",
             "404"],
            0,
            "Any answer but a 400 is a guess, delivered with a 200, to a client that "
            "has no way to know."),
    ],
    exercises=[
        _pex("todo-m17-query-1", "Refuse an unreadable filter",
             "`listQueryFrom` answered with a list of problems. Send them as a "
             "validation 400, exactly as the write routes do.",
             _M17_FULL,
             """    const query = listQueryFrom(url.searchParams);
    if (Array.isArray(query)) {
      sendError(res, { kind: "validation", fields: query });""",
             [(_M17_S3_SCRIPT, _M17_S3_OUT)],
             ["Hand `url.searchParams` to `listQueryFrom`.",
              "A list means refused — `Array.isArray`.",
              "`sendError(res, { kind: \"validation\", fields: query });`"]),
        _pfix("todo-m17-query-fix1", "Banana means false",
              "`GET /todos?done=banana` answers `200` with the unfinished todos. "
              "So does `?done=flase`, and a client with that typo will never know.",
              _m17(query=_M17_QUERY_LENIENT),
              _M17_FULL,
              [(_M17_S3_SCRIPT, _M17_S3_OUT)],
              ["What does `done === \"true\"` make of `\"banana\"`?",
               "There are three cases, not two: true, false, and not understood.",
               "`if (done === \"true\") { … } else if (done === \"false\") { … } else if (done !== null) { errors.push({ field: \"done\", message: \"must be true or false\" }); }`"],
              difficulty="Easy"),
        _pch("todo-m17-query-build", "Write listQueryFrom", "Medium",
             "Write `listQueryFrom(params)`.\n\n"
             "* `done`: absent → `undefined`; `\"true\"` / `\"false\"` → the "
             "boolean; anything else → `done: must be true or false`\n"
             "* `q`: absent → `undefined`; otherwise the text as given\n"
             "* any errors → the list; otherwise the `ListQuery`\n\n"
             "`ListQuery` is declared above it.",
             _M17_FULL,
             _M17_QUERY.split("function listQueryFrom", 1)[1].split("{\n", 1)[1].rsplit("\n}", 1)[0],
             [(_M17_S3_SCRIPT, _M17_S3_OUT),
              ("\n".join(_M17_SETUP + ["GET /todos?q=milk", "GET /todos?done=false&q=oat", "GET /todos?done=1"]),
               "\n".join(_M17_SETUP_OUT + [_arr(_TODO_A, _TODO_OAT3), _arr(_TODO_OAT3), _v(_FE_DONE)]))],
             ["`const query: ListQuery = { done: undefined, q: undefined };` and `const errors: FieldError[] = [];`",
              "`const done = params.get(\"done\");` — then `if … else if … else if (done !== null)`.",
              "`const q = params.get(\"q\"); if (q !== null) { query.q = q; }`",
              "`if (errors.length > 0) { return errors; } return query;`"]),
    ],
    quiz=[
        _pq("Why is an unknown *parameter* ignored, when an unreadable *value* is refused?",
            ["An unknown name may come from a newer client and harms nothing; a value you cannot read means you cannot answer the question asked",
             "Unknown parameters are refused too",
             "Because `searchParams` drops them",
             "No reason; it is arbitrary"],
            0,
            "Two different questions. Ignoring names keeps old servers working with "
            "new clients; refusing values keeps answers honest."),
        _pq("The plan said to default `?done=banana`. What does a default cost the client?",
            ["A 200 with the wrong list — and no way to find out its question was misread",
             "Nothing",
             "A slower response",
             "A 404"],
            0,
            "Defaults are right for *absent*. For present-and-wrong they turn a "
            "client's mistake into your silent wrong answer."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — search, together.
# ---------------------------------------------------------------------------

_M17_S4_SCRIPT = "\n".join(_M17_SETUP + ["GET /todos?q=milk", "GET /todos?q=MILK&done=false",
                                         "GET /todos?q=oat%20milk", "GET /todos?q=oat+milk",
                                         "GET /todos?q=tests&done=false", "GET /todos?q=",
                                         "GET /todos?colour=red", "GET /boom"])
_M17_S4_OUT = "\n".join(_M17_SETUP_OUT + [_arr(_TODO_A, _TODO_OAT3), _arr(_TODO_A, _TODO_OAT3),
                                          _arr(_TODO_OAT3), _arr(_TODO_OAT3), "200 []",
                                          _arr(_TODO_A, _TODO_B_DONE, _TODO_OAT3),
                                          _arr(_TODO_A, _TODO_B_DONE, _TODO_OAT3), _NF])

_M17_ROUTE_BY_URL = _M17_ROUTE.replace(
    '  if (req.method === "GET" && url.pathname === "/todos") {',
    '  if (req.method === "GET" && req.url === "/todos") {')
assert _M17_ROUTE_BY_URL != _M17_ROUTE

_M17_S4 = _pstep(
    "search", "Search, and both at once",
    "`?q=`, filters that compose, a route that must match the pathname — and `/boom` retired.",
    """
`?q=milk` finds every todo whose title contains *milk*, in any case. Combined
with `done`, both filters apply:

```
GET /todos?q=milk                  every todo mentioning milk
GET /todos?q=milk&done=false       …that is not done yet
GET /todos?q=oat%20milk            a space, encoded
GET /todos?q=oat+milk              the same space, the other way
```

The order the parameters are written in does not matter: `listTodos` always
applies `done` first and `q` second, and a todo has to pass both either way.

### The route must match the pathname

```ts
if (req.method === "GET" && url.pathname === "/todos") {
```

Every route since module 7 has compared `url.pathname`, and this is the module
that collects on it. `req.url` is `/todos?q=milk` — path *and* query — so a
route written as `req.url === "/todos"` matches only the request with no
question in it, and every filtered request falls through to a 404.

### The shape has not changed — yet

The response is still a bare array: `[…]`. That is on borrowed time. A filtered
list raises a question a bare array cannot answer — *how many are there
altogether?* — and module 18 changes the shape to answer it. It will be the
project's one breaking change.

### Retiring `/boom`

Module 16 needed something to throw, and `/boom` was built for the purpose, with
a stated expiry date. It is deleted here, and the contract says so with a
struck-through row. The boundary stays — it has nothing to catch today, which is
exactly how a boundary should spend its time.
""",
    """
```bash
$ curl -s 'localhost:3000/todos?q=MILK&done=false'
[{"id":1,"title":"Buy milk","done":false},{"id":3,"title":"Buy oat milk","done":false}]

$ curl -s 'localhost:3000/todos?q=oat+milk'
[{"id":3,"title":"Buy oat milk","done":false}]

$ curl -s -i localhost:3000/boom
HTTP/1.1 404 Not Found
```
""",
    pitfalls=[
        "Every filtered request is a 404 — the route compares `req.url`, which includes the query string. Route on `url.pathname`.",
        "Splitting `url.search` on `&` and `=` by hand. `searchParams` does it, decodes `%20` and `+`, and handles repeats.",
        "Trimming or refusing `?q=`. An empty search matches everything; that is a fine answer to a client that asked for nothing in particular.",
        "Leaving `/boom` in. It was scaffolding with an announced expiry; a route that throws on purpose has no place in a server you would run.",
        "Returning `{ items, total }` early. The envelope is module 18's, and it is a breaking change that deserves its own module.",
    ],
    warmup=[
        _pq("`GET /todos?q=milk`. What is `req.url`, and what is `url.pathname`?",
            ["`\"/todos?q=milk\"` and `\"/todos\"`",
             "Both `\"/todos\"`",
             "Both `\"/todos?q=milk\"`",
             "`\"/todos\"` and `\"/todos?q=milk\"`"],
            0,
            "`req.url` is everything after the host. The pathname is only the "
            "path — which is what a route is."),
    ],
    exercises=[
        _pex("todo-m17-search-1", "Case-blind",
             "Keep the todos whose title contains `q`, whatever the case of either.",
             _M17_FULL,
             "t.title.toLowerCase().includes(q)",
             [(_M17_S4_SCRIPT, _M17_S4_OUT)],
             ["`q` has already been lower-cased.",
              "Lower-case the title too, then ask whether `q` appears in it.",
              "`t.title.toLowerCase().includes(q)`"]),
        _pfix("todo-m17-search-fix1", "Any question is a 404",
              "`GET /todos` works. `GET /todos?q=milk` answers `404`, and so does "
              "every other request with a query string.",
              _m17(_M17_ROUTE_BY_URL),
              _M17_FULL,
              [(_M17_S4_SCRIPT, _M17_S4_OUT)],
              ["What does the list route compare?",
               "What is `req.url` for `/todos?q=milk`?",
               "`url.pathname === \"/todos\"`"],
              difficulty="Intro"),
        _pch("todo-m17-search-build", "Write listTodos", "Easy",
             "Write the body of `listTodos(query)`: start from every todo, keep only "
             "those whose `done` matches if `query.done` is set, then only those "
             "whose title contains `query.q` in any case if it is set.",
             _M17_FULL,
             _M17_LIST.split("{\n", 1)[1].rsplit("\n}", 1)[0],
             [(_M17_S4_SCRIPT, _M17_S4_OUT)],
             ["`let items = todos;`",
              "`if (query.done !== undefined) { items = items.filter((t) => t.done === query.done); }`",
              "Lower-case `query.q` once, into a `const`, before filtering on it.",
              "`return items;`"]),
    ],
    quiz=[
        _pq("`?done=false&q=milk` and `?q=milk&done=false` — do they answer the same?",
            ["Yes — both filters apply either way, and a todo must pass both",
             "No — the first parameter wins",
             "No — the second parameter wins",
             "Only if both are present"],
            0,
            "The order in the URL is not an instruction. `listTodos` decides the "
            "order it applies them in, and for filters it cannot matter."),
        _pq("Why keep the boundary now that `/boom` is gone?",
            ["It is for the bugs nobody has found yet — nothing throwing today is exactly how it should be",
             "Only for `/boom`",
             "It should be removed",
             "Because `parseJson` needs it"],
            0,
            "A boundary with nothing to catch is a boundary working."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M17_FINAL = _pch(
    "todo-m17-build", "Module 17 build — the list can be asked", "Medium",
    "Write `listQueryFrom` and `listTodos`.\n\n"
    "* `listQueryFrom(params)` — `done` must be absent, `true` or `false` "
    "(otherwise `done: must be true or false`); `q` is any text; answer the "
    "`ListQuery` or the list of errors\n"
    "* `listTodos(query)` — every todo, narrowed by `done` if set, then by a "
    "case-blind title search if `q` is set\n\n"
    "`ListQuery` is declared above `listQueryFrom`, and the list route already "
    "calls both. Unknown parameters are ignored.",
    _m17(listtodos="", query=_M17_QUERY.rstrip("\n") + "\n\n" + _M17_LIST),
    _M17_QUERY.split("};\n\n", 1)[1].rstrip("\n") + "\n\n" + _M17_LIST.rstrip("\n"),
    [("\n".join(_M17_SETUP + ["GET /todos?done=true", "GET /todos?done=false&q=MILK",
                              "GET /todos?q=oat+milk&colour=blue", "GET /todos?done=yes",
                              "GET /todos?done=true&q=milk", 'PATCH /todos/3 {"done":true}',
                              "GET /todos?done=true&q=milk", "DELETE /todos/2", "GET /todos?done=true",
                              "GET /todos"]),
      "\n".join(_M17_SETUP_OUT + [_arr(_TODO_B_DONE), _arr(_TODO_A, _TODO_OAT3), _arr(_TODO_OAT3), _v(_FE_DONE),
                                  "200 []", '200 {"id":3,"title":"Buy oat milk","done":true}',
                                  _arr('{"id":3,"title":"Buy oat milk","done":true}'), "204",
                                  _arr('{"id":3,"title":"Buy oat milk","done":true}'),
                                  _arr(_TODO_A, '{"id":3,"title":"Buy oat milk","done":true}')]))],
    ["`listQueryFrom`: `params.get(\"done\")` — `\"true\"`, `\"false\"`, `null`, or an error.",
     "`params.get(\"q\")` — any text but `null` becomes `query.q`.",
     "`listTodos`: `let items = todos;` then `items = items.filter(…)` for each filter that is set.",
     "Lower-case both the title and the search text.",
     "`?colour=blue` is ignored — only `done` values are refused."],
)


_TODO_MODULES.append(_pmod(
    key="todo-filter", number=17, phase="real",
    title="Filtering with query strings",
    what="searchParams, and a 400 when a filter's value is junk",
    goal="Let a client filter the list by `done` and search it by title through the query string, and refuse a filter value the API cannot understand.",
    why=_M17_WHY,
    est_minutes=50,
    builds_on=["todo-boundary"],
    concepts=["query string", "searchParams", "null vs absent vs empty", "truthy strings",
              "filter", "map", "case-insensitive search", "unknown parameters", "defaults"],
    deliverable="`GET /todos?done=false&q=milk` answers the unfinished todos that "
                "mention milk; `?done=banana` is a 400 naming `done`; and nothing "
                "else in the API changed.",
    objectives=[
        "Read a query-string parameter with `searchParams.get`, and handle absent, empty and present separately",
        "Explain why `\"false\"` is truthy, and compare parameter values with the exact text",
        "Narrow a list with `filter`, turn one into another with `map`, and say what each does to the original",
        "Compose optional filters, applying only those the client asked for",
        "Search case-insensitively with `toLowerCase` and `includes`",
        "Refuse a filter value the API cannot understand with a validation 400 — and argue why unknown parameters are ignored instead",
    ],
    endpoints=[
        _pep("GET", "/todos", "List todos — filtered by `done` and a title search",
             "?done=true&q=milk", "[Todo] — a bare array until module 18", "200 · 400"),
        _pep("GET", "/boom", "Retired — module 16's scaffolding; the boundary stays", "", "—", "—"),
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M17_BRIEF,
    syntax=_M17_SYNTAX,
    steps=[_M17_S1, _M17_S2, _M17_S3, _M17_S4],
    final_build=_M17_FINAL,
    acceptance=[
        "`curl -s 'localhost:3000/todos?done=true'` returns only finished todos; `?done=false` only unfinished ones.",
        "`curl -s localhost:3000/todos` still returns every todo — an absent filter filters nothing.",
        "`curl -s 'localhost:3000/todos?q=MILK'` finds *Buy milk* — the search ignores case.",
        "`curl -s 'localhost:3000/todos?q=milk&done=false'` applies both filters.",
        "`curl -s -i 'localhost:3000/todos?done=banana'` returns 400 naming `done`; so does `?done=`.",
        "`curl -s 'localhost:3000/todos?colour=red'` returns every todo — unknown parameters are ignored.",
        "`curl -s -i localhost:3000/boom` returns 404.",
        "No request to any other route behaves differently from module 16.",
    ],
    manual_test="""
Make a few todos and finish one:

```bash
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
curl -s -X POST localhost:3000/todos -d '{"title":"Write tests"}'
curl -s -X POST localhost:3000/todos -d '{"title":"Buy oat milk"}'
curl -s -X PATCH localhost:3000/todos/2 -d '{"done":true}'
```

Ask the list questions — and quote every URL, or the shell will eat the `&`:

```bash
curl -s 'localhost:3000/todos?done=true'
curl -s 'localhost:3000/todos?done=false'
curl -s 'localhost:3000/todos?q=MILK'
curl -s 'localhost:3000/todos?q=milk&done=false'
curl -s 'localhost:3000/todos?q=oat%20milk'
```

Then the ones that must be refused, and the one that must not:

```bash
curl -s -i 'localhost:3000/todos?done=banana'   # 400, naming done
curl -s -i 'localhost:3000/todos?done='         # 400 — empty is not absent
curl -s 'localhost:3000/todos?colour=red'       # every todo — unknown names are ignored
```

Last, forget the quotes once, on purpose, and read what the shell says:

```bash
curl -s localhost:3000/todos?q=milk&done=false
```
""",
    reference="""// server.ts — module 17
//
// The list can be asked a question: `?done=true|false` and `?q=<text>`, alone or
// together. The query string is input like any other — a value the API cannot
// understand is a validation 400 naming the parameter. An absent parameter means
// "don't filter"; an unknown one is ignored.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

// addTodo's `title: string` has been a promise since module 2. As of this
// module, every caller can actually keep it.
function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}

function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  return true;
}

// `filter` returns a NEW array and never touches the one it is called on, so the
// store is safe. `items` starts as every todo and follows each narrower list in
// turn; a filter nobody asked for is skipped. Both sides of the search are
// lower-cased, so `?q=MILK` finds "Buy milk".
function listTodos(query: ListQuery): Todo[] {
  let items = todos;
  if (query.done !== undefined) {
    items = items.filter((t) => t.done === query.done);
  }
  if (query.q !== undefined) {
    const q = query.q.toLowerCase();
    items = items.filter((t) => t.title.toLowerCase().includes(q));
  }
  return items;
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
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

function idText(pathname: string): string | undefined {
  const parts = pathname.split("/");
  if (parts.length !== 3 || parts[1] !== "todos") {
    return undefined;
  }
  return parts[2];
}

function parseId(text: string): number | undefined {
  const id = Number(text);
  if (!Number.isInteger(id) || id < 1) {
    return undefined;
  }
  return id;
}

function todoId(pathname: string): number | undefined {
  const text = idText(pathname);
  if (text === undefined) {
    return undefined;
  }
  return parseId(text);
}

// ---- the boundary ----------------------------------------------------------
// Everything below this line and above the handler exists because a client can
// send any JSON at all: a string, a number, a boolean, null, an array, or an
// object. Only the last is a body.

// typeof says "object" for null AND for arrays, so both are named explicitly.
// Without the null check, `"title" in null` would throw — a 500.
function objectFrom(data: unknown): object | undefined {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    return undefined;
  }
  return data;
}

// One thing wrong with one field. `field` is the name the client used, so a
// form can show `message` next to the right box.
type FieldError = {
  field: string;
  message: string;
};

// A validator answers with the value, or with what was wrong with it. Shape
// first (module 13), because the value rules can only be asked of a string.
// The emptiness check trims, so a title of spaces counts as empty; the title is
// stored as sent.
function titleFrom(value: unknown): string | FieldError {
  if (typeof value !== "string") {
    return { field: "title", message: "must be a string" };
  }
  if (value.trim() === "") {
    return { field: "title", message: "must not be empty" };
  }
  if (value.length > 100) {
    return { field: "title", message: "must be at most 100 characters" };
  }
  return value;
}

function doneFrom(value: unknown): boolean | FieldError {
  if (typeof value !== "boolean") {
    return { field: "done", message: "must be true or false" };
  }
  return value;
}

// Create can only find one problem — there is one field — but answers with a
// LIST anyway, so both write routes fail in one shape. A title is required
// here; on a patch nothing is.
function createFrom(data: unknown): string | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  if (!("title" in obj)) {
    return [{ field: "title", message: "is required" }];
  }
  const title = titleFrom(obj.title);
  if (typeof title !== "string") {
    return [title];
  }
  return title;
}

// Every field that is present is checked, whatever happened to the one before,
// so a client hears about every mistake in one response. Any error at all
// refuses the whole patch: applying the good half is a result nobody asked for.
function changesFrom(data: unknown): Partial<Todo> | FieldError[] {
  const obj = objectFrom(data);
  if (obj === undefined) {
    return [{ field: "body", message: "must be a JSON object" }];
  }
  const changes: Partial<Todo> = {};
  const errors: FieldError[] = [];
  if ("title" in obj) {
    const title = titleFrom(obj.title);
    if (typeof title === "string") {
      changes.title = title;
    } else {
      errors.push(title);
    }
  }
  if ("done" in obj) {
    const done = doneFrom(obj.done);
    if (typeof done === "boolean") {
      changes.done = done;
    } else {
      errors.push(done);
    }
  }
  if (errors.length > 0) {
    return errors;
  }
  return changes;
}

// What a client asked the list. `undefined` means "not asked" — no filter.
type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
};

// The query string is input, checked like a body and refused in the same shape.
// Three cases for `done`: absent (null) is no filter; "true"/"false" is a
// filter; anything else — "banana", "", "TRUE" — is a question we cannot
// answer, and guessing would hand the client a wrong list with a 200.
// Parameters we do not know (?colour=red) are ignored: they may come from a
// newer client.
function listQueryFrom(params: URLSearchParams): ListQuery | FieldError[] {
  const query: ListQuery = { done: undefined, q: undefined };
  const errors: FieldError[] = [];
  const done = params.get("done");
  if (done === "true") {
    query.done = true;
  } else if (done === "false") {
    query.done = false;
  } else if (done !== null) {
    errors.push({ field: "done", message: "must be true or false" });
  }
  const q = params.get("q");
  if (q !== null) {
    query.q = q;
  }
  if (errors.length > 0) {
    return errors;
  }
  return query;
}

// ---- errors ----------------------------------------------------------------
// Every failure the API can report, tagged by `kind`. A kind is a literal type,
// so a misspelt one is a compile error. Adding `invalid_json` here is what made
// errorReply's `never` line fail until it had a case — module 15's payoff.
type ApiError =
  | { kind: "not_found" }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }
  | { kind: "server_error" };

type ErrorReply = {
  status: number;
  body: object;
};

// The ONE place a failure becomes a status and a body — so they can never
// disagree. Pure: it decides and sends nothing, which is what makes it testable.
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "validation":
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  // Every case returns, so `err` is `never` here — nothing is left for it to be.
  // Add a kind to ApiError without a case above and THIS line stops compiling,
  // naming the kind. The return only satisfies the return type; it cannot run.
  const unhandled: never = err;
  return unhandled;
}

function sendError(res: ServerResponse, err: ApiError): void {
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}

// JSON.parse THROWS on text that is not JSON — the client's mistake, and an
// expected one. It is caught here, where we know exactly what failed, and turned
// back into an ordinary value the routes must check. This is the only JSON.parse
// in the file.
type Parsed =
  | { ok: true; data: unknown }
  | { ok: false };

function parseJson(text: string): Parsed {
  try {
    return { ok: true, data: JSON.parse(text) };
  } catch {
    return { ok: false };
  }
}

async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const id = todoId(url.pathname);

  // Routed on the PATHNAME — `req.url` includes the query string, which is why
  // every route since module 7 has compared `url.pathname`.
  if (req.method === "GET" && url.pathname === "/todos") {
    const query = listQueryFrom(url.searchParams);
    if (Array.isArray(query)) {
      sendError(res, { kind: "validation", fields: query });
      return;
    }
    send(res, 200, listTodos(query));
    return;
  }

  if (req.method === "POST" && url.pathname === "/todos") {
    const body = await readBody(req);
    const parsed = parseJson(body);
    if (!parsed.ok) {
      sendError(res, { kind: "invalid_json" });
      return;
    }
    // A list means refused; a string is the title. Array.isArray tells which.
    const checked = createFrom(parsed.data);
    if (Array.isArray(checked)) {
      sendError(res, { kind: "validation", fields: checked });
      return;
    }
    // Checked before anything touches the store — a refused body never uses an id.
    const todo = addTodo(checked);
    send(res, 201, todo);
    return;
  }

  if (req.method === "GET" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      sendError(res, { kind: "not_found" });
      return;
    }
    send(res, 200, todo);
    return;
  }

  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);                 // look up first: a bad body to a
    if (todo === undefined) {                  // missing todo is still a 404
      sendError(res, { kind: "not_found" });
      return;
    }
    const body = await readBody(req);
    const parsed = parseJson(body);
    if (!parsed.ok) {
      sendError(res, { kind: "invalid_json" });
      return;
    }
    const checked = changesFrom(parsed.data);
    if (Array.isArray(checked)) {
      sendError(res, { kind: "validation", fields: checked });
      return;
    }
    const updated = updateTodo(todo, checked);
    send(res, 200, updated);
    return;
  }

  if (req.method === "DELETE" && id !== undefined) {
    const removed = deleteTodo(id);
    if (!removed) {
      sendError(res, { kind: "not_found" });
      return;
    }
    sendEmpty(res, 204);
    return;
  }

  sendError(res, { kind: "not_found" });
}

// The error boundary: one `try` around every route, so an exception anywhere —
// in a route that exists today or one added next year — is a clean 500 instead
// of a dead process. The `await` is what keeps the `try` open until `route`'s
// promise settles; without it the rejection would escape. The details go to the
// log, never to the client. And if the route had already started answering, the
// status cannot be replaced — only the response ended.
async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
  try {
    await route(req, res);
  } catch (err: unknown) {
    console.error(err);
    if (res.headersSent) {
      res.end();
      return;
    }
    sendError(res, { kind: "server_error" });
  }
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Accept `?done=1` and `?done=0` as well. Then write down every spelling you now support, forever, and decide whether it was worth it.",
        "Support `?q=` against several words — `?q=buy+milk` matching titles containing *both*. Use `.split(\" \")` and ask each word in turn. What should `?q=+++` do?",
        "Repeat a parameter: `?done=true&done=false`. `get` takes the first; is that right, or is it a 400? Look up what `getAll` returns and decide.",
        "Filter on the server versus on the client: with 10,000 todos and a phone on 3G, measure (or estimate) the bytes each approach sends for `?done=false`.",
    ],
    glossary=[
        _pgloss("query string", "Everything after the `?` in a URL — `name=value` pairs joined by `&`. How a client asks a GET a question."),
        _pgloss("searchParams", "`url.searchParams` — the query string, split up and decoded. `get(name)` answers a string, or `null` if absent."),
        _pgloss("truthy", "A value that counts as true in an `if` — including the non-empty string `\"false\"`. Why parameters are compared with exact text."),
        _pgloss("filter", "`list.filter(fn)` — a new array of the elements for which `fn` returns true. The original is unchanged."),
        _pgloss("map", "`list.map(fn)` — a new array of whatever `fn` returns for each element. Same length in and out."),
        _pgloss("case-insensitive", "Comparing after lower-casing both sides, so `MILK` finds *Buy milk*."),
        _pgloss("default", "What an absent input means — for a filter, *don't filter*. Right for absent; wrong for present-and-unreadable."),
        _pgloss("forward compatibility", "An old server working with a newer client — why unknown parameters are ignored rather than refused."),
    ],
    cheatsheet="""
```ts
url.searchParams.get("done")   // "true" | "false" | "banana" | "" | null(absent)

// three cases, not two — and never `if (done)`: "false" is truthy
if (done === "true") {
  query.done = true;
} else if (done === "false") {
  query.done = false;
} else if (done !== null) {
  errors.push({ field: "done", message: "must be true or false" });
}

// compose the filters that were asked for
let items = todos;
if (query.done !== undefined) {
  items = items.filter((t) => t.done === query.done);      // assign it!
}
if (query.q !== undefined) {
  const q = query.q.toLowerCase();
  items = items.filter((t) => t.title.toLowerCase().includes(q));
}

list.map((t) => t.title)       // ["Buy milk", …] — which: filter · what: map
```

| Request | Answer |
|---|---|
| `/todos` | every todo |
| `/todos?done=true` · `?done=false` | done only · not done only |
| `/todos?q=MILK` | titles containing *milk*, any case |
| `/todos?q=milk&done=false` | both filters |
| `/todos?q=oat+milk` · `?q=oat%20milk` | the same search |
| `/todos?done=banana` · `?done=` | **400** `done: must be true or false` |
| `/todos?colour=red` | every todo — unknown names ignored |
""",
    self_check=[
        "Can you say what `searchParams.get` returns for an absent parameter, an empty one, and `?done=false`?",
        "Can you explain why `if (done)` treats `?done=false` as true?",
        "Can you say what `filter` and `map` each do, and what each does to the array they are called on?",
        "Can you explain why `items = items.filter(…)` needs the assignment?",
        "Can you argue why `?done=banana` is a 400 while `?colour=red` is ignored?",
        "Can you say why a route written as `req.url === \"/todos\"` breaks this module?",
    ],
    review=[
        _pq("`?done=false`. What goes wrong with `if (url.searchParams.get(\"done\")) { … done only … }`?",
            ["`\"false\"` is a non-empty string, so it is truthy — the client gets the finished todos",
             "Nothing",
             "It does not compile",
             "`get` returns `false`, so the branch is skipped correctly"],
            0,
            "A query string is text. The comparison has to be with the text."),
        _pq("Which of these should be a 400?",
            ["`?done=banana`",
             "`/todos` with no parameters",
             "`?colour=red`",
             "`?q=`"],
            0,
            "Only a value the API cannot understand is refused. Absent, unknown and "
            "empty-search are all answerable."),
        _pq("`items.filter((t) => t.done);` on a line of its own — what does it do?",
            ["Builds a filtered array and throws it away; `items` is unchanged",
             "Removes the unfinished todos from `items`",
             "Removes them from the store",
             "It does not compile"],
            0,
            "`filter` returns its result. The assignment is the whole point."),
        _pq("Why does this module add a route change and nothing else to the router?",
            ["Every route has matched `url.pathname` since module 7, so a query string never broke one",
             "Because query strings are only for GET",
             "It rewrites the router",
             "Because the boundary handles query strings"],
            0,
            "A decision made ten modules ago, paying for itself."),
        _pq("The plan said to *default* `?done=banana`. Why was that reversed?",
            ["A default answers a misread question with a 200 and the wrong list — the quiet wrong answer modules 13-16 removed",
             "Defaults are slower",
             "TypeScript does not allow defaults",
             "It was not reversed"],
            0,
            "The default survived where it belongs: an absent parameter."),
        _pq("What does `todos.map((t) => t.title)` return for three todos?",
            ["An array of three titles",
             "The todos whose title is truthy",
             "One string of all the titles",
             "The first title"],
            0,
            "One output per input. `map` never changes how many."),
    ],
    milestone="The list can be asked a question. `?done=` and `?q=` narrow it, "
              "alone or together; a question the API cannot read is a 400 that "
              "says so; and module 7's decision to route on the pathname paid for "
              "itself without a line of the router changing.",
))
