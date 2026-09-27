# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 32 practice - the APIs worth knowing cold.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[32]`.
#
# Reuses the module file's Python mirrors (`_JRandom32`, `_jshuffle32`,
# `_ohash32`, `_f32`, `_plus_months32`, ...), which were checked against a real
# JVM - so a seeded shuffle or a `%.2f` here is computed exactly the way Java
# computes it, never typed.
#
# Same rules as the module: every String.format passes Locale.ROOT, and every
# pattern that prints a NAME passes Locale.ENGLISH.
# ---------------------------------------------------------------------------


def _p32prog(helpers, body):
    return _jcls(
        helpers.rstrip("\n") + "\n\n"
        + _MAIN_SIG + "\n"
        + "        Scanner sc = new Scanner(System.in);\n"
        + body.rstrip("\n") + "\n"
        + "    }",
        imports=_IMPORTS32,
    )


def _p32s(eid, title, difficulty, prompt, body, tests, hints):
    """No helpers - write main's whole body."""
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _j32s(body), body, tests, hints)


def _p32m(eid, title, difficulty, prompt, helpers, body, tests, hints):
    """Write the METHOD(S); main is given."""
    return _jch(eid, title, difficulty, prompt, _p32prog(helpers, body),
                helpers.rstrip("\n").lstrip("\n"), tests, hints)


def _p32t(eid, title, difficulty, prompt, types, body, region, tests, hints):
    """A helper class above Main; `region` is the part of it you write."""
    return _jch(eid, title, difficulty, prompt, _j32t(types, body), region, tests, hints)


def _lines32(rows, out):
    """stdin = a count, then one line per row (each row a tuple of tokens)."""
    stdin = "\n".join([str(len(rows))] + [" ".join(str(t) for t in r) for r in rows])
    return _case(stdin, out)


# --- Family A - arithmetic that fails loudly --------------------------------

_CLOCK32 = ([(9, 5), (22, 3)], [(0, -1)], [(5, -30), (12, 48)], [(23, 1), (1, -25)],
            [(7, 0), (18, -18), (3, 100)])
_BUCKET32 = ([15, -1], [0, 9, 10], [-10, -11], [99, -99, 5], [-5])
_FACT32 = (5, 12, 13, 15, 1)
_POW32 = ((2, 62), (2, 63), (3, 39), (-2, 63), (10, 18))
_NEAR32 = ([(17, 5), (-17, 5)], [(25, 10), (-25, 10)], [(7, 7)], [(-1, 4), (2, 4)],
           [(149, 100), (150, 100), (-150, 100)])


def _fact_out32(n):
    lines, f = [], 1
    for k in range(1, n + 1):
        f *= k
        if not _fits32(f):
            lines.append(f"overflow at {k}")
            break
        lines.append(f"{k}! = {f}")
    return _nl(*lines)


def _pow_out32(b, e):
    r = 1
    for _ in range(e):
        r *= b
        if not _fitsl32(r):
            return "overflow"
    return str(r)


