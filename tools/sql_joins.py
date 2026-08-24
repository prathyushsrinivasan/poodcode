# -*- coding: utf-8 -*-
"""SQL track, chapters 1-8: joins, from the mechanism up to eight-table queries.

Exec'd by tools/gen_seed.py after tools/sql_defs.py, whose `concept`, `sq`,
`chal` and `q` helpers it uses. Every expected output in here is computed by
running the reference query — nothing is typed by hand.
"""

# ===========================================================================
# 1. How a join actually works
# ===========================================================================

concept(
    "sql_join_model",
    "SQL: Join Foundations",
    "How a Join Actually Works",
    "A join pairs rows from two tables and keeps the pairs a condition says to keep.",
    "Most people learn joins as four keywords to memorise, which is exactly why the keywords "
    "stop helping the moment a query goes wrong. There is one mechanism underneath all four: "
    "build every possible pairing of a left row with a right row, test each pairing against "
    "the ON condition, keep the ones that pass. An outer join adds a single extra step — any "
    "row on the preserved side that never found a partner is added back, padded with NULLs. "
    "Once you can see those steps, every join question collapses into the same two questions: "
    "which pairings do I want, and which lonely rows do I want to keep anyway?",
    """
A join is **three steps**, always in this order:

```
1. PAIR      every left row with every right row       (the cartesian product)
2. KEEP      only the pairs where ON is true           (the match)
3. ADD BACK  unmatched rows from the preserved side,
             padded with NULL                          (outer joins only)
```

Step 3 is the *only* thing separating `INNER`, `LEFT`, `RIGHT` and `FULL`. They
share steps 1 and 2 exactly.

```sql
-- The same query twice. The second one shows the machinery.
SELECT o.name, p.name FROM owners o JOIN pets p ON p.owner_id = o.id;
SELECT o.name, p.name FROM owners o, pets p WHERE p.owner_id = o.id;
```

No real database *builds* the cartesian product — it uses indexes and hash tables
to jump straight to the matches. But it always produces the answer that
definition describes, so reasoning this way is never wrong.
""",
    """
### Step 1 — pair everything

`owners` has 4 rows, `pets` has 5. Pair each with each and you get **20**. That
is a `CROSS JOIN`, and it is the raw material every other join is carved out of:

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o
CROSS JOIN pets p;          -- 4 x 5 = 20 rows
```

| owner | pet  |
|-------|------|
| Ana   | Milo |
| Ana   | Nala |
| Ana   | Otto |  ← nonsense, but it *is* a pairing
| ...   | ...  |

### Step 2 — keep the pairs that mean something

Of those 20 pairings, only the ones where the pet's `owner_id` equals the owner's
`id` describe reality. `ON` is that test:

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o
JOIN pets p ON p.owner_id = o.id;   -- 4 rows survive
```

| owner | pet  |
|-------|------|
| Ana   | Milo |
| Ana   | Nala |
| Ben   | Otto |
| Cleo  | Pip  |

Look at what already happened. **Ana appears twice** — she owns two pets, so she
takes part in two surviving pairs. A join does not "add columns to a table"; it
builds a **new table** whose row count you have to reason about. Meanwhile `Dane`
and `Rex` vanished entirely.

### Step 3 — decide who gets kept anyway

No pairing containing Dane passes the test. If you want him in the answer
regardless, declare his side **preserved**:

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o
LEFT JOIN pets p ON p.owner_id = o.id;   -- 5 rows
```

| owner | pet    |
|-------|--------|
| Ana   | Milo   |
| Ana   | Nala   |
| Ben   | Otto   |
| Cleo  | Pip    |
| Dane  | *NULL* |

Dane's row is padded: every column that would have come from `pets` is `NULL`.
Those NULLs are not missing data — they are the join saying *"no partner here"*,
and the next chapters turn that signal into a tool.

### `ON` is a condition, not a key list

`ON` accepts any boolean expression. Equality on a foreign key is merely the most
common one:

```sql
ON p.owner_id = o.id                                 -- equi-join, the usual case
ON p.owner_id = o.id AND p.species = 'cat'           -- extra condition, same step 2
ON e.salary BETWEEN b.min_salary AND b.max_salary    -- no key in sight at all
ON 1 = 1                                             -- true for every pair = CROSS JOIN
```

Sit with that last one. `JOIN ... ON 1=1` really is a cross join, because step 2
throws nothing away. There is no "key magic" in a join. There is only the
condition.

### Why the column list comes last

```sql
SELECT   o.name, p.name     -- 5th: pick columns
FROM     owners o           -- 1st: start here
JOIN     pets p ON ...      -- 2nd: pair + match
WHERE    ...                -- 3rd: filter the joined rows
GROUP BY ...                -- 4th: fold rows together
ORDER BY ...                -- 6th: sort
```

`SELECT` is written first and evaluated nearly last. When a join returns the
wrong *number of rows*, the `SELECT` list is never the culprit — `FROM` and `ON`
are. Debug from the top of the query downward, not from the left of the line
rightward.

### Ambiguity and aliases

Both tables have a `name` column, so bare `SELECT name` is an error. Two fixes,
one of them good:

```sql
SELECT o.name, p.name                    -- works, but both columns come back called "name"
SELECT o.name AS owner, p.name AS pet    -- do this
```

Short aliases (`owners o`, `pets p`) are not shorthand for the lazy. Once four
tables are in play, `o.id` / `p.id` / `oi.id` is the only thing keeping the query
readable.

### Watch out for

- **A join can multiply rows.** If the right side has *n* matches for a left row,
  that row comes back *n* times. This is the number-one cause of "my `SUM` is too
  big"; Chapter 9 is devoted to it.
- **A join can lose rows.** An inner join silently drops anything unmatched on
  *either* side. If a count went down when you added a join, that is why.
- **`JOIN` with no `ON` is a syntax error** in SQLite, but `,` with no `WHERE` is
  a cross join that runs happily and returns a million rows. Prefer explicit
  `JOIN ... ON` so the mistake cannot be silent.
""",
    [
        q("`owners` has 4 rows and `pets` has 5. How many rows does `FROM owners CROSS JOIN pets` return?",
          ["20", "9", "5", "4"], 0,
          "A cross join pairs every left row with every right row: 4 x 5 = 20. That is step 1 of every join."),
        q("What is the *only* difference between `INNER JOIN` and `LEFT JOIN`?",
          ["LEFT JOIN adds back left rows that found no match, padded with NULL",
           "LEFT JOIN reads the left table first",
           "LEFT JOIN allows conditions other than equality",
           "LEFT JOIN stops at the first match, so it is faster"], 0,
          "Both pair and match identically. LEFT JOIN then performs one extra step: unmatched left rows are re-added with NULL in every right-hand column."),
        q("How many rows does `FROM owners o JOIN pets p ON 1 = 1` return?",
          ["20 — the condition is true for every pair, so nothing is filtered out",
           "0 — `1 = 1` is not a valid join condition",
           "4 — it behaves like a normal key join",
           "It is a syntax error"], 0,
          "`ON` is just a boolean test applied to each pairing. A condition that is always true keeps all 20 pairings, which is exactly a cross join."),
        q("After `owners JOIN pets ON pets.owner_id = owners.id`, why does Ana appear twice?",
          ["She owns two pets, so two different pairings pass the ON test",
           "The join accidentally duplicated her row",
           "Because `owners.id` is not unique",
           "Because `pets` has more rows than `owners`"], 0,
          "A join builds a new table of surviving pairs. A left row with two matches takes part in two surviving pairs, so it appears twice. Nothing went wrong."),
        q("In `SELECT o.name, p.name FROM owners o JOIN pets p ON ...`, what are the output column names?",
          ["Both are called `name`, which is why you should alias them",
           "`o.name` and `p.name`",
           "`owners.name` and `pets.name`",
           "Selecting two columns with the same name is an error"], 0,
          "SQLite names each output column after its source column, so you get two columns both called `name`. Alias them (`AS owner`, `AS pet`) to keep the result readable."),
        q("A query returned *fewer* rows after you added a join. What is the most likely cause?",
          ["The join is inner, so rows with no match on the other side were dropped",
           "The database ran out of memory",
           "You forgot an `ORDER BY`",
           "Joins always reduce the row count"], 0,
          "An inner join keeps only matched pairs. Anything unmatched on either side vanishes — usually rows whose foreign key is NULL or points at something that no longer exists."),
    ],
    [
        sq("sql_join_model-cross", "Count every pairing",
           "Step 1 of every join is pairing each row on the left with each row on the right. "
           "Fill in the join type that does *only* that step, and report the number of pairings as `pairs`.",
           "pets",
           "SELECT COUNT(*) AS pairs\nFROM owners o\nCROSS JOIN pets p;",
           ["CROSS JOIN"],
           variants=("INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Suki', 'cat', 2);",),
           hint="4 owners x 5 pets. The keyword is two words, and it filters nothing at all."),
        sq("sql_join_model-filter", "A join is a filtered cross product",
           "This uses the old comma syntax, so right now it is a cross join returning 20 rows. "
           "Fill in the `WHERE` condition that cuts it down to the 4 real owner/pet pairs. "
           "Order by owner name, then pet name.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\nFROM owners o, pets p\nWHERE p.owner_id = o.id\nORDER BY o.name, p.name;",
           ["p.owner_id = o.id"],
           variants=("UPDATE pets SET owner_id = 3 WHERE name = 'Otto';",),
           hint="Keep a pairing when the pet's owner_id equals the owner's id."),
        sq("sql_join_model-on", "`ON` takes any condition",
           "`ON` is not a list of keys — it is a boolean test. Extend the condition so the join keeps "
           "only pairs where the pet is also a cat. Order by owner name, then pet name.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\nFROM owners o\nJOIN pets p ON p.owner_id = o.id AND p.species = 'cat'\nORDER BY o.name, p.name;",
           ["AND p.species = 'cat'"],
           variants=("UPDATE pets SET species = 'cat' WHERE name = 'Otto';",),
           hint="Add `AND` plus a comparison on p.species inside the same ON clause."),
        sq("sql_join_model-widen", "A join makes a wider row",
           "The join is already right; it produces rows carrying columns from *both* tables. "
           "Fill in the select list so each row shows the owner's name as `owner`, the pet's name as "
           "`pet`, and the pet's species as `species`. Order by owner, then pet.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet, p.species AS species\nFROM owners o\nJOIN pets p ON p.owner_id = o.id\nORDER BY o.name, p.name;",
           ["o.name AS owner, p.name AS pet, p.species AS species"],
           hint="Three items, each qualified with its table alias and renamed with AS."),
        sq("sql_join_model-multiply", "Watch a row multiply",
           "An inner join duplicates a left row once per match. Fill in the blank so the query reports, "
           "per owner, how many joined rows they produced, as `rows_produced`. Owners with no pets "
           "simply will not appear. Order by owner name.",
           "pets",
           "SELECT o.name AS owner, COUNT(*) AS rows_produced\nFROM owners o\nJOIN pets p ON p.owner_id = o.id\nGROUP BY o.id, o.name\nORDER BY o.name;",
           ["GROUP BY o.id, o.name"],
           variants=("INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Suki', 'cat', 2), (7, 'Tao', 'dog', 2);",),
           hint="Group by the owner. Grouping by id *and* name is the habit to build — names are not unique."),
        sq("sql_join_model-alwaystrue", "`ON 1 = 1` is a cross join",
           "Prove `ON` really is just a boolean test: fill in a condition that is true for every pairing, "
           "so this `JOIN` returns the full cartesian product as `pairs`.",
           "pets",
           "SELECT COUNT(*) AS pairs\nFROM owners o\nJOIN pets p ON 1 = 1;",
           ["1 = 1"],
           hint="Any always-true expression. The shortest one compares a constant to itself."),

        chal("sql_join_model-predict", "Predict all three counts",
             "Return **one row with three columns** — `inner_rows`, `cross_rows`, `left_rows` — holding "
             "the number of rows produced by, respectively: `owners JOIN pets ON pets.owner_id = owners.id`, "
             "`owners CROSS JOIN pets`, and `owners LEFT JOIN pets ON pets.owner_id = owners.id`. "
             "Write each count as its own subquery in the select list.",
             "pets",
             "SELECT\n"
             "  (SELECT COUNT(*) FROM owners o JOIN pets p ON p.owner_id = o.id)      AS inner_rows,\n"
             "  (SELECT COUNT(*) FROM owners o CROSS JOIN pets p)                     AS cross_rows,\n"
             "  (SELECT COUNT(*) FROM owners o LEFT JOIN pets p ON p.owner_id = o.id) AS left_rows;",
             variants=("INSERT INTO owners (id, name, city) VALUES (5, 'Eda', 'Porto');",),
             hint="A parenthesised SELECT returning exactly one row and one column can be used anywhere a value can.",
             difficulty="Easy"),
        chal("sql_join_model-rebuild", "Rebuild an inner join by hand",
             "Without using the word `JOIN` anywhere, list every owner/pet pair as `owner` and `pet` — "
             "exactly what `owners JOIN pets ON pets.owner_id = owners.id` returns. Use the comma form "
             "plus a `WHERE`. Order by owner name, then pet name.",
             "pets",
             "SELECT o.name AS owner, p.name AS pet\n"
             "FROM owners o, pets p\n"
             "WHERE p.owner_id = o.id\n"
             "ORDER BY o.name, p.name;",
             variants=("INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Suki', 'cat', 4);",),
             hint="`FROM a, b` is the cartesian product; the WHERE clause then performs step 2 of the join.",
             difficulty="Easy"),
        chal("sql_join_model-perowner", "How much does each owner multiply?",
             "For every owner — including ones with no pets — show `owner` and `pet_count`, the number of "
             "pets they own (`0` when they own none). Order by `pet_count` descending, then `owner` ascending.",
             "pets",
             "SELECT o.name AS owner, COUNT(p.id) AS pet_count\n"
             "FROM owners o\n"
             "LEFT JOIN pets p ON p.owner_id = o.id\n"
             "GROUP BY o.id, o.name\n"
             "ORDER BY pet_count DESC, owner;",
             variants=("DELETE FROM pets WHERE owner_id = 1;",),
             hint="You need every owner, so the join must be outer. And COUNT(*) would count Dane's padded row as 1 — count a column from the pets side instead.",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 2. INNER JOIN
# ===========================================================================

concept(
    "sql_inner_join",
    "SQL: Join Foundations",
    "INNER JOIN",
    "Keep only the rows that matched on both sides — the default, and the one to justify.",
    "INNER JOIN is the join you get when you write JOIN, and it is the right answer perhaps "
    "seven times in ten. Its defining property is that it is destructive in both directions: "
    "a row survives only if it found a partner, so anything unmatched on either side is gone "
    "with no warning, no NULL, and no row count to notice. That is exactly what you want when "
    "both sides are genuinely required — an order line without a product is meaningless — and "
    "exactly what you do not want when one side is optional. The skill is not writing INNER "
    "JOIN; it is being able to say out loud which rows you just agreed to throw away.",
    """
```sql
SELECT c.name, o.id, o.order_date
FROM orders o
JOIN customers c ON c.id = o.customer_id;    -- INNER is the default
```

`INNER JOIN`, `JOIN` and (with a `WHERE`) the comma form are the same thing.
A row appears in the result **if and only if** the `ON` condition found it a
partner.

| you wrote                     | you are asserting                                     |
|-------------------------------|--------------------------------------------------------|
| `orders JOIN customers`       | every order I care about has a customer                |
| `customers JOIN orders`       | I only care about customers who have ordered           |
| `products JOIN order_items`   | I only care about products that have been sold         |

The left/right order of an inner join changes **nothing** about the result set —
only the readability. `a JOIN b` and `b JOIN a` return the same rows.
""",
    """
### The one rule

> A row survives an inner join only if the `ON` condition matched it to at least
> one row on the other side.

Everything else follows. In the `shop` dataset:

```sql
SELECT c.name AS customer, COUNT(*) AS orders
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY c.name;
```

`Farid` and `Hugo` are **not in the result**. They exist, they signed up, they
have never ordered — and the inner join deleted them from your report. If the
question was *"how many orders has each customer placed?"*, that answer is wrong:
the honest answer includes two customers with zero. If the question was *"which
customers are active?"*, it is exactly right.

Same query, same data, two different questions. The join type is where you record
which question you are actually answering.

### Inner joins compose without surprises

Chain as many as the question needs. Each one is another "must have matched":

```sql
SELECT c.name AS customer, p.name AS product, i.quantity
FROM orders o
JOIN customers   c ON c.id = o.customer_id
JOIN order_items i ON i.order_id = o.id
JOIN products    p ON p.id = i.product_id
ORDER BY o.id, p.name;
```

Read it as a sentence: *orders, that have a customer, that have lines, whose
lines have a product.* Order 113 has no lines, so it disappears at the third
join — quietly, and correctly, because a query about products cannot say anything
about an order with no products in it.

### `ON` versus `WHERE` (for an inner join, it does not matter)

```sql
FROM orders o JOIN customers c ON c.id = o.customer_id AND c.city = 'Lisbon'
FROM orders o JOIN customers c ON c.id = o.customer_id WHERE c.city = 'Lisbon'
```

For an **inner** join these are identical, and the optimiser treats them
identically. Filter early, filter late — a row that fails either test is gone
either way.

**This stops being true the moment the join becomes outer**, and the difference
is the single most common outer-join bug. Chapter 3 covers it. Building the habit
now — *join conditions go in `ON`, row filters go in `WHERE`* — means you never
have to unlearn anything.

### Rows in, rows out

A useful reflex when a result looks wrong: compare the counts.

```sql
SELECT COUNT(*) AS order_rows FROM orders;                        -- 13
SELECT COUNT(*) AS joined_rows                                    -- 20
FROM orders o JOIN order_items i ON i.order_id = o.id;
```

20 > 13, because most orders have several lines and one order (113) has none.
Anytime the joined count differs from the count you started with, the join either
**multiplied** (the right side has multiple matches) or **filtered** (some left
rows had none). Knowing which one happened tells you whether your `SUM` is about
to be wrong.

### `USING` and `NATURAL` — one is fine, one is a trap

```sql
JOIN order_items USING (order_id)   -- fine: names the column explicitly, folds it to one output column
NATURAL JOIN order_items            -- avoid: joins on EVERY same-named column
```

`NATURAL JOIN` looks elegant and is a landmine. It silently joins on every column
the two tables happen to share — so `orders NATURAL JOIN order_items` would join
on `id = id` as well as `order_id`, and return nothing at all. Worse, adding a
column called `created_at` to both tables one day changes what your existing
query means. Never use it.

### Watch out for

- **Silent deletion.** No error, no NULL, no warning; just missing rows. If a
  total is smaller than you expected, suspect the inner join first.
- **Foreign keys that can be NULL.** `employees.dept_id` is nullable, so
  `employees JOIN departments` drops `Dov`. A nullable FK is a signal that the
  relationship is optional — which usually means you wanted `LEFT JOIN`.
- **Joining on the wrong column.** `ON i.order_id = o.customer_id` is perfectly
  valid SQL that returns confident nonsense. Types line up; meaning does not.
""",
    [
        q("Which customers are missing from `FROM customers c JOIN orders o ON o.customer_id = c.id`?",
          ["Any customer who has never placed an order",
           "Any customer with a NULL city",
           "None — an inner join keeps every customer",
           "Any customer whose orders are all cancelled"], 0,
          "An inner join keeps a customer only if at least one order matched. Farid and Hugo have never ordered, so they are silently dropped."),
        q("Do `a JOIN b ON a.k = b.k` and `b JOIN a ON a.k = b.k` return the same rows?",
          ["Yes — the order of an inner join's operands never changes its result",
           "No — the left table is always preserved",
           "No — the first table's columns come first, which changes the rows",
           "Only if both tables have the same number of rows"], 0,
          "Inner joins are symmetric. Operand order can change column order and can influence the plan, but never which rows come back."),
        q("For an **inner** join, is `ON a.k = b.k AND b.x = 1` different from `ON a.k = b.k WHERE b.x = 1`?",
          ["No — for an inner join they are equivalent",
           "Yes — the ON version keeps unmatched rows",
           "Yes — the WHERE version runs first",
           "Yes — ON cannot contain anything but equality"], 0,
          "For an inner join a row must pass both tests either way. The distinction only becomes real for outer joins, where ON runs before rows are added back and WHERE runs after."),
        q("`orders` has 13 rows; `orders JOIN order_items ON order_items.order_id = orders.id` has 20. Why?",
          ["Most orders have several lines, so those order rows are duplicated once per line",
           "The join added 7 empty rows",
           "order_items has 20 rows and the join returns the larger table",
           "The join condition is wrong"], 0,
          "One row per *line*, not per order. Orders with several lines are repeated; order 113, which has no lines, is dropped. 20 is the size of order_items minus nothing, which is the giveaway."),
        q("Why should you avoid `NATURAL JOIN`?",
          ["It joins on every same-named column, so adding a column silently changes the query",
           "It is slower than an explicit JOIN",
           "It is not supported by SQLite",
           "It can only join two tables"], 0,
          "It infers the join condition from column names. `orders NATURAL JOIN order_items` would also join `id = id` and return nothing — and a future `created_at` column on both tables would break every natural join over them."),
        q("`employees JOIN departments ON departments.id = employees.dept_id` drops `Dov`. Why?",
          ["His `dept_id` is NULL, and NULL never equals anything",
           "His department was deleted",
           "He was hired most recently",
           "His salary is outside every band"], 0,
          "`NULL = 4` is not false, it is unknown — and `ON` keeps only pairs where the condition is *true*. A nullable foreign key is usually a hint that you wanted LEFT JOIN."),
    ],
    [
        sq("sql_inner_join-basic", "Name the join",
           "Show every order with the customer who placed it: `order_id`, `customer`, `order_date`. "
           "Fill in the join type that keeps only orders that matched a customer. Order by `order_id`.",
           "shop",
           "SELECT o.id AS order_id, c.name AS customer, o.order_date\nFROM orders o\nJOIN customers c ON c.id = o.customer_id\nORDER BY o.id;",
           ["JOIN customers c ON c.id = o.customer_id"],
           hint="One keyword plus the table, its alias, and an ON condition matching orders.customer_id to customers.id."),
        sq("sql_inner_join-oncond", "Fill in the ON",
           "Every order line should show which product it is for. Fill in the `ON` condition. "
           "Columns: `order_id`, `product`, `quantity`. Order by `order_id`, then `product`.",
           "shop",
           "SELECT i.order_id, p.name AS product, i.quantity\nFROM order_items i\nJOIN products p ON p.id = i.product_id\nORDER BY i.order_id, p.name;",
           ["p.id = i.product_id"],
           variants=("UPDATE order_items SET product_id = 9 WHERE id = 1;",),
           hint="Match the line's product_id to the product's primary key."),
        sq("sql_inner_join-chain", "Chain three tables",
           "Show each order line as `order_id`, `customer`, `product`. That needs orders joined to "
           "customers *and* to order_items, then order_items to products. Fill in the missing join. "
           "Order by `order_id`, then `product`.",
           "shop",
           "SELECT o.id AS order_id, c.name AS customer, p.name AS product\n"
           "FROM orders o\n"
           "JOIN customers   c ON c.id = o.customer_id\n"
           "JOIN order_items i ON i.order_id = o.id\n"
           "JOIN products    p ON p.id = i.product_id\n"
           "ORDER BY o.id, p.name;",
           ["JOIN order_items i ON i.order_id = o.id"],
           hint="Each join adds one more 'must have matched'. This one links an order to its lines."),
        sq("sql_inner_join-filter", "Filter the joined rows",
           "Show only the shipped orders placed by customers in Lisbon: `order_id`, `customer`, `order_date`. "
           "Fill in the `WHERE`. Order by `order_id`.",
           "shop",
           "SELECT o.id AS order_id, c.name AS customer, o.order_date\n"
           "FROM orders o\n"
           "JOIN customers c ON c.id = o.customer_id\n"
           "WHERE o.status = 'shipped' AND c.city = 'Lisbon'\n"
           "ORDER BY o.id;",
           ["o.status = 'shipped' AND c.city = 'Lisbon'"],
           variants=("UPDATE customers SET city = 'Lisbon' WHERE name = 'Elif';",),
           hint="Two conditions joined by AND — one on the order's status, one on the customer's city."),
        sq("sql_inner_join-using", "`USING` instead of `ON`",
           "When both sides name the join column identically, `USING (col)` is shorter than `ON` *and* "
           "folds the two columns into one. `order_items` and `orders` share nothing, but `order_items.order_id` "
           "matches the alias `o.order_id` below. Fill in the `USING` clause. Columns: `order_id`, `lines`. "
           "Order by `order_id`.",
           "shop",
           "SELECT order_id, COUNT(*) AS lines\n"
           "FROM order_items\n"
           "JOIN (SELECT id AS order_id, status FROM orders) o USING (order_id)\n"
           "WHERE o.status = 'shipped'\n"
           "GROUP BY order_id\n"
           "ORDER BY order_id;",
           ["USING (order_id)"],
           hint="`USING (column_name)` — one column name in parentheses, and it must exist on both sides."),
        sq("sql_inner_join-count", "Count what the join produced",
           "How many rows does joining orders to their lines produce? Report it as `joined_rows`. "
           "Fill in the aggregate.",
           "shop",
           "SELECT COUNT(*) AS joined_rows\nFROM orders o\nJOIN order_items i ON i.order_id = o.id;",
           ["COUNT(*)"],
           variants=("DELETE FROM order_items WHERE order_id = 101;",),
           hint="One row per surviving pair. There are 20 order lines and every one has a matching order."),

        chal("sql_inner_join-lisbon", "Lisbon spending",
             "For every customer in Lisbon who has at least one order, show `customer` and `order_count`, "
             "the number of orders they have placed (any status). Order by `order_count` descending, then "
             "`customer` ascending.",
             "shop",
             "SELECT c.name AS customer, COUNT(*) AS order_count\n"
             "FROM customers c\n"
             "JOIN orders o ON o.customer_id = c.id\n"
             "WHERE c.city = 'Lisbon'\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY order_count DESC, customer;",
             variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 7, '2023-12-04', 'shipped', 'app');",),
             hint="Inner join is right here — the question already says 'who has at least one order'.",
             difficulty="Easy"),
        chal("sql_inner_join-catrevenue", "Revenue by category",
             "Across every order line, total the money charged per product category. Show `category` and "
             "`revenue`, where revenue is `SUM(quantity * unit_price)` rounded to 2 decimal places. "
             "Only categories with at least one sold line appear. Order by `revenue` descending, then `category`.",
             "shop",
             "SELECT cat.name AS category, ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue\n"
             "FROM order_items i\n"
             "JOIN products   p   ON p.id = i.product_id\n"
             "JOIN categories cat ON cat.id = p.category_id\n"
             "GROUP BY cat.id, cat.name\n"
             "ORDER BY revenue DESC, category;",
             variants=("UPDATE products SET category_id = 3 WHERE name = 'Kettle';",),
             hint="Three tables: lines -> products -> categories. Use the line's unit_price, not the product's current price.",
             difficulty="Medium"),
        chal("sql_inner_join-appweb", "Who buys on the app?",
             "List every customer who has placed at least one order through the `app` channel. Show "
             "`customer` and `app_orders`. Order by `app_orders` descending, then `customer` ascending.",
             "shop",
             "SELECT c.name AS customer, COUNT(*) AS app_orders\n"
             "FROM customers c\n"
             "JOIN orders o ON o.customer_id = c.id\n"
             "WHERE o.channel = 'app'\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY app_orders DESC, customer;",
             variants=("UPDATE orders SET channel = 'app' WHERE customer_id = 7;",),
             hint="Filter on the channel, then group by the customer. Customers with no app orders should not appear at all — which the inner join gives you for free.",
             difficulty="Easy"),
    ],
)


# ===========================================================================
# 3. LEFT JOIN and the anti-join
# ===========================================================================

concept(
    "sql_left_join",
    "SQL: Join Foundations",
    "LEFT JOIN & Finding What Is Missing",
    "Keep every row on the left, matched or not — and turn the unmatched ones into an answer.",
    "LEFT JOIN exists for one reason: to preserve rows that have nothing to match. That makes "
    "it the join for every question of the form 'for each X, ... including the ones with none'. "
    "But its real power is the inversion: if unmatched rows come back with NULLs, then filtering "
    "for those NULLs gives you precisely the rows that had no partner. That is the anti-join, "
    "and it answers 'customers who never ordered', 'products never sold', 'files with no owner' "
    "with one join and one IS NULL. The catch is that a LEFT JOIN is fragile — one condition in "
    "the wrong clause silently turns it back into an inner join, and nothing warns you.",
    """
```sql
SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;
```

Every customer comes back. Those with orders appear once per order; those without
appear once, with **every `orders` column NULL**.

Two uses, and the second is the one worth memorising:

```sql
-- 1. "for each X, including the empty ones"
SELECT c.name, COUNT(o.id) AS orders
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;

-- 2. the ANTI-JOIN: "X that has no Y at all"
SELECT c.name
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

**`LEFT JOIN` = `LEFT OUTER JOIN`.** The `OUTER` is optional noise.
""",
    """
### The preserved side

"Left" means *the table written to the left of the keyword*. It is preserved:
every one of its rows appears in the output at least once, no matter what.

```sql
SELECT c.name AS customer, o.id AS order_id, o.status
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
ORDER BY c.name, o.id;
```

| customer | order_id | status  |
|----------|----------|---------|
| Ada      | 101      | shipped |
| Ada      | 102      | shipped |
| Ada      | 108      | shipped |
| ...      | ...      | ...     |
| Farid    | *NULL*   | *NULL*  |  ← preserved, padded
| Hugo     | *NULL*   | *NULL*  |  ← preserved, padded

Farid's row is not "a row from `orders`". There is no such row. The database
manufactured NULLs to fill the space where an `orders` row would have gone.

### The anti-join — the pattern to actually memorise

Turn that padding into a filter and you have found every unmatched row:

```sql
SELECT c.name AS customer
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL          -- only the padded rows survive
ORDER BY c.name;
```

| customer |
|----------|
| Farid    |
| Hugo     |

Three rules make this reliable:

1. **Test a column that can never be NULL in a real row.** `o.id` is the primary
   key, so `o.id IS NULL` can only mean "padding". Testing `o.status IS NULL`
   would also catch real orders that happen to have a NULL status.
2. **The test goes in `WHERE`, never in `ON`.** In `ON` it would be part of the
   match, not a filter on the result.
3. **Use `IS NULL`, never `= NULL`.** `x = NULL` is unknown for every `x`,
   including NULL, so it matches nothing. Ever.

This one shape answers a whole family of questions:

```sql
-- products never sold
FROM products p LEFT JOIN order_items i ON i.product_id = p.id WHERE i.id IS NULL
-- categories with no products
FROM categories c LEFT JOIN products p ON p.category_id = c.id WHERE p.id IS NULL
-- orders with no lines
FROM orders o LEFT JOIN order_items i ON i.order_id = o.id WHERE i.id IS NULL
```

### `COUNT(*)` versus `COUNT(column)` — the classic wrong zero

```sql
SELECT c.name, COUNT(*) AS wrong, COUNT(o.id) AS right
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name;
```

For Farid, `COUNT(*)` returns **1** — his padded row is still a row. `COUNT(o.id)`
returns **0**, because `COUNT(column)` skips NULLs. With a `LEFT JOIN`, always
count a column from the *optional* side.

The same trap applies to `SUM`: `SUM(i.quantity)` over a customer with no lines
returns `NULL`, not `0`. Wrap it: `COALESCE(SUM(i.quantity), 0)`.

### `ON` versus `WHERE` — where LEFT JOINs go to die

This is the highest-value paragraph in the chapter.

```sql
-- A: "every customer, with their shipped orders"
SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped';

-- B: "customers who have a shipped order"   <-- NOT the same query
SELECT c.name, o.id
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'shipped';
```

Remember the three steps. `ON` runs during step 2, **before** unmatched rows are
added back. `WHERE` runs after the whole join is finished.

- In **A**, `Dara` (whose only order is pending) fails the match, so she is added
  back with NULLs. She is in the result with `NULL`. Correct for "every customer".
- In **B**, Dara is added back with `o.status = NULL`, then `WHERE NULL = 'shipped'`
  is *unknown*, so the row is discarded. **The LEFT JOIN has been silently
  demoted to an INNER JOIN.**

> **Any `WHERE` condition on the optional side of a `LEFT JOIN` turns it into an
> inner join — unless the condition is `IS NULL`.**

If you want it in `WHERE` *and* you want the padding kept, you have to say so:
`WHERE o.status = 'shipped' OR o.id IS NULL`. Putting it in `ON` is cleaner.

### `LEFT JOIN` chains

Once one join is outer, everything downstream of it must be too:

```sql
SELECT c.name AS customer, p.name AS product
FROM customers c
LEFT JOIN orders      o ON o.customer_id = c.id
LEFT JOIN order_items i ON i.order_id = o.id
LEFT JOIN products    p ON p.id = i.product_id
ORDER BY c.name, p.name;
```

Make the second join `INNER` and Farid's padded row — whose `o.id` is NULL —
fails to match anything and is dropped, undoing the first `LEFT JOIN`. One inner
join anywhere in the chain collapses the whole thing.

### Watch out for

- **`WHERE right_table.col = something`** — the demotion above. The most common
  outer-join bug there is.
- **`COUNT(*)` after a LEFT JOIN** — counts padded rows as 1.
- **`SUM` over no rows is NULL, not 0** — `COALESCE` it.
- **An `IN` list on the optional side** — `WHERE o.status IN ('shipped','pending')`
  demotes just as surely as `=` does.
- **Right-side NULLs that were already there.** If `orders.status` can genuinely
  be NULL, `WHERE o.status IS NULL` finds both padding *and* real rows. Test the
  primary key instead.
""",
    [
        q("What does `LEFT JOIN` guarantee?",
          ["Every row of the left table appears at least once in the result",
           "Every row of the right table appears at least once",
           "The result has the same number of rows as the left table",
           "Rows are returned in left-table order"], 0,
          "At least once — a left row with three matches appears three times. What is guaranteed is that it is never dropped."),
        q("`FROM customers c LEFT JOIN orders o ON o.customer_id = c.id WHERE o.status = 'shipped'` — what has happened?",
          ["The LEFT JOIN has been demoted to an INNER JOIN",
           "Nothing; it still returns every customer",
           "It is a syntax error",
           "Only cancelled orders are excluded"], 0,
          "Padded rows have `o.status = NULL`, and `NULL = 'shipped'` is unknown, so the WHERE discards exactly the rows the LEFT JOIN added back. Put the condition in ON instead."),
        q("Which column should an anti-join test with `IS NULL`?",
          ["The right table's primary key, which can never be NULL in a real row",
           "Any column on the right table",
           "The join column on the left table",
           "A text column, so the comparison is cheap"], 0,
          "Testing the primary key guarantees that `IS NULL` means 'this row is padding'. Any other column might legitimately be NULL in a matched row, giving false positives."),
        q("After a LEFT JOIN, why does `COUNT(*)` return 1 for a customer with no orders?",
          ["The padded row is still a row, and COUNT(*) counts rows",
           "COUNT(*) always returns at least 1",
           "The customer has one cancelled order",
           "It is a SQLite quirk"], 0,
          "COUNT(*) counts rows regardless of content. COUNT(o.id) skips NULLs and correctly returns 0. After a LEFT JOIN, always count a column from the optional side."),
        q("Why does `WHERE o.id = NULL` never find the padded rows?",
          ["Any comparison with NULL is unknown, not true, so nothing matches",
           "NULL can only be compared with strings",
           "It works, but only in SQLite",
           "You must write `WHERE o.id == NULL`"], 0,
          "NULL means unknown; `unknown = unknown` is unknown, which WHERE treats as not-true. `IS NULL` is a separate operator that exists precisely because of this."),
        q("`c LEFT JOIN o ON ... INNER JOIN i ON i.order_id = o.id` — what happens to customers with no orders?",
          ["They are dropped: their padded row has o.id NULL, which matches nothing in the inner join",
           "They are kept, with NULLs from both tables",
           "It is a syntax error to mix join types",
           "They appear twice"], 0,
          "One inner join downstream collapses the whole chain. Once a join is outer, every join that depends on its output has to be outer too."),
        q("You want *every* customer plus only their `shipped` orders. Where does `status = 'shipped'` go?",
          ["In the ON clause, so it filters the match rather than the finished join",
           "In the WHERE clause",
           "In a HAVING clause",
           "Either one — they are equivalent"], 0,
          "ON runs before unmatched rows are added back, so it narrows which orders count as a match while still preserving every customer. WHERE runs afterwards and would delete the padded rows."),
    ],
    [
        sq("sql_left_join-keepall", "Keep every customer",
           "List every customer with each of their orders — including customers who have never ordered. "
           "Columns: `customer`, `order_id`. Fill in the join type. Order by `customer`, then `order_id`.",
           "shop",
           "SELECT c.name AS customer, o.id AS order_id\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id\nORDER BY c.name, o.id;",
           ["LEFT JOIN"],
           variants=("DELETE FROM order_items WHERE order_id IN (101,102,108); DELETE FROM orders WHERE customer_id = 1;",),
           hint="Two words. The preserved table is the one written before the keyword."),
        sq("sql_left_join-anti", "The anti-join",
           "Find every customer who has never placed an order. Show just `customer`. "
           "Fill in the `WHERE` that keeps only the padded rows. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer\nFROM customers c\nLEFT JOIN orders o ON o.customer_id = c.id\nWHERE o.id IS NULL\nORDER BY c.name;",
           ["o.id IS NULL"],
           variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 6, '2023-12-01', 'shipped', 'web');",),
           hint="Test the orders primary key with IS NULL — never with `= NULL`."),
        sq("sql_left_join-countcol", "Count the right column",
           "Show every customer and how many orders they have placed, as `customer` and `order_count`, "
           "with `0` for customers who have none. `COUNT(*)` would wrongly give them 1 — fill in the "
           "aggregate that gives 0. Order by `order_count` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS order_count\n"
           "FROM customers c\n"
           "LEFT JOIN orders o ON o.customer_id = c.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY order_count DESC, customer;",
           ["COUNT(o.id)"],
           variants=("DELETE FROM order_items WHERE order_id IN (103,110); DELETE FROM orders WHERE customer_id = 2;",),
           hint="COUNT of a column skips NULLs. Pick a column from the optional side."),
        sq("sql_left_join-oncond", "Filter the match, not the result",
           "Show every customer alongside their **shipped** orders only — but keep customers who have "
           "no shipped orders, with NULL. Fill in the extra condition, and put it in the right clause. "
           "Columns: `customer`, `order_id`. Order by `customer`, then `order_id`.",
           "shop",
           "SELECT c.name AS customer, o.id AS order_id\n"
           "FROM customers c\n"
           "LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped'\n"
           "ORDER BY c.name, o.id;",
           ["AND o.status = 'shipped'"],
           variants=("UPDATE orders SET status = 'cancelled' WHERE customer_id = 1;",),
           hint="It belongs inside ON, joined with AND. In WHERE it would delete the very rows you are preserving."),
        sq("sql_left_join-coalesce", "NULL is not zero",
           "Show every customer and the total quantity of items they have ever ordered, as `customer` "
           "and `items`. `SUM` over no rows is NULL — fill in the function that turns that into `0`. "
           "Order by `items` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COALESCE(SUM(i.quantity), 0) AS items\n"
           "FROM customers c\n"
           "LEFT JOIN orders      o ON o.customer_id = c.id\n"
           "LEFT JOIN order_items i ON i.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY items DESC, customer;",
           ["COALESCE(SUM(i.quantity), 0)"],
           variants=("UPDATE order_items SET quantity = quantity + 1 WHERE order_id = 101;",),
           hint="COALESCE returns its first non-NULL argument. Wrap the SUM and give 0 as the fallback."),
        sq("sql_left_join-chain", "Keep the chain outer",
           "Show every customer with every product they have ever bought, keeping customers who have "
           "bought nothing (with NULL). The second and third joins must not undo the first — fill in "
           "the join type for the second one. Columns: `customer`, `product`. "
           "Order by `customer`, then `product`.",
           "shop",
           "SELECT c.name AS customer, p.name AS product\n"
           "FROM customers c\n"
           "LEFT JOIN orders      o ON o.customer_id = c.id\n"
           "LEFT JOIN order_items i ON i.order_id = o.id\n"
           "LEFT JOIN products    p ON p.id = i.product_id\n"
           "ORDER BY c.name, p.name;",
           ["LEFT JOIN order_items i ON i.order_id = o.id"],
           hint="Once one join is outer, every join downstream of it has to be outer too, or the padded rows get dropped."),

        chal("sql_left_join-neversold", "Products nobody has ever bought",
             "List every product that has never appeared on an order line. Show `product` and `price`. "
             "Order by `product`.",
             "shop",
             "SELECT p.name AS product, p.price\n"
             "FROM products p\n"
             "LEFT JOIN order_items i ON i.product_id = p.id\n"
             "WHERE i.id IS NULL\n"
             "ORDER BY p.name;",
             variants=("DELETE FROM order_items WHERE product_id IN (1, 6);",),
             hint="Anti-join: preserve products, then keep only the rows where the order_items primary key came back NULL.",
             difficulty="Easy"),
        chal("sql_left_join-emptycat", "Categories with nothing in them",
             "List every category that contains no products at all, as `category`. Order by `category`.",
             "shop",
             "SELECT c.name AS category\n"
             "FROM categories c\n"
             "LEFT JOIN products p ON p.category_id = c.id\n"
             "WHERE p.id IS NULL\n"
             "ORDER BY c.name;",
             variants=("DELETE FROM order_items WHERE product_id IN (6,7); DELETE FROM products WHERE category_id = 3;",),
             hint="Same anti-join shape, one level up: categories preserved, products optional.",
             difficulty="Easy"),
        chal("sql_left_join-shipped", "Every customer, shipped revenue only",
             "For every customer — including those who have never ordered and those whose orders are all "
             "cancelled or pending — show `customer` and `shipped_revenue`: the total "
             "`quantity * unit_price` across their **shipped** orders, rounded to 2 decimals, and `0.0` "
             "when there is none. Order by `shipped_revenue` descending, then `customer` ascending.",
             "shop",
             "SELECT c.name AS customer,\n"
             "       ROUND(COALESCE(SUM(i.quantity * i.unit_price), 0), 2) AS shipped_revenue\n"
             "FROM customers c\n"
             "LEFT JOIN orders      o ON o.customer_id = c.id AND o.status = 'shipped'\n"
             "LEFT JOIN order_items i ON i.order_id = o.id\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY shipped_revenue DESC, customer;",
             variants=("UPDATE orders SET status = 'shipped' WHERE id IN (104, 106);",),
             hint="The status test belongs in the first ON, not in WHERE. Then COALESCE the SUM so 'no rows' becomes 0.",
             difficulty="Medium"),
        chal("sql_left_join-emptyorders", "Orders that were never filled",
             "Find every order that has no order lines at all. Show `order_id`, `customer`, `order_date`. "
             "Order by `order_id`.",
             "shop",
             "SELECT o.id AS order_id, c.name AS customer, o.order_date\n"
             "FROM orders o\n"
             "JOIN customers c ON c.id = o.customer_id\n"
             "LEFT JOIN order_items i ON i.order_id = o.id\n"
             "WHERE i.id IS NULL\n"
             "ORDER BY o.id;",
             variants=("DELETE FROM order_items WHERE order_id IN (105, 112);",),
             hint="Two joins with different jobs: customers is required (inner), order_items is the one you are testing for absence (outer + IS NULL).",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 4. RIGHT, FULL OUTER, CROSS
# ===========================================================================

concept(
    "sql_right_full_cross",
    "SQL: Join Foundations",
    "RIGHT, FULL OUTER & CROSS JOIN",
    "The other three shapes: preserve the right side, preserve both, or preserve nothing and pair everything.",
    "RIGHT JOIN is LEFT JOIN with the tables swapped, which is why most codebases never contain "
    "one — writing every outer join in the same direction makes a long query far easier to read. "
    "FULL OUTER JOIN is genuinely different: it preserves both sides at once, and it is the "
    "correct tool for exactly one job, reconciling two lists to find what each is missing. CROSS "
    "JOIN has no condition at all and is the only join people write by accident, but written on "
    "purpose it is how you build a complete grid — every day crossed with every product — so "
    "that a later outer join can show you the zeroes rather than just omitting them.",
    """
```sql
a LEFT  JOIN b ON ...   -- keep all of a
a RIGHT JOIN b ON ...   -- keep all of b            (= b LEFT JOIN a)
a FULL  JOIN b ON ...   -- keep all of both
a CROSS JOIN b          -- no condition; every pairing
```

On `pets`, the row counts are worth learning by heart:

| join                                         | rows | who is kept        |
|----------------------------------------------|------|--------------------|
| `owners INNER JOIN pets`                     | 4    | matched only       |
| `owners LEFT JOIN pets`                      | 5    | + Dane             |
| `owners RIGHT JOIN pets`                     | 5    | + Rex              |
| `owners FULL JOIN pets`                      | 6    | + Dane and Rex     |
| `owners CROSS JOIN pets`                     | 20   | every pairing      |

SQLite has supported `RIGHT` and `FULL OUTER JOIN` since 3.39 (2022); older
versions and MySQL 5.x do not have `FULL`, and the `UNION` workaround below is
still worth knowing.
""",
    """
### RIGHT JOIN — the same tool, held backwards

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o
RIGHT JOIN pets p ON p.owner_id = o.id;
```

Now `pets` is preserved, so `Rex` (the stray with `owner_id IS NULL`) appears
with a NULL owner, and `Dane` is gone. That is **identical** to:

```sql
FROM pets p LEFT JOIN owners o ON p.owner_id = o.id
```

So why does `RIGHT JOIN` exist? Occasionally the reading order of a long query is
better with the "main" table first. In practice, most style guides say: **write
every outer join as `LEFT`, and reorder the tables instead.** A query where the
preserved table is always the one you already read is enormously easier to
follow, especially with four joins in play.

### FULL OUTER JOIN — reconciliation

This is the one that does something the others cannot: preserve **both** sides.

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o
FULL OUTER JOIN pets p ON p.owner_id = o.id
ORDER BY o.name, p.name;
```

| owner  | pet    |
|--------|--------|
| *NULL* | Rex    |  ← pet with no owner
| Ana    | Milo   |
| Ana    | Nala   |
| Ben    | Otto   |
| Cleo   | Pip    |
| Dane   | *NULL* |  ← owner with no pet

Six rows: the four matches plus one orphan from each side. That is the shape of
every **reconciliation** — two systems that are supposed to agree, and you need
to see the discrepancies in both directions at once:

```sql
SELECT COALESCE(a.ref, b.ref) AS ref,
       CASE WHEN a.ref IS NULL THEN 'missing from A'
            WHEN b.ref IS NULL THEN 'missing from B'
            ELSE 'in both' END AS state
FROM ledger_a a
FULL OUTER JOIN ledger_b b ON b.ref = a.ref;
```

Note the `COALESCE` — in a full outer join, *either* side's columns may be NULL,
so neither alone is a safe key to select or order by.

**Where `FULL` is unavailable**, it is exactly a left join unioned with the
right-hand anti-join:

```sql
SELECT o.name AS owner, p.name AS pet
FROM owners o LEFT JOIN pets p ON p.owner_id = o.id
UNION ALL
SELECT NULL, p.name
FROM pets p
WHERE NOT EXISTS (SELECT 1 FROM owners o WHERE o.id = p.owner_id);
```

### CROSS JOIN — on purpose, not by accident

No `ON`. Every pairing. The accidental version is `FROM a, b` with a forgotten
`WHERE`, and it is how you turn a 10-thousand-row table into a 100-million-row
result.

Written deliberately, it builds a **complete grid** — and a complete grid is what
lets a report show zeroes instead of gaps:

```sql
-- Every category x every channel, even the combinations that never happened
SELECT cat.name AS category, ch.channel, COUNT(o.id) AS orders
FROM categories cat
CROSS JOIN (SELECT DISTINCT channel FROM orders) ch
LEFT JOIN products    p  ON p.category_id = cat.id
LEFT JOIN order_items i  ON i.product_id = p.id
LEFT JOIN orders      o  ON o.id = i.order_id AND o.channel = ch.channel
GROUP BY cat.name, ch.channel;
```

Without the cross join, a category that has never sold on the app is simply
absent from the report. With it, it is there with a `0` — which is usually the
number the reader most needs to see.

### Watch out for

- **`FULL JOIN` needs `COALESCE` on the key.** Selecting only `a.id` loses the
  identity of every row that came from `b` alone.
- **`ORDER BY` after a full join** puts NULLs first in SQLite (ascending). Sort
  by the coalesced value if you want stable, meaningful order.
- **`RIGHT JOIN` mixed with `LEFT JOIN`** in one query is genuinely hard to
  reason about, because the preserved side changes halfway down. Normalise to
  `LEFT`.
- **Accidental cross joins** are silent. If a query suddenly gets slow and the
  row count exploded, count your `ON` clauses: *n* tables need *n − 1* of them.
""",
    [
        q("`a RIGHT JOIN b ON cond` is equivalent to which query?",
          ["`b LEFT JOIN a ON cond`", "`a LEFT JOIN b ON cond`",
           "`a FULL JOIN b ON cond`", "`a CROSS JOIN b`"], 0,
          "RIGHT JOIN preserves the right operand, which is exactly what a LEFT JOIN does after you swap the tables. That is why most style guides say to write every outer join as LEFT."),
        q("How many rows does `owners FULL OUTER JOIN pets ON pets.owner_id = owners.id` return?",
          ["6 — the 4 matches, plus Dane, plus Rex", "4", "5", "20"], 0,
          "A full outer join keeps every match, then adds back the unmatched rows from *both* sides: Dane (an owner with no pet) and Rex (a pet with no owner)."),
        q("After a FULL OUTER JOIN, why is `SELECT a.id` unsafe?",
          ["Rows that came only from `b` have `a.id` NULL, so the identity is lost",
           "`a.id` is ambiguous after a full join",
           "Full joins do not allow qualified column names",
           "It is safe — `a.id` is always populated"], 0,
          "Either side's columns can be NULL in a full outer join. Use `COALESCE(a.id, b.id)` so every row carries its key regardless of which side it came from."),
        q("What is the safe, deliberate use of `CROSS JOIN`?",
          ["Building a complete grid so a report can show zeroes for combinations that never occurred",
           "Speeding up a join when there is no index",
           "Joining three or more tables at once",
           "Removing duplicate rows"], 0,
          "Cross-joining the dimensions gives you every combination; a LEFT JOIN onto the facts then fills in counts, leaving 0 where nothing happened, instead of the row being absent."),
        q("A query over 4 tables suddenly returns millions of rows. What should you count first?",
          ["The join conditions — n tables need n-1 of them",
           "The number of columns in the SELECT list",
           "The indexes on each table",
           "The number of rows in the smallest table"], 0,
          "A missing ON (or a forgotten WHERE with comma syntax) leaves an accidental cross join, and it fails silently — the query is valid, just enormous."),
        q("Since which SQLite version are `RIGHT JOIN` and `FULL OUTER JOIN` available?",
          ["3.39 (2022) — before that, only LEFT existed",
           "They have always been supported",
           "They are still unsupported; the app emulates them",
           "3.25, alongside window functions"], 0,
          "SQLite gained RIGHT and FULL OUTER JOIN in 3.39. The app bundles 3.46, so both work here — but on an older engine you would emulate FULL with LEFT JOIN plus a UNION ALL of the right-hand anti-join."),
    ],
    [
        sq("sql_right_full_cross-right", "Preserve the right side",
           "List every pet with its owner — including the stray who has no owner. Fill in the join type "
           "so `pets` is the preserved table while still being written second. "
           "Columns: `owner`, `pet`. Order by `pet`.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\nFROM owners o\nRIGHT JOIN pets p ON p.owner_id = o.id\nORDER BY p.name;",
           ["RIGHT JOIN"],
           variants=("UPDATE pets SET owner_id = NULL WHERE name = 'Otto';",),
           hint="Two words, the mirror image of LEFT JOIN."),
        sq("sql_right_full_cross-flip", "The same query as a LEFT JOIN",
           "Rewrite the previous answer without `RIGHT`: swap the tables so `pets` is written first and "
           "the join is `LEFT`. Fill in the `FROM` line. Columns: `owner`, `pet`. Order by `pet`.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\nFROM pets p\nLEFT JOIN owners o ON p.owner_id = o.id\nORDER BY p.name;",
           ["FROM pets p"],
           variants=("UPDATE pets SET owner_id = NULL WHERE name = 'Otto';",),
           hint="The preserved table goes before the keyword. Same rows, same order, no RIGHT needed."),
        sq("sql_right_full_cross-full", "Preserve both sides",
           "Show every owner and every pet side by side, keeping owners with no pet *and* pets with no "
           "owner. Fill in the join type. Columns: `owner`, `pet`. Order by `owner`, then `pet`.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\nFROM owners o\nFULL OUTER JOIN pets p ON p.owner_id = o.id\nORDER BY o.name, p.name;",
           ["FULL OUTER JOIN"],
           variants=("INSERT INTO owners (id, name, city) VALUES (5, 'Eda', 'Faro');",),
           hint="Three words. It is the only join that adds back unmatched rows from both directions."),
        sq("sql_right_full_cross-coalesce", "Give every full-join row a key",
           "After a full outer join either side can be NULL, so neither name alone identifies the row. "
           "Fill in the expression that produces a single `label` column: the owner's name when there is "
           "one, otherwise the pet's name. Also show `side`. Order by `label`.",
           "pets",
           "SELECT COALESCE(o.name, p.name) AS label,\n"
           "       CASE WHEN o.id IS NULL THEN 'pet only'\n"
           "            WHEN p.id IS NULL THEN 'owner only'\n"
           "            ELSE 'both' END AS side\n"
           "FROM owners o\n"
           "FULL OUTER JOIN pets p ON p.owner_id = o.id\n"
           "ORDER BY label, side;",
           ["COALESCE(o.name, p.name)"],
           hint="COALESCE takes the first non-NULL of its arguments."),
        sq("sql_right_full_cross-cross", "Build a complete grid",
           "Produce every combination of city and species — including combinations that do not exist in "
           "the data. Fill in the join that pairs everything with everything. Columns: `city`, `species`. "
           "Order by `city`, then `species`.",
           "pets",
           "SELECT c.city, s.species\n"
           "FROM (SELECT DISTINCT city FROM owners WHERE city IS NOT NULL) c\n"
           "CROSS JOIN (SELECT DISTINCT species FROM pets) s\n"
           "ORDER BY c.city, s.species;",
           ["CROSS JOIN"],
           variants=("INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Zip', 'fish', 1);",),
           hint="Two words, and unlike every other join it takes no ON clause."),
        sq("sql_right_full_cross-emulate", "FULL OUTER without FULL",
           "Older engines have no `FULL OUTER JOIN`. Rebuild it: a LEFT JOIN for everything owner-side, "
           "then the pets that matched no owner. Fill in the set operator that stacks the two results "
           "without removing duplicates. Columns: `owner`, `pet`. Order by `owner`, then `pet`.",
           "pets",
           "SELECT o.name AS owner, p.name AS pet\n"
           "FROM owners o\n"
           "LEFT JOIN pets p ON p.owner_id = o.id\n"
           "UNION ALL\n"
           "SELECT NULL AS owner, p.name AS pet\n"
           "FROM pets p\n"
           "WHERE p.owner_id IS NULL\n"
           "ORDER BY owner, pet;",
           ["UNION ALL"],
           variants=("UPDATE pets SET owner_id = NULL WHERE name = 'Pip';",),
           hint="Two words. Plain UNION would also de-duplicate, which you do not want here."),

        chal("sql_right_full_cross-orphans", "Both kinds of orphan at once",
             "Using one full outer join, list every row that failed to match: owners with no pet and pets "
             "with no owner. Show `label` (the owner's name or the pet's name) and `kind` "
             "(`'owner with no pet'` or `'pet with no owner'`). Order by `kind`, then `label`.",
             "pets",
             "SELECT COALESCE(o.name, p.name) AS label,\n"
             "       CASE WHEN p.id IS NULL THEN 'owner with no pet'\n"
             "            ELSE 'pet with no owner' END AS kind\n"
             "FROM owners o\n"
             "FULL OUTER JOIN pets p ON p.owner_id = o.id\n"
             "WHERE o.id IS NULL OR p.id IS NULL\n"
             "ORDER BY kind, label;",
             variants=("INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Zip', 'fish', NULL);",),
             hint="Full join, then keep rows where either primary key came back NULL. CASE decides which kind of orphan it is.",
             difficulty="Medium"),
        chal("sql_right_full_cross-grid", "A grid with real zeroes",
             "For every combination of city (`Lisbon`, `Porto`, `Braga`) and species (`bird`, `cat`, `dog`), "
             "show `city`, `species` and `pet_count` — the number of pets of that species owned by someone "
             "in that city, **including 0** for combinations that never occur. Build the city list from "
             "`owners` (ignoring NULL cities) and the species list from `pets`. "
             "Order by `city`, then `species`.",
             "pets",
             "SELECT c.city, s.species, COUNT(p.id) AS pet_count\n"
             "FROM (SELECT DISTINCT city FROM owners WHERE city IS NOT NULL) c\n"
             "CROSS JOIN (SELECT DISTINCT species FROM pets) s\n"
             "LEFT JOIN owners o ON o.city = c.city\n"
             "LEFT JOIN pets   p ON p.owner_id = o.id AND p.species = s.species\n"
             "GROUP BY c.city, s.species\n"
             "ORDER BY c.city, s.species;",
             variants=("UPDATE owners SET city = 'Porto' WHERE name = 'Ana';",),
             hint="Cross join the two dimension lists first, then LEFT JOIN the facts onto that grid. The species test belongs in the last ON, not in WHERE.",
             difficulty="Medium"),
        chal("sql_right_full_cross-counts", "All five row counts",
             "Return one row with five columns — `inner_rows`, `left_rows`, `right_rows`, `full_rows`, "
             "`cross_rows` — giving the number of rows each join type produces over `owners` and `pets` "
             "joined on `pets.owner_id = owners.id`. Write each as a subquery.",
             "pets",
             "SELECT\n"
             "  (SELECT COUNT(*) FROM owners o JOIN pets p ON p.owner_id = o.id)             AS inner_rows,\n"
             "  (SELECT COUNT(*) FROM owners o LEFT JOIN pets p ON p.owner_id = o.id)        AS left_rows,\n"
             "  (SELECT COUNT(*) FROM owners o RIGHT JOIN pets p ON p.owner_id = o.id)       AS right_rows,\n"
             "  (SELECT COUNT(*) FROM owners o FULL OUTER JOIN pets p ON p.owner_id = o.id)  AS full_rows,\n"
             "  (SELECT COUNT(*) FROM owners o CROSS JOIN pets p)                            AS cross_rows;",
             variants=("INSERT INTO owners (id, name, city) VALUES (5, 'Eda', 'Faro');",
                       "INSERT INTO pets (id, name, species, owner_id) VALUES (6, 'Zip', 'fish', NULL);"),
             hint="Five scalar subqueries in one select list. Predict the numbers before you run it — 4, 5, 5, 6, 20.",
             difficulty="Easy"),
    ],
)


# ===========================================================================
# 5. Choosing the right join  ***the decision framework***
# ===========================================================================

concept(
    "sql_join_choice",
    "SQL: Join Foundations",
    "Choosing the Right Join",
    "A decision procedure: read the question, find the preserved side, pick the join, then prove it.",
    "Knowing what each join does is not the same as knowing which one this question needs, and "
    "the gap between the two is where most wrong SQL lives. The good news is that the choice is "
    "mechanical. Every join question hides three sub-questions: which table is the one I am "
    "reporting on, must its rows survive even with no match, and do I want the matched rows or "
    "precisely the unmatched ones. Answer those three and the join type is determined — you are "
    "not choosing, you are reading off a table. This chapter turns that into a procedure you can "
    "run on any question in under a minute, plus the counting check that proves you got it right.",
    """
Four questions, asked in order. Each answer eliminates options.

```
Q1. Which table is the SUBJECT of the sentence? -------> it goes on the LEFT
Q2. Must every subject row appear, even with no match?
      no  -> INNER JOIN            yes -> keep going
Q3. Do you want the matches, or exactly the NON-matches?
      matches      -> LEFT JOIN
      non-matches  -> LEFT JOIN + WHERE right.pk IS NULL      (anti-join)
Q4. Does the OTHER table also have rows that must survive?
      yes -> FULL OUTER JOIN
```

And the special case that skips all four: **no relationship at all, you want
every combination** → `CROSS JOIN`.

| the question says...                | join                              |
|-------------------------------------|-----------------------------------|
| "orders **with** their customer"    | `INNER`                           |
| "**each** customer and their orders"| `LEFT`                            |
| "customers **including** those with none" | `LEFT`                      |
| "customers **without** any orders"  | `LEFT` + `IS NULL`                |
| "**every** X **and every** Y, matched where possible" | `FULL OUTER`    |
| "**every combination** of X and Y"  | `CROSS`                           |
""",
    """
### The four questions, worked

Take a real request: **"Show me each product category and how much revenue it
made last quarter."**

**Q1 — who is the subject?** *Category.* The answer has one row per category, so
`categories` goes on the left and everything else hangs off it.

**Q2 — must every category appear, even with no revenue?** Read the sentence
again: *"each product category"*. Yes. A category that sold nothing is still a
category, and a report that silently omits it is how a business misses that a
whole line has flatlined. → **outer**.

**Q3 — matches or non-matches?** Matches (with zeroes). → `LEFT JOIN`.

**Q4 — does `order_items` have rows that must survive?** No; a line without a
category would be a data bug, not a report row. → stay `LEFT`, not `FULL`.

```sql
SELECT cat.name AS category,
       ROUND(COALESCE(SUM(i.quantity * i.unit_price), 0), 2) AS revenue
FROM categories cat
LEFT JOIN products    p ON p.category_id = cat.id
LEFT JOIN order_items i ON i.product_id = p.id
LEFT JOIN orders      o ON o.id = i.order_id AND o.status = 'shipped'
GROUP BY cat.id, cat.name
ORDER BY revenue DESC, category;
```

`Toys` comes back with `0.0`. With an inner join it would simply not exist.

### The words that give it away

English is surprisingly reliable about this. These phrasings are near-decisive:

| phrase in the request                | it means                          | join                |
|--------------------------------------|-----------------------------------|---------------------|
| "**with** their …", "that have …"    | both sides required               | `INNER`             |
| "**each** …", "**per** …", "**every** …" | the subject must survive      | `LEFT`              |
| "… **including** those with none"    | explicitly asks for the zeroes    | `LEFT`              |
| "… **and 0 if** …"                   | same, plus `COALESCE`             | `LEFT`              |
| "**without** …", "**never** …", "**no** …", "**missing** …" | absence *is* the answer | `LEFT` + `IS NULL` |
| "**only** …", "**at least one** …"   | presence is the filter            | `INNER` (or `EXISTS`) |
| "reconcile", "**compare** A and B", "either side" | both preserved       | `FULL OUTER`        |
| "**all combinations**", "**for each … × each …**" | no relationship       | `CROSS`             |

"Each" versus "with" is the highest-yield distinction in this whole track.
*"Customers with orders"* is inner. *"Each customer and their orders"* is left.
Same tables, different report.

### Then prove it — the counting check

Choosing is half of it; verifying costs ten seconds and catches nearly everything.

**Check 1 — did the subject survive?**

```sql
SELECT COUNT(*) FROM customers;              -- 8
SELECT COUNT(DISTINCT c.id) FROM customers c JOIN orders o ON o.customer_id = c.id;  -- 6
```

If your report claims one row per customer and 6 ≠ 8, your join is inner and you
wanted outer. Any time the distinct count of your subject drops, a join ate rows.

**Check 2 — did the subject multiply?**

```sql
SELECT COUNT(*) FROM orders;                 -- 13
SELECT COUNT(*) FROM orders o JOIN order_items i ON i.order_id = o.id;   -- 20
```

20 > 13, so each order row now exists once *per line*. Any `SUM` of an
order-level column (a shipping fee, a discount) is now inflated. That is Chapter
9's territory, and this count is how you notice you are in it.

**Check 3 — is the filter demoting your outer join?** If a `LEFT JOIN` query and
the same query with `INNER JOIN` return the same number of rows, the `LEFT` is
doing nothing — almost always because a `WHERE` on the optional side demoted it.

### Three worked diagnoses

**"Our top-customers report is missing people."**
Symptom: customers who ordered only cancelled items are absent.
Cause: `WHERE o.status = 'shipped'` after a `LEFT JOIN`.
Fix: move it into `ON`. The customer is preserved with `NULL`, and `COALESCE`
turns that into `0`.

**"Total revenue is about 40% too high."**
Symptom: a per-order `shipping_fee` summed after joining `order_items`.
Cause: the join fanned each order out to one row per line, so the fee was counted
once per line.
Fix: aggregate the lines *first* (a subquery or CTE), then join one row to one
row. Chapter 9.

**"This 'unsold products' list is empty and I know it shouldn't be."**
Symptom: `LEFT JOIN order_items i ... WHERE i.quantity IS NULL` returns nothing.
Cause: `quantity` is `NOT NULL`, so it is NULL only in padded rows — that part is
fine — but the query also has `WHERE i.order_id > 0` somewhere, which discards
the padding.
Fix: test the primary key with `IS NULL`, and put *nothing else* about the
optional table in `WHERE`.

### The one-minute checklist

1. Write the subject table first.
2. Does every subject row have to survive? → `LEFT`, else `INNER`.
3. Is *absence* the answer? → add `WHERE right.pk IS NULL`.
4. Does the other side also need preserving? → `FULL OUTER`.
5. Every condition about the **optional** table goes in `ON`, never `WHERE`.
6. Count the subject's distinct rows before and after. They should match.
7. If you aggregate, check whether a fan-out multiplied the rows first.

### Watch out for

- **Defaulting to `INNER` because it is what `JOIN` types out.** It is the right
  answer often, but it should be a decision, not an accident.
- **Using `LEFT JOIN` everywhere "to be safe".** It is not safe; it hides the
  fact that you never decided, and it can mask genuine data bugs that an inner
  join would have made visible as a missing row.
- **`OUTER` on the wrong side.** If the subject is not the preserved table, the
  join is decorative.
""",
    [
        q("\"Show each customer and their total spend, including customers who have never bought anything.\" Which join?",
          ["LEFT JOIN from customers", "INNER JOIN", "FULL OUTER JOIN", "CROSS JOIN"], 0,
          "'Each customer ... including those with none' names the subject and demands its rows survive. Customers goes on the left, preserved, and COALESCE turns the resulting NULL sum into 0."),
        q("\"List the products that have never been ordered.\" Which shape?",
          ["LEFT JOIN order_items, then `WHERE order_items.id IS NULL`",
           "INNER JOIN order_items",
           "FULL OUTER JOIN order_items",
           "CROSS JOIN order_items"], 0,
          "'Never' means absence is the answer. Preserve products, then keep only the padded rows by testing the order_items primary key with IS NULL."),
        q("\"Reconcile our invoice list against the bank's, showing anything either side is missing.\"",
          ["FULL OUTER JOIN", "LEFT JOIN", "INNER JOIN", "Two separate LEFT JOINs and hope"], 0,
          "Both lists must survive, because a discrepancy can be in either direction. That is the one job only a FULL OUTER JOIN does in a single pass."),
        q("Your report should have one row per customer, but `COUNT(DISTINCT c.id)` after the join is 6 while `customers` has 8. What happened?",
          ["An inner join dropped the two customers with no match",
           "Two customers were deleted",
           "The GROUP BY is wrong",
           "COUNT(DISTINCT) does not work across joins"], 0,
          "The subject's distinct count fell, which only a filtering join can cause. Either switch to LEFT, or find the WHERE clause on the optional side that demoted an existing LEFT."),
        q("A `LEFT JOIN` query returns exactly as many rows as the same query with `INNER JOIN`. What does that tell you?",
          ["The LEFT is doing nothing — most likely a WHERE on the optional side demoted it",
           "The tables have the same number of rows",
           "The join condition uses the primary key",
           "Nothing; that is normal"], 0,
          "If no row was preserved, either every left row genuinely matched, or something after the join deleted the padded rows. In practice it is nearly always the second."),
        q("Which phrasing signals an INNER JOIN rather than a LEFT JOIN?",
          ["\"orders **with** their customer\"",
           "\"**each** order and its customer\"",
           "\"every order, **including** ones with no customer\"",
           "\"orders **without** a customer\""], 0,
          "'With' asserts both sides are present and required. 'Each' preserves the subject, 'including' explicitly asks for the empty ones, and 'without' is the anti-join."),
        q("Where must a condition on the *optional* table go in an outer join?",
          ["In the ON clause", "In the WHERE clause", "In a HAVING clause", "Either — they are equivalent"], 0,
          "ON is evaluated before unmatched rows are added back, so it narrows the match while preserving the subject. WHERE runs afterwards and deletes exactly the rows the outer join added."),
        q("\"Show a row for every salesperson x every month of the year, even months with no sales.\"",
          ["CROSS JOIN the two dimension lists, then LEFT JOIN the sales onto that grid",
           "INNER JOIN salespeople to sales",
           "FULL OUTER JOIN salespeople to sales",
           "LEFT JOIN salespeople to sales"], 0,
          "There is no relationship between a salesperson and a month, so a cross join builds the complete grid; the LEFT JOIN onto sales then fills in counts, leaving 0 where nothing happened."),
    ],
    [
        sq("sql_join_choice-each", "\"Each\" means preserve",
           "The request: **\"Show each customer and how many orders they have placed.\"** The word "
           "*each* decides the join. Fill it in. Columns: `customer`, `order_count` (0 when none). "
           "Order by `order_count` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS order_count\n"
           "FROM customers c\n"
           "LEFT JOIN orders o ON o.customer_id = c.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY order_count DESC, customer;",
           ["LEFT JOIN"],
           variants=("DELETE FROM order_items WHERE order_id = 109; DELETE FROM orders WHERE customer_id = 7;",),
           hint="Q1: customers is the subject. Q2: 'each' says every subject row must survive."),
        sq("sql_join_choice-with", "\"With\" means required",
           "The request: **\"List the orders **with** the name of the customer who placed them.\"** "
           "Here both sides are required, so the join is the plain one. Fill it in. "
           "Columns: `order_id`, `customer`. Order by `order_id`.",
           "shop",
           "SELECT o.id AS order_id, c.name AS customer\n"
           "FROM orders o\n"
           "JOIN customers c ON c.id = o.customer_id\n"
           "ORDER BY o.id;",
           ["JOIN"],
           hint="Q2 is 'no' — an order with no customer would be a data bug, not a report row."),
        sq("sql_join_choice-without", "\"Without\" means anti-join",
           "The request: **\"Which customers have never ordered anything?\"** Absence is the answer, so "
           "after the outer join you keep only the padded rows. Fill in the `WHERE`. "
           "Columns: `customer`, `city`. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer, c.city\n"
           "FROM customers c\n"
           "LEFT JOIN orders o ON o.customer_id = c.id\n"
           "WHERE o.id IS NULL\n"
           "ORDER BY c.name;",
           ["o.id IS NULL"],
           variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 8, '2023-12-02', 'pending', 'web');",),
           hint="Q3 is 'non-matches'. Test the *primary key* of the optional table."),
        sq("sql_join_choice-oncond", "Rule 5: conditions on the optional side go in ON",
           "The request: **\"Show each customer and how many **shipped** orders they have.\"** The status "
           "test must not delete the customers who have none. Fill in the whole `ON` clause. "
           "Columns: `customer`, `shipped_orders`. Order by `shipped_orders` desc, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS shipped_orders\n"
           "FROM customers c\n"
           "LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped'\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY shipped_orders DESC, customer;",
           ["o.customer_id = c.id AND o.status = 'shipped'"],
           variants=("UPDATE orders SET status = 'pending' WHERE customer_id = 1;",),
           hint="Both the key match and the status test, joined by AND, inside ON."),
        sq("sql_join_choice-check", "The counting check",
           "Prove a join filtered your subject. Return one row: `all_customers` (how many customers "
           "exist) and `joined_customers` (how many distinct customers survive an INNER JOIN to orders). "
           "Fill in the second expression.",
           "shop",
           "SELECT\n"
           "  (SELECT COUNT(*) FROM customers) AS all_customers,\n"
           "  (SELECT COUNT(DISTINCT c.id) FROM customers c JOIN orders o ON o.customer_id = c.id) AS joined_customers;",
           ["COUNT(DISTINCT c.id)"],
           variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 6, '2023-12-01', 'shipped', 'web');",),
           hint="You want distinct customers, not joined rows — otherwise the fan-out inflates it."),
        sq("sql_join_choice-fanout", "The fan-out check",
           "Prove a join multiplied your subject. Return one row: `order_rows` (rows in `orders`) and "
           "`joined_rows` (rows after joining orders to their lines). Fill in the second expression.",
           "shop",
           "SELECT\n"
           "  (SELECT COUNT(*) FROM orders) AS order_rows,\n"
           "  (SELECT COUNT(*) FROM orders o JOIN order_items i ON i.order_id = o.id) AS joined_rows;",
           ["(SELECT COUNT(*) FROM orders o JOIN order_items i ON i.order_id = o.id)"],
           variants=("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (21, 113, 1, 1, 79.50);",),
           hint="A plain COUNT(*) over the joined result — the number you compare against the unjoined count."),
        sq("sql_join_choice-cross", "\"Every combination\" means CROSS",
           "The request: **\"A row for every city x every order status, even the combinations that never "
           "happened.\"** There is no relationship between the two, so fill in the join that produces "
           "every pairing. Columns: `city`, `status`. Order by `city`, then `status`.",
           "shop",
           "SELECT ci.city, st.status\n"
           "FROM (SELECT DISTINCT city FROM customers WHERE city IS NOT NULL) ci\n"
           "CROSS JOIN (SELECT DISTINCT status FROM orders) st\n"
           "ORDER BY ci.city, st.status;",
           ["CROSS JOIN"],
           hint="The special case that skips all four questions."),

        chal("sql_join_choice-diagnose", "Diagnose and fix the demoted join",
             "This report is meant to show **every** customer with their shipped-order count, but a filter "
             "in the wrong clause is deleting the customers who have none:\n\n"
             "```sql\n"
             "SELECT c.name, COUNT(o.id)\n"
             "FROM customers c\n"
             "LEFT JOIN orders o ON o.customer_id = c.id\n"
             "WHERE o.status = 'shipped'\n"
             "GROUP BY c.id, c.name;\n"
             "```\n\n"
             "Write the fixed version. Columns: `customer`, `shipped_orders` (0 when none). "
             "Order by `shipped_orders` descending, then `customer` ascending. All 8 customers must appear.",
             "shop",
             "SELECT c.name AS customer, COUNT(o.id) AS shipped_orders\n"
             "FROM customers c\n"
             "LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped'\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY shipped_orders DESC, customer;",
             variants=("UPDATE orders SET status = 'cancelled' WHERE customer_id IN (1, 5);",),
             hint="Move the status test out of WHERE and into ON. Nothing else needs to change.",
             difficulty="Medium"),
        chal("sql_join_choice-report", "One report, four decisions",
             "Build the category report described in the lesson: for **every** category — including ones "
             "with no products and ones whose products never sold — show `category` and `revenue`, the "
             "total `quantity * unit_price` over **shipped** orders only, rounded to 2 decimals and `0.0` "
             "when there is none. Order by `revenue` descending, then `category` ascending.",
             "shop",
             "SELECT cat.name AS category,\n"
             "       ROUND(COALESCE(SUM(i.quantity * i.unit_price), 0), 2) AS revenue\n"
             "FROM categories cat\n"
             "LEFT JOIN products    p ON p.category_id = cat.id\n"
             "LEFT JOIN order_items i ON i.product_id = p.id\n"
             "LEFT JOIN orders      o ON o.id = i.order_id AND o.status = 'shipped'\n"
             "GROUP BY cat.id, cat.name\n"
             "ORDER BY revenue DESC, category;",
             variants=("UPDATE orders SET status = 'cancelled' WHERE channel = 'app';",),
             hint="Categories is the subject, so it leads and every join below it is LEFT. The status filter belongs in the last ON — in WHERE it would delete Toys.",
             difficulty="Medium"),
        chal("sql_join_choice-mixed", "Two different joins in one query",
             "For every **product** — including ones never sold — show `product`, `category` and "
             "`units_sold` (0 when none). A product's category is required (inner), its sales are optional "
             "(outer). Order by `units_sold` descending, then `product` ascending.",
             "shop",
             "SELECT p.name AS product, cat.name AS category, COALESCE(SUM(i.quantity), 0) AS units_sold\n"
             "FROM products p\n"
             "JOIN categories cat ON cat.id = p.category_id\n"
             "LEFT JOIN order_items i ON i.product_id = p.id\n"
             "GROUP BY p.id, p.name, cat.name\n"
             "ORDER BY units_sold DESC, product;",
             variants=("DELETE FROM order_items WHERE product_id = 1;",),
             hint="Run the four questions separately for each joined table. Categories: required. Order lines: optional.",
             difficulty="Medium"),
        chal("sql_join_choice-active", "\"Only\" means inner",
             "The request: **\"Which customers have placed at least one order on **both** the web and the "
             "app?\"** Show `customer`. Order by `customer`.",
             "shop",
             "SELECT c.name AS customer\n"
             "FROM customers c\n"
             "JOIN orders o ON o.customer_id = c.id\n"
             "GROUP BY c.id, c.name\n"
             "HAVING COUNT(DISTINCT o.channel) = 2\n"
             "ORDER BY customer;",
             variants=("UPDATE orders SET channel = 'web' WHERE customer_id = 1;",),
             hint="'At least one' is presence, so the join is inner. Then a HAVING on the count of distinct channels expresses 'both'.",
             difficulty="Medium"),
    ],
)
