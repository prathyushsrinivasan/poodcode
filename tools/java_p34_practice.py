# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 34 practice - records, sealed types and pattern matching.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[34]`.
#
# Like the module, every program here needs JDK 21. Uses the module's helpers
# (`_j34s`, `_j34t`, `_j34th`, `_rec34`, `_rows34`, `_toks34`, `_PARSE34`,
# `_pobj34`, `_EXPR34`, `_EXPR_PARSE34`, the Python expression mirrors).
# Hash-based collections are only printed through LinkedHash* or Tree*.
# ---------------------------------------------------------------------------

def _p34s(eid, title, difficulty, prompt, body, tests, hints):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _j34s(body), body, tests, hints)


def _p34t(eid, title, difficulty, prompt, types, body, region, tests, hints):
    return _jch(eid, title, difficulty, prompt, _j34t(types, body), region.strip("\n"),
                tests, hints)


def _p34h(eid, title, difficulty, prompt, types, helpers, body, region, tests, hints):
    return _jch(eid, title, difficulty, prompt, _j34th(types, helpers, body),
                region.strip("\n"), tests, hints)


# --- Family A - records ---------------------------------------------------------

_BOOKS34 = ([("Dune", 412), ("Emma", 474)], [("Solo", 1)], [("A", 10), ("B", 20), ("C", 30)],
            [("Ulysses", 730)], [("x", 0), ("y", 5)])

_RECT34 = """
record Rect(int w, int h) {
    int area() {
        return w * h;
    }

    int perimeter() {
        return 2 * (w + h);
    }

    boolean isSquare() {
        return w == h;
    }
}
"""
_RECT_REGION34 = "\n".join(_RECT34.strip("\n").split("\n")[1:-1])
_RECTS34 = ([(3, 4)], [(5, 5), (1, 2)], [(0, 7)], [(10, 10), (2, 8), (6, 6)], [(1, 1)])

_PERCENT34 = """
record Percent(int value) {
    Percent {
        if (value < 0 || value > 100) {
            throw new IllegalArgumentException("out of range: " + value);
        }
    }
}
"""
_PERCENT_REGION34 = "\n".join(_PERCENT34.strip("\n").split("\n")[1:-1])
_PCTS34 = ([50, 101], [0], [-1, 100, 7], [200, -5], [99, 1, 100, 0])

_SPAN34 = """
record Span(int minutes) {
    static Span ofHours(int hours) {
        return new Span(hours * 60);
    }

    Span plus(Span other) {
        return new Span(minutes + other.minutes);
    }

    @Override
    public String toString() {
        return minutes / 60 + "h" + (minutes % 60 < 10 ? "0" : "") + minutes % 60 + "m";
    }
}
"""
_SPAN_REGION34 = "\n".join(_SPAN34.strip("\n").split("\n")[1:-1])
_SPANROWS34 = ([("h", 2), ("m", 5)], [("m", 59)], [("h", 1), ("h", 1), ("m", 90)],
               [("m", 0)], [("m", 45), ("m", 30), ("h", 3)])


def _span34(mins):
    return f"{mins // 60}h{mins % 60:02d}m"


def _span_out34(rows):
    total, out = 0, []
    for (k, v) in rows:
        total += v * 60 if k == "h" else v
        out.append(_span34(total))
    return _nl(*out)


_WITH34 = """
record Point(int x, int y) {
    Point withX(int newX) {
        return new Point(newX, y);
    }

    Point withY(int newY) {
        return new Point(x, newY);
    }
}
"""
_WITH_REGION34 = "\n".join(_WITH34.strip("\n").split("\n")[1:-1])
_MOVES34 = ([("x", 5), ("y", 2)], [("y", -1)], [("x", 1), ("x", 2), ("y", 3)],
            [("y", 0), ("x", 0)], [("x", 9), ("y", 9), ("x", -9)])


def _moves_out34(moves):
    x = y = 0
    out = [_pt34(0, 0)]
    for (k, v) in moves:
        if k == "x":
            x = v
        else:
            y = v
        out.append(_pt34(x, y))
    return _nl(*out)


