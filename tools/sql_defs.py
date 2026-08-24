# -*- coding: utf-8 -*-
"""SQL track for the Learn section — joins and everything above them.

This file AUTHORS the SQL half of `seeds/concepts.json` plus the whole of
`seeds/sql_datasets.json`. It is `exec`'d by tools/gen_seed.py, which merges the
four dicts at the bottom (`SQL_CONCEPTS`, `SQL_CATEGORY`, `SQL_LESSONS`,
`SQL_EXERCISES`) into the catalog and writes the datasets out beside it.

Why this file computes instead of asserting
-------------------------------------------
Every expected output here is **computed**, never typed. `sq()` takes a dataset
and a reference query, runs the query through Python's SQLite, and renders the
result grid with `render_grid`. Those rendering rules are a byte-for-byte mirror
of `src-tauri/src/sqlexec.rs::render_value`, which is what lets the same expected
string be produced here and matched there.

That mirror is not taken on trust. `src-tauri/tests/verify_sql.rs` replays every
authored solution through the *real* Rust engine and asserts it is Accepted, so a
divergence between the two renderers — or between Python's SQLite and the 3.46
that ships with the app — fails the build instead of failing a learner.

Data conventions that keep the two engines in step
--------------------------------------------------
- **Money is always a multiple of 0.25.** Those are exactly representable in
  binary floating point, so `79.50 + 48.00` is exactly `127.5` on every machine
  and no expected output ever depends on float noise.
- **No REAL ever reaches exponent form.** `render_real` asserts it, because
  Python prints `1e+16` where Rust prints `10000000000000000`.
- **Every exercise pins a row order.** Result-set order is undefined without an
  `ORDER BY`, so each prompt names one; that is how real SQL is written anyway.
"""

import sqlite3

# The app bundles SQLite 3.46 (via rusqlite's `bundled` feature). Authoring
# against an older engine than the joins chapters need would fail with a bare
# syntax error deep inside a generated query, so fail here with the reason
# instead. 3.39 is the floor: it is the release that added RIGHT and FULL OUTER
# JOIN, without which the outer-join chapter cannot be written at all.
_MIN_SQLITE = (3, 39, 0)
_HAVE_SQLITE = tuple(int(p) for p in sqlite3.sqlite_version.split("."))
assert _HAVE_SQLITE >= _MIN_SQLITE, (
    f"the SQL track needs SQLite >= {'.'.join(map(str, _MIN_SQLITE))} to author "
    f"(RIGHT / FULL OUTER JOIN); this Python links SQLite {sqlite3.sqlite_version}"
)


# ---------------------------------------------------------------------------
# Rendering — the exact mirror of src-tauri/src/sqlexec.rs
# ---------------------------------------------------------------------------


def render_real(f):
    """Format a REAL so Python and Rust agree.

    Both languages emit the shortest decimal that round-trips, so they only
    disagree in two places: Rust drops the `.0` on whole numbers (fixed by
    appending it), and the two use different exponent notation (rejected here,
    because no dataset in this track needs numbers that large).
    """
    assert f == f, "NaN reached a result set — no exercise should produce one"
    assert f not in (float("inf"), float("-inf")), "infinity reached a result set"
    s = repr(f)
    assert "e" not in s and "E" not in s, (
        f"REAL {f!r} renders in exponent form; Rust would print it differently"
    )
    if "." not in s:
        s += ".0"
    return s


def render_value(v):
    """One SQLite value as the exact text `sqlexec::render_value` produces."""
    if v is None:
        return "NULL"
    if isinstance(v, bytes):
        return "X'" + v.hex().upper() + "'"
    if isinstance(v, bool):  # sqlite3 never returns these, but be explicit
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return render_real(v)
    return str(v).replace("\r", "").replace("\n", "\\n")


def render_grid(columns, rows):
    """Header line, then one line per row, cells joined by ' | '."""
    out = [" | ".join(columns)]
    for r in rows:
        out.append(" | ".join(render_value(v) for v in r))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Executing authored SQL the same way the app does
# ---------------------------------------------------------------------------


def split_statements(sql):
    """Split a batch into complete statements.

    Splitting on bare `;` would cut a semicolon inside a string literal in half;
    `sqlite3.complete_statement` knows where literals and comments end, so
    re-joining fragments until it reports a complete statement is safe.
    """
    out, buf = [], ""
    for part in sql.split(";"):
        buf += part + ";"
        if sqlite3.complete_statement(buf):
            s = buf.strip()
            if s not in ("", ";"):
                out.append(s)
            buf = ""
    tail = buf.strip().rstrip(";").strip()
    if tail:
        out.append(tail)
    return out


