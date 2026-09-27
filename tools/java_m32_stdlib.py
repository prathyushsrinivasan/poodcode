# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 32 - The APIs worth knowing cold.  Part 11, in one module.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# The roadmap's Part 11 lists Math, Arrays, Collections, String, StringBuilder,
# Objects, Random and the java.time classes. Most of that list is already
# taught where it is first needed - Arrays in module 1, String in 6-7,
# StringBuilder in 8, Collections in 17-20 - so this module covers exactly the
# REMAINDER, and each lesson is about the place the API bites:
#
#   32.1 Math        - arithmetic that fails SILENTLY, and the methods that don't
#   32.2 Objects     - the null-safe helpers module 13's Objects.hash came from
#   32.3 Random      - a seed makes "random" reproducible, and so testable
#   32.4 LocalDate   - immutable dates, and month arithmetic that clamps
#   32.5 Formatting  - String.format, DateTimeFormatter, and the Locale
#
# JUDGING NOTES
#   * `Random(seed)` is fully specified by the JDK (a 48-bit LCG), so seeded
#     output is identical on every JVM. The Python mirror `_JRandom32` below is
#     that algorithm, including `nextInt(bound)`'s rejection loop, and
#     `_jshuffle32` is `Collections.shuffle`'s documented backward walk. Both
#     were checked against a real JVM when this module was written.
#   * EVERY String.format call passes `Locale.ROOT`, and every formatter that
#     prints a day or month NAME passes `Locale.ENGLISH`. The default locale is
#     the learner's machine's, so "3.14" can legitimately print as "3,14" -
#     lesson 32.5 teaches that as the point, not as a footnote.
#   * `%.2f` rounds HALF_UP on the value's shortest decimal representation
#     (so 1.005 prints 1.01, not Python's 1.00). `_f32` mirrors exactly that.
#   * Day and month names are mirrored from fixed tables, never from Python's
#     locale-dependent strftime.
# ---------------------------------------------------------------------------

import calendar as _cal32
import datetime as _dt32
import math as _math32
from decimal import Decimal as _Dec32, ROUND_HALF_UP as _HALF_UP32

_M32 = []

_IMPORTS32 = ("import java.util.*;\n"
              "import java.time.*;\n"
              "import java.time.format.*;\n"
              "import java.time.temporal.*;\n")


def _j32s(body):
    """Scanner-opening main, no helpers."""
    return _jscan(body, imports=_IMPORTS32)


def _j32(helpers, body):
    """Static helper methods above a Scanner-opening main."""
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS32,
    )


def _j32t(types, body):
    """Helper CLASSES above Main, then a Scanner-opening main."""
    return _joop(types, body, imports=_IMPORTS32)


# ===========================================================================
# Python mirrors of the Java behaviour this module teaches.
# ===========================================================================

_INT_MIN32, _INT_MAX32 = -(1 << 31), (1 << 31) - 1
_LONG_MIN32, _LONG_MAX32 = -(1 << 63), (1 << 63) - 1


def _i32w(x):
    """Wrap to a Java int, exactly as overflow does."""
    x &= 0xFFFFFFFF
    return x - (1 << 32) if x >= (1 << 31) else x


def _fits32(x):
    return _INT_MIN32 <= x <= _INT_MAX32


def _fitsl32(x):
    return _LONG_MIN32 <= x <= _LONG_MAX32


def _round32(x):
    """`Math.round(double)`: floor(x + 0.5), so halves go UP - even negative ones."""
    return _math32.floor(x + 0.5)


def _jd32(x):
    """How Java prints a double of modest size (Double.toString)."""
    x = float(x)
    assert x == 0 or 1e-3 <= abs(x) < 1e7, f"double {x} outside plain notation"
    return repr(x)


def _f32(x, places=2):
    """`String.format(Locale.ROOT, "%.<places>f", x)` - HALF_UP on the shortest
    decimal representation of the double, which is what the JDK does."""
    q = _Dec32(1).scaleb(-places)
    return str(_Dec32(repr(float(x))).quantize(q, rounding=_HALF_UP32))


_MASK32 = (1 << 48) - 1


class _JRandom32:
    """java.util.Random, bit for bit."""

    def __init__(self, seed):
        self.s = (seed ^ 0x5DEECE66D) & _MASK32

    def _next(self, bits):
        self.s = (self.s * 0x5DEECE66D + 0xB) & _MASK32
        return _i32w(self.s >> (48 - bits))

    def next_int(self, bound=None):
        if bound is None:
            return self._next(32)
        assert bound > 0
        r = self._next(31)
        m = bound - 1
        if bound & m == 0:
            return _i32w((bound * r) >> 31)
        u = r
        while True:
            r = u % bound
            if _i32w(u - r + m) >= 0:
                return r
            u = self._next(31)

    def next_boolean(self):
        return self._next(1) != 0


def _jshuffle32(xs, rnd):
    """`Collections.shuffle(list, rnd)`: walk backwards, swapping a random
    earlier-or-equal element into each position."""
    xs = list(xs)
    for i in range(len(xs), 1, -1):
        j = rnd.next_int(i)
        xs[i - 1], xs[j] = xs[j], xs[i - 1]
    return xs


def _jhash32(s):
    """`String.hashCode()`."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return _i32w(h)


def _ohash32(*vals):
    """`Objects.hash(...)` = `Arrays.hashCode(Object[])` over Strings/ints/nulls."""
    h = 1
    for v in vals:
        e = 0 if v is None else (_jhash32(v) if isinstance(v, str) else v)
        h = _i32w(31 * h + e)
    return h


_DOW32 = ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")
_DOW3_32 = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
_MON3_32 = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
            "Nov", "Dec")


def _d32(iso):
    return _dt32.date.fromisoformat(iso)


def _dow32(d):
    return _DOW32[d.weekday()]


def _plus_months32(d, k):
    """`LocalDate.plusMonths(k)`: clamp the day to the target month's length."""
    total = d.year * 12 + (d.month - 1) + k
    y, m0 = divmod(total, 12)
    last = _cal32.monthrange(y, m0 + 1)[1]
    return _dt32.date(y, m0 + 1, min(d.day, last))


def _period32(a, b):
    """`Period.between(a, b).toString()` for a <= b."""
    assert a <= b, "negative periods are not mirrored"
    tm = (b.year * 12 + b.month) - (a.year * 12 + a.month)
    days = b.day - a.day
    if tm > 0 and days < 0:
        tm -= 1
        days = (b - _plus_months32(a, tm)).days
    y, m = divmod(tm, 12)
    if y == m == days == 0:
        return "P0D"
    return ("P" + (f"{y}Y" if y else "") + (f"{m}M" if m else "")
            + (f"{days}D" if days else ""))


def _pretty32(d):
    """`ofPattern("EEE, d MMM yyyy", Locale.ENGLISH)`."""
    return f"{_DOW3_32[d.weekday()]}, {d.day} {_MON3_32[d.month - 1]} {d.year:04d}"


def _slash32(d):
    """`ofPattern("dd/MM/yyyy")`."""
    return f"{d.day:02d}/{d.month:02d}/{d.year:04d}"


# ===========================================================================
# 32.1 Math
# ===========================================================================

# (array, rotation steps) - every case has at least one NEGATIVE step, which
# is exactly where `%` and `floorMod` disagree.
_ROT32 = (
    ([10, 20, 30, 40, 50], [2, -1, 7, -6, 0]),
    ([5, 6, 7], [-3, -4, 3, 1, -1]),
    ([9], [0, -5, 5]),
    ([1, 2, 3, 4], [-9, 13, 4]),
    ([8, 6, 4, 2, 0, 1], [-1, -7, 11]),
)


def _rot32(a, ks, out):
    return _case("\n".join([str(len(a)), _sp(a), str(len(ks)), _sp(ks)]), out)


def _rot_out32(a, ks):
    return _nl(*[a[k % len(a)] for k in ks])   # Python's % IS floorMod


# Sums chosen so that one overflows only IN THE MIDDLE - the final total would
# fit, and only a check at every step notices.
_SUMS32 = (
    [1, 2, 3],
    [2147483647, 1],
    [2000000000, 2000000000, -2000000000],
    [-2147483648, -1],
    [1000000000, 1000000000, 147483647],
)


def _exact_sum32(xs):
    total = 0
    for x in xs:
        total += x
        if not _fits32(total):
            return "overflow"
    return str(total)


# (sum, count) pairs: truncation, floor and rounding only differ for negatives
# and halves, so every case has at least one of each.
_DIVS32 = (
    [(7, 2), (-7, 2)],
    [(10, 4), (-10, 4)],
    [(9, 3), (-1, 3)],
    [(-9, 4), (5, 2), (0, 7)],
    [(-15, 6), (15, 6), (-2, 5)],
)


def _div_line32(s, c):
    return f"{_jdiv(s, c)} {s // c} {_round32(s / c)}"


def _divcase32(pairs):
    stdin = "\n".join([str(len(pairs))] + [f"{s} {c}" for (s, c) in pairs])
    return _case(stdin, _nl(*[_div_line32(s, c) for (s, c) in pairs]))