_P34_A = _jfam(
    "p34-records", "Records",
    "A class that is just its data - plus the methods, rules and factories that belong "
    "to it.",
    """
```java
record Rect(int w, int h) {
    Rect { if (w < 0 || h < 0) throw new IllegalArgumentException(); }   // rules
    static Rect square(int s) { return new Rect(s, s); }                  // factory
    int area() { return w * h; }                                          // behaviour
    Rect withW(int newW) { return new Rect(newW, h); }                    // a "wither"
}
```

Everything a record adds returns a value or a NEW record; nothing changes an
existing one. A "wither" - `withX`, `withW` - is the record's version of a
setter: the same record with one component replaced.
""",
    [
        _p34t("j34-pa-declare", "Declare it", "Intro",
              "Declare `Book` as a record of a `title` and a number of `pages`, so `main` "
              "can print each book and the total page count.",
              "record Book(String title, int pages) {}\n",
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Book b = new Book(sc.next(), sc.nextInt());\n"
              "            System.out.println(b);\n"
              "            total += b.pages();\n"
              "        }\n"
              "        System.out.println(total);",
              "record Book(String title, int pages) {}",
              [_rows34(rows, _nl(*[_rec34("Book", title=t, pages=p) for (t, p) in rows],
                                 sum(p for (_, p) in rows))) for rows in _BOOKS34],
              ["`record Book(String title, int pages) {}`",
               "The accessor is `pages()`, generated from the component name.",
               "A record prints as `Book[title=Dune, pages=412]`."]),

        _p34t("j34-pa-derived", "Derived values", "Easy",
              "Give `Rect` three methods computed from its components: `area()`, "
              "`perimeter()` and `isSquare()`.",
              _RECT34,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Rect r = new Rect(sc.nextInt(), sc.nextInt());\n"
              "            System.out.println(r + \" \" + r.area() + \" \" + r.perimeter() + \" \" + r.isSquare());\n"
              "        }",
              _RECT_REGION34,
              [_rows34(rows, _nl(*[f"{_rec34('Rect', w=w, h=h)} {w * h} {2 * (w + h)} "
                                   f"{_jbool(w == h)}" for (w, h) in rows]))
               for rows in _RECTS34],
              ["Inside a record, the components are fields: `w * h`.",
               "Derived values are methods, not extra fields - a record cannot declare "
               "extra instance fields.",
               "`2 * (w + h)` and `w == h`."]),

        _p34t("j34-pa-validate", "A percentage that must be one", "Medium",
              "Give `Percent` a compact constructor that rejects any value outside 0..100 "
              "with `IllegalArgumentException`. `main` prints the record or `invalid`.",
              _PERCENT34,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int v = sc.nextInt();\n"
              "            try {\n"
              "                System.out.println(new Percent(v));\n"
              "            } catch (IllegalArgumentException e) {\n"
              "                System.out.println(\"invalid\");\n"
              "            }\n"
              "        }",
              _PERCENT_REGION34,
              [_toks34([str(v) for v in vs],
                       _nl(*[(_rec34("Percent", value=v) if 0 <= v <= 100 else "invalid")
                             for v in vs])) for vs in _PCTS34],
              ["`Percent { ... }` - no parameter list.",
               "Throw if `value < 0 || value > 100`.",
               "Because the check is in the constructor, an invalid Percent can never "
               "exist anywhere in the program."]),

        _p34t("j34-pa-span", "A factory and a custom `toString`", "Medium",
              "Give `Span` a static factory `ofHours(h)`, a `plus(other)` returning a new "
              "Span, and a `toString` printing like `2h05m`. `main` keeps a running total "
              "and prints it after each step.",
              _SPAN34,
              "        int n = sc.nextInt();\n"
              "        Span total = new Span(0);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String unit = sc.next();\n"
              "            int amount = sc.nextInt();\n"
              "            Span step = unit.equals(\"h\") ? Span.ofHours(amount) : new Span(amount);\n"
              "            total = total.plus(step);\n"
              "            System.out.println(total);\n"
              "        }",
              _SPAN_REGION34,
              [_rows34(rows, _span_out34(rows)) for rows in _SPANROWS34],
              ["`static Span ofHours(int hours) { return new Span(hours * 60); }`",
               "`plus` returns `new Span(minutes + other.minutes)`.",
               "`toString` must be `public`.",
               "Pad the minutes to two digits: `5` minutes is `05`."]),

        _p34t("j34-pa-withers", "Withers", "Hard",
              "Give `Point` two withers - `withX(newX)` and `withY(newY)` - each returning "
              "a copy with one coordinate replaced. `main` starts at the origin and applies "
              "the moves, printing the point after each.",
              _WITH34,
              "        int n = sc.nextInt();\n"
              "        Point p = new Point(0, 0);\n"
              "        System.out.println(p);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String axis = sc.next();\n"
              "            int v = sc.nextInt();\n"
              "            p = axis.equals(\"x\") ? p.withX(v) : p.withY(v);\n"
              "            System.out.println(p);\n"
              "        }",
              _WITH_REGION34,
              [_rows34(m, _moves_out34(m)) for m in _MOVES34],
              ["A record cannot change, so a 'setter' returns a new record.",
               "`return new Point(newX, y);` keeps the old y.",
               "`main` reassigns `p` - exactly like `date = date.plusDays(1)`."]),
    ],
)


# --- Family B - records in practice ---------------------------------------------

_PAIRSB34 = ([("a", "b"), ("b", "a"), ("a", "b")], [("x", "x")], [("p", "q"), ("p", "q"), ("p", "q")],
             [("m", "n"), ("n", "m"), ("m", "m"), ("n", "n")], [("ada", "bo"), ("cy", "di")])


def _distinct_pairs34(rows):
    seen = []
    for r in rows:
        if r not in seen:
            seen.append(r)
    return _nl(len(seen), "[" + ", ".join(_rec34("Pair", a=a, b=b) for (a, b) in seen) + "]")


_PLAYLIST34 = """
record Playlist(String name, List<String> songs) {
    Playlist {
        songs = List.copyOf(songs);
    }
}
"""
_PLAYLISTS34 = (("road", ["a", "b"]), ("gym", ["x"]), ("calm", ["p", "q", "r"]),
                ("empty", []), ("mix", ["one", "two"]))

_KEY34 = """
record Key(String city, int year) implements Comparable<Key> {
    private static final Comparator<Key> ORDER =
            Comparator.comparing(Key::city).thenComparingInt(Key::year);

    @Override
    public int compareTo(Key other) {
        return ORDER.compare(this, other);
    }
}
"""
_KEY_REGION34 = "\n".join(_KEY34.strip("\n").split("\n")[1:-1])
_SALES34 = ([("oslo", 2024), ("lima", 2023), ("oslo", 2024)], [("rome", 2020)],
            [("b", 2), ("a", 3), ("a", 1), ("b", 2), ("a", 3)],
            [("x", 2000), ("x", 1999)], [("paris", 2024), ("paris", 2023), ("berlin", 2024)])


def _sales_out34(rows):
    counts = {}
    for r in rows:
        counts[r] = counts.get(r, 0) + 1
    return "{" + ", ".join(f"{_rec34('Key', city=c, year=y)}={counts[(c, y)]}"
                           for (c, y) in sorted(counts)) + "}"


_EMP34 = "record Employee(String name, String dept, int salary) {}\n"
_EMPS34 = ([("ada", "eng", 120), ("bo", "ops", 90), ("cy", "eng", 150)],
           [("solo", "hr", 70)],
           [("a", "x", 10), ("b", "x", 10), ("c", "w", 5)],
           [("z", "eng", 100), ("y", "eng", 100), ("x", "eng", 200)],
           [("p", "b", 1), ("q", "a", 2), ("r", "b", 3), ("s", "a", 4)])


def _emp_sorted34(rows):
    ordered = sorted(rows, key=lambda r: (r[1], -r[2], r[0]))
    return _nl(*[_rec34("Employee", name=n, dept=d, salary=s) for (n, d, s) in ordered])


def _emp_group34(rows):
    tot = {}
    for (_n, d, s) in rows:
        tot[d] = tot.get(d, 0) + s
    return "{" + ", ".join(f"{d}={tot[d]}" for d in sorted(tot)) + "}"


