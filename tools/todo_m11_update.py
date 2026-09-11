# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 11 — PATCH /todos/:id, partial update.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses module 10's program pieces (`_M10_STORE`, …) and
# request/response constants, which are already in the shared namespace.
#
# A PATCH IS NOT A TODO. `{"done":true}` has no id and no title, and the module
# is about typing that honestly (`Partial<Todo>`), building it from exactly the
# fields a client may change (`changesFrom`), and applying it without touching
# anything else (`{ ...todo, ...changes }`).
#
# MODULE 9'S TECHNIQUE, AGAIN. The client's `id` is ignored rather than
# rejected, because `changesFrom` copies two named fields and has nowhere to put
# a third. Module 9 promised this module would do exactly that, and step 1 says
# so.
#
# `data: any` IS WRITTEN OUT LOUD. `changesFrom` takes what `JSON.parse` handed
# back, and its parameter says what that is. Module 13 changes that one word to
# `unknown` and every line of the function stops compiling — which is the whole
# of module 13's argument, set up here on purpose.
#
# REPLACE, NOT MUTATE — and the reason is module 14's. `updateTodo` builds a new
# todo and swaps it into the array with `indexOf`. Mutating in place would
# produce the same output today; the difference is that a new object is an
# all-or-nothing change, so when module 14 validates the result before storing
# it, a rejected patch leaves the store exactly as it was. `.indexOf(` is gated
# here: you have the object and want its position. Module 12's `.findIndex(` is
# the other case — you have an id and want a position.
#
# THE GRADABLE BUGS, all visible on ordinary requests (see PROJECTS_ROADMAP.md,
# trap 3): a patch that copies the whole body, a spread in the wrong order, the
# explicit `undefined` that wipes a title, an update never stored, and reading
# the body before the lookup (a junk body to a missing todo becomes a 500 instead
# of a 404).
# ---------------------------------------------------------------------------

_M11_CHANGES = """function changesFrom(data: any): Partial<Todo> {
  const changes: Partial<Todo> = {};
  if (data.title !== undefined) {
    changes.title = data.title;
  }
  if (data.done !== undefined) {
    changes.done = data.done;
  }
  return changes;
}
"""

_M11_UPDATE = """function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}
"""

_M11_PATCH_ROUTE = """  if (req.method === "PATCH" && id !== undefined) {
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
  }"""

_M11_HANDLER = _M10_HANDLER.replace(
    """    send(res, 200, todo);
    return;
  }

  send(res, 404, { error: "not_found" });
}""",
    """    send(res, 200, todo);
    return;
  }

""" + _M11_PATCH_ROUTE + """

  send(res, 404, { error: "not_found" });
}""")
assert _M11_HANDLER != _M10_HANDLER, "module 11: PATCH route was not inserted"


def _m11(handler=_M11_HANDLER, changes=_M11_CHANGES, update=_M11_UPDATE):
    """A module-11 server program: module 10's, plus the two patch functions."""
    return _server("\n\n".join(p.rstrip("\n") for p in
                               (_M10_STORE, _M10_SEND, _M10_READBODY,
                                _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                changes, update, handler)))


_M11_FULL = _m11()

_TODO_TYPE = """type Todo = {
  id: number;
  title: string;
  done: boolean;
};
"""

# --- Step 1's plain program: what changesFrom keeps of five bodies ----------
_M11_S1_PRINTS = """
console.log(JSON.stringify(changesFrom(JSON.parse('{"done":true}'))));
console.log(JSON.stringify(changesFrom(JSON.parse('{"title":"Buy oat milk"}'))));
console.log(JSON.stringify(changesFrom(JSON.parse('{"title":"Ship it","done":false}'))));
console.log(JSON.stringify(changesFrom(JSON.parse('{"id":99,"done":true,"isAdmin":true}'))));
console.log(JSON.stringify(changesFrom(JSON.parse('{}'))));
"""
_M11_S1_OUT = ('{"done":true}\n{"title":"Buy oat milk"}\n{"title":"Ship it","done":false}\n'
               '{"done":true}\n{}')


def _m11_s1(changes=_M11_CHANGES):
    return _plain(_TODO_TYPE + "\n" + changes.rstrip("\n") + "\n" + _M11_S1_PRINTS)


# --- Step 2's plain program: applying a patch to one todo -------------------
_M11_APPLY = """function applyChanges(todo: Todo, changes: Partial<Todo>): Todo {
  return { ...todo, ...changes };
}
"""

_M11_S2_PRINTS = """
const todo: Todo = { id: 1, title: "Buy milk", done: false };
console.log(JSON.stringify(applyChanges(todo, changesFrom(JSON.parse('{"done":true}')))));
console.log(JSON.stringify(applyChanges(todo, changesFrom(JSON.parse('{"title":"Buy oat milk"}')))));
console.log(JSON.stringify(applyChanges(todo, changesFrom(JSON.parse('{"id":99}')))));
console.log(JSON.stringify(todo));
"""
_M11_S2_OUT = ('{"id":1,"title":"Buy milk","done":true}\n'
               '{"id":1,"title":"Buy oat milk","done":false}\n'
               '{"id":1,"title":"Buy milk","done":false}\n'
               '{"id":1,"title":"Buy milk","done":false}')


def _m11_s2(apply=_M11_APPLY, changes=_M11_CHANGES):
    return _plain(_TODO_TYPE + "\n" + changes.rstrip("\n") + "\n\n" + apply.rstrip("\n")
                  + "\n" + _M11_S2_PRINTS)


_TODO_A_DONE = '{"id":1,"title":"Buy milk","done":true}'
_TODO_A_OAT = '{"id":1,"title":"Buy oat milk","done":false}'
_TODO_A_OAT_DONE = '{"id":1,"title":"Buy oat milk","done":true}'

_M11_WHY = (
    "A todo can be created and fetched, and never changed. The one thing a todo "
    "list is for — ticking something off — is impossible: the only way to mark "
    "`Buy milk` done is to create a second todo with the same title and ignore "
    "the first. Every todo is frozen at the moment it was posted, typos "
    "included. This module gives the resource its first verb that changes what "
    "is already there."
)

