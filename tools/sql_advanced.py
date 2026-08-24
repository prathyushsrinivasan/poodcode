# -*- coding: utf-8 -*-
"""SQL track, chapters 14-16: set operations, NULL semantics, and query plans.

Exec'd by tools/gen_seed.py last, in the same namespace as the other chapters.
"""

# ===========================================================================
# 14. Set operations
# ===========================================================================

concept(
    "sql_set_ops",
    "SQL: Sets & NULLs",
    "UNION, INTERSECT & EXCEPT",
    "Stack and compare whole result sets — and know when a set operator beats a join.",
    "Joins combine tables sideways, adding columns; set operators combine them vertically, "
    "adding rows. That makes them the natural tool whenever two queries produce the same shape "
    "and you want them treated as one list: this month's customers plus last month's, the "
    "accounts in system A but not in system B, the products that appear on both lists. The one "
    "detail that costs people real money is UNION versus UNION ALL — plain UNION sorts and "
    "de-duplicates every time, which is wasted work when the inputs are already disjoint and "
    "is silently destructive when a legitimately repeated row gets folded away.",
    """
```sql
SELECT city FROM customers
UNION                      -- distinct rows from both  (sorts + de-duplicates)
SELECT city FROM suppliers;

SELECT ... UNION ALL ...   -- everything, duplicates kept  (no sort: cheaper)
SELECT ... INTERSECT ...   -- rows present in BOTH        (distinct)
SELECT ... EXCEPT ...      -- rows in the first, not the second  (distinct)
```

Rules that apply to all four:

- both sides need the **same number of columns**, in a compatible order;
- column **names come from the first** query;
- **`ORDER BY` goes at the very end**, once, and applies to the combined result;
- `NULL` counts as a value here — `UNION`, `INTERSECT` and `EXCEPT` all treat two
  NULLs as equal, unlike `=`.

| you want | operator |
|---|---|
| both lists, no duplicates | `UNION` |
| both lists, keep everything | `UNION ALL` |
| in both | `INTERSECT` |
| in the first only | `EXCEPT` |
""",
    """
### `UNION` versus `UNION ALL`

They differ in exactly one way and it matters twice:

```sql
SELECT city FROM customers UNION     SELECT city FROM owners;   -- distinct cities
SELECT city FROM customers UNION ALL SELECT city FROM owners;   -- every row, duplicates kept
```

**Cost.** `UNION` must compare every row against every other, so it sorts (or
hashes) the whole result. On large inputs that is the dominant cost of the query.
`UNION ALL` streams both sides straight through.

**Correctness.** If two rows are *supposed* to be there twice — two orders on the
same day for the same amount, two identical log lines — `UNION` silently merges
them into one. That is a data-loss bug that looks like a rounding error.

**The rule:** write `UNION ALL` unless you actively need de-duplication. When the
inputs are disjoint by construction (this month's rows and last month's rows),
`UNION` is pure waste.

### `INTERSECT` and `EXCEPT`

```sql
-- Customers who ordered in both March and April
SELECT customer_id FROM orders WHERE order_date LIKE '2023-03%'
INTERSECT
SELECT customer_id FROM orders WHERE order_date LIKE '2023-04%';

-- Customers who ordered in March but not April
SELECT customer_id FROM orders WHERE order_date LIKE '2023-03%'
EXCEPT
SELECT customer_id FROM orders WHERE order_date LIKE '2023-04%';
```

Both de-duplicate, and both are *set* operations — so `EXCEPT` is "in the first
and not the second", not "subtract one occurrence".

`EXCEPT` is often the most readable way to write an anti-join, especially when
the comparison is on several columns at once:

```sql
-- Rows in the export that are missing from the import, on a three-column key
SELECT account, period, amount FROM export
EXCEPT
SELECT account, period, amount FROM import;
```

Doing that with `NOT EXISTS` needs three correlated equality tests and a
`IS NOT DISTINCT FROM` dance if any column is nullable. `EXCEPT` compares NULLs
as equal for free.

### Set operator or join?

| question | reach for |
|---|---|
| "combine two similar lists into one" | `UNION ALL` |
| "which ids are in both lists" | `INTERSECT` (or `EXISTS`) |
| "which ids are only in list A" | `EXCEPT` (or `NOT EXISTS` / anti-join) |
| "attach B's columns to A's rows" | a **join** — no set operator can do this |
| "compare whole rows across several columns" | `EXCEPT` — it handles NULLs |

The dividing line: a set operator needs both sides to have the **same shape** and
gives you no way to see columns from both at once. The moment you want A's name
next to B's total, it has to be a join.

### Ordering and parentheses

```sql
SELECT name, 'customer' AS kind FROM customers
UNION ALL
SELECT name, 'owner'    AS kind FROM owners
ORDER BY kind, name;               -- once, at the very end
```

A tagging column like `kind` is the standard trick for keeping track of which
branch a row came from — worth adding whenever the two sides are not obviously
distinguishable.

`ORDER BY` inside a branch is not allowed (except with a `LIMIT`, and even then it
applies before the union). If you need per-branch ordering or limiting, wrap each
branch in a subquery or CTE.

Chained operators evaluate **left to right**, and `INTERSECT` does *not* bind
tighter than `UNION` in SQLite. Parenthesise anything non-obvious:

```sql
(SELECT ... UNION SELECT ...) EXCEPT SELECT ...
```

### Emulating `FULL OUTER JOIN`

Chapter 4's workaround, now that the operator makes sense:

```sql
SELECT o.name AS owner, p.name AS pet FROM owners o LEFT JOIN pets p ON p.owner_id = o.id
UNION ALL
SELECT NULL, p.name FROM pets p WHERE p.owner_id IS NULL;
```

`UNION ALL`, not `UNION` — two owners could legitimately share a name.

### Watch out for

- **`UNION` where `UNION ALL` was meant**: slower, and it silently drops genuine
  duplicates.
- **Mismatched column counts** is an error; mismatched column *meanings* is not.
  `SELECT a, b UNION SELECT b, a` runs happily and is nonsense.
- **Column names come from the first branch only.** Alias there.
- **`ORDER BY` in the middle** is a syntax error in SQLite.
- **`EXCEPT` is not subtraction.** Three copies minus one copy leaves nothing,
  not two.
""",
    [
        q("What is the only difference between `UNION` and `UNION ALL`?",
          ["UNION removes duplicate rows, which costs a sort; UNION ALL keeps everything",
           "UNION requires the same column names",
           "UNION ALL only works with two queries",
           "UNION sorts the output by the first column"], 0,
          "De-duplication is the whole difference, and it has both a cost (a sort or hash over the whole result) and a risk (genuinely repeated rows are merged away)."),
        q("Where do the output column names of a set operation come from?",
          ["The first query", "The last query", "Both must match exactly", "They are unnamed"], 0,
          "Only the first branch's names (or aliases) survive, so that is where the aliasing has to happen."),
        q("How do `UNION`, `INTERSECT` and `EXCEPT` treat two NULLs?",
          ["As equal — unlike `=`, which would return unknown",
           "As different, like `=` does",
           "They reject NULLs",
           "It depends on the engine"], 0,
          "Set operators compare rows by identity, not with `=`. That is what makes EXCEPT such a clean way to diff two tables whose columns are nullable."),
        q("Where does `ORDER BY` go in a `UNION` query?",
          ["Once, at the very end, applying to the combined result",
           "In each branch",
           "Immediately before UNION",
           "It is not allowed at all"], 0,
          "A branch-level ORDER BY is a syntax error in SQLite (barring a LIMIT). If you need per-branch ordering, wrap each branch in a subquery."),
        q("Which question can a set operator NOT answer?",
          ["\"Show each customer's name next to their order total\"",
           "\"Which ids appear in both lists\"",
           "\"Which ids are only in list A\"",
           "\"Combine last month's and this month's rows\""], 0,
          "Set operators stack rows of the same shape. Putting one table's columns beside another's is what a join is for."),
        q("`SELECT x FROM a EXCEPT SELECT x FROM b` where `a` has three copies of `1` and `b` has one. What comes back?",
          ["Nothing — EXCEPT is a set operation, not subtraction",
           "Two rows of `1`", "One row of `1`", "Three rows of `1`"], 0,
          "EXCEPT asks whether the value appears in b at all. It does, so every copy is excluded. Multiset subtraction is not what it does."),
    ],
    [
        sq("sql_set_ops-unionall", "Stack two lists",
           "Build one list of every person in the shop and every owner of a pet — sorry, of every "
           "customer and every category name, tagged by where it came from. Fill in the operator that "
           "keeps everything. Columns: `label`, `kind`. Order by `kind`, then `label`.",
           "shop",
           "SELECT name AS label, 'customer' AS kind FROM customers\n"
           "UNION ALL\n"
           "SELECT name AS label, 'category' AS kind FROM categories\n"
           "ORDER BY kind, label;",
           ["UNION ALL"],
           variants=("INSERT INTO categories (id, name) VALUES (6, 'Ada');",),
           hint="Two words. Plain UNION would de-duplicate, merging a customer and a category that share a name."),
        sq("sql_set_ops-union", "Distinct cities from two sources",
           "List every distinct city, whether it comes from a customer or from the literal list of "
           "warehouse cities below. Fill in the operator that removes duplicates. "
           "Columns: `city`. Order by `city`.",
           "shop",
           "SELECT city FROM customers WHERE city IS NOT NULL\n"
           "UNION\n"
           "SELECT 'Faro'\n"
           "ORDER BY city;",
           ["UNION"],
           variants=("UPDATE customers SET city = 'Faro' WHERE id <= 4;",),
           hint="One word, and it is the more expensive of the two because it has to sort."),
        sq("sql_set_ops-intersect", "In both months",
           "Find the customers who ordered in **both** March and April 2023. Fill in the operator. "
           "Columns: `customer_id`. Order by `customer_id`.",
           "shop",
           "SELECT customer_id FROM orders WHERE order_date LIKE '2023-03%'\n"
           "INTERSECT\n"
           "SELECT customer_id FROM orders WHERE order_date LIKE '2023-04%'\n"
           "ORDER BY customer_id;",
           ["INTERSECT"],
           variants=("UPDATE orders SET order_date = '2023-04-25' WHERE id = 103;",),
           hint="One word, and like UNION it de-duplicates."),
        sq("sql_set_ops-except", "In the first, not the second",
           "Find the customers who ordered in March 2023 but **not** in April. Fill in the operator. "
           "Columns: `customer_id`. Order by `customer_id`.",
           "shop",
           "SELECT customer_id FROM orders WHERE order_date LIKE '2023-03%'\n"
           "EXCEPT\n"
           "SELECT customer_id FROM orders WHERE order_date LIKE '2023-04%'\n"
           "ORDER BY customer_id;",
           ["EXCEPT"],
           variants=("UPDATE orders SET order_date = '2023-04-25' WHERE id = 101;",),
           hint="One word. It asks about presence, not about counts."),
        sq("sql_set_ops-tag", "Tag which side a row came from",
           "When two branches produce similar-looking rows, add a literal column saying which is which. "
           "Fill in the tag on the second branch. Columns: `name`, `source`. "
           "Order by `source`, then `name`.",
           "hr",
           "SELECT name, 'employee' AS source FROM employees WHERE dept_id = 1\n"
           "UNION ALL\n"
           "SELECT name, 'department' AS source FROM departments\n"
           "ORDER BY source, name;",
           ["'department' AS source"],
           hint="A string literal aliased to the same column name the first branch used."),
        sq("sql_set_ops-diff", "Diff two whole rows",
           "Which `(product_id, quantity)` pairs appear on order 101 but not on order 111? Fill in the "
           "operator that compares whole rows and handles NULLs as equal. "
           "Columns: `product_id`, `quantity`. Order by `product_id`.",
           "shop",
           "SELECT product_id, quantity FROM order_items WHERE order_id = 101\n"
           "EXCEPT\n"
           "SELECT product_id, quantity FROM order_items WHERE order_id = 111\n"
           "ORDER BY product_id;",
           ["EXCEPT"],
           variants=("UPDATE order_items SET quantity = 2 WHERE order_id = 111;",),
           hint="The set-difference operator compares the whole row, across both columns at once."),

        chal("sql_set_ops-fullouter", "FULL OUTER JOIN, emulated",
             "Without using `FULL OUTER JOIN`, produce the same six rows: every owner with their pet, "
             "plus the pet that has no owner. Show `owner` and `pet`. "
             "Order by `owner`, then `pet`.",
             "pets",
             "SELECT o.name AS owner, p.name AS pet\n"
             "FROM owners o LEFT JOIN pets p ON p.owner_id = o.id\n"
             "UNION ALL\n"
             "SELECT NULL AS owner, p.name AS pet\n"
             "FROM pets p WHERE p.owner_id IS NULL\n"
             "ORDER BY owner, pet;",
             variants=("UPDATE pets SET owner_id = NULL WHERE name IN ('Otto', 'Pip');",),
             hint="A LEFT JOIN for the owner side, then UNION ALL the pets that matched nobody. UNION ALL, because two owners could share a name.",
             difficulty="Medium"),
        chal("sql_set_ops-churn", "Who came, went and stayed",
             "Classify every customer who ordered in the first half of 2023 (`order_date < '2023-07-01'`) "
             "or the second half, into `both`, `first half only` or `second half only`. "
             "Show `customer` and `period`. Order by `period`, then `customer`.",
             "shop",
             "WITH h1 AS (SELECT DISTINCT customer_id FROM orders WHERE order_date < '2023-07-01'),\n"
             "     h2 AS (SELECT DISTINCT customer_id FROM orders WHERE order_date >= '2023-07-01')\n"
             "SELECT c.name AS customer, 'both' AS period\n"
             "FROM (SELECT customer_id FROM h1 INTERSECT SELECT customer_id FROM h2) x\n"
             "JOIN customers c ON c.id = x.customer_id\n"
             "UNION ALL\n"
             "SELECT c.name, 'first half only'\n"
             "FROM (SELECT customer_id FROM h1 EXCEPT SELECT customer_id FROM h2) x\n"
             "JOIN customers c ON c.id = x.customer_id\n"
             "UNION ALL\n"
             "SELECT c.name, 'second half only'\n"
             "FROM (SELECT customer_id FROM h2 EXCEPT SELECT customer_id FROM h1) x\n"
             "JOIN customers c ON c.id = x.customer_id\n"
             "ORDER BY period, customer;",
             variants=("UPDATE orders SET order_date = '2023-02-01' WHERE id > 106;",),
             hint="Two CTEs for the two halves, then INTERSECT and two EXCEPTs, stacked with UNION ALL and joined back to get the names.",
             difficulty="Medium"),
        chal("sql_set_ops-catalogue", "One catalogue, two kinds of row",
             "Produce a single list of everything sellable: every product as `Electronics: Headphones` "
             "and every category that currently has no products as `Empty: Toys`. "
             "Show `entry` and `kind` (`product` or `empty category`). "
             "Order by `kind`, then `entry`.",
             "shop",
             "SELECT cat.name || ': ' || p.name AS entry, 'product' AS kind\n"
             "FROM products p JOIN categories cat ON cat.id = p.category_id\n"
             "UNION ALL\n"
             "SELECT 'Empty: ' || c.name, 'empty category'\n"
             "FROM categories c\n"
             "WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.category_id = c.id)\n"
             "ORDER BY kind, entry;",
             variants=("DELETE FROM order_items WHERE product_id IN (8,9,10); DELETE FROM products WHERE category_id = 4;",),
             hint="Two differently-shaped queries made to line up: `||` builds the label in each, and a literal supplies the kind.",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 15. NULL semantics
# ===========================================================================

concept(
    "sql_nulls",
    "SQL: Sets & NULLs",
    "NULL & Three-Valued Logic",
    "NULL means unknown, so comparing it gives unknown — and unknown is not true.",
    "SQL does not have two truth values, it has three: true, false and unknown. NULL is the "
    "value that produces unknown, and because WHERE keeps only rows where the condition is "
    "true, a row can fail both a condition and its negation at once. That single rule explains "
    "almost every NULL surprise there is: why x = NULL never matches, why NOT IN collapses, "
    "why an outer join's padded rows disappear when you filter on them, why COUNT(*) and "
    "COUNT(col) disagree, and why the empty string and NULL behave nothing alike despite "
    "looking identical in a result grid. Learn the rule and the surprises stop being surprises.",
    """
```
   NULL = NULL        -> unknown        NULL IS NULL      -> true
   NULL <> 1          -> unknown        NULL IS NOT NULL  -> false
   NULL + 1           -> NULL           'a' || NULL       -> NULL
   true  AND unknown  -> unknown        true  OR unknown  -> true
   false AND unknown  -> false          false OR unknown  -> unknown
```

**`WHERE` keeps only `true`.** Both `unknown` and `false` are discarded, which is
why a row can fail `x = 1` *and* `x <> 1`.

| what you want | write |
|---|---|
| is it missing | `x IS NULL` |
| substitute a default | `COALESCE(x, 0)` |
| NULL-safe equality | `x IS y` (SQLite) — `IS NOT DISTINCT FROM` elsewhere |
| turn a value into NULL | `NULLIF(x, 0)` — handy against divide-by-zero |
| absence, safely | `NOT EXISTS` — never `NOT IN` |
""",
    """
### Unknown is not false

```sql
SELECT COUNT(*) FROM responses WHERE q1_score = 5;      -- rows scoring 5
SELECT COUNT(*) FROM responses WHERE q1_score <> 5;     -- rows scoring anything else?
```

Add those two together and you do **not** get the row count. The rows where
`q1_score IS NULL` fail both, because `NULL = 5` and `NULL <> 5` are each
*unknown*, and `WHERE` keeps only `true`. To include them you must say so:

```sql
WHERE q1_score <> 5 OR q1_score IS NULL
```

This is the origin of most "my filters do not add up" bug reports.

### `IS NULL`, and SQLite's `IS`

`= NULL` is never true, so there is a separate operator:

```sql
WHERE comment IS NULL           -- correct
WHERE comment = NULL            -- matches nothing, ever
```

SQLite also has a NULL-safe equality, which treats two NULLs as equal:

```sql
WHERE a IS b                    -- true when both are NULL, or both equal
```

The standard spelling is `IS NOT DISTINCT FROM`; Postgres uses that, MySQL spells
it `<=>`. Useful when comparing two nullable columns for a diff.

### `NULL` versus the empty string

They look the same in most result grids and behave completely differently:

```sql
SELECT COUNT(*)          FROM responses;                       -- 6  every row
SELECT COUNT(comment)    FROM responses;                       -- 4  non-NULL comments
SELECT COUNT(*)          FROM responses WHERE comment = '';    -- 1  the empty one
SELECT COUNT(*)          FROM responses WHERE comment IS NULL; -- 2  the missing ones
SELECT length(comment)   FROM responses WHERE id = 5;          -- 0
SELECT length(comment)   FROM responses WHERE id = 4;          -- NULL
```

`''` is a known value that happens to be empty. `NULL` is the absence of a value.
Deciding which one your column uses — and then being consistent — saves a lot of
`COALESCE(comment, '')` further downstream.

### Arithmetic and concatenation propagate NULL

```sql
q1_score + q2_score              -- NULL if EITHER is NULL
'Dear ' || name || ','           -- NULL if name is NULL, not "Dear ,"
COALESCE(q1_score, 0) + COALESCE(q2_score, 0)   -- 0 for missing
```

One NULL anywhere in an expression poisons the whole thing. String building is
where this bites hardest, because a single missing middle name turns an entire
formatted address into `NULL`.

### Aggregates skip NULL — except `COUNT(*)`

```sql
SELECT COUNT(*)      AS rows,       -- 6
       COUNT(q1_score) AS answered,  -- 4
       SUM(q1_score)   AS total,     -- 32
       AVG(q1_score)   AS mean       -- 8.0   = 32 / 4, NOT 32 / 6
FROM responses;
```

`AVG` divides by the number of non-NULL values. If "no answer" should count as
zero, say it explicitly:

```sql
SUM(q1_score) * 1.0 / COUNT(*)      -- 5.33: treats missing as 0
```

Both are defensible; they answer different questions, and a report should be
clear about which.

And over **zero rows**: `COUNT` gives `0`, everything else gives `NULL`.

### `NOT IN` — the trap, restated

Because it deserves saying twice:

```sql
WHERE segment NOT IN (SELECT segment FROM respondents)   -- ZERO ROWS, always
```

`respondents.segment` contains a NULL (Chen's), so one of the expanded
comparisons is `x <> NULL` — unknown — and `true AND unknown` is unknown. Use
`NOT EXISTS`, or filter the NULLs out of the subquery.

### Sorting and grouping

- **`ORDER BY`**: SQLite sorts NULLs **first** ascending, last descending.
  Postgres does the opposite by default. `ORDER BY x IS NULL, x` forces NULLs
  last portably. SQLite 3.30+ also supports `NULLS LAST`.
- **`GROUP BY`**: all NULLs form **one group**, so a NULL city is a group, not
  thirteen groups.
- **`DISTINCT`**: keeps one NULL.
- **`UNIQUE` constraints**: allow *many* NULLs, because two NULLs are not equal
  for constraint purposes. A "unique email" column that permits NULL permits any
  number of rows with no email.

So `GROUP BY`, `DISTINCT` and the set operators treat NULLs as equal, while `=`,
`JOIN ... ON` and `UNIQUE` do not. That inconsistency is standard, deliberate,
and worth memorising rather than reasoning about.

### Joining on a nullable column

```sql
FROM employees e JOIN departments d ON d.id = e.dept_id
```

`Dov` has `dept_id IS NULL`, so `NULL = 4` is unknown and he is dropped. A
nullable foreign key is a strong hint that the relationship is optional — and
that the join should have been `LEFT`.

### Watch out for

- **`= NULL`** matches nothing. Use `IS NULL`.
- **`NOT IN` with any NULL** returns nothing.
- **`x <> 'a'` excludes NULLs** as well as `'a'`.
- **`SUM` over no rows is NULL**, not `0`.
- **`COUNT(col)` ≠ `COUNT(*)`** whenever the column is nullable.
- **`UNIQUE` does not stop repeated NULLs.**
- **`CASE WHEN x = NULL`** never fires; use `CASE WHEN x IS NULL`.
""",
    [
        q("What does `WHERE q1_score <> 5` do to rows where `q1_score IS NULL`?",
          ["It excludes them — `NULL <> 5` is unknown, and WHERE keeps only true",
           "It includes them",
           "It raises an error",
           "It includes them only if the column is nullable"], 0,
          "A row can fail both `= 5` and `<> 5`. To include the missing ones you have to say `OR q1_score IS NULL` explicitly."),
        q("`SELECT 'Dear ' || name || ','` where `name` is NULL returns what?",
          ["NULL — one NULL poisons the whole expression",
           "'Dear ,'", "'Dear NULL,'", "An empty string"], 0,
          "Concatenation and arithmetic both propagate NULL. Wrap the nullable part in COALESCE if you want a placeholder instead."),
        q("`responses` has 6 rows and 4 non-NULL `q1_score` values summing to 32. What is `AVG(q1_score)`?",
          ["8.0 — AVG divides by the count of non-NULL values",
           "5.33 — it divides by the row count",
           "NULL", "32"], 0,
          "AVG ignores NULLs in both the numerator and the denominator. If missing should count as zero, write `SUM(q1_score) * 1.0 / COUNT(*)` and say so in the column name."),
        q("How do `GROUP BY` and `DISTINCT` treat NULLs?",
          ["As equal to each other — all NULLs form one group, and DISTINCT keeps one",
           "As distinct from each other",
           "They exclude NULLs",
           "They raise an error"], 0,
          "Grouping, DISTINCT and the set operators compare by identity and treat NULLs as the same. `=`, join conditions and UNIQUE constraints do not. The inconsistency is standard."),
        q("A `UNIQUE` column allows NULL. How many NULL rows can it hold?",
          ["Any number — two NULLs are not equal for constraint purposes",
           "Exactly one", "None", "Two"], 0,
          "Because NULL = NULL is unknown rather than true, a uniqueness check never fires between two NULLs. A 'unique email' column that permits NULL permits unlimited rows with no email."),
        q("What is the difference between `''` and `NULL` in a TEXT column?",
          ["`''` is a known value of length 0; NULL is the absence of a value, and `length(NULL)` is NULL",
           "There is none in SQLite",
           "`''` is stored as NULL",
           "NULL is shorter"], 0,
          "They print the same in most grids and behave differently everywhere else: COUNT(col) counts the empty string but not the NULL, and `col = ''` never matches a NULL."),
        q("How do you make NULLs sort last in SQLite, portably?",
          ["`ORDER BY x IS NULL, x` — the boolean sorts false (0) before true (1)",
           "`ORDER BY x DESC`", "`ORDER BY COALESCE(x, 0)`", "NULLs always sort last"], 0,
          "SQLite puts NULLs first ascending; Postgres puts them last. Sorting by the `IS NULL` flag first works the same way everywhere, and SQLite 3.30+ also accepts `NULLS LAST`."),
        q("Why should you use `NOT EXISTS` instead of `NOT IN` against a nullable column?",
          ["A single NULL in the list makes the whole NOT IN condition unknown, so it returns no rows",
           "NOT EXISTS is always faster",
           "NOT IN cannot take a subquery",
           "NOT EXISTS ignores NULLs in the outer table"], 0,
          "NOT IN expands to a chain of `<>` tests ANDed together, and `x <> NULL` is unknown forever. NOT EXISTS asks about row existence and never performs that comparison."),
    ],
    [
        sq("sql_nulls-isnull", "Test for absence",
           "Find the responses that have no comment at all. `= NULL` would match nothing — fill in the "
           "operator that works. Columns: `id`, `respondent_id`. Order by `id`.",
           "survey",
           "SELECT id, respondent_id\nFROM responses\nWHERE comment IS NULL\nORDER BY id;",
           ["IS NULL"],
           variants=("UPDATE responses SET comment = NULL WHERE id = 1;",),
           hint="Two words, and it is an operator in its own right rather than a comparison."),
        sq("sql_nulls-orisnull", "Do not lose the unknowns",
           "Find every response that did **not** score 9 on q1 — including the ones that gave no score "
           "at all. Fill in the extra condition. Columns: `id`, `q1_score`. Order by `id`.",
           "survey",
           "SELECT id, q1_score\nFROM responses\nWHERE q1_score <> 9 OR q1_score IS NULL\nORDER BY id;",
           ["OR q1_score IS NULL"],
           variants=("UPDATE responses SET q1_score = 9 WHERE id = 3;",),
           hint="`<>` alone silently drops the NULLs, so add the missing case explicitly."),
        sq("sql_nulls-counts", "Three counts that disagree",
           "Show why `COUNT(*)` and `COUNT(col)` are different. Fill in the three count expressions. "
           "Columns: `all_rows`, `with_q1`, `with_comment`.",
           "survey",
           "SELECT COUNT(*) AS all_rows, COUNT(q1_score) AS with_q1, COUNT(comment) AS with_comment\n"
           "FROM responses;",
           ["COUNT(*) AS all_rows, COUNT(q1_score) AS with_q1, COUNT(comment) AS with_comment"],
           variants=("UPDATE responses SET comment = NULL;",),
           hint="COUNT(*) counts rows; COUNT(column) counts non-NULL values. Note the empty-string comment still counts."),
        sq("sql_nulls-coalesce", "Substitute a default",
           "Show each response's total score, treating a missing answer as 0 instead of poisoning the "
           "sum. Fill in the expression. Columns: `id`, `total`. Order by `id`.",
           "survey",
           "SELECT id, COALESCE(q1_score, 0) + COALESCE(q2_score, 0) AS total\n"
           "FROM responses\nORDER BY id;",
           ["COALESCE(q1_score, 0) + COALESCE(q2_score, 0)"],
           variants=("UPDATE responses SET q2_score = 4 WHERE q2_score IS NULL;",),
           hint="Wrap each nullable term separately — COALESCE around the whole sum would be too late."),
        sq("sql_nulls-emptyvsnull", "Empty string is not NULL",
           "Distinguish the three states of `comment`: missing, empty, and present. Fill in the CASE "
           "expression. Columns: `id`, `state`. Order by `id`.",
           "survey",
           "SELECT id,\n"
           "       CASE WHEN comment IS NULL THEN 'missing'\n"
           "            WHEN comment = '' THEN 'empty'\n"
           "            ELSE 'present' END AS state\n"
           "FROM responses\n"
           "ORDER BY id;",
           ["CASE WHEN comment IS NULL THEN 'missing'\n            WHEN comment = '' THEN 'empty'\n            ELSE 'present' END"],
           variants=("UPDATE responses SET comment = '' WHERE comment IS NULL;",),
           hint="Test IS NULL first — `comment = ''` would be unknown for a NULL and fall through to ELSE."),
        sq("sql_nulls-sort", "Push NULLs to the bottom",
           "Order the respondents by segment with the unknown segment last, portably. Fill in the "
           "`ORDER BY`. Columns: `name`, `segment`.",
           "survey",
           "SELECT name, segment\nFROM respondents\nORDER BY segment IS NULL, segment, name;",
           ["segment IS NULL, segment, name"],
           variants=("UPDATE respondents SET segment = NULL WHERE name = 'Ada';",),
           hint="Sort by the boolean flag first — false (0) sorts before true (1) — then by the value."),
        sq("sql_nulls-nullif", "Guard a division",
           "Compute each session's average milliseconds per page view without dividing by zero. Fill in "
           "the function that turns a `0` denominator into NULL. Columns: `session_id`, `avg_ms`. "
           "Order by `session_id`.",
           "events",
           "SELECT s.id AS session_id,\n"
           "       ROUND(COALESCE(SUM(v.ms_on_page), 0) * 1.0 / NULLIF(COUNT(v.id), 0), 1) AS avg_ms\n"
           "FROM sessions s\n"
           "LEFT JOIN page_views v ON v.session_id = s.id\n"
           "GROUP BY s.id\n"
           "ORDER BY s.id;",
           ["NULLIF(COUNT(v.id), 0)"],
           variants=("DELETE FROM page_views WHERE session_id <= 4;",),
           hint="`NULLIF(a, b)` returns NULL when a equals b — so a zero count becomes NULL and the division yields NULL rather than erroring."),
        sq("sql_nulls-safeeq", "NULL-safe equality",
           "Find the pairs of respondents who share a segment — **including two whose segment is both "
           "NULL**. Fill in SQLite's NULL-safe comparison. Columns: `a`, `b`. Order by `a`, then `b`.",
           "survey",
           "SELECT x.name AS a, y.name AS b\n"
           "FROM respondents x\n"
           "JOIN respondents y ON x.segment IS y.segment AND y.id > x.id\n"
           "ORDER BY a, b;",
           ["x.segment IS y.segment"],
           variants=("UPDATE respondents SET segment = NULL WHERE name IN ('Dara', 'Elif');",),
           hint="SQLite's `IS` compares two values treating NULLs as equal — the standard spells it IS NOT DISTINCT FROM."),

        chal("sql_nulls-notin", "The NOT IN trap, fixed",
             "List the respondents who have **never** submitted a response with a q2 score. Write it so "
             "the NULLs in `q2_score` cannot collapse the result to nothing. Show `name`. Order by `name`.",
             "survey",
             "SELECT r.name\n"
             "FROM respondents r\n"
             "WHERE NOT EXISTS (\n"
             "  SELECT 1 FROM responses s WHERE s.respondent_id = r.id AND s.q2_score IS NOT NULL\n"
             ")\n"
             "ORDER BY r.name;",
             variants=("UPDATE responses SET q2_score = NULL;",),
             hint="NOT EXISTS around a correlated subquery that already filters out the NULL scores. NOT IN would be at the mercy of them.",
             difficulty="Medium"),
        chal("sql_nulls-twoaverages", "Two honest averages",
             "For q1, report both readings side by side: `avg_of_answers` (AVG, which skips missing "
             "answers) and `avg_treating_missing_as_zero`, each rounded to 2 decimals, plus `answered` "
             "and `all_rows` so the difference is explicable.",
             "survey",
             "SELECT COUNT(*) AS all_rows,\n"
             "       COUNT(q1_score) AS answered,\n"
             "       ROUND(AVG(q1_score), 2) AS avg_of_answers,\n"
             "       ROUND(COALESCE(SUM(q1_score), 0) * 1.0 / COUNT(*), 2) AS avg_treating_missing_as_zero\n"
             "FROM responses;",
             variants=("UPDATE responses SET q1_score = NULL WHERE id <= 3;",),
             hint="AVG gives the first. For the second, divide the SUM by the row count — and multiply by 1.0 so it is float division.",
             difficulty="Easy"),
        chal("sql_nulls-profile", "A NULL profile of the table",
             "For the `responses` table, report how many rows are missing each nullable column. Show "
             "`column_name` and `missing`, one row per column (`q1_score`, `q2_score`, `comment`), built "
             "by stacking three counts. Order by `missing` descending, then `column_name`.",
             "survey",
             "SELECT 'q1_score' AS column_name, SUM(CASE WHEN q1_score IS NULL THEN 1 ELSE 0 END) AS missing FROM responses\n"
             "UNION ALL\n"
             "SELECT 'q2_score', SUM(CASE WHEN q2_score IS NULL THEN 1 ELSE 0 END) FROM responses\n"
             "UNION ALL\n"
             "SELECT 'comment', SUM(CASE WHEN comment IS NULL THEN 1 ELSE 0 END) FROM responses\n"
             "ORDER BY missing DESC, column_name;",
             variants=("UPDATE responses SET comment = NULL, q2_score = 5;",),
             hint="`SUM(CASE WHEN ... IS NULL THEN 1 ELSE 0 END)` counts missing values; UNION ALL stacks one such query per column.",
             difficulty="Medium"),
        chal("sql_nulls-optional", "Nullable keys need outer joins",
             "Show every employee with their department name, substituting `'(unassigned)'` where there "
             "is none, and their manager's name, substituting `'(none)'`. "
             "Show `employee`, `department`, `manager`. Order by `employee`.",
             "hr",
             "SELECT e.name AS employee,\n"
             "       COALESCE(d.name, '(unassigned)') AS department,\n"
             "       COALESCE(m.name, '(none)') AS manager\n"
             "FROM employees e\n"
             "LEFT JOIN departments d ON d.id = e.dept_id\n"
             "LEFT JOIN employees   m ON m.id = e.manager_id\n"
             "ORDER BY e.name;",
             variants=("UPDATE employees SET dept_id = NULL WHERE dept_id = 3;",),
             hint="Both foreign keys are nullable, so both joins have to be outer — then COALESCE the padded NULLs into readable text.",
             difficulty="Easy"),
    ],
)


# ===========================================================================
# 16. Performance
# ===========================================================================

concept(
    "sql_performance",
    "SQL: Performance",
    "Indexes, Query Plans & Join Cost",
    "Read the plan, index the join and filter columns, and keep your predicates sargable.",
    "A join that is instant on a thousand rows and unusable on ten million is not a different "
    "query, it is the same query hitting a different strategy. The database picks that strategy "
    "for you, and EXPLAIN QUERY PLAN tells you which one it picked — whether it scanned a whole "
    "table or seeked into an index, and in what order it visited the tables. Almost all real "
    "tuning is one of three moves: add the index the plan is missing, rewrite a predicate so an "
    "index can actually be used, or reduce the number of rows before the expensive step rather "
    "than after. Guessing is optional; the plan is right there.",
    """
```sql
EXPLAIN QUERY PLAN
SELECT c.name, o.id FROM customers c JOIN orders o ON o.customer_id = c.id;
```

```
SCAN c                                        <- reads every customer row
SEARCH o USING INDEX ix_orders_cust (customer_id=?)   <- seeks, per customer
```

`SCAN` = read the whole table. `SEARCH ... USING INDEX` = jump straight to the
matching rows. A `SCAN` of the *inner* table of a join is the classic problem: it
happens once per outer row.

**Index the columns you join on and filter on**:

```sql
CREATE INDEX ix_orders_customer ON orders(customer_id);
CREATE INDEX ix_items_order     ON order_items(order_id);
CREATE INDEX ix_orders_status_date ON orders(status, order_date);   -- composite
```

**Sargable** = the index can be used. A column wrapped in a function cannot be:

```sql
WHERE substr(order_date,1,7) = '2023-03'                    -- NOT sargable
WHERE order_date >= '2023-03-01' AND order_date < '2023-04-01'  -- sargable
```
""",
    """
### Read the plan first

`EXPLAIN QUERY PLAN` is cheap, exact, and available right now: paste any query
into the **Run query** box on the exercises below with those three words in front
of it and read the plan live. (The exercises themselves are judged on results
rather than on plan text, because the exact wording of a plan changes between
SQLite versions — but the plan is the tool you reach for in real work.)

It tells you two things that matter:

1. **Access method per table.** `SCAN t` reads every row; `SEARCH t USING INDEX
   ix (col=?)` uses an index; `SEARCH t USING INTEGER PRIMARY KEY (rowid=?)` is
   the fastest of all.
2. **Join order.** The first line is the outer table. Everything below it runs
   once *per row* of what came before, which is why a `SCAN` in the second
   position is so much worse than a `SCAN` in the first.

```
SCAN customers
SEARCH orders USING INDEX ix_orders_customer (customer_id=?)
```
Good: eight customers, eight index seeks.

```
SCAN customers
SCAN orders
```
Bad: eight customers × the whole orders table.

### What an index actually is

A sorted structure mapping column values to rows. That is why it helps equality
(`= 5`), ranges (`BETWEEN`, `>`, `<`), prefix matching (`LIKE 'abc%'`) and
`ORDER BY` — all of which are questions about sorted order — and does nothing for
`LIKE '%abc'`, which is not.

Indexes are not free: every `INSERT`, `UPDATE` and `DELETE` maintains them, and
they occupy space. Index what you query on, not everything.

**Primary keys are already indexed.** In SQLite an `INTEGER PRIMARY KEY` *is* the
rowid, which is the fastest possible lookup. It is **foreign keys that usually
are not** — SQLite does not index them automatically — and a foreign key is
exactly what you join on. That single omission is the most common cause of a slow
join in a SQLite schema.

### Composite indexes and the left-prefix rule

```sql
CREATE INDEX ix ON orders(status, order_date);
```

This index serves:

```sql
WHERE status = 'shipped'                                   -- yes (left prefix)
WHERE status = 'shipped' AND order_date >= '2023-06-01'    -- yes (both)
WHERE order_date >= '2023-06-01'                           -- NO (skips the first column)
```

Column order matters. The rule of thumb: **equality columns first, then the range
column, then anything you only select**. An index that also covers the selected
columns lets the engine answer entirely from the index — a *covering index* — and
never touch the table at all.

### Sargability — do not wrap the column

The single highest-yield rewrite:

```sql
WHERE substr(order_date, 1, 7) = '2023-03'        -- function on the column: full scan
WHERE order_date >= '2023-03-01'
  AND order_date <  '2023-04-01'                  -- plain column: index range seek

WHERE customer_id + 0 = 5                          -- arithmetic on the column: scan
WHERE customer_id = 5                              -- seek

WHERE lower(email) = 'a@b.com'                     -- scan (unless you index lower(email))
```

The index stores the column's values, not `substr()` of them. Wrap the *constant*
instead of the column whenever you can — and when you genuinely need a function,
SQLite supports an **expression index**:

```sql
CREATE INDEX ix_email_lower ON users(lower(email));
```

### Join strategies

Given `A JOIN B ON a.k = b.k`:

- **Nested loop** — for each row of A, find B's matches. With an index on `b.k`
  this is excellent; without one it is |A| × |B|.
- **Hash join** — build a hash of B keyed on `k`, probe once per A row. Needs
  equality, which is why range joins cannot use it.
- **Merge join** — both sides already sorted on `k`, walk them together.

SQLite uses nested loops almost exclusively, so **the index on the inner table's
join column is the whole game**. Bigger engines have more options, but the
principle transfers: equality joins have fast strategies available, range joins
have fewer.

### Filter early

The optimiser pushes filters down when it can, but shaping the query helps:

```sql
-- Filters after building a big join
SELECT ... FROM orders o JOIN order_items i ON ... WHERE o.order_date >= '2023-09-01';

-- Filters first, then joins far fewer rows
WITH recent AS (SELECT * FROM orders WHERE order_date >= '2023-09-01')
SELECT ... FROM recent o JOIN order_items i ON i.order_id = o.id;
```

Both are usually planned identically in SQLite. The version that *always* helps is
**aggregating before joining**, which reduces the row count rather than just
reordering the work — the same rewrite that fixed the fan-out in Chapter 9.

### `ANALYZE` and statistics

The planner chooses using estimates. If it has none, it guesses:

```sql
ANALYZE;    -- collect table/index statistics into sqlite_stat1
```

Run it after bulk-loading data. A plan that suddenly goes wrong on a table that
grew ten times is very often stale statistics.

### A tuning checklist

1. `EXPLAIN QUERY PLAN` the query. Find the `SCAN`s.
2. Is the scanned table the inner side of a join? Index its join column.
3. Is a `WHERE` column wrapped in a function? Rewrite to a range, or index the
   expression.
4. Does a composite index exist whose *left prefix* your predicates match?
5. Can you aggregate or filter before the biggest join?
6. `ANALYZE` if the statistics are stale.
7. Re-read the plan. It either changed or it did not — no guessing required.

### Watch out for

- **Indexing everything.** Writes slow down and the planner gets more ways to
  choose badly.
- **An index on a low-selectivity column** (`status`, with three values) rarely
  helps on its own; as the *first* column of a composite it can.
- **`SELECT *` defeats covering indexes** — the engine must visit the table for
  the columns you did not need.
- **`OR` across different columns** often cannot use an index; `UNION` of two
  indexed queries sometimes can.
- **Benchmarking on 100 rows** proves nothing. Plans change with size, which is
  exactly why you read the plan rather than the clock.
""",
    [
        q("In `EXPLAIN QUERY PLAN` output, what does `SCAN orders` mean?",
          ["Every row of `orders` is read",
           "The rows are read in sorted order",
           "An index is being used",
           "The table is being locked"], 0,
          "SCAN is a full table read. It is acceptable for the outer table of a join or a small table; on the inner side it happens once per outer row."),
        q("Which predicate can use an index on `orders(order_date)`?",
          ["`order_date >= '2023-03-01' AND order_date < '2023-04-01'`",
           "`substr(order_date, 1, 7) = '2023-03'`",
           "`order_date || '' = '2023-03-01'`",
           "`date(order_date) = '2023-03-01'`"], 0,
          "The index stores the column's values. Wrapping the column in a function means the index no longer describes what you are asking about — that is what 'sargable' means."),
        q("Which columns does SQLite index automatically?",
          ["The primary key only — foreign keys are not indexed for you",
           "Primary keys and foreign keys",
           "Every column",
           "None"], 0,
          "An INTEGER PRIMARY KEY is the rowid. Foreign keys get no index, and a foreign key is exactly what you join on — the most common cause of a slow SQLite join."),
        q("With `CREATE INDEX ix ON orders(status, order_date)`, which query cannot use it?",
          ["`WHERE order_date >= '2023-06-01'` alone",
           "`WHERE status = 'shipped'`",
           "`WHERE status = 'shipped' AND order_date >= '2023-06-01'`",
           "All three can use it"], 0,
          "A composite index is usable from its left prefix inward. Skipping the first column means the index's sort order says nothing useful about your predicate."),
        q("Why can a range join not use a hash join?",
          ["Hashing requires equality; there is no hash of 'is between'",
           "Ranges are always on text columns",
           "Hash joins need an index",
           "It can"], 0,
          "A hash lookup answers 'which rows have exactly this key'. A range asks about an interval, so the engine falls back to scanning or to a B-tree range seek."),
        q("What does `ANALYZE` do?",
          ["Collects table and index statistics so the planner can estimate row counts",
           "Rebuilds every index",
           "Runs the query and reports timings",
           "Checks the database for corruption"], 0,
          "The planner chooses between strategies using estimates. Stale statistics after a table grows tenfold are a common cause of a plan that was fine yesterday."),
        q("Why does `SELECT *` defeat a covering index?",
          ["The index holds only some columns, so the engine must visit the table for the rest",
           "`SELECT *` disables the optimiser",
           "It forces a sort",
           "It does not"], 0,
          "A covering index answers the query entirely from the index. Ask for a column the index does not carry and every matched row needs a table lookup as well."),
        q("A join is slow. What is the first thing to do?",
          ["Run EXPLAIN QUERY PLAN and look for a SCAN on the inner table",
           "Add an index to every column",
           "Rewrite it as a subquery",
           "Add a LIMIT"], 0,
          "The plan tells you what the engine actually chose. Tuning without it is guessing, and the fix is usually one specific missing index that the plan names for you."),
    ],
    [
        sq("sql_performance-schema", "See what is already indexed",
           "Before adding an index, find out what exists. `sqlite_schema` lists every object in the "
           "database. Fill in the `WHERE` that keeps only indexes SQLite created for you (their names "
           "start with `sqlite_autoindex`) and ones you created. Columns: `name`, `tbl_name`. "
           "Order by `tbl_name`, then `name`.",
           "shop",
           "CREATE INDEX ix_orders_customer ON orders(customer_id);\n"
           "SELECT name, tbl_name\n"
           "FROM sqlite_schema\n"
           "WHERE type = 'index'\n"
           "ORDER BY tbl_name, name;",
           ["type = 'index'"],
           variants=("CREATE INDEX ix_items_product ON order_items(product_id);",),
           hint="`sqlite_schema.type` is 'table', 'index', 'view' or 'trigger'."),
        sq("sql_performance-index", "Index the foreign key",
           "SQLite does not index foreign keys for you, and a foreign key is exactly what you join on. "
           "Fill in the `CREATE INDEX` statement for the column `order_items` joins by, then the query "
           "runs against the tuned schema. Columns: `order_id`, `lines`. Order by `order_id`.",
           "shop",
           "CREATE INDEX ix_items_order ON order_items(order_id);\n"
           "SELECT o.id AS order_id, COUNT(i.id) AS lines\n"
           "FROM orders o\n"
           "LEFT JOIN order_items i ON i.order_id = o.id\n"
           "GROUP BY o.id\n"
           "ORDER BY o.id;",
           ["CREATE INDEX ix_items_order ON order_items(order_id);"],
           variants=("DELETE FROM order_items WHERE id > 15;",),
           hint="`CREATE INDEX <name> ON <table>(<column>);` — name it ix_items_order."),
        sq("sql_performance-sargable", "Make the predicate sargable",
           "This filter wraps the column in `substr`, so no index on `order_date` could ever help. "
           "Rewrite it as a half-open range. Columns: `order_id`, `order_date`. Order by `order_id`.",
           "shop",
           "SELECT id AS order_id, order_date\n"
           "FROM orders\n"
           "WHERE order_date >= '2023-03-01' AND order_date < '2023-04-01'\n"
           "ORDER BY id;",
           ["order_date >= '2023-03-01' AND order_date < '2023-04-01'"],
           variants=("UPDATE orders SET order_date = '2023-03-30' WHERE id > 108;",),
           hint="Two comparisons on the bare column: greater-or-equal the first of the month, strictly less than the first of the next."),
        sq("sql_performance-composite", "A composite index, left prefix first",
           "Build one index that serves both `WHERE status = ?` and "
           "`WHERE status = ? AND order_date >= ?`. Fill in the column list, equality column first. "
           "Columns: `order_id`, `order_date`. Order by `order_date`, then `order_id`.",
           "shop",
           "CREATE INDEX ix_orders_status_date ON orders(status, order_date);\n"
           "SELECT id AS order_id, order_date\n"
           "FROM orders\n"
           "WHERE status = 'shipped' AND order_date >= '2023-06-01'\n"
           "ORDER BY order_date, id;",
           ["(status, order_date)"],
           variants=("UPDATE orders SET status = 'shipped' WHERE status = 'pending';",),
           hint="Equality column first, then the one you range over — that is the left-prefix rule."),
        sq("sql_performance-covering", "A covering index",
           "Give the engine an index that can answer the query without touching the table at all: it "
           "has to carry both the filtered column and the selected one. Fill in the column list. "
           "Columns: `order_date`. Order by `order_date`.",
           "shop",
           "CREATE INDEX ix_orders_cust_date ON orders(customer_id, order_date);\n"
           "SELECT order_date FROM orders WHERE customer_id = 1 ORDER BY order_date;",
           ["(customer_id, order_date)"],
           variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 1, '2023-01-20', 'shipped', 'web');",),
           hint="Filter column first, then the column being selected, so no table lookup is needed."),
        sq("sql_performance-preagg", "Reduce rows before the join",
           "Aggregating before joining shrinks the work instead of just reordering it. Fill in the CTE "
           "that collapses order lines to one row per order. Columns: `customer`, `spend`. "
           "Order by `spend` descending, then `customer`.",
           "shop",
           "WITH totals AS (\n"
           "  SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id\n"
           ")\n"
           "SELECT c.name AS customer, ROUND(SUM(t.total), 2) AS spend\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "JOIN totals t ON t.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY spend DESC, customer;",
           ["  SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id"],
           variants=("UPDATE order_items SET quantity = 2 WHERE id % 2 = 0;",),
           hint="Twenty line rows become thirteen order rows before they meet the customers."),
        sq("sql_performance-analyze", "Give the planner statistics",
           "Collect table and index statistics so the optimiser estimates row counts instead of "
           "guessing. Fill in the statement; the query afterwards then reads back the table it wrote. "
           "Columns: `tbl`, `idx`. Order by `tbl`, then `idx`.",
           "shop",
           "CREATE INDEX ix_items_order2 ON order_items(order_id);\n"
           "ANALYZE;\n"
           "SELECT tbl, idx FROM sqlite_stat1 WHERE idx IS NOT NULL ORDER BY tbl, idx;",
           ["ANALYZE;"],
           variants=("CREATE INDEX ix_orders_status2 ON orders(status);",),
           hint="One word plus a semicolon. It writes its results into the sqlite_stat1 table."),

        chal("sql_performance-indexed", "Index it, then prove it",
             "Create an index on `orders(customer_id)` and then run the customer-order join, so the "
             "plan can seek instead of scanning. Show `customer` and `order_count` for every customer "
             "who has ordered. Order by `order_count` descending, then `customer` ascending.",
             "shop",
             "CREATE INDEX ix_orders_customer ON orders(customer_id);\n"
             "SELECT c.name AS customer, COUNT(o.id) AS order_count\n"
             "FROM customers c\n"
             "JOIN orders o ON o.customer_id = c.id\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY order_count DESC, customer;",
             variants=("INSERT INTO orders (id, customer_id, order_date, status, channel) VALUES (114, 6, '2023-12-01', 'shipped', 'web'), (115, 6, '2023-12-08', 'shipped', 'app');",),
             hint="Two statements in one batch: the CREATE INDEX first, then the query. The last statement that returns rows is what gets compared.",
             difficulty="Easy"),
        chal("sql_performance-rewrite", "Rewrite an unsargable report",
             "This report filters with `substr(order_date, 1, 7) IN ('2023-09','2023-10')`, which no "
             "index can serve. Produce the same answer using half-open date ranges instead: for orders "
             "placed in September or October 2023, show `order_id`, `order_date` and `status`. "
             "Order by `order_date`, then `order_id`.",
             "shop",
             "SELECT id AS order_id, order_date, status\n"
             "FROM orders\n"
             "WHERE order_date >= '2023-09-01' AND order_date < '2023-11-01'\n"
             "ORDER BY order_date, id;",
             variants=("UPDATE orders SET order_date = '2023-10-05' WHERE id <= 104;",),
             hint="The two months are adjacent, so one range covers both: from the first of September up to (not including) the first of November.",
             difficulty="Easy"),
        chal("sql_performance-audit", "Audit the join columns",
             "Every foreign key in this schema should be indexed, because every one of them is a join "
             "column. Create an index on each of `orders(customer_id)`, `order_items(order_id)`, "
             "`order_items(product_id)` and `products(category_id)`, then report what now exists: "
             "`tbl_name` and `name` for every index you created (they all start with `ix_`). "
             "Order by `tbl_name`, then `name`.",
             "shop",
             "CREATE INDEX ix_orders_customer ON orders(customer_id);\n"
             "CREATE INDEX ix_items_order ON order_items(order_id);\n"
             "CREATE INDEX ix_items_product ON order_items(product_id);\n"
             "CREATE INDEX ix_products_category ON products(category_id);\n"
             "SELECT tbl_name, name FROM sqlite_schema\n"
             "WHERE type = 'index' AND name LIKE 'ix\\_%' ESCAPE '\\'\n"
             "ORDER BY tbl_name, name;",
             hint="Four CREATE INDEX statements, then query sqlite_schema for type = 'index'. The underscore in `ix_` is a LIKE wildcard, so escape it.",
             difficulty="Medium"),
        chal("sql_performance-topcust", "A tuned top-customers report",
             "Build the report the fast way: index `order_items(order_id)` and `orders(customer_id)`, "
             "aggregate the lines to one row per order in a CTE, then join. Show `customer` and `spend` "
             "(rounded to 2) for the customers who have spent anything on **shipped** orders. "
             "Order by `spend` descending, then `customer` ascending.",
             "shop",
             "CREATE INDEX ix_items_o ON order_items(order_id);\n"
             "CREATE INDEX ix_orders_c ON orders(customer_id);\n"
             "WITH totals AS (\n"
             "  SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id\n"
             ")\n"
             "SELECT c.name AS customer, ROUND(SUM(t.total), 2) AS spend\n"
             "FROM customers c\n"
             "JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped'\n"
             "JOIN totals t ON t.order_id = o.id\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY spend DESC, customer;",
             variants=("UPDATE orders SET status = 'cancelled' WHERE channel = 'web';",),
             hint="Indexes, then the CTE, then the query — all in one batch. Pre-aggregating means the customers meet 13 order rows rather than 20 line rows.",
             difficulty="Medium"),
    ],
)
