# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Module 16 practice - throwing, checked exceptions, and resources.
#
# exec()-ed by tools/java_course.py; fills `_PRACTICE[16]`.
#
# Two program shapes are used:
#   _p16meth  - the blanked region is a METHOD beside a given `main` (module 9's
#               shape), for `throw` and `throws` exercises.
#   _p16types - the blanked region is one or more TOP-LEVEL types above `main`
#               (module 11's shape), for custom exceptions and AutoCloseable.
#
# File I/O is Part 9, so every resource here is a hand-written AutoCloseable -
# which is better anyway, because the closing order shows up in the output.
# ---------------------------------------------------------------------------


_RD_V = "        int v = sc.nextInt();\n"
_RD_VW = "        int v = sc.nextInt();\n        int w = sc.nextInt();\n"
_RD_S16 = "        String s = sc.next();\n"


def _p16meth(eid, title, difficulty, prompt, helpers, body, tests, hints,
             read=_RD_V):
    helpers = helpers.strip("\n")
    members = (helpers + "\n\n" + _MAIN_SIG + "\n"
               + "        Scanner sc = new Scanner(System.in);\n"
               + read + body.rstrip("\n") + "\n    }")
    return _jch(eid, title, difficulty, prompt, _jcls(members), helpers,
                tests, hints)


def _p16types(eid, title, difficulty, prompt, types, body, tests, hints):
    types = types.strip("\n")
    return _jch(eid, title, difficulty, prompt, _joop(types, body), types,
                tests, hints)


# --- Family A - throwing deliberately ----------------------------------------