_M32.append(_jlesson(
    "m32-math", "`Math`, and the arithmetic that fails silently",
    "`int` overflow wraps without a word, `%` goes negative, and `round` returns a long.",
    """
Every operator you have used on an `int` so far has a failure mode that does
**not** throw. `Math` is where the versions that behave live.

## Overflow wraps, silently

```java
int big = Integer.MAX_VALUE;     // 2147483647
System.out.println(big + 1);     // -2147483648   no exception, no warning
```

An `int` is 32 bits, and arithmetic on it is arithmetic *modulo 2^32*. Adding one
to the largest value wraps round to the smallest. Nothing tells you, and the
wrong number flows on into everything computed from it.

The `*Exact` methods do the same arithmetic but **throw
`ArithmeticException`** the moment the true answer does not fit:

```java
Math.addExact(a, b)        Math.subtractExact(a, b)
Math.multiplyExact(a, b)   Math.negateExact(a)
Math.toIntExact(someLong)  // a long that must fit in an int
```

Use them wherever an overflow would be a bug rather than an intention - totals,
sizes, money. Note that checking the *final* total is not enough: a running sum
can overflow in the middle and come back into range by the end, and only a
check at every step notices.

**The one that surprises everybody:**

```java
Math.abs(Integer.MIN_VALUE)      // -2147483648  - still negative!
```

There is no positive `int` large enough to hold the answer, so it wraps back to
itself. Any code that says "take the absolute value, so it is non-negative" is
wrong for exactly one input.

## `%` is a remainder, not a modulus

```java
-1 % 5                 // -1   the sign follows the LEFT operand
Math.floorMod(-1, 5)   //  4   the sign follows the divisor
```

For a circular index - "step `k` places round an array of `n`" - a negative `k`
with `%` produces a negative index and an `ArrayIndexOutOfBoundsException`.
`Math.floorMod(k, n)` always lands in `0..n-1`. Its partner `Math.floorDiv`
rounds *down* where `/` truncates *toward zero*:

| expression | `/` and `%` | `floorDiv` and `floorMod` |
|---|---|---|
| `7, 2` | `3`, `1` | `3`, `1` |
| `-7, 2` | `-3`, `-1` | `-4`, `1` |

## Rounding, and the types it returns

| call | returns | `-2.5` gives |
|---|---|---|
| `(int) x` | `int` | `-2` - truncates toward zero |
| `Math.floor(x)` | **`double`** | `-3.0` |
| `Math.ceil(x)` | **`double`** | `-2.0` |
| `Math.round(x)` | **`long`** for a `double` | `-2` - halves go *up* |

`Math.round` is `floor(x + 0.5)`: `2.5` rounds to `3`, and `-2.5` rounds to
`-2`, not `-3`. It returns a `long` because a `double` can be far larger than
any `int` - so `int r = Math.round(d);` does not compile without a cast.

`Math.pow(2, 10)` is `1024.0`, a `double`. For integer powers, a loop of
`multiplyExact` is exact where `pow` quietly loses precision beyond 2^53.
""",
    warmup=[
        _jq("`Integer.MAX_VALUE + 1` evaluates to…",
            ["-2147483648", "an ArithmeticException", "2147483648", "0"],
            0,
            "int arithmetic wraps silently. Only the `*Exact` methods throw."),
        _jq("`-7 % 3` in Java is…",
            ["-1", "2", "1", "-2"],
            0,
            "`%` takes the sign of the left operand. `Math.floorMod(-7, 3)` is 2."),
    ],
    exercises=[
        _je("j32-ma-floormod", "Round and round",
            "Each query steps `k` places round the array, where `k` may be negative "
            "(backwards). Print the element it lands on. Replace `____` with the index "
            "expression that always lands inside the array.",
            _j32s(_RD_ARR
                  + "        int q = sc.nextInt();\n"
                    "        for (int i = 0; i < q; i++) {\n"
                    "            int k = sc.nextInt();\n"
                    "            System.out.println(a[Math.floorMod(k, n)]);\n"
                    "        }"),
            "Math.floorMod(k, n)",
            [_rot32(a, ks, _rot_out32(a, ks)) for (a, ks) in _ROT32],
            hints=["The index has to end up in `0..n-1` for every `k`, including "
                   "negative ones.",
                   "`k % n` is negative when `k` is.",
                   "`Math.floorMod(k, n)` takes the sign of `n`, which is positive.",
                   "Stepping -1 from index 0 lands on the LAST element."],
            difficulty="Easy"),

        _jfix("j32-ma-percent", "The index that went negative",
              "This circular lookup works for every non-negative step and throws "
              "`ArrayIndexOutOfBoundsException` for the first negative one. Fix the "
              "index so stepping backwards wraps round.",
              _j32s(_RD_ARR
                    + "        int q = sc.nextInt();\n"
                      "        for (int i = 0; i < q; i++) {\n"
                      "            int k = sc.nextInt();\n"
                      "            System.out.println(a[k % n]);\n"
                      "        }"),
              _j32s(_RD_ARR
                    + "        int q = sc.nextInt();\n"
                      "        for (int i = 0; i < q; i++) {\n"
                      "            int k = sc.nextInt();\n"
                      "            System.out.println(a[Math.floorMod(k, n)]);\n"
                      "        }"),
              [_rot32(a, ks, _rot_out32(a, ks)) for (a, ks) in _ROT32],
              hints=["`-1 % 5` is `-1` in Java, not `4`.",
                     "The remainder takes the sign of the left operand.",
                     "`Math.floorMod(k, n)` takes the sign of the right one.",
                     "The hand-written alternative is `((k % n) + n) % n` - correct, and "
                     "the reason `floorMod` exists."],
              difficulty="Easy"),

        _je("j32-ma-exact", "The total that noticed",
            "Add the numbers up as `int`s, but refuse to print a wrapped-round answer: if "
            "the running total ever overflows, print `overflow` instead. Replace `____` "
            "with the checked addition.",
            _j32s(_RD_ARR
                  + "        int total = 0;\n"
                    "        try {\n"
                    "            for (int x : a) {\n"
                    "                total = Math.addExact(total, x);\n"
                    "            }\n"
                    "            System.out.println(total);\n"
                    "        } catch (ArithmeticException e) {\n"
                    "            System.out.println(\"overflow\");\n"
                    "        }"),
            "                total = Math.addExact(total, x);",
            [_acase(xs, _exact_sum32(xs)) for xs in _SUMS32],
            hints=["`total += x` would wrap silently and print a nonsense number.",
                   "`Math.addExact(total, x)` throws `ArithmeticException` instead.",
                   "The check happens at EVERY step: `2e9 + 2e9 - 2e9` ends in range but "
                   "overflows on the way.",
                   "`1000000000 + 1000000000 + 147483647` is exactly `Integer.MAX_VALUE`, "
                   "which fits."],
            difficulty="Medium"),

        _jch("j32-ma-round", "Three ways to divide", "Medium",
             "For each `sum count` pair print three numbers on one line: Java's `/`, "
             "`Math.floorDiv`, and `Math.round` of the true (double) average. Write the "
             "`println`.",
             _j32s("        int pairs = sc.nextInt();\n"
                   "        for (int i = 0; i < pairs; i++) {\n"
                   "            int sum = sc.nextInt();\n"
                   "            int count = sc.nextInt();\n"
                   "            System.out.println((sum / count) + \" \" + Math.floorDiv(sum, count)\n"
                   "                    + \" \" + Math.round((double) sum / count));\n"
                   "        }"),
             "            System.out.println((sum / count) + \" \" + Math.floorDiv(sum, count)\n"
             "                    + \" \" + Math.round((double) sum / count));",
             [_divcase32(p) for p in _DIVS32],
             hints=["`/` on two ints truncates toward zero: `-7 / 2` is `-3`.",
                    "`Math.floorDiv(-7, 2)` rounds down: `-4`.",
                    "`(double) sum / count` casts BEFORE dividing, so the division is "
                    "done in double.",
                    "`Math.round(-3.5)` is `-3` - halves always go up, even negative ones.",
                    "Parenthesise `(sum / count)` so `+` does not glue the string on "
                    "first."]),
    ],
    quiz=[
        _jq("`Math.abs(Integer.MIN_VALUE)` returns…",
            ["-2147483648", "2147483648", "an ArithmeticException", "0"],
            0,
            "There is no positive int that large, so it wraps back to itself."),
        _jq("`Math.round(2.5)` and `Math.round(-2.5)` are…",
            ["3 and -2", "3 and -3", "2 and -2", "2 and -3"],
            0,
            "`Math.round` is floor(x + 0.5): halves always go up."),
    ],
))


# ===========================================================================
# 32.2 Objects
# ===========================================================================

# Tokens read from stdin, where "-" stands for null.
_PAIRS32 = (
    [("ada", "ada"), ("-", "ada")],
    [("-", "-"), ("bo", "cy")],
    [("ada", "-"), ("x", "x"), ("-", "y")],
    [("-", "q")],
    [("pear", "pear"), ("fig", "-"), ("-", "-")],
)

_NULLREAD32 = ("    static String read(Scanner sc) {\n"
               "        String token = sc.next();\n"
               "        return token.equals(\"-\") ? null : token;\n"
               "    }")


def _nv32(t):
    return None if t == "-" else t


