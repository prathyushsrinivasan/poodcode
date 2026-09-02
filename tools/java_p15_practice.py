# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 15 practice - catching exceptions.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[15]`.
#
# Module 15 scope: what an exception is, try/catch, finally, the hierarchy,
# several catch blocks and multi-catch. `throw`, `throws`, custom types and
# try-with-resources are module 16, so nothing here raises one deliberately.
#
# No exercise prints a stack trace or a JDK-generated message other than
# ArithmeticException's "/ by zero", which is stable. Where the identity of an
# exception matters, programs print getClass().getSimpleName().
# ---------------------------------------------------------------------------


_RD_TWO = "        int a = sc.nextInt();\n        int b = sc.nextInt();\n"
_RD_L15 = "        String s = sc.nextLine();\n"
_RD_L15_2 = _RD_L15 + "        String t = sc.nextLine();\n"


def _p15ex(eid, title, difficulty, prompt, body, tests, hints, read=_RD_TWO):
    body = body.rstrip("\n")
    return _jch(eid, title, difficulty, prompt, _jscan(read + body + "\n"),
                body, tests, hints)


def _p15meth(eid, title, difficulty, prompt, helpers, body, tests, hints, read):
    """The blanked region is a METHOD beside a given `main`, as in module 9."""
    helpers = helpers.strip("\n")
    members = (helpers + "\n\n" + _MAIN_SIG + "\n"
               + "        Scanner sc = new Scanner(System.in);\n"
               + read + body.rstrip("\n") + "\n    }")
    return _jch(eid, title, difficulty, prompt, _jcls(members), helpers,
                tests, hints)


def _isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def _p15_line(line):
    """One line of `<int> <int>`: the quotient, or the failing type's name."""
    parts = line.split(" ")
    if not _isint(parts[0]):
        return "NumberFormatException"      # parts[0] is read first
    if len(parts) < 2:
        return "ArrayIndexOutOfBoundsException"
    if not _isint(parts[1]):
        return "NumberFormatException"
    if int(parts[1]) == 0:
        return "ArithmeticException"
    return str(_jdiv(int(parts[0]), int(parts[1])))


def _p15_running(rows):
    """Running total of the quotients, `skip` for any line that fails."""
    total = 0
    out = []
    for line in rows:
        parts = line.split(" ")
        ok = (len(parts) >= 2 and _isint(parts[0]) and _isint(parts[1])
              and int(parts[1]) != 0)
        if ok:
            total += _jdiv(int(parts[0]), int(parts[1]))
            out.append(str(total))
        else:
            out.append("skip")
    out.append("total=" + str(total))
    return _nl(*out)


# --- Family A - the four you meet constantly ---------------------------------

