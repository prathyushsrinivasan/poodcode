# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 20 — A router, layers and a test you wrote.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-19's program pieces.
#
# CLOSES THE PROJECT. Three things, in the order the roadmap gave them:
#
#   * LAYERS. The file is reorganised into four sections — rules, store,
#     service, http — where each calls only the ones before it. The new layer is
#     the SERVICE: `createTodo(body)`, `patchTodo(id, body)` and friends, which
#     take plain values and answer a value or an `ApiError`, and know nothing
#     about requests or responses. The proof that the layering is real is
#     mechanical: steps 1, 3 and 4 run the whole application below the http
#     layer as a PLAIN program — no `node:http` import at all — and it compiles.
#     If any service function mentioned `ServerResponse`, it would not.
#
#   * A ROUTER. Two tables — `Record<string, CollectionRoute>` and
#     `Record<string, ItemRoute>` — keyed by method. `noUncheckedIndexedAccess`
#     makes a lookup `Route | undefined`, and the `undefined` branch is exactly
#     405 Method Not Allowed, with the table's own keys as the `allow` list and
#     the `Allow` header. Module 7 declined to do 405 because "doing it properly
#     needs the set of verbs a path allows, which is a routing table, which is
#     module 20". This is that module. `DELETE /todos` changes from 404 to 405,
#     declared in the contract.
#
#   * A TEST RUNNER BY HAND — `test`, `expectEqual`, `runTests`, ~30 lines —
#     which is the argument for what a framework does: a list of named functions,
#     a `try`/`catch` around each, an assertion that is just a `throw`, a fresh
#     store per test, and a count. Its graded bugs are the two ways a home-made
#     runner lies: tests that share state (isolation), and an assertion that does
#     not throw — caught by the suite's test of `expectEqual` itself. Step 4 then
#     uses the suite as the grader for an application bug.
#
# `.map(` IS USED FOR REAL here, in tests — comparing one field of many todos —
# which is the use module 17 promised.
#
# THE SMOKE TEST over HTTP is in the manual test: a zero-dependency `smoke.ts`
# that fetches the running server. The judged programs cannot boot a second
# process, and the replayer is already exactly that — a smoke test without the
# expectations — which the module says.
# ---------------------------------------------------------------------------

_M20_APIERROR = """type ApiError =
  | { kind: "not_found" }
  | { kind: "method_not_allowed"; allow: string[] }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }
  | { kind: "server_error" };
"""

_M20_REPLY = _M16_REPLY.replace("""    case "validation":""", """    case "method_not_allowed":
      return { status: 405, body: { error: "method_not_allowed", allow: err.allow } };
    case "validation":""", 1)
assert _M20_REPLY != _M16_REPLY

_M20_SERVICE = """function listPage(params: URLSearchParams): Page | ApiError {
  const query = listQueryFrom(params);
  if (Array.isArray(query)) {
    return { kind: "validation", fields: query };
  }
  return listTodos(query);
}

function createTodo(body: string): Todo | ApiError {
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const checked = createFrom(parsed.data);
  if (Array.isArray(checked)) {
    return { kind: "validation", fields: checked };
  }
  return addTodo(checked);
}

function getTodo(id: number): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  return todo;
}

function patchTodo(id: number, body: string): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const checked = changesFrom(parsed.data);
  if (Array.isArray(checked)) {
    return { kind: "validation", fields: checked };
  }
  return updateTodo(todo, checked);
}

function removeTodo(id: number): ApiError | undefined {
  if (!deleteTodo(id)) {
    return { kind: "not_found" };
  }
  return undefined;
}
"""

_M20_PATCHTODO = "function patchTodo" + _M20_SERVICE.split("function patchTodo", 1)[1].split("\n}\n", 1)[0] + "\n}"

_M20_SENDERROR = """function sendError(res: ServerResponse, err: ApiError): void {
  if (err.kind === "method_not_allowed") {
    res.setHeader("Allow", err.allow.join(", "));
  }
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}

function sendResult(res: ServerResponse, status: number, result: Todo | Page | ApiError): void {
  if ("kind" in result) {
    sendError(res, result);
    return;
  }
  send(res, status, result);
}
"""

_M20_TABLES = """type CollectionRoute = (req: IncomingMessage, res: ServerResponse, url: URL) => Promise<void>;
type ItemRoute = (req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>;

const collectionRoutes: Record<string, CollectionRoute> = {
  GET: async (req, res, url) => {
    sendResult(res, 200, listPage(url.searchParams));
  },
  POST: async (req, res) => {
    sendResult(res, 201, createTodo(await readBody(req)));
  },
};

const itemRoutes: Record<string, ItemRoute> = {
  GET: async (req, res, id) => {
    sendResult(res, 200, getTodo(id));
  },
  PATCH: async (req, res, id) => {
    sendResult(res, 200, patchTodo(id, await readBody(req)));
  },
  DELETE: async (req, res, id) => {
    const err = removeTodo(id);
    if (err !== undefined) {
      sendError(res, err);
      return;
    }
    sendEmpty(res, 204);
  },
};
"""

_M20_ITEM_BRANCH = """  const id = todoId(url.pathname);
  if (id !== undefined) {
    const run = itemRoutes[method];
    if (run === undefined) {
      sendError(res, { kind: "method_not_allowed", allow: Object.keys(itemRoutes) });
      return;
    }
    await run(req, res, id);
    return;
  }"""

_M20_ROUTE = """async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const method = req.method ?? "GET";
  if (url.pathname === "/todos") {
    const run = collectionRoutes[method];
    if (run === undefined) {
      sendError(res, { kind: "method_not_allowed", allow: Object.keys(collectionRoutes) });
      return;
    }
    await run(req, res, url);
    return;
  }
""" + _M20_ITEM_BRANCH + """
  sendError(res, { kind: "not_found" });
}
"""

_M20_RULES = (_M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE, _M14_CREATE, _M14_CHANGES,
              _M18_QUERY, _M16_PARSE, _M20_APIERROR, _M20_REPLY)


def _m20_store(sort=_M18_SORT):
    return (_M19_STORE, _M19_UPDATE, _M19_DELETE, sort, _M18_LIST, _M19_LOAD)


def _m20(service=_M20_SERVICE, tables=_M20_TABLES, route=_M20_ROUTE, sort=_M18_SORT):
    """A module-20 server program: rules, store, service, http — each section
    calling only the ones above it."""
    http = (_M10_SEND, _M12_SENDEMPTY, _M10_READBODY, _M20_SENDERROR,
            _M10_IDTEXT, _M10_PARSEID, _M10_TODOID, tables, route, _M16_BOUNDARY)
    parts = _M20_RULES + _m20_store(sort) + (service,) + http
    return _server_disk("\n\n".join(p.rstrip("\n") for p in parts if p))


def _m20_plain(body, service=_M20_SERVICE, sort=_M18_SORT):
    """Everything below the http layer, as a PLAIN program — no `node:http`.
    That it compiles at all is the proof the layers are real."""
    parts = _M20_RULES + _m20_store(sort) + (service,)
    return ('import { readFileSync, writeFileSync, existsSync } from "node:fs";\n\n'
            + "\n\n".join(p.rstrip("\n") for p in parts) + "\n\n" + _pbp(body))


_M20_FULL = _m20()

# --- Step 1's plain program: the service, called directly -------------------
_M20_S1_BODY = """
function show(result: Todo | Page | ApiError | undefined): void {
  console.log(JSON.stringify(result));
}

show(createTodo('{"title":"Buy milk"}'));
show(createTodo('{"title":""}'));
show(createTodo("not json"));
show(patchTodo(1, '{"done":true}'));
show(patchTodo(9, "not json"));
show(getTodo(2));
show(listPage(new URLSearchParams("done=true")));
show(listPage(new URLSearchParams("limit=0")));
show(removeTodo(1));
show(removeTodo(1));
"""

_M20_S1_OUT = "\n".join([
    _TODO_A,
    '{"kind":"validation","fields":[' + _FE_EMPTY + "]}",
    '{"kind":"invalid_json"}',
    _TODO_A_DONE,
    '{"kind":"not_found"}',
    '{"kind":"not_found"}',
    '{"items":[' + _TODO_A_DONE + '],"total":1}',
    '{"kind":"validation","fields":[' + _FE_LIMIT + "]}",
    "undefined",
    '{"kind":"not_found"}',
])

_M20_PATCH_PARSE_FIRST = _M20_SERVICE.replace("""function patchTodo(id: number, body: string): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }""", """function patchTodo(id: number, body: string): Todo | ApiError {
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }""")
assert _M20_PATCH_PARSE_FIRST != _M20_SERVICE

# --- Steps 3-4's plain program: the runner and the suite --------------------
_M20_EXPECT = """function expectEqual(actual: unknown, expected: unknown): void {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) {
    throw new Error("expected " + e + ", got " + a);
  }
}
"""