def _pairs32(pairs, out):
    stdin = "\n".join([str(len(pairs))] + [f"{a} {b}" for (a, b) in pairs])
    return _case(stdin, out)


def _eq_out32(pairs):
    return _nl(*[_jbool(_nv32(a) == _nv32(b)) for (a, b) in pairs])


_TOKS32 = (["ada", "-", "bo"], ["-"], ["x", "y"], ["-", "-", "z", "-"], ["solo"])


def _toks32(ts, out):
    return _case("\n".join([str(len(ts)), " ".join(ts)]), out)


_TAG32 = """
class Tag {
    private final String name;

    Tag(String name) {
        this.name = Objects.requireNonNull(name, "name");
    }

    String name() {
        return name;
    }
}
"""

# (key, count) pairs: the two entries of each case; "-" is a null key.
_ENTRIES32 = (
    (("ada", 3), ("ada", 3)),
    (("ada", 3), ("ada", 4)),
    (("-", 1), ("-", 1)),
    (("-", 2), ("bo", 2)),
    (("pear", 0), ("pear", 0)),
)

_ENTRY32 = """
class Entry {
    private final String key;
    private final int count;

    Entry(String key, int count) {
        this.key = key;
        this.count = count;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Entry)) return false;
        Entry other = (Entry) o;
        return count == other.count && Objects.equals(key, other.key);
    }

    @Override
    public int hashCode() {
        return Objects.hash(key, count);
    }
}
"""

def _entry_case32(e1, e2):
    (k1, c1), (k2, c2) = e1, e2
    same = _nv32(k1) == _nv32(k2) and c1 == c2
    h1, h2 = _ohash32(_nv32(k1), c1), _ohash32(_nv32(k2), c2)
    return _case(f"{k1} {c1}\n{k2} {c2}",
                 _nl(_jbool(same), _jbool(h1 == h2), h1))


_M32.append(_jlesson(
    "m32-objects", "`Objects` - the null-safe helpers",
    "Module 13 used `Objects.hash`. Here is the rest of the class, and why it exists.",
    """
`java.util.Objects` (note the **s**) is a small class of static helpers, and
nearly all of them answer the same question: *what if this is null?*

## `Objects.equals(a, b)`

```java
a.equals(b)            // NullPointerException if a is null
Objects.equals(a, b)   // true if both null, false if one is, else a.equals(b)
```

Every `equals` method you write that compares a field which may be null wants
this - it is why module 13's `equals` could be one line.

## `Objects.hash(...)` and `Objects.hashCode(x)`

`Objects.hash(key, count)` combines several fields into one hash, using the
same `31 * h + next` recipe as `String.hashCode`, and treats null as `0`.
`Objects.hashCode(x)` is the single-value version: `x.hashCode()`, or `0` for
null.

They are **not** interchangeable for one value: `Objects.hash(x)` wraps `x` in
an array first, so it is `31 + x.hashCode()`. Use `hash` for several fields,
`hashCode` for one.

## `Objects.requireNonNull(x, "name")`

```java
Tag(String name) {
    this.name = Objects.requireNonNull(name, "name");
}
```

It returns its argument unchanged, or throws `NullPointerException` **with your
message** if it is null. The point is *where* it throws: here, at construction,
naming the culprit - rather than an hour later, deep inside a method that
happened to be the first to call `name.length()`. This is module 12's "establish
the invariant in the constructor", in one call.

## The rest

```java
Objects.toString(x, "(none)")   // x.toString(), or the default for null
Objects.isNull(x)               // x == null  - as a method, so it can be
Objects.nonNull(x)              // x != null    a method reference
list.stream().filter(Objects::nonNull).count();
```

`isNull` and `nonNull` look pointless next to `==`. They exist so a null check
can be passed around as a `Predicate` - `filter(Objects::nonNull)` reads better
than `filter(x -> x != null)`, and says the same thing.
""",
    warmup=[
        _jq("`Objects.equals(null, null)` returns…",
            ["true", "false", "throws NullPointerException", "does not compile"],
            0,
            "Two nulls are equal; one null and one value are not."),
        _jq("`Objects.requireNonNull(x, \"x\")` returns…",
            ["x itself, or throws NPE with the message \"x\"", "a boolean",
             "an Optional", "void"],
            0,
            "Returning its argument is what lets it sit inside an assignment."),
    ],
    exercises=[
        _jfix("j32-ob-equals", "The comparison that crashed on null",
              "Each line holds two tokens, where `-` means null. This program compares "
              "them with `a.equals(b)` and throws `NullPointerException` as soon as the "
              "left one is null. Make the comparison null-safe.",
              _j32(_NULLREAD32,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String a = read(sc);\n"
                   "            String b = read(sc);\n"
                   "            System.out.println(a.equals(b));\n"
                   "        }"),
              _j32(_NULLREAD32,
                   "        int n = sc.nextInt();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            String a = read(sc);\n"
                   "            String b = read(sc);\n"
                   "            System.out.println(Objects.equals(a, b));\n"
                   "        }"),
              [_pairs32(p, _eq_out32(p)) for p in _PAIRS32],
              hints=["Calling any method on a null reference throws.",
                     "`b` being null is fine - `\"ada\".equals(null)` is simply false.",
                     "`Objects.equals(a, b)` handles null on either side.",
                     "Two nulls compare equal."],
              difficulty="Easy"),

        _je("j32-ob-tostring", "A default for nothing",
            "Print each token, or `(none)` where it is null. Replace `____` with the "
            "expression.",
            _j32(_NULLREAD32,
                 "        int n = sc.nextInt();\n"
                 "        for (int i = 0; i < n; i++) {\n"
                 "            String value = read(sc);\n"
                 "            System.out.println(Objects.toString(value, \"(none)\"));\n"
                 "        }"),
            "Objects.toString(value, \"(none)\")",
            [_toks32(ts, _nl(*[(t if t != "-" else "(none)") for t in ts]))
             for ts in _TOKS32],
            hints=["Printing a null String prints the four letters `null`.",
                   "`Objects.toString(x, dflt)` returns the default when `x` is null.",
                   "`Objects.toString(value, \"(none)\")`",
                   "The one-argument `Objects.toString(x)` would print `null` - which is "
                   "exactly what you are avoiding."],
            difficulty="Easy"),

        _je("j32-ob-require", "Refused at the door",
            "`Tag` must never hold a null name. Try to build one per token (`-` is null) "
            "and print the name, or `rejected` when the constructor refuses. Replace "
            "`____` with the constructor's one line.",
            _j32t(_TAG32,
                  "        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String token = sc.next();\n"
                  "            String name = token.equals(\"-\") ? null : token;\n"
                  "            try {\n"
                  "                Tag tag = new Tag(name);\n"
                  "                System.out.println(tag.name());\n"
                  "            } catch (NullPointerException e) {\n"
                  "                System.out.println(\"rejected\");\n"
                  "            }\n"
                  "        }"),
            "        this.name = Objects.requireNonNull(name, \"name\");",
            [_toks32(ts, _nl(*[(t if t != "-" else "rejected") for t in ts]))
             for ts in _TOKS32],
            hints=["The constructor is where an invariant is established (module 12).",
                   "`Objects.requireNonNull(name, \"name\")` returns `name` or throws.",
                   "Because it RETURNS its argument, it fits inside the assignment.",
                   "A plain `this.name = name;` would let a null in, and print `null` "
                   "instead of `rejected`."],
            difficulty="Medium"),

        _jch("j32-ob-hash", "`equals` and `hashCode`, null-safe", "Hard",
             "`Entry` has a key that may be null and a count. Write its `equals` (using "
             "`Objects.equals` for the key) and its `hashCode` (using `Objects.hash`). "
             "`main` prints whether two entries are equal, whether their hashes match, "
             "and the first entry's hash.",
             _j32t(_ENTRY32,
                   "        String k1 = sc.next();\n"
                   "        int c1 = sc.nextInt();\n"
                   "        String k2 = sc.next();\n"
                   "        int c2 = sc.nextInt();\n"
                   "        Entry e1 = new Entry(k1.equals(\"-\") ? null : k1, c1);\n"
                   "        Entry e2 = new Entry(k2.equals(\"-\") ? null : k2, c2);\n"
                   "        System.out.println(e1.equals(e2));\n"
                   "        System.out.println(e1.hashCode() == e2.hashCode());\n"
                   "        System.out.println(e1.hashCode());"),
             "    @Override\n"
             "    public boolean equals(Object o) {\n"
             "        if (this == o) return true;\n"
             "        if (!(o instanceof Entry)) return false;\n"
             "        Entry other = (Entry) o;\n"
             "        return count == other.count && Objects.equals(key, other.key);\n"
             "    }\n"
             "\n"
             "    @Override\n"
             "    public int hashCode() {\n"
             "        return Objects.hash(key, count);\n"
             "    }",
             [_entry_case32(e1, e2) for (e1, e2) in _ENTRIES32],
             hints=["`key.equals(other.key)` throws when `key` is null.",
                    "`Objects.equals(key, other.key)` does not.",
                    "`hashCode` must use exactly the fields `equals` uses: "
                    "`Objects.hash(key, count)`.",
                    "`Objects.hash` treats a null key as 0, so no special case is needed.",
                    "Equal objects must have equal hashes - the second line is `true` "
                    "whenever the first is."]),
    ],
    quiz=[
        _jq("`Objects.hash(x)` versus `Objects.hashCode(x)` for a single non-null x…",
            ["differ: hash(x) is 31 + x.hashCode()", "are identical",
             "hash(x) throws on null", "hashCode(x) is deprecated"],
            0,
            "`hash` is varargs, so it hashes a one-element array."),
        _jq("The best place for `Objects.requireNonNull` is…",
            ["a constructor or method entry, so the failure names the culprit",
             "inside every getter", "in main only", "in toString"],
            0,
            "Fail where the bad value arrives, not where it is first used."),
    ],
))