def run_sql(setup, sql):
    """Run `sql` against a fresh database built from `setup`; return the grid.

    Mirrors `sqlexec::run`: every statement executes in order and the last one
    that returns rows is the output.
    """
    con = sqlite3.connect(":memory:")
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(setup)
        cur = con.cursor()
        grid = None
        for stmt in split_statements(sql):
            cur.execute(stmt)
            if cur.description is not None:
                cols = [d[0] for d in cur.description]
                grid = (cols, cur.fetchall())
        assert grid is not None, f"no statement returned a result set:\n{sql}"
        return render_grid(*grid)
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Datasets — the databases every exercise queries.
#
# Each is replayed into a brand-new in-memory database before every single run,
# so nothing an exercise does can leak into the next one. They are deliberately
# small enough to read end to end: you cannot learn joins from data you cannot
# see, and every "surprise" an outer join can produce is planted in here on
# purpose (an owner with no pet, a pet with no owner, a customer who never
# ordered, a category with no products, an order with no lines, a NULL city).
# ---------------------------------------------------------------------------

DATASETS = {}


def dataset(key, title, summary, story, sql):
    sql = sql.strip() + "\n"
    # Prove the dataset actually builds before anything tries to query it.
    con = sqlite3.connect(":memory:")
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(sql)
    finally:
        con.close()
    DATASETS[key] = {
        "key": key,
        "title": title,
        "summary": summary,
        "story": story.strip(),
        "sql": sql,
    }


dataset(
    "pets",
    "pets — the join laboratory",
    "Four owners, five pets. Small enough to count every row a join produces by hand.",
    """
Two tables, nine rows, and every outer-join surprise planted on purpose:

- **`owners`** — `Dane` owns **no pet**. He is the row an `INNER JOIN` throws away
  and a `LEFT JOIN` keeps.
- **`pets`** — `Rex` has `owner_id IS NULL`: a stray. He is the row a
  `RIGHT JOIN` keeps and an ordinary `LEFT JOIN owners→pets` never shows you.

So on `owners LEFT JOIN pets` you get **5** rows, on `pets LEFT JOIN owners` you
get **5**, on `INNER JOIN` you get **4**, on `FULL OUTER JOIN` you get **6**, and
on `CROSS JOIN` you get **4 × 5 = 20**. Being able to predict those five numbers
before you run anything is most of what "understanding joins" means.
""",
    """
CREATE TABLE owners (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT
);
CREATE TABLE pets (
  id       INTEGER PRIMARY KEY,
  name     TEXT NOT NULL,
  species  TEXT NOT NULL,
  owner_id INTEGER REFERENCES owners(id)
);
INSERT INTO owners (id, name, city) VALUES
  (1, 'Ana',  'Lisbon'),
  (2, 'Ben',  'Porto'),
  (3, 'Cleo', 'Lisbon'),
  (4, 'Dane', 'Braga');
INSERT INTO pets (id, name, species, owner_id) VALUES
  (1, 'Milo', 'cat',  1),
  (2, 'Nala', 'cat',  1),
  (3, 'Otto', 'dog',  2),
  (4, 'Pip',  'bird', 3),
  (5, 'Rex',  'dog',  NULL);
""",
)


