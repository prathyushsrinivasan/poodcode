# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Todo API · Module 18 — Sorting and pagination.
#
# exec()'d by tools/projects_track.py inside its namespace; appends one module
# to `_TODO_MODULES`. Reuses modules 10-17's program pieces.
#
# THE PROJECT'S ONE BREAKING CHANGE. `GET /todos` stops answering a bare array
# and answers `{"items":[…],"total":n}`. The roadmap asked that it be said
# loudly, with a paragraph about why envelopes exist; step 3 is that
# paragraph, and the contract row says it in the "Changed in" column.
#
# THREE PARAMETERS, ALL CHECKED THE MODULE-14 WAY. `?sort=oldest|newest|title`
# (default oldest — the store's own order, which is id order), `?limit=` 1-100
# (default 20) and `?offset=` 0 or more (default 0). Each bad one is a field
# error, all collected, in the same 400 as everything else. The plan said
# `?sort`; it did not say which values, and a small closed set of words beat the
# `-id` / `title` sign convention on one count: it needs no parsing to explain.
# The project brief's "newest first" is not the default — changing the ORDER
# as well as the SHAPE of the list in one module would be two breaking changes.
#
# `.sort` SORTS IN PLACE, and that is the module's best graded bug: when no
# filter was asked for, `items` IS the store, and `items.sort(…)` reorders it.
# Every later plain `GET /todos` — which relies on the store being in id order —
# then comes back in whatever order the last client asked for. `.slice()` first.
#
# OTHER GRADABLE BUGS: `slice(offset, limit)` rather than
# `slice(offset, offset + limit)` (page two is empty); `total` counted after the
# page is cut rather than before (every client's page count is wrong); and a
# limit with no ceiling (`?limit=1000000` accepted).
#
# `localeCompare` IS LOCALE-AWARE, which makes it the right tool and slightly
# awkward to grade: every title in the expected output starts with a capital
# letter, so no two are ordered differently by any locale Node ships.
# ---------------------------------------------------------------------------

_M18_SORT = """type Sort = "oldest" | "newest" | "title";

function sortTodos(items: Todo[], sort: Sort): Todo[] {
  if (sort === "newest") {
    return items.slice().sort((a, b) => b.id - a.id);
  }
  if (sort === "title") {
    return items.slice().sort((a, b) => a.title.localeCompare(b.title));
  }
  return items;
}
"""

_M18_LIST = """type Page = {
  items: Todo[];
  total: number;
};

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
"""

_M18_QUERY = """type ListQuery = {
  done: boolean | undefined;
  q: string | undefined;
  sort: Sort;
  limit: number;
  offset: number;
};

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
    query.sort = sort;
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
"""


def _m18(route=_M17_ROUTE, query=_M18_QUERY, sort=_M18_SORT, listtodos=_M18_LIST):
    """A module-18 server program: module 17's, answering a page in an envelope."""
    return _server_bare("\n\n".join(p.rstrip("\n") for p in
                                    (_M10_STORE, sort, listtodos, _M10_SEND, _M10_READBODY,
                                     _M10_IDTEXT, _M10_PARSEID, _M10_TODOID,
                                     _M11_UPDATE, _M12_DELETE, _M12_SENDEMPTY,
                                     _M13_OBJECT, _M14_FIELDERROR, _M14_TITLE, _M14_DONE,
                                     _M14_CREATE, _M14_CHANGES, query,
                                     _M16_APIERROR, _M16_REPLY, _M15_SENDERROR,
                                     route, _M16_PARSE, _M16_BOUNDARY) if p))


_M18_FULL = _m18()

# --- Step 1's plain program: three orders, and the store left alone ---------
_M18_S1_STORE = """type Todo = {
  id: number;
  title: string;
  done: boolean;
};

const todos: Todo[] = [
  { id: 1, title: "Write tests", done: false },
  { id: 2, title: "Buy milk", done: true },
  { id: 3, title: "Ship it", done: false },
  { id: 4, title: "Buy oat milk", done: false },
];

function titles(list: Todo[]): string {
  return JSON.stringify(list.map((t) => t.title));
}
"""

_M18_S1_PRINTS = """
console.log(titles(sortTodos(todos, "newest")));
console.log(titles(sortTodos(todos, "title")));
console.log(titles(sortTodos(todos, "oldest")));
console.log(titles(todos));
"""
_M18_S1_OUT = "\n".join([
    '["Buy oat milk","Ship it","Buy milk","Write tests"]',
    '["Buy milk","Buy oat milk","Ship it","Write tests"]',
    '["Write tests","Buy milk","Ship it","Buy oat milk"]',
    '["Write tests","Buy milk","Ship it","Buy oat milk"]',
])


def _m18_s1(sort=_M18_SORT):
    return _plain(_M18_S1_STORE.rstrip("\n") + "\n\n" + sort.rstrip("\n") + "\n" + _M18_S1_PRINTS)


# --- Step 2's plain program: page arithmetic --------------------------------
_M18_PAGEOF = """function pageOf(list: string[], offset: number, limit: number): string[] {
  return list.slice(offset, offset + limit);
}
"""

_M18_S2_PRINTS = """
const letters = ["a", "b", "c", "d", "e"];

console.log(JSON.stringify(pageOf(letters, 0, 2)));
console.log(JSON.stringify(pageOf(letters, 2, 2)));
console.log(JSON.stringify(pageOf(letters, 4, 2)));
console.log(JSON.stringify(pageOf(letters, 6, 2)));
console.log(JSON.stringify(pageOf(letters, 1, 3)));
console.log(JSON.stringify(pageOf(letters, 0, 20)));
console.log(JSON.stringify(letters));
"""
_M18_S2_OUT = "\n".join(['["a","b"]', '["c","d"]', '["e"]', "[]", '["b","c","d"]',
                         '["a","b","c","d","e"]', '["a","b","c","d","e"]'])


def _m18_s2(pageof=_M18_PAGEOF):
    return _plain(pageof.rstrip("\n") + "\n" + _M18_S2_PRINTS)