# ===========================================================================
# 32.3 Random
# ===========================================================================

# (seed, how many)
_SEEDS32 = ((42, 5), (7, 3), (2024, 6), (1, 4), (123456789, 5))


def _dice32(seed, n):
    r = _JRandom32(seed)
    return [r.next_int(6) + 1 for _ in range(n)]


def _seedcase32(seed, n, out):
    return _case(f"{seed} {n}", out)


# (seed, lo, hi, how many) - an INCLUSIVE range.
_RANGES32 = ((42, 1, 6, 6), (7, 10, 12, 6), (2024, -3, 3, 6), (1, 0, 1, 8),
             (99, 5, 9, 6))


def _range32(seed, lo, hi, n, off=1):
    r = _JRandom32(seed)
    return [r.next_int(hi - lo + off) + lo for _ in range(n)]


def _rangecase32(seed, lo, hi, n):
    got = _range32(seed, lo, hi, n)
    return _case(f"{seed} {lo} {hi} {n}", _sp(got))


def _deal32(seed, n):
    deck = _jshuffle32(range(1, n + 1), _JRandom32(seed))
    a = [deck[i] for i in range(0, n, 2)]
    b = [deck[i] for i in range(1, n, 2)]
    return _nl(_jarr(deck), _sp(a), _sp(b))


_DEALS32 = ((42, 6), (7, 5), (2024, 8), (1, 4), (123456789, 7))

# Sanity: the reseeding bug must actually change the output, and the
# off-by-one range bug must actually be visible, for these data.
for _s, _n in _SEEDS32:
    assert len(set(_dice32(_s, _n))) > 1, f"seed {_s} rolls a constant"
assert any(_range32(s, lo, hi, n) != _range32(s, lo, hi, n, off=0)
           for (s, lo, hi, n) in _RANGES32)
assert sum(_hi in _range32(_s, _lo, _hi, _n) for (_s, _lo, _hi, _n) in _RANGES32) >= 3, \
    "most ranges should actually roll their upper bound"


_M32.append(_jlesson(
    "m32-random", "`Random`, and the seed that makes it testable",
    "Random numbers you can reproduce - which is the only kind you can test.",
    """
`java.util.Random` is not random. It is a **pseudo-random generator**: a small
formula that turns one number (its *state*) into the next, and whose output
merely *looks* random. The starting state is the **seed**.

```java
Random rnd = new Random(42);     // seeded: the same sequence, every run, every JVM
Random any = new Random();       // seeded from the clock: different each run
```

That is not a weakness - it is the most useful thing about it. A simulation,
a shuffled test deck, a procedurally generated level: with a fixed seed, a bug
you saw once you can see again. The algorithm behind `Random` is written into
its specification, so seed 42 produces the same numbers on every machine and
every Java version. Every exercise in this lesson is judged on exactly that.

## The methods

```java
rnd.nextInt(6)          // 0..5   - the bound is EXCLUSIVE
rnd.nextInt(6) + 1      // 1..6   - a die
rnd.nextInt(hi - lo + 1) + lo   // lo..hi inclusive
rnd.nextBoolean()       // a coin
rnd.nextDouble()        // [0.0, 1.0)
rnd.nextInt()           // any int at all, negative included
```

The exclusive upper bound is the source of the classic off-by-one:
`nextInt(hi - lo) + lo` can never produce `hi`.

## One generator, created once

```java
for (int i = 0; i < 5; i++) {
    System.out.println(new Random(seed).nextInt(6));   // the SAME number, 5 times
}
```

A new generator with the same seed starts the same sequence from the top, so
this prints its first value five times. Create the generator **once**, then
draw from it.

## Shuffling

```java
Collections.shuffle(list, new Random(seed));   // reproducible
Collections.shuffle(list);                     // not
```

`shuffle` walks the list backwards, swapping each position with a random one at
or before it - the Fisher-Yates shuffle, which makes every ordering equally
likely. Writing it yourself with `nextInt(size)` for *every* position (instead
of `nextInt(i + 1)`) is a well-known bug: it looks random and is measurably
biased.

## And the others

`Math.random()` is a shared, unseeded `Random` returning a `double` - fine for a
quick script, untestable in a program. `ThreadLocalRandom.current()` is the one
to use from several threads (module 31), and it cannot be seeded. For anything
security-related - tokens, passwords, keys - use `java.security.SecureRandom`;
`Random`'s next output can be predicted from a few of its previous ones.
""",
    warmup=[
        _jq("Two `new Random(42)` objects, each asked for `nextInt(100)` three times…",
            ["produce the same three numbers", "produce different numbers",
             "throw", "depend on the clock"],
            0,
            "Same seed, same sequence - that is the point of a seed."),
        _jq("`rnd.nextInt(6)` returns values in…",
            ["0..5", "1..6", "0..6", "1..5"],
            0,
            "The bound is exclusive. Add 1 for a die."),
    ],
    exercises=[
        _je("j32-ra-dice", "A reproducible die",
            "Read a seed and a count, then roll a six-sided die that many times with one "
            "seeded generator, printing the rolls on one line. Replace `____` with a "
            "single roll.",
            _j32s("        long seed = sc.nextLong();\n"
                  "        int n = sc.nextInt();\n"
                  "        Random rnd = new Random(seed);\n"
                  "        StringBuilder out = new StringBuilder();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            if (i > 0) out.append(' ');\n"
                  "            out.append(rnd.nextInt(6) + 1);\n"
                  "        }\n"
                  "        System.out.println(out);"),
            "rnd.nextInt(6) + 1",
            [_seedcase32(s, n, _sp(_dice32(s, n))) for (s, n) in _SEEDS32],
            hints=["`nextInt(6)` gives 0..5.",
                   "A die shows 1..6, so shift by one.",
                   "`rnd.nextInt(6) + 1`",
                   "Because the seed is fixed, the judge knows exactly which rolls to "
                   "expect."],
            difficulty="Easy"),

        _jfix("j32-ra-reseed", "The die that always rolled the same",
              "This builds a fresh generator on every roll, so it prints the same number "
              "over and over. Make it draw a sequence from ONE generator.",
              _j32s("        long seed = sc.nextLong();\n"
                    "        int n = sc.nextInt();\n"
                    "        StringBuilder out = new StringBuilder();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            Random rnd = new Random(seed);\n"
                    "            if (i > 0) out.append(' ');\n"
                    "            out.append(rnd.nextInt(6) + 1);\n"
                    "        }\n"
                    "        System.out.println(out);"),
              _j32s("        long seed = sc.nextLong();\n"
                    "        int n = sc.nextInt();\n"
                    "        Random rnd = new Random(seed);\n"
                    "        StringBuilder out = new StringBuilder();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (i > 0) out.append(' ');\n"
                    "            out.append(rnd.nextInt(6) + 1);\n"
                    "        }\n"
                    "        System.out.println(out);"),
              [_seedcase32(s, n, _sp(_dice32(s, n))) for (s, n) in _SEEDS32],
              hints=["A generator with a given seed always starts its sequence from the "
                     "same place.",
                     "Building one per iteration means taking the FIRST value every time.",
                     "Move `new Random(seed)` above the loop.",
                     "The same mistake without a seed is subtler: generators created in "
                     "the same instant can share a clock-derived seed."],
              difficulty="Easy"),

        _jfix("j32-ra-range", "The value that never came up",
              "Roll numbers in the INCLUSIVE range `lo..hi`. This version can never "
              "produce `hi`. Fix the bound.",
              _j32s("        long seed = sc.nextLong();\n"
                    "        int lo = sc.nextInt();\n"
                    "        int hi = sc.nextInt();\n"
                    "        int n = sc.nextInt();\n"
                    "        Random rnd = new Random(seed);\n"
                    "        StringBuilder out = new StringBuilder();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (i > 0) out.append(' ');\n"
                    "            out.append(rnd.nextInt(hi - lo) + lo);\n"
                    "        }\n"
                    "        System.out.println(out);"),
              _j32s("        long seed = sc.nextLong();\n"
                    "        int lo = sc.nextInt();\n"
                    "        int hi = sc.nextInt();\n"
                    "        int n = sc.nextInt();\n"
                    "        Random rnd = new Random(seed);\n"
                    "        StringBuilder out = new StringBuilder();\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            if (i > 0) out.append(' ');\n"
                    "            out.append(rnd.nextInt(hi - lo + 1) + lo);\n"
                    "        }\n"
                    "        System.out.println(out);"),
              [_rangecase32(s, lo, hi, n) for (s, lo, hi, n) in _RANGES32],
              hints=["`nextInt(bound)` returns `0..bound-1`.",
                     "`nextInt(hi - lo)` therefore gives `0..hi-lo-1`, and adding `lo` "
                     "gives `lo..hi-1`.",
                     "There are `hi - lo + 1` values in an inclusive range.",
                     "`rnd.nextInt(hi - lo + 1) + lo`"],
              difficulty="Medium"),

        _jch("j32-ra-deal", "Shuffle and deal", "Medium",
             "Build the deck `1..n`, shuffle it reproducibly with the seed, print the "
             "shuffled deck, then deal it alternately into two hands (first card to hand "
             "A) and print each hand on its own line.",
             _j32s("        long seed = sc.nextLong();\n"
                   "        int n = sc.nextInt();\n"
                   "        List<Integer> deck = new ArrayList<>();\n"
                   "        for (int i = 1; i <= n; i++) {\n"
                   "            deck.add(i);\n"
                   "        }\n"
                   "        Collections.shuffle(deck, new Random(seed));\n"
                   "        System.out.println(deck);\n"
                   "        StringBuilder a = new StringBuilder();\n"
                   "        StringBuilder b = new StringBuilder();\n"
                   "        for (int i = 0; i < n; i++) {\n"
                   "            StringBuilder hand = (i % 2 == 0) ? a : b;\n"
                   "            if (hand.length() > 0) hand.append(' ');\n"
                   "            hand.append(deck.get(i));\n"
                   "        }\n"
                   "        System.out.println(a);\n"
                   "        System.out.println(b);"),
             "        Collections.shuffle(deck, new Random(seed));\n"
             "        System.out.println(deck);\n"
             "        StringBuilder a = new StringBuilder();\n"
             "        StringBuilder b = new StringBuilder();\n"
             "        for (int i = 0; i < n; i++) {\n"
             "            StringBuilder hand = (i % 2 == 0) ? a : b;\n"
             "            if (hand.length() > 0) hand.append(' ');\n"
             "            hand.append(deck.get(i));\n"
             "        }\n"
             "        System.out.println(a);\n"
             "        System.out.println(b);",
             [_seedcase32(s, n, _deal32(s, n)) for (s, n) in _DEALS32],
             hints=["`Collections.shuffle(deck, new Random(seed))` - the two-argument "
                    "form is the reproducible one.",
                    "Printing a `List` gives `[a, b, c]`.",
                    "Even positions (0, 2, 4, ...) go to hand A, odd ones to hand B.",
                    "`(i % 2 == 0) ? a : b` picks the hand without duplicating the "
                    "append code.",
                    "With `n` odd, hand A gets one card more."]),
    ],
    quiz=[
        _jq("Why is a seeded `Random` valuable in a test?",
            ["the same seed reproduces the same sequence, so a failure can be replayed",
             "it is more random", "it is faster", "it is thread-safe"],
            0,
            "Reproducibility is what makes randomness testable."),
        _jq("Generating a password reset token should use…",
            ["SecureRandom", "new Random()", "Math.random()", "new Random(seed)"],
            0,
            "`Random`'s future output can be predicted from a few past values."),
    ],
))


