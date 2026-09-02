# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 15 - What an exception is, and catching it.
#
# exec()-ed by tools/java_course.py; appends one module to `_MODULES`.
#
# Opens Part 5. Everything from modules 1-14 is available; `throw`, `throws`
# and custom exceptions are module 16, and try-with-resources is module 16 too.
#
# OUTPUT STABILITY: an exception's stack trace and some of its default messages
# vary between JDK versions, so no exercise here prints a raw trace. Where the
# identity of an exception matters, programs print
# `e.getClass().getSimpleName()`, which is specified. The only default message
# used is ArithmeticException's "/ by zero", which is stable, and
# NumberFormatException's, which is printed only via getSimpleName().
# ---------------------------------------------------------------------------

_M15 = []


# --- 15.1 what an exception is ----------------------------------------------

_M15.append(_jlesson(
    "m15-what", "What an exception is",
    "The second way out of a method, and what happens to the stack.",
    """
Every method you have written so far had exactly one way to finish: run to the
end, or `return`. An **exception** is the second way — an abrupt exit that
carries an object describing what went wrong.

```java
int[] a = new int[3];
System.out.println(a[5]);      // ArrayIndexOutOfBoundsException
System.out.println("after");   // never runs
```

**What actually happens**, in order:

1. The JVM creates an exception object — here an
   `ArrayIndexOutOfBoundsException` — recording the type, a message, and the
   call stack at the moment of failure.
2. The current method **stops immediately**. No further statement in it runs.
3. Java looks for a handler in that method. If there is none, the method exits
   abruptly and the search continues in *its* caller, then that caller's caller.
   This is **stack unwinding**.
4. If nobody handles it, the thread dies and the JVM prints a **stack trace**.

That trace is the most useful thing in Java and the most ignored. Read it from
the **top**: the first line is the exception type and message, and the first
`at ...` line is exactly where it happened.

```
Exception in thread "main" java.lang.ArithmeticException: / by zero
	at Main.divide(Main.java:7)
	at Main.main(Main.java:3)
```

`divide` failed at line 7, and it was called from `main` at line 3.

**The four you will meet constantly:**

| Exception | Cause |
|---|---|
| `NullPointerException` | calling a method on `null` |
| `ArrayIndexOutOfBoundsException` | index outside `0 .. length-1` |
| `ArithmeticException` | integer division by zero |
| `NumberFormatException` | `Integer.parseInt("abc")` |

**Only integer division throws.** `1.0 / 0` is `Infinity`, a legal `double`.
That asymmetry surprises people, and it is why the exercises here stay with
`int`.

**An exception is an object.** `e.getMessage()` returns its text, and
`e.getClass().getSimpleName()` returns its type name — both are ordinary method
calls on an ordinary object.
""",
    warmup=[
        _jq("What happens to the statements after the line that throws, inside the same method?",
            ["They never run — the method exits abruptly",
             "They run, then the exception is reported",
             "Only the next one runs",
             "They run if they do not use the failed variable"],
            0,
            "An exception is an immediate exit. Nothing further in that method executes."),
        _jq("Which of these does NOT throw?",
            ["1.0 / 0", "1 / 0", "new int[3][5]", "Integer.parseInt(\"x\")"],
            0,
            "Floating-point division by zero gives Infinity. Only integer division throws "
            "ArithmeticException."),
    ],
    exercises=[
        _je("j15-what-name", "Name the failure",
            "The program divides by zero inside a `try`. Replace `____` so the catch "
            "block prints the exception's simple class name.",
            _jscan("        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        try {\n"
                   "            System.out.println(a / b);\n"
                   "        } catch (ArithmeticException e) {\n"
                   "            System.out.println(e.getClass().getSimpleName());\n"
                   "        }"),
            "e.getClass().getSimpleName()",
            [_case("6 3", "2"), _case("6 0", "ArithmeticException"),
             _case("-9 3", "-3"), _case("0 0", "ArithmeticException"),
             _case("7 2", "3")],
            hints=["An exception is an object, so you can call methods on it.",
                   "`getClass()` gives its class; that has a `getSimpleName()`.",
                   "`e.getClass().getSimpleName()`"],
            difficulty="Intro"),

        _je("j15-what-message", "Read the message",
            "Print the exception's message instead of its type. For integer division "
            "by zero Java's message is exactly `/ by zero`.",
            _jscan("        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        try {\n"
                   "            System.out.println(a / b);\n"
                   "        } catch (ArithmeticException e) {\n"
                   "            System.out.println(e.getMessage());\n"
                   "        }"),
            "e.getMessage()",
            [_case("6 3", "2"), _case("6 0", "/ by zero"),
             _case("-9 3", "-3"), _case("0 0", "/ by zero"),
             _case("8 4", "2")],
            hints=["Every exception carries a human-readable message.",
                   "The method is a plain getter.",
                   "`e.getMessage()`"],
            difficulty="Intro"),

        _jfix("j15-what-order", "Statements after the throw",
              "This program means to print the quotient and then `done`, and to print "
              "`error` instead when the division fails. As written it prints `done` "
              "even on success and never on failure. Move the statements so both cases "
              "are right: on success print the quotient then `done`; on failure print "
              "`error` only.",
              _jscan("        int a = sc.nextInt();\n"
                     "        int b = sc.nextInt();\n"
                     "        try {\n"
                     "            System.out.println(a / b);\n"
                     "        } catch (ArithmeticException e) {\n"
                     '            System.out.println("error");\n'
                     "        }\n"
                     '        System.out.println("done");'),
              _jscan("        int a = sc.nextInt();\n"
                     "        int b = sc.nextInt();\n"
                     "        try {\n"
                     "            System.out.println(a / b);\n"
                     '            System.out.println("done");\n'
                     "        } catch (ArithmeticException e) {\n"
                     '            System.out.println("error");\n'
                     "        }"),
              [_case("6 3", _nl(2, "done")), _case("6 0", "error"),
               _case("-9 3", _nl(-3, "done")), _case("0 0", "error"),
               _case("9 2", _nl(4, "done"))],
              hints=["Anything after the `try`/`catch` runs whichever branch was "
                     "taken — that is why `done` appears on failure too.",
                     "To make a statement part of the success path, put it INSIDE the "
                     "`try`, after the risky line.",
                     "If the division throws, the `println(\"done\")` on the next line "
                     "of the try never runs, which is exactly what you want.",
                     "Move `System.out.println(\"done\");` into the try block and "
                     "delete it from after the catch."],
              difficulty="Easy"),

        _jch("j15-what-index", "Guard an array access", "Easy",
             "Read an array, then an index. Print the element at that index, or "
             "`out of range` if the index is invalid. Catch the exception rather than "
             "checking the index first.",
             _jscan(_RD_ARR
                    + "        int i = sc.nextInt();\n"
                    + "        try {\n"
                      "            System.out.println(a[i]);\n"
                      "        } catch (ArrayIndexOutOfBoundsException e) {\n"
                      '            System.out.println("out of range");\n'
                      "        }"),
             "        try {\n"
             "            System.out.println(a[i]);\n"
             "        } catch (ArrayIndexOutOfBoundsException e) {\n"
             '            System.out.println("out of range");\n'
             "        }",
             [_akcase([3, 1, 4], 1, 1), _akcase([3, 1, 4], 5, "out of range"),
              _akcase([7], 0, 7), _akcase([3, 1, 4], -1, "out of range"),
              _akcase([3, 1, 4], 2, 4)],
             hints=["Put the risky access inside `try { ... }`.",
                    "`catch (ArrayIndexOutOfBoundsException e) { ... }` follows it "
                    "immediately.",
                    "A negative index throws the same exception as one that is too "
                    "big — case four checks that.",
                    "Print nothing else: on success only the element, on failure only "
                    "the message."]),
    ],
    quiz=[
        _jq("What is stack unwinding?",
            ["Java searching each caller in turn for a handler, exiting methods abruptly as it goes",
             "The JVM clearing memory after a crash",
             "Reversing the order of method calls",
             "Printing the stack trace"],
            0,
            "The exception propagates outward from where it was thrown until something "
            "catches it, or the thread dies."),
        _jq("In a stack trace, which line tells you where the failure happened?",
            ["The first `at ...` line, directly under the exception type",
             "The last `at ...` line",
             "The line mentioning main",
             "It is not shown"],
            0,
            "Read from the top. The frames below it are the callers that led there."),
    ],
))