dataset(
    "shop",
    "shop — a small online store",
    "Customers, orders, order lines, products and categories: the classic five-table shape.",
    """
The workhorse of this track — a normalised store, five tables deep:

```
categories ──< products ──< order_items >── orders >── customers
                                                          │
                                                          └─< (referred_by, self-reference)
```

Read `──<` as "one row here, many rows there". `order_items` is a **junction**:
one row per *line* of an order, so an order with three products is three rows.
That single fact is behind most wrong SQL people write, and several exercises
here exist purely to make you meet it.

Planted on purpose:

- **`Farid` and `Hugo` have never ordered** — the anti-join targets.
- **Order 113 has no lines** — an order created and abandoned.
- **`Hose` and `Sun Hat` have never been ordered**; the **`Toys`** category has
  no products at all.
- **`Dara`'s `city` is `NULL`**, and most customers' `referred_by` is `NULL`.
- **Order 104 is `cancelled` and 106, 110, 113 are `pending`** — so "revenue"
  and "orders" mean different things depending on where you put the filter.
- **`order_items.unit_price` is the price *as charged*,** which is not always
  `products.price`: prices move, invoices do not.
- Orders 108 and 112 both total exactly **90.00**, so ranking has a real tie in it.

Every money value is a multiple of 0.25, so the arithmetic here is exact.
""",
    """
CREATE TABLE categories (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE products (
  id           INTEGER PRIMARY KEY,
  name         TEXT NOT NULL,
  category_id  INTEGER REFERENCES categories(id),
  price        REAL NOT NULL,
  discontinued INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE customers (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  city        TEXT,
  signup_date TEXT NOT NULL,
  referred_by INTEGER REFERENCES customers(id)
);
CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  order_date  TEXT NOT NULL,
  status      TEXT NOT NULL,
  channel     TEXT NOT NULL
);
CREATE TABLE order_items (
  id         INTEGER PRIMARY KEY,
  order_id   INTEGER NOT NULL REFERENCES orders(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity   INTEGER NOT NULL,
  unit_price REAL NOT NULL
);

INSERT INTO categories (id, name) VALUES
  (1, 'Electronics'), (2, 'Kitchen'), (3, 'Books'), (4, 'Garden'), (5, 'Toys');

INSERT INTO products (id, name, category_id, price, discontinued) VALUES
  (1,  'Headphones',   1,  79.50, 0),
  (2,  'Laptop Stand', 1,  45.00, 0),
  (3,  'Webcam',       1, 120.00, 1),
  (4,  'Kettle',       2,  32.00, 0),
  (5,  'Chef Knife',   2,  88.25, 0),
  (6,  'SQL Basics',   3,  24.00, 0),
  (7,  'Deep Joins',   3,  31.50, 0),
  (8,  'Trowel',       4,  12.75, 0),
  (9,  'Hose',         4,  28.00, 0),
  (10, 'Sun Hat',      4,  15.00, 0);

INSERT INTO customers (id, name, city, signup_date, referred_by) VALUES
  (1, 'Ada',    'Lisbon', '2023-01-15', NULL),
  (2, 'Brahim', 'Porto',  '2023-02-02', 1),
  (3, 'Chen',   'Lisbon', '2023-02-20', 1),
  (4, 'Dara',   NULL,     '2023-03-05', NULL),
  (5, 'Elif',   'Braga',  '2023-05-11', 2),
  (6, 'Farid',  'Porto',  '2023-06-30', NULL),
  (7, 'Gita',   'Lisbon', '2023-07-19', 3),
  (8, 'Hugo',   'Braga',  '2023-09-01', NULL);

INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES
  (101, 1, '2023-03-01', 'shipped',   'web'),
  (102, 1, '2023-04-12', 'shipped',   'web'),
  (103, 2, '2023-03-15', 'shipped',   'app'),
  (104, 3, '2023-04-02', 'cancelled', 'web'),
  (105, 3, '2023-05-20', 'shipped',   'app'),
  (106, 4, '2023-06-01', 'pending',   'web'),
  (107, 5, '2023-06-15', 'shipped',   'app'),
  (108, 1, '2023-08-09', 'shipped',   'app'),
  (109, 7, '2023-09-05', 'shipped',   'web'),
  (110, 2, '2023-09-22', 'pending',   'web'),
  (111, 5, '2023-10-02', 'shipped',   'web'),
  (112, 3, '2023-10-18', 'shipped',   'app'),
  (113, 7, '2023-11-01', 'pending',   'web');

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES
  (1,  101, 1, 1,  79.50),
  (2,  101, 6, 2,  24.00),
  (3,  102, 4, 1,  32.00),
  (4,  102, 8, 2,  12.75),
  (5,  103, 2, 1,  45.00),
  (6,  103, 1, 1,  79.50),
  (7,  104, 5, 1,  88.25),
  (8,  105, 7, 1,  31.50),
  (9,  105, 6, 1,  24.00),
  (10, 106, 3, 1, 120.00),
  (11, 107, 5, 1,  88.25),
  (12, 107, 4, 1,  32.00),
  (13, 108, 2, 2,  45.00),
  (14, 109, 1, 1,  79.50),
  (15, 109, 7, 1,  31.50),
  (16, 110, 6, 3,  24.00),
  (17, 111, 5, 1,  88.25),
  (18, 111, 8, 1,  12.75),
  (19, 111, 6, 1,  24.00),
  (20, 112, 2, 2,  45.00);
""",
)


