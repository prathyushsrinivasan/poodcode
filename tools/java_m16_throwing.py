# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 16 - Throwing, checked exceptions, and resources.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Closes Part 5. Module 15 covered catching; this one covers raising, the
# checked/unchecked split that the compiler enforces, writing your own exception
# types, and try-with-resources.
#
# File I/O is Part 9, so try-with-resources is demonstrated with a hand-written
# `AutoCloseable` rather than a FileReader - which is better anyway, because the
# closing order is then visible in the output.
# ---------------------------------------------------------------------------

_M16 = []


def _m16prog(types, members):
    """Top-level types AND a `Main` with helper methods beside `main`.

    `_joop` gives types plus a bare main; `_jcls` gives helpers but no extra
    types. The checked-exception exercise needs both, because a checked
    exception only forces a `throws` clause when it crosses a method boundary -
    thrown and caught inside `main` it compiles perfectly well."""
    return _jp(_IMPORTS + "\n" + types.rstrip("\n")
               + "\n\npublic class Main {\n" + members.rstrip("\n") + "\n}")


# --- 16.1 throw -------------------------------------------------------------

_M16.append(_jlesson(
    "m16-throw", "`throw`",
    "Raising one yourself, and which type to pick.",
    """
Module 12 listed three responses to a bad argument: clamp, reject, or throw. The
third one is now available.

```java
static int sqrtFloor(int n) {
    if (n < 0) {
        throw new IllegalArgumentException("negative: " + n);
    }
    ...
}
```

**`throw` takes an exception object**, so it is almost always paired with `new`.
The statement exits the method immediately — everything module 15 said about
unwinding applies identically, whether the JVM threw it or you did.

**Throw when the call itself is a mistake.** Clamping and rejecting suit a value
that is merely out of range in an expected way. Throwing says *this should never
have been called like this*, and it refuses to continue with a half-sensible
answer. Silently returning `-1` from a method that cannot compute an answer is
how a small bug becomes a mysterious one three layers away.

**The two you will throw most:**

| Type | Meaning |
|---|---|
| `IllegalArgumentException` | this argument is wrong |
| `IllegalStateException` | the object is not in a state where this call makes sense |

Both are unchecked, so no caller is forced to handle them — which is right,
because both indicate a programming error rather than a situation to recover
from.

**Always give it a message.** `throw new IllegalArgumentException()` tells
whoever reads the trace nothing. Include the offending value: the message is the
only thing that reaches the person debugging it at 3am.

**`throw` is a statement, not an expression.** Code after it on the same path is
unreachable and will not compile — which conveniently means a method ending in
`throw` needs no `return` after it.
""",
    warmup=[
        _jq("Which exception says 'the argument you passed is wrong'?",
            ["IllegalArgumentException", "IllegalStateException",
             "ArithmeticException", "NullPointerException"],
            0,
            "`IllegalStateException` is for the object being in the wrong state, which "
            "is a different complaint."),
        _jq("Why does a method whose last statement is `throw` not need a `return`?",
            ["The code after a throw is unreachable, so there is no path that falls off the end",
             "Because throw returns null",
             "It does need one",
             "Because the method must be void"],
            0,
            "Definite-return analysis knows the method cannot complete normally on that "
            "path."),
    ],
    exercises=[
        _je("j16-throw-basic", "Refuse a negative",
            "`square` should reject a negative argument. Replace `____` with the "
            "statement that raises an `IllegalArgumentException` carrying the offending "
            "value as its message.",
            _jcls("    static int square(int n) {\n"
                  "        if (n < 0) {\n"
                  '            throw new IllegalArgumentException("negative: " + n);\n'
                  "        }\n"
                  "        return n * n;\n"
                  "    }\n"
                  "\n"
                  + _MAIN_SIG + "\n"
                  "        Scanner sc = new Scanner(System.in);\n"
                  "        int v = sc.nextInt();\n"
                  "        try {\n"
                  "            System.out.println(square(v));\n"
                  "        } catch (IllegalArgumentException e) {\n"
                  "            System.out.println(e.getMessage());\n"
                  "        }\n"
                  "    }"),
            '            throw new IllegalArgumentException("negative: " + n);',
            [_case("5", 25), _case("-3", "negative: -3"), _case("0", 0),
             _case("-1", "negative: -1"), _case("12", 144)],
            hints=["`throw` needs an object, so pair it with `new`.",
                   "The type for a bad argument is `IllegalArgumentException`.",
                   "Pass the message to its constructor, including the value: "
                   '`"negative: " + n`.',
                   "No `return` is needed after it — that path cannot continue."],
            difficulty="Easy"),

        _je("j16-throw-state", "Refuse in the wrong state",
            "A `Gate` may only be opened when it is closed. Replace `____` with the "
            "exception type that says *the object is not in a state where this call "
            "makes sense*.",
            _joop("class Gate {\n"
                  "    private boolean open;\n"
                  "\n"
                  "    void open() {\n"
                  "        if (open) {\n"
                  '            throw new IllegalStateException("already open");\n'
                  "        }\n"
                  "        open = true;\n"
                  "    }\n"
                  "\n"
                  "    boolean isOpen() {\n"
                  "        return open;\n"
                  "    }\n"
                  "}",
                  "        int k = sc.nextInt();\n"
                  "        Gate g = new Gate();\n"
                  "        try {\n"
                  "            for (int i = 0; i < k; i++) {\n"
                  "                g.open();\n"
                  "            }\n"
                  '            System.out.println("opened " + k);\n'
                  "        } catch (IllegalStateException e) {\n"
                  "            System.out.println(e.getMessage());\n"
                  "        }"),
            "IllegalStateException",
            [_case("1", "opened 1"), _case("2", "already open"),
             _case("0", "opened 0"), _case("3", "already open"),
             _case("5", "already open")],
            hints=["The argument is fine here — `open()` takes none.",
                   "What is wrong is the object's condition at the time of the call.",
                   "`IllegalStateException`",
                   "Opening twice is the caller's mistake, so refusing loudly is "
                   "right."],
            difficulty="Easy"),

        _jfix("j16-throw-silent", "The silent failure",
              "`parsePositive` returns `-1` when it cannot produce an answer, and the "
              "caller has no way to tell that apart from a real result. Change it to "
              "throw an `IllegalArgumentException` with the message "
              "`not positive: <value>` instead, and let `main`'s existing handler "
              "report it.",
              _jcls("    static int parsePositive(int n) {\n"
                    "        if (n <= 0) {\n"
                    "            return -1;\n"
                    "        }\n"
                    "        return n;\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int v = sc.nextInt();\n"
                    "        try {\n"
                    "            System.out.println(parsePositive(v));\n"
                    "        } catch (IllegalArgumentException e) {\n"
                    "            System.out.println(e.getMessage());\n"
                    "        }\n"
                    "    }"),
              _jcls("    static int parsePositive(int n) {\n"
                    "        if (n <= 0) {\n"
                    '            throw new IllegalArgumentException("not positive: " + n);\n'
                    "        }\n"
                    "        return n;\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int v = sc.nextInt();\n"
                    "        try {\n"
                    "            System.out.println(parsePositive(v));\n"
                    "        } catch (IllegalArgumentException e) {\n"
                    "            System.out.println(e.getMessage());\n"
                    "        }\n"
                    "    }"),
              [_case("5", 5), _case("-3", "not positive: -3"),
               _case("0", "not positive: 0"), _case("1", 1),
               _case("-1", "not positive: -1")],
              hints=["`-1` is indistinguishable from a legitimate answer in general, "
                     "which is why sentinel returns cause trouble.",
                     "Replace the `return -1;` with a `throw`.",
                     "The message must be exactly `not positive: ` followed by the "
                     "value.",
                     "`main` already catches it and prints the message — you do not "
                     "change `main` at all."],
              difficulty="Easy"),

        _jch("j16-throw-validate", "Validate then compute", "Medium",
             "Write `static int divide(int a, int b)` which throws an "
             "`IllegalArgumentException` with the message `divide by zero` when `b` is "
             "`0`, and otherwise returns `a / b`. `main` is written and reports the "
             "message.",
             _jcls("    static int divide(int a, int b) {\n"
                   "        if (b == 0) {\n"
                   '            throw new IllegalArgumentException("divide by zero");\n'
                   "        }\n"
                   "        return a / b;\n"
                   "    }\n"
                   "\n"
                   + _MAIN_SIG + "\n"
                   "        Scanner sc = new Scanner(System.in);\n"
                   "        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        try {\n"
                   "            System.out.println(divide(a, b));\n"
                   "        } catch (IllegalArgumentException e) {\n"
                   "            System.out.println(e.getMessage());\n"
                   "        }\n"
                   "    }"),
             "    static int divide(int a, int b) {\n"
             "        if (b == 0) {\n"
             '            throw new IllegalArgumentException("divide by zero");\n'
             "        }\n"
             "        return a / b;\n"
             "    }",
             [_case("6 3", 2), _case("6 0", "divide by zero"),
              _case("-9 3", -3), _case("0 0", "divide by zero"),
              _case("-7 2", -3)],
             hints=["Check the precondition FIRST, then do the work.",
                    "Throwing your own exception here gives a much better message "
                    "than the JVM's `/ by zero`.",
                    "No `return` after the throw, and no `else` needed.",
                    "Integer division truncates toward zero, so `-7 / 2` is `-3`."]),
    ],
    quiz=[
        _jq("When is throwing better than returning a sentinel like -1?",
            ["When the sentinel could be a legitimate result, or when continuing would hide a bug",
             "Always",
             "Never - sentinels are faster",
             "Only in static methods"],
            0,
            "A sentinel silently blends into real data. An exception cannot be ignored "
            "by accident."),
        _jq("What should an exception message contain?",
            ["Enough context to debug it, including the offending value",
             "Nothing - the type is enough",
             "The stack trace",
             "The method name only"],
            0,
            "The message is often the only thing that survives into a log."),
    ],
))