_P32_A = _jfam(
    "p32-math", "Arithmetic that fails loudly",
    "`floorMod`, `floorDiv`, the `*Exact` methods and `Math.round`.",
    """
Three habits, each replacing an operator that is quietly wrong for some inputs:

```java
Math.floorMod(k, n)        // not k % n       - negative k
Math.floorDiv(v, 10)       // not v / 10      - negative v rounds DOWN
Math.multiplyExact(a, b)   // not a * b       - throws instead of wrapping
```

And one to remember the shape of: `Math.round(x)` is `floor(x + 0.5)` and
returns a `long`, so `Math.round(-2.5)` is `-2`.

The worked case: 13! does not fit in an `int`. Multiplying with `*` gives
`1932053504` - wrong, and plausible. `multiplyExact` throws at 13, which is the
only honest answer.
""",
    [
        _p32s("j32-pa-clock", "The 24-hour clock", "Intro",
              "Each line is an hour `h` and an offset `k` in hours (possibly negative). "
              "Print the hour on a 24-hour clock after the offset.",
              "        int q = sc.nextInt();\n"
              "        for (int i = 0; i < q; i++) {\n"
              "            int h = sc.nextInt();\n"
              "            int k = sc.nextInt();\n"
              "            System.out.println(Math.floorMod(h + k, 24));\n"
              "        }",
              [_lines32(rows, _nl(*[(h + k) % 24 for (h, k) in rows])) for rows in _CLOCK32],
              ["`(h + k) % 24` goes negative for a large negative offset.",
               "`Math.floorMod(h + k, 24)` always lands in 0..23.",
               "One hour before midnight (0, -1) is 23."]),

        _p32s("j32-pa-bucket", "Buckets of ten", "Easy",
              "Each value belongs to the bucket `floor(v / 10)`, so -1 is in bucket -1 "
              "and 15 in bucket 1. Print `v -> bucket` for each.",
              _RD_ARR
              + "        for (int v : a) {\n"
                "            System.out.println(v + \" -> \" + Math.floorDiv(v, 10));\n"
                "        }",
              [_acase(vs, _nl(*[f"{v} -> {v // 10}" for v in vs])) for vs in _BUCKET32],
              ["`-1 / 10` is 0 in Java - it truncates toward zero.",
               "Bucket boundaries must not have a double-width bucket around zero.",
               "`Math.floorDiv(v, 10)` rounds down: -1 goes to -1."]),

        _p32s("j32-pa-factorial", "Factorials until they break", "Medium",
              "Print `k! = value` for k = 1..n using `int` arithmetic, but the moment a "
              "factorial does not fit, print `overflow at k` and stop.",
              "        int n = sc.nextInt();\n"
              "        int f = 1;\n"
              "        for (int k = 1; k <= n; k++) {\n"
              "            try {\n"
              "                f = Math.multiplyExact(f, k);\n"
              "            } catch (ArithmeticException e) {\n"
              "                System.out.println(\"overflow at \" + k);\n"
              "                break;\n"
              "            }\n"
              "            System.out.println(k + \"! = \" + f);\n"
              "        }",
              [_case(str(n), _fact_out32(n)) for n in _FACT32],
              ["`f * k` wraps silently at 13!; `Math.multiplyExact(f, k)` throws.",
               "Put the `try` INSIDE the loop, so the catch block still knows `k`.",
               "`break` after reporting - there is nothing sensible to multiply next.",
               "12! = 479001600 is the largest factorial an int can hold."]),

        _p32s("j32-pa-power", "Powers that must be exact", "Medium",
              "Read a base and an exponent and print base^exponent as a `long` computed "
              "by repeated `multiplyExact` - or `overflow` if it does not fit.",
              "        long base = sc.nextLong();\n"
              "        int exp = sc.nextInt();\n"
              "        long result = 1;\n"
              "        try {\n"
              "            for (int i = 0; i < exp; i++) {\n"
              "                result = Math.multiplyExact(result, base);\n"
              "            }\n"
              "            System.out.println(result);\n"
              "        } catch (ArithmeticException e) {\n"
              "            System.out.println(\"overflow\");\n"
              "        }",
              [_case(f"{b} {e}", _pow_out32(b, e)) for (b, e) in _POW32],
              ["`Math.pow` returns a double, which cannot hold every long exactly.",
               "`Math.multiplyExact(long, long)` throws on overflow.",
               "2^63 does not fit, but (-2)^63 does: it is exactly `Long.MIN_VALUE`.",
               "3^39 fits; 3^40 would not."]),

        _p32s("j32-pa-nearest", "Rounding to a multiple", "Hard",
              "For each `x m` pair print two numbers: `x` rounded to the NEAREST multiple "
              "of `m` (halves go up, as `Math.round` does), and `x` rounded DOWN to a "
              "multiple of `m`.",
              "        int q = sc.nextInt();\n"
              "        for (int i = 0; i < q; i++) {\n"
              "            int x = sc.nextInt();\n"
              "            int m = sc.nextInt();\n"
              "            long nearest = Math.round((double) x / m) * m;\n"
              "            int down = Math.floorDiv(x, m) * m;\n"
              "            System.out.println(nearest + \" \" + down);\n"
              "        }",
              [_lines32(rows, _nl(*[f"{_round32(x / m) * m} {(x // m) * m}"
                                    for (x, m) in rows]))
               for rows in _NEAR32],
              ["Divide in double, round, then multiply back.",
               "`Math.round` returns a long, so `nearest` is a long.",
               "-25 to the nearest 10 is -20: `Math.round(-2.5)` is -2.",
               "Rounding down is `Math.floorDiv(x, m) * m` - for -17 and 5 that is -20, "
               "where `(x / m) * m` would give -15."]),
    ],
)


# --- Family B - null-safe with Objects ----------------------------------------

_PAIRSB32 = (
    [("ada", "ada"), ("-", "ada"), ("-", "-")],
    [("bo", "cy")],
    [("x", "x"), ("y", "y"), ("-", "z"), ("q", "-")],
    [("-", "-"), ("-", "-")],
    [("pear", "Pear"), ("fig", "fig")],
)

_TOKSB32 = (["ada", "-", "bo"], ["-"], ["x", "y", "z"], ["-", "-", "q", "-"], ["solo", "-"])

_ACCTS32 = ([("ada", "EUR"), ("-", "USD")], [("bo", "-")], [("-", "-"), ("cy", "JPY")],
            [("grace", "GBP")], [("x", "-"), ("-", "y"), ("z", "CHF")])

_HASHB32 = ([("ada", "bo")], [("-", "x")], [("a", "-"), ("-", "-")],
            [("hello", "world")], [("Aa", "BB")])