dataset(
    "hr",
    "hr — an org chart with salary bands",
    "Thirteen employees, four departments, four pay bands. Built for self-joins and range joins.",
    """
Three tables chosen so that each demands a *different* kind of join:

- **`employees`** carries `manager_id`, a foreign key **back into its own table**.
  Joining `employees` to `employees` is the only way to put a person next to
  their manager. `Rita` (the CEO) has `manager_id IS NULL`, so an inner self-join
  drops her and a left self-join keeps her.
- **`departments`** has **`Research`, which employs nobody**, and `Dov` the
  recruiter has **`dept_id IS NULL`** — one gap in each direction.
- **`salary_bands`** has no key in common with `employees` at all. You join it
  with `salary BETWEEN min_salary AND max_salary` — a **non-equi join**, and the
  clearest proof that `ON` takes any boolean condition, not just `a.x = b.y`.

Two more things were planted deliberately. `Ugo` and `Vera` are both on 142000,
so ranking within Engineering has a real tie in it. And `Yara`, an account
executive on commission, **out-earns `Toma`, her own VP** — the one row that makes
"paid more than their manager" return something.

The reporting chain is four levels deep (`Rita → Sami → Ugo → Wren`), which is
exactly what a recursive CTE is for.
""",
    """
CREATE TABLE departments (
  id     INTEGER PRIMARY KEY,
  name   TEXT NOT NULL,
  budget INTEGER NOT NULL
);
CREATE TABLE employees (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL,
  title      TEXT NOT NULL,
  dept_id    INTEGER REFERENCES departments(id),
  manager_id INTEGER REFERENCES employees(id),
  salary     INTEGER NOT NULL,
  hired_on   TEXT NOT NULL
);
CREATE TABLE salary_bands (
  band       TEXT PRIMARY KEY,
  min_salary INTEGER NOT NULL,
  max_salary INTEGER NOT NULL
);

INSERT INTO departments (id, name, budget) VALUES
  (1, 'Engineering', 900000),
  (2, 'Sales',       400000),
  (3, 'Support',     250000),
  (4, 'Research',    150000);

INSERT INTO employees (id, name, title, dept_id, manager_id, salary, hired_on) VALUES
  (1,  'Rita', 'CEO',               NULL, NULL, 210000, '2018-01-08'),
  (2,  'Sami', 'VP Engineering',    1,    1,    175000, '2018-03-19'),
  (3,  'Toma', 'VP Sales',          2,    1,    165000, '2019-05-06'),
  (4,  'Ugo',  'Senior Engineer',   1,    2,    142000, '2019-09-02'),
  (5,  'Vera', 'Senior Engineer',   1,    2,    142000, '2020-02-17'),
  (6,  'Wren', 'Engineer',          1,    4,     98000, '2021-06-14'),
  (7,  'Xu',   'Engineer',          1,    4,     96000, '2021-11-01'),
  (8,  'Yara', 'Account Executive', 2,    3,    172000, '2020-08-24'),
  (9,  'Zeno', 'Account Executive', 2,    3,     91000, '2022-01-10'),
  (10, 'Ana',  'Support Lead',      3,    1,     88000, '2020-04-13'),
  (11, 'Bo',   'Support Agent',     3,    10,    61000, '2022-03-07'),
  (12, 'Cai',  'Support Agent',     3,    10,    59000, '2023-02-20'),
  (13, 'Dov',  'Recruiter',         NULL, 1,     72000, '2023-05-15');

INSERT INTO salary_bands (band, min_salary, max_salary) VALUES
  ('Junior', 0,      75000),
  ('Mid',    75001,  110000),
  ('Senior', 110001, 160000),
  ('Exec',   160001, 999999);
""",
)