# --- 16.2 checked vs unchecked ----------------------------------------------

_M16.append(_jlesson(
    "m16-checked", "Checked versus unchecked",
    "The one place Java's compiler makes you plan for failure.",
    """
```
Throwable
├── Error                     unchecked
└── Exception                 CHECKED
    └── RuntimeException      unchecked
```

The rule is exactly that shape: **everything under `Exception` is checked,
except the `RuntimeException` subtree.**

**Checked means the compiler forces a decision.** If a method can throw a checked
exception, every caller must either catch it or declare that it too may throw:

```java
static void risky() throws Exception {        // "I might throw this"
    throw new Exception("boom");
}

static void caller() throws Exception {       // choice 1: pass it on
    risky();
}

static void handler() {                       // choice 2: deal with it
    try { risky(); }
    catch (Exception e) { ... }
}
```

Leave out both and you get *unreported exception … must be caught or declared to
be thrown*.

**`throws` is a declaration, not an action.** It appears in the signature and
says what may come out. `throw` is the statement that raises one. The names are
one letter apart and mean entirely different things.

**Which to use, in practice:**

- **Checked** for conditions a caller could plausibly recover from, that are not
  the caller's fault — a file is missing, a network call failed.
- **Unchecked** for programming errors — a null where one should not be, an
  argument that violates a documented precondition.

**The design debate is real.** Checked exceptions force a decision at every
level, which is either disciplined or exhausting depending on who you ask; most
modern Java libraries lean unchecked. Knowing the rule matters more than
picking a side, and being able to say *why* both exist is what an interviewer is
after.

**`main` may declare `throws` too.** `public static void main(String[] args)
throws Exception` is legal and common in small programs — the failure then
terminates the JVM with a trace.
""",
    warmup=[
        _jq("Which of these is CHECKED?",
            ["Exception", "RuntimeException", "IllegalArgumentException",
             "ArithmeticException"],
            0,
            "Everything under Exception is checked except the RuntimeException subtree, "
            "and the other three are all in it."),
        _jq("What is the difference between `throw` and `throws`?",
            ["`throw` raises one; `throws` declares in the signature that one may come out",
             "They are synonyms",
             "`throws` raises several at once",
             "`throw` is for checked exceptions only"],
            0,
            "One is a statement, the other part of the method's contract."),
    ],
    exercises=[
        _je("j16-checked-declare", "Declare what may come out",
            "`risky` throws a checked `Exception`, so its signature must say so. "
            "Replace `____` with the clause that declares it.",
            _jcls("    static int risky(int n) throws Exception {\n"
                  "        if (n < 0) {\n"
                  '            throw new Exception("negative");\n'
                  "        }\n"
                  "        return n * 2;\n"
                  "    }\n"
                  "\n"
                  + _MAIN_SIG + "\n"
                  "        Scanner sc = new Scanner(System.in);\n"
                  "        int v = sc.nextInt();\n"
                  "        try {\n"
                  "            System.out.println(risky(v));\n"
                  "        } catch (Exception e) {\n"
                  "            System.out.println(e.getMessage());\n"
                  "        }\n"
                  "    }"),
            "throws Exception",
            [_case("5", 10), _case("-3", "negative"), _case("0", 0),
             _case("-1", "negative"), _case("21", 42)],
            hints=["`Exception` itself is checked, so the compiler insists the "
                   "signature mentions it.",
                   "The clause goes after the parameter list and before the opening "
                   "brace.",
                   "`throws Exception`",
                   "Note the `s` — `throws` declares, `throw` raises."],
            difficulty="Easy"),

        _je("j16-checked-propagate", "Pass it up instead of handling it",
            "`middle` does not want to handle the failure — it just calls `risky` and "
            "lets it propagate. Replace `____` so `middle` compiles.",
            _jcls("    static int risky(int n) throws Exception {\n"
                  "        if (n < 0) {\n"
                  '            throw new Exception("negative");\n'
                  "        }\n"
                  "        return n * 2;\n"
                  "    }\n"
                  "\n"
                  "    static int middle(int n) throws Exception {\n"
                  "        return risky(n) + 1;\n"
                  "    }\n"
                  "\n"
                  + _MAIN_SIG + "\n"
                  "        Scanner sc = new Scanner(System.in);\n"
                  "        int v = sc.nextInt();\n"
                  "        try {\n"
                  "            System.out.println(middle(v));\n"
                  "        } catch (Exception e) {\n"
                  '            System.out.println("caught " + e.getMessage());\n'
                  "        }\n"
                  "    }"),
            "    static int middle(int n) throws Exception {",
            [_case("5", 11), _case("-3", "caught negative"), _case("0", 1),
             _case("-1", "caught negative"), _case("20", 41)],
            hints=["A caller has two choices: catch it, or declare it. `middle` "
                   "chooses to declare.",
                   "So `middle` needs the same `throws Exception` clause.",
                   "Without it you get *unreported exception ... must be caught or "
                   "declared to be thrown*.",
                   "`main` is the one that finally catches it."],
            difficulty="Medium"),

        _jfix("j16-checked-missing", "The unreported exception",
              "This does not compile: `wrap` calls a method that throws a checked "
              "exception but neither catches nor declares it. Make `wrap` declare it "
              "and let `main`'s handler deal with it.",
              _jcls("    static int risky(int n) throws Exception {\n"
                    "        if (n < 0) {\n"
                    '            throw new Exception("negative");\n'
                    "        }\n"
                    "        return n * 2;\n"
                    "    }\n"
                    "\n"
                    "    static int wrap(int n) {\n"
                    "        return risky(n);\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int v = sc.nextInt();\n"
                    "        try {\n"
                    "            System.out.println(wrap(v));\n"
                    "        } catch (Exception e) {\n"
                    "            System.out.println(e.getMessage());\n"
                    "        }\n"
                    "    }"),
              _jcls("    static int risky(int n) throws Exception {\n"
                    "        if (n < 0) {\n"
                    '            throw new Exception("negative");\n'
                    "        }\n"
                    "        return n * 2;\n"
                    "    }\n"
                    "\n"
                    "    static int wrap(int n) throws Exception {\n"
                    "        return risky(n);\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int v = sc.nextInt();\n"
                    "        try {\n"
                    "            System.out.println(wrap(v));\n"
                    "        } catch (Exception e) {\n"
                    "            System.out.println(e.getMessage());\n"
                    "        }\n"
                    "    }"),
              [_case("5", 10), _case("-3", "negative"), _case("0", 0),
               _case("-1", "negative"), _case("7", 14)],
              hints=["The compiler message is *unreported exception java.lang.Exception; "
                     "must be caught or declared to be thrown*.",
                     "`wrap` has to make one of those two choices.",
                     "Wrapping the call in try/catch would also compile, but the brief "
                     "asks you to declare it.",
                     "Add `throws Exception` to `wrap`'s signature and change nothing "
                     "else."],
              difficulty="Medium"),

        _jch("j16-checked-choose", "Catch here, or pass it on", "Medium",
             "Write `static int safe(int n)` which calls the given `risky(int)` and "
             "returns `0` instead of letting the checked exception escape — so `safe` "
             "itself declares no `throws`. `main` calls it directly with no handler.",
             _jcls("    static int risky(int n) throws Exception {\n"
                   "        if (n < 0) {\n"
                   '            throw new Exception("negative");\n'
                   "        }\n"
                   "        return n * 2;\n"
                   "    }\n"
                   "\n"
                   "    static int safe(int n) {\n"
                   "        try {\n"
                   "            return risky(n);\n"
                   "        } catch (Exception e) {\n"
                   "            return 0;\n"
                   "        }\n"
                   "    }\n"
                   "\n"
                   + _MAIN_SIG + "\n"
                   "        Scanner sc = new Scanner(System.in);\n"
                   "        System.out.println(safe(sc.nextInt()));\n"
                   "    }"),
             "    static int safe(int n) {\n"
             "        try {\n"
             "            return risky(n);\n"
             "        } catch (Exception e) {\n"
             "            return 0;\n"
             "        }\n"
             "    }",
             [_case("5", 10), _case("-3", 0), _case("0", 0),
              _case("-1", 0), _case("21", 42)],
             hints=["`safe` takes the other choice: it handles the exception rather "
                    "than declaring it.",
                    "Because it catches, its signature stays clean — that is what "
                    "lets `main` call it with no try/catch.",
                    "`return` from inside the try, and `return 0;` from the catch.",
                    "Every path returns, which the compiler checks."]),
    ],
    quiz=[
        _jq("A method calls something that throws a checked exception. What are its options?",
            ["Catch it, or declare `throws` for it", "Ignore it",
             "Only catch it", "Only declare it"],
            0,
            "Exactly two, and the compiler will not let you skip both."),
        _jq("Which is the better choice for a violated precondition, like a negative count?",
            ["Unchecked - it is a programming error, not a recoverable situation",
             "Checked, so every caller must handle it",
             "An Error",
             "Return null"],
            0,
            "Checked exceptions are for conditions a caller could reasonably recover "
            "from and did not cause."),
    ],
))