_TODO_SHIP4 = '{"id":4,"title":"Ship it","done":false}'
_M18_SETUP = _M17_SETUP + [_POST_C]
_M18_SETUP_OUT = _M17_SETUP_OUT + ["201 " + _TODO_SHIP4]


def _page(total, *todos):
    return '200 {"items":[' + ",".join(todos) + '],"total":%d}' % total


_FE_SORT = _fe("sort", "must be oldest, newest or title")
_FE_LIMIT = _fe("limit", "must be a whole number from 1 to 100")
_FE_OFFSET = _fe("offset", "must be a whole number, 0 or more")

_M18_WHY = (
    "The list can be filtered, but not ordered and not cut. A client that wants "
    "the latest ten todos downloads every one and sorts them itself; a client "
    "showing twenty at a time downloads all ten thousand to draw the first "
    "screen. And there is a question a filtered bare array cannot answer at all: "
    "*how many are there?* To say \"page 1 of 50\", a client needs a number the "
    "response has nowhere to put. `[…]` has no room for anything but todos."
)

_M18_BRIEF = """
### The whole module in one line

Let a client choose the order and ask for one page at a time — and tell it how
many there are altogether.

### Three more parameters

| Parameter | Values | Default |
|---|---|---|
| `sort` | `oldest` · `newest` · `title` | `oldest` — the order they were created |
| `limit` | a whole number, 1 to 100 | 20 |
| `offset` | a whole number, 0 or more | 0 |

```
GET /todos?done=false&sort=newest&limit=10&offset=20
```

*The unfinished todos, newest first, the third page of ten.* Filter, then sort,
then cut — in that order, always.

### The breaking change

```
GET /todos
[{"id":1,…},{"id":2,…}]                                   ← until now
{"items":[{"id":1,…},{"id":2,…}],"total":2}               ← from this module
```

Every client that read the list as an array breaks. It is the only such change
in the whole project, and step 3 is about why it is worth it.

### Two array methods, one trap

```ts
list.slice(2, 4)                   // a new array of elements 2 and 3
list.sort((a, b) => b.id - a.id)   // sorts `list` itself — and returns it
```

`slice` copies. `sort` does not — it rearranges the array you call it on. When
that array is the store, every client sees the new order.
"""

_M18_SYNTAX = [
    _syn(
        "items.slice().sort((a, b) => b.id - a.id)",
        "Sort a **copy**. `sort` rearranges the array it is called on; "
        "`slice()` with no arguments copies the whole array first.",
        """
const newest = todos.slice().sort((a, b) => b.id - a.id);
// todos is untouched; newest is a new, sorted array
""",
        "Unlike `filter` and `map`, `sort` changes the original — and returns "
        "it, so `const sorted = todos.sort(…)` looks like a copy and is not.",
    ),
    _syn(
        "(a, b) => b.id - a.id",
        "A **comparator**: negative means `a` comes first, positive means `b` "
        "does, zero means leave them as they are.",
        """
(a, b) => a.id - b.id    // smallest id first — oldest
(a, b) => b.id - a.id    // largest id first — newest
""",
        "Subtracting numbers gives exactly that sign. Swap `a` and `b` to "
        "reverse the order.",
    ),
    _syn(
        "a.title.localeCompare(b.title)",
        "Compare two strings the way a person alphabetises — the comparator for "
        "text.",
        """
"Buy milk".localeCompare("Ship it");   // negative — B before S
"Ship it".localeCompare("Buy milk");   // positive
""",
        "`<` compares character codes, which sorts every capital before every "
        "lower-case letter. `localeCompare` does not.",
    ),
    _syn(
        "sorted.slice(query.offset, query.offset + query.limit)",
        "Elements from position `offset` up to — but not including — "
        "`offset + limit`. A page.",
        """
["a", "b", "c", "d", "e"].slice(2, 4);    // ["c", "d"]
["a", "b", "c", "d", "e"].slice(4, 6);    // ["e"]  — no error past the end
""",
        "The second argument is where to **stop**, not how many to take.",
    ),
    _syn(
        'type Sort = "oldest" | "newest" | "title";',
        "A union of literal types — module 15's idea without objects. Exactly "
        "three strings are a `Sort`.",
        """
const s: Sort = "newest";      // fine
const t: Sort = "random";      // error
""",
        "`sort === \"oldest\" || sort === \"newest\" || sort === \"title\"` narrows "
        "a `string` to it.",
    ),
    _syn(
        "return { items: page, total: sorted.length };",
        "The **envelope**: the page of todos, and how many there are before the "
        "page was cut.",
        "",
        "`total` counts the filtered list, not the page and not the store.",
    ),
    _syn(
        "items.filter((t) => t.done === query.done)",
        "Module 17's filter — which, unlike `sort`, never touches the array it is "
        "called on.",
        "",
        "",
        recap=True,
    ),
]


# ---------------------------------------------------------------------------
# Step 1 — sort, and the array it sorts.
# ---------------------------------------------------------------------------