dataset(
    "events",
    "events — sessions and page views",
    "Five users, twelve sessions, twenty page views, stamped with dates. Built for window functions.",
    """
A product-analytics shape, where almost every question is "compared to the
previous row" — which is what window functions answer:

- **`users`** — `eli` has **never started a session**.
- **`sessions`** — one row per visit. `ada` visits on **March 1, 2, 3, then 6 and
  7**: a deliberate gap, so *gaps-and-islands* has something to find. Session 11
  has **`ended_at IS NULL`** — still open, and a reminder that a duration
  calculation must decide what to do about that. Two pairs of sessions by
  *different* users **overlap in time** (1 with 6, and 3 with 9), which is what
  makes an interval-overlap join return anything.
- **`page_views`** — one row per page, with `ms_on_page`, for running totals and
  per-session shares.

Timestamps are stored as `TEXT` in `'YYYY-MM-DD HH:MM:SS'` form. That is not
laziness — in SQLite it is the recommended format precisely because it sorts and
compares correctly as plain text, and `julianday()` / `strftime()` read it
directly.
""",
    """
CREATE TABLE users (
  id         INTEGER PRIMARY KEY,
  email      TEXT NOT NULL,
  plan       TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE sessions (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id),
  started_at TEXT NOT NULL,
  ended_at   TEXT,
  device     TEXT NOT NULL
);
CREATE TABLE page_views (
  id          INTEGER PRIMARY KEY,
  session_id  INTEGER NOT NULL REFERENCES sessions(id),
  url         TEXT NOT NULL,
  viewed_at   TEXT NOT NULL,
  ms_on_page  INTEGER NOT NULL
);

INSERT INTO users (id, email, plan, created_at) VALUES
  (1, 'ada@example.com', 'pro',  '2024-01-04'),
  (2, 'bo@example.com',  'free', '2024-01-11'),
  (3, 'cyd@example.com', 'pro',  '2024-02-02'),
  (4, 'dee@example.com', 'team', '2024-02-19'),
  (5, 'eli@example.com', 'free', '2024-03-08');

INSERT INTO sessions (id, user_id, started_at, ended_at, device) VALUES
  (1,  1, '2024-03-01 09:00:00', '2024-03-01 09:25:00', 'desktop'),
  (2,  1, '2024-03-02 08:40:00', '2024-03-02 09:05:00', 'desktop'),
  (3,  1, '2024-03-03 20:10:00', '2024-03-03 20:35:00', 'mobile'),
  (4,  1, '2024-03-06 07:55:00', '2024-03-06 08:20:00', 'desktop'),
  (5,  1, '2024-03-07 19:30:00', '2024-03-07 19:45:00', 'mobile'),
  (6,  2, '2024-03-01 09:10:00', '2024-03-01 09:30:00', 'mobile'),
  (7,  2, '2024-03-05 12:00:00', '2024-03-05 12:30:00', 'mobile'),
  (8,  3, '2024-03-02 15:00:00', '2024-03-02 16:05:00', 'desktop'),
  (9,  3, '2024-03-03 20:15:00', '2024-03-03 20:40:00', 'desktop'),
  (10, 3, '2024-03-04 15:20:00', '2024-03-04 15:33:00', 'tablet'),
  (11, 4, '2024-03-04 10:00:00', NULL,                  'desktop'),
  (12, 4, '2024-03-08 10:00:00', '2024-03-08 10:45:00', 'desktop');

INSERT INTO page_views (id, session_id, url, viewed_at, ms_on_page) VALUES
  (1,  1,  '/home',     '2024-03-01 09:00:10', 12000),
  (2,  1,  '/pricing',  '2024-03-01 09:02:30', 45000),
  (3,  1,  '/docs',     '2024-03-01 09:10:00', 60000),
  (4,  2,  '/home',     '2024-03-02 08:40:20',  8000),
  (5,  2,  '/docs',     '2024-03-02 08:45:00', 90000),
  (6,  3,  '/blog',     '2024-03-03 20:11:00', 30000),
  (7,  4,  '/home',     '2024-03-06 07:55:30',  5000),
  (8,  4,  '/pricing',  '2024-03-06 08:00:00', 25000),
  (9,  4,  '/checkout', '2024-03-06 08:10:00', 40000),
  (10, 5,  '/blog',     '2024-03-07 19:31:00', 15000),
  (11, 6,  '/home',     '2024-03-01 09:11:00',  9000),
  (12, 7,  '/home',     '2024-03-05 12:01:00',  7000),
  (13, 7,  '/pricing',  '2024-03-05 12:05:00', 33000),
  (14, 8,  '/docs',     '2024-03-02 15:01:00', 75000),
  (15, 8,  '/docs',     '2024-03-02 15:20:00', 82000),
  (16, 9,  '/home',     '2024-03-03 20:16:00', 11000),
  (17, 10, '/blog',     '2024-03-04 15:21:00', 22000),
  (18, 11, '/home',     '2024-03-04 10:01:00', 14000),
  (19, 12, '/pricing',  '2024-03-08 10:02:00', 28000),
  (20, 12, '/checkout', '2024-03-08 10:20:00', 51000);
""",
)