# --- 15.2 try and catch -----------------------------------------------------

_M15.append(_jlesson(
    "m15-catch", "`try` and `catch`",
    "Marking the risky region, and deciding what to do instead.",
    """
```java
try {
    // statements that might fail
} catch (ArithmeticException e) {
    // what to do instead
}
```

**The `try` block is a region, not a single statement.** If anything inside it
throws, the rest of the block is skipped and control jumps to the matching
`catch`. Execution then continues *after* the whole construct — the try block is
never resumed.

**`catch` is matched by type, and subclasses count.** A
`catch (RuntimeException e)` will catch an `ArithmeticException`, because
`ArithmeticException` is a `RuntimeException`. That is the same `instanceof`
subtree rule from module 13.

**The variable `e` is an ordinary object.** `e.getMessage()`,
`e.getClass().getSimpleName()`, and `e.toString()` all work, and its scope is
the catch block only.

## Scope, and the "might not be initialised" trap

```java
try {
    int v = Integer.parseInt(s);
} catch (NumberFormatException e) { }
System.out.println(v);           // does NOT compile: v is out of scope
```

A variable declared inside the `try` does not exist outside it. And moving the
declaration out brings a second problem:

```java
int v;
try { v = Integer.parseInt(s); }
catch (NumberFormatException e) { }
System.out.println(v);           // does NOT compile: v might not be assigned
```

Java refuses because the catch path leaves `v` unassigned. **The fix is to give
it a value in the catch block** — which is usually what you wanted anyway:

```java
int v;
try { v = Integer.parseInt(s); }
catch (NumberFormatException e) { v = 0; }     // a default
```

That pattern — *try to compute it, fall back on failure* — is most of what
`catch` is for in practice.

**Do not catch what you can cheaply test.** Checking `b != 0` is clearer and
faster than catching `ArithmeticException`. Exceptions are for the situations
you genuinely cannot check in advance, like parsing arbitrary text.
""",
    warmup=[
        _jq("`catch (RuntimeException e)` — will it catch an ArithmeticException?",
            ["Yes, because ArithmeticException is a subclass of RuntimeException",
             "No, the types must match exactly",
             "Only if you also catch ArithmeticException",
             "Only for integer division"],
            0,
            "Catch matching follows the type hierarchy, the same subtree rule as "
            "`instanceof`."),
        _jq("Why does printing a variable declared inside a `try` fail to compile outside it?",
            ["Its scope is the try block, exactly like any other block-local variable",
             "Because exceptions delete variables",
             "Because try blocks run in a separate method",
             "It does compile"],
            0,
            "A `try` block is an ordinary block. Declare the variable before it if you "
            "need it afterwards."),
    ],
    exercises=[
        _je("j15-catch-parse", "Fall back on a default",
            "Read a line and try to parse it as an integer, printing it doubled. If it "
            "is not a number, print `0`. Replace `____` with the assignment the catch "
            "block needs.",
            _jscan("        String s = sc.nextLine();\n"
                   "        int v;\n"
                   "        try {\n"
                   "            v = Integer.parseInt(s);\n"
                   "        } catch (NumberFormatException e) {\n"
                   "            v = 0;\n"
                   "        }\n"
                   "        System.out.println(v * 2);"),
            "            v = 0;",
            [_lcase("21", 42), _lcase("abc", 0), _lcase("0", 0),
             _lcase("-5", -10), _lcase("3.5", 0)],
            hints=["`v` is declared before the try, so it survives — but Java insists "
                   "every path assigns it.",
                   "The catch block is the path that has not assigned it yet.",
                   "Give it the fallback value the brief asks for: `v = 0;`",
                   "`3.5` is not an `int`, so `parseInt` throws for it too."],
            difficulty="Easy"),

        _je("j15-catch-type", "Catch the supertype",
            "Both a bad number and a division by zero should print `bad input`. "
            "Replace `____` with a single catch type that covers both.",
            _jscan("        String s = sc.nextLine();\n"
                   "        String t = sc.nextLine();\n"
                   "        try {\n"
                   "            int a = Integer.parseInt(s);\n"
                   "            int b = Integer.parseInt(t);\n"
                   "            System.out.println(a / b);\n"
                   "        } catch (RuntimeException e) {\n"
                   '            System.out.println("bad input");\n'
                   "        }"),
            "RuntimeException",
            [_l2case("6", "3", "2"), _l2case("6", "0", "bad input"),
             _l2case("x", "3", "bad input"), _l2case("9", "y", "bad input"),
             _l2case("-9", "3", "-3")],
            hints=["`NumberFormatException` and `ArithmeticException` have a common "
                   "ancestor.",
                   "Both are unchecked, so both sit under `RuntimeException`.",
                   "Catching the supertype catches every subclass — the same subtree "
                   "rule as `instanceof`.",
                   "`RuntimeException`"],
            difficulty="Easy"),

        _jfix("j15-catch-scope", "The variable that escaped",
              "This does not compile: `v` is declared inside the `try`, so the "
              "`println` after it cannot see the name. Move the declaration out and "
              "make sure every path assigns it. On a bad number print `-1`.",
              _jscan("        String s = sc.nextLine();\n"
                     "        try {\n"
                     "            int v = Integer.parseInt(s);\n"
                     "        } catch (NumberFormatException e) {\n"
                     "        }\n"
                     "        System.out.println(v);"),
              _jscan("        String s = sc.nextLine();\n"
                     "        int v;\n"
                     "        try {\n"
                     "            v = Integer.parseInt(s);\n"
                     "        } catch (NumberFormatException e) {\n"
                     "            v = -1;\n"
                     "        }\n"
                     "        System.out.println(v);"),
              [_lcase("21", 21), _lcase("abc", -1), _lcase("0", 0),
               _lcase("-5", -5), _lcase("", -1)],
              hints=["Declare `int v;` BEFORE the `try`, so its scope covers the "
                     "println.",
                     "Then the try block assigns it rather than declaring it — drop "
                     "the `int`.",
                     "Java now complains that `v` might not be assigned on the catch "
                     "path.",
                     "Assign the fallback in the catch: `v = -1;`",
                     "An empty line is not a number either, so it takes the catch "
                     "path."],
              difficulty="Medium"),

        _jch("j15-catch-loop", "Keep going after a failure", "Medium",
             "Read `n`, then `n` lines each holding a token. Print the total of the "
             "ones that parse as integers, ignoring the rest. A failure must not stop "
             "the loop.",
             _jscan("        int n = Integer.parseInt(sc.nextLine());\n"
                    "        int total = 0;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String s = sc.nextLine();\n"
                    "            try {\n"
                    "                total += Integer.parseInt(s);\n"
                    "            } catch (NumberFormatException e) {\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(total);"),
             "            try {\n"
             "                total += Integer.parseInt(s);\n"
             "            } catch (NumberFormatException e) {\n"
             "            }",
             [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                    sum(int(x) for x in xs if x.lstrip("-").isdigit()))
              for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                         ["-4", "5", "x"], ["0", "0", "0"])],
             hints=["The `try` goes INSIDE the loop, around the parse.",
                    "Putting it around the whole loop instead would abandon every "
                    "remaining line on the first bad one.",
                    "An empty catch block is acceptable here because the brief says to "
                    "ignore failures — but say so in a comment in real code.",
                    "Only add to `total` when the parse succeeds, so the `+=` belongs "
                    "inside the try."]),
    ],
    quiz=[
        _jq("After a caught exception, where does execution continue?",
            ["After the whole try/catch construct",
             "At the line after the one that threw, inside the try",
             "At the start of the try block again",
             "The program exits"],
            0,
            "The try block is abandoned. It is never resumed part-way through."),
        _jq("When should you check a condition instead of catching an exception?",
            ["Whenever the check is cheap and reliable, like `b != 0`",
             "Never — catching is always better",
             "Only inside loops",
             "Only for checked exceptions"],
            0,
            "Exceptions are for what you cannot reasonably test in advance. Using them "
            "for ordinary control flow is slower and much harder to read."),
    ],
))