_P15_A = _jfam(
    "p15-common", "The four you meet constantly",
    "Recognise the failure, then catch exactly it.",
    """
Four exceptions account for most of what a beginner Java program throws, and
knowing which one a piece of code can produce is most of the skill:

| Exception | Thrown by |
|---|---|
| `ArithmeticException` | integer division or `%` by zero |
| `ArrayIndexOutOfBoundsException` | an index outside `0 .. length-1` |
| `NumberFormatException` | `Integer.parseInt` on anything non-numeric |
| `NullPointerException` | calling a method on a `null` reference |

The shape is always the same:

```java
try {
    risky();
} catch (TheSpecificType e) {
    // what to do instead
}
```

**Catch the narrowest type that covers what you expect.** Catching
`RuntimeException` around a large block will also swallow a
`NullPointerException` caused by a typo, and report it as though it were an
expected failure. The bug then hides for months.

**Only integer division throws.** `1.0 / 0` is `Infinity`, a perfectly legal
`double`. Every variant here stays with `int` for that reason.

Two things to notice as you work through these:

- **The rest of the `try` block is skipped.** A statement after the failing line
  does not run, which is what lets you write the success path as a sequence.
- **`e` is an ordinary object.** `e.getMessage()` and
  `e.getClass().getSimpleName()` are just method calls.
""",
    [
        _p15ex("j15-pr-divzero", "Divide safely", "Intro",
               "Read two integers and print `a / b`, or `undefined` if `b` is zero. "
               "Catch the exception rather than testing `b`.",
               """
        try {
            System.out.println(a / b);
        } catch (ArithmeticException e) {
            System.out.println("undefined");
        }
""",
               [_case(f"{x} {y}", _jdiv(x, y) if y != 0 else "undefined")
                for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (-7, 2))],
               ["Put the division inside `try { ... }`.",
                "The type raised by integer division by zero is "
                "`ArithmeticException`.",
                "Print `undefined` from the catch block and nothing else.",
                "Integer division truncates toward zero, so `-7 / 2` is `-3`."]),

        _p15ex("j15-pr-modzero", "Remainder by zero too", "Intro",
               "Read two integers and print `a % b`, or `undefined` if that is not "
               "possible.",
               """
        try {
            System.out.println(a % b);
        } catch (ArithmeticException e) {
            System.out.println("undefined");
        }
""",
               [_case(f"{x} {y}",
                      (abs(x) % abs(y)) * (1 if x >= 0 else -1) if y != 0
                      else "undefined")
                for (x, y) in ((7, 3), (7, 0), (-7, 3), (0, 0), (8, 4))],
               ["`%` throws the same exception as `/` when the right side is zero.",
                "So the catch is identical.",
                "Java's `%` takes the sign of the LEFT operand: `-7 % 3` is `-1`, not "
                "`2`.",
                "Case three checks exactly that."]),

        _p15ex("j15-pr-badindex", "Index that may not exist", "Easy",
               "Read an array, then an index. Print the element there, or `no such "
               "index`. Catch rather than checking the bounds.",
               """
        int i = sc.nextInt();
        try {
            System.out.println(a[i]);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("no such index");
        }
""",
               [_akcase(a, i, a[i] if 0 <= i < len(a) else "no such index")
                for (a, i) in (([3, 1, 4], 1), ([3, 1, 4], 5), ([7], 0),
                               ([3, 1, 4], -1), ([3, 1, 4], 3))],
               ["Read the index after the array.",
                "A negative index throws the same exception as one that is too big — "
                "cases four checks it.",
                "An index equal to the length is out of range, since valid indices "
                "stop at `length - 1`.",
                "Catch `ArrayIndexOutOfBoundsException` specifically."],
               read=_RD_ARR),

        _p15ex("j15-pr-parse", "Parse or report", "Easy",
               "Read one line. Print the number doubled, or `not a number`.",
               """
        try {
            System.out.println(Integer.parseInt(s) * 2);
        } catch (NumberFormatException e) {
            System.out.println("not a number");
        }
""",
               [_lcase(w, int(w) * 2 if _isint(w) else "not a number")
                for w in ("21", "abc", "0", "-5", "3.5")],
               ["`Integer.parseInt` throws `NumberFormatException` for anything it "
                "cannot read as an `int`.",
                "That includes decimals — `3.5` is not an `int`.",
                "Do the doubling inside the try, so it is skipped on failure.",
                "An empty or blank line would also throw."],
               read=_RD_L15),

        _p15ex("j15-pr-name-it", "Which one was it?", "Easy",
               "Read two lines, parse both as integers and print the quotient. On any "
               "failure, print the exception's simple class name instead.",
               """
        try {
            int x = Integer.parseInt(s);
            int y = Integer.parseInt(t);
            System.out.println(x / y);
        } catch (RuntimeException e) {
            System.out.println(e.getClass().getSimpleName());
        }
""",
               [_l2case(x, y,
                        (_jdiv(int(x), int(y)) if _isint(x) and _isint(y) and int(y) != 0
                         else ("NumberFormatException" if not (_isint(x) and _isint(y))
                               else "ArithmeticException")))
                for (x, y) in (("6", "3"), ("6", "0"), ("x", "3"),
                               ("9", "y"), ("-9", "3"))],
               ["One catch of the common supertype is enough when you only report "
                "the type.",
                "`RuntimeException` covers both `NumberFormatException` and "
                "`ArithmeticException`.",
                "`e.getClass().getSimpleName()` gives the short name with no package "
                "prefix.",
                "Note the order of failures: a bad first line throws before the "
                "second is even read."],
               read=_RD_L15_2),
    ])


# --- Family B - try, catch, finally ------------------------------------------