_P34_B = _jfam(
    "p34-immutable", "Records in practice",
    "Keys, snapshots, sorting by accessor, and grouping with streams.",
    """
Records slot into everything the collections and streams modules taught, because
their accessors are ordinary methods:

```java
list.sort(Comparator.comparing(Employee::dept)
        .thenComparing(Employee::salary, Comparator.reverseOrder()));

Map<String, Integer> byDept = staff.stream()
        .collect(Collectors.groupingBy(Employee::dept, TreeMap::new,
                 Collectors.summingInt(Employee::salary)));
```

And as keys they bring value-based `equals` and `hashCode` for free. For a
**sorted** map, a record key also needs an order - implement `Comparable`,
usually with a comparator built once in a `static final` field.
""",
    [
        _p34t("j34-pb-distinct", "Distinct pairs, in first-seen order", "Intro",
              "Collect `Pair` records into a `LinkedHashSet` and print how many distinct "
              "pairs there were, then the set.",
              "record Pair(String a, String b) {}\n",
              "        int n = sc.nextInt();\n"
              "        Set<Pair> pairs = new LinkedHashSet<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            pairs.add(new Pair(sc.next(), sc.next()));\n"
              "        }\n"
              "        System.out.println(pairs.size());\n"
              "        System.out.println(pairs);",
              "        Set<Pair> pairs = new LinkedHashSet<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            pairs.add(new Pair(sc.next(), sc.next()));\n"
              "        }\n"
              "        System.out.println(pairs.size());\n"
              "        System.out.println(pairs);",
              [_rows34(rows, _distinct_pairs34(rows)) for rows in _PAIRSB34],
              ["Equal components mean equal records, so duplicates collapse.",
               "`(a, b)` and `(b, a)` are different pairs - order of components matters.",
               "`LinkedHashSet` keeps first-insertion order."]),

        _p34t("j34-pb-copy", "A snapshot that cannot be changed", "Easy",
              "Give `Playlist` a compact constructor that stores an unmodifiable copy of "
              "its songs. `main` then shows the caller's changes do not reach it, and that "
              "adding through `songs()` is refused.",
              _PLAYLIST34,
              "        String name = sc.next();\n"
              "        int n = sc.nextInt();\n"
              "        List<String> source = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            source.add(sc.next());\n"
              "        }\n"
              "        Playlist p = new Playlist(name, source);\n"
              "        source.clear();\n"
              "        System.out.println(p);\n"
              "        try {\n"
              "            p.songs().add(\"extra\");\n"
              "            System.out.println(\"modified\");\n"
              "        } catch (UnsupportedOperationException e) {\n"
              "            System.out.println(\"unmodifiable\");\n"
              "        }",
              "\n".join(_PLAYLIST34.strip("\n").split("\n")[1:-1]),
              [_case(f"{nm}\n{len(ss)}\n{' '.join(ss)}" if ss else f"{nm}\n0\n",
                     _nl(_rec34("Playlist", name=nm, songs=_jarr(ss)), "unmodifiable"))
               for (nm, ss) in _PLAYLISTS34],
              ["`Playlist { songs = List.copyOf(songs); }`",
               "`source.clear()` empties the caller's list - the record's copy is unaffected.",
               "The copy is unmodifiable, so `add` throws `UnsupportedOperationException`."]),

        _p34t("j34-pb-key", "A sorted composite key", "Medium",
              "Count sales per (city, year) in a `TreeMap<Key, Integer>`. A TreeMap needs "
              "an order, so make `Key` implement `Comparable`: by city, then by year - using "
              "a comparator built once in a static field.",
              _KEY34,
              "        int n = sc.nextInt();\n"
              "        Map<Key, Integer> sales = new TreeMap<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            sales.merge(new Key(sc.next(), sc.nextInt()), 1, Integer::sum);\n"
              "        }\n"
              "        System.out.println(sales);",
              _KEY_REGION34,
              [_rows34(rows, _sales_out34(rows)) for rows in _SALES34],
              ["A record may have static fields - just not extra instance fields.",
               "`Comparator.comparing(Key::city).thenComparingInt(Key::year)`",
               "Accessors are method references like any other: `Key::city`.",
               "`compareTo` delegates: `return ORDER.compare(this, other);`"]),

        _p34t("j34-pb-sort", "Sorting by accessor", "Medium",
              "Sort the employees by department, then by salary highest first, then by "
              "name, and print them. Build the comparator from the record's accessors.",
              _EMP34,
              "        int n = sc.nextInt();\n"
              "        List<Employee> staff = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            staff.add(new Employee(sc.next(), sc.next(), sc.nextInt()));\n"
              "        }\n"
              "        staff.sort(Comparator.comparing(Employee::dept)\n"
              "                .thenComparing(Employee::salary, Comparator.reverseOrder())\n"
              "                .thenComparing(Employee::name));\n"
              "        for (Employee e : staff) {\n"
              "            System.out.println(e);\n"
              "        }",
              "        staff.sort(Comparator.comparing(Employee::dept)\n"
              "                .thenComparing(Employee::salary, Comparator.reverseOrder())\n"
              "                .thenComparing(Employee::name));",
              [_rows34(rows, _emp_sorted34(rows)) for rows in _EMPS34],
              ["`Comparator.comparing(Employee::dept)` first.",
               "`thenComparing(Employee::salary, Comparator.reverseOrder())` - highest "
               "first, only among equal departments.",
               "`thenComparing(Employee::name)` breaks the last ties."]),

        _p34t("j34-pb-group", "Totals per department", "Hard",
              "Sum the salaries per department with one stream pipeline, into a `TreeMap` "
              "so departments print in order.",
              _EMP34,
              "        int n = sc.nextInt();\n"
              "        List<Employee> staff = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            staff.add(new Employee(sc.next(), sc.next(), sc.nextInt()));\n"
              "        }\n"
              "        Map<String, Integer> totals = staff.stream()\n"
              "                .collect(Collectors.groupingBy(Employee::dept, TreeMap::new,\n"
              "                        Collectors.summingInt(Employee::salary)));\n"
              "        System.out.println(totals);",
              "        Map<String, Integer> totals = staff.stream()\n"
              "                .collect(Collectors.groupingBy(Employee::dept, TreeMap::new,\n"
              "                        Collectors.summingInt(Employee::salary)));",
              [_rows34(rows, _emp_group34(rows)) for rows in _EMPS34],
              ["Module 27's three-argument `groupingBy`: classifier, map factory, "
               "downstream collector.",
               "`Employee::dept` classifies; `TreeMap::new` orders the keys.",
               "`Collectors.summingInt(Employee::salary)` totals each group."]),
    ],
)


# --- Family C - instanceof patterns ----------------------------------------------

_MIXED34 = (["i:5", "s:hello", "i:7"], ["d:2.5"], ["b:true", "i:-3", "s:xyz", "s:tiny"],
            ["s:pattern", "d:0.5", "i:0", "s:ab"], ["b:false", "i:21", "s:longest", "s:four"])


def _vals34(ts):
    return [_pobj34(t) for t in ts]


def _sum_ints34(ts):
    return sum(v for (k, v) in _vals34(ts) if k == "int")


def _longest34(ts):
    best = None
    for (k, v) in _vals34(ts):
        if k == "str" and (best is None or len(v) > len(best)):
            best = v
    return best or "(none)"


def _count_long34(ts):
    return sum(1 for (k, v) in _vals34(ts) if k == "str" and len(v) > 3)