# --- 15.3 finally -----------------------------------------------------------

_M15.append(_jlesson(
    "m15-finally", "`finally`",
    "The block that runs whatever happens.",
    """
```java
try {
    risky();
} catch (SomeException e) {
    handle();
} finally {
    cleanUp();          // runs on EVERY path
}
```

**`finally` runs whether or not an exception was thrown, and whether or not it
was caught.** It even runs when the `try` block executes a `return`. Its job is
cleanup that must not be skipped — closing a file, releasing a lock, restoring
state.

**The exact order** is worth committing to memory:

| Situation | Order |
|---|---|
| No exception | try body, then finally |
| Exception, caught | try up to the throw, catch, then finally |
| Exception, not caught | try up to the throw, finally, **then** the exception propagates |
| `return` inside try | try body, **finally**, then the method actually returns |

That third row is the one people get wrong: `finally` runs even when nothing
catches, on the way out.

**`try` needs at least one of `catch` or `finally`**, but not both. A
`try`/`finally` with no catch is perfectly normal — it says "I am not handling
this, but I am cleaning up regardless."

**Never `return` from a `finally` block.** It silently discards any exception
that was in flight, and any value the `try` was about to return:

```java
try { return 1; } finally { return 2; }     // returns 2 — the 1 is lost
```

The compiler warns; take the warning. The same applies to `break` and
`continue`.

> Module 16 introduces **try-with-resources**, which replaces almost every
> `finally` block you would otherwise write for closing things. `finally` is
> still what you reach for when the cleanup is not a resource.
""",
    warmup=[
        _jq("An exception is thrown inside `try` and NOT caught. Does `finally` run?",
            ["Yes — it runs on the way out, before the exception propagates",
             "No, the method exits immediately",
             "Only if there is a catch block somewhere",
             "Only for checked exceptions"],
            0,
            "That is exactly what `finally` is for: cleanup that survives an unhandled "
            "failure."),
        _jq("What does `try { return 1; } finally { return 2; }` return?",
            ["2 — the finally's return replaces it", "1", "It does not compile",
             "Both, in order"],
            0,
            "A return in finally discards whatever was in flight, exceptions included. "
            "Never do it."),
    ],
    exercises=[
        _je("j15-finally-order", "Prove the order",
            "Print `try`, then `catch` only if the division fails, then always "
            "`finally`. Replace `____` with the block that must always run.",
            _jscan("        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        try {\n"
                   '            System.out.println("try");\n'
                   "            System.out.println(a / b);\n"
                   "        } catch (ArithmeticException e) {\n"
                   '            System.out.println("catch");\n'
                   "        } finally {\n"
                   '            System.out.println("finally");\n'
                   "        }"),
            "        } finally {\n"
            '            System.out.println("finally");\n'
            "        }",
            [_case("6 3", _nl("try", 2, "finally")),
             _case("6 0", _nl("try", "catch", "finally")),
             _case("-9 3", _nl("try", -3, "finally")),
             _case("0 0", _nl("try", "catch", "finally")),
             _case("8 2", _nl("try", 4, "finally"))],
            hints=["`finally` comes after the catch block, attached to the same "
                   "`try`.",
                   "It runs on both paths, so `finally` is always the last line "
                   "printed.",
                   "On success the quotient is printed and `catch` is not.",
                   "`} finally { ... }`"],
            difficulty="Easy"),

        _je("j15-finally-nocatch", "Cleanup without handling",
            "This program does not handle the failure — it only guarantees cleanup. "
            "Replace `____` with the keyword that attaches a block running on every "
            "path, including the failing one.",
            _jscan("        int a = sc.nextInt();\n"
                   "        int b = sc.nextInt();\n"
                   "        int result = -1;\n"
                   "        try {\n"
                   "            result = a / b;\n"
                   "        } catch (ArithmeticException e) {\n"
                   "            result = 0;\n"
                   "        } finally {\n"
                   '            System.out.println("closed");\n'
                   "        }\n"
                   "        System.out.println(result);"),
            "finally",
            [_case("6 3", _nl("closed", 2)), _case("6 0", _nl("closed", 0)),
             _case("-9 3", _nl("closed", -3)), _case("0 0", _nl("closed", 0)),
             _case("9 3", _nl("closed", 3))],
            hints=["One keyword, between the catch block's closing brace and the "
                   "opening brace of the cleanup block.",
                   "It is the block that runs regardless of outcome.",
                   "`finally`",
                   "Note that `closed` is printed before the result, because the "
                   "finally block runs before execution leaves the construct."],
            difficulty="Intro"),

        _jfix("j15-finally-return", "The return that swallowed everything",
              "This helper is meant to return the parsed value, or `-1` when parsing "
              "fails, and to print `done` either way. The `return` inside `finally` "
              "makes it return `0` for everything. Remove that return so the real "
              "values survive.",
              _jcls("    static int parse(String s) {\n"
                    "        try {\n"
                    "            return Integer.parseInt(s);\n"
                    "        } catch (NumberFormatException e) {\n"
                    "            return -1;\n"
                    "        } finally {\n"
                    '            System.out.println("done");\n'
                    "            return 0;\n"
                    "        }\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        System.out.println(parse(sc.nextLine()));\n"
                    "    }"),
              _jcls("    static int parse(String s) {\n"
                    "        try {\n"
                    "            return Integer.parseInt(s);\n"
                    "        } catch (NumberFormatException e) {\n"
                    "            return -1;\n"
                    "        } finally {\n"
                    '            System.out.println("done");\n'
                    "        }\n"
                    "    }\n"
                    "\n"
                    + _MAIN_SIG + "\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        System.out.println(parse(sc.nextLine()));\n"
                    "    }"),
              [_lcase("21", _nl("done", 21)), _lcase("abc", _nl("done", -1)),
               _lcase("0", _nl("done", 0)), _lcase("-5", _nl("done", -5)),
               _lcase("x1", _nl("done", -1))],
              hints=["A `return` in `finally` overrides whatever the try or catch was "
                     "about to return.",
                     "It would also discard an exception in flight, which is worse.",
                     "Delete `return 0;` and keep the `println`.",
                     "`done` still prints first on every path, because finally runs "
                     "before the method actually returns."],
              difficulty="Medium"),

        _jch("j15-finally-count", "Count every attempt", "Medium",
             "Read `n`, then `n` tokens. Print the number that parsed successfully, "
             "then the number attempted. Increment the attempt counter in a `finally` "
             "so it counts both outcomes.",
             _jscan("        int n = Integer.parseInt(sc.nextLine());\n"
                    "        int ok = 0;\n"
                    "        int tried = 0;\n"
                    "        for (int i = 0; i < n; i++) {\n"
                    "            String s = sc.nextLine();\n"
                    "            try {\n"
                    "                Integer.parseInt(s);\n"
                    "                ok++;\n"
                    "            } catch (NumberFormatException e) {\n"
                    "            } finally {\n"
                    "                tried++;\n"
                    "            }\n"
                    "        }\n"
                    "        System.out.println(ok);\n"
                    "        System.out.println(tried);"),
             "            try {\n"
             "                Integer.parseInt(s);\n"
             "                ok++;\n"
             "            } catch (NumberFormatException e) {\n"
             "            } finally {\n"
             "                tried++;\n"
             "            }",
             [_case("\n".join([str(len(xs))] + list(xs)) + "\n",
                    _nl(sum(1 for x in xs if x.lstrip("-").isdigit()), len(xs)))
              for xs in (["1", "two", "3"], ["10"], ["a", "b"],
                         ["-4", "5", "x"], ["0", "0", "0"])],
             hints=["`ok++` belongs inside the try, AFTER the parse — so it only runs "
                    "when the parse succeeded.",
                    "`tried++` belongs in the `finally`, so it counts both paths.",
                    "The catch block can be empty; the brief only asks you to count.",
                    "All three blocks sit inside the loop, so each token is its own "
                    "attempt."]),
    ],
    quiz=[
        _jq("Is `try` with only a `finally` and no `catch` legal?",
            ["Yes — it means 'I am not handling this, but I will clean up'",
             "No, catch is mandatory",
             "Only inside a method that declares throws",
             "Only with try-with-resources"],
            0,
            "`try` needs at least one of catch or finally. Either alone is fine."),
        _jq("A method does `return x;` inside a try that has a finally. When does finally run?",
            ["After the return value is computed, but before the method actually returns",
             "Never — return skips it",
             "After the caller receives the value",
             "Only if an exception was thrown"],
            0,
            "Which is why a `return` inside finally can replace the value that was "
            "already on its way out."),
    ],
))