dataset(
    "survey",
    "survey — a form nobody finished",
    "Five respondents, six responses, NULLs everywhere. Built for three-valued logic.",
    """
A deliberately gappy dataset, because the only way to learn what `NULL` does is
to work with data that is full of it:

- `q1_score` and `q2_score` are missing in different rows, so `COUNT(*)`,
  `COUNT(q1_score)` and `AVG(q1_score)` all disagree — correctly.
- Response 4 answered **nothing at all**.
- Response 5's `comment` is the **empty string**, response 2's is `NULL`. They
  look identical in most result grids and behave completely differently.
- `Chen`'s `segment` is `NULL`, which is what makes `NOT IN (SELECT segment …)`
  quietly return nothing.
- `Ada` responded **twice**, so "one row per respondent" needs a decision.
""",
    """
CREATE TABLE respondents (
  id      INTEGER PRIMARY KEY,
  name    TEXT NOT NULL,
  segment TEXT
);
CREATE TABLE responses (
  id            INTEGER PRIMARY KEY,
  respondent_id INTEGER NOT NULL REFERENCES respondents(id),
  q1_score      INTEGER,
  q2_score      INTEGER,
  comment       TEXT,
  submitted_at  TEXT NOT NULL
);

INSERT INTO respondents (id, name, segment) VALUES
  (1, 'Ada',    'enterprise'),
  (2, 'Brahim', 'smb'),
  (3, 'Chen',   NULL),
  (4, 'Dara',   'smb'),
  (5, 'Elif',   'enterprise');

INSERT INTO responses (id, respondent_id, q1_score, q2_score, comment, submitted_at) VALUES
  (1, 1, 9,    8,    'Great',        '2024-04-01'),
  (2, 2, NULL, 7,    NULL,           '2024-04-02'),
  (3, 3, 6,    NULL, 'Fine',         '2024-04-02'),
  (4, 4, NULL, NULL, NULL,           '2024-04-03'),
  (5, 5, 10,   9,    '',             '2024-04-04'),
  (6, 1, 7,    NULL, 'Second visit', '2024-05-10');
""",
)


# ---------------------------------------------------------------------------
# Exercise authoring
# ---------------------------------------------------------------------------

SQL_EXERCISES = {}
_SEEN_IDS = set()


def sq(eid, title, prompt, dataset_key, solution, blanks, variants=(), hint="",
       kind="drill", difficulty="", allow_empty=False):
    """Author one SQL exercise, computing its expected outputs.

    `solution` is the complete reference query. `blanks` are exact substrings of
    it to replace with `____` in the starter — for a drill that is the one clause
    the chapter teaches; for a challenge it is the whole query.

    `variants` are extra test cases: each is a snippet of SQL applied to the
    dataset *after* it is built and *before* the query runs, so the same answer is
    checked against changed data. A query that hard-codes `WHERE id = 3` instead
    of expressing the rule passes case 1 and fails case 2 — which is the point.
    """
    assert eid not in _SEEN_IDS, f"duplicate SQL exercise id {eid!r}"
    _SEEN_IDS.add(eid)
    ds = DATASETS[dataset_key]
    setup = ds["sql"]

    starter = solution
    for b in blanks:
        assert b in starter, f"{eid}: blank not found in the solution: {b!r}"
        starter = starter.replace(b, "____", 1)
    assert starter != solution, f"{eid}: no blank was applied"

    tests = []
    for delta in ("",) + tuple(variants):
        full_setup = setup if not delta else setup + "\n" + delta.strip() + "\n"
        tests.append({"input": delta, "output": run_sql(full_setup, solution)})

    # An empty result set is nearly always an authoring slip, so it has to be
    # asked for. The exception is an exercise whose *point* is that the answer is
    # currently "nothing" (proving a range table has no gaps, say) — there the
    # variants supply the data that makes it return rows, and at least one of
    # them must, or the exercise would pass for any query with the right header.
    non_empty = sum(1 for t in tests if "\n" in t["output"])
    if allow_empty:
        assert non_empty, f"{eid}: every case returns an empty result set"
    else:
        assert non_empty == len(tests), \
            f"{eid}: a case returns an empty result set (pass allow_empty=True if that is the lesson)"

    ex = {
        "id": eid,
        "title": title,
        "prompt": prompt,
        "hint": hint,
        "language": "sql",
        "kind": kind,
        "difficulty": difficulty,
        "starter": starter,
        "solution": solution,
        "tests": tests,
        "source_slug": "",
        "dataset": dataset_key,
    }
    return ex


