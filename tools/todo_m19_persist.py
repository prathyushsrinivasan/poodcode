# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 19 — Persistence on disk.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-18's program pieces.
#
# THE STORE SURVIVES A RESTART. Every change is written to `todos.json` before
# it is answered — write-through, one `writeFileSync` per change — and the file
# is read back once, at boot. The file holds the counter as well as the todos:
# `{"nextId":4,"todos":[…]}`. Deriving the next id from the todos instead
# (`length + 1`, or the largest id plus one) hands out an id that was deleted
# before the restart — module 2's collision, and module 12's "ids are never
# reused", broken by a reboot. Both derivations are graded.
#
# THE FILE IS UNTRUSTED INPUT, as the roadmap said: module 13 applies to your
# own disk. A file is loaded through the same checks as a request — `objectFrom`,
# module 14's `titleFrom` — plus two a request never needed: ids must be unique
# and ascending (module 18's store-order invariant) and every one below
# `nextId`. A file that fails is REFUSED: the server does not start. The
# tempting alternative — log it and start empty — is graded as a bug, because
# the first write after it overwrites the only copy of the user's data.
#
# GRADING PERSISTENCE needed a new replayer (`_DRIVER_DISK` in projects_track.py):
# an optional first line `FILE <text>` sets todos.json up before boot, the last
# line printed is what it holds afterwards, and a `loadStore` that throws is
# printed as `boot refused: <message>`. It also removes the file when a case has
# no FILE line — which is what resolves the roadmap's flagged risk that one test
# case's file would leak into the next, since the real judge runs every case of
# a submission in one scratch directory.
#
# UNGRADABLE, AND TAUGHT: writing before answering (so a 201 means "on disk")
# prints the same lines either way; and a crash halfway through `writeFileSync`
# can leave half a file, which a write-to-temp-then-rename would prevent — the
# ambient declarations have no `renameSync`, and the stretch list has the idea.
# ---------------------------------------------------------------------------

_M19_STORE = """type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

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
"""

_M19_UPDATE = """function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  saveStore();
  return updated;
}
"""

_M19_DELETE = """function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  saveStore();
  return true;
}
"""

_M19_LOAD = """type Saved = {
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
"""


def _m19(route=_M17_ROUTE, store=_M19_STORE, update=_M19_UPDATE, delete=_M19_DELETE,
         load=_M19_LOAD):
    """A module-19 server program: module 18's, booted from todos.json and
    writing every change back to it."""
    return _server_disk("\n\n".join(p.rstrip("\n") for p in
                                    (store, _M18_SORT, _M18_LIST, _M10_SEND, _M10_READBODY,
                                     _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                     update, delete, _M12_SENDEMPTY,
                                     _M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE,
                                     _M14_CREATE, _M14_CHANGES, _M18_QUERY,
                                     _M16_APIERROR, _M16_REPLY, _M15_SENDERROR,
                                     route, _M16_PARSE, load, _M16_BOUNDARY) if p))


_M19_FULL = _m19()

# --- Step 1's plain program: a round trip through a file -------------------
_M19_S1_BODY = """type Todo = {
  id: number;
  title: string;
  done: boolean;
};

type Saved = {
  nextId: number;
  todos: Todo[];
};

const saved: Saved = {
  nextId: 3,
  todos: [
    { id: 1, title: "Buy milk", done: false },
    { id: 2, title: "Write tests", done: true },
  ],
};

writeFileSync("todos.json", JSON.stringify(saved));
const text = readFileSync("todos.json", "utf8");
console.log(text);
console.log(existsSync("todos.json"));
console.log(existsSync("nothing-here.json"));
const back: unknown = JSON.parse(text);
console.log(JSON.stringify(back) === JSON.stringify(saved));
"""

_M19_S1_OUT = "\n".join([
    '{"nextId":3,"todos":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":true}]}',
    "true", "false", "true"])


def _m19_s1(body=_M19_S1_BODY):
    return 'import { readFileSync, writeFileSync, existsSync } from "node:fs";\n\n' + _pbp(body)


def _file(next_id, *todos):
    return 'FILE {"nextId":%d,"todos":[%s]}' % (next_id, ",".join(todos))


_NOFILE = "FILE (none)"
_TODO_OAT4 = '{"id":4,"title":"Buy oat milk","done":false}'


def _refused(why):
    return "boot refused: todos.json is " + why


_NOT_JSON = _refused("not JSON")
_NOT_SAVED = _refused("not a saved todo list")

_M19_WHY = (
    "Stop the server and start it again, and every todo is gone. The whole API "
    "— eighteen modules of validation, errors, filters and pages — keeps its "
    "data in an array that lives exactly as long as the process. A deploy wipes "
    "it. A crash wipes it. Closing the laptop wipes it. Everything a client "
    "created was only ever borrowed. The last promise on the project's list is "
    "\"stopping the server and starting it again does not lose your todos\", and "
    "nothing so far has kept it."
)

_M19_BRIEF = """
### The whole module in one line

Write every change to a file before answering, read the file back at boot, and
refuse to start from a file you cannot trust.

### Two moments

| When | What | Function |
|---|---|---|
| every change | write the whole store to `todos.json` | `saveStore()` |
| boot | read it back, check it, load it | `loadStore()` |

```json
{"nextId":4,"todos":[{"id":1,"title":"Buy milk","done":false},{"id":2,…}]}
```

The file holds **the counter as well as the todos**. Step 3 is about why the
counter cannot be worked out from them.

### The file is input

You wrote it — but so could a text editor, a half-finished write, a different
version of your server, or a colleague "just fixing one thing". Everything
modules 13 and 14 said about a request body applies to your own disk. And a file
that fails the checks is not an empty list: it is somebody's data, and starting
empty would overwrite it.

### What the replayer does now

It has three new jobs, so persistence can be checked at all:

```
FILE {"nextId":2,"todos":[…]}     ← optional first line: todos.json before boot
GET /todos
POST /todos {"title":"Buy milk"}
```
```
200 {"items":[…],"total":1}
201 {"id":2,…}
FILE {"nextId":3,"todos":[…]}     ← always last: todos.json afterwards
```

It boots the way your `server.ts` will — `loadStore()`, then `createServer` — and
if `loadStore` throws it prints `boot refused: <your message>` instead of
starting.
"""

