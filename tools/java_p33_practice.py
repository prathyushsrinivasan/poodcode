# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 33 practice - enums, switch and nested classes.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[33]`.
#
# Uses module 33's helpers (`_j33s`, `_j33t`, `_toks33`, `_rows33`, `_jmap33`).
# Every map printed here is an EnumMap or an EnumSet, both of which iterate in
# declaration order - so no output depends on hashing.
# ---------------------------------------------------------------------------


def _p33s(eid, title, difficulty, prompt, body, tests, hints):
    """No helper types - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _j33s(body), body, tests, hints)


def _p33t(eid, title, difficulty, prompt, types, body, region, tests, hints):
    """Helper types above Main; `region` (inside the types, or main's body) is yours."""
    return _jch(eid, title, difficulty, prompt, _j33t(types, body), region.rstrip("\n"),
                tests, hints)


def _inner33(types):
    """The body of a single `enum X { ... }` / `class X { ... }`, without its braces."""
    lines = types.strip("\n").split("\n")
    return "\n".join(lines[1:-1])


# --- Family A - enums with data ------------------------------------------------

_COLOR33 = """
enum Color {
    RED, GREEN, BLUE
}
"""
_COLORTOKS33 = (["RED", "PINK", "BLUE"], ["GREEN"], ["red", "BLUE", "BLUE", "TEAL"],
                ["NONE"], ["BLUE", "GREEN", "RED"])

_SIZE33 = """
enum Size {
    SMALL(250), MEDIUM(350), LARGE(500);

    private final int ml;

    Size(int ml) {
        this.ml = ml;
    }

    int ml() {
        return ml;
    }
}
"""
_ML33 = {"SMALL": 250, "MEDIUM": 350, "LARGE": 500}
_CUPS33 = (["SMALL", "LARGE"], ["MEDIUM"], ["LARGE", "LARGE", "LARGE"],
           ["SMALL", "SMALL", "MEDIUM", "LARGE"], ["MEDIUM", "SMALL"])

_GRADE33 = """
enum Grade {
    A(90), B(80), C(70), D(60), F(0);

    private final int min;

    Grade(int min) {
        this.min = min;
    }

    static Grade of(int score) {
        for (Grade g : values()) {
            if (score >= g.min) {
                return g;
            }
        }
        throw new IllegalArgumentException();
    }
}
"""
_GRADE_REGION33 = (
    "    static Grade of(int score) {\n"
    "        for (Grade g : values()) {\n"
    "            if (score >= g.min) {\n"
    "                return g;\n"
    "            }\n"
    "        }\n"
    "        throw new IllegalArgumentException();\n"
    "    }"
)
_GMIN33 = (("A", 90), ("B", 80), ("C", 70), ("D", 60), ("F", 0))
_SCORES33 = ([95, 42], [90, 89, 80], [0], [100, 60, 59, 70], [75])


def _grade_of33(score):
    return next(g for (g, m) in _GMIN33 if score >= m)


_PRIORITY33 = """
enum Priority {
    LOW, MEDIUM, HIGH, URGENT
}
"""
_PRIS33 = ("LOW", "MEDIUM", "HIGH", "URGENT")
_TASKS33 = ([("write", "LOW"), ("fix", "URGENT"), ("test", "HIGH")],
            [("solo", "MEDIUM")],
            [("b", "HIGH"), ("a", "HIGH"), ("c", "LOW")],
            [("x", "URGENT"), ("y", "URGENT"), ("w", "MEDIUM"), ("v", "LOW")],
            [("deploy", "MEDIUM"), ("audit", "LOW")])


def _tasks_out33(rows):
    ordered = sorted(rows, key=lambda r: (-_PRIS33.index(r[1]), r[0]))
    return _nl(*[f"{p} {n}" for (n, p) in ordered])


_UNIT33 = """
enum Unit {
    KM("kilometres"), M("metres"), CM("centimetres");

    private final String label;

    Unit(String label) {
        this.label = label;
    }

    @Override
    public String toString() {
        return label;
    }
}
"""
_ULABEL33 = {"KM": "kilometres", "M": "metres", "CM": "centimetres"}
_UROWS33 = ([(3, "KM")], [(10, "M"), (5, "CM")], [(1, "CM"), (2, "KM"), (7, "M")],
            [(0, "M")], [(42, "KM"), (42, "CM")])


_P33_A = _jfam(
    "p33-enums", "Enums with data",
    "`valueOf`, `values()`, fields, a static lookup, and `name()` versus `toString()`.",
    """
An enum is a class whose instances you list:

```java
enum Grade {
    A(90), B(80), C(70), D(60), F(0);
    private final int min;
    Grade(int min) { this.min = min; }

    static Grade of(int score) {             // a lookup over values()
        for (Grade g : values()) {
            if (score >= g.min) return g;
        }
        throw new IllegalArgumentException();
    }
}
```

Two facts carry this family. Enums are `Comparable` in **declaration order**, so
sorting a list of them needs no comparator. And `name()` is final and always the
declared name - `valueOf` uses it - while `toString()` can be overridden for
display. Parse with `valueOf`, print with `toString`, and the two never collide.
""",
    [
        _p33t("j33-pa-parse", "Valid and invalid names", "Intro",
              "Parse each token as a `Color`. Print the valid ones in order, then "
              "`invalid: k` for how many were not colours. `valueOf` throws "
              "`IllegalArgumentException` for a bad name.",
              _COLOR33,
              "        int n = sc.nextInt();\n"
              "        int invalid = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String token = sc.next();\n"
              "            try {\n"
              "                System.out.println(Color.valueOf(token));\n"
              "            } catch (IllegalArgumentException e) {\n"
              "                invalid++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(\"invalid: \" + invalid);",
              "        int n = sc.nextInt();\n"
              "        int invalid = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String token = sc.next();\n"
              "            try {\n"
              "                System.out.println(Color.valueOf(token));\n"
              "            } catch (IllegalArgumentException e) {\n"
              "                invalid++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(\"invalid: \" + invalid);",
              [_toks33(ts, _nl(*([t for t in ts if t in ("RED", "GREEN", "BLUE")]
                                 + [f"invalid: {sum(1 for t in ts if t not in ('RED', 'GREEN', 'BLUE'))}"])))
               for ts in _COLORTOKS33],
              ["`Color.valueOf(token)` either returns a constant or throws.",
               "Catch `IllegalArgumentException` and count it.",
               "`red` is not `RED` - no normalising in this one."]),

        _p33t("j33-pa-field", "Cups by size", "Easy",
              "Write `Size`'s body: SMALL, MEDIUM and LARGE hold 250, 350 and 500 ml. "
              "`main` prints the total volume of the order.",
              _SIZE33,
              "        int n = sc.nextInt();\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            total += Size.valueOf(sc.next()).ml();\n"
              "        }\n"
              "        System.out.println(total + \" ml\");",
              _inner33(_SIZE33),
              [_toks33(ts, f"{sum(_ML33[t] for t in ts)} ml") for ts in _CUPS33],
              ["`SMALL(250), MEDIUM(350), LARGE(500);`",
               "A private final field and a constructor that sets it.",
               "`int ml()` returns it."]),

        _p33t("j33-pa-lookup", "Score to grade", "Easy",
              "Write `Grade.of(score)`: return the FIRST grade, in declaration order, whose "
              "minimum the score reaches.",
              _GRADE33,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int score = sc.nextInt();\n"
              "            System.out.println(score + \" \" + Grade.of(score));\n"
              "        }",
              _GRADE_REGION33,
              [_toks33([str(s) for s in ss], _nl(*[f"{s} {_grade_of33(s)}" for s in ss]))
               for ss in _SCORES33],
              ["`static Grade of(int score)` - static, because there is no Grade yet.",
               "Loop over `values()`, highest minimum first.",
               "The enum can read `g.min` even though it is private - same class.",
               "F's minimum is 0, so every non-negative score finds a grade."]),

        _p33t("j33-pa-sort", "Most urgent first", "Medium",
              "Each task is `name PRIORITY`. Print them most urgent first, breaking ties by "
              "name. Enums compare in declaration order, so no comparator for the "
              "priority itself is needed.",
              _PRIORITY33,
              "        int n = sc.nextInt();\n"
              "        List<String> names = new ArrayList<>();\n"
              "        List<Priority> pris = new ArrayList<>();\n"
              "        List<Integer> order = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            names.add(sc.next());\n"
              "            pris.add(Priority.valueOf(sc.next()));\n"
              "            order.add(i);\n"
              "        }\n"
              "        order.sort(Comparator.comparing((Integer i) -> pris.get(i)).reversed()\n"
              "                .thenComparing(i -> names.get(i)));\n"
              "        for (int i : order) {\n"
              "            System.out.println(pris.get(i) + \" \" + names.get(i));\n"
              "        }",
              "        order.sort(Comparator.comparing((Integer i) -> pris.get(i)).reversed()\n"
              "                .thenComparing(i -> names.get(i)));",
              [_rows33(rows, _tasks_out33(rows)) for rows in _TASKS33],
              ["Enums implement `Comparable` by ordinal: LOW < MEDIUM < HIGH < URGENT.",
               "`Comparator.comparing(i -> pris.get(i))` then `.reversed()` puts URGENT "
               "first.",
               "The lambda's parameter type has to be spelled `(Integer i)` - "
               "`reversed()` gives inference nothing to work from.",
               "`.thenComparing(i -> names.get(i))` breaks ties alphabetically."]),

        _p33t("j33-pa-display", "`name()` for parsing, `toString()` for people", "Hard",
              "Write `Unit`'s body so each constant prints as a friendly label (KM prints "
              "`kilometres`) while `valueOf(\"KM\")` still works. `main` prints `amount "
              "label (NAME)`.",
              _UNIT33,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int amount = sc.nextInt();\n"
              "            Unit u = Unit.valueOf(sc.next());\n"
              "            System.out.println(amount + \" \" + u + \" (\" + u.name() + \")\");\n"
              "        }",
              _inner33(_UNIT33),
              [_rows33(rows, _nl(*[f"{a} {_ULABEL33[u]} ({u})" for (a, u) in rows]))
               for rows in _UROWS33],
              ["Each constant passes its label to the constructor.",
               "Override `toString()` to return the label - it must be `public`.",
               "`name()` is final: it is always `KM`, whatever `toString` says.",
               "`valueOf` matches on `name()`, so overriding `toString` never breaks "
               "parsing."]),
    ],
)


# --- Family B - EnumMap and EnumSet ---------------------------------------------

_WEEK33 = """
enum Day {
    MON, TUE, WED, THU, FRI, SAT, SUN
}
"""
_VOTESB33 = (["BLUE", "RED", "BLUE"], ["GREEN"], ["RED", "RED", "GREEN", "BLUE", "GREEN"],
             ["BLUE"], ["GREEN", "GREEN", "GREEN"])
_COLORS33 = ("RED", "GREEN", "BLUE")
_WORKED33 = (["MON", "WED"], ["SUN"], ["FRI", "MON", "TUE", "FRI"], ["SAT", "SUN"],
             ["THU", "WED", "TUE", "MON", "FRI"])
_SPANSB33 = (("MON", "FRI"), ("SAT", "SUN"), ("WED", "WED"), ("TUE", "THU"), ("MON", "SUN"))

_LENGTH33 = """
enum Length {
    SHORT, MEDIUM, LONG;

    static Length of(String word) {
        if (word.length() <= 3) {
            return SHORT;
        }
        return word.length() <= 6 ? MEDIUM : LONG;
    }
}
"""
_GROUPS33 = (["ada", "banana", "kiwi", "strawberry"], ["x"], ["pear", "plum", "fig", "melon"],
             ["watermelon", "grapefruit"], ["a", "bb", "cccc", "ddddddd", "eee"])


def _len_of33(w):
    return "SHORT" if len(w) <= 3 else ("MEDIUM" if len(w) <= 6 else "LONG")


def _group_out33(ws):
    groups = {}
    for w in ws:
        groups.setdefault(_len_of33(w), []).append(w)
    return _jmap33([(k, _jarr(groups[k])) for k in ("SHORT", "MEDIUM", "LONG") if k in groups])


_P33_B = _jfam(
    "p33-maps", "`EnumMap` and `EnumSet`",
    "Collections keyed by an enum: array-backed, and always in declaration order.",
    """
```java
Map<Color, Integer> counts = new EnumMap<>(Color.class);
Set<Day> worked = EnumSet.noneOf(Day.class);
EnumSet.of(Day.SAT, Day.SUN)          EnumSet.allOf(Day.class)
EnumSet.range(Day.MON, Day.FRI)       EnumSet.complementOf(worked)
```

An `EnumSet` is a bit field - one bit per constant - and an `EnumMap` is an
array indexed by ordinal. Both print in declaration order, whatever order you
added things in, which makes them the natural choice whenever the keys are an
enum and the output has to be predictable.
""",
    [
        _p33t("j33-pb-count", "Votes by colour", "Intro",
              "Count the votes for each colour in an `EnumMap` and print it.",
              _COLOR33,
              "        int n = sc.nextInt();\n"
              "        Map<Color, Integer> votes = new EnumMap<>(Color.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            votes.merge(Color.valueOf(sc.next()), 1, Integer::sum);\n"
              "        }\n"
              "        System.out.println(votes);",
              "        int n = sc.nextInt();\n"
              "        Map<Color, Integer> votes = new EnumMap<>(Color.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            votes.merge(Color.valueOf(sc.next()), 1, Integer::sum);\n"
              "        }\n"
              "        System.out.println(votes);",
              [_toks33(ts, _jmap33([(c, ts.count(c)) for c in _COLORS33 if c in ts]))
               for ts in _VOTESB33],
              ["`new EnumMap<>(Color.class)`.",
               "`merge(key, 1, Integer::sum)` counts.",
               "It prints RED before GREEN before BLUE, whatever the input order."]),

        _p33t("j33-pb-all", "Including the colours nobody chose", "Easy",
              "Print every colour with its vote count, one per line, including zeros.",
              _COLOR33,
              "        int n = sc.nextInt();\n"
              "        Map<Color, Integer> votes = new EnumMap<>(Color.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            votes.merge(Color.valueOf(sc.next()), 1, Integer::sum);\n"
              "        }\n"
              "        for (Color c : Color.values()) {\n"
              "            System.out.println(c + \" \" + votes.getOrDefault(c, 0));\n"
              "        }",
              "        for (Color c : Color.values()) {\n"
              "            System.out.println(c + \" \" + votes.getOrDefault(c, 0));\n"
              "        }",
              [_toks33(ts, _nl(*[f"{c} {ts.count(c)}" for c in _COLORS33])) for ts in _VOTESB33],
              ["The map only has keys that were voted for.",
               "Loop over `Color.values()` instead.",
               "`getOrDefault(c, 0)` fills the gaps."]),

        _p33t("j33-pb-set", "Days worked, days off", "Medium",
              "Collect the days worked into an `EnumSet` (duplicates collapse), print it, "
              "then print the days NOT worked.",
              _WEEK33,
              "        int n = sc.nextInt();\n"
              "        Set<Day> worked = EnumSet.noneOf(Day.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            worked.add(Day.valueOf(sc.next()));\n"
              "        }\n"
              "        System.out.println(worked);\n"
              "        System.out.println(EnumSet.complementOf(EnumSet.copyOf(worked)));",
              "        Set<Day> worked = EnumSet.noneOf(Day.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            worked.add(Day.valueOf(sc.next()));\n"
              "        }\n"
              "        System.out.println(worked);\n"
              "        System.out.println(EnumSet.complementOf(EnumSet.copyOf(worked)));",
              [_toks33(ts, _nl(_jarr([d for d in _DAYS33 if d in ts]),
                               _jarr([d for d in _DAYS33 if d not in ts])))
               for ts in _WORKED33],
              ["`EnumSet.noneOf(Day.class)` is an empty set of days.",
               "A set ignores the second FRI.",
               "`EnumSet.complementOf` needs an `EnumSet`, and `worked` is declared as a "
               "`Set` - `EnumSet.copyOf(worked)` bridges the two.",
               "Both print in declaration order, MON first."]),

        _p33t("j33-pb-range", "A range of days", "Medium",
              "Read two days and print every day from the first to the second INCLUSIVE, "
              "then how many there are.",
              _WEEK33,
              "        Day from = Day.valueOf(sc.next());\n"
              "        Day to = Day.valueOf(sc.next());\n"
              "        Set<Day> span = EnumSet.range(from, to);\n"
              "        System.out.println(span);\n"
              "        System.out.println(span.size());",
              "        Set<Day> span = EnumSet.range(from, to);\n"
              "        System.out.println(span);\n"
              "        System.out.println(span.size());",
              [_case(f"{a} {b}", _nl(_jarr(list(_DAYS33[_DAYS33.index(a):_DAYS33.index(b) + 1])),
                                     _DAYS33.index(b) - _DAYS33.index(a) + 1))
               for (a, b) in _SPANSB33],
              ["`EnumSet.range(from, to)` includes both ends.",
               "It follows declaration order - which is why MON..FRI means the working "
               "week.",
               "A range from a day to itself has one element."]),

        _p33t("j33-pb-group", "Words grouped by length class", "Hard",
              "`Length.of(word)` classifies a word as SHORT (≤ 3), MEDIUM (≤ 6) or LONG. "
              "Group the words into an `EnumMap<Length, List<String>>`, keeping input "
              "order within each group, and print it.",
              _LENGTH33,
              "        int n = sc.nextInt();\n"
              "        Map<Length, List<String>> groups = new EnumMap<>(Length.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String w = sc.next();\n"
              "            groups.computeIfAbsent(Length.of(w), k -> new ArrayList<>()).add(w);\n"
              "        }\n"
              "        System.out.println(groups);",
              "        Map<Length, List<String>> groups = new EnumMap<>(Length.class);\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String w = sc.next();\n"
              "            groups.computeIfAbsent(Length.of(w), k -> new ArrayList<>()).add(w);\n"
              "        }\n"
              "        System.out.println(groups);",
              [_toks33(ws, _group_out33(ws)) for ws in _GROUPS33],
              ["`computeIfAbsent(key, k -> new ArrayList<>())` creates each list once.",
               "Then `.add(w)` onto whatever list came back.",
               "The groups print SHORT, MEDIUM, LONG - declaration order - and skip empty "
               "ones."]),
    ],
)


# --- Family C - switch ----------------------------------------------------------

_MONTHS33 = ([1, 2], [4, 6, 9, 11], [12], [7, 8, 2], [3, 5, 10])


def _mdays33(m):
    return 28 if m == 2 else (30 if m in (4, 6, 9, 11) else 31)


_TEXTS33 = ("hello world 42", "AEIOU xyz", "rhythm", "a1b2c3!?", "Queue up 7 items")


def _classify33(s):
    v = c = d = o = 0
    for ch in s:
        low = ch.lower()
        if low in "aeiou":
            v += 1
        elif "a" <= low <= "z":
            c += 1
        elif "0" <= ch <= "9":
            d += 1
        elif ch != " ":
            o += 1
    return f"vowels {v} consonants {c} digits {d} other {o}"


_EXPRS33 = ([(7, "+", 5), (7, "/", 2)], [(9, "%", 4), (3, "^", 2)], [(-6, "*", 7)],
            [(5, "/", 0), (1, "-", 9)], [(100, "/", 7), (100, "%", 7), (2, "x", 2)])


def _calc33(a, op, b):
    if op == "+":
        return str(a + b)
    if op == "-":
        return str(a - b)
    if op == "*":
        return str(a * b)
    if op in "/%":
        if b == 0:
            return "division by zero"
        return str(_jdiv(a, b)) if op == "/" else str(a - _jdiv(a, b) * b)
    return f"bad op {op}"


_GROUP33 = """
enum Group {
    CHILD, ADULT, SENIOR
}
"""
_TICKETS33 = ([("CHILD", "no"), ("ADULT", "yes")], [("SENIOR", "no")],
              [("ADULT", "no"), ("SENIOR", "yes"), ("CHILD", "yes")], [("ADULT", "yes")],
              [("CHILD", "no"), ("CHILD", "yes"), ("SENIOR", "yes")])


def _ticket33(g, weekend):
    if g == "CHILD":
        return 5
    if g == "ADULT":
        return 15 if weekend == "yes" else 12
    return 12 - 4 if weekend == "yes" else 6


_PACK33 = ("tent", "stove", "lamp", "map")
_PACKDAYS33 = ([1], [3], [4, 2], [2, 1], [4])


def _pack_out33(ds):
    out = []
    for d in ds:
        out.append(f"trip of {d}:")
        out.extend(_PACK33[i] for i in range(d - 1, -1, -1))
    return _nl(*out)


_P33_C = _jfam(
    "p33-switch", "`switch`, both kinds",
    "Arrow arms and shared labels - and, once, a fall-through on purpose.",
    """
```java
int days = switch (month) {          // an expression: it has a value
    case 2 -> 28;
    case 4, 6, 9, 11 -> 30;
    default -> 31;
};

switch (c) {                          // a statement with arrows: no fall-through
    case 'a', 'e', 'i', 'o', 'u' -> vowels++;
    default -> other++;
}
```

Arrow arms run exactly their own code. A block arm in an expression ends with
`yield`. And the classic colon-style statement still falls through without
`break` - which, just occasionally, is exactly what you want: the last drill
uses it deliberately.
""",
    [
        _p33s("j33-pc-days", "Days in a month", "Intro",
              "Print the number of days in each month number (ignore leap years), using a "
              "switch expression.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int month = sc.nextInt();\n"
              "            int days = switch (month) {\n"
              "                case 2 -> 28;\n"
              "                case 4, 6, 9, 11 -> 30;\n"
              "                default -> 31;\n"
              "            };\n"
              "            System.out.println(month + \" \" + days);\n"
              "        }",
              [_toks33([str(m) for m in ms], _nl(*[f"{m} {_mdays33(m)}" for m in ms]))
               for ms in _MONTHS33],
              ["`case 4, 6, 9, 11 -> 30;` shares one arm between four labels.",
               "An int switch needs a `default` - the compiler cannot know which ints "
               "occur.",
               "The whole switch ends with `;` because it is an expression."]),

        _p33s("j33-pc-chars", "Classifying characters", "Easy",
              "Read one line and count vowels, consonants, digits and other non-space "
              "characters. Lower-case each character first, then switch on it.",
              "        String line = sc.nextLine();\n"
              "        int vowels = 0, consonants = 0, digits = 0, other = 0;\n"
              "        for (char ch : line.toCharArray()) {\n"
              "            char c = Character.toLowerCase(ch);\n"
              "            switch (c) {\n"
              "                case 'a', 'e', 'i', 'o', 'u' -> vowels++;\n"
              "                case ' ' -> { }\n"
              "                default -> {\n"
              "                    if (c >= 'a' && c <= 'z') {\n"
              "                        consonants++;\n"
              "                    } else if (Character.isDigit(c)) {\n"
              "                        digits++;\n"
              "                    } else {\n"
              "                        other++;\n"
              "                    }\n"
              "                }\n"
              "            }\n"
              "        }\n"
              "        System.out.println(\"vowels \" + vowels + \" consonants \" + consonants\n"
              "                + \" digits \" + digits + \" other \" + other);",
              [_lcase(t, _classify33(t)) for t in _TEXTS33],
              ["You can switch on a `char`.",
               "`case 'a', 'e', 'i', 'o', 'u' -> vowels++;`",
               "`case ' ' -> { }` is an arm that deliberately does nothing.",
               "Everything else goes to a `default` block that sorts it further."]),

        _p33s("j33-pc-calc", "An integer calculator", "Medium",
              "Each line is `a op b`. Support `+ - * / %` with Java's integer semantics; "
              "print `division by zero` for a zero divisor and `bad op X` for any other "
              "operator.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int a = sc.nextInt();\n"
              "            String op = sc.next();\n"
              "            int b = sc.nextInt();\n"
              "            try {\n"
              "                int r = switch (op) {\n"
              "                    case \"+\" -> a + b;\n"
              "                    case \"-\" -> a - b;\n"
              "                    case \"*\" -> a * b;\n"
              "                    case \"/\" -> a / b;\n"
              "                    case \"%\" -> a % b;\n"
              "                    default -> throw new IllegalArgumentException(op);\n"
              "                };\n"
              "                System.out.println(r);\n"
              "            } catch (ArithmeticException e) {\n"
              "                System.out.println(\"division by zero\");\n"
              "            } catch (IllegalArgumentException e) {\n"
              "                System.out.println(\"bad op \" + op);\n"
              "            }\n"
              "        }",
              [_rows33(rows, _nl(*[_calc33(a, o, b) for (a, o, b) in rows])) for rows in _EXPRS33],
              ["Switch on the operator String.",
               "`default -> throw new IllegalArgumentException(op);` - a throw is a legal "
               "arm.",
               "Integer `/` and `%` by zero throw `ArithmeticException`.",
               "`100 / 7` is 14 and `100 % 7` is 2."]),

        _p33t("j33-pc-yield", "Ticket prices", "Medium",
              "A CHILD pays 5. An ADULT pays 12, or 15 at weekends. A SENIOR pays half the "
              "adult weekday price (6), but at weekends pays the adult weekday price minus "
              "4. Compute each price with a switch expression over `Group`, using a block "
              "and `yield` where an arm needs more than one line.",
              _GROUP33,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Group g = Group.valueOf(sc.next());\n"
              "            boolean weekend = sc.next().equals(\"yes\");\n"
              "            int price = switch (g) {\n"
              "                case CHILD -> 5;\n"
              "                case ADULT -> weekend ? 15 : 12;\n"
              "                case SENIOR -> {\n"
              "                    int adultWeekday = 12;\n"
              "                    yield weekend ? adultWeekday - 4 : adultWeekday / 2;\n"
              "                }\n"
              "            };\n"
              "            System.out.println(g + \" \" + price);\n"
              "        }",
              "            int price = switch (g) {\n"
              "                case CHILD -> 5;\n"
              "                case ADULT -> weekend ? 15 : 12;\n"
              "                case SENIOR -> {\n"
              "                    int adultWeekday = 12;\n"
              "                    yield weekend ? adultWeekday - 4 : adultWeekday / 2;\n"
              "                }\n"
              "            };",
              [_rows33(rows, _nl(*[f"{g} {_ticket33(g, w)}" for (g, w) in rows]))
               for rows in _TICKETS33],
              ["Three constants, three arms - no `default` needed.",
               "`case ADULT -> weekend ? 15 : 12;` fits on one line.",
               "The SENIOR arm uses a block: `{ ...; yield value; }`.",
               "`yield`, not `return`, inside a switch expression's block."]),

        _p33s("j33-pc-pack", "Fall-through on purpose", "Hard",
              "A trip of `d` days (1 to 4) needs every item from the `d`-th down to the "
              "first: day 4 adds a map, 3 a lamp, 2 a stove and 1 a tent. Print `trip of d:` "
              "then the items, most specific first - using ONE colon-style switch that falls "
              "through deliberately, with no `break` at all.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int d = sc.nextInt();\n"
              "            System.out.println(\"trip of \" + d + \":\");\n"
              "            switch (d) {\n"
              "                case 4:\n"
              "                    System.out.println(\"map\");\n"
              "                case 3:\n"
              "                    System.out.println(\"lamp\");\n"
              "                case 2:\n"
              "                    System.out.println(\"stove\");\n"
              "                case 1:\n"
              "                    System.out.println(\"tent\");\n"
              "            }\n"
              "        }",
              [_toks33([str(d) for d in ds], _pack_out33(ds)) for ds in _PACKDAYS33],
              ["Enter the switch at the trip's length and let it fall through the smaller "
               "cases.",
               "Order the cases from 4 down to 1.",
               "No `break` anywhere - that is the whole trick.",
               "Leave a comment saying the fall-through is intentional; in real code, "
               "readers assume it is a bug."]),
    ],
)


# --- Family D - nested classes --------------------------------------------------

_PAIRSD33 = ([("ada", 3), ("bo", 9), ("cy", 4)], [("solo", 1)], [("x", -5), ("y", -2)],
             [("a", 7), ("b", 7), ("c", 1)], [("pear", 10), ("fig", 30), ("plum", 20)])

_QUEUE33 = """
class IntQueue {
    private static class Node {
        final int value;
        Node next;

        Node(int value) {
            this.value = value;
        }
    }

    private Node head;
    private Node tail;

    void add(int x) {
        Node node = new Node(x);
        if (tail == null) {
            head = node;
        } else {
            tail.next = node;
        }
        tail = node;
    }

    int remove() {
        int v = head.value;
        head = head.next;
        if (head == null) {
            tail = null;
        }
        return v;
    }

    boolean isEmpty() {
        return head == null;
    }
}
"""
_QUEUE_REGION33 = (
    "    void add(int x) {\n"
    "        Node node = new Node(x);\n"
    "        if (tail == null) {\n"
    "            head = node;\n"
    "        } else {\n"
    "            tail.next = node;\n"
    "        }\n"
    "        tail = node;\n"
    "    }\n"
    "\n"
    "    int remove() {\n"
    "        int v = head.value;\n"
    "        head = head.next;\n"
    "        if (head == null) {\n"
    "            tail = null;\n"
    "        }\n"
    "        return v;\n"
    "    }"
)
_QOPS33 = ([("add", 1), ("add", 2), ("remove",), ("add", 3), ("remove",), ("remove",)],
           [("add", 9), ("remove",)],
           [("add", 5), ("add", 6), ("add", 7), ("remove",), ("remove",), ("add", 8), ("remove",), ("remove",)],
           [("add", 4), ("remove",), ("add", 4), ("remove",)],
           [("add", 1), ("add", 2), ("add", 3), ("remove",)])


def _queue_out33(ops):
    q, out = [], []
    for op in ops:
        if op[0] == "add":
            q.append(op[1])
        else:
            out.append(q.pop(0))
    return _nl(_sp(out), "empty" if not q else "left " + _sp(q))


_BANK33 = """
class Bank {
    private final int ratePercent;

    Bank(int ratePercent) {
        this.ratePercent = ratePercent;
    }

    class Account {
        private final String owner;
        private final int balance;

        Account(String owner, int balance) {
            this.owner = owner;
            this.balance = balance;
        }

        int interest() {
            return balance * ratePercent / 100;
        }

        String describe() {
            return owner + " " + balance + " +" + interest();
        }
    }

    Account open(String owner, int balance) {
        return new Account(owner, balance);
    }
}
"""
_BANK_REGION33 = (
    "        int interest() {\n"
    "            return balance * ratePercent / 100;\n"
    "        }"
)
_BANKS33 = ((5, [("ada", 1000), ("bo", 250)]), (10, [("cy", 99)]), (3, [("x", 0), ("y", 700)]),
            (0, [("solo", 500)]), (12, [("pear", 1234), ("fig", 50), ("plum", 800)]))

_REV33 = """
class Reversed implements Iterable<String> {
    private final List<String> items;

    Reversed(List<String> items) {
        this.items = items;
    }

    @Override
    public Iterator<String> iterator() {
        return new Iterator<String>() {
            private int index = items.size() - 1;

            @Override
            public boolean hasNext() {
                return index >= 0;
            }

            @Override
            public String next() {
                return items.get(index--);
            }
        };
    }
}
"""
_REV_REGION33 = (
    "        return new Iterator<String>() {\n"
    "            private int index = items.size() - 1;\n"
    "\n"
    "            @Override\n"
    "            public boolean hasNext() {\n"
    "                return index >= 0;\n"
    "            }\n"
    "\n"
    "            @Override\n"
    "            public String next() {\n"
    "                return items.get(index--);\n"
    "            }\n"
    "        };"
)
_REVS33 = (["a", "b", "c"], ["solo"], ["pear", "fig"], ["x", "y", "z", "w"], ["one", "two", "three"])


_P33_D = _jfam(
    "p33-nested", "Nested classes",
    "Static nested for helpers, inner when you need the outer object, anonymous for "
    "a one-off.",
    """
```java
class IntQueue {
    private static class Node { ... }       // needs no IntQueue: static
}
class Bank {
    private final int ratePercent;
    class Account {                         // reads ratePercent: inner
        int interest() { return balance * ratePercent / 100; }
    }
}
return new Iterator<String>() { ... };      // anonymous, with its own state
```

The question to ask every time is *does this class need the outer object?* If
not, make it `static`: it is cheaper, and it cannot accidentally keep a large
outer object alive. If it does - an iterator over its outer collection, an
account that reads its bank's rate - an inner class is exactly right.
""",
    [
        _p33s("j33-pd-pair", "A static nested pair", "Intro",
              "Read `name value` pairs into a list of a static nested `Entry` class "
              "declared inside `Main`, and print the entry with the largest value (the "
              "first one on a tie).",
              "        int n = sc.nextInt();\n"
              "        List<Entry> entries = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            entries.add(new Entry(sc.next(), sc.nextInt()));\n"
              "        }\n"
              "        Entry best = entries.get(0);\n"
              "        for (Entry e : entries) {\n"
              "            if (e.value > best.value) {\n"
              "                best = e;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(best.name + \" \" + best.value);\n"
              "    }\n"
              "\n"
              "    static class Entry {\n"
              "        final String name;\n"
              "        final int value;\n"
              "\n"
              "        Entry(String name, int value) {\n"
              "            this.name = name;\n"
              "            this.value = value;\n"
              "        }",
              [_rows33(rows, "{} {}".format(*max(rows, key=lambda r: r[1]))) for rows in _PAIRSD33],
              ["`main` is static, so it can only create a nested class that is static too.",
               "Declare `static class Entry` inside `Main`, after `main`.",
               "The region ends inside `Entry` - its closing brace is already there.",
               "`>` rather than `>=` keeps the first of equal values."]),

        _p33t("j33-pd-queue", "A linked queue", "Easy",
              "`IntQueue` keeps a private static `Node` class and `head`/`tail` pointers. "
              "Write `add` (append at the tail) and `remove` (take from the head). `main` "
              "prints the removed values, then what is left.",
              _QUEUE33,
              "        int n = sc.nextInt();\n"
              "        IntQueue q = new IntQueue();\n"
              "        List<Integer> removed = new ArrayList<>();\n"
              "        List<Integer> added = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (sc.next().equals(\"add\")) {\n"
              "                int x = sc.nextInt();\n"
              "                q.add(x);\n"
              "                added.add(x);\n"
              "            } else {\n"
              "                removed.add(q.remove());\n"
              "            }\n"
              "        }\n"
              "        StringBuilder out = new StringBuilder();\n"
              "        for (int x : removed) {\n"
              "            if (out.length() > 0) out.append(' ');\n"
              "            out.append(x);\n"
              "        }\n"
              "        System.out.println(out);\n"
              "        StringBuilder left = new StringBuilder();\n"
              "        while (!q.isEmpty()) {\n"
              "            left.append(left.length() == 0 ? \"left \" : \" \").append(q.remove());\n"
              "        }\n"
              "        System.out.println(left.length() == 0 ? \"empty\" : left.toString());",
              _QUEUE_REGION33,
              [_rows33(ops, _queue_out33(ops)) for ops in _QOPS33],
              ["An empty queue has `tail == null`: the new node is both head and tail.",
               "Otherwise link it after the current tail, then move the tail.",
               "`remove` takes `head.value` and advances `head`.",
               "When the last node leaves, reset `tail` to null too - or the next `add` "
               "links onto a node nobody can reach."]),

        _p33t("j33-pd-inner", "An inner class reads its bank", "Medium",
              "`Bank.Account` is an INNER class, so it can read its bank's `ratePercent`. "
              "Write `interest()`: balance times the rate, over 100, in integer arithmetic.",
              _BANK33,
              "        Bank bank = new Bank(sc.nextInt());\n"
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            Bank.Account a = bank.open(sc.next(), sc.nextInt());\n"
              "            System.out.println(a.describe());\n"
              "        }",
              _BANK_REGION33,
              [_case(f"{r}\n{len(rows)}\n" + "\n".join(f"{o} {b}" for (o, b) in rows),
                     _nl(*[f"{o} {b} +{b * r // 100}" for (o, b) in rows]))
               for (r, rows) in _BANKS33],
              ["`ratePercent` belongs to the Bank, not the Account.",
               "An inner class reads it directly - it is `Bank.this.ratePercent`.",
               "`balance * ratePercent / 100` multiplies first, so the division does not "
               "lose everything.",
               "Outside, the type is spelled `Bank.Account`."]),

        _p33t("j33-pd-reverse", "Iterating backwards", "Medium",
              "`Reversed` makes any list iterable from the end. Write `iterator()`'s body: "
              "return an ANONYMOUS `Iterator<String>` holding its own index, starting at "
              "the last element.",
              _REV33,
              "        int n = sc.nextInt();\n"
              "        List<String> items = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            items.add(sc.next());\n"
              "        }\n"
              "        for (String s : new Reversed(items)) {\n"
              "            System.out.println(s);\n"
              "        }\n"
              "        System.out.println(items);",
              _REV_REGION33,
              [_toks33(ws, _nl(*list(reversed(ws)), _jarr(ws))) for ws in _REVS33],
              ["An `Iterator` has two methods, so a lambda cannot implement it.",
               "`new Iterator<String>() { ... }` with a field `index`.",
               "`hasNext()` is `index >= 0`; `next()` returns `items.get(index--)`.",
               "The original list is untouched - the last line proves it."]),

        _p33s("j33-pd-local", "A local class", "Hard",
              "Inside `main`, declare a LOCAL class `Stats` that tracks the count, sum, "
              "minimum and maximum of the numbers added to it. Feed it the input and print "
              "`count sum min max`.",
              "        class Stats {\n"
              "            int count;\n"
              "            int sum;\n"
              "            int min = Integer.MAX_VALUE;\n"
              "            int max = Integer.MIN_VALUE;\n"
              "\n"
              "            void add(int x) {\n"
              "                count++;\n"
              "                sum += x;\n"
              "                min = Math.min(min, x);\n"
              "                max = Math.max(max, x);\n"
              "            }\n"
              "        }\n"
              "        int n = sc.nextInt();\n"
              "        Stats stats = new Stats();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            stats.add(sc.nextInt());\n"
              "        }\n"
              "        System.out.println(stats.count + \" \" + stats.sum + \" \" + stats.min + \" \" + stats.max);",
              [_acase(xs, f"{len(xs)} {sum(xs)} {min(xs)} {max(xs)}")
               for xs in ([3, 1, 2], [7], [-4, -8, -3], [10, 10, 4], [5, -5, 0, 9])],
              ["A class can be declared inside a method body, like a local variable.",
               "It is visible only inside `main`.",
               "Start `min` at `Integer.MAX_VALUE` and `max` at `Integer.MIN_VALUE`.",
               "A local class is rare in practice - but it is the honest shape for a "
               "helper nothing else should see."]),
    ],
)


# --- Family E - state machines ---------------------------------------------------

_SEASON33 = """
enum Season {
    WINTER, SPRING, SUMMER, AUTUMN;

    Season next() {
        return values()[(ordinal() + 1) % values().length];
    }

    Season previous() {
        return values()[Math.floorMod(ordinal() - 1, values().length)];
    }
}
"""
_SEASONS33 = ("WINTER", "SPRING", "SUMMER", "AUTUMN")
_SSTEPS33 = (("WINTER", 1), ("AUTUMN", 1), ("SPRING", 6), ("SUMMER", 0), ("WINTER", 9))
_SBACK33 = (("WINTER", 1), ("SPRING", 1), ("SUMMER", 6), ("AUTUMN", 0), ("SPRING", 9))

_DOOR33 = """
enum DoorState {
    OPEN, CLOSED, LOCKED
}

class Door {
    private DoorState state = DoorState.CLOSED;
    private int ignored;

    void handle(String event) {
        DoorState next = switch (state) {
            case OPEN -> event.equals("close") ? DoorState.CLOSED : null;
            case CLOSED -> switch (event) {
                case "open" -> DoorState.OPEN;
                case "lock" -> DoorState.LOCKED;
                default -> null;
            };
            case LOCKED -> event.equals("unlock") ? DoorState.CLOSED : null;
        };
        if (next == null) {
            ignored++;
        } else {
            state = next;
        }
    }

    DoorState state() {
        return state;
    }

    int ignored() {
        return ignored;
    }
}
"""
_DOOR_REGION33 = (
    "        DoorState next = switch (state) {\n"
    "            case OPEN -> event.equals(\"close\") ? DoorState.CLOSED : null;\n"
    "            case CLOSED -> switch (event) {\n"
    "                case \"open\" -> DoorState.OPEN;\n"
    "                case \"lock\" -> DoorState.LOCKED;\n"
    "                default -> null;\n"
    "            };\n"
    "            case LOCKED -> event.equals(\"unlock\") ? DoorState.CLOSED : null;\n"
    "        };"
)
_DOORT33 = {("OPEN", "close"): "CLOSED", ("CLOSED", "open"): "OPEN",
            ("CLOSED", "lock"): "LOCKED", ("LOCKED", "unlock"): "CLOSED"}
_DOOREVS33 = (["open", "close", "lock"], ["lock", "open", "unlock", "open"], ["close"],
              ["open", "lock", "open", "close", "close"], ["lock", "unlock", "lock", "unlock", "open"])


def _door_out33(evs):
    s, ign, trail = "CLOSED", 0, []
    for e in evs:
        n = _DOORT33.get((s, e))
        if n is None:
            ign += 1
        else:
            s = n
        trail.append(s)
    return _nl(_sp(trail), f"{s} ignored {ign}")


_WORDTEXT33 = ("hello world", "  leading and trailing  ", "one", "a-b c3d", "no...words!!here")


def _words33(s):
    count, inside = 0, False
    for ch in s:
        letter = ch.isascii() and ch.isalpha()
        if letter and not inside:
            count += 1
        inside = letter
    return count


_VEND33 = """
enum VendState {
    IDLE, HAS_COIN
}
"""
_VENDEVS33 = (["coin", "select"], ["select", "coin", "coin", "refund"],
              ["coin", "select", "coin", "select", "select"], ["refund"],
              ["coin", "refund", "coin", "select", "coin"])


def _vend_out33(evs):
    s, vended, out = "IDLE", 0, []
    for e in evs:
        if s == "IDLE":
            if e == "coin":
                s, msg = "HAS_COIN", "accepted"
            else:
                msg = "ignored"
        else:
            if e == "select":
                s, msg = "IDLE", "vended"
                vended += 1
            elif e == "refund":
                s, msg = "IDLE", "refunded"
            else:
                msg = "ignored"
        out.append(f"{e}: {msg}")
    out.append(f"vended {vended}, holding coin: {'true' if s == 'HAS_COIN' else 'false'}")
    return _nl(*out)


_P33_E = _jfam(
    "p33-machines", "State machines",
    "An enum of states, and a switch that says what each event does in each state.",
    """
```java
enum DoorState { OPEN, CLOSED, LOCKED }

DoorState next = switch (state) {           // every state covered, no default
    case OPEN   -> event.equals("close") ? DoorState.CLOSED : null;
    case CLOSED -> switch (event) { case "open" -> DoorState.OPEN;
                                    case "lock" -> DoorState.LOCKED;
                                    default -> null; };
    case LOCKED -> event.equals("unlock") ? DoorState.CLOSED : null;
};
```

Write down the transition table first - state down the side, event across the
top - and the switch is a transcription of it. Everything the table leaves blank
is an invalid event, and it is worth deciding explicitly what that does:
ignore it, count it, or throw.
""",
    [
        _p33t("j33-pe-cycle", "Seasons forward", "Intro",
              "Print the season `k` steps after the given one.",
              _SEASON33,
              "        Season s = Season.valueOf(sc.next());\n"
              "        int k = sc.nextInt();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            s = s.next();\n"
              "        }\n"
              "        System.out.println(s);",
              "        for (int i = 0; i < k; i++) {\n"
              "            s = s.next();\n"
              "        }\n"
              "        System.out.println(s);",
              [_case(f"{s} {k}", _SEASONS33[(_SEASONS33.index(s) + k) % 4]) for (s, k) in _SSTEPS33],
              ["`next()` is already written; call it `k` times.",
               "Assign the result - an enum constant never changes.",
               "Nine steps from WINTER lands on SPRING."]),

        _p33t("j33-pe-back", "Seasons backward", "Easy",
              "Print the season `k` steps BEFORE the given one, using `previous()`.",
              _SEASON33,
              "        Season s = Season.valueOf(sc.next());\n"
              "        int k = sc.nextInt();\n"
              "        for (int i = 0; i < k; i++) {\n"
              "            s = s.previous();\n"
              "        }\n"
              "        System.out.println(s);",
              "        for (int i = 0; i < k; i++) {\n"
              "            s = s.previous();\n"
              "        }\n"
              "        System.out.println(s);",
              [_case(f"{s} {k}", _SEASONS33[(_SEASONS33.index(s) - k) % 4]) for (s, k) in _SBACK33],
              ["`previous()` uses `Math.floorMod(ordinal() - 1, ...)` - module 32 - because "
               "`ordinal() - 1` is -1 for WINTER.",
               "Call it `k` times.",
               "One step back from WINTER is AUTUMN."]),

        _p33t("j33-pe-door", "A door with a lock", "Medium",
              "A door starts CLOSED. OPEN + close → CLOSED; CLOSED + open → OPEN; CLOSED + "
              "lock → LOCKED; LOCKED + unlock → CLOSED. Anything else is ignored and "
              "counted. Write the switch expression that computes `next` (null for an "
              "ignored event).",
              _DOOR33,
              "        int n = sc.nextInt();\n"
              "        Door door = new Door();\n"
              "        StringBuilder trail = new StringBuilder();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            door.handle(sc.next());\n"
              "            if (trail.length() > 0) trail.append(' ');\n"
              "            trail.append(door.state());\n"
              "        }\n"
              "        System.out.println(trail);\n"
              "        System.out.println(door.state() + \" ignored \" + door.ignored());",
              _DOOR_REGION33,
              [_toks33(evs, _door_out33(evs)) for evs in _DOOREVS33],
              ["One arm per state; three states, no `default`.",
               "OPEN and LOCKED accept a single event each: a `? :` is enough.",
               "CLOSED accepts two, so its arm is itself a switch over the event String.",
               "An inner String switch DOES need a `default` - here `null` for 'ignored'."]),

        _p33s("j33-pe-words", "Counting words with two states", "Medium",
              "Count the words in a line, where a word is a maximal run of ASCII letters. "
              "Walk the characters with a two-state machine - INSIDE a word or OUTSIDE - "
              "and count each OUTSIDE → INSIDE transition.",
              "        String line = sc.nextLine();\n"
              "        boolean inside = false;\n"
              "        int words = 0;\n"
              "        for (char c : line.toCharArray()) {\n"
              "            boolean letter = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');\n"
              "            if (letter && !inside) {\n"
              "                words++;\n"
              "            }\n"
              "            inside = letter;\n"
              "        }\n"
              "        System.out.println(words);",
              [_lcase(t, _words33(t)) for t in _WORDTEXT33],
              ["A boolean is a perfectly good two-state machine.",
               "A word STARTS when a letter follows a non-letter.",
               "Update the state after every character: `inside = letter;`.",
               "`a-b c3d` has four words: a, b, c and d."]),

        _p33t("j33-pe-vending", "A vending machine", "Hard",
              "The machine is IDLE or HAS_COIN. IDLE + coin → HAS_COIN (`accepted`). "
              "HAS_COIN + select → IDLE (`vended`); HAS_COIN + refund → IDLE (`refunded`). "
              "Anything else is `ignored` and changes nothing. Print `event: result` per "
              "event, then how many were vended and whether a coin is still held. Write the "
              "whole of `main`'s loop.",
              _VEND33,
              "        int n = sc.nextInt();\n"
              "        VendState state = VendState.IDLE;\n"
              "        int vended = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String event = sc.next();\n"
              "            String result;\n"
              "            switch (state) {\n"
              "                case IDLE -> {\n"
              "                    if (event.equals(\"coin\")) {\n"
              "                        state = VendState.HAS_COIN;\n"
              "                        result = \"accepted\";\n"
              "                    } else {\n"
              "                        result = \"ignored\";\n"
              "                    }\n"
              "                }\n"
              "                case HAS_COIN -> {\n"
              "                    if (event.equals(\"select\")) {\n"
              "                        state = VendState.IDLE;\n"
              "                        vended++;\n"
              "                        result = \"vended\";\n"
              "                    } else if (event.equals(\"refund\")) {\n"
              "                        state = VendState.IDLE;\n"
              "                        result = \"refunded\";\n"
              "                    } else {\n"
              "                        result = \"ignored\";\n"
              "                    }\n"
              "                }\n"
              "                default -> throw new IllegalStateException();\n"
              "            }\n"
              "            System.out.println(event + \": \" + result);\n"
              "        }\n"
              "        System.out.println(\"vended \" + vended + \", holding coin: \" + (state == VendState.HAS_COIN));",
              "        for (int i = 0; i < n; i++) {\n"
              "            String event = sc.next();\n"
              "            String result;\n"
              "            switch (state) {\n"
              "                case IDLE -> {\n"
              "                    if (event.equals(\"coin\")) {\n"
              "                        state = VendState.HAS_COIN;\n"
              "                        result = \"accepted\";\n"
              "                    } else {\n"
              "                        result = \"ignored\";\n"
              "                    }\n"
              "                }\n"
              "                case HAS_COIN -> {\n"
              "                    if (event.equals(\"select\")) {\n"
              "                        state = VendState.IDLE;\n"
              "                        vended++;\n"
              "                        result = \"vended\";\n"
              "                    } else if (event.equals(\"refund\")) {\n"
              "                        state = VendState.IDLE;\n"
              "                        result = \"refunded\";\n"
              "                    } else {\n"
              "                        result = \"ignored\";\n"
              "                    }\n"
              "                }\n"
              "                default -> throw new IllegalStateException();\n"
              "            }\n"
              "            System.out.println(event + \": \" + result);\n"
              "        }",
              [_toks33(evs, _vend_out33(evs)) for evs in _VENDEVS33],
              ["Switch on the STATE; inside each arm, decide on the event.",
               "A switch STATEMENT over an enum is not checked for exhaustiveness, so "
               "`result` would not be definitely assigned without the `default` arm.",
               "`default -> throw new IllegalStateException();` satisfies the compiler "
               "and documents 'cannot happen'.",
               "A second coin while holding one is ignored, not refunded."]),
    ],
)


_PRACTICE[33] = [_P33_A, _P33_B, _P33_C, _P33_D, _P33_E]