_MONEYC34 = """
class Money {
    private final String currency;
    private final int cents;

    Money(String currency, int cents) {
        this.currency = currency;
        this.cents = cents;
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof Money m && cents == m.cents && currency.equals(m.currency);
    }

    @Override
    public int hashCode() {
        return Objects.hash(currency, cents);
    }
}
"""
_MONEYC_REGION34 = "\n".join(_MONEYC34.strip("\n").split("\n")[9:-1])
_MONEYS34 = ([("EUR", 5), ("EUR", 5), ("USD", 5)], [("GBP", 1)], [("JPY", 0), ("JPY", 1), ("JPY", 0)],
             [("EUR", 10), ("USD", 10), ("EUR", 10), ("USD", 10)], [("CHF", 7)])

_INITS34 = (["s:ada", "i:4", "s:"], ["s:bob"], ["b:true", "s:zed", "d:1.5"], ["s:", "s:x"],
            ["i:1", "s:grace", "s:hopper"])


def _initial34(tok):
    k, v = _pobj34(tok)
    return "-" if k != "str" or v == "" else v[0].upper()


_P34_C = _jfam(
    "p34-instanceof", "`instanceof` patterns",
    "Test, cast and bind in one step - and let flow scoping do the rest.",
    """
Every drill reads typed tokens - `i:5`, `d:2.5`, `b:true`, `s:text` - through
module 34's `parse` helper, so the values arrive as a genuinely mixed
`List<Object>`.

```java
if (o instanceof Integer i) total += i;
if (o instanceof String s && s.length() > 3) count++;
if (!(o instanceof String s) || s.isEmpty()) return "-";   // s IS in scope after ||
return s.substring(0, 1);
```

That last line is the subtle one. The right side of `||` runs only when the left
side is *false* - that is, when `o` *is* a String - so `s` is in scope there,
and after the `if`.
""",
    [
        _p34h("j34-pc-sum", "Adding up the integers", "Intro",
              "Sum only the Integers in the mixed list.",
              "", _PARSE34,
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Object o = parse(sc.next());\n"
              "            if (o instanceof Integer x) {\n"
              "                total += x;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(total);",
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Object o = parse(sc.next());\n"
              "            if (o instanceof Integer x) {\n"
              "                total += x;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(total);",
              [_toks34(ts, _sum_ints34(ts)) for ts in _MIXED34],
              ["`o instanceof Integer x` binds `x` as an Integer.",
               "`total += x` unboxes it.",
               "The loop variable is already `i`, so name the binding something else."]),

        _p34h("j34-pc-longest", "The longest string", "Easy",
              "Print the longest String in the mixed list (the first, on a tie), or "
              "`(none)` when there are no Strings.",
              "", _PARSE34,
              "        int n = sc.nextInt();\n"
              "        String best = null;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (parse(sc.next()) instanceof String s && (best == null || s.length() > best.length())) {\n"
              "                best = s;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(best == null ? \"(none)\" : best);",
              "        String best = null;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (parse(sc.next()) instanceof String s && (best == null || s.length() > best.length())) {\n"
              "                best = s;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(best == null ? \"(none)\" : best);",
              [_toks34(ts, _longest34(ts)) for ts in _MIXED34],
              ["The pattern can test any expression, not just a variable.",
               "`s` is in scope on the right of `&&`.",
               "Strict `>` keeps the first of equal-length strings."]),

        _p34h("j34-pc-count", "Long strings only", "Medium",
              "Count the Strings longer than three characters with a single `if` that both "
              "matches and tests the length.",
              "", _PARSE34,
              "        int n = sc.nextInt();\n"
              "        int count = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Object o = parse(sc.next());\n"
              "            if (o instanceof String s && s.length() > 3) {\n"
              "                count++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(count);",
              "            if (o instanceof String s && s.length() > 3) {\n"
              "                count++;\n"
              "            }",
              [_toks34(ts, _count_long34(ts)) for ts in _MIXED34],
              ["`o instanceof String s && s.length() > 3`",
               "With `||` instead of `&&`, `s` would be out of scope - it would be used "
               "exactly when the match failed.",
               "`tiny` has exactly four letters, so it counts."]),

        _p34t("j34-pc-equals", "`equals` for an ordinary class", "Medium",
              "`Money` is a class, not a record. Write its `equals` with a type pattern "
              "(currency and cents must both match) and a matching `hashCode`. `main` "
              "counts the distinct amounts in a HashSet.",
              _MONEYC34,
              "        int n = sc.nextInt();\n"
              "        Set<Money> distinct = new HashSet<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            distinct.add(new Money(sc.next(), sc.nextInt()));\n"
              "        }\n"
              "        System.out.println(distinct.size());",
              _MONEYC_REGION34,
              [_rows34(rows, len(set(rows))) for rows in _MONEYS34],
              ["`return o instanceof Money m && cents == m.cents && currency.equals(m.currency);`",
               "Compare the int with `==` and the String with `equals`.",
               "`hashCode` must use the same two fields: `Objects.hash(currency, cents)`.",
               "A record would have generated both - this is what it saves you."]),

        _p34h("j34-pc-initial", "In scope after `||`", "Hard",
              "Print each value's initial - its first letter, upper-cased - or `-` when it "
              "is not a String or is an empty one. Write `initial` with a single guard "
              "clause using `!(... instanceof String s) || ...`.",
              "",
              _PARSE34 + "\n\n"
              "    static String initial(Object o) {\n"
              "        if (!(o instanceof String s) || s.isEmpty()) {\n"
              "            return \"-\";\n"
              "        }\n"
              "        return s.substring(0, 1).toUpperCase();\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String token = sc.next();\n"
              "            System.out.println(initial(parse(token)));\n"
              "        }",
              "    static String initial(Object o) {\n"
              "        if (!(o instanceof String s) || s.isEmpty()) {\n"
              "            return \"-\";\n"
              "        }\n"
              "        return s.substring(0, 1).toUpperCase();\n"
              "    }",
              [_toks34(ts, _nl(*[_initial34(t) for t in ts])) for ts in _INITS34],
              ["The right side of `||` runs only when `o` IS a String - so `s` is usable "
               "there.",
               "After the `if` returns, the compiler knows `o` was a non-empty String.",
               "`s:` is an empty string: the token is two characters, and `substring(2)` "
               "is `\"\"`.",
               "`substring(0, 1).toUpperCase()` is the initial."]),
    ],
)


# --- Family D - sealed types ------------------------------------------------------