_P16_A = _jfam(
    "p16-throw", "Throwing deliberately",
    "Refuse the call rather than inventing an answer.",
    """
Module 12 gave three responses to a bad argument: **clamp**, **reject**, or
**throw**. The third one is now available:

```java
static int sqrtFloor(int n) {
    if (n < 0) {
        throw new IllegalArgumentException("negative: " + n);
    }
    ...
}
```

**Throw when the call itself is a mistake** — when there is no sensible value to
return and continuing would hide a bug. Returning `-1` instead is the trap:
`-1` is indistinguishable from a real answer, so the mistake travels silently
until it surfaces somewhere unrelated.

**The two standard types:**

| Type | Says |
|---|---|
| `IllegalArgumentException` | this argument is wrong |
| `IllegalStateException` | the object is not in a state where this call makes sense |

Both are unchecked, which is right: both report a programming error rather than
a condition to recover from.

**Always include the offending value in the message.** The message is often the
only thing that survives into a log, and `"negative"` helps far less than
`"negative: -7"`.

**Check first, then work.** Validate at the top of the method and throw before
anything is computed or mutated — otherwise a rejected call can still leave the
object half-changed, which is exactly the invariant violation module 12 was
about.

**No `return` is needed after a `throw`.** That path cannot continue, so the
compiler's definite-return analysis is already satisfied.
""",
    [
        _p16meth("j16-pr-negative", "Refuse a negative", "Easy",
                 "Write `static int square(int n)` which throws an "
                 "`IllegalArgumentException` with the message `negative: <n>` for a "
                 "negative argument, and otherwise returns `n * n`.",
                 """
    static int square(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("negative: " + n);
        }
        return n * n;
    }
""",
                 """        try {
            System.out.println(square(v));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                 [_case(str(v), v * v if v >= 0 else f"negative: {v}")
                  for v in (5, -3, 0, -1, 12)],
                 ["Validate at the top, before computing anything.",
                  "`throw new IllegalArgumentException(\"negative: \" + n);`",
                  "Include the value in the message — that is what makes it useful.",
                  "No `return` after the throw; that path cannot continue.",
                  "Zero is not negative, so it returns `0`."]),

        _p16meth("j16-pr-range", "Only within range", "Easy",
                 "Write `static int percent(int n)` which throws an "
                 "`IllegalArgumentException` with the message `out of range: <n>` "
                 "unless `n` is between `0` and `100` inclusive, and otherwise returns "
                 "`n`.",
                 """
    static int percent(int n) {
        if (n < 0 || n > 100) {
            throw new IllegalArgumentException("out of range: " + n);
        }
        return n;
    }
""",
                 """        try {
            System.out.println(percent(v));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                 [_case(str(v), v if 0 <= v <= 100 else f"out of range: {v}")
                  for v in (50, -1, 101, 0, 100)],
                 ["Both bounds are INCLUSIVE, so `0` and `100` are accepted.",
                  "Combine the two failing conditions with `||`.",
                  "Cases four and five sit exactly on the boundaries and must "
                  "succeed.",
                  "One throw covers both directions, since the message is the same "
                  "shape."]),

        _p16meth("j16-pr-divide", "A better message than the JVM's", "Easy",
                 "Write `static int divide(int a, int b)` which throws an "
                 "`IllegalArgumentException` with the message `divide by zero` when `b` "
                 "is zero, and otherwise returns `a / b`.",
                 """
    static int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("divide by zero");
        }
        return a / b;
    }
""",
                 """        try {
            System.out.println(divide(v, w));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                 [_case(f"{x} {y}", _jdiv(x, y) if y != 0 else "divide by zero")
                  for (x, y) in ((6, 3), (6, 0), (-9, 3), (0, 0), (-7, 2))],
                 ["Checking first gives a far better message than letting the JVM "
                  "throw `/ by zero`.",
                  "It also lets you choose the TYPE, which is what callers catch on.",
                  "Return `a / b` only after the check.",
                  "Integer division truncates toward zero, so `-7 / 2` is `-3`."],
                 read=_RD_VW),

        _p16types("j16-pr-state", "Wrong state, not wrong argument", "Medium",
                  "Write a `Gate` class with `private boolean open`, a `void open()` "
                  "that throws an `IllegalStateException` with the message "
                  "`already open` if it is already open, and `boolean isOpen()`.",
                  """
class Gate {
    private boolean open;

    void open() {
        if (open) {
            throw new IllegalStateException("already open");
        }
        open = true;
    }

    boolean isOpen() {
        return open;
    }
}
""",
                  """        int k = sc.nextInt();
        Gate g = new Gate();
        try {
            for (int i = 0; i < k; i++) {
                g.open();
            }
            System.out.println("opened " + k);
        } catch (IllegalStateException e) {
            System.out.println(e.getMessage());
        }""",
                  [_case(str(k), f"opened {k}" if k <= 1 else "already open")
                   for k in (1, 2, 0, 3, 5)],
                  ["`open()` takes no argument, so nothing about the ARGUMENT can be "
                   "wrong.",
                   "What is wrong is the object's condition, which is "
                   "`IllegalStateException`.",
                   "Check before setting the flag.",
                   "A `k` of `0` never calls it and a `k` of `1` succeeds; anything "
                   "more fails on the second call."]),

        _p16meth("j16-pr-validate-array", "Guard the index yourself", "Medium",
                 "Write `static int at(int[] a, int i)` which throws an "
                 "`IllegalArgumentException` with the message `bad index: <i>` when `i` "
                 "is outside the array, and otherwise returns `a[i]`.",
                 """
    static int at(int[] a, int i) {
        if (i < 0 || i >= a.length) {
            throw new IllegalArgumentException("bad index: " + i);
        }
        return a[i];
    }
""",
                 """        int i = sc.nextInt();
        try {
            System.out.println(at(a, i));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                 [_akcase(a, i, a[i] if 0 <= i < len(a) else f"bad index: {i}")
                  for (a, i) in (([3, 1, 4], 1), ([3, 1, 4], 5), ([7], 0),
                                 ([3, 1, 4], -1), ([3, 1, 4], 3))],
                 ["Both ends need checking: negative, and at or past the length.",
                  "`i >= a.length` rather than `>` — the last valid index is "
                  "`length - 1`.",
                  "Throwing your own type with a clear message beats letting "
                  "`ArrayIndexOutOfBoundsException` escape, because you control the "
                  "wording and the type.",
                  "Case five uses an index exactly equal to the length."],
                 read=_RD_ARR),
    ])


# --- Family B - checked, and throws ------------------------------------------

_P16_B = _jfam(
    "p16-checked", "Checked exceptions and `throws`",
    "The one place the compiler makes you decide.",
    """
```
Throwable
├── Error                     unchecked
└── Exception                 CHECKED
    └── RuntimeException      unchecked
```

**Everything under `Exception` is checked, except the `RuntimeException`
subtree.** A checked exception obliges every caller to make a choice:

```java
static void risky() throws Exception { ... }     // DECLARES it

static void pass() throws Exception { risky(); } // 1. propagate
static void deal() {                             // 2. handle
    try { risky(); } catch (Exception e) { }
}
```

Do neither and the compiler says *unreported exception … must be caught or
declared to be thrown*.

**`throw` raises; `throws` declares.** One letter apart, completely different
jobs. `throw` is a statement in the body; `throws` is part of the signature.

**The obligation only appears at a method boundary.** A checked exception thrown
and caught inside the *same* method needs no `throws` clause at all — which is
why the compile error can seem to come and go as you refactor.

**Handling makes the signature clean.** A method that catches everything it can
throw declares nothing, and its callers need no handler. That is often exactly
what you want at the edge of a subsystem.

**Which to choose:** checked for what a caller could reasonably recover from and
did not cause (a missing file, a failed request); unchecked for programming
errors (a bad argument, an impossible state). Most modern Java libraries lean
unchecked.
""",
    [
        _p16meth("j16-pr-declare", "Declare it", "Easy",
                 "Write `static int risky(int n) throws Exception` which throws a "
                 "checked `Exception` with the message `negative` for a negative "
                 "argument, and otherwise returns `n * 2`.",
                 """
    static int risky(int n) throws Exception {
        if (n < 0) {
            throw new Exception("negative");
        }
        return n * 2;
    }
""",
                 """        try {
            System.out.println(risky(v));
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }""",
                 [_case(str(v), v * 2 if v >= 0 else "negative")
                  for v in (5, -3, 0, -1, 21)],
                 ["`Exception` itself is checked, so the signature must say `throws "
                  "Exception`.",
                  "The clause goes after the parameter list, before the brace.",
                  "Note the `s`: `throws` declares, `throw` raises. Both appear in "
                  "this method.",
                  "`main` already catches it."]),

        _p16meth("j16-pr-propagate", "Pass it up", "Medium",
                 "`risky` is given. Write `static int middle(int n)` which calls it, "
                 "adds `1` to the result, and does NOT handle the failure — so it must "
                 "declare the checked exception itself.",
                 """
    static int risky(int n) throws Exception {
        if (n < 0) {
            throw new Exception("negative");
        }
        return n * 2;
    }

    static int middle(int n) throws Exception {
        return risky(n) + 1;
    }
""",
                 """        try {
            System.out.println(middle(v));
        } catch (Exception e) {
            System.out.println("caught " + e.getMessage());
        }""",
                 [_case(str(v), v * 2 + 1 if v >= 0 else "caught negative")
                  for v in (5, -3, 0, -1, 20)],
                 ["`middle` takes the propagate option, so it needs the same `throws "
                  "Exception` clause.",
                  "Without it: *unreported exception java.lang.Exception; must be "
                  "caught or declared to be thrown*.",
                  "It does not catch anything — the exception passes straight through "
                  "to `main`.",
                  "Write BOTH methods; `risky` is shown in the prompt so you can copy "
                  "it."]),

        _p16meth("j16-pr-handle", "Handle it instead", "Medium",
                 "`risky` is given. Write `static int safe(int n)` which calls it and "
                 "returns `0` instead of letting the checked exception escape — so "
                 "`safe` declares no `throws` at all.",
                 """
    static int risky(int n) throws Exception {
        if (n < 0) {
            throw new Exception("negative");
        }
        return n * 2;
    }

    static int safe(int n) {
        try {
            return risky(n);
        } catch (Exception e) {
            return 0;
        }
    }
""",
                 """        System.out.println(safe(v));""",
                 [_case(str(v), v * 2 if v >= 0 else 0)
                  for v in (5, -3, 0, -1, 21)],
                 ["`safe` takes the handle option, so its signature stays clean.",
                  "That is what lets `main` call it with no try/catch at all.",
                  "Return from inside the try, and return the fallback from the "
                  "catch.",
                  "Every path returns, which the compiler checks.",
                  "Write both methods."]),

        _p16meth("j16-pr-unchecked-nodeclare", "Unchecked needs no clause", "Medium",
                 "Write `static int strict(int n)` which throws an "
                 "`IllegalArgumentException` with the message `negative` for a negative "
                 "argument and otherwise returns `n * 2` — with **no** `throws` clause, "
                 "because the type is unchecked.",
                 """
    static int strict(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("negative");
        }
        return n * 2;
    }
""",
                 """        try {
            System.out.println(strict(v));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                 [_case(str(v), v * 2 if v >= 0 else "negative")
                  for v in (5, -3, 0, -1, 21)],
                 ["`IllegalArgumentException` is a `RuntimeException`, so it is "
                  "unchecked.",
                  "The compiler imposes nothing: no `throws` clause, and callers need "
                  "no handler.",
                  "Compare with the first variant in this family — the only "
                  "difference is which part of the hierarchy the type sits in.",
                  "`main` catches it anyway, because it wants to report the message."]),

        _p16meth("j16-pr-inside", "Thrown and caught in one method", "Hard",
                 "Write `static int localOnly(int n)` which throws a checked "
                 "`Exception` for a negative argument AND catches it in the same "
                 "method, returning `-1`. It must need no `throws` clause.",
                 """
    static int localOnly(int n) {
        try {
            if (n < 0) {
                throw new Exception("negative");
            }
            return n * 2;
        } catch (Exception e) {
            return -1;
        }
    }
""",
                 """        System.out.println(localOnly(v));""",
                 [_case(str(v), v * 2 if v >= 0 else -1)
                  for v in (5, -3, 0, -1, 21)],
                 ["A checked exception only forces a `throws` clause when it CROSSES "
                  "a method boundary.",
                  "Thrown and caught inside the same method, the compiler is already "
                  "satisfied.",
                  "So the whole body goes inside one try, with the catch returning "
                  "`-1`.",
                  "That is why the compile error seems to appear and disappear as you "
                  "move code between methods.",
                  "Both paths return, so no definite-assignment question arises."]),
    ])


# --- Family C - custom types --------------------------------------------------

_P16_C = _jfam(
    "p16-custom", "Your own exception types",
    "A class, a parent, and a message passed up.",
    """
```java
class TooSmallException extends RuntimeException {
    TooSmallException(String message) {
        super(message);
    }
}
```

That is the minimum: **extend**, and pass the message up with `super`. The
parent you pick decides everything else:

| Extend | Result |
|---|---|
| `RuntimeException` | unchecked — no caller is forced to handle it |
| `Exception` | checked — every caller must catch or declare |

**`super(message)` must be the first statement**, and without it `getMessage()`
returns `null`.

**Why a distinct type at all?** Because `catch` matches on **type**. A distinct
type lets one handler deal with insufficient funds and another with a malformed
command — without anyone comparing message strings, which is fragile and
untestable.

**Carry data, not just a sentence.** An exception is an object, so it may have
fields:

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

Now the handler can act on the number instead of re-deriving it.

**Name it ending in `Exception`.** Universal convention, and breaking it reads
badly at every call site.

**Do not invent one per method.** A custom type earns its place when a caller
would realistically catch *that case specifically*.
""",
    [
        _p16types("j16-pr-custom-basic", "Declare one", "Easy",
                  "Write an unchecked `TooSmallException` whose constructor takes a "
                  "message and passes it up. `main` throws it for values below `10`.",
                  """
class TooSmallException extends RuntimeException {
    TooSmallException(String message) {
        super(message);
    }
}
""",
                  """        int v = sc.nextInt();
        try {
            if (v < 10) {
                throw new TooSmallException("too small: " + v);
            }
            System.out.println(v);
        } catch (TooSmallException e) {
            System.out.println(e.getMessage());
        }""",
                  [_case(str(v), v if v >= 10 else f"too small: {v}")
                   for v in (15, 3, 10, 0, -5)],
                  ["Extend `RuntimeException` to make it unchecked.",
                   "The constructor takes a `String` and calls `super(message);` as "
                   "its first statement.",
                   "Without that call `getMessage()` would return `null`.",
                   "The class name ends in `Exception`, by convention."]),

        _p16types("j16-pr-custom-checked", "Make it checked", "Medium",
                  "Write a CHECKED `TooSmallException` — extending `Exception` rather "
                  "than `RuntimeException`. `main` throws and catches it in the same "
                  "block, so no `throws` clause is needed anywhere.",
                  """
class TooSmallException extends Exception {
    TooSmallException(String message) {
        super(message);
    }
}
""",
                  """        int v = sc.nextInt();
        try {
            if (v < 10) {
                throw new TooSmallException("too small: " + v);
            }
            System.out.println(v);
        } catch (TooSmallException e) {
            System.out.println(e.getMessage());
        }""",
                  [_case(str(v), v if v >= 10 else f"too small: {v}")
                   for v in (15, 3, 10, 0, -5)],
                  ["Extending `Exception` directly makes the type checked.",
                   "It compiles here because the throw and the catch are in the SAME "
                   "method — the obligation only appears at a method boundary.",
                   "Move the throw into a helper and `main` would suddenly need a "
                   "`throws` clause on it.",
                   "Only the `extends` clause differs from the previous variant."]),

        _p16types("j16-pr-custom-data", "Carry the number", "Hard",
                  "Write an unchecked `ShortfallException` holding a "
                  "`private final int shortfall`, with the message `short by "
                  "<shortfall>` and an `int getShortfall()`. `main` prints both the "
                  "message and the number.",
                  """
class ShortfallException extends RuntimeException {
    private final int shortfall;

    ShortfallException(int shortfall) {
        super("short by " + shortfall);
        this.shortfall = shortfall;
    }

    int getShortfall() {
        return shortfall;
    }
}
""",
                  """        int have = sc.nextInt();
        int want = sc.nextInt();
        try {
            if (want > have) {
                throw new ShortfallException(want - have);
            }
            System.out.println(have - want);
        } catch (ShortfallException e) {
            System.out.println(e.getMessage());
            System.out.println(e.getShortfall());
        }""",
                  [_case(f"{h} {w}", h - w if w <= h
                         else _nl(f"short by {w - h}", w - h))
                   for (h, w) in ((100, 30), (50, 80), (10, 10), (0, 5), (7, 100))],
                  ["An exception is an ordinary object: fields, constructor, getters.",
                   "`super(\"short by \" + shortfall);` must come FIRST, before the "
                   "field assignment.",
                   "The field is `private final`, like any other well-encapsulated "
                   "class.",
                   "The handler can now use the number directly rather than parsing "
                   "the message."]),

        _p16types("j16-pr-two-types", "Two types, two handlers", "Hard",
                  "Write TWO unchecked exception types, `NegativeException` and "
                  "`TooBigException`, each taking a message. `main` throws the first "
                  "for a negative value and the second for anything above `100`, and "
                  "catches them separately — printing `low: <v>` or `high: <v>`.",
                  """
class NegativeException extends RuntimeException {
    NegativeException(String message) {
        super(message);
    }
}

class TooBigException extends RuntimeException {
    TooBigException(String message) {
        super(message);
    }
}
""",
                  """        int v = sc.nextInt();
        try {
            if (v < 0) {
                throw new NegativeException("low: " + v);
            }
            if (v > 100) {
                throw new TooBigException("high: " + v);
            }
            System.out.println(v);
        } catch (NegativeException e) {
            System.out.println(e.getMessage());
        } catch (TooBigException e) {
            System.out.println(e.getMessage());
        }""",
                  [_case(str(v), v if 0 <= v <= 100
                         else (f"low: {v}" if v < 0 else f"high: {v}"))
                   for v in (50, -3, 101, 0, 100)],
                  ["Two separate classes, each extending `RuntimeException`.",
                   "They are siblings, so neither hides the other and the catch order "
                   "is free.",
                   "This is the whole reason for distinct types: `catch` matches on "
                   "type, so the two cases can be handled independently.",
                   "A single type with different messages would force the handler to "
                   "inspect strings.",
                   "Cases four and five sit on the boundaries and must succeed."]),

        _p16types("j16-pr-supertype-catch", "Catch a family", "Hard",
                  "Write an unchecked `AppException`, then `NegativeException` and "
                  "`TooBigException` both extending **`AppException`**. `main` throws "
                  "the right one and catches the common supertype once.",
                  """
class AppException extends RuntimeException {
    AppException(String message) {
        super(message);
    }
}

class NegativeException extends AppException {
    NegativeException(String message) {
        super(message);
    }
}

class TooBigException extends AppException {
    TooBigException(String message) {
        super(message);
    }
}
""",
                  """        int v = sc.nextInt();
        try {
            if (v < 0) {
                throw new NegativeException("low: " + v);
            }
            if (v > 100) {
                throw new TooBigException("high: " + v);
            }
            System.out.println(v);
        } catch (AppException e) {
            System.out.println(e.getClass().getSimpleName() + " " + e.getMessage());
        }""",
                  [_case(str(v), v if 0 <= v <= 100
                         else (f"NegativeException low: {v}" if v < 0
                               else f"TooBigException high: {v}"))
                   for v in (50, -3, 101, 0, 100)],
                  ["Three classes: a base extending `RuntimeException`, and two "
                   "extending the base.",
                   "Each constructor passes the message up with `super(message)` — "
                   "the chain runs all the way to `Throwable`.",
                   "Catching `AppException` catches both subclasses, exactly as the "
                   "subtree rule says.",
                   "That is how real applications organise failures: one family per "
                   "subsystem, so a caller can be as specific or as general as it "
                   "likes.",
                   "`getSimpleName()` still reports the ACTUAL type, which is what "
                   "makes the output differ."]),
    ])


# --- Family D - try-with-resources -------------------------------------------

_P16_D = _jfam(
    "p16-resources", "try-with-resources",
    "Closing without a `finally`.",
    """
```java
try (Res r = new Res()) {
    r.use();
}                               // close() is called automatically
```

The resource is declared in the parentheses, and Java closes it when the block
ends — normally, by exception, or by `return`. It replaces this entirely:

```java
Res r = null;
try { r = new Res(); r.use(); }
finally { if (r != null) r.close(); }
```

**The type must implement `AutoCloseable`**, an interface with one method:

```java
class Res implements AutoCloseable {
    @Override
    public void close() { System.out.println("closed"); }
}
```

`AutoCloseable.close()` is declared `throws Exception`, but an implementation may
declare a **narrower** clause — including none. That is module 13's rule (an
override may restrict, never broaden) put to work: with no `throws`, callers
need no handler.

**Several resources are separated by semicolons**, and they are closed in
**reverse order** — the last opened is released first, because it may depend on
the earlier one.

**Closing happens before any `catch` or `finally` on the same `try`.** So the
output order for a failing block is: body up to the throw, close, catch,
finally.

**The resource variable is implicitly final.** You cannot reassign it inside the
block — Java has to know what it is going to close.
""",
    [
        _p16types("j16-pr-res-basic", "Let it close itself", "Easy",
                  "Write a `Res` class implementing `AutoCloseable`, with "
                  "`void use(int n)` printing `using <n>` and `close()` printing "
                  "`closed`. `main` opens one with try-with-resources.",
                  """
class Res implements AutoCloseable {
    void use(int n) {
        System.out.println("using " + n);
    }

    @Override
    public void close() {
        System.out.println("closed");
    }
}
""",
                  """        int v = sc.nextInt();
        try (Res r = new Res()) {
            r.use(v);
        }
        System.out.println("done");""",
                  [_case(str(v), _nl(f"using {v}", "closed", "done"))
                   for v in (5, 0, -3, 100, 1)],
                  ["`implements AutoCloseable` is what makes it usable in the "
                   "parentheses.",
                   "`close()` must be `public`, because interface methods are.",
                   "Declaring no `throws` clause on `close()` is allowed and spares "
                   "`main` a handler.",
                   "`closed` prints before `done`, because the resource is released "
                   "as the block ends."]),

        _p16types("j16-pr-res-named", "Which one closed", "Easy",
                  "Same idea, but `Res` takes a name in its constructor and prints "
                  "`open <name>` there and `close <name>` in `close()`.",
                  """
class Res implements AutoCloseable {
    private final String name;

    Res(String name) {
        this.name = name;
        System.out.println("open " + name);
    }

    @Override
    public void close() {
        System.out.println("close " + name);
    }
}
""",
                  """        String nm = sc.next();
        try (Res r = new Res(nm)) {
            System.out.println("using " + nm);
        }""",
                  [_case(w, _nl(f"open {w}", f"using {w}", f"close {w}"))
                   for w in ("a", "file", "db", "x", "sock")],
                  ["The constructor prints as a side effect, which is how the opening "
                   "order becomes visible.",
                   "Store the name in a `private final` field.",
                   "`close()` reads the same field.",
                   "Three lines in a fixed order: open, use, close."]),

        _p16types("j16-pr-res-order", "Reverse closing order", "Medium",
                  "Same `Res` class. `main` opens two in one try-with-resources — they "
                  "close in REVERSE order, so the second name is released first.",
                  """
class Res implements AutoCloseable {
    private final String name;

    Res(String name) {
        this.name = name;
        System.out.println("open " + name);
    }

    @Override
    public void close() {
        System.out.println("close " + name);
    }
}
""",
                  """        String x = sc.next();
        String y = sc.next();
        try (Res a = new Res(x); Res b = new Res(y)) {
            System.out.println("using " + x + " " + y);
        }""",
                  [_case(f"{x} {y}", _nl(f"open {x}", f"open {y}",
                                         f"using {x} {y}", f"close {y}", f"close {x}"))
                   for (x, y) in (("a", "b"), ("db", "file"), ("x", "y"),
                                  ("one", "two"), ("p", "q"))],
                  ["Separate the two declarations with a SEMICOLON inside the "
                   "parentheses.",
                   "They are constructed left to right, so the `open` lines follow the "
                   "input order.",
                   "They are closed in reverse, so the `close` lines are the other way "
                   "round.",
                   "That ordering exists because the later resource may depend on the "
                   "earlier one.",
                   "You are writing only the `Res` class; `main` is given."]),

        _p16types("j16-pr-res-exception", "Closed even when it fails", "Hard",
                  "`Res.use(int n)` divides `100` by `n`, so `0` makes it throw. Write "
                  "`Res` so that a failing block still closes — and note that closing "
                  "happens BEFORE the catch runs.",
                  """
class Res implements AutoCloseable {
    void use(int n) {
        System.out.println("using " + (100 / n));
    }

    @Override
    public void close() {
        System.out.println("closed");
    }
}
""",
                  """        int v = sc.nextInt();
        try (Res r = new Res()) {
            r.use(v);
        } catch (ArithmeticException e) {
            System.out.println("error");
        }""",
                  [_case(str(v), _nl(f"using {_jdiv(100, v)}", "closed") if v != 0
                         else _nl("closed", "error"))
                   for v in (5, 0, -4, 100, 2)],
                  ["`use` prints `using ` followed by `100 / n`.",
                   "When `n` is zero it throws before printing anything.",
                   "try-with-resources closes on EVERY path, so `closed` appears "
                   "either way.",
                   "Closing happens before the catch block runs, which is why the "
                   "failing case prints `closed` and then `error`.",
                   "You write only the class; `main` is given."]),

        _p16types("j16-pr-res-counter", "A resource that reports", "Hard",
                  "Write a `Counter` class implementing `AutoCloseable` with "
                  "`private int used`, a `void use()` that increments it, and a "
                  "`close()` that prints `used=<count>`. `main` uses it `k` times "
                  "inside a try-with-resources.",
                  """
class Counter implements AutoCloseable {
    private int used;

    void use() {
        used = used + 1;
    }

    @Override
    public void close() {
        System.out.println("used=" + used);
    }
}
""",
                  """        int k = sc.nextInt();
        try (Counter c = new Counter()) {
            for (int i = 0; i < k; i++) {
                c.use();
            }
            System.out.println("finished");
        }""",
                  [_case(str(k), _nl("finished", f"used={k}"))
                   for k in (3, 0, 1, 10, 5)],
                  ["The field starts at `0` by default; no constructor is needed.",
                   "`use()` increments and returns nothing.",
                   "`close()` prints the total — and it runs after the block body, so "
                   "`finished` comes first.",
                   "A `k` of `0` never calls `use`, and the resource still closes and "
                   "reports `used=0`.",
                   "This is the shape of a resource that reports statistics on "
                   "release."]),
    ])


# --- Family E - choosing the response ----------------------------------------

_P16_E = _jfam(
    "p16-choose", "Clamp, reject, or throw",
    "Three answers to a bad argument, and when each is right.",
    """
Module 12 named the choice; now all three are available.

| Response | Behaviour | Right when |
|---|---|---|
| **Clamp** | silently adjust to the nearest legal value | out-of-range is expected and harmless — volume, brightness |
| **Reject** | change nothing, return `false` | the caller can reasonably handle refusal, and refusal is routine |
| **Throw** | raise an exception | the call is a programming error, and continuing would hide a bug |

The wrong answer is the fourth one: accept the bad value and let the field go
bad. That turns a small mistake at the call site into a corrupted object that
fails somewhere else entirely.

**How to choose, in one question:** *could a reasonable caller pass this?*

- Yes, routinely → clamp or reject.
- Only by mistake → throw.

**Sentinel returns are the trap.** `return -1` looks like rejecting, but the
sentinel is indistinguishable from a real answer whenever `-1` is in range. A
`boolean` return says "did it work" without ambiguity; an exception cannot be
ignored by accident at all.

**Whichever you choose, be consistent within a class.** A class where one setter
clamps and another throws is confusing to use, and the confusion shows up as
bugs in the caller rather than in the class.

**And validate before mutating.** A method that half-updates and then throws
leaves the object in a state its invariant forbids — which is worse than either
outcome.
""",
    [
        _p16types("j16-pr-clamp", "Clamp it", "Easy",
                  "Write a `Volume` class with `private int level` held between `0` and "
                  "`100`. Both the constructor and `void set(int v)` CLAMP out of range "
                  "values. Add `int get()`.",
                  """
class Volume {
    private int level;

    Volume(int level) {
        this.level = clamp(level);
    }

    void set(int v) {
        level = clamp(v);
    }

    int get() {
        return level;
    }

    private int clamp(int v) {
        if (v < 0) {
            return 0;
        }
        if (v > 100) {
            return 100;
        }
        return v;
    }
}
""",
                  """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Volume vol = new Volume(a1);
        System.out.println(vol.get());
        vol.set(b1);
        System.out.println(vol.get());""",
                  [_case(f"{x} {y}", _nl(min(max(x, 0), 100), min(max(y, 0), 100)))
                   for (x, y) in ((50, 150), (-10, 20), (0, 100), (200, -1), (7, 7))],
                  ["Write the rule ONCE in a `private` helper and call it from both "
                   "places.",
                   "Duplicating it in the constructor and the setter is how the two "
                   "drift apart later.",
                   "Clamping is silent: `150` becomes `100` with no complaint.",
                   "That is right for a volume, where an out-of-range request is a "
                   "reasonable thing for a caller to make."]),

        _p16types("j16-pr-reject", "Reject it", "Medium",
                  "Write an `Age` class with `private int years`. The constructor "
                  "clamps a negative to `0`; `boolean set(int v)` REJECTS anything "
                  "outside `0..150`, returning `false` and changing nothing. Add "
                  "`int get()`.",
                  """
class Age {
    private int years;

    Age(int years) {
        if (years < 0) {
            this.years = 0;
        } else {
            this.years = years;
        }
    }

    boolean set(int v) {
        if (v < 0 || v > 150) {
            return false;
        }
        years = v;
        return true;
    }

    int get() {
        return years;
    }
}
""",
                  """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        Age age = new Age(a1);
        System.out.println(age.set(b1));
        System.out.println(age.get());""",
                  [_case(f"{x} {y}",
                         (lambda start: _nl(_jbool(0 <= y <= 150),
                                            y if 0 <= y <= 150 else start))(max(x, 0)))
                   for (x, y) in ((30, 40), (30, 200), (-5, 10), (0, -1), (99, 150))],
                  ["Rejecting means returning `false` and leaving the field exactly as "
                   "it was.",
                   "Check the range BEFORE assigning, never after.",
                   "The boolean return is unambiguous in a way a sentinel value would "
                   "not be.",
                   "Case five proposes exactly `150`, which is inside the inclusive "
                   "range."]),

        _p16types("j16-pr-throw-it", "Throw it", "Medium",
                  "Write a `Percent` class with `private int value`. Both the "
                  "constructor and `void set(int v)` THROW an "
                  "`IllegalArgumentException` with the message `bad: <v>` for anything "
                  "outside `0..100`. Add `int get()`.",
                  """
class Percent {
    private int value;

    Percent(int value) {
        this.value = check(value);
    }

    void set(int v) {
        value = check(v);
    }

    int get() {
        return value;
    }

    private int check(int v) {
        if (v < 0 || v > 100) {
            throw new IllegalArgumentException("bad: " + v);
        }
        return v;
    }
}
""",
                  """        int a1 = sc.nextInt();
        int b1 = sc.nextInt();
        try {
            Percent p = new Percent(a1);
            System.out.println(p.get());
            p.set(b1);
            System.out.println(p.get());
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }""",
                  [_case(f"{x} {y}",
                         (f"bad: {x}" if not (0 <= x <= 100)
                          else (_nl(x, f"bad: {y}") if not (0 <= y <= 100)
                                else _nl(x, y))))
                   for (x, y) in ((50, 80), (150, 20), (10, -1), (0, 100), (7, 7))],
                  ["One `private` helper does the checking for both entry points, as "
                   "before — but this time it throws instead of adjusting.",
                   "It returns the value when valid, so `this.value = check(value);` "
                   "reads naturally.",
                   "A failing constructor means no object is ever created, which is "
                   "the strongest guarantee of the three.",
                   "Case two fails in the constructor, so only one line is printed.",
                   "Case three constructs fine and fails on the `set`."]),

        _p16types("j16-pr-no-half-update", "Do not half-update", "Hard",
                  "Write a `Pair` class with `private int a, b` and "
                  "`void setBoth(int newA, int newB)` which throws an "
                  "`IllegalArgumentException` with the message `negative` if EITHER "
                  "value is negative — validating both before assigning either, so a "
                  "rejected call changes nothing. Add `String show()` returning "
                  "`<a>,<b>`.",
                  """
class Pair {
    private int a;
    private int b;

    Pair(int a, int b) {
        this.a = a;
        this.b = b;
    }

    void setBoth(int newA, int newB) {
        if (newA < 0 || newB < 0) {
            throw new IllegalArgumentException("negative");
        }
        this.a = newA;
        this.b = newB;
    }

    String show() {
        return a + "," + b;
    }
}
""",
                  """        int p = sc.nextInt();
        int q = sc.nextInt();
        Pair pair = new Pair(1, 2);
        try {
            pair.setBoth(p, q);
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }
        System.out.println(pair.show());""",
                  [_case(f"{x} {y}",
                         f"{x},{y}" if x >= 0 and y >= 0 else _nl("negative", "1,2"))
                   for (x, y) in ((3, 4), (-1, 4), (3, -4), (0, 0), (-1, -1))],
                  ["Validate BOTH arguments first, then assign both.",
                   "Assigning `a` and then discovering `b` is bad would leave the "
                   "object half-updated — the exact invariant violation module 12 "
                   "warned about.",
                   "Cases two and three have one bad value each, and the pair must "
                   "still read `1,2` afterwards.",
                   "`0` is not negative, so case four succeeds."]),

        _p16types("j16-pr-sentinel-trap", "Why a sentinel is not enough", "Hard",
                  "Write a `Store` class with `private int stock` and "
                  "`int take(int n)` which returns the number actually taken — but "
                  "throws an `IllegalArgumentException` with the message `bad amount` "
                  "when `n` is not positive, because `-1` would be indistinguishable "
                  "from a real answer. Taking more than the stock takes all of it. Add "
                  "`int stock()`.",
                  """
class Store {
    private int stock;

    Store(int stock) {
        this.stock = stock;
    }

    int take(int n) {
        if (n <= 0) {
            throw new IllegalArgumentException("bad amount");
        }
        int taken = n;
        if (taken > stock) {
            taken = stock;
        }
        stock = stock - taken;
        return taken;
    }

    int stock() {
        return stock;
    }
}
""",
                  """        int have = sc.nextInt();
        int want = sc.nextInt();
        Store st = new Store(have);
        try {
            System.out.println(st.take(want));
        } catch (IllegalArgumentException e) {
            System.out.println(e.getMessage());
        }
        System.out.println(st.stock());""",
                  [_case(f"{h} {w}",
                         _nl("bad amount", h) if w <= 0
                         else _nl(min(w, h), h - min(w, h)))
                   for (h, w) in ((10, 3), (10, 20), (5, 0), (5, -2), (7, 7))],
                  ["The return value is a real quantity, so any sentinel could "
                   "collide with a legitimate answer — which is why this one throws.",
                   "Validate first, then clamp the amount to what is available, then "
                   "subtract.",
                   "Taking more than the stock is NOT an error here: it takes "
                   "everything and returns that.",
                   "A rejected call must leave the stock untouched — throw before any "
                   "subtraction.",
                   "Cases three and four pass a non-positive amount and print the "
                   "message plus the unchanged stock."]),
    ])


_PRACTICE[16] = [_P16_A, _P16_B, _P16_C, _P16_D, _P16_E]