_M19_SYNTAX = [
    _syn(
        "writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));",
        "Replace the file's whole contents with this string — creating the file "
        "if it does not exist. Returns once the write is done.",
        """
import { writeFileSync } from "node:fs";
writeFileSync("todos.json", "[]");
""",
        "It takes a **string**. An object has to be `JSON.stringify`d first — "
        "`String(obj)` and `obj.toString()` both give `\"[object Object]\"`.",
    ),
    _syn(
        'readFileSync(DATA_FILE, "utf8")',
        "The file's contents as a string. The same function every program in "
        "this track has used to read stdin — with a file name instead of `0`.",
        """
const text = readFileSync("todos.json", "utf8");
""",
        "Throws if the file does not exist — which is what `existsSync` is for.",
    ),
    _syn(
        "existsSync(DATA_FILE)",
        "`true` if there is a file at that path. How a server tells its first-ever "
        "boot from every other one.",
        """
if (!existsSync("todos.json")) {
  // first start: nothing to load
}
""",
        "No file is not an error — it is an empty store. A file that is there and "
        "wrong is a different matter.",
    ),
    _syn(
        'throw new Error(DATA_FILE + " is not JSON");',
        "Module 16's `throw` — here used to *refuse to boot*. Nothing catches it "
        "in `server.ts`, so the process stops with that message.",
        "",
        "Stopping is the right answer: a server that cannot read its data must "
        "not start answering as though it had none.",
    ),
    _syn(
        "const items: unknown[] = obj.todos;",
        "After `Array.isArray`, the compiler types the array as `any[]`. Saying "
        "`unknown[]` puts every element back behind a check.",
        """
if (Array.isArray(obj.todos)) {
  const items: unknown[] = obj.todos;   // each item must earn its type
}
""",
        "`Array.isArray` proves it is an array, not what is in it.",
    ),
    _syn(
        "todos.push(...saved.todos);",
        "Push every element of one array onto another — module 11's spread, in a "
        "call.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — a file round trip.
# ---------------------------------------------------------------------------

_M19_S1 = _pstep(
    "file", "A round trip through a file",
    "`writeFileSync`, `readFileSync` and `existsSync`, and what goes in the file.",
    """
`node:fs` — the module you have imported `readFileSync` from since module 4, to
read stdin — also writes files:

```ts
import { readFileSync, writeFileSync, existsSync } from "node:fs";

writeFileSync("todos.json", text);             // replace the file with `text`
const back = readFileSync("todos.json", "utf8");  // the file, as a string
existsSync("todos.json");                      // is there a file there?
```

All three are **synchronous**: they finish before the next line runs. For a small
file written a few times a second that is fine, and it keeps the order of events
obvious. (Their `async` cousins exist; a stretch goal tries them.)

### What goes in the file

The store is two variables — `todos` and `nextId` — so the file holds both:

```ts
type Saved = {
  nextId: number;
  todos: Todo[];
};
```

```json
{"nextId":3,"todos":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":true}]}
```

`writeFileSync` takes a **string**, so the object is `JSON.stringify`d on the way
out and `JSON.parse`d on the way back — the same pair every request and response
has used since module 5.

### Strings only

```ts
writeFileSync("todos.json", saved);              // does not compile — not a string
writeFileSync("todos.json", saved.toString());   // compiles. Writes "[object Object]".
```

The second is the one that bites: it compiles, runs, and leaves a file that says
`[object Object]` and nothing else. Every object's default `toString` says that.
`JSON.stringify` is the only way to turn a todo into text you can turn back.

### One line per file, on purpose

`JSON.stringify` with one argument writes everything on one line. That is what
the replayer prints, so it is what this track uses. `JSON.stringify(saved, null,
2)` would indent it for humans — equally valid JSON, and a reasonable choice for
your own server.
""",
    """
```
{"nextId":3,"todos":[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write tests","done":true}]}
true
false
true
```

The file's text, that it exists, that another name does not, and that parsing it
gives back exactly what was saved. `[object Object]` on the first line means the
object was never turned into JSON.
""",
    pitfalls=[
        "The file says `[object Object]` — it was written with `toString()` or `String()`. Only `JSON.stringify` makes text you can read back.",
        "`readFileSync(\"todos.json\")` without `\"utf8\"`. It returns bytes, not a string, and the declarations here only accept the string form.",
        "Saving only `todos`. The counter lives next to them and has to survive too — step 3 is why.",
        "Reading a file that may not exist without `existsSync` first. `readFileSync` throws on a missing file.",
        "Assuming the file is JSON because you wrote it. Step 4.",
    ],
    warmup=[
        _pq("`writeFileSync(\"todos.json\", saved.toString())` — what is in the file?",
            ["`[object Object]` — the default text of every object",
             "The object as JSON",
             "Nothing; it throws",
             "It does not compile"],
            0,
            "It compiles because `toString` returns a string. `JSON.stringify` is "
            "the only conversion that can be undone."),
    ],
    exercises=[
        _pex("todo-m19-file-1", "Write it down",
             "Write `saved` to `todos.json`, as JSON.",
             _m19_s1(),
             'writeFileSync("todos.json", JSON.stringify(saved));',
             [("", _M19_S1_OUT)],
             ["The function that writes a whole file takes a name and a string.",
              "Turn the object into a string you can read back.",
              '`writeFileSync("todos.json", JSON.stringify(saved));`']),
        _pfix("todo-m19-file-fix1", "[object Object]",
              "The file is written, and it says `[object Object]`. Nothing of the "
              "two todos survives.",
              _m19_s1(_M19_S1_BODY.replace('writeFileSync("todos.json", JSON.stringify(saved));',
                                           'writeFileSync("todos.json", saved.toString());')),
              _m19_s1(),
              [("", _M19_S1_OUT)],
              ["What does an object's `toString()` return?",
               "Which conversion to text can be turned back into the object?",
               '`writeFileSync("todos.json", JSON.stringify(saved));`'],
              difficulty="Intro"),
        _pex("todo-m19-file-2", "Is it there?",
             "Ask whether a file called `nothing-here.json` exists.",
             _m19_s1(),
             'existsSync("nothing-here.json")',
             [("", _M19_S1_OUT)],
             ["`node:fs` has a function that answers exactly this.",
              "It takes a path and returns a boolean.",
              '`existsSync("nothing-here.json")`']),
    ],
    quiz=[
        _pq("Why does the file hold `nextId` as well as the todos?",
            ["The counter is part of the store's state — step 3 shows it cannot be worked out from the todos",
             "For readability",
             "JSON needs a number at the top level",
             "It does not need to"],
            0,
            "Two variables of state, two fields in the file."),
        _pq("`writeFileSync` returns. What is true?",
            ["The write has finished — the next line runs after it",
             "The write has been queued and will finish later",
             "The file may still be empty",
             "Nothing; it returns immediately"],
            0,
            "Synchronous: done means done. It makes \"save, then answer\" "
            "straightforward."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — write-through: every change, saved.
# ---------------------------------------------------------------------------

_M19_S2_CASES = [
    ("\n".join([_POST_A, _POST_B, 'PATCH /todos/1 {"done":true}', "DELETE /todos/2",
                'POST /todos {"title":""}']),
     "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "200 " + _TODO_A_DONE, "204", _v(_FE_EMPTY),
                _file(3, _TODO_A_DONE)])),
    ("\n".join([_POST_A, _POST_B]),
     "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, _file(3, _TODO_A, _TODO_B)])),
    ("\n".join(["GET /todos", "GET /todos/1", "DELETE /todos/1"]),
     "\n".join([_page(0), _NF, _NF, _NOFILE])),
]

_M19_S2 = _pstep(
    "save", "Every change, written down",
    "`saveStore`, one call in each function that changes the store, and saving before answering.",
    """
Three functions change the store: `addTodo`, `updateTodo`, `deleteTodo`. Each one
ends by writing the whole store to disk:

```ts
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
```

— and the same one line at the end of `updateTodo` and `deleteTodo`, after the
change is made. This is **write-through**: memory and disk never disagree for
longer than one function call.

### Why the store, not the routes

The routes do not know about the file at all. The three functions that change
the store are the only places a change can happen, so they are the only places
that need to save — and a route added next year that calls `addTodo` is saved
without anyone remembering to. Put `saveStore()` in the routes instead and the
first route someone forgets is data that silently vanishes on restart.

### Why the whole store every time

Writing everything on every change is wasteful — and for a few thousand todos it
takes well under a millisecond, and it is impossible to get wrong in the ways
that writing *only what changed* can be. Real databases exist because this stops
being true at some size; this project is not that size.

### Save, then answer

The route calls `addTodo` — which saves — and only then sends its `201`. So a
`201` means *it is on disk*. Answer first and save afterwards, and a crash in
between leaves a client holding an id for a todo that does not exist after the
restart.

### What does not save

A refused create never reaches `addTodo`. A `GET` changes nothing. A `DELETE` of a
todo that is not there returns before `splice`. None of them touch the file — and
on a brand-new server that has only been *read*, there is no file at all.
""",
    """
Three scripts, and what `todos.json` holds after each:

```
create, create, tick, delete, refused create   FILE {"nextId":3,"todos":[{"id":1,…,"done":true}]}
create, create                                 FILE {"nextId":3,"todos":[{"id":1,…},{"id":2,…}]}
list, fetch, delete — reads and misses only     FILE (none)
```

The deleted todo must be gone from the first. If it is still there, one of the
three functions does not save.
""",
    pitfalls=[
        "A deleted todo comes back after a restart — `deleteTodo` changes memory and never saves. Every function that changes the store saves at the end.",
        "The newest todo is missing from the file — `saveStore()` was called before `todos.push`. Save *after* the change.",
        "Calling `saveStore` in the routes. The first route that forgets loses data; the store functions are the only places a change happens.",
        "Answering before saving. A `201` should mean the todo will survive a crash.",
        "Saving on a read. A `GET` changes nothing; writing the file on every request is wasted I/O and a pointless risk.",
    ],
    warmup=[
        _pq("A client gets `201` for a new todo, and the server crashes a moment later. With write-through, is the todo there after the restart?",
            ["Yes — it was written to disk before the 201 was sent",
             "Only if the client retries",
             "No — writes happen on shutdown",
             "Only if it was the last todo"],
            0,
            "Save, then answer. The status code is a promise about the disk."),
    ],
    exercises=[
        _pex("todo-m19-save-1", "Save the whole store",
             "Write the counter and the todos to `DATA_FILE`, as one JSON object "
             "with the keys `nextId` then `todos`.",
             _M19_FULL,
             "  writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));",
             _M19_S2_CASES,
             ["`writeFileSync` replaces the whole file.",
              "The object is `{ nextId: nextId, todos: todos }` — in that order.",
              "`writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));`"]),
        _pfix("todo-m19-save-fix1", "The todo that came back",
              "Delete a todo, restart, and it is back. After the first script, "
              "`todos.json` still holds the deleted *Write tests*.",
              _m19(delete=_M19_DELETE.replace("  todos.splice(i, 1);\n  saveStore();\n", "  todos.splice(i, 1);\n")),
              _M19_FULL,
              _M19_S2_CASES,
              ["Which of the three store functions does not write the file?",
               "Memory changed; did the disk?",
               "`saveStore();` after the `splice`."],
              difficulty="Intro"),
        _pfix("todo-m19-save-fix2", "Saved a moment too soon",
              "After two creates, `todos.json` says `nextId` is 3 — and holds only "
              "*Buy milk*. The todo just created is never in the file until "
              "something else saves.",
              _m19(store=_M19_STORE.replace("  todos.push(todo);\n  saveStore();\n", "  saveStore();\n  todos.push(todo);\n")),
              _M19_FULL,
              _M19_S2_CASES,
              ["What is in `todos` at the moment `saveStore()` runs?",
               "Save after the change, not before it.",
               "`todos.push(todo);` then `saveStore();`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does `saveStore()` live in `addTodo`, `updateTodo` and `deleteTodo`, not in the routes?",
            ["They are the only places the store changes, so every change — including from routes not yet written — is saved",
             "Routes cannot call `writeFileSync`",
             "For speed",
             "It could go either place equally well"],
            0,
            "Put a rule where it cannot be forgotten."),
        _pq("A fresh server answers `GET /todos` twice and a `DELETE` of a missing todo. What is on disk?",
            ["Nothing — no file; nothing changed",
             "`{\"nextId\":1,\"todos\":[]}`",
             "An empty file",
             "`[]`"],
            0,
            "Only changes are written. A server that has only been read has "
            "nothing to save."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — load at boot, counter included.
# ---------------------------------------------------------------------------

_M19_FILE_A_B = _file(4, _TODO_A, _TODO_B_DONE)
_M19_S3_CASES = [
    ("\n".join([_M19_FILE_A_B, "GET /todos", _POST_OAT, "GET /todos/4", "GET /todos/3"]),
     "\n".join([_page(2, _TODO_A, _TODO_B_DONE), "201 " + _TODO_OAT4, "200 " + _TODO_OAT4, _NF,
                _file(5, _TODO_A, _TODO_B_DONE, _TODO_OAT4)])),
    ("GET /todos",
     "\n".join([_page(0), _NOFILE])),
    ("\n".join(['FILE {"nextId":1,"todos":[]}', _POST_A]),
     "\n".join(["201 " + _TODO_A, _file(2, _TODO_A)])),
]

_M19_LOADSTORE = _M19_LOAD.split("function loadStore", 1)[1]
_M19_LOAD_NO_NEXT = _M19_LOAD.replace("  todos.push(...saved.todos);\n  nextId = saved.nextId;\n",
                                      "  todos.push(...saved.todos);\n")
_M19_LOAD_LENGTH = _M19_LOAD.replace("  nextId = saved.nextId;\n", "  nextId = saved.todos.length + 1;\n")
assert _M19_LOAD_NO_NEXT != _M19_LOAD and _M19_LOAD_LENGTH != _M19_LOAD

_M19_S3 = _pstep(
    "load", "Boot from the file",
    "`loadStore`, the first-ever start, and why the counter cannot be worked out from the todos.",
    """
Once, before the server starts listening, read the file back:

```ts
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
```

and at the bottom of `server.ts`:

```ts
loadStore();
const server = createServer(handler);
```

**No file is not an error.** It is the first time this server has ever run, and
the store starts empty. `existsSync` tells the two apart. (`savedFrom` is step
4's; for now, read it as "the checked contents, or `undefined`".)

`parseJson` is module 16's, reused: the file is text that might not be JSON,
exactly like a request body.

### The counter is state

Look at this file:

```json
{"nextId":4,"todos":[{"id":1,…},{"id":2,…}]}
```

Two todos, and the next id is **4**. There was a todo 3; it was deleted. Now
suppose the file held only the todos and the server worked the counter out:

| Worked out as | Gives | Next todo gets |
|---|---|---|
| `todos.length + 1` | 3 | id 3 — **the deleted one's** |
| largest id + 1 | 3 | id 3 — **the deleted one's** |
| never restored | 1 | id 1 — **a duplicate** |
| saved in the file | 4 | id 4 ✓ |

Every derivation reissues the id of the last todo deleted before the restart. A
client that still holds id 3 — in a URL, a bookmark, another database — now
points at a different todo. Module 2 demonstrated this collision with
`length + 1` before there was even a delete; module 12 promised *ids are never
reused*. A restart is just a slower way to break that promise, and the only fix
is to remember the counter.

### And refusing to start

If the file is there and wrong, `loadStore` **throws** — and nothing catches it.
The process stops with the message, before it has answered a single request.
Next step is about why that is the right thing to do.
""",
    """
```
FILE {"nextId":4,"todos":[{"id":1,…},{"id":2,…,"done":true}]}
GET /todos                   → both, total 2
POST /todos {"title":"Buy oat milk"}   → id 4 — not 3, not 1
FILE {"nextId":5,"todos":[…three…]}
```

And with no file at all: an empty list, and still no file afterwards.
""",
    pitfalls=[
        "After a restart the next todo gets id 1, duplicating one that exists — `loadStore` loaded the todos and never restored `nextId`.",
        "After a restart the next todo reuses a deleted id — the counter was worked out as `todos.length + 1` (or largest id + 1). Save it; load it.",
        "Treating a missing file as an error. It is the first boot; start empty.",
        "`todos = saved.todos;` — `todos` is a `const`. Push the loaded todos into it instead, so every function holding a reference to the store sees them.",
        "Calling `loadStore()` after `listen`. For a moment the server answers from an empty store. Load, then listen.",
    ],
    warmup=[
        _pq("The file says `{\"nextId\":4,\"todos\":[…ids 1 and 2…]}`. What id does the next todo get?",
            ["4 — the saved counter; 3 was used and deleted",
             "3 — one more than the largest id",
             "3 — one more than the count",
             "1 — the counter resets on boot"],
            0,
            "The gap at 3 is history, and the counter is how the store remembers it."),
    ],
    exercises=[
        _pfix("todo-m19-load-fix1", "Id 1, again",
              "After booting from a file of two todos, `POST /todos` answers "
              "`201 {\"id\":1,…}` — and there is already a todo 1.",
              _m19(load=_M19_LOAD_NO_NEXT),
              _M19_FULL,
              _M19_S3_CASES,
              ["What is `nextId` after `loadStore` runs?",
               "The file has it; does the store get it?",
               "`nextId = saved.nextId;` after the push."],
              difficulty="Intro"),
        _pfix("todo-m19-load-fix2", "A counter worked out",
              "After booting from a file of two todos whose `nextId` is 4, the next "
              "todo gets id 3 — the id of a todo deleted before the restart.",
              _m19(load=_M19_LOAD_LENGTH),
              _M19_FULL,
              _M19_S3_CASES,
              ["Where does the new `nextId` come from?",
               "Two todos, ids 1 and 2, and 3 was deleted. Can the count tell you that?",
               "The file saved the counter for exactly this. `nextId = saved.nextId;`"],
              difficulty="Easy"),
        _pch("todo-m19-load-1", "Write loadStore", "Easy",
             "Write the body of `loadStore()`:\n\n"
             "* no file → return; the store stays empty\n"
             "* read it and `parseJson` it — not JSON → throw `todos.json is not JSON`\n"
             "* `savedFrom` it — `undefined` → throw `todos.json is not a saved todo list`\n"
             "* otherwise push the todos into the store, and restore the counter",
             _M19_FULL,
             _M19_LOADSTORE.split("{\n", 1)[1].rsplit("\n}", 1)[0],
             _M19_S3_CASES + [("FILE nope\nGET /todos", "\n".join([_NOT_JSON, "FILE nope"]))],
             ["`if (!existsSync(DATA_FILE)) { return; }`",
              "`const parsed = parseJson(readFileSync(DATA_FILE, \"utf8\"));`",
              "`throw new Error(DATA_FILE + \" is not JSON\");` — the message is checked.",
              "`todos.push(...saved.todos); nextId = saved.nextId;`"]),
    ],
    quiz=[
        _pq("Why not work out `nextId` as the largest saved id plus one?",
            ["If the newest todo was deleted before the restart, its id would be handed out again",
             "Because finding the largest id is slow",
             "Because ids are strings",
             "It works fine"],
            0,
            "A deleted id is only remembered by the counter. Lose the counter and "
            "you lose the promise that ids are never reused."),
        _pq("There is no `todos.json`. What does `loadStore` do?",
            ["Returns — it is the first boot, and the store starts empty",
             "Throws — the file is missing",
             "Creates an empty file",
             "Waits for the file"],
            0,
            "No file is a normal state. A bad file is not."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the file is input too.
# ---------------------------------------------------------------------------

def _bad_file_case(file_text, why, requests=("GET /todos",)):
    return ("\n".join(["FILE " + file_text] + list(requests)),
            "\n".join([_refused(why), "FILE " + file_text]))


_T1_OK = '{"id":1,"title":"Buy milk","done":false}'
_M19_S4_CASES = [
    _bad_file_case("not json", "not JSON", ("GET /todos", _POST_A)),
    _bad_file_case("[]", "not a saved todo list", ("GET /todos", _POST_A)),
    _bad_file_case('{"nextId":2,"todos":[{"id":1,"title":5,"done":false}]}', "not a saved todo list"),
    _bad_file_case('{"nextId":2,"todos":[{"id":1,"title":"","done":false}]}', "not a saved todo list"),
    _bad_file_case('{"nextId":3,"todos":[' + _T1_OK + ',{"id":1,"title":"Write tests","done":false}]}',
                   "not a saved todo list"),
    _bad_file_case('{"nextId":1,"todos":[' + _T1_OK + "]}", "not a saved todo list"),
    _bad_file_case('{"nextId":2.5,"todos":[]}', "not a saved todo list"),
    ('FILE {"nextId":2,"todos":[' + _T1_OK + "]}\nGET /todos",
     "\n".join([_page(1, _TODO_A), 'FILE {"nextId":2,"todos":[' + _T1_OK + "]}"])),
]

_M19_LOAD_FORGIVING = _M19_LOAD.replace("""  const parsed = parseJson(readFileSync(DATA_FILE, "utf8"));
  if (!parsed.ok) {
    throw new Error(DATA_FILE + " is not JSON");
  }
  const saved = savedFrom(parsed.data);
  if (saved === undefined) {
    throw new Error(DATA_FILE + " is not a saved todo list");
  }""", """  const parsed = parseJson(readFileSync(DATA_FILE, "utf8"));
  if (!parsed.ok) {
    console.error(DATA_FILE + " is not JSON; starting empty");
    return;
  }
  const saved = savedFrom(parsed.data);
  if (saved === undefined) {
    console.error(DATA_FILE + " is not a saved todo list; starting empty");
    return;
  }""")
assert _M19_LOAD_FORGIVING != _M19_LOAD

_M19_LOAD_SHAPE_ONLY = _M19_LOAD.replace("""  const id = obj.id;
  const title = titleFrom(obj.title);
  if (typeof id !== "number" || !Number.isInteger(id) || id < 1) {
    return undefined;
  }
  if (typeof title !== "string" || typeof obj.done !== "boolean") {
    return undefined;
  }
  return { id: id, title: title, done: obj.done };""", """  const id = obj.id;
  const title = obj.title;
  if (typeof id !== "number" || !Number.isInteger(id) || id < 1) {
    return undefined;
  }
  if (typeof title !== "string" || typeof obj.done !== "boolean") {
    return undefined;
  }
  return { id: id, title: title, done: obj.done };""")
assert _M19_LOAD_SHAPE_ONLY != _M19_LOAD

_M19_SAVEDFROM = "function savedFrom" + _M19_LOAD.split("function savedFrom", 1)[1].split("\n}\n", 1)[0] + "\n}"

_M19_S4 = _pstep(
    "trust", "Your own disk is input too",
    "`todoFrom` and `savedFrom`, the checks a file needs that a request never did, and refusing to start.",
    """
You wrote `todos.json`. So did everything else that has ever touched it: a text
editor, a sync tool, an older version of this server, a disk that filled up
halfway through a write, a colleague fixing one typo by hand. The file is input,
and modules 13 and 14 apply to it word for word.

### A todo from the file

```ts
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
```

`objectFrom` from module 13, and **`titleFrom` from module 14** — so a title the
API would refuse over HTTP is refused from disk too. Otherwise a file could hold
a todo that no request could have created, and every later check that assumed
titles are never empty would be wrong.

### The file as a whole

```ts
function savedFrom(data: unknown): Saved | undefined {
  // an object with a whole-number nextId and a todos array…
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
```

Two checks here that a request never needed, because they are about how todos
relate to *each other*:

* **Ids strictly increasing** — `todo.id <= lastId` refuses a duplicate *and* a
  file out of order. Module 18's `oldest` sort relies on the store being in id
  order; a file is how that invariant could be broken from outside.
* **Every id below `nextId`** — or the counter would hand out an id that is
  already taken.

And note `const items: unknown[] = obj.todos;`. `Array.isArray` proves the value
is an array, and the compiler then calls it `any[]` — which would wave every
element through unchecked. Saying `unknown[]` puts each one back behind
`todoFrom`.

### Refuse to start

When the file fails, `loadStore` throws and the server does not start. The
alternative is tempting:

```ts
if (saved === undefined) {
  console.error("bad file; starting empty");
  return;
}
```

It keeps the server up. And then the first client creates a todo, `addTodo`
calls `saveStore`, and the file — the only copy of the user's data, broken by one
stray comma — is **overwritten** with a list of one. A crash would have lost
nothing. A server that will not start is loud, obvious and harmless; someone
fixes the comma and restarts. A server that starts empty is quiet, and destroys
exactly what it was built to keep.
""",
    """
Each of these files stops the server before it answers anything, and is left
exactly as it was:

```
not json                                            boot refused: todos.json is not JSON
[]                                                  boot refused: … is not a saved todo list
{"nextId":2,"todos":[{"id":1,"title":5,…}]}         refused — title is not a string
{"nextId":2,"todos":[{"id":1,"title":"",…}]}        refused — module 14's rule
{…"todos":[{"id":1,…},{"id":1,…}]}                  refused — duplicate id
{"nextId":1,"todos":[{"id":1,…}]}                   refused — id not below nextId
```

And a good file loads.
""",
    pitfalls=[
        "A corrupt file is replaced by a one-todo list after the first create — `loadStore` logged the problem and started empty, and `saveStore` overwrote the only copy. Refuse to start instead.",
        "A todo with an empty title loads from disk — the file was checked for types but not for module 14's rules. Reuse `titleFrom`: a todo no request could create must not load either.",
        "Two todos with the same id load, and `GET /todos/1` can only ever find the first. Ids must be unique — and ascending, which checks both.",
        "Iterating `obj.todos` straight after `Array.isArray` — its elements are `any`, so nothing forces a check. Assign it to `unknown[]` first.",
        "Checking that the file has the right keys and stopping there. A `nextId` of `2.5` or `-1` has the key and is still wrong.",
    ],
    warmup=[
        _pq("The server finds `todos.json` is not valid JSON. What should it do?",
            ["Refuse to start, leaving the file untouched — so someone can fix it",
             "Start empty and log a warning",
             "Delete the file and start empty",
             "Start, and answer 500 to every request"],
            0,
            "Starting empty means the next write destroys the data. Refusing is "
            "loud and loses nothing."),
    ],
    exercises=[
        _pfix("todo-m19-trust-fix1", "Starting empty",
              "A `todos.json` that is not JSON is logged, and the server starts "
              "with an empty list. The first create then answers `201` — and "
              "overwrites the file. Whatever was in it is gone.",
              _m19(load=_M19_LOAD_FORGIVING),
              _M19_FULL,
              _M19_S4_CASES,
              ["What does the first `saveStore()` after boot write over?",
               "A server that cannot read its data should not start answering.",
               "`throw new Error(DATA_FILE + \" is not JSON\");` — and the same for a file that is not a saved todo list."],
              difficulty="Easy"),
        _pfix("todo-m19-trust-fix2", "A todo no request could make",
              "A file holding `{\"title\":\"\"}` loads, and the list shows a todo "
              "with an empty title — which `POST /todos` would have refused.",
              _m19(load=_M19_LOAD_SHAPE_ONLY),
              _M19_FULL,
              _M19_S4_CASES,
              ["Which rules does a title from a request go through?",
               "Is a title from disk checked against the same ones?",
               "`const title = titleFrom(obj.title);`"],
              difficulty="Easy"),
        _pch("todo-m19-trust-1", "Write savedFrom", "Hard",
             "Write `savedFrom(data)` — the checked contents of the file, or "
             "`undefined`:\n\n"
             "* an object with `nextId` and `todos`\n"
             "* `nextId` a whole number, 1 or more; `todos` an array\n"
             "* every element a todo by `todoFrom`, ids strictly increasing, and "
             "every id below `nextId`\n\n"
             "`todoFrom` is written above it.",
             _M19_FULL,
             _M19_SAVEDFROM,
             _M19_S4_CASES,
             ["`const obj = objectFrom(data);` and both `in` checks.",
              "`const next = obj.nextId;` then `typeof`, `Number.isInteger`, `>= 1` — and `Array.isArray(obj.todos)`.",
              "`const items: unknown[] = obj.todos;` so each element must be checked.",
              "Loop with `let lastId = 0;` — refuse if `todo.id <= lastId || todo.id >= next`.",
              "`return { nextId: next, todos: loaded };`"]),
    ],
    quiz=[
        _pq("Why does a todo loaded from disk go through `titleFrom`?",
            ["So the store can never hold a todo no request could have created — every rule holds wherever data comes from",
             "Because the file might be an HTTP request",
             "For speed",
             "It does not need to"],
            0,
            "An invariant is only as strong as its weakest entrance. The file is "
            "an entrance."),
        _pq("`Array.isArray(obj.todos)` is true. What is the type of each element?",
            ["`any` — which is why the array is assigned to `unknown[]` before the loop",
             "`Todo`",
             "`unknown`",
             "`object`"],
            0,
            "`Array.isArray` narrows to `any[]`. One annotation puts the elements "
            "back behind a check."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M19_BUILD_BLANK = "function todoFrom" + _M19_LOAD.split("function todoFrom", 1)[1].rstrip("\n")

_M19_FINAL = _pch(
    "todo-m19-build", "Module 19 build — still there tomorrow", "Hard",
    "Write the loading half of persistence.\n\n"
    "* `todoFrom(value)` — a `Todo` from an unknown value, with module 14's title "
    "rules, a whole-number id from 1, and a boolean `done`; else `undefined`\n"
    "* `savedFrom(data)` — `{ nextId, todos }` with ids strictly increasing and "
    "all below `nextId`; else `undefined`\n"
    "* `loadStore()` — nothing if there is no file; throw `todos.json is not "
    "JSON` or `todos.json is not a saved todo list`; otherwise load the todos and "
    "the counter\n\n"
    "Saving is already done: `saveStore` is at the top, called by every function "
    "that changes the store. The replayer boots with `loadStore()`.",
    _M19_FULL,
    _M19_BUILD_BLANK,
    [("\n".join(['FILE {"nextId":5,"todos":[' + _TODO_A + "," + _TODO_B_DONE + "," + _TODO_SHIP4 + "]}",
                 "GET /todos?done=false", _POST_OAT, 'PATCH /todos/1 {"done":true}', "DELETE /todos/2",
                 "GET /todos?sort=newest&limit=2"]),
      "\n".join([_page(2, _TODO_A, _TODO_SHIP4), '201 {"id":5,"title":"Buy oat milk","done":false}',
                 "200 " + _TODO_A_DONE, "204",
                 _page(3, '{"id":5,"title":"Buy oat milk","done":false}', _TODO_SHIP4),
                 _file(6, _TODO_A_DONE, _TODO_SHIP4, '{"id":5,"title":"Buy oat milk","done":false}')])),
     ("\n".join([_POST_A, "GET /todos"]),
      "\n".join(["201 " + _TODO_A, _page(1, _TODO_A), _file(2, _TODO_A)]))]
    + [c for c in _M19_S4_CASES if c[1].startswith("boot refused")]
    + [_bad_file_case('{"nextId":3,"todos":[{"id":2,"title":"Write tests","done":true},' + _T1_OK + "]}",
                      "not a saved todo list"),
       _bad_file_case('{"todos":[]}', "not a saved todo list")],
    ["`todoFrom`: `objectFrom`, three `in` checks, then `titleFrom(obj.title)` and `typeof` for the rest.",
     "`savedFrom`: `const items: unknown[] = obj.todos;` and a loop tracking `lastId`.",
     "`loadStore`: `existsSync`, then `parseJson(readFileSync(DATA_FILE, \"utf8\"))`, then `savedFrom` — throwing with the exact messages.",
     "`todos.push(...saved.todos); nextId = saved.nextId;`",
     "Every refused file must still be in `FILE` afterwards, exactly as it was."],
)


_TODO_MODULES.append(_pmod(
    key="todo-persist", number=19, phase="real",
    title="Persistence on disk",
    what="read the file on boot, write it on change, and validate what you load",
    goal="Make the store survive a restart: write every change to a file before answering, load it at boot, and refuse to start from a file that fails the API's own rules.",
    why=_M19_WHY,
    est_minutes=60,
    builds_on=["todo-page"],
    concepts=["writeFileSync", "readFileSync", "existsSync", "write-through",
              "save before answering", "the counter is state", "untrusted files",
              "invariants across records", "refusing to boot"],
    deliverable="A server whose todos — and id counter — survive a restart, and "
                "which refuses to start from a file it cannot trust rather than "
                "overwrite it.",
    objectives=[
        "Write a whole store to a file as JSON and read it back, and say why `toString` will not do",
        "Save after every change, in the three functions that change the store, before the change is answered",
        "Load the store at boot, treating a missing file as a first start",
        "Explain why the id counter must be saved rather than worked out from the todos",
        "Check a loaded file with the same rules as a request, plus the rules that relate records to each other",
        "Refuse to boot from a bad file, and explain why starting empty would destroy data",
    ],
    endpoints=[
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M19_BRIEF,
    syntax=_M19_SYNTAX,
    steps=[_M19_S1, _M19_S2, _M19_S3, _M19_S4],
    final_build=_M19_FINAL,
    acceptance=[
        "Create two todos, stop the server with Ctrl-C, start it again: `curl -s localhost:3000/todos` still lists both.",
        "Delete the newest todo, restart, and create another: it gets a new id — never the deleted one's.",
        "`cat todos.json` after any change shows exactly what `GET /todos` does, plus `nextId`.",
        "A fresh directory with no `todos.json` starts with an empty list, and has no file until the first change.",
        "Replace `todos.json` with `not json` and start the server: it refuses, with a message naming the file — and the file is unchanged.",
        "A file with an empty title, a duplicate id, or an id at or above `nextId` is refused the same way.",
        "A refused create, a read, or a delete of a missing todo leaves `todos.json` untouched.",
    ],
    manual_test="""
Start clean, make some todos, and look at the file after each change:

```bash
rm -f todos.json
node server.ts &
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
curl -s -X POST localhost:3000/todos -d '{"title":"Write tests"}'
curl -s -X POST localhost:3000/todos -d '{"title":"Ship it"}'
cat todos.json
curl -s -X DELETE localhost:3000/todos/3
cat todos.json          # nextId is still 4
```

Now the point of the module. Stop it and start it again:

```bash
kill %1
node server.ts &
curl -s localhost:3000/todos                                    # both still there
curl -s -X POST localhost:3000/todos -d '{"title":"Again"}'     # id 4 — not 3
```

Then break the file, three ways, and watch it refuse:

```bash
kill %1
cp todos.json good.json

echo 'not json' > todos.json && node server.ts          # refuses: not JSON
sed 's/"Buy milk"/""/' good.json > todos.json && node server.ts   # refuses: empty title
sed 's/"nextId":5/"nextId":2/' good.json > todos.json && node server.ts   # refuses: ids above nextId

cp good.json todos.json && node server.ts &             # and back to normal
```

Each time, `cat todos.json` afterwards: the broken file is still there to fix.
Nothing was overwritten.
""",
    reference="""// server.ts — module 19
//
// The store survives a restart. Every change is written to todos.json before it
// is answered, and the file is read back once, at boot. The file holds the id
// counter as well as the todos — work it out from them instead and a restart
// reissues a deleted id. And the file is INPUT: it is checked with the same
// rules as a request, and a file that fails stops the server from starting
// rather than being overwritten by the first change.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { readFileSync, writeFileSync, existsSync } from "node:fs";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
let nextId = 1;

// ---- persistence: saving ---------------------------------------------------
// Write-through: the three functions that change the store each end with
// saveStore(), so memory and disk never disagree for longer than one call — and
// a route written next year is saved without anyone remembering to. The whole
// store every time: well under a millisecond at this size, and impossible to
// get subtly wrong.
const DATA_FILE = "todos.json";

function saveStore(): void {
  writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));
}

// addTodo's `title: string` has been a promise since module 2. As of this
// module, every caller can actually keep it.
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

// `sort` rearranges the array it is called on — unlike filter and map — and
// when no filter was asked for, `items` IS the store. So every sort works on a
// copy (`slice()`). `oldest` needs no sort at all: the store is kept in id
// order (push appends, splice removes, updateTodo replaces in place), and that
// invariant is what a plain GET /todos relies on.
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

// Filter, then sort, then cut — the only order in which all three are right.
// `total` counts what MATCHED, before the page is cut: the one number a client
// cannot work out for itself.
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
// in the file — the one that reads todos.json uses it too.
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

// ---- persistence: loading --------------------------------------------------
// The file is input. Whoever wrote it — this server, an older one, an editor, a
// write cut off halfway — it is checked with the request rules (objectFrom,
// module 14's titleFrom), so the store can never hold a todo no request could
// have created.
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

// Two rules a request never needed, because they relate todos to each other:
// ids strictly increasing (unique, and the id order module 18's `oldest`
// relies on), and all below nextId (or the counter would reissue one).
// Array.isArray types the array `any[]`; `unknown[]` puts every element back
// behind todoFrom.
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

// No file is a first start: an empty store. A file that fails is somebody's
// data — so this THROWS, and nothing catches it: the server refuses to start,
// leaving the file for a person to fix. Logging and starting empty would let the
// first saveStore() overwrite the only copy. The counter is restored from the
// file, never worked out from the todos: that would reissue a deleted id.
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

async function route(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = new URL(req.url ?? "/", "http://localhost");
  const id = todoId(url.pathname);

  // Routed on the PATHNAME — `req.url` includes the query string, which is why
  // every route since module 7 has compared `url.pathname`. This line did not
  // change for the envelope: listTodos now returns a Page, and send takes any
  // object. A breaking change for every client; one type on the server.
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
    // addTodo saves before it returns, so this 201 means "on disk".
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
// status cannot be replaced — only the response ended. (A disk that fails inside
// saveStore lands here too: a 500, and the todo is not reported as saved.)
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

// Load, THEN listen — or for a moment the server would answer from an empty
// store. If loadStore throws, nothing catches it and the process stops here,
// with the message, before answering anything.
loadStore();
const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Make the write atomic: write to `todos.json.tmp`, then rename it over `todos.json` (`renameSync` in `node:fs`). A rename replaces the file in one step, so a crash mid-write leaves the old file whole rather than half a new one. Why does the order of the two calls matter?",
        "Pretty-print the file with `JSON.stringify(data, null, 2)`, so a person can read and fix it. What does that cost, and does anything in `loadStore` need to change?",
        "Switch to `writeFile` from `node:fs/promises` and `await` it. What changes in `addTodo`'s signature — and in every caller? Is \"save, then answer\" still true?",
        "Add a `version` field to the file. Write `loadStore` so it can read version 1 (today's) and version 2 (with, say, a `createdAt` on each todo), upgrading the old one as it loads.",
        "Put the file somewhere configurable — `process.env.DATA_FILE ?? \"todos.json\"` — and run two servers side by side on different files. Then run two on the *same* file and describe exactly how they destroy each other's data.",
    ],
    glossary=[
        _pgloss("persistence", "Keeping data beyond the life of the process — here, in `todos.json`."),
        _pgloss("writeFileSync", "Replace a file's contents with a string, creating it if needed, and return once it is written."),
        _pgloss("existsSync", "Whether a file exists. How a server tells a first start from a restart."),
        _pgloss("write-through", "Saving on every change, so memory and disk never disagree for longer than one operation."),
        _pgloss("durability", "The promise that an answered change survives a crash — why the store saves before the route answers."),
        _pgloss("counter as state", "`nextId` is part of what must be saved; working it out from the surviving todos reissues deleted ids."),
        _pgloss("cross-record invariant", "A rule about how records relate — unique, ascending ids below `nextId` — which no single todo can check alone."),
        _pgloss("fail closed", "Refusing to run when something is wrong, rather than carrying on with a guess. A corrupt file stops the boot."),
    ],
    cheatsheet="""
```ts
import { readFileSync, writeFileSync, existsSync } from "node:fs";

const DATA_FILE = "todos.json";

// every change: the whole store, counter included
function saveStore(): void {
  writeFileSync(DATA_FILE, JSON.stringify({ nextId: nextId, todos: todos }));
}
// …called at the END of addTodo, updateTodo and deleteTodo — after the change

// boot: once, before listen
function loadStore(): void {
  if (!existsSync(DATA_FILE)) {
    return;                                   // first start — empty store
  }
  const parsed = parseJson(readFileSync(DATA_FILE, "utf8"));
  if (!parsed.ok) {
    throw new Error(DATA_FILE + " is not JSON");            // refuse to start
  }
  const saved = savedFrom(parsed.data);       // request rules + id rules
  if (saved === undefined) {
    throw new Error(DATA_FILE + " is not a saved todo list");
  }
  todos.push(...saved.todos);
  nextId = saved.nextId;                      // never worked out from the todos
}

loadStore();
const server = createServer(handler);
```

| The file | Boot |
|---|---|
| missing | empty store — first start |
| `{"nextId":4,"todos":[…ids 1, 2…]}` | loads; next id is **4** |
| `not json` · `[]` · `{"todos":[]}` | **refused** |
| a todo with `"title":""` or `"title":5` | **refused** — request rules apply |
| duplicate or out-of-order ids | **refused** |
| an id ≥ `nextId` | **refused** |

| `nextId` worked out as | After deleting id 3 and restarting |
|---|---|
| saved in the file | 4 ✓ |
| `todos.length + 1` · largest id + 1 | 3 — reissued |
| not restored | 1 — duplicated |
""",
    self_check=[
        "Can you say why `saved.toString()` writes a useless file, and what writes a useful one?",
        "Can you say which three functions save, why they and not the routes, and why after the change?",
        "Can you explain why `nextId` is saved — with an example of an id a derivation would reissue?",
        "Can you tell a missing file from a bad one, and say what the server does with each?",
        "Can you name the two checks a file needs that a request never did?",
        "Can you explain, step by step, how \"log it and start empty\" destroys a user's data?",
    ],
    review=[
        _pq("Where should `saveStore()` be called?",
            ["At the end of `addTodo`, `updateTodo` and `deleteTodo` — the only places the store changes",
             "In every route",
             "Once, when the server shuts down",
             "On a timer every few seconds"],
            0,
            "Every change saved, by construction. A shutdown hook never runs on a "
            "crash; a timer loses whatever changed since it last fired."),
        _pq("Todos 1, 2 and 3 exist; 3 is deleted; the server restarts. Why must the next todo not be 3?",
            ["A client may still hold id 3 — a URL, a bookmark — and it would now name a different todo",
             "Because 3 is odd",
             "Because the file is sorted",
             "It may be 3; ids are only unique while running"],
            0,
            "Ids are a promise to clients, not a detail of one process. The saved "
            "counter keeps it across restarts."),
        _pq("`todos.json` is missing. What does `loadStore` do?",
            ["Nothing — it is a first start, and the store is empty",
             "Throws",
             "Writes an empty file",
             "Retries until it appears"],
            0,
            "Missing and malformed are different states with different answers."),
        _pq("A saved todo has `\"title\":\"\"`. Why refuse the whole file rather than skip that todo?",
            ["Skipping loses data silently and the next save makes the loss permanent; refusing keeps everything for a person to fix",
             "Because one bad todo means all are bad",
             "Because `titleFrom` throws",
             "It should skip it"],
            0,
            "Any automatic fix is a guess about somebody's data. The safe move is "
            "to change nothing and say so."),
        _pq("Why is `obj.todos` assigned to `unknown[]` after `Array.isArray`?",
            ["`Array.isArray` types it `any[]`, which would let every element through unchecked",
             "Because arrays cannot be iterated otherwise",
             "For speed",
             "Because `Todo[]` is not allowed"],
            0,
            "Proving it is an array says nothing about what is in it."),
        _pq("Why does the server load *before* it listens?",
            ["Otherwise it answers from an empty store until loading finishes — and a create in that window could overwrite the file",
             "Because `listen` deletes the file",
             "It does not matter",
             "Because `loadStore` is async"],
            0,
            "Boot is: know what you have, then start taking questions."),
    ],
    milestone="Your todos are still there tomorrow. Every change is on disk before "
              "it is answered, a restart picks up exactly where the last run left "
              "off — counter and all — and a file the server cannot trust stops it "
              "cold instead of being quietly overwritten.",
))