# --- 15.4 the hierarchy and multi-catch -------------------------------------

_M15.append(_jlesson(
    "m15-hierarchy", "The hierarchy, and catching several things",
    "What sits under what, and how to write more than one handler.",
    """
```
Throwable
├── Error                     ← do NOT catch (OutOfMemoryError, StackOverflowError)
└── Exception
    ├── RuntimeException      ← UNCHECKED
    │   ├── ArithmeticException
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   └── IllegalArgumentException → NumberFormatException
    └── IOException, ...      ← CHECKED (module 16)
```

**`Error` means the JVM is in trouble** — out of memory, stack overflown. You
are not meant to catch these; there is nothing sensible to do. `catch
(Throwable t)` sweeps them up along with everything else, which is why it is
almost always wrong.

**Everything under `RuntimeException` is unchecked** — the compiler does not
force you to handle it. Everything else under `Exception` is **checked**, and
module 16 is about what that obliges you to do.

## Several catch blocks

```java
try {
    ...
} catch (NumberFormatException e) {      // most specific FIRST
    ...
} catch (RuntimeException e) {           // more general after
    ...
}
```

**Order matters, and the compiler enforces it.** The first matching catch wins,
so a general handler above a specific one would make the specific one
unreachable — and Java rejects that outright rather than letting you write dead
code.

## Multi-catch

When two types want the *same* handling, one block can take both:

```java
} catch (NumberFormatException | ArithmeticException e) {
    System.out.println("bad input");
}
```

The types must not be related by inheritance — `catch (Exception | RuntimeException e)`
is a compile error, because one already covers the other. Inside the block, `e`
is effectively final and typed as the nearest common supertype.

**Catch as narrowly as you can.** `catch (Exception e)` around a large block
hides bugs: a `NullPointerException` from a typo gets quietly reported as "bad
input" and you never find it.
""",
    warmup=[
        _jq("Why must a specific catch come before a general one?",
            ["The first match wins, so a general handler first makes the specific one unreachable",
             "It is only a style convention",
             "Because of multi-catch",
             "It does not matter"],
            0,
            "Java rejects the unreachable block at compile time rather than silently "
            "ignoring it."),
        _jq("Why is `catch (NumberFormatException | RuntimeException e)` illegal?",
            ["The two are related by inheritance, so one already covers the other",
             "Multi-catch allows only two types",
             "RuntimeException cannot be caught",
             "It is legal"],
            0,
            "Multi-catch alternatives must be disjoint. NumberFormatException is already "
            "a RuntimeException."),
    ],
    exercises=[
        _je("j15-hier-multi", "One handler, two types",
            "A bad number and a division by zero should both print `bad`, but a "
            "negative divisor should be reported separately. Replace `____` with a "
            "multi-catch clause covering the two failure types.",
            _jscan("        String s = sc.nextLine();\n"
                   "        String t = sc.nextLine();\n"
                   "        try {\n"
                   "            int a = Integer.parseInt(s);\n"
                   "            int b = Integer.parseInt(t);\n"
                   "            System.out.println(a / b);\n"
                   "        } catch (NumberFormatException | ArithmeticException e) {\n"
                   '            System.out.println("bad");\n'
                   "        }"),
            "NumberFormatException | ArithmeticException",
            [_l2case("6", "3", "2"), _l2case("6", "0", "bad"),
             _l2case("x", "3", "bad"), _l2case("9", "y", "bad"),
             _l2case("-9", "3", "-3")],
            hints=["Separate the two types with a single `|`.",
                   "They must not be related by inheritance — these two are siblings, "
                   "so it is allowed.",
                   "`NumberFormatException | ArithmeticException`",
                   "`e` is typed as their nearest common supertype inside the block."],
            difficulty="Easy"),

        _je("j15-hier-specific", "Specific first",
            "Print `not a number` for a parse failure and `other` for anything else "
            "unchecked. Replace `____` with the type of the FIRST catch block.",
            _jscan("        String s = sc.nextLine();\n"
                   "        String t = sc.nextLine();\n"
                   "        try {\n"
                   "            int a = Integer.parseInt(s);\n"
                   "            int b = Integer.parseInt(t);\n"
                   "            System.out.println(a / b);\n"
                   "        } catch (NumberFormatException e) {\n"
                   '            System.out.println("not a number");\n'
                   "        } catch (RuntimeException e) {\n"
                   '            System.out.println("other");\n'
                   "        }"),
            "NumberFormatException",
            [_l2case("6", "3", "2"), _l2case("6", "0", "other"),
             _l2case("x", "3", "not a number"), _l2case("9", "y", "not a number"),
             _l2case("8", "4", "2")],
            hints=["The more specific type has to come first.",
                   "A parse failure throws `NumberFormatException`, which is a "
                   "subclass of `RuntimeException`.",
                   "Putting `RuntimeException` first would make the second block "
                   "unreachable and fail to compile.",
                   "Division by zero falls through to the general handler and prints "
                   "`other`."],
            difficulty="Easy"),

        _jfix("j15-hier-order", "The unreachable handler",
              "This does not compile: the general handler is written first, so the "
              "specific one below it can never be reached. Swap them so a parse "
              "failure prints `parse` and everything else unchecked prints `other`.",
              _jscan("        String s = sc.nextLine();\n"
                     "        String t = sc.nextLine();\n"
                     "        try {\n"
                     "            int a = Integer.parseInt(s);\n"
                     "            int b = Integer.parseInt(t);\n"
                     "            System.out.println(a / b);\n"
                     "        } catch (RuntimeException e) {\n"
                     '            System.out.println("other");\n'
                     "        } catch (NumberFormatException e) {\n"
                     '            System.out.println("parse");\n'
                     "        }"),
              _jscan("        String s = sc.nextLine();\n"
                     "        String t = sc.nextLine();\n"
                     "        try {\n"
                     "            int a = Integer.parseInt(s);\n"
                     "            int b = Integer.parseInt(t);\n"
                     "            System.out.println(a / b);\n"
                     "        } catch (NumberFormatException e) {\n"
                     '            System.out.println("parse");\n'
                     "        } catch (RuntimeException e) {\n"
                     '            System.out.println("other");\n'
                     "        }"),
              [_l2case("6", "3", "2"), _l2case("6", "0", "other"),
               _l2case("x", "3", "parse"), _l2case("9", "y", "parse"),
               _l2case("-8", "2", "-4")],
              hints=["Java refuses to compile a catch block that can never run.",
                     "`NumberFormatException` is a `RuntimeException`, so the general "
                     "one above swallows it first.",
                     "Put the specific catch first and the general one second.",
                     "The bodies stay exactly as they are — only the order changes."],
              difficulty="Easy"),

        _jch("j15-hier-report", "Report the kind", "Medium",
             "Read two lines. Print the quotient if both parse and the divisor is "
             "non-zero. Otherwise print the simple class name of whichever exception "
             "occurred, using a single catch of the common supertype.",
             _jscan("        String s = sc.nextLine();\n"
                    "        String t = sc.nextLine();\n"
                    "        try {\n"
                    "            int a = Integer.parseInt(s);\n"
                    "            int b = Integer.parseInt(t);\n"
                    "            System.out.println(a / b);\n"
                    "        } catch (RuntimeException e) {\n"
                    "            System.out.println(e.getClass().getSimpleName());\n"
                    "        }"),
             "        } catch (RuntimeException e) {\n"
             "            System.out.println(e.getClass().getSimpleName());\n"
             "        }",
             [_l2case("6", "3", "2"),
              _l2case("6", "0", "ArithmeticException"),
              _l2case("x", "3", "NumberFormatException"),
              _l2case("9", "y", "NumberFormatException"),
              _l2case("-9", "3", "-3")],
             hints=["One catch block is enough if you report the type rather than "
                    "branching on it.",
                    "`RuntimeException` covers both failures here.",
                    "`e.getClass().getSimpleName()` gives the short name without the "
                    "package.",
                    "Note that reporting the type is fine for a demonstration; real "
                    "code should usually handle the two cases differently."]),
    ],
    quiz=[
        _jq("Which of these should you almost never catch?",
            ["Error and Throwable", "RuntimeException", "IOException",
             "NumberFormatException"],
            0,
            "`Error` means the JVM is in trouble and there is nothing sensible to do. "
            "`catch (Throwable t)` sweeps those up too."),
        _jq("Why is a broad `catch (Exception e)` around a large block risky?",
            ["A genuine bug like a NullPointerException gets silently reported as an expected failure",
             "It is slower",
             "It does not compile",
             "It catches Errors as well"],
            0,
            "Catch as narrowly as you can, so that surprises stay visible instead of "
            "being disguised as handled cases."),
    ],
))