# ===========================================================================
# 32.4 LocalDate
# ===========================================================================

# (ISO date, days to add)
_PLUS32 = (("2024-01-31", 1), ("2023-12-25", 7), ("2024-02-28", 2),
           ("2023-03-01", -1), ("2024-12-31", 365))

# (from, to), from <= to
_BETWEEN32 = (("2024-01-01", "2024-12-31"), ("2023-01-31", "2024-03-01"),
              ("2024-02-29", "2024-02-29"), ("2020-05-15", "2024-05-14"),
              ("2023-12-25", "2024-01-08"))

# (start date, how many months)
_MONTHS32 = (("2024-01-31", 4), ("2023-10-31", 5), ("2024-03-15", 3),
             ("2023-08-31", 4), ("2024-02-29", 3))


def _plus_case32(iso, k):
    d = _d32(iso) + _dt32.timedelta(days=k)
    return _case(f"{iso}\n{k}", _nl(d.isoformat(), _dow32(d)))


def _between_case32(a, b):
    da, db = _d32(a), _d32(b)
    return _case(f"{a}\n{b}", _nl((db - da).days, _period32(da, db)))


def _months_case32(iso, k):
    d0 = _d32(iso)
    lines = []
    chained = d0
    for i in range(1, k + 1):
        chained = _plus_months32(chained, 1)
        lines.append(f"{_plus_months32(d0, i).isoformat()} {chained.isoformat()}")
    return _case(f"{iso}\n{k}", _nl(*lines))


_M32.append(_jlesson(
    "m32-dates", "`LocalDate` - dates without the pain",
    "Immutable values, arithmetic that respects the calendar, and the month that clamps.",
    """
Java's original `java.util.Date` was mutable, counted months from zero and years
from 1900, and mixed up "a date" with "an instant in time". **`java.time`**
(Java 8) replaced it, and it is built on one design decision: **every type is
an immutable value.**

`LocalDate` is a date with no time and no time zone - a birthday, a due date,
a holiday. "Local" means *as it reads on a calendar*, not "in my time zone".

```java
LocalDate d = LocalDate.of(2024, 1, 31);     // months are 1-12, finally
LocalDate e = LocalDate.parse("2024-01-31"); // ISO yyyy-MM-dd
System.out.println(d);                       // 2024-01-31
d.getDayOfWeek()                             // WEDNESDAY  (a DayOfWeek enum)
d.isLeapYear()      d.lengthOfMonth()        // true, 31
d.isBefore(e)       d.isAfter(e)   d.equals(e)
```

## Immutability, and the bug it causes

```java
d.plusDays(1);                // computes a new date... and throws it away
System.out.println(d);        // still 2024-01-31
d = d.plusDays(1);            // what you meant
```

Every "modifying" method - `plusDays`, `minusWeeks`, `withDayOfMonth` - returns
a **new** `LocalDate`. That makes dates safe to share, cache and use as map
keys; it also means a call whose result is ignored does nothing at all. It is
exactly the `String.toUpperCase()` mistake from module 6.

## Month arithmetic clamps

```java
LocalDate.of(2024, 1, 31).plusMonths(1)   // 2024-02-29 - no Feb 31, so the last day
```

`plusMonths` keeps the day-of-month if it can and otherwise **clamps to the
month's last day**. That has a consequence people trip over: adding one month
three times is not the same as adding three months.

```java
jan31.plusMonths(3)                               // 2024-04-30
jan31.plusMonths(1).plusMonths(1).plusMonths(1)   // 2024-04-29 - the 29 stuck
```

For a monthly schedule, always compute each date from the *original* start.

## How far apart?

```java
ChronoUnit.DAYS.between(a, b)    // a long: total days, negative if b < a
Period.between(a, b)             // P1Y1M1D - years, months and days
```

They answer different questions. `DAYS.between` is "how many days", which is
what a fine, an interval or a countdown needs. `Period` is "how would a person
say it" - one year, one month, one day - and its `getDays()` is only the *days
part*, not the total. Mixing them up is a real bug: `Period.between(jan1,
mar1).getDays()` is `0`.
""",
    warmup=[
        _jq("`d.plusDays(1);` on its own line…",
            ["changes nothing - the new date is discarded", "moves d forward a day",
             "does not compile", "throws"],
            0,
            "LocalDate is immutable. Assign the result."),
        _jq("`LocalDate.of(2023, 1, 31).plusMonths(1)` is…",
            ["2023-02-28", "2023-03-03", "2023-02-31", "an exception"],
            0,
            "It clamps to the last valid day of February."),
    ],
    exercises=[
        _je("j32-da-plus", "A week from Tuesday",
            "Read a date and a number of days (possibly negative). Print the date that "
            "many days later, then its day of the week. Replace `____` with the "
            "arithmetic.",
            _j32s("        LocalDate date = LocalDate.parse(sc.next());\n"
                  "        int k = sc.nextInt();\n"
                  "        LocalDate later = date.plusDays(k);\n"
                  "        System.out.println(later);\n"
                  "        System.out.println(later.getDayOfWeek());"),
            "date.plusDays(k)",
            [_plus_case32(iso, k) for (iso, k) in _PLUS32],
            hints=["`plusDays` returns a NEW date.",
                   "A negative argument goes backwards - no need for `minusDays`.",
                   "`date.plusDays(k)`",
                   "Month and year boundaries, and leap days, are handled for you."],
            difficulty="Easy"),

        _jfix("j32-da-immutable", "The date that would not move",
              "This is meant to print the date `k` days later and its weekday, but it "
              "prints the original date every time. Fix it.",
              _j32s("        LocalDate date = LocalDate.parse(sc.next());\n"
                    "        int k = sc.nextInt();\n"
                    "        date.plusDays(k);\n"
                    "        System.out.println(date);\n"
                    "        System.out.println(date.getDayOfWeek());"),
              _j32s("        LocalDate date = LocalDate.parse(sc.next());\n"
                    "        int k = sc.nextInt();\n"
                    "        date = date.plusDays(k);\n"
                    "        System.out.println(date);\n"
                    "        System.out.println(date.getDayOfWeek());"),
              [_plus_case32(iso, k) for (iso, k) in _PLUS32],
              hints=["`LocalDate` never changes after it is made.",
                     "`plusDays` hands back a new date - which this code ignores.",
                     "`date = date.plusDays(k);`",
                     "Module 6's `s.toUpperCase();` is the same bug in a different class."],
              difficulty="Easy"),

        _je("j32-da-between", "How long, two ways",
            "Read two dates, the first no later than the second. Print the total number "
            "of days between them, then the `Period`. Replace `____` with the day count.",
            _j32s("        LocalDate from = LocalDate.parse(sc.next());\n"
                  "        LocalDate to = LocalDate.parse(sc.next());\n"
                  "        System.out.println(ChronoUnit.DAYS.between(from, to));\n"
                  "        System.out.println(Period.between(from, to));"),
            "ChronoUnit.DAYS.between(from, to)",
            [_between_case32(a, b) for (a, b) in _BETWEEN32],
            hints=["`ChronoUnit.DAYS.between(a, b)` counts every day from a up to b.",
                   "It returns a `long`, and would be negative if `to` came first.",
                   "`Period` prints as `P1Y1M1D`, and `P0D` for no gap at all.",
                   "The two answer different questions: 'how many days' versus 'how "
                   "would a person say it'."],
            difficulty="Easy"),

        _jch("j32-da-monthly", "The schedule that drifted", "Hard",
             "A monthly payment starts on a date. For each of the next `k` months print "
             "two dates on one line: the date computed from the START (`start.plusMonths(i)`), "
             "and the date reached by adding one month to the PREVIOUS date. Watch the "
             "second column drift after a short month.",
             _j32s("        LocalDate start = LocalDate.parse(sc.next());\n"
                   "        int k = sc.nextInt();\n"
                   "        LocalDate chained = start;\n"
                   "        for (int i = 1; i <= k; i++) {\n"
                   "            chained = chained.plusMonths(1);\n"
                   "            System.out.println(start.plusMonths(i) + \" \" + chained);\n"
                   "        }"),
             "        LocalDate chained = start;\n"
             "        for (int i = 1; i <= k; i++) {\n"
             "            chained = chained.plusMonths(1);\n"
             "            System.out.println(start.plusMonths(i) + \" \" + chained);\n"
             "        }",
             [_months_case32(iso, k) for (iso, k) in _MONTHS32],
             hints=["`plusMonths` clamps: Jan 31 plus one month is the last day of "
                    "February.",
                    "The first column never drifts, because each value starts from the "
                    "original day-of-month.",
                    "The second column starts from a clamped date, so the smaller day "
                    "sticks.",
                    "`chained = chained.plusMonths(1);` - remember to assign.",
                    "A date concatenated to a String prints in ISO form."]),
    ],
    quiz=[
        _jq("`Period.between(2024-01-01, 2024-03-01).getDays()` is…",
            ["0", "60", "2", "59"],
            0,
            "The Period is P2M; `getDays()` is only the days PART."),
        _jq("Why is `LocalDate` immutable?",
            ["so it can be shared, cached and used as a map key safely",
             "for speed only", "because Java has no setters", "it is not"],
            0,
            "Values that cannot change cannot be changed behind your back."),
    ],
))