_M18_S1 = _pstep(
    "sort", "Sort — a copy",
    "Comparators, `localeCompare`, and the one array method that changes the array.",
    """
`sort` puts an array in order. You tell it *what* order with a **comparator** —
a function that looks at two elements and says which comes first:

```ts
(a, b) => a.id - b.id      // negative: a first · positive: b first · 0: as they are
```

Subtracting ids gives exactly the right sign. Smallest id first is **oldest
first**; swap the two and it is **newest first**:

```ts
(a, b) => b.id - a.id
```

Text needs a different comparator, because you cannot subtract strings:

```ts
(a, b) => a.title.localeCompare(b.title)
```

`localeCompare` compares the way a person alphabetises. (`a.title < b.title`
compares character codes, which puts every capital letter before every small
one — *Zebra* before *apple*.)

### The trap

`filter` and `map` build a new array and leave the old one alone. **`sort` does
not.** It rearranges the array you call it on — and then returns that same
array, so it *looks* like it made a new one:

```ts
const newest = todos.sort((a, b) => b.id - a.id);
newest === todos     // true. The store is now newest-first.
```

In `listTodos`, `items` *is* the store whenever no filter was asked for. Sort it
in place and every client — including ones that never mentioned `sort` — gets
whatever order the last client asked for. So copy first:

```ts
type Sort = "oldest" | "newest" | "title";

function sortTodos(items: Todo[], sort: Sort): Todo[] {
  if (sort === "newest") {
    return items.slice().sort((a, b) => b.id - a.id);
  }
  if (sort === "title") {
    return items.slice().sort((a, b) => a.title.localeCompare(b.title));
  }
  return items;
}
```

`slice()` with no arguments copies the whole array. `oldest` needs no sort at
all: the store has always been in id order — `push` adds to the end, `splice`
removes without reordering, `updateTodo` replaces in place — and that is an
**invariant** worth protecting, not re-deriving.
""",
    """
Against *Write tests* (1), *Buy milk* (2), *Ship it* (3), *Buy oat milk* (4):

```
newest    ["Buy oat milk","Ship it","Buy milk","Write tests"]
title     ["Buy milk","Buy oat milk","Ship it","Write tests"]
oldest    ["Write tests","Buy milk","Ship it","Buy oat milk"]
todos     ["Write tests","Buy milk","Ship it","Buy oat milk"]
```

The last two lines must match. If they come out in title order, a sort changed
the original.
""",
    pitfalls=[
        "Plain `GET /todos` comes back in the order the last client sorted by — `items.sort(…)` without `.slice()` sorted the store itself. Copy first.",
        "`const sorted = todos.sort(…)` looks like a copy. It is the same array, now reordered; `sort` returns what it sorted.",
        "Sorting titles with `<`. Every capital comes before every lower-case letter. Use `localeCompare`.",
        "A comparator that returns a boolean — `(a, b) => a.id > b.id`. `sort` needs negative, zero or positive; `true`/`false` gives an order that depends on the engine.",
        "Sorting `oldest` by id every time. It works, and it hides a broken invariant — if the store were ever out of order, you would want to know.",
    ],
    warmup=[
        _pq("After `const s = todos.sort((a, b) => b.id - a.id);`, what is true?",
            ["`s` and `todos` are the same array, and it is now newest-first",
             "`s` is a sorted copy; `todos` is unchanged",
             "`todos` is empty",
             "`s` is `undefined`"],
            0,
            "`sort` works in place and returns its own array. That is what makes it "
            "dangerous on the store."),
    ],
    exercises=[
        _pex("todo-m18-sort-1", "Newest first",
             "Write the comparator that puts the largest id first.",
             _m18_s1(),
             "b.id - a.id",
             [("", _M18_S1_OUT)],
             ["Negative means `a` comes first.",
              "For the larger id to come first, subtract the other way round.",
              "`b.id - a.id`"]),
        _pfix("todo-m18-sort-fix1", "The sort that moved the store",
              "Sorting by `newest` and then by `title` works — and afterwards the "
              "original list is in title order too, and so is `oldest`.",
              _m18_s1(_M18_SORT.replace("items.slice().sort(", "items.sort(")),
              _m18_s1(),
              [("", _M18_S1_OUT)],
              ["Does `sort` build a new array, like `filter`?",
               "Which array is `items` when it is passed the whole list?",
               "Copy before sorting: `items.slice().sort(…)` — in both places."],
              difficulty="Easy"),
        _pex("todo-m18-sort-2", "Alphabetical",
             "Order two todos by title, the way a person would alphabetise them.",
             _m18_s1(),
             "a.title.localeCompare(b.title)",
             [("", _M18_S1_OUT)],
             ["Strings cannot be subtracted.",
              "There is a string method that answers negative, zero or positive.",
              "`a.title.localeCompare(b.title)`"]),
    ],
    quiz=[
        _pq("A comparator returns `-3` for `(a, b)`. What does `sort` do with them?",
            ["Puts `a` before `b` — any negative number means `a` first",
             "Puts `b` before `a`",
             "Moves `a` three places",
             "Leaves them as they are"],
            0,
            "Only the sign matters. That is why subtracting ids works."),
        _pq("Why does `sortTodos` return `items` untouched for `oldest`?",
            ["The store is always in id order — a kept invariant — so there is nothing to sort",
             "Because `oldest` cannot be sorted",
             "Because `slice` is slow",
             "It is a bug"],
            0,
            "And it is why sorting the store in place is a visible bug: it breaks "
            "the one order nobody sorts."),
    ],
)


# ---------------------------------------------------------------------------
# Step 2 — slice, and page arithmetic.
# ---------------------------------------------------------------------------

