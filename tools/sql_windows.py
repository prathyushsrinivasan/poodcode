# -*- coding: utf-8 -*-
"""SQL track, chapters 12-13: window functions.

Exec'd by tools/gen_seed.py after the aggregation chapters, same namespace.
"""

# ===========================================================================
# 12. Window function basics
# ===========================================================================

concept(
    "sql_window_basics",
    "SQL: Window Functions",
    "Window Functions: OVER, PARTITION BY & Frames",
    "Aggregate without collapsing: every row keeps its identity and gains a computed neighbourhood.",
    "GROUP BY answers questions about groups by destroying the rows inside them — five orders "
    "become one total and the orders are gone. A window function answers the same kind of "
    "question while leaving every row in place, so each row can carry both its own values and "
    "a fact about its neighbours: this line's amount and the order's total, this day's revenue "
    "and the running total, this salary and the department average. OVER() is what draws the "
    "neighbourhood: PARTITION BY says which rows count as neighbours, ORDER BY imposes a "
    "sequence within them, and the frame says how much of that sequence this row can see.",
    """
```sql
SELECT name, salary, dept_id,
       AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
FROM employees;
```

Thirteen rows in, **thirteen rows out** — each now carrying its department's
average. `GROUP BY` would have returned four rows and lost the names.

```
OVER (
  PARTITION BY <what makes rows neighbours>   -- optional; default = one big window
  ORDER BY     <the sequence within a partition>   -- optional
  ROWS/RANGE   <how much of that sequence this row sees>   -- optional
)
```

The rule that catches everyone: **adding `ORDER BY` to `OVER` changes the default
frame** from the whole partition to *everything up to and including this row* —
which is exactly why `SUM(x) OVER (ORDER BY d)` is a running total rather than a
grand total.

| you want | write |
|---|---|
| the group's total on every row | `SUM(x) OVER (PARTITION BY g)` |
| a running total | `SUM(x) OVER (ORDER BY d)` |
| a running total per group | `SUM(x) OVER (PARTITION BY g ORDER BY d)` |
| the previous row's value | `LAG(x) OVER (ORDER BY d)` |
| a 3-row moving average | `AVG(x) OVER (ORDER BY d ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` |
""",
    """
### Aggregate without collapsing

Compare the two directly:

```sql
-- GROUP BY: 4 rows, names destroyed
SELECT dept_id, AVG(salary) FROM employees GROUP BY dept_id;

-- OVER: 13 rows, names intact, each with its department's average
SELECT name, salary, AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg
FROM employees
ORDER BY dept_id, name;
```

| name | salary | dept_avg |
|------|--------|----------|
| Sami | 175000 | 130600.0 |
| Ugo  | 142000 | 130600.0 |
| Vera | 142000 | 130600.0 |
| Wren |  98000 | 130600.0 |
| Xu   |  96000 | 130600.0 |

Every engineer now carries the engineering average, and you can subtract on the
spot: `salary - AVG(salary) OVER (PARTITION BY dept_id)`. Doing that with
`GROUP BY` needs a subquery and a join back.

### `PARTITION BY` is `GROUP BY` for windows

`PARTITION BY dept_id` splits the rows into independent windows, one per
department; the function restarts in each. Omit it and the window is the entire
result set:

```sql
SUM(salary) OVER ()                        -- the company payroll, on every row
SUM(salary) OVER (PARTITION BY dept_id)    -- that department's payroll
```

`OVER ()` with empty parentheses is not a typo — it is "the whole result set as
one window", and it is the tidiest way to get a grand total onto every row for a
percentage-of-total calculation.

### `ORDER BY` inside `OVER` changes the frame

This is the crucial mechanic.

```sql
SUM(amount) OVER (PARTITION BY cust)                  -- the customer's TOTAL, on every row
SUM(amount) OVER (PARTITION BY cust ORDER BY date)    -- a RUNNING total
```

Without `ORDER BY`, the default frame is the whole partition. With `ORDER BY`, the
default becomes `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` — everything
from the start of the partition up to here. Same function, same partition,
completely different number, and nothing in the syntax shouts about it.

### Frames: `ROWS` versus `RANGE`

Spell the frame out when you want something other than the default:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW   -- running total (explicit)
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW           -- 3-row moving window
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING           -- centred on this row
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING   -- everything from here on
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- the default when ORDER BY is present
```

The difference between `ROWS` and `RANGE` only shows up with **ties**:

- `ROWS` counts physical rows. `2 PRECEDING` means the two rows above, whatever
  their values.
- `RANGE` works on values. With `ORDER BY salary`, `CURRENT ROW` in `RANGE` mode
  includes *every* row with the same salary.

So a running total ordered by a column with duplicates jumps in steps under
`RANGE` and increments one row at a time under `ROWS`. When in doubt for a moving
average or a running total, write `ROWS` — it does what people picture.

### Where window functions may appear

```
FROM -> WHERE -> GROUP BY -> HAVING -> [WINDOW FUNCTIONS] -> SELECT -> ORDER BY
```

They run **after** `WHERE`, `GROUP BY` and `HAVING`, and **before** the final
`ORDER BY`. Two consequences:

1. **You cannot filter on a window function in `WHERE` or `HAVING`.**
   `WHERE ROW_NUMBER() OVER (...) = 1` is an error. Wrap the query in a CTE and
   filter outside — that is the whole technique behind top-N-per-group.
2. **They see post-aggregation rows.** You can combine them with `GROUP BY`:
   `SUM(SUM(amount)) OVER (ORDER BY month)` is a running total *of monthly
   totals*, and it is legal precisely because the window runs after the grouping.

### Naming a window

When three functions share one window, declare it once:

```sql
SELECT name, salary,
       AVG(salary) OVER w AS dept_avg,
       MIN(salary) OVER w AS dept_min,
       MAX(salary) OVER w AS dept_max
FROM employees
WINDOW w AS (PARTITION BY dept_id);
```

### Watch out for

- **`ORDER BY` in `OVER` silently turns a total into a running total.**
- **`WHERE` cannot see a window function.** Use a CTE.
- **`RANGE` with ties** behaves differently from `ROWS`; prefer `ROWS` unless you
  specifically want value-based grouping.
- **`ORDER BY` in `OVER` is not the query's `ORDER BY`.** The window's order
  controls the computation; the outer one controls the output. Write both.
- **A partition with one row** gives `LAG` a `NULL`, `AVG` its own value, and a
  running total equal to itself. Usually right, occasionally not what a report
  wants — `COALESCE` accordingly.
""",
    [
        q("What is the essential difference between `GROUP BY` and a window function?",
          ["GROUP BY collapses rows into one per group; a window function keeps every row and adds a computed column",
           "Window functions are faster",
           "GROUP BY cannot use AVG",
           "Window functions can only be used with ORDER BY"], 0,
          "Both compute over a set of rows. GROUP BY returns one row per set; OVER returns every original row, each carrying the value computed over its window."),
        q("What does adding `ORDER BY` inside `OVER (...)` change?",
          ["The default frame becomes 'start of partition to current row', turning a total into a running total",
           "Only the output order",
           "Nothing — it is decorative",
           "It makes the function ignore NULLs"], 0,
          "Without ORDER BY the frame is the whole partition. With it, the default is UNBOUNDED PRECEDING to CURRENT ROW — the single most surprising default in SQL."),
        q("What does `OVER ()` with empty parentheses mean?",
          ["The window is the entire result set — useful for putting a grand total on every row",
           "It is a syntax error",
           "The window is one row",
           "The window is the current GROUP BY group"], 0,
          "An empty OVER treats every row as a neighbour, which is the tidiest way to compute each row's share of the overall total."),
        q("When do `ROWS` and `RANGE` frames differ?",
          ["When the ORDER BY column has ties: RANGE includes every row with the same value, ROWS counts physical rows",
           "Never — they are synonyms",
           "Only with PARTITION BY",
           "RANGE only works on dates"], 0,
          "RANGE is value-based, ROWS is position-based. A running total ordered by a column with duplicates jumps in steps under RANGE. Prefer ROWS unless you want the value semantics."),
        q("Why is `WHERE ROW_NUMBER() OVER (...) = 1` an error?",
          ["Window functions run after WHERE, so the value does not exist yet — wrap the query in a CTE",
           "ROW_NUMBER needs a PARTITION BY",
           "You must use HAVING instead",
           "It is valid SQL"], 0,
          "The pipeline is FROM, WHERE, GROUP BY, HAVING, then window functions. Compute the number in a CTE or subquery and filter on it in the outer query."),
        q("Is `SUM(SUM(amount)) OVER (ORDER BY month)` legal?",
          ["Yes — the window runs after grouping, so it is a running total of the monthly totals",
           "No, aggregates cannot be nested",
           "Yes, but it means the same as `SUM(amount)`",
           "Only in a CTE"], 0,
          "The inner SUM aggregates within each month; the outer windowed SUM then runs across the grouped rows. It reads oddly and is the standard way to write a running total of a grouped measure."),
        q("What does `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` give you?",
          ["A three-row moving window: the two rows before this one plus this one",
           "The two rows before this one only",
           "Every row up to this one",
           "The two rows after this one"], 0,
          "The frame is inclusive at both ends, so 2 PRECEDING through CURRENT ROW is three rows — the usual shape for a moving average."),
    ],
    [
        sq("sql_window_basics-partition", "The group's average, on every row",
           "Show every employee with their department's average salary alongside their own. Fill in the "
           "`OVER` clause. Columns: `employee`, `salary`, `dept_avg` (rounded to 2). "
           "Order by `dept_id`, then `employee`.",
           "hr",
           "SELECT e.name AS employee, e.salary,\n"
           "       ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id), 2) AS dept_avg\n"
           "FROM employees e\n"
           "ORDER BY e.dept_id, e.name;",
           ["OVER (PARTITION BY e.dept_id)"],
           variants=("UPDATE employees SET dept_id = 1 WHERE dept_id IS NULL;",),
           hint="`OVER (PARTITION BY <column>)` — the column that decides which rows are neighbours."),
        sq("sql_window_basics-empty", "The grand total, on every row",
           "Show each order's total next to the total across all orders, and its share as a percentage. "
           "Fill in the empty `OVER`. Columns: `order_id`, `total`, `share_pct`. "
           "Order by `share_pct` descending, then `order_id`.",
           "shop",
           "WITH t AS (\n"
           "  SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id\n"
           ")\n"
           "SELECT order_id, ROUND(total, 2) AS total,\n"
           "       ROUND(total * 100.0 / SUM(total) OVER (), 1) AS share_pct\n"
           "FROM t\n"
           "ORDER BY share_pct DESC, order_id;",
           ["SUM(total) OVER ()"],
           variants=("DELETE FROM order_items WHERE order_id > 105;",),
           hint="Empty parentheses after OVER mean 'the whole result set is the window'."),
        sq("sql_window_basics-running", "A running total",
           "Show the orders in date order with a running count of orders so far. Fill in the `OVER` "
           "clause — the presence of `ORDER BY` inside it is what makes the count cumulative. "
           "Columns: `order_id`, `order_date`, `running_orders`. Order by `order_date`, then `order_id`.",
           "shop",
           "SELECT id AS order_id, order_date,\n"
           "       COUNT(*) OVER (ORDER BY order_date, id) AS running_orders\n"
           "FROM orders\n"
           "ORDER BY order_date, id;",
           ["OVER (ORDER BY order_date, id)"],
           variants=("DELETE FROM order_items; DELETE FROM orders WHERE id % 2 = 0;",),
           hint="ORDER BY inside OVER, tie-broken by id so the sequence is deterministic."),
        sq("sql_window_basics-runpart", "A running total per group",
           "Give each customer their own running spend across their orders in date order. Fill in the "
           "`OVER` clause. Columns: `customer`, `order_date`, `order_total`, `running_spend`. "
           "Order by `customer`, then `order_date`.",
           "shop",
           "WITH t AS (\n"
           "  SELECT o.customer_id, o.id, o.order_date,\n"
           "         SUM(i.quantity * i.unit_price) AS order_total\n"
           "  FROM orders o JOIN order_items i ON i.order_id = o.id\n"
           "  GROUP BY o.customer_id, o.id, o.order_date\n"
           ")\n"
           "SELECT c.name AS customer, t.order_date,\n"
           "       ROUND(t.order_total, 2) AS order_total,\n"
           "       ROUND(SUM(t.order_total) OVER (PARTITION BY t.customer_id ORDER BY t.order_date, t.id), 2) AS running_spend\n"
           "FROM t JOIN customers c ON c.id = t.customer_id\n"
           "ORDER BY customer, t.order_date;",
           ["OVER (PARTITION BY t.customer_id ORDER BY t.order_date, t.id)"],
           variants=("UPDATE order_items SET quantity = 2;",),
           hint="Both clauses inside one OVER: PARTITION BY the customer, ORDER BY the date."),
        sq("sql_window_basics-frame", "A three-row moving average",
           "Average each session's page-view duration over itself and the two page views before it. "
           "Fill in the frame. Columns: `view_id`, `ms_on_page`, `moving_avg` (rounded to 1). "
           "Order by `view_id`.",
           "events",
           "SELECT id AS view_id, ms_on_page,\n"
           "       ROUND(AVG(ms_on_page) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS moving_avg\n"
           "FROM page_views\n"
           "ORDER BY id;",
           ["ROWS BETWEEN 2 PRECEDING AND CURRENT ROW"],
           variants=("UPDATE page_views SET ms_on_page = ms_on_page * 2 WHERE id % 3 = 0;",),
           hint="`ROWS BETWEEN <n> PRECEDING AND CURRENT ROW` — inclusive at both ends, so 2 PRECEDING gives three rows."),
        sq("sql_window_basics-named", "Name the window once",
           "Three functions share the same window. Fill in the `WINDOW` clause that declares it as `w`. "
           "Columns: `employee`, `salary`, `dept_min`, `dept_max`. Order by `dept_id`, then `employee`.",
           "hr",
           "SELECT e.name AS employee, e.salary,\n"
           "       MIN(e.salary) OVER w AS dept_min,\n"
           "       MAX(e.salary) OVER w AS dept_max\n"
           "FROM employees e\n"
           "WINDOW w AS (PARTITION BY e.dept_id)\n"
           "ORDER BY e.dept_id, e.name;",
           ["WINDOW w AS (PARTITION BY e.dept_id)"],
           hint="`WINDOW <name> AS (<the OVER body>)`, placed after FROM/WHERE and before ORDER BY."),
        sq("sql_window_basics-aggwindow", "A running total of grouped totals",
           "Group the orders by month, then run a cumulative total across the months. The nesting is "
           "legal because windows run after grouping — fill in the windowed aggregate. "
           "Columns: `month`, `monthly_orders`, `orders_to_date`. Order by `month`.",
           "shop",
           "SELECT substr(order_date, 1, 7) AS month,\n"
           "       COUNT(*) AS monthly_orders,\n"
           "       SUM(COUNT(*)) OVER (ORDER BY substr(order_date, 1, 7)) AS orders_to_date\n"
           "FROM orders\n"
           "GROUP BY substr(order_date, 1, 7)\n"
           "ORDER BY month;",
           ["SUM(COUNT(*)) OVER (ORDER BY substr(order_date, 1, 7))"],
           variants=("UPDATE orders SET order_date = '2023-03-11' WHERE id > 108;",),
           hint="An aggregate inside a windowed aggregate: SUM(COUNT(*)) OVER (ORDER BY the month expression)."),

        chal("sql_window_basics-vsavg", "Above or below your department",
             "For every employee in a department, show `employee`, `department`, `salary`, `dept_avg` "
             "(rounded to 2) and `diff` — their salary minus that average, rounded to 2. Employees with "
             "no department are excluded. Order by `diff` descending, then `employee`.",
             "hr",
             "SELECT e.name AS employee, d.name AS department, e.salary,\n"
             "       ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id), 2) AS dept_avg,\n"
             "       ROUND(e.salary - AVG(e.salary) OVER (PARTITION BY e.dept_id), 2) AS diff\n"
             "FROM employees e\n"
             "JOIN departments d ON d.id = e.dept_id\n"
             "ORDER BY diff DESC, employee;",
             variants=("UPDATE employees SET salary = 60000 WHERE dept_id = 1 AND name <> 'Sami';",),
             hint="The same window expression can be used twice — once shown, once subtracted. No subquery or self-join needed.",
             difficulty="Medium"),
        chal("sql_window_basics-cumulative", "Cumulative revenue by month",
             "For every month that has shipped orders, show `month` (`YYYY-MM`), `revenue` (that month's "
             "total `quantity * unit_price`, rounded to 2) and `cumulative` (revenue to date, rounded to "
             "2). Order by `month`.",
             "shop",
             "SELECT substr(o.order_date, 1, 7) AS month,\n"
             "       ROUND(SUM(i.quantity * i.unit_price), 2) AS revenue,\n"
             "       ROUND(SUM(SUM(i.quantity * i.unit_price)) OVER (ORDER BY substr(o.order_date, 1, 7)), 2) AS cumulative\n"
             "FROM orders o\n"
             "JOIN order_items i ON i.order_id = o.id\n"
             "WHERE o.status = 'shipped'\n"
             "GROUP BY substr(o.order_date, 1, 7)\n"
             "ORDER BY month;",
             variants=("UPDATE orders SET status = 'shipped';",),
             hint="Group by month first; the windowed SUM then runs over the grouped rows, which is why the aggregate is nested.",
             difficulty="Medium"),
        chal("sql_window_basics-share", "Each line's share of its order",
             "For every order line, show `order_id`, `product`, `line_total` (rounded to 2) and "
             "`pct_of_order` — that line's share of its own order's total, as a percentage rounded to 1 "
             "decimal. Order by `order_id`, then `pct_of_order` descending, then `product`.",
             "shop",
             "SELECT i.order_id, p.name AS product,\n"
             "       ROUND(i.quantity * i.unit_price, 2) AS line_total,\n"
             "       ROUND((i.quantity * i.unit_price) * 100.0\n"
             "             / SUM(i.quantity * i.unit_price) OVER (PARTITION BY i.order_id), 1) AS pct_of_order\n"
             "FROM order_items i\n"
             "JOIN products p ON p.id = i.product_id\n"
             "ORDER BY i.order_id, pct_of_order DESC, product;",
             variants=("UPDATE order_items SET quantity = id;",),
             hint="Partition by the order so the denominator is that order's total. No ORDER BY inside OVER — you want the whole partition, not a running sum.",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 13. Ranking, LAG/LEAD, top-N-per-group
# ===========================================================================

concept(
    "sql_window_rank",
    "SQL: Window Functions",
    "Ranking, LAG/LEAD & Top-N Per Group",
    "ROW_NUMBER, RANK and DENSE_RANK; reading neighbouring rows; and the CTE-then-filter pattern.",
    "Three ranking functions exist because ties can mean three different things, and choosing "
    "the wrong one produces a report that is subtly, arguably wrong rather than obviously "
    "broken. ROW_NUMBER breaks every tie arbitrarily and gives exactly one row per position, "
    "which is what deduplication and pagination need. RANK gives tied rows the same number and "
    "then skips, the way sports standings work. DENSE_RANK gives them the same number and does "
    "not skip. Alongside them, LAG and LEAD read the previous and next row directly, replacing "
    "an entire family of awkward self joins. All of them share one structural constraint: you "
    "cannot filter on them where they are computed, so the answer is always a CTE.",
    """
```sql
ROW_NUMBER() OVER (PARTITION BY g ORDER BY x DESC)   -- 1,2,3,4  (ties broken arbitrarily)
RANK()       OVER (PARTITION BY g ORDER BY x DESC)   -- 1,2,2,4  (ties share, then skip)
DENSE_RANK() OVER (PARTITION BY g ORDER BY x DESC)   -- 1,2,2,3  (ties share, no skip)

LAG(x)  OVER (ORDER BY d)      -- the previous row's x   (NULL on the first row)
LEAD(x) OVER (ORDER BY d)      -- the next row's x       (NULL on the last row)
LAG(x, 2, 0) OVER (ORDER BY d) -- two rows back, defaulting to 0
```

**Top-N per group** — the pattern this chapter exists for:

```sql
WITH ranked AS (
  SELECT ..., ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
  FROM employees
)
SELECT * FROM ranked WHERE rn <= 2;
```

The CTE is not stylistic. `WHERE rn <= 2` is impossible in the inner query,
because window functions are computed after `WHERE` runs.
""",
    """
### Three functions, one tie

Engineering has `Sami 175000`, `Ugo 142000`, `Vera 142000`, `Wren 98000`,
`Xu 96000`. Ordered by salary descending:

| name | salary | ROW_NUMBER | RANK | DENSE_RANK |
|------|--------|-----------:|-----:|-----------:|
| Sami | 175000 | 1 | 1 | 1 |
| Ugo  | 142000 | 2 | 2 | 2 |
| Vera | 142000 | 3 | 2 | 2 |
| Wren |  98000 | 4 | 4 | 3 |
| Xu   |  96000 | 5 | 5 | 4 |

- **`ROW_NUMBER`** — always 1..n, no gaps, no duplicates. Ugo gets 2 and Vera gets
  3 *arbitrarily*; nothing in the data decides it. Add a tie-breaker to `ORDER BY`
  if you need the result to be reproducible.
- **`RANK`** — tied rows share, then the next value skips ahead. Two silver
  medals, no bronze.
- **`DENSE_RANK`** — tied rows share, and nothing is skipped. Answers "which
  distinct salary level is this".

Choose by the question: *"give me one row per group"* → `ROW_NUMBER`. *"who is in
the top 3, ties included"* → `RANK`. *"what are the three highest salaries"* →
`DENSE_RANK`.

### Top-N per group

The pattern in full, with a tie-breaker so it is deterministic:

```sql
WITH ranked AS (
  SELECT e.name, e.salary, d.name AS department,
         ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC, e.name) AS rn
  FROM employees e
  JOIN departments d ON d.id = e.dept_id
)
SELECT department, name, salary
FROM ranked
WHERE rn <= 2
ORDER BY department, rn;
```

Swap `ROW_NUMBER` for `RANK` and Ugo *and* Vera both come back — "the top 2
salaries" rather than "2 people". That one-word change is the entire difference
between the two reports, and it is worth being deliberate about which one the
request asked for.

### Deduplication

The other everyday use of `ROW_NUMBER`: keep one row per key.

```sql
WITH ranked AS (
  SELECT r.*, ROW_NUMBER() OVER (PARTITION BY respondent_id ORDER BY submitted_at DESC, id DESC) AS rn
  FROM responses r
)
SELECT * FROM ranked WHERE rn = 1;      -- each respondent's latest response
```

Partition by what should be unique, order by what decides the winner, keep `rn = 1`.
The same shape deletes duplicates (`DELETE ... WHERE id IN (SELECT id FROM ranked
WHERE rn > 1)`).

### `LAG` and `LEAD` — the previous and next row

```sql
SELECT order_date,
       total,
       LAG(total)  OVER (ORDER BY order_date) AS prev_total,
       total - LAG(total) OVER (ORDER BY order_date) AS change
FROM daily;
```

The first row's `LAG` is `NULL`, so `change` is `NULL` there — correct, since
there is nothing to compare against. Supply a default if you would rather have a
number: `LAG(total, 1, 0)`.

Chapter 7 built a running count with a quadratic self join. `LAG` is the same idea
done properly: one pass, no join, and it does not care whether the keys are
consecutive.

Related, and useful:

```sql
FIRST_VALUE(x) OVER (PARTITION BY g ORDER BY d)   -- the group's first value, on every row
LAST_VALUE(x)  OVER (PARTITION BY g ORDER BY d
                     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
NTILE(4)       OVER (ORDER BY x)                  -- quartile buckets
```

`LAST_VALUE` almost always needs that explicit frame: the default frame ends at
the current row, so without it `LAST_VALUE` returns the current row's own value —
a classic and very confusing bug.

### Gaps and islands

The showcase problem. `ada` has sessions on March 1, 2, 3, 6 and 7. Find the runs
of consecutive days:

```sql
WITH days AS (
  SELECT DISTINCT user_id, date(started_at) AS d FROM sessions
),
marked AS (
  SELECT user_id, d,
         julianday(d) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY d) AS grp
  FROM days
)
SELECT user_id, MIN(d) AS run_start, MAX(d) AS run_end, COUNT(*) AS days
FROM marked
GROUP BY user_id, grp;
```

The trick: for consecutive days, the date and the row number both increase by 1,
so their **difference is constant** within a run and jumps at every gap. Grouping
by that difference groups by run. It looks like sleight of hand the first time and
becomes obvious the second.

### Watch out for

- **`WHERE rn = 1` in the same `SELECT`** that computes `rn` is an error. Always
  a CTE.
- **`ROW_NUMBER` without a tie-breaker** gives non-reproducible results whenever
  the ordering column has duplicates.
- **`LAST_VALUE` without an explicit frame** returns the current row.
- **`LAG` across a partition boundary** returns `NULL`, not the previous
  partition's last row — which is right, and worth confirming you wanted.
- **`RANK` vs `DENSE_RANK` in a "top 3"** filter: `RANK <= 3` can return fewer
  than three distinct values after a tie, `DENSE_RANK <= 3` always returns three
  levels.
""",
    [
        q("Salaries 175000, 142000, 142000, 98000. What does `RANK()` produce, descending?",
          ["1, 2, 2, 4", "1, 2, 2, 3", "1, 2, 3, 4", "1, 1, 2, 3"], 0,
          "RANK gives tied rows the same value and then skips the positions they consumed — two silver medals and no bronze. DENSE_RANK would give 1, 2, 2, 3."),
        q("You need exactly one row per group. Which function?",
          ["ROW_NUMBER, with a tie-breaker in ORDER BY so the winner is reproducible",
           "RANK", "DENSE_RANK", "NTILE(1)"], 0,
          "Only ROW_NUMBER guarantees a single row at position 1. RANK and DENSE_RANK both give tied rows the same number, so `= 1` could return several."),
        q("Why must top-N-per-group be written with a CTE?",
          ["Window functions are computed after WHERE, so you cannot filter on the rank where you compute it",
           "CTEs are faster",
           "ROW_NUMBER requires a CTE",
           "To avoid a cartesian product"], 0,
          "The pipeline runs WHERE before window functions exist. Computing the rank in a CTE (or subquery) and filtering in the outer query is the only way."),
        q("What does `LAG(x) OVER (ORDER BY d)` return on the first row of a partition?",
          ["NULL — supply a third argument to LAG for a default",
           "0", "The last row's value", "An error"], 0,
          "There is no previous row, so the result is NULL. `LAG(x, 1, 0)` substitutes 0 instead."),
        q("Why does `LAST_VALUE(x) OVER (PARTITION BY g ORDER BY d)` return the current row's value?",
          ["The default frame ends at the current row, so the 'last' value is this one",
           "LAST_VALUE is broken in SQLite",
           "It needs DESC ordering",
           "It requires PARTITION BY to be omitted"], 0,
          "With ORDER BY present the default frame is UNBOUNDED PRECEDING to CURRENT ROW. Spell out `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to see the whole partition."),
        q("In the gaps-and-islands trick, why does `date - ROW_NUMBER()` identify a run?",
          ["Within a run both increase by 1 each row, so the difference is constant and changes at every gap",
           "ROW_NUMBER restarts at each gap",
           "Dates are stored as integers",
           "It only works when the dates are sorted"], 0,
          "Two sequences advancing in lockstep have a constant difference; a skipped date breaks the lockstep and shifts the difference. Grouping by it groups by run."),
        q("`WHERE RANK() <= 3` vs `WHERE DENSE_RANK() <= 3` — how do they differ after a tie?",
          ["RANK can return fewer than three distinct values; DENSE_RANK always returns three levels",
           "They are identical",
           "DENSE_RANK returns fewer rows",
           "RANK cannot be filtered"], 0,
          "A three-way tie at position 1 makes RANK jump to 4, so `RANK <= 3` returns only that tied group. DENSE_RANK counts distinct levels, so it always reaches three of them."),
    ],
    [
        sq("sql_window_rank-rownumber", "Number the rows",
           "Number each department's employees from highest-paid down, one number per person. Fill in "
           "the function. Columns: `department`, `employee`, `salary`, `rn`. "
           "Order by `department`, then `rn`.",
           "hr",
           "SELECT d.name AS department, e.name AS employee, e.salary,\n"
           "       ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC, e.name) AS rn\n"
           "FROM employees e\n"
           "JOIN departments d ON d.id = e.dept_id\n"
           "ORDER BY department, rn;",
           ["ROW_NUMBER()"],
           variants=("UPDATE employees SET salary = 100000 WHERE dept_id = 1;",),
           hint="The one that always produces 1, 2, 3 with no gaps and no repeats."),
        sq("sql_window_rank-three", "All three at once",
           "Show the difference between the ranking functions on Engineering's salaries. Fill in the "
           "two missing ones. Columns: `employee`, `salary`, `rn`, `rnk`, `dense`. "
           "Order by `salary` descending, then `employee`.",
           "hr",
           "SELECT e.name AS employee, e.salary,\n"
           "       ROW_NUMBER() OVER (ORDER BY e.salary DESC, e.name) AS rn,\n"
           "       RANK()       OVER (ORDER BY e.salary DESC) AS rnk,\n"
           "       DENSE_RANK() OVER (ORDER BY e.salary DESC) AS dense\n"
           "FROM employees e\n"
           "WHERE e.dept_id = 1\n"
           "ORDER BY e.salary DESC, employee;",
           ["RANK()       OVER (ORDER BY e.salary DESC) AS rnk,\n       DENSE_RANK() OVER (ORDER BY e.salary DESC) AS dense"],
           variants=("UPDATE employees SET salary = 142000 WHERE dept_id = 1;",),
           hint="One shares-and-skips, the other shares-without-skipping. Both take no arguments."),
        sq("sql_window_rank-topn", "Top two per department",
           "Keep each department's two highest-paid people. Fill in the filter on the CTE's rank column. "
           "Columns: `department`, `employee`, `salary`. Order by `department`, then `rn`.",
           "hr",
           "WITH ranked AS (\n"
           "  SELECT d.name AS department, e.name AS employee, e.salary,\n"
           "         ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC, e.name) AS rn\n"
           "  FROM employees e JOIN departments d ON d.id = e.dept_id\n"
           ")\n"
           "SELECT department, employee, salary FROM ranked\n"
           "WHERE rn <= 2\n"
           "ORDER BY department, rn;",
           ["WHERE rn <= 2"],
           variants=("UPDATE employees SET dept_id = 2 WHERE name IN ('Wren', 'Xu');",),
           hint="A plain WHERE on the CTE's column — legal out here, impossible inside."),
        sq("sql_window_rank-dedupe", "Keep the latest row per key",
           "The survey lets a respondent answer more than once. Keep only each respondent's most recent "
           "response. Fill in the `OVER` clause. Columns: `respondent`, `submitted_at`, `q1_score`. "
           "Order by `respondent`.",
           "survey",
           "WITH ranked AS (\n"
           "  SELECT r.respondent_id, r.submitted_at, r.q1_score,\n"
           "         ROW_NUMBER() OVER (PARTITION BY r.respondent_id ORDER BY r.submitted_at DESC, r.id DESC) AS rn\n"
           "  FROM responses r\n"
           ")\n"
           "SELECT p.name AS respondent, k.submitted_at, k.q1_score\n"
           "FROM ranked k JOIN respondents p ON p.id = k.respondent_id\n"
           "WHERE k.rn = 1\n"
           "ORDER BY respondent;",
           ["OVER (PARTITION BY r.respondent_id ORDER BY r.submitted_at DESC, r.id DESC)"],
           variants=("INSERT INTO responses (id, respondent_id, q1_score, q2_score, comment, submitted_at) VALUES (7, 2, 3, 3, 'Later', '2024-06-01');",),
           hint="Partition by what should be unique; order so the row you want to keep sorts first."),
        sq("sql_window_rank-lag", "Read the previous row",
           "Show each order's total next to the previous order's total, in date order. Fill in the "
           "function. Columns: `order_id`, `order_date`, `total`, `prev_total`. "
           "Order by `order_date`, then `order_id`.",
           "shop",
           "WITH t AS (\n"
           "  SELECT o.id, o.order_date, SUM(i.quantity * i.unit_price) AS total\n"
           "  FROM orders o JOIN order_items i ON i.order_id = o.id\n"
           "  GROUP BY o.id, o.order_date\n"
           ")\n"
           "SELECT id AS order_id, order_date, ROUND(total, 2) AS total,\n"
           "       ROUND(LAG(total) OVER (ORDER BY order_date, id), 2) AS prev_total\n"
           "FROM t\n"
           "ORDER BY order_date, id;",
           ["LAG(total) OVER (ORDER BY order_date, id)"],
           variants=("UPDATE order_items SET unit_price = 10.00;",),
           hint="Three letters, then the column, then an OVER with the ordering that defines 'previous'."),
        sq("sql_window_rank-lead", "Read the next row",
           "For each of a user's sessions, show when their next session started. Fill in the function. "
           "Columns: `user_id`, `started_at`, `next_started_at`. Order by `user_id`, then `started_at`.",
           "events",
           "SELECT user_id, started_at,\n"
           "       LEAD(started_at) OVER (PARTITION BY user_id ORDER BY started_at) AS next_started_at\n"
           "FROM sessions\n"
           "ORDER BY user_id, started_at;",
           ["LEAD(started_at) OVER (PARTITION BY user_id ORDER BY started_at)"],
           variants=("DELETE FROM page_views WHERE session_id > 6; DELETE FROM sessions WHERE id > 6;",),
           hint="The mirror image of LAG, partitioned so it never reads across into another user's sessions."),
        sq("sql_window_rank-lastvalue", "Make LAST_VALUE see the whole partition",
           "Show every employee with the lowest-paid person in their department. The default frame stops "
           "at the current row, so fill in the frame that opens it up. "
           "Columns: `employee`, `salary`, `lowest_in_dept`. Order by `dept_id`, then `salary` desc, then `employee`.",
           "hr",
           "SELECT e.name AS employee, e.salary,\n"
           "       LAST_VALUE(e.salary) OVER (\n"
           "         PARTITION BY e.dept_id ORDER BY e.salary DESC\n"
           "         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING\n"
           "       ) AS lowest_in_dept\n"
           "FROM employees e\n"
           "ORDER BY e.dept_id, e.salary DESC, employee;",
           ["ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING"],
           hint="Both bounds unbounded, so the frame covers the entire partition rather than stopping here."),

        chal("sql_window_rank-topprod", "Best seller in each category",
             "For every category that has sold anything, show `category`, `product` and `units` — the "
             "single best-selling product by total quantity. Break ties by product name (alphabetically "
             "first wins), so exactly one row per category comes back. "
             "Order by `units` descending, then `category`.",
             "shop",
             "WITH sales AS (\n"
             "  SELECT cat.name AS category, p.name AS product, SUM(i.quantity) AS units\n"
             "  FROM order_items i\n"
             "  JOIN products   p   ON p.id = i.product_id\n"
             "  JOIN categories cat ON cat.id = p.category_id\n"
             "  GROUP BY cat.id, cat.name, p.id, p.name\n"
             "),\n"
             "ranked AS (\n"
             "  SELECT category, product, units,\n"
             "         ROW_NUMBER() OVER (PARTITION BY category ORDER BY units DESC, product) AS rn\n"
             "  FROM sales\n"
             ")\n"
             "SELECT category, product, units FROM ranked\n"
             "WHERE rn = 1\n"
             "ORDER BY units DESC, category;",
             variants=("UPDATE order_items SET quantity = 1;",),
             hint="Aggregate to per-product sales first, rank within category with a deterministic tie-break, then keep rn = 1.",
             difficulty="Medium"),
        chal("sql_window_rank-monthdelta", "Month-on-month change",
             "For each month with shipped orders, show `month`, `revenue` (rounded to 2), `prev_revenue` "
             "(the previous listed month's revenue, NULL for the first) and `change` (the difference, "
             "rounded to 2, NULL for the first). Order by `month`.",
             "shop",
             "WITH monthly AS (\n"
             "  SELECT substr(o.order_date, 1, 7) AS month,\n"
             "         SUM(i.quantity * i.unit_price) AS revenue\n"
             "  FROM orders o JOIN order_items i ON i.order_id = o.id\n"
             "  WHERE o.status = 'shipped'\n"
             "  GROUP BY substr(o.order_date, 1, 7)\n"
             ")\n"
             "SELECT month,\n"
             "       ROUND(revenue, 2) AS revenue,\n"
             "       ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_revenue,\n"
             "       ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2) AS change\n"
             "FROM monthly\n"
             "ORDER BY month;",
             variants=("UPDATE orders SET status = 'shipped';",),
             hint="Aggregate to one row per month in a CTE, then LAG across those rows. The first row's LAG is NULL and so is its change — that is correct.",
             difficulty="Medium"),
        chal("sql_window_rank-islands", "Streaks of consecutive active days",
             "For every user, find their runs of consecutive days on which they started at least one "
             "session. Show `user_email`, `run_start`, `run_end` and `days`. "
             "Order by `user_email`, then `run_start`.",
             "events",
             "WITH days AS (\n"
             "  SELECT DISTINCT user_id, date(started_at) AS d FROM sessions\n"
             "),\n"
             "marked AS (\n"
             "  SELECT user_id, d,\n"
             "         julianday(d) - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY d) AS grp\n"
             "  FROM days\n"
             ")\n"
             "SELECT u.email AS user_email, MIN(m.d) AS run_start, MAX(m.d) AS run_end, COUNT(*) AS days\n"
             "FROM marked m\n"
             "JOIN users u ON u.id = m.user_id\n"
             "GROUP BY u.email, m.grp\n"
             "ORDER BY user_email, run_start;",
             variants=("INSERT INTO sessions (id, user_id, started_at, ended_at, device) VALUES (13, 1, '2024-03-04 08:00:00', '2024-03-04 08:10:00', 'mobile'), (14, 1, '2024-03-05 08:00:00', '2024-03-05 08:10:00', 'mobile');",),
             hint="Distinct days per user, then subtract the row number from the day number. That difference is constant inside a run, so group by it.",
             difficulty="Medium"),
        chal("sql_window_rank-quartile", "Salary quartiles",
             "Split all employees into four salary quartiles with `NTILE(4)` ordered by salary ascending "
             "(tie-broken by name). Show `quartile`, `headcount`, `min_salary` and `max_salary`. "
             "Order by `quartile`.",
             "hr",
             "WITH q AS (\n"
             "  SELECT name, salary, NTILE(4) OVER (ORDER BY salary, name) AS quartile\n"
             "  FROM employees\n"
             ")\n"
             "SELECT quartile, COUNT(*) AS headcount, MIN(salary) AS min_salary, MAX(salary) AS max_salary\n"
             "FROM q\n"
             "GROUP BY quartile\n"
             "ORDER BY quartile;",
             variants=("DELETE FROM employees WHERE manager_id IS NOT NULL AND id > 8;",),
             hint="NTILE assigns the bucket in a CTE; the outer query then aggregates per bucket. With 13 rows the buckets are not all the same size, which is expected.",
             difficulty="Medium"),
    ],
)