_M20_RUNTESTS = """function runTests(): void {
  let failed = 0;
  for (const t of tests) {
    resetStore();
    try {
      t.run();
      console.log("ok - " + t.name);
    } catch (err: unknown) {
      failed = failed + 1;
      if (err instanceof Error) {
        console.log("not ok - " + t.name + ": " + err.message);
      } else {
        console.log("not ok - " + t.name);
      }
    }
  }
  console.log(tests.length - failed + " passed, " + failed + " failed");
}
"""

_M20_RUNNER_HEAD = """type Test = {
  name: string;
  run: () => void;
};

const tests: Test[] = [];

function test(name: string, run: () => void): void {
  tests.push({ name: name, run: run });
}
"""

_M20_RESET = """function resetStore(): void {
  todos.splice(0, todos.length);
  nextId = 1;
}
"""

_M20_SUITE = """test("a new todo gets the next id, not done", () => {
  expectEqual(createTodo('{"title":"Buy milk"}'), { id: 1, title: "Buy milk", done: false });
});

test("ids are never reused after a delete", () => {
  createTodo('{"title":"Buy milk"}');
  createTodo('{"title":"Write tests"}');
  removeTodo(2);
  expectEqual(createTodo('{"title":"Ship it"}'), { id: 3, title: "Ship it", done: false });
});

test("a blank title is refused, naming the field", () => {
  expectEqual(createTodo('{"title":"  "}'), {
    kind: "validation",
    fields: [{ field: "title", message: "must not be empty" }],
  });
});

test("text that is not JSON is invalid_json", () => {
  expectEqual(createTodo("not json"), { kind: "invalid_json" });
});

test("a missing todo is not_found, whatever its body", () => {
  expectEqual(patchTodo(9, "not json"), { kind: "not_found" });
});

test("a patch with two mistakes names both and changes nothing", () => {
  createTodo('{"title":"Buy milk"}');
  expectEqual(patchTodo(1, '{"title":"","done":"yes"}'), {
    kind: "validation",
    fields: [
      { field: "title", message: "must not be empty" },
      { field: "done", message: "must be true or false" },
    ],
  });
  expectEqual(getTodo(1), { id: 1, title: "Buy milk", done: false });
});

test("the list filters, sorts and pages, with a total", () => {
  createTodo('{"title":"Buy milk"}');
  createTodo('{"title":"Write tests"}');
  createTodo('{"title":"Ship it"}');
  patchTodo(2, '{"done":true}');
  const page = listPage(new URLSearchParams("done=false&sort=newest&limit=1"));
  if ("kind" in page) {
    throw new Error("expected a page, got " + page.kind);
  }
  expectEqual(page.items.map((t) => t.title), ["Ship it"]);
  expectEqual(page.total, 2);
});

test("sorting never reorders the store", () => {
  createTodo('{"title":"Write tests"}');
  createTodo('{"title":"Buy milk"}');
  listPage(new URLSearchParams("sort=title"));
  const page = listPage(new URLSearchParams(""));
  if ("kind" in page) {
    throw new Error("expected a page, got " + page.kind);
  }
  expectEqual(page.items.map((t) => t.id), [1, 2]);
});

test("every kind of error has its status", () => {
  expectEqual(errorReply({ kind: "not_found" }).status, 404);
  expectEqual(errorReply({ kind: "method_not_allowed", allow: ["GET"] }).status, 405);
  expectEqual(errorReply({ kind: "validation", fields: [] }).status, 400);
  expectEqual(errorReply({ kind: "invalid_json" }).status, 400);
  expectEqual(errorReply({ kind: "server_error" }).status, 500);
});

test("expectEqual fails on a mismatch", () => {
  let threw = false;
  try {
    expectEqual(1, 2);
  } catch {
    threw = true;
  }
  if (!threw) {
    throw new Error("expectEqual let 1 equal 2");
  }
});

runTests();
"""

_M20_TEST_NAMES = [
    "a new todo gets the next id, not done",
    "ids are never reused after a delete",
    "a blank title is refused, naming the field",
    "text that is not JSON is invalid_json",
    "a missing todo is not_found, whatever its body",
    "a patch with two mistakes names both and changes nothing",
    "the list filters, sorts and pages, with a total",
    "sorting never reorders the store",
    "every kind of error has its status",
    "expectEqual fails on a mismatch",
]
_M20_TESTS_OUT = "\n".join(["ok - " + n for n in _M20_TEST_NAMES] + ["10 passed, 0 failed"])


def _m20_tests(expect=_M20_EXPECT, runtests=_M20_RUNTESTS, suite=_M20_SUITE, sort=_M18_SORT):
    body = "\n\n".join(p.rstrip("\n") for p in (_M20_RUNNER_HEAD, expect, _M20_RESET, runtests, suite))
    return _m20_plain(body, sort=sort)


_M20_TESTS_FULL = _m20_tests()


def _m405(*allow):
    return '405 {"error":"method_not_allowed","allow":[' + ",".join('"%s"' % a for a in allow) + "]}"


_M405_COLL = _m405("GET", "POST")
_M405_ITEM = _m405("GET", "PATCH", "DELETE")

_M20_WHY = (
    "Nineteen modules in, `server.ts` is some five hundred lines, and the only "
    "way to check any of it is to start the server and throw curl at it. The "
    "rules about what a todo may be are tangled with the code that reads "
    "requests, so testing the one means driving the other. The router is a "
    "column of `if`s that answers `DELETE /todos` with 404 — \"no such "
    "address\" — for an address that plainly exists. And nothing would tell you "
    "if the next change broke module 12's promise that ids are never reused. "
    "The API works. It is not yet in a shape you could hand to someone, or add "
    "a feature to without fear."
)

_M20_BRIEF = """
### The whole module in one line

Give the code layers that each do one job, a router that knows which verbs a
path allows, and a test suite — written by hand — that proves the rules hold.

### Four layers

```
http      requests and responses: readBody, sendError, the route tables, route, handler
  ↓
service   what the API does: createTodo(body), patchTodo(id, body), … → a value, or an ApiError
  ↓
store     the data, in memory and on disk: addTodo, listTodos, saveStore, loadStore
  ↓
rules     what input may say: titleFrom, changesFrom, listQueryFrom, parseJson, errorReply
```

Each layer calls only the ones below it. The new one is the **service**: the
whole application, with no idea that HTTP exists. It takes strings and numbers,
and it answers with a todo, a page, or an `ApiError` — values, which a test can
compare.

### A router that knows its verbs

```ts
const itemRoutes: Record<string, ItemRoute> = {
  GET:    async (req, res, id) => { … },
  PATCH:  async (req, res, id) => { … },
  DELETE: async (req, res, id) => { … },
};
```

Look the method up; if it is not there, the path exists and the verb does not —
**405**, with the table's own keys as the list of what *is* allowed. Module 7
put this off until there was a routing table. Here it is.

### A test runner in thirty lines

```ts
test("ids are never reused after a delete", () => {
  createTodo('{"title":"Buy milk"}');
  createTodo('{"title":"Write tests"}');
  removeTodo(2);
  expectEqual(createTodo('{"title":"Ship it"}'), { id: 3, title: "Ship it", done: false });
});
```

No framework, no install. Writing the runner is how you find out what a test
framework actually is: a list, a `try`/`catch`, a `throw`, and a count.
"""