_ACCT32 = """
class Account {
    private final String owner;
    private final String currency;

    Account(String owner, String currency) {
        this.owner = Objects.requireNonNull(owner, "owner is required");
        this.currency = Objects.requireNonNull(currency, "currency is required");
    }

    String describe() {
        return owner + " " + currency;
    }
}
"""

_ACCT_REGION32 = (
    "        this.owner = Objects.requireNonNull(owner, \"owner is required\");\n"
    "        this.currency = Objects.requireNonNull(currency, \"currency is required\");"
)


def _acct_out32(rows):
    out = []
    for (o, c) in rows:
        if o == "-":
            out.append("owner is required")
        elif c == "-":
            out.append("currency is required")
        else:
            out.append(f"{o} {c}")
    return _nl(*out)


_P32_B = _jfam(
    "p32-objects", "Null-safe with `Objects`",
    "`equals`, `toString`, `nonNull`, `requireNonNull` and `hash` - null handled once, "
    "in the library.",
    """
Each of these replaces a null check you would otherwise write by hand:

```java
Objects.equals(a, b)                   // a == null ? b == null : a.equals(b)
Objects.toString(x, "?")               // x == null ? "?" : x.toString()
Objects::nonNull                       // x -> x != null, as a Predicate
Objects.requireNonNull(x, "x is required")   // throw here, with this message
Objects.hash(a, b)                     // 31 * (31 + h(a)) + h(b), null = 0
```

Every drill reads tokens where `-` stands for null, through a small `read`
helper, so null really does reach the code being tested.
""",
    [
        _p32m("j32-pb-count", "How many pairs match", "Intro",
              "Count the pairs whose two tokens are equal (`-` is null, and two nulls "
              "count as equal). Write `countEqual`.",
              _NULLREAD32 + "\n\n"
              "    static int countEqual(String[] left, String[] right) {\n"
              "        int count = 0;\n"
              "        for (int i = 0; i < left.length; i++) {\n"
              "            if (Objects.equals(left[i], right[i])) {\n"
              "                count++;\n"
              "            }\n"
              "        }\n"
              "        return count;\n"
              "    }",
              "        int n = sc.nextInt();\n"
              "        String[] left = new String[n];\n"
              "        String[] right = new String[n];\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            left[i] = read(sc);\n"
              "            right[i] = read(sc);\n"
              "        }\n"
              "        System.out.println(countEqual(left, right));",
              [_pairs32(p, str(sum(1 for (a, b) in p if _nv32(a) == _nv32(b))))
               for p in _PAIRSB32],
              ["`left[i].equals(right[i])` throws when the left one is null.",
               "`Objects.equals` is null-safe on both sides.",
               "`pear` and `Pear` are different Strings - equals is case-sensitive.",
               "`read` is part of the region: it turns `-` into null."]),

        _p32s("j32-pb-default", "Placeholders in a row", "Easy",
              "Print all the tokens on one line separated by commas, showing `?` for each "
              "null (`-`).",
              "        int n = sc.nextInt();\n"
              "        List<String> shown = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String token = sc.next();\n"
              "            String value = token.equals(\"-\") ? null : token;\n"
              "            shown.add(Objects.toString(value, \"?\"));\n"
              "        }\n"
              "        System.out.println(String.join(\",\", shown));",
              [_toks32(ts, ",".join("?" if t == "-" else t for t in ts)) for ts in _TOKSB32],
              ["Convert `-` to a real null first, then handle the null.",
               "`Objects.toString(value, \"?\")` gives the default for null.",
               "`String.join(\",\", list)` from module 7 builds the line."]),

        _p32s("j32-pb-nonnull", "Counting what is there", "Easy",
              "Read the tokens into a list (with nulls for `-`) and print how many are "
              "non-null, using a stream and a method reference from `Objects`.",
              "        int n = sc.nextInt();\n"
              "        List<String> values = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String token = sc.next();\n"
              "            values.add(token.equals(\"-\") ? null : token);\n"
              "        }\n"
              "        System.out.println(values.stream().filter(Objects::nonNull).count());\n"
              "        System.out.println(values.size());",
              [_toks32(ts, _nl(sum(1 for t in ts if t != "-"), len(ts))) for ts in _TOKSB32],
              ["An `ArrayList` accepts null elements.",
               "`filter(Objects::nonNull)` keeps the present ones.",
               "`count()` returns a long.",
               "The second line shows the list itself still holds the nulls."]),

        _p32t("j32-pb-message", "Refused, with a reason", "Medium",
              "An `Account` needs both an owner and a currency. Write the constructor's two "
              "lines so a missing one is rejected with the message `owner is required` or "
              "`currency is required`. `main` prints either the account or the message.",
              _ACCT32,
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String o = sc.next();\n"
              "            String c = sc.next();\n"
              "            try {\n"
              "                Account a = new Account(o.equals(\"-\") ? null : o,\n"
              "                                        c.equals(\"-\") ? null : c);\n"
              "                System.out.println(a.describe());\n"
              "            } catch (NullPointerException e) {\n"
              "                System.out.println(e.getMessage());\n"
              "            }\n"
              "        }",
              _ACCT_REGION32,
              [_lines32(rows, _acct_out32(rows)) for rows in _ACCTS32],
              ["`Objects.requireNonNull(x, message)` puts YOUR message on the exception.",
               "Check the owner first - when both are missing, the owner's message wins.",
               "The message is the whole point: it names the field that was missing.",
               "This is the one exception message it is safe to print, because you wrote it."]),

        _p32s("j32-pb-hashes", "`hash` versus `hashCode`", "Hard",
              "For each pair of tokens (`-` is null) print `Objects.hash(a, b)`, then "
              "`Objects.hashCode(a)`, separated by a space.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String x = sc.next();\n"
              "            String y = sc.next();\n"
              "            String a = x.equals(\"-\") ? null : x;\n"
              "            String b = y.equals(\"-\") ? null : y;\n"
              "            System.out.println(Objects.hash(a, b) + \" \" + Objects.hashCode(a));\n"
              "        }",
              [_lines32(rows, _nl(*[f"{_ohash32(_nv32(a), _nv32(b))} "
                                    f"{0 if _nv32(a) is None else _jhash32(a)}"
                                    for (a, b) in rows]))
               for rows in _HASHB32],
              ["`Objects.hash(a, b)` is `31 * (31 * 1 + h(a)) + h(b)`, with null as 0.",
               "`Objects.hashCode(a)` is just `a.hashCode()`, or 0 for null.",
               "Both are null-safe; neither throws.",
               "`\"Aa\"` and `\"BB\"` have the SAME String hash (2112) - a real collision, "
               "which is why equal hashes never prove equality."]),
    ],
)