# ===========================================================================
# 32.5 Formatting
# ===========================================================================

_SCORES32 = ([("ada", 97), ("bo", 5)], [("grace", 100)], [("x", 0), ("yy", 12), ("zzz", 345)],
             [("alan", 88), ("barbara", 1234)], [("linus", 7), ("ken", 42)])


def _scores32(rows, out):
    stdin = "\n".join([str(len(rows))] + [f"{n} {s}" for (n, s) in rows])
    return _case(stdin, out)


def _table32(rows):
    return _nl(*[f"{n:<8}|{s:>5}" for (n, s) in rows])


# Integer lists whose averages print to two places - including a HALF (x.xx5)
# that shows the rounding rule.
_AVGS32 = ([1, 2], [10, 20, 25], [1, 1, 1, 2, 2, 2, 2, 2], [-3, -4], [100])


def _avg32(xs):
    return _f32(sum(xs) / len(xs))


_SLASH32 = ("31/01/2024", "29/02/2024", "01/12/2023", "15/08/1947", "03/03/2024")


def _slash_case32(s):
    dd, mm, yy = (int(p) for p in s.split("/"))
    d = _dt32.date(yy, mm, dd)
    return _case(s, _nl(d.isoformat(), _dow32(d), _pretty32(d)))


_REFMT32 = ("2024-01-31", "2024-02-29", "2023-12-01", "1947-08-15", "2024-03-03")


_M32.append(_jlesson(
    "m32-format", "Formatting, and the `Locale` nobody passes",
    "`String.format` and `DateTimeFormatter` - and why the same line prints `3.14` here "
    "and `3,14` in Berlin.",
    """
## `String.format` and `printf`

```java
String.format("%-8s|%5d", name, score)   // "ada     |   97"
System.out.printf("%d items%n", n);      // printf = format + print
```

A format specifier is `%[flags][width][.precision]conversion`:

| spec | means | `42` / `3.14159` / `"ab"` |
|---|---|---|
| `%d` | integer | `42` |
| `%5d` | right-aligned in 5 | `   42` |
| `%-5d` | left-aligned in 5 | `42   ` |
| `%05d` | zero-padded | `00042` |
| `%x` | hexadecimal | `2a` |
| `%.2f` | 2 decimal places | `3.14` |
| `%8.3f` | width 8, 3 places | `   3.142` |
| `%s` / `%-6s` | string / left in 6 | `ab` / `ab    ` |
| `%b` | boolean | `true` |
| `%%` / `%n` | a literal `%` / a newline | |

`%.2f` **rounds half up**, on the number as Java would print it: `1.005` becomes
`1.01`. (Python's formatting gives `1.00` for the same value - a reminder that
"round to two places" is less universal than it sounds.)

## The `Locale`, which is the actual lesson

```java
String.format("%.2f", 3.14159)              // "3.14" - on YOUR machine
// on a machine set to German:              // "3,14"
String.format(Locale.ROOT, "%.2f", 3.14159) // "3.14" everywhere
```

Without a `Locale` argument, `format` uses the machine's default, which decides
the decimal separator, the digit grouping of `%,d`, and the language of month
names. That is right for text shown to a *person*, and a bug for anything a
*program* will read back - a CSV file, a log line, a JSON number, a test's
expected output. Pass `Locale.ROOT` (the neutral locale) whenever the output is
data. Every program in this module does.

## `DateTimeFormatter`

```java
DateTimeFormatter f = DateTimeFormatter.ofPattern("dd/MM/yyyy");
LocalDate d = LocalDate.parse("31/01/2024", f);   // parse with a pattern
d.format(f)                                       // "31/01/2024"
d.format(DateTimeFormatter.ofPattern("EEE, d MMM yyyy", Locale.ENGLISH))
                                                  // "Wed, 31 Jan 2024"
```

The pattern letters are **case-sensitive**, and the classic bug is one letter:

| letter | means |
|---|---|
| `yyyy` | year |
| `MM` / `MMM` | month number / short month name |
| `dd` / `d` | day, padded / not |
| `EEE` | short day name |
| `HH` / `mm` / `ss` | hour (0-23) / **minute** / second |

`dd/mm/yyyy` asks for *minutes*, which a `LocalDate` does not have - formatting
throws `UnsupportedTemporalTypeException`. A name pattern (`EEE`, `MMM`) also
depends on the locale, so pass one, as above.

Like everything in `java.time`, a `DateTimeFormatter` is immutable and
thread-safe, so a formatter is normally a `static final` constant, built once.
""",
    warmup=[
        _jq("`String.format(\"%05d\", 42)` is…",
            ["00042", "42000", "   42", "42   "],
            0,
            "The `0` flag pads with zeros to the width."),
        _jq("In a `DateTimeFormatter` pattern, `mm` means…",
            ["minutes", "month", "milliseconds", "month name"],
            0,
            "Month is `MM`. Case matters."),
    ],
    exercises=[
        _je("j32-fo-table", "A table that lines up",
            "Print each name left-aligned in 8 characters, a `|`, then the score "
            "right-aligned in 5. Replace `____` with the format string.",
            _j32s("        int n = sc.nextInt();\n"
                  "        for (int i = 0; i < n; i++) {\n"
                  "            String name = sc.next();\n"
                  "            int score = sc.nextInt();\n"
                  "            System.out.println(String.format(Locale.ROOT, \"%-8s|%5d\", name, score));\n"
                  "        }"),
            "\"%-8s|%5d\"",
            [_scores32(rows, _table32(rows)) for rows in _SCORES32],
            hints=["`%s` is a string and `%d` an integer.",
                   "A number between `%` and the letter is a width; `-` left-aligns.",
                   "`\"%-8s|%5d\"`",
                   "A name longer than 8 is NOT truncated - the width is a minimum."],
            difficulty="Easy"),

        _je("j32-fo-average", "Two decimal places",
            "Print the average of the integers to exactly two decimal places. Replace "
            "`____` with the format call.",
            _j32s(_RD_ARR
                  + "        int sum = 0;\n"
                    "        for (int x : a) {\n"
                    "            sum += x;\n"
                    "        }\n"
                    "        double average = (double) sum / n;\n"
                    "        System.out.println(String.format(Locale.ROOT, \"%.2f\", average));"),
            "String.format(Locale.ROOT, \"%.2f\", average)",
            [_acase(xs, _avg32(xs)) for xs in _AVGS32],
            hints=["`%.2f` prints a double with two digits after the point.",
                   "Pass `Locale.ROOT` first so the separator is always a dot.",
                   "`String.format(Locale.ROOT, \"%.2f\", average)`",
                   "`1.625` rounds UP to `1.63`: halves round up."],
            difficulty="Easy"),

        _jfix("j32-fo-pattern", "Minutes where the month should be",
              "This should parse an ISO date and print it as `dd/MM/yyyy`, but it throws "
              "`UnsupportedTemporalTypeException` on every input. Fix the pattern.",
              _j32s("        LocalDate d = LocalDate.parse(sc.next());\n"
                    "        DateTimeFormatter f = DateTimeFormatter.ofPattern(\"dd/mm/yyyy\");\n"
                    "        System.out.println(d.format(f));"),
              _j32s("        LocalDate d = LocalDate.parse(sc.next());\n"
                    "        DateTimeFormatter f = DateTimeFormatter.ofPattern(\"dd/MM/yyyy\");\n"
                    "        System.out.println(d.format(f));"),
              [_case(iso, _slash32(_d32(iso))) for iso in _REFMT32],
              hints=["Pattern letters are case-sensitive.",
                     "Lower-case `mm` is minute-of-hour.",
                     "A `LocalDate` has no time, so it cannot supply minutes.",
                     "Month is upper-case `MM`."],
              difficulty="Easy"),

        _jch("j32-fo-parse", "Read it one way, print it another", "Medium",
             "Read a date written `dd/MM/yyyy`. Print it in ISO form, then its day of the "
             "week, then as `EEE, d MMM yyyy` in English. Write the three lines, parsing "
             "with a formatter.",
             _j32s("        DateTimeFormatter in = DateTimeFormatter.ofPattern(\"dd/MM/yyyy\");\n"
                   "        DateTimeFormatter out = DateTimeFormatter.ofPattern(\"EEE, d MMM yyyy\", Locale.ENGLISH);\n"
                   "        LocalDate d = LocalDate.parse(sc.next(), in);\n"
                   "        System.out.println(d);\n"
                   "        System.out.println(d.getDayOfWeek());\n"
                   "        System.out.println(d.format(out));"),
             "        LocalDate d = LocalDate.parse(sc.next(), in);\n"
             "        System.out.println(d);\n"
             "        System.out.println(d.getDayOfWeek());\n"
             "        System.out.println(d.format(out));",
             [_slash_case32(s) for s in _SLASH32],
             hints=["`LocalDate.parse(text, formatter)` - the two-argument form.",
                    "Printing a `LocalDate` directly gives ISO `yyyy-MM-dd`.",
                    "`getDayOfWeek()` prints in capitals: `WEDNESDAY`.",
                    "`d.format(out)` uses the English names because `out` was built "
                    "with `Locale.ENGLISH`.",
                    "`d` (single letter) does not pad the day; `dd` would."]),
    ],
    quiz=[
        _jq("Output that another PROGRAM will parse should be formatted with…",
            ["Locale.ROOT", "the default locale", "Locale.GERMAN", "no format at all"],
            0,
            "The default locale changes decimal separators and names per machine."),
        _jq("`String.format(Locale.ROOT, \"%.2f\", 2.675)` prints…",
            ["2.68", "2.67", "2.7", "2.675"],
            0,
            "Java rounds half up on the value as it prints it: 2.675 becomes 2.68."),
    ],
))