_ANIMALS34 = """
sealed interface Animal permits Dog, Cat, Cow {}

record Dog(String name) implements Animal {}

record Cat(String name, int lives) implements Animal {}

record Cow(String name) implements Animal {}
"""
_ANIMALROWS34 = ([("dog", "rex"), ("cat", "tom", 9)], [("cow", "daisy")],
                 [("cat", "kit", 3), ("dog", "fido"), ("cow", "bess")], [("dog", "a"), ("dog", "b")],
                 [("cat", "felix", 1)])
_READANIMAL34 = (
    "    static Animal read(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        return switch (kind) {\n"
    "            case \"dog\" -> new Dog(sc.next());\n"
    "            case \"cat\" -> new Cat(sc.next(), sc.nextInt());\n"
    "            default -> new Cow(sc.next());\n"
    "        };\n"
    "    }"
)


def _animal_if34(r):
    if r[0] == "dog":
        return f"{r[1]} says woof"
    if r[0] == "cat":
        return f"{r[1]} says meow ({r[2]} lives)"
    return f"{r[1]} says moo"


_ACCOUNTS34 = """
sealed abstract class Account permits Checking, Savings {
    final int balance;

    Account(int balance) {
        this.balance = balance;
    }

    abstract int monthlyInterest();
}

final class Checking extends Account {
    Checking(int balance) {
        super(balance);
    }

    int monthlyInterest() {
        return 0;
    }
}

final class Savings extends Account {
    Savings(int balance) {
        super(balance);
    }

    int monthlyInterest() {
        return balance / 100;
    }
}
"""
_ACCOUNTS_REGION34 = _ACCOUNTS34[_ACCOUNTS34.index("final class Checking"):].strip("\n")
_ACCTROWS34 = ([("checking", 500), ("savings", 1000)], [("savings", 99)],
               [("savings", 12345), ("checking", 1), ("savings", 100)], [("checking", 0)],
               [("savings", 250), ("savings", 350)])

_RESULT34 = """
sealed interface Result permits Ok, Err {}

record Ok(int value) implements Result {}

record Err(String message) implements Result {}
"""
_PARSERESULT34 = (
    "    static Result parseNumber(String text) {\n"
    "        try {\n"
    "            return new Ok(Integer.parseInt(text));\n"
    "        } catch (NumberFormatException e) {\n"
    "            return new Err(\"not a number: \" + text);\n"
    "        }\n"
    "    }"
)
_RTOKS34 = (["12", "x", "30"], ["abc"], ["-5", "5", "0"], ["1.5", "7"], ["99", "9", "oops"])


def _is_int34(t):
    """What `Integer.parseInt` accepts, for these small tokens: an optional sign
    and digits. (Python's `int()` would also accept `1_0` and spaces.)"""
    body = t[1:] if t[:1] in "+-" else t
    return body.isdigit() and body.isascii()


def _results_out34(ts):
    out, total, errs = [], 0, 0
    for t in ts:
        if _is_int34(t):
            out.append(_rec34("Ok", value=int(t)))
            total += int(t)
        else:
            out.append(_rec34("Err", message=f"not a number: {t}"))
            errs += 1
    out.append(f"sum {total}, errors {errs}")
    return _nl(*out)


_TREE34 = """
sealed interface Tree permits Leaf, Node {}

record Leaf() implements Tree {}

record Node(Tree left, int value, Tree right) implements Tree {}
"""
# Pre-order with the value FIRST: "5 3 . . 8 . ." is node 5 with children 3 and 8.
_TREEPARSE34 = (
    "    static Tree parse(Scanner sc) {\n"
    "        String t = sc.next();\n"
    "        if (t.equals(\".\")) {\n"
    "            return new Leaf();\n"
    "        }\n"
    "        int value = Integer.parseInt(t);\n"
    "        Tree left = parse(sc);\n"
    "        Tree right = parse(sc);\n"
    "        return new Node(left, value, right);\n"
    "    }"
)
_TREES34 = ("5 3 . . 8 . .", ".", "1 . 2 . 3 . .", "10 4 1 . . . 20 . 30 . .", "7 . .")


def _ptree34(tokens):
    t = tokens.pop(0)
    if t == ".":
        return None
    v = int(t)
    left = _ptree34(tokens)
    right = _ptree34(tokens)
    return (left, v, right)


def _tsum34(t):
    return 0 if t is None else _tsum34(t[0]) + t[1] + _tsum34(t[2])


def _theight34(t):
    return 0 if t is None else 1 + max(_theight34(t[0]), _theight34(t[2]))


def _tcount34(t):
    return 0 if t is None else 1 + _tcount34(t[0]) + _tcount34(t[2])


_TOLL34 = """
sealed interface Vehicle permits Bike, Motor {}

record Bike() implements Vehicle {}

sealed interface Motor extends Vehicle permits Car, Van {}

record Car(int seats) implements Motor {}

record Van(int axles) implements Motor {}
"""
_TOLL_REGION34 = (
    "sealed interface Motor extends Vehicle permits Car, Van {}\n"
    "\n"
    "record Car(int seats) implements Motor {}\n"
    "\n"
    "record Van(int axles) implements Motor {}"
)
_TOLLROWS34 = ([("bike",), ("car", 4)], [("van", 3)], [("car", 7), ("van", 2), ("bike",)],
               [("bike",), ("bike",)], [("van", 5), ("car", 2)])


def _toll34(r):
    if r[0] == "bike":
        return "Bike[] 0 unmotorised"
    if r[0] == "car":
        toll = 5 if r[1] <= 5 else 8
        return f"{_rec34('Car', seats=r[1])} {toll} motorised"
    return f"{_rec34('Van', axles=r[1])} {4 * r[1]} motorised"


