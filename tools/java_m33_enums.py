# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 33 - Enums, switch and nested classes.  Opens Part 13.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# WHY THIS MODULE EXISTS: thirty-two modules in, the course had never declared
# an `enum`, never written a `switch`, and never put one class inside another.
# All three are everyday Java, all three are asked about, and the design
# patterns module (35) leans on every one of them - an enum singleton, a
# strategy per constant, a Builder as a static nested class. So Part 13 opens by
# closing that gap.
#
# `enum `, `switch`, `EnumMap`, `EnumSet`, `static class` and `Iterable<`
# become legal here and nowhere earlier (see _SCOPE_RULES). Using a JDK enum -
# module 32's `DayOfWeek.SATURDAY` - was always fine; DECLARING one is new.
#
# JAVA VERSION: switch EXPRESSIONS and arrow labels (`case A, B -> ...`,
# `yield`) are Java 14+. Lesson 33.3 teaches the classic statement first, then
# the expression, and says which is which.
#
# JUDGING NOTES
#   * EnumMap iterates in DECLARATION order, so printing one is deterministic -
#     unlike a HashMap. That is a lesson point, not only a convenience.
#   * Exception names only, never messages.
# ---------------------------------------------------------------------------

_M33 = []

_IMPORTS33 = ("import java.util.*;\n"
              "import java.util.function.*;\n"
              "import java.time.*;\n")


def _j33s(body):
    return _jscan(body, imports=_IMPORTS33)


def _j33t(types, body):
    """Helper types above Main, then a Scanner-opening main."""
    return _joop(types, body, imports=_IMPORTS33)