# --- 16.3 custom exceptions -------------------------------------------------

_M16.append(_jlesson(
    "m16-custom", "Your own exception types",
    "A class like any other, with a name that says what went wrong.",
    """
An exception type is an ordinary class that extends an existing one — which is
module 13's inheritance, put to work.

```java
class InsufficientFundsException extends RuntimeException {
    InsufficientFundsException(String message) {
        super(message);
    }
}
```

That is the entire minimum: extend, and pass the message up with `super`.

**Which parent decides checked or unchecked:**

| Extend | Result |
|---|---|
| `RuntimeException` | unchecked — no caller is forced to handle it |
| `Exception` | checked — every caller must catch or declare |

**Why bother, instead of throwing `IllegalArgumentException` everywhere?**
Because the *type* is what a caller catches. A distinct type lets one handler
deal with insufficient funds and a different one deal with a bad account number,
without parsing message strings.

**Carry the data, not just a sentence.** An exception is an object, so it can
hold fields:

```java
class InsufficientFundsException extends RuntimeException {
    private final int shortfall;

    InsufficientFundsException(int shortfall) {
        super("short by " + shortfall);
        this.shortfall = shortfall;
    }

    int getShortfall() { return shortfall; }
}
```

Now the handler can *do* something with the number rather than re-deriving it.

**Naming:** end the class in `Exception`. It is a universal convention, and code
that breaks it reads badly everywhere.

**Do not create one per method.** A custom type earns its place when a caller
would realistically want to catch *that* case specifically. Otherwise
`IllegalArgumentException` with a good message is better than a class nobody
distinguishes.
""",
    warmup=[
        _jq("How do you make a custom exception unchecked?",
            ["Extend RuntimeException", "Extend Exception", "Extend Error",
             "Add the `unchecked` keyword"],
            0,
            "The checked/unchecked split is decided entirely by which part of the "
            "hierarchy you extend."),
        _jq("What does `super(message)` do in an exception's constructor?",
            ["Passes the message to Throwable, so getMessage() returns it",
             "Rethrows the exception",
             "Prints the message",
             "Nothing useful"],
            0,
            "The message field lives on `Throwable`, so the constructor has to hand it "
            "up."),
    ],
    exercises=[
        _je("j16-custom-declare", "Declare your own type",
            "Replace `____` with the declaration of an unchecked exception class named "
            "`TooSmallException`.",
            _joop("class TooSmallException extends RuntimeException {\n"
                  "    TooSmallException(String message) {\n"
                  "        super(message);\n"
                  "    }\n"
                  "}",
                  "        int v = sc.nextInt();\n"
                  "        try {\n"
                  "            if (v < 10) {\n"
                  '                throw new TooSmallException("too small: " + v);\n'
                  "            }\n"
                  "            System.out.println(v);\n"
                  "        } catch (TooSmallException e) {\n"
                  "            System.out.println(e.getMessage());\n"
                  "        }"),
            "class TooSmallException extends RuntimeException {",
            [_case("15", 15), _case("3", "too small: 3"), _case("10", 10),
             _case("0", "too small: 0"), _case("-5", "too small: -5")],
            hints=["An exception type is just a class that extends an existing "
                   "exception.",
                   "Extending `RuntimeException` makes it unchecked, so no caller is "
                   "forced to handle it.",
                   "`class TooSmallException extends RuntimeException {`",
                   "The constructor passes the message up with `super(message)`."],
            difficulty="Easy"),

        _je("j16-custom-super", "Pass the message up",
            "The constructor must hand its message to the parent so `getMessage()` "
            "returns it. Replace `____` with that call.",
            _joop("class BadInputException extends RuntimeException {\n"
                  "    BadInputException(String message) {\n"
                  "        super(message);\n"
                  "    }\n"
                  "}",
                  "        String s = sc.nextLine();\n"
                  "        try {\n"
                  "            if (s.isBlank()) {\n"
                  '                throw new BadInputException("blank input");\n'
                  "            }\n"
                  "            System.out.println(s.length());\n"
                  "        } catch (BadInputException e) {\n"
                  "            System.out.println(e.getMessage());\n"
                  "        }"),
            "        super(message);",
            [_lcase("hello", 5), _lcase(" ", "blank input"), _lcase("a", 1),
             _lcase("   ", "blank input"), _lcase("Java", 4)],
            hints=["The message field belongs to `Throwable`, several levels up.",
                   "The way to set it is the constructor chain.",
                   "`super(message);` — and it must be the first statement.",
                   "Without it `getMessage()` returns `null`."],
            difficulty="Easy"),

        _jfix("j16-custom-checked", "Checked when it should not be",
              "`TooSmallException` extends `Exception`, so it is checked — and `check` "
              "throws it without declaring `throws`, which does not compile. The "
              "exception reports a programming error, so make it unchecked by changing "
              "which class it extends. Do not add a `throws` clause.",
              _m16prog("class TooSmallException extends Exception {\n"
                       "    TooSmallException(String message) {\n"
                       "        super(message);\n"
                       "    }\n"
                       "}",
                       "    static void check(int v) {\n"
                       "        if (v < 10) {\n"
                       '            throw new TooSmallException("too small: " + v);\n'
                       "        }\n"
                       "    }\n"
                       "\n"
                       + _MAIN_SIG + "\n"
                       "        Scanner sc = new Scanner(System.in);\n"
                       "        int v = sc.nextInt();\n"
                       "        try {\n"
                       "            check(v);\n"
                       "            System.out.println(v);\n"
                       "        } catch (TooSmallException e) {\n"
                       "            System.out.println(e.getMessage());\n"
                       "        }\n"
                       "    }"),
              _m16prog("class TooSmallException extends RuntimeException {\n"
                       "    TooSmallException(String message) {\n"
                       "        super(message);\n"
                       "    }\n"
                       "}",
                       "    static void check(int v) {\n"
                       "        if (v < 10) {\n"
                       '            throw new TooSmallException("too small: " + v);\n'
                       "        }\n"
                       "    }\n"
                       "\n"
                       + _MAIN_SIG + "\n"
                       "        Scanner sc = new Scanner(System.in);\n"
                       "        int v = sc.nextInt();\n"
                       "        try {\n"
                       "            check(v);\n"
                       "            System.out.println(v);\n"
                       "        } catch (TooSmallException e) {\n"
                       "            System.out.println(e.getMessage());\n"
                       "        }\n"
                       "    }"),
              [_case("15", 15), _case("3", "too small: 3"), _case("10", 10),
               _case("0", "too small: 0"), _case("-5", "too small: -5")],
              hints=["The error is *unreported exception TooSmallException; must be "
                     "caught or declared to be thrown*, reported on `check`.",
                     "Note that it only appears because the throw crosses a method "
                     "boundary — thrown and caught inside `main` it would have "
                     "compiled.",
                     "Extending `Exception` makes a type checked; extending "
                     "`RuntimeException` makes it unchecked.",
                     "A violated precondition is a programming error, which is the "
                     "unchecked case — so change the `extends` clause.",
                     "Everything else — the constructor, `check`, the throw, the "
                     "catch — stays exactly as it is."],
              difficulty="Medium"),

        _jch("j16-custom-data", "An exception that carries data", "Hard",
             "Write an unchecked `InsufficientFundsException` holding a "
             "`private final int shortfall`, whose constructor sets the message to "
             "`short by <shortfall>` and stores the number, with `int getShortfall()`. "
             "`main` uses it and prints both the message and the shortfall.",
             _joop("class InsufficientFundsException extends RuntimeException {\n"
                   "    private final int shortfall;\n"
                   "\n"
                   "    InsufficientFundsException(int shortfall) {\n"
                   '        super("short by " + shortfall);\n'
                   "        this.shortfall = shortfall;\n"
                   "    }\n"
                   "\n"
                   "    int getShortfall() {\n"
                   "        return shortfall;\n"
                   "    }\n"
                   "}",
                   "        int balance = sc.nextInt();\n"
                   "        int want = sc.nextInt();\n"
                   "        try {\n"
                   "            if (want > balance) {\n"
                   "                throw new InsufficientFundsException(want - balance);\n"
                   "            }\n"
                   "            System.out.println(balance - want);\n"
                   "        } catch (InsufficientFundsException e) {\n"
                   "            System.out.println(e.getMessage());\n"
                   "            System.out.println(e.getShortfall());\n"
                   "        }"),
             "class InsufficientFundsException extends RuntimeException {\n"
             "    private final int shortfall;\n"
             "\n"
             "    InsufficientFundsException(int shortfall) {\n"
             '        super("short by " + shortfall);\n'
             "        this.shortfall = shortfall;\n"
             "    }\n"
             "\n"
             "    int getShortfall() {\n"
             "        return shortfall;\n"
             "    }\n"
             "}",
             [_case("100 30", 70), _case("50 80", _nl("short by 30", 30)),
              _case("10 10", 0), _case("0 5", _nl("short by 5", 5)),
              _case("7 100", _nl("short by 93", 93))],
             hints=["An exception is an ordinary object, so it may have fields, a "
                    "constructor and getters.",
                    "`super(\"short by \" + shortfall);` must be the FIRST statement, "
                    "before assigning the field.",
                    "The field is `private final` — the same encapsulation rules as "
                    "any other class.",
                    "Extending `RuntimeException` keeps it unchecked, so `main` needs "
                    "no `throws`.",
                    "The handler can now use the number, not just the sentence."]),
    ],
    quiz=[
        _jq("Why give a custom exception its own type rather than reusing IllegalArgumentException?",
            ["So a caller can catch that specific case without inspecting message text",
             "It is faster",
             "Because IllegalArgumentException is checked",
             "To avoid writing a message"],
            0,
            "The type is the thing `catch` matches on. Distinguishing by message string "
            "is fragile."),
        _jq("What is the naming convention for an exception class?",
            ["End the name in `Exception`", "Start it with `Ex`",
             "Use all capitals", "There is none"],
            0,
            "Universal in Java, and breaking it makes code read badly at every call "
            "site."),
    ],
))