_M11_BRIEF = """
### The whole module in one line

Let a client change a todo's `title` or `done` — either, both, or neither —
without touching anything else about it.

### A PATCH is not a todo

```
PATCH /todos/1   {"done":true}
```

That body has no `id` and no `title`. It is not a todo; it is a **description of
a change** to one. So it cannot be typed as `Todo`, and it cannot be stored as
one. It has to be *applied* to the todo that is already there.

```ts
type Todo           = { id: number;  title: string;  done: boolean };
type Partial<Todo>  = { id?: number; title?: string; done?: boolean };   // every field optional
```

`Partial<Todo>` is TypeScript's name for "some of a todo's fields, maybe none".
That is exactly what a patch is.

### Three pieces, one per step

```ts
const changes = changesFrom(data);              // 1. keep only what a client may change
const updated = { ...todo, ...changes };        // 2. the old todo, with the changes on top
todos[todos.indexOf(todo)] = updated;           // 3. swap it into the store
```

### PATCH, not PUT

`PUT` means *replace the whole thing with this*. A client that `PUT`s
`{"done":true}` is asking for a todo with no title. `PATCH` means *change these
fields and leave the rest alone*, which is what "tick it off" actually is. This
API has only `PATCH`, and the stretch list has `PUT` for anyone who wants to feel
the difference.

### What stays wrong, on purpose

`{"done":"yes"}` is accepted and stored — `done` becomes the string `"yes"`.
`JSON.parse` still hands back `any`, `changesFrom` still trusts it, and the
`data: any` in its signature now says so out loud. That word is the one module
13 changes.
"""

