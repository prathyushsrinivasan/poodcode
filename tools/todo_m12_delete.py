# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 12 — DELETE /todos/:id, and 204.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10 and 11's program pieces.
#
# CLOSES PHASE 3. Every verb on the resource now works, and the phase's outcome
# line — "create, read, update and delete a todo over HTTP" — is true.
#
# PAYS OFF MODULE 2. Module 2 argued for an id counter over `todos.length + 1`
# and demonstrated the collision with a `.shift()`, because there was no delete
# yet. This is the delete that would have caused it, and step 4 grades the
# collision over real HTTP: three creates, delete the middle one, create again,
# and a `length + 1` store hands out id 3 twice.
#
# THE GRADABLE BUGS are all silent data loss, which is exactly why they are
# worth grading: `findIndex` answers -1 rather than undefined, and
# `splice(-1, 1)` removes the LAST element — so a delete of a missing todo
# quietly deletes somebody else's and answers 204. `splice(i)` with no count
# deletes everything from i onward.
#
# ONE UNGRADABLE LESSON, taught in prose: sending a body with a 204. Node's
# `ServerResponse` discards a body on a 204, so `send(res, 204, {…})` and the
# correct empty response print the same `204` line through the replayer — the
# same family as module 8's accumulation bugs (see PROJECTS_ROADMAP.md, trap 3).
# The manual test shows the difference with `curl -i`, where the stray
# `Content-Type` header gives it away.
# ---------------------------------------------------------------------------

_M12_DELETE = """function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  return true;
}
"""

_M12_SENDEMPTY = """function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
}
"""

_M12_DELETE_ROUTE = """  if (req.method === "DELETE" && id !== undefined) {
    const removed = deleteTodo(id);
    if (!removed) {
      send(res, 404, { error: "not_found" });
      return;
    }
    sendEmpty(res, 204);
    return;
  }"""

_M12_HANDLER = _M11_HANDLER.replace(
    """    send(res, 200, updated);
    return;
  }

  send(res, 404, { error: "not_found" });
}""",
    """    send(res, 200, updated);
    return;
  }

""" + _M12_DELETE_ROUTE + """

  send(res, 404, { error: "not_found" });
}""")
assert _M12_HANDLER != _M11_HANDLER, "module 12: DELETE route was not inserted"