_M18_S2 = _pstep(
    "slice", "One page at a time",
    "`slice(start, end)`, `offset` and `limit`, and the page past the end.",
    """
A client showing twenty todos at a time does not want ten thousand. It asks for
one **page**:

* `limit` — how many at most
* `offset` — how many to skip first

```
offset 0, limit 2   →  a b
offset 2, limit 2   →  c d
offset 4, limit 2   →  e
offset 6, limit 2   →  (nothing)
```

### `slice(start, end)`

```ts
function pageOf(list: string[], offset: number, limit: number): string[] {
  return list.slice(offset, offset + limit);
}
```

`slice` returns a new array of the elements from `start` up to — **not
including** — `end`. The second argument is a *position to stop at*, not a
*count*. So a page is `slice(offset, offset + limit)`, and `slice(offset,
limit)` is a bug that happens to work on the first page (where `offset` is 0)
and nowhere else.

### Past the end is not an error

`["a","b","c","d","e"].slice(6, 8)` is `[]`. Asking for the fourth page of three
is not a mistake the client made — the list might have shrunk since it last
looked — and "no todos on that page" is a perfectly good answer. So an offset
past the end is a `200` with no items, not a 400.

### Like `filter`, `slice` copies

The list `slice` was called on is untouched. The trap in this module is `sort`,
not `slice`.

### Offset versus cursor

Offset paging is simple and has one known weakness: if a todo is added or
deleted while a client is paging, the pages shift under it, and one todo is seen
twice or never. Big APIs use a *cursor* — "the ones after id 40" — instead. For
this API, offsets are the right trade; the stretch goals try the other.
""",
    """
Your `pageOf` answers:

```
offset 0, limit 2     ["a","b"]
offset 2, limit 2     ["c","d"]
offset 4, limit 2     ["e"]
offset 6, limit 2     []
offset 1, limit 3     ["b","c","d"]
offset 0, limit 20    ["a","b","c","d","e"]
the list itself       ["a","b","c","d","e"]
```

If page two is empty, `slice` was given the limit as its end.
""",
    pitfalls=[
        "Page two is empty — `slice(offset, limit)`. The second argument is where to stop: `offset + limit`.",
        "An offset past the end answers 400. The list may have shrunk since the client last asked; an empty page is the right answer.",
        "Paging before filtering — cutting the store into pages and then filtering each one. Pages come out short and inconsistent. Filter, sort, then cut.",
        "Page numbers off by one: `?page=1` meaning the first page to one client and the second to another. Offsets have no such ambiguity — 0 is the start.",
    ],
    warmup=[
        _pq("`[\"a\",\"b\",\"c\",\"d\",\"e\"].slice(2, 4)` — what is it?",
            ["`[\"c\", \"d\"]` — from position 2 up to, not including, 4",
             "`[\"c\", \"d\", \"e\", \"f\"]` — four elements from 2",
             "`[\"b\", \"c\", \"d\"]`",
             "`[\"c\", \"d\", \"e\"]`"],
            0,
            "Start and stop, not start and count. Which is why the page's end is "
            "`offset + limit`."),
    ],
    exercises=[
        _pex("todo-m18-slice-1", "Where the page stops",
             "Return the page: skip `offset` elements and take at most `limit`.",
             _m18_s2(),
             "list.slice(offset, offset + limit)",
             [("", _M18_S2_OUT)],
             ["`slice` takes a start and an end position.",
              "The page ends `limit` elements after it starts.",
              "`list.slice(offset, offset + limit)`"]),
        _pfix("todo-m18-slice-fix1", "Page two is empty",
              "The first page is right. The second — offset 2, limit 2 — is `[]`, "
              "and so is every page after it.",
              _m18_s2(_M18_PAGEOF.replace("list.slice(offset, offset + limit)", "list.slice(offset, limit)")),
              _m18_s2(),
              [("", _M18_S2_OUT)],
              ["What does `slice`'s second argument mean?",
               "For offset 2, limit 2 the page should stop at position 4.",
               "`list.slice(offset, offset + limit)`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("A client asks for `offset=40&limit=20` and there are 45 todos. What comes back?",
            ["The last five, and a total of 45",
             "A 400 — the page is not full",
             "Twenty todos, wrapping round to the start",
             "An empty page"],
            0,
            "A short last page is normal. `total` lets the client see it was the "
            "last one."),
        _pq("Why is an offset past the end a 200 with no items rather than a 400?",
            ["The client asked a valid question whose answer happens to be empty — the list may have shrunk",
             "Because 400 is only for bodies",
             "It should be a 404",
             "Because `slice` cannot fail"],
            0,
            "Validation is about whether a question makes sense, not whether its "
            "answer is interesting."),
    ],
)


# ---------------------------------------------------------------------------
# Step 3 — the envelope.
# ---------------------------------------------------------------------------

_M18_S3_SCRIPT = "\n".join(_M18_SETUP + ["GET /todos", "GET /todos?limit=2", "GET /todos?limit=2&offset=2",
                                         "GET /todos?offset=4", "GET /todos?done=false&limit=1",
                                         "GET /todos?q=milk&limit=1&offset=1"])
_M18_S3_OUT = "\n".join(_M18_SETUP_OUT + [
    _page(4, _TODO_A, _TODO_B_DONE, _TODO_OAT3, _TODO_SHIP4),
    _page(4, _TODO_A, _TODO_B_DONE), _page(4, _TODO_OAT3, _TODO_SHIP4), _page(4),
    _page(3, _TODO_A), _page(2, _TODO_OAT3)])

_M18_S3 = _pstep(
    "envelope", "The envelope — and the one breaking change",
    "`{ items, total }`, why a list response should always have been an object, and what `total` counts.",
    """
Here is the change:

```
GET /todos?limit=2
[{"id":1,…},{"id":2,…}]                            ← what module 17 would send
{"items":[{"id":1,…},{"id":2,…}],"total":4}        ← what this module sends
```

The todos move inside an object, next to a number. Every client that did
`reply.length` or `reply[0]` is now broken — `reply.items.length` and
`reply.items[0]` are what they need. That is a **breaking change**: a change a
client has to be rewritten for. It is the only one in this project.

### Why the array had to go

A page of two todos cannot tell a client whether there are two todos or two
thousand. To draw *Page 1 of 2* — or to know whether to show a *Next* button — it
needs the **total**, and an array has nowhere to put it. Put it in a header?
Headers are easy to lose and awkward to read. Put a marker element in the array?
Now every consumer has to strip it out.

An object has room. And not only for this:

```json
{"items":[…],"total":4}
{"items":[…],"total":4,"next":"/todos?offset=2&limit=2"}    // one day
```

A field added to an object breaks nobody — clients ignore keys they do not know,
exactly as the server ignores parameters it does not know. So the envelope is
the **last** breaking change the list needs: every future addition fits in it.

That is the lesson worth keeping: *a collection response should be an object
from day one.* This project started with a bare array because module 7 had one
route and no reason to plan; most real APIs have a version of this module in
their history, and wish they did not.

### What `total` counts

```ts
function listTodos(query: ListQuery): Page {
  let items = todos;
  // …filters…
  const sorted = sortTodos(items, query.sort);
  const page = sorted.slice(query.offset, query.offset + query.limit);
  return { items: page, total: sorted.length };
}
```

The number of todos **matching the question** — after filtering, before cutting.
Not the store: `?done=false` with 3 unfinished of 4 has a total of 3. Not the
page: that is `items.length`, which the client can count itself. `total` is the
one number it cannot.

### The route did not change

```ts
send(res, 200, listTodos(query));
```

The same line as module 17 — `listTodos` now returns a `Page` instead of an
array, and `send` takes any object. A breaking change to every client, and a
one-type change to the server. That asymmetry is exactly why breaking changes
are easy to make by accident.
""",
    """
```bash
$ curl -s 'localhost:3000/todos?limit=2'
{"items":[{"id":1,…},{"id":2,…}],"total":4}

$ curl -s 'localhost:3000/todos?done=false&limit=1'
{"items":[{"id":1,…}],"total":3}
```

`total` is 3 in the second — the unfinished ones, not the whole store, and not
the page.
""",
    pitfalls=[
        "`total` always equals the number of items on the page — it was counted after `slice`. Count the filtered list before it is cut.",
        "`total` counting the whole store, ignoring filters. A client paging through `?done=false` would page past the end of what it asked for.",
        "Changing the list's shape without saying so. Every client breaks; the contract row marks it, and a real API would version it or announce it.",
        "Wrapping single-todo responses in an envelope too \"for consistency\". `GET /todos/1` is one todo and has nothing to count; changing it would be a second breaking change for no gain.",
        "Filtering after paging — `total` and the pages then disagree about what is being counted.",
    ],
    warmup=[
        _pq("4 todos, 3 unfinished. `GET /todos?done=false&limit=2` — what is `total`?",
            ["3 — the todos matching the question, before the page was cut",
             "2 — the todos on this page",
             "4 — every todo",
             "1 — the todos on the next page"],
            0,
            "The number the client cannot work out for itself."),
    ],
    exercises=[
        _pex("todo-m18-envelope-1", "The page in its envelope",
             "Return the page of todos, and how many matched before it was cut.",
             _M18_FULL,
             "return { items: page, total: sorted.length };",
             [(_M18_S3_SCRIPT, _M18_S3_OUT)],
             ["The response is an object with two keys, in the order `items`, `total`.",
              "`page` is what goes on this page; `sorted` is everything that matched.",
              "`return { items: page, total: sorted.length };`"]),
        _pfix("todo-m18-envelope-fix1", "Page 1 of 1, always",
              "`GET /todos?limit=2` with four todos answers `\"total\":2`. A client "
              "drawing page numbers thinks there is only one page.",
              _m18(listtodos=_M18_LIST.replace("total: sorted.length", "total: page.length")),
              _M18_FULL,
              [(_M18_S3_SCRIPT, _M18_S3_OUT)],
              ["What is `total` counting?",
               "The client can count the page itself. What can it not count?",
               "`total: sorted.length`"],
              difficulty="Intro"),
    ],
    quiz=[
        _pq("Why is `{ items, total }` the *last* breaking change the list needs?",
            ["New fields can be added to an object without breaking clients, which ignore keys they do not know",
             "Because arrays are deprecated",
             "Because `total` covers every future need",
             "It is not; more will follow"],
            0,
            "An array is closed; an object is open. That is the whole argument for "
            "envelopes."),
        _pq("The route line `send(res, 200, listTodos(query))` did not change. Why is this still a breaking change?",
            ["What goes over the wire changed shape — clients read the wire, not your code",
             "It is not breaking",
             "Because the status changed",
             "Because `listTodos` was renamed"],
            0,
            "A one-type change on the server; a rewrite for every client. Which is "
            "why these are easy to make by accident."),
    ],
)


# ---------------------------------------------------------------------------
# Step 4 — checking sort, limit and offset.
# ---------------------------------------------------------------------------

_M18_S4_SCRIPT = "\n".join(_M18_SETUP + [
    "GET /todos?sort=newest&limit=2", "GET /todos?sort=title", "GET /todos",
    "GET /todos?sort=oldest&offset=3", "GET /todos?sort=random", "GET /todos?limit=0",
    "GET /todos?limit=101", "GET /todos?limit=100&done=true", "GET /todos?limit=2.5",
    "GET /todos?offset=-1", "GET /todos?done=maybe&limit=abc&offset=x"])
_M18_S4_OUT = "\n".join(_M18_SETUP_OUT + [
    _page(4, _TODO_SHIP4, _TODO_OAT3),
    _page(4, _TODO_A, _TODO_OAT3, _TODO_SHIP4, _TODO_B_DONE),
    _page(4, _TODO_A, _TODO_B_DONE, _TODO_OAT3, _TODO_SHIP4),
    _page(4, _TODO_SHIP4),
    _v(_FE_SORT), _v(_FE_LIMIT), _v(_FE_LIMIT), _page(1, _TODO_B_DONE), _v(_FE_LIMIT),
    _v(_FE_OFFSET), _v(_FE_DONE, _FE_LIMIT, _FE_OFFSET)])

_M18_LIMIT_BLOCK = """  const limit = params.get("limit");
  if (limit !== null) {
    const n = Number(limit);
    if (Number.isInteger(n) && n >= 1 && n <= 100) {
      query.limit = n;
    } else {
      errors.push({ field: "limit", message: "must be a whole number from 1 to 100" });
    }
  }"""
assert _M18_QUERY.count(_M18_LIMIT_BLOCK) == 1

_M18_S4 = _pstep(
    "checks", "Three more questions, checked",
    "`sort`, `limit` and `offset` in `listQueryFrom` — defaults in one place, every error collected.",
    """
Three new parameters, three new ways to be wrong, and one familiar function to
put them in. The defaults go in the starting object, so an absent parameter
simply leaves its default alone:

```ts
const query: ListQuery = { done: undefined, q: undefined, sort: "oldest", limit: 20, offset: 0 };
```

### `sort` — one of three words

```ts
const sort = params.get("sort");
if (sort === "oldest" || sort === "newest" || sort === "title") {
  query.sort = sort;
} else if (sort !== null) {
  errors.push({ field: "sort", message: "must be oldest, newest or title" });
}
```

After the three comparisons the compiler has narrowed `sort` from `string` to
`"oldest" | "newest" | "title"` — exactly the `Sort` type — so the assignment
compiles. Try assigning it without the check and it will not.

### `limit` — a whole number, with a ceiling

```ts
const limit = params.get("limit");
if (limit !== null) {
  const n = Number(limit);
  if (Number.isInteger(n) && n >= 1 && n <= 100) {
    query.limit = n;
  } else {
    errors.push({ field: "limit", message: "must be a whole number from 1 to 100" });
  }
}
```

Module 10's `Number` and `Number.isInteger`, back again. The ceiling is the
point of the parameter: without it, `?limit=1000000` is the whole list in one
response — the very thing paging exists to prevent — and one client can make
the server build it as often as it likes.

`offset` is the same shape with no ceiling and a floor of 0.

### Every error, together

`?done=maybe&limit=abc&offset=x` is three mistakes, and the client hears about
all three in one 400 — module 14's rule, applied to a query string:

```json
{"error":"validation","fields":[
  {"field":"done","message":"must be true or false"},
  {"field":"limit","message":"must be a whole number from 1 to 100"},
  {"field":"offset","message":"must be a whole number, 0 or more"}]}
```

### Filter, sort, cut — in that order

Sorting before filtering does the same work on more todos. Cutting before
sorting gives the right number of todos from the wrong part of the list. There
is only one order in which all three are right.
""",
    """
```bash
$ curl -s 'localhost:3000/todos?sort=newest&limit=2'
{"items":[{"id":4,…},{"id":3,…}],"total":4}

$ curl -s 'localhost:3000/todos'
{"items":[{"id":1,…},{"id":2,…},{"id":3,…},{"id":4,…}],"total":4}

$ curl -s -i 'localhost:3000/todos?limit=1000'
HTTP/1.1 400 Bad Request
```

The second answer is in id order *after* someone asked for newest — the store
was not sorted in place.
""",
    pitfalls=[
        "`?limit=1000000` accepted — a limit with a floor and no ceiling. The whole list in one response is the thing paging exists to prevent.",
        "`query.sort = sort` without checking the value: it does not compile, since a `string` is not a `Sort`. Compare against each allowed word first.",
        "Returning at the first bad parameter. Three mistakes, one 400 naming all three.",
        "`?offset=` accepted as 0 surprises people. `Number(\"\")` is 0, module 10 said so, and 0 is the default anyway — harmless here, but know why.",
        "Treating `?limit=2.5` as 2. It is not a whole number, and rounding a client's input is guessing again.",
    ],
    warmup=[
        _pq("Why does `limit` need a maximum?",
            ["Without one, a single request can ask for the whole list — the load paging exists to prevent",
             "JSON cannot hold more than 100 items",
             "For the `total` to be right",
             "It does not"],
            0,
            "A parameter meant to make responses small is only as good as its "
            "ceiling."),
    ],
    exercises=[
        _pfix("todo-m18-checks-fix1", "No ceiling",
              "`GET /todos?limit=101` answers 200 with every todo. So would "
              "`?limit=1000000` with a million of them.",
              _m18(query=_M18_QUERY.replace("n >= 1 && n <= 100", "n >= 1")),
              _M18_FULL,
              [(_M18_S4_SCRIPT, _M18_S4_OUT)],
              ["What range does the error message promise?",
               "The check has a floor. Where is the ceiling?",
               "`Number.isInteger(n) && n >= 1 && n <= 100`"],
              difficulty="Intro"),
        _pch("todo-m18-checks-1", "Check the limit", "Easy",
             "Read `limit`. If it is present, it must be a whole number from 1 to "
             "100 — store it in `query.limit`, or collect `limit: must be a whole "
             "number from 1 to 100`.",
             _M18_FULL,
             _M18_LIMIT_BLOCK,
             [(_M18_S4_SCRIPT, _M18_S4_OUT)],
             ["`const limit = params.get(\"limit\");` — absent leaves the default.",
              "`const n = Number(limit);`",
              "`Number.isInteger(n) && n >= 1 && n <= 100`",
              "Otherwise `errors.push({ field: \"limit\", message: \"must be a whole number from 1 to 100\" });`"]),
        _pex("todo-m18-checks-2", "One of three words",
             "Accept `sort` only if it is one of the three words the API knows.",
             _M18_FULL,
             'sort === "oldest" || sort === "newest" || sort === "title"',
             [(_M18_S4_SCRIPT, _M18_S4_OUT)],
             ["Compare with each allowed word.",
              "Any one of them will do.",
              '`sort === "oldest" || sort === "newest" || sort === "title"`']),
    ],
    quiz=[
        _pq("How does `query.sort = sort` compile, when `sort` came from a query string?",
            ["The three `===` comparisons narrowed `sort` from `string` to the three literal words",
             "`Sort` is just `string`",
             "Because of `as`",
             "It does not compile"],
            0,
            "Literal types and narrowing, exactly as module 15 used them for `kind`."),
        _pq("In what order must `listTodos` filter, sort and cut?",
            ["Filter, then sort, then cut — any other order gives the wrong todos or the wrong total",
             "Cut, then filter, then sort",
             "Sort, then cut, then filter",
             "Any order"],
            0,
            "Cutting has to be last, or the page is taken from the wrong list."),
    ],
)


# ---------------------------------------------------------------------------
# Module build.
# ---------------------------------------------------------------------------

_M18_FINAL = _pch(
    "todo-m18-build", "Module 18 build — a page, in order, with a total", "Hard",
    "Write `sortTodos`, the `Page` type and `listTodos`.\n\n"
    "* `sortTodos(items, sort)` — `newest` is largest id first, `title` is "
    "alphabetical; `oldest` is the order the store is already in. **Never** "
    "reorder the array you were given.\n"
    "* `Page` — `{ items: Todo[]; total: number }`\n"
    "* `listTodos(query)` — filter by `done` and `q` as in module 17, sort, then "
    "cut out the page at `offset`/`limit`; answer `{ items, total }`, where "
    "`total` counts every todo that matched\n\n"
    "`listQueryFrom`, with its defaults and checks, is further down.",
    _M18_FULL,
    _M18_SORT.split("\n\n", 1)[1].rstrip("\n") + "\n\n" + _M18_LIST.rstrip("\n"),
    [("\n".join(_M18_SETUP + [
        "GET /todos?sort=title&limit=3", "GET /todos?sort=newest&done=false",
        "GET /todos?q=milk&sort=newest", "GET /todos", "GET /todos?limit=1&offset=1&sort=title",
        'PATCH /todos/1 {"done":true}', "GET /todos?done=true&sort=newest", "DELETE /todos/3",
        "GET /todos?sort=title", "GET /todos?offset=10", "GET /todos?sort=size&limit=500"]),
      "\n".join(_M18_SETUP_OUT + [
          _page(4, _TODO_A, _TODO_OAT3, _TODO_SHIP4),
          _page(3, _TODO_SHIP4, _TODO_OAT3, _TODO_A),
          _page(2, _TODO_OAT3, _TODO_A),
          _page(4, _TODO_A, _TODO_B_DONE, _TODO_OAT3, _TODO_SHIP4),
          _page(4, _TODO_OAT3),
          "200 " + _TODO_A_DONE,
          _page(2, _TODO_B_DONE, _TODO_A_DONE),
          "204",
          _page(3, _TODO_A_DONE, _TODO_SHIP4, _TODO_B_DONE),
          _page(3),
          _v(_FE_SORT, _FE_LIMIT)]))],
    ["`sortTodos`: `items.slice().sort((a, b) => b.id - a.id)` for newest; `localeCompare` for title; `return items;` for oldest.",
     "`listTodos`: `let items = todos;` and module 17's two filters.",
     "`const sorted = sortTodos(items, query.sort);`",
     "`const page = sorted.slice(query.offset, query.offset + query.limit);`",
     "`return { items: page, total: sorted.length };` — and the fourth request, plain `GET /todos`, must still be in id order."],
)


_TODO_MODULES.append(_pmod(
    key="todo-page", number=18, phase="real",
    title="Sorting and pagination",
    what="?sort, ?limit, ?offset, and the envelope that makes paging usable",
    goal="Let a client choose the list's order and fetch it one page at a time, and answer with the page and the total in an envelope.",
    why=_M18_WHY,
    est_minutes=60,
    builds_on=["todo-filter"],
    concepts=["sort", "comparators", "localeCompare", "sorting in place", "slice",
              "offset and limit", "envelope", "breaking change", "literal union"],
    deliverable="`GET /todos?done=false&sort=newest&limit=10&offset=0` answers "
                "`{\"items\":[…],\"total\":n}` — and a plain `GET /todos` is still in "
                "id order, however the last client sorted.",
    objectives=[
        "Write a comparator for numbers and one for text, and reverse either",
        "Explain why `sort` on the store is a bug that other clients see, and prevent it with a copy",
        "Cut a page with `slice(offset, offset + limit)`, and say why a page past the end is not an error",
        "Answer a list in an envelope, and say what `total` counts and why a client needs it",
        "Explain what a breaking change is, why this one was worth making, and why a collection should be an object from the start",
        "Validate `sort`, `limit` and `offset` alongside `done`, collecting every error, with defaults in one place",
    ],
    endpoints=[
        _pep("GET", "/todos", "List todos — filter, search, sort and page",
             "?done&q&sort=newest&limit=20&offset=0", '{"items":[Todo],"total":n}', "200 · 400"),
        _pep("*", "anything else", "Fall through — through `sendError`, like every failure now",
             "", '{"error":"not_found"}', "404"),
    ],
    brief=_M18_BRIEF,
    syntax=_M18_SYNTAX,
    steps=[_M18_S1, _M18_S2, _M18_S3, _M18_S4],
    final_build=_M18_FINAL,
    acceptance=[
        "`curl -s localhost:3000/todos` answers `{\"items\":[…],\"total\":n}` — not a bare array.",
        "`curl -s 'localhost:3000/todos?sort=newest&limit=2'` answers the two newest todos and the full total.",
        "`curl -s 'localhost:3000/todos?sort=title'` answers the todos alphabetically by title.",
        "After any sorted request, `curl -s localhost:3000/todos` is still in id order.",
        "`curl -s 'localhost:3000/todos?offset=1000'` is a 200 with `\"items\":[]` and the real total.",
        "`curl -s 'localhost:3000/todos?done=false&limit=1'` has a `total` counting the unfinished todos, not the page and not the store.",
        "`?sort=random`, `?limit=0`, `?limit=101`, `?limit=2.5` and `?offset=-1` each answer 400 naming the parameter; several at once are named together.",
    ],
    manual_test="""
Make enough todos to page through:

```bash
for t in 'Write tests' 'Buy milk' 'Ship it' 'Buy oat milk' 'Call Sam'; do
  curl -s -X POST localhost:3000/todos -d "{\\"title\\":\\"$t\\"}" > /dev/null
done
curl -s -X PATCH localhost:3000/todos/2 -d '{"done":true}' > /dev/null
```

Walk it a page at a time, and watch `total` stay put while `items` moves:

```bash
curl -s 'localhost:3000/todos?limit=2'
curl -s 'localhost:3000/todos?limit=2&offset=2'
curl -s 'localhost:3000/todos?limit=2&offset=4'
curl -s 'localhost:3000/todos?limit=2&offset=6'     # empty page, same total
```

Order it, and then prove the store was not touched:

```bash
curl -s 'localhost:3000/todos?sort=newest'
curl -s 'localhost:3000/todos?sort=title'
curl -s 'localhost:3000/todos'                      # still id order
```

Combine everything:

```bash
curl -s 'localhost:3000/todos?done=false&q=buy&sort=title&limit=1'
```

And refuse the nonsense — all of it at once:

```bash
curl -s 'localhost:3000/todos?sort=size&limit=1000&offset=-5'
```

Last: find any code of your own that reads `GET /todos` — a script, a page — and
fix it for the envelope. That is what a breaking change costs.
""",
    reference="""// server.ts — module 18
//
// The list answers one page at a time, in the order asked for, inside an
// envelope: {"items":[…],"total":n}. That envelope is this project's one
// BREAKING change — every client that read the list as an array had to change —
// and it is the last the list will need, because an object has room for fields
// an array never did.
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
        "Add `\"next\"` to the envelope: the URL of the next page, or `null` on the last one. Notice that adding it breaks no client — the envelope earning its keep.",
        "Replace offsets with a cursor: `?after=40` returns todos with an id greater than 40. Delete a todo between two page requests and compare what each scheme shows. What does a cursor make impossible (hint: *jump to page 7*)?",
        "Sort by title with ties broken by id. `sort` is stable — equal titles keep the order they arrived in — so is the tie-break already there? Prove it with two todos called *Buy milk*.",
        "Support `?sort=-title` (descending) generally: a leading `-` reverses any sort. Is that nicer than a list of words? Which is easier to document, and to validate?",
        "Version the API instead of breaking it: serve the bare array at `/v1/todos` and the envelope at `/v2/todos`. How long would you keep v1, and how would you know when nobody uses it?",
    ],
    glossary=[
        _pgloss("comparator", "The function `sort` is given: negative if `a` comes first, positive if `b` does, zero if either."),
        _pgloss("sort in place", "`sort` rearranges the array it is called on and returns that same array — unlike `filter`, `map` and `slice`."),
        _pgloss("localeCompare", "Compares two strings as a person alphabetises. The comparator for text."),
        _pgloss("slice", "`list.slice(start, end)` — a new array from `start` up to, not including, `end`. With no arguments, a copy."),
        _pgloss("pagination", "Answering a list one page at a time — here, `offset` elements skipped and at most `limit` returned."),
        _pgloss("envelope", "An object wrapping a collection — `{ items, total }` — with room for facts about the list as well as its contents."),
        _pgloss("breaking change", "A change clients must be rewritten for. The envelope is this project's only one."),
        _pgloss("invariant", "Something the code keeps true at all times — here, that the store is in id order. Sorting it in place breaks it."),
    ],
    cheatsheet="""
```ts
// sort a COPY — sort rearranges the array it is called on, and returns it
items.slice().sort((a, b) => a.id - b.id)                   // oldest first
items.slice().sort((a, b) => b.id - a.id)                   // newest first
items.slice().sort((a, b) => a.title.localeCompare(b.title)) // A → Z

// a page: start, and where to STOP
sorted.slice(query.offset, query.offset + query.limit)

// filter → sort → cut; total counts what matched
const sorted = sortTodos(items, query.sort);
const page = sorted.slice(query.offset, query.offset + query.limit);
return { items: page, total: sorted.length };

// a literal union, narrowed from a string
type Sort = "oldest" | "newest" | "title";
if (sort === "oldest" || sort === "newest" || sort === "title") {
  query.sort = sort;
}
```

| Parameter | Allowed | Default | Refused |
|---|---|---|---|
| `sort` | `oldest` · `newest` · `title` | `oldest` | anything else |
| `limit` | whole, 1–100 | 20 | `0`, `101`, `2.5`, `abc` |
| `offset` | whole, 0 or more | 0 | `-1`, `x` — but past the end is fine |

| | `filter` · `map` · `slice` | `sort` |
|---|---|---|
| Returns | a new array | **the same array** |
| The original | untouched | **rearranged** |
""",
    self_check=[
        "Can you write a comparator for newest-first and one for alphabetical, and say what sign each returns?",
        "Can you explain why `items.sort(…)` in `listTodos` changes what *other* clients see — and when `items` is the store?",
        "Can you say what `slice`'s second argument means, and what `slice(offset, limit)` gets wrong?",
        "Can you say exactly what `total` counts, and why it is not `items.length`?",
        "Can you explain what makes the envelope a breaking change, and why it is the last one the list needs?",
        "Can you say why `limit` has a ceiling, and why an offset past the end is not an error?",
    ],
    review=[
        _pq("Which of these changes the array it is called on?",
            ["`sort`",
             "`filter`",
             "`map`",
             "`slice`"],
            0,
            "The odd one out — and it returns the array too, which disguises it."),
        _pq("`GET /todos?sort=title` followed by `GET /todos`. The second comes back in title order. Why?",
            ["The first sorted the store in place — with no filter, `items` was the store itself",
             "The server caches sorts",
             "`oldest` sorts by title",
             "The client sent `sort` twice"],
            0,
            "`slice()` before `sort()`. One copy, and the store keeps its order."),
        _pq("What does `[\"a\",\"b\",\"c\",\"d\",\"e\"].slice(2, 2)` return?",
            ["`[]` — start and stop are the same position",
             "`[\"c\", \"d\"]`",
             "`[\"c\"]`",
             "An error"],
            0,
            "Which is page two, if you wrote `slice(offset, limit)`."),
        _pq("`?done=false&limit=2`, and 3 of 4 todos are unfinished. What is `total`?",
            ["3", "2", "4", "1"],
            0,
            "Matched, before cutting. Not the page; not the store."),
        _pq("Why did the list change from `[…]` to `{ items, total }` — and why is that change worth its cost?",
            ["An array has no room for the total a pager needs; an object can grow new fields without breaking clients again",
             "Arrays are slower to serialise",
             "JSON requires objects at the top level",
             "For consistency with single todos"],
            0,
            "One break now, instead of one every time the list learns something new."),
        _pq("`?limit=1000000`. What should happen, and why?",
            ["400 naming `limit` — a limit with no ceiling lets one request ask for everything",
             "200 with everything",
             "200 with 100 todos, silently capped",
             "404"],
            0,
            "Silently capping is guessing. Refusing tells the client its question "
            "was outside what the API answers."),
    ],
    milestone="The list stays usable at any size: filtered, ordered, and served "
              "one page at a time with a total the client can build a pager "
              "from. It cost one breaking change — the last one the list will "
              "need.",
))