_P15_B = _jfam(
    "p15-finally", "try, catch, finally",
    "Which block runs, and in what order.",
    """
```java
try {
    a();            // stops at the first failure
} catch (E e) {
    b();            // only if E was thrown
} finally {
    c();            // ALWAYS
}
d();                // after the whole construct, on both paths
```

**The order, in every case:**

| Situation | Runs |
|---|---|
| No exception | try body → finally → after |
| Caught | try up to the throw → catch → finally → after |
| Not caught | try up to the throw → **finally** → propagates (no "after") |
| `return` in try | try body → **finally** → the method returns |

The third row is the one people get wrong: `finally` runs on the way out even
when nothing catches.

**A statement after the try/catch runs on both paths** — which is the bug the
variants below keep exercising. If something should only happen on success, it
belongs *inside* the try, after the risky line. If it must happen regardless, it
belongs in `finally` (or after, if no exception can escape).

**`try` needs at least one of `catch` or `finally`**, not both. A
`try`/`finally` with no catch is a normal thing to write: *I am not handling
this, but I am cleaning up anyway.*

**Never `return` from `finally`.** It discards whatever the `try` was about to
return — and, worse, any exception in flight.
""",
    [
        _p15ex("j15-pr-order", "Print the path taken", "Easy",
               "Print `start`, then the quotient, then `end` — but on a division "
               "failure print `start`, then `caught`, then `end`. `end` must appear "
               "either way.",
               """
        System.out.println("start");
        try {
            System.out.println(a / b);
        } catch (ArithmeticException e) {
            System.out.println("caught");
        } finally {
            System.out.println("end");
        }
""",
               [_case(f"{x} {y}",
                      _nl("start", _jdiv(x, y), "end") if y != 0
                      else _nl("start", "caught", "end"))
                for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (8, 2))],
               ["`start` is printed before the try, so it always comes first.",
                "The quotient and `caught` are alternatives — exactly one appears.",
                "`end` goes in a `finally`, so it runs on both paths.",
                "It would also work after the whole construct here, since nothing "
                "escapes — but `finally` says the intent."]),

        _p15ex("j15-pr-success-only", "Only on success", "Medium",
               "Print the quotient and then `ok` when the division works, and only "
               "`failed` when it does not. Nothing else may print.",
               """
        try {
            System.out.println(a / b);
            System.out.println("ok");
        } catch (ArithmeticException e) {
            System.out.println("failed");
        }
""",
               [_case(f"{x} {y}",
                      _nl(_jdiv(x, y), "ok") if y != 0 else "failed")
                for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (8, 2))],
               ["`ok` belongs to the success path, so it goes INSIDE the try.",
                "Putting it after the try/catch would print it on the failing path "
                "too.",
                "Putting it in a `finally` would do the same.",
                "When the division throws, the `println(\"ok\")` on the next line "
                "never runs — which is exactly what you want."]),

        _p15ex("j15-pr-cleanup", "Cleanup with no handler", "Medium",
               "Read the two numbers. Compute `a / b` into a variable, using `-1` when "
               "it fails. Print `closed` from a `finally`, then the value.",
               """
        int result;
        try {
            result = a / b;
        } catch (ArithmeticException e) {
            result = -1;
        } finally {
            System.out.println("closed");
        }
        System.out.println(result);
""",
               [_case(f"{x} {y}", _nl("closed", _jdiv(x, y) if y != 0 else -1))
                for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (9, 3))],
               ["Declare `result` BEFORE the try, or it is out of scope afterwards.",
                "Java then insists every path assigns it, so the catch block must "
                "too.",
                "`closed` prints from the finally, which runs before execution leaves "
                "the construct — so it comes first.",
                "The value prints after, from outside."]),

        _p15ex("j15-pr-count-attempts", "Count both outcomes", "Medium",
               "Read `n`, then `n` lines. Print how many parsed, then how many were "
               "attempted, counting attempts in a `finally`.",
               """
        int ok = 0;
        int tried = 0;
        for (int i = 0; i < n; i++) {
            String w = sc.nextLine();
            try {
                Integer.parseInt(w);
                ok++;
            } catch (NumberFormatException e) {
            } finally {
                tried++;
            }
        }
        System.out.println(ok);
        System.out.println(tried);
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      _nl(sum(1 for x in xs if _isint(x)), len(xs)))
                for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                           ["-4", "5", "x"], ["0", "0"])],
               ["All three blocks go inside the loop, so each line is its own "
                "attempt.",
                "`ok++` sits after the parse inside the try, so it only runs on "
                "success.",
                "`tried++` goes in the `finally`, so it counts both outcomes.",
                "An empty catch block is acceptable here because the brief says to "
                "ignore failures."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-nested", "A try inside a try", "Hard",
               "Read two lines. Parse the first; if it fails print `outer`. If it "
               "parses, divide `100` by it inside an inner try, printing `inner` on "
               "division failure and the quotient otherwise. Print `done` last, "
               "whatever happens.",
               """
        try {
            int v = Integer.parseInt(s);
            try {
                System.out.println(100 / v);
            } catch (ArithmeticException e) {
                System.out.println("inner");
            }
        } catch (NumberFormatException e) {
            System.out.println("outer");
        } finally {
            System.out.println("done");
        }
""",
               [_lcase(w, _nl("outer", "done") if not _isint(w)
                       else (_nl("inner", "done") if int(w) == 0
                             else _nl(_jdiv(100, int(w)), "done")))
                for w in ("5", "0", "abc", "-4", "100")],
               ["Two nested try blocks, each catching a different type.",
                "The inner one only exists on the path where the parse succeeded.",
                "The outer `finally` runs on every path, so `done` is always last.",
                "A `finally` attaches to its own `try`, so putting it on the outer "
                "one covers both routes.",
                "Case two divides by zero and takes the inner handler; case three "
                "never reaches the inner try at all."],
               read=_RD_L15),
    ])


# --- Family C - the hierarchy ------------------------------------------------

_P15_C = _jfam(
    "p15-hierarchy", "The hierarchy",
    "Catch order, supertypes, and multi-catch.",
    """
```
Throwable
├── Error                     ← never catch
└── Exception
    ├── RuntimeException      ← unchecked
    │   ├── ArithmeticException
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   └── IllegalArgumentException → NumberFormatException
    └── IOException, ...      ← checked
```

**A catch matches subclasses too.** `catch (RuntimeException e)` catches an
`ArithmeticException`, for the same reason `x instanceof Rect` is true for a
`Square` — it is the subtree rule from module 13.

**Specific first, general after.** The first matching catch wins, so a general
handler above a specific one makes the specific one unreachable — and Java
refuses to compile that rather than letting you write dead code.

```java
} catch (NumberFormatException e) {     // specific
} catch (RuntimeException e) {          // general
```

**Multi-catch** handles several types the same way:

```java
} catch (NumberFormatException | ArithmeticException e) {
```

The alternatives must be **unrelated**. `catch (Exception | RuntimeException e)`
is a compile error, because one already covers the other. Inside the block `e`
is typed as the nearest common supertype and is effectively final.

**Catch narrowly.** The temptation is `catch (Exception e)` around everything;
the cost is that a real bug is reported as an expected failure and nobody
notices for months.
""",
    [
        _p15ex("j15-pr-supertype", "One handler for both", "Easy",
               "Read two lines and print the quotient. Print `bad` for either a parse "
               "failure or a division by zero, using a SINGLE catch of their common "
               "supertype.",
               """
        try {
            int x = Integer.parseInt(s);
            int y = Integer.parseInt(t);
            System.out.println(x / y);
        } catch (RuntimeException e) {
            System.out.println("bad");
        }
""",
               [_l2case(x, y, _jdiv(int(x), int(y))
                        if _isint(x) and _isint(y) and int(y) != 0 else "bad")
                for (x, y) in (("6", "3"), ("6", "0"), ("x", "3"),
                               ("9", "y"), ("-8", "2"))],
               ["Both failures are unchecked, so they share `RuntimeException` as an "
                "ancestor.",
                "Catching the supertype catches every subclass.",
                "One catch block, not two.",
                "This is fine when both get the same treatment; use separate blocks "
                "when they do not."],
               read=_RD_L15_2),

        _p15ex("j15-pr-multicatch", "Two types, one block", "Easy",
               "Same task, but name the two types explicitly in a multi-catch rather "
               "than catching their supertype.",
               """
        try {
            int x = Integer.parseInt(s);
            int y = Integer.parseInt(t);
            System.out.println(x / y);
        } catch (NumberFormatException | ArithmeticException e) {
            System.out.println("bad");
        }
""",
               [_l2case(x, y, _jdiv(int(x), int(y))
                        if _isint(x) and _isint(y) and int(y) != 0 else "bad")
                for (x, y) in (("6", "3"), ("6", "0"), ("x", "3"),
                               ("9", "y"), ("-8", "2"))],
               ["Separate the two types with a single `|`.",
                "They must be UNRELATED — these two are siblings, so it is legal.",
                "`catch (NumberFormatException | ArithmeticException e)`",
                "This is narrower than catching `RuntimeException`, so a "
                "NullPointerException from a typo would still escape and be visible. "
                "That is the advantage."],
               read=_RD_L15_2),

        _p15ex("j15-pr-two-blocks", "Report them differently", "Medium",
               "Same input. Print the quotient on success, `parse` for a bad number, "
               "and `math` for a division by zero — with the catch blocks in the only "
               "order that compiles.",
               """
        try {
            int x = Integer.parseInt(s);
            int y = Integer.parseInt(t);
            System.out.println(x / y);
        } catch (NumberFormatException e) {
            System.out.println("parse");
        } catch (ArithmeticException e) {
            System.out.println("math");
        }
""",
               [_l2case(x, y, _jdiv(int(x), int(y))
                        if _isint(x) and _isint(y) and int(y) != 0
                        else ("parse" if not (_isint(x) and _isint(y)) else "math"))
                for (x, y) in (("6", "3"), ("6", "0"), ("x", "3"),
                               ("9", "y"), ("-8", "2"))],
               ["Two catch blocks on the same try, one per type.",
                "These two are siblings, so neither hides the other and either order "
                "compiles — but list them in the order you would read them.",
                "The first matching block wins.",
                "A bad first line throws before the second is read, so case three "
                "reports `parse`."],
               read=_RD_L15_2),

        _p15ex("j15-pr-specific-first", "Specific before general", "Medium",
               "Same input. Print `parse` for a bad number and `other` for any other "
               "unchecked failure — which requires the specific handler first.",
               """
        try {
            int x = Integer.parseInt(s);
            int y = Integer.parseInt(t);
            System.out.println(x / y);
        } catch (NumberFormatException e) {
            System.out.println("parse");
        } catch (RuntimeException e) {
            System.out.println("other");
        }
""",
               [_l2case(x, y, _jdiv(int(x), int(y))
                        if _isint(x) and _isint(y) and int(y) != 0
                        else ("parse" if not (_isint(x) and _isint(y)) else "other"))
                for (x, y) in (("6", "3"), ("6", "0"), ("x", "3"),
                               ("9", "y"), ("-8", "2"))],
               ["`NumberFormatException` is a `RuntimeException`, so the general "
                "handler would swallow it if written first.",
                "Java rejects an unreachable catch block at compile time, so getting "
                "the order wrong will not even build.",
                "Specific first, general after.",
                "Division by zero falls through to the general handler and prints "
                "`other`."],
               read=_RD_L15_2),

        _p15ex("j15-pr-narrow", "Do not swallow the bug", "Hard",
               "Read two lines. Parse both and print `100 / (x - y)`. Catch ONLY "
               "`ArithmeticException`, printing `math`, so that a parse failure is left "
               "to escape rather than being silently reported.",
               """
        int x = Integer.parseInt(s);
        int y = Integer.parseInt(t);
        try {
            System.out.println(100 / (x - y));
        } catch (ArithmeticException e) {
            System.out.println("math");
        }
""",
               [_l2case(str(x), str(y), _jdiv(100, x - y) if x != y else "math")
                for (x, y) in ((5, 3), (4, 4), (10, 0), (-5, -5), (0, 4))],
               ["Do the parsing OUTSIDE the try, so a bad number is not caught here.",
                "Only the arithmetic is inside, and only `ArithmeticException` is "
                "caught.",
                "That is what 'catch narrowly' means in practice: the try block "
                "covers exactly the failure you are prepared for.",
                "`x - y` of zero is the only failure this program handles.",
                "Every test case parses successfully, so the escape path is never "
                "exercised — but the narrowness is the point."],
               read=_RD_L15_2),
    ])


# --- Family D - recovering ---------------------------------------------------

_P15_D = _jfam(
    "p15-recover", "Recovering with a default",
    "Try to compute it; fall back if you cannot.",
    """
The most common real use of `catch` is not reporting a failure but **supplying a
value instead**:

```java
int v;
try {
    v = Integer.parseInt(s);
} catch (NumberFormatException e) {
    v = 0;                          // the fallback
}
```

Two compiler rules shape this, and both bite once:

**Scope.** A variable declared inside the `try` does not exist outside it. If you
need it afterwards, declare it before.

**Definite assignment.** Having declared it outside, Java insists it is assigned
on *every* path before it is read — and the catch path is one of them. So the
catch block has to supply the default. That requirement is not a nuisance; it is
the compiler making you decide what happens when things fail.

**Inside a method, `return` from both branches** is often tidier:

```java
static int parseOr(String s, int fallback) {
    try {
        return Integer.parseInt(s);
    } catch (NumberFormatException e) {
        return fallback;
    }
}
```

Both paths return, so there is no definite-assignment question at all.

**Do not catch what you can cheaply test.** `if (b != 0)` is clearer and faster
than catching `ArithmeticException`. Exceptions are for what you cannot check in
advance — parsing arbitrary text is the canonical case, because "is this a valid
int?" is exactly as much work as parsing it.
""",
    [
        _p15ex("j15-pr-default", "Parse with a fallback", "Easy",
               "Read a line and a fallback integer on the next line. Print the parsed "
               "value, or the fallback if the first line is not a number.",
               """
        int fallback = Integer.parseInt(sc.nextLine());
        int v;
        try {
            v = Integer.parseInt(s);
        } catch (NumberFormatException e) {
            v = fallback;
        }
        System.out.println(v);
""",
               [_case(w + "\n" + str(f) + "\n", int(w) if _isint(w) else f)
                for (w, f) in (("21", 0), ("abc", -1), ("0", 9),
                               ("-5", 7), ("x1", 100))],
               ["Declare `v` before the try so it is still in scope for the print.",
                "Java then requires every path to assign it, catch included.",
                "The catch assigns the fallback rather than reporting anything.",
                "Read the fallback first — it is on the second line."],
               read=_RD_L15),

        _p15meth("j15-pr-method", "A method that never fails", "Medium",
                 "Write `static int parseOr(String s, int fallback)` returning the "
                 "parsed value or the fallback. `main` calls it for each of `n` lines "
                 "and prints the total.",
                 """
    static int parseOr(String s, int fallback) {
        try {
            return Integer.parseInt(s);
        } catch (NumberFormatException e) {
            return fallback;
        }
    }
""",
                 """        int total = 0;
        for (int i = 0; i < n; i++) {
            total += parseOr(sc.nextLine(), 0);
        }
        System.out.println(total);""",
                 [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                        sum(int(x) for x in xs if _isint(x)))
                  for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                             ["-4", "5", "x"], ["0", "7"])],
                 ["Returning from both branches avoids the definite-assignment "
                  "question entirely.",
                  "`return` inside the try, `return fallback` inside the catch.",
                  "The method is `static` because `main` is.",
                  "A fallback of `0` means unparseable lines contribute nothing to "
                  "the total."],
                 read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-clamp-or-catch", "Test, do not catch", "Medium",
               "Read two integers. Print `a / b`, or `undefined` when `b` is zero — but "
               "decide with an `if` rather than an exception, because the check is "
               "cheap and reliable.",
               """
        if (b == 0) {
            System.out.println("undefined");
        } else {
            System.out.println(a / b);
        }
""",
               [_case(f"{x} {y}", _jdiv(x, y) if y != 0 else "undefined")
                for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (-7, 2))],
               ["This is the same task as the first variant in family A, solved the "
                "other way.",
                "A single `if` is clearer and faster than setting up a try/catch.",
                "Exceptions are for what you cannot test in advance — this is not "
                "that.",
                "Knowing which tool fits is the point of having both."]),

        _p15ex("j15-pr-first-valid", "The first one that works", "Medium",
               "Read `n` lines. Print the first one that parses as an integer, or "
               "`none` if none do.",
               """
        String answer = "none";
        for (int i = 0; i < n; i++) {
            String w = sc.nextLine();
            if (answer.equals("none")) {
                try {
                    Integer.parseInt(w);
                    answer = w;
                } catch (NumberFormatException e) {
                }
            }
        }
        System.out.println(answer);
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      next((x for x in xs if _isint(x)), "none"))
                for xs in (["a", "2", "3"], ["10"], ["a", "b"],
                           ["x", "y", "-4"], ["0", "1"])],
               ["Every line must still be READ, so do not break out of the loop.",
                "Guard the attempt so only the first success sticks.",
                "The parse result is discarded — you only need to know whether it "
                "threw.",
                "Seeding the answer as `\"none\"` makes the no-match case need no "
                "special handling."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-sum-valid", "Add up what you can", "Easy",
               "Read `n` lines and print the total of the ones that parse, ignoring the "
               "rest.",
               """
        int total = 0;
        for (int i = 0; i < n; i++) {
            try {
                total += Integer.parseInt(sc.nextLine());
            } catch (NumberFormatException e) {
            }
        }
        System.out.println(total);
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      sum(int(x) for x in xs if _isint(x)))
                for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                           ["-4", "5", "x"], ["0", "0", "0"])],
               ["The try goes INSIDE the loop, around one line's parse.",
                "Around the whole loop instead, the first bad line would abandon "
                "every remaining one.",
                "`total +=` only happens when the parse succeeded, because the throw "
                "skips it.",
                "An all-bad input leaves the total at `0`."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),
    ])


# --- Family E - surviving a loop ---------------------------------------------

_P15_E = _jfam(
    "p15-loops", "Loops that survive failure",
    "Where the try goes decides how much you lose.",
    """
The single most consequential decision when catching inside a loop is **where
the `try` starts**:

```java
try {
    for (String s : lines) process(s);      // ONE failure abandons the rest
} catch (E e) { ... }

for (String s : lines) {
    try { process(s); }                     // each line stands alone
    catch (E e) { ... }
}
```

Both compile. The first stops at the first bad line; the second processes all of
them. Which you want depends entirely on the problem — a batch import usually
wants the second, a transaction usually wants the first — but it must be a
decision rather than an accident.

**The per-iteration form is the more common one**, and it has a natural shape:

```java
for (...) {
    try {
        // the risky work
        ok++;                    // only on success
    } catch (E e) {
        failed++;                // only on failure
    } finally {
        attempted++;             // always
    }
}
```

Those three counters answer three different questions, and putting each
increment in the right block is most of the exercise.

**Read every line whatever happens.** If the input says there are `n` lines,
your loop must consume `n` lines — including the bad ones. Skipping a read on
the failure path leaves the scanner out of step and every subsequent line is
misinterpreted, which looks like a completely unrelated bug.
""",
    [
        _p15ex("j15-pr-per-line", "One failure must not stop the rest", "Medium",
               "Read `n` lines. For each, print the number doubled, or `skip` if it "
               "does not parse.",
               """
        for (int i = 0; i < n; i++) {
            String w = sc.nextLine();
            try {
                System.out.println(Integer.parseInt(w) * 2);
            } catch (NumberFormatException e) {
                System.out.println("skip");
            }
        }
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      _nl(*[(int(x) * 2 if _isint(x) else "skip") for x in xs]))
                for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                           ["-4", "5", "x"], ["0", "7"])],
               ["The try goes inside the loop, around one line's work.",
                "The read happens before the try, so every line is consumed whatever "
                "happens.",
                "Exactly one line of output per input line.",
                "Around the whole loop instead, case one would print `2` and then "
                "stop."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-three-counters", "Three counters", "Medium",
               "Read `n` lines. Print how many parsed, how many failed, and how many "
               "were attempted — on three lines, using try, catch and finally "
               "respectively.",
               """
        int ok = 0;
        int failed = 0;
        int tried = 0;
        for (int i = 0; i < n; i++) {
            String w = sc.nextLine();
            try {
                Integer.parseInt(w);
                ok++;
            } catch (NumberFormatException e) {
                failed++;
            } finally {
                tried++;
            }
        }
        System.out.println(ok);
        System.out.println(failed);
        System.out.println(tried);
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      _nl(sum(1 for x in xs if _isint(x)),
                          sum(1 for x in xs if not _isint(x)), len(xs)))
                for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                           ["-4", "5", "x"], ["0", "0"])],
               ["Each counter belongs in a different block.",
                "`ok++` after the parse inside the try; `failed++` in the catch; "
                "`tried++` in the finally.",
                "The third is always the sum of the first two here, which is a good "
                "check that you put them in the right places.",
                "All three are declared before the loop."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-stop-first", "Stop at the first bad one", "Medium",
               "Read `n` lines. Print each number doubled, but STOP at the first line "
               "that does not parse and print `aborted` — putting the try around the "
               "whole loop.",
               """
        try {
            for (int i = 0; i < n; i++) {
                System.out.println(Integer.parseInt(sc.nextLine()) * 2);
            }
        } catch (NumberFormatException e) {
            System.out.println("aborted");
        }
""",
               [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                      _nl(*([int(x) * 2 for x in
                             xs[:next((i for (i, x) in enumerate(xs)
                                       if not _isint(x)), len(xs))]]
                            + (["aborted"] if any(not _isint(x) for x in xs) else []))))
                for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                           ["-4", "5", "x"], ["0", "7"])],
               ["This is the OTHER placement: the try wraps the entire loop.",
                "The first failure jumps straight out, so no later line is even "
                "read.",
                "Case one prints `2`, then `aborted`, and never reaches the `3`.",
                "An all-good input prints every value and no `aborted` at all.",
                "Neither placement is right in general — it depends on whether "
                "partial results are useful."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-report-each", "Say what went wrong", "Medium",
               "Read `n` lines, each meant to be two integers separated by a space. "
               "Print the quotient, or the simple class name of whatever failed.",
               """
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            try {
                String[] parts = line.split(" ");
                int x = Integer.parseInt(parts[0]);
                int y = Integer.parseInt(parts[1]);
                System.out.println(x / y);
            } catch (RuntimeException e) {
                System.out.println(e.getClass().getSimpleName());
            }
        }