def chal(eid, title, prompt, dataset_key, solution, variants=(), hint="",
         difficulty="Medium", allow_empty=False):
    """A challenge: the learner writes the whole query, so the blank is all of it."""
    return sq(eid, title, prompt, dataset_key, solution, [solution.strip()],
              variants=variants, hint=hint, kind="challenge", difficulty=difficulty,
              allow_empty=allow_empty)


# ---------------------------------------------------------------------------
# Concepts
# ---------------------------------------------------------------------------

SQL_CONCEPTS = {}
SQL_CATEGORY = {}
SQL_LESSONS = {}


def concept(key, category, name, what, deep, in_sql, lesson, quiz, exercises):
    SQL_CONCEPTS[key] = {
        "name": name,
        "what": what,
        "deep": deep,
        "java": in_sql,  # the catalog's "In <language>" slot
        "language": "sql",
        "quiz": quiz,
        "practice": [],
        "cards": [],
    }
    SQL_CATEGORY[key] = category
    SQL_LESSONS[key] = lesson.strip() + "\n"
    SQL_EXERCISES[key] = exercises
    for ex in exercises:
        assert ex["dataset"] in DATASETS, f"{ex['id']}: unknown dataset"


def q(question, options, answer, explanation):
    return {
        "question": question,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


# The Learn tab renders categories in the order declared in src/pages/Learn.tsx.
# Keeping the authoritative list here — and refusing to generate a chapter filed
# under anything else — is what stops a new chapter from silently landing at the
# bottom of the page under an unrecognised heading.
SQL_CATEGORY_ORDER = [
    "SQL: Join Foundations",
    "SQL: Aggregation",
    "SQL: Subqueries & CTEs",
    "SQL: Window Functions",
    "SQL: Sets & NULLs",
    "SQL: Performance",
]


def _check_sql():
    """Validate the assembled SQL syllabus before it is written out."""
    assert SQL_CONCEPTS, "the SQL track generated no chapters"
    for key, c in SQL_CONCEPTS.items():
        cat = SQL_CATEGORY[key]
        assert cat in SQL_CATEGORY_ORDER, f"{key}: unknown SQL category {cat!r}"
        assert SQL_LESSONS.get(key, "").strip(), f"{key}: empty lesson"
        assert len(c["quiz"]) >= 4, f"{key}: needs at least 4 quiz questions"
        exercises = SQL_EXERCISES.get(key, [])
        assert exercises, f"{key}: no exercises"
        drills = [e for e in exercises if e["kind"] != "challenge"]
        challenges = [e for e in exercises if e["kind"] == "challenge"]
        assert drills, f"{key}: no warm-up drills"
        assert challenges, f"{key}: no coding challenges"
        for e in exercises:
            # A multi-row answer with no ORDER BY would depend on the query plan.
            rows = max(t["output"].count("\n") for t in e["tests"])
            assert rows >= 1, f"{e['id']}: every expected result set is empty"
            if rows > 1:
                assert "ORDER BY" in e["solution"].upper(), \
                    f"{e['id']}: {rows} rows and no ORDER BY — the order is undefined"

    # Chapters are listed in the order they were authored; make sure that order
    # never interleaves categories, which would scatter a section across the page.
    seen, last = [], None
    for key in SQL_CONCEPTS:
        cat = SQL_CATEGORY[key]
        if cat != last:
            assert cat not in seen, f"category {cat!r} is split across the syllabus"
            seen.append(cat)
            last = cat
    assert seen == [c for c in SQL_CATEGORY_ORDER if c in seen], \
        f"chapters are authored out of category order: {seen}"

    n_ex = sum(len(v) for v in SQL_EXERCISES.values())
    n_q = sum(len(c["quiz"]) for c in SQL_CONCEPTS.values())
    print(f"  SQL track: {len(SQL_CONCEPTS)} chapters, {n_ex} exercises, "
          f"{n_q} quiz questions, {len(DATASETS)} datasets")