# ===========================================================================
# Capstone - the library desk
# ===========================================================================

# (loan date, loan days, returned date, fine per day in cents)
_LOANS32 = (
    ("2024-02-20", 14, "2024-03-08", 25),
    ("2024-01-31", 21, "2024-02-15", 50),
    ("2023-12-20", 14, "2024-01-03", 30),
    ("2024-02-28", 7, "2024-03-31", 125),
    ("2023-06-01", 30, "2023-08-15", 99),
)

_CAP_HELPERS32 = (
    "    static final DateTimeFormatter PRETTY =\n"
    "            DateTimeFormatter.ofPattern(\"EEE, d MMM yyyy\", Locale.ENGLISH);\n"
    "\n"
    "    static long daysLate(LocalDate due, LocalDate returned) {\n"
    "        return Math.max(0, ChronoUnit.DAYS.between(due, returned));\n"
    "    }\n"
    "\n"
    "    static String money(long cents) {\n"
    "        return String.format(Locale.ROOT, \"%.2f\", cents / 100.0);\n"
    "    }"
)

_CAP_BODY32 = (
    "        LocalDate loaned = LocalDate.parse(sc.next());\n"
    "        int days = sc.nextInt();\n"
    "        LocalDate returned = LocalDate.parse(sc.next());\n"
    "        int perDay = sc.nextInt();\n"
    "        LocalDate due = loaned.plusDays(days);\n"
    "        long late = daysLate(due, returned);\n"
    "        long fine = Math.multiplyExact(late, (long) perDay);\n"
    "        System.out.println(\"due: \" + due.format(PRETTY));\n"
    "        System.out.println(\"returned: \" + returned.format(PRETTY));\n"
    "        System.out.println(late == 0 ? \"on time\" : \"late by \" + late + \" days\");\n"
    "        System.out.println(\"fine: \" + money(fine));"
)


def _cap_case32(loaned, days, returned, per_day):
    due = _d32(loaned) + _dt32.timedelta(days=days)
    ret = _d32(returned)
    late = max(0, (ret - due).days)
    fine = late * per_day
    return _case(f"{loaned} {days}\n{returned} {per_day}",
                 _nl("due: " + _pretty32(due),
                     "returned: " + _pretty32(ret),
                     "on time" if late == 0 else f"late by {late} days",
                     "fine: " + _f32(fine / 100.0)))


_M32_CAP = _jcap(
    "The library desk",
    """
A book is lent on a date for a number of days, and comes back on another date.
Write the three helpers the desk's `main` relies on:

* **`PRETTY`** - a `static final DateTimeFormatter` printing `EEE, d MMM yyyy` in
  English. Built once; formatters are immutable and thread-safe.
* **`daysLate(due, returned)`** - the number of days after the due date the book
  came back, as a `long`, and **never negative**: early is simply on time.
* **`money(cents)`** - a fine in cents as a two-decimal string, **locale-proof**.

`main` then works out the due date (`plusDays` - and remembers to keep the
result), multiplies the late days by the daily fine with `Math.multiplyExact` so
an absurd fine throws instead of wrapping, and prints four lines.
""",
    _jch("j32-cap-desk", "The library desk", "Hard",
         "Write `PRETTY`, `daysLate` and `money` as the brief describes, so the given "
         "`main` prints its four lines.",
         _j32(_CAP_HELPERS32, _CAP_BODY32),
         _CAP_HELPERS32,
         [_cap_case32(*loan) for loan in _LOANS32],
         hints=["`DateTimeFormatter.ofPattern(\"EEE, d MMM yyyy\", Locale.ENGLISH)` - the "
                "locale fixes the day and month names.",
                "`ChronoUnit.DAYS.between(due, returned)` is negative when the book came "
                "back early.",
                "`Math.max(0, ...)` floors it at zero; with a `long` argument it returns a "
                "`long`.",
                "`cents / 100.0` divides in double; `%.2f` prints two places.",
                "Pass `Locale.ROOT` to `String.format` so the separator is a dot on every "
                "machine.",
                "Returned exactly on the due date is on time: zero days late."]),
    example_io="stdin:  2024-02-20 14\n        2024-03-08 25\n\n"
               "stdout: due: Tue, 5 Mar 2024\n        returned: Fri, 8 Mar 2024\n"
               "        late by 3 days\n        fine: 0.75",
    rubric=[
        "`PRETTY` is a `static final` formatter built with `Locale.ENGLISH`.",
        "`daysLate` uses `ChronoUnit.DAYS.between`, not `Period.getDays()`.",
        "`daysLate` never returns a negative number.",
        "`money` passes `Locale.ROOT` to `String.format`.",
        "No `LocalDate` method is called with its result ignored.",
    ],
)