""",
               [_case("\n".join([str(len(rows))] + list(rows)) + "\n",
                      _nl(*[_p15_line(r) for r in rows]))
                for rows in (["6 3", "6 0", "x 3"],
                             ["10 2"],
                             ["nope", "4 2"],
                             ["-9 3", "8 y"],
                             ["1 1", "0 0"])],
               ["One try per line, so a bad line does not stop the rest.",
                "A line with only one part makes `parts[1]` throw "
                "`ArrayIndexOutOfBoundsException` — catching `RuntimeException` covers "
                "that as well as the other two.",
                "Case three's first line is a single word and must report the array "
                "exception.",
                "`e.getClass().getSimpleName()` prints the type without its package."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),

        _p15ex("j15-pr-running-total", "Keep a running total", "Hard",
               "Read `n` lines, each meant to be two integers. Print the running total "
               "of the quotients after each successful line, and `skip` for each line "
               "that fails. Finish with `total=<the total>`.",
               """
        int total = 0;
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine();
            try {
                String[] parts = line.split(" ");
                int x = Integer.parseInt(parts[0]);
                int y = Integer.parseInt(parts[1]);
                total += x / y;
                System.out.println(total);
            } catch (RuntimeException e) {
                System.out.println("skip");
            }
        }
        System.out.println("total=" + total);
""",
               [_case("\n".join([str(len(rows))] + list(rows)) + "\n",
                      _p15_running(rows))
                for rows in (["6 3", "6 0", "9 3"],
                             ["10 2"],
                             ["nope", "4 2"],
                             ["-9 3", "8 y"],
                             ["1 1", "2 2"])],
               ["The total must only change on a successful line, so update it "
                "inside the try after the division.",
                "Print the running total in the same place, so a failed line prints "
                "`skip` instead.",
                "A failed line must leave the total untouched — which happens "
                "naturally, because the throw skips the `+=`.",
                "The summary line prints once, after the loop.",
                "Catching `RuntimeException` covers a bad number, a division by zero "
                "and a malformed line all at once."],
               read="        int n = Integer.parseInt(sc.nextLine());\n"),
    ])


_PRACTICE[15] = [_P15_A, _P15_B, _P15_C, _P15_D, _P15_E]
