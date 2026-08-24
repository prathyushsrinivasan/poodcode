# -*- coding: utf-8 -*-
"""SQL track, chapters 9-11: aggregation over joins, subqueries, and CTEs.

Exec'd by tools/gen_seed.py after the join chapters, in the same namespace.
"""

# ===========================================================================
# 9. GROUP BY over joins
# ===========================================================================

concept(
    "sql_group_by",
    "SQL: Aggregation",
    "Aggregating Over Joins",
    "GROUP BY, HAVING, and the fan-out that quietly doubles your totals.",
    "GROUP BY on a single table is easy; GROUP BY after a join is where careers' worth of "
    "wrong dashboards come from. The reason is that aggregation happens after joining, so it "
    "aggregates whatever the join produced — and a one-to-many join produced more rows than "
    "you started with. Every order-level value is now repeated once per line, and SUM adds it "
    "every time. Nothing errors, nothing warns; the number is simply wrong, and wrong by a "
    "plausible-looking amount. The cure is to think in grain: know what one row means before "
    "and after each join, and aggregate a column only at the grain it actually lives at.",
    """
Evaluation order — the reason so much of this is counter-intuitive:

```
FROM / JOIN   ->  WHERE  ->  GROUP BY  ->  HAVING  ->  SELECT  ->  ORDER BY
```

- `WHERE` filters **rows**, before grouping. It cannot see an aggregate.
- `HAVING` filters **groups**, after grouping. It can.
- `SELECT` runs after grouping, which is why its aliases are visible to
  `ORDER BY` but not to `WHERE`.

```sql
SELECT   c.name, COUNT(o.id) AS orders
FROM     customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'shipped'
WHERE    c.city = 'Lisbon'          -- filters customers
GROUP BY c.id, c.name
HAVING   COUNT(o.id) >= 2           -- filters the resulting groups
ORDER BY orders DESC;
```

| aggregate         | ignores NULL? | over zero rows |
|-------------------|---------------|----------------|
| `COUNT(*)`        | no (counts rows) | `0`         |
| `COUNT(col)`      | yes           | `0`            |
| `SUM/AVG/MIN/MAX` | yes           | **`NULL`**     |
""",
    """
### Group by the key, not just the label

```sql
GROUP BY c.name              -- two customers called "Ada" become one group
GROUP BY c.id, c.name        -- correct
```

Grouping by the primary key guarantees one group per entity. Adding the name is
what lets you `SELECT` it. Strict engines (Postgres, and MySQL in
`ONLY_FULL_GROUP_BY`) *require* every non-aggregated select column to be grouped
by; SQLite does not, and will happily hand you an arbitrary row's value:

```sql
SELECT c.name, o.status, COUNT(*) FROM ... GROUP BY c.id;   -- o.status is arbitrary!
```

That runs in SQLite and returns nonsense for `o.status`. Write the query as if
the strict rule applied and it is correct everywhere.

### The fan-out bug — the one to internalise

The `shop` dataset has 13 orders and 20 order lines. Watch what the join does:

```sql
SELECT c.name AS customer, COUNT(*) AS looks_like_orders
FROM customers c
JOIN orders      o ON o.customer_id = c.id
JOIN order_items i ON i.order_id = o.id
GROUP BY c.id, c.name;
```

`COUNT(*)` here counts **lines**, not orders. Ada has 3 orders but 6 lines, so she
comes back with 6. The fix depends on what you meant:

```sql
COUNT(DISTINCT o.id)          -- 3: how many orders
COUNT(*)                      -- 6: how many lines
SUM(i.quantity)               -- how many units      (line grain: correct)
SUM(o.some_order_level_value) -- WRONG: added once per line
```

`COUNT(DISTINCT o.id)` rescues counts. **Nothing rescues a `SUM` of an
order-level column** — you have to change the shape of the query:

```sql
-- Aggregate the fanned-out side first, then join one row to one row.
SELECT c.name AS customer,
       COUNT(o.id)                AS orders,
       ROUND(SUM(t.total), 2)     AS spend
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN (SELECT order_id, SUM(quantity * unit_price) AS total
      FROM order_items
      GROUP BY order_id) t ON t.order_id = o.id
GROUP BY c.id, c.name;
```

Now `orders` counts orders and `spend` sums one value per order. Both are right,
and they stay right when someone adds a third table next month.

**The diagnostic:** if a total is a small integer multiple of what you expected,
or if `COUNT(*)` exceeds the number of rows in the table you think you are
counting, you have a fan-out.

### `WHERE` versus `HAVING`

```sql
WHERE  o.status = 'shipped'      -- discard rows before grouping
HAVING COUNT(*) >= 2             -- discard groups after grouping
HAVING o.status = 'shipped'      -- legal in SQLite, but it is a WHERE in disguise
```

The rule: **if the condition mentions an aggregate, it is `HAVING`; otherwise it
is `WHERE`.** Putting a row filter in `HAVING` still works but is slower — every
row is grouped first, then thrown away — and it reads as though something subtler
is going on.

The exception that matters: with an outer join, a condition on the optional table
belongs in `ON` (Chapter 3), not in `WHERE` *or* `HAVING`.

### Aggregates and NULL

`SUM`, `AVG`, `MIN`, `MAX` and `COUNT(col)` all skip NULLs. Two consequences:

```sql
AVG(q1_score)                        -- the average of the answers given
SUM(q1_score) * 1.0 / COUNT(*)       -- the average treating "no answer" as 0
```

Those are different numbers and both are sometimes what you want; say which.

And over **zero rows** the aggregates split: `COUNT` returns `0`, everything else
returns `NULL`. After a `LEFT JOIN` this is exactly the "customer who never
ordered" case, so:

```sql
COALESCE(SUM(i.quantity), 0)     -- 0, not NULL
COUNT(i.id)                      -- already 0
```

### Grouping by an expression

```sql
SELECT substr(o.order_date, 1, 7) AS month, COUNT(*) AS orders
FROM orders o
GROUP BY substr(o.order_date, 1, 7)
ORDER BY month;
```

SQLite also lets you `GROUP BY month` (the alias) or `GROUP BY 1` (the position).
The alias form is readable; the position form is a maintenance hazard as soon as
someone reorders the select list.

### Watch out for

- **`COUNT(*)` after a `LEFT JOIN`** counts padded rows as 1. Count a column from
  the optional side.
- **`SUM` over no rows is `NULL`**, and `NULL` in a report is usually a bug.
- **`AVG` of a fanned-out column** is wrong twice over: wrong denominator *and*
  wrong numerator.
- **`WHERE COUNT(*) > 1`** is an error — `WHERE` runs before the count exists.
- **Grouping by a name instead of a key** silently merges distinct entities.
""",
    [
        q("In what order do WHERE, GROUP BY and HAVING run?",
          ["WHERE, then GROUP BY, then HAVING",
           "GROUP BY, then WHERE, then HAVING",
           "HAVING, then WHERE, then GROUP BY",
           "They run in the order written"], 0,
          "WHERE filters rows before they are grouped; HAVING filters the groups that result. That is why WHERE cannot see an aggregate and HAVING can."),
        q("After `customers JOIN orders JOIN order_items`, what does `COUNT(*)` count per customer?",
          ["Order lines", "Orders", "Customers", "Products"], 0,
          "The order_items join fans each order out to one row per line, so the surviving rows are lines. Use COUNT(DISTINCT o.id) if you meant orders."),
        q("Why does `SUM(o.shipping_fee)` break after joining order_items, when `COUNT(DISTINCT o.id)` does not?",
          ["The fee is repeated once per line and SUM adds every copy; DISTINCT collapses the repeated ids",
           "SUM cannot be used after a join",
           "shipping_fee is nullable",
           "It does not break"], 0,
          "COUNT(DISTINCT) de-duplicates by value and the ids are distinct per order, so it survives. Sums of a repeated value have no such escape — aggregate the fanned side in a subquery first."),
        q("What does `SUM(x)` return when the group has zero matching rows?",
          ["NULL — wrap it in COALESCE if you want 0", "0", "An error", "An empty string"], 0,
          "COUNT returns 0 over no rows; SUM, AVG, MIN and MAX all return NULL. After a LEFT JOIN that is exactly the 'never ordered' case."),
        q("Which condition belongs in HAVING rather than WHERE?",
          ["`COUNT(*) >= 2`", "`c.city = 'Lisbon'`", "`o.status = 'shipped'`", "`o.order_date >= '2023-06-01'`"], 0,
          "If the condition mentions an aggregate it must be HAVING, because the aggregate does not exist until after grouping. Everything else belongs in WHERE, where it filters fewer rows."),
        q("Why is `GROUP BY c.name` risky?",
          ["Two different customers with the same name collapse into one group",
           "Names cannot be grouped in SQLite",
           "It is slower than grouping by id",
           "It breaks ORDER BY"], 0,
          "Grouping must be by something unique per entity. `GROUP BY c.id, c.name` gives one group per customer and still lets you select the name."),
        q("`AVG(q1_score)` over responses where some scores are NULL — what is the denominator?",
          ["The number of non-NULL scores", "The number of rows", "The number of respondents", "Always 1"], 0,
          "AVG skips NULLs entirely, so it averages the answers actually given. If you want unanswered treated as 0, write `SUM(q1_score) * 1.0 / COUNT(*)` and say so."),
    ],
    [
        sq("sql_group_by-key", "Group by the key",
           "Count each customer's orders. Fill in the `GROUP BY` so two customers who happen to share a "
           "name never merge. Columns: `customer`, `order_count`. "
           "Order by `order_count` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS order_count\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY order_count DESC, customer;",
           ["GROUP BY c.id, c.name"],
           variants=("UPDATE customers SET name = 'Ada' WHERE id = 3;",),
           hint="Group by the primary key first, then the name so you can select it."),
        sq("sql_group_by-distinct", "Count orders, not lines",
           "This join fans each order out to one row per line, so `COUNT(*)` would count lines. "
           "Fill in the expression that counts **orders**. Columns: `customer`, `orders`, `units`. "
           "Order by `orders` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(DISTINCT o.id) AS orders, SUM(i.quantity) AS units\n"
           "FROM customers c\n"
           "JOIN orders      o ON o.customer_id = c.id\n"
           "JOIN order_items i ON i.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY orders DESC, customer;",
           ["COUNT(DISTINCT o.id)"],
           variants=("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (21, 101, 4, 2, 32.00);",),
           hint="DISTINCT inside COUNT, applied to the order's primary key."),
        sq("sql_group_by-having", "Filter the groups",
           "Keep only the customers with **two or more** orders. That test mentions an aggregate, so it "
           "goes in the clause that runs after grouping — fill it in. "
           "Columns: `customer`, `order_count`. Order by `order_count` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS order_count\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "GROUP BY c.id, c.name\n"
           "HAVING COUNT(o.id) >= 2\n"
           "ORDER BY order_count DESC, customer;",
           ["HAVING COUNT(o.id) >= 2"],
           variants=("DELETE FROM order_items WHERE order_id IN (102, 108); DELETE FROM orders WHERE id IN (102, 108);",),
           hint="HAVING plus the same aggregate you selected."),
        sq("sql_group_by-where", "Filter the rows first",
           "Count each customer's **shipped** orders, keeping only customers with at least one. The "
           "status test does not mention an aggregate, so it belongs in the earlier clause — fill it in. "
           "Columns: `customer`, `shipped`. Order by `shipped` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS shipped\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "WHERE o.status = 'shipped'\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY shipped DESC, customer;",
           ["WHERE o.status = 'shipped'"],
           variants=("UPDATE orders SET status = 'cancelled' WHERE channel = 'app';",),
           hint="WHERE, because it tests a plain column. Filtering before grouping is also cheaper."),
        sq("sql_group_by-preagg", "Aggregate before joining",
           "Total each customer's spend at **order** grain, so nothing is double-counted. Fill in the "
           "join condition that attaches the pre-aggregated order totals. "
           "Columns: `customer`, `orders`, `spend`. Order by `spend` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS orders, ROUND(SUM(t.total), 2) AS spend\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "JOIN (SELECT order_id, SUM(quantity * unit_price) AS total\n"
           "      FROM order_items GROUP BY order_id) t ON t.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY spend DESC, customer;",
           ["ON t.order_id = o.id"],
           variants=("UPDATE order_items SET unit_price = unit_price * 2 WHERE order_id = 111;",),
           hint="The subquery already has one row per order_id. Match it to the order."),
        sq("sql_group_by-month", "Group by an expression",
           "Count orders per calendar month. Fill in the expression that pulls `YYYY-MM` out of the "
           "`YYYY-MM-DD` date text. Columns: `month`, `orders`. Order by `month`.",
           "shop",
           "SELECT substr(o.order_date, 1, 7) AS month, COUNT(*) AS orders\n"
           "FROM orders o\n"
           "GROUP BY substr(o.order_date, 1, 7)\n"
           "ORDER BY month;",
           ["substr(o.order_date, 1, 7) AS month"],
           variants=("UPDATE orders SET order_date = '2024-01-15' WHERE id IN (111, 112, 113);",),
           hint="`substr(text, start, length)` — start at 1, take 7 characters. Alias it `month`."),
        sq("sql_group_by-nullavg", "What AVG ignores",
           "In the survey, show how many rows there are, how many gave a q1 score, and the average of "
           "those scores rounded to 2 decimals. Fill in the two count expressions so the difference is "
           "visible. Columns: `rows_total`, `answered`, `avg_score`.",
           "survey",
           "SELECT COUNT(*) AS rows_total, COUNT(q1_score) AS answered,\n"
           "       ROUND(AVG(q1_score), 2) AS avg_score\n"
           "FROM responses;",
           ["COUNT(*) AS rows_total, COUNT(q1_score) AS answered"],
           variants=("UPDATE responses SET q1_score = 5 WHERE q1_score IS NULL;",),
           hint="COUNT(*) counts rows; COUNT(column) skips NULLs. AVG skips them too."),

        chal("sql_group_by-bigspend", "Customers who spent over 150",
             "Find every customer whose total spend across **shipped** orders exceeds 150. "
             "Show `customer` and `spend` (rounded to 2 decimals). "
             "Order by `spend` descending, then `customer` ascending.",
             "shop",
             "SELECT c.name AS customer, ROUND(SUM(i.quantity * i.unit_price), 2) AS spend\n"
             "FROM customers c\n"
             "JOIN orders      o ON o.customer_id = c.id\n"
             "JOIN order_items i ON i.order_id = o.id\n"
             "WHERE o.status = 'shipped'\n"
             "GROUP BY c.id, c.name\n"
             "HAVING SUM(i.quantity * i.unit_price) > 150\n"
             "ORDER BY spend DESC, customer;",
             variants=("UPDATE order_items SET quantity = 1;",),
             hint="The status test is a row filter (WHERE); the spend threshold is an aggregate test (HAVING). Summing line totals is safe — that is line grain.",
             difficulty="Medium"),
        chal("sql_group_by-monthly", "Monthly revenue and order count",
             "For each calendar month that has at least one **shipped** order, show `month` (as `YYYY-MM`), "
             "`orders` (distinct shipped orders) and `revenue` (total `quantity * unit_price`, rounded to "
             "2 decimals). Order by `month`.",
             "shop",
             "SELECT substr(o.order_date, 1, 7) AS month,\n"
             "       COUNT(DISTINCT o.id) AS orders,\n"
             "       ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue\n"
             "FROM orders o\n"
             "JOIN order_items i ON i.order_id = o.id\n"
             "WHERE o.status = 'shipped'\n"
             "GROUP BY substr(o.order_date, 1, 7)\n"
             "ORDER BY month;",
             variants=("UPDATE orders SET order_date = '2023-03-20' WHERE id IN (107, 108);",),
             hint="COUNT(DISTINCT o.id) survives the line-level fan-out; the revenue sum is already at line grain.",
             difficulty="Medium"),
        chal("sql_group_by-deptstats", "Department pay statistics",
             "For every department — including one that employs nobody — show `department`, `headcount`, "
             "`total_pay` (0 when empty), `avg_pay` (rounded to 2 decimals, NULL when empty) and "
             "`top_earner` (the highest salary, NULL when empty). "
             "Order by `total_pay` descending, then `department` ascending.",
             "hr",
             "SELECT d.name AS department,\n"
             "       COUNT(e.id) AS headcount,\n"
             "       COALESCE(SUM(e.salary), 0) AS total_pay,\n"
             "       ROUND(AVG(e.salary), 2) AS avg_pay,\n"
             "       MAX(e.salary) AS top_earner\n"
             "FROM departments d\n"
             "LEFT JOIN employees e ON e.dept_id = d.id\n"
             "GROUP BY d.id, d.name\n"
             "ORDER BY total_pay DESC, department;",
             variants=("UPDATE employees SET dept_id = 4 WHERE name IN ('Wren', 'Xu');",),
             hint="LEFT JOIN keeps Research. COUNT(e.id) gives it 0, COALESCE turns its NULL sum into 0, and AVG/MAX are left NULL on purpose — there is no average of nobody.",
             difficulty="Medium"),
        chal("sql_group_by-fanout", "Show the fan-out",
             "Demonstrate the bug in a single row. Return `orders_correct` — the number of shipped orders "
             "counted properly — and `orders_inflated`, the same count done naively as `COUNT(*)` after "
             "joining order lines. Both from one query over the joined tables.",
             "shop",
             "SELECT COUNT(DISTINCT o.id) AS orders_correct, COUNT(*) AS orders_inflated\n"
             "FROM orders o\n"
             "JOIN order_items i ON i.order_id = o.id\n"
             "WHERE o.status = 'shipped';",
             variants=("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (21, 101, 4, 1, 32.00), (22, 101, 5, 1, 88.25);",),
             hint="Two aggregates over the same joined rows: one de-duplicates by order id, the other does not.",
             difficulty="Easy"),
    ],
)


# ===========================================================================
# 10. Subqueries
# ===========================================================================

concept(
    "sql_subqueries",
    "SQL: Subqueries & CTEs",
    "Subqueries: IN, EXISTS & Correlated",
    "A query inside a query — and the NULL trap that makes NOT IN return nothing.",
    "A subquery is just a query used as a value, a list, or a table. Which of those three it "
    "is determines everything about how it behaves and what it costs. As a value it must "
    "return exactly one row and column. As a list it feeds IN, which is readable and has one "
    "spectacular failure mode: if the list contains a single NULL, NOT IN returns no rows at "
    "all, silently, forever. As a table it goes in FROM and is often the cleanest fix for a "
    "fan-out. The fourth form, the correlated subquery, references the outer row and so runs "
    "conceptually once per row — expressive, occasionally slow, and the natural home of EXISTS.",
    """
Four shapes, four jobs:

```sql
-- 1. SCALAR: one row, one column. Usable anywhere a value is.
WHERE salary > (SELECT AVG(salary) FROM employees)

-- 2. LIST: one column, many rows. Feeds IN / NOT IN.
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'shipped')

-- 3. DERIVED TABLE: goes in FROM, must be aliased.
FROM (SELECT order_id, SUM(quantity) AS units FROM order_items GROUP BY order_id) t

-- 4. CORRELATED: references the outer row; the natural home of EXISTS.
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)
```

> **`NOT IN` with a NULL anywhere in the list returns zero rows.** Always.
> Use `NOT EXISTS`, or `WHERE col IS NOT NULL` inside the subquery.

| need                   | reach for              |
|------------------------|------------------------|
| "has at least one ..." | `EXISTS`               |
| "has no ..."           | `NOT EXISTS`           |
| a small literal set    | `IN (1, 2, 3)`         |
| a value to compare to  | scalar subquery        |
| to stop a fan-out      | derived table in `FROM`|
""",
    """
### Scalar subqueries — a query used as a number

```sql
SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;
```

The inner query runs once and produces one number. If it ever returns more than
one row you get an error; if it returns none, you get `NULL` — and `salary > NULL`
is unknown, so the outer query returns nothing. That silent-empty-result is worth
remembering.

Scalar subqueries also work in the `SELECT` list, where they act as a per-row
lookup:

```sql
SELECT c.name AS customer,
       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS orders
FROM customers c;
```

That is a **correlated** scalar subquery — it mentions `c.id` from the outer
query, so it cannot be evaluated once. It is a perfectly good way to express
"and also count this", and it avoids the fan-out entirely. Its cost is one lookup
per outer row, which an index makes cheap.

### `IN` — a query used as a list

```sql
SELECT name FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE status = 'shipped');
```

Readable and usually fast; the planner typically rewrites it into a semi-join.
Note that `IN` **does not multiply rows** — a customer with five shipped orders
still appears once. That is `IN`'s quiet advantage over a join when you only want
existence.

### The `NOT IN` NULL trap

This is the single most surprising behaviour in SQL, so here it is in full.

```sql
-- Which respondents are NOT in the 'smb' or 'enterprise' segments?
SELECT name FROM respondents
WHERE segment NOT IN (SELECT segment FROM respondents WHERE name <> 'Chen');
```

`Chen`'s segment is `NULL`... but even excluding Chen, imagine any NULL sneaking
into that list. `x NOT IN (a, b, NULL)` expands to:

```
x <> a  AND  x <> b  AND  x <> NULL
                          ^^^^^^^^^ always UNKNOWN
```

`true AND unknown` is `unknown`, which `WHERE` treats as not-true. So the whole
condition can never be true, and **the query returns zero rows regardless of the
data**. No error. No warning.

Three fixes:

```sql
WHERE NOT EXISTS (SELECT 1 FROM t WHERE t.segment = r.segment)   -- best
WHERE segment NOT IN (SELECT segment FROM t WHERE segment IS NOT NULL)
LEFT JOIN t ON ... WHERE t.pk IS NULL                            -- the anti-join
```

`NOT EXISTS` is immune because it asks a different question: not "is this value
absent from a list", but "does a matching row fail to exist". `IN` (the positive
form) is safe — a NULL in the list simply never matches.

### `EXISTS` — existence, not values

```sql
SELECT c.name
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'shipped');
```

`SELECT 1` because nothing about the selected value matters; `EXISTS` only asks
whether a row came back. The engine can stop at the first match, which makes it
efficient even against a huge inner table.

Three ways to write "customers who have shipped orders", all equivalent:

```sql
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status='shipped')
WHERE c.id IN (SELECT customer_id FROM orders WHERE status='shipped')
JOIN orders o ON o.customer_id = c.id AND o.status='shipped'  -- needs DISTINCT!
```

The join version fans out — a customer with three shipped orders appears three
times unless you add `DISTINCT` or a `GROUP BY`. That is the reason to prefer
`EXISTS` or `IN` when you want existence rather than data.

And "customers with no shipped orders", also three ways:

```sql
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status='shipped')
LEFT JOIN orders o ON o.customer_id = c.id AND o.status='shipped' WHERE o.id IS NULL
WHERE c.id NOT IN (SELECT customer_id FROM orders WHERE status='shipped')   -- risky
```

### Derived tables — a query used as a table

```sql
SELECT c.name, t.units
FROM customers c
JOIN (SELECT o.customer_id, SUM(i.quantity) AS units
      FROM orders o JOIN order_items i ON i.order_id = o.id
      GROUP BY o.customer_id) t ON t.customer_id = c.id;
```

The alias (`t`) is mandatory. This is the fan-out fix from Chapter 9, and once a
query has two or three of these, a CTE (next chapter) says the same thing far
more legibly.

### Correlated subqueries and cost

A correlated subquery conceptually runs once per outer row. Modern optimisers
often flatten it into a join, but not always — and when they do not, an
un-indexed correlated subquery over a large table is quadratic. The tells:

- the inner query mentions an outer column → correlated
- it appears in `SELECT` or in a per-row `WHERE` → runs per row
- the correlated column is not indexed → each run is a full scan

The fix is usually to aggregate once into a derived table and join to it.

### Watch out for

- **`NOT IN` + NULL = no rows.** The big one.
- **A scalar subquery returning more than one row** is a runtime error, which
  means it can pass in testing and fail in production when the data grows.
- **Forgetting to alias a derived table** is a syntax error in most engines.
- **`IN` with a huge subquery** may materialise the whole list; `EXISTS` can
  short-circuit.
- **`COUNT(*) > 0` instead of `EXISTS`** counts every match before deciding.
""",
    [
        q("Why can `NOT IN (SELECT ...)` return zero rows even when matches obviously exist?",
          ["A NULL in the list makes every comparison unknown, so the condition is never true",
           "NOT IN is not supported with subqueries",
           "The subquery ran out of memory",
           "NOT IN requires an index"], 0,
          "`x NOT IN (a, NULL)` expands to `x <> a AND x <> NULL`, and the second half is unknown forever. `true AND unknown` is unknown, which WHERE discards. Use NOT EXISTS."),
        q("Is the positive `IN (SELECT ...)` also broken by NULLs in the list?",
          ["No — a NULL simply never matches, so it just contributes nothing",
           "Yes, identically to NOT IN",
           "Yes, but only in SQLite",
           "Only when the outer column is NULL"], 0,
          "For IN you need one comparison to be true; an unknown among them does not prevent that. It is only the negated form, where every comparison must be true, that NULL destroys."),
        q("What does `EXISTS (SELECT 1 FROM ...)` return `1` for?",
          ["Nothing — EXISTS only asks whether any row came back; the selected value is ignored",
           "The number of matching rows",
           "The first matching id",
           "It is required syntax"], 0,
          "EXISTS is a pure existence test, so people write `SELECT 1` to make that obvious. `SELECT *` would behave identically."),
        q("Which of these fans out, returning a customer once per matching order?",
          ["`JOIN orders o ON o.customer_id = c.id`",
           "`WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)`",
           "`WHERE c.id IN (SELECT customer_id FROM orders)`",
           "None of them"], 0,
          "Only the join produces one output row per match. IN and EXISTS are existence tests: they filter the outer row, they never duplicate it."),
        q("A derived table in FROM is missing its alias. What happens?",
          ["A syntax error", "It works, using the first column name",
           "It becomes a correlated subquery", "It is silently ignored"], 0,
          "A table expression in FROM has to be nameable so its columns can be referenced. Give it an alias."),
        q("What makes a subquery *correlated*?",
          ["It references a column from the outer query, so it cannot be evaluated once",
           "It appears in the WHERE clause",
           "It returns more than one row",
           "It uses an aggregate"], 0,
          "The reference to the outer row is the definition. That is what forces it to be evaluated per row (conceptually — the optimiser often rewrites it into a join)."),
        q("A scalar subquery in a WHERE clause returns two rows. What happens?",
          ["A runtime error — which may only appear once the data grows",
           "The first row is used", "It returns NULL", "The condition becomes unknown"], 0,
          "Scalar context demands exactly one row. That the failure is data-dependent is what makes it dangerous: the query passes in testing and breaks later."),
    ],
    [
        sq("sql_subqueries-scalar", "A query used as a number",
           "List the employees who earn more than the company average. Fill in the scalar subquery. "
           "Columns: `employee`, `salary`. Order by `salary` descending, then `employee`.",
           "hr",
           "SELECT name AS employee, salary\n"
           "FROM employees\n"
           "WHERE salary > (SELECT AVG(salary) FROM employees)\n"
           "ORDER BY salary DESC, employee;",
           ["(SELECT AVG(salary) FROM employees)"],
           variants=("UPDATE employees SET salary = 250000 WHERE name = 'Cai';",),
           hint="One row, one column, in parentheses. Nothing else in the query changes."),
        sq("sql_subqueries-in", "A query used as a list",
           "Name the customers who have at least one shipped order, without duplicating anybody. "
           "Fill in the operator that tests membership of the subquery's results. "
           "Columns: `customer`. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer\n"
           "FROM customers c\n"
           "WHERE c.id IN (SELECT customer_id FROM orders WHERE status = 'shipped')\n"
           "ORDER BY c.name;",
           ["IN"],
           variants=("UPDATE orders SET status = 'pending' WHERE customer_id IN (1, 3);",),
           hint="Two letters. Unlike a join, it never multiplies the outer row."),
        sq("sql_subqueries-exists", "Existence, not values",
           "Same question, written as an existence test. Fill in the correlated condition inside the "
           "subquery. Columns: `customer`. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer\n"
           "FROM customers c\n"
           "WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'shipped')\n"
           "ORDER BY c.name;",
           ["o.customer_id = c.id AND o.status = 'shipped'"],
           variants=("UPDATE orders SET status = 'cancelled' WHERE channel = 'web';",),
           hint="Link the inner order back to the outer customer, then add the status test."),
        sq("sql_subqueries-notexists", "The safe negation",
           "Find the customers with **no** shipped order. `NOT IN` would be at the mercy of NULLs — "
           "fill in the operator that is immune. Columns: `customer`. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer\n"
           "FROM customers c\n"
           "WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'shipped')\n"
           "ORDER BY c.name;",
           ["NOT EXISTS"],
           variants=("UPDATE orders SET status = 'shipped';",),
           hint="Two words. It asks whether a matching row fails to exist, so no NULL comparison is ever involved."),
        sq("sql_subqueries-guard", "Make NOT IN safe",
           "This `NOT IN` would collapse to zero rows because `respondents.segment` contains a NULL. "
           "Fill in the guard inside the subquery that keeps it honest. Columns: `name`. Order by `name`.",
           "survey",
           "SELECT name\n"
           "FROM respondents\n"
           "WHERE id NOT IN (SELECT respondent_id FROM responses WHERE q1_score IS NOT NULL)\n"
           "ORDER BY name;",
           ["WHERE q1_score IS NOT NULL"],
           variants=("UPDATE responses SET q1_score = NULL WHERE respondent_id = 5;",),
           hint="Filter the NULLs out of the list before NOT IN ever sees them."),
        sq("sql_subqueries-derived", "A query used as a table",
           "Join to a pre-aggregated table of per-order totals. Fill in the alias the derived table "
           "needs. Columns: `order_id`, `total`. Order by `total` descending, then `order_id`.",
           "shop",
           "SELECT t.order_id, ROUND(t.total, 2) AS total\n"
           "FROM (SELECT order_id, SUM(quantity * unit_price) AS total\n"
           "      FROM order_items GROUP BY order_id) t\n"
           "ORDER BY total DESC, t.order_id;",
           ["      FROM order_items GROUP BY order_id) t"],
           variants=("DELETE FROM order_items WHERE id <= 5;",),
           hint="Close the parenthesis and give the subquery a one-letter name."),
        sq("sql_subqueries-correlated", "A lookup per row",
           "Show every customer with their order count, computed by a correlated subquery instead of a "
           "join — so nothing fans out. Fill in the subquery. Columns: `customer`, `orders`. "
           "Order by `orders` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer,\n"
           "       (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) AS orders\n"
           "FROM customers c\n"
           "ORDER BY orders DESC, customer;",
           ["(SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id)"],
           variants=("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_id = 1); DELETE FROM orders WHERE customer_id = 1;",),
           hint="A COUNT over orders, correlated back to the outer customer's id. It returns 0 rather than NULL for customers with none."),

        chal("sql_subqueries-aboveavg", "Above their own department's average",
             "Find every employee who earns more than the average salary **of their own department**. "
             "Show `employee`, `department`, `salary`. Employees with no department are excluded. "
             "Order by `salary` descending, then `employee`.",
             "hr",
             "SELECT e.name AS employee, d.name AS department, e.salary\n"
             "FROM employees e\n"
             "JOIN departments d ON d.id = e.dept_id\n"
             "WHERE e.salary > (SELECT AVG(x.salary) FROM employees x WHERE x.dept_id = e.dept_id)\n"
             "ORDER BY e.salary DESC, employee;",
             variants=("UPDATE employees SET salary = 500000 WHERE name = 'Cai';",),
             hint="A correlated scalar subquery: the inner AVG must be restricted to the outer row's department.",
             difficulty="Medium"),
        chal("sql_subqueries-neverbought", "Never bought from Books",
             "List every customer who has **never** ordered a product from the `Books` category — "
             "including customers who have never ordered at all. Show `customer`. Order by `customer`.",
             "shop",
             "SELECT c.name AS customer\n"
             "FROM customers c\n"
             "WHERE NOT EXISTS (\n"
             "  SELECT 1\n"
             "  FROM orders      o\n"
             "  JOIN order_items i   ON i.order_id = o.id\n"
             "  JOIN products    p   ON p.id = i.product_id\n"
             "  JOIN categories  cat ON cat.id = p.category_id\n"
             "  WHERE o.customer_id = c.id AND cat.name = 'Books'\n"
             ")\n"
             "ORDER BY c.name;",
             variants=("UPDATE products SET category_id = 3;",),
             hint="NOT EXISTS around a whole four-table join. The correlation is the `o.customer_id = c.id` inside it.",
             difficulty="Medium"),
        chal("sql_subqueries-priciest", "The priciest line of each order",
             "For every order that has lines, show `order_id` and `product` — the product on that order's "
             "most expensive line (by `quantity * unit_price`). If an order ties, show every tied product. "
             "Order by `order_id`, then `product`.",
             "shop",
             "SELECT o.id AS order_id, p.name AS product\n"
             "FROM orders o\n"
             "JOIN order_items i ON i.order_id = o.id\n"
             "JOIN products    p ON p.id = i.product_id\n"
             "WHERE i.quantity * i.unit_price = (\n"
             "  SELECT MAX(x.quantity * x.unit_price) FROM order_items x WHERE x.order_id = o.id\n"
             ")\n"
             "ORDER BY o.id, p.name;",
             variants=("UPDATE order_items SET unit_price = 24.00, quantity = 1;",),
             hint="A correlated subquery computing that order's maximum line total, compared against each line.",
             difficulty="Medium"),
        chal("sql_subqueries-bothsides", "Ordered on web and app",
             "Using two `EXISTS` clauses, list every customer who has ordered through **both** the web "
             "and the app. Show `customer`. Order by `customer`.",
             "shop",
             "SELECT c.name AS customer\n"
             "FROM customers c\n"
             "WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.channel = 'web')\n"
             "  AND EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.channel = 'app')\n"
             "ORDER BY c.name;",
             variants=("UPDATE orders SET channel = 'app' WHERE customer_id = 7;",),
             hint="Two independent existence tests joined by AND. No join, so nothing fans out and no DISTINCT is needed.",
             difficulty="Easy"),
    ],
)


# ===========================================================================
# 11. CTEs
# ===========================================================================

concept(
    "sql_cte",
    "SQL: Subqueries & CTEs",
    "CTEs & Recursive CTEs",
    "Name a subquery once with WITH, then use it like a table — including to walk a hierarchy.",
    "A common table expression is a derived table you gave a name to, which sounds like a "
    "cosmetic change and is not. Naming lets you reference the same intermediate result twice "
    "instead of pasting it twice, lets you chain steps so each one is a readable sentence, and "
    "turns a query that nests four levels deep into a list of stages a reader can follow top to "
    "bottom. Then there is the part that has no non-recursive equivalent at all: WITH RECURSIVE "
    "walks a structure of unknown depth — a reporting chain, a category tree, a sequence of "
    "dates you need to generate — by repeatedly feeding its own output back into itself.",
    """
```sql
WITH order_totals AS (
  SELECT order_id, SUM(quantity * unit_price) AS total
  FROM order_items
  GROUP BY order_id
)
SELECT o.id, t.total
FROM orders o
JOIN order_totals t ON t.order_id = o.id;
```

Chain as many as you like; each may reference the ones above it:

```sql
WITH a AS (...),
     b AS (SELECT ... FROM a ...),
     c AS (SELECT ... FROM b ...)
SELECT * FROM c;
```

A recursive CTE has three parts, and the shape never varies:

```sql
WITH RECURSIVE chain AS (
    SELECT ...  FROM t WHERE <the starting rows>      -- 1. anchor
    UNION ALL                                        -- 2. UNION ALL, not UNION
    SELECT ...  FROM t JOIN chain ON ...             -- 3. recursive step
)
SELECT * FROM chain;
```

The recursion stops when the step produces no new rows.
""",
    """
### From nested to named

Here is a query with two derived tables. It is correct, and it is unpleasant:

```sql
SELECT c.name, t.total, t.total - a.avg_total AS vs_average
FROM customers c
JOIN (SELECT o.customer_id, SUM(i.quantity*i.unit_price) AS total
      FROM orders o JOIN order_items i ON i.order_id=o.id GROUP BY o.customer_id) t
  ON t.customer_id = c.id
CROSS JOIN (SELECT AVG(total) AS avg_total FROM
             (SELECT o.customer_id, SUM(i.quantity*i.unit_price) AS total
              FROM orders o JOIN order_items i ON i.order_id=o.id GROUP BY o.customer_id)) a;
```

The same subquery appears twice, because a derived table cannot be referenced by
name. With CTEs it is written once and read once:

```sql
WITH spend AS (
  SELECT o.customer_id, SUM(i.quantity * i.unit_price) AS total
  FROM orders o
  JOIN order_items i ON i.order_id = o.id
  GROUP BY o.customer_id
),
average AS (SELECT AVG(total) AS avg_total FROM spend)
SELECT c.name AS customer,
       ROUND(s.total, 2) AS total,
       ROUND(s.total - a.avg_total, 2) AS vs_average
FROM customers c
JOIN spend s ON s.customer_id = c.id
CROSS JOIN average a
ORDER BY total DESC;
```

Each `WITH` clause is a named step. That is the whole feature, and it is worth
a great deal: a reader can check one stage at a time, and you can develop the
query the same way — write the first CTE, `SELECT * FROM` it, confirm it, move on.

### CTEs versus derived tables versus views

| | scope | reusable in the query | stored |
|---|---|---|---|
| derived table | one spot in `FROM` | no | no |
| **CTE** | the whole statement | **yes** | no |
| view | the whole database | yes | yes |

A CTE is a view that lives for one statement. If three queries need the same
step, that is a view; if one query needs it twice, that is a CTE.

**Performance note:** SQLite may either inline a CTE into the outer query or
materialise it once. You can insist:

```sql
WITH spend AS MATERIALIZED (...)       -- compute once, reuse
WITH spend AS NOT MATERIALIZED (...)   -- inline at each use
```

Materialising is usually right when the CTE is expensive and used more than once.

### Recursive CTEs — walking a hierarchy

`employees.manager_id` points into `employees`. A self join gets you one level; a
recursive CTE gets you all of them:

```sql
WITH RECURSIVE chain AS (
    -- anchor: where the walk starts
    SELECT id, name, manager_id, 1 AS depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- step: everyone reporting to somebody already in `chain`
    SELECT e.id, e.name, e.manager_id, c.depth + 1
    FROM employees e
    JOIN chain c ON e.manager_id = c.id
)
SELECT name, depth FROM chain ORDER BY depth, name;
```

How it runs:

```
round 0 (anchor):  Rita                       depth 1
round 1:           Sami, Toma, Ana, Dov       depth 2   (report to Rita)
round 2:           Ugo, Vera, Yara, Zeno,
                   Bo, Cai                    depth 3
round 3:           Wren, Xu                   depth 4
round 4:           (nothing new) -> stop
```

Each round joins the *previous round's output* to the table. When a round adds
nothing, the recursion ends.

**`UNION ALL`, not `UNION`.** `UNION` de-duplicates, which costs a sort on every
round and — worse — would silently drop a legitimately repeated row.

### Building a path

Carry a text column along and you get the full chain:

```sql
WITH RECURSIVE chain AS (
    SELECT id, name, name AS path FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, c.path || ' > ' || e.name
    FROM employees e JOIN chain c ON e.manager_id = c.id
)
SELECT path FROM chain ORDER BY path;
```

`Rita > Sami > Ugo > Wren`. Anything you can compute from the parent row can be
accumulated this way — a depth, a running cost, a materialised path.

### Generating rows out of nothing

The other everyday use: a recursive CTE with no table at all, to produce a series.

```sql
WITH RECURSIVE months(m) AS (
    SELECT '2023-01'
    UNION ALL
    SELECT strftime('%Y-%m', date(m || '-01', '+1 month')) FROM months WHERE m < '2023-12'
)
SELECT * FROM months;
```

This is how you get a **complete calendar** to LEFT JOIN your data onto, so months
with no sales appear as `0` instead of being missing — the Chapter 4 grid idea,
built rather than stored.

### Guarding against infinite recursion

If the data has a cycle (A manages B manages A), the recursion never terminates.
Two defences:

```sql
WHERE depth < 20                                   -- a hard depth cap
WHERE instr(path, '>' || e.name || '>') = 0        -- refuse to revisit a node
```

SQLite also supports `LIMIT` on the outer query, which stops the recursion early
once enough rows exist.

### Watch out for

- **`UNION` instead of `UNION ALL`** in the recursive step: slower, and it can
  drop rows you needed.
- **An anchor that selects nothing** produces an empty result with no error. Run
  the anchor on its own first.
- **Cycles** hang the query. Cap the depth while developing.
- **A recursive CTE referencing itself twice** is not allowed — the recursive term
  may mention the CTE exactly once.
- **CTE column names**: `WITH t(a, b) AS (...)` renames them, and the count must
  match exactly.
""",
    [
        q("What can a CTE do that a derived table in FROM cannot?",
          ["Be referenced by name more than once in the same statement",
           "Contain a GROUP BY",
           "Be used in a WHERE clause",
           "Return more than one column"], 0,
          "A derived table exists at one spot in FROM, so needing it twice means writing it twice. A CTE is named for the whole statement."),
        q("Which three parts does a recursive CTE always have?",
          ["An anchor query, `UNION ALL`, and a recursive query that joins back to the CTE",
           "A SELECT, a WHERE and an ORDER BY",
           "An anchor, a `UNION`, and a LIMIT",
           "Two anchors and a join"], 0,
          "The anchor supplies the starting rows, UNION ALL stacks each round's output, and the recursive term joins the table to the previous round. It stops when a round adds nothing."),
        q("Why `UNION ALL` rather than `UNION` in the recursive step?",
          ["UNION de-duplicates, which costs a sort every round and can drop rows you needed",
           "UNION is not allowed in a CTE",
           "UNION ALL sorts the result",
           "There is no difference"], 0,
          "De-duplicating on every round is expensive and semantically wrong here — two employees can legitimately produce identical rows, and UNION would silently merge them."),
        q("What happens if a recursive CTE's anchor query returns no rows?",
          ["The whole CTE is empty, with no error",
           "SQLite reports an error", "It recurses forever", "The recursive term runs anyway"], 0,
          "Recursion needs something to start from. An empty anchor produces an empty result silently — which is why you run the anchor on its own first when debugging."),
        q("The data contains a management cycle. What happens, and what prevents it?",
          ["The query never terminates; cap the depth or refuse to revisit a visited node",
           "SQLite detects the cycle automatically",
           "The recursion stops after 100 rounds by default",
           "UNION ALL prevents cycles"], 0,
          "Nothing detects it for you. Carry a depth column and add `WHERE depth < n`, or carry a path string and refuse rows already in it."),
        q("What does `WITH t AS MATERIALIZED (...)` ask SQLite to do?",
          ["Compute the CTE once and reuse the result, instead of inlining it at each use",
           "Store the CTE permanently",
           "Create an index on the CTE",
           "Run the CTE in parallel"], 0,
          "It is an optimiser hint. Materialising pays off when the CTE is expensive and referenced more than once; NOT MATERIALIZED forces inlining, which can let a filter push down into it."),
        q("How do you generate a complete list of months to join sparse data onto?",
          ["A recursive CTE that starts at the first month and adds one month per round",
           "SELECT DISTINCT month FROM the data",
           "A CROSS JOIN of the data with itself",
           "You cannot; you need a calendar table"], 0,
          "The recursive CTE builds the full series from nothing, and a LEFT JOIN onto it turns missing months into 0 instead of missing rows — the same reason Chapter 4 cross-joined its dimensions."),
    ],
    [
        sq("sql_cte-basic", "Name a step",
           "Compute each order's total in a CTE, then join it. Fill in the `WITH` header that names the "
           "CTE `order_totals`. Columns: `order_id`, `customer`, `total`. "
           "Order by `total` descending, then `order_id`.",
           "shop",
           "WITH order_totals AS (\n"
           "  SELECT order_id, SUM(quantity * unit_price) AS total\n"
           "  FROM order_items GROUP BY order_id\n"
           ")\n"
           "SELECT o.id AS order_id, c.name AS customer, ROUND(t.total, 2) AS total\n"
           "FROM orders o\n"
           "JOIN customers    c ON c.id = o.customer_id\n"
           "JOIN order_totals t ON t.order_id = o.id\n"
           "ORDER BY total DESC, order_id;",
           ["WITH order_totals AS ("],
           variants=("UPDATE order_items SET quantity = 4 WHERE order_id = 105;",),
           hint="`WITH <name> AS (` — the name is what the rest of the query joins to."),
        sq("sql_cte-chain", "Chain two CTEs",
           "The first CTE computes each customer's spend; the second averages it. Fill in the second "
           "CTE's body so it reads from the first. Columns: `customer`, `total`, `vs_average`. "
           "Order by `total` descending, then `customer`.",
           "shop",
           "WITH spend AS (\n"
           "  SELECT o.customer_id, SUM(i.quantity * i.unit_price) AS total\n"
           "  FROM orders o JOIN order_items i ON i.order_id = o.id\n"
           "  GROUP BY o.customer_id\n"
           "),\n"
           "average AS (SELECT AVG(total) AS avg_total FROM spend)\n"
           "SELECT c.name AS customer, ROUND(s.total, 2) AS total,\n"
           "       ROUND(s.total - a.avg_total, 2) AS vs_average\n"
           "FROM customers c\n"
           "JOIN spend s ON s.customer_id = c.id\n"
           "CROSS JOIN average a\n"
           "ORDER BY total DESC, customer;",
           ["SELECT AVG(total) AS avg_total FROM spend"],
           variants=("UPDATE order_items SET unit_price = 100.00 WHERE order_id = 101;",),
           hint="A CTE can read the CTEs declared before it, so just average `total` over `spend`."),
        sq("sql_cte-anchor", "The anchor",
           "Walk the org chart from the top. Fill in the anchor's `WHERE` — the condition that picks the "
           "one person with no manager. Columns: `name`, `depth`. Order by `depth`, then `name`.",
           "hr",
           "WITH RECURSIVE chain AS (\n"
           "  SELECT id, name, 1 AS depth FROM employees WHERE manager_id IS NULL\n"
           "  UNION ALL\n"
           "  SELECT e.id, e.name, c.depth + 1 FROM employees e JOIN chain c ON e.manager_id = c.id\n"
           ")\n"
           "SELECT name, depth FROM chain ORDER BY depth, name;",
           ["WHERE manager_id IS NULL"],
           variants=("UPDATE employees SET manager_id = 2 WHERE name = 'Ana';",),
           hint="The root of the hierarchy is the row whose manager_id is absent."),
        sq("sql_cte-step", "The recursive step",
           "Same walk, but the recursive term is missing. Fill in the line that finds everyone reporting "
           "to somebody already in `chain`. Columns: `name`, `depth`. Order by `depth`, then `name`.",
           "hr",
           "WITH RECURSIVE chain AS (\n"
           "  SELECT id, name, 1 AS depth FROM employees WHERE manager_id IS NULL\n"
           "  UNION ALL\n"
           "  SELECT e.id, e.name, c.depth + 1 FROM employees e JOIN chain c ON e.manager_id = c.id\n"
           ")\n"
           "SELECT name, depth FROM chain ORDER BY depth, name;",
           ["FROM employees e JOIN chain c ON e.manager_id = c.id"],
           hint="Join the table to the CTE itself: the employee's manager_id equals a chain row's id."),
        sq("sql_cte-path", "Accumulate a path",
           "Build each person's full reporting path, `Rita > Sami > Ugo`. Fill in the expression that "
           "extends the parent's path. Columns: `path`. Order by `path`.",
           "hr",
           "WITH RECURSIVE chain AS (\n"
           "  SELECT id, name AS path FROM employees WHERE manager_id IS NULL\n"
           "  UNION ALL\n"
           "  SELECT e.id, c.path || ' > ' || e.name FROM employees e JOIN chain c ON e.manager_id = c.id\n"
           ")\n"
           "SELECT path FROM chain ORDER BY path;",
           ["c.path || ' > ' || e.name"],
           variants=("UPDATE employees SET manager_id = 4 WHERE name = 'Zeno';",),
           hint="`||` concatenates in SQL. Take the parent's path, add a separator, add this person's name."),
        sq("sql_cte-series", "Generate a series",
           "Produce every month of 2023 as `YYYY-MM`, with no table involved. Fill in the recursive step "
           "that advances one month. Columns: `month`. Order by `month`.",
           "shop",
           "WITH RECURSIVE months(month) AS (\n"
           "  SELECT '2023-01'\n"
           "  UNION ALL\n"
           "  SELECT strftime('%Y-%m', date(month || '-01', '+1 month')) FROM months WHERE month < '2023-12'\n"
           ")\n"
           "SELECT month FROM months ORDER BY month;",
           ["strftime('%Y-%m', date(month || '-01', '+1 month'))"],
           hint="Turn `2023-01` into the date `2023-01-01`, add a month, then format it back to `%Y-%m`."),
        sq("sql_cte-cap", "Cap the depth",
           "A cycle in the data would make this run forever. Fill in the guard that stops the walk after "
           "three levels. Columns: `name`, `depth`. Order by `depth`, then `name`.",
           "hr",
           "WITH RECURSIVE chain AS (\n"
           "  SELECT id, name, 1 AS depth FROM employees WHERE manager_id IS NULL\n"
           "  UNION ALL\n"
           "  SELECT e.id, e.name, c.depth + 1\n"
           "  FROM employees e JOIN chain c ON e.manager_id = c.id\n"
           "  WHERE c.depth < 3\n"
           ")\n"
           "SELECT name, depth FROM chain ORDER BY depth, name;",
           ["WHERE c.depth < 3"],
           hint="A WHERE on the recursive term, testing the depth carried from the previous round."),

        chal("sql_cte-orgchart", "The whole org chart",
             "Using one recursive CTE, list every employee with their `depth` (the CEO is 1) and their "
             "`path` from the CEO, formatted `Rita > Sami > Ugo`. "
             "Show `name`, `depth`, `path`. Order by `path`.",
             "hr",
             "WITH RECURSIVE chain AS (\n"
             "  SELECT id, name, 1 AS depth, name AS path\n"
             "  FROM employees WHERE manager_id IS NULL\n"
             "  UNION ALL\n"
             "  SELECT e.id, e.name, c.depth + 1, c.path || ' > ' || e.name\n"
             "  FROM employees e JOIN chain c ON e.manager_id = c.id\n"
             ")\n"
             "SELECT name, depth, path FROM chain ORDER BY path;",
             variants=("UPDATE employees SET manager_id = 10 WHERE name = 'Dov';",),
             hint="Carry two accumulators through the recursion — a number that increments and a string that concatenates.",
             difficulty="Medium"),
        chal("sql_cte-subtree", "Everyone under Sami",
             "List everyone in `Sami`'s reporting tree — Sami included — with their `depth` relative to "
             "Sami (Sami is 1). Show `name`, `depth`. Order by `depth`, then `name`.",
             "hr",
             "WITH RECURSIVE tree AS (\n"
             "  SELECT id, name, 1 AS depth FROM employees WHERE name = 'Sami'\n"
             "  UNION ALL\n"
             "  SELECT e.id, e.name, t.depth + 1 FROM employees e JOIN tree t ON e.manager_id = t.id\n"
             ")\n"
             "SELECT name, depth FROM tree ORDER BY depth, name;",
             variants=("UPDATE employees SET manager_id = 4 WHERE name IN ('Yara', 'Zeno');",),
             hint="Only the anchor changes: start from Sami instead of from the row with no manager.",
             difficulty="Medium"),
        chal("sql_cte-calendar", "Every month, including the empty ones",
             "Show every month of 2023 as `month` (`YYYY-MM`) with `orders` — the number of orders placed "
             "in it, **0 for months with none**. Generate the calendar with a recursive CTE and LEFT JOIN "
             "the orders onto it. Order by `month`.",
             "shop",
             "WITH RECURSIVE months(month) AS (\n"
             "  SELECT '2023-01'\n"
             "  UNION ALL\n"
             "  SELECT strftime('%Y-%m', date(month || '-01', '+1 month')) FROM months WHERE month < '2023-12'\n"
             ")\n"
             "SELECT m.month, COUNT(o.id) AS orders\n"
             "FROM months m\n"
             "LEFT JOIN orders o ON substr(o.order_date, 1, 7) = m.month\n"
             "GROUP BY m.month\n"
             "ORDER BY m.month;",
             variants=("DELETE FROM order_items; DELETE FROM orders WHERE id > 103;",),
             hint="The calendar is the preserved side, so orders join onto it with LEFT and COUNT(o.id) gives 0.",
             difficulty="Medium"),
        chal("sql_cte-topspend", "Spend, ranked against the average",
             "For every customer who has spent anything, show `customer`, `spend` (rounded to 2 decimals) "
             "and `share_pct` — their spend as a percentage of total spend across all customers, rounded "
             "to 1 decimal. Use CTEs so nothing is computed twice. "
             "Order by `spend` descending, then `customer`.",
             "shop",
             "WITH spend AS (\n"
             "  SELECT o.customer_id, SUM(i.quantity * i.unit_price) AS total\n"
             "  FROM orders o JOIN order_items i ON i.order_id = o.id\n"
             "  GROUP BY o.customer_id\n"
             "),\n"
             "grand AS (SELECT SUM(total) AS all_total FROM spend)\n"
             "SELECT c.name AS customer,\n"
             "       ROUND(s.total, 2) AS spend,\n"
             "       ROUND(s.total * 100.0 / g.all_total, 1) AS share_pct\n"
             "FROM spend s\n"
             "JOIN customers c ON c.id = s.customer_id\n"
             "CROSS JOIN grand g\n"
             "ORDER BY spend DESC, customer;",
             variants=("DELETE FROM order_items WHERE order_id NOT IN (101, 103);",),
             hint="Second CTE sums the first. CROSS JOIN attaches the single grand-total row to every customer, and `* 100.0` forces float division.",
             difficulty="Medium"),
    ],
)