# --- Family C - seeded randomness ----------------------------------------------

_COINS32 = ((42, 8), (7, 5), (2024, 10), (1, 3), (99, 6))
_SUMSC32 = ((42, 3), (7, 10), (2024, 1), (1, 6), (99, 4))
_PICKS32 = ((42, ["ada", "bo", "cy", "di", "ed"], 2), (7, ["x", "y", "z"], 3),
            (2024, ["pear", "fig", "plum", "kiwi"], 1), (1, ["a", "b", "c", "d", "e", "f"], 4),
            (99, ["solo"], 1))
_WALKS32 = ((42, 10), (7, 5), (2024, 20), (1, 1), (99, 15))
_FY32 = ((42, [1, 2, 3, 4, 5]), (7, [10, 20, 30]), (2024, [5, 4, 3, 2, 1, 0]),
         (1, [9, 8]), (99, [3, 1, 4, 1, 5, 9, 2]))


def _coins_out32(seed, n):
    r = _JRandom32(seed)
    flips = ["H" if r.next_boolean() else "T" for _ in range(n)]
    return _nl("".join(flips), flips.count("H"))


def _walk_out32(seed, n):
    r = _JRandom32(seed)
    pos = best = 0
    for _ in range(n):
        pos += 1 if r.next_boolean() else -1
        best = max(best, pos)
    return _nl(pos, best)


def _pick_out32(seed, ws, k):
    return _jarr(_jshuffle32(ws, _JRandom32(seed))[:k])