def _m12(handler=_M12_HANDLER, delete=_M12_DELETE, store=_M10_STORE,
         sendempty=_M12_SENDEMPTY):
    """A module-12 server program: module 11's, plus delete and an empty send."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (store, _M10_SEND, _M10_READBODY,
                                _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                _M11_CHANGES, _M11_UPDATE,
                                delete, sendempty, handler)))


_M12_FULL = _m12()

# --- Steps 1-2's plain program: deleting from a store of three --------------
_M12_PLAIN_STORE = """type Todo = {
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

_M12_PLAIN_PRINTS = """
addTodo("Buy milk");
addTodo("Write tests");
addTodo("Ship it");

console.log(deleteTodo(2));
console.log(JSON.stringify(todos));
console.log(deleteTodo(2));
console.log(deleteTodo(99));
console.log(JSON.stringify(todos));
console.log(JSON.stringify(addTodo("Again")));
"""

_T1 = '{"id":1,"title":"Buy milk","done":false}'
_T3 = '{"id":3,"title":"Ship it","done":false}'
_M12_PLAIN_OUT = "\n".join([
    "true",
    "[" + _T1 + "," + _T3 + "]",
    "false",
    "false",
    "[" + _T1 + "," + _T3 + "]",
    '{"id":4,"title":"Again","done":false}',
])


def _m12_plain(delete=_M12_DELETE):
    return _plain(_M12_PLAIN_STORE + "\n" + delete.rstrip("\n") + "\n" + _M12_PLAIN_PRINTS)


_POST_C = 'POST /todos {"title":"Ship it"}'
_POST_D = 'POST /todos {"title":"Again"}'
_TODO_C = '{"id":3,"title":"Ship it","done":false}'
_TODO_D4 = '{"id":4,"title":"Again","done":false}'

_M12_WHY = (
    "A todo can be created, fetched and changed, and never removed. Finished "
    "todos pile up forever, and a typo'd one can only be renamed into something "
    "less wrong. The resource is one verb short of complete — and that verb is "
    "the one module 2 was worried about, because a delete is the first thing "
    "that can make two todos want the same id."
)

_M12_BRIEF = """
### The whole module in one line

Remove a todo by its id, answer `204` with no body, and `404` if it was never
there — or is already gone.

### Three new things, one per step

```ts
const i = todos.findIndex((t) => t.id === id);   // where is the todo with this id?  (-1: nowhere)
todos.splice(i, 1);                              // remove one element, at that position
sendEmpty(res, 204);                             // done, and there is nothing to say
```

### Why `findIndex` and not module 11's `indexOf`

Module 11 had the todo in hand — `findTodo` had just returned it — and asked
*where is this object?* A delete has only a number from the URL. Its question is
*where is the todo **whose id is 7**?*, which is a condition rather than an
object, and `findIndex` is `find` that answers with a position instead of the
thing.

### The most dangerous number in this module is `-1`

`findIndex` answers `-1` when nothing matches — not `undefined`. And
`splice(-1, 1)` does not fail; it counts from the **end** and removes the last
todo. So a delete that forgets to check for `-1` answers `DELETE /todos/99` with
a cheerful `204`, and somebody else's todo is gone. Step 1 grades exactly that.

### 204: success with nothing to say

After a delete there is no todo to send back. `204 No Content` says *it worked*
and promises an empty body — so for the first time since module 5, a response
leaves without going through `send`.

### Module 2's collision, finally

```
POST ×3              →  ids 1, 2, 3
DELETE /todos/2
POST                 →  todos.length + 1 is 3.  Todo 3 already exists.
```

Module 2 chose a counter over `todos.length + 1` and could only demonstrate why
with a `.shift()`. This is the delete it was worried about, and step 4 runs the
collision over HTTP.
"""

_M12_SYNTAX = [
    _syn(
        "const i = todos.findIndex((t) => t.id === id);",
        "The position of the first element for which the arrow function returns "
        "`true` — `find`, answering *where* rather than *what*.",
        """
const todos = [{ id: 1 }, { id: 3 }, { id: 7 }];
todos.findIndex((t) => t.id === 3);    // 1
todos.findIndex((t) => t.id === 99);   // -1
""",
        "It answers **`-1`**, not `undefined`, when nothing matches — and `-1` is a "
        "perfectly good number to hand to the next line. Check for it by name: "
        "`if (i === -1)`.",
    ),
    _syn(
        "todos.splice(i, 1);",
        "Remove elements from an array in place: start at position `i`, remove "
        "`1`. Everything after it shifts down one.",
        """
const xs = ["a", "b", "c", "d"];
xs.splice(1, 1);     // xs is now ["a", "c", "d"]
""",
        "Both arguments matter. `splice(i)` with no count removes **everything** "
        "from `i` to the end. `splice(-1, 1)` counts from the end and removes the "
        "last element — which is what a missing `-1` check does to your store.",
    ),
    _syn(
        "function sendEmpty(res: ServerResponse, status: number): void { … }",
        "A response with a status and no body — and so no `Content-Type`, since "
        "there is no content to have a type.",
        """
function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
}
""",
        "Module 5's rule was that every response leaves through a helper. It "
        "still does — this is the second helper, for the one status that must "
        "not have a body.",
    ),
    _syn(
        "sendEmpty(res, 204);",
        "**204 No Content** — it worked, and there is nothing to send back. The "
        "status a successful delete answers with.",
        "",
        "Node throws away a body sent with a 204 rather than erroring, so "
        "`send(res, 204, {…})` looks fine in a test and ships a `Content-Type` "
        "header promising JSON that never arrives. Use `sendEmpty`.",
    ),
    _syn(
        "if (!removed) { … }",
        "`!` flips a boolean. Read `!removed` as \"not removed\" — true exactly "
        "when the delete found nothing.",
        "",
        "",
        recap=True,
    ),
    _syn(
        "const todos: Todo[] = [];",
        "Module 2's store. `const` binds the array, not its contents — `splice` "
        "changes the contents and the binding never moves.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — finding a position by id.
# ---------------------------------------------------------------------------

_M12_S1 = _pstep(
    "findindex", "Where is the todo with this id?",
    "`findIndex`, and the `-1` that must never reach the next line.",
    """
To remove an element from an array you need its **position**. You have an id.

Module 11 found a position with `indexOf`, but it had the todo object itself in
hand. A delete does not: the URL gives you `7` and nothing else. The question is
no longer *where is this object?* but *where is the todo whose id is 7?* — a
condition, not an object.

```ts
const i = todos.findIndex((t) => t.id === id);
```

`findIndex` is module 3's `find` with a different answer. Same arrow function,
same walk down the array, same stop at the first match — but instead of the todo
it hands back **where** the todo is.

| | Gives you | When nothing matches |
|---|---|---|
| `find` (module 3) | the todo | `undefined` |
| `indexOf` (module 11) | a position, for an object you hold | `-1` |
| `findIndex` | a position, for a condition | **`-1`** |

### `-1` is not `undefined`, and that is the danger

`find` returned `Todo | undefined`, and the compiler made you handle the
`undefined` before you could use the result. `findIndex` returns a plain
`number`, and `-1` *is* a number. The compiler has no idea it means "not found",
so it will happily let you hand it to the next line.

And the next line is `splice`, which reads a negative position as "count from the
end". `splice(-1, 1)` removes the **last** todo. So this:

```ts
const i = todos.findIndex((t) => t.id === id);
todos.splice(i, 1);
return true;
```

answers `DELETE /todos/99` — a todo that never existed — by deleting whichever
todo happens to be last, and reporting success. No error, no crash, and a user
somewhere is missing their todo.

The check has to be written by hand, and by name:

```ts
if (i === -1) {
  return false;
}
```
""",
    """
With three todos in the store, your `deleteTodo` reports:

```
deleteTodo(2)     true      [1, 3] remain
deleteTodo(2)     false     already gone
deleteTodo(99)    false     never existed — and [1, 3] still remain
```

The third line is the step. If `deleteTodo(99)` says `true`, or todo 3 has
vanished, the `-1` got through.
""",
    pitfalls=[
        "Forgetting the `-1` check. `splice(-1, 1)` removes the **last** todo, so deleting a todo that does not exist quietly deletes someone else's and answers 204.",
        "`if (i === undefined)`. `findIndex` never answers `undefined`; TypeScript refuses the comparison because a `number` cannot be `undefined`. The not-found value is `-1`.",
        "`if (!i)`. Position 0 is falsy, so this treats the **first** todo as missing and can never delete it.",
        "`if (i < 0)` is correct but hides the intent. `i === -1` says exactly what `findIndex` promises; either works.",
        "Using `findTodo` and then `indexOf` to delete. It works, and it walks the array twice to answer one question — `findIndex` exists for exactly this.",
    ],
    warmup=[
        _pq("`[{ id: 1 }, { id: 3 }].findIndex((t) => t.id === 7)` — what is it?",
            ["`-1`",
             "`undefined`",
             "`null`",
             "It throws"],
            0,
            "Positions are numbers, and `-1` is the number no array position can "
            "be. Which is exactly why it is dangerous when it is not checked."),
        _pq("What does `todos.splice(-1, 1)` do?",
            ["Removes the last element — a negative position counts from the end",
             "Nothing, because -1 is not a position",
             "Throws a RangeError",
             "Removes the first element"],
            0,
            "Which means an unchecked `-1` from `findIndex` does not fail. It "
            "deletes the wrong todo."),
    ],
    exercises=[
        _pex("todo-m12-find-1", "Where is it?",
             "`deleteTodo` needs the position of the todo with this id. Find it.",
             _m12_plain(),
             "  const i = todos.findIndex((t) => t.id === id);",
             [("", _M12_PLAIN_OUT)],
             ["You have an id, not the object — so `indexOf` cannot help.",
              "It is `find` that answers with a position. Same arrow function as `findTodo`.",
              "Store it in `i`; the next line checks it.",
              "`const i = todos.findIndex((t) => t.id === id);`"]),
        _pfix("todo-m12-find-fix1", "Deleting todo 99 deleted todo 3",
              "`deleteTodo(99)` — for a todo nobody ever created — answers "
              "`true`. And afterwards, todo 3 is gone.\n\n"
              "Nothing threw. Nothing warned.",
              _m12_plain("""function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  todos.splice(i, 1);
  return true;
}
"""),
              _m12_plain(),
              [("", _M12_PLAIN_OUT)],
              ["What does `findIndex` answer when no todo has id 99?",
               "And what does `splice` do with that number?",
               "`-1` counts from the end. It has to be stopped before it reaches `splice`.",
               "`if (i === -1) { return false; }` between the two lines."],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does the compiler not stop you passing `findIndex`'s not-found value to `splice`?",
            ["It is `-1`, an ordinary `number` — unlike `find`'s `undefined`, nothing in the type says \"missing\"",
             "Because `splice` accepts `undefined`",
             "It does stop you, under `noUncheckedIndexedAccess`",
             "Because `-1` is converted to `0`"],
            0,
            "A sentinel value hides the failure inside a value of the right type. "
            "Module 10 made the same argument for `parseId` returning `undefined` "
            "rather than `0`."),
        _pq("Why is `findIndex` the right call here, when module 11 used `indexOf`?",
            ["A delete has only an id — a condition — not the todo object `indexOf` would need",
             "`indexOf` cannot find objects",
             "`findIndex` is faster",
             "`indexOf` returns `undefined` when nothing matches"],
            0,
            "`indexOf(x)`: where is this exact thing? `findIndex(fn)`: where is the "
            "first thing this is true of?"),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — removing it.
# ---------------------------------------------------------------------------

_M12_S2 = _pstep(
    "splice", "Removing it",
    "`splice(i, 1)`, what shifts, and why the counter is the reason ids survive it.",
    """
```ts
todos.splice(i, 1);
```

`splice` edits the array **in place**: start at position `i`, remove `1`
element. Everything after it moves down one position.

```
before   [ {id:1}, {id:2}, {id:3} ]     positions 0 1 2
splice(1, 1)
after    [ {id:1}, {id:3} ]             positions 0 1
```

Todo 3 was at position 2 and is now at position 1. **Its id did not change** —
and that is the whole reason ids and positions are different things. Module 11
found positions with `indexOf` rather than `id - 1` for exactly this reason:
after one delete, they stop lining up.

### Both arguments matter

```ts
todos.splice(i, 1);    // remove one, at i
todos.splice(i);       // remove EVERYTHING from i to the end
```

Leave off the count and `splice` assumes you mean "the rest of the array". Delete
todo 2 of three that way, and todo 3 goes with it.

### The whole function

```ts
function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);
  return true;
}
```

It answers `true` if it removed something and `false` if there was nothing to
remove. That boolean is all the route needs to choose between 204 and 404.

### The id that is never handed out again

After deleting todo 2, the next `addTodo` gives id **4**, not 2 and not 3.
`nextId` only ever goes up, so no id is ever reused — which means a client that
remembers `/todos/2` gets a 404 forever, rather than some other todo that
happens to have inherited the number. That is module 2's counter doing what it
was for.
""",
    """
```
deleteTodo(2)                 true
todos                         [1, 3]      ← 3 kept its id, moved position
addTodo("Again")              id 4        ← never 2, never 3
```

If the list after the first delete is just `[1]`, the count is missing from
`splice`.
""",
    pitfalls=[
        "`splice(i)` with no count. Removes everything from `i` to the end — one delete, and every todo after it is gone too.",
        "Confusing `splice` with `slice`. `slice` copies part of an array and changes nothing; `splice` removes from the array itself. Module 18 is `slice`'s.",
        "Deleting by position: `todos.splice(id - 1, 1)`. It works until the first delete, then removes the wrong todo every time after.",
        "Reusing ids after a delete. A client holding `/todos/2` must get a 404, not a stranger's todo — which is why the counter never goes back.",
        "Building a new array without the todo and forgetting to store it. `splice` edits in place precisely so there is nothing to forget.",
    ],
    warmup=[
        _pq("`const xs = [\"a\", \"b\", \"c\", \"d\"]; xs.splice(1);` — what is `xs` now?",
            ["`[\"a\"]` — with no count, `splice` removes everything from position 1 on",
             "`[\"a\", \"c\", \"d\"]`",
             "`[\"b\", \"c\", \"d\"]`",
             "Unchanged — `splice` returns a copy"],
            0,
            "The count is not optional in spirit. Always say how many."),
    ],
    exercises=[
        _pex("todo-m12-splice-1", "Remove exactly one",
             "The position is found and checked. Remove the todo at it — that one, "
             "and nothing else.",
             _m12_plain(),
             "  todos.splice(i, 1);",
             [("", _M12_PLAIN_OUT)],
             ["The array method that removes elements in place.",
              "It takes a starting position and how many to remove.",
              "`todos.splice(i, 1);`"]),
        _pfix("todo-m12-splice-fix1", "One delete, two todos gone",
              "Deleting todo 2 from a store of three leaves only todo 1. Todo 3 "
              "was never asked about, and it is gone too.",
              _m12_plain(_M12_DELETE.replace("todos.splice(i, 1);", "todos.splice(i);")),
              _m12_plain(),
              [("", _M12_PLAIN_OUT)],
              ["What does `splice` do when you tell it where to start but not how many?",
               "With no count it removes to the end of the array.",
               "`todos.splice(i, 1);`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Todo 3 sits at position 2. Todo 2 is deleted. Where is todo 3, and what is its id?",
            ["Position 1, id 3 — positions shift, ids never do",
             "Position 2, id 3",
             "Position 1, id 2",
             "Position 2, id 2"],
            0,
            "This is why modules 11 and 12 find positions by looking, never by "
            "arithmetic on the id."),
        _pq("After deleting todo 2 of three, `addTodo` hands out which id?",
            ["4 — the counter only goes up, so no id is ever reused",
             "2 — the first free id",
             "3 — `todos.length + 1`",
             "It depends on which todo was deleted"],
            0,
            "An id is a promise that an address means one todo. Reusing it would "
            "break that promise for anyone still holding the old address."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — 204.
# ---------------------------------------------------------------------------

_M12_S3 = _pstep(
    "nocontent", "204: success, and nothing to say",
    "The status that promises an empty body — and the second helper responses leave through.",
    """
Every successful response so far has carried the resource: the todo you created,
fetched or changed. After a delete there is no resource. What should the body be?

**Nothing.** `204 No Content` means *it worked, and there is nothing to send
back* — and it is a promise, not a suggestion: a 204 has no body at all.

```ts
function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
}
```

No `Content-Type` either. That header describes the body, and there is no body
to describe. This is the first response since module 5 that does not go through
`send`, and module 5's rule still holds — every response leaves through a helper
— there are just two helpers now, one for each kind of response.

### The mistake no test here can catch

```ts
send(res, 204, { deleted: true });
```

Node's HTTP server knows 204 has no body, so it quietly **throws the body away**
instead of erroring. Through the replayer, that line prints exactly `204` — the
same as the correct one — so no graded exercise in this module can tell them
apart. (Module 8 hit the same wall with bugs that only a 64 KB body can expose.)

`curl -i` can tell them apart:

```
$ curl -s -i -X DELETE localhost:3000/todos/1
HTTP/1.1 204 No Content
Content-Type: application/json      ← promising JSON that never arrives
```

A client that trusts that header and tries to parse the empty body as JSON will
fail. Use `sendEmpty`, and check with `-i`.

### And the second delete

```
DELETE /todos/1   →  204
DELETE /todos/1   →  404
```

The second one is correct. The todo is not there, so there is nothing at that
address — module 10's definition. Some people expect a repeated delete to answer
204 again, since the end state (no todo 1) is the same; the stretch list has the
argument. This project answers what is true *now*.
""",
    """
```bash
$ curl -s -i -X DELETE localhost:3000/todos/1
HTTP/1.1 204 No Content

$ curl -s -i -X DELETE localhost:3000/todos/1
HTTP/1.1 404 Not Found
Content-Type: application/json

{"error":"not_found"}
```

No `Content-Type` on the 204. If yours has one, it went through `send`.
""",
    pitfalls=[
        "`send(res, 204, …)`. Node drops the body silently, so it passes every test here — and ships a `Content-Type: application/json` header promising a body that is not there. Only `curl -i` shows it.",
        "Answering `200` with `{\"deleted\":true}`. Not wrong, but it invents a body shape the rest of the API does not have, and every client has to learn it. 204 says the same thing with nothing.",
        "Sending the deleted todo back. Some APIs do; this one does not, because a response describing a resource that no longer exists invites a client to keep using it.",
        "Answering 204 for a todo that was never there. The delete removed nothing — that is a 404.",
        "`res.end()` without `res.writeHead(204)`. The status defaults to 200, so the client is told \"OK, and here is nothing\", which is a different claim.",
    ],
    warmup=[
        _pq("What should the body of a successful `DELETE /todos/1` be?",
            ["Nothing — it is a 204, which promises an empty body",
             "The deleted todo",
             "`{\"deleted\":true}`",
             "`[]`"],
            0,
            "There is no resource left to describe. 204 is the status that says "
            "so."),
    ],
    exercises=[
        _pex("todo-m12-nocontent-1", "An empty response",
             "Write the helper's body: a status line with no body and no headers.",
             _M12_FULL,
             """  res.writeHead(status);
  res.end();""",
             [("\n".join([_POST_A, "DELETE /todos/1", "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "204", "200 []"]))],
             ["Two lines. The first sets the status; the second finishes the response.",
              "No headers object — there is no body, so there is no content type.",
              "`res.end()` with nothing in the parentheses.",
              "`res.writeHead(status);` then `res.end();`"]),
        _pfix("todo-m12-nocontent-fix1", "A 204 for nothing",
              "`DELETE /todos/1` works. So does `DELETE /todos/1` a second time — "
              "it answers `204` again, for a todo that is already gone. So does "
              "`DELETE /todos/99`.",
              _m12(_M12_HANDLER.replace(
                  """    const removed = deleteTodo(id);
    if (!removed) {
      send(res, 404, { error: "not_found" });
      return;
    }
    sendEmpty(res, 204);""",
                  """    deleteTodo(id);
    sendEmpty(res, 204);""")),
              _M12_FULL,
              [("\n".join([_POST_A, "DELETE /todos/1", "DELETE /todos/1", "DELETE /todos/99"]),
                "\n".join(["201 " + _TODO_A, "204", _NF, _NF]))],
              ["`deleteTodo` already knows whether it removed anything. What does it return?",
               "The route throws that answer away.",
               "Keep it, and answer 404 when it is `false`.",
               "`const removed = deleteTodo(id); if (!removed) { send(res, 404, …); return; }`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why can no graded exercise here tell `send(res, 204, {...})` from `sendEmpty(res, 204)`?",
            ["Node discards a body sent with a 204, so both print exactly `204` through the replayer",
             "Because the replayer ignores 2xx bodies",
             "Because they really are identical",
             "Because `send` checks for 204"],
            0,
            "The difference is a header promising content that never arrives, and "
            "the replayer prints no headers. `curl -i` is the test for this one."),
        _pq("`DELETE /todos/1` twice. What does the second one answer, and why?",
            ["404 — there is nothing at that address any more",
             "204 — the end state is the same",
             "500 — the todo was already deleted",
             "409 Conflict"],
            0,
            "Both answers exist in real APIs. This one reports what is true when "
            "the request arrives."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the route, and module 2's collision.
# ---------------------------------------------------------------------------

_M12_S4 = _pstep(
    "route", "The route — and the collision module 2 predicted",
    "DELETE on the same `id`, the resource complete, and why `length + 1` was never an id.",
    """
```ts
if (req.method === "DELETE" && id !== undefined) {
  const removed = deleteTodo(id);
  if (!removed) {
    send(res, 404, { error: "not_found" });
    return;
  }
  sendEmpty(res, 204);
  return;
}
```

Module 10's condition, a fourth verb. No body to read — a delete says everything
it needs to in its URL — so it is the shortest route in the handler.

### The resource is complete

| Verb | Path | Answer | Module |
|---|---|---|---|
| `GET` | `/todos` | 200, the list | 7 |
| `POST` | `/todos` | 201, the new todo | 9 |
| `GET` | `/todos/:id` | 200 · 404 | 10 |
| `PATCH` | `/todos/:id` | 200 · 404 | 11 |
| `DELETE` | `/todos/:id` | 204 · 404 | **12** |

That is phase 3's promise kept: create, read, update and delete, over HTTP, each
with its own status code and its own way to fail.

### The collision module 2 predicted

Module 2 had a choice for ids: a counter that only goes up, or `todos.length + 1`.
It chose the counter and showed why with a `.shift()`, because there was no delete
yet. There is now. Here is the store module 2 turned down, meeting a delete:

```
POST "Buy milk"        length 0 → id 1
POST "Write tests"     length 1 → id 2
POST "Ship it"         length 2 → id 3
DELETE /todos/2        length is now 2
POST "Again"           length 2 → id 3        ← "Ship it" is already id 3
```

Two todos with id 3. `GET /todos/3` finds whichever comes first; `DELETE /todos/3`
removes one of them, and the client cannot say which. Every address in the API
has stopped meaning one thing.

The counter never has this problem, because it never looks at the list. It only
goes up. That was a decision taken in module 2, before there was a server, for a
reason that could only be *shown* ten modules later — and the last exercise in
this step shows it.
""",
    """
```bash
$ for t in 'Buy milk' 'Write tests' 'Ship it'; do
>   curl -s -X POST localhost:3000/todos -d "{\\"title\\":\\"$t\\"}"; echo
> done
$ curl -s -i -X DELETE localhost:3000/todos/2         # 204
$ curl -s -X POST localhost:3000/todos -d '{"title":"Again"}'
{"id":4,"title":"Again","done":false}
```

Id 4. Not 2, not 3. The address `/todos/2` is a 404 forever, and `/todos/3` still
means "Ship it".
""",
    pitfalls=[
        "Reading the body on a DELETE. It has none that matters — the URL says everything, and a route that waits for a body is a route that can hang.",
        "Deleting before checking the result. `deleteTodo` answers whether it removed anything; a route that ignores that answers 204 for todos that were never there.",
        "Assuming ids are positions anywhere in the handler. After the first delete, `todos[id - 1]` is a different todo, or nothing.",
        "An id scheme based on the list — `todos.length + 1`, or the highest id plus one. The first can hand out an id that is already in use after a delete; the second can reuse the id of a todo deleted from the end.",
        "Putting the DELETE route above the 404 is necessary; putting it above the other `:id` routes is harmless. They cannot overlap, because each matches a different verb.",
    ],
    warmup=[
        _pq("A store makes ids with `todos.length + 1`. Three creates, delete id 2, "
            "one more create. What id does it get?",
            ["3 — and \"Ship it\" already has id 3, so two todos now share it",
             "4",
             "2, reusing the deleted one",
             "1"],
            0,
            "The list got shorter, so `length + 1` went backwards. Module 2 chose a "
            "counter to make this impossible, and this is the request sequence that "
            "proves it."),
    ],
    exercises=[
        _pex("todo-m12-route-1", "The delete route",
             "Add the route. Delete the todo; if nothing was removed, answer 404; "
             "otherwise answer 204 with no body.",
             _M12_FULL,
             _M12_DELETE_ROUTE,
             [("\n".join([_POST_A, _POST_B, "DELETE /todos/1", "DELETE /todos/1",
                          "GET /todos/1", "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "204", _NF, _NF,
                          "200 [" + _TODO_B + "]"]))],
             ["The condition is the verb and `id !== undefined`, like the other two `:id` routes.",
              "`deleteTodo(id)` answers whether it removed anything. Keep that answer.",
              "Not removed: 404 and `return`. Removed: `sendEmpty(res, 204)` and `return`.",
              "No `readBody` — a delete has nothing in its body worth reading."]),
        _pfix("todo-m12-route-fix1", "Two todos called 3",
              "This store makes ids the way module 2 decided not to. Create three, "
              "delete the middle one, create another — and `GET /todos` shows two "
              "todos with id 3.\n\n"
              "Every route is correct. The store is not.",
              _m12(store=_M10_STORE.replace(
                  "const todos: Todo[] = [];\nlet nextId = 1;",
                  "const todos: Todo[] = [];").replace(
                  """  const todo: Todo = { id: nextId, title: title, done: false };
  nextId = nextId + 1;""",
                  """  const todo: Todo = { id: todos.length + 1, title: title, done: false };""")),
              _M12_FULL,
              [("\n".join([_POST_A, _POST_B, _POST_C, "DELETE /todos/2", _POST_D, "GET /todos"]),
                "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "201 " + _TODO_C, "204",
                           "201 " + _TODO_D4,
                           "200 [" + _TODO_A + "," + _TODO_C + "," + _TODO_D4 + "]"]))],
              ["After the delete the list has two todos. What is `todos.length + 1`?",
               "An id has to be something that never goes backwards, whatever happens to the list.",
               "Module 2's store kept a separate counter, `let nextId = 1;`, and bumped it on every add.",
               "`let nextId = 1;` beside the array, `id: nextId` in the todo, then `nextId = nextId + 1;`."],
              difficulty="Medium"),
    ],
    quiz=[
        _pq("Why does the DELETE route not call `readBody`?",
            ["The URL says everything a delete needs; waiting for a body is work, and a way to hang, for nothing",
             "DELETE requests cannot have a body",
             "`readBody` only works for POST",
             "Because the body was already read by `todoId`"],
            0,
            "Module 8's rule: read inside the route that needs it. This one does "
            "not."),
        _pq("What went wrong in the `todos.length + 1` store, in one sentence?",
            ["The id depended on the list, and a delete made the list shorter, so an id already in use was handed out again",
             "`length` is off by one",
             "The counter overflowed",
             "`push` put the todo in the wrong place"],
            0,
            "An id must never depend on anything that can go down. The counter "
            "depends on nothing but itself."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M12_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M12_DELETE, _M12_SENDEMPTY, _M12_HANDLER))

_M12_FINAL = _pch(
    "todo-m12-build", "Module 12 build — the complete resource", "Medium",
    "Write `deleteTodo`, `sendEmpty` and the handler — all five routes.\n\n"
    "* `deleteTodo(id)` — remove the todo with that id and answer `true`, or "
    "answer `false` and remove nothing\n"
    "* `sendEmpty(res, status)` — a status with no body and no headers\n"
    "* the handler — list, create, fetch one, patch, delete, and the 404\n\n"
    "The script uses every verb. It deletes the middle todo of three, deletes it "
    "again, deletes one that never existed, and then creates a fourth — whose id "
    "must be 4.",
    _M12_FULL,
    _M12_BUILD_BLANK,
    [("\n".join([_POST_A, _POST_B, _POST_C,
                 'PATCH /todos/1 {"done":true}',
                 "DELETE /todos/2", "DELETE /todos/2", "DELETE /todos/99",
                 _POST_D, "GET /todos/2", "GET /todos"]),
      "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "201 " + _TODO_C,
                 "200 " + _TODO_A_DONE,
                 "204", _NF, _NF,
                 "201 " + _TODO_D4, _NF,
                 "200 [" + _TODO_A_DONE + "," + _TODO_C + "," + _TODO_D4 + "]"]))],
    ["`deleteTodo`: `findIndex` by id, `return false` on `-1`, then `splice(i, 1)` and `return true`.",
     "`sendEmpty`: `res.writeHead(status);` and `res.end();` — nothing else.",
     "The handler is module 11's with one more route: `DELETE` on `id !== undefined`, 404 or 204.",
     "`DELETE /todos/99` must leave the store alone. If todo 4 comes out wrong or todo 3 goes missing, the `-1` got through."],
)


_TODO_MODULES.append(_pmod(
    key="todo-delete", number=12, phase="crud",
    title="DELETE /todos/:id — and 204",
    what="findIndex, splice, and the response with no body",
    goal="Remove a todo, answer correctly when it was never there — and complete the resource.",
    why=_M12_WHY,
    est_minutes=45,
    builds_on=["todo-store", "todo-one", "todo-update"],
    concepts=["findIndex", "-1 as not-found", "splice", "positions vs ids",
              "204 No Content", "ids that are never reused"],
    deliverable="The complete resource: every verb on a todo works over HTTP, and no id "
                "is ever handed out twice.",
    objectives=[
        "Find a position by condition with `findIndex`, and say how it differs from `find` and `indexOf`",
        "Explain what an unchecked `-1` does to `splice`, and write the check that stops it",
        "Remove exactly one element with `splice`, and predict what `splice(i)` removes instead",
        "Say why a todo's position changes after a delete and its id does not",
        "Answer a delete with 204 and no body, and explain why `send(res, 204, …)` passes a test and is still wrong",
        "Reproduce module 2's id collision with a `length + 1` store, and explain why the counter cannot collide",
    ],
    endpoints=[
        _pep("DELETE", "/todos/:id", "Delete a todo", "", "(empty)", "204 · 404"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M12_BRIEF,
    syntax=_M12_SYNTAX,
    steps=[_M12_S1, _M12_S2, _M12_S3, _M12_S4],
    final_build=_M12_FINAL,
    acceptance=[
        "`curl -s -i -X DELETE localhost:3000/todos/1` returns 204 with no body and no `Content-Type` header.",
        "Running the same delete a second time returns 404 and `{\"error\":\"not_found\"}`.",
        "`curl -s -i -X DELETE localhost:3000/todos/99` returns 404 — and every other todo is still there afterwards.",
        "`curl -s localhost:3000/todos/1` after deleting it returns 404.",
        "Deleting the middle of three todos leaves the other two with their ids unchanged.",
        "Creating a todo after a delete gives it a new id — never the deleted one, never one already in use.",
        "Every verb works: `GET /todos`, `POST /todos`, `GET`, `PATCH` and `DELETE` on `/todos/:id`.",
    ],
    manual_test="""
With `node server.ts` running, make three:

```bash
for t in 'Buy milk' 'Write tests' 'Ship it'; do
  curl -s -X POST localhost:3000/todos -d "{\\"title\\":\\"$t\\"}"; echo
done
```

Delete the middle one, twice, and one that never existed:

```bash
curl -s -i -X DELETE localhost:3000/todos/2     # 204, no body
curl -s -i -X DELETE localhost:3000/todos/2     # 404 — already gone
curl -s -i -X DELETE localhost:3000/todos/99    # 404 — and nothing else was touched
curl -s localhost:3000/todos                    # 1 and 3, ids unchanged
curl -s -X POST localhost:3000/todos -d '{"title":"Again"}'   # id 4
```

Now look at the difference no test in this module could see. Change the delete
route to `send(res, 204, { deleted: true });`, restart, and delete something with
`-i`:

```
HTTP/1.1 204 No Content
Content-Type: application/json
```

A header promising JSON, and no JSON. Put `sendEmpty` back and the header goes
with it.

Last, break it the way step 1 warned. Remove the `if (i === -1)` check from
`deleteTodo`, restart, create three todos and `DELETE /todos/99`. It answers 204 —
and `GET /todos` will show you which todo paid for it.
""",
    reference="""// server.ts — module 12
//
// The complete resource. Every verb on a todo works over HTTP — list, create,
// fetch, patch and delete — and phase 3 is done.
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [];
// Module 2's counter, and this is the module it was for. It only ever goes up,
// so a deleted todo's id is never handed out again — `todos.length + 1` would
// hand out an id ALREADY IN USE after the first delete from the middle.
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

function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}

// We have an id, not the todo — so `findIndex`, not module 11's `indexOf`.
//
// -1 IS THE DANGER. findIndex answers -1 for "not found", and splice(-1, 1)
// does not fail: it counts from the end and removes the LAST todo. Without the
// check, DELETE /todos/99 deletes somebody else's todo and answers 204.
function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);          // one element, at i. splice(i) would take the rest.
  return true;
}

function send(res: ServerResponse, status: number, data: object): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data));
}

// The second way a response leaves: a status with no body, and so no
// Content-Type — there is no content to have a type. Node would silently drop
// a body sent with a 204 anyway, but not the header that promised it.
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

function changesFrom(data: any): Partial<Todo> {
  const changes: Partial<Todo> = {};
  if (data.title !== undefined) {
    changes.title = data.title;
  }
  if (data.done !== undefined) {
    changes.done = data.done;
  }
  return changes;
}

async function handler(req: IncomingMessage, res: ServerResponse): Promise<void> {
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

  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data = JSON.parse(body);
    const updated = updateTodo(todo, changesFrom(data));
    send(res, 200, updated);
    return;
  }

  // No body to read: a delete says everything it needs to in its URL.
  if (req.method === "DELETE" && id !== undefined) {
    const removed = deleteTodo(id);
    if (!removed) {
      send(res, 404, { error: "not_found" });   // never there, or already gone
      return;
    }
    sendEmpty(res, 204);
    return;
  }

  send(res, 404, { error: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Make a repeated delete answer 204 instead of 404, on the grounds that the end state — no todo 1 — is the same. Then write down what a client loses by not being able to tell \"I deleted it\" from \"it was already gone\".",
        "Add `DELETE /todos` that removes every todo with `done: true` and answers `{\"removed\":n}`. Decide whether it should be a 200 or a 204, given that it has something to say.",
        "Swap the counter for \"the highest id in the list plus one\". Find the request sequence that makes it reuse an id. (Hint: delete from the end.)",
        "Make `deleteTodo` return the removed todo, or `undefined`, instead of a boolean. `splice` hands back what it removed — as an array — and `noUncheckedIndexedAccess` will have an opinion about reading `[0]` from it.",
        "Soft delete: instead of `splice`, add a `deletedAt` counter to the todo and have every other route skip deleted todos. Count how many routes had to change — that number is the argument against it.",
    ],
    glossary=[
        _pgloss("findIndex", "`array.findIndex(fn)` — the position of the first element `fn` is true of, or `-1`. `find` that answers where rather than what."),
        _pgloss("-1", "The not-found answer from `findIndex` and `indexOf`. A real number, so the compiler cannot tell it means \"missing\" — check it by name."),
        _pgloss("splice", "`array.splice(i, n)` — remove `n` elements starting at `i`, in place. With no `n`, removes everything from `i` on. A negative `i` counts from the end."),
        _pgloss("204 No Content", "It worked, and there is nothing to send back. Carries no body and no `Content-Type`."),
        _pgloss("position vs id", "Where a todo sits in the array versus which todo it is. Positions shift on every delete; ids never change."),
        _pgloss("id reuse", "Handing out an id that belonged to a deleted todo — or worse, one still in use. What a `length + 1` scheme does after a delete, and what a counter cannot do."),
        _pgloss("CRUD", "Create, read, update, delete — the four things a resource can have done to it. This module completes them."),
    ],
    cheatsheet="""
```ts
// position by id: -1 means nowhere, and must never reach splice
function deleteTodo(id: number): boolean {
  const i = todos.findIndex((t) => t.id === id);
  if (i === -1) {
    return false;
  }
  todos.splice(i, 1);            // one, at i
  return true;
}

// a response with no body and no Content-Type
function sendEmpty(res: ServerResponse, status: number): void {
  res.writeHead(status);
  res.end();
}

// the route: no body to read
if (req.method === "DELETE" && id !== undefined) {
  const removed = deleteTodo(id);
  if (!removed) { send(res, 404, { error: "not_found" }); return; }
  sendEmpty(res, 204);
  return;
}
```

| You have | You want | Call | Not found |
|---|---|---|---|
| a condition | the element | `find` | `undefined` |
| an object | its position | `indexOf` | `-1` |
| a condition | its position | `findIndex` | `-1` |

| Request | Answer |
|---|---|
| `DELETE /todos/1`, exists | `204`, no body |
| `DELETE /todos/1`, again | `404` |
| `DELETE /todos/99`, never existed | `404` — and nothing else touched |
| `POST` after a delete | a new id, never reused |

| Symptom | Cause |
|---|---|
| deleting a missing todo deletes the last one | no `i === -1` check; `splice(-1, 1)` |
| one delete removes several todos | `splice(i)` with no count |
| 204 for a todo that was never there | the route ignored `deleteTodo`'s answer |
| 204 has a `Content-Type` header | sent with `send`, not `sendEmpty` |
| two todos share an id after a delete | ids from `todos.length + 1` |
""",
    self_check=[
        "Can you say which of `find`, `indexOf` and `findIndex` a delete needs, and why the other two do not fit?",
        "Can you explain exactly what happens when `findIndex`'s `-1` reaches `splice(i, 1)`?",
        "Can you predict what `splice(i)` removes, and what `splice(i, 1)` does?",
        "Can you say why todo 3's position changes after deleting todo 2 and its id does not?",
        "Can you explain why `send(res, 204, …)` passes every test here and is still wrong, and how you would see it?",
        "Can you walk through the request sequence that makes a `length + 1` store hand out a duplicate id?",
        "Can you name all five routes of the finished resource with their success status codes?",
    ],
    review=[
        _pq("`deleteTodo(99)` in a store with no todo 99 and no `-1` check. What happens?",
            ["`splice(-1, 1)` removes the last todo, and the function reports success",
             "Nothing — `splice` ignores negative positions",
             "It throws, and the replayer answers 500",
             "A compile error, because `-1` is not a valid index"],
            0,
            "Silent data loss, answered with a 204. The most dangerous bug in the "
            "module is one that looks like success."),
        _pq("What does `findIndex` answer when no element matches?",
            ["`-1`",
             "`undefined`",
             "`null`",
             "The array's length"],
            0,
            "A number, so the type cannot warn you. The same reason module 10 "
            "made `parseId` return `undefined` rather than a magic number."),
        _pq("Why does a 204 response not go through `send`?",
            ["`send` always writes a JSON body and a `Content-Type`; a 204 must have neither",
             "`send` cannot take status 204",
             "Because a 204 is an error",
             "It should go through `send`; `sendEmpty` is optional"],
            0,
            "Two kinds of response, two helpers. Module 5's rule — every response "
            "leaves through one — still holds."),
        _pq("After three creates and `DELETE /todos/2`, what does the next create get with this project's store?",
            ["Id 4 — the counter only goes up",
             "Id 2 — the freed one",
             "Id 3 — `length + 1`",
             "An error, because 2 is missing"],
            0,
            "And `/todos/2` is a 404 forever, which is the promise an id makes."),
        _pq("Which of these routes reads a request body?",
            ["`POST /todos` and `PATCH /todos/:id`",
             "All five",
             "Only `POST /todos`",
             "`PATCH` and `DELETE`"],
            0,
            "A route reads a body only when the change it makes is described in "
            "one. A delete's change is described by its URL alone."),
        _pq("Module 2 demonstrated the id collision with `.shift()`. Why not with a delete?",
            ["There was no delete yet — this module is the first that can remove a todo by id",
             "`splice` did not exist in module 2's TypeScript",
             "Because a delete cannot cause a collision",
             "It did use a delete"],
            0,
            "A decision made ten modules early, for a reason that could only be "
            "shown now. That is what building the data model first buys."),
    ],
    milestone="The resource is complete. Every verb on a todo works over HTTP — "
              "create, list, fetch, patch and delete — with its own status code "
              "and its own honest failure, and no id is ever handed out twice. "
              "Phase 3 is done.",
))