_P34_D = _jfam(
    "p34-sealed", "Sealed hierarchies",
    "A closed list of cases - of records, final classes, or a sealed sub-hierarchy.",
    """
```java
sealed interface Result permits Ok, Err {}
record Ok(int value) implements Result {}
record Err(String message) implements Result {}

sealed interface Vehicle permits Bike, Motor {}
sealed interface Motor extends Vehicle permits Car, Van {}   // sealed, in turn
```

`Result` is a common shape: an operation that either produced a value or failed,
as data rather than as an exception. A sealed hierarchy can also be layered - a
permitted subtype that is itself `sealed` closes its own branch - and a tree is
the classic recursive case: a `Node` holds more `Tree`s.
""",
    [
        _p34h("j34-pd-animals", "Three animals", "Intro",
              "`Animal` is sealed with three record cases. Describe each with an "
              "`instanceof` chain: a dog says woof, a cat says meow and reports its lives, "
              "a cow says moo.",
              _ANIMALS34,
              _READANIMAL34 + "\n\n"
              "    static String speak(Animal a) {\n"
              "        if (a instanceof Dog d) {\n"
              "            return d.name() + \" says woof\";\n"
              "        } else if (a instanceof Cat c) {\n"
              "            return c.name() + \" says meow (\" + c.lives() + \" lives)\";\n"
              "        } else if (a instanceof Cow c) {\n"
              "            return c.name() + \" says moo\";\n"
              "        }\n"
              "        throw new IllegalStateException();\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            System.out.println(speak(read(sc)));\n"
              "        }",
              "    static String speak(Animal a) {\n"
              "        if (a instanceof Dog d) {\n"
              "            return d.name() + \" says woof\";\n"
              "        } else if (a instanceof Cat c) {\n"
              "            return c.name() + \" says meow (\" + c.lives() + \" lives)\";\n"
              "        } else if (a instanceof Cow c) {\n"
              "            return c.name() + \" says moo\";\n"
              "        }\n"
              "        throw new IllegalStateException();\n"
              "    }",
              [_rows34(rows, _nl(*[_animal_if34(r) for r in rows])) for rows in _ANIMALROWS34],
              ["One `instanceof` pattern per record.",
               "The binding names can be reused in separate branches.",
               "An `if` chain still needs the final `throw` - the next family's switch "
               "will not."]),

        _p34t("j34-pd-final", "Final subclasses", "Easy",
              "`Account` is a sealed abstract class permitting `Checking` and `Savings`. "
              "Write both as FINAL subclasses: checking pays no interest, savings pays 1% a "
              "month (integer division).",
              _ACCOUNTS34,
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String kind = sc.next();\n"
              "            int balance = sc.nextInt();\n"
              "            Account a = kind.equals(\"checking\") ? new Checking(balance) : new Savings(balance);\n"
              "            System.out.println(kind + \" \" + a.monthlyInterest());\n"
              "            total += a.monthlyInterest();\n"
              "        }\n"
              "        System.out.println(total);",
              _ACCOUNTS_REGION34,
              [_rows34(rows, _nl(*[f"{k} {0 if k == 'checking' else b // 100}" for (k, b) in rows],
                                 sum(0 if k == 'checking' else b // 100 for (k, b) in rows)))
               for rows in _ACCTROWS34],
              ["Each permitted subclass must be `final`, `sealed` or `non-sealed`.",
               "`final class Checking extends Account` with a constructor calling "
               "`super(balance)`.",
               "`balance` is a field of the abstract class, readable in the subclass.",
               "`balance / 100` is 1% in integer arithmetic."]),

        _p34h("j34-pd-result", "Success or failure, as data", "Medium",
              "`parseNumber` returns an `Ok` or an `Err` instead of throwing. Print each "
              "result, then the sum of the Oks and the number of Errs.",
              _RESULT34, _PARSERESULT34,
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        int errors = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Result r = parseNumber(sc.next());\n"
              "            System.out.println(r);\n"
              "            if (r instanceof Ok ok) {\n"
              "                total += ok.value();\n"
              "            } else {\n"
              "                errors++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(\"sum \" + total + \", errors \" + errors);",
              "            if (r instanceof Ok ok) {\n"
              "                total += ok.value();\n"
              "            } else {\n"
              "                errors++;\n"
              "            }",
              [_toks34(ts, _results_out34(ts)) for ts in _RTOKS34],
              ["A `Result` is exactly one of two records.",
               "`r instanceof Ok ok` - anything else must be an `Err`, because the "
               "interface is sealed.",
               "The failure travels as a value you can print, count or pass on."]),

        _p34h("j34-pd-tree", "A recursive sealed type", "Medium",
              "A `Tree` is a `Leaf` or a `Node(left, value, right)`. Write `sum`, `height` "
              "and `size` recursively with `instanceof` patterns. Input is pre-order with "
              "`.` for a leaf.",
              _TREE34,
              _TREEPARSE34 + "\n\n"
              "    static int sum(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return sum(n.left()) + n.value() + sum(n.right());\n"
              "        }\n"
              "        return 0;\n"
              "    }\n"
              "\n"
              "    static int height(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return 1 + Math.max(height(n.left()), height(n.right()));\n"
              "        }\n"
              "        return 0;\n"
              "    }\n"
              "\n"
              "    static int size(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return 1 + size(n.left()) + size(n.right());\n"
              "        }\n"
              "        return 0;\n"
              "    }",
              "        Tree t = parse(sc);\n"
              "        System.out.println(sum(t) + \" \" + height(t) + \" \" + size(t));",
              "    static int sum(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return sum(n.left()) + n.value() + sum(n.right());\n"
              "        }\n"
              "        return 0;\n"
              "    }\n"
              "\n"
              "    static int height(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return 1 + Math.max(height(n.left()), height(n.right()));\n"
              "        }\n"
              "        return 0;\n"
              "    }\n"
              "\n"
              "    static int size(Tree t) {\n"
              "        if (t instanceof Node n) {\n"
              "            return 1 + size(n.left()) + size(n.right());\n"
              "        }\n"
              "        return 0;\n"
              "    }",
              [_case(src, f"{_tsum34(_ptree34(src.split()))} {_theight34(_ptree34(src.split()))} "
                          f"{_tcount34(_ptree34(src.split()))}") for src in _TREES34],
              ["A Leaf contributes nothing: 0 for all three.",
               "`t instanceof Node n` - then recurse on `n.left()` and `n.right()`.",
               "Height is 1 plus the taller subtree.",
               "Sealing is what makes 'not a Node, so a Leaf' a safe conclusion."]),

        _p34h("j34-pd-layers", "A sealed sub-hierarchy", "Hard",
              "`Vehicle` permits `Bike` and `Motor`, and `Motor` is itself sealed, "
              "permitting `Car` and `Van`. Write `Motor` and its two records. A car's toll "
              "is 5 (8 above five seats), a van's is 4 per axle, and a bike is free.",
              _TOLL34,
              "    static int toll(Vehicle v) {\n"
              "        if (v instanceof Car c) {\n"
              "            return c.seats() <= 5 ? 5 : 8;\n"
              "        } else if (v instanceof Van van) {\n"
              "            return 4 * van.axles();\n"
              "        }\n"
              "        return 0;\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String kind = sc.next();\n"
              "            Vehicle v = switch (kind) {\n"
              "                case \"car\" -> new Car(sc.nextInt());\n"
              "                case \"van\" -> new Van(sc.nextInt());\n"
              "                default -> new Bike();\n"
              "            };\n"
              "            System.out.println(v + \" \" + toll(v) + \" \"\n"
              "                    + (v instanceof Motor ? \"motorised\" : \"unmotorised\"));\n"
              "        }",
              _TOLL_REGION34,
              [_rows34(rows, _nl(*[_toll34(r) for r in rows])) for rows in _TOLLROWS34],
              ["`sealed interface Motor extends Vehicle permits Car, Van {}`",
               "A sealed permitted subtype satisfies the rule - it continues the hierarchy "
               "as sealed.",
               "`record Car(int seats) implements Motor {}` - implementing `Motor` makes it "
               "a `Vehicle` too.",
               "`v instanceof Motor` is true for cars and vans alike."]),
    ],
)


# --- Family E - pattern switch ----------------------------------------------------

_TEMPS34 = """
sealed interface Reading permits Celsius, Fahrenheit {}

record Celsius(int degrees) implements Reading {}

record Fahrenheit(int degrees) implements Reading {}
"""
_TEMPROWS34 = ([("c", 35), ("f", 50)], [("c", -5)], [("f", 100), ("c", 20), ("f", 30)],
               [("c", 30), ("f", 86)], [("f", 32), ("c", 0), ("c", 10)])


def _feel34(k, d):
    c = d if k == "c" else _jdiv((d - 32) * 5, 9)
    if c >= 30:
        return f"{c}C hot"
    if c <= 0:
        return f"{c}C freezing"
    return f"{c}C mild"


_SIMPLIFY34 = (
    "    static Expr simplify(Expr e) {\n"
    "        return switch (e) {\n"
    "            case Num n -> n;\n"
    "            case Neg(Neg(Expr inner)) -> simplify(inner);\n"
    "            case Neg(Expr inner) -> new Neg(simplify(inner));\n"
    "            case Add(Expr l, Expr r) -> {\n"
    "                Expr a = simplify(l);\n"
    "                Expr b = simplify(r);\n"
    "                if (a instanceof Num(int x) && x == 0) {\n"
    "                    yield b;\n"
    "                }\n"
    "                if (b instanceof Num(int y) && y == 0) {\n"
    "                    yield a;\n"
    "                }\n"
    "                yield new Add(a, b);\n"
    "            }\n"
    "            case Mul(Expr l, Expr r) -> {\n"
    "                Expr a = simplify(l);\n"
    "                Expr b = simplify(r);\n"
    "                if (a instanceof Num(int x) && x == 0 || b instanceof Num(int y) && y == 0) {\n"
    "                    yield new Num(0);\n"
    "                }\n"
    "                if (a instanceof Num(int x) && x == 1) {\n"
    "                    yield b;\n"
    "                }\n"
    "                if (b instanceof Num(int y) && y == 1) {\n"
    "                    yield a;\n"
    "                }\n"
    "                yield new Mul(a, b);\n"
    "            }\n"
    "        };\n"
    "    }"
)

_SHOWEVAL34 = (
    "    static int eval(Expr e) {\n"
    "        return switch (e) {\n"
    "            case Num(int v) -> v;\n"
    "            case Add(Expr l, Expr r) -> eval(l) + eval(r);\n"
    "            case Mul(Expr l, Expr r) -> eval(l) * eval(r);\n"
    "            case Neg(Expr inner) -> -eval(inner);\n"
    "        };\n"
    "    }\n"
    "\n"
    "    static String show(Expr e) {\n"
    "        return switch (e) {\n"
    "            case Num(int v) -> String.valueOf(v);\n"
    "            case Add(Expr l, Expr r) -> \"(\" + show(l) + \" + \" + show(r) + \")\";\n"
    "            case Mul(Expr l, Expr r) -> \"(\" + show(l) + \" * \" + show(r) + \")\";\n"
    "            case Neg(Expr inner) -> \"-\" + show(inner);\n"
    "        };\n"
    "    }"
)


def _simplify34(e):
    if e[0] == "num":
        return e
    if e[0] == "neg":
        if e[1][0] == "neg":
            return _simplify34(e[1][1])
        return ("neg", _simplify34(e[1]))
    a, b = _simplify34(e[1]), _simplify34(e[2])
    if e[0] == "add":
        if a == ("num", 0):
            return b
        if b == ("num", 0):
            return a
        return ("add", a, b)
    if a == ("num", 0) or b == ("num", 0):
        return ("num", 0)
    if a == ("num", 1):
        return b
    if b == ("num", 1):
        return a
    return ("mul", a, b)


_SIMPS34 = ("add 0 mul 1 5", "neg neg 7", "mul add 2 3 0", "add mul 1 neg neg 4 add 0 0",
            "neg add 1 mul 2 1")


def _simp_case34(src):
    e = _parse_expr34(src.split())
    s = _simplify34(e)
    return _case(src, _nl(_show34(e), _show34(s), _eval34(s)))


_P34_E = _jfam(
    "p34-switch", "Pattern switches",
    "Type patterns, record patterns, guards and nesting - with no `default` over a "
    "sealed type.",
    """
```java
return switch (reading) {
    case Celsius(int c) when c >= 30 -> "hot";
    case Celsius(int c) -> "mild";
    case Fahrenheit(int f) -> ...;
};

case Neg(Neg(Expr inner)) -> simplify(inner);    // nested record patterns
case Neg(Expr inner) -> new Neg(simplify(inner)); // the general case AFTER
```

Two habits. Put the specific cases (guards, nested patterns) above the general
ones - the compiler rejects any case an earlier one dominates. And leave out the
`default` over a sealed type, so the next new case is a compile error rather than
a silent fall into "other".
""",
    [
        _p34h("j34-pe-animals", "Three animals, one switch", "Intro",
              "Rewrite family D's `speak` as a pattern switch with record patterns and no "
              "`default`.",
              _ANIMALS34,
              _READANIMAL34 + "\n\n"
              "    static String speak(Animal a) {\n"
              "        return switch (a) {\n"
              "            case Dog(String name) -> name + \" says woof\";\n"
              "            case Cat(String name, int lives) -> name + \" says meow (\" + lives + \" lives)\";\n"
              "            case Cow(String name) -> name + \" says moo\";\n"
              "        };\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            System.out.println(speak(read(sc)));\n"
              "        }",
              "    static String speak(Animal a) {\n"
              "        return switch (a) {\n"
              "            case Dog(String name) -> name + \" says woof\";\n"
              "            case Cat(String name, int lives) -> name + \" says meow (\" + lives + \" lives)\";\n"
              "            case Cow(String name) -> name + \" says moo\";\n"
              "        };\n"
              "    }",
              [_rows34(rows, _nl(*[_animal_if34(r) for r in rows])) for rows in _ANIMALROWS34],
              ["`case Dog(String name) -> ...` deconstructs the record.",
               "Three permitted records, three cases - no `default`, no `throw`.",
               "Compare with the `if` chain: same logic, and now checked for completeness."]),

        _p34h("j34-pe-result", "Folding results", "Easy",
              "Total the Oks and count the Errs with a pattern switch over the sealed "
              "`Result` - a statement switch, since each arm updates a variable.",
              _RESULT34, _PARSERESULT34,
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        int errors = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Result r = parseNumber(sc.next());\n"
              "            System.out.println(r);\n"
              "            switch (r) {\n"
              "                case Ok(int value) -> total += value;\n"
              "                case Err e -> errors++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(\"sum \" + total + \", errors \" + errors);",
              "            switch (r) {\n"
              "                case Ok(int value) -> total += value;\n"
              "                case Err e -> errors++;\n"
              "            }",
              [_toks34(ts, _results_out34(ts)) for ts in _RTOKS34],
              ["A pattern switch STATEMENT must be exhaustive too.",
               "`case Ok(int value) -> total += value;`",
               "`case Err e -> errors++;` - the binding need not be used."]),

        _p34h("j34-pe-guards", "Hot, mild or freezing", "Medium",
              "A reading is in Celsius or Fahrenheit. Convert to whole Celsius (Fahrenheit: "
              "`(f - 32) * 5 / 9`, integer division), then classify with guarded cases: "
              "30 and above is hot, 0 and below is freezing, anything else mild. Print "
              "`<c>C <word>`.",
              _TEMPS34,
              "    static int celsius(Reading r) {\n"
              "        return switch (r) {\n"
              "            case Celsius(int c) -> c;\n"
              "            case Fahrenheit(int f) -> (f - 32) * 5 / 9;\n"
              "        };\n"
              "    }\n"
              "\n"
              "    static String feel(int c) {\n"
              "        return switch (Integer.valueOf(c)) {\n"
              "            case Integer t when t >= 30 -> t + \"C hot\";\n"
              "            case Integer t when t <= 0 -> t + \"C freezing\";\n"
              "            case Integer t -> t + \"C mild\";\n"
              "        };\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String unit = sc.next();\n"
              "            int d = sc.nextInt();\n"
              "            Reading r = unit.equals(\"c\") ? new Celsius(d) : new Fahrenheit(d);\n"
              "            System.out.println(feel(celsius(r)));\n"
              "        }",
              "    static String feel(int c) {\n"
              "        return switch (Integer.valueOf(c)) {\n"
              "            case Integer t when t >= 30 -> t + \"C hot\";\n"
              "            case Integer t when t <= 0 -> t + \"C freezing\";\n"
              "            case Integer t -> t + \"C mild\";\n"
              "        };\n"
              "    }",
              [_rows34(rows, _nl(*[_feel34(k, d) for (k, d) in rows])) for rows in _TEMPROWS34],
              ["Switching on the boxed `Integer` lets every case be a guarded type pattern.",
               "Guarded cases first; the plain `case Integer t` last catches the rest.",
               "The unguarded case makes the switch exhaustive - no default needed.",
               "50°F is 10°C: `(50 - 32) * 5 / 9`."]),

        _p34h("j34-pe-tree", "The tree, by switch", "Medium",
              "Rewrite family D's tree `sum` and `height` as pattern switches with record "
              "patterns. The input is the same pre-order format.",
              _TREE34,
              _TREEPARSE34 + "\n\n"
              "    static int sum(Tree t) {\n"
              "        return switch (t) {\n"
              "            case Leaf l -> 0;\n"
              "            case Node(Tree left, int value, Tree right) -> sum(left) + value + sum(right);\n"
              "        };\n"
              "    }\n"
              "\n"
              "    static int height(Tree t) {\n"
              "        return switch (t) {\n"
              "            case Leaf l -> 0;\n"
              "            case Node(Tree left, int value, Tree right) -> 1 + Math.max(height(left), height(right));\n"
              "        };\n"
              "    }",
              "        Tree t = parse(sc);\n"
              "        System.out.println(sum(t) + \" \" + height(t));",
              "    static int sum(Tree t) {\n"
              "        return switch (t) {\n"
              "            case Leaf l -> 0;\n"
              "            case Node(Tree left, int value, Tree right) -> sum(left) + value + sum(right);\n"
              "        };\n"
              "    }\n"
              "\n"
              "    static int height(Tree t) {\n"
              "        return switch (t) {\n"
              "            case Leaf l -> 0;\n"
              "            case Node(Tree left, int value, Tree right) -> 1 + Math.max(height(left), height(right));\n"
              "        };\n"
              "    }",
              [_case(src, f"{_tsum34(_ptree34(src.split()))} {_theight34(_ptree34(src.split()))}")
               for src in _TREES34],
              ["`case Leaf l -> 0;`",
               "`case Node(Tree left, int value, Tree right) -> ...` binds all three parts.",
               "Two cases cover the sealed `Tree` - exhaustive, no default."]),

        _p34h("j34-pe-simplify", "Simplifying expressions", "Hard",
              "Write `simplify` for module 34's `Expr`: simplify the children first, then "
              "`x + 0` and `0 + x` become `x`; `x * 0` and `0 * x` become `0`; `x * 1` and "
              "`1 * x` become `x`; and a double negation `--x` becomes `x`. Use a nested "
              "record pattern for the double negation, placed before the general `Neg` case.",
              _EXPR34, _EXPR_PARSE34 + "\n\n" + _SHOWEVAL34 + "\n\n" + _SIMPLIFY34,
              "        Expr e = parse(sc);\n"
              "        Expr s = simplify(e);\n"
              "        System.out.println(show(e));\n"
              "        System.out.println(show(s));\n"
              "        System.out.println(eval(s));",
              _SIMPLIFY34,
              [_simp_case34(src) for src in _SIMPS34],
              ["`case Neg(Neg(Expr inner)) -> simplify(inner);` - a pattern inside a "
               "pattern.",
               "It must come BEFORE `case Neg(Expr inner)`, which would otherwise dominate "
               "it.",
               "For `Add` and `Mul`, simplify both sides first, then look at the results.",
               "`a instanceof Num(int x) && x == 0` recognises a literal zero.",
               "A block arm with several `if (...) { yield ...; }` checks, and a final "
               "`yield` for the general case.",
               "`eval` of the simplified expression equals `eval` of the original - the "
               "simplification never changes the value."]),
    ],
)


_PRACTICE[34] = [_P34_A, _P34_B, _P34_C, _P34_D, _P34_E]