# --- 16.4 try-with-resources ------------------------------------------------

_M16.append(_jlesson(
    "m16-resources", "try-with-resources",
    "Closing things without a `finally` block.",
    """
Anything that must be released — a file, a socket, a database connection — used
to need this:

```java
Resource r = null;
try {
    r = new Resource();
    r.use();
} finally {
    if (r != null) r.close();       // null check, and close() may itself throw
}
```

**try-with-resources replaces all of it:**

```java
try (Resource r = new Resource()) {
    r.use();
}                                    // close() is called automatically
```

The resource is declared in the parentheses, and Java closes it when the block
ends — normally, by exception, or by `return`.

**The type must implement `AutoCloseable`**, an interface with a single method:

```java
class Resource implements AutoCloseable {
    @Override
    public void close() {
        System.out.println("closed");
    }
}
```

`AutoCloseable.close()` is declared `throws Exception`, but an implementation may
declare a *narrower* throws clause — including none at all, as above. That is
module 13's rule that an override may not broaden what it throws, used to good
effect: with no `throws`, callers need no handler.

**Several resources, separated by semicolons:**

```java
try (Resource a = new Resource("a"); Resource b = new Resource("b")) {
    ...
}
```

**They are closed in REVERSE order** — `b` first, then `a` — because the later
one may depend on the earlier. That ordering shows up in the exercises, and it is
the detail most people have not thought about.

**Closing happens before any `catch` or `finally` attached to the same `try`.**
So the output order is: body, close, then catch, then finally.

**The resource variable is implicitly final.** You cannot reassign it inside the
block, which is exactly right — Java has to know what to close.
""",
    warmup=[
        _jq("What interface must a try-with-resources resource implement?",
            ["AutoCloseable", "Closeable only", "Serializable", "Comparable"],
            0,
            "`Closeable` extends `AutoCloseable` and is the older, IO-specific one."),
        _jq("Two resources are opened in one try-with-resources. In what order are they closed?",
            ["Reverse order - the last opened is closed first",
             "The order they were opened",
             "Alphabetically",
             "Undefined"],
            0,
            "The later resource may depend on the earlier one, so it must be released "
            "first."),
    ],
    exercises=[
        _je("j16-res-basic", "Let Java close it",
            "`Res` implements `AutoCloseable` and prints `closed` when closed. Replace "
            "`____` with the try-with-resources header that opens one and closes it "
            "automatically.",
            _joop("class Res implements AutoCloseable {\n"
                  "    void use(int n) {\n"
                  '        System.out.println("using " + n);\n'
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public void close() {\n"
                  '        System.out.println("closed");\n'
                  "    }\n"
                  "}",
                  "        int v = sc.nextInt();\n"
                  "        try (Res r = new Res()) {\n"
                  "            r.use(v);\n"
                  "        }\n"
                  '        System.out.println("done");'),
            "try (Res r = new Res())",
            [_case(str(v), _nl(f"using {v}", "closed", "done"))
             for v in (5, 0, -3, 100, 1)],
            hints=["The resource is declared inside the parentheses of the `try`.",
                   "No `finally` and no explicit `close()` call are needed.",
                   "`try (Res r = new Res())`",
                   "`closed` prints before `done`, because the resource is released "
                   "as the block ends."],
            difficulty="Easy"),

        _je("j16-res-closeable", "Make it closeable",
            "For a class to be usable in try-with-resources it must implement one "
            "interface. Replace `____` with the class declaration.",
            _joop("class Res implements AutoCloseable {\n"
                  "    private final String name;\n"
                  "\n"
                  "    Res(String name) {\n"
                  "        this.name = name;\n"
                  "    }\n"
                  "\n"
                  "    @Override\n"
                  "    public void close() {\n"
                  '        System.out.println("closed " + name);\n'
                  "    }\n"
                  "}",
                  "        String nm = sc.next();\n"
                  "        try (Res r = new Res(nm)) {\n"
                  '            System.out.println("using " + nm);\n'
                  "        }"),
            "class Res implements AutoCloseable {",
            [_case(w, _nl(f"using {w}", f"closed {w}"))
             for w in ("a", "file", "db", "x", "sock")],
            hints=["The interface has a single method, `close()`.",
                   "`class Res implements AutoCloseable {`",
                   "`close()` must be `public`, because interface methods are.",
                   "The interface declares `close() throws Exception`, but an "
                   "implementation may narrow that to nothing — which is why `main` "
                   "needs no handler."],
            difficulty="Easy"),

        _jfix("j16-res-leak", "The close that gets skipped",
              "`use` divides by its argument, so a `0` makes it throw. This version "
              "calls `close()` as the last statement of the `try`, which is therefore "
              "skipped on the failing path — the resource leaks. Rewrite it as "
              "try-with-resources so it is closed on **both** paths. On failure the "
              "resource is closed before the handler runs, so `closed` comes before "
              "`error`.",
              _joop("class Res implements AutoCloseable {\n"
                    "    void use(int n) {\n"
                    '        System.out.println("using " + (100 / n));\n'
                    "    }\n"
                    "\n"
                    "    @Override\n"
                    "    public void close() {\n"
                    '        System.out.println("closed");\n'
                    "    }\n"
                    "}",
                    "        int v = sc.nextInt();\n"
                    "        Res r = new Res();\n"
                    "        try {\n"
                    "            r.use(v);\n"
                    "            r.close();\n"
                    "        } catch (ArithmeticException e) {\n"
                    '            System.out.println("error");\n'
                    "        }"),
              _joop("class Res implements AutoCloseable {\n"
                    "    void use(int n) {\n"
                    '        System.out.println("using " + (100 / n));\n'
                    "    }\n"
                    "\n"
                    "    @Override\n"
                    "    public void close() {\n"
                    '        System.out.println("closed");\n'
                    "    }\n"
                    "}",
                    "        int v = sc.nextInt();\n"
                    "        try (Res r = new Res()) {\n"
                    "            r.use(v);\n"
                    "        } catch (ArithmeticException e) {\n"
                    '            System.out.println("error");\n'
                    "        }"),
              [_case(str(v), _nl(f"using {_jdiv(100, v)}", "closed") if v != 0
                     else _nl("closed", "error"))
               for v in (5, 0, -4, 100, 2)],
              hints=["When `use` throws, the `r.close()` on the next line never runs "
                     "— that is the leak.",
                     "Move the construction into the `try`'s parentheses and delete "
                     "the explicit `close()` call.",
                     "`try (Res r = new Res()) { r.use(v); } catch (...) { ... }`",
                     "Closing happens BEFORE the catch block runs, which is why the "
                     "failing case prints `closed` and then `error`.",
                     "A `finally` with a null check would also fix it; "
                     "try-with-resources is the modern way and is much harder to get "
                     "wrong."],
              difficulty="Medium"),

        _jch("j16-res-order", "Two resources, closed backwards", "Medium",
             "Open two `Res` objects named from input in one try-with-resources, print "
             "`using <a> <b>` inside the block, and let both close. They close in "
             "reverse order, so the second name is reported closed first.",
             _joop("class Res implements AutoCloseable {\n"
                   "    private final String name;\n"
                   "\n"
                   "    Res(String name) {\n"
                   "        this.name = name;\n"
                   '        System.out.println("open " + name);\n'
                   "    }\n"
                   "\n"
                   "    @Override\n"
                   "    public void close() {\n"
                   '        System.out.println("close " + name);\n'
                   "    }\n"
                   "}",
                   "        String x = sc.next();\n"
                   "        String y = sc.next();\n"
                   "        try (Res a = new Res(x); Res b = new Res(y)) {\n"
                   '            System.out.println("using " + x + " " + y);\n'
                   "        }"),
             "        try (Res a = new Res(x); Res b = new Res(y)) {\n"
             '            System.out.println("using " + x + " " + y);\n'
             "        }",
             [_case(f"{x} {y}", _nl(f"open {x}", f"open {y}",
                                    f"using {x} {y}", f"close {y}", f"close {x}"))
              for (x, y) in (("a", "b"), ("db", "file"), ("x", "y"),
                             ("one", "two"), ("p", "q"))],
             hints=["Separate the two declarations with a SEMICOLON inside the "
                    "parentheses.",
                    "They are constructed left to right, so `open` prints in the "
                    "order given.",
                    "They are closed in REVERSE order, so the second `close` line is "
                    "the first resource.",
                    "That ordering exists because the later resource may depend on "
                    "the earlier one.",
                    "No `finally` is needed anywhere."]),
    ],
    quiz=[
        _jq("When is a try-with-resources resource closed?",
            ["As the block ends, on every path - normal, exception or return",
             "Only on the normal path",
             "Only if an exception is thrown",
             "When the JVM exits"],
            0,
            "It has the same guarantee as `finally`, with none of the boilerplate."),
        _jq("Why may `close()` in your own resource declare no `throws` clause?",
            ["An override may narrow what it throws, and narrowing to nothing spares callers a handler",
             "Because close() never fails",
             "Because AutoCloseable is unchecked",
             "It may not - the clause is required"],
            0,
            "The same rule module 13 gave for access modifiers applies to the throws "
            "clause: an override may be more restrictive, never less."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m16_run(start, ops):
    out = ["open vault"]
    bal = start
    for op in ops:
        parts = op.split(" ")
        if len(parts) != 2:
            out.append("BadCommandException: " + op)
            continue
        verb, amt = parts[0], parts[1]
        try:
            n = int(amt)
        except ValueError:
            out.append("BadCommandException: " + op)
            continue
        if verb == "in":
            if n <= 0:
                out.append("BadCommandException: " + op)
                continue
            bal += n
            out.append("balance=" + str(bal))
        elif verb == "out":
            if n <= 0:
                out.append("BadCommandException: " + op)
                continue
            if n > bal:
                out.append("InsufficientFundsException: short by " + str(n - bal))
                continue
            bal -= n
            out.append("balance=" + str(bal))
        else:
            out.append("BadCommandException: " + op)
    out.append("final=" + str(bal))
    out.append("close vault")
    return _nl(*out)


def _m16_case(start, ops):
    return _case("\n".join([str(start), str(len(ops))] + list(ops)) + "\n",
                 _m16_run(start, ops))


_M16_CAP = _jcap(
    "Vault",
    """
Everything in Part 5 in one program: two custom exception types, a resource that
closes itself, and a loop that survives every bad command.

## Input

```
start
n
<command>       x n
```

Each command should be `in <amount>` or `out <amount>` with a positive integer
amount.

## Output

`open vault` first (printed by the resource's constructor), then one line per
command, then the final balance, then `close vault`.

| Situation | Print |
|---|---|
| A valid `in` or `out` | `balance=<new balance>` |
| Not exactly two words, a non-numeric amount, an amount `<= 0`, or an unknown verb | `BadCommandException: <the whole command line>` |
| `out` for more than the balance | `InsufficientFundsException: short by <amount - balance>` |

Then:

```
final=<balance>
close vault
```

## The types you must write

| Type | What it is |
|---|---|
| `BadCommandException` | unchecked, extends `RuntimeException`, message is the offending command |
| `InsufficientFundsException` | unchecked, holds a `private final int shortfall`, message `short by <shortfall>`, with `int getShortfall()` |
| `Vault` | `implements AutoCloseable`; the constructor prints `open vault` and `close()` prints `close vault`; holds the balance with `deposit`, `withdraw` and `balance()` |

## What the hidden cases check

- **A failure never stops the loop.** Every command is attempted and the summary
  always prints.
- **A malformed command is reported before any arithmetic**, and the whole
  original line is echoed — so check `split(" ").length` before touching
  `parts[1]`.
- **A rejected command does not change the balance.** Throw before mutating.
- **`close vault` is printed by try-with-resources**, not by an explicit call.
  It must come last, after `final=`.
- **The two exception types are caught separately**, because they are reported
  differently — which is the whole reason for giving them distinct types.
""",
    _jch("j16-cap-vault", "Vault", "Hard",
         "Write the three types where you see `____`. `main` is already written: it "
         "opens the vault with try-with-resources, runs the commands, and prints the "
         "summary.",
         _joop("class BadCommandException extends RuntimeException {\n"
               "    BadCommandException(String message) {\n"
               "        super(message);\n"
               "    }\n"
               "}\n"
               "\n"
               "class InsufficientFundsException extends RuntimeException {\n"
               "    private final int shortfall;\n"
               "\n"
               "    InsufficientFundsException(int shortfall) {\n"
               '        super("short by " + shortfall);\n'
               "        this.shortfall = shortfall;\n"
               "    }\n"
               "\n"
               "    int getShortfall() {\n"
               "        return shortfall;\n"
               "    }\n"
               "}\n"
               "\n"
               "class Vault implements AutoCloseable {\n"
               "    private int balance;\n"
               "\n"
               "    Vault(int balance) {\n"
               "        this.balance = balance;\n"
               '        System.out.println("open vault");\n'
               "    }\n"
               "\n"
               "    int balance() {\n"
               "        return balance;\n"
               "    }\n"
               "\n"
               "    void deposit(int amount) {\n"
               "        balance = balance + amount;\n"
               "    }\n"
               "\n"
               "    void withdraw(int amount) {\n"
               "        if (amount > balance) {\n"
               "            throw new InsufficientFundsException(amount - balance);\n"
               "        }\n"
               "        balance = balance - amount;\n"
               "    }\n"
               "\n"
               "    @Override\n"
               "    public void close() {\n"
               '        System.out.println("close vault");\n'
               "    }\n"
               "}",
               "        int start = Integer.parseInt(sc.nextLine());\n"
               "        int n = Integer.parseInt(sc.nextLine());\n"
               "        try (Vault v = new Vault(start)) {\n"
               "            for (int i = 0; i < n; i++) {\n"
               "                String line = sc.nextLine();\n"
               "                try {\n"
               '                    String[] parts = line.split(" ");\n'
               "                    if (parts.length != 2) {\n"
               "                        throw new BadCommandException(line);\n"
               "                    }\n"
               "                    int amount;\n"
               "                    try {\n"
               "                        amount = Integer.parseInt(parts[1]);\n"
               "                    } catch (NumberFormatException e) {\n"
               "                        throw new BadCommandException(line);\n"
               "                    }\n"
               "                    if (amount <= 0) {\n"
               "                        throw new BadCommandException(line);\n"
               "                    }\n"
               '                    if (parts[0].equals("in")) {\n'
               "                        v.deposit(amount);\n"
               '                    } else if (parts[0].equals("out")) {\n'
               "                        v.withdraw(amount);\n"
               "                    } else {\n"
               "                        throw new BadCommandException(line);\n"
               "                    }\n"
               '                    System.out.println("balance=" + v.balance());\n'
               "                } catch (InsufficientFundsException e) {\n"
               '                    System.out.println("InsufficientFundsException: "\n'
               "                        + e.getMessage());\n"
               "                } catch (BadCommandException e) {\n"
               '                    System.out.println("BadCommandException: "\n'
               "                        + e.getMessage());\n"
               "                }\n"
               "            }\n"
               '            System.out.println("final=" + v.balance());\n'
               "        }"),
         "class BadCommandException extends RuntimeException {\n"
         "    BadCommandException(String message) {\n"
         "        super(message);\n"
         "    }\n"
         "}\n"
         "\n"
         "class InsufficientFundsException extends RuntimeException {\n"
         "    private final int shortfall;\n"
         "\n"
         "    InsufficientFundsException(int shortfall) {\n"
         '        super("short by " + shortfall);\n'
         "        this.shortfall = shortfall;\n"
         "    }\n"
         "\n"
         "    int getShortfall() {\n"
         "        return shortfall;\n"
         "    }\n"
         "}\n"
         "\n"
         "class Vault implements AutoCloseable {\n"
         "    private int balance;\n"
         "\n"
         "    Vault(int balance) {\n"
         "        this.balance = balance;\n"
         '        System.out.println("open vault");\n'
         "    }\n"
         "\n"
         "    int balance() {\n"
         "        return balance;\n"
         "    }\n"
         "\n"
         "    void deposit(int amount) {\n"
         "        balance = balance + amount;\n"
         "    }\n"
         "\n"
         "    void withdraw(int amount) {\n"
         "        if (amount > balance) {\n"
         "            throw new InsufficientFundsException(amount - balance);\n"
         "        }\n"
         "        balance = balance - amount;\n"
         "    }\n"
         "\n"
         "    @Override\n"
         "    public void close() {\n"
         '        System.out.println("close vault");\n'
         "    }\n"
         "}",
         [_m16_case(start, ops) for (start, ops) in (
             (100, ["in 50", "out 30", "out 500"]),
             (0, ["out 1"]),
             (10, ["in x", "in 0", "sideways 5", "in 5"]),
             (50, ["out 50", "out 1"]),
             (5, ["in 5", "in 5", "out 12", "nope"]),
         )],
         hints=["Both exception types extend `RuntimeException`, so nothing needs a "
                "`throws` clause.",
                "`BadCommandException`'s message IS the offending line, so "
                "`super(message)` is all its constructor does.",
                "`InsufficientFundsException` stores the shortfall AND sets the "
                "message from it — `super(\"short by \" + shortfall);` first, then "
                "assign the field.",
                "`Vault` implements `AutoCloseable`; the constructor prints "
                "`open vault` and `close()` prints `close vault`, both as their only "
                "output.",
                "`withdraw` must throw BEFORE subtracting, so a rejected withdrawal "
                "leaves the balance untouched.",
                "`deposit` does no validation — `main` has already rejected "
                "non-positive amounts before calling it.",
                "`main` catches the two types separately because they are reported "
                "differently. That is the whole reason for two types.",
                "`close vault` is printed by try-with-resources as the block ends, so "
                "it lands after `final=`."]),
    example_io="stdin:  100\n        3\n        in 50\n        out 30\n        out 500\n\n"
               "stdout: open vault\n        balance=150\n        balance=120\n"
               "        InsufficientFundsException: short by 380\n        final=120\n"
               "        close vault",
    rubric=[
        "Both exception types extend `RuntimeException`, so no `throws` clause appears anywhere.",
        "`BadCommandException` carries the offending line as its message.",
        "`InsufficientFundsException` stores the shortfall and derives its message from it.",
        "`Vault` implements `AutoCloseable` and prints `open vault` / `close vault` from its constructor and `close()`.",
        "`withdraw` throws before mutating, so a refused withdrawal leaves the balance unchanged.",
        "The two exception types are caught by separate handlers.",
        "No bad command stops the loop.",
        "`close vault` comes from try-with-resources, after `final=`.",
    ],
)


_MODULES.append(_jmod(
    16, 5, "Exception handling",
    "Throwing, checked exceptions, and resources",
    "Raise exceptions deliberately, understand the split the compiler enforces, write "
    "exception types of your own, and let try-with-resources do the closing.",
    """
Module 15 was about surviving other people's failures. This one is about
declaring your own.

`throw` is the third answer to a bad argument, alongside module 12's clamping and
rejecting — and it is the right one when the call itself is a mistake rather
than a situation to absorb. The discipline is to throw early, name the type
precisely, and put the offending value in the message.

The **checked/unchecked split** is the one place Java's type system makes you
plan for failure. Everything under `Exception` is checked except the
`RuntimeException` subtree, and a checked exception obliges every caller to
catch it or declare it. Use checked for what a caller could recover from and did
not cause; unchecked for programming errors.

**Custom exception types** are ordinary classes — module 13's inheritance doing
real work. The reason to write one is that `catch` matches on *type*, so a
distinct type is what lets one handler deal with insufficient funds and another
with a malformed command, without anyone parsing message strings.

**try-with-resources** then removes the last of the boilerplate: declare the
resource in the parentheses, implement `AutoCloseable`, and closing happens on
every path — in reverse order, before any catch, with no `finally` in sight.
""",
    _M16,
    capstone=_M16_CAP,
    objectives=[
        "Throw an exception deliberately, with a type and message that help.",
        "Choose between IllegalArgumentException and IllegalStateException.",
        "Say precisely what checked means, and where the boundary sits in the hierarchy.",
        "Use `throws` to propagate, and explain how it differs from `throw`.",
        "Decide whether a new exception type should be checked or unchecked.",
        "Write a custom exception, including one that carries data.",
        "Use try-with-resources, and implement `AutoCloseable`.",
        "State the closing order for several resources, and when closing happens.",
    ],
    why="Throwing well is what makes a library usable: a precise type and a message "
        "with the offending value turn a three-hour debugging session into a "
        "thirty-second one. The checked-versus-unchecked question is asked in almost "
        "every Java interview, and try-with-resources is the idiom every modern "
        "codebase uses for anything that must be released.",
    est_minutes=300,
    glossary=[
        _jg("throw", "The statement that raises an exception object."),
        _jg("throws", "A clause in a method signature declaring what checked exceptions "
                      "may come out of it."),
        _jg("checked exception", "Anything under Exception but not under "
                                 "RuntimeException. Callers must catch or declare it."),
        _jg("unchecked exception", "RuntimeException and its subclasses, plus Error. The "
                                   "compiler imposes nothing."),
        _jg("IllegalArgumentException", "The standard 'this argument is wrong'. "
                                        "Unchecked."),
        _jg("IllegalStateException", "The standard 'the object is not in a state where "
                                     "this call makes sense'. Unchecked."),
        _jg("custom exception", "A class extending RuntimeException (unchecked) or "
                                "Exception (checked), named ending in Exception."),
        _jg("AutoCloseable", "The interface with a single `close()` method that "
                             "try-with-resources requires."),
        _jg("try-with-resources", "`try (R r = new R()) { ... }` - closes r on every "
                                  "path, in reverse declaration order, with no finally."),
        _jg("unreported exception", "The compile error you get for a checked exception "
                                    "that is neither caught nor declared."),
    ],
    cheatsheet="""
```java
// --- throwing ------------------------------------------------------------
throw new IllegalArgumentException("negative: " + n);   // bad argument
throw new IllegalStateException("already open");        // bad object state
// Always include the offending value. Code after a throw is unreachable.

// --- checked vs unchecked ------------------------------------------------
// Throwable
//  ├─ Error                  unchecked - never catch
//  └─ Exception              CHECKED
//      └─ RuntimeException   unchecked

static void risky() throws Exception { ... }   // DECLARES (note the s)
static void a() throws Exception { risky(); }  // choice 1: propagate
static void b() { try { risky(); }             // choice 2: handle
                  catch (Exception e) { } }
// Neither one => "unreported exception ... must be caught or declared"

// --- a custom type -------------------------------------------------------
class TooSmallException extends RuntimeException {   // unchecked
    private final int shortfall;
    TooSmallException(int shortfall) {
        super("short by " + shortfall);              // FIRST statement
        this.shortfall = shortfall;
    }
    int getShortfall() { return shortfall; }
}
// extends Exception instead => checked. Name it ...Exception.

// --- try-with-resources --------------------------------------------------
class Res implements AutoCloseable {
    @Override public void close() { ... }      // may narrow the throws clause
}

try (Res a = new Res(); Res b = new Res()) {   // semicolon between
    ...
}                    // closes b THEN a, on every path, before any catch

// Replaces:
Res r = null;
try { r = new Res(); ... } finally { if (r != null) r.close(); }
```
""",
    self_check=[
        "Can you say when throwing beats clamping or returning a sentinel?",
        "Can you pick between IllegalArgumentException and IllegalStateException for a given mistake?",
        "Can you draw the checked/unchecked boundary on the hierarchy?",
        "Can you state the two options a caller of a checked-throwing method has?",
        "Can you explain the difference between `throw` and `throws` without hesitating?",
        "Can you write a custom exception that carries a field, and say why that helps?",
        "Can you decide whether a new exception type should extend Exception or RuntimeException?",
        "Can you rewrite a null-check-plus-finally block as try-with-resources?",
        "Can you say in what order two resources are closed, and why?",
    ],
    review=[
        _jq("Which of these is a CHECKED exception?",
            ["Exception", "IllegalStateException", "NumberFormatException",
             "ArithmeticException"],
            0,
            "The other three all live under RuntimeException."),
        _jq("A method body contains `throw new Exception(\"x\");` and nothing else. What must its signature include?",
            ["`throws Exception`", "nothing", "`throw Exception`",
             "`catch Exception`"],
            0,
            "Exception is checked, so the method must declare it or catch it itself."),
        _jq("```java\ntry (Res a = new Res(\"a\"); Res b = new Res(\"b\")) { }\n```\nWhich closes first?",
            ["b", "a", "Neither - close is not called", "Both simultaneously"],
            0,
            "Reverse declaration order, because the later resource may depend on the "
            "earlier."),
        _jq("In the capstone, why must `withdraw` throw before subtracting?",
            ["So a refused withdrawal leaves the balance unchanged",
             "For speed",
             "Because the exception is unchecked",
             "It does not matter"],
            0,
            "An operation that fails halfway leaves the object in a state its "
            "invariant forbids - module 12's lesson, now with exceptions."),
    ],
    milestone="You can design a failure story for your own code: throwing precisely, "
              "choosing checked or unchecked deliberately, giving distinct problems "
              "distinct types, and releasing resources without a single `finally` "
              "block. Part 5 is complete.",
))