# ===========================================================================
# Capstone
# ===========================================================================

def _m15_eval(lines):
    out = []
    ok = 0
    failed = 0
    for line in lines:
        parts = line.split(" ")
        try:
            if len(parts) != 3:
                raise ValueError("shape")
            a = int(parts[0])
            b = int(parts[2])
            op = parts[1]
            if op == "/":
                v = _jdiv(a, b) if b != 0 else None
                if b == 0:
                    out.append("ArithmeticException")
                    failed += 1
                    continue
            elif op == "+":
                v = a + b
            elif op == "-":
                v = a - b
            elif op == "*":
                v = a * b
            else:
                out.append("unknown op")
                failed += 1
                continue
            out.append(str(v))
            ok += 1
        except ValueError:
            out.append("NumberFormatException")
            failed += 1
    out.append(f"ok={ok} failed={failed}")
    return _nl(*out)


def _m15_case(lines):
    return _case("\n".join([str(len(lines))] + list(lines)) + "\n",
                 _m15_eval(lines))


_M15_CAP = _jcap(
    "Robust calculator",
    """
A one-line calculator that must never crash, however badly the input is
malformed.

## Input

```
n
<line>        x n
```

Each line is meant to be `<int> <op> <int>` with `op` one of `+ - * /` and single
spaces between the three parts.

## Output

One line per input line, then a summary line.

| Situation | Print |
|---|---|
| It evaluates | the result |
| Either number will not parse, **or** the line does not have exactly three parts | `NumberFormatException` |
| Division by zero | `ArithmeticException` |
| The operator is none of `+ - * /` | `unknown op` |

Then, finally:

```
ok=<how many evaluated> failed=<how many did not>
```

## What the hidden cases check

- **A malformed line must not stop the loop.** Every line is attempted, and the
  summary counts all of them.
- **A line with the wrong number of parts is reported as `NumberFormatException`,
  not as an array error.** Reading `parts[2]` on a one-word line would throw
  `ArrayIndexOutOfBoundsException` — check `parts.length` first and treat a bad
  shape the same as a bad number.
- **`unknown op` counts as failed**, and is detected before any arithmetic.
- **Integer division truncates toward zero**, so `-7 / 2` is `-3`.
- **The summary always prints**, even when every line failed.
""",
    _jch("j15-cap-calc", "Robust calculator", "Hard",
         "Write the body of the loop where you see `____` — the parsing, the "
         "evaluation, the error reporting and the counting. Reading `n` and printing "
         "the summary are already written.",
         _jscan("        int n = Integer.parseInt(sc.nextLine());\n"
                "        int ok = 0;\n"
                "        int failed = 0;\n"
                "        for (int i = 0; i < n; i++) {\n"
                "            String line = sc.nextLine();\n"
                "            try {\n"
                '                String[] parts = line.split(" ");\n'
                "                if (parts.length != 3) {\n"
                '                    throw new NumberFormatException("shape");\n'
                "                }\n"
                "                int a = Integer.parseInt(parts[0]);\n"
                "                int b = Integer.parseInt(parts[2]);\n"
                "                String op = parts[1];\n"
                '                if (op.equals("+")) {\n'
                "                    System.out.println(a + b);\n"
                "                    ok++;\n"
                '                } else if (op.equals("-")) {\n'
                "                    System.out.println(a - b);\n"
                "                    ok++;\n"
                '                } else if (op.equals("*")) {\n'
                "                    System.out.println(a * b);\n"
                "                    ok++;\n"
                '                } else if (op.equals("/")) {\n'
                "                    System.out.println(a / b);\n"
                "                    ok++;\n"
                "                } else {\n"
                '                    System.out.println("unknown op");\n'
                "                    failed++;\n"
                "                }\n"
                "            } catch (NumberFormatException e) {\n"
                '                System.out.println("NumberFormatException");\n'
                "                failed++;\n"
                "            } catch (ArithmeticException e) {\n"
                '                System.out.println("ArithmeticException");\n'
                "                failed++;\n"
                "            }\n"
                "        }\n"
                '        System.out.println("ok=" + ok + " failed=" + failed);'),
         "            try {\n"
         '                String[] parts = line.split(" ");\n'
         "                if (parts.length != 3) {\n"
         '                    throw new NumberFormatException("shape");\n'
         "                }\n"
         "                int a = Integer.parseInt(parts[0]);\n"
         "                int b = Integer.parseInt(parts[2]);\n"
         "                String op = parts[1];\n"
         '                if (op.equals("+")) {\n'
         "                    System.out.println(a + b);\n"
         "                    ok++;\n"
         '                } else if (op.equals("-")) {\n'
         "                    System.out.println(a - b);\n"
         "                    ok++;\n"
         '                } else if (op.equals("*")) {\n'
         "                    System.out.println(a * b);\n"
         "                    ok++;\n"
         '                } else if (op.equals("/")) {\n'
         "                    System.out.println(a / b);\n"
         "                    ok++;\n"
         "                } else {\n"
         '                    System.out.println("unknown op");\n'
         "                    failed++;\n"
         "                }\n"
         "            } catch (NumberFormatException e) {\n"
         '                System.out.println("NumberFormatException");\n'
         "                failed++;\n"
         "            } catch (ArithmeticException e) {\n"
         '                System.out.println("ArithmeticException");\n'
         "                failed++;\n"
         "            }",
         [_m15_case(lines) for lines in (
             ["6 + 3", "6 / 0", "x * 2"],
             ["10 / 3"],
             ["1 ^ 2", "4 - 9"],
             ["nonsense", "7 * 0", "-7 / 2"],
             ["5 + 5", "5 / 5", "5 % 5"],
         )],
         hints=["Put the whole per-line job inside one `try`, so a failure anywhere "
                "lands in the same handlers.",
                "Split on a single space, then check `parts.length != 3` BEFORE "
                "touching `parts[2]` — otherwise you get an "
                "ArrayIndexOutOfBoundsException instead of the required message.",
                "Reporting a bad shape as a `NumberFormatException` is easiest done "
                "by throwing one yourself: "
                "`throw new NumberFormatException(\"shape\");` inside the try, where "
                "your own catch will pick it up.",
                "Compare the operator with `.equals`, never `==`.",
                "Check for an unknown operator BEFORE doing any arithmetic, and count "
                "it as failed.",
                "Division by zero throws on its own — let it, and catch "
                "`ArithmeticException`.",
                "Increment `ok` only on the paths that printed a number.",
                "The summary line is already written for you and always runs."]),
    example_io="stdin:  3\n        6 + 3\n        6 / 0\n        x * 2\n\n"
               "stdout: 9\n        ArithmeticException\n        NumberFormatException\n"
               "        ok=1 failed=2",
    rubric=[
        "One `try` covers the whole per-line job, inside the loop.",
        "`parts.length` is checked before `parts[2]` is read.",
        "A malformed line is reported as `NumberFormatException`, never as an array error.",
        "An unrecognised operator prints `unknown op` and counts as failed.",
        "Division by zero is caught rather than pre-checked, and prints `ArithmeticException`.",
        "`ok` is incremented only where a value was printed.",
        "No failure stops the loop; every line is attempted.",
        "The summary line prints exactly once, at the end.",
    ],
)