_P32_C = _jfam(
    "p32-random", "Seeded randomness",
    "One generator, created once, from a seed - so every run is the same run.",
    """
```java
Random rnd = new Random(seed);   // once, before any loop
rnd.nextInt(6) + 1               // a die
rnd.nextBoolean()                // a coin
Collections.shuffle(list, rnd);  // a reproducible shuffle
```

The judge can check these programs only because a seeded `Random` is
deterministic: its algorithm is part of the Java specification. The same seed
gives the same numbers on every machine - which is exactly what you want from a
simulation you need to debug.
""",
    [
        _p32s("j32-pc-coin", "Heads or tails", "Intro",
              "Read a seed and a count. Flip a coin that many times with `nextBoolean` "
              "(true is heads), print the flips as a string of `H` and `T`, then the "
              "number of heads.",
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        Random rnd = new Random(seed);\n"
              "        StringBuilder flips = new StringBuilder();\n"
              "        int heads = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            if (rnd.nextBoolean()) {\n"
              "                flips.append('H');\n"
              "                heads++;\n"
              "            } else {\n"
              "                flips.append('T');\n"
              "            }\n"
              "        }\n"
              "        System.out.println(flips);\n"
              "        System.out.println(heads);",
              [_seedcase32(s, n, _coins_out32(s, n)) for (s, n) in _COINS32],
              ["Create the `Random` once, above the loop.",
               "`nextBoolean()` is the coin.",
               "Build the string with a `StringBuilder`."]),

        _p32s("j32-pc-sum", "Total of the dice", "Easy",
              "Read a seed and a count, roll that many six-sided dice from one generator, "
              "and print their total.",
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        Random rnd = new Random(seed);\n"
              "        int total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            total += rnd.nextInt(6) + 1;\n"
              "        }\n"
              "        System.out.println(total);",
              [_seedcase32(s, n, sum(_dice32(s, n))) for (s, n) in _SUMSC32],
              ["`rnd.nextInt(6) + 1` is one die.",
               "One generator for all the rolls.",
               "The smallest possible total is n, the largest 6n."]),

        _p32s("j32-pc-pick", "Pick k without repeats", "Medium",
              "Read a seed, a list of words and `k`. Choose `k` distinct words at random by "
              "shuffling a copy of the list with the seed and taking the first `k`. Print "
              "them as a list.",
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        List<String> words = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            words.add(sc.next());\n"
              "        }\n"
              "        int k = sc.nextInt();\n"
              "        List<String> copy = new ArrayList<>(words);\n"
              "        Collections.shuffle(copy, new Random(seed));\n"
              "        System.out.println(copy.subList(0, k));",
              [_case(f"{s}\n{len(ws)}\n{' '.join(ws)}\n{k}", _pick_out32(s, ws, k))
               for (s, ws, k) in _PICKS32],
              ["Picking k times with `nextInt(n)` could pick the same word twice.",
               "Shuffle, then take a prefix: every k-subset is equally likely.",
               "`subList(0, k)` is a view of the first k elements.",
               "Shuffle a COPY so the caller's list keeps its order."]),

        _p32s("j32-pc-walk", "A random walk", "Medium",
              "Start at 0. On each of `n` steps move +1 if `nextBoolean()` is true and -1 "
              "otherwise. Print the final position, then the highest position ever reached "
              "(the start counts, so it is at least 0).",
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        Random rnd = new Random(seed);\n"
              "        int pos = 0;\n"
              "        int best = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            pos += rnd.nextBoolean() ? 1 : -1;\n"
              "            best = Math.max(best, pos);\n"
              "        }\n"
              "        System.out.println(pos);\n"
              "        System.out.println(best);",
              [_seedcase32(s, n, _walk_out32(s, n)) for (s, n) in _WALKS32],
              ["One `nextBoolean()` call per step - calling it twice would consume two "
               "values and change every later step.",
               "Track the maximum as you go with `Math.max`.",
               "`best` starts at 0 because the walk starts at 0."]),

        _p32m("j32-pc-fisher", "Fisher-Yates by hand", "Hard",
              "Write `shuffle(int[] a, Random rnd)`: walk from the last index down to 1, "
              "swapping each position with a random index at or before it. Done right, "
              "it matches `Collections.shuffle` with the same seed exactly - `main` checks.",
              "    static void shuffle(int[] a, Random rnd) {\n"
              "        for (int i = a.length - 1; i > 0; i--) {\n"
              "            int j = rnd.nextInt(i + 1);\n"
              "            int tmp = a[i];\n"
              "            a[i] = a[j];\n"
              "            a[j] = tmp;\n"
              "        }\n"
              "    }",
              "        long seed = sc.nextLong();\n"
              "        int n = sc.nextInt();\n"
              "        int[] a = new int[n];\n"
              "        List<Integer> list = new ArrayList<>();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            a[i] = sc.nextInt();\n"
              "            list.add(a[i]);\n"
              "        }\n"
              "        shuffle(a, new Random(seed));\n"
              "        Collections.shuffle(list, new Random(seed));\n"
              "        System.out.println(Arrays.toString(a));\n"
              "        System.out.println(list);",
              [_case(f"{s}\n{len(xs)}\n{_sp(xs)}",
                     _nl(_jarr(_jshuffle32(xs, _JRandom32(s))),
                         _jarr(_jshuffle32(xs, _JRandom32(s)))))
               for (s, xs) in _FY32],
              ["Position `i` may swap with any index `0..i` - including itself.",
               "That is `rnd.nextInt(i + 1)`.",
               "Walking DOWN from the end is what `Collections.shuffle` does too, which "
               "is why the two agree draw for draw.",
               "Using `nextInt(a.length)` for every position looks random and is biased.",
               "Stop at 1: position 0 has only itself to swap with."]),
    ],
)


# --- Family D - LocalDate arithmetic --------------------------------------------

_WEEKDAYS32 = (["2024-03-03"], ["2000-01-01", "1999-12-31"], ["2024-02-29", "2023-02-28"],
               ["1969-07-20"], ["2038-01-19", "2024-12-25"])
_YEARS32 = ([2024, 2023], [1900], [2000, 2100], [1996, 1997, 1998], [2400])
_COUNT32 = (("2024-01-01", "2024-01-11"), ("2024-03-03", "2024-03-03"),
            ("2024-12-25", "2024-12-20"), ("2023-02-28", "2023-03-01"),
            ("2024-02-28", "2024-03-01"))
_SPANS32 = (("2024-03-04", "2024-03-11"), ("2024-03-09", "2024-03-11"),
            ("2024-02-26", "2024-03-25"), ("2024-03-03", "2024-03-03"),
            ("2023-12-29", "2024-01-02"))
