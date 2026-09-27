# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 34 - Records, sealed types and pattern matching.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# MODERN JAVA, AND THE JDK IT NEEDS. Everything here arrived between Java 16 and
# Java 21: records and `instanceof` patterns (16), sealed types (17), and
# pattern matching in `switch` with record patterns (21). This is the one
# module in the course that REQUIRES JDK 21 or later - on an older JDK its
# programs do not compile. The module summary says so up front.
#
# TEACHING SPINE: data-oriented programming. A record says "this is just data",
# a sealed interface says "and these are ALL the shapes it can take", and a
# pattern-matching switch takes it apart - with the compiler checking that no
# shape was forgotten. Lesson 34.5 is where the three meet; the capstone and the
# expression evaluator are the classic demonstrations.
#
# `record `, `sealed`, `permits`, `case null`, ` when ` and `List.copyOf`
# become legal here and nowhere earlier.
#
# JUDGING NOTES
#   * A record's toString is `Point[x=1, y=2]` - specified, and mirrored by
#     `_rec34`.
#   * Hash-based collections are printed only through LinkedHashSet /
#     LinkedHashMap (insertion order) or TreeMap, never HashSet / HashMap.
# ---------------------------------------------------------------------------

import math as _math34

_M34 = []

_IMPORTS34 = ("import java.util.*;\n"
              "import java.util.stream.*;\n")


def _j34s(body):
    return _jscan(body, imports=_IMPORTS34)


def _j34t(types, body):
    return _joop(types, body, imports=_IMPORTS34)


def _j34th(types, helpers, body):
    """Helper types above Main, static helpers inside it, then main."""
    return _jp(
        _IMPORTS34 + "\n"
        + types.strip("\n") + "\n\n"
        + "public class Main {\n"
        + helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }\n}"
    )


def _rec34(_rtype, **fields):
    """How a record prints. (The type is positional-only in spirit, so a
    component may itself be called `name`.)"""
    return f"{_rtype}[" + ", ".join(f"{k}={v}" for (k, v) in fields.items()) + "]"


def _pt34(x, y):
    return _rec34("Point", x=x, y=y)


def _rows34(rows, out):
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


