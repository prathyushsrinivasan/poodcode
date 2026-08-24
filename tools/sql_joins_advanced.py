# -*- coding: utf-8 -*-
"""SQL track, chapters 6-8: the joins that are not "table A to table B".

A table joined to itself, a join whose condition is a range rather than an
equality, and what happens once five tables are in play. Exec'd by
tools/gen_seed.py after tools/sql_joins.py, in the same namespace.
"""

# ===========================================================================
# 6. Self joins
# ===========================================================================

concept(
    "sql_self_join",
    "SQL: Join Foundations",
    "Self Joins",
    "Join a table to itself to put two of its own rows side by side.",
    "A self join looks exotic until you notice the database does not care that both aliases "
    "point at the same table — it pairs rows, matches, and preserves exactly as before. What "
    "makes it feel strange is that you have to hold two roles in your head at once: the same "
    "table is playing 'employee' on one side and 'manager' on the other, and the aliases are "
    "the only thing keeping them apart. Reach for it whenever a row's meaning depends on "
    "another row of the same table: an employee and their manager, a customer and who referred "
    "them, a reading and the previous reading, two rows that duplicate each other.",
    """
Two aliases, one table. The aliases are not optional — they are the whole trick.

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

Read the `ON` as a sentence: *the manager row's `id` equals this employee row's
`manager_id`*.

| pattern                   | shape                                        |
|---------------------------|----------------------------------------------|
| row → its parent          | `LEFT JOIN t p ON p.id = t.parent_id`        |
| row → its children        | `LEFT JOIN t c ON c.parent_id = t.id`        |
| find duplicate pairs      | `JOIN t b ON b.key = a.key AND b.id > a.id`  |
| compare two rows in a group | `JOIN t b ON b.grp = a.grp AND b.x > a.x`  |

`LEFT` vs `INNER` matters as much as ever: an inner self join on `manager_id`
drops the CEO, whose manager is NULL.
""",
    """
### Two roles, one table

`employees` holds a `manager_id` that points back into `employees`. To show a
person next to their manager you need the table twice — once playing *employee*,
once playing *manager*:

```sql
SELECT e.name AS employee, e.title, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY e.name;
```

| employee | title           | manager |
|----------|-----------------|---------|
| Ana      | Support Lead    | Rita    |
| Bo       | Support Agent   | Ana     |
| Cai      | Support Agent   | Ana     |
| ...      | ...             | ...     |
| Rita     | CEO             | *NULL*  |

`Rita` has `manager_id IS NULL`, so nothing matched her — and `LEFT JOIN`
preserved her with a NULL manager. Change it to `JOIN` and the CEO disappears
from the org chart, which is a memorable way to get a report wrong.

There is no special syntax here. The database sees two row sources that happen to
read the same storage. Everything from Chapter 1 applies unchanged.

### The direction is a choice

Flip the `ON` and you get the opposite report — managers with their reports:

```sql
SELECT m.name AS manager, e.name AS reports_to_them
FROM employees m
LEFT JOIN employees e ON e.manager_id = m.id
ORDER BY m.name, e.name;
```

Now the preserved side is the manager, so people who manage nobody appear once
with `NULL`. Same table, same key, opposite question. Naming the aliases after
the *roles* (`e`/`m`, `child`/`parent`, `curr`/`prev`) rather than after the table
is what keeps this straight.

### Finding duplicates and pairs

Pair every row with every *other* row in its group, and use an inequality to stop
each pair appearing twice:

```sql
-- Employees who share a salary
SELECT a.name AS employee_a, b.name AS employee_b, a.salary
FROM employees a
JOIN employees b ON b.salary = a.salary AND b.id > a.id
ORDER BY a.salary DESC, employee_a;
```

`b.id > a.id` is doing two jobs at once. Without it you would get `(Ugo, Ugo)` —
every row matches itself — and both `(Ugo, Vera)` and `(Vera, Ugo)`. With it, each
unordered pair appears exactly once, in a predictable order. `b.id <> a.id` fixes
only the first problem.

This is the standard duplicate-detector: join on the columns that should be
unique, add `b.id > a.id`, and every row that comes back is a genuine collision.

### Chains and multi-level hops

Two self joins gets you a grandparent:

```sql
SELECT e.name AS employee, m.name AS manager, mm.name AS skip_level
FROM employees e
LEFT JOIN employees m  ON m.id  = e.manager_id
LEFT JOIN employees mm ON mm.id = m.manager_id
ORDER BY e.name;
```

Each hop is one more join, so a fixed depth is fine. An **arbitrary** depth — "the
whole chain up to the CEO, however long it is" — cannot be written this way; that
is what a recursive CTE is for, and it gets its own chapter.

### Watch out for

- **Forgetting the aliases.** `FROM employees JOIN employees ON ...` is an error
  in SQLite ("duplicate table name") — which is lucky, because the alternative
  would be a query where no column reference means anything.
- **Self-matching.** Any `ON` that a row satisfies against itself will pair it
  with itself. Add `b.id <> a.id`, or `b.id > a.id` if you also want to
  de-duplicate the pairs.
- **Inner joining on a nullable self-reference.** Drops the root every time: the
  CEO, the first customer, the record with no predecessor.
- **A self join to find the previous row.** It works
  (`ON b.n = a.n - 1`), but window functions (`LAG`) do it in one pass with no
  join at all. Chapter 12.
""",
    [
        q("Why must a self join alias both copies of the table?",
          ["Otherwise no column reference can say which copy it means",
           "Because SQLite caches the table by name",
           "To make the query run faster",
           "Aliases are optional in a self join"], 0,
          "Both sides expose the same column names. Without distinct aliases `id` is ambiguous — and SQLite rejects the duplicate table name outright, which is the friendlier outcome."),
        q("`FROM employees e JOIN employees m ON m.id = e.manager_id` — who is missing?",
          ["The CEO, whose manager_id is NULL",
           "Everyone who manages nobody",
           "Nobody — self joins keep every row",
           "The most recently hired employee"], 0,
          "An inner join needs a match. `NULL = anything` is unknown, so the root of the hierarchy is dropped. Use LEFT JOIN to keep them."),
        q("In a duplicate-finding self join, what does `AND b.id > a.id` accomplish?",
          ["It stops a row matching itself and stops each pair appearing twice",
           "It sorts the output",
           "It makes the join an inner join",
           "It ensures b is the newer row"], 0,
          "`>` excludes the self-match (where the ids are equal) and picks exactly one of the two orderings of each pair, so `(Ugo, Vera)` appears once rather than twice."),
        q("You want each manager listed with the people who report to them, including managers with no reports. What is the ON?",
          ["`LEFT JOIN employees e ON e.manager_id = m.id`, with m preserved",
           "`LEFT JOIN employees m ON m.id = e.manager_id`",
           "`JOIN employees e ON e.id = m.manager_id`",
           "`CROSS JOIN employees e`"], 0,
          "The preserved side is whichever role you are reporting on. Here it is the manager, so the manager alias comes first and the ON looks up rows whose manager_id points at them."),
        q("Why can a self join not produce a full reporting chain of unknown depth?",
          ["Each level needs one more join, and the number of levels is not known when you write the query",
           "Self joins may not be nested",
           "The optimiser refuses more than two copies of a table",
           "It can, using CROSS JOIN"], 0,
          "A fixed number of joins gives a fixed depth. Walking a hierarchy of arbitrary depth needs recursion — a `WITH RECURSIVE` CTE."),
        q("What is a better tool than a self join for comparing each row with the previous row?",
          ["A window function such as LAG", "A CROSS JOIN", "A HAVING clause", "A NATURAL JOIN"], 0,
          "`LAG(x) OVER (ORDER BY ...)` reads the previous row in one pass, with no join, no self-match to exclude, and no dependence on the keys being consecutive."),
    ],
    [
        sq("sql_self_join-manager", "Employee and manager",
           "Show every employee next to their manager — including the CEO, who has none. "
           "Fill in the `ON`. Columns: `employee`, `manager`. Order by `employee`.",
           "hr",
           "SELECT e.name AS employee, m.name AS manager\n"
           "FROM employees e\n"
           "LEFT JOIN employees m ON m.id = e.manager_id\n"
           "ORDER BY e.name;",
           ["m.id = e.manager_id"],
           variants=("UPDATE employees SET manager_id = 2 WHERE name = 'Ana';",),
           hint="The manager row's id equals this employee row's manager_id."),
        sq("sql_self_join-alias", "Name the second copy",
           "Same report, but the second copy of the table has lost its alias. Fill in the whole "
           "`LEFT JOIN` line, aliasing the manager copy as `m`. Columns: `employee`, `manager_title`. "
           "Order by `employee`.",
           "hr",
           "SELECT e.name AS employee, m.title AS manager_title\n"
           "FROM employees e\n"
           "LEFT JOIN employees m ON m.id = e.manager_id\n"
           "ORDER BY e.name;",
           ["LEFT JOIN employees m ON m.id = e.manager_id"],
           hint="`LEFT JOIN employees <alias> ON <alias>.id = e.manager_id`."),
        sq("sql_self_join-reports", "Flip the direction",
           "Now report on managers instead: every employee, with how many people report to them "
           "(0 for most). Fill in the `ON`. Columns: `manager`, `direct_reports`. "
           "Order by `direct_reports` descending, then `manager`.",
           "hr",
           "SELECT m.name AS manager, COUNT(e.id) AS direct_reports\n"
           "FROM employees m\n"
           "LEFT JOIN employees e ON e.manager_id = m.id\n"
           "GROUP BY m.id, m.name\n"
           "ORDER BY direct_reports DESC, manager;",
           ["e.manager_id = m.id"],
           variants=("UPDATE employees SET manager_id = 1 WHERE dept_id = 3;",),
           hint="The preserved side is the manager, so look for rows whose manager_id points at them."),
        sq("sql_self_join-dupes", "Find the salary twins",
           "Find every pair of employees on the same salary, without pairing anyone with themselves "
           "and without listing each pair twice. Fill in the extra condition. "
           "Columns: `employee_a`, `employee_b`, `salary`. Order by `salary` desc, then `employee_a`.",
           "hr",
           "SELECT a.name AS employee_a, b.name AS employee_b, a.salary\n"
           "FROM employees a\n"
           "JOIN employees b ON b.salary = a.salary AND b.id > a.id\n"
           "ORDER BY a.salary DESC, employee_a;",
           ["AND b.id > a.id"],
           variants=("UPDATE employees SET salary = 96000 WHERE name = 'Wren';",),
           hint="A strict inequality on the ids does both jobs at once."),
        sq("sql_self_join-referrer", "Who referred whom",
           "In the shop, `customers.referred_by` points at another customer. Show every customer "
           "alongside the person who referred them (NULL when nobody did). Fill in the join line. "
           "Columns: `customer`, `referrer`. Order by `customer`.",
           "shop",
           "SELECT c.name AS customer, r.name AS referrer\n"
           "FROM customers c\n"
           "LEFT JOIN customers r ON r.id = c.referred_by\n"
           "ORDER BY c.name;",
           ["LEFT JOIN customers r ON r.id = c.referred_by"],
           variants=("UPDATE customers SET referred_by = 5 WHERE name = 'Hugo';",),
           hint="Same table again, aliased `r` for referrer, matched on its id."),
        sq("sql_self_join-skip", "Two hops up",
           "Show every employee with their manager and their manager's manager. Fill in the second "
           "self join. Columns: `employee`, `manager`, `skip_level`. Order by `employee`.",
           "hr",
           "SELECT e.name AS employee, m.name AS manager, mm.name AS skip_level\n"
           "FROM employees e\n"
           "LEFT JOIN employees m  ON m.id  = e.manager_id\n"
           "LEFT JOIN employees mm ON mm.id = m.manager_id\n"
           "ORDER BY e.name;",
           ["LEFT JOIN employees mm ON mm.id = m.manager_id"],
           hint="Third alias, joined to the *manager* copy rather than the employee copy."),

        chal("sql_self_join-paidmore", "Paid more than the boss",
             "Find every employee who earns strictly more than their own manager. "
             "Show `employee`, `employee_salary`, `manager`, `manager_salary`. "
             "Order by `employee_salary` descending, then `employee`.",
             "hr",
             "SELECT e.name AS employee, e.salary AS employee_salary,\n"
             "       m.name AS manager, m.salary AS manager_salary\n"
             "FROM employees e\n"
             "JOIN employees m ON m.id = e.manager_id\n"
             "WHERE e.salary > m.salary\n"
             "ORDER BY employee_salary DESC, employee;",
             variants=("UPDATE employees SET salary = 50000 WHERE name = 'Toma';",
                       "UPDATE employees SET salary = 200000 WHERE name = 'Ugo';"),
             hint="Inner join is right — someone with no manager cannot out-earn them. Then compare the two salary columns in WHERE.",
             difficulty="Medium"),
        chal("sql_self_join-samecity", "Referrals that stayed local",
             "Find every customer who was referred by someone **in the same city**. Show `customer`, "
             "`referrer` and `city`. Order by `city`, then `customer`.",
             "shop",
             "SELECT c.name AS customer, r.name AS referrer, c.city\n"
             "FROM customers c\n"
             "JOIN customers r ON r.id = c.referred_by AND r.city = c.city\n"
             "ORDER BY c.city, c.name;",
             variants=("UPDATE customers SET city = 'Lisbon' WHERE name = 'Brahim';",),
             hint="Both conditions can live in the same ON. A customer with no referrer, or with a NULL city, will not match — which is correct.",
             difficulty="Medium"),
        chal("sql_self_join-teamsize", "Managers and their team's payroll",
             "For every employee who manages at least one person, show `manager`, `direct_reports` and "
             "`team_salary` — the total salary of their direct reports (not including their own). "
             "Order by `team_salary` descending, then `manager` ascending.",
             "hr",
             "SELECT m.name AS manager, COUNT(e.id) AS direct_reports, SUM(e.salary) AS team_salary\n"
             "FROM employees m\n"
             "JOIN employees e ON e.manager_id = m.id\n"
             "GROUP BY m.id, m.name\n"
             "ORDER BY team_salary DESC, manager;",
             variants=("UPDATE employees SET manager_id = 3 WHERE name = 'Wren';",),
             hint="'At least one' makes it an inner join — managers with no reports drop out on their own, so no HAVING is needed.",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 7. Non-equi joins
# ===========================================================================

concept(
    "sql_non_equi_join",
    "SQL: Join Foundations",
    "Non-Equi & Range Joins",
    "Join on `BETWEEN`, `<`, or overlap tests when the two tables share no key at all.",
    "The habit of writing ON a.id = b.a_id every single time hardens into a belief that joins "
    "need a foreign key. They do not. ON takes any boolean expression, so two tables with "
    "nothing in common can still be joined by a rule: a salary falls inside a band, a "
    "transaction date falls inside a rate period, two bookings overlap in time. These are "
    "range or non-equi joins, and they are the natural answer to a whole class of problems "
    "that otherwise get solved with a wall of nested CASE expressions. The price is that a "
    "range has no hash key, so the engine has more work to do — which makes understanding "
    "the cost part of using them well.",
    """
```sql
-- A lookup table with no key in common at all
SELECT e.name, b.band
FROM employees e
JOIN salary_bands b ON e.salary BETWEEN b.min_salary AND b.max_salary;
```

`BETWEEN x AND y` is shorthand for `>= x AND <= y`, **inclusive at both ends**.

| pattern                | condition                                              |
|------------------------|--------------------------------------------------------|
| value falls in a bucket| `ON v BETWEEN b.lo AND b.hi`                           |
| point in a time period | `ON t.at >= p.start AND t.at < p.end`                  |
| two periods overlap    | `ON a.start < b.end AND b.start < a.end`               |
| running comparison     | `ON b.date <= a.date` (then aggregate)                 |
| nearest earlier row    | `ON b.at < a.at` + pick the max                        |

An inner range join still drops non-matches: a salary outside every band is gone.
Cover your ranges, or use `LEFT JOIN` and see the gap.
""",
    """
### Banding without a key

`employees` and `salary_bands` share no column. What relates them is a *rule*:

```sql
SELECT e.name AS employee, e.salary, b.band
FROM employees e
JOIN salary_bands b ON e.salary BETWEEN b.min_salary AND b.max_salary
ORDER BY e.salary DESC, employee;
```

| employee | salary | band   |
|----------|--------|--------|
| Rita     | 210000 | Exec   |
| Sami     | 175000 | Exec   |
| Ugo      | 142000 | Senior |
| Wren     |  98000 | Mid    |
| Cai      |  59000 | Junior |

Mechanically nothing new is happening: pair every employee with every band (13 × 4
= 52 pairings), keep the ones where the condition is true. Because the bands do
not overlap, exactly one survives per employee — which is a property of *your
data*, not of the join.

**Overlapping bands would silently duplicate every employee.** That is the first
thing to check when a range join returns more rows than you expected. The second
is gaps: an employee on 75000.5 falls between `Junior` (ends 75000) and `Mid`
(starts 75001) and would vanish from an inner join entirely.

Compare that to writing it out by hand:

```sql
CASE WHEN salary <= 75000 THEN 'Junior'
     WHEN salary <= 110000 THEN 'Mid'
     WHEN salary <= 160000 THEN 'Senior'
     ELSE 'Exec' END
```

It works, but the thresholds are now buried in the query. In the table version,
changing a band is an `UPDATE`, not a code deploy — and every query that bands
salaries agrees automatically.

### Half-open ranges for time

For dates and timestamps, prefer `>= start AND < end` over `BETWEEN`:

```sql
JOIN rate_periods r ON t.happened_at >= r.starts_at AND t.happened_at < r.ends_at
```

`BETWEEN '2024-01-01' AND '2024-01-31'` silently excludes everything that
happened on the 31st after midnight, because `'2024-01-31 14:00:00'` sorts after
`'2024-01-31'`. Half-open intervals have no such edge: consecutive periods tile
the timeline exactly, with no gap and no double-count.

### Overlap — the condition worth memorising

Two intervals overlap **iff each starts before the other ends**:

```sql
ON a.start_at < b.end_at AND b.start_at < a.end_at
```

That is the whole test. It is far easier to get right than enumerating the four
or five ways two intervals can be positioned, and it generalises to "did these
two bookings clash", "was this session live during that incident", "do these two
employment periods overlap".

### Self joins with an inequality: running totals the hard way

Join a table to itself on `<=` and every row is paired with every earlier row:

```sql
SELECT a.id AS order_id, a.order_date, COUNT(b.id) AS orders_so_far
FROM orders a
JOIN orders b ON b.order_date <= a.order_date
GROUP BY a.id, a.order_date
ORDER BY a.order_date, a.id;
```

This is the classic pre-window-function running total, and it is worth writing
once so you feel the cost: it is **quadratic**, because every row is paired with
every earlier row. On 10,000 rows that is 50 million pairings. `SUM(...) OVER
(ORDER BY ...)` does the same job in one pass — Chapter 12.

### Why range joins are slower

An equality join can hash: build a lookup of the right side keyed by the join
column, then probe it once per left row. A range condition has no such key —
there is no hash of "is between". The engine falls back to scanning the right
side, or to a B-tree range scan if an index on the range column exists. Keep the
right-hand table small (a bands table has four rows), and index the column being
ranged over when it is large.

### Watch out for

- **Overlapping ranges silently duplicate rows.** Check
  `COUNT(*)` before and after.
- **Gaps in the ranges silently drop rows.** Use `LEFT JOIN` while developing so
  gaps show up as NULLs rather than as absences.
- **`BETWEEN` is inclusive**, which is nearly always wrong for timestamps.
- **`BETWEEN hi AND lo` returns nothing.** It does not reorder the bounds and it
  does not warn you.
- **Quadratic self joins.** Fine on hundreds of rows, fatal on millions.
""",
    [
        q("`BETWEEN 10 AND 20` is equivalent to which condition?",
          ["`>= 10 AND <= 20` — inclusive at both ends",
           "`> 10 AND < 20`", "`>= 10 AND < 20`", "`> 10 AND <= 20`"], 0,
          "BETWEEN is inclusive on both sides. That is fine for integer bands and usually wrong for timestamps, where you want a half-open `>= start AND < end`."),
        q("A range join returns more rows than the left table has. What is the most likely cause?",
          ["The ranges overlap, so some rows match more than one",
           "The join should have been a LEFT JOIN",
           "There is a gap between the ranges",
           "BETWEEN was written backwards"], 0,
          "Nothing forces the ranges to be disjoint. If two bands both contain 100000, every employee on 100000 comes back twice. Overlaps duplicate; gaps drop."),
        q("Why prefer `>= start AND < end` over `BETWEEN start AND end` for timestamps?",
          ["BETWEEN includes the end instant, so consecutive periods overlap and times later on the end date are lost",
           "BETWEEN is slower on dates",
           "BETWEEN does not work on TEXT dates",
           "There is no difference"], 0,
          "`BETWEEN '2024-01-01' AND '2024-01-31'` excludes everything after midnight on the 31st, and adjacent BETWEEN periods both contain the shared boundary. Half-open intervals tile the timeline exactly."),
        q("Which condition tests that two intervals overlap?",
          ["`a.start < b.end AND b.start < a.end`",
           "`a.start < b.start AND a.end < b.end`",
           "`a.start BETWEEN b.start AND b.end`",
           "`a.start = b.start OR a.end = b.end`"], 0,
          "Each interval must begin before the other ends. It is one line and it covers every arrangement, including full containment in either direction."),
        q("Why is a range join usually slower than an equality join?",
          ["A range has no hash key, so the engine cannot build a hash lookup and must scan or range-scan",
           "Ranges force a full table lock",
           "BETWEEN is implemented as two separate joins",
           "It is not — range joins are faster"], 0,
          "Hash joins need equality. With a range the engine scans the right side per left row, or uses a B-tree index to narrow it. Keeping the ranged table small, or indexing the ranged column, is what makes it acceptable."),
        q("`JOIN orders b ON b.order_date <= a.order_date` then `GROUP BY a.id` — what is the complexity?",
          ["Quadratic: every row is paired with every earlier row",
           "Linear: each row matches once",
           "Logarithmic, because dates are indexed",
           "Constant"], 0,
          "n rows produce roughly n²/2 pairings. It is the classic pre-window running total; `SUM(...) OVER (ORDER BY ...)` computes the same answer in a single pass."),
    ],
    [
        sq("sql_non_equi_join-band", "Band by salary",
           "Put every employee in their salary band. Fill in the `ON` condition — there is no shared key, "
           "so it has to be a range test. Columns: `employee`, `salary`, `band`. "
           "Order by `salary` descending, then `employee`.",
           "hr",
           "SELECT e.name AS employee, e.salary, b.band\n"
           "FROM employees e\n"
           "JOIN salary_bands b ON e.salary BETWEEN b.min_salary AND b.max_salary\n"
           "ORDER BY e.salary DESC, employee;",
           ["e.salary BETWEEN b.min_salary AND b.max_salary"],
           variants=("UPDATE salary_bands SET max_salary = 90000 WHERE band = 'Junior'; UPDATE salary_bands SET min_salary = 90001 WHERE band = 'Mid';",),
           hint="BETWEEN the band's lower and upper bound. Both bounds are inclusive."),
        sq("sql_non_equi_join-explicit", "The same test without BETWEEN",
           "Rewrite the band join using two explicit comparisons instead of `BETWEEN`, so the inclusivity "
           "is visible. Fill in the condition. Columns: `employee`, `band`. Order by `employee`.",
           "hr",
           "SELECT e.name AS employee, b.band\n"
           "FROM employees e\n"
           "JOIN salary_bands b ON e.salary >= b.min_salary AND e.salary <= b.max_salary\n"
           "ORDER BY e.name;",
           ["e.salary >= b.min_salary AND e.salary <= b.max_salary"],
           hint="Two comparisons joined by AND — greater-or-equal the floor, less-or-equal the ceiling."),
        sq("sql_non_equi_join-count", "How many per band",
           "Count the employees in each band, keeping bands that contain nobody. Fill in the join type. "
           "Columns: `band`, `headcount`. Order by `headcount` descending, then `band`.",
           "hr",
           "SELECT b.band, COUNT(e.id) AS headcount\n"
           "FROM salary_bands b\n"
           "LEFT JOIN employees e ON e.salary BETWEEN b.min_salary AND b.max_salary\n"
           "GROUP BY b.band\n"
           "ORDER BY headcount DESC, b.band;",
           ["LEFT JOIN"],
           variants=("UPDATE employees SET salary = 40000 WHERE dept_id = 3;",),
           hint="Bands are the subject and every one must appear, so the join is outer — and COUNT a column from the employees side."),
        sq("sql_non_equi_join-halfopen", "Half-open, for dates",
           "Count the shop's orders per calendar quarter of 2023 using half-open date ranges. "
           "Fill in the condition that puts an order in a quarter. Columns: `quarter`, `orders`. "
           "Order by `quarter`.",
           "shop",
           "WITH quarters(quarter, starts_at, ends_at) AS (\n"
           "  VALUES ('Q1','2023-01-01','2023-04-01'),\n"
           "         ('Q2','2023-04-01','2023-07-01'),\n"
           "         ('Q3','2023-07-01','2023-10-01'),\n"
           "         ('Q4','2023-10-01','2024-01-01')\n"
           ")\n"
           "SELECT q.quarter, COUNT(o.id) AS orders\n"
           "FROM quarters q\n"
           "LEFT JOIN orders o ON o.order_date >= q.starts_at AND o.order_date < q.ends_at\n"
           "GROUP BY q.quarter\n"
           "ORDER BY q.quarter;",
           ["o.order_date >= q.starts_at AND o.order_date < q.ends_at"],
           variants=("UPDATE orders SET order_date = '2023-01-05' WHERE id IN (111, 112);",),
           hint="Greater-or-equal the start, strictly less than the end — so no order lands in two quarters."),
        sq("sql_non_equi_join-overlap", "Do these sessions overlap?",
           "Find every pair of sessions by *different* users that were live at the same time. "
           "Fill in the overlap test. Columns: `a_id`, `b_id`. Order by `a_id`, then `b_id`.",
           "events",
           "SELECT a.id AS a_id, b.id AS b_id\n"
           "FROM sessions a\n"
           "JOIN sessions b\n"
           "  ON a.user_id < b.user_id\n"
           " AND a.started_at < b.ended_at AND b.started_at < a.ended_at\n"
           "ORDER BY a.id, b.id;",
           ["a.started_at < b.ended_at AND b.started_at < a.ended_at"],
           variants=("UPDATE sessions SET started_at = '2024-03-02 08:50:00', ended_at = '2024-03-02 09:10:00' WHERE id = 6;",),
           hint="Each interval starts before the other one ends. Two comparisons, ANDed."),
        sq("sql_non_equi_join-running", "A running count the slow way",
           "For each order, count how many orders were placed on or before its date (the pre-window-function "
           "running total). Fill in the inequality. Columns: `order_id`, `order_date`, `orders_so_far`. "
           "Order by `order_date`, then `order_id`.",
           "shop",
           "SELECT a.id AS order_id, a.order_date, COUNT(b.id) AS orders_so_far\n"
           "FROM orders a\n"
           "JOIN orders b ON b.order_date <= a.order_date\n"
           "GROUP BY a.id, a.order_date\n"
           "ORDER BY a.order_date, a.id;",
           ["b.order_date <= a.order_date"],
           hint="Pair each order with every order dated on or before it, then count the partners."),

        chal("sql_non_equi_join-bandpay", "Payroll by band",
             "For every salary band — including any that is empty — show `band`, `headcount` and "
             "`total_salary` (0 when the band is empty). Order by `total_salary` descending, then `band`.",
             "hr",
             "SELECT b.band, COUNT(e.id) AS headcount, COALESCE(SUM(e.salary), 0) AS total_salary\n"
             "FROM salary_bands b\n"
             "LEFT JOIN employees e ON e.salary BETWEEN b.min_salary AND b.max_salary\n"
             "GROUP BY b.band\n"
             "ORDER BY total_salary DESC, b.band;",
             variants=("UPDATE employees SET salary = 300000 WHERE name = 'Rita';",),
             hint="Bands lead, LEFT JOIN the employees onto them by range, then COALESCE the SUM so an empty band shows 0 rather than NULL.",
             difficulty="Medium"),
        chal("sql_non_equi_join-gap", "Find the uncovered salaries",
             "Prove the bands cover everybody: list every employee whose salary falls in **no** band, "
             "showing `employee` and `salary`. With the shipped data the answer is nobody — but the "
             "hidden cases move the boundaries, and your query has to catch it. "
             "Order by `salary` descending, then `employee`.",
             "hr",
             "SELECT e.name AS employee, e.salary\n"
             "FROM employees e\n"
             "LEFT JOIN salary_bands b ON e.salary BETWEEN b.min_salary AND b.max_salary\n"
             "WHERE b.band IS NULL\n"
             "ORDER BY e.salary DESC, employee;",
             variants=("UPDATE salary_bands SET max_salary = 130000 WHERE band = 'Senior'; UPDATE salary_bands SET min_salary = 150000 WHERE band = 'Exec';",
                       "DELETE FROM salary_bands WHERE band = 'Mid';"),
             hint="An anti-join, but on a range instead of a key: LEFT JOIN the bands, then keep the rows where no band matched.",
             difficulty="Medium",
             allow_empty=True),
        chal("sql_non_equi_join-clash", "Overlapping sessions on the same day",
             "Find every pair of sessions belonging to **different users** that overlapped in time. Show "
             "`user_a`, `user_b` (the users' emails), `a_id` and `b_id`, with the lower user id always "
             "in the `a` position. Ignore sessions that have not ended. "
             "Order by `a_id`, then `b_id`.",
             "events",
             "SELECT ua.email AS user_a, ub.email AS user_b, a.id AS a_id, b.id AS b_id\n"
             "FROM sessions a\n"
             "JOIN sessions b ON a.user_id < b.user_id\n"
             "              AND a.started_at < b.ended_at AND b.started_at < a.ended_at\n"
             "JOIN users ua ON ua.id = a.user_id\n"
             "JOIN users ub ON ub.id = b.user_id\n"
             "WHERE a.ended_at IS NOT NULL AND b.ended_at IS NOT NULL\n"
             "ORDER BY a.id, b.id;",
             variants=("UPDATE sessions SET started_at = '2024-03-01 09:05:00', ended_at = '2024-03-01 09:20:00' WHERE id = 6;",),
             hint="Three ideas at once: the self join with `<` on user_id to avoid mirrored pairs, the overlap test, and two more joins to fetch the emails.",
             difficulty="Medium"),
    ],
)


# ===========================================================================
# 8. Many tables at once
# ===========================================================================

concept(
    "sql_multi_join",
    "SQL: Join Foundations",
    "Many Tables at Once",
    "Five-table queries, the fan-out that inflates your totals, and how to keep it all readable.",
    "Joining two tables is a mechanism; joining five is a discipline. Each join is applied to "
    "the result of everything above it, so the query is a pipeline where the row count changes "
    "at every step — and once a one-to-many join has fanned the rows out, every column from "
    "above it is repeated. Sum such a column and you get a number that is confidently, "
    "silently too large. The remedy is not cleverness but structure: know your grain, aggregate "
    "before you join when two independent one-to-many branches meet, and name your aliases so "
    "the query can still be read a month later.",
    """
Each join is applied to **the result so far**, not to the original table:

```
orders                       13 rows
  JOIN customers             13 rows   (many-to-one: no change)
  JOIN order_items           20 rows   (one-to-many: FAN-OUT)
  JOIN products              20 rows   (many-to-one: no change)
```

**Grain** = what one row means. It starts as "one order" and becomes "one order
line". Every order-level column is now repeated once per line.

| join direction | effect on row count |
|----------------|---------------------|
| many-to-one (FK → PK)   | unchanged (or smaller if inner and unmatched) |
| one-to-many (PK → FK)   | **multiplied** |
| one-to-one              | unchanged |

The rule that saves you: **`SUM` a column only at the grain it belongs to.** If
you fanned out, aggregate the fanned side first, then join one row to one row.
""",
    """
### Reading a five-table query

```sql
SELECT c.name AS customer, cat.name AS category, p.name AS product, i.quantity
FROM orders o
JOIN customers   c   ON c.id  = o.customer_id
JOIN order_items i   ON i.order_id = o.id
JOIN products    p   ON p.id  = i.product_id
JOIN categories  cat ON cat.id = p.category_id
WHERE o.status = 'shipped'
ORDER BY c.name, p.name;
```

Read top to bottom as a pipeline. Start at `orders`. Attach the customer (one
each — row count unchanged). Attach the lines (several each — **row count
multiplied**). Attach each line's product, then that product's category (one each
— unchanged).

The row count only ever changes at a one-to-many step. Learning to spot those at
a glance — *is the join column unique on the far side?* — is the whole skill.

### The fan-out bug, in full

Suppose orders carried a `shipping_fee`. This looks obviously right and is wrong:

```sql
SELECT c.name, SUM(o.shipping_fee) AS fees, SUM(i.quantity * i.unit_price) AS goods
FROM customers c
JOIN orders      o ON o.customer_id = c.id
JOIN order_items i ON i.order_id = o.id
GROUP BY c.id, c.name;
```

After the `order_items` join, an order with three lines is three rows — and
`o.shipping_fee` appears in all three. `SUM` adds it three times. `goods` is
correct (it is at line grain, which is where those columns live); `fees` is
inflated by the number of lines.

Two fixes, both worth knowing:

```sql
-- 1. Aggregate the fanned side first, then join one row to one row.
SELECT c.name AS customer, SUM(o.shipping_fee) AS fees, SUM(x.goods) AS goods
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN (SELECT order_id, SUM(quantity * unit_price) AS goods
      FROM order_items GROUP BY order_id) x ON x.order_id = o.id
GROUP BY c.id, c.name;

-- 2. Or de-duplicate the repeated value.
SUM(DISTINCT o.shipping_fee)   -- WRONG: two orders with the same fee collapse to one
```

Fix 1 is the real one. `DISTINCT` inside an aggregate is a trap: it de-duplicates
*values*, not *rows*, so two orders that happen to have the same fee become one.

### Two independent one-to-many branches multiply each other

The nastiest version. Say orders also had `order_notes`:

```
orders JOIN order_items   -- order 101 -> 2 rows
       JOIN order_notes   -- order 101 -> 3 notes
                          -- result: 2 x 3 = 6 rows for order 101
```

Neither join is wrong on its own; together they produce a partial cross product,
and *both* sums are now inflated. Whenever two independent one-to-many branches
hang off the same parent, aggregate each branch separately before joining:

```sql
FROM orders o
LEFT JOIN (SELECT order_id, SUM(quantity) AS units  FROM order_items GROUP BY order_id) it ON it.order_id = o.id
LEFT JOIN (SELECT order_id, COUNT(*)      AS notes  FROM order_notes GROUP BY order_id) nt ON nt.order_id = o.id
```

Now each subquery contributes exactly one row per order, and nothing multiplies.

### Join order: readability versus execution

You write joins in an order; the optimiser executes them in whatever order it
thinks is cheapest. `EXPLAIN QUERY PLAN` shows what it actually chose.

So write for the reader:

1. **Start with the subject** — the table whose grain the answer has.
2. **Follow the relationships outward,** one hop at a time. Never join a table
   before the table it depends on.
3. **Group outer joins together at the bottom** when you can, so the "everything
   from here down is optional" boundary is visible.
4. **Alias by meaning:** `o`, `oi`, `c`, `p`, `cat`. Single letters are fine
   until two tables start with the same one; then use `cust` and `cat`.

### `WHERE` on an inner-joined table is free; on an outer-joined one it is not

Mixed queries are where this bites. In the five-table query above, `WHERE
o.status = 'shipped'` is fine — every join is inner. Change any of them to `LEFT`
and that same `WHERE`, if it touches the optional table, demotes it. When a query
mixes join types, check every `WHERE` predicate against the join type of the
table it mentions.

### Watch out for

- **Missing `ON`.** *n* tables need *n − 1* join conditions. Count them.
- **A `SUM` that is a suspiciously round multiple of the truth** — 2×, 3× — is
  almost always fan-out.
- **`COUNT(DISTINCT o.id)` versus `COUNT(*)`** after a fan-out: the first counts
  orders, the second counts lines. Say which one you meant.
- **`SELECT *` in a multi-table query.** Duplicate column names, huge rows, and a
  result that silently changes shape when someone adds a column.
- **An inner join buried among outer ones** collapses everything above it.
""",
    [
        q("What does 'grain' mean for a joined result?",
          ["What a single row represents — one order, or one order line",
           "How many tables are joined",
           "Whether the join is inner or outer",
           "The sort order of the result"], 0,
          "Grain is the unit of a row. It changes the moment a one-to-many join fans the rows out, and that change is what invalidates a SUM of any column from above the join."),
        q("`orders JOIN order_items` then `SUM(orders.shipping_fee)` — what goes wrong?",
          ["Each order's fee is added once per line, inflating the total",
           "The fee becomes NULL",
           "The query returns no rows",
           "Nothing; SUM handles duplicates"], 0,
          "The fan-out repeats every order-level column once per line. The fee is at order grain but the rows are now at line grain, so the sum multiplies."),
        q("Why is `SUM(DISTINCT o.shipping_fee)` a bad fix for that?",
          ["It de-duplicates values, so two different orders with the same fee collapse into one",
           "DISTINCT is not allowed inside SUM",
           "It is slower",
           "It is a good fix"], 0,
          "DISTINCT operates on values, not on rows. Two separate £5 fees are indistinguishable, so the total is now too *small*. Aggregate the fanned side in a subquery instead."),
        q("Two independent one-to-many branches (order_items and order_notes) hang off `orders`. What happens?",
          ["They multiply each other: 2 lines x 3 notes = 6 rows for that order",
           "SQLite rejects the query",
           "Only the first branch fans out",
           "The rows are de-duplicated automatically"], 0,
          "Each branch fans out independently, producing a partial cross product. Aggregate each branch into its own one-row-per-order subquery before joining."),
        q("How many join conditions does a five-table join need?",
          ["Four — n tables need n-1", "Five", "Three", "It depends on the indexes"], 0,
          "Every table after the first needs one condition linking it to what came before. A missing one leaves an accidental cross join that runs fine and returns far too many rows."),
        q("After joining orders to order_items, what does `COUNT(*)` count?",
          ["Order lines, not orders — use COUNT(DISTINCT o.id) for orders",
           "Orders", "Customers", "Products"], 0,
          "Post-fan-out, one row is one line. COUNT(*) counts lines; COUNT(DISTINCT o.id) counts the orders those lines belong to."),
        q("Does the order you write joins in determine the order the database executes them?",
          ["No — the optimiser reorders them; write for readability and check EXPLAIN QUERY PLAN",
           "Yes, always, top to bottom",
           "Yes, but only for inner joins",
           "Only when there are indexes"], 0,
          "The written order is for humans. The planner picks its own order based on statistics and indexes, which you can inspect with EXPLAIN QUERY PLAN."),
    ],
    [
        sq("sql_multi_join-five", "Five tables in a row",
           "Join orders all the way down to categories. Fill in the missing join. "
           "Columns: `customer`, `category`, `product`, `quantity`, for shipped orders only. "
           "Order by `customer`, then `product`.",
           "shop",
           "SELECT c.name AS customer, cat.name AS category, p.name AS product, i.quantity\n"
           "FROM orders o\n"
           "JOIN customers   c   ON c.id = o.customer_id\n"
           "JOIN order_items i   ON i.order_id = o.id\n"
           "JOIN products    p   ON p.id = i.product_id\n"
           "JOIN categories  cat ON cat.id = p.category_id\n"
           "WHERE o.status = 'shipped'\n"
           "ORDER BY c.name, p.name;",
           ["JOIN categories  cat ON cat.id = p.category_id"],
           hint="One more hop: from the product to the category it belongs to."),
        sq("sql_multi_join-grain", "Which count did you mean?",
           "After joining orders to their lines, `COUNT(*)` counts lines. Fill in the expression that "
           "counts **orders** instead. Columns: `customer`, `orders`, `lines`. "
           "Order by `orders` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(DISTINCT o.id) AS orders, COUNT(*) AS lines\n"
           "FROM customers c\n"
           "JOIN orders      o ON o.customer_id = c.id\n"
           "JOIN order_items i ON i.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY orders DESC, customer;",
           ["COUNT(DISTINCT o.id)"],
           variants=("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (21, 113, 1, 1, 79.50);",),
           hint="Count the distinct order id rather than the rows."),
        sq("sql_multi_join-preagg", "Aggregate before you join",
           "Total each customer's spend without letting the line-level fan-out touch the order count. "
           "Fill in the subquery that collapses order lines to one row per order. "
           "Columns: `customer`, `orders`, `spend`. Order by `spend` descending, then `customer`.",
           "shop",
           "SELECT c.name AS customer, COUNT(o.id) AS orders, ROUND(SUM(t.total), 2) AS spend\n"
           "FROM customers c\n"
           "JOIN orders o ON o.customer_id = c.id\n"
           "JOIN (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) t\n"
           "  ON t.order_id = o.id\n"
           "GROUP BY c.id, c.name\n"
           "ORDER BY spend DESC, customer;",
           ["(SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id)"],
           variants=("UPDATE order_items SET quantity = 3 WHERE order_id = 101;",),
           hint="A SELECT over order_items that groups by order_id and sums quantity * unit_price."),
        sq("sql_multi_join-outer", "One outer join among the inner ones",
           "Show every **product** with the category it belongs to and the number of lines it has ever "
           "appeared on — including products never sold. The category join stays inner; fill in the "
           "type for the order-lines join. Columns: `product`, `category`, `times_sold`. "
           "Order by `times_sold` descending, then `product`.",
           "shop",
           "SELECT p.name AS product, cat.name AS category, COUNT(i.id) AS times_sold\n"
           "FROM products p\n"
           "JOIN categories cat ON cat.id = p.category_id\n"
           "LEFT JOIN order_items i ON i.product_id = p.id\n"
           "GROUP BY p.id, p.name, cat.name\n"
           "ORDER BY times_sold DESC, product;",
           ["LEFT JOIN"],
           variants=("DELETE FROM order_items WHERE product_id IN (1, 2);",),
           hint="Products with no lines must survive, so that one join is outer."),
        sq("sql_multi_join-conditions", "Count the ON clauses",
           "Four tables need three join conditions. One is missing, leaving an accidental cross join. "
           "Fill it in. Columns: `order_id`, `customer`, `product`. Order by `order_id`, then `product`.",
           "shop",
           "SELECT o.id AS order_id, c.name AS customer, p.name AS product\n"
           "FROM orders o\n"
           "JOIN customers   c ON c.id = o.customer_id\n"
           "JOIN order_items i ON i.order_id = o.id\n"
           "JOIN products    p ON p.id = i.product_id\n"
           "WHERE o.status = 'pending'\n"
           "ORDER BY o.id, p.name;",
           ["ON p.id = i.product_id"],
           hint="The last table needs to be tied to the line that references it."),
        sq("sql_multi_join-hr", "Three tables, three roles",
           "For every employee show their department, their manager and their salary band — keeping "
           "employees with no department and no manager. Fill in the department join. "
           "Columns: `employee`, `department`, `manager`, `band`. Order by `employee`.",
           "hr",
           "SELECT e.name AS employee, d.name AS department, m.name AS manager, b.band\n"
           "FROM employees e\n"
           "LEFT JOIN departments  d ON d.id = e.dept_id\n"
           "LEFT JOIN employees    m ON m.id = e.manager_id\n"
           "LEFT JOIN salary_bands b ON e.salary BETWEEN b.min_salary AND b.max_salary\n"
           "ORDER BY e.name;",
           ["LEFT JOIN departments  d ON d.id = e.dept_id"],
           hint="Outer, because Dov has no department. Match the department's id to the employee's dept_id."),

        chal("sql_multi_join-topcat", "Each customer's favourite category",
             "For every customer who has bought anything, find how much they spent in each category and "
             "keep only their biggest. Show `customer`, `category` and `spend` (rounded to 2 decimals). "
             "If a customer ties across two categories, show both. "
             "Order by `spend` descending, then `customer`, then `category`.",
             "shop",
             "WITH per_cat AS (\n"
             "  SELECT c.id AS cid, c.name AS customer, cat.name AS category,\n"
             "         ROUND(SUM(i.quantity * i.unit_price), 2) AS spend\n"
             "  FROM customers   c\n"
             "  JOIN orders      o   ON o.customer_id = c.id\n"
             "  JOIN order_items i   ON i.order_id = o.id\n"
             "  JOIN products    p   ON p.id = i.product_id\n"
             "  JOIN categories  cat ON cat.id = p.category_id\n"
             "  GROUP BY c.id, c.name, cat.name\n"
             ")\n"
             "SELECT customer, category, spend\n"
             "FROM per_cat pc\n"
             "WHERE spend = (SELECT MAX(spend) FROM per_cat x WHERE x.cid = pc.cid)\n"
             "ORDER BY spend DESC, customer, category;",
             variants=("UPDATE products SET category_id = 1 WHERE category_id = 3;",),
             hint="Compute spend per customer per category first, then keep the rows whose spend equals that customer's maximum.",
             difficulty="Medium"),
        chal("sql_multi_join-orderdetail", "A full order detail line",
             "Produce the detail lines of every shipped order: `order_id`, `order_date`, `customer`, "
             "`product`, `category`, `quantity`, and `line_total` (`quantity * unit_price`, rounded to 2). "
             "Order by `order_id`, then `product`.",
             "shop",
             "SELECT o.id AS order_id, o.order_date, c.name AS customer, p.name AS product,\n"
             "       cat.name AS category, i.quantity,\n"
             "       ROUND(i.quantity * i.unit_price, 2) AS line_total\n"
             "FROM orders o\n"
             "JOIN customers   c   ON c.id = o.customer_id\n"
             "JOIN order_items i   ON i.order_id = o.id\n"
             "JOIN products    p   ON p.id = i.product_id\n"
             "JOIN categories  cat ON cat.id = p.category_id\n"
             "WHERE o.status = 'shipped'\n"
             "ORDER BY o.id, p.name;",
             variants=("UPDATE orders SET status = 'shipped' WHERE status = 'pending';",),
             hint="Every join here is inner: a line without a product, or a product without a category, would be a data bug rather than a report row.",
             difficulty="Easy"),
        chal("sql_multi_join-nofanout", "Orders, lines and units — without inflating anything",
             "For every customer — including those who have never ordered — show `customer`, "
             "`order_count` (distinct orders, any status), `line_count` (order lines) and `units` "
             "(total quantity, 0 when none). Getting all three right from one join chain is the point. "
             "Order by `order_count` descending, then `customer` ascending.",
             "shop",
             "SELECT c.name AS customer,\n"
             "       COUNT(DISTINCT o.id) AS order_count,\n"
             "       COUNT(i.id) AS line_count,\n"
             "       COALESCE(SUM(i.quantity), 0) AS units\n"
             "FROM customers c\n"
             "LEFT JOIN orders      o ON o.customer_id = c.id\n"
             "LEFT JOIN order_items i ON i.order_id = o.id\n"
             "GROUP BY c.id, c.name\n"
             "ORDER BY order_count DESC, customer;",
             variants=("INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (21, 113, 4, 5, 32.00);",),
             hint="COUNT(DISTINCT o.id) survives the fan-out; COUNT(i.id) counts lines and gives 0 for padded rows; COALESCE turns a NULL SUM into 0.",
             difficulty="Medium"),
    ],
)