_AGES32 = (("1990-05-15", "2024-03-03"), ("2000-02-29", "2023-03-01"),
           ("2000-02-29", "2024-02-28"), ("2010-03-03", "2024-03-03"),
           ("1985-12-31", "2024-01-01"))


def _countdown32(a, b):
    n = (_d32(b) - _d32(a)).days
    if n == 0:
        return "today"
    return f"in {n} days" if n > 0 else f"{-n} days ago"


def _workdays32(a, b):
    d, e, n = _d32(a), _d32(b), 0
    while d < e:
        if d.weekday() < 5:
            n += 1
        d += _dt32.timedelta(days=1)
    return n


def _with_year32(d, y):
    """`LocalDate.withYear(y)`: Feb 29 clamps to Feb 28 in a common year."""
    return _dt32.date(y, d.month, min(d.day, _cal32.monthrange(y, d.month)[1]))


def _age_out32(birth, today):
    b, t = _d32(birth), _d32(today)
    p = _period32(b, t)
    years = int(p[1:p.index("Y")]) if "Y" in p else 0
    nxt = _with_year32(b, t.year)
    if nxt < t:
        nxt = _with_year32(b, t.year + 1)
    return _nl(years, nxt.isoformat(), (nxt - t).days)


_P32_D = _jfam(
    "p32-dates", "`LocalDate` arithmetic",
    "Immutable dates: every change is a new value, and the calendar's rules are "
    "already built in.",
    """
```java
LocalDate d = LocalDate.parse("2024-02-29");
d.getDayOfWeek()            // THURSDAY
d.isLeapYear()              // true
d = d.plusDays(1);          // 2024-03-01 - assign it!
d.withYear(2023)            // 2023-02-28 - clamped, like plusMonths
ChronoUnit.DAYS.between(a, b)   // total days, signed
for (LocalDate x = a; x.isBefore(b); x = x.plusDays(1)) { ... }   // every day in [a, b)
```

Leap years are the Gregorian rule - divisible by 4, except centuries, except
every 400 years - and `LocalDate` applies it for you. 1900 was not a leap year;
2000 was.
""",
    [
        _p32s("j32-pd-weekday", "What day was it?", "Intro",
              "Print the day of the week of each date.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            LocalDate d = LocalDate.parse(sc.next());\n"
              "            System.out.println(d + \" \" + d.getDayOfWeek());\n"
              "        }",
              [_toks32(ds, _nl(*[f"{x} {_dow32(_d32(x))}" for x in ds])) for ds in _WEEKDAYS32],
              ["`LocalDate.parse` reads ISO `yyyy-MM-dd`.",
               "`getDayOfWeek()` returns a `DayOfWeek` enum, which prints in capitals.",
               "Print the date first, then the day."]),

        _p32s("j32-pd-leap", "Leap years", "Easy",
              "For each year print `year leap` or `year common`, then the number of days "
              "in that year's February - asking `LocalDate`, not writing the rule by hand.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int year = sc.nextInt();\n"
              "            LocalDate feb = LocalDate.of(year, 2, 1);\n"
              "            System.out.println(year + \" \" + (feb.isLeapYear() ? \"leap\" : \"common\")\n"
              "                    + \" \" + feb.lengthOfMonth());\n"
              "        }",
              [_toks32([str(y) for y in ys],
                       _nl(*[f"{y} {'leap' if _cal32.isleap(y) else 'common'} "
                             f"{29 if _cal32.isleap(y) else 28}" for y in ys]))
               for ys in _YEARS32],
              ["`LocalDate.of(year, 2, 1)` is any date in that February.",
               "`isLeapYear()` and `lengthOfMonth()` answer both questions.",
               "1900 and 2100 are common; 2000 and 2400 are leap - the century rule."]),

        _p32s("j32-pd-countdown", "Countdown", "Easy",
              "Read today's date and an event's date. Print `today`, `in N days`, or "
              "`N days ago`.",
              "        LocalDate today = LocalDate.parse(sc.next());\n"
              "        LocalDate event = LocalDate.parse(sc.next());\n"
              "        long n = ChronoUnit.DAYS.between(today, event);\n"
              "        if (n == 0) {\n"
              "            System.out.println(\"today\");\n"
              "        } else if (n > 0) {\n"
              "            System.out.println(\"in \" + n + \" days\");\n"
              "        } else {\n"
              "            System.out.println((-n) + \" days ago\");\n"
              "        }",
              [_case(f"{a}\n{b}", _countdown32(a, b)) for (a, b) in _COUNT32],
              ["`ChronoUnit.DAYS.between(today, event)` is negative for a past event.",
               "It returns a `long`.",
               "Across the end of February, the leap day is counted automatically."]),

        _p32s("j32-pd-workdays", "Working days", "Medium",
              "Count the weekdays (Monday to Friday) from the first date INCLUSIVE to the "
              "second EXCLUSIVE, by walking day by day.",
              "        LocalDate from = LocalDate.parse(sc.next());\n"
              "        LocalDate to = LocalDate.parse(sc.next());\n"
              "        int count = 0;\n"
              "        for (LocalDate d = from; d.isBefore(to); d = d.plusDays(1)) {\n"
              "            DayOfWeek w = d.getDayOfWeek();\n"
              "            if (w != DayOfWeek.SATURDAY && w != DayOfWeek.SUNDAY) {\n"
              "                count++;\n"
              "            }\n"
              "        }\n"
              "        System.out.println(count);",
              [_case(f"{a}\n{b}", _workdays32(a, b)) for (a, b) in _SPANS32],
              ["A `for` loop works on dates too: `d = d.plusDays(1)` is the step.",
               "`isBefore(to)` makes the end exclusive.",
               "`DayOfWeek` is an enum, so compare with `==`.",
               "A Monday-to-Monday week has exactly five working days."]),

        _p32s("j32-pd-birthday", "Age and the next birthday", "Hard",
              "Read a birth date and today's date. Print the age in whole years, the date "
              "of the next birthday (today counts), and how many days away it is. A 29 "
              "February birthday falls on 28 February in a common year.",
              "        LocalDate birth = LocalDate.parse(sc.next());\n"
              "        LocalDate today = LocalDate.parse(sc.next());\n"
              "        System.out.println(Period.between(birth, today).getYears());\n"
              "        LocalDate next = birth.withYear(today.getYear());\n"
              "        if (next.isBefore(today)) {\n"
              "            next = birth.withYear(today.getYear() + 1);\n"
              "        }\n"
              "        System.out.println(next);\n"
              "        System.out.println(ChronoUnit.DAYS.between(today, next));",
              [_case(f"{b}\n{t}", _age_out32(b, t)) for (b, t) in _AGES32],
              ["`Period.between(birth, today).getYears()` is the age - here the "
               "years PART is exactly what you want.",
               "`withYear` moves a date to another year, clamping 29 February.",
               "If this year's birthday has already passed, use next year's.",
               "A birthday today is zero days away, not a year away."]),
    ],
)