def _toks33(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


def _rows33(rows, out):
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


def _jmap33(pairs):
    """How an EnumMap / TreeMap prints."""
    return "{" + ", ".join(f"{k}={v}" for (k, v) in pairs) + "}"


# ===========================================================================
# 33.1 Enums
# ===========================================================================

_DIRS33 = ("NORTH", "EAST", "SOUTH", "WEST")

_DIRECTION33 = """
enum Direction {
    NORTH, EAST, SOUTH, WEST
}
"""

_DTOKS33 = (["NORTH", "WEST"], ["SOUTH"], ["EAST", "EAST", "NORTH"], ["WEST", "SOUTH", "EAST"],
            ["NORTH", "SOUTH", "WEST", "EAST"])
_DMIXED33 = (["north", "West"], ["SOUTH"], ["east", "EaSt", "NORTH"], ["west", "south"],
             ["North", "sOuTh", "WEST", "east"])

_COIN33 = """
enum Coin {
    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);

    private final int cents;

    Coin(int cents) {
        this.cents = cents;
    }

    int cents() {
        return cents;
    }
}
"""

_COIN_BODY33 = (
    "    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);\n"
    "\n"
    "    private final int cents;\n"
    "\n"
    "    Coin(int cents) {\n"
    "        this.cents = cents;\n"
    "    }\n"
    "\n"
    "    int cents() {\n"
    "        return cents;\n"
    "    }"
)

_CENTS33 = {"PENNY": 1, "NICKEL": 5, "DIME": 10, "QUARTER": 25}
_COINS33 = (["QUARTER", "DIME"], ["PENNY"], ["NICKEL", "NICKEL", "PENNY", "QUARTER"],
            ["DIME", "DIME", "DIME"], ["QUARTER", "QUARTER", "QUARTER", "QUARTER", "PENNY"])


def _coins_out33(ts):
    total = sum(_CENTS33[t] for t in ts)
    return _nl(total, _nl(*[f"{t} {_CENTS33[t]}" for t in ts]))


_M33.append(_jlesson(
    "m33-enum", "Enums: a fixed set of objects",
    "Not named integers - a class with exactly the instances you list.",
    """
Before Java 5, a set of options was a handful of constants:

```java
static final int NORTH = 0, EAST = 1, SOUTH = 2, WEST = 3;
void move(int direction) { ... }     // move(42) compiles. So does move(EAST + 7).
```

Nothing stops a caller passing an int that means nothing. An **enum** is the
fix, and it is much more than named numbers:

```java
enum Direction {
    NORTH, EAST, SOUTH, WEST
}

void move(Direction d) { ... }       // only these four values - or null - fit
```

An enum is **a class with a fixed set of instances**. `Direction.NORTH` is an
object, created once when the class loads, and there will never be a fifth
`Direction`. That has consequences:

* **Compare with `==`.** There is exactly one `NORTH`, so identity is equality -
  and `==` cannot throw on null, where `.equals` could.
* **`toString()` and `name()`** both give `"NORTH"`. `name()` is final and always
  the declared name; `toString()` can be overridden for display.
* **`ordinal()`** is the position in the declaration: `NORTH` is 0. Useful for
  arithmetic *within* the enum, and **never** something to store in a file or
  database - reorder the constants and every stored number silently changes
  meaning.
* **`Direction.values()`** returns a fresh array of every constant, in order.
* **`Direction.valueOf("EAST")`** turns a name back into the constant, and
  throws `IllegalArgumentException` for anything else - including `"east"`.
  Names are case-sensitive.

## Enums can have fields

Because an enum is a class, each constant can carry data, passed to a
constructor:

```java
enum Coin {
    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);   // note the semicolon

    private final int cents;

    Coin(int cents) {           // implicitly private: nobody else may call it
        this.cents = cents;
    }

    int cents() { return cents; }
}
```

The constants must come first, and when anything follows them, the list ends
with a `;`. The constructor is always private - it runs exactly once per
constant, and that is the only way instances are ever made.
""",
    warmup=[
        _jq("`Direction.valueOf(\"east\")` when the constant is `EAST`…",
            ["throws IllegalArgumentException", "returns EAST", "returns null",
             "does not compile"],
            0,
            "Names are case-sensitive. Normalise the input first."),
        _jq("Two enum constants are best compared with…",
            ["==", ".equals only", "compareTo", "their ordinals"],
            0,
            "Each constant is a single object, and `==` is null-safe."),
    ],
    exercises=[
        _je("j33-en-valueof", "From text to constant",
            "Read direction names and print each one with its position in the "
            "declaration. Replace `____` with the conversion from the token.",
            _j33t(_DIRECTION33,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String token = sc.next();\n"
                  "            Direction d = Direction.valueOf(token);\n"
                  "            System.out.println(d + \" \" + d.ordinal());\n"
                  "        }"),
            "Direction.valueOf(token)",
            [_toks33(ts, _nl(*[f"{t} {_DIRS33.index(t)}" for t in ts])) for ts in _DTOKS33],
            hints=["Every enum gets a static `valueOf(String)` for free.",
                   "`Direction.valueOf(token)`",
                   "`ordinal()` is the 0-based position in the declaration.",
                   "Printing the constant prints its name."],
            difficulty="Easy"),

        _jfix("j33-en-case", "The name that did not match",
              "Users type directions in any case. `valueOf` is case-sensitive, so this "
              "throws `IllegalArgumentException` on `north`. Normalise the token first - "
              "locale-proof, as module 32 taught.",
              _j33t(_DIRECTION33,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Direction d = Direction.valueOf(sc.next());\n"
                    "            System.out.println(d + \" \" + d.ordinal());\n"
                    "        }"),
              _j33t(_DIRECTION33,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Direction d = Direction.valueOf(sc.next().toUpperCase(Locale.ROOT));\n"
                    "            System.out.println(d + \" \" + d.ordinal());\n"
                    "        }"),
              [_toks33(ts, _nl(*[f"{t.upper()} {_DIRS33.index(t.upper())}" for t in ts]))
               for ts in _DMIXED33],
              hints=["The constant is `NORTH`; `valueOf(\"north\")` finds nothing.",
                     "Upper-case the token before looking it up.",
                     "`toUpperCase(Locale.ROOT)` - in a Turkish locale, a plain "
                     "`toUpperCase()` turns `i` into a dotted capital `İ`, and the lookup "
                     "fails again.",
                     "`Direction.valueOf(sc.next().toUpperCase(Locale.ROOT))`"],
              difficulty="Easy"),

        _je("j33-en-values", "Every constant, in order",
            "Read one direction and print every OTHER direction, in declaration order. "
            "Replace `____` with the array of all the constants.",
            _j33t(_DIRECTION33,
                  "        Direction skip = Direction.valueOf(sc.next());\n"
                  "        for (Direction d : Direction.values()) {\n"
                  "            if (d != skip) {\n"
                  "                System.out.println(d);\n"
                  "            }\n"
                  "        }"),
            "Direction.values()",
            [_case(t, _nl(*[d for d in _DIRS33 if d != t])) for t in _DIRS33],
            hints=["Every enum has a static `values()` returning all its constants.",
                   "The order is the order they were declared in.",
                   "`d != skip` is the right comparison: there is only one of each.",
                   "`values()` returns a new array each call - cache it if you call it "
                   "in a hot loop."],
            difficulty="Easy"),

        _jch("j33-en-coins", "Coins that know their value", "Medium",
             "Write the body of `enum Coin`: four constants carrying their value in cents "
             "(1, 5, 10, 25), a private final field, a constructor and a `cents()` getter. "
             "`main` prints the total and then each coin with its value.",
             _j33t(_COIN33,
                   "        int n = sc.nextInt();\n"
                   "        List<Coin> coins = new ArrayList<>();\n"
                   "        int total = 0;\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Coin c = Coin.valueOf(sc.next());\n"
                   "            coins.add(c);\n"
                   "            total += c.cents();\n"
                   "        }\n"
                   "        System.out.println(total);\n"
                   "        for (Coin c : coins) {\n"
                   "            System.out.println(c + \" \" + c.cents());\n"
                   "        }"),
             _COIN_BODY33,
             [_toks33(ts, _coins_out33(ts)) for ts in _COINS33],
             hints=["Constants first: `PENNY(1), NICKEL(5), DIME(10), QUARTER(25);`",
                    "The `;` after the last constant is required once anything follows.",
                    "`private final int cents;` and a constructor `Coin(int cents)`.",
                    "An enum constructor cannot be public - it is private whether you "
                    "write it or not.",
                    "`int cents() { return cents; }`"]),
    ],
    quiz=[
        _jq("Why should `ordinal()` never be stored in a database?",
            ["reordering the constants silently changes what every stored number means",
             "it is slow", "it can be negative", "it is not unique"],
            0,
            "Store `name()` instead - or a field you control."),
        _jq("An enum constructor is…",
            ["always private", "public by default", "protected", "not allowed"],
            0,
            "Only the enum itself may create its instances, once each."),
    ],
))


# ===========================================================================
# 33.2 Enums with behaviour
# ===========================================================================

_OP33 = """
enum Op {
    ADD("+", (a, b) -> a + b),
    SUB("-", (a, b) -> a - b),
    MUL("*", (a, b) -> a * b);

    private final String symbol;
    private final IntBinaryOperator fn;

    Op(String symbol, IntBinaryOperator fn) {
        this.symbol = symbol;
        this.fn = fn;
    }

    String symbol() {
        return symbol;
    }

    int apply(int a, int b) {
        return fn.applyAsInt(a, b);
    }
}
"""

_OPSYM33 = {"ADD": ("+", lambda a, b: a + b), "SUB": ("-", lambda a, b: a - b),
            "MUL": ("*", lambda a, b: a * b)}
_CALCS33 = ([(3, "ADD", 4)], [(10, "SUB", 12), (6, "MUL", 7)], [(0, "MUL", 99)],
            [(-5, "ADD", 5), (-3, "MUL", -3)], [(100, "SUB", 1), (2, "ADD", 2), (5, "MUL", 5)])


def _calc_out33(rows):
    return _nl(*[f"{a} {_OPSYM33[o][0]} {b} = {_OPSYM33[o][1](a, b)}" for (a, o, b) in rows])


_SHAPE33 = """
enum Shape {
    SQUARE {
        int area(int size) {
            return size * size;
        }
    },
    TRIANGLE {
        int area(int size) {
            return size * size / 2;
        }
    },
    STRIP {
        int area(int size) {
            return size;
        }
    };

    abstract int area(int size);
}
"""

_SHAPE_REGION33 = (
    "    SQUARE {\n"
    "        int area(int size) {\n"
    "            return size * size;\n"
    "        }\n"
    "    },\n"
    "    TRIANGLE {\n"
    "        int area(int size) {\n"
    "            return size * size / 2;\n"
    "        }\n"
    "    },\n"
    "    STRIP {\n"
    "        int area(int size) {\n"
    "            return size;\n"
    "        }\n"
    "    };"
)

_AREA33 = {"SQUARE": lambda s: s * s, "TRIANGLE": lambda s: s * s // 2, "STRIP": lambda s: s}
_SHAPES33 = ([("SQUARE", 3)], [("TRIANGLE", 5), ("STRIP", 7)], [("SQUARE", 0), ("TRIANGLE", 1)],
             [("STRIP", 4), ("SQUARE", 4), ("TRIANGLE", 4)], [("TRIANGLE", 10)])

_SUIT33 = """
enum Suit {
    CLUBS, DIAMONDS, HEARTS, SPADES
}
"""
_SUITS33 = ("CLUBS", "DIAMONDS", "HEARTS", "SPADES")
_HANDS33 = (["HEARTS", "CLUBS", "HEARTS"], ["SPADES"], ["DIAMONDS", "SPADES", "CLUBS", "SPADES"],
            ["HEARTS", "HEARTS", "HEARTS"], ["SPADES", "HEARTS", "DIAMONDS", "CLUBS", "CLUBS"])


def _suit_count33(ts):
    return _jmap33([(s, ts.count(s)) for s in _SUITS33 if s in ts])


_DAY33 = """
enum Day {
    MON, TUE, WED, THU, FRI, SAT, SUN;

    Day next() {
        return values()[(ordinal() + 1) % values().length];
    }
}
"""
_DAYS33 = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
_DAYTOKS33 = (["MON", "SUN"], ["SAT"], ["FRI", "SUN", "WED"], ["SUN"], ["THU", "TUE", "SUN", "MON"])


def _next_out33(ts):
    return _nl(*[f"{t} -> {_DAYS33[(_DAYS33.index(t) + 1) % 7]}" for t in ts])


_M33.append(_jlesson(
    "m33-behaviour", "Enums with behaviour",
    "Methods, a lambda per constant, a body per constant - and `EnumMap`.",
    """
An enum is a class, so it can have methods - and each constant can bring its
own behaviour. There are three ways to do it.

## 1. A field holding a lambda

```java
enum Op {
    ADD("+", (a, b) -> a + b),
    SUB("-", (a, b) -> a - b),
    MUL("*", (a, b) -> a * b);

    private final String symbol;
    private final IntBinaryOperator fn;

    Op(String symbol, IntBinaryOperator fn) { this.symbol = symbol; this.fn = fn; }

    int apply(int a, int b) { return fn.applyAsInt(a, b); }
}
```

Each constant passes module 25's functional interface to the constructor. This is
the **strategy pattern** in five lines, and there is no `if` or `switch` anywhere:
the choice of behaviour *is* the choice of constant.

## 2. A body per constant

```java
enum Shape {
    SQUARE   { int area(int s) { return s * s; } },
    TRIANGLE { int area(int s) { return s * s / 2; } };

    abstract int area(int s);
}
```

The enum declares an `abstract` method and every constant supplies a body - the
compiler refuses to build the enum if one forgets. Each constant is then really
an instance of its own anonymous subclass. Use this when a behaviour is too big
for a one-line lambda.

## 3. An ordinary method using the constant's data

```java
Day next() {
    return values()[(ordinal() + 1) % values().length];
}
```

Wrap-around arithmetic is one of the few legitimate uses of `ordinal()`: it
stays inside the enum, so it can never go stale.

## `EnumMap` and `EnumSet`

```java
Map<Suit, Integer> counts = new EnumMap<>(Suit.class);
Set<Suit> red = EnumSet.of(Suit.HEARTS, Suit.DIAMONDS);
EnumSet.allOf(Suit.class)     EnumSet.noneOf(Suit.class)     EnumSet.range(MON, FRI)
```

When the keys are an enum, these beat `HashMap` and `HashSet` twice over. They
are backed by an array indexed by ordinal (an `EnumSet` is literally a bit
field), so they are faster and smaller. And **they iterate in declaration
order** - so printing an `EnumMap` gives the same line on every run, which a
`HashMap` never promises.
""",
    warmup=[
        _jq("An `EnumMap<Suit, Integer>` iterates its keys in…",
            ["the order the constants are declared", "insertion order",
             "alphabetical order", "no defined order"],
            0,
            "It is an array indexed by ordinal."),
        _jq("An enum declares `abstract int area(int s);`. A constant with no body…",
            ["does not compile", "returns 0", "throws at run time", "inherits a default"],
            0,
            "Every constant must supply the method."),
    ],
    exercises=[
        _je("j33-bh-op", "A calculator with no `if`",
            "Each line is `a OP b` with OP one of `ADD`, `SUB`, `MUL`. Print `a symbol b = "
            "result`. Replace `____` with the call that computes the result.",
            _j33t(_OP33,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            int a = sc.nextInt();\n"
                  "            Op op = Op.valueOf(sc.next());\n"
                  "            int b = sc.nextInt();\n"
                  "            System.out.println(a + \" \" + op.symbol() + \" \" + b + \" = \" + op.apply(a, b));\n"
                  "        }"),
            "op.apply(a, b)",
            [_rows33(rows, _calc_out33(rows)) for rows in _CALCS33],
            hints=["The constant already knows how to compute - ask it.",
                   "`op.apply(a, b)` calls the lambda stored in that constant.",
                   "Adding a DIV constant would need no change to `main` at all.",
                   "This is the strategy pattern with an enum as the registry."],
            difficulty="Easy"),

        _jch("j33-bh-abstract", "A body per constant", "Medium",
             "`Shape` declares `abstract int area(int size)`. Write its three constants, "
             "each with its own body: a SQUARE's area is size², a TRIANGLE's is size²/2 "
             "(integer division), and a STRIP's is just size.",
             _j33t(_SHAPE33,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Shape s = Shape.valueOf(sc.next());\n"
                   "            int size = sc.nextInt();\n"
                   "            System.out.println(s + \" \" + s.area(size));\n"
                   "        }"),
             _SHAPE_REGION33,
             [_rows33(rows, _nl(*[f"{s} {_AREA33[s](z)}" for (s, z) in rows]))
              for rows in _SHAPES33],
             hints=["Each constant is followed by a class body in braces: `SQUARE { ... },`",
                    "Inside, implement `int area(int size)`.",
                    "Constants are separated by commas and the last ends with `;`.",
                    "Forgetting one body is a compile error - the enum's abstract method "
                    "demands it."]),

        _je("j33-bh-enummap", "Counting by suit",
            "Count how many cards of each suit were dealt and print the map. Replace "
            "`____` with the map's construction.",
            _j33t(_SUIT33,
                  "        int n = sc.nextInt();\n"
                  "        Map<Suit, Integer> counts = new EnumMap<>(Suit.class);\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            Suit s = Suit.valueOf(sc.next());\n"
                  "            counts.merge(s, 1, Integer::sum);\n"
                  "        }\n"
                  "        System.out.println(counts);"),
            "new EnumMap<>(Suit.class)",
            [_toks33(ts, _suit_count33(ts)) for ts in _HANDS33],
            hints=["`EnumMap` needs the enum's `Class` object to size its array.",
                   "`new EnumMap<>(Suit.class)`",
                   "It prints in DECLARATION order - CLUBS before HEARTS - whatever order "
                   "the cards came in.",
                   "`merge(s, 1, Integer::sum)` is module 31's counting idiom."],
            difficulty="Easy"),

        _jfix("j33-bh-next", "The day after Sunday",
              "`next()` should wrap round from SUN to MON, but it throws "
              "`ArrayIndexOutOfBoundsException` for SUN. Fix it.",
              _j33t(_DAY33.replace("return values()[(ordinal() + 1) % values().length];",
                                   "return values()[ordinal() + 1];"),
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Day d = Day.valueOf(sc.next());\n"
                    "            System.out.println(d + \" -> \" + d.next());\n"
                    "        }"),
              _j33t(_DAY33,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Day d = Day.valueOf(sc.next());\n"
                    "            System.out.println(d + \" -> \" + d.next());\n"
                    "        }"),
              [_toks33(ts, _next_out33(ts)) for ts in _DAYTOKS33],
              hints=["SUN is the last constant: `ordinal()` is 6, and there is no index 7.",
                     "Wrap the index round with `%`.",
                     "`values()[(ordinal() + 1) % values().length]`",
                     "The ordinal never goes negative, so `%` is safe here - no floorMod "
                     "needed."],
              difficulty="Easy"),
    ],
    quiz=[
        _jq("Giving each enum constant a lambda field is an example of…",
            ["the strategy pattern", "the singleton pattern", "inheritance",
             "reflection"],
            0,
            "The behaviour is chosen by choosing the constant."),
        _jq("Why prefer `EnumMap` to `HashMap` for enum keys?",
            ["faster, smaller, and iterates in declaration order",
             "it allows null keys", "it is thread-safe", "it sorts values"],
            0,
            "An array indexed by ordinal beats hashing."),
    ],
))


# ===========================================================================
# 33.3 switch
# ===========================================================================

_GRADES33 = (["A", "C"], ["B"], ["F", "A", "B"], ["C", "C"], ["B", "F"])
_GRADEMSG33 = {"A": "excellent", "B": "good", "C": "pass"}


def _grade_out33(ts):
    return _nl(*[_GRADEMSG33.get(t, "try again") for t in ts])


_WDATES33 = (["2024-03-02", "2024-03-04"], ["2024-03-03"], ["2023-12-25", "2023-12-30", "2024-01-05"],
             ["2024-02-29"], ["2024-03-09", "2024-03-10", "2024-03-11"])


def _kind33(iso):
    return "weekend" if _d32(iso).weekday() >= 5 else "weekday"


_CMDS33 = (
    [("push", 3), ("push", 4), ("peek",), ("pop",), ("peek",)],
    [("push", 1), ("pop",), ("pop",)],
    [("peek",), ("push", 9)],
    [("push", 5), ("push", 6), ("push", 7), ("pop",), ("pop",), ("pop",)],
    [("pop",), ("push", 2), ("size",), ("pop",), ("size",)],
)


def _cmd_out33(cmds):
    stack, out = [], []
    for c in cmds:
        if c[0] == "push":
            stack.append(c[1])
        elif c[0] == "pop":
            out.append(str(stack.pop()) if stack else "empty")
        elif c[0] == "peek":
            out.append(str(stack[-1]) if stack else "empty")
        else:
            out.append(f"size {len(stack)}")
    return _nl(*out)


def _cmd_case33(cmds):
    return _case("\n".join([str(len(cmds))] + [" ".join(str(x) for x in c) for c in cmds]),
                 _cmd_out33(cmds))


_ZONE33 = """
enum Zone {
    LOCAL, NATIONAL, INTERNATIONAL
}
"""
_PARCELS33 = ([("LOCAL", 3)], [("NATIONAL", 5), ("NATIONAL", 8)], [("INTERNATIONAL", 1)],
              [("LOCAL", 20), ("NATIONAL", 6), ("INTERNATIONAL", 4)], [("NATIONAL", 0)])


def _ship33(zone, w):
    if zone == "LOCAL":
        return 5
    if zone == "NATIONAL":
        return 10 + (w - 5) * 2 if w > 5 else 10
    return 25 + w * 3


_M33.append(_jlesson(
    "m33-switch", "`switch` - the statement and the expression",
    "The classic statement falls through. The Java 14 expression does not, and must "
    "cover every case.",
    """
## The statement, and the bug it is famous for

```java
switch (grade) {
    case "A":
        System.out.println("excellent");
        break;
    case "B":
        System.out.println("good");
        break;
    default:
        System.out.println("try again");
}
```

A `switch` statement jumps to the matching label and then **keeps going** until
it hits a `break` - straight through every following label. Leave out one
`break` and a single `"A"` prints `excellent`, `good` *and* `try again`. That
fall-through is occasionally useful (several labels sharing one body) and far
more often a bug.

You can switch on an `int`, `char`, `String` or enum (and their wrappers). With
an enum you write the bare constant name - `case SATURDAY:`, not
`case DayOfWeek.SATURDAY:`.

## The expression (Java 14)

```java
String kind = switch (day) {
    case SATURDAY, SUNDAY -> "weekend";
    default -> "weekday";
};
```

Three differences, each fixing a problem with the statement:

1. **Arrow labels never fall through.** Each arm runs exactly its own code.
2. **Several labels share an arm** with a comma - no fall-through needed.
3. **It is an expression**: it produces a value, so the variable is assigned in
   exactly one place, and it ends with a `;`.

An arm that needs more than one line uses a block and **`yield`** to produce its
value:

```java
int cost = switch (zone) {
    case LOCAL -> 5;
    case NATIONAL -> {
        int base = 10;
        yield weight > 5 ? base + (weight - 5) * 2 : base;
    }
    case INTERNATIONAL -> 25 + weight * 3;
};
```

## Exhaustiveness

A switch *expression* must produce a value for **every** possible input. Over an
enum, covering every constant is enough - no `default` needed - and then adding
a new constant later turns every switch that forgot it into a **compile error**.
A switch *statement* with a missing case compiles happily and silently does
nothing. That difference alone is a reason to prefer the expression.
""",
    warmup=[
        _jq("A `switch` statement case with no `break`…",
            ["falls through into the next case's code", "is a compile error",
             "returns", "skips the rest of the switch"],
            0,
            "Execution continues until a `break` or the end of the switch."),
        _jq("In a switch EXPRESSION, a block arm produces its value with…",
            ["yield", "return", "break", "the last expression"],
            0,
            "`return` would return from the whole method."),
    ],
    exercises=[
        _jfix("j33-sw-fallthrough", "Excellent, good, pass, try again",
              "A grade of `A` should print one line, `excellent`. This prints four, "
              "because every case falls into the next. Fix the switch.",
              _j33s("        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String grade = sc.next();\n"
                    "            switch (grade) {\n"
                    "                case \"A\":\n"
                    "                    System.out.println(\"excellent\");\n"
                    "                case \"B\":\n"
                    "                    System.out.println(\"good\");\n"
                    "                case \"C\":\n"
                    "                    System.out.println(\"pass\");\n"
                    "                default:\n"
                    "                    System.out.println(\"try again\");\n"
                    "            }\n"
                    "        }"),
              _j33s("        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String grade = sc.next();\n"
                    "            switch (grade) {\n"
                    "                case \"A\":\n"
                    "                    System.out.println(\"excellent\");\n"
                    "                    break;\n"
                    "                case \"B\":\n"
                    "                    System.out.println(\"good\");\n"
                    "                    break;\n"
                    "                case \"C\":\n"
                    "                    System.out.println(\"pass\");\n"
                    "                    break;\n"
                    "                default:\n"
                    "                    System.out.println(\"try again\");\n"
                    "            }\n"
                    "        }"),
              [_toks33(ts, _grade_out33(ts)) for ts in _GRADES33],
              hints=["A statement switch keeps executing after its matching label.",
                     "Only `F` - which goes straight to `default` - is right already.",
                     "Add `break;` at the end of each case.",
                     "Or rewrite it as a switch with arrow labels, which cannot fall "
                     "through."],
              difficulty="Easy"),

        _je("j33-sw-arrow", "Weekday or weekend",
            "Print each date with `weekend` or `weekday`, using a switch expression over "
            "its `DayOfWeek`. Replace `____` with the arm that covers both weekend days.",
            _j33s("        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            LocalDate date = LocalDate.parse(sc.next());\n"
                  "            String kind = switch (date.getDayOfWeek()) {\n"
                  "                case SATURDAY, SUNDAY -> \"weekend\";\n"
                  "                default -> \"weekday\";\n"
                  "            };\n"
                  "            System.out.println(date + \" \" + kind);\n"
                  "        }"),
            "                case SATURDAY, SUNDAY -> \"weekend\";",
            [_toks33(ds, _nl(*[f"{x} {_kind33(x)}" for x in ds])) for ds in _WDATES33],
            hints=["Several labels can share one arm, separated by commas.",
                   "Inside a switch over an enum, write the bare constant: `SATURDAY`, not "
                   "`DayOfWeek.SATURDAY`.",
                   "`case SATURDAY, SUNDAY -> \"weekend\";`",
                   "`DayOfWeek` has seven constants, so the `default` is needed here."],
            difficulty="Easy"),

        _je("j33-sw-string", "A command interpreter",
            "Run stack commands: `push x`, `pop`, `peek` and `size`. `pop` and `peek` "
            "print the value, or `empty`. Replace `____` with the `pop` case.",
            _j33s("        int n = sc.nextInt();\n"
                  "        Deque<Integer> stack = new ArrayDeque<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String cmd = sc.next();\n"
                  "            switch (cmd) {\n"
                  "                case \"push\" -> stack.push(sc.nextInt());\n"
                  "                case \"pop\" -> System.out.println(stack.isEmpty() ? \"empty\" : String.valueOf(stack.pop()));\n"
                  "                case \"peek\" -> System.out.println(stack.isEmpty() ? \"empty\" : String.valueOf(stack.peek()));\n"
                  "                case \"size\" -> System.out.println(\"size \" + stack.size());\n"
                  "                default -> System.out.println(\"unknown \" + cmd);\n"
                  "            }\n"
                  "        }"),
            "                case \"pop\" -> System.out.println(stack.isEmpty() ? \"empty\" : String.valueOf(stack.pop()));",
            [_cmd_case33(c) for c in _CMDS33],
            hints=["Arrow labels work in a switch STATEMENT too - and do not fall through.",
                   "Switching on a `String` compares with `equals`, not `==`.",
                   "Mirror the `peek` case, but call `pop()`.",
                   "Both branches of `? :` must be Strings, hence `String.valueOf`."],
            difficulty="Medium"),

        _jch("j33-sw-yield", "Shipping by zone", "Medium",
             "Compute each parcel's cost with a switch EXPRESSION over its `Zone`: LOCAL "
             "costs 5; NATIONAL costs 10, plus 2 per kilogram over 5; INTERNATIONAL costs "
             "25 plus 3 per kilogram. Cover every constant, with no `default`.",
             _j33t(_ZONE33,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            Zone zone = Zone.valueOf(sc.next());\n"
                   "            int weight = sc.nextInt();\n"
                   "            int cost = switch (zone) {\n"
                   "                case LOCAL -> 5;\n"
                   "                case NATIONAL -> {\n"
                   "                    int base = 10;\n"
                   "                    yield weight > 5 ? base + (weight - 5) * 2 : base;\n"
                   "                }\n"
                   "                case INTERNATIONAL -> 25 + weight * 3;\n"
                   "            };\n"
                   "            System.out.println(zone + \" \" + weight + \" \" + cost);\n"
                   "        }"),
             "            int cost = switch (zone) {\n"
             "                case LOCAL -> 5;\n"
             "                case NATIONAL -> {\n"
             "                    int base = 10;\n"
             "                    yield weight > 5 ? base + (weight - 5) * 2 : base;\n"
             "                }\n"
             "                case INTERNATIONAL -> 25 + weight * 3;\n"
             "            };",
             [_rows33(rows, _nl(*[f"{z} {w} {_ship33(z, w)}" for (z, w) in rows]))
              for rows in _PARCELS33],
             hints=["`int cost = switch (zone) { ... };` - it is an expression, so it ends "
                    "with `;`.",
                    "One-line arms: `case LOCAL -> 5;`",
                    "A multi-line arm is a block that ends with `yield value;`.",
                    "No `default`: covering all three constants makes the switch "
                    "exhaustive.",
                    "Add a fourth Zone later and this line stops compiling - which is the "
                    "point."]),
    ],
    quiz=[
        _jq("A switch EXPRESSION over an enum covers every constant, and a new constant is "
            "added later. The switch…",
            ["no longer compiles until the new constant is handled",
             "silently returns 0", "throws at run time", "falls through"],
            0,
            "Exhaustiveness is checked by the compiler."),
        _jq("`case SATURDAY, SUNDAY -> \"weekend\";` shows…",
            ["several labels sharing one arrow arm", "fall-through",
             "a type pattern", "a label with a guard"],
            0,
            "No fall-through needed to share code."),
    ],
))


# ===========================================================================
# 33.4 Nested classes
# ===========================================================================

_STACK33 = """
class IntStack {
    private static class Node {
        final int value;
        final Node next;

        Node(int value, Node next) {
            this.value = value;
            this.next = next;
        }
    }

    private Node top;
    private int size;

    void push(int x) {
        top = new Node(x, top);
        size++;
    }

    int pop() {
        int v = top.value;
        top = top.next;
        size--;
        return v;
    }

    boolean isEmpty() {
        return top == null;
    }

    int size() {
        return size;
    }
}
"""

_PUSHES33 = ([1, 2, 3], [7], [5, 5, 9, 1], [10, 20], [4, 3, 2, 1, 0])

_RANGE33 = """
class Range implements Iterable<Integer> {
    private final int start;
    private final int end;
    private final int step;

    Range(int start, int end, int step) {
        this.start = start;
        this.end = end;
        this.step = step;
    }

    @Override
    public Iterator<Integer> iterator() {
        return new RangeIterator();
    }

    private class RangeIterator implements Iterator<Integer> {
        private int next = start;

        @Override
        public boolean hasNext() {
            return next < end;
        }

        @Override
        public Integer next() {
            int value = next;
            next += step;
            return value;
        }
    }
}
"""

_RANGE_REGION33 = (
    "    private class RangeIterator implements Iterator<Integer> {\n"
    "        private int next = start;\n"
    "\n"
    "        @Override\n"
    "        public boolean hasNext() {\n"
    "            return next < end;\n"
    "        }\n"
    "\n"
    "        @Override\n"
    "        public Integer next() {\n"
    "            int value = next;\n"
    "            next += step;\n"
    "            return value;\n"
    "        }\n"
    "    }"
)

_RANGES33 = ((0, 5, 1), (2, 11, 3), (5, 5, 1), (-3, 3, 2), (10, 12, 5))


def _range_out33(a, b, s):
    xs = list(range(a, b, s))
    return _nl(_sp(xs) if xs else "(none)", len(xs))


_TEAM33 = """
class Team {
    private final String name;
    private final List<Player> players = new ArrayList<>();

    Team(String name) {
        this.name = name;
    }

    class Player {
        private final String name;

        Player(String name) {
            this.name = name;
        }

        String badge() {
            return name + " (" + Team.this.name + ")";
        }
    }

    void add(String playerName) {
        players.add(new Player(playerName));
    }

    void printBadges() {
        for (Player p : players) {
            System.out.println(p.badge());
        }
    }
}
"""

_TEAMS33 = (("lions", ["ada", "bo"]), ("owls", ["cy"]), ("foxes", ["x", "y", "z"]),
            ("bees", ["solo"]), ("crows", ["pear", "fig"]))

_ANONS33 = (["pear", "fig", "banana", "kiwi"], ["bb", "a", "ccc", "aa"], ["solo"],
            ["dd", "cc", "bb", "aa"], ["x", "yyy", "zz", "w"])


_M33.append(_jlesson(
    "m33-nested", "Classes inside classes",
    "Static nested, inner, local and anonymous - and the hidden reference that tells "
    "them apart.",
    """
Every class so far has been top-level. Java also lets you declare a class
**inside** another, in four flavours - and the difference that matters is a
single hidden field.

## Static nested class

```java
class IntStack {
    private static class Node {       // belongs to IntStack, but needs no IntStack
        final int value;
        final Node next;
        Node(int value, Node next) { this.value = value; this.next = next; }
    }
    private Node top;
    void push(int x) { top = new Node(x, top); }
}
```

A `static` nested class is an ordinary class that happens to live inside
another: it can be `private` (so nothing outside the stack even knows `Node`
exists), and it can see its outer class's private members - but it has **no
link to any outer instance**. This is the default choice, and the right one for
helpers like a list node or a `Builder` (module 35).

## Inner class (non-static)

```java
class Range implements Iterable<Integer> {
    private final int start, end;
    private class RangeIterator implements Iterator<Integer> {
        private int next = start;         // reads the OUTER object's field
        ...
    }
    public Iterator<Integer> iterator() { return new RangeIterator(); }
}
```

An inner class carries a hidden reference to the outer object that created it,
so it can read that object's fields directly - here, the `Range`'s `start` and
`end`. That is exactly what an iterator needs. When a name is shadowed, the outer
one is spelled **`Range.this.start`**.

The hidden reference has a cost: an inner-class object keeps its outer object
alive for as long as it lives. A long-lived inner object can quietly pin a large
outer one in memory, which is why "make it `static` unless it needs the outer
instance" is the rule.

## Local and anonymous classes

A **local class** is declared inside a method body and is visible only there. An
**anonymous class** is declared and instantiated in one expression:

```java
words.sort(new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return Integer.compare(a.length(), b.length());
    }
});
```

Before lambdas, this was how you passed behaviour around. Since module 25 a lambda
does it in one line - *when the interface has one abstract method*. An anonymous
class is still needed for anything else: an interface with several methods, an
abstract class, or an object that needs its own state. (One more difference:
inside an anonymous class, `this` is the anonymous object; inside a lambda it is
the enclosing one.)

## Making something iterable

`implements Iterable<Integer>` with an `iterator()` method is all the enhanced
`for` loop needs:

```java
for (int x : new Range(0, 10, 3)) { ... }   // 0 3 6 9
```
""",
    warmup=[
        _jq("An inner (non-static) class instance…",
            ["holds a hidden reference to its outer instance",
             "cannot see the outer class's private fields", "must be public",
             "cannot have fields"],
            0,
            "Which is how it reads the outer fields - and why it can pin them in memory."),
        _jq("A class needs `for (int x : obj)` to work. It must…",
            ["implement Iterable<Integer>", "extend ArrayList", "be an enum",
             "have a public size() method"],
            0,
            "The enhanced for loop calls `iterator()`."),
    ],
    exercises=[
        _je("j33-ne-node", "A private node",
            "`IntStack` keeps its elements in a private static nested `Node` class. Push "
            "every number, then pop them all. Replace `____` with the line that pushes a "
            "new node on top.",
            _j33t(_STACK33,
                  _RD_ARR
                  + "        IntStack stack = new IntStack();\n"
                    "        for (int x : a) {\n"
                    "            stack.push(x);\n"
                    "        }\n"
                    "        System.out.println(stack.size());\n"
                    "        StringBuilder out = new StringBuilder();\n"
                    "        while (!stack.isEmpty()) {\n"
                    "            if (out.length() > 0) out.append(' ');\n"
                    "            out.append(stack.pop());\n"
                    "        }\n"
                    "        System.out.println(out);"),
            "        top = new Node(x, top);",
            [_acase(xs, _nl(len(xs), _sp(list(reversed(xs))))) for xs in _PUSHES33],
            hints=["The new node's `next` is the current top.",
                   "`new Node(x, top)` - `Node` is visible inside `IntStack` even though "
                   "it is private.",
                   "Then the new node BECOMES the top.",
                   "Nothing outside `IntStack` can name `Node` at all - that is the "
                   "encapsulation."],
            difficulty="Easy"),

        _jch("j33-ne-iterator", "An inner iterator", "Hard",
             "Make `Range` work in an enhanced `for` loop. Write the private INNER class "
             "`RangeIterator`: it starts at the range's `start`, and hands out `start`, "
             "`start + step`, ... while below `end`.",
             _j33t(_RANGE33,
                   "        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        int s = sc.nextInt();\n"
                   "        StringBuilder out = new StringBuilder();\n"
                   "        int count = 0;\n"
                   "        for (int x : new Range(a, b, s)) {\n"
                   "            if (out.length() > 0) out.append(' ');\n"
                   "            out.append(x);\n"
                   "            count++;\n"
                   "        }\n"
                   "        System.out.println(count == 0 ? \"(none)\" : out.toString());\n"
                   "        System.out.println(count);"),
             _RANGE_REGION33,
             [_case(f"{a} {b} {s}", _range_out33(a, b, s)) for (a, b, s) in _RANGES33],
             hints=["`private class RangeIterator implements Iterator<Integer>` - no "
                    "`static`, because it reads the outer Range's fields.",
                    "A field `next`, initialised from the outer `start`.",
                    "`hasNext()` is `next < end`.",
                    "`next()` returns the current value, then advances by `step`.",
                    "`iterator()` is already written: it returns `new RangeIterator()`."]),

        _jfix("j33-ne-outer", "Whose name is it?",
              "Each badge should read `player (team)`, but it prints the player's name "
              "twice: inside `Player`, `this.name` is the PLAYER's field. Refer to the "
              "enclosing team's name instead.",
              _j33t(_TEAM33.replace("Team.this.name", "this.name"),
                    "        Team team = new Team(sc.next());\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            team.add(sc.next());\n"
                    "        }\n"
                    "        team.printBadges();"),
              _j33t(_TEAM33,
                    "        Team team = new Team(sc.next());\n"
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            team.add(sc.next());\n"
                    "        }\n"
                    "        team.printBadges();"),
              [_case(f"{t}\n{len(ps)}\n{' '.join(ps)}", _nl(*[f"{p} ({t})" for p in ps]))
               for (t, ps) in _TEAMS33],
              hints=["`Player` has its own `name` field, which shadows the team's.",
                     "`this` inside `Player` is the player.",
                     "The enclosing instance is `Team.this`.",
                     "`Team.this.name`"],
              difficulty="Medium"),

        _je("j33-ne-anon", "The way it was done before lambdas",
            "Sort the words by length, then alphabetically, using an ANONYMOUS "
            "`Comparator` class. Replace `____` with the line that starts it.",
            _j33s("        int n = sc.nextInt();\n"
                  "        List<String> words = new ArrayList<>();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            words.add(sc.next());\n"
                  "        }\n"
                  "        words.sort(new Comparator<String>() {\n"
                  "            @Override\n"
                  "            public int compare(String a, String b) {\n"
                  "                if (a.length() != b.length()) {\n"
                  "                    return Integer.compare(a.length(), b.length());\n"
                  "                }\n"
                  "                return a.compareTo(b);\n"
                  "            }\n"
                  "        });\n"
                  "        System.out.println(words);"),
            "        words.sort(new Comparator<String>() {",
            [_toks33(ws, _jarr(sorted(ws, key=lambda w: (len(w), w)))) for ws in _ANONS33],
            hints=["An anonymous class is `new Interface() { ...body... }`.",
                   "`new Comparator<String>() {` opens it; the body is already written.",
                   "It is closed by `}` and then the `)` of `sort(`.",
                   "The lambda version is one line: "
                   "`Comparator.comparing(String::length).thenComparing(...)`."],
            difficulty="Easy"),
    ],
    quiz=[
        _jq("A list's `Node` class should normally be…",
            ["a private static nested class", "an inner class", "a public top-level class",
             "an anonymous class"],
            0,
            "It needs no link to any particular list object."),
        _jq("Inside an anonymous class, `this` refers to…",
            ["the anonymous object", "the enclosing object", "the interface",
             "nothing - it is illegal"],
            0,
            "Unlike a lambda, where `this` is the enclosing object."),
    ],
))


# ===========================================================================
# 33.5 State machines
# ===========================================================================

_LIGHT33 = """
enum Light {
    RED, GREEN, YELLOW;

    Light next() {
        return values()[(ordinal() + 1) % values().length];
    }
}
"""
_LIGHTS33 = ("RED", "GREEN", "YELLOW")
_LSTEPS33 = (("RED", 3), ("YELLOW", 1), ("GREEN", 5), ("RED", 0), ("YELLOW", 4))


def _lights_out33(start, k):
    i = _LIGHTS33.index(start)
    return _sp([_LIGHTS33[(i + j) % 3] for j in range(k + 1)])


_TURN33 = """
enum State {
    LOCKED, UNLOCKED
}

class Turnstile {
    private State state = State.LOCKED;
    private int wastedCoins;
    private int blockedPushes;

    void handle(String event) {
        state = switch (state) {
            case LOCKED -> {
                if (event.equals("COIN")) {
                    yield State.UNLOCKED;
                }
                blockedPushes++;
                yield State.LOCKED;
            }
            case UNLOCKED -> {
                if (event.equals("PUSH")) {
                    yield State.LOCKED;
                }
                wastedCoins++;
                yield State.UNLOCKED;
            }
        };
    }

    String report() {
        return state + " " + wastedCoins + " " + blockedPushes;
    }
}
"""

_TURN_REGION33 = (
    "        state = switch (state) {\n"
    "            case LOCKED -> {\n"
    "                if (event.equals(\"COIN\")) {\n"
    "                    yield State.UNLOCKED;\n"
    "                }\n"
    "                blockedPushes++;\n"
    "                yield State.LOCKED;\n"
    "            }\n"
    "            case UNLOCKED -> {\n"
    "                if (event.equals(\"PUSH\")) {\n"
    "                    yield State.LOCKED;\n"
    "                }\n"
    "                wastedCoins++;\n"
    "                yield State.UNLOCKED;\n"
    "            }\n"
    "        };"
)

_EVENTS33 = (["COIN", "PUSH"], ["PUSH", "PUSH", "COIN"], ["COIN", "COIN", "COIN", "PUSH", "PUSH"],
             ["PUSH"], ["COIN", "PUSH", "COIN", "COIN", "PUSH", "PUSH"])


def _turn_out33(evs):
    state, wasted, blocked, trail = "LOCKED", 0, 0, []
    for e in evs:
        if state == "LOCKED":
            if e == "COIN":
                state = "UNLOCKED"
            else:
                blocked += 1
        else:
            if e == "PUSH":
                state = "LOCKED"
            else:
                wasted += 1
        trail.append(state)
    return _nl(_sp(trail), f"{state} {wasted} {blocked}")


_STATUS33 = """
enum Status {
    PLACED, PAID, SHIPPED, DELIVERED
}
"""
_STATUSES33 = ("PLACED", "PAID", "SHIPPED", "DELIVERED")
_LABEL33 = {"PLACED": "waiting for payment", "PAID": "being packed",
            "SHIPPED": "on its way", "DELIVERED": "arrived"}
_STOKS33 = (["PLACED", "SHIPPED"], ["SHIPPED"], ["PAID", "DELIVERED", "SHIPPED"],
            ["DELIVERED"], ["SHIPPED", "PLACED", "SHIPPED", "PAID"])

_LABEL_BUGGY33 = (
    "            String label = \"?\";\n"
    "            switch (s) {\n"
    "                case PLACED -> label = \"waiting for payment\";\n"
    "                case PAID -> label = \"being packed\";\n"
    "                case DELIVERED -> label = \"arrived\";\n"
    "            }\n"
)
_LABEL_FIXED33 = (
    "            String label = switch (s) {\n"
    "                case PLACED -> \"waiting for payment\";\n"
    "                case PAID -> \"being packed\";\n"
    "                case SHIPPED -> \"on its way\";\n"
    "                case DELIVERED -> \"arrived\";\n"
    "            };\n"
)

_VOTES33 = (["PAID", "PLACED", "PAID"], ["DELIVERED"], ["SHIPPED", "SHIPPED", "PLACED"],
            ["PLACED", "PAID", "SHIPPED", "DELIVERED"], ["DELIVERED", "DELIVERED"])


_M33.append(_jlesson(
    "m33-machines", "State machines: enums and switch together",
    "A set of states, a set of events, and one switch that says what happens next.",
    """
A **state machine** is a thing that is always in exactly one of a fixed set of
states, and moves between them in response to events. A traffic light, a
turnstile, an order, a TCP connection, a game character - all of them. It is the
place enums and switch expressions were made for:

* the **states** are an enum, so an invalid state cannot even be written down;
* the **transition** is a switch expression over the current state, so the
  compiler checks that every state has been handled.

```java
enum State { LOCKED, UNLOCKED }

state = switch (state) {
    case LOCKED   -> event.equals("COIN") ? State.UNLOCKED : State.LOCKED;
    case UNLOCKED -> event.equals("PUSH") ? State.LOCKED   : State.UNLOCKED;
};
```

Two design choices worth making deliberately:

**Where does the transition live?** For a small machine, one switch in one
method, as above, is clearest - the whole behaviour is on one screen. For a
large one, each constant can carry its own `next(event)` body (lesson 33.2's
constant-specific methods), so each state's rules sit with that state.

**Cyclic machines** - a traffic light - need no switch at all: `next()` is
`values()[(ordinal() + 1) % values().length]`, and the declaration order *is*
the cycle.

And the lesson from 33.3 matters most here. A switch **statement** that forgets
a state compiles and silently does nothing when that state turns up. A switch
**expression** that forgets one does not compile. For a state machine - where
"we added a state and forgot to handle it" is the most common bug of all - that
is the difference between a compile error today and a stuck order in
production.

Counting how often each state or event occurs is an `EnumMap` job; iterating
`values()` prints every constant, including the ones with a count of zero.
""",
    warmup=[
        _jq("A traffic light's `next()` can be written with no switch because…",
            ["the declaration order is the cycle", "enums cannot be switched on",
             "switch is slow", "ordinal() is random"],
            0,
            "`values()[(ordinal() + 1) % values().length]`."),
        _jq("A new state is added to an enum. Which switch keeps compiling and silently "
            "ignores it?",
            ["a switch statement with no default", "an exhaustive switch expression",
             "both", "neither"],
            0,
            "Only the expression is checked for exhaustiveness."),
    ],
    exercises=[
        _je("j33-sm-light", "A traffic light",
            "Start at a colour and print it, then the next `k` colours of the cycle RED, "
            "GREEN, YELLOW - all on one line. Replace `____` with `next()`'s return "
            "expression.",
            _j33t(_LIGHT33,
                  "        Light light = Light.valueOf(sc.next());\n"
                  "        int k = sc.nextInt();\n"
                  "        StringBuilder out = new StringBuilder(light.toString());\n"
                  "        for (int i = 0; i < k; i++) {\n"
                  "            light = light.next();\n"
                  "            out.append(' ').append(light);\n"
                  "        }\n"
                  "        System.out.println(out);"),
            "values()[(ordinal() + 1) % values().length]",
            [_case(f"{s} {k}", _lights_out33(s, k)) for (s, k) in _LSTEPS33],
            hints=["The declaration order is the order of the cycle.",
                   "Take the next ordinal, wrapping round with `%`.",
                   "`values()[(ordinal() + 1) % values().length]`",
                   "Reordering the constants would change the cycle - which here is "
                   "exactly right."],
            difficulty="Easy"),

        _jch("j33-sm-turnstile", "A turnstile", "Hard",
             "Write `handle`'s transition as a switch expression over `state`. LOCKED + "
             "COIN unlocks; LOCKED + PUSH stays locked and counts a blocked push. "
             "UNLOCKED + PUSH locks; UNLOCKED + COIN stays unlocked and counts a wasted "
             "coin. `main` prints the state after each event, then the final report.",
             _j33t(_TURN33,
                   "        int n = sc.nextInt();\n"
                   "        Turnstile t = new Turnstile();\n"
                   "        StringBuilder trail = new StringBuilder();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            t.handle(sc.next());\n"
                   "            if (trail.length() > 0) trail.append(' ');\n"
                   "            trail.append(t.report().split(\" \")[0]);\n"
                   "        }\n"
                   "        System.out.println(trail);\n"
                   "        System.out.println(t.report());"),
             _TURN_REGION33,
             [_toks33(evs, _turn_out33(evs)) for evs in _EVENTS33],
             hints=["`state = switch (state) { case LOCKED -> {...} case UNLOCKED -> {...} };`",
                    "Each arm is a block, because it may also update a counter.",
                    "Inside a block, produce the next state with `yield`.",
                    "No `default`: two cases cover the enum, so the switch is exhaustive.",
                    "Event strings are compared with `equals`, never `==`."]),

        _jfix("j33-sm-missing", "The state nobody handled",
              "Every status should get a label, but SHIPPED orders print `?` - the switch "
              "statement never mentions SHIPPED, and nothing complained. Rewrite it as a "
              "switch EXPRESSION covering every status, so a forgotten one cannot compile.",
              _j33t(_STATUS33,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Status s = Status.valueOf(sc.next());\n"
                    + _LABEL_BUGGY33
                    + "            System.out.println(s + \": \" + label);\n"
                      "        }"),
              _j33t(_STATUS33,
                    "        int n = sc.nextInt();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Status s = Status.valueOf(sc.next());\n"
                    + _LABEL_FIXED33
                    + "            System.out.println(s + \": \" + label);\n"
                      "        }"),
              [_toks33(ts, _nl(*[f"{t}: {_LABEL33[t]}" for t in ts])) for ts in _STOKS33],
              hints=["A switch statement is allowed to skip constants.",
                     "`String label = switch (s) { ... };` must produce a value for every "
                     "Status.",
                     "Add `case SHIPPED -> \"on its way\";`",
                     "With all four covered, no `default` is needed - and a fifth status "
                     "would break the build, not the output."],
              difficulty="Medium"),

        _jch("j33-sm-counts", "Every state, even the empty ones", "Medium",
             "Count how many orders are in each status with an `EnumMap`, then print "
             "EVERY status and its count - including zeros - in declaration order.",
             _j33t(_STATUS33,
                   "        int n = sc.nextInt();\n"
                   "        Map<Status, Integer> counts = new EnumMap<>(Status.class);\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            counts.merge(Status.valueOf(sc.next()), 1, Integer::sum);\n"
                   "        }\n"
                   "        for (Status s : Status.values()) {\n"
                   "            System.out.println(s + \" \" + counts.getOrDefault(s, 0));\n"
                   "        }"),
             "        for (int i = 0; i < n; i++) {\n"
             "            counts.merge(Status.valueOf(sc.next()), 1, Integer::sum);\n"
             "        }\n"
             "        for (Status s : Status.values()) {\n"
             "            System.out.println(s + \" \" + counts.getOrDefault(s, 0));\n"
             "        }",
             [_toks33(ts, _nl(*[f"{s} {ts.count(s)}" for s in _STATUSES33])) for ts in _VOTES33],
             hints=["`counts.merge(status, 1, Integer::sum)` counts.",
                    "Printing the map itself would skip the statuses nobody reached.",
                    "Iterate `Status.values()` instead, and use `getOrDefault(s, 0)`.",
                    "Both the map and `values()` are in declaration order."]),
    ],
    quiz=[
        _jq("Why model a state machine's states as an enum rather than Strings?",
            ["an invalid state cannot be written, and switches can be checked for "
             "completeness", "enums are faster to print", "Strings cannot be switched on",
             "enums are mutable"],
            0,
            "The type system does half the testing."),
        _jq("To print every status's count, including zero counts, iterate…",
            ["Status.values(), with getOrDefault", "the EnumMap's keySet",
             "the EnumMap's entrySet", "the input again"],
            0,
            "A map only holds keys that were put into it."),
    ],
))


# ===========================================================================
# Capstone - the order tracker
# ===========================================================================

_ORDER33 = """
enum OrderStatus {
    PLACED, PAID, SHIPPED, DELIVERED, CANCELLED;

    OrderStatus on(String event) {
        return switch (this) {
            case PLACED -> switch (event) {
                case "pay" -> PAID;
                case "cancel" -> CANCELLED;
                default -> throw new IllegalStateException();
            };
            case PAID -> switch (event) {
                case "ship" -> SHIPPED;
                case "cancel" -> CANCELLED;
                default -> throw new IllegalStateException();
            };
            case SHIPPED -> switch (event) {
                case "deliver" -> DELIVERED;
                default -> throw new IllegalStateException();
            };
            case DELIVERED, CANCELLED -> throw new IllegalStateException();
        };
    }
}
"""

_ORDER_REGION33 = _ORDER33.strip("\n").split("\n", 1)[1].rsplit("\n", 1)[0]

_ORDERSTATES33 = ("PLACED", "PAID", "SHIPPED", "DELIVERED", "CANCELLED")
_TRANS33 = {
    ("PLACED", "pay"): "PAID", ("PLACED", "cancel"): "CANCELLED",
    ("PAID", "ship"): "SHIPPED", ("PAID", "cancel"): "CANCELLED",
    ("SHIPPED", "deliver"): "DELIVERED",
}

_ORDERS33 = (
    [["pay", "ship", "deliver"], ["cancel"]],
    [["pay", "cancel"], ["ship"], []],
    [["pay", "ship", "cancel"], ["pay", "ship"], ["pay", "ship", "deliver", "pay"]],
    [[]],
    [["cancel", "pay"], ["pay", "ship", "deliver"], ["pay"], ["pay", "ship", "deliver"]],
)


def _order_out33(orders):
    lines, counts = [], {s: 0 for s in _ORDERSTATES33}
    for i, evs in enumerate(orders, start=1):
        s, bad = "PLACED", None
        for e in evs:
            nxt = _TRANS33.get((s, e))
            if nxt is None:
                bad = e
                break
            s = nxt
        lines.append(f"order {i}: {s}" if bad is None else f"order {i}: {s} (rejected {bad})")
        counts[s] += 1
    lines.append(_jmap33([(s, counts[s]) for s in _ORDERSTATES33 if counts[s]]))
    return _nl(*lines)


def _order_case33(orders):
    stdin = "\n".join([str(len(orders))]
                      + [" ".join([str(len(evs))] + evs) for evs in orders])
    return _case(stdin, _order_out33(orders))


_M33_CAP = _jcap(
    "The order tracker",
    """
An order is always in one of five states - `PLACED`, `PAID`, `SHIPPED`,
`DELIVERED`, `CANCELLED` - and moves between them on events:

| from | `pay` | `ship` | `deliver` | `cancel` |
|---|---|---|---|---|
| PLACED | PAID | | | CANCELLED |
| PAID | | SHIPPED | | CANCELLED |
| SHIPPED | | | DELIVERED | |
| DELIVERED, CANCELLED | | | | |

Write `OrderStatus.on(event)`, returning the next state, and throwing
`IllegalStateException` for any event the table leaves blank. Use a switch
expression over `this` - covering every constant, with **no `default`** at the
outer level - and an inner switch over the event.

`main` replays each order's events, stopping at the first rejected one, prints
each order's final state (and the rejected event), and then an `EnumMap` of how
many orders ended in each state.
""",
    _jch("j33-cap-orders", "The order tracker", "Hard",
         "Write the `OrderStatus` enum's constants and its `on(String event)` method, as "
         "the brief's table describes.",
         _j33t(_ORDER33,
               "        int n = sc.nextInt();\n"
               "        Map<OrderStatus, Integer> finals = new EnumMap<>(OrderStatus.class);\n"
               "        for (int i = 1; i <= n; i++) {\n"
               "            int k = sc.nextInt();\n"
               "            OrderStatus s = OrderStatus.PLACED;\n"
               "            String rejected = null;\n"
               "            for (int j = 0; j < k; j++) {\n"
               "                String event = sc.next();\n"
               "                if (rejected != null) {\n"
               "                    continue;\n"
               "                }\n"
               "                try {\n"
               "                    s = s.on(event);\n"
               "                } catch (IllegalStateException e) {\n"
               "                    rejected = event;\n"
               "                }\n"
               "            }\n"
               "            System.out.println(\"order \" + i + \": \" + s\n"
               "                    + (rejected == null ? \"\" : \" (rejected \" + rejected + \")\"));\n"
               "            finals.merge(s, 1, Integer::sum);\n"
               "        }\n"
               "        System.out.println(finals);"),
         _ORDER_REGION33,
         [_order_case33(o) for o in _ORDERS33],
         hints=["Constants first: `PLACED, PAID, SHIPPED, DELIVERED, CANCELLED;`",
                "`return switch (this) { ... };` - inside the enum, `this` is the current "
                "constant.",
                "Each arm can itself be a switch expression over the `String` event.",
                "`default -> throw new IllegalStateException();` - a `throw` is allowed "
                "as an arm.",
                "`case DELIVERED, CANCELLED -> throw ...` - the final states accept "
                "nothing.",
                "The outer switch needs no `default`: five constants, five covered.",
                "The EnumMap prints in declaration order, skipping states nobody ended "
                "in."]),
    example_io="stdin:  2\n        3 pay ship deliver\n        1 cancel\n\n"
               "stdout: order 1: DELIVERED\n        order 2: CANCELLED\n"
               "        {DELIVERED=1, CANCELLED=1}",
    rubric=[
        "The states are an enum; no state is ever a String or an int.",
        "`on` is a switch expression over `this` that covers every constant without a `default`.",
        "Invalid transitions throw `IllegalStateException` rather than returning the old state.",
        "The final counts use an `EnumMap`, so they print in declaration order.",
    ],
)


_MODULES.append(_jmod(
    33, 13, "Advanced Java",
    "Enums, switch and nested classes",
    "The three everyday language features the course had not needed yet - and the "
    "ones every design pattern after this relies on.",
    """
Thirty-two modules without an `enum`, a `switch` or a class inside a class. This
module closes that gap, because the rest of Part 13 cannot do without them.

* **Enums are classes with a fixed set of instances.** Compare with `==`; convert
  with `valueOf` (case-sensitive, throws on a bad name); list with `values()`;
  never store `ordinal()`. Constants can carry fields, a lambda each, or a whole
  method body each.
* **`EnumMap` and `EnumSet`** are the collections for enum keys - smaller, faster,
  and iterating in declaration order.
* **`switch` statements fall through** without `break`. **Switch expressions**
  (Java 14) do not: arrow arms, comma-separated labels, `yield` for block arms, a
  value at the end - and, over an enum, a compile error if a constant is missing.
* **Nested classes**: `static` nested (no outer instance - the default choice),
  inner (a hidden reference to the outer object, spelled `Outer.this`), local and
  anonymous. Implementing `Iterable` with an inner iterator makes a class work in
  an enhanced `for`.
* **State machines** put all of it together: an enum of states and an exhaustive
  switch for the transitions.
""",
    _M33,
    capstone=_M33_CAP,
    objectives=[
        "Declare an enum, and explain why it is a class with a fixed set of instances.",
        "Use `values()`, `valueOf()`, `name()` and `ordinal()`, and say why ordinals must not be persisted.",
        "Give enum constants fields, lambda-valued fields and constant-specific method bodies.",
        "Use `EnumMap` and `EnumSet`, and say why they beat hash-based collections for enum keys.",
        "Explain switch fall-through, and fix a missing `break`.",
        "Write switch expressions with arrow arms, shared labels and `yield`.",
        "Explain exhaustiveness, and why a switch expression over an enum needs no `default`.",
        "Choose between static nested, inner, local and anonymous classes.",
        "Reach an enclosing instance with `Outer.this`, and explain the memory cost of inner classes.",
        "Make a class iterable with an inner `Iterator`.",
        "Model a state machine with an enum and an exhaustive switch.",
    ],
    why="Enums and switch are on every Java interview's list of basics, and the "
        "follow-ups are where people slip: why not store the ordinal, what does "
        "`valueOf` throw, why did this switch print three lines, what is the difference "
        "between a static nested and an inner class, why can an inner class leak memory. "
        "They are also the building blocks of the next three modules - an enum is the "
        "safest singleton, a constant per strategy is the neatest strategy pattern, and a "
        "Builder is a static nested class.",
    est_minutes=300,
    glossary=[
        _jg("enum", "A class with a fixed, named set of instances, created once when the "
                    "class loads."),
        _jg("ordinal()", "A constant's 0-based position in the declaration. Fine for "
                         "arithmetic inside the enum; never persist it."),
        _jg("valueOf(String)", "Converts a constant's exact name back to the constant; "
                               "throws IllegalArgumentException otherwise."),
        _jg("Constant-specific body", "A class body attached to one enum constant, "
                                      "usually implementing an abstract method the enum "
                                      "declares."),
        _jg("EnumMap / EnumSet", "Array- and bit-field-backed collections for enum keys; "
                                 "iterate in declaration order."),
        _jg("Fall-through", "In a switch statement, execution continuing into the next "
                            "case because there was no `break`."),
        _jg("Switch expression", "A switch that produces a value, with arrow arms that "
                                 "never fall through (Java 14)."),
        _jg("yield", "Produces the value of a block arm in a switch expression."),
        _jg("Exhaustive", "Covering every possible value. Required of a switch "
                          "expression, and checked by the compiler for enums."),
        _jg("Static nested class", "A class declared `static` inside another; no link to "
                                   "an outer instance."),
        _jg("Inner class", "A non-static nested class; each instance holds a hidden "
                           "reference to the outer instance (`Outer.this`)."),
        _jg("Anonymous class", "A class declared and instantiated in one expression, "
                               "with no name."),
        _jg("Iterable", "An interface with one method, `iterator()`; implementing it "
                        "lets a class be used in an enhanced `for`."),
    ],
    cheatsheet="""
```java
// --- enums ------------------------------------------------------------------------
enum Coin {
    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);   // constants first, then ';'
    private final int cents;
    Coin(int cents) { this.cents = cents; }        // always private
    int cents() { return cents; }
}
Coin.valueOf("DIME")         // exact name, else IllegalArgumentException
Coin.values()                // every constant, declaration order (a new array)
c.name()  c.ordinal()  c == Coin.DIME   // == is right: one instance each

enum Op {                    // a behaviour per constant
    ADD((a, b) -> a + b), MUL((a, b) -> a * b);
    private final IntBinaryOperator fn;
    Op(IntBinaryOperator fn) { this.fn = fn; }
    int apply(int a, int b) { return fn.applyAsInt(a, b); }
}
enum Shape { SQUARE { int area(int s) { return s * s; } }; abstract int area(int s); }
Day next() { return values()[(ordinal() + 1) % values().length]; }

Map<Suit, Integer> m = new EnumMap<>(Suit.class);   // declaration-order iteration
Set<Suit> red = EnumSet.of(Suit.HEARTS, Suit.DIAMONDS);

// --- switch ----------------------------------------------------------------------
switch (grade) {                 // STATEMENT: falls through without break
    case "A": System.out.println("excellent"); break;
    default:  System.out.println("try again");
}
String kind = switch (day) {     // EXPRESSION (Java 14): no fall-through
    case SATURDAY, SUNDAY -> "weekend";
    default -> "weekday";
};
int cost = switch (zone) {       // exhaustive over an enum: no default needed
    case LOCAL -> 5;
    case NATIONAL -> { int base = 10; yield base + weight; }
    case INTERNATIONAL -> throw new IllegalStateException();
};

// --- nested classes -------------------------------------------------------------
class Outer {
    private static class Node { }            // static nested: no outer instance
    private class Inner { int f() { return Outer.this.x; } }   // inner: has one
}
new Comparator<String>() { public int compare(String a, String b) { ... } }  // anonymous
class Range implements Iterable<Integer> { public Iterator<Integer> iterator() { ... } }
```
""",
    self_check=[
        "Can you explain why an enum constant should be compared with `==`?",
        "Can you say what `valueOf(\"east\")` does when the constant is `EAST`, and how to fix it?",
        "Can you explain why an ordinal must not be written to a database?",
        "Can you give an enum constant its own behaviour in two different ways?",
        "Can you say two reasons to use `EnumMap` over `HashMap` for enum keys?",
        "Can you predict what a switch statement with no `break`s prints?",
        "Can you write a switch expression with shared labels and a `yield` block?",
        "Can you explain why a switch expression over an enum needs no `default`, and what happens when a constant is added?",
        "Can you say when a nested class should be `static`, and what an inner class costs?",
        "Can you reach an outer field that an inner class's field shadows?",
        "Can you make your own class work in an enhanced `for` loop?",
    ],
    review=[
        _jq("An enum's constants are reordered. What silently changes?",
            ["every ordinal() value", "every name()", "every valueOf() result",
             "nothing"],
            0,
            "Which is why ordinals must never be stored."),
        _jq("```java\nswitch (x) {\n    case 1: System.out.print(\"a\");\n    case 2: System.out.print(\"b\");\n    default: System.out.print(\"c\");\n}\n```\nWith `x = 1` this prints…",
            ["abc", "a", "ac", "nothing"],
            0,
            "No breaks: it falls through every following case."),
        _jq("A switch expression over an enum with three constants lists all three and no "
            "`default`. A fourth constant is added. The result is…",
            ["a compile error at that switch", "a silent 0", "an exception at run time",
             "the first arm runs"],
            0,
            "Exhaustiveness is re-checked on every compile."),
        _jq("A `Node` class used only inside a linked list should be…",
            ["private static nested", "a public inner class", "anonymous", "an enum"],
            0,
            "No outer-instance reference to carry around."),
        _jq("`EnumMap` prints its entries in…",
            ["declaration order of the enum", "insertion order", "hash order",
             "value order"],
            0,
            "It is an array indexed by ordinal."),
    ],
    milestone="You can model a fixed set of values as an enum with its own data and "
              "behaviour, write a switch that the compiler checks for completeness, and "
              "choose the right kind of nested class - the vocabulary the design patterns "
              "module is written in.",
))