_M20_SYNTAX = [
    _syn(
        "function createTodo(body: string): Todo | ApiError { … }",
        "A **service** function: plain values in, a value or an `ApiError` out. "
        "No `req`, no `res` — the application with the HTTP taken away.",
        """
createTodo('{"title":"Buy milk"}');   // { id: 1, title: "Buy milk", done: false }
createTodo("not json");               // { kind: "invalid_json" }
""",
        "Because it answers in values, a test can call it and compare the answer. "
        "Nothing has to be started.",
    ),
    _syn(
        '"kind" in result',
        "Module 13's `in`, telling a union's halves apart: only an `ApiError` has "
        "a `kind`, so this narrows `Todo | Page | ApiError` to the error.",
        """
if ("kind" in result) {
  sendError(res, result);       // ApiError
  return;
}
send(res, status, result);      // Todo | Page
""",
    ),
    _syn(
        "type ItemRoute = (req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>;",
        "A **function type**: the shape of a function — its parameters and what "
        "it returns — given a name, like any other type.",
        """
type Check = () => void;
const c: Check = () => { console.log("ran"); };
""",
        "Arrow functions assigned to it get their parameter types from it, so "
        "`async (req, res, id) => { … }` needs no annotations.",
    ),
    _syn(
        "const itemRoutes: Record<string, ItemRoute> = { GET: …, PATCH: …, DELETE: … };",
        "`Record<string, T>` is an object used as a lookup table: any string key, "
        "every value a `T`. Here, a method name to the function that answers it.",
        """
const run = itemRoutes[method];   // ItemRoute | undefined — the flag at work
""",
        "Under `noUncheckedIndexedAccess` a lookup may miss, so it is typed "
        "`| undefined` — and that `undefined` is exactly the 405.",
    ),
    _syn(
        "Object.keys(itemRoutes)",
        "The object's own keys, as an array of strings — here, every method the "
        "path allows.",
        """
Object.keys({ GET: 1, POST: 2 });   // ["GET", "POST"]
""",
        "The 405's `allow` list comes from the table itself, so it cannot "
        "disagree with what the router actually does.",
    ),
    _syn(
        'res.setHeader("Allow", err.allow.join(", "));',
        "`join` glues an array of strings into one, with a separator between. "
        "`setHeader` sets a header before `writeHead` sends the rest.",
        """
["GET", "POST"].join(", ");    // "GET, POST"
""",
        "HTTP requires an `Allow` header on a 405. The replayer does not print "
        "headers, so `curl -i` is how you see it.",
    ),
    _syn(
        'throw new Error("expected " + e + ", got " + a);',
        "An assertion is just a `throw`. The runner's `catch` turns it into "
        "`not ok`.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — layers, and the service.
# ---------------------------------------------------------------------------

_M20_S1 = _pstep(
    "layers", "Layers: the application without HTTP",
    "Four sections that each call only the ones below, and a service that answers in values.",
    """
Read your module-19 PATCH route and count its jobs:

1. find the todo (store)
2. read the body (HTTP)
3. parse it (rules)
4. check the changes (rules)
5. apply them (store)
6. choose a status and send it (HTTP)

Six jobs from three different worlds, interleaved. To test job 4 you have to
fake jobs 2 and 6. That is the problem layers solve.

### Four sections, one direction

```
http      readBody · sendError · sendResult · the route tables · route · handler
service   listPage · createTodo · getTodo · patchTodo · removeTodo
store     addTodo · findTodo · updateTodo · deleteTodo · listTodos · saveStore · loadStore
rules     objectFrom · titleFrom · createFrom · changesFrom · listQueryFrom · parseJson · errorReply
```

**Each layer calls only the ones below it.** The rules call nothing. The store
uses the rules to check what it loads. The service uses both. HTTP uses the
service. Nothing ever calls *up*. (Types — `Todo`, `ApiError` — are shared
vocabulary, and any layer may name them.)

### The new layer

```ts
function patchTodo(id: number, body: string): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const checked = changesFrom(parsed.data);
  if (Array.isArray(checked)) {
    return { kind: "validation", fields: checked };
  }
  return updateTodo(todo, checked);
}
```

That is the PATCH route — every rule it enforces, in the order it enforces them
— with the HTTP taken out. It takes the body as a *string*, so the one HTTP job
it needed (reading the stream) happens outside it. And it answers with a **value**:
a todo, or module 15's `ApiError`. Not a status code, not a response; what
happened. Deciding what that looks like on the wire is the next layer's job.

Still lookup first: `patchTodo(9, "not json")` is `not_found`, exactly as
`PATCH /todos/9 not json` has been a 404 since module 13.

### The proof

This step's program is the rules, the store and the service — **with no
`node:http` import at all**. It compiles. That is not a style claim about the
code; it is the compiler confirming that nothing below the http layer knows
HTTP exists. Mention `ServerResponse` in a service function and it would stop
compiling.
""",
    """
Called directly, the service answers in values:

```
createTodo('{"title":"Buy milk"}')     {"id":1,"title":"Buy milk","done":false}
createTodo('{"title":""}')             {"kind":"validation","fields":[…]}
createTodo("not json")                 {"kind":"invalid_json"}
patchTodo(1, '{"done":true}')          {"id":1,…,"done":true}
patchTodo(9, "not json")               {"kind":"not_found"}
getTodo(2)                             {"kind":"not_found"}
listPage(done=true)                    {"items":[…],"total":1}
listPage(limit=0)                      {"kind":"validation","fields":[…]}
removeTodo(1)                          undefined
removeTodo(1)                          {"kind":"not_found"}
```

No server, no replayer, no requests — and every rule of the API checked.
""",
    pitfalls=[
        "`patchTodo(9, \"not json\")` answers `invalid_json` — the service parses before it looks up. A missing todo is a 404 whatever its body; lookup first, as since module 13.",
        "A service function that takes `res` and sends. Then it cannot be called without a server, and the layer is HTTP again with a different name.",
        "A service function that returns a status code. `404` is HTTP's word; the service's word is `{ kind: \"not_found\" }`, and `errorReply` translates.",
        "Calling *up* — the store calling a service function, or the rules calling the store. Every such call is a loop in the design, and loops are what make code impossible to test in pieces.",
        "Splitting into layers and then putting the same check in two of them \"to be safe\". Each rule lives in one place; the layers above call it.",
    ],
    warmup=[
        _pq("Why does `patchTodo` take the body as a `string` rather than taking `req`?",
            ["Reading a request stream is HTTP's job; with a string, the service can be called with no request at all",
             "Strings are faster",
             "Because `req` cannot be passed to functions",
             "Because JSON is a string"],
            0,
            "The boundary between layers is drawn exactly where the types stop "
            "mentioning HTTP."),
    ],
    exercises=[
        _pex("todo-m20-layers-1", "The create, with no HTTP in it",
             "The title has passed every check. Store it, and answer with the todo "
             "the store made.",
             _m20_plain(_M20_S1_BODY),
             "return addTodo(checked);",
             [("", _M20_S1_OUT)],
             ["The store has a function that makes a todo from a title.",
              "It returns the todo — which is the service's answer.",
              "`return addTodo(checked);`"]),
        _pfix("todo-m20-layers-fix1", "Wrong about the body of a todo that is not there",
              "`patchTodo(9, \"not json\")` answers `{\"kind\":\"invalid_json\"}`. "
              "There is no todo 9 — so there is nothing for the body to be wrong "
              "about.",
              _m20_plain(_M20_S1_BODY, service=_M20_PATCH_PARSE_FIRST),
              _m20_plain(_M20_S1_BODY),
              [("", _M20_S1_OUT)],
              ["Which question does `patchTodo` ask first?",
               "Since module 13: look up, *then* read.",
               "Move `findTodo` and its `not_found` above `parseJson`."],
              difficulty="Easy"),
        _pch("todo-m20-layers-build", "Write patchTodo", "Medium",
             "Write `patchTodo(id, body)`:\n\n"
             "* no todo with that id → `{ kind: \"not_found\" }` — before anything else\n"
             "* not JSON → `{ kind: \"invalid_json\" }`\n"
             "* `changesFrom` refuses → `{ kind: \"validation\", fields }`\n"
             "* otherwise the updated todo",
             _m20_plain(_M20_S1_BODY),
             _M20_PATCHTODO,
             [("", _M20_S1_OUT)],
             ["`const todo = findTodo(id); if (todo === undefined) { return { kind: \"not_found\" }; }`",
              "`const parsed = parseJson(body);` — `!parsed.ok` is `invalid_json`.",
              "`changesFrom(parsed.data)` — a list is `{ kind: \"validation\", fields: checked }`.",
              "`return updateTodo(todo, checked);`"]),
    ],
    quiz=[
        _pq("What does it prove that this step's program compiles with no `node:http` import?",
            ["That nothing in the rules, store or service refers to HTTP — the layering is real, checked by the compiler",
             "That the server will start",
             "Nothing; imports are optional",
             "That the service is fast"],
            0,
            "An architecture claim the compiler verifies is worth ten in a README."),
        _pq("Why does the service answer `{ kind: \"not_found\" }` rather than `404`?",
            ["A status code is HTTP's vocabulary; the service says what happened, and the http layer translates",
             "404 is not a number in TypeScript",
             "For speed",
             "There is no difference"],
            0,
            "The same service could sit behind a command-line tool, where 404 "
            "means nothing and *not found* still does."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — the route tables.
# ---------------------------------------------------------------------------

_M20_S2_SCRIPT = "\n".join([_POST_A, "DELETE /todos", 'PUT /todos/1 {"title":"x"}', "POST /todos/1 {}",
                            "GET /todos/abc", "GET /nothing", "PATCH /todos/9 nope", "GET /todos",
                            'PATCH /todos/1 {"done":true}', "DELETE /todos/1", "DELETE /todos/1"])
_M20_S2_OUT = "\n".join(["201 " + _TODO_A, _M405_COLL, _M405_ITEM, _M405_ITEM, _NF, _NF, _NF,
                         _page(1, _TODO_A), "200 " + _TODO_A_DONE, "204", _NF, _file(2)])

_M20_ROUTE_404 = _M20_ROUTE.replace(
    '      sendError(res, { kind: "method_not_allowed", allow: Object.keys(itemRoutes) });',
    '      sendError(res, { kind: "not_found" });')
assert _M20_ROUTE_404 != _M20_ROUTE

_M20_S2 = _pstep(
    "router", "A router that knows its verbs",
    "Route tables keyed by method, a lookup that may miss, and 405 at last.",
    """
Every route since module 7 has been an `if`: *this verb and this path*. Read the
column of them and try to answer a simple question: **which verbs does
`/todos/1` accept?** You have to read every `if`. So does the code — which is why
`DELETE /todos` has always been a 404, *no such address*, when the address is
fine and only the verb is wrong.

### Two tables

The API has two kinds of path — the collection and one item — so two tables,
each mapping a method to the function that answers it:

```ts
type CollectionRoute = (req: IncomingMessage, res: ServerResponse, url: URL) => Promise<void>;
type ItemRoute = (req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>;

const itemRoutes: Record<string, ItemRoute> = {
  GET: async (req, res, id) => {
    sendResult(res, 200, getTodo(id));
  },
  PATCH: async (req, res, id) => {
    sendResult(res, 200, patchTodo(id, await readBody(req)));
  },
  DELETE: async (req, res, id) => { … },
};
```

Each route is now one call into the service and one call to send what it
answered. `sendResult` is where the service's values meet HTTP:

```ts
function sendResult(res: ServerResponse, status: number, result: Todo | Page | ApiError): void {
  if ("kind" in result) {
    sendError(res, result);
    return;
  }
  send(res, status, result);
}
```

### The lookup, and what a miss means

```ts
if (url.pathname === "/todos") {
  const run = collectionRoutes[method];
  if (run === undefined) {
    sendError(res, { kind: "method_not_allowed", allow: Object.keys(collectionRoutes) });
    return;
  }
  await run(req, res, url);
  return;
}
```

`collectionRoutes[method]` has type `CollectionRoute | undefined` — the
`noUncheckedIndexedAccess` flag this track has compiled under since module 1,
paying off one last time. The compiler will not let you call `run` until you
have said what a miss means, and a miss means precisely: *the path exists, the
verb does not.* That is **405 Method Not Allowed**, and HTTP requires it to say
what *is* allowed — which is just the table's keys.

`ApiError` gains a fifth kind, and module 15's `never` line walks you to
`errorReply` to give it a case:

```ts
| { kind: "method_not_allowed"; allow: string[] }
```

```
DELETE /todos     405 {"error":"method_not_allowed","allow":["GET","POST"]}
PUT /todos/1      405 {"error":"method_not_allowed","allow":["GET","PATCH","DELETE"]}
GET /todos/abc    404 — not an item path at all
```

Module 7 asked whether `POST /todos` (back then) should be a 405, and answered:
"doing 405 properly needs the set of verbs a path allows, which is a routing
table, which is module 20." This is that table.
""",
    """
```bash
$ curl -s -i -X DELETE localhost:3000/todos
HTTP/1.1 405 Method Not Allowed
Allow: GET, POST
{"error":"method_not_allowed","allow":["GET","POST"]}

$ curl -s -i -X PUT localhost:3000/todos/1 -d '{}'
HTTP/1.1 405 Method Not Allowed
Allow: GET, PATCH, DELETE
```

The `Allow` header only shows with `-i`; the replayer prints the body, where the
same list is.
""",
    pitfalls=[
        "`PUT /todos/1` answers 404 — the item router treats a missing method as a missing path. The path is fine; only the verb is wrong. 405.",
        "Writing the `allow` list by hand — `[\"GET\", \"POST\"]`. The first route someone adds makes it a lie. `Object.keys` of the table cannot disagree with the table.",
        "Calling `run` without checking it. It does not compile — `Cannot invoke an object which is possibly 'undefined'` — which is the flag doing its job.",
        "Answering 405 for `/todos/abc`. That is not an item path at all; there is nothing at the address, whatever the verb. 404.",
        "Forgetting the `Allow` header. HTTP requires it on a 405; clients and tools use it to decide what to try next.",
    ],
    warmup=[
        _pq("`DELETE /todos`. Which status is honest?",
            ["405 — the address exists; that verb is not supported on it",
             "404 — there is nothing to delete",
             "400 — the request was malformed",
             "204 — nothing was deleted, successfully"],
            0,
            "404 says *wrong address*. The address is right."),
    ],
    exercises=[
        _pex("todo-m20-router-1", "What is allowed here",
             "The collection has no route for this method. Answer 405, listing "
             "every method it does have — taken from the table itself.",
             _M20_FULL,
             "Object.keys(collectionRoutes)",
             [(_M20_S2_SCRIPT, _M20_S2_OUT)],
             ["The table's keys *are* the allowed methods.",
              "There is a function that returns an object's keys as an array.",
              "`Object.keys(collectionRoutes)`"]),
        _pfix("todo-m20-router-fix1", "A verb answered as an address",
              "`PUT /todos/1` and `POST /todos/1` answer `404 {\"error\":\"not_found\"}` "
              "— as though there were no todo 1. There is; it just does not take "
              "those verbs.",
              _m20(route=_M20_ROUTE_404),
              _M20_FULL,
              [(_M20_S2_SCRIPT, _M20_S2_OUT)],
              ["What does a miss in `itemRoutes` mean — the path, or the verb?",
               "The collection branch gets this right. Compare them.",
               "`sendError(res, { kind: \"method_not_allowed\", allow: Object.keys(itemRoutes) });`"],
              difficulty="Intro"),
        _pch("todo-m20-router-build", "Route to an item", "Medium",
             "Write the item branch of `route`: if the path names a todo, look the "
             "method up in `itemRoutes`; answer 405 with the allowed methods if it "
             "is not there, otherwise run it with the id.",
             _M20_FULL,
             _M20_ITEM_BRANCH,
             [(_M20_S2_SCRIPT, _M20_S2_OUT)],
             ["`const id = todoId(url.pathname); if (id !== undefined) { … }`",
              "`const run = itemRoutes[method];` — its type includes `undefined`.",
              "`if (run === undefined) { sendError(res, { kind: \"method_not_allowed\", allow: Object.keys(itemRoutes) }); return; }`",
              "`await run(req, res, id); return;`"]),
    ],
    quiz=[
        _pq("Why is the 405's `allow` list `Object.keys(itemRoutes)` rather than written out?",
            ["It comes from the same table the router uses, so it can never disagree with what the router does",
             "It is shorter",
             "HTTP requires `Object.keys`",
             "For speed"],
            0,
            "One source of truth, again — module 15's idea applied to routes."),
        _pq("`itemRoutes[method]` is typed `ItemRoute | undefined`. Why?",
            ["`noUncheckedIndexedAccess`: any key might be missing, and the compiler makes you say what a miss means",
             "Because `Record` is optional",
             "Because methods can be `undefined`",
             "It is typed `ItemRoute`"],
            0,
            "The flag module 3 introduced. Its last lesson is that the missing "
            "case is often exactly the answer you needed to write."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — a test runner by hand.
# ---------------------------------------------------------------------------

_M20_EXPECT_SOFT = _M20_EXPECT.replace('    throw new Error("expected " + e + ", got " + a);',
                                       '    console.error("expected " + e + ", got " + a);')
_M20_RUNTESTS_NORESET = _M20_RUNTESTS.replace("    resetStore();\n", "")
assert _M20_EXPECT_SOFT != _M20_EXPECT and _M20_RUNTESTS_NORESET != _M20_RUNTESTS

_M20_S3 = _pstep(
    "runner", "A test runner in thirty lines",
    "`test`, `expectEqual`, `runTests` — and the two ways a home-made runner lies.",
    """
The service answers in values, so checking it is comparing values. Here is
everything a test framework has to do, written out:

```ts
type Test = {
  name: string;
  run: () => void;
};

const tests: Test[] = [];

function test(name: string, run: () => void): void {
  tests.push({ name: name, run: run });
}
```

**A test is a name and a function**, and `test(…)` only *records* it. Nothing
runs yet. (`() => void` is a function type — the shape of a function with no
parameters that returns nothing.)

```ts
function expectEqual(actual: unknown, expected: unknown): void {
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a !== e) {
    throw new Error("expected " + e + ", got " + a);
  }
}
```

**An assertion is a `throw`.** Comparing as JSON is crude and honest: two todos
are equal if they would look the same on the wire — the thing clients see. (It
is also key-order sensitive, which module 5 warned about. Build expected objects
in the order the code does.)

```ts
function runTests(): void {
  let failed = 0;
  for (const t of tests) {
    resetStore();
    try {
      t.run();
      console.log("ok - " + t.name);
    } catch (err: unknown) {
      failed = failed + 1;
      if (err instanceof Error) {
        console.log("not ok - " + t.name + ": " + err.message);
      } else {
        console.log("not ok - " + t.name);
      }
    }
  }
  console.log(tests.length - failed + " passed, " + failed + " failed");
}
```

**Running is a loop, a `try`, and a count.** One test's failure is caught and
reported, and the next test still runs — module 16's boundary, one per test.

### The two ways it can lie

**Shared state.** Every test starts with `resetStore()` — an empty list and a
counter back at 1. Without it, the second test sees the first one's todos, its
ids are off by however many came before, and whether it passes depends on the
*order* the tests run in. Tests must not be able to see each other.

**An assertion that does not assert.** If `expectEqual` logged instead of
throwing, every test would print `ok`. A runner that cannot fail is worse than
none, because it is believed. So the suite includes a test *of* `expectEqual`:

```ts
test("expectEqual fails on a mismatch", () => {
  let threw = false;
  try {
    expectEqual(1, 2);
  } catch {
    threw = true;
  }
  if (!threw) {
    throw new Error("expectEqual let 1 equal 2");
  }
});
```

That is all a framework is. The ones you will use add nicer output, async tests,
filtering, and a hundred conveniences — and every one of them is these thirty
lines underneath.
""",
    """
```
ok - a new todo gets the next id, not done
ok - ids are never reused after a delete
ok - a blank title is refused, naming the field
…
ok - expectEqual fails on a mismatch
10 passed, 0 failed
```

Ten tests of the whole API's rules, in a program with no server in it.
""",
    pitfalls=[
        "The second test fails with id 4 where it expected 3 — and passes when run alone. The tests share a store: reset it before each one.",
        "Every test passes, including the one testing `expectEqual` — no, that one fails, because `expectEqual` logs instead of throwing. An assertion that does not throw cannot fail a test.",
        "Comparing objects with `===`. Two separately built todos are never `===`; compare their JSON.",
        "Building the expected object in a different key order — `{ done: false, id: 1, title: … }` — so the JSON differs. Match the order the code builds them in.",
        "Stopping at the first failure. Each test runs in its own `try`, so one failure is reported and the rest still run — you want the whole list of what broke.",
    ],
    warmup=[
        _pq("What does calling `test(\"…\", () => { … })` do?",
            ["Records the test in the list — nothing runs until `runTests()`",
             "Runs the test immediately",
             "Runs the test and prints ok",
             "Throws if the test fails"],
            0,
            "Collect first, run later — which is what lets the runner reset the "
            "store between tests and count the results."),
    ],
    exercises=[
        _pex("todo-m20-runner-1", "An assertion is a throw",
             "The values differ. Fail the test — with a message that shows both.",
             _M20_TESTS_FULL,
             'throw new Error("expected " + e + ", got " + a);',
             [("", _M20_TESTS_OUT)],
             ["How does the runner learn that a test failed?",
              "Its `catch` receives whatever was thrown.",
              "`throw new Error(\"expected \" + e + \", got \" + a);`"]),
        _pfix("todo-m20-runner-fix1", "Tests that can see each other",
              "`ids are never reused after a delete` fails — `expected … id 3, got "
              "… id 4` — and passes if it is the only test. Later tests fail "
              "too, with numbers that depend on what ran before them.",
              _m20_tests(runtests=_M20_RUNTESTS_NORESET),
              _M20_TESTS_FULL,
              [("", _M20_TESTS_OUT)],
              ["What is in the store when the second test starts?",
               "There is a function for exactly this, and nothing calls it.",
               "`resetStore();` at the top of the loop, before each test runs."],
              difficulty="Easy"),
        _pfix("todo-m20-runner-fix2", "An assertion that cannot fail",
              "Nine tests pass. The tenth — the test *of* `expectEqual` — says "
              "`expectEqual let 1 equal 2`. If it had not been there, every test "
              "in the suite would pass whatever the code did.",
              _m20_tests(expect=_M20_EXPECT_SOFT),
              _M20_TESTS_FULL,
              [("", _M20_TESTS_OUT)],
              ["What does `expectEqual` do when the values differ?",
               "Can a test fail if nothing is thrown?",
               "`throw new Error(\"expected \" + e + \", got \" + a);` instead of logging."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does every test start with `resetStore()`?",
            ["So no test can see another's todos — each result depends only on the test itself, not on the order they run in",
             "To make them faster",
             "Because the store is saved to disk",
             "To test `resetStore`"],
            0,
            "Isolation. A test that passes only after another one has run is "
            "testing the order, not the code."),
        _pq("Why does the suite test `expectEqual` itself?",
            ["If the assertion cannot fail, every test passes whatever the code does — and the suite is believed",
             "For coverage numbers",
             "Because `JSON.stringify` is unreliable",
             "It does not need to"],
            0,
            "Who tests the tests? One test, once, that proves a failure can be "
            "seen."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the suite as a tool.
# ---------------------------------------------------------------------------

_M20_SORT_IN_PLACE = _M18_SORT.replace("items.slice().sort(", "items.sort(")

_M20_S4 = _pstep(
    "suite", "The suite catches what you missed",
    "Tests as a record of every promise the API made — and using them to find a bug.",
    """
Read the suite's test names as a list:

```
a new todo gets the next id, not done                    module 2
ids are never reused after a delete                      modules 2, 12, 19
a blank title is refused, naming the field               module 14
text that is not JSON is invalid_json                    module 16
a missing todo is not_found, whatever its body           modules 11, 13
a patch with two mistakes names both and changes nothing module 14
the list filters, sorts and pages, with a total          modules 17, 18
sorting never reorders the store                         module 18
every kind of error has its status                       modules 15, 16, 20
expectEqual fails on a mismatch                          this one
```

Every one is a promise some earlier module made in prose and a pitfall. The
suite is where those promises stop depending on anyone remembering them.

### One field of many

```ts
expectEqual(page.items.map((t) => t.title), ["Ship it"]);
expectEqual(page.items.map((t) => t.id), [1, 2]);
```

When a test is about *which* todos and in *what order*, comparing whole todos is
noise. `map` — module 17's — turns the list into just the part the test is
about, and the failure message then shows exactly that.

### Using it

Here is how this goes in practice. Someone tidies `sortTodos` and drops a
`.slice()` that looked redundant. Every request still works. The manual test in
module 18 would catch it — if anyone ran it. Instead:

```
ok - the list filters, sorts and pages, with a total
not ok - sorting never reorders the store: expected [1,2], got [2,1]
9 passed, 1 failed
```

The test names the promise that broke, and the message shows how. You fix the
**code**, not the test.

### And over HTTP?

The judged programs cannot start a second process to fetch from, so the
end-to-end check lives in the manual test: a `smoke.ts` that starts nothing,
fetches your running server, and compares status lines — which is exactly what
the replayer has been doing since module 4, minus the expected output. You have
been reading a smoke-test runner for sixteen modules.
""",
    """
With `sortTodos` correct, all ten pass:

```
…
ok - sorting never reorders the store
…
10 passed, 0 failed
```
""",
    pitfalls=[
        "`sorting never reorders the store` fails with `expected [1,2], got [2,1]` — `sortTodos` sorts `items` in place, and with no filter `items` is the store. Fix the code: `.slice()` before `.sort()`.",
        "\"Fixing\" a failing test by changing what it expects. A test that fails is reporting a broken promise; change the expectation only if the promise itself was wrong.",
        "Tests that compare whole objects when they are about one field. The failure message becomes a wall of JSON; `map` to the part that matters.",
        "Testing through HTTP what the service can answer directly. Every test that needs a server is slower and fails for more reasons than the one it is about.",
        "A suite nobody runs. Put `node test.ts` next to `node server.ts` and run it before every change you keep.",
    ],
    warmup=[
        _pq("A test fails after a change you were sure was harmless. What do you change first?",
            ["The code — the test is reporting a promise your change broke",
             "The test's expected value",
             "Delete the test",
             "Nothing; tests are flaky"],
            0,
            "Unless the promise itself was wrong. That is a decision, not a fix."),
    ],
    exercises=[
        _pfix("todo-m20-suite-fix1", "The test that caught it",
              "One test fails:\n\n"
              "    not ok - sorting never reorders the store: expected [1,2], got [2,1]\n\n"
              "The test is right. Find the code that breaks the promise and fix it.",
              _m20_tests(sort=_M20_SORT_IN_PLACE),
              _M20_TESTS_FULL,
              [("", _M20_TESTS_OUT)],
              ["Which function sorts, and what array does it sort?",
               "When there is no filter, which array is `items`?",
               "`items.slice().sort(…)` — in both branches of `sortTodos`."],
              difficulty="Easy"),
        _pex("todo-m20-suite-1", "Just the titles",
             "The test is about which todo is on the page. Compare only the "
             "titles of the page's items.",
             _M20_TESTS_FULL,
             "page.items.map((t) => t.title)",
             [("", _M20_TESTS_OUT)],
             ["One title per todo on the page.",
              "Module 17's method for turning each element into something else.",
              "`page.items.map((t) => t.title)`"]),
    ],
    quiz=[
        _pq("Why do the tests call the service rather than send HTTP requests?",
            ["The service holds every rule and answers in values — no server to start, and a failure has one possible cause",
             "HTTP cannot be tested",
             "The service is faster to write",
             "Tests may not use `fetch`"],
            0,
            "Test each thing at the lowest layer that owns it. The smoke test "
            "checks that the layers are wired together."),
        _pq("What does `page.items.map((t) => t.id)` give a test?",
            ["Just the ids, in order — so the assertion and its failure message are about exactly what the test checks",
             "The page's total",
             "A copy of the todos",
             "The store's ids"],
            0,
            "`map` narrows a comparison to the part that matters."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M20_FINAL = _pch(
    "todo-m20-build", "Module 20 build — the finished Todo API", "Hard",
    "Write the service layer — the whole application, with no HTTP in it.\n\n"
    "* `listPage(params)` — the page, or a `validation` error from `listQueryFrom`\n"
    "* `createTodo(body)` — `invalid_json`, `validation`, or the new todo\n"
    "* `getTodo(id)` — the todo, or `not_found`\n"
    "* `patchTodo(id, body)` — `not_found` first, then `invalid_json`, "
    "`validation`, or the updated todo\n"
    "* `removeTodo(id)` — `undefined` if it was deleted, `not_found` if it was "
    "not there\n\n"
    "Everything else — rules, store, disk, the route tables, the boundary — is "
    "written. The script walks the whole contract across two boots.",
    _M20_FULL,
    _M20_SERVICE.rstrip("\n"),
    [("\n".join([_POST_A, _POST_B, _POST_OAT, 'PATCH /todos/2 {"done":true}',
                 "GET /todos?done=false&sort=title", "DELETE /todos/3", 'PUT /todos/1 {"title":"x"}',
                 "DELETE /todos", "POST /todos not json", 'POST /todos {"title":""}',
                 "PATCH /todos/9 nope", "GET /todos/3", "GET /todos?limit=1&offset=1",
                 "GET /todos?sort=size"]),
      "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "201 " + _TODO_OAT3, "200 " + _TODO_B_DONE,
                 _page(2, _TODO_A, _TODO_OAT3), "204", _M405_ITEM, _M405_COLL, _BADJSON,
                 _v(_FE_EMPTY), _NF, _NF, _page(2, _TODO_B_DONE), _v(_FE_SORT),
                 _file(4, _TODO_A, _TODO_B_DONE)])),
     ("\n".join([_file(4, _TODO_A, _TODO_B_DONE), _POST_OAT,
                 "GET /todos?sort=newest", 'PATCH /todos/4 {"title":"Buy oat milk!","done":"no"}',
                 "GET /todos/4", "DELETE /todos/1", "GET /todos?q=milk"]),
      "\n".join(["201 " + _TODO_OAT4, _page(3, _TODO_OAT4, _TODO_B_DONE, _TODO_A),
                 _v(_FE_DONE), "200 " + _TODO_OAT4, "204", _page(1, _TODO_OAT4),
                 _file(5, _TODO_B_DONE, _TODO_OAT4)])),
     _bad_file_case('{"nextId":2,"todos":[{"id":1,"title":"","done":false}]}', "not a saved todo list",
                    (_POST_A, "GET /todos"))],
    ["Every service function answers a value — never sends, never mentions `res`.",
     "`createTodo`: `parseJson`, then `createFrom`, then `addTodo` — each failure as its `ApiError`.",
     "`patchTodo`: `findTodo` **first**, so `PATCH /todos/9 nope` is a 404.",
     "`removeTodo`: `if (!deleteTodo(id)) { return { kind: \"not_found\" }; } return undefined;`",
     "`listPage`: `listQueryFrom(params)` — a list is `{ kind: \"validation\", fields: query }`; otherwise `listTodos(query)`."],
)


_TODO_MODULES.append(_pmod(
    key="todo-structure", number=20, phase="real",
    title="A router, layers and a smoke test",
    what="split store / service / routes, then prove it with a test you wrote",
    goal="Leave the code in layers that each do one job, behind a router that knows which verbs a path allows, with a hand-written test suite proving every rule the API promised.",
    why=_M20_WHY,
    est_minutes=70,
    builds_on=["todo-persist"],
    concepts=["layers", "dependency direction", "service layer", "function types",
              "Record as a lookup table", "405 Method Not Allowed", "Allow header",
              "a test runner", "assertions", "test isolation", "smoke test"],
    deliverable="The finished Todo API: rules, store, service and http in layers "
                "that each call only the ones below; a router that answers 405 with "
                "the allowed methods; and a zero-dependency test suite that checks "
                "every promise the project made.",
    objectives=[
        "Organise the code into rules, store, service and http, each calling only the layers below it",
        "Write service functions that take plain values and answer a value or an `ApiError`, with no reference to HTTP",
        "Prove the layering with the compiler: the application below http compiles with no `node:http` import",
        "Route with tables keyed by method, and turn a lookup miss into a 405 whose `allow` list comes from the table",
        "Write a test runner — `test`, `expectEqual`, `runTests` — and say what each part of a framework is for",
        "Keep tests isolated, test the assertion itself, and use a failing test to find a bug in the code rather than the test",
    ],
    endpoints=[
        _pep("*", "/todos · /todos/:id", "A verb the path does not support — the route table's keys say which do",
             "", '{"error":"method_not_allowed","allow":[…]}', "405"),
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M20_BRIEF,
    syntax=_M20_SYNTAX,
    steps=[_M20_S1, _M20_S2, _M20_S3, _M20_S4],
    final_build=_M20_FINAL,
    acceptance=[
        "`server.ts` is in four sections — rules, store, service, http — and no function calls one in a section after its own.",
        "No service function's signature mentions `IncomingMessage` or `ServerResponse`.",
        "`curl -s -i -X DELETE localhost:3000/todos` returns 405, `Allow: GET, POST`, and the same list in the body.",
        "`curl -s -i -X PUT localhost:3000/todos/1 -d '{}'` returns 405 with `Allow: GET, PATCH, DELETE`; `GET /todos/abc` is still 404.",
        "`node test.ts` prints `ok` for every test and a count, with no dependencies installed.",
        "Deleting `resetStore()` from the runner, or making `expectEqual` log instead of throw, makes the suite report a failure.",
        "Every acceptance check from modules 1-19 still passes — the refactor changed no response except `405`.",
    ],
    manual_test="""
**Split the file.** Node runs `.ts` imports directly, so the layers can be real
files:

```
rules.ts     objectFrom · FieldError · titleFrom · … · parseJson · ApiError · errorReply
store.ts     import { … } from "./rules.ts";   Todo · todos · addTodo · … · loadStore
service.ts   import { … } from "./store.ts";   createTodo · patchTodo · …
server.ts    import { … } from "./service.ts"; the route tables · route · handler · listen
test.ts      import { … } from "./service.ts"; the runner and the suite
```

Put `export` in front of everything another file uses, and `import { addTodo,
findTodo } from "./store.ts"` where it is needed. (For `tsc`, add
`--allowImportingTsExtensions`.) If `service.ts` ever needs to import from
`server.ts`, a layer is calling up — stop and move the code.

**Run the tests:**

```bash
node test.ts
```

Every line `ok`. Now break something on purpose — delete the `.slice()` in
`sortTodos` — and run it again. Put it back.

**The smoke test** checks the layers are wired together, against the real
server. Start it, then save this as `smoke.ts` and run `node smoke.ts`:

```ts
const base = "http://127.0.0.1:3000";
const checks: [string, string, string | undefined, number][] = [
  ["POST", "/todos", '{"title":"Smoke"}', 201],
  ["GET", "/todos", undefined, 200],
  ["DELETE", "/todos", undefined, 405],
  ["PATCH", "/todos/999999", "nope", 404],
  ["POST", "/todos", "not json", 400],
];
let failed = 0;
for (const [method, path, body, want] of checks) {
  const reply = await fetch(base + path, { method: method, body: body });
  const ok = reply.status === want;
  if (!ok) {
    failed = failed + 1;
  }
  console.log((ok ? "ok" : "not ok") + " - " + method + " " + path + " → " + reply.status);
}
console.log(failed === 0 ? "smoke: all good" : "smoke: " + failed + " failed");
```

It is the replayer with expectations — which is all a smoke test is.

**And last**, run the whole project's acceptance list from the top. Every check
from module 1 on should still pass. That is what finished means.
""",
    reference="""// server.ts — module 20: the finished Todo API
//
// Four layers, each calling only the ones above it in this file:
//
//   rules     what input may say — pure checks, no data, no I/O
//   store     the data, in memory and on disk
//   service   what the API does — plain values in, a value or an ApiError out
//   http      requests and responses: the only code that knows HTTP exists
//
// The service is the whole application with the HTTP taken out, which is what
// lets test.ts check every rule without starting a server. Routes live in two
// tables keyed by method, so a verb a path does not support is a 405 that lists
// the ones it does.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFileSync, writeFileSync, existsSync } from "node:fs";

// ============================================================================
// rules — what input may say
// ============================================================================

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

// What a client asked the list. The defaults live in one place — the object
// listQueryFrom starts from — so an absent parameter just leaves its default.
type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
  sort: Sort;
  limit: number;
  offset: number;
};

// The query string is input, checked like a body and refused in the same shape,
// every error collected. Absent means the default; present and unreadable is a
// 400; parameters we do not know are ignored. `limit` has a ceiling, or one
// request could ask for the whole list — the load paging exists to prevent.
function listQueryFrom(params: URLSearchParams): ListQuery | FieldError[] {
  const query: ListQuery = { done: undefined, q: undefined, sort: "oldest", limit: 20, offset: 0 };
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
  const sort = params.get("sort");
  if (sort === "oldest" || sort === "newest" || sort === "title") {
    query.sort = sort;                         // narrowed to Sort by the three ===
  } else if (sort !== null) {
    errors.push({ field: "sort", message: "must be oldest, newest or title" });
  }
  const limit = params.get("limit");
  if (limit !== null) {
    const n = Number(limit);
    if (Number.isInteger(n) && n >= 1 && n <= 100) {
      query.limit = n;
    } else {
      errors.push({ field: "limit", message: "must be a whole number from 1 to 100" });
    }
  }
  const offset = params.get("offset");
  if (offset !== null) {
    const n = Number(offset);
    if (Number.isInteger(n) && n >= 0) {
      query.offset = n;
    } else {
      errors.push({ field: "offset", message: "must be a whole number, 0 or more" });
    }
  }
  if (errors.length > 0) {
    return errors;
  }
  return query;
}

// JSON.parse THROWS on text that is not JSON — an expected failure, caught here
// and turned back into an ordinary value the caller must check. The only
// JSON.parse in the file: requests and todos.json both come through it.
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

// Every failure the API can report, tagged by `kind`. Adding a kind makes
// errorReply's `never` line fail until it has a case — which is how
// method_not_allowed got its 405.
type ApiError =
  | { kind: "not_found" }
  | { kind: "method_not_allowed"; allow: string[] }
  | { kind: "validation"; fields: FieldError[] }
  | { kind: "invalid_json" }
  | { kind: "server_error" };

type ErrorReply = {
  status: number;
  body: object;
};

// The ONE place a failure becomes a status and a body — so they can never
// disagree. Pure: it decides and sends nothing, which is why it is a rule and
// not HTTP, and why test.ts can check it.
function errorReply(err: ApiError): ErrorReply {
  switch (err.kind) {
    case "not_found":
      return { status: 404, body: { error: "not_found" } };
    case "method_not_allowed":
      return { status: 405, body: { error: "method_not_allowed", allow: err.allow } };
    case "validation":
      return { status: 400, body: { error: "validation", fields: err.fields } };
    case "invalid_json":
      return { status: 400, body: { error: "invalid_json" } };
    case "server_error":
      return { status: 500, body: { error: "server_error" } };
  }
  // Every case returns, so `err` is `never` here — nothing is left for it to be.
  const unhandled: never = err;
  return unhandled;
}

// ============================================================================
// store — the data, in memory and on disk
// ============================================================================

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

// Write-through: the three functions that change the store each end with
// saveStore(), so memory and disk never disagree for longer than one call.
const DATA_FILE = "todos.json";

function saveStore(): void {
  writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));
}

function addTodo(title: string): Todo {
  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;
  todos.push(todo);
  saveStore();
  return todo;
}

function findTodo(id: number): Todo | undefined {
  return todos.find((t) => t.id === id);
}

function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  saveStore();
  return updated;
}

function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  saveStore();
  return true;
}

type Sort = "oldest" | "newest" | "title";

// Sorts work on a copy: `sort` rearranges the array it is called on, and with no
// filter `items` IS the store — whose id order a plain GET /todos relies on.
function sortTodos(items: Todo[], sort: Sort): Todo[] {
  if (sort === "newest") {
    return items.slice().sort((a, b) => b.id - a.id);
  }
  if (sort === "title") {
    return items.slice().sort((a, b) => a.title.localeCompare(b.title));
  }
  return items;
}

type Page = {
  items: Todo[];
  total: number;
};

// Filter, then sort, then cut. `total` counts what matched, before the cut.
function listTodos(query: ListQuery): Page {
  let items = todos;
  if (query.done !== undefined) {
    items = items.filter((t) => t.done === query.done);
  }
  if (query.q !== undefined) {
    const q = query.q.toLowerCase();
    items = items.filter((t) => t.title.toLowerCase().includes(q));
  }
  const sorted = sortTodos(items, query.sort);
  const page = sorted.slice(query.offset, query.offset + query.limit);
  return { items: page, total: sorted.length };
}

// The file is input: checked with the request rules, plus two that relate todos
// to each other — ids strictly increasing, all below nextId.
type Saved = {
  nextId: number;
  todos: Todo[];
};

function todoFrom(value: unknown): Todo | undefined {
  const obj = objectFrom(value);
  if (obj === undefined || !("id" in obj) || !("title" in obj) || !("done" in obj)) {
    return undefined;
  }
  const id = obj.id;
  const title = titleFrom(obj.title);
  if (typeof id !== "number" || !Number.isInteger(id) || id < 1) {
    return undefined;
  }
  if (typeof title !== "string" || typeof obj.done !== "boolean") {
    return undefined;
  }
  return { id: id, title: title, done: obj.done };
}

function savedFrom(data: unknown): Saved | undefined {
  const obj = objectFrom(data);
  if (obj === undefined || !("nextId" in obj) || !("todos" in obj)) {
    return undefined;
  }
  const next = obj.nextId;
  if (typeof next !== "number" || !Number.isInteger(next) || next < 1 || !Array.isArray(obj.todos)) {
    return undefined;
  }
  const items: unknown[] = obj.todos;
  const loaded: Todo[] = [];
  let lastId = 0;
  for (const item of items) {
    const todo = todoFrom(item);
    if (todo === undefined || todo.id <= lastId || todo.id >= next) {
      return undefined;
    }
    loaded.push(todo);
    lastId = todo.id;
  }
  return { nextId: next, todos: loaded };
}

// No file is a first start. A bad file stops the boot rather than be
// overwritten by the first change. The counter is restored, never worked out.
function loadStore(): void {
  if (!existsSync(DATA_FILE)) {
    return;
  }
  const parsed = parseJson(readFileSync(DATA_FILE, "utf8"));
  if (!parsed.ok) {
    throw new Error(DATA_FILE + " is not JSON");
  }
  const saved = savedFrom(parsed.data);
  if (saved === undefined) {
    throw new Error(DATA_FILE + " is not a saved todo list");
  }
  todos.push(...saved.todos);
  nextId = saved.nextId;
}

// ============================================================================
// service — what the API does, with no HTTP in it
// ============================================================================
// Each function is one route's rules, in the order they apply, answering a
// VALUE: the result, or what went wrong as an ApiError. None of them mentions a
// request or a response — which the compiler proves every time test.ts, which
// imports no node:http, type-checks against them.

function listPage(params: URLSearchParams): Page | ApiError {
  const query = listQueryFrom(params);
  if (Array.isArray(query)) {
    return { kind: "validation", fields: query };
  }
  return listTodos(query);
}

function createTodo(body: string): Todo | ApiError {
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const checked = createFrom(parsed.data);
  if (Array.isArray(checked)) {
    return { kind: "validation", fields: checked };
  }
  return addTodo(checked);
}

function getTodo(id: number): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  return todo;
}

// Look up FIRST: a bad body sent to a todo that does not exist is not_found,
// as it has been since module 13.
function patchTodo(id: number, body: string): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  const parsed = parseJson(body);
  if (!parsed.ok) {
    return { kind: "invalid_json" };
  }
  const checked = changesFrom(parsed.data);
  if (Array.isArray(checked)) {
    return { kind: "validation", fields: checked };
  }
  return updateTodo(todo, checked);
}

function removeTodo(id: number): ApiError | undefined {
  if (!deleteTodo(id)) {
    return { kind: "not_found" };
  }
  return undefined;
}

// ============================================================================
// http — the only code that knows about requests and responses
// ============================================================================

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

// HTTP requires a 405 to say what IS allowed, in an `Allow` header; the body
// carries the same list for clients that only read JSON.
function sendError(res: ServerResponse, err: ApiError): void {
  if (err.kind === "method_not_allowed") {
    res.setHeader("Allow", err.allow.join(", "));
  }
  const reply = errorReply(err);
  send(res, reply.status, reply.body);
}

// Where the service's values meet HTTP. Only an ApiError has a `kind`.
function sendResult(res: ServerResponse, status: number, result: Todo | Page | ApiError): void {
  if ("kind" in result) {
    sendError(res, result);
    return;
  }
  send(res, status, result);
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

// Two kinds of path, two tables, each a method → the function that answers it.
// Each route is one call into the service and one call to send its answer.
type CollectionRoute = (req: IncomingMessage, res: ServerResponse, url: URL) => Promise<void>;
type ItemRoute = (req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>;

const collectionRoutes: Record<string, CollectionRoute> = {
  GET: async (req, res, url) => {
    sendResult(res, 200, listPage(url.searchParams));
  },
  POST: async (req, res) => {
    sendResult(res, 201, createTodo(await readBody(req)));
  },
};

const itemRoutes: Record<string, ItemRoute> = {
  GET: async (req, res, id) => {
    sendResult(res, 200, getTodo(id));
  },
  PATCH: async (req, res, id) => {
    sendResult(res, 200, patchTodo(id, await readBody(req)));
  },
  DELETE: async (req, res, id) => {
    const err = removeTodo(id);
    if (err !== undefined) {
      sendError(res, err);
      return;
    }
    sendEmpty(res, 204);
  },
};

// A lookup in a Record is `Route | undefined` under noUncheckedIndexedAccess —
// and the `undefined` is exactly 405: the path exists, the verb does not. The
// allowed methods come from the table itself, so they cannot disagree with it.
async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const method = req.method ?? "GET";
  if (url.pathname === "/todos") {
    const run = collectionRoutes[method];
    if (run === undefined) {
      sendError(res, { kind: "method_not_allowed", allow: Object.keys(collectionRoutes) });
      return;
    }
    await run(req, res, url);
    return;
  }
  const id = todoId(url.pathname);
  if (id !== undefined) {
    const run = itemRoutes[method];
    if (run === undefined) {
      sendError(res, { kind: "method_not_allowed", allow: Object.keys(itemRoutes) });
      return;
    }
    await run(req, res, id);
    return;
  }
  sendError(res, { kind: "not_found" });
}

// The error boundary: one `try` around every route, so an exception anywhere is
// a logged, plain 500 instead of a dead process.
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

// Load, then listen. A file that cannot be trusted stops the process here.
loadStore();
const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Answer `HEAD` and `OPTIONS` properly: `HEAD` like `GET` without a body, and `OPTIONS` as a 204 with the `Allow` header. Should they appear in the tables, or be handled once in `route` for every path?",
        "Generalise the router: routes as `{ method, pattern: \"/todos/:id\", run }` with a `matchPath(pattern, pathname)` that extracts named parameters. What does it cost, and at how many kinds of path would you switch?",
        "Make the store injectable: `saveStore` and `loadStore` take the file name, and `test.ts` points them at a temporary one — so running the tests never touches `todos.json`.",
        "Add async tests to the runner — `run: () => void | Promise<void>` — and `await` each one. Then write a test that uses `fetch` against a server started on port 0 inside the test, and notice you have rebuilt the replayer.",
        "Pick a real framework — `node:test` is built into Node — and port three tests to it. Which of its features did your thirty lines already have?",
        "Go back to the project's stretch list: `PUT`, tags, a completion endpoint, SQLite via `node:sqlite`, an HTML page. Each is now one table entry, one service function and some tests.",
    ],
    glossary=[
        _pgloss("layer", "A section of code with one job, calling only the layers below it: here rules, store, service and http."),
        _pgloss("service layer", "The application with the transport taken out: plain values in, a value or an `ApiError` out."),
        _pgloss("dependency direction", "The rule that calls only go downward. A call upward is a loop that makes pieces impossible to test alone."),
        _pgloss("function type", "`(req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>` — the shape of a function, as a type."),
        _pgloss("Record", "`Record<string, T>` — an object used as a lookup table from string keys to `T`s."),
        _pgloss("405 Method Not Allowed", "The path exists; the verb is not supported on it. Must carry an `Allow` header listing the verbs that are."),
        _pgloss("assertion", "A check that throws when a value is not what was expected — `expectEqual`. How a test fails."),
        _pgloss("test isolation", "Each test starts from the same known state and cannot see another's effects — `resetStore()` before each."),
        _pgloss("smoke test", "A quick end-to-end check that the assembled system answers at all — requests in, status lines compared."),
    ],
    cheatsheet="""
```
http      readBody · sendError · sendResult · route tables · route · handler
  ↓ calls only downward
service   listPage · createTodo · getTodo · patchTodo · removeTodo   → value | ApiError
  ↓
store     addTodo · findTodo · updateTodo · deleteTodo · listTodos · saveStore · loadStore
  ↓
rules     objectFrom · titleFrom · createFrom · changesFrom · listQueryFrom · parseJson · errorReply
```

```ts
// service: values in, values out — no req, no res
function getTodo(id: number): Todo | ApiError {
  const todo = findTodo(id);
  if (todo === undefined) {
    return { kind: "not_found" };
  }
  return todo;
}

// http: a table per kind of path; a miss is a 405
type ItemRoute = (req: IncomingMessage, res: ServerResponse, id: number) => Promise<void>;
const itemRoutes: Record<string, ItemRoute> = { GET: …, PATCH: …, DELETE: … };

const run = itemRoutes[method];                 // ItemRoute | undefined
if (run === undefined) {
  sendError(res, { kind: "method_not_allowed", allow: Object.keys(itemRoutes) });
  return;
}
await run(req, res, id);

// a test framework, entire
test("name", () => { expectEqual(actual, expected); });   // record
function expectEqual(a: unknown, e: unknown): void {      // assert = throw
  if (JSON.stringify(a) !== JSON.stringify(e)) {
    throw new Error("expected …, got …");
  }
}
for (const t of tests) {                                  // run: reset, try, count
  resetStore();
  try { t.run(); … } catch (err: unknown) { … }
}
```

| Request | Module 19 | Module 20 |
|---|---|---|
| `DELETE /todos` | 404 | **405** `allow: ["GET","POST"]` |
| `PUT /todos/1` · `POST /todos/1` | 404 | **405** `allow: ["GET","PATCH","DELETE"]` |
| `GET /todos/abc` | 404 | 404 — not an item path |
| everything else | — | byte-for-byte the same |
""",
    self_check=[
        "Can you name the four layers, what each is for, and the one direction calls may go?",
        "Can you say what a service function takes and returns, and why it never mentions `res`?",
        "Can you explain how compiling the service with no `node:http` import proves the layering?",
        "Can you say why `itemRoutes[method]` may be `undefined`, and why that case is a 405 rather than a 404?",
        "Can you write `test`, `expectEqual` and `runTests` from memory, and say what each part of a framework it stands for?",
        "Can you describe the two ways a hand-written runner lies, and the line in each that prevents it?",
    ],
    review=[
        _pq("Which function belongs in the service layer?",
            ["`patchTodo(id, body)` — the route's rules, answering a todo or an `ApiError`",
             "`readBody(req)`",
             "`sendError(res, err)`",
             "`titleFrom(value)`"],
            0,
            "`readBody` and `sendError` are HTTP; `titleFrom` is a rule. The "
            "service is the part that decides what the API does."),
        _pq("`DELETE /todos`. Why is 405 right and 404 wrong?",
            ["The address exists; only the verb is unsupported — and a 405 says which verbs are",
             "Because DELETE is never allowed",
             "Because 404 is for items only",
             "404 is right"],
            0,
            "Status codes say *whose mistake, and what kind*. Wrong verb and wrong "
            "address are different mistakes."),
        _pq("Where does the 405's list of allowed methods come from?",
            ["`Object.keys` of the route table the router just looked in",
             "A constant written next to each path",
             "The HTTP specification",
             "The client's request"],
            0,
            "A list derived from the table cannot drift from the table."),
        _pq("What is a test framework, at bottom?",
            ["A list of named functions, a `try`/`catch` around each, an assertion that throws, fresh state per test, and a count",
             "A library that must be installed",
             "A way to run the server",
             "A type checker"],
            0,
            "Everything else a framework offers is convenience layered on those "
            "five things."),
        _pq("A test passes when run alone and fails in the suite. What is the likeliest cause?",
            ["Shared state — an earlier test left todos behind; reset before each test",
             "The test is wrong",
             "The suite runs too fast",
             "`JSON.stringify` is non-deterministic"],
            0,
            "Order-dependent results are the signature of tests that can see "
            "each other."),
        _pq("A test fails after a change. When is changing the test's expectation the right fix?",
            ["Only when the promise it checks was itself wrong, and you have decided to change the promise",
             "Always — the code is newer",
             "Never",
             "When the failure message is long"],
            0,
            "A test is a promise written down. Changing it is changing the "
            "contract, and should feel like it."),
    ],
    milestone="The Todo API is finished: a data model, a store that survives "
              "restarts, every verb on the resource, input that is never trusted, "
              "one error shape, a list you can filter, sort and page — in layers "
              "you could hand to someone, behind a router that knows its verbs, "
              "with a suite that proves every promise. Twenty modules, no framework, "
              "no dependencies, and not a line you were not taught.",
))