# --- Family E - format specifiers -----------------------------------------------

_IDS32 = ([7, 42], [1], [123, 4567], [0, 9999], [10, 100, 1000])
_HEX32 = ([255, 16], [0], [4096, 10], [48879], [1, 2, 3])
_PASS32 = ([(3, 4)], [(1, 3), (2, 3)], [(0, 5)], [(7, 7), (1, 8)], [(5, 16)])
_ITEMS32 = ([("tea", 2, 350)], [("apple", 3, 45), ("bread", 1, 299)],
            [("x", 10, 5)], [("coffee", 1, 1005), ("milk", 2, 99), ("jam", 1, 450)],
            [("candles", 12, 125)])
_SHIFTS32 = ([("09:15", "17:45")], [("08:00", "12:00"), ("13:00", "17:30")],
             [("22:00", "23:59")], [("00:00", "00:01"), ("10:10", "10:10")],
             [("07:45", "16:20"), ("09:00", "18:15"), ("12:30", "13:00")])


def _receipt32(rows):
    lines, total = [], 0
    for (name, qty, cents) in rows:
        cost = qty * cents
        total += cost
        lines.append(f"{name:<10} x{qty:<3}{_f32(cost / 100.0):>8}")
    lines.append(f"{'TOTAL':<14}{_f32(total / 100.0):>8}")
    return _nl(*lines)


def _mins32(t):
    h, m = (int(p) for p in t.split(":"))
    return h * 60 + m


def _shifts32(rows):
    lines, total = [], 0
    for (a, b) in rows:
        m = _mins32(b) - _mins32(a)
        total += m
        lines.append(f"{a}-{b} {m // 60}h {m % 60:02d}m")
    lines.append(f"total {total // 60}h {total % 60:02d}m")
    return _nl(*lines)