_MODULES.append(_jmod(
    32, 11, "The APIs worth knowing cold",
    "The APIs worth knowing cold",
    "The standard-library corners every Java developer is expected to know without "
    "looking up - and exactly where each one bites.",
    """
Most of the roadmap's "APIs worth knowing cold" list was taught where it was first
needed: `Arrays` in module 1, `String` in 6 and 7, `StringBuilder` in 8, the
collections in 17-20. This module is the remainder, and every lesson is about the
place the API fails quietly:

* **`Math`.** `int` overflow wraps without a word, so use `addExact` and friends
  where it would be a bug. `%` is a remainder that goes negative - `floorMod` is the
  modulus. `Math.abs(Integer.MIN_VALUE)` is still negative, and `Math.round`
  returns a `long` and rounds halves up.
* **`Objects`.** `equals`, `hash`, `toString` and `requireNonNull`, all of which
  exist to make null somebody else's problem - or, with `requireNonNull`, a problem
  reported at the door.
* **`Random`.** A seed makes it reproducible, which is what makes it testable.
  Create it once; `nextInt(bound)` excludes the bound; `SecureRandom` for anything
  secret.
* **`LocalDate`.** Immutable - so an ignored `plusDays` does nothing. Month
  arithmetic clamps, so chaining `plusMonths(1)` drifts. `DAYS.between` counts days;
  `Period` describes the gap the way a person would.
* **Formatting.** `String.format`'s specifiers, `DateTimeFormatter`'s
  case-sensitive letters (`MM` is month, `mm` is minute), and the `Locale` argument
  that decides whether your output is `3.14` or `3,14`.
""",
    _M32,
    capstone=_M32_CAP,
    objectives=[
        "Explain why int overflow is silent, and use the `*Exact` methods to make it loud.",
        "Say why `Math.abs(Integer.MIN_VALUE)` is negative.",
        "Choose between `%` and `Math.floorMod`, and `/` and `Math.floorDiv`, for negative operands.",
        "Predict the result and type of `Math.round`, `Math.floor`, `Math.ceil` and an `(int)` cast.",
        "Use `Objects.equals`, `Objects.hash`, `Objects.toString` and `Objects.requireNonNull`.",
        "Use a seeded `Random` to make output reproducible, and avoid the reseeding and off-by-one bugs.",
        "Shuffle reproducibly with `Collections.shuffle(list, rnd)`.",
        "Do date arithmetic with `LocalDate`, remembering that every method returns a new value.",
        "Explain why chained `plusMonths(1)` drifts, and compute a schedule from its start instead.",
        "Distinguish `ChronoUnit.DAYS.between` from `Period.between`.",
        "Write `String.format` specifiers for width, alignment, padding and precision.",
        "Say when to pass `Locale.ROOT`, and fix a `DateTimeFormatter` pattern that uses `mm` for month.",
    ],
    why="Interviewers rarely ask about these APIs directly - they show up as the bug in "
        "your solution. An average that goes negative in the wrong direction, a circular "
        "buffer that crashes on a negative index, a sum that wraps, a date that never "
        "moves, a test that passes on your laptop and fails on the CI machine in another "
        "country. Knowing exactly where each of these bites is what lets you write the "
        "correct version first time, and explain why it is correct.",
    est_minutes=300,
    glossary=[
        _jg("Integer overflow", "When an int result does not fit in 32 bits it wraps "
                                "round, silently. `Integer.MAX_VALUE + 1` is "
                                "`Integer.MIN_VALUE`."),
        _jg("Math.addExact", "Adds two ints (or longs) and throws ArithmeticException "
                             "instead of wrapping. Also `subtractExact`, `multiplyExact`, "
                             "`negateExact`, `toIntExact`."),
        _jg("Math.floorMod", "A modulus whose result takes the sign of the divisor - "
                             "always 0..n-1 for a positive n. Unlike `%`, which is a "
                             "remainder."),
        _jg("Math.floorDiv", "Integer division that rounds down (toward negative "
                             "infinity), where `/` truncates toward zero."),
        _jg("Math.round", "`floor(x + 0.5)`: halves round up. Returns a long for a "
                          "double argument."),
        _jg("Objects.requireNonNull", "Returns its argument, or throws "
                                      "NullPointerException with your message if it is "
                                      "null - at the point the bad value arrives."),
        _jg("Seed", "The starting state of a pseudo-random generator. The same seed "
                    "always produces the same sequence."),
        _jg("SecureRandom", "A generator whose output cannot feasibly be predicted - "
                            "the one to use for tokens, keys and passwords."),
        _jg("LocalDate", "An immutable calendar date with no time or time zone."),
        _jg("Period", "A date-based amount of time in years, months and days - "
                      "`P1Y2M3D`."),
        _jg("ChronoUnit.DAYS.between", "The total number of days between two dates, as "
                                       "a long."),
        _jg("DateTimeFormatter", "An immutable, thread-safe pattern for printing and "
                                 "parsing dates and times."),
        _jg("Locale.ROOT", "The neutral locale. Pass it when output is data another "
                           "program will read."),
    ],
    cheatsheet="""
```java
// --- Math: make failure loud --------------------------------------------------
Math.addExact(a, b)  Math.multiplyExact(a, b)  Math.toIntExact(someLong)  // throw
Math.abs(Integer.MIN_VALUE)          // -2147483648 - still negative
-1 % 5  == -1        Math.floorMod(-1, 5)  == 4     // circular index: floorMod
-7 / 2  == -3        Math.floorDiv(-7, 2)  == -4
Math.round(2.5) == 3   Math.round(-2.5) == -2       // long; halves go up
Math.floor(-2.5) == -3.0   Math.ceil(2.1) == 3.0    // double!
(int) -2.9 == -2                                    // truncates toward zero

// --- Objects: null-safe ---------------------------------------------------------
Objects.equals(a, b)                 // null-safe equals
Objects.hash(key, count)             // several fields -> one hash (null = 0)
Objects.hashCode(x)                  // ONE value; 0 for null (not the same as hash(x))
Objects.toString(x, "(none)")        // default for null
this.name = Objects.requireNonNull(name, "name");   // reject at the door
list.stream().filter(Objects::nonNull)

// --- Random ------------------------------------------------------------------
Random rnd = new Random(42);         // create ONCE; same seed, same sequence
rnd.nextInt(6) + 1                   // a die: bound is exclusive
rnd.nextInt(hi - lo + 1) + lo        // lo..hi inclusive
Collections.shuffle(list, rnd);      // reproducible shuffle
// secrets: SecureRandom.   threads: ThreadLocalRandom.current().

// --- LocalDate -----------------------------------------------------------------
LocalDate d = LocalDate.parse("2024-01-31");
d = d.plusDays(1);                   // ASSIGN - it is immutable
d.getDayOfWeek()  d.isLeapYear()  d.lengthOfMonth()  d.isBefore(e)
LocalDate.of(2024, 1, 31).plusMonths(1)    // 2024-02-29 (clamped)
start.plusMonths(i)                  // schedules: from the START, never chained
ChronoUnit.DAYS.between(a, b)        // total days (long)
Period.between(a, b)                 // P1Y1M1D; getDays() is only the days PART

// --- Formatting ------------------------------------------------------------------
String.format(Locale.ROOT, "%-8s|%5d|%05d|%.2f|%x|%%", s, n, n, x, n)
DateTimeFormatter f = DateTimeFormatter.ofPattern("dd/MM/yyyy");   // MM month, mm MINUTE
LocalDate.parse("31/01/2024", f);   d.format(f);
DateTimeFormatter.ofPattern("EEE, d MMM yyyy", Locale.ENGLISH)      // names need a locale
```
""",
    self_check=[
        "Can you say what `Integer.MAX_VALUE + 1` is, and which method would have thrown instead?",
        "Can you explain why checking only the final total misses some overflows?",
        "Can you give `-7 % 3`, `Math.floorMod(-7, 3)`, `-7 / 2` and `Math.floorDiv(-7, 2)`?",
        "Can you say what `Math.round(-2.5)` returns, and its type?",
        "Can you say why `Objects.hash(x)` differs from `Objects.hashCode(x)`?",
        "Can you explain what a seed is, and why seeding makes a program testable?",
        "Can you spot the bug in `new Random(seed)` inside a loop?",
        "Can you explain why `d.plusDays(1);` does nothing?",
        "Can you explain why adding one month three times can differ from adding three months?",
        "Can you say when `Period.getDays()` is the wrong way to count days?",
        "Can you say what `mm` means in a date pattern, and what happens if you use it on a LocalDate?",
        "Can you say when to pass `Locale.ROOT`, and what can go wrong without it?",
    ],
    review=[
        _jq("A running `int` total goes 2e9, 4e9, 2e9. Checking only the final value…",
            ["misses the overflow in the middle", "catches it", "throws", "is exact"],
            0,
            "The middle step wrapped. `addExact` checks every step."),
        _jq("A circular buffer of size n steps back from index 0. The safe index is…",
            ["Math.floorMod(i - 1, n)", "(i - 1) % n", "Math.abs(i - 1) % n", "i - 1"],
            0,
            "`%` would give -1 and an out-of-bounds exception."),
        _jq("`for (...) { new Random(7).nextInt(10); }` produces…",
            ["the same number every iteration", "a random sequence",
             "an exception", "a different number each time"],
            0,
            "Each new generator restarts the same sequence."),
        _jq("Monthly dates for a loan taken on 31 January should be computed as…",
            ["start.plusMonths(i)", "d = d.plusMonths(1) repeatedly",
             "d.plusDays(30 * i)", "Period.ofMonths(i).getDays()"],
            0,
            "Chaining lets a clamped day stick."),
        _jq("`String.format(\"%.2f\", x)` in a CSV export is a bug because…",
            ["the default locale may use a comma as the decimal separator",
             "it rounds", "it is slow", "it adds spaces"],
            0,
            "Pass `Locale.ROOT` for anything a program will read back."),
    ],
    milestone="You know where the standard library fails quietly - overflow, negative "
              "remainders, reseeded generators, ignored dates, drifting months and "
              "locale-dependent output - and you reach for the version that fails "
              "loudly, or not at all.",
))