def _toks34(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


# ===========================================================================
# 34.1 Records
# ===========================================================================

_POINTS34 = ([(1, 2), (3, 4)], [(0, 0)], [(-1, 5), (5, -1), (2, 2)], [(7, 7), (7, 7)],
             [(10, 0), (0, 10), (-3, -4)])

_SEEN34 = ([(1, 2), (3, 4), (1, 2)], [(0, 0), (0, 0), (0, 0)], [(5, 5)],
           [(1, 2), (2, 1), (1, 2), (2, 1)], [(-1, 0), (0, -1), (0, 0), (-1, 0)])


def _seen_out34(pts):
    seen, out = set(), []
    for p in pts:
        out.append(f"{_pt34(*p)} {'repeat' if p in seen else 'new'}")
        seen.add(p)
    return _nl(*out, len(seen))


_RANGE34 = """
record Range(int lo, int hi) {
    Range {
        if (lo > hi) {
            int t = lo;
            lo = hi;
            hi = t;
        }
    }

    int length() {
        return hi - lo;
    }
}
"""

_RANGES34 = ([(2, 5)], [(9, 3)], [(4, 4), (8, 1)], [(-5, 5), (5, -5)], [(0, 100), (100, 0), (7, 6)])


def _range_out34(rows):
    out = []
    for (a, b) in rows:
        lo, hi = min(a, b), max(a, b)
        out.append(f"{_rec34('Range', lo=lo, hi=hi)} {hi - lo}")
    return _nl(*out)


_FRACTION34 = """
record Fraction(int num, int den) {
    Fraction {
        if (den == 0) {
            throw new IllegalArgumentException("zero denominator");
        }
        if (den < 0) {
            num = -num;
            den = -den;
        }
        int g = gcd(Math.abs(num), den);
        num /= g;
        den /= g;
    }

    static int gcd(int a, int b) {
        return b == 0 ? a : gcd(b, a % b);
    }

    Fraction plus(Fraction other) {
        return new Fraction(num * other.den + other.num * den, den * other.den);
    }
}
"""

_FRACTION_REGION34 = "\n".join(_FRACTION34.strip("\n").split("\n")[1:-1])

_FRACS34 = ([(1, 2, 1, 3)], [(1, 2, 1, 2), (3, 4, -1, 4)], [(2, -4, 0, 5)],
            [(5, 0, 1, 1), (-6, -8, 1, 4)], [(1, 3, 2, 3), (7, 10, -7, 10)])


def _frac34(n, d):
    if d == 0:
        return None
    if d < 0:
        n, d = -n, -d
    g = _math34.gcd(abs(n), d)
    return (n // g, d // g)


def _frac_out34(rows):
    out = []
    for (a, b, c, d) in rows:
        f1, f2 = _frac34(a, b), _frac34(c, d)
        if f1 is None or f2 is None:
            out.append("invalid")
            continue
        s = _frac34(f1[0] * f2[1] + f2[0] * f1[1], f1[1] * f2[1])
        out.append(_rec34("Fraction", num=s[0], den=s[1]))
    return _nl(*out)


_M34.append(_jlesson(
    "m34-records", "Records: a class that is just its data",
    "One line instead of forty - and a compact constructor for the rules.",
    """
Module 13 wrote a `Point` by hand: two private final fields, a constructor,
two getters, `equals`, `hashCode` and `toString`. Forty-odd lines, and every one
of them follows mechanically from "a point is an x and a y". A **record** says
exactly that, and the compiler writes the rest:

```java
record Point(int x, int y) {}
```

From that one line you get:

* a **private final field** for each component, and a **canonical constructor**
  taking them in order: `new Point(1, 2)`;
* an **accessor** per component, named after it - `p.x()`, not `p.getX()`;
* **`equals` and `hashCode`** comparing every component, so two points with the
  same coordinates are equal, and work as keys in a `HashMap` or members of a
  `HashSet`;
* **`toString`**: `Point[x=1, y=2]`.

A record is **final** (nothing can extend it), cannot extend another class (it
already extends `java.lang.Record`), and cannot declare extra instance fields.
It *can* have methods, static fields and factories, and implement interfaces.

## The compact constructor

Rules still need somewhere to live. A record can declare its constructor in
**compact** form - no parameter list, no field assignments:

```java
record Range(int lo, int hi) {
    Range {
        if (lo > hi) {           // validate or normalise the PARAMETERS...
            int t = lo;
            lo = hi;
            hi = t;
        }
    }                            // ...and the fields are assigned from them here
}
```

Inside it, `lo` and `hi` are the constructor's **parameters**, and you may
reassign them; the compiler assigns the fields from them when the body ends.
Writing `this.lo = ...` yourself is a compile error - the field is final and the
compiler is about to assign it. This is where a record's invariants live: throw
to reject, reassign to normalise.

## When to use one

A record is right when a class *is* its data: a point, a range, a money amount,
a key made of several parts, a row from a query, a message between two parts
of a program. It is wrong when an object has identity and changing state - a
bank account, a game character - because every record is a value, equal to any
other with the same components.
""",
    warmup=[
        _jq("For `record Point(int x, int y) {}`, the accessor for x is…",
            ["p.x()", "p.getX()", "p.x", "Point.x(p)"],
            0,
            "Accessors are named after the components, without `get`."),
        _jq("Two separately constructed `new Point(1, 2)` records are…",
            ["equal by equals(), and not ==", "== and equal", "neither", "== but not equal"],
            0,
            "equals compares components; == compares references."),
    ],
    exercises=[
        _je("j34-rc-declare", "One line of data",
            "Declare `Point` as a record of two ints, `x` and `y`, so `main` can print each "
            "point and the sum of its coordinates. Replace `____` with the declaration.",
            _j34t("record Point(int x, int y) {}\n",
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  "            System.out.println(p + \" \" + (p.x() + p.y()));\n"
                  "        }"),
            "record Point(int x, int y) {}",
            [_rows34(pts, _nl(*[f"{_pt34(x, y)} {x + y}" for (x, y) in pts])) for pts in _POINTS34],
            hints=["`record Name(components) {}`",
                   "The components are `int x, int y`.",
                   "The empty braces are the (empty) body.",
                   "The constructor, accessors and `toString` all come for free."],
            difficulty="Easy"),

        _je("j34-rc-equals", "Equal by value",
            "Report whether each point has been seen before, then how many distinct points "
            "there were. Replace `____` with the call that both records the point and says "
            "whether it was new.",
            _j34t("record Point(int x, int y) {}\n",
                  "        int n = sc.nextInt();\n"
                  "        Set<Point> seen = new HashSet<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Point p = new Point(sc.nextInt(), sc.nextInt());\n"
                  "            boolean fresh = seen.add(p);\n"
                  "            System.out.println(p + (fresh ? \" new\" : \" repeat\"));\n"
                  "        }\n"
                  "        System.out.println(seen.size());"),
            "seen.add(p)",
            [_rows34(pts, _seen_out34(pts)) for pts in _SEEN34],
            hints=["`Set.add` returns `false` when an equal element was already there.",
                   "`seen.add(p)`",
                   "Every point is a NEW object - it is the record's value-based `equals` and "
                   "`hashCode` that make repeats count as repeats.",
                   "With a plain class and no `equals`, every line would say `new`."],
            difficulty="Easy"),

        _jfix("j34-rc-compact", "Assigning the field yourself",
              "`Range` should swap its ends when they arrive backwards, but its compact "
              "constructor assigns the fields directly - which does not compile. Normalise "
              "the parameters instead.",
              _j34t(_RANGE34.replace(
                  "            int t = lo;\n            lo = hi;\n            hi = t;\n",
                  "            this.lo = hi;\n            this.hi = lo;\n"),
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Range r = new Range(sc.nextInt(), sc.nextInt());\n"
                  "            System.out.println(r + \" \" + r.length());\n"
                  "        }"),
              _j34t(_RANGE34,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Range r = new Range(sc.nextInt(), sc.nextInt());\n"
                    "            System.out.println(r + \" \" + r.length());\n"
                    "        }"),
              [_rows34(rows, _range_out34(rows)) for rows in _RANGES34],
              hints=["In a compact constructor, `lo` and `hi` are PARAMETERS.",
                     "The compiler assigns the final fields from them after the body - so "
                     "you may not assign the fields yourself.",
                     "Swap the parameters with a temporary variable.",
                     "`int t = lo; lo = hi; hi = t;`"],
              difficulty="Medium"),

        _jch("j34-rc-fraction", "A fraction that keeps itself tidy", "Hard",
             "Write the body of `record Fraction(int num, int den)`: a compact constructor "
             "that rejects a zero denominator with `IllegalArgumentException`, moves any "
             "minus sign to the numerator, and reduces by the greatest common divisor; a "
             "static `gcd`; and `plus(other)`. `main` adds pairs and prints the sums.",
             _j34t(_FRACTION34,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            int a = sc.nextInt(), b = sc.nextInt(), c = sc.nextInt(), d = sc.nextInt();\n"
                   "            try {\n"
                   "                System.out.println(new Fraction(a, b).plus(new Fraction(c, d)));\n"
                   "            } catch (IllegalArgumentException e) {\n"
                   "                System.out.println(\"invalid\");\n"
                   "            }\n"
                   "        }"),
             _FRACTION_REGION34,
             [_rows34(rows, _frac_out34(rows)) for rows in _FRACS34],
             hints=["The compact constructor is `Fraction { ... }` - no parameter list.",
                    "Throw first; then `if (den < 0) { num = -num; den = -den; }`.",
                    "Divide both by `gcd(Math.abs(num), den)`; `gcd(0, d)` is `d`, so zero "
                    "becomes `0/1`.",
                    "A record may have static methods: `static int gcd(int a, int b)`.",
                    "`plus` builds a new Fraction - the constructor reduces it for free.",
                    "Because every Fraction is reduced on the way in, `equals` compares "
                    "values correctly: 1/2 equals 2/4."]),
    ],
    quiz=[
        _jq("Inside a compact constructor, `this.lo = hi;` is…",
            ["a compile error - the compiler assigns the fields itself",
             "the normal way to set a field", "ignored", "a runtime error"],
            0,
            "Reassign the parameters; the fields are assigned from them afterwards."),
        _jq("A record is a poor fit for…",
            ["an object with identity and changing state, like a bank account",
             "a point", "a composite map key", "a message between components"],
            0,
            "Records are values: equal whenever their components are."),
    ],
))


# ===========================================================================
# 34.2 Records in practice
# ===========================================================================

_TEAM34 = """
record Team(String name, List<String> members) {
    Team {
        members = List.copyOf(members);
    }
}
"""

_TEAMS34 = (("lions", ["ada", "bo"]), ("owls", ["cy"]), ("foxes", ["x", "y", "z"]),
            ("bees", []), ("crows", ["pear", "fig"]))


def _team_out34(name, ms):
    return _nl(_rec34("Team", name=name, members=_jarr(ms)), len(ms), len(ms) + 1)


_SCORE34 = """
record Score(String name, int points) implements Comparable<Score> {
    @Override
    public int compareTo(Score other) {
        if (points != other.points) {
            return Integer.compare(other.points, points);
        }
        return name.compareTo(other.name);
    }
}
"""

_SCORES34 = ([("ada", 90), ("bo", 95)], [("solo", 1)], [("c", 5), ("a", 5), ("b", 7)],
             [("x", 0), ("y", -1), ("z", 0)], [("pear", 10), ("fig", 30), ("plum", 20)])


def _scores_out34(rows):
    ordered = sorted(rows, key=lambda r: (-r[1], r[0]))
    return _nl(*[_rec34("Score", name=n, points=p) for (n, p) in ordered])


_CELLS34 = ([(0, 0), (0, 1), (0, 0)], [(2, 2)], [(1, 0), (0, 1), (1, 0), (0, 1), (1, 0)],
            [(5, 5), (5, 5), (5, 5)], [(0, 0), (1, 1), (2, 2), (1, 1)])


def _cells_out34(cells):
    counts = {}
    for c in cells:
        counts[c] = counts.get(c, 0) + 1
    return "{" + ", ".join(f"{_rec34('Cell', row=r, col=c)}={n}"
                           for ((r, c), n) in counts.items()) + "}"


_MONEY34 = """
record Money(String currency, long cents) {
    Money {
        Objects.requireNonNull(currency, "currency");
    }

    Money plus(Money other) {
        if (!currency.equals(other.currency)) {
            throw new IllegalArgumentException(other.currency);
        }
        return new Money(currency, cents + other.cents);
    }

    @Override
    public String toString() {
        return String.format(Locale.ROOT, "%s %d.%02d", currency, cents / 100, cents % 100);
    }
}
"""

_MONEY_REGION34 = (
    "    Money plus(Money other) {\n"
    "        if (!currency.equals(other.currency)) {\n"
    "            throw new IllegalArgumentException(other.currency);\n"
    "        }\n"
    "        return new Money(currency, cents + other.cents);\n"
    "    }\n"
    "\n"
    "    @Override\n"
    "    public String toString() {\n"
    "        return String.format(Locale.ROOT, \"%s %d.%02d\", currency, cents / 100, cents % 100);\n"
    "    }"
)

_WALLETS34 = ([("EUR", 150), ("EUR", 275)], [("USD", 5)], [("GBP", 1000), ("EUR", 1), ("GBP", 99)],
              [("JPY", 0), ("JPY", 0)], [("CHF", 1999), ("CHF", 1), ("USD", 50), ("CHF", 100)])


def _money34(cur, cents):
    return f"{cur} {cents // 100}.{cents % 100:02d}"


def _wallet_out34(rows):
    cur, total = rows[0]
    out = []
    for (c, v) in rows[1:]:
        if c != cur:
            out.append(f"mismatch: {c}")
        else:
            total += v
    out.append(_money34(cur, total))
    return _nl(*out)


_M34.append(_jlesson(
    "m34-practice", "Records in practice",
    "Shallow immutability, records as keys, and a record with rules of its own.",
    """
## A record is only as immutable as its components

Every field of a record is `final`, so a record can never be pointed at a
different list. But the *list itself* can still change:

```java
record Team(String name, List<String> members) {}

List<String> people = new ArrayList<>(List.of("ada", "bo"));
Team t = new Team("lions", people);
people.add("late");            // t.members() now has three people!
```

`final` makes the *reference* unchangeable, not the object it refers to - the
same shallow copy trap as module 12's defensive copying. The fix belongs in the
compact constructor:

```java
record Team(String name, List<String> members) {
    Team {
        members = List.copyOf(members);   // an unmodifiable snapshot
    }
}
```

`List.copyOf` (Java 10) returns an **unmodifiable** copy: later changes to the
caller's list do not reach it, and `t.members().add(...)` throws
`UnsupportedOperationException` instead of quietly changing a "value". (It also
rejects null elements, which is usually what you want.) `Set.copyOf` and
`Map.copyOf` do the same for sets and maps.

## Records as keys

Because `equals` and `hashCode` compare components, a record is the natural
**composite key**:

```java
record Cell(int row, int col) {}
Map<Cell, Integer> visits = new LinkedHashMap<>();
visits.merge(new Cell(r, c), 1, Integer::sum);
```

The old workaround - a `String` key like `r + "," + c` - works until someone
forgets the comma. A record key cannot be malformed.

## Records can implement interfaces, override methods, and add behaviour

```java
record Score(String name, int points) implements Comparable<Score> {
    public int compareTo(Score o) { ... }
}
record Money(String currency, long cents) {
    Money plus(Money other) { ... }          // returns a NEW Money
    @Override public String toString() { ... }
}
```

The one thing a record method never does is change the record: "modifying"
methods return a new one, exactly like `LocalDate.plusDays` in module 32. And if
you override `toString`, `equals` or `hashCode`, override them consistently - a
record's generated versions are usually what you want.
""",
    warmup=[
        _jq("A record has a `List<String>` component. After construction, the caller "
            "adds to the original list. The record's list…",
            ["changes too, unless the constructor copied it", "is unaffected - records are "
             "deeply immutable", "throws", "is null"],
            0,
            "`final` protects the reference, not the list."),
        _jq("`List.copyOf(list).add(\"x\")`…",
            ["throws UnsupportedOperationException", "adds x", "returns false",
             "does not compile"],
            0,
            "It is an unmodifiable snapshot."),
    ],
    exercises=[
        _jfix("j34-rp-copy", "The team that grew by itself",
              "The team is built, and THEN the caller adds `late` to its own list - and the "
              "team's members change too. Make the record take an unmodifiable snapshot in "
              "a compact constructor.",
              _j34t("record Team(String name, List<String> members) {}\n",
                    "        String name = sc.next();\n"
                    "        int n = sc.nextInt();\n"
                    "        List<String> people = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            people.add(sc.next());\n"
                    "        }\n"
                    "        Team team = new Team(name, people);\n"
                    "        people.add(\"late\");\n"
                    "        System.out.println(team);\n"
                    "        System.out.println(team.members().size());\n"
                    "        System.out.println(people.size());"),
              _j34t(_TEAM34,
                    "        String name = sc.next();\n"
                    "        int n = sc.nextInt();\n"
                    "        List<String> people = new ArrayList<>();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            people.add(sc.next());\n"
                    "        }\n"
                    "        Team team = new Team(name, people);\n"
                    "        people.add(\"late\");\n"
                    "        System.out.println(team);\n"
                    "        System.out.println(team.members().size());\n"
                    "        System.out.println(people.size());"),
              [_case(f"{t}\n{len(ms)}\n{' '.join(ms)}" if ms else f"{t}\n0\n",
                     _team_out34(t, ms)) for (t, ms) in _TEAMS34],
              hints=["The record holds the SAME list object the caller still has.",
                     "Give the record a compact constructor: `Team { ... }`.",
                     "`members = List.copyOf(members);` reassigns the parameter to a "
                     "snapshot.",
                     "The caller's list still grows - only the team's copy is protected."],
              difficulty="Medium"),

        _je("j34-rp-comparable", "Records that sort themselves",
            "`Score` implements `Comparable`: highest points first, then by name. Replace "
            "`____` with the comparison for the points.",
            _j34t(_SCORE34,
                  "        int n = sc.nextInt();\n"
                  "        List<Score> scores = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            scores.add(new Score(sc.next(), sc.nextInt()));\n"
                  "        }\n"
                  "        Collections.sort(scores);\n"
                  "        for (Score s : scores) {\n"
                  "            System.out.println(s);\n"
                  "        }"),
            "            return Integer.compare(other.points, points);",
            [_rows34(rows, _scores_out34(rows)) for rows in _SCORES34],
            hints=["Highest first means comparing the OTHER score's points with this one's.",
                   "`Integer.compare(other.points, points)` - never subtraction (module 20).",
                   "Inside the record, the private fields `points` and `other.points` are "
                   "accessible directly.",
                   "Ties fall through to `name.compareTo(other.name)`."],
            difficulty="Easy"),

        _je("j34-rp-key", "A composite key",
            "Count visits to each grid cell, keyed by a `Cell` record, and print the map in "
            "first-visit order. Replace `____` with the key.",
            _j34t("record Cell(int row, int col) {}\n",
                  "        int n = sc.nextInt();\n"
                  "        Map<Cell, Integer> visits = new LinkedHashMap<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            int r = sc.nextInt();\n"
                  "            int c = sc.nextInt();\n"
                  "            visits.merge(new Cell(r, c), 1, Integer::sum);\n"
                  "        }\n"
                  "        System.out.println(visits);"),
            "new Cell(r, c)",
            [_rows34(cells, _cells_out34(cells)) for cells in _CELLS34],
            hints=["A new `Cell` is built for every visit - and still finds the old entry.",
                   "That works because a record's `equals` and `hashCode` compare "
                   "components.",
                   "`new Cell(r, c)`",
                   "`LinkedHashMap` prints in insertion order, so the output is predictable."],
            difficulty="Easy"),

        _jch("j34-rp-money", "Money that refuses to mix", "Medium",
             "Write `Money.plus` - returning a NEW `Money`, and throwing "
             "`IllegalArgumentException` (with the other currency as its message) when the "
             "currencies differ - and override `toString` to print `EUR 1.50`. `main` sums "
             "the amounts, reporting any mismatch.",
             _j34t(_MONEY34,
                   "        int n = sc.nextInt();\n"
                   "        Money total = new Money(sc.next(), sc.nextLong());\n"
                   "        for (int i = 1; i < n; i++) {\n"
                   "            Money m = new Money(sc.next(), sc.nextLong());\n"
                   "            try {\n"
                   "                total = total.plus(m);\n"
                   "            } catch (IllegalArgumentException e) {\n"
                   "                System.out.println(\"mismatch: \" + e.getMessage());\n"
                   "            }\n"
                   "        }\n"
                   "        System.out.println(total);"),
             _MONEY_REGION34,
             [_rows34(rows, _wallet_out34(rows)) for rows in _WALLETS34],
             hints=["`plus` never changes `this` - it returns `new Money(currency, cents + "
                    "other.cents)`.",
                    "Compare currencies with `equals`.",
                    "`throw new IllegalArgumentException(other.currency);` - the message is "
                    "yours, so printing it is safe.",
                    "`toString` must be `public` to override `Object`'s.",
                    "`%02d` pads the cents: 5 cents is `0.05`."]),
    ],
    quiz=[
        _jq("The best place to copy a record's mutable component is…",
            ["its compact constructor", "every accessor", "the caller", "toString"],
            0,
            "Copy once on the way in; the record is then safe for its whole life."),
        _jq("Why is a record a better composite key than `r + \",\" + c`?",
            ["it cannot be malformed, and equality is by component",
             "it is shorter", "Strings cannot be keys", "it sorts itself"],
            0,
            "A String key is only as good as the code that builds it."),
    ],
))


# ===========================================================================
# 34.3 Pattern matching for instanceof
# ===========================================================================

# Tokens are typed values - `i:5`, `d:2.5`, `b:true`, `s:text` - parsed to an
# Integer, Double, Boolean or String behind an `Object`. An if chain with
# `valueOf` rather than a switch expression: a switch whose arms mix int and
# double can undergo numeric promotion, and a lesson about types should not
# depend on that rule.
_PARSE34 = (
    "    static Object parse(String token) {\n"
    "        String value = token.substring(2);\n"
    "        char kind = token.charAt(0);\n"
    "        if (kind == 'i') {\n"
    "            return Integer.valueOf(value);\n"
    "        }\n"
    "        if (kind == 'd') {\n"
    "            return Double.valueOf(value);\n"
    "        }\n"
    "        if (kind == 'b') {\n"
    "            return Boolean.valueOf(value);\n"
    "        }\n"
    "        return value;\n"
    "    }"
)

_OBJS34 = (["i:5", "s:hello"], ["d:2.5"], ["b:true", "i:-3", "s:x"], ["s:pattern", "d:0.5", "i:0"],
           ["b:false", "d:10.0", "s:ab", "i:21"])


def _pobj34(tok):
    kind, val = tok[0], tok[2:]
    if kind == "i":
        return ("int", int(val))
    if kind == "d":
        return ("dbl", float(val))
    if kind == "b":
        return ("bool", val == "true")
    return ("str", val)


def _describe34(tok):
    kind, v = _pobj34(tok)
    if kind == "int":
        return f"int doubled {v * 2}"
    if kind == "str":
        return f"string of length {len(v)}"
    if kind == "dbl":
        return f"double halved {_jd32(v / 2)}"
    return "something else"


def _numeric34(tok):
    kind, v = _pobj34(tok)
    if kind == "int":
        return f"{v} is an int"
    if kind == "dbl":
        return f"{_jd32(v)} is a double"
    return f"{tok[2:]} is not a number"


def _shout34(tok):
    kind, v = _pobj34(tok)
    return v.upper() + "!" if kind == "str" else "not text"


_PTCLS34 = """
class Point {
    private final int x;
    private final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
    }

    @Override
    public boolean equals(Object o) {
        return o instanceof Point p && x == p.x && y == p.y;
    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y);
    }
}
"""

_PTCLS_REGION34 = (
    "    @Override\n"
    "    public boolean equals(Object o) {\n"
    "        return o instanceof Point p && x == p.x && y == p.y;\n"
    "    }\n"
    "\n"
    "    @Override\n"
    "    public int hashCode() {\n"
    "        return Objects.hash(x, y);\n"
    "    }"
)

_PTPAIRS34 = ([((1, 2), (1, 2))], [((1, 2), (2, 1))], [((0, 0), (0, 0)), ((3, 4), (3, 5))],
              [((-1, -1), (-1, -1)), ((5, 5), (5, 5))], [((7, 0), (0, 7)), ((9, 9), (9, 9))])


def _ptpairs_case34(pairs):
    stdin = "\n".join([str(len(pairs))] + [f"{a[0]} {a[1]} {b[0]} {b[1]}" for (a, b) in pairs])
    distinct = set()
    lines = []
    for (a, b) in pairs:
        lines.append(_jbool(a == b))
        distinct.add(a)
        distinct.add(b)
    lines.append(len(distinct))
    return _case(stdin, _nl(*lines))


_M34.append(_jlesson(
    "m34-instanceof", "Pattern matching for `instanceof`",
    "Test and cast in one step - so the cast can never disagree with the test.",
    """
Module 13's downcast was always three steps, and the third one was a place for a
mistake to hide:

```java
if (o instanceof String) {          // 1. test
    String s = (String) o;          // 2. cast - repeating the type
    System.out.println(s.length()); // 3. use
}
```

Nothing forces step 2 to name the same type as step 1. Copy the block for
`Double` and forget to change the cast, and it compiles - and throws
`ClassCastException` at run time.

A **type pattern** (Java 16) does the test and the cast together, and binds the
result to a new variable:

```java
if (o instanceof String s) {
    System.out.println(s.length());
}
```

`s` exists only where the test is known to have succeeded. The cast cannot
disagree with the test because there is no separate cast.

## Flow scoping

The binding is in scope wherever the compiler can prove the match happened -
which includes *after* a negated test that returns:

```java
if (!(o instanceof String s)) {
    return "not text";
}
return s.toUpperCase();            // s is definitely a String here
```

and the rest of a `&&` chain:

```java
if (o instanceof String s && s.length() > 3) { ... }
```

(With `||` it is not in scope - the right-hand side runs precisely when the
match *failed*.)

## `equals`, in one line

The pattern was practically designed for `equals`:

```java
@Override
public boolean equals(Object o) {
    return o instanceof Point p && x == p.x && y == p.y;
}
```

`instanceof` is false for `null`, so the null check is built in too.
""",
    warmup=[
        _jq("In `if (o instanceof String s && s.isEmpty())`, the second `s`…",
            ["is in scope, because && only runs it after a match", "is a compile error",
             "may be null", "refers to a different variable"],
            0,
            "Flow scoping: s exists wherever the match is certain."),
        _jq("`null instanceof String s` is…",
            ["false, and s is not bound", "true", "a NullPointerException",
             "a compile error"],
            0,
            "instanceof is never true for null."),
    ],
    exercises=[
        _je("j34-pm-describe", "What is it?",
            "Each token is a typed value: `i:5` an Integer, `d:2.5` a Double, `b:true` a "
            "Boolean and `s:text` a String. Describe each one. Replace `____` with the "
            "String test that also binds `s`.",
            _j34th("", _PARSE34 + "\n\n"
                   "    static String describe(Object o) {\n"
                   "        if (o instanceof Integer i) {\n"
                   "            return \"int doubled \" + (i * 2);\n"
                   "        } else if (o instanceof String s) {\n"
                   "            return \"string of length \" + s.length();\n"
                   "        } else if (o instanceof Double d) {\n"
                   "            return \"double halved \" + (d / 2);\n"
                   "        }\n"
                   "        return \"something else\";\n"
                   "    }",
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            System.out.println(describe(parse(sc.next())));\n"
                   "        }"),
            "o instanceof String s",
            [_toks34(ts, _nl(*[_describe34(t) for t in ts])) for ts in _OBJS34],
            hints=["`o instanceof String s` tests and binds in one go.",
                   "`s` is then a `String` inside that branch - no cast.",
                   "A Boolean matches none of the three patterns.",
                   "The other two branches show the same shape for Integer and Double."],
            difficulty="Easy"),

        _jfix("j34-pm-cast", "The cast that disagreed with the test",
              "The Double branch was copied from the Integer branch and still casts to "
              "`Integer` - so it compiles, then throws `ClassCastException` for every double. "
              "Rewrite both branches with type patterns so there is no separate cast to get "
              "wrong.",
              _j34th("", _PARSE34 + "\n\n"
                     "    static String numeric(Object o) {\n"
                     "        if (o instanceof Integer) {\n"
                     "            Integer n = (Integer) o;\n"
                     "            return n + \" is an int\";\n"
                     "        } else if (o instanceof Double) {\n"
                     "            Integer n = (Integer) o;\n"
                     "            return n + \" is a double\";\n"
                     "        }\n"
                     "        return o + \" is not a number\";\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            System.out.println(numeric(parse(sc.next())));\n"
                     "        }"),
              _j34th("", _PARSE34 + "\n\n"
                     "    static String numeric(Object o) {\n"
                     "        if (o instanceof Integer n) {\n"
                     "            return n + \" is an int\";\n"
                     "        } else if (o instanceof Double d) {\n"
                     "            return d + \" is a double\";\n"
                     "        }\n"
                     "        return o + \" is not a number\";\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            System.out.println(numeric(parse(sc.next())));\n"
                     "        }"),
              [_toks34(ts, _nl(*[_numeric34(t) for t in ts])) for ts in _OBJS34],
              hints=["`(Integer) o` on a Double compiles - the compiler only knows `o` is an "
                     "Object.",
                     "`o instanceof Double d` gives you `d` already typed as a Double.",
                     "With a pattern there is no cast left to disagree with the test.",
                     "A Double prints as `2.5`, an Integer as `5`."],
              difficulty="Easy"),

        _je("j34-pm-flow", "Bail out early",
            "Shout any String (upper-case plus `!`); anything else is `not text`. Replace "
            "`____` with the NEGATED pattern test that returns early.",
            _j34th("", _PARSE34 + "\n\n"
                   "    static String shout(Object o) {\n"
                   "        if (!(o instanceof String s)) {\n"
                   "            return \"not text\";\n"
                   "        }\n"
                   "        return s.toUpperCase() + \"!\";\n"
                   "    }",
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            System.out.println(shout(parse(sc.next())));\n"
                   "        }"),
            "!(o instanceof String s)",
            [_toks34(ts, _nl(*[_shout34(t) for t in ts])) for ts in _OBJS34],
            hints=["`!(o instanceof String s)` is true when `o` is NOT a String.",
                   "The `if` returns in that case - so after it, the match must have "
                   "happened.",
                   "That is why `s` is in scope on the last line: flow scoping.",
                   "The parentheses around the `instanceof` are required."],
            difficulty="Medium"),

        _jch("j34-pm-equals", "`equals` in one line", "Medium",
             "`Point` is an ordinary class (not a record). Write its `equals` with a type "
             "pattern, and a matching `hashCode`. `main` compares pairs of points and "
             "counts the distinct ones in a `HashSet`.",
             _j34t(_PTCLS34,
                   "        int n = sc.nextInt();\n"
                   "        Set<Point> distinct = new HashSet<>();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Point a = new Point(sc.nextInt(), sc.nextInt());\n"
                   "            Point b = new Point(sc.nextInt(), sc.nextInt());\n"
                   "            System.out.println(a.equals(b));\n"
                   "            distinct.add(a);\n"
                   "            distinct.add(b);\n"
                   "        }\n"
                   "        System.out.println(distinct.size());"),
             _PTCLS_REGION34,
             [_ptpairs_case34(p) for p in _PTPAIRS34],
             hints=["`return o instanceof Point p && x == p.x && y == p.y;`",
                    "`instanceof` is false for null, so no separate null check is needed.",
                    "`p.x` is readable here: private means private to the CLASS, not the "
                    "object.",
                    "`hashCode` must use the same fields: `Objects.hash(x, y)`.",
                    "Without `hashCode`, the HashSet would count equal points twice."]),
    ],
    quiz=[
        _jq("The main safety gain of `o instanceof String s` over test-then-cast is…",
            ["the cast can no longer name a different type from the test",
             "it is faster", "it allows null", "it avoids boxing"],
            0,
            "There is no separate cast to get wrong."),
        _jq("After `if (!(o instanceof Point p)) return false;`, the variable p…",
            ["is in scope and definitely a Point", "is out of scope", "may be null",
             "is a compile error"],
            0,
            "The early return proves the match."),
    ],
))


# ===========================================================================
# 34.4 Sealed types
# ===========================================================================

_SHAPES34 = """
sealed interface Shape permits Square, Rect, Triangle {}

record Square(int side) implements Shape {}

record Rect(int w, int h) implements Shape {}

record Triangle(int base, int height) implements Shape {}
"""

_AREA_IF34 = (
    "    static int area(Shape s) {\n"
    "        if (s instanceof Square q) {\n"
    "            return q.side() * q.side();\n"
    "        } else if (s instanceof Rect r) {\n"
    "            return r.w() * r.h();\n"
    "        } else if (s instanceof Triangle t) {\n"
    "            return t.base() * t.height() / 2;\n"
    "        }\n"
    "        throw new IllegalStateException();\n"
    "    }"
)

_READSHAPE34 = (
    "    static Shape read(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        return switch (kind) {\n"
    "            case \"square\" -> new Square(sc.nextInt());\n"
    "            case \"rect\" -> new Rect(sc.nextInt(), sc.nextInt());\n"
    "            default -> new Triangle(sc.nextInt(), sc.nextInt());\n"
    "        };\n"
    "    }"
)

_SHAPEROWS34 = ([("square", 3), ("rect", 2, 5)], [("triangle", 4, 3)],
                [("rect", 1, 1), ("square", 0), ("triangle", 5, 5)], [("square", 10)],
                [("triangle", 7, 2), ("rect", 3, 4), ("square", 6)])


def _shape34(row):
    k = row[0]
    if k == "square":
        return _rec34("Square", side=row[1]), row[1] * row[1]
    if k == "rect":
        return _rec34("Rect", w=row[1], h=row[2]), row[1] * row[2]
    return _rec34("Triangle", base=row[1], height=row[2]), row[1] * row[2] // 2


def _shapes_out34(rows):
    return _nl(*[f"{_shape34(r)[0]} {_shape34(r)[1]}" for r in rows])


_DOTSHAPES34 = """
sealed interface Shape permits Square, Rect, Dot {}

record Square(int side) implements Shape {}

record Rect(int w, int h) implements Shape {}

record Dot() implements Shape {}
"""

_DOTROWS34 = ([("square", 3), ("dot",)], [("dot",)], [("rect", 2, 5), ("dot",), ("square", 1)],
              [("rect", 4, 4)], [("dot",), ("dot",), ("square", 2)])


def _dot_out34(rows):
    out = []
    for r in rows:
        if r[0] == "dot":
            out.append("Dot[] 0")
        else:
            out.append(f"{_shape34(r)[0]} {_shape34(r)[1]}")
    return _nl(*out)


_VEHICLES34 = """
sealed abstract class Vehicle permits Car, Truck {
    abstract int wheels();
}

final class Car extends Vehicle {
    int wheels() {
        return 4;
    }
}

non-sealed class Truck extends Vehicle {
    int wheels() {
        return 6;
    }
}

class DumpTruck extends Truck {
    @Override
    int wheels() {
        return 10;
    }
}
"""

_VTOKS34 = (["car", "truck"], ["dump"], ["dump", "car", "car"], ["truck", "truck"],
            ["car", "dump", "truck", "car"])
_WHEELS34 = {"car": 4, "truck": 6, "dump": 10}

_PAYMENTS34 = """
sealed interface Payment permits Card, Cash, Voucher {}

record Card(String last4, int cents) implements Payment {}

record Cash(int cents) implements Payment {}

record Voucher(String code, int percentOff) implements Payment {}
"""

_PAYMENTS_REGION34 = (
    "record Card(String last4, int cents) implements Payment {}\n"
    "\n"
    "record Cash(int cents) implements Payment {}\n"
    "\n"
    "record Voucher(String code, int percentOff) implements Payment {}"
)

_PAYROWS34 = ([("card", "4242", 1999), ("cash", 500)], [("voucher", "SPRING", 15)],
              [("cash", 1), ("card", "0001", 100), ("voucher", "X", 100)],
              [("card", "9999", 0)], [("voucher", "HALF", 50), ("cash", 250)])


def _pay_out34(rows):
    out = []
    for r in rows:
        if r[0] == "card":
            out.append(f"card ending {r[1]}: {r[2]} cents")
        elif r[0] == "cash":
            out.append(f"cash: {r[1]} cents")
        else:
            out.append(f"voucher {r[1]}: {r[2]}% off")
    return _nl(*out)


_M34.append(_jlesson(
    "m34-sealed", "Sealed types: a hierarchy the compiler can see all of",
    "`permits` lists every subtype - so \"which kinds are there?\" has an answer.",
    """
An interface is normally open: anyone, anywhere, can implement it. That is the
point of an interface - and the problem, when what you are modelling really is
a closed set:

* a shape is a square, a rectangle or a triangle;
* a payment is by card, in cash or by voucher;
* an expression is a number, a sum, a product or a negation.

A **sealed** type (Java 17) lists its permitted subtypes, and nothing else may
extend or implement it:

```java
sealed interface Shape permits Square, Rect, Triangle {}

record Square(int side) implements Shape {}
record Rect(int w, int h) implements Shape {}
record Triangle(int base, int height) implements Shape {}
```

Try to add `record Circle(int r) implements Shape {}` without listing it, and the
**compiler** rejects it. So the compiler, and every reader, knows the complete
list of shapes - which is exactly what lesson 34.5 needs to check that a switch
covers them all.

## What the permitted subtypes must say

Each permitted subtype must declare how *it* continues the hierarchy - one of:

| modifier | meaning |
|---|---|
| `final` | nothing extends me (records are implicitly final) |
| `sealed ... permits ...` | a closed list extends me, in turn |
| `non-sealed` | I am open again: anyone may extend me |

```java
sealed abstract class Vehicle permits Car, Truck { abstract int wheels(); }
final class Car extends Vehicle { ... }
non-sealed class Truck extends Vehicle { ... }
class DumpTruck extends Truck { ... }        // allowed: Truck re-opened it
```

`non-sealed` is the escape hatch for a branch you genuinely want extensible;
`DumpTruck` is still a `Vehicle`, reached through `Truck`.

## Records and sealed interfaces together

Records are the natural leaves of a sealed hierarchy: each case is *just its
data*, and the sealed interface says *these are all the cases*. This pairing -
sometimes called an **algebraic data type** - is how modern Java models "one of
several shapes of data", where older Java would have used a class hierarchy with
an abstract method, or a class with a `type` field and a pile of nullable fields
that only some types use.
""",
    warmup=[
        _jq("A class not listed in `permits` tries to implement a sealed interface. "
            "The result is…",
            ["a compile error", "a runtime exception", "a warning", "it works"],
            0,
            "The list is enforced by the compiler."),
        _jq("A permitted subclass of a sealed class must be declared…",
            ["final, sealed or non-sealed", "abstract", "public", "static"],
            0,
            "It has to say how the hierarchy continues below it. Records are "
            "implicitly final."),
    ],
    exercises=[
        _je("j34-se-permits", "Closing the hierarchy",
            "Make `Shape` a sealed interface permitting exactly `Square`, `Rect` and "
            "`Triangle`. `main` reads shapes and prints each with its area. Replace `____` "
            "with the permits clause.",
            _j34th(_SHAPES34, _READSHAPE34 + "\n\n" + _AREA_IF34,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Shape s = read(sc);\n"
                   "            System.out.println(s + \" \" + area(s));\n"
                   "        }"),
            "permits Square, Rect, Triangle",
            [_rows34(rows, _shapes_out34(rows)) for rows in _SHAPEROWS34],
            hints=["`sealed interface Shape permits A, B, C {}`",
                   "List the three record names.",
                   "Records are implicitly final, which satisfies the rule that a permitted "
                   "subtype must say how the hierarchy continues.",
                   "The instanceof chain still needs a `throw` at the end - lesson 34.5's "
                   "switch will not."],
            difficulty="Easy"),

        _jfix("j34-se-outside", "The shape nobody permitted",
              "`Dot` implements `Shape`, but `Shape`'s `permits` list does not mention it, "
              "so nothing compiles. Add it to the list (the rest of the program already "
              "handles dots).",
              _j34th(_DOTSHAPES34.replace("permits Square, Rect, Dot", "permits Square, Rect"),
                     "    static Shape read(Scanner sc) {\n"
                     "        String kind = sc.next();\n"
                     "        return switch (kind) {\n"
                     "            case \"square\" -> new Square(sc.nextInt());\n"
                     "            case \"rect\" -> new Rect(sc.nextInt(), sc.nextInt());\n"
                     "            default -> new Dot();\n"
                     "        };\n"
                     "    }\n"
                     "\n"
                     "    static int area(Shape s) {\n"
                     "        if (s instanceof Square q) {\n"
                     "            return q.side() * q.side();\n"
                     "        } else if (s instanceof Rect r) {\n"
                     "            return r.w() * r.h();\n"
                     "        }\n"
                     "        return 0;\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            Shape s = read(sc);\n"
                     "            System.out.println(s + \" \" + area(s));\n"
                     "        }"),
              _j34th(_DOTSHAPES34,
                     "    static Shape read(Scanner sc) {\n"
                     "        String kind = sc.next();\n"
                     "        return switch (kind) {\n"
                     "            case \"square\" -> new Square(sc.nextInt());\n"
                     "            case \"rect\" -> new Rect(sc.nextInt(), sc.nextInt());\n"
                     "            default -> new Dot();\n"
                     "        };\n"
                     "    }\n"
                     "\n"
                     "    static int area(Shape s) {\n"
                     "        if (s instanceof Square q) {\n"
                     "            return q.side() * q.side();\n"
                     "        } else if (s instanceof Rect r) {\n"
                     "            return r.w() * r.h();\n"
                     "        }\n"
                     "        return 0;\n"
                     "    }",
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            Shape s = read(sc);\n"
                     "            System.out.println(s + \" \" + area(s));\n"
                     "        }"),
              [_rows34(rows, _dot_out34(rows)) for rows in _DOTROWS34],
              hints=["Read the compiler's complaint: `Dot` is not allowed in the sealed "
                     "hierarchy.",
                     "A sealed type's subtypes are exactly the ones it lists.",
                     "`permits Square, Rect, Dot`",
                     "A record with no components prints as `Dot[]`."],
              difficulty="Easy"),

        _je("j34-se-nonsealed", "Opening one branch again",
            "`Vehicle` is sealed, `Car` is final, and `DumpTruck` extends `Truck` - which "
            "only compiles if `Truck` re-opens the hierarchy. Replace `____` with the "
            "modifier that does that.",
            _j34t(_VEHICLES34,
                  "        int n = sc.nextInt();\n"
                  "        int total = 0;\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String kind = sc.next();\n"
                  "            Vehicle v = kind.equals(\"car\") ? new Car()\n"
                  "                    : kind.equals(\"truck\") ? new Truck() : new DumpTruck();\n"
                  "            System.out.println(kind + \" \" + v.wheels());\n"
                  "            total += v.wheels();\n"
                  "        }\n"
                  "        System.out.println(total);"),
            "non-sealed",
            [_toks34(ts, _nl(*[f"{t} {_WHEELS34[t]}" for t in ts],
                             sum(_WHEELS34[t] for t in ts))) for ts in _VTOKS34],
            hints=["A permitted subclass must be `final`, `sealed` or `non-sealed`.",
                   "`final` would forbid `DumpTruck`.",
                   "`non-sealed class Truck extends Vehicle` lets anyone extend Truck.",
                   "`DumpTruck` is still a `Vehicle` - reached through the open branch."],
            difficulty="Easy"),

        _jch("j34-se-payment", "Three ways to pay", "Medium",
             "`Payment` is sealed and permits `Card`, `Cash` and `Voucher`. Write the three "
             "records: a Card has `last4` (a String) and `cents`; Cash has `cents`; a "
             "Voucher has a `code` and `percentOff`. `main` describes each payment.",
             _j34th(_PAYMENTS34,
                    "    static String describe(Payment p) {\n"
                    "        if (p instanceof Card c) {\n"
                    "            return \"card ending \" + c.last4() + \": \" + c.cents() + \" cents\";\n"
                    "        } else if (p instanceof Cash c) {\n"
                    "            return \"cash: \" + c.cents() + \" cents\";\n"
                    "        } else if (p instanceof Voucher v) {\n"
                    "            return \"voucher \" + v.code() + \": \" + v.percentOff() + \"% off\";\n"
                    "        }\n"
                    "        throw new IllegalStateException();\n"
                    "    }",
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String kind = sc.next();\n"
                    "            Payment p = switch (kind) {\n"
                    "                case \"card\" -> new Card(sc.next(), sc.nextInt());\n"
                    "                case \"cash\" -> new Cash(sc.nextInt());\n"
                    "                default -> new Voucher(sc.next(), sc.nextInt());\n"
                    "            };\n"
                    "            System.out.println(describe(p));\n"
                    "        }"),
             _PAYMENTS_REGION34,
             [_rows34(rows, _pay_out34(rows)) for rows in _PAYROWS34],
             hints=["Each is `record Name(components) implements Payment {}`.",
                    "`last4` is a String so leading zeros survive: `0001`.",
                    "The accessor names come from the component names - `describe` "
                    "already calls `last4()`, `cents()`, `code()` and `percentOff()`.",
                    "No `final` needed: records are implicitly final."]),
    ],
    quiz=[
        _jq("Why seal an interface whose implementations are all known?",
            ["so the compiler knows the complete list, and can check a switch covers it",
             "for speed", "so it can have fields", "so it can be instantiated"],
            0,
            "Lesson 34.5 cashes this in."),
        _jq("`non-sealed` on a permitted subclass means…",
            ["anyone may extend that subclass", "nothing may extend it",
             "it is abstract", "it is not part of the hierarchy"],
            0,
            "An explicit escape hatch for one branch."),
    ],
))


# ===========================================================================
# 34.5 Pattern matching in switch
# ===========================================================================

_AREA_SW34 = (
    "    static int area(Shape s) {\n"
    "        return switch (s) {\n"
    "            case Square q -> q.side() * q.side();\n"
    "            case Rect(int w, int h) -> w * h;\n"
    "            case Triangle(int b, int h) -> b * h / 2;\n"
    "        };\n"
    "    }"
)

_LABEL_OK34 = (
    "    static String label(Shape s) {\n"
    "        return switch (s) {\n"
    "            case Square q when q.side() == 0 -> \"empty square\";\n"
    "            case Square q -> \"square\";\n"
    "            case Rect(int w, int h) when w == h -> \"square-ish rect\";\n"
    "            case Rect r -> \"rect\";\n"
    "            case Triangle t -> \"triangle\";\n"
    "        };\n"
    "    }"
)

_LABEL_BAD34 = (
    "    static String label(Shape s) {\n"
    "        return switch (s) {\n"
    "            case Square q -> \"square\";\n"
    "            case Square q when q.side() == 0 -> \"empty square\";\n"
    "            case Rect r -> \"rect\";\n"
    "            case Rect(int w, int h) when w == h -> \"square-ish rect\";\n"
    "            case Triangle t -> \"triangle\";\n"
    "        };\n"
    "    }"
)

_LABELROWS34 = ([("square", 0), ("square", 2)], [("rect", 3, 3)], [("rect", 2, 5), ("triangle", 1, 1)],
                [("square", 5), ("rect", 0, 0)], [("triangle", 4, 4), ("square", 0), ("rect", 1, 2)])


def _label34(row):
    k = row[0]
    if k == "square":
        return "empty square" if row[1] == 0 else "square"
    if k == "rect":
        return "square-ish rect" if row[1] == row[2] else "rect"
    return "triangle"


_NULLTOKS34 = (["i:5", "null", "i:-2"], ["s:hi"], ["null", "null"], ["i:0", "b:true", "s:x"],
               ["d:2.5", "i:100", "null"])


def _classify34(tok):
    if tok == "null":
        return "nothing"
    kind, v = _pobj34(tok)
    if kind == "int":
        return "positive int" if v > 0 else "other int"
    if kind == "str":
        return f"text {v}"
    return "something else"


_EXPR34 = """
sealed interface Expr permits Num, Add, Mul, Neg {}

record Num(int value) implements Expr {}

record Add(Expr left, Expr right) implements Expr {}

record Mul(Expr left, Expr right) implements Expr {}

record Neg(Expr inner) implements Expr {}
"""

_EXPR_PARSE34 = (
    "    static Expr parse(Scanner sc) {\n"
    "        String t = sc.next();\n"
    "        return switch (t) {\n"
    "            case \"add\" -> new Add(parse(sc), parse(sc));\n"
    "            case \"mul\" -> new Mul(parse(sc), parse(sc));\n"
    "            case \"neg\" -> new Neg(parse(sc));\n"
    "            default -> new Num(Integer.parseInt(t));\n"
    "        };\n"
    "    }"
)

_EXPR_REGION34 = (
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

_EXPRS34 = ("add 1 2", "mul add 1 2 3", "neg mul 4 add 5 6", "7",
            "add mul 2 3 neg add 1 mul 2 2")


def _parse_expr34(tokens):
    t = tokens.pop(0)
    if t in ("add", "mul"):
        a = _parse_expr34(tokens)
        b = _parse_expr34(tokens)
        return (t, a, b)
    if t == "neg":
        return ("neg", _parse_expr34(tokens))
    return ("num", int(t))


def _eval34(e):
    if e[0] == "num":
        return e[1]
    if e[0] == "add":
        return _eval34(e[1]) + _eval34(e[2])
    if e[0] == "mul":
        return _eval34(e[1]) * _eval34(e[2])
    return -_eval34(e[1])


def _show34(e):
    if e[0] == "num":
        return str(e[1])
    if e[0] == "add":
        return f"({_show34(e[1])} + {_show34(e[2])})"
    if e[0] == "mul":
        return f"({_show34(e[1])} * {_show34(e[2])})"
    return "-" + _show34(e[1])


def _expr_case34(src):
    e = _parse_expr34(src.split())
    return _case(src, _nl(_show34(e), _eval34(e)))


_M34.append(_jlesson(
    "m34-switch", "Pattern matching in `switch`",
    "Types, record deconstruction and guards as case labels - checked for completeness.",
    """
Lesson 34.4's `area` was an `instanceof` chain ending in a `throw` that could
never happen. Java 21 lets a `switch` match on **types**:

```java
static int area(Shape s) {
    return switch (s) {
        case Square q -> q.side() * q.side();
        case Rect(int w, int h) -> w * h;          // a RECORD pattern
        case Triangle(int b, int h) -> b * h / 2;
    };
}
```

No `default`, and no `throw`: `Shape` is sealed, the three cases cover every
permitted subtype, and the compiler knows it. Add a fourth shape and **this
switch stops compiling** until it handles it - lesson 33.3's exhaustiveness,
now for types instead of enum constants.

## Record patterns

`case Rect(int w, int h)` matches a `Rect` *and* takes it apart, binding its
components to new variables. Record patterns nest, so `case Add(Num(int a),
Num(int b))` matches "an addition of two plain numbers". This is
**deconstruction**: the record's constructor puts data together, and its pattern
takes it back apart.

## Guards

A `when` clause adds a condition:

```java
case Square q when q.side() == 0 -> "empty square";
case Square q -> "square";
```

Order now matters. Cases are tried top to bottom, and a case that can never be
reached is a compile error: an unguarded `case Square q` **dominates** a later
`case Square q when ...`, which could therefore never run. More specific cases
go first.

## `null`

A switch has always thrown `NullPointerException` on a null selector. A pattern
switch may handle it explicitly instead:

```java
return switch (o) {
    case null -> "nothing";
    case Integer i when i > 0 -> "positive int";
    case Integer i -> "other int";
    case String s -> "text " + s;
    default -> "something else";
};
```

Over `Object` - which is not sealed - a `default` is still needed.

## Why this matters

Sealed interface + records + pattern switch is a complete way to model data
with several shapes: the types say what the cases are, the records hold each
case's data, and the switch handles every case with the compiler checking
nothing was forgotten. The expression evaluator below is the classic example -
and the one interviewers use.
""",
    warmup=[
        _jq("A switch over a sealed interface covers every permitted subtype. It "
            "needs…",
            ["no default", "a default", "a throw after it", "a case null"],
            0,
            "The compiler knows the list is complete."),
        _jq("`case Square q` appears ABOVE `case Square q when q.side() == 0`. The "
            "result is…",
            ["a compile error: the guarded case is dominated", "the guard runs first",
             "both run", "a warning only"],
            0,
            "An unreachable case is an error. Specific cases go first."),
    ],
    exercises=[
        _je("j34-sp-area", "Taking a rectangle apart",
            "Compute areas with a pattern switch over the sealed `Shape`. Replace `____` "
            "with the arm that matches a `Rect` and binds its width and height directly.",
            _j34th(_SHAPES34, _READSHAPE34 + "\n\n" + _AREA_SW34,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Shape s = read(sc);\n"
                   "            System.out.println(s + \" \" + area(s));\n"
                   "        }"),
            "            case Rect(int w, int h) -> w * h;",
            [_rows34(rows, _shapes_out34(rows)) for rows in _SHAPEROWS34],
            hints=["A record pattern names the record and its components: `Rect(int w, int h)`.",
                   "The component variables can be named anything - they bind by position.",
                   "`case Rect(int w, int h) -> w * h;`",
                   "No `default`: the three cases cover the sealed interface."],
            difficulty="Easy"),

        _jfix("j34-sp-dominance", "The case that could never run",
              "The unguarded `case Square q` comes before the guarded one, so the guarded "
              "case can never match - and the compiler rejects the switch. The same mistake "
              "is made for `Rect`. Reorder the cases.",
              _j34th(_SHAPES34, _READSHAPE34 + "\n\n" + _LABEL_BAD34,
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            System.out.println(label(read(sc)));\n"
                     "        }"),
              _j34th(_SHAPES34, _READSHAPE34 + "\n\n" + _LABEL_OK34,
                     "        int n = sc.nextInt();\n"
                     "        for (int i = 0; i < n; i++) {\n"
                     "            System.out.println(label(read(sc)));\n"
                     "        }"),
              [_rows34(rows, _nl(*[_label34(r) for r in rows])) for rows in _LABELROWS34],
              hints=["Cases are tried top to bottom.",
                     "An unguarded `case Square q` matches EVERY square, so nothing below it "
                     "for squares is reachable.",
                     "Put each guarded case ABOVE the plain case for the same type.",
                     "The compiler calls this domination, and treats it as an error rather "
                     "than a warning."],
              difficulty="Medium"),

        _je("j34-sp-null", "A switch that expects null",
            "Classify each value (`null` in the input is a real null). Replace `____` with "
            "the arm that handles null - without it, the switch would throw "
            "`NullPointerException`.",
            _j34th("", _PARSE34 + "\n\n"
                   "    static String classify(Object o) {\n"
                   "        return switch (o) {\n"
                   "            case null -> \"nothing\";\n"
                   "            case Integer i when i > 0 -> \"positive int\";\n"
                   "            case Integer i -> \"other int\";\n"
                   "            case String s -> \"text \" + s;\n"
                   "            default -> \"something else\";\n"
                   "        };\n"
                   "    }",
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String token = sc.next();\n"
                   "            Object o = token.equals(\"null\") ? null : parse(token);\n"
                   "            System.out.println(classify(o));\n"
                   "        }"),
            "            case null -> \"nothing\";",
            [_toks34(ts, _nl(*[_classify34(t) for t in ts])) for ts in _NULLTOKS34],
            hints=["A pattern switch can have a `case null` arm.",
                   "`case null -> \"nothing\";`",
                   "Without it, a null selector throws NullPointerException before any "
                   "case is tried.",
                   "`Object` is not sealed, so the `default` is still needed."],
            difficulty="Easy"),

        _jch("j34-sp-expr", "An expression evaluator", "Hard",
             "An `Expr` is a `Num`, an `Add`, a `Mul` or a `Neg` - a sealed interface with "
             "four records. Write `eval` (its value) and `show` (fully parenthesised: `(1 + "
             "2)`, `(a * b)`, and `-x` for a negation), each as a pattern switch with "
             "record patterns. `main` parses prefix input like `mul add 1 2 3`.",
             _j34th(_EXPR34, _EXPR_PARSE34 + "\n\n" + _EXPR_REGION34,
                    "        Expr e = parse(sc);\n"
                    "        System.out.println(show(e));\n"
                    "        System.out.println(eval(e));"),
             _EXPR_REGION34,
             [_expr_case34(src) for src in _EXPRS34],
             hints=["`case Num(int v) -> v;`",
                    "`case Add(Expr l, Expr r) -> eval(l) + eval(r);` - the pattern binds "
                    "both sides, and the method recurses on them.",
                    "`case Neg(Expr inner) -> -eval(inner);`",
                    "No `default` in either switch: four records, four cases.",
                    "`show` builds the same shape with Strings: `\"(\" + show(l) + \" + \" + "
                    "show(r) + \")\"`.",
                    "Adding a `Sub` record later would break both switches at compile "
                    "time - which is the feature."]),
    ],
    quiz=[
        _jq("`case Rect(int w, int h)` is called…",
            ["a record pattern", "a type witness", "a guard", "a wildcard"],
            0,
            "It matches the type and deconstructs its components."),
        _jq("Over a non-sealed type such as `Object`, a pattern switch…",
            ["still needs a default", "needs no default", "cannot use guards",
             "cannot match null"],
            0,
            "Only a sealed hierarchy gives the compiler a complete list."),
    ],
))


# ===========================================================================
# Capstone - the ledger
# ===========================================================================

_TXN34 = """
sealed interface Txn permits Deposit, Withdrawal, Transfer {}

record Deposit(String account, int amount) implements Txn {}

record Withdrawal(String account, int amount) implements Txn {}

record Transfer(String from, String to, int amount) implements Txn {}
"""

_APPLY34 = (
    "    static String apply(Txn t, Map<String, Integer> balances) {\n"
    "        return switch (t) {\n"
    "            case Deposit d when d.amount() <= 0 -> \"rejected: non-positive\";\n"
    "            case Withdrawal w when w.amount() <= 0 -> \"rejected: non-positive\";\n"
    "            case Transfer x when x.amount() <= 0 -> \"rejected: non-positive\";\n"
    "            case Deposit(String account, int amount) -> {\n"
    "                balances.merge(account, amount, Integer::sum);\n"
    "                yield \"ok\";\n"
    "            }\n"
    "            case Withdrawal(String account, int amount) -> {\n"
    "                if (balances.getOrDefault(account, 0) < amount) {\n"
    "                    yield \"rejected: insufficient funds\";\n"
    "                }\n"
    "                balances.merge(account, -amount, Integer::sum);\n"
    "                yield \"ok\";\n"
    "            }\n"
    "            case Transfer(String from, String to, int amount) -> {\n"
    "                if (balances.getOrDefault(from, 0) < amount) {\n"
    "                    yield \"rejected: insufficient funds\";\n"
    "                }\n"
    "                balances.merge(from, -amount, Integer::sum);\n"
    "                balances.merge(to, amount, Integer::sum);\n"
    "                yield \"ok\";\n"
    "            }\n"
    "        };\n"
    "    }"
)

_READTXN34 = (
    "    static Txn read(Scanner sc) {\n"
    "        String kind = sc.next();\n"
    "        return switch (kind) {\n"
    "            case \"deposit\" -> new Deposit(sc.next(), sc.nextInt());\n"
    "            case \"withdraw\" -> new Withdrawal(sc.next(), sc.nextInt());\n"
    "            default -> new Transfer(sc.next(), sc.next(), sc.nextInt());\n"
    "        };\n"
    "    }"
)

_LEDGERS34 = (
    [("deposit", "ada", 100), ("withdraw", "ada", 30), ("transfer", "ada", "bo", 50),
     ("withdraw", "bo", 80)],
    [("deposit", "cy", 0), ("withdraw", "cy", 5), ("deposit", "cy", 5)],
    [("transfer", "x", "y", 10), ("deposit", "x", 10), ("transfer", "x", "y", 10),
     ("transfer", "y", "x", -3)],
    [("deposit", "solo", 1)],
    [("deposit", "b", 500), ("deposit", "a", 250), ("transfer", "b", "c", 499),
     ("withdraw", "b", 2), ("withdraw", "c", 499), ("withdraw", "a", 250)],
)


def _ledger_out34(txns):
    bal, out = {}, []
    for t in txns:
        amount = t[-1]
        if amount <= 0:
            out.append("rejected: non-positive")
            continue
        if t[0] == "deposit":
            bal[t[1]] = bal.get(t[1], 0) + amount
            out.append("ok")
        elif t[0] == "withdraw":
            if bal.get(t[1], 0) < amount:
                out.append("rejected: insufficient funds")
            else:
                bal[t[1]] = bal.get(t[1], 0) - amount
                out.append("ok")
        else:
            if bal.get(t[1], 0) < amount:
                out.append("rejected: insufficient funds")
            else:
                bal[t[1]] = bal.get(t[1], 0) - amount
                bal[t[2]] = bal.get(t[2], 0) + amount
                out.append("ok")
    out.append("{" + ", ".join(f"{k}={bal[k]}" for k in sorted(bal)) + "}")
    return _nl(*out)


_M34_CAP = _jcap(
    "The ledger",
    """
Every transaction is one of three shapes - and the types say so:

```java
sealed interface Txn permits Deposit, Withdrawal, Transfer {}
record Deposit(String account, int amount) implements Txn {}
record Withdrawal(String account, int amount) implements Txn {}
record Transfer(String from, String to, int amount) implements Txn {}
```

Write `apply(txn, balances)`, returning `ok` or the reason it was rejected:

* any transaction whose amount is **not positive** is `rejected: non-positive`;
* a withdrawal or transfer larger than the source account's balance (accounts
  start at 0) is `rejected: insufficient funds`;
* otherwise update the balances and return `ok`.

Write it as **one pattern switch** over the sealed `Txn` - guards for the
non-positive rule, record patterns to take each transaction apart, and no
`default`. `main` applies every transaction in order and then prints the
balances (a `TreeMap`, so sorted by account).
""",
    _jch("j34-cap-ledger", "The ledger", "Hard",
         "Write `apply` as the brief describes: a single pattern switch over the sealed "
         "`Txn`, with guards and record patterns and no `default`.",
         _j34th(_TXN34, _READTXN34 + "\n\n" + _APPLY34,
                "        int n = sc.nextInt();\n"
                "        Map<String, Integer> balances = new TreeMap<>();\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            System.out.println(apply(read(sc), balances));\n"
                "        }\n"
                "        System.out.println(balances);"),
         _APPLY34,
         [_rows34(t, _ledger_out34(t)) for t in _LEDGERS34],
         hints=["`return switch (t) { ... };`",
                "Guarded cases FIRST: `case Deposit d when d.amount() <= 0 -> ...` - "
                "otherwise the record pattern below would dominate them.",
                "`case Deposit(String account, int amount) -> { ...; yield \"ok\"; }`",
                "Inside a block arm, `yield` can sit inside an `if` to leave early.",
                "`balances.getOrDefault(from, 0) < amount` checks the funds.",
                "`merge(account, -amount, Integer::sum)` subtracts.",
                "No `default`: three records, three unguarded cases - exhaustive."]),
    example_io="stdin:  2\n        deposit ada 100\n        withdraw ada 130\n\n"
               "stdout: ok\n        rejected: insufficient funds\n        {ada=100}",
    rubric=[
        "The transaction kinds are records permitted by a sealed interface.",
        "`apply` is one switch over `Txn`, using record patterns to reach the components.",
        "The non-positive rule is expressed with `when` guards placed before the unguarded cases.",
        "The switch has no `default` - adding a fourth transaction type would be a compile error.",
        "A rejected transaction leaves every balance unchanged.",
    ],
)


_MODULES.append(_jmod(
    34, 13, "Advanced Java",
    "Records, sealed types and pattern matching",
    "Modern Java's answer to \"this is just data, and it comes in these shapes\" - "
    "with the compiler checking that every shape is handled. Requires JDK 21 or later.",
    """
**This module needs JDK 21 or later** - its features arrived between Java 16 and
21, and on an older JDK its programs will not compile.

* **Records** declare a class that is just its data in one line: final fields, a
  canonical constructor, accessors (`p.x()`), and value-based `equals`, `hashCode`
  and `toString`. Rules go in a **compact constructor**, which reassigns its
  parameters - never the fields.
* **Records are shallowly immutable.** Copy mutable components with `List.copyOf`
  in the compact constructor. Records make excellent composite keys, and can
  implement interfaces and add methods - which return new records.
* **`instanceof` patterns** test and cast in one step (`o instanceof String s`),
  with flow scoping - including after a negated test that returns - and a one-line
  `equals`.
* **Sealed types** list their permitted subtypes, each `final`, `sealed` or
  `non-sealed`. The compiler, and every reader, then knows every case.
* **Pattern matching in `switch`** (Java 21): type patterns, **record patterns**
  that deconstruct, `when` guards, `case null`, and **exhaustiveness** over a
  sealed hierarchy - no `default`, and a compile error when a new case appears.
""",
    _M34,
    capstone=_M34_CAP,
    objectives=[
        "Declare a record and list everything the compiler generates for it.",
        "Validate and normalise in a compact constructor, reassigning parameters rather than fields.",
        "Explain shallow immutability, and fix it with `List.copyOf`.",
        "Use a record as a composite map key, and say why it beats a String key.",
        "Add methods and interfaces to a record, keeping it immutable.",
        "Replace test-then-cast with an `instanceof` type pattern, and use flow scoping.",
        "Write `equals` with a type pattern.",
        "Declare a sealed hierarchy, and choose `final`, `sealed` or `non-sealed` for each subtype.",
        "Write an exhaustive pattern switch over a sealed type with no `default`.",
        "Deconstruct records with record patterns, and order guarded cases to avoid domination.",
        "Handle `null` in a pattern switch.",
        "Model data with several shapes as a sealed interface of records.",
    ],
    why="Records, sealed types and pattern matching are what \"modern Java\" means in "
        "an interview today - and the questions probe whether you understand them or have "
        "only seen the syntax: is a record immutable (only shallowly), where does "
        "validation go, why seal an interface, why does this switch need no default, why "
        "is this case a compile error. The expression evaluator in lesson 34.5 is itself a "
        "common interview problem, and the sealed-records-and-switch answer is the one "
        "that shows you know current Java.",
    est_minutes=330,
    glossary=[
        _jg("record", "A class declared by its components; the compiler generates final "
                      "fields, a canonical constructor, accessors, equals, hashCode and "
                      "toString."),
        _jg("Canonical constructor", "The constructor taking every component in order."),
        _jg("Compact constructor", "A record constructor with no parameter list; it "
                                   "validates or reassigns the parameters, and the "
                                   "fields are assigned afterwards."),
        _jg("Shallow immutability", "Final references to objects that may themselves "
                                    "still change."),
        _jg("List.copyOf", "An unmodifiable copy of a collection (Java 10); rejects "
                           "nulls."),
        _jg("Type pattern", "`o instanceof String s` - a test that also binds a typed "
                            "variable."),
        _jg("Flow scoping", "A pattern variable is in scope wherever the compiler can "
                            "prove the match succeeded."),
        _jg("sealed", "A class or interface that lists its permitted direct subtypes."),
        _jg("non-sealed", "A permitted subtype that re-opens the hierarchy below it."),
        _jg("Record pattern", "`Rect(int w, int h)` - matches a record and binds its "
                              "components."),
        _jg("Guard", "A `when` condition on a switch case."),
        _jg("Dominance", "A case that can never be reached because an earlier case "
                         "matches everything it would; a compile error."),
        _jg("Exhaustive switch", "A switch covering every possible value - checked by the "
                                 "compiler for enums and sealed types."),
        _jg("Algebraic data type", "A sealed type whose cases are records - one of "
                                   "several shapes of data."),
    ],
    cheatsheet="""
```java
// --- records ------------------------------------------------------------------
record Point(int x, int y) {}          // fields, ctor, x()/y(), equals, hashCode, toString
new Point(1, 2)                        // Point[x=1, y=2]
record Range(int lo, int hi) {
    Range {                            // compact constructor
        if (lo > hi) { int t = lo; lo = hi; hi = t; }   // reassign PARAMETERS
    }                                  // (this.lo = ... is a compile error)
    int length() { return hi - lo; }
}
record Team(String name, List<String> members) {
    Team { members = List.copyOf(members); }            // deep-enough copy
}
record Score(String name, int points) implements Comparable<Score> { ... }
Map<Cell, Integer> visits = new LinkedHashMap<>();      // record as composite key

// --- instanceof patterns -----------------------------------------------------------
if (o instanceof String s && s.length() > 3) { ... }
if (!(o instanceof String s)) return "not text";        // flow scoping:
return s.toUpperCase();                                 // s is in scope here
public boolean equals(Object o) { return o instanceof Point p && x == p.x && y == p.y; }

// --- sealed ------------------------------------------------------------------------------
sealed interface Shape permits Square, Rect, Triangle {}
record Square(int side) implements Shape {}             // records are final
final class Car extends Vehicle {}  non-sealed class Truck extends Vehicle {}

// --- pattern switch (Java 21) ----------------------------------------------------
return switch (shape) {                                 // exhaustive: no default
    case Square q when q.side() == 0 -> 0;              // guarded FIRST
    case Square q -> q.side() * q.side();
    case Rect(int w, int h) -> w * h;                   // record pattern
    case Triangle(int b, int h) -> b * h / 2;
};
switch (o) { case null -> ...; case Integer i -> ...; default -> ...; }
```
""",
    self_check=[
        "Can you list the six things `record Point(int x, int y) {}` generates?",
        "Can you explain why `this.lo = hi;` does not compile in a compact constructor?",
        "Can you show a record whose 'immutable' state changes, and fix it?",
        "Can you say why a record makes a better composite key than a concatenated String?",
        "Can you rewrite a test-then-cast as a type pattern, and say what bug that removes?",
        "Can you explain flow scoping with a negated `instanceof` and an early return?",
        "Can you write `equals` in one line with a pattern?",
        "Can you say what `final`, `sealed` and `non-sealed` mean on a permitted subtype?",
        "Can you explain why a switch over a sealed interface needs no `default`?",
        "Can you explain domination, and order guarded cases correctly?",
        "Can you write an expression evaluator with a sealed interface and record patterns?",
    ],
    review=[
        _jq("```java\nrecord P(List<String> xs) {}\nvar src = new ArrayList<>(List.of(\"a\"));\nvar p = new P(src);\nsrc.add(\"b\");\n```\n`p.xs().size()` is…",
            ["2 - the record shares the caller's list", "1", "an exception",
             "a compile error"],
            0,
            "Copy in the compact constructor to prevent it."),
        _jq("`if (o instanceof Integer i || i > 0)` is…",
            ["a compile error - i is not in scope on the right of ||",
             "fine", "a runtime error", "true for null"],
            0,
            "The right side of || runs exactly when the match failed."),
        _jq("A sealed interface gains a new permitted record. A switch over it with no "
            "`default`…",
            ["fails to compile until the new case is handled", "silently skips it",
             "throws MatchException for it", "falls through"],
            0,
            "That is what exhaustiveness is for."),
        _jq("`case Rect r ->` appears before `case Rect(int w, int h) when w == h ->`. "
            "The result is…",
            ["a compile error: the second case is dominated", "the guard runs first",
             "both run", "a warning"],
            0,
            "Specific cases must come first."),
        _jq("Records are a poor fit for…",
            ["an entity whose state changes over time", "a composite key",
             "an AST node", "a query result row"],
            0,
            "A record is a value; it has no identity to keep."),
    ],
    milestone="You can model data with several shapes as a sealed interface of records, "
              "take it apart with an exhaustive pattern switch, and keep it genuinely "
              "immutable - the modern-Java answer to a question the older course could "
              "only answer with class hierarchies and casts.",
))