_P32_E = _jfam(
    "p32-format", "Format specifiers",
    "`%[flags][width][.precision]conversion` - and `Locale.ROOT` every time.",
    """
| spec | `42` | spec | `3.14159` |
|---|---|---|---|
| `%5d` | `   42` | `%.2f` | `3.14` |
| `%-5d` | `42   ` | `%8.3f` | `   3.142` |
| `%05d` | `00042` | `%.1f%%` | `3.1%` |
| `%x` / `%X` | `2a` / `2A` | `%s` / `%-6s` | left / padded text |

The width is a **minimum**: a longer value is never cut off, it just pushes the
rest of the line along. And every call in this family passes `Locale.ROOT`,
because a program's output is data.
""",
    [
        _p32s("j32-pe-ids", "Zero-padded IDs", "Intro",
              "Print each number as a four-digit ID, zero-padded: `ID-0007`.",
              _RD_ARR
              + "        for (int x : a) {\n"
                "            System.out.println(String.format(Locale.ROOT, \"ID-%04d\", x));\n"
                "        }",
              [_acase(xs, _nl(*[f"ID-{x:04d}" for x in xs])) for xs in _IDS32],
              ["`%04d`: the `0` flag pads with zeros, `4` is the width.",
               "Numbers wider than 4 are printed in full.",
               "Pass `Locale.ROOT` first."]),

        _p32s("j32-pe-hex", "Decimal and hex", "Easy",
              "Print each number as `n = 0xhex = 0XHEX` - lower-case hex, then upper-case.",
              _RD_ARR
              + "        for (int x : a) {\n"
                "            System.out.println(String.format(Locale.ROOT, \"%d = 0x%x = 0X%X\", x, x, x));\n"
                "        }",
              [_acase(xs, _nl(*[f"{x} = 0x{x:x} = 0X{x:X}" for x in xs])) for xs in _HEX32],
              ["`%x` is lower-case hexadecimal, `%X` upper-case.",
               "The same argument is passed three times - one per specifier.",
               "48879 is `0xbeef`."]),

        _p32s("j32-pe-percent", "Pass rates", "Easy",
              "Each line is `passed total`. Print the pass rate as a percentage with one "
              "decimal place and a `%` sign, e.g. `75.0%`.",
              "        int n = sc.nextInt();\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            int passed = sc.nextInt();\n"
              "            int total = sc.nextInt();\n"
              "            double rate = 100.0 * passed / total;\n"
              "            System.out.println(String.format(Locale.ROOT, \"%.1f%%\", rate));\n"
              "        }",
              [_lines32(rows, _nl(*[_f32(100.0 * p / t, 1) + "%" for (p, t) in rows]))
               for rows in _PASS32],
              ["`100.0 * passed / total` divides in double - `passed / total` alone would "
               "be integer division.",
               "`%.1f` is one decimal place.",
               "A literal percent sign in a format string is written `%%`."]),

        _p32s("j32-pe-receipt", "A receipt", "Medium",
              "Each item is `name quantity priceInCents`. Print one line per item as "
              "`%-10s x%-3d%8.2f` (name, quantity, line cost in currency units), then a "
              "total line `%-14s%8.2f` with the label `TOTAL`.",
              "        int n = sc.nextInt();\n"
              "        long total = 0;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            String name = sc.next();\n"
              "            int qty = sc.nextInt();\n"
              "            int cents = sc.nextInt();\n"
              "            long cost = (long) qty * cents;\n"
              "            total += cost;\n"
              "            System.out.println(String.format(Locale.ROOT, \"%-10s x%-3d%8.2f\",\n"
              "                    name, qty, cost / 100.0));\n"
              "        }\n"
              "        System.out.println(String.format(Locale.ROOT, \"%-14s%8.2f\", \"TOTAL\", total / 100.0));",
              [_lines32(rows, _receipt32(rows)) for rows in _ITEMS32],
              ["Keep money in whole cents while adding up; divide by `100.0` only to print.",
               "`%-10s` left-aligns the name in ten characters.",
               "`%8.2f` right-aligns the cost in eight, with two places.",
               "`x%-3d` puts the quantity after an `x`, left-aligned in three.",
               "The total's label is 14 wide so its number lines up with the others."]),

        _p32s("j32-pe-shifts", "A timesheet", "Hard",
              "Each line is a shift `start end` as `HH:mm` times on the same day. Print "
              "`start-end Hh MMm` for each (minutes zero-padded), then `total Hh MMm`. Use "
              "`LocalTime` and `Duration`.",
              "        int n = sc.nextInt();\n"
              "        Duration total = Duration.ZERO;\n"
              "        for (int i = 0; i < n; i++) {\n"
              "            LocalTime start = LocalTime.parse(sc.next());\n"
              "            LocalTime end = LocalTime.parse(sc.next());\n"
              "            Duration d = Duration.between(start, end);\n"
              "            total = total.plus(d);\n"
              "            System.out.println(String.format(Locale.ROOT, \"%s-%s %dh %02dm\",\n"
              "                    start, end, d.toHours(), d.toMinutes() % 60));\n"
              "        }\n"
              "        System.out.println(String.format(Locale.ROOT, \"total %dh %02dm\",\n"
              "                total.toHours(), total.toMinutes() % 60));",
              [_lines32(rows, _shifts32(rows)) for rows in _SHIFTS32],
              ["`LocalTime.parse(\"09:15\")` reads `HH:mm`, and prints back the same way.",
               "`Duration.between(start, end)` is the length of the shift.",
               "`toHours()` is whole hours; `toMinutes() % 60` the minutes left over.",
               "`Duration` is immutable too: `total = total.plus(d);`",
               "`%02d` zero-pads the minutes to two digits."]),
    ],
)


_PRACTICE[32] = [_P32_A, _P32_B, _P32_C, _P32_D, _P32_E]