_M11_SYNTAX = [
    _syn(
        "Partial<Todo>",
        "The type `Todo` with every field made optional. Exactly the shape of "
        "\"some of a todo's fields, maybe none\" — which is what a patch is.",
        """
const changes: Partial<Todo> = { done: true };     // fine — title and id may be absent
const empty: Partial<Todo> = {};                   // also fine
""",
        "It makes `id` optional too — which means it *allows* one. The type does "
        "not stop a client's id reaching a patch; `changesFrom` does, by never "
        "copying it.",
    ),
    _syn(
        "function changesFrom(data: any): Partial<Todo> { … }",
        "Build a patch out of a parsed body, copying only the fields a client is "
        "allowed to change. `data: any` states out loud what `JSON.parse` hands "
        "you.",
        """
const changes: Partial<Todo> = {};
if (data.done !== undefined) {
  changes.done = data.done;
}
""",
        "Copy a field only when it is there. `{ title: data.title }` for a body "
        "with no title makes a patch whose title is `undefined` — and step 2 shows "
        "what that does to the todo it is applied to.",
    ),
    _syn(
        "const updated: Todo = { ...todo, ...changes };",
        "Object **spread**: a new object with every field of `todo`, then every "
        "field of `changes` on top. A key that appears twice keeps the **later** "
        "value.",
        """
const todo = { id: 1, title: "Buy milk", done: false };
const updated = { ...todo, ...{ done: true } };
// { id: 1, title: "Buy milk", done: true } — and `todo` is untouched
""",
        "Order is the whole meaning. `{ ...changes, ...todo }` puts the old todo "
        "*on top of* the changes, and every patch silently does nothing.",
    ),
    _syn(
        "const i = todos.indexOf(todo);",
        "The position of one exact object in an array — the one you already have "
        "in hand from `findTodo`.",
        """
const i = todos.indexOf(todo);   // 0, 1, 2 …
todos[i] = updated;              // swap the new todo into that slot
""",
        "`indexOf` compares *identity*, not contents, so it finds the object "
        "`findTodo` returned and not a lookalike. It answers `-1` if the object is "
        "not there — which cannot happen here, because you just found it.",
    ),
    _syn(
        "todos[i] = updated;",
        "Write into one slot of an array. The array is `const`; its contents are "
        "not — module 2's distinction, doing real work at last.",
        "",
        "Reading `todos[i]` gives `Todo | undefined`, because a read can miss. "
        "Writing does not, because a write never produces a value to be unsure of.",
    ),
    _syn(
        "const id = todoId(url.pathname);",
        "Module 10's id, parsed once at the top. `PATCH` reads it exactly as "
        "`GET` does and parses nothing.",
        "",
        "",
        recap=True,
    ),
    _syn(
        "const data = JSON.parse(body);",
        "Module 9's parse — still `any`, still trusted, still named as a hole.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — what a patch is.
# ---------------------------------------------------------------------------

_M11_S1 = _pstep(
    "partial", "What a patch is",
    "`Partial<Todo>`, and building one out of only the fields a client may change.",
    """
Here is what a client sends to tick a todo off:

```
PATCH /todos/1   {"done":true}
```

Try to type that body as a `Todo` and the compiler refuses: there is no `id` and
no `title`. Nor should there be — the client is not describing a todo, it is
describing a **change** to one.

### `Partial<Todo>`

```ts
Partial<Todo>
// means exactly:
// { id?: number; title?: string; done?: boolean }
```

`Partial` takes a type and makes every field optional. `{ done: true }` fits.
`{ title: "Buy oat milk" }` fits. `{}` fits — a patch that changes nothing is
still a patch. Anything with a field `Todo` does not have does not.

### Build it from named fields, never from the whole body

```ts
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
```

Start empty. Copy `title` if it was sent. Copy `done` if it was sent. Copy
**nothing else**, ever.

This is module 9's technique, word for word. There, the create route ignored a
client's `id` because `addTodo` takes only a title and had nowhere to put one.
Here, `changesFrom` copies two fields by name and has nowhere to put a third. A
client can send `{"id":99,"isAdmin":true,"done":true}` and the patch that comes
out is `{"done":true}` — no check, no rejection, no field it did not name.

Notice what does *not* protect you: the type. `Partial<Todo>` has an optional
`id`, so `const changes: Partial<Todo> = data;` would compile and would let the
client renumber the todo. The guard is the code that chooses the fields.

### `data: any`, said out loud

`changesFrom` takes what `JSON.parse` returned, and its parameter type is the
honest description of that: `any`. You have been trusting `any` since module 9
without writing the word. Writing it makes the hole visible in the one place it
lives — and module 13 changes that single word to `unknown`, at which point
every line of this function stops compiling. That is module 13.
""",
    """
Your `changesFrom` keeps exactly this of five bodies:

```
{"done":true}                             →  {"done":true}
{"title":"Buy oat milk"}                  →  {"title":"Buy oat milk"}
{"title":"Ship it","done":false}          →  {"title":"Ship it","done":false}
{"id":99,"done":true,"isAdmin":true}      →  {"done":true}
{}                                        →  {}
```

The fourth is the one that matters. Two fields nobody may set, gone, and nothing
had to say no.
""",
    pitfalls=[
        "Typing the body as `Todo`. It is not one — it has no id and usually no title — and the compiler will say so the moment you try.",
        "`const changes: Partial<Todo> = data;`. Compiles, because `Partial<Todo>` has an optional `id` — and now a client can renumber a todo by sending one.",
        "Assuming `Partial<Todo>` keeps the id out. It does the opposite: it *allows* an id. The code that names the fields is the guard, not the type.",
        "Copying fields in a loop over whatever the body contains. Every field a client invents lands in your store — `isAdmin`, `id`, `__proto__`. Name the fields you accept.",
        "Treating `{}` as an error. A patch that changes nothing is a valid patch; the todo comes back unchanged with a 200.",
    ],
    warmup=[
        _pq("A client sends `PATCH /todos/1 {\"done\":true}`. Why can the body not be typed as `Todo`?",
            ["It has no `id` and no `title` — it describes a change to a todo, not a todo",
             "Because `done` must be a string in JSON",
             "Because `Todo` is only for responses",
             "It can; missing fields default to `undefined`"],
            0,
            "A patch is a different kind of thing from the resource it changes, "
            "and `Partial<Todo>` is the type for that kind of thing."),
        _pq("`Partial<Todo>` — is `{ id: 7 }` a valid value of it?",
            ["Yes — `Partial` makes every field optional, `id` included, so the type does not keep the id out",
             "No — `Partial` removes the id",
             "No — `Partial` requires at least one field",
             "Only if `id` is a string"],
            0,
            "Which is why the guard is `changesFrom`, which never copies `id`, "
            "rather than the type."),
    ],
    exercises=[
        _pex("todo-m11-partial-1", "Start with an empty patch",
             "`changesFrom` builds a patch one field at a time. Declare the empty "
             "one it starts from — typed as some of a todo's fields, maybe none.",
             _m11_s1(),
             "  const changes: Partial<Todo> = {};",
             [("", _M11_S1_OUT)],
             ["The type is the one this module is named after.",
              "`Todo` would not accept `{}` — it needs all three fields.",
              "It is `const`: the binding never changes, only the object's contents.",
              "`const changes: Partial<Todo> = {};`"]),
        _pfix("todo-m11-partial-fix1", "The patch that let the id through",
              "`changesFrom` compiles and passes most bodies through correctly. "
              "But `{\"id\":99,\"done\":true,\"isAdmin\":true}` comes out with the "
              "`id` and the `isAdmin` still in it — the patch is the whole body.",
              _m11_s1("""function changesFrom(data: any): Partial<Todo> {
  const changes: Partial<Todo> = data;
  return changes;
}
"""),
              _m11_s1(),
              [("", _M11_S1_OUT)],
              ["It compiles because `data` is `any` and `Partial<Todo>` allows an id. Neither is protecting you.",
               "Start from an empty patch instead of the body.",
               "Copy `title` and `done` by name, each only when it is not `undefined`.",
               "`const changes: Partial<Todo> = {};` then two `if (data.x !== undefined) { changes.x = data.x; }`"],
              difficulty="Easy"),
        _pex("todo-m11-partial-2", "Copy done, if it was sent",
             "`title` is handled. Handle `done` the same way: copy it into the "
             "patch only when the body has one.",
             _m11_s1(),
             """  if (data.done !== undefined) {
    changes.done = data.done;
  }""",
             [("", _M11_S1_OUT)],
             ["It is the `title` block with one word changed.",
              "The check is `data.done !== undefined` — `false` is a perfectly good value to send, so do not test for truthiness.",
              "Inside: `changes.done = data.done;`."]),
    ],
    quiz=[
        _pq("What stops a client's `id` reaching the patch?",
            ["`changesFrom` copies `title` and `done` by name and never copies `id` — the same technique module 9 used",
             "`Partial<Todo>` removes the `id` field",
             "`JSON.parse` drops unknown fields",
             "The route checks for an `id` and rejects it"],
            0,
            "Code that names what it accepts cannot accept what it did not name."),
        _pq("Why does `changesFrom` check `data.done !== undefined` rather than `if (data.done)`?",
            ["`false` is a real value to send — `{\"done\":false}` un-ticks a todo, and a truthiness test would ignore it",
             "`!== undefined` is faster",
             "`if (data.done)` does not compile on `any`",
             "There is no difference"],
            0,
            "Un-ticking is as much a change as ticking. A falsy value is still a "
            "value the client sent."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — applying it.
# ---------------------------------------------------------------------------

_M11_S2 = _pstep(
    "spread", "Applying a patch",
    "Object spread, the rule that the later key wins, and the `undefined` that erases a title.",
    """
You have the todo and a patch. The result is the todo with the patch laid over
it:

```ts
const updated = { ...todo, ...changes };
```

`...todo` copies every field of the todo into a **new** object. `...changes`
then copies every field of the patch into it. Where both have a field, the one
written **later** wins — which is the whole design:

```ts
const todo    = { id: 1, title: "Buy milk", done: false };
const changes = { done: true };

{ ...todo, ...changes }    // { id: 1, title: "Buy milk", done: true }   ✓
{ ...changes, ...todo }    // { id: 1, title: "Buy milk", done: false }  — the patch did nothing
```

Same two objects, opposite order, and the second line quietly throws the
client's change away. There is no error, because both lines are perfectly valid;
the order *is* the meaning.

### A new object, not an edited one

```ts
const updated = { ...todo, ...changes };
console.log(todo.done);      // still false
```

Spread never touches `todo`. It builds something new. Step 3 is about why that
is worth having — for now, notice the last line of this step's program, which
prints the original todo after three patches and finds it exactly as it was.

### The `undefined` that erases a title

Here is the most natural way to write `changesFrom`, and it is wrong:

```ts
function changesFrom(data: any): Partial<Todo> {
  return { title: data.title, done: data.done };
}
```

Send `{"done":true}` and the patch is `{ title: undefined, done: true }`. Spread
that over the todo, and `title: undefined` is a field like any other — it **wins**:

```ts
{ ...todo, ...{ title: undefined, done: true } }
// { id: 1, title: undefined, done: true }
```

`JSON.stringify` then leaves `undefined` fields out entirely, so the client gets
back `{"id":1,"done":true}` and the title is simply gone. It compiles, because
`Partial<Todo>` says `title?: string` and TypeScript does not distinguish a
missing field from one set to `undefined`.

A field that is *absent* from the patch leaves the old value alone. A field that
is *present and undefined* overwrites it. That is why step 1 copies each field
only inside an `if`.
""",
    """
Four lines from this step's program, and each is worth reading:

```
{"done":true}               →  {"id":1,"title":"Buy milk","done":true}
{"title":"Buy oat milk"}    →  {"id":1,"title":"Buy oat milk","done":false}
{"id":99}                   →  {"id":1,"title":"Buy milk","done":false}
(the original, afterwards)  →  {"id":1,"title":"Buy milk","done":false}
```

The third is a patch the client meant to renumber with; it changed nothing. The
fourth is the original todo, untouched by three spreads.
""",
    pitfalls=[
        "`{ ...changes, ...todo }`. Valid, compiles, and every patch silently does nothing — the old todo is spread on top of the changes.",
        "`{ title: data.title, done: data.done }` as the patch. A body without a title makes `title: undefined`, which wins the spread and erases the title. The response then has no `title` field at all.",
        "Expecting TypeScript to catch the explicit `undefined`. `title?: string` accepts both \"absent\" and \"undefined\", and only one of them leaves the old value alone.",
        "Thinking spread edits `todo`. It builds a new object; `todo` is exactly as it was. That is a feature — step 3 is why.",
        "Spreading `data` directly: `{ ...todo, ...data }`. Every field the client sent lands on the todo, `id` and `isAdmin` included.",
    ],
    warmup=[
        _pq("`{ ...{ a: 1, b: 2 }, ...{ b: 3 } }` — what is it?",
            ["`{ a: 1, b: 3 }` — the later spread wins where both have a key",
             "`{ a: 1, b: 2 }`",
             "`{ b: 3 }`",
             "A compile error, because `b` appears twice"],
            0,
            "Spread copies left to right, and a later copy of a key overwrites an "
            "earlier one. Put the changes last."),
    ],
    exercises=[
        _pex("todo-m11-spread-1", "The todo, with the changes on top",
             "Return a new todo: every field of `todo`, then every field of "
             "`changes` over it.",
             _m11_s2(),
             "{ ...todo, ...changes }",
             [("", _M11_S2_OUT)],
             ["Two spreads inside one pair of braces.",
              "The one written later wins where both have a field.",
              "The changes have to win.",
              "`{ ...todo, ...changes }`"]),
        _pfix("todo-m11-spread-fix1", "Every patch does nothing",
              "No error, every line prints a todo — and every one of them is the "
              "original. `{\"done\":true}` leaves `done` false; a new title leaves "
              "the old one.",
              _m11_s2(_M11_APPLY.replace("{ ...todo, ...changes }", "{ ...changes, ...todo }")),
              _m11_s2(),
              [("", _M11_S2_OUT)],
              ["Where two spreads share a key, which one wins?",
               "The old todo has every key. Whatever is spread last overwrites the patch completely.",
               "`{ ...todo, ...changes }`"],
              difficulty="Intro"),
        _pfix("todo-m11-spread-fix2", "The title that vanished",
              "Patch a todo with `{\"done\":true}` and the answer is "
              "`{\"id\":1,\"done\":true}` — no `title` field at all. Patch it with a "
              "new title and `done` disappears instead.\n\n"
              "`applyChanges` is correct. The patch it is given is not.",
              _m11_s2(changes="""function changesFrom(data: any): Partial<Todo> {
  return { title: data.title, done: data.done };
}
"""),
              _m11_s2(),
              [("", _M11_S2_OUT)],
              ["For a body with no title, what is `data.title`?",
               "A field that is *present* and `undefined` still wins a spread. Only an *absent* field leaves the old value alone.",
               "Build the patch empty and add each field only when it was sent.",
               "`const changes: Partial<Todo> = {};` and an `if (data.x !== undefined)` per field."],
              difficulty="Medium"),
    ],
    quiz=[
        _pq("`{ ...todo, ...{ title: undefined } }` — what is the title?",
            ["`undefined` — a present key wins the spread even when its value is `undefined`",
             "The old title, because `undefined` is skipped",
             "A compile error",
             "An empty string"],
            0,
            "Spread copies keys, not values-that-look-meaningful. The fix is not "
            "to put the key there in the first place."),
        _pq("After `const updated = { ...todo, ...changes };`, what has happened to `todo`?",
            ["Nothing — spread builds a new object and leaves `todo` exactly as it was",
             "It now has the changes too",
             "It has been emptied",
             "It is the same object as `updated`"],
            0,
            "Which means the store still holds the old one. Step 3 puts the new "
            "one there."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — replacing it in the store.
# ---------------------------------------------------------------------------

_M11_S3 = _pstep(
    "replace", "Replacing it in the store",
    "`indexOf`, writing into a slot, and why a new object beats an edited one.",
    """
`{ ...todo, ...changes }` built a new todo. The store still holds the old one,
so as far as the next `GET` is concerned, nothing happened. The new one has to
go where the old one was:

```ts
function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}
```

`todos.indexOf(todo)` finds the position of that exact object — the one
`findTodo` handed you — and `todos[i] = updated` swaps the new one into its slot.
The array is `const`; its contents are not. That distinction from module 2 has
been waiting nine modules for something to do.

### Why not just edit the todo in place?

This would produce identical output today:

```ts
if (changes.title !== undefined) { todo.title = changes.title; }
if (changes.done !== undefined) { todo.done = changes.done; }
```

The difference shows up in module 14. There, a patch has to be **checked** before
it is stored — `{"title":""}` must be refused with a 400. Build-then-swap makes
that trivial:

```ts
const updated = { ...todo, ...changes };
// module 14: check `updated` here — and if it is bad, answer 400 and stop.
// The store has not been touched.
todos[i] = updated;
```

Edit-in-place has already changed the stored todo by the time you could check
it, so a rejected patch would be half-applied. A new object is all-or-nothing:
the store changes in one assignment, or not at all.

### `indexOf` versus `findIndex`

`indexOf` answers "where is **this object**?" — you have it in hand from
`findTodo`, so that is the right question. Module 12 deletes by id, where you
*do not* have the object, only a number; its question is "where is the todo
**whose id is 7**?", which is `findIndex`, and it is that module's.
""",
    """
```bash
$ curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'
{"id":1,"title":"Buy milk","done":false}

$ curl -s -X PATCH localhost:3000/todos/1 -d '{"done":true}'
{"id":1,"title":"Buy milk","done":true}

$ curl -s localhost:3000/todos/1
{"id":1,"title":"Buy milk","done":true}
```

The third request is the step. A patch that answered correctly and was never
stored would pass the second and fail the third.
""",
    pitfalls=[
        "Building `updated` and never storing it. The PATCH answers with the right todo, and the next GET shows the old one — the response and the store disagree.",
        "`todos[id] = updated`. The id is not the position: todo 1 lives at index 0, and after a delete (module 12) the two stop lining up entirely.",
        "Pushing `updated` instead of replacing. The list now has two todos with the same id, and `findTodo` keeps returning the old one because it comes first.",
        "Mutating the found todo field by field. Same output today, and a half-applied patch the moment module 14 can reject one partway through.",
        "Reading `todos[i]` and expecting a `Todo`. A read is `Todo | undefined` under `noUncheckedIndexedAccess`; a write is not. You only need the write.",
    ],
    warmup=[
        _pq("`updateTodo` builds `updated` with a spread and returns it, but never "
            "writes it into `todos`. What does `GET /todos/1` show after a PATCH?",
            ["The old todo — the new one was built and answered with, and never stored",
             "The new todo, because spread updates the original",
             "A 404",
             "Both todos"],
            0,
            "Spread builds a new object and leaves the old one where it was. "
            "Somebody has to swap it in."),
    ],
    exercises=[
        _pex("todo-m11-replace-1", "Find its slot",
             "`updated` is built. Find the position of the todo it replaces.",
             _M11_FULL,
             "  const i = todos.indexOf(todo);",
             [("\n".join([_POST_A, _POST_B, 'PATCH /todos/2 {"done":true}', "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "201 " + _TODO_B,
                          '200 {"id":2,"title":"Write tests","done":true}',
                          '200 [' + _TODO_A + ',{"id":2,"title":"Write tests","done":true}]']))],
             ["You have the object itself, from `findTodo`. You want where it is.",
              "The array method that answers \"where is this exact object?\"",
              "The next line writes into `todos[i]`.",
              "`const i = todos.indexOf(todo);`"]),
        _pfix("todo-m11-replace-fix1", "The change nobody saved",
              "`PATCH /todos/1 {\"done\":true}` answers "
              "`{\"id\":1,\"title\":\"Buy milk\",\"done\":true}`. Then `GET /todos/1` "
              "answers with `done: false`. The response and the store disagree.",
              _m11(update="""function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  return updated;
}
"""),
              _M11_FULL,
              [("\n".join([_POST_A, 'PATCH /todos/1 {"done":true}', "GET /todos/1"]),
                "\n".join(["201 " + _TODO_A, "200 " + _TODO_A_DONE, "200 " + _TODO_A_DONE]))],
              ["Spread made a new todo. Where is the old one still living?",
               "The store's array still holds the original object.",
               "Find the original's position and write the new one there.",
               "`const i = todos.indexOf(todo);` then `todos[i] = updated;`"],
              difficulty="Easy"),
    ],
    quiz=[
        _pq("Why does this project build a new todo and swap it in, instead of editing the stored one?",
            ["A new object is all-or-nothing — module 14 can check it and refuse it before the store is touched",
             "Editing objects is not allowed in TypeScript",
             "Spread is faster than assignment",
             "`findTodo` returns a copy, so edits would be lost"],
            0,
            "Build, check, commit. Editing in place commits before you can check."),
        _pq("Why `indexOf` here and not `findIndex`?",
            ["You already have the object from `findTodo` — `indexOf` finds that exact object; `findIndex` is for when you only have a condition like an id",
             "`findIndex` does not exist",
             "`indexOf` works on ids",
             "They behave identically"],
            0,
            "Module 12 is the other case: a delete has an id and no object, and "
            "asks `findIndex` where the matching todo is."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — the route.
# ---------------------------------------------------------------------------

_M11_S4 = _pstep(
    "route", "The route: look up, then read",
    "PATCH on the same `id` as GET — and why the lookup comes before the body.",
    """
```ts
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
```

The condition is module 10's with a different verb. `id` was parsed at the top
of the handler; this route parses nothing.

### The lookup goes first

Module 9's write route was four lines: read, parse, store, answer. This one is
the same four lines with a **lookup in front**, and the order is not a matter of
taste. Consider a client that patches a todo that does not exist, with a body
that is not JSON:

```
PATCH /todos/9   notjson
```

Look up first: there is no todo 9, and the answer is `404` — true, and the most
useful thing the client can hear. Parse first: `JSON.parse` throws, and the
answer is `500` — the server blaming itself, for a request whose real problem is
that it is aimed at nothing. The body of a request to a missing resource is
irrelevant, so do not read it.

### 200, with the whole todo

A PATCH answers `200` and the todo **as it now is** — every field, not just the
ones that changed. The client sent a fragment; it gets back the whole thing,
which is what it would have to fetch next anyway.

### What still gets through

```
PATCH /todos/1   {"done":"yes"}      →  200 {"id":1,"title":"Buy milk","done":"yes"}
PATCH /todos/1   {"title":""}        →  200 with an empty title
PATCH /todos/1   notjson             →  500
```

All three are wrong. The first two are the hole module 9 named — `any` at the
boundary, trusted: module 13 makes the type honest (a string `done` becomes a
400) and module 14 checks values and names the field (an empty title). The third
never becomes a value at all, and waits for module 16's `catch`. `changesFrom`'s
`data: any` is where 13 and 14 both start.
""",
    """
```bash
$ curl -s -X PATCH localhost:3000/todos/1 -d '{"done":true}'
{"id":1,"title":"Buy milk","done":true}

$ curl -s -X PATCH localhost:3000/todos/1 -d '{"title":"Buy oat milk"}'
{"id":1,"title":"Buy oat milk","done":true}

$ curl -s -i -X PATCH localhost:3000/todos/9 -d 'notjson'
HTTP/1.1 404 Not Found
```

Two changes that each left the other field alone, and a patch to nothing that
was answered honestly without its body ever being read.
""",
    pitfalls=[
        "Reading and parsing the body before the lookup. A junk body sent to a missing todo becomes a 500 — the server blaming itself for a request that was aimed at nothing.",
        "Answering with the patch instead of the updated todo. The client sent `{\"done\":true}` and learns nothing from having it handed back.",
        "Answering 204 because \"nothing needs saying\". The client usually wants the result — and module 12's 204 is for a resource that no longer exists to be described.",
        "Parsing the id again inside the route. `todoId` ran once at the top; `id` is already a number here.",
        "Forgetting the `return` after the 404. The rest of the route then runs against `undefined` — and `updateTodo` will not compile with it, which is the compiler catching this for you.",
    ],
    warmup=[
        _pq("`PATCH /todos/9 notjson` when there is no todo 9. What should the client get?",
            ["404 — the resource does not exist, so its body is irrelevant and never needs reading",
             "500, because the body is not JSON",
             "400, because the body is not JSON",
             "200 with an empty todo"],
            0,
            "Look up first. The most useful true thing to tell this client is that "
            "it is aiming at nothing."),
    ],
    exercises=[
        _pex("todo-m11-route-1", "The patch route",
             "Add the route. Find the todo (404 if it is missing), then read and "
             "parse the body, update the todo from it, and answer with the "
             "result.",
             _M11_FULL,
             _M11_PATCH_ROUTE,
             [("\n".join([_POST_A, 'PATCH /todos/1 {"done":true}',
                          'PATCH /todos/1 {"title":"Buy oat milk"}',
                          'PATCH /todos/1 {}', 'PATCH /todos/2 {"done":true}', "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "200 " + _TODO_A_DONE, "200 " + _TODO_A_OAT_DONE,
                          "200 " + _TODO_A_OAT_DONE, _NF, "200 [" + _TODO_A_OAT_DONE + "]"]))],
             ["The condition is `req.method === \"PATCH\" && id !== undefined`.",
              "First `findTodo(id)` and the 404 branch — before anything reads the body.",
              "Then module 9's two lines, `await readBody(req)` and `JSON.parse(body)`.",
              "`updateTodo(todo, changesFrom(data))`, then `send(res, 200, updated);` and `return;`.",
              "The fourth request is an empty patch: a 200, and nothing changes."]),
        _pfix("todo-m11-route-fix1", "A 500 for a todo that is not there",
              "Patching a todo that exists works. Patching one that does not, with "
              "a body that is not JSON, answers `500 {\"error\":\"server_error\"}` "
              "— the server blaming itself.\n\n"
              "It should be a 404, and the body should never have been read.",
              _m11(_M11_HANDLER.replace(
                  """    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data = JSON.parse(body);
    const updated""",
                  """    const body = await readBody(req);
    const data = JSON.parse(body);
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    const updated""")),
              _M11_FULL,
              [("\n".join([_POST_A, 'PATCH /todos/1 {"done":true}', "PATCH /todos/9 notjson"]),
                "\n".join(["201 " + _TODO_A, "200 " + _TODO_A_DONE, _NF]))],
              ["Which line throws on `notjson`? Does it need to run for a todo that does not exist?",
               "The body of a request to a missing resource is irrelevant.",
               "Move the lookup and its 404 above the read and the parse.",
               "`findTodo`, the 404 branch, *then* `readBody` and `JSON.parse`."],
              difficulty="Easy"),
        _pch("todo-m11-route-build", "The four-route router", "Medium",
             "Write the handler.\n\n"
             "* `GET /todos` → `200` with the array\n"
             "* `POST /todos` → `201` with the created todo\n"
             "* `GET /todos/:id` → `200` with the todo, or `404`\n"
             "* `PATCH /todos/:id` → `200` with the updated todo, or `404` — "
             "looked up before the body is read\n"
             "* anything else → `404`\n\n"
             "`todoId`, `changesFrom` and `updateTodo` are written above.",
             _M11_FULL,
             _M11_HANDLER.rstrip("\n"),
             [("\n".join([_POST_A, _POST_B, 'PATCH /todos/1 {"id":99,"done":true}',
                          "GET /todos/1", "GET /todos/99", "PATCH /todos/5 notjson", "GET /todos"]),
               "\n".join(["201 " + _TODO_A, "201 " + _TODO_B, "200 " + _TODO_A_DONE,
                          "200 " + _TODO_A_DONE, _NF, _NF,
                          "200 [" + _TODO_A_DONE + "," + _TODO_B + "]"]))],
             ["Module 10's handler, plus one route below the GET-one route.",
              "Both `:id` routes read the same `id` from the top of the handler.",
              "The third request tries to renumber todo 1 to 99. `changesFrom` has nowhere to put the 99.",
              "`PATCH /todos/5 notjson` must be a 404 — which means the lookup runs before `readBody`."]),
    ],
    quiz=[
        _pq("Module 9's write route was read, parse, store, answer. What does PATCH add, and where?",
            ["A lookup, in front — a missing todo is a 404 before anything reads the body",
             "A validation step between parse and store",
             "A second parse",
             "Nothing; it is the same four lines"],
            0,
            "Module 14 will add the other insertion — a check between parse and "
            "store. The shape never changes; it only gains steps."),
        _pq("A PATCH of `{\"done\":true}` succeeds. What does the response body contain?",
            ["The whole todo as it now is — id, title and done",
             "`{\"done\":true}`, the patch that was applied",
             "Nothing; it is a 204",
             "`{\"ok\":true}`"],
            0,
            "The client sent a fragment and gets back the whole resource, which "
            "is what it would otherwise have to fetch next."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M11_BUILD_BLANK = "\n\n".join(p.rstrip("\n") for p in (_M11_CHANGES, _M11_UPDATE, _M11_HANDLER))

_M11_FINAL = _pch(
    "todo-m11-build", "Module 11 build — a todo can change", "Medium",
    "Write `changesFrom`, `updateTodo` and the handler.\n\n"
    "* `changesFrom(data)` — a `Partial<Todo>` holding `title` and `done`, each "
    "only if the body sent it, and nothing else\n"
    "* `updateTodo(todo, changes)` — a new todo with the changes on top, swapped "
    "into the store, and returned\n"
    "* the handler — module 10's three routes plus `PATCH /todos/:id`, which "
    "looks the todo up *before* reading the body\n\n"
    "The requests tick a todo off, rename it, try to renumber it, send an empty "
    "patch, patch a todo that does not exist, and check the store agrees with "
    "every answer.",
    _M11_FULL,
    _M11_BUILD_BLANK,
    [("\n".join([_POST_A, _POST_B,
                 'PATCH /todos/1 {"done":true}',
                 'PATCH /todos/1 {"title":"Buy oat milk"}',
                 'PATCH /todos/1 {"id":7}',
                 'PATCH /todos/2 {}',
                 'PATCH /todos/3 {"done":true}',
                 "GET /todos"]),
      "\n".join(["201 " + _TODO_A, "201 " + _TODO_B,
                 "200 " + _TODO_A_DONE,
                 "200 " + _TODO_A_OAT_DONE,
                 "200 " + _TODO_A_OAT_DONE,
                 "200 " + _TODO_B,
                 _NF,
                 "200 [" + _TODO_A_OAT_DONE + "," + _TODO_B + "]"]))],
    ["`changesFrom` starts from `{}` typed `Partial<Todo>`, and copies each of the two fields only when it is not `undefined`.",
     "`updateTodo` is `{ ...todo, ...changes }` — changes last — then `indexOf` and a write into that slot.",
     "The rename in the fourth request must keep `done: true` from the third. An explicit `undefined` in the patch would erase it.",
     "`{\"id\":7}` is ignored: the answer is todo 1, unchanged.",
     "The last request is the one that proves every patch was stored, not just answered."],
)


_TODO_MODULES.append(_pmod(
    key="todo-update", number=11, phase="crud",
    title="PATCH /todos/:id — partial update",
    what="Partial<T>, object spread, and a patch built from the fields you allow",
    goal="Change a todo's title or done flag without touching anything else about it.",
    why=_M11_WHY,
    est_minutes=55,
    builds_on=["todo-store", "todo-create", "todo-one"],
    concepts=["Partial<T>", "object spread", "later key wins", "absent vs undefined",
              "replace, don't mutate", "indexOf", "lookup before read"],
    deliverable="A todo that can be ticked off and renamed — changing only what the "
                "client named, and only the fields a client may change.",
    objectives=[
        "Say why a PATCH body is not a `Todo`, and type it as `Partial<Todo>`",
        "Build a patch from named fields, and explain why that — not the type — keeps a client's id out",
        "Apply a patch with object spread, and predict the result when the two spreads are swapped",
        "Explain the difference between a field that is absent and one that is `undefined`, and which one erases a title",
        "Replace a todo in the store with `indexOf`, and say why a new object is safer than an edited one",
        "Put the lookup before the body read, and name the request that turns a 404 into a 500 when you don't",
    ],
    endpoints=[
        _pep("PATCH", "/todos/:id", "Change title and/or done", '{"done":true}',
             "Todo, as it now is", "200 · 404"),
        _pep("GET", "/todos/:id", "Fetch one todo", "", "Todo", "200 · 404"),
        _pep("*", "anything else", "Fall through", "", '{"error":"not_found"}', "404"),
    ],
    brief=_M11_BRIEF,
    syntax=_M11_SYNTAX,
    steps=[_M11_S1, _M11_S2, _M11_S3, _M11_S4],
    final_build=_M11_FINAL,
    acceptance=[
        "`curl -s -X PATCH localhost:3000/todos/1 -d '{\"done\":true}'` returns 200 and the todo with `done: true` and its title unchanged.",
        "`curl -s -X PATCH localhost:3000/todos/1 -d '{\"title\":\"New\"}'` changes the title and leaves `done` as it was.",
        "`curl -s localhost:3000/todos/1` after a PATCH shows the change — the store agrees with the response.",
        "`curl -s -X PATCH localhost:3000/todos/1 -d '{\"id\":99}'` returns todo 1, still id 1.",
        "`curl -s -X PATCH localhost:3000/todos/1 -d '{}'` returns 200 and the todo unchanged.",
        "`curl -s -i -X PATCH localhost:3000/todos/99 -d 'notjson'` returns 404, not 500 — the lookup runs before the body is read.",
        "`changesFrom` names the two fields it copies; nothing spreads the parsed body directly.",
    ],
    manual_test="""
With `node server.ts` running:

```bash
curl -s -X POST localhost:3000/todos -d '{"title":"Buy milk"}'

curl -s -X PATCH localhost:3000/todos/1 -d '{"done":true}'            # ticked off
curl -s -X PATCH localhost:3000/todos/1 -d '{"title":"Buy oat milk"}' # renamed; still done
curl -s -X PATCH localhost:3000/todos/1 -d '{"done":false}'           # un-ticked — false is a value
curl -s localhost:3000/todos/1                                        # the store agrees

# fields that are not the client's to change
curl -s -X PATCH localhost:3000/todos/1 -d '{"id":99,"isAdmin":true}' # todo 1, unchanged

# a patch to nothing, with a body nobody should read
curl -s -i -X PATCH localhost:3000/todos/42 -d 'notjson'              # 404, not 500
```

Then the three this module still gets wrong — all `any`, all module 13 and 14's:

```bash
curl -s -X PATCH localhost:3000/todos/1 -d '{"done":"yes"}'   # done is now the string "yes"
curl -s -X PATCH localhost:3000/todos/1 -d '{"title":""}'     # an empty title, accepted
curl -s -i -X PATCH localhost:3000/todos/1 -d 'notjson'       # 500 for a todo that does exist
```

Last, try the bug from step 2 on purpose. Change `changesFrom` to
`return { title: data.title, done: data.done };`, restart, and send
`{"done":true}`. Watch the title disappear from the response — and from the
store. Then put it back.
""",
    reference="""// server.ts — module 11
//
// A todo can change. A PATCH body is not a todo but a description of a change
// to one: `changesFrom` builds it from the two fields a client may touch, a
// spread applies it, and the result replaces the old todo in the store.
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

// REPLACE, DON'T MUTATE. Build the new todo, then swap it into the old one's
// slot. Same output as editing in place today; the difference is module 14's —
// a new object can be checked before it is stored, so a rejected patch leaves
// the store exactly as it was. `indexOf` because we hold the object itself.
function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };   // changes LAST: later keys win
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
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

// The patch a client may make: `title` and `done`, each only if it was sent.
//
// * Named fields, never the whole body — a client's `id` or `isAdmin` has
//   nowhere to go. Module 9's technique: ignore input by having no place for it.
// * Only when present. `{ title: data.title }` for a body with no title is a
//   patch with `title: undefined`, which WINS the spread and erases the title.
// * `data: any` is the honest type of what JSON.parse returned. Module 13
//   changes this one word to `unknown`, and every line below stops compiling.
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

  // LOOK UP, THEN READ. A patch aimed at a missing todo is a 404 whatever its
  // body says — read and parse first, and `notjson` to a missing todo becomes
  // a 500 that blames the server for a request aimed at nothing.
  if (req.method === "PATCH" && id !== undefined) {
    const todo = findTodo(id);
    if (todo === undefined) {
      send(res, 404, { error: "not_found" });
      return;
    }
    const body = await readBody(req);
    const data = JSON.parse(body);           // still `any` — module 13
    const updated = updateTodo(todo, changesFrom(data));
    send(res, 200, updated);                 // the whole todo, as it now is
    return;
  }

  send(res, 404, { error: "not_found" });
}

const server = createServer(handler);
server.listen(3000, "127.0.0.1", () => console.log("listening on 3000"));
""",
    stretch=[
        "Add `PUT /todos/:id`, which replaces the title and `done` together and treats a missing field as an error rather than \"leave it alone\". Then write two sentences on when a client would want each verb.",
        "Change `updateTodo` to edit the found todo in place instead of swapping in a new one. Every test still passes. Now write down exactly which line of module 14 would have to be different because of it.",
        "Belt and braces: make `updateTodo` build `{ ...todo, ...changes, id: todo.id }`. Explain why it changes nothing today, and what future mistake it would catch.",
        "Send `{\"done\":\"yes\"}` and then `GET /todos?done=true` in your head, module 17's way. What would a filter on `done === true` make of a todo whose `done` is a string?",
        "Add `POST /todos/:id/toggle` that flips `done`. It needs no body at all. Decide whether it is a better API than `PATCH {\"done\":true}`, and say for whom.",
    ],
    glossary=[
        _pgloss("PATCH", "The HTTP verb for \"change these fields, leave the rest alone\". Its body is a description of a change, not a resource."),
        _pgloss("PUT", "The verb for \"replace the whole thing with this\". A `PUT` of `{\"done\":true}` would ask for a todo with no title."),
        _pgloss("Partial<T>", "`T` with every field optional. The type of a patch — and it allows every field, `id` included."),
        _pgloss("object spread", "`{ ...a, ...b }` — a new object with `a`'s fields, then `b`'s on top. Later keys win."),
        _pgloss("absent vs undefined", "A key that is not there leaves a spread alone; a key that is there with `undefined` overwrites. `JSON.stringify` then drops it, and the field vanishes."),
        _pgloss("indexOf", "`array.indexOf(x)` — the position of that exact value, or `-1`. Compares identity for objects."),
        _pgloss("replace, don't mutate", "Build the new version and swap it in, rather than editing the stored one — so a change can be checked before anything is committed."),
    ],
    cheatsheet="""
```ts
// the patch: named fields, each only if sent
function changesFrom(data: any): Partial<Todo> {
  const changes: Partial<Todo> = {};
  if (data.title !== undefined) { changes.title = data.title; }
  if (data.done !== undefined) { changes.done = data.done; }
  return changes;
}

// apply and replace: new object, changes last, swapped into its slot
function updateTodo(todo: Todo, changes: Partial<Todo>): Todo {
  const updated: Todo = { ...todo, ...changes };
  const i = todos.indexOf(todo);
  todos[i] = updated;
  return updated;
}

// the route: look up, THEN read
if (req.method === "PATCH" && id !== undefined) {
  const todo = findTodo(id);
  if (todo === undefined) { send(res, 404, { error: "not_found" }); return; }
  const body = await readBody(req);
  const data = JSON.parse(body);
  send(res, 200, updateTodo(todo, changesFrom(data)));
  return;
}
```

| Body | Result | Why |
|---|---|---|
| `{"done":true}` | done changes, title kept | only `done` was in the patch |
| `{"title":"x"}` | title changes, done kept | only `title` was in the patch |
| `{}` | unchanged, 200 | an empty patch is a valid patch |
| `{"id":99}` | unchanged | `changesFrom` never copies `id` |
| to a missing todo, any body | 404 | looked up before the body is read |
| `{"done":"yes"}` | ⚠️ stored as a string | `any` → modules 13 and 14 |

| Symptom | Cause |
|---|---|
| every patch does nothing | `{ ...changes, ...todo }` — spread order reversed |
| title vanishes on a `done` patch | patch built as `{ title: data.title, … }` — explicit `undefined` |
| response right, next GET old | new todo built but never written into `todos` |
| client's id or extra fields stored | spread or assigned `data` directly |
| 500 patching a missing todo | body parsed before the lookup |
""",
    self_check=[
        "Can you say why a PATCH body is not a `Todo`, and what `Partial<Todo>` allows that `Todo` does not?",
        "Can you explain why `Partial<Todo>` does not keep a client's id out, and what does?",
        "Can you predict `{ ...todo, ...changes }` and `{ ...changes, ...todo }` for the same two objects?",
        "Can you explain why `{ title: data.title, done: data.done }` erases a title, and why the compiler does not catch it?",
        "Can you say what `updateTodo` does that a spread alone does not, and why a new object beats an edited one?",
        "Can you name the request that proves the lookup belongs before the body read?",
    ],
    review=[
        _pq("A client sends `PATCH /todos/1 {\"title\":\"x\"}`. With the buggy `changesFrom` that returns `{ title: data.title, done: data.done }`, what does the todo become?",
            ["`done` is erased — the patch has `done: undefined`, which wins the spread, and `JSON.stringify` drops it",
             "Only the title changes; `undefined` is ignored by spread",
             "A compile error",
             "The whole todo is replaced with `{\"title\":\"x\"}`"],
            0,
            "Absent leaves a field alone; present-and-undefined overwrites it. The "
            "type `Partial<Todo>` cannot tell the two apart."),
        _pq("Which line keeps a client from renumbering a todo with `PATCH {\"id\":99}`?",
            ["None needs to — `changesFrom` copies `title` and `done` by name, so the 99 is never put anywhere",
             "`Partial<Todo>`, which removes `id`",
             "An `if (data.id !== undefined)` that answers 400",
             "`updateTodo`, which refuses objects with an id"],
            0,
            "Module 9's technique again. The strongest check is the one that "
            "never has to run."),
        _pq("Why does `PATCH /todos/9 notjson` answer 404 rather than 500 in this module?",
            ["The route looks the todo up before reading the body, so `JSON.parse` never runs for a missing todo",
             "Because `changesFrom` catches the parse error",
             "Because the replayer rejects bad JSON",
             "Because 404 is always checked first by Node"],
            0,
            "The order of two lines decides whose fault the answer blames. Look "
            "up, then read."),
        _pq("`updateTodo` swaps a new object into the store instead of editing the old one. What does that buy, and when?",
            ["An all-or-nothing change — module 14 can check the new todo and refuse it before the store is touched",
             "Speed, today",
             "Nothing; it is style",
             "It lets two clients patch at the same time"],
            0,
            "Build, check, commit. Editing in place commits first and checks "
            "never."),
        _pq("`findTodo(id)` found the todo. Why is `todos.indexOf(todo)` the right way to find its position, rather than using `id - 1`?",
            ["Ids are not positions — they only line up until something is deleted, which is module 12",
             "`id - 1` does not compile",
             "`indexOf` is faster",
             "Positions start at 1"],
            0,
            "Todo 3 lives at index 2 today. Delete todo 1, and it lives at index "
            "1. The id never moves; the position does."),
        _pq("What is still wrong with `PATCH /todos/1 {\"done\":\"yes\"}`, and which module fixes it?",
            ["`done` is stored as the string `\"yes\"`, because `data` is `any` — module 13 makes the type honest and 14 rejects it with a 400",
             "Nothing; `\"yes\"` is truthy",
             "It is a 500 — module 16",
             "It is a 404 — module 10"],
            0,
            "The same hole module 9 named, now with a second route standing in it. "
            "`changesFrom`'s `data: any` is exactly where it gets closed."),
    ],
    milestone="A todo can change. A client can tick one off, rename it or un-tick "
              "it, touching only the fields it named and only the fields it may "
              "touch — and every answer is the todo as the store now holds it.",
))