_MODULES.append(_jmod(
    15, 5, "Exception handling",
    "What an exception is, and catching it",
    "Understand the second way out of a method, catch what you can handle, clean up "
    "with `finally`, and read the hierarchy well enough to catch narrowly.",
    """
Part 5 opens on the mechanism every non-trivial Java program depends on.

Until now a method had one exit: run to the end or `return`. An exception is a
second exit that carries an object describing the failure and **unwinds the
stack** looking for someone willing to deal with it. Understanding that
propagation — and being able to read a stack trace from the top — is most of
what separates debugging from guessing.

`try`/`catch` marks a region and supplies an alternative. The traps are small
and universal: a variable declared inside the `try` is invisible outside it; a
variable declared outside must be assigned on every path, catch included; and
catching broadly disguises real bugs as expected failures.

`finally` is the block that runs whatever happens — including on the way out of
an unhandled exception, and including when the `try` returns. It is for cleanup
that must not be skipped, and the one thing you must never put in it is a
`return`.

The hierarchy then tells you what to catch: `Error` never, `RuntimeException`
and its subclasses when you have something useful to do, and — from module 16 —
checked exceptions because the compiler insists.
""",
    _M15,
    capstone=_M15_CAP,
    objectives=[
        "Describe what happens when an exception is thrown, including stack unwinding.",
        "Read a stack trace and name the line that failed.",
        "Write `try`/`catch` and explain where execution resumes afterwards.",
        "Avoid the scope and definite-assignment traps around a `try` block.",
        "Use `finally` for cleanup, and say when it runs relative to `return`.",
        "Place the exception hierarchy: Throwable, Error, Exception, RuntimeException.",
        "Order several catch blocks correctly, and use multi-catch where it fits.",
        "Choose between catching an exception and testing a condition up front.",
    ],
    why="Every program that touches input, files or a network has to decide what to do "
        "when things go wrong, and Java makes that decision explicit in the type "
        "system. Interviews ask for the hierarchy and for checked-versus-unchecked "
        "constantly; production code lives or dies on whether its handlers are narrow "
        "enough to leave real bugs visible.",
    est_minutes=300,
    glossary=[
        _jg("exception", "An object describing a failure, thrown to exit a method "
                         "abruptly and carry the details outward."),
        _jg("throw", "The act of raising an exception. Module 16 covers writing one "
                     "yourself."),
        _jg("stack unwinding", "Java exiting each method in turn, searching every "
                               "caller for a handler."),
        _jg("stack trace", "The list of frames recorded when the exception was created. "
                           "Read it from the top."),
        _jg("try block", "The region whose failures you want to handle. An ordinary "
                         "block, so variables declared in it are local to it."),
        _jg("catch block", "A handler chosen by type. Subclasses of the caught type "
                           "match too."),
        _jg("finally", "A block that runs on every path out of the try, including "
                       "uncaught exceptions and returns."),
        _jg("multi-catch", "`catch (A | B e)` — one handler for several unrelated "
                           "types."),
        _jg("Throwable", "The root of everything you can throw or catch."),
        _jg("Error", "A JVM-level failure such as OutOfMemoryError. Do not catch it."),
        _jg("RuntimeException", "The root of the unchecked exceptions - the compiler "
                                "does not force you to handle them."),
        _jg("definite assignment", "Java's rule that a local must be assigned on every "
                                   "path before it is read - which is why a catch block "
                                   "usually has to supply a default."),
    ],
    cheatsheet="""
```java
// --- the shape ----------------------------------------------------------
try {
    risky();
} catch (NumberFormatException e) {     // most specific FIRST
    ...
} catch (RuntimeException e) {          // more general after
    ...
} finally {
    cleanUp();                          // runs on EVERY path
}

// try needs at least one of catch / finally, not both.

// --- multi-catch (types must be unrelated) ------------------------------
} catch (NumberFormatException | ArithmeticException e) { ... }

// --- the exception object -----------------------------------------------
e.getMessage()                    // the text
e.getClass().getSimpleName()      // "ArithmeticException"
e.printStackTrace()               // to stderr; not for judged output

// --- scope + definite assignment ----------------------------------------
int v;                            // declare OUTSIDE if you need it after
try { v = Integer.parseInt(s); }
catch (NumberFormatException e) { v = 0; }   // every path must assign
System.out.println(v);

// --- the hierarchy -------------------------------------------------------
// Throwable
//  ├─ Error                    ← never catch
//  └─ Exception
//      ├─ RuntimeException     ← UNCHECKED
//      │   ArithmeticException, NullPointerException,
//      │   ArrayIndexOutOfBoundsException, IllegalArgumentException,
//      │   └─ NumberFormatException
//      └─ IOException, ...     ← CHECKED (module 16)

// --- traps ---------------------------------------------------------------
try { return 1; } finally { return 2; }   // returns 2 — NEVER return in finally
1 / 0        // throws ArithmeticException
1.0 / 0      // Infinity — floating point does NOT throw
catch (Exception e) { }                   // hides real bugs; catch narrowly
```
""",
    self_check=[
        "Can you describe, in order, what happens between a throw and a stack trace?",
        "Given a stack trace, can you say which line failed and who called it?",
        "Can you explain why a variable declared inside a `try` cannot be printed after it?",
        "Can you say why Java refuses to compile a read of a variable only assigned in the try?",
        "Can you state the four situations in which `finally` runs?",
        "Can you say what `try { return 1; } finally { return 2; }` returns, and why that is bad?",
        "Can you draw the hierarchy from Throwable down to NumberFormatException?",
        "Can you say why a general catch must come after a specific one?",
        "Can you give a case where testing a condition beats catching an exception?",
    ],
    review=[
        _jq("```java\ntry {\n    System.out.println(\"a\");\n    int x = 1 / 0;\n    System.out.println(\"b\");\n} catch (ArithmeticException e) {\n    System.out.println(\"c\");\n} finally {\n    System.out.println(\"d\");\n}\n```\nWhat is printed?",
            ["a c d", "a b c d", "a c", "a d"],
            0,
            "`b` is skipped because the throw abandons the rest of the try. The catch "
            "runs, then finally."),
        _jq("Which is the odd one out?",
            ["1.0 / 0", "1 / 0", "Integer.parseInt(\"x\")", "new int[2][3]"],
            0,
            "Floating-point division by zero yields Infinity rather than throwing. The "
            "other two throw; the array creation is fine but is there to make you "
            "read carefully."),
        _jq("Why does `catch (RuntimeException e)` before `catch (ArithmeticException e)` fail to compile?",
            ["The second block is unreachable, since the first already matches",
             "You may only have one catch block",
             "They are in the wrong package",
             "It compiles with a warning"],
            0,
            "Java rejects dead catch blocks outright. Specific first, general after."),
        _jq("In the capstone, why check `parts.length` before reading `parts[2]`?",
            ["Otherwise a malformed line throws ArrayIndexOutOfBoundsException instead of the required NumberFormatException",
             "For speed",
             "Because split can return null",
             "It is not necessary"],
            0,
            "The brief specifies what a bad shape must report, so the array access has "
            "to be guarded rather than allowed to fail on its own."),
    ],
    milestone="You can keep a program running through bad input, clean up reliably with "
              "`finally`, and read a stack trace well enough to find the real cause "
              "rather than guessing.",
))
